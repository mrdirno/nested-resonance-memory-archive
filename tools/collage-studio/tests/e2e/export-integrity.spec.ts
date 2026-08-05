/**
 * EXPORT INTEGRITY — the artifact-level proof for wishing-well report d88093af:
 *
 *   "When I hit export sometimes it will show a black screen basically
 *    something is causing an out of bounds or issue or error when composing
 *    the elements o assume ... partial elements of the collage appeared but
 *    it failed to export full image."
 *
 * WHY THESE ASSERTIONS AND NOT A SCREENSHOT
 *   Every failure in that report produces a file that LOOKS fine to any check
 *   that only asks "did an image appear?". Over a platform's canvas ceiling the
 *   encoder returns a valid, correctly-sized, entirely BLACK JPEG — right
 *   dimensions, right mime type, plausible byte count. So the test has to read
 *   PIXELS and prove that something was actually drawn.
 *
 *   `lib/exportLimits.ts` sweeps the ladder's decision logic in-process (68
 *   cases, no DOM). What it cannot reach is the WIRING — and the wiring was the
 *   entire bug: that module existed, passed its own tests, and was imported by
 *   nothing. These tests exercise the real app, the real worker and the real
 *   encoder, which is the only place that mistake was visible.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.export-integrity.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.export-integrity.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** A valid solid-colour PNG, built in-process — no fixture files needed. */
function makePng(r: number, g: number, b: number, size = 96): Buffer {
  const w = size, h = size;
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; // 8-bit truecolour RGB
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) { row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b; }
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const idat = zlib.deflateSync(raw);
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

/** BRIGHT, saturated, and distinct — so "the export is black" cannot be confused
 *  with "the user's photographs happened to be dark". */
const brightPhotos = (n: number) =>
  Array.from({ length: n }, (_, i) => {
    const wheel: [number, number, number][] = [
      [255, 64, 64], [64, 255, 64], [64, 64, 255], [255, 255, 64],
      [255, 64, 255], [64, 255, 255], [255, 160, 32], [160, 32, 255],
    ];
    const [r, g, b] = wheel[i % wheel.length];
    return { name: `bright_${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b) };
  });

const upload = (page: Page, files: { name: string; mimeType: string; buffer: Buffer }[]) =>
  page.locator('input[type="file"]').first().setInputFiles(files);

interface Sample {
  w: number; h: number; min: number; max: number; mean: number;
  /** Share of sampled pixels that are essentially black. */
  blackShare: number;
  /** Distinct coarse colours found — a real collage has several. */
  hues: number;
}

/**
 * Read the EXPORTED image's own pixels.
 *
 * Deliberately samples the decoded <img> (the exported blob) rather than the
 * live preview canvas: the preview was never broken, and sampling it would make
 * this test pass on exactly the bug it exists to catch.
 */
const sampleResult = (page: Page): Promise<Sample | null> =>
  page.evaluate(() => {
    const img = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    if (!img || !img.naturalWidth) return null;
    const N = 220; // downsample: reading 16M pixels in-page is not the point
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(img, 0, 0, N, N);
    const d = cx.getImageData(0, 0, N, N).data;
    let min = 255, max = 0, sum = 0, black = 0, n = 0;
    const seen = new Set<number>();
    for (let i = 0; i < d.length; i += 4) {
      const lum = (d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114);
      if (lum < min) min = lum;
      if (lum > max) max = lum;
      sum += lum; n++;
      if (lum < 12) black++;
      seen.add(((d[i] >> 5) << 6) | ((d[i + 1] >> 5) << 3) | (d[i + 2] >> 5));
    }
    return {
      w: img.naturalWidth, h: img.naturalHeight,
      min, max, mean: sum / n, blackShare: black / n, hues: seen.size,
    };
  });

/** Open the export sheet and choose a size row by its label. */
async function exportAt(page: Page, label: string) {
  await page.getByRole('button', { name: 'Export' }).first().click();
  await expect(page.getByRole('dialog').filter({ hasText: 'Export' }).first()).toBeVisible();
  await page.getByRole('radio', { name: new RegExp(`^${label}`) }).click();
  // The primary reads "Render 2K JPG" — matching /^Export/ picks the sheet's
  // own scrim instead and the click is swallowed.
  await page.getByRole('button', { name: new RegExp(`^Render ${label} JPG`) }).click();
}

test.describe('export integrity (wish d88093af: black / partial export)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await upload(page, brightPhotos(8));
    await expect(page.locator('canvas, img').first()).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(1200); // let the first preview settle
  });

  test('R1: a 2K export contains PIXELS, not a black rectangle', async ({ page }) => {
    await exportAt(page, '2K');
    await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 90_000 });

    const s = await sampleResult(page);
    expect(s).not.toBeNull();

    // The long edge is the tier, to within the double-floor. `dimsForTier`
    // floors the WIDTH and then derives the height from it, so at a non-integer
    // aspect the long side lands a pixel or two short (2048 @0.666 -> 1363x2046).
    // That is deliberate — the helper is documented as conservative so a derived
    // size can never exceed a measured ceiling. What matters is that it never
    // OVERSHOOTS the tier and never silently collapses to something tiny.
    expect(Math.max(s!.w, s!.h)).toBeLessThanOrEqual(2048);
    expect(Math.max(s!.w, s!.h)).toBeGreaterThan(2040);

    // THE ASSERTION THAT WOULD HAVE CAUGHT THE BUG. A black export satisfies
    // every structural check and fails all three of these.
    expect(s!.max).toBeGreaterThan(90);        // something bright was drawn
    expect(s!.blackShare).toBeLessThan(0.75);  // not a black rectangle
    expect(s!.hues).toBeGreaterThan(3);        // several distinct fragments landed
  });

  test('R2: MAX asks the DEVICE, and never returns a black giant', async ({ page }) => {
    // The old path started at a hardcoded 30000px and accepted whatever came
    // back. The ladder now starts from a measured ceiling and validates the
    // blob, so this must be a real picture at a size the device can actually do.
    await exportAt(page, 'MAX');
    await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 180_000 });

    const s = await sampleResult(page);
    expect(s).not.toBeNull();
    expect(Math.max(s!.w, s!.h)).toBeGreaterThanOrEqual(2048);
    expect(s!.max).toBeGreaterThan(90);
    expect(s!.blackShare).toBeLessThan(0.75);
    expect(s!.hues).toBeGreaterThan(3);
  });

  test('R3: the ladder reports which tier won and why — no silent acceptance', async ({ page }) => {
    const logs: string[] = [];
    page.on('console', (m) => { if (/^export/.test(m.text())) logs.push(m.text()); });
    await exportAt(page, '4K');
    await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 120_000 });
    // Every export now leaves an audit line naming the winning tier and every
    // tier it rejected on the way down. Silence here means nothing validated.
    expect(logs.join('\n')).toMatch(/export: \d+px \(\d+x\d+\) won/);
  });
});
