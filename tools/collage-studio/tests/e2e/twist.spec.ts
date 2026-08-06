/**
 * TWIST AT THE ARTIFACT — the per-fragment lean, proved on PIXELS.
 *
 * From wishing-well 253b1ba7 (anonymous): *"Also maybe twisting capabilities…"* —
 * the half of that wish that was deliberately NOT shipped with Composition,
 * because it is the first change that has to reach the hot draw loop AND all
 * three export paths, so it was owed its own increment and its own proof.
 *
 * The pure geometry is swept in tests/unit/twist.invariants.mjs (79,200 corner
 * containments, the minimality of the expansion, the bit-identical untwisted
 * path). Three things live only out here:
 *
 *   T1  THE CHIP REACHES THE PIXELS, and the four modes are four PICTURES.
 *       A picker whose entries render the same image is a lie in the UI.
 *
 *   T2  THE CORNERS DO NOT OPEN UP. This is the whole reason the rotation is
 *       applied to the SAMPLING rather than to the cell, and it is the one
 *       failure a screenshot review would wave through: solid white tiles on a
 *       near-black background, and the share of background pixels must not grow
 *       when the twist comes on. If the destination rect is not expanded by
 *       |cos|+|sin|, four dark wedges appear in every fragment and this fails.
 *
 *   T3  THE EXPORT CARRIES IT. Twice now a composition feature has reached the
 *       preview and not the downloaded file (previewSrc-vs-src, then crop focus)
 *       because an export path rebuilt its own asset list. A preview-only suite
 *       cannot see that class of defect, so this one renders a real export and
 *       asks which preview it matches.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.twist.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.twist.config.ts
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

/**
 * BARRED tiles. Horizontal bands are the fixture a rotation is visible in: a
 * solid tile looks identical at every angle, which would make a build that
 * ignores twist entirely pass T1 and T3.
 */
const barred = (n = 10) => Array.from({ length: n }, (_, i) => {
  const hue: [number, number, number][] = [
    [236, 72, 60], [60, 200, 236], [250, 210, 70], [130, 240, 130],
    [220, 120, 250], [255, 150, 60], [90, 140, 250], [250, 250, 250],
    [70, 230, 200], [250, 90, 170],
  ];
  const [r, g, b] = hue[i % hue.length];
  return {
    name: `bars_${i}.png`,
    mimeType: 'image/png',
    buffer: png(128, 128, (_x, y) => (Math.floor(y / 8) % 2 === 0 ? [r, g, b] : [16, 16, 20])),
  };
});

/**
 * SOLID, near-white tiles. For the coverage proof only: every pixel a fragment
 * can possibly draw is bright, so any dark pixel inside the collage is
 * background showing through — which is the exact defect being tested for, and
 * nothing else can produce it.
 */
const solids = (n = 10) => Array.from({ length: n }, (_, i) => ({
  name: `solid_${i}.png`,
  mimeType: 'image/png',
  // Each file a slightly different white, so the fill sees ten distinct sources.
  buffer: png(96, 96, () => [250 - i, 250 - i, 252 - i] as [number, number, number]),
}));

// --- page helpers ------------------------------------------------------------

async function boot(page: Page, files: { name: string; mimeType: string; buffer: Buffer }[]) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(files);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // The tabs are labelled Layout / Settings — NOT Simple / Advanced (scar: an
  // e2e written against the internal state names finds no button and times out).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  // An even grid with full coverage, so "background pixel" means what it says.
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.waitForTimeout(1400);
}

async function pickTwist(page: Page, label: string) {
  await page.getByRole('group', { name: 'Twist' }).getByRole('button', { name: label, exact: true }).click();
  await page.waitForTimeout(1100);   // the still path debounces 50ms then encodes a blob
}

/** The on-screen preview, downsampled to N x N and returned as raw RGBA. */
const previewBits = (page: Page, N = 128): Promise<number[] | null> =>
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
const exportBits = (page: Page, N = 128): Promise<number[] | null> =>
  page.evaluate((N) => {
    const img = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    if (!img || !img.naturalWidth) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(img, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

/** Mean absolute per-channel difference, 0..255. */
function meanDiff(a: number[], b: number[]): number {
  let sum = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) {
    sum += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]);
    n += 3;
  }
  return sum / n;
}

/** Share of sampled pixels dark enough to only be the background. */
function darkShare(a: number[]): number {
  let dark = 0, n = 0;
  for (let i = 0; i < a.length; i += 4) {
    if (a[i] * 0.299 + a[i + 1] * 0.587 + a[i + 2] * 0.114 < 40) dark++;
    n++;
  }
  return dark / n;
}

async function exportAt(page: Page, label: string) {
  await page.getByRole('button', { name: 'Export' }).first().click();
  await expect(page.getByRole('dialog').filter({ hasText: 'Export' }).first()).toBeVisible();
  await page.getByRole('radio', { name: new RegExp(`^${label}`) }).click();
  await page.getByRole('button', { name: new RegExp(`^Render ${label} JPG`) }).click();
  await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 90_000 });
}

const MODES = ['Tilt', 'Scatter', 'Pinwheel', 'Cascade'];

// =============================================================================

test.describe('twist (wish 253b1ba7: "twisting capabilities")', () => {

  test('T1: every chip moves the picture, and no two chips are the same picture', async ({ page }) => {
    await boot(page, barred());

    const shots: Record<string, number[]> = {};
    await pickTwist(page, 'Straight');
    const straight = await previewBits(page);
    expect(straight).not.toBeNull();

    for (const m of MODES) {
      await pickTwist(page, m);
      const bits = await previewBits(page);
      expect(bits, `${m} produced no preview`).not.toBeNull();
      shots[m] = bits!;
      // A twist re-samples every fragment through a rotation; on barred tiles
      // that is a large, unmistakable change. 6/255 mean is roughly "you can
      // see it from across the room" and is far above JPEG shimmer.
      expect(meanDiff(straight!, bits!), `${m} barely changed the picture`).toBeGreaterThan(6);
    }

    for (let i = 0; i < MODES.length; i++) {
      for (let j = i + 1; j < MODES.length; j++) {
        expect(
          meanDiff(shots[MODES[i]], shots[MODES[j]]),
          `${MODES[i]} and ${MODES[j]} render the same picture — one is a dead chip`,
        ).toBeGreaterThan(3);
      }
    }
  });

  test('T2: the corners do not open up — a twist must not show background', async ({ page }) => {
    await boot(page, solids());

    await pickTwist(page, 'Straight');
    const base = await previewBits(page);
    expect(base).not.toBeNull();
    const baseDark = darkShare(base!);

    for (const m of MODES) {
      await pickTwist(page, m);
      const bits = await previewBits(page);
      expect(bits).not.toBeNull();
      const dark = darkShare(bits!);
      // THE ASSERTION. Unexpanded, a 15-degree twist opens a wedge at all four
      // corners of every fragment — several percent of the frame turns
      // background-coloured. One point of slack covers resampling at the cell
      // edges; the defect is an order of magnitude bigger than that.
      expect(dark, `${m} leaked background: ${(baseDark * 100).toFixed(2)}% -> ${(dark * 100).toFixed(2)}%`)
        .toBeLessThan(baseDark + 0.01);
    }
  });

  test('T3: the exported FILE carries the twist, not the straight crop', async ({ page }) => {
    await boot(page, barred());

    await pickTwist(page, 'Straight');
    const straightPreview = await previewBits(page);
    await pickTwist(page, 'Scatter');
    const twistedPreview = await previewBits(page);
    expect(straightPreview).not.toBeNull();
    expect(twistedPreview).not.toBeNull();

    await exportAt(page, '2K');
    const exported = await exportBits(page);
    expect(exported).not.toBeNull();

    // A RELATIVE test, deliberately. The export is a different renderer at a
    // different resolution through a different encoder, so it never matches a
    // preview exactly — but it must be CLOSER to the preview it was asked for
    // than to the one it was not. An export that rebuilt its own asset list and
    // dropped the twist inverts this, and nothing else does.
    const dSame = meanDiff(twistedPreview!, exported!);
    const dCross = meanDiff(straightPreview!, exported!);
    expect(
      dSame,
      `the exported file matches the STRAIGHT preview (${dCross.toFixed(1)}) better than the ` +
      `twisted one (${dSame.toFixed(1)}) — the twist did not reach the export path`,
    ).toBeLessThan(dCross);
  });

  test('T4: a POSITION-KEYED twist reaches the export too', async ({ page }) => {
    // T3 drives Scatter, whose angle is a hash of the slot seed and therefore
    // the ONE mode that does not care where its fragment sits. A geometry-keyed
    // mode takes a different route — the angle is re-derived at export time
    // against the layout the export actually computed (App.tsx retwistFor),
    // because `computeLayout` is not scale-invariant and the export recomputes
    // its own. So Scatter passing says nothing about Cascade, and this is the
    // blind spot an adversarial audit named before it could become a scar.
    //
    // The assertion is deliberately the ROBUST one rather than the symmetrical
    // one T3 uses: on the ~11% of seeds where the export's layout genuinely
    // bifurcates from the preview's, the whole partition differs and a
    // "closer to which preview" comparison is not a statement about twist at
    // all. "The exported file is not a STRAIGHT render" is true either way, and
    // it is exactly what fails if the angle never reaches the export.
    await boot(page, barred());

    await pickTwist(page, 'Straight');
    const straightPreview = await previewBits(page);
    expect(straightPreview).not.toBeNull();

    await pickTwist(page, 'Cascade');
    await exportAt(page, '2K');
    const exported = await exportBits(page);
    expect(exported).not.toBeNull();

    const d = meanDiff(straightPreview!, exported!);
    expect(
      d,
      `the 2K export is indistinguishable from a straight render (${d.toFixed(1)}) — ` +
      `Cascade never reached the export path`,
    ).toBeGreaterThan(6);
  });
});
