'use strict';
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1100, height: 760 } });
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 120000, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.keyboard.press('7');
  await page.waitForTimeout(300);
  await page.evaluate(() => document.querySelector('#lab-exp-seg button[data-exp="disc"]').click());
  // let the meter fill in
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) { await page.waitForTimeout(1000); const l = await page.textContent('#lab-lambda'); const c = await page.textContent('#lab-clamp'); if (/\/s/.test(l) && /%/.test(c) && !/^0%/.test(c.trim())) break; }
  await page.evaluate(() => { const p = document.querySelector('#panel-lab .panel-body'); if (p) p.scrollTop = 0; });
  await page.screenshot({ path: path.join(__dirname, 'shots', '83-lab-experiments.png') });
  await page.evaluate(() => { const p = document.querySelector('#panel-lab .panel-body'); if (p) p.scrollTop = 900; });
  await page.screenshot({ path: path.join(__dirname, 'shots', '84-lab-experiments-scrolled.png') });
  console.log('readouts:', await page.textContent('#lab-lambda'), '|', await page.textContent('#lab-clamp'), '|', await page.textContent('#lab-pairs'));
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
