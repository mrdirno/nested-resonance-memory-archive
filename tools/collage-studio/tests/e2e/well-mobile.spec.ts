/**
 * THE WELL IS MOBILE-WATERTIGHT — a ship gate for the shared wishing well that
 * every trade runs (shared/toolkit.js), asserted at real phone viewports.
 *
 * WHY IT EXISTS
 *   Wish d88093af arrived with a second complaint riding on it: "your
 *   something's broken or feedback stuff is too long it's cumbersome." Driving
 *   the real form turned up more than length — every control in it was under
 *   the 44px minimum: 37px inputs, 39px selects, 31px identity buttons and an
 *   18px "Cancel", on all six trades at once, because they share one file.
 *
 *   The well is where this program's entire demand signal comes from. A form
 *   that is painful on a phone in a hallway is a form that does not get filled
 *   in, and nothing downstream can recover a wish that was never sent. So the
 *   size of its controls is a gate, not a preference.
 *
 * Serve the repo root and point at it:
 *   python3 -m http.server 8899   (from the repo root)
 *   npx playwright test --config playwright.well-mobile.config.ts
 */
import { test, expect, type Page } from '@playwright/test';

const TRADE_PATHS = ['/av/index.html', '/plumbing/index.html', '/electrical/index.html'];
const WIDTHS = [320, 360, 390, 430];

/** Open the well and expand the optional block, so BOTH states get measured. */
async function openWell(page: Page, expand: boolean) {
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(
      (x) => /wish/i.test(x.textContent || '') && !x.classList.contains('av-idbtn'),
    ) as HTMLButtonElement | undefined;
    b?.click();
  });
  await expect(page.locator('.av-form')).toBeVisible({ timeout: 10_000 });
  if (expand) {
    await page.locator('.av-more-t').click();
    await expect(page.locator('.av-more')).toBeVisible();
  }
}

interface Probe { under44: { t: string; h: number }[]; docOverflowX: number; sheetOverflowX: number }

const probe = (page: Page): Promise<Probe> =>
  page.evaluate(() => {
    const under44 = [...document.querySelectorAll('.av-form button,.av-form input,.av-form select,.av-form textarea')]
      .filter((e) => (e as HTMLElement).offsetParent !== null && !e.closest('.av-hp'))
      .map((e) => ({ t: (e.textContent || (e as HTMLInputElement).name || '').trim().slice(0, 22), h: Math.round(e.getBoundingClientRect().height) }))
      .filter((o) => o.h < 44);
    const s = document.querySelector('.av-sheet');
    return {
      under44,
      docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      sheetOverflowX: s ? s.scrollWidth - s.clientWidth : 0,
    };
  });

for (const path of TRADE_PATHS) {
  test.describe(`wishing well is watertight — ${path}`, () => {
    for (const width of WIDTHS) {
      test(`${width}px: 44px targets, zero horizontal overflow`, async ({ page }) => {
        await page.setViewportSize({ width, height: 780 });
        await page.goto(path);
        await openWell(page, false);

        const closed = await probe(page);
        expect(closed.under44, `controls under 44px at ${width} (fold closed)`).toEqual([]);
        expect(closed.docOverflowX, 'document scrolls sideways').toBe(0);
        expect(closed.sheetOverflowX, 'sheet scrolls sideways').toBe(0);

        await page.locator('.av-more-t').click();
        const open = await probe(page);
        expect(open.under44, `controls under 44px at ${width} (fold open)`).toEqual([]);
        expect(open.docOverflowX).toBe(0);
        expect(open.sheetOverflowX).toBe(0);
      });
    }

    test('the fast path is short: Send is reachable without hunting', async ({ page }) => {
      await page.setViewportSize({ width: 390, height: 844 });
      await page.goto(path);
      await openWell(page, false);

      // The optional block starts COLLAPSED — that is the whole fix. If a future
      // edit expands it by default, the form is long again and this fails.
      await expect(page.locator('.av-more')).toBeHidden();
      await expect(page.locator('.av-more-t')).toBeVisible();

      // On the bug path — the one the operator was actually on — Send must sit
      // within the first screen. It was previously below six optional groups.
      await page.evaluate(() => {
        const b = [...document.querySelectorAll('.av-idbtn')].find((x) => /wrong|broken/i.test(x.textContent || '')) as HTMLButtonElement | undefined;
        b?.click();
      });
      const sendTop = await page.locator('.av-send').evaluate((e) => e.getBoundingClientRect().top);
      expect(sendTop).toBeLessThanOrEqual(844);

      // NOTHING was removed to achieve that — every field still exists, folded.
      await page.locator('.av-more-t').click();
      const names = await page.evaluate(() =>
        [...document.querySelectorAll('.av-form [name]')].map((e) => (e as HTMLInputElement).name));
      for (const required of ['tool_title', 'tool_purpose', 'requester_name', 'requester_company', 'requester_role', 'example', 'contact']) {
        expect(names, `${required} must survive the fold`).toContain(required);
      }
    });
  });
}
