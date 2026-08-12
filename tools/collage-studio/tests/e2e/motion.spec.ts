/**
 * THE MOVE AT THE ARTIFACT — proved on PIXELS, on a real browser.
 *
 * The arithmetic is swept in tests/unit/motion.invariants.mjs (19 invariants:
 * 27,000 setups where a move at t=0 is `Object.is`-identical to no move,
 * 69,000 crops with zero clamps against a naive pan that clamps 13,764/22,700,
 * periodicity to 8.9e-16, the codec round trip, and the over-long-group scar
 * closed). Five things can only be proved out here:
 *
 *   T1  THE PICTURE ACTUALLY MOVES. A sweep can prove the geometry is a
 *       function of time; only a browser can prove that the function is being
 *       CALLED sixty times a second. The compositor's tick is demand-driven —
 *       "nothing playing and nothing dirty -> NO rAF is rescheduled", and a
 *       photos-only scene "draws once and stops" — so a move that reached the
 *       geometry and not the loop would be a still collage with correct maths.
 *
 *   T2  AND STOPS, BACK ON THE EXACT PICTURE. `still` is the boot state and the
 *       no-op; going back to it must give the frame the app started on, not a
 *       frame parked wherever the last cycle happened to leave it.
 *
 *   T3  IT IS REACHABLE AT ALL. The video export was gated on
 *       `clips.length > 0`, so a collage of PHOTOGRAPHS could not be recorded —
 *       correct for a still, wrong the moment the fragments drift, and the one
 *       thing that would have made this feature invisible to anyone who never
 *       imported a video. This asserts the sheet now offers video for a
 *       photos-only collage that moves, and does NOT for one that does not.
 *
 *   T4  THE STILL EXPORT IS UNTOUCHED. The identity guarantee, observed at the
 *       real artifact rather than in the sweep: the downloaded PICTURE is
 *       rendered by a WORKER on another thread with its own OffscreenCanvas and
 *       passes no time at all, so a move must not shift it by one channel. This
 *       is the check that would catch a move leaking into the three surfaces
 *       that produce a single frame.
 *
 *   T5  THE CODE CARRIES IT. A move is part of the recipe, so it must survive
 *       being sent — round-tripped through the real strip, on the real page.
 *
 *   T6  IT IS WATERTIGHT ON A PHONE. Six more chips on a 320px screen, and the
 *       operator's law is that nothing clips or alters when zoomed out.
 *
 * THE FIXTURE IS THE MEASUREMENT. Flat tiles cannot see this feature at all: a
 * move changes WHICH PART of a photograph a fragment samples, and every part of
 * a flat colour is the same colour. So each tile carries a steep diagonal ramp
 * and a hard edge — a crop that shifts by a few percent then moves real pixels,
 * and a test that passes proves sampling moved rather than that something did.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.motion.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.motion.config.ts
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

const HUES: [number, number, number][] = [
  [230, 60, 50], [50, 200, 90], [60, 90, 235], [235, 200, 45],
  [200, 60, 190], [45, 205, 215], [240, 130, 40], [120, 235, 60],
];

/**
 * A STEEP DIAGONAL RAMP WITH A HARD EDGE THROUGH IT.
 *
 * The ramp makes any crop shift readable as a channel shift; the edge makes it
 * readable as a STRUCTURAL change too, so a test cannot pass on a global
 * brightness wobble that happened for some other reason. 384px so a fragment
 * pushing in by ~6% is resampling genuinely different source pixels rather than
 * the same ones interpolated.
 */
const fixtures = () => HUES.map((rgb, i) => ({
  name: `ramp_${i}.png`,
  mimeType: 'image/png',
  buffer: png(384, 384, (x, y) => {
    const t = (x + y) / (383 * 2);
    const edge = (x > 190 && x < 210) || (y > 120 && y < 140) ? 0.15 : 1;
    return [
      Math.round(rgb[0] * (0.25 + 0.75 * t) * edge),
      Math.round(rgb[1] * (0.25 + 0.75 * (1 - t)) * edge),
      Math.round(rgb[2] * (0.35 + 0.65 * t) * edge),
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

async function pickMove(page: Page, id: string) {
  await page.getByTestId(`move-${id}`).click();
  // The still path debounces then encodes a blob; the live path has to mount a
  // Stage, decode every still and land its first frame.
  await page.waitForTimeout(1800);
}

/**
 * THE ARTWORK, downsampled to N x N as raw RGBA.
 *
 * The LARGEST canvas, not the first: a moving collage mounts the Stage inside
 * the art frame, and the page carries other, smaller canvases. Falls back to
 * the still preview's blob image, which is what a collage at rest renders.
 */
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

/** Open the export sheet. The trigger is the header's Export button. */
async function openSheet(page: Page) {
  await page.getByRole('button', { name: /export/i }).first().click();
  await page.locator('[aria-label="Export size"]').waitFor({ timeout: 30_000 });
}

/** Dismiss it via the sheet's own X — the scrim sits under an animating panel. */
async function closeSheet(page: Page) {
  await page.locator('[role="dialog"][aria-labelledby="export-title"]')
    .getByRole('button', { name: 'Close', exact: true }).click();
  await expect(page.locator('[aria-label="Export size"]')).toHaveCount(0, { timeout: 15_000 });
}

async function renderPicture(page: Page) {
  await openSheet(page);
  await page.getByRole('button', { name: /^Render .* JPG$/ }).first().click();
  await expect(page.locator('img[alt="Rendered collage"]')).toBeVisible({ timeout: 150_000 });
  // The result modal decodes the blob it was handed; reading its pixels before
  // that lands measures an empty image, not an export.
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
 * THE BARS, AND WHERE THEY CAME FROM.
 *
 * Both are asserted for every move, because each alone can be fooled. The SHARE
 * (how much of the frame changed) catches a move that shifts one fragment and
 * leaves the rest frozen; the WORST (how far any one sample travelled) catches
 * a move that has decayed into a global shimmer of a couple of levels.
 *
 * The numbers are the floor of three measured runs, with margin, NOT a guess —
 * a threshold picked by taste is how a test ends up flaking at 5% (this one
 * did, on `pulse`, at exactly that bar):
 *
 *     drift  16.7 / 19.0 / 19.9 %    worst 164 / 167 / 170
 *     sway   13.7 / 15.5 / 16.3 %    worst 165 / 169 / 170
 *     wander  7.4 /  7.8 /  9.3 %    worst 152 / 157 / 168
 *     push    7.8 /  9.0 /  9.1 %    worst 152 / 163 / 175
 *     pulse   3.9 /  5.1 /  7.3 %    worst 143 / 147 / 152
 *
 * The split is a property of the feature and not of the fixture: a PAN slides
 * new source pixels across the whole fragment, while a pure ZOOM (`push`,
 * `pulse`) only moves what is near structure — so a zoom legitimately changes a
 * smaller share of the frame while changing it just as hard where it does.
 */
const MIN_SHARE = { drift: 0.10, sway: 0.08, wander: 0.04, push: 0.04, pulse: 0.02 };
const MIN_WORST = 90;

// =============================================================================

test.describe('THE MOVE', () => {
  /**
   * A WALL-CLOCK BUDGET, NOT THE 30 s DEFAULT.
   *
   * This test WAITS rather than scrubs — it predates THE PLAYHEAD, and the
   * waiting is the point of T1/T2: the schedule must run on its own under a
   * real rAF clock and not only when a ruler asks it a question. But it waits
   * 5.2 s at rest and then brackets four turn boundaries, which is already past
   * the config's 30 s default before a single pixel is read, so it failed on
   * the clock rather than on the composition — identically against production,
   * i.e. it had nothing to do with whatever change was being reviewed at the
   * time. Same budget the scrub-based specs carry.
   */
  test.describe.configure({ timeout: 300_000 });

  test('T1/T2 the collage moves when asked, and stops on the picture it started from', async ({ page }) => {
    await boot(page);

    // AT REST. Two samples a second apart must be the same frame — this is the
    // control, and it is also the assertion that a still collage still idles.
    const rest0 = await artBits(page);
    expect(rest0).not.toBeNull();
    await page.waitForTimeout(1100);
    const rest1 = await artBits(page);
    const still = diff(rest0!, rest1!);
    expect.soft(still.moved, `a STILL collage must not move (worst ${still.worst})`).toBeLessThan(0.01);

    // MOVING. Sampled a quarter of a cycle apart, which is where the envelope
    // has travelled furthest — the move is deliberately slow, so two samples
    // 200ms apart would be a weak test of a real feature.
    await pickMove(page, 'drift');
    const a = await artBits(page);
    await page.waitForTimeout(2600);
    const b = await artBits(page);
    expect(a).not.toBeNull();
    expect(b).not.toBeNull();
    const moved = diff(a!, b!);
    console.log(`[motion] drift: moved ${(moved.moved * 100).toFixed(2)}%  worst ${moved.worst}`);
    expect(moved.moved, `DRIFT must move the picture (worst ${moved.worst})`).toBeGreaterThan(MIN_SHARE.drift);
    expect(moved.worst, 'DRIFT must move it by a lot somewhere').toBeGreaterThan(MIN_WORST);

    // AND EVERY OTHER MOVE ON THE ROW MOVES SOMETHING. A roster whose entries
    // are all wired to the same chip is a lie the "did it change?" check above
    // cannot see.
    for (const id of ['push', 'sway', 'pulse', 'wander']) {
      await pickMove(page, id);
      const p = await artBits(page);
      await page.waitForTimeout(2600);
      const q = await artBits(page);
      const d = diff(p!, q!);
      console.log(`[motion] ${id}: moved ${(d.moved * 100).toFixed(2)}%  worst ${d.worst}`);
      expect(d.moved, `${id} must move the picture (worst ${d.worst})`)
        .toBeGreaterThan(MIN_SHARE[id as keyof typeof MIN_SHARE]);
      expect(d.worst, `${id} must move it by a lot somewhere`).toBeGreaterThan(MIN_WORST);
    }

    // BACK TO STILL — and back to the picture it began on.
    await pickMove(page, 'still');
    await page.waitForTimeout(1200);
    const back = await artBits(page);
    const restored = diff(back!, rest0!);
    expect(restored.moved, `STILL must restore the original frame (worst ${restored.worst})`).toBeLessThan(0.02);
  });

  test('T3 a photos-only collage can be recorded only once it moves', async ({ page }) => {
    await boot(page);

    await openSheet(page);
    const atRest = await page.getByText('Record the moving collage').count();
    await closeSheet(page);
    expect(atRest, 'a STILL photo collage has nothing to record').toBe(0);

    await pickMove(page, 'wander');
    await openSheet(page);
    const moving = await page.getByText('Record the moving collage').count();
    await expect(page.getByRole('button', { name: /^Record \d+s video$/ })).toBeVisible();
    await closeSheet(page);
    expect(moving, 'a MOVING photo collage must be recordable').toBeGreaterThan(0);
  });

  test('T4 the exported PICTURE is untouched by a move', async ({ page }) => {
    await boot(page);
    await renderPicture(page);
    const atRest = await exportBits(page);
    expect(atRest).not.toBeNull();
    await closeResult(page);

    await pickMove(page, 'wander');
    await renderPicture(page);
    const moving = await exportBits(page);
    expect(moving).not.toBeNull();

    // NOT "close enough". The still surfaces pass no time, `sampleMove` returns
    // the shared NO_MOVE at t=0, and `calculateSmartCrop` branches on that
    // identity — so the worker's own pixels must be the pixels it drew before
    // this feature existed. JPEG encoding is deterministic for identical input,
    // so the bar is a channel, not a percentage.
    const d = diff(moving!, atRest!, 0);
    expect(d.worst, `the picture export must not see the move (${(d.moved * 100).toFixed(2)}% of samples differ)`)
      .toBeLessThanOrEqual(1);
  });

  test('T5 the move travels in the composition code', async ({ page }) => {
    await boot(page);
    await pickMove(page, 'sway');
    const code = await page.getByTestId('composition-code').first().innerText();
    expect(code.trim().length, 'the strip must show a code').toBeGreaterThan(8);

    // Reset to still, then paste the code back — the move must come with it.
    await pickMove(page, 'still');
    await expect(page.getByTestId('move-still')).toHaveAttribute('data-active', 'true');

    await page.getByTestId('composition-code-input').fill(code.trim());
    await page.getByTestId('composition-code-open').click();
    await page.waitForTimeout(1500);
    await expect(page.getByTestId('move-sway')).toHaveAttribute('data-active', 'true');
  });

  test('T6 the move row is watertight on a phone', async ({ page }) => {
    await boot(page);
    await pickMove(page, 'wander');
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(500);
      const m = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
        chips: Array.from(document.querySelectorAll('[data-testid^="move-"]')).map((el) => {
          const r = el.getBoundingClientRect();
          return { right: r.right, w: r.width, h: r.height };
        }),
      }));
      expect(m.scrollW, `no horizontal overflow at ${w}px`).toBeLessThanOrEqual(m.clientW);
      expect(m.chips.length, `the move row must be present at ${w}px`).toBe(6);
      for (const c of m.chips) {
        expect(c.right, `a move chip runs off the screen at ${w}px`).toBeLessThanOrEqual(m.clientW + 1);
        expect(c.w * c.h, `a move chip has collapsed at ${w}px`).toBeGreaterThan(200);
      }
    }
  });
});
