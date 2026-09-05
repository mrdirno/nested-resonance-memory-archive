/**
 * THE POOLED VOCABULARY GATE — driven through the real search box on real pages.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `shared/docsindex.js` is a GENERATED union of every name and
 * `aka` any of the thirteen trades wrote for a document, added to the search
 * index of every trade that already carries that document. Two things about that
 * sentence can silently stop being true, and neither is visible to any check this
 * repo already owns:
 *
 *   · THE TAG. shared/docspec.js reads `window.DOCS_POOL` and degrades to the
 *     trade's own words when it is absent. A page that lost the <script> line
 *     looks completely normal, returns 200, and quietly searches one man's
 *     vocabulary again. This is the `commons/tips.html` scar exactly — a shared
 *     engine reading a `window.X` a page must supply — and it is asserted here on
 *     the REAL PAGE (`window.DOCS_POOL` actually defined), never by grepping for
 *     a filename, because a grep passes on the comment that explains the absence.
 *   · THE BOUNDARY. Pooling must widen SEARCH and nothing else. `aka` also feeds
 *     the ROUTER line inside the block a man pastes into his AI, so a pooled term
 *     reaching `library()` would put another trade's word into his document. And
 *     a pooled term must never introduce a document the trade does not hold —
 *     that is the entitlement rail, and it is the only reason this needs no
 *     permission model.
 *
 * WHAT IT ASSERTS, per trade, on the shipped pages:
 *   1  DOCS_POOL is live on the page (the tag, proved by the object, not the text)
 *   2  every pooled document id is carried by TWO OR MORE trades — the 57
 *      single-trade documents can never push a word onto anybody
 *   3  pooling introduces NO document: ids before === ids after, exactly
 *   4  the merged library the BLOCK is built from carries none of the pooled
 *      terms — search widened, the document's own name for itself did not
 *   5  every pooled term for a document this trade carries actually RETURNS that
 *      document through the real box
 *   6  every word the trade's OWN author wrote still returns its document — the
 *      regression half, because a wider index can bury a narrow hit
 *   7  the near-name quarantine is REAL: a pair one edit apart owned by different
 *      documents is absent from the pool, asserted by name on the live data
 *   8  a pooled word is LABELLED as another trade's name for it, so a man never
 *      mistakes a word that works for the word his trade writes down
 *
 *   node tools/toolkit-gates/docs-pool.mjs [base-url]
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
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name).sort();

/* The near-name pairs the generator quarantined, named here so the rail is a test
   and not a claim. Each is one edit apart on the squashed form and belongs to a
   DIFFERENT document: "not us" is the damage note, "notes" is the minutes; "what
   we laid" is flooring's own record, "what we said" is the minutes. If a later
   cycle relaxes the quarantine these come back and this fails. */
const QUARANTINED = ['not us', 'notes', 'what we said', 'what we laid', 'blocked', 'locked', 'flash', 'clash'];

let checked = 0, failing = 0;
const fail = (m) => { console.log('  FAIL  ' + m); failing++; };
const ok = (m) => { console.log('  ok    ' + m); checked++; };

const browser = await chromium.launch();
const page = await browser.newPage();

/* Pass 1 — who carries what, read out of each engine's own merge. */
const carriers = new Map();
for (const t of TRADES) {
  await page.goto(`${BASE}/${t}/write-up.html`, { waitUntil: 'load' });
  const ids = await page.evaluate(() => window.DocSpec.library().map(d => d.id));
  for (const id of ids) { if (!carriers.has(id)) carriers.set(id, new Set()); carriers.get(id).add(t); }
}

let poolIds = [];
for (const t of TRADES) {
  console.log(`\n${t}`);
  await page.goto(`${BASE}/${t}/write-up.html`, { waitUntil: 'load' });

  const r = await page.evaluate(() => {
    const D = window.DocSpec;
    const lib = D.library();
    const pool = D.pooled(lib);
    const si = document.querySelector('.srch input');
    const n2i = {}; lib.forEach(d => n2i[d.name] = d.id);
    const search = (q) => {
      si.value = q; si.dispatchEvent(new Event('input'));
      return {
        ids: [...document.querySelectorAll('.lib li:not(.grp) .nm')].map(n => n2i[n.textContent]).filter(Boolean),
        grps: [...document.querySelectorAll('.lib li.grp')].map(n => n.textContent)
      };
    };
    const out = {
      hasPool: !!window.DOCS_POOL,
      poolIds: window.DOCS_POOL ? Object.keys(window.DOCS_POOL) : [],
      libIds: lib.map(d => d.id),
      pooledIds: pool.map(d => d.id),
      libAka: {},          // what the BLOCK is built from
      poolOnly: {},        // what search gained
      poolProbe: [],       // pooled term -> which ids came back
      ownProbe: [],        // the trade's own words, the regression half
      labelProbe: null,
      overrule: [],        // 9 — a loan taken over this shelf's own author
      claims: 0
    };
    lib.forEach(d => out.libAka[d.id] = [d.name].concat(d.aka || []));
    pool.forEach(d => { if (d.poolOnly && d.poolOnly.length) out.poolOnly[d.id] = d.poolOnly.slice(); });
    /* 9 · A CLAIM BEATS A LOAN. Every whole term this shelf's OWN authors wrote,
       and who wrote it. Then: did the pool hand any of those words to a DIFFERENT
       document on this same shelf? The pool is generated from the SHARED documents
       only, so every trade-specific document is invisible to it — which is exactly
       the kind that gets its word taken. Read off window.DOCS_POOL rather than off
       poolOnly, because poolOnly is the engine's answer and this must be able to
       fail when that answer is wrong. */
    const claim = {};
    lib.forEach(d => [d.name].concat(d.aka || []).forEach(w => {
      const k = window.Find.norm(w);
      if (k) claim[k] = (claim[k] && claim[k] !== d.id) ? '*' : d.id;   // '*' = shelf gate A's job
    }));
    out.claims = Object.keys(claim).length;
    const P = window.DOCS_POOL || {};
    lib.forEach(d => (P[d.id] || []).forEach(term => {
      const k = window.Find.norm(term);
      const owner = claim[k];
      if (!owner || owner === '*' || owner === d.id) return;
      const lent = (out.poolOnly[d.id] || []).some(x => window.Find.norm(x) === k);
      if (lent) out.overrule.push([term, d.id, owner, search(term).ids[0] || '-']);
    }));
    for (const id of Object.keys(out.poolOnly)) for (const term of out.poolOnly[id]) {
      const s = search(term);
      out.poolProbe.push([term, id, s.ids.includes(id), s.ids[0] === id]);
      if (!out.labelProbe && s.ids[0] === id) out.labelProbe = [term, id, s.grps.slice()];
    }
    lib.forEach(d => [d.name].concat(d.aka || []).forEach(w => {
      const s = search(w);
      out.ownProbe.push([w, d.id, s.ids.includes(d.id)]);
    }));
    si.value = ''; si.dispatchEvent(new Event('input'));
    return out;
  });

  /* 1 — the tag, proved by the object it must define */
  if (!r.hasPool) fail(`${t}/write-up.html does not define window.DOCS_POOL — the page lost <script src="../shared/docsindex.js">, and search silently narrowed to one author's words`);
  else ok(`DOCS_POOL live on the page (${r.poolIds.length} document ids)`);
  poolIds = r.poolIds;

  /* 3 — pooling introduces no document */
  const a = r.libIds.join('|'), b = r.pooledIds.join('|');
  if (a !== b) fail(`${t}: pooled() changed the library — ${r.libIds.length} ids in, ${r.pooledIds.length} out. Pooling may only widen SEARCH`);
  else ok(`library unchanged by pooling: ${r.libIds.length} documents in, ${r.libIds.length} out`);

  /* 4 — the block never sees a pooled word */
  let leaked = 0;
  for (const id of Object.keys(r.poolOnly)) {
    const mine = new Set(r.libAka[id].map(x => String(x).toLowerCase()));
    for (const term of r.poolOnly[id]) if (mine.has(String(term).toLowerCase())) leaked++;
  }
  if (leaked) fail(`${t}: ${leaked} pooled term(s) reached the merged library — they would print in the ROUTER line of the block he pastes into his AI`);
  else ok(`block vocabulary untouched: ${Object.keys(r.poolOnly).length} document(s) widened for search only`);

  /* 9 — A CLAIM BEATS A LOAN: the pool never takes a word off this shelf's own
     author. Added 2026-09-05, and it is a gate because it already bit: paving's
     author moved "delay" onto his own lost-day document and off the general
     notice, and typing "delay" still led the general notice because sixteen other
     shelves had voted the word onto `delay-notice` and the pool lent it back. The
     shelf gate caught that one downstream, as a mis-led alias; this catches the
     CAUSE, on every shelf, including the shared documents the shelf gate's B probe
     would report only as somebody else's failure. */
  if (r.overrule.length) fail(`${t}: ${r.overrule.length} pooled term(s) overrule this shelf's own author — ` +
    r.overrule.map(([term, lent, owner, led]) => `"${term}" lent to ${lent} though ${owner} claims it (box led ${led})`).join('; '));
  else ok(`no loan overrules an author: ${r.claims} claimed term(s) on this shelf, 0 taken by the pool`);

  /* 5 — every pooled term actually finds its document */
  const missed = r.poolProbe.filter(p => !p[2]);
  if (missed.length) fail(`${t}: ${missed.length}/${r.poolProbe.length} pooled term(s) do not return their document — e.g. "${missed[0][0]}" -> ${missed[0][1]}`);
  else ok(`${r.poolProbe.length} pooled term(s) return their own document, ${r.poolProbe.filter(p => p[3]).length} of them first`);

  /* 6 — the regression half */
  const broke = r.ownProbe.filter(p => !p[2]);
  if (broke.length) fail(`${t}: ${broke.length} word(s) this trade's OWN author wrote stopped finding their document — a wider index buried a narrow hit — e.g. "${broke[0][0]}" -> ${broke[0][1]}`);
  else ok(`${r.ownProbe.length} of this trade's own words still find their document`);

  /* 8 — the label */
  if (!r.labelProbe) ok('no pooled term ranks first here — nothing to label');
  else if (!r.labelProbe[2].some(g => /Another trade/.test(g)))
    fail(`${t}: "${r.labelProbe[0]}" returns ${r.labelProbe[1]} first and the page does not say it is another trade's name for it — headings were [${r.labelProbe[2].join(' / ') || 'none'}]`);
  else ok(`a pooled word is labelled: "${r.labelProbe[0]}" -> "Another trade's name for it"`);
}

/* 2 — the entitlement rail, cross-trade */
console.log('\nrack-wide');
const orphan = poolIds.filter(id => (carriers.get(id) || new Set()).size < 2);
if (orphan.length) fail(`single-trade document(s) in the pool: ${orphan.join(', ')} — a word written for a document only one trade holds must never be pushed anywhere`);
else ok(`all ${poolIds.length} pooled document ids are carried by 2+ trades (${carriers.size - poolIds.length} single-trade documents excluded)`);

/* 7 — the quarantine, by name */
const inPool = new Set();
await page.goto(`${BASE}/${TRADES[0]}/write-up.html`, { waitUntil: 'load' });
const allTerms = await page.evaluate(() => {
  const out = [];
  const P = window.DOCS_POOL || {};
  for (const id of Object.keys(P)) for (const t of P[id]) out.push(window.Find.norm(t));
  return out;
});
allTerms.forEach(t => inPool.add(t));
const escaped = QUARANTINED.filter(q => inPool.has(q));
if (escaped.length) fail(`near-name quarantine leaked: ${escaped.map(x => '"' + x + '"').join(', ')} — each is one edit from a term meaning a DIFFERENT document, which is the strike/struck class`);
else ok(`near-name quarantine holds: ${QUARANTINED.map(x => '"' + x + '"').join(', ')} all absent from the pool`);

await browser.close();
console.log('\n' + '='.repeat(60));
console.log(`POOLED VOCABULARY GATE — ${TRADES.length} trade(s), ${checked + failing} checks, ${failing} failing`);
console.log(`base: ${BASE}`);
process.exit(failing ? 1 : 0);
