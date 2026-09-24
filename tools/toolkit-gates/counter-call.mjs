/**
 * THE COUNTER CALL SAYS ONLY WHAT HE TYPED — a gate for siding/counter-call.html.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * Siding's supply-house order (C3749) is the page in this kit with the most
 * words that collide with another trade's and the most places a refusal can die
 * quietly: a nail type in a note placeholder, a gutter size offered as a choice,
 * a numbered profile in an example, a unit welded onto a number he never gave a
 * unit, a "1" on a line he only ticked to remember. The four-lens panel that
 * scored the page (6 · 7 · 7 · 6) found that NO shipped gate reads a shape #1
 * page's words — order-live-header, send-is-copy, no-clock and mobile-watertight
 * all run on it and none of them would notice "16 in. o.c." in a sub or roofing's
 * pink left in :root. So the words are asserted here, twice:
 *
 *   STATIC (plain node — the deploy runs this half against the staged artifact):
 *     V  every string in TOOLKIT_ITEMS.order is free of brands, the refusals'
 *        vocabulary (trade.js 1-12), roofing's words, and — on every NAME — the
 *        kit's own collisions (bare soffit / trim / panel / starter / coil / J /
 *        hanger / gutter / elbow; leader and conductor anywhere);
 *     U  each catalogue line is sold ONE way (`unit`, a unit the page knows) or
 *        TWO ways (`ways`), never both and never neither; every `ask` names an
 *        axis whose first option is a neutral question; no axis has a default;
 *        no line pre-fills a count;
 *     P  the page: comments stripped, no brand / roofing word anywhere and the
 *        refusal vocabulary only inside the warn block that names it as refused;
 *        :root is trade.js's palette; the title is the page's name and not the
 *        working title; no pickfilter, no lang layer, legacyKey: null, Qty opens
 *        blank, SAME LOT rides the write-in, and "extra" is not a charge;
 *     R  the registry carries it, and its words are held to V.
 *
 *   DRIVE (a real browser on the real page — local by default, or a base url):
 *     D  a filled-in call with two pasted lines and every catalogue line ticked
 *        produces a document that equals the clipboard, welds a unit only where
 *        the counter sells one way, never prints a count he did not type, names
 *        every counter callback (no count, a bare number on a two-way line, an
 *        open hand / way / back, no colour, nowhere to land), gathers SAME LOT
 *        as a strict subset, carries none of the banned words, prints the truck
 *        after his lines on a delivery and nothing of it on a will-call, and
 *        survives a reload, a Clear and a Start-from-last.
 *
 *   --prove runs the checkers against planted defects — one per class — and
 *   fails unless every one of them goes red. An assertion that was never run as
 *   a control is a guess dressed as a gate (§SCARS 2026-08-28).
 *
 *   node tools/toolkit-gates/counter-call.mjs                   # static + drive, local
 *   node tools/toolkit-gates/counter-call.mjs https://mrdirno.github.io/nested-resonance-memory-archive/
 *   node tools/toolkit-gates/counter-call.mjs --static --root=HELIOS-BRIDGE/dist
 *   node tools/toolkit-gates/counter-call.mjs --prove
 */
import { readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize, resolve } from 'path';
import vm from 'vm';

const args = process.argv.slice(2);
const STATIC_ONLY = args.includes('--static');
const PROVE = args.includes('--prove');
const rootArg = (args.find(a => a.startsWith('--root=')) || '').slice(7);
const BASE = args.find(a => /^https?:\/\//.test(a)) || '';
const ROOT = rootArg ? resolve(rootArg) : fileURLToPath(new URL('../../', import.meta.url));
const PAGE = 'siding/counter-call.html';

const fails = [], notes = [];
let checks = 0;
const ok = (c, m) => { checks++; (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };

/* ── THE WORDS ─────────────────────────────────────────────────────────────── */
/* Full names only — never "quad", "royal" or "mastic" alone (roofing prints
 * "mastic" as a plain noun). These are here to be REFUSED; they never appear on
 * a page. */
const BRAND = /\b(hardie\w*|colorplus|smartside|certainteed|alside|ply ?gem|kaycan|norandex|gentek|variform|georgia[- ]pacific|azek|versatex|royal building|boral|truexterior|miratec|fypon|tyvek|typar|zip system|vycor|osi quad|quad max|geocel|sashco|big stretch|alu-?rex|amerimax|englert|leaffilter|gutter helmet|tapco|van mark|mid-america|malco|pac-?tool|abc supply|beacon roofing|srs distribution|musket brown|arctic white|cedarmill|nichiha|allura|mitten|diablo|builders edge|home depot|lowe'?s|menards)\b|\b(LP|DAP)\b/i;
const REFUSAL = [
  [/\bexposures?\b|\breveal\b|to the weather|course height|off (the )?grade/i, 'exposure, reveal or clearance to grade (refusals 1 and 3)'],
  [/\b(double|triple)[- ]?\d|\bD\d(\.\d)?\b/i, 'a numbered profile — the digit is the course exposure (refusal 3)'],
  [/\bo\.?c\.?\b|on cent(er|re)|\bspacing\b|\bgaps?\b|\boverlaps?\b|\bclearances?\b/i, 'a spacing, gap or clearance (refusals 2, 3, 5)'],
  [/\b(nails?|nailing|screws?|staples?|rivets?|ring[- ]shank|stainless|hot[- ]dip\w*|galv\w*|hdg|penny)\b|\b\d+d\b/i, 'a fastener type (refusal 2)'],
  [/\b[5-7]\s*(-|–)?\s*(in\b|inch|"|”)|k[- ]?style|half[- ]round|\b\d\s*[x×]\s*\d\b/i, 'a gutter or downspout size (refusal 5)'],
  [/\bwarrant\w*|\blifetime\b|\btransferable\b|\bguarante\w*/i, 'a warranty statement (refusal 10)'],
  [/\b(rated|ratings?|high[- ]wind|hurricane|impact[- ]resist\w*|class a|fire[- ]rated|ignition|wui|ember|certified)\b/i, 'a rating (refusals 1 and 9)'],
  [/\b(price[ds]?|pricing|quote[ds]?|estimat\w*|budget|invoice)\b|\$\d|\bcosts?\b(?!\s*code)/i, 'money (refusal 11)'],
  [/\b(net free area|nfa|irc|ibc|permit\w*|inspection\w*)\b|\bcodes?\b/i, 'a code call, permit or inspection (refusal 9)'],
  [/\blead[- ](safe|paint|based|test\w*)|\basbestos\b|\brrp\b|\bhepa\b|\bcontainment\b|safe to (cut|sand|remove|pull)|pre-?19\d\d/i, 'a lead or asbestos word (refusal 6)'],
  [/\b(rot|rotten|mou?ld|mildew|moisture|sheathing|osb|plywood)\b/i, 'rot, moisture, mould or sheathing (refusals 7 and 8)'],
  [/\b(weather[- ]?tight|water[- ]?tight|complete package|everything you need|all set)\b/i, 'a release or sufficiency claim (refusal 12)'],
  [/\bR-?\d+\b|r-value/i, 'an R-value'],
  /* Refusal 2's and refusal 5's OWN words (C3750) — the list was closed and an
   * audit planted each of these green. */
  [/\bgauge\b|\bedge distance\b|\bpenetration depth\b|\bpatterns?\b|\bper (board|piece|course|stud|square)\b/i, 'a fastening spec — gauge, edge distance, depth, pattern or a count per board (refusal 2)'],
  [/\bslopes?\b|\bper (10|ten) ?f(oo|ee)?t\b|\bfall of\b|\bpitch (it|them|the gutter)\b/i, 'a gutter slope (refusal 5)'],
];
const DONOR = /drip[- ]?edge|\bshingles?\b|underlayment|\bridge\b|dry-in|ice[- ](and|&)[- ]water|\bvalley\b|kick[- ]?out|step[- ]?flash\w*|counter-?flash\w*|\broof/i;
/* On every NAME (an item, a category, a flag, an axis, the title, the registry
 * name): the kit's own collisions, trade.js THE NAME COLLISIONS. */
const NAME_COLLISIONS = [
  [/(?<!eave )\bsoffits?\b/i, 'bare "soffit" — framing\'s is inside the building, roofing\'s is a vent: say the eave soffit'],
  [/\btrim\b(?! coil| boards?)/i, 'bare "trim" — framing\'s interior trim unless EXTERIOR is on it'],
  [/(?<!siding )\bstarter\b/i, 'bare "starter" — roofing sells a shingle starter strip by the bundle'],
  [/(?<!trim |gutter )\bcoils?\b/i, 'bare "coil" — HVAC\'s coils, and two different rolls in this kit'],
  [/\bhangers?\b(?! — for the gutter)/i, 'bare "hangers" — framing, electrical, plumbing and steel all hang things'],
  [/(?<!the )\bgutters?\b/i, 'bare "gutter" — concrete\'s and paving\'s curb and gutter'],
  [/(?<!downspout )\belbows?\b/i, 'bare "elbows" — a plumber\'s fitting'],
];
const NAME_OK_TRIM = /\bexterior\b|\butility trim\b/i;   // a name carrying trim says EXTERIOR, or is the utility trim
/* On EVERY string: never these, in any context. */
const ANY_COLLISIONS = [
  [/\bleaders?\b|conductor head/i, '"leader" — electrical\'s fish leader; say downspout'],
  [/\bpanels?\b/i, '"panel" — the load centre on twelve kits'],
  [/(?<![\w-])J(?![\w-])/, 'bare "J" — framing\'s J-bead sits next to it; say J-channel'],
];
const CLOCK = /if i don'?t hear|unless i hear|deemed|considered approved|no reply means|your silence|i'?ll take it as/i;

function collectStrings(o, out = []) {
  if (typeof o === 'string') out.push(o);
  else if (Array.isArray(o)) o.forEach(x => collectStrings(x, out));
  else if (o && typeof o === 'object') Object.keys(o).forEach(k => collectStrings(o[k], out));
  return out;
}
function namesOf(order) {
  const names = [];
  order.cats.forEach(c => {
    names.push(c.name, c.docName || '');
    (c.items || []).forEach(i => {
      names.push(i.n);
      (i.flags || []).forEach(f => names.push(f.label));
      (i.ax || []).forEach(a => names.push(a.label));
    });
  });
  (order.writeinFlags || []).forEach(f => names.push(f.label));
  return names.filter(Boolean);
}

/* The checkers are plain functions so --prove can feed them planted defects. */
/* THE KIT'S OWN EXAMPLE OUTFIT is "Rivet Exteriors" (every siding placeholder
 * signs as Dale W of it), and "rivet" is also a fastener — the one place a word
 * this gate refuses is a proper noun the kit already prints. Lifted out by exact
 * phrase, never by the bare word. */
const KIT_NAMES = /\bRivet Exteriors\b/g;
function wordFaults(s, { names = false, refusals = true } = {}) {
  const f = [];
  s = String(s).replace(KIT_NAMES, ' ');
  if (BRAND.test(s)) f.push('a brand or product line');
  if (DONOR.test(s)) f.push('a roofing word');
  if (refusals) REFUSAL.forEach(([re, why]) => { if (re.test(s)) f.push(why); });
  ANY_COLLISIONS.forEach(([re, why]) => { if (re.test(s)) f.push(why); });
  if (names) NAME_COLLISIONS.forEach(([re, why]) => {
    if (!re.test(s)) return;
    if (/trim/.test(why) && NAME_OK_TRIM.test(s)) return;
    f.push(why);
  });
  return f;
}
const UNITS_KNOWN = ['piece', 'roll', 'ea'];
function structureFaults(order) {
  const f = [];
  const wi = order.cats[0];
  if (!wi || !wi.writein) f.push('the write-in is not the first section');
  if (!(order.writeinFlags || []).some(x => x.k === 'lot')) f.push('SAME LOT does not ride the write-in');
  order.cats.slice(1).forEach(c => (c.items || []).forEach(i => {
    if (!!i.unit === !!i.ways) f.push(`${i.n}: sold ${i.unit && i.ways ? 'both one way and two ways' : 'neither one way nor two ways'}`);
    if (i.unit && UNITS_KNOWN.indexOf(i.unit) === -1) f.push(`${i.n}: unit "${i.unit}" is not one the page prints`);
    if (i.qtyDefault != null && i.qtyDefault !== '') f.push(`${i.n}: pre-fills a count`);
    (i.ax || []).forEach(a => {
      if (a.def != null) f.push(`${i.n}: axis "${a.label}" has a default`);
      if (!/^— .+ —$/.test(String(a.opts && a.opts[0]))) f.push(`${i.n}: axis "${a.label}" does not open on a neutral question`);
    });
    (i.ask || []).forEach(k => { if (!(i.ax || []).some(a => a.k === k)) f.push(`${i.n}: asks "${k}" but has no such axis`); });
  }));
  return f;
}

function loadOrder(root) {
  const src = readFileSync(join(root, 'siding', 'items.js'), 'utf8');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox);
  return sandbox.window.TOOLKIT_ITEMS && sandbox.window.TOOLKIT_ITEMS.order;
}
function loadTrade(root) {
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(readFileSync(join(root, 'siding', 'trade.js'), 'utf8'), sandbox);
  vm.runInContext(readFileSync(join(root, 'siding', 'tools.js'), 'utf8'), sandbox);
  return { trade: sandbox.window.TOOLKIT_TRADE, tools: sandbox.window.TOOLKIT_TOOLS };
}
/* The page as a reader and a browser meet it: HTML comments, the stylesheet and
 * JS comments gone (a comment may NAME a refused word to explain the refusal),
 * the warn block split out (it names the refused things as refused). */
/* The warn block's job is to NAME what the page refuses, so its "no …" list is
 * lifted out before its words are checked — and anything left that a refusal
 * forbids fails it (a positive "leave a gap" inside the warn is still a gap). */
const WARN_NEGATED = /\bno (squares figured off a drawing|fastener|gap|exposure|clearance|gutter or downspout size|hanger layout|flashing detail|rating|warranty term)s?\b|\bor the code\b/gi;
function attrText(html) {
  const out = [];
  html.replace(/<!--[\s\S]*?-->/g, ' ').replace(/\b(placeholder|content|title|aria-label|alt)="([^"]*)"/gi, (m, k, v) => { out.push(v); return m; });
  return out.join(' \n ');
}
/* AN INLINE SCRIPT IS READ FOR ITS STRINGS, NEVER AS TEXT (C3750). This used to
 * paste the script's code into the page text and strip tags after — and the "<"
 * of `ymd.length < 3` opened a pseudo-tag that ran to the next ">" nine thousand
 * characters later, so the textarea's placeholder (where the siding itself is
 * typed), the note placeholder and every sentence the script builds into the
 * message were never read. Only a string can reach the glass or the message, so
 * the string literals ARE the script's words: comments out, then every quoted
 * literal, escapes resolved. */
function scriptStrings(js) {
  const code = js.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:"'\\])\/\/.*$/gm, '$1');
  const out = [];
  code.replace(/"((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)'/g, (m, a, b) => {
    out.push((a !== undefined ? a : b).replace(/\\n/g, ' ').replace(/\\u([0-9a-f]{4})/gi, (x, h) => String.fromCharCode(parseInt(h, 16))).replace(/\\(.)/g, '$1'));
    return m;
  });
  return out.join(' \n ');
}
function pageText(html) {
  let s = html.replace(/<!--[\s\S]*?-->/g, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ');
  s = s.replace(/<script>([\s\S]*?)<\/script>/gi, (m, js) => ' ' + scriptStrings(js) + ' ');
  const warn = (s.match(/<div class="warn">([\s\S]*?)<\/div>/) || [, ''])[1];
  const rest = s.replace(/<div class="warn">[\s\S]*?<\/div>/, ' ');
  const plain = t => t.replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ');
  return { rest: plain(rest) + ' \n ' + attrText(rest), warn: plain(warn) };
}

/* ── THE DOCUMENT CHECKERS ─────────────────────────────────────────────────── */
function docFaults(doc, expect) {
  const f = [];
  /* The truck's half is shared/dropoff.js's block, with its own chips and its
   * own gate (dropoff-block.mjs) — "On the roof" is one of its landings on every
   * trade. His words and ours are checked; the shared block's are not re-owned. */
  const body = doc.replace(/\n\nHOW IT GETS IN AND WHERE IT LANDS\n[\s\S]*?not a booking[^\n]*/g, '')
    .replace(/\bcost code\b/gi, '').replace(/\bgate code\b/gi, '');
  wordFaults(body).forEach(x => f.push('the document carries ' + x));
  if (CLOCK.test(doc)) f.push('the document turns silence into a yes');
  if (/no number on it/i.test(doc)) f.push('"no number on it" — it prints right under his PO');
  if (!/Field request — not a PO, and there's no money on it\./.test(doc)) f.push('the closing lost "Field request — not a PO"');
  (expect.welded || []).forEach(([name, want]) => {
    const re = new RegExp('^- ' + want.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '  ' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'm');
    if (!re.test(doc)) f.push(`a one-way line lost its unit: expected "- ${want}  ${name}"`);
  });
  (expect.twoWay || []).forEach(([name, q]) => {
    const esc = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (!new RegExp('^- ' + q + '  ' + esc, 'm').test(doc)) f.push(`a two-way line was re-counted: expected "- ${q}  ${name}" bare`);
    if (!new RegExp('a bare ' + q + ' on ' + esc + ' — ').test(doc)) f.push(`a bare number on a two-way line was not asked: ${name}`);
  });
  (expect.blank || []).forEach(name => {
    const esc = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (!new RegExp('^- ' + esc + '(  |$)', 'm').test(doc)) f.push(`a line he only ticked printed a count he never typed: ${name}`);
  });
  (expect.asked || []).forEach(s => { if (doc.indexOf(s) === -1) f.push('a counter callback is missing: ' + s); });
  return f;
}

/* ── STATIC ────────────────────────────────────────────────────────────────── */
function staticChecks(root) {
  const pagePath = join(root, PAGE);
  ok(existsSync(pagePath), `${PAGE} is staged`);
  if (!existsSync(pagePath)) return;
  const order = loadOrder(root);
  ok(!!(order && order.cats && order.cats.length), 'siding/items.js declares TOOLKIT_ITEMS.order');
  if (!order) return;
  const lines = order.cats.reduce((n, c) => n + (c.items || []).length, 0);
  ok(lines >= 20 && lines <= 40, `the picker is a jog, not a catalog (${lines} lines)`);

  const vocab = collectStrings(order);
  const vf = [];
  vocab.forEach(s => wordFaults(s).forEach(x => vf.push(`"${s.slice(0, 60)}" — ${x}`)));
  ok(vf.length === 0, `V  every one of ${vocab.length} vocabulary strings is clean` + (vf.length ? ':\n        ' + vf.join('\n        ') : ''));
  const nf = [];
  namesOf(order).forEach(s => wordFaults(s, { names: true }).forEach(x => nf.push(`"${s}" — ${x}`)));
  ok(nf.length === 0, 'V  every name is free of the kit\'s collisions' + (nf.length ? ':\n        ' + nf.join('\n        ') : ''));

  const sf = structureFaults(order);
  ok(sf.length === 0, 'U  every line is sold one way or two, every ask has a neutral, nothing is pre-filled' + (sf.length ? ':\n        ' + sf.join('\n        ') : ''));

  const html = readFileSync(pagePath, 'utf8');
  const { rest, warn } = pageText(html);
  const pf = wordFaults(rest.replace(/\bcost code\b/gi, '').replace(/\bgate code\b/gi, '')).map(x => 'outside the warn block: ' + x);
  wordFaults(warn.replace(WARN_NEGATED, ' ')).forEach(x => pf.push('in the warn block: ' + x));
  ok(pf.length === 0, 'P  the page\'s own words are clean (refusals named only in the warn block)' + (pf.length ? ':\n        ' + pf.join('\n        ') : ''));
  ok(/no exposure/.test(warn) && /warranty term/.test(warn) && /Double-check it before you send it/.test(warn),
    'P  the warn block names what the page refuses and says double-check it');

  const { trade, tools } = loadTrade(root);
  const rootCss = (html.match(/:root\{([\s\S]*?)\}/) || [, ''])[1];
  const v = k => ((rootCss.match(new RegExp('--' + k + ':\\s*(#[0-9A-Fa-f]{6})')) || [, ''])[1] || '').toUpperCase();
  ok(v('flag') === String(trade.accent).toUpperCase() && v('deep') === String(trade.accentDeep).toUpperCase()
     && v('tint') === String(trade.accentTint).toUpperCase() && v('flag-ink') === String(trade.accentInk).toUpperCase(),
    `P  :root wears siding's palette (flag ${v('flag')} deep ${v('deep')} tint ${v('tint')} ink ${v('flag-ink')})`);
  const title = (html.match(/<title>([^<]*)<\/title>/) || [, ''])[1];
  const apple = (html.match(/apple-mobile-web-app-title" content="([^"]*)"/) || [, ''])[1];
  ok(/^The Counter Call — Siding &amp; Exteriors Field Toolkit$/.test(title) && apple === 'The Counter Call',
    `P  the title is the page's name ("${title}" / "${apple}")`);
  ok(!/pickfilter\.js|lang\.js/.test(html), 'P  no filter bar above the write-in and no language layer this page never asked for');
  ok(/filter:\s*false/.test(html), 'P  the engine is told the list is short enough to read whole (filter: false)');
  ok(/legacyKey:\s*null/.test(html), 'P  the job card says it has no predecessor (legacyKey: null)');
  ok(/qtyDefault:\s*""/.test(html) && /writeinQtyDefault:\s*""/.test(html), 'P  every Qty opens blank — a tick means "remember this", never "one"');
  ok(/writeinFlags:\s*D\.writeinFlags/.test(html), 'P  SAME LOT rides the lines he types');
  const charge = (html.match(/<select id="fCharge">([\s\S]*?)<\/select>/) || [, ''])[1];
  ok(/>Job</.test(charge) && !/T&amp;M|extra/i.test(charge), 'P  "T&M / extra" is not a charge on a page that ships no extra-work tag');

  const entry = (tools || []).find(t => t.href === 'counter-call.html');
  ok(!!entry, 'R  the registry carries the page, so the hub and every page\'s Tools menu list it');
  if (entry) {
    const rf = wordFaults(entry.name, { names: true }).concat(wordFaults(entry.desc));
    ok(rf.length === 0, `R  the registry's name and description are clean` + (rf.length ? ': ' + rf.join('; ') : ''));
  }
}

/* ── PROVE ─────────────────────────────────────────────────────────────────── */
function prove() {
  const plant = [
    ['brand', () => wordFaults('the ColorPlus in the clay').length],
    ['refusal 2', () => wordFaults('siding nails — the length off your instructions').length],
    ['refusal 3', () => wordFaults('double 4 in the clay').length],
    ['refusal 5', () => wordFaults('5 in. K-style').length],
    ['refusal 10', () => wordFaults('matched for the warranty').length],
    ['refusal 11', () => wordFaults('about $40 a square').length],
    ['roofing word', () => wordFaults('20 stick drip edge').length],
    ['refusal 2 (spec)', () => wordFaults('coil nails in the pattern off the sheet').length],
    ['refusal 5 (slope)', () => wordFaults('hangers — a quarter inch of slope per ten feet').length],
    ['bare soffit name', () => wordFaults('Soffit — vented', { names: true }).length],
    ['bare starter name', () => wordFaults('Starter strip', { names: true }).length],
    ['bare trim name', () => wordFaults('Trim & coil', { names: true }).length],
    ['bare J', () => wordFaults('which J — the siding\'s').length],
    ['panel', () => wordFaults('twelve siding panels').length],
  ];
  plant.push(
    ['capitalised numbered profile', () => wordFaults('Double 4 in the clay').length],
    ['spec word in a placeholder', () => wordFaults(pageText('<div class="head"><input id="fFor" placeholder="8d galv nails 16 in. o.c."></div><div class="warn">x</div>').rest).length],
    ['brand and roof words in the meta description', () => wordFaults(pageText('<meta name="description" content="Roof shingles off the Tyvek counter"><div class="warn">x</div>').rest).length],
    ['positive refusal inside the warn block', () => wordFaults(pageText('<div class="warn">This page sets no gap. Leave a 3/16 gap at every butt joint.</div>').warn.replace(WARN_NEGATED, ' ')).length],
    ['gutter size and warranty in a registry description', () => wordFaults('5 in K-style gutters and a lifetime warranty on the lot').length]
  );
  plant.forEach(([k, fn]) => ok(fn() > 0, `PROVE  the word checker goes red on a planted ${k}`));
  /* AND THE CONTROL THE OTHER WAY: the warn's own "no …" list is lifted out, so
     naming a refusal as refused is not itself a fault. */
  ok(wordFaults(pageText('<div class="warn">no fastener, no gap, no exposure, no clearance, no gutter or downspout size, no hanger layout, no flashing detail, no rating and no warranty term</div>').warn.replace(WARN_NEGATED, ' ')).length === 0,
    'PROVE  the warn block may name what the page refuses without failing');

  const good = loadOrder(ROOT);
  const clone = JSON.parse(JSON.stringify(good));
  const j = clone.cats[1].items.find(i => i.n === 'J-channel'); j.unit = 'piece';
  ok(structureFaults(clone).some(x => /J-channel/.test(x)), 'PROVE  the structure checker goes red on a unit welded to a two-way line');
  const clone2 = JSON.parse(JSON.stringify(good));
  const ec = clone2.cats.find(c => c.id === 'gutter').items.find(i => i.n === 'End caps'); ec.ax[0].opts = ['Left', 'Right'];
  ok(structureFaults(clone2).some(x => /End caps/.test(x)), 'PROVE  the structure checker goes red on an axis with no neutral');
  const clone3 = JSON.parse(JSON.stringify(good)); clone3.writeinFlags = [];
  ok(structureFaults(clone3).some(x => /SAME LOT/.test(x)), 'PROVE  the structure checker goes red when SAME LOT leaves the write-in');

  const doc = "COUNTER CALL\n\nEAVE SOFFIT & FASCIA\n- 10 pieces  Eave soffit — vented\n- 1  End caps\n\nField request — not a PO, and there's no number on it.";
  const df = docFaults(doc, { twoWay: [['Eave soffit — vented', '10']], blank: ['End caps'], asked: ['End caps — left or right?'] });
  ok(df.some(x => /re-counted/.test(x)), 'PROVE  the document checker goes red on a two-way line given a unit');
  ok(df.some(x => /never typed/.test(x)), 'PROVE  the document checker goes red on a count he never typed');
  ok(df.some(x => /no number on it/.test(x)), 'PROVE  the document checker goes red on "no number on it"');
  ok(df.some(x => /callback is missing/.test(x)), 'PROVE  the document checker goes red on a missing callback');
  ok(docFaults('- 2  Trim coil\nField request — not a PO, and there\'s no money on it.', { welded: [['Trim coil', '2 rolls']] }).length > 0,
    'PROVE  the document checker goes red on a one-way line that lost its unit');
}

/* ── DRIVE ─────────────────────────────────────────────────────────────────── */
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
function serve(root) {
  return new Promise(res => {
    const s = createServer((rq, rs) => {
      const rel = normalize(decodeURIComponent(rq.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      const p = join(root, rel);
      if (!p.startsWith(root) || !existsSync(p) || statSync(p).isDirectory()) { rs.writeHead(404); return rs.end('no'); }
      rs.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
      rs.end(readFileSync(p));
    });
    s.listen(0, '127.0.0.1', () => res({ s, port: s.address().port }));
  });
}

async function drive() {
  const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
  const { chromium } = require('playwright');
  let server = null, base = BASE;
  if (!base) { server = await serve(ROOT); base = `http://127.0.0.1:${server.port}/`; }
  base = base.replace(/\/*$/, '/');
  const b = await chromium.launch({ args: ['--mute-audio'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(() => {
    window.__copied = null;
    Object.defineProperty(navigator, 'clipboard', { configurable: true,
      value: { writeText: t => { window.__copied = String(t); return Promise.resolve(); } } });
  });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.goto(base + PAGE, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => document.querySelectorAll('#list li.item').length > 20, null, { timeout: 15000 });
  await p.waitForTimeout(400);

  const preview = async () => (await p.textContent('#preview')) || '';
  const row = name => p.locator('#list li.item', { has: p.locator('.name', { hasText: new RegExp('^' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$') }) }).first();
  const tick = async (name, qty, note) => {
    const li = row(name);
    await li.locator('.tick').check();
    if (qty != null) await li.locator('.i-qty').fill(qty);
    if (note != null) await li.locator('.i-note').fill(note);
    return li;
  };

  await p.fill('#fJob', '412 Marchmont — full re-side');
  await p.fill('#fBy', 'Dale W — Rivet Exteriors — 559-555-0143');
  await p.fill('#fFor', 'rear and both gables — tear-off Thursday');
  await p.fill('#fCol', 'body clay · trim white');
  const wi = p.locator('#list .cat').first().locator('.wi-input');
  await wi.fill('6 box dutch lap — the clay\n160 ft of gutter & 6 downspouts — white');
  await p.locator('#list .cat').first().locator('.wi-add').click();
  await p.locator('#list .cat').first().locator('li.item').first().locator('.i-flag').check();

  /* Every catalogue line ticked: some counted, some only ticked, two-way lines
     given a bare number, one-way lines given a bare number, some axes answered
     and some left on the neutral, colour said on some and not on others. */
  await tick('Siding starter strip', '');
  await tick('Outside corners', '4', 'white');
  await tick('Inside corners', '', 'white');
  await tick('J-channel', '14');
  await tick('Utility trim / undersill', '12 pc', 'white');
  await tick('Drip cap / Z-flashing', '6 pc', 'white');
  await tick('Eave soffit — vented', '10', 'white');
  await tick('Eave soffit — solid', '2 cartons', 'white');
  await tick('F-channel', '8 pc', 'white');
  await tick('Fascia cover', '120 ft', 'white');
  const coil = await tick('Trim coil', '2');
  await coil.locator('.i-flag').check();
  await tick('Exterior trim boards', '9 pc', 'white');
  await tick('Exterior window & door trim', '4 pc', 'white');
  await tick('Mounting blocks', '5', '3 light, 2 receptacle — white');
  await tick('Vent hoods', '2', 'white');
  await tick('Touch-up for the pre-finished', '1', 'clay');
  await tick('Downspout', '6', 'white');
  const elb = await tick('Downspout elbows', '12', 'white');
  await elb.locator('select.i-ax').selectOption('Front (A)');
  await tick('End caps', '4');
  await tick('Downspout outlets', '6', 'white');
  await tick('Hangers — for the gutter', '2 boxes');
  await tick('Downspout straps', '1 box', 'white');
  await tick('Sealant / caulk', '1 case', 'white');
  await tick('Fasteners', '3 boxes', 'the ones the instructions name');
  await tick('Housewrap', '2');
  await tick('Wrap tape', '');
  await tick('Saw blades', '2', 'for the fibre cement');
  await p.waitForTimeout(300);

  let doc = await preview();
  const delivered = doc;
  const f1 = docFaults(doc, {
    welded: [['Trim coil', '2 rolls'], ['Outside corners', '4 pieces'], ['Downspout', '6 pieces'], ['Mounting blocks', '5 ea'], ['Housewrap', '2 rolls'], ['Touch-up for the pre-finished', '1 ea']],
    twoWay: [['J-channel', '14'], ['Eave soffit — vented', '10']],
    blank: ['Siding starter strip', 'Inside corners', 'Wrap tape'],
    asked: ['with no count on them (Siding starter strip, Inside corners, Wrap tape)',
            'Trim coil — which back?', 'End caps — left or right?',
            'with no colour said (J-channel, Trim coil, End caps) — the house has more than one colour (up top), so don\'t pull those till I tell you which.',
            'Nothing on here says where it lands'],
  });
  ok(f1.length === 0, 'D  a full delivery call says only what he typed and asks what the counter would' + (f1.length ? ':\n        ' + f1.join('\n        ') : ''));
  ok(!/Downspout elbows — front or side\?/.test(doc) && /12 ea  Downspout elbows  ·  Front \(A\)/.test(doc), 'D  an answered axis prints and is not asked again');
  ok(/^- 2 rolls  Trim coil  \[SAME LOT\]$/m.test(doc) && /^- 6 box dutch lap — the clay  \[SAME LOT\]$/m.test(doc),
    'D  the SAME LOT tag rides the ticked line and the pasted one');
  const sameBlock = (doc.split('— — — SAME LOT AS WHAT\'S ALREADY UP — — —')[1] || '').split('\n\n')[0];
  ok(/- 6 box dutch lap — the clay/.test(sameBlock) && /- Trim coil/.test(sameBlock)
     && /pull each one off ONE lot and put the lot on the ticket/.test(sameBlock) && !/ALL OF IT/.test(doc),
    'D  SAME LOT gathers the pasted siding and the ticked coil, asks for ONE lot per product, and never says it all comes off one lot');
  /* THE TRUCK'S HALF, AFTER HIS LINES: the counter keys the lines at three,
     dispatch reads the gate at six. Fill the block the way a man does — the gate
     line first, the landing forgotten — then answer the landing. */
  await p.locator('details.more > summary').click();
  await p.fill('#do-gate', 'side gate off the driveway, past the meter');
  await p.waitForTimeout(200);
  doc = await preview();
  const iTruck = doc.indexOf('HOW IT GETS IN AND WHERE IT LANDS'), iLast = doc.indexOf('- 2 ea  Saw blades'), iCharge = doc.indexOf('Charge to: Job');
  ok(iTruck > iLast && iLast > 0 && iCharge > iTruck, `D  the truck's half prints after his lines and before the charge (${iLast} < ${iTruck} < ${iCharge})`);
  ok(/Nothing on here says where it lands/.test(doc), 'D  a gate with no landing is still asked where it lands');
  await p.locator('.do-chips[data-ax="land"] .do-chip[data-v="Ground — laydown or driveway"]').click();
  await p.waitForTimeout(200);
  doc = await preview();
  ok(/Set it: Ground — laydown or driveway/.test(doc) && !/Nothing on here says where it lands/.test(doc),
    'D  once it says where it lands, the counter is not asked');

  await p.fill('#fLot', 'LOT 0417-B off the first drop');
  await p.waitForTimeout(200);
  doc = await preview();
  ok(/Lots already up: LOT 0417-B off the first drop/.test(doc) && !/pull each one off ONE lot/.test(doc),
    'D  typed lots ride the SAME LOT block and replace the ONE-lot ask');
  /* THE C3749 AUDIT: one lot field used to switch the colour question off on
     every SAME LOT line, so a siding carton's lot silenced the coil. A line that
     shows with no colour said is asked, lot or no lot. */
  ok(/with no colour said \(J-channel, Trim coil, End caps\)/.test(doc),
    'D  with lots typed, a SAME LOT line that shows is still asked its colour');

  const copied = await p.evaluate(async () => { document.getElementById('copy').click(); await new Promise(r => setTimeout(r, 250)); return window.__copied; });
  ok(copied === (await preview()), `D  the clipboard is the preview, byte for byte (${(copied || '').length} chars)`);

  await p.locator('#segMode button[data-v="Will-call"]').click();
  await p.fill('#fPick', 'Luis, in the box truck — about 7');
  await p.waitForTimeout(200);
  doc = await preview();
  ok(/Will-call/.test(doc) && /Coming for it: Luis/.test(doc) && !/HOW IT GETS IN/.test(doc) && !/Nothing on here says where it lands/.test(doc)
     && /have what you've got ready/.test(doc) && !/send what you've got/.test(doc),
    'D  a will-call carries who is coming, none of the truck\'s half, and a close worded for a pickup');
  ok(docFaults(doc, {}).length === 0, 'D  the will-call document is clean too');

  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => document.querySelectorAll('#list li.item.is-checked').length > 20, null, { timeout: 15000 });
  await p.waitForTimeout(300);
  const after = await preview();
  ok(after === doc, `D  a reload brings back the whole call — lines, header, mode and lot (${after.length} vs ${doc.length} chars)`);

  ok(!(await p.isVisible('#last')), 'D  "Start from last call" is not offered above a live call');
  await p.click('#clear');
  await p.waitForTimeout(250);
  ok(/\(nothing on it yet\)/.test(await preview()), 'D  Clear empties the call');
  ok(await p.isVisible('#last'), 'D  Clear offers "Start from last call"');
  await p.click('#last');
  await p.waitForTimeout(300);
  const back = await preview();
  ok(/6 box dutch lap — the clay/.test(back) && /2 rolls  Trim coil/.test(back), 'D  "Start from last call" brings the lines back');

  /* ── THE C3749 AUDIT'S STATE BUGS, each driven the way a man meets it ── */
  const fresh = async () => { await p.click('#clear'); await p.waitForTimeout(200); };
  const pick = async (name, v) => { await row(name).locator('select.i-ax').selectOption(v); };

  // 1. Lines pasted and never Added go on the call, not in the bin.
  await fresh();
  await p.locator('#list .cat').first().locator('.wi-input').fill('3 box dutch lap — clay\n2 roll trim coil — white');
  const flushed = await p.evaluate(async () => { document.getElementById('copy').click(); await new Promise(r => setTimeout(r, 250)); return window.__copied || ''; });
  ok(/- 3 box dutch lap — clay/.test(flushed) && /- 2 roll trim coil — white/.test(flushed),
    'D  a pasted takeoff nobody tapped Add on still goes on the copied call');

  // 2. Clear takes the answers with it: a re-ticked row opens on its question.
  await fresh();
  await tick('End caps', '4', 'white'); await pick('End caps', 'Left');
  const coil2 = await tick('Trim coil', '2', 'white'); await pick('Trim coil', 'Mill back'); await coil2.locator('.i-flag').check();
  await fresh();
  await tick('End caps', '4', 'white'); await tick('Trim coil', '2', 'white');
  await p.waitForTimeout(200);
  doc = await preview();
  ok(/End caps — left or right\?/.test(doc) && /Trim coil — which back\?/.test(doc) && !/Trim coil  \[SAME LOT\]/.test(doc) && !/Mill back|·  Left/.test(doc),
    'D  Clear resets every row\'s selects and SAME LOT, so yesterday\'s answers never print as today\'s');

  // 3. "Some of each — in the note" with nothing in the note is still asked.
  await pick('End caps', 'Some of each — in the note');
  await row('End caps').locator('.i-note').fill('');
  await p.waitForTimeout(200);
  ok(/End caps — how many of each\?/.test(await preview()), 'D  "some of each" with an empty note is asked how many of each');
  await row('End caps').locator('.i-note').fill('2 left, 2 right — white');
  await p.waitForTimeout(200);
  ok(!/End caps — how many of each\?/.test(await preview()), 'D  and stops being asked once the note says it');

  // 4. A write-in that happens to spell a catalogue name is his sentence.
  await fresh();
  await p.locator('#list .cat').first().locator('.wi-input').fill('End caps');
  await p.locator('#list .cat').first().locator('.wi-add').click();
  await p.locator('#list .cat').first().locator('li.item').first().locator('.i-qty').fill('4');
  await p.waitForTimeout(200);
  doc = await preview();
  ok(/^- 4  End caps$/m.test(doc) && !/End caps — left or right\?/.test(doc),
    'D  a write-in spelled like a catalogue line gets no unit and no question it has no box to answer');

  // 5. An unsaid day and an unnamed site are asked, never printed as a prompt.
  await p.locator('#segWhen button[data-v="date"]').click();
  await p.fill('#fJob', '');
  await p.locator('#segMode button[data-v="Deliver it"]').click();
  await p.waitForTimeout(200);
  doc = await preview();
  ok(!/pick a time/.test(doc) && /I picked a day and didn't say which/.test(doc) && /No job or street on it/.test(doc),
    'D  a day not said and a delivery with no site are asked, and "pick a time" never prints');

  // 6. Start from last brings back the lines, never yesterday's urgency or day.
  await p.fill('#fDate', '2026-09-20T07:00');
  await p.check('#fHot');
  await p.fill('#fJob', '412 Marchmont — full re-side');
  await p.waitForTimeout(200);
  await fresh();
  ok(await p.isVisible('#last'), 'D  an empty call offers "Start from last call"');
  await tick('Housewrap', '1');
  await p.waitForTimeout(150);
  ok(!(await p.isVisible('#last')), 'D  ticking a line takes the offer away');
  await row('Housewrap').locator('.tick').uncheck();
  await p.waitForTimeout(150);
  ok(await p.isVisible('#last'), 'D  and emptying the call brings it back');
  // The stashed call is made YESTERDAY's: the engine stamps when a list was saved
  // and the page drops urgency, day and driver only off an earlier day (C3750).
  await p.evaluate(() => {
    const k = 'toolkit.siding.counterCall.v1.last', r = JSON.parse(localStorage.getItem(k));
    r.t = Date.now() - 2 * 86400000; localStorage.setItem(k, JSON.stringify(r));
  });
  await p.click('#last');
  await p.waitForTimeout(300);
  doc = await preview();
  ok(/^- 4  End caps$/m.test(doc) && !/SHORT ON THE WALL/.test(doc) && /Need it: in the morning/.test(doc),
    'D  "Start from last call" restores yesterday\'s lines without yesterday\'s SHORT ON THE WALL or its date');

  // 7. ...but a call saved TODAY is his own list coming back after a stray Clear,
  //    urgency and day and all (C3750 — the audit's undo that dropped them).
  await p.check('#fHot');
  await p.locator('#segWhen button[data-v="date"]').click();
  await p.fill('#fDate', '2026-09-30T07:00');
  await p.waitForTimeout(300);
  await fresh();
  ok(await p.isVisible('#last'), 'D  a stray Clear leaves "Start from last call" on the glass');
  await p.click('#last');
  await p.waitForTimeout(300);
  doc = await preview();
  ok(/^- 4  End caps$/m.test(doc) && /SHORT ON THE WALL/.test(doc) && !/Need it: in the morning/.test(doc),
    'D  undoing a stray Clear brings today\'s call back with its SHORT ON THE WALL and its day');

  const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(over <= 0, `D  no sideways scroll at 390px with the whole call on it (${over}px)`);
  ok(errs.length === 0, 'D  zero page errors' + (errs.length ? ': ' + errs.slice(0, 2).join(' | ') : ''));

  /* 8. THE REAL DAY, NOT A REWRITTEN `t` (C3751). Check 6 above backdates the
   *    stored stamp by hand, so it could not see that every save — opening the
   *    page, a blur, Clear's own — restamped it to today, which let yesterday's
   *    SHORT ON THE WALL and driver ride into the next call. This one crosses a
   *    real midnight on the browser's clock and touches nothing in storage. */
  {
    const c2 = await b.newContext({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true });
    const d1 = await c2.newPage();
    await d1.clock.install({ time: new Date('2026-09-23T15:00:00') });
    await d1.goto(base + PAGE, { waitUntil: 'domcontentloaded' });
    await d1.waitForFunction(() => document.querySelectorAll('#list li.item').length > 20, null, { timeout: 15000 });
    await d1.fill('#fJob', '88 Alder Ct'); await d1.dispatchEvent('#fJob', 'change');
    await d1.locator('#segMode button[data-v="Will-call"]').click();
    await d1.fill('#fPick', 'Luis, in the box truck — about 7'); await d1.dispatchEvent('#fPick', 'input');
    await d1.check('#fHot');
    await d1.fill('.wi-input', '12 sq dutch lap — clay'); await d1.click('.wi-add');
    await d1.waitForTimeout(600);
    await d1.close();
    const d2 = await c2.newPage();
    await d2.clock.install({ time: new Date('2026-09-24T15:05:00') });
    await d2.goto(base + PAGE, { waitUntil: 'domcontentloaded' });
    await d2.waitForFunction(() => document.querySelectorAll('#list li.item').length > 20, null, { timeout: 15000 });
    await d2.waitForTimeout(500);
    await d2.click('#clear'); await d2.waitForTimeout(250);
    await d2.click('#last'); await d2.waitForTimeout(300);
    const s = await d2.evaluate(() => ({ hot: document.getElementById('fHot').checked, pick: document.getElementById('fPick').value, doc: document.getElementById('preview').textContent }));
    ok(/12 sq dutch lap/.test(s.doc) && !s.hot && !s.pick && !/SHORT ON THE WALL/.test(s.doc),
      `D  a call built yesterday, reopened today, Cleared and restored comes back without yesterday's SHORT ON THE WALL or driver (hot=${s.hot}, driver="${s.pick}")`);

    /* 9. THE CALL STAYS WITH ITS HOUSE (C3751): a stray Clear on the next
     *    house's empty call, and "+ Another job" then Clear, both handed the
     *    first house's call to the second. */
    const ownerRun = async (strayOnEmpty) => {
      const c3 = await b.newContext({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true });
      const q = await c3.newPage();
      await q.goto(base + PAGE, { waitUntil: 'domcontentloaded' });
      await q.waitForFunction(() => document.querySelectorAll('#list li.item').length > 20, null, { timeout: 15000 });
      await q.fill('#fJob', '88 Alder Ct'); await q.dispatchEvent('#fJob', 'change');
      await q.fill('.wi-input', '12 sq dutch lap — clay'); await q.click('.wi-add'); await q.waitForTimeout(150);
      if (strayOnEmpty) { await q.click('#clear'); await q.waitForTimeout(200); }
      await q.click('.jc-chip.jc-new'); await q.waitForTimeout(250);
      await q.fill('#fJob', '1120 Birch St'); await q.dispatchEvent('#fJob', 'change'); await q.waitForTimeout(100);
      await q.click('#clear'); await q.waitForTimeout(250);
      const onB = await q.isVisible('#last');
      await q.locator('.jc-chip:not(.jc-new)').first().click(); await q.waitForTimeout(250);
      const onA = await q.isVisible('#last');
      await c3.close();
      return { onA, onB };
    };
    const r1 = await ownerRun(true), r2 = await ownerRun(false);
    ok(r1.onA && !r1.onB, `D  a stray Clear on the next house's empty call leaves the last call on its own house (A ${r1.onA}, B ${r1.onB})`);
    ok(r2.onA && !r2.onB, `D  "+ Another job" then Clear keeps the call on the house it was built on (A ${r2.onA}, B ${r2.onB})`);
    await c2.close();
  }

  notes.push('\n----- THE CALL A SIDING LEAD WOULD SEND (delivery, before the lot was typed) -----\n' + delivered + '\n-----');
  await b.close();
  if (server) server.s.close();
}

if (PROVE) prove();
else {
  staticChecks(ROOT);
  if (!STATIC_ONLY) await drive();
}

console.log(notes.join('\n'));
console.log('\n' + '='.repeat(60));
if (fails.length) { console.log(fails.join('\n')); console.log(`\n${fails.length} FAILING of ${checks}`); process.exit(1); }
console.log(`ALL ${checks} CHECKS PASS — ${PROVE ? 'prove (planted defects all red)' : (STATIC_ONLY ? 'static' : 'static + drive')} — ${BASE || ROOT}`);
