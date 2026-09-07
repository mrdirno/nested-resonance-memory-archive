// tests/e2e/solo.spec.ts
// -----------------------------------------------------------------------------
// SOLO — THE ARTIFACT PROOF: adding audio starts it and opens the room where the
// decision lives; soloing one source puts every other one out of the room and
// changes NOBODY's intent.
//
// From the well, verbatim: "When adding audio — Should start the added audio
// then take immediately to the details to see all audio playing that way user
// can solo the audio to determine what to keep enabled or muted should be
// intuitive." Every test here is one clause of that sentence.
//
// WHY THE ASSERTIONS READ THE ELEMENTS. `applyMutes` writes audibility onto each
// `<video>`/`<audio>` element's own `muted`, and that is the switch which gates
// the signal entering the WebAudio graph — so `el.muted` IS the feature's
// observable state, and it is identical across engines where AudioContext
// plumbing is not. INTENT is read separately, off `aria-pressed` on each
// source's speaker button, because the whole claim of this rung is that the two
// move independently: the room goes quiet, the piece does not change.
//
//   npx playwright test tests/e2e/solo.spec.ts
// or against the deployed release:
//   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
//     npx playwright test tests/e2e/solo.spec.ts
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');
/** A video that carries a tone — a clip whose sound is worth soloing. */
const TONE_A = join(HERE, '..', 'fixtures', 'tone_a.mp4');
/** 6.0 s in three 2.0 s tone thirds, audio only. */
const MUSIC = join(HERE, '..', 'fixtures', 'music_thirds.m4a');
const MUSIC_NAME = 'music_thirds.m4a';
const CLIP_NAME = 'tone_a.mp4';

/** See audition.spec.ts — the one forgiven pageerror family. */
const HARNESS_ERRORS = [/service ?worker/i];
const realErrors = (errors: string[]) =>
  errors.filter((m) => !HARNESS_ERRORS.some((re) => re.test(m)));

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');
const monitor = (page: Page) => page.locator('audio').first();
const detailsToggle = (page: Page) => page.getByRole('button', { name: 'Details', exact: true });

const audioState = (page: Page) =>
  monitor(page).evaluate((el: HTMLAudioElement) => ({ muted: el.muted, paused: el.paused, t: el.currentTime }));

/** Every clip decoder's own gate, in DOM order. */
const clipMutes = (page: Page) =>
  page.locator('video').evaluateAll((els) => els.map((e) => (e as HTMLVideoElement).muted));

async function boot(page: Page, errors: string[], opts?: { withClip?: boolean }) {
  page.on('pageerror', (e) => errors.push(e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });
  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  if (opts?.withClip) {
    await page.locator('input[type="file"]').first().setInputFiles([TONE_A]);
    // THE CLIP IS IN WHEN ITS DECODER IS. Not when its chip is visible: the
    // chips live inside the collapsed Details panel, which nothing has opened
    // yet at this point in the boot — that is the state the next line is about
    // to change, and waiting on it here would be waiting for the feature under
    // test to have already happened.
    await expect.poll(async () => page.locator('video').count(), { timeout: 120_000 })
      .toBeGreaterThan(0);
  }
}

test.describe('solo', () => {

  test('T1 — adding music starts it and opens Details on the sources', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await boot(page, errors);

    // BEFORE: nothing to hear and nowhere to decide it. Stated rather than
    // assumed, because the preview mounts only once something can play — the
    // same ordering that made the first cut of this feature fire into a
    // component that did not exist yet (see `soundArrival` in VideoStage).
    // With photographs alone there is no dock at all — the preview mounts with
    // the first thing that can PLAY. So "the panel is shut" is literally "there
    // is no panel", which is the state a person adding a song is coming from.
    await expect(detailsToggle(page)).toHaveCount(0);

    await musicInput(page).setInputFiles(MUSIC);

    // PART 2 — "take immediately to the details".
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'true', { timeout: 15_000 });
    await expect(page.getByTestId('source-chip-music')).toBeVisible();

    // PART 1 — "should start the added audio". Unmuted AND ROLLING: a parked
    // element with the right number on it is silence wearing a good disguise.
    await expect.poll(async () => (await audioState(page)).muted, { timeout: 15_000 }).toBe(false);
    await expect.poll(async () => (await audioState(page)).paused, { timeout: 15_000 }).toBe(false);
    const first = (await audioState(page)).t;
    await page.waitForTimeout(600);
    expect((await audioState(page)).t, 'the music must actually be advancing').toBeGreaterThan(first);

    // And the notice says the true thing rather than the old "press the speaker".
    await expect(page.getByText(/playing/i).first()).toBeVisible({ timeout: 10_000 });

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T2 — soloing the music puts the clip out of the room and changes no intent', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await boot(page, errors, { withClip: true });
    await musicInput(page).setInputFiles(MUSIC);
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'true', { timeout: 15_000 });

    const clipSpeaker = page.getByRole('button', { name: `Mute ${CLIP_NAME}` });
    // The clip's sound is IN the piece before we start, which is what makes the
    // rest of this test mean anything.
    await expect(clipSpeaker).toHaveAttribute('aria-pressed', 'true');

    await page.getByRole('button', { name: `Solo ${MUSIC_NAME}` }).click();

    // THE ROOM: the music sounds, every clip decoder is gated shut.
    await expect.poll(async () => (await audioState(page)).muted, { timeout: 10_000 }).toBe(false);
    await expect.poll(async () => clipMutes(page), { timeout: 10_000 })
      .toEqual(expect.arrayContaining([true]));
    expect(await clipMutes(page), 'no clip may sound while another source is soloed')
      .not.toContain(false);

    // THE PIECE: untouched. The speaker still says the clip's sound is in the
    // export, and it is still the button that would change that.
    await expect(clipSpeaker).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByRole('button', { name: `Mute ${MUSIC_NAME}` })).toHaveCount(0);

    // AND IT SAYS SO. The banner is the sentence that makes a listening mode
    // safe to offer beside the switches that are not listening modes.
    const banner = page.getByTestId('solo-banner');
    await expect(banner).toBeVisible();
    await expect(banner).toContainText(/export/i);
    await expect(banner).toContainText(MUSIC_NAME);

    // A SHUT PANEL MUST STILL SAY THE ROOM IS SOLOED. Otherwise the state is
    // running with nothing on screen to show it — the panel skeptic's
    // "persistent indicator visible from every screen it can be toggled from".
    await detailsToggle(page).click();
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'false');
    await expect(banner).toBeHidden();
    await expect(detailsToggle(page)).toHaveClass(/video-transport__details-toggle--solo/);
    await expect(detailsToggle(page)).toHaveAttribute('title', new RegExp(`Soloing ${MUSIC_NAME}`));
    await detailsToggle(page).click();
    await expect(banner).toBeVisible();

    // RELEASE — the same button, a second tap, and the mix comes back.
    await page.getByRole('button', { name: `Stop soloing ${MUSIC_NAME}` }).click();
    await expect(banner).toHaveCount(0);
    await expect.poll(async () => clipMutes(page), { timeout: 10_000 })
      .toEqual(expect.arrayContaining([false]));

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T3 — a MUTED source can be soloed, and soloing does not un-mute it', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await boot(page, errors, { withClip: true });
    await musicInput(page).setInputFiles(MUSIC);
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'true', { timeout: 15_000 });

    // Take the clip OUT of the piece — the decision this feature exists to help
    // someone reconsider.
    await page.getByRole('button', { name: `Mute ${CLIP_NAME}` }).click();
    const clipSpeaker = page.getByRole('button', { name: `Unmute ${CLIP_NAME}` });
    await expect(clipSpeaker).toHaveAttribute('aria-pressed', 'false');
    await expect.poll(async () => clipMutes(page), { timeout: 10_000 }).not.toContain(false);

    // Now audition the thing you switched off. This is the clause the whole
    // module is shaped around: "to determine what to keep enabled or muted".
    await page.getByRole('button', { name: `Solo ${CLIP_NAME}` }).click();
    await expect.poll(async () => clipMutes(page), { timeout: 10_000 }).toContain(false);
    // The music steps out, even though ITS sound is in the piece.
    await expect.poll(async () => (await audioState(page)).muted, { timeout: 10_000 }).toBe(true);

    // AND THE DECISION IS STILL THE USER'S. Listening did not re-enable it.
    await expect(clipSpeaker).toHaveAttribute('aria-pressed', 'false');

    // Releasing returns it to the silence the user chose.
    await page.getByRole('button', { name: `Stop soloing ${CLIP_NAME}` }).click();
    await expect.poll(async () => clipMutes(page), { timeout: 10_000 }).not.toContain(false);
    await expect(clipSpeaker).toHaveAttribute('aria-pressed', 'false');

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T4 — removing the soloed source gives the room back', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await boot(page, errors, { withClip: true });
    await musicInput(page).setInputFiles(MUSIC);
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'true', { timeout: 15_000 });

    await page.getByRole('button', { name: `Solo ${CLIP_NAME}` }).click();
    await expect(page.getByTestId('solo-banner')).toBeVisible();
    // The music is out of the room while the clip owns it.
    await expect.poll(async () => (await audioState(page)).muted, { timeout: 10_000 }).toBe(true);

    // Remove the soloed clip. A solo left pointing at nothing is silent for
    // every remaining source, with no chip left to tap to escape it — which is
    // an app that has simply gone deaf.
    await page.getByRole('button', { name: `Stop playing ${CLIP_NAME}` }).click();

    await expect(page.getByTestId('solo-banner')).toHaveCount(0, { timeout: 10_000 });
    await expect.poll(async () => (await audioState(page)).muted, { timeout: 15_000 }).toBe(false);
    await expect.poll(async () => (await audioState(page)).paused, { timeout: 15_000 }).toBe(false);

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T5 — at 320px the chip names survive the fourth button', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await page.setViewportSize({ width: 320, height: 720 });
    await boot(page, errors, { withClip: true });
    await musicInput(page).setInputFiles(MUSIC);
    await expect(detailsToggle(page)).toHaveAttribute('aria-expanded', 'true', { timeout: 15_000 });

    // THE PANEL'S LAYOUT FINDING, asserted rather than eyeballed: the name is on
    // its own row, so a fourth 44px button cannot squeeze it to nothing — which
    // would defeat the one thing solo is for, telling sources apart.
    for (const id of [`source-chip-music`, `source-chip-`]) {
      const chip = id === 'source-chip-music'
        ? page.getByTestId('source-chip-music')
        : page.locator('[data-testid^="source-chip-"]').first();
      const name = chip.locator('.video-transport__chip-name').first();
      const box = await name.boundingBox();
      expect(box, `${id}: the name row must be laid out`).not.toBeNull();
      expect(box!.width, `${id}: the name row is ${box!.width}px wide at 320`).toBeGreaterThan(60);
    }

    // Every tap target on the row still clears 44px.
    const taps = await page.locator('.video-transport__chip-actions > button').evaluateAll(
      (els) => els.map((e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; }),
    );
    expect(taps.length, 'the action rows must have rendered').toBeGreaterThan(3);
    for (const [w, h] of taps) {
      expect(Math.min(w, h), `a ${w}x${h} tap target is under the 44px floor`).toBeGreaterThanOrEqual(43.5);
    }

    // And the page still does not scroll sideways.
    const over = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(over, 'the page must not scroll horizontally at 320px').toBeLessThanOrEqual(1);

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });
});
