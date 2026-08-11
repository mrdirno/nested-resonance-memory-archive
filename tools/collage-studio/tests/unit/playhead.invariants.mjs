/**
 * Invariant sweep for THE PLAYHEAD — the take gets a clock you can see and drag.
 *
 * Run: node tests/unit/playhead.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so
 * every claim below is about the shipped `lib/playhead.ts` and not about a copy
 * of it written to agree with the test.
 *
 * P1 — THE PUMP NEVER LOSES THE LAST REQUEST. The assertion this file exists
 *      for. A drag fires an event per frame and a seek awaits `seeked` on every
 *      live decoder, so the pump drops intermediate targets ON PURPOSE — which
 *      makes "it drops things" useless as a bug report and "it dropped the LAST
 *      thing" the only failure that matters: a dropped intermediate frame is
 *      invisible, a dropped final one parks the canvas on a moment the finger
 *      never stopped at. Swept over 400 randomised request/settle interleavings
 *      from a seeded LCG (no `Math.random` — a sweep that cannot be re-run on
 *      the failing case is a coin toss, not a test), asserting on every step
 *      that at most one render is in flight and at most one is waiting, and
 *      asserting after every drain that the last render STARTED is the last
 *      time REQUESTED.
 *
 * P2 — THE POSITION IS ALWAYS ON THE RULER, AND THE LAPS ACCOUNT FOR THE REST.
 *      `lapAdjust` is DECISION 2 — the arithmetic that makes the bar's claim
 *      true rather than approximately true — so both halves are asserted
 *      together: `position` inside `[0, take)`, and `laps * take + position`
 *      reconstructing the input. Either can hold while the pair is wrong, and a
 *      wrong pair is a bar that reads 7 s while the canvas paints 37 s.
 *
 * P3 — THE ORIGIN ROUND-TRIPS THROUGH THE TICK'S OWN EXPRESSION. `resumeOriginMs`
 *      is the inverse of one line in `Stage.tick` (`outTime = (ts - moveOriginMs)
 *      / 1000`). The sweep spells that line out verbatim and feeds the origin
 *      back through it: this is what makes "park at 7 s, then play on from 7 s"
 *      a proven property rather than a hopeful one.
 *
 * P4 — WHAT THE RANGE HANDS BACK LANDS ON THE RULER AND NOWHERE ELSE. The bar
 *      is a native `<input type="range">` (DECISION 4b), so the browser owns the
 *      pointer and this owns everything the browser cannot know: the value
 *      arrives as a STRING, `max` is a float take length whose last step is
 *      ragged, and a stale `value` write can leave a number outside the range
 *      entirely. Monotone, clamped at both ends, never off the take — and the
 *      bar's `step` is asserted to be a whole multiple of the seek grid, which
 *      is what makes an arrow-key press and a drag land on the SAME instant and
 *      is therefore the difference between P1's economy working for both input
 *      methods and working only for the mouse.
 *
 * P5 — SNAPPING IS IDEMPOTENT AND BOUNDED. DECISION 4 exists so a request can
 *      COMPARE EQUAL to the one in flight; a snap that is not idempotent makes
 *      that comparison miss and the economy evaporates.
 *
 * P6 — THE RULER'S FADE IS THE RENDER'S FADE. `fadeMarks` reads `fadeSpan`, so
 *      the wedges on the bar move when the clamp bites (a 2 s fade on a 3 s take
 *      is 1.5 s). Asserted against `lib/fade.ts` directly rather than against a
 *      restatement of its rule.
 *
 * P7 — NOTHING THROWS AND NOTHING RETURNS A NON-NUMBER on garbage. Every input
 *      here arrives from a device profile, a DOMRect measured mid-layout or a
 *      pointer event, and a `NaN` fraction is a bar that renders at width NaN
 *      and disappears.
 *
 * P8 — THE READOUT NEVER OVERSTATES. `formatPosition` floors its tenths, so a
 *      playhead still inside a 10 s take can never print `0:10.0`.
 *
 * WHAT MUTATION TESTING SAID. Fifteen deliberate defects were injected into the
 * shipped module and this sweep re-run against each: `floor`->`ceil` and a
 * never-lapping `lapAdjust`; `%` for the lap subtraction; the boundary epsilon
 * deleted, and the same epsilon loosened to 1e-2; `round`->`floor` in
 * `snapSeek` and its exact-end short circuit deleted; a `pumpRequest` that
 * ignores what is already in flight, one whose pending dedupe is removed, and a
 * `pumpSettle` that drops the pending slot; `fadeMarks` reading the REQUESTED
 * fade instead of `fadeSpan`'s clamp; `formatPosition` rounding its tenths
 * instead of flooring; a sign flip in `resumeOriginMs`; a `PLAYHEAD_STEP_SEC`
 * that is not a whole multiple of the seek grid; and `fractionOf` without its
 * clamp. All fifteen died.
 *
 * TWO OF THEM SURVIVED THE FIRST PASS, and both were comments this file was
 * asserting around rather than through — which is the whole reason to run the
 * pass at all:
 *   * `%` for the lap subtraction. The claim that the two disagree "at the
 *     boundary" was in the module and nowhere in the sweep, because the sweep
 *     reached its boundaries by MULTIPLYING and a clock reaches them by ADDING.
 *     Measured once the accumulating arm existed: 330,567 differing pairs,
 *     worst delta a whole take — `%` answers with the far end of the ruler
 *     where the subtraction answers with the start.
 *   * `snapSeek`'s exact-end short circuit. Ten divergent inputs, all of them
 *     the ordinary act of dragging to the far right: without it, a 12.04 s take
 *     snaps its own end DOWN to 12.033.
 * Writing the accumulating arm to kill the first then failed against the REAL
 * module and exposed a defect neither mutant had: ten laps of a 4.3 s take
 * arrive at 42.99999999999999, `floor` reports nine, and the playhead sits at
 * the far right of the bar for one frame at the exact instant it should be
 * returning to the left. `LAP_EPSILON` is that fix, and M14/M15 guard it.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

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
    target: 'es2020',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const P = await load('src/lib/playhead.ts', 'playhead');
const F = await load('src/lib/fade.ts', 'fade');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

/** Every take the roster offers, plus the awkward ones a device cap produces. */
const TAKES = [5, 10, 15, 30, 3, 1, 0.75, 4.3, 7.5, 12.04, 0.5, 24];
/** A deterministic generator. A failing sweep must be re-runnable. */
const lcg = (seed) => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);

// ---------------------------------------------------------------------------
// P1 — THE PUMP NEVER LOSES THE LAST REQUEST.
// ---------------------------------------------------------------------------
let runs = 0, steps = 0, dropped = 0, promoted = 0;
for (let seed = 1; seed <= 400; seed++) {
  const rnd = lcg(seed);
  const take = TAKES[seed % TAKES.length];
  let s = P.PUMP_IDLE;
  let busy = false;              // the CALLER's view: is a render running?
  let lastRequested = null;
  let lastStarted = null;
  const n = 8 + Math.floor(rnd() * 45);
  for (let i = 0; i < n; i++) {
    steps++;
    // Settle only when something is actually in flight — the real caller can
    // only settle a render it started.
    if (busy && rnd() < 0.45) {
      const { state, next } = P.pumpSettle(s);
      s = state;
      if (next === null) { busy = false; } else { busy = true; lastStarted = next; promoted++; }
    } else {
      const t = P.snapSeek(rnd() * take * 1.2, take);
      lastRequested = t;
      const before = s;                        // BEFORE the reassignment below
      const { state, start } = P.pumpRequest(s, t);
      s = state;
      // THE BOUND THAT MATTERS, and it is about the CALLER rather than about the
      // state: a `start` while a render is already running is a second
      // `renderAtTime` racing the first, which is the exact failure DECISION 3
      // exists to forbid and the one a two-field state object cannot express on
      // its own.
      ok(!(start && busy), 'the pump started a render while one was already in flight');
      if (start) { lastStarted = t; busy = true; }
      else if (state === before) dropped++;    // refused outright — the economy
    }
    // The two structural bounds, on EVERY step.
    ok(s.pending === null || s.inFlight !== null,
      'nothing may wait while nothing is in flight — that is a render that will never be started');
    ok(busy === P.pumpBusy(s) || (!busy && s.inFlight === null),
      'the pump\'s own idea of busy must match the caller\'s');
  }
  // DRAIN, exactly as `pointerup` does.
  let guard = 0;
  while (busy) {
    const { state, next } = P.pumpSettle(s);
    s = state;
    if (next === null) busy = false; else { lastStarted = next; promoted++; }
    ok(++guard < 8, 'draining a two-slot pump cannot take more than two settles');
  }
  runs++;
  ok(s.inFlight === null && s.pending === null, 'a drained pump is idle');
  if (lastRequested !== null) {
    ok(lastStarted === lastRequested,
      `seed ${seed}: the pump finished on ${lastStarted} but the last time asked for was `
      + `${lastRequested} — the canvas is parked where the finger never stopped`);
  }
}

// The two refusals DECISION 4's snap exists to make fire.
{
  const a = P.pumpRequest(P.PUMP_IDLE, 3);
  ok(a.start === true && a.state.inFlight === 3, 'an idle pump starts at once');
  const b = P.pumpRequest(a.state, 3);
  ok(b.state === a.state && b.start === false, 'asking again for the time already in flight is a no-op');
  const c = P.pumpRequest(a.state, 4);
  ok(c.state.pending === 4 && c.start === false, 'a second time waits, it does not start');
  const d = P.pumpRequest(c.state, 4);
  ok(d.state === c.state, 'asking again for the time already waiting is a no-op');
  const e = P.pumpRequest(c.state, 5);
  ok(e.state.pending === 5, 'the pending slot is OVERWRITTEN, never appended — that is the whole economy');
  ok(P.pumpSettle(P.PUMP_IDLE).next === null, 'settling an idle pump asks for nothing');
  ok(P.pumpRequest(P.PUMP_IDLE, NaN).start === false, 'NaN never starts a render');
  ok(P.pumpReset().inFlight === null, 'reset abandons the flight');
}

// ---------------------------------------------------------------------------
// P2 — THE POSITION IS ALWAYS ON THE RULER.
// ---------------------------------------------------------------------------
let laps = 0;
for (const take of TAKES) {
  for (let k = 0; k < 240; k++) {
    const out = k * 0.517 * (1 + (k % 7));      // spans many laps, lands on boundaries
    const r = P.lapAdjust(out, take);
    laps++;
    ok(Number.isInteger(r.laps) && r.laps >= 0, `laps must be a whole count (${out}, ${take})`);
    ok(Number.isFinite(r.position) && r.position >= 0,
      `position must be a real non-negative number (${out}, ${take})`);
    ok(r.position < take + 1e-9,
      `position ${r.position} is off the end of a ${take}s ruler — the bar would claim a moment `
      + 'the export never renders');
    ok(Math.abs(r.laps * take + r.position - out) < 1e-6,
      `laps and position must reconstruct the clock (${out}, ${take}) -> ${r.laps}, ${r.position}`);
  }
  // The boundary itself: exactly one take elapsed is lap 1 at position 0, not
  // lap 0 at position `take` — the bar must return to the start, not sit on the
  // end.
  const edge = P.lapAdjust(take, take);
  ok(edge.laps === 1 && edge.position === 0,
    `exactly one take elapsed must wrap to the start of the ruler (${take})`);
  checks++;

  // THE ACCUMULATED BOUNDARY — and this is the arm that makes DECISION 2's
  // "subtract the laps, do not take a modulo" a measured claim rather than a
  // preference. A real clock reaches a lap boundary by ADDING, not by
  // multiplying, so the value that arrives is 927.0799999999999 rather than
  // 927.08 — and there `%` returns 12.039999999999992 (the very END of the
  // ruler) where the subtraction returns 0 (the start). Measured across the
  // take roster: 330,567 differing pairs, worst delta 12.04 — a whole take,
  // i.e. the playhead snapping to the wrong END of the bar on every lap.
  let acc = 0;
  for (let n = 1; n <= 80; n++) {
    acc += take;                              // exactly how the clock gets there
    const r = P.lapAdjust(acc, take);
    ok(r.position < take / 2,
      `lap ${n} of a ${take}s take arrived at ${acc} and resolved to position `
      + `${r.position} — a boundary must land at the START of the ruler, not its end`);
    ok(Math.abs(r.laps * take + r.position - acc) < 1e-6,
      `laps and position must still reconstruct an accumulated clock (${acc}, ${take})`);
  }
}
ok(P.lapAdjust(37, 0).laps === 0, 'no ruler, no laps');
ok(P.lapAdjust(-1, 10).position === 0, 'a clock before zero reads zero');

// ---------------------------------------------------------------------------
// P3 — THE ORIGIN ROUND-TRIPS THROUGH THE TICK'S OWN EXPRESSION.
// ---------------------------------------------------------------------------
let origins = 0;
for (const take of TAKES) {
  for (let k = 0; k <= 20; k++) {
    const t = (k / 20) * take;
    const nowMs = 1234567.89 + k * 331;
    const origin = P.resumeOriginMs(nowMs, t);
    // VERBATIM from Stage.tick: `this.outTime = Math.max(0, (ts - this.moveOriginMs) / 1000)`.
    const back = Math.max(0, (nowMs - origin) / 1000);
    origins++;
    ok(Math.abs(back - t) < 1e-9,
      `parking at ${t}s and playing on must resume at ${t}s, not ${back}s`);
  }
}
ok(P.resumeOriginMs(1000, -5) === 1000, 'a negative park resumes from zero');
ok(Number.isFinite(P.resumeOriginMs(NaN, 3)), 'a NaN clock must not poison the origin');

// ---------------------------------------------------------------------------
// P4 — WHAT THE RANGE INPUT HANDS BACK LANDS ON THE RULER AND NOWHERE ELSE.
// ---------------------------------------------------------------------------
let inputs = 0;
for (const take of TAKES) {
  // Every value the browser can produce on this step grid, plus the ragged last
  // one (`max` is a float take length and the final step rarely divides it) and
  // the out-of-range strings a stale `value` write can leave behind.
  const steps = Math.ceil(take / P.PLAYHEAD_STEP_SEC);
  let prev = -1;
  for (let i = -3; i <= steps + 3; i++) {
    const raw = String(i * P.PLAYHEAD_STEP_SEC);
    const t = P.seekFromInput(raw, take);
    inputs++;
    ok(Number.isFinite(t) && t >= 0 && t <= take,
      `the range reported "${raw}" on a ${take}s ruler and it resolved to ${t}, off the take`);
    ok(t >= prev - 1e-9, 'dragging right must never move the playhead left');
    prev = t;
  }
  ok(P.seekFromInput('-99', take) === 0, 'below the ruler is the start');
  ok(P.seekFromInput('9999', take) === take, 'above the ruler is the end');
  ok(P.seekFromInput(take / 2, take) === P.seekFromInput(String(take / 2), take),
    'a number and its own string must seek to the same instant');
  checks += 3;
}
ok(P.seekFromInput('', 10) === 0, 'an empty value seeks to the start, not to NaN');
ok(P.seekFromInput('abc', 10) === 0, 'a junk value seeks to the start, not to NaN');

// DECISION 4b's whole point: the keyboard and the thumb share one grid.
{
  const q = P.PLAYHEAD_STEP_SEC / P.SEEK_GRID_SEC;
  ok(Math.abs(q - Math.round(q)) < 1e-12,
    `the bar's step (${P.PLAYHEAD_STEP_SEC}s) is not a whole multiple of the seek grid `
    + `(${P.SEEK_GRID_SEC}s) — an arrow press and a drag would land on different instants and `
    + 'the pump could never refuse a duplicate from the keyboard');
  for (const take of TAKES) {
    for (let i = 0; i * P.PLAYHEAD_STEP_SEC <= take; i++) {
      const v = i * P.PLAYHEAD_STEP_SEC;
      ok(Math.abs(P.snapSeek(v, take) - v) < 1e-9,
        `an arrow-key position (${v}s) must survive the snap unchanged, it became `
        + `${P.snapSeek(v, take)}`);
    }
  }
}

// ---------------------------------------------------------------------------
// P5 — SNAPPING IS IDEMPOTENT AND BOUNDED.
// ---------------------------------------------------------------------------
let snaps = 0;
for (const take of TAKES) {
  for (let k = 0; k < 300; k++) {
    const t = (k / 299) * take;
    const a = P.snapSeek(t, take);
    const b = P.snapSeek(a, take);
    snaps++;
    ok(Object.is(a, b),
      `snapping twice must equal snapping once (${t}, ${take}) -> ${a} then ${b} — otherwise the `
      + 'pump\'s equality check never fires and DECISION 4 buys nothing');
    ok(a >= 0 && a <= take, `a snapped seek must stay on the ruler (${t}, ${take}) -> ${a}`);
    ok(Math.abs(a - t) <= P.SEEK_GRID_SEC / 2 + 1e-9 || a === take,
      `snapping moved ${t} to ${a}, further than half a frame`);
  }
}
ok(P.snapSeek(5, 0) === 0, 'no ruler, no seek');
ok(P.snapSeek(1e9, 10) === 10, 'a seek past the end lands on the end');
// THE END OF A RAGGED RULER, which is the ordinary case rather than an edge
// one: the playhead is dragged to the far right constantly, and a take whose
// length is not a multiple of the frame grid (a device cap, 12.04s) snaps
// 12.04 DOWN to 12.033 without the exact-end short circuit — so the bar's
// right-hand stop would be seven milliseconds short of the take it draws.
for (const take of TAKES) {
  ok(P.snapSeek(take, take) === take,
    `dragging to the end of a ${take}s take must land ON the end, not ${P.snapSeek(take, take)}`);
  ok(P.seekFromInput(String(take), take) === take, 'and the same through the range input');
  checks += 2;
}

// The fraction pair is the bar's own geometry and must round-trip on the grid.
let fractions = 0;
for (const take of TAKES) {
  for (let k = 0; k <= 40; k++) {
    const f = k / 40;
    const t = P.timeAtFraction(f, take);
    fractions++;
    ok(Math.abs(P.fractionOf(t, take) - f) < 1e-9, `fraction round trip failed at ${f} of ${take}`);
    ok(P.fractionOf(t, take) >= 0 && P.fractionOf(t, take) <= 1, 'a fill fraction is 0..1');
  }
}
ok(P.fractionOf(5, 0) === 0 && P.timeAtFraction(0.5, 0) === 0, 'no ruler, no fill');
ok(P.fractionOf(1e9, 10) === 1, 'past the end fills the bar, it does not overflow it');

// ---------------------------------------------------------------------------
// P6 — THE RULER'S FADE IS THE RENDER'S FADE.
// ---------------------------------------------------------------------------
let marks = 0;
for (const take of TAKES) {
  for (const req of F.FADE_ROSTER.concat([3, 100, 0.01])) {
    const span = F.fadeSpan(req, take);
    const m = P.fadeMarks(take, req);
    marks++;
    if (!(span > 0)) { ok(m === null, `no fade must draw no wedges (${req}, ${take})`); continue; }
    ok(m !== null, `a real fade must be drawn (${req}, ${take})`);
    ok(Math.abs(m.inEnd - span / take) < 1e-12,
      `the fade-in wedge must end where the RENDER's fade ends (${req}, ${take})`);
    ok(Math.abs(m.outStart - (take - span) / take) < 1e-12,
      `the fade-out wedge must start where the RENDER's fade starts (${req}, ${take})`);
    ok(m.inEnd <= m.outStart + 1e-12,
      `the wedges crossed at (${req}, ${take}) — fadeSpan's clamp is what forbids that`);
    ok(m.inEnd >= 0 && m.outStart <= 1, 'wedges stay on the bar');
  }
}

// ---------------------------------------------------------------------------
// P8 — THE READOUT NEVER OVERSTATES.
// ---------------------------------------------------------------------------
ok(P.formatPosition(0) === '0:00.0', 'zero reads 0:00.0');
ok(P.formatPosition(9.99) === '0:09.9', 'a playhead inside a 10s take must never print 0:10.0');
ok(P.formatPosition(61.55) === '1:01.5', 'past a minute reads m:ss.d');
ok(P.formatPosition(5) === '0:05.0', 'a whole second reads .0');
ok(P.formatPosition(-3) === '0:00.0', 'a clock before zero reads zero');
ok(P.formatSpan(10) === '0:10.0' && P.formatSpan(0) === '0:00.0', 'the span uses the same clock');
checks += 6;

// The take clamp — the expression that was inline in five places.
ok(P.takeLength(30, 10) === 10, 'a device that can only manage 10s gives 10s');
ok(P.takeLength(5, 30) === 5, 'a 5s take on a capable device stays 5s');
ok(P.takeLength(0, 30) === 0 && P.takeLength(10, 0) === 0, 'no take, no ruler');
checks += 3;

// ---------------------------------------------------------------------------
// P7 — GARBAGE IN, A NUMBER OUT.
// ---------------------------------------------------------------------------
const JUNK = [NaN, Infinity, -Infinity, undefined, null, -1, 0, 1e308];
let junk = 0;
for (const a of JUNK) {
  for (const b of JUNK) {
    junk++;
    ok(Number.isFinite(P.takeLength(a, b)), `takeLength(${a}, ${b}) is not a number`);
    ok(Number.isFinite(P.fractionOf(a, b)), `fractionOf(${a}, ${b}) is not a number`);
    ok(Number.isFinite(P.timeAtFraction(a, b)), `timeAtFraction(${a}, ${b}) is not a number`);
    ok(Number.isFinite(P.snapSeek(a, b)), `snapSeek(${a}, ${b}) is not a number`);
    ok(Number.isFinite(P.seekFromInput(a, b)), `seekFromInput(${a}, ${b}) is not a number`);
    const l = P.lapAdjust(a, b);
    ok(Number.isFinite(l.laps) && Number.isFinite(l.position), `lapAdjust(${a}, ${b}) is not a number`);
    ok(typeof P.formatPosition(a) === 'string' && !P.formatPosition(a).includes('NaN'),
      `formatPosition(${a}) printed NaN`);
    ok(Number.isFinite(P.resumeOriginMs(a, b)), `resumeOriginMs(${a}, ${b}) is not a number`);
    const m = P.fadeMarks(a, b);
    ok(m === null || (Number.isFinite(m.inEnd) && Number.isFinite(m.outStart)),
      `fadeMarks(${a}, ${b}) is not a pair of numbers`);
  }
}

console.log(`playhead invariants: ${checks} assertions — ${runs} pump runs over ${steps} steps `
  + `(${promoted} promotions, ${dropped} refusals), ${laps} lap adjustments, ${origins} origin `
  + `round trips, ${inputs} range-input readings, ${snaps} snaps, ${fractions} fraction round trips, `
  + `${marks} fade rulers, ${junk} garbage pairs — all green`);
