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
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

// > AUTOSAVE_DEBOUNCE_MS (1500) plus room to zip the pool and commit the IDB
// write. The debounced snapshot must have landed before the reload, or there is
// nothing to restore and the assertion would (correctly) fail.
const AUTOSAVE_SETTLE_MS = 2800;

test.describe('crash-safe session recovery', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
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
