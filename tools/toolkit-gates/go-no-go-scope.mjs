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
 *   S7  EVERY note with a proceed reply (siding CLOSE, paving PAVE, landscape,
 *       painting and doors PROCEED), run in the sandbox (C3752): never on an
 *       empty note, never over a hold he typed with nothing ticked, never over a
 *       fenced hold alone or all of them; still offered on a closable hold; a
 *       mixed or typed note says what it never reaches; a fenced stop asks for no
 *       written go; landscape fences unlocated lines and painting untested paint.
 *   S8  the write-ups that record a direction or a condition — plumbing's line
 *       strike and ready-for-cover, concrete's conditions notice and directed
 *       work, flooring's, painting's and doors' directed write-ups — name the hold
 *       no direction clears in note AND halt.
 *   S9  hvac's T&M tag, run in EN and ES: HOLD over a locked-out or off-and-
 *       tagged unit keeps it off until it's repaired, never "the way I found it".
 *   S10 the write-up engine's EXTRA INSTRUCTIONS, emitted last, carry the
 *       exception: nothing he types there clears a hold the document names.
 *
 * WHAT IT DOES NOT DO (said so a scar does not overclaim it): it reads each note's
 * DATA for which holds are fenced; whether a stop left closable really risks no
 * one is a judgement the audit makes, not this gate. On HEAD before C3752, S7 was
 * red on four of five notes (18 faults: PAVE and PROCEED printed on an empty note
 * and under "an open trench nobody shored, a crew still in it").
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
/* S7 — EVERY NOTE'S PROCEED REPLY, RUN (C3752). S4b ran siding's close and no
 * other: paving, landscape, painting and doors still printed "Or reply PAVE /
 * PROCEED and we … as it sits — in writing" on an empty note and under a hold
 * typed in words the page cannot classify — "an open utility trench, nobody
 * shored it, a crew is still in it" got PAVE. Each note's own script runs in the
 * sandbox with Note.mount captured; its closings are asked what the note says. */
const NOTES = [
  { page: 'siding/not-ready-to-side.html', items: 'siding/items.js', key: 'notready', word: 'CLOSE' },
  { page: 'paving/not-ready-to-pave.html', items: 'paving/items.js', key: 'notready', word: 'PAVE' },
  { page: 'landscape/not-ready-to-plant.html', items: 'landscape/items.js', key: 'notready', word: 'PROCEED', must: [/locate/i, 'stop for lines nobody has located'] },
  { page: 'painting/not-ready.html', items: 'painting/items.js', key: 'notready', word: 'PROCEED', must: [/old paint|tested|pre-?1978|lead/i, 'stop for old paint nobody has tested'] },
  { page: 'doors/not-ready-to-hang.html', items: 'doors/items.js', key: 'nothang', word: 'PROCEED' },
];
function noteBehaviour(n, itemsSrc, pageSrc) {
  const f = [];
  const sb = { window: {} };
  vm.createContext(sb);
  let cfg = null;
  try {
    vm.runInContext(itemsSrc, sb);
    sb.Note = { mount: c => { cfg = c; return { refresh() {}, get() {} }; } };
    const js = (pageSrc.match(/<script>([\s\S]*?)<\/script>/g) || []).map(m => m.replace(/^<script>|<\/script>$/g, '')).join('\n');
    vm.runInContext(js, sb);
  } catch (e) { return [`${n.page} would not run in the sandbox: ` + String(e).split('\n')[0]]; }
  if (!cfg) return [`${n.page} never mounted a note`];
  const stops = ((sb.window.TOOLKIT_ITEMS || {})[n.key] || {}).stops || [];
  const say = (ticked, typed) => (cfg.closing || []).map(x => typeof x === 'function' ? x(k => (k === 'stops' ? ticked : k === 'extra' ? (typed || '') : '')) : x).join('\n');
  const offers = t => new RegExp('reply ' + n.word + '\\b').test(t);
  const fenced = stops.filter(x => x.fence).map(x => x.name);
  const open = stops.filter(x => !x.fence).map(x => x.name);
  if (!fenced.length) f.push(`no ${n.page.split('/')[0]} stop carries a fence`);
  if (!open.length) f.push(`every ${n.page.split('/')[0]} stop is fenced — ${n.word} can never be offered`);
  if (n.must && !stops.some(x => x.fence && (n.must[0].test(x.name) || n.must[0].test(x.fence)))) f.push(`no fenced ${n.must[1]}`);
  stops.filter(x => x.fence && WRITTEN_GO.test((x.sub || '') + ' ' + (x.ask || ''))).forEach(x => f.push(`the fenced stop "${x.name}" still asks for a written direction`));
  if (offers(say([], ''))) f.push(`${n.word} is offered on an empty note`);
  if (offers(say([], 'an open trench nobody shored, a crew still in it'))) f.push(`with nothing ticked, ${n.word} is offered over a hold he typed`);
  fenced.forEach(nm => { if (offers(say([nm], ''))) f.push(`${n.word} is offered over "${nm}" alone`); });
  if (fenced.length && offers(say(fenced, ''))) f.push(`${n.word} is offered over every fenced hold at once`);
  if (open.length && !offers(say([open[0]], ''))) f.push(`${n.word} is not offered on "${open[0]}", a hold whose call is theirs`);
  if (open.length && fenced.length && !new RegExp(n.word + ' never reaches').test(say([open[0], fenced[0]], ''))) f.push(`a mixed note offers ${n.word} without saying what it never reaches`);
  if (open.length && !new RegExp(n.word + " never reaches[^\\n]*the one I've written in").test(say([open[0]], 'a live drop'))) f.push(`a ${n.word} note is silent about the hold he typed`);
  return f;
}
/* S8 — A WRITE-UP THAT RECORDS A DIRECTION NAMES THE HOLD NO DIRECTION CLEARS
 * (C3752), in its note AND its halt, the way S3 holds steel's Directed to Set.
 * Plumbing's line strike coached "name who directed it closed … never backfill
 * on your own say-so" — a GC's say-so as the way past a struck line; concrete's
 * conditions notice asked for "written direction on how to go" over "a line in
 * the trench" and walls "sloughing"; flooring's You Told Me To Put It In Anyway
 * was the first answer for "old 9x9 tile" and never named the stuff. */
const WRITEUPS = [
  { rel: 'plumbing/docs.js', id: 'line-strike', note: [/owner/i, /releas/i], halt: [/make the calls/i],
    never: /who directed it closed if it wasn't|never backfill on your own say-so/i },
  { rel: 'concrete/docs.js', id: 'conditions-notice', note: [/locate/i, /competent person/i], halt: [/locate/i, /competent person/i] },
  { rel: 'flooring/docs.js', id: 'directed-to-proceed', note: [/9x9|9-by-9|nine-by-nine/i, /mastic|cutback/i, /survey|tested/i],
    halt: [/9x9|9-by-9|nine-by-nine/i, /mastic|cutback/i, /survey|tested/i] },
  /* The two directed write-ups whose own trade's note gained a fence this cycle —
   * found by the rider, not the audit: once the note says no written word clears
   * untested old paint or wire at the frame, a shelf that writes up "you told me
   * to coat / hang it" over exactly that is the gap the note just closed. */
  { rel: 'painting/docs.js', id: 'coated-under-protest', note: [/old paint nobody's tested/i, /no direction/i], halt: [/old paint nobody's tested/i, /wrong document/i] },
  { rel: 'doors/docs.js', id: 'hung-under-protest', note: [/wire at the frame/i, /no direction/i], halt: [/wire at the frame/i, /wrong document/i] },
  /* And two the lines verifier found by searching his words, not the shelf's names: concrete's
   * Directed Work Confirmation is the only answer to "he told me to", and plumbing's
   * Ready-for-Cover Letter is OUR release of the ground a struck line may lie in. */
  { rel: 'concrete/docs.js', id: 'directed-work-confirmation', note: [/line in the trench/i, /competent person/i, /no direction/i], halt: [/line in the trench/i, /competent person/i, /wrong document/i] },
  { rel: 'plumbing/docs.js', id: 'ready-for-cover', note: [/struck line/i, /owner/i, /no direction/i], halt: [/owner hasn't released|line got hit/i, /not ours to release/i] },
];
function writeupFaults(w, src) {
  const sb = { window: {} };
  vm.createContext(sb);
  try { vm.runInContext(src, sb); } catch (e) { return [`${w.rel} would not load: ` + String(e).split('\n')[0]]; }
  const d = (((sb.window.TRADE_DOCS || {}).docs) || []).find(x => x.id === w.id);
  if (!d) return [`no ${w.id} on ${w.rel.split('/')[0]}'s shelf`];
  const f = [];
  const note = String(d.note || ''), halt = [].concat(d.halt || []).join(' ');
  w.note.forEach(re => { if (!re.test(note)) f.push(`${w.id}'s note never says ${re}`); });
  w.halt.forEach(re => { if (!re.test(halt)) f.push(`${w.id}'s halt never says ${re}`); });
  if (w.never && w.never.test(JSON.stringify(d))) f.push(`${w.id} still coaches a say-so past the hold: ${JSON.stringify(d).match(w.never)[0]}`);
  return f;
}
/* S9 — HOLD NEVER PUTS A LOCKED-OUT UNIT BACK ON (C3752). HVAC's T&M tag closed
 * "or HOLD and I'll leave it the way I found it" under "It's unsafe — I've got it
 * locked out" and "Off and tagged — I shut it down", where the way he found it was
 * running. Run in both tongues through the SHIPPED shared/lang.js, with the ES
 * twins the ES page actually stores. */
function tmTagHoldFaults(itemsSrc, pageSrc, langSrc) {
  const f = [];
  for (const lang of ['en', 'es']) {
    const sb = { window: {}, localStorage: { getItem: () => lang, setItem() {} }, navigator: { language: 'en-US' },
      document: { documentElement: {}, getElementById: () => null, querySelector: () => null, createElement: () => ({ appendChild() {}, setAttribute() {} }) },
      location: { reload() {} } };
    vm.createContext(sb);
    let cfg = null;
    try {
      vm.runInContext(langSrc, sb);
      sb.Lang = sb.window.Lang;
      vm.runInContext(itemsSrc, sb);
      sb.Note = { mount: c => { cfg = c; return { refresh() {}, get() {} }; } };
      const js = (pageSrc.match(/<script>([\s\S]*?)<\/script>/g) || []).map(m => m.replace(/^<script>|<\/script>$/g, '')).join('\n');
      vm.runInContext(js, sb);
    } catch (e) { if (!cfg) return [`the hvac tag would not run in the sandbox (${lang}): ` + String(e).split('\n')[0]]; }
    if (!cfg) return ['the hvac tag never mounted a note'];
    const T = sb.window.TOOLKIT_ITEMS.tag || {}, ES = sb.window.TOOLKIT_ITEMS.tag_es || {};
    const tw = (k, en) => lang === 'en' ? en : ((ES[k] || []).find(p => p.en === en) || { es: en }).es;
    const unsafe = (T.found || []).filter(x => x.staysOff).map(x => tw('found', x.name));
    const off = (T.right || []).filter(x => x.staysOff).map(x => tw('right', x.v));
    if (!unsafe.length || !off.length) return ['no found tick or right-now pick carries staysOff — the locked-out unit is not marked in the data'];
    const say = (found, right) => (cfg.closing || []).map(x => typeof x === 'function' ? x(k => (k === 'found' ? found : k === 'right' ? right : '')) : x).join('\n');
    const BACK = /the way I found it|como lo encontré/;
    unsafe.forEach(nm => { if (BACK.test(say([nm], ''))) f.push(`(${lang}) HOLD under "${nm}" still leaves it the way he found it`); });
    off.forEach(v => { if (BACK.test(say([], v))) f.push(`(${lang}) HOLD under "${v}" still leaves it the way he found it`); });
    if (!BACK.test(say([], ''))) f.push(`(${lang}) with nothing locked out, HOLD lost the line it always had`);
  }
  return f;
}
/* S10 — HIS OWN EXTRA LINE NEVER CLEARS THE HOLD EITHER (C3752). The engine emits
 * "EXTRA INSTRUCTIONS FROM ME — OBEY THESE TOO" last, after the note and the halt,
 * so "backfill it as soon as the GC says" typed there rode over a halt that had
 * just said no direction releases a struck line. Read off the SHIPPED engine: the
 * exception sits between that heading and his text, on every shelf at once. */
function extraFaults(engineSrc) {
  const m = engineSrc.match(/function emitExtra\(L\) \{([\s\S]*?)\n  \}/);
  if (!m) return ['shared/docspec.js has no emitExtra'];
  const body = noComments(m[1]);
  const head = body.indexOf('OBEY THESE TOO'), exc = body.search(/Except one that would clear a hold this document says only its owner clears/), his = body.indexOf('S.extra.trim()');
  if (exc === -1) return ['the extra-instructions block carries no exception for a hold only its owner clears'];
  if (!(head < exc && exc < his)) return ['the exception is not between the heading and his text'];
  return [];
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
  NOTES.forEach(n => {
    const pg = read(n.page);
    const planted = pg.replace(/closing: \[/, 'closing: [\n      "Or reply ' + n.word + ' and we do it as it sits — in writing.",');
    ok(planted !== pg && noteBehaviour(n, read(n.items), planted).length > 0, `PROVE  a static ${n.word} line planted on ${n.page} goes red (S7)`);
  });
  const shelf = (id, note, halt) => 'window.TRADE_DOCS = ' + JSON.stringify({ docs: [{ id, note, halt }] }) + ';';
  WRITEUPS.forEach(w => {
    const bare = writeupFaults(w, shelf(w.id, 'narrative only', 'Only if the condition itself is not described.'));
    ok(bare.length > 0 && bare.every(x => /never says/.test(x)), `PROVE  ${w.id} with no fence in its note or halt goes red, for that reason (S8)`);
  });
  const sayso = writeupFaults(WRITEUPS[0], shelf('line-strike', 'the owner released it', 'make the calls. Never backfill on your own say-so.'));
  ok(sayso.length === 1 && /say-so/.test(sayso[0]), 'PROVE  the old say-so coaching planted back in the line strike goes red (S8)');
  const eng = read('shared/docspec.js');
  const engCut = eng.replace(/\n    L\.push\("\(Except one that would clear[^\n]*\n/, '\n');
  ok(engCut !== eng && extraFaults(engCut).length > 0, 'PROVE  the extra-instructions exception taken out goes red (S10)');
  const hvItems = read('hvac/items.js'), hvPage = read('hvac/tm-tag.html');
  const hvPlanted = hvPage.replace(/var off = \(get\("found"\)[\s\S]*?get\("right"\)\];/, 'var off = false;');
  const hvF = tmTagHoldFaults(hvItems, hvPlanted, read('shared/lang.js'));
  ok(hvPlanted !== hvPage && hvF.length > 0 && hvF.every(x => /still leaves it the way he found it/.test(x)), "PROVE  hvac's HOLD switched back to 'the way I found it' goes red, for that reason (S9)");
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
  NOTES.forEach(n => {
    const nb = noteBehaviour(n, read(n.items), read(n.page));
    ok(nb.length === 0, `S7  ${n.page}, run: ${n.word} never on an empty note, a typed hold or a fenced one; offered on a closable hold; fenced stops ask for no written go` + (nb.length ? ': ' + nb.join('; ') : ''));
  });
  WRITEUPS.forEach(w => {
    const wf = writeupFaults(w, read(w.rel));
    ok(wf.length === 0, `S8  ${w.rel.split('/')[0]}'s ${w.id} names the hold no direction clears, in its note and its halt` + (wf.length ? ': ' + wf.join('; ') : ''));
  });
  const ex = extraFaults(read('shared/docspec.js'));
  ok(ex.length === 0, "S10 the write-up engine's extra instructions never clear a hold the document says only its owner clears" + (ex.length ? ': ' + ex.join('; ') : ''));
  const hv = tmTagHoldFaults(read('hvac/items.js'), read('hvac/tm-tag.html'), read('shared/lang.js'));
  ok(hv.length === 0, "S9  hvac's T&M tag, run in EN and ES: HOLD over a locked-out or off-and-tagged unit keeps it off until it's repaired" + (hv.length ? ': ' + hv.join('; ') : ''));
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
