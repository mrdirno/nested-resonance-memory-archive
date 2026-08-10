/**
 * THE COMPOSITION CODE, AT THE ARTIFACT — proved on PIXELS.
 *
 * The pure round trip is swept in tests/unit/rollCode.invariants.mjs across
 * 198k assertions. This proves the thing a unit test cannot reach: that the code
 * shown on the real page, pasted back into the real page, puts the SAME PICTURE
 * on the canvas — and that a link carrying it opens that picture on a cold load.
 *
 * WHY THE ASSERTION IS A PIXEL HASH AND NOT "THE CONTROLS MATCH"
 *   Every field could round-trip through the codec perfectly and the picture
 *   still not come back — a setter left out of `applyCompositionCode`, a locked
 *   fragment surviving the change, the shuffle counter left running. Reading the
 *   controls back would agree with the wiring by construction. The canvas is the
 *   only witness that does not.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.roll-code.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.roll-code.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** A solid-colour PNG built in-process — no fixture files, fully deterministic. */
function makePng(r: number, g: number, b: number, size = 96): Buffer {
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

/** Six distinct, distinctly-coloured sources. Distinct so the DEAL is visible. */
const TILES = [
  [230, 40, 40], [40, 200, 90], [50, 90, 240],
  [240, 200, 40], [200, 60, 220], [30, 220, 220],
].map(([r, g, b], i) => ({
  name: `tile-${i}.png`, mimeType: 'image/png', buffer: makePng(r, g, b),
}));

/**
 * A fingerprint of what is actually on the canvas: the natural size of the
 * preview (so a frame-shape change cannot hide behind a stretch) and a hash of
 * its pixels sampled on a fixed grid.
 */
async function fingerprint(page: Page): Promise<{ w: number; h: number; hash: string; mean: number; sig: string; live: boolean }> {
  return page.evaluate(() => {
    const liveEl = document.querySelector('canvas') as HTMLCanvasElement | null;
    const el = liveEl ?? (document.querySelector('img[src^="blob:"]') as HTMLImageElement | null);
    if (!el) return { w: 0, h: 0, hash: 'no-preview', mean: -1, sig: '', live: false };
    const sw = el instanceof HTMLCanvasElement ? el.width : el.naturalWidth;
    const sh = el instanceof HTMLCanvasElement ? el.height : el.naturalHeight;
    if (!sw || !sh) return { w: 0, h: 0, hash: 'empty-preview', mean: -1, sig: '', live: false };
    const c = document.createElement('canvas');
    c.width = 128; c.height = 128;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    if (!ctx) return { w: sw, h: sh, hash: 'no-2d', mean: -1, sig: '', live: !!liveEl };
    ctx.drawImage(el as CanvasImageSource, 0, 0, c.width, c.height);
    const px = ctx.getImageData(0, 0, c.width, c.height).data;
    // FNV-1a over every byte. Any pixel that moves changes it.
    let hash = 0x811c9dc5, sum = 0;
    for (let i = 0; i < px.length; i++) {
      hash ^= px[i];
      hash = Math.imul(hash, 0x01000193) >>> 0;
      if (i % 4 !== 3) sum += px[i];
    }
    // THE BLOCK SIGNATURE — 256 blocks, each reduced to its dominant channel or
    // a luma bucket. See `same` below for why an exact hash alone was not a
    // witness here.
    const N = 16, B = c.width / N;
    let sig = '';
    for (let by = 0; by < N; by++) {
      for (let bx = 0; bx < N; bx++) {
        let R = 0, G = 0, Bl = 0, n = 0;
        for (let y = by * B; y < (by + 1) * B; y++) {
          for (let x = bx * B; x < (bx + 1) * B; x++) {
            const i = (y * c.width + x) * 4;
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
    return {
      w: sw, h: sh, sig, live: !!liveEl,
      hash: hash.toString(16).padStart(8, '0'),
      mean: sum / ((px.length / 4) * 3),
    };
  });
}

/**
 * SAME PICTURE — and the exact pixel hash is only PART of that test.
 *
 * A composition carrying a MOVE mounts the live Stage canvas instead of the
 * static JPEG, and a drifting canvas renders different pixels every frame:
 * sampling one twice, 700ms apart, with no interaction at all, gives two
 * different FNV hashes at identical luma. This spec's exact-hash comparison
 * therefore reported a false red on roughly one run in five — always with the
 * tell "same size, same luma, different hash", always on a live preview.
 * Measured, not deduced: 20 readbacks of an untouched preview gave 1 distinct
 * hash on a still one and 6 on a drifting one, while the block signature gave
 * 1 in every case and still separated all ten of ten distinct rolls.
 *
 * So `sig` carries the comparison always, and the exact hash — strictly the
 * stronger claim — is asserted wherever it is admissible, which is every pair
 * where neither picture is supposed to be moving. (Same fix as
 * tests/e2e/undo.spec.ts, which is where this was diagnosed.)
 */
const same = (a: Awaited<ReturnType<typeof fingerprint>>, b: typeof a) =>
  a.w === b.w && a.h === b.h && a.sig === b.sig
  && (a.live || b.live || a.hash === b.hash);

const show = (f: Awaited<ReturnType<typeof fingerprint>>) =>
  `${f.w}x${f.h} ${f.live ? 'live' : 'still'} #${f.hash} luma=${f.mean.toFixed(2)}`;

/** The preview is debounced and rendered off a blob; give it room to settle. */
async function settle(page: Page) {
  await page.waitForTimeout(1400);
}

async function boot(page: Page, query = '') {
  await page.goto(APP_URL + query);
  await page.locator('input[type="file"]').first().setInputFiles(TILES);
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  await settle(page);
}

const codeOf = (page: Page) => page.getByTestId('composition-code').innerText();

/** The readout's fragment count, so a roll that would be OVERRIDDEN by the
 *  "every source gets a slot" rule can be rolled again instead of flaking. */
async function fragments(page: Page): Promise<number> {
  const txt = await page.locator('.ui-readout').first().innerText();
  const m = /(\d+)\s*FRAGMENTS/i.exec(txt.replace(/\s+/g, ' '));
  return m ? Number(m[1]) : -1;
}

/**
 * Roll the dice. Nothing more.
 *
 * THIS USED TO FILTER, AND THE FILTER WAS THE BUG'S HIDING PLACE. The first cut
 * re-rolled until the composition asked for at least as many fragments as there
 * are sources, with a docstring explaining that below that line "the app grows
 * the count to cover the sources … it would make a code applied BEFORE the
 * upload land on a different count than one applied after". That is not a test
 * precondition, it is a defect description — and every test called the helper,
 * so the suite was green over exactly the half of the space where the feature
 * worked. An adversarial audit measured the other half: a 3-fragment code opened
 * with 6 photographs produced 6, and 21% of rolls ask for fewer fragments than a
 * 40-photograph pool. T7 now drives that case on purpose.
 *
 * If a helper's docstring explains WHY a case is excluded, write the case down
 * and go and look at it.
 */
async function roll(page: Page) {
  await page.getByRole('button', { name: /Roll the dice/i }).first().click();
  await settle(page);
}

test.describe('the composition code', () => {
  test.setTimeout(240_000);

  test('T1 — pasting the code puts the same picture back, pixel for pixel', async ({ page }) => {
    await boot(page);
    await roll(page);

    const codeA = await codeOf(page);
    const shotA = await fingerprint(page);
    expect(codeA, 'the page showed no composition code').toMatch(/^[0-9A-Z]+-[0-9A-Z]+-[0-9A-Z]+/);
    expect(shotA.mean, 'the canvas is blank').toBeGreaterThan(0);

    // Move somewhere else entirely.
    await roll(page);
    const codeB = await codeOf(page);
    const shotB = await fingerprint(page);
    expect(codeB, 'two rolls produced the same code — the test proves nothing').not.toBe(codeA);
    expect(same(shotA, shotB),
      `two rolls produced the same picture: ${show(shotA)} vs ${show(shotB)}`).toBe(false);

    // Now come back.
    await page.getByTestId('composition-code-input').fill(codeA);
    await page.getByTestId('composition-code-open').click();
    await settle(page);

    const shotBack = await fingerprint(page);
    expect(await codeOf(page), 'the code changed on the way back in').toBe(codeA);
    expect(same(shotA, shotBack),
      `the picture did not come back: was ${show(shotA)}, returned ${show(shotBack)}`).toBe(true);
  });

  test('T2 — a link carrying the code opens that collage on a cold load', async ({ page }) => {
    await boot(page);
    await roll(page);
    const code = await codeOf(page);
    const shot = await fingerprint(page);

    // A whole new page. Nothing survives but the code in the URL.
    await boot(page, `?c=${encodeURIComponent(code)}`);
    const cold = await fingerprint(page);

    expect(await codeOf(page), 'the link opened a different composition').toBe(code);
    expect(same(shot, cold),
      `the link did not reproduce the collage: was ${show(shot)}, cold load ${show(cold)}`).toBe(true);
  });

  test('T3 — the address bar carries the composition, so the URL is shareable', async ({ page }) => {
    await boot(page);
    await roll(page);
    const code = await codeOf(page);
    // The rewrite is debounced; it must land without another interaction.
    await expect.poll(async () => new URL(page.url()).searchParams.get('c'), { timeout: 8000 })
      .toBe(code);
  });

  test('T6 — a code that arrived in the hash opens, and does not linger there stale', async ({ page }) => {
    await boot(page);
    await roll(page);
    const code = await codeOf(page);

    // Chat clients and hand-typed links move a code between ? and # without
    // meaning anything by it, so both must work.
    await boot(page, `#c=${encodeURIComponent(code)}`);
    expect(await codeOf(page), 'a hash link opened a different composition').toBe(code);

    // Once answered in the query, the hash must not park a second, stale code
    // in the same address bar.
    await expect.poll(async () => new URL(page.url()).searchParams.get('c'), { timeout: 8000 })
      .toBe(code);
    expect(new URL(page.url()).hash, 'a stale code was left in the hash').toBe('');
  });

  test('T4 — a code that is not one is refused, and the picture does not move', async ({ page }) => {
    await boot(page);
    await roll(page);
    const before = await fingerprint(page);
    const code = await codeOf(page);

    for (const junk of ['nonsense', code.slice(0, 6), `${code}-oops-oops`, '🎲']) {
      await page.getByTestId('composition-code-input').fill(junk);
      await page.getByTestId('composition-code-open').click();
      await settle(page);
      await expect(page.locator('.ui-code').getByText(/not a composition code/i)).toBeVisible();
      const after = await fingerprint(page);
      expect(same(before, after),
        `"${junk}" moved the picture: ${show(before)} -> ${show(after)}`).toBe(true);
      expect(await codeOf(page), `"${junk}" changed the composition code`).toBe(code);
    }
  });

  test('T7 — a code asking for FEWER fragments than you have sources is honoured', async ({ page }) => {
    // The audit's scenario, exactly. The sender picks a count against a pool
    // that is already loaded; the recipient's code lands before any pool exists.
    // Grow-to-cover used to read that first drop as a late add and quietly
    // replace the sender's number — and 400ms later the address bar was
    // rewritten to the NEW code, so what they were sent was unrecoverable.
    await boot(page);
    // ALL THE WAY DOWN TO 1, which is where the codec used to lie: both floors
    // read `Math.max(2, …)`, so a one-fragment composition minted a code saying
    // two and opened as two. The stepper disables only once you have landed ON
    // 1, so it is a resting state, and stopping this loop short of it was how
    // the browser proof missed it.
    const fewer = page.getByRole('button', { name: 'Fewer fragments' });
    while (await fragments(page) > 1 && await fewer.isEnabled()) {
      await fewer.click();
      await page.waitForTimeout(120);
    }
    await settle(page);
    expect(await fragments(page), 'the stepper did not reach one fragment').toBe(1);

    expect(await fragments(page), 'the stepper did not reach a count below the source count')
      .toBeLessThan(TILES.length);
    const code = await codeOf(page);
    const shot = await fingerprint(page);
    const asked = await fragments(page);

    await boot(page, `?c=${encodeURIComponent(code)}`);
    expect(await fragments(page), 'the pool overrode the count the code asked for').toBe(asked);
    expect(await codeOf(page), 'the address bar was rewritten to a different composition').toBe(code);
    expect(same(shot, await fingerprint(page)),
      `a code asking for ${asked} fragments did not reproduce: was ${show(shot)}`).toBe(true);
  });

  test('T8 — a damaged link says so, and keeps what it was sent', async ({ page }) => {
    await boot(page);
    await roll(page);
    const code = await codeOf(page);

    // The way a code really arrives broken: a chat client ate the tail. Note
    // that this is only DETECTABLE because of the checksum — the seed is the one
    // variable-length field, so a truncated tail used to read as a smaller
    // number and the code opened, cleanly, as somebody else's collage.
    const damaged = code.slice(0, code.length - 4);
    await boot(page, `?c=${encodeURIComponent(damaged)}`);

    // It must be VISIBLE, not silently dropped and then overwritten by the
    // address-bar rewrite 400ms later.
    await expect(page.getByTestId('composition-code-input')).toHaveValue(damaged);
    await expect(page.locator('.ui-code').getByText(/not a composition code/i)).toBeVisible();

    // And it must still be repairable in place.
    await page.getByTestId('composition-code-input').fill(code);
    await page.getByTestId('composition-code-open').click();
    await settle(page);
    expect(await codeOf(page), 'the repaired code did not open').toBe(code);
  });

  test('T9 — pinning a fragment is admitted, because it cannot travel in a code', async ({ page }) => {
    await boot(page);
    await roll(page);
    const strip = page.locator('.ui-code');
    await expect(strip.getByText(/sources are never in the code/i)).toBeVisible();

    // Pin one fragment on the canvas. The lock overlay is the app's own control.
    const cell = page.locator('svg g').first();
    if (await cell.count() === 0) test.skip(true, 'no lock overlay on this preview path');
    await cell.click({ force: true });
    await page.waitForTimeout(500);

    await expect(strip.getByText(/pinned fragments are not in the code/i),
      'a pinned fragment silently changed what the code means').toBeVisible();
  });

  test('T10 — a DERIVED count gets out of the way of your pool; a CHOSEN one does not', async ({ page }) => {
    // The audit's second scenario. The address bar now carries this page's own
    // code, so a plain REFRESH is indistinguishable from opening a link — and a
    // count the app merely derived from "you had 6 photographs" must not then be
    // pinned onto an import of a different size. The code records which kind it
    // is; this proves both branches.
    await boot(page);                                   // 6 tiles, count derived = 6
    const derived = await codeOf(page);
    expect(await fragments(page)).toBe(TILES.length);

    await page.goto(APP_URL + `?c=${encodeURIComponent(derived)}`);
    await page.locator('input[type="file"]').first().setInputFiles(TILES.slice(0, 3));
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await settle(page);
    // A derived count is a default, and the recipient's own pool is a better one.
    expect(await fragments(page), 'a derived count was pinned onto a different pool').toBe(3);

    // Now the other branch: a count the user actually chose survives the pool.
    await boot(page);
    const fewer = page.getByRole('button', { name: 'Fewer fragments' });
    while (await fragments(page) > 4) { await fewer.click(); await page.waitForTimeout(120); }
    await settle(page);
    const chosen = await codeOf(page);
    expect(chosen, 'choosing a count did not change the code').not.toBe(derived);

    await boot(page, `?c=${encodeURIComponent(chosen)}`);
    expect(await fragments(page), 'a chosen count was overridden by the pool').toBe(4);
  });

  test('T5 — the strip is watertight on a phone', async ({ page }) => {
    await boot(page);
    await roll(page);

    for (const width of [320, 360, 390, 430]) {
      await page.setViewportSize({ width, height: 780 });
      await page.waitForTimeout(350);

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      expect(overflow.scrollWidth,
        `${width}px: the page scrolls sideways (${overflow.scrollWidth} > ${overflow.clientWidth})`)
        .toBeLessThanOrEqual(overflow.clientWidth);

      // The code is one unbroken 30-odd character token — exactly the thing that
      // blows a narrow layout open. It must wrap INSIDE its own box.
      const fits = await page.evaluate(() => {
        const strip = document.querySelector('.ui-code') as HTMLElement | null;
        const value = document.getElementById('composition-code-value');
        const copy = document.querySelector('.ui-code__copy') as HTMLElement | null;
        const go = document.querySelector('.ui-code__go') as HTMLElement | null;
        const input = document.querySelector('.ui-code__open input') as HTMLElement | null;
        if (!strip || !value || !copy || !go || !input) return null;
        const s = strip.getBoundingClientRect(), v = value.getBoundingClientRect();
        return {
          spill: Math.max(0, v.right - s.right) + Math.max(0, s.left - v.left),
          copyH: copy.getBoundingClientRect().height,
          goH: go.getBoundingClientRect().height,
          goW: go.getBoundingClientRect().width,
          inputH: input.getBoundingClientRect().height,
          inputFont: parseFloat(getComputedStyle(input).fontSize),
          stripRight: s.right,
          viewport: document.documentElement.clientWidth,
        };
      });
      expect(fits, `${width}px: the code strip is not on the page`).not.toBeNull();
      expect(fits!.spill, `${width}px: the code overflows its own box by ${fits!.spill}px`)
        .toBeLessThanOrEqual(1);
      expect(fits!.stripRight, `${width}px: the strip runs past the viewport`)
        .toBeLessThanOrEqual(fits!.viewport + 1);
      for (const [what, h] of [['copy', fits!.copyH], ['open', fits!.goH], ['input', fits!.inputH]] as const) {
        expect(h, `${width}px: the ${what} target is ${h}px, under the 44px minimum`)
          .toBeGreaterThanOrEqual(44);
      }
      expect(fits!.goW, `${width}px: the Open button is ${fits!.goW}px wide`).toBeGreaterThanOrEqual(44);
      // Under 16px, iOS Safari zooms the page when the field takes focus — which
      // IS the "alters if zoomed on a phone" failure this gate exists for.
      expect(fits!.inputFont, `${width}px: the paste field is ${fits!.inputFont}px and will zoom iOS`)
        .toBeGreaterThanOrEqual(16);
    }
  });
});
