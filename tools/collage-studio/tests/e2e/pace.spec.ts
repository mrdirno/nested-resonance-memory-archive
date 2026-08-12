/**
 * THE PACE AT THE ARTIFACT — proved on PIXELS, on a real browser, with NO CLOCK.
 *
 * The arithmetic is swept in tests/unit/pace.invariants.mjs (13 invariants: the
 * dissolve share proved invariant at every rate WITH a red proof that the
 * rejected design doubles it, rest-at-zero by reference, the 22-character code
 * and all four earlier generations still opening). Four things can only be
 * proved out here.
 *
 *   P1  THE RATE REACHES THE COMPOSITOR. A sweep can prove `paceTime` scales a
 *       number; only a browser can prove the Stage asks it, that the answer
 *       reaches `refreshTurn`, and that the pictures actually land somewhere
 *       else because of it.
 *
 *   P2  IN BOTH DIRECTIONS. Faster is the easy half — anything that perturbs
 *       the schedule looks like "faster" if you only ever measure more. SLOWER
 *       is the half that catches a sign error, and it is measured as the wall
 *       still holding its opening deal at an instant where 1x has already cut.
 *
 *   P3  THE PERMUTATION SURVIVES THE RATE. Six photographs, six hues, one each.
 *       A rate is a change to WHEN the deal is read, so the app's oldest promise
 *       — every source once, never twice — has to hold at every one of them.
 *
 *   P4  IT IS WATERTIGHT ON A PHONE. Five more chips on a 320px screen.
 *
 * WHY EVERY MEASUREMENT IS A SCRUB AND NOT A WAIT.
 *   The obvious test counts cuts in a wall-clock window and compares the counts.
 *   It is slow (two 12-second windows), and it is a race: a rAF-driven schedule
 *   under a loaded CI machine lands its cut a frame either side of where a
 *   `waitForTimeout` looks. THE PLAYHEAD makes the whole thing deterministic —
 *   `renderAtTime` is a PURE function of the instant, which is exactly why the
 *   offline exporter can walk it — so parking on 3.0s asks the composition a
 *   question with one right answer:
 *
 *     march holds 5s. At 1x, t=3.0 is inside the opening hold: the base deal.
 *     At 2x the schedule reads 6.0s, one cut in and settled. At 0.5x, t=6.0
 *     reads 3.0s and is STILL the base deal, where 1x has already cut.
 *
 *   Same pixels, three rates, no timer anywhere. And because the scrub path IS
 *   the offline walk, a green run here is evidence about the exported file and
 *   not only about the preview.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test tests/e2e/pace.spec.ts --project=chromium
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test tests/e2e/pace.spec.ts --project=chromium
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** The take the ruler must be long enough to reach 6.0s on. */
const TAKE = 10;
/** `march`'s hold, from lib/turn.ts. The whole test is arithmetic on this. */
const MARCH_HOLD = 5.0;

// --- fixtures (the turn spec's, for the reason its header gives) -------------

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

const HUES: [number, number, number][] = [
  [235, 30, 30], [30, 220, 60], [40, 70, 240],
  [240, 215, 35], [225, 45, 225], [35, 215, 225],
];

/** Variation entirely in BRIGHTNESS, so the hue census (which classifies by
 *  DIRECTION in RGB) is invariant to it while the crop still has structure. */
const fixtures = () => HUES.map((rgb, i) => ({
  name: `hue-${i}.png`,
  mimeType: 'image/png',
  buffer: png(320, 320, (x, y) => {
    const t = 0.30 + 0.70 * ((x + y) / (319 * 2));
    const edge = (x > 150 && x < 172) || (y > 96 && y < 118) ? 0.45 : 1;
    const k = t * edge;
    return [Math.round(rgb[0] * k), Math.round(rgb[1] * k), Math.round(rgb[2] * k)] as [number, number, number];
  }),
}));

// --- page helpers ------------------------------------------------------------

async function boot(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(fixtures());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // Tabs are labelled Layout / Settings — NOT Simple / Advanced (scar).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.getByRole('button', { name: 'Layout' }).first().click();
  await page.waitForTimeout(1600);
}

const chip = async (page: Page, id: string) => {
  await page.getByTestId(id).click();
  // A chip change rebuilds the scene: the Stage re-binds every fragment and
  // re-establishes the assignment at the current park.
  await page.waitForTimeout(1400);
};

const playhead = (page: Page) => page.getByLabel(/^Playhead/);

/** Park the whole composition on an instant. `fill` is the only way to place a
 *  range precisely, and the STRING form matters (scar: trim.spec.ts:494). */
const scrubTo = async (page: Page, t: number) => {
  await playhead(page).fill(String(t));
  await page.waitForTimeout(800);
};

/** The artwork, downsampled to N x N as raw RGBA — the LARGEST canvas. */
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

/** Share of samples that differ by more than `tol`, and the worst difference. */
function diff(a: number[], b: number[], tol = 6): { moved: number; worst: number } {
  let moved = 0; let worst = 0; let n = 0;
  for (let i = 0; i < a.length; i += 4) {
    const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
    if (d > worst) worst = d;
    if (d > tol) moved++;
    n++;
  }
  return { moved: moved / Math.max(1, n), worst };
}

/** How many of the six prototype hues are on the wall. A permutation keeps all
 *  six; a duplicate makes one VANISH, which is what this counts. */
function hueCensus(bits: number[]): number {
  const seen = new Set<number>();
  for (let i = 0; i < bits.length; i += 4) {
    const r = bits[i]; const g = bits[i + 1]; const b = bits[i + 2];
    const mag = Math.hypot(r, g, b);
    if (mag < 40) continue;                       // gutter / background
    let best = -1; let bestDot = 0;
    for (let h = 0; h < HUES.length; h++) {
      const [hr, hg, hb] = HUES[h];
      const hm = Math.hypot(hr, hg, hb);
      const dot = (r * hr + g * hg + b * hb) / (mag * hm);
      if (dot > bestDot) { bestDot = dot; best = h; }
    }
    if (best >= 0 && bestDot > 0.985) seen.add(best);
  }
  return seen.size;
}

// -----------------------------------------------------------------------------

test.describe('THE PACE', () => {
  test.describe.configure({ mode: 'serial', timeout: 300_000 });

  test('P1/P2 a rate moves the schedule, in both directions, on real pixels', async ({ page }) => {
    await boot(page);
    await chip(page, 'turn-march');
    await page.getByRole('button', { name: `${TAKE}s`, exact: true }).click();
    await expect(playhead(page)).toBeVisible({ timeout: 60_000 });

    // THE CONTROL, and it is the assertion that makes the rest mean anything:
    // at the roster's own tempo, 3.0s is inside march's opening 5s hold, so the
    // wall must be showing exactly the deal it opened on.
    await scrubTo(page, 0);
    const rest = await artBits(page);
    await scrubTo(page, 3.0);
    const even3 = await artBits(page);
    expect(rest).not.toBeNull();
    expect(even3).not.toBeNull();
    const held = diff(rest!, even3!);
    expect(held.moved,
      `1x must NOT have cut by ${3.0}s (march holds ${MARCH_HOLD}s) — worst ${held.worst}`)
      .toBeLessThan(0.02);

    // FASTER. 2x reads the schedule at 6.0s: one cut in, and settled (the
    // dissolve is 0.7/2 = 0.35s and long over).
    await chip(page, 'pace-rush');
    await scrubTo(page, 3.0);
    const rush3 = await artBits(page);
    expect(rush3).not.toBeNull();
    const cut = diff(even3!, rush3!);
    // PRINTED, not only asserted: the book quotes these, and a number nobody
    // can read off a run is a number somebody will eventually invent.
    console.log(`[pace] 2x @3.0s vs 1x @3.0s: ${(cut.moved * 100).toFixed(1)}% of the frame moved, worst channel ${cut.worst}/255`);
    expect(cut.moved, `2x must have cut by 3.0s — worst ${cut.worst}`).toBeGreaterThan(0.60);
    expect(cut.worst, 'and must change fragments outright, not merely soften them').toBeGreaterThan(60);
    expect(hueCensus(rush3!), 'every photograph exactly once, at 2x').toBe(6);

    // SLOWER — the half that catches a sign error. At 0.5x, 6.0s reads 3.0s and
    // the wall is STILL on its opening deal, where 1x has already cut once.
    await chip(page, 'pace-slow');
    await scrubTo(page, 6.0);
    const slow6 = await artBits(page);
    expect(slow6).not.toBeNull();
    const stillHeld = diff(rest!, slow6!);
    expect(stillHeld.moved,
      `0.5x must still be holding the opening deal at 6.0s — worst ${stillHeld.worst}`)
      .toBeLessThan(0.02);

    await chip(page, 'pace-even');
    await scrubTo(page, 6.0);
    const even6 = await artBits(page);
    expect(even6).not.toBeNull();
    const oneX = diff(rest!, even6!);
    console.log(`[pace] 1x @6.0s vs rest: ${(oneX.moved * 100).toFixed(1)}% moved, worst ${oneX.worst}/255`
      + ` | 0.5x @6.0s vs rest: ${(stillHeld.moved * 100).toFixed(1)}% moved, worst ${stillHeld.worst}/255`
      + ` | 1x @3.0s vs rest: ${(held.moved * 100).toFixed(1)}% moved, worst ${held.worst}/255`);
    expect(oneX.moved, `1x MUST have cut by 6.0s — worst ${oneX.worst}`).toBeGreaterThan(0.60);
    expect(hueCensus(even6!), 'every photograph exactly once, at 1x after a cut').toBe(6);
  });

  test('P3 the pace travels in the composition code', async ({ page }) => {
    await boot(page);
    await chip(page, 'turn-march');
    await chip(page, 'pace-brisk');
    const code = await page.getByTestId('composition-code').innerText();
    expect(code.trim().length, 'the strip must show a code').toBeGreaterThan(8);

    await chip(page, 'pace-even');
    await expect(page.getByTestId('pace-even')).toHaveAttribute('data-active', 'true');
    await page.getByTestId('composition-code-input').fill(code.trim());
    await page.getByTestId('composition-code-open').click();
    await page.waitForTimeout(1200);
    await expect(page.getByTestId('pace-brisk')).toHaveAttribute('data-active', 'true');
  });

  test('P5 the chip you just tapped still looks chosen — the pace row AND its siblings', async ({ page }) => {
    // FOUND BY LOOKING AT THE LIVE PAGE, and it was never about the pace.
    // `.ui-chip:hover:not(:disabled)` is specificity (0,3,0) and
    // `.ui-chip[data-active='true']` is (0,2,0), so hover WON and the chip you
    // had just chosen rendered `--surface-3`. Measured on production before the
    // fix: rgb(31,36,39) for a chosen-and-hovered chip against rgb(22,25,27)
    // for one that was genuinely unchosen — nine units per channel, where the
    // right answer is `--signal`. On iOS a tap leaves a STICKY hover, so the
    // chip you tapped sat there looking untapped on the exact device this app
    // is for. Playwright's `click` leaves the pointer on the element, which is
    // precisely that state, so this arm is the finger.
    await boot(page);
    const signal = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--signal').trim());
    expect(signal, 'the palette must define --signal').toMatch(/^#|rgb/);
    const asRgb = await page.evaluate((hex) => {
      const d = document.createElement('div');
      d.style.color = hex; document.body.appendChild(d);
      const v = getComputedStyle(d).color; d.remove(); return v;
    }, signal);

    // EVERY roster row on this page, not only the one this cycle added: the
    // rule is shared, so the sweep is the point.
    // `sync-beat` is here because THE BEAT added a roster row and this guard is
    // the one that would catch it rendering unchosen — the C144 lesson is that
    // the sweep, not the row, is the point, so a new row joins the list in the
    // cycle that adds it rather than in the cycle that breaks it.
    for (const id of ['pace-rush', 'move-drift', 'turn-swap', 'look-noir', 'sync-beat']) {
      const chip = page.getByTestId(id);
      if (await chip.count() === 0) continue;
      await chip.click();
      await page.waitForTimeout(600);
      await expect(chip).toHaveAttribute('data-active', 'true');
      const bg = await chip.evaluate((el) => getComputedStyle(el).backgroundColor);
      expect(bg, `${id}: a chosen chip under the pointer must still read as chosen`).toBe(asRgb);
    }
  });

  test('P4 the row is watertight on a phone', async ({ page }) => {
    await boot(page);
    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.waitForTimeout(500);
      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollW,
        `${width}px: the page must not scroll sideways (${overflow.scrollW} > ${overflow.clientW})`)
        .toBeLessThanOrEqual(overflow.clientW);

      const boxes = await page.getByTestId(/^pace-/).evaluateAll((els) =>
        els.map((e) => {
          const r = e.getBoundingClientRect();
          return { w: r.width, h: r.height, right: r.right, clipped: e.scrollWidth > e.clientWidth + 1 };
        }));
      expect(boxes.length, `${width}px: all five pace chips must be present`).toBe(5);
      for (const b of boxes) {
        expect(b.h, `${width}px: a 44px tap target`).toBeGreaterThanOrEqual(44);
        expect(b.right, `${width}px: a chip may not run off the edge`).toBeLessThanOrEqual(width + 0.5);
        expect(b.clipped, `${width}px: a chip label may not be clipped`).toBe(false);
      }
    }
  });
});
