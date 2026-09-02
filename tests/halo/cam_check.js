'use strict';
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 900, height: 640 } });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.addInitScript(() => { try { if (!localStorage.getItem('resonance-chamber-v2')) localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(800);
  const c = await page.evaluate(() => ({ az: document.getElementById('cam-az') && document.getElementById('cam-az').textContent, user: window.__probe.state.cam.user, st: JSON.stringify(window.__probe.state.cam), stored: localStorage.getItem('resonance-chamber-v2').slice(0, 200) }));
  console.log('after boot with stored user cam:', JSON.stringify(c));
  // now drag, wait, reload (the smoke path)
  const box = await page.evaluate(() => { const r = document.querySelector('canvas').getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; });
  await page.mouse.move(box.x, box.y); await page.mouse.down(); await page.mouse.move(box.x + 150, box.y + 60, { steps: 8 }); await page.mouse.up();
  await page.waitForTimeout(2500);
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('resonance-chamber-v2')).cam);
  console.log('stored after drag:', JSON.stringify(stored));
  await page.reload();
  const rawEarly = await page.evaluate(() => localStorage.getItem('resonance-chamber-v2'));
  console.log('raw storage right after reload:', String(rawEarly).slice(0, 160));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(800);
  const c2 = await page.evaluate(() => ({ st: JSON.stringify(window.__probe.state.cam), stored: JSON.parse(localStorage.getItem('resonance-chamber-v2')).cam,
    hud: ['cam-az', 'cam-el', 'cam-dist'].map(id => document.getElementById(id) && document.getElementById(id).textContent) }));
  console.log('after reload (immediately):', JSON.stringify(c2));
  await page.waitForTimeout(2500);
  const c3 = await page.evaluate(() => ({ st: JSON.stringify(window.__probe.state.cam), hud: ['cam-az', 'cam-el', 'cam-dist'].map(id => document.getElementById(id) && document.getElementById(id).textContent) }));
  console.log('after reload (+2.5 s):', JSON.stringify(c3));
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
