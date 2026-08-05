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

const pick = async (page: Page, group: string, label: string) => {
  await page.getByRole('group', { name: group }).getByRole('button', { name: label, exact: true }).click();
  await page.waitForTimeout(1200);
};

test.describe('composition', () => {
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
