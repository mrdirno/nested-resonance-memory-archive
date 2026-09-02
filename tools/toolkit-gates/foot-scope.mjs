/**
 * FOOT SCOPE — a block under the list may not name a row the list does not show.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `shared/rowlog.js` ships NAMED DOCUMENT FILTERS so a chase list can send a man
 * only what is still open, and only what is HIS. The engine's own blocks obey
 * that scope — the flagged block draws from `scopedRows()`, and its comment says
 * why: "a man must never read somebody else's problem inside a message addressed
 * to him". A page's OWN `docFoot` is the one place that discipline can be lost,
 * because it is hand-written per page and the engine hands it the filter keys in
 * `ctx` that it is free to ignore.
 *
 * IT WAS LOST, AND THE SWEEP THAT FOUND IT WAS LOOKING FOR SOMETHING ELSE.
 * `framing/whats-in-the-wall.html` scoped to "not covered yet" printed one row —
 * and then, underneath, "STILL NEED FROM YOU — I can't put these in until
 * somebody gives me a number" naming a piece that was COVERED. It was already in
 * the wall, it was not in the body, and the AV contractor reading it had no line
 * above to argue with. A flag does not clear itself when a row is covered, so
 * that piece had been asking for its size in every copy since it went in.
 *
 * THE RULE, and it is deliberately the cheap static one so it fires at authoring
 * time rather than after a drive nobody wrote: a page that declares `filters:`
 * and whose `docFoot` reaches for the WHOLE row set must either narrow it by the
 * filters the engine handed it, or SAY SO IN THE PRINTED TEXT.
 * `masonry/wheres-the-wall.html` passes on the second branch and has since it
 * shipped — it prints "(every wall on my log, not just the ones above)" — which
 * is the honest version of the same decision and the reason the rule is
 * "scope it or say so" rather than "always scope it".
 *
 *   node tools/toolkit-gates/foot-scope.mjs
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { join } from 'path';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const fails = [], notes = [];
let checks = 0;
const ok = (c, m) => { checks++; (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };

/* The whole-list reaches. `docRows`/`scopedRows` are the engine's own and are
   already narrowed; these are the ones that hand back everything. */
const WHOLE_LIST = /\b(rowsNow\(\)|rl\.rows\(\))/;
/* Narrowing it, however the page spells that. */
const NARROWED = /\bc\s*(&&\s*c)?\.filters|\bscopedNow\s*\(|\bfilters\s*\|\|\s*\[\]|\bc\.filters\b/;
/* Or telling the reader, in the text the reader gets. */
const DISCLOSED = /not just the ones above|every \w+ on my log|whole list|all of them, not/i;

function footOf(src) {
  const i = src.indexOf('docFoot:');
  if (i < 0) return null;
  // to the end of the property — the next top-level key at the same indent
  const rest = src.slice(i);
  const j = rest.search(/\n    \},\n/);
  return j < 0 ? rest.slice(0, 4000) : rest.slice(0, j);
}

const trades = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
  .map(d => d.name).sort();

let looked = 0;
for (const t of trades) {
  for (const f of readdirSync(join(ROOT, t)).filter(x => x.endsWith('.html')).sort()) {
    const p = join(ROOT, t, f);
    const src = readFileSync(p, 'utf8');
    if (!/shared\/rowlog\.js/.test(src)) continue;
    if (!/\bfilters:\s*\[/.test(src)) continue;      // no document filters, no scope to lose
    const foot = footOf(src);
    if (!foot || !WHOLE_LIST.test(foot)) continue;   // the foot names no rows
    looked++;
    ok(NARROWED.test(foot) || DISCLOSED.test(foot),
      `${t}/${f}: docFoot narrows to what the copy contains, or says out loud that it does not`);
  }
}

ok(looked > 0, `the rule found pages to apply to (${looked} filtered row logs with a row-reading docFoot)`);

notes.forEach(n => console.log(n));
console.log(`\n${checks} checks · ${fails.length} failing`);
if (fails.length) { console.log(''); fails.forEach(f => console.log(f)); process.exit(1); }
console.log('FOOT SCOPE: green.');
