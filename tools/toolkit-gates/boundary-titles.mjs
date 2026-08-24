/**
 * BOUNDARY-PAGE TITLES — the tab says what the config says.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * The three boundary pages are one page file copied per trade; the runtime
 * swaps the on-page text from the trade's config, but <title> and the
 * apple-mobile-web-app-title are baked and the runtime never touches them —
 * they are what a browser tab, a bookmark, a home-screen icon and a link
 * preview show. Found 2026-08-24 (C3654): sitework's rough-in page wore
 * masonry's <title> over concrete's apple-title while its own config said
 * "Before We Dig"; sitework's answer page wore masonry's title; three trades'
 * apple-titles said concrete's "What I'll Set". Stand-ups copy a sibling and
 * patch the lines somebody remembers — this asserts the two lines nobody does.
 *
 *   node tools/toolkit-gates/boundary-titles.mjs
 */
import { readdirSync, readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { join } from 'path';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const PAGES = {
  'rough-in-request.html': 'TOOLKIT_ROUGHIN',
  'answer-back.html': 'TOOLKIT_ANSWER',
  'notes-back.html': 'TOOLKIT_ANSWER',
  'getting-in.html': 'TOOLKIT_GETIN',
};

const norm = s => String(s || '')
  .replace(/&rsquo;|&#8217;/g, '’').replace(/&amp;/g, '&')
  .replace(/[’']/g, "'").trim();

function toolName(itemsSrc, blk) {
  const m = itemsSrc.match(new RegExp('window\\.' + blk + '\\s*=\\s*\\{([\\s\\S]*?)\\n\\};'));
  if (!m) return null;
  const f = m[1].match(/["']?toolName["']?\s*:\s*"((?:[^"\\]|\\.)*)"/);
  return f ? f[1].replace(/\\"/g, '"') : null;
}

const fails = [];
let checked = 0;
const trades = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
  .map(d => d.name).sort();

for (const t of trades) {
  const itemsPath = join(ROOT, t, 'items.js');
  if (!existsSync(itemsPath)) continue;
  const items = readFileSync(itemsPath, 'utf8');
  for (const [page, blk] of Object.entries(PAGES)) {
    const p = join(ROOT, t, page);
    if (!existsSync(p)) continue;
    const cfg = toolName(items, blk);
    if (!cfg) continue; // page without a config falls back wholesale — other gates own that
    checked++;
    const src = readFileSync(p, 'utf8');
    const rel = `${t}/${page}`;
    const ttl = (src.match(/<title>([^<]*)<\/title>/) || [])[1] || '';
    const pageName = norm(ttl.split(' — ')[0]);
    if (pageName !== norm(cfg)) {
      fails.push(`${rel}  <title> says “${ttl.split(' — ')[0]}” — its own config says “${cfg}”. The tab and the link preview are wearing another trade's name.`);
    }
    const ap = (src.match(/apple-mobile-web-app-title" content="([^"]*)"/) || [])[1];
    if (ap && norm(ap) !== norm(cfg)) {
      fails.push(`${rel}  apple-title says “${ap}” — its own config says “${cfg}”. That is the name a home-screen icon gets.`);
    }
  }
}

if (fails.length) {
  console.error(`BOUNDARY TITLES — ${fails.length} defect(s) across ${checked} page(s):`);
  for (const f of fails) console.error('  ' + f);
  process.exit(1);
}
console.log(`BOUNDARY TITLES — ${checked} page(s) clean: every tab, bookmark and home-screen name is the trade's own.`);
