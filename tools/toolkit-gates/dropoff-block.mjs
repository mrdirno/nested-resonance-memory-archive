/**
 * THE DROP-OFF BLOCK — does the job it claims, on every page that mounts it.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * shared/dropoff.js exists because a Delivery button that collected nothing had
 * been shipped for four months on plumbing/supply-house-order.html. The failure
 * was invisible: the button was there, it lit up, it changed one word of the
 * message, and nothing about the page said the other seven answers were missing.
 * A gate that only checks the block renders would re-ship exactly that.
 *
 * So this drives it the way a foreman does and asserts the OUTPUT:
 *
 *  · IT SHOWS ONLY WHERE IT BELONGS. Tap the delivery mode and the block is on
 *    the glass; tap back and it is gone AND OUT OF THE DOCUMENT. A will-call
 *    carrying gate codes is the same lie in the other direction.
 *  · EVERY ANSWER HE GIVES REACHES THE MESSAGE. Each chip, the not-before clock
 *    and all three text fields are set and then looked for, by value, in what the
 *    real Copy button puts on the clipboard.
 *  · IT IS AN ASK, NOT A BOOKING. The line that says so must be in the document
 *    every time the block is. A man who ticks "boom · not before 7 · level 2" and
 *    taps Copy can believe he has scheduled a crane; he has put text on a
 *    clipboard, and the only thing standing between those two is that sentence.
 *  · IT SURVIVES THE JOB. The answers are the same all year, so they are sticky —
 *    asserted through a real reload, because sticky that does not come back is
 *    worse than not sticky at all: he stops checking.
 *  · NOTHING RATED, NOTHING PRICED, NO COMPANY NAMED. The block's own options are
 *    scanned for a capacity, a weight, a reach, a price or a brand (§SAFETY).
 *
 *   node tools/toolkit-gates/dropoff-block.mjs
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      if (readFileSync(join(ROOT, t, f), 'utf8').includes('shared/dropoff.js')) out.push(`${t}/${f}`);
    }
  }
  return out;
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
function serve() {
  return new Promise(res => {
    const s = createServer((req, rq) => {
      const rel = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      const p = join(ROOT, rel);
      if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { rq.writeHead(404); return rq.end('no'); }
      rq.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
      rq.end(readFileSync(p));
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
async function copied(page) {
  await page.evaluate(() => { window.__copied = null; });
  await page.click('#copy');
  /* A document() that THROWS never reaches the clipboard; that is a defect of
     the page, reported as one, not a gate crash. */
  try {
    await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  } catch (e) { return ''; }
  return page.evaluate(() => window.__copied);
}

/* ONE BANNED-WORD PASS OVER THE BLOCK'S OWN OPTIONS. The chips describe a place,
 * a clock and a pair of hands. The moment one of them carries a tonnage, a reach,
 * a price or a manufacturer, this stops being logistics and becomes a spec we do
 * not have (§SAFETY, and the liability skeptic's first trap). */
const BANNED = /\b(\d+\s?(ton|lb|lbs|kg|ft-?lb)|capacity|rated|rating|reach of|\$|price|priced|quote)\b/i;

/* THE PAPERWORK AXIS HANDS THE PROCESS BACK (v2, 2026-08-19). A chip that says
 * "COI on file" is a tick that sounds satisfied — the exact pattern
 * getting-in.mjs bans one level up: this page has no channel back and can never
 * know a certificate is on file or a carrier is approved. So any paperwork chip
 * carrying a status word must be an ASK aimed at the supply house ("tell me …"),
 * and no chip anywhere on the block may claim a thing was granted. */
const STATUS = /\b(on file|approved|cleared|confirmed|booked|scheduled|granted|done|handled|coordinated|in place|signed off)\b/i;
const HANDBACK = /\b(tell me|tell us|send me|who.s)\b/i;
const NEVER = /\b(confirmed|booked|scheduled|granted|coordinated|signed off)\b/i;

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

/* A bare URL argument drives the DEPLOYED site instead of the working tree:
 *   node tools/toolkit-gates/dropoff-block.mjs https://mrdirno.github.io/nested-resonance-memory-archive
 * Which pages mount the block is still read off disk — the artifact is the repo. */
const LIVE = (process.argv.slice(2).find(a => /^https?:\/\//.test(a)) || '').replace(/\/$/, '');
const { s, port } = await serve();
const BASE = LIVE || `http://127.0.0.1:${port}`;
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no page mounts shared/dropoff.js'); process.exit(1); }

for (const rel of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`${BASE}/${rel}`, { waitUntil: 'load' });
  await page.waitForSelector('#dropoff', { state: 'attached' });

  /* the banned-word pass, off what actually rendered */
  const opts = await page.$$eval('#dropoff .do-chip', els => els.map(e => e.textContent.trim()));
  for (const o of opts) if (BANNED.test(o)) fail(rel, `the drop-off chip "${o}" carries a rating, a capacity or a price`);
  for (const o of opts) if (NEVER.test(o)) fail(rel, `the drop-off chip "${o}" claims something was granted — this page has no channel back`);
  if (opts.length < 8) fail(rel, `only ${opts.length} drop-off chips rendered — the block did not mount`);
  const paper = await page.$$eval('#dropoff .do-chips[data-ax="paper"] .do-chip', els => els.map(e => e.textContent.trim()));
  if (paper.length < 3) fail(rel, `the paperwork axis rendered ${paper.length} chip(s) — the v2 block did not mount`);
  for (const o of paper) {
    const st = o.search(STATUS), hb = o.search(HANDBACK);
    /* ask FIRST: "COI on file — tell me if it isn't" skims as "COI on file" */
    if (st >= 0 && (hb < 0 || hb > st)) fail(rel, `paperwork chip "${o}" reads as a state before it asks the supply house for anything`);
  }
  if (!(await page.$('#dropoff textarea'))) fail(rel, 'the gate line is not a textarea — the four-clause sentence the chips cannot carry has nowhere to wrap');

  /* find the mode control that reveals it: tap each seg button, then walk each
   * header <select> (the engine-driven order pages reveal it off `fHow`), until
   * it is on — and remember how, because the other half of the test has to turn
   * it back OFF the same way. */
  const isOn = () => page.$eval('#dropoff', el => el.classList.contains('on'));
  async function drive(want) {
    if ((await isOn()) === want) return true;
    for (const b of await page.$$('.seg button')) {
      await b.click();
      if ((await isOn()) === want) return true;
    }
    const sels = await page.$$eval('select[id^="f"]', els => els.filter(e => /^f[A-Z]/.test(e.id) && !(document.getElementById('list') || {contains: () => false}).contains(e)).map(e => ({ id: e.id, opts: [...e.options].map(o => o.value) })));
    for (const sel of sels) {
      for (const v of sel.opts) {
        await page.selectOption('#' + sel.id, v);
        if ((await isOn()) === want) return true;
      }
    }
    return (await isOn()) === want;
  }
  /* ONE LINE ON THE LIST FIRST (the rule jobcard-scope.mjs wrote down): the
   * engine-driven order pages short-circuit their whole document to "(nothing
   * on it yet)" when nothing is ticked, which drops the footer the block prints
   * in. Copying an empty list and calling the block absent is the gate lying. */
  await page.evaluate(() => {
    const t = document.querySelector('#list .item .tick');
    if (t && !t.checked) { t.checked = true; t.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  const shown = await drive(true);
  if (!shown) { fail(rel, 'no control on the page ever reveals the drop-off block — it is mounted and unreachable'); await ctx.close(); continue; }

  /* fill it the way a foreman does: chips first, then the three text answers */
  const picked = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('#dropoff .do-chips').forEach(box => {
      const c = box.querySelector('.do-chip');
      if (c) { c.click(); out.push(c.getAttribute('data-v')); }
      /* the one multi row gets a SECOND tick: both must print, joined, and a
         pick-one row must still hold exactly one */
      if (box.getAttribute('data-multi')) {
        const d = box.querySelectorAll('.do-chip')[1];
        if (d) { d.click(); out.push(d.getAttribute('data-v')); }
      }
    });
    return out;
  });
  const litPerBox = await page.$$eval('#dropoff .do-chips', boxes => boxes.map(b => ({ multi: !!b.getAttribute('data-multi'), on: b.querySelectorAll('.do-chip.on').length })));
  for (const b of litPerBox) {
    if (b.multi && b.on !== 2) fail(rel, `the multi-select row holds ${b.on} lit chip(s) after two taps — it is not multi-select`);
    if (!b.multi && b.on !== 1) fail(rel, `a pick-one row holds ${b.on} lit chip(s) after one tap`);
  }
  const typed = { 'do-nb': '07:00', 'do-gate': 'ZGATEZ 4 off Cedar code 1180', 'do-meet': 'ZMEETZ 209-555-0166', 'do-sign': 'ZSIGNZ 209-555-0188' };
  for (const [id, v] of Object.entries(typed)) {
    await page.evaluate(({ id, v }) => {
      const el = document.getElementById(id);
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }, { id, v });
  }

  let doc = await copied(page);
  if (!doc) fail(rel, 'the Copy button never put text on the clipboard — the page\'s document() threw or copy is unwired');
  for (const v of picked) if (!doc.includes(v)) fail(rel, `the chip "${v}" is ticked and is not in the sent document`);
  for (const v of Object.values(typed)) {
    const needle = v === '07:00' ? '07:00' : v;
    if (!doc.includes(needle)) fail(rel, `"${needle}" was typed into the drop-off block and is not in the sent document`);
  }
  if (!/not a booking/i.test(doc)) fail(rel, 'the drop-off block is in the document without the line that says it is an ask and not a booking');
  /* DRIVER FIRST, ONE CLOCK (v2 rules 5 and 6): the gate line carries the
     not-before clock and opens the block; the call line and the paperwork come
     before the place; "When:" never carries a time. */
  const blk = doc.slice(doc.indexOf('HOW IT GETS IN'));
  const at = re => { const m = blk.match(re); return m ? m.index : -1; };
  const iGate = at(/^- Getting in: /m), iCall = at(/^- Gate's wrong or nobody's there — call: /m), iPaper = at(/^- Before the gate: /m),
        iPlace = at(/^- (Set it|Who takes it): /m), iSign = at(/^- Signs for it/m), iWhen = at(/^- When: /m);
  if (iGate < 0) fail(rel, 'no "Getting in:" line in the block');
  else if (!/^- Getting in: .*not before 07:00/m.test(blk)) fail(rel, 'the not-before clock is not printed on the gate line — two clocks for one fact');
  if (iCall < 0 || iCall < iGate) fail(rel, 'the "call if the gate\'s wrong" line is missing or printed before the gate line');
  if (iPaper < 0 || iPaper < iCall || (iPlace >= 0 && iPaper > iPlace)) fail(rel, 'the paperwork line is missing or not printed between the call line and the place');
  if (iSign >= 0 && iWhen >= 0 && iWhen < iSign) fail(rel, 'the dispatch window is printed above who signs — driver lines come first');
  if (/^- When: .*\d{1,2}:\d{2}/m.test(blk)) fail(rel, 'the "When:" line carries a clock — the not-before control is the only clock');
  const paperLine = (blk.match(/^- Before the gate: (.*)$/m) || [])[1] || '';
  if (!paperLine.includes(' · ')) fail(rel, `two paperwork chips were ticked and the printed line is "${paperLine}" — not joined`);

  /* the other half of the mode: it must leave the document entirely — UNLESS
   * the page declares, in its source, that a truck is always coming
   * (`drop.show(true)`: the lumber load, the yard call — there is no will-call
   * to hide behind). Omission still fails; the claim has to be in the diff. */
  const alwaysOn = /drop\.show\(true\)/.test(readFileSync(join(ROOT, rel), 'utf8'));
  if (alwaysOn) {
    if (!(await isOn())) fail(rel, 'declares drop.show(true) and the block is not on');
  } else {
    if (!await drive(false)) fail(rel, 'no control on the page ever HIDES the drop-off block — a will-call would carry gate codes');
    doc = await copied(page);
    for (const v of Object.values(typed)) {
      if (doc.includes(v)) fail(rel, `"${v}" is a delivery answer and is still in the document after switching off delivery`);
    }
  }

  /* it survives the job: real reload, then back into the delivery mode */
  await page.waitForTimeout(700);
  await page.reload({ waitUntil: 'load' });
  await page.waitForSelector('#dropoff', { state: 'attached' });
  const back = await page.evaluate(() => ({
    gate: (document.getElementById('do-gate') || {}).value,
    meet: (document.getElementById('do-meet') || {}).value,
    on: document.querySelectorAll('#dropoff .do-chip.on').length,
  }));
  if (back.gate !== typed['do-gate']) fail(rel, `the gate line did not survive a reload (came back ${JSON.stringify(back.gate)})`);
  if (back.meet !== typed['do-meet']) fail(rel, 'who is meeting the truck did not survive a reload');
  if (back.on !== picked.length) fail(rel, `${picked.length} chip(s) were ticked and ${back.on} came back after a reload`);

  console.log(` ${rel}  ${opts.length} chips, ${picked.length} axes, block ${alwaysOn ? 'always on (declared)' : 'in and out of the document'}`);
  await ctx.close();

  /* ── THE SEED (v2 rule 9) — only on a page that REPLACED its old boxes ────
   * The page declares `carry: ["fAccess", "fSigner"]` on its job card: the two
   * boxes left the page and the block took their place. A phone that typed a
   * gate code into the old textarea in June must see it on the block's gate
   * line the first morning — and a man who then CLEARS the block must not get
   * it back on reload. Driven against both storage shapes the card reads: the
   * card's own store, and the pre-card legacy key it adopts. */
  const src = readFileSync(join(ROOT, rel), 'utf8');
  const carry = (src.match(/carry:\s*\[([^\]]*)\]/) || [])[1];
  if (!carry) continue;
  const trade = (src.match(/trade:\s*"([^"]+)"/) || [])[1];
  const legacyKey = (src.match(/legacyKey:\s*"([^"]+)"/) || [])[1];
  const dkey = (src.match(/var DKEY = "([^"]+)"/) || [])[1];
  if (!trade || !dkey) { fail(rel, 'declares carry: but no trade / DKEY could be read from the source — the seed cannot be exercised'); continue; }
  const GATE = 'ZJUNEGATEZ off Elm, code 4411', SIGN = 'ZJUNESIGNZ 209-555-0101', MEET = 'ZJUNEMEETZ 209-555-0102';
  const carriesMeet = /fMeet/.test(carry);
  for (const shape of ['card', 'legacy']) {
    if (shape === 'legacy' && !legacyKey) continue;
    const c2 = await browser.newContext({ viewport: { width: 390, height: 780 } });
    await c2.addInitScript(STUB);
    await c2.addInitScript(({ shape, trade, legacyKey, GATE, SIGN, MEET }) => {
      if (shape === 'card') {
        localStorage.setItem(`toolkit.${trade}.jobcard.v1`, JSON.stringify({ v: 1, seq: 1, cur: 'j1', device: {},
          jobs: [{ id: 'j1', name: 'June job', at: 1, f: { fAccess: GATE, fSigner: SIGN, fMeet: MEET, fPO: '24-118' } }] }));
      } else {
        localStorage.setItem(legacyKey, JSON.stringify({ fJob: 'June job', fAccess: GATE, fSigner: SIGN, fMeet: MEET, fPO: '24-118' }));
      }
    }, { shape, trade, legacyKey, GATE, SIGN, MEET });
    const pg = await c2.newPage();
    await pg.goto(`${BASE}/${rel}`, { waitUntil: 'load' });
    await pg.waitForSelector('#dropoff', { state: 'attached' });
    const got = await pg.evaluate(() => ({ gate: (document.getElementById('do-gate') || {}).value, sign: (document.getElementById('do-sign') || {}).value, meet: (document.getElementById('do-meet') || {}).value }));
    if (got.gate !== GATE) fail(rel, `[${shape}] the gate code typed into the old box did not reach the block (gate reads ${JSON.stringify(got.gate)})`);
    if (got.sign !== SIGN) fail(rel, `[${shape}] the old signer did not reach the block (reads ${JSON.stringify(got.sign)})`);
    if (carriesMeet && got.meet !== MEET) fail(rel, `[${shape}] "who's meeting the truck" left the grid and did not reach the block (reads ${JSON.stringify(got.meet)})`);
    if (!carriesMeet && got.meet) fail(rel, `[${shape}] the block's meet field was seeded from nowhere (reads ${JSON.stringify(got.meet)})`);
    /* and it is in the document, through the replace */
    await pg.evaluate(() => { const t = document.querySelector('#list .item .tick'); if (t && !t.checked) { t.checked = true; t.dispatchEvent(new Event('change', { bubbles: true })); } });
    const onNow = () => pg.$eval('#dropoff', el => el.classList.contains('on'));
    if (!(await onNow())) {
      for (const b of await pg.$$('.seg button')) { await b.click(); if (await onNow()) break; }
    }
    if (!(await onNow())) {
      const sel = await pg.$$eval('select[id^="f"]', els => els.filter(e => /^f[A-Z]/.test(e.id)).map(e => ({ id: e.id, opts: [...e.options].map(o => o.value) })));
      outer: for (const sl of sel) for (const v of sl.opts) {
        try { await pg.selectOption('#' + sl.id, v, { timeout: 1500 }); } catch (e) { continue outer; }
        if (await onNow()) break outer;
      }
    }
    if (!(await onNow())) fail(rel, `[${shape}] could not reveal the block to read the seeded document`);
    const d1 = await copied(pg);
    if (!d1.includes(GATE)) fail(rel, `[${shape}] the seeded gate code is on the glass and not in the sent document`);
    if (carriesMeet && !d1.includes(MEET)) fail(rel, `[${shape}] the seeded "who's meeting" number is not in the sent document`);
    if ((d1.match(/Meeting the truck:/g) || []).length) fail(rel, `[${shape}] the old "Meeting the truck:" line still prints beside the block's call line`);
    if ((d1.match(new RegExp('Signs for it if I\'m not there', 'g')) || []).length > 1) fail(rel, `[${shape}] "Signs for it" printed twice — the old line and the block both print`);
    /* clear, reload: it must NOT come back (the drawer the block lives in may be
       closed; open it the way a thumb would, then tap the real button) */
    await pg.evaluate(() => { document.querySelectorAll('details').forEach(d => { d.open = true; }); });
    await pg.click('#do-clr');
    await pg.waitForTimeout(300);
    await pg.reload({ waitUntil: 'load' });
    await pg.waitForSelector('#dropoff', { state: 'attached' });
    const back = await pg.evaluate(() => (document.getElementById('do-gate') || {}).value);
    if (back) fail(rel, `[${shape}] the block was cleared and the old gate code came back on reload (${JSON.stringify(back)}) — the seed must run once`);
    await c2.close();
  }
  console.log(` ${rel}  seed: old boxes → block, in the document once, cleared stays cleared (card${legacyKey ? ' + legacy' : ''})`);
}

await browser.close();
s.close();

if (fails.length) {
  console.error(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`\nOK${LIVE ? ' (LIVE ' + LIVE + ')' : ''} — ${list.length} page(s) carry a drop-off block that shows where it belongs, prints what he ticked, and survives the job.`);
