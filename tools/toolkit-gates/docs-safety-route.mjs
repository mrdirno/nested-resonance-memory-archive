/**
 * THE SAFETY ROUTE — an injury typed into any shelf's document search opens the
 * incident report, and a word that is not an injury does not.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS, measured before a line of it was written (C3747, 2026-09-23).
 *
 * Every trade's write-up page answers "tripped and fell" from the same library, and
 * for a year the answer depended on which single words happened to be lying around.
 * shared/find.js indexes an alias WORD BY WORD and shared/docsindex.js lends a
 * shared document's words to all nineteen shelves, so the incident report could only
 * be reached through words — and every word it answered to, it took from somebody.
 * C3746 gave it "fell off" and "fell from" as aliases; the price, measured on the
 * frozen C3747 instrument, was 199 searches on up to 19 shelves that opened the
 * INCIDENT REPORT for "off", "power off", "shut off", "time off", "dropped off",
 * "change from the architect", "report from the inspector", "delay from weather".
 * And "tripped and fell", "slipped and fell", "passed out", "cut my hand" still
 * missed it on 66 of 95 probes, because no alias could carry them without lending
 * "tripped", "cut", "slipped" and "lift" to the electrician's "tripped breaker", the
 * concrete man's "saw cut" and "lift station".
 *
 * C3747 moved them to `phrases` (shared/docspec.js, phrased(): a whole run of his
 * words, never indexed, never pooled). Every gate on the rack stayed green through
 * BOTH states — docs-shelf probes the words an author wrote, typed whole, and the
 * damage was always on words nobody wrote, on shelves nobody drafted for. So the
 * route itself is asserted here, in plain node, against the SHIPPED engine and the
 * SHIPPED phrase rule (never a copy of either), which is what lets the deploy run it.
 *
 * FOUR CLASSES, every one checked on every shelf:
 *   S  SAFETY FLOOR   each phrase below leads the incident report. The list is the
 *                     set that leads it on 19 of 19 shelves the day this shipped —
 *                     a floor, not an aspiration. A phrase that misses anywhere is
 *                     not added here; it is the next rung.
 *   N  NOT AN INJURY  each phrase below does NOT lead the incident report. The
 *                     frozen bare words (tripped, saw cut, cut and patch, lift
 *                     station, schedule slipped) and the C3746 price list. Three
 *                     probes are left out on purpose, each leading the incident
 *                     report on ONE shelf through that trade's own alias rather than
 *                     a lent word: "tripped breaker", "dropped off", "damage from the
 *                     painters".
 *   W  LENDS NO WORD  the promise `phrases` exists for. Every WORD of every phrase on
 *                     the shelf, typed alone (open and closed), comes back from
 *                     phrased() as the very object the engine returned — the rule did
 *                     nothing — and no phrase is a single word (that is an alias by
 *                     another name, and it would lend exactly what `aka` lends).
 *   R  WIRED          the page applies the rule: shared/docspec.js's renderLibrary()
 *                     still hands the engine's result to phrased() before it draws.
 *
 * WHAT THIS DOES NOT CATCH, said so nobody reads green as more than it is: the
 * phrases stay dark that were never written ("fell of ladder", "knocked off the
 * ladder", "fel off"), and "fell behind schedule" still opens the incident report on
 * 17 shelves through the one-word alias "fell" — at HEAD too, and the next rung.
 *
 * NEGATIVE CONTROL — a gate nobody has watched fail is a decoration.
 *     node tools/toolkit-gates/docs-safety-route.mjs --prove
 * rebuilds every shelf three times out of its own data and REQUIRES each detector
 * to go red on every shelf: S with `phrases` stripped from every document; N with
 * "fell off" and "fell from" put back as incident-report aliases (the C3746 state);
 * W with a one-word phrase ("fell") added. Exits non-zero if a detector stays green.
 *
 *   node tools/toolkit-gates/docs-safety-route.mjs [--root=DIR] [--prove]
 *   node tools/toolkit-gates/docs-safety-route.mjs --root=HELIOS-BRIDGE/dist   # the deploy
 */
import { readdirSync, existsSync, readFileSync } from 'fs';
import { fileURLToPath } from 'url';

const args = process.argv.slice(2);
const PROVE = args.includes('--prove');
const rootArg = (args.find(a => a.startsWith('--root=')) || '').slice(7);
const ROOT = rootArg ? rootArg.replace(/\/?$/, '/') : fileURLToPath(new URL('../../', import.meta.url));
const INCIDENT = 'incident-report';

const SAFETY = [
  'tripped and fell', 'slipped and fell', 'passed out', 'he passed out', 'cut my hand',
  'fell off', 'fell from', 'fall off', 'fall from', 'fallen off', 'falls from height', 'fell of the ladder',
  'fell off the lift', 'fell off the ladder', 'fell off a ladder', 'fell off the roof', 'fell off the scaffold',
  'fell off the scissor lift', 'fell from the lift', 'fell from the ladder', 'slipped off the ladder',
  'trip and fall', 'slip and fall', 'tool fell from the lift', 'dropped a tool from the lift',
  'display fell off the wall', 'the new guy tripped and fell off the ladder',
  'got hurt', 'got hurt on site', 'near miss', 'struck by', 'caught between', 'electrocuted',
];
const NOT_INJURY = [
  'tripped', 'breaker tripped', 'gfci tripped', 'trip charge', 'return trip',
  'cut', 'saw cut', 'cut and patch', 'cut sheet', 'cut list',
  'slipped', 'schedule slipped', 'slip sheet',
  'lift', 'lift station', 'scissor lift', 'lift gate',
  'off', 'from', 'power off', 'shut off', 'time off',
  'change from the architect', 'rfi from the architect', 'report from the inspector',
  'delay from weather', 'leak from above', 'passed inspection', 'out of scope', 'hand off',
];

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(`${ROOT}${d.name}/docs.js`) && existsSync(`${ROOT}${d.name}/write-up.html`))
  .map(d => d.name).sort();
if (!TRADES.length) { console.error('FAIL: no trade docs.js found under ' + ROOT); process.exit(1); }

const SRC = {
  find: readFileSync(ROOT + 'shared/find.js', 'utf8'),
  pool: existsSync(ROOT + 'shared/docsindex.js') ? readFileSync(ROOT + 'shared/docsindex.js', 'utf8') : '',
  spec: readFileSync(ROOT + 'shared/docspec.js', 'utf8'),
};

/* One shelf, the way its page loads it: find.js, the pool, the trade, then the
   engine with no document (the mount is guarded, the exports are not). `mutate`
   is the negative control's hook; it runs before the first index is built. */
function shelf(trade, mutate) {
  const win = {};
  new Function('window', SRC.find)(win);
  if (SRC.pool) new Function('window', SRC.pool)(win);
  for (const f of ['trade.js', 'docs.js']) new Function('window', readFileSync(`${ROOT}${trade}/${f}`, 'utf8'))(win);
  new Function('window', 'document', SRC.spec)(win, undefined);
  if (mutate) mutate(win);
  return win;
}

function run(trade, mutate) {
  const win = shelf(trade, mutate);
  const out = { S: [], N: [], W: [], R: [], checks: 0 };
  const DS = win.DocSpec, F = win.Find;
  if (!DS || typeof DS.phrased !== 'function' || typeof DS.findIx !== 'function') {
    out.R.push('shared/docspec.js exports no phrased()/findIx() — the phrase rule cannot be asked');
    return out;
  }
  const ix = DS.findIx();
  const answer = q => DS.phrased(ix, F.search(ix, q), q);
  const lead = q => { const r = answer(q); return r.hits[0] ? r.hits[0].id : '(nothing)'; };
  const carries = DS.library().some(d => d.id === INCIDENT);

  if (carries) {
    for (const q of SAFETY) { out.checks++; const id = lead(q); if (id !== INCIDENT) out.S.push(`"${q}" led ${id}`); }
    for (const q of NOT_INJURY) { out.checks++; if (lead(q) === INCIDENT) out.N.push(`"${q}" led the incident report`); }
  }
  for (const d of DS.library()) {
    for (const p of d.phrases || []) {
      const toks = F.toks(p);
      out.checks++;
      if (toks.length < 2) out.W.push(`${d.id}: phrase "${p}" is one word — an alias by another name`);
      for (const w of toks) {
        for (const q of [w, w + ' ']) {
          out.checks++;
          const res = F.search(ix, q);
          if (DS.phrased(ix, res, q) !== res) out.W.push(`${d.id}: "${q.trim()}" alone (from "${p}") was moved by the phrase rule`);
        }
      }
    }
  }
  return out;
}

/* R — the page draws what phrased() returns, not what the engine returned. */
const wired = /res\s*=\s*phrased\(\s*findIx\(\)\s*,\s*res\s*,\s*S\.q\s*\)/.test(SRC.spec);

if (PROVE) {
  const controls = {
    S: win => {
      (win.DocSpec.shared || []).forEach(d => { delete d.phrases; });
      const L = win.TRADE_DOCS || {};
      (L.docs || []).forEach(d => { delete d.phrases; });
      Object.values(L.overrides || {}).forEach(o => { delete o.phrases; });
    },
    N: win => {
      const inc = (win.DocSpec.shared || []).find(d => d.id === INCIDENT);
      const L = win.TRADE_DOCS; if (!inc || !L) return;
      const ov = (L.overrides = L.overrides || {});
      const cur = ov[INCIDENT] || {};
      ov[INCIDENT] = Object.assign({}, cur, { aka: (cur.aka || inc.aka || []).concat(['fell off', 'fell from']) });
    },
    W: win => {
      const inc = (win.DocSpec.shared || []).find(d => d.id === INCIDENT);
      if (inc) inc.phrases = (inc.phrases || []).concat(['fell']);
      const L = win.TRADE_DOCS || {};
      const o = (L.overrides || {})[INCIDENT];
      if (o && o.phrases) o.phrases = o.phrases.concat(['fell']);
    },
  };
  let ok = true;
  for (const [k, mutate] of Object.entries(controls)) {
    let red = 0;
    for (const t of TRADES) if (run(t, mutate)[k].length) red++;
    console.log(`  ${k}: went red on ${red}/${TRADES.length} shelves`);
    if (red !== TRADES.length) ok = false;
  }
  console.log(`\nNEGATIVE CONTROL — ${ok ? 'every detector works.' : 'A DETECTOR IS BLIND.'}`);
  process.exit(ok ? 0 : 1);
}

let checks = 1, failing = 0;
if (!wired) { failing++; console.log('  R  shared/docspec.js renderLibrary() no longer passes the engine result through phrased() — the page and this gate disagree   ** FAIL **'); }
for (const t of TRADES) {
  const r = run(t);
  checks += r.checks;
  const bad = [...r.R.map(x => 'R ' + x), ...r.S.map(x => 'S ' + x), ...r.N.map(x => 'N ' + x), ...r.W.map(x => 'W ' + x)];
  if (bad.length) failing++;
  console.log(`  ${t.padEnd(12)} ${String(r.checks).padStart(4)} check(s) · S ${r.S.length} · N ${r.N.length} · W ${r.W.length}${bad.length ? '   ** FAIL **' : ''}`);
  for (const b of bad.slice(0, 8)) console.log('      ' + b);
}
console.log(`\nSAFETY ROUTE GATE — ${TRADES.length} trade(s), ${checks} checks, ${failing} failing`);
process.exit(failing ? 1 : 0);
