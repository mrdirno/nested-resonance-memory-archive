/**
 * THE BEAT AT THE ARTIFACT — proved on PIXELS, against a track whose tempo the
 * test itself chose, with NO CLOCK.
 *
 * The arithmetic is swept in tests/unit/beat.invariants.mjs (17 invariants,
 * including a red proof that a constant dissolve smears a snapped hold, twelve
 * tempi detected exactly, and white noise refused). Four things can only be
 * proved out here.
 *
 *   B1  THE TRACK IS ACTUALLY LISTENED TO. A sweep can prove `detectBeat` finds
 *       120 BPM in an array; only a browser can prove the app decodes the file
 *       somebody picked, runs it, and says so on the chip.
 *
 *   B2  THE GRID REACHES THE COMPOSITOR, AND IT MOVES THE CUT. `march` holds
 *       5.0 s. Snapped to a 120 BPM grid it holds EIGHT BEATS — 4.0 s — so at
 *       t=4.8 s the synced wall has cut and settled while the unsynced one is
 *       still showing the deal it opened on. Same pictures, same mode, same
 *       take: the only difference is the music.
 *
 *   B3  THE PERMUTATION SURVIVES IT. Six photographs, six hues, one each. A
 *       schedule is a change to WHEN the deal is read, so the app's oldest
 *       promise — every source once, never twice — has to hold on it.
 *
 *   B4  IT IS WATERTIGHT ON A PHONE. One more chip row at 320 px.
 *
 * WHY THE MEASUREMENT IS A SCRUB AND NOT A WAIT — the reason pace.spec.ts gives
 * at length: `renderAtTime` is a PURE function of the instant (which is why the
 * offline exporter can walk it), so parking on 4.8 s asks the composition a
 * question with one right answer, and a green run here is evidence about the
 * exported file rather than only about the preview.
 *
 * WHY THE MOVE IS SET TO STILL: adding music turns the drift on by design
 * ("music means the piece moves"), and a drifting crop changes pixels at every
 * instant — which would make "the wall has not cut" unmeasurable. Turning it
 * off leaves the cut as the only thing that can move a pixel.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test tests/e2e/beat.spec.ts --project=chromium
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test tests/e2e/beat.spec.ts --project=chromium
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** The tempo the fixture is built at. 120 BPM = a 0.5 s beat. */
const BPM = 120;
/** `march`'s hold, from lib/turn.ts. */
const MARCH_HOLD = 5.0;
/** What the snap must choose: the multiple of 0.5 s nearest 5 s in ratio. */
const SNAPPED_HOLD = 4.0;
/** The take the ruler must be long enough to reach 4.8 s on. */
const TAKE = 10;

// --- fixtures ----------------------------------------------------------------

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

/**
 * A CLICK TRACK AS A 16-BIT PCM WAV, built here rather than committed.
 *
 * WAV because it is the one container every browser decodes without an encoder
 * in the test, and because the point is the TEMPO, which survives being carried
 * uncompressed. The first click is at t=0, so the grid's phase is 0 and the
 * arithmetic the assertions do stays readable: a cut at 4.0 s IS the eighth
 * beat.
 */
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
  header.writeUInt16LE(1, 20);        // PCM
  header.writeUInt16LE(1, 22);        // mono
  header.writeUInt32LE(rate, 24);
  header.writeUInt32LE(rate * 2, 28); // byte rate
  header.writeUInt16LE(2, 32);        // block align
  header.writeUInt16LE(16, 34);       // bits
  header.write('data', 36);
  header.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([header, pcm]);
}

const HUES: [number, number, number][] = [
  [235, 30, 30], [30, 220, 60], [40, 70, 240],
  [240, 215, 35], [225, 45, 225], [35, 215, 225],
];

const fixtures = () => HUES.map((rgb, i) => ({
  name: `hue-${i}.png`,
  mimeType: 'image/png',
  buffer: png(320, 320, (x, y) => {
    const t = 0.30 + 0.70 * ((x + y) / (319 * 2));
    const edge = (x > 150 && x < 172) || (y > 96 && y < 118) ? 0.45 : 1;
    const k = t * edge;
    return [Math.round(rgb[0] * k), Math.round(rgb[1] * k), Math.round(rgb[2] * k)] as [number, number, number];
  }),
}));

const music = () => [{ name: `click-${BPM}.wav`, mimeType: 'audio/wav', buffer: clickWav(BPM, 12) }];

// --- page helpers ------------------------------------------------------------

async function boot(page: Page) {
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(fixtures());
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // Tabs are labelled Layout / Settings — NOT Simple / Advanced (scar).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.getByRole('button', { name: 'Layout' }).first().click();
  await page.waitForTimeout(1600);
}

const musicInput = (page: Page) => page.locator('input[type="file"][accept*="audio"]');
const caption = (page: Page) => page.getByTestId('beat-caption');

const chip = async (page: Page, id: string) => {
  await page.getByTestId(id).click();
  // A chip change rebuilds the scene: the Stage re-binds every fragment and
  // re-establishes the assignment at the current park.
  await page.waitForTimeout(1400);
};

const playhead = (page: Page) => page.getByLabel(/^Playhead/);

/** Park the whole composition on an instant. The STRING form matters (scar). */
const scrubTo = async (page: Page, t: number) => {
  await playhead(page).fill(String(t));
  await page.waitForTimeout(800);
};

/** The artwork, downsampled to N x N as raw RGBA — the LARGEST canvas. */
const artBits = (page: Page, N = 150): Promise<number[] | null> =>
  page.evaluate((N) => {
    const canvases = Array.from(document.querySelectorAll('canvas')) as HTMLCanvasElement[];
    let el: CanvasImageSource | null = null;
    let best = 0;
    for (const c of canvases) {
      const a = c.width * c.height;
      if (a > best) { best = a; el = c; }
    }
    if (!el) el = document.querySelector('img[src^="blob:"]') as HTMLImageElement | null;
    if (!el) return null;
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', { willReadFrequently: true });
    if (!cx) return null;
    cx.drawImage(el, 0, 0, N, N);
    return Array.from(cx.getImageData(0, 0, N, N).data);
  }, N);

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

/** How many of the six prototype hues are on the wall. A permutation keeps all
 *  six; a duplicate makes one VANISH, which is what this counts. */
function hueCensus(bits: number[]): number {
  const seen = new Set<number>();
  for (let i = 0; i < bits.length; i += 4) {
    const r = bits[i]; const g = bits[i + 1]; const b = bits[i + 2];
    const mag = Math.hypot(r, g, b);
    if (mag < 40) continue;
    let best = -1; let bestDot = 0;
    for (let h = 0; h < HUES.length; h++) {
      const [hr, hg, hb] = HUES[h];
      const hm = Math.hypot(hr, hg, hb);
      const dot = (r * hr + g * hg + b * hb) / (mag * hm);
      if (dot > bestDot) { bestDot = dot; best = h; }
    }
    if (best >= 0 && bestDot > 0.985) seen.add(best);
  }
  return seen.size;
}

// -----------------------------------------------------------------------------

test.describe('THE BEAT', () => {
  test.describe.configure({ mode: 'serial', timeout: 300_000 });

  test('B1/B2/B3 the music moves the cut, and the deal is still a permutation', async ({ page }) => {
    await boot(page);

    // WITHOUT MUSIC the row is still here and says what it needs — the house
    // rule (scar C126) is that a control explains itself rather than dying.
    await expect(caption(page)).toContainText(/Add a track/i);

    await musicInput(page).setInputFiles(music());

    // B1 — the app decoded the file and measured it.
    await expect(caption(page), 'the chip must report the tempo it actually found')
      .toContainText(new RegExp(`${BPM} BPM`), { timeout: 60_000 });
    console.log(`[beat] caption after import: ${await caption(page).textContent()}`);

    // Adding music turns the DRIFT on by design; a drifting crop moves pixels at
    // every instant and would make "has not cut" unmeasurable.
    await chip(page, 'move-still');
    await chip(page, 'turn-march');
    await page.getByRole('button', { name: `${TAKE}s`, exact: true }).click();
    await expect(playhead(page)).toBeVisible({ timeout: 60_000 });

    // THE CONTROL: unsynced, `march` holds 5 s, so 4.8 s is still inside its
    // opening hold and the wall must be showing the deal it opened on.
    await scrubTo(page, 0);
    const rest = await artBits(page);
    await scrubTo(page, 4.8);
    const off48 = await artBits(page);
    expect(rest).not.toBeNull();
    expect(off48).not.toBeNull();
    const held = diff(rest!, off48!);
    expect(held.moved,
      `OFF must NOT have cut by 4.8s (march holds ${MARCH_HOLD}s) — worst ${held.worst}`)
      .toBeLessThan(0.02);

    // B2 — ON THE BEAT. Eight beats of a 120 BPM track is 4.0 s, so by 4.8 s the
    // cut has happened AND its 0.7 s dissolve is over.
    await chip(page, 'sync-beat');
    await expect(caption(page), 'the caption must say what it snapped to')
      .toContainText(/cutting every 2 bars/i);
    await scrubTo(page, 4.8);
    const on48 = await artBits(page);
    expect(on48).not.toBeNull();
    const cut = diff(off48!, on48!);
    console.log(`[beat] ON @4.8s vs OFF @4.8s: ${(cut.moved * 100).toFixed(1)}% of the frame moved,`
      + ` worst channel ${cut.worst}/255 (snapped hold ${SNAPPED_HOLD}s vs the roster's ${MARCH_HOLD}s)`);
    expect(cut.moved, `the synced wall must have cut by 4.8s — worst ${cut.worst}`).toBeGreaterThan(0.60);
    expect(cut.worst, 'and must change fragments outright, not merely soften them').toBeGreaterThan(60);

    // B3 — every photograph exactly once, on the synced schedule. Printed at
    // every instant measured, because "the census dropped" and "the wall is
    // mid-dissolve" look the same from one number.
    console.log(`[beat] hue census — rest ${hueCensus(rest!)}, OFF@4.8 ${hueCensus(off48!)}, ON@4.8 ${hueCensus(on48!)}`);
    expect(hueCensus(on48!), 'every source once, never twice, on the beat').toBe(6);

    // AND IT IS NOT SIMPLY CUTTING CONSTANTLY: before the first snapped cut the
    // synced wall is on the same opening deal the unsynced one is.
    await scrubTo(page, 3.0);
    const on30 = await artBits(page);
    expect(on30).not.toBeNull();
    const stillHeld = diff(rest!, on30!);
    console.log(`[beat] ON @3.0s vs rest: ${(stillHeld.moved * 100).toFixed(1)}% moved, worst ${stillHeld.worst}/255`);
    expect(stillHeld.moved,
      `the synced wall must still be holding at 3.0s (first cut at ${SNAPPED_HOLD}s) — worst ${stillHeld.worst}`)
      .toBeLessThan(0.02);
  });

  test('B4 the new row is watertight on a phone', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 720 });
    await boot(page);
    await musicInput(page).setInputFiles(music());
    await expect(caption(page)).toContainText(new RegExp(`${BPM} BPM`), { timeout: 60_000 });

    const overflow = await page.evaluate(() => ({
      scrollW: document.documentElement.scrollWidth,
      clientW: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollW,
      `zero horizontal overflow at 320px (scrollWidth ${overflow.scrollW} vs clientWidth ${overflow.clientW})`)
      .toBeLessThanOrEqual(overflow.clientW);

    for (const id of ['sync-off', 'sync-beat']) {
      const box = await page.getByTestId(id).boundingBox();
      expect(box, `${id} must be on screen`).not.toBeNull();
      expect(box!.height, `${id} must clear 44px`).toBeGreaterThanOrEqual(44);
      expect(box!.x + box!.width, `${id} must not run off the right edge`).toBeLessThanOrEqual(320);
    }
    console.log('[beat] 320px: no horizontal overflow, both chips >= 44px and inside the viewport');
  });
});
