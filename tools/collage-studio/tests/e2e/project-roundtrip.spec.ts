// tests/e2e/project-roundtrip.spec.ts
// -----------------------------------------------------------------------------
// SAVE, REOPEN, AND KEEP WORKING.
//
// The freeze this file exists for is invisible in every other kind of test. The
// build passes (vite/esbuild strips types without checking them), the app boots,
// the project loads, images appear — and then selecting Stencil hangs the canvas
// forever with nothing logged and no error anywhere.
//
// MECHANISM: `loadProject` pushed assets with NO `previewSrc` (tsc had been
// reporting exactly that at project.ts:87, unread). `stencil.ts` then does
// `img.src = imgAsset.previewSrc` -> "undefined" -> <base>/undefined -> 404, and
// awaited a promise wired ONLY to `onload`. No onload, no rejection, no timeout:
// `computeStencilLayout` never returns, `setLayoutItems` is never called, and
// `isLayoutComputing` stays true for the rest of the session.
//
// So the assertion is on the SPINNER CLEARING, not on pixels: a stale layout
// still renders its old fragments, which is why "the canvas has content" would
// pass straight through this bug.
// -----------------------------------------------------------------------------

import { test, expect } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

test.describe('project round-trip', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    }).catch(() => { /* fine */ });
  });

  test('a reopened project can still switch layout mode', async ({ page }) => {
    test.setTimeout(180_000);

    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });

    // Save -> a .collage archive lands on disk. Ctrl+S is the documented
    // shortcut (Header.tsx:37) and avoids depending on the Export sheet's
    // layout, which is not what this test is about.
    const dl = page.waitForEvent('download', { timeout: 60_000 });
    await page.keyboard.press('Control+s');
    const saved = await (await dl).path();
    expect(saved, 'the project archive must actually be written').toBeTruthy();

    // A FRESH session — the bug lives only on the LOAD path, so reusing the
    // in-memory pool would hide it completely.
    await page.reload();

    const chooser = page.waitForEvent('filechooser', { timeout: 30_000 });
    // EXACT: the composition-code strip (SimpleControls) also has an "Open",
    // and a substring match now finds both. This one is the Header's, which
    // opens a saved project.
    await page.getByRole('button', { name: 'Open', exact: true }).click();
    await (await chooser).setFiles(saved!);

    await expect(page.locator('svg g').first()).toBeVisible({ timeout: 60_000 });

    // The reload must really have re-hydrated from the archive, or everything
    // below grades an empty pool.
    // The reload must really have re-hydrated from the archive, or everything
    // below grades an empty pool.
    await expect(page.locator('svg g')).not.toHaveCount(0);

    // Stencil lives in the Settings tab.
    await page.getByRole('button', { name: 'Settings' }).click();
    const stencil = page.getByRole('button', { name: /Stencil/i }).first();
    await expect(stencil).toBeVisible({ timeout: 10_000 });
    await stencil.click();
    // Prove the MODE actually changed — a click that misses would make the
    // spinner assertion below vacuously true.
    await expect(page.getByText(/cut from the light and dark/i)).toBeVisible({ timeout: 5_000 });

    // THE ASSERTION. `isLayoutComputing` drives the only spinner on screen once
    // the import has drained; if computeStencilLayout never resolves it spins
    // forever. Content-based checks pass regardless, because the PREVIOUS
    // layout's fragments are still on the canvas.
    await expect(page.locator('.animate-spin')).toHaveCount(0, { timeout: 8_000 });
  });
});
