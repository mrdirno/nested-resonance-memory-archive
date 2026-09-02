'use strict';
/* Structured gain/loss: does the pumping actually lock to the mode's
   azimuthal lobes, and does an amplifying region stay bounded?
   With a mode of order m, the speed should be modulated m-fold around the
   axis; with gain off it should be flat. */
const { chromium } = require('playwright');
const path = require('path');

const BASE = {
  particles: 200000, stepsPerSec: 0.02, smooth: false, fieldForm: 'chladni',
  fieldExp: 0, damping: 2.5, quality: 0.5, colorMode: 1, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'pi' },
  offsetMode: 'auto', strideIndex: 51,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false,
              equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45,
            mag: 0, twist: false, aniso: 0, helix: 0, cascade: 'out',
            selfgrav: 0, gainloss: 0 },
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
  const page = await browser.newPage({ viewport: { width: 1000, height: 760 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.addInitScript(() => {
    try { localStorage.setItem('resonance-chamber-v2',
      JSON.stringify({ particles: 200000, quality: 0.5 })); } catch (e) {}
  });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(1500);

  const probe = () => page.evaluate(() => {
    const P = window.__probe, ts = P.texSize;
    const pb = new Float32Array(ts * ts * 4), vb = new Float32Array(ts * ts * 4);
    P.renderer.readRenderTargetPixels(P.posA, 0, 0, ts, ts, pb);
    P.renderer.readRenderTargetPixels(P.velA, 0, 0, ts, ts, vb);
    const total = Math.min(P.state.particles, ts * ts);
    const NA = 48, sum = new Float64Array(NA), cnt = new Float64Array(NA);
    let n = 0, bad = 0, maxsp = 0;
    for (let i = 0; i < total; i++) {
      const j = i * 4, x = pb[j], z = pb[j + 2];
      if (!Number.isFinite(x)) { bad++; continue; }
      const sp = Math.hypot(vb[j], vb[j + 1], vb[j + 2]);
      if (!Number.isFinite(sp)) { bad++; continue; }
      maxsp = Math.max(maxsp, sp);
      let a = Math.atan2(z, x); if (a < 0) a += 2 * Math.PI;
      const k = Math.min(NA - 1, Math.floor(a / (2 * Math.PI) * NA));
      sum[k] += sp; cnt[k]++; n++;
    }
    const prof = Array.from({ length: NA }, (_, k) => cnt[k] ? sum[k] / cnt[k] : 0);
    const mu = prof.reduce((s, v) => s + v, 0) / NA;
    // Fourier power of the azimuthal speed profile at each order
    const power = [];
    for (let m = 1; m <= 8; m++) {
      let c = 0, s = 0;
      for (let k = 0; k < NA; k++) {
        const a = (k + 0.5) / NA * 2 * Math.PI;
        c += (prof[k] - mu) * Math.cos(m * a);
        s += (prof[k] - mu) * Math.sin(m * a);
      }
      power.push(Math.hypot(c, s) / NA / (mu || 1));
    }
    return { n, bad, maxsp, meanSpeed: mu, power,
             modes: document.getElementById('ro-modes').textContent.trim() };
  });

  const run = async (gl, secs, shot) => {
    await page.evaluate(([b, g]) => {
      const s = JSON.parse(JSON.stringify(b));
      s.cosmos.gainloss = g;
      window.__probe.applyPreset({ state: s, step: 6 });
      window.__probe.reseed();
      window.__t0 = window.__probe.simTime;
    }, [BASE, gl]);
    const t0 = Date.now();
    for (;;) {
      const el = await page.evaluate(() => window.__probe.simTime - window.__t0);
      if (el >= secs || Date.now() - t0 > 220000) break;
      await page.waitForTimeout(1200);
    }
    const r = await probe();
    const best = r.power.indexOf(Math.max(...r.power)) + 1;
    console.log('gain/loss ' + String(gl).padEnd(5),
      'mode', r.modes.padEnd(8),
      'mean speed', r.meanSpeed.toFixed(2).padStart(7),
      'max', r.maxsp.toFixed(1).padStart(7),
      'non-finite', r.bad,
      '| strongest azimuthal order', best,
      '(' + r.power[best - 1].toFixed(3) + ')');
    if (shot) await page.screenshot({ path: path.join(__dirname, 'shots', shot) });
    return r;
  };

  await run(0, 18, '64-gl-off.png');
  await run(0.6, 18, '65-gl-on.png');
  await run(1, 18, '66-gl-max.png');

  const real = errs.filter(e => !/SwiftShader|GroupMarker|fallback|deprecat|GPU stall|ERR_CONNECTION/i.test(e));
  console.log(real.length ? 'ERRORS: ' + real.slice(0, 3).join(' | ') : 'no page errors');
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
