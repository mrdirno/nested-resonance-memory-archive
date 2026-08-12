// =============================================================================
// THE SPEED — invariant sweep.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// Transpiles the REAL modules with esbuild and asserts against them — never a
// re-implementation, because a sweep that re-implements the thing it is testing
// only proves the two copies agree. There are exactly TWO re-implementations in
// this file and both are deliberate:
//
//   `legacyPlayback`  — `computeClipPlayback` as it shipped BEFORE this feature,
//                       verbatim. It exists so the identity clause ("a build
//                       with every speed at 1 is bit-identical to the build
//                       before the control existed") is a MEASUREMENT rather
//                       than a claim in a comment.
//   `afterwardsRate`  — the REJECTED design: let the caller multiply the sync
//                       rate by the speed after the fact. It exists to be
//                       refuted, in numbers, at the exact place it degenerates.
//
// THE ONE THAT MATTERS IS I3: under a stretch mode every clip's ON-SCREEN length
// still equals the reference AT EVERY COMBINATION OF SPEEDS. That is what "match
// the lengths" means, and it is the property the rejected design breaks — I3b
// measures by how much.
//
//   node tests/unit/speed.invariants.mjs
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
  SPEEDS, NATURAL_SPEED, SPEED_MIN, SPEED_MAX, safeSpeed, isSped, speedLabel, screenLength,
} = await load('src/lib/speed.ts', 'speed');
const {
  computeClipPlayback, referenceLength, CLIP_LENGTH_MODES, RATE_MIN, RATE_MAX,
} = await load('src/lib/videoSync.ts', 'videosync');
const {
  normaliseWindow, sourceTimeAt, audioPlan, audioSchedule, audioPositionAt,
  schedulePositionAt, effectiveLength, MAX_AUDIO_LAPS,
} = await load('src/lib/clipWindow.ts', 'clipwindow');

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

const RATES = SPEEDS.map((s) => s.rate);

// --- the two deliberate re-implementations -----------------------------------

/** `computeClipPlayback` EXACTLY as it shipped before the speed control. */
const legacyPlayback = (clips, mode) => {
  const validDuration = (d) => Number.isFinite(d) && d > 0;
  const clampRate = (r) =>
    !Number.isFinite(r) || r <= 0 ? 1 : Math.min(RATE_MAX, Math.max(RATE_MIN, r));
  const durs = clips.map((c) => c.durationSec).filter(validDuration);
  let ref = null;
  if (durs.length > 0) {
    if (mode === 'stretch-longest') ref = Math.max(...durs);
    else if (mode === 'speed-shortest') ref = Math.min(...durs);
  }
  return clips.map((c) => {
    let rate = 1;
    if (ref && ref > 0 && validDuration(c.durationSec)) rate = c.durationSec / ref;
    return { id: c.id, playbackRate: clampRate(rate), loop: true };
  });
};

/** THE REJECTED DESIGN: sync first, then multiply the user's speed onto it. */
const afterwardsRate = (clips, mode) => {
  const base = legacyPlayback(clips, mode);
  return base.map((p, i) => ({
    ...p,
    playbackRate: Math.min(RATE_MAX, Math.max(RATE_MIN, p.playbackRate * safeSpeed(clips[i].speed))),
  }));
};

// --- clip-set generator -------------------------------------------------------

const clipSets = (seed, n) => {
  const r = rng(seed);
  const out = [];
  for (let k = 0; k < n; k++) {
    const count = 1 + Math.floor(r() * 4);
    const clips = [];
    for (let i = 0; i < count; i++) {
      clips.push({
        id: `c${k}-${i}`,
        // 0.2s .. 60s, the range a real import spans.
        durationSec: 0.2 + r() * 59.8,
        speed: RATES[Math.floor(r() * RATES.length)],
      });
    }
    out.push(clips);
  }
  return out;
};

// =============================================================================
// I1 — THE IDENTITY CLAUSE. Every speed at 1 (absent OR explicit) reproduces the
//      pre-feature numbers BITWISE, in every mode. Not "close": Object.is.
// =============================================================================
{
  let checked = 0, worst = null;
  for (const clips of clipSets(0xC150, 240)) {
    for (const absent of [true, false]) {
      const input = clips.map((c) => ({
        id: c.id,
        durationSec: c.durationSec,
        ...(absent ? {} : { speed: 1 }),
      }));
      for (const mode of CLIP_LENGTH_MODES) {
        const got = computeClipPlayback(input, mode);
        const want = legacyPlayback(input, mode);
        for (let i = 0; i < got.length; i++) {
          checked++;
          if (!Object.is(got[i].playbackRate, want[i].playbackRate) || got[i].loop !== want[i].loop) {
            worst = worst ?? `${mode} clip ${got[i].id}: ${got[i].playbackRate} vs ${want[i].playbackRate}`;
          }
        }
      }
    }
  }
  ok('I1 speed 1 (absent or explicit) is bit-identical to the pre-feature build',
    worst === null, worst ?? `${checked} rates identical across 3 modes`);
}

// =============================================================================
// I2 — UNDER 'loop' THE RATE IS THE SPEED. No reference means nothing is being
//      matched, so the clip runs at exactly what was asked for.
// =============================================================================
{
  let bad = null, checked = 0;
  for (const clips of clipSets(0x5EED, 200)) {
    const got = computeClipPlayback(clips, 'loop');
    got.forEach((p, i) => {
      checked++;
      const want = safeSpeed(clips[i].speed);
      if (!Object.is(p.playbackRate, want)) bad = bad ?? `${p.id}: ${p.playbackRate} != ${want}`;
    });
  }
  ok("I2 'loop' plays each clip at exactly its own speed", bad === null,
    bad ?? `${checked} clips, all rate === safeSpeed`);
}

// =============================================================================
// I3 — THE SYNC INVARIANT SURVIVES EVERY COMBINATION OF SPEEDS. Under a stretch
//      mode, on-screen length (window / rate) === the reference, for every clip.
//      This is what "same length" means, and the speeds are inside the reference
//      rather than on top of the rate precisely so it cannot be broken.
// =============================================================================
{
  let bad = null, checked = 0, clamped = 0;
  for (const clips of clipSets(0xA11, 300)) {
    for (const mode of ['stretch-longest', 'speed-shortest']) {
      const ref = referenceLength(clips, mode);
      const got = computeClipPlayback(clips, mode);
      got.forEach((p, i) => {
        const raw = clips[i].durationSec / ref;
        // A clamped rate cannot land on the reference — that is the clamp doing
        // its job against an engine bound, and it is counted, not excused.
        if (raw < RATE_MIN || raw > RATE_MAX) { clamped++; return; }
        checked++;
        const seen = clips[i].durationSec / p.playbackRate;
        if (Math.abs(seen - ref) > 1e-9) bad = bad ?? `${mode} ${p.id}: sees ${seen}, ref ${ref}`;
      });
    }
  }
  ok('I3 a stretch mode lands every clip on the reference at every speed', bad === null,
    bad ?? `${checked} clips on-screen-equal (${clamped} rate-clamped, excluded)`);
}

// =============================================================================
// I3b — THE REJECTED DESIGN, REFUTED IN NUMBERS. Multiplying the speed onto the
//       sync rate afterwards makes "match the lengths" false by exactly the
//       speed ratio: two clips asked to be the same length come out different.
// =============================================================================
{
  let worstSpread = 0, example = '';
  for (const clips of clipSets(0xBAD, 300)) {
    if (clips.length < 2) continue;
    const mode = 'stretch-longest';
    const got = afterwardsRate(clips, mode);
    const seen = got.map((p, i) => clips[i].durationSec / p.playbackRate);
    const spread = Math.max(...seen) / Math.min(...seen);
    if (spread > worstSpread) {
      worstSpread = spread;
      example = `${seen.map((s) => s.toFixed(2)).join('s / ')}s from speeds ${clips.map((c) => c.speed).join(',')}`;
    }
  }
  // The shipped design's spread is exactly 1 (I3). The rejected one is not.
  ok('I3b the rejected "multiply afterwards" design breaks equal lengths', worstSpread > 1.5,
    `worst on-screen spread ${worstSpread.toFixed(2)}x — ${example}`);
}

// =============================================================================
// I4 — THE REFERENCE IS TAKEN OVER SCREEN LENGTHS, NOT OVER FILES.
// =============================================================================
{
  let bad = null;
  for (const clips of clipSets(0x4EF, 200)) {
    const seen = clips.map((c) => c.durationSec / safeSpeed(c.speed));
    const wantMax = Math.max(...seen), wantMin = Math.min(...seen);
    const gotMax = referenceLength(clips, 'stretch-longest');
    const gotMin = referenceLength(clips, 'speed-shortest');
    if (!Object.is(gotMax, wantMax)) bad = bad ?? `stretch: ${gotMax} != ${wantMax}`;
    if (!Object.is(gotMin, wantMin)) bad = bad ?? `speed: ${gotMin} != ${wantMin}`;
    if (referenceLength(clips, 'loop') !== null) bad = bad ?? 'loop invented a reference';
  }
  ok('I4 the reference is max/min of window/speed, and loop still has none', bad === null,
    bad ?? '200 clip sets');
}

// =============================================================================
// I5 — safeSpeed IS TOTAL. Absent, NaN, Infinity, 0, negative, and both
//      out-of-roster directions all resolve to something a chip can express.
// =============================================================================
{
  // THE ASYMMETRY IS THE DECISION, and the sweep is what made me write it down:
  // a FINITE out-of-range number is a value somebody meant, so it is clamped
  // into the roster; a NON-FINITE one is a broken value, so it falls back to the
  // untouched state. That is `clipWindow.safeRate`'s rule verbatim, and the two
  // must agree because they end up multiplied together.
  const cases = [
    [undefined, 1], [null, 1], [NaN, 1], [Infinity, 1], [-Infinity, 1],
    [0, 1], [-2, 1], [1e9, SPEED_MAX], [1e-9, SPEED_MIN],
    [0.25, 0.25], [4, 4], [1, 1], [3, 3],
  ];
  let bad = null;
  for (const [input, want] of cases) {
    const got = safeSpeed(input);
    if (!Object.is(got, want)) bad = bad ?? `safeSpeed(${String(input)}) = ${got}, want ${want}`;
    if (!(got >= SPEED_MIN && got <= SPEED_MAX)) bad = bad ?? `safeSpeed(${String(input)}) escaped the roster`;
  }
  if (isSped(undefined) || isSped(1) || isSped(NaN)) bad = bad ?? 'isSped said a natural clip is sped';
  if (!isSped(2) || !isSped(0.5)) bad = bad ?? 'isSped missed a sped clip';
  ok('I5 safeSpeed is total and isSped agrees with it', bad === null, bad ?? `${cases.length} cases`);
}

// =============================================================================
// I6 — THE ROSTER IS EXACT IN BOTH DIRECTIONS, and that is load-bearing rather
//      than tidy: a speed DIVIDES a window to pick the reference and MULTIPLIES
//      a source time the decoder is asked to seek to, so the same quantity makes
//      the round trip. Powers of two survive it exactly; the pace's 0.75 does
//      not, which is why that roster is not this one.
// =============================================================================
{
  const r = rng(0x1E6);
  let exact = 0, total = 0, drifted = null;
  for (let i = 0; i < 4000; i++) {
    const d = 0.05 + r() * 600;
    const s = RATES[Math.floor(r() * RATES.length)];
    total++;
    if (Object.is(screenLength(d, s) * s, d)) exact++;
    else drifted = drifted ?? `${d} at ${s}x came back as ${screenLength(d, s) * s}`;
  }
  // The contrast case: a non-dyadic rate of the kind lib/pace.ts deliberately
  // carries. If this were also exact the invariant above would be vacuous.
  let nonDyadicExact = 0;
  const r2 = rng(0x1E6);
  for (let i = 0; i < 4000; i++) {
    const d = 0.05 + r2() * 600;
    if (Object.is((d / 0.75) * 0.75, d)) nonDyadicExact++;
  }
  ok('I6 every roster speed round-trips a window bitwise', exact === total,
    drifted ?? `${exact}/${total} exact at {${RATES.join(', ')}}x, vs ${nonDyadicExact}/4000 at 0.75x`);
}

// =============================================================================
// I7 — THE E2E'S CLAIM, IN ARITHMETIC. A speed is a RE-PARAMETERISATION of the
//      clip's own time: the frame at output t under speed s is the frame at
//      output t*s under speed 1. The browser proves it on pixels; this proves
//      the seek target underneath is the same double, trimmed and looping too.
// =============================================================================
{
  const r = rng(0x7EE);
  let bad = null, checked = 0;
  for (let i = 0; i < 3000; i++) {
    const span = 0.3 + r() * 30;
    const w = normaliseWindow(span, r() < 0.5 ? 0 : r() * span * 0.4, r() < 0.5 ? span : span * (0.6 + r() * 0.4));
    const s = RATES[Math.floor(r() * RATES.length)];
    const loop = r() < 0.5;
    const t = r() * 40;
    const sped = sourceTimeAt({ window: w, loop, rate: s }, t);
    const natural = sourceTimeAt({ window: w, loop, rate: 1 }, t * s);
    checked++;
    if (!Object.is(sped, natural)) bad = bad ?? `t=${t} s=${s}: ${sped} vs ${natural}`;
  }
  ok('I7 speed s at time t is speed 1 at time t*s, bitwise', bad === null,
    bad ?? `${checked} (window, loop, speed, instant) cases`);
}

// =============================================================================
// I8 — THE SOUND STILL SITS WHERE THE PICTURE IS, at every speed. The plan's
//      start offset must equal `sourceTimeAt` at the mix's first instant, and
//      the node MODEL must track the picture through the take.
// =============================================================================
{
  const r = rng(0x50D);
  let bad = null, checked = 0;
  for (let i = 0; i < 1500; i++) {
    const span = 0.5 + r() * 20;
    const w = normaliseWindow(span, r() * span * 0.3, span * (0.7 + r() * 0.3));
    const s = RATES[Math.floor(r() * RATES.length)];
    const p = { window: w, loop: true, rate: s };
    const startAt = r() * 10;
    const plan = audioPlan(p, startAt);
    if (plan.silent) continue;
    checked++;
    if (Math.abs(plan.offset - sourceTimeAt(p, startAt)) > 1e-9) {
      bad = bad ?? `offset ${plan.offset} != picture ${sourceTimeAt(p, startAt)} at ${s}x`;
    }
    for (const u of [0, 0.37, 1.2, 3.9]) {
      const sound = audioPositionAt(plan, u);
      const picture = sourceTimeAt(p, startAt + u);
      if (sound !== null && Math.abs(sound - picture) > 1e-6) {
        bad = bad ?? `at ${s}x, u=${u}: sound ${sound} vs picture ${picture}`;
      }
    }
  }
  ok('I8 the audio plan tracks the sped picture', bad === null, bad ?? `${checked} plans`);
}

// =============================================================================
// I9 — THE COMPOSED RATE IS CLAMPED ONCE, against the ELEMENT's bound. A speed
//      on top of a sync rate can leave the range HTMLMediaElement honours; the
//      clamp is inside `computeClipPlayback`, so no caller can miss it.
// =============================================================================
{
  // 0.2s beside a 60s clip is a 300x ratio; at 4x the raw rate leaves RATE_MAX.
  const clips = [
    { id: 'tiny', durationSec: 0.2, speed: 1 },
    { id: 'long', durationSec: 60, speed: 4 },
  ];
  const got = computeClipPlayback(clips, 'speed-shortest');
  const raw = 60 / referenceLength(clips, 'speed-shortest');
  const inRange = got.every((p) => p.playbackRate >= RATE_MIN && p.playbackRate <= RATE_MAX);
  ok('I9 a composed rate past the element bound is clamped, once', inRange && raw > RATE_MAX,
    `raw ${raw.toFixed(1)}x -> clamped ${got[1].playbackRate}x (bound ${RATE_MAX})`);
}

// =============================================================================
// I10 — A SPEED SHORTENS THE PICTURE LAP, and the lap schedule stays bounded.
//       4x on a clip whose audio ends inside the window is the cheapest way to
//       quadruple the node count; the cap must hold and SAY so rather than
//       silently emitting an unbounded schedule.
// =============================================================================
{
  const span = 6;
  const w = normaliseWindow(span, 0, span);
  let bad = null;
  const counts = [];
  for (const s of RATES) {
    const sched = audioSchedule({ window: w, loop: true, rate: s }, 0, 120, 3); // audio ends at 3s
    counts.push(`${s}x:${sched.starts.length}`);
    if (sched.starts.length > MAX_AUDIO_LAPS) bad = bad ?? `${s}x emitted ${sched.starts.length} nodes`;
    if (!sched.lapped) bad = bad ?? `${s}x did not take the lap schedule`;
    // Every entry must still land where the picture is.
    for (const st of sched.starts) {
      const picture = sourceTimeAt({ window: w, loop: true, rate: s }, st.when);
      if (Math.abs(schedulePositionAt(sched.starts, st.when) - picture) > 1e-6 && st.when > 0) {
        bad = bad ?? `${s}x: lap at ${st.when} does not sit on the picture`;
      }
    }
  }
  const faster = audioSchedule({ window: w, loop: true, rate: 4 }, 0, 120, 3).starts.length;
  const natural = audioSchedule({ window: w, loop: true, rate: 1 }, 0, 120, 3).starts.length;
  ok('I10 a speed laps the sound with the picture, bounded', bad === null && faster > natural,
    bad ?? `laps in a 120s take — ${counts.join(' ')} (4x is ${(faster / natural).toFixed(1)}x the laps)`);
}

// =============================================================================
// I11 — THE ON-SCREEN LENGTH AGREES WITH clipWindow.effectiveLength, which is
//       the same quantity approached from the other module. Two definitions of
//       "how long is this on screen" is how this project got three copies of
//       `sourceTimeAt`.
// =============================================================================
{
  const r = rng(0xE11);
  let bad = null;
  for (let i = 0; i < 2000; i++) {
    const span = 0.3 + r() * 30;
    const w = normaliseWindow(span, 0, span);
    const s = RATES[Math.floor(r() * RATES.length)];
    const viaSpeed = screenLength(w.length, s);
    const viaWindow = effectiveLength({ window: w, loop: true, rate: s });
    if (!Object.is(viaSpeed, viaWindow)) bad = bad ?? `${w.length} at ${s}x: ${viaSpeed} vs ${viaWindow}`;
  }
  ok('I11 screenLength and effectiveLength are the same number', bad === null, bad ?? '2000 windows');
}

// =============================================================================
// I12 — THE LABELS. A badge on the tightest row in the app must be short and
//       must never say "1x" (absence is the natural state, and a badge that
//       renders for every clip is not a badge).
// =============================================================================
{
  let bad = null;
  const want = { 0.25: '0.25×', 0.5: '0.5×', 1: '1×', 2: '2×', 4: '4×' };
  for (const s of RATES) {
    if (speedLabel(s) !== want[s]) bad = bad ?? `speedLabel(${s}) = ${speedLabel(s)}`;
    if (speedLabel(s).length > 5) bad = bad ?? `label ${speedLabel(s)} is too long for the chip`;
  }
  if (SPEEDS.filter((s) => s.rate === NATURAL_SPEED).length !== 1) bad = bad ?? 'the roster is not centred on 1x';
  if (SPEEDS.length !== 5) bad = bad ?? `roster is ${SPEEDS.length} chips, not 5`;
  ok('I12 the roster labels are short, centred on 1x, and five wide', bad === null,
    bad ?? SPEEDS.map((s) => s.label).join(' '));
}

console.log('\nTHE SPEED — invariant sweep\n' + '='.repeat(64));
for (const line of results) console.log(line);
console.log('='.repeat(64));
console.log(failures === 0 ? `ALL ${results.length} GREEN` : `${failures} FAILING`);
process.exit(failures === 0 ? 0 : 1);
