/**
 * THE POST AT THE ARTIFACT — the exported SVG opens back up, with the pictures.
 *
 * The manifest codec is swept in tests/unit/svgProject.invariants.mjs (2,070
 * checks: round trip across hostile captions, escaping inverses, image recovery,
 * every refusal). Four things can only be proved out here, in a real browser,
 * through the real Export sheet and the real Open button:
 *
 *   S1  THE FILE IS THE PROJECT. Export an SVG, RELOAD the page so nothing is in
 *       memory, open the file, and export again — and require the two downloads
 *       to be BYTE-IDENTICAL. That single equality covers everything a weaker
 *       assertion would have to enumerate: the settings, the caption, the look,
 *       the source pool's ORDER and LENGTH (a pool that comes back short or
 *       shuffled re-deals every fragment), each picture's analysis floats, and
 *       each picture's actual bytes. Any one of them drifting moves the file.
 *
 *   S2  A CAPTION CANNOT CORRUPT THE FILE. The manifest used to ride in an XML
 *       comment, where `--` is illegal and `-->` closes it early — both typeable
 *       into the title box. This renders the exported SVG in the browser's own
 *       XML parser and requires a document, not a parse error.
 *
 *   S3  THE PICTURES ARE IN THERE. The pool is embedded and matched by
 *       `data-src-id`; a project with more photographs than fragments carries
 *       the undrawn ones too, because `arrangeBag` deals from the pool's length.
 *
 *   S4  A FILE IT CANNOT OPEN IS REFUSED, VISIBLY. `loadProject` fails closed by
 *       design; a refusal that shows nothing is indistinguishable from a hang.
 *
 * Run against the live dev server (NEVER :5173 — that is Persona 500):
 *   npx playwright test --config playwright.svg-project.config.ts
 * or against the deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.svg-project.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/**
 * THE CAPTION THAT USED TO BREAK THE FILE. `--` is illegal anywhere inside an
 * XML comment and `-->` ends one; both are ordinary things to type.
 */
const HOSTILE_TITLE = 'DAY 3 -- the rough-in --> punchlist & <notes>';

// --- fixtures ----------------------------------------------------------------

function png(w: number, h: number, pixel: (x: number, y: number) => [number, number, number]): Buffer {
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(zlib.crc32(Buffer.concat([t, data])) >>> 0, 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2;
  const rows: Buffer[] = [];
  for (let y = 0; y < h; y++) {
    const row = Buffer.alloc(1 + w * 3);
    for (let x = 0; x < w; x++) {
      const [r, g, b] = pixel(x, y);
      row[1 + x * 3] = r; row[1 + x * 3 + 1] = g; row[1 + x * 3 + 2] = b;
    }
    rows.push(row);
  }
  const idat = zlib.deflateSync(Buffer.concat(rows));
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

/**
 * DISTINCT tiles, not the near-white solids the title proof uses. Which photo
 * lands in which fragment is exactly what a lost pool order corrupts, so every
 * source has to be visibly different from every other one — with identical
 * tiles, a re-dealt collage looks like the same collage.
 */
const tiles = (n: number) => Array.from({ length: n }, (_, i) => {
  const hue = (i * 360) / n;
  const [r, g, b] = hsl(hue, 0.85, 0.5);
  return {
    name: `tile_${i}.png`,
    mimeType: 'image/png',
    // A diagonal wedge so the ENERGY CENTROID differs per tile too — that is
    // what the analysis carries, and it decides where each crop is anchored.
    buffer: png(96, 96, (x, y) => (x + y * (1 + i % 3) > 96 ? [r, g, b] : [255 - r, 255 - g, 255 - b])),
  };
});

function hsl(h: number, s: number, l: number): [number, number, number] {
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  const [r, g, b] =
    h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] :
    h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return [Math.round((r + m) * 255), Math.round((g + m) * 255), Math.round((b + m) * 255)];
}

// --- page helpers ------------------------------------------------------------

async function boot(page: Page, n = 6) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles(tiles(n));
  await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
  // Layout / Settings — NOT Simple / Advanced (scar: an e2e written against the
  // internal state names finds no button and times out).
  await page.getByRole('button', { name: 'Settings' }).first().click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).first().click();
  await page.getByRole('button', { name: 'Layout' }).first().click();
  await page.waitForTimeout(1400);
}

/** Drives the real Export sheet, takes the real download, returns the bytes. */
async function downloadSvg(page: Page): Promise<string> {
  await page.getByRole('button', { name: 'Export' }).first().click();
  const dialog = page.getByRole('dialog').filter({ hasText: 'Export' }).first();
  await expect(dialog).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 90_000 }),
    dialog.getByRole('button', { name: /Vector SVG/ }).first().click(),
  ]);
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const c of stream) chunks.push(c as Buffer);
  await page.waitForTimeout(600);
  return Buffer.concat(chunks).toString('utf8');
}

/** Drives the real Open button through the real file chooser. */
async function openFile(page: Page, path: string) {
  const [chooser] = await Promise.all([
    page.waitForEvent('filechooser', { timeout: 30_000 }),
    page.getByRole('button', { name: 'Open' }).first().click(),
  ]);
  await chooser.setFiles(path);
}

const onDisk = (name: string, text: string): string => {
  const p = join(mkdtempSync(join(tmpdir(), 'collage-svg-')), name);
  writeFileSync(p, text, 'utf8');
  return p;
};

const code = (page: Page) => page.getByTestId('composition-code').innerText();

/** Every `data-src-id` in the document, in order of appearance. */
const srcIds = (svg: string): string[] =>
  Array.from(svg.matchAll(/data-src-id="([^"]+)"/g)).map((m) => m[1]);

/** Split at the undrawn-pool stash, so "what is painted" and "what is merely
 *  carried" can be counted apart — the whole point of S3. */
const STASH = '<defs id="collage-sources">';
const drawnIds = (svg: string): string[] =>
  srcIds(svg.includes(STASH) ? svg.slice(0, svg.indexOf(STASH)) : svg);
const stashedIds = (svg: string): string[] =>
  svg.includes(STASH) ? srcIds(svg.slice(svg.indexOf(STASH))) : [];

/** What the fragment stepper currently reads. */
const fragmentCount = async (page: Page): Promise<number> =>
  parseInt(await page.locator('.ui-stepper__value').first().innerText(), 10);

// =============================================================================

test.describe('the post — the SVG is the project', () => {

  test('S1: export, reload, open, export again — byte-identical', async ({ page }) => {
    await boot(page, 6);

    await page.getByTestId('title-input').fill(HOSTILE_TITLE);
    await page.getByTestId('look-warm').click();
    await page.waitForTimeout(1400);

    const codeBefore = await code(page);
    const first = await downloadSvg(page);
    expect(first, 'the export carries a project manifest').toContain('id="collage-project"');
    expect(first, 'the old comment container is gone').not.toContain('JSON_MANIFEST');

    const path = onDisk('post.svg', first);

    // RELOAD. Nothing survives in memory — the file is the only thing carrying
    // this collage, which is the whole claim.
    await page.goto(APP_URL);
    await page.waitForTimeout(1200);

    // PROVE THE RELOAD EMPTIED IT, or the equality below could be satisfied by a
    // page that never lost the composition. The sharp case is `?c=`: the app
    // keeps the composition code in the address bar and replays it at mount, so
    // a reload that kept the query string would restore this collage WITHOUT the
    // file and the byte-equality below would prove nothing. Both are checked —
    // no pictures, and a different composition.
    expect(await page.locator('img[src^="blob:"], canvas').count(), 'a collage survived the reload').toBe(0);
    expect(await page.getByTestId('title-input').count(), 'the caption box survived the reload').toBe(0);
    expect(await code(page), 'the composition survived the reload — the file is not being tested')
      .not.toBe(codeBefore);

    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(2200);

    // The settings a person can SEE came back.
    expect(await page.getByTestId('title-input').inputValue()).toBe(HOSTILE_TITLE);
    await expect(page.getByTestId('look-warm')).toHaveAttribute('aria-pressed', 'true');
    expect(await code(page), 'the composition code is the same composition').toBe(codeBefore);

    // And the file it produces is the file it came from — every setting, the
    // pool's order and length, every analysis float, every picture's bytes.
    const second = await downloadSvg(page);
    expect(srcIds(second), 'the same sources, in the same order').toEqual(srcIds(first));
    expect(
      second.length,
      `the reopened project re-exports a different file (${first.length} bytes out, ${second.length} back)`,
    ).toBe(first.length);
    expect(second === first, 'the round trip is not byte-exact').toBe(true);
  });

  test('S2: a caption with -- and --> still parses as XML', async ({ page }) => {
    await boot(page, 4);
    await page.getByTestId('title-input').fill(HOSTILE_TITLE);
    await page.waitForTimeout(1400);

    const svg = await downloadSvg(page);
    expect(svg).toContain('id="collage-project"');

    // The browser's OWN XML parser, which is what renders an .svg file. A
    // `parsererror` element is how it reports a document it could not build.
    const verdict = await page.evaluate((text) => {
      const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
      const err = doc.getElementsByTagName('parsererror');
      const meta = doc.getElementById('collage-project');
      return {
        error: err.length ? (err[0].textContent || 'parsererror').slice(0, 240) : null,
        root: doc.documentElement ? doc.documentElement.nodeName : null,
        title: meta ? (JSON.parse(meta.textContent || '{}')?.state?.title?.text ?? null) : null,
      };
    }, svg);

    expect(verdict.error, `the exported SVG is not well-formed XML: ${verdict.error}`).toBeNull();
    expect(verdict.root).toBe('svg');
    // Parsed by the browser, out of the real document — not by our own reader.
    expect(verdict.title, 'the caption survived the container it broke before').toBe(HOSTILE_TITLE);

    // The same construction in the OLD container, measured rather than asserted.
    const oldBreaks = await page.evaluate((t) => {
      const doc = new DOMParser().parseFromString(
        `<?xml version="1.0"?>\n<!-- JSON_MANIFEST: {"title":{"text":${JSON.stringify(t)}}} -->\n<svg xmlns="http://www.w3.org/2000/svg"/>`,
        'image/svg+xml',
      );
      return doc.getElementsByTagName('parsererror').length > 0;
    }, HOSTILE_TITLE);
    expect(oldBreaks, 'the old comment container was already safe — this fix has no subject').toBe(true);
  });

  test('S3: the pool travels whole, including what is not drawn', async ({ page }) => {
    await boot(page, 5);

    const drawnAll = await downloadSvg(page);
    expect(srcIds(drawnAll).length, 'five sources, five ids').toBe(5);
    expect(new Set(srcIds(drawnAll)).size).toBe(5);
    expect(stashedIds(drawnAll), 'nothing to stash when every photo is drawn').toEqual([]);

    // Cut the collage to THREE fragments while five photographs are loaded. The
    // pool is still five, and `arrangeBag` deals from its LENGTH — so a file
    // carrying only the three it shows would reopen as a different pairing.
    //
    // The stepper is "Fewer fragments" in the LAYOUT tab. An earlier draft of
    // this test looked for a button named `−` in Settings, found nothing, and
    // skipped the reduction entirely — so it asserted "5 of 5 carried" about a
    // collage that was still drawing all five, and passed while proving nothing.
    // Hence the explicit before/after on the stepper's own readout.
    expect(await fragmentCount(page), 'the pool did not start at five').toBe(5);
    const fewer = page.getByRole('button', { name: 'Fewer fragments' }).first();
    await expect(fewer).toBeVisible();
    // Click until it STOPS FALLING, not to a number picked in advance:
    // `updateCountSmart` snaps a Balanced layout to a grid product (cols x rows,
    // both at least 2), so from five the reachable step down is four and three
    // is a fixed point that does not exist. Targeting 3 made this test fail on
    // correct app behaviour; the premise is "fewer fragments than photographs",
    // and the exact number is the app's to choose.
    let n = await fragmentCount(page);
    for (let i = 0; i < 12; i++) {
      await fewer.click();
      await page.waitForTimeout(450);
      const next = await fragmentCount(page);
      if (next === n) break;
      n = next;
    }
    await page.waitForTimeout(1600);
    const drawnCount = await fragmentCount(page);
    expect(drawnCount, 'the stepper never reduced the count below the pool').toBeLessThan(5);

    const svg = await downloadSvg(page);
    const drawn = new Set(drawnIds(svg));
    const stashed = new Set(stashedIds(svg));
    const ids = new Set(srcIds(svg));
    expect(drawn.size, `${drawnCount} fragments should paint ${drawnCount} sources`).toBe(drawnCount);
    expect(stashed.size, 'the photographs that are not drawn must still travel')
      .toBe(5 - drawnCount);
    expect(
      ids.size,
      `the file carries ${ids.size} of the 5 photographs in the project — a short pool re-deals every slot`,
    ).toBe(5);

    // Reopening it must still land on the same picture.
    const path = onDisk('pool.svg', svg);
    await page.goto(APP_URL);
    await page.waitForTimeout(1200);
    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(2200);
    const back = await downloadSvg(page);
    expect(back === svg, 'a project with undrawn photographs does not round-trip').toBe(true);
  });

  test('S4: a file it cannot open is refused, and says so', async ({ page }) => {
    await boot(page, 3);

    // An SVG in the OLD form: a real manifest, no image identity. It cannot be
    // reopened exactly, so it must be refused rather than half-opened.
    const legacy = onDisk('legacy.svg',
      `<?xml version="1.0"?>\n<!-- JSON_MANIFEST: {"version":"1.0","layout":{"mode":"balanced","count":6,"seed":1,"aspect":1,"gutter":0.005},"style":{"background":"#000"}} -->\n` +
      `<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>`);

    const before = await code(page);
    await openFile(page, legacy);
    await page.waitForTimeout(2000);

    // The refusal is VISIBLE. Before this, a rejected file did nothing at all —
    // no picture, no message, no way to tell it apart from a slow one.
    await expect(page.getByText(/COULDN'T OPEN THAT FILE/i).first()).toBeVisible({ timeout: 6000 });
    // And it left the open composition alone.
    expect(await code(page), 'a refused file changed the composition anyway').toBe(before);
  });

  test('S5: watertight on a phone, with the file that reopens', async ({ page }) => {
    await boot(page, 4);
    await page.getByTestId('title-input').fill(HOSTILE_TITLE);
    await page.waitForTimeout(1200);

    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(250);
      const m = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      }));
      expect(m.scrollW, `horizontal overflow at ${w}px (${m.scrollW} > ${m.clientW})`)
        .toBeLessThanOrEqual(m.clientW);
    }
  });

  /**
   * S6 — THE GATE HAS TO SEE THE THING IT IS GRADING.
   *
   * S5 above measures a header in its RESTING state, and the increment this file
   * proves out put a NEW state in that header: on a refused file the Open button
   * stops saying "Open" (4 characters) and says "COULDN'T OPEN THAT FILE" (23),
   * in a `ui-btn--compact` that sits on the same row as Export and Save. A gate
   * that never renders that state is grading the old header.
   *
   * This is the trim scar repeated as a rule: `mobile-watertight.spec.ts` imports
   * PNGs, so the whole video transport does not exist while it runs, and eleven
   * controls sat under the 44px law unmeasured for as long as that was true.
   * So the refusal is FORCED here, at every width the law names, and the row is
   * measured on its own — an overflowing header inside a scroll container would
   * not move `documentElement.scrollWidth` at all.
   */
  test('S6: the refusal is watertight too, at every width', async ({ page }) => {
    await boot(page, 3);

    const legacy = onDisk('legacy.svg',
      `<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>`);
    await openFile(page, legacy);
    const bad = page.getByText(/COULDN'T OPEN THAT FILE/i).first();
    await expect(bad).toBeVisible({ timeout: 6000 });

    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(250);

      // The message is still on screen — the 6 s timer has not run out mid-loop.
      await expect(bad).toBeVisible();

      const m = await page.evaluate(() => {
        const doc = document.documentElement;
        // The button carrying the message, and the row it lives on.
        const btn = Array.from(document.querySelectorAll('button'))
          .find((b) => /COULDN'T OPEN/i.test(b.textContent || ''))!;
        const row = btn.parentElement!;
        const r = btn.getBoundingClientRect();
        return {
          scrollW: doc.scrollWidth, clientW: doc.clientWidth,
          rowScrollW: row.scrollWidth, rowClientW: row.clientWidth,
          h: r.height, right: r.right, left: r.left,
          clipped: btn.scrollWidth > btn.clientWidth + 1,
        };
      });

      expect(m.scrollW, `page overflow at ${w}px (${m.scrollW} > ${m.clientW})`)
        .toBeLessThanOrEqual(m.clientW);
      expect(m.rowScrollW, `the header row overflows at ${w}px (${m.rowScrollW} > ${m.rowClientW})`)
        .toBeLessThanOrEqual(m.rowClientW + 1);
      expect(m.h, `the refusal button is ${m.h}px tall at ${w}px — the law says 44`)
        .toBeGreaterThanOrEqual(44);
      expect(m.left, `the refusal starts off-screen left at ${w}px`).toBeGreaterThanOrEqual(0);
      expect(m.right, `the refusal runs past the viewport at ${w}px`).toBeLessThanOrEqual(w);
      expect(m.clipped, `the refusal text is clipped inside its own button at ${w}px`).toBe(false);
    }
  });
});
