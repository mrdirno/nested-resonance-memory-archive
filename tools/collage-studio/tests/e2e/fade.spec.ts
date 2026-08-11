/**
 * THE FADE AT THE ARTIFACT — proved by DECODING THE EXPORTED FILE AND READING
 * ITS ENVELOPE.
 *
 * THE SOUNDTRACK put music under the collage and THE MOVE gave a photo collage
 * a time axis to put it under. What came out began at full level on sample zero
 * and ENDED MID-BAR: `mixSources` renders exactly `ceil(seconds * 48000)`
 * samples and hands every one of them to the encoder, so the last sample of a
 * 5 s take is whatever the song happened to be doing at 5.000 s. This suite is
 * the proof that it no longer does.
 *
 * WHY THE MEASUREMENT NEEDS A TIME AXIS, AND WHY NOTHING CHEAPER WILL DO.
 * A fade is the one edit that changes NOTHING a measurement without a clock can
 * see. The tone is the same tone. The take is the same length. The status pill
 * still says "sound", the muxer still writes a track, `measureTones` still
 * reports 1500 Hz at three orders of magnitude over the control — because it
 * reads a window from the MIDDLE, which is exactly the part a fade leaves
 * alone. Every assertion in `soundtrack.spec.ts` passes on a file with no fade
 * in it. So this reads `toneEnvelope` (`./tone-measure`) — the same instrument
 * the lap schedule needed, moved out of `trim.spec.ts` on this, its second
 * caller — and asserts the SHAPE.
 *
 *   F1  THE TAKE FADES IN AND OUT, AND OVER THE RIGHT LENGTH. A 5 s take with
 *       a 2 s fade is a trapezoid: up over [0,2], flat over [2,3], down over
 *       [3,5]. The assertions are laid out in three layers, weakest first, and
 *       the last one is the one that carries the test:
 *         (a) the ends are quiet and the middle is not — kills "no fade at all";
 *         (b) the ramps are monotone — kills "the ends got muted" and a sign
 *             error, both of which pass (a);
 *         (c) the measured envelope matches the trapezoid POINT BY POINT.
 *       (c) is there because (a) and (b) are both invariant under the RAMP
 *       LENGTH: a 1 s fade, a 0.5 s fade and a fade that spends the whole take
 *       ramping all pass them. This is the same lesson `trim.spec.ts` wrote
 *       down when duty cycle and longest-silence both scored a one-second-late
 *       render as perfect — a statistic that says HOW MUCH never says WHERE.
 *       The expected numbers are written out by hand here rather than imported,
 *       so a defect inside `fade.fadeGainAt` cannot rubber-stamp itself; the
 *       shipped function is then cross-checked against those same hand numbers,
 *       so the two can never drift apart silently either.
 *
 *   F2  AND WITH THE FADE OFF, THE SAME TAKE IS FLAT — the before, measured
 *       rather than remembered. It also carries the second half of the design:
 *       the fade runs AFTER the true-peak limiter, so the PLATEAU of the faded
 *       take must sit at the same level as the un-faded take's. Fading first
 *       would let the ends set the limiter's scale and make the untouched
 *       middle of the export louder, which is the one way this feature could
 *       change a part of the file nobody asked it to touch.
 *
 *   F3  IT IS WATERTIGHT ON A PHONE. One new 44 px target in a bar that was
 *       already eleven controls wide, at 320/360/390/430 px.
 *
 * Run against the running collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.fade.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.fade.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { toneEnvelope } from './tone-measure';
import { fadeGainAt, fadeSpan } from '../../src/lib/fade';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

/** 2.0 s of a pure 1500 Hz sine, AAC in an .m4a — audio only, no video track.
 *  1500 x 2.0 = 3000 whole cycles, so the loop is phase-continuous and the tone
 *  under test is genuinely flat before a fade touches it. */
const MUSIC = join(HERE, '..', 'fixtures', 'music_1500.m4a');
const HZ_MUSIC = 1500;

const TAKE = 5;
const FADE = 2;
/** 20 slices across the take. Fine enough to see a 2 s ramp as a ramp rather
 *  than as two levels, coarse enough that each window holds ~375 cycles of the
 *  tone and the Goertzel reading is stable. */
const SLICE = 0.25;

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');

async function bootWithMusic(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });

  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await musicInput(page).setInputFiles([MUSIC]);
  await expect(
    page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }),
    'the music chip must appear before anything here means anything',
  ).toBeVisible({ timeout: 60_000 });
}

/** The fade chip's accessible name always opens with "Fade ", so one locator
 *  finds it in every one of its four states. */
const fadeChip = (page: Page) => page.getByRole('button', { name: /^Fade / });

/** Tap the chip until it reads the wanted length. Cycling is the control's
 *  whole shape (one 44 px target, four states), so the test drives it the way a
 *  thumb does rather than reaching past it into React state. */
async function setFade(page: Page, label: string) {
  const chip = fadeChip(page);
  await expect(chip, 'the fade chip must be offered once the take carries sound')
    .toBeVisible({ timeout: 30_000 });
  for (let i = 0; i < 6; i++) {
    if ((await chip.innerText()).trim() === label) return;
    await chip.click();
  }
  expect(await chip.innerText(), `the fade chip never reached ${label}`).toBe(label);
}

async function renderTake(page: Page): Promise<string> {
  const five = page.getByRole('button', { name: `${TAKE}s`, exact: true });
  if (await five.count()) await five.first().click();
  await page.getByRole('button', { name: 'Record video' }).click();
  const readout = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
  await expect(readout).toBeVisible({ timeout: 360_000 });
  const text = (await readout.first().innerText()).replace(/\s+/g, ' ');
  const src = await page.evaluate(() => {
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    return el?.src ?? '';
  });
  expect(src, 'the take must have produced a real file to measure').toContain('blob:');
  return text;
}

/** The measured envelope, normalised by its own loudest slice, so the claim
 *  survives any encoder level and any change to the limiter's ceiling. */
async function normalisedEnvelope(page: Page, tag: string) {
  const env = await toneEnvelope(page, HZ_MUSIC, SLICE);
  expect(env.ok, `${tag}: the export must carry a decodable audio track — ${env.reason}`).toBe(true);
  expect(env.slices.length, `${tag}: the envelope must have real slices`).toBeGreaterThan(15);
  expect(env.dur, `${tag}: the file must be about ${TAKE}s, got ${env.dur}`).toBeGreaterThan(TAKE * 0.85);
  const peak = Math.max(...env.slices.map((s) => s.e));
  expect(peak, `${tag}: the tone must be in the file at all`).toBeGreaterThan(0.005);
  const norm = env.slices.map((s) => ({ t: s.t + SLICE / 2, g: s.e / peak, e: s.e }));
  console.log(`[fade/${tag}] dur=${env.dur.toFixed(2)}s peak=${peak.toFixed(5)} envelope=`
    + norm.map((s) => Math.min(9, Math.round(s.g * 9))).join(''));
  return { peak, norm };
}

test.describe('THE FADE', () => {
  test('F1/F2 — the take fades in and out over the length it says, and off is flat',
    async ({ page }) => {
      test.setTimeout(600_000);
      await bootWithMusic(page);

      // ---- F2, THE CONTROL: the same take with no fade ---------------------
      // Measured first and on the same page, so "before" is a real file and not
      // a memory of one. The chip must START at OFF: every export made before
      // this feature existed has to remain reproducible today, and a roster
      // whose default did something would quietly retire all of them.
      await expect(fadeChip(page), 'the fade must arrive OFF').toHaveText('OFF', { timeout: 30_000 });
      const flatReadout = await renderTake(page);
      console.log(`[fade/off] result: ${flatReadout}`);
      expect(flatReadout, 'the control take must carry sound or it measures nothing')
        .toContain('sound');
      const flat = await normalisedEnvelope(page, 'off');

      // FLAT. Every slice of an un-faded take sits near the peak — this is the
      // "before" the whole increment is against, and it is also what makes the
      // fade assertions below meaningful rather than a reading of the fixture.
      const flatMin = Math.min(...flat.norm.map((s) => s.g));
      expect(flatMin,
        `with the fade OFF every slice must be near full level; the quietest is ${flatMin.toFixed(3)} `
        + 'of the peak, which means the file was already shaped before the fade existed')
        .toBeGreaterThan(0.7);

      await page.getByRole('button', { name: 'Close', exact: true }).first().click();

      // ---- F1: the same take, faded ---------------------------------------
      await setFade(page, `${FADE}s`);
      const fadedReadout = await renderTake(page);
      console.log(`[fade/on] result: ${fadedReadout}`);
      const faded = await normalisedEnvelope(page, 'on');

      // THE EXPECTED TRAPEZOID, WRITTEN OUT BY HAND. A 5 s take with a 2 s fade
      // is `min(t/2, (5-t)/2, 1)` — no import, so a defect inside the shipped
      // envelope cannot certify itself with its own arithmetic.
      const expected = (t: number) => Math.max(0, Math.min(t / FADE, (TAKE - t) / FADE, 1));

      // ...and the shipped function is held to those same hand numbers, so the
      // two cannot drift apart in silence later either.
      for (let t = 0; t <= TAKE; t += 0.05) {
        expect(fadeGainAt(t, TAKE, fadeSpan(FADE, TAKE)),
          `lib/fade disagrees with this test's own trapezoid at t=${t.toFixed(2)}`)
          .toBeCloseTo(expected(t), 9);
      }

      const inside = faded.norm.filter((s) => s.t < TAKE);

      // (a) THE ENDS ARE QUIET AND THE MIDDLE IS NOT.
      const head = inside[0];
      const tail = inside[inside.length - 1];
      const mid = inside.reduce((a, b) => (Math.abs(b.t - TAKE / 2) < Math.abs(a.t - TAKE / 2) ? b : a));
      expect(head.g, `the take still opens at ${(head.g * 100).toFixed(0)}% of full level`)
        .toBeLessThan(0.25);
      expect(tail.g, `the take still ends at ${(tail.g * 100).toFixed(0)}% of full level — this is `
        + 'the hard cut the whole increment exists to remove').toBeLessThan(0.25);
      expect(mid.g, 'the middle of the take must be at full level').toBeGreaterThan(0.9);

      // (b) THE RAMPS ARE MONOTONE. Sampled either side of the plateau with a
      // slack of one slice, because a slice that straddles a knee is genuinely
      // part-ramp and part-plateau.
      const rise = inside.filter((s) => s.t < FADE - SLICE);
      const fall = inside.filter((s) => s.t > TAKE - FADE + SLICE);
      for (let i = 1; i < rise.length; i++) {
        expect(rise[i].g, `the fade IN descends between ${rise[i - 1].t}s and ${rise[i].t}s`)
          .toBeGreaterThan(rise[i - 1].g - 0.05);
      }
      for (let i = 1; i < fall.length; i++) {
        expect(fall[i].g, `the fade OUT ascends between ${fall[i - 1].t}s and ${fall[i].t}s`)
          .toBeLessThan(fall[i - 1].g + 0.05);
      }

      // (c) THE SHAPE, POINT BY POINT — the assertion that pins the LENGTH.
      // AAC carries priming samples at the head, so the decoded stream is
      // shifted by a frame or two (~40 ms of a 2 s ramp); 0.12 absorbs that and
      // the encoder's own smoothing, and is far tighter than the 0.5 a
      // half-length ramp would need to pass.
      const worst = { t: -1, want: 0, got: 0, d: 0 };
      for (const s of inside) {
        const want = expected(s.t);
        const d = Math.abs(s.g - want);
        if (d > worst.d) { worst.t = s.t; worst.want = want; worst.got = s.g; worst.d = d; }
      }
      console.log(`[fade/on] worst slice: t=${worst.t.toFixed(2)}s want=${worst.want.toFixed(3)} `
        + `got=${worst.got.toFixed(3)} delta=${worst.d.toFixed(3)}`);
      expect(worst.d,
        `the exported envelope is not the ${FADE}s trapezoid it claims: at t=${worst.t.toFixed(2)}s `
        + `it should be at ${(worst.want * 100).toFixed(0)}% of full level and it is at `
        + `${(worst.got * 100).toFixed(0)}%. A shorter or longer ramp passes every other assertion `
        + 'in this test, which is why this one exists.')
        .toBeLessThan(0.12);

      // ---- F2, THE SECOND HALF: the fade runs AFTER the limiter ------------
      // The plateau of the faded take must sit at the same absolute level as
      // the un-faded take's. Fading BEFORE the limiter would let the ramps
      // lower the measured peak, the limiter would scale by less, and the
      // middle of the export — the part nobody asked this feature to touch —
      // would come back louder.
      const ratio = faded.peak / flat.peak;
      console.log(`[fade] plateau ratio faded/flat = ${ratio.toFixed(3)} `
        + `(${faded.peak.toFixed(5)} / ${flat.peak.toFixed(5)})`);
      expect(ratio,
        `switching the fade on moved the level of the UNFADED middle by ${((ratio - 1) * 100).toFixed(0)}% `
        + '— the envelope is being applied before the true-peak limiter instead of after it')
        .toBeGreaterThan(0.8);
      expect(ratio, 'same, in the other direction').toBeLessThan(1.25);
    });

  test('F3 — the fade chip is watertight on a phone', async ({ page }) => {
    test.setTimeout(180_000);
    await bootWithMusic(page);

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.waitForTimeout(500);

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollWidth,
        `${width}px: the page must not scroll sideways (scrollWidth ${overflow.scrollWidth} > `
        + `clientWidth ${overflow.clientWidth})`).toBeLessThanOrEqual(overflow.clientWidth);

      const chip = fadeChip(page).first();
      await expect(chip, `${width}px: the fade chip must be reachable`).toBeVisible({ timeout: 30_000 });
      const box = await chip.boundingBox();
      expect(box, `${width}px: the fade chip has no box`).not.toBeNull();
      expect(box!.height, `${width}px: the fade chip is ${box!.height}px tall`).toBeGreaterThanOrEqual(43.5);
      expect(box!.width, `${width}px: the fade chip is ${box!.width}px wide`).toBeGreaterThanOrEqual(43.5);

      // NOT CLIPPED BY AN ANCESTOR. The chip lives in a horizontally scrolling
      // row, so being off the right edge is legal and being cut off vertically
      // is not — the distinction the plain overflow check above cannot make,
      // and the one that hid "Clear all" on every phone when the music button
      // made the rail taller.
      const cutVertically = await chip.evaluate((el) => {
        const r = el.getBoundingClientRect();
        let n = el.parentElement;
        while (n && n !== document.body) {
          const cs = getComputedStyle(n);
          if (cs.overflowY !== 'visible') {
            const p = n.getBoundingClientRect();
            if (r.bottom > p.bottom + 0.5 || r.top < p.top - 0.5) return true;
          }
          n = n.parentElement;
        }
        return false;
      });
      expect(cutVertically, `${width}px: the fade chip is clipped by an ancestor`).toBe(false);

      // AND IT STILL WORKS AT THIS WIDTH — a target that is 44px and inert is
      // the defect this component has been filed against before.
      const before = (await chip.innerText()).trim();
      await chip.click();
      await expect(chip, `${width}px: tapping the fade chip changed nothing`)
        .not.toHaveText(before, { timeout: 5_000 });
    }
  });
});
