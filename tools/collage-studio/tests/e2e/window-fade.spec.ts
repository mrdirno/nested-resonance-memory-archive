/**
 * THE RANGE FADE AT THE ARTIFACT — proved by DECODING THE EXPORTED FILE AND
 * READING ITS ENVELOPE AT THE LAP JOINS.
 *
 * "Need to be able to add fade even when selecting clip range for audio", from
 * the field. THE FADE (`lib/fade.ts`) fades the SUMMED MIX at the take's two
 * ends and cannot reach a splice in the middle: a music range shorter than the
 * take LAPS, and every wrap was a hard cut with no control anywhere in the app.
 * This suite is the proof that it no longer is — and, just as importantly, that
 * the parts of the file the control was NOT asked to touch did not move.
 *
 * WHY THE MEASUREMENT IS AT THE JOINS AND NOWHERE ELSE.
 * Everything `soundtrack.spec.ts` and `fade.spec.ts` assert passes on a file with
 * no range fade in it: the tone is the same tone, the take is the same length,
 * the take's own ends are shaped by the take fade, and the middle of a lap is
 * exactly the part this envelope leaves alone. The only place the feature exists
 * is the instant the window comes round. So this reads `toneEnvelope` and asserts
 * the shape AT the boundaries the lap arithmetic predicts, against the same take
 * measured with the control OFF.
 *
 *   R1  THE JOINS DIP AND THE MIDDLES DO NOT. A 5 s take over a 1.2 s music
 *       range laps at 1.2 / 2.4 / 3.6 / 4.8 s. With the fade ON every one of
 *       those instants must be far below the level of the lap middles, and with
 *       it OFF none of them may be — the "before" measured as a real file rather
 *       than remembered. Three layers, weakest first:
 *         (a) the control take is flat at the joins — kills "the fixture was
 *             already shaped";
 *         (b) the faded take dips at the joins — kills "no fade at all";
 *         (c) the faded take's lap MIDDLES are still at full level — kills the
 *             version of this feature the judge panel rejected, where a fade on
 *             every lap becomes tremolo and the music ducks continuously.
 *       (c) is the assertion that fails if anyone ever widens the clamp: the
 *       quarter-of-a-lap bound (`windowFadeSpan`) is exactly what keeps half of
 *       every lap untouched, and no amount of dipping at the joins is worth a
 *       music bed that pumps.
 *
 *   R2  THE CLAMP IS VISIBLE, NOT SILENT. 0.5 s asked for on a 1.2 s range is
 *       0.3 s, and the readout has to say so — a roster whose entries silently
 *       collapse into one another is the inert-control defect this component has
 *       been filed against four times.
 *
 *   R4  A CLIP'S OWN SOUND GETS THE SAME ROW, AND ITS VALUE SURVIVES THE ROUND
 *       TRIP. The music's fade lives in App state; a CLIP's lives on the Stage and
 *       comes back through `status.clips[].fade` — which is exactly the path
 *       SCAR-C160 documents as swallowing the LAST field added to it, because the
 *       status signature is a hand-built string with the fields spelled out. A
 *       control the user can tap that reads back stale is the same defect wearing
 *       a new field name, so it is asserted rather than assumed.
 *
 *   R3  IT IS WATERTIGHT ON A PHONE. A fourth roster row in a sheet that had no
 *       height bound at all, at 320/360/390/430 px, with the Done button still
 *       reachable — the covered-button class this component is scarred by.
 *
 * Run against the running collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.window-fade.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.window-fade.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { toneEnvelope } from './tone-measure';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

/** 2.0 s of a pure 1500 Hz sine, AAC in an .m4a — audio only, no video track. */
const MUSIC = join(HERE, '..', 'fixtures', 'music_1500.m4a');
const MUSIC_NAME = 'music_1500.m4a';

/** A real video clip, for the half of this feature that is not the music. */
const CLIP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');
const CLIP_NAME = 'ramp_rgb.mp4';
const HZ_MUSIC = 1500;

const TAKE = 5;
/** The range. 1500 × 1.2 = 1800 WHOLE cycles, so the un-faded loop is
 *  phase-continuous and the control take is genuinely flat at its joins — a
 *  window that split a cycle would put a click there and measure as a dip in the
 *  file this suite is trying to prove is flat. */
const RANGE_OUT = 1.2;
/** What the row offers, and what the material allows: `windowFadeSpan` clamps to
 *  a QUARTER of the lap, so 0.5 asked for on 1.2 s of audio is 0.3 s. */
const ASKED = 0.5;
const EFFECTIVE = RANGE_OUT / 4;
/** Where the window comes round inside the take. */
const JOINS = [1.2, 2.4, 3.6, 4.8];

/** 0.06 s slices: narrow enough that a 0.3 s ramp either side of a join is not
 *  averaged away, wide enough to hold ~90 cycles of the tone so the Goertzel
 *  reading is stable. */
const SLICE = 0.06;

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
    page.getByRole('button', { name: new RegExp(`Remove the music, ${MUSIC_NAME.replace('.', '\\.')}`) }),
    'the music chip must appear before anything here means anything',
  ).toBeVisible({ timeout: 60_000 });
}

const sheet = (page: Page) => page.getByRole('dialog', { name: `Trim ${MUSIC_NAME}` });

/** Open the trim sheet the way a thumb does — through the chip, never by
 *  reaching past the UI into React state. */
async function openSheet(page: Page) {
  const trim = page.getByRole('button', { name: `Trim ${MUSIC_NAME}` });
  await expect(trim, 'the trim chip must be enabled once the length has probed')
    .toBeEnabled({ timeout: 60_000 });
  await trim.click();
  await expect(sheet(page)).toBeVisible({ timeout: 15_000 });
}

async function closeSheet(page: Page) {
  await sheet(page).getByRole('button', { name: 'Done' }).click();
  await expect(sheet(page)).toBeHidden({ timeout: 15_000 });
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
  expect(env.dur, `${tag}: the file must be about ${TAKE}s, got ${env.dur}`).toBeGreaterThan(TAKE * 0.85);
  const peak = Math.max(...env.slices.map((s) => s.e));
  expect(peak, `${tag}: the tone must be in the file at all`).toBeGreaterThan(0.005);
  const norm = env.slices.map((s) => ({ t: s.t + SLICE / 2, g: s.e / peak }));
  console.log(`[range-fade/${tag}] dur=${env.dur.toFixed(2)}s peak=${peak.toFixed(5)} envelope=`
    + norm.map((s) => Math.min(9, Math.round(s.g * 9))).join(''));
  /** The measured level nearest an output time. */
  const at = (t: number) => norm.reduce((best, s) =>
    (Math.abs(s.t - t) < Math.abs(best.t - t) ? s : best), norm[0]).g;
  return { peak, norm, at };
}

test.describe('THE RANGE FADE', () => {
  test('R1/R2 — the joins dip, the lap middles do not, and the clamp is said out loud',
    async ({ page }) => {
      test.setTimeout(600_000);
      await bootWithMusic(page);

      // ---- set the range, with the fade still OFF --------------------------
      await openSheet(page);
      await sheet(page).getByLabel(`Out point for ${MUSIC_NAME}`).fill(String(RANGE_OUT));
      const readout = sheet(page).getByTestId('window-fade-readout');
      await expect(readout, 'the row must arrive OFF and say so')
        .toHaveText(/full level/, { timeout: 10_000 });
      await closeSheet(page);

      // ---- THE CONTROL: the same take, no range fade -----------------------
      const flatText = await renderTake(page);
      console.log(`[range-fade/off] result: ${flatText}`);
      expect(flatText, 'the control take must carry sound or it measures nothing').toContain('sound');
      const flat = await normalisedEnvelope(page, 'off');

      // (a) FLAT AT THE JOINS. This is the "before": a hard splice, and the
      //     reason the assertion below means anything at all.
      for (const j of JOINS) {
        expect(flat.at(j),
          `with the range fade OFF the join at ${j}s reads ${flat.at(j).toFixed(3)} of peak — the `
          + 'fixture was already shaped, so this suite would prove nothing')
          .toBeGreaterThan(0.6);
      }

      await page.getByRole('button', { name: 'Close', exact: true }).first().click();

      // ---- THE SAME TAKE, FADED --------------------------------------------
      await openSheet(page);
      await sheet(page).getByTestId(`window-fade-${ASKED}`).click();

      // R2 — the clamp is visible. 0.5 asked for, 0.3 delivered, and the row
      // says both rather than pretending the roster entry was honoured.
      await expect(readout,
        'the readout must say what the material actually allows, not what was tapped')
        .toHaveText(new RegExp(`${ASKED.toFixed(1)}s → ${EFFECTIVE.toFixed(1)}s`), { timeout: 10_000 });
      await closeSheet(page);

      const fadedText = await renderTake(page);
      console.log(`[range-fade/on] result: ${fadedText}`);
      const faded = await normalisedEnvelope(page, 'on');

      // (b) THE JOINS DIP. Each one is the bottom of a 0.3 s ramp down into a
      //     0.3 s ramp back up, so the slice on the boundary must be a long way
      //     under the level the control take measured there.
      for (const j of JOINS) {
        const g = faded.at(j);
        console.log(`[range-fade] join ${j}s: off=${flat.at(j).toFixed(3)} on=${g.toFixed(3)}`);
        expect(g,
          `the join at ${j}s reads ${g.toFixed(3)} of peak with the fade ON — the window comes `
          + 'round there and the envelope is supposed to be closed')
          .toBeLessThan(0.45);
        expect(g,
          `the join at ${j}s did not move at all (off ${flat.at(j).toFixed(3)}, on ${g.toFixed(3)}) — `
          + 'the envelope reached the file at the wrong instant, or not at all')
          .toBeLessThan(flat.at(j) * 0.75);
      }

      // (c) AND THE MIDDLES ARE UNTOUCHED — the assertion that fails if the
      //     clamp is ever widened past a quarter of the lap. Half of every lap
      //     must still sit at full level, or the music bed pumps.
      for (const j of JOINS) {
        const mid = j - RANGE_OUT / 2;
        if (mid < 0.6 || mid > TAKE - 0.6) continue;   // inside the TAKE fade's own reach
        expect(faded.at(mid),
          `the middle of the lap at ${mid.toFixed(2)}s reads ${faded.at(mid).toFixed(3)} of peak — a `
          + 'range fade that ducks the middle of a lap is tremolo, not a fade')
          .toBeGreaterThan(0.7);
      }
    });

  test('R3 — the fade row is watertight on a phone', async ({ page }) => {
    test.setTimeout(240_000);
    await bootWithMusic(page);

    /* The four phone widths the law names, PLUS one landscape probe. Height is
       what a sheet runs out of, and a phone held sideways to drag a range handle
       is the ordinary way to reach 320px of it — at 430x932 a fourth roster row
       fits with room to spare, so a portrait-only sweep cannot see the defect it
       is here to prevent. */
    for (const [width, height] of [[320, 568], [360, 780], [390, 844], [430, 932], [568, 320]]) {
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(400);
      await openSheet(page);

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollWidth,
        `${width}px: the page must not scroll sideways (scrollWidth ${overflow.scrollWidth} > `
        + `clientWidth ${overflow.clientWidth})`).toBeLessThanOrEqual(overflow.clientWidth);

      for (const sec of [0, 0.1, 0.5, 1]) {
        const btn = sheet(page).getByTestId(`window-fade-${sec}`);
        await expect(btn, `${width}px: the ${sec}s fade button must be reachable`)
          .toBeVisible({ timeout: 15_000 });
        const box = await btn.boundingBox();
        expect(box, `${width}px: the ${sec}s button has no box`).not.toBeNull();
        expect(box!.height, `${width}px: the ${sec}s button is ${box!.height}px tall`)
          .toBeGreaterThanOrEqual(43.5);
      }

      // IT STILL DOES THE JOB AT THIS WIDTH — a 44px target that is inert is the
      // defect this component has been filed against before.
      await sheet(page).getByTestId('window-fade-1').click();
      await expect(sheet(page).getByTestId('window-fade-readout'),
        `${width}px: tapping a fade button changed nothing`)
        .toHaveText(/in and out|a quarter of the range/, { timeout: 5_000 });
      await sheet(page).getByTestId('window-fade-0').click();

      // AND THE SHEET DID NOT GROW PAST THE SCREEN. A fourth roster row on a
      // 568px-tall phone is exactly how a sheet outgrows its viewport — and the
      // half that goes missing is the TOP, not the bottom, because the panel is
      // pinned to the bottom edge (`items-end`) inside a `fixed inset-0` host
      // that the page cannot scroll. So BOTH ends are asserted after asking the
      // browser to reveal them: Close (the header) and Done (the footer). With no
      // height bound and no overflow the header sits at a NEGATIVE y and nothing
      // can bring it back, which is the covered-control class this component is
      // already scarred by.
      for (const [what, loc] of [
        ['Close trim', sheet(page).getByRole('button', { name: 'Close trim' })],
        ['Done', sheet(page).getByRole('button', { name: 'Done' })],
      ] as const) {
        await loc.scrollIntoViewIfNeeded();
        const b = await loc.boundingBox();
        expect(b, `${width}px: ${what} has no box`).not.toBeNull();
        expect(b!.height, `${width}px: ${what} is ${b!.height}px tall`).toBeGreaterThanOrEqual(43.5);
        expect(b!.y,
          `${width}x${height}: ${what} sits at y=${b!.y.toFixed(1)}, above the top of the screen — the sheet `
          + 'outgrew the viewport and cannot be scrolled back to it')
          .toBeGreaterThanOrEqual(-0.5);
        expect(b!.y + b!.height,
          `${width}x${height}: ${what} ends at ${(b!.y + b!.height).toFixed(1)}px, past the `
          + `${height}px viewport`)
          .toBeLessThanOrEqual(height + 0.5);
      }
      const done = sheet(page).getByRole('button', { name: 'Done' });
      await done.scrollIntoViewIfNeeded();
      await done.click();
      await expect(sheet(page)).toBeHidden({ timeout: 10_000 });
    }
  });

  test('R4 — a clip gets the same row, and the value survives the round trip', async ({ page }) => {
    test.setTimeout(240_000);
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.locator('input[type="file"]').first().setInputFiles([CLIP]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: `Stop playing ${CLIP_NAME}` }))
      .toBeVisible({ timeout: 200_000 });

    const trim = page.getByRole('button', { name: `Trim ${CLIP_NAME}` });
    await expect(trim, "a clip's trim chip must be enabled once its length has probed")
      .toBeEnabled({ timeout: 60_000 });
    await trim.click();
    const clipSheet = page.getByRole('dialog', { name: `Trim ${CLIP_NAME}` });
    await expect(clipSheet).toBeVisible({ timeout: 15_000 });

    const readout = clipSheet.getByTestId('window-fade-readout');
    await expect(readout, "a clip's sound gets the same row as the music's")
      .toHaveText(/full level/, { timeout: 10_000 });

    await clipSheet.getByTestId('window-fade-0.5').click();
    // THE ROUND TRIP. Stage -> emitStatus -> the signature -> React -> the row.
    // If `fade` is missing from the hand-built signature the Stage holds the new
    // value, the export renders it, and this readout never moves (SCAR-C160).
    await expect(readout, 'the clip fade did not come back out of the Stage — check the status signature')
      .toHaveText(/in and out|a quarter of the range/, { timeout: 10_000 });
    await expect(clipSheet.getByTestId('window-fade-0.5'), 'the tapped entry must read as pressed')
      .toHaveAttribute('aria-pressed', 'true');

    // And OFF comes back too, which a signature that only ever grows would hide.
    await clipSheet.getByTestId('window-fade-0').click();
    await expect(readout).toHaveText(/full level/, { timeout: 10_000 });
  });
});
