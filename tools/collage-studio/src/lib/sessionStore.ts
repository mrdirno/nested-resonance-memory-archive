// src/lib/sessionStore.ts
// -----------------------------------------------------------------------------
// CRASH-SAFE SESSION RECOVERY — the durable store (browser only).
//
// TWO stores, and the split is the whole performance story. `project` holds one
// small row — the settings manifest plus each image's id/name/size/analysis.
// `assets` holds the image BYTES, one Blob row per asset id. A flush writes the
// manifest row always and an image row only the first time that image is seen
// (see `planAssetWrites` in session.ts for the diff, and for what the first cut
// of this cost).
//
// WHAT THIS REPLACED, and why it had to go: v1 stored the session as the same
// `.collage` ZIP a manual Save downloads — appealing ("one format, no drift"),
// and ruinous. The archive carries the image bytes, so nudging a slider on a
// twenty-photo project re-fetched and re-zipped ~80MB on the main thread every
// 1.5s, and restoring meant unzipping it all back. IndexedDB stores Blobs
// natively; the zip was only ever needed to produce a FILE, and a stored session
// is not a file. The `.collage` format itself is untouched — every saved project
// still opens exactly as before.
//
// V1 ROWS ARE STILL READ. A session written by the previous build is somebody's
// unfinished work sitting in their browser right now; an upgrade that discarded
// it would be a strange way to ship a feature about not losing work. `loadSession`
// returns a tagged `archive` result for those, which App feeds through the
// original `loadProject` round-trip once. The next flush rewrites it as v2.
//
// EVERY call fails soft. Private-mode Safari denies IndexedDB, a quota can be
// exceeded, a transaction can abort — none of that may ever break the editor,
// because this is insurance, not a feature the user asked to depend on. A failed
// write just means the last snapshot stands; a failed read means no restore is
// offered. The app behaves identically with the store absent.
//
// The session persists images + all layout/style/title settings. It does NOT
// carry live video clips or the soundtrack (neither does a manual save), so a
// restored video project comes back as its extracted stills plus every setting —
// the 90% of "what I was doing" that used to vanish whole.
//
// Author: Aldrin Payopay (aldrin.gdf@gmail.com)
// -----------------------------------------------------------------------------

import { SESSION_DB, SESSION_STORE, SESSION_ASSETS, SESSION_KEY, SESSION_DB_VERSION } from './session';
import type { SessionAssetEntry } from './session';

/** The v2 manifest row: settings + per-image metadata, no bytes. Kilobytes. */
interface SessionRecordV2 {
  v: 2;
  /** `AppState` fields plus `images: SessionAssetEntry[]` — one manifest shape. */
  manifest: { images?: SessionAssetEntry[] } & Record<string, unknown>;
  savedAt: number;
  /** Image count, so the banner can name it without touching the assets store. */
  images: number;
}

/** The v1 row this build still reads: the whole project as one `.collage` blob. */
interface SessionRecordV1 {
  blob: Blob;
  savedAt: number;
  images: number;
}

type AnyRecord = Partial<SessionRecordV2> & Partial<SessionRecordV1>;

/** Open (or create) the database. Resolves null on any failure. */
function openDb(): Promise<IDBDatabase | null> {
  return new Promise((resolve) => {
    try {
      if (typeof indexedDB === 'undefined') { resolve(null); return; }
      const req = indexedDB.open(SESSION_DB, SESSION_DB_VERSION);
      req.onupgradeneeded = () => {
        const db = req.result;
        // Both are created if absent, and `project` is never dropped — a v1 row
        // living in it is a real session and survives the upgrade intact.
        if (!db.objectStoreNames.contains(SESSION_STORE)) db.createObjectStore(SESSION_STORE);
        if (!db.objectStoreNames.contains(SESSION_ASSETS)) db.createObjectStore(SESSION_ASSETS);
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve(null);
      req.onblocked = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

function closeQuietly(db: IDBDatabase) { try { db.close(); } catch { /* ignore */ } }

/**
 * Which image ids already have their bytes stored. KEYS ONLY — this is the read
 * that lets a flush skip work, so it must never pull a blob to decide not to
 * write one.
 */
export async function storedAssetIds(): Promise<string[]> {
  const db = await openDb();
  if (!db) return [];
  const res = await new Promise<string[]>((resolve) => {
    try {
      if (!db.objectStoreNames.contains(SESSION_ASSETS)) { resolve([]); return; }
      const tx = db.transaction(SESSION_ASSETS, 'readonly');
      const rq = tx.objectStore(SESSION_ASSETS).getAllKeys();
      rq.onsuccess = () => resolve((rq.result || []).map(String));
      rq.onerror = () => resolve([]);
      tx.onabort = () => resolve([]);
    } catch {
      resolve([]);
    }
  });
  closeQuietly(db);
  return res;
}

/**
 * The bytes for one asset: the original, and the ≤1024px thumbnail the whole
 * preview path draws. `preview` is null when the asset never had a separate one
 * (`createThumbnail` returns the source unchanged under 1024px), so identical
 * bytes are never stored twice.
 *
 * ARRAYBUFFER, NOT BLOB, AND THIS IS THE WHOLE FEATURE ON SAFARI. WebKit accepts
 * a plain object, an ArrayBuffer and a Uint8Array into IndexedDB and REFUSES a
 * Blob — the transaction errors with an empty error and aborts. Both stores are
 * written in one transaction, so a single Blob took the manifest down with it:
 * on WebKit nothing was ever persisted, no banner was ever offered, and crash
 * recovery was a silent no-op from the day it shipped. Chromium stores Blobs
 * happily, which is exactly why nobody saw it. Measured, per engine:
 *
 *   value kind      Chromium   WebKit
 *   plain object    OK         OK
 *   ArrayBuffer     OK         OK
 *   Uint8Array      OK         OK
 *   Blob            OK         ERROR (empty name, empty message)
 *
 * A phone browser under memory pressure is the entire premise of this feature,
 * and on iOS every browser is WebKit. The mime type rides along so the Blob can
 * be rebuilt exactly on the way out.
 */
export interface StoredAsset {
  full: ArrayBuffer;
  fullType: string;
  preview: ArrayBuffer | null;
  previewType: string | null;
}

/** What v2 rows written before the WebKit fix hold — read, never written. */
interface LegacyBlobAsset { full: Blob; preview: Blob | null }

/** Rebuild the pair of blobs from a row of either shape. Null if unusable. */
function assetToBlobs(v: unknown): { full: Blob; preview: Blob | null } | null {
  const a = v as Partial<StoredAsset> & Partial<LegacyBlobAsset>;
  if (!a || !a.full) return null;
  // Rows written by the first v2 deploy hold real Blobs; keep reading them.
  if (typeof Blob !== 'undefined' && a.full instanceof Blob) {
    const p = a.preview instanceof Blob ? a.preview : null;
    return { full: a.full, preview: p };
  }
  try {
    const full = new Blob([a.full as ArrayBuffer], { type: (a as StoredAsset).fullType || 'image/jpeg' });
    const pb = (a as StoredAsset).preview;
    const preview = pb ? new Blob([pb], { type: (a as StoredAsset).previewType || 'image/jpeg' }) : null;
    return { full, preview };
  } catch {
    return null;
  }
}

export interface SessionWrite {
  /** Settings + `images: SessionAssetEntry[]`. Small; written every flush. */
  manifest: { images?: SessionAssetEntry[] } & Record<string, unknown>;
  savedAt: number;
  images: number;
  /** Only the bytes that are NEW to the store (from `planAssetWrites`). */
  write: { id: string; asset: StoredAsset }[];
  /** Ids to delete — assets the pool dropped. */
  drop: string[];
}

/**
 * Commit a snapshot. One transaction over both stores, so the manifest and the
 * bytes it names can never land half-written: an abort leaves the PREVIOUS
 * snapshot whole, which is the only state a recovery feature may fail into.
 */
export async function putSession(w: SessionWrite): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    try {
      const tx = db.transaction([SESSION_STORE, SESSION_ASSETS], 'readwrite');
      const assets = tx.objectStore(SESSION_ASSETS);
      for (const a of w.write) assets.put(a.asset, a.id);
      for (const id of w.drop) assets.delete(id);
      const record: SessionRecordV2 = { v: 2, manifest: w.manifest, savedAt: w.savedAt, images: w.images };
      tx.objectStore(SESSION_STORE).put(record, SESSION_KEY);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
      tx.onabort = () => resolve();
    } catch {
      resolve();
    }
  });
  closeQuietly(db);
}

/** Read the one manifest row. Shared by the metadata peek and the full restore. */
async function readRecord(db: IDBDatabase): Promise<AnyRecord | null> {
  return new Promise((resolve) => {
    try {
      const tx = db.transaction(SESSION_STORE, 'readonly');
      const rq = tx.objectStore(SESSION_STORE).get(SESSION_KEY);
      rq.onsuccess = () => resolve((rq.result as AnyRecord | undefined) ?? null);
      rq.onerror = () => resolve(null);
      tx.onabort = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

/**
 * Cheap existence + metadata read for the launch banner. Never touches the
 * assets store, so offering a restore costs the same whether the session holds
 * two photographs or two hundred.
 */
export async function getSessionMeta(): Promise<{ savedAt: number; images: number } | null> {
  const db = await openDb();
  if (!db) return null;
  const rec = await readRecord(db);
  closeQuietly(db);
  if (!rec) return null;
  // v2 is valid when it names images; v1 is valid when it still has its blob.
  const isV2 = rec.v === 2 && Array.isArray(rec.manifest?.images);
  const isV1 = !!rec.blob;
  if (!isV2 && !isV1) return null;
  return { savedAt: rec.savedAt ?? 0, images: rec.images ?? 0 };
}

export type LoadedSession =
  /** v2: the manifest plus every image's bytes, ready to hydrate. No unzip. */
  | { kind: 'session'; manifest: { images?: SessionAssetEntry[] } & Record<string, unknown>; assets: Record<string, { full: Blob; preview: Blob | null }> }
  /** v1: a `.collage` archive written by the previous build. */
  | { kind: 'archive'; blob: Blob };

/**
 * Pull everything needed for an actual restore. Null if there is nothing, or if
 * the row names an image whose bytes are missing — fail closed, because a pool
 * that comes back short re-deals every fragment after the gap (see
 * `hydrateSessionAssets`). The blobs come out in one keyed read; the caller
 * mints the object URLs, because the app owns those for the session.
 */
export async function loadSession(): Promise<LoadedSession | null> {
  const db = await openDb();
  if (!db) return null;
  const rec = await readRecord(db);
  if (!rec) { closeQuietly(db); return null; }

  if (rec.v !== 2 || !Array.isArray(rec.manifest?.images)) {
    closeQuietly(db);
    return rec.blob ? { kind: 'archive', blob: rec.blob } : null;
  }

  const manifest = rec.manifest as { images?: SessionAssetEntry[] } & Record<string, unknown>;
  const ids = (manifest.images ?? []).map((e) => e.id);
  const assets = await new Promise<Record<string, { full: Blob; preview: Blob | null }> | null>((resolve) => {
    try {
      if (!db.objectStoreNames.contains(SESSION_ASSETS)) { resolve(null); return; }
      const tx = db.transaction(SESSION_ASSETS, 'readonly');
      const store = tx.objectStore(SESSION_ASSETS);
      const out: Record<string, { full: Blob; preview: Blob | null }> = {};
      let missing = false;
      for (const id of ids) {
        const rq = store.get(id);
        rq.onsuccess = () => {
          const pair = assetToBlobs(rq.result);
          if (pair) out[id] = pair; else missing = true;
        };
        rq.onerror = () => { missing = true; };
      }
      tx.oncomplete = () => resolve(missing ? null : out);
      tx.onerror = () => resolve(null);
      tx.onabort = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
  closeQuietly(db);
  return assets ? { kind: 'session', manifest, assets } : null;
}

/** Forget the stored session (on Discard, so the next launch does not re-ask). */
export async function clearSession(): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    try {
      const stores = [SESSION_STORE, SESSION_ASSETS].filter((s) => db.objectStoreNames.contains(s));
      const tx = db.transaction(stores, 'readwrite');
      // The bytes go too. Leaving orphaned assets behind would hold a whole
      // project's worth of storage for a session the user explicitly discarded.
      for (const s of stores) tx.objectStore(s).clear();
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
      tx.onabort = () => resolve();
    } catch {
      resolve();
    }
  });
  closeQuietly(db);
}
