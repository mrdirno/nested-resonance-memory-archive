/**
 * WHERE THE WALL'S AT — the gate for trade #11's signature document.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/wall-state.mjs [base-url]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 *
 * WHY A PAGE GETS ITS OWN GATE. mobile-watertight measures whether the page is
 * usable; rowlog-restore measures whether the log survives a device wipe.
 * Neither reads the DOCUMENT, and this page exists only for its document — it
 * publishes the number two other trades' gate ladders count down to. So this
 * drives the real page and asserts what the Copy button actually put on the
 * clipboard.
 *
 * WHAT IT REFUSES TO LET DRIFT, each one a rule from masonry/items.js or the
 * book, asserted rather than trusted:
 *   · THE COURSE reaches the document. It is the whole point of the page.
 *   · THE INVERSE-CLAIM GUARD prints on every copy — "a wall not named here is a
 *     wall I have said nothing about". A list of the dangerous walls will be read
 *     as clearing the rest; without this line it silently is.
 *   · The NOBODY TOUCHES block and the CELLS STILL OPEN call-out are drawn from
 *     the WHOLE log even under a filter, and SAY SO when scoped — dropping a
 *     "don't backfill against it" notice because somebody tapped a filter is a
 *     safety defect, and printing it without saying so contradicts the body.
 *   · NO CLOCK TIME. roofing/whats-open.html stamps one because its argument is
 *     about a single night; this one is about a day and a course, and the two
 *     pages look alike enough for a later cycle to copy it across.
 *   · No percentage VALUE and no money symbol anywhere in the document.
 *   · The no-course nudge fires in the UI and NEVER prints — publishing "3 of
 *     these have no course" invites the receiver to argue the record instead of
 *     acting on it (the same rule the return leg holds on dateless yesses).
 *   · A count that merely restates the active filter does not print twice.
 *   · The pencil-open state is watertight at all four widths with 44px targets.
 *
 * THE ONE THING TO KNOW BEFORE EDITING THIS FILE: a `learn` axis SELECTS on
 * Enter. Clicking its chip afterwards toggles the value back OFF and the add is
 * refused for an empty required field — silently, with an empty list. The first
 * cut of this driver did exactly that and reported fourteen document failures on
 * a page that was working.
 */
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url)).replace(/\/$/, '');
const args = process.argv.slice(2);
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');
const URL_ = `${BASE}/masonry/wheres-the-wall.html`;

const fails = []; let ok = 0;
const check = (cond, msg) => { if (cond) ok++; else fails.push(msg); };

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, permissions: ['clipboard-read', 'clipboard-write'] });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(URL_);
await page.waitForSelector('#bar');

// header
await page.fill('#hJob', 'Building B');
await page.fill('#hFrom', 'Dave — Kerrigan Masonry');
await page.fill('#hTel', '(503) 555-0147');

async function pickLearn(key, val) {
  /* Enter on a learn axis LEARNS the word and SELECTS it in one move — the
     hidden input already carries it. Clicking the chip afterwards TOGGLES IT
     OFF, which is what the first cut of this driver did, and the page then
     correctly refused to add a row with a required field empty. Engine
     behaviour, driver bug. */
  const inp = page.locator(`[data-learn="${key}"]`);
  await inp.fill(val);
  await inp.press('Enter');
  const hidden = page.locator(`input[data-k="${key}"]`);
  const got = await hidden.inputValue();
  if (got !== val) {
    const chip = page.locator(`[data-chips="${key}"] button.rl-chip`).filter({ hasText: val }).first();
    if (await chip.count()) await chip.click();
    else fails.push(`typing "${val}" into ${key} neither selected it nor produced a chip`);
  }
}
async function pickChip(key, val) {
  const chip = page.locator(`[data-chips="${key}"] button.rl-chip`).filter({ hasText: val }).first();
  if (await chip.count()) await chip.click();
  else fails.push(`no chip "${val}" on axis ${key}`);
}
async function addRow({ wall, state, course, hold, touch, next }) {
  await pickLearn('wall', wall);
  await page.locator('select[data-k="state"]').selectOption({ label: state });
  if (course) await pickLearn('course', course);
  if (hold) await pickChip('hold', hold);
  if (touch) await pickChip('touch', touch);
  if (next) await pickChip('next', next);
  await page.locator('#rlAdd').click();
}

await addRow({ wall: 'Grid C 4 to 9', state: 'On the wall', course: 'course 14',
  hold: "Another trade's rough-in", touch: 'Braces are ours, call before anybody moves one', next: 'Carry on up' });
await addRow({ wall: 'East elevation', state: 'Capped out', course: 'top course',
  hold: "Nothing — we're going", touch: 'Not braced yet, come see me', next: 'Grout it next' });
await addRow({ wall: 'West elevation', state: 'Grouted', course: 'top course',
  hold: "Nothing — we're going", next: 'Strike, tool and point up' });

const rowCount = await page.locator('#list .rl-row, #list li').count();
check(rowCount >= 3, `expected 3 rows in the list, found ${rowCount}`);

// ---- the document, everything ----
await page.locator('#copyBtn').click();
const doc = await page.evaluate(() => navigator.clipboard.readText());

check(/^Building B — where the wall's at — /.test(doc), 'line 1 is not "job — subject — date"');
check(!/\d{1,2}:\d{2}(am|pm)/i.test(doc), 'the document carries a CLOCK TIME — this one is a day and a course, not a night');
check(/2 WITH CELLS STILL OPEN/.test(doc), `header count line wrong — got: ${(doc.match(/^.*WALLS.*$/m) || [''])[0]}`);
check(/1 HELD ON SOMEBODY ELSE/.test(doc), 'held count missing from the header');
check(/course 14/.test(doc), 'the course did not reach the document — that is the whole point of the page');
check(/NOBODY TOUCHES THESE/.test(doc), 'the nobody-touches block is missing');
check(/not braced yet, come see me/i.test(doc), 'an unbraced wall did not print in the nobody-touches block');
check(/CELLS STILL OPEN: /.test(doc), 'the cells-still-open call-out is missing');
// "CELLS STILL OPEN" appears TWICE — in the header count and in the footer
// call-out — so the call-out is split()[2], not [1]. Reading [1] graded the body.
const callout = doc.split('CELLS STILL OPEN').pop() || '';
check(/Grid C 4 to 9 — course 14 · East elevation — top course/.test(callout),
  `the cells call-out does not separate wall from course: ${callout.split('\n')[0]}`);
check(/A wall not named here is a wall I have said nothing about/.test(doc), 'THE INVERSE-CLAIM GUARD IS MISSING FROM THE DOCUMENT');
check(!/\d+\s?%/.test(doc), 'a percentage VALUE reached the document');
check(!/\$/.test(doc), 'a money symbol reached the document');

// ---- the filtered copies ----
await page.locator('#segScope button[data-f="stillopen"]').click();
await page.locator('#copyBtn').click();
const open = await page.evaluate(() => navigator.clipboard.readText());
const openCount = (open.match(/^\d+ WALLS? OF \d+ .*$/m) || [''])[0];
check(/^2 WALLS OF 3 — STILL TO GROUT/.test(openCount), `still-to-grout scope did not narrow: ${openCount}`);
check(!/WITH CELLS STILL OPEN/.test(openCount), `the count restates the filter it is already labelled with: ${openCount}`);
check(!/West elevation —/.test(open.split('NOBODY TOUCHES')[0]), 'a grouted wall survived the still-to-grout filter in the body');
check(/every wall on my log/.test(open), 'the footer did not say it covers the whole log while a filter is on — it contradicts the body above it');

await page.locator('#segScope button[data-f="held"]').click();
await page.locator('#copyBtn').click();
const held = await page.evaluate(() => navigator.clipboard.readText());
const heldCount = (held.match(/^\d+ WALLS? OF \d+ .*$/m) || [''])[0];
check(/^1 WALL OF 3 — HELD ON SOMEBODY ELSE/.test(heldCount), `held scope did not narrow: ${heldCount}`);
check((heldCount.match(/HELD ON SOMEBODY ELSE/g) || []).length === 1, `"held on somebody else" printed twice in one line: ${heldCount}`);
check(/Grid C 4 to 9/.test(held.split('NOBODY TOUCHES')[0]), 'the held wall is not in the held-scope body');

await page.locator('#segScope button[data-f=""]').click();

// ---- the no-course nudge, and it must never print ----
await pickLearn('wall', 'North stair');
await page.locator('select[data-k="state"]').selectOption({ label: 'Leads up' });
await page.locator('#rlAdd').click();
const nudge = await page.locator('#nocourse').innerText().catch(() => '');
check(/1 wall standing with no course/.test(nudge), `the no-course nudge did not fire: "${nudge}"`);
await page.locator('#copyBtn').click();
const doc2 = await page.evaluate(() => navigator.clipboard.readText());
check(!/no course/i.test(doc2), 'the no-course count PRINTED — it is a UI nudge and must never reach the receiver');

// ---- the pencil state, which the mobile gate does not measure ----
const pencil = page.locator('#list .rl-pen, #list [data-act="edit"], #list button').first();
let pencilOpened = false;
if (await pencil.count()) { await pencil.click(); pencilOpened = true; }
else {
  const anyBtn = page.locator('#list button').first();
  if (await anyBtn.count()) { await anyBtn.click(); pencilOpened = true; }
}
if (pencilOpened) {
  for (const width of [320, 360, 390, 430]) {
    await page.setViewportSize({ width, height: 800 });
    const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    check(over <= 0, `pencil open: overflows by ${over}px at ${width}px`);
    const small = await page.evaluate((min) => {
      const bad = [];
      document.querySelectorAll('#list button, #list select, #list input, #list label').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        if (Math.min(r.width, r.height) < min - 0.5) bad.push(`${el.tagName.toLowerCase()} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.textContent || '').trim().slice(0, 24)}"`);
      });
      return bad;
    }, 44);
    check(small.length === 0, `pencil open at ${width}px: ${small.length} control(s) under 44px — ${small.slice(0, 4).join(' | ')}`);
  }
  await page.setViewportSize({ width: 390, height: 844 });
}
check(pencilOpened, 'could not open the pencil editor — the revealed state was not measured');

// the wishing-well fetch is unsupported on file:// and fires on every page in
// the program — it is not this page's defect. Everything else is.
const real = errs.filter(e => !/Fetch API cannot load|URL scheme "file"/.test(e));
check(real.length === 0, `page errors: ${real.slice(0, 3).join(' | ')}`);

await browser.close();
console.log(`\nWHERE THE WALL'S AT — driven end to end at 390px: ${ok} assertion(s) passed, ${fails.length} failing`);
for (const f of fails) console.log('  ✗ ' + f);
process.exit(fails.length ? 1 : 0);
