/**
 * THE COMMONS BAG GATE — the state every other gate loads past.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/commons-bag.mjs [base-url]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 *
 * WHY THIS EXISTS. mobile-watertight loads all 76 pages FRESH, and commons-mobile
 * ticks rows without ever leaving the chip it ticked them on. Both grade a commons
 * whose bag is empty or single-trade — so neither one can see the surface that only
 * exists once you are carrying picks from a trade you are no longer looking at.
 * That is the same hole the collage gate had when it measured an app with no video
 * loaded: eleven controls under 44px hid behind it for weeks.
 *
 * WHAT HID BEHIND IT HERE (§SCARS 2026-08-13). Tick three rows under Electrical,
 * tap Plumbing, and the engine kept the picks, stopped rendering them, kept
 * COUNTING them, and then stamped the OPEN CHIP on all of them: Copy produced
 * "WHAT'S IN THE BAG — PLUMBING" over glow rods, lineman's pliers and wire
 * strippers. Three real defects in one state — a count you cannot reconcile, picks
 * you cannot reach to remove, and a document that told somebody an electrician's
 * tools were a plumber's.
 *
 * SO IT DRIVES THE REAL PAGE rather than seeding storage: it ticks with the mouse,
 * switches chips, and reads what the page's own Copy button puts on the clipboard —
 * because the defect was in the DOCUMENT, and a document is not a render. Surfaces
 * come from COMMONS_SURFACES in the shipped engine, so surface #3 is covered the
 * day it lands with no edit here.
 */
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const BASE = (args.find((a) => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const WIDTHS = [320, 360, 390, 430];
const MIN_TAP = 44;
/** The two trades are arbitrary and that is the point — any two differ. */
const FROM = 'Electrical';
const TO = 'Plumbing';

const browser = await chromium.launch();
const boot = await browser.newPage();
await boot.goto(`${BASE}/commons/index.html`);
const SURFACES = await boot.evaluate(() => (window.COMMONS_SURFACES || []).map((s) => s.href));
await boot.close();

if (!SURFACES.length) {
  console.error('FAIL: no surfaces parsed out of COMMONS_SURFACES — the engine did not load');
  await browser.close();
  process.exit(1);
}

const fails = [];
let checked = 0;

/** Tick rows in the open trade's own section that do NOT also belong to `avoid`,
 *  so that switching to `avoid` genuinely leaves them behind. */
async function tickAwayRows(page, avoid, want) {
  const own = page.locator('.sec').nth(1);
  const rows = await own.locator('li.item').all();
  const took = [];
  for (const row of rows) {
    if (took.length >= want) break;
    const tags = (await row.locator('.tag').allTextContents()).map((t) => t.trim());
    if (tags.some((t) => t.toLowerCase().startsWith(avoid.toLowerCase()))) continue;
    await row.locator('label').click();
    took.push((await row.locator('.nm').textContent()).trim());
  }
  return took;
}

/* ── 0. TWO ROWS MAY NOT SHARE AN ID ────────────────────────────────────────
 * Found live 2026-08-15 on the shipped gear list: "Inverted marking paint wand"
 * and "Marking paint" both carried id "marking-paint", and both are visible to a
 * GC. The engine keys picks BY ID (commons.js: `picks.push(g.id)` / `picked(g.id)`),
 * so ticking either rendered both as checked, put both in the bag document, and
 * made it impossible to remove one without the other. It survived every gate
 * because each gate ticks whatever row is at an index and reads the row it
 * ticked — nothing on this surface was ever comparing two rows to each other.
 * This is structural rather than behavioural on purpose: driving the collision
 * needs both rows to sit under the same open chip, which is one accident away
 * from being untestable, and the invariant holds regardless. */
{
  const boot2 = await browser.newPage();
  await boot2.goto(`${BASE}/commons/index.html`);
  const surfaces = await boot2.evaluate(() => (window.COMMONS_SURFACES || []).filter((s) => s.data && s.rows));
  for (const s of surfaces) {
    /* Each surface loads only its OWN data file, so the rows have to be read on
       the page that ships them — reading them all off index.html would silently
       check one surface and pass the other two on an empty array. */
    await boot2.goto(`${BASE}/commons/${s.href}`);
    const rows = await boot2.evaluate((k) => (window[k] || []).map((r) => ({ id: r.id, n: r.n })), s.rows);
    /* `fails` entries are [where, lines] PAIRS — the reporter at the bottom
       destructures them and calls bad.join(). Pushing a bare string here made
       the whole gate throw inside its own reporter, which is how the first cut
       of this check "passed" without ever firing. Found by negative control. */
    const bad = [];
    if (!rows.length) bad.push(`no rows readable on ${s.href} — the id check graded nothing`);
    const seen = new Map();
    for (const r of rows) {
      if (seen.has(r.id)) {
        bad.push(`id "${r.id}" is on two rows — "${seen.get(r.id)}" and "${r.n}". The bag keys picks by id, so ticking one ticks both and neither can be removed alone.`);
      } else { seen.set(r.id, r.n); checked++; }
    }
    if (bad.length) fails.push([`${s.data} — row ids`, bad]);
  }
  await boot2.close();
}

for (const href of SURFACES) {
  const url = `${BASE}/commons/${href}`;

  /* ---- 1. THE DOCUMENT, at one width, driven end to end ---- */
  {
    const ctx = await browser.newContext({
      viewport: { width: 390, height: 844 },
      permissions: ['clipboard-read', 'clipboard-write'],
    });
    const page = await ctx.newPage();
    const bad = [];
    await page.goto(url);
    await page.locator('.chip', { hasText: FROM }).first().click();
    const took = await tickAwayRows(page, TO, 3);

    if (took.length < 2) bad.push(`could not find 2 rows under ${FROM} that ${TO} does not share`);
    else {
      await page.locator('.chip', { hasText: TO }).first().click();
      await page.waitForTimeout(120);

      const cnt = Number(await page.locator('#cnt').textContent());
      const ticked = await page.locator('li.item input:checked').count();
      if (cnt !== ticked) {
        bad.push(`counter says ${cnt} and ${ticked} row(s) are ticked on screen — a pick nobody can see or take back out`);
      }

      const copied = await page.evaluate(async () => {
        await navigator.clipboard.writeText('');
        document.getElementById('copy').click();
        await new Promise((r) => setTimeout(r, 250));
        return navigator.clipboard.readText();
      });

      // THE DEFECT: the open chip stamped on rows that are not its trade.
      const head = copied.split('\n')[0];
      if (new RegExp(TO, 'i').test(head)) {
        bad.push(`the document is headed "${head}" and not one row in it is ${TO}'s`);
      }
      for (const name of took) {
        if (!copied.includes(name)) bad.push(`"${name}" is in the bag and not in the document`);
      }
      const block = copied.split('\n').find((l) => /^ALSO /i.test(l)) || '';
      if (!block) bad.push('the rows from another trade ride in the document under no heading of their own');
      else if (!new RegExp(FROM, 'i').test(block)) {
        bad.push(`"${block}" does not name ${FROM}, so the reader cannot tell whose rows these are`);
      }
    }

    checked++;
    if (bad.length) fails.push([`commons/${href} — the document`, bad]);
    else console.log(`PASS  commons/${href} — the document names whose rows these are`);
    await ctx.close();
  }

  /* ---- 2. THE GEOMETRY, at every width, default and bumped text ---- */
  for (const width of WIDTHS) {
    for (const bumped of [false, true]) {
      const ctx = await browser.newContext({ viewport: { width, height: 800 } });
      const page = await ctx.newPage();
      await page.goto(url);
      await page.locator('.chip', { hasText: FROM }).first().click();
      await tickAwayRows(page, TO, 4);
      await page.locator('.chip', { hasText: TO }).first().click();
      if (bumped) await page.evaluate(() => (document.documentElement.style.fontSize = '20px'));
      await page.waitForTimeout(120);

      const bad = await page.evaluate((MIN_TAP) => {
        const de = document.documentElement;
        const out = [];
        const away = [...document.querySelectorAll('.sec')].find((s) =>
          /^also/i.test(s.querySelector('h2')?.textContent || ''),
        );
        if (!away) return ['the rows carried in from another trade did not render at all'];
        const over = de.scrollWidth - de.clientWidth;
        if (over > 0) {
          const wide = [...document.querySelectorAll('*')]
            .map((el) => ({ el, b: el.getBoundingClientRect() }))
            .filter((x) => x.b.left >= 0 && x.b.right > de.clientWidth + 0.5)
            .sort((a, b) => b.b.right - a.b.right)[0];
          out.push(`overflows by ${over}px — widest culprit .${wide ? wide.el.className || wide.el.tagName : '?'}`);
        }
        for (const lab of away.querySelectorAll('label.lab')) {
          const b = lab.getBoundingClientRect();
          const short = Math.round(Math.min(b.width, b.height));
          if (short < MIN_TAP) out.push(`a row carried in from another trade is a ${short}px tap target`);
        }
        const note = away.querySelector('.secnote');
        if (!note || !/these belong to/i.test(note.textContent)) {
          out.push('the section does not say whose rows these are');
        }
        return out;
      }, MIN_TAP);

      checked++;
      const tag = `commons/${href} @${width}px${bumped ? ' bumped' : ''}`;
      if (bad.length) fails.push([tag, bad]);
      await ctx.close();
    }
  }
  console.log(`PASS  commons/${href} — carried rows are watertight at ${WIDTHS.join('/')}px`);
}

await browser.close();

for (const [where, bad] of fails) console.log(`\nFAIL  ${where}\n      ${bad.join('\n      ')}`);
console.log(
  `\n${checked} state(s) checked with a cross-trade bag across ${SURFACES.length} surface(s) — ${fails.length} failing`,
);
process.exit(fails.length ? 1 : 0);
