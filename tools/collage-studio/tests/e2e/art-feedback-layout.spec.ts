// Author: Aldrin Payopay · GPL-3.0-only
// T-18986: real feedback must not resize the artwork or move its controls.
// Run with --project=chromium --workers=1 (the project mutes device output).
import { test, expect, type Locator, type Page } from '@playwright/test';

test.setTimeout(120_000);
test.use({ actionTimeout: 15_000 });
const URL = process.env.COLLAGE_BASE_URL || '/';
const VIEWPORTS = [
  { width: 1280, height: 720 }, { width: 844, height: 390 },
  { width: 320, height: 664 }, { width: 390, height: 844 },
  { width: 320, height: 448 },
];
const DICED = 'Unlocked, enabled layers in this art composition rolled.';
const UNDONE = 'Undid: Dice art.';
const INVALID = 'This art recipe version is not supported.';
const PREVIEW_DICED = 'Preview variation rolled. Kept layers are unchanged.';
const APPLIED = 'Editable artwork applied. Keep layering here, or close to arrange and export in Studio.';
const status = (room: Locator) => room.locator('.art-footer [role=status]');
const alert = (room: Locator) => room.locator('.art-footer [role=alert]');
const feedback = (room: Locator) => room.locator('.art-feedback');

async function openRoom(page: Page) {
  await page.goto(URL);
  const entry = page.getByRole('button', { name: 'Art Room', exact: true });
  if (!await entry.isVisible()) await page.getByRole('button', { name: 'Add', exact: true }).click();
  await entry.click();
  const room = page.getByTestId('art-rack');
  await expect(room).toBeVisible();
  const pause = room.getByRole('button', { name: 'Pause art preview', exact: true });
  if (await pause.isVisible()) await pause.click();
  await room.getByLabel('Art playhead', { exact: true }).fill('2.25');
  await expect(room.locator('.art-transport output')).toHaveText('2.3 / 8s');
  return room;
}

async function geometry(room: Locator) {
  await room.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
  return room.evaluate(element => {
    const rect = (selector: string) => {
      const target = element.querySelector(selector)!;
      const b = target.getBoundingClientRect();
      return { x: b.x, y: b.y, width: b.width, height: b.height };
    };
    const canvas = element.querySelector<HTMLCanvasElement>('canvas[aria-label="Animated art preview"]')!;
    const b = canvas.getBoundingClientRect(), ratio = canvas.width / canvas.height;
    const width = Math.min(b.width, b.height * ratio), height = width / ratio;
    return {
      // object-fit:contain leaves letterboxing: measure the actual fitted image.
      artwork: { x: b.x + (b.width - width) / 2, y: b.y + (b.height - height) / 2, width, height },
      canvas: rect('canvas[aria-label="Animated art preview"]'),
      transport: rect('.art-transport'),
      play: rect('.art-transport button'),
      seek: rect('input[aria-label="Art playhead"]'),
      time: rect('.art-transport output'),
      footer: rect('.art-footer'),
      dice: rect('.art-dice-controls'),
      apply: rect('.art-apply'),
    };
  });
}
type Geometry = Awaited<ReturnType<typeof geometry>>;

async function stable(room: Locator, before: Geometry, label: string) {
  const after = await geometry(room);
  for (const part of Object.keys(before) as (keyof Geometry)[]) {
    for (const axis of ['x', 'y', 'width', 'height'] as const) {
      expect(Math.abs(after[part][axis] - before[part][axis]),
        `${label}: ${part}.${axis}, before=${before[part][axis]}, after=${after[part][axis]}`).toBeLessThanOrEqual(1);
    }
  }
  return after;
}

async function controlsFit(room: Locator, viewport: { width: number; height: number }) {
  const frame = await geometry(room);
  for (const [name, b] of Object.entries(frame)) {
    expect(b.x, `${name} left`).toBeGreaterThanOrEqual(-1);
    expect(b.y, `${name} top`).toBeGreaterThanOrEqual(-1);
    expect(b.x + b.width, `${name} right`).toBeLessThanOrEqual(viewport.width + 1);
    expect(b.y + b.height, `${name} bottom`).toBeLessThanOrEqual(viewport.height + 1);
  }
  await expect(room.getByLabel('Animated art preview', { exact: true })).toHaveCSS('object-fit', 'contain');
  for (const control of [room.locator('.art-transport button'), room.locator('.art-dice-controls button').first(), room.locator('.art-apply')]) {
    const b = await control.evaluate(e => {
      const r = e.getBoundingClientRect(), hit = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
      return { width: r.width, height: r.height, hit: hit === e || e.contains(hit) };
    });
    expect(b.width).toBeGreaterThanOrEqual(43.5);
    expect(b.height).toBeGreaterThanOrEqual(43.5);
    expect(b.hit, 'control center is unobstructed without scrolling it into view').toBe(true);
  }
  // Keep the established small-screen stage floor, including its fitted image.
  if (viewport.width === 320) {
    const minimum = viewport.height === 448 ? 60 : 140;
    expect(frame.canvas.height).toBeGreaterThanOrEqual(minimum);
    expect(frame.artwork.height).toBeGreaterThanOrEqual(minimum);
  }
}

async function readableFeedback(room: Locator, message: string, role: 'status' | 'alert') {
  await expect(role === 'status' ? status(room) : alert(room)).toHaveText(message);
  await expect(role === 'status' ? alert(room) : status(room)).toHaveCount(0);
  const slot = feedback(room);
  await expect(slot).toBeVisible();
  await expect(slot).toHaveAttribute('tabindex', '0');
  await expect(slot).toHaveAttribute('aria-label', 'Art Room feedback');
  expect(await slot.textContent()).toBe(message); // no truncation of the accessible message
}

async function emptyFeedback(room: Locator) {
  await expect(status(room)).toHaveCount(0);
  await expect(alert(room)).toHaveCount(0);
  await expect(feedback(room)).toBeVisible();
  await expect(feedback(room)).toHaveText('');
  expect(await feedback(room).getAttribute('tabindex')).toBeNull();
}

async function invalidRecipe(room: Locator) {
  await room.getByLabel('Open art recipe', { exact: true }).setInputFiles({
    name: 'unsupported-art-recipe.json', mimeType: 'application/json', buffer: Buffer.from('{}'),
  });
  await expect(alert(room)).toHaveText(INVALID);
}

test.afterEach(async ({ page }, info) => {
  if (info.status !== info.expectedStatus) await page.screenshot({ path: info.outputPath('feedback-layout-failure.png') });
});

for (const expanded of [false, true]) {
  test(`${expanded ? 'expanded preview' : 'editing'} keeps artwork and controls still through Dice, Undo and real recipe errors`, async ({ page }, info) => {
    const errors: string[] = [];
    page.on('pageerror', e => errors.push(e.message));
    for (const viewport of VIEWPORTS) {
      await test.step(`${viewport.width} × ${viewport.height}`, async () => {
        await page.setViewportSize(viewport);
        const room = await openRoom(page);
        if (expanded) await room.getByRole('button', { name: 'Expand art preview', exact: true }).click();
        await expect(status(room)).toHaveCount(0);
        await expect(alert(room)).toHaveCount(0);
        const empty = await geometry(room);
        // This is deliberately the first regression assertion on the old public
        // build. A missing new feedback class is not evidence of a layout jump.
        await room.getByRole('button', { name: 'Dice art', exact: true }).click();
        await expect(status(room)).toHaveText(DICED);
        await stable(room, empty, 'empty → Dice notice');
        await readableFeedback(room, DICED, 'status');
        if (expanded) await page.keyboard.press('Control+z');
        else await room.getByRole('button', { name: 'Undo art edit', exact: true }).click();
        await expect(status(room)).toHaveText(UNDONE);
        await stable(room, empty, 'Dice → Undo notice');
        await readableFeedback(room, UNDONE, 'status');
        await invalidRecipe(room);
        await stable(room, empty, 'Undo notice → invalid recipe alert');
        await readableFeedback(room, INVALID, 'alert');
        await controlsFit(room, viewport);
        await expect(room.getByLabel('Art playhead', { exact: true })).toHaveValue('2.25');

        if (!expanded) {
          // Entering audition changes the available actions, so take a new
          // baseline. Choosing this same preview again clears its Dice notice
          // without entering/leaving audition or changing the room mode.
          const preview = room.getByRole('button', { name: 'Preview Knot Foundry', exact: true });
          await preview.click();
          await expect(room.getByTestId('art-audition')).toBeVisible();
          await emptyFeedback(room);
          const auditionEmpty = await geometry(room);
          await room.getByRole('button', { name: 'Dice preview', exact: true }).click();
          await expect(status(room)).toHaveText(PREVIEW_DICED);
          await stable(room, auditionEmpty, 'empty audition → Dice preview notice');
          await readableFeedback(room, PREVIEW_DICED, 'status');
          await preview.click();
          await emptyFeedback(room);
          await stable(room, auditionEmpty, 'Dice preview notice → cleared through preview');
          await controlsFit(room, viewport);
        }
        await page.screenshot({ path: info.outputPath(`feedback-${expanded ? 'expanded' : 'editing'}-${viewport.width}-${viewport.height}.png`) });
      });
    }
    expect(errors).toEqual([]);
  });
}

test('real Apply feedback at 150% text remains complete and keyboard scrollable without moving the preview', async ({ page }, info) => {
  await page.setViewportSize({ width: 320, height: 664 });
  const room = await openRoom(page);
  // The ordinary Apply message fits the default two-line slot. Exercise a real
  // enlarged-text accessibility condition; feedback content and actions remain
  // entirely application-produced. The other two tests use default typography.
  await page.addStyleTag({ content: '.art-feedback{font-size:16.5px}' });
  await room.getByRole('button', { name: 'Use in Studio', exact: true }).click();
  await expect(status(room)).toHaveText(APPLIED, { timeout: 30_000 });
  // Apply changes the button from Use to Update. Measure once that authored
  // source transition has finished, then compare notices with the same action.
  await expect(room.getByRole('button', { name: 'Update in Studio', exact: true })).toBeEnabled();
  const applied = await geometry(room);
  await readableFeedback(room, APPLIED, 'status');
  const slot = feedback(room);
  await room.getByRole('button', { name: /^Dice layer/ }).focus();
  await page.keyboard.press('Tab');
  await expect(slot).toBeFocused();
  const scroll = await slot.evaluate(e => ({ top: e.scrollTop, max: e.scrollHeight - e.clientHeight }));
  expect(scroll.max, 'the real Apply message at 150% text overflows the two-line 320px slot').toBeGreaterThan(0);
  await page.keyboard.press('End');
  await expect.poll(() => slot.evaluate(e => e.scrollTop)).toBeGreaterThan(scroll.top);
  expect(await slot.textContent()).toBe(APPLIED);
  await stable(room, applied, 'keyboard scroll within feedback');
  await page.keyboard.press('Home');
  await expect.poll(() => slot.evaluate(e => e.scrollTop)).toBe(0);
  await room.getByRole('button', { name: 'Dice art', exact: true }).click();
  await expect(status(room)).toHaveText(DICED);
  await stable(room, applied, 'long Apply notice → short Dice notice');
  await room.getByRole('button', { name: 'Undo art edit', exact: true }).click();
  await expect(status(room)).toHaveText(UNDONE);
  await stable(room, applied, 'long Apply notice → Undo notice');
  await invalidRecipe(room);
  await readableFeedback(room, INVALID, 'alert');
  await stable(room, applied, 'long Apply notice → real recipe alert');
  await controlsFit(room, { width: 320, height: 664 });
  await page.screenshot({ path: info.outputPath('feedback-keyboard-320-664.png') });
});
