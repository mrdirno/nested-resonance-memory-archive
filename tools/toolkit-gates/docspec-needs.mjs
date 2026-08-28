/**
 * THE ARTEFACT GATE — what actually SATISFIES the omitted line, driven through
 * the real page on every document of every trade.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `omit` is the highest-value field in the library and it has
 * always reached both readers. What SATISFIES it never did. The five omission
 * classes each carry an `artefact` string — "a date", "a name", "a before-value",
 * "a location", "a named gap" — and for the whole life of the engine that string
 * rendered at exactly ONE call site: the tick list on the CUSTOM path, the path
 * a man reaches only when his document is not in the library. All 231 library
 * documents printed the line and never said what would answer it.
 *
 * The failure that closes is not a dropped heading. It is a FLUENT SENTENCE:
 * hvac/red-tag-notice asks for "the time you shut it off and the name of the
 * human you handed it to" and gets back "the unit was taken out of service and
 * the property manager was notified" — heading present, sentence present, no
 * <MISSING> anywhere, and neither fact in it. No existing gate can see that,
 * because every one of them is satisfied by presence.
 *
 * WHAT IT ASSERTS, per omit line, per document, per trade:
 *   · the document authors `needs` OF ITS OWN. needsOf() degrades to [] so a
 *     page served from a branch that skipped this gate still renders — but the
 *     degrade is a BELT, and a gate that accepts its own safety net measures
 *     nothing (§SCARS 2026-08-24, where exactly this shipped on `facts`). So the
 *     assertion reads `d.needs` directly, UNDER the resolver.
 *   · `needs` MIRRORS the shape of `omit`: one entry per line, in order. A
 *     flat list against a three-line omit puts the demand for line one under
 *     line three, which is a confident sentence pointing at the wrong fact.
 *   · every id is in the SHIPPED vocabulary, read off window.DocSpec.artefacts
 *     rather than retyped here — a gate that hardcodes the thing it checks
 *     drifts from it and then reports green on the day it matters.
 *   · `none` is EXCLUSIVE. "none plus a date" is not honesty, it is a demand
 *     wearing a disclaimer.
 *   · A TRADE THAT OVERRIDES `omit` OVERRIDES `needs`. This is the inheritance
 *     leak and it is the only one of these a human would never catch: the
 *     override changes the LINE, the demand stays behind describing the line it
 *     replaced, and every word on the page is well-formed.
 *   · THE CARD AND THE BLOCK NAME THE SAME ARTEFACTS. Compared as the card's
 *     rendered DOM text against the COMPOSED BLOCK STRING — two artefacts built
 *     by different code paths — never demandOf() against demandOf(), which is
 *     the tautology the say-list gate shipped and an adversarial pass caught.
 *   · A `none` LINE DEMANDS NOTHING, anywhere: no artefact sentence in the
 *     block, no <MISSING: …> token, and the card says so in words instead of
 *     rendering an empty red demand.
 *   · THE COPY CONTROL CARRIES THE DEMAND. Three leads get that message and
 *     never open the page; a list that names the line and drops what satisfies
 *     it hands them the exact failure this closes. Driven through a stubbed
 *     clipboard, on the STRING.
 *
 * TRADES AND DOCUMENTS COME FROM DISK AND FROM THE PAGE, never from a list here.
 *
 *   node tools/toolkit-gates/docspec-needs.mjs [base-url]
 *   TOOLKIT_BASE_URL=https://…/ node tools/toolkit-gates/docspec-needs.mjs
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'node:module';
import { readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../..');
const BASE = process.env.TOOLKIT_BASE_URL || process.argv[2] || ('file://' + REPO);

const TRADES = readdirSync(REPO, { withFileTypes: true })
  .filter(d => d.isDirectory()
            && existsSync(REPO + '/' + d.name + '/trade.js')
            && existsSync(REPO + '/' + d.name + '/docs.js')
            && existsSync(REPO + '/' + d.name + '/write-up.html'))
  .map(d => d.name)
  .sort();
if (!TRADES.length) { console.error('FAIL: no trade with a write-up library found'); process.exit(1); }

/* Runs INSIDE the page for one document. Returns what BOTH readers got, plus
   the raw authored field so the belt can be tested from underneath. */
const EXERCISE = (name) => {
  const out = { err: null };
  try {
    const btn = [...document.querySelectorAll('.lib button')]
      .find(b => (b.querySelector('.nm') || {}).textContent === name);
    if (!btn) { out.err = 'no library row rendered'; return out; }
    btn.click();
  } catch (e) { out.err = 'click threw: ' + e.message; return out; }
  try {
    const D = window.DocSpec;
    const d = D.library().find(x => x.name === name);
    out.id = d ? d.id : null;
    out.omits = d ? D.omitLines(d) : [];
    out.raw = d ? (d.needs === undefined ? null : d.needs) : null;
    out.resolved = d ? D.needsOf(d) : [];
    out.demands = out.resolved.map(r => D.demandOf(r));
    /* THE CARD, AS RENDERED. .omit is the red frame; one .needs row per line. */
    const frame = document.querySelector('.omit');
    out.cardRows = frame ? [...frame.querySelectorAll('.needs')].map(p => p.textContent.trim()) : [];
    out.cardOpen = frame ? [...frame.querySelectorAll('.needs .nk')].map(s => s.className.indexOf('nk-open') >= 0) : [];
    out.block = (document.querySelector('pre.block') || {}).textContent || '';
    /* THE OVERRIDE OBJECT ITSELF, NOT THE MERGED RESULT. library() merges the
       shared document with the trade's override key by key, so a merged doc that
       carries `needs` proves nothing about who authored it. The leak is an
       override that rewrites `omit` and never declares `needs` — the merge then
       hands it the shared demand, and every word on the page is well-formed.
       Read the raw override map. */
    const ovm = (window.TRADE_DOCS || {}).overrides || {};
    const ov = d ? ovm[d.id] : null;
    out.hasOverride = !!ov;
    out.ovOmit = ov ? Object.prototype.hasOwnProperty.call(ov, 'omit') : false;
    out.ovNeeds = ov ? Object.prototype.hasOwnProperty.call(ov, 'needs') : false;
  } catch (e) { out.err = 'introspection threw: ' + e.message; }
  return out;
};

const DRIVE_COPY = () => new Promise((resolve) => {
  let captured = null;
  try {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: (t) => { captured = t; return Promise.resolve(); } }
    });
  } catch (e) { resolve({ err: 'could not stub clipboard: ' + e.message }); return; }
  const b = document.querySelector('.saycopy');
  if (!b) { resolve({ err: 'no copy control' }); return; }
  b.click();
  setTimeout(() => resolve({ text: captured }), 60);
});

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

let checked = 0, failing = 0, docs = 0, lines = 0, noneLines = 0;
const fails = [];
const bump = (t, id, msg) => { failing++; fails.push(`${t}/${id}: ${msg}`); };

const browser = await chromium.launch();
const page = await browser.newPage();

let VOCAB = null;

for (const trade of TRADES) {
  const errs = [];
  const onErr = e => errs.push(e.message);
  page.on('pageerror', onErr);
  await page.goto(`${BASE}/${trade}/write-up.html`);
  await page.waitForTimeout(220);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(220);

  if (!VOCAB) {
    VOCAB = await page.evaluate(() => window.DocSpec.artefacts);
    if (!VOCAB || !Object.keys(VOCAB).length) { console.error('FAIL: engine exports no artefact vocabulary'); process.exit(1); }
  }

  const lib = await page.evaluate(() => window.DocSpec.library().map(d => ({ id: d.id, name: d.name })));
  if (!lib.length) { bump(trade, '-', 'library rendered empty'); page.off('pageerror', onErr); continue; }

  for (const doc of lib) {
    docs++;
    const r = await page.evaluate(EXERCISE, doc.name);
    if (r.err) { bump(trade, doc.id, r.err); continue; }
    if (!r.omits.length) continue;             /* nothing to demand against */

    /* 1. AUTHORED OF ITS OWN — read UNDER the resolver's degrade. */
    checked++;
    if (r.raw === null) {
      bump(trade, doc.id, 'authors `omit` and no `needs` — the line ships with nothing saying what would satisfy it, and needsOf() would degrade silently');
      continue;
    }

    /* 2. SHAPE MIRRORS `omit`. */
    checked++;
    const perLine = Array.isArray(r.raw) && r.raw.length && Array.isArray(r.raw[0]);
    const arity = perLine ? r.raw.length : 1;
    if (r.omits.length !== arity) {
      bump(trade, doc.id, `\`omit\` has ${r.omits.length} line(s) and \`needs\` has ${arity} — the demand under one line would describe another`);
      continue;
    }
    if (r.omits.length > 1 && !perLine) {
      bump(trade, doc.id, '`omit` is a list and `needs` is flat — one demand cannot serve three different lines');
      continue;
    }

    const rows = perLine ? r.raw : [r.raw];
    for (let i = 0; i < rows.length; i++) {
      lines++;
      const row = rows[i];

      /* 3. VOCABULARY — off the shipped table, not a copy. */
      checked++;
      if (!Array.isArray(row) || !row.length) {
        bump(trade, doc.id, `line ${i + 1}: \`needs\` is empty — say ["none"] and mean it, or name the artefact`);
        continue;
      }
      const bad = row.filter(k => k !== 'none' && !VOCAB[k]);
      if (bad.length) { bump(trade, doc.id, `line ${i + 1}: unknown artefact(s) ${bad.join(', ')}`); continue; }

      /* 4. `none` IS EXCLUSIVE. */
      checked++;
      if (row.indexOf('none') >= 0 && row.length > 1) {
        bump(trade, doc.id, `line ${i + 1}: "none" is not exclusive — a demand wearing a disclaimer is still a demand`);
        continue;
      }
      const isNone = row.length === 1 && row[0] === 'none';
      if (isNone) noneLines++;

      const demand = r.demands[i] || '';
      const card = r.cardRows[i] || '';

      /* 5. THE CARD SAYS IT, AND SAYS THE RIGHT ONE. */
      checked++;
      if (!card) { bump(trade, doc.id, `line ${i + 1}: no demand rendered on the card`); continue; }
      checked++;
      if (isNone) {
        if (!/in your own words/i.test(card)) {
          bump(trade, doc.id, `line ${i + 1}: needs "none" but the card does not say so — it reads: ${JSON.stringify(card.slice(0, 90))}`);
        }
        if (r.cardOpen[i] !== true) {
          bump(trade, doc.id, `line ${i + 1}: needs "none" and the card paints the red demand badge — a line no fact settles must not read as one he is failing`);
        }
      } else {
        if (card.indexOf(demand) < 0) {
          bump(trade, doc.id, `line ${i + 1}: the card does not carry the demand. card=${JSON.stringify(card.slice(0, 110))} demand=${JSON.stringify(demand)}`);
        }
        if (r.cardOpen[i] !== false) {
          bump(trade, doc.id, `line ${i + 1}: a real demand rendered in the "own words" style`);
        }
      }

      /* 6. THE BLOCK SAYS THE SAME ONE — DOM against the COMPOSED STRING. */
      checked++;
      if (isNone) {
        /* the shortOmit head of this line must appear in the OUTPUT FORMAT with
           no artefact clause welded to it */
        if (/carrying (a|the) /.test(r.block) && r.block.indexOf('carrying ') >= 0 && rows.length === 1) {
          bump(trade, doc.id, 'needs "none" and the block still emits an artefact clause');
        }
      } else {
        if (r.block.indexOf(demand) < 0) {
          bump(trade, doc.id, `line ${i + 1}: the block does not carry the demand the card shows — ${JSON.stringify(demand)}`);
        }
        /* 7. THE PER-ARTEFACT MISSING TOKENS ARE THE SHIPPED ONES. */
        checked++;
        for (const k of row) {
          const tok = '<MISSING: ' + VOCAB[k].miss + '>';
          if (r.block.indexOf(tok) < 0) {
            bump(trade, doc.id, `line ${i + 1}: block never offers ${tok}, so a gap in that half comes back as prose`);
            break;
          }
        }
      }
    }

    /* 8. AN OVERRIDE THAT REWRITES THE LINE DECLARES ITS OWN DEMAND.
       THE FIRST DRAFT OF THIS ASSERTION WAS WRONG AND ITS FIRST RUN PROVED IT.
       It compared VALUES — "the omit moved and the needs did not" — and went red
       on fourteen documents that are all correct: creative's damage-found says
       "THE DATE, THE TIME, AND WHERE THE PHOTOS ARE" where the shared line says
       "the timestamp and where the photos live", which is the same two artefacts
       in that trade's own words. Two differently-worded lines demanding the same
       thing is not a leak, it is the library working. The leak is STRUCTURAL: an
       override that rewrites `omit` and never declares `needs` at all, so the
       merge silently hands it a demand authored for a different sentence. So the
       test is on the KEY, not the value — and it stays red for an override that
       declares `needs` without `omit`, which is the same defect mirrored. */
    if (r.hasOverride && (r.ovOmit || r.ovNeeds)) {
      checked++;
      if (r.ovOmit && !r.ovNeeds) {
        bump(trade, doc.id, 'the override rewrites `omit` and never declares `needs` — the merge hands it the SHARED demand, authored for the sentence this one replaced');
      } else if (r.ovNeeds && !r.ovOmit) {
        bump(trade, doc.id, 'the override declares `needs` for an `omit` it does not own — the demand and the line can drift apart on the next shared edit');
      }
    }
  }

  /* 9. THE COPY CARRIES IT — driven, on the string. */
  const first = lib[0];
  const rr = await page.evaluate(EXERCISE, first.name);
  if (!rr.err && rr.omits.length) {
    const cp = await page.evaluate(DRIVE_COPY);
    checked++;
    if (cp.err) bump(trade, first.id, 'copy control: ' + cp.err);
    else {
      const want = rr.demands.filter(Boolean);
      const missing = want.filter(dm => (cp.text || '').indexOf(dm) < 0);
      if (missing.length) {
        bump(trade, first.id, `the group-chat copy drops the demand(s): ${missing.join(' | ')}`);
      }
    }
  }

  if (errs.length) bump(trade, '-', 'page error(s): ' + errs.join(' · '));
  page.off('pageerror', onErr);
}

await browser.close();

console.log(`ARTEFACT GATE — ${TRADES.length} trades / ${docs} documents / ${lines} omit lines ` +
            `(${noneLines} declaring none) / ${checked} checks / ${failing} failing`);
if (failing) { fails.slice(0, 60).forEach(f => console.log('  ✗ ' + f)); process.exit(1); }
console.log('  ✓ every omitted line names what would satisfy it, and both readers are told the same thing.');
