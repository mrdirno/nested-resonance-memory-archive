/**
 * THE NAME-TABLE GATE — proves the synonyms do work, and that the page cannot
 * hand a man a trademark to write on a purchase order.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/commons-names.mjs [base-url]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 *
 * WHY THIS EXISTS. The panel that ranked this rung voted it down once, on one
 * argument: this project has met the translation problem twice and solved it both
 * times as ROUTING INSIDE A TOOL — av/items.js writes its asks in the receiver's
 * vocabulary, shared/docspec.js carries `aka` so a man finds his write-up under
 * whatever his shop calls it — and a synonym that only sits in a list does no
 * work. The build had to answer that or not ship.
 *
 * The answer is that names.js is an INDEX every commons surface searches through.
 * So this gate does not check that the name table renders. It goes to the GEAR
 * LIST, types words that appear NOWHERE on that page, and demands the right row.
 * Every probe is derived from the data — no hand-picked examples — so a word
 * added next month is tested the day it lands, and a gear row renamed out of the
 * join fails the build instead of quietly becoming a glossary entry.
 *
 * The second half is the rails. This page is evidence about the WORD and will be
 * read as authority about the OBJECT, so: no digit anywhere (a name that needs a
 * number to be right is certified data we do not ship), no two names joined by a
 * slash, no trademark sitting where the order name goes, every alias attributed,
 * every row declaring its object.
 */
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const BASE = (args.find((a) => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const WIDTHS = [320, 360, 390, 430];
const MIN_TAP = 44;
const FLOOR = 6;      /* rows written for a trade, matching the deploy's bar */
const NARROW = 3;     /* tagged to at most three trades = written for one of them */
const KINDS = ['tm', 'reg', 'say', 'sup'];

const fails = [];
let checked = 0;
const fail = (m) => fails.push(m);
const ok = () => { checked++; };

/* ── the data, read the way the browser reads it ───────────────────────────── */
const w = {};
for (const f of ['commons/commons.js', 'commons/names.js', 'commons/gear.js', 'commons/tips.js']) {
  new Function('window', readFileSync(ROOT + f, 'utf8'))(w);
}
const NAMES = w.COMMONS_NAMES || [];
const GEAR = w.COMMONS_GEAR || [];
const TRADES = (w.COMMONS_TRADES || []).map((t) => t.slug).filter((s) => s !== 'universal');

if (!NAMES.length) { console.error('FAIL: names.js defined no rows'); process.exit(1); }
if (typeof w.Commons?.aka !== 'function') { console.error('FAIL: commons.js exports no alias join'); process.exit(1); }

/* ── 1. the rails, on the data ─────────────────────────────────────────────── */
const seenId = new Set();
for (const r of NAMES) {
  const where = `names.js:${r.id}`;
  const strings = [r.n, r.o, r.no || '', ...(r.a || []).flatMap((a) => [a.n, a.by])];

  if (seenId.has(r.id)) fail(`${where}: duplicate id`);
  seenId.add(r.id);

  /* Rail 4 — a name that needs a number to be right is certified data. */
  for (const s of strings) {
    if (/\d/.test(s)) fail(`${where}: a digit in "${s}" — this page does not separate near-names by size, gauge, gang or rating`);
  }
  /* Rail 1 — one object, or two rows. Never two names on one line. */
  if (/[/]| or /i.test(r.n)) fail(`${where}: "${r.n}" joins two names — if both sides would not satisfy the same order, they are two rows`);
  /* Rail 7 — the object is declared and checkable, not implied. */
  if (!r.o || r.o.length < 12) fail(`${where}: no object clause — the row is evidence about a word and must say what the thing IS`);
  if (!Array.isArray(r.a) || !r.a.length) fail(`${where}: no aliases — a row nobody would type is dead weight`);
  if (!Array.isArray(r.t) || !r.t.length) fail(`${where}: untagged`);
  for (const t of r.t || []) {
    if (t !== 'universal' && !TRADES.includes(t)) fail(`${where}: tagged "${t}", which is not a trade on the commons`);
  }
  for (const a of r.a || []) {
    if (!KINDS.includes(a.k)) fail(`${where}: alias "${a.n}" has kind "${a.k}" — the page frames a word by its kind and has no framing for that`);
    if (!a.by || a.by.length < 3) fail(`${where}: alias "${a.n}" says nobody in particular — a regional word must carry who says it`);
    /* k:"reg" PRINTS AS "you might hear", which promises a PLACE. Nineteen aliases
     * in the first seed named a COHORT instead — "some crews", "older hands",
     * "overseas" — which reads to a man as a region he has never worked in. The
     * check is a ban-list of the phrases that actually showed up rather than an
     * allow-list of places, because an allow-list would reject the next real
     * region somebody adds. */
    if (a.k === 'reg' && /\b(some (crews|shops|counters|techs|hands)|older hands|older \w+ (men|hands)|overseas|the field|plenty of|on both sides)\b/i.test(a.by)) {
      fail(`${where}: alias "${a.n}" prints as "you might hear" but is attributed to "${a.by}" — that is a cohort, not a place. Use k:"say".`);
    }
    /* Rail 2 — the trademark is what people SAY. It never becomes the order name. */
    if (a.k === 'tm' && a.n.trim().toLowerCase() === r.n.trim().toLowerCase()) {
      fail(`${where}: the order name IS the trademark`);
    }
  }
  ok();
}

/* ── 2. every chip is backed by rows somebody wrote for that trade ─────────── */
for (const t of TRADES) {
  const written = NAMES.filter((r) => r.t.includes(t) && !r.t.includes('universal') && r.t.length <= NARROW);
  if (written.length < FLOOR) {
    fail(`coverage: ${t} has a chip on the commons and ${written.length} name row(s) written for it (floor ${FLOOR}) — a chip with nothing behind it is a lie told to one trade`);
  } else ok();
}
const floorRows = NAMES.filter((r) => r.t.includes('universal'));
if (!floorRows.length) fail('coverage: no universal rows — the page opens on the universal chip and would open blank');
else ok();

/* ── 3. the probes: words that are NOT on the gear page ────────────────────── */
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const gearHay = norm(GEAR.map((g) => `${g.n} ${g.w}`).join(' '));
const probes = [];
for (const g of GEAR) {
  for (const word of w.Commons.aka(g)) {
    if (gearHay.includes(norm(word))) continue;   /* already findable without the index — proves nothing */
    probes.push({ word, expect: g.n });
  }
}

/* ── the browser ───────────────────────────────────────────────────────────── */
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 780 } });
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e)));

/* 3a. THE ROUTE — on the GEAR list, not the name table. */
await page.goto(`${BASE}/commons/index.html`);
await page.waitForSelector('.chip');
if (!probes.length) {
  fail('route: not one word in names.js reaches a gear row that does not already contain it — the index is decorative');
} else {
  for (const p of probes) {
    await page.fill('#q', p.word);
    const note = (await page.locator('.secnote').first().textContent()) || '';
    const hits = (await page.locator('#sections .nm').allTextContents()).map((s) => s.trim());
    if (/closest/i.test(note) && !hits.includes(p.expect)) {
      fail(`route: "${p.word}" fell through to the closest-match fallback on the gear list — expected ${p.expect}`);
    } else if (!hits.includes(p.expect)) {
      fail(`route: "${p.word}" did not surface ${p.expect} on the gear list (got: ${hits.slice(0, 3).join(', ') || 'nothing'})`);
    } else ok();
  }
  await page.fill('#q', '');
}

/* 3a-ii. THE HAND-OFF. The index can only route to objects THIS surface carries,
 * and the gear list is tools — cable ties and wire connectors are consumables and
 * have no row on it. Found live on the shipped page: "zap strap" dropped "zap" as
 * noise, matched "strap" by infix, came back at full coverage, and the page said
 * "Matches: Wire strippers" with total confidence. So every alias belonging to a
 * names row that the gear list CANNOT answer must produce the hand-off instead of
 * a confident wrong hit. Derived from the data, same as the probes above. */
const gearIds = new Set(GEAR.map((g) => g.id));
const gearNames = new Set(GEAR.map((g) => norm(g.n.replace(/\(.*?\)/g, ' ').split(',')[0])));
const orphans = NAMES.filter((r) => !gearIds.has(r.id) && !gearNames.has(norm(r.n)));
let handoffProbes = 0;
for (const r of orphans.slice(0, 24)) {
  const word = (r.a || [])[0] && r.a[0].n;
  if (!word || gearHay.includes(norm(word))) continue;
  await page.fill('#q', word);
  const titles = await page.locator('.sechead h2').allTextContents();
  handoffProbes++;
  /* A word may belong to several objects — "mud ring" and "plumber's tape" each
   * name two — and there the honest hand-off is BOTH, not a picked side. So the
   * gate asks that the page handed off, not that it handed off to one row. */
  const ambiguous = NAMES.filter((x) => (x.a || []).some((al) => norm(al.n) === norm(word))).length > 1;
  const want = ambiguous ? /things go by that/i : new RegExp('^he means ' + r.n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$', 'i');
  if (!titles.some((t) => want.test(t.trim()))) {
    fail(`handoff: "${word}" is a ${r.n} and the gear list carries no such row, but it answered with ${titles.join(' / ')} instead of handing him to the name table`);
  } else ok();
}
await page.fill('#q', '');

/* A word the whole commons has never heard must NOT produce a hand-off — that
 * would be a guess wearing a certainty the page has not earned. */
await page.fill('#q', 'qwertyuiop');
if ((await page.locator('.sechead h2').allTextContents()).some((t) => /he means/i.test(t))) {
  fail('handoff: fired on a word nothing in the commons knows — a guess is not a hand-off');
} else ok();
await page.fill('#q', '');

/* 3b. a word in NOTHING still never dead-ends (find.js rule 2, honestly labelled) */
await page.fill('#q', 'qwertyuiop');
const deadNote = (await page.locator('.secnote').first().textContent()) || '';
const deadHits = await page.locator('#sections .nm').count();
if (!deadHits) fail('route: a query that matches nothing emptied the page — "nothing matches" is a bug, not a state');
else if (!/closest/i.test(deadNote)) fail(`route: a fallback result is not labelled as one ("${deadNote.slice(0, 70)}")`);
else ok();
await page.fill('#q', '');

/* 3c. tapping a trade clears the box — that is a man asking to browse */
await page.fill('#q', 'tape');
await page.locator('.chip', { hasText: 'Plumbing' }).first().click();
if ((await page.inputValue('#q')) !== '') fail('route: tapping a trade chip left a stale query in the box');
else ok();

/* ── 4. the framing, on the name table itself ──────────────────────────────── */
await page.goto(`${BASE}/commons/names.html`);
await page.waitForSelector('.chip');
for (const slug of ['universal', ...TRADES]) {
  await page.evaluate((v) => localStorage.setItem('commons.view.v1', v), slug);
  await page.reload();
  await page.waitForSelector('#sections .item');
  const rows = await page.locator('#sections .item').count();
  const eyes = await page.locator('#sections .item .nmeye').count();
  const objs = await page.locator('#sections .item .obj').count();
  if (eyes !== rows) fail(`framing: ${slug} renders ${rows} rows and ${eyes} "order it as" labels — a row without it reads as a list of equal names`);
  else if (objs !== rows) fail(`framing: ${slug} renders ${rows} rows and ${objs} object clauses`);
  else ok();
  const byless = await page.locator('#sections .aka:not(:has(.by))').count();
  if (byless) fail(`framing: ${slug} renders ${byless} alias(es) with nobody attributed`);
  else ok();
}

/* 4b. the document: the generic leads every line, whatever was ticked */
await page.evaluate(() => localStorage.setItem('commons.view.v1', 'electrical'));
await page.reload();
await page.waitForSelector('#sections .item');
await page.locator('#sections .item .lab').first().click();
await page.locator('#sections .item .lab').nth(1).click();
await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
await page.click('#copy');
const doc = await page.evaluate(() => navigator.clipboard.readText());
const lines = doc.split('\n').filter((l) => l.startsWith('- '));
if (!lines.length) fail('document: Copy produced no picked lines');
for (const line of lines) {
  const lead = line.replace(/^- /, '').split('  (')[0].trim();
  const row = NAMES.find((r) => r.n === lead);
  if (!row) { fail(`document: "${lead}" leads a line and is not an order name in names.js`); continue; }
  const tm = (row.a || []).filter((a) => a.k === 'tm').map((a) => a.n.toLowerCase());
  if (tm.includes(lead.toLowerCase())) fail(`document: a trademark leads the line "${line}"`);
  else ok();
}
if (lines.length && !/they might say/.test(doc)) {
  fail('document: the aliases ride along unlabelled — a pasted line must say which half is talk');
} else ok();

/* ── 5. mobile-watertight, with the box in play ────────────────────────────── */
for (const surface of ['index.html', 'tips.html', 'names.html']) {
  for (const width of WIDTHS) {
    await page.setViewportSize({ width, height: 780 });
    await page.goto(`${BASE}/commons/${surface}`);
    await page.waitForSelector('.chip');
    await page.fill('#q', 'wire');           /* the state a screenshot of a fresh load never sees */
    const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (over > 0) fail(`mobile: ${surface} at ${width}px overflows by ${over}px with a query in the box`);
    else ok();
    const small = await page.evaluate((min) => {
      const out = [];
      /* The row checkbox is 22px BY DESIGN and is not the tap target — the whole
       * .lab wrapping it is, which is why the label is measured and the box is
       * not. Measuring the box instead reports four failures on a page where a
       * thumb has never missed. */
      document.querySelectorAll('button, a.btn, .rail a, input:not([type="checkbox"]), .lab').forEach((el) => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height || el.hasAttribute('hidden')) return;
        if (r.height < min - 0.5) out.push((el.id || el.className || el.tagName) + ' ' + Math.round(r.height) + 'px');
      });
      return out;
    }, MIN_TAP);
    if (small.length) fail(`mobile: ${surface} at ${width}px has tap targets under ${MIN_TAP}px — ${small.slice(0, 4).join(', ')}`);
    else ok();
  }
}

if (pageErrors.length) fail(`page errors: ${pageErrors.slice(0, 3).join(' | ')}`);

await browser.close();

console.log(`${checked} checks · ${probes.length} routing probes derived from the data · ${NAMES.length} name rows`);
if (fails.length) {
  console.error(`\nFAIL — ${fails.length}:`);
  fails.forEach((f) => console.error('  ✗ ' + f));
  process.exit(1);
}
console.log('commons-names: PASS');
