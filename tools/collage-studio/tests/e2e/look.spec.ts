/**
 * THE LOOK AT THE ARTIFACT — the colour grade, proved on PIXELS and on the file.
 *
 * The grade arithmetic is swept in tests/unit/grade.invariants.mjs (46,987
 * checks: the no-op rule, the roster's index space, the two emitters denoting
 * ONE colour transform to 6.7e-16, the codec round trip, and a red proof
 * pricing the sRGB pin at 105/255 worst case). Five things can only be proved
 * out here, on a real browser, against real pixels:
 *
 *   T1  IT REACHES THE PREVIEW, AND GOING BACK TO `NONE` GIVES BACK THE EXACT
 *       PICTURE. The second half is the one that matters: `gradeSteps` returns
 *       an empty pipeline for `none` and every caller is guarded on it, so an
 *       ungraded render must be the render it always was — not "close enough".
 *
 *   T2  EACH CHIP IS THE LOOK IT SAYS IT IS. Not merely "different from none":
 *       measured in the DIRECTION each name claims. A roster whose entries all
 *       change the picture but two of which are secretly the same grade is a
 *       lie in the UI that no "did it change?" assertion can see.
 *
 *   T3  THE EXPORT CARRIES IT. Three times in this codebase a composition
 *       feature reached the preview and not the downloaded file, because an
 *       export path rebuilt its own inputs. The export is a WORKER on another
 *       thread with its own OffscreenCanvas — exactly the shape that defect
 *       takes — so a real file is rendered and its own pixels are read.
 *
 *   T4  THE SVG IS THE SAME GRADE AS THE RASTER. The vector path emits real
 *       `<filter>` primitives, not a CSS string, and SVG filters default to
 *       LINEAR light while canvas evaluates in sRGB. The emitted filter pins
 *       sRGB; this test rasterises the actual downloaded SVG and compares its
 *       channel shift against the canvas's. Deleting that one attribute moves
 *       them ~29/255 apart on this look — an order of magnitude over the bar.
 *
 *   T5  THE CODE CARRIES IT. A grade is part of the recipe, so it must survive
 *       being sent — round-tripped through the real strip, on the real page.
 *
 *   T6  IT IS WATERTIGHT ON A PHONE. Eight chips cannot fit one 320px line, so
 *       the row must WRAP rather than push the page sideways.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.look.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.look.config.ts
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
 * HALF SATURATED COLOUR, HALF NEUTRAL GREY — and the split is the measurement.
 *
 * The colourful tiles are what make a chroma change readable (`punch` adds
 * colour, `bleach` takes it away); the neutral ones are what make a CAST
 * readable, because on a neutral R-B is zero until something tints it, and a
 * warm/cool claim measured over saturated tiles is measured against whatever
 * hues the fixture happened to contain. Both are needed: a fixture of only
 * colours cannot see `warm`, and a fixture of only greys cannot see `punch`.
 */
const TILES: [number, number, number][] = [
  [214, 46, 38], [40, 176, 82], [46, 84, 214], [222, 190, 40],
  [186, 52, 176], [40, 190, 200],
  [58, 58, 58], [110, 110, 110], [160, 160, 160], [208, 208, 208],
];
const fixtures = () => TILES.map((rgb, i) => ({
  name: `tile_${i}.png`,
  mimeType: 'image/png',
  buffer: png(96, 96, () => rgb),
}));

// --- page helpers ------------------------------------------------------------

async function boot(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(fixtures());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // Tabs are labelled Layout / Settings — NOT Simple / Advanced (scar: an e2e
  // written against the internal state names finds no button and times out).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.getByRole('button', { name: 'Layout' }).first().click();
  await page.waitForTimeout(1400);
}

async function pickLook(page: Page, id: string) {
  await page.getByTestId(`look-${id}`).click();
  await page.waitForTimeout(1200);   // the still path debounces 50ms, then encodes a blob
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

// --- metrics -----------------------------------------------------------------

/** Mean R, G, B over a frame. The one statistic every prediction below reads. */
function channelMeans(a: number[]): [number, number, number] {
  let r = 0, g = 0, b = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) { r += a[i]; g += a[i + 1]; b += a[i + 2]; n++; }
  return [r / n, g / n, b / n];
}

/** Mean (max-min) over a frame — how much COLOUR there is, in 0..255. */
function meanChroma(a: number[]): number {
  let s = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) {
    s += Math.max(a[i], a[i + 1], a[i + 2]) - Math.min(a[i], a[i + 1], a[i + 2]);
    n++;
  }
  return s / n;
}

/** Mean R - B. Positive is a warm cast, negative a cool one. */
function warmth(a: number[]): number {
  let s = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) { s += a[i] - a[i + 2]; n++; }
  return s / n;
}

/** Spread of luma — how steep the curve is. */
function contrastSpread(a: number[]): number {
  const ys: number[] = [];
  for (let i = 0; i < a.length; i += 4) ys.push(0.213 * a[i] + 0.715 * a[i + 1] + 0.072 * a[i + 2]);
  const m = ys.reduce((x, y) => x + y, 0) / ys.length;
  return Math.sqrt(ys.reduce((x, y) => x + (y - m) ** 2, 0) / ys.length);
}

function maxAbsDiff(a: number[], b: number[]): number {
  let worst = 0;
  for (let i = 0; i < a.length; i += 4) {
    worst = Math.max(worst,
      Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
  }
  return worst;
}

function meanAbsDiff(a: number[], b: number[]): number {
  let sum = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) {
    sum += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]);
    n += 3;
  }
  return sum / n;
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
  await closeResult(page);
  return Buffer.concat(chunks).toString('utf8');
}

/** Rasterise an SVG STRING in the page and read its pixels — the real renderer. */
const rasteriseSvg = (page: Page, svg: string, N = 160): Promise<number[] | null> =>
  page.evaluate(async ({ svg, N }) => {
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    try {
      const img = new Image();
      await new Promise<void>((res, rej) => {
        img.onload = () => res();
        img.onerror = () => rej(new Error('svg failed to decode'));
        img.src = url;
      });
      const c = document.createElement('canvas'); c.width = N; c.height = N;
      const cx = c.getContext('2d', { willReadFrequently: true });
      if (!cx) return null;
      cx.drawImage(img, 0, 0, N, N);
      return Array.from(cx.getImageData(0, 0, N, N).data);
    } finally { URL.revokeObjectURL(url); }
  }, { svg, N });

// =============================================================================

test.describe('the look', () => {

  test('T1: it reaches the preview, and NONE gives back the exact picture', async ({ page }) => {
    await boot(page);

    const before = await previewBits(page);
    expect(before).not.toBeNull();

    await pickLook(page, 'punch');
    const graded = await previewBits(page);
    expect(graded).not.toBeNull();

    // It actually did something, and something LARGE — a grade that moves the
    // frame by a couple of levels is indistinguishable from JPEG noise.
    const moved = meanAbsDiff(before!, graded!);
    console.log(`T1 punch moved the preview by ${moved.toFixed(1)}/255 mean`);
    expect(moved).toBeGreaterThan(6);

    // THE NO-OP. Back to none, and the picture must be the one we started with.
    await pickLook(page, 'none');
    const back = await previewBits(page);
    expect(back).not.toBeNull();

    const residue = maxAbsDiff(before!, back!);
    console.log(`T1 residue after returning to NONE: ${residue}/255 worst channel`);
    // Zero, not "small": the same blob is re-encoded from the same instruction
    // stream, so any residue at all means `none` is not the no-op it claims.
    expect(residue).toBe(0);
  });

  test('T2: every chip is the look it says it is', async ({ page }) => {
    await boot(page);

    const base = await previewBits(page);
    expect(base).not.toBeNull();
    const baseChroma = meanChroma(base!);
    const baseWarmth = warmth(base!);
    const baseSpread = contrastSpread(base!);
    const baseLuma = channelMeans(base!).reduce((a, b) => a + b, 0) / 3;
    console.log(`T2 none: chroma ${baseChroma.toFixed(1)} warmth ${baseWarmth.toFixed(1)} ` +
      `spread ${baseSpread.toFixed(1)} luma ${baseLuma.toFixed(1)}`);

    // The fixture has to be colourful enough for a chroma claim to mean
    // anything. Asserted, not assumed — a fixture that drifted grey would make
    // every "colour goes down" test pass for the wrong reason.
    expect(baseChroma).toBeGreaterThan(40);

    const seen: Record<string, number[]> = { none: base! };

    for (const id of ['punch', 'faded', 'mono', 'noir', 'warm', 'cool', 'bleach']) {
      await pickLook(page, id);
      const bits = await previewBits(page);
      expect(bits, `${id} produced no preview`).not.toBeNull();
      seen[id] = bits!;
      console.log(`T2 ${id.padEnd(7)}: chroma ${meanChroma(bits!).toFixed(1)} ` +
        `warmth ${warmth(bits!).toFixed(1)} spread ${contrastSpread(bits!).toFixed(1)}`);
    }

    // Each claim, in the direction its own name makes.
    expect(meanChroma(seen.punch), 'punch must add colour').toBeGreaterThan(baseChroma + 4);
    expect(meanChroma(seen.faded), 'faded must pull colour back').toBeLessThan(baseChroma - 4);
    expect(meanChroma(seen.bleach), 'bleach must strip colour').toBeLessThan(baseChroma - 4);
    // JPEG chroma subsampling leaves a little colour at every edge, so the bar
    // for "colourless" is a level or two rather than zero.
    expect(meanChroma(seen.mono), 'mono must be colourless').toBeLessThan(6);
    expect(meanChroma(seen.noir), 'noir must be colourless').toBeLessThan(6);
    expect(contrastSpread(seen.noir), 'noir must steepen the curve').toBeGreaterThan(baseSpread + 2);
    // WARM AND COOL ARE MEASURED AGAINST EACH OTHER, not against the ungraded
    // frame — and that is a correction, not a weakening. Every other claim above
    // is MULTIPLICATIVE on whatever the deal contains (saturate scales the
    // chroma that is there, contrast scales the spread that is there), so a base
    // offset cannot flip it. A TONE is not: sepia washes the picture's own hues
    // out before the rotation turns what is left, so `cool` lands near a fixed
    // R-B regardless of what it started from — and on a deal that dealt itself
    // blue (this fixture's own base R-B has been measured from -9.7 to +9.7
    // across runs, and the tail is wider) `cool < base - 5` is arithmetic about
    // the RANDOM DEAL rather than about the grade. Caught in C3647 by the desk's
    // own axis test failing on exactly this, one run in eight.
    // The three claims below are each robust to the deal, and each for its own
    // reason. `warm` is a 30% BLEND toward a matrix whose output R-B is positive
    // for any input, so it can only raise R-B — measured at +14 over the
    // ungraded frame on deals whose own cast ranged from -17 to +10, and that
    // shift is the claim rather than a threshold. `cool` runs saturate 0.30
    // BEFORE its tone, so only 9% of the picture's own cast survives to compete
    // with a strong cool tone: its output is negative whatever it started from.
    // And the two ends being far apart is a claim about the axis, not the deal.
    // NOTE what is deliberately NOT asserted: that `warm`'s OUTPUT is positive.
    // At 30% tone it is not, on a deal that dealt itself blue (measured -2.6
    // against a base of -16.8) — the roster's warm is a lean, not a wash.
    const warmCast = warmth(seen.warm), coolCast = warmth(seen.cool);
    expect(warmCast - baseWarmth, 'warm must lean warm').toBeGreaterThan(5);
    expect(coolCast, 'cool must land cool whatever it started from').toBeLessThan(0);
    expect(warmCast - coolCast, 'warm and cool must be far apart').toBeGreaterThan(15);

    // AND NO TWO CHIPS MAY BE THE SAME GRADE. A roster with a duplicate looks
    // fine one chip at a time and is a broken picker.
    const ids = Object.keys(seen);
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const d = meanAbsDiff(seen[ids[i]], seen[ids[j]]);
        expect(d, `${ids[i]} and ${ids[j]} are the same picture (${d.toFixed(2)}/255)`).toBeGreaterThan(2);
      }
    }
  });

  test('T3: the export carries it — the worker thread, not the preview', async ({ page }) => {
    await boot(page);

    await exportAt(page, '2K');
    const plain = await exportBits(page);
    expect(plain).not.toBeNull();
    await closeResult(page);

    await pickLook(page, 'warm');
    await exportAt(page, '2K');
    const graded = await exportBits(page);
    expect(graded).not.toBeNull();
    await closeResult(page);

    const dWarmth = warmth(graded!) - warmth(plain!);
    console.log(`T3 export warmth shift: ${dWarmth.toFixed(1)}/255 ` +
      `(none ${warmth(plain!).toFixed(1)} -> warm ${warmth(graded!).toFixed(1)})`);
    // The file itself is warmer. If the worker ignored the look this is ~0.
    expect(dWarmth).toBeGreaterThan(5);

    // And it is the SAME shift the preview shows — the export is not merely
    // graded, it is graded the same amount. (Different resolutions and two
    // JPEG passes, so this is a direction-and-magnitude check, not equality.)
    const pv = await previewBits(page);
    await pickLook(page, 'none');
    const pvPlain = await previewBits(page);
    const dPreview = warmth(pv!) - warmth(pvPlain!);
    console.log(`T3 preview warmth shift: ${dPreview.toFixed(1)}/255`);
    expect(Math.abs(dWarmth - dPreview)).toBeLessThan(6);
  });

  test('T4: the SVG is the same grade as the raster', async ({ page }) => {
    await boot(page);

    const pvPlain = await previewBits(page);
    const svgPlain = await downloadSvg(page);

    await pickLook(page, 'warm');
    const pvWarm = await previewBits(page);
    const svgWarm = await downloadSvg(page);

    // The filter is really in the file, with the sRGB pin that makes it agree.
    expect(svgPlain, 'an ungraded SVG must carry no filter').not.toContain('<filter');
    expect(svgWarm).toContain('<filter id="look"');
    expect(svgWarm).toContain('color-interpolation-filters="sRGB"');
    expect(svgWarm).toContain('filter="url(#look)"');

    const rPlain = await rasteriseSvg(page, svgPlain);
    const rWarm = await rasteriseSvg(page, svgWarm);
    expect(rPlain).not.toBeNull();
    expect(rWarm).not.toBeNull();

    const svgShift = warmth(rWarm!) - warmth(rPlain!);
    const canvasShift = warmth(pvWarm!) - warmth(pvPlain!);
    console.log(`T4 warmth shift — svg ${svgShift.toFixed(1)}/255, canvas ${canvasShift.toFixed(1)}/255`);

    expect(svgShift, 'the SVG must actually be graded').toBeGreaterThan(5);
    // THE sRGB PROOF. The unit sweep measures a mean 29.5/255 divergence for
    // this look if the pin is dropped, so a 6-level bar here is an order of
    // magnitude inside the failure it is watching for.
    expect(Math.abs(svgShift - canvasShift),
      'the SVG and the canvas must be the same grade').toBeLessThan(6);
  });

  test('T5: the code carries it', async ({ page }) => {
    await boot(page);
    await pickLook(page, 'noir');

    const noirBits = await previewBits(page);
    const code = (await page.getByTestId('composition-code').first().innerText()).trim();
    console.log(`T5 code with noir: ${code}`);
    expect(code.length).toBeGreaterThan(8);

    // Open it as a RECIPIENT would: a cold page, then the same photographs.
    await page.goto(`${APP_URL}${APP_URL.includes('?') ? '&' : '?'}c=${encodeURIComponent(code)}`);
    await page.locator('input[type="file"]').first().setInputFiles(fixtures());
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(1800);

    await expect(page.getByTestId('look-noir')).toHaveAttribute('data-active', 'true');
    const reopened = await previewBits(page);
    expect(reopened).not.toBeNull();
    // Colourless, exactly as noir claims — proving the grade travelled, not
    // merely that a chip lit up.
    console.log(`T5 reopened chroma ${meanChroma(reopened!).toFixed(1)}`);
    expect(meanChroma(reopened!)).toBeLessThan(6);
    expect(meanAbsDiff(noirBits!, reopened!)).toBeLessThan(3);
  });

  test('T6: the row is watertight on a phone', async ({ page }) => {
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await boot(page);
      await pickLook(page, 'bleach');

      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollW,
        `horizontal overflow at ${w}px: ${overflow.scrollW} > ${overflow.clientW}`)
        .toBeLessThanOrEqual(overflow.clientW);

      // Every chip is reachable and big enough for a thumb, and none of them
      // spills out of the dock that holds them.
      // NINE since THE DESK: the eight looks and the ADJUST door beside them.
      // The count is asserted rather than "at least eight" on purpose — a chip
      // that quietly appears in this row is a chip nobody measured at 320px.
      const chips = page.locator('[data-testid^="look-"]');
      const n = await chips.count();
      expect(n).toBe(9);
      const dock = await page.locator('.ui-looks').first().boundingBox();
      expect(dock).not.toBeNull();
      for (let i = 0; i < n; i++) {
        const box = await chips.nth(i).boundingBox();
        expect(box, `chip ${i} has no box at ${w}px`).not.toBeNull();
        expect(box!.height, `chip ${i} is ${box!.height}px tall at ${w}px`).toBeGreaterThanOrEqual(44);
        expect(box!.width, `chip ${i} is ${box!.width}px wide at ${w}px`).toBeGreaterThanOrEqual(44);
        expect(box!.x + box!.width,
          `chip ${i} spills past the dock at ${w}px`).toBeLessThanOrEqual(dock!.x + dock!.width + 1);
      }
    }
  });
});
