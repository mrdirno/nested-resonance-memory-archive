/**
 * THE LEVEL AT THE ARTIFACT — proved by DECODING TWO EXPORTED FILES AND
 * DIVIDING ONE TONE BY ANOTHER.
 *
 * Every gain in this app used to be a boolean wearing a number's clothes, so
 * "how loud is the music under the clips" had exactly two answers: ALL and
 * NOTHING. This suite is the proof that it now has five, and that the number the
 * chip says is the number the FILE gets.
 *
 * WHY THE MEASUREMENT IS A RATIO WITHIN ONE FILE, and this is the whole design
 * of the suite rather than a convenience:
 *
 *   `offlineAudio.mixSources` ends by scaling the entire mix to a -3 dBFS
 *   ceiling. So the ABSOLUTE energy of the music in an export is not a function
 *   of the music's level alone — turn the music down and the summed peak falls,
 *   the limiter scales less, and everything comes back up. A test that asserted
 *   "the 1500 Hz bin got smaller" would be asserting the limiter's behaviour and
 *   would fail for a correct implementation.
 *
 *   The limiter multiplies EVERY sample by one scalar, so it cancels exactly out
 *   of the ratio between two tones in the same file. That ratio — music energy
 *   over clip energy — IS the level, and it is the only quantity here that is.
 *   Two sources, two frequencies, one file, one division.
 *
 * THE FIXTURES ARE PURE TONES because a Goertzel bin is a single-frequency
 * question: `tone_a.mp4` is 440 Hz of picture-plus-sound and `music_1500.m4a` is
 * 1500 Hz of sound alone. Neither is a harmonic of the other, nor of the 5000 Hz
 * control, so "the file is loud" can never masquerade as "the music is loud".
 *
 *   L1  THE HEADLINE. One clip, one song, exported twice — at 100% music and at
 *       25% — and the music-to-clip ratio must fall by ~4x (12 dB). This is the
 *       one edit everybody makes after dropping a song onto footage, and until
 *       this rung it was unaskable.
 *
 *   L2  THE CHIP SAYS SO WITHOUT OPENING ANYTHING. A level that only exists
 *       inside a sheet is a level nobody can see they set.
 *
 *   L3  MUTE STILL WINS, AT EVERY LEVEL. `muted` is intent and the level is what
 *       the sound does when it is NOT muted; a level that could resurrect a
 *       muted source would have made the two controls one, which is the
 *       two-guards-on-one-resource defect this app's audio path is scarred by.
 *
 *   L4  IT IS WATERTIGHT ON A PHONE. Five more 44 px chips inside the sheet that
 *       already carries a trim strip, two range handles and a speed roster, at
 *       320/360/390/430 px.
 *
 * Run against the running collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.level.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.level.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { measureTones, HZ_CONTROL } from './tone-measure';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** 440 Hz, with a picture. The thing the music has to sit UNDER. */
const CLIP = join(HERE, '..', 'fixtures', 'tone_a.mp4');
const HZ_CLIP = 440;

/** 1200 Hz, in a .mov — the second clip L5 measures the first one against, and
 *  the container pair `video-audio-export.spec.ts` already covers (plain ISO and
 *  QuickTime), so a level is not accidentally proved on one muxer only. */
const CLIP_B = join(HERE, '..', 'fixtures', 'tone_b.mov');
const HZ_CLIP_B = 1200;

/** 2.0 s of a pure 1500 Hz sine, audio only. The thing being turned down. */
const MUSIC = join(HERE, '..', 'fixtures', 'music_1500.m4a');
const HZ_MUSIC = 1500;

/** MUSIC IS NOT A SOURCE ON ITS OWN. There is no collage — and therefore no
 *  dock, and therefore no music chip — until something can be DRAWN, which is
 *  `soundtrack.spec`'s `bootWithPhotos` for the same reason. The two tests that
 *  do not need a clip's sound take these instead, because a photo collage is
 *  cheaper to render than a video one and neither is measuring the picture. */
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');

async function boot(page: Page) {
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
}

/** Boot with two photographs, so the collage — and with it the dock the music
 *  chip lives in — actually exists. */
async function bootWithPhotos(page: Page) {
  await boot(page);
  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
}

/** Leave the clip's sound ON whatever the import default is — `video-audio-export`'s
 *  rule, and for its reason: a test that breaks when a default moves was testing
 *  the default. */
const ensureClipSoundOn = async (page: Page, name: string) => {
  const off = page.getByRole('button', { name: `Unmute ${name}` });
  if (await off.count()) await off.first().click();
  await expect(page.getByRole('button', { name: `Mute ${name}` })).toBeVisible({ timeout: 15_000 });
};

/** A 5 s take rather than the default 10: half the render, still two and a half
 *  laps of the 2 s track. */
async function pickShortTake(page: Page) {
  const five = page.getByRole('button', { name: '5s', exact: true });
  if (await five.count()) await five.first().click();
}

/**
 * RECORD, AND PROVE AN ARTIFACT EXISTS BEFORE MEASURING IT — `soundtrack.spec`'s
 * guard, kept because a measurement that finds no file returns "not ok" and a
 * ratio computed from two absent files is 0/0, which is a shape a careless
 * assertion can read as success.
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
  expect(text, 'this suite measures sound; a silent export proves nothing about a level').toContain('sound');
  return text;
}

/** Dismiss the result sheet so the dock is reachable for the next take. */
async function closeResult(page: Page) {
  const close = page.getByRole('button', { name: /close|done/i }).last();
  if (await close.count()) await close.click().catch(() => { /* already gone */ });
  await expect(page.locator('video[controls]')).toBeHidden({ timeout: 30_000 }).catch(() => { /* fine */ });
}

/**
 * THE QUANTITY UNDER TEST: music energy over clip energy in ONE decoded file.
 * The limiter's scalar cancels; the encoder's gain cancels; the take length
 * cancels. What is left is the level.
 */
async function musicOverClip(page: Page, tag: string): Promise<number> {
  const t = await measureTones(page, [HZ_MUSIC, HZ_CLIP], HZ_CONTROL);
  expect(t.ok, `the export must carry an audio track — ${t.reason}`).toBe(true);
  const music = t.bins[0];
  const clip = t.bins[1];
  console.log(`[level] ${tag}: 1500Hz=${music.toFixed(5)} 440Hz=${clip.toFixed(5)} ` +
    `control=${t.control.toFixed(5)} ratio=${(music / (clip || 1e-9)).toFixed(4)} rms=${t.rms.toFixed(4)}`);
  // BOTH tones must actually be there, or the ratio is measuring an absence. A
  // missing clip tone makes the ratio enormous; a missing music tone makes it 0,
  // and either would sail through a one-sided bound.
  expect(music, `the music must be in the file at all (${tag})`).toBeGreaterThan(t.control * 4);
  expect(clip, `the clip's own sound must be in the file at all (${tag})`).toBeGreaterThan(t.control * 4);
  return music / clip;
}

/** Open the music's sheet, set a level chip, close it. */
async function setMusicLevel(page: Page, chip: string) {
  await page.getByRole('button', { name: /Trim music_1500\.m4a/ }).click();
  const target = page.getByTestId(`level-${chip}`);
  await expect(target, 'the level roster must be on the music sheet').toBeVisible({ timeout: 15_000 });
  await target.click();
  await expect(target).toHaveAttribute('aria-pressed', 'true', { timeout: 10_000 });
  await page.getByRole('button', { name: 'Done' }).click();
}

test.describe('THE LEVEL', () => {
  test('L1 — turning the music down moves the mix, measured in the file', async ({ page }) => {
    test.setTimeout(900_000);
    await boot(page);

    await page.locator('input[type="file"]').first().setInputFiles([CLIP]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await ensureClipSoundOn(page, 'tone_a.mp4');

    await musicInput(page).setInputFiles([MUSIC]);
    await expect(
      page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }),
    ).toBeVisible({ timeout: 60_000 });

    // --- take one: the music at 100%, which is where it has always been -------
    await renderTake(page);
    const loud = await musicOverClip(page, 'music at 100%');
    await closeResult(page);

    // --- take two: the same collage with the music at 25% ---------------------
    await setMusicLevel(page, 'quarter');
    await renderTake(page);
    const quiet = await musicOverClip(page, 'music at 25%');

    const moved = quiet / loud;
    const dB = -20 * Math.log10(moved);
    console.log(`[level] ratio 100%: ${loud.toFixed(4)} -> 25%: ${quiet.toFixed(4)} ` +
      `= ${moved.toFixed(4)}x (${dB.toFixed(1)} dB down)`);

    // 0.25 exactly, if AAC were transparent. The band is generous in the same
    // proportion the codec is lossy — and it is still nowhere near 1.0, which is
    // what a chip wired to nothing would produce, nor near 0, which is what a
    // chip that muted instead of quietening would.
    expect(
      moved,
      `the music must sit ~12 dB under where it was — got ${dB.toFixed(1)} dB`,
    ).toBeGreaterThan(0.15);
    expect(
      moved,
      `the music must actually move — got ${dB.toFixed(1)} dB, which is a control doing nothing`,
    ).toBeLessThan(0.42);
  });

  test('L2 — the chip says the level without opening anything', async ({ page }) => {
    test.setTimeout(300_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC]);
    await expect(page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }))
      .toBeVisible({ timeout: 60_000 });

    // Absent at 100%: a badge that renders for every source is not a badge.
    await expect(page.getByTestId('track-level')).toHaveCount(0);

    await setMusicLevel(page, 'bed');
    await expect(
      page.getByTestId('track-level'),
      'a quietened track must say so on the chip, not only inside the sheet',
    ).toHaveText('6%', { timeout: 15_000 });

    // AND IT SURVIVES A REBUILD. The level is written to the Stage AND to the
    // parent in one handler precisely because the parent owns the track; if only
    // the Stage knew, this would read 100% again the moment anything remounted.
    await page.getByRole('button', { name: /Trim music_1500\.m4a/ }).click();
    await expect(page.getByTestId('level-bed')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('level-readout')).toContainText('24.1 dB under');
    await page.getByRole('button', { name: 'Done' }).click();
  });

  test('L3 — mute still wins at every level', async ({ page }) => {
    test.setTimeout(600_000);
    await boot(page);
    await page.locator('input[type="file"]').first().setInputFiles([CLIP]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await ensureClipSoundOn(page, 'tone_a.mp4');
    await musicInput(page).setInputFiles([MUSIC]);
    await expect(page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }))
      .toBeVisible({ timeout: 60_000 });

    // A level is set FIRST, then the source is muted. The order matters: a
    // implementation that treated the level as the gain outright — rather than
    // as a multiplier ON intent — would put the music back at 6% instead of out.
    await setMusicLevel(page, 'bed');
    await page.getByRole('button', { name: /Hear the music/ }).click();
    await page.getByRole('button', { name: /Mute the music/ }).click();
    await expect(page.getByRole('button', { name: /Put the music back in the piece/ }))
      .toBeVisible({ timeout: 15_000 });

    // The sheet must SAY the level cannot be heard rather than going quietly
    // inert — the defect class this component is scarred by four times over.
    await page.getByRole('button', { name: /Trim music_1500\.m4a/ }).click();
    await expect(page.getByTestId('level-readout')).toContainText('out of the piece');
    await expect(page.getByTestId('level-bed'), 'the roster stays usable on a muted source')
      .toBeEnabled();
    await page.getByRole('button', { name: 'Done' }).click();

    await renderTake(page);
    const t = await measureTones(page, [HZ_MUSIC, HZ_CLIP], HZ_CONTROL);
    console.log(`[level] muted-at-6%: 1500Hz=${t.bins[0].toFixed(5)} 440Hz=${t.bins[1].toFixed(5)} ` +
      `control=${t.control.toFixed(5)}`);
    expect(t.ok, `the clip's own sound must still be in the file — ${t.reason}`).toBe(true);
    expect(t.bins[1], 'the clip must still be audible; only the music was muted')
      .toBeGreaterThan(t.control * 4);
    /**
     * AGAINST THE CLIP, NOT AGAINST THE CONTROL — and the first draft of this
     * assertion got it wrong in a way worth keeping written down.
     *
     * `soundtrack.spec` T2 bounds its muted case at `control * 4`, and that is
     * right THERE: its collage is photographs, so muting the only source leaves
     * the mixer writing no audio track at all and the bound is over digital
     * silence. Here a 440 Hz clip is still sounding, so the file is a real AAC
     * encode and EVERY empty bin carries that encode's quantisation noise —
     * including the 5000 Hz control. Measured: music 0.00015 against a control
     * of 0.000042, i.e. 3.6x the "floor", on a take where the music is 732x down
     * from where it sits unmuted and 567x below the clip it was under. The tone
     * is gone; the yardstick moved.
     *
     * So the bound is a RATIO WITHIN THE FILE, which is this suite's whole
     * design: a muted source must sit at least 100x (40 dB) under the source it
     * shares the mix with. A level that failed to compose with mute — one that
     * put the music back at 6% instead of out — measures ~16x under, and fails
     * this by a factor of six.
     */
    const underClip = t.bins[1] / t.bins[0];
    console.log(`[level] muted music sits ${underClip.toFixed(0)}x under the clip`);
    expect(
      underClip,
      `a muted track must be GONE, not quiet — 1500Hz=${t.bins[0]} vs clip ${t.bins[1]}`,
    ).toBeGreaterThan(100);
  });

  /**
   * A CLIP'S LEVEL TRAVELS A DIFFERENT ROUTE FROM THE MUSIC'S, and that is the
   * whole reason this test exists rather than being argued from L1.
   *
   * The music's level is written to the Stage AND to the parent, comes back
   * through `setSoundtrack`'s same-url branch, and is emitted by
   * `soundtrack.soundtrackSource`. A clip's is written to the Stage ONLY, lives
   * on the clip record beside its mute, and is emitted by
   * `describeAudioSources`. Two emitters, two lifetimes, one `mixGain` — and
   * "the wiring is the same" is an argument, which is exactly the kind of thing
   * that was true about this app's audio path on the days its exports shipped
   * silent. So it gets its own file and its own division.
   */
  test('L5 — a clip’s own level moves the mix too, on its own route', async ({ page }) => {
    test.setTimeout(600_000);
    await boot(page);

    await page.locator('input[type="file"]').first().setInputFiles([CLIP, CLIP_B]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await ensureClipSoundOn(page, 'tone_a.mp4');
    await ensureClipSoundOn(page, 'tone_b.mov');

    // Quieten A (440 Hz) and leave B (1200 Hz) alone. ONE export is enough here:
    // the clips are two independent sources in one file, so B is the reference A
    // is measured against and there is nothing a second take would add.
    await page.getByRole('button', { name: 'Trim tone_a.mp4' }).click();
    await expect(page.getByTestId('level-quarter')).toBeVisible({ timeout: 15_000 });
    await page.getByTestId('level-quarter').click();
    await expect(page.getByTestId('level-quarter')).toHaveAttribute('aria-pressed', 'true');
    await page.getByRole('button', { name: 'Done' }).click();

    // The badge is the clip's, read off the Stage row rather than off React state.
    await expect(
      page.getByTestId('clip-level-badge-' + (await page.evaluate(() => {
        const b = document.querySelector('[data-testid^="clip-level-badge-"]');
        return b?.getAttribute('data-testid')?.replace('clip-level-badge-', '') ?? '';
      }))),
      'a quietened clip must say so on its chip',
    ).toHaveText('25%');

    await renderTake(page);
    const t = await measureTones(page, [HZ_CLIP, HZ_CLIP_B], HZ_CONTROL);
    expect(t.ok, `the export must carry an audio track — ${t.reason}`).toBe(true);
    const ratio = t.bins[0] / t.bins[1];
    console.log(`[level] clip A at 25%: 440Hz=${t.bins[0].toFixed(5)} 1200Hz=${t.bins[1].toFixed(5)} ` +
      `control=${t.control.toFixed(5)} A/B=${ratio.toFixed(4)}`);
    expect(t.bins[1], 'the untouched clip must still be at full').toBeGreaterThan(t.control * 8);
    expect(t.bins[0], 'the quietened clip must still be IN the mix, not muted')
      .toBeGreaterThan(t.control * 4);

    /**
     * THE BOUND IS AGAINST THE UNTOUCHED PAIR, MEASURED — not against 0.25.
     * `video-audio-export.spec.ts` exports these same two clips at full and
     * reads 440=0.08489, 1200=0.11819, i.e. A/B = 0.7183 with nobody quietened:
     * the two fixtures are not equally loud and never were. A quarter of that is
     * 0.1796, and the band below is that number with room for the codec.
     */
    const BOTH_FULL = 0.08489 / 0.11819;
    const moved = ratio / BOTH_FULL;
    console.log(`[level] A/B ${BOTH_FULL.toFixed(4)} at full -> ${ratio.toFixed(4)} = ${moved.toFixed(4)}x`);
    expect(moved, `the clip must sit ~12 dB under where it was — got ${(-20 * Math.log10(moved)).toFixed(1)} dB`)
      .toBeGreaterThan(0.15);
    expect(moved, 'the clip level must actually move the file').toBeLessThan(0.42);
  });

  test('L4 — the sheet is watertight at phone widths with the level row in it', async ({ page }) => {
    test.setTimeout(300_000);
    await bootWithPhotos(page);
    await musicInput(page).setInputFiles([MUSIC]);
    await expect(page.getByRole('button', { name: /Remove the music, music_1500\.m4a/ }))
      .toBeVisible({ timeout: 60_000 });
    await page.getByRole('button', { name: /Trim music_1500\.m4a/ }).click();
    await expect(page.getByTestId('level-full')).toBeVisible({ timeout: 15_000 });

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      const m = await page.evaluate(() => {
        const chips = Array.from(document.querySelectorAll('[data-testid^="level-"]'))
          .filter((e) => e.tagName === 'BUTTON') as HTMLElement[];
        return {
          sw: document.documentElement.scrollWidth,
          cw: document.documentElement.clientWidth,
          chips: chips.length,
          // The 44 px thumb floor, and the widest chip, so a roster that fits by
          // overflowing its row rather than by shrinking is visible here.
          short: chips.filter((e) => e.getBoundingClientRect().height < 43.5).length,
          right: Math.max(...chips.map((e) => Math.round(e.getBoundingClientRect().right))),
        };
      });
      console.log(`[level] @${width}px  scrollWidth=${m.sw} client=${m.cw} chips=${m.chips} ` +
        `shortest-under-44=${m.short} rightmost=${m.right}`);
      expect(m.chips, `all five level chips must be present at ${width}px`).toBe(5);
      expect(m.sw, `the page must not scroll sideways at ${width}px`).toBeLessThanOrEqual(m.cw);
      expect(m.short, `every level chip must clear 44px at ${width}px`).toBe(0);
      expect(m.right, `the roster must not run past the viewport at ${width}px`)
        .toBeLessThanOrEqual(m.cw + 1);
    }
  });
});
