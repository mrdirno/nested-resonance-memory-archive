/**
 * ONE LAYOUT AT THE ARTIFACT — the exported file's partition IS the preview's.
 *
 * The pure geometry is swept in tests/unit/oneLayout.invariants.mjs (the whole
 * 23-generator roster plus the seven legacy modes, at the real export sizes from
 * `dimsForTier`, with the pre-fix function kept as the oracle so the sweep
 * measures the divergence it removes: 10.5% of seeds at count=24 and 24.5% at
 * count=40 came back as a different partition, worst drift 1.18 of the canvas).
 *
 * ONE thing lives only out here: whether the SHIPPED APP still wires the preview
 * and an export to the same partition once React state, debounces and the export
 * dialog are in the way. Three times now a composition feature has been correct
 * in its module and wrong at the seam (previewSrc-vs-src, then crop focus, then
 * the export rebuilding its own asset list), so a green module proves nothing
 * about the file a user downloads.
 *
 * WHY THE SVG EXPORT, AND WHY THIS IS NOT A PIXEL TEST. `handleExportSVG` writes
 * the actual cell polygons into the file as <clipPath> paths, so the exported
 * artifact can be compared to the preview's own overlay GEOMETRICALLY rather
 * than by asking whether two renders look similar. That matters because it makes
 * the test a 100% discriminator instead of a seed lottery:
 *
 *   - the SVG rounds coordinates with toFixed(2) at width 1000, so its own noise
 *     floor is 0.005/1000 = 5e-6 normalised;
 *   - MEASURED on the pre-fix code over 60 seeds x 2 aspects, the smallest
 *     preview-vs-SVG disagreement was 4.5e-4 — ninety times that floor, on the
 *     BEST seed. The worst was 0.90 of the canvas.
 *
 * So TOL = 2e-5 passes cleanly after the fix and fails on every seed before it.
 * A "which preview does this look more like" pixel comparison could only have
 * caught the ~11% of seeds where the partition changes grossly.
 *
 * Drive `Balanced` / `Minimal` deliberately: `complex` (voronoi) was measured
 * already scale-invariant at 2e-16, so a suite that only exercised it would have
 * been green against the broken build. Same lesson as twist's T4.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.one-layout.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.one-layout.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** Normalised. 4x the SVG's own toFixed(2) floor, 22x below the pre-fix best case. */
const TOL = 2e-5;

// --- fixtures ----------------------------------------------------------------

function png(w: number, h: number, pixel: (x: number, y: number) => [number, number, number]): Buffer {
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; // 8-bit truecolour RGB
  const rows: Buffer[] = [];
  for (let y = 0; y < h; y++) {
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) {
      const [r, g, b] = pixel(x, y);
      row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b;
    }
    rows.push(row);
  }
  const idat = zlib.deflateSync(Buffer.concat(rows));
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

const tiles = (n = 12) => Array.from({ length: n }, (_, i) => {
  const hue: [number, number, number][] = [
    [236, 72, 60], [60, 200, 236], [250, 210, 70], [130, 240, 130],
    [220, 120, 250], [255, 150, 60], [90, 140, 250], [250, 250, 250],
    [70, 230, 200], [250, 90, 170], [180, 180, 60], [120, 90, 240],
  ];
  const [r, g, b] = hue[i % hue.length];
  return { name: `tile_${i}.png`, mimeType: 'image/png', buffer: png(96, 96, () => [r, g, b] as [number, number, number]) };
});

// --- geometry ----------------------------------------------------------------

type Cell = [number, number][];

/** Parse "M x y L x y … Z" into vertices. Both writers emit exactly this shape. */
function parsePath(d: string): Cell {
  const out: Cell = [];
  const re = /[ML]\s+(-?[\d.]+)\s+(-?[\d.]+)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(d))) out.push([parseFloat(m[1]), parseFloat(m[2])]);
  return out;
}

const normalise = (cells: Cell[], W: number, H: number): Cell[] =>
  cells.map((c) => c.map(([x, y]) => [x / W, y / H] as [number, number]));

/** Largest normalised vertex disagreement. Infinity when the two are not even the same shape. */
function maxVertexDelta(a: Cell[], b: Cell[]): number {
  if (a.length !== b.length) return Infinity;
  let worst = 0;
  for (let i = 0; i < a.length; i++) {
    if (a[i].length !== b[i].length) return Infinity;
    for (let k = 0; k < a[i].length; k++) {
      worst = Math.max(worst, Math.abs(a[i][k][0] - b[i][k][0]), Math.abs(a[i][k][1] - b[i][k][1]));
    }
  }
  return worst;
}

// --- page helpers ------------------------------------------------------------

async function boot(page: Page, files: { name: string; mimeType: string; buffer: Buffer }[]) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(files);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // The tabs are labelled Layout / Settings — NOT Simple / Advanced (scar: an
  // e2e written against the internal state names finds no button and times out).
  await page.getByRole('button', { name: 'Settings' }).first().click();
}

async function pickMode(page: Page, label: string) {
  await page.getByRole('button', { name: label, exact: true }).first().click();
  await page.waitForTimeout(1400);   // the layout effect debounces 50ms then renders
}

async function pickAspect(page: Page, label: string) {
  await page.getByRole('button', { name: label, exact: true }).first().click();
  await page.waitForTimeout(1400);
}

/**
 * The PREVIEW's own cells, straight off the lock overlay — the <svg viewBox="0 0
 * 1200 …"> App.tsx draws from `layoutItems`. This is the partition on screen,
 * not a re-computation of it.
 */
async function previewCells(page: Page): Promise<{ cells: Cell[]; W: number; H: number }> {
  const raw = await page.evaluate(() => {
    const svg = Array.from(document.querySelectorAll('svg[viewBox]'))
      .find((s) => (s.getAttribute('viewBox') || '').startsWith('0 0 1200 ')) as SVGSVGElement | undefined;
    if (!svg) return null;
    const [, , w, h] = (svg.getAttribute('viewBox') || '').split(/\s+/).map(Number);
    const ds = Array.from(svg.querySelectorAll('g')).map((g) => g.querySelector('path')?.getAttribute('d') || '');
    return { w, h, ds: ds.filter(Boolean) };
  });
  expect(raw, 'the preview overlay was not found — no partition to compare').not.toBeNull();
  return { cells: normalise(raw!.ds.map(parsePath), raw!.w, raw!.h), W: raw!.w, H: raw!.h };
}

/**
 * The EXPORTED FILE's cells. Drives the real Export dialog, takes the real
 * download, and parses the clip paths out of the bytes that landed on disk.
 */
async function exportedSvgCells(page: Page): Promise<{ cells: Cell[]; W: number; H: number }> {
  await page.getByRole('button', { name: 'Export' }).first().click();
  const dialog = page.getByRole('dialog').filter({ hasText: 'Export' }).first();
  await expect(dialog).toBeVisible();
  // Scoped to the dialog and `.first()`: the app has a SECOND "Vector SVG"
  // button outside it, and an unscoped role query trips strict mode.
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 90_000 }),
    dialog.getByRole('button', { name: /Vector SVG/ }).first().click(),
  ]);
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const c of stream) chunks.push(c as Buffer);
  const svg = Buffer.concat(chunks).toString('utf8');

  const vb = /<svg[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
  expect(vb, 'the exported SVG has no viewBox').not.toBeNull();
  const ds = Array.from(svg.matchAll(/<clipPath id="clip-\d+">\s*<path d="([^"]+)"/g)).map((m) => m[1]);
  return { cells: normalise(ds.map(parsePath), parseFloat(vb![1]), parseFloat(vb![2])), W: parseFloat(vb![1]), H: parseFloat(vb![2]) };
}

async function assertOneLayout(page: Page, where: string) {
  const preview = await previewCells(page);
  expect(preview.cells.length, `${where}: the preview drew no cells`).toBeGreaterThan(6);

  const exported = await exportedSvgCells(page);
  expect(
    exported.cells.length,
    `${where}: the export has ${exported.cells.length} fragments, the preview has ${preview.cells.length} — ` +
    `the export computed its own partition and slots fell off the end of it`,
  ).toBe(preview.cells.length);

  // The two canvases are DIFFERENT SIZES on purpose (1200 vs 1000): if the
  // normalised geometry matches, the export is the preview scaled, which is the
  // whole rung.
  expect(preview.W).not.toBe(exported.W);

  const d = maxVertexDelta(preview.cells, exported.cells);
  expect(
    d,
    `${where}: the exported file's partition is ${d.toExponential(2)} away from the preview's ` +
    `(normalised). Pre-fix the BEST seed measured 4.5e-4 and the worst 0.90; the SVG's own ` +
    `rounding floor is 5e-6. The export is not drawing the composition that was on screen.`,
  ).toBeLessThan(TOL);
}

// =============================================================================

test.describe('one layout (the preview partition is the exported partition)', () => {

  test('A1: an even grid exports the partition that was on screen', async ({ page }) => {
    await boot(page, tiles());
    await pickMode(page, 'Balanced');
    await assertOneLayout(page, 'Balanced @ 2:3');
  });

  test('A2: it survives a different canvas aspect', async ({ page }) => {
    // The basis height is `1200 / aspect`, so an aspect the app did not start on
    // is the case where an inferred basis (rather than the passed one) goes
    // wrong — and the export's whole-pixel dimensions do not share the preview's
    // aspect exactly, which is what broke the first version of this fix.
    await boot(page, tiles());
    await pickMode(page, 'Minimal');
    await pickAspect(page, '16:9');
    await assertOneLayout(page, 'Minimal @ 16:9');
  });
});
