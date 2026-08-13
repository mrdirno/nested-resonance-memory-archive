/**
 * THE ROW-LOG RESTORE GATE — "the backup can actually be put back"
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS GATE EXISTS. Twenty-one shipped row-log pages across nine trades tell
 * a man, in their own words, that the spreadsheet copy "is also your backup: this
 * lives in this browser on this phone" — and low-voltage/device-checkout goes
 * further and tells him to send himself that copy at the end of a big day,
 * because "a browser you haven't opened in a couple of weeks can clear it out,
 * and a new phone definitely will." Every word of that was true. The engine had a
 * TSV writer and no reader, so the copy he was told to keep could not be put
 * back. A backup you cannot restore is a receipt for one, and the man who took
 * the advice is precisely the man who finds out on the new phone.
 *
 * WHAT IT ASSERTS, and why it is a round trip rather than a unit test. The claim
 * is not "importTsv parses tabs" — it is "the thing this page COPIED can be
 * pasted back into this page and give the same list." So the gate drives the real
 * add bar, clicks the page's own real "Copy for spreadsheet" button, throws the
 * browser away, opens the page in a FRESH CONTEXT (a new phone: empty
 * localStorage, no draft, nothing carried), pastes the captured text through the
 * real control, and then compares the DATA LINES of a freshly generated TSV
 * against the original. Byte-identical or it fails.
 *
 * IT RUNS OVER localhost, NOT file://, DELIBERATELY. The engine's copy path asks
 * for window.isSecureContext before it touches navigator.clipboard, and a file://
 * page is not one — so a gate run on file:// would silently exercise the
 * execCommand fallback and never test the path production uses. http://127.0.0.1
 * is a trustworthy origin, so this drives the same branch a phone does.
 *
 * IT IS DATA-DRIVEN FROM DISK. Pages are discovered by looking for
 * shared/rowlog.js in the HTML, so a row log shipped next month is covered the
 * day it lands with no edit here — and a page that cannot be driven is reported
 * as a LOUD skip with its reason, never quietly counted as green.
 *
 *   node tools/toolkit-gates/rowlog-restore.mjs [--only=slug/page.html]
 */
import { createRequire } from 'module';
import { readdirSync, existsSync, readFileSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const ROWS = 3;

/* ── discover every row-log page on disk ─────────────────────────────────── */
function trades() {
  return readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
}
function pages() {
  const out = [];
  for (const t of trades()) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, t, f), 'utf8');
      if (src.includes('shared/rowlog.js')) out.push(`${t}/${f}`);
    }
  }
  return ONLY ? out.filter(p => p === ONLY) : out;
}

/* ── a static server, because the copy path needs a trustworthy origin ───── */
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
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

/* ── drive the REAL add bar, generically ──────────────────────────────────
 * Every config declares different fields, so the filler works off what the
 * engine actually rendered rather than off a per-page script: text inputs get a
 * marker, a `learn` box gets one through its real blur handler, selects take
 * option 1 (never index 0 — that is the neutral option the engine requires and
 * the document drops), and one chip is tapped per chip axis. The chip box that
 * belongs to a `learn` field is skipped, or the seed would overwrite the marker
 * that makes the row identifiable. */
async function addRow(page, marker) {
  await page.evaluate((mk) => {
    const bar = document.querySelector('#bar');
    const learnKeys = new Set([...bar.querySelectorAll('[data-learn]')].map(e => e.getAttribute('data-learn')));
    bar.querySelectorAll('[data-learn]').forEach(el => {
      el.value = mk + '-' + el.getAttribute('data-learn');
      el.dispatchEvent(new Event('blur', { bubbles: true }));
    });
    bar.querySelectorAll('input[data-k]').forEach(el => {
      if (el.type === 'hidden') return;
      el.value = mk + '-' + el.getAttribute('data-k');
      el.dispatchEvent(new Event('input', { bubbles: true }));
    });
    bar.querySelectorAll('select[data-k]').forEach(el => {
      if (el.options.length > 1) { el.selectedIndex = 1; el.dispatchEvent(new Event('change', { bubbles: true })); }
    });
    bar.querySelectorAll('.rl-chips[data-chips]').forEach(box => {
      const k = box.getAttribute('data-chips');
      if (learnKeys.has(k)) return;
      const c = box.querySelector('.rl-chip[data-v]');
      if (c) c.click();
    });
  }, marker);
  await page.click('#rlAdd');
}

/* Capture what the page's own button puts on the clipboard. Overriding
 * navigator.clipboard rather than reading the OS clipboard keeps the gate
 * headless-safe and still exercises the real click → real tsv() → real copy. */
async function grabTsv(page) {
  await page.evaluate(() => {
    window.__cap = null;
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: t => { window.__cap = t; return Promise.resolve(); } }
    });
  });
  await page.click('#tsvBtn');
  await page.waitForFunction(() => window.__cap !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__cap);
}

const dataLines = tsv => tsv.split(/\r?\n/).slice(tsv.split(/\r?\n/).findIndex(l => l.includes('\t')) + 1).filter(l => l.trim());

async function putBack(page, text) {
  await page.evaluate(() => { const d = document.querySelector('details.rl-imp'); if (d) d.open = true; });
  const ta = await page.$('#rlImpTa');
  if (!ta) throw new Error('no restore control on the page — the engine did not mount it');
  await page.evaluate(t => { document.querySelector('#rlImpTa').value = t; }, text);
  await page.click('#rlImpGo');
  return page.evaluate(() => (document.querySelector('#rlImpSay') || {}).textContent || '');
}

/* ── run ──────────────────────────────────────────────────────────────────── */
const { s, port } = await serve();
const BASE = `http://127.0.0.1:${port}`;
const browser = await chromium.launch();
const list = pages();
let fail = 0, skip = 0, ok = 0;

for (const p of list) {
  let ctxA, ctxB;
  try {
    /* ── the phone that did the work ───────────────────────────────────── */
    ctxA = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const a = await ctxA.newPage();
    await a.goto(`${BASE}/${p}`, { waitUntil: 'load' });
    await a.waitForSelector('#rlAdd', { timeout: 5000 });
    for (let i = 0; i < ROWS; i++) await addRow(a, `ZQ${i}`);
    const made = await a.$$eval('.rl-row', r => r.length);
    if (made !== ROWS) { console.log(`SKIP  ${p} — could not drive the add bar (${made}/${ROWS} rows made)`); skip++; continue; }
    const before = await grabTsv(a);
    const beforeRows = dataLines(before);
    if (beforeRows.length !== ROWS) { console.log(`FAIL  ${p} — TSV wrote ${beforeRows.length} data rows for ${ROWS} list rows`); fail++; continue; }

    /* ── the new phone: empty storage, nothing carried ─────────────────── */
    ctxB = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const b = await ctxB.newPage();
    await b.goto(`${BASE}/${p}`, { waitUntil: 'load' });
    await b.waitForSelector('#rlAdd', { timeout: 5000 });
    const fresh = await b.$$eval('.rl-row', r => r.length);
    if (fresh !== 0) { console.log(`FAIL  ${p} — fresh context was not empty (${fresh} rows)`); fail++; continue; }

    const said = await putBack(b, before);
    const back = await b.$$eval('.rl-row', r => r.length);
    if (back !== ROWS) { console.log(`FAIL  ${p} — restored ${back}/${ROWS} rows · control said "${said.trim()}"`); fail++; continue; }

    const afterRows = dataLines(await grabTsv(b));
    const same = afterRows.length === beforeRows.length && afterRows.every((l, i) => l === beforeRows[i]);
    if (!same) {
      console.log(`FAIL  ${p} — the restored list does not re-copy identically`);
      for (let i = 0; i < Math.max(afterRows.length, beforeRows.length); i++) {
        if (afterRows[i] !== beforeRows[i]) console.log(`        row ${i}\n          out: ${beforeRows[i]}\n          in : ${afterRows[i]}`);
      }
      fail++; continue;
    }

    /* ── it ADDS, it never replaces: paste again and nothing is lost ───── */
    await putBack(b, before);
    const twice = await b.$$eval('.rl-row', r => r.length);
    if (twice !== ROWS * 2) { console.log(`FAIL  ${p} — second paste gave ${twice} rows, expected ${ROWS * 2} (import must add, never replace)`); fail++; continue; }

    /* ── and a header that matches nothing must fail LOUDLY, not import ── */
    const before3 = await b.$$eval('.rl-row', r => r.length);
    const refused = await putBack(b, 'nothing\tto\tsee\nhere\tat\tall');
    const after3 = await b.$$eval('.rl-row', r => r.length);
    if (after3 !== before3 || !/couldn'?t find/i.test(refused)) {
      console.log(`FAIL  ${p} — junk paste changed the list (${before3}→${after3}) or said nothing useful: "${refused.trim()}"`); fail++; continue;
    }

    console.log(`PASS  ${p} — ${ROWS} rows out, ${ROWS} back on a fresh device, re-copy byte-identical, additive, junk refused`);
    ok++;
  } catch (e) {
    console.log(`FAIL  ${p} — ${e.message}`);
    fail++;
  } finally {
    if (ctxA) await ctxA.close();
    if (ctxB) await ctxB.close();
  }
}

await browser.close();
s.close();
console.log(`\n${list.length} row-log page(s) — ${ok} passing, ${fail} failing, ${skip} skipped`);
process.exit(fail ? 1 : 0);
