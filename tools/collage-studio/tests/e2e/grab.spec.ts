/**
 * THE GRAB AT THE ARTIFACT — press any fragment, drag its picture, let go.
 *
 * THE WISH, verbatim (anonymous Collage user, 2026-09-23): "Wish I had the
 * ability to move the image or video around if I click a tile and hold down
 * with a finger and drag and release to set new image focal point".
 *
 * THE BASELINE this spec exists to overturn, measured on the build before it:
 * that exact gesture — a real Chromium touch through CDP, held 600 ms, dragged
 * 160 px, released, on a Pixel 5 in the editing view — moved the picture 0.0
 * RGB. And the shipped reframe (full bleed, armed fragment) had a touch bug no
 * spec could see, because every spec drove `page.mouse`: a touch drag ends in no
 * click, so the flag meant to eat the drag's click survived and ate the NEXT
 * genuine tap. Measured: arm, drag by touch, tap once — the puck stayed up.
 *
 * SO EVERY TOUCH HERE IS A REAL ONE. `Input.dispatchTouchEvent` goes through
 * Chromium's own input pipeline — touch-action, pointer capture, the click a tap
 * synthesises and the one a drag does not — which `page.mouse` and synthetic
 * PointerEvents both skip. That makes the touch tests Chromium-only; WebKit has
 * no equivalent in Playwright, and iOS remains unverified on a device.
 *
 * THE INSTRUMENT is reframe.spec's: vertical-GRADIENT sources, so which part of
 * which photograph a fragment shows is a question the rendered pixels answer —
 * projected onto each source's gradient, `s` says WHICH photograph and `t` says
 * HOW FAR DOWN IT the fragment's centre sits. Dragging the picture DOWN shows
 * the part ABOVE, so `t` falls: direction and magnitude in one number.
 *
 * Run against the collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test -c playwright.grab.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test -c playwright.grab.config.ts
 */
import { test, expect, type Page, type CDPSession } from '@playwright/test';
import zlib from 'node:zlib';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const HERE = dirname(fileURLToPath(import.meta.url));
const GRAD_CLIP = join(HERE, '..', 'fixtures', 'grad_vertical.mp4');

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
  ihdr[8] = 8; ihdr[9] = 2;
  const rows: Buffer[] = [];
  for (let y = 0; y < h; y++) {
    const t = h > 1 ? y / (h - 1) : 0;
    const px = [0, 1, 2].map((k) => Math.round(top[k] + (bottom[k] - top[k]) * t));
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) { row[1 + x * 3] = px[0]; row[2 + x * 3] = px[1]; row[3 + x * 3] = px[2]; }
    rows.push(row);
  }
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(Buffer.concat(rows))), chunk('IEND', Buffer.alloc(0))]);
}

/** Four sources, eight ends, all >=110 apart in RGB — plus the clip's own grey ramp (240 -> 20). */
const SOURCES: Array<[RGB, RGB]> = [
  [[250, 20, 20], [20, 20, 250]],
  [[250, 250, 20], [20, 250, 250]],
  [[250, 140, 20], [20, 140, 250]],
  [[200, 20, 200], [20, 200, 20]],
];
const GREY: [RGB, RGB] = [[240, 240, 240], [20, 20, 20]];

type Fit = { s: number; t: number; resid: number };
function fitTo(c: RGB, ramps: Array<[RGB, RGB]>): Fit {
  let best: Fit = { s: -1, t: 0, resid: Infinity };
  ramps.forEach(([a, b], s) => {
    const d: RGB = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const len2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
    const raw = ((c[0] - a[0]) * d[0] + (c[1] - a[1]) * d[1] + (c[2] - a[2]) * d[2]) / len2;
    const t = Math.max(0, Math.min(1, raw));
    const resid = dist(c, [a[0] + d[0] * t, a[1] + d[1] * t, a[2] + d[2] * t]);
    if (resid < best.resid) best = { s, t, resid };
  });
  return best;
}

const tiles = () => SOURCES.map(([t, b], i) => ({ name: `grad-${i}.png`, mimeType: 'image/png', buffer: makeGradient(t, b) }));
const OVERLAY = 'svg[viewBox^="0 0 1200 "]';
const cells = (page: Page) => page.locator(`${OVERLAY} > g`);
const pins = (page: Page) => page.locator(`${OVERLAY} foreignObject`);

/** Mean colour of the RENDERED artwork at the centre of fragment `n`. */
async function cellColour(page: Page, n: number): Promise<RGB> {
  const out = await page.evaluate(({ n, sel }) => {
    const g = document.querySelectorAll(`${sel} > g`)[n] as unknown as SVGGraphicsElement | undefined;
    const el = (document.querySelector('[data-testid="studio-artwork"] canvas') as HTMLCanvasElement | null)
      ?? (document.querySelector('canvas') as HTMLCanvasElement | null)
      ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!g || !el) return null;
    const gb = g.getBoundingClientRect();
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
    const x = Math.min(c.width - 3, Math.max(2, Math.round(u * c.width)));
    const y = Math.min(c.height - 3, Math.max(2, Math.round(v * c.height)));
    const px = ctx.getImageData(x - 2, y - 2, 5, 5).data;
    let r = 0, g2 = 0, b = 0, k = 0;
    for (let i = 0; i < px.length; i += 4) { r += px[i]; g2 += px[i + 1]; b += px[i + 2]; k++; }
    return k ? [r / k, g2 / k, b / k] : null;
  }, { n, sel: OVERLAY });
  expect(out, `fragment ${n} must be measurable on the rendered artwork`).not.toBeNull();
  return out as RGB;
}

/** A read that has stopped moving — the preview is produced asynchronously. */
async function stableColour(page: Page, n: number, tries = 14): Promise<RGB> {
  let prev = await cellColour(page, n);
  for (let i = 0; i < tries; i++) {
    await page.waitForTimeout(200);
    const now = await cellColour(page, n);
    if (dist(now, prev) < 2) return now;
    prev = now;
  }
  return prev;
}

async function allColours(page: Page): Promise<RGB[]> {
  const n = await cells(page).count();
  const out: RGB[] = [];
  for (let i = 0; i < n; i++) out.push(await stableColour(page, i, 6));
  return out;
}

async function boxes(page: Page) {
  return page.evaluate((sel) => Array.from(document.querySelectorAll(`${sel} > g`), (g) => {
    const b = (g as unknown as SVGGraphicsElement).getBoundingClientRect();
    return { x: b.x, y: b.y, w: b.width, h: b.height };
  }), OVERLAY);
}

async function artBox(page: Page) {
  return page.evaluate((sel) => {
    const b = document.querySelector(sel)!.getBoundingClientRect();
    return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)].join(',');
  }, OVERLAY);
}

async function boot(page: Page, files: Parameters<ReturnType<Page['locator']>['setInputFiles']>[0] = tiles()) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
  }).catch(() => { /* no SW here is fine */ });
  await page.locator('input[type="file"]').first().setInputFiles(files);
  await expect(page.locator(`${OVERLAY} > g`).first()).toBeVisible({ timeout: 120_000 });
  // A rectangular partition, so a fragment's bounding-box centre is inside it.
  const tools = page.getByRole('navigation', { name: 'Studio tools' });
  await tools.getByRole('button', { name: 'Layout', exact: true }).click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.waitForTimeout(1200);
  await page.getByRole('button', { name: 'Close editing panel', exact: true }).click();
  await page.waitForTimeout(800);
}

/** A fragment roomy enough to drag in, wholly on screen, clear of the bottom controls. */
async function roomyCell(page: Page): Promise<number> {
  const bs = await boxes(page);
  const vp = page.viewportSize() ?? { width: 1280, height: 720 };
  let best = -1, area = -1;
  bs.forEach((b, i) => {
    if (b.y < 0 || b.y + b.h > vp.height - 60 || b.h < 110 || b.w < 60) return;
    if (b.w * b.h > area) { area = b.w * b.h; best = i; }
  });
  expect(best, 'no fragment is roomy enough to drag in').toBeGreaterThanOrEqual(0);
  return best;
}

// --- REAL TOUCH -------------------------------------------------------------
type Pt = { x: number; y: number; id?: number };
const touchPoints = (pts: Pt[]) => pts.map((p, i) => ({ x: p.x, y: p.y, id: p.id ?? i + 1, radiusX: 4, radiusY: 4, force: 1 }));
const tStart = (cdp: CDPSession, pts: Pt[]) => cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: touchPoints(pts) });
const tMove = (cdp: CDPSession, pts: Pt[]) => cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: touchPoints(pts) });
const tEnd = (cdp: CDPSession, remaining: Pt[] = []) => cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: touchPoints(remaining) });

async function touchTap(page: Page, cdp: CDPSession, x: number, y: number, holdMs = 70, jitter = 0) {
  await tStart(cdp, [{ x, y }]);
  if (jitter) { await page.waitForTimeout(20); await tMove(cdp, [{ x: x + jitter, y }]); }
  await page.waitForTimeout(holdMs);
  await tEnd(cdp);
  await page.waitForTimeout(450);
}

/** Press, optionally rest, drag `dy` in 16 steps, release. Returns the art box at press and just before release. */
async function touchDrag(page: Page, cdp: CDPSession, x: number, y: number, dy: number, restMs = 0) {
  await tStart(cdp, [{ x, y }]);
  const atPress = await artBox(page);
  if (restMs) await page.waitForTimeout(restMs);
  const litWhileHeld = await page.locator('[data-grabbed]').count();
  for (let i = 1; i <= 16; i++) { await tMove(cdp, [{ x, y: y + (dy * i) / 16 }]); await page.waitForTimeout(16); }
  const beforeRelease = await artBox(page);
  await tEnd(cdp);
  await page.waitForTimeout(500);
  return { atPress, beforeRelease, litWhileHeld };
}

/** Which way the finger has room to go: toward the part of the photograph the crop is NOT showing. */
const fingerDir = (t: number) => (t < 0.5 ? -1 : 1);

test.describe('THE GRAB — press any fragment, drag its picture, let go', () => {
  test('touch, editing view: the wisher\'s gesture moves the picture; taps still pin; the first tap after a drag acts; Undo takes it back; a second finger puts it back', async ({ page, browserName, isMobile }) => {
    test.skip(browserName !== 'chromium' || !isMobile, 'real touch needs CDP — Mobile Chrome only');
    test.setTimeout(240_000);
    await boot(page);
    const cdp = await page.context().newCDPSession(page);
    const n = await roomyCell(page);
    const b = (await boxes(page))[n];
    const cx = b.x + b.w / 2;
    const cy = b.y + b.h / 2;

    const all0 = await allColours(page);
    const c0 = await stableColour(page, n);
    const f0 = fitTo(c0, SOURCES);
    expect(f0.resid, 'the fragment shows one of the four gradients').toBeLessThan(12);

    // 1. A PLAIN TAP PINS — and moves NOTHING else: no notice row appears to
    //    reflow the artwork under the next tap (the C3748 audit measured a
    //    teaching notice pushing the art 37 px down, so a quick second tap
    //    pinned the fragment above the one aimed at; the notice was cut).
    const pinned0 = await pins(page).count();
    const art0 = await artBox(page);
    await touchTap(page, cdp, cx, cy);
    await expect(pins(page)).toHaveCount(pinned0 + 1);
    expect(await artBox(page), 'a tap reflowed the artwork').toBe(art0);
    expect(dist(await stableColour(page, n), c0), 'a tap moved the picture').toBeLessThan(4);
    await touchTap(page, cdp, cx, cy);                       // and unpins
    await expect(pins(page)).toHaveCount(pinned0);

    // 2. A TAP THAT WANDERS 8 PX ON GLASS IS STILL A TAP — it pins, moves nothing.
    await touchTap(page, cdp, cx, cy, 70, 8);
    await expect(pins(page)).toHaveCount(pinned0 + 1);
    expect(dist(await stableColour(page, n), c0), 'an 8 px tremble reframed the picture').toBeLessThan(4);
    await touchTap(page, cdp, cx, cy);
    await expect(pins(page)).toHaveCount(pinned0);

    // 3. THE WISHER'S GESTURE: press, hold, drag, release — and the art band
    //    must not move under the finger at any point of it.
    const dir = fingerDir(f0.t);
    const dy = dir * Math.min(140, b.h * 0.6);
    const g = await touchDrag(page, cdp, cx, cy - dy / 2, dy, 600);
    expect(g.litWhileHeld, 'the held fragment lights up before it moves').toBe(1);
    expect(g.beforeRelease, 'the artwork moved under the finger mid-drag').toBe(g.atPress);
    await expect(page.locator('[data-grabbed]')).toHaveCount(0);
    const c1 = await stableColour(page, n);
    const f1 = fitTo(c1, SOURCES);
    expect(f1.s, 'the fragment still shows the same photograph').toBe(f0.s);
    // finger DOWN shows the part ABOVE (t falls); finger UP shows the part below
    expect((f1.t - f0.t) * -dir, `the picture did not follow the finger (t ${f0.t.toFixed(3)} -> ${f1.t.toFixed(3)})`).toBeGreaterThan(0.03);
    await expect(pins(page), 'the drag pinned the fragment').toHaveCount(pinned0);
    const all1 = await allColours(page);
    all0.forEach((c, i) => { if (i !== n) expect(dist(all1[i], c), `fragment ${i} moved with fragment ${n}`).toBeLessThan(6); });

    // 4. THE FIRST TAP AFTER A TOUCH DRAG ACTS (the shipped bug ate it).
    await touchTap(page, cdp, cx, cy);
    await expect(pins(page), 'the first tap after a touch drag was eaten').toHaveCount(pinned0 + 1);
    await touchTap(page, cdp, cx, cy);
    await expect(pins(page)).toHaveCount(pinned0);

    // 5. PRESS AND GO: no rest before moving — still a drag, further the same way.
    await touchDrag(page, cdp, cx, cy - dy / 2, dy, 0);
    const c2 = await stableColour(page, n);
    const f2 = fitTo(c2, SOURCES);
    expect((f2.t - f1.t) * -dir, 'press-and-go did not drag').toBeGreaterThan(0.01);

    // 6. UNDO TAKES IT BACK, one drag per step; REDO puts it forward again.
    const tools = page.getByRole('navigation', { name: 'Studio tools' });
    await tools.getByRole('button', { name: 'Layout', exact: true }).click();
    await page.getByTestId('undo-dock').click();
    await page.waitForTimeout(600);
    expect(fitTo(await stableColour(page, n), SOURCES).t, 'undo did not take back the second drag').toBeCloseTo(f1.t, 1);
    await page.getByTestId('undo-dock').click();
    await page.waitForTimeout(600);
    expect(dist(await stableColour(page, n), c0), 'two undos did not bring back the untouched picture').toBeLessThan(6);
    await page.getByTestId('redo-dock').click();
    await page.waitForTimeout(600);
    expect(fitTo(await stableColour(page, n), SOURCES).t, 'redo did not put the first drag back').toBeCloseTo(f1.t, 1);
    await page.getByRole('button', { name: 'Close editing panel', exact: true }).click();
    await page.waitForTimeout(600);

    // 7. A SECOND FINGER MID-DRAG PUTS THE PICTURE BACK and records nothing.
    const before7 = await stableColour(page, n);
    const b7 = (await boxes(page))[n];
    const x7 = b7.x + b7.w / 2, y7 = b7.y + b7.h / 2 - dy / 2;
    await tStart(cdp, [{ x: x7, y: y7, id: 1 }]);
    for (let i = 1; i <= 10; i++) { await tMove(cdp, [{ x: x7, y: y7 + (dy * i) / 10, id: 1 }]); await page.waitForTimeout(16); }
    await page.waitForTimeout(300);
    const mid = await stableColour(page, n, 4);
    expect(dist(mid, before7), 'the first finger never moved the picture').toBeGreaterThan(4);
    await tStart(cdp, [{ x: x7, y: y7 + dy, id: 1 }, { x: x7 + 30, y: y7, id: 2 }]);
    await page.waitForTimeout(120);
    await tEnd(cdp, [{ x: x7, y: y7 + dy, id: 1 }]);
    await tEnd(cdp);
    await page.waitForTimeout(600);
    expect(dist(await stableColour(page, n), before7), 'a second finger did not put the picture back').toBeLessThan(6);
  });

  test('touch, full bleed: an UNARMED fragment drags without arming; the armed one still drags; one tap after disarms', async ({ page, browserName, isMobile }) => {
    test.skip(browserName !== 'chromium' || !isMobile, 'real touch needs CDP — Mobile Chrome only');
    test.setTimeout(200_000);
    await boot(page);
    const cdp = await page.context().newCDPSession(page);
    await page.getByRole('button', { name: 'Expand preview', exact: true }).first().click();
    await expect(page.getByRole('button', { name: 'Back to editing', exact: true }).first()).toBeVisible({ timeout: 15_000 });
    await page.waitForTimeout(800);
    const puck = page.getByTestId('cell-actions');
    const n = await roomyCell(page);
    const b = (await boxes(page))[n];
    const x = b.x + b.w * 0.25, y0 = b.y + b.h * 0.3;
    const c0 = await stableColour(page, n);
    const f0 = fitTo(c0, SOURCES);
    const dir = fingerDir(f0.t);
    const dy = dir * Math.min(100, b.h * 0.35);

    // an unarmed fragment: the drag moves it and arms nothing
    await touchDrag(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy), dy, 0);
    expect(await puck.count(), 'a drag armed the fragment').toBe(0);
    const f1 = fitTo(await stableColour(page, n), SOURCES);
    expect((f1.t - f0.t) * -dir, 'an unarmed fragment did not drag in full bleed').toBeGreaterThan(0.02);

    // arm it, drag the armed one (the shipped path), then ONE tap disarms
    await touchTap(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy));
    await expect(puck).toHaveCount(1);
    await touchDrag(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy), -dy, 0);
    await expect(puck, 'the drag disarmed the fragment it was correcting').toHaveCount(1);
    await touchTap(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy));
    await expect(puck, 'the first tap after a touch drag was eaten (the shipped bug)').toHaveCount(0);

    // RECENTRE IS ONE UNDO STEP, like the drag it reverses: Recentre, then the
    // rail's Undo, and the hand-set frame is back (before C3748 that Undo
    // restored a snapshot equal to the screen and spent itself).
    await touchTap(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy));
    await expect(puck).toHaveCount(1);
    const dragged = await stableColour(page, n);
    await page.getByTestId('cell-recentre').click();
    await page.waitForTimeout(500);
    expect(dist(await stableColour(page, n), c0), 'Recentre did not restore the automatic crop').toBeLessThan(6);
    await page.getByTestId('undo').click();
    await page.waitForTimeout(700);
    expect(dist(await stableColour(page, n), dragged), 'Undo after Recentre did not bring the hand-set frame back').toBeLessThan(6);
    if (await puck.count()) await touchTap(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy));
    await expect(puck).toHaveCount(0);

    // A PENDING TRADE OWNS THE CANVAS: with Swap armed, a drag on another
    // fragment moves nothing and the trade is still waiting for its partner.
    await touchTap(page, cdp, x, dir > 0 ? y0 : y0 + Math.abs(dy));
    await expect(puck).toHaveCount(1);
    const swapBtn = page.getByTestId('cell-swap');
    await expect(swapBtn, 'four different photographs: the armed fragment must be tradeable').toHaveCount(1);
    {
      await swapBtn.click();
      await expect(page.getByTestId('swap-pending')).toBeVisible();
      const all = await boxes(page);
      const other = all.findIndex((bx, i) => i !== n && bx.h > 90 && bx.y > 0 && bx.y + bx.h < (page.viewportSize()?.height ?? 800) - 100);
      expect(other, 'no second fragment to drag on').toBeGreaterThanOrEqual(0);
      const ob = all[other];
      const oc0 = await stableColour(page, other);
      await touchDrag(page, cdp, ob.x + ob.w * 0.75, ob.y + ob.h * 0.3, Math.min(90, ob.h * 0.4), 0);
      expect(dist(await stableColour(page, other), oc0), 'a drag moved a picture while a trade was pending').toBeLessThan(6);
      await expect(page.getByTestId('swap-pending'), 'the drag cancelled or completed the pending trade').toBeVisible();
      await page.getByTestId('swap-cancel').click();
      await expect(page.getByTestId('swap-pending')).toHaveCount(0);
    }
  });

  test('touch, a video clip: the clip\'s picture follows the finger and the clip keeps playing', async ({ page, browserName, isMobile }) => {
    test.skip(browserName !== 'chromium' || !isMobile, 'real touch needs CDP — Mobile Chrome only');
    test.setTimeout(200_000);
    await boot(page, [...tiles().slice(0, 3), { name: 'grad_vertical.mp4', mimeType: 'video/mp4', buffer: readFileSync(GRAD_CLIP) }]);
    const cdp = await page.context().newCDPSession(page);
    await expect.poll(() => page.evaluate(() => Array.from(document.querySelectorAll('video')).some((v) => v.readyState >= 2 && !v.paused)), { timeout: 60_000 }).toBe(true);
    // WHICH fragment holds the clip: the one whose colour fits the grey ramp
    const count = await cells(page).count();
    let n = -1;
    for (let i = 0; i < count; i++) {
      const c = await stableColour(page, i, 6);
      const grey = fitTo(c, [GREY]);
      const colour = fitTo(c, SOURCES.slice(0, 3));
      if (grey.resid < 10 && grey.resid < colour.resid) { n = i; break; }
    }
    expect(n, 'no fragment is showing the grey clip').toBeGreaterThanOrEqual(0);
    const b = (await boxes(page))[n];
    const f0 = fitTo(await stableColour(page, n), [GREY]);
    const dir = fingerDir(f0.t);
    const dy = dir * Math.min(120, b.h * 0.5);
    const t0 = await page.evaluate(() => Math.max(...Array.from(document.querySelectorAll('video')).map((v) => v.currentTime)));
    await touchDrag(page, cdp, b.x + b.w / 2, b.y + b.h / 2 - dy / 2, dy, 400);
    const f1 = fitTo(await stableColour(page, n), [GREY]);
    expect((f1.t - f0.t) * -dir, `the clip's picture did not follow the finger (t ${f0.t.toFixed(3)} -> ${f1.t.toFixed(3)})`).toBeGreaterThan(0.03);
    await page.waitForTimeout(700);
    const t1 = await page.evaluate(() => Math.max(...Array.from(document.querySelectorAll('video')).map((v) => v.currentTime)));
    // a 3 s looping clip: "keeps playing" is "the playhead is not parked where it was"
    expect(Math.abs(t1 - t0), 'the clip stopped playing').toBeGreaterThan(0.05);
  });

  test('mouse, editing view: a drag moves the picture and pins nothing; a click still pins', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'desktop mouse');
    test.setTimeout(180_000);
    await boot(page);
    const n = await roomyCell(page);
    const b = (await boxes(page))[n];
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
    const c0 = await stableColour(page, n);
    const f0 = fitTo(c0, SOURCES);
    const pinned0 = await pins(page).count();

    await page.mouse.click(cx, cy);
    await expect(pins(page), 'a click did not pin').toHaveCount(pinned0 + 1);
    await page.mouse.click(cx, cy);
    await expect(pins(page)).toHaveCount(pinned0);

    const dir = fingerDir(f0.t);
    const dy = dir * Math.min(140, b.h * 0.6);
    await page.mouse.move(cx, cy - dy / 2);
    await page.mouse.down();
    for (let i = 1; i <= 16; i++) await page.mouse.move(cx, cy - dy / 2 + (dy * i) / 16);
    await page.mouse.up();
    await page.waitForTimeout(500);
    const f1 = fitTo(await stableColour(page, n), SOURCES);
    expect((f1.t - f0.t) * -dir, 'a mouse drag did not move the picture').toBeGreaterThan(0.03);
    await expect(pins(page), 'the drag\'s own click pinned the fragment').toHaveCount(pinned0);
    await page.mouse.click(cx, cy);
    await expect(pins(page), 'the next click after a drag did not pin').toHaveCount(pinned0 + 1);
    await page.mouse.click(cx, cy);
    await expect(pins(page)).toHaveCount(pinned0);

    // ESCAPE CANCELS A LIVE DRAG: the picture goes back to where the press
    // found it, no view changes under the pointer, nothing is pinned.
    const held = await stableColour(page, n);
    const art = await artBox(page);
    await page.mouse.move(cx, cy - dy / 2);
    await page.mouse.down();
    for (let i = 1; i <= 10; i++) await page.mouse.move(cx, cy - dy / 2 + (dy * i) / 10);
    await page.waitForTimeout(300);
    expect(dist(await stableColour(page, n, 4), held), 'the drag never moved the picture').toBeGreaterThan(4);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
    expect(await artBox(page), 'Escape changed the view under a live drag').toBe(art);
    await page.mouse.up();
    await page.waitForTimeout(500);
    expect(dist(await stableColour(page, n), held), 'Escape did not put the picture back').toBeLessThan(6);
    await expect(pins(page), 'the cancelled drag pinned the fragment').toHaveCount(pinned0);
  });

  test('the written instruction and the credit sit under Crop focus', async ({ page }) => {
    test.setTimeout(120_000);
    await boot(page);
    const tools = page.getByRole('navigation', { name: 'Studio tools' });
    await tools.getByRole('button', { name: 'Layout', exact: true }).click();
    await page.getByRole('group', { name: 'Layout controls' }).getByRole('button').filter({ hasText: /canvas/i }).first().click();
    const credit = page.getByTestId('grab-credit');
    await expect(credit).toContainText('Drag any picture on the artwork to move it inside its fragment');
    await expect(credit).toContainText('anonymous Collage user');
    await credit.scrollIntoViewIfNeeded();
    await expect(credit).toBeVisible();
  });
});
