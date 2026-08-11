// src/lib/playhead.ts
// -----------------------------------------------------------------------------
// THE PLAYHEAD — the take gets a clock you can see and drag.
//
// WHY THIS FILE EXISTS
//   Every capability this app has shipped for six cycles is about TIME — THE
//   MOVE, the trim window, the soundtrack's range, the lap schedule, THE FADE —
//   and not one of them is observable without exporting a file. The preview
//   drifts forever with no beginning, no end and no position, so "does the
//   fade-out land where I think it does" costs a render, and "what does this
//   look like at seven seconds" is unanswerable. Two separate rungs of the
//   capability ladder ask for the same widget in the same words: the timeline
//   rung owes `playhead scrub`, and THE MOVE's own rung says "the honest next
//   cut is a scrub or a 'show me' that runs one cycle, which is the same widget
//   the timeline rung wants anyway."
//
//   This file is the arithmetic of that widget. It owns four things nothing
//   else in the tree owns: WHERE the take's clock is, WHAT a pointer on a bar
//   means, HOW a drag is throttled into seeks, and WHERE the fade sits on the
//   ruler. The Stage owns the seek itself (it already does — `renderAtTime`),
//   and the component owns the pixels.
//
// DECISION 1 — THE BAR MEASURES THE TAKE, AND THE TAKE IS THE ONLY SPAN THERE
//   IS. The tempting alternative is to measure the longest clip, which is what
//   a conventional NLE timeline shows. It is wrong here twice: a collage of
//   photographs has no clip at all (and is exactly the case THE MOVE and THE
//   SOUNDTRACK exist to serve), and the file that comes out is `seconds` long
//   whatever the sources are — a 3 s clip laps three times inside a 10 s take
//   and a 30 s clip is cut off at 10. The take length is the one number every
//   surface already agrees on, so it is the ruler.
//
// DECISION 2 — THE CLOCK LAPS THE TAKE, BECAUSE A WRAPPED BAR OVER AN
//   UNWRAPPED CLOCK IS A LIE. `outTime` counts up from the moment the Stage
//   started and never wraps; the bar has to answer "where am I" at t = 37 s of
//   a 10 s take. Showing `37 mod 10 = 7` while the move is at phase 37 is
//   precisely the preview-is-not-the-file divergence ONE LAYOUT and THE TITLE
//   were built to prevent, and it is not hypothetical arithmetic: the move is
//   periodic on a FIXED 12 s cycle (`motion.MOVE_CYCLE_SEC`), deliberately not
//   on the take, so at t = 37 the picture is at move phase 1 and the bar would
//   claim 7. The fix is not a cleverer modulo, it is to make the statement
//   TRUE — wrap the CLOCK, not just its readout. `lapAdjust` returns how many
//   whole takes have elapsed so the caller can push the origin forward by
//   exactly that much: the position lands inside the ruler and the move at
//   bar-position p is the move the exporter renders at p.
//
//   It is a jump, not a subtraction: a backgrounded tab returns with minutes of
//   elapsed time, and one `-= take` would leave the bar off the end of its own
//   ruler until the next frame. The laps are counted and applied at once.
//
// DECISION 2b — AND THE LAP RE-SEEKS NOTHING. The tempting next step is to
//   restart every clip and the music at the lap, so the whole composition
//   loops the take. It is deliberately NOT taken here, for the reason the
//   ladder already gave for the end-of-take fade: it would change what every
//   preview this app has ever shown does, as a rider on a feature, and that is
//   a decision to make on its own. It also buys nothing the bar needs — a
//   clip's LIVE position is governed by its element (native loop, or the
//   `enforceWindow` watchdog) while the EXPORT computes `sourceTimeAt`, so the
//   two already free-run against each other from the first frame; that
//   divergence is pre-existing, documented on the trim rung, and orthogonal to
//   a ruler. The clock is what the bar measures and the clock is what laps.
//
//   A SCRUB is the opposite case and does seek everything, clips and music
//   alike: parking on 7 s is a deliberate act by someone who asked for that
//   instant, so it is the one place the cost of an exact seek is obviously
//   worth paying.
//
// DECISION 3 — A DRAG IS LATEST-WINS, NOT A QUEUE. A seek is `renderAtTime`,
//   which awaits `seeked` on every live decoder — tens of milliseconds on a
//   good day, and the 400 ms timeout on a bad one. A pointer drag fires an
//   event per frame. Firing one seek per event queues sixty renders of moments
//   the finger has already left, so the picture arrives seconds after the
//   thumb and the last one to land is not the one you stopped on. `pumpRequest`
//   / `pumpSettle` hold at most ONE in flight and at most ONE pending, and the
//   pending slot is overwritten rather than appended — so the work is bounded
//   by the decoder rather than by the input rate, and the invariant that
//   matters is the one the sweep asserts: whatever time was requested LAST is
//   the time the pump is guaranteed to finish on. A dropped intermediate frame
//   is invisible; a dropped final one parks the canvas on the wrong moment.
//
// DECISION 4 — SEEK TARGETS ARE SNAPPED TO A FRAME, AND THE GRID IS THE
//   PICTURE'S, NOT THE POINTER'S. Two adjacent pixels on a 360 px bar under a
//   30 s take are 83 ms apart, but two adjacent pixels under a 5 s take are
//   14 ms — finer than a frame at any rate this app renders, so the second seek
//   is a decode that cannot change what is on screen. Quantising to
//   `SEEK_GRID_SEC` makes the request COMPARE EQUAL to the one in flight, which
//   is what lets the pump skip it entirely rather than merely order it.
//
// DECISION 4b — THE BAR IS A NATIVE `<input type="range">`, WHICH IS WHY THERE
//   IS NO POINTER MATH IN THIS FILE. A hand-rolled bar would need its own
//   pointer capture, its own clamp, its own keyboard handling and its own
//   accessible name, and it would still lose the thing that matters most here:
//   a range input keeps pointer capture through a drag that leaves the element,
//   which is the ordinary case for a thumb on a 44 px bar at the bottom of a
//   phone. The range owns "where did the finger land" and this file owns
//   everything the range cannot know. `PLAYHEAD_STEP_SEC` is its `step`, and it
//   is an exact multiple of `SEEK_GRID_SEC` so that an arrow-key press and a
//   drag land on the SAME grid — otherwise the two input methods produce seeks
//   that never compare equal and DECISION 3's economy is keyboard-only.
//
// DECISION 5 — THE FADE IS DRAWN FROM `fadeSpan`, NOT FROM THE REQUEST. The
//   chip says `2s` and a 3 s take gives you 1.5 s (fade.ts DECISION 2). The
//   ruler is the one place a user can SEE that clamp happen, so it must read
//   the same function the render does; a bar drawn from the requested number
//   would disagree with the file at exactly the take lengths where the clamp
//   bites.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

import { fadeSpan } from './fade';

/**
 * The finest seek this app can show — DECISION 4. One frame at the FASTEST
 * cadence it renders: `videoExport`'s profile is 30 fps, or 24 on a lean
 * device, so 1/30 is at least as fine as a frame of anything this app can
 * produce and a seek below it cannot change a file.
 */
export const SEEK_GRID_SEC = 1 / 30;

/**
 * The bar's `step` — DECISION 4b. One arrow-key press moves a tenth of a
 * second, which crosses a 5 s take in fifty presses rather than a hundred and
 * fifty, and 0.1 is EXACTLY 3/30 so every keyboard position is also a position
 * a drag can produce. The sweep asserts that multiple rather than trusting the
 * decimal.
 */
export const PLAYHEAD_STEP_SEC = 0.1;

/**
 * How close to the end of the ruler still counts as the end — see `lapAdjust`.
 * A nanosecond: far below anything the picture or the readout can express, and
 * far above the float error an accumulating clock carries into a boundary.
 */
export const LAP_EPSILON = 1e-9;

/**
 * The take length this device will actually record — the clamp that was spelled
 * `Math.min(seconds, profile.maxSeconds)` inline in five places in VideoStage,
 * including two that feed the user-facing label. One name, one rule.
 *
 * Returns 0 for anything non-finite or non-positive, and 0 is the documented
 * "there is no ruler": every function here treats it as "do nothing".
 */
export const takeLength = (requested: number, maxSeconds: number): number => {
  if (!Number.isFinite(requested) || !(requested > 0)) return 0;
  if (!Number.isFinite(maxSeconds) || !(maxSeconds > 0)) return 0;
  return Math.min(requested, maxSeconds);
};

/**
 * HOW MANY WHOLE TAKES HAVE ELAPSED, and where inside the current one we are —
 * DECISION 2.
 *
 * `laps` is what the caller adds to the clock's ORIGIN (times 1000, in ms);
 * `position` is `outTime` with those laps removed and is always in `[0, take)`
 * for a positive take. Both are returned because the caller needs to do exactly
 * one thing with each and deriving either from the other at the call site is
 * how the two drift apart.
 */
export const lapAdjust = (
  outTime: number, take: number,
): { laps: number; position: number } => {
  if (!Number.isFinite(outTime) || !(outTime > 0)) return { laps: 0, position: 0 };
  if (!Number.isFinite(take) || !(take > 0)) return { laps: 0, position: outTime };
  const whole = Math.floor(outTime / take);
  // Subtract the laps rather than take a modulo. `%` re-derives the remainder
  // from a division this has already done and the two disagree exactly at the
  // boundary the caller is about to test: measured over the take roster, 330,567
  // differing pairs with a worst delta of a WHOLE TAKE — at an accumulated
  // boundary `%` answers with the far end of the ruler where the subtraction
  // answers with the start.
  const position = Math.max(0, outTime - whole * take);
  // AND THE BOUNDARY IS APPROACHED FROM BELOW. A clock reaches a lap by
  // ACCUMULATING, so it arrives a float hair short of it — ten laps of a 4.3 s
  // take lands on 42.99999999999999, not 43. `floor` then reports NINE laps and
  // a position of 4.299999999999997, which is the far right of the bar at the
  // exact instant the playhead should be returning to the left, and one frame
  // later it jumps. The two ends of a ruler are the same point: anything within
  // a nanosecond of the end IS the start of the next lap, and saying so here is
  // what stops every caller from having to know it.
  if (take - position < LAP_EPSILON) return { laps: whole + 1, position: 0 };
  return { laps: whole, position };
};

/** Position -> fill fraction, clamped to the bar. */
export const fractionOf = (t: number, take: number): number => {
  if (!Number.isFinite(t) || !Number.isFinite(take) || !(take > 0)) return 0;
  if (!(t > 0)) return 0;
  return t >= take ? 1 : t / take;
};

/** Fill fraction -> position, clamped to the take. */
export const timeAtFraction = (f: number, take: number): number => {
  if (!Number.isFinite(f) || !Number.isFinite(take) || !(take > 0)) return 0;
  if (!(f > 0)) return 0;
  return f >= 1 ? take : f * take;
};

/**
 * Snap a seek target to the frame grid — DECISION 4. Also the clamp: nothing
 * downstream of this should ever have to ask whether a time is inside the take.
 */
export const snapSeek = (t: number, take: number, grid = SEEK_GRID_SEC): number => {
  if (!Number.isFinite(take) || !(take > 0)) return 0;
  if (!Number.isFinite(t) || !(t > 0)) return 0;
  if (t >= take) return take;
  if (!(grid > 0)) return t;
  const snapped = Math.round(t / grid) * grid;
  return snapped >= take ? take : snapped;
};

/**
 * The value a native range input just handed us, as a seek — DECISION 4b. It
 * arrives as a STRING and the browser has already clamped it to `[0, max]` on
 * its own step grid, but `max` is a float take length and the last step is
 * ragged, so it still has to be snapped and clamped here rather than trusted.
 */
export const seekFromInput = (raw: string | number, take: number): number =>
  snapSeek(typeof raw === 'number' ? raw : Number.parseFloat(raw), take);

/**
 * WHERE THE FADE SITS ON THE RULER — DECISION 5. Fractions, so the bar can draw
 * them with no knowledge of its own width, and `null` when there is no fade so
 * the caller renders nothing rather than two zero-width elements.
 */
export const fadeMarks = (
  take: number, requestedFade: number,
): { inEnd: number; outStart: number } | null => {
  const f = fadeSpan(requestedFade, take);
  if (!(f > 0)) return null;
  return { inEnd: fractionOf(f, take), outStart: fractionOf(take - f, take) };
};

/**
 * `m:ss.d` — the readout. Tenths, because the thing being located is a beat in
 * a ten-second take and hundredths on a phone is noise that changes width every
 * frame. Never negative, never `NaN` on the screen.
 */
export const formatPosition = (t: number): string => {
  const s = Number.isFinite(t) && t > 0 ? t : 0;
  const m = Math.floor(s / 60);
  const rest = s - m * 60;
  // Floor, not round: a readout that shows `0:10.0` while the playhead is still
  // inside a 10 s take says the take is over when it is not.
  const whole = Math.floor(rest);
  const tenth = Math.floor((rest - whole) * 10);
  return `${m}:${whole < 10 ? '0' : ''}${whole}.${tenth}`;
};

/** The whole ruler, as one string for the readout and the accessible name. */
export const formatSpan = (take: number): string =>
  formatPosition(Number.isFinite(take) && take > 0 ? take : 0);

/**
 * The clock origin that makes a running preview continue FROM `t` — the one
 * line that turns "park the canvas at 7 s" into "and play on from 7 s".
 *
 * The Stage's tick computes `outTime = (ts - moveOriginMs) / 1000`, so the
 * origin that yields `t` at wall-clock `nowMs` is this. Exported (rather than
 * inlined in the Stage) because it is the exact inverse of that one expression
 * and the sweep asserts the round trip.
 */
export const resumeOriginMs = (nowMs: number, t: number): number => {
  const now = Number.isFinite(nowMs) ? nowMs : 0;
  const at = Number.isFinite(t) && t > 0 ? t * 1000 : 0;
  const origin = now - at;
  // Every call site passes a `snapSeek` result and is therefore already inside
  // the take — but `t * 1000` still overflows for an absurd one, and an origin
  // of -Infinity does not merely misplace the clock, it pins it at Infinity for
  // the life of the scene with no frame able to bring it back. An
  // unrepresentable park is no park.
  return Number.isFinite(origin) ? origin : now;
};

// -----------------------------------------------------------------------------
// THE SEEK PUMP — DECISION 3.
//
// A pure two-slot state machine. `inFlight` is the time a render is currently
// running for; `pending` is the only one waiting. Requests overwrite `pending`;
// a settle promotes it. That is the whole thing, and the reason it is a value
// rather than a closure is so the invariants below can be swept without a
// browser, a timer or a decoder.
// -----------------------------------------------------------------------------

export interface PumpState {
  /** The seek a render is running for, or null when nothing is in flight. */
  readonly inFlight: number | null;
  /** The one waiting seek. Overwritten, never queued. */
  readonly pending: number | null;
}

export const PUMP_IDLE: PumpState = { inFlight: null, pending: null };

/**
 * Ask for `t`.
 *
 * Returns the next state and whether the CALLER must now start a render (true
 * only when the pump was idle). A request for the time already in flight with
 * nothing pending is dropped — DECISION 4's snap is what makes that comparison
 * fire often enough to matter.
 */
export const pumpRequest = (
  s: PumpState, t: number,
): { state: PumpState; start: boolean } => {
  if (!Number.isFinite(t)) return { state: s, start: false };
  if (s.inFlight === null) return { state: { inFlight: t, pending: null }, start: true };
  if (s.inFlight === t && s.pending === null) return { state: s, start: false };
  if (s.pending === t) return { state: s, start: false };
  return { state: { inFlight: s.inFlight, pending: t }, start: false };
};

/**
 * The in-flight render finished.
 *
 * Returns the next state and the time to render NEXT, or null when the pump has
 * caught up. The promotion is unconditional — a pending equal to the one that
 * just finished cannot exist, because `pumpRequest` refuses it.
 */
export const pumpSettle = (
  s: PumpState,
): { state: PumpState; next: number | null } => {
  if (s.pending === null) return { state: PUMP_IDLE, next: null };
  return { state: { inFlight: s.pending, pending: null }, next: s.pending };
};

/** Abandon everything in flight — pointer cancelled, component unmounted. */
export const pumpReset = (): PumpState => PUMP_IDLE;

/** Is a seek running or waiting? The bar shows its own handle from this. */
export const pumpBusy = (s: PumpState): boolean => s.inFlight !== null;
