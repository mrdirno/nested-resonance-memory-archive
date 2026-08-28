/**
 * WHAT CAME BACK — the access answer records what we were told and never a permit.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * `shared/whatcameback.js` is the return leg of the one boundary where the
 * receiver can leave a crew standing at a locked door. It is mounted as an INTAKE
 * on every trade's `getting-in.html`, and its rows are not configured anywhere —
 * they ARE that page's live ticks. Three things can go wrong with it and only one
 * is the ordinary kind.
 *
 * THE KIND THAT MATTERS MOST — AN AFFIRMATIVE REACHING A PERMIT. The ask side was
 * built so no tick can claim a permit was satisfied; `getting-in.mjs` bans the
 * words outright. An ANSWER layer is where that discipline dies quietly, because
 * its whole job is to record a yes. So the rule is asserted mechanically: every
 * heads-up line naming a permitted activity is driven through its ENTIRE ladder,
 * every rung it can wear is collected, and not one of them may be an affirmative
 * — and the brief built on top of them may not contain an approval word anywhere.
 * A future cycle giving the flagged list a "got it" rung to make it consistent
 * with the other list would look like a tidy-up and would be the defect.
 *
 * AND THE TWO REGEXES MUST AGREE. The module carries its own copy of the
 * permitted-activity test rather than importing one, deliberately — the ask page
 * has to run with or without the module, and a rule that lives only in the
 * optional half silently stops applying when that half is absent. A duplicated
 * constant is a promise, so it is checked here character for character against
 * the one `getting-in.mjs` already enforces.
 *
 * THE ORDINARY KIND — an answer on the glass that never reaches the message, the
 * same class every order page and the ask itself were caught on. Everything is
 * set and then looked for BY VALUE in what the real Copy buttons put on the
 * clipboard.
 *
 * AND SILENCE HAS TO BE LOUD. The single output nobody else can compute is what
 * they never answered, and it is the reason to open this at all: an untapped row
 * is not a no and not a yes, and it must appear in the gap block, in the on-page
 * banner, and in the day-of check.
 *
 *   node tools/toolkit-gates/what-came-back.mjs
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
  for (const t of trades) if (existsSync(join(ROOT, t, 'getting-in.html'))) out.push(t);
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
  window.confirm = () => true;
};

/* THE WORDS THAT WOULD TURN A RECORD INTO A GRANT. Identical in spirit to the ask
   side's list; "approved/granted" is not softened here just because this document
   is downstream of a real answer — the man reading it on a lock screen at 5:50am
   cannot tell our summary from the building's own paperwork, and that is exactly
   the confusion the whole handback rule exists to prevent. */
const BANNED = [
  [/\b(permit (obtained|pulled|in hand|on file|issued)|permitted and|already permitted)\b/i, 'claims a permit was obtained — nothing here can know that'],
  [/\b(approved|authoriz(ed|ation)|cleared for|clearance granted|granted)\b/i, 'reads as a grant; this page records what somebody said, it does not grant anything'],
  [/\bfire watch (arranged|in place|covered|provided|set)\b/i, 'a fire watch is the building\'s determination, never ours to declare'],
  [/\b(lockout|tagout|loto)\b/i, 'an execution procedure with joint signatures is not a row on a brief'],
  [/\bconfined space\b/i, 'confined space entry is a permit with atmospheric records'],
  [/\b(request|reference|permit) ?#|\bticket ?#/i, 'a generated reference number impersonates a numbering authority'],
  [/\b(date of birth|dob|social security|ssn|badge number)\b/i, 'personal identifiers do not belong on a client-side page'],
  [/\b(\d+\s?(ton|lb|lbs|kg)|\$\d|\bprice[d]?\b|\bquote[d]?\b)/i, 'a rating or a price is a spec we do not have'],
];

/* An affirmative on a flagged line is the kill condition. These are the shapes a
   rung would have to take to become one. */
const AFFIRMATIVE = /\b(got it|yes|ok(ay)?|fine|good|done|set|clear(ed)?|handled|covered|sorted|already open|approved|confirmed)\b/i;

const fails = [];
const fail = (t, m) => fails.push(`${t}  ${m}`);
let checks = 0;
const ck = () => { checks++; };

/* ── 1. THE TWO REGEXES AGREE, off disk, before a browser is launched ───────── */
function permittedSrc(file) {
  const s = readFileSync(join(ROOT, file), 'utf8');
  const m = s.match(/const PERMITTED = (\/[^\n]*?\/i);|var PERMITTED = (\/[^\n]*?\/i);/);
  return m ? (m[1] || m[2]) : null;
}
{
  const a = permittedSrc('tools/toolkit-gates/getting-in.mjs');
  const b = permittedSrc('shared/whatcameback.js');
  ck();
  if (!a || !b) fail('(source)', `could not read the PERMITTED test out of ${!a ? 'getting-in.mjs' : 'whatcameback.js'} — the duplicated-constant promise cannot be checked`);
  else if (a !== b) fail('(source)', `the permitted-activity test has DRIFTED between the ask gate and the answer module:\n      getting-in.mjs   ${a}\n      whatcameback.js  ${b}\n      one of them now classifies a line the other does not, and the affirmative-free ladder is the thing that stops applying`);
}

/* The driver uses the module's OWN test, parsed off disk — never a third copy.
   A gate carrying its own hardcoded duplicate of the rule it is checking is how
   this very gate spent its first run reporting two trades as untestable while the
   module classified their lines correctly. */
const PERMITTED = (() => {
  const src = permittedSrc('shared/whatcameback.js');
  if (!src) return /$^/;
  const body = src.slice(1, src.lastIndexOf('/'));
  return new RegExp(body, 'i');
})();

const { s, port } = await serve();
const browser = await chromium.launch();
const trades = pages();
if (!trades.length) { console.error('no trade ships getting-in.html'); process.exit(1); }

for (const t of trades) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto(`http://127.0.0.1:${port}/${t}/getting-in.html`, { waitUntil: 'load' });

  ck();
  const mounted = await page.$('#wcbCard');
  if (!mounted) { fail(t, 'the answer layer never mounted — the ask ships with no return leg on this trade'); await ctx.close(); continue; }

  /* ---- 2. DRIVE THE ASK, the way the foreman does before he sends it ------- */
  await page.fill('[data-f="day"] input', '2026-08-22');
  await page.fill('[data-f="window"] input', '6pm - 2am');
  await page.fill('[data-f="site"] input', 'Bishop Ranch 3');
  await page.fill('[data-f="count"] input', '3');

  const needNames = await page.$$eval('[data-f="need"] li .nm', e => e.map(x => x.textContent));
  const headNames = await page.$$eval('[data-f="heads"] li .nm', e => e.map(x => x.textContent));

  /* Tick three logistics asks and, on the heads list, one permitted line and one
     ordinary one — the pair is the whole point, because they must not behave the
     same way. */
  const needPick = [0, 1, 2].filter(i => i < needNames.length);
  const permIdx = headNames.findIndex(n => PERMITTED.test(n));
  const plainIdx = headNames.findIndex(n => !PERMITTED.test(n));
  ck();
  if (permIdx < 0) fail(t, 'no heads-up option on this trade names a permitted activity — the affirmative-free ladder is untested here, which means it is unasserted');
  const headPick = [permIdx, plainIdx].filter(i => i >= 0);

  const needBoxes = await page.$$('[data-f="need"] li input');
  for (const i of needPick) await needBoxes[i].click();
  const headBoxes = await page.$$('[data-f="heads"] li input');
  for (const i of headPick) await headBoxes[i].click();
  await page.waitForTimeout(180);

  /* ---- 3. THE ROWS ARE THE ASK, not a second copy of it ------------------- */
  const rowNames = list => page.$$eval(list + ' li .wcb-nm', e => e.map(x => x.firstChild.textContent));
  const gotNeed = await rowNames('#wcbNeed');
  const gotHead = await rowNames('#wcbHead');
  ck();
  for (const i of needPick) if (!gotNeed.includes(needNames[i])) fail(t, `ticked "${needNames[i]}" on the ask and it never became a row to answer`);
  for (const i of headPick) if (!gotHead.includes(headNames[i])) fail(t, `flagged "${headNames[i]}" on the ask and it never became a row to answer`);
  ck();
  if (gotNeed.length !== needPick.length) fail(t, `answered rows (${gotNeed.length}) do not track the ticks (${needPick.length}) — the list has its own copy of the ask`);

  /* Untick one and it must GO. An answer to a question no longer being asked is
     the second version of the truth this module exists to refuse. */
  await needBoxes[needPick[needPick.length - 1]].click();
  await page.waitForTimeout(180);
  ck();
  const afterUntick = await rowNames('#wcbNeed');
  if (afterUntick.includes(needNames[needPick[needPick.length - 1]]))
    fail(t, 'unticking an ask left its answer row behind — the answer list is a copy, not the ask');
  await needBoxes[needPick[needPick.length - 1]].click();
  await page.waitForTimeout(180);

  /* ---- 4. THE LADDERS, and the one that may never say yes ------------------ */
  async function cycle(listSel, name) {
    const seen = [];
    for (let k = 0; k < 8; k++) {
      const lis = await page.$$(listSel + ' li');
      let li = null;
      for (const x of lis) {
        const n = await x.evaluate(e => e.querySelector('.wcb-nm').firstChild.textContent);
        if (n === name) { li = x; break; }
      }
      if (!li) return seen;
      const chip = await li.$eval('.wcb-chip', e => e.textContent.trim());
      if (seen.length && chip === seen[0]) return seen;  // wrapped
      seen.push(chip);
      await li.$eval('.wcb-row', e => e.click());
      await page.waitForTimeout(70);
    }
    return seen;
  }
  async function setRung(listSel, name, label) {
    for (let k = 0; k < 8; k++) {
      const lis = await page.$$(listSel + ' li');
      let li = null;
      for (const x of lis) {
        const n = await x.evaluate(e => e.querySelector('.wcb-nm').firstChild.textContent);
        if (n === name) { li = x; break; }
      }
      if (!li) return false;
      const chip = await li.$eval('.wcb-chip', e => e.textContent.trim());
      if (chip === label) return true;
      await li.$eval('.wcb-row', e => e.click());
      await page.waitForTimeout(70);
    }
    return false;
  }

  if (permIdx >= 0) {
    const rungs = await cycle('#wcbHead', headNames[permIdx]);
    ck();
    for (const r of rungs) {
      if (/nothing said/i.test(r)) continue;
      if (AFFIRMATIVE.test(r))
        fail(t, `THE PERMIT RULE IS BROKEN: "${headNames[permIdx]}" can be answered "${r}". A permitted activity has no affirmative rung — the most this page may ever record is who owns the process.`);
    }
    ck();
    if (rungs.length > 3) fail(t, `the flagged ladder has ${rungs.length - 1} rungs beyond silence (${JSON.stringify(rungs)}) — it is drifting toward the logistics ladder`);
  }
  if (plainIdx >= 0) {
    const rungs = await cycle('#wcbHead', headNames[plainIdx]);
    ck();
    if (rungs.length < 3) fail(t, `an ordinary heads-up line "${headNames[plainIdx]}" only offers ${JSON.stringify(rungs)} — it is wearing the permit ladder it does not need`);
  }
  {
    const rungs = await cycle('#wcbNeed', gotNeed[0]);
    ck();
    if (rungs.length !== 5) fail(t, `the logistics ladder on "${gotNeed[0]}" is ${JSON.stringify(rungs)} — expected silence plus four answers, wrapping back to silence`);
    ck();
    if (!/nothing said/i.test(rungs[0])) fail(t, `an untapped logistics row reads "${rungs[0]}" instead of nothing said — silence must be the default and it must say so`);
  }

  /* ---- 5. SET A REAL ANSWER AND READ THE BRIEF ---------------------------- */
  const V = {
    win: '6 to 11', who: 'Manny - front desk', cell: '415-555-0177',
    by: 'Diane - building engineer', on: '2026-08-18',
  };
  await page.fill('#wcbWin', V.win);
  await page.fill('#wcbWho', V.who);
  await page.fill('#wcbCell', V.cell);
  await page.fill('#wcbBy', V.by);
  await page.fill('#wcbOn', V.on);

  const answeredRow = gotNeed[0], detail = 'badge works after 6';
  ck();
  if (!await setRung('#wcbNeed', answeredRow, 'Got it')) fail(t, `could not reach "Got it" on "${answeredRow}"`);
  await page.$$eval('#wcbNeed li', (lis, args) => {
    for (const li of lis) {
      if (li.querySelector('.wcb-nm').firstChild.textContent !== args[0]) continue;
      const f = li.querySelector('.wcb-said');
      if (f) { f.value = args[1]; f.dispatchEvent(new Event('input', { bubbles: true })); }
    }
  }, [answeredRow, detail]);

  const routed = permIdx >= 0 ? headNames[permIdx] : null, who2 = 'Jim at Summit Alarm 415-555-0190';
  if (routed) {
    ck();
    if (!await setRung('#wcbHead', routed, 'They named who owns it')) fail(t, `could not reach the routing rung on "${routed}"`);
    await page.$$eval('#wcbHead li', (lis, args) => {
      for (const li of lis) {
        if (li.querySelector('.wcb-nm').firstChild.textContent !== args[0]) continue;
        const f = li.querySelector('.wcb-said');
        if (f) { f.value = args[1]; f.dispatchEvent(new Event('input', { bubbles: true })); }
      }
    }, [routed, who2]);
  }
  await page.waitForTimeout(160);

  const copy = async sel => {
    await page.evaluate(() => { window.__copied = null; });
    await page.click(sel);
    await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
    return page.evaluate(() => window.__copied);
  };
  const brief = await copy('#wcbCopy');

  /* Every answer on the glass is in the message. */
  ck();
  for (const [k, v] of Object.entries(V)) {
    if (k === 'on') continue;   // printed as a formatted date, checked below
    if (!brief.includes(v)) fail(t, `"${v}" (${k}) is on the glass and NOT in the brief`);
  }
  ck();
  if (!brief.includes(detail)) fail(t, `the detail typed against "${answeredRow}" never reached the brief`);
  if (routed) { ck(); if (!brief.includes(who2)) fail(t, `the name we were told to call on "${routed}" never reached the brief`); }

  /* THE WINDOW THEY GAVE, printed against the one we asked for. Both lenses put
     this above everything else on the page. */
  ck();
  if (!/we asked for 6pm - 2am/i.test(brief))
    fail(t, 'the brief carries the window they gave without the one we asked for — a narrowed window nobody spelled out is the most expensive line on this page');

  /* SILENCE IS LOUD. Two rows were left untapped; both must be named. */
  const silentRows = [gotNeed[1], gotNeed[2]].filter(Boolean).filter(n => n !== answeredRow);
  ck();
  if (!/NOTHING SAID ABOUT THESE/.test(brief)) fail(t, 'the brief has no gap block — what they never answered is the only output nobody else can compute');
  for (const n of silentRows) { ck(); if (!brief.includes(n)) fail(t, `"${n}" was never answered and the brief does not say so`); }
  ck();
  if (!/Silence is not a yes/i.test(brief)) fail(t, 'the gap block never says silence is not a yes — that sentence is the whole finding');

  /* THE FLAGGED BLOCK NEVER READS AS A GRANT. */
  if (routed) {
    ck();
    if (!/STILL ON THEIR PROCESS/.test(brief)) fail(t, 'a flagged line was answered and the brief has no "still on their process" block');
    ck();
    if (!/is a permit/i.test(brief)) fail(t, 'the flagged block never says nothing on it is a permit');
  }

  /* STALENESS — the answer predates the night by four days. */
  ck();
  if (!/4 days older than the night/i.test(brief)) fail(t, 'the brief does not say how much older than the night the answer is');
  ck();
  const staleBanner = await page.$('#wcbStale .wcb-stale');
  if (!staleBanner) fail(t, 'the on-page staleness banner never rendered for a four-day-old answer');

  /* THE DAY-OF CHECK is a different document and it carries the gaps. */
  const recheck = await copy('#wcbRe');
  ck();
  if (recheck === brief) fail(t, 'the day-of check is the same text as the brief — one goes to the crew, the other to the building');
  for (const n of silentRows) { ck(); if (!recheck.includes(n)) fail(t, `the day-of check does not carry the still-open "${n}"`); }
  ck();
  if (recheck.length > brief.length) fail(t, 'the day-of check is longer than the brief — it is answered from a lock screen or it is not answered');

  /* ---- 6. NOTHING ANYWHERE READS AS A GRANT ------------------------------- */
  for (const doc of [brief, recheck]) {
    for (const [re, why] of BANNED) {
      ck();
      if (re.test(doc)) fail(t, `the document carries banned content (${JSON.stringify((doc.match(re) || [])[0])}) — ${why}`);
    }
  }

  /* ---- 7. MOBILE-WATERTIGHT with the layer open and populated ------------- */
  for (const w of [320, 360, 390, 430]) {
    await page.setViewportSize({ width: w, height: 780 });
    await page.waitForTimeout(120);
    ck();
    const o = await page.evaluate(() => ({ s: document.documentElement.scrollWidth, c: document.documentElement.clientWidth }));
    if (o.s > o.c) fail(t, `horizontal overflow at ${w}px with the answer layer populated: scrollWidth ${o.s} > clientWidth ${o.c}`);
  }
  await page.setViewportSize({ width: 390, height: 780 });
  await page.waitForTimeout(100);
  ck();
  const small = await page.$$eval('#wcbCard button, #wcbCard input, #wcbCard textarea', els =>
    els.filter(e => e.offsetParent !== null).map(e => ({ t: (e.textContent || e.id || e.type).slice(0, 40), h: Math.round(e.getBoundingClientRect().height) }))
      .filter(x => x.h < 44));
  for (const x of small) fail(t, `tap target "${x.t}" is ${x.h}px — under the 44px floor for a thumb in a glove`);

  ck();
  if (errs.length) fail(t, `page errors: ${errs.join(' | ')}`);
  await ctx.close();
}

await browser.close();
s.close();

if (fails.length) {
  console.error('WHAT CAME BACK — FAILURES:\n' + fails.map(f => '  ' + f).join('\n'));
  process.exit(1);
}
console.log(`WHAT CAME BACK — ${trades.length} page(s) clean, ${checks} checks: silence is named, no permit ever gets a yes, every answer reaches the brief.`);
