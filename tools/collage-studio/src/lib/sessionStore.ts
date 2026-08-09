// src/lib/sessionStore.ts
// -----------------------------------------------------------------------------
// CRASH-SAFE SESSION RECOVERY — the durable store (browser only).
//
// One IndexedDB row holding the whole working project as a `.collage` blob — the
// EXACT bytes `buildProjectBlob` produces for a manual save, so restore is just
// the proven `loadProject` round-trip pointed at storage instead of a file. Why
// IndexedDB and not localStorage: the archive carries the image bytes and blows
// straight past the 5MB localStorage cap (see history.ts, which refuses blobs
// for that reason); IndexedDB stores a Blob natively and survives a tab reload.
//
// EVERY call fails soft. Private-mode Safari denies IndexedDB, a quota can be
// exceeded, a transaction can abort — none of that may ever break the editor,
// because this is insurance, not a feature the user asked to depend on. A
// failed write just means the last snapshot stands; a failed read means no
// restore is offered. The app behaves identically with the store absent.
//
// The `.collage` format persists images + all layout/style/title settings. It
// does NOT carry live video clips or the soundtrack (neither does a manual
// save), so a restored video project comes back as its extracted stills plus
// every setting — the 90% of "what I was doing" that used to vanish whole.
//
// Author: Aldrin Payopay (aldrin.gdf@gmail.com)
// -----------------------------------------------------------------------------

import { SESSION_DB, SESSION_STORE, SESSION_KEY } from './session';

interface StoredSession {
  /** The `.collage` archive — identical to what a manual Save downloads. */
  blob: Blob;
  /** Epoch ms the snapshot was written; drives the "moments ago" label. */
  savedAt: number;
  /** Image count at write time; shown in the banner without decoding the blob. */
  images: number;
}

/** Open (or create) the one-store database. Resolves null on any failure. */
function openDb(): Promise<IDBDatabase | null> {
  return new Promise((resolve) => {
    try {
      if (typeof indexedDB === 'undefined') { resolve(null); return; }
      const req = indexedDB.open(SESSION_DB, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(SESSION_STORE)) db.createObjectStore(SESSION_STORE);
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve(null);
      req.onblocked = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

/** Write the current session, replacing any previous one. Best-effort. */
export async function putSession(blob: Blob, images: number): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    try {
      const tx = db.transaction(SESSION_STORE, 'readwrite');
      const record: StoredSession = { blob, savedAt: Date.now(), images };
      tx.objectStore(SESSION_STORE).put(record, SESSION_KEY);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
      tx.onabort = () => resolve();
    } catch {
      resolve();
    }
  });
  try { db.close(); } catch { /* ignore */ }
}

/** Cheap existence + metadata read that never pulls the (large) blob. */
export async function getSessionMeta(): Promise<{ savedAt: number; images: number } | null> {
  const db = await openDb();
  if (!db) return null;
  const res = await new Promise<{ savedAt: number; images: number } | null>((resolve) => {
    try {
      const tx = db.transaction(SESSION_STORE, 'readonly');
      const rq = tx.objectStore(SESSION_STORE).get(SESSION_KEY);
      rq.onsuccess = () => {
        const v = rq.result as StoredSession | undefined;
        resolve(v && v.blob ? { savedAt: v.savedAt, images: v.images } : null);
      };
      rq.onerror = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
  try { db.close(); } catch { /* ignore */ }
  return res;
}

/** Pull the stored archive for an actual restore. Null if none / unreadable. */
export async function getSessionBlob(): Promise<Blob | null> {
  const db = await openDb();
  if (!db) return null;
  const res = await new Promise<Blob | null>((resolve) => {
    try {
      const tx = db.transaction(SESSION_STORE, 'readonly');
      const rq = tx.objectStore(SESSION_STORE).get(SESSION_KEY);
      rq.onsuccess = () => {
        const v = rq.result as StoredSession | undefined;
        resolve(v?.blob ?? null);
      };
      rq.onerror = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
  try { db.close(); } catch { /* ignore */ }
  return res;
}

/** Forget the stored session (on Discard, so the next launch does not re-ask). */
export async function clearSession(): Promise<void> {
  const db = await openDb();
  if (!db) return;
  await new Promise<void>((resolve) => {
    try {
      const tx = db.transaction(SESSION_STORE, 'readwrite');
      tx.objectStore(SESSION_STORE).delete(SESSION_KEY);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
      tx.onabort = () => resolve();
    } catch {
      resolve();
    }
  });
  try { db.close(); } catch { /* ignore */ }
}
