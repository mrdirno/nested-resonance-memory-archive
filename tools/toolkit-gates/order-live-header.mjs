/**
 * THE PREVIEW IS THE DOCUMENT — a gate for shape #1 (checklist → a request).
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHAT IT ASSERTS, and why it had to be an assertion rather than a rule:
 *
 *   (1) ANYTHING THAT REACHES THE COPIED DOCUMENT REACHES THE PREVIEW.
 *       Every order page puts a live block on the glass under a label that
 *       promises it is what the counter/yard/shop gets. A header field wired
 *       into the document builder but not into the re-render breaks that promise
 *       silently: the copied text is right, the block he PROOFREADS is a
 *       generation stale, and the one thing he checks before sending is the one
 *       thing that lies. Six of seven shipped order pages failed this the day it
 *       was first run — every one of them on the fields that live OUTSIDE the
 *       config's `watch` list (a charge code, a hot flag, a delivery method).
 *
 *   (2) ANYTHING THAT REACHES THE COPIED DOCUMENT SURVIVES A RELOAD, ALONE.
 *       This half was GREEN the first time it ran, and the reason is worth
 *       writing down rather than taking credit for: the save rides the
 *       re-render, so those same unwatched fields reached storage on nothing
 *       but shared/draft.js's flush at pagehide — §SCARS 2026-08-13's fix doing
 *       a job it was not written for. It is asserted here so the next page
 *       cannot quietly stop being that lucky. ALONE is load-bearing: set the
 *       header in one pass and a single watched field co-triggers a snapshot
 *       that carries every unwatched one home with it, and a page that persists
 *       nothing on its own passes.
 *
 * IT DERIVES EVERYTHING FROM THE PAGE. No per-page field list, no roster to
 * update: the pages are found on disk by their shape (a #list, a #preview, a
 * #copy and a #clear), the controls are found by id, and whether a field is IN
 * the document is decided by CHANGING IT AND READING WHAT THE REAL COPY BUTTON
 * PUTS ON THE CLIPBOARD. A trade shipped next month is covered the day it lands.
 *
 *   node tools/toolkit-gates/order-live-header.mjs [--only=plumbing/x.html]
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7);

function trades() {
  return readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
}
/* SHAPE #1 BY ITS SHAPE, not by which engine it happens to load: two of the
 * live order pages are hand-forks that predate shared/checklist-request.js, and
 * a gate that only covered the engine would have missed the two pages with the
 * longest-standing version of this defect. */
function pages() {
  const out = [];
  for (const t of trades()) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, t, f), 'utf8');
      if (src.includes('id="list"') && src.includes('id="preview"') &&
          src.includes('id="copy"') && src.includes('id="clear"')) out.push(`${t}/${f}`);
    }
  }
  return ONLY ? out.filter(p => p === ONLY) : out;
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

/* The REAL copy path, captured rather than simulated: the page's own click
 * handler runs, builds its own text and hands it to navigator.clipboard, which
 * is stubbed before any page script exists. Reading a rebuilt string out of the
 * page instead would test a function no user can reach. */
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

/* EVERY control outside the ticked list, not just the `f`-prefixed ones. The
 * house convention is `f` + a capital, and scoping to it would have been enough
 * for the five pages that existed the day this was written — and would have
 * silently skipped shared/dropoff.js the week after, which renders its own
 * controls under its own ids and puts every one of them in the sent document.
 * A control that does not reach the document is skipped for free, because the
 * test for "is it in the document" is changing it and reading the clipboard.
 * The ticked-line controls live inside #list and are covered by the row gates. */
async function controls(page) {
  return page.evaluate(() => {
    const out = [];
    document.querySelectorAll('input,select,textarea').forEach(el => {
      if (!el.id) return;
      if (el.closest('#list')) return;
      if (el.type === 'hidden') return;
      out.push({ id: el.id, tag: el.tagName.toLowerCase(), type: el.type || '', opts: el.tagName === 'SELECT' ? el.options.length : 0 });
    });
    return out;
  });
}

/* Change it the way a thumb changes it, and report the value that landed so the
 * reload half can look for the same thing. A date input will not take a marker
 * string, a select has no free text, and a checkbox has two states — so each
 * kind gets the change that is real for it, and none of them gets a value the
 * page could have produced on its own. */
async function poke(page, c) {
  return page.evaluate(({ id, tag, type, opts }) => {
    const el = document.getElementById(id);
    const fire = () => { el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); };
    if (type === 'checkbox') { el.checked = !el.checked; fire(); return { kind: 'toggle', v: el.checked }; }
    if (tag === 'select') {
      if (opts < 2) return null;
      el.selectedIndex = (el.selectedIndex + 1) % opts;
      fire();
      return { kind: 'select', v: el.value };
    }
    if (type === 'date') { el.value = '2031-07-09'; fire(); return { kind: 'value', v: '2031-07-09' }; }
    if (type === 'datetime-local') { el.value = '2031-07-09T06:45'; fire(); return { kind: 'value', v: '2031-07-09T06:45' }; }
    const mk = 'ZQ' + id.toUpperCase() + 'MARK';
    el.value = mk; fire();
    return { kind: 'value', v: mk };
  }, c);
}

async function restore(page, id, was) {
  await page.evaluate(({ id, was }) => {
    const el = document.getElementById(id);
    if (el.type === 'checkbox') el.checked = was; else el.value = was;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, { id, was });
}

const fails = [];
function fail(page, msg) { fails.push(`${page}  ${msg}`); }

const { s, port } = await serve();
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no shape #1 pages found'); process.exit(1); }

for (const rel of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await page.waitForFunction(() => {
    const p = document.getElementById('preview');
    return p && p.textContent.trim().length > 0;
  }, null, { timeout: 8000 });

  const cs = await controls(page);
  const inDoc = [];
  const found = new Set();

  /* (1) the live half */
  async function sweep(pool) {
    for (const c of pool) {
      if (found.has(c.id)) continue;
      const was = await page.evaluate(id => {
        const el = document.getElementById(id);
        return el.type === 'checkbox' ? el.checked : el.value;
      }, c.id);

      const before = { doc: await copied(page), prev: await page.textContent('#preview') };
      const p = await poke(page, c);
      if (!p) continue;
      const after = { doc: await copied(page), prev: await page.textContent('#preview') };

      if (after.doc !== before.doc) {
        found.add(c.id);
        inDoc.push({ id: c.id, kind: p.kind, v: p.v });
        if (after.prev === before.prev) {
          fail(rel, `#${c.id} reaches the copied document and never reaches the preview — the block labelled "what you send" is stale until something else pokes it`);
        }
      }
      await restore(page, c.id, was);
    }
  }
  await sweep(cs);

  /* THE MODE THE PAGE OPENS IN IS NOT THE ONLY MODE. A delivery block that only
   * exists once he taps Delivery is invisible to a sweep taken as-loaded, and
   * invisible is exactly how a block ships without a re-render — the defect this
   * gate is for. So every segment button is tapped in turn and anything that now
   * reaches the document is swept in that state. A control already proved to be
   * in the document is skipped, so this costs one extra pass over the leftovers
   * and not a combinatorial one. */
  const segs = await page.$$('.seg button, .seg [data-v]');
  for (let i = 0; i < segs.length; i++) {
    try { await segs[i].click(); } catch (e) { continue; }
    await sweep(cs.filter(c => !found.has(c.id)));
  }

  /* (2) the reload half — ONE FIELD AT A TIME, from a clean device each time.
   * Setting them together is the test that lies: the save on these pages rides
   * the re-render, so a single watched field co-triggers a snapshot that carries
   * every unwatched one home with it, and a page that persists nothing on its
   * own passes. The failure a man actually hits is the lonely one — he toggles
   * the hot flag, the phone rings, he comes back. So: wipe storage, reload, poke
   * exactly one control, wait past the 250 ms debounce, reload, look for it. */
  for (const f of inDoc) {
    await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await page.reload({ waitUntil: 'load' });
    await page.waitForFunction(() => {
      const p = document.getElementById('preview');
      return p && p.textContent.trim().length > 0;
    }, null, { timeout: 8000 });

    await page.evaluate(({ id, kind, v }) => {
      const el = document.getElementById(id);
      if (kind === 'toggle') el.checked = v; else el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }, f);
    await page.waitForTimeout(700);
    await page.reload({ waitUntil: 'load' });
    await page.waitForFunction(() => {
      const p = document.getElementById('preview');
      return p && p.textContent.trim().length > 0;
    }, null, { timeout: 8000 });

    const now = await page.evaluate(id => {
      const el = document.getElementById(id);
      if (!el) return null;
      return el.type === 'checkbox' ? el.checked : el.value;
    }, f.id);
    if (now !== f.v) {
      fail(rel, `#${f.id} is printed in the document and does not survive a reload on its own (set ${JSON.stringify(f.v)}, came back ${JSON.stringify(now)})`);
    }
  }

  console.log(`${fails.length ? ' ' : ' '}${rel}  ${cs.length} header control(s), ${inDoc.length} in the document`);
  await ctx.close();
}

await browser.close();
s.close();

if (fails.length) {
  console.error(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`\nOK — ${list.length} order page(s): everything in the document is on the glass and survives a reload.`);
