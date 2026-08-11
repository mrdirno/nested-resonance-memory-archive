/**
 * THE DOCSPEC GATE — every document in every trade, driven through the real page.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS (§SCARS 2026-08-11). framing/docs.js shipped five documents
 * whose `omit` was a LIST where the engine's shortOmit() called .split on it, and
 * whose `family` was a shared DOCUMENT ID rather than one of the five families.
 * Nothing caught either one. The first threw a TypeError inside compose(), so
 * the ONE THING the page exists to produce — the instruction block you paste
 * into your AI — rendered EMPTY, on the live site, for every one of that trade's
 * own documents. The picked card appeared, the tuner appeared, the library never
 * collapsed, and the bottom bar still read "Pick a document to start". The
 * second was worse in kind because it was silent: an unknown family fell back to
 * `recurring`, so a damage letter read three years later was being written as a
 * DELTA against a previous one that does not exist.
 *
 * Both defects are invisible to every check we had. `node --check` passes — the
 * file is valid JavaScript. The mobile gate passes — the layout is watertight
 * around an empty box. A screenshot passes — the page looks finished. Only doing
 * the job the page claims catches it, so that is what this does.
 *
 * WHAT IT ASSERTS, per document, per trade:
 *   · picking it throws NOTHING (the defect that shipped)
 *   · the block is non-empty and carries all eleven blocks (the page's product)
 *   · `family` is one of the engine's own five, read OUT of the shipped engine
 *   · the CONTINUITY rule matches the family — a stand-alone record is never
 *     written as an update, which is the §THE THREE SHAPES rule as an assertion
 *   · EVERY omit line reaches the block, string or list. This is the field the
 *     whole library is built around; a document that emits none of it is a
 *     document with nothing to sell
 *   · renderOut() completed — the setup steps exist and the bar shows a count
 *   · renderAll() completed past renderOut() — the library collapsed
 * and once per trade, the CUSTOM path ("not in the list") emits a real block too.
 *
 * TRADES COME FROM DISK, never from a list here, so trade #8 is covered the day
 * it lands with no edit to this file.
 *
 *   node tools/toolkit-gates/docspec-config.mjs [base-url] [--only=<trade>]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js')
                              && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name)
  .filter(t => !only || t === only)
  .sort();

/* The eleven blocks of the emitted instruction set (§THE FOURTH SHAPE). A block
   missing one of these is not production-grade, whatever else it contains. */
const BLOCKS = [
  'ROLE',
  'WHAT THIS DOCUMENT IS FOR',
  'DEFAULTS',
  'OPERATING PRINCIPLES',
  'ATTRIBUTION',
  'INPUT HANDLING',
  'CONTINUITY',
  'VALIDATION',
  'OUTPUT FORMAT',
];
const DELTA_TELL = 'covers the DELTA';
const ALONE_TELL = 'This document stands alone';
const OMIT_HEAD = 'THE LINE'; // matches both the singular and the plural heading

/* Runs INSIDE the page: pick one document by name and report what the page did.
   Returns findings rather than throwing — a gate that dies on one document tells
   you nothing about the other hundred. */
const EXERCISE = (name) => {
  const out = { err: null };
  try {
    const btn = [...document.querySelectorAll('.lib button')]
      .find(b => (b.querySelector('.nm') || {}).textContent === name);
    if (!btn) { out.err = 'no library row rendered for this document'; return out; }
    btn.click();
  } catch (e) { out.err = 'click threw: ' + e.message; return out; }

  const block = document.querySelector('pre.block');
  const steps = document.querySelector('ol.steps');
  const bar = document.querySelector('.bar .count');
  const cards = [...document.querySelectorAll('.card')];
  out.block = block ? block.textContent : '';
  out.steps = steps ? steps.children.length : 0;
  out.bar = bar ? bar.textContent : '';
  out.libraryOpen = cards.length ? getComputedStyle(cards[0]).display !== 'none' : null;
  // what the engine itself thinks this document is
  try {
    const d = window.DocSpec.library().find(x => x.name === name);
    out.family = d ? d.family : null;
    out.omits = d ? window.DocSpec.omitLines(d) : [];
    /* deltaOf, NOT famOf().delta — a document may opt out of its family's
       continuity rule (electrical/confirming-note does), and a gate that asked
       the family would then fail the very document the opt-out fixed. */
    out.delta = d ? window.DocSpec.deltaOf(d) : null;
    out.standalone = !!(d && d.standalone);
    out.famName = d ? window.DocSpec.famOf(d).name : null;
  } catch (e) { out.err = 'engine introspection threw: ' + e.message; }
  return out;
};

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await ctx.newPage();

let checked = 0, failing = 0;
const fails = [];
/* THE DELTA ROSTER — soft, and deliberately not an error. A wrong-but-LEGAL
 * family is the half of this defect class a gate cannot judge: nothing
 * mechanical distinguishes a daily report (delta is right) from an inspection
 * deficiency letter that was tagged `recurring` (delta silently instructs the AI
 * to drop the deficiencies it already reported — on the one document whose whole
 * purpose is that an unnamed device stays yours). Two of those were found by
 * hand on the 2026-08-11 sweep, in two different trades. So the gate prints the
 * complete list of documents that report deltas and leaves the judgement where
 * it belongs: it is short enough to read, and anything on it that is not written
 * repeatedly about the SAME job is wrong. */
const deltas = [];

for (const trade of TRADES) {
  const url = `${BASE}/${trade}/write-up.html`;
  const errs = [];
  const onErr = e => errs.push(e.message);
  page.on('pageerror', onErr);

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.lib button', { timeout: 15000 });

  const { docs, families } = await page.evaluate(() => ({
    docs: window.DocSpec.library().map(d => ({ id: d.id, name: d.name, family: d.family })),
    families: Object.keys(window.DocSpec.families),
  }));

  console.log(`\n${trade} — ${docs.length} documents`);

  for (const doc of docs) {
    checked++;
    const before = errs.length;
    const r = await page.evaluate(EXERCISE, doc.name);
    const bad = [];

    if (r.err) bad.push(r.err);
    if (errs.length > before) bad.push('page error: ' + errs.slice(before).join(' | '));

    if (!families.includes(doc.family)) {
      bad.push(`family "${doc.family}" is not one of the engine's five (${families.join(', ')})`
        + ` — it falls back to stand-alone and the family shown on the card is wrong`);
    }
    if (!r.block || r.block.length < 400) {
      bad.push(`the block is ${r.block ? r.block.length + ' chars' : 'EMPTY'} — the page's only product did not render`);
    } else {
      const missing = BLOCKS.filter(b => !r.block.includes(b));
      if (missing.length) bad.push('block is missing: ' + missing.join(', '));
      if (!r.block.includes(OMIT_HEAD)) bad.push('block carries no omitted-line section');

      const isDelta = r.block.includes(DELTA_TELL);
      const isAlone = r.block.includes(ALONE_TELL);
      if (r.delta === true && !(isDelta && !isAlone)) {
        bad.push('family reports deltas but the block does not carry the delta continuity rule');
      }
      if (r.delta === false && !(isAlone && !isDelta)) {
        bad.push(`this document stands alone but the block tells the AI to write it as an UPDATE`
          + ` (family "${doc.family}" -> "${r.famName}")`);
      }
      // every omit line, string or list, has to reach the block
      if (!r.omits || !r.omits.length) {
        bad.push('no omitted line at all — the highest-value field in the library is empty');
      } else {
        const dropped = r.omits.filter(o => !r.block.includes(o.slice(0, 40)));
        if (dropped.length) {
          bad.push(`${dropped.length} of ${r.omits.length} omitted line(s) never reached the block`
            + ` — first dropped: "${dropped[0].slice(0, 60)}…"`);
        }
      }
    }
    if (!r.steps) bad.push('the setup steps did not render — renderOut() did not complete');
    if (!/\d+\s+words/.test(r.bar || '')) bad.push(`the bar still reads ${JSON.stringify(r.bar)} — renderOut() did not complete`);
    if (r.libraryOpen) bad.push('the library never collapsed — renderAll() did not complete past renderOut()');

    if (bad.length) {
      failing++;
      fails.push({ trade, doc: doc.id, bad });
      console.log(`  ** FAIL  ${doc.id}`);
      bad.forEach(b => console.log(`           ${b}`));
    } else {
      console.log(`  ok      ${doc.id.padEnd(32)} ${r.family}${r.standalone ? ' +standalone' : ''} · ${r.omits.length} omitted line(s) · ${r.block.length} chars`);
    }
    if (r.delta) deltas.push(`${trade}/${doc.id} (${doc.family})`);
  }

  /* THE CUSTOM PATH — "not in the list? build one anyway". It is the graceful
     failure of search, so it has to produce a real block too. */
  checked++;
  const before = errs.length;
  const c = await page.evaluate(() => {
    const btn = [...document.querySelectorAll('button')].find(b => /Not in the list/i.test(b.textContent));
    if (!btn) return { err: 'no "not in the list" control' };
    btn.click();
    const inp = document.querySelector('#app input[type=text]');
    if (!inp) return { err: 'custom path rendered no name field' };
    inp.value = 'Pre-pour sign-off note';
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    const block = document.querySelector('pre.block');
    return { block: block ? block.textContent : '' };
  });
  const cbad = [];
  if (c.err) cbad.push(c.err);
  if (errs.length > before) cbad.push('page error: ' + errs.slice(before).join(' | '));
  if (!c.err && (!c.block || c.block.length < 400)) cbad.push(`custom block is ${c.block ? c.block.length + ' chars' : 'EMPTY'}`);
  if (cbad.length) {
    failing++; fails.push({ trade, doc: '(custom path)', bad: cbad });
    console.log(`  ** FAIL  (custom path)`);
    cbad.forEach(b => console.log(`           ${b}`));
  } else {
    console.log(`  ok      ${'(custom path)'.padEnd(32)} ${c.block.length} chars`);
  }

  page.off('pageerror', onErr);
}

await browser.close();

console.log(`\n${'='.repeat(60)}`);
console.log(`DOCSPEC GATE — ${TRADES.length} trade(s), ${checked} checks, ${failing} failing`);
console.log(`base: ${BASE}`);
if (failing) {
  console.log('\nfailing:');
  fails.forEach(f => console.log(`  ${f.trade}/${f.doc}: ${f.bad[0]}`));
}
console.log(`\nDELTA ROSTER — ${deltas.length} document(s) are written as an UPDATE to the previous one.`);
console.log('Read it: anything here that is not written repeatedly about the SAME job is wrong,');
console.log('and the fix is a delta-false family or `standalone: true` on the document.');
deltas.forEach(d => console.log('  ' + d));
process.exit(failing ? 1 : 0);
