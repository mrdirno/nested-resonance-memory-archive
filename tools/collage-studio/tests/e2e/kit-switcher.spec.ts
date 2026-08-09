/**
 * THE KIT SWITCHER IS WATERTIGHT — a ship gate for the one control whose entire
 * job is moving a tradesperson between kits (shared/toolkit.js).
 *
 * WHY IT EXISTS
 *   The cross-trade links rendered as 10.5px uppercase words in the hub footer.
 *   MEASURED on all six LIVE hubs at 320/360/390/430 before this gate existed:
 *   16.7px tall, 7-8 of them per page, 100% under the 44px law — on the control
 *   a crew uses to get from their kit to the one next to them on the job.
 *
 *   And it was worse than a tap target. The switcher existed on the SIX HUBS
 *   ONLY. From any of the 26 TOOL pages there was no route to another kit at
 *   all: the nav dropdown that every page of every trade carries listed that
 *   trade's own tools and nothing else. Six pages out of thirty-two could reach
 *   the rest of the program.
 *
 *   The renderer was also pasted into each hub — six copies of one function,
 *   which is exactly how /plumbing/ once shipped reachable from nowhere. The
 *   runtime owns it now, so a seventh trade is one line in TRADES and appears
 *   in both mounts on every page.
 *
 * Serve the repo root and point at it:
 *   python3 -m http.server 8899   (from the repo root)
 *   npx playwright test --config playwright.kit-switcher.config.ts
 * Against production:
 *   KIT_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/ \
 *     npx playwright test --config playwright.kit-switcher.config.ts
 */
import { test, expect, type Page } from '@playwright/test';

// RELATIVE, deliberately. The deployed site lives under a repo path
// (/nested-resonance-memory-archive/) and a leading slash resolves against the
// ORIGIN — silently dropping the prefix and 404ing every live run.
const TRADES = ['av', 'plumbing', 'electrical', 'hvac', 'gc', 'low-voltage', 'framing'];
// One real tool page per trade — the half of the site that had no route out.
const TOOLPAGE: Record<string, string> = {
  av: 'consumables.html',
  plumbing: 'rough-in-request.html',
  electrical: 'pull-list.html',
  hvac: 'repair-recommendation.html',
  gc: 'weather-day.html',
  'low-voltage': 'device-checkout.html',
  // Trade #7's signature tool — the backing ledger, and the ANSWER to the ask
  // five of the six trades above already send at this crew.
  framing: 'whats-in-the-wall.html',
};
const WIDTHS = [320, 360, 390, 430];
const MIN_TAP = 44;

/* HOW MANY CHIPS SHOULD BE THERE, derived from TRADES above so that standing up
 * the next trade is still one line. The HUB renders everyone-who-is-not-me PLUS
 * the commons; the NAV dropdown renders everyone-who-is-not-me and omits the
 * commons (`kit:false`), because that menu already carries "What's in the bag"
 * three rows higher and the same destination twice in one menu is clutter. */
const NAV_KITS = TRADES.length - 1;
const HUB_KITS = NAV_KITS + 1; // + the commons

interface HubProbe {
  kits: { t: string; h: number }[];
  foot: { t: string; h: number }[];
  /** one-word labels rendered on two lines = the word itself was broken */
  wordBreaks: { t: string; w: number; l: number }[];
  hrefs: (string | null)[];
  markerLeft: boolean;
  aboveFoot: boolean;
  drift: string;
  overflowX: number;
}

const probeHub = (page: Page): Promise<HubProbe> =>
  page.evaluate(() => {
    const sizes = (sel: string) =>
      [...document.querySelectorAll(sel)].map((e) => ({
        t: (e.getAttribute('aria-label') || e.textContent || '').trim().slice(0, 26),
        h: Math.round(e.getBoundingClientRect().height * 10) / 10,
      }));
    const me = (window as any).Toolkit?.trade;
    const row = ((window as any).Toolkit?.trades || []).find((x: any) => x.slug === me?.slug);
    return {
      kits: sizes('.av-kits-foot .av-kit'),
      foot: sizes('.foot a'),
      wordBreaks: [...document.querySelectorAll('.av-kits-foot .av-kit b')]
        .map((e) => {
          const t = (e.textContent || '').trim();
          return { t, w: t.split(/\s+/).length, l: e.getClientRects().length };
        })
        .filter((o) => o.l > o.w),
      hrefs: [...document.querySelectorAll('.av-kits-foot .av-kit')].map((a) => a.getAttribute('href')),
      // The runtime retires the mount marker once it has placed the block.
      markerLeft: !!document.getElementById('siblings'),
      aboveFoot: !!document.querySelector('.av-kits-foot + .foot'),
      // THE DRIFT GATE. TRADES carries a COPY of each trade's icon and accent,
      // because a trade.js only loads on its own pages and /av/ cannot ask
      // /plumbing/ what colour it is. A copy that can drift is a copy that will,
      // so every hub checks its own row against its own trade.js.
      drift: row ? (row.icon === me.icon && row.accent === me.accent ? 'ok' : `MISMATCH ${row.icon}/${row.accent} vs ${me.icon}/${me.accent}`) : 'NO ROW',
      overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });

for (const trade of TRADES) {
  test.describe(`kit switcher — ${trade}`, () => {
    for (const width of WIDTHS) {
      test(`${width}px hub: every kit is a 44px target, nothing scrolls sideways`, async ({ page }) => {
        await page.setViewportSize({ width, height: 800 });
        await page.goto(`${trade}/`);
        await expect(page.locator('.av-kits-foot .av-kit').first()).toBeVisible({ timeout: 10_000 });

        const r = await probeHub(page);

        // Everyone who is not me, including the commons — the footer link row it
        // replaced listed exactly this set. DERIVED, not a literal: trade #7 was
        // the first to be added after this gate existed and it turned 35 tests
        // red on nothing but two hardcoded integers, on a change whose whole
        // point is that a new trade is one line. A count that has to be edited
        // every time the thing it counts grows is not a gate, it is a chore.
        expect(r.kits.length, 'kits rendered').toBe(HUB_KITS);
        expect(r.kits.filter((k) => k.h < MIN_TAP), `kit chips under ${MIN_TAP}px`).toEqual([]);
        // The footer's own links are the same class and were the same 16.7px.
        expect(r.foot.filter((k) => k.h < MIN_TAP), `footer links under ${MIN_TAP}px`).toEqual([]);
        expect(r.wordBreaks, 'a label was broken mid-word').toEqual([]);
        expect(r.overflowX, 'document scrolls sideways').toBe(0);
        expect(r.markerLeft, 'the #siblings mount marker was left in the footer').toBe(false);
        expect(r.aboveFoot, 'the switcher block must sit directly above the footer').toBe(true);
        expect(r.drift, 'TRADES row disagrees with this trade.js').toBe('ok');
        for (const h of r.hrefs) expect(h).toMatch(/^\.\.\/[a-z-]+\/$/);
        expect(r.hrefs).not.toContain(`../${trade}/`); // never link a kit to itself
      });
    }

    /* THE BRAND IS THE ONLY THING ON THE BAR THAT SAYS WHICH KIT YOU ARE IN, and
       it was being hard-cut mid-word with no ellipsis: the span could not shrink,
       so the PARENT's overflow:hidden did the cutting. MEASURED LIVE at 390px
       before the fix — /plumbing/ lost 13px, /electrical/ 28px, /low-voltage/
       42px, and trade #7 rendered "Framing & Drywall" as the two letters "FR".
       A fragment with no ellipsis does not read as a truncation, it reads as a
       name. The word may be shortened; it may be dropped entirely (the <=380px
       rule does exactly that, deliberately); it may never be silently cut. */
    for (const width of WIDTHS) {
      test(`${width}px: the brand names the kit, or says nothing — never a fragment`, async ({ page }) => {
        await page.setViewportSize({ width, height: 800 });
        await page.goto(`${trade}/`);
        await expect(page.locator('.av-brand')).toBeVisible({ timeout: 10_000 });
        const b = await page.evaluate(() => {
          const a = document.querySelector('.av-brand') as HTMLElement;
          const s = a.querySelector('span') as HTMLElement;
          return {
            hardCut: a.scrollWidth > Math.ceil(a.getBoundingClientRect().width) + 1,
            wordShown: getComputedStyle(s).display !== 'none',
            ellipsis: getComputedStyle(s).textOverflow,
          };
        });
        expect(b.hardCut, 'the brand is cut off by its own container').toBe(false);
        if (b.wordShown) {
          expect(b.ellipsis, 'a visible brand word that can be squeezed must ellipsize').toBe('ellipsis');
        }
      });
    }

    test('a tool page can reach another kit at all — the nav switcher', async ({ page }) => {
      await page.setViewportSize({ width: 390, height: 800 });
      await page.goto(`${trade}/${TOOLPAGE[trade]}`);
      await page.locator('.av-menu>button').click();

      const nav = await page.evaluate(() => {
        const chips = [...document.querySelectorAll('.av-drop .av-kit')].map((e) => ({
          t: (e.getAttribute('aria-label') || '').slice(0, 26),
          h: Math.round(e.getBoundingClientRect().height * 10) / 10,
        }));
        const d = document.querySelector('.av-drop')!.getBoundingClientRect();
        return {
          chips,
          breaks: [...document.querySelectorAll('.av-drop .av-kit b')]
            .map((e) => { const t = (e.textContent || '').trim(); return { t, w: t.split(/\s+/).length, l: e.getClientRects().length }; })
            .filter((o) => o.l > o.w),
          right: Math.round(d.right), bottom: Math.round(d.bottom),
          vw: document.documentElement.clientWidth, vh: window.innerHeight,
          overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        };
      });

      // The other trades, and NOT the commons: it is `kit:false` because the menu
      // already carries "What's in the bag" as its own row three entries above.
      // One fewer than the hub for exactly that reason — asserted as a
      // relationship rather than as two integers somebody has to remember.
      expect(nav.chips.length, 'kits offered on a tool page').toBe(NAV_KITS);
      expect(nav.chips.filter((c) => c.h < MIN_TAP), `nav chips under ${MIN_TAP}px`).toEqual([]);
      expect(nav.breaks, 'a nav label was broken mid-word').toEqual([]);
      expect(nav.right, 'the menu runs off the right edge').toBeLessThanOrEqual(nav.vw);
      expect(nav.bottom, 'the menu runs off the bottom').toBeLessThanOrEqual(nav.vh);
      expect(nav.overflowX).toBe(0);
    });

    test('the menu stays on the glass on the shortest screen we own', async ({ page }) => {
      // It had NO max-height before the switcher landed: a six-tool trade already
      // ran past a 568px screen with nothing to scroll.
      await page.setViewportSize({ width: 320, height: 568 });
      await page.goto(`${trade}/${TOOLPAGE[trade]}`);
      await page.locator('.av-menu>button').click();

      const s = await page.evaluate(() => {
        const d = document.querySelector('.av-drop') as HTMLElement;
        d.scrollTop = d.scrollHeight; // the LAST kit must be reachable, not merely present
        const last = [...document.querySelectorAll('.av-drop .av-kit')].pop()!.getBoundingClientRect();
        const r = d.getBoundingClientRect();
        return {
          bottom: Math.round(r.bottom), right: Math.round(r.right),
          vh: window.innerHeight, vw: document.documentElement.clientWidth,
          lastReachable: last.bottom <= window.innerHeight + 1 && last.top >= 0,
          overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        };
      });
      expect(s.bottom).toBeLessThanOrEqual(s.vh);
      expect(s.right).toBeLessThanOrEqual(s.vw);
      expect(s.lastReachable, 'the last kit cannot be scrolled to').toBe(true);
      expect(s.overflowX).toBe(0);
    });

    test('the chip actually lands you in the other kit', async ({ page }) => {
      // A render is not a route. Tap the first chip and assert the destination
      // hub is really there — and that IT can get back, which is what makes the
      // switcher a network rather than six dead ends.
      await page.setViewportSize({ width: 390, height: 800 });
      await page.goto(`${trade}/`);
      const chip = page.locator('.av-kits-foot .av-kit').first();
      const dest = (await chip.getAttribute('href'))!.replace('../', '').replace('/', '');
      await chip.click();
      await expect(page).toHaveURL(new RegExp(`/${dest}/(index\\.html)?$`));
      if (dest !== 'commons') {
        await expect(page.locator('.av-kits-foot .av-kit').first()).toBeVisible({ timeout: 10_000 });
        const back = await page.locator('.av-kits-foot .av-kit').evaluateAll(
          (els) => els.map((e) => e.getAttribute('href')));
        expect(back, 'the kit you landed in must offer the one you came from').toContain(`../${trade}/`);
      }
    });
  });
}
