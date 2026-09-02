'use strict';
/* memory_budget_identity.js — the kill-test for the test build's tick-budget hook.
 
   The shipped page issues at most 2 physics ticks per rendered frame, so simulated
   time can never outrun the wall clock. The test build adds window.__tickBudget,
   which raises that cap. The claim this test exists to break: because the tick is
   FIXED (TICK = 1/20 s) and simTick() takes no wall-clock argument, issuing the same
   number of ticks in fewer frames must give the SAME trajectory.
 
   Method: identical seeded initial conditions (Math.random is replaced by a seeded
   LCG before reseed), identical settings, exactly 200 physics ticks, advanced once
   as 200 frames x 1 tick and once as 20 frames x 10 ticks. Frames are stepped one
   at a time from the driver so both runs land on exactly the same step count.
   Then the two position textures are compared element by element.
 
   Pass: identical tick counts and max |dx| = 0 across every live particle.
 
   Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const ERRS = [];

const argN = (process.argv.find(a => a.startsWith('--n=')) || '').slice(4);
const N = argN ? parseInt(argN, 10) : 262144;
const LAB = process.argv.includes('--lab');
const TICKS = 200;
const SEED = 20260902;

const READ = () => {
  const P = window.__probe, ts = P.texSize;
  let buf;
  if (P.posA.texture.type === THREE.HalfFloatType) {
    const raw = new Uint16Array(ts * ts * 4);
    P.renderer.readRenderTargetPixels(P.posA, 0, 0, ts, ts, raw);
    buf = new Float32Array(raw.length);
    const h2f = x => { const s = (x & 0x8000) ? -1 : 1, e = (x & 0x7C00) >> 10, f = x & 0x3FF;
      return e === 0 ? s * Math.pow(2, -14) * (f / 1024) : e === 31 ? NaN : s * Math.pow(2, e - 15) * (1 + f / 1024); };
    for (let i = 0; i < raw.length; i++) buf[i] = h2f(raw[i]);
  } else {
    buf = new Float32Array(ts * ts * 4);
    P.renderer.readRenderTargetPixels(P.posA, 0, 0, ts, ts, buf);
  }
  return { type: P.posA.texture.type === THREE.HalfFloatType ? 'half' : 'float',
           v: Array.from(buf.subarray(0, Math.min(buf.length, 4 * 262144))) };
};

async function run(browser, budget) {
  const page = await newPage(browser);
  await page.evaluate(({ n, seed, budget, stop, lab }) => {
    let s = seed >>> 0;
    Math.random = () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
    const P = window.__probe;
    const st = JSON.parse(JSON.stringify(P.state));
    st.particles = n; st.quality = 0.5;
    st.sound = Object.assign({}, st.sound, { level: 0 });
    st.cosmos = Object.assign({}, st.cosmos, { selfgrav: 0.3, epoch: true, epochLen: 10, cascade: 'out' });
    st.lab = { on: lab };
    st.autoOrbit = false;
    window.__simStop = 0;
    window.__tickBudget = budget;
    window.__forceDt = budget * 0.05;
    P.applyPreset({ state: st, step: 9028 });
    P.reseed();
    window.__simStop = P.simTime + stop;
  }, { n: N, seed: SEED, budget, stop: TICKS * 0.05, lab: LAB });

  await page.waitForFunction(() => window.__probe.simTime >= window.__simStop - 1e-9, null,
                             { timeout: 300000, polling: 100 });
  const r = await page.evaluate(READ);
  const t = await page.evaluate(() => window.__probe.simTime);
  await page.close();
  return { budget, simTime: t, ticks: Math.round(t / 0.05), pos: r.v, type: r.type };
}

async function newPage(browser) {
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  page.on('pageerror', e => ERRS.push(e.message));
  await page.addInitScript(n => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {}
  }, N);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 180000 });
  await page.waitForTimeout(600);
  await page.evaluate(() => document.querySelector('[data-scn="spinchladni"]').click());
  await page.waitForTimeout(400);
  return page;
}

(async () => {
  const SW = process.argv.includes('--sw');
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: SW ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox']
             : ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-gpu-sandbox', '--no-sandbox'],
  });
  // --control runs the SAME budget twice: it separates "the hook changes physics"
  // from "the harness is not reproducible run to run".
  const CONTROL = process.argv.includes('--control');
  const a = await run(browser, 1);
  const b = await run(browser, CONTROL ? 1 : 10);

  let maxAbs = 0, sum2 = 0, n = 0, bad = 0;
  const L = Math.min(a.pos.length, b.pos.length);
  for (let i = 0; i < L; i++) {
    if (i % 4 === 3) continue;
    const x = a.pos[i], y = b.pos[i];
    if (!Number.isFinite(x) || !Number.isFinite(y)) { bad++; continue; }
    const d = Math.abs(x - y);
    if (d > maxAbs) maxAbs = d;
    sum2 += d * d; n++;
  }
  const rms = Math.sqrt(sum2 / Math.max(1, n));
  const ticksMatch = a.ticks === b.ticks && a.simTime === b.simTime;
  const pass = ticksMatch && maxAbs === 0 && bad === 0;
  const out = { particles: N, lab_on: LAB, seed: SEED, target_ticks: TICKS,
    backend: process.argv.includes('--sw') ? 'swiftshader' : 'gpu', texture_type: a.type,
    run_budget1: { ticks: a.ticks, simTime: a.simTime },
    run_budget10: { ticks: b.ticks, simTime: b.simTime },
    mode: process.argv.includes('--control') ? 'control (1 vs 1)' : '1 vs 10',
    compared_components: n, nonfinite: bad, max_abs_diff: maxAbs, rms_diff: rms,
    ticks_match: ticksMatch, pass, pageerrors: ERRS.slice(0, 5) };
  fs.writeFileSync(path.join(__dirname, `memory_budget_identity${N}${LAB ? '_lab' : ''}.json`), JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
  console.log(pass ? 'PASS — the tick-budget hook does not change the trajectory.'
                   : 'FAIL — the tick-budget hook changes the trajectory; the run plan is invalid.');
  await browser.close();
  process.exit(pass ? 0 : 1);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
