// tests/e2e/video-resolution.spec.ts
// -----------------------------------------------------------------------------
// THE EXPORTED VIDEO IS ACTUALLY HI-RES — PROVEN BY MEASURING THE PIXELS.
//
// Two ceilings stacked, and only one of them was ever visible:
//
//   SIZE.   `maxBackingW = opts.maxBackingWidth ?? logicalW`, and VideoStage
//           constructed the Stage as `createStage(cv, { onStatus })` — passing
//           neither. So every exported MP4 was 1200px wide, on every device,
//           from any source, while the still export offered 16384.
//
//   SOURCE. `stillKey = asset.previewSrc || asset.src` — the Stage draws the
//           <=1024px THUMBNAIL. The still exporter draws the ORIGINAL and says
//           why (render.worker.ts: "TWO SOURCES, IN ORDER OF QUALITY"). The
//           video path never got that fix.
//
// WHY THE SECOND ONE NEEDS ITS OWN MEASUREMENT. Lifting the size alone is
// trivially "verifiable" — the file is bigger, the dimensions read back larger,
// every assertion passes — and it would be a 4K container full of upscaled
// 1024px thumbnails. A bigger file that is not a better picture is exactly the
// claim this must not make, and NOTHING about the frame size can detect it.
//
// So the picture is measured directly. The fixture is a stripe pattern whose
// period is chosen to DIE in a 1024px thumbnail and SURVIVE in the original:
// 6px at 3000px wide becomes ~2px at 1024 (at Nyquist — it washes to flat grey)
// and ~4px at 2048 (plainly resolved). The test then renders the SAME scene at
// the SAME canvas size twice, changing one thing — which source the Stage draws
// — and measures horizontal gradient energy along a scanline. Flat grey scores
// near zero; real stripes score high. That difference is the feature.
//
// Run (dev):  npx playwright test tests/e2e/video-resolution.spec.ts --project=chromium
// Run (live): COLLAGE_BASE_URL=https://mrdirno.github.io/... npx playwright test ...
//   NOTE: the in-page `import('/src/lib/stage.ts')` is a DEV-SERVER path. Against
//   a built site the module specifier does not exist, so the Stage-level tests
//   skip themselves rather than pass vacuously.
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const STAGE_MOD = '/src/lib/stage.ts';
const FRAME_MOD = '/src/lib/frameExport.ts';

/** The dev server serves TS modules; a built deploy does not. */
const devModules = async (page: Page): Promise<boolean> =>
  page.evaluate(async (m) => {
    try { await import(/* @vite-ignore */ m); return true; } catch { return false; }
  }, STAGE_MOD);

/**
 * ONE SCENE, RENDERED TWICE, ONE VARIABLE.
 *
 * Returns the horizontal gradient energy of the rendered frame under each
 * source choice, plus the canvas size each render actually produced.
 */
const renderBothWays = (page: Page, maxWidth: number) =>
  page.evaluate(async ({ modUrl, maxWidth }) => {
    const mod = await import(/* @vite-ignore */ modUrl);

    // --- the fixture: fine stripes a thumbnail cannot carry -------------------
    const makeStripes = (size: number, period: number): string => {
      const c = document.createElement('canvas');
      c.width = size; c.height = size;
      const x = c.getContext('2d')!;
      x.fillStyle = '#000'; x.fillRect(0, 0, size, size);
      x.fillStyle = '#fff';
      for (let i = 0; i < size; i += period) x.fillRect(i, 0, period / 2, size);
      return c.toDataURL('image/png');
    };
    // Downsample it the way createThumbnail does, so `previewSrc` is a truthful
    // stand-in for what the app really holdsrather than a second full-res copy.
    const downscale = async (dataUrl: string, to: number): Promise<string> => {
      const img = new Image(); img.src = dataUrl; await img.decode();
      const c = document.createElement('canvas');
      c.width = to; c.height = to;
      c.getContext('2d')!.drawImage(img, 0, 0, img.width, img.height, 0, 0, to, to);
      return c.toDataURL('image/png');
    };

    const ORIGINAL = 3000, PERIOD = 6, THUMB = 1024;
    const full = makeStripes(ORIGINAL, PERIOD);
    const preview = await downscale(full, THUMB);

    // --- the scene: one asset filling the frame ------------------------------
    const L = 1200;                       // the Stage's logical width
    const asset = {
      id: 'a', src: full, previewSrc: preview,
      width: ORIGINAL, height: ORIGINAL,
      analysis: { color: { r: 128, g: 128, b: 128 } },
    };
    const layoutItems = [{
      id: 'i0',
      path: [{ x: 0, y: 0 }, { x: L, y: 0 }, { x: L, y: L }, { x: 0, y: L }],
      bounds: { x: 0, y: 0, w: L, h: L },
    }];

    const cv = document.createElement('canvas');
    cv.style.width = '600px'; cv.style.height = '600px';
    document.body.appendChild(cv);
    const stage = mod.createStage(cv, {});
    stage.setScene({ layoutItems, orderedAssets: [asset], mode: 'simple', aspect: 1, bgColor: '#000' });

    // Let the preview thumbnail land, so run A is genuinely the OLD behaviour
    // (a bound, decoded thumbnail) rather than an empty cache.
    await new Promise((r) => setTimeout(r, 900));

    /** Total |Δ| along the middle scanline — flat grey ≈ 0, crisp stripes ≫ 0. */
    const scanEnergy = (): number => {
      const x = cv.getContext('2d')!;
      const y = Math.floor(cv.height / 2);
      const d = x.getImageData(0, y, cv.width, 1).data;
      let e = 0;
      for (let i = 4; i < d.length; i += 4) e += Math.abs(d[i] - d[i - 4]);
      return e / cv.width;                       // per-pixel, so size cannot flatter it
    };

    const takeOne = async (fullRes: boolean) => {
      stage.beginOfflineRender({ maxWidth, fullRes });
      if (fullRes && typeof stage.prepareOfflineStills === 'function') {
        await stage.prepareOfflineStills({ timeoutMs: 20000 });
      }
      await stage.renderAtTime(0);
      const out = { w: cv.width, h: cv.height, energy: scanEnergy() };
      stage.endOfflineRender();
      return out;
    };

    // Order matters: thumbnails FIRST, so the full-res run cannot be credited
    // with a cache the previous run happened to leave behind.
    const thumbs = await takeOne(false);
    const originals = await takeOne(true);

    // After the render, the live path must be back on its own clamp — a leak
    // here would leave the preview decoding originals for the rest of the session.
    const afterW = cv.width;

    // And a SECOND take at a different size must still be correct: state that
    // leaks across takes is how a mid-stream resize corrupts an H.264 stream.
    stage.beginOfflineRender({ maxWidth: 1600, fullRes: true });
    if (typeof stage.prepareOfflineStills === 'function') await stage.prepareOfflineStills({ timeoutMs: 20000 });
    await stage.renderAtTime(0);
    const second = { w: cv.width, h: cv.height };
    stage.endOfflineRender();

    stage.destroy();
    cv.remove();
    return { thumbs, originals, afterW, second };
  }, { modUrl: STAGE_MOD, maxWidth });

test.describe('the exported video is hi-res, in size AND in picture', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await page.waitForLoadState('domcontentloaded');
  });

  test('the render honours the chosen width instead of the welded 1200', async ({ page }) => {
    test.setTimeout(120_000);
    if (!(await devModules(page))) test.skip(true, 'Stage module is a dev-server path');

    const r = await renderBothWays(page, 2048);
    console.log('sizes:', JSON.stringify(r));

    // THE BUG, stated as an assertion: 1200 was the only width this ever produced.
    expect(r.thumbs.w).toBe(2048);
    expect(r.originals.w).toBe(2048);
    expect(r.thumbs.w).toBeGreaterThan(1200);

    // A second take at a different size is honoured too — the size is per-take,
    // not a one-shot that sticks.
    expect(r.second.w).toBe(1600);
  });

  test('the render draws the ORIGINAL, not the 1024px thumbnail', async ({ page }) => {
    test.setTimeout(120_000);
    if (!(await devModules(page))) test.skip(true, 'Stage module is a dev-server path');

    const r = await renderBothWays(page, 2048);
    console.log('detail:', JSON.stringify(r));

    // Same canvas, same scene, same frame — the ONLY difference is the source.
    expect(r.originals.w).toBe(r.thumbs.w);
    expect(r.originals.h).toBe(r.thumbs.h);

    // Stripes at this period survive the original and die in the thumbnail, so
    // "more edge energy" IS "more of the photograph reached the file". The
    // margin is deliberately generous: this must not go red on a rounding
    // difference between engines, only on the source actually being wrong.
    console.log(`thumb energy ${r.thumbs.energy.toFixed(2)} vs original ${r.originals.energy.toFixed(2)}`);
    expect(r.originals.energy).toBeGreaterThan(r.thumbs.energy * 1.5);
  });

  /**
   * THE ONE THAT RUNS ON THE LIVE SITE.
   *
   * The three tests above import `/src/lib/*.ts`, which only a dev server
   * serves — against production they skip, and a suite that skips itself on the
   * only build users touch has verified nothing there. This one drives the REAL
   * UI end to end: import a clip, open the sheet, pick a rung, take it, and read
   * the finished file's dimensions off the `<video>` that plays it back. That
   * number is the deliverable, and 1200 was the only value it could ever hold.
   */
  test('LIVE-CAPABLE: doing the job end to end produces a file wider than 1200', async ({ page }) => {
    test.setTimeout(300_000);
    await page.setViewportSize({ width: 900, height: 900 });
    await page.goto(APP_URL);

    await page.locator('input[type="file"]').first()
      .setInputFiles(new URL('../fixtures/ramp_rgb.mp4', import.meta.url).pathname);
    await expect(page.locator('canvas').first()).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: 'Trim ramp_rgb.mp4' })).toBeVisible({ timeout: 200_000 });

    await page.getByRole('button', { name: /export/i }).first().click();
    const sheet = page.getByRole('dialog');
    await expect(sheet).toBeVisible({ timeout: 20_000 });

    const sizeRow = page.getByRole('radiogroup', { name: 'Video size' });
    if (await sizeRow.count() === 0) {
      test.skip(true, 'this engine offers no WebCodecs ladder');
    }
    // Pick the TOP rung the device offered — the case that would have been
    // impossible before, and the one most likely to expose an encoder limit.
    const rungs = sizeRow.locator('button[role="radio"]:not([disabled])');
    const n = await rungs.count();
    expect(n, 'no selectable rungs').toBeGreaterThan(0);
    const top = rungs.nth(n - 1);
    const rungLabel = (await top.innerText()).replace(/\s+/g, ' ').trim();
    await top.click();

    // Shortest take on offer: this test is about the FRAME, not the duration.
    // Scoped to the SHEET: the video dock carries its own 5s/Record controls,
    // and a page-wide match hits whichever the DOM happens to order first.
    await sheet.getByRole('button', { name: /^5s$/ }).click();
    await sheet.getByRole('button', { name: /Record .*video/i }).click();

    const take = page.getByRole('dialog', { name: 'Recorded take' });
    await expect(take).toBeVisible({ timeout: 240_000 });
    const dims = await take.locator('video').evaluate(async (v: HTMLVideoElement) => {
      if (!v.videoWidth) await new Promise((r) => v.addEventListener('loadedmetadata', r, { once: true }));
      return { w: v.videoWidth, h: v.videoHeight };
    });

    console.log(`chose "${rungLabel}" -> encoded ${dims.w}x${dims.h}`);
    expect(dims.w, 'the take produced no decodable frame').toBeGreaterThan(0);
    // THE BUG, as an assertion against the delivered artifact.
    expect(dims.w, `still pinned at the old fixed width (${dims.w}x${dims.h})`).toBeGreaterThan(1200);
    // And the file is the size the sheet PROMISED, not merely "bigger".
    expect(rungLabel).toContain(String(dims.w));
  });

  test('the size ladder never offers a rung this device would refuse', async ({ page }) => {
    test.setTimeout(120_000);
    if (!(await devModules(page))) test.skip(true, 'frameExport module is a dev-server path');

    const r = await page.evaluate(async (m) => {
      const fe = await import(/* @vite-ignore */ m);
      const out: { aspect: number; rungs: { label: string; w: number; h: number; supported: boolean }[]; verified: boolean[] }[] = [];
      for (const aspect of [0.666, 1, 1.7778]) {
        const rungs = await fe.probeVideoSizes(aspect);
        // Re-ask the encoder DIRECTLY about every rung the ladder offered. The
        // ladder's promise is that this can never disagree with it.
        const verified: boolean[] = [];
        for (const rr of rungs.filter((x: { supported: boolean }) => x.supported)) {
          let ok = false;
          try {
            const Enc = (window as unknown as { VideoEncoder?: typeof VideoEncoder }).VideoEncoder;
            if (Enc) {
              // Ask across the level ladder exactly as pickCodec does.
              for (const idc of ['1f', '20', '28', '29', '2a', '32', '33', '34']) {
                const res = await Enc.isConfigSupported({
                  codec: `avc1.4200${idc}`, width: rr.width, height: rr.height,
                  bitrate: 12_000_000, framerate: 30,
                });
                if (res.supported) { ok = true; break; }
              }
            }
          } catch { ok = false; }
          verified.push(ok);
        }
        out.push({
          aspect,
          rungs: rungs.map((x: { label: string; width: number; height: number; supported: boolean }) =>
            ({ label: x.label, w: x.width, h: x.height, supported: x.supported })),
          verified,
        });
      }
      return out;
    }, FRAME_MOD);

    console.log('ladder:', JSON.stringify(r, null, 1));
    for (const row of r) {
      const offered = row.rungs.filter((x) => x.supported);
      expect(offered.length, `aspect ${row.aspect} offers nothing`).toBeGreaterThan(0);
      // THE PROMISE. Every offered rung really encodes on this device.
      for (let i = 0; i < row.verified.length; i++) {
        expect(row.verified[i], `aspect ${row.aspect} offered ${offered[i].label} ${offered[i].w}x${offered[i].h} but the encoder refuses it`).toBe(true);
      }
      // And every rung beats the 1200px this replaced.
      const top = offered[offered.length - 1];
      expect(top.w * top.h).toBeGreaterThan(1200 * (1200 / row.aspect));
    }
  });
});
