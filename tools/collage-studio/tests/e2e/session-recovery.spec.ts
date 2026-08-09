// tests/e2e/session-recovery.spec.ts
// -----------------------------------------------------------------------------
// CRASH-SAFE SESSION RECOVERY — the whole reason this feature exists.
//
// THE WISH (collage well, bug, about_tool=export): "As I was capturing the video
// at 4k resolution ... the app refreshed or crashed and lost what I was doing."
//
// Before this, EVERY bit of project state lived only in React `useState`. A tab
// reload — an OOM kill under a 4K capture, or a stray pull-to-refresh — wiped it
// whole, with no autosave anywhere in the app. The cure: the working project is
// written to IndexedDB continuously, and the next launch OFFERS to bring it back.
//
// This drives the REAL UI: import photos, let the debounced autosave land, then
// `page.reload()` — the exact event that used to destroy the work — and assert
// the collage comes BACK. A `page.reload()` keeps the same browser context, so
// IndexedDB survives it, which is precisely the property the feature relies on.
//
// Run against the collage dev server explicitly (SCAR: :5173 is Persona 500):
//   COLLAGE_BASE_URL=http://localhost:5199/ npx playwright test \
//     tests/e2e/session-recovery.spec.ts --project=chromium
// -----------------------------------------------------------------------------

import { test, expect } from '@playwright/test';
import JSZip from 'jszip';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

/** A plausible `AnalysisResult`, so a hand-built archive hydrates like a real one. */
const ANALYSIS = { face: null, energy: { x: 0.5, y: 0.5 }, color: { r: 128, g: 128, b: 128, h: 0, s: 0, l: 0.5 } };

/**
 * A `.collage` archive exactly as the PREVIOUS build wrote it into IndexedDB —
 * note the manifest carries no width/height, which is what forces the load path
 * to fall back to a real decode. `bytes` is what lands in `images/`, so a caller
 * can hand it a genuine JPEG or deliberate garbage.
 */
async function legacyArchive(bytes: Buffer): Promise<Buffer> {
  const zip = new JSZip();
  zip.file('manifest.json', JSON.stringify({
    version: '1.0',
    mode: 'simple',
    layout: { mode: 'minimal', primitive: 'rect', count: 4, density: 1, countOwned: true, shuffle: 0, seed: 7, aspect: 1, gutter: 0.005, entropy: 0, arrangement: 'natural', focus: 'auto', twist: 'none', move: 'still' },
    style: { background: '#000000', look: 'none' },
    images: [{ id: 'legacy-1', storageFilename: 'asset-0-legacy-1.jpg', originalName: 'legacy.jpg', analysis: ANALYSIS }],
  }));
  zip.folder('images')!.file('asset-0-legacy-1.jpg', bytes);
  return zip.generateAsync({ type: 'nodebuffer' });
}

/**
 * Write a v1 ROW into the app's IndexedDB — a `{blob, savedAt, images}` record
 * with no `v`, exactly what the previous build left in people's browsers.
 *
 * Opened WITHOUT a version on purpose: by the time this runs the app has already
 * created the database at v2, and asking for v1 against a v2 database raises
 * VersionError, fires `onerror`, and writes nothing — a seed that silently does
 * not seed, which looks precisely like the feature being broken.
 */
async function seedLegacySession(page: import('@playwright/test').Page, archive: Buffer) {
  const wrote = await page.evaluate(async (b64: string) => {
    const bin = atob(b64);
    const arr = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    const blob = new Blob([arr], { type: 'application/zip' });

    const open = (version?: number) => new Promise<IDBDatabase | null>((res) => {
      const r = version ? indexedDB.open('collage-session', version) : indexedDB.open('collage-session');
      r.onupgradeneeded = () => { const d = r.result; if (!d.objectStoreNames.contains('project')) d.createObjectStore('project'); };
      r.onsuccess = () => res(r.result);
      r.onerror = () => res(null);
      r.onblocked = () => res(null);
    });

    let db = await open();
    if (!db) return false;
    if (!db.objectStoreNames.contains('project')) {
      const next = db.version + 1; db.close();
      db = await open(next);
      if (!db) return false;
    }
    const ok = await new Promise<boolean>((resolve) => {
      const stores = ['project', ...(db!.objectStoreNames.contains('assets') ? ['assets'] : [])];
      const tx = db!.transaction(stores, 'readwrite');
      // A v1 row and v2 asset rows must never coexist, or the fallback under
      // test is not the path that runs.
      if (stores.includes('assets')) tx.objectStore('assets').clear();
      tx.objectStore('project').put({ blob, savedAt: Date.now() - 60_000, images: 1 }, 'current');
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
      tx.onabort = () => resolve(false);
    });
    db.close();
    return ok;
  }, archive.toString('base64'));
  expect(wrote, 'the legacy session was seeded').toBe(true);
}

// > AUTOSAVE_DEBOUNCE_MS (1500) plus room to zip the pool and commit the IDB
// write. The debounced snapshot must have landed before the reload, or there is
// nothing to restore and the assertion would (correctly) fail.
const AUTOSAVE_SETTLE_MS = 2800;

test.describe('crash-safe session recovery', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    // COUNT THE WRITES AT THE STORE. The bug this suite now guards is an
    // autosave that re-persisted every image byte on every settings change, and
    // the honest measurement of that is not a stopwatch — it is how many rows go
    // into the `assets` store. Patched before app code runs, per store name, so
    // a manifest write and an image write can never be confused for each other.
    await page.addInitScript(() => {
      (window as any).__idbPuts = { assets: 0, project: 0 };
      const put = IDBObjectStore.prototype.put;
      IDBObjectStore.prototype.put = function (this: IDBObjectStore, ...args: any[]) {
        const c = (window as any).__idbPuts;
        if (c && this.name in c) c[this.name]++;
        return (put as any).apply(this, args);
      };
    });
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    }).catch(() => { /* fine */ });
  });

  test('a reloaded session can be restored, images and all', async ({ page }) => {
    test.setTimeout(120_000);

    // COLD START: an empty context has no stored session, so the offer must NOT
    // appear. A banner that false-fires on a first-ever visit would be worse than
    // no banner at all.
    await expect(page.getByText(/pick up where you left off/i)).toHaveCount(0);

    // Do real work: import two photos and wait for the collage to render.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });

    // Let the debounced autosave write the session to IndexedDB.
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS);

    // THE CRASH, simulated: the reload that used to lose everything.
    await page.reload();

    // THE OFFER. The banner appears, and its subtitle names the two images —
    // proof the metadata round-tripped, not just that a box rendered.
    const banner = page.getByText(/pick up where you left off/i);
    await expect(banner).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/2 images · saved/i)).toBeVisible();

    // The pool is genuinely empty right now (a fresh boot), so nothing on the
    // stage — restoring has to be what puts it back.
    await expect(page.locator('svg g')).toHaveCount(0);

    // RESTORE.
    await page.getByRole('button', { name: 'Restore', exact: true }).click();

    // The collage is back on the stage, and the banner is gone.
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 30_000 });
    await expect(page.locator('svg g')).not.toHaveCount(0);
    await expect(page.getByText(/pick up where you left off/i)).toHaveCount(0);
  });

  test('the restore banner is watertight on a phone', async ({ page }) => {
    test.setTimeout(120_000);

    // Seed a session once, then re-check the banner across the phone widths the
    // toolkit LAW names. This banner is used one-handed in a hallway; a card that
    // clips or forces a sideways scroll at 320px fails the ship gate.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS);

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.reload();
      await expect(page.getByText(/pick up where you left off/i)).toBeVisible({ timeout: 15_000 });

      // ZERO horizontal overflow — the whole page, not just the banner.
      const overflow = await page.evaluate(() => {
        const el = document.documentElement;
        return el.scrollWidth - el.clientWidth;
      });
      expect(overflow, `no horizontal overflow at ${width}px`).toBeLessThanOrEqual(0);

      // Both taps clear 44px, on both axes for the icon-only Dismiss. Rounded to
      // the nearest device pixel: the CSS commands 44px and sub-pixel layout can
      // report 43.99999, which is float noise, not a short target — while a real
      // shortfall (the scar was 37px) still rounds below 44 and fails.
      const restore = await page.getByRole('button', { name: 'Restore', exact: true }).boundingBox();
      const dismiss = await page.getByRole('button', { name: 'Dismiss saved session' }).boundingBox();
      expect(Math.round(restore!.height), `Restore ≥44px tall at ${width}px`).toBeGreaterThanOrEqual(44);
      expect(Math.round(dismiss!.height), `Dismiss ≥44px tall at ${width}px`).toBeGreaterThanOrEqual(44);
      expect(Math.round(dismiss!.width), `Dismiss ≥44px wide at ${width}px`).toBeGreaterThanOrEqual(44);
    }
  });

  // ---------------------------------------------------------------------------
  // THE SECOND WISH (collage well, bug, about_tool=project): "Restoring images is
  // slow and is glitching. Endless loop of restore, also does not restore
  // quickly." The three tests below are the three defects behind that sentence.
  // ---------------------------------------------------------------------------

  test('a settings change re-saves the manifest and NOT the image bytes', async ({ page }) => {
    test.setTimeout(120_000);

    // THE GLITCH. v1 stored the session as the whole `.collage` archive, so every
    // debounce re-fetched and re-zipped the entire pool — a title keystroke cost
    // the same as importing the photographs did. The store now keeps bytes one
    // row per asset, so the steady state is a small manifest row and NO image
    // writes at all. That is a count, so count it.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS);

    const first = await page.evaluate(() => (window as any).__idbPuts);
    expect(first.assets, 'both images persisted exactly once each').toBe(2);
    expect(first.project, 'the manifest row was written').toBeGreaterThanOrEqual(1);

    // AND THE THUMBNAIL TIER WENT WITH THEM. The app draws `previewSrc` — a
    // ≤1024px JPEG — everywhere, so a session that stored only the originals
    // came back with full-resolution previews and made the editor slower AFTER
    // recovering than before the crash. Both fixtures are wider than 1024px, so
    // both must have a genuinely smaller second blob on disk.
    const tiers = await page.evaluate(async () => {
      const db: IDBDatabase = await new Promise((res, rej) => {
        const r = indexedDB.open('collage-session');
        r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
      });
      const rows: { full: number; preview: number }[] = await new Promise((res) => {
        const tx = db.transaction('assets', 'readonly');
        const rq = tx.objectStore('assets').getAll();
        rq.onsuccess = () => res((rq.result || []).map((a: any) => ({ full: a?.full?.size ?? 0, preview: a?.preview?.size ?? 0 })));
        rq.onerror = () => res([]);
      });
      db.close();
      return rows;
    });
    expect(tiers.length, 'both assets are on disk').toBe(2);
    for (const t of tiers) {
      expect(t.preview, 'a thumbnail was stored beside the original').toBeGreaterThan(0);
      expect(t.preview, 'the thumbnail is genuinely smaller than the original').toBeLessThan(t.full);
    }

    // Change a setting the manifest carries and nothing else: the title. Then
    // wait out the debounce twice over.
    await page.evaluate(() => {
      const el = document.querySelector('input[placeholder*="TITLE" i], input[aria-label*="title" i]') as HTMLInputElement | null;
      if (el) {
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!;
        setter.call(el, 'FIELD TEST');
        el.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    // Belt and braces: a shuffle is a settings change too, and it needs no DOM
    // hunting — so the assertion holds even if the title field moves.
    await page.keyboard.press('Space').catch(() => { /* not fatal */ });
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS + 1200);

    const after = await page.evaluate(() => (window as any).__idbPuts);
    // THE ASSERTION THE BUG REPORT IS ABOUT: zero further image writes.
    expect(after.assets, 'a settings change writes NO image rows').toBe(first.assets);
    // ...and the autosave really did keep running (otherwise "no writes" would
    // just mean the feature broke, which is the trap this pairing closes).
    expect(after.project, 'the manifest was re-saved').toBeGreaterThan(first.project);
  });

  test('restore is quick, and never re-decodes the pool', async ({ page }) => {
    test.setTimeout(120_000);

    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS);

    await page.reload();
    await expect(page.getByText(/pick up where you left off/i)).toBeVisible({ timeout: 15_000 });

    // v1 unzipped the whole archive and then `new Image()`-decoded every
    // photograph IN SEQUENCE, purely to relearn the width and height the app had
    // already written down. The manifest carries them now, so restore is object
    // URLs and bookkeeping. The budget is deliberately loose — it is here to
    // catch a return to per-image decoding, not to police milliseconds.
    const t0 = Date.now();
    await page.getByRole('button', { name: 'Restore', exact: true }).click();
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 30_000 });
    const elapsed = Date.now() - t0;
    expect(elapsed, `restore landed in ${elapsed}ms`).toBeLessThan(6_000);

    // Restoring must not re-persist what it just read back out of the store.
    const puts = await page.evaluate(() => (window as any).__idbPuts);
    expect(puts.assets, 'a restore writes no image rows').toBe(0);
  });

  test('a session whose image will not decode cannot hang the restore', async ({ page }) => {
    test.setTimeout(120_000);

    // THE ENDLESS LOOP. `loadProject`'s archive branch awaited `imgElem.onload`
    // with no `onerror` and no timeout, so an asset the browser refuses to decode
    // — a blob truncated by a quota failure, a 4K frame on a phone already at its
    // memory line — never settled that promise. Tap Restore: the banner vanishes
    // and nothing else EVER happens. Reload, and the offer is right there again.
    // That is the loop the report describes, and it is why this test asserts an
    // OUTCOME rather than a picture: hanging forever is the only failure mode.
    await seedLegacySession(page, await legacyArchive(Buffer.from('this is definitely not a JPEG')));
    await page.reload();
    await expect(page.getByText(/pick up where you left off/i)).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: 'Restore', exact: true }).click();

    // Whatever it decides — take the asset it could not measure, or refuse the
    // session — it must DECIDE. The card leaving the screen is that decision
    // landing, so BOTH of its states have to be gone: while the restore runs the
    // heading reads "Bringing it back", and asserting only on the idle wording
    // would go green the instant the button was tapped. Which it did, the first
    // time this test was written — a test that cannot observe the hang is not a
    // test of the hang.
    await expect(page.getByText(/pick up where you left off|bringing it back/i))
      .toHaveCount(0, { timeout: 25_000 });

    // And the app is still alive, not wedged behind a promise that never settled:
    // a fresh import works.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });
  });

  test('a session written by the previous build still restores', async ({ page }) => {
    test.setTimeout(120_000);

    // The store changed shape under people who had unfinished work sitting in it.
    // Discarding those would be a strange way to ship a feature about not losing
    // work, so v1 rows are still read — through the original archive round-trip.
    await seedLegacySession(page, await legacyArchive(readFileSync(IMG_A)));
    await page.reload();
    await expect(page.getByText(/pick up where you left off/i)).toBeVisible({ timeout: 15_000 });
    await expect(page.locator('svg g')).toHaveCount(0);

    await page.getByRole('button', { name: 'Restore', exact: true }).click();
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/pick up where you left off/i)).toHaveCount(0);
  });

  test('dismissing the offer clears it for good', async ({ page }) => {
    test.setTimeout(120_000);

    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(AUTOSAVE_SETTLE_MS);

    await page.reload();
    await expect(page.getByText(/pick up where you left off/i)).toBeVisible({ timeout: 15_000 });

    // DISMISS — the user chooses to start fresh.
    await page.getByRole('button', { name: 'Dismiss saved session' }).click();
    await expect(page.getByText(/pick up where you left off/i)).toHaveCount(0);

    // And it stays dismissed: a further reload does not re-offer the discarded
    // session, because Dismiss cleared it from storage.
    await page.reload();
    await expect(page.getByText(/pick up where you left off/i)).toHaveCount(0, { timeout: 8_000 });
  });
});
