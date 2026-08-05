/**
 * MOBILE-WATERTIGHT — a SHIP GATE, asserted on the real page, not eyeballed.
 *
 * Operator law (2026-08-04): "must be mobile friendly always — don't make
 * anything that's gonna clip or alter if zoomed out on phone." These pages get
 * used one-handed, on a phone, in a hallway. A screenshot of a render is not
 * this verification: it drives the app at the four widths that matter and reads
 * the numbers back out of the layout engine.
 *
 * Run (dev):  npx playwright test --config playwright.mobile.config.ts
 * Run (live): COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *               npx playwright test --config playwright.mobile.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** The widths a real phone actually reports, smallest first. */
const WIDTHS = [320, 360, 390, 430];

function makePng(r: number, g: number, b: number, size = 64): Buffer {
  const w = size, h = size;
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2;
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) { row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b; }
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const idat = zlib.deflateSync(raw);
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

const shots = () => Array.from({ length: 6 }, (_, i) => ({
  name: `m-${i}.png`,
  mimeType: 'image/png',
  buffer: makePng(30 + i * 40, 90, 200 - i * 25),
}));

/** Horizontal overflow, and the widest element responsible for it. */
async function overflow(page: Page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const over = doc.scrollWidth - doc.clientWidth;
    const worst: { tag: string; cls: string; right: number }[] = [];
    if (over > 0) {
      document.querySelectorAll('*').forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.right > doc.clientWidth + 1) {
          worst.push({ tag: el.tagName, cls: String((el as HTMLElement).className).slice(0, 60), right: Math.round(r.right) });
        }
      });
      worst.sort((a, b) => b.right - a.right);
    }
    return { over, clientWidth: doc.clientWidth, worst: worst.slice(0, 5) };
  });
}

/** Any interactive control whose hit box is under the one-thumb minimum. */
async function smallTargets(page: Page) {
  return page.evaluate(() => {
    const bad: { tag: string; label: string; w: number; h: number }[] = [];
    document.querySelectorAll('button, [role="button"], a[href], input[type="checkbox"], input[type="radio"]')
      .forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) return;                 // not rendered
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none') return;
        if (r.height < 44 - 0.5 || r.width < 44 - 0.5) {
          bad.push({
            tag: el.tagName,
            label: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 40),
            w: Math.round(r.width), h: Math.round(r.height),
          });
        }
      });
    return bad;
  });
}

for (const width of WIDTHS) {
  test(`no horizontal overflow and thumb-sized controls at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 780 });
    await page.goto(APP_URL);
    await page.locator('input[type="file"]').first().setInputFiles(shots());
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });

    const before = await overflow(page);
    expect(before.over, `simple tab overflows by ${before.over}px — ${JSON.stringify(before.worst)}`).toBeLessThanOrEqual(0);

    // The panel carrying the new arrangement + focus pickers.
    await page.getByRole('button', { name: 'Settings' }).first().click();
    await page.waitForTimeout(400);

    const after = await overflow(page);
    expect(after.over, `advanced tab overflows by ${after.over}px — ${JSON.stringify(after.worst)}`).toBeLessThanOrEqual(0);

    // Both new pickers are present and scrollable rather than wrapped off-screen.
    for (const group of ['Arrangement', 'Crop focus']) {
      const row = page.getByRole('group', { name: group });
      await expect(row).toBeVisible();
      const fits = await row.evaluate((el) => el.scrollWidth >= el.clientWidth && el.clientWidth <= document.documentElement.clientWidth);
      expect(fits, `${group} row is wider than the viewport instead of scrolling inside it`).toBe(true);
    }

    const small = await smallTargets(page);
    expect(small, `controls under 44px: ${JSON.stringify(small)}`).toEqual([]);
  });
}

test('zoomed out, the page still does not scroll sideways', async ({ page }) => {
  // "don't make anything that's gonna clip or alter if zoomed out on phone" —
  // a pinch-out is a wider layout viewport at the same CSS width, which is what
  // a small viewport with a large deviceScaleFactor reproduces.
  await page.setViewportSize({ width: 320, height: 600 });
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(shots());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.waitForTimeout(400);
  for (const scale of [0.5, 0.67, 0.8]) {
    await page.evaluate((s) => {
      document.documentElement.style.zoom = String(s);
    }, scale);
    await page.waitForTimeout(250);
    const o = await overflow(page);
    expect(o.over, `zoom ${scale} overflows by ${o.over}px — ${JSON.stringify(o.worst)}`).toBeLessThanOrEqual(0);
  }
  await page.evaluate(() => { document.documentElement.style.zoom = ''; });
});
