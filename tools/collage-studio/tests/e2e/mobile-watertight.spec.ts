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
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const HERE = dirname(fileURLToPath(import.meta.url));
/** A real video, because the video dock does not exist without one. */
const RAMP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');

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

/**
 * THE GATE COULD NOT SEE THE VIDEO DOCK, AND THE VIDEO DOCK WAS THE PART THAT
 * FAILED.
 *
 * Every test above imports PNGs, so the whole live-stage transport — clip chips,
 * trim, per-clip sound, play/pause, monitor, take length, Record — simply does
 * not exist while they run, and the suite reported the app watertight for months
 * on the strength of the photo-only page. Measured at 390px with one video
 * loaded: ELEVEN controls under the law, from `Stop playing` at 24x28 to
 * `Record video` — the button that starts an export — at 32x32.
 *
 * A gate that grades the easy half is the same defect as a test driving only the
 * geometry-independent twist mode, one layer up: it is green for a reason that
 * has nothing to do with the thing being asserted.
 */
test('the VIDEO dock is thumb-sized too, at 320/360/390/430', async ({ page }) => {
  test.setTimeout(300_000);
  await page.setViewportSize({ width: 390, height: 780 });
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles([RAMP]);
  await expect(page.locator('canvas').first()).toBeVisible({ timeout: 200_000 });
  // The dock only renders once the clip is admitted — wait for the clip's own
  // chip rather than a timer, so a slow decode does not silently grade an empty
  // bar and call it a pass.
  await expect(page.getByRole('button', { name: 'Trim ramp_rgb.mp4' }))
    .toBeVisible({ timeout: 200_000 });

  for (const width of WIDTHS) {
    await page.setViewportSize({ width, height: 780 });
    await page.waitForTimeout(300);

    const o = await overflow(page);
    expect(o.over, `the video dock overflows by ${o.over}px at ${width} — ${JSON.stringify(o.worst)}`)
      .toBeLessThanOrEqual(0);

    const small = await smallTargets(page);
    expect(small, `video-dock controls under 44px at ${width}px: ${JSON.stringify(small)}`).toEqual([]);

    // The take button is the one control that must never be pushed off-screen:
    // it is the reason the dock exists, and a wrapped row is exactly how a
    // primary action ends up behind a horizontal scroll nobody discovers.
    const rec = page.getByRole('button', { name: 'Record video' });
    const box = await rec.boundingBox();
    expect(box, 'Record video must be laid out').not.toBeNull();
    expect(box!.x + box!.width, `Record video sits past the right edge at ${width}px`)
      .toBeLessThanOrEqual(width + 0.5);
  }
});

test('the export sheet\'s VIDEO SIZE row is watertight at 320/360/390/430', async ({ page }) => {
  // The size ladder only exists when a clip is on the canvas (video is the only
  // thing it applies to) and it is the newest control in the sheet — a wrapping
  // row of rungs, which is precisely the shape that runs off a 320px screen.
  test.setTimeout(300_000);
  await page.setViewportSize({ width: 390, height: 780 });
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles([RAMP]);
  await expect(page.locator('canvas').first()).toBeVisible({ timeout: 200_000 });
  await expect(page.getByRole('button', { name: 'Trim ramp_rgb.mp4' }))
    .toBeVisible({ timeout: 200_000 });

  for (const width of WIDTHS) {
    await page.setViewportSize({ width, height: 780 });
    await page.waitForTimeout(300);

    // Open the sheet fresh at each width: the row is laid out on open, and a
    // sheet that was opened wide and then narrowed is not the case a phone hits.
    await page.getByRole('button', { name: /export/i }).first().click();
    const sheet = page.getByRole('dialog');
    await expect(sheet).toBeVisible({ timeout: 20_000 });

    const sizeRow = page.getByRole('radiogroup', { name: 'Video size' });
    // The probe is async; on a device with no encoder there is legitimately no
    // row, and asserting its absence is not this test's job.
    if (await sizeRow.count() > 0) {
      await expect(sizeRow).toBeVisible();
      // Every rung sits inside the viewport — a rung you have to scroll
      // sideways to find is a rung nobody picks.
      const rungs = sizeRow.getByRole('radio');
      const n = await rungs.count();
      expect(n, 'the size row rendered with no rungs').toBeGreaterThan(0);
      for (let i = 0; i < n; i++) {
        const box = await rungs.nth(i).boundingBox();
        expect(box, `rung ${i} is not laid out at ${width}px`).not.toBeNull();
        expect(box!.x + box!.width, `size rung ${i} runs past the right edge at ${width}px`)
          .toBeLessThanOrEqual(width + 0.5);
        expect(box!.height, `size rung ${i} is under a thumb at ${width}px`).toBeGreaterThanOrEqual(44 - 0.5);
      }
    }

    const o = await overflow(page);
    expect(o.over, `the export sheet overflows by ${o.over}px at ${width} — ${JSON.stringify(o.worst)}`)
      .toBeLessThanOrEqual(0);

    const small = await smallTargets(page);
    expect(small, `export-sheet controls under 44px at ${width}px: ${JSON.stringify(small)}`).toEqual([]);

    await page.keyboard.press('Escape');
    await expect(sheet).toBeHidden({ timeout: 10_000 });
  }
});

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
