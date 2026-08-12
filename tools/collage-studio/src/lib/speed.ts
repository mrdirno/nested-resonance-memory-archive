// =============================================================================
// THE SPEED — how fast ONE CLIP runs.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// THE RUNG, AND WHY THE LADDER KEPT IT SEPARATE FROM THE PACE.
//   "Speed — per-clip speed ramps / freeze frames (video-length sync is step 1).
//   NOT the same rung as THE PACE, and the distinction is worth keeping
//   straight: the pace is a property of the COMPOSITION's clock and moves the
//   drift and the cuts; this one is a property of a SOURCE and moves the
//   pictures inside a clip." Both are true at once and they compose — a clip at
//   half speed inside a collage that cuts twice as often — which is exactly why
//   they are two controls in two places and not one dial with a shared roster.
//
// IT ENTERS THROUGH THE ONE RATE THIS APP ALREADY HAS, AND THAT IS THE WHOLE
// IMPLEMENTATION.
//   `clipWindow.sourceTimeAt` is the single function where OUTPUT time becomes
//   SOURCE time, and it already takes a `rate` — "at rate r the clip advances r
//   seconds of content per second of output" — because video-length sync needed
//   one. A user speed is a factor in exactly that number. So the live `<video>`
//   (`el.playbackRate`), the offline picture seek (`renderAtTime` ->
//   `sourceTimeAt`) and the offline audio mix (`audioPlan.playbackRate` ->
//   `AudioBufferSourceNode`) all pick it up with NO new seam, no new argument
//   threaded through four render paths, and no fourth copy of the formula this
//   project has already been burned by three times.
//
// SO THE ONLY REAL DECISION IS HOW A SPEED COMPOSES WITH VIDEO-LENGTH SYNC,
// and the honest answer is the one people find surprising:
//
//   IN A SYNC MODE, A PER-CLIP SPEED MOVES THE REFERENCE — IT CANNOT MAKE ONE
//   CLIP RUN FASTER THAN ANOTHER.
//
//   `stretch-longest` and `speed-shortest` mean "every clip lands on ONE
//   on-screen length". That is a constraint on the result, so whatever a speed
//   does it cannot break it: with the reference `ref` chosen, every clip's rate
//   is `window / ref` and every clip's on-screen lap is `ref` by construction.
//   What a speed changes is which length `ref` IS — because the reference is
//   taken over the lengths the viewer would SEE at the speeds asked for
//   (`window / speed`), not over the raw files. Set one clip to 2x under
//   `speed-shortest` and the whole collage turns over twice as fast; set it
//   under `loop` (the default, where there is no reference) and that clip alone
//   runs at 2x. Both are the same rule, and the UI says which one is in force
//   rather than leaving the user to discover it.
//
// EVERY RATE IN THE ROSTER IS A POWER OF TWO, and here that is a guarantee
// rather than a legibility choice — the opposite of `lib/pace.ts`, which
// deliberately carries 0.75 and 1.5 and documents that reversibility is a
// property nothing needs. A pace multiplies a clock nobody divides back. A
// speed divides a WINDOW (`window / speed`, to decide the reference) and then
// multiplies a SOURCE TIME a decoder is asked to seek to, so the same quantity
// makes a round trip through both operations. {1/4, 1/2, 1, 2, 4} are exact in
// binary in both directions, so that trip is lossless at every roster entry and
// there is no rate at which the reference and the seek disagree in the last
// bits.
//
// WHAT IS NOT HERE, SAID PLAINLY.
//   - A FREEZE (speed 0) is not shipped. `sourceTimeAt` would hold at the IN
//     point for free (`t * 0` is 0), but `AudioBufferSourceNode.playbackRate`
//     of 0 is not a still frame, it is an undefined-to-stalled node, and a
//     picture that freezes while its sound keeps running is the preview/export
//     divergence this project files scars about. A freeze is its own rung.
//   - A RAMP (speed changing over the take) is not shipped either. This is one
//     scalar per clip; a ramp is a curve, and a curve needs the keyframe
//     machinery `lib/motion.ts` has for position and scale but not for time.
//   - A SPEED DOES NOT RIDE THE DICE OR THE COMPOSITION CODE, for the same
//     reason the trim and the music do not: a code is a RECIPE somebody else
//     opens with their own sources, and a speed is a fact about a FILE the code
//     cannot see. `lib/rollCode.ts` owns that boundary and it does not move.
// =============================================================================

/** One entry on the roster: what the chip says and what it multiplies. */
export interface SpeedChoice {
  /** Stable id — the test hook and the React key. Never shown. */
  id: string;
  /** The multiplier itself. */
  rate: number;
  /** The chip's face. */
  label: string;
  /** The chip's `title`, in the app's own voice. */
  title: string;
}

/**
 * THE ROSTER. Five, matching every other chip row in this app, and centred on
 * 1x so the default is visibly the middle rather than an end.
 */
export const SPEEDS: readonly SpeedChoice[] = [
  { id: 'quarter', rate: 0.25, label: '0.25×', title: 'Quarter speed — four times as long on screen' },
  { id: 'half', rate: 0.5, label: '0.5×', title: 'Half speed — twice as long on screen' },
  { id: 'natural', rate: 1, label: '1×', title: 'The clip as it was shot' },
  { id: 'double', rate: 2, label: '2×', title: 'Double speed — half as long on screen' },
  { id: 'quad', rate: 4, label: '4×', title: 'Four times speed — a quarter as long on screen' },
];

/** The speed a clip has when nobody has touched it. */
export const NATURAL_SPEED = 1;

export const SPEED_MIN = 0.25;
export const SPEED_MAX = 4;

const finite = (n: number | undefined | null): n is number =>
  typeof n === 'number' && Number.isFinite(n);

/**
 * Any input to a usable multiplier.
 *
 * ABSENT MEANS NATURAL, NEVER "KEEP WHAT IS THERE" — the same rule
 * `normaliseWindow` states, and this project has a scar with that exact name.
 * Out-of-roster values are CLAMPED rather than refused: the only way to hold one
 * is a restored session or a hand-edited state, and a clip stuck at a speed no
 * chip can express is worse than a clip at the nearest one that can.
 *
 * A FINITE OUT-OF-RANGE NUMBER IS CLAMPED; A NON-FINITE ONE IS NOT. `1e9`
 * becomes `SPEED_MAX` because somebody meant a large number, while `Infinity`
 * becomes 1 because that is a broken value rather than a big one. The asymmetry
 * looks like an oversight and is the opposite: it is `clipWindow.safeRate`'s
 * rule verbatim, and these two functions produce numbers that get multiplied
 * together, so they cannot disagree about what a non-number means.
 */
export const safeSpeed = (speed?: number | null): number => {
  if (!finite(speed) || speed <= 0) return NATURAL_SPEED;
  return speed < SPEED_MIN ? SPEED_MIN : speed > SPEED_MAX ? SPEED_MAX : speed;
};

/** True when this clip is not running as it was shot. The badge test. */
export const isSped = (speed?: number | null): boolean => safeSpeed(speed) !== NATURAL_SPEED;

/** The roster entry a value resolves to, or null when it sits between chips. */
export const speedChoice = (speed?: number | null): SpeedChoice | null => {
  const s = safeSpeed(speed);
  return SPEEDS.find((c) => c.rate === s) ?? null;
};

/**
 * `2x`, `0.5x`, `0.25x` — no trailing zeros, so the badge on a clip chip is as
 * short as it can be on the row that is tightest on a phone.
 */
export const speedLabel = (speed?: number | null): string => {
  const s = safeSpeed(speed);
  const n = Number.isInteger(s) ? String(s) : String(Number(s.toFixed(2)));
  return `${n}×`;
};

/**
 * How long `sourceSeconds` of a clip LASTS ON SCREEN at this speed.
 *
 * This is the quantity video-length sync must reason on — "match the shortest
 * clip" has to mean the shortest thing the viewer SEES, which is the same
 * argument `clipWindow.effectiveLength` makes for the trim window. Sync gets
 * both by being handed `window.length / speed`.
 */
export const screenLength = (sourceSeconds: number, speed?: number | null): number => {
  if (!finite(sourceSeconds) || sourceSeconds <= 0) return 0;
  return sourceSeconds / safeSpeed(speed);
};
