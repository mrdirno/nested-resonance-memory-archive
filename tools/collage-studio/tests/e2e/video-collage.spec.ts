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

/**
 * Where to point the run. Defaults to the dev server via `baseURL`; set it to a
 * deployed URL to re-run the SAME proof against a real release —
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/
 * A green dev run only proves the source is right; this proves the artifact
 * that actually shipped is.
 */
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
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

/**
 * Drive the import sheet the way a user actually does: ONE tap on ADD VIDEO.
 * `viaFramePicker` walks the curate path instead, so both routes stay covered.
 */
const enableFramePicker = async (page: Page) => {
  await page.evaluate(() => localStorage.setItem('genart.framePicker', '1'));
  await page.reload();
};

const importClip = async (page: Page, opts: { frames?: number; viaFramePicker?: boolean } = {}) => {
  const frames = opts.frames ?? 6;
  if (opts.viaFramePicker) await enableFramePicker(page);
  await page.locator('input[type="file"]').first().setInputFiles(CLIP);

  const addVideo = page.getByRole('button', { name: 'ADD VIDEO' });
  await expect(addVideo).toBeVisible({ timeout: 20_000 });

  // Fewer frames than the default keeps the run quick; the count input is a range.
  const count = page.getByLabel('Number of frames to extract');
  if (await count.count()) await count.fill(String(frames));

  // Wait on the SHEET, not on a button. Every footer button is swapped out the
  // moment extraction starts, so `addVideo` goes hidden while the work is still
  // running — waiting on that raced the extraction and looked like a product bug.
  const sheet = page.getByRole('dialog', { name: 'Import video frames' });

  if (!opts.viaFramePicker) {
    await addVideo.click();
    await expect(sheet).toBeHidden({ timeout: 120_000 });
    return;
  }

  await page.getByRole('button', { name: 'PICK FRAMES' }).click();
  const add = page.getByRole('button', { name: /ADD \d+ FRAMES?/ });
  await expect(add).toBeVisible({ timeout: 60_000 });
  await add.click();
  await expect(sheet).toBeHidden({ timeout: 60_000 });
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
    // Surface page-side failures in the test output. An exception inside a React
    // handler otherwise shows up only as "the element never appeared", which
    // costs a debugging round-trip every single time.
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    page.on('console', (m) => {
      if (m.type() === 'error' || m.type() === 'warning') console.log(`[${m.type()}]`, m.text());
    });

    // The blazeface CDN is optional (the app degrades to aiState 'failed'), but
    // waiting on it makes the run slow and flaky. Let it fail fast.
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    // A released build ships a cache-first service worker; without this the run
    // can silently exercise a PREVIOUS release that the SW still holds.
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
      if (typeof caches !== 'undefined') {
        for (const k of await caches.keys()) await caches.delete(k);
      }
    }).catch(() => { /* no SW support in this context is fine */ });
  });

  test('the sheet is video-only until the picker is switched on in settings', async ({ page }) => {
    test.setTimeout(90_000);
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);

    // The old sheet's ONLY action was "EXTRACT N FRAMES", which is why live
    // playback looked like it did not exist. Video is the sole way forward now.
    await expect(page.getByRole('button', { name: 'ADD VIDEO' })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('button', { name: /EXTRACT \d+ FRAMES?/ })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'PICK FRAMES' })).toHaveCount(0);
    await expect(page.getByText(/keep playing/i)).toBeVisible();

    // ...and the setting genuinely brings it back.
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'Settings' }).click();
    const toggle = page.getByRole('switch', { name: /Choose frames on import/i });
    await expect(toggle).toHaveAttribute('aria-checked', 'false');
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-checked', 'true');

    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.getByRole('button', { name: 'PICK FRAMES' })).toBeVisible({ timeout: 20_000 });
  });

  test('the frame-picker route still works when enabled', async ({ page }) => {
    test.setTimeout(120_000);
    await importClip(page, { viaFramePicker: true });
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('button', { name: /Stop playing motion\.webm/ })).toBeVisible();
  });

  test('no chrome sits on top of the collage', async ({ page }) => {
    test.setTimeout(120_000);
    await importClip(page);

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    const art = await canvas.boundingBox();
    expect(art).not.toBeNull();

    // Every persistent control must live OUTSIDE the artwork's box. This is the
    // whole complaint: a bar floating over the collage covers the one thing the
    // screen exists to show.
    for (const name of ['Record video', 'Play clips', 'Pause clips', /Stop playing motion\.webm/] as const) {
      const el = page.getByRole('button', { name: name as never });
      if (!(await el.count())) continue;
      const box = await el.first().boundingBox();
      if (!box || !art) continue;
      const overlaps =
        box.x < art.x + art.width && box.x + box.width > art.x &&
        box.y < art.y + art.height && box.y + box.height > art.y;
      expect(overlaps, `${String(name)} overlaps the collage`).toBe(false);
    }
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

  test('each clip has its own sound toggle, muted by default', async ({ page }) => {
    test.setTimeout(120_000);
    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    // A collage that shouts the moment you drop a clip in is not a nice thing
    // to build, so every clip starts silent and says so.
    const unmute = page.getByRole('button', { name: /Unmute motion\.webm/ });
    await expect(unmute).toBeVisible();
    await expect(unmute).toHaveAttribute('aria-pressed', 'false');

    await unmute.click();
    const mute = page.getByRole('button', { name: /Mute motion\.webm/ });
    await expect(mute).toBeVisible();
    await expect(mute).toHaveAttribute('aria-pressed', 'true');

    // And it is really audible, not just relabelled.
    expect(await page.evaluate(() => {
      const v = Array.from(document.querySelectorAll('video'))
        .find((e) => e.src.startsWith('blob:'));
      return v ? !v.muted && v.volume > 0 : false;
    })).toBe(true);

    await mute.click();
    await expect(page.getByRole('button', { name: /Unmute motion\.webm/ })).toHaveAttribute('aria-pressed', 'false');
  });

  test('video is offered in the export sheet and saves a file', async ({ page }) => {
    test.setTimeout(180_000);
    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    await page.getByRole('button', { name: 'Export', exact: true }).click();

    // Scope to the sheet: the dock transport carries its own identical length
    // buttons, so an unscoped '5s' matches two and clicks the obscured one.
    const sheet = page.getByRole('dialog').filter({ hasText: 'Record the moving collage' });
    await expect(sheet).toBeVisible({ timeout: 15_000 });
    await sheet.getByRole('button', { name: '5s', exact: true }).click();
    await sheet.getByRole('button', { name: /Record 5s video/i }).click();

    const preview = page.locator('video[controls]');
    await expect(preview).toBeVisible({ timeout: 90_000 });

    // "Save" must actually hand a file over, not just look like a button.
    const save = page.getByRole('button', { name: 'Save' });
    await expect(save).toBeVisible();
    const dl = page.waitForEvent('download', { timeout: 30_000 });
    await save.click();
    const file = await dl;
    expect(file.suggestedFilename()).toMatch(/^collage-.*\.(mp4|webm)$/);
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
    const preview = page.locator('video[controls]');
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
