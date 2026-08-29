/**
 * THE REFRAME AT THE ARTIFACT — the picture moves inside its fragment, on PIXELS.
 *
 * The arithmetic (the finger-following, the clamp, the lean, the fragment never
 * moving) is swept in tests/unit/reframe.invariants.mjs against the shipped
 * `calculateSmartCrop`. This proves the three things a unit test cannot reach:
 *
 *   1. that the DRAWN photograph really moves, on the real rendered preview,
 *   2. that the correction SURVIVES A RE-DEAL — which is the whole reason a
 *      frame is keyed by asset id rather than by slot, and
 *   3. that Recentre puts it back.
 *
 * THE INSTRUMENT is three-band tiles: each source is a tall image cut into a
 * TOP, a MIDDLE and a BOTTOM band of a different colour. A crop is much shorter
 * than a band, so "which part of the photograph is showing" is a question the
 * page answers in RGB — and dragging the picture DOWN must reveal the band
 * ABOVE, which is a claim about direction and magnitude at once. A luminance
 * delta would only say something changed.
 *
 * IT IDENTIFIES ITS OWN SOURCE. Which tile landed in which fragment is up to
 * the fill, and the resting anchor is up to the energy pass, so nothing here
 * assumes either: the test drags fully one way and fully the other, then looks
 * for the ONE source whose top band and bottom band explain both readings. A
 * test that had to be told the answer could not tell you it was wrong.
 *
 * Run against the collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test tests/e2e/reframe.spec.ts --project=chromium
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test tests/e2e/reframe.spec.ts --project=chromium
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

type RGB = [number, number, number];
const dist = (a: RGB, b: RGB) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

/** A vertical-GRADIENT PNG built in-process — no fixture files. */
function makeGradient(top: RGB, bottom: RGB, w = 120, h = 900): Buffer {
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
    const t = h > 1 ? y / (h - 1) : 0;
    const r = Math.round(top[0] + (bottom[0] - top[0]) * t);
    const g = Math.round(top[1] + (bottom[1] - top[1]) * t);
    const b = Math.round(top[2] + (bottom[2] - top[2]) * t);
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) { row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b; }
    rows.push(row);
  }
  const idat = zlib.deflateSync(Buffer.concat(rows));
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

/**
 * FOUR SOURCES, EIGHT ENDS, ALL >=110 APART IN RGB.
 *
 * A GRADIENT AND NOT BANDS, and that is a scar rather than a preference: with
 * banded tiles the rendered colour is CONSTANT while the crop moves inside one
 * band, so "drag until the colour stops changing" — the only pass count that
 * holds on a Pixel as well as on a desktop — settled in the middle of a band
 * and called it the end of the photograph. A gradient makes every pixel of
 * travel measurable, so the settle really is the clamp.
 */
const SOURCES: Array<[RGB, RGB]> = [
  [[250, 20, 20], [20, 20, 250]],
  [[250, 250, 20], [20, 250, 250]],
  [[250, 140, 20], [20, 140, 250]],
  [[200, 20, 200], [20, 200, 20]],
];
const TOP = (s: number) => SOURCES[s][0];
const BOTTOM = (s: number) => SOURCES[s][1];

const tiles = () => SOURCES.map(([t, b], i) => ({
  name: `grad-${i}.png`,
  mimeType: 'image/png',
  buffer: makeGradient(t, b),
}));

/** The preview's own partition — the overlay App.tsx draws from `layoutItems`. */
const cells = (page: Page) => page.locator('svg[viewBox^="0 0 1200 "] > g');

/** Mean colour of the RENDERED preview at the centre of fragment `n`. */
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

/**
 * A READ THAT HAS STOPPED MOVING.
 *
 * The still preview is produced asynchronously — renderCanvas, then toBlob,
 * then an object URL an <img> has to load — so ANY read taken immediately
 * after a gesture is racing it. Under three parallel workers that race is lost
 * often enough that a drag looked like it did nothing, twice in a row, which is
 * exactly what the settle test below reads as "we reached the end". Serial runs
 * hid it completely. Every measurement in this file goes through here.
 */
async function stableColour(page: Page, n: number, tries = 14): Promise<RGB> {
  let prev = await cellColour(page, n);
  for (let i = 0; i < tries; i++) {
    await page.waitForTimeout(220);
    const now = await cellColour(page, n);
    if (dist(now, prev) < 2) return now;
    prev = now;
  }
  return prev;
}

async function allColours(page: Page): Promise<RGB[]> {
  const n = await cells(page).count();
  const out: RGB[] = [];
  for (let i = 0; i < n; i++) out.push(await cellColour(page, i));
  return out;
}

/** Every fragment's box, so "the fragment never moves" is a measurement. */
async function allBoxes(page: Page) {
  return page.evaluate(() => Array.from(
    document.querySelectorAll('svg[viewBox^="0 0 1200 "] > g'),
    (g) => {
      const b = (g as unknown as SVGGraphicsElement).getBoundingClientRect();
      return [b.x, b.y, b.width, b.height] as [number, number, number, number];
    },
  ));
}

async function boot(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  // The face model is a CDN load the app already degrades from; blocking it
  // keeps the resting anchor deterministic (see "THE CROP ANCHOR DEPENDS ON A
  // CDN RACE" in the ladder).
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW here is fine */ });

  await page.locator('input[type="file"]').first().setInputFiles(tiles());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // A rectangular partition, so a fragment's bounding-box centre is really
  // inside the fragment — every measurement here depends on it.
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

/** Point at a fragment and wait until the puck is up. */
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

/** The roomiest fragment — the puck sits at a centroid and a tiny cell is all puck. */
async function biggestCell(page: Page): Promise<number> {
  const boxes = await allBoxes(page);
  let best = 0, area = -1;
  boxes.forEach((b, i) => { const a = b[2] * b[3]; if (a > area) { area = a; best = i; } });
  return best;
}

/**
 * DRAG THE PICTURE inside fragment `n` ALL THE WAY to its end.
 *
 * One pass can only travel as far as the viewport allows, and how far that is
 * in SOURCE pixels depends on the fragment's size, the phone's width and the
 * photograph's own dimensions — so a fixed pass count is a guess that holds on
 * a desktop and fails on a Pixel (measured: Mobile Chrome and WebKit both
 * stopped a band short of the end). It drags until the rendered colour STOPS
 * CHANGING instead, which is the clamp announcing itself, and fails loudly if
 * it never settles.
 */
async function dragPicture(page: Page, n: number, dir: -1 | 1, maxPasses = 20) {
  const start = await stableColour(page, n);
  let last = start;
  let settled = 0;
  for (let p = 0; p < maxPasses; p++) {
    const box = await cells(page).nth(n).boundingBox();
    if (!box) throw new Error(`fragment ${n} has no box`);
    const vp = page.viewportSize() ?? { width: 1280, height: 720 };
    const cx0 = box.x + box.width / 2;
    const cy0 = box.y + box.height / 2;
    // WHERE A DRAG CAN ACTUALLY START, and both exclusions were measured here
    // rather than reasoned about. (1) The full-bleed RAIL owns the bottom ~90px
    // of the screen and its pill takes the pointerdown, so a fragment reaching
    // the floor cannot be grabbed down there — a real overlap, not a test
    // artefact. (2) The PUCK sits on the centroid. Start near the edge the drag
    // comes from, clamped above the rail, and step aside horizontally if that
    // clamp lands under the puck.
    let sy = dir > 0 ? box.y + box.height * 0.18 : box.y + box.height * 0.82;
    sy = Math.max(box.y + 8, Math.min(sy, box.y + box.height - 8));
    sy = Math.max(box.y + 8, Math.min(sy, vp.height - 96));
    let sx = cx0;
    if (Math.abs(sy - cy0) < 44) {
      sx = cx0 + Math.min(box.width / 2 - 8, 130) * (cx0 > vp.width / 2 ? -1 : 1);
    }
    const room = dir > 0 ? vp.height - sy - 4 : sy - 4;
    const dy = dir * Math.max(60, room);
    await page.mouse.move(sx, sy);
    await page.mouse.down();
    for (let i = 1; i <= 20; i++) await page.mouse.move(sx, sy + (dy * i) / 20);
    await page.mouse.up();
    await page.waitForTimeout(420);
    const now = await stableColour(page, n);
    if (process.env.REFRAME_DEBUG) {
      const puck = await page.getByTestId('cell-actions').count();
      console.log(`[cell ${n} drag ${dir > 0 ? 'down' : 'up'} pass ${p}] start=(${Math.round(sx)},${Math.round(sy)}) dy=${Math.round(dy)} colour=${now.map(Math.round)} puck=${puck}`);
    }
    // A PASS THAT MOVED NOTHING, ON A PICTURE THAT HAS NOT MOVED AT ALL, is a
    // gesture that did not land — never the clamp. Counting it as a settle is
    // how the first version of this helper declared victory on a drag the app
    // never received.
    const stuckAtStart = dist(now, start) < 3;
    if (dist(now, last) < 3 && !(stuckAtStart && p < 4)) {
      settled++;
      if (settled >= 2) { await page.waitForTimeout(300); return; }
    } else settled = 0;
    last = now;
  }
  throw new Error(`fragment ${n} never reached the end of its photograph in ${maxPasses} passes`);
}

test.describe('THE REFRAME — the picture moves inside its fragment', () => {
  test('T1 — a drag moves the photograph, both ways, and moves nothing else', async ({ page }) => {
    test.setTimeout(240_000);
    await boot(page);
    await enterFullBleed(page);

    const before = await allColours(page);
    const boxesBefore = await allBoxes(page);
    const n = before.length;
    expect(n, 'the partition must have fragments to reframe').toBeGreaterThan(1);

    const target = await biggestCell(page);
    await armCell(page, target);

    // DOWN moves the picture down, so the band ABOVE comes into view.
    await dragPicture(page, target, 1);
    const afterDown = await stableColour(page, target);

    // UP is the other end of the same photograph.
    await dragPicture(page, target, -1);
    const afterUp = await stableColour(page, target);

    // WHICH SOURCE IS THIS? The one whose two ENDS explain both readings.
    const explains = SOURCES.map((_, s) => s).filter(
      (s) => dist(afterDown, TOP(s)) < 55 && dist(afterUp, BOTTOM(s)) < 55,
    );
    expect(
      explains.length,
      `exactly one source must explain down=${afterDown.map(Math.round)} up=${afterUp.map(Math.round)}`,
    ).toBe(1);

    const s = explains[0];
    expect(dist(afterDown, TOP(s)), 'dragging down must reveal the TOP of the photograph').toBeLessThan(55);
    expect(dist(afterUp, BOTTOM(s)), 'dragging up must reveal the BOTTOM of the photograph').toBeLessThan(55);
    expect(dist(afterDown, afterUp), 'the two ends must be plainly different pictures').toBeGreaterThan(90);

    // AND NOTHING ELSE MOVED — the fragment stays exactly where it was...
    const boxesAfter = await allBoxes(page);
    expect(boxesAfter.length).toBe(boxesBefore.length);
    for (let i = 0; i < boxesBefore.length; i++) {
      for (let k = 0; k < 4; k++) {
        expect(
          Math.abs(boxesAfter[i][k] - boxesBefore[i][k]),
          `fragment ${i} must not have moved (component ${k})`,
        ).toBeLessThan(1.5);
      }
    }
    // ...and every OTHER picture is untouched.
    const others = await allColours(page);
    for (let i = 0; i < n; i++) {
      if (i === target) continue;
      expect(dist(others[i], before[i]), `fragment ${i} must be untouched`).toBeLessThan(18);
    }
  });

  test('T2 — Recentre appears only on a moved picture, and puts it back', async ({ page }) => {
    test.setTimeout(240_000);
    await boot(page);
    await enterFullBleed(page);

    const target = await biggestCell(page);
    const before = await stableColour(page, target);
    const puck = await armCell(page, target);
    await expect(
      puck.getByTestId('cell-recentre'),
      'a picture nobody moved offers no way back',
    ).toHaveCount(0);

    await dragPicture(page, target, 1);
    const moved = await stableColour(page, target);
    expect(dist(moved, before), 'the drag must have done something to measure').toBeGreaterThan(60);

    const recentre = page.getByTestId('cell-actions').getByTestId('cell-recentre');
    await expect(recentre, 'a moved picture offers the way back').toBeVisible({ timeout: 10_000 });
    await recentre.click();
    await page.waitForTimeout(1200);

    const back = await stableColour(page, target);
    expect(dist(back, before), 'Recentre must restore the crop the app chose').toBeLessThan(22);
    await expect(
      page.getByTestId('cell-actions').getByTestId('cell-recentre'),
      'and the verb retires with the correction',
    ).toHaveCount(0);
  });

  test('T3 — the correction survives a re-deal', async ({ page }) => {
    test.setTimeout(240_000);
    await boot(page);
    await enterFullBleed(page);

    const target = await biggestCell(page);
    await armCell(page, target);
    await dragPicture(page, target, 1);
    const moved = await stableColour(page, target);

    // Which source is showing its TOP band? That is the corrected one.
    const s = SOURCES.map((_, i) => i).find((i) => dist(moved, TOP(i)) < 55);
    expect(s, `the drag must have parked on a recognisable top band (${moved.map(Math.round)})`).not.toBeUndefined();

    // SHUFFLE re-deals which picture sits in which fragment. Retried, because a
    // random permutation is free to be the identity and a vacuous re-deal would
    // make the claim below unfalsifiable.
    const shuffle = page.getByRole('button', { name: /shuffle/i }).first();
    let dealt = false;
    for (let i = 0; i < 5 && !dealt; i++) {
      const was = await allColours(page);
      await shuffle.click();
      await page.waitForTimeout(1400);
      const now = await allColours(page);
      dealt = now.some((c, k) => dist(c, was[k]) > 60);
    }
    expect(dealt, 'the shuffle must actually have re-dealt something').toBe(true);

    // THE CLAIM: wherever that picture landed, it still shows its top band.
    const after = await allColours(page);
    const found = after.some((c) => dist(c, TOP(s as number)) < 60);
    expect(
      found,
      `the corrected picture must still be showing ${TOP(s as number)} somewhere after the re-deal; saw ${JSON.stringify(after.map((c) => c.map(Math.round)))}`,
    ).toBe(true);
  });
});
