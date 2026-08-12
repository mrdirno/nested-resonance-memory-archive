/**
 * VIDEO-LENGTH SYNC — make the clips in a collage share a coherent length.
 *
 * Several videos of different durations, played together, drift into visual
 * noise. This decides each clip's <video>.playbackRate and loop so they line up.
 * Three modes, because that is all the distinct BEHAVIOUR there is (a "natural"
 * mode and a "loop to the longest" mode are identical once every clip loops):
 *
 *   - 'loop'            DEFAULT. Natural speed, every clip loops. The longest
 *                       clip sets the visible period; shorter clips simply repeat
 *                       within it. Nothing is sped up or slowed down.
 *   - 'stretch-longest' Every clip is slowed to the LONGEST clip's length
 *                       (rate = d / Lmax, ≤ 1), so they share one period, in phase.
 *   - 'speed-shortest'  Every clip is sped up to the SHORTEST clip's length
 *                       (rate = d / Lmin, ≥ 1), so the whole collage turns over
 *                       on the shortest clip's clock.
 *
 * Time-stretch via playbackRate shifts audio pitch; that is the accepted cost of
 * the two stretch modes and the reason 'loop' is the default.
 *
 * THE PER-CLIP SPEED ENTERS HERE, and nowhere else (see lib/speed.ts).
 *   A user speed and a sync rate are the same physical quantity — seconds of
 *   content per second of output — so letting the caller multiply them together
 *   afterwards would be a second place that decides a clip's rate, and the
 *   clamp below would then be applied to the wrong number. Instead the speed is
 *   an input to this function, and the rule it obeys is stated once:
 *
 *     the reference is taken over the lengths the viewer would SEE
 *     (`durationSec / speed`), and every clip's rate is then `durationSec / ref`.
 *
 *   So under a stretch mode a speed moves the TARGET everything lands on rather
 *   than making one clip outrun another — that is what "same length" means, and
 *   the invariant below is unchanged by the feature. Under 'loop' there is no
 *   reference and the rate IS the speed, which is the case a user has in mind.
 */
import { safeSpeed, screenLength } from './speed';

export type ClipLengthMode = 'loop' | 'stretch-longest' | 'speed-shortest';

export const CLIP_LENGTH_MODES: ClipLengthMode[] = ['loop', 'stretch-longest', 'speed-shortest'];

export interface ClipTiming {
  id: string;
  /** Natural duration in seconds. Non-finite / ≤0 is treated as "unknown" → rate 1. */
  durationSec: number;
  /**
   * The user's per-clip speed multiplier. Absent / invalid is 1 (`safeSpeed`),
   * so every call site that predates the control is unchanged by construction.
   */
  speed?: number;
}

export interface ClipPlayback {
  id: string;
  playbackRate: number;
  loop: boolean;
}

// HTMLMediaElement.playbackRate is spec-bounded; Chromium honours ~[0.0625, 16]
// and WebKit ~[0.05, 16]. Past that a clip freezes or the rate is silently
// dropped, so a pathological duration ratio is clamped rather than trusted.
export const RATE_MIN = 0.0625;
export const RATE_MAX = 16;

const clampRate = (r: number): number =>
  !Number.isFinite(r) || r <= 0 ? 1 : Math.min(RATE_MAX, Math.max(RATE_MIN, r));

const validDuration = (d: number): boolean => Number.isFinite(d) && d > 0;

/**
 * The reference length a given mode syncs to, or null for 'loop' / when no clip
 * has a known duration. Exposed so the UI can show "matching 8.4s" and the
 * export can size a loop.
 *
 * IT IS TAKEN OVER SCREEN LENGTHS, NOT OVER FILES. `screenLength` divides by the
 * clip's speed, so "the shortest clip" means the shortest thing the viewer sees
 * — the same correction `clipWindow.effectiveLength` made when the trim window
 * arrived, for the same reason: a clip the user has set to 4x is a quarter as
 * long on screen, and a reference that ignores that syncs to a length nothing
 * plays at.
 */
export const referenceLength = (clips: ClipTiming[], mode: ClipLengthMode): number | null => {
  const durs = clips
    .filter((c) => validDuration(c.durationSec))
    .map((c) => screenLength(c.durationSec, c.speed));
  if (durs.length === 0) return null;
  if (mode === 'stretch-longest') return Math.max(...durs);
  if (mode === 'speed-shortest') return Math.min(...durs);
  return null; // 'loop' has no single reference
};

/**
 * Per-clip playbackRate + loop for a mode. Pure and total: every input clip gets
 * exactly one output (same id), an unknown/zero duration always maps to the
 * clip's own speed, and a single clip under a stretch mode is not rescaled (it
 * is already its own reference, so `d / (d/s)` is exactly `s`).
 *
 * Invariant for the stretch modes, up to clamping: a clip's EFFECTIVE length
 * (durationSec / playbackRate) equals the reference for every clip with a known
 * duration — that is what "same length" means and is what the unit sweep checks.
 * It holds at every combination of speeds, because the speeds are inside the
 * reference and the rate is `durationSec / ref` regardless.
 *
 * THE IDENTITY CLAUSE, asserted rather than hoped for: with every speed absent
 * or 1, `screenLength` returns `durationSec` unchanged and every number in here
 * is the one that shipped before the control existed — bit-identical, not
 * merely close, since no arithmetic is performed on the default path at all.
 */
export const computeClipPlayback = (clips: ClipTiming[], mode: ClipLengthMode): ClipPlayback[] => {
  const ref = referenceLength(clips, mode); // Lmax, Lmin, or null
  return clips.map((c) => {
    // No reference (the 'loop' default) means nothing is being matched, so the
    // clip runs at exactly the speed it was asked to run at.
    let rate = safeSpeed(c.speed);
    if (ref && ref > 0 && validDuration(c.durationSec)) {
      rate = c.durationSec / ref;
    }
    return { id: c.id, playbackRate: clampRate(rate), loop: true };
  });
};
