/**
 * THE TITLE AT THE ARTIFACT — the caption, proved on PIXELS and on the file.
 *
 * The wrap arithmetic is swept in tests/unit/title.invariants.mjs (82,871
 * checks: containment, the line budget, scale invariance, the red proof for the
 * plate-padding rule). Five things can only be proved out here:
 *
 *   T1  IT REACHES THE PREVIEW, AND CLEARING IT GIVES BACK THE EXACT PICTURE.
 *       The second half is the one that matters: `planTitle` returns null for an
 *       empty title and every emitter returns on null, so an untitled render
 *       must be the render it always was — not "close enough".
 *
 *   T2  THE FOUR CHIPS ARE FOUR PLACES. A picker whose entries put the ink in
 *       the same band is a lie in the UI.
 *
 *   T3  THE EXPORT CARRIES IT. Twice in this codebase a composition feature has
 *       reached the preview and not the downloaded file, because an export path
 *       rebuilt its own inputs (previewSrc-vs-src, then crop focus). The export
 *       here is a WORKER on another thread with its own OffscreenCanvas, which
 *       is exactly the shape that defect takes, so the file is rendered and its
 *       own pixels are read.
 *
 *   T4  THE SVG CARRIES REAL TEXT, and the SAME WRAP. One plan serves four
 *       surfaces; if the SVG re-wrapped, its line count and plate would drift
 *       from the raster's. Both are measured and compared.
 *
 *   T5  IT IS WATERTIGHT ON A PHONE with a long title in the box — the case
 *       that actually overflows a control strip.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.title.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.title.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

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
  ihdr[8] = 8; ihdr[9] = 2;
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

/**
 * SOLID, near-white tiles — the same fixture the twist coverage proof uses.
 * Every pixel a fragment can draw is bright, so the caption's dark scrim is the
 * largest signal in the frame; the gutters are dark too, which is why the
 * measurements below DIFFERENCE against the same collage rendered untitled
 * rather than counting dark pixels outright.
 */
const solids = (n = 10) => Array.from({ length: n }, (_, i) => ({
  name: `solid_${i}.png`,
  mimeType: 'image/png',
  buffer: png(96, 96, () => [250 - i, 250 - i, 252 - i] as [number, number, number]),
}));

const SHORT = 'PARIS 25';
const LONG = 'Kitchen remodel — before and after, day three of the second week';

// --- page helpers ------------------------------------------------------------

async function boot(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(solids());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // The tabs are labelled Layout / Settings — NOT Simple / Advanced (scar: an
  // e2e written against the internal state names finds no button and times out).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.getByRole('button', { name: 'Layout' }).first().click();
  await page.waitForTimeout(1400);
}

async function typeTitle(page: Page, text: string) {
  await page.getByTestId('title-input').fill(text);
  await page.waitForTimeout(1200);   // the still path debounces 50ms, then encodes a blob
}

async function pickPlace(page: Page, id: string) {
  await page.getByTestId(`title-place-${id}`).click();
  await page.waitForTimeout(1200);
}

/** The on-screen preview, downsampled to N x N and returned as raw RGBA. */
const previewBits = (page: Page, N = 160): Promise<number[] | null> =>
  page.evaluate((N) => {
    const el = (document.querySelector('canvas') as HTMLCanvasElement | null)
      ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!el) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(el as CanvasImageSource, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

/** The EXPORTED file's own pixels, at the same N — never the preview. */
const exportBits = (page: Page, N = 160): Promise<number[] | null> =>
  page.evaluate((N) => {
    const img = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    if (!img || !img.naturalWidth) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(img, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

function meanDiff(a: number[], b: number[]): number {
  let sum = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) {
    sum += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]);
    n += 3;
  }
  return sum / n;
}

/**
 * MEAN DIFFERENCE INSIDE A HORIZONTAL BAND, between two renders of the same
 * composition.
 *
 * Deliberately NOT "count the dark pixels": the layout's own GUTTERS are dark,
 * and on a `Balanced` grid they put a dark line in essentially every row, which
 * swamps a scrim measured in absolute terms (measured: 5.1% of the bottom band
 * reads dark with NO caption at all). Differencing against the same collage
 * rendered without a title cancels the gutters exactly and leaves the caption
 * and nothing else.
 */
function bandDiff(a: number[], b: number[], N: number, from: number, to: number): number {
  let sum = 0, n = 0;
  for (let y = Math.floor(from * N); y < Math.floor(to * N); y++) {
    for (let x = 0; x < N; x++) {
      const i = (y * N + x) * 4;
      sum += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]);
      n += 3;
    }
  }
  return n ? sum / n : 0;
}

/** The rows in which two renders differ — i.e. exactly where the caption is. */
function diffRows(a: number[], b: number[], N: number): { first: number; last: number; span: number } {
  let first = -1, last = -1;
  for (let y = 0; y < N; y++) {
    let sum = 0;
    for (let x = 0; x < N; x++) {
      const i = (y * N + x) * 4;
      sum += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]);
    }
    if (sum / (N * 3) > 8) { if (first < 0) first = y; last = y; }
  }
  return first < 0
    ? { first: 0, last: 0, span: 0 }
    : { first: first / N, last: (last + 1) / N, span: (last - first + 1) / N };
}

async function exportAt(page: Page, label: string) {
  await page.getByRole('button', { name: 'Export' }).first().click();
  await expect(page.getByRole('dialog').filter({ hasText: 'Export' }).first()).toBeVisible();
  await page.getByRole('radio', { name: new RegExp(`^${label}`) }).click();
  await page.getByRole('button', { name: new RegExp(`^Render ${label} JPG`) }).click();
  await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 90_000 });
}

async function closeResult(page: Page) {
  const close = page.getByRole('button', { name: /Close|Done/ }).first();
  if (await close.count()) { await close.click(); await page.waitForTimeout(400); }
}

/** Drives the real Export dialog, takes the real download, returns the bytes. */
async function downloadSvg(page: Page): Promise<string> {
  await page.getByRole('button', { name: 'Export' }).first().click();
  const dialog = page.getByRole('dialog').filter({ hasText: 'Export' }).first();
  await expect(dialog).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 90_000 }),
    dialog.getByRole('button', { name: /Vector SVG/ }).first().click(),
  ]);
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const c of stream) chunks.push(c as Buffer);
  return Buffer.concat(chunks).toString('utf8');
}

// =============================================================================

test.describe('the title', () => {

  test('T1: it reaches the preview, and clearing it gives back the exact picture', async ({ page }) => {
    await boot(page);

    const before = await previewBits(page);
    expect(before, 'no preview to start from').not.toBeNull();

    await typeTitle(page, SHORT);
    const titled = await previewBits(page);
    expect(titled).not.toBeNull();
    const on = meanDiff(before!, titled!);
    expect(on, 'typing a title changed nothing on screen').toBeGreaterThan(1.5);

    // THE NO-OP. `planTitle` returns null on an empty string and every emitter
    // returns on null, so this is not "close enough" — it is the same render.
    await typeTitle(page, '');
    const cleared = await previewBits(page);
    expect(cleared).not.toBeNull();
    const off = meanDiff(before!, cleared!);
    expect(
      off,
      `clearing the title left ${off.toFixed(3)}/255 of residue — an untitled render is ` +
      `supposed to run the instruction stream it always ran`,
    ).toBeLessThan(0.05);
  });

  test('T2: the four chips are four places', async ({ page }) => {
    await boot(page);
    const plain = await previewBits(page);
    expect(plain, 'no untitled baseline').not.toBeNull();

    await typeTitle(page, SHORT);

    await pickPlace(page, 'bl');
    const bl = await previewBits(page);
    expect(bl).not.toBeNull();
    const blBot = bandDiff(plain!, bl!, 160, 0.75, 1.0);
    const blTop = bandDiff(plain!, bl!, 160, 0.0, 0.25);
    expect(blBot, 'BOT L changed nothing in the bottom band').toBeGreaterThan(2);
    expect(
      blBot,
      `BOT L moved the bottom band by ${blBot.toFixed(2)}/255 and the top band by ` +
      `${blTop.toFixed(2)} — a caption that lands in both is not placed at all`,
    ).toBeGreaterThan(blTop * 8 + 1);

    await pickPlace(page, 'tl');
    const tl = await previewBits(page);
    expect(tl).not.toBeNull();
    const tlTop = bandDiff(plain!, tl!, 160, 0.0, 0.25);
    const tlBot = bandDiff(plain!, tl!, 160, 0.75, 1.0);
    expect(tlTop, 'TOP L changed nothing in the top band').toBeGreaterThan(2);
    expect(tlTop).toBeGreaterThan(tlBot * 8 + 1);

    // And BOT C is not BOT L — a centred caption is a different picture.
    await pickPlace(page, 'bc');
    const bc = await previewBits(page);
    expect(meanDiff(bl!, bc!), 'BOT C rendered the same as BOT L').toBeGreaterThan(0.8);
  });

  test('T3: the export carries it — the worker thread draws the same caption', async ({ page }) => {
    await boot(page);

    // An UNTITLED export first. Everything but the caption is identical between
    // the two files, so differencing them isolates the caption exactly.
    await exportAt(page, '2K');
    const plain = await exportBits(page);
    expect(plain).not.toBeNull();
    await closeResult(page);

    await typeTitle(page, SHORT);
    await exportAt(page, '2K');
    const titled = await exportBits(page);
    expect(titled).not.toBeNull();

    const bot = bandDiff(plain!, titled!, 160, 0.7, 1.0);
    const top = bandDiff(plain!, titled!, 160, 0.0, 0.3);
    expect(
      bot,
      `the two exported 2K files differ by ${bot.toFixed(2)}/255 in the bottom band — the ` +
      `caption reached the preview and not the file, which is the ` +
      `export-rebuilds-its-own-inputs defect this codebase has shipped twice`,
    ).toBeGreaterThan(2);
    expect(
      bot,
      `the difference is spread over the whole frame (top band ${top.toFixed(2)}/255) rather ` +
      `than confined to the caption — the export is not drawing the same composition`,
    ).toBeGreaterThan(top * 8 + 1);
  });

  test('T4: the SVG carries real text, and the same wrap as the raster', async ({ page }) => {
    await boot(page);

    // The untitled baseline, for the wrap comparison at the end.
    await exportAt(page, '2K');
    const plain = await exportBits(page, 200);
    expect(plain).not.toBeNull();
    await closeResult(page);

    await typeTitle(page, LONG);

    const svg = await downloadSvg(page);

    const titleGroup = /<g id="Title">([\s\S]*?)<\/g>/.exec(svg);
    expect(titleGroup, 'the exported SVG has no Title group').not.toBeNull();
    const group = titleGroup![1];

    const texts = Array.from(group.matchAll(/<text[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*>([^<]*)<\/text>/g));
    expect(texts.length, 'the SVG title has no <text> elements').toBeGreaterThan(0);
    expect(texts.length, 'a caption is never more than three lines').toBeLessThanOrEqual(3);

    // REAL TEXT, not outlines: what was typed is in the file, verbatim.
    const joined = texts.map((t) => t[3]).join(' ').replace(/&amp;/g, '&').replace(/&#8230;|…/g, '');
    expect(joined.replace(/\s+/g, ' ').trim().slice(0, 20)).toBe(LONG.slice(0, 20));

    // The plate, inside the viewBox with room to spare (the containment rule).
    const vb = /<svg[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
    expect(vb).not.toBeNull();
    const W = parseFloat(vb![1]), H = parseFloat(vb![2]);
    const rect = /<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/.exec(group);
    expect(rect, 'the SVG title has no scrim rect').not.toBeNull();
    const [rx, ry, rw, rh] = rect!.slice(1, 5).map(parseFloat);
    const m = 0.05 * Math.min(W, H);
    expect(rx).toBeGreaterThanOrEqual(m - 0.5);
    expect(ry).toBeGreaterThanOrEqual(m - 0.5);
    expect(rx + rw).toBeLessThanOrEqual(W - m + 0.5);
    expect(ry + rh).toBeLessThanOrEqual(H - m + 0.5);

    // THE SAME WRAP, measured on BOTH surfaces. The SVG declares its scrim from
    // `y` to `y+height`; the rendered raster is asked which rows changed when
    // the caption came on. One dropped or added line moves those numbers by a
    // whole line height, so a re-wrap on either path shows up here.
    await exportAt(page, '2K');
    const bits = await exportBits(page, 200);
    expect(bits).not.toBeNull();
    const rows = diffRows(plain!, bits!, 200);
    const svgTop = ry / H, svgBottom = (ry + rh) / H, svgSpan = rh / H;
    const lineFrac = (rh / Math.max(1, texts.length)) / H;
    expect(rows.span, 'the raster export changed no rows at all').toBeGreaterThan(0.01);
    expect(
      Math.abs(rows.span - svgSpan),
      `the SVG's scrim is ${(svgSpan * 100).toFixed(1)}% of the frame tall over ` +
      `${texts.length} line(s) and the rendered file's caption occupies ` +
      `${(rows.span * 100).toFixed(1)}% — one line is ${(lineFrac * 100).toFixed(1)}%, so the ` +
      `two paths wrapped the same text differently, which is what one shared plan prevents`,
    ).toBeLessThan(Math.max(0.02, lineFrac * 0.6));
    expect(
      Math.abs(rows.last - svgBottom),
      `the caption's bottom edge is at ${(rows.last * 100).toFixed(1)}% in the raster and ` +
      `${(svgBottom * 100).toFixed(1)}% in the SVG`,
    ).toBeLessThan(0.03);
    expect(Math.abs(rows.first - svgTop)).toBeLessThan(Math.max(0.03, lineFrac * 0.6));

    // And the state that a saved project restores carries the caption. The
    // manifest moved out of an XML comment and into a <metadata> element when
    // the SVG became re-openable — a caption containing `--` or `-->` made the
    // comment form ill-formed XML. See tests/e2e/svg-project.spec.ts.
    expect(svg).toContain('id="collage-project"');
    expect(svg).toContain('"title"');
  });

  test('T5: watertight with a long title in the box', async ({ page }) => {
    await boot(page);
    await typeTitle(page, LONG);

    // THE FOUR WIDTHS THE PAGES ACTUALLY GET USED AT. A strip that fits a Pixel
    // 5 and splits a 320px screen has not been checked; these are asserted on
    // the REAL page with a long caption in the box, which is the case that
    // overflows.
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(250);
      const m = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
        spill: Array.from(document.querySelectorAll('.ui-titler *')).filter((el) => {
          const r = el.getBoundingClientRect();
          return r.width > 0 && (r.left < -0.5 || r.right > document.documentElement.clientWidth + 0.5);
        }).length,
      }));
      expect(m.scrollW, `the page scrolls sideways at ${w}px (${m.scrollW} > ${m.clientW})`).toBeLessThanOrEqual(m.clientW);
      expect(m.spill, `a title control hangs off the viewport at ${w}px`).toBe(0);
    }

    const overflow = await page.evaluate(() => ({
      scrollW: document.documentElement.scrollWidth,
      clientW: document.documentElement.clientWidth,
      spill: Array.from(document.querySelectorAll('.ui-titler *')).filter((el) => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && (r.left < -0.5 || r.right > document.documentElement.clientWidth + 0.5);
      }).length,
    }));
    expect(
      overflow.scrollW,
      `the page scrolls sideways with a title typed (${overflow.scrollW} > ${overflow.clientW})`,
    ).toBeLessThanOrEqual(overflow.clientW);
    expect(overflow.spill, 'a control in the title strip hangs off the viewport').toBe(0);

    // Tap targets. A control you cannot hit on a ladder is not shipped.
    for (const id of ['title-input', 'title-clear', 'title-place-bl', 'title-place-tc', 'title-size-lg']) {
      const box = await page.getByTestId(id).boundingBox();
      expect(box, `${id} is not on the page`).not.toBeNull();
      expect(box!.height, `${id} is ${box!.height}px tall`).toBeGreaterThanOrEqual(43.5);
    }

    // The clear button really clears, on a phone, in one tap.
    await page.getByTestId('title-clear').click();
    await page.waitForTimeout(300);
    await expect(page.getByTestId('title-input')).toHaveValue('');
  });
});
