/**
 * REACHABLE CONTROLS — a wish, verbatim: "wish it better is gone … also the add
 * audio and aspect ratio are not visible" (collage well, 2026-09-06, anonymous).
 *
 * All three were true, and measured on the live site before the fix:
 *   - the topbar Feedback trigger was guarded on `!hasImages` (C3712), so it
 *     vanished the moment a project loaded — on every viewport, desktop too;
 *   - "Add music" was the third 76px tile of a panel with 279px on an iPhone 12
 *     and 232px on an SE: clipped on the first, eight pixels tall on the second;
 *   - the aspect picker sat ~1250px down a pane whose visible height is 178px
 *     on a phone, under a tab called "Canvas & crop".
 *
 * This gate reads those three back out of the layout engine in the LOADED state
 * — the state the earlier gates never graded, because they imported files and
 * then only measured the empty topbar. A control counts as on screen when its
 * box is inside its pane's box with the pane unscrolled, and inside the viewport.
 *
 * Run (dev):  npx playwright test --config playwright.reachable.config.ts
 * Run (live): COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *               npx playwright test --config playwright.reachable.config.ts
 */
import { test, expect, type Page, type Locator } from '@playwright/test';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/** The screens that matter: four phone widths, an SE with Safari's chrome up,
 *  a phone on its side, and a laptop. Heights are what the browser reports. */
const SCREENS = [
  { w: 320, h: 568 }, { w: 360, h: 640 }, { w: 375, h: 553 }, { w: 390, h: 664 },
  { w: 430, h: 740 }, { w: 844, h: 390 }, { w: 1280, h: 720 },
];

async function loadSample(page: Page) {
  await page.goto(APP_URL);
  await page.getByRole('button', { name: 'Try a lyric film' }).click();
  await expect(page.getByRole('navigation', { name: 'Studio tools' })).toBeVisible({ timeout: 90_000 });
  await page.waitForTimeout(400);
}

/** A box, or a failure that names what was missing. */
async function box(l: Locator, what: string) {
  const b = await l.boundingBox();
  expect(b, `${what} must be laid out`).not.toBeNull();
  return b!;
}

/** Inside another box, with a half-pixel of tolerance for subpixel layout. */
function within(inner: { x: number; y: number; width: number; height: number },
                outer: { x: number; y: number; width: number; height: number }) {
  return inner.x >= outer.x - 0.5 && inner.y >= outer.y - 0.5
    && inner.x + inner.width <= outer.x + outer.width + 0.5
    && inner.y + inner.height <= outer.y + outer.height + 0.5;
}

for (const { w, h } of SCREENS) {
  test(`wish, Add music and the frame's shape are on screen once a project is loaded, at ${w}x${h}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: h });
    await loadSample(page);
    const viewport = { x: 0, y: 0, width: w, height: h };

    // 1. THE WELL, in the topbar, in the loaded state — the thing that was gone.
    const wish = page.locator('header [data-wish-well]');
    await expect(wish, 'the wish-it-better trigger must be in the topbar with a project loaded').toBeVisible();
    const wb = await box(wish, 'the topbar wish trigger');
    expect(within(wb, viewport), `wish trigger ${JSON.stringify(wb)} is off screen at ${w}`).toBe(true);
    expect(wb.width, 'wish trigger narrower than a thumb').toBeGreaterThanOrEqual(43.5);
    expect(wb.height, 'wish trigger shorter than a thumb').toBeGreaterThanOrEqual(43.5);
    // The wisher missed the WORD. It shows from 360 up; under that the row
    // cannot pay for it and the icon stands alone.
    const labelShown = await wish.locator('span').evaluate((el) => getComputedStyle(el).display !== 'none');
    expect(labelShown, `wish label ${labelShown ? 'shown' : 'hidden'} at ${w}`).toBe(w >= 360);

    // Nothing in the row may be pushed past the edge: the shell is
    // `fixed inset-0; overflow: hidden`, so those pixels are destroyed, not
    // scrolled, and a document-width check reads clean while a button is gone.
    for (const btn of await page.locator('header button').all()) {
      const b = await box(btn, 'a topbar button');
      const name = await btn.getAttribute('aria-label') || await btn.textContent();
      expect(b.x + b.width, `${name} runs past the right edge at ${w}`).toBeLessThanOrEqual(w + 0.5);
      expect(b.x, `${name} runs past the left edge at ${w}`).toBeGreaterThanOrEqual(-0.5);
      expect(b.width, `${name} under 44px wide at ${w}`).toBeGreaterThanOrEqual(43.5);
      expect(b.height, `${name} under 44px tall at ${w}`).toBeGreaterThanOrEqual(43.5);
    }
    // Open keeps its name when it loses its label.
    await expect(page.getByRole('button', { name: 'Open', exact: true })).toBeVisible();

    // 2. ADD MUSIC, inside the Add panel's own box, panel unscrolled.
    await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Add', exact: true }).click();
    const panel = page.locator('#studio-editing-panel');
    await expect(panel).toBeVisible();
    const pb = await box(panel, 'the editing panel');
    const addPanel = page.locator('.studio-add-panel');
    expect(await addPanel.evaluate((el) => el.scrollTop), 'the Add panel must start unscrolled').toBe(0);
    for (const name of ['Art Room', 'Add more images or video', /music/i]) {
      const tile = addPanel.getByRole('button', { name, exact: typeof name === 'string' });
      const tb = await box(tile, `the ${String(name)} tile`);
      expect(within(tb, pb), `${String(name)} tile ${JSON.stringify(tb)} is outside the panel ${JSON.stringify(pb)} at ${w}x${h}`).toBe(true);
      expect(within(tb, viewport), `${String(name)} tile is off screen at ${w}x${h}`).toBe(true);
      expect(tb.height, `${String(name)} tile under 44px`).toBeGreaterThanOrEqual(43.5);
    }

    // 3. THE FRAME'S SHAPE, first row of the tab that is named for it.
    await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Layout', exact: true }).click();
    await page.getByRole('button', { name: 'Canvas & crop', exact: true }).click();
    const dock = page.locator('.studio-controls-panel:not([hidden]) .ui-dock');
    await expect(dock).toBeVisible();
    expect(await dock.evaluate((el) => el.scrollTop), 'the Canvas & crop pane must start unscrolled').toBe(0);
    const db = await box(dock, 'the Canvas & crop pane');
    const ratios = dock.locator('.ui-ratio');
    await expect(ratios).toHaveCount(4);
    for (const r of await ratios.all()) {
      const rb = await box(r, 'an aspect button');
      const label = (await r.textContent() || '').trim();
      expect(within(rb, db), `aspect ${label} ${JSON.stringify(rb)} sits outside the visible pane ${JSON.stringify(db)} at ${w}x${h}`).toBe(true);
      expect(within(rb, viewport), `aspect ${label} is off screen at ${w}x${h}`).toBe(true);
      expect(rb.height, `aspect ${label} under 44px`).toBeGreaterThanOrEqual(43.5);
    }
  });
}

/**
 * THE TOPBAR IS NOT EVERY SURFACE. Under 550px tall and 700px wide the topbar
 * and taskbar hide while an editor is open (the C3712 short-screen rule), so a
 * topbar-only trigger is gone in exactly the state a person edits in. The panel
 * heading is the one row present whenever an editor is open; the well rides it
 * there, and only there — one visible trigger at a time.
 */
test('while editing on a short screen the well rides the panel heading (360x448)', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 448 });
  await loadSample(page);
  // Not editing: the topbar carries it, the heading does not.
  await expect(page.locator('header [data-wish-well]')).toBeVisible();
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Add', exact: true }).click();
  await expect(page.locator('#studio-editing-panel')).toBeVisible();
  // Editing: the topbar is gone, so the heading's trigger must be the one on screen.
  await expect(page.locator('header')).toBeHidden();
  const wish = page.locator('#studio-editing-panel .studio-inspector-heading [data-wish-well]');
  await expect(wish).toBeVisible();
  const wb = await box(wish, 'the heading wish trigger');
  expect(within(wb, { x: 0, y: 0, width: 360, height: 448 }), `heading wish trigger ${JSON.stringify(wb)} is off screen`).toBe(true);
  expect(wb.width).toBeGreaterThanOrEqual(43.5);
  expect(wb.height).toBeGreaterThanOrEqual(43.5);
  // Done is still there beside it: the way out was not paid for with the way in.
  await expect(page.getByRole('button', { name: 'Close editing panel' })).toBeVisible();
  // Leaving the editor hands the trigger back to the topbar; the heading's hides.
  await page.getByRole('button', { name: 'Close editing panel' }).click();
  await expect(page.locator('header [data-wish-well]')).toBeVisible();
});

/**
 * THE WELL OPENS. `../shared/feedback.js` only exists on the deployed site (in
 * dev it 404s and the button does nothing), so this case grades the live
 * release and skips itself where there is no well to open.
 */
test('the wish trigger opens the shared well from the loaded state', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 664 });
  await loadSample(page);
  const hasWell = await page.evaluate(() => typeof (window as any).Feedback?.open === 'function');
  test.skip(!hasWell, 'no shared/feedback.js on this origin (dev server) — graded on the live site');
  await page.locator('header [data-wish-well]').click();
  await expect(page.getByRole('dialog', { name: 'Send feedback' })).toBeVisible();
});
