/**
 * THE NO-CLOCK GATE — silence is never a yes, in the document that leaves.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY IT EXISTS. Every freelance and field delivery template in circulation
 * carries some version of "please review within N days, after which the work is
 * considered accepted". It is the single most-copied sentence in the genre and
 * it is banned on this rack, because a page with no channel back may never
 * certify anything and a receiver who spots one reads the whole message as fine
 * print. The rule has been written down three times and has still had to be cut
 * out of shipped work twice — once from `creative/docs.js` in the 2026-08-15
 * adversarial fan-out ("I'll work to it as written if I don't hear back"), and
 * once as a pre-selected default that converted a client's silence into a spec
 * nobody chose. A rule that lives only in a document is a rule the twentieth
 * page forgets, so this is the rule as an ASSERTION.
 *
 * WHAT IT MEASURES, and why here rather than in the source. It reads the
 * DOCUMENT — what the real page puts in #preview after every control on it has
 * been driven — not the source, and not the prose on the glass. That boundary is
 * the whole design: the toolkit's own teaching copy is FULL of this vocabulary
 * on purpose (`cut-note` tells a man in as many words that silence reads as
 * agreement, which is a warning, not a clause), and a gate that matched source
 * strings would fail the pages doing the right thing while missing a clause
 * assembled at runtime out of two harmless halves. The artefact that leaves the
 * browser is the only thing that can carry the defect, so the artefact is what
 * is measured.
 *
 * IT DERIVES ITS PAGES FROM DISK — every `<trade>/*.html` carrying a #preview,
 * whatever shape it is. A trade shipped next month is covered the day it lands.
 *
 *   node tools/toolkit-gates/no-clock.mjs [base-url] [--only=slug/page.html]
 *
 * Default base is a local static server over the working tree. Pass the live URL
 * after a deploy to re-drive it against the artifact.
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
const BASE = args.find(a => /^https?:\/\//.test(a)) || '';

/* THE CLAUSE FAMILY. Each one is the AFFIRMATIVE construction only — "silence is
 * not a yes" is a sentence this program deliberately ships and must never fail.
 * The test the receiving lens gave, and it is mechanical: a verb with legal
 * weight (accepted · approved · final) attached to a timer or to silence. */
const CLAUSES = [
  [/\b(deemed|considered)\s+(to\s+be\s+)?(approved|accepted|final|complete|signed[-\s]?off)\b/i, 'deemed/considered approved'],
  [/\b(approved|accepted|final)\b[^.!?]{0,70}\bif\s+(i|we)\s+(don'?t|do not)\s+hear\b/i, 'approved if I don’t hear back'],
  [/\bif\s+(i|we)\s+(don'?t|do not)\s+hear[^.!?]{0,60}\b(i'?ll|we'?ll|i will|we will)\s+(proceed|assume|treat|take|go ahead)\b/i, 'silence → I proceed'],
  [/\bunless\s+(i|we)\s+hear[^.!?]{0,70}\b(approved|accepted|final|proceed|assume|go ahead)\b/i, 'unless I hear otherwise'],
  [/\bwithin\s+\d+\s+(business\s+)?days?\b[^.!?]{0,90}\b(approved|accepted|final|closed)\b/i, 'a review window with a verdict on the end of it'],
  [/\byour\s+silence\b/i, 'your silence'],
  [/\bno\s+(reply|response)\b[^.!?]{0,50}\b(approval|accepted|agreement|means yes)\b/i, 'no reply means yes'],
];

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
      /* THE SECOND TONGUE IS A SECOND DOCUMENT. Twelve pages carry a trade's
         `tag_es` vocabulary behind shared/lang.js, and the ES text renders only
         when localStorage says so — so a clause planted in the Spanish half is
         invisible to a gate that loads the page and reads it. Found by running
         this gate's own control (2026-09-03): the planted clause went in at the
         wrong offset, landed in `tag_es`, and the gate stayed green on a page
         that was carrying it. Every bilingual page is driven twice. */
      if (/id="preview"/.test(src)) out.push({ page: `${t}/${f}`, langs: /shared\/lang\.js/.test(src) ? ['en','es'] : ['en'] });
    }
  }
  return ONLY ? out.filter(p => p.page === ONLY) : out;
}

const MIME = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml' };
async function serve() {
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

/* DRIVE EVERYTHING, because a clause can hide behind a control nobody clicked.
 * Every checkbox on, every text field carrying a marker, every select moved off
 * its default — then read what the page decided to say. */
const DRIVE = () => {
  const fire = (el, ...names) => names.forEach(n => el.dispatchEvent(new Event(n, { bubbles: true })));
  document.querySelectorAll('input[type=checkbox]').forEach(cb => { if (!cb.checked) cb.click(); });
  document.querySelectorAll('input[type=text], input:not([type]), input[type=date], input[type=tel], input[type=email], textarea')
    .forEach(el => { if (!el.value) { el.value = 'XQZ'; fire(el, 'input', 'change'); } });
  document.querySelectorAll('select').forEach(sel => {
    if (sel.options.length > 1) { sel.selectedIndex = sel.options.length - 1; fire(sel, 'change', 'input'); }
  });
  document.querySelectorAll('input[type=radio]').forEach(r => { if (!r.checked) r.click(); });
  return (document.getElementById('preview') || {}).textContent || '';
};

const list = pages();
const srv = BASE ? null : await serve();
const base = BASE || `http://127.0.0.1:${srv.port}/`;
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
let checked = 0, failing = 0;
for (const { page, langs } of list) {
  for (const lang of langs) {
    const p = await ctx.newPage();
    try {
      const href = new URL(page, base).href;
      if (lang !== 'en') {
        await p.goto(href, { waitUntil: 'domcontentloaded' });
        await p.evaluate(l => { try { localStorage.setItem('toolkit.lang', l); } catch (e) {} }, lang);
      }
      await p.goto(href, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(220);
      let doc = '';
      try { doc = await p.evaluate(DRIVE); } catch (e) { doc = ''; }
      await p.waitForTimeout(140);
      try { doc += '\n' + await p.$eval('#preview', e => e.textContent); } catch (e) {}
      checked++;
      const hits = CLAUSES.filter(([rx]) => rx.test(doc));
      if (hits.length) {
        failing++;
        console.log(`FAIL  ${page}${lang === 'en' ? '' : '  [' + lang + ']'}`);
        hits.forEach(([rx, name]) => console.log(`        ${name} — ${JSON.stringify((doc.match(rx) || [])[0])}`));
      }
    } finally { await p.close(); }
  }
}
await b.close(); if (srv) srv.s.close();
console.log(`\n${checked} document(s) driven and read — ${failing} carrying a clock`);
process.exit(failing ? 1 : 0);
