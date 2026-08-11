/**
 * THE ROW-LOG COMMIT-MERGE GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * Encodes §SCARS 2026-08-10 "THE PENCIL SHEET HOLDS A PHOTOGRAPH, AND SAVE PUTS
 * IT BACK", which named itself a CLASS rather than a bug and asked for "a gate
 * across all of them, not a patch". This is that gate.
 *
 * THE DEFECT: the edit bar is a SNAPSHOT of a row taken when the pencil opened,
 * and while it sits open the row underneath can still move — the tap ladder
 * advances it, the walk settles it. `commit()` used to write the whole snapshot
 * back, so Save silently reverted field verification a man had walked out and
 * confirmed. Nothing on screen changes when it happens, which is why it survived
 * every look.
 *
 * WHAT THIS ASSERTS, on the REAL page in a REAL browser: add a row, open the
 * pencil, advance the row while the editor is open, press Save — and the status
 * that was advanced must survive. Measured 16/16 row-log pages FAILING before
 * the fix and 16/16 passing after; the pre-fix run is the part that matters,
 * because a test that passes on both the broken and the fixed code is evidence
 * of nothing.
 *
 * The page list is derived from disk, so a row-log page shipped next month is
 * covered the day it lands:
 *   node tools/toolkit-gates/rowlog-commit-merge.mjs [base-url]
 * Default base is a LOCAL SERVER (these pages need same-origin scripts, so
 * file:// will not do); pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync, readFileSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');
const ROOT = fileURLToPath(new URL('../../', import.meta.url));

const BASE = process.env.BASE || 'http://127.0.0.1:8777';
/* Every page that mounts the row-log engine, found rather than listed. */
const PAGES = (process.env.PAGES || readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js'))
  .map(d => d.name).sort()
  .flatMap(dir => readdirSync(ROOT + dir)
    .filter(f => f.endsWith('.html') && readFileSync(ROOT + dir + '/' + f, 'utf8').includes('shared/rowlog.js'))
    .sort().map(f => `${dir}/${f}`))
  .join(',')).split(',').filter(Boolean);

const browser = await chromium.launch();
let failures = 0;

for (const page of PAGES) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto(`${BASE}/${page}`, { waitUntil: 'networkidle' });
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await p.reload({ waitUntil: 'networkidle' });

  // Fill every visible control in the add bar, then Add one row.
  const added = await p.evaluate(() => {
    const bar = document.querySelector('.rl-bar') || document.getElementById('rlBar')
      || document.querySelector('[class*="rl-"]')?.closest('div');
    const scope = document.querySelector('#rlAdd')?.closest('div, form, section') || document;
    let n = 0;
    scope.querySelectorAll('input[type=text], input:not([type]), textarea').forEach((el) => {
      if (el.offsetParent === null) return;
      el.value = 'TEST-' + (++n);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    scope.querySelectorAll('select').forEach((el) => {
      if (el.offsetParent === null) return;
      if (el.options.length > 1) { el.selectedIndex = 1; el.dispatchEvent(new Event('change', { bubbles: true })); }
    });
    document.getElementById('rlAdd').click();
    return { adv: document.querySelectorAll('[data-adv]').length, rows: document.querySelectorAll('[data-edit]').length };
  });

  if (!added.rows) { console.log(`FAIL ${page}: could not add a row`); failures++; await ctx.close(); continue; }
  if (!added.adv) { console.log(`SKIP ${page} — no status ladder on this config`); await ctx.close(); continue; }

  const r = await p.evaluate(() => {
    const advBtn = () => document.querySelector('[data-adv]');
    const id = advBtn().getAttribute('data-adv');
    const chipOf = () => {
      const row = document.querySelector(`[data-adv="${id}"]`);
      return (row.textContent || '').trim();
    };

    // 1. advance the row once from the list (this is the tap ladder)
    advBtn().click();
    const afterFirstTap = chipOf();

    // 2. open the pencil on that row  →  the bar now holds a PHOTOGRAPH of it
    document.querySelector(`[data-edit="${id}"]`).click();
    const inEdit = document.getElementById('rlAdd').textContent.trim();

    // 3. advance the row AGAIN while the pencil sits open — this is the move the
    //    walk makes, reduced to its smallest reproducible form
    document.querySelector(`[data-adv="${id}"]`).click();
    const afterSecondTap = chipOf();

    // 4. Save the still-open editor
    document.getElementById('rlAdd').click();
    const afterSave = chipOf();

    return { inEdit, afterFirstTap, afterSecondTap, afterSave };
  });

  const ok = r.afterSave === r.afterSecondTap;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${page}`);
  console.log(`   pencil opened as "${r.inEdit}"`);
  console.log(`   after 1st tap : ${JSON.stringify(r.afterFirstTap)}`);
  console.log(`   after 2nd tap : ${JSON.stringify(r.afterSecondTap)}   (pencil open)`);
  console.log(`   after Save    : ${JSON.stringify(r.afterSave)}`);
  if (!ok) { console.log('   ^ Save reverted the row to the snapshot the pencil took.'); failures++; }
  if (errs.length) { console.log('   pageerror: ' + errs.join(' | ')); failures++; }
  await ctx.close();
}

await browser.close();
console.log(failures ? `\n${failures} FAILURE(S)` : '\nall green');
process.exit(failures ? 1 : 0);
