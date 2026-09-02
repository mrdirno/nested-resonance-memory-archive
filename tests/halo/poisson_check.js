'use strict';
/* Does the solver solve Poisson, or does it just make a blur that happens to
   attract? Textbook check: confine the swarm to a thin spherical shell with
   the shell vessel, then read the potential mesh the solver wrote. For a
   shell of radius a, grad^2 phi = rho gives phi = const inside and phi ~ -1/r
   outside. So: flat within, and r*|phi| constant beyond - both falsifiable. */
const { chromium } = require('playwright');
const path = require('path');

const STATE = {
  particles: 250000, stepsPerSec: 0.02, smooth: false, fieldForm: 'chladni',
  fieldExp: -2, damping: 3, quality: 0.5, colorMode: 0, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'pi' },
  offsetMode: 'auto', strideIndex: 51,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false,
              equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45,
            mag: 0, twist: false, aniso: 0, helix: 0, cascade: 'out',
            selfgrav: 0.05, gainloss: 0 },      // tiny: shape it, don't move it
  sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true,
           level: 0.5, register: -1, pitchSpace: 'shepard' },
  vessel: { form: 'shell', gain: 4, radius: 0.5, girth: 0.01 },
  guides: false, autoOrbit: false,
};

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.addInitScript(() => {
    try { localStorage.setItem('resonance-chamber-v2',
      JSON.stringify({ particles: 250000, quality: 0.5 })); } catch (e) {}
  });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(1200);

  await page.evaluate(s => {
    window.__probe.applyPreset({ state: s, step: 3 });
    window.__probe.reseed();
    window.__t0 = window.__probe.simTime;
  }, STATE);
  const t0 = Date.now();
  for (;;) {
    const el = await page.evaluate(() => window.__probe.simTime - window.__t0);
    if (el >= 20 || Date.now() - t0 > 240000) break;
    await page.waitForTimeout(1200);
  }

  const out = await page.evaluate(() => {
    const P = window.__probe, PM = P.PM;
    const w = PM.N * PM.TX, h = PM.N * PM.TY;
    // the potential mesh is a half-float target: read raw and decode
    const raw = new Uint16Array(w * h * 4);
    P.renderer.readRenderTargetPixels(P.pmPot, 0, 0, w, h, raw);
    const h2f = x => {
      const sgn = (x & 0x8000) ? -1 : 1, e = (x & 0x7C00) >> 10, f = x & 0x03FF;
      if (e === 0) return sgn * Math.pow(2, -14) * (f / 1024);
      if (e === 0x1F) return f ? NaN : sgn * Infinity;
      return sgn * Math.pow(2, e - 15) * (1 + f / 1024);
    };
    const buf = new Float32Array(w * h * 4);
    for (let i = 0; i < raw.length; i++) buf[i] = h2f(raw[i]);
    // read phi(cell) and bin by distance from the mesh centre
    const at = (i, j, k) => {
      const tc = k % PM.TX, tr = Math.floor(k / PM.TX);
      const px = tc * PM.N + i, py = tr * PM.N + j;
      return buf[(py * w + px) * 4];
    };
    const cell = 2 * PM.HALF / PM.N;
    const NB = 16, sum = new Float64Array(NB), cnt = new Float64Array(NB);
    for (let k = 0; k < PM.N; k++)
      for (let j = 0; j < PM.N; j++)
        for (let i = 0; i < PM.N; i++) {
          const x = (i + 0.5 - PM.N / 2) * cell;
          const y = (j + 0.5 - PM.N / 2) * cell;
          const z = (k + 0.5 - PM.N / 2) * cell;
          const r = Math.hypot(x, y, z);
          const b = Math.floor(r / PM.HALF * NB);
          if (b >= NB) continue;
          sum[b] += at(i, j, k); cnt[b]++;
        }
    const prof = [];
    for (let b = 0; b < NB; b++) {
      const r = (b + 0.5) / NB * PM.HALF;
      prof.push([r, cnt[b] ? sum[b] / cnt[b] : 0]);
    }
    return { prof, shellR: P.state.vessel.radius * 15 };
  });

  console.log('shell at r =', out.shellR.toFixed(2), '(mesh half-width 15.3)\n');
  console.log('   r      phi       r*|phi|');
  for (const [r, phi] of out.prof) {
    console.log(r.toFixed(2).padStart(6), phi.toFixed(4).padStart(9),
      (r * Math.abs(phi)).toFixed(3).padStart(10),
      r < out.shellR ? ' inside' : ' outside');
  }
  const inside = out.prof.filter(([r]) => r < out.shellR * 0.8).map(([, p]) => p);
  const outside = out.prof.filter(([r]) => r > out.shellR * 1.25 && r < 13)
    .map(([r, p]) => r * Math.abs(p));
  const spread = a => {
    const mu = a.reduce((s, v) => s + v, 0) / a.length;
    return Math.sqrt(a.reduce((s, v) => s + (v - mu) ** 2, 0) / a.length) / Math.abs(mu);
  };
  console.log('\ninside  phi variation      ', (spread(inside) * 100).toFixed(1) + '%  (flat = Poisson)');
  console.log('outside r*|phi| variation  ', (spread(outside) * 100).toFixed(1) + '%  (constant = 1/r tail)');
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
