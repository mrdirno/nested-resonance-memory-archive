// src/lib/compositionHistory.ts
// -----------------------------------------------------------------------------
// UNDO — the roll you liked, brought back.
//
// WHY THIS FILE EXISTS
//   Reported from the field (wishing well, collage/layout): *"Need an undo
//   button for quick recall … rolling the dice in full view."* Full bleed puts
//   the dice under your thumb precisely so you can roll it again and again to
//   compare layouts — and every press DESTROYS the one before it. Fifteen
//   setState calls land at once and the composition you were looking at three
//   seconds ago does not exist anywhere. The fastest way to find something good
//   was also the only way to lose it.
//
// WHAT A STEP IS, AND WHY IT IS NOT "EVERY STATE CHANGE"
//   A history that recorded every setState would put fifty entries in the stack
//   for one drag of the chaos slider and undo would walk you back through a
//   slider instead of back to a picture. So a step is a DESTRUCTIVE COMPOSITION
//   EVENT — the roll, the shuffle, the remix, an applied code — the four things
//   that replace the whole composition at once. Everything a person does with a
//   slider between two rolls rides along inside the snapshot, because the
//   snapshot is taken at the MOMENT of the destructive action, off the live
//   state. Roll, nudge the gutter, roll again, undo: you get your nudged
//   version back, not the one before you touched it.
//
// PAST / PRESENT / FUTURE — AND WHY PRESENT IS NOT STORED HERE
//   The live app IS the present. This module holds only what is behind and
//   ahead of it, and every operation is handed the present by the caller. That
//   is what keeps it pure and synchronous: `handleDice` cannot know the state
//   it is about to produce (fifteen setState calls have not landed yet), but it
//   knows exactly what is on screen right now, which is the thing worth
//   keeping. A model that tried to store the present would have to observe it
//   arriving asynchronously and would race the very button that caused it.
//
// WHAT IS IN A SNAPSHOT
//   The composition CODE (`rollCode.ts` — round-trip exact, swept to hard
//   equality) plus the two things the code deliberately leaves out: the
//   fragments pinned by hand, and the name of the recipe the last roll drew
//   from. The code omits them because a code is a recipe you SEND and neither
//   travels; undo is not sending anything, so both come back.
//
//   The photographs are not in here and could not be — the code has never
//   carried them. That is also the honest boundary of the feature: undo
//   restores a COMPOSITION, never a pool. Clearing your images is not an
//   undoable step and this module must not pretend otherwise.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

/**
 * One composition, complete enough to put back on screen exactly as it was.
 */
export interface CompositionSnapshot {
  /** The composition code — every parameter of the picture except the photographs. */
  code: string;
  /** Fragments pinned by hand: `[cellIndex, imageId]`. Not in the code; a lock is not a recipe. */
  locks: Array<[number, string]>;
  /** Name of the recipe the last roll drew from, so the readout matches the picture. */
  recipe?: string;
}

/**
 * What is behind the present and what is ahead of it. The present itself lives
 * in the app, and is passed in to every operation — see the header.
 */
export interface CompositionHistory {
  past: CompositionSnapshot[];
  future: CompositionSnapshot[];
}

/**
 * How many steps back each direction keeps.
 *
 * Chosen for the reported use — rolling repeatedly to compare — where the
 * interesting range is "the last handful", not "everything since I opened the
 * tab". A snapshot is a short string plus a handful of pairs, so the cap is
 * about the UNDO being useful (a stack you cannot remember the shape of is not
 * a recall), not about bytes.
 */
export const HISTORY_LIMIT = 24;

export const emptyHistory = (): CompositionHistory => ({ past: [], future: [] });

/** Locks arrive from a Map's iteration order, which is insertion order — two equal sets can differ. */
const locksKey = (locks: Array<[number, string]>): string =>
  locks
    .map(([i, id]) => `${i}:${id}`)
    .sort()
    .join('|');

/**
 * Two snapshots describing the same picture. Used ONLY to refuse a duplicate
 * step: pressing the dice twice before React has re-rendered would otherwise
 * push the same composition twice, and the first undo would then appear to do
 * nothing — which reads as a broken button, not as a no-op.
 */
export const sameSnapshot = (a: CompositionSnapshot, b: CompositionSnapshot): boolean =>
  a.code === b.code && a.recipe === b.recipe && locksKey(a.locks) === locksKey(b.locks);

export const canUndo = (h: CompositionHistory): boolean => h.past.length > 0;
export const canRedo = (h: CompositionHistory): boolean => h.future.length > 0;

/**
 * Record the composition that is on screen, immediately BEFORE something
 * replaces it.
 *
 * Clearing `future` is not an implementation detail, it is the rule that makes
 * undo trustworthy: once you undo three rolls and then roll a NEW one, the
 * three you abandoned are gone. Keeping them would mean the redo button
 * sometimes jumps to a picture from a branch you left, and a control that does
 * something different depending on history you cannot see is worse than no
 * control.
 */
export const commit = (
  h: CompositionHistory,
  present: CompositionSnapshot,
  limit: number = HISTORY_LIMIT,
): CompositionHistory => {
  const top = h.past[h.past.length - 1];
  if (top && sameSnapshot(top, present)) {
    // Same picture already on top. Still a branch: the future is abandoned.
    return h.future.length === 0 ? h : { past: h.past, future: [] };
  }
  return { past: [...h.past, present].slice(-limit), future: [] };
};

/**
 * Step back. Returns the snapshot to put on screen and the history that
 * results, or `null` when there is nothing behind the present — the caller
 * disables the button on `canUndo`, and this is the second lock on the door.
 */
export const undo = (
  h: CompositionHistory,
  present: CompositionSnapshot,
  limit: number = HISTORY_LIMIT,
): { history: CompositionHistory; restore: CompositionSnapshot } | null => {
  if (h.past.length === 0) return null;
  const restore = h.past[h.past.length - 1];
  return {
    history: { past: h.past.slice(0, -1), future: [...h.future, present].slice(-limit) },
    restore,
  };
};

/** Step forward again, undoing an undo. Mirror of `undo`; `null` when there is nothing ahead. */
export const redo = (
  h: CompositionHistory,
  present: CompositionSnapshot,
  limit: number = HISTORY_LIMIT,
): { history: CompositionHistory; restore: CompositionSnapshot } | null => {
  if (h.future.length === 0) return null;
  const restore = h.future[h.future.length - 1];
  return {
    history: { past: [...h.past, present].slice(-limit), future: h.future.slice(0, -1) },
    restore,
  };
};
