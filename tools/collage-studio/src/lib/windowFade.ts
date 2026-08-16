// src/lib/windowFade.ts
// -----------------------------------------------------------------------------
// THE RANGE FADE — the cut you chose stops arriving as a click.
//
// WHY THIS FILE EXISTS
//   "Need to be able to add fade even when selecting clip range for audio", from
//   the field. THE FADE (`lib/fade.ts`) fades the SUMMED MIX at the take's two
//   ends and is structurally incapable of this: a 10 s chorus under a 30 s take
//   splices hard at 10 s and 20 s, and no control in the app could touch those
//   two instants. The book named the hole in the same cycle that shipped the
//   audio range — "no fade in/out at the range edges" — and the person who used
//   the range asked for it by name.
//
// WHAT IT IS
//   ONE envelope per SOURCE, in SOURCE time: silence at the window's IN point,
//   full level through the middle, silence again where the sound runs out. It is
//   therefore a fact about the WINDOW, so it repeats every lap — which is the
//   whole point, because the splice repeats every lap too.
//
// DECISION 1 — THE ENVELOPE IS `fade.ts`'s, NOT A NEW ONE. `windowFadeGainAt` is
//   `fadeGainAt` with the LAP as its "take". Same linear shape, same reason
//   (DECISION 1 there: it is the only curve a WebAudio `AudioParam` and a sample
//   walk can both express exactly), same `rampGainAt` reader, so the two emitters
//   below are asserted equal to one function rather than to each other. A second
//   curve here would have made the range fade and the take fade audibly different
//   kinds of fade in one export.
//
// DECISION 2 — THE CLAMP IS LENGTH/4, WHERE THE TAKE FADE'S IS LENGTH/2, and the
//   difference is not fussiness. `fadeSpan`'s half is safe for a take that plays
//   ONCE: the worst case is a triangle, once. A WINDOW LAPS, so the same clamp
//   makes a short loop a triangle wave — a 0.6 s window at 0.25 s would be ramping
//   83% of the time, which is not a fade, it is tremolo. A quarter guarantees at
//   least half of EVERY lap sits at full level, whatever the roster is asked for.
//
// DECISION 3 — THE ROSTER'S SHORT END IS 0.1 s, AND THAT ENTRY IS THE FEATURE.
//   The judge panel split exactly here. A splice click is a sub-10 ms waveform
//   discontinuity; a "fade the range" gesture is 0.5–2 s. Offering only the long
//   end cures a click by cutting a hole in the music at every wrap — three
//   audible dips under a 30 s take, which reads as a broken file where a click
//   reads as an edit. 0.1 s kills the discontinuity and is inaudible as a dip even
//   on a 1 s loop; 0.5 and 1 s are the edit gesture, for the ordinary case where
//   the range outlasts the take and never laps at all. One control, one rule
//   (short to smooth a join, long to shape a range), no conditional semantics.
//
// DECISION 4 — THE OUT EDGE IS `audibleEnd`, NEVER `outSec`. When a container's
//   audio track is shorter than its video the sound stops BEFORE the OUT point,
//   and a ramp scheduled at OUT simply never runs — the chip would do nothing on
//   exactly the clips whose splice is harshest. `clipWindow.ts` already made that
//   quantity a named function for this class of mistake; this file asks it rather
//   than re-deriving it, and the lap boundaries come from `lapEdges` for the same
//   reason.
//
// DECISION 5 — IT IS PRE-LIMITER, AND `fade.ts` DECISION 4 DOES NOT EXTEND HERE.
//   The take fade runs AFTER the true-peak limiter precisely so switching it on
//   cannot change the level of the untouched middle. A per-source envelope cannot:
//   it is inside the mix graph by construction, so it is part of the buffer the
//   peak is measured over, and on a mix that was over the ceiling, turning a range
//   fade on can make the whole export slightly LOUDER. That is not a defect to
//   hide — it is exactly what THE LEVEL already does, for the same reason, and it
//   is stated here rather than inherited silently from a neighbouring decision.
//
// DECISION 6 — IT DOES NOT RIDE THE DICE OR THE COMPOSITION CODE. Same sentence
//   the trim, the speed, the level and the music itself all carry: a `?c=` code is
//   a recipe somebody else opens with their own sources, and a range fade is a
//   fact about a FILE the code cannot see. It is the fifth per-source fact that
//   does not survive a project file either, which is the ladder's own trigger for
//   one `SourceState` rather than a fifth field — a format change that deserves
//   its own cycle.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

import { fadeGainAt, type FadeRamp } from './fade';
import {
  audibleEnd, lapEdges, safeRate, MAX_AUDIO_LAPS,
  type ClipWindow, type WindowedPlayback,
} from './clipWindow';

/** The roster, in SOURCE seconds. 0 is OFF and is the default: every export made
 *  before this existed must stay bit-identical, and the only way to promise that
 *  is for the untouched setting to be the one that does nothing. */
export const WINDOW_FADE_ROSTER: readonly number[] = [0, 0.1, 0.5, 1];

/** The button's own text. `OFF` rather than `0s`, for `fade.ts`'s reason: the
 *  numbers beside it are seconds of MEDIA and two controls reading `0s` invite
 *  exactly one misreading. */
export const windowFadeLabel = (sec: number): string => (!(sec > 0) ? 'OFF' : `${sec}s`);

/**
 * Any number a caller can hand in, as a fade length. Absent, NaN, Infinity and
 * negative all mean OFF — the same "absent is the default, never keep what is
 * there" rule the window itself follows, and the reason the Stage can take this
 * straight off a prop without a second guard.
 *
 * IT DOES NOT CLAMP TO THE ROSTER. `windowFadeSpan` clamps against the material,
 * which is the bound that matters; a roster is what the UI offers, not what the
 * exported API is allowed to be handed.
 */
export const safeFade = (sec: number | null | undefined): number =>
  typeof sec === 'number' && Number.isFinite(sec) && sec > 0 ? sec : 0;

/**
 * The EFFECTIVE fade for this window — DECISION 2.
 *
 * `length` is the AUDIBLE length of the lap (`audibleLength` below), not the
 * window's, so a clip whose sound runs out early is clamped against the sound it
 * actually has.
 */
export const windowFadeSpan = (requested: number, length: number): number => {
  if (!Number.isFinite(requested) || !Number.isFinite(length)) return 0;
  if (!(requested > 0) || !(length > 0)) return 0;
  return Math.min(requested, length / 4);
};

/** SOURCE seconds this source actually sounds for inside its window — DECISION 4. */
export const audibleLength = (w: ClipWindow, spanLimit?: number): number => {
  const hi = audibleEnd(w, spanLimit);
  const len = hi - w.inSec;
  return Number.isFinite(len) && len > 0 ? len : 0;
};

/**
 * THE ENVELOPE. SOURCE position -> gain, 0..1.
 *
 * `pos` is seconds into the FILE (what `currentTime` reads and what
 * `schedulePositionAt` models), so the caller never has to hold a second idea of
 * where the sound is. Outside the audible part of the window the answer is 0,
 * which is also what the node is doing there.
 */
export const windowFadeGainAt = (
  pos: number, inSec: number, length: number, f: number,
): number => {
  if (!(f > 0)) return 1;
  if (!Number.isFinite(pos) || !(length > 0)) return 0;
  return fadeGainAt(pos - inSec, length, f);
};

/** EPS for "these two automation points are the same instant". A ramp to a value
 *  over a zero-length span is the degenerate event `fade.ts` refuses to schedule,
 *  so coincident points collapse into one instead of being emitted as a pair. */
const SAME_INSTANT = 1e-6;

const pusher = (out: FadeRamp[]) => (when: number, value: number): void => {
  if (!Number.isFinite(when) || !Number.isFinite(value)) return;
  const w = when > 0 ? when : 0;
  const last = out.length ? out[out.length - 1] : null;
  if (last && w <= last.when + SAME_INSTANT) { last.value = value; return; }
  out.push({ when: w, value });
};

/**
 * THE OFFLINE EMITTER — the whole take's envelope, in OUTPUT time, ready to be
 * scheduled on a gain node the mixer puts in series with the source's level.
 *
 * It walks the SAME lap boundaries `audioSchedule` walks, out of the same
 * `lapEdges`, so the ramp and the splice cannot land at different instants. Lap
 * zero is joined PART-WAY (the mix can start anywhere in the source's lap), which
 * is why the first point is the envelope's value at the phase rather than 0.
 *
 * The cap is `MAX_AUDIO_LAPS`, deliberately the same number the schedule itself
 * stops at: past it the sound is silent anyway, so the fade can never be the
 * reason an export changes and there is no second cap for a user to discover.
 */
export const mixWindowRamps = (
  p: WindowedPlayback,
  startAt: number,
  seconds: number,
  spanLimit: number | undefined,
  requested: number,
): FadeRamp[] => {
  const lenA = audibleLength(p.window, spanLimit);
  const f = windowFadeSpan(requested, lenA);
  if (!(f > 0)) return [];
  const dur = Number.isFinite(seconds) && seconds > 0 ? seconds : 0;
  if (!(dur > 0)) return [];

  const r = safeRate(p.rate);
  const edges = lapEdges(p, startAt);
  const ph = edges.phase;
  const out: FadeRamp[] = [];
  const push = pusher(out);

  // LAP ZERO, joined at `ph`. Everything after it is a whole lap and takes the
  // same four points; this one takes whichever of them are still ahead.
  push(0, windowFadeGainAt(p.window.inSec + ph, p.window.inSec, lenA, f));
  if (ph < f) push((f - ph) / r, 1);
  if (ph < lenA - f) push((lenA - f - ph) / r, 1);
  if (ph < lenA) push((lenA - ph) / r, 0);

  if (!edges.loops) return out;

  // EVERY LATER LAP, timed ABSOLUTELY off the first boundary rather than by
  // adding the period to the previous one, so a thousand laps cannot accumulate
  // a thousand roundings — `audioSchedule`'s own rule, for its own reason.
  for (let k = 0; k < MAX_AUDIO_LAPS; k++) {
    const base = edges.first + k * edges.period;
    if (!(base < dur)) break;
    push(base, 0);
    push(base + f / r, 1);
    push(base + (lenA - f) / r, 1);
    push(base + lenA / r, 0);
  }
  return out;
};

/**
 * THE LIVE EMITTER — the REST of the lap the element is in right now, relative to
 * the instant this is called.
 *
 * The monitor cannot use the schedule above: it has no mix clock, the frame loop
 * is demand-driven (a still collage with a soundtrack draws nothing at all), and
 * a background tab throttles rAF to zero — so an envelope written per frame would
 * park mid-ramp and stay there. This returns AUTOMATION instead, armed from the
 * element's own position and re-armed at each wrap, which is the same thing
 * `applyTakeFade` does to the master gain and for the same reason.
 *
 * `pos` is the element's `currentTime`. The remaining points are whichever of the
 * lap's three still lie ahead of it.
 */
export const liveWindowRamps = (
  pos: number, inSec: number, length: number, f: number, rate: number,
): FadeRamp[] => {
  if (!(f > 0) || !(length > 0)) return [];
  if (!Number.isFinite(pos)) return [];
  const r = safeRate(rate);
  const raw = pos - inSec;
  const u = raw < 0 ? 0 : raw > length ? length : raw;
  const out: FadeRamp[] = [];
  const push = pusher(out);
  push(0, windowFadeGainAt(inSec + u, inSec, length, f));
  if (u < f) push((f - u) / r, 1);
  if (u < length - f) push((length - f - u) / r, 1);
  if (u < length) push((length - u) / r, 0);
  return out;
};
