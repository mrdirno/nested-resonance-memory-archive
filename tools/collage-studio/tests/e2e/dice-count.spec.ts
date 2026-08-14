/**
 * THE DICE MUST SEE HOW MANY PHOTOS YOU ACTUALLY SENT.
 *
 * WISHED FOR (wishing well, kind=bug): *"You should make randomize the same
 * count as the images uploaded — why everytime I hit random it does over 100 it
 * should be within range of the number of images sent."*
 *
 * WHAT WAS BROKEN
 *   On import the app snaps the fragment count to the number of distinct sources
 *   (source-count.spec.ts is that proof). Then one press of the dice threw it
 *   away: `rollDice` was never told how big the pool was, so it sampled out of a
 *   recipe's absolute range — Cathedral [90,220], Sunflower [80,260] — and
 *   twelve photographs became two hundred fragments, every one of them a repeat.
 *   And it LATCHED: `countOwned` went true, so every later press did it again.
 *
 * WHY THIS IS AN E2E AND NOT ONLY A UNIT SWEEP
 *   `tests/unit/diceRollCount.invariants.mjs` sweeps the pure sampler across
 *   every pool size x every recipe x thousands of seeds — it is the thorough
 *   oracle. It is also structurally blind to the defect that actually shipped,
 *   which was WIRING: the pool was never passed in. Only a real press of the
 *   real button against a real upload can see that, which is this file.
 *
 * Run against the running collage dev server (:5199, never :5173):
 *   npx playwright test --config playwright.dice-count.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.dice-count.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/**
 * The contract, written here as literals ON PURPOSE.
 *
 * Importing them from `diceRoll.ts` would make this gate agree with whatever the
 * constant happens to be, which is a gate that can never fail. These are the
 * numbers the wish was answered with; changing them has to break this file.
 */
const MAX_REPEATS = 3;   // no source appears more than three times...
const MIN_FIGURE = 24;   // ...unless three copies could not make a figure at all

const ceilingFor = (n: number) => Math.max(n * MAX_REPEATS, MIN_FIGURE);

// A valid solid-colour PNG built in-process — any number of DISTINCT photos with
// no fixture files. Distinct colours because the app colour-analyses every image.
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
  ihdr[8] = 8; ihdr[9] = 2; // 8-bit truecolour RGB
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) { row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b; }
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const idat = zlib.deflateSync(raw);
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h /= 360;
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const hk = (t: number) => {
    if (t < 0) t += 1; if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  return [Math.round(hk(h + 1 / 3) * 255), Math.round(hk(h) * 255), Math.round(hk(h - 1 / 3) * 255)];
}

const distinctPhotos = (n: number, tag = 'a') =>
  Array.from({ length: n }, (_, i) => {
    const [r, g, b] = hslToRgb((i / Math.max(1, n)) * 360, 0.7, 0.5);
    return { name: `photo_${tag}_${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b) };
  });

const upload = (page: Page, files: { name: string; mimeType: string; buffer: Buffer }[]) =>
  page.locator('input[type="file"]').first().setInputFiles(files);

/** The integer shown as "<n> FRAGMENTS" — the number the user is complaining about. */
const fragments = (page: Page) =>
  page.evaluate(() => {
    const el = document.querySelector('.ui-readout');
    const m = el?.textContent?.match(/(\d+)\s*FRAGMENTS/i);
    return m ? parseInt(m[1], 10) : null;
  });

/** Press the dice and wait for the readout to settle. Returns the new count. */
async function roll(page: Page): Promise<number> {
  await page.getByTestId('dock-dice').click();
  // The count is applied synchronously with the press; the poll is for React's
  // commit, not for a layout worker.
  await page.waitForTimeout(120);
  const n = await fragments(page);
  expect(n, 'the fragment readout disappeared after a roll').not.toBeNull();
  return n as number;
}

/** Roll `presses` times over a pool of `pool` photos and return every count seen. */
async function rollSeries(page: Page, pool: number, presses: number): Promise<number[]> {
  await upload(page, distinctPhotos(pool));
  await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(pool);
  const seen: number[] = [];
  for (let i = 0; i < presses; i++) seen.push(await roll(page));
  return seen;
}

test.describe('the dice honours the pool', () => {
  test.beforeEach(async ({ page }) => { await page.goto(APP_URL); });

  test('D1: twelve photos — every roll lands at or under 36, the wish verbatim', async ({ page }) => {
    const POOL = 12, PRESSES = 14;
    const seen = await rollSeries(page, POOL, PRESSES);
    const hi = ceilingFor(POOL);
    expect(seen.filter((c) => c > hi), `rolls exceeded ${hi} fragments from ${POOL} photos: ${seen.join(', ')}`)
      .toEqual([]);
    // ...and it is still a dice: pressing it fourteen times must not hand back
    // one number over and over, or the fix has traded a bug for a dead button.
    expect(new Set(seen).size, `the dice returned the same count every press: ${seen.join(', ')}`)
      .toBeGreaterThan(1);
  });

  test('D2: three photos — the small-pool floor, not three fragments and not two hundred', async ({ page }) => {
    const POOL = 3, PRESSES = 10;
    const seen = await rollSeries(page, POOL, PRESSES);
    const hi = ceilingFor(POOL); // 24 — three copies of three photos is not a figure
    expect(seen.filter((c) => c > hi), `over ${hi} from ${POOL} photos: ${seen.join(', ')}`).toEqual([]);
  });

  test('D3: forty photos — a big pool is NOT clamped down to a small figure', async ({ page }) => {
    const POOL = 40, PRESSES = 8;
    const seen = await rollSeries(page, POOL, PRESSES);
    const hi = ceilingFor(POOL); // 120
    expect(seen.filter((c) => c > hi), `over ${hi} from ${POOL} photos: ${seen.join(', ')}`).toEqual([]);
    // The ceiling must not have become a pin: a 40-photo pool has real room under
    // it, and eight presses that all land on the same number is a dead button.
    expect(new Set(seen).size, `the range collapsed at a big pool: ${seen.join(', ')}`).toBeGreaterThan(1);
    expect(Math.max(...seen), `every roll came back tiny — the ceiling became a floor: ${seen.join(', ')}`)
      .toBeGreaterThan(POOL);
  });

  test('D4: the ceiling is a DEFAULT, not a cage — the stepper still goes past it', async ({ page }) => {
    await upload(page, distinctPhotos(4));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(4);
    await roll(page);
    const more = page.getByRole('button', { name: 'More fragments' });
    const before = (await fragments(page)) as number;
    for (let i = 0; i < 30; i++) await more.click();
    const after = (await fragments(page)) as number;
    expect(after, 'the stepper could not push the count past the rolled value').toBeGreaterThan(before);
    expect(after, 'the stepper was capped by the roll ceiling — it must not be')
      .toBeGreaterThan(ceilingFor(4));
  });

  test('D6: DENSITY is inside the ceiling — the number on screen is count x density', async ({ page }) => {
    // The panel's catch: the readout prints `count * density`, the chips go to
    // 4x, and the dice deliberately does not roll density. A ceiling written on
    // `count` alone lets twelve photographs become 144 fragments WITH the fix in,
    // which is the wisher's literal complaint reproducing through its own fix.
    const POOL = 12;
    await upload(page, distinctPhotos(POOL));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(POOL);
    await page.getByTitle(/^4×/).click();
    await expect.poll(() => fragments(page), { timeout: 10_000 }).toBe(POOL * 4);
    const seen: number[] = [];
    for (let i = 0; i < 8; i++) seen.push(await roll(page));
    expect(seen.filter((c) => c > ceilingFor(POOL)),
      `at density 4x the screen went over ${ceilingFor(POOL)} fragments: ${seen.join(', ')}`).toEqual([]);
  });

  test('D5: photos added AFTER a roll are never stranded', async ({ page }) => {
    await upload(page, distinctPhotos(5, 'a'));
    await expect.poll(() => fragments(page), { timeout: 30_000 }).toBe(5);
    await roll(page);
    await upload(page, distinctPhotos(60, 'b')); // pool 65 — way past the rolled count
    await expect.poll(() => fragments(page), { timeout: 60_000 }).toBeGreaterThanOrEqual(65);
  });
});
