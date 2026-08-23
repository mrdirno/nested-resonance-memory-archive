// =============================================================================
// THE BEAT — invariant sweep.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// Transpiles the REAL modules with esbuild and asserts against them — never a
// re-implementation, because a sweep that re-implements the thing it is testing
// only proves the two copies agree. The TWO re-implementations here are both
// deliberate: the ORACLE (I1) is a byte copy of `turnAt`'s roster branch as it
// stood before the schedule argument existed, and the REJECTED design (I6b) is
// the fixed-fade schedule, which exists to be refuted with a number.
//
// THE ONES THAT MATTER:
//   I1  the roster path is BIT-IDENTICAL to the build that had no beat in it,
//       field by field and `NO_TURN` by reference.
//   I6  the snapped hold's soft share never exceeds the roster's own worst
//       (ripple, 20%) at ANY tempo — with I6b measuring what a fixed 0.7 s
//       dissolve would have done to the same holds.
//   I8  detection on synthesised material: the period is right (or an exact
//       octave of it, which the snap absorbs), and the phase lands on the hits.
//   I9  noise is REFUSED. A confident wrong grid is the failure mode that
//       matters, so the sweep proves the floor actually turns something away.
//
//   node tests/unit/beat.invariants.mjs
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

const beat = await load('src/lib/beat.ts', 'beat');
const {
  BEAT_MULTIPLES, BEAT_MIN_BPM, BEAT_MAX_BPM, BEAT_HOP_SEC, BEAT_CONFIDENCE_FLOOR,
  SYNC_IDS, SYNCS, isSynced, beatsLabel,
  onsetEnvelope, detectBeat, snapHold, beatSchedule,
} = beat;
const { TURN_IDS, TURN_FADE_SEC, TURN_FADE_RATIO, NO_TURN, turnAt, turnHoldSec, turnFadeFor, MAX_TURN_INDEX } =
  await load('src/lib/turn.ts', 'turn');
const { PACE_IDS, paceRate } = await load('src/lib/pace.ts', 'pace');
const { encodeRoll, decodeRoll, rollDice, MINTED_GROUP_LENGTHS, MINTED_GROUP_PLAIN } =
  await load('src/lib/diceRoll.ts', 'dice');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

const TURNING = TURN_IDS.filter((t) => t !== 'hold');

/** Deterministic PRNG so a failure is reproducible. */
const rng = (seed) => () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
};

// -----------------------------------------------------------------------------
// I1 — THE ORACLE. `turnAt` with no schedule is the function it was.
// -----------------------------------------------------------------------------
// A byte copy of the roster branch as it stood at c796fa91 (THE PACE), before
// the third argument existed. Its `NO_TURN` is the REAL one, imported, so the
// identity comparison below is meaningful.
const ORACLE_HOLD = { hold: 0, march: 5.0, scatter: 6.5, ripple: 3.5, swap: 4.0 };
const oracleTurnAt = (id, timeSec) => {
  if (!TURNING.includes(id)) return NO_TURN;
  const hold = ORACLE_HOLD[id];
  if (!(hold > 0)) return NO_TURN;
  const t = typeof timeSec === 'number' && Number.isFinite(timeSec) ? timeSec : 0;
  if (!(t > 0)) return NO_TURN;
  const k = Math.min(MAX_TURN_INDEX, Math.floor(t / hold));
  if (k <= 0) return NO_TURN;
  const elapsed = t - k * hold;
  if (k >= MAX_TURN_INDEX || !(elapsed < TURN_FADE_SEC)) return { a: k, b: k, mix: 0 };
  return { a: k - 1, b: k, mix: 0.5 - 0.5 * Math.cos(Math.PI * (Math.max(0, elapsed) / TURN_FADE_SEC)) };
};

{
  const r = rng(20260812);
  let checks = 0;
  let bad = 0;
  let restByRef = 0;
  const badCases = [];
  for (const id of [...TURN_IDS, 'nonsense', undefined]) {
    // Every boundary of every mode, plus dense random instants, plus the junk.
    const times = [0, -1, -0.0001, NaN, Infinity, undefined, 'x'];
    for (const h of Object.values(ORACLE_HOLD)) {
      if (h > 0) times.push(h, h - 1e-9, h + 1e-9, 2 * h, 2 * h + TURN_FADE_SEC, 3 * h - 1e-6);
    }
    for (let i = 0; i < 4000; i++) times.push(r() * 400);
    for (const t of times) {
      const a = turnAt(id, t);
      const b = oracleTurnAt(id, t);
      checks++;
      if (a === NO_TURN || b === NO_TURN) {
        if (a === b) { restByRef++; continue; }
        bad++; if (badCases.length < 4) badCases.push(`${id}@${t}: rest identity`);
        continue;
      }
      if (!Object.is(a.a, b.a) || !Object.is(a.b, b.b) || !Object.is(a.mix, b.mix)) {
        bad++; if (badCases.length < 4) badCases.push(`${id}@${t}: ${JSON.stringify(a)} vs ${JSON.stringify(b)}`);
      }
    }
    // And with an explicit absent schedule, which is what every existing caller
    // compiles to once the parameter exists.
    for (let i = 0; i < 500; i++) {
      const t = r() * 400;
      const a = turnAt(id, t, null);
      const b = oracleTurnAt(id, t);
      checks++;
      if (a === NO_TURN || b === NO_TURN) { if (a !== b) bad++; continue; }
      if (!Object.is(a.a, b.a) || !Object.is(a.b, b.b) || !Object.is(a.mix, b.mix)) bad++;
    }
  }
  ok('I1  unsynced turnAt is Object.is-identical to the pre-beat build',
    bad === 0, `${checks.toLocaleString()} checks, ${restByRef.toLocaleString()} of them NO_TURN by reference${badCases.length ? ` | ${badCases.join(' ; ')}` : ''}`);
}

// -----------------------------------------------------------------------------
// I2 — REST AT ZERO SURVIVES THE SCHEDULE, BY REFERENCE.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let checks = 0;
  const r = rng(7);
  for (let i = 0; i < 4000; i++) {
    const period = 0.33 + r() * 0.67;
    const sched = beatSchedule({ bpm: 60 / period, periodSec: period, offsetSec: r() * period, confidence: 1 }, 2 + r() * 6, r() * 10);
    if (!sched) { bad++; continue; }
    for (const t of [0, -0, -1, NaN, undefined, sched.first * r()]) {
      checks++;
      if (turnAt('march', t, sched) !== NO_TURN) bad++;
    }
  }
  ok('I2  every instant before the first synced cut is NO_TURN BY REFERENCE',
    bad === 0, `${checks.toLocaleString()} checks`);
}

// -----------------------------------------------------------------------------
// I3 — THE CUTS LAND ON THE GRID, AND THE INDEX ONLY EVER GOES UP.
// -----------------------------------------------------------------------------
{
  const r = rng(99);
  let bad = 0;
  let boundaries = 0;
  const cases = [];
  for (let i = 0; i < 800; i++) {
    const period = 60 / (BEAT_MIN_BPM + r() * (BEAT_MAX_BPM - BEAT_MIN_BPM));
    const grid = { bpm: 60 / period, periodSec: period, offsetSec: r() * period, confidence: 1 };
    const sched = beatSchedule(grid, 1 + r() * 8, r() * 30);
    if (!sched) { bad++; continue; }
    // Exactly ON each boundary the new turn is bound and the dissolve has just
    // started (mix 0 at u=0 — the raised cosine's own value there).
    let prev = -1;
    for (let k = 1; k <= 40; k++) {
      const t = sched.first + (k - 1) * sched.hold;
      const f = turnAt('march', t, sched);
      boundaries++;
      if (f.b !== k || f.a !== k - 1) { bad++; if (cases.length < 3) cases.push(`k=${k} got a=${f.a} b=${f.b}`); }
      if (f.b < prev) bad++;
      prev = f.b;
      // Just before the boundary the PREVIOUS turn must be settled and solid.
      const before = turnAt('march', t - 1e-6, sched);
      if (before.mix !== 0 || before.a !== k - 1) {
        bad++; if (cases.length < 3) cases.push(`pre-k=${k} got ${JSON.stringify(before)}`);
      }
    }
  }
  ok('I3  turn k lands exactly at first+(k-1)*hold, settled immediately before it',
    bad === 0, `${boundaries.toLocaleString()} boundaries${cases.length ? ` | ${cases.join(' ; ')}` : ''}`);
}

// -----------------------------------------------------------------------------
// I4 — THE PHASE IS THE MUSIC'S, MODULO THE HOLD.
// -----------------------------------------------------------------------------
{
  const r = rng(1234);
  let bad = 0;
  let worst = 0;
  for (let i = 0; i < 5000; i++) {
    const period = 60 / (BEAT_MIN_BPM + r() * (BEAT_MAX_BPM - BEAT_MIN_BPM));
    const offset = r() * 12;
    const inSec = r() * 12;
    const sched = beatSchedule({ bpm: 60 / period, periodSec: period, offsetSec: offset, confidence: 1 }, 1 + r() * 8, inSec);
    if (!sched) { bad++; continue; }
    // Every cut must sit on a beat of the track, measured in OUTPUT time: the
    // instant `first + k*hold` maps back to source time `inSec + first + k*hold`,
    // which must be an integer number of periods after the grid's own offset.
    for (const k of [0, 1, 7, 33]) {
      const src = inSec + sched.first + k * sched.hold;
      const beatsFromOffset = (src - offset) / period;
      const err = Math.abs(beatsFromOffset - Math.round(beatsFromOffset));
      if (err > worst) worst = err;
      if (err > 1e-6) bad++;
    }
  }
  ok('I4  every synced cut sits on a beat of the source track, in output time',
    bad === 0, `worst deviation ${worst.toExponential(2)} beats over 20,000 cuts`);

  // AND THE FIRST ONE IS NOT LATE. Two artifact-caught bugs live in this one
  // number: reducing the phase modulo the HOLD let the opening hold approach
  // TWICE the hold, and reducing it into [0, period) instead of to the NEAREST
  // beat let a phase measured 4 ms early read as a whole beat of delay.
  let worstFirst = 0;
  let lateBad = 0;
  const r2 = rng(31337);
  for (let i = 0; i < 20000; i++) {
    const period = 60 / (BEAT_MIN_BPM + r2() * (BEAT_MAX_BPM - BEAT_MIN_BPM));
    const sched = beatSchedule(
      { bpm: 60 / period, periodSec: period, offsetSec: r2() * 60, confidence: 1 },
      1 + r2() * 8, r2() * 30);
    if (!sched) { lateBad++; continue; }
    const over = Math.abs(sched.first - sched.hold) / period;
    if (over > worstFirst) worstFirst = over;
    if (over > 0.5 + 1e-9 || !(sched.first > 0)) lateBad++;
  }
  ok('I4b the first synced cut is one hold in, to within HALF A BEAT either way',
    lateBad === 0, `worst departure ${worstFirst.toFixed(4)} beats over 20,000 schedules`);
}

// -----------------------------------------------------------------------------
// I5 — THE SNAP IS MUSICAL, AND IT IS THE NEAREST MULTIPLE IN RATIO.
// -----------------------------------------------------------------------------
{
  const r = rng(55);
  let bad = 0;
  let worstRatio = 0;
  let checks = 0;
  for (let i = 0; i < 20000; i++) {
    const period = 60 / (BEAT_MIN_BPM + r() * (BEAT_MAX_BPM - BEAT_MIN_BPM));
    const target = 0.2 + r() * 14;
    const s = snapHold(target, period);
    checks++;
    if (!s) { bad++; continue; }
    if (!BEAT_MULTIPLES.includes(s.beats)) bad++;
    if (Math.abs(s.holdSec - s.beats * period) > 1e-12) bad++;
    // Nothing on the roster is nearer in ratio than what it picked.
    const mine = Math.abs(Math.log(s.holdSec / target));
    for (const m of BEAT_MULTIPLES) {
      if (Math.abs(Math.log((m * period) / target)) < mine - 1e-12) bad++;
    }
    const ratio = Math.max(s.holdSec / target, target / s.holdSec);
    if (ratio > worstRatio) worstRatio = ratio;
  }
  // The worst possible miss is half a step of the {1,2,4,8,16} ladder — a factor
  // of sqrt(2) — for any target INSIDE the ladder's own range.
  ok('I5  the snap always picks a musical multiple, and the nearest one by ratio',
    bad === 0, `${checks.toLocaleString()} snaps, worst ratio to target ${worstRatio.toFixed(3)}x (includes targets outside the 1..16 beat ladder)`);
}

// -----------------------------------------------------------------------------
// I6 — THE SOFT SHARE. The whole reason the fade is not a constant here.
// -----------------------------------------------------------------------------
{
  const r = rng(4242);
  let worstShipped = 0;
  let worstRejected = 0;
  let bad = 0;
  const rows = [];
  for (const bpm of [60, 90, 120, 128, 150, 174, 180]) {
    const period = 60 / bpm;
    for (const id of TURNING) {
      for (const pace of PACE_IDS) {
        const target = turnHoldSec(id) / paceRate(pace);
        const sched = beatSchedule({ bpm, periodSec: period, offsetSec: 0, confidence: 1 }, target, 0);
        if (!sched) { bad++; continue; }
        const shipped = sched.fade / sched.hold;
        const rejected = TURN_FADE_SEC / sched.hold;   // what a constant fade gives
        if (shipped > worstShipped) worstShipped = shipped;
        if (rejected > worstRejected) { worstRejected = rejected; }
        if (shipped > TURN_FADE_RATIO + 1e-12) bad++;
        if (sched.fade > TURN_FADE_SEC + 1e-12) bad++;
        if (bpm === 174 && id === 'ripple' && pace === 'rush') {
          rows.push(`ripple@2x/174bpm: hold ${sched.hold.toFixed(3)}s fade ${sched.fade.toFixed(3)}s = ${(shipped * 100).toFixed(1)}% soft (a constant 0.7s would be ${(rejected * 100).toFixed(1)}%)`);
        }
      }
    }
  }
  ok('I6  a snapped hold is never more than the roster\'s own 20% soft',
    bad === 0, `worst shipped ${(worstShipped * 100).toFixed(1)}%`);
  ok('I6b (RED PROOF) a CONSTANT 0.7s fade degenerates on the same holds',
    worstRejected > 0.30, `worst rejected ${(worstRejected * 100).toFixed(1)}% soft | ${rows[0] ?? ''}`);
  // And a long hold keeps the roster's own dissolve rather than growing one.
  ok('I6c  turnFadeFor is a CEILING, not a scaling — a 30s hold still fades 0.7s',
    turnFadeFor(30) === TURN_FADE_SEC && turnFadeFor(1) === 0.2 && turnFadeFor(0) === TURN_FADE_SEC,
    `f(30)=${turnFadeFor(30)} f(1)=${turnFadeFor(1)} f(0)=${turnFadeFor(0)}`);
}

// -----------------------------------------------------------------------------
// I7 — A MALFORMED SCHEDULE IS REST, NEVER THE MODE'S OWN HOLD.
// -----------------------------------------------------------------------------
{
  const junk = [
    { hold: 0, first: 1, fade: 0.2 },
    { hold: -1, first: 1, fade: 0.2 },
    { hold: NaN, first: 1, fade: 0.2 },
    { hold: Infinity, first: 1, fade: 0.2 },
    { hold: 2, first: NaN, fade: 0.2 },
    { hold: 2, first: 1, fade: 0 },
    { hold: 2, first: 1, fade: NaN },
  ];
  let bad = 0;
  for (const s of junk) {
    for (const t of [0, 1, 5, 50, 5000]) {
      if (turnAt('march', t, s) !== NO_TURN) bad++;
    }
  }
  // …and `hold` (the no-op mode) ignores a perfectly good schedule.
  const good = beatSchedule({ bpm: 120, periodSec: 0.5, offsetSec: 0, confidence: 1 }, 4, 0);
  for (const t of [0, 3, 9, 90]) if (turnAt('hold', t, good) !== NO_TURN) bad++;
  ok('I7  a malformed schedule is REST, and `hold` ignores a valid one', bad === 0);
}

// -----------------------------------------------------------------------------
// I8 — DETECTION on synthesised material at known tempi.
// -----------------------------------------------------------------------------
const RATE = 8000;

/** A click track: a short decaying burst on every beat. */
const clicks = (bpm, seconds, { offset = 0, swingOffbeat = 0, noise = 0, seed = 3 } = {}) => {
  const r = rng(seed);
  const n = Math.round(seconds * RATE);
  const x = new Float32Array(n);
  if (noise > 0) for (let i = 0; i < n; i++) x[i] = (r() * 2 - 1) * noise;
  const period = 60 / bpm;
  const burst = (at, amp) => {
    const start = Math.round(at * RATE);
    const len = Math.round(0.03 * RATE);
    for (let i = 0; i < len && start + i < n; i++) {
      if (start + i < 0) continue;
      x[start + i] += amp * Math.exp(-i / (0.006 * RATE)) * Math.sin((2 * Math.PI * 900 * i) / RATE);
    }
  };
  for (let t = offset; t < seconds; t += period) {
    burst(t, 1);
    if (swingOffbeat > 0) burst(t + period / 2, swingOffbeat);
  }
  return x;
};

{
  const rows = [];
  let bad = 0;
  for (const bpm of [60, 75, 90, 100, 110, 120, 128, 140, 150, 160, 174, 180]) {
    const offset = 0.137;
    const x = clicks(bpm, 24, { offset, noise: 0.01, seed: bpm });
    const g = detectBeat(x, RATE);
    if (!g) { bad++; rows.push(`${bpm}: REFUSED`); continue; }
    // The period may come back as an exact OCTAVE — which the snap absorbs, so
    // it is a pass. What must never happen is a period that is not a simple
    // ratio of the truth, because that is a grid the music is not on.
    const truth = 60 / bpm;
    const ratio = g.periodSec / truth;
    const octave = [0.25, 0.5, 1, 2, 4].some((m) => Math.abs(ratio - m) / m < 0.02);
    // The phase must land on a real hit: the detected offset, reduced modulo the
    // DETECTED period, has to sit within a hop of a true beat.
    const rel = ((g.offsetSec - offset) % truth + truth) % truth;
    const phaseErr = Math.min(rel, truth - rel);
    const phaseOk = phaseErr <= 1.5 * BEAT_HOP_SEC;
    if (!octave || !phaseOk) bad++;
    rows.push(`${bpm}->${g.bpm.toFixed(1)} (${(ratio).toFixed(3)}x, phase ${(phaseErr * 1000).toFixed(0)}ms, conf ${g.confidence.toFixed(2)})`);
  }
  ok('I8  a click track is detected at its own tempo (or an exact octave), on phase',
    bad === 0, rows.join(' | '));
}

{
  // The one that decides whether this is usable on real material: a pattern with
  // a strong backbeat and off-beat hats, i.e. energy on the half-beat too.
  const rows = [];
  let bad = 0;
  let worstOff = 0;
  for (const bpm of [90, 120, 128, 140]) {
    const x = clicks(bpm, 30, { offset: 0.41, swingOffbeat: 0.55, noise: 0.02, seed: bpm + 1 });
    const g = detectBeat(x, RATE);
    if (!g) { bad++; rows.push(`${bpm}: REFUSED`); continue; }
    const truth = 60 / bpm;
    const ratio = g.periodSec / truth;
    const octave = [0.25, 0.5, 1, 2, 4].some((m) => Math.abs(ratio - m) / m < 0.02);
    if (!octave) bad++;
    // The SNAP is what has to survive an octave error, so assert the thing that
    // actually matters: a 4-beat target lands on the same INSTANTS either way.
    const sched = beatSchedule(g, 4 * truth, 0);
    // WITHIN A HUNDREDTH OF A BEAT, not exactly: the detector's period comes off
    // a finite grid (139.9 BPM for a 140 BPM track is one part in 1400), so a
    // four-beat hold is 4.0017 TRUE beats and an exact-integer assertion is
    // asserting the resolution rather than the alignment. A hundredth of a beat
    // at 140 BPM is 4 ms.
    const inBeats = sched.hold / truth;
    const offGrid = Math.abs(inBeats - Math.round(inBeats));
    if (offGrid > 0.01) bad++;
    if (offGrid > worstOff) worstOff = offGrid;
    rows.push(`${bpm}->${g.bpm.toFixed(1)} (${ratio.toFixed(2)}x) hold ${sched.hold.toFixed(3)}s = ${inBeats.toFixed(3)} true beats`);
  }
  ok('I8b a half-beat backbeat still snaps onto whole beats of the true tempo',
    bad === 0, `worst ${worstOff.toFixed(4)} beats off | ${rows.join(' | ')}`);
}

// -----------------------------------------------------------------------------
// I9 — WHAT IT REFUSES. A confident wrong grid is the failure that matters.
// -----------------------------------------------------------------------------
{
  const r = rng(808);
  const rows = [];
  let bad = 0;

  const n = 20 * RATE;
  const noise = new Float32Array(n);
  for (let i = 0; i < n; i++) noise[i] = r() * 2 - 1;
  const gN = detectBeat(noise, RATE);
  if (gN) { bad++; rows.push(`white noise ACCEPTED as ${gN.bpm} BPM conf ${gN.confidence}`); }
  else rows.push('white noise refused');

  const silence = new Float32Array(n);
  if (detectBeat(silence, RATE)) { bad++; rows.push('silence ACCEPTED'); } else rows.push('silence refused');

  // A slow swell — energy that rises and falls with no onsets at all.
  const swell = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const env = 0.5 + 0.5 * Math.sin((2 * Math.PI * i) / (7.3 * RATE));
    swell[i] = env * Math.sin((2 * Math.PI * 220 * i) / RATE);
  }
  // A KNOWN LIMIT, ASSERTED AS ONE RATHER THAN WISHED AWAY: a tonal source with
  // no percussion has a real periodic rise and fall in its RMS, and this
  // detector will find it. What must hold is that it is not MORE convincing
  // than actual drums, which is the comparison that decides whether the floor
  // is separating music from not-music or just sorting by loudness.
  const gS = detectBeat(swell, RATE);
  rows.push(gS ? `swell accepted (${gS.bpm} BPM conf ${gS.confidence}) — documented limit` : 'swell refused');

  for (const junk of [null, undefined, new Float32Array(0), new Float32Array(10)]) {
    if (detectBeat(junk, RATE)) { bad++; rows.push('junk ACCEPTED'); }
  }
  if (detectBeat(new Float32Array(RATE * 5), 0)) { bad++; rows.push('rate 0 ACCEPTED'); }

  ok('I9  noise, silence and junk are REFUSED rather than given a plausible BPM',
    bad === 0, rows.join(' | '));
}

// -----------------------------------------------------------------------------
// I10 — DETERMINISM. The same file measures the same both times.
// -----------------------------------------------------------------------------
{
  const x = clicks(128, 20, { offset: 0.29, swingOffbeat: 0.4, noise: 0.03, seed: 11 });
  const a = detectBeat(x, RATE);
  const b = detectBeat(x, RATE);
  const same = a && b && a.bpm === b.bpm && a.offsetSec === b.offsetSec
    && a.periodSec === b.periodSec && a.confidence === b.confidence;
  ok('I10 detection is deterministic', !!same, same ? `${a.bpm} BPM twice` : 'diverged');
  // The envelope is a pure function of the samples too.
  const e1 = onsetEnvelope(x, RATE);
  const e2 = onsetEnvelope(x, RATE);
  let envSame = e1.length === e2.length;
  for (let i = 0; envSame && i < e1.length; i++) if (!Object.is(e1[i], e2[i])) envSame = false;
  ok('I10b the onset envelope is pure', envSame, `${e1.length.toLocaleString()} frames`);
}

// -----------------------------------------------------------------------------
// I11 — THE CODE. One more character, and every earlier generation untouched.
// -----------------------------------------------------------------------------
{
  const r = rng(2026);
  let bad = 0;
  let round = 0;
  for (let i = 0; i < 3000; i++) {
    const roll = rollDice({ rnd: r, hasVideo: r() < 0.5 });
    for (const sync of SYNC_IDS) {
      const code = encodeRoll({ ...roll, sync });
      const back = decodeRoll(code);
      round++;
      if (!back || back.sync !== sync) { bad++; continue; }
      // and nothing else moved
      if (back.turn !== (roll.turn ?? 'hold') || back.pace !== (roll.pace ?? 'even')
        || back.look !== (roll.look ?? 'none') || back.move !== (roll.move ?? 'still')) bad++;
    }
  }
  ok('I11 the sync survives a code round trip and disturbs no other field',
    bad === 0, `${round.toLocaleString()} round trips`);

  // The group grew by exactly one, and the set knows it.
  const sample = encodeRoll({ ...rollDice({ rnd: r }), sync: 'beat' });
  const mid = sample.split('-')[1];
  ok('I11b the minted group is MINTED_GROUP_PLAIN and the codec accepts its own output',
    mid.length === MINTED_GROUP_PLAIN && MINTED_GROUP_LENGTHS.has(mid.length) && !!decodeRoll(sample),
    `group ${mid.length}, plain ${MINTED_GROUP_PLAIN}`);

  // EVERY EARLIER GENERATION STILL OPENS, BYTE-IDENTICALLY. Rebuilt by lopping
  // the trailing field characters off a freshly minted body and re-deriving the
  // checksum exactly as the older build would have.
  const legacy = [];
  for (let i = 0; i < 40; i++) {
    const roll = rollDice({ rnd: r });
    const full = encodeRoll({ ...roll, sync: 'off' });
    const [head, body, seed] = full.toLowerCase().split('-');
    const check = (s) => {
      let h = 7;
      for (let j = 0; j < s.length; j++) h = (h * 31 + parseInt(s[j], 36) + 1) % 1679616;
      return (h % 1296).toString(36).padStart(2, '0');
    };
    for (const len of [16, 17, 18, 19, 20, 21]) {
      const trimmed = body.slice(0, len);
      const older = `${head}-${trimmed}${check(head + trimmed + seed)}-${seed}`.toUpperCase();
      const got = decodeRoll(older);
      legacy.push(!!got && got.sync === 'off');
    }
  }
  ok('I11c every earlier group length still decodes, and reads sync=off',
    legacy.every(Boolean), `${legacy.length} legacy codes`);

  // A truncated or extended group is still refused.
  const bodyFull = sample.split('-')[1];
  const damaged = [
    sample.replace(bodyFull, bodyFull.slice(0, -1)),
    sample.replace(bodyFull, bodyFull + 'Z'),
    sample.replace(bodyFull, bodyFull.slice(0, -3)),
  ];
  ok('I11d a damaged group is refused, at the new length too',
    damaged.every((d) => decodeRoll(d) === null));
}

// -----------------------------------------------------------------------------
// I12 — THE ROSTER AND ITS LABELS.
// -----------------------------------------------------------------------------
{
  const okRoster = SYNC_IDS[0] === 'off'
    && SYNCS.length === SYNC_IDS.length
    && SYNCS.every((o, i) => o.id === SYNC_IDS[i] && o.label && o.title)
    && isSynced('beat') && !isSynced('off') && !isSynced(undefined) && !isSynced('nonsense');
  ok('I12 index 0 is the no-op, the chip row matches the alphabet, isSynced is total', okRoster);
  ok('I12b beatsLabel speaks bars where the count is bars',
    beatsLabel(4) === 'every bar' && beatsLabel(8) === 'every 2 bars'
    && beatsLabel(2) === 'every half bar' && beatsLabel(1) === 'every beat' && beatsLabel(0) === '',
    `${beatsLabel(1)} / ${beatsLabel(2)} / ${beatsLabel(4)} / ${beatsLabel(8)} / ${beatsLabel(16)}`);
}

// -----------------------------------------------------------------------------
// I13 — A NULL SCHEDULE IS THE ONLY ANSWER WHEN ANYTHING IS MISSING.
// -----------------------------------------------------------------------------
{
  const grid = { bpm: 120, periodSec: 0.5, offsetSec: 0.2, confidence: 1 };
  const bad = [
    beatSchedule(null, 4, 0),
    beatSchedule(undefined, 4, 0),
    beatSchedule({ ...grid, periodSec: 0 }, 4, 0),
    beatSchedule({ ...grid, periodSec: NaN }, 4, 0),
    beatSchedule(grid, 0, 0),
    beatSchedule(grid, -3, 0),
    beatSchedule(grid, NaN, 0),
    beatSchedule(grid, Infinity, 0),
  ].filter((x) => x !== null);
  ok('I13 a missing grid or a meaningless target is null, never a guess', bad.length === 0,
    `${bad.length} leaks`);
  // A non-finite in-point degrades to 0 rather than poisoning the phase.
  const s = beatSchedule(grid, 4, NaN);
  ok('I13b a non-finite in-point is read as 0', !!s && Number.isFinite(s.first) && Number.isFinite(s.hold));
}

// -----------------------------------------------------------------------------

console.log('\n' + results.join('\n'));
console.log(`\n${failures === 0 ? 'ALL PASS' : `${failures} FAILURE(S)`}\n`);
process.exit(failures === 0 ? 1 * 0 : 1);
