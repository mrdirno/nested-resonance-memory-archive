// src/lib/takeMap.ts
// -----------------------------------------------------------------------------
// THE STRIP — what is IN the take, drawn on the ruler that already measures it.
//
// WHY THIS FILE EXISTS
//   THE PLAYHEAD gave the take a clock you can see and drag, and the ladder
//   filed the gap it left in the same breath: "THE RULER SHOWS THE TAKE AND NOT
//   WHAT IS IN IT. The bar knows the take's length and the fade's shape and
//   nothing else." Everything else that happens inside those ten seconds is
//   invisible until a file comes out — WHERE THE COLLAGE CUTS (THE TURN, scaled
//   by THE PACE, snapped by THE BEAT) and WHERE EACH SOURCE REPEATS (the trim
//   window, the sync rate, THE SPEED). Four cycles of time-domain work, none of
//   it observable.
//
//   The cost is not only "you cannot see it". It is that two of those features
//   are RELATIONSHIPS — a beat sync is a claim that the cuts land on the music,
//   a trim is a claim about which three seconds repeat — and a relationship you
//   cannot see is a relationship you cannot check. This file is the arithmetic
//   of a picture of them: fractions of the take, so the bar can draw it with no
//   knowledge of its own width, exactly as `fadeMarks` already does.
//
// DECISION 1 — THE MAP IS DERIVED FROM THE COMPOSITOR'S OWN SCHEDULE, NOT FROM
//   A SECOND BELIEF ABOUT IT. Two things decide when the wall cuts: `turnAt`'s
//   roster branch (turn k at scaled time `k * hold`, the clock scaled by
//   `paceTime`) and its scheduled branch (turn k at `first + (k-1) * hold`, in
//   raw output time, because a beat grid sits at absolute instants the music
//   decides and is deliberately NOT paced). A ruler that re-derived either one
//   would be a fourth partition of the same problem ONE LAYOUT exists to
//   refuse, and it would diverge silently — a mark 40 ms from the cut looks
//   right and is a lie about the one relationship the user is checking.
//
//   So `cutPlan` collapses both branches into ONE output-time `TurnSchedule`,
//   and the sweep asserts that every mark it produces is a turn boundary
//   ACCORDING TO `turnAt` ITSELF — the compositor's function, imported and
//   interrogated, rather than a restatement of its algebra. When the roster
//   path is scaled, the fade scales with it (`TURN_FADE_SEC / rate`): the pace
//   scales the CLOCK, so a dissolve is the same FRACTION of the hold at every
//   tempo, which is `lib/pace.ts`'s own invariant read from the other side.
//
// DECISION 2 — A LANE IS A LAP COUNT, NOT A CLIP'S POSITION. A conventional NLE
//   lane says "this clip runs from 4 s to 9 s". A collage has no such thing:
//   every source is on screen for the WHOLE take, laid out in space rather than
//   in sequence, and what actually varies is HOW OFTEN each one comes back
//   round. So a lane draws the seams — the instants a source restarts — and the
//   last pass is drawn short when the take ends mid-lap, which is the fact the
//   ladder asked for in these words: "so you can see that the 3s clip laps
//   three times inside a 10s take and that the trimmed one covers only its
//   window."
//
//   The period is `clipWindow.effectiveLength`, the function the sync rung
//   already made the one answer to "how long is this clip ON SCREEN" — window
//   length over rate, with THE SPEED already folded into that rate by
//   `computeClipPlayback`. Recomputing it here from a duration and a trim would
//   be the second place that decides a clip's period, which is the exact defect
//   `videoSync`'s own header refuses.
//
// DECISION 3 — NO SILENT CAPS. A 0.2 s window inside a 30 s take laps 150
//   times; drawn as 150 seams on a 360 px bar that is a solid smear that LOOKS
//   like a clip which never repeats — the drawing would state the opposite of
//   the truth. Past `MAX_LANE_SEGMENTS` the lane goes `dense`: one unbroken bar
//   plus the exact `laps` count for the label, which says "too fast to draw"
//   instead of pretending. Cuts past `MAX_STRIP_CUTS` are counted in `hidden`
//   for the same reason. Every cap in here reports what it dropped.
//
// DECISION 4 — A SOURCE WITH NO KNOWN LENGTH GETS NO LANE, AND IS COUNTED. A
//   clip whose duration never probed has `window.length === 0`, and the only
//   honest lane for it is none: a full-width bar would claim it plays once
//   through, an empty one would claim it is silent. `unknownLanes` is separate
//   from `hiddenLanes` because they are different facts — "there was no room to
//   draw it" and "there was nothing to draw" — and one counter for both is how
//   a diagnostic becomes decoration.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

import { effectiveLength, type WindowedPlayback } from './clipWindow';
import { paceRate } from './pace';
import { fractionOf } from './playhead';
import { MAX_TURN_INDEX, TURN_FADE_SEC, isTurning, turnHoldSec, type TurnSchedule } from './turn';

/**
 * How close to a boundary still counts as landing on it. Same order as
 * `playhead.LAP_EPSILON` and for the same reason: a lap length that divides the
 * take exactly arrives a float hair over or under, and `ceil` turns a hair into
 * a whole extra pass drawn one pixel wide at the very end of the bar.
 */
export const MAP_EPSILON = 1e-9;

/** Cuts drawn before the strip stops drawing them — DECISION 3. */
export const MAX_STRIP_CUTS = 256;

/** Seams drawn before a lane goes solid — DECISION 3. */
export const MAX_LANE_SEGMENTS = 48;

/** Lanes drawn before the rest are counted instead — DECISION 3. */
export const MAX_LANES = 8;

/**
 * THE CUT SCHEDULE, IN THE TAKE'S OWN SECONDS — DECISION 1.
 *
 * Returns the same `{hold, first, fade}` shape `turn.ts` already speaks, with
 * both of its branches resolved into output time:
 *
 *   synced   — the grid `lib/beat.ts` produced, used verbatim. It is already in
 *              output time and is deliberately not paced (`stage.ts`: "1.5x on
 *              a beat grid is not a faster cut, it is a cut that lands between
 *              the drums").
 *   roster   — the mode's hold divided by the pace rate, because `paceTime`
 *              scales the CLOCK the schedule is read against: a boundary at
 *              scaled `k * hold` is at real `k * hold / rate`. The first cut is
 *              one hold in, which is where `turnAt` puts turn 1.
 *
 * Null means the wall never re-cuts, and `hold`/junk/a malformed grid all mean
 * the same thing here that they mean to `turnAt`: rest. The validity test on a
 * handed-in schedule is `scheduledTurnAt`'s, character for character, so the
 * strip cannot show a grid the compositor is ignoring.
 */
export const cutPlan = (
  turnId: unknown,
  paceId: unknown,
  sched?: TurnSchedule | null,
): TurnSchedule | null => {
  // `turnAt` refuses a non-turning mode BEFORE it looks at the schedule, so a
  // beat grid under `hold` cuts nothing and must draw nothing.
  if (!isTurning(turnId)) return null;
  if (sched) {
    const { hold, first, fade } = sched;
    if (!(hold > 0) || !Number.isFinite(hold) || !Number.isFinite(first) || !(fade > 0)) return null;
    return { hold, first, fade };
  }
  const hold = turnHoldSec(turnId);
  if (!(hold > 0)) return null;
  const r = paceRate(paceId);
  const rate = Number.isFinite(r) && r > 0 ? r : 1;
  return { hold: hold / rate, first: hold / rate, fade: TURN_FADE_SEC / rate };
};

export interface CutMarks {
  /** Fractions of the take where a cut BEGINS, ascending. */
  at: number[];
  /** The dissolve's width, as a fraction of the take. A cut is a BAND, not a
   *  hairline: `march` at rest spends 0.7 s of every 5 s cross-fading, and a
   *  ruler that draws it as an instant hides the one number THE PACE keeps
   *  invariant. */
  fade: number;
  /** Cuts inside the take that were not drawn — DECISION 3. */
  hidden: number;
}

const NO_CUTS: CutMarks = { at: [], fade: 0, hidden: 0 };

/**
 * WHERE THE COLLAGE CUTS, as fractions of the take.
 *
 * Turn k lands at `first + (k-1) * hold` — the scheduled branch's expression,
 * which the roster branch also satisfies because `cutPlan` sets `first = hold`
 * there. Indexed, never accumulated: adding `hold` in a loop drifts by a float
 * per turn and the last mark of a 30 s take would sit visibly off the cut.
 */
export const cutMarks = (
  plan: TurnSchedule | null | undefined,
  take: number,
): CutMarks => {
  if (!plan || !Number.isFinite(take) || !(take > 0)) return NO_CUTS;
  const { hold, first, fade } = plan;
  if (!(hold > 0) || !(fade > 0) || !Number.isFinite(first)) return NO_CUTS;
  const at: number[] = [];
  let hidden = 0;
  // The compositor clamps its own turn index at `MAX_TURN_INDEX` and parks
  // there, so a mark past it would be a cut that never happens.
  for (let k = 1; k <= MAX_TURN_INDEX; k++) {
    const t = first + (k - 1) * hold;
    if (!(t < take)) break;
    if (!(t >= 0)) continue;
    if (at.length < MAX_STRIP_CUTS) at.push(fractionOf(t, take));
    else hidden++;
  }
  return { at, fade: Math.min(1, fade / take), hidden };
};

export interface LaneSegment {
  /** Fraction of the take this pass starts at. */
  start: number;
  /** Fraction of the take this pass ends at. */
  end: number;
  /** Did this pass run all the way to the source's OUT point inside the take?
   *  The last one usually has not, and drawing that is the point. */
  whole: boolean;
}

export interface LanePasses {
  segments: LaneSegment[];
  /** Passes inside the take, counting a partial one. EXACT — never capped. */
  laps: number;
  /** Too many seams to draw honestly: the caller renders one solid bar and
   *  says `laps` — DECISION 3. */
  dense: boolean;
}

const NO_PASSES: LanePasses = { segments: [], laps: 0, dense: false };

/**
 * ONE SOURCE'S PASSES THROUGH THE TAKE.
 *
 * `lapSec` is output seconds — `effectiveLength`, i.e. the trim window divided
 * by the rate that already carries THE SPEED. A source longer than the take
 * gets exactly one pass, marked NOT whole, which is the true statement that it
 * never finishes.
 */
export const lapSegments = (lapSec: number, take: number): LanePasses => {
  if (!Number.isFinite(lapSec) || !(lapSec > 0)) return NO_PASSES;
  if (!Number.isFinite(take) || !(take > 0)) return NO_PASSES;
  // The epsilon is subtracted BEFORE the ceil: a 5 s lap in a 10 s take is
  // 2.0000000000000004 on some pairs, and a third segment one hair wide at the
  // right-hand edge reads as a clip that repeats once more than it does.
  const laps = Math.max(1, Math.ceil(take / lapSec - MAP_EPSILON));
  if (laps > MAX_LANE_SEGMENTS) return { segments: [], laps, dense: true };
  const segments: LaneSegment[] = [];
  for (let i = 0; i < laps; i++) {
    const s = i * lapSec;
    const e = Math.min(take, s + lapSec);
    segments.push({
      start: fractionOf(s, take),
      end: fractionOf(e, take),
      whole: s + lapSec <= take + MAP_EPSILON,
    });
  }
  return { segments, laps, dense: false };
};

export interface TakeSourceInput {
  id: string;
  kind: 'clip' | 'music';
  /** The file's name, for the lane's own title. Optional because a clip's name
   *  is optional upstream, and `laneLabel` already falls back to its kind. */
  label?: string;
  /** EXACTLY what the Stage was handed for this source — window, loop, rate. */
  playback: WindowedPlayback;
}

export interface TakeLane extends LanePasses {
  id: string;
  kind: 'clip' | 'music';
  label: string;
  /** Output seconds one pass lasts. */
  lapSec: number;
}

export interface TakeMap {
  cuts: CutMarks;
  lanes: TakeLane[];
  /** Sources past `MAX_LANES` — DECISION 3. */
  hiddenLanes: number;
  /** Sources with no usable length — DECISION 4. */
  unknownLanes: number;
  /** Nothing to draw. The caller renders no strip at all rather than an empty
   *  box: a ruler with an empty tray under it says the take is empty, and a
   *  still collage under no music is not empty, it is still. */
  empty: boolean;
}

export const EMPTY_MAP: TakeMap = {
  cuts: NO_CUTS, lanes: [], hiddenLanes: 0, unknownLanes: 0, empty: true,
};

/**
 * THE WHOLE STRIP, in fractions.
 *
 * Sources keep the order they arrive in — which is the order the clip chips are
 * rendered in one row below, and the only thing that tells you which lane is
 * which without spending width on a label.
 */
export const takeMap = (
  take: number,
  sources: readonly TakeSourceInput[] | null | undefined,
  plan: TurnSchedule | null | undefined,
): TakeMap => {
  if (!Number.isFinite(take) || !(take > 0)) return EMPTY_MAP;
  const cuts = cutMarks(plan, take);
  const lanes: TakeLane[] = [];
  let hiddenLanes = 0;
  let unknownLanes = 0;
  for (const s of sources ?? []) {
    // `effectiveLength` reads `p.window.length` and a source is assembled by a
    // caller, not by this module — so a playback that is not a shaped object is
    // a throw inside a render, on a component that has no error boundary above
    // it. Totality is the contract every other module in this tree keeps; the
    // sweep's junk triples are what found this one.
    if (!s || !s.playback || typeof s.playback !== 'object' || !s.playback.window) {
      unknownLanes++;
      continue;
    }
    const lapSec = effectiveLength(s.playback);
    const passes = lapSegments(lapSec, take);
    if (passes.laps <= 0) { unknownLanes++; continue; }
    if (lanes.length >= MAX_LANES) { hiddenLanes++; continue; }
    lanes.push({
      id: s.id,
      kind: s.kind === 'music' ? 'music' : 'clip',
      label: typeof s.label === 'string' ? s.label : '',
      lapSec,
      ...passes,
    });
  }
  return {
    cuts,
    lanes,
    hiddenLanes,
    unknownLanes,
    empty: cuts.at.length === 0 && lanes.length === 0,
  };
};

/** Seconds, at the resolution a lane label can carry. `3.5s`, `12s`. */
const secLabel = (s: number): string =>
  s >= 10 ? `${Math.round(s)}s` : `${(Math.round(s * 10) / 10).toFixed(1)}s`;

/**
 * WHAT A LANE SAYS WHEN YOU ASK IT. One line, because it is a `title` on a 6 px
 * bar and the answer has to fit in a tooltip on a phone that has no hover.
 *
 * `x2.5` rather than `x3`: the fractional part IS the information — it says the
 * take ends mid-pass, which is the difference between a loop that lands and one
 * that gets cut off.
 */
export const laneLabel = (lane: TakeLane, take: number): string => {
  const times = Number.isFinite(take) && take > 0 && lane.lapSec > 0
    ? take / lane.lapSec
    : 0;
  const rounded = Math.round(times * 10) / 10;
  const passes = rounded >= 1 ? `x${rounded % 1 === 0 ? rounded.toFixed(0) : rounded.toFixed(1)}` : 'cut off';
  return `${lane.label || (lane.kind === 'music' ? 'music' : 'clip')} — ${secLabel(lane.lapSec)} ${passes}`;
};
