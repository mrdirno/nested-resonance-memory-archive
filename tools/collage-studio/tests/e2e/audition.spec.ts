// tests/e2e/audition.spec.ts
// -----------------------------------------------------------------------------
// CUT AUDITION — THE ARTIFACT PROOF: holding a trim handle makes the monitor
// loop that cut, releasing keeps it looping, closing gives the room back.
//
// From the well, verbatim: "The audio ripping doesn't have a playback… if
// you're at the front you play on the cut, if you're dragging the back you play
// a few seconds before up to the cut, then loop again to dial things in
// quickly." Every test here is one clause of that sentence.
//
// WHY THE ASSERTIONS READ THE ELEMENT, NOT THE SPEAKER. The audition retargets
// the Stage's OWN track element (`stage.setAudition`), so `muted`, `paused` and
// `currentTime` on that one element ARE the feature's observable state — and
// they are identical across engines, where AudioContext plumbing is not. The
// suite's own history (soundtrack.spec: intent-vs-audible) is why the monitor
// is also asserted to be ROLLING, never just "in range": a parked playhead
// inside the window is silence wearing the right number.
//
// DETERMINISM (panel-judged): real pointer/keyboard input only — Playwright's
// input carries user activation; `locator.focus()` does not, and `.play()`
// without activation rejects. Position asserted by POLLED SAMPLES with ~0.6 s
// slop (timeupdate granularity + the 150 ms reseek throttle + engine seek
// latency), never by one read after a fixed wait. No clock mocking: the media
// clock is the thing under test.
//
//   npx playwright test tests/e2e/audition.spec.ts
// or against the deployed release:
//   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
//     npx playwright test tests/e2e/audition.spec.ts
// -----------------------------------------------------------------------------

import { test, expect, type Page, type Locator } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');
/** 6.0 s in three 2.0 s tone thirds (900/1500/2300 Hz), audio only. */
const MUSIC_THIRDS = join(HERE, '..', 'fixtures', 'music_thirds.m4a');
/** 2.0 s of 1500 Hz — the REPLACEMENT song for the recovery test. */
const MUSIC_1500 = join(HERE, '..', 'fixtures', 'music_1500.m4a');

const TAIL = 2.5;   // AUDITION_TAIL_SEC — pinned by tests/unit/audition.invariants.mjs
const SLOP = 0.6;

/**
 * The one forgiven pageerror: WebKit races the app's own SW `reg.update()`
 * against THIS harness's unregister-service-workers boot step — an artifact of
 * the test rig, reproducible with the audition code absent. Nothing else is
 * forgiven (C164: a green run must not hide an uncaught assert).
 */
const HARNESS_ERRORS = [/service worker registration/i];
const realErrors = (errors: string[]) =>
  errors.filter((m) => !HARNESS_ERRORS.some((re) => re.test(m)));

/**
 * How the position walks are judged, and why not "every sample in bounds":
 * twenty media-playing tests share this machine's CPU, and a wrap seek landing
 * a beat late under that load parks one sample past the boundary — harness
 * weather, not the feature. So: MOST samples inside the window (0.8), a HARD
 * ceiling/floor a real defect would break (a dead wrap runs away monotonically;
 * a wrap to 0 instead of the cut floors every post-wrap sample), and the wrap
 * itself observed. A wrong window fails the share; a dead feature fails them all.
 */
const shareInside = (samples: number[], lo: number, hi: number) =>
  samples.filter((v) => v >= lo && v <= hi).length / Math.max(1, samples.length);

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');
/** The Stage's one `<audio>` — the track monitor the audition retargets. */
const monitor = (page: Page) => page.locator('audio').first();

const monitorState = (page: Page) =>
  monitor(page).evaluate((el: HTMLAudioElement) => ({
    muted: el.muted, paused: el.paused, t: el.currentTime,
  }));

/** N samples of `currentTime`, `gapMs` apart — the rolling-monitor instrument. */
const sampleTimes = async (page: Page, n: number, gapMs: number): Promise<number[]> => {
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    out.push((await monitorState(page)).t);
    await page.waitForTimeout(gapMs);
  }
  return out;
};

async function bootWithPhotosAndMusic(page: Page, errors: string[]) {
  page.on('pageerror', (e) => errors.push(e.message));   // C164: a green run must not hide an uncaught assert
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW in this context is fine */ });
  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await musicInput(page).setInputFiles(MUSIC_THIRDS);
}

/** Open the trim sheet once the length probe lands (the button gates on it). */
async function openSheet(page: Page, name: string): Promise<Locator> {
  const btn = page.getByRole('button', { name: `Trim ${name}` });
  await expect(btn).toBeEnabled({ timeout: 30_000 });
  await btn.click();
  const sheet = page.getByRole('dialog', { name: `Trim ${name}` });
  await expect(sheet).toBeVisible();
  return sheet;
}

/** Click a range input at a fraction of its width and return the value it took
 *  — the assert target is what the input REALLY became, not a prediction of
 *  what a click lands on (engines disagree about thumb geometry). */
async function grabAt(slider: Locator, frac: number): Promise<number> {
  const box = await slider.boundingBox();
  if (!box) throw new Error('slider has no box');
  await slider.click({ position: { x: Math.max(2, box.width * frac), y: box.height / 2 } });
  return parseFloat(await slider.inputValue());
}

test.describe('cut audition', () => {

  test('T1 — grabbing the IN handle plays ON the cut, and the monitor rolls', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await bootWithPhotosAndMusic(page, errors);
    const sheet = await openSheet(page, 'music_thirds.m4a');

    // Before any grab the room is as the user left it: sound never enabled.
    expect((await monitorState(page)).muted, 'monitor muted before the grab — audition must be what unmutes it').toBe(true);

    const inSlider = sheet.getByRole('slider', { name: 'In point for music_thirds.m4a' });
    const cut = await grabAt(inSlider, 1 / 3);
    expect(cut).toBeGreaterThan(0.5);   // the grab really moved the handle

    // The grab is the gesture: unmuted, rolling, inside [cut, cut+tail].
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(false);
    await expect.poll(async () => (await monitorState(page)).paused, { timeout: 5_000 }).toBe(false);
    await expect.poll(async () => (await monitorState(page)).t, { timeout: 5_000 })
      .toBeGreaterThan(cut - SLOP);
    const walk = await sampleTimes(page, 5, 120);
    expect(new Set(walk.map((v) => v.toFixed(3))).size,
      `the monitor must actually be rolling — ${walk.join(',')}`).toBeGreaterThan(1);
    expect(shareInside(walk, cut - SLOP, cut + TAIL + SLOP),
      `audition stayed around [cut, cut+tail] — ${walk.map((v) => v.toFixed(2)).join(',')}`)
      .toBeGreaterThanOrEqual(0.8);
    for (const v of walk) {
      expect(v, `hard floor: a wrap must land on the cut, never at 0 — ${walk.join(',')}`)
        .toBeGreaterThan(cut - TAIL / 2);
    }

    // The playhead line is drawn, on the strip, while the handle is hot.
    const opacity = await sheet.getByTestId('audition-playhead')
      .evaluate((el) => (el as HTMLElement).style.opacity);
    expect(opacity).toBe('1');

    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T2 — the loop comes round on the cut, and release does not stop it', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await bootWithPhotosAndMusic(page, errors);
    const sheet = await openSheet(page, 'music_thirds.m4a');
    const inSlider = sheet.getByRole('slider', { name: 'In point for music_thirds.m4a' });
    const cut = await grabAt(inSlider, 1 / 4);

    // Pointer is UP now (click released) — "then loop again": still rolling.
    await expect.poll(async () => (await monitorState(page)).paused, { timeout: 5_000 }).toBe(false);

    // Watch most of two laps: never past the tail boundary, and at least one
    // visible wrap — a backward jump of more than half the loop.
    const samples = await sampleTimes(page, 30, 150);
    let wrapped = false;
    for (let i = 1; i < samples.length; i++) {
      if (samples[i] < samples[i - 1] - TAIL / 2) wrapped = true;
    }
    expect(wrapped, `expected a lap in ${samples.map((v) => v.toFixed(2)).join(',')}`).toBe(true);
    expect(shareInside(samples, cut - SLOP, cut + TAIL + SLOP),
      `stayed around the audition window — ${samples.map((x) => x.toFixed(2)).join(',')}`)
      .toBeGreaterThanOrEqual(0.8);
    for (const v of samples) {
      // A DEAD wrap runs away monotonically and breaks this ceiling; a late one
      // under harness load does not.
      expect(v, `hard ceiling — ${samples.map((x) => x.toFixed(2)).join(',')}`)
        .toBeLessThan(cut + TAIL + 1.2);
      expect(v, 'hard floor: the wrap lands on the cut, never at 0')
        .toBeGreaterThan(cut - TAIL / 2);
    }
    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T3 — the OUT handle plays the approach, up to the cut; Escape gives the room back', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await bootWithPhotosAndMusic(page, errors);
    const sheet = await openSheet(page, 'music_thirds.m4a');

    const outSlider = sheet.getByRole('slider', { name: 'Out point for music_thirds.m4a' });
    const cut = await grabAt(outSlider, 5 / 6);
    expect(cut).toBeLessThan(6);   // the grab really pulled OUT in from the end

    // The approach: [cut - tail, cut], never meaningfully past the cut.
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(false);
    await expect.poll(async () => (await monitorState(page)).t, { timeout: 6_000 })
      .toBeGreaterThan(cut - TAIL - SLOP);
    const walk = await sampleTimes(page, 12, 150);
    expect(shareInside(walk, cut - TAIL - SLOP, cut + SLOP),
      `approach stayed around [cut-tail, cut] — ${walk.map((x) => x.toFixed(2)).join(',')}`)
      .toBeGreaterThanOrEqual(0.8);
    for (const v of walk) {
      expect(v, `hard ceiling: the loop ends AT the cut — ${walk.map((x) => x.toFixed(2)).join(',')}`)
        .toBeLessThan(cut + 1.0);
      expect(v, 'hard floor: the approach starts at cut-tail, not at 0')
        .toBeGreaterThan(cut - TAIL - 1.0);
    }

    // Escape closes the sheet THROUGH UNMOUNT (no blur first) — the room comes
    // back exactly as it was: muted, because sound was never switched on.
    await page.keyboard.press('Escape');
    await expect(sheet).not.toBeVisible();
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(true);
    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T4 — replacing the song mid-audition recovers instead of dying on a dead blob', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await bootWithPhotosAndMusic(page, errors);
    const sheet = await openSheet(page, 'music_thirds.m4a');
    const inSlider = sheet.getByRole('slider', { name: 'In point for music_thirds.m4a' });
    await grabAt(inSlider, 1 / 3);
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(false);

    // Replace THE SONG while the handle is hot: `adoptSoundtrack` revokes the
    // old blob and swaps the spec without unmounting the sheet's guard — the
    // `key={url}` remount and the Stage's null-audition rebuild are what this
    // test exists to hold.
    await musicInput(page).setInputFiles(MUSIC_1500);
    const sheet2 = page.getByRole('dialog', { name: 'Trim music_1500.m4a' });
    await expect(sheet2).toBeVisible({ timeout: 30_000 });

    // The old audition died with the old track: a fresh sheet, a quiet room.
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(true);

    // And the NEW track auditions — same grab, new song. Gated on the probe
    // having landed (the remounted sheet briefly has span 0).
    await expect(sheet2.getByTestId('trim-readout')).toContainText('of 2.0s', { timeout: 30_000 });
    const inSlider2 = sheet2.getByRole('slider', { name: 'In point for music_1500.m4a' });
    await grabAt(inSlider2, 1 / 3);
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 10_000 }).toBe(false);
    await expect.poll(async () => (await monitorState(page)).t, { timeout: 10_000 }).toBeLessThan(TAIL + SLOP);
    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T5 — watertight at 390 with the audition live', async ({ page }) => {
    test.setTimeout(240_000);
    const errors: string[] = [];
    await page.setViewportSize({ width: 390, height: 844 });
    await bootWithPhotosAndMusic(page, errors);
    const sheet = await openSheet(page, 'music_thirds.m4a');
    const inSlider = sheet.getByRole('slider', { name: 'In point for music_thirds.m4a' });
    await grabAt(inSlider, 1 / 2);
    await expect.poll(async () => (await monitorState(page)).paused, { timeout: 5_000 }).toBe(false);

    const scroll = await page.evaluate(() => ({
      sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    }));
    expect(scroll.sw, '390px with the audition rolling: the page must not scroll sideways')
      .toBeLessThanOrEqual(scroll.cw);

    // The playhead is INSIDE the strip, not painting off its edge.
    const strip = sheet.locator('div.relative.h-16');
    const ph = sheet.getByTestId('audition-playhead');
    const sb = await strip.boundingBox();
    const pb = await ph.boundingBox();
    expect(sb && pb && pb.x >= sb.x - 1 && pb.x + pb.width <= sb.x + sb.width + 1,
      'playhead line stays inside the strip').toBe(true);
    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('T6 — the keyboard arms it too: Tab parks silently, the first arrow speaks, blur stops', async ({ page, browserName }) => {
    test.skip(browserName === 'webkit',
      'WebKit reaches a range input by Tab only with Full Keyboard Access on — the pointer path, which every WebKit test above drives, is the same arming code');
    test.setTimeout(240_000);
    const errors: string[] = [];
    await bootWithPhotosAndMusic(page, errors);
    await openSheet(page, 'music_thirds.m4a');

    // Focus starts on Close (the sheet's own mount rule); one Tab parks on IN.
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() =>
      (document.activeElement as HTMLInputElement | null)?.getAttribute('aria-label') ?? '');
    expect(focused).toBe('In point for music_thirds.m4a');
    // PARKED IS SILENT — focus alone is not a gesture and must not speak.
    expect((await monitorState(page)).muted).toBe(true);

    // The first arrow is the gesture.
    await page.keyboard.press('ArrowRight');
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(false);
    await expect.poll(async () => (await monitorState(page)).paused, { timeout: 5_000 }).toBe(false);

    // Leaving the handle gives the room back.
    await page.keyboard.press('Shift+Tab');
    await expect.poll(async () => (await monitorState(page)).muted, { timeout: 5_000 }).toBe(true);
    expect(realErrors(errors), `pageerrors: ${errors.join(' | ')}`).toEqual([]);
  });
});
