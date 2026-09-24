/**
 * ONE TAP, ONE CHANGE — the job card under a double tap, on every page that mounts it.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * C3749 made the first tap on "+ Another job" land (it used to be eaten by the
 * repaint a blur triggered), and a man who had learned to tap twice now landed
 * his SECOND tap on whatever the new row put under his finger: at one job the
 * row is only that button, at two the label appears and the job he just left
 * sits where the button was. The second tap switched him back, and the next
 * house's name he typed renamed the job he had left — its lot, gate and PO with
 * it. Found by the C3751 audit with real touches; no gate drove a double tap.
 *
 * For every page that mounts shared/jobcard.js (found by its mount call, never a
 * list): type the job name, double-tap "+ Another job" with REAL CDP touches
 * (110 ms apart), then type the next house. Asserts the new job is current, the
 * cursor is still in the name box, and the first job keeps its name.
 *
 *   node tools/toolkit-gates/jobcard-retap.mjs [liveBaseUrl] [--only=trade/page.html]
 */
import { createRequire } from 'module';
import { readdirSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const ONLY = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const BASE = (args.find(a => /^https?:\/\//.test(a)) || 'file://' + ROOT).replace(/\/*$/, '/');

function pages() {
  const out = [];
  for (const d of readdirSync(ROOT, { withFileTypes: true })) {
    if (!d.isDirectory() || d.name.startsWith('.') || !existsSync(join(ROOT, d.name, 'tools.js'))) continue;
    for (const f of readdirSync(join(ROOT, d.name)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, d.name, f), 'utf8');
      if (/JobCard\.mount\(/.test(src)) out.push(`${d.name}/${f}`);
    }
  }
  return out.filter(p => !ONLY || p === ONLY).sort();
}

const b = await chromium.launch({ args: ['--mute-audio'] });
const fails = [];
let n = 0;
for (const page of pages()) {
  n++;
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  try {
    await p.goto(BASE + page, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(300);
    const name = await p.evaluate(() => {
      const f = document.querySelector('#fJob') || document.querySelector('.jc ~ .hgrid input[type=text], input[type=text]');
      return f ? (f.id ? '#' + f.id : null) : null;
    });
    if (!name) { fails.push(`${page}: no job-name field to type in`); await ctx.close(); continue; }
    const cdp = await ctx.newCDPSession(p);
    await p.focus(name);
    await p.keyboard.type('412 Marchmont');
    const bb = await p.locator('.jc-chip.jc-new').boundingBox();
    if (!bb) { fails.push(`${page}: no "+ Another job" button`); await ctx.close(); continue; }
    const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2;
    const tap = async () => {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y, id: 1 }] });
      await new Promise(r => setTimeout(r, 50));
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    };
    await tap();
    await new Promise(r => setTimeout(r, 110));
    await tap();
    await p.waitForTimeout(400);
    const s = await p.evaluate(nm => ({
      focus: document.activeElement === document.querySelector(nm),
      cur: (document.querySelector('.jc-chip.on') || {}).textContent || '',
      chips: [...document.querySelectorAll('.jc-chip:not(.jc-new)')].map(c => c.textContent)
    }), name);
    await p.keyboard.type('88 Linden');
    await p.waitForTimeout(300);
    const after = await p.evaluate(() => [...document.querySelectorAll('.jc-chip:not(.jc-new)')].map(c => c.textContent + (c.classList.contains('on') ? '*' : '')));
    if (/412 Marchmont/.test(s.cur)) fails.push(`${page}: the second tap switched back to the job he just left (${JSON.stringify(s.chips)})`);
    if (!s.focus) fails.push(`${page}: the double tap took the cursor out of the name box`);
    if (!after.includes('412 Marchmont') || !after.some(c => /88 Linden\*/.test(c))) fails.push(`${page}: after the double tap the next house's name went to the wrong job (${JSON.stringify(after)})`);
    if (errs.length) fails.push(`${page}: page errors: ${errs[0]}`);
    console.log((fails.some(f => f.startsWith(page)) ? '  ✗ ' : '  ok ') + page);
  } catch (e) {
    fails.push(`${page}: ${String(e).split('\n')[0]}`);
  }
  await ctx.close();
}
await b.close();
if (fails.length) {
  console.log('\n' + fails.map(f => '  ✗ ' + f).join('\n'));
  console.log(`\nJOBCARD RETAP — ${fails.length} failing over ${n} page(s)`);
  process.exit(1);
}
console.log(`\nPASS — ${n} page(s): a double tap on "+ Another job" makes one job, keeps the cursor, and the next name goes to the new job.`);
