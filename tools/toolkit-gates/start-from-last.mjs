/**
 * START FROM LAST, CLEAR AND THE BOX — the list's lifecycle, driven as a
 * sequence on every page the checklist engine mounts (C3750).
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY IT EXISTS. C3749 rewrote three things in shared/checklist-request.js —
 * one reset for Clear and Start-from-last, Start-from-last as a SWAP, and Copy /
 * Send flushing an un-Added write-in — and the only gate that drove any of it
 * was siding's, on a page that hides Start-from-last over a live list. So the
 * swap had never been driven by anything, and an audit that did drive it found
 * three defects in a day: every row's count reset to the tool's "1" instead of
 * its own default (hvac's truck stock renders thirty rows at their par), a list
 * pasted before a Clear riding out on the NEXT call through the new flush, and a
 * swapped-back list wearing the other list's header. End-state gates cannot see
 * any of that; it lives between two taps.
 *
 * WHAT IT ASSERTS, per page, found on disk by the engine it mounts:
 *   Q  after Clear, every row's count is its OWN rendered default (data-def)
 *   B  Clear empties the write-in box, and a later Copy carries none of it
 *   F  Copy carries an un-Added write-in exactly as Add would have put it on the
 *      list (a page may echo a line in a callback block — framing's "DROP NOT
 *      SAID" does — so the measure is parity with Add, not a count of one), and
 *      the glass shows it after
 *   U  Start-from-last after a Clear brings the rows AND their header back
 *   T  on a start (nothing ticked), a header typed today is not replaced
 *   S  where the button stands over a live list: the swap brings the other list
 *      back with its own header, a second tap swaps back, and no row keeps a
 *      count it was not saved with
 *
 *   node tools/toolkit-gates/start-from-last.mjs [--only=trade/page.html] [--engine=path/to/checklist-request.js]
 *
 * --engine serves another copy of the engine in place of the one on disk: run it
 * with HEAD's (git show HEAD:shared/checklist-request.js) to prove the gate goes
 * red on the defects it was written for.
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize, resolve } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const ENGINE = (args.find(a => a.startsWith('--engine=')) || '').slice(9);
const ENGINE_SRC = ENGINE ? readFileSync(resolve(ENGINE)) : null;

function pages() {
  const out = [];
  for (const d of readdirSync(ROOT, { withFileTypes: true })) {
    if (!d.isDirectory() || d.name.startsWith('.') || !existsSync(join(ROOT, d.name, 'tools.js'))) continue;
    for (const f of readdirSync(join(ROOT, d.name)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, d.name, f), 'utf8');
      // The engine by its mount call, not by a mention: two forks still name it
      // in a comment and drive their own list.
      if (/ChecklistRequest\.mount\(/.test(src) && src.includes('id="clear"') && src.includes('id="copy"')) out.push(`${d.name}/${f}`);
    }
  }
  out.sort();
  return ONLY ? out.filter(p => p === ONLY) : out;
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
function serve() {
  return new Promise(res => {
    const s = createServer((req, rq) => {
      const rel = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      if (ENGINE_SRC && rel.replace(/\\/g, '/').endsWith('shared/checklist-request.js')) {
        rq.writeHead(200, { 'content-type': 'text/javascript' }); return rq.end(ENGINE_SRC);
      }
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

const fails = [];
let checks = 0;
function check(page, id, ok, msg) { checks++; if (!ok) fails.push(`${page}  ${id}  ${msg}`); }

/* A header field the page saves WITH THE LIST (persistExtra), never one the job
 * card owns per job: the first of these that exists and is not a job-card field. */
const HEADER_IDS = ['fNotes', 'fFor', 'fTo', 'fProj', 'fCut'];

async function run(browser, base, rel) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto(base + rel, { waitUntil: 'load' });
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload({ waitUntil: 'load' });

  const settle = () => page.waitForTimeout(400);           // past the engine's 250 ms save debounce
  const rows = page.locator('#list li.item');
  const tick = async (i) => { const t = rows.nth(i).locator('.tick'); if (!(await t.isChecked())) await t.check(); };
  const setQty = async (i, v) => {
    const q = rows.nth(i).locator('.i-qty');
    if (!(await q.count())) return false;
    await q.evaluate((el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }, v);
    return true;
  };
  const setField = (id, v) => page.evaluate(({ id, v }) => {
    const el = document.getElementById(id);
    el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true }));
  }, { id, v });
  const field = (id) => page.evaluate(id => document.getElementById(id).value, id);
  const clear = async () => { await page.click('#clear'); await settle(); };
  const copy = async () => {
    await page.evaluate(() => { window.__copied = null; });
    await page.click('#copy');
    await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
    return page.evaluate(() => window.__copied);
  };
  const lastVisible = async () => (await page.locator('#last').count()) > 0 && (await page.locator('#last').isVisible());
  const tickedNames = () => page.evaluate(() => [...document.querySelectorAll('#list li.item.is-checked .name')].map(n => n.textContent));
  const nameOf = (i) => rows.nth(i).locator('.name').textContent();

  // Two catalogue rows that carry a count box (the first two such rows).
  const n = await rows.count();
  const withQty = [];
  for (let i = 0; i < n && withQty.length < 2; i++) {
    if (await rows.nth(i).locator('.rm').count()) continue;
    if (await rows.nth(i).locator('.i-qty').count()) withQty.push(i);
  }
  const [a, b] = withQty.length === 2 ? withQty : [0, 1];
  const qtyOf = async (i) => (await rows.nth(i).locator('.i-qty').count()) ? rows.nth(i).locator('.i-qty').inputValue() : null;
  const hasQty = withQty.length === 2;
  const nameA = await nameOf(a), nameB = await nameOf(b);

  // ── Q: Clear puts every count back to its own default ───────────────────────
  await tick(a); await setQty(a, '97'); await tick(b); await setQty(b, '98'); await settle();
  await clear();
  const qBad = await page.evaluate(() => [...document.querySelectorAll('#list .i-qty')]
    .filter(q => q.value !== (q.getAttribute('data-def') ?? q.value))
    .map(q => `${q.closest('.item').querySelector('.name').textContent}: "${q.value}" not "${q.getAttribute('data-def')}"`));
  check(rel, 'Q', qBad.length === 0, `after Clear ${qBad.length} row(s) hold a count that is not their own default — ${qBad.slice(0, 3).join(' · ')}`);

  // ── B / F: the write-in box ─────────────────────────────────────────────────
  const hasBox = (await page.locator('#list .wi-input').count()) > 0;
  if (hasBox) {
    const box = page.locator('#list .wi-input').first();
    await clear();
    await box.fill('ZQBOXLINE 11');
    await clear();
    check(rel, 'B1', (await box.inputValue()) === '', 'Clear left text in the write-in box');
    await tick(a); await settle();
    const t1 = await copy();
    check(rel, 'B2', !t1.includes('ZQBOXLINE'), 'a line pasted before Clear went out on the next Copy');
    await clear();
    await box.fill('ZQFLUSH 7');
    await page.locator('#list .wi-add').first().click();
    await tick(a); await settle();
    const nAdded = (await copy()).split('ZQFLUSH 7').length - 1;
    await clear();
    await box.fill('ZQFLUSH 7');
    await tick(a); await settle();
    const t2 = await copy();
    const nFlush = t2.split('ZQFLUSH 7').length - 1;
    check(rel, 'F1', nFlush >= 1 && nFlush === nAdded, `an un-Added write-in reached the copied message ${nFlush} time(s); Add puts it there ${nAdded}`);
    const glass = await page.locator('#preview').innerText().catch(() => '');
    check(rel, 'F2', glass.includes('ZQFLUSH 7'), 'after Copy the glass does not show the write-in the message carried');
    await clear();
  }

  // ── U / T / S: Start from last ──────────────────────────────────────────────
  if (await page.locator('#last').count()) {
    const hid = (await page.evaluate(ids => ids.find(id => {
      const el = document.getElementById(id);
      return el && !el.closest('#list') && !el.closest('#jobcard') && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && el.type !== 'date' && el.type !== 'datetime-local';
    }) || null, HEADER_IDS));
    await clear();
    // List A: one line with its own count, and a header.
    await tick(a); await setQty(a, '41');
    if (hid) await setField(hid, 'ZQHEADA');
    await settle();
    await clear();                                          // A goes to "last"
    if (hid) check(rel, 'U0', (await field(hid)) === '', `Clear left the header field #${hid} filled`);
    check(rel, 'U1', await lastVisible(), 'Start from last is not offered after a Clear');
    if (await lastVisible()) {
      await page.click('#last'); await settle();
      const tk = await tickedNames();
      check(rel, 'U2', tk.includes(nameA), `Start from last after a Clear did not bring back "${nameA}"`);
      if (hasQty) {
        const qa = await qtyOf(a);
        check(rel, 'U3', qa === '41', `the restored line came back with count "${qa}", not the "41" it was saved with`);
      }
      if (hid) check(rel, 'U4', (await field(hid)) === 'ZQHEADA', `undoing a Clear did not bring the header back (#${hid} = "${await field(hid)}")`);

      // T: a header he typed today is not replaced on a start.
      if (hid) {
        await clear();                                      // A to "last" again
        await setField(hid, 'ZQTODAY'); await settle();
        if (await lastVisible()) {
          await page.click('#last'); await settle();
          check(rel, 'T1', (await field(hid)) === 'ZQTODAY', `Start from last replaced the header typed today (#${hid} = "${await field(hid)}")`);
          check(rel, 'T2', (await tickedNames()).includes(nameA), 'with a header typed, Start from last did not bring the lines');
        }
      }

      // S: the swap, where the button stands over a live list.
      await clear();                                        // whatever is live goes to "last"; rebuild A cleanly
      await page.evaluate(() => { try { Object.keys(localStorage).filter(k => /\.last$/.test(k)).forEach(k => localStorage.removeItem(k)); } catch (e) {} });
      await tick(a); await setQty(a, '41');
      if (hid) await setField(hid, 'ZQHEADA');
      await settle();
      await clear();                                        // A (with header) in "last"
      await tick(b); await setQty(b, '52'); await settle(); // B live, header untouched
      if (await lastVisible()) {
        await page.click('#last'); await settle();          // swap: A up, B to "last"
        const tk1 = await tickedNames();
        check(rel, 'S1', tk1.includes(nameA) && !tk1.includes(nameB), `the swap brought up [${tk1.join(', ')}], not "${nameA}" alone`);
        if (hid) check(rel, 'S2', (await field(hid)) === 'ZQHEADA', `the swapped-in list came up without its header (#${hid} = "${await field(hid)}")`);
        if (hasQty) {
          const qb = await rows.nth(b).locator('.i-qty').evaluate(q => [q.value, q.getAttribute('data-def')]);
          check(rel, 'S3', qb[0] === qb[1], `the row swapped out kept count "${qb[0]}", not its default "${qb[1]}"`);
        }
        if (await lastVisible()) {
          await page.click('#last'); await settle();        // swap back: B up, A to "last"
          const tk2 = await tickedNames();
          check(rel, 'S4', tk2.includes(nameB) && !tk2.includes(nameA), `swapping back brought up [${tk2.join(', ')}], not "${nameB}" alone`);
          if (hid) check(rel, 'S5', (await field(hid)) === '', `the list swapped back wears the other list's header (#${hid} = "${await field(hid)}")`);
          if (hasQty) {
            const qb2 = await qtyOf(b);
            check(rel, 'S6', qb2 === '52', `swapping back returned "${nameB}" with count "${qb2}", not the "52" it was saved with`);
          }
        }
      }
    }
  }
  check(rel, 'E', errs.length === 0, `page errors: ${errs.join(' | ').slice(0, 200)}`);
  await ctx.close();
}

const list = pages();
if (!list.length) { console.error('start-from-last: no engine pages found' + (ONLY ? ` for --only=${ONLY}` : '')); process.exit(1); }
const { s, port } = await serve();
const browser = await chromium.launch({ args: ['--mute-audio'] });
for (const rel of list) {
  const before = fails.length;
  try { await run(browser, `http://127.0.0.1:${port}/`, rel); }
  catch (e) { fails.push(`${rel}  X  the drive threw: ${String(e).split('\n')[0]}`); }
  console.log(`${fails.length === before ? 'ok  ' : 'FAIL'}  ${rel}`);
}
await browser.close();
s.close();
if (fails.length) { console.log('\n' + fails.join('\n')); }
console.log(`\nSTART FROM LAST — ${list.length} page(s), ${checks} checks, ${fails.length} failing${ENGINE ? ` (engine: ${ENGINE})` : ''}`);
process.exit(fails.length ? 1 : 0);
