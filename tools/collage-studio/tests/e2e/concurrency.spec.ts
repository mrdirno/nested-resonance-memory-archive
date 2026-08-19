// tests/e2e/concurrency.spec.ts
// -----------------------------------------------------------------------------
// EVERY IMPORTED VIDEO PLAYS AT ONCE — the wish, asserted at the level it was
// made. From the field: "Multiple videos should play back at the same time.
// Concurrency not just one."
//
// video-collage.spec.ts already proves two HD clips both HOLD DECODERS. That is
// the gate, not the claim (scar C165): a clip can own a decoder and sit paused,
// or play into an element whose pixels never reach the composition. This file
// asserts the claim itself, twice over:
//
//   1. ELEMENTS — every stage <video> is unpaused, ready, and its currentTime
//      ADVANCES over a measured interval. Not `readyState >= 2` (a paused
//      element passes) and not `!paused` alone (iOS Low Power Mode leaves
//      `paused === false` while the clock is frozen — stage.armPlayProbe exists
//      because of exactly that lie).
//   2. PIXELS — each clip's own region of the live canvas changes over time.
//      The three fixtures are hue-keyed (red / green / blue field under WHITE
//      STRIPES, 50% duty, moving half a period every 400 ms) so each clip's
//      fragments can be found on the composition without assuming anything
//      about the layout, ANY crop of the frame flips field↔white between two
//      samples 400 ms apart (a single sweeping bar missed narrow crops — the
//      first cut of this file was flaky on exactly that), and a frozen clip
//      cannot hide behind a neighbour that is moving.
//   3. THE WISH, LITERALLY — two 4K clips (3840×2160, the frame a phone shoots)
//      on an iPhone UA BOTH play. Under the shipped budget (3 × 1080p) the
//      second was refused a-priori with "1 of 2 clips playing (these clips are
//      too high-resolution…)"; this test fails on that code and passes on
//      `lib/admission.ts`'s caps. The fixtures are real 3840×2160 VP9 streams
//      (flat stripes, ~16 KB each) so the decoder budget is charged the real
//      frame, not a hint.
//
// The element check is the load-bearing one: it is immune to the turn re-cutting
// the composition mid-sample. The pixel check is what ties "the element plays"
// to "the person sees it play", which is the sentence the wish is about.
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** Hue-keyed motion fixtures: white stripes moving over one saturated field. */
const DRIFTS = ['drift_a', 'drift_b', 'drift_c']
  .map((n) => join(HERE, '..', 'fixtures', `${n}.webm`));
/** The same law at 3840×2160 — two phone-shot 4K frames, red and green. */
const DRIFTS_4K = ['drift_a4k', 'drift_b4k']
  .map((n) => join(HERE, '..', 'fixtures', `${n}.webm`));

/** Which channel dominates each fixture, in DRIFTS order. */
type Hue = 'r' | 'g' | 'b';
const HUES: Hue[] = ['r', 'g', 'b'];

const startPlaybackIfGated = async (page: Page) => {
  const tap = page.getByRole('button', { name: 'Tap to play' });
  if (await tap.isVisible().catch(() => false)) await tap.click();
};

/** The stage's own clip decoders — never the result preview (`controls`). */
const stageClocks = (page: Page): Promise<{ src: string; paused: boolean; ready: number; t: number }[]> =>
  page.evaluate(() =>
    Array.from(document.querySelectorAll('video'))
      .filter((v) => !v.hasAttribute('controls') && (v.getAttribute('src') || '').startsWith('blob:'))
      .map((v) => ({ src: v.src, paused: v.paused, ready: v.readyState, t: v.currentTime })));

/**
 * Downsample the live canvas and split it into per-hue pixel sets. 48x48 keeps
 * a fragment of a 3-way layout tens of pixels big while staying cheap enough
 * to run twice 400ms apart without skewing its own measurement.
 */
const sampleHueRegions = (page: Page) =>
  page.evaluate(() => {
    const src = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!src || !src.width || !src.height) return null;
    const N = 48;
    const t = document.createElement('canvas');
    t.width = N; t.height = N;
    const tc = t.getContext('2d', { willReadFrequently: true });
    if (!tc) return null;
    tc.drawImage(src, 0, 0, N, N);
    const d = tc.getImageData(0, 0, N, N).data;
    const regions: Record<string, number[]> = { r: [], g: [], b: [] };
    const rgb: number[] = new Array(d.length);
    for (let i = 0; i < d.length; i += 4) {
      const r = d[i], g = d[i + 1], b = d[i + 2];
      rgb[i] = r; rgb[i + 1] = g; rgb[i + 2] = b; rgb[i + 3] = 255;
      // Saturated field pixels only — the white bar and any grade wash are
      // deliberately excluded so a region is the CLIP'S OWN ground.
      if (r > 120 && g < 90 && b < 90) regions.r.push(i);
      else if (g > 110 && r < 90 && b < 90) regions.g.push(i);
      else if (b > 120 && r < 90 && g < 90) regions.b.push(i);
    }
    return { rgb, regions };
  });

/** Re-read the same pixel indices and count how many moved past a threshold. */
const countChangedAt = (page: Page, indices: number[], before: number[]) =>
  page.evaluate(({ indices, before }) => {
    const src = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!src || !src.width || !src.height) return -1;
    const N = 48;
    const t = document.createElement('canvas');
    t.width = N; t.height = N;
    const tc = t.getContext('2d', { willReadFrequently: true });
    if (!tc) return -1;
    tc.drawImage(src, 0, 0, N, N);
    const d = tc.getImageData(0, 0, N, N).data;
    let changed = 0;
    for (const i of indices) {
      if (Math.abs(d[i] - before[i]) > 40 ||
          Math.abs(d[i + 1] - before[i + 1]) > 40 ||
          Math.abs(d[i + 2] - before[i + 2]) > 40) changed++;
    }
    return changed;
  }, { indices, before });

const IPHONE_UA =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
  + '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';

/**
 * The proof, shared by both device shapes below. Kept to ONE helper so the
 * phone run and the desktop run cannot drift into asserting different things.
 */
const proveAllThreePlay = async (page: Page) => {
  await page.locator('input[type="file"]').first().setInputFiles(DRIFTS);

  await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
  for (const n of ['drift_a', 'drift_b', 'drift_c']) {
    await expect(page.getByRole('button', { name: new RegExp(`Stop playing ${n}\\.webm`) }))
      .toBeVisible({ timeout: 200_000 });
  }
  await startPlaybackIfGated(page);

  // --- 1. ELEMENTS: three decoders, all unpaused and ready -------------------
  await expect.poll(async () => {
    const rows = await stageClocks(page);
    return rows.filter((r) => !r.paused && r.ready >= 2).length;
  }, {
    message: 'all three clips must be unpaused with data — not merely admitted',
    timeout: 60_000,
  }).toBe(3);

  // ...and every clock ADVANCES. `paused === false` is a claim; a moving
  // currentTime is the fact. Sampled per element, matched by src.
  const t0 = await stageClocks(page);
  await page.waitForTimeout(700);
  const t1 = await stageClocks(page);
  for (const a of t0) {
    const b = t1.find((x) => x.src === a.src);
    expect(b, `decoder ${a.src} vanished mid-measurement`).toBeTruthy();
    expect(b!.t, `a clip is live but its clock is frozen (${a.src})`).toBeGreaterThan(a.t);
  }

  // --- 2. PIXELS: each clip's own ground on the canvas moves -----------------
  // Regions are re-derived here, AFTER the element wait, so a slow first paint
  // cannot hand us a half-composed frame to diff against.
  let firstSample = await sampleHueRegions(page);
  // The very first composition can still be mid-fill; retry briefly until all
  // three hues have real ground on the canvas.
  for (let i = 0; i < 20; i++) {
    if (firstSample &&
        firstSample.regions.r.length >= 10 &&
        firstSample.regions.g.length >= 10 &&
        firstSample.regions.b.length >= 10) break;
    await page.waitForTimeout(400);
    firstSample = await sampleHueRegions(page);
  }
  expect(firstSample, 'the live canvas must be readable').not.toBeNull();
  for (const h of HUES) {
    expect(firstSample!.regions[h].length,
      `clip ${h}'s field never reached the composition — its fragments are not on screen`)
      .toBeGreaterThanOrEqual(10);
  }

  // 400ms at 25fps is ten source frames — the bar sweeps ~40px of a 480px
  // field, far past the 40-step channel threshold, while staying inside one
  // turn hold so a re-cut cannot masquerade as playback.
  await page.waitForTimeout(400);
  for (const h of HUES) {
    const region = firstSample!.regions[h];
    const changed = await countChangedAt(page, region, firstSample!.rgb);
    expect(changed, `clip ${h} is on screen but its pixels never move — playing for the dock, frozen for the person`)
      .toBeGreaterThanOrEqual(Math.max(2, Math.floor(region.length * 0.02)));
  }

  // --- 3. NO FALSE STALL. The stall judge (stage.armPlayProbe → admission.judgeStall)
  // has had its first window, its strike window and a re-probe by now; three
  // healthy decoders must still be three, and the notice must not claim a
  // measurement that never happened. A judge that accused a loading or
  // wrapping clip would have evicted one here — the wish regressing under a
  // new name.
  await page.waitForTimeout(2500);
  const after = await stageClocks(page);
  expect(after.filter((r) => !r.paused && r.ready >= 2).length, 'a healthy clip was evicted by a false stall verdict').toBe(3);
  await expect(page.getByText(/can't run them all|clips playing/)).toHaveCount(0);
};

test.describe('every imported video plays at once — a phone', () => {
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

  test('three clips, three moving regions, three advancing clocks', async ({ page }) => {
    test.setTimeout(240_000);
    await proveAllThreePlay(page);
  });

  test('THE WISH: two 4K clips on a phone BOTH play — not "1 of 2"', async ({ page }) => {
    test.setTimeout(240_000);
    await page.locator('input[type="file"]').first().setInputFiles(DRIFTS_4K);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    for (const n of ['drift_a4k', 'drift_b4k']) {
      await expect(page.getByRole('button', { name: new RegExp(`Stop playing ${n}\\.webm`) }))
        .toBeVisible({ timeout: 200_000 });
    }
    await startPlaybackIfGated(page);

    // Both decoders, both unpaused, both with data — and both REAL 4K, so the
    // budget was charged 2 × 8,294,400, which the shipped 6,220,800 refused.
    await expect.poll(async () => {
      const rows = await page.evaluate(() =>
        Array.from(document.querySelectorAll('video'))
          .filter((v) => !v.hasAttribute('controls') && (v.getAttribute('src') || '').startsWith('blob:'))
          .map((v) => ({ paused: v.paused, ready: v.readyState, w: v.videoWidth, h: v.videoHeight })));
      return rows.filter((r) => !r.paused && r.ready >= 2 && r.w === 3840 && r.h === 2160).length;
    }, {
      message: 'both 4K clips must hold a decoder, unpaused, with data — the shipped budget seated ONE',
      timeout: 60_000,
    }).toBe(2);

    const t0 = await stageClocks(page);
    expect(t0.length, 'exactly two stage decoders').toBe(2);
    await page.waitForTimeout(700);
    const t1 = await stageClocks(page);
    for (const a of t0) {
      const b = t1.find((x) => x.src === a.src);
      expect(b, `decoder ${a.src} vanished mid-measurement`).toBeTruthy();
      expect(b!.t, `a 4K clip is live but its clock is frozen (${a.src})`).toBeGreaterThan(a.t);
    }

    // And the sentence the wisher read is GONE: no "1 of 2 clips playing".
    await expect(page.getByText(/1 of 2 clips playing/)).toHaveCount(0);

    // Pixels: both fields on the canvas, both moving.
    let first = await sampleHueRegions(page);
    for (let i = 0; i < 20; i++) {
      if (first && first.regions.r.length >= 10 && first.regions.g.length >= 10) break;
      await page.waitForTimeout(400);
      first = await sampleHueRegions(page);
    }
    expect(first, 'the live canvas must be readable').not.toBeNull();
    for (const h of ['r', 'g'] as Hue[]) {
      expect(first!.regions[h].length, `4K clip ${h}'s field never reached the composition`).toBeGreaterThanOrEqual(10);
    }
    await page.waitForTimeout(400);
    for (const h of ['r', 'g'] as Hue[]) {
      const region = first!.regions[h];
      const changed = await countChangedAt(page, region, first!.rgb);
      expect(changed, `4K clip ${h} is on screen but its pixels never move`)
        .toBeGreaterThanOrEqual(Math.max(2, Math.floor(region.length * 0.02)));
    }
  });
});

test.describe('every imported video plays at once — a desktop', () => {
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

  test('three clips, three moving regions, three advancing clocks', async ({ page }) => {
    test.setTimeout(240_000);
    await proveAllThreePlay(page);
  });
});
