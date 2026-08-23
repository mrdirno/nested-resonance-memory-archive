/**
 * THE DESK AT THE ARTIFACT — the grade as four axes, proved on PIXELS.
 *
 * The arithmetic is swept in tests/unit/grade.invariants.mjs (71,095 checks:
 * all eight looks round-tripping through the desk bit for bit, 1,812 reachable
 * desks on the grid `num` is exact on and inside the range CSS Filter Effects
 * defines, the two emitters denoting ONE transform on grades that are NOT on
 * the roster, and the codec's optional group). Six things can only be proved
 * out here, in a browser, against real pixels:
 *
 *   T1  OPENING THE DESK MOVES NO PIXEL. Every look is a POINT in this space,
 *       so tapping ADJUST on a graded collage must show you where the preset
 *       already is — bit for bit, not "close". This is the property the whole
 *       feature rests on: a person drags ONE axis, and a desk that restated the
 *       preset on the way in would change three things they did not touch.
 *
 *   T2  EACH AXIS MOVES THE PICTURE IN THE DIRECTION IT NAMES. Four axes, four
 *       independent statistics — luma, spread, chroma, R-B. A desk whose
 *       sliders are wired to the wrong fields passes every "did it change?"
 *       assertion ever written and fails this one.
 *
 *   T3  THE EXPORT CARRIES A CUSTOM GRADE. The export is a WORKER on another
 *       thread, and it used to receive a roster ID; it now receives the five
 *       numbers themselves across a structured clone. Three times in this
 *       codebase a composition feature reached the preview and not the file.
 *
 *   T4  THE SVG CARRIES IT TOO, and is the SAME grade as the raster. The vector
 *       path emits real `<filter>` primitives from the same pipeline; sRGB is
 *       pinned there for grades that are on no roster exactly as for the eight.
 *
 *   T5  THE CODE CARRIES IT. A custom grade is the most recipe-shaped thing in
 *       the app. Round-tripped through the real strip, on the real page — and
 *       the pixels are compared, not just the readouts.
 *
 *   T6  IT IS WATERTIGHT ON A PHONE with the panel OPEN — the state a screenshot
 *       of the closed dock cannot see. Nine chips now, and four 44px ranges.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.desk.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.desk.config.ts
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


// --- the desk's own helpers --------------------------------------------------

/** Open the ADJUST panel. Idempotent: it is a toggle, so only open if closed. */
async function openDesk(page: Page) {
  const chip = page.getByTestId('look-desk');
  if ((await chip.getAttribute('aria-expanded')) !== 'true') await chip.click();
  await expect(page.getByTestId('desk-panel')).toBeVisible();
}

/**
 * Set ONE axis and wait for the still path.
 *
 * `fill` on a range input is how Playwright moves a slider without simulating a
 * drag; the value must land on the control's own step or it is rejected as
 * "Malformed value" (the scar THE SPEED's spec records) — every value below is
 * on the 0.01 grid the desk snaps to anyway.
 */
async function setAxis(page: Page, key: string, value: number) {
  await page.getByTestId(`desk-${key}`).fill(String(value));
  await page.waitForTimeout(1200);
}

/** Mean luma over a frame — the statistic EXPOSURE is about. */
function luma(a: number[]): number {
  let s = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) { s += 0.213 * a[i] + 0.715 * a[i + 1] + 0.072 * a[i + 2]; n++; }
  return s / n;
}

test.describe('the desk', () => {

  test('T1: opening the desk on a graded collage moves no pixel', async ({ page }) => {
    await boot(page);
    // WARM is the strongest test of this: it is the only roster look whose
    // warmth axis is neither zero nor an endpoint (sepia 0.30 = +0.5), so a
    // desk that seeded from anything but the preset's own numbers would show.
    await pickLook(page, 'warm');
    const before = await previewBits(page);
    expect(before).not.toBeNull();

    await openDesk(page);
    await page.waitForTimeout(1200);
    const after = await previewBits(page);
    expect(after).not.toBeNull();

    const worst = maxAbsDiff(before!, after!);
    console.log(`T1 opening the desk: worst channel delta ${worst}/255`);
    expect(worst, 'opening the desk restated the grade').toBe(0);

    // And it says WARM's own numbers back: +3% exposure, +5% contrast,
    // +35% colour, WARM 50% — read off the page, not off the roster.
    await expect(page.getByTestId('desk-read-exposure')).toHaveText('+3%');
    await expect(page.getByTestId('desk-read-contrast')).toHaveText('+5%');
    await expect(page.getByTestId('desk-read-colour')).toHaveText('+35%');
    await expect(page.getByTestId('desk-read-warmth')).toHaveText('WARM 50%');
    // Still the preset until an axis actually moves: the chip row may not say
    // CUSTOM for a picture that is exactly one of the eight.
    await expect(page.getByTestId('look-warm')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('look-desk')).toHaveAttribute('aria-pressed', 'false');
  });

  test('T2: every axis moves the picture in the direction it names', async ({ page }) => {
    await boot(page);
    await openDesk(page);
    const base = await previewBits(page);
    expect(base).not.toBeNull();
    const b = {
      luma: luma(base!), spread: contrastSpread(base!),
      chroma: meanChroma(base!), warm: warmth(base!),
    };
    console.log(`T2 base  luma ${b.luma.toFixed(1)} spread ${b.spread.toFixed(1)} ` +
      `chroma ${b.chroma.toFixed(1)} R-B ${b.warm.toFixed(1)}`);

    // EXPOSURE — brighter, and nothing else claimed.
    await setAxis(page, 'exposure', 1.4);
    let bits = await previewBits(page);
    const up = luma(bits!);
    console.log(`T2 exposure 1.4 -> luma ${up.toFixed(1)} (was ${b.luma.toFixed(1)})`);
    expect(up, 'exposure up must raise mean luma').toBeGreaterThan(b.luma + 12);
    await setAxis(page, 'exposure', 0.7);
    bits = await previewBits(page);
    const down = luma(bits!);
    console.log(`T2 exposure 0.7 -> luma ${down.toFixed(1)}`);
    expect(down, 'exposure down must lower mean luma').toBeLessThan(b.luma - 12);
    await setAxis(page, 'exposure', 1);

    // CONTRAST — the curve, measured as the spread of luma.
    await setAxis(page, 'contrast', 1.5);
    bits = await previewBits(page);
    const steep = contrastSpread(bits!);
    console.log(`T2 contrast 1.5 -> spread ${steep.toFixed(1)} (was ${b.spread.toFixed(1)})`);
    expect(steep, 'contrast up must widen the luma spread').toBeGreaterThan(b.spread + 4);
    await setAxis(page, 'contrast', 1);

    // COLOUR — all the way down is black and white.
    await setAxis(page, 'colour', 0);
    bits = await previewBits(page);
    const grey = meanChroma(bits!);
    console.log(`T2 colour 0 -> chroma ${grey.toFixed(1)} (was ${b.chroma.toFixed(1)})`);
    expect(grey, 'colour at zero must be black and white').toBeLessThan(6);
    await setAxis(page, 'colour', 1);

    // WARMTH — bipolar, and measured as ONE END AGAINST THE OTHER rather than
    // against the ungraded frame. That is not a softer claim, it is the correct
    // one: a tone REPLACES the picture's own cast rather than adding to it (a
    // sepia washes the hues out before the rotation turns what is left), so on
    // a deal that happens to be blue-dominant the cool end can be LESS blue
    // than the ungraded frame while still being the cool end of the axis. The
    // deal is random — this fixture's own R-B ranges over ~40/255 between runs
    // — and a threshold measured off it is a test that fails on Tuesday.
    // Comparing the two ends is invariant to the deal, and the SIGNS below are
    // the absolute half: at |0.8| the tone dominates whatever was there.
    await setAxis(page, 'warmth', 0.8);
    bits = await previewBits(page);
    const hot = warmth(bits!);
    await setAxis(page, 'warmth', -0.8);
    bits = await previewBits(page);
    const cold = warmth(bits!);
    console.log(`T2 warmth +0.8 -> R-B ${hot.toFixed(1)}, -0.8 -> R-B ${cold.toFixed(1)} ` +
      `(ungraded ${b.warm.toFixed(1)})`);
    expect(hot - cold, 'the two ends of the warmth axis must be far apart').toBeGreaterThan(20);
    // The warm end is a claim about a SHIFT (a tone can only raise R-B), the
    // cool end a claim about an ABSOLUTE (its saturate runs first, so 9% of the
    // picture's own cast survives to argue with the tone). Neither is a
    // threshold read off one lucky deal — see look.spec T2 for the same pair.
    expect(hot - b.warm, 'the warm end must lean warm').toBeGreaterThan(8);
    expect(cold, 'the cool end must land cool whatever it started from').toBeLessThan(0);

    // ...and the row now says CUSTOM, because the picture is on no roster.
    await expect(page.getByTestId('look-desk')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('look-none')).toHaveAttribute('aria-pressed', 'false');

    // BACK TO NONE returns the exact opening picture — the no-op rule, reached
    // through the desk's own reset rather than through the chip row.
    await page.getByTestId('desk-reset').click();
    await page.waitForTimeout(1400);
    const restored = await previewBits(page);
    const worst = maxAbsDiff(base!, restored!);
    console.log(`T2 reset -> worst channel delta ${worst}/255`);
    expect(worst, 'the reset must give back the exact ungraded picture').toBe(0);
    await expect(page.getByTestId('look-desk')).toHaveAttribute('aria-pressed', 'false');
  });

  test('T3: the export carries a custom grade — the worker thread, not the preview', async ({ page }) => {
    await boot(page);
    await openDesk(page);
    const plain = await previewBits(page);

    await setAxis(page, 'colour', 0);
    await setAxis(page, 'contrast', 1.45);
    await setAxis(page, 'exposure', 0.9);
    const onScreen = await previewBits(page);
    expect(meanChroma(onScreen!), 'the preview should be black and white').toBeLessThan(6);

    // '2K' is the roster's own first row (PRESETS in ExportDialog) — the label
    // the dialog actually renders, not a size a test wished for.
    await exportAt(page, '2K');
    const file = await exportBits(page);
    expect(file).not.toBeNull();
    const fileChroma = meanChroma(file!);
    const plainChroma = meanChroma(plain!);
    console.log(`T3 exported chroma ${fileChroma.toFixed(1)} vs ungraded ${plainChroma.toFixed(1)}`);
    // The FILE is monochrome, and the ungraded fixture is not — so the assertion
    // is not vacuous on a fixture that happens to be grey.
    expect(plainChroma, 'the fixture must have colour for this to mean anything').toBeGreaterThan(30);
    expect(fileChroma, 'the exported file lost the custom grade').toBeLessThan(8);
    // ...and it is the SAME grade the preview showed, not merely also grey.
    expect(Math.abs(luma(file!) - luma(onScreen!)),
      'the file and the preview are different grades').toBeLessThan(12);
    await closeResult(page);
  });

  test('T4: the SVG is the same custom grade as the raster', async ({ page }) => {
    await boot(page);
    await openDesk(page);
    await setAxis(page, 'warmth', -0.9);
    await setAxis(page, 'colour', 0.4);

    const canvasBits = await previewBits(page);
    const svg = await downloadSvg(page);
    expect(svg, 'the SVG must carry a filter for a grade on no roster').toContain('<filter');
    expect(svg).toContain('color-interpolation-filters="sRGB"');
    const svgBits = await rasteriseSvg(page, svg);
    expect(svgBits).not.toBeNull();

    const c = warmth(canvasBits!), v = warmth(svgBits!);
    console.log(`T4 cast: canvas R-B ${c.toFixed(1)}, svg R-B ${v.toFixed(1)}`);
    // Both cool, and by the same amount. The sRGB pin is what makes the second
    // half true; dropping it moves them ~29/255 apart (grade.invariants I9).
    expect(c, 'the canvas should be cool').toBeLessThan(-4);
    expect(Math.abs(c - v), 'the SVG is a different grade from the canvas').toBeLessThan(8);
  });

  test('T5: the code carries a custom grade', async ({ page }) => {
    await boot(page);
    await openDesk(page);
    await setAxis(page, 'exposure', 1.3);
    await setAxis(page, 'warmth', 0.7);
    await setAxis(page, 'colour', 0.5);
    const madeBits = await previewBits(page);
    const madeWarm = warmth(madeBits!);

    const code = (await page.getByTestId('composition-code').innerText()).trim();
    console.log(`T5 code ${code}`);
    expect(code.length, 'a custom grade must lengthen the middle group').toBeGreaterThan(0);

    // Away from it — a different look entirely — then back via the real box.
    await pickLook(page, 'mono');
    await expect(page.getByTestId('look-desk')).toHaveAttribute('aria-pressed', 'false');
    expect(meanChroma((await previewBits(page))!), 'mono should be grey').toBeLessThan(6);

    await page.getByTestId('composition-code-input').fill(code);
    await page.getByTestId('composition-code-open').click();
    await page.waitForTimeout(1600);

    await expect(page.getByTestId('look-desk')).toHaveAttribute('aria-pressed', 'true');
    await openDesk(page);
    await expect(page.getByTestId('desk-read-exposure')).toHaveText('+30%');
    await expect(page.getByTestId('desk-read-warmth')).toHaveText('WARM 70%');
    const back = await previewBits(page);
    console.log(`T5 R-B made ${madeWarm.toFixed(1)} reopened ${warmth(back!).toFixed(1)}`);
    expect(meanAbsDiff(madeBits!, back!), 'the code opened a different picture').toBeLessThan(3);
  });

  test('T6: the panel is watertight on a phone', async ({ page }) => {
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await boot(page);
      await openDesk(page);
      await setAxis(page, 'warmth', -1);

      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollW,
        `horizontal overflow at ${w}px with the desk open: ${overflow.scrollW} > ${overflow.clientW}`)
        .toBeLessThanOrEqual(overflow.clientW);

      const dock = await page.locator('.ui-looks').first().boundingBox();
      expect(dock).not.toBeNull();

      // The nine chips — eight looks and the door.
      const chips = page.locator('[data-testid^="look-"]');
      expect(await chips.count()).toBe(9);
      for (let i = 0; i < 9; i++) {
        const box = await chips.nth(i).boundingBox();
        expect(box, `chip ${i} has no box at ${w}px`).not.toBeNull();
        expect(box!.height, `chip ${i} is ${box!.height}px tall at ${w}px`).toBeGreaterThanOrEqual(44);
        expect(box!.x + box!.width,
          `chip ${i} spills past the dock at ${w}px`).toBeLessThanOrEqual(dock!.x + dock!.width + 1);
      }

      // ...and the four ranges the panel discloses. A range is only a tap target
      // if the thumb is: the app styles them at 44px and this is what holds it.
      for (const ax of ['exposure', 'contrast', 'colour', 'warmth']) {
        const box = await page.getByTestId(`desk-${ax}`).boundingBox();
        expect(box, `${ax} has no box at ${w}px`).not.toBeNull();
        expect(box!.height, `${ax} is ${box!.height}px tall at ${w}px`).toBeGreaterThanOrEqual(44);
        expect(box!.x + box!.width,
          `${ax} spills past the dock at ${w}px`).toBeLessThanOrEqual(dock!.x + dock!.width + 1);
      }
      const reset = await page.getByTestId('desk-reset').boundingBox();
      expect(reset!.height, `the reset is ${reset!.height}px tall at ${w}px`).toBeGreaterThanOrEqual(44);
    }
  });
});
