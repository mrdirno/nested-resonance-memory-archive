// Author: Aldrin Payopay · GPL-3.0-only
// C3733 — THE TITLE COLOUR reaches the export a person actually sends.
//
// The SVG export is the honest witness here: it is text, it is deterministic,
// and `vectorExport` draws its title through the SAME `titlePlanToSvg` the live
// canvas and the video worker draw through — so a colour proven in the SVG is a
// colour proven on every surface. No pixels, no audio, no stubs: a real image is
// dropped, a real title is typed, a real swatch is tapped, and the real Export
// sheet writes the real file.
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';
import fs from 'node:fs/promises';

// A valid, decodable 96×96 PNG built in-process — the app needs real pixels to
// intake, and a fixture on disk is one more thing to keep in sync.
function pngCrc32(bytes: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function whitePng(): Buffer {
  const chunk = (kind: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const body = Buffer.concat([Buffer.from(kind), data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(pngCrc32(body));
    return Buffer.concat([len, body, crc]);
  };
  const head = Buffer.alloc(13); head.writeUInt32BE(96, 0); head.writeUInt32BE(96, 4); head[8] = 8; head[9] = 2;
  const pixels = Buffer.alloc(96 * (1 + 96 * 3), 245);
  for (let y = 0; y < 96; y++) pixels[y * 289] = 0;
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', head), chunk('IDAT', zlib.deflateSync(pixels)), chunk('IEND', Buffer.alloc(0))]);
}

async function boot(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.locator('input[type=file][accept="image/*,video/*"]')
    .setInputFiles({ name: 'owned-art.png', mimeType: 'image/png', buffer: whitePng() });
  await page.getByRole('navigation', { name: 'Studio tools' })
    .getByRole('button', { name: 'Text', exact: true }).click();
  // The Text tool opens on Lyrics & captions; the titler is behind its own tab.
  await page.getByRole('button', { name: 'Title', exact: true }).click();
  await page.getByTestId('title-input').fill('FIRST LIGHT');
  // The swatches only exist once there is a title to colour.
  await expect(page.getByTestId('title-color-black')).toBeVisible({ timeout: 60_000 });
}

/** Open the Export sheet, take the Vector SVG, and return the file's text. */
async function exportSvg(page: Page): Promise<string> {
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const dl = page.waitForEvent('download');
  await page.getByRole('button', { name: /Vector SVG/ }).click();
  const p = (await (await dl).path())!;
  return fs.readFile(p, 'utf8');
}

/** Just the Title group, so a fill from some OTHER element cannot pass the test. */
function titleGroup(svg: string): string {
  const a = svg.indexOf('<g id="Title">');
  expect(a, 'the SVG carries a Title group').toBeGreaterThanOrEqual(0);
  const b = svg.indexOf('</g>', a);
  return svg.slice(a, b + 4);
}

test('the title colour a person picks is the colour every export paints', async ({ page }) => {
  await boot(page);

  // DEFAULT WHITE — the legacy pair, unchanged, so no old project moves.
  let g = titleGroup(await exportSvg(page));
  expect(g).toContain('fill="#ffffff"');          // ink
  expect(g).toContain('fill="rgba(0,0,0,0.42)"');  // dark plate

  // BLACK — the scrim MUST flip to light, or a black title is invisible on a
  // dark photo. This is the whole reason the polarity is derived, not chosen.
  await page.getByTestId('title-color-black').click();
  await expect(page.getByTestId('title-color-black')).toHaveAttribute('aria-pressed', 'true');
  g = titleGroup(await exportSvg(page));
  expect(g).toContain('fill="#111111"');             // near-black ink
  expect(g).toContain('fill="rgba(255,255,255,0.60)"'); // LIGHT plate
  expect(g).not.toContain('fill="rgba(0,0,0,0.42)"');   // never the dark one

  // YELLOW — a luminous ink keeps the legacy dark plate; only a dark ink flips.
  await page.getByTestId('title-color-yellow').click();
  g = titleGroup(await exportSvg(page));
  expect(g).toContain('fill="#ffd400"');
  expect(g).toContain('fill="rgba(0,0,0,0.42)"');
});
