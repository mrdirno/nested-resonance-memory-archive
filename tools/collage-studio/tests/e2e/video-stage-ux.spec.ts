// Author: Aldrin Payopay · GPL-3.0-only
// Public UI only: compact transport, retained playback and reachable Stop.
import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';

async function nativeArt(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.getByRole('button', { name: 'Art Room', exact: true }).click();
  await page.getByRole('button', { name: 'Add artwork', exact: true }).click();
  await expect(page.locator('.art-footer p[role=status]')).toContainText('Editable artwork applied', { timeout: 60_000 });
  await page.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  await expect(page.getByTestId('video-transport')).toBeVisible();
}

test('playback stays compact at narrow and short viewport sizes', async ({ page }, info) => {
  await nativeArt(page);
  const transport = page.getByTestId('video-transport');
  await expect(transport.getByRole('button', { name: 'Record video', exact: true })).toBeHidden();
  await expect(transport.getByRole('button', { name: 'Details', exact: true })).toHaveAttribute('aria-expanded', 'false');
  for (const viewport of [{ width: 320, height: 448 }, { width: 360, height: 780 }, { width: 844, height: 390 }]) {
    await page.setViewportSize(viewport);
    const geometry = await transport.evaluate((element) => {
      const bar = element.querySelector('.video-transport__bar')!.getBoundingClientRect();
      const range = element.querySelector('input[type=range]')!.getBoundingClientRect();
      const visible = [...element.querySelectorAll('button')].filter(button => button.getClientRects().length > 0);
      return {
        height: bar.height, rangeWidth: range.width,
        controls: visible.map(button => { const r = button.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height }; }),
      };
    });
    expect(geometry.height, JSON.stringify(geometry)).toBeLessThanOrEqual(60);
    expect(geometry.rangeWidth).toBeGreaterThanOrEqual(100);
    expect(geometry.controls).toHaveLength(3);
    for (const r of geometry.controls) {
      expect(r.left).toBeGreaterThanOrEqual(0);
      expect(r.right).toBeLessThanOrEqual(viewport.width);
      expect(r.top).toBeGreaterThanOrEqual(0);
      expect(r.bottom).toBeLessThanOrEqual(viewport.height);
      expect(r.width).toBeGreaterThanOrEqual(44);
      expect(r.height).toBeGreaterThanOrEqual(44);
    }
    await page.screenshot({ path: info.outputPath(`playback-${viewport.width}x${viewport.height}.png`) });
  }
});

test('Details retains the canvas and parked playhead, and its controls remain usable', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await nativeArt(page);
  const transport = page.getByTestId('video-transport');
  const playhead = transport.getByLabel(/^Playhead/);
  await playhead.fill('2.5');
  await expect(playhead).toHaveValue('2.5');
  const canvas = await page.locator('canvas[aria-hidden=true]').first().elementHandle();
  expect(canvas).not.toBeNull();
  const details = transport.getByRole('button', { name: 'Details', exact: true });
  await details.click();
  await expect(transport.getByRole('region', { name: 'Media and recording details' })).toBeVisible();
  await expect(transport.getByRole('button', { name: 'Record video', exact: true })).toBeEnabled();
  await transport.getByRole('button', { name: '5s', exact: true }).click();
  await expect(playhead).toHaveAttribute('max', '5');
  await playhead.fill('2.5');
  await details.click();
  await expect(playhead).toHaveValue('2.5');
  expect(await canvas!.evaluate(element => element.isConnected && element === document.querySelector('canvas[aria-hidden=true]'))).toBe(true);
  await playhead.focus();
  await page.keyboard.press('ArrowRight');
  await expect(playhead).toHaveValue('2.6');
  await expect(transport.getByRole('button', { name: 'Unmute preview', exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});

test('rendering exposes Stop outside the collapsed recording details', async ({ page }) => {
  test.setTimeout(90_000);
  await nativeArt(page);
  const transport = page.getByTestId('video-transport');
  await transport.getByRole('button', { name: 'Details', exact: true }).click();
  await transport.getByRole('button', { name: 'Record video', exact: true }).click();
  const stop = transport.getByRole('button', { name: 'Stop recording', exact: true });
  await expect(stop).toBeVisible();
  await expect(transport.getByRole('region', { name: 'Media and recording details' })).toBeHidden();
  await stop.click();
  await expect(stop).toBeHidden({ timeout: 60_000 });
  await expect(transport.getByRole('button', { name: 'Details', exact: true })).toBeVisible();
});

test('source trims remain reachable through Details without crowding playback', async ({ page }) => {
  test.setTimeout(90_000);
  await page.setViewportSize({ width: 360, height: 640 });
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles(fileURLToPath(new URL('../fixtures/ramp_rgb.mp4', import.meta.url)));
  const transport = page.getByTestId('video-transport');
  await expect(transport).toBeVisible({ timeout: 60_000 });
  const trim = transport.getByRole('button', { name: 'Trim ramp_rgb.mp4', exact: true });
  await expect(trim).toBeHidden();
  const details = transport.getByRole('button', { name: 'Details', exact: true });
  await details.click();
  await trim.click();
  const sheet = page.getByRole('dialog', { name: 'Trim ramp_rgb.mp4', exact: true });
  await sheet.getByLabel('In point for ramp_rgb.mp4', { exact: true }).fill('0.5');
  await sheet.getByRole('button', { name: 'Done', exact: true }).click();
  await details.click();
  await expect(trim).toBeHidden();
  await details.click();
  await trim.click();
  await expect(sheet.getByLabel('In point for ramp_rgb.mp4', { exact: true })).toHaveValue('0.5');
  await sheet.getByRole('button', { name: 'Done', exact: true }).click();
  await expect(transport.getByRole('button', { name: 'Unmute preview', exact: true })).toBeVisible();
});

test('editing and Details share space, and Escape leaves expanded playback intact', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 664 });
  await nativeArt(page);
  const transport = page.getByTestId('video-transport');
  const details = transport.getByRole('button', { name: 'Details', exact: true });
  const layout = page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Layout', exact: true });
  await layout.click();
  await expect(page.getByRole('complementary', { name: 'Editing panel' })).toBeVisible();
  await details.click();
  await expect(page.getByRole('complementary', { name: 'Editing panel' })).toBeHidden();
  await expect(details).toHaveAttribute('aria-expanded', 'true');
  await layout.click();
  await expect(details).toHaveAttribute('aria-expanded', 'false');
  await page.getByRole('button', { name: 'Close editing panel', exact: true }).click();
  await details.click();
  await page.getByRole('button', { name: 'Expand preview', exact: true }).click();
  await expect(details).toHaveAttribute('aria-expanded', 'false');
  await expect(transport).toBeVisible();
  await details.click();
  const playhead = transport.getByLabel(/^Playhead/);
  await playhead.fill('2.5');
  await playhead.focus();
  await page.keyboard.press('Escape');
  await expect(details).toHaveAttribute('aria-expanded', 'false');
  await expect(details).toBeFocused();
  await expect(playhead).toHaveValue('2.5');
  await expect(page.getByRole('button', { name: 'Back to editing', exact: true })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: 'Expand preview', exact: true })).toBeVisible();
});
