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
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

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

/**
 * WHICH PHOTOGRAPH, AND HOW FAR DOWN IT — by projecting the reading onto each
 * source's own gradient and keeping the best fit.
 *
 * Comparing to the ENDPOINT colour was the obvious instrument and it is the
 * weak one: a crop parked at the top of a photograph is centred half a crop
 * HEIGHT in, so a tall fragment reads measurably down the gradient and a fixed
 * RGB threshold has to be loosened until it stops discriminating. The
 * projection separates the two questions the assertion actually asks — WHICH
 * source (the perpendicular residual, ~1 for the right one and >50 for any
 * other) and WHERE ON IT (the parameter t) — so each can be given a tight bar.
 */
type Fit = { s: number; t: number; resid: number };
function fitSource(c: RGB): Fit {
  let best: Fit = { s: -1, t: 0, resid: Infinity };
  SOURCES.forEach(([a, b], s) => {
    const d: RGB = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const len2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
    const raw = ((c[0] - a[0]) * d[0] + (c[1] - a[1]) * d[1] + (c[2] - a[2]) * d[2]) / len2;
    const t = Math.max(0, Math.min(1, raw));
    const resid = dist(c, [a[0] + d[0] * t, a[1] + d[1] * t, a[2] + d[2] * t]);
    if (resid < best.resid) best = { s, t, resid };
  });
  return best;
}

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

// --- THE FILE ROUND TRIP (T4/T5) --------------------------------------------
// Lifted verbatim from svg-project.spec.ts, which is where the SVG-as-project
// claim is proved for everything EXCEPT the reframe. Same three helpers, same
// real Export sheet and real file chooser — a round trip driven any other way
// would be a round trip through a path the user does not have.

/** Drives the real Export sheet, takes the real download, returns the bytes. */
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
  await page.waitForTimeout(600);
  return Buffer.concat(chunks).toString('utf8');
}

/** Drives the real Open button through the real file chooser. */
async function openFile(page: Page, path: string) {
  const [chooser] = await Promise.all([
    page.waitForEvent('filechooser', { timeout: 30_000 }),
    page.getByRole('button', { name: 'Open' }).first().click(),
  ]);
  await chooser.setFiles(path);
}

const onDisk = (name: string, text: string): string => {
  const p = join(mkdtempSync(join(tmpdir(), 'collage-reframe-')), name);
  writeFileSync(p, text, 'utf8');
  return p;
};

/**
 * THE WAY IN HAS TO BE REACHABLE, and after a reload it is offered a rival.
 *
 * The pool is empty and there is an autosaved session on disk, so the restore
 * banner renders — and at `top-3` it is 94vw wide, centred, and lands exactly on
 * the header's Open button on a phone. `.click()` then hits the CARD, no file
 * chooser opens, and the failure reads as a Playwright timeout rather than as
 * what it is: the offer to bring back the last session covering the one control
 * that opens a different one. Asserted, because a click that lands on the wrong
 * element is invisible to every other assertion in this file.
 */
async function expectOpenReachable(page: Page) {
  const hit = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /^open$/i.test((b.getAttribute('aria-label') || b.textContent || '').trim()));
    if (!btn) return 'no Open button on the page';
    const r = btn.getBoundingClientRect();
    const top = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
    if (!top) return 'nothing at the centre of Open';
    return btn.contains(top) ? 'ok' : `covered by <${top.tagName.toLowerCase()} class="${(top.className || '').toString().slice(0, 70)}">`;
  });
  expect(hit, 'the Open button is not the thing on top of the Open button').toBe('ok');
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

/**
 * A FRAGMENT A DRAG CAN ACTUALLY START IN, both ways.
 *
 * Size alone is not the question and picking on size alone is what made this
 * spec flaky: the seed is random per boot, so some runs handed the biggest cell
 * to a fragment sitting on the floor of the screen — where the full-bleed rail
 * owns the pointer — or to one so short that the puck covers every legal grab
 * point. Both directions need a start point clear of the rail AND of the
 * centroid, so that is what is measured before area is even considered.
 */
const RAIL_PX = 96;
async function biggestCell(page: Page): Promise<number> {
  const boxes = await allBoxes(page);
  const vp = page.viewportSize() ?? { width: 1280, height: 720 };
  let best = -1, area = -1;
  boxes.forEach((b, i) => {
    const [, y, w, h] = b;
    const lo = y + 8;
    const hi = Math.min(y + h - 8, vp.height - RAIL_PX);
    if (hi - lo < 60 || h < 120) return;
    const a = w * h;
    if (a > area) { area = a; best = i; }
  });
  expect(best, 'no fragment is roomy enough to drag in — the partition is unusable').toBeGreaterThanOrEqual(0);
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
/**
 * WHERE A DRAG CAN START, ranked FURTHEST-FROM-THE-CENTROID FIRST.
 *
 * Two things cover the artwork and both take the pointerdown: the PUCK, which
 * sits on the centroid and is up to 196px wide, and the full-bleed RAIL, which
 * owns the bottom ~96px of the screen. Neither can be reasoned around from a
 * bounding box alone — a narrow fragment has no point at its own half-width
 * that clears a 98px puck arm — so the helper below TRIES a point and moves on
 * to the next when the grab did not take. That is also the honest model of the
 * gesture: a user whose thumb lands on a button tries somewhere else.
 */
function grabPoints(box: { x: number; y: number; width: number; height: number },
                    vp: { width: number; height: number }, dir: -1 | 1) {
  const lo = box.y + 8;
  const hi = Math.min(box.y + box.height - 8, vp.height - RAIL_PX);
  const cx0 = box.x + box.width / 2;
  const cy0 = box.y + box.height / 2;
  const ys = dir > 0 ? [0.18, 0.08, 0.32, 0.45] : [0.82, 0.92, 0.68, 0.55];
  const xs = [0.5, 0.08, 0.92, 0.25, 0.75];
  const pts: Array<[number, number]> = [];
  for (const fy of ys) for (const fx of xs) {
    const y = Math.max(lo, Math.min(box.y + box.height * fy, hi));
    pts.push([box.x + box.width * fx, y]);
  }
  return pts.sort((a, b) => Math.hypot(b[0] - cx0, b[1] - cy0) - Math.hypot(a[0] - cx0, a[1] - cy0));
}

async function dragPicture(page: Page, n: number, dir: -1 | 1, maxPasses = 24) {
  const start = await stableColour(page, n);
  let last = start;
  let settled = 0;
  let ci = 0;
  for (let p = 0; p < maxPasses; p++) {
    const box = await cells(page).nth(n).boundingBox();
    if (!box) throw new Error(`fragment ${n} has no box`);
    const vp = page.viewportSize() ?? { width: 1280, height: 720 };
    const pts = grabPoints(box, vp, dir);
    if (ci >= pts.length) throw new Error(`fragment ${n}: no point in it takes a drag`);
    const [sx, sy] = pts[ci];
    const room = dir > 0 ? vp.height - sy - 4 : sy - 4;
    const dy = dir * Math.max(60, room);
    await page.mouse.move(sx, sy);
    await page.mouse.down();
    for (let i = 1; i <= 20; i++) await page.mouse.move(sx, sy + (dy * i) / 20);
    await page.mouse.up();
    await page.waitForTimeout(300);
    const now = await stableColour(page, n);
    if (process.env.REFRAME_DEBUG) {
      const puck = await page.getByTestId('cell-actions').count();
      console.log(`[cell ${n} drag ${dir > 0 ? 'down' : 'up'} pass ${p} pt${ci}] start=(${Math.round(sx)},${Math.round(sy)}) dy=${Math.round(dy)} colour=${now.map(Math.round)} puck=${puck}`);
    }
    const moved = dist(now, last) >= 3;
    if (moved) { settled = 0; last = now; continue; }
    // A PASS THAT MOVED NOTHING on a picture that has not moved AT ALL is a
    // grab that never landed, never the clamp. Try the next point before
    // believing the photograph has run out.
    if (dist(now, start) < 3) { ci++; last = now; continue; }
    settled++;
    if (settled >= 2) { await page.waitForTimeout(300); return; }
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

    // WHICH SOURCE IS THIS, AND WHERE ON IT? Asked of the readings themselves.
    const fd = fitSource(afterDown);
    const fu = fitSource(afterUp);
    expect(fd.resid, `down=${afterDown.map(Math.round)} must lie on one source's gradient`).toBeLessThan(35);
    expect(fu.resid, `up=${afterUp.map(Math.round)} must lie on one source's gradient`).toBeLessThan(35);
    expect(fu.s, 'both ends must be the SAME photograph').toBe(fd.s);
    expect(fd.t, 'dragging down must park at the TOP of the photograph').toBeLessThan(0.3);
    expect(fu.t, 'dragging up must park at the BOTTOM of it').toBeGreaterThan(0.7);
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
    // 30, NOT 60. How far a drag can travel in RGB depends on the seed — which
    // photograph landed in the biggest fragment, and how much of it the crop
    // already showed — so a threshold set from one lucky deal fails on an
    // unlucky one (measured: 49.5 on a run this file used to call a no-op).
    // 30 is the smallest number that still makes the restore assertion below
    // non-vacuous, because it is outside that assertion's own 22-RGB band.
    expect(dist(moved, before), 'the drag must have done something to measure').toBeGreaterThan(30);

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

    // Which photograph is parked at its top? That is the corrected one.
    const fm = fitSource(moved);
    expect(fm.resid, `the drag must land on a recognisable source (${moved.map(Math.round)})`).toBeLessThan(35);
    expect(fm.t, 'and it must be parked at the top of it').toBeLessThan(0.3);
    const s = fm.s;

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
    const found = after.some((c) => {
      const f = fitSource(c);
      return f.s === s && f.resid < 35 && f.t < 0.35;
    });
    expect(
      found,
      `source ${s} must still be parked at its top somewhere after the re-deal (top ${TOP(s)}); saw ${JSON.stringify(after.map((c) => c.map(Math.round)))}`,
    ).toBe(true);
  });

  /**
   * T4 — THE CORRECTION IS IN THE FILE.
   *
   * The three tests above prove the reframe on SCREEN. This one proves it in the
   * ARTIFACT, and it is the test that was red before the commit shipped: the SVG
   * is this app's project file, it already DREW the corrected crop, and it
   * carried "the pool's own untouched analyses" — which did not include the one
   * thing in an analysis a person put there. So the file rendered one collage
   * and REOPENED as another, silently, and the crash-safe autosave (which
   * serialises the same analyses) dropped the correction with it.
   *
   * BYTE-IDENTICAL IS THE ASSERTION, not "looks similar". Every `<image>` in the
   * file carries the transform its crop produced, so a lost frame moves bytes;
   * S1 in svg-project.spec.ts proves the round trip is exact for everything
   * else, which is what makes equality here a claim about the frame alone.
   */
  test('T4 — the correction travels in the file: export, reload, open, export again', async ({ page }) => {
    test.setTimeout(300_000);
    await boot(page);
    await enterFullBleed(page);

    const target = await biggestCell(page);
    const before = await stableColour(page, target);
    await armCell(page, target);
    await dragPicture(page, target, 1);
    const moved = await stableColour(page, target);
    // 30 for the reason T2 above spells out: the travel a drag can express is
    // a property of the seed, not of the gesture.
    expect(dist(moved, before), 'the drag must have done something to measure').toBeGreaterThan(30);

    // Out of full bleed and back to the ordinary preview, which is what the
    // colour fingerprint below is read from on both sides of the round trip.
    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    await page.waitForTimeout(1200);
    const fingerprint = await allColours(page);

    const first = await downloadSvg(page);
    expect(first, 'the export carries a project manifest').toContain('id="collage-project"');
    expect(
      first,
      'THE CLAIM: the hand-set frame is in the manifest the file carries',
    ).toMatch(/"frame":\s*\{\s*"x"/);

    const path = onDisk('reframed.svg', first);

    // RELOAD. Nothing survives in memory — the file is the only thing carrying
    // this correction, which is the whole point.
    await page.goto(APP_URL);
    await page.waitForTimeout(1200);
    expect(await page.locator('img[src^="blob:"], canvas').count(), 'a collage survived the reload').toBe(0);
    await expectOpenReachable(page);

    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(2600);

    // WHAT A PERSON SEES: the same photographs, showing the same parts of
    // themselves. Read off the rendered preview, fragment by fragment.
    const after = await allColours(page);
    expect(after.length, 'the reopened project has the same number of fragments').toBe(fingerprint.length);
    const worst = Math.max(...after.map((c, i) => dist(c, fingerprint[i])));
    expect(
      worst,
      `a fragment came back cropped somewhere else (worst ${Math.round(worst)} RGB apart)\n` +
        `  saved: ${JSON.stringify(fingerprint.map((c) => c.map(Math.round)))}\n` +
        `  opened: ${JSON.stringify(after.map((c) => c.map(Math.round)))}`,
    ).toBeLessThan(24);

    // AND THE FILE IT PRODUCES IS THE FILE IT CAME FROM.
    const second = await downloadSvg(page);
    expect(
      second.length,
      `the reopened project re-exports a different file (${first.length} bytes out, ${second.length} back)`,
    ).toBe(first.length);
    expect(second === first, 'the round trip is not byte-exact').toBe(true);
  });

  /**
   * T5 — RECENTRE REACHES A CORRECTION MADE IN A PREVIOUS SESSION.
   *
   * The verb used to be gated on the in-memory Map, so a picture corrected,
   * saved and reopened drew its correction with no way back — the way IN is a
   * drag and the way OUT was gone. The predicate now asks the PHOTOGRAPH.
   */
  test('T5 — the way back survives the round trip', async ({ page }) => {
    test.setTimeout(300_000);
    await boot(page);
    await enterFullBleed(page);

    const target = await biggestCell(page);
    const before = await stableColour(page, target);
    await armCell(page, target);
    await dragPicture(page, target, 1);
    expect(dist(await stableColour(page, target), before), 'the drag must have done something').toBeGreaterThan(30);

    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    await page.waitForTimeout(1000);
    const path = onDisk('recentre.svg', await downloadSvg(page));

    await page.goto(APP_URL);
    await page.waitForTimeout(1200);
    await expectOpenReachable(page);
    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(2600);

    await enterFullBleed(page);
    // THE SAME FRAGMENT, and that is T4's result rather than an assumption: the
    // reopened project re-exports byte for byte, so the deal it came back with
    // is the deal it was saved with and the corrected picture is in the slot it
    // was corrected in. Hunting for it by arming every cell in turn is what the
    // first version did, and it was silently vacuous — `armCell` returns as soon
    // as ANY puck is up, so after the first iteration it never clicked again.
    await armCell(page, target);
    const recentre = page.getByTestId('cell-actions').getByTestId('cell-recentre');
    await expect(
      recentre,
      'a reopened correction offers no way back — the verb was gated on memory',
    ).toBeVisible({ timeout: 15_000 });

    const wasCorrected = await stableColour(page, target);
    await recentre.click();
    await page.waitForTimeout(1400);
    const back = await stableColour(page, target);
    expect(dist(back, wasCorrected), 'Recentre on a reopened correction must actually move the picture').toBeGreaterThan(30);
    await expect(
      page.getByTestId('cell-actions').getByTestId('cell-recentre'),
      'and the verb retires with the correction',
    ).toHaveCount(0);
  });
  /**
   * T6 — THE CRASH-SAFE SNAPSHOT CARRIES IT TOO.
   *
   * The third writer, and the one nobody would notice was missing until they
   * needed it: `flushSession` serialises the same analyses the archive and the
   * SVG do, so before this the autosave that exists to survive an OOM during a
   * 4K capture wrote the pool WITHOUT the correction — you would come back to
   * your collage with every photograph cropped where the detector had put it.
   *
   * Read straight out of IndexedDB rather than through a restore, because the
   * claim is about what was WRITTEN. The restore path itself is covered by
   * session-recovery.spec, and driving it here would test that file's subject
   * instead of this one's.
   */
  test('T6 — the autosave writes the correction into the session', async ({ page }) => {
    test.setTimeout(240_000);
    await boot(page);
    await enterFullBleed(page);

    const target = await biggestCell(page);
    const before = await stableColour(page, target);
    await armCell(page, target);
    await dragPicture(page, target, 1);
    expect(dist(await stableColour(page, target), before), 'the drag must have done something').toBeGreaterThan(30);

    // Past the debounce (AUTOSAVE_DEBOUNCE_MS = 1500) with room for the write.
    await page.waitForTimeout(4000);

    const manifest = await page.evaluate(async () => {
      const db: IDBDatabase = await new Promise((res, rej) => {
        const rq = indexedDB.open('collage-session', 2);
        rq.onsuccess = () => res(rq.result);
        rq.onerror = () => rej(rq.error);
      });
      const rec: any = await new Promise((res, rej) => {
        const rq = db.transaction('project', 'readonly').objectStore('project').get('current');
        rq.onsuccess = () => res(rq.result);
        rq.onerror = () => rej(rq.error);
      });
      db.close();
      return rec?.manifest ?? null;
    });

    expect(manifest, 'nothing was autosaved at all').not.toBeNull();
    const framed = (manifest.images ?? []).filter((i: any) => i?.analysis?.frame);
    expect(
      framed.length,
      `the snapshot carries ${manifest.images?.length ?? 0} images and not one correction — ` +
        'a crash here would come back with the crop the detector chose',
    ).toBe(1);
    const f = framed[0].analysis.frame;
    expect(Number.isFinite(f.x) && Number.isFinite(f.y), 'the frame in the snapshot is not a pair of numbers').toBe(true);
  });
});
