// Author: Aldrin Payopay · GPL-3.0-only
// C3741 — THE TITLE FONT reaches the export a person actually sends.
//
// Same honest witness as the colour proof: the SVG export is text, deterministic,
// and `vectorExport` draws its title through the SAME `titlePlanToSvg` the live
// canvas and the video worker draw through — so a family proven in the SVG is a
// family proven on every surface. No pixels, no audio, no stubs: a real image is
// dropped, a real title is typed, a real font chip is tapped, and the real Export
// sheet writes the real file.
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';
import fs from 'node:fs/promises';

// The stacks the module ships, restated so the test agrees with the render, not
// with the source. `SANS` is the legacy family every untouched title keeps.
const SANS = '"Helvetica Neue", Helvetica, Arial, sans-serif';
const SERIF = 'Georgia, "Times New Roman", Times, serif';
const MONO = '"Courier New", Courier, monospace';

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
  // The font chips only exist once there is a title to set.
  await expect(page.getByTestId('title-font-serif')).toBeVisible({ timeout: 60_000 });
}

/** Open the Export sheet, take the Vector SVG, and return the file's text. */
async function exportSvg(page: Page): Promise<string> {
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const dl = page.waitForEvent('download');
  await page.getByRole('button', { name: /Vector SVG/ }).click();
  const p = (await (await dl).path())!;
  return fs.readFile(p, 'utf8');
}

/** Just the Title group, so a font on some OTHER element cannot pass the test. */
function titleGroup(svg: string): string {
  const a = svg.indexOf('<g id="Title">');
  expect(a, 'the SVG carries a Title group').toBeGreaterThanOrEqual(0);
  const b = svg.indexOf('</g>', a);
  return svg.slice(a, b + 4);
}

test('the title font a person picks is the family every export paints', async ({ page }) => {
  await boot(page);

  // DEFAULT SANS — the legacy family, unchanged, so no old project moves.
  let g = titleGroup(await exportSvg(page));
  expect(g).toContain(`font-family='${SANS}'`);

  // SERIF — the export must switch families, and the sans stack must be gone
  // from the Title group, or "changed the font" would be a lie on the wire.
  await page.getByTestId('title-font-serif').click();
  await expect(page.getByTestId('title-font-serif')).toHaveAttribute('aria-pressed', 'true');
  g = titleGroup(await exportSvg(page));
  expect(g).toContain(`font-family='${SERIF}'`);
  expect(g).not.toContain(`font-family='${SANS}'`);

  // MONO — a third, distinct family, proving it is a real choice and not a toggle.
  await page.getByTestId('title-font-mono').click();
  await expect(page.getByTestId('title-font-mono')).toHaveAttribute('aria-pressed', 'true');
  g = titleGroup(await exportSvg(page));
  expect(g).toContain(`font-family='${MONO}'`);

  // POSTER — the heavy display face, and back to it naming Impact on the wire.
  await page.getByTestId('title-font-poster').click();
  g = titleGroup(await exportSvg(page));
  expect(g).toContain('Impact');
});
