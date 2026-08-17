/**
 * THE RECONCILE JOIN GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * shared/reconcile.js matches the OTHER company's reply back onto the rows that
 * asked for it, and a wrong match silently marks an item committed that nobody
 * committed to. That failure has no symptom until a wall is closed, so the join
 * is asserted rather than eyeballed.
 *
 * IT SWEEPS THE REAL MODULE, never a copy — the file is read off disk and run,
 * so a rule that drifts in reconcile.js and not here fails here. (A test that
 * re-implements the logic it is testing asserts that two copies agree.)
 *
 * WHAT IT HOLDS DOWN:
 *  · THE ROUND TRIP. The request page's own document line, answered through
 *    answer-back's own document format, must come home to the row it came from
 *    — for EVERY grouping the list could have been copied on, because the axis
 *    the document was grouped by is dropped from its lines and the page cannot
 *    know which walk the other man is holding.
 *  · THE VERDICT VOCABULARY. answer-back's ladder is read out of the shipped
 *    page and every rung must be classified here. A rung renamed there and not
 *    here reads every answer as "he didn't say yes or no" — silently, on all
 *    seven trades at once.
 *  · THE NEAR-MISS. Two rows that differ by one token (60 AFF / 48 AFF) are the
 *    normal case on a real list. The exact line must take its own row, and the
 *    other row must be reported unanswered rather than quietly stolen.
 *  · TIMIDITY. A hand-typed reply that half-resembles two rows must come back
 *    NOT SURE, so the surface shows it switched off.
 *  · THE PARSER'S FALSE DROP. "Off the main tee" is a real ask in two
 *    vocabularies and starts with one of our header keys. Dropping it turns a
 *    real answer into a row this page reports as never mentioned.
 *
 *   node tools/toolkit-gates/reconcile-join.mjs
 */
import { readFileSync, readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));

/* Run the shipped file. It is an IIFE whose only global effect is
   window.Reconcile, so a bare object is a sufficient window. */
const src = readFileSync(ROOT + 'shared/reconcile.js', 'utf8');
const win = {};
new Function('window', src)(win);
const R = win.Reconcile;

let fails = 0, checks = 0;
function ok(cond, what, extra) {
  checks++;
  if (cond) return true;
  fails++;
  console.log('  FAIL  ' + what + (extra ? '\n        ' + extra : ''));
  return false;
}

/* ── the two document formats, as the shipped pages write them ──────────────
   rough-in-request docRow: one line per item, middots, the grouped axis
   dropped. answer-back docRow: his line, an em-dash, then his answer. */
const dots = (a) => a.filter(x => x != null && String(x).trim() !== '').join(' · ');
const dash = (a) => a.filter(x => x && String(x).trim()).join(' — ');

const ROWS = [
  { id: 1, area: 'CR-204', ask: 'Back box + mud ring', spec: '4-11/16 sq', place: '60 AFF', by: 'before rock', who: 'Electrician', note: '' },
  { id: 2, area: 'CR-204', ask: 'Back box + mud ring', spec: '4-11/16 sq', place: '48 AFF', by: 'before rock', who: 'Electrician', note: '' },
  { id: 3, area: 'CR-206', ask: 'Conduit to the ceiling', spec: '1in EMT', place: 'to the rack', by: 'before rock', who: 'Electrician', note: 'pull string in it' },
  { id: 4, area: 'Lobby', ask: 'Floor box', spec: '4-gang', place: 'at the column', by: 'before the pour', who: 'Electrician', note: '' },
  { id: 5, area: 'Rack room', ask: 'Access door', spec: '24x24', place: 'above the rack', by: 'before paint', who: 'GC', note: '' },
];

// what the request page SENDS, grouped by g (that axis is the heading, so it is
// dropped from the line)
const sent = (r, g) => dots([
  g === 'area' ? null : r.area, r.ask, r.spec, r.place,
  g === 'by' ? null : r.by, g === 'who' ? null : r.who, r.note,
]);

// the four forms the page offers the matcher — must mirror the mount config in
// <trade>/rough-in-request.html
const forms = (r) => [
  dots([r.area, r.ask, r.spec, r.place, r.by, r.who, r.note]),
  dots([r.area, r.ask, r.spec, r.place, r.by, r.note]),
  dots([r.ask, r.spec, r.place, r.by, r.who, r.note]),
  dots([r.area, r.ask, r.spec, r.place, r.who, r.note]),
];
const forMatch = (rows) => rows.map(r => ({ id: r.id, text: forms(r) }));

// what answer-back SENDS BACK, grouped by his answer (its default)
function reply(items, { job = 'Building C', from = 'Sparky — Volt EC', groupBy = 'status' } = {}) {
  const out = [`${job} — my answer on your list — Aug 11`, '', `Job: ${job}`, 'To: Rico — Acme AV', `From: ${from}`, 'On your list off E4.01', '', `${items.length} LINES — answered`];
  if (groupBy === 'status') {
    const order = ['Will do', 'In already', "Can't", 'Need to know'];
    for (const st of order) {
      const g = items.filter(i => i.status === st);
      if (!g.length) continue;
      out.push('', `${st.toUpperCase()} — ${g.length} ROW${g.length === 1 ? '' : 'S'}`);
      for (const i of g) out.push(dash([i.line, dots([i.when, i.note])]));
    }
  } else {
    const whens = [...new Set(items.map(i => i.when || ''))];
    for (const w of whens) {
      const g = items.filter(i => (i.when || '') === w);
      out.push('', `${(w || 'NO DATE').toUpperCase()} — ${g.length} ROW${g.length === 1 ? '' : 'S'}`);
      for (const i of g) out.push(dash([dots([i.line, i.status.toUpperCase()]), dots([i.note])]));
    }
  }
  out.push('', "That's my answer on everything you sent. Anything under CAN'T or NEED TO KNOW I need back from you before I can move on it — call me and I'll walk it with you.");
  out.push("This is what I'm committing to off the list you sent me. There's no price on it, it isn't a change order, and it doesn't change anybody's scope.");
  return out.join('\n');
}

/* ── 1. THE VERDICT VOCABULARY, READ OFF THE SHIPPED PAGE ──────────────────── */
console.log('verdict vocabulary — answer-back\'s ladder must be fully classified');
{
  /* THE GATE WAS MATCHING ON SOURCE SHAPE AND HAD SILENTLY STOPPED DOING ITS
     JOB (found standing up trade #13). It read `var ANSWERS = [...]` with a
     regex; a later cycle made the ladder per-trade — `var ANSWERS = (A.answers
     && A.answers.length === 4) ? A.answers.slice() : [...]` — and the regex
     stopped matching. The `ok(!!m)` went red, which looks like one failure, but
     everything real was inside `if (m)`: the classification checks this section
     EXISTS to run were not running at all. Exactly the class §SCARS already
     records one layer down — matching on words means a gate stops testing the
     day somebody improves the wording — so this now reads the FALLBACK literal
     out of the page AND every trade's own declared ladder out of its items.js,
     both derived from disk, and classifies all of them. */
  const ab = readFileSync(ROOT + 'av/answer-back.html', 'utf8');
  const m = /var ANSWERS = [\s\S]{0,120}?\[([^\]]+)\]/.exec(ab);
  ok(!!m, 'answer-back.html still declares the four default rungs inline');
  const ladders = [];
  if (m) {
    ladders.push({ from: 'av/answer-back.html (default)', rungs: m[1].split(',').map(s => s.trim().replace(/^["']|["']$/g, '')) });
  }
  /* A trade that renames the ladder in its own vocabulary is exactly the case
     that must not go unclassified, and it is the one the old regex could never
     have seen even when it matched. */
  for (const dir of readdirSync(ROOT, { withFileTypes: true })) {
    if (!dir.isDirectory()) continue;
    const items = ROOT + dir.name + '/items.js';
    if (!existsSync(items)) continue;
    const w = {};
    try { new Function('window', readFileSync(items, 'utf8'))(w); } catch { continue; }
    const own = w.TOOLKIT_ANSWER && w.TOOLKIT_ANSWER.answers;
    if (Array.isArray(own) && own.length) ladders.push({ from: dir.name + '/items.js', rungs: own });
  }
  ok(ladders.length >= 1, `read ${ladders.length} ladder(s) off disk`, ladders.map(l => l.from).join(' · '));
  for (const { from, rungs } of ladders) {
    ok(rungs.length >= 3, `${from}: read ${rungs.length} rungs`, rungs.join(' / '));
    for (const rung of rungs) {
      const key = R.norm(rung);
      ok(Object.prototype.hasOwnProperty.call(R.VERDICTS, key),
        `"${rung}" (${from}) is classified in reconcile.js VERDICTS`,
        `normalises to "${key}" — add it, or every answer on that trade reads as "didn't say yes or no"`);
    }
  }
}

/* ── 2. THE CLEAN ROUND TRIP, ON EVERY GROUPING ────────────────────────────── */
console.log('round trip — every grouping the list could have been copied on');
for (const g of ['who', 'area', 'by', '']) {
  const items = ROWS.map((r, i) => ({
    row: r, line: sent(r, g),
    status: ['Will do', 'Will do', 'In already', "Can't", 'Need to know'][i],
    when: ['Thursday', 'Thursday', '', '', ''][i], note: ['', '', '', 'panel is full', 'which column?'][i],
  }));
  const parsed = R.parse(reply(items));
  ok(parsed.lines.length === ROWS.length,
    `[group:${g || 'none'}] ${ROWS.length} answer lines survive the parser`,
    `got ${parsed.lines.length}: ${parsed.lines.map(l => l.ask).join(' | ')}`);

  const res = R.pair(forMatch(ROWS), parsed.lines);
  ok(res.pairs.length === ROWS.length, `[group:${g || 'none'}] every row is paired`, `got ${res.pairs.length}`);
  ok(res.unplaced.length === 0, `[group:${g || 'none'}] no answer line left unplaced`, JSON.stringify(res.unplaced));

  for (const p of res.pairs) {
    const line = parsed.lines[p.lineIx];
    const src = items.find(i => i.line === (line.raw.split(' — ')[0]) || line.ask === i.line);
    ok(!!src && src.row.id === p.rowId,
      `[group:${g || 'none'}] line "${line.ask.slice(0, 34)}…" came home to row ${src ? src.row.id : '?'}`,
      `paired with row ${p.rowId}`);
    ok(p.sure, `[group:${g || 'none'}] row ${p.rowId} is SURE (exact=${p.exact}, score=${p.score.toFixed(2)})`);
  }

  // the verdicts survive the trip
  const byRow = Object.fromEntries(res.pairs.map(p => [p.rowId, parsed.lines[p.lineIx].verdict]));
  ok(byRow[1] === 'yes' && byRow[3] === 'in' && byRow[4] === 'no' && byRow[5] === 'ask',
    `[group:${g || 'none'}] verdicts land: ${JSON.stringify(byRow)}`);
}

/* ── 3. GROUPED BY WHEN — the rung rides IN the line, not in the heading ───── */
console.log('grouped by when — the verdict is inside the line');
{
  const items = ROWS.slice(0, 3).map((r, i) => ({
    row: r, line: sent(r, 'who'),
    status: ['Will do', "Can't", 'In already'][i],
    when: ['Thursday', 'Thursday', 'Monday'][i], note: '',
  }));
  const parsed = R.parse(reply(items, { groupBy: 'when' }));
  const res = R.pair(forMatch(ROWS), parsed.lines);
  const byRow = Object.fromEntries(res.pairs.map(p => [p.rowId, parsed.lines[p.lineIx].verdict]));
  ok(byRow[1] === 'yes' && byRow[2] === 'no' && byRow[3] === 'in',
    `verdicts read off the line: ${JSON.stringify(byRow)}`);
  for (const p of res.pairs) ok(p.sure, `row ${p.rowId} still SURE with the rung inside the line`);
}

/* ── 4. THE NEAR-MISS — one answer, two rows that differ by one token ──────── */
console.log('near-miss — the exact line takes its own row and steals nothing');
{
  const items = [{ line: sent(ROWS[0], 'who'), status: 'Will do', when: 'Thursday', note: '' }];
  const parsed = R.parse(reply(items));
  const res = R.pair(forMatch(ROWS), parsed.lines);
  ok(res.pairs.length === 1, 'exactly one pair', JSON.stringify(res.pairs));
  ok(res.pairs[0] && res.pairs[0].rowId === 1, 'it is row 1 (60 AFF), not row 2 (48 AFF)');
  ok(res.pairs[0] && res.pairs[0].exact && res.pairs[0].sure, 'and it is exact + sure');
  ok(res.unmatched.length === 4 && res.unmatched.includes(2),
    'the other four rows come back unanswered, row 2 among them', JSON.stringify(res.unmatched));
}

/* ── 5. TIMIDITY — a hand-typed reply that half-resembles two rows ─────────── */
console.log('timidity — a loose hand-typed reply is proposed, never assumed');
{
  const parsed = R.parse('back box CR-204 60 aff — yeah thursday');
  ok(parsed.lines.length === 1, 'the one line survives');
  const res = R.pair(forMatch(ROWS), parsed.lines);
  if (ok(res.pairs.length === 1, 'it proposes one pair', JSON.stringify(res.pairs))) {
    ok(res.pairs[0].rowId === 1, 'against the closest row');
    ok(!res.pairs[0].sure, `and it is NOT sure (score ${res.pairs[0].score.toFixed(2)})`);
  }
}

/* ── 6. JUNK NEVER PAIRS ───────────────────────────────────────────────────── */
console.log('junk — a reply with nothing of ours in it pairs with nothing');
{
  const parsed = R.parse("Thanks bud. I'll be on site Tuesday, call me when you get there.");
  const res = R.pair(forMatch(ROWS), parsed.lines);
  ok(res.pairs.length === 0, 'no pairs', JSON.stringify(res.pairs));
  ok(res.unmatched.length === ROWS.length, 'and every row is still unanswered');
}

/* ── 7. THE PARSER'S FALSE DROP ────────────────────────────────────────────── */
console.log('parser — a real ask that starts with one of our header keys survives');
{
  const p = R.parse([
    'Building C — my answer on your list — Aug 11',
    '',
    'Job: Building C',
    'Off: E4.01',
    'Still open: 3 of 11',
    '11 LINES — 4 will do',
    '',
    'WILL DO — 2 ROWS',
    'Off the main tee · hold a full tile · before the lid — Thursday',
    'To the rack · 1in conduit — Thursday',
  ].join('\n'));
  const kept = p.lines.map(l => l.ask);
  ok(kept.length === 2, 'the two asks are kept, the headers are not', JSON.stringify(kept));
  ok(kept.some(k => /main tee/.test(k)), '"Off the main tee" survives — the colon is what makes a header');
  ok(kept.some(k => /To the rack/i.test(k)), '"To the rack" survives');
  ok(p.dropped.length === 6, 'and every dropped line is handed back to be shown', JSON.stringify(p.dropped));
  ok(p.lines.every(l => l.verdict === 'yes'), 'both carry the heading\'s verdict');
}

/* ── 8. A BARE LIST OF ASKS — no header at all, first line must survive ────── */
console.log('bare paste — a man who pastes only his four asks loses none of them');
{
  const lines = ROWS.slice(0, 4).map(r => sent(r, 'who'));
  const p = R.parse(lines.join('\n'));
  ok(p.lines.length === 4, 'all four survive', `got ${p.lines.length}`);
  const res = R.pair(forMatch(ROWS), p.lines);
  ok(res.pairs.length === 4 && res.pairs.every(x => x.sure), 'and all four pair, all sure');
  ok(res.pairs.every(p2 => p2.lineIx >= 0), 'with a line index each');
}

/* ── 9. ONE LINE CANNOT TAKE TWO ROWS ──────────────────────────────────────── */
console.log('assignment — every row and every line is claimed at most once');
{
  const items = ROWS.map(r => ({ line: sent(r, 'who'), status: 'Will do', when: 'Thursday', note: '' }));
  const parsed = R.parse(reply(items));
  const res = R.pair(forMatch(ROWS), parsed.lines);
  const rows = res.pairs.map(p => p.rowId), lns = res.pairs.map(p => p.lineIx);
  ok(new Set(rows).size === rows.length, 'no row claimed twice', JSON.stringify(rows));
  ok(new Set(lns).size === lns.length, 'no line claimed twice', JSON.stringify(lns));
}

/* ── 10. DETERMINISM — the same input twice is the same answer ─────────────── */
console.log('determinism — no ordering luck in the greedy assignment');
{
  const items = ROWS.map((r, i) => ({ line: sent(r, 'who'), status: i % 2 ? 'Will do' : "Can't", when: '', note: '' }));
  const txt = reply(items);
  const a = JSON.stringify(R.pair(forMatch(ROWS), R.parse(txt).lines));
  const b = JSON.stringify(R.pair(forMatch([...ROWS].reverse()), R.parse(txt).lines).pairs.slice().sort((x, y) => x.rowId - y.rowId));
  const a2 = JSON.stringify(JSON.parse(a).pairs.slice().sort((x, y) => x.rowId - y.rowId));
  ok(a2 === b, 'row order does not change the pairing', `${a2}\n        ${b}`);
}

/* ── 11. A RATIO IS NOT AN IDENTITY (adversarial audit 2026-08-11) ─────────── */
console.log('identity — one wrong room number is never "sure", however high it scores');
{
  // a line about CR-208, which is on nobody's list. It differs from the CR-206
  // row by exactly one token out of ~12.
  const line = sent(ROWS[2], 'who').replace('CR-206', 'CR-208');
  const parsed = R.parse(reply([{ line, status: 'Will do', when: 'Thursday', note: '' }]));
  const res = R.pair(forMatch(ROWS), parsed.lines);
  if (ok(res.pairs.length === 1, 'it still PROPOSES the closest row — nothing is hidden', JSON.stringify(res.pairs))) {
    ok(res.pairs[0].score >= 0.85, `and it scores high (${res.pairs[0].score.toFixed(3)}) — which is exactly the trap`);
    ok(!res.pairs[0].sure, 'BUT IT IS NOT SURE — a ratio cannot tell a typo from a different room');
    ok(!res.pairs[0].exact, 'and not exact');
  }
}

/* ── 12. IDENTICAL FORMS ACROSS ROWS — same device, three rooms ────────────── */
console.log('ambiguity — one line matching several rows exactly is sure of none of them');
{
  const three = [1, 2, 3].map(i => ({ id: i, area: `CR-20${i}`, ask: 'Back box', spec: 'Deep box + 2-gang mud ring', place: '60 AFF', by: 'before rock', who: 'Electrician', note: '' }));
  // copied grouped by WHERE, so the room is the heading and is not on the line
  const line = sent(three[0], 'area');
  const parsed = R.parse(reply([{ line, status: 'Will do', when: '', note: '' }]));
  const res = R.pair(forMatch(three), parsed.lines);
  ok(res.pairs.length === 1, 'one line claims one row', JSON.stringify(res.pairs));
  ok(res.pairs[0] && res.pairs[0].exact, 'the match IS exact — three rows produce the same string');
  ok(res.pairs[0] && !res.pairs[0].sure,
    'and precisely because it is exact against THREE rows, it is not sure',
    JSON.stringify(res.pairs[0]));
  ok(res.unmatched.length === 2, 'the other two rooms come back unanswered, not silently ticked');
}

/* ── 13. A DISCLAIMER PHRASE INSIDE A ROW MUST NOT TRUNCATE THE DOCUMENT ───── */
console.log('sign-off — our own shipped spec text is not a sign-off');
{
  // av/items.js ships this spec under "Keep the wall clear"; it matches DISCLAIM.
  const trap = { area: 'CR-204', ask: 'Keep the wall clear', spec: 'Walk the wall with me before anybody roughs it', place: '', by: 'before rock', who: 'Electrician', note: '' };
  const items = [
    { line: sent(ROWS[0], 'who'), status: 'Will do', when: 'Thursday', note: '' },
    { line: sent(trap, 'who'), status: 'Will do', when: 'Thursday', note: '' },
    { line: sent(ROWS[2], 'who'), status: "Can't", when: '', note: 'panel is full' },
  ];
  const parsed = R.parse(reply(items));
  ok(parsed.lines.length === 3, 'all three answers survive — the trap row does not cut the document',
    `got ${parsed.lines.length}: ${parsed.lines.map(l => l.ask.slice(0, 30)).join(' | ')}`);
  ok(parsed.lines.some(l => /Keep the wall clear/.test(l.ask)), 'including the trap row itself');
  // and his own note carrying one of the phrases
  const p2 = R.parse(reply([
    { line: sent(ROWS[0], 'who'), status: 'Will do', when: 'Thursday', note: 'verify it before I set the box' },
    { line: sent(ROWS[2], 'who'), status: 'Need to know', when: '', note: 'which column?' },
  ]));
  ok(p2.lines.length === 2, "his own note carrying a disclaimer phrase does not cut the rest either",
    `got ${p2.lines.length}`);
}

/* ── 14. A SIGNATURE AT THE BOTTOM IS NOT A HEADER BLOCK AT THE TOP ────────── */
console.log('subject rule — a phone number in the sign-off must not eat the first answer');
{
  const p = R.parse([
    'back box CR-204 60 aff mud ring — will do thursday',
    'conduit to the rack CR-206 — will do tuesday',
    'Call me: 555-0134',
  ].join('\n'));
  ok(p.lines.length === 2, 'both answers survive', JSON.stringify(p.lines.map(l => l.ask)));
  ok(p.lines.some(l => /back box/i.test(l.ask)), 'including the FIRST one');
  // ...and a real document still loses its subject line
  const q = R.parse(reply([{ line: sent(ROWS[0], 'who'), status: 'Will do', when: '', note: '' }]));
  ok(q.dropped.some(l => /my answer on your list/.test(l)), 'while a real document still drops its subject');
}

/* ── 15. A PASTED EMAIL'S NO-BREAK SPACES ─────────────────────────────────── */
console.log('unicode — NBSP around the em dash must not swallow his date');
{
  const clean = `${sent(ROWS[0], 'who')} — Thursday`;
  const nbsp = clean.replace(' — ', ' — ');
  const p = R.parse('WILL DO — 1 ROW\n' + nbsp);
  ok(p.lines.length === 1, 'the line survives');
  ok(p.lines[0].tail === 'Thursday', 'and his date is read off the tail, not buried in the ask', JSON.stringify(p.lines[0]));
  const res = R.pair(forMatch(ROWS), p.lines);
  ok(res.pairs.length === 1 && res.pairs[0].rowId === 1 && res.pairs[0].sure,
    'and it is still an exact, sure match to row 1', JSON.stringify(res.pairs));
}

console.log('');
console.log(fails ? `RECONCILE JOIN GATE: ${fails} FAILED of ${checks}` : `RECONCILE JOIN GATE: ${checks} checks, all green`);
process.exit(fails ? 1 : 0);
