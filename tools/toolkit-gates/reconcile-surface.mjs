/**
 * THE RECONCILE SURFACE GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `tools/toolkit-gates/reconcile-join.mjs` asserts the MATCH. This asserts what
 * the match is allowed to DO once it reaches the glass, because the whole design
 * rests on properties that live in the surface and not in the join:
 *
 *  · A PAIR WE ARE NOT SURE OF ARRIVES SWITCHED OFF. This is the safety property
 *    the module's own header claims, and it SHIPPED FALSE — every pair defaulted
 *    on, unsure ones included, so a fuzzy guess against a hand-typed reply was
 *    one tap on a button from marking somebody's row committed. Nothing in the
 *    pure-logic sweep could see it: `pair()` returned `sure:false` correctly and
 *    the surface ignored the flag. A property asserted only in a comment is a
 *    property that is true until someone edits the line under it.
 *  · NOTHING MOVES WITHOUT AN EXPLICIT TAP. A reply that says neither yes nor no
 *    offers no apply button at all — not a disabled one, none.
 *  · A DISABLED CONTROL SAYS WHY. Zero to tick means two different things
 *    (everything is already on the list / nothing has been vouched for yet) and
 *    the wrong sentence there is the page lying about its own state.
 *  · AND IT MOUNTS ON EVERY TRADE, with no page error. The request page is one
 *    script block copied per trade; the deploy asserts the file is loaded and
 *    mounted, and this asserts it actually came up.
 *
 *   node tools/toolkit-gates/reconcile-surface.mjs [base-url]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const BASE = (process.argv.slice(2).find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js')
    && existsSync(ROOT + d.name + '/rough-in-request.html'))
  .map(d => d.name).sort();

let fails = 0;
const ok = (c, what, extra) => {
  if (c) { console.log('  ok   ' + what); return true; }
  fails++; console.log('  FAIL ' + what + (extra ? '\n       ' + extra : '')); return false;
};

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });

async function fresh(trade) {
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(`${BASE}/${trade}/rough-in-request.html`);
  await p.waitForFunction(() => !!document.querySelector('#rcPaste'), null, { timeout: 20000 });
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload();
  await p.waitForFunction(() => !!document.querySelector('#rcPaste'), null, { timeout: 20000 });
  return { p, errs };
}

// ── every trade carries it, and it comes up ────────────────────────────────
console.log(`the intake mounts on every trade (${TRADES.length} found on disk)`);
for (const t of TRADES) {
  const { p, errs } = await fresh(t);
  const r = await p.evaluate(() => ({
    card: !!document.querySelector('#rcCard'),
    api: typeof (window.Reconcile || {}).pair === 'function',
    apply: typeof ((window.RowLog || {}).mount) === 'function',
  }));
  ok(r.card && r.api && errs.length === 0, `${t}: card mounted, Reconcile live, no page error`,
    JSON.stringify({ ...r, errs }));
  await p.close();
}

// ── the surface properties, driven on one trade ────────────────────────────
const TRADE = TRADES.includes('av') ? 'av' : TRADES[0];
console.log(`\nthe surface, driven on ${TRADE}`);
const { p, errs } = await fresh(TRADE);

const asks = await p.$$eval('#bar select[data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
for (const [a, area, place] of [[asks[0], 'CR-204', '60 AFF'], [asks[1], 'CR-206', 'to the rack']]) {
  await p.selectOption('#bar select[data-k="ask"]', a);
  await p.evaluate(() => { const d = document.querySelector('#pickers'); if (d) d.open = true; });
  await p.fill('[data-learn="area"]', area);
  await p.dispatchEvent('[data-learn="area"]', 'blur');
  const pl = await p.$('[data-k="place"]'); if (pl) await p.fill('[data-k="place"]', place);
  await p.click('.rl-add');
}
const req = await p.textContent('#preview');
const rowLines = req.split('\n').filter(l => /CR-20/.test(l));
ok(rowLines.length === 2, 'the request document carries both rows', JSON.stringify(rowLines));

// A) he forwarded the list back with no verdict on anything
await p.fill('#rcPaste', rowLines.join('\n'));
await p.click('#rcGo');
let r = await p.evaluate(() => ({
  blocks: [...document.querySelectorAll('#rcOut .rc-block')].map(x => ({
    h: (x.querySelector('.rc-h') || {}).textContent || '', n: x.querySelectorAll('.rc-pair').length })),
  apply: !!document.querySelector('#rcApply'),
}));
ok(r.blocks.some(b => /didn't say yes or no/i.test(b.h) && b.n === 2),
  'a verdict-less forward lands under "didn\'t say yes or no"', JSON.stringify(r.blocks));
ok(!r.blocks.some(b => /doing these/i.test(b.h)), 'and offers nothing for ticking');
ok(!r.apply, 'with no apply button at all — not a disabled one, none');

// B) a loose hand-typed reply: proposed, switched OFF, and it says so
await p.evaluate(() => { document.querySelector('#rcIntake').open = true; });
await p.fill('#rcPaste', 'WILL DO — 1 ROW\nthe back box in 204 — thursday');
await p.click('#rcGo');
r = await p.evaluate(() => {
  const y = [...document.querySelectorAll('#rcOut .rc-block')]
    .find(x => /doing these/i.test((x.querySelector('.rc-h') || {}).textContent || ''));
  if (!y) return null;
  const pr = [...y.querySelectorAll('.rc-pair')];
  const b = document.querySelector('#rcApply');
  return {
    n: pr.length, on: pr.filter(x => x.classList.contains('on')).length,
    pressed: pr.map(x => x.getAttribute('aria-pressed')),
    subs: pr.map(x => x.querySelector('.rc-sub').textContent),
    btn: b ? b.textContent : null, dis: b ? b.disabled : null,
    note: (y.querySelector('.note') || {}).textContent || '',
  };
});
ok(!!r && r.n === 1, 'the loose line proposes exactly one pair', JSON.stringify(r));
ok(!!r && r.on === 0 && r.pressed[0] === 'false', 'IT ARRIVES SWITCHED OFF', JSON.stringify(r && { on: r.on, pressed: r.pressed }));
ok(!!r && /not sure/i.test(r.subs[0]), 'and says "not sure it\'s the same one"', r && r.subs[0]);
ok(!!r && r.dis === true, 'the apply button is disabled', JSON.stringify(r && r.btn));
ok(!!r && !/nothing left to tick/i.test(r.btn || ''), 'and does NOT claim there is nothing left to tick', r && r.btn);
ok(!!r && /couldn't be sure/i.test(r.note), 'the note tells him he can vouch for it', r && r.note.slice(0, 90));

// vouching for it turns it on
await p.evaluate(() => document.querySelector('#rcOut .rc-pair[data-tick]').click());
let b2 = await p.evaluate(() => ({ t: document.querySelector('#rcApply').textContent, d: document.querySelector('#rcApply').disabled }));
ok(b2.d === false && /Tick 1 row/i.test(b2.t), 'tapping it on enables the apply', JSON.stringify(b2));
// and off again
await p.evaluate(() => document.querySelector('#rcOut .rc-pair[data-tick]').click());
b2 = await p.evaluate(() => ({ t: document.querySelector('#rcApply').textContent, d: document.querySelector('#rcApply').disabled }));
ok(b2.d === true, 'and tapping it off disables it again — the toggle flips the effective state', JSON.stringify(b2));

// C) an unvouched unsure pair must never reach the list
await p.evaluate(() => { const b = document.querySelector('#rcApply'); if (b && !b.disabled) b.click(); });
const stored = await p.evaluate(() => {
  const k = Object.keys(localStorage).find(x => /rough-in-request/.test(x));
  return JSON.parse(localStorage.getItem(k)).rows.map(x => x.values.status || '');
});
ok(stored.every(s => s === ''), 'NOTHING was committed while the only pair was unvouched', JSON.stringify(stored));
ok(errs.length === 0, 'no page errors through the whole surface', errs.join(' | '));

// ── D) AN "IN" ROW IS A FACT SOMEBODY WALKED OUT AND VERIFIED ──────────────
// The report is a photograph and the list moves under it. Apply must never walk
// a row back DOWN the ladder, and the card must not still be offering a row the
// man already settled by hand.
console.log('\nthe list moves under the report');
{
  await p.evaluate(() => { document.querySelector('#rcIntake').open = true; });
  await p.fill('#rcPaste', 'WILL DO — 2 ROWS\n' + rowLines.join('\n'));
  await p.click('#rcGo');
  let n = await p.evaluate(() => (document.querySelector('#rcApply') || {}).textContent);
  ok(/Tick 2 rows/i.test(n || ''), 'both rows are proposed', n);

  // he walks the job with the card open and settles row 1 by hand: Committed, then In
  await p.evaluate(() => { document.querySelectorAll('.rl-tap')[0].click(); document.querySelectorAll('.rl-tap')[0].click(); });
  const mid = await p.evaluate(() => {
    const k = Object.keys(localStorage).find(x => /rough-in-request/.test(x));
    return { stored: JSON.parse(localStorage.getItem(k)).rows.map(r => r.values.status || ''),
             btn: (document.querySelector('#rcApply') || {}).textContent };
  });
  ok(mid.stored[0] === 'In', 'row 1 is now In — verified with his own eyes', JSON.stringify(mid.stored));
  ok(/Tick 1 row/i.test(mid.btn || ''), 'and the card followed the list down to 1', mid.btn);

  await p.evaluate(() => { const b = document.querySelector('#rcApply'); if (b && !b.disabled) b.click(); });
  const after = await p.evaluate(() => {
    const k = Object.keys(localStorage).find(x => /rough-in-request/.test(x));
    return { stored: JSON.parse(localStorage.getItem(k)).rows.map(r => r.values.status || ''),
             msg: document.querySelector('#rcMsg').textContent };
  });
  ok(after.stored[0] === 'In', 'APPLY DID NOT WALK IT BACK DOWN TO COMMITTED', JSON.stringify(after.stored));
  ok(after.stored[1] === 'Committed', 'and the other row was ticked normally', JSON.stringify(after.stored));
  ok(/Ticked 1 row/i.test(after.msg), 'the confirmation counts what actually moved', after.msg);
}

// ── E) HIS FLAG IS THE LOUDEST THING IN A REPLY ────────────────────────────
// answer-back prints a flagged row twice (its answer block AND the FLAGGED
// block). The flag must reach "he pushed back", not the couldn't-place drawer.
console.log('\nhis flag reaches the pushback block');
{
  /* CLEAR THROUGH THE PAGE'S OWN CONTROL, never localStorage.clear() + reload
     (§SCARS 2026-08-05 — that is a circular test: the reload fires `pagehide`,
     the engine flushes its still-in-memory rows straight back, and the "fresh"
     page comes up carrying everything you thought you wiped. This gate proved
     it on itself — two rows and an "already in" tag appeared on a list that had
     just been emptied). #clearBtn is armed by the first tap and fires on the
     second, exactly as a thumb would do it. */
  await p.click('#clearBtn'); await p.click('#clearBtn');
  await p.waitForFunction(() => document.querySelectorAll('.rl-tap').length === 0);
  const asks2 = await p.$$eval('#bar select[data-k="ask"] option', o => o.map(x => x.value).filter(Boolean));
  await p.selectOption('#bar select[data-k="ask"]', asks2[0]);
  await p.evaluate(() => { const d = document.querySelector('#pickers'); if (d) d.open = true; });
  await p.fill('[data-learn="area"]', 'CR-204'); await p.dispatchEvent('[data-learn="area"]', 'blur');
  await p.click('.rl-add');
  const line = (await p.textContent('#preview')).split('\n').filter(l => /CR-204/.test(l))[0];
  await p.evaluate(() => { document.querySelector('#rcIntake').open = true; });
  await p.fill('#rcPaste', [
    'Building C — my answer on your list — Aug 11', '', 'Job: Building C', '',
    'NEED TO KNOW — 1 ROW', line + ' — whose scope is this?', '',
    'FLAGGED — 1', 'Not mine · ' + line + ' · Need to know',
  ].join('\n'));
  await p.click('#rcGo');
  const r2 = await p.evaluate(() => {
    const b = [...document.querySelectorAll('#rcOut .rc-block')]
      .find(x => /pushed back/i.test((x.querySelector('.rc-h') || {}).textContent || ''));
    const drawer = document.querySelector('#rcOut details');
    return b ? { n: b.querySelectorAll('.rc-pair').length,
                 tags: [...b.querySelectorAll('.rc-tag')].map(t => t.textContent),
                 drawer: drawer ? drawer.querySelector('summary').textContent : '' } : null;
  });
  ok(!!r2 && r2.n === 1, 'the flagged row lands under "he pushed back on these"', JSON.stringify(r2));
  ok(!!r2 && r2.tags.some(t => /not mine/i.test(t)), 'wearing his flag as a tag', JSON.stringify(r2 && r2.tags));
  ok(!!r2 && !/couldn't place/i.test(r2.drawer), 'and nothing was left in the couldn\'t-place drawer', r2 && r2.drawer);
}

await browser.close();
console.log('');
console.log(fails ? `RECONCILE SURFACE GATE: ${fails} FAILED` : 'RECONCILE SURFACE GATE: all green');
process.exit(fails ? 1 : 0);
