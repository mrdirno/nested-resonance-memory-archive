'use strict';
/* Page-side test of the Jeans worker's claim: the self-gravity collapse
   threshold in Spinning Chladni is set by rotational support (Omega =
   6*helix/damping), not by the expansion rate. Predictions from the port:
   H-independent ~0.51 at helix 0.8; helix 1.2 -> 0.62; helix 0.4 -> 0.35;
   helix 0 -> 0.30. Measured here on the real GPU page at 262k particles. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const RUNS = [
  { name: 'H1.2 sg0     (ref)',    hubble: 1.2, selfgrav: 0 },
  { name: 'H1.2 sg0.45',           hubble: 1.2, selfgrav: 0.45 },
  { name: 'H1.2 sg0.6',            hubble: 1.2, selfgrav: 0.6 },
  { name: 'H0.3 sg0',              hubble: 0.3, selfgrav: 0 },
  { name: 'H0.3 sg0.45',           hubble: 0.3, selfgrav: 0.45 },
  { name: 'H0.3 sg0.6',            hubble: 0.3, selfgrav: 0.6 },
  { name: 'H2.4 sg0',              hubble: 2.4, selfgrav: 0 },
  { name: 'H2.4 sg0.45',           hubble: 2.4, selfgrav: 0.45 },
  { name: 'H2.4 sg0.6',            hubble: 2.4, selfgrav: 0.6 },
  { name: 'H1.2 helix0.4 sg0.45',  hubble: 1.2, helix: 0.4, selfgrav: 0.45 },
  { name: 'H1.2 helix0   sg0.45',  hubble: 1.2, helix: 0,   selfgrav: 0.45 },
  { name: 'H1.2 helix1.2 sg0.55',  hubble: 1.2, helix: 1.2, selfgrav: 0.55 },
  { name: 'H1.2 helix1.2 sg0.75',  hubble: 1.2, helix: 1.2, selfgrav: 0.75 },
];
const only = process.argv[2] ? new RegExp(process.argv[2]) : null;
const N = 262144;

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.addInitScript(n => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {}
  }, N);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.waitForTimeout(1000);
  // the user's preset, from the page itself
  await page.evaluate(() => document.querySelector('[data-scn="spinchladni"]').click());
  await page.waitForTimeout(500);
  const base = await page.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state)));
  base.particles = N; base.quality = 0.5; base.sound = Object.assign({}, base.sound, { level: 0 });
  console.log('base cosmos:', JSON.stringify(base.cosmos), 'particles', base.particles);

  const results = [];
  for (const run of RUNS) {
    if (only && !only.test(run.name)) continue;
    const s = JSON.parse(JSON.stringify(base));
    s.cosmos.hubble = run.hubble;
    s.cosmos.selfgrav = run.selfgrav;
    if (run.helix !== undefined) s.cosmos.helix = run.helix;
    await page.evaluate(st => {
      window.__probe.applyPreset({ state: st, step: 9028 });
      window.__probe.reseed();
      window.__t0 = window.__probe.simTime;
    }, s);
    const wall0 = Date.now();
    const samples = [];
    let lastT = -1;
    for (;;) {
      const t = await page.evaluate(() => window.__probe.simTime - window.__t0);
      if (t >= 28 && t - lastT >= 0.45) {
        lastT = t;
        samples.push(await page.evaluate(() => {
          const P = window.__probe, ts = P.texSize, n = P.state.particles;
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
          // mean radius, and density contrast on a 16^3 grid of the +-15.3 box
          const G = 16, half = 15.3, cell = 2 * half / G, cnt = new Float64Array(G * G * G);
          let sr = 0, m = 0, bad = 0, sy2 = 0;
          for (let i = 0; i < n; i++) {
            const x = buf[4 * i], y = buf[4 * i + 1], z = buf[4 * i + 2];
            if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z)) { bad++; continue; }
            sr += Math.hypot(x, y, z); sy2 += y * y; m++;
            const gi = Math.floor((x + half) / cell), gj = Math.floor((y + half) / cell), gk = Math.floor((z + half) / cell);
            if (gi >= 0 && gi < G && gj >= 0 && gj < G && gk >= 0 && gk < G) cnt[(gk * G + gj) * G + gi]++;
          }
          let s1 = 0, s2 = 0, occ = 0, mx = 0;
          for (let c = 0; c < cnt.length; c++) { if (cnt[c] > 0) { s1 += cnt[c]; s2 += cnt[c] * cnt[c]; occ++; if (cnt[c] > mx) mx = cnt[c]; } }
          const mu = s1 / Math.max(1, occ);
          return { r: sr / Math.max(1, m), rmsY: Math.sqrt(sy2 / Math.max(1, m)), contrast: Math.sqrt(Math.max(0, s2 / Math.max(1, occ) - mu * mu)) / mu, maxCell: mx, bad, m, t: window.__probe.simTime - window.__t0 };
        }));
      }
      if (t >= 30 || Date.now() - wall0 > 480000) break;
      await page.waitForTimeout(400);
    }
    const r = samples.reduce((a, s) => a + s.r, 0) / Math.max(1, samples.length);
    const c = samples.reduce((a, s) => a + s.contrast, 0) / Math.max(1, samples.length);
    const last = samples[samples.length - 1] || {};
    const row = { name: run.name, r, contrast: c, rmsY: last.rmsY, maxCell: last.maxCell, bad: last.bad, samples: samples.length, tEnd: last.t, wall: Math.round((Date.now() - wall0) / 1000) };
    results.push(row);
    console.log(row.name.padEnd(24), 'r', r.toFixed(2), 'contrast', c.toFixed(2), 'rmsY', (last.rmsY || 0).toFixed(2),
      'maxCell', last.maxCell, 'bad', last.bad, 'n', last.m, 'samples', samples.length, 'tEnd', (last.t || 0).toFixed(1), `[${row.wall}s]`);
    fs.writeFileSync(path.join(__dirname, 'spin_support.json'), JSON.stringify(results, null, 1));
  }
  console.log('done');
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
