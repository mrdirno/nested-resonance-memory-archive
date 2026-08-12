/**
 * THE SPEED AT THE ARTIFACT — a clip's own clock, proved on PIXELS, with NO
 * wall-clock anywhere.
 *
 * The arithmetic is swept in tests/unit/speed.invariants.mjs (13 invariants:
 * the identity clause measured bitwise against the pre-feature build, the
 * stretch-mode invariant holding at every combination of speeds WITH a red
 * proof that the rejected "multiply afterwards" design breaks it by up to 61x,
 * and the exactness the power-of-two roster buys). Five things can only be
 * proved out here.
 *
 *   S1  THE SPEED REACHES THE PICTURE. A sweep can prove a multiplication;
 *       only a browser can prove the chip writes it into the scene, that the
 *       Stage composes it with video-length sync, and that the decoder is
 *       actually asked for a DIFFERENT FRAME because of it.
 *
 *   S2  IN BOTH DIRECTIONS. Faster is the easy half — anything that perturbs a
 *       seek looks like "faster" if you only ever measure "different". SLOWER
 *       is the half that catches a sign or reciprocal error, and it is measured
 *       as the wall still showing the FIRST third at an instant where 1x has
 *       moved on to the second.
 *
 *   S3  A SPEED IS A RE-PARAMETERISATION OF THE CLIP'S OWN TIME, which is the
 *       whole claim of lib/speed.ts stated as pixels: the frame at output 1.5s
 *       under 2x must be THE SAME FRAME as the frame at output 3.0s under 1x.
 *       Same canvas, two routes to it. (I7 asserts the seek target underneath
 *       is the same double; this asserts the picture that comes back is the
 *       same picture, which is a claim about the decoder, not about arithmetic.)
 *
 *   S4  THE PREVIEW SOUNDS LIKE THE FILE WILL. `preservesPitch` defaults TRUE
 *       on a media element, so a live <video> at 2x time-stretches while the
 *       offline mixer's AudioBufferSourceNode resamples and carries the pitch —
 *       the preview and the export disagreeing about what a rate SOUNDS like.
 *       Asserted on the real element, because that flag is the fix.
 *
 *   S5  IT IS WATERTIGHT ON A PHONE, with the sheet OPEN — five more 44px
 *       targets inside a modal that already carries a filmstrip and two range
 *       handles, at 320/360/390/430.
 *
 * WHY THE MEASUREMENT IS A SCRUB. `renderAtTime` is a pure function of the
 * instant — it is what the offline exporter walks the take with — so parking on
 * an instant asks the composition a question with exactly one right answer, and
 * a green run here is evidence about the exported FILE and not only about the
 * preview. `ramp_rgb.mp4` is 6 seconds in three flat thirds (0-2 RED, 2-4
 * GREEN, 4-6 BLUE), so "which frame is showing" is legible as a channel — the
 * instrument trim.spec.ts built and playhead.spec.ts already reuses.
 *
 * Run: npx playwright test --config=playwright.speed.config.ts
 * Against production:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config=playwright.speed.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const RAMP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');
const CLIP = 'ramp_rgb.mp4';

/** ONE SOURCE, for the reason playhead.spec.ts gives: `stageChannel` averages
 *  the WHOLE canvas, so a second picture in the average makes the classifier's
 *  margin depend on the dice. A colour proof needs a canvas that is only the
 *  thing being graded. */

/** The take. 5s is the shortest roster entry and every assertion below fits
 *  inside it — including 2x, which LAPS the 6s clip within it. */
const TAKE = 5;

type Channel = 'r' | 'g' | 'b' | '?';

/** Which third of the clip is on screen, read off the LIVE Stage canvas.
 *  Verbatim the instrument trim.spec.ts and playhead.spec.ts grade timing with. */
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

/** The artwork downsampled to N x N as raw RGBA — pace.spec.ts's instrument. */
const artBits = (page: Page, N = 120): Promise<number[] | null> =>
  page.evaluate((n) => {
    const canvases = Array.from(document.querySelectorAll('canvas')) as HTMLCanvasElement[];
    let el: HTMLCanvasElement | null = null;
    let best = 0;
    for (const c of canvases) {
      const a = c.width * c.height;
      if (a > best) { best = a; el = c; }
    }
    if (!el) return null;
    const c = document.createElement('canvas'); c.width = n; c.height = n;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(el, 0, 0, n, n);
    return Array.from(cx.getImageData(0, 0, n, n).data);
  }, N);

/** Share of samples differing by more than `tol`, and the worst difference. */
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

const playhead = (page: Page) => page.getByLabel(/^Playhead/);
const trimButton = (page: Page) => page.getByRole('button', { name: `Trim ${CLIP}` });

const boot = async (page: Page) => {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });
  await page.locator('input[type="file"]').first().setInputFiles([RAMP]);
  await expect(page.locator('canvas').first()).toBeVisible({ timeout: 120_000 });
  await page.getByRole('button', { name: `${TAKE}s`, exact: true }).click();
  await expect(playhead(page)).toBeVisible({ timeout: 60_000 });
};

/** Set the clip's speed through the real sheet, exactly as a thumb would. */
const setSpeed = async (page: Page, id: string) => {
  await trimButton(page).click();
  const chip = page.getByTestId(`speed-${id}`);
  await expect(chip).toBeVisible({ timeout: 15_000 });
  await chip.click();
  await expect(chip).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'Close trim' }).click();
  await expect(page.getByRole('dialog', { name: `Trim ${CLIP}` })).toHaveCount(0);
  // The scene is rebuilt on a speed change; let the decoders re-settle before
  // the first scrub asks them for a frame.
  await page.waitForTimeout(700);
};

const scrubTo = async (page: Page, t: number) => {
  // The STRING form matters: Playwright's range fill compares what it wrote
  // against the DOM's normalised value (scar: trim.spec.ts:494).
  await playhead(page).fill(String(t));
  await page.waitForTimeout(800);
};

/** Read the third showing at each instant, in order. */
const walk = async (page: Page, instants: number[]): Promise<Channel[]> => {
  const out: Channel[] = [];
  for (const t of instants) { await scrubTo(page, t); out.push(await stageChannel(page)); }
  return out;
};

test.describe('THE SPEED', () => {
  test('a clip runs at the speed it was given, both ways, and the frames prove it', async ({ page }) => {
    await boot(page);

    // ---- S1a: the control. 1x maps output time to source time one for one ---
    const natural = await walk(page, [1.0, 3.0, 4.5]);
    expect(natural.join(''), `1x must read the three thirds in order, got ${natural.join('')}`)
      .toBe('rgb');

    // ---- S1b: 2x reads the clip twice as fast, and LAPS it inside the take --
    await setSpeed(page, 'double');
    // EVERY INSTANT IS ON THE 0.1s GRID — `PLAYHEAD_STEP_SEC` is the bar's step
    // and a range `fill` off the grid is rejected as "Malformed value", which
    // reads like a broken selector rather than an off-grid number.
    const fast = await walk(page, [0.5, 1.5, 2.3, 3.5]);
    // 0.5 -> src 1.0 (r), 1.5 -> 3.0 (g), 2.3 -> 4.6 (b), 3.5 -> 7.0 % 6 = 1.0 (r).
    // That last one is the lap: at 1x a 6s clip cannot reach its end in a 5s
    // take at all, so a repeat is only possible because the clip is sped.
    expect(fast.join(''), `2x must read r,g,b then LAP back to r — got ${fast.join('')}`)
      .toBe('rgbr');
    // The badge on the dock chip must say so without opening anything.
    await expect(page.getByText('2×', { exact: true }).first()).toBeVisible();

    // ---- S3: the same frame by two routes ----------------------------------
    // 2x at 1.5s and 1x at 3.0s are both source time 3.0. If a speed were
    // anything other than a re-parameterisation of the clip's own clock, these
    // two canvases would differ.
    await scrubTo(page, 1.5);
    const twoXat1p5 = await artBits(page);
    await setSpeed(page, 'natural');
    await scrubTo(page, 3.0);
    const oneXat3 = await artBits(page);
    expect(twoXat1p5 && oneXat3, 'both canvases must be readable').toBeTruthy();
    const same = diff(twoXat1p5!, oneXat3!);
    console.log(`[speed] 2x@1.5s vs 1x@3.0s: ${(same.moved * 100).toFixed(1)}% of the frame differs,`
      + ` worst channel ${same.worst}/255`);
    expect(same.moved,
      `2x at 1.5s and 1x at 3.0s are the same source instant and must be the same picture`
      + ` — ${(same.moved * 100).toFixed(1)}% differed, worst ${same.worst}/255`)
      .toBeLessThan(0.02);

    // ...and the control that keeps it from being vacuous: a DIFFERENT source
    // instant on the same clip must differ a lot on this fixture.
    await scrubTo(page, 1.0);
    const oneXat1 = await artBits(page);
    const other = diff(oneXat1!, oneXat3!);
    console.log(`[speed] 1x@1.0s vs 1x@3.0s (different thirds):`
      + ` ${(other.moved * 100).toFixed(1)}% differs, worst ${other.worst}/255`);
    expect(other.moved, 'two different thirds must not measure as the same picture')
      .toBeGreaterThan(0.60);

    // ---- S2: slower is the other direction ---------------------------------
    await setSpeed(page, 'half');
    const slow = await walk(page, [3.0, 4.5]);
    // 3.0 -> src 1.5 (r) where 1x reads GREEN; 4.5 -> src 2.25 (g) where 1x
    // reads BLUE. Both instants disagree with the control run above, which is
    // what a reciprocal or sign error cannot fake.
    expect(slow.join(''), `0.5x must still be on the first third at 3.0s and the second at 4.5s`
      + ` — got ${slow.join('')} where 1x read ${natural.slice(1).join('')}`)
      .toBe('rg');

    // ---- S4: the live element pitches with the rate, like the mixer does ----
    const pitch = await page.evaluate(() => {
      const v = document.querySelector('video') as (HTMLVideoElement & { webkitPreservesPitch?: boolean }) | null;
      return v ? { rate: v.playbackRate, preserves: v.preservesPitch, webkit: v.webkitPreservesPitch } : null;
    });
    console.log(`[speed] live element: rate=${pitch?.rate} preservesPitch=${pitch?.preserves}`);
    expect(pitch, 'the clip must still have a live element').toBeTruthy();
    expect(pitch!.rate, 'the element must carry the composed rate').toBeCloseTo(0.5, 3);
    expect(pitch!.preserves,
      'preservesPitch must be false so the preview sounds like the exported file — the offline'
      + ' AudioBufferSourceNode always carries pitch with rate and cannot be told not to')
      .toBe(false);
  });

  test('the sheet is watertight on a phone, with the speed row in it', async ({ page }) => {
    await boot(page);
    await trimButton(page).click();
    await expect(page.getByTestId('speed-natural')).toBeVisible({ timeout: 15_000 });

    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(250);

      const overflow = await page.evaluate(() => ({
        scroll: document.documentElement.scrollWidth,
        client: document.documentElement.clientWidth,
      }));
      expect(overflow.scroll,
        `${w}px: the page must not scroll sideways with the clip sheet open`
        + ` (${overflow.scroll} > ${overflow.client})`)
        .toBeLessThanOrEqual(overflow.client);

      for (const id of ['quarter', 'half', 'natural', 'double', 'quad']) {
        const box = await page.getByTestId(`speed-${id}`).boundingBox();
        expect(box, `${w}px: speed chip ${id} must be laid out`).toBeTruthy();
        expect(box!.height, `${w}px: speed chip ${id} is ${box!.height}px tall`).toBeGreaterThanOrEqual(44);
        expect(box!.width, `${w}px: speed chip ${id} is ${box!.width}px wide`).toBeGreaterThanOrEqual(44);
      }

      // The two things the sheet must never lose to a new row: the readout that
      // says what the speed DOES, and the button that closes it.
      await expect(page.getByTestId('speed-readout')).toBeVisible();
      const done = await page.getByRole('button', { name: 'Done' }).boundingBox();
      expect(done, `${w}px: Done must be laid out`).toBeTruthy();
      expect(done!.y + done!.height, `${w}px: Done must be on screen without a pinch`)
        .toBeLessThanOrEqual(780);
    }

    // And the row still WORKS at the tightest width — a target big enough that
    // changes nothing is not a control.
    await page.setViewportSize({ width: 320, height: 780 });
    await page.getByTestId('speed-double').click();
    await expect(page.getByTestId('speed-double')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('speed-readout')).toContainText('on screen');
  });
});
