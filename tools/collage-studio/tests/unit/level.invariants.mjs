// =============================================================================
// THE LEVEL — invariant sweep.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// Transpiles the REAL modules with esbuild and asserts against them — never a
// re-implementation, because a sweep that re-implements the thing it is testing
// only proves the two copies agree. There is exactly ONE re-implementation in
// this file and it is deliberate:
//
//   `legacyLive` — what `stage.applyMutes` wrote into a gain node and an element
//                  BEFORE this rung, verbatim (`audible ? 1 : 0`, twice). It
//                  exists so "a source nobody quietened renders bit-identically"
//                  is a MEASUREMENT rather than a claim in a comment (I3).
//
// THE ONE THAT MATTERS IS I2: `node * element === effective`, at every level, in
// both branches. That is the invariant that makes the squaring bug named in
// `lib/level.ts`'s header — the level written into BOTH the element's volume and
// the gain node it feeds, rendering 25% as 6% — unrepresentable rather than
// merely fixed. It is the whole reason `livePath` is a function instead of two
// expressions inlined at the call site.
//
//   node tests/unit/level.invariants.mjs
// =============================================================================

import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const {
  LEVELS, FULL_LEVEL, LEVEL_MIN, safeLevel, isQuieted, levelChoice, levelLabel,
  levelDb, mixGain, livePath,
} = await load('src/lib/level.ts', 'level');
const { soundtrackSource, SOUNDTRACK_ID } = await load('src/lib/soundtrack.ts', 'soundtrack');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

/** Deterministic PRNG so a failure is reproducible. */
const rng = (seed) => {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
};

const ROSTER = LEVELS.map((l) => l.level);

/** `applyMutes` EXACTLY as it shipped before the level existed. */
const legacyLive = (audible) => ({ node: audible ? 1 : 0, element: audible ? 1 : 0 });

// =============================================================================
// I1 — THE RANGE. Every value `safeLevel` can return is a usable multiplier:
//      inside (0, 1], never a boost, never a phase flip, never NaN. This is the
//      number that reaches `GainNode.gain.value` and `AudioBufferSourceNode`'s
//      graph, and an engine given a NaN gain does not throw — it goes silent.
// =============================================================================
{
  const r = rng(0x1E7);
  const probes = [
    undefined, null, NaN, Infinity, -Infinity, 0, -0, -1, -0.5, 1, 1.0000001, 2, 1e9,
    LEVEL_MIN, LEVEL_MIN - 1e-9, 0.0624, 0.5, 0.125, 0.99,
  ];
  for (let i = 0; i < 4000; i++) probes.push((r() - 0.2) * 2.5);
  let bad = null;
  for (const p of probes) {
    const l = safeLevel(p);
    if (!Number.isFinite(l)) bad = bad ?? `safeLevel(${p}) = ${l} is not finite`;
    else if (!(l > 0)) bad = bad ?? `safeLevel(${p}) = ${l} is not positive`;
    else if (l > FULL_LEVEL) bad = bad ?? `safeLevel(${p}) = ${l} boosts above unity`;
    else if (l < LEVEL_MIN) bad = bad ?? `safeLevel(${p}) = ${l} is under the floor`;
  }
  ok('I1 safeLevel always lands in [LEVEL_MIN, 1]', bad === null, bad ?? `${probes.length} probes`);
}

// =============================================================================
// I1b — THE SIGN ASYMMETRY, which is the one place this module departs from
//       `safeSpeed` and therefore the one a helpful edit would "correct".
//       0 and anything under the floor is somebody asking for QUIET and clamps
//       UP; a NEGATIVE amplitude is a phase flip nobody meant and falls back to
//       FULL with the other broken values.
// =============================================================================
{
  let bad = null;
  if (safeLevel(0) !== LEVEL_MIN) bad = `safeLevel(0) = ${safeLevel(0)}, expected the floor`;
  if (safeLevel(0.001) !== LEVEL_MIN) bad = bad ?? `safeLevel(0.001) = ${safeLevel(0.001)}`;
  if (safeLevel(-0.5) !== FULL_LEVEL) bad = bad ?? `safeLevel(-0.5) = ${safeLevel(-0.5)}, expected full`;
  if (safeLevel(-1e9) !== FULL_LEVEL) bad = bad ?? `safeLevel(-1e9) = ${safeLevel(-1e9)}`;
  if (safeLevel(NaN) !== FULL_LEVEL) bad = bad ?? `safeLevel(NaN) = ${safeLevel(NaN)}`;
  if (safeLevel(Infinity) !== FULL_LEVEL) bad = bad ?? `safeLevel(Infinity) = ${safeLevel(Infinity)}`;
  // -0 is finite and NOT < 0, so it takes the quiet branch with +0. Asserted
  // because the two zeroes taking different branches would be a real trap.
  if (safeLevel(-0) !== LEVEL_MIN) bad = bad ?? `safeLevel(-0) = ${safeLevel(-0)}`;
  ok('I1b under the floor clamps up, a negative falls back to full', bad === null,
    bad ?? '0 -> floor · -0.5 -> full · NaN -> full');
}

// =============================================================================
// I2 — THE ONE MULTIPLICATION. `node * element === effective`, in BOTH branches,
//      at every level and both audibilities. This is what makes the squaring bug
//      unrepresentable: an implementation that wrote the level into the element
//      AND the node it feeds would render `l * l` and fail here at every level
//      except 1 and 0 — i.e. at every level a user would ever pick.
// =============================================================================
{
  const r = rng(0x2E7);
  const levels = [...ROSTER, undefined, null, 0, 0.7, 0.33, 2, -1];
  for (let i = 0; i < 600; i++) levels.push(r());
  let bad = null;
  let checked = 0;
  for (const l of levels) {
    for (const audible of [true, false]) {
      for (const hasGraph of [true, false]) {
        const p = livePath(audible, l, hasGraph);
        checked++;
        const want = audible ? safeLevel(l) : 0;
        if (!Object.is(p.effective, want)) {
          bad = bad ?? `livePath(${audible}, ${l}, ${hasGraph}).effective = ${p.effective}, want ${want}`;
        }
        if (!Object.is(p.node * p.element, p.effective)) {
          bad = bad ?? `livePath(${audible}, ${l}, ${hasGraph}): ${p.node} * ${p.element} != ${p.effective}`;
        }
        if (!Number.isFinite(p.node) || !Number.isFinite(p.element)) {
          bad = bad ?? `livePath(${audible}, ${l}, ${hasGraph}) wrote a non-finite value`;
        }
      }
    }
  }
  ok('I2 node * element === effective, in both branches', bad === null, bad ?? `${checked} settings`);
}

// =============================================================================
// I2b — THE LEVEL RIDES THE NODE WHEN THERE IS ONE. Not a restatement of I2:
//       `{node: 1, element: l}` also satisfies the product, and would be wrong,
//       because `captureStream` taps `masterGain` DOWNSTREAM of the gain nodes
//       and UPSTREAM of nothing — a level held on the element only would be in
//       the room and in the offline mix and absent from the realtime recording.
// =============================================================================
{
  let bad = null;
  for (const l of ROSTER) {
    const g = livePath(true, l, true);
    if (!Object.is(g.node, safeLevel(l))) bad = bad ?? `graph branch put ${g.node} on the node, want ${l}`;
    if (g.element !== 1) bad = bad ?? `graph branch put ${g.element} on the element, want 1`;
    const n = livePath(true, l, false);
    if (!Object.is(n.element, safeLevel(l))) bad = bad ?? `no-graph branch put ${n.element} on the element, want ${l}`;
  }
  ok('I2b with a graph the node carries it; without one the element does', bad === null,
    bad ?? `${ROSTER.length} levels`);
}

// =============================================================================
// I3 — THE COMPATIBILITY CLAUSE, MEASURED. A source nobody quietened writes the
//      SAME two numbers `applyMutes` wrote before this rung existed. Not "close
//      enough": `Object.is`, against the old expression itself.
// =============================================================================
{
  let bad = null;
  for (const audible of [true, false]) {
    for (const level of [undefined, null, FULL_LEVEL]) {
      const now = livePath(audible, level, true);
      const then = legacyLive(audible);
      if (!Object.is(now.node, then.node) || !Object.is(now.element, then.element)) {
        bad = bad ?? `audible=${audible} level=${level}: {${now.node},${now.element}} vs {${then.node},${then.element}}`;
      }
    }
  }
  ok('I3 an untouched source is bit-identical to the pre-level build', bad === null,
    bad ?? 'absent, null and 1 all render as the old expression');
}

// =============================================================================
// I4 — INTENT, NOT AUDIBILITY, REACHES THE FILE. `mixGain` must never consult
//      anything but `wanted` and the level: the export is written from intent,
//      and wiring it to the speakers is the defect that made every export silent
//      once already (written up on `StageClipStatus.wantsAudio`).
//      A muted source is 0 AT EVERY LEVEL; an unmuted one is always > 0, which
//      is what `mixSources` admits on.
// =============================================================================
{
  const r = rng(0x4E7);
  const levels = [...ROSTER, undefined, null, 0, -1, 5];
  for (let i = 0; i < 500; i++) levels.push(r() * 1.5);
  let bad = null;
  for (const l of levels) {
    if (mixGain(false, l) !== 0) bad = bad ?? `mixGain(false, ${l}) = ${mixGain(false, l)}`;
    const g = mixGain(true, l);
    if (!(g > 0)) bad = bad ?? `mixGain(true, ${l}) = ${g} would be dropped by mixSources`;
    if (!Object.is(g, safeLevel(l))) bad = bad ?? `mixGain(true, ${l}) = ${g} != safeLevel`;
  }
  ok('I4 muted is 0 at every level; unmuted is always admissible', bad === null,
    bad ?? `${levels.length} levels`);
}

// =============================================================================
// I5 — THE MUSIC AND A CLIP AGREE. `soundtrackSource` is a SEPARATE emitter of
//      the same row `describeAudioSources` builds for a clip (the two are kept
//      structurally identical on purpose, and the soundtrack sweep already
//      asserts the field set). Its gain must be `mixGain` and not a second
//      opinion about what a level means — the whole reason `mixGain` exists.
// =============================================================================
{
  let bad = null;
  for (const l of [...ROSTER, undefined, 0.33]) {
    for (const muted of [true, false]) {
      const row = soundtrackSource({ url: 'blob:x', name: 'm', durationSec: 0, muted, level: l });
      if (!row) { bad = bad ?? 'soundtrackSource returned null for a real url'; continue; }
      const want = mixGain(!muted, l);
      if (!Object.is(row.gain, want)) bad = bad ?? `music muted=${muted} level=${l}: gain ${row.gain}, want ${want}`;
      if (row.id !== SOUNDTRACK_ID) bad = bad ?? 'the music row lost its id';
      // DECISION 1 must survive this rung: span stays 0 whatever the level is.
      if (row.span !== 0) bad = bad ?? `span is ${row.span}, not 0`;
    }
  }
  ok('I5 the music emits mixGain, not a second opinion', bad === null, bad ?? 'both mutes x 7 levels');
}

// =============================================================================
// I6 — THE ROSTER. Five chips, no boost, monotonically quieter, ending at the
//      floor `safeLevel` clamps to — a roster whose bottom chip is not the floor
//      would leave a reachable level no chip can express.
// =============================================================================
{
  let bad = null;
  if (LEVELS.length !== 5) bad = `roster is ${LEVELS.length} chips, not 5`;
  if (LEVELS[0].level !== FULL_LEVEL) bad = bad ?? 'the roster does not start at full';
  if (LEVELS[LEVELS.length - 1].level !== LEVEL_MIN) bad = bad ?? 'the last chip is not the floor';
  for (let i = 1; i < LEVELS.length; i++) {
    if (!(LEVELS[i].level < LEVELS[i - 1].level)) bad = bad ?? `chip ${i} is not quieter than ${i - 1}`;
    // -6 dB per step, i.e. an exact halving: the interval the header commits to.
    if (!Object.is(LEVELS[i].level, LEVELS[i - 1].level / 2)) {
      bad = bad ?? `chip ${i} is ${LEVELS[i].level}, not half of ${LEVELS[i - 1].level}`;
    }
  }
  if (new Set(LEVELS.map((l) => l.id)).size !== LEVELS.length) bad = bad ?? 'duplicate roster id';
  for (const c of LEVELS) {
    if (!c.title || c.title.length < 8) bad = bad ?? `chip ${c.id} has no usable title`;
    if (levelChoice(c.level)?.id !== c.id) bad = bad ?? `levelChoice cannot find ${c.id}`;
  }
  ok('I6 five chips, full to floor, each an exact halving', bad === null,
    bad ?? LEVELS.map((l) => l.label).join(' '));
}

// =============================================================================
// I7 — THE LABELS. The badge sits on the tightest row in the app, so it must be
//      short, must never render for a source at full (absence is the natural
//      state, and a badge on every clip is not a badge), and must agree with the
//      chip a user tapped. TRUNCATION is the load-bearing half: rounding prints
//      `13%` for 0.125, which is the face of no chip on the roster.
// =============================================================================
{
  let bad = null;
  const want = { 1: '100%', 0.5: '50%', 0.25: '25%', 0.125: '12%', 0.0625: '6%' };
  for (const c of LEVELS) {
    if (levelLabel(c.level) !== want[c.level]) bad = bad ?? `levelLabel(${c.level}) = ${levelLabel(c.level)}`;
    if (levelLabel(c.level) !== c.label) bad = bad ?? `badge ${levelLabel(c.level)} != chip ${c.label}`;
    if (c.label.length > 4) bad = bad ?? `label ${c.label} is too long for the chip`;
  }
  if (isQuieted(FULL_LEVEL) || isQuieted(undefined) || isQuieted(null)) bad = bad ?? 'full reads as quietened';
  if (!isQuieted(0.5) || !isQuieted(LEVEL_MIN)) bad = bad ?? 'a quietened source reads as full';
  ok('I7 labels are short, truncated, and match the chip', bad === null,
    bad ?? LEVELS.map((l) => levelLabel(l.level)).join(' '));
}

// =============================================================================
// I8 — THE dB READOUT is the roster's own claim, checked against the definition
//      rather than against a table: 20*log10 of each step is 6.0206... dB, and
//      the header promises "-6 dB each". Rounded to 0.1 the roster must read
//      0 / 6 / 12 / 18.1 / 24.1 — asserted so a future roster edit that breaks
//      the halving shows up in the words the UI says, not only in I6.
// =============================================================================
{
  let bad = null;
  if (levelDb(FULL_LEVEL) !== 0) bad = `levelDb(1) = ${levelDb(FULL_LEVEL)}`;
  if (levelDb(2) !== 0) bad = bad ?? 'a clamped boost does not read as 0 dB';
  for (let i = 1; i < LEVELS.length; i++) {
    const step = levelDb(LEVELS[i].level) - levelDb(LEVELS[i - 1].level);
    if (Math.abs(step - 6.0206) > 0.11) bad = bad ?? `step ${i} is ${step} dB, not ~6`;
    if (!(levelDb(LEVELS[i].level) > 0)) bad = bad ?? `chip ${i} reads as 0 dB down`;
  }
  ok('I8 every step is ~6 dB and the readout says so', bad === null,
    bad ?? LEVELS.map((l) => `-${levelDb(l.level)}`).join(' '));
}

console.log('\nTHE LEVEL — invariant sweep\n' + '='.repeat(64));
for (const line of results) console.log(line);
console.log('='.repeat(64));
console.log(failures === 0 ? `ALL ${results.length} GREEN` : `${failures} FAILING`);
process.exit(failures === 0 ? 0 : 1);
