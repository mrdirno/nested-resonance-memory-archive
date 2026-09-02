'use strict';
/* memory_throughput.js — TIMING ONLY. Non-scoring feasibility pilot for the
   pre-registered memory test.
 
   This script deliberately reads NO memory index, NO Retained, NO Two-back and
   NO lab log. It measures one thing: how many simulated seconds of the fixed
   1/20 s physics tick the page advances per second of wall clock, at a given
   particle count, per-frame tick budget, and GL backend. Its only purpose is to
   fix the particle count and the run plan BEFORE the protocol is registered.
 
   Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SW = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'];
const GPU = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist',
             '--enable-features=Vulkan,UseSkiaRenderer', '--disable-gpu-sandbox', '--no-sandbox'];

const CASES = [];
for (const backend of ['gpu', 'swiftshader']) {
  for (const n of [262144, 1048576, 4194304]) {
    for (const budget of [1, 10]) CASES.push({ backend, n, budget });
  }
}

const MEASURE_WALL_MS = 20000;   // 20 s of wall clock per case
const results = [];

async function runCase(c) {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: c.backend === 'gpu' ? GPU : SW,
  });
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.addInitScript(n => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {}
  }, c.n);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 180000 });
  await page.waitForTimeout(800);

  const gl = await page.evaluate(() => {
    const g = window.__probe.renderer.getContext();
    const d = g.getExtension('WEBGL_debug_renderer_info');
    return { renderer: d ? g.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'unknown',
             float: !!g.getExtension('EXT_color_buffer_float') };
  });

  await page.evaluate(() => document.querySelector('[data-scn="spinchladni"]').click());
  await page.waitForTimeout(400);
  const applied = await page.evaluate(({ n, budget }) => {
    const P = window.__probe;
    const s = JSON.parse(JSON.stringify(P.state));
    s.particles = n; s.quality = 0.5;
    s.sound = Object.assign({}, s.sound, { level: 0 });
    s.cosmos = Object.assign({}, s.cosmos, { selfgrav: 0.3, epoch: true, epochLen: 10, cascade: 'out' });
    s.lab = { on: true };
    P.applyPreset({ state: s, step: 9028 });
    P.reseed();
    window.__forceDt = budget * 0.05;
    window.__tickBudget = budget;
    window.__t0 = P.simTime;
    window.__s0 = P.step;
    return { particles: P.state.particles, texSize: P.texSize };
  }, c);

  const wall0 = Date.now();
  await page.waitForTimeout(MEASURE_WALL_MS);
  const adv = await page.evaluate(() => ({ dt: window.__probe.simTime - window.__t0,
                                           dstep: window.__probe.step - window.__s0 }));
  const wall = (Date.now() - wall0) / 1000;
  await browser.close();

  return { ...c, gl: gl.renderer, floatRT: gl.float, particles: applied.particles, texSize: applied.texSize,
           simSec: +adv.dt.toFixed(2), ticks: adv.dstep, wall: +wall.toFixed(1),
           simPerWall: +(adv.dt / wall).toFixed(3), ticksPerSec: +(adv.dstep / wall).toFixed(2),
           errs: errs.slice(0, 3) };
}

(async () => {
  for (const c of CASES) {
    let row;
    try { row = await runCase(c); }
    catch (e) { row = { ...c, failed: String(e).slice(0, 200) }; }
    results.push(row);
    console.log([row.backend.padEnd(12), String(row.particles || row.n).padStart(8),
      'budget ' + row.budget, (row.gl || 'FAILED').slice(0, 46).padEnd(48),
      row.failed ? row.failed : `sim ${row.simSec}s / wall ${row.wall}s = ${row.simPerWall} x   ticks/s ${row.ticksPerSec}`,
      row.errs && row.errs.length ? 'ERR:' + row.errs[0].slice(0, 60) : ''].join(' '));
    fs.writeFileSync(path.join(__dirname, 'memory_throughput.json'), JSON.stringify(results, null, 1));
  }
  console.log('\nTIMING ONLY — no memory value was read by this script.');
})().catch(e => { console.error('crashed:', e); process.exit(2); });
