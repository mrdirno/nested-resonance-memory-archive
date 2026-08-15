/**
 * EVERY ANSWER REACHES THE MESSAGE — on every page built on shared/note.js.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * THE BACKPORT. On 2026-08-14 the ORDER engine was caught with a defect nobody
 * could see, because the OUTPUT was right: a hand-kept `watch` list that had to
 * agree with a hand-written `document()`, drifted on four of five pages, and ten
 * controls were in the sent text and out of the re-render. `order-live-header.mjs`
 * was written to catch that class — and it only ever looked at the order pages.
 *
 * Shape #2 is a DIFFERENT engine with a different failure mode, so the same
 * question has to be asked of it in its own terms rather than assumed answered.
 * `note.js` binds `input` and `change` once, on the whole form, by delegation —
 * there is no second list to drift — so the drift bug cannot happen here by
 * construction. What CAN still happen is the other half of the same class: a
 * field that renders, accepts an answer, and never reaches the document, because
 * its `kind` was misspelled (BUILDERS returns undefined and the field is dropped
 * SILENTLY, no warning), its `id` collides with another field's, or a `docSkip`
 * was left on from the page it was copied from. Every one of those looks correct
 * on screen and is invisible until a receiver acts on a message missing a line.
 *
 * So this asserts the outcome rather than the mechanism, on every note page of
 * every trade: change ONE field, alone, on a freshly wiped device, and the text
 * the real Copy button produces must CHANGE. A field the config deliberately
 * keeps out of the document declares that with `docSkip` and is exempted BY NAME
 * — read out of the page's own source, so an author cannot silence this gate
 * without saying in the config that the omission was on purpose.
 *
 *   node tools/toolkit-gates/note-live-fields.mjs
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));

/* `--only=<substring>` narrows the run, the same way mobile-watertight.mjs does.
   It is for iterating, never for shipping: the unfiltered run is the gate. */
const ONLY = (process.argv.slice(2).find(a => a.startsWith('--only=')) || '').slice(7);

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      if (!readFileSync(join(ROOT, t, f), 'utf8').includes('shared/note.js')) continue;
      if (ONLY && !`${t}/${f}`.includes(ONLY)) continue;
      out.push(`${t}/${f}`);
    }
  }
  return out;
}

/* The ids the config itself says stay out of the document. One line each in the
   house style — `{ id: "site", kind: "text", …, docSkip: true }` — so the id is
   the last one named before the flag. */
function skipped(src) {
  const out = new Set();
  for (const line of src.split('\n')) {
    if (!/docSkip:\s*true/.test(line)) continue;
    const m = line.match(/id:\s*["']([^"']+)["']/);
    if (m) out.add(m[1]);
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
  window.confirm = () => true;
};
async function copied(page) {
  await page.evaluate(() => { window.__copied = null; });
  await page.click('#copy');
  await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__copied);
}

/* Set one field, whatever kind it turns out to be, and say whether we managed to
   change anything at all — a field we could not drive is reported, never skipped
   quietly, because a silent skip is how a gate stops testing without saying so. */
async function drive(page, id, sentinel) {
  return page.evaluate(([fid, val]) => {
    const f = document.querySelector(`[data-f="${fid}"]`);
    if (!f) return 'no such field';
    const fire = el => { el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); };
    const rows = f.querySelectorAll('.rowlist .row');
    if (rows.length) {
      const cells = rows[0].querySelectorAll('.cell input, .cell select');
      if (!cells.length) return 'row with no cells';
      let did = false;
      for (const c of cells) {
        if (c.tagName === 'SELECT') { if (c.options.length > 1) { c.selectedIndex = c.options.length - 1; fire(c); did = true; } }
        else { c.value = val; fire(c); did = true; }
      }
      return did ? '' : 'row cells undriveable';
    }
    const ticks = f.querySelectorAll('ul.ticks input[type=checkbox]');
    if (ticks.length) { ticks[0].checked = true; ticks[0].dispatchEvent(new Event('change', { bubbles: true })); return ''; }
    const chip = f.querySelector('.pick button, .seg button');
    if (chip) { chip.click(); return ''; }
    const sel = f.querySelector('select');
    if (sel) { if (sel.options.length < 2) return 'select with one option'; sel.selectedIndex = sel.options.length - 1; fire(sel); return ''; }
    const ta = f.querySelector('textarea');
    if (ta) { ta.value = val; fire(ta); return ''; }
    const inp = f.querySelector('input');
    if (inp) { inp.value = inp.type === 'date' ? '2026-08-22' : val; fire(inp); return ''; }
    return 'no control inside the field';
  }, [id, sentinel]);
}

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

const { s, port } = await serve();
const browser = await chromium.launch();
const list = pages();
if (!list.length) { console.error('no page mounts shared/note.js'); process.exit(1); }

let checked = 0;
for (const rel of list) {
  const src = readFileSync(join(ROOT, rel), 'utf8');
  const skip = skipped(src);

  const ctx0 = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx0.addInitScript(STUB);
  const probe = await ctx0.newPage();
  await probe.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await probe.waitForSelector('[data-f]', { state: 'attached' });
  const ids = await probe.$$eval('[data-f]', els => els.map(e => e.getAttribute('data-f')));
  await ctx0.close();

  if (new Set(ids).size !== ids.length) fail(rel, `duplicate field id in the config — only the last one is tracked: ${ids.filter((v, i) => ids.indexOf(v) !== i).join(', ')}`);

  for (const id of ids) {
    if (skip.has(id)) continue;
    /* EACH FIELD ALONE, FROM A WIPED DEVICE. Together they mask each other: a
       dropped field is invisible when six others already changed the text. */
    const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
    await ctx.addInitScript(STUB);
    const page = await ctx.newPage();
    await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
    await page.waitForSelector('[data-f]', { state: 'attached' });
    const before = await copied(page);
    const why = await drive(page, id, `ZZ${id}ZZ`);
    if (why) { fail(rel, `field "${id}" could not be driven (${why}) — this gate is not testing it`); await ctx.close(); continue; }
    const after = await copied(page);
    if (after === before) fail(rel, `field "${id}" takes an answer on the glass and NOTHING reaches the message, and the config never said docSkip — a misspelled kind, a colliding id, or a docSkip copied in from another page`);
    checked++;
    await ctx.close();
  }
}

await browser.close();
s.close();

if (fails.length) {
  console.error(`\nNOTE LIVE FIELDS — ${fails.length} defect(s) across ${list.length} page(s):\n`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`NOTE LIVE FIELDS — ${checked} in-document field(s) across ${list.length} page(s): every one of them reaches the message.`);
