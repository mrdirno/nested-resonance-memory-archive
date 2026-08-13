/**
 * THE NO-THIRD-PARTY GATE — "nothing leaves this origin unless a man asked it to"
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * THE RAIL: self-contained client-side static pages only — no external API, no
 * third-party CDN, and a tool's own work never leaves the browser. Every tool
 * page in this program says a version of that to the user in its own warn block.
 *
 * WHY IT IS A GATE AND NOT A SENTENCE. On 2026-08-13 an end-to-end drive of a new
 * page reported one stray console error, and the stray error was
 * `shared/toolkit.js` calling `https://worldtimeapi.org/api/ip` on EVERY page
 * load of ALL 76 pages of ALL NINE TRADES — an unconsented request to somebody
 * else's server, to an endpoint that is by design an IP lookup, fired from pages
 * that promise the opposite. It had shipped, been reviewed, and been swept past
 * repeatedly, because nothing about it is visible: the page looks right, the
 * feature it powered (a date that survives a wrong tablet clock) was real and
 * good, and the request happens where nobody looks. A rule stated in a document
 * is a rule that loses to a well-meaning nicety. This is the rule as an
 * assertion.
 *
 * WHAT IT MEASURES. Every page derived from disk is loaded with nothing touched,
 * and EVERY request the page makes is checked against its own origin. No
 * interaction, because the question is specifically what fires unasked — the
 * wishing-well POST and the feedback POST are deliberate, consented acts behind
 * an explicit tap and are not this gate's business. `data:` and `blob:` URLs are
 * the page's own bytes and are allowed.
 *
 *   node tools/toolkit-gates/no-third-party.mjs [--only=slug/page.html]
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

/* Discovered exactly the way mobile-watertight discovers them, so the two gates
 * can never disagree about what "every page" means — a trade dir is one with a
 * trade.js, plus the commons. Two gates covering two different page sets is how
 * a page ends up green on the list nobody was looking at. */
function pages() {
  const dirs = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && existsSync(join(ROOT, d.name, 'trade.js')))
    .map(d => d.name)
    .concat(existsSync(join(ROOT, 'commons')) ? ['commons'] : [])
    .sort();
  const out = dirs.flatMap(dir =>
    readdirSync(join(ROOT, dir)).filter(f => f.endsWith('.html')).sort().map(f => `${dir}/${f}`));
  return ONLY ? out.filter(p => p === ONLY) : out;
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
const { s, port } = await new Promise(res => {
  const s = createServer((rq, rs) => {
    const rel = normalize(decodeURIComponent(rq.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
    const p = join(ROOT, rel);
    if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { rs.writeHead(404); return rs.end('no'); }
    rs.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    rs.end(readFileSync(p));
  });
  s.listen(0, '127.0.0.1', () => res({ s, port: s.address().port }));
});
const BASE = `http://127.0.0.1:${port}`;
const ORIGIN = BASE;

const browser = await chromium.launch();
const list = pages();
let fail = 0;

for (const p of list) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  const off = new Set();
  page.on('request', r => {
    const u = r.url();
    if (u.startsWith('data:') || u.startsWith('blob:') || u.startsWith('about:')) return;
    if (!u.startsWith(ORIGIN + '/')) off.add(r.resourceType() + ' ' + u);
  });
  try {
    await page.goto(`${BASE}/${p}`, { waitUntil: 'load' });
    // Give anything deferred to boot (the runtime resolves the date after av:ready).
    await page.waitForTimeout(1200);
  } catch (e) {
    console.log(`FAIL  ${p} — ${e.message}`); fail++; await ctx.close(); continue;
  }
  if (off.size) {
    console.log(`FAIL  ${p} — ${off.size} request(s) left the origin with nothing touched:`);
    [...off].forEach(u => console.log(`        ${u}`));
    fail++;
  } else {
    console.log(`PASS  ${p}`);
  }
  await ctx.close();
}

await browser.close();
s.close();
console.log(`\n${list.length} page(s) loaded untouched — ${fail} making third-party requests`);
process.exit(fail ? 1 : 0);
