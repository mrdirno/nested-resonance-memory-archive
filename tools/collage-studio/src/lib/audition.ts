// src/lib/audition.ts
// -----------------------------------------------------------------------------
// CUT AUDITION — HEARING THE TRIM HANDLE YOU ARE HOLDING.
//
// From the well, verbatim intent: "you know where your sound starts and stops…
// how pro daws do it is it just cycles the playback as you drive the slider —
// if you're at the front you play on the cut, if you're dragging the back you
// play a few seconds before up to the cut, then loop again to dial things in
// quickly."
//
// That is TWO windows, one per handle, and both are SUB-WINDOWS of the trim:
//
//   IN  handle → [in, in + tail]   — the cut is the ONSET. You hear what the
//                                    range will open with, from its first sample.
//   OUT handle → [out - tail, out] — the cut is the LANDING. You hear the
//                                    approach, and the loop ends exactly where
//                                    the range will.
//
// WHY THIS IS A MODULE AND NOT TWO EXPRESSIONS IN A COMPONENT: the loop is
// enforced by `clipWindow.liveWrapTarget` — the SAME decision the live monitor
// and the offline mix already share for the trim window itself — so the audition
// has no wrap arithmetic of its own to drift. All this file owns is which
// sub-window an edge means, and the two policy constants. The Stage holds the
// element (one element, its own — a second element on the same blob is a second
// decoder and an out-of-phase double of the exact source being judged).
//
// THE FADE IS DELIBERATELY NOT IN HERE. The range fade's envelope is armed on
// the REAL window (`stage.armTrackFade`), so an OUT audition hears the true
// configured landing — fade and all — while the artificial edge (out - tail)
// wraps hard, which is what a DAW's loop audition does too.
// -----------------------------------------------------------------------------

import { type ClipWindow, liveWrapTarget } from './clipWindow';

export type AuditionEdge = 'in' | 'out';

/**
 * How much of the range plays around the cut before the loop comes round.
 *
 * 2.5 s is one full bar at 96 BPM, and at least one bar everywhere at or above
 * it — which covers the band nearly all field footage and music beds sit in —
 * while keeping the wheel's cycle (the wait to re-hear the cut you just moved)
 * under the ~3 s where dialing stops feeling live. "A few seconds", as wished,
 * leaning short because the loop is the tool, not the listen.
 */
export const AUDITION_TAIL_SEC = 2.5;

/**
 * Floor between explicit reseeks while the IN handle is driven. An IN move is
 * the one motion that must RESTART playback (the onset is the information); a
 * gap under real seek latency on blob media just stacks seeks into stutter,
 * and one over ~250 ms makes the wheel feel dead. The OUT handle never
 * reseeks — the wrap watchdog is already running toward it.
 */
export const AUDITION_RESEEK_GAP_MS = 150;

const finite = (n: unknown): n is number =>
  typeof n === 'number' && Number.isFinite(n);

/**
 * The sub-window one edge auditions. TOTAL: any object shaped like a window
 * resolves to a playable, contained window — hostile fields clamp rather than
 * escape into a seek target.
 *
 * `full` is ALWAYS false, and that is load-bearing rather than cosmetic:
 * `liveWrapTarget` short-circuits a full window to "leave the element alone",
 * and an untrimmed track auditioned at its IN point is exactly a full window
 * whose audition must still loop. Which makes this file a SECOND producer of
 * `ClipWindow` — so be explicit about the dialect: here `full` is a steering
 * signal for the wrap decision, never the whole-clip FACT `normaliseWindow`
 * documents, and nothing downstream but `liveWrapTarget` may read this window.
 *
 * On a range shorter than twice the tail the two edges' windows OVERLAP, and on
 * one shorter than the tail they are BOTH the whole range. That is correct, not
 * degenerate: the audition of a 1 s range is that 1 s, whichever handle you hold.
 */
export const auditionWindow = (edge: AuditionEdge, w: ClipWindow): ClipWindow => {
  const lo = finite(w?.inSec) && w.inSec > 0 ? w.inSec : 0;
  const hiRaw = finite(w?.outSec) ? w.outSec : lo;
  const hi = hiRaw > lo ? hiRaw : lo;
  const from = edge === 'in' ? lo : Math.max(lo, hi - AUDITION_TAIL_SEC);
  const to = edge === 'in' ? Math.min(hi, lo + AUDITION_TAIL_SEC) : hi;
  return { inSec: from, outSec: to, length: to - from, full: false };
};

/**
 * Where the audition playhead should jump, or null to leave it playing.
 * Definitionally `liveWrapTarget` over `auditionWindow` — kept as ONE exported
 * call so the sweep pins the composition and any future "improvement" that
 * grows wrap logic of its own goes red instead of drifting.
 */
export const auditionWrap = (
  edge: AuditionEdge,
  w: ClipWindow,
  currentTime: number,
): number | null =>
  liveWrapTarget(
    { window: auditionWindow(edge, w), loop: true, rate: 1 },
    currentTime,
  );
