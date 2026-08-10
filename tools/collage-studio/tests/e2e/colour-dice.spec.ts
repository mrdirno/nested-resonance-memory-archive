/**
 * THE COLOUR DICE, AT THE ARTIFACT.
 *
 * Wished for (wishing well, collage/layout): *"Add another dice for color
 * sorting and cropping style. For full view for better ui/ux."*
 *
 * The roll itself is swept in tests/unit/dealRoll.invariants.mjs — 1.1M chained
 * rolls proving it never returns `natural`, never returns the deal already on
 * screen, and never spins. That grades ARITHMETIC and can see nothing at all
 * about whether the app is wired to it (scar, earned three times in this repo).
 *
 * So the claim here is the PROMISE the button makes, and it has two halves that
 * fail in opposite directions:
 *
 *   IT MUST CHANGE THE PICTURE — else it is a dead button.
 *   IT MUST NOT MOVE THE LAYOUT — else it is the first dice with a new icon,
 *   and the entire reason it exists (roll the colour sort WITHOUT losing the
 *   shape you just found) is gone.
 *
 * The witness for the second half is the composition CODE, read off the page:
 * a byte-level serialisation of every parameter of the picture that no browser
 * is free to perturb, and one that CANNOT agree with the wiring by construction
 * the way reading the controls back would. Its field layout is fixed and
 * asserted in tests/unit/rollCode.invariants.mjs:
 *
 *   HEAD(7) - MID(15) owned look move CHK(2) - SEED
 *   head = layout(2) count(3) entropy(2)
 *   mid  = aspect(1) gutter(2) zoom(2) bg(1) | arrangement(1) focus(1) twist(1) | primitive(1) rgb(5)
 *
 * Everything outside the three-character middle must come back identical, and
 * something inside it must not.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.colour-dice.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.colour-dice.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/**
 * A PNG built in-process — no fixture files, fully deterministic.
 *
 * NOT a flat colour. A flat tile cannot express a CROP: every part of it is the
 * same pixel, so `focus` moving from Centre to Thirds repaints nothing and the
 * "it reached the pixels" assertion below fails against a button that is
 * working perfectly (this spec's second run, on two engines). So each tile is a
 * field of its own hue with a near-white block in ONE quadrant — enough
 * internal structure that where the fragment is centred is visible, while the
 * hue that every arrangement metric ranks on stays dominant.
 */
function makePng(r: number, g: number, b: number, quadrant = 0, size = 96): Buffer {
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
  const qx = (quadrant % 2) * (w / 2), qy = Math.floor(quadrant / 2) * (h / 2);
  const raw = Buffer.concat(Array.from({ length: h }, (_, y) => {
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) {
      const inBlock = x >= qx + 6 && x < qx + w / 2 - 6 && y >= qy + 6 && y < qy + h / 2 - 6;
      row[1 + x * 3] = inBlock ? 250 : r;
      row[1 + x * 3 + 1] = inBlock ? 250 : g;
      row[1 + x * 3 + 2] = inBlock ? 250 : b;
    }
    return row;
  }));
  const idat = zlib.deflateSync(raw);
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

/**
 * Eight sources spread right around the hue circle, and at three luminances.
 *
 * NOT arbitrary: every arrangement in the roster ranks photos by a COLOUR
 * metric (hue, luma, chroma, warmth, punch), so a pool that is all one hue or
 * all one brightness would re-sort into visually the same picture and this
 * spec's "the picture changed" half would fail for a reason that is the
 * fixture's fault rather than the app's.
 */
const TILES = [
  [235, 40, 40], [240, 150, 30], [235, 225, 60], [60, 210, 80],
  [40, 190, 200], [55, 90, 240], [160, 60, 230], [230, 60, 170],
].map(([r, g, b], i) => ({
  name: `tile-${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b, i % 4),
}));

/**
 * A 16x16 block signature of whatever preview is mounted.
 *
 * Lifted from undo.spec.ts, which measured why an exact pixel hash is NOT
 * admissible here: a composition carrying a MOVE mounts the live Stage canvas,
 * and a drifting canvas renders different pixels every frame. The block
 * signature was validated for both stability under that drift and for
 * discrimination before it was adopted there.
 */
async function fingerprint(page: Page): Promise<{ sig: string; w: number; h: number }> {
  return page.evaluate(() => {
    const liveEl = document.querySelector('canvas') as HTMLCanvasElement | null;
    const el = liveEl ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!el) return { sig: '', w: 0, h: 0 };
    const sw = el instanceof HTMLCanvasElement ? el.width : el.naturalWidth;
    const sh = el instanceof HTMLCanvasElement ? el.height : el.naturalHeight;
    if (!sw || !sh) return { sig: '', w: 0, h: 0 };
    const S = 128;
    const c = document.createElement('canvas');
    c.width = S; c.height = S;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    if (!ctx) return { sig: '', w: sw, h: sh };
    ctx.drawImage(el as CanvasImageSource, 0, 0, S, S);
    const px = ctx.getImageData(0, 0, S, S).data;
    const N = 16, B = S / N;
    let sig = '';
    for (let by = 0; by < N; by++) {
      for (let bx = 0; bx < N; bx++) {
        let R = 0, G = 0, Bl = 0, n = 0;
        for (let y = by * B; y < (by + 1) * B; y++) {
          for (let x = bx * B; x < (bx + 1) * B; x++) {
            const i = (y * S + x) * 4;
            R += px[i]; G += px[i + 1]; Bl += px[i + 2]; n++;
          }
        }
        R /= n; G /= n; Bl /= n;
        const mx = Math.max(R, G, Bl), mn = Math.min(R, G, Bl);
        sig += (mx - mn) > 36
          ? (mx === R ? 'R' : mx === G ? 'G' : 'B')
          : '0123'[Math.min(3, Math.floor(((R + G + Bl) / 3) / 64))];
      }
    }
    return { sig, w: sw, h: sh };
  });
}

/** Sample until two consecutive reads 200ms apart agree — never a hoped-for timeout. */
async function settled(page: Page, timeoutMs = 20_000) {
  const started = Date.now();
  await page.waitForTimeout(200);
  let prev = await fingerprint(page);
  let stable = 0;
  while (Date.now() - started < timeoutMs) {
    await page.waitForTimeout(200);
    const next = await fingerprint(page);
    const agrees = !!next.sig && next.sig === prev.sig && next.w === prev.w;
    prev = next;
    if (agrees && ++stable >= 2) return next;
    if (!agrees) stable = 0;
  }
  return prev;
}

const codeOf = (page: Page) => page.getByTestId('composition-code').innerText();

/**
 * Split a composition code into the two claims this spec cares about.
 * `kept` is everything the colour dice promised not to touch; `deal` is the
 * three characters it owns.
 *
 * THE LAST TWO CHARACTERS ARE THE CHECKSUM, and they are deliberately NOT in
 * `kept`. The checksum is a function of every field including the three the
 * button legitimately changes, so demanding it come back identical would be
 * demanding the button do nothing — the assertion would pass only on a dead
 * control. (This spec's first run failed exactly there, and the failure looked
 * like a product bug: "the colour dice moved something it does not own", with
 * the diff sitting entirely inside the checksum.)
 */
function parts(code: string) {
  const [head, mid, seed] = code.trim().split('-');
  return {
    head,
    seed,
    kept: `${head}|${mid.slice(0, 6)}|${mid.slice(9, -2)}|${seed}`,
    deal: mid.slice(6, 9),
    raw: code.trim(),
  };
}

async function boot(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(TILES);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  const first = await settled(page);
  // Calibrate the ruler before using it: a signature that moves on an untouched
  // preview would make every assertion below meaningless.
  const again = await fingerprint(page);
  expect(first.sig, 'the block signature is unstable on an untouched preview — the witness is broken')
    .toBe(again.sig);
  return first;
}

test.describe('the colour dice', () => {
  test('rolls the sort and the crop, and moves nothing else', async ({ page }) => {
    await boot(page);

    // Roll a real composition first. Starting from the app's default would let
    // the assertion pass against a layout nobody chose — and `natural/auto/none`
    // is the one starting deal where ANY draw differs, which is the easy case.
    await page.getByTestId('dock-dice').click();
    await settled(page);

    const before = parts(await codeOf(page));
    const beforeShot = await settled(page);

    // FIVE presses, not one. The roll draws from 10 x 5 x 5, so a single press
    // is a weak test of "always different" — and the chained case (each result
    // fed back as the next `previous`) is the one the field actually performs
    // and the one where a collision can happen at all.
    let prev = before;
    let prevShot = beforeShot;
    let repaints = 0;
    for (let i = 1; i <= 5; i++) {
      await page.getByTestId('dock-colour-dice').click();
      const shot = await settled(page);
      const now = parts(await codeOf(page));
      const repainted = shot.sig !== prevShot.sig;
      if (repainted) repaints++;

      // THE LAYOUT DID NOT MOVE — every field outside the three the button owns.
      expect(now.kept, `press ${i}: the colour dice moved something it does not own\n  before ${prev.raw}\n  after  ${now.raw}`)
        .toBe(prev.kept);
      // THE DEAL DID — at least one of arrangement / focus / twist.
      expect(now.deal, `press ${i}: the colour dice returned the deal already on screen (${now.raw})`)
        .not.toBe(prev.deal);
      // NEVER THE UNSORTED ORDER — `natural` is index 0 of the arrangement roster.
      expect(now.deal[0], `press ${i}: the colour dice returned \`natural\`, which is not a colour sort`)
        .not.toBe('0');
      // AND IT REACHED THE PIXELS — asserted per-press ON THE COLOUR SORT,
      // which is the headline of the wish and is always visible across sources
      // this distinctly coloured. A parameter change that never repaints is a
      // dead button that would otherwise pass every code assertion above.
      if (now.deal[0] !== prev.deal[0]) {
        expect(repainted,
          `press ${i}: the arrangement changed (${prev.deal[0]} -> ${now.deal[0]}) and the picture did not repaint`)
          .toBe(true);
      }

      prev = now;
      prevShot = shot;
    }

    // A CROP-ONLY ROLL IS ALLOWED TO BE INVISIBLE, and pretending otherwise is
    // how a test starts lying: `auto` falls back to the busiest region on a
    // photograph with no face in it, which is exactly what `energy` already is,
    // so that one pair genuinely paints the same picture. What is NOT allowed
    // is a button that mostly does nothing.
    expect(repaints, `only ${repaints} of 5 presses changed the picture`).toBeGreaterThanOrEqual(3);
  });

  test('is under your thumb in full bleed, where it was wished for', async ({ page }) => {
    await boot(page);
    await page.getByTestId('dock-dice').click();
    await settled(page);
    const before = parts(await codeOf(page));

    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    const rail = page.getByTestId('rail-colour-dice');
    await expect(rail).toBeVisible();

    // 44px is a law, in both rows of a wrapped rail.
    const box = await rail.boundingBox();
    expect(box!.width, 'the rail colour dice is under the 44px tap target').toBeGreaterThanOrEqual(43.5);
    expect(box!.height, 'the rail colour dice is under the 44px tap target').toBeGreaterThanOrEqual(43.5);

    const railBefore = await settled(page);
    await rail.click();
    const railAfter = await settled(page);
    expect(railAfter.sig, 'the rail colour dice did not change the picture').not.toBe(railBefore.sig);

    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    const after = parts(await codeOf(page));
    expect(after.kept, 'the rail colour dice moved something it does not own').toBe(before.kept);
    expect(after.deal, 'the rail colour dice changed nothing').not.toBe(before.deal);
  });

  test('the full-bleed rail is watertight at every phone width', async ({ page }) => {
    await boot(page);
    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await expect(page.getByTestId('rail-colour-dice')).toBeVisible();

    // The seventh button is what made this necessary: six were already 295 of
    // the 304 pixels a 320px phone has.
    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 720 });
      await page.waitForTimeout(250);

      const overflow = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollW, `${w}px: the page scrolls sideways (${overflow.scrollW} > ${overflow.clientW})`)
        .toBeLessThanOrEqual(overflow.clientW);

      // Every control in the rail: inside the viewport, and still 44px.
      const ids = ['rail-dice', 'rail-colour-dice', 'undo', 'redo'];
      for (const id of ids) {
        const b = await page.getByTestId(id).boundingBox();
        expect(b, `${w}px: ${id} is not laid out`).not.toBeNull();
        expect(b!.width, `${w}px: ${id} is under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
        expect(b!.height, `${w}px: ${id} is under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
        expect(b!.x, `${w}px: ${id} starts off the left edge`).toBeGreaterThanOrEqual(-0.5);
        expect(b!.x + b!.width, `${w}px: ${id} runs off the right edge`).toBeLessThanOrEqual(w + 0.5);
      }

      // Exit is the ONLY way out on a touch device — never allowed to be the
      // control that fell off the edge.
      const exit = await page.getByRole('button', { name: 'Exit full bleed' }).boundingBox();
      expect(exit!.x + exit!.width, `${w}px: Exit runs off the right edge`).toBeLessThanOrEqual(w + 0.5);
      expect(exit!.height, `${w}px: Exit is under the 44px tap target`).toBeGreaterThanOrEqual(43.5);
    }
  });
});
