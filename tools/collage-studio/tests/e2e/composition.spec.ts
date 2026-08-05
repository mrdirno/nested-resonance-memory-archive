/**
 * COMPOSITION AT THE ARTIFACT — arrangement and crop focus, proved on PIXELS.
 *
 * The pure invariants (permutation, determinism, focus anchors, share codes) are
 * swept in tests/unit/composition.invariants.mjs. This proves the thing a unit
 * test cannot reach: that choosing an arrangement in the real UI actually moves
 * the photographs on the real canvas, in the direction the chip's label claims.
 *
 * The assertion is deliberately a PHYSICAL one rather than "the DOM changed".
 * Upload a luminance ramp of solid tiles, then:
 *   Spotlight -> the bright end of the ramp is pulled to the CENTRE of the frame
 *   Eclipse   -> the same ramp is turned inside out; the centre goes dark
 * so a wiring bug that leaves the arrangement unread fails here even though
 * every pure test still passes.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.composition.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.composition.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** A solid-colour PNG built in-process — no fixture files, any colour we like. */
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

/**
 * A luminance ramp with a colour cast, so the tiles are distinct SOURCES (the
 * fill dedupes by source) and still order cleanly by brightness. Pure greys
 * would work too; the cast makes a failure easier to read in a trace.
 */
const RAMP = 24;
const ramp = () => Array.from({ length: RAMP }, (_, i) => {
  const v = Math.round(12 + (i / (RAMP - 1)) * 231);
  return {
    name: `ramp-${String(i).padStart(2, '0')}.png`,
    mimeType: 'image/png',
    buffer: makePng(v, Math.max(0, v - 10), Math.min(255, v + 8)),
  };
});

/** Mean luminance of the rendered preview inside a normalised sub-rectangle. */
async function meanLuma(page: Page, x0: number, y0: number, x1: number, y1: number): Promise<number> {
  return page.evaluate(({ x0, y0, x1, y1 }) => {
    // The still path is `renderCanvas -> toBlob -> <img>`; the live path is a
    // <canvas>. Read whichever is on screen so the proof does not depend on
    // which preview the app chose.
    const el = (document.querySelector('canvas') as HTMLCanvasElement | null)
      ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!el) return -1;
    const sw = el instanceof HTMLCanvasElement ? el.width : el.naturalWidth;
    const sh = el instanceof HTMLCanvasElement ? el.height : el.naturalHeight;
    if (!sw || !sh) return -1;
    const c = document.createElement('canvas');
    c.width = 160; c.height = Math.max(1, Math.round((160 * sh) / sw));
    const ctx = c.getContext('2d', { willReadFrequently: true });
    if (!ctx) return -1;
    ctx.drawImage(el as CanvasImageSource, 0, 0, c.width, c.height);
    const px = ctx.getImageData(
      Math.floor(x0 * c.width), Math.floor(y0 * c.height),
      Math.max(1, Math.floor((x1 - x0) * c.width)), Math.max(1, Math.floor((y1 - y0) * c.height)),
    ).data;
    let sum = 0, n = 0;
    for (let i = 0; i < px.length; i += 4) { sum += (px[i] + px[i + 1] + px[i + 2]) / 3; n++; }
    return n ? sum / n : -1;
  }, { x0, y0, x1, y1 });
}

/** Centre brightness minus the mean of the four corners. */
async function centreBias(page: Page): Promise<number> {
  const centre = await meanLuma(page, 0.35, 0.35, 0.65, 0.65);
  const corners = await Promise.all([
    meanLuma(page, 0, 0, 0.22, 0.22),
    meanLuma(page, 0.78, 0, 1, 0.22),
    meanLuma(page, 0, 0.78, 0.22, 1),
    meanLuma(page, 0.78, 0.78, 1, 1),
  ]);
  expect(centre).toBeGreaterThanOrEqual(0);
  const edge = corners.reduce((a, b) => a + b, 0) / corners.length;
  return centre - edge;
}

async function boot(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(ramp());
  // The still preview is a blob <img>; a video-free pool never goes live.
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await page.getByRole('button', { name: 'Settings' }).first().click();
  // An even grid, so "centre" and "corner" mean what they say.
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.waitForTimeout(1200);
}

/**
 * A tile with a bright blob in ONE corner and a dark field everywhere else.
 *
 * The point is that its crop MATTERS: the energy centroid lands on the blob, so
 * an energy-anchored fragment is bright and a dead-centre fragment is dark. A
 * solid tile — which every other fixture here uses — looks identical under every
 * crop, and would make an export that ignores the crop setting pass.
 */
function blobPng(corner: number, size = 128): Buffer {
  const w = size, h = size;
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2;
  const bx = corner % 2 === 0 ? 0 : size >> 1;
  const by = corner < 2 ? 0 : size >> 1;
  const rows: Buffer[] = [];
  for (let y = 0; y < h; y++) {
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) {
      const inBlob = x >= bx && x < bx + (size >> 1) && y >= by && y < by + (size >> 1);
      const v = inBlob ? 245 : 14;
      row[1 + x * 3] = v; row[1 + x * 3 + 1] = inBlob ? 235 : 10; row[1 + x * 3 + 2] = inBlob ? 250 : 22;
    }
    rows.push(row);
  }
  const idat = zlib.deflateSync(Buffer.concat(rows));
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

const blobs = () => Array.from({ length: 8 }, (_, i) => ({
  name: `blob-${i}.png`, mimeType: 'image/png', buffer: blobPng(i % 4),
}));

/** Mean luminance of the EXPORTED file, read from the result modal's <img>. */
async function exportedMean(page: Page): Promise<number> {
  await page.getByRole('button', { name: 'Export' }).first().click();
  await expect(page.getByRole('dialog').filter({ hasText: 'Export' }).first()).toBeVisible();
  await page.getByRole('radio', { name: /^2K/ }).click();
  await page.getByRole('button', { name: /^Render 2K JPG/ }).click();
  const shot = page.locator('img[alt="Rendered collage"]');
  await expect(shot).toBeVisible({ timeout: 120_000 });
  await page.waitForTimeout(600);
  const mean = await page.evaluate(() => {
    const img = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    if (!img || !img.naturalWidth) return -1;
    const c = document.createElement('canvas'); c.width = 200; c.height = 200;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return -1;
    cx.drawImage(img, 0, 0, 200, 200);
    const d = cx.getImageData(0, 0, 200, 200).data;
    let sum = 0, n = 0;
    for (let i = 0; i < d.length; i += 4) { sum += (d[i] + d[i + 1] + d[i + 2]) / 3; n++; }
    return sum / n;
  });
  await page.getByRole('button', { name: 'Close' }).first().click();
  await page.waitForTimeout(400);
  return mean;
}

const pick = async (page: Page, group: string, label: string) => {
  await page.getByRole('group', { name: group }).getByRole('button', { name: label, exact: true }).click();
  await page.waitForTimeout(1200);
};

/** Same sign, and at least half the magnitude the preview promised. */
const exportExpectations = (previewGap: number, exportGap: number): boolean => {
  const sameDirection = Math.sign(previewGap) === Math.sign(exportGap);
  const enough = Math.abs(exportGap) >= Math.abs(previewGap) * 0.5;
  if (!sameDirection || !enough) {
    throw new Error(`export did not follow the preview: preview gap ${previewGap.toFixed(1)}, export gap ${exportGap.toFixed(1)} — the crop focus is not reaching the export path`);
  }
  return true;
};

test.describe('composition', () => {
  /**
   * THE EXPORT MUST BE WHAT YOU SAW.
   *
   * The still-image export used to rebuild its own asset list from the raw pool,
   * so the crop focus — which lives on a per-slot COPY of the asset — never
   * reached it: the preview re-framed, and the downloaded PNG came out at the
   * historical anchor. A preview-only assertion cannot see that, which is
   * exactly why it survived the first round of tests. This drives BOTH and
   * compares them.
   */
  test('the exported file carries the crop focus the preview showed', async ({ page }) => {
    await page.goto(APP_URL);
    await page.locator('input[type="file"]').first().setInputFiles(blobs());
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.getByRole('button', { name: 'Settings' }).first().click();
    await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
    await page.waitForTimeout(1200);

    await pick(page, 'Crop focus', 'Detail');
    const detailPreview = await meanLuma(page, 0, 0, 1, 1);
    const detailExport = await exportedMean(page);

    await pick(page, 'Crop focus', 'Centre');
    const centrePreview = await meanLuma(page, 0, 0, 1, 1);
    const centreExport = await exportedMean(page);

    // The fixture has to be able to tell the two modes apart at all, or the
    // comparison below proves nothing.
    const previewGap = detailPreview - centrePreview;
    expect(Math.abs(previewGap), `the preview did not distinguish Detail from Centre (${detailPreview.toFixed(1)} vs ${centrePreview.toFixed(1)})`).toBeGreaterThan(8);

    // And the export has to move the SAME way. Before the fix both exports were
    // identical (the setting never reached the worker) and this gap was ~0.
    const exportGap = detailExport - centreExport;
    expect(exportExpectations(previewGap, exportGap)).toBe(true);
  });

  test('arrangement moves the photographs — Spotlight and Eclipse are opposites', async ({ page }) => {
    await boot(page);

    await pick(page, 'Arrangement', 'Spotlight');
    const spotlight = await centreBias(page);

    await pick(page, 'Arrangement', 'Eclipse');
    const eclipse = await centreBias(page);

    // The labels are a promise about pixels: brightest to the middle, then the
    // same ramp turned inside out. If the arrangement were never read, both
    // numbers would be the same noise around zero and this fails.
    expect(spotlight, `Spotlight must pull light to the centre (bias ${spotlight.toFixed(1)})`).toBeGreaterThan(12);
    expect(eclipse, `Eclipse must push light to the rim (bias ${eclipse.toFixed(1)})`).toBeLessThan(-12);
    expect(spotlight - eclipse).toBeGreaterThan(40);
  });

  test('Natural is the default and every arrangement stays selectable', async ({ page }) => {
    await boot(page);
    const group = page.getByRole('group', { name: 'Arrangement' });
    await expect(group.getByRole('button', { name: 'Natural', exact: true })).toHaveAttribute('data-active', 'true');
    await expect(group.getByRole('button')).toHaveCount(11);
    await expect(page.getByRole('group', { name: 'Crop focus' }).getByRole('button')).toHaveCount(5);
  });

  test('crop focus re-frames the pictures without losing any', async ({ page }) => {
    await boot(page);
    const before = await meanLuma(page, 0, 0, 1, 1);

    // Solid tiles cannot change under a re-crop — which is the point: this
    // asserts the focus switch does not blank, drop or duplicate a fragment,
    // the failure mode a per-slot analysis override could plausibly cause.
    await pick(page, 'Crop focus', 'Wander');
    const wander = await meanLuma(page, 0, 0, 1, 1);
    expect(wander).toBeGreaterThanOrEqual(0);
    expect(Math.abs(wander - before), 'a re-crop of solid tiles must not change the frame').toBeLessThan(6);

    await pick(page, 'Crop focus', 'Centre');
    const centre = await meanLuma(page, 0, 0, 1, 1);
    expect(Math.abs(centre - before)).toBeLessThan(6);
    await expect(page.getByRole('group', { name: 'Crop focus' })
      .getByRole('button', { name: 'Centre', exact: true })).toHaveAttribute('data-active', 'true');
  });

  test('the dice rolls a composition, and the chips follow it', async ({ page }) => {
    await boot(page);
    await page.getByRole('button', { name: 'Layout', exact: true }).first().click();
    const seen = new Set<string>();
    for (let i = 0; i < 8; i++) {
      await page.getByRole('button', { name: /roll the dice/i }).click();
      await page.waitForTimeout(500);
      await page.getByRole('button', { name: 'Settings' }).first().click();
      const active = await page.getByRole('group', { name: 'Arrangement' })
        .locator('button[data-active="true"]').first().innerText();
      seen.add(active.trim());
      await page.getByRole('button', { name: 'Layout', exact: true }).first().click();
    }
    // Eight rolls landing on one arrangement would mean the dice never reaches
    // the roster it is supposed to be widening.
    expect(seen.size, `the dice only ever chose ${[...seen].join(', ')}`).toBeGreaterThan(1);
  });
});
