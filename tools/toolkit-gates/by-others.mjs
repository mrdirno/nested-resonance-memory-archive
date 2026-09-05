/**
 * BY OTHERS — one vendor per message, the rep on it, and no rung of it is hearsay.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `<trade>/by-others.html` is a config on shape #3. A four-lens panel (a GC
 * super · the PM at a foodservice equipment contractor, answering from the
 * RECEIVING end · an owner's rep who holds the OFCI matrix · a skeptic armed
 * with the program's own rules) scored it 7 / 7 / 7 / 5 and changed the design.
 * The corrections a later cycle could undo while believing it was tidying up
 * are asserted here:
 *
 * 1. ONE VENDOR PER MESSAGE, BY VALUE. The Close-In List's "Owner vendor / rep"
 *    is one bucket for five companies; this page's receiver is the typed vendor
 *    name. The drive puts two vendors and a nameless row on the list and
 *    requires the message to one man to carry ONLY his open rows — the other
 *    vendor's name and rows must be ABSENT from it.
 *
 * 2. THE VENDOR IS NEVER SEEDED. Zero chips under the vendor field before a man
 *    types one. A manufacturer, distributor or rep agency in a seed is
 *    impersonation with a shelf life, and the names change every job.
 *
 * 3. THE GATES ARE THE CLOSE-IN LIST'S OWN. The gate chips on the glass must
 *    equal TOOLKIT_ROUGHIN.milestones, in order, and the config must declare no
 *    gate list of its own — one list, two tools, or they drift.
 *
 * 4. NO RUNG IS HEARSAY AND THERE IS NO "NOTHING BACK". The ladder is checked
 *    against factory verbs AND against the overdue-label-in-a-status the panel
 *    killed by name; the settled rung is something he can see.
 *
 * 5. THE GATE'S DAY IS A FACT ON LINE ONE, TYPED ONCE, NEVER STORED ON A ROW.
 *    With no day typed, line one carries the rows' shared milestone; with one
 *    typed, it carries the day verbatim; the send date is NOT on line one.
 *
 * 6. THE KILLED WORDS STAY DEAD. In the SENT document: no "core drill", no "on
 *    the owner's schedule", no "promised", no money, no day count. The asks
 *    carry no "when you set it" and no "anything you still need from us" as a
 *    row (it lives in the closing). One flag, and it does not say "date".
 *
 * 7. `told` HOLDS ONE VALUE AND KEEPS NO HISTORY — overwritten, and the previous
 *    value gone from the message, the spreadsheet copy AND storage.
 *
 * Everything else is the ordinary kind: every field set and then looked for BY
 * VALUE in what the REAL Copy button put on the clipboard, the ladder tapped to
 * the top and one past, reload, Clear, and four widths with the 44px floor.
 *
 *   node tools/toolkit-gates/by-others.mjs [baseUrl]
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');
const ROOT = fileURLToPath(new URL('../../', import.meta.url));

const fails = [], notes = [];
let checks = 0;
const ok = (c, m) => { checks++; (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };

function trades() {
  return readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'by-others.html')))
    .map(d => d.name).sort();
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
function serve() {
  return new Promise(res => {
    const s = createServer((rq, rs) => {
      const rel = normalize(decodeURIComponent(rq.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      const p = join(ROOT, rel);
      if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { rs.writeHead(404); return rs.end('no'); }
      rs.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
      rs.end(readFileSync(p));
    });
    s.listen(0, '127.0.0.1', () => res({ s, port: s.address().port }));
  });
}

const STUB = () => {
  window.__copied = null;
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: { writeText: t => { window.__copied = String(t); return Promise.resolve(); } },
  });
};

/* ── THE STATIC BANS ──────────────────────────────────────────────────────── */

/* A FACTORY VERB IS A STATE HE DOES NOT HOLD — legal in asks and in told, never
   in states. Plus the one this panel killed by name. */
const FACTORY_VERB = /\b(released?|releasing|fabricat\w*|in production|produced|approved?|submitted|submittal|acknowledg\w*|shipped|shipping|in transit|dispatched|booked for|nothing back|no answer|waiting)\b/i;

/* NAMING A REAL HOUSE ON A DOCUMENT HE SENDS. The long pole's list, plus the
   houses an owner's vendor actually is — kitchen, refrigeration, EVSE, signage,
   furniture. A real, checkable ban rather than a capitalisation heuristic. */
const REAL_HOUSE = /\b(square ?d|schneider|eaton|siemens|abb|general electric|\bge\b|generac|kohler|cummins|acuity|lithonia|lutron|trane|carrier|york|daikin|lennox|greenheck|mitsubishi|zurn|watts|sloan|moen|graybar|rexel|wesco|ferguson|grainger|hobart|traulsen|true (refrigeration|manufacturing)|vulcan|captive.?aire|kolpak|amerikooler|nor-?lake|manitowoc|hoshizaki|scotsman|rational|middleby|blodgett|welbilt|ali group|chargepoint|blink|evgo|daktronics|watchfire|steelcase|herman ?miller|haworth|knoll|hill-?rom|stryker|philips|siemens healthineers|ge healthcare)\b/i;

/* MONEY, CLAIMS AND ARITHMETIC — the three things that turn an ask into the one
   document that costs the user the relationship it was written to protect. */
const CLAIM_WORDS = [
  [/\bpromis\w*/i, 'the word "promised" — what he was LAST TOLD, never what was promised'],
  [/\b(backcharge|liquidated|\bLDs?\b|delay claim|claim against|damages|who eats)\b/i, 'claim language on a page that must never read as a delay exhibit'],
  [/\b(quote[ds]?|pricing|unit price|invoice|\$\d)/i, 'money — the PM\'s lane, and this page has no business in it'],
  [/\b(overdue|past due|days late|late by|elapsed|running late)\b/i, 'day arithmetic — the page never counts a day, ever'],
  [/\b\d+\s*(week|wk)s?\s*(lead|ARO)/i, 'a lead time we do not have and cannot have'],
  [/\b\d+\s*(lb|lbs|kg|ton)s?\b/i, 'a weight is a spec we do not hold'],
  [/\b(furnish(ed|es)?[- ]?(vs|versus|or)[- ]?install|yours to furnish|OFCI|OFOI)\b/i, 'a furnish-vs-install call — the subcontract, a PM\'s lane'],
];
/* Words the panel killed from the SENT document. Legal in the page's own UI copy
   to the super (his vocabulary) — never in what the vendor or the rep reads. */
const DOC_BANS = [
  [/core[- ]?drill/i, '"core drill" — the two receiving lenses: it gets forwarded as "your GC is threatening me" and lands on the wrong man'],
  [/owner.s schedule/i, '"on the owner\'s schedule, not mine" — who-eats-it with the dollar sign filed off'],
  [/moves? the date|delaying/i, 'schedule-impact language printed to an outside vendor — the first sentence of a delay claim'],
];

function configOf(trade) {
  const src = readFileSync(join(ROOT, trade, 'items.js'), 'utf8');
  const i = src.indexOf('window.TOOLKIT_BYOTHERS');
  if (i < 0) return null;
  const j = src.indexOf('\n};', i);
  return src.slice(i, j < 0 ? src.length : j + 3);
}
const arrOf = (cfg, k) => {
  const m = cfg.match(new RegExp('\\n\\s*' + k + '\\s*:\\s*\\[([\\s\\S]*?)\\]'));
  if (!m) return null;
  return [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(x => x[1].replace(/\\"/g, '"'));
};
const strOf = (cfg, k) => {
  const m = cfg.match(new RegExp('\\n\\s*' + k + '\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"'));
  return m ? m[1] : null;
};

function staticChecks(trade) {
  const cfg = configOf(trade);
  ok(!!cfg, `${trade}: items.js declares TOOLKIT_BYOTHERS`);
  if (!cfg) return;

  const states = arrOf(cfg, 'states'), asks = arrOf(cfg, 'asks'), items = arrOf(cfg, 'items'), flags = arrOf(cfg, 'flags');
  const short = arrOf(cfg, 'askShort'), lines = arrOf(cfg, 'askLines');
  ok(Array.isArray(states) && states.length >= 3, `${trade}: states[] has a real ladder (${states ? states.length : 0} rungs)`);
  ok(Array.isArray(asks) && asks.length >= 4, `${trade}: asks[] has a real braid to break (${asks ? asks.length : 0} questions)`);
  ok(Array.isArray(items) && items.length >= 12, `${trade}: items[] seeds the jog (${items ? items.length : 0})`);
  ok(Array.isArray(flags) && flags.length === 1, `${trade}: ONE flag, not a spreadsheet (${flags ? flags.length : 0})`);
  ok(short && lines && asks && short.length === asks.length && lines.length === asks.length,
    `${trade}: askShort[] and askLines[] are parallel to asks[] (${short && short.length}/${lines && lines.length}/${asks && asks.length})`);

  (states || []).forEach(s => ok(!FACTORY_VERB.test(s),
    `${trade}: ladder rung "${s}" is his own act or his own eyes — no factory verb, no overdue label`));
  if (states && states.length) ok(/\b(in|here|on site|in hand|saw it)\b/i.test(states[states.length - 1]),
    `${trade}: the settled rung "${states[states.length - 1]}" is something he can SEE`);

  (flags || []).forEach(f => ok(!/date|delay|schedule/i.test(f), `${trade}: the flag "${f}" carries no schedule-impact language`));

  // THE KILLED ASKS STAY DEAD. "When you set it" has no close-in gate and turns
  // the page into a delivery chase (the long pole in a hat — GC gets never);
  // "anything you still need from us" is open-ended as a row and lives in the
  // closing instead.
  (asks || []).forEach(a => ok(!/\b(set it|need the room|room clear|still need from us|need from us)\b/i.test(a),
    `${trade}: ask "${a.slice(0, 48)}" is not one the panel killed`));
  // THE FIRST ASK IS THE CHEAPEST — one line back in an hour.
  if (asks && asks.length) ok(/\byours\b/i.test(asks[0]), `${trade}: the first ask is "which of these are yours" — the answer the receiving desk gives most, one line, an hour ("${asks[0]}")`);
  // THE DOCUMENT ASK OUTRANKS THE PARAGRAPH ASK — the sheet comes before "where it lands and what it needs".
  if (asks && asks.length >= 2) {
    const iSheet = asks.findIndex(a => /sheet/i.test(a)), iLands = asks.findIndex(a => /where it lands/i.test(a));
    ok(iSheet >= 0 && (iLands < 0 || iSheet < iLands), `${trade}: "send me the sheet" is asked before "tell me where it lands" (${iSheet} < ${iLands})`);
  }
  // AND THE CLOSING CARRIES THE HALF NOBODY WRITES.
  const closing = strOf(cfg, 'closing') || '';
  ok(/need from the building|still need from us|need from us/i.test(closing), `${trade}: "anything you need from us" lives in the closing, not as a row ask`);
  ok(/isn't yours|not yours/i.test(closing) && /whose/i.test(closing), `${trade}: the closing carries the receiving desk's line — if it isn't yours, tell me whose`);
  ok(/sheet/i.test(closing) && /rev/i.test(closing), `${trade}: the closing asks for the sheet and the rev`);
  ok(/\{off\}/.test(closing), `${trade}: the closing names the set he is building off ({off})`);

  // NO GATE LIST OF ITS OWN — the gates are the Close-In List's.
  ok(!arrOf(cfg, 'gates') && !arrOf(cfg, 'milestones'), `${trade}: config declares no gate list of its own — TOOLKIT_ROUGHIN.milestones is the one list`);
  const page = readFileSync(join(ROOT, trade, 'by-others.html'), 'utf8');
  ok(/TOOLKIT_ROUGHIN/.test(page) && /milestones/.test(page), `${trade}: the page reads its gates from TOOLKIT_ROUGHIN.milestones`);

  // NO-GATE SEEDS AND FURNISH-FIGHT SEEDS STAY OUT. A super can type them.
  const all = [...(states || []), ...(asks || []), ...(items || []), ...(flags || [])];
  (items || []).forEach(s => ok(!/\b(copier|vending|med[- ]?gas|access control|card reader|door contact)\b/i.test(s),
    `${trade}: seed "${s.slice(0, 44)}" has a gate and pre-decides no furnish-vs-install fight`));
  all.forEach(s => ok(!REAL_HOUSE.test(s), `${trade}: seed "${s.slice(0, 44)}" names no real house`));

  // The claim words are checked over the whole authored config, prose included.
  CLAIM_WORDS.forEach(([re, why]) => {
    const m = cfg.match(re);
    ok(!m, `${trade}: config carries no ${why}${m ? ` — found "${m[0]}"` : ''}`);
  });
  // The document-only bans are checked over what the DOCUMENT is built from.
  ['closing', 'closingRep', 'docBoundary', 'docRepNoName', 'docEveryLede', 'docAllLede'].forEach(k => {
    const s = strOf(cfg, k) || '';
    DOC_BANS.forEach(([re, why]) => ok(!re.test(s), `${trade}: ${k} carries no ${why}`));
  });
  (lines || []).forEach(l => DOC_BANS.forEach(([re, why]) => ok(!re.test(l), `${trade}: askLine "${l.slice(0, 30)}…" carries no ${why}`)));
}

/* ── THE DRIVE ─────────────────────────────────────────────────────────────── */
async function drive(browser, base, trade, width = 390) {
  const ctx = await browser.newContext({ viewport: { width, height: 860 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(STUB);
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(base + trade + '/by-others.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  return { p, ctx, errs };
}

const setK = (p, k, v) => p.evaluate(([k, v]) => {
  const el = document.querySelector(`#bar [data-k="${k}"]`);
  el.value = v; el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true }));
}, [k, v]);
const setLearn = async (p, k, v) => {
  await p.fill(`#bar [data-learn="${k}"]`, v);
  await p.evaluate(k => document.querySelector(`#bar [data-learn="${k}"]`).dispatchEvent(new Event('blur')), k);
};
const chip = async (p, k, v) => {
  const cur = await p.evaluate(k => document.querySelector(`#bar [data-k="${k}"]`).value, k);
  if (cur === v) return;
  await p.click(`#bar [data-chips="${k}"] .rl-chip[data-v="${v}"]`);
};

async function addRow(p, vals) {
  await setLearn(p, 'item', vals.item);
  if (vals.vendor != null) { if (vals.vendor === '') await setK(p, 'vendor', ''); else await setLearn(p, 'vendor', vals.vendor); }
  if (vals.where != null) await setLearn(p, 'where', vals.where);
  if (vals.tag != null) await setK(p, 'tag', vals.tag);
  if (vals.ask != null) await setK(p, 'ask', vals.ask);
  if (vals.gate != null) await chip(p, 'gate', vals.gate);
  if (vals.state != null) await setK(p, 'state', vals.state);
  if (vals.told != null) await setK(p, 'told', vals.told);
  await p.click('#rlAdd');
  await p.waitForTimeout(120);
}

const copied = async p => { await p.click('#copyBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };
const copiedTsv = async p => { await p.click('#tsvBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };
const pickTo = async (p, value) => { await p.selectOption('#selTo', { value }); await p.waitForTimeout(150); };
const line1 = doc => doc.split('\n')[0];

async function driveTrade(browser, base, trade) {
  const { p, ctx, errs } = await drive(browser, base, trade);

  const asks = await p.$$eval('#bar [data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
  const states = await p.$$eval('#bar [data-k="state"] option', o => o.map(x => x.value).filter(Boolean));
  const gates = await p.$$eval('#bar [data-chips="gate"] .rl-chip', o => o.map(x => x.getAttribute('data-v')));
  const miles = await p.evaluate(() => (window.TOOLKIT_ROUGHIN.milestones || []).map(m => m.label));
  const short = await p.evaluate(() => (window.TOOLKIT_BYOTHERS.askShort || []));
  const today = await p.evaluate(() => (window.Toolkit && Toolkit.todayStr) ? Toolkit.todayStr() : new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }));
  ok(asks.length >= 4 && states.length >= 3, `${trade}: the page's own controls carry the vocabulary (${asks.length} asks / ${states.length} rungs)`);
  ok(gates.length >= 5 && JSON.stringify(gates) === JSON.stringify(miles),
    `${trade}: the gate chips ARE the Close-In List's milestones, in order (${gates.length})`);
  const vendorSeed = await p.$$eval('#bar [data-chips="vendor"] .rl-chip', o => o.length);
  ok(vendorSeed === 0, `${trade}: the vendor field is never seeded — ${vendorSeed} chips before a man types one`);

  // The header rides on every message.
  await p.fill('#hJob', 'Rosewood ES');
  await p.fill('#hOff', 'P-101 rev 4');
  await p.fill('#hFrom', 'Ken, site super');
  await p.fill('#hTel', '555-0134');
  await p.fill('#hRep', 'Priya, owner rep');
  await p.waitForTimeout(120);

  // TWO VENDORS, ONE NAMELESS ROW, ONE ROW ALREADY IN — the boundary, built on purpose.
  await addRow(p, { item: 'GATE-WALKIN', tag: 'K-4', vendor: 'the kitchen guy, Dave', where: 'Kitchen 114', ask: asks[1], gate: gates[1], state: states[0], told: 'Dave, 8/2 — FS-3 rev 2, sent in April' });
  await addRow(p, { item: 'GATE-HOOD', tag: 'K-12', ask: asks[1], gate: gates[1] });                 // vendor, where and gate carry
  await addRow(p, { item: 'GATE-DONE', tag: 'K-31', ask: asks[1], gate: gates[1], state: states[states.length - 1] });
  await addRow(p, { item: 'GATE-SIGN', vendor: 'the sign outfit, Lou', where: 'Site', ask: asks[2], gate: gates[0], state: '' });
  await addRow(p, { item: 'GATE-EVSE', vendor: '', where: 'North lot', ask: asks[2], gate: gates[0], state: '' });
  ok((await p.$$('#list .rl-row')).length === 5, `${trade}: five rows on the glass`);

  const noname = await p.$eval('#noname', e => ({ hidden: e.hidden, t: e.textContent }));
  ok(!noname.hidden && /1 piece with no name/i.test(noname.t), `${trade}: the nameless piece is named on the glass, where he can fix it`);

  /* ── ONE VENDOR, ONE MESSAGE ─────────────────────────────────────────────── */
  const toVals = await p.$$eval('#selTo option', o => o.map(x => x.value));
  ok(toVals.includes('v:the kitchen guy, Dave') && toVals.includes('v:the sign outfit, Lou') && toVals.includes('rep') && toVals.includes('all'),
    `${trade}: the To-select offers each named vendor, the rep, and his own record (${toVals.length} options)`);
  await pickTo(p, 'v:the kitchen guy, Dave');
  const askVal = await p.inputValue('#selAsk');
  ok(askVal === 'a:' + asks[1], `${trade}: with ONE question on his rows it is picked — it is the content, not a choice ("${askVal}")`);
  let doc = await copied(p);
  ok(/^Rosewood ES — K-4, K-12: /.test(line1(doc)), `${trade}: line 1 names the job, then the pieces BY TAG ("${line1(doc)}")`);
  ok(line1(doc).includes(short[1]), `${trade}: line 1 carries the question, short — the lock-screen line`);
  ok(line1(doc).endsWith(gates[1].toLowerCase()), `${trade}: with no day typed, line 1 ends on the rows' shared gate ("${line1(doc)}")`);
  ok(!line1(doc).includes(today), `${trade}: and NO send date on line 1 — the sender lens killed "Sep 5 hanging off the subject with no noun"`);
  for (const v of ['To: the kitchen guy, Dave', 'cc: Priya, owner rep', 'From: Ken, site super · 555-0134', 'Building off: P-101 rev 4',
                   'GATE-WALKIN (K-4)', 'GATE-HOOD (K-12)', 'Kitchen 114', 'last I heard: Dave, 8/2 — FS-3 rev 2, sent in April', 'On 2 pieces:']) {
    ok(doc.includes(v), `${trade}: "${v}" reaches the message`);
  }
  for (const v of ['GATE-SIGN', 'GATE-EVSE', 'GATE-DONE', 'the sign outfit', 'North lot']) {
    ok(!doc.includes(v), `${trade}: "${v}" is ABSENT from Dave's message — another man's piece, a nameless piece, and a piece already in`);
  }
  ok(!doc.includes('owner rep — owner'), `${trade}: the rep's tag is not printed twice when his own words already carry it`);
  ok(!/\n[^\n]*\basked\b/i.test(doc.split('\n').filter(l => /^GATE-/.test(l)).join('\n')), `${trade}: the rung is his record — "asked" is on no row line in a message to the vendor himself`);
  /* A BARE NAME GETS THE TAG, so the vendor knows who is on the thread. */
  await p.fill('#hRep', 'Priya'); await p.waitForTimeout(150);
  doc = await copied(p);
  ok(doc.includes("cc: Priya — owner's rep"), `${trade}: a bare rep name gets " — owner's rep" appended ("${(doc.match(/cc: [^\n]*/) || [''])[0]}")`);
  await p.fill('#hRep', 'Priya, owner rep'); await p.waitForTimeout(150);
  doc = await copied(p);
  ok(doc.split(asks[1]).length - 1 <= 1, `${trade}: the question prints once, never per row (${doc.split(asks[1]).length - 1})`);
  ok(doc.includes('sheet and the rev') && doc.includes("isn't yours, tell me whose") && doc.includes("I'm building off P-101 rev 4"),
    `${trade}: the closing is the receiving desk's own two lines, with his set named`);
  ok(/isn't an RFI or a change order/.test(doc) && /whose scope/.test(doc), `${trade}: the message says out loud what it is not`);
  CLAIM_WORDS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the message carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  DOC_BANS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the message carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });

  /* THE GATE'S DAY — typed once, a fact on line one, never on a row. */
  await p.fill('#hDay', 'slab pours 9/12');
  await p.waitForTimeout(150);
  doc = await copied(p);
  ok(line1(doc).endsWith('slab pours 9/12'), `${trade}: the day rides on line 1 verbatim ("${line1(doc)}")`);
  ok(!line1(doc).includes(gates[1].toLowerCase()), `${trade}: and replaces the bare milestone there`);
  const rowLines = doc.split('\n').filter(l => /^GATE-/.test(l));
  ok(rowLines.length === 2 && rowLines.every(l => !l.includes('9/12')), `${trade}: the day is on NO row line — it is a fact about the gate, not a field`);

  /* SWITCHING THE VENDOR SWITCHES THE WHOLE MESSAGE. */
  await pickTo(p, 'v:the sign outfit, Lou');
  doc = await copied(p);
  ok(doc.includes('To: the sign outfit, Lou') && doc.includes('GATE-SIGN') && !doc.includes('GATE-WALKIN') && !doc.includes('GATE-HOOD') && !doc.includes('GATE-EVSE') && !doc.includes('kitchen guy'),
    `${trade}: Lou's message carries only Lou's row — and not the kitchen guy's name`);
  ok(line1(doc).startsWith('Rosewood ES — 1 piece: '), `${trade}: with no tag on the row, line 1 counts pieces instead ("${line1(doc)}")`);

  /* ── THE ROLL-UP TO THE REP ──────────────────────────────────────────────── */
  await pickTo(p, 'rep');
  doc = await copied(p);
  ok(line1(doc).includes('what your vendors still owe me') && line1(doc).endsWith('slab pours 9/12'), `${trade}: the roll-up's line 1 ("${line1(doc)}")`);
  ok(doc.includes('To: Priya, owner rep') && !doc.includes('cc:'), `${trade}: the roll-up is TO the rep, not cc'd`);
  for (const v of ['GATE-WALKIN', 'GATE-HOOD', 'GATE-SIGN', 'GATE-EVSE']) ok(doc.includes(v), `${trade}: "${v}" is in the roll-up — everything still open`);
  ok(/^GATE-WALKIN[^\n]*\basked\b/im.test(doc), `${trade}: and the roll-up DOES carry the rung — the rep sees which ones he asked direct`);
  ok(!doc.includes('GATE-DONE'), `${trade}: the piece already in is NOT in the roll-up`);
  ok(/THE KITCHEN GUY, DAVE — 2 ROWS/.test(doc) && /THE SIGN OUTFIT, LOU — 1 ROW/.test(doc), `${trade}: the roll-up reads by vendor`);
  const nsBlock = doc.split(/NOT SET — 1 ROW/)[1] || '';
  ok(nsBlock.split('\n')[1] && nsBlock.split('\n')[1].startsWith('GATE-EVSE'), `${trade}: the nameless piece sits under NOT SET, its own heading`);
  ok(/the name is the whole ask/.test(doc), `${trade}: and the roll-up says the name is the whole ask`);
  ok((await p.$eval('#segGroup button.on', e => e.getAttribute('data-g'))) === 'vendor', `${trade}: the list on screen follows the roll-up's grouping — the preview is what the button copies`);
  ok(await p.$eval('#askRow', e => e.hidden), `${trade}: the question row hides on the roll-up — it asks one thing of the rep`);
  DOC_BANS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the roll-up carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });

  /* ── HIS OWN RECORD ──────────────────────────────────────────────────────── */
  await pickTo(p, 'all');
  doc = await copied(p);
  ok(line1(doc).includes(today), `${trade}: his own record carries today's date on line 1 — it is his, not a message`);
  ok(['GATE-WALKIN', 'GATE-HOOD', 'GATE-SIGN', 'GATE-EVSE', 'GATE-DONE'].every(v => doc.includes(v)), `${trade}: every row, including the one already in`);

  /* ── `told` KEEPS NO HISTORY ─────────────────────────────────────────────── */
  await p.click('#list .rl-row .rl-edit');
  await p.waitForTimeout(120);
  await setK(p, 'told', 'Dana, 8/9 — the second thing they told me');
  await p.click('#rlAdd');
  await p.waitForTimeout(150);
  await pickTo(p, 'all');
  doc = await copied(p);
  const tsv = await copiedTsv(p);
  const store = await p.evaluate(() => JSON.stringify(window.localStorage));
  ok(doc.includes('Dana, 8/9 — the second thing they told me'), `${trade}: the latest thing he was told rides on the line`);
  ok(!doc.includes('Dave, 8/2'), `${trade}: the PREVIOUS one is gone from the message — no history to paste back at him`);
  ok(!tsv.includes('Dave, 8/2'), `${trade}: and gone from the spreadsheet copy`);
  ok(!store.includes('Dave, 8/2'), `${trade}: and gone from storage — the field holds one value, so it can never become an exhibit`);
  ok(!tsv.includes('9/12'), `${trade}: the gate's day is on no row in the spreadsheet either`);

  /* ── THE LADDER IS TAP-TO-ADVANCE AND DOES NOT WRAP ─────────────────────── */
  const rowSel = '#list .rl-row';
  const before = await p.$eval(rowSel + ' .rl-st', e => e.getAttribute('data-st'));
  await p.click(rowSel + ' .rl-tap');
  await p.waitForTimeout(120);
  const after = await p.$eval(rowSel + ' .rl-st', e => e.getAttribute('data-st'));
  ok(before !== after, `${trade}: one tap moves a row up the ladder (${before || 'blank'} → ${after})`);
  for (let i = 0; i < states.length + 2; i++) { await p.click(rowSel + ' .rl-tap'); await p.waitForTimeout(60); }
  const top = await p.$eval(rowSel + ' .rl-st', e => e.getAttribute('data-st'));
  ok(top === states[states.length - 1], `${trade}: the ladder stops at "${states[states.length - 1]}" and never wraps back to blank`);

  /* ── IT SURVIVES A RELOAD, AND CLEAR TAKES EVERYTHING ──────────────────── */
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  ok((await p.$$('#list .rl-row')).length === 5, `${trade}: the list survives a reload`);
  ok((await p.inputValue('#hJob')) === 'Rosewood ES' && (await p.inputValue('#hRep')) === 'Priya, owner rep' && (await p.inputValue('#hDay')) === 'slab pours 9/12',
    `${trade}: and so do the header, the rep and the gate's day`);

  await p.click('#clearBtn'); await p.waitForTimeout(80);
  await p.click('#clearBtn'); await p.waitForTimeout(200);
  ok((await p.$$('#list .rl-row')).length === 0, `${trade}: Clear takes the list`);
  ok((await p.inputValue('#hJob')) === '' && (await p.inputValue('#hRep')) === '' && (await p.inputValue('#hDay')) === '' && (await p.inputValue('#hOff')) === '',
    `${trade}: and the header, the rep and the day with it — a different job must never inherit the last one's rep`);
  ok((await p.inputValue('#selTo')) === '', `${trade}: and the receiver resets, so the next job does not send the last job's vendor`);

  ok(errs.length === 0, `${trade}: no page errors${errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''}`);
  await ctx.close();
}

/* ── THE WIDTHS ─────────────────────────────────────────────────────────────── */
async function widths(browser, base, trade) {
  for (const w of [320, 360, 390, 430]) {
    const { p, ctx } = await drive(browser, base, trade, w);
    const asks = await p.$$eval('#bar [data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
    const gates = await p.$$eval('#bar [data-chips="gate"] .rl-chip', o => o.map(x => x.getAttribute('data-v')));
    await addRow(p, { item: 'A very long piece indeed — the walk-in cooler and freezer with the floor depression', tag: 'OF-14', vendor: 'the refrigeration outfit out of the valley, Marisol', where: 'Kitchen 114', ask: asks[1], gate: gates[1] });
    await p.waitForTimeout(150);
    await pickTo(p, 'v:the refrigeration outfit out of the valley, Marisol');
    const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    ok(over <= 0, `${trade} @${w}: no horizontal scroll (${over}px)`);
    const small = await p.$$eval('#segGroup button, #selTo, #selAsk, #hDay, #copyBtn, #tsvBtn, #rlAdd, #list .rl-tap, #list .rl-edit',
      els => els.filter(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.height < 44; }).map(e => (e.id || e.className) + ':' + Math.round(e.getBoundingClientRect().height)));
    ok(small.length === 0, `${trade} @${w}: every control clears the 44px floor${small.length ? ' — ' + small.join(', ') : ''}`);
    await ctx.close();
  }
}

/* ── RUN ────────────────────────────────────────────────────────────────── */
const argBase = process.argv[2];
const list = trades();
if (!list.length) { console.error('FAIL: no trade ships by-others.html'); process.exit(1); }
list.forEach(staticChecks);

let server = null, base = argBase;
if (!base) { server = await serve(); base = `http://127.0.0.1:${server.port}/`; }
if (!base.endsWith('/')) base += '/';
const browser = await chromium.launch();
try {
  for (const t of list) { await driveTrade(browser, base, t); await widths(browser, base, t); }
} finally {
  await browser.close();
  if (server) server.s.close();
}

notes.forEach(n => console.log(n));
fails.forEach(f => console.log(f));
console.log(`\n${fails.length ? 'FAIL' : 'PASS'}: by-others — ${checks} checks over ${list.length} trade(s) (${list.join(', ')}), ${fails.length} failing, base ${base}`);
process.exit(fails.length ? 1 : 0);
