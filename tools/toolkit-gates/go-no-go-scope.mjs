/**
 * NO WRITTEN WORD CLEARS A HOLD THAT RISKS A PERSON — a gate for the go/no-go notes.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * Six kits ship a morning-of go/no-go note on shared/note.js (paving, landscape,
 * painting, doors, siding, steel), and five of them close on the same two
 * buttons: fix it and tell me when, or direct me IN WRITING to do it as it sits.
 * On a finish trade that second button is a warranty choice the receiver may
 * lawfully make. Steel's note (C3738) was built as their twin and inherited it
 * whole — "reply SET and we fly it as it sits" — under a stop list where ten of
 * thirteen holds risk a person: a hot line in the swing, anchor bolts nobody
 * approved, the deck below not poured, hot work with no watch, the wind. The
 * stops said "I don't fly under a hot line" and the close under them offered to.
 * Siding's CLOSE reached an old house nobody had tested and ground a jack could
 * not stand on. No gate read a close against the stops above it; C3749 found it
 * by reading the storefront, which already said the page did something else.
 *
 * WHAT IT ASSERTS, plain node, off the shipped files:
 *   S1  steel's close is FIX / NEW DAY and "There's no reply that flies it as it
 *       sits"; no reply keyword SET or CLEAR (a one-word "CLEAR" at 6 a.m. reads
 *       as the all-clear); no fly-as-it-sits offer anywhere on the page, the
 *       registry or the vocabulary except in the sentences that refuse it.
 *   S2  no steel stop asks for a written direction, and the Getting In power-line
 *       ask never offers a line cover as the way past a hot line.
 *   S3  steel's Directed-to-Set write-up names every hold the note says only its
 *       owner can clear — all eight — in both its note and its halt.
 *   S4  siding's CLOSE is fenced by DATA: the six holds no written word clears
 *       carry `fence`, and the page offers CLOSE and prints the fence off them.
 *   S5  every go/no-go note opens with its own trade's heading, never a donor's
 *       (siding's opened NOT READY TO PAVE for fourteen days).
 *   S2b no line lets a name, a say-so or the receiver's own day clear a person
 *       hold (C3751: a pick over an occupied floor, the deck below, a hot line,
 *       suspect old flooring).
 *   S6  flooring's Give Me The Go — a SEVENTH note the list above never named —
 *       run in the sandbox: its written go never reaches "the old stuff" (C3751).
 *
 * WHAT IT DOES NOT YET DO (C3751, said so the scar does not overclaim it): it
 * classifies holds on steel, siding and flooring only. Paving, landscape,
 * painting and doors keep a proceed reply that is offered with nothing ticked,
 * over a hold typed in words the page cannot classify; generalising S4b to every
 * note found by its mount call is the next rung, not a claim of this one.
 *
 *   node tools/toolkit-gates/go-no-go-scope.mjs [--root=HELIOS-BRIDGE/dist] [--prove]
 */
import { readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { join, resolve } from 'path';
import vm from 'vm';

const args = process.argv.slice(2);
const PROVE = args.includes('--prove');
const rootArg = (args.find(a => a.startsWith('--root=')) || '').slice(7);
const ROOT = rootArg ? resolve(rootArg) : fileURLToPath(new URL('../../', import.meta.url));

const fails = [], notes = [];
let checks = 0;
const ok = (c, m) => { checks++; (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };
const read = rel => readFileSync(join(ROOT, rel), 'utf8');
const noComments = s => s.replace(/<!--[\s\S]*?-->/g, ' ').replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:"'])\/\/.*$/gm, '$1');

/* The sentences that REFUSE the fly-as-it-sits reply are the only place the
 * words may stand. Lift them out, then nothing that offers it may remain. */
const REFUSALS = /no reply that flies it as it sits|no answer that flies it as it sits|never permission to fly it as it sits|permission to fly the iron as it sits|not permission to fly it as it sits/gi;
/* Not only the old scar's wording (C3750): an audit synced steel's close to
 * doors' own "reply PROCEED and we hang them as they stand" and S1 stayed green. */
const OFFER = /as it sits|as they sit|as (it|they) stands?|\bas[- ]is\b|fly it anyway|fly it as|set it anyway|(fly|set|hang) (it|them) anyway|reply (SET|CLEAR|PROCEED|GO|OK|YES)\b|sign[- ]?off to (set|fly)/i;
const WRITTEN_GO = /\bin writing\b|\bdirect me\b|\bsign[- ]?off\b|\byour (go|ok|say-so)\b|\bgive me the (go|ok)\b|\bok to (set|fly)\b|\bapprove (the )?(set|pick)\b/i;
const HOLDS = ['anchor bolt', 'an embed a connection sits on', 'the deck below', 'a hot line', "the crane's own setup",
  "hot work without the building's permit and a watch", 'the wind', "a detail that doesn't match"];
const FENCED = ["Sheathing's not on, not fastened off, or there are gaps", 'No nailers or blocking where the trim lands',
  "Took the old wall off and there's rot behind it", "The house is old and nobody's said who's testing before we cut",
  "I can't get a jack or a lift to the wall", 'Weather — my call, my words'];
const HEADS = { 'paving/not-ready-to-pave.html': /^NOT READY TO PAVE$/, 'landscape/not-ready-to-plant.html': /^NOT READY TO PLANT$/,
  'painting/not-ready.html': /^NOT READY FOR PAINT$/, 'doors/not-ready-to-hang.html': /^NOT READY TO HANG$/,
  "siding/not-ready-to-side.html": /^WALL'S NOT READY$/, 'steel/not-ready-to-set.html': /^NOT READY TO SET$/,
  'flooring/give-me-the-go.html': /^BEFORE THIS FLOOR GOES DOWN$/ };
/* A NAME, A SAY-SO OR THE RECEIVER'S OWN DAY IS NOT A CLEAR (C3751). The six-note
 * list above missed a seventh note and three lines that clear a person hold on a
 * name: steel's pick over an occupied floor ("until you name who owns that"), its
 * deck below ("the day I can load it" — the engineer's release, not the super's),
 * its power line ("or tell me who owns the de-energize"), and flooring's suspect
 * old goods ("nobody on my crew touches it until you say"). */
const NAMED_CLEAR = /until you name|name who clears[^.]*before we pick|the day I can load it|or tell me who owns the de-energize|touches it until you say/i;

function load(rel, key) {
  const sb = { window: {} };
  vm.createContext(sb);
  vm.runInContext(read(rel), sb);
  return key ? key.split('.').reduce((o, k) => (o || {})[k], sb.window) : sb.window;
}

/* ── the checkers, plain functions so --prove can feed them planted defects ── */
function steelCloseFaults(page) {
  const f = [];
  const src = noComments(page);
  if (!/Reply FIX with who's fixing each one and when/.test(src)) f.push('the first button is not FIX');
  if (!/reply NEW DAY with the day/.test(src)) f.push('the second button is not NEW DAY');
  if (!/There's no reply that flies it as it sits/.test(src)) f.push('the close never says no reply flies it as it sits');
  const left = src.replace(REFUSALS, ' ');
  const m = left.match(OFFER);
  if (m) f.push(`an offer to proceed survives: "…${left.slice(Math.max(0, m.index - 50), m.index + 30).replace(/\s+/g, ' ')}…"`);
  return f;
}
function steelStopFaults(stops) {
  return (stops || []).filter(s => WRITTEN_GO.test(s.sub || '')).map(s => `the stop "${s.name}" asks for a written direction`);
}
function directedFaults(doc) {
  const f = [];
  ['note', 'halt'].forEach(k => HOLDS.forEach(h => { if ((doc[k] || '').indexOf(h) === -1) f.push(`the directed-to-set ${k} does not name "${h}"`); }));
  return f;
}
function fenceFaults(stops, page) {
  const f = [];
  FENCED.forEach(nm => {
    const s = (stops || []).find(x => x.name === nm);
    if (!s) f.push(`no stop named "${nm}" — the fence list and the data disagree`);
    else if (!s.fence) f.push(`"${nm}" is not fenced`);
  });
  const src = noComments(page);
  if (!/x\.fence/.test(src) || !/There's no CLOSE on these/.test(src) || !/CLOSE never reaches/.test(src)) f.push('the page does not offer CLOSE and print the fence off the data');
  return f;
}
/* S4b — SIDING'S CLOSE, RUN RATHER THAN READ (C3750). S4 only looked for the
 * fence's words on the page; with the fence condition switched off it stayed
 * green while a note of fenced holds offered to hang over them, and the drive
 * that would have caught it is run by the lane, not by the deploy. This runs the
 * page's own script in a sandbox with Note.mount captured, then asks each closing
 * function what the note would say for a set of ticks and a typed hold. */
function sidingClosings(itemsSrc, pageSrc) {
  const sb = { window: {} };
  vm.createContext(sb);
  vm.runInContext(itemsSrc, sb);
  let cfg = null;
  sb.Note = { mount: c => { cfg = c; return { refresh() {}, get() {} }; } };
  const js = (pageSrc.match(/<script>([\s\S]*?)<\/script>/g) || []).map(m => m.replace(/^<script>|<\/script>$/g, '')).join('\n');
  vm.runInContext(js, sb);
  return { closing: (cfg && cfg.closing) || [], stops: ((sb.window.TOOLKIT_ITEMS || {}).notready || {}).stops || [] };
}
function sidingCloseBehaviour(itemsSrc, pageSrc) {
  const f = [];
  let c;
  try { c = sidingClosings(itemsSrc, pageSrc); } catch (e) { return ['the siding page script would not run in the sandbox: ' + String(e).split('\n')[0]]; }
  const say = (ticked, typed) => c.closing.map(x => typeof x === 'function' ? x(k => (k === 'stops' ? ticked : k === 'extra' ? (typed || '') : '')) : x).join('\n');
  const offers = t => /reply CLOSE/.test(t);
  const fenced = c.stops.filter(x => x.fence).map(x => x.name);
  const open = c.stops.filter(x => !x.fence).map(x => x.name);
  if (!fenced.length || !open.length) return ['the siding stops carry no fenced or no closable hold to test'];
  if (offers(say([], 'a live drop on the back wall'))) f.push('with nothing ticked, CLOSE is offered over a hold he typed');
  fenced.forEach(nm => { if (offers(say([nm], ''))) f.push(`CLOSE is offered over "${nm}" alone`); });
  if (offers(say(fenced, ''))) f.push('CLOSE is offered over every fenced hold at once');
  if (!offers(say([open[0]], ''))) f.push(`CLOSE is not offered on "${open[0]}", a hold whose call is theirs`);
  const mixed = say([open[0], fenced[0]], '');
  if (!/CLOSE never reaches/.test(mixed)) f.push('a mixed note offers CLOSE without saying what it never reaches');
  if (!/CLOSE never reaches[^\n]*the one I've written in/.test(say([open[0]], 'a live drop'))) f.push('a CLOSE note is silent about the hold he typed');
  return f;
}
/* S6 — FLOORING'S GO NEVER REACHES THE OLD STUFF (C3751). Give Me The Go is a
 * seventh go/no-go note the list above never named, and its one closing offered
 * "give me the go in writing — laid over … as it is today" with "It might be the
 * old stuff" ticked, against the page's own warn (stop until the owner's survey).
 * Run, not read: the page's script in a sandbox, each closing asked what the
 * letter would say. */
function flooringGoBehaviour(pageSrc) {
  const f = [];
  let cfg = null;
  const sb = { window: {} };
  vm.createContext(sb);
  sb.Note = { mount: c => { cfg = c; return { refresh() {}, get() {} }; } };
  const js = (pageSrc.match(/<script>([\s\S]*?)<\/script>/g) || []).map(m => m.replace(/^<script>|<\/script>$/g, '')).join('\n');
  try { vm.runInContext(js, sb); } catch (e) { return ['the flooring page script would not run in the sandbox: ' + String(e).split('\n')[0]]; }
  if (!cfg) return ['the flooring page never mounted a note'];
  const field = (cfg.sections || []).flatMap(x => x.fields || []).find(x => x.id === 'stuck');
  const opts = (field && field.options) || [];
  const fenced = opts.filter(o => o.fence).map(o => o.name);
  const open = opts.filter(o => !o.fence).map(o => o.name);
  if (!fenced.some(n => /old stuff/i.test(n))) f.push('"It might be the old stuff" carries no fence');
  const say = ticked => (cfg.closing || []).map(x => typeof x === 'function' ? x(k => (k === 'stuck' ? ticked : '')) : x).join('\n');
  const offers = t => /give me the go in writing/i.test(t);
  fenced.forEach(nm => { if (offers(say([nm]))) f.push(`the go is offered over "${nm}" alone`); });
  if (fenced.length && offers(say(fenced))) f.push('the go is offered over every fenced hold at once');
  if (open.length && !offers(say([open[0]]))) f.push(`the go is not offered on "${open[0]}", a hold whose call is theirs`);
  if (fenced.length && open.length && !/go never reaches/.test(say([open[0], fenced[0]]))) f.push('a mixed letter keeps the go without saying what it never reaches');
  return f;
}
const headOf = page => (page.match(/docName:\s*"([^"]*)"/) || [, ''])[1].replace(/\\'/g, "'");

if (PROVE) {
  const good = read('steel/not-ready-to-set.html');
  ok(steelCloseFaults(good.replace("Or reply NEW DAY", "Or reply SET and we fly it as it sits — in writing. Or reply NEW DAY")).length > 0, 'PROVE  a planted SET reply goes red');
  ok(steelCloseFaults(good.replace('Reply FIX with', 'Reply CLEAR with')).length > 0, 'PROVE  a planted CLEAR keyword goes red');
  ok(steelStopFaults([{ name: 'x', sub: 'or direct me in writing to field-fit it' }]).length > 0, 'PROVE  a stop asking for a written direction goes red');
  const doc = { note: HOLDS.slice(0, 5).join(', '), halt: HOLDS.join(', ') };
  ok(directedFaults(doc).length > 0, 'PROVE  a directed-to-set note missing three holds goes red');
  ok(fenceFaults([{ name: FENCED[0] }], 'x.fence There\'s no CLOSE on these CLOSE never reaches').length > 0, 'PROVE  an unfenced hold goes red');
  ok(!HEADS['siding/not-ready-to-side.html'].test('NOT READY TO PAVE'), 'PROVE  a donor heading on siding goes red');
  const sItems = read('siding/items.js'), sPage = read('siding/not-ready-to-side.html');
  const unfenced = sPage.replace('if (!s.some(function (nm) { return !FENCE[nm]; })) return "";', '');
  ok(unfenced !== sPage && sidingCloseBehaviour(sItems, unfenced).length > 0, 'PROVE  the fence condition switched off goes red (S4b)');
  const fl = read('flooring/give-me-the-go.html');
  const flUnfenced = fl.replace(/,\s*fence: "the old stuff"/, '');
  ok(flUnfenced !== fl && flooringGoBehaviour(flUnfenced).length > 0, "PROVE  flooring's go over the old stuff, unfenced, goes red (S6)");
  ok(NAMED_CLEAR.test("nothing swings over somebody's head until you name who owns that") && NAMED_CLEAR.test('nobody on my crew touches it until you say.'), 'PROVE  a name-or-say-so clear goes red (S2b)');
  ok(steelCloseFaults(good.replace("Or reply NEW DAY", "Or reply PROCEED and we set them as they stand. Or reply NEW DAY")).length > 0, 'PROVE  a reworded proceed offer goes red');
  ok(steelStopFaults([{ name: 'x', sub: 'give me the ok to set it on the bolts we have' }]).length > 0, 'PROVE  a reworded written-go ask goes red');
} else {
  const steelPage = read('steel/not-ready-to-set.html');
  const sf = steelCloseFaults(steelPage);
  ok(sf.length === 0, 'S1  steel closes on FIX / NEW DAY and refuses fly-as-it-sits' + (sf.length ? ': ' + sf.join('; ') : ''));
  const reg = (load('steel/tools.js').TOOLKIT_TOOLS || []).find(t => t.href === 'not-ready-to-set.html') || {};
  const regLeft = String(reg.desc || '').replace(REFUSALS, ' ');
  ok(!!reg.desc && !OFFER.test(regLeft), 'S1  the steel registry line offers no fly-as-it-sits');
  const steelItems = load('steel/items.js');
  const stF = steelStopFaults((steelItems.TOOLKIT_ITEMS.notready || {}).stops);
  ok(stF.length === 0, 'S2  no steel stop asks for a written direction' + (stF.length ? ': ' + stF.join('; ') : ''));
  const itemsSrc = read('steel/items.js');
  ok(!/power-down or the line cover/.test(itemsSrc) && /a covered line is still a hot line/.test(itemsSrc),
    'S2  the steel Getting In ask never offers a line cover as the way past a hot line');
  const named = ['steel/items.js', 'flooring/items.js', 'flooring/give-me-the-go.html'].filter(rel => NAMED_CLEAR.test(noComments(read(rel))));
  ok(named.length === 0, "S2b  no line lets a name, a say-so or the receiver's own day clear a person hold" + (named.length ? ': ' + named.join(', ') : ''));
  const docs = load('steel/docs.js', 'TRADE_DOCS') || {};
  const dts = (docs.docs || []).find(d => d.id === 'directed-to-set');
  const df = dts ? directedFaults(dts) : ['no directed-to-set document on the steel shelf'];
  ok(df.length === 0, 'S3  the directed-to-set write-up names all eight holds only their owner clears' + (df.length ? ': ' + df.join('; ') : ''));
  const sidingItems = load('siding/items.js');
  const ff = fenceFaults((sidingItems.TOOLKIT_ITEMS.notready || {}).stops, read('siding/not-ready-to-side.html'));
  ok(ff.length === 0, 'S4  siding\'s CLOSE is fenced off the data on all six holds no written word clears' + (ff.length ? ': ' + ff.join('; ') : ''));
  const fb = sidingCloseBehaviour(read('siding/items.js'), read('siding/not-ready-to-side.html'));
  ok(fb.length === 0, 'S4b siding\'s CLOSE, run: never over nothing ticked, a fenced hold or a typed one; offered on a closable hold' + (fb.length ? ': ' + fb.join('; ') : ''));
  const flb = flooringGoBehaviour(read('flooring/give-me-the-go.html'));
  ok(flb.length === 0, "S6  flooring's go, run: never over the old stuff alone, and named where a mixed letter keeps it" + (flb.length ? ': ' + flb.join('; ') : ''));
  Object.keys(HEADS).forEach(rel => {
    if (!existsSync(join(ROOT, rel))) { ok(false, `S5  ${rel} is missing`); return; }
    const h = headOf(read(rel));
    ok(HEADS[rel].test(h), `S5  ${rel} opens with its own heading ("${h}")`);
  });
}

console.log(notes.join('\n'));
console.log('\n' + '='.repeat(60));
if (fails.length) { console.log(fails.join('\n')); console.log(`\n${fails.length} FAILING of ${checks}`); process.exit(1); }
console.log(`ALL ${checks} CHECKS PASS — ${PROVE ? 'prove (planted defects all red)' : 'go/no-go scope'} — ${ROOT}`);
