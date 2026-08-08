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

    for (const w of [320, 360, 390, 430]) {
      await page.setViewportSize({ width: w, height: 780 });
      await page.waitForTimeout(250);

      // RE-TRIGGERED AT EVERY WIDTH, not triggered once and measured four times:
      // the red button retires after 6 s and the notice toast after 4, so a loop
      // that set the state once would be measuring a RESTING header by the third
      // viewport and calling it proof. The refusal has to be live under the
      // ruler.
      await openFile(page, legacy);
      const bad = page.getByText(/COULDN'T OPEN THAT FILE/i).first();
      await expect(bad, `the refusal never appeared at ${w}px`).toBeVisible({ timeout: 6000 });

      const m = await page.evaluate(() => {
        const doc = document.documentElement;
        const btn = Array.from(document.querySelectorAll('button'))
          .find((b) => /open/i.test(b.getAttribute('aria-label') || b.textContent || ''))!;
        const row = btn.parentElement!;
        // EVERY control on the row, not just the one that changed. The first
        // version of this test measured the refusal button alone and passed
        // while the button NEXT to it — Export, the primary action — hung 94px
        // outside the viewport. A gate that only grades the element it just
        // touched is grading its own author's assumptions.
        const controls = Array.from(row.querySelectorAll('button')).map((b) => {
          const r = b.getBoundingClientRect();
          const label = b.getAttribute('aria-label') || (b.textContent || '').trim().slice(0, 20);
          // How much of it is actually ON SCREEN. `getBoundingClientRect().width`
          // reports the full 100.6px for a button 94px off the right edge, and
          // the app sits in a `fixed inset-0` with `overflow: hidden`, so those
          // pixels are destroyed rather than scrolled — `doc.scrollWidth` reads
          // clean throughout. Visible width is the only honest number here.
          const visible = Math.max(0, Math.min(r.right, doc.clientWidth) - Math.max(r.left, 0));
          return { label, w: r.width, h: r.height, visible, right: r.right };
        });
        // And the text inside: `.ui-btn__msg` caps at 108px with an ellipsis, so
        // a message longer than that renders as a lie with a "…" on the end.
        const texts = Array.from(row.querySelectorAll('span')).map((s) => ({
          t: (s.textContent || '').trim().slice(0, 24),
          clipped: s.scrollWidth > s.clientWidth + 1,
        })).filter((x) => x.t.length > 0);
        return {
          scrollW: doc.scrollWidth, clientW: doc.clientWidth,
          rowScrollW: row.scrollWidth, rowClientW: row.clientWidth,
          controls, texts,
        };
      });

      expect(m.scrollW, `page overflow at ${w}px (${m.scrollW} > ${m.clientW})`)
        .toBeLessThanOrEqual(m.clientW);
      expect(m.rowScrollW, `the header row overflows at ${w}px (${m.rowScrollW} > ${m.rowClientW})`)
        .toBeLessThanOrEqual(m.rowClientW + 1);

      for (const c of m.controls) {
        expect(c.h, `"${c.label}" is ${c.h}px tall at ${w}px — the law says 44`)
          .toBeGreaterThanOrEqual(44);
        expect(c.visible, `"${c.label}" is clipped at ${w}px — ${c.visible.toFixed(1)}px of ${c.w.toFixed(1)}px on screen`)
          .toBeGreaterThan(c.w - 1);
        expect(c.right, `"${c.label}" runs past the viewport at ${w}px (right=${c.right.toFixed(1)})`)
          .toBeLessThanOrEqual(w + 1);
      }
      for (const t of m.texts) {
        expect(t.clipped, `"${t.t}" is truncated inside the header at ${w}px`).toBe(false);
      }

      // AND THE MESSAGE IS READABLE WHERE IT LANDS. Contrast, in the state the
      // refusal is actually born in: the pointer is still on the button that
      // just failed. `.ui-btn:hover` (0-2-0) used to beat `.ui-btn--bad` (0-1-0)
      // on background but not on colour, painting #1a0505 on --surface-3 at a
      // measured 1.25:1. WCAG AA for this size is 4.5:1.
      // `.ui-btn` transitions `background`, so reading `getComputedStyle`
      // immediately after the state flips samples an INTERPOLATED colour — which
      // is how this assertion first failed at 3.77:1 on a pair that settles at
      // 8.97:1. The settled colour is the one a person reads.
      await page.waitForTimeout(600);
      const contrast = await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button'))
          .find((b) => b.className.includes('ui-btn--bad'));
        if (!btn) return null;
        const cs = getComputedStyle(btn);
        const lum = (c: string) => {
          const [r, g, b] = (c.match(/\d+(\.\d+)?/g) || ['0', '0', '0']).slice(0, 3).map(Number);
          const f = (v: number) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
          return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
        };
        const a = lum(cs.backgroundColor), b = lum(cs.color);
        return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
      });
      if (contrast !== null) {
        expect(contrast, `the refusal button reads at ${contrast.toFixed(2)}:1 at ${w}px — AA wants 4.5`)
          .toBeGreaterThanOrEqual(4.5);
      }
    }
  });

  /**
   * S7 — THE DOOR S1 WAS NOT WATCHING.
   *
   * S1's byte-identical equality is only as wide as the state it varies, and it
   * varies none: it exports from a freshly booted app on the Layout tab. An
   * adversarial audit drove the identical flow with THREE CLICKS ON SHUFFLE in
   * front of it and the deal came back different — `shuffleTrigger` seeds which
   * photograph lands in which fragment (twice: `createRng(seed + shuffleTrigger)`
   * into `assignSources`, and again as `arrangeBag({ shuffle })`) and it was in
   * NEITHER direction of the project file. The composition code had carried it
   * the whole time, which is what makes it a gap rather than an unknown.
   *
   * The same run found `mode` written and never restored, so an export taken with
   * SETTINGS open reopened on Layout and re-exported a different manifest.
   *
   * Both ride in one test on purpose: they are the same defect wearing two
   * fields — live state that reaches the FILE and does not come back — so the
   * proof is S1's own equality with those two knobs turned first.
   */
  test('S7: shuffled, and exported from Settings — still byte-identical', async ({ page }) => {
    await boot(page, 6);

    // The re-deal. Three presses, so a fix that restored only "was it shuffled"
    // rather than the value itself does not pass by accident.
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: /Shuffle\s*images/ }).first().click();
      await page.waitForTimeout(400);
    }
    await page.waitForTimeout(1000);
    const codeBefore = await code(page);

    // And take the export from the OTHER tab, which is what put `mode` in the
    // manifest as something other than what reopening would set.
    await page.getByRole('button', { name: 'Settings' }).first().click();
    await page.waitForTimeout(400);

    const first = await downloadSvg(page);
    const path = onDisk('shuffled.svg', first);

    await page.goto(APP_URL);
    await page.waitForTimeout(800);
    expect(await page.locator('img[src^="blob:"], canvas').count(), 'the reload did not clear the app').toBe(0);

    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(1800);

    // THE TAB, CAPTURED BEFORE ANYTHING TOUCHES IT. The two defects are checked
    // independently and in this order on purpose: reading the composition code
    // means visiting the Layout tab, which destroys the evidence for the tab
    // defect, and asserting the tab first would short-circuit the run before the
    // shuffle was ever examined. One broken field must not hide the other.
    const tabRestored = await page.getByRole('button', { name: 'Settings' })
      .first().getAttribute('class') ?? '';

    // THE SHUFFLE. The composition code is the cheap, readable witness — it folds
    // the shuffle group into its checksum, which is how the audit localised this
    // ("003G"->"00NC", trailing "-3" dropped). It only renders on the Layout tab.
    await page.getByRole('button', { name: 'Layout' }).first().click();
    await page.waitForTimeout(600);
    expect(await code(page), 'the shuffle did not survive the round trip').toBe(codeBefore);

    // THE TAB. `mode` was written into the manifest and read by nothing.
    expect(tabRestored, 'the tab the export was taken from did not come back')
      .toMatch(/border-emerald-500/);

    // The second export has to be taken from the same tab as the first, or
    // `mode` alone moves the bytes.
    await page.getByRole('button', { name: 'Settings' }).first().click();
    await page.waitForTimeout(600);

    const second = await downloadSvg(page);
    expect(srcIds(second), 'the photographs were dealt into different fragments')
      .toEqual(srcIds(first));
    expect(second === first, 'a shuffled project does not round-trip byte-exact').toBe(true);
  });

  /**
   * S8 — THE LATCH HAS TO DIE WITH THE LOAD THAT ARMED IT.
   *
   * Opening a project latches its fragment count so the incoming pool cannot be
   * read as a late add. Nothing bumped `dropId`, so the latch outlived the Open
   * and the NEXT import paid for it: that drop's final effect pass took the
   * `drop !== dropId` branch, cleared the latch and returned WITHOUT reaching
   * grow-to-cover — so the first photographs added after opening a project got
   * no fragment, exactly once, silently. That breaks the "nothing uploaded is
   * stranded" guarantee the effect's own comment block states in full.
   */
  test('S8: photos added right after opening a project are not stranded', async ({ page }) => {
    await boot(page, 4);

    // The count has to be OWNED or there is no latch to outlive anything — a
    // DERIVED count is a default and `handleLoadProject` deliberately does not
    // protect it. One press of the stepper is what takes it over.
    // (The stepper is press-and-hold, so one click can land more than one step.
    //  What matters is that it moved off the derived value and now OWNS it.)
    await page.getByRole('button', { name: 'More fragments' }).first().click();
    await page.waitForTimeout(800);
    const owned = await fragmentCount(page);
    expect(owned, 'the stepper did not take the count over').toBeGreaterThan(4);

    const svg = await downloadSvg(page);
    const path = onDisk('owned.svg', svg);

    await page.goto(APP_URL);
    await openFile(page, path);
    await expect(page.locator('img[src^="blob:"], canvas').first()).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(1800);
    expect(await fragmentCount(page), 'the reopened project did not carry its own count').toBe(owned);

    // A genuine late add, through the real file input, exactly as a second drop.
    // SIX new sources, not two: the stepper is press-and-hold and can land on 6,
    // and an expectation of ">= 6" is then satisfied by the BUG (the count simply
    // stays where it was). The add has to overshoot the owned count by enough
    // that "grew" and "did not grow" cannot produce the same number — this is the
    // audit's own 4 -> 4 -> 10 shape.
    await page.locator('input[type="file"]').first().setInputFiles(tiles(10).slice(4));
    await page.waitForTimeout(3500);

    expect(await fragmentCount(page),
      `the import after Open was swallowed — grow-to-cover never ran for that drop (count stuck at the latched ${owned})`)
      .toBeGreaterThanOrEqual(10);
  });
});
