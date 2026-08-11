// src/lib/fade.ts
// -----------------------------------------------------------------------------
// THE FADE — the take stops sounding like somebody pulled the cable out.
//
// WHY THIS FILE EXISTS
//   THE SOUNDTRACK put music under the collage and THE MOVE gave a photo collage
//   a time axis to put it under. What came out was a file that begins at full
//   level on sample zero and ENDS MID-BAR: `mixSources` renders exactly
//   `ceil(seconds * 48000)` samples and the encoder takes them, so the last
//   sample of a 5 s take is whatever the song happened to be doing at 5.000 s.
//   Every editor on earth answers this with a fade, and the Audio rung of the
//   capability ladder has named it as the first thing owed since the soundtrack
//   shipped.
//
// THE SHAPE
//   One envelope: silence at both ends, full level in the middle, LINEAR in
//   between. `fadeGainAt` is the only place that number is decided, and both
//   surfaces that can carry sound read it — the offline mix through
//   `applyFade` (per sample) and the realtime recorder through `fadeRamps` (as
//   WebAudio automation on the master gain). Same file, same numbers, and the
//   sweep asserts the two agree pointwise.
//
// DECISION 1 — LINEAR, AND THAT IS THE REASON THERE ARE TWO EMITTERS AT ALL.
//   An equal-power (cosine) fade is the nicer curve and it is unrepresentable
//   here: the realtime path schedules automation on an `AudioParam`, and the
//   only automation both engines implement identically for an arbitrary span is
//   `linearRampToValueAtTime`. A cosine would need `setValueCurveAtTime` with a
//   sampled table on one side and a closed form on the other — two shapes, two
//   roundings, and a fade that is measurably not the same fade depending on
//   which recorder your browser gave you. That is precisely the
//   preview-is-not-the-file divergence ONE LAYOUT and THE TITLE exist to
//   prevent, and this file refuses it the same way: pick the shape BOTH sides
//   can express exactly, then prove they express it identically.
//
// DECISION 2 — THE FADES CANNOT MEET AND CROSS. `fadeSpan` clamps the requested
//   length to `take / 2`, so at worst the two ramps meet exactly at the midpoint
//   and the envelope is a triangle that touches 1. Without the clamp a 2 s fade
//   on a 3 s take overlaps itself: `min(up, down)` would still be well defined,
//   but the middle of the take — the part the user is actually listening to —
//   would never reach full level, and it would get quieter the shorter the take
//   was. Clamping makes "a fade longer than the take" unrepresentable rather
//   than merely tested.
//
// DECISION 3 — THE MIDDLE IS NOT TOUCHED, BY CONSTRUCTION. `applyFade` walks
//   the two fade REGIONS and never the samples between them. A full-buffer loop
//   multiplying by the envelope would in fact be bit-identical in the middle
//   (`x * 1.0` is exact in IEEE-754, so this is not the `NO_MOVE` case, and
//   claiming it was would be borrowing an argument that does not apply); what
//   the region walk buys is that the bound becomes a VALUE the sweep can assert
//   rather than a property implied by the arithmetic — plus 2.88 M multiplies
//   not spent on a 30 s stereo take. The sweep asserts the two halves of that
//   seam separately, because either can be true while the pair is wrong: that
//   `fadeGainAt` really is 1 everywhere outside the regions, and that the
//   regions tile the buffer with no gap and no overlap.
//
// DECISION 4 — IT IS APPLIED AFTER THE TRUE-PEAK LIMITER, AND THE ORDER MATTERS
//   IN ONE DIRECTION ONLY. The limiter measures the peak of the whole mix and
//   scales by `CEILING / peak`; fading FIRST would let the ends decide that
//   scale, so switching a fade on would make the untouched middle of the take
//   LOUDER. Limiting first keeps the middle bit-identical to the same export
//   with the fade off, and the fade can never breach the ceiling it just
//   established, because the envelope is <= 1 everywhere. One order is safe in
//   both respects; the other is safe in neither.
//
// DECISION 5 — IT IS A PROPERTY OF THE TAKE, NOT OF THE COMPOSITION. The fade
//   lives beside the take LENGTH — same state, same bar, same lifetime — and
//   therefore does NOT ride the dice, the composition code or the project file,
//   exactly as the take length never has. A `?c=` code is a recipe somebody
//   else opens with their own pictures and their own music; "2 second fade" is
//   a fact about a render, and there is nothing in a picture recipe for it to
//   be about.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

/** The roster, in seconds. 0 is OFF and is the default: every export made
 *  before this existed must stay bit-identical, and the only way to promise
 *  that is for the untouched setting to be the one that does nothing. */
export const FADE_ROSTER: readonly number[] = [0, 0.5, 1, 2];

/** The chip's own text. `OFF` rather than `0s` — the row beside it is the take
 *  LENGTH in seconds, and two adjacent controls reading `5s` and `0s` invite
 *  exactly one misreading. */
export const fadeLabel = (sec: number): string =>
  !(sec > 0) ? 'OFF' : sec < 1 ? `${sec}s` : `${sec}s`;

/** The next roster entry, wrapping. One control, one tap, one job — the take
 *  bar is already eleven targets wide on a phone and a fifth chip group would
 *  be the exact scar the colour dice left in the trades' rails. */
export const nextFade = (sec: number): number => {
  const i = FADE_ROSTER.findIndex((v) => v === sec);
  return FADE_ROSTER[(i < 0 ? 0 : i + 1) % FADE_ROSTER.length];
};

/**
 * The EFFECTIVE fade length for this take — DECISION 2.
 *
 * Everything downstream takes this number rather than the user's request, so
 * "the fades overlap" is not a state the envelope, the ramps or the sample walk
 * can be handed.
 */
export const fadeSpan = (requested: number, take: number): number => {
  if (!Number.isFinite(requested) || !Number.isFinite(take)) return 0;
  if (!(requested > 0) || !(take > 0)) return 0;
  return Math.min(requested, take / 2);
};

/**
 * THE ENVELOPE. Output time -> gain, 0..1.
 *
 * `f` must already be a `fadeSpan` result. `min(up, down)` rather than a
 * three-branch piecewise: with `f <= take/2` the two ramps do not overlap, so
 * the two spellings agree — and the min form stays defined (and monotone into
 * the triangle) at exactly the boundary where the branchy one has to pick a
 * side.
 */
export const fadeGainAt = (t: number, take: number, f: number): number => {
  if (!(f > 0)) return 1;
  if (!(t > 0) || !(take > 0)) return 0;
  if (t >= take) return 0;
  const up = t < f ? t / f : 1;
  const rest = take - t;
  const down = rest < f ? rest / f : 1;
  return up < down ? up : down;
};

/** One automation point on the realtime path. */
export interface FadeRamp { when: number; value: number }

/**
 * The SAME envelope as a WebAudio automation schedule — DECISION 1.
 *
 * `setValueAtTime(pts[0])` then `linearRampToValueAtTime` for each point after
 * it. The middle point is omitted when the fade is exactly half the take,
 * because a ramp to the value it already holds over a zero-length span is a
 * degenerate event some engines drop and others honour, and neither is worth
 * finding out about at record time.
 */
export const fadeRamps = (take: number, f: number): readonly FadeRamp[] => {
  if (!(f > 0) || !(take > 0)) return [];
  const pts: FadeRamp[] = [{ when: 0, value: 0 }, { when: f, value: 1 }];
  if (take - f > f) pts.push({ when: take - f, value: 1 });
  pts.push({ when: take, value: 0 });
  return pts;
};

/**
 * Read the schedule back as a gain — the function the sweep uses to prove the
 * two emitters are one envelope. Exported because a claim that only a test can
 * evaluate is a claim nobody can check at the call site.
 */
export const rampGainAt = (ramps: readonly FadeRamp[], t: number): number => {
  if (!ramps.length) return 1;
  if (t <= ramps[0].when) return ramps[0].value;
  for (let i = 1; i < ramps.length; i++) {
    const a = ramps[i - 1], b = ramps[i];
    if (t <= b.when) {
      const span = b.when - a.when;
      if (!(span > 0)) return b.value;
      return a.value + ((b.value - a.value) * (t - a.when)) / span;
    }
  }
  return ramps[ramps.length - 1].value;
};

/**
 * The sample bounds of the two ramp regions — DECISION 3, as a value rather
 * than as a comment, so the sweep can assert the tiling directly.
 *
 * `[0, inEnd)` is the fade in, `[outStart, length)` is the fade out, and
 * `fadeGainAt` is exactly 1 on everything between them.
 */
export const fadeRegions = (
  length: number, sampleRate: number, take: number, f: number,
): { inEnd: number; outStart: number } => {
  if (!(f > 0) || !(take > 0) || !(sampleRate > 0) || !(length > 0)) {
    return { inEnd: 0, outStart: length };
  }
  const inEnd = Math.min(length, Math.ceil(f * sampleRate));
  const outStart = Math.max(inEnd, Math.min(length, Math.floor((take - f) * sampleRate)));
  return { inEnd, outStart };
};

/**
 * Apply the envelope to a rendered mix, in place.
 *
 * Takes the channel arrays rather than an `AudioBuffer` so it is testable in
 * node without a WebAudio implementation — the mixer holds the buffer and this
 * holds the shape, which is the same split `clipWindow` has with the mixer's
 * scheduling. Returns whether it changed anything, so the caller can report an
 * honest "did the file actually get a fade".
 */
export const applyFade = (
  channels: Float32Array[], sampleRate: number, take: number, f: number,
): boolean => {
  if (!(f > 0) || !(take > 0) || !(sampleRate > 0) || !channels.length) return false;
  let touched = false;
  for (const d of channels) {
    const { inEnd, outStart } = fadeRegions(d.length, sampleRate, take, f);
    for (let i = 0; i < inEnd; i++) d[i] *= fadeGainAt(i / sampleRate, take, f);
    for (let i = outStart; i < d.length; i++) d[i] *= fadeGainAt(i / sampleRate, take, f);
    if (inEnd > 0 || outStart < d.length) touched = true;
  }
  return touched;
};
