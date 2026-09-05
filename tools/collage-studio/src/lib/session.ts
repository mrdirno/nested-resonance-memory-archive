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

import { normalizeArtRecipe, type ArtRecipe } from './artRack';

/** IndexedDB coordinates. One database; the manifest row plus one row per image. */
export const SESSION_DB = 'collage-session';
export const SESSION_STORE = 'project';
export const SESSION_KEY = 'current';
/**
 * The image bytes, one record per asset, keyed by asset id — the store that made
 * this feature cheap enough to actually run. See `planAssetWrites`.
 */
export const SESSION_ASSETS = 'assets';
/** Bumped from 1 when `SESSION_ASSETS` was added; v1 rows are still readable. */
export const SESSION_DB_VERSION = 2;

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

// -----------------------------------------------------------------------------
// THE SNAPSHOT PLAN — why the autosave stopped re-zipping the whole pool.
//
// THE WISH (collage well, bug, about_tool=project): "Restoring images is slow and
// is glitching. Endless loop of restore, also does not restore quickly."
//
// The first cut of this feature stored the session as the SAME `.collage` zip a
// manual Save downloads — one row, one blob, "one format, no drift". That reads
// well and costs everything: the archive carries the image BYTES, so every
// debounce rebuilt the entire pool. Nudge the gutter slider on a twenty-photo
// project and 1.5s later the app re-fetched and re-zipped ~80MB on the main
// thread, for a manifest change of a few dozen characters. That is the glitch.
//
// The bytes are the part that never changes. So the store keeps them ONE row per
// asset, keyed by asset id, and a flush writes only what is genuinely new:
//
//   settings change  -> 0 image writes, one small manifest row
//   one photo added  -> 1 image write
//   one photo removed-> 1 delete
//
// `planAssetWrites` is that diff, and it is pure so the sweep can prove the
// steady-state claim (a pool that did not change writes NOTHING) rather than
// leaving it as a comment. IndexedDB stores Blobs natively — the zip was only
// ever needed to make a FILE, and a stored session is not a file.
// -----------------------------------------------------------------------------

/** What a flush must write and what it must delete, given what is already stored. */
export interface AssetWritePlan {
  /** Asset ids whose bytes are not in the store yet — read and write these. */
  write: string[];
  /** Ids in the store that the live pool no longer contains — delete these. */
  drop: string[];
}

/**
 * Diff the live pool against the store. Order follows the pool for `write` and
 * the store for `drop`, so a plan is deterministic and a test can name it.
 * Duplicate ids collapse: the pool is a set of assets, and writing one twice
 * would be the same bytes at twice the price.
 */
export function planAssetWrites(poolIds: readonly string[], storedIds: readonly string[]): AssetWritePlan {
  const stored = new Set(storedIds);
  const pool = new Set(poolIds);
  const write: string[] = [];
  const seen = new Set<string>();
  for (const id of poolIds) {
    if (stored.has(id) || seen.has(id)) continue;
    seen.add(id);
    write.push(id);
  }
  const drop: string[] = [];
  for (const id of storedIds) if (!pool.has(id)) drop.push(id);
  return { write, drop };
}

/**
 * One image as the session persists it. Note `width`/`height`: the live asset
 * has always known its own size, and the old restore path threw that away and
 * paid to `new Image()`-decode every photograph back — sequentially — just to
 * learn it again. Carrying two numbers turns restore into pure bookkeeping.
 */
export interface SessionAssetEntry {
  id: string;
  originalName: string;
  width: number;
  height: number;
  analysis: unknown;
  art?: ArtRecipe;
}

/** The two URLs a restored asset needs. See `hydrateSessionAssets`. */
export interface AssetUrls {
  /** Object URL over the original bytes. */
  src: string;
  /** Object URL over the ≤1024px thumbnail — ALIASES `src` when there isn't one. */
  previewSrc: string;
}

/** Live pool -> the manifest's image list. Pure; the caller adds the settings. */
export function sessionEntries(
  images: readonly { id: string; originalName?: string; width: number; height: number; analysis: unknown; art?: ArtRecipe }[],
): SessionAssetEntry[] {
  return images.map((i) => ({
    id: i.id,
    originalName: i.originalName || 'image.png',
    width: i.width,
    height: i.height,
    analysis: i.analysis,
    ...(i.art === undefined ? {} : { art: normalizeArtRecipe(i.art) }),
  }));
}

/** Validate the entire native-art pool before the caller mints recovery URLs. */
export function preflightSessionAssets(entries: unknown): SessionAssetEntry[] | null {
  if (!Array.isArray(entries) || entries.length === 0) return null;
  const out: SessionAssetEntry[] = [];
  for (const entry of entries) {
    if (!entry || typeof entry !== 'object' || typeof entry.id !== 'string' || !entry.id) return null;
    try {
      out.push({ ...entry, ...(entry.art === undefined ? {} : { art: normalizeArtRecipe(entry.art) }) });
    } catch { return null; }
  }
  return out;
}

/**
 * Manifest entries + the URLs minted for each id -> the pool to hydrate.
 *
 * BOTH URLS, AND THAT IS THE POINT. The first cut of restore set `previewSrc` to
 * the FULL-RESOLUTION original — and the app draws `previewSrc` everywhere
 * (App's still-render pass, and `stage.ts`, whose own comment states the
 * contract: "The Stage draws `previewSrc` — a <=1024px JPEG — everywhere").
 * A 4032x3024 phone photo is 15.5x the pixels of its 1024px thumbnail, so every
 * restored project silently promoted its whole pool to full-res previews: each
 * slider drag then re-decoded ~48MB per image, the editor got permanently
 * slower AFTER recovering than it was before the crash, and on a phone the tab
 * died again — which brings back the restore banner, which is the loop the
 * report actually describes. The thumbnail tier is now stored beside the
 * original and comes back with it.
 *
 * FAILS CLOSED, and for the reason `loadFromSVG` already documents: `arrangeBag`
 * deals from the pool's order and length, so ONE missing source re-deals every
 * fragment after it. A restore that silently comes back short is not a slightly
 * different collage, it is somebody else's collage. Null means "offer them a
 * fresh start", which is honest; a short pool is not.
 */
export function hydrateSessionAssets(
  entries: readonly SessionAssetEntry[] | undefined | null,
  urlById: Readonly<Record<string, AssetUrls>>,
): { id: string; src: string; previewSrc: string; originalName: string; width: number; height: number; analysis: unknown; art?: ArtRecipe }[] | null {
  const checked = preflightSessionAssets(entries);
  if (!checked) return null;
  const out = [];
  for (const e of checked) {
    const u = urlById[e.id];
    if (!u || !u.src) return null;
    out.push({
      id: e.id,
      src: u.src,
      // Aliases `src` when the asset never had a separate thumbnail — which is
      // exactly what `createThumbnail` does for an image already under 1024px,
      // so the pool comes back with the same aliasing an upload produces.
      previewSrc: u.previewSrc || u.src,
      originalName: e.originalName || 'image.png',
      width: typeof e.width === 'number' && e.width > 0 ? e.width : 0,
      height: typeof e.height === 'number' && e.height > 0 ? e.height : 0,
      analysis: e.analysis,
      ...(e.art === undefined ? {} : { art: e.art }),
    });
  }
  return out;
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
