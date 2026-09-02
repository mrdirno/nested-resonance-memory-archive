'use strict';
/* The disc worker's falsifiers, on the page itself at the fixed 1/20 tick:
   Razor Disc under Euler forms a razor (mean|y| ~ 0.005-0.01, ~100% on the
   force ceiling, speed ~86); under the exact-rotation (Boris) step the same
   settings pile matter at the poles. And what the two steps do to the user's
   own Spinning Chladni. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const N = 262144;
const RUNS = [
  { name: 'SC mag0 Euler',                 scn: 'spinchladni', lorentz: 'euler', step: 9028, cosmos: { mag: 0 } },
  { name: 'SC mag0.05 Euler',              scn: 'spinchladni', lorentz: 'euler', step: 9028, cosmos: { mag: 0.05 } },
  { name: 'SC mag0.05 exact',              scn: 'spinchladni', lorentz: 'boris', step: 9028, cosmos: { mag: 0.05 } },
  { name: 'SC mag0.2 Euler',               scn: 'spinchladni', lorentz: 'euler', step: 9028, cosmos: { mag: 0.2 } },
  { name: 'SC mag0.2 exact',               scn: 'spinchladni', lorentz: 'boris', step: 9028, cosmos: { mag: 0.2 } },
  { name: 'SC sg0.3 sub2 Euler (lab c)',   scn: 'spinchladni', lorentz: 'euler', step: 9028, cosmos: { selfgrav: 0.3 }, substeps: 2 },
];
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.addInitScript(n => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {} }, N);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.waitForTimeout(800);
  const results = [];
  for (const run of RUNS) {
    await page.evaluate(r => {
      const P = window.__probe;
      P.applyScenario(r.scn);
      const s = JSON.parse(JSON.stringify(P.state));
      s.particles = 262144; s.quality = 0.5; s.lorentz = r.lorentz; s.lab = { on: true };
      Object.assign(s.cosmos, r.cosmos || {}); s.substeps = r.substeps || 1;
      s.sound = Object.assign({}, s.sound, { level: 0 });
      P.applyPreset({ state: s, step: r.step });
      P.reseed();
      window.__t0 = P.simTime;
    }, run);
    const wall0 = Date.now();
    const samples = [];
    let lastT = -1;
    for (;;) {
      const t = await page.evaluate(() => window.__probe.simTime - window.__t0);
      if (t >= 27 && t - lastT >= 0.9) {
        lastT = t;
        samples.push(await page.evaluate(() => {
          const P = window.__probe, ts = P.texSize, n = P.state.particles;
          const rd = (tgt) => {
            if (tgt.texture.type === THREE.HalfFloatType) {
              const raw = new Uint16Array(ts * ts * 4); P.renderer.readRenderTargetPixels(tgt, 0, 0, ts, ts, raw);
              const b = new Float32Array(raw.length);
              const h2f = x => { const s = (x & 0x8000) ? -1 : 1, e = (x & 0x7C00) >> 10, f = x & 0x3FF;
                return e === 0 ? s * Math.pow(2, -14) * (f / 1024) : e === 31 ? NaN : s * Math.pow(2, e - 15) * (1 + f / 1024); };
              for (let i = 0; i < raw.length; i++) b[i] = h2f(raw[i]); return b;
            }
            const b = new Float32Array(ts * ts * 4); P.renderer.readRenderTargetPixels(tgt, 0, 0, ts, ts, b); return b;
          };
          const pos = rd(P.posA), vel = rd(P.velA);
          const ys = [];
          let sr = 0, sv = 0, m = 0, clampN = 0;
          // skip the twin rows (last 2R rows) so the sample is ordinary matter
          const R = P.lab.twinRows || 0, lim = Math.min(n, ts * (ts - 2 * R));
          for (let i = 0; i < lim; i++) {
            const x = pos[4 * i], y = pos[4 * i + 1], z = pos[4 * i + 2];
            if (!Number.isFinite(x + y + z)) continue;
            ys.push(Math.abs(y)); sr += Math.hypot(x, y, z);
            sv += Math.hypot(vel[4 * i], vel[4 * i + 1], vel[4 * i + 2]);
            if (vel[4 * i + 3] > 0.5) clampN++;
            m++;
          }
          ys.sort((a, b) => a - b);
          const mean = ys.reduce((a, b) => a + b, 0) / Math.max(1, ys.length);
          return { meanY: mean, p90Y: ys[Math.floor(ys.length * 0.9)] || 0, r: sr / m, v: sv / m, clamp: clampN / m,
                   lambda: P.lab.lambda, labClamp: P.lab.clampFrac, t: P.simTime - window.__t0 };
        }));
      }
      if (t >= 30 || Date.now() - wall0 > 600000) break;
      await page.waitForTimeout(400);
    }
    const avg = k => samples.reduce((a, s) => a + s[k], 0) / Math.max(1, samples.length);
    const row = { name: run.name, meanY: avg('meanY'), p90Y: avg('p90Y'), r: avg('r'), v: avg('v'), clamp: avg('clamp'),
                  lambda: samples.length ? samples[samples.length - 1].lambda : NaN, samples: samples.length, wall: Math.round((Date.now() - wall0) / 1000) };
    results.push(row);
    console.log(row.name.padEnd(34), 'labClamp', (samples.length ? samples[samples.length-1].labClamp : NaN), 'mean|y|', row.meanY.toFixed(4), 'p90|y|', row.p90Y.toFixed(3), 'r', row.r.toFixed(2),
      'speed', row.v.toFixed(1), 'on-ceiling', (row.clamp * 100).toFixed(0) + '%', 'lambda', Number.isFinite(row.lambda) ? row.lambda.toFixed(2) : '-', `[${row.wall}s]`);
    fs.writeFileSync(path.join(__dirname, 'boris2_test.json'), JSON.stringify(results, null, 1));
  }
  console.log('done');
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
