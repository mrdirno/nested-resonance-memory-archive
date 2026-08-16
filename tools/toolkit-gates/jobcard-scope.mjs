/**
 * THE JOB CARD KEEPS ITS JOBS APART — a gate for shared/jobcard.js.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * shared/jobcard.js exists because six order pages hand-copied a sticky header
 * keyed to the PAGE while its own comment claimed the values belonged to the
 * JOB. The redesign makes every job a chip and the picker the guard. That buys
 * exactly one thing — a foreman on two jobs stops sending the warehouse's gate
 * code to the downtown supplier — and it is worth nothing if the separation is
 * not real. A card that leaks is strictly worse than the sticky header it
 * replaced, because it LOOKS job-aware.
 *
 * So this drives the real page and asserts the separation as OUTPUT, off the
 * clipboard, not off the DOM:
 *
 *  · A NEW JOB STARTS EMPTY. The safety property, and the whole reason "+ New
 *    job" is a deliberate tap rather than something inferred from him editing
 *    the name box. Every per-job field is asserted blank after the tap.
 *  · JOB A'S ANSWERS NEVER REACH JOB B'S DOCUMENT. The per-job values that
 *    actually print are collected from job A's real copied text, then looked for
 *    in job B's — and finding any one of them is the failure this module was
 *    built to stop.
 *  · SWITCHING BACK RESTORES. A picker that forgets on the way back is a picker
 *    that costs him the gate code every time he checks the other job.
 *  · THE DEVICE FIELDS DO NOT MOVE. "Requested by" is him on every job; blanking
 *    it with the rest would make the card feel broken on the second tap.
 *  · IT SURVIVES A RELOAD. Sticky that does not come back is worse than not
 *    sticky at all — he stops trusting it (the reason dropoff-block.mjs asserts
 *    the same thing three files away).
 *  · NOBODY LOSES A GATE CODE ON THE WAY IN. The old per-page key is seeded in a
 *    clean profile and the values are asserted to arrive on job #1. A migration
 *    that drops a foreman's saved access note is a data-loss bug shipped to a
 *    live page.
 *  · NO `fresh:` SCOPE EVER COMES BACK. It existed for about an hour and
 *    order-live-header.mjs killed it: a field printed in the document has to
 *    survive a reload, and blanking it on load loses a delivery method the man
 *    picked twenty minutes ago without losing anything he would notice. The
 *    reasoning is in shared/jobcard.js; this is the assertion, so the next page
 *    cannot re-invent it.
 *
 * WHAT IT DERIVES vs WHAT IT READS. The scopes are learned from the module's own
 * BEHAVIOUR — fill the header, then read which ids landed under `jobs[].f`
 * (per-job) and which under `device` in its store. Only `legacyKey` is read from
 * the page source, because the name of a key that no longer gets written cannot
 * be observed by driving the page.
 *
 *   node tools/toolkit-gates/jobcard-scope.mjs [--only=electrical/pull-list.html]
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const ONLY = (process.argv.slice(2).find(a => a.startsWith('--only=')) || '').slice(7);

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, t, f), 'utf8');
      if (src.includes('shared/jobcard.js')) out.push({ rel: `${t}/${f}`, trade: t, src });
    }
  }
  return ONLY ? out.filter(p => p.rel === ONLY) : out;
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

/* Fill every header control the house convention names (id `f` + a capital,
 * outside the ticked list) with a value that cannot occur by accident. Dates and
 * checkboxes are left alone — a marker string is not a datetime, and this gate
 * is about text the counter reads. */
async function fillHeader(page, tag) {
  return page.evaluate(t => {
    const list = document.getElementById('list');
    const put = {};
    document.querySelectorAll('input[id^="f"],select[id^="f"],textarea[id^="f"]').forEach(el => {
      if (!/^f[A-Z]/.test(el.id) || el.type === 'hidden') return;
      if (list && list.contains(el)) return;
      if (el.tagName === 'SELECT') return;
      if (['date', 'datetime-local', 'time', 'checkbox', 'radio', 'number'].includes(el.type)) return;
      const v = `Z${t}_${el.id}Z`;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      put[el.id] = v;
    });
    return put;
  }, tag);
}

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

const { s, port } = await serve();
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no page mounts shared/jobcard.js'); process.exit(1); }

for (const { rel, trade, src } of list) {
  /* ── the source-level regression guard ────────────────────────────────── */
  if (/\bfresh\s*:/.test(src.slice(src.indexOf('JobCard.mount')))) {
    fail(rel, 'JobCard.mount declares a `fresh:` scope — order-live-header.mjs killed that scope, see shared/jobcard.js');
  }
  const legacyKey = (src.match(/legacyKey:\s*"([^"]+)"/) || [])[1] || null;

  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await page.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 })
    .catch(() => fail(rel, 'no job chip rendered — shared/jobcard.js did not mount'));

  /* ONE LINE ON THE LIST FIRST, and it is not incidental. Every one of these
   * pages short-circuits its own document when nothing is ticked — `if
   * (!ctx.count) return out + "(nothing on it yet)"` — which drops the whole
   * footer where the gate code, the signer and the PO are printed. Copying an
   * empty list and concluding the card guards nothing is the gate lying about
   * three live pages, which is exactly what it did the first time it ran. */
  const ticked = await page.evaluate(() => {
    const t = document.querySelector('#list .item .tick');
    if (!t) return false;
    t.checked = true;
    t.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  });
  if (!ticked) fail(rel, 'no tickable line in #list — the document cannot be exercised');

  const KEY = `toolkit.${trade}.jobcard.v1`;
  const putA = await fillHeader(page, 'A');
  await page.waitForTimeout(60);

  const store = await page.evaluate(k => { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }, KEY);
  if (!store || !store.jobs || !store.jobs.length) { fail(rel, `nothing written to ${KEY} after filling the header`); await ctx.close(); continue; }
  const jobA = store.jobs.find(j => j.id === store.cur) || store.jobs[0];
  const PER = Object.keys(jobA.f || {}).filter(id => putA[id]);
  const DEV = Object.keys(store.device || {}).filter(id => putA[id]);
  if (!PER.length) { fail(rel, 'no per-job field was recorded — perJob is empty or the ids do not exist on the page'); await ctx.close(); continue; }
  for (const id of PER) if (DEV.includes(id)) fail(rel, `#${id} is declared BOTH per-job and device — one of them is a lie`);

  /* Which per-job answers actually reach the counter. Those are the ones a leak
   * would be measured in; a field that never prints cannot contaminate. */
  const docA = await copied(page);
  const visible = PER.filter(id => docA.includes(putA[id]));
  if (!visible.length) fail(rel, 'not one per-job field reaches the sent document — the card is guarding nothing');

  /* ── a new job starts EMPTY ───────────────────────────────────────────── */
  const newBtn = await page.$('#jobcard .jc-new');
  if (!newBtn) { fail(rel, 'no "+ New job" control — a second job cannot be started'); await ctx.close(); continue; }
  await newBtn.click();
  await page.waitForTimeout(60);

  const afterNew = await page.evaluate(ids => {
    const o = {};
    ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
    return o;
  }, PER.concat(DEV));
  for (const id of PER) {
    if (afterNew[id]) fail(rel, `#${id} still reads "${afterNew[id]}" on a brand-new job — a new job must start empty`);
  }
  for (const id of DEV) {
    if (afterNew[id] !== putA[id]) fail(rel, `#${id} is a device field and was cleared by starting a new job (now "${afterNew[id]}")`);
  }

  /* ── and job A's answers never reach job B's document ─────────────────── */
  const docB = await copied(page);
  for (const id of visible) {
    if (docB.includes(putA[id])) fail(rel, `#${id} from the first job is in the SECOND job's sent document — the cards leak`);
  }

  /* ── switching back restores ──────────────────────────────────────────── */
  await fillHeader(page, 'B');
  await page.waitForTimeout(60);
  const chips = await page.$$('#jobcard .jc-chip[data-j]');
  if (chips.length < 2) fail(rel, `only ${chips.length} job chip(s) after starting a second job`);
  else {
    await chips[0].click();
    await page.waitForTimeout(60);
    const back = await page.evaluate(ids => {
      const o = {};
      ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
      return o;
    }, PER);
    for (const id of PER) {
      if (back[id] !== putA[id]) fail(rel, `#${id} came back as "${back[id]}" instead of "${putA[id]}" after switching to the other job and back`);
    }
  }

  /* ── it survives a reload ─────────────────────────────────────────────── */
  await page.reload({ waitUntil: 'load' });
  await page.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 }).catch(() => {});
  const reloaded = await page.evaluate(ids => {
    const o = {};
    ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
    return o;
  }, PER);
  for (const id of PER) {
    if (reloaded[id] !== putA[id]) fail(rel, `#${id} did not survive a reload (came back "${reloaded[id]}", expected "${putA[id]}")`);
  }
  await ctx.close();

  /* ── nobody loses a gate code on the way in ───────────────────────────── */
  if (legacyKey) {
    const c2 = await browser.newContext({ viewport: { width: 390, height: 780 } });
    await c2.addInitScript(STUB);
    const seed = {};
    PER.concat(DEV).forEach(id => { seed[id] = `ZOLD_${id}Z`; });
    await c2.addInitScript(([k, v]) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }, [legacyKey, seed]);
    const p2 = await c2.newPage();
    await p2.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
    await p2.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 }).catch(() => {});
    const got = await p2.evaluate(ids => {
      const o = {};
      ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
      return o;
    }, PER.concat(DEV));
    for (const id of PER.concat(DEV)) {
      if (got[id] !== seed[id]) fail(rel, `the old key ${legacyKey} held #${id}="${seed[id]}" and the job card came up with "${got[id]}" — a migration that loses a saved answer`);
    }
    await c2.close();
  } else {
    fail(rel, 'no legacyKey declared — a page that had a sticky header must adopt it or the foreman loses it');
  }

  console.log(` ${rel}  ${PER.length} per-job, ${DEV.length} device, ${visible.length} of them in the document`);
}

await browser.close();
s.close();

if (fails.length) {
  console.log(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.log('  ✗ ' + f);
  process.exit(1);
}
console.log(`\nPASS — ${list.length} page(s): jobs stay apart, a new job starts empty, nothing is lost on the way in.`);
