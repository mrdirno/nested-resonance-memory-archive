/**
 * THE PICK FILTER — narrowing a list must narrow it, and never lose the job.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * shared/pickfilter.js hides rows. Every defect that shape can ship is invisible
 * to a screenshot, and three of them were already sitting in the reference
 * implementation this was extracted from:
 *
 *  · CLASSES THAT HIDE NOTHING. `.is-hidden` toggles correctly and no page has a
 *    display rule for it, so the filter "works" and the list never moves. The
 *    only honest question is what the browser COMPUTED, not what class is on.
 *  · THE ESCAPE HATCH VANISHING. The write-in section is where a man goes when
 *    the list does not have his thing — which is exactly the moment a filter is
 *    narrowing hardest. Hide it with everything else and the tool dead-ends at
 *    its own dead end. (The reference did: one write-in row, then filter for
 *    anything else, and the Add box went with it.)
 *  · THE MASS-TICK ON AN EMPTY BOX. "Check shown" with nothing typed means all
 *    151 of them, one thumb, no confirm.
 *
 * And the one that would be worst in the field: a row ticked and then filtered
 * out of sight must still be IN THE DOCUMENT. Hiding is a view; ticking is the
 * order. So this gate ticks a line, filters it off the glass, presses the page's
 * own Copy button and reads the clipboard for it.
 *
 * Every probe word is SELF-DERIVED from the page's own item names — a gate
 * carrying its own word list is a gate that passes on a page whose vocabulary
 * changed underneath it.
 *
 *   node tools/toolkit-gates/pickfilter.mjs [base-url]
 *
 * Default base is a throwaway localhost server over the working tree, because
 * file:// silently takes the clipboard FALLBACK path and this gate reads the
 * clipboard. Pass the live URL after a deploy to re-run against production.
 */
import { createRequire } from 'module';
import { createServer } from 'node:http';
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, extname, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

// The house pattern: the only node_modules in this tree belongs to Collage Studio.
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, t, f), 'utf8');
      if (src.includes('shared/pickfilter.js')) out.push(`${t}/${f}`);
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

const fails = [];
const fail = (p, m) => fails.push(`${p}: ${m}`);

let list = pages();
if (only) list = list.filter(p => p === only);
if (!list.length) { console.error('no pages mount shared/pickfilter.js'); process.exit(1); }

const given = args.find(a => !a.startsWith('--'));
const local = given ? null : await serve();
const BASE = (given || `http://127.0.0.1:${local.port}`).replace(/\/$/, '');

const browser = await chromium.launch();
let checks = 0;

for (const rel of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 760 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto(`${BASE}/${rel}`, { waitUntil: 'load' });
  await page.waitForTimeout(250);

  const q = page.locator('.pf-q, #q').first();
  if (!(await q.count())) { fail(rel, 'no filter input on a page that loads pickfilter.js'); await ctx.close(); continue; }

  /* ── the rails: a control a thumb has to hit, and a font iOS will not zoom ── */
  const bar = await page.evaluate(() => {
    const pick = el => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return { w: r.width, h: r.height, fs: parseFloat(cs.fontSize), shown: cs.display !== 'none' };
    };
    return {
      q: pick(document.querySelector('.pf-q, #q')),
      cat: pick(document.querySelector('.pf-cat')),
      check: pick(document.querySelector('.pf-check, #checkShown')),
    };
  });
  if (bar.q.fs < 16) fail(rel, `the filter box is ${bar.q.fs}px — under 16 iOS zooms the page on focus`);
  for (const [k, v] of Object.entries(bar)) {
    if (!v || !v.shown) continue;
    const short = Math.min(v.w, v.h);
    if (short < 44) fail(rel, `the ${k} control is ${short.toFixed(1)}px on its short side (44 minimum)`);
  }
  /* CHECK SHOWN IS NOT REACHABLE UNTIL THE LIST IS ACTUALLY NARROWED. */
  if (bar.check && bar.check.shown) fail(rel, '"Check shown" is on screen with an empty box — one tap ticks the whole list');

  const shape = await page.evaluate(() => {
    const items = [...document.querySelectorAll('#list .item')];
    const keep = [...document.querySelectorAll('#list .cat')].filter(c => c.querySelector('.addrow, .addbar, .wi-add'));
    return {
      total: items.length,
      cats: document.querySelectorAll('#list .cat').length,
      keeps: keep.length,
      // the longest word on the first real row — the page's own vocabulary
      word: (() => {
        for (const it of items) {
          const w = (it.querySelector('.name') || it).textContent
            .split(/[^A-Za-z0-9]+/).filter(x => x.length >= 5).sort((a, b) => b.length - a.length)[0];
          if (w) return w;
        }
        return null;
      })(),
      hasSel: !!document.querySelector('.pf-cat'),
    };
  });
  if (!shape.word) { fail(rel, 'no item name long enough to probe with'); await ctx.close(); continue; }

  const vis = () => page.evaluate(() =>
    [...document.querySelectorAll('#list .item')].filter(i => getComputedStyle(i).display !== 'none').length);
  const label = () => page.evaluate(() => {
    const el = document.querySelector('.pf-none, #nomatch');
    return el && getComputedStyle(el).display !== 'none' ? el.textContent.trim() : '';
  });

  if (await vis() !== shape.total) fail(rel, 'rows are hidden before anything was typed');

  /* ── 1. a word off the page narrows the page, and .is-hidden really hides ── */
  await q.fill(shape.word);
  await page.waitForTimeout(120);
  const nHit = await vis();
  if (nHit === 0) fail(rel, `"${shape.word}" — its own item name — matched nothing`);
  if (nHit >= shape.total) fail(rel, `"${shape.word}" hid nothing: the class toggles and no rule hides it`);
  if (await label() !== '') fail(rel, `an exact match was labelled approximate ("${await label()}")`);

  /* ── 2. the escape hatch is never filtered away ─────────────────────────── */
  const hatch = await page.evaluate(() => {
    const c = [...document.querySelectorAll('#list .cat')].find(x => x.querySelector('.addrow, .addbar, .wi-add'));
    if (!c) return 'none';
    return getComputedStyle(c).display !== 'none' && !!c.querySelector('.wi-input, input, textarea') ? 'ok' : 'gone';
  });
  if (hatch === 'gone') fail(rel, 'the write-in section was hidden by the filter — the page dead-ends at its own dead end');

  /* 2b. AND STILL THERE ONCE IT HOLDS A ROW. An empty section is never hidden by
   * the empty-section rule, so the defect this is really about only exists after
   * a man has written something in: his own row does not match the next thing he
   * filters for, the section goes with it, and the Add box goes with the section.
   * This is the reference implementation's live bug. */
  if (hatch === 'ok') {
    await q.fill('');
    await page.waitForTimeout(80);
    const added = await page.evaluate(() => {
      const c = [...document.querySelectorAll('#list .cat')].find(x => x.querySelector('.addrow, .addbar, .wi-add'));
      const box = c.querySelector('.wi-input, input[type="text"], textarea');
      const btn = c.querySelector('.wi-add, .addbtn, button');
      if (!box || !btn) return false;
      box.value = 'qqzz gate row';
      box.dispatchEvent(new Event('input', { bubbles: true }));
      btn.click();
      return c.querySelectorAll('.item').length > 0;
    });
    if (added) {
      await q.fill(shape.word);
      await page.waitForTimeout(120);
      const still = await page.evaluate(() => {
        const c = [...document.querySelectorAll('#list .cat')].find(x => x.querySelector('.addrow, .addbar, .wi-add'));
        return !!c && getComputedStyle(c).display !== 'none'
          && !!c.querySelector('.wi-input, input[type="text"], textarea');
      });
      if (!still) fail(rel, 'once a write-in row existed, filtering for anything else took the Add box off the page with it');
      // put the page back to a clean list for the assertions that follow
      const clr0 = page.locator('#clear').first();
      if (await clr0.count()) { await clr0.click(); await page.waitForTimeout(200); }
      await q.fill(shape.word);
      await page.waitForTimeout(120);
    }
  }

  /* ── 3. nonsense never dead-ends, and it says so ────────────────────────── */
  await q.fill('zzqqxyw');
  await page.waitForTimeout(120);
  const nNone = await vis();
  const lNone = await label();
  if (nNone === 0) fail(rel, 'a nonsense query emptied the list — "nothing matches" is a bug, not a state');
  if (!/^Nothing matched/.test(lNone)) fail(rel, `a nonsense query was not labelled as approximate (label: ${JSON.stringify(lNone)})`);

  /* ── 4. a typo lands, and is labelled as the guess it is ────────────────── */
  const typo = shape.word.slice(0, -2) + shape.word.slice(-1);
  await q.fill(typo);
  await page.waitForTimeout(120);
  if (await vis() === 0) fail(rel, `one typo ("${typo}") emptied the list`);
  const lTypo = await label();
  if (lTypo && !/^(Closest to|Nothing matched)/.test(lTypo)) fail(rel, `unexpected honesty label: ${JSON.stringify(lTypo)}`);

  /* ── 5. "Check shown" appears only while narrowed, and ticks only what is ── */
  await q.fill(shape.word);
  await page.waitForTimeout(120);
  const chk = page.locator('.pf-check, #checkShown').first();
  if (await chk.count()) {
    if (!(await chk.isVisible())) fail(rel, '"Check shown" is missing while the list IS narrowed');
    await chk.click();
    await page.waitForTimeout(150);
    const ticked = await page.evaluate(() => ({
      on: document.querySelectorAll('#list .item.is-checked').length,
      onHidden: [...document.querySelectorAll('#list .item.is-checked')]
        .filter(i => getComputedStyle(i).display === 'none').length,
    }));
    if (ticked.on !== nHit) fail(rel, `"Check shown" ticked ${ticked.on} rows with ${nHit} on screen`);
    if (ticked.onHidden) fail(rel, `"Check shown" ticked ${ticked.onHidden} row(s) that were not shown`);
  }

  /* ── 5b. THE NARROWED BAR IS THE WIDEST THE BAR EVER GETS, and it is a state
   * mobile-watertight never sees: that gate measures the page as it loads, and
   * "Check shown" only exists after somebody types. A third control appearing in
   * a row that fit two is exactly how a page starts scrolling sideways. ────── */
  for (const w of [320, 360, 390, 430]) {
    await page.setViewportSize({ width: w, height: 760 });
    await page.waitForTimeout(60);
    const over = await page.evaluate(() => {
      const d = document.documentElement;
      const bar = document.querySelector('.pf-bar');
      const wide = bar && [...bar.children].find(el => el.getBoundingClientRect().right > d.clientWidth + 1);
      return { doc: d.scrollWidth - d.clientWidth, body: document.body.scrollWidth - d.clientWidth,
               who: wide ? wide.className : null };
    });
    if (over.doc > 0 || over.body > 0)
      fail(rel, `narrowed, the page scrolls sideways at ${w}px (doc +${over.doc}, body +${over.body}${over.who ? ', culprit .' + over.who : ''})`);
  }
  await page.setViewportSize({ width: 390, height: 760 });
  await page.waitForTimeout(60);

  /* ── 6. ticked then filtered off the glass is STILL IN THE DOCUMENT ─────── */
  await q.fill('zzqqxyw');
  await page.waitForTimeout(150);
  const copied = await page.evaluate(async () => {
    const b = document.getElementById('copy');
    if (!b) return null;
    b.click();
    await new Promise(r => setTimeout(r, 120));
    return window.__copied;
  });
  if (copied === null) fail(rel, 'no #copy button to prove the document with');
  else if (!copied || !copied.toLowerCase().includes(shape.word.toLowerCase()))
    fail(rel, `a ticked row disappeared from the document once a filter hid it ("${shape.word}" not in the copy)`);

  /* ── 7. one section, and the hatch still there ──────────────────────────── */
  if (shape.hasSel) {
    await q.fill('');
    const opt = await page.evaluate(() => {
      const s = document.querySelector('.pf-cat');
      const v = s.options[1].value;
      s.value = v; s.dispatchEvent(new Event('change', { bubbles: true }));
      return v;
    });
    await page.waitForTimeout(120);
    const secOnly = await page.evaluate(id => {
      const cats = [...document.querySelectorAll('#list .cat')];
      const shown = cats.filter(c => getComputedStyle(c).display !== 'none');
      const hatchShown = shown.some(c => c.querySelector('.addrow, .addbar, .wi-add'));
      const strays = shown.filter(c => c.getAttribute('data-id') !== id && !c.querySelector('.addrow, .addbar, .wi-add'));
      return { strays: strays.length, hatchShown };
    }, opt);
    if (secOnly.strays) fail(rel, `picking one section left ${secOnly.strays} other section(s) on screen`);
    if (!secOnly.hatchShown) fail(rel, 'picking one section hid the write-in escape hatch');
  }

  /* ── 8. Clear un-filters, or the fresh list looks like a broken one ─────── */
  const clr = page.locator('#clear').first();
  if (await clr.count()) {
    await q.fill(shape.word);
    await page.waitForTimeout(100);
    await clr.click();
    await page.waitForTimeout(200);
    const after = await page.evaluate(() => ({
      q: (document.querySelector('.pf-q, #q') || {}).value,
      vis: [...document.querySelectorAll('#list .item')].filter(i => getComputedStyle(i).display !== 'none').length,
      on: document.querySelectorAll('#list .item.is-checked').length,
    }));
    if (after.q) fail(rel, `Clear left "${after.q}" in the filter box`);
    if (after.on) fail(rel, `Clear left ${after.on} row(s) ticked`);
    if (after.vis === 0) fail(rel, 'Clear left an empty list on screen');
  }

  /* ── 9. the section marker reads n / total and moves when you tick ──────── */
  const tally = await page.evaluate(() => {
    const secs = [...document.querySelectorAll('#list .cat')]
      .filter(c => !c.querySelector('.addrow, .addbar, .wi-add') && c.querySelectorAll('.item').length);
    if (!secs.length) return null;
    // The engine marks sections with [data-n]; the page the shape was proved on
    // has always used [data-tally]. Either is the same readout.
    const mark = c => c.querySelector('[data-n], [data-tally]');
    const bad = secs.filter(c => !/^\d+\s*\/\s*\d+$/.test((mark(c) || {}).textContent || ''));
    const s = secs.find(c => mark(c) && c.querySelector('.tick'));
    if (!s) return { bad: bad.length, of: secs.length, before: null, after: null };
    const before = mark(s).textContent;
    s.querySelector('.tick').click();
    return { bad: bad.length, of: secs.length, before, after: mark(s).textContent };
  });
  if (tally) {
    if (tally.bad) fail(rel, `${tally.bad}/${tally.of} section markers do not read "n / total"`);
    if (tally.before !== null && tally.before === tally.after)
      fail(rel, `the section marker did not move when a row was ticked (${tally.before})`);
  }

  if (errs.length) fail(rel, `page error: ${errs[0].split('\n')[0]}`);

  checks += 13;
  console.log(` ${rel.padEnd(32)} ${shape.total} items / ${shape.cats} sections · "${shape.word}" → ${nHit} · ${shape.hasSel ? 'section picker' : 'no picker'}`);
  await ctx.close();
}

await browser.close();
if (local) local.s.close();

if (fails.length) {
  console.error(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`\nOK — ${list.length} page(s), ${checks} assertions: the filter narrows, never dead-ends, never hides the way out, and never drops a ticked line from the document.`);
