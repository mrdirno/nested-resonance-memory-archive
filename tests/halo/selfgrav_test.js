'use strict';
/* Does the backreaction do physics, or is it a slider that renders?
   Test: turn the eigenmode field almost off and let the swarm's own gravity
   act. With self-gravity ON a uniform ball must go lumpy (Jeans-style
   fragmentation); with it OFF at identical settings it must stay smooth.
   Measured on the density variance of the same 32^3 mesh the solver uses. */
const { chromium } = require('playwright');
const path = require('path');

const BASE = {
  particles: 300000, stepsPerSec: 0.5, smooth: true, fieldForm: 'chladni',
  fieldExp: 2, damping: 1, quality: 0.5, colorMode: 3, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'phi' },
  offsetMode: 'auto', strideIndex: 0,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false,
              equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 1.2, epoch: true, epochLen: 10,
            mag: 0.4, twist: true, aniso: 0.55, helix: 0.8, cascade: 'out', selfgrav: 0 },
  sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true,
           level: 0.5, register: -1, pitchSpace: 'shepard' },
  vessel: { form: 'off', gain: 1.2, radius: 0.62, girth: 0.02 },
  guides: false, autoOrbit: false,
};

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.addInitScript(() => {
    try { localStorage.setItem('resonance-chamber-v2',
      JSON.stringify({ particles: 300000, quality: 0.5 })); } catch (e) {}
  });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(1500);

  // clumpiness measured independently of the solver: bin the read-back
  // positions on a 24^3 grid and report the density variance over mean^2
  const clump = () => page.evaluate(() => {
    const P = window.__probe, ts = P.texSize;
    const pb = new Float32Array(ts * ts * 4);
    P.renderer.readRenderTargetPixels(P.posA, 0, 0, ts, ts, pb);
    const total = Math.min(P.state.particles, ts * ts);
    const N = 24, E = 15.3, g = new Float64Array(N * N * N);
    let n = 0, bad = 0, rsum = 0;
    for (let i = 0; i < total; i++) {
      const j = i * 4, x = pb[j], y = pb[j + 1], z = pb[j + 2];
      if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z)) { bad++; continue; }
      rsum += Math.hypot(x, y, z);
      const ix = Math.floor((x / E * 0.5 + 0.5) * N);
      const iy = Math.floor((y / E * 0.5 + 0.5) * N);
      const iz = Math.floor((z / E * 0.5 + 0.5) * N);
      if (ix < 0 || iy < 0 || iz < 0 || ix >= N || iy >= N || iz >= N) continue;
      g[(iz * N + iy) * N + ix]++; n++;
    }
    // only cells inside the ball carry signal; use occupied cells
    let occ = 0, s = 0, s2 = 0;
    for (let i = 0; i < g.length; i++) if (g[i] > 0) { occ++; s += g[i]; s2 += g[i] * g[i]; }
    const mu = s / occ;
    return { contrast: Math.sqrt(s2 / occ - mu * mu) / mu, n, bad,
             occupied: occ, rmean: rsum / (n + bad) };
  });

  const run = async (selfgrav, seconds, label, shot) => {
    await page.evaluate(([b, sg]) => {
      const s = JSON.parse(JSON.stringify(b));
      s.cosmos.selfgrav = sg;
      window.__probe.applyPreset({ state: s, step: 4 });
      window.__probe.reseed();
      window.__t0 = window.__probe.simTime;
    }, [BASE, selfgrav]);
    const t0 = Date.now();
    const marks = [];
    for (const t of [2, seconds / 2, seconds]) {
      for (;;) {
        const el = await page.evaluate(() => window.__probe.simTime - window.__t0);
        if (el >= t) break;
        if (Date.now() - t0 > 260000) break;
        await page.waitForTimeout(1000);
      }
      marks.push(await clump());
    }
    const fps = (await page.textContent('#ro-fps')).trim();
    console.log(label.padEnd(22),
      'contrast', marks.map(m => m.contrast.toFixed(3)).join(' -> '),
      '| r_mean', marks[marks.length - 1].rmean.toFixed(2),
      '| non-finite', marks[marks.length - 1].bad,
      '| fps', fps);
    if (shot) await page.screenshot({ path: path.join(__dirname, 'shots', shot) });
    return marks;
  };

  // calibration sweep: want a slider whose low end is cohesion, whose
  // middle fragments, and whose top collapses - so watch contrast (structure)
  // against r_mean (global collapse) together.
  const out = [];
  for (const sg of [0, 0.3, 0.8, 2]) {
    out.push([sg, await run(sg, 26, 'selfgrav ' + sg,
      sg === 0 ? '61-sg-off.png' : sg === 1 ? '62-sg-on.png' : null)]);
  }
  console.log('\nsg     contrast   r_mean   (r_mean ~12 = holding against the expansion)');
  for (const [sg, m] of out) {
    console.log(String(sg).padEnd(6), m[2].contrast.toFixed(3).padStart(8),
      m[2].rmean.toFixed(2).padStart(8));
  }
  const real = errs.filter(e => !/SwiftShader|GroupMarker|fallback|deprecat|GPU stall/i.test(e));
  console.log(real.length ? 'ERRORS: ' + real.slice(0, 3).join(' | ') : 'no page errors');
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
