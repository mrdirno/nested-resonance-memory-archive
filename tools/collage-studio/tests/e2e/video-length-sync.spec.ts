/**
 * VIDEO-LENGTH SYNC — the artifact-level proof that the sync modes reach the
 * real <video> elements. The maths is swept in tests/unit/videoSync.invariants.mjs;
 * this drives the UI control and reads back HTMLVideoElement.playbackRate, so it
 * covers UI -> App/VideoStage -> Stage -> the actual media element.
 *
 *   npx playwright test --config playwright.source-count.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const CLIP = join(HERE, '..', 'fixtures', 'motion.webm');            // ~4.0s
const CLIP_SHORT = join(HERE, '..', 'fixtures', 'motion_short.webm'); // ~1.6s

const rates = (page: Page) =>
  page.evaluate(() => [...document.querySelectorAll('video')].map((v) => (v as HTMLVideoElement).playbackRate));
const videoCount = (page: Page) => page.evaluate(() => document.querySelectorAll('video').length);

test.describe('video-length sync', () => {
  test.beforeEach(async ({ page }) => { await page.goto(APP_URL); });

  test('two clips of different length take synced playbackRates per mode', async ({ page }) => {
    // A 4.0s clip and a 1.6s clip: one source each -> two fragments -> both play.
    await page.locator('input[type="file"]').first().setInputFiles([CLIP, CLIP_SHORT]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
    await expect.poll(() => videoCount(page), { timeout: 90_000 }).toBe(2);

    // DEFAULT — LOOP: every clip at its own natural speed.
    await expect.poll(async () => (await rates(page)).every((r) => Math.abs(r - 1) < 0.02), { timeout: 20_000 }).toBe(true);

    // STRETCH to longest: the 1.6s clip slows to ~0.41x, the 4.0s clip stays 1x.
    await page.getByRole('button', { name: 'Stretch clips to the longest' }).click();
    await expect.poll(async () => {
      const r = (await rates(page)).sort((a, b) => a - b);
      return r.length === 2 && r[0] < 0.6 && Math.abs(r[1] - 1) < 0.03;
    }, { timeout: 20_000 }).toBe(true);

    // SPEED to shortest: the 4.0s clip speeds to ~2.44x, the 1.6s clip stays 1x.
    await page.getByRole('button', { name: 'Speed clips to the shortest' }).click();
    await expect.poll(async () => {
      const r = (await rates(page)).sort((a, b) => a - b);
      return r.length === 2 && Math.abs(r[0] - 1) < 0.03 && r[1] > 1.8;
    }, { timeout: 20_000 }).toBe(true);

    // Back to LOOP resets both to natural speed.
    await page.getByRole('button', { name: 'Loop clips at natural speed' }).click();
    await expect.poll(async () => (await rates(page)).every((r) => Math.abs(r - 1) < 0.02), { timeout: 20_000 }).toBe(true);
  });
});
