// src/lib/clipWindow.ts
// -----------------------------------------------------------------------------
// TRIM — THE IN/OUT WINDOW, AND THE ONE PLACE OUTPUT TIME BECOMES SOURCE TIME.
//
// WHY THIS IS A MODULE AND NOT FOUR EXPRESSIONS
//   Three timelines have to agree on "what is this clip showing at output time
//   t", and until now they agreed by each carrying its own copy of the same two
//   lines:
//
//     - `Stage.seekClipTo`      target = loop ? (t*rate) % span : min(t*rate, span)
//     - `offlineAudio.mixSources`  loopStart/loopEnd/offset chosen to reproduce it
//     - the live <video>        playbackRate + native loop, reproducing it again
//
//   Three copies of one formula is exactly the shape this project keeps getting
//   burned by — the preview and the export derived independently, agreeing right
//   up until one of them changes. Adding a window to a formula that lives in
//   three places is adding it in three places. So the formula moved HERE, the
//   window went in ONCE, and the three consumers now ASK instead of remembering.
//
// THE COMPATIBILITY CLAUSE — asserted (I2), not hoped for.
//   An untrimmed clip is `inSec = 0, outSec = span`, and then
//   `sourceTimeAt` evaluates `0 + (loop ? (t*rate) % span : min(t*rate, span))`.
//   Adding exactly zero to a non-negative double is the identity in IEEE-754, so
//   every existing project, every clip nobody trims, and every frame of every
//   export renders BIT-IDENTICALLY to the code this replaced. Only a clip the
//   user actually trims moves.
//
// THE UNITS, because getting them backwards is silent and invisible in review.
//   `t` is OUTPUT time — seconds into the finished piece, which is what the
//   frame loop counts. The return is SOURCE time — seconds into the media file,
//   which is what `currentTime` and `AudioBufferSourceNode.offset` take. `rate`
//   converts between them (video-length sync sets it): at rate r the clip
//   advances r seconds of content per second of output.
// -----------------------------------------------------------------------------

/**
 * The shortest window we will hand to a decoder. Below this a looping window
 * seeks more often than it decodes, and `% len` starts resolving several laps
 * inside one frame — the picture stops being a clip and becomes a strobe.
 */
export const MIN_WINDOW_SEC = 0.15;

/** A resolved, always-valid window. Produced only by `normaliseWindow`. */
export interface ClipWindow {
  /** IN point, seconds into the source. Always `0 <= inSec < outSec`. */
  inSec: number;
  /** OUT point, seconds into the source. Always `<= span`. */
  outSec: number;
  /** `outSec - inSec`. Zero only when the span itself is unusable. */
  length: number;
  /** True when the window is the WHOLE clip — the untrimmed default path. */
  full: boolean;
}

/** A window plus how it is played. The complete argument to `sourceTimeAt`. */
export interface WindowedPlayback {
  window: ClipWindow;
  loop: boolean;
  /** Video-length-sync speed. `<= 0` or non-finite is read as 1. */
  rate: number;
}

/**
 * What an `AudioBufferSourceNode` must be set to so its sound sits at exactly
 * the source time the picture is showing. Every field maps 1:1 onto the node.
 */
export interface AudioPlan {
  loop: boolean;
  loopStart: number;
  loopEnd: number;
  playbackRate: number;
  /** The second argument to `node.start(0, offset)`. */
  offset: number;
  /**
   * THIS CLIP HAS NO SOUND INSIDE THE CHOSEN WINDOW — do not wire a node at all.
   *
   * Reachable whenever a container's audio track is SHORTER than its video track
   * (a mic that cut out, a short music bed, footage assembled by a tool that does
   * not pad audio) and the user trims to a window at or past where the audio
   * ends. Silence is the honest answer there; the alternative is worse than it
   * sounds, and was measured — see the note on `audioPlan`.
   */
  silent: boolean;
  /**
   * The third argument to `node.start(0, offset, duration)` — buffer-seconds to
   * play before stopping. Null when looping (the loop region bounds it instead).
   *
   * A non-looping `AudioBufferSourceNode` plays from `offset` to the END OF THE
   * BUFFER, not to the end of anything we asked for, so without this a trimmed
   * clip's sound runs straight through the material the user cut while the
   * picture is frozen at the OUT point.
   */
  stopAfter: number | null;
}

const finite = (n: number | undefined | null): n is number =>
  typeof n === 'number' && Number.isFinite(n);

const clamp = (n: number, lo: number, hi: number): number =>
  n < lo ? lo : n > hi ? hi : n;

/** `<= 0`, non-finite, or absent all mean "natural speed". */
export const safeRate = (rate: number | undefined): number =>
  finite(rate) && rate > 0 ? rate : 1;

/**
 * Resolve any pair of user numbers into a window that is safe to play.
 *
 * TOTAL BY CONSTRUCTION. Absent, NaN, Infinity, negative, inverted, identical,
 * out-of-range and sub-minimum all resolve — there is no input that returns a
 * window a consumer has to re-check, because a consumer that re-checks is a
 * fourth copy of this logic.
 *
 * `span` is the PLAYABLE span, i.e. `stage.ts`'s `max(EPS, duration - EPS)`,
 * not the raw duration: seeking to exactly `duration` is a no-op on some engines
 * and fires `ended` on others, and both paint a frame that was not asked for.
 * Clamping the OUT point to the span means that guard now covers trimming too,
 * for free, instead of being a rule the trim code had to remember.
 *
 * ABSENT MEANS THE DEFAULT, NEVER "KEEP WHAT IS THERE" — this project has a scar
 * with that exact name. An absent `inSec` is 0 and an absent `outSec` is `span`,
 * which together are the whole clip.
 */
export const normaliseWindow = (
  span: number,
  inSec?: number,
  outSec?: number,
): ClipWindow => {
  // Unknown or unusable duration: there is no window to speak of. Consumers
  // still get valid numbers, and `sourceTimeAt` degenerates to "the start".
  if (!finite(span) || span <= 0) {
    return { inSec: 0, outSec: 0, length: 0, full: true };
  }

  let lo = finite(inSec) ? clamp(inSec, 0, span) : 0;
  let hi = finite(outSec) ? clamp(outSec, 0, span) : span;

  // A clip shorter than the floor cannot be trimmed at all — it is already
  // less than one window. Hand back the whole thing rather than a window that
  // is longer than the media.
  if (span <= MIN_WINDOW_SEC) {
    return { inSec: 0, outSec: span, length: span, full: true };
  }

  // Inverted or too short: grow forward first (the user's IN point is the one
  // they chose most recently in the common drag), and only pull IN back when
  // there is no room left at the end.
  if (hi - lo < MIN_WINDOW_SEC) {
    hi = Math.min(span, lo + MIN_WINDOW_SEC);
    if (hi - lo < MIN_WINDOW_SEC) lo = Math.max(0, hi - MIN_WINDOW_SEC);
  }

  const length = hi - lo;
  // `full` is an EXACT test, deliberately. It is what makes the untrimmed path
  // bit-identical, so "nearly the whole clip" must not qualify: a window of
  // [0, span-1e-9] genuinely is a trim and takes the trimmed path.
  return { inSec: lo, outSec: hi, length, full: lo === 0 && hi === span };
};

/**
 * THE FORMULA. Output time -> source time, for one clip.
 *
 * Looping walks the window forever; non-looping runs to the OUT point and holds
 * there, which is what the video element does when it stops advancing.
 *
 * Bit-identical to the pre-trim expression whenever `inSec` is exactly 0 — see
 * the compatibility clause at the top of this file, and invariant I2.
 */
export const sourceTimeAt = (p: WindowedPlayback, t: number): number => {
  const { window: w } = p;
  const len = w.length;
  if (!(len > 0)) return w.inSec;
  const r = safeRate(p.rate);
  const u = finite(t) && t > 0 ? t * r : 0;
  return w.inSec + (p.loop ? u % len : Math.min(u, len));
};

/**
 * How long one turn of this clip lasts ON SCREEN — the window's length after
 * the sync rate is applied. This, not the file's duration, is what
 * `videoSync.computeClipPlayback` must reckon on once a clip can be trimmed:
 * "match the shortest clip" has to mean the shortest thing the viewer SEES, or
 * trimming a clip to two seconds leaves the whole collage still turning over on
 * its untrimmed sixty.
 */
export const effectiveLength = (p: WindowedPlayback): number => {
  const len = p.window.length;
  if (!(len > 0)) return 0;
  return len / safeRate(p.rate);
};

/**
 * The `AudioBufferSourceNode` settings that put the sound where the picture is.
 *
 * The node's own loop semantics do the work: with `loopStart`/`loopEnd` set to
 * the window, playback from `offset` walks the window and wraps inside it. All
 * this function has to get right is the START offset, and it gets it right by
 * construction — it is `sourceTimeAt` at the output's start time, which is the
 * same call the picture makes. That equality is invariant I7 and is asserted
 * against a model of the node rather than against a second copy of the algebra.
 *
 * `spanLimit` exists because a container's audio and video streams need not be
 * the same length: `loopEnd` past the decoded buffer's end is undefined
 * behaviour, so the caller passes the decoded buffer's real duration.
 *
 * IT CLAMPS. IT DOES NOT RE-NORMALISE, and that distinction is a MEASURED bug
 * rather than a style preference. `normaliseWindow`'s minimum-window repair
 * exists to rescue a window the USER typed, against the media's OWN span —
 * moving the IN point is the right rescue there. Applied against a DIFFERENT
 * stream's span it is catastrophic: a 6 s video whose audio track is only 3 s,
 * trimmed to 4→6, clamped BOTH ends to 2.99998, saw a zero-length window and
 * "repaired" it to [2.84998, 2.99998] — so the export looped the last 150 ms of
 * the audio ~33 times across a 5 s take, with the 440 Hz that is 95% of the
 * clip's sound measured at exactly zero. The picture was correct throughout.
 * Found by an adversarial audit driving the real app, not by any assertion here.
 *
 * So: the IN point never moves because a different stream is short. If the
 * window lands entirely past the end of the audio there is genuinely nothing to
 * play, and the plan says `silent` instead of inventing something to loop.
 */
export const audioPlan = (
  p: WindowedPlayback,
  startAt: number,
  spanLimit?: number,
): AudioPlan => {
  const rate = safeRate(p.rate);
  const at = finite(startAt) && startAt > 0 ? startAt : 0;
  const lo = p.window.inSec;
  const hi = finite(spanLimit) && spanLimit > 0
    ? Math.min(p.window.outSec, spanLimit)
    : p.window.outSec;
  const len = hi - lo;

  if (!(len > 0)) {
    return {
      loop: false, loopStart: 0, loopEnd: 0, playbackRate: rate,
      offset: lo, silent: true, stopAfter: null,
    };
  }

  const scoped: WindowedPlayback = {
    window: { inSec: lo, outSec: hi, length: len, full: p.window.full && hi === p.window.outSec },
    loop: p.loop,
    rate: p.rate,
  };
  const offset = sourceTimeAt(scoped, at);

  // The 0.01s floor is inherited, not invented: a `loopEnd - loopStart` below
  // it makes the node's wrap unstable across engines, and a clip that short is
  // better served by running out than by strobing.
  const looping = p.loop && len > 0.01;
  return {
    loop: looping,
    loopStart: looping ? lo : 0,
    loopEnd: looping ? hi : 0,
    playbackRate: rate,
    offset,
    silent: false,
    // A non-looping node otherwise plays to the end of the BUFFER — i.e. straight
    // through everything the user trimmed away, under a picture that has already
    // frozen at the OUT point.
    stopAfter: looping ? null : Math.max(0, hi - offset),
  };
};

/**
 * A MODEL OF `AudioBufferSourceNode`, so the two timelines can be ASSERTED
 * equal instead of assumed equal.
 *
 * This is the Web Audio contract written down: where the sound sits `u` seconds
 * after `start(0, offset)`. Nothing in the app calls it — the browser does this
 * — but the sweep does, and that is the point: the previous version of this
 * agreement lived in a comment, and a comment cannot go red.
 */
export const audioPositionAt = (plan: AudioPlan, u: number): number | null => {
  if (plan.silent) return null;
  const r = safeRate(plan.playbackRate);
  const elapsed = finite(u) && u > 0 ? u * r : 0;
  // `stopAfter` is buffer-seconds, so it is compared against the un-rated
  // elapsed buffer time — past it the node has stopped and there is no position.
  if (!plan.loop) {
    if (plan.stopAfter !== null && elapsed >= plan.stopAfter) return null;
    return plan.offset + elapsed;
  }
  const len = plan.loopEnd - plan.loopStart;
  if (!(len > 0)) return plan.offset;
  return plan.loopStart + (((plan.offset - plan.loopStart) + elapsed) % len);
};

/**
 * Where a LIVE `<video>` should jump back to, or `null` to leave it alone.
 *
 * The element has no in/out points, so a trimmed clip is enforced by watching
 * `currentTime` on the frames the compositor is already drawing. Two rules and
 * no third:
 *
 *   - past the OUT point (or before the IN point, which a native `loop` wrap
 *     produces) -> back to IN when looping, hold at OUT when not.
 *   - an untrimmed window never returns anything, so the default path keeps the
 *     element's own native loop and gains no seeks, no hitches and no watchdog.
 *
 * The tolerance is one frame at 24 fps. Tighter and an ordinary decode overshoot
 * re-seeks every frame; looser and a short window visibly runs past its end.
 */
export const LIVE_WINDOW_SLOP_SEC = 1 / 24;

export const liveWrapTarget = (
  p: WindowedPlayback,
  currentTime: number,
): number | null => {
  const w = p.window;
  if (w.full || !(w.length > 0) || !finite(currentTime)) return null;
  if (currentTime >= w.outSec) return p.loop ? w.inSec : null;
  // A wrap to 0 by the element's own `loop`, or a stale position from before
  // the user moved the IN point. Both land here.
  if (currentTime < w.inSec - LIVE_WINDOW_SLOP_SEC) return w.inSec;
  return null;
};
