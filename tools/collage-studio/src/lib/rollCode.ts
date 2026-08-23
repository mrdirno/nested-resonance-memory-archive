// src/lib/rollCode.ts
// -----------------------------------------------------------------------------
// THE COMPOSITION CODE — the one seam between what is ON SCREEN and a Roll.
//
// WHY THIS FILE EXISTS
//   `diceRoll.ts` has had `encodeRoll` / `decodeRoll` since the roster landed,
//   and the module header has promised "same code, same collage, on any device"
//   the whole time. Nothing in the app ever called either function. The reason
//   is visible the moment you try: the roll flows ONE WAY. `handleDice` takes a
//   Roll apart into fifteen `setState` calls and there is no way back — no
//   function anywhere turns what is currently on screen INTO a Roll. Without
//   that direction there is no code to show, so there was no code.
//
//   This is that direction, and its inverse, in one place. Both are pure, so the
//   round trip is a property a sweep can hold to a hard equality instead of a
//   tolerance (tests/unit/rollCode.invariants.mjs).
//
// THE PROMISE, STATED PRECISELY
//   For every composition the UI can reach:  decode(encode(state)) === state.
//   Not "within a slider detent". Exactly. That is only true because the state
//   space IS the code's grid — see `snapRoll` in diceRoll.ts, and note that the
//   grid was chosen to contain the sliders' own steps (chaos 0.01, padding
//   0.001) rather than the other way round.
//
//   The images are NOT in the code and never will be. A code is a recipe: the
//   same code with your photographs is your collage. That is what makes one
//   worth sending.
//
// WHY THE SHUFFLE IS A FOURTH GROUP RATHER THAN PART OF THE SEED
//   `shuffleTrigger` is added to the seed to re-deal which photograph lands in
//   which fragment. Folding it into the seed on the way out would be wrong in a
//   way that is easy to miss: the seed also drives the LAYOUT, the twist angles
//   and the render, and only the deal is meant to move. So it travels as its
//   own optional trailing group, and a code without one deals from zero.
// -----------------------------------------------------------------------------

import type { LayoutMode, PrimitiveType } from '../types';
import type { ArrangementId, FocusId, TwistId } from './composition';
import type { Desk, LookId } from './grade';
import type { MoveId } from './motion';
import type { TurnId } from './turn';
import type { PaceId } from './pace';
import type { SyncId } from './beat';
import { type Roll, encodeRoll, decodeRoll, snapRoll } from './diceRoll';

/**
 * Everything about a collage EXCEPT the photographs — the app state the code
 * is a serialisation of. Named for the state variables in App.tsx so the wiring
 * is a transcription rather than a translation.
 */
export interface CompositionState {
  layoutMode: LayoutMode;
  primitive: PrimitiveType;
  count: number;
  /** 1..4 — the fragment multiplier. Travels as `zoom`, which is derived from it. */
  density: number;
  entropy: number;
  aspect: number;
  gutter: number;
  bgColor: string;
  seed: number;
  arrangement: ArrangementId;
  focus: FocusId;
  twist: TwistId;
  /**
   * THE LOOK — the colour grade. In the code, unlike the TITLE, because a grade
   * IS part of the recipe: "these fragments, dealt this way, leaning this far,
   * graded like this" describes a picture somebody can rebuild with their own
   * photographs. A caption cannot — somebody else's words over your pictures is
   * not the same collage, which is why that one stays out.
   */
  look: LookId;
  /**
   * THE DESK — the grade as four axes, when the user has moved one off the
   * preset. `null` is the ordinary case and means the look above IS the grade.
   *
   * In the code for the reason the look is, only more so: a custom grade is the
   * most recipe-shaped thing in the app — four numbers that describe a picture
   * anybody can rebuild with their own photographs. Leaving it out would mint a
   * code that decodes to the PRESET the user started from, which is a different
   * picture arriving under the same name, silently. (Contrast the title and the
   * fade, which are facts about YOUR render.)
   */
  adjust: Desk | null;
  /**
   * THE MOVE — how the picture drifts inside its fragment. In the code for the
   * same reason the look is: "these fragments, dealt this way, leaning this
   * far, graded like this, drifting like this" is a picture somebody can
   * rebuild with their own photographs, which is the entire test for whether
   * something belongs in a recipe.
   */
  move: MoveId;
  /**
   * THE TURN — how often the pictures re-cut to different fragments. In the
   * code for the same reason the move is: "these fragments, dealt this way,
   * re-cutting like this" is a picture somebody can rebuild with their own
   * photographs, and that is the whole test for whether something belongs in a
   * recipe. (Contrast the title and the fade, which are facts about YOUR
   * render, not about the composition.)
   */
  turn: TurnId;
  /**
   * THE PACE — how fast the clock the move and the turn are read against runs.
   * In the code for the reason all three above are: "these fragments, dealt
   * this way, re-cutting like this, at this tempo" is a picture somebody can
   * rebuild with their own photographs. It is the RATE half of what the move
   * and turn rosters used to answer alone.
   */
  pace: PaceId;
  /**
   * THE BEAT — whether the cuts snap to the music's grid. In the code because
   * the RELATIONSHIP is a recipe ("this one cuts on the beat"); the tempo it
   * snaps to is a fact about a file and stays out, exactly as the title and the
   * fade do. A code opened without music simply cuts on its own clock, and
   * cuts on the beat the moment a track is added.
   */
  sync: SyncId;
  /** How many times "Shuffle images" has re-dealt. */
  shuffle: number;
  /** True once the count is the user's decision rather than the source total. */
  countOwned: boolean;
}

/** The app's own derivation, in one place so the two directions cannot drift. */
export const zoomForDensity = (density: number) => 1 + (density - 1) * 0.5;
export const densityForZoom = (zoom: number) =>
  Math.max(1, Math.min(4, Math.round(1 + (zoom - 1) * 2)));

export const rollFromState = (s: CompositionState): Roll => snapRoll({
  layout: s.layoutMode,
  primitive: s.primitive,
  count: s.count,
  entropy: s.entropy,
  aspect: s.aspect,
  gutter: s.gutter,
  zoom: zoomForDensity(s.density),
  bg: s.bgColor,
  seed: s.seed,
  arrangement: s.arrangement,
  focus: s.focus,
  twist: s.twist,
  look: s.look,
  desk: s.adjust,
  move: s.move,
  turn: s.turn,
  pace: s.pace,
  sync: s.sync,
  countOwned: s.countOwned,
});

export const stateFromRoll = (r: Roll, shuffle = 0): CompositionState => ({
  layoutMode: r.layout,
  primitive: r.primitive,
  count: r.count,
  density: densityForZoom(r.zoom),
  entropy: r.entropy,
  aspect: r.aspect,
  gutter: r.gutter,
  bgColor: r.bg,
  seed: r.seed,
  arrangement: r.arrangement,
  focus: r.focus,
  twist: r.twist,
  // A Roll built before this field existed carries no look, and the picture it
  // described was ungraded — so the absence maps to `none` rather than to a
  // missing value the UI would have to defend against.
  look: r.look ?? 'none',
  // Absent means "the look above is the grade" — every Roll built before this
  // field existed described a collage on one of the eight, so the absence maps
  // to `null` rather than to a neutral desk. The difference is not cosmetic: a
  // materialised desk would show CUSTOM in the UI for a code that is a preset.
  adjust: r.desk ?? null,
  // Absent means `still` — a Roll built before this field existed described a
  // collage that did not move, so the absence maps to the no-op rather than to
  // a missing value the UI would have to defend against.
  move: r.move ?? 'still',
  // Absent means `hold` — a Roll built before this field existed described a
  // collage of one held deal, so the absence maps to the no-op.
  turn: r.turn ?? 'hold',
  // Absent means `even` — a Roll built before this field existed described a
  // collage running at the tempo the roster was written at, so the absence maps
  // to the no-op exactly as the three above do.
  pace: r.pace ?? 'even',
  // Absent means `off` — a Roll built before this field existed described a
  // collage cutting on its own clock, so the absence maps to the no-op exactly
  // as the four above do.
  sync: r.sync ?? 'off',
  shuffle,
  countOwned: !!r.countOwned,
});

const SHUFFLE_MAX = 36 ** 4 - 1; // four base-36 characters; ~1.7M re-deals

/** The composition on screen, as a code. */
export const encodeState = (s: CompositionState): string => {
  const sh = Math.max(0, Math.min(SHUFFLE_MAX, Math.round(s.shuffle || 0)));
  // The shuffle group is built FIRST so it can be folded into the code's
  // checksum. A guard that covers three of the four groups is a guard with a
  // hole in it, and the hole was measurable: every mangling that survived the
  // first cut had landed in this group.
  const group = sh > 0 ? sh.toString(36) : '';
  const base = encodeRoll(rollFromState(s), group);
  return group ? `${base}-${group.toUpperCase()}` : base;
};

/**
 * A code, as a composition — or null.
 *
 * NULL IS A REAL ANSWER AND MUST STAY ONE. This is fed straight from a text box
 * somebody pasted into, so the failure case is not exotic, it is Tuesday: a
 * truncated code, a chat client's smart quotes, a URL fragment, a word. Half a
 * composition applied on top of the one already on screen would be worse than
 * nothing, because the user cannot tell which half moved.
 */
export const decodeState = (code: string): CompositionState | null => {
  if (typeof code !== 'string') return null;
  const cleaned = code.trim().replace(/\s+/g, '');
  if (!cleaned) return null;
  const parts = cleaned.split('-');
  if (parts.length < 3 || parts.length > 4) return null;
  let shuffle = 0;
  const group = parts.length === 4 ? parts[3] : '';
  if (group) {
    if (!/^[0-9a-zA-Z]{1,4}$/.test(group)) return null;
    shuffle = parseInt(group, 36);
    if (!Number.isFinite(shuffle) || shuffle < 0) return null;
  }
  const roll = decodeRoll(parts.slice(0, 3).join('-'), group);
  if (!roll) return null;
  return stateFromRoll(roll, shuffle);
};

// =============================================================================
// THE LINK
// =============================================================================

/** The query key a composition rides in. Short, because it is typed by hand. */
export const CODE_PARAM = 'c';

/**
 * The code in a URL, if there is a readable one.
 *
 * Both the query string and the hash are searched: a code pasted into a chat
 * client survives either, and people move them between the two without meaning
 * anything by it.
 */
export const codeFromUrl = (href: string): string | null => {
  try {
    const url = new URL(href);
    const direct = url.searchParams.get(CODE_PARAM);
    if (direct) return direct;
    const hash = url.hash.replace(/^#/, '');
    if (!hash) return null;
    const inHash = new URLSearchParams(hash.includes('=') ? hash : `${CODE_PARAM}=${hash}`);
    return inHash.get(CODE_PARAM);
  } catch {
    return null;
  }
};
