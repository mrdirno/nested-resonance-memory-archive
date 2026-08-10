// src/lib/dealRoll.ts
// -----------------------------------------------------------------------------
// THE COLOUR DICE — colour sorting and cropping style, WITHOUT losing the
// layout you just found.
//
// WISHED FOR (wishing well, collage/layout): *"Add another dice for color
// sorting and cropping style. For full view for better ui/ux."*
//
// WHY IT IS A SECOND BUTTON AND NOT A FLAG ON THE FIRST
//   The main dice replaces the WHOLE composition — generator, fragment count,
//   chaos, aspect, gutter, background, seed, grade, motion. That is what makes
//   it worth pressing, and it is also why it is useless once you like the shape
//   you are looking at: the only way to try a different colour sorting was to
//   roll the shape away with it. So the arrangement and the crop, the two
//   things that decide WHICH photo lands WHERE and WHAT part of it you see,
//   had no roll of their own. They lived in the Advanced panel as three
//   pickers — thirty-two chips you scroll a dock to reach, which on a phone in
//   full bleed is not a control that exists.
//
// WHAT IT ROLLS, AND WHAT IT REFUSES TO TOUCH
//   ROLLS: arrangement (the colour sort), focus (what each fragment centres
//   on), twist (how the picture leans in its fragment).
//   LEAVES ALONE: layout, count, entropy, aspect, gutter, background, zoom,
//   seed, look, move, the title, the soundtrack. The seed matters most of that
//   list — it drives the subdivision, so rolling it would move every fragment
//   edge and the button would silently be the first dice again.
//
// NEVER `natural`
//   `natural` is the source-first fill: no colour sorting at all. It is a real
//   answer and the main dice keeps it a fifth of the time — but a button whose
//   entire job is colour sorting cannot hand back the unsorted order and call
//   it a roll. Ten arrangements remain, all of them sorts.
//
// ALWAYS DIFFERENT
//   A dice that returns what is already on screen is a broken button, and this
//   one draws from a space small enough (10 x 5 x 5) that the collision is not
//   theoretical. So the roll is checked against the deal it is replacing and
//   stepped forward when it matches — see `rollDeal`. Swept in
//   tests/unit/dealRoll.invariants.mjs across chained rolls, which is the shape
//   the field actually presses it in.
// -----------------------------------------------------------------------------

import type { LayoutMode } from '../types';
import { ARRANGEMENT_IDS, type ArrangementId, type FocusId, type TwistId } from './composition';
import { arrangementFor, focusFor, twistFor } from './diceRoll';

/** The three fields this dice owns. Everything else in a `Roll` is off limits. */
export interface Deal {
  arrangement: ArrangementId;
  focus: FocusId;
  twist: TwistId;
}

/**
 * Every arrangement that is a SORT — the roster minus `natural`.
 *
 * Derived from `ARRANGEMENT_IDS` rather than written out, so an arrangement
 * appended to the roster is reachable by this dice on the same commit that adds
 * it. A chip the dice can never reach may as well not exist.
 */
export const SORTED_ARRANGEMENT_IDS: ArrangementId[] =
  ARRANGEMENT_IDS.filter((id) => id !== 'natural');

/**
 * How often the colour dice comes back STRAIGHT.
 *
 * Lower than the main dice's 0.58 because half this button's name is the crop
 * and a roll pressed for the lean that keeps coming back square has not shown
 * you the row. Not near zero, because the crop-in cost a twist charges — real
 * picture thrown away, see `TWIST_MODES` — does not care which button asked.
 */
export const DEAL_STRAIGHT_CHANCE = 0.45;

export interface DealOptions {
  /**
   * The layout ON SCREEN. Not rolled — read, because which arrangements and
   * twists can even be SEEN depends on whether the figure has a centre. A
   * colour wheel over a rectilinear grid is a wheel nobody can read.
   */
  layout: LayoutMode;
  /** The deal being replaced. The roll is never allowed to return it unchanged. */
  previous?: Deal;
  /** Injectable for tests / reproduction. Defaults to `Math.random`. */
  rnd?: () => number;
}

/**
 * Roll the colour sorting and the crop.
 *
 * DRAWS A BOUNDED NUMBER OF VALUES — at most seven, never a retry loop. A
 * redraw-until-different loop would take an unbounded number of values off the
 * stream and, on a degenerate rng, not terminate at all; stepping the
 * arrangement forward one place in the roster is a single deterministic move
 * that is guaranteed to differ, and it costs nothing.
 */
export const rollDeal = (opts: DealOptions): Deal => {
  const rnd = opts.rnd ?? Math.random;

  // `naturalChance: 0` — see the header. The gate still draws, so the stream
  // position does not depend on which dice is asking.
  const arrangement = arrangementFor(opts.layout, rnd, 0);
  const focus = focusFor(rnd);
  const twist = twistFor(opts.layout, rnd, DEAL_STRAIGHT_CHANCE);

  const prev = opts.previous;
  const same = !!prev
    && prev.arrangement === arrangement
    && prev.focus === focus
    && prev.twist === twist;
  if (!same) return { arrangement, focus, twist };

  // Collided with what is on screen. Step the arrangement — the axis with the
  // most alternatives, and the one the button is named after.
  // `Math.max(0, …)`: an id outside the sorted roster cannot reach here (the
  // gate above is closed), but a -1 would silently step to the wrong element
  // rather than fail, and a silent wrong answer is the worse failure.
  const i = Math.max(0, SORTED_ARRANGEMENT_IDS.indexOf(arrangement));
  return {
    arrangement: SORTED_ARRANGEMENT_IDS[(i + 1) % SORTED_ARRANGEMENT_IDS.length],
    focus,
    twist,
  };
};
