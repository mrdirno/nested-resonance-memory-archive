/**
 * READY TO ROCK — the walk before you hang, and no rung of it is a production report.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `framing/ready-to-rock.html` is a config on shape #3. A four-lens panel (a
 * commercial drywall foreman — the author · the GC super who gets the rock list
 * and owns the Close-In List · the EC foreman who gets the last call · a skeptic
 * armed with the program's rules) scored it 8 / 7 / 8 / 7, all build-with-
 * changes, and the changes are asserted here so a later cycle cannot undo them
 * while tidying up:
 *
 * 1. NO HUNG RUNG. The ladder is blank → Clear, two rungs, and the tap cycles
 *    back. Hung-by-room-by-day is the daily log, which somebody else owns.
 *    A hung room LEAVES the list ("Next walk") and keeps what is still held.
 *
 * 2. THE SUPER'S WORD NEVER PRINTS. The rung reads Clear on the glass; the
 *    document says "Closing:" and the word "clear" is absent from every
 *    message — it is the super's sign-off word and it starts an argument.
 *
 * 3. RANGES, NOT ROWS. 301 302 303 305 → "301–303 · 305". Never a row per room.
 *
 * 4. A HOLD IS ONE CHIP AND SIX WORDS, INDEPENDENT OF THE RUNG. Untag it and
 *    the words go with it — gone from the message, the spreadsheet copy AND
 *    storage. Retag it and the words stay. Words with no chip never commit.
 *
 * 5. NOT-WALKED ROOMS PRINT NOWHERE — not closing, not held, not mentioned.
 *
 * 6. ONE TAP CLEARS THE REST OF AN AREA — the exception-driven walk.
 *
 * 7. THE LAST CALL IS A FREE NARROWING: a trade's message carries only the
 *    rooms held for HIM, with NO chip on the line, under the rooms being
 *    rocked; GC / inspection / other are never offered as receivers.
 *
 * 8. NO COUNTS IN THE TEXT, no "tonight", no "not before", no day arithmetic,
 *    no money, no real house; the day rides on line one and on no row.
 *
 *   node tools/toolkit-gates/ready-to-rock.mjs [baseUrl]
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
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'ready-to-rock.html')))
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
const REAL_HOUSE = /\b(usg|sheetrock|certainteed|gold bond|national gypsum|georgia[- ]pacific|densglass|durock|hardie|clarkdietrich|simpson|hilti|dewalt|milwaukee|makita|procore|bluebeam)\b/i;
const VOCAB_BANS = [
  [/joint compound/i, '"joint compound" — it is mud'],
  [/\baccessories\b/i, '"accessories" — it is bead'],
  [/gypsum ceiling|gypsum board/i, 'the spec-sheet noun — it is board, it is a lid'],
];
const CLAIM_WORDS = [
  [/\bpromis\w*/i, 'the word "promised"'],
  [/\b(backcharge|liquidated|\bLDs?\b|delay claim|claim against|damages|who eats)\b/i, 'claim language'],
  [/\b(quote[ds]?|pricing|unit price|invoice|\$\d)/i, 'money'],
  [/\b(overdue|past due|days late|late by|elapsed|running late|held since|since (mon|tue|wed|thu|fri|sat|sun))\b/i, 'day arithmetic — the page never counts a day'],
  [/\b\d+\s*(lb|lbs|kg|ton)s?\b/i, 'a weight'],
  [/\b(o\.?c\.?|on cent(er|re)|screw pattern|nail(ing)? pattern|\d+\s*("|in\.?|inch(es)?)\s*(aff|off the floor|high)|hour rating|\d-?hr\b|stc\b|r-?\d+)\b/i, 'a spacing, height or rating (§SAFETY — nothing sized, spaced or rated)'],
];
const DOC_BANS = [
  [/\bclear\b/i, 'the super\'s word "clear" — the GC super\'s block: the rung reads Clear on the glass, the message says Closing'],
  [/\btonight\b/i, '"tonight" — a clock; dead at 6:40am, which is when he walks'],
  [/not before\b/i, '"not before" — aimed at a later argument, not at Thursday'],
  [/\bhung\b/i, '"hung" — a production report is the daily log'],
  [/\b(not walked|not started)\b/i, 'a not-walked room, which prints nowhere'],
];

function configOf(trade) {
  const src = readFileSync(join(ROOT, trade, 'items.js'), 'utf8');
  const i = src.indexOf('window.TOOLKIT_ROCK');
  if (i < 0) return null;
  const j = src.indexOf('\n};', i);
  return src.slice(i, j < 0 ? src.length : j + 3);
}
const strOf = (cfg, k) => {
  const m = cfg.match(new RegExp('\\n\\s*' + k + '\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"'));
  return m ? m[1] : null;
};
const whoOf = cfg => {
  const m = cfg.match(/\n\s*who\s*:\s*\[([\s\S]*?)\n\s*\]/);
  if (!m) return null;
  return [...m[1].matchAll(/\{\s*v:\s*"([^"]+)"\s*,\s*send:\s*(true|false)\s*\}/g)].map(x => ({ v: x[1], send: x[2] === 'true' }));
};

function staticChecks(trade) {
  const cfg = configOf(trade);
  ok(!!cfg, `${trade}: items.js declares TOOLKIT_ROCK`);
  if (!cfg) return;
  const page = readFileSync(join(ROOT, trade, 'ready-to-rock.html'), 'utf8');

  const who = whoOf(cfg) || [];
  ok(who.length >= 8, `${trade}: who[] carries the trades that hold a room (${who.length})`);
  ok(who.some(w => w.v === 'EC' && w.send) && who.some(w => w.v === 'GC' && !w.send) && who.some(w => /inspection/i.test(w.v) && !w.send),
    `${trade}: EC gets a last call; GC and inspection ride in the super's message only`);
  who.filter(w => !w.send).forEach(w => ok(/^(GC|Inspection|Other)$/.test(w.v), `${trade}: "${w.v}" has no message of its own — only GC, inspection and other may`));
  who.forEach(w => ok(!REAL_HOUSE.test(w.v), `${trade}: chip "${w.v}" names no real house`));

  // NO HUNG RUNG — two rungs, and the tap cycles.
  ok(!/\bhung\b/i.test(cfg.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '')) || /never a third rung|NO HUNG RUNG/.test(cfg),
    `${trade}: the config offers no HUNG rung`);
  ok(/var STATES = \[CLEAR\];/.test(page) && /statusOrder: STATES/.test(page), `${trade}: the ladder is exactly [Clear]`);
  ok(/statusWrap: true/.test(page), `${trade}: the tap cycles back to blank — one tap undoes a fat finger`);
  ok(/shared\/rowlog\.js/.test(page), `${trade}: rides shape #3`);
  ok(/rl\.remove\(/.test(page), `${trade}: a hung room LEAVES the list (Next walk) instead of earning a rung`);

  // THE CLOSING IS A MILESTONE, and the super's word never prints.
  const closing = strOf(cfg, 'closing') || '', closingTrade = strOf(cfg, 'closingTrade') || '';
  ok(/first sheet goes up/.test(closing) && /first sheet goes up/.test(closingTrade), `${trade}: both closings turn on "before the first sheet goes up" — a milestone, never a clock`);
  ok(/hear from them/.test(closing) && /from you/.test(closing), `${trade}: the super's closing lets the release come through the holder OR the super`);
  ok(/text me the day/.test(closingTrade) && /till I hear from you/.test(closingTrade), `${trade}: the trade's closing asks for the day and says the room stays held till he hears`);
  ok((strOf(cfg, 'docSubject') || '') === 'ROCK LIST', `${trade}: the subject is ROCK LIST — the trade's own phrase ("${strOf(cfg, 'docSubject')}")`);
  ok((strOf(cfg, 'docClosing') || '') === 'Closing:', `${trade}: the closing rooms print under "Closing:"`);
  ['docSubject', 'docSubjectTrade', 'docClosing', 'docRocking', 'docRockingNoDay', 'docHeld', 'closing', 'closingTrade', 'docBoundary', 'docHanging'].forEach(k => {
    const s = strOf(cfg, k) || '';
    DOC_BANS.forEach(([re, why]) => ok(!re.test(s), `${trade}: ${k} carries no ${why}`));
  });
  CLAIM_WORDS.forEach(([re, why]) => { const m = cfg.match(re); ok(!m, `${trade}: config carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  VOCAB_BANS.forEach(([re, why]) => { const m = cfg.match(re); ok(!m, `${trade}: config carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  ok(!REAL_HOUSE.test(cfg), `${trade}: config names no real house`);
  const ph = strOf(cfg, 'phHold') || '';
  ok(!/\d/.test(ph), `${trade}: the hold placeholder teaches a condition and carries no number ("${ph}")`);
}

/* ── THE DRIVE ─────────────────────────────────────────────────────────────── */
async function drive(browser, base, trade, width = 390) {
  const ctx = await browser.newContext({ viewport: { width, height: 860 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ctx.addInitScript(STUB);
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto(base + trade + '/ready-to-rock.html', { waitUntil: 'domcontentloaded' });
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
const chip = async (p, k, v) => { await p.click(`#bar [data-chips="${k}"] .rl-chip[data-v="${v}"]`); await p.waitForTimeout(40); };
const chipVal = (p, k) => p.evaluate(k => document.querySelector(`#bar [data-k="${k}"]`).value, k);
const copied = async p => { await p.click('#copyBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };
const copiedTsv = async p => { await p.click('#tsvBtn'); await p.waitForTimeout(120); return p.evaluate(() => window.__copied || ''); };
const pickTo = async (p, value) => { await p.selectOption('#selTo', { value }); await p.waitForTimeout(150); };
const line1 = doc => doc.split('\n')[0];
const rowLines = doc => doc.split('\n').filter(l => /^HELD /.test(l));
const rowCount = p => p.$$eval('#list .rl-row', r => r.length);
/* Open the pencil on the row whose main text is exactly `room`. */
async function pencil(p, room) {
  const id = await p.evaluate(room => {
    const rows = [...document.querySelectorAll('#list .rl-row')];
    const r = rows.find(x => x.querySelector('.rl-main') && x.querySelector('.rl-main').textContent.trim() === room);
    return r ? r.querySelector('.rl-edit').getAttribute('data-edit') : null;
  }, room);
  if (id == null) throw new Error('no row ' + room);
  await p.click(`#list .rl-edit[data-edit="${id}"]`);
  await p.waitForTimeout(120);
}
async function tapRow(p, room) {
  const id = await p.evaluate(room => {
    const rows = [...document.querySelectorAll('#list .rl-row')];
    const r = rows.find(x => x.querySelector('.rl-main') && x.querySelector('.rl-main').textContent.trim() === room);
    return r ? r.querySelector('.rl-tap').getAttribute('data-adv') : null;
  }, room);
  await p.click(`#list .rl-tap[data-adv="${id}"]`);
  await p.waitForTimeout(100);
}
const stateOf = (p, room) => p.evaluate(room => {
  const rows = [...document.querySelectorAll('#list .rl-row')];
  const r = rows.find(x => x.querySelector('.rl-main') && x.querySelector('.rl-main').textContent.trim() === room);
  return r ? (r.querySelector('.rl-st').getAttribute('data-st') || '') : null;
}, room);
const subOf = (p, room) => p.evaluate(room => {
  const rows = [...document.querySelectorAll('#list .rl-row')];
  const r = rows.find(x => x.querySelector('.rl-main') && x.querySelector('.rl-main').textContent.trim() === room);
  const s = r && r.querySelector('.rl-sub');
  return s ? s.textContent : '';
}, room);
async function holdRow(p, room, who, words) {
  await pencil(p, room);
  await chip(p, 'who', who);
  await setK(p, 'hold', words);
  await p.click('#rlAdd');
  await p.waitForTimeout(150);
}

async function driveTrade(browser, base, trade) {
  const { p, ctx, errs } = await drive(browser, base, trade);

  const chips = await p.$$eval('#bar [data-chips="who"] .rl-chip', o => o.map(x => x.getAttribute('data-v')));
  ok(chips.length >= 8 && chips.includes('EC') && chips.includes('GC'), `${trade}: the hold chips are on the glass (${chips.length})`);
  ok((await p.$$eval('#bar [data-chips="area"] .rl-chip', o => o.length)) === 0, `${trade}: the area is learned, never seeded`);

  // The header rides on every message.
  await p.fill('#hJob', 'Bldg C');
  await p.fill('#hSuper', 'Ken — site super');
  await p.fill('#hFrom', 'Mike — Apex Interiors');
  await p.fill('#hTel', '555-0134');
  await p.fill('#hDay', 'Thu');
  await p.waitForTimeout(120);

  /* THE WHOLE FLOOR AT ONCE — in one area, learned first so the range carries it. */
  await setLearn(p, 'area', 'L3 west');
  await p.click('#bulk summary');
  await p.fill('#bFrom', '301'); await p.fill('#bTo', '312');
  await p.click('#bGo'); await p.waitForTimeout(200);
  ok((await rowCount(p)) === 12, `${trade}: a range of twelve rooms lands in one tap (${await rowCount(p)})`);
  ok(/12 rooms/.test(await p.$eval('#tally', e => e.textContent)) && /12 not walked/.test(await p.$eval('#tally', e => e.textContent)),
    `${trade}: the tally says twelve rooms, none walked — counts live on the glass`);
  const restBefore = await p.$eval('#restRow', e => e.hidden);
  ok(!restBefore && /Rest of L3 west — clear \(12\)/.test(await p.$eval('#restRow', e => e.textContent)), `${trade}: the rest-of-the-area button offers to clear the twelve untouched rooms`);

  /* HOLDS: a chip and six words, through the pencil. */
  await holdRow(p, '304', 'EC', 'no rings north wall');
  await holdRow(p, '309', 'EC', 'cable on the stud face');
  await holdRow(p, '306', 'GC', 'your gear, you said hold it');
  await holdRow(p, '311', 'Mech', 'trunk not wrapped');
  ok(/held · EC · no rings north wall/.test(await subOf(p, '304')), `${trade}: a held row shows who and what's in the way on the glass`);

  /* WORDS WITH NO CHIP NEVER COMMIT — the guard, on Add. */
  await setK(p, 'room', '312 east wall');
  await setK(p, 'hold', 'test not on the riser');
  await p.click('#rlAdd'); await p.waitForTimeout(150);
  ok((await rowCount(p)) === 12, `${trade}: a hold with nobody on it is refused at Add (${await rowCount(p)} rows)`);
  ok(!(await p.$eval('#whoSay', e => e.hidden)), `${trade}: and the page says who's holding it? — tap one`);
  await chip(p, 'who', 'Plumber');
  await p.click('#rlAdd'); await p.waitForTimeout(150);
  ok((await rowCount(p)) === 13, `${trade}: with a chip on it the wall row lands (${await rowCount(p)})`);
  ok((await chipVal(p, 'who')) === '' && (await p.$eval('#bar [data-k="hold"]', e => e.value)) === '', `${trade}: neither the chip nor the words carry to the next room — a hold is a deliberate act per room`);

  /* A ROOM ON ANOTHER FLOOR, NOT WALKED. It must print nowhere. */
  await setLearn(p, 'area', 'L4');
  await setK(p, 'room', '401');
  await p.click('#rlAdd'); await p.waitForTimeout(120);
  ok((await rowCount(p)) === 14, `${trade}: fourteen rows on the glass`);

  /* ONE TAP CLEARS THE REST OF L3 WEST — and only L3 west. */
  await p.click('#restRow button[data-rest="L3 west"]'); await p.waitForTimeout(200);
  ok((await stateOf(p, '301')) === 'Clear' && (await stateOf(p, '312')) === 'Clear', `${trade}: the untouched L3 west rooms are clear in one tap`);
  ok((await stateOf(p, '304')) === '' && (await stateOf(p, '401')) === '', `${trade}: a held room keeps its rung and the other floor is untouched`);
  ok(/Rest of L4 — clear \(1\)/.test(await p.$eval('#restRow', e => e.textContent)) && !/L3 west/.test(await p.$eval('#restRow', e => e.textContent)),
    `${trade}: the button for L3 west is gone and L4's remains`);

  /* ── HIS OWN COPY, THEN THE SUPER'S ─────────────────────────────────────── */
  let doc = await copied(p);
  ok(line1(doc) === 'ROCK LIST — Bldg C · L3 west · hanging Thu', `${trade}: line 1 is the subject, the job, the one area walked and the day ("${line1(doc)}")`);
  ok(!/^To:/m.test(doc) && doc.includes('From: Mike — Apex Interiors · 555-0134'), `${trade}: his own copy has no To: line and carries his name`);
  ok(doc.includes('Closing: 301–303 · 305 · 307 · 308 · 310 · 312'), `${trade}: the closing rooms print as RANGES, three make a run, two stay two ("${(doc.match(/Closing:[^\n]*/) || [''])[0]}")`);
  const rl0 = rowLines(doc);
  ok(rl0.length === 5, `${trade}: five held lines in the body (${rl0.length})`);
  for (const v of ['HELD 304 — EC — no rings north wall', 'HELD 306 — GC — your gear, you said hold it', 'HELD 309 — EC — cable on the stud face', 'HELD 311 — Mech — trunk not wrapped', 'HELD 312 east wall — Plumber — test not on the riser', 'L3 WEST — 5 ROWS']) {
    ok(doc.includes(v), `${trade}: "${v}" reaches the rock list`);
  }
  ok(!doc.includes('401') && !/L4/.test(doc), `${trade}: the not-walked room on the other floor prints NOWHERE`);
  ok(doc.includes("Want one held that isn't? Say so before the first sheet goes up.") && doc.includes('My walk, not a sign-off'), `${trade}: the closing is a milestone and the boundary line is last`);
  DOC_BANS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the rock list carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  CLAIM_WORDS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the rock list carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  { const m = doc.match(/\b(EC|Mech|Plumber|GC)\s+\d+\b/) || doc.match(/\d+[ \t]+(held|closing)\b/i);
    ok(!m, `${trade}: no count of anything in the text — no scoreboard${m ? ` — found "${m[0]}"` : ''}`); }
  ok(rowLines(doc).every(l => !/\bThu\b/.test(l)), `${trade}: the day is on line 1 and on NO row`);

  await pickTo(p, 'super');
  doc = await copied(p);
  ok(doc.includes('To: Ken — site super') && line1(doc) === 'ROCK LIST — Bldg C · L3 west · hanging Thu', `${trade}: addressed to the super, same line 1`);

  /* ── THE LAST CALL: ONE TRADE, HIS ROOMS, NO CHIP, THE ADDRESS ABOVE ──── */
  const toVals = await p.$$eval('#selTo option', o => o.map(x => x.value));
  ok(toVals.includes('t:EC') && toVals.includes('t:Mech') && toVals.includes('t:Plumber') && !toVals.includes('t:GC') && !toVals.includes('t:Inspection') && !toVals.includes('t:Other'),
    `${trade}: the To-select offers the trades holding rooms and never GC, inspection or other (${toVals.join(' ')})`);
  ok((await p.$$eval('#selTo option', o => o.map(x => x.textContent))).some(t => /^EC — last call on 2 rooms/.test(t)), `${trade}: the EC option counts his rooms on the glass`);
  await pickTo(p, 't:EC');
  doc = await copied(p);
  ok(line1(doc) === 'LAST CALL BEFORE ROCK — EC — Bldg C · L3 west · hanging Thu', `${trade}: the last call's line 1 names the trade ("${line1(doc)}")`);
  ok(doc.includes('To: EC') && doc.includes('Rocking Thu: 301–303 · 305 · 307 · 308 · 310 · 312'), `${trade}: "get out" has an address — the rooms being rocked ride above his`);
  const ecRows = rowLines(doc);
  ok(ecRows.length === 2 && ecRows[0] === 'HELD 304 — no rings north wall' && ecRows[1] === 'HELD 309 — cable on the stud face', `${trade}: only his two rooms, and NO chip on the line (${JSON.stringify(ecRows)})`);
  for (const v of ['306', '311', '312 east wall', 'GC', 'Mech', 'Plumber', 'your gear', 'trunk', 'riser', '401']) {
    ok(!doc.includes(v), `${trade}: "${v}" is ABSENT from the EC's last call — another man's room, or a room nobody walked`);
  }
  ok(doc.includes("Get out before the first sheet goes up, or text me the day. I don't rock a held room till I hear from you."), `${trade}: the trade's closing`);
  ok(!doc.includes('My walk, not a sign-off'), `${trade}: the boundary line is the super's, not the trade's`);
  DOC_BANS.forEach(([re, why]) => { const m = doc.match(re); ok(!m, `${trade}: the last call carries no ${why}${m ? ` — found "${m[0]}"` : ''}`); });
  await pickTo(p, 't:Mech');
  doc = await copied(p);
  ok(rowLines(doc).length === 1 && rowLines(doc)[0] === 'HELD 311 — trunk not wrapped' && doc.includes('To: Mech') && !doc.includes('304'), `${trade}: Mech's last call is the mirror`);

  /* ── RETAG KEEPS THE WORDS; UNTAG ERASES THEM EVERYWHERE ─────────────── */
  await pencil(p, '311');
  await chip(p, 'who', 'Plumber');
  await p.click('#rlAdd'); await p.waitForTimeout(150);
  ok(/held · Plumber · trunk not wrapped/.test(await subOf(p, '311')), `${trade}: moving a hold to another trade keeps the words`);
  await pencil(p, '306');
  await chip(p, 'who', 'GC');                       // tap the on-chip: untag
  ok((await p.$eval('#bar [data-k="hold"]', e => e.value)) === '', `${trade}: untagging the chip empties the words in the same tap`);
  await p.click('#rlAdd'); await p.waitForTimeout(150);
  ok((await subOf(p, '306')) === '', `${trade}: 306 is no longer held`);
  await pickTo(p, 'super');
  doc = await copied(p);
  const tsv = await copiedTsv(p);
  const store = await p.evaluate(() => JSON.stringify(window.localStorage));
  ok(!doc.includes('your gear') && !tsv.includes('your gear') && !store.includes('your gear'), `${trade}: the untagged hold's words are gone from the message, the spreadsheet copy AND storage — nothing to paste back`);
  ok(rowLines(doc).length === 4 && !doc.includes('306'), `${trade}: 306 is neither held nor closing now (blank rung, no hold) — it prints nowhere`);
  ok(tsv.includes('trunk not wrapped') && /311\tL3 west\t\tPlumber\ttrunk not wrapped/.test(tsv), `${trade}: the spreadsheet copy carries the retagged hold`);

  /* THE GUARD IN THE PENCIL: words typed with the chip off never commit. */
  await pencil(p, '305');
  await setK(p, 'hold', 'owner walk first');
  await p.click('#rlAdd'); await p.waitForTimeout(150);
  ok((await subOf(p, '305')) === '' && (await stateOf(p, '305')) === 'Clear', `${trade}: Save with words and no chip is refused — 305 stays clear and unheld`);
  await p.click('#rlCancel'); await p.waitForTimeout(100);

  /* ── THE TAP CYCLES: Clear → blank → Clear ─────────────────────────────── */
  await tapRow(p, '301');
  ok((await stateOf(p, '301')) === '', `${trade}: one tap takes a clear room back to blank`);
  await tapRow(p, '301');
  ok((await stateOf(p, '301')) === 'Clear', `${trade}: and one more brings it back — the ladder is two rungs and it cycles`);
  await tapRow(p, '304');
  ok((await stateOf(p, '304')) === 'Clear' && /held · EC/.test(await subOf(p, '304')), `${trade}: a held room can be marked clear and STAYS held — the hold is independent of the rung`);
  await tapRow(p, '304');

  /* ── NEXT WALK: THE CLOSING ROOMS LEAVE, EVERYTHING ELSE STAYS ───────── */
  const before = await rowCount(p);
  ok(!(await p.$eval('#nextBtn', e => e.hidden)) && /Next walk — the 8 closing rooms come off/.test(await p.$eval('#nextBtn', e => e.textContent)),
    `${trade}: Next walk names the eight closing rooms it will take off ("${await p.$eval('#nextBtn', e => e.textContent)}")`);
  await p.click('#nextBtn'); await p.waitForTimeout(80);
  ok(before === (await rowCount(p)), `${trade}: one tap arms it, nothing leaves yet`);
  await p.click('#nextBtn'); await p.waitForTimeout(200);
  ok((await rowCount(p)) === 6, `${trade}: the eight closing rooms are gone; the held, the untagged and the not-walked stay (${await rowCount(p)})`);
  for (const r of ['304', '309', '311', '312 east wall', '306', '401']) ok((await stateOf(p, r)) !== null, `${trade}: ${r} is still on the list`);
  ok((await p.$eval('#nextBtn', e => e.hidden)), `${trade}: with nothing closing, Next walk is gone`);

  /* ── IT SURVIVES A RELOAD, AND CLEAR TAKES EVERYTHING ──────────────────── */
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  ok((await rowCount(p)) === 6, `${trade}: the list survives a reload`);
  ok((await p.inputValue('#hJob')) === 'Bldg C' && (await p.inputValue('#hDay')) === 'Thu' && (await p.inputValue('#selTo')) === 'super',
    `${trade}: and so do the header, the day and the receiver`);
  await p.click('#clearBtn'); await p.waitForTimeout(80);
  await p.click('#clearBtn'); await p.waitForTimeout(200);
  ok((await rowCount(p)) === 0, `${trade}: Clear takes the list`);
  ok((await p.inputValue('#hJob')) === '' && (await p.inputValue('#hSuper')) === '' && (await p.inputValue('#hDay')) === '' && (await p.inputValue('#selTo')) === '',
    `${trade}: and the header, the super and the day with it — the next job must never inherit the last one's super`);

  ok(errs.length === 0, `${trade}: no page errors${errs.length ? ' — ' + errs.slice(0, 2).join(' | ') : ''}`);
  await ctx.close();
}

/* ── THE WIDTHS ─────────────────────────────────────────────────────────────── */
async function widths(browser, base, trade) {
  for (const w of [320, 360, 390, 430]) {
    const { p, ctx } = await drive(browser, base, trade, w);
    await setLearn(p, 'area', 'Level 3 west wing, corridor side of the nurse station');
    await setK(p, 'room', '2114 north wall by the med room door');
    await chip(p, 'who', 'Sprinkler');
    await setK(p, 'hold', 'drops not cut to the lid, heads still boxed on the floor');
    await p.click('#rlAdd'); await p.waitForTimeout(120);
    await setK(p, 'room', '2115'); await p.click('#rlAdd'); await p.waitForTimeout(120);
    await pickTo(p, 't:Sprinkler');
    const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    ok(over <= 0, `${trade} @${w}: no horizontal scroll (${over}px)`);
    const small = await p.$$eval('#selTo, #copyBtn, #tsvBtn, #rlAdd, #list .rl-tap, #list .rl-edit, #restRow button, #clearBtn, #bar .rl-chip',
      els => els.filter(e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.height < 44; }).map(e => (e.id || e.className) + ':' + Math.round(e.getBoundingClientRect().height)));
    ok(small.length === 0, `${trade} @${w}: every control clears the 44px floor${small.length ? ' — ' + small.join(', ') : ''}`);
    await ctx.close();
  }
}

/* ── RUN ────────────────────────────────────────────────────────────────── */
const argBase = process.argv[2];
const list = trades();
if (!list.length) { console.error('FAIL: no trade ships ready-to-rock.html'); process.exit(1); }
list.forEach(staticChecks);

const srv = argBase ? null : await serve();
const base = argBase ? argBase.replace(/\/?$/, '/') : `http://127.0.0.1:${srv.port}/`;
const browser = await chromium.launch();
try {
  for (const t of list) { await driveTrade(browser, base, t); await widths(browser, base, t); }
} catch (e) {
  fails.push('FAIL  the drive threw: ' + String(e).split('\n')[0]);
} finally {
  await browser.close();
  if (srv) srv.s.close();
}
console.log(notes.join('\n'));
if (fails.length) console.log(fails.join('\n'));
console.log(`\n${checks} checks · ${fails.length} failing`);
console.log(fails.length ? 'READY TO ROCK: RED.' : 'READY TO ROCK: green.');
process.exit(fails.length ? 1 : 0);
