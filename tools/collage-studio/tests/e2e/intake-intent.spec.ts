/**
 * THE WISH, AT THE ARTIFACT — both halves of one field report.
 *
 *   *"Be able to add music or sound without the video. Right now if you use a
 *   video for the sound or import audio from video it just imports video… if
 *   you're importing audio it should not display the video.*
 *
 *   *Also when full mode is active if I click a box or segment there should be
 *   ability to remove that from the group of images displayed or videos."*
 *
 * WHY THESE TESTS AND NOT THE UNIT SWEEPS. `tests/unit/intake.invariants.mjs`
 * proves the ladder answers "music" for a `.mov` under the music intent, and
 * `tests/unit/evict.invariants.mjs` proves which ids leave a pool. Neither can
 * see the two things that actually broke: that all three file buttons were
 * wired to ONE handler which never learned which was pressed, and that the
 * desktop picker's `accept` list greyed the video out before the routing ever
 * ran. Those are wiring, and wiring is only visible at the page.
 *
 *   T1  THE MUSIC BUTTON TAKES THE SOUND AND LEAVES THE PICTURES. A .mov with a
 *       real h264 track: the chip appears, and the fragment count does NOT move.
 *       Before this, that file became a third fragment — the rectangle in the
 *       report.
 *   T2  AND THE SOUND IS REALLY IN THE FILE. Structural absence ("no new
 *       fragment") is exactly the cheap green this repo has been burned by, so
 *       the second half is a Goertzel read of the DECODED export: 440 Hz, the
 *       clip's own tone, against a 5000 Hz control. A collage of two
 *       photographs has no other way to make a sound.
 *   T3  AN AUDIO-ONLY .mp4 IS SOUND, NOT A BROKEN CLIP. The ambiguous container
 *       belongs to video under every other path — deliberately — and the music
 *       button is the one place that must overrule it.
 *   T4  A PICTURE HANDED TO THE MUSIC BUTTON IS REFUSED, ALOUD. "I asked for
 *       sound and got a picture" is the bug; quietly adding the jpg would be
 *       that same bug wearing a different extension.
 *   T5  FULL BLEED: TAP A FRAGMENT, THROW ITS SOURCE OUT. The second half of
 *       the wish, end to end — the pool shrinks by exactly one and the notice
 *       names the file that left.
 *   T6  AND THE PIN STILL WORKS — outside full bleed the tap pins directly,
 *       exactly as it always has, and inside it the pin is one labelled button
 *       away.
 *   T7  MOBILE-WATERTIGHT. The puck at 320/360/390/430: nothing spills, both
 *       targets are 44 px, and both are reachable over the artwork.
 *
 * Run against the running collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.intake.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.intake.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';
import { measureTones, HZ_CONTROL } from './tone-measure';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** h264 pictures AND a 440 Hz AAC tone, in the container the wish names. */
const CLIP_MOV = join(HERE, '..', 'fixtures', 'tone_a.mov');
const HZ_CLIP = 440;
/** An .mp4 carrying ONLY an AAC track — the ambiguous container, with no pictures. */
const SOUND_ONLY = join(HERE, '..', 'fixtures', 'soundonly.mp4');
const A_PICTURE = join(HERE, '..', 'fixtures', 'img_a.jpg');

// A valid solid-colour PNG built in-process, so a test can upload any number of
// DISTINCT photos with no fixture files (copied shape from source-count.spec).
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
const PALETTE: [number, number, number][] = [[220, 40, 40], [40, 200, 90], [60, 90, 230], [230, 200, 40], [180, 60, 210]];
const photos = (n: number) =>
  Array.from({ length: n }, (_, i) => {
    const [r, g, b] = PALETTE[i % PALETTE.length];
    return { name: `photo_${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b) };
  });

const anyInput = (page: Page) => page.locator('input[type="file"]').first();
/** `accept*="audio"` is how five other suites find this input; it stays true
 *  after the accept list widened to take video containers too. */
const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');

/** The integer shown as "<n> FRAGMENTS" in the persistent readout — the pool
 *  size, because the count follows `distinctSourceCount` until someone owns it. */
const fragments = (page: Page) =>
  page.evaluate(() => {
    const el = document.querySelector('.ui-readout');
    const m = el?.textContent?.match(/(\d+)\s*FRAGMENTS/i);
    return m ? parseInt(m[1], 10) : null;
  });

async function boot(page: Page, n = 2) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.evaluate(async () => {
    const regs = await navigator.serviceWorker?.getRegistrations?.();
    if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
    if (typeof caches !== 'undefined') { for (const k of await caches.keys()) await caches.delete(k); }
  }).catch(() => { /* no SW here is fine */ });
  await anyInput(page).setInputFiles(photos(n));
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await expect.poll(() => fragments(page), { timeout: 60_000 }).toBe(n);
}

/** The preview's own partition — the overlay App.tsx draws from `layoutItems`. */
const cells = (page: Page) => page.locator('svg[viewBox^="0 0 1200 "] > g');

/**
 * Point at a fragment, and wait until the puck is actually up.
 *
 * RETRIED ON PURPOSE, and the retry is documentation. The arming is cleared
 * whenever the partition changes — an index into a layout that has been replaced
 * points at a different fragment, and a Remove button floating over the wrong
 * picture is the worst bug this feature could have. Removing a source rebuilds
 * the partition, so a tap landing in the window between the pool changing and
 * the new layout settling is swallowed BY DESIGN. The app would rather eat a tap
 * than delete the wrong photograph; the test taps again, exactly as a hand would.
 */
async function armCell(page: Page, n = 0) {
  const puck = page.getByTestId('cell-actions');
  await expect.poll(async () => {
    if (await puck.count()) return true;
    await cells(page).nth(n).click({ force: true }).catch(() => { /* mid-relayout */ });
    await page.waitForTimeout(400);
    return (await puck.count()) > 0;
  }, { timeout: 30_000 }).toBe(true);
  return puck;
}

async function enterFullBleed(page: Page) {
  await page.getByRole('button', { name: 'Maximize the shot' }).click();
  await expect(page.getByRole('button', { name: 'Exit full bleed' })).toBeVisible({ timeout: 15_000 });
}

test.describe('THE WISH — sound without the pictures, and a fragment you can throw out', () => {
  test('T1 — the music button takes a .mov for its SOUND and adds no fragment', async ({ page }) => {
    await boot(page, 2);

    await musicInput(page).setInputFiles(CLIP_MOV);
    await expect(
      page.getByRole('button', { name: /Remove the music, tone_a\.mov/ }),
      'the clip must be adopted as the SOUNDTRACK — the chip names the file',
    ).toBeVisible({ timeout: 60_000 });

    // THE REPORT, INVERTED. A .mov routed as video takes ~10 s to probe, extract
    // a poster and land; polling to a steady 2 for longer than that is what makes
    // "no rectangle appeared" a measurement rather than a race won by luck.
    await page.waitForTimeout(6_000);
    expect(await fragments(page), 'the video must NOT have become a fragment').toBe(2);
    // And no live CLIP was mounted for it either. Not by the trim button —
    // a clip row and the music row both offer `Trim <name>`, and asserting on
    // that would have failed against the very chip this test wants. A clip row
    // is the only one carrying its own mute.
    await expect(
      page.getByRole('button', { name: /^(Mute|Unmute) tone_a\.mov$/ }),
      'the file must be a soundtrack, not a clip with pictures in the collage',
    ).toHaveCount(0);
  });

  test('T2 — and the sound is really in the exported file (440 Hz, decoded)', async ({ page }) => {
    test.setTimeout(420_000);
    await boot(page, 2);
    await musicInput(page).setInputFiles(CLIP_MOV);
    await expect(page.getByRole('button', { name: /Remove the music, tone_a\.mov/ })).toBeVisible({ timeout: 60_000 });

    const five = page.getByRole('button', { name: '5s', exact: true });
    if (await five.count()) await five.first().click();
    await page.getByRole('button', { name: 'Record video' }).click();
    const readout = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
    await expect(readout).toBeVisible({ timeout: 360_000 });
    const text = (await readout.first().innerText()).replace(/\s+/g, ' ');
    const src = await page.evaluate(() => (document.querySelector('video[controls]') as HTMLVideoElement | null)?.src ?? '');
    expect(src, 'the take must have produced a real file to measure').toContain('blob:');
    console.log(`[intake] result: ${text}`);

    const t = await measureTones(page, [HZ_CLIP], HZ_CONTROL);
    console.log(`[intake] decoded ${t.durationSec.toFixed(2)}s rms=${t.rms.toFixed(4)} ` +
      `440Hz=${t.bins[0].toFixed(5)} control=${t.control.toFixed(5)} ratio=${(t.bins[0] / (t.control || 1e-9)).toFixed(1)}x`);
    expect(t.ok, `the export must carry an audio track — ${t.reason}`).toBe(true);
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);
    expect(
      t.bins[0],
      `440 Hz — the CLIP's tone — must be in a collage of two photographs, ` +
      `which have no other way to make a sound (clip=${t.bins[0]} control=${t.control})`,
    ).toBeGreaterThan(t.control * 8);
  });

  test('T3 — an audio-only .mp4 through the music button is sound, not a broken clip', async ({ page }) => {
    await boot(page, 2);
    await musicInput(page).setInputFiles(SOUND_ONLY);
    await expect(
      page.getByRole('button', { name: /Remove the music, soundonly\.mp4/ }),
      'an .mp4 with no video track is exactly the file the ambiguous-container rule mis-sorts',
    ).toBeVisible({ timeout: 60_000 });
    await page.waitForTimeout(4_000);
    expect(await fragments(page)).toBe(2);
  });

  test('T4 — a picture handed to the music button is refused ALOUD, never added', async ({ page }) => {
    await boot(page, 2);
    await musicInput(page).setInputFiles(A_PICTURE);
    await expect(
      page.getByText(/music button takes sound/i),
      'a refusal that says which button you pressed is recoverable; a silent picture is the bug',
    ).toBeVisible({ timeout: 20_000 });
    await page.waitForTimeout(2_000);
    expect(await fragments(page), 'the jpg must not have joined the collage').toBe(2);
    await expect(page.getByRole('button', { name: /Remove the music/ })).toHaveCount(0);
  });

  test('T5 — full bleed: tap a fragment, throw its source out of the pool', async ({ page }) => {
    await boot(page, 3);
    await enterFullBleed(page);

    // Nothing is offered until you point at something — the tap is what asks.
    await expect(page.getByTestId('cell-actions')).toHaveCount(0);
    const puck = await armCell(page, 0);
    await expect(puck, 'tapping a fragment in full bleed must offer what can be done to it').toBeVisible({ timeout: 10_000 });
    await expect(puck.getByTestId('cell-lock')).toBeVisible();

    await puck.getByTestId('cell-remove').click();

    await expect(
      page.getByText(/^Removed photo_\d\.png\.$/),
      'a removal you cannot identify is indistinguishable from a bug',
    ).toBeVisible({ timeout: 15_000 });
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(2);
    // The puck goes with it, and full bleed is not disturbed — you are still
    // comparing, which is why you were in here.
    await expect(page.getByTestId('cell-actions')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Exit full bleed' })).toBeVisible();

    // A second removal takes exactly one more. (The failure this guards is the
    // one an empty clipId would cause: one tap emptying the pool.)
    const again = await armCell(page, 0);
    await again.getByTestId('cell-remove').click();
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(1);
  });

  test('T6 — outside full bleed the tap still PINS, and inside it the pin is one labelled button away', async ({ page }) => {
    await boot(page, 3);

    // A pinned fragment wears the lock badge — the `<foreignObject>` the overlay
    // draws at its centroid. Counted rather than colour-matched: an ARMED cell is
    // outlined emerald while its puck is open, so the outline colour answers
    // "which one are you pointing at", not "which ones are pinned".
    const pinned = page.locator('svg[viewBox^="0 0 1200 "] foreignObject');

    // The shipped gesture, untouched: no puck, and the fragment pins.
    await cells(page).first().click({ force: true });
    await expect(page.getByTestId('cell-actions'), 'the puck is a full-bleed affordance only').toHaveCount(0);
    await expect(pinned, 'a tap outside full bleed must still pin the fragment').toHaveCount(1, { timeout: 10_000 });

    // And in full bleed the same pin is reachable — labelled, which it never was.
    await enterFullBleed(page);
    await (await armCell(page, 1)).getByTestId('cell-lock').click();
    await expect(pinned).toHaveCount(2, { timeout: 10_000 });
    // The button now offers the opposite, which is how you know it took.
    await expect(page.getByRole('button', { name: 'Unpin this fragment' })).toBeVisible();
  });

  for (const width of [320, 360, 390, 430]) {
    test(`T7 — the fragment puck is watertight at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 780 });
      await boot(page, 4);
      await enterFullBleed(page);
      const puck = await armCell(page, 0);
      await expect(puck).toBeVisible({ timeout: 10_000 });

      const m = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
        bsw: document.body.scrollWidth,
      }));
      expect(m.sw, `the document must not scroll sideways at ${width}px`).toBeLessThanOrEqual(m.cw);
      expect(m.bsw).toBeLessThanOrEqual(m.cw);

      for (const id of ['cell-lock', 'cell-remove']) {
        const box = await puck.getByTestId(id).boundingBox();
        expect(box, `${id} must be on screen at ${width}px`).not.toBeNull();
        expect(Math.round(box!.width), `${id} tap width at ${width}px`).toBeGreaterThanOrEqual(44);
        expect(Math.round(box!.height), `${id} tap height at ${width}px`).toBeGreaterThanOrEqual(44);
        // WHOLE, not merely present: a puck clipped by the edge of the artwork
        // is a button you cannot press, at exactly the fragments in the corners.
        expect(box!.x, `${id} spills off the left at ${width}px`).toBeGreaterThanOrEqual(0);
        expect(box!.x + box!.width, `${id} spills off the right at ${width}px`).toBeLessThanOrEqual(width);
      }

      // And it still does the job at this width.
      await puck.getByTestId('cell-remove').click();
      await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(3);
    });
  }
});
