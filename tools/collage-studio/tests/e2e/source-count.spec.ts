/**
 * FRAGMENT COUNT FOLLOWS THE UPLOAD — the artifact-level proof of the source-first
 * fill. The pure invariants are swept in tests/unit/fill.invariants.mjs; this proves
 * the WIRING a unit test cannot reach: that the on-screen fragment count equals the
 * number of photos/videos imported (R1), and that a video imports as ONE PLAYING
 * element rather than its extracted stills (R3).
 *
 * Run against the live dev server:
 *   npx playwright test --config playwright.source-count.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.source-count.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
// VP9: the codec every Chromium build decodes, so a red test means the feature
// broke, never that the fixture was unplayable.
const CLIP = join(HERE, '..', 'fixtures', 'motion.webm');

// A valid solid-colour PNG built in-process — lets a test upload any number of
// DISTINCT photos with no fixture files. Distinct colours because the app runs a
// colour analysis on every image.
function makePng(r: number, g: number, b: number, size = 64): Buffer {
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

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h /= 360;
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const hk = (t: number) => {
    if (t < 0) t += 1; if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  return [Math.round(hk(h + 1 / 3) * 255), Math.round(hk(h) * 255), Math.round(hk(h - 1 / 3) * 255)];
}

const distinctPhotos = (n: number, tag = 'a') =>
  Array.from({ length: n }, (_, i) => {
    const [r, g, b] = hslToRgb((i / Math.max(1, n)) * 360, 0.7, 0.5);
    return { name: `photo_${tag}_${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b) };
  });

const upload = (page: Page, files: { name: string; mimeType: string; buffer: Buffer }[]) =>
  page.locator('input[type="file"]').first().setInputFiles(files);

/** The integer shown as "<n> FRAGMENTS" in the persistent readout. */
const fragments = (page: Page) =>
  page.evaluate(() => {
    const el = document.querySelector('.ui-readout');
    const m = el?.textContent?.match(/(\d+)\s*FRAGMENTS/i);
    return m ? parseInt(m[1], 10) : null;
  });

/** FNV-ish hash of the live composition at 32x32 — changes iff the picture moved. */
const sampleCanvas = (page: Page) =>
  page.evaluate(() => {
    const src = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!src || !src.width || !src.height) return -1;
    const t = document.createElement('canvas'); t.width = 32; t.height = 32;
    const tc = t.getContext('2d'); if (!tc) return -1;
    tc.drawImage(src, 0, 0, 32, 32);
    const d = tc.getImageData(0, 0, 32, 32).data;
    let hsh = 2166136261;
    for (let i = 0; i < d.length; i += 4) hsh = (Math.imul(hsh ^ d[i], 16777619) + Math.imul(d[i + 1], 31) + d[i + 2]) >>> 0;
    return hsh;
  });

test.describe('fragment count follows the upload (source-first)', () => {
  test.beforeEach(async ({ page }) => { await page.goto(APP_URL); });

  test('R1: N distinct photos -> N fragments, uncapped past the old 12', async ({ page }) => {
    await upload(page, distinctPhotos(15));
    // The old code capped at min(assetCount, 12) and stranded the other three.
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(15);
  });

  test('R1+R3: one video counts ONCE and PLAYS as a single element', async ({ page }) => {
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
    // A video is ONE source — not its 8-12 extracted frames (old count was 12).
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(1);
    // And that single fragment is the LIVE clip: the composition moves.
    const tap = page.getByRole('button', { name: 'Tap to play' });
    if (await tap.isVisible().catch(() => false)) await tap.click();
    const a = await sampleCanvas(page);
    await page.waitForTimeout(800);
    const b = await sampleCanvas(page);
    expect(a).not.toBe(-1);            // canvas is live
    expect(b).not.toBe(a);             // motion => the playable version got position
  });

  test('R1: mixed 3 photos + 1 video -> 4 fragments', async ({ page }) => {
    await upload(page, distinctPhotos(3));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(3);
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(4);
  });

  test('R1: count climbs as more media lands, never capped', async ({ page }) => {
    await upload(page, distinctPhotos(6, 'a'));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(6);
    await upload(page, distinctPhotos(3, 'b'));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(9);
  });

  test('R3 regression: a video added AFTER the count is user-owned still appears and plays', async ({ page }) => {
    await upload(page, distinctPhotos(3));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(3);
    // The user takes the wheel and shrinks the count below the source total.
    await page.getByRole('button', { name: 'Fewer fragments' }).click();
    await expect.poll(() => fragments(page), { timeout: 10_000 }).toBe(2);
    // Now import a video. Grow-to-cover must lift the count so the clip has a slot.
    await page.locator('input[type="file"]').first().setInputFiles(CLIP);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 120_000 });
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(4); // 3 photos + 1 video, none stranded
    const tap = page.getByRole('button', { name: 'Tap to play' });
    if (await tap.isVisible().catch(() => false)) await tap.click();
    const a = await sampleCanvas(page);
    await page.waitForTimeout(800);
    const b = await sampleCanvas(page);
    expect(a).not.toBe(-1);
    expect(b).not.toBe(a); // the late-added clip actually plays
  });

  test('a user-chosen count LARGER than the uploads is preserved on later imports', async ({ page }) => {
    await upload(page, distinctPhotos(3, 'a'));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(3);
    const more = page.getByRole('button', { name: 'More fragments' });
    for (let i = 0; i < 5; i++) await more.click(); // 3 -> 8
    await expect.poll(() => fragments(page), { timeout: 10_000 }).toBe(8);
    await upload(page, distinctPhotos(1, 'b')); // sources now 4, still < 8
    // Grow-to-cover only lifts a count that is BELOW the sources; a larger choice stands.
    await expect.poll(() => fragments(page), { timeout: 10_000 }).toBe(8);
  });
});
