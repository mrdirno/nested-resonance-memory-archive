/**
 * THE STRIP AT THE ARTIFACT — the ruler stops measuring an empty ten seconds.
 *
 * The arithmetic is swept in tests/unit/takeMap.invariants.mjs (11 invariants,
 * 14 of 14 mutations killed, and the marks asserted against `turnAt` itself).
 * Four things can only be proved out here, and the last two are the point:
 *
 *   S1  THE STRIP IS ON THE PAGE AND COUNTS WHAT IS IN THE TAKE. A sweep can
 *       prove `cutMarks` returns two fractions; only a browser can prove the
 *       app builds the map from the sources it is actually playing and puts it
 *       under the bar.
 *
 *   S2  THE MARKS ARE WHERE THE CUTS ARE, MEASURED IN THE DOM. Not "a tick
 *       exists" — the tick's own bounding box, as a fraction of the row's,
 *       against `hold / take` computed here. A ruler that is 40 ms out looks
 *       right and lies about the one relationship a user is checking.
 *
 *   S3  THE MUSIC MOVES THEM. `march` holds 5.0 s; snapped to a 120 BPM grid it
 *       holds 4.0 s, so the same mode over the same 15 s take goes from TWO
 *       marks at 1/3 and 2/3 to THREE at 4/15, 8/15 and 12/15. This is the
 *       assertion the whole increment exists for: THE BEAT shipped two cycles
 *       ago and there has been no way to see whether it took — the file was the
 *       only witness.
 *
 *   S4  A LANE COUNTS ITS PASSES, AND THE SPEED MOVES THEM. A 6 s clip laps 3
 *       times in a 15 s take; at 2x it laps 5. That number reaching the DOM is
 *       proof the lane's period is `effectiveLength` — the same function the
 *       live element, the offline seek and the offline mixer read — rather than
 *       a duration this component looked up for itself.
 *
 *   S5  IT IS WATERTIGHT ON A PHONE. The mobile law, on new rows added to the
 *       densest bar in the app.
 *
 *   S7  A COLLAGE OF PHOTOGRAPHS THAT MOVES FINALLY HAS A STRIP. The defect
 *       DECISION 5 closes, stated as a before and an after one chip apart: a
 *       still photo collage draws NO strip (correct, and the control), and the
 *       same collage on PUSH draws a drift row whose seam is measured in the
 *       DOM against `MOVE_CYCLE_SEC / take`. This is the commonest thing this
 *       app makes and it was the one composition the ruler said nothing about.
 *
 * Run against the collage dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test tests/e2e/take-strip.spec.ts --project=chromium
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test tests/e2e/take-strip.spec.ts --project=chromium
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** 6.000 s, three flat thirds. Built by trim.spec's suite; borrowed, not copied. */
const RAMP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');
const CLIP = 'ramp_rgb.mp4';

/** The take every assertion here is stated against — a roster value (5/10/15/30). */
const TAKE = 15;
/** `march`'s hold, from lib/turn.ts. */
const MARCH_HOLD = 5.0;
/** The click track's tempo, and what a 5 s hold snaps to on it: eight beats. */
const BPM = 120;
const SNAPPED_HOLD = 4.0;
/** The music fixture's length, so the music lane's lap count is arithmetic. */
const MUSIC_SEC = 12;
/** `MOVE_CYCLE_SEC` from lib/motion.ts — the drift's period at 1x. */
const MOVE_CYCLE = 12;

// --- fixtures (the PNG writer and the click track are beat.spec.ts's) --------

function png(w: number, h: number, pixel: (x: number, y: number) => [number, number, number]): Buffer {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  let o = 0;
  for (let y = 0; y < h; y++) {
    raw[o++] = 0;
    for (let x = 0; x < w; x++) {
      const [r, g, b] = pixel(x, y);
      raw[o++] = r; raw[o++] = g; raw[o++] = b;
    }
  }
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const body = Buffer.concat([Buffer.from(type, 'ascii'), data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(body) >>> 0);
    return Buffer.concat([len, body, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

let CRC_TABLE: number[] | null = null;
function crc32(buf: Buffer): number {
  if (!CRC_TABLE) {
    CRC_TABLE = [];
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      CRC_TABLE[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

/** A click track as 16-bit PCM WAV — the one container every browser decodes
 *  without an encoder in the test. First click at t=0, so the grid's phase is 0
 *  and the arithmetic below stays readable. */
function clickWav(bpm: number, seconds: number, rate = 22050): Buffer {
  const n = Math.round(seconds * rate);
  const pcm = Buffer.alloc(n * 2);
  const period = 60 / bpm;
  const burstLen = Math.round(0.035 * rate);
  const samples = new Float32Array(n);
  for (let t = 0; t < seconds; t += period) {
    const start = Math.round(t * rate);
    for (let i = 0; i < burstLen && start + i < n; i++) {
      samples[start + i] += Math.exp(-i / (0.007 * rate)) * Math.sin((2 * Math.PI * 1000 * i) / rate);
    }
  }
  for (let i = 0; i < n; i++) {
    const v = Math.max(-1, Math.min(1, samples[i] * 0.85));
    pcm.writeInt16LE(Math.round(v * 32767), i * 2);
  }
  const header = Buffer.alloc(44);
  header.write('RIFF', 0);
  header.writeUInt32LE(36 + pcm.length, 4);
  header.write('WAVE', 8);
  header.write('fmt ', 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(1, 22);
  header.writeUInt32LE(rate, 24);
  header.writeUInt32LE(rate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write('data', 36);
  header.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([header, pcm]);
}

const HUES: [number, number, number][] = [
  [235, 30, 30], [30, 220, 60], [40, 70, 240], [240, 215, 35],
];

const photos = () => HUES.map((rgb, i) => ({
  name: `hue-${i}.png`,
  mimeType: 'image/png',
  buffer: png(280, 280, (x, y) => {
    const t = 0.30 + 0.70 * ((x + y) / (279 * 2));
    return [Math.round(rgb[0] * t), Math.round(rgb[1] * t), Math.round(rgb[2] * t)] as [number, number, number];
  }),
}));

const music = () => [{ name: `click-${BPM}.wav`, mimeType: 'audio/wav', buffer: clickWav(BPM, MUSIC_SEC) }];

// --- page helpers ------------------------------------------------------------

const playhead = (page: Page) => page.getByLabel(/^Playhead/);
const strip = (page: Page) => page.getByTestId('take-strip');
const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');
const caption = (page: Page) => page.getByTestId('beat-caption');

const chip = async (page: Page, id: string) => {
  await page.getByTestId(id).click();
  await page.waitForTimeout(900);
};

const setTake = async (page: Page, sec: number) => {
  await page.getByRole('button', { name: `${sec}s`, exact: true }).click();
  await expect(playhead(page)).toBeVisible({ timeout: 60_000 });
};

/**
 * WHERE THE MARKS ACTUALLY ARE — S2's instrument.
 *
 * Each tick's own box against the row's own box, so the answer is a fraction of
 * the drawn ruler rather than of anything this test assumed about layout. A
 * percentage that never left the style attribute would prove only that React
 * wrote what the module returned.
 */
const markFractions = (page: Page): Promise<number[]> =>
  page.evaluate(() => {
    const row = document.querySelector('[data-testid="take-strip-cuts"]') as HTMLElement | null;
    if (!row) return [];
    const box = row.getBoundingClientRect();
    if (!(box.width > 0)) return [];
    return Array.from(row.querySelectorAll('[data-testid="take-strip-cut"]'))
      .map((el) => ((el as HTMLElement).getBoundingClientRect().x - box.x) / box.width)
      .sort((a, b) => a - b);
  });

/**
 * S2b's instrument — WHERE THE THUMB WOULD BE at a given instant, in page
 * pixels, and where the marks actually are.
 *
 * A range thumb is a pseudo-element and cannot be queried, so its centre is
 * computed the way the engine lays it out: `x + thumb/2 + f * (width - thumb)`.
 * The thumb width is READ FROM THE PAGE (`--range-thumb`), not assumed here —
 * that token is the single number the inset under the bar is derived from, so a
 * test that hard-coded 26 would pass against a build that had changed it.
 */
const axis = (page: Page, seconds: number, take: number) =>
  page.evaluate(({ seconds, take }) => {
    const bar = document.querySelector('input[type="range"][aria-label^="Playhead"]') as HTMLInputElement | null;
    const row = document.querySelector('[data-testid="take-strip-cuts"]') as HTMLElement | null;
    if (!bar || !row) return null;
    const thumb = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--range-thumb')) || 0;
    const b = bar.getBoundingClientRect();
    const f = take > 0 ? seconds / take : 0;
    return {
      thumb,
      thumbX: b.x + thumb / 2 + f * (b.width - thumb),
      marks: Array.from(row.querySelectorAll('[data-testid="take-strip-cut"]'))
        .map((el) => (el as HTMLElement).getBoundingClientRect().x)
        .sort((a, c) => a - c),
    };
  }, { seconds, take });

const lanes = (page: Page): Promise<{ kind: string; laps: number; dense: boolean }[]> =>
  page.evaluate(() => Array.from(document.querySelectorAll('[data-testid="take-strip-lane"]'))
    .map((el) => ({
      kind: (el as HTMLElement).dataset.kind || '',
      laps: Number((el as HTMLElement).dataset.laps || 0),
      dense: (el as HTMLElement).dataset.dense === '1',
    })));

const bootPhotos = async (page: Page) => {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(photos());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await page.waitForTimeout(1200);
};

// -----------------------------------------------------------------------------

test.describe('THE STRIP', () => {
  test.describe.configure({ mode: 'serial', timeout: 300_000 });

  test('S1/S2/S3 the marks are the cuts, and the music moves them', async ({ page }) => {
    await bootPhotos(page);

    // Music is what makes a photo collage live, and it is also lane #1.
    await musicInput(page).setInputFiles(music());
    await expect(caption(page), 'the app must decode the track and measure it')
      .toContainText(new RegExp(`${BPM} BPM`), { timeout: 60_000 });

    await chip(page, 'move-still');
    await chip(page, 'turn-march');
    await setTake(page, TAKE);

    // --- S1: the strip is there and counts what is in the take ---------------
    await expect(strip(page), 'the strip must be under the bar').toBeVisible({ timeout: 30_000 });
    const unsyncedCuts = Math.floor((TAKE - 0.0001) / MARCH_HOLD); // 5s, 10s
    await expect(strip(page)).toHaveAttribute('data-cuts', String(unsyncedCuts));

    const shown = await lanes(page);
    console.log(`[strip] lanes: ${JSON.stringify(shown)}`);
    expect(shown.length, 'photographs have no lane; the music does').toBe(1);
    expect(shown[0].kind).toBe('music');
    expect(shown[0].laps, `a ${MUSIC_SEC}s track laps ${Math.ceil(TAKE / MUSIC_SEC)}x inside a ${TAKE}s take`)
      .toBe(Math.ceil(TAKE / MUSIC_SEC));
    expect(shown[0].dense).toBe(false);

    // --- S2: measured in the DOM, not in the style attribute -----------------
    const drawn = await markFractions(page);
    const want = Array.from({ length: unsyncedCuts }, (_, i) => ((i + 1) * MARCH_HOLD) / TAKE);
    console.log(`[strip] unsynced marks: ${drawn.map((f) => f.toFixed(4)).join(', ')} `
      + `(want ${want.map((f) => f.toFixed(4)).join(', ')})`);
    expect(drawn.length).toBe(want.length);
    drawn.forEach((f, i) => {
      expect(Math.abs(f - want[i]),
        `mark ${i + 1} sits at ${(f * 100).toFixed(2)}% and the cut is at ${(want[i] * 100).toFixed(2)}%`)
        .toBeLessThan(0.01);
    });

    // --- S2b: THE MARK IS UNDER THE THUMB ------------------------------------
    // The whole claim of this feature is that the playhead crosses a mark when
    // the collage cuts. The bar and the strip are two elements, so that claim is
    // geometry and has to be measured as geometry: for every cut, where the
    // thumb's CENTRE lands at that instant against where the tick is drawn.
    // Before the inset this was out by half a thumb at the ends.
    const geo = await axis(page, MARCH_HOLD, TAKE);
    expect(geo, 'the bar and the strip must both be on the page').not.toBeNull();
    console.log(`[strip] thumb ${geo!.thumb}px — at ${MARCH_HOLD}s the thumb centre is `
      + `${geo!.thumbX.toFixed(1)} and the first mark is at ${geo!.marks[0].toFixed(1)}`);
    expect(Math.abs(geo!.thumbX - geo!.marks[0]),
      'the playhead at the cut must sit ON the mark, not beside it')
      .toBeLessThanOrEqual(2);

    // --- S3: THE BEAT, finally visible ---------------------------------------
    await chip(page, 'sync-beat');
    await expect(caption(page)).toContainText(/cutting every 2 bars/i);
    const syncedCuts = Math.floor((TAKE - 0.0001) / SNAPPED_HOLD); // 4s, 8s, 12s
    await expect(strip(page),
      `a 120 BPM snap holds ${SNAPPED_HOLD}s, so a ${TAKE}s take gains a mark`)
      .toHaveAttribute('data-cuts', String(syncedCuts));

    const onBeat = await markFractions(page);
    const wantBeat = Array.from({ length: syncedCuts }, (_, i) => ((i + 1) * SNAPPED_HOLD) / TAKE);
    console.log(`[strip] synced marks: ${onBeat.map((f) => f.toFixed(4)).join(', ')} `
      + `(want ${wantBeat.map((f) => f.toFixed(4)).join(', ')})`);
    expect(onBeat.length).toBe(wantBeat.length);
    onBeat.forEach((f, i) => {
      expect(Math.abs(f - wantBeat[i]),
        `synced mark ${i + 1} sits at ${(f * 100).toFixed(2)}%, the beat is at ${(wantBeat[i] * 100).toFixed(2)}%`)
        .toBeLessThan(0.015);
    });

    // AND THE TWO SETS ARE GENUINELY DIFFERENT — the assertion that would fail
    // if the strip were drawing the roster and ignoring the grid.
    expect(Math.abs(onBeat[0] - drawn[0]),
      'the first mark must MOVE when the music decides the schedule')
      .toBeGreaterThan(0.03);
  });

  test('S4 a lane counts its passes, and the speed moves them', async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.locator('input[type="file"]').first().setInputFiles([RAMP]);
    await expect(page.locator('canvas').first()).toBeVisible({ timeout: 120_000 });
    await setTake(page, TAKE);
    await expect(strip(page)).toBeVisible({ timeout: 30_000 });

    const natural = await lanes(page);
    console.log(`[strip] clip lane at 1x: ${JSON.stringify(natural)}`);
    expect(natural.length).toBe(1);
    expect(natural[0].kind).toBe('clip');
    expect(natural[0].laps, `a 6s clip laps ${Math.ceil(TAKE / 6)}x inside a ${TAKE}s take`)
      .toBe(Math.ceil(TAKE / 6));

    // THE SPEED, through the real sheet, exactly as a thumb would (speed.spec).
    await page.getByRole('button', { name: `Trim ${CLIP}` }).click();
    const double = page.getByTestId('speed-double');
    await expect(double).toBeVisible({ timeout: 15_000 });
    await double.click();
    await expect(double).toHaveAttribute('aria-pressed', 'true');
    await page.getByRole('button', { name: 'Close trim' }).click();
    await page.waitForTimeout(900);

    const sped = await lanes(page);
    console.log(`[strip] clip lane at 2x: ${JSON.stringify(sped)}`);
    expect(sped[0].laps, 'at 2x the same clip is 3s on screen and laps 5x')
      .toBe(Math.ceil(TAKE / 3));
  });

  test('S6 a mark is never drawn on a wall that cannot cut', async ({ page }) => {
    // THE DEFECT THIS PINS. Three places in this app answer "is the wall
    // turning". The Stage builds its ring from the fragments NOT holding a live
    // clip and switches the feature off below two of them; App's own `turning`
    // counts the POOL. Every frame extracted from a video carries a `clipId` and
    // binds to that clip, so a collage made of videos has an EMPTY ring and
    // never cuts — in the preview and in the exported file — while the chip row
    // says MARCH. The first version of this strip drew that intent: two ticks
    // under a wall that never re-deals. Found by an adversarial audit, because
    // no spec in this suite had ever put a clip and a turn mode in one scene.
    //
    // The assertion is made BOTH ways round: the strip must say zero, and the
    // PICTURE must prove there was nothing to say — the same instant, past the
    // would-be first cut and past its dissolve, is byte-comparable with the
    // turn off and with the turn on.
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.locator('input[type="file"]').first().setInputFiles([
      join(HERE, '..', 'fixtures', 'motion.webm'),
      join(HERE, '..', 'fixtures', 'motion_short.webm'),
    ]);
    await expect(page.locator('canvas').first()).toBeVisible({ timeout: 120_000 });
    await setTake(page, TAKE);
    await page.waitForTimeout(1500);

    // A moving crop would change pixels at every instant and make "it did not
    // cut" unmeasurable — the reason beat.spec.ts sets this too.
    await chip(page, 'move-still');

    const PAST_FIRST_CUT = MARCH_HOLD + 0.8;  // 5.8s: past the cut AND its 0.7s dissolve
    await page.locator('input[type="range"][aria-label^="Playhead"]').fill(String(PAST_FIRST_CUT));
    await page.waitForTimeout(1200);
    const held = await page.evaluate(() => {
      const cs = Array.from(document.querySelectorAll('canvas')) as HTMLCanvasElement[];
      let el: HTMLCanvasElement | null = null; let best = 0;
      for (const c of cs) { const a = c.width * c.height; if (a > best) { best = a; el = c; } }
      if (!el) return null;
      const s = document.createElement('canvas'); s.width = 96; s.height = 96;
      const cx = s.getContext('2d', { willReadFrequently: true });
      if (!cx) return null;
      cx.drawImage(el, 0, 0, 96, 96);
      return Array.from(cx.getImageData(0, 0, 96, 96).data);
    });
    expect(held).not.toBeNull();

    await chip(page, 'turn-march');
    await expect(strip(page)).toBeVisible({ timeout: 30_000 });
    await expect(strip(page),
      'a wall of clips has an empty turn ring, so there is no cut to mark')
      .toHaveAttribute('data-cuts', '0');
    await expect(page.getByTestId('take-strip-cut')).toHaveCount(0);

    await page.locator('input[type="range"][aria-label^="Playhead"]').fill(String(PAST_FIRST_CUT));
    await page.waitForTimeout(1200);
    const marched = await page.evaluate(() => {
      const cs = Array.from(document.querySelectorAll('canvas')) as HTMLCanvasElement[];
      let el: HTMLCanvasElement | null = null; let best = 0;
      for (const c of cs) { const a = c.width * c.height; if (a > best) { best = a; el = c; } }
      if (!el) return null;
      const s = document.createElement('canvas'); s.width = 96; s.height = 96;
      const cx = s.getContext('2d', { willReadFrequently: true });
      if (!cx) return null;
      cx.drawImage(el, 0, 0, 96, 96);
      return Array.from(cx.getImageData(0, 0, 96, 96).data);
    });
    expect(marched).not.toBeNull();

    let moved = 0; let worst = 0;
    for (let i = 0; i < held!.length; i += 4) {
      const d = Math.max(
        Math.abs(held![i] - marched![i]),
        Math.abs(held![i + 1] - marched![i + 1]),
        Math.abs(held![i + 2] - marched![i + 2]),
      );
      if (d > worst) worst = d;
      if (d > 6) moved++;
    }
    const share = moved / (held!.length / 4);
    console.log(`[strip] MARCH on a wall of clips at ${PAST_FIRST_CUT}s: `
      + `${(share * 100).toFixed(1)}% of the frame moved, worst ${worst}/255 — and the strip drew 0 marks`);
    expect(share,
      `the wall must NOT have cut (ring is empty) — worst channel ${worst}`)
      .toBeLessThan(0.02);
  });

  test('S7 a collage of photographs that moves finally has a strip', async ({ page }) => {
    await bootPhotos(page);

    // THE TURN IS WHAT KEEPS THE TRANSPORT MOUNTED for the control half.
    // `liveMode` is `clips.length > 0 || moving || turning || soundtrack`, so a
    // still photo collage with the turn on HOLD has no Stage at all — and a
    // strip that is absent because its whole surface unmounted would prove
    // nothing about DECISION 5. MARCH holds the surface open while the move,
    // and only the move, is the thing being switched.
    await chip(page, 'turn-march');
    await chip(page, 'move-still');
    await setTake(page, TAKE);

    // --- CONTROL: the strip is mounted and drawing, and there is NO drift row.
    await expect(strip(page)).toBeVisible({ timeout: 30_000 });
    const cuts = Math.floor((TAKE - 0.0001) / MARCH_HOLD);   // 5s, 10s
    await expect(strip(page)).toHaveAttribute('data-cuts', String(cuts));
    await expect(strip(page), 'a still collage has no drift row').toHaveAttribute('data-drift', '0');
    await expect(page.getByTestId('take-strip-drift'),
      'the row must be absent, not an empty trough').toHaveCount(0);

    // --- AFTER: one chip. The wall is now breathing as well as cutting.
    await chip(page, 'move-push');
    const laps = Math.ceil(TAKE / MOVE_CYCLE);               // 15 / 12 -> 2
    await expect(strip(page)).toHaveAttribute('data-drift', String(laps));
    await expect(strip(page), 'the drift must not disturb the cuts')
      .toHaveAttribute('data-cuts', String(cuts));
    await expect(strip(page), 'photographs are not sources: no lane').toHaveAttribute('data-lanes', '0');
    expect(await lanes(page), 'the drift must not have leaked into the source lanes').toHaveLength(0);

    // --- THE SEAM IS WHERE THE DRIFT COMES BACK TO REST, measured in the DOM
    //     the way S2 measures a cut: the second pass's own box against the
    //     row's, never the percentage that was written into the style.
    const seam = await page.evaluate(() => {
      const row = document.querySelector('[data-testid="take-strip-drift"]') as HTMLElement | null;
      if (!row) return null;
      const box = row.getBoundingClientRect();
      if (!(box.width > 0)) return null;
      const seg = Array.from(row.children)
        .map((el) => (el as HTMLElement).getBoundingClientRect())
        .sort((a, b) => a.x - b.x);
      return { n: seg.length, at: seg.map((r) => (r.x - box.x) / box.width) };
    });
    expect(seam, 'the drift row must be on the page').not.toBeNull();
    console.log(`[strip] drift row: ${seam!.n} passes, seams at `
      + seam!.at.map((f) => f.toFixed(4)).join(', ') + ` (expected 0, ${(MOVE_CYCLE / TAKE).toFixed(4)})`);
    expect(seam!.n, 'a 12s cycle in a 15s take is one whole pass and one short one').toBe(laps);
    expect(seam!.at[0]).toBeLessThan(0.005);
    expect(Math.abs(seam!.at[1] - MOVE_CYCLE / TAKE),
      'the seam is one drift cycle in, to within a pixel of a 300px row').toBeLessThan(0.01);

    // --- THE HEADLINE. Turn the cutting off: the take now contains the drift
    //     and NOTHING ELSE. Before DECISION 5 this exact state answered `empty`
    //     and drew no strip at all — a bare ruler over ten seconds the collage
    //     was busy for, on the commonest thing this app makes.
    await chip(page, 'turn-hold');
    await expect(strip(page), 'a drifting photo collage must still draw a strip')
      .toBeVisible({ timeout: 30_000 });
    await expect(strip(page)).toHaveAttribute('data-cuts', '0');
    await expect(strip(page)).toHaveAttribute('data-lanes', '0');
    await expect(strip(page), 'the drift is the only thing in this take')
      .toHaveAttribute('data-drift', String(laps));

    // --- AND THE PACE MOVES IT, which is the drift row's own version of S3:
    //     2x makes the cycle 6s, so the same take holds three passes.
    await chip(page, 'pace-rush');
    const rushed = Math.ceil(TAKE / (MOVE_CYCLE / 2));   // 15 / 6 -> 3
    await expect(strip(page), 'at 2x the collage breathes three times, not two')
      .toHaveAttribute('data-drift', String(rushed));
  });

  test('S5 the new rows are watertight on a phone', async ({ page }) => {
    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await bootPhotos(page);
      await musicInput(page).setInputFiles(music());
      await expect(caption(page)).toContainText(new RegExp(`${BPM} BPM`), { timeout: 60_000 });
      await chip(page, 'turn-march');
      // THE DRIFT ROW IS PART OF THE MOBILE LAW NOW. Three rows plus the gaps
      // is the densest this bar has ever been; a row added without this line
      // would be measured on a build that never drew it.
      await chip(page, 'move-push');
      await setTake(page, TAKE);
      await expect(strip(page)).toBeVisible({ timeout: 30_000 });
      await expect(strip(page)).toHaveAttribute('data-drift', String(Math.ceil(TAKE / MOVE_CYCLE)));

      const box = await page.evaluate(() => {
        const el = document.querySelector('[data-testid="take-strip"]') as HTMLElement | null;
        const r = el?.getBoundingClientRect();
        return {
          scrollW: document.documentElement.scrollWidth,
          clientW: document.documentElement.clientWidth,
          left: r ? r.x : 0,
          right: r ? r.x + r.width : 0,
          height: r ? r.height : 0,
        };
      });
      console.log(`[strip] ${width}px: scrollW ${box.scrollW} clientW ${box.clientW} `
        + `strip ${box.left.toFixed(1)}..${box.right.toFixed(1)} h=${box.height.toFixed(1)}`);
      expect(box.scrollW, `${width}px: zero horizontal overflow with the strip drawn`)
        .toBeLessThanOrEqual(box.clientW);
      expect(box.left, `${width}px: the strip must start on screen`).toBeGreaterThanOrEqual(-0.5);
      expect(box.right, `${width}px: the strip must not run off the right edge`)
        .toBeLessThanOrEqual(box.clientW + 0.5);
      // It must also be VISIBLE rather than collapsed: three rows at 6px plus
      // the gaps is 22px, and a strip that renders at zero height is not a
      // strip. The floor stays at 8 rather than tracking the row count — this
      // assertion is about collapse, and a tighter number would fail the day a
      // scene legitimately has fewer rows to draw.
      expect(box.height, `${width}px: the strip must have real height`).toBeGreaterThan(8);
    }
  });
});
