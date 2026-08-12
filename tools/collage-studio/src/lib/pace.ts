// =============================================================================
// THE PACE — how fast the collage's clock runs.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// WHAT WAS MISSING, AND THE LADDER FILED IT TWICE IN THE SAME WORDS.
//   Two rungs said it independently. "THE TURN'S HOLD IS A PROPERTY OF THE
//   MODE, so 'cut faster' is not askable" — `march` is 5 s, `ripple` is 3.5 s,
//   and the only way to change that was to pick a different mode, which also
//   changes the permutation. "A MOVE IS ONE ROSTER PICK FOR THE WHOLE COLLAGE,
//   and the speed is not a control" — `MOVE_CYCLE_SEC` is a constant, so there
//   was no way at all. Both rosters conflate the SHAPE of a rhythm with its
//   RATE. THE PACE is the second axis, and with it the shape roster finally
//   answers only the question it is good at: what KIND of motion, never how
//   fast.
//
// ONE DIAL OVER BOTH, BECAUSE A COLLAGE HAS ONE CLOCK.
//   The drift and the cut are two expressions of the same tempo, and somebody
//   who wants it faster does not want to answer two questions about it. Two
//   independent dials (a slow drift under fast cuts) is a real look and a real
//   generalisation; it is filed on the ladder rather than shipped here, because
//   the first cut of a rate control should make the existing rosters honest,
//   not double the roster count.
//
// SCALE THE CLOCK, NOT THE PERIODS — the decision this whole file turns on.
//   The obvious implementation divides each period by the rate: `hold / r`,
//   `MOVE_CYCLE_SEC / r`. It is wrong, and provably so, because `TURN_FADE_SEC`
//   is a CONSTANT that does not divide with them. `ripple` holds 3.5 s and
//   dissolves for 0.7 s of it — 20% of the time soft. Divide only the hold and
//   at 2x it holds 1.75 s with the same 0.7 s dissolve (40% soft), and at 4x it
//   holds 0.875 s (80% soft): the wall stops cutting and starts smearing, and
//   the roster's fastest mode degenerates first.
//   Scaling the TIME handed to the schedule leaves `fade / hold` INVARIANT by
//   construction — both are read off the same scaled clock — so a fast pace is
//   a faster CUT and never a permanent cross-fade. That is also why this
//   control needs no clamp and no per-mode exception: there is no rate at which
//   the schedule degenerates, only rates nobody would pick.
//
// REST AT ZERO SURVIVES, FOR FREE. `0 * r === 0` for every rate, so `turnAt`
//   and `sampleMove` still return `NO_TURN` / `NO_MOVE` BY REFERENCE at t=0 —
//   which is what keeps the still preview, the raster export and the SVG
//   bit-identical to a build without this file. The pace reaches exactly the
//   two surfaces that pass a time (the live Stage and the offline walk it
//   shares with the exporter) and cannot reach the three that do not.
//
// WHAT THE RATES ACTUALLY GUARANTEE, AFTER THE SWEEP CORRECTED ME.
//   The first draft of this comment claimed all five rates are dyadic
//   rationals and therefore exact and reversible in binary. Half true and the
//   wrong half: 1/2, 1, 2 are powers of two and exact both ways, but 3/4 and
//   3/2 carry a factor of THREE, and `0.1 * 0.75 / 0.75` comes back as
//   0.10000000000000002. The sweep (I3) found it before the roster shipped.
//   Reversibility turns out to be a property nothing needs — no caller ever
//   divides by the rate. What every caller DOES need is that the live preview
//   and the offline walk land on the same instant, and that holds for any rate
//   whatsoever, because both apply the SAME single multiplication to the same
//   `outTime`: one correctly-rounded operation, deterministic, no accumulation.
//   The rates are still kept simple and binary-friendly — but as a legibility
//   choice on the chips, not as a numerical guarantee this file relies on.
//
// IT IS NOT THE `Speed` RUNG. That one is per-CLIP speed ramps and freeze
//   frames — a property of a source. This is a property of the COMPOSITION's
//   clock, and the two compose: a clip may run at half speed inside a collage
//   that cuts twice as often.
// =============================================================================

/** The roster. Index order is the composition code's alphabet — APPEND ONLY.
 *  Reordering this array silently repoints every code ever minted. */
export type PaceId = 'even' | 'slow' | 'easy' | 'brisk' | 'rush';

/** Index 0 is the no-op and must stay index 0: an absent character in a legacy
 *  composition code decodes as 0, and `PACE_IDS[0]` is what it becomes. */
export const PACE_IDS: PaceId[] = ['even', 'slow', 'easy', 'brisk', 'rush'];

interface PaceDef {
  id: PaceId;
  label: string;
  title: string;
  /** Multiplier on the clock the move and the turn are read against. */
  rate: number;
}

const DEFS: Record<PaceId, PaceDef> = {
  even:  { id: 'even',  label: '1×',    rate: 1,    title: 'The tempo the roster was written at: a 12s drift, and each mode holds as long as it says.' },
  slow:  { id: 'slow',  label: '0.5×',  rate: 0.5,  title: 'Half speed. Everything on the clock takes twice as long.' },
  easy:  { id: 'easy',  label: '0.75×', rate: 0.75, title: 'A shade under. Slower than the roster without going languid.' },
  brisk: { id: 'brisk', label: '1.5×',  rate: 1.5,  title: 'Half again. The drift breathes and the cuts land sooner.' },
  rush:  { id: 'rush',  label: '2×',    rate: 2,    title: 'Double speed. Twice the cuts, twice the breath, same shapes.' },
};

/**
 * THE ROW THE CHIPS RENDER — SLOWEST TO FASTEST, which is deliberately NOT the
 * code alphabet.
 *
 * Every other roster in this app can be one list because its no-op belongs at
 * the left edge (`none`, `still`, `hold`). A rate's no-op belongs in the
 * MIDDLE, and the code alphabet cannot move it there: index 0 is what an absent
 * character decodes to, so `even` is pinned to the front of `PACE_IDS` forever.
 * Sorted from the same DEFS rather than hand-written, so the two orders cannot
 * drift apart.
 */
export const PACES: { id: PaceId; label: string; title: string }[] =
  [...PACE_IDS]
    .sort((a, b) => DEFS[a].rate - DEFS[b].rate)
    .map((id) => ({ id, label: DEFS[id].label, title: DEFS[id].title }));

const isPaceId = (id: unknown): id is PaceId =>
  typeof id === 'string' && Object.prototype.hasOwnProperty.call(DEFS, id);

/** The multiplier, and 1 for anything this build does not know. */
export const paceRate = (id: unknown): number => (isPaceId(id) ? DEFS[id].rate : 1);

/** Does this id change the clock at all? `even`, junk and undefined: no. */
export const isPaced = (id: unknown): boolean => isPaceId(id) && DEFS[id].rate !== 1;

/**
 * THE ONE SEAM: the take's clock, as the move and the turn should read it.
 *
 * Returns `timeSec` UNCHANGED — not multiplied by 1 — whenever the pace is
 * neutral or the clock is not a finite number. Multiplying by 1.0 happens to be
 * exact for every finite double, but "happens to be exact" is not the claim
 * worth making about a value four render paths compare for identity; an early
 * return makes a build with an unset pace structurally the build that never had
 * one, and that is what the sweep asserts with `Object.is`.
 *
 * Non-finite passes straight through for the same reason: `turnAt` and
 * `sampleMove` both already read a non-finite clock as rest, and sanitising it
 * here would be this module quietly changing a behaviour that is not its.
 */
export const paceTime = (id: unknown, timeSec: number): number => {
  const rate = paceRate(id);
  if (rate === 1 || !Number.isFinite(timeSec)) return timeSec;
  return timeSec * rate;
};
