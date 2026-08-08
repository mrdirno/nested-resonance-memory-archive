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
 * There is ONE import route, because there is only one thing importing a video
 * can mean. The `viaFramePicker` variant of this helper is gone with the route.
 */
const importClip = async (page: Page) => {
  await page.locator('input[type="file"]').first().setInputFiles(CLIP);
  // NO SHEET. Loading a video means "put this in the collage"; every question
  // the sheet used to ask has a defensible default, and asking turned a one
  // gesture action into a three tap errand.
  await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
};

/** Autoplay is allowed to be refused; the gesture path is the supported answer. */
const startPlaybackIfGated = async (page: Page) => {
  const tap = page.getByRole('button', { name: 'Tap to play' });
  if (await tap.isVisible().catch(() => false)) await tap.click();
};

// NOTE: the Chromium `channel` lives in playwright.config.ts, per project. It
// used to be set file-wide here, which handed it to the WebKit projects as well
// and made them fail to LAUNCH — see the comment above `projects` in the config.

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

  test('a dropped video goes straight into the collage, with no sheet', async ({ page }) => {
    test.setTimeout(120_000);
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);

    // Not one prompt, not one extra tap: the clip lands and plays.
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
    await expect(page.getByRole('dialog', { name: 'Import video frames' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: /Stop playing motion\.webm/ })).toBeVisible();

    // ...and the frames it needed are really in the pool, just not asked about.
    // The chip reads "Mute" because the clip's sound is already part of the
    // piece — importing a video is a statement that you want the video.
    await expect(page.getByRole('button', { name: /Mute motion\.webm/ })).toBeVisible();
  });

  /**
   * THE ASK IS GONE, AND IT STAYS GONE.
   *
   * These two used to assert the opposite: that the frame picker was merely
   * OFF BY DEFAULT and that its route "still works when enabled". That is the
   * shape of the bug the owner reported three times — default-off is still an
   * ask, because the switch sits in Settings offering to start asking. Both
   * tests are now the negative, and they fail the moment anything re-introduces
   * a way to be asked how many frames to pull.
   */
  test('nothing anywhere asks how many frames to pull', async ({ page }) => {
    test.setTimeout(120_000);

    // A stale preference from a visit BEFORE the route was deleted must not
    // resurrect it. This is exactly how a returning user stays stuck on
    // behaviour that has already been removed for everyone else.
    await page.evaluate(() => localStorage.setItem('genart.framePicker', '1'));
    await page.reload();
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });

    await expect(page.getByRole('dialog', { name: /frame/i })).toHaveCount(0);
    await expect(page.getByLabel(/number of frames/i)).toHaveCount(0);
    await expect(page.getByRole('button', { name: /PICK FRAMES/i })).toHaveCount(0);
    await expect(page.getByRole('button', { name: /ADD \d+ FRAMES?/i })).toHaveCount(0);
    await expect(page.getByRole('button', { name: /Stop playing motion\.webm/ })).toBeVisible();
  });

  test('no control offers to extract frames, in the settings or on the canvas', async ({ page }) => {
    test.setTimeout(90_000);
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });

    // The button that takes a video used to be LABELLED "Extract frames from a
    // video" — a live surface still asking, long after the default path had
    // stopped. Accessible names are the thing under test, not the icon.
    await expect(page.getByRole('button', { name: /extract frames/i })).toHaveCount(0);
    await expect(page.getByRole('button', { name: /Add a video/i })).toBeVisible();

    await page.getByRole('button', { name: 'Settings' }).click();
    await expect(page.getByRole('switch', { name: /frames/i })).toHaveCount(0);

    // Belt and braces: no control ANYWHERE names frames as something to pick.
    const asks = await page.evaluate(() => {
      const bad = /(choose|pick|extract|how many|number of).{0,24}frames?/i;
      return Array.from(document.querySelectorAll('button,[role=switch],label,input,a'))
        .map(e => `${e.getAttribute('aria-label') || ''} ${e.getAttribute('title') || ''} ${e.textContent || ''}`)
        .filter(t => bad.test(t))
        .map(t => t.replace(/\s+/g, ' ').trim().slice(0, 90));
    });
    expect(asks, `controls still asking about frames: ${JSON.stringify(asks)}`).toEqual([]);
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

  /**
   * TWO DIFFERENT QUESTIONS, AND THIS TEST USED TO CONFLATE THEM.
   *
   * "A collage that shouts the moment you drop a clip in is not a nice thing to
   * build" is TRUE, and it is about the SPEAKERS. It got implemented as "the
   * clip's sound is not part of the piece", which is a statement about the
   * FILE — and that is how exports came out silent: the export read the same
   * flag, so a person who never hunted down the speaker chip got an MP4 with no
   * audio track and nothing on screen said so.
   *
   * Both properties are asserted here now, separately, because they must both
   * hold: the sound is IN the piece from the moment of import, and the room
   * stays quiet until you ask to hear it.
   */
  test('a clip’s sound is in the piece on import, while the room stays quiet', async ({ page }) => {
    test.setTimeout(120_000);
    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    // INTENT: selected, and the chip says so.
    const mute = page.getByRole('button', { name: /Mute motion\.webm/ });
    await expect(mute).toBeVisible();
    await expect(mute).toHaveAttribute('aria-pressed', 'true');

    // THE ROOM: still silent. The monitor starts off, so the element stays
    // muted — which is also what keeps it autoplay-eligible.
    await expect(page.getByRole('button', { name: 'Unmute preview' })).toBeVisible();
    expect(
      await page.evaluate(() => {
        const v = Array.from(document.querySelectorAll('video'))
          .find((e) => e.src.startsWith('blob:'));
        return v ? v.muted : null;
      }),
      'importing a clip must not make noise',
    ).toBe(true);

    // Turning the monitor on makes that same clip really audible, not just
    // relabelled.
    await page.getByRole('button', { name: 'Unmute preview' }).click();
    await expect(page.getByRole('button', { name: 'Mute preview' })).toBeVisible({ timeout: 10_000 });
    expect(await page.evaluate(() => {
      const v = Array.from(document.querySelectorAll('video'))
        .find((e) => e.src.startsWith('blob:'));
      return v ? !v.muted && v.volume > 0 : false;
    })).toBe(true);

    // And the per-clip switch still works in both directions.
    await mute.click();
    const unmute = page.getByRole('button', { name: /Unmute motion\.webm/ });
    await expect(unmute).toHaveAttribute('aria-pressed', 'false');
    await unmute.click();
    await expect(page.getByRole('button', { name: /Mute motion\.webm/ }))
      .toHaveAttribute('aria-pressed', 'true');
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

    // WHICH BUTTON IS THE DOWNLOAD depends on whether the device can share the
    // FILE, and that answer changed when the export became a render: the
    // renderer emits MP4, `canShare` accepts MP4 where it refused the old WebM
    // take, so the sheet now correctly leads with share-to-Photos and the plain
    // download moved to its own button. Resolve it rather than assume — and note
    // `getByRole({name})` is a SUBSTRING match, so a bare 'Save' silently
    // matches 'Save video' and fires the share sheet, which downloads nothing.
    const shareLed = await page.getByRole('button', { name: 'Save video', exact: true }).count();
    const save = shareLed
      ? page.getByRole('button', { name: 'Download', exact: true })
      : page.getByRole('button', { name: 'Save', exact: true });
    await expect(save).toBeVisible();
    const dl = page.waitForEvent('download', { timeout: 30_000 });
    await save.click();
    const file = await dl;
    expect(file.suggestedFilename()).toMatch(/^collage-.*\.(mp4|webm)$/);
  });

  test('still records when the browser cannot capture a canvas (the iOS path)', async ({ page }) => {
    test.setTimeout(180_000);

    // Reproduce the failure this fallback exists for: iOS Safari is the platform
    // where canvas capture is unsupported at every version, so remove it and
    // MediaRecorder entirely and require a file to come back anyway.
    await page.addInitScript(() => {
      delete (HTMLCanvasElement.prototype as unknown as Record<string, unknown>).captureStream;
      delete (window as unknown as Record<string, unknown>).MediaRecorder;
      // Sharing off, so this test is about the ENCODER and lands deterministically
      // on the plain download button. The share route has its own test.
      Object.defineProperty(navigator, 'canShare', { value: undefined, configurable: true });
      Object.defineProperty(navigator, 'share', { value: undefined, configurable: true });
    });
    await page.reload();

    expect(await page.evaluate(() =>
      typeof (HTMLCanvasElement.prototype as unknown as Record<string, unknown>).captureStream)).toBe('undefined');

    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    await page.getByRole('button', { name: '5s', exact: true }).click();
    await page.getByRole('button', { name: 'Record video' }).click();

    const preview = page.locator('video[controls]');
    await expect(preview).toBeVisible({ timeout: 120_000 });

    // MP4, and it really decodes — the whole point is a file Photos will take.
    const verdict = await preview.evaluate(async (el: HTMLVideoElement) => {
      if (el.readyState < 1) {
        await new Promise<void>((res) => {
          el.addEventListener('loadedmetadata', () => res(), { once: true });
          setTimeout(res, 8000);
        });
      }
      const t0 = el.currentTime;
      await el.play().catch(() => { /* controls are present */ });
      await new Promise((r) => setTimeout(r, 900));
      return { w: el.videoWidth, h: el.videoHeight, advanced: el.currentTime > t0, dur: el.duration };
    });
    expect(verdict.w).toBeGreaterThan(0);
    expect(verdict.advanced, 'the WebCodecs file must actually play').toBe(true);
    // Unlike the MediaRecorder path this one writes a real duration.
    expect(Number.isFinite(verdict.dur) && verdict.dur > 0).toBe(true);

    const dl = page.waitForEvent('download', { timeout: 30_000 });
    await page.getByRole('button', { name: 'Save' }).click();
    expect((await dl).suggestedFilename()).toMatch(/\.mp4$/);
  });

  test('an iPhone-shaped device gets a share-to-Photos save, and the file is MP4', async ({ page }) => {
    test.setTimeout(180_000);

    // Reproduce an iPhone as far as the export path can see one: no canvas
    // capture, no MediaRecorder, and a share sheet that accepts files. The
    // `download` attribute is ignored for blob: URLs on iOS Safari, so a Save
    // button that only downloads is a button that silently does nothing there.
    await page.addInitScript(() => {
      delete (HTMLCanvasElement.prototype as unknown as Record<string, unknown>).captureStream;
      delete (window as unknown as Record<string, unknown>).MediaRecorder;
      const shared: { type: string; name: string }[] = [];
      (window as unknown as Record<string, unknown>).__shared = shared;
      (navigator as unknown as Record<string, unknown>).canShare = (d: { files?: File[] }) => !!d?.files?.length;
      (navigator as unknown as Record<string, unknown>).share = async (d: { files?: File[] }) => {
        for (const f of d.files ?? []) shared.push({ type: f.type, name: f.name });
      };
    });
    await page.reload();

    await importClip(page);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 20_000 });
    await startPlaybackIfGated(page);

    await page.getByRole('button', { name: '5s', exact: true }).click();
    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('video[controls]')).toBeVisible({ timeout: 120_000 });

    // Share leads; download is still there, just not the headline.
    const save = page.getByRole('button', { name: 'Save video' });
    await expect(save).toBeVisible();
    await expect(page.getByRole('button', { name: 'Download' })).toBeVisible();

    await save.click();
    const shared = await page.evaluate(() => (window as unknown as { __shared: { type: string; name: string }[] }).__shared);
    expect(shared.length, 'the share sheet must actually receive the file').toBe(1);
    // MP4/H.264 is what iOS will accept into Photos. WebM would be refused.
    expect(shared[0].type).toBe('video/mp4');
    expect(shared[0].name).toMatch(/\.mp4$/);
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

// -----------------------------------------------------------------------------
// A PHONE, AND MORE THAN ONE CLIP.
//
// Everything above imports ONE 480x360 clip. That fixture is 172,800 source
// pixels, so it fits inside any decode budget this app has ever carried — which
// is precisely why the bug below shipped and survived a green suite: the
// admission pass was never asked to seat a second clip, and never asked to seat
// a BIG one.
//
// The UA override is what makes this a phone. `detectStageCaps` branches on
// /iPad|iPhone|iPod/ in the user agent, so overriding it selects the mobile
// budget on whichever engine is running, while keeping Chromium's VP9 decode.
// -----------------------------------------------------------------------------

/** 1080p on purpose: 1920x1080 = 2,073,600 pixels EACH. */
const HD_A = join(HERE, '..', 'fixtures', 'hd_a.webm');
const HD_B = join(HERE, '..', 'fixtures', 'hd_b.webm');

/** FIVE small clips — more than any mobile decoder budget, so the realtime
 *  preview must defer some while the offline render must seat them all. */
const TONES = ['tone_a', 'tone_b', 'tone_c', 'tone_d', 'tone_e']
  .map((n) => join(HERE, '..', 'fixtures', `${n}.webm`));

const IPHONE_UA =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
  + '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';

test.describe('more than one clip, on a phone', () => {
  test.use({ userAgent: IPHONE_UA, viewport: { width: 390, height: 844 } });

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
      if (typeof caches !== 'undefined') {
        for (const k of await caches.keys()) await caches.delete(k);
      }
    }).catch(() => { /* no SW in this context is fine */ });
  });

  /**
   * THE REGRESSION.
   *
   * `maxLivePixels` was a flat 2_500_000 on mobile while `maxLiveClips` said 3.
   * Clip #1 is admitted free (refreshAdmission lets the first one in regardless
   * of the pixel sum); clip #2 pushes the total to 4,147,200 and is deferred as
   * `over-pixel-cap`. Every phone, every time, forever: exactly ONE video ever
   * played. The cap is now denominated in 1080p streams, so N clips means N.
   *
   * Asserted on the DECODERS, not on the dock: a chip renders for a deferred
   * clip too — it just shows a still — so counting chips would pass while the
   * bug was live.
   */
  test('two HD clips BOTH play — the pixel budget does not pin it at one', async ({ page }) => {
    test.setTimeout(240_000);

    await page.locator('input[type="file"]').first().setInputFiles([HD_A, HD_B]);

    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing hd_a\.webm/ }))
      .toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing hd_b\.webm/ }))
      .toBeVisible({ timeout: 200_000 });

    await startPlaybackIfGated(page);

    // An evicted clip has had its src REMOVED (stage.evict), so `currentSrc` is
    // the honest test of "this one still owns a decoder".
    await expect.poll(async () => page.evaluate(() =>
      Array.from(document.querySelectorAll('video'))
        .filter((v) => v.currentSrc && v.readyState >= 2 && !v.ended).length,
    ), {
      message: 'both clips must hold a live decoder',
      timeout: 60_000,
    }).toBe(2);

    // And the stage must not be telling the user it gave up on one of them.
    await expect(page.getByText(/of 2 clips playing/)).toHaveCount(0);
  });

  /**
   * THE IMPORT IS NOT A WALL.
   *
   * A `fixed inset-0` scrim used to sit over everything from the first file
   * until the last one decoded. On a phone, after Photos has already spent a
   * while handing the files over, that is indistinguishable from a hang — and
   * it covered the collage that was busy filling in behind it.
   */
  test('the import never covers the collage', async ({ page }) => {
    test.setTimeout(240_000);

    await page.locator('input[type="file"]').first().setInputFiles([HD_A, HD_B]);

    /** Anything viewport-sized under the middle of the screen that is not the art. */
    const scrimUnderCentre = () => page.evaluate(() => {
      const el = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
      if (!el) return '';
      const r = el.getBoundingClientRect();
      const coversViewport =
        r.width >= window.innerWidth * 0.98 && r.height >= window.innerHeight * 0.98;
      if (!coversViewport) return '';
      const tag = el.tagName.toLowerCase();
      if (tag === 'canvas' || tag === 'svg' || tag === 'g' || tag === 'path') return '';
      return `${tag}.${String((el as HTMLElement).className || '')}`;
    });

    // Sample repeatedly across the whole import rather than once: the old scrim
    // was only up WHILE work was in flight, which is exactly when nobody looked.
    const deadline = Date.now() + 120_000;
    let sampled = 0;
    while (Date.now() < deadline) {
      const blocking = await scrimUnderCentre();
      expect(blocking, 'a full-screen overlay covered the collage during import').toBe('');
      sampled++;
      if (await page.getByRole('button', { name: /Stop playing hd_b\.webm/ }).count()) break;
      await page.waitForTimeout(150);
    }
    expect(sampled, 'the import finished before anything could be sampled').toBeGreaterThan(3);
  });

  /**
   * THE EXPORT IS NOT CAPPED LIKE THE PREVIEW.
   *
   * The realtime decoder budget (mobile: 3) exists so LIVE compositing keeps up
   * with a clock. It has no business in the FILE: an offline render seeks one
   * frame at a time with no clock, so a clip it defers exports as a FROZEN STILL
   * while its sound is mixed in regardless — audio over a picture that never
   * moves. The complaint was exactly that ("stop pulling single frames … output
   * the full videos"). This imports FIVE clips onto a 3-clip phone, proves the
   * preview really is capped, then proves the render seats every one.
   *
   * Asserted on the DECODERS (`<video>` with a blob src), not on the dock: a
   * chip renders for a deferred clip too, so counting chips would pass while the
   * bug was live. A live clip has `stage.createVideo`'s element with its src set;
   * an evicted one has had that src REMOVED, so the count is honest.
   */
  test('the offline render seats EVERY clip, not just the realtime budget', async ({ page }) => {
    test.setTimeout(300_000);

    // Stage clip decoders only. The result-preview <video controls> carries its
    // own blob: URL, so it would inflate the count after the take — exclude it.
    const blobVideos = () => page.evaluate(() =>
      Array.from(document.querySelectorAll('video'))
        .filter((v) => !v.hasAttribute('controls') && (v.getAttribute('src') || '').startsWith('blob:')).length);

    await page.locator('input[type="file"]').first().setInputFiles(TONES);

    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing tone_e\.webm/ }))
      .toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    // PRECONDITION: the live preview is capped — strictly fewer decoders than
    // clips. Without this the render assertion below would pass even if nothing
    // was ever deferred, proving nothing.
    await expect.poll(blobVideos, {
      message: 'the phone budget must defer at least one of the five clips',
      timeout: 60_000,
    }).toBeLessThan(5);

    // Sound is off for every clip by default, so this takes the render path.
    // beginOfflineRender lifts the caps synchronously at the start of the take,
    // so all five elements carry a src for the whole render.
    await page.getByRole('button', { name: 'Record video' }).click();

    await expect.poll(blobVideos, {
      message: 'the offline render must seat all five clips, not the realtime 3',
      timeout: 180_000,
    }).toBe(5);

    // And a real file must come back — the render completed with every clip in
    // it, not just started. The result sheet only shows on ok:true.
    await expect(page.locator('video[controls]')).toBeVisible({ timeout: 180_000 });

    // The budget is back: the extra decoders were released, so the preview is
    // capped again and nothing leaked past the take.
    await expect.poll(blobVideos, {
      message: 'the realtime cap must be restored after the render',
      timeout: 60_000,
    }).toBeLessThan(5);
  });
});

// -----------------------------------------------------------------------------
// THE RENDER IS NOT A RECORDING.
//
// "Choppy" is what a realtime take looks like after the fact. Both realtime
// paths sample a canvas that is playing: MediaRecorder pulls from a stream, and
// `recordFrames` samples on rAF, snaps its schedule forward when it is late and
// drops frames under backpressure. Under this app's own load those are the
// normal case, and the stall ends up in the file.
//
// `renderOffline` has one invariant that no realtime path can hold:
//
//     frames encoded === round(duration x fps)     EXACTLY
//
// because the timeline is defined by the frame INDEX, not the clock. A dropped
// frame breaks it, a stalled decoder breaks it, a slow encoder does not. That
// equality is the whole assertion below.
// -----------------------------------------------------------------------------

test.describe('the video is rendered, not screen-recorded', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
      if (typeof caches !== 'undefined') {
        for (const k of await caches.keys()) await caches.delete(k);
      }
    }).catch(() => { /* no SW in this context is fine */ });
  });

  test('every frame is present — no drops, exact duration', async ({ page }) => {
    test.setTimeout(300_000);

    // TWO 1080p clips: the load that makes a realtime take stutter. A render
    // that only holds on the easy scene proves nothing.
    await page.locator('input[type="file"]').first().setInputFiles([HD_A, HD_B]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing hd_b\.webm/ }))
      .toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    // Sound is off for every clip by default, so this takes the render path.
    await page.getByRole('button', { name: 'Record video' }).click();

    const stat = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
    await expect(stat).toBeVisible({ timeout: 240_000 });
    const line = (await stat.innerText()).trim();

    const m = line.match(/([\d.]+)s\s+·\s+[^·]+·\s+(\d+)fps\s+·\s+(\d+)\s+frames/);
    expect(m, `could not parse the take's stat line: ${line}`).not.toBeNull();

    const durationSec = parseFloat(m![1]);
    const fps = parseInt(m![2], 10);
    const frames = parseInt(m![3], 10);

    // THE INVARIANT. Realtime cannot hold this under load; the renderer must.
    expect(frames, `${line} — frames must equal duration x fps exactly`)
      .toBe(Math.round(durationSec * fps));
    expect(frames).toBeGreaterThan(fps);          // a real take, not one frame
    expect(durationSec).toBeGreaterThan(1);

    // It must also be a file that actually plays, not just an even one.
    const verdict = await page.evaluate(async () => {
      // MUST be the RESULT preview, not a source clip. Stage mints a hidden
      // <video src="blob:..."> per live clip, so a `video[src^="blob:"]` query
      // returns a 1920x1080 FIXTURE and every assertion below silently grades
      // the input instead of the output. `controls` is unique to the result.
      const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
      if (!el) return { played: false, w: 0, reason: 'no preview element' };
      if (el.readyState < 1) {
        await new Promise<void>((res) => {
          el.addEventListener('loadedmetadata', () => res(), { once: true });
          setTimeout(res, 8000);
        });
      }
      const t0 = el.currentTime;
      await el.play().catch(() => { /* controls present; autoplay may be refused */ });
      await new Promise((r) => setTimeout(r, 900));
      return { played: el.currentTime > t0, w: el.videoWidth, reason: '' };
    });
    expect(verdict.w, 'the render must carry a real video track').toBeGreaterThan(0);
    expect(verdict.played, 'the rendered file must actually play').toBe(true);

    // RESOLUTION IS PART OF "NOT CHOPPY BUT ALSO NOT WORSE".
    //
    // `captureBackingW` is a REALTIME compositing budget — 720 on mobile, 1080
    // on desktop — chosen so a live take can keep up. An offline render pays
    // none of that: it seeks, draws and encodes one frame at a time with no
    // clock, so it can afford the full logical surface. Inheriting the realtime
    // cap made the export LOWER RESOLUTION THAN THE PREVIEW ON THE SAME SCREEN.
    expect(verdict.w, `render must use the full backing surface, got ${verdict.w}px`)
      .toBeGreaterThanOrEqual(1200);
  });

  test('a clip with sound on still always produces a take', async ({ page }) => {
    test.setTimeout(300_000);

    await page.locator('input[type="file"]').first().setInputFiles([HD_A]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    // Turning sound on is the ONE case that must not be traded for smoothness:
    // the renderer draws frames and has no audio to capture, so the realtime
    // recorder has to stay reachable. Nothing was removed by making render the
    // default — this is the proof.
    const unmute = page.getByRole('button', { name: /Unmute hd_a\.webm/ });
    if (await unmute.count()) {
      await unmute.click();
      await expect(page.getByRole('button', { name: /Mute hd_a\.webm/ }))
        .toBeVisible({ timeout: 10_000 });
    }

    await page.getByRole('button', { name: 'Record video' }).click();
    const stat = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
    await expect(stat).toBeVisible({ timeout: 240_000 });

    // THE INVARIANT IS "YOU ALWAYS GET A VIDEO", not "you always get sound".
    // Realtime is allowed to drop frames — that is what it is — and where the
    // realtime path cannot run at all (iOS: no MediaRecorder, no captureStream)
    // the app must fall back to the silent render rather than produce nothing.
    // Honouring "wants sound" unconditionally made an iPhone return NOTHING,
    // which is how this assertion was written in the first place.
    const line = (await stat.innerText()).trim();
    expect(line).toMatch(/\d+\s+frames/);
    expect(parseInt(line.match(/(\d+)\s+frames/)![1], 10)).toBeGreaterThan(0);
  });
});
