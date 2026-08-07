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
/**
 * The point in the window past which THIS CLIP HAS NO SOUND — the OUT point, or
 * the end of the decoded audio if that comes first.
 *
 * One line, and it is a function because two callers need it and the last time
 * this quantity was computed in one place and inferred in another it produced
 * the lap defect. `audioPlan` bounds the node with it; `audioSchedule` decides
 * whether the clip straddles with it. Same number, one definition.
 */
const audibleEnd = (w: ClipWindow, spanLimit?: number): number =>
  finite(spanLimit) && spanLimit > 0 ? Math.min(w.outSec, spanLimit) : w.outSec;

export const audioPlan = (
  p: WindowedPlayback,
  startAt: number,
  spanLimit?: number,
): AudioPlan => {
  const rate = safeRate(p.rate);
  const at = finite(startAt) && startAt > 0 ? startAt : 0;
  const lo = p.window.inSec;
  const hi = audibleEnd(p.window, spanLimit);
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

// -----------------------------------------------------------------------------
// THE LAP SCHEDULE — WHEN THE AUDIO TRACK IS SHORTER THAN THE TRIM WINDOW.
//
// `audioPlan` above clamps `loopEnd` into the decoded buffer, which is right —
// a loop region past the buffer is undefined behaviour. But a CLAMPED loop
// region is also a clamped PERIOD, and the period is the thing the picture and
// the sound have to share. `shortaudio.mp4` (6 s of picture, 3 s of sound)
// trimmed to 2->5: the picture laps every 3 s and the node laps every 1 s, so
// after the first second the two walk apart and never meet again. Measured by an
// adversarial audit through real Web Audio: 16 of 24 sampled instants played a
// 440 Hz tone under a picture the file has no sound for.
//
// It is NOT a clamp bug — the clamp is the only safe thing to hand the node.
// The mistake is asking ONE node to express a signal that is not periodic at its
// own loop length. So this case stops using the node's own loop and schedules
// one NON-looping node per PICTURE lap: the sound plays the part the file has,
// then there is nothing until the picture comes back round. Which is exactly
// what the live `<video>` already does — its audio track simply runs out while
// the picture keeps going — so the export now reproduces the preview instead of
// inventing a drone the preview never had.
// -----------------------------------------------------------------------------

/**
 * ONE `AudioBufferSourceNode.start(...)`, in the node's own vocabulary.
 *
 * `when` is CONTEXT seconds from the start of the mix (never negative — a lap
 * that began before the mix window is entered part-way through instead, by
 * advancing its `offset`). `offset` and `duration` are BUFFER seconds, which is
 * the coordinate both of those arguments are defined in and the reason a rate
 * never appears in them.
 */
export interface AudioStart {
  when: number;
  offset: number;
  /** Third argument to `start`. Null only for a natively-looping node. */
  duration: number | null;
  loop: boolean;
  loopStart: number;
  loopEnd: number;
  playbackRate: number;
}

/** Every node one clip needs, plus what the mixer has to tell the user. */
export interface AudioSchedule {
  starts: AudioStart[];
  /** The window is past the end of this clip's audio — wire nothing, and SAY so. */
  silent: boolean;
  /** True when the lap schedule was used, i.e. this clip straddles its audio end. */
  lapped: boolean;
  /** The take is longer than `MAX_AUDIO_LAPS` laps; the tail is silent. */
  truncated: boolean;
}

/**
 * A ceiling on nodes per clip, because a lap schedule is unbounded in principle.
 *
 * IT IS REACHABLE, and the first two versions of this comment got the reason
 * wrong in opposite directions — which is why the mechanism below is MEASURED
 * rather than argued.
 *
 * The original claim was "a lap is at least `MIN_WINDOW_SEC` of OUTPUT time
 * whatever the rate, because sync sets `rate = length / target` and so
 * `length / rate` IS the target". That is false, but NOT for the reason the
 * second version then asserted. The rate clamp (`videoSync`'s `RATE_MAX` = 16)
 * is not a cause at all: where it engages it LENGTHENS the lap — an unclamped
 * 16.667 against a 9 ms reference gives a 9.000 ms lap, the clamped 16 gives
 * 9.375 ms — so it strictly REDUCES the node count. Swept over 23,040 real
 * clip-cases (files 0.15–600 s × 3 sync modes × 5 trims), the rate clamped in
 * 2,940 of them and the shortest output lap across all of them was exactly
 * 0.150000 s, comfortably above the threshold.
 *
 * THE ACTUAL MECHANISM is `normaliseWindow`'s own floor clause: for a span at or
 * under `MIN_WINDOW_SEC` it hands back the WHOLE span, so a source FILE shorter
 * than 150 ms produces a sub-150 ms window, and that window becomes the sync
 * reference every other clip is timed against. `lapOut = max(len / RATE_MAX,
 * reference)`, so the cap binds only when some file is itself under the floor.
 * Cheapest real reproduction: ONE 62 ms clip whose audio track is shorter than
 * its video, in a 120 s take — 0.058 s laps, 2,048 entries, `truncated` true,
 * and the sound stops at 118.726 s.
 *
 * The take bound is sound and stays: `prepareOfflineAudio` refuses past
 * MAX_PCM_BYTES (~174.76 s), and `frameExport` clamps tighter still, which only
 * widens the margin.
 *
 * What matters is that the degradation is SILENCE past the cap, never the wrong
 * sound — a truncated schedule under-plays and cannot desync — and that it is no
 * longer unannounced: `truncated` reaches the user as a warning through
 * `mixSources`. A clip lapping every 58 ms is a strobe with a buzz on it long
 * before the cap is the reason it sounds wrong.
 */
export const MAX_AUDIO_LAPS = 2048;

const startFromPlan = (plan: AudioPlan): AudioStart => ({
  when: 0,
  offset: plan.offset,
  duration: plan.stopAfter,
  loop: plan.loop,
  loopStart: plan.loopStart,
  loopEnd: plan.loopEnd,
  playbackRate: plan.playbackRate,
});

/**
 * Every node this clip needs, for a mix of `seconds` starting at output time
 * `startAt`.
 *
 * THE SCOPE OF THE CHANGE IS THE BRANCH CONDITION, and that is on purpose. A
 * schedule differs from `audioPlan` if and ONLY IF the plan wanted to loop over
 * LESS than the picture window — which is precisely the defect and nothing else.
 * Every other input (untrimmed, trimmed with sound all the way to OUT,
 * non-looping, silent) returns the plan's own numbers in one entry, so those
 * exports are bit-identical to what shipped. Asserted, not asserted-in-a-comment:
 * invariant I16.
 */
export const audioSchedule = (
  p: WindowedPlayback,
  startAt: number,
  seconds: number,
  spanLimit?: number,
): AudioSchedule => {
  const plan = audioPlan(p, startAt, spanLimit);
  const one = (): AudioSchedule =>
    ({ starts: [startFromPlan(plan)], silent: false, lapped: false, truncated: false });

  if (plan.silent) return { starts: [], silent: true, lapped: false, truncated: false };

  const r = plan.playbackRate;
  const lo = p.window.inSec;
  const hiA = audibleEnd(p.window, spanLimit);
  const lenA = hiA - lo;                   // source seconds this clip actually has
  const L = p.window.length;               // source seconds the PICTURE laps over
  const lapOut = L / r;                    // output seconds per picture lap

  /**
   * THE STRADDLE IS DECIDED ON THE WINDOW, NOT ON WHETHER `audioPlan` CHOSE TO
   * LOOP — and reading it off the plan left a hole exactly one slider detent
   * wide. `audioPlan` refuses a loop region under 10 ms because a node's WRAP is
   * unstable below that across engines; short-circuiting on `!plan.loop` then
   * inherited that refusal into a path THAT NEVER WRAPS. A window overlapping
   * its audio by 9 ms took the single-node path and played one blip for the
   * whole take where the picture asks for one per lap (measured: 15 blips
   * collapsed to 1 on a 30 s take). The trim slider's step is 0.01 s, so it was
   * one detent from correct. The 10 ms floor still applies — to `L`, the period
   * actually being scheduled, where its reason holds.
   */
  const straddles = p.loop
    && lenA > 0
    && hiA < p.window.outSec
    && L > 0.01
    && lapOut > 0 && Number.isFinite(lapOut);
  if (!straddles) return one();

  const dur = finite(seconds) && seconds > 0 ? seconds : 0;
  const at = finite(startAt) && startAt > 0 ? startAt : 0;
  // Where the PICTURE sits inside its lap at the mix's first sample — the same
  // `% L` the frame loop walks, and the number `audioPlan` had to compute as
  // `% lenA` because that was the only period its single node could express.
  const raw = (at * r) % L;
  const ph = finite(raw) && raw >= 0 ? raw : 0;

  const starts: AudioStart[] = [];
  const push = (when: number, offset: number, duration: number) => {
    starts.push({ when, offset, duration, loop: false, loopStart: 0, loopEnd: 0, playbackRate: r });
  };

  // LAP ZERO is already in progress when the mix begins, so it is joined
  // part-way. Past `lenA` there is nothing left of it to join — the file's sound
  // for this lap has already run out — and the honest entry is no entry.
  if (ph < lenA) push(0, lo + ph, lenA - ph);

  // Every later lap, timed ABSOLUTELY off the first boundary rather than by
  // adding `lapOut` to the previous one, so a thousand laps cannot accumulate a
  // thousand roundings.
  const firstBoundary = (L - ph) / r;
  let truncated = false;
  for (let k = 0; ; k++) {
    const when = firstBoundary + k * lapOut;
    if (!(when < dur)) break;
    if (starts.length >= MAX_AUDIO_LAPS) { truncated = true; break; }
    push(when, lo, lenA);
  }

  return { starts, silent: false, lapped: true, truncated };
};

/**
 * A MODEL OF A WHOLE SCHEDULE — where the sound is at output time `u`, or `null`
 * for silence. `audioPositionAt` models one node; this models the set of them,
 * and the sweep asserts the two agree on every single-entry schedule so this is
 * an EXTENSION of that contract rather than a second copy of it.
 */
export const schedulePositionAt = (starts: AudioStart[], u: number): number | null => {
  const t = finite(u) && u > 0 ? u : 0;
  for (const s of starts) {
    if (t < s.when) continue;
    const local = (t - s.when) * safeRate(s.playbackRate);
    if (s.loop) {
      const len = s.loopEnd - s.loopStart;
      if (!(len > 0)) return s.offset;
      return s.loopStart + (((s.offset - s.loopStart) + local) % len);
    }
    if (s.duration !== null && local >= s.duration) continue;
    return s.offset + local;
  }
  return null;
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
