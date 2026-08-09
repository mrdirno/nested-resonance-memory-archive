// src/lib/session.ts
// -----------------------------------------------------------------------------
// CRASH-SAFE SESSION RECOVERY — the pure decision core.
//
// THE WISH (collage well, bug, about_tool=export): "As I was capturing the video
// at 4k resolution ... the app refreshed or crashed and lost what I was doing."
//
// A 4K video capture pushes a phone's browser to the edge of its memory; the OS
// reloads the tab, or a stray pull-to-refresh reloads it, and because every bit
// of project state lived only in React `useState`, the whole collage vanished.
// There was no autosave anywhere in the app — the only durable save was the user
// manually downloading a `.collage` archive, which nobody does mid-capture.
//
// The cure is the thing every real editor has and this one did not: the working
// project is written to durable storage continuously, and on the next launch the
// app OFFERS to bring it back. This module is the PURE half — the gates that
// decide WHEN to write and WHEN to offer a restore. The browser-only IndexedDB
// I/O lives in `sessionStore.ts`; keeping the decisions here is what lets the
// unit sweep prove them without a DOM.
//
// The safety properties these gates encode, and why each one exists:
//   • never autosave an EMPTY pool     — nothing to lose, and a blank snapshot
//                                         would clobber the very session a user
//                                         is one tap away from restoring.
//   • never autosave DURING an export  — the capture is the memory cliff we are
//                                         fixing; zipping the pool at that exact
//                                         moment is throwing fuel on the fire.
//   • never autosave WHILE a restore is offered — it would overwrite the stored
//                                         session before the user accepts it.
//   • only OFFER a restore into an empty pool — never shadow a project that a
//                                         deep link or an Open already loaded.
//
// Author: Aldrin Payopay (aldrin.gdf@gmail.com)
// -----------------------------------------------------------------------------

/** IndexedDB coordinates. One database, one store, one row: the current session. */
export const SESSION_DB = 'collage-session';
export const SESSION_STORE = 'project';
export const SESSION_KEY = 'current';

/**
 * How long the pool must sit still before a snapshot is written. Long enough
 * that dragging a slider or typing a title does not re-zip the pool on every
 * frame; short enough that "what I was doing" is at most this stale when the
 * tab dies. The pre-capture checkpoint (App.tsx) bypasses this entirely, so the
 * one moment that actually crashes is always saved at zero staleness.
 */
export const AUTOSAVE_DEBOUNCE_MS = 1500;

export interface AutosaveGate {
  /** Size of the live image pool. Zero means there is nothing worth persisting. */
  imageCount: number;
  /** A still export OR a video capture is running right now. */
  isExporting: boolean;
  /** A restore banner is on screen / a restore is in flight. */
  isRestoring: boolean;
}

/**
 * May a session snapshot be written at this instant? All three guards must be
 * clear. This is the single chokepoint every autosave trigger passes through.
 */
export function canAutosave(g: AutosaveGate): boolean {
  return g.imageCount > 0 && !g.isExporting && !g.isRestoring;
}

/**
 * Should the browser's native "leave site?" prompt fire on unload? Only when
 * there is work that is not on disk — i.e. a non-empty pool changed since the
 * last explicit download. This catches an accidental refresh / back-gesture /
 * tab close; it does NOT fire on a hard OOM kill, which is exactly what the
 * IndexedDB autosave is there to cover.
 */
export function hasUnsavedWork(imageCount: number, dirty: boolean): boolean {
  return imageCount > 0 && dirty;
}

/**
 * Should the restore banner be shown? Only when a stored session exists AND the
 * live pool is empty. The second half is the safety rail: a project loaded by a
 * deep link or by Open must never be shadowed by an offer to replace it.
 *
 * Note this is the exact complement of `canAutosave`'s image guard — the two can
 * never both be true for the same pool, so offering a restore always freezes the
 * writer that would overwrite it.
 */
export function shouldPromptRestore(hasStoredSession: boolean, imageCount: number): boolean {
  return hasStoredSession && imageCount === 0;
}

/**
 * Coarse "how long ago" label for the restore banner. Pure — the caller passes
 * the delta so the function never reads the clock. Buckets, not precision: the
 * user only needs to recognise the session, not time it.
 */
export function formatAgo(deltaMs: number): string {
  const s = Math.max(0, Math.floor(deltaMs / 1000));
  if (s < 45) return 'moments ago';
  const m = Math.floor(s / 60);
  if (m < 1) return 'moments ago';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}
