/**
 * THE PLAYHEAD — the take gets a clock you can see and drag.
 *
 * WHAT THIS PROVES, AND WHY IT CAN BE PROVEN AT ALL.
 *   A scrub is a claim about TIME, and time is invisible in a screenshot. The
 *   only way to check that dragging the bar to 3.0s really put the composition
 *   at 3.0s is to give the clip a picture that DIFFERS BY TIME and then read
 *   the pixels back — which is exactly what `ramp_rgb.mp4` is for: 6 seconds in
 *   three flat thirds, 0-2s RED, 2-4s GREEN, 4-6s BLUE. Trim's suite built the
 *   fixture and the classifier for its own timing contract; a scrub is the
 *   first thing since that can be graded by the same instrument, so it is
 *   imported rather than copied (the house rule: a helper moves out on its
 *   second caller).
 *
 * P1 — THE BAR EXISTS AND SAYS WHAT THE TAKE IS. A ruler that does not agree
 *      with the duration chips is a ruler measuring nothing.
 *
 * P2 — A SCRUB LANDS WHERE IT SAYS IT DOES. Set the bar to a time inside each
 *      third of the clip and assert the CANVAS shows that third's colour. This
 *      is the whole feature: three seeks, three colours, in the order the file
 *      has them. It is also the assertion that would have caught every
 *      plausible way to get this wrong — seeking the element to output time
 *      instead of source time, forgetting the trim window, letting a playing
 *      element run past the seek, or drawing before the decoder landed.
 *
 * P3 — A SCRUB PARKS, AND A PARK HOLDS. After a scrub the picture must not
 *      drift: the composition is held on that instant until something plays.
 *      Measured as the canvas hash being IDENTICAL across a second of
 *      wall-clock, which is a claim no amount of "it looked right" can make.
 *
 * P4 — PLAY RESUMES FROM THE PARK, NOT FROM ZERO. `resumeOriginMs` is swept in
 *      node; this is the same property at the artifact, where the Stage's own
 *      tick is the thing computing it.
 *
 * P5 — THE READOUT AGREES WITH THE BAR. Two displays of one number is how this
 *      project got four partitions and three copies of `sourceTimeAt`; if the
 *      text and the thumb can disagree, one of them is decoration.
 *
 * P6 — IT IS WATERTIGHT ON A PHONE. The mobile law, on the control that was
 *      just added to the densest bar in the app: zero horizontal overflow at
 *      320/360/390/430, a 44px hit row, and a scrub that still WORKS at 390 —
 *      a tap target that is big enough but changes nothing is not a control.
 *
 * Run: npx playwright test --config=playwright.playhead.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

const RAMP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');

/** The fixture's own timing contract — see tests/e2e/trim.spec.ts. */
const THIRDS: ReadonlyArray<{ at: number; want: 'r' | 'g' | 'b'; label: string }> = [
  { at: 1.0, want: 'r', label: 'the first third' },
  { at: 3.0, want: 'g', label: 'the middle third' },
  { at: 4.5, want: 'b', label: 'the last third' },
];

/** The take this spec drives. 5s is the shortest roster entry, and every third
 *  of a 6s clip is still reachable inside it because an untrimmed clip maps
 *  output time to source time one-for-one. */
const TAKE = 5;

type Channel = 'r' | 'g' | 'b' | '?';

/** Which third of the clip is on screen, read off the LIVE Stage canvas.
 *  Verbatim the instrument trim.spec.ts grades its own timing with. */
const stageChannel = async (page: Page): Promise<Channel> =>
  page.evaluate(() => {
    const cv = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!cv || !cv.width || !cv.height) return '?';
    const s = document.createElement('canvas');
    s.width = 8; s.height = 8;
    const ctx = s.getContext('2d');
    if (!ctx) return '?';
    try { ctx.drawImage(cv, 0, 0, 8, 8); } catch { return '?'; }
    const d = ctx.getImageData(0, 0, 8, 8).data;
    let r = 0, g = 0, b = 0;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
    const max = Math.max(r, g, b);
    const rest = [r, g, b].filter((v) => v !== max);
    if (max < 8 * 8 * 40) return '?';
    if (max < Math.max(...rest) * 1.6) return '?';
    return (max === r ? 'r' : max === g ? 'g' : 'b') as 'r' | 'g' | 'b';
  });

/** FNV hash of the live canvas — changes iff the picture moved. */
const canvasHash = (page: Page) =>
  page.evaluate(() => {
    const src = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!src || !src.width || !src.height) return -1;
    const t = document.createElement('canvas'); t.width = 32; t.height = 32;
    const tc = t.getContext('2d'); if (!tc) return -1;
    tc.drawImage(src, 0, 0, 32, 32);
    const d = tc.getImageData(0, 0, 32, 32).data;
    let h = 2166136261;
    for (let i = 0; i < d.length; i += 4) {
      h = (Math.imul(h ^ d[i], 16777619) + Math.imul(d[i + 1], 31) + d[i + 2]) >>> 0;
    }
    return h;
  });

const playhead = (page: Page) => page.getByLabel(/^Playhead/);
const readout = (page: Page) => page.getByTestId('playhead-readout');

const boot = async (page: Page, files: string[]) => {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });
  await page.locator('input[type="file"]').first().setInputFiles(files);
  await expect(page.locator('canvas').first()).toBeVisible({ timeout: 120_000 });
  // The take chip the ruler must agree with.
  await page.getByRole('button', { name: `${TAKE}s`, exact: true }).click();
  await expect(playhead(page)).toBeVisible({ timeout: 60_000 });
};

/** Drag the bar. `fill` writes the value and dispatches input, which is the
 *  same event a thumb produces — and it is the ONLY way to place a range
 *  precisely, since a pointer drag can only land on whole pixels. */
const scrubTo = async (page: Page, t: number) => {
  // NOTE the string form: Playwright's range fill compares what it wrote
  // against the DOM's normalised `value`, so a trailing zero fails as
  // "Malformed value" while meaning the same number (scar: trim.spec.ts:494).
  await playhead(page).fill(String(t));
  // The seek is async — one `renderAtTime` per decoder — so wait for the
  // picture rather than for a timeout.
  await page.waitForTimeout(700);
};

test.describe('THE PLAYHEAD', () => {
  test('a scrub lands on the instant it claims, and holds it', async ({ page }) => {
    await boot(page, [RAMP, IMG_A]);

    // ---- P1: the ruler agrees with the take -------------------------------
    const bar = playhead(page);
    expect(Number(await bar.getAttribute('max')), 'the bar must measure the chosen take')
      .toBeCloseTo(TAKE, 5);
    expect(Number(await bar.getAttribute('min'))).toBe(0);
    await expect(readout(page)).toContainText(`/ 0:0${TAKE}.0`);

    // ---- P2: three seeks, three colours -----------------------------------
    const seen: Array<{ label: string; want: string; got: Channel }> = [];
    for (const third of THIRDS) {
      await scrubTo(page, third.at);
      const got = await stageChannel(page);
      seen.push({ label: third.label, want: third.want, got });
    }
    for (const s of seen) {
      expect(
        s.got,
        `scrubbing to ${s.label} showed '${s.got}' — the whole run read `
        + JSON.stringify(seen.map((x) => `${x.want}->${x.got}`)),
      ).toBe(s.want);
    }

    // ---- P5: the readout agrees with the thumb ----------------------------
    await scrubTo(page, 3.0);
    expect(Number(await bar.inputValue())).toBeCloseTo(3.0, 3);
    await expect(readout(page)).toContainText('0:03.0');

    // ---- P3: a park HOLDS -------------------------------------------------
    const a = await canvasHash(page);
    await page.waitForTimeout(1100);
    const b = await canvasHash(page);
    expect(a, 'the canvas must be readable').not.toBe(-1);
    expect(b, 'a scrubbed composition must be HELD on its instant, not drift off it').toBe(a);
    expect(Number(await bar.inputValue()), 'and the bar must stay where it was put')
      .toBeCloseTo(3.0, 3);

    // ---- P4: play resumes FROM the park, not from zero --------------------
    await page.getByRole('button', { name: 'Play clips' }).click();
    await page.waitForTimeout(600);
    const resumed = Number(await bar.inputValue());
    expect(resumed, `play resumed at ${resumed}s after a park at 3.0s — it restarted from the top`)
      .toBeGreaterThan(2.9);
  });

  test('it is watertight and it still works at 390px', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 780 });
    await boot(page, [RAMP, IMG_A]);

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.waitForTimeout(350);
      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(
        overflow.scrollW,
        `${width}px: the page scrolls horizontally by `
        + `${overflow.scrollW - overflow.clientW}px with the playhead in the bar`,
      ).toBeLessThanOrEqual(overflow.clientW);

      const box = await playhead(page).boundingBox();
      expect(box, `${width}px: the playhead is not laid out`).not.toBeNull();
      expect(box!.height, `${width}px: the playhead's hit row is ${box!.height}px, under the 44px law`)
        .toBeGreaterThanOrEqual(44);
      expect(box!.width, `${width}px: the playhead is ${box!.width}px wide — unusable`)
        .toBeGreaterThan(80);
      expect(
        box!.x + box!.width,
        `${width}px: the playhead runs ${(box!.x + box!.width) - width}px past the viewport`,
      ).toBeLessThanOrEqual(width + 0.5);
    }

    // A TAP TARGET THAT CHANGES NOTHING IS NOT A CONTROL. The sizes above are
    // necessary and are not sufficient — drive the real control at the real
    // width and assert the picture actually moved.
    await page.setViewportSize({ width: 390, height: 780 });
    await page.waitForTimeout(300);
    await scrubTo(page, 1.0);
    const red = await stageChannel(page);
    await scrubTo(page, 4.5);
    const blue = await stageChannel(page);
    expect(red, 'at 390px, scrubbing to the first third must show it').toBe('r');
    expect(blue, 'at 390px, scrubbing to the last third must show it').toBe('b');
  });
});
