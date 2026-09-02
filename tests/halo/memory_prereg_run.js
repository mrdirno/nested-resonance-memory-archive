'use strict';
/* memory_prereg_run.js — one run of the pre-registered cross-epoch memory test.
 
   Drives HELIOS-V501 (HALO) at full particle count on the real GPU and records,
   for every epoch boundary:
     - the page's own instrument values (Retained, Two-back, lambda, ceiling share)
     - the raw 32^3 particle-mesh density that the instrument turns into those
       numbers, written as float32 so that every control — including the
       region-matched ones the page cannot display — is computable offline, by
       anyone, without a GPU.
 
   The simulation is stopped on exact tick boundaries (window.__simStop), so a run
   is reproducible tick for tick; initial conditions are drawn from a seeded LCG
   installed over Math.random before the preset is applied.
 
   usage: node memory_prereg_run.js --sg=0.3 --gl=0 --seed=12345 [--epochs=24]
                                    [--n=4194304] [--budget=10] [--out=DIR] [--sw]
 
   Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const arg = (k, d) => {
  const a = process.argv.find(s => s.startsWith('--' + k + '='));
  return a === undefined ? d : a.slice(k.length + 3);
};
const SG = parseFloat(arg('sg', '0.3'));
const GL = parseFloat(arg('gl', '0'));
const SEED = parseInt(arg('seed', '12345'), 10);
const EPOCHS = parseInt(arg('epochs', '24'), 10);
const N = parseInt(arg('n', '4194304'), 10);
const BUDGET = parseInt(arg('budget', '10'), 10);
const EPOCH_LEN = parseFloat(arg('epochlen', '10'));
const OUT = arg('out', path.resolve(__dirname, '../../data/results/halo/memory_prereg'));
const SW = process.argv.includes('--sw');
const PRESET = arg('preset', 'spinchladni');   // 'spinchladni' | 'default'
const TICK = 0.05;

const TAG = `${PRESET}_sg${SG}_gl${GL}_seed${SEED}_n${N}_e${EPOCHS}`;

const SW_ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'];
const GPU_ARGS = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-gpu-sandbox', '--no-sandbox'];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: SW ? SW_ARGS : GPU_ARGS,
  });
  const errs = [];
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  page.on('pageerror', e => errs.push(String(e.message).slice(0, 300)));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 200)); });
  await page.addInitScript(n => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {}
  }, N);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 300000 });
  await page.waitForTimeout(800);
  if (PRESET === 'spinchladni') {
    await page.evaluate(() => document.querySelector('[data-scn="spinchladni"]').click());
    await page.waitForTimeout(500);
  }

  const applied = await page.evaluate(({ n, seed, sg, gl, budget, epochLen, preset }) => {
    let s = seed >>> 0;
    Math.random = () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
    const P = window.__probe;
    // 'spinchladni' takes the scenario the page itself just applied; 'default' takes
    // the page's own shipped DEFAULTS, so neither arm is a bespoke construction.
    const st = JSON.parse(JSON.stringify(preset === 'default' ? P.DEFAULTS : P.state));
    st.particles = n; st.quality = 0.5;
    st.autoOrbit = false;
    st.sound = Object.assign({}, st.sound, { level: 0 });
    st.cosmos = Object.assign({}, st.cosmos,
      { selfgrav: sg, gainloss: gl, epoch: true, epochLen: epochLen, cascade: 'out' });
    st.lab = { on: true };
    window.__simStop = 0;
    window.__tickBudget = budget;
    window.__forceDt = budget * 0.05;
    P.applyPreset({ state: st, step: preset === 'default' ? 0 : 9028 });
    P.reseed();
    return { particles: P.state.particles, texSize: P.texSize, simTime: P.simTime,
             cosmos: JSON.parse(JSON.stringify(P.state.cosmos)),
             lorentz: P.state.lorentz, substeps: P.state.substeps,
             smooth: P.state.smooth, damping: P.state.damping,
             stepsPerSec: P.state.stepsPerSec, fieldExp: P.state.fieldExp,
             caps: P.caps() };
  }, { n: N, seed: SEED, sg: SG, gl: GL, budget: BUDGET, epochLen: EPOCH_LEN, preset: PRESET });

  console.log(`[${TAG}] ${applied.particles} particles, tex ${applied.texSize}, ` +
              `${applied.caps.renderer.slice(0, 40)}, pmDens ${applied.caps.pmDensType}, ` +
              `float_blend ${applied.caps.float_blend}`);

  const meshPath = path.join(OUT, TAG + '.mesh.f32');
  const meshFd = fs.openSync(meshPath, 'w');
  const rows = [];
  const wall0 = Date.now();

  for (let k = 1; k <= EPOCHS; k++) {
    // (a) stop one tick BEFORE the boundary: this is the end-of-epoch density the
    //     instrument snapshots as the relic on the very next tick.
    await page.evaluate(t => { window.__simStop = t; }, +(k * EPOCH_LEN - TICK).toFixed(6));
    await page.waitForFunction(() => window.__probe.simTime >= window.__simStop - 1e-9,
                               null, { timeout: 600000, polling: 100 });
    const mesh = await page.evaluate(() => Array.from(window.__probe.labReadDensity()));
    fs.writeSync(meshFd, Buffer.from(new Float32Array(mesh).buffer));

    // (b) advance one tick so the zoom-out fires and the instrument scores it.
    await page.evaluate(t => { window.__simStop = t; }, +(k * EPOCH_LEN).toFixed(6));
    await page.waitForFunction(() => window.__probe.simTime >= window.__simStop - 1e-9,
                               null, { timeout: 600000, polling: 50 });
    const r = await page.evaluate(() => {
      const P = window.__probe, L = P.lab;
      const f = v => Number.isFinite(v) ? v : null;
      return { simTime: P.simTime, epochN: P.epochN, labEpochs: L.epochs,
               retained: f(L.retained), twoback: f(L.retained2),
               memory: f(L.memory), memory2: f(L.memory2),
               lambda: f(L.lambda), ceiling: f(L.clampFrac),
               lbar: f(L.lbar), lpre: f(L.lpre) };
    });
    rows.push({ epoch: k, ...r });
    if (k % 4 === 0 || k === EPOCHS) {
      console.log(`  epoch ${String(k).padStart(2)}  t=${r.simTime.toFixed(1)}  ` +
        `retained=${r.retained === null ? '  -  ' : r.retained.toFixed(3).padStart(6)}  ` +
        `twoback=${r.twoback === null ? '  -  ' : r.twoback.toFixed(3).padStart(6)}  ` +
        `ceiling=${r.ceiling === null ? '-' : r.ceiling.toFixed(3)}  [${Math.round((Date.now() - wall0) / 1000)}s]`);
    }
  }
  fs.closeSync(meshFd);

  const capsEnd = await page.evaluate(() => window.__probe.caps());
  const log = await page.evaluate(() => window.__probe.lab.log.map(r => r.join(',')));
  const out = {
    tag: TAG, schema: 'halo-memory-prereg/1',
    params: { selfgrav: SG, gainloss: GL, seed: SEED, epochs: EPOCHS, particles: N,
              tick_budget: BUDGET, epoch_len: EPOCH_LEN, preset: PRESET,
              step: PRESET === 'default' ? 0 : 9028,
              backend: SW ? 'swiftshader' : 'gpu' },
    applied, caps_end: capsEnd, mesh_file: path.basename(meshPath), mesh_n: 32, mesh_count: EPOCHS,
    csv_head: 't,step,lambda,memory,memory_twoback,on_ceiling,l_prescribed,l_realized,C1,C2,C3,C4,C5,C6,C7,C8,C9,selfgrav,gainloss,hubble,epoch,substeps',
    csv_rows: log, epochs: rows,
    wall_seconds: Math.round((Date.now() - wall0) / 1000), pageerrors: errs.slice(0, 10),
  };
  fs.writeFileSync(path.join(OUT, TAG + '.json'), JSON.stringify(out, null, 1));
  console.log(`[${TAG}] wrote ${TAG}.json + ${path.basename(meshPath)} ` +
              `(${EPOCHS} meshes, ${Math.round((Date.now() - wall0) / 1000)}s wall)`);
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
