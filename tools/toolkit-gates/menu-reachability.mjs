/**
 * THE TOOLS-MENU REACHABILITY GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * Encodes wishing-well bug a596d8c9, reported from the field against
 * /av/consumables.html: "the tools modal when populated has no scroll so
 * whatever is on the bottom of the tools modal gets cutoff".
 *
 * CAUSE: .av-drop was bounded by calc(100vh - 72px). 100vh is the LARGE
 * viewport — the page height as if the browser's chrome were hidden — so on iOS
 * Safari with the URL bar showing it is ~130px taller than the glass. The menu
 * was built taller than the screen and the scroller was told it fit, which is
 * why it scrolled a little and then stopped with its bottom still cut off.
 *
 * Chromium ALONE CANNOT SEE THIS BUG: there 100vh === window.innerHeight, so
 * every naive check passes. Pass B below reproduces the real condition by
 * running at the large viewport while innerHeight reports the true glass —
 * which is exactly what iOS does. Against the pre-fix runtime it measured the
 * last row 110.4px below the glass on every page of every trade.
 *
 *   node tools/toolkit-gates/menu-reachability.mjs [base-url]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy:
 *   node tools/toolkit-gates/menu-reachability.mjs \
 *     https://mrdirno.github.io/nested-resonance-memory-archive/
 */
import { createRequire } from 'module';
import { readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';

// The repo's only browser driver lives with Collage Studio; resolve it from
// here rather than installing a second copy.
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
/* THE TRAILING SLASH IS LOAD-BEARING, so it is not left to whoever types the
 * command. Pages are joined as BASE + page with a repo-relative path, so a base
 * pasted without it builds `…/nested-resonance-memory-archiveav/index.html` —
 * every page 404s, every page reports no Tools menu, and this gate then printed
 * PASS over ZERO checks. Measured exactly that on 2026-08-17: "0 page x viewport
 * checks over 0 toolkit pages (117 page(s) carry no Tools menu)", exit 0, while
 * the menu was live and working on all twelve trades. */
const BASE = (process.argv[2] || 'file://' + ROOT).replace(/\/*$/, '/');

// Every dir that declares a trade, plus the commons — derived from disk so a new
// trade is covered the day it lands, with no edit here.
const DIRS = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js'))
  .map(d => d.name)
  .concat(existsSync(ROOT + 'commons') ? ['commons'] : [])
  .sort();

const PAGES = [];
for (const d of DIRS) {
  for (const f of readdirSync(ROOT + d).filter(f => f.endsWith('.html')).sort()) PAGES.push(`${d}/${f}`);
}

// Pass A: ordinary phone glass. Pass B: the iOS condition (large viewport that
// 100vh sees, paired with the smaller glass the eye and innerHeight see).
const PASS_A = [{ w: 320, h: 480 }, { w: 360, h: 600 }, { w: 390, h: 664 }, { w: 430, h: 745 }];
const PASS_B = [{ w: 390, h: 794, glass: 664 }, { w: 430, h: 883, glass: 745 }, { w: 360, h: 730, glass: 600 }];

const browser = await chromium.launch();
const fails = [];
let checked = 0, skipped = 0, tightest = { margin: Infinity };

async function check(page, vp, glass) {
  const ctx = await browser.newContext({
    viewport: { width: vp.w, height: vp.h }, isMobile: true, hasTouch: true, deviceScaleFactor: 2,
  });
  if (glass) await ctx.addInitScript(g => {
    Object.defineProperty(window, 'innerHeight', { get: () => g, configurable: true });
  }, glass);
  const p = await ctx.newPage();
  await p.goto(BASE + page, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(120);
  if (!(await p.$('.av-menu > button'))) { await ctx.close(); return null; }
  await p.click('.av-menu > button');
  await p.waitForTimeout(140);

  const r = await p.evaluate(() => {
    const glass = window.innerHeight;
    const drop = document.querySelector('.av-drop');
    const box = drop.getBoundingClientRect();

    // A page's own bottom action dock may overlap the menu. That is FINE while the
    // menu paints on top of it (the bar is z-index 40; page docks measured 20-30),
    // and reserving space for one would only shorten the menu. But if a page ever
    // ships a dock ABOVE the bar its rows really would be hidden — so hit-test.
    let dockSel = null, dockTop = glass;
    for (const el of document.body.getElementsByTagName('*')) {
      if (el === window.__avMenu || window.__avMenu.contains(el)) continue;
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' || cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;
      const b = el.getBoundingClientRect();
      if (b.height < 8 || b.width < 8) continue;
      if (b.bottom < glass - 4 || b.top > glass - 8 || b.top < glass * 0.35) continue;
      if (b.right <= box.left + 4 || b.left >= box.right - 4) continue;
      if (b.top < dockTop) { dockTop = b.top; dockSel = el.tagName.toLowerCase() + '.' + String(el.className || '').split(' ')[0]; }
    }
    let dockCovers = false;
    if (dockSel) {
      const hit = document.elementFromPoint(box.left + 20, Math.min(box.bottom, glass) - 6);
      dockCovers = !(hit && window.__avMenu.contains(hit));
    }

    // Drive it the way a thumb would: scroll the menu to its very end, then ask
    // whether the last row is on the glass.
    drop.scrollTop = drop.scrollHeight;
    const rows = drop.querySelectorAll('a');
    const last = rows[rows.length - 1].getBoundingClientRect();
    const de = document.documentElement;
    return {
      glass, dockSel, dockCovers,
      overhang: +(last.bottom - glass).toFixed(1),
      label: (rows[rows.length - 1].textContent || '').trim().slice(0, 20),
      hOverflow: de.scrollWidth - de.clientWidth,
      // the scroll cue must survive: 4 background layers say it parsed
      layers: getComputedStyle(drop).backgroundImage.split(/,(?![^(]*\))/).length,
      maxH: getComputedStyle(drop).maxHeight,
    };
  });
  await ctx.close();
  return r;
}

for (const page of PAGES) {
  let sawMenu = false;
  for (const [label, set] of [['A', PASS_A], ['B', PASS_B]]) {
    for (const vp of set) {
      const r = await check(page, vp, vp.glass);
      if (!r) continue;
      sawMenu = true; checked++;
      const where = `${page} @${vp.w}x${vp.h}${vp.glass ? ` glass ${vp.glass} [iOS]` : ''}`;
      const bad = [];
      if (r.overhang > 0) bad.push(`last row "${r.label}" is ${r.overhang}px below the glass — UNREACHABLE (max-height ${r.maxH})`);
      if (r.hOverflow > 0) bad.push(`${r.hOverflow}px horizontal overflow`);
      if (r.dockCovers) bad.push(`page dock ${r.dockSel} paints OVER the menu — its rows are hidden`);
      if (r.layers < 4) bad.push(`scroll cue did not parse (${r.layers} background layer(s))`);
      if (bad.length) fails.push(`${where}: ${bad.join('; ')}`);
      else if (-r.overhang < tightest.margin) tightest = { margin: -r.overhang, where };
    }
  }
  if (!sawMenu) skipped++;
}

await browser.close();
console.log(`\nmenu-reachability: ${checked} page x viewport checks over ${PAGES.length - skipped} toolkit pages ` +
            `in ${DIRS.length} dir(s) (${skipped} page(s) carry no Tools menu)`);
console.log(`base: ${BASE}`);
if (fails.length) {
  console.log(`\n${fails.length} FAILURE(S):`);
  fails.forEach(f => console.log('  FAIL ' + f));
  process.exit(1);
}
/* ZERO CHECKS IS NOT A PASS. A gate whose finding-list is empty because it never
 * looked reports exactly like one that looked everywhere and found nothing, and
 * this one did: a base URL missing its slash skipped all 117 pages and printed
 * the green line below with `tightest clearance: Infinitypx (undefined)` — a
 * number that is unreachable when any page is measured, and was sitting in the
 * output being ignored. The same silence arrives from a renamed selector or a
 * timeout too short for a slow host, and both are worth failing on. Anything
 * that legitimately has no menu is already counted in `skipped`, so the only
 * state this rejects is having measured NOTHING. */
if (!checked) {
  console.log(`\nFAIL — 0 checks ran. ${PAGES.length} page(s) were found and every one of them ` +
              `reported no Tools menu, so nothing was measured and there is nothing to pass.`);
  console.log(`  Usually the base URL: pages are fetched as BASE + a repo-relative path, ` +
              `so check ${BASE} actually serves ${BASE}${PAGES[0] || 'av/index.html'} .`);
  process.exit(1);
}
console.log(`PASS — the last row of the Tools menu is reachable everywhere, including under the iOS ` +
            `large-viewport condition; zero horizontal overflow; scroll cue intact.`);
console.log(`tightest clearance: ${tightest.margin}px  (${tightest.where})`);
