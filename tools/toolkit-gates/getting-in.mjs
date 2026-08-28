/**
 * GETTING IN — the access ask does the job it claims, on every trade that ships it.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * This page crosses the one boundary in the program where the receiver can leave
 * a crew standing at a locked door, and it is the first one aimed at a party that
 * is not another trade. Two things can go wrong with it, and only one of them is
 * the ordinary kind.
 *
 * THE ORDINARY KIND — an answer he gives that never reaches the message. Same
 * class the order pages were caught on: the control is on the glass, it lights
 * up, and the block labelled "what you send" does not carry it. So every field is
 * set and then looked for BY VALUE in what the real Copy button puts on the
 * clipboard, and the heading is checked separately because the heading is the
 * only part of this document most receivers ever read.
 *
 * THE KIND THAT MATTERS MORE — a heads-up tick quietly becoming a STATUS. Hot
 * work, a sprinkler head, the fire panel, a power-down: each of those is a permit
 * the building owns and NUMBERS, and the whole reason this page survived its own
 * kill review is that none of its ticks claims one was obtained. They hand the
 * process back by name. A later cycle rewriting "tell me who puts the panel on
 * test — we don't" into "fire alarm coordinated" would look like a tidy-up and
 * would be the defect. So the handback is asserted as a RULE: any option naming a
 * permitted activity must end in a question aimed at the man who owns it, and the
 * words that make a permit sound satisfied are banned outright — as are
 * lockout/tagout and confined space, which are execution procedures with joint
 * signatures and have no business being a checkbox anywhere.
 *
 * AND THE PII FLOOR. Names are optional and they are the one thing Clear wipes.
 * There is no field for a date of birth, an ID number or a badge number, and the
 * document only spends a line saying so when names are actually on it.
 *
 *   node tools/toolkit-gates/getting-in.mjs
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
  for (const t of trades) if (existsSync(join(ROOT, t, 'getting-in.html'))) out.push(`${t}/getting-in.html`);
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
async function copied(page) {
  await page.evaluate(() => { window.__copied = null; });
  await page.click('#copy');
  await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__copied);
}

/* A PERMIT IS NEVER SATISFIED BY A CHECKBOX. These are the words that would make
   one of these ticks read as a state instead of an ask, plus the two procedures
   that must not appear at all, plus the usual spec/price/brand floor (§SAFETY). */
const BANNED = [
  [/\b(lockout|tagout|loto)\b/i, 'lockout/tagout is an execution procedure with joint signatures, not a tick'],
  [/\bconfined space\b/i, 'confined space entry is a permit with atmospheric records, not a tick'],
  [/\bfire watch (arranged|in place|covered|provided)\b/i, 'a fire watch is the building\'s determination, never ours to declare'],
  [/\b(permit (obtained|pulled|in hand|on file)|permitted and|already permitted)\b/i, 'this claims a permit was obtained — the page has no way to know'],
  [/\b(approved|confirmed|booked|scheduled|granted)\b/i, 'this page has no channel back and can never know an ask was granted'],
  [/\b(request|reference|permit) ?#|\bticket ?#/i, 'a generated reference number impersonates a numbering authority'],
  [/\b(date of birth|dob|social security|ssn|driver.s licen[cs]e|badge number)\b/i, 'personal identifiers do not belong on a client-side page'],
  [/\b(\d+\s?(ton|lb|lbs|kg)|capacity|rated|rating|\$|price|priced|quote)\b/i, 'a rating, a capacity or a price is a spec we do not have'],
];

/* Any option naming one of these has to hand the process back to the man who owns
   it — the sub must address HIM, not report a state of ours. */
const PERMITTED = /\b(hot work|fire alarm|sprinkler|power(ed)?[ -]?(down|off)?|torch|solder|clinical|patient|roof access|kettle|asbestos|regulated material|permit|impairment|panel on test|valve|closure)\b/i;
const HANDBACK = /\b(tell me|tell us|your |you want|who |how you)/i;

const fails = [];
const perms = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

const { s, port } = await serve();
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no trade ships getting-in.html'); process.exit(1); }

for (const rel of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await page.waitForSelector('[data-f="need"]', { state: 'attached' });

  /* ---- 1. THE VOCABULARY, off what actually rendered ---------------------- */
  const need = await page.$$eval('[data-f="need"] li label', els => els.map(e => e.textContent.trim()));
  const heads = await page.$$eval('[data-f="heads"] li label', els => els.map(e => e.textContent.trim()));
  if (need.length < 8) fail(rel, `only ${need.length} "what we need" options rendered`);
  if (heads.length < 8) fail(rel, `only ${heads.length} heads-up options rendered`);

  for (const o of need.concat(heads))
    for (const [re, why] of BANNED)
      if (re.test(o)) fail(rel, `option "${o}" — ${why}`);

  const headOpts = await page.$$eval('[data-f="heads"] li', els => els.map(e => ({
    name: (e.querySelector('.nm') || {}).textContent || '',
    sub: (e.querySelector('.sb') || {}).textContent || '',
  })));
  /* A GATE THAT CHECKED NOTHING STILL SAID "CLEAN" (found 2026-08-28). The
     handback rule only fires on an option this regex classifies, and for two
     trades it classified none of them: flooring and sitework write their permit
     lines as "something powered down" (the \b after `power` never matches
     "powered"), "regulated material" and "who owns the closure and the permit
     for it". Both trades hand back correctly — the authors wrote them well — but
     this gate had been reporting "every permit hands back" across 15 pages while
     running ZERO handback assertions on two of them, and nothing in the output
     said so. The regex is widened; more importantly the COUNT is now printed per
     trade, because the failure was never a wrong answer, it was a silent zero. */
  let permCount = 0;
  for (const o of headOpts) {
    if (!PERMITTED.test(o.name)) continue;
    permCount++;
    if (!o.sub) { fail(rel, `heads-up "${o.name}" names a permitted activity with no handback at all`); continue; }
    if (!HANDBACK.test(o.sub)) fail(rel, `heads-up "${o.name}" → "${o.sub}" reports a state instead of handing the process back`);
  }

  /* ---- 2. DRIVE IT the way a foreman does -------------------------------- */
  const V = {
    window: '6pm - 2am', site: 'Bishop Ranch 3', room: 'IDF 3B', how: 'behind the elevator lobby',
    scope: 'pulling cable up to the penthouse', howlong: 'about 4 hours', loud: 'hammer drill 2 hrs',
    note: 'short power bump, exact window with your engineer', count: '3',
    to: 'Diane - building engineer', me: 'Mike R - 415-555-0134', co: 'Bayline Integration',
  };
  const set = async (f, v) => { await page.fill(`[data-f="${f}"] input`, v); };
  await page.fill('[data-f="day"] input', '2026-08-22');
  for (const f of ['window', 'site', 'scope', 'howlong', 'loud', 'count', 'to', 'me', 'co']) await set(f, V[f]);
  await page.fill('[data-f="note"] textarea', V.note);
  await page.fill('[data-f="spaces"] .row input[aria-label="Room"]', V.room);
  await page.fill('[data-f="spaces"] .row input[aria-label="How you get to it"]', V.how);
  await page.click('[data-f="run"] .pick button');
  const runPick = await page.$eval('[data-f="run"] .pick button', b => b.textContent.trim());
  const tick = async (f, n) => {
    const boxes = await page.$$(`[data-f="${f}"] li input`);
    const on = [];
    for (let i = 0; i < Math.min(n, boxes.length); i++) { await boxes[i].click(); on.push(i); }
    return on;
  };
  await tick('need', 3);
  await tick('heads', 3);

  const doc = await copied(page);

  /* ---- 3. EVERY ANSWER REACHED THE MESSAGE ------------------------------- */
  for (const [f, v] of Object.entries(V))
    if (!doc.includes(v)) fail(rel, `"${v}" (${f}) is on the glass and NOT in the message`);
  if (!doc.includes(runPick)) fail(rel, `the "how often" pick "${runPick}" never reached the message`);

  const onNeed = await page.$$eval('[data-f="need"] li input:checked', els =>
    els.map(e => e.closest('li')).map(li => ({ nm: li.querySelector('.nm').textContent, sb: (li.querySelector('.sb') || {}).textContent || '' })));
  const onHeads = await page.$$eval('[data-f="heads"] li input:checked', els =>
    els.map(e => e.closest('li')).map(li => ({ nm: li.querySelector('.nm').textContent, sb: (li.querySelector('.sb') || {}).textContent || '' })));
  for (const o of onNeed.concat(onHeads)) {
    if (!doc.includes(o.nm)) fail(rel, `ticked "${o.nm}" is not in the message`);
    if (o.sb && !doc.includes(o.sb)) fail(rel, `the handback on "${o.nm}" ("${o.sb}") was dropped from the message — the tick shipped without its question`);
  }

  /* ---- 4. THE HEADING IS THE ASK ----------------------------------------- */
  const want = await page.evaluate(() => new Date(2026, 7, 22).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }));
  const head = doc.split('\n')[0];
  if (!head.includes(want)) fail(rel, `the first line does not carry the date ("${want}") — he triages this off a lock screen: ${JSON.stringify(head)}`);
  if (!head.includes(V.window)) fail(rel, `the first line does not carry the window: ${JSON.stringify(head)}`);
  if (!/ACCESS REQUEST/.test(head)) fail(rel, `the first line does not say what it is: ${JSON.stringify(head)}`);
  if (!doc.split('\n')[1] || !doc.split('\n')[1].includes(V.site)) fail(rel, 'the building is not on the second line');

  /* ---- 5. AN ASK, NEVER A BOOKING ---------------------------------------- */
  if (!/ask, not a booking/i.test(doc)) fail(rel, 'the ask-not-a-booking line is missing — a man can park six guys at a locked door on the strength of this');
  if (!/window you.{0,3}re actually giving us/i.test(doc)) fail(rel, 'the message never asks him to state the window he is actually granting — the grant narrows and nobody notices');

  /* ---- 6. THE PII FLOOR --------------------------------------------------- */
  if (await page.$('[data-f="crew"] input[aria-label="Name"]') === null) fail(rel, 'no crew name row at all');
  if (/no dates of birth/i.test(doc)) fail(rel, 'the names-only line prints when there are no names on the ask');
  await page.fill('[data-f="crew"] .row input[aria-label="Name"]', 'Mike Reyes');
  const doc2 = await copied(page);
  if (!doc2.includes('Mike Reyes')) fail(rel, 'a crew name is on the glass and not in the message');
  if (!/no dates of birth, no ID numbers/i.test(doc2)) fail(rel, 'names are on the ask and the message never says badging data stays in HIS system');
  for (const [re, why] of BANNED) {
    if (/approved|confirmed|booked|scheduled|granted/i.test(re.source)) continue; // "actually giving us" is our own ask, checked above
    if (re.test(doc2)) fail(rel, `the message itself carries banned content — ${why}`);
  }

  perms.push(`${rel.split('/')[0]}:${permCount}`);
  if (!permCount) fail(rel, 'NOT ONE heads-up option on this trade is classified as a permitted activity, so the handback rule ran zero assertions here. Either this kit genuinely flags nothing permitted (say so in items.js), or the classifier does not know this trade\'s words for it — which is the defect that made two trades look clean for weeks.');

  /* ---- 7. IT SURVIVES THE JOB, AND CLEAR TAKES THE NAMES ------------------ */
  await page.reload({ waitUntil: 'load' });
  await page.waitForSelector('[data-f="need"]', { state: 'attached' });
  const doc3 = await copied(page);
  for (const k of ['site', 'me', 'co', 'window', 'scope']) if (!doc3.includes(V[k])) fail(rel, `${k} did not survive a reload — a man loses this every time he takes a call`);
  if (!doc3.includes('Mike Reyes')) fail(rel, 'the crew list did not survive a reload — a draft that evaporates is worse than no draft');
  await page.click('#clear');
  await page.waitForTimeout(120);
  const doc4 = await copied(page);
  if (doc4.includes('Mike Reyes')) fail(rel, 'CLEAR left the crew names on the phone — that is the roster a lost phone hands over');
  if (!doc4.includes(V.me) || !doc4.includes(V.co)) fail(rel, 'CLEAR wiped the sender block — he has to retype his own cell every time');

  await ctx.close();
}

await browser.close();
s.close();

if (fails.length) {
  console.error(`\nGETTING IN — ${fails.length} defect(s) across ${list.length} page(s):\n`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`GETTING IN — ${list.length} page(s) clean: every answer reaches the message, every permit hands back, names clear.`);
console.log(`  permitted-activity lines actually asserted, by trade: ${perms.join(' · ')}`);
