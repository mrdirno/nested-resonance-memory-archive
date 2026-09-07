/**
 * INVARIANT SWEEP for src/lib/solo.ts — who is coming out of the speakers.
 *
 *   node tests/unit/solo.invariants.mjs
 *
 * Transpiles and imports the REAL module. No re-implementation — a sweep
 * against a copy grades the copy (C150).
 *
 * THE THREE THAT CARRY THE FEATURE, and each is a panel finding rather than a
 * tidy idea (av/AV_SOCIETY.md §THE PANEL, C3719 — scored 8 / 5 / 3):
 *
 *   S4  A TAKE IS NEVER SOLOED, for its whole duration and not merely at its
 *       start. The skeptic lens scored this 3 and would have cut solo outright
 *       over it: the realtime capture path taps the same WebAudio gains this
 *       plan writes, so a solo engaged MID-take records as a silent dropout in
 *       a file that otherwise looks fine. Asserted as byte-identity with the
 *       no-solo plan, so the guard cannot be "remembered" wrongly by a caller.
 *   S3  YOU CAN SOLO A MUTED SOURCE — the plan for a soloed source is identical
 *       whether its own speaker is on or off. This reads like a bug until you
 *       remember the wish: you are auditioning to decide what to KEEP, so the
 *       one you most need to hear is the one currently switched off.
 *   S7  PURITY. The inputs are deep-frozen and re-checked after every call. A
 *       solo that could write a mute is the export-corruption bug this app has
 *       already shipped once, wearing a new name.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const dir = mkdtempSync(join(tmpdir(), 'solo-'));

/** BUNDLE, DO NOT TRANSFORM — a transform dies the day the module grows an import. */
const load = async (rel, out) => {
  const tmp = join(dir, out);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: tmp,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    logLevel: 'silent',
  });
  return import(pathToFileURL(tmp).href);
};

const S = await load('src/lib/solo.ts', 'solo.mjs');
const { monitorPlan, nextSolo, pruneSolo, soloBanner, NO_EXCLUSIVE, AUDITION_LEVEL } = S;

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const assert = (cond, m) => (cond ? ok() : fail(m));

/** Deterministic, so a failure is a failure anyone can re-run. */
const mulberry32 = (a) => () => {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const deepFreeze = (o) => {
  if (o && typeof o === 'object' && !Object.isFrozen(o)) {
    Object.freeze(o);
    for (const k of Object.keys(o)) deepFreeze(o[k]);
  }
  return o;
};

const clone = (o) => JSON.parse(JSON.stringify(o));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// ---------------------------------------------------------------------------
// THE SWEEP
// ---------------------------------------------------------------------------
const SEEDS = 400;
for (let seed = 0; seed < SEEDS; seed++) {
  const rnd = mulberry32(seed * 7919 + 13);
  const n = 1 + Math.floor(rnd() * 7);
  const sources = [];
  for (let i = 0; i < n; i++) {
    const s = { id: `s${i}`, wantsAudio: rnd() < 0.6 };
    if (rnd() < 0.2) s.broken = true;
    if (rnd() < 0.35) s.live = rnd() < 0.5;
    if (rnd() < 0.4) s.level = Math.round(rnd() * 100) / 100;
    sources.push(s);
  }
  const ids = sources.map((s) => s.id);
  const soundOn = rnd() < 0.7;
  const capturing = rnd() < 0.35;

  // A stale id is deliberately in the draw: an exclusive pointing at a source
  // that has been removed must not make some OTHER source audible.
  const pickId = () => (rnd() < 0.12 ? 'gone' : ids[Math.floor(rnd() * ids.length)]);
  const r = rnd();
  const exclusive = r < 0.4 ? NO_EXCLUSIVE
    : r < 0.7 ? { kind: 'solo', id: pickId() }
      : { kind: 'audition', id: pickId() };

  const input = { sources, soundOn, exclusive, capturing };
  const before = clone(input);
  deepFreeze(input);

  let plan;
  try {
    plan = monitorPlan(input);
  } catch (e) {
    fail(`seed ${seed}: monitorPlan threw on frozen input — ${e && e.message}`);
    continue;
  }

  // S7 — PURITY. Frozen inputs survive the call unchanged.
  assert(same(before, input), `seed ${seed}: S7 monitorPlan mutated its input`);

  // S12 — SHAPE. Same length, same ids, same order. A caller applies these rows
  // to elements positionally; a reorder puts one clip's gain on another's decoder.
  assert(plan.length === sources.length, `seed ${seed}: S12 plan length ${plan.length} != ${sources.length}`);
  assert(plan.every((row, i) => row.id === sources[i].id), `seed ${seed}: S12 plan reordered its rows`);

  const only = exclusive.kind === 'none' ? null : exclusive.id;
  const soloing = exclusive.kind === 'solo' && !capturing;
  const auditioning = exclusive.kind === 'audition';

  for (let i = 0; i < sources.length; i++) {
    const s = sources[i];
    const row = plan[i];
    const held = s.live !== false;

    // S10 — a broken source is never audible, under any exclusive.
    if (s.broken) {
      assert(!row.audible, `seed ${seed}: S10 broken ${s.id} came out audible`);
    }

    // S2 — exclusivity. When someone owns the room, nobody else is in it.
    if ((soloing || auditioning) && s.id !== only) {
      assert(!row.audible, `seed ${seed}: S2 ${s.id} audible while ${only} owns the room`);
      assert(row.reason === 'soloed-out' || row.reason === 'broken',
        `seed ${seed}: S2 ${s.id} reason ${row.reason} under an exclusive`);
    }

    // S1 — with no exclusive in force, audibility is the plain rule.
    if (!soloing && !auditioning) {
      const want = soundOn && s.wantsAudio && !s.broken && held;
      assert(row.audible === want,
        `seed ${seed}: S1 ${s.id} audible=${row.audible} want=${want}`);
    }

    // S5 / S6 — an audition outranks the monitor switch; a solo does not.
    if (auditioning && s.id === only) {
      assert(row.audible === (!s.broken && held),
        `seed ${seed}: S5 audition on ${s.id} did not ignore the monitor switch`);
      assert(row.level === AUDITION_LEVEL,
        `seed ${seed}: S11 audition on ${s.id} played at ${row.level}, not unity`);
    }
    if (soloing && s.id === only) {
      assert(row.audible === (soundOn && !s.broken && held),
        `seed ${seed}: S6 solo on ${s.id} audible=${row.audible} soundOn=${soundOn}`);
      // S11 — a solo plays at the source's OWN level. DAW-true, and the reason
      // `soloBanner` names the level: a source at 15% soloed into an empty room
      // sounds like a broken feature rather than like the level you set.
      assert(row.level === s.level,
        `seed ${seed}: S11 solo on ${s.id} played at ${row.level}, not its own ${s.level}`);
    }

    // Reason is never 'audible' unless it is, and vice versa.
    assert(row.audible === (row.reason === 'audible'),
      `seed ${seed}: ${s.id} audible=${row.audible} disagrees with reason=${row.reason}`);
  }

  // S4 — A TAKE IS NEVER SOLOED. Not "cleared at the start": for the whole take
  // the plan IS the no-solo plan, byte for byte.
  if (exclusive.kind === 'solo') {
    const rolling = monitorPlan({ sources, soundOn, exclusive, capturing: true });
    const none = monitorPlan({ sources, soundOn, exclusive: NO_EXCLUSIVE, capturing: true });
    assert(same(rolling, none), `seed ${seed}: S4 a solo reached a running take`);
  }

  // S3 — YOU CAN SOLO A MUTED SOURCE: flipping the soloed source's own intent
  // changes nothing about the plan.
  if (exclusive.kind === 'solo' && ids.includes(exclusive.id)) {
    const flipped = sources.map((s) => (s.id === exclusive.id ? { ...s, wantsAudio: !s.wantsAudio } : s));
    const a = monitorPlan({ sources, soundOn, exclusive, capturing: false });
    const b = monitorPlan({ sources: flipped, soundOn, exclusive, capturing: false });
    assert(same(a, b), `seed ${seed}: S3 solo read the soloed source's own mute`);
  }

  // S9 — pruneSolo drops a solo whose source is gone, and keeps one that is not.
  for (const cand of [null, 'gone', ids[0], ids[ids.length - 1]]) {
    const kept = pruneSolo(cand, ids);
    assert(kept === (cand !== null && ids.includes(cand) ? cand : null),
      `seed ${seed}: S9 pruneSolo(${cand}) = ${kept}`);
  }
}

// ---------------------------------------------------------------------------
// S8 — THE EXCLUSIVE TOGGLE, exhaustively over a small alphabet.
// ---------------------------------------------------------------------------
for (const a of ['a', 'b', 'c']) {
  assert(nextSolo(null, a) === a, `S8 nextSolo(null, ${a})`);
  assert(nextSolo(a, a) === null, `S8 nextSolo(${a}, ${a}) must release`);
  for (const b of ['a', 'b', 'c']) {
    if (a === b) continue;
    assert(nextSolo(a, b) === b, `S8 nextSolo(${a}, ${b}) must move the solo`);
    // Two taps on two different chips leaves exactly the second one soloed —
    // never both, which is what "one at a time" means when it is tested.
    assert(nextSolo(nextSolo(a, b), b) === null, `S8 double tap on ${b} must release`);
  }
}

// ---------------------------------------------------------------------------
// THE BANNER — it must carry the level when the source is turned down, and must
// never claim the export changed.
// ---------------------------------------------------------------------------
{
  const plain = soloBanner('beach.mp4');
  assert(/^Soloing beach\.mp4 —/.test(plain), `banner: ${plain}`);
  assert(/export/i.test(plain), 'banner must say the export is unchanged');
  assert(!/%/.test(plain), 'banner must not invent a level at unity');
  assert(!/%/.test(soloBanner('x', { level: 1 })), 'banner must not print 100%');
  assert(soloBanner('x', { level: 0.15 }).includes('at 15%'), 'banner must name a quieted level');
  assert(soloBanner('x', { level: 0 }).includes('at 0%'), 'banner must name a silenced level');
  const off = soloBanner('x', { audible: false });
  assert(/preview sound/.test(off), `banner must say why nothing is heard: ${off}`);
  // A NaN or out-of-range level says nothing rather than "at NaN%".
  assert(!/NaN|Infinity/.test(soloBanner('x', { level: NaN }) + soloBanner('x', { level: Infinity })),
    'banner must not print a non-finite level');
}

console.log(`solo.invariants: ${checks} checks, ${fails} failures`);
process.exit(fails ? 1 : 0);
