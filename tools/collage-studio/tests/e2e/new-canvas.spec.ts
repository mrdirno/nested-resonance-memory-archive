/**
 * NEW CANVAS — a wish, verbatim: "How to reset canvas no way to create new
 * canvas" (collage well, bug, about_tool=upload, 2026-09-07, anonymous).
 *
 * There was a way, and it was invisible: `Clear all sources`, the third row of
 * a collapsed "Project actions" disclosure at the foot of the Add panel — below
 * the fold of a pane that fits exactly three tiles on an SE, behind a word the
 * wisher never used. The fix is a "New canvas" button in the Add panel's
 * heading (no vertical cost; present whenever the panel is) that asks before
 * it clears. This gate grades what the judge panel named as WRONG IF:
 *   1. the button is on screen, inside the panel, 44px, at every screen, and
 *      the heading stays one 48px row (a wrapped heading pushes a tile under);
 *   2. one tap clears nothing — the pool is unchanged until "Start over";
 *   3. "Keep working" and Escape both put the tiles back, and Escape does not
 *      close the panel on the way;
 *   4. "Start over" empties the canvas to the start screen, drops the title's
 *      words, keeps the title's size, and never opens a browser dialog.
 *
 * Run (dev):  npx playwright test --config playwright.reachable.config.ts
 * Run (live): COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *               npx playwright test --config playwright.reachable.config.ts
 */
import { test, expect, type Page, type Locator } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const IMG_A = join(HERE, '..', 'fixtures', 'img_a.jpg');
const IMG_B = join(HERE, '..', 'fixtures', 'img_b.jpg');
const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** The same seven screens the reachable gate grades. */
const SCREENS = [
  { w: 320, h: 568 }, { w: 360, h: 640 }, { w: 375, h: 553 }, { w: 390, h: 664 },
  { w: 430, h: 740 }, { w: 844, h: 390 }, { w: 1280, h: 720 },
];

const tools = (page: Page) => page.getByRole('navigation', { name: 'Studio tools' });

/** Two photographs in and the taskbar up — cheaper than the lyric film, and enough. */
async function loadTwo(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles([IMG_A, IMG_B]);
  await expect(tools(page)).toBeVisible({ timeout: 60_000 });
  await expect(page.locator('.studio-art-band')).toBeVisible();
  await page.waitForTimeout(400);
}

async function box(l: Locator, what: string) {
  const b = await l.boundingBox();
  expect(b, `${what} must be laid out`).not.toBeNull();
  return b!;
}

function within(inner: { x: number; y: number; width: number; height: number },
                outer: { x: number; y: number; width: number; height: number }) {
  return inner.x >= outer.x - 0.5 && inner.y >= outer.y - 0.5
    && inner.x + inner.width <= outer.x + outer.width + 0.5
    && inner.y + inner.height <= outer.y + outer.height + 0.5;
}

for (const { w, h } of SCREENS) {
  test(`New canvas is in the Add panel's heading, on screen, one row, and asks first, at ${w}x${h}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: h });
    await loadTwo(page);
    const viewport = { x: 0, y: 0, width: w, height: h };

    await tools(page).getByRole('button', { name: 'Add', exact: true }).click();
    const panel = page.locator('#studio-editing-panel');
    await expect(panel).toBeVisible();
    const pb = await box(panel, 'the editing panel');

    // 1. THE BUTTON, in the heading, inside the panel and the viewport, a thumb wide.
    const heading = panel.locator('.studio-inspector-heading');
    const hb = await box(heading, 'the panel heading');
    expect(hb.height, `the heading wrapped to ${hb.height}px at ${w}`).toBeLessThanOrEqual(48.5);
    const btn = page.getByRole('button', { name: 'New canvas', exact: true });
    await expect(btn).toBeVisible();
    const bb = await box(btn, 'the New canvas button');
    expect(within(bb, pb), `New canvas ${JSON.stringify(bb)} is outside the panel ${JSON.stringify(pb)} at ${w}x${h}`).toBe(true);
    expect(within(bb, viewport), `New canvas is off screen at ${w}x${h}`).toBe(true);
    expect(bb.width, 'New canvas narrower than a thumb').toBeGreaterThanOrEqual(43.5);
    expect(bb.height, 'New canvas shorter than a thumb').toBeGreaterThanOrEqual(43.5);
    // The wisher's word is "canvas": the label shows at every width.
    const labelShown = await btn.locator('span').evaluate((el) => getComputedStyle(el).display !== 'none');
    expect(labelShown, `New canvas label hidden at ${w}`).toBe(true);
    // The heading's own title is still legible, and nothing in the row leaves the screen.
    const h2b = await box(heading.locator('h2'), 'the heading title');
    expect(h2b.width, `the heading title was crushed to ${h2b.width}px at ${w}`).toBeGreaterThanOrEqual(40);
    for (const b of await heading.locator('button').all()) {
      if (!(await b.isVisible())) continue;
      const r = await box(b, 'a heading button');
      const name = await b.getAttribute('aria-label') || await b.textContent();
      expect(r.x + r.width, `${name} runs past the right edge at ${w}`).toBeLessThanOrEqual(w + 0.5);
      expect(r.x, `${name} runs past the left edge at ${w}`).toBeGreaterThanOrEqual(-0.5);
    }
    await expect(page.getByRole('button', { name: 'Close editing panel' })).toBeVisible();

    // 2. ONE TAP CLEARS NOTHING. The question takes the tiles' place, fits the
    //    pane unscrolled, and both answers are thumbs inside it.
    await btn.click();
    await expect(page.locator('.studio-art-band'), 'the first tap cleared the canvas').toBeVisible();
    const card = panel.locator('.studio-new-canvas');
    await expect(card).toBeVisible();
    expect(await card.evaluate((el) => el.scrollTop), 'the question must start unscrolled').toBe(0);
    await expect(panel.locator('.studio-add-panel')).toHaveCount(0);
    await expect(btn, 'the button must step aside while its question is up').toHaveCount(0);
    for (const name of ['Keep working', 'Start over']) {
      const answer = page.getByRole('button', { name, exact: true });
      const ab = await box(answer, `the ${name} answer`);
      expect(within(ab, pb), `${name} ${JSON.stringify(ab)} is outside the panel at ${w}x${h}`).toBe(true);
      expect(within(ab, viewport), `${name} is off screen at ${w}x${h}`).toBe(true);
      expect(ab.height, `${name} under 44px`).toBeGreaterThanOrEqual(43.5);
    }
    await expect(page.getByRole('button', { name: 'Keep working', exact: true }), 'focus must land on the safe answer').toBeFocused();
  });
}

for (const { w, h } of [{ w: 390, h: 664 }, { w: 1280, h: 720 }]) {
  test(`Keep and Escape keep; Start over clears the words and keeps the settings, at ${w}x${h}`, async ({ page }) => {
    let dialogs = 0;
    page.on('dialog', (d) => { dialogs++; d.dismiss().catch(() => {}); });
    await page.setViewportSize({ width: w, height: h });
    await loadTwo(page);

    // A title with a size, so the words going and the size staying are both visible.
    await tools(page).getByRole('button', { name: 'Text', exact: true }).click();
    await page.getByRole('button', { name: 'Title', exact: true }).click();
    const title = page.getByPlaceholder('Say what it is');
    await title.fill('old words');
    await page.getByTestId('title-size-sm').click();
    await expect(page.getByTestId('title-size-sm')).toHaveAttribute('aria-pressed', 'true');

    const open = async () => {
      await tools(page).getByRole('button', { name: 'Add', exact: true }).click();
      await page.getByRole('button', { name: 'New canvas', exact: true }).click();
      await expect(page.getByRole('button', { name: 'Start over', exact: true })).toBeVisible();
    };

    // 3a. Keep working: tiles back, focus back on the button, canvas untouched.
    await open();
    await page.getByRole('button', { name: 'Keep working', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Start over', exact: true })).toHaveCount(0);
    await expect(page.locator('.studio-add-panel').getByRole('button', { name: 'Art Room', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'New canvas', exact: true })).toBeFocused();
    await expect(page.locator('.studio-art-band')).toBeVisible();

    // 3b. Escape does the same and leaves the panel open.
    await page.getByRole('button', { name: 'New canvas', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Start over', exact: true })).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('button', { name: 'Start over', exact: true })).toHaveCount(0);
    await expect(page.locator('#studio-editing-panel'), 'Escape closed the panel instead of the question').toBeVisible();
    await expect(page.locator('.studio-art-band')).toBeVisible();

    // 4. Start over: the start screen, no taskbar, the topbar back to its empty
    //    state, a status line that promises nothing it cannot do, no dialog.
    await page.getByRole('button', { name: 'New canvas', exact: true }).click();
    await page.getByRole('button', { name: 'Start over', exact: true }).click();
    await expect(page.locator('.studio-start')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Start a new piece' })).toBeVisible();
    await expect(page.locator('.studio-art-band')).toHaveCount(0);
    await expect(tools(page)).toHaveCount(0);
    await expect(page.locator('#studio-editing-panel')).toBeHidden();
    await expect(page.locator('header')).toHaveAttribute('data-loaded', 'false');
    const status = page.getByRole('status');
    await expect(status).toContainText(/fresh canvas/i);
    await expect(status).not.toContainText(/undo|restore/i);
    expect(dialogs, 'a browser dialog opened').toBe(0);

    // The next piece starts without the old words and with the old size.
    await page.locator('input[type="file"]').first().setInputFiles([IMG_A]);
    await expect(tools(page)).toBeVisible({ timeout: 60_000 });
    await tools(page).getByRole('button', { name: 'Text', exact: true }).click();
    await page.getByRole('button', { name: 'Title', exact: true }).click();
    await expect(page.getByPlaceholder('Say what it is')).toHaveValue('');
    await page.getByPlaceholder('Say what it is').fill('new words');
    await expect(page.getByTestId('title-size-sm')).toHaveAttribute('aria-pressed', 'true');
  });
}
