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
import type { LookId } from './grade';
import type { MoveId } from './motion';
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
   * THE MOVE — how the picture drifts inside its fragment. In the code for the
   * same reason the look is: "these fragments, dealt this way, leaning this
   * far, graded like this, drifting like this" is a picture somebody can
   * rebuild with their own photographs, which is the entire test for whether
   * something belongs in a recipe.
   */
  move: MoveId;
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
  move: s.move,
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
  // Absent means `still` — a Roll built before this field existed described a
  // collage that did not move, so the absence maps to the no-op rather than to
  // a missing value the UI would have to defend against.
  move: r.move ?? 'still',
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
