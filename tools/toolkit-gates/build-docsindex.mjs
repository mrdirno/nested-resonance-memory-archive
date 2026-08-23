/**
 * THE POOLED DOCUMENT VOCABULARY — generator and drift check.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS, measured before a line of it was written.
 *
 * Eight documents in this library live on all thirteen trades, and every trade
 * RENAMED them. `delay-notice` goes by seven different names across the rack;
 * `daily-report` six, `damage-found` six, `handover` six, `site-walk` five. Each
 * trade's author also wrote his own `aka` list — his record of what people
 * actually SAY for it. So the search on any one page knows ONE man's words for a
 * document that thirteen men named.
 *
 * Driven through the real search box on the real pages, 733 unambiguous terms
 * against all 13 trades — 9,529 searches:
 *
 *     his own library HOLDS the document, and the page found it     2,802
 *     his own library HOLDS it and the page returned something else 1,083
 *         of those, handed over with NO hedge, as an exact match      512
 *
 * The 512 are the ones that matter. "somebody got hurt" on the AV page returns
 * the Damage / Pre-Existing Condition Note, not the Incident / Near-Miss Report,
 * with no "Closest to" label on it. "first aid" returns the Turnover Summary.
 * "recordable" returns the Daily Field Report. The document he wants is sitting
 * in his own library under a name his trade's author did not happen to write.
 *
 * THE FIX IS NOT A FEATURE, IT IS A UNION. Every name and every `aka` anybody on
 * the rack wrote for a document id becomes searchable on every trade that ALREADY
 * CARRIES THAT DOCUMENT ID. No page gains a document. No block changes. The man
 * gets thirteen authors' vocabulary for his own shelf instead of one author's.
 *
 * WHAT A JUDGE PANEL CUT, and why the rails below are mechanisms rather than copy:
 *
 *   · A CROSS-TRADE HAND-OFF WAS KILLED 3-0. The other 5,644 misses are queries
 *     naming a document the reader's trade does not carry at all, and the obvious
 *     move — route him to the trade that owns it — was refused on consequence, not
 *     taste. Every instruction block introduces the reader in the OWNING trade's
 *     words: sitework's "A Line Got Hit" opens *"I am the foreman who was on the
 *     machine or in the hole; we do sitework and underground utility work."* A
 *     plumber sent there is handed a document that introduces him as somebody
 *     else, addressed to somebody else's chain, carrying somebody else's refusals.
 *     Today he gets a wrong document in his own voice and rejects it in two
 *     seconds; routed, he gets a plausible document in the wrong voice that he
 *     asked for by name. The failure gets quieter and more expensive.
 *   · SINGLE-TRADE DOCUMENTS ARE STRUCTURALLY UNPOOLABLE, and that is the whole
 *     safety argument. A term can only be pooled onto a trade that already has
 *     that document id, so of the 69 documents on the rack the 49 that live on
 *     exactly one trade can never push a word anywhere. The entitlement question
 *     — may this man author this document — is already settled by the document
 *     being on his page. That is why pooling needs no permission model and the
 *     hand-off would have needed one nobody can build client-side.
 *   · THE NEAR-NAME QUARANTINE (below) exists because `line-strike` (plumbing) and
 *     `line-struck` (sitework) are one stem apart and are different documents on
 *     different trades. Both are single-trade, so pooling cannot reach them — but
 *     "cannot happen today" is exactly the claim this repo has watched rot, so it
 *     is a rule in the generator and an assertion in the deploy instead.
 *
 * THE RAILS, all four checkable:
 *   R1  a term is pooled only if it resolves to exactly ONE document id across
 *       the whole rack, folded through the ENGINE'S OWN normalizer.
 *   R2  a term is quarantined if its squashed key is within one edit of a key
 *       owned by a DIFFERENT document id — the strike/struck class, refused
 *       before it can exist.
 *   R3  a document id is poolable only if two or more trades carry it.
 *   R4  the merged library comes from shared/docspec.js's own exported
 *       `library()`, in plain node with a synthetic window. This file never
 *       re-implements the merge, and the DEPLOY runs `--check` against the
 *       staged artifact and refuses a diff, so the generated file cannot drift
 *       from the thirteen libraries it claims to summarise.
 *
 *   node tools/toolkit-gates/build-docsindex.mjs            # write shared/docsindex.js
 *   node tools/toolkit-gates/build-docsindex.mjs --check    # fail on any diff
 *   node tools/toolkit-gates/build-docsindex.mjs --check --root=HELIOS-BRIDGE/dist
 */
import { readdirSync, existsSync, readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';

const args = process.argv.slice(2);
const CHECK = args.includes('--check');
const rootArg = (args.find(a => a.startsWith('--root=')) || '').slice(7);
const ROOT = (rootArg ? rootArg.replace(/\/?$/, '/') : fileURLToPath(new URL('../../', import.meta.url)));
const OUT = ROOT + 'shared/docsindex.js';

/* THE ENGINE'S OWN NORMALIZER AND ITS OWN MERGE, both loaded rather than copied.
   find.js is a plain IIFE; docspec.js exports before it mounts and returns early
   with no `document`, which is the only reason this runs without a browser. */
function loadEngine(tradeFiles) {
  const win = {};
  new Function('window', readFileSync(ROOT + 'shared/find.js', 'utf8'))(win);
  for (const f of tradeFiles) new Function('window', readFileSync(f, 'utf8'))(win);
  new Function('window', 'document', readFileSync(ROOT + 'shared/docspec.js', 'utf8'))(win, undefined);
  return win;
}

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(`${ROOT}${d.name}/docs.js`) && existsSync(`${ROOT}${d.name}/write-up.html`))
  .map(d => d.name).sort();
if (!TRADES.length) { console.error('FAIL: no trade docs.js found under ' + ROOT); process.exit(1); }

/* Pass 1 — every document every trade actually carries, out of the real merge. */
const probe = loadEngine([]);          // for norm/squash/dist only
const norm = probe.Find.norm, squash = probe.Find.squash, dist = probe.Find.dist;
const carriers = new Map();            // docId -> Set(trade)
const said = new Map();                // folded term -> Set(docId)
const surface = new Map();             // folded term -> the first spelling seen (what we ship)

for (const t of TRADES) {
  const win = loadEngine([`${ROOT}${t}/trade.js`, `${ROOT}${t}/docs.js`]);
  const lib = win.DocSpec.library();
  for (const d of lib) {
    if (!carriers.has(d.id)) carriers.set(d.id, new Set());
    carriers.get(d.id).add(t);
    for (const w of [d.name].concat(d.aka || [])) {
      const k = norm(w);
      if (!k) continue;
      if (!said.has(k)) { said.set(k, new Set()); surface.set(k, String(w)); }
      said.get(k).add(d.id);
    }
  }
}

/* R1 — one term, one document, or it is not pooled. */
const single = [...said].filter(([, ids]) => ids.size === 1).map(([k, ids]) => [k, [...ids][0]]);
const ambiguous = said.size - single.length;

/* R2 — the strike/struck class. A key within one edit of a key owned by a
   DIFFERENT document is quarantined in BOTH directions. Compared on the squashed
   form because that is the form the engine's fuzzy tier compares. */
const quarantined = new Set();
for (let i = 0; i < single.length; i++) {
  for (let j = i + 1; j < single.length; j++) {
    if (single[i][1] === single[j][1]) continue;
    const a = squash(single[i][0]), b = squash(single[j][0]);
    if (Math.abs(a.length - b.length) > 1) continue;
    if (dist(a, b, 1) <= 1) { quarantined.add(single[i][0]); quarantined.add(single[j][0]); }
  }
}

/* R3 — a document nobody else carries has nowhere to pool to, and the 49
   single-trade documents are the whole entitlement exposure. */
const POOL = {};
for (const [k, id] of single) {
  if (quarantined.has(k)) continue;
  if ((carriers.get(id) || new Set()).size < 2) continue;
  (POOL[id] = POOL[id] || []).push(surface.get(k));
}
for (const id of Object.keys(POOL)) POOL[id].sort((a, b) => norm(a) < norm(b) ? -1 : 1);

const ids = Object.keys(POOL).sort();
const nTerms = ids.reduce((a, id) => a + POOL[id].length, 0);

const body = `/* FIELD TOOLKIT — SHARED: THE POOLED DOCUMENT VOCABULARY.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * GENERATED — do not hand-edit. Regenerate with:
 *     node tools/toolkit-gates/build-docsindex.mjs
 * That file carries the measurement, the rails and the panel's reasoning; the
 * deploy runs it with --check against the staged artifact and refuses a diff, so
 * this cannot quietly stop being true.
 *
 * Eight documents live on all thirteen trades and every trade renamed them —
 * delay-notice alone goes by seven names. Each row below is one document id and
 * every name or \`aka\` ANY trade wrote for it. shared/docspec.js adds these to
 * the search index of a trade that ALREADY CARRIES that document id, so a man
 * searching his own shelf gets thirteen authors' words for it instead of one.
 *
 * It can never introduce a document: a term is only pooled onto trades that
 * already hold its document, single-trade documents are excluded outright, a
 * term meaning two different documents anywhere on the rack is excluded, and so
 * is any term within one edit of a term meaning a different document.
 *
 * ${TRADES.length} trades · ${ids.length} poolable document ids · ${nTerms} terms
 * · ${ambiguous} ambiguous term(s) refused · ${quarantined.size} quarantined as near-names
 */
window.DOCS_POOL = {
${ids.map(id => `  ${JSON.stringify(id)}: [${POOL[id].map(t => JSON.stringify(t)).join(', ')}]`).join(',\n')}
};
`;

if (CHECK) {
  const have = existsSync(OUT) ? readFileSync(OUT, 'utf8') : '';
  if (have !== body) {
    console.error('FAIL: shared/docsindex.js does not match what the thirteen libraries generate.');
    console.error('      A document, a name or an aka changed and the pooled vocabulary was not rebuilt.');
    console.error('      Run: node tools/toolkit-gates/build-docsindex.mjs');
    const a = have.split('\n'), b = body.split('\n');
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      if (a[i] !== b[i]) { console.error(`      first diff, line ${i + 1}:\n        on disk: ${a[i]}\n        rebuilt: ${b[i]}`); break; }
    }
    process.exit(1);
  }
  console.log(`POOLED VOCABULARY — in step with disk: ${TRADES.length} trades, ${ids.length} document ids, ${nTerms} terms, ${ambiguous} ambiguous refused, ${quarantined.size} near-names quarantined`);
} else {
  writeFileSync(OUT, body);
  console.log(`wrote ${OUT}`);
  console.log(`  trades              ${TRADES.length}`);
  console.log(`  documents on rack   ${carriers.size}   (poolable: ${ids.length}, single-trade and therefore excluded: ${[...carriers.values()].filter(s => s.size < 2).length})`);
  console.log(`  terms pooled        ${nTerms}`);
  console.log(`  ambiguous refused   ${ambiguous}`);
  console.log(`  near-name quarantine ${quarantined.size}  ${[...quarantined].slice(0, 8).map(x => '"' + x + '"').join(' ')}`);
}
