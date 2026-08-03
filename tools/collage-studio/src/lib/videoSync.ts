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
 */
export type ClipLengthMode = 'loop' | 'stretch-longest' | 'speed-shortest';

export const CLIP_LENGTH_MODES: ClipLengthMode[] = ['loop', 'stretch-longest', 'speed-shortest'];

export interface ClipTiming {
  id: string;
  /** Natural duration in seconds. Non-finite / ≤0 is treated as "unknown" → rate 1. */
  durationSec: number;
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
 */
export const referenceLength = (clips: ClipTiming[], mode: ClipLengthMode): number | null => {
  const durs = clips.map((c) => c.durationSec).filter(validDuration);
  if (durs.length === 0) return null;
  if (mode === 'stretch-longest') return Math.max(...durs);
  if (mode === 'speed-shortest') return Math.min(...durs);
  return null; // 'loop' has no single reference
};

/**
 * Per-clip playbackRate + loop for a mode. Pure and total: every input clip gets
 * exactly one output (same id), an unknown/zero duration always maps to rate 1,
 * and a single clip is never rescaled (it is already its own reference).
 *
 * Invariant for the stretch modes, up to clamping: a clip's EFFECTIVE length
 * (durationSec / playbackRate) equals the reference for every clip with a known
 * duration — that is what "same length" means and is what the unit sweep checks.
 */
export const computeClipPlayback = (clips: ClipTiming[], mode: ClipLengthMode): ClipPlayback[] => {
  const ref = referenceLength(clips, mode); // Lmax, Lmin, or null
  return clips.map((c) => {
    let rate = 1;
    if (ref && ref > 0 && validDuration(c.durationSec)) {
      rate = c.durationSec / ref;
    }
    return { id: c.id, playbackRate: clampRate(rate), loop: true };
  });
};
