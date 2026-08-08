/**
 * THE SOUNDTRACK AT THE ARTIFACT — proved by DECODING THE EXPORTED FILE.
 *
 * THE MOVE gave a collage of photographs a time axis, so a photo collage can be
 * exported as a video. That video was necessarily SILENT: every sample this app
 * had ever mixed came out of a video clip's own audio track, and a collage made
 * of photographs has no clips. This suite is the proof that it no longer is.
 *
 * WHY THE PROOF HAS TO BE SAMPLES. The whole history of the audio path in this
 * repo is of cheaper signals being true while the file was quiet: a status pill,
 * `progress.withAudio`, the absence of a warning, a muxed-chunk count — each was
 * green throughout the cycle where every export shipped silent because
 * `describeAudioSources` read the SPEAKERS instead of the user's intent. So the
 * measurement is a Goertzel filter over the decoded MP4 (`./tone-measure`), and
 * the fixture is a PURE TONE at 1500 Hz — not a harmonic of any tone already in
 * this fixture set, and measured against a 5000 Hz control so "the file is loud"
 * can never masquerade as "the file contains the music".
 *
 *   T1  MUSIC LANDS IN A PHOTO COLLAGE'S EXPORT, WITH NO OTHER INTERACTION —
 *       and it LAPS. Two photographs, one music file, press record. Nothing is
 *       unmuted, the speaker is never pressed. That path is the whole feature,
 *       and it is also the exact shape of the owner's report that exposed the
 *       intent-vs-audible bug ("I know for sure there's audio"), so it is the
 *       one that must work untouched. The measurement window is the MIDDLE of
 *       the take, which is past the end of a 2.0 s track — silence there means
 *       the mixer played the file once and stopped instead of lapping it.
 *
 *   T2  MUTING THE MUSIC REALLY REMOVES IT. The other half of intent: a chip
 *       that changes nothing in the file is an inert control, which is the class
 *       of defect this project has already been filed against four times.
 *
 *   T3  IT IS WATERTIGHT ON A PHONE. A new chip in the dock's scroll row and a
 *       new button in the top-right column, at 320/360/390/430 px.
 *
 * Run against the running collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.soundtrack.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.soundtrack.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { measureTones, HZ_CONTROL } from './tone-measure';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** Two real photographs — the pixels are irrelevant here; the point is that
 *  NEITHER is a video, so the only sound this app could possibly emit is the
 *  music. Before this feature that meant: no sound at all, ever. */
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

/** 2.0 s of a pure 1500 Hz sine, AAC in an .m4a — audio only, no video track.
 *  SHORTER THAN THE TAKE ON PURPOSE: the take is 5 s, so a file that carries
 *  the tone at its midpoint carries it on a LAP. */
const MUSIC = join(HERE, '..', 'fixtures', 'music_1500.m4a');
const HZ_MUSIC = 1500;
const TRACK_SEC = 2.0;

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');

async function bootWithPhotos(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  // The face model is a CDN script nothing here needs; blocking it keeps the run
  // off the network and out of a 30 s stall.
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });

  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
}

/** A 5 s take rather than the default 10: half the render, and still two and a
 *  half laps of a 2 s track. */
async function pickShortTake(page: Page) {
  const five = page.getByRole('button', { name: '5s', exact: true });
  if (await five.count()) await five.first().click();
}

/**
 * RECORD, AND PROVE AN ARTIFACT EXISTS BEFORE MEASURING IT.
 *
 * A measurement that finds no file returns "not ok", and a test that only
 * asserts a tone is ABSENT would then pass without a render ever having
 * happened — the vacuous green this repo has been bitten by (a preview-only e2e
 * cannot see an export defect). So this returns the result readout, which names
 * the frame count and whether the muxer wrote a sound track, and refuses to
 * proceed without a real `blob:` video on the page.
 */
async function renderTake(page: Page): Promise<string> {
  await pickShortTake(page);
  await page.getByRole('button', { name: 'Record video' }).click();
  const readout = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
  await expect(readout).toBeVisible({ timeout: 360_000 });
  const text = (await readout.first().innerText()).replace(/\s+/g, ' ');

  const src = await page.evaluate(() => {
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    return el?.src ?? '';
  });
  expect(src, 'the take must have produced a real file to measure').toContain('blob:');

  const frames = Number(/(\d+) frames/.exec(text)?.[1] ?? 0);
  expect(frames, `an offline render emits duration x fps frames — got "${text}"`).toBeGreaterThan(60);
  console.log(`[soundtrack] result: ${text}`);
  return text;
}

test.describe('THE SOUNDTRACK', () => {
  test('T1 — music lands in a photo collage’s export, untouched, and it laps', async ({ page }) => {
    test.setTimeout(420_000);
    await bootWithPhotos(page);

    // A photo collage has no live clips, so before this the dock did not exist
    // at all and the export sheet refused video. Adding music is what makes the
    // Stage mount — `liveMode` had to widen exactly as THE MOVE widened it.
    await musicInput(page).setInputFiles([MUSIC]);
    await expect(
      page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }),
      'the music chip must appear in the dock for a collage with no clips at all',
    ).toBeVisible({ timeout: 60_000 });

    // THE DEFAULT IS THE ASSERTION. A clip arrives muted (a collage that shouts
    // on import is not a nice thing to build); music does not, because adding it
    // is an explicit act whose entire purpose is the sound.
    // The chip's accessible name is its NEXT ACTION, and with the monitor still
    // off that action is "hear it" — the state to assert is `aria-pressed`,
    // which is the intent the FILE will carry.
    await expect(
      page.getByRole('button', { name: /Hear the music/ }),
      'music must arrive IN the piece — the export cannot honour a switch nobody found',
    ).toHaveAttribute('aria-pressed', 'true', { timeout: 30_000 });

    // The speaker is NEVER pressed. `soundOn` stays false for this whole test,
    // which is the condition that used to empty the mix.
    const readout = await renderTake(page);
    expect(
      readout,
      'the result readout must SAY the file has sound — the label that used to hard-code "silent" onto the branch that renders it',
    ).toContain('sound');

    const t = await measureTones(page, [HZ_MUSIC], HZ_CONTROL);
    console.log(`[soundtrack] decoded ${t.durationSec.toFixed(2)}s, rms=${t.rms.toFixed(4)}, ` +
      `1500Hz=${t.bins[0].toFixed(5)}, control=${t.control.toFixed(5)}, ratio=${(t.bins[0] / (t.control || 1e-9)).toFixed(1)}x`);
    expect(t.ok, `the export must carry an audio track — ${t.reason}`).toBe(true);
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);
    expect(
      t.bins[0],
      `1500 Hz (the music) must be present — music=${t.bins[0]} control=${t.control}`,
    ).toBeGreaterThan(t.control * 8);
    // The window `measureTones` reads is the middle of the decoded stream. A
    // take longer than the track can only sound there if the track LAPPED.
    expect(
      t.durationSec,
      `the take must outrun the ${TRACK_SEC}s track, or lapping is not under test — got ${t.durationSec}s`,
    ).toBeGreaterThan(TRACK_SEC * 1.5);
  });

  test('T2 — muting the music really removes it from the file', async ({ page }) => {
    test.setTimeout(420_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC]);

    // THREE STATES, NOT TWO, and the name always names the next action. Music
    // arrives in the piece with the monitor off, so the first press is "hear
    // it"; only the second press takes it OUT of the file.
    await page.getByRole('button', { name: /Hear the music/ }).click();
    await expect(
      page.getByRole('button', { name: /Mute the music/ }),
      'once the monitor is on, the chip must offer to mute',
    ).toBeVisible({ timeout: 15_000 });

    await page.getByRole('button', { name: /Mute the music/ }).click();
    await expect(
      page.getByRole('button', { name: /Put the music back in the piece/ }),
      'the chip must read back the state it was just put into',
    ).toBeVisible({ timeout: 15_000 });

    const readout = await renderTake(page);
    expect(
      readout,
      'with the only source muted the muxer writes no audio track, and the readout must say so',
    ).toContain('silent');

    const t = await measureTones(page, [HZ_MUSIC], HZ_CONTROL);
    console.log(`[soundtrack] muted: ok=${t.ok} 1500Hz=${t.ok ? t.bins[0] : 'n/a'} (${t.reason})`);
    // Either there is no audio track at all (the honest answer when nothing is
    // audible: the mixer writes no track rather than a silent one), or there is
    // one and the tone is down at the noise floor.
    if (t.ok) {
      expect(
        t.bins[0],
        `a muted track must not sound — music=${t.bins[0]} control=${t.control}`,
      ).toBeLessThan(t.control * 4);
    }
  });

  test('T3 — the music chip and button are watertight on a phone', async ({ page }) => {
    test.setTimeout(180_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC]);
    await expect(page.getByRole('button', { name: /Remove the music/ })).toBeVisible({ timeout: 60_000 });

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.waitForTimeout(500);

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(
        overflow.scrollWidth,
        `${width}px: the page must not scroll sideways (scrollWidth ${overflow.scrollWidth} > clientWidth ${overflow.clientWidth})`,
      ).toBeLessThanOrEqual(overflow.clientWidth);

      // NO RAIL BUTTON MAY BE CLIPPED — and this is the assertion the overflow
      // check above cannot make. The stage rail is ABSOLUTELY POSITIONED inside
      // an `overflow-hidden` band, so a button pushed past the bottom is simply
      // cut off and costs the document no scrollWidth at all. Adding the music
      // button made the column 68px taller than the threshold that decides
      // column-vs-row, and "Clear all" disappeared on every phone with the dock
      // open, with every existing gate green. So: walk each rail button's
      // clipping ancestors and require its box to be inside all of them.
      for (const name of ['Maximize the shot', 'Add more images or video', 'Add a video', 'Add music', 'Replace the music', 'Clear all']) {
        const btn = page.getByRole('button', { name, exact: true });
        if (!(await btn.count())) continue;
        const cut = await btn.first().evaluate((el) => {
          const r = el.getBoundingClientRect();
          let n = el.parentElement;
          while (n && n !== document.body) {
            const cs = getComputedStyle(n);
            if (cs.overflow !== 'visible' || cs.overflowY !== 'visible' || cs.overflowX !== 'visible') {
              const p = n.getBoundingClientRect();
              if (r.bottom > p.bottom + 0.5 || r.top < p.top - 0.5 || r.right > p.right + 0.5) return true;
            }
            n = n.parentElement;
          }
          return false;
        });
        expect(cut, `${width}px: "${name}" is clipped by an ancestor that hides its overflow`).toBe(false);
      }

      // The two controls this increment added, at the operator's 44px law. The
      // chip lives in a horizontally scrolling row, so its own box may sit off
      // the right edge — the law is about the TARGET, not about where it is.
      for (const name of [/Mute the music|Hear the music|Put the music back in the piece/, /Remove the music/, /Add music|Replace the music/]) {
        const btn = page.getByRole('button', { name }).first();
        if (!(await btn.count())) continue;
        const box = await btn.boundingBox();
        if (!box) continue;
        expect(box.width, `${width}px: ${name} is ${box.width}px wide`).toBeGreaterThanOrEqual(43.5);
        expect(box.height, `${width}px: ${name} is ${box.height}px tall`).toBeGreaterThanOrEqual(43.5);
      }
    }
  });
});
