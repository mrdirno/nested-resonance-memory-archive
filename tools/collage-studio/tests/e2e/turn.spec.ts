/**
 * THE TURN AT THE ARTIFACT — proved on PIXELS, on a real browser.
 *
 * The arithmetic is swept in tests/unit/turn.invariants.mjs (13 invariants:
 * 65,600 assignments proved to be PERMUTATIONS across five modes, n=1..64 and
 * forty consecutive turns; rest by reference; the codec round trip; and the
 * pre-turn 20-character code still opening as `hold`). Five things can only be
 * proved out here:
 *
 *   T1  THE WALL ACTUALLY RE-CUTS. A sweep can prove the assignment is a
 *       function of time; only a browser can prove the function is being CALLED
 *       and that the pictures the compositor binds actually follow it. The
 *       Stage's tick is demand-driven — a photos-only scene "draws once and
 *       stops" — so a turn that reached the schedule and not the loop would be
 *       a still collage with an immaculate permutation nobody ever sees.
 *
 *   T2  AND `hold` DOES NOT. The control. Without it, T1 measures "the app is
 *       noisy" rather than "the turn turned".
 *
 *   T3  NOBODY IS DUPLICATED, ON REAL PIXELS. This is the promise the whole
 *       design is built around, and the fixture is what makes it observable:
 *       six photographs, six unmistakable hues, one fragment each. Count the
 *       hues on the canvas before a turn and after one — six both times. If a
 *       permutation broke, a hue would VANISH (something else would be showing
 *       twice), and this is the check that sees it.
 *
 *   T4  THE STILL SURFACES ARE UNTOUCHED. The exported PICTURE is drawn by a
 *       worker on another thread that passes no time at all, so a turn must not
 *       shift it by one channel. `NO_TURN` is returned by reference at t=0 for
 *       exactly this reason, and this is the check that would catch it leaking.
 *
 *   T5  THE CODE CARRIES IT. A turn is part of the recipe — "these fragments,
 *       dealt this way, re-cutting like this" — so it must survive being sent.
 *
 *   T6  IT IS WATERTIGHT ON A PHONE. Five more chips on a 320px screen, and the
 *       operator's law is that nothing clips or alters when zoomed out.
 *
 * THE FIXTURE IS THE MEASUREMENT, AND IT IS THE OPPOSITE FIXTURE TO THE MOVE'S.
 * A move is proved with steep ramps, because it changes WHICH PART of one photo
 * a fragment samples. A turn changes WHICH PHOTO, so it is proved with six
 * flat, maximally-separated hues: any fragment is one identifiable photograph
 * at a glance, and "the same six are on screen" is a countable fact rather than
 * a percentage.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.turn.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.turn.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

// --- fixtures ----------------------------------------------------------------

function png(w: number, h: number, pixel: (x: number, y: number) => [number, number, number]): Buffer {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  let o = 0;
  for (let y = 0; y < h; y++) {
    raw[o++] = 0;
    for (let x = 0; x < w; x++) {
      const [r, g, b] = pixel(x, y);
      raw[o++] = r; raw[o++] = g; raw[o++] = b;
    }
  }
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const body = Buffer.concat([Buffer.from(type, 'ascii'), data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(body) >>> 0);
    return Buffer.concat([len, body, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

let CRC_TABLE: number[] | null = null;
function crc32(buf: Buffer): number {
  if (!CRC_TABLE) {
    CRC_TABLE = [];
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      CRC_TABLE[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

/**
 * SIX HUES, AS FAR APART AS RGB GOES, each with a gentle luminance ramp so the
 * crop still has something to sample and the JPEG has something to encode.
 * These are the prototypes `hueCensus` classifies against — change one here and
 * change it there.
 */
const HUES: [number, number, number][] = [
  [235, 30, 30],    // red
  [30, 220, 60],    // green
  [40, 70, 240],    // blue
  [240, 215, 35],   // yellow
  [225, 45, 225],   // magenta
  [35, 215, 225],   // cyan
];

const fixtures = () => HUES.map((rgb, i) => ({
  name: `hue-${i}.png`,
  mimeType: 'image/png',
  buffer: png(320, 320, (x, y) => {
    const t = 0.72 + 0.28 * ((x + y) / (319 * 2));
    return [
      Math.round(rgb[0] * t),
      Math.round(rgb[1] * t),
      Math.round(rgb[2] * t),
    ] as [number, number, number];
  }),
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
  await page.waitForTimeout(1600);
}

async function pickTurn(page: Page, id: string) {
  await page.getByTestId(`turn-${id}`).click();
  // The still path debounces then encodes a blob; the live path has to mount a
  // Stage, decode every still and land its first frame.
  await page.waitForTimeout(1800);
}

/** The artwork, downsampled to N x N as raw RGBA. The LARGEST canvas, because a
 *  turning collage mounts the Stage and the page carries smaller canvases. */
const artBits = (page: Page, N = 150): Promise<number[] | null> =>
  page.evaluate((N) => {
    const canvases = Array.from(document.querySelectorAll('canvas')) as HTMLCanvasElement[];
    let el: CanvasImageSource | null = null;
    let best = 0;
    for (const c of canvases) {
      const a = c.width * c.height;
      if (a > best) { best = a; el = c; }
    }
    if (!el) el = document.querySelector('img[src^="blob:"]') as HTMLImageElement | null;
    if (!el) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(el, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

/** The EXPORTED file's own pixels — never the preview. */
const exportBits = (page: Page, N = 150): Promise<number[] | null> =>
  page.evaluate((N) => {
    const img = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    if (!img || !img.naturalWidth) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(img, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

/** Share of samples that differ by more than `tol`, and the worst difference. */
function diff(a: number[], b: number[], tol = 6): { moved: number; worst: number } {
  let moved = 0; let worst = 0; let n = 0;
  for (let i = 0; i < a.length; i += 4) {
    const d = Math.max(
      Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]),
    );
    if (d > tol) moved++;
    if (d > worst) worst = d;
    n++;
  }
  return { moved: moved / n, worst };
}

/**
 * HOW MANY OF THE SIX PHOTOGRAPHS ARE ON THE CANVAS.
 *
 * Every sample is assigned to its nearest hue prototype, and a hue counts as
 * PRESENT once it owns at least 4% of the classified samples — well under the
 * ~16% an equal-area six-way split would give each, and well over the leakage a
 * dark background, a hairline or a cross-dissolve contributes. Unclassifiable
 * samples (the background, and any sample mid-dissolve that sits between two
 * prototypes) are simply not counted, which is why this is a census of what is
 * VISIBLE rather than a partition of the frame.
 */
function hueCensus(bits: number[], protos: [number, number, number][]): { present: number; shares: number[] } {
  const owned = new Array(protos.length).fill(0);
  let classified = 0;
  for (let i = 0; i < bits.length; i += 4) {
    const r = bits[i], g = bits[i + 1], b = bits[i + 2];
    // Ignore anything too dark to carry a hue: the background, and the gutters.
    if (r + g + b < 90) continue;
    let best = -1; let bestD = Infinity;
    for (let p = 0; p < protos.length; p++) {
      const [pr, pg, pb] = protos[p];
      // Compare DIRECTION, not brightness — every fixture carries a luminance
      // ramp, and a crop of its dark corner is the same photograph.
      const n1 = Math.hypot(r, g, b) || 1;
      const n2 = Math.hypot(pr, pg, pb) || 1;
      const d = Math.hypot(r / n1 - pr / n2, g / n1 - pg / n2, b / n1 - pb / n2);
      if (d < bestD) { bestD = d; best = p; }
    }
    if (best < 0 || bestD > 0.22) continue;   // between two hues: mid-dissolve
    owned[best]++;
    classified++;
  }
  const shares = owned.map((o) => (classified ? o / classified : 0));
  return { present: shares.filter((s) => s >= 0.04).length, shares };
}

async function openSheet(page: Page) {
  await page.getByRole('button', { name: /export/i }).first().click();
  await page.locator('[aria-label="Export size"]').waitFor({ timeout: 30_000 });
}

async function closeSheet(page: Page) {
  await page.locator('[role="dialog"][aria-labelledby="export-title"]')
    .getByRole('button', { name: 'Close', exact: true }).click();
  await expect(page.locator('[aria-label="Export size"]')).toHaveCount(0, { timeout: 15_000 });
}

async function renderPicture(page: Page) {
  await openSheet(page);
  await page.getByRole('button', { name: /^Render .* JPG$/ }).first().click();
  await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 150_000 });
  await page.waitForFunction(() => {
    const i = document.querySelector('img[alt="Rendered collage"]') as HTMLImageElement | null;
    return !!i && i.complete && i.naturalWidth > 0;
  }, undefined, { timeout: 150_000 });
}

async function closeResult(page: Page) {
  await page.getByRole('button', { name: 'Close', exact: true }).last().click();
  await expect(page.locator('img[alt="Rendered collage"]')).toHaveCount(0, { timeout: 15_000 });
}

/**
 * THE BAR. A turn re-points whole fragments at whole photographs, so it moves a
 * far larger share of the frame than a crop drift ever does — the floor here is
 * deliberately well under a measured run rather than a taste-picked number, and
 * `hold` is asserted on the other side of the same measurement.
 */
const MIN_TURNED_SHARE = 0.08;

// =============================================================================

test.describe('THE TURN', () => {
  test('T1/T2 the collage re-cuts when asked, and holds when not', async ({ page }) => {
    await boot(page);

    // AT REST — `hold` is the boot state. Two samples five seconds apart must be
    // the same frame. Five, not one: the fastest turn's hold is 3.5s, so a
    // shorter window would pass even if `hold` were quietly turning.
    const rest0 = await artBits(page);
    expect(rest0).not.toBeNull();
    await page.waitForTimeout(5200);
    const rest1 = await artBits(page);
    const held = diff(rest0!, rest1!);
    console.log(`[turn] hold: moved ${(held.moved * 100).toFixed(2)}%  worst ${held.worst}`);
    expect(held.moved, `HOLD must not re-cut the collage (worst ${held.worst})`).toBeLessThan(0.01);

    // TURNING. Sampled across a turn boundary: `ripple` holds for 3.5s, so a
    // sample at ~0.5s and one at ~5s bracket exactly one completed cut.
    for (const id of ['ripple', 'swap', 'march', 'scatter']) {
      await pickTurn(page, id);
      const a = await artBits(page);
      await page.waitForTimeout(7200);
      const b = await artBits(page);
      expect(a).not.toBeNull();
      expect(b).not.toBeNull();
      const d = diff(a!, b!);
      console.log(`[turn] ${id}: moved ${(d.moved * 100).toFixed(2)}%  worst ${d.worst}`);
      expect(d.moved, `${id} must re-cut the collage (worst ${d.worst})`).toBeGreaterThan(MIN_TURNED_SHARE);
      expect(d.worst, `${id} must change a fragment outright somewhere`).toBeGreaterThan(60);
    }

    // BACK TO HOLD — and back to the deal it began on, because turn 0 is the
    // identity and `hold` is the no-op.
    await pickTurn(page, 'hold');
    await page.waitForTimeout(1400);
    const back = await artBits(page);
    const restored = diff(back!, rest0!);
    expect(restored.moved, `HOLD must restore the original deal (worst ${restored.worst})`).toBeLessThan(0.03);
  });

  test('T2b ripple holds part of the wall and march does not', async ({ page }) => {
    // THE ROSTER IS NOT ONE CHIP WIRED FOUR TIMES. T1 measures across TWO turns,
    // by which point every mode has moved every fragment and all four report the
    // same share — a real number, and a blind one. Measured across exactly ONE
    // turn the modes are structurally different: `march` rotates the whole wall,
    // `ripple` rotates one parity half and leaves the other exactly where it is.
    await boot(page);

    // `pickTurn` lands ~1.8s into the schedule (the scene rebuild restarts the
    // clock), so each wait below brackets the FIRST cut and stops short of the
    // second: ripple cuts at 3.5s and again at 7.0s; march at 5.0s and 10.0s.
    await pickTurn(page, 'ripple');
    const r0 = await artBits(page);
    await page.waitForTimeout(2900);
    const rippled = diff(r0!, (await artBits(page))!);

    await pickTurn(page, 'march');
    const m0 = await artBits(page);
    await page.waitForTimeout(4400);
    const marched = diff(m0!, (await artBits(page))!);

    console.log(`[turn] one cut — ripple ${(rippled.moved * 100).toFixed(1)}%  march ${(marched.moved * 100).toFixed(1)}%`);
    expect(rippled.moved, 'RIPPLE must still cut something').toBeGreaterThan(MIN_TURNED_SHARE);
    expect(marched.moved, 'MARCH must move the whole wall in one cut').toBeGreaterThan(0.80);
    expect(rippled.moved, 'RIPPLE must leave a real part of the wall alone').toBeLessThan(0.75);
  });

  test('T3 every photograph is on the wall exactly once, before and after a cut', async ({ page }) => {
    await boot(page);

    // The fixture is six photographs and the app snaps the fragment count to the
    // number of sources, so all six are dealt and none repeats.
    const before = hueCensus((await artBits(page, 220))!, HUES);
    console.log(`[turn] census at rest: ${before.present}/6  shares ${before.shares.map((s) => (s * 100).toFixed(1)).join('/')}`);
    expect(before.present, 'all six photographs must be on the wall at rest').toBe(6);

    await pickTurn(page, 'march');
    // Two full holds plus a fade: past the first cut and settled, so nothing is
    // mid-dissolve when the census runs.
    await page.waitForTimeout(6400);
    const after = hueCensus((await artBits(page, 220))!, HUES);
    console.log(`[turn] census after a cut: ${after.present}/6  shares ${after.shares.map((s) => (s * 100).toFixed(1)).join('/')}`);
    expect(after.present,
      'a cut must be a PERMUTATION — six photographs in, six photographs out, none doubled')
      .toBe(6);

    // And it really did cut: the wall is not the frame it was.
    await pickTurn(page, 'hold');
  });

  test('T4 the exported PICTURE is untouched by a turn', async ({ page }) => {
    await boot(page);
    await renderPicture(page);
    const atRest = await exportBits(page);
    expect(atRest).not.toBeNull();
    await closeResult(page);

    await pickTurn(page, 'scatter');
    await page.waitForTimeout(8000);      // well past the first cut
    await renderPicture(page);
    const turning = await exportBits(page);
    expect(turning).not.toBeNull();

    // NOT "close enough". The still surfaces pass no time, `turnAt` returns the
    // shared NO_TURN at t=0, and the compositor branches on `mix > 0` — so the
    // worker's own pixels must be the pixels it drew before this existed.
    const d = diff(turning!, atRest!, 0);
    expect(d.worst, `the picture export must not see the turn (${(d.moved * 100).toFixed(2)}% of samples differ)`)
      .toBeLessThanOrEqual(1);
  });

  test('T5 the turn travels in the composition code', async ({ page }) => {
    await boot(page);
    await pickTurn(page, 'swap');
    const code = await page.getByTestId('composition-code').first().innerText();
    expect(code.trim().length, 'the strip must show a code').toBeGreaterThan(8);

    await pickTurn(page, 'hold');
    await expect(page.getByTestId('turn-hold')).toHaveAttribute('data-active', 'true');

    await page.getByTestId('composition-code-input').fill(code.trim());
    await page.getByTestId('composition-code-open').click();
    await page.waitForTimeout(1500);
    await expect(page.getByTestId('turn-swap')).toHaveAttribute('data-active', 'true');
  });

  test('T6 the turn row is watertight on a phone', async ({ page }) => {
    await boot(page);
    await pickTurn(page, 'ripple');
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(500);
      const m = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
        chips: Array.from(document.querySelectorAll('[data-testid^="turn-"]')).map((el) => {
          const r = el.getBoundingClientRect();
          return { right: r.right, w: r.width, h: r.height };
        }),
      }));
      expect(m.scrollW, `no horizontal overflow at ${w}px`).toBeLessThanOrEqual(m.clientW);
      expect(m.chips.length, `the turn row must be present at ${w}px`).toBe(5);
      for (const c of m.chips) {
        expect(c.right, `a turn chip runs off the screen at ${w}px`).toBeLessThanOrEqual(m.clientW + 1);
        expect(c.w * c.h, `a turn chip has collapsed at ${w}px`).toBeGreaterThan(200);
      }
    }
  });
});
