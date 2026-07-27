// tests/e2e/video-collage.spec.ts
// -----------------------------------------------------------------------------
// THE VIDEO COLLAGE ACTUALLY MOVES.
//
// This file exists because "the build passed" and "the canvas mounted" are not
// evidence that a video collage plays. The failure modes this feature has are
// all SILENT — an over-cap <video> is paused by the system with no error, iOS
// Low Power Mode blocks muted autoplay without rejecting the promise, a canvas
// nobody paints emits zero frames and records a valid empty file, and a
// `drawImage` of a stalled element returns the same frame forever. Every one of
// those leaves the DOM looking exactly like success.
//
// So the assertion is on PIXELS OVER TIME, sampled from the live canvas itself:
// hash the whole composition, wait, hash it again, and require that it changed.
// Nothing short of real decoded frames reaching the canvas can pass that.
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
/** VP9 + Opus: the one codec pair every Chromium build decodes, so a red test
 *  means the feature broke, never that the fixture was unplayable. */
const CLIP = join(HERE, '..', 'fixtures', 'motion.webm');

/**
 * A hash of the WHOLE live composition, downsampled to 32x32 so it is cheap and
 * so a one-pixel dither cannot masquerade as motion. Reads through a scratch
 * canvas because the Stage canvas carries a transform and a device-pixel
 * backing store whose size we do not want to assume.
 */
const sampleCanvas = (page: Page): Promise<number> =>
  page.evaluate(() => {
    const src = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!src || !src.width || !src.height) return -1;
    const t = document.createElement('canvas');
    t.width = 32; t.height = 32;
    const tc = t.getContext('2d');
    if (!tc) return -1;
    tc.drawImage(src, 0, 0, 32, 32);
    const d = tc.getImageData(0, 0, 32, 32).data;
    let h = 2166136261;
    for (let i = 0; i < d.length; i += 4) {
      h = (Math.imul(h ^ d[i], 16777619) + Math.imul(d[i + 1], 31) + d[i + 2]) >>> 0;
    }
    return h;
  });

/** Drive the import sheet all the way to frames-in-the-pool. */
const importClip = async (page: Page, frames = 6) => {
  await page.locator('input[type="file"]').first().setInputFiles(CLIP);

  const extract = page.getByRole('button', { name: /EXTRACT \d+ FRAMES?/ });
  await expect(extract).toBeVisible({ timeout: 20_000 });

  // Fewer frames than the default keeps the run quick; the count input is a range.
  const count = page.getByLabel('Number of frames to extract');
  if (await count.count()) await count.fill(String(frames));

  await page.getByRole('button', { name: /EXTRACT \d+ FRAMES?/ }).click();

  const add = page.getByRole('button', { name: /ADD \d+ FRAMES?/ });
  await expect(add).toBeVisible({ timeout: 60_000 });
  await add.click();
  await expect(add).toBeHidden({ timeout: 30_000 });
};

/** Autoplay is allowed to be refused; the gesture path is the supported answer. */
const startPlaybackIfGated = async (page: Page) => {
  const tap = page.getByRole('button', { name: 'Tap to play' });
  if (await tap.isVisible().catch(() => false)) await tap.click();
};

// The FULL Chromium build, not the default headless shell: the shell ships
// without the media stack, so `MediaRecorder`, `canvas.captureStream()` and VP9
// decode are all absent there. Testing this feature on it would prove nothing
// except that the shell cannot do video. Must be file-level — Playwright refuses
// `channel` inside a describe because it forces a new worker.
test.use({ channel: 'chromium' });

test.describe('video collage', () => {
  test.beforeEach(async ({ page }) => {
    // The blazeface CDN is optional (the app degrades to aiState 'failed'), but
    // waiting on it makes the run slow and flaky. Let it fail fast.
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto('/');
  });

  test('a clip keeps moving inside the collage', async ({ page }) => {
    test.setTimeout(120_000);

    await importClip(page);

    // The live compositor replaces the still <img>, and the clip is listed.
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('button', { name: /Stop playing motion\.webm/ })).toBeVisible();

    await startPlaybackIfGated(page);

    // THE PROOF. Two samples, far enough apart that a 25fps source must have
    // advanced several frames between them.
    const first = await sampleCanvas(page);
    expect(first, 'the live canvas should be readable').not.toBe(-1);

    let moved = false;
    for (let i = 0; i < 12 && !moved; i++) {
      await page.waitForTimeout(250);
      const next = await sampleCanvas(page);
      if (next !== -1 && next !== first) moved = true;
    }
    expect(moved, 'the composition must change over time — a video collage that never repaints is a still').toBe(true);
  });

  test('pausing actually stops the pixels', async ({ page }) => {
    test.setTimeout(120_000);

    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    // Wait until it is demonstrably moving before claiming a pause means anything.
    let a = await sampleCanvas(page);
    let moving = false;
    for (let i = 0; i < 12 && !moving; i++) {
      await page.waitForTimeout(250);
      const b = await sampleCanvas(page);
      if (b !== -1 && b !== a) { moving = true; a = b; }
    }
    expect(moving, 'precondition: it must be playing before a pause can be tested').toBe(true);

    await page.getByRole('button', { name: 'Pause clips' }).click();
    // One settle tick: the frame in flight when pause landed is still allowed.
    await page.waitForTimeout(400);

    const held = await sampleCanvas(page);
    await page.waitForTimeout(700);
    expect(await sampleCanvas(page), 'a paused collage must hold its frame').toBe(held);
  });

  test('dropping a clip keeps its frames and stops its playback', async ({ page }) => {
    test.setTimeout(120_000);

    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });

    await page.getByRole('button', { name: /Stop playing motion\.webm/ }).click();

    // The live path is gone...
    await expect(page.locator('canvas')).toBeHidden({ timeout: 20_000 });
    // ...and the extracted stills are still the collage, so the still preview returns.
    await expect(page.locator('img[src^="blob:"]')).toBeVisible({ timeout: 20_000 });
  });

  test('records the moving collage to a playable file', async ({ page }) => {
    test.setTimeout(180_000);

    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    // Shortest offered take, so the assertion is about correctness not patience.
    await page.getByRole('button', { name: '5s', exact: true }).click();
    await page.getByRole('button', { name: 'Record video' }).click();

    // The result sheet only renders on a take that came back ok:true — which
    // `record()` only returns after it has decoded the file back.
    const preview = page.locator('video[src^="blob:"]');
    await expect(preview).toBeVisible({ timeout: 90_000 });

    // And the element must actually be able to play it: real dimensions, and a
    // currentTime that advances. A valid-looking blob that decodes to nothing
    // would pass a mere visibility check.
    const verdict = await preview.evaluate(async (el: HTMLVideoElement) => {
      if (el.readyState < 1) {
        await new Promise<void>((res) => {
          el.addEventListener('loadedmetadata', () => res(), { once: true });
          setTimeout(res, 8000);
        });
      }
      const t0 = el.currentTime;
      await el.play().catch(() => { /* controls are present; autoplay may be refused */ });
      await new Promise((r) => setTimeout(r, 900));
      return { w: el.videoWidth, h: el.videoHeight, advanced: el.currentTime > t0 };
    });

    expect(verdict.w, 'the recording must have a real video track').toBeGreaterThan(0);
    expect(verdict.h).toBeGreaterThan(0);
    expect(verdict.advanced, 'the recorded file must actually play').toBe(true);

    await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
  });
});
