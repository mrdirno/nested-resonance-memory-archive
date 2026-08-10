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
 *   T4  THE TAKE GIVES THE MUSIC BACK. The offline render pauses every source
 *       and replays only the CLIPS, so the first export left the live music
 *       stopped for good — with no control that revives it. Found by an
 *       adversarial audit, not by any gate that existed.
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

/**
 * 6.0 s in three 2.0 s thirds — 900 Hz, then 1500 Hz, then 2300 Hz, AAC in an
 * .m4a with no video track. The point is that WHICH PART of a song came out is a
 * different measurement from WHETHER a song came out: a single-tone fixture
 * measures identically whether the range was honoured or ignored. None of the
 * three is a harmonic of another, nor of the 5000 Hz control (whose own
 * neighbours, 4500 and 4600, are comfortably clear of it).
 */
const MUSIC_THIRDS = join(HERE, '..', 'fixtures', 'music_thirds.m4a');
const HZ_LOW = 900;
const HZ_MID = 1500;
const HZ_HIGH = 2300;

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

  test('T4 — the music is still playing after a take', async ({ page }) => {
    test.setTimeout(420_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC]);

    // Monitor ON, so the music is genuinely audible before the render — this is
    // the state a person is in when they press Record, and the state in which
    // losing it is unmistakable.
    await page.getByRole('button', { name: /Hear the music/ }).click();
    await expect(page.getByRole('button', { name: /Mute the music/ })).toBeVisible({ timeout: 15_000 });

    const rolling = () => page.evaluate(() => {
      const el = document.querySelector('audio') as HTMLAudioElement | null;
      return el ? { present: true, paused: el.paused, muted: el.muted, t: el.currentTime } : { present: false, paused: true, muted: true, t: 0 };
    });
    const before = await rolling();
    expect(before.present, 'the Stage must hold an <audio> element for the music').toBe(true);
    expect(before.paused, 'the music must be rolling before the take').toBe(false);

    await renderTake(page);

    // THE OFFLINE RENDER PAUSES EVERYTHING AND REPLAYS ONLY THE CLIPS.
    // `beginOfflineRender` calls `pauseAll`, and `endOfflineRender` walked
    // `offlineWantPlay` — a list only clips are ever put on — so the first
    // export left the live soundtrack stopped for good. Nothing in the UI
    // revives it: the chip toggles INTENT, and the intent never changed. Every
    // other gate was green while the preview was silent from the first take on.
    const after = await rolling();
    console.log(`[soundtrack] audio after take: paused=${after.paused} muted=${after.muted} t=${after.t.toFixed(2)}`);
    expect(after.present, 'the element must survive the render').toBe(true);
    expect(after.paused, 'the music must still be playing AFTER the take').toBe(false);
  });

  test('T5 — music picked before any photograph waits, and says so', async ({ page }) => {
    test.setTimeout(120_000);
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);

    // No photographs at all — the drop target is live at zero images and now
    // advertises music, so this is a reachable path rather than a contrivance.
    await musicInput(page).setInputFiles([MUSIC]);
    await page.waitForTimeout(800);

    // THE NOTICE MUST NOT NAME A CONTROL THAT IS NOT ON SCREEN. With no stage
    // there is no dock, no chip and no speaker.
    const notice = await page.locator('div.fixed.bottom-24').first().innerText().catch(() => '');
    expect(notice, `the notice must not send anyone hunting for a speaker — got "${notice}"`)
      .not.toMatch(/press the speaker/i);
    expect(notice).toMatch(/add photos/i);

    // AND NO EMPTY CHROME. The dock's portal bar used to render 13px of nothing
    // whenever a source existed but the Stage did not.
    const emptyBars = await page.evaluate(() =>
      Array.from(document.querySelectorAll('div.border-b.border-white\\/5'))
        .filter((el) => el.textContent?.trim() === '' && el.querySelectorAll('button').length === 0)
        .filter((el) => el.getBoundingClientRect().height > 0).length);
    expect(emptyBars, 'no empty dock bar may be rendered with nothing to put in it').toBe(0);

    // And it is genuinely WAITING: add photographs and the music turns up.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
    await expect(
      page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }),
      'the music that was waiting must appear the moment there is a collage to put it under',
    ).toBeVisible({ timeout: 120_000 });
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

  /**
   * T6 — THE RANGE, PROVED BY DECODING THE EXPORTED FILE.
   *
   * From the field: "the audio import is cool — need a way to click it and
   * select the range". Until this, the only cut of a song this app could play
   * was the first N seconds of it.
   *
   * WHY THE FIXTURE IS THREE TONES. A range is the one edit that changes WHICH
   * PART of a file comes out while leaving every cheap signal identical: the
   * readout still says "sound", the chip still says the track's name, the mix
   * still has an audio track, and `music_1500.m4a` would measure exactly the
   * same at 1500 Hz whether the window was honoured or ignored. So the track is
   * 6 s in three 2 s thirds — 900 / 1500 / 2300 Hz, none of them a harmonic of
   * another or of the 5000 Hz control — and the window is the MIDDLE third.
   * Then "the range reached the file" and "the range was dropped" are two
   * different measurements and not two readings of one.
   *
   * AND THE TAKE OUTRUNS THE WINDOW ON PURPOSE. 5 s of output over a 2 s window
   * is two and a half laps, so this also asserts that a TRIMMED soundtrack still
   * laps over its window — the branch `lib/soundtrack.ts` DECISION 1b is about,
   * where handing the container duration over as the span would instead lap at
   * the file's length with a sliver of silence cut into every repeat.
   */
  test('T6 — the music plays the range you picked, and laps inside it', async ({ page }) => {
    test.setTimeout(420_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC_THIRDS]);
    await expect(
      page.getByRole('button', { name: /Remove the music, music_thirds\.m4a/ }),
    ).toBeVisible({ timeout: 60_000 });

    // THE LENGTH HAS TO LAND FIRST. It is probed asynchronously, and the range
    // button is deliberately disabled until it does — two handles on a
    // zero-width axis is a control that looks broken rather than pending.
    const trimBtn = page.getByRole('button', { name: 'Trim music_thirds.m4a' });
    await expect(trimBtn).toBeEnabled({ timeout: 30_000 });
    await expect(
      trimBtn, 'an untrimmed track wears no range badge',
    ).not.toContainText('→');

    await trimBtn.click();
    const sheet = page.getByRole('dialog', { name: 'Trim music_thirds.m4a' });
    await expect(sheet).toBeVisible({ timeout: 15_000 });

    // MOBILE-WATERTIGHT, ON THE SHEET ITSELF — a new full-screen surface on a
    // phone, checked where it is actually used rather than assumed from the
    // clip sheet it shares code with.
    await page.setViewportSize({ width: 390, height: 780 });
    await page.waitForTimeout(300);
    const sheetOverflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(
      sheetOverflow.scrollWidth,
      '390px with the range sheet open: the page must not scroll sideways',
    ).toBeLessThanOrEqual(sheetOverflow.clientWidth);
    for (const label of ['In point for music_thirds.m4a', 'Out point for music_thirds.m4a']) {
      const box = await sheet.getByLabel(label).boundingBox();
      expect(box?.height ?? 0, `${label} must be a 44px target`).toBeGreaterThanOrEqual(43.5);
    }

    // OUT first, then IN — pulling IN past the current OUT is repaired by the
    // window's own floor, and setting the far edge first keeps every
    // intermediate state legal instead of leaning on that repair.
    await sheet.getByLabel('Out point for music_thirds.m4a').fill('4');
    await sheet.getByLabel('In point for music_thirds.m4a').fill('2');
    await expect(sheet.getByTestId('trim-readout')).toContainText('2.0s→4.0s');
    await sheet.getByRole('button', { name: 'Close trim' }).click();
    await expect(sheet).toBeHidden({ timeout: 10_000 });

    // THE CHIP MUST SAY SO. A window is the one edit that changes what the
    // export contains while leaving the collage looking identical, so it has to
    // be legible without opening anything.
    await expect(
      page.getByTestId('track-range'),
      'a trimmed track wears its range on the chip',
    ).toHaveText('0:02→0:04', { timeout: 15_000 });

    await page.setViewportSize({ width: 1280, height: 900 });

    /**
     * THE LIVE TIMELINE HOLDS THE RANGE TOO — asserted here because "the preview
     * and the export derived the same thing independently and agreed right up
     * until one of them changed" is the shape this project keeps getting burned
     * by, and a range you can see in the file but not HEAR in the monitor is
     * exactly that bug wearing a different hat.
     *
     * `<audio>` has no in/out points, so the window is held by watching
     * `currentTime` — from the frame loop where one is running, and from the
     * element's own `timeupdate` where none is (a still collage with music and
     * no clips draws nothing at all). The tolerance is that event's ~250 ms plus
     * a frame: the claim under test is "it stays inside the part you picked",
     * not "it is sample-accurate", which is the offline mixer's job and is what
     * the tone measurement below actually proves.
     */
    const walk = await page.evaluate(async () => {
      const el = document.querySelector('audio') as HTMLAudioElement | null;
      if (!el) return { found: false, samples: [] as number[], advanced: false };
      const samples: number[] = [];
      for (let i = 0; i < 30; i++) {
        samples.push(el.currentTime);
        await new Promise((r) => setTimeout(r, 100));
      }
      return { found: true, samples, advanced: new Set(samples.map((s) => s.toFixed(2))).size > 3 };
    });
    expect(walk.found, 'the Stage must hold a live <audio> element for the music').toBe(true);
    expect(
      walk.advanced,
      `the monitor must actually be rolling, or "it stayed in range" is vacuous — ${walk.samples.join(',')}`,
    ).toBe(true);
    const stray = walk.samples.filter((s) => s < 2 - 0.4 || s > 4 + 0.4);
    expect(
      stray,
      `the live monitor must stay inside the 2→4 range it was given — strayed to ${stray.join(',')} ` +
      `(all: ${walk.samples.map((s) => s.toFixed(2)).join(',')})`,
    ).toEqual([]);

    const readout = await renderTake(page);
    expect(readout, 'a trimmed track is still sound').toContain('sound');

    const t = await measureTones(page, [HZ_LOW, HZ_MID, HZ_HIGH], HZ_CONTROL);
    console.log(`[soundtrack] range: ${t.durationSec.toFixed(2)}s rms=${t.rms.toFixed(4)} ` +
      `900=${t.bins[0].toFixed(5)} 1500=${t.bins[1].toFixed(5)} 2300=${t.bins[2].toFixed(5)} ` +
      `control=${t.control.toFixed(5)}`);
    expect(t.ok, `the export must carry an audio track — ${t.reason}`).toBe(true);
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);

    // THE PART YOU PICKED IS THERE...
    expect(
      t.bins[1],
      `1500 Hz (the middle third, which is what was selected) must be present — ` +
      `mid=${t.bins[1]} control=${t.control}`,
    ).toBeGreaterThan(t.control * 8);

    // ...AND THE PARTS YOU CUT ARE NOT. This is the whole assertion: without the
    // window the file starts at 0:00 and 900 Hz would be the loudest thing in it.
    expect(
      t.bins[0],
      `900 Hz (the first third, cut away) must not be in the file — low=${t.bins[0]} mid=${t.bins[1]}`,
    ).toBeLessThan(t.bins[1] / 8);
    expect(
      t.bins[2],
      `2300 Hz (the last third, cut away) must not be in the file — high=${t.bins[2]} mid=${t.bins[1]}`,
    ).toBeLessThan(t.bins[1] / 8);

    // AND IT LAPPED INSIDE THE WINDOW. `measureTones` reads the MIDDLE of the
    // decoded stream, which for a 5 s take is past the end of a 2 s window — the
    // tone can only be there if the window repeated.
    expect(
      t.durationSec,
      `the take must outrun the 2 s window, or lapping inside a range is not under test`,
    ).toBeGreaterThan(3);
  });
});
