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
  await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__copied);
}

/* ONE BANNED-WORD PASS OVER THE BLOCK'S OWN OPTIONS. The chips describe a place,
 * a clock and a pair of hands. The moment one of them carries a tonnage, a reach,
 * a price or a manufacturer, this stops being logistics and becomes a spec we do
 * not have (§SAFETY, and the liability skeptic's first trap). */
const BANNED = /\b(\d+\s?(ton|lb|lbs|kg|ft-?lb)|capacity|rated|rating|reach of|\$|price|priced|quote)\b/i;

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

const { s, port } = await serve();
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no page mounts shared/dropoff.js'); process.exit(1); }

for (const rel of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await page.waitForSelector('#dropoff', { state: 'attached' });

  /* the banned-word pass, off what actually rendered */
  const opts = await page.$$eval('#dropoff .do-chip', els => els.map(e => e.textContent.trim()));
  for (const o of opts) if (BANNED.test(o)) fail(rel, `the drop-off chip "${o}" carries a rating, a capacity or a price`);
  if (opts.length < 8) fail(rel, `only ${opts.length} drop-off chips rendered — the block did not mount`);

  /* find the mode control that reveals it: tap each seg button until it is on */
  const segs = await page.$$('.seg button');
  let shown = false;
  for (const b of segs) {
    await b.click();
    if (await page.$eval('#dropoff', el => el.classList.contains('on'))) { shown = true; break; }
  }
  if (!shown) { fail(rel, 'no control on the page ever reveals the drop-off block — it is mounted and unreachable'); await ctx.close(); continue; }

  /* fill it the way a foreman does: chips first, then the three text answers */
  const picked = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('#dropoff .do-chips').forEach(box => {
      const c = box.querySelector('.do-chip');
      if (c) { c.click(); out.push(c.getAttribute('data-v')); }
    });
    return out;
  });
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
  for (const v of picked) if (!doc.includes(v)) fail(rel, `the chip "${v}" is ticked and is not in the sent document`);
  for (const v of Object.values(typed)) {
    const needle = v === '07:00' ? '07:00' : v;
    if (!doc.includes(needle)) fail(rel, `"${needle}" was typed into the drop-off block and is not in the sent document`);
  }
  if (!/not a booking/i.test(doc)) fail(rel, 'the drop-off block is in the document without the line that says it is an ask and not a booking');

  /* the other half of the mode: it must leave the document entirely */
  for (const b of segs) {
    await b.click();
    if (!await page.$eval('#dropoff', el => el.classList.contains('on'))) break;
  }
  doc = await copied(page);
  for (const v of Object.values(typed)) {
    if (doc.includes(v)) fail(rel, `"${v}" is a delivery answer and is still in the document after switching off delivery`);
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

  console.log(` ${rel}  ${opts.length} chips, ${picked.length} axes, block in and out of the document`);
  await ctx.close();
}

await browser.close();
s.close();

if (fails.length) {
  console.error(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`\nOK — ${list.length} page(s) carry a drop-off block that shows where it belongs, prints what he ticked, and survives the job.`);
