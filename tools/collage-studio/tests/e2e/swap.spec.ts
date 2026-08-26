/**
 * THE SWAP AT THE ARTIFACT — two fragments trading pictures, proved on PIXELS.
 *
 * The pure rules (transposition, pin rewrite, refusals, totality) are swept in
 * tests/unit/swap.invariants.mjs — 676k assertions, four mutants dead. This
 * proves the two things a unit test cannot reach:
 *
 *   1. that the trade really moves the PHOTOGRAPHS on the real canvas, and
 *   2. that it SURVIVES A RE-DEAL — which is the whole reason the plan rewrites
 *      the pins, and the one claim that a happy-path test would miss entirely.
 *
 * THE INSTRUMENT is solid-colour tiles. Every fragment is one flat colour, so
 * "which picture is in cell 3" is a question the page answers in RGB, and a
 * swap is visible as two colours changing places with each other and nothing
 * else moving. A luminance metric would not do: it can tell you something
 * changed, not that two specific things exchanged.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test tests/e2e/swap.spec.ts --project=chromium
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test tests/e2e/swap.spec.ts --project=chromium
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
 * SIX TILES FAR APART IN RGB. Far apart so a fragment's identity survives the
 * app's own colour handling (the default look is neutral, but a grade would
 * shift every one of these together and the DISTANCES are what the assertions
 * read). Distinct filenames so they are six distinct SOURCES to the fill.
 */
const PALETTE: Array<[number, number, number]> = [
  [230, 20, 20],   // red
  [20, 200, 60],   // green
  [30, 60, 230],   // blue
  [235, 205, 20],  // yellow
  [200, 30, 200],  // magenta
  [20, 210, 215],  // cyan
];
const tiles = () => PALETTE.map(([r, g, b], i) => ({
  name: `tile-${i}-${r}_${g}_${b}.png`,
  mimeType: 'image/png',
  buffer: makePng(r, g, b),
}));

type RGB = [number, number, number];
const dist = (a: RGB, b: RGB) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

/** The preview's own partition — the overlay App.tsx draws from `layoutItems`. */
const cells = (page: Page) => page.locator('svg[viewBox^="0 0 1200 "] > g');

/**
 * The mean colour of the rendered preview at the CENTRE of fragment `n`.
 *
 * It reads the fragment's own bounding box out of the live DOM and maps its
 * centre onto whichever preview is on screen — the still path's blob `<img>` or
 * the live `<canvas>` — so the measurement follows the app's choice rather than
 * assuming one. The patch is small (±2% of the frame) so it stays inside the
 * fragment even when the partition is not a perfect grid.
 */
async function cellColour(page: Page, n: number): Promise<RGB> {
  const out = await page.evaluate((n) => {
    const gs = document.querySelectorAll('svg[viewBox^="0 0 1200 "] > g');
    const g = gs[n] as SVGGElement | undefined;
    const el = (document.querySelector('canvas') as HTMLCanvasElement | null)
      ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!g || !el) return null;
    const gb = (g as unknown as SVGGraphicsElement).getBoundingClientRect();
    const eb = el.getBoundingClientRect();
    if (!eb.width || !eb.height) return null;
    // Normalised position of the fragment's centre inside the preview element.
    const u = (gb.left + gb.width / 2 - eb.left) / eb.width;
    const v = (gb.top + gb.height / 2 - eb.top) / eb.height;
    if (!(u >= 0 && u <= 1 && v >= 0 && v <= 1)) return null;

    const sw = el instanceof HTMLCanvasElement ? el.width : el.naturalWidth;
    const sh = el instanceof HTMLCanvasElement ? el.height : el.naturalHeight;
    if (!sw || !sh) return null;
    const c = document.createElement('canvas');
    c.width = 200; c.height = Math.max(1, Math.round((200 * sh) / sw));
    const ctx = c.getContext('2d', { willReadFrequently: true });
    if (!ctx) return null;
    ctx.drawImage(el as CanvasImageSource, 0, 0, c.width, c.height);
    const half = 2;
    const x = Math.min(c.width - 1 - half, Math.max(half, Math.round(u * c.width)));
    const y = Math.min(c.height - 1 - half, Math.max(half, Math.round(v * c.height)));
    const px = ctx.getImageData(x - half, y - half, half * 2 + 1, half * 2 + 1).data;
    let r = 0, g2 = 0, b = 0, k = 0;
    for (let i = 0; i < px.length; i += 4) { r += px[i]; g2 += px[i + 1]; b += px[i + 2]; k++; }
    return k ? [r / k, g2 / k, b / k] : null;
  }, n);
  expect(out, `fragment ${n} must be measurable on the rendered preview`).not.toBeNull();
  return out as RGB;
}

async function allColours(page: Page): Promise<RGB[]> {
  const n = await cells(page).count();
  const out: RGB[] = [];
  for (let i = 0; i < n; i++) out.push(await cellColour(page, i));
  return out;
}

async function boot(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  // The face model is a CDN load the app already degrades from; blocking it
  // keeps the crop anchor deterministic across runs (see the ladder entry
  // "THE CROP ANCHOR DEPENDS ON A CDN RACE").
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW here is fine */ });

  await page.locator('input[type="file"]').first().setInputFiles(tiles());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // A rectangular partition, so a fragment's bounding-box centre really is
  // inside the fragment — the measurement above depends on it.
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.waitForTimeout(1500);
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.waitForTimeout(400);
}

async function enterFullBleed(page: Page) {
  await page.getByRole('button', { name: 'Maximize the shot' }).click();
  await expect(page.getByRole('button', { name: 'Exit full bleed' })).toBeVisible({ timeout: 15_000 });
  await page.waitForTimeout(600);
}

/**
 * Point at a fragment and wait until the puck is up.
 *
 * RETRIED for the reason `intake-intent.spec.ts` documents: the arming is
 * cleared whenever the partition changes, so a tap landing in the window
 * between a state change and the new layout settling is swallowed BY DESIGN.
 */
async function armCell(page: Page, n: number) {
  const puck = page.getByTestId('cell-actions');
  await expect.poll(async () => {
    if (await puck.count()) return true;
    await cells(page).nth(n).click({ force: true }).catch(() => { /* mid-relayout */ });
    await page.waitForTimeout(400);
    return (await puck.count()) > 0;
  }, { timeout: 30_000 }).toBe(true);
  return puck;
}

/** Two fragments showing measurably different pictures — the swap needs a pair. */
async function pickPair(colours: RGB[]): Promise<[number, number]> {
  for (let i = 0; i < colours.length; i++) {
    for (let j = i + 1; j < colours.length; j++) {
      if (dist(colours[i], colours[j]) > 90) return [i, j];
    }
  }
  throw new Error(`no two fragments differ enough to trade: ${JSON.stringify(colours)}`);
}

test.describe('THE SWAP — direct manipulation of the sources', () => {
  test('T1 — two fragments really trade pictures, and nothing else moves', async ({ page }) => {
    test.setTimeout(180_000);
    await boot(page);
    await enterFullBleed(page);

    const before = await allColours(page);
    const [a, b] = await pickPair(before);

    const puck = await armCell(page, a);
    await expect(puck.getByTestId('cell-swap'), 'a fragment with a partner offers the third verb').toBeVisible();
    await puck.getByTestId('cell-swap').click();

    // The mode is announced, and every OTHER fragment is now a destination.
    await expect(page.getByTestId('swap-pending')).toBeVisible();
    await expect(page.getByTestId('swap-cancel')).toBeVisible();

    await cells(page).nth(b).click({ force: true });
    await expect(page.getByTestId('swap-pending'), 'the trade closes the mode').toHaveCount(0);
    await page.waitForTimeout(1200);

    const after = await allColours(page);
    expect(after.length, 'the partition must not have changed').toBe(before.length);

    // THE MEASUREMENT: the two colours changed places with each other.
    expect(dist(after[a], before[b]), `fragment ${a} must now show what ${b} showed`).toBeLessThan(45);
    expect(dist(after[b], before[a]), `fragment ${b} must now show what ${a} showed`).toBeLessThan(45);
    expect(dist(after[a], before[a]), `fragment ${a} must actually have changed`).toBeGreaterThan(60);

    // AND NOTHING ELSE MOVED — the transposition claim, on pixels.
    for (let i = 0; i < before.length; i++) {
      if (i === a || i === b) continue;
      expect(dist(after[i], before[i]), `fragment ${i} was not part of the trade and must not have moved`).toBeLessThan(45);
    }

    // The trade is DISCLOSED: both cells come back pinned, which is what makes
    // it survive a re-deal, so the badge appearing is the honest half.
    const pinsAfter = await page.locator('svg[viewBox^="0 0 1200 "] foreignObject').count();
    expect(pinsAfter, 'both traded fragments must be pinned').toBeGreaterThanOrEqual(2);
  });

  test('T2 — THE REDEAL: a shuffle re-deals everything else and the trade holds', async ({ page }) => {
    test.setTimeout(180_000);
    await boot(page);
    await enterFullBleed(page);

    const before = await allColours(page);
    const [a, b] = await pickPair(before);

    const puck = await armCell(page, a);
    await puck.getByTestId('cell-swap').click();
    await cells(page).nth(b).click({ force: true });
    await page.waitForTimeout(1200);
    const traded = await allColours(page);
    expect(dist(traded[a], before[b]), 'the trade must have landed first').toBeLessThan(45);

    // SHUFFLE re-deals every unpinned fragment (`shuffleTrigger` is a dependency
    // of the assignment effect). This is the exact event that would silently
    // undo a swap written only into `shuffledIndices` — the sweep's mutant m1
    // fails 162,521 assertions on it, and this is the same claim at the artifact.
    await page.getByTestId('rail-shuffle').click();
    await page.waitForTimeout(1800);

    const after = await allColours(page);
    expect(after.length, 'a shuffle does not change the partition').toBe(before.length);
    expect(dist(after[a], traded[a]), `fragment ${a} must KEEP the traded picture through a re-deal`).toBeLessThan(45);
    expect(dist(after[b], traded[b]), `fragment ${b} must KEEP the traded picture through a re-deal`).toBeLessThan(45);

    // And the shuffle really did re-deal — otherwise the assertion above is
    // vacuous, which is exactly how this test would lie.
    let moved = 0;
    for (let i = 0; i < before.length; i++) {
      if (i === a || i === b) continue;
      if (dist(after[i], traded[i]) > 60) moved++;
    }
    expect(moved, 'the shuffle must actually have re-dealt the unpinned fragments').toBeGreaterThan(0);
  });

  test('T3 — Escape cancels a pending trade without leaving full bleed', async ({ page }) => {
    test.setTimeout(120_000);
    await boot(page);
    await enterFullBleed(page);

    const before = await allColours(page);
    const [a] = await pickPair(before);

    const puck = await armCell(page, a);
    await puck.getByTestId('cell-swap').click();
    await expect(page.getByTestId('swap-pending')).toBeVisible();

    await page.keyboard.press('Escape');
    await expect(page.getByTestId('swap-pending'), 'Escape backs out of the trade').toHaveCount(0);
    await expect(
      page.getByRole('button', { name: 'Exit full bleed' }),
      'and it must NOT also cost you full bleed — you cancel a mis-tap to try again',
    ).toBeVisible();

    const after = await allColours(page);
    for (let i = 0; i < before.length; i++) {
      expect(dist(after[i], before[i]), `a cancelled trade moves nothing (fragment ${i})`).toBeLessThan(45);
    }
  });

  test('T4 — tapping the parked fragment again cancels, and a lone picture is never offered a trade', async ({ page }) => {
    test.setTimeout(180_000);
    await boot(page);
    await enterFullBleed(page);
    const before = await allColours(page);
    const [a] = await pickPair(before);

    const puck = await armCell(page, a);
    await puck.getByTestId('cell-swap').click();
    await expect(page.getByTestId('swap-pending')).toBeVisible();

    // TAP THE PARKED FRAGMENT WHERE THE PILL IS NOT. The pending pill is
    // positioned on that fragment's own centroid, so a centre-of-element click
    // lands on the pill, not on the canvas — which is exactly what WebKit and
    // Mobile Chrome reported when this test clicked the element's centre. The
    // gesture is real; the reachable area is the part of the fragment the pill
    // leaves showing, and this finds it rather than assuming it exists.
    const spot = await page.evaluate((n) => {
      const g = document.querySelectorAll('svg[viewBox^="0 0 1200 "] > g')[n] as SVGGElement | undefined;
      const pill = document.querySelector('[data-testid="cell-actions"]');
      if (!g || !pill) return null;
      const r = (g as unknown as SVGGraphicsElement).getBoundingClientRect();
      const p = pill.getBoundingClientRect();
      const clear = (x: number, y: number) =>
        !(x >= p.left - 4 && x <= p.right + 4 && y >= p.top - 4 && y <= p.bottom + 4)
        && document.elementFromPoint(x, y)?.closest('g') === g;
      // Inset from each edge in turn — the pill is centred, so an edge is where
      // the fragment shows through if it shows through anywhere.
      const cands: Array<[number, number]> = [
        [r.left + r.width * 0.08, r.top + r.height / 2],
        [r.right - r.width * 0.08, r.top + r.height / 2],
        [r.left + r.width / 2, r.top + r.height * 0.08],
        [r.left + r.width / 2, r.bottom - r.height * 0.08],
      ];
      for (const [x, y] of cands) if (clear(x, y)) return { x, y };
      return null;
    }, a);

    if (spot) {
      await page.mouse.click(spot.x, spot.y);
      await expect(page.getByTestId('swap-pending'), 'the parked fragment cancels where the pill leaves it showing').toHaveCount(0);
    } else {
      // A fragment the pill covers entirely. Then the X IS the way out, and it
      // must be — a mode with no reachable exit is the defect this branch exists
      // to refuse to paper over.
      await page.getByTestId('swap-cancel').click();
      await expect(page.getByTestId('swap-pending'), 'the pill\'s own X is the guaranteed way out').toHaveCount(0);
    }

    // A collage with ONE picture has nobody to trade with, and offering a dead
    // button over it is the inert-control defect this repo has been filed for.
    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    await page.waitForTimeout(400);
    await page.reload();
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    }).catch(() => { /* fine */ });
    await page.locator('input[type="file"]').first().setInputFiles([{
      name: 'lonely.png', mimeType: 'image/png', buffer: makePng(230, 20, 20),
    }]);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(1200);
    await enterFullBleed(page);

    const solo = await armCell(page, 0);
    await expect(solo.getByTestId('cell-lock'), 'the pin verb is still there').toBeVisible();
    await expect(
      solo.getByTestId('cell-swap'),
      'a single fragment has no partner, so the trade must not be offered',
    ).toHaveCount(0);
  });

  test('T6 — UNDO really brings the pre-swap picture back, and REDO puts the trade on again', async ({ page }) => {
    test.setTimeout(180_000);
    await boot(page);
    await enterFullBleed(page);

    const before = await allColours(page);
    const [a, b] = await pickPair(before);

    const puck = await armCell(page, a);
    await puck.getByTestId('cell-swap').click();
    await cells(page).nth(b).click({ force: true });
    await page.waitForTimeout(1200);
    const traded = await allColours(page);
    expect(dist(traded[a], before[b]), 'the trade must have landed first').toBeLessThan(45);

    // A SWAP PUSHES A HISTORY STEP, so Undo has to actually reach it. It very
    // nearly did not: a step restores the composition CODE and the PINS, and a
    // swap changes neither of the code's fields — so every setter in
    // `applyCompositionCode` writes back an identical value, React bails out of
    // the re-render, and the assignment effect never recomputes. The pins would
    // have reverted while the PICTURES stayed traded: an Undo that visibly does
    // nothing, which is worse than no Undo at all because it looks like one.
    await page.getByRole('button', { name: 'Undo the last composition change' }).click();
    await page.waitForTimeout(1500);
    const undone = await allColours(page);
    expect(dist(undone[a], before[a]), `Undo must put fragment ${a}'s original picture back`).toBeLessThan(45);
    expect(dist(undone[b], before[b]), `Undo must put fragment ${b}'s original picture back`).toBeLessThan(45);
    for (let i = 0; i < before.length; i++) {
      expect(dist(undone[i], before[i]), `Undo must restore the WHOLE deal (fragment ${i})`).toBeLessThan(45);
    }

    await page.getByRole('button', { name: 'Redo the composition change' }).click();
    await page.waitForTimeout(1500);
    const redone = await allColours(page);
    expect(dist(redone[a], traded[a]), `Redo must put the trade back on at ${a}`).toBeLessThan(45);
    expect(dist(redone[b], traded[b]), `Redo must put the trade back on at ${b}`).toBeLessThan(45);
  });

  test('T5 — MOBILE-WATERTIGHT: the puck fits and stays tappable at every phone width, in both states', async ({ page }) => {
    test.setTimeout(240_000);
    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await boot(page);
      await enterFullBleed(page);
      const before = await allColours(page);
      const [a] = await pickPair(before);
      const puck = await armCell(page, a);

      // Three verbs at 44 px, and the puck whole inside the viewport.
      for (const id of ['cell-lock', 'cell-swap', 'cell-remove']) {
        const box = await puck.getByTestId(id).boundingBox();
        expect(box, `${id} must be laid out at ${width}px`).not.toBeNull();
        expect(box!.width, `${id} must be a 44px target at ${width}px`).toBeGreaterThanOrEqual(43.5);
        expect(box!.height, `${id} must be a 44px target at ${width}px`).toBeGreaterThanOrEqual(43.5);
      }
      const pb = await puck.boundingBox();
      expect(pb!.x, `the puck must not hang off the left edge at ${width}px`).toBeGreaterThanOrEqual(-0.5);
      expect(pb!.x + pb!.width, `the puck must not hang off the right edge at ${width}px`).toBeLessThanOrEqual(width + 0.5);

      // The pending-trade pill is wider than the three verbs and has to fit too.
      await puck.getByTestId('cell-swap').click();
      await expect(page.getByTestId('swap-pending')).toBeVisible();
      const sb = await page.getByTestId('cell-actions').boundingBox();
      expect(sb!.x, `the pending pill must not hang off the left edge at ${width}px`).toBeGreaterThanOrEqual(-0.5);
      expect(sb!.x + sb!.width, `the pending pill must not hang off the right edge at ${width}px`).toBeLessThanOrEqual(width + 0.5);
      const cancel = await page.getByTestId('swap-cancel').boundingBox();
      expect(cancel!.width, `cancel must be a 44px target at ${width}px`).toBeGreaterThanOrEqual(43.5);

      // And the page itself never scrolls sideways in either state.
      const over = await page.evaluate(() =>
        document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(over, `the page must not scroll sideways at ${width}px`).toBeLessThanOrEqual(0);

      await page.keyboard.press('Escape');
    }
  });
});
