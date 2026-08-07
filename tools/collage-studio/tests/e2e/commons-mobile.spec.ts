/**
 * THE COMMONS IS MOBILE-WATERTIGHT, AND IT ACTUALLY DOES THE JOB — a ship gate.
 *
 * Operator law (2026-08-04): "must be mobile friendly always — don't make
 * anything that's gonna clip or alter if zoomed out on phone." The commons is
 * read one-handed, standing up, by somebody deciding what to throw in the bag.
 *
 * WHY IT ALSO EXERCISES THE JOB. The gate that shipped before this one measured
 * the app with no video loaded and therefore graded a transport that did not
 * exist — eleven controls under 44px hid behind that for weeks. So this one
 * ticks real gear, filters to a real trade, and reads the COPIED TEXT back,
 * because a page that renders perfectly and hands you the wrong list is a page
 * that failed.
 *
 * Serve the repo root and point at it:
 *   python3 -m http.server 8765     (from the repo root)
 *   npx playwright test --config playwright.commons.config.ts
 *
 * Against production:
 *   COMMONS_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/ \
 *     npx playwright test --config playwright.commons.config.ts
 */
import { test, expect, type Page } from '@playwright/test';

// RELATIVE, deliberately — the deployed site lives under a repo path
// (/nested-resonance-memory-archive/) and a leading slash resolves against the
// ORIGIN, silently dropping that prefix and 404ing every live run.
const PATH = 'commons/';
const WIDTHS = [320, 360, 390, 430];

interface Probe {
  under44: { t: string; h: number }[];
  docOverflowX: number;
  clipped: { t: string; cls: string; right: number }[];
  dockCovers: boolean;
}

/** Everything the operator's law actually asserts, read out of the layout engine. */
const probe = (page: Page): Promise<Probe> =>
  page.evaluate(() => {
    const doc = document.documentElement;

    const visible = (e: Element) => (e as HTMLElement).offsetParent !== null;

    // Every interactive control, not a hand-picked subset — the previous gate's
    // whole failure was grading a subset.
    const under44 = [...document.querySelectorAll('button,input,select,textarea,a[href]')]
      .filter(visible)
      .map((e) => {
        const r = e.getBoundingClientRect();
        // A checkbox's tap target is its label, which is what a thumb hits.
        const lab = e.closest('label');
        const h = lab ? lab.getBoundingClientRect().height : r.height;
        return { t: (e.textContent || (e as HTMLInputElement).name || e.tagName).trim().slice(0, 26), h: Math.round(h) };
      })
      .filter((o) => o.h < 44);

    const clipped: { t: string; cls: string; right: number }[] = [];
    document.querySelectorAll('*').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.right > doc.clientWidth + 1) {
        clipped.push({
          t: (el.textContent || '').trim().slice(0, 24),
          cls: String((el as HTMLElement).className).slice(0, 40),
          right: Math.round(r.right),
        });
      }
    });

    // The sticky dock must never sit on top of the last row of content.
    const dock = document.querySelector('.dock') as HTMLElement | null;
    const items = [...document.querySelectorAll('.item')];
    const last = items[items.length - 1];
    let dockCovers = false;
    if (dock && last) {
      window.scrollTo(0, document.body.scrollHeight);
      const d = dock.getBoundingClientRect();
      const l = last.getBoundingClientRect();
      dockCovers = l.bottom > d.top;
      window.scrollTo(0, 0);
    }

    return { under44, docOverflowX: doc.scrollWidth - doc.clientWidth, clipped, dockCovers };
  });

test.describe('the commons is watertight on a phone', () => {
  for (const width of WIDTHS) {
    test(`${width}px: 44px targets, zero horizontal overflow, nothing clipped`, async ({ page }) => {
      await page.setViewportSize({ width, height: 780 });
      await page.goto(PATH);
      await expect(page.locator('.item').first()).toBeVisible({ timeout: 10_000 });

      const home = await probe(page);
      expect(home.docOverflowX, `document scrolls sideways at ${width}`).toBe(0);
      expect(home.clipped, `elements past the right edge at ${width}`).toEqual([]);
      expect(home.under44, `controls under 44px at ${width}`).toEqual([]);
      expect(home.dockCovers, 'the dock covers the last row').toBe(false);

      // ...and again with a trade selected, which adds a whole second section.
      await page.locator('.chip', { hasText: 'HVAC/R' }).click();
      await expect(page.locator('.sec')).toHaveCount(2);
      const filtered = await probe(page);
      expect(filtered.docOverflowX, `overflow with a trade open at ${width}`).toBe(0);
      expect(filtered.clipped, `clipping with a trade open at ${width}`).toEqual([]);
      expect(filtered.under44, `controls under 44px with a trade open at ${width}`).toEqual([]);
    });
  }

  test('320px with the OS text size bumped up still does not clip', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 780 });
    await page.goto(PATH);
    await expect(page.locator('.item').first()).toBeVisible();
    // The narrowest phone AND a user who cannot read 14px. Both at once is the
    // real worst case, and "zoomed out" in the operator's words is the same
    // failure mode: content that stops fitting its box.
    await page.addStyleTag({ content: 'html{font-size:22px}' });
    await page.locator('.chip', { hasText: 'Low-voltage' }).click();
    const p = await probe(page);
    expect(p.docOverflowX, 'sideways scroll at 320px / 22px root').toBe(0);
    expect(p.clipped, 'clipped elements at 320px / 22px root').toEqual([]);
  });
});

test.describe('the commons does the job it claims', () => {
  test.use({ permissions: ['clipboard-read', 'clipboard-write'] });

  test('the universal floor is always shown, and a trade adds to it', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PATH);

    // The whole thesis: a plumber who only sees plumbing gear learned nothing,
    // so the shared floor is never filtered away.
    await expect(page.locator('.sec')).toHaveCount(1);
    const floor = await page.locator('.sec').first().locator('.item').count();
    expect(floor).toBeGreaterThan(8);

    await page.locator('.chip', { hasText: 'Plumbing' }).click();
    await expect(page.locator('.sec')).toHaveCount(2);
    const stillFloor = await page.locator('.sec').first().locator('.item').count();
    expect(stillFloor, 'the universal floor survived the filter').toBe(floor);

    // ...and the trade section holds only that trade's gear, never universal.
    const second = page.locator('.sec').nth(1);
    await expect(second.locator('.item').first()).toBeVisible();
    expect(await second.locator('.item').count()).toBeGreaterThan(5);
  });

  test('ticking gear builds a bag and copies a list somebody can actually send', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PATH);
    await page.locator('.chip', { hasText: 'Electrical' }).click();

    await expect(page.locator('#copy')).toBeDisabled();

    // One from the shared floor, one from the trade — so the copied list has to
    // carry both headings, which is where a lazy implementation gets it wrong.
    const floorItem = page.locator('.sec').first().locator('.item').first();
    const tradeItem = page.locator('.sec').nth(1).locator('.item').first();
    const floorName = (await floorItem.locator('.nm').textContent())!.trim();
    const tradeName = (await tradeItem.locator('.nm').textContent())!.trim();

    await floorItem.locator('label').click();
    await tradeItem.locator('label').click();

    await expect(page.locator('#cnt')).toHaveText('2');
    await expect(page.locator('#copy')).toBeEnabled();

    await page.locator('#copy').click();
    const copied = await page.evaluate(() => navigator.clipboard.readText());

    expect(copied).toContain(floorName);
    expect(copied).toContain(tradeName);
    expect(copied).toContain('EVERY TRADE');
    expect(copied).toContain('ELECTRICAL');
    expect(copied).toMatch(/2 items/);
    // No brand, no price, no affiliate anything — the reason the page exists.
    expect(copied).not.toMatch(/https?:\/\//);
  });

  test('the bag survives a reload, because a bag you retype is not a bag', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PATH);
    await page.locator('.item').first().locator('label').click();
    await expect(page.locator('#cnt')).toHaveText('1');

    await page.reload();
    await expect(page.locator('#cnt')).toHaveText('1');
    await expect(page.locator('.item').first().locator('input')).toBeChecked();

    await page.locator('#clr').click();
    await expect(page.locator('#cnt')).toHaveText('0');
    await page.reload();
    await expect(page.locator('#cnt')).toHaveText('0');
  });

  test('the way to correct the list is on the page and opens', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PATH);
    // COMMONS is community-fed or it is just our opinion. The well must open
    // even with placeholder Supabase config (a local or preview copy), because
    // a hard failure here is a silent loss of the only correction path.
    await page.locator('#addbtn').click();
    await expect(page.locator('.fb-sheet, .fb-form, [role="dialog"]').first()).toBeVisible({ timeout: 5_000 });
  });

  test('no page error, and the data file actually loaded', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PATH);
    await expect(page.locator('.item').first()).toBeVisible();

    const n = await page.evaluate(() => (window as unknown as { COMMONS_GEAR: unknown[] }).COMMONS_GEAR.length);
    expect(n, 'an empty commons is not a commons').toBeGreaterThanOrEqual(20);
    expect(errors, 'console/page errors').toEqual([]);
  });
});
