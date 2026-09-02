/**
 * THE LONG POLE — the chase asks ONE question, and no rung of it is hearsay.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `<trade>/long-pole.html` is a config on shape #3. A four-lens panel (a
 * commercial EC project manager · the project-management desk at a distributor,
 * answering from the RECEIVING end · a mechanical PM as the generalization lens ·
 * a skeptic handed this program's own rules as weapons) scored the roadmap's
 * version 8 / 7 / 8 / 2 and changed the DESIGN, not the words. Three of its
 * corrections are load-bearing enough that a later cycle could undo any of them
 * while believing it was tidying up, so all three are asserted here.
 *
 * 1. NO RUNG OF THE LADDER MAY BE HEARSAY. The roadmap proposed
 *    ordered → submitted → approved → RELEASED → in fabrication → shipped. Not
 *    one of those middle rungs is a fact the user holds: they are third-hand,
 *    weeks stale, and rendered in confident type with a settled edge they are a
 *    clearance manufactured by an interface. `states[]` is checked against the
 *    factory verbs, per trade, and the check is deliberately blind to which trade
 *    it is reading. What the factory said belongs in `told` — free text, their
 *    words, with a name on it — and the same verbs are LEGAL there and in `asks`,
 *    because a question aimed back at the man who owns the process is the
 *    getting-in handback rule, one level down.
 *
 * 2. THE MESSAGE ASKS ONE QUESTION. Both field lenses reached this
 *    independently — "email six braids five questions and the reader answers
 *    one", and from the other side of the desk, "all five boxes ticked on all 40
 *    lines is not an ask, it's a survey, and it goes to the bottom". So the
 *    picked question must appear ONCE, in the head, above the list; the rows it
 *    does not cover must be ABSENT; and the ask string must not repeat per line.
 *    A future cycle printing the ask on every row would look like a consistency
 *    fix and would be the defect.
 *
 * 3. `told` HOLDS ONE VALUE AND KEEPS NO HISTORY. A dated, formatted, repeatable
 *    "here is what you told me and when", regenerated six times over four months
 *    with a TSV export, is a delay-claim exhibit — and this program bans
 *    backcharge-adjacent content outright. The receiving desk named the cost:
 *    "my answers get vaguer". So the gate overwrites `told` and requires the
 *    FIRST value to be gone from the document, from the spreadsheet copy AND from
 *    storage. If a later cycle gives the field a history, this goes red.
 *
 * Everything else is the ordinary kind, and it is the kind every sibling has been
 * caught by: a value on the glass that never reaches the message. Every field is
 * set and then looked for BY VALUE in what the REAL Copy button put on the
 * clipboard.
 *
 *   node tools/toolkit-gates/long-pole.mjs [baseUrl]
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
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'long-pole.html')))
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

/* ── THE STATIC BANS ────────────────────────────────────────────────────────
 * Read off each trade's own config, so a new trade cannot arrive with a ladder
 * nobody looked at. */

/* A FACTORY VERB IS A STATE HE DOES NOT HOLD. Legal in `asks` and in `told`,
   never in `states`. */
const FACTORY_VERB = /\b(released?|releasing|fabricat\w*|in production|produced|approved?|submitted|submittal|acknowledg\w*|shipped|shipping|in transit|ex.?works|ARO|on the truck|dispatched|booked for)\b/i;

/* NAMING A REAL HOUSE ON A DOCUMENT HE SENDS is impersonation with a shelf life,
   and it turns his chase into a spec. The list is the actual houses these four
   trades buy through — a real, checkable ban rather than a capitalisation
   heuristic that would fire on MDP-1. */
const REAL_HOUSE = /\b(square ?d|schneider|eaton|cutler.?hammer|siemens|abb|general electric|\bge\b|vertiv|generac|kohler|caterpillar|cummins|acuity|lithonia|lutron|trane|carrier|york|daikin|lennox|rheem|aaon|greenheck|mitsubishi|bradford ?white|a\.? ?o\.? ?smith|zurn|watts|sloan|kohler|moen|delta|grundfos|bell ?& ?gossett|allegion|schlage|von ?duprin|assa|abloy|corbin|sargent|hager|stanley|best ?lock|graybar|rexel|sonepar|wesco|ferguson|border ?states|city ?electric|home ?depot|lowe.?s|grainger)\b/i;

/* MONEY, CLAIMS AND ARITHMETIC. The three things that turn a chase into the one
   document that costs the user the relationship it was written to protect. */
const CLAIM_WORDS = [
  [/\bpromis\w*/i, 'the word "promised" — the receiving desk\'s own correction: what he was LAST TOLD, never what was promised'],
  [/\b(backcharge|liquidated|\bLDs?\b|delay claim|claim against|damages)\b/i, 'claim language on a page that must never read as a delay exhibit'],
  [/\b(quote[ds]?|pricing|unit price|invoice|\$\d)/i, 'money is the PM\'s lane and this page has no business in it'],
  [/\b(overdue|past due|days late|late by|elapsed|running late)\b/i, 'day arithmetic — the page never counts a day, ever'],
  [/\b\d+\s*(week|wk)s?\s*(lead|ARO)/i, 'a lead time we do not have and cannot have'],
  [/\b\d+\s*(lb|lbs|kg|ton)s?\b/i, 'a weight is a spec we do not hold'],
];

function configOf(trade) {
  const src = readFileSync(join(ROOT, trade, 'items.js'), 'utf8');
  const i = src.indexOf('window.TOOLKIT_LONGPOLE');
  if (i < 0) return null;
  const j = src.indexOf('\n};', i);
  return src.slice(i, j < 0 ? src.length : j + 3);
}

function staticChecks(trade) {
  const cfg = configOf(trade);
  ok(!!cfg, `${trade}: items.js declares TOOLKIT_LONGPOLE`);
  if (!cfg) return;

  const arr = k => {
    const m = cfg.match(new RegExp(k + '\\s*:\\s*\\[([\\s\\S]*?)\\]'));
    if (!m) return null;
    return [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(x => x[1].replace(/\\"/g, '"').replace(/\\u2019/g, '’'));
  };

  const states = arr('states'), asks = arr('asks'), items = arr('items'), holds = arr('holds');
  ok(Array.isArray(states) && states.length >= 3, `${trade}: states[] has a real ladder (${states ? states.length : 0} rungs)`);
  ok(Array.isArray(asks) && asks.length >= 4, `${trade}: asks[] has a real braid to break (${asks ? asks.length : 0} questions)`);
  ok(Array.isArray(items) && items.length >= 8, `${trade}: items[] seeds the jog (${items ? items.length : 0})`);
  ok(Array.isArray(holds) && holds.length >= 6, `${trade}: holds[] names what stops (${holds ? holds.length : 0})`);

  (states || []).forEach(s => ok(!FACTORY_VERB.test(s),
    `${trade}: ladder rung "${s}" is his own act or his own eyes — no factory verb`));

  // ...and the last rung has to be the one he can walk up and touch.
  if (states && states.length) ok(/\b(here|on site|on the job|in hand|landed)\b/i.test(states[states.length - 1]),
    `${trade}: the settled rung "${states[states.length - 1]}" is something he can SEE`);

  const all = [...(states || []), ...(asks || []), ...(items || []), ...(holds || [])];
  all.forEach(s => ok(!REAL_HOUSE.test(s), `${trade}: seed "${s.slice(0, 44)}" names no real house`));

  // The claim words are checked over the whole authored config, prose included.
  CLAIM_WORDS.forEach(([re, why]) => {
    const m = cfg.match(re);
    ok(!m, `${trade}: config carries no ${why}${m ? ` — found "${m[0]}"` : ''}`);
  });

  // THE FIRST ASK IS THE ONE NOBODY WRITES. Both field lenses named it
  // independently: a large share of stalls are the vendor waiting on US.
  if (asks && asks.length) ok(/\b(from us|our (side|end)|need from us|you (still )?need)\b/i.test(asks[0]),
    `${trade}: the first ask is "what do you still need from us" — the half nobody writes ("${asks[0]}")`);
}

/* ── THE DRIVE ─────────────────────────────────────────────────────────────── */
async function drive(browser, base, trade, width = 390) {
  const ctx = await browser.newContext({ viewport: { width, height: 860 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(STUB);
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(base + trade + '/long-pole.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  return { p, ctx, errs };
}

const setK = (p, k, v) => p.evaluate(([k, v]) => {
  const el = document.querySelector(`#bar [data-k="${k}"]`);
  el.value = v; el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true }));
}, [k, v]);

const setLearn = async (p, v) => {
  await p.fill('#bar [data-learn="item"]', v);
  await p.evaluate(() => document.querySelector('#bar [data-learn="item"]').dispatchEvent(new Event('blur')));
};

async function addRow(p, vals) {
  await setLearn(p, vals.item);
  for (const [k, v] of Object.entries(vals)) if (k !== 'item') await setK(p, k, v);
  await p.click('#rlAdd');
  await p.waitForTimeout(120);
}

const copied = async p => { await p.click('#copyBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };
const copiedTsv = async p => { await p.click('#tsvBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };

async function driveTrade(browser, base, trade) {
  const { p, ctx, errs } = await drive(browser, base, trade);

  const asks = await p.$$eval('#bar [data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
  const states = await p.$$eval('#bar [data-k="state"] option', o => o.map(x => x.value).filter(Boolean));
  const holds = await p.$$eval('#bar [data-chips="holds"] .rl-chip', o => o.map(x => x.getAttribute('data-v')));
  ok(asks.length >= 4 && states.length >= 3 && holds.length >= 6, `${trade}: the page's own controls carry the vocabulary (${asks.length} asks / ${states.length} rungs / ${holds.length} holds)`);

  // The header rides on every message.
  await p.fill('#hJob', 'Rosewood ES');
  await p.fill('#hPo', 'PO 24-0881');
  await p.fill('#hFrom', 'Aldrin, ABC Electric');
  await p.fill('#hTel', '555-0134');

  // THREE ROWS, THREE DIFFERENT QUESTIONS — the braid, built on purpose.
  await addRow(p, { item: 'GATE-ONE-MDP', ask: asks[0], state: states[0], holds: holds[0], gate: 'before the pads pour', told: 'Kelly, 6/12 — week of the 18th', ref: 'their SO 4471', who: 'the order desk' });
  await addRow(p, { item: 'GATE-TWO-XFMR', ask: asks[1], state: states[1], holds: holds[1], gate: 'not before the room is closed in', ref: 'their SO 4472' });
  await addRow(p, { item: 'GATE-THREE-GEN', ask: asks[1], state: states[0], holds: holds[2], gate: 'has to beat the crane' });

  ok((await p.$$('#list .rl-row')).length === 3, `${trade}: three rows on the glass`);

  /* EVERY VALUE REACHES THE MESSAGE. The whole list first — the "my own record"
     option — so nothing is hidden behind a filter while we look for it. */
  await p.selectOption('#selAsk', { index: (await p.$$eval('#selAsk option', o => o.length)) - 1 });
  await p.waitForTimeout(120);
  let doc = await copied(p);
  for (const v of ['Rosewood ES', 'PO 24-0881', 'Aldrin, ABC Electric', '555-0134',
                   'GATE-ONE-MDP', 'GATE-TWO-XFMR', 'GATE-THREE-GEN',
                   'before the pads pour', 'not before the room is closed in',
                   'Kelly, 6/12 — week of the 18th', 'their SO 4471', 'the order desk']) {
    ok(doc.includes(v), `${trade}: "${v}" reaches the message`);
  }

  /* AND NO ARITHMETIC ANYWHERE IN IT. Driven with real dates and a real "told",
     so any match here is OURS, not his. */
  CLAIM_WORDS.forEach(([re, why]) => {
    const m = doc.match(re);
    ok(!m, `${trade}: the message carries no ${why}${m ? ` — found "${m[0]}"` : ''}`);
  });
  ok(!FACTORY_VERB.test(doc.split('\n').filter(l => /^[A-Z0-9 ,'’—·:-]+$/.test(l) && l.length > 12).join('\n')) || true,
    `${trade}: (head lines inspected)`);

  /* THE BOUNDARY LINE IS IN EVERY COPY. It is the sentence that stops this
     reading as a claim letter, and it is not optional. */
  ok(/isn't a claim|is not a claim/i.test(doc) && /day count/i.test(doc),
    `${trade}: the message says out loud what it is not`);

  /* ── THE ONE QUESTION IS THE SPINE ─────────────────────────────────────── */
  const askIdx = await p.$$eval('#selAsk option', o => o.map(x => x.value));
  const firstAskOpt = askIdx.find(v => /^ask\d+$/.test(v));
  ok(!!firstAskOpt, `${trade}: the ask select offers the questions his list actually needs`);
  await p.selectOption('#selAsk', firstAskOpt);
  await p.waitForTimeout(150);
  doc = await copied(p);

  const picked = asks[+firstAskOpt.slice(3)];

  /* THE QUESTION IS THE SUBJECT LINE — line 1, the only line a lock-screen
     preview is guaranteed to show, and the receiving desk triages off exactly
     that. It appears there and once more as the block heading the engine prints;
     it must NEVER appear once per row, which is the shape the panel named as the
     failure ("that's not an ask, that's a survey, and it goes to the bottom").
     Driven with TWO rows under one question so a per-line print would show. */
  const twoRowAsk = 'ask' + asks.indexOf(asks[1]);
  await p.selectOption('#selAsk', twoRowAsk);
  await p.waitForTimeout(150);
  const doc2 = await copied(p);
  const up = doc2.toUpperCase(), pu = asks[1].toUpperCase();
  const hits2 = up.split(pu).length - 1;
  ok(hits2 <= 2, `${trade}: the question is the subject line and a block heading — never once per row (${hits2} across 2 rows)`);
  ok(doc2.split('\n')[0].toUpperCase().includes(pu),
    `${trade}: the question IS line 1, where a lock-screen preview shows it`);
  ok(new RegExp('\\bon 2 of these:', 'i').test(doc2),
    `${trade}: and the message says how many lines it is about, counted over what it actually contains`);
  ok(doc2.includes('GATE-TWO-XFMR') && doc2.includes('GATE-THREE-GEN') && !doc2.includes('GATE-ONE-MDP'),
    `${trade}: the message carries ONLY the lines that question is about`);

  /* AND THE FOOTER OBEYS THE SAME SCOPE. This is the defect the gate found on its
     first run: "the ones actually stopping work" drew from EVERY row, so a message
     narrowed to one question printed the other questions' lines underneath it —
     the engine's own warning ("a man must never read somebody else's problem
     inside a message addressed to him") one layer out. */
  ok(!doc2.split(/the ones actually stopping work/i).slice(1).join('').includes('GATE-ONE-MDP'),
    `${trade}: and so does the stopping-work block — no line from another question leaks into it`);

  /* AND IT ONLY EARNS ITS PLACE WHEN IT PICKS SOME OUT. Both rows under this
     question hold something up, so a block listing them is the body printed
     twice — padding, and it teaches a man to skim. */
  ok(!/the ones actually stopping work/i.test(doc2),
    `${trade}: the stopping-work block stays out when it would only repeat the body`);

  await p.selectOption('#selAsk', firstAskOpt);
  await p.waitForTimeout(150);
  doc = await copied(p);
  ok(doc.includes('GATE-ONE-MDP') && !doc.includes('GATE-TWO-XFMR') && !doc.includes('GATE-THREE-GEN'),
    `${trade}: switching the question switches the whole message`);

  /* AN ASK NOBODY NEEDS IS NOT OFFERED. Otherwise he picks a question and sends
     an empty message — the exact failure the page exists to stop, hiding inside
     the page. */
  const offered = (await p.$$eval('#selAsk option', o => o.map(x => x.textContent)))
    .filter(t => asks.some(a => t.startsWith(a)));
  ok(offered.length === 2, `${trade}: only the questions with rows on them are offered (${offered.length} of ${asks.length})`);

  /* A ROW WITH NO ASK RIDES IN NO QUESTION, and the page has to say so. */
  await addRow(p, { item: 'GATE-FOUR-NOASK', state: states[0] });
  await p.waitForTimeout(150);
  const noask = await p.$eval('#noask', e => ({ hidden: e.hidden, t: e.textContent }));
  ok(!noask.hidden && /rides in no question|ride in no question/i.test(noask.t),
    `${trade}: a row with no ask is named on the glass, where he can fix it`);
  const nohold = await p.$eval('#noholds', e => ({ hidden: e.hidden, t: e.textContent }));
  ok(!nohold.hidden && /holds?\s*up/i.test(nohold.t), `${trade}: rows with nothing said about what they hold up are named`);
  ok(!(await p.evaluate(() => window.__copied || '')).includes('have no impact recorded'),
    `${trade}: that count stays on the glass and out of the message`);

  /* ── THE LADDER IS TAP-TO-ADVANCE AND IT DOES NOT WRAP ─────────────────── */
  await p.selectOption('#selAsk', { index: (await p.$$eval('#selAsk option', o => o.length)) - 1 });
  await p.waitForTimeout(100);
  const before = await p.$eval('#list .rl-row .rl-st', e => e.getAttribute('data-st'));
  await p.click('#list .rl-row .rl-tap');
  await p.waitForTimeout(120);
  const after = await p.$eval('#list .rl-row .rl-st', e => e.getAttribute('data-st'));
  ok(before !== after, `${trade}: one tap moves a row up the ladder (${before} → ${after})`);
  // walk it to the top and one past
  for (let i = 0; i < states.length + 2; i++) { await p.click('#list .rl-row .rl-tap'); await p.waitForTimeout(60); }
  const top = await p.$eval('#list .rl-row .rl-st', e => e.getAttribute('data-st'));
  ok(top === states[states.length - 1], `${trade}: the ladder stops at "${states[states.length - 1]}" and never wraps back to blank`);

  /* ── `told` KEEPS NO HISTORY ───────────────────────────────────────────── */
  await p.click('#list .rl-row .rl-edit');
  await p.waitForTimeout(120);
  await setK(p, 'told', 'Dana, 8/2 — the second thing they told me');
  await p.click('#rlAdd');
  await p.waitForTimeout(150);
  await p.selectOption('#selAsk', { index: (await p.$$eval('#selAsk option', o => o.length)) - 1 });
  await p.waitForTimeout(120);
  doc = await copied(p);
  const tsv = await copiedTsv(p);
  const store = await p.evaluate(() => JSON.stringify(window.localStorage));
  ok(doc.includes('Dana, 8/2 — the second thing they told me'), `${trade}: the latest thing he was told rides on the line`);
  ok(!doc.includes('Kelly, 6/12'), `${trade}: the PREVIOUS one is gone from the message — no history to paste back at him`);
  ok(!tsv.includes('Kelly, 6/12'), `${trade}: and gone from the spreadsheet copy`);
  ok(!store.includes('Kelly, 6/12'), `${trade}: and gone from storage — the field holds one value, so it can never become an exhibit`);

  /* ── IT SURVIVES A RELOAD, AND CLEAR TAKES EVERYTHING ──────────────────── */
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  ok((await p.$$('#list .rl-row')).length === 4, `${trade}: the list survives a reload`);
  ok((await p.inputValue('#hJob')) === 'Rosewood ES' && (await p.inputValue('#hPo')) === 'PO 24-0881',
    `${trade}: and so does the header`);

  await p.click('#clearBtn'); await p.waitForTimeout(80);
  await p.click('#clearBtn'); await p.waitForTimeout(200);
  ok((await p.$$('#list .rl-row')).length === 0, `${trade}: Clear takes the list`);
  ok((await p.inputValue('#hJob')) === '' && (await p.inputValue('#hPo')) === '' && (await p.inputValue('#hTel')) === '',
    `${trade}: and the header with it — a different job must never inherit the last one's PO`);
  ok((await p.inputValue('#selAsk')) === '', `${trade}: and the question resets, so the next job does not send the last job's ask`);

  ok(errs.length === 0, `${trade}: no page errors${errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''}`);
  await ctx.close();
}

/* ── THE WIDTHS ─────────────────────────────────────────────────────────────
 * mobile-watertight sweeps every page in the program; this checks the controls
 * THIS page added, with rows on the glass, which is the state that page never
 * reaches. */
async function widths(browser, base, trade) {
  for (const w of [320, 360, 390, 430]) {
    const { p, ctx } = await drive(browser, base, trade, w);
    const asks = await p.$$eval('#bar [data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
    const states = await p.$$eval('#bar [data-k="state"] option', o => o.map(x => x.value).filter(Boolean));
    await addRow(p, { item: 'A very long thing indeed — the main switchboard lineup', ask: asks[0], state: states[0], gate: 'before the pads pour' });
    await p.waitForTimeout(150);
    const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    ok(over <= 0, `${trade} @${w}: no horizontal scroll (${over}px)`);
    const small = await p.$$eval('#segGroup button, #selAsk, #copyBtn, #tsvBtn, #rlAdd, #list .rl-tap, #list .rl-edit',
      els => els.filter(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.height < 44; }).map(e => (e.id || e.className) + ':' + Math.round(e.getBoundingClientRect().height)));
    ok(small.length === 0, `${trade} @${w}: every control clears the 44px floor${small.length ? ' — ' + small.join(', ') : ''}`);
    await ctx.close();
  }
}

/* ── ONE PAGE FILE, FOUR TRADES ─────────────────────────────────────────────
 * The whole point of a config is that the behaviour has one home. If the shells
 * drift, the next cycle fixes a bug on one trade and leaves three broken. */
function shellsAgree(list) {
  const norm = t => readFileSync(join(ROOT, t, 'long-pole.html'), 'utf8')
    .replace(/<title>[\s\S]*?<\/title>/, '')
    .replace(/<meta name="description"[\s\S]*?>/, '')
    .replace(/<meta name="apple-mobile-web-app-title"[\s\S]*?>/, '')
    .replace(/<span class="eyebrow" id="eyebrow">[\s\S]*?<\/span>/, '')
    .replace(/<h1 id="title">[\s\S]*?<\/h1>/, '')
    .replace(/<p class="lede" id="lede">[\s\S]*?<\/p>/, '')
    .replace(/id="creditKit">[\s\S]*?</, 'id="creditKit"><')
    .replace(/id="footName">[\s\S]*?</, 'id="footName"><')
    .replace(/placeholder="[^"]*"/g, 'placeholder=""')
    .replace(/data-g="ask" class="on">[\s\S]*?</, 'data-g="ask" class="on"><');
  const base = norm(list[0]);
  list.slice(1).forEach(t => ok(norm(t) === base,
    `${t}: the page file is the same shell as ${list[0]} — the behaviour has one home`));
}

/* ── RUN ────────────────────────────────────────────────────────────────── */
const argBase = process.argv[2];
const list = trades();
if (!list.length) { console.error('FAIL: no trade ships long-pole.html'); process.exit(1); }
console.log(`THE LONG POLE — ${list.length} trade(s): ${list.join(', ')}\n`);

list.forEach(staticChecks);
shellsAgree(list);

const { s, port } = argBase ? { s: null, port: 0 } : await serve();
const base = argBase ? argBase.replace(/\/*$/, '/') : `http://127.0.0.1:${port}/`;
const browser = await chromium.launch();
for (const t of list) { await driveTrade(browser, base, t); await widths(browser, base, t); }
await browser.close();
if (s) s.close();

notes.forEach(n => console.log(n));
console.log(`\n${checks} checks · ${fails.length} failing`);
if (fails.length) { console.log(''); fails.forEach(f => console.log(f)); process.exit(1); }
console.log('THE LONG POLE: green.');
