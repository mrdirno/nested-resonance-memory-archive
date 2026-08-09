/**
 * THE BACKING LEDGER IS WATERTIGHT — the ship gate for trade #7's signature tool
 * (framing/whats-in-the-wall.html), and for the trade standing up around it.
 *
 * WHY IT EXISTS
 *   Five of the six toolkits that shipped before framing send an ask AT this
 *   crew — backing behind a TV, head-end plywood, blocking for a carrier, a run
 *   behind the uppers. Those asks were recorded nowhere, and the wall closed.
 *   This page is the first place the ANSWER to a cross-boundary ask can live, so
 *   the thing that must be gated is not that it renders: it is that a foreman
 *   can walk a room on a phone, log what went in, and get a document that names
 *   the room, the height, the requester and the day it got covered.
 *
 *   A SCREENSHOT OF A RENDER IS NOT A VERIFICATION (§MOBILE-WATERTIGHT). So the
 *   job test below does the job the page claims — types the header, adds two
 *   real pieces through the real add bar, taps a row up the ladder, scopes the
 *   send to one trade — and reads the COPIED TEXT back.
 *
 * AND ONE SAFETY ASSERTION THAT IS THE WHOLE REASON THIS TRADE IS DANGEROUS.
 *   A mounting height is the single most damaging number this toolkit could ever
 *   volunteer: it gets buried behind rock before anybody notices it was ours and
 *   not the architect's. So the height field is asserted NAKED — no value, no
 *   placeholder digit, no chips, no options — and nothing in the emitted
 *   document may contain a height the user did not type (§SAFETY, and items.js
 *   says the same thing in prose).
 *
 * Serve the repo root and point at it:
 *   python3 -m http.server 8899   (from the repo root)
 *   npx playwright test --config playwright.backing.config.ts
 * Against production:
 *   BACKING_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/ \
 *     npx playwright test --config playwright.backing.config.ts
 */
import { test, expect, type Page } from '@playwright/test';

// RELATIVE, deliberately. The deployed site lives under a repo path
// (/nested-resonance-memory-archive/) and a leading slash resolves against the
// ORIGIN — silently dropping the prefix and 404ing every live run.
const PAGE = 'framing/whats-in-the-wall.html';
// Every page the trade ships, so a seventh trade cannot land with one good page
// and four that spill sideways.
const TRADE_PAGES = [
  'framing/',
  'framing/whats-in-the-wall.html',
  'framing/rough-in-request.html',
  'framing/answer-back.html',
  'framing/tm-tag.html',
  'framing/write-up.html',
  'framing/credits.html',
];
const WIDTHS = [320, 360, 390, 430];
const MIN_TAP = 44;

interface Geo {
  overflowX: number;
  under44: { t: string; h: number }[];
  pastRight: { t: string; r: number }[];
  vw: number;
}

/** Everything a thumb can hit, measured where it actually sits on the glass. */
const geometry = (page: Page): Promise<Geo> =>
  page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const vis = (e: Element) => (e as HTMLElement).offsetParent !== null
      && e.getBoundingClientRect().height > 0;
    const tappable = [...document.querySelectorAll('button,select,input:not([type=hidden]),textarea,a')]
      .filter(vis)
      // The nav's own controls are gated by kit-switcher.spec; this gate owns the page.
      .filter((e) => !e.closest('.av-bar') && !e.closest('.av-drop') && !e.closest('.av-sheet'));
    /* MEASURE WHAT A THUMB ACTUALLY HITS, not the element the DOM happens to
       name. A checkbox is 20px on every browser there is and cannot be made
       bigger without breaking its own rendering — but clicking its wrapping
       LABEL toggles it, so the label IS the target. Measuring the box instead
       reported 17 failures on this trade, 14 on plumbing and 8 on electrical
       for controls that are all comfortably over the line. A gate that cries
       wolf on three shipped trades gets switched off, which is worse than not
       having it. */
    const target = (e: Element) => {
      const lab = e.closest('label');
      const box = (lab && (e as HTMLInputElement).type === 'checkbox' ? lab : e).getBoundingClientRect();
      return Math.round(box.height * 10) / 10;
    };
    return {
      overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      under44: tappable
        .map((e) => ({
          t: ((e.textContent || (e as HTMLInputElement).placeholder || e.id || '') as string).trim().slice(0, 24),
          h: target(e),
        }))
        .filter((o) => o.h < 44),
      pastRight: [...document.querySelectorAll('.wrap *')]
        .filter(vis)
        .map((e) => ({ t: (e.textContent || '').trim().slice(0, 24), r: Math.round(e.getBoundingClientRect().right) }))
        .filter((o) => o.r > vw + 1),
      vw,
    };
  });

test.describe('framing toolkit — mobile watertight', () => {
  for (const path of TRADE_PAGES) {
    for (const width of WIDTHS) {
      test(`${path} at ${width}px: nothing spills, nothing under ${MIN_TAP}px`, async ({ page }) => {
        await page.setViewportSize({ width, height: 800 });
        await page.goto(path);
        // The runtime's own nav, not `.foot`: tm-tag and write-up close with a
        // sticky action bar instead of a footer, and waiting on something every
        // page has ALSO proves shared/toolkit.js actually booted on it.
        await expect(page.locator('.av-bar')).toBeVisible({ timeout: 10_000 });

        const g = await geometry(page);
        expect(g.overflowX, 'document scrolls sideways').toBe(0);
        expect(g.pastRight, 'something renders past the right edge').toEqual([]);
        expect(g.under44, `controls under ${MIN_TAP}px`).toEqual([]);
      });
    }
  }

  /* ZOOMED OUT, which is the operator's own wording and a different failure from
     a narrow viewport: the OS text size goes up and every fixed box has to grow
     with it instead of clipping what is inside it. */
  test('320px at a 22px root — the bumped-text-size phone', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto(PAGE);
    await page.addStyleTag({ content: 'html{font-size:22px}' });
    await expect(page.locator('#bar')).toBeVisible({ timeout: 10_000 });

    const g = await geometry(page);
    expect(g.overflowX, 'document scrolls sideways with big text').toBe(0);
    expect(g.pastRight, 'something renders past the right edge with big text').toEqual([]);
  });
});

test.describe('framing backing ledger — it does the job', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PAGE);
    await expect(page.locator('#bar')).toBeVisible({ timeout: 10_000 });
    // A previous run's draft would make every assertion below a lie.
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(page.locator('#bar')).toBeVisible({ timeout: 10_000 });
  });

  /* THE FIELD THAT MUST NEVER SUGGEST ANYTHING. Asserted before the job test,
     because a seeded height would still produce a passing document. */
  test('the height field is naked — no value, no digit in the placeholder', async ({ page }) => {
    const h = page.locator('#rl_high');
    await expect(h).toBeVisible();
    expect(await h.inputValue(), 'the height field shipped with a value in it').toBe('');
    const ph = (await h.getAttribute('placeholder')) || '';
    expect(ph, `the height placeholder contains a number: "${ph}"`).not.toMatch(/\d/);
    // …and it is a free-text field, never a picker: a chip list of heights is a
    // recommendation with extra steps.
    expect(await page.locator('[data-chips="high"]').count(), 'the height field grew chips').toBe(0);

    // The page must SAY it out loud too — the warn block is the user-facing half
    // of the same rule.
    await expect(page.locator('#warn')).toContainText(/we won.t guess/i);
  });

  test('walk a room, log two pieces, and the message says what is in the wall', async ({ page }) => {
    await page.fill('#hJob', 'Building C');
    await page.fill('#hFrom', 'M. Alvarez — Apex Interiors');
    await page.fill('#hTel', '415-555-0177');

    // ── piece one: a TV backing the AV foreman asked for ────────────────────
    await page.selectOption('#rl_what', 'TV / monitor');
    await page.locator('[data-chips="went"] button', { hasText: /^Plywood$/ }).click();
    await page.locator('[data-chips="who"] button', { hasText: /^AV$/ }).click();
    await page.fill('[data-learn="area"]', 'Rm 314');
    await page.fill('[data-learn="wall"]', 'north wall, corridor side');
    await page.fill('#rl_high', '48 to 84 off the floor');
    await page.fill('#rl_size', '32 wide');
    await page.locator('[data-chips="how"] button', { hasText: /^Text$/ }).click();
    await page.locator('#rlAdd').click();
    await expect(page.locator('.rl-row')).toHaveCount(1);

    // ── piece two: casework, same room — the sticky fields must carry ───────
    await page.selectOption('#rl_what', 'Casework & uppers');
    await page.locator('[data-chips="went"] button', { hasText: /^2x flat$/ }).click();
    await page.locator('[data-chips="who"] button', { hasText: /^Casework$/ }).click();
    await page.fill('#rl_high', '80 to 92 off the floor');
    await page.locator('#rlAdd').click();
    await expect(page.locator('.rl-row')).toHaveCount(2);

    // The room carried without being retyped — that is the whole reason a walk
    // of eleven rooms is usable on a phone.
    const doc0 = await page.locator('#preview').innerText();
    expect((doc0.match(/Rm 314/g) || []).length, 'the sticky room did not carry to row two').toBeGreaterThanOrEqual(2);

    // ── tap the first row up the ladder ─────────────────────────────────────
    // Rows land BLANK, not on the first rung — a default is a claim, and this
    // page must never assert that a piece went in. So it is blank → Asked → In
    // → Covered, and reaching Covered is three taps by design.
    const row = page.locator('.rl-row').first();
    await row.click();
    await expect(page.locator('#preview')).toContainText(/asked/i);
    await row.click();
    await row.click();
    await expect(page.locator('#preview')).toContainText(/covered/i);

    // ── the document ────────────────────────────────────────────────────────
    const doc = await page.locator('#preview').innerText();
    expect(doc, 'the job is not in the subject line').toContain('Building C');
    expect(doc, 'who sent it is missing').toContain('M. Alvarez');
    expect(doc, 'the room is missing').toContain('Rm 314');
    expect(doc, 'the wall and side are missing').toContain('north wall');
    expect(doc, 'the height he typed is missing').toContain('48 to 84');
    // …VERBATIM. The page labels his number; it never appends to it.
    expect(doc, 'the page duplicated the height wording').not.toMatch(/off the floor off the floor/);
    expect(doc, 'the second piece is missing').toContain('Casework & uppers');
    // The tally by requester is what turns a log into evidence.
    expect(doc, 'the by-requester tally is missing').toMatch(/AV 1/);
    expect(doc, 'the closing ask is missing').toMatch(/before we close it/i);
    expect(doc, 'the boundary sentence is missing').toMatch(/isn.t in that wall/i);
    // §SAFETY, asserted rather than trusted — and asserted on FIGURES, not on
    // words. The closing line says "no price on it" and "it doesn't rate, size
    // or approve anything" on purpose; a regex that bans the word banned the
    // disclaimer that exists to enforce the rule.
    expect(doc, 'a money figure leaked into the document').not.toMatch(/[$£€]\s?\d|\d+\.\d{2}\b|\bper (hour|hr|man)\b/i);

    // ── scope it to one receiver: the come-look message ─────────────────────
    await page.locator('#segWho button', { hasText: /^AV$/ }).click();
    const scoped = await page.locator('#preview').innerText();
    expect(scoped, 'the scoped message is not addressed to him').toMatch(/To: AV/);
    expect(scoped, "the other trade's row leaked into his message").not.toContain('Casework & uppers');
    expect(scoped, 'a one-receiver message still carries a cross-trade tally').not.toMatch(/AV 1 ·/);

    // ── and the copy button actually copies THAT ────────────────────────────
    await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.locator('#copyBtn').click();
    const clip = await page.evaluate(() => navigator.clipboard.readText());
    expect(clip, 'the clipboard did not get the scoped document').toContain('Rm 314');
    expect(clip, 'the clipboard got the unscoped document').not.toContain('Casework & uppers');
  });

  /* THE HELD BLOCK IS THE HALF THAT PAYS THIS WEEK: a piece he cannot build
     because nobody gave him a number has to arrive as an ASK, not as a silent
     gap in a list of things that went in. */
  test('a piece held for a height lands in its own block with the ask on it', async ({ page }) => {
    await page.fill('#hJob', 'Building C');
    await page.selectOption('#rl_what', 'Marker board / tack board');
    await page.locator('[data-chips="who"] button', { hasText: /^AV$/ }).click();
    await page.fill('[data-learn="area"]', 'Rm 210');
    await page.locator('#rlAdd').click();
    await expect(page.locator('.rl-row')).toHaveCount(1);

    // Flag it through the real pencil, the way a foreman would.
    await page.locator('.rl-row .rl-edit').first().click();
    const flag = page.locator('.rl-flagchip', { hasText: /Need a height/ }).first();
    await expect(flag).toBeVisible({ timeout: 5_000 });
    await flag.click();

    const doc = await page.locator('#preview').innerText();
    expect(doc, 'the held block is missing').toMatch(/STILL NEED FROM YOU/);
    expect(doc, 'the held row does not say what it is waiting on').toMatch(/Need a height/);
    expect(doc, 'the held row lost its room').toContain('Rm 210');
  });
});
