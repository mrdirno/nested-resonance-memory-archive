/**
 * THE LANGUAGE-LAYER GATE — every page that mounts shared/lang.js, in both tongues.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * THE BACKPORT (2026-08-23). The toolkit's first bilingual page (gc/tm-tag.html,
 * from the wish "Todo en Español para los Latinos") was proven by an e2e that
 * lived in one session's scratch and died with it. The layer is now an engine
 * on twelve pages, so the proof becomes a gate: run over every page that mounts
 * the engine, derived from disk, so a trade that adopts it next month is
 * covered the day it lands with no edit here.
 *
 * WHAT IT ASSERTS, per page, and why each one is here:
 *  · THE ENGLISH DOCUMENT IS BYTE-IDENTICAL to the one the committed page
 *    (git HEAD) produces for the same answers. The panel bound "EN mode's
 *    document is byte-identical to before" and a receiver's inbox is full of
 *    the old shape; a wrapper that changes one heading breaks every search.
 *    Both trees are driven under the same frozen clock so the stamp cannot
 *    differ. A page not in HEAD yet is new and skips this one check, loudly.
 *  · THE PHONE'S TONGUE IS FOLLOWED on a wiped device: an es-* locale opens en
 *    español with the ES chip lit and <html lang="es">; an en-* locale opens in
 *    English with nothing moved.
 *  · THE ES DOCUMENT STAYS READABLE AT THE TOP OF THE CHAIN: the document name
 *    and every section head print "ES / EN", and every picked option whose
 *    Spanish differs from its English prints "ES (EN)". A CM who cannot read
 *    the tag cannot reply OK to it, and the reply is the whole point.
 *  · THE FLIP TRANSLATES THE DRAFT, BOTH WAYS: picks made in EN arrive in ES
 *    as their twins after the toggle, and come back verbatim after the second
 *    toggle (§SCARS 2026-08-18 — the remap has to happen at boot; this is the
 *    e2e that caught the exit-flush overwrite and it must never be un-run).
 *  · THE TWINS ARE COMPLETE: for every vocabulary key the page maps, items.js
 *    carries the same number of ES entries as EN and every en-twin matches an
 *    EN option verbatim — the remap is a dictionary and a missing word is a
 *    pick that silently survives the flip untranslated.
 *  · NOTHING OVERFLOWS IN SPANISH at 320 / 360 / 390 / 430 — Spanish runs a
 *    third longer than English and the mobile gate only ever reads the page
 *    in English; the language chips are ≥ 44px and inside the glass.
 *  · ZERO page errors in either tongue, on every load.
 *
 *   node tools/toolkit-gates/lang-layer.mjs            (the gate)
 *   node tools/toolkit-gates/lang-layer.mjs --only=gc   (iterating; never the ship)
 */
import { readdirSync, readFileSync, existsSync, statSync, mkdtempSync, rmSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { execSync } from 'child_process';
import { extname, join, normalize } from 'path';
import { tmpdir } from 'os';
import vm from 'vm';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const ONLY = (process.argv.slice(2).find(a => a.startsWith('--only=')) || '').slice(7);
const FROZEN = '2026-08-23T10:00:00-07:00';

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      if (!readFileSync(join(ROOT, t, f), 'utf8').includes('shared/lang.js')) continue;
      if (ONLY && !`${t}/${f}`.includes(ONLY)) continue;
      out.push(`${t}/${f}`);
    }
  }
  return out;
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
function serve(root) {
  return new Promise(res => {
    const s = createServer((req, rq) => {
      const rel = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      const p = join(root, rel);
      if (!p.startsWith(root) || !existsSync(p) || statSync(p).isDirectory()) { rq.writeHead(404); return rq.end('no'); }
      rq.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
      rq.end(readFileSync(p));
    });
    s.listen(0, '127.0.0.1', () => res({ s, port: s.address().port }));
  });
}

/* HEAD, exported whole, so the identity check compares against what is
   actually committed rather than against a memory of it. */
function exportHead(dirs) {
  const dir = mkdtempSync(join(tmpdir(), 'lang-layer-head-'));
  try {
    execSync(`git -C "${ROOT}" archive HEAD ${dirs.map(d => `"${d}"`).join(' ')} | tar -x -C "${dir}"`, { stdio: 'pipe' });
  } catch (e) { /* a dir not yet in HEAD makes archive fail; fall back per dir */
    for (const d of dirs) { try { execSync(`git -C "${ROOT}" archive HEAD "${d}" | tar -x -C "${dir}"`, { stdio: 'pipe' }); } catch (e2) {} }
  }
  return dir;
}

const STUB = () => {
  window.__copied = null;
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: { writeText: t => { window.__copied = String(t); return Promise.resolve(); } },
  });
  window.confirm = () => true;
};

async function newCtx(browser, locale, width) {
  const ctx = await browser.newContext({ viewport: { width: width || 390, height: 780 }, locale });
  await ctx.clock.install({ time: new Date(FROZEN) });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e && e.message || e)));
  return { ctx, page, errors };
}

async function copied(page) {
  await page.evaluate(() => { window.__copied = null; });
  await page.click('#copy');
  await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__copied);
}

/* Drive every field the same deterministic way on every tree and tongue: text
   gets a sentinel, the LAST chip / tick / select option, every row cell. Same
   answers in, so the only thing that can differ is the page. */
async function driveAll(page) {
  return page.evaluate(() => {
    const fire = el => { el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); };
    const out = [];
    for (const f of document.querySelectorAll('[data-f]')) {
      const id = f.getAttribute('data-f');
      const rows = f.querySelectorAll('.rowlist .row');
      if (rows.length) {
        for (const c of rows[0].querySelectorAll('.cell input, .cell select')) {
          if (c.tagName === 'SELECT') { if (c.options.length > 1) { c.selectedIndex = c.options.length - 1; fire(c); } }
          else { c.value = c.type === 'number' ? '3' : `ZZ${id}ZZ`; fire(c); }
        }
        out.push(id); continue;
      }
      const ticks = f.querySelectorAll('ul.ticks input[type=checkbox]');
      if (ticks.length) { const t = ticks[ticks.length - 1]; t.checked = true; t.dispatchEvent(new Event('change', { bubbles: true })); out.push(id); continue; }
      const chips = f.querySelectorAll('.pick button, .seg button');
      if (chips.length) { chips[chips.length - 1].click(); out.push(id); continue; }
      const sel = f.querySelector('select');
      if (sel) { if (sel.options.length > 1) { sel.selectedIndex = sel.options.length - 1; fire(sel); } out.push(id); continue; }
      const ta = f.querySelector('textarea');
      if (ta) { ta.value = `ZZ${id}ZZ`; fire(ta); out.push(id); continue; }
      const inp = f.querySelector('input');
      if (inp) { inp.value = inp.type === 'date' ? '2026-08-22' : `ZZ${id}ZZ`; fire(inp); out.push(id); continue; }
    }
    return out;
  });
}

/* The page's own declarations, read out of its source: the draft key, the
   vocabulary spec handed to Lang.vocab, the remap plan handed to Lang.remapDraft. */
function declared(src) {
  const key = (src.match(/var KEY = "([^"]+)"/) || [])[1];
  const specTxt = (src.match(/Lang\.vocab\(\s*T\s*,\s*ES\s*,\s*(\{[^}]*\})\s*\)/) || [])[1];
  const planStart = src.indexOf('Lang.remapDraft(');
  let plan = null;
  if (planStart >= 0) {
    const open = src.indexOf('{', planStart);
    let depth = 0, i = open;
    for (; i < src.length; i++) { if (src[i] === '{') depth++; else if (src[i] === '}') { depth--; if (!depth) break; } }
    plan = new Function('return ' + src.slice(open, i + 1))();
  }
  const spec = specTxt ? new Function('return ' + specTxt)() : null;
  return { key, spec, plan };
}

function itemsOf(trade) {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(readFileSync(join(ROOT, trade, 'items.js'), 'utf8'), ctx);
  return ctx.window.TOOLKIT_ITEMS || {};
}
const enName = it => typeof it === 'string' ? it : (it.v !== undefined ? it.v : it.name);

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);
const notes = [];

const list = pages();
if (!list.length) { console.error('no page mounts shared/lang.js'); process.exit(1); }
const dirs = Array.from(new Set(['shared'].concat(list.map(p => p.split('/')[0]))));
const headDir = exportHead(dirs);
const work = await serve(ROOT);
const head = await serve(headDir);
const browser = await chromium.launch();

for (const rel of list) {
  const trade = rel.split('/')[0];
  const src = readFileSync(join(ROOT, rel), 'utf8');
  const { key, spec, plan } = declared(src);
  const items = itemsOf(trade);
  const T = items.tag || {}, ES = items.tag_es || {};

  /* ── 1. the twins are complete ─────────────────────────────────────── */
  if (!key) fail(rel, 'no `var KEY = "…"` — the remap and the mount must share one declared key');
  if (!spec) fail(rel, 'no Lang.vocab(T, ES, {…}) call found — the vocabulary is not mapped');
  if (!plan) fail(rel, 'no Lang.remapDraft(KEY, ES, {…}) call — a flip would leave saved picks untranslated');
  if (!/Lang\.toggle\(/.test(src)) fail(rel, 'Lang.toggle(api) is never called — the chips do nothing');
  if (!/Lang\.chrome\(/.test(src)) fail(rel, 'Lang.chrome({…}) is never called — the plate stays English in ES mode');
  if (spec) {
    for (const k of Object.keys(spec)) {
      const en = (T[k] || []).map(enName), es = ES[k] || [];
      if (!en.length) { fail(rel, `vocab "${k}" is mapped but items.js has no tag.${k}`); continue; }
      if (es.length !== en.length) { fail(rel, `tag_es.${k} has ${es.length} entries, tag.${k} has ${en.length} — every option needs its twin`); continue; }
      const enSet = new Set(en);
      for (const p of es) {
        if (!p || typeof p.es !== 'string' || typeof p.en !== 'string') { fail(rel, `tag_es.${k} entry is not { es, en }: ${JSON.stringify(p)}`); continue; }
        if (!enSet.has(p.en)) fail(rel, `tag_es.${k} twin "${p.en}" matches no EN option verbatim — the remap cannot find it`);
        if (!p.es.trim()) fail(rel, `tag_es.${k} "${p.en}" has an empty es`);
        if (spec[k] === 'plain' && p.es !== p.en && !/^[—-]/.test(p.en) && !/\(.+\)/.test(p.es)) fail(rel, `tag_es.${k} "${p.es}" is a <select> value and carries no (EN) twin of its own — the document prints it raw`);
      }
      const dup = es.map(p => p.es).filter((v, i, a) => a.indexOf(v) !== i);
      if (dup.length) fail(rel, `tag_es.${k} has two entries with the same es — the remap back to EN is ambiguous: ${dup.join(' | ')}`);
    }
  }

  /* ── 2. EN document byte-identical to HEAD ─────────────────────────── */
  const inHead = existsSync(join(headDir, rel));
  let enDoc = null, enTitle = null;
  {
    const a = await newCtx(browser, 'en-US');
    await a.page.goto(`http://127.0.0.1:${work.port}/${rel}`, { waitUntil: 'load' });
    await a.page.waitForSelector('[data-f]', { state: 'attached' });
    const lang = await a.page.evaluate(() => document.documentElement.lang);
    const lit = await a.page.evaluate(() => ({ en: document.getElementById('lang-en')?.classList.contains('on'), es: document.getElementById('lang-es')?.classList.contains('on') }));
    if (lang !== 'en') fail(rel, `an en-US phone opened with <html lang="${lang}">`);
    if (!lit.en || lit.es) fail(rel, `an en-US phone opened with the chips lit EN=${lit.en} ES=${lit.es}`);
    enTitle = await a.page.title();
    await driveAll(a.page);
    enDoc = await copied(a.page);
    if (a.errors.length) fail(rel, `page error(s) in EN: ${a.errors.join(' | ')}`);
    await a.ctx.close();
  }
  if (inHead) {
    const b = await newCtx(browser, 'en-US');
    await b.page.goto(`http://127.0.0.1:${head.port}/${rel}`, { waitUntil: 'load' });
    await b.page.waitForSelector('[data-f]', { state: 'attached' });
    await driveAll(b.page);
    const headDoc = await copied(b.page);
    await b.ctx.close();
    if (headDoc !== enDoc) {
      const al = headDoc.split('\n'), bl = enDoc.split('\n');
      let i = 0; while (i < al.length && i < bl.length && al[i] === bl[i]) i++;
      fail(rel, `the ENGLISH document changed against HEAD at line ${i + 1}:\n      HEAD: ${JSON.stringify(al[i] || '')}\n      now:  ${JSON.stringify(bl[i] || '')}`);
    }
  } else {
    notes.push(`${rel} is not in HEAD — new page, the EN identity check has nothing to compare to`);
  }

  /* ── 3. ES mode from an es-* phone: chips, lang, bilingual document ──── */
  {
    const c = await newCtx(browser, 'es-MX');
    await c.page.goto(`http://127.0.0.1:${work.port}/${rel}`, { waitUntil: 'load' });
    await c.page.waitForSelector('[data-f]', { state: 'attached' });
    const lang = await c.page.evaluate(() => document.documentElement.lang);
    if (lang !== 'es') fail(rel, `an es-MX phone opened with <html lang="${lang}"> — the phone's tongue is not followed`);
    const chips = await c.page.evaluate(() => ['lang-en', 'lang-es'].map(id => { const b = document.getElementById(id); if (!b) return null; const r = b.getBoundingClientRect(); return { on: b.classList.contains('on'), h: r.height, w: r.width, right: r.right, pressed: b.getAttribute('aria-pressed') }; }));
    if (!chips[0] || !chips[1]) fail(rel, 'the EN/ES chips are not on the page');
    else {
      if (!chips[1].on || chips[0].on) fail(rel, `es-MX phone: chips lit EN=${chips[0].on} ES=${chips[1].on}`);
      if (chips[1].pressed !== 'true' || chips[0].pressed !== 'false') fail(rel, `aria-pressed EN=${chips[0].pressed} ES=${chips[1].pressed}`);
      for (const [i, ch] of chips.entries()) if (ch.h < 44 || ch.w < 44) fail(rel, `${i ? 'ES' : 'EN'} chip is ${Math.round(ch.w)}×${Math.round(ch.h)}px — under the 44px thumb`);
    }
    const esTitle = await c.page.title();
    if (esTitle === enTitle) fail(rel, `the title did not change in ES ("${esTitle}")`);
    await driveAll(c.page);
    const esDoc = await copied(c.page);
    const firstLine = esDoc.split('\n')[0];
    if (!/ \/ /.test(firstLine)) fail(rel, `ES document name is not bilingual "ES / EN": ${JSON.stringify(firstLine)}`);
    /* every docHead the page declares must print bilingual */
    const heads = Array.from(src.matchAll(/docHead:\s*t\("([^"]+)",\s*"([^"]+)"\)/g));
    for (const [, en, es] of heads) {
      if (!es.includes(' / ')) fail(rel, `docHead "${es}" does not carry its English half`);
      if (!esDoc.includes(es)) fail(rel, `ES document is missing the head "${es}"`);
    }
    if (spec) {
      for (const k of Object.keys(spec)) {
        if (spec[k] === 'plain') continue;
        const last = (ES[k] || [])[(ES[k] || []).length - 1];
        /* the driver picked the LAST option of every control; a tick with a sub
           prints "es — sub (en)", exactly as Lang.tick composes it */
        if (last && last.es !== last.en) {
          const want = (spec[k] === 'tick' && last.sub) ? `${last.es} — ${last.sub} (${last.en})` : `${last.es} (${last.en})`;
          if (!esDoc.includes(want)) fail(rel, `the "ES (EN)" composition for vocab "${k}" did not reach the ES document (looked for ${JSON.stringify(want)})`);
        }
      }
    }
    if (c.errors.length) fail(rel, `page error(s) in ES: ${c.errors.join(' | ')}`);
    await c.ctx.close();
  }

  /* ── 4. the flip translates the draft, both ways ───────────────────── */
  if (key && plan) {
    const d = await newCtx(browser, 'en-US');
    const url = `http://127.0.0.1:${work.port}/${rel}`;
    await d.page.goto(url, { waitUntil: 'load' });
    await d.page.waitForSelector('[data-f]', { state: 'attached' });
    await driveAll(d.page);
    /* flush like the toggle does, then read the EN draft */
    const draftEn = await d.page.evaluate(k => { window.dispatchEvent(new Event('pagehide')); return JSON.parse(localStorage.getItem(k) || 'null'); }, key);
    if (!draftEn) fail(rel, `no draft under "${key}" after driving every field — the mount key and KEY disagree`);
    else {
      await Promise.all([d.page.waitForNavigation({ waitUntil: 'load' }), d.page.click('#lang-es')]);
      await d.page.waitForSelector('[data-f]', { state: 'attached' });
      const draftEs = await d.page.evaluate(k => JSON.parse(localStorage.getItem(k) || 'null'), key);
      const twin = (k, en) => { const p = (ES[k] || []).find(x => x.en === en); return p ? p.es : en; };
      for (const f of plan.singles || []) {
        const v = draftEn[f.id]; if (typeof v !== 'string' || !v) continue;
        if (draftEs[f.id] !== twin(f.key, v)) fail(rel, `flip EN→ES: "${f.id}" was "${v}", arrived as "${draftEs[f.id]}", expected "${twin(f.key, v)}"`);
      }
      for (const f of plan.lists || []) {
        const v = draftEn[f.id]; if (!Array.isArray(v)) continue;
        const want = v.map(n => twin(f.key, n));
        if (JSON.stringify(draftEs[f.id]) !== JSON.stringify(want)) fail(rel, `flip EN→ES: "${f.id}" ${JSON.stringify(v)} arrived as ${JSON.stringify(draftEs[f.id])}, expected ${JSON.stringify(want)}`);
      }
      for (const f of plan.rows || []) {
        const v = draftEn[f.id]; if (!Array.isArray(v)) continue;
        v.forEach((r, i) => { const got = draftEs[f.id] && draftEs[f.id][i] && draftEs[f.id][i][f.col]; if (r[f.col] && got !== twin(f.key, r[f.col])) fail(rel, `flip EN→ES: "${f.id}[${i}].${f.col}" was "${r[f.col]}", arrived as "${got}"`); });
      }
      const lit = await d.page.evaluate(() => document.getElementById('lang-es').classList.contains('on'));
      if (!lit) fail(rel, 'after tapping ES the ES chip is not lit');
      await Promise.all([d.page.waitForNavigation({ waitUntil: 'load' }), d.page.click('#lang-en')]);
      await d.page.waitForSelector('[data-f]', { state: 'attached' });
      const draftBack = await d.page.evaluate(k => JSON.parse(localStorage.getItem(k) || 'null'), key);
      const strip = o => { const c = JSON.parse(JSON.stringify(o)); return c; };
      if (JSON.stringify(strip(draftBack)) !== JSON.stringify(strip(draftEn))) {
        const ka = Object.keys(draftEn).filter(k2 => JSON.stringify(draftEn[k2]) !== JSON.stringify(draftBack[k2]));
        fail(rel, `flip EN→ES→EN did not come back verbatim — differs at ${ka.map(k2 => `${k2}: ${JSON.stringify(draftEn[k2])} → ${JSON.stringify(draftBack[k2])}`).join('; ')}`);
      }
    }
    if (d.errors.length) fail(rel, `page error(s) across the flip: ${d.errors.join(' | ')}`);
    await d.ctx.close();
  }

  /* ── 5. nothing overflows in Spanish, at four widths, filled in ────── */
  for (const w of [320, 360, 390, 430]) {
    const e = await newCtx(browser, 'es-MX', w);
    await e.page.goto(`http://127.0.0.1:${work.port}/${rel}`, { waitUntil: 'load' });
    await e.page.waitForSelector('[data-f]', { state: 'attached' });
    await driveAll(e.page);
    const m = await e.page.evaluate(() => {
      const de = document.documentElement;
      const tog = document.querySelector('.langtog');
      const r = tog ? tog.getBoundingClientRect() : null;
      let culprit = '';
      if (de.scrollWidth > de.clientWidth) {
        let worst = null, wr = 0;
        for (const el of document.querySelectorAll('body *')) { const b = el.getBoundingClientRect(); if (b.left < de.clientWidth && b.right > wr) { wr = b.right; worst = el; } }
        culprit = worst ? `${worst.tagName.toLowerCase()}${worst.className ? '.' + String(worst.className).split(' ')[0] : ''} right=${Math.round(wr)}` : '';
      }
      return { sw: de.scrollWidth, cw: de.clientWidth, togRight: r ? r.right : null, culprit };
    });
    if (m.sw > m.cw) fail(rel, `ES @${w}px overflows: scrollWidth ${m.sw} > clientWidth ${m.cw} (${m.culprit})`);
    if (m.togRight !== null && m.togRight > w + 0.5) fail(rel, `ES @${w}px: the language chips end at ${Math.round(m.togRight)}px, past the glass`);
    if (e.errors.length) fail(rel, `page error(s) in ES @${w}: ${e.errors.join(' | ')}`);
    await e.ctx.close();
  }
}

await browser.close();
work.s.close(); head.s.close();
rmSync(headDir, { recursive: true, force: true });

for (const n of notes) console.log('  · ' + n);
if (fails.length) {
  console.error(`\nLANG LAYER — ${fails.length} defect(s) across ${list.length} page(s):\n`);
  for (const f of fails) console.error('  ✗ ' + f);
  process.exit(1);
}
console.log(`LANG LAYER — PASS on ${list.length} page(s): EN document identical to HEAD, phone tongue followed, ES document bilingual, flip round-trips the draft, twins complete, no overflow in Spanish at 320/360/390/430, zero page errors.`);
