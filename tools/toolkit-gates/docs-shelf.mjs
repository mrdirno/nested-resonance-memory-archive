/**
 * THE SHELF GATE — one word, one document, on every shelf on the rack.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `shared/docsindex.js` has refused, since the day it was
 * written, to POOL a term that means two different documents — "a term meaning
 * two different documents anywhere on the rack is excluded", 35 of them refused,
 * and the deploy regenerates the file and rejects a diff so the claim cannot rot.
 * Nothing refused to AUTHOR one. The rail existed at the pooling layer and was
 * absent one layer up, where the words are actually written, and on 2026-09-02
 * the measurement said what that cost on the merged shelves a man actually sees:
 *
 *   19 ambiguous whole terms across 16 shelves — "damage" alone on 12 of them,
 *   sitting as an alias on `incident-report` AND on `damage-found`, whose name
 *   opens with the word;
 *   21 authored aliases, of 1,707 probed at the real search box, that handed back
 *   a DIFFERENT document than the one their author wrote them on — "meeting" on
 *   16 of 16, because "Toolbox Talk / Safety Meeting Note" carried the word in
 *   its NAME and a name outranks an alias.
 *
 * Neither is visible to any gate we had. docspec-config drives every document and
 * passes: each one composes. find-honesty drives the box and passes: the LABEL is
 * honest either way — "exact" is a true statement about a tie. Only asking the
 * shelf to name ONE document per word catches it.
 *
 * WHAT IT ASSERTS, per trade, all of it derived from the shipped engine and the
 * shelf's own data so a document added next month is covered the day it lands:
 *
 *   A  AMBIGUITY   no whole name-or-alias term on the merged shelf resolves to
 *                  more than one document. Read out of window.DocSpec.library(),
 *                  which is the merge the page itself renders.
 *   B  LEAD        every authored alias, typed WHOLE into the real search box,
 *                  leads the document its author wrote it on. This is the half A
 *                  cannot see: nothing is ambiguous when a name eats an alias
 *                  outright, and the author's intent is defeated all the same.
 *   C  DROP        every id in a trade's `drop` names a real shared document. A
 *                  typo there drops nothing, silently, forever. The words a drop
 *                  takes off the shelf are COUNTED and printed, never failed:
 *                  roofing's drop is a document displaced by a document, so its
 *                  words had to be carried over and were; creative's is a
 *                  document displaced by a shipped TOOL, so its words leave on
 *                  purpose. Only a human can tell those apart, so this reports.
 *
 * NEGATIVE CONTROL — a gate nobody has watched fail is a decoration.
 *     node tools/toolkit-gates/docs-shelf.mjs --prove
 * re-authors the defect on every shelf out of that shelf's OWN data (A: copy one
 * document's alias onto another; B: probe a word that lives in a different
 * document's name) and REQUIRES both to go red. --prove exits non-zero if the
 * detectors stay green.
 *
 *     node tools/toolkit-gates/docs-shelf.mjs [base-url] [--only=trade] [--prove]
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
const PROVE = args.includes('--prove');
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js')
                              && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name)
  .filter(t => !only || t === only)
  .sort();

/* Runs INSIDE the page, against the merged library the page itself rendered and
   the search box a man actually types into. `prove` re-authors the defect from
   this shelf's own data — never from a string kept here, which would drift. */
const EXERCISE = async (prove) => {
  const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
  const lib = window.DocSpec.library();
  const dropped = (window.TRADE_DOCS && window.TRADE_DOCS.drop) || [];
  const sharedIds = window.DocSpec.shared.map(d => d.id);
  const out = { ambiguous: [], lead: [], drop: [], darkened: [], probes: 0 };

  /* ── A · AMBIGUITY ─────────────────────────────────────────────────────── */
  const claims = {};
  const own = lib.map(d => ({ id: d.id, terms: [norm(d.name), ...(d.aka || []).map(norm)].filter(Boolean) }));
  if (prove && own.length > 1) {
    /* copy a term off document 0 onto document 1 — the exact shape of the defect */
    const stolen = own[0].terms.find(t => t && !own[1].terms.includes(t));
    if (stolen) own[1].terms.push(stolen);
  }
  for (const d of own) for (const t of new Set(d.terms)) (claims[t] = claims[t] || new Set()).add(d.id);
  for (const [term, ids] of Object.entries(claims)) if (ids.size > 1) out.ambiguous.push({ term, ids: [...ids] });

  /* ── B · LEAD ──────────────────────────────────────────────────────────── */
  const si = document.querySelector('input[type=search][aria-label="Search documents"]');
  const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  const type = async (q) => {
    set.call(si, q); si.dispatchEvent(new Event('input', { bubbles: true }));
    await new Promise(r => setTimeout(r, 0));
    const rows = [...document.querySelectorAll('ul.lib > li .nm')].map(n => n.textContent);
    return rows;
  };
  const probes = [];
  for (const d of lib) for (const a of (d.aka || [])) probes.push({ doc: d.name, alias: a });
  if (prove) {
    /* a word that lives in ANOTHER document's name is exactly what defeated 21
       authored aliases; claim one for a document that never wrote it */
    const victim = lib[0], thief = lib.find(d => d !== victim && /\s/.test(d.name));
    const word = thief && norm(thief.name).split(' ').find(w => w.length > 4 && !norm(victim.name).includes(w));
    if (word) probes.push({ doc: victim.name, alias: word });
  }
  for (const p of probes) {
    out.probes++;
    const rows = await type(p.alias);
    if (rows[0] !== p.doc) out.lead.push({ alias: p.alias, wrote: p.doc, led: rows[0] || '(nothing)' });
  }
  await type('');

  /* ── C · DROP ──────────────────────────────────────────────────────────── */
  for (const id of dropped) {
    if (!sharedIds.includes(id)) { out.drop.push(id); continue; }
    const gone = window.DocSpec.shared.find(d => d.id === id);
    const live = new Set(lib.flatMap(d => [norm(d.name), ...(d.aka || []).map(norm)]));
    for (const a of (gone.aka || [])) if (!live.has(norm(a))) out.darkened.push({ id, alias: a });
  }
  return out;
};

const browser = await chromium.launch();
const fails = []; let checked = 0, darkened = 0, provedA = 0, provedB = 0;

for (const trade of TRADES) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 800 }, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(String(e)));
  await page.goto(`${BASE}/${trade}/write-up.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(400);

  const r = await page.evaluate(EXERCISE, PROVE);
  checked += r.probes + r.ambiguous.length;
  darkened += r.darkened.length;
  if (PROVE) { if (r.ambiguous.length) provedA++; if (r.lead.length) provedB++; }

  const bad = [];
  if (errs.length) bad.push(`page error: ${errs[0]}`);
  r.ambiguous.forEach(a => bad.push(`A ambiguous "${a.term}" → ${a.ids.join(' , ')}`));
  r.lead.forEach(l => bad.push(`B "${l.alias}" was written on «${l.wrote}» and led «${l.led}»`));
  r.drop.forEach(d => bad.push(`C drop "${d}" is not a shared document id — it drops nothing`));

  if (!PROVE && bad.length) fails.push({ trade, bad });
  console.log(`  ${trade.padEnd(12)} ${String(r.probes).padStart(4)} alias probe(s) · ` +
              `${r.ambiguous.length} ambiguous · ${r.lead.length} mis-led · ` +
              `${r.darkened.length} word(s) dark by drop${bad.length && !PROVE ? '   ** FAIL **' : ''}`);
  await ctx.close();
}
await browser.close();

console.log('');
if (PROVE) {
  const ok = provedA === TRADES.length && provedB === TRADES.length;
  console.log(`NEGATIVE CONTROL — A went red on ${provedA}/${TRADES.length} shelves, ` +
              `B went red on ${provedB}/${TRADES.length}. ${ok ? 'Both detectors work.' : 'A DETECTOR IS BLIND.'}`);
  process.exit(ok ? 0 : 1);
}
console.log(`SHELF GATE — ${TRADES.length} trade(s), ${checked} checks, ${fails.length} trade(s) failing` +
            (darkened ? ` · ${darkened} alias(es) left the shelf with a drop (reported, not failed)` : ''));
fails.forEach(f => f.bad.forEach(b => console.log(`  ${f.trade}: ${b}`)));
process.exit(fails.length ? 1 : 0);
