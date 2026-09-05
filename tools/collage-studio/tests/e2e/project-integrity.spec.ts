// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
// Real save/open/restore routes. Unit coverage is projectLocks.invariants.mjs.
import { test, expect, type Page, type Download } from '@playwright/test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import JSZip from 'jszip';
import { createHash } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const cells = (page: Page) => page.locator('svg[viewBox^="0 0 1200 "] > g');
// Archive members historically lose their MIME labels on load. Normalize that
// label only: every source byte, crop, placement and manifest field must match.
// Hashing avoids dumping megabytes of image data when an assertion fails.
const svgDigest = (svg: string) => createHash('sha256')
  .update(svg.replace(/data:[^;"\s]*;base64,/g, 'data:;base64,')).digest('hex');

async function bytes(download: Download): Promise<Buffer> {
  const stream = await download.createReadStream();
  if (!stream) throw new Error('No downloaded file');
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(chunk as Buffer);
  return Buffer.concat(chunks);
}

async function boot(page: Page) {
  await page.route('**/cdn.jsdelivr.net/**', (route) => route.abort());
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles([
    join(HERE, '../fixtures/img_a.jpg'), join(HERE, '../fixtures/img_b.jpg'),
  ]);
  await expect(cells(page).first()).toBeVisible({ timeout: 60_000 });
  await page.getByRole('button', { name: 'Settings', exact: true }).click();
  await page.getByRole('button', { name: 'Balanced', exact: true }).click();
  await page.getByRole('button', { name: 'Layout', exact: true }).click();
  await expect(page.locator('.animate-spin')).toHaveCount(0, { timeout: 15_000 });
}

async function downloadSvg(page: Page): Promise<string> {
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const dialog = page.getByRole('dialog').filter({ hasText: 'Export' }).first();
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 60_000 }),
    dialog.getByRole('button', { name: /Vector SVG/ }).click(),
  ]);
  return (await bytes(download)).toString('utf8');
}

test('a manual pin survives file, SVG and crash-safe save', async ({ page }) => {
  test.setTimeout(180_000);
  await boot(page);
  await cells(page).first().locator('path').first().click();
  await expect(cells(page).first().locator('foreignObject')).toHaveCount(1);

  // Read the real durable row: a lone pin must schedule a write by itself.
  await expect.poll(() => page.evaluate(() => new Promise<number>((resolve) => {
    const request = indexedDB.open('collage-session');
    request.onerror = () => resolve(-1);
    request.onsuccess = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('project')) { db.close(); resolve(-1); return; }
      const read = db.transaction('project').objectStore('project').get('current');
      read.onsuccess = () => { const n = read.result?.manifest?.locks?.length ?? 0; db.close(); resolve(n); };
      read.onerror = () => { db.close(); resolve(-1); };
    };
  })), { timeout: 15_000 }).toBe(1);

  const originalSvg = await downloadSvg(page);
  const [saved] = await Promise.all([page.waitForEvent('download'), page.keyboard.press('Control+s')]);
  const zip = await JSZip.loadAsync(await bytes(saved));
  const manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  expect(manifest.locks).toHaveLength(1);
  expect(manifest.locks[0][0]).toBe(0);
  expect(manifest.images.some((image: { id: string }) => image.id === manifest.locks[0][1])).toBeTruthy();
  const path = await saved.path();
  expect(path).toBeTruthy();

  await page.reload();
  const [chooser] = await Promise.all([
    page.waitForEvent('filechooser'), page.getByRole('button', { name: 'Open', exact: true }).click(),
  ]);
  await chooser.setFiles(path!);
  await expect(cells(page).first().locator('foreignObject')).toHaveCount(1, { timeout: 60_000 });
  await expect(page.locator('.animate-spin')).toHaveCount(0);
  expect(svgDigest(await downloadSvg(page))).toBe(svgDigest(originalSvg));
});

test('a failed original read refuses Save, then can retry successfully', async ({ page }) => {
  test.setTimeout(120_000);
  await boot(page);
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  let downloads = 0;
  page.on('download', () => downloads++);
  // Fault injection at the source-byte read. Decoded artwork remains open.
  await page.evaluate(() => {
    const target = window as typeof window & { projectIntegrityFetch?: typeof fetch };
    target.projectIntegrityFetch = window.fetch;
    window.fetch = (input, init) => typeof input === 'string' && input.startsWith('blob:')
      ? Promise.reject(new Error('Injected source read failure')) : target.projectIntegrityFetch!(input, init);
  });
  await page.keyboard.press('Control+s');
  await expect(page.getByText(/Could not save .*original could not be read/i)).toBeVisible();
  expect(downloads).toBe(0);
  expect(errors).toEqual([]);
  await expect(cells(page).first()).toBeVisible();
  await page.evaluate(() => {
    const target = window as typeof window & { projectIntegrityFetch?: typeof fetch };
    window.fetch = target.projectIntegrityFetch!;
    delete target.projectIntegrityFetch;
  });
  const [saved] = await Promise.all([page.waitForEvent('download'), page.keyboard.press('Control+s')]);
  expect((await bytes(saved)).byteLength).toBeGreaterThan(0);
});
