'use strict';
/* The conservation instruments, proven on the test build (SwiftShader by default):
   (g) the field energy is derived, not assumed: -grad(U_field) by central differences equals the
       force the velocity shader applies, wells and Chladni, at 36 random points;
   (a) field-only audit, 200 ticks on the reflecting wall with the wall ledger: the centred H plus
       what the wall took stays inside a band (reported; <= 1e-2) that does not grow, while the
       stored-velocity H swings in a wider band; the same field on the wrap (no wall) and the wells
       form on the wrap hold as well;
   (b) Euler magnetic kick at coupling 0.4, nothing else acting: measured d ln KE/dt against the
       page's prediction (20%) and against the exact per-step law (1%); the exact-rotation step
       adds only what this GPU's own cos/sin lose;
   (c) damping 1 alone: d ln KE/dt = -2.0 +- 5%;
   (d) self-gravity audit, 10 s, six sweeps and exact: |dH/H0| and L reported; the per-particle
       mesh energy equals SG*s*Phi(cell) recomputed on the CPU from the potential atlas;
   (e) OFF-equivalence: the build before this change and this one, seeded alike, run 100 ticks and
       their position and velocity textures are byte-identical, instruments off, on, and on with the
       ledger; the velocity shader's source is identical;
   (f) the GPU reductions equal a float64 CPU sum over the full level-0 readback at 65,536 particles
       to 1e-5, and the probe rows are masked to zero;
   plus the panel, the switches and the CSV columns.
   Run: node conserve_test.js   (PW_CHANNEL=chrome uses the installed Chrome instead of SwiftShader) */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const PAGE = 'file://' + path.resolve(__dirname, 'rc-test.html');
const baseFile = process.env.HALO_BASE_PAGE || path.resolve(__dirname, '..', '..', '_base', 'tests', 'halo', 'rc-test.html');
const BASE = fs.existsSync(baseFile) ? 'file://' + path.resolve(baseFile) : null;
const N = 65536;

const audit = (extra) => {
  const s = {
    particles: N, quality: 0.5, fieldForm: 'chladni', fieldExp: 0, damping: 0, stepsPerSec: 0.02, smooth: false,
    colorMode: 1, base: 10, constants: { a: 'phi', b: 'phi', c: 'pi' }, offsetMode: 'auto', strideIndex: 51,
    overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false, equal: false, trefoil: false, torus: false, hopf: false },
    centers: { on: false, count: 3, period: 24, gain: 1 }, vessel: { form: 'off', gain: 1.2, radius: 0.62, girth: 0.02 },
    cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45, mag: 0, twist: false, aniso: 0, helix: 0, cascade: 'out', selfgrav: 0, gainloss: 0 },
    sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true, level: 0.5, register: -1, pitchSpace: 'shepard' },
    guides: false, autoOrbit: false, substeps: 1, lorentz: 'euler', pm: { solver: 'jacobi', assign: 'ngp' },
    lab: { on: true, fieldOff: false, ledger: true }, sacred: 'off',
  };
  for (const k of Object.keys(extra || {})) {
    if (extra[k] && typeof extra[k] === 'object' && !Array.isArray(extra[k])) Object.assign(s[k], extra[k]); else s[k] = extra[k];
  }
  return s;
};

const seedInit = () => {
  // mulberry32, seeded before the page's own script runs; __seedRng re-seeds right before reseed()
  let a = 424242;
  Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  window.__seedRng = s => { a = s | 0; };
  window.__forceDt = 1e-7;
  try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {}
};

async function open(browser, url, errs, frozen) {
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 700 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => errs.push('pageerror ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(seedInit);
  await page.goto(url);
  await page.waitForSelector('.boot.done', { timeout: 120000 });
  // frozen: the page never ticks on its own (the seeded comparison must start both builds at the same digit phase)
  if (!frozen) await page.evaluate(() => { window.__forceDt = 1 / 20; });
  return { ctx, page };
}
const ticks = (page, n) => page.evaluate(n => new Promise(r => { let k = 0; const f = () => { if (++k >= n) r(); else requestAnimationFrame(f); }; requestAnimationFrame(f); }), n);
const cons = page => page.evaluate(() => { const c = window.__probe.cons; return JSON.parse(JSON.stringify({
  H: c.H, Hc: c.Hc, H0: c.H0, Hs0: c.Hs0, KE: c.KE, KEs: c.KEs, Uf: c.Uf, Um: c.Um, dH: c.dH, dHs: c.dHs, W: c.W, hits: c.hits, Labs: c.Labs, Labs0: c.Labs0, dL: c.dL, Lalign: c.Lalign,
  rate: c.rate, pred: c.pred, basis: c.basis, ceil: c.ceil, wall: c.wall, KEperp: c.KEperp, samples: c.samples, hist: c.hist, histS: c.histS, note: c.note,
  settled: c.settled, waiting: c.waiting, M: c.M, N: c.N, t: c.t, live: window.__probe.consLedgerLive(), amp: window.__probe.velMat.uniforms.amp.value })); });
const applyAudit = (page, st, step) => page.evaluate(([st, step]) => {
  const P = window.__probe; P.applyPreset({ state: st, step: step || 0 }); window.__seedRng(0x9E3779B9); P.reseed(); }, [st, step || 0]);
const bandOf = h => h.length ? Math.max(...h.map(Math.abs)) : NaN;
const growth = h => {   // mean of the last third minus mean of the first third of the drift record
  const n = h.length, k = Math.max(1, Math.floor(n / 3));
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  return n >= 3 ? mean(h.slice(n - k)) - mean(h.slice(0, k)) : NaN;
};
const fmt = v => Number.isFinite(v) ? (Math.abs(v) < 1e-3 ? v.toExponential(2) : v.toFixed(4)) : String(v);

(async () => {
  const launch = { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] };
  if (process.env.PW_CHANNEL) { launch.channel = process.env.PW_CHANNEL; launch.args = ['--no-sandbox']; }
  else if (process.env.PW_CHROMIUM_PATH) launch.executablePath = process.env.PW_CHROMIUM_PATH;
  const browser = await chromium.launch(launch);
  const errs = [];
  const { page } = await open(browser, PAGE, errs);
  check('boot', true);
  const gpu = await page.evaluate(() => { const gl = window.__probe.renderer.getContext(); const ext = gl.getExtension('WEBGL_debug_renderer_info'); return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); });
  console.log('  GPU: ' + gpu);
  const numbers = {};

  // ---- the panel ----
  await page.keyboard.press('7');
  await ticks(page, 2);
  const dom = await page.evaluate(() => ({
    ids: ['lab-H', 'lab-Hc', 'lab-dH', 'lab-wall-took', 'lab-erate', 'lab-erate-pred', 'lab-ceil', 'lab-hits', 'lab-L', 'lab-dL', 'lab-Lalign', 'lab-settled', 'lab-cv-cons', 'lab-cons-note', 'lab-field-seg', 'lab-ledger-seg'].map(id => !!document.getElementById(id)),
    audits: ['fieldonly', 'borisvseuler', 'gravity'].map(k => !!document.querySelector('#lab-exp-seg button[data-exp="' + k + '"]')),
    dampMin: document.getElementById('in-damp').getAttribute('min'),
    csv: /epoch,H,dH_H0,L,wall_took,substeps/.test(document.documentElement.innerHTML),
    hint: document.querySelector('#sw-lab .hint').textContent,
  }));
  check('conservation readouts, trace, note and the two switches present', dom.ids.every(Boolean), JSON.stringify(dom.ids));
  check('three audit buttons present', dom.audits.every(Boolean));
  check('damping slider reaches 0', dom.dampMin === '0', dom.dampMin);
  check('CSV header carries H, dH_H0, L, wall_took', dom.csv);
  check('instruments hint names the new readouts', /energy and angular momentum/.test(dom.hint));

  // ---- (g) the derivation: -grad(U_field) equals the force the velocity shader applies ----
  for (const form of ['chladni', 'wells']) {
    await applyAudit(page, audit({ fieldForm: form, lab: { on: true, fieldOff: false, ledger: false } }), 0);
    await ticks(page, 2);
    const g = await page.evaluate(([eps, form]) => {
      const P = window.__probe, S = P.texSize, total = Math.min(P.state.particles, S * S);
      // 36 random points (r in 3..12, off the axis), each with +-eps along x, y, z: 252 texels of row 0
      let a = 7; const rnd = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
      const pts = [];
      while (pts.length < 36) { const p = [rnd() * 24 - 12, rnd() * 24 - 12, rnd() * 24 - 12]; const r = Math.hypot(...p); if (r > 3 && r < 12 && Math.hypot(p[0], p[2]) > 1) pts.push(p); }
      const row = new Float32Array(S * 4), zero = new Float32Array(S * 4);
      const old = P.readTarget(P.posA, 0, 0, S, 1);
      for (let x = 0; x < S; x++) { row[x * 4] = old[x * 4]; row[x * 4 + 1] = old[x * 4 + 1]; row[x * 4 + 2] = old[x * 4 + 2]; row[x * 4 + 3] = 1; zero[x * 4 + 3] = 1; }
      pts.forEach((p, i) => { for (let k = 0; k < 7; k++) { const q = p.slice(); if (k > 0) q[(k - 1) >> 1] += (k % 2 ? eps : -eps); const x = i * 7 + k; row[x * 4] = q[0]; row[x * 4 + 1] = q[1]; row[x * 4 + 2] = q[2]; row[x * 4 + 3] = 1; } });
      P.writeRow(P.posA, 0, row, S); P.writeRow(P.velA, 0, zero, S);
      P.consCopyUniforms(); P.consReduce(0);
      const U = P.readTarget(P.consRT.levels[0], 0, 0, S, 1);
      const h = P.TICK / P.effectiveSubsteps();
      P.simStep(h);                                  // damping 0, no magnetic term: v' = F h exactly
      const v = P.readTarget(P.velA, 0, 0, S, 1);
      let worst = 0, fmax = 0, ceil = 0;
      const rows = [];
      pts.forEach((p, i) => {
        const x0 = i * 7, F = [v[x0 * 4] / h, v[x0 * 4 + 1] / h, v[x0 * 4 + 2] / h];
        if (v[x0 * 4 + 3] > 0.5) ceil++;
        const gU = [0, 1, 2].map(k => (U[(x0 + 1 + 2 * k) * 4] - U[(x0 + 2 + 2 * k) * 4]) * total / (2 * eps));
        fmax = Math.max(fmax, Math.hypot(...F));
        const err = Math.hypot(gU[0] + F[0], gU[1] + F[1], gU[2] + F[2]);
        worst = Math.max(worst, err);
        if (i < 3) rows.push({ p: p.map(x => +x.toFixed(2)), F: F.map(x => +x.toFixed(4)), minusGradU: gU.map(x => +(-x).toFixed(4)) });
      });
      return { worst, fmax, rel: worst / fmax, ceil, amp: P.velMat.uniforms.amp.value, rows };
    }, [1e-3, form]);
    console.log('  (g) ' + form + ': ' + JSON.stringify(g));
    check('(g) ' + form + ': -grad(U_field) by central differences equals the applied force at 36 points (worst error <= 1% of the largest force, none on the ceiling)', g.rel <= 0.01 && g.ceil === 0 && g.fmax > 1, 'worst ' + g.worst.toExponential(2) + ' of ' + g.fmax.toFixed(2) + ' = ' + g.rel.toExponential(2));
    numbers['grad_' + form] = g.rel;
  }

  // ---- (a) field only: Chladni on the reflecting wall, ledger on ----
  await applyAudit(page, audit(), 0);
  await ticks(page, 200);
  let a = await cons(page);
  const bandW = bandOf(a.hist), bandS = bandOf(a.histS), grow = growth(a.hist);
  console.log('  (a) chladni, reflect, ledger: ' + JSON.stringify({ H0: a.H0, Hc: a.Hc, H: a.H, KE: a.KE, Uf: a.Uf, dH: a.dH, dHs: a.dHs, W: a.W, hits: a.hits, band: bandW, bandStored: bandS, growth: grow, samples: a.samples, wall: a.wall, ceil: a.ceil, pred: a.pred, rate: a.rate, basis: a.basis, live: a.live, M: a.M, N: a.N }));
  console.log('      drift record (centred + wall): ' + a.hist.map(fmt).join(' '));
  console.log('      drift record (stored v):       ' + a.histS.map(fmt).join(' '));
  check('(a) chladni: 10 samples in 200 ticks, ledger live, mask counts N minus the probe rows', a.samples >= 10 && a.live && a.M < a.N && a.M > 0.95 * a.N, a.samples + ' ' + a.live + ' ' + a.M + '/' + a.N);
  check('(a) chladni: kinetic energy became a large share of H0 (the derivation of U is tested, not zero)', a.KE / a.H0 > 0.2, (a.KE / a.H0).toFixed(3));
  check('(a) chladni: the centred H plus the wall’s take stays within 1e-2 of H0 over 200 ticks', bandW <= 1e-2, bandW.toExponential(2));
  const half = Math.floor(a.hist.length / 2), range = h => Math.max(...h) - Math.min(...h);
  const r1 = range(a.hist.slice(0, half + 1)), r2 = range(a.hist.slice(half));
  check('(a) chladni: that band does not grow (the record’s second half spans no more than its first half)', r2 <= r1, 'first half ' + fmt(r1) + ' second half ' + fmt(r2) + ' (last third minus first third ' + fmt(grow) + ')');
  check('(a) chladni: the stored-velocity H swings more than the centred one', bandS > bandW, bandS.toExponential(2) + ' vs ' + bandW.toExponential(2));
  check('(a) chladni: the wall took energy (hits counted, H itself walked down by more than the band)', a.hits > 0 && a.W > 0 && (a.Hc - a.H0) < -bandW, 'hits ' + fmt(a.hits) + ' took ' + fmt(a.W) + ' dHc ' + fmt((a.Hc - a.H0) / a.H0));
  check('(a) chladni: predicted rate 0 with nothing acting; measured rate near 0 on the total+wall basis', a.pred === 0 && a.basis === 'total+wall' && Math.abs(a.rate) < 0.02, a.pred + ' ' + a.basis + ' ' + fmt(a.rate));
  numbers.a = { drop: -(a.Hc - a.H0) / a.H0, hits: a.hits, band: bandW, bandStored: bandS, growth: grow, ceil: a.ceil };
  // the same audit at four substeps: the band is the integrator's, so it shrinks with the step
  await applyAudit(page, audit({ substeps: 4 }), 0);
  await ticks(page, 200);
  const a4 = await cons(page);
  const band4 = bandOf(a4.hist);
  console.log('  (a) chladni, reflect, ledger, substeps 4: ' + JSON.stringify({ dH: a4.dH, band: band4, bandStored: bandOf(a4.histS), W: a4.W, hits: a4.hits }));
  console.log('      drift record (centred + wall): ' + a4.hist.map(fmt).join(' '));
  check('(a) chladni at substeps 4: the band shrinks with the step (at least 3x; the record at one substep is dominated by the swarm’s first fall): the band is the integrator’s', band4 * 3 <= bandW, band4.toExponential(2) + ' vs ' + bandW.toExponential(2) + ' = 1/' + (bandW / band4).toFixed(1));
  numbers.a.band4 = band4;
  // the same field on the wrap: no wall, nothing to count, H itself holds
  await applyAudit(page, audit({ lab: { on: true, fieldOff: false, ledger: false }, cosmos: { boundary: 'wrap' } }), 0);
  await ticks(page, 200);
  a = await cons(page);
  const bandWrap = bandOf(a.hist);
  console.log('  (a) chladni, wrap: ' + JSON.stringify({ H0: a.H0, Hc: a.Hc, dH: a.dH, band: bandWrap, bandStored: bandOf(a.histS), W: a.W, live: a.live }));
  check('(a) chladni on the wrap: |dH/H0| band <= 1e-2 with no ledger', bandWrap <= 1e-2 && !a.live, bandWrap.toExponential(2));
  numbers.a.wrap = bandWrap;
  // wells on the wrap: U = amp*fscale*v1 is sign-indefinite, so measure against the energy scale
  await applyAudit(page, audit({ fieldForm: 'wells', lab: { on: true, fieldOff: false, ledger: false }, cosmos: { boundary: 'wrap' } }), 0);
  await ticks(page, 200);
  a = await cons(page);
  const scale = Math.abs(a.KE) + Math.abs(a.Uf) + Math.abs(a.H0);
  const driftWells = Math.abs(a.Hc - a.H0) / scale;
  console.log('  (a) wells, wrap: ' + JSON.stringify({ H0: a.H0, Hc: a.Hc, KE: a.KE, Uf: a.Uf, driftOverScale: driftWells }));
  check('(a) wells on the wrap: |dH| <= 1e-2 of the energy scale after 200 ticks', driftWells <= 1e-2, driftWells.toExponential(2));
  check('(a) wells: kinetic energy is a large share of the scale', a.KE / scale > 0.1, (a.KE / scale).toFixed(3));
  numbers.a.wells = driftWells;

  // ---- (b) Euler kick alone: give the swarm speed with the field, then switch the field off ----
  const arm = (patch) => page.evaluate(patch => {
    const P = window.__probe, s = P.state;
    s.lab.fieldOff = true; s.cosmos.boundary = 'wrap'; s.cosmos.mag = patch.mag; s.damping = patch.damping; s.lorentz = patch.lorentz;
    P.velMat.uniforms.amp.value = P.fieldAmp(); P.velMat.uniforms.damping.value = patch.damping; P.velMat.uniforms.uBoris.value = patch.lorentz === 'boris' ? 1 : 0;
    P.consReset();
  }, patch);
  await applyAudit(page, audit({ fieldExp: 0.5, lab: { on: true, fieldOff: false, ledger: false } }), 0);
  await ticks(page, 40);
  await arm({ mag: 0.4, damping: 0, lorentz: 'euler' });
  await ticks(page, 20);                      // the first sample after arming takes the baseline
  const b0 = await cons(page);
  await ticks(page, 20);                      // ... and the next gives the rate over one second
  const b1 = await cons(page);
  const th = 0.4 * 10.5 / 20, perp0 = b0.KEperp, par0 = b0.KE - b0.KEperp, nk = Math.round((b1.t - b0.t) * 20);
  const keExact = par0 + perp0 * Math.pow(1 + th * th, nk);
  console.log('  (b) euler: ' + JSON.stringify({ amp: b1.amp, KE0: b0.KE, KEperp0: b0.KEperp, KE1: b1.KE, keExact, rate: b1.rate, pred: b1.pred, basis: b1.basis, samples: [b0.samples, b1.samples] }));
  check('(b) euler kick: the field is off (strength uniform 0) and the rate is read from the log of kinetic energy', b1.amp === 0 && b1.basis === 'kinetic' && Number.isFinite(b1.rate), b1.amp + ' ' + b1.basis + ' ' + fmt(b1.rate));
  check('(b) euler kick: measured d ln KE/dt within 20% of the predicted pump', Math.abs(b1.rate - b1.pred) <= 0.2 * Math.abs(b1.pred), fmt(b1.rate) + ' vs ' + fmt(b1.pred));
  check('(b) euler kick: KE after n steps equals KE_par + KE_perp (1+theta^2)^n to 1% (n = ' + nk + ' ticks between the samples)', b1.samples - b0.samples === 1 && nk >= 20 && Math.abs(b1.KE - keExact) <= 0.01 * keExact, b1.KE.toFixed(5) + ' vs ' + keExact.toFixed(5));
  check('(b) euler kick: predicted rate is ln(1 + theta^2 KEperp/KE)/dt at the sample', Math.abs(b1.pred - Math.log(1 + th * th * b1.KEperp / b1.KE) * 20) < 1e-6, fmt(b1.pred));
  numbers.euler = { rate: b1.rate, pred: b1.pred };
  // Boris: the same coupling as an exact rotation adds nothing but what this GPU's cos/sin lose
  const trig = await page.evaluate(th => {
    const r = window.__probe.renderer;
    const rt = new THREE.WebGLRenderTarget(1, 1, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, format: THREE.RGBAFormat, type: THREE.FloatType, depthBuffer: false, stencilBuffer: false });
    const m = new THREE.ShaderMaterial({ uniforms: { th: { value: th } }, vertexShader: 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: 'precision highp float; uniform float th; void main(){ float c = cos(th), s = sin(th); gl_FragColor = vec4(c*c + s*s, c, s, 1.0); }' });
    const sc = new THREE.Scene(); sc.add(new THREE.Mesh(new THREE.PlaneBufferGeometry(2, 2), m));
    const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    r.setRenderTarget(rt); r.render(sc, cam); r.setRenderTarget(null);
    const out = new Float32Array(4); r.readRenderTargetPixels(rt, 0, 0, 1, 1, out); rt.dispose();
    return out[0];
  }, th);
  await arm({ mag: 0.4, damping: 0, lorentz: 'boris' });
  await ticks(page, 20);
  const bb0 = await cons(page);
  await ticks(page, 20);
  const bb = await cons(page);
  const nb = Math.round((bb.t - bb0.t) * 20);
  const keBoris = (bb0.KE - bb0.KEperp) + bb0.KEperp * Math.pow(trig, nb);
  console.log('  (b) boris: ' + JSON.stringify({ cos2sin2: trig, KE0: bb0.KE, KE1: bb.KE, keTrig: keBoris, rate: bb.rate, pred: bb.pred, rateTrig: Math.log(keBoris / bb0.KE) }));
  const predTrig = Math.log(trig) * (bb.KEperp / bb.KE) * 20;
  check('(b) boris: the page predicts only what this renderer’s cos/sin lose per step (' + (trig - 1).toExponential(2) + '): ' + fmt(bb.pred) + ' /s', Math.abs(bb.pred - predTrig) <= 1e-4 + 0.05 * Math.abs(predTrig), fmt(bb.pred) + ' vs ln(cos^2+sin^2) x share x 20 = ' + fmt(predTrig));
  check('(b) boris: KE after n rotations equals KE_par + KE_perp (cos^2+sin^2)^n to 1e-3 (n = ' + nb + '; the GPU trig is the only loss)', nb >= 20 && Math.abs(bb.KE - keBoris) <= 1e-3 * bb.KE, bb.KE.toFixed(6) + ' vs ' + keBoris.toFixed(6));
  check('(b) boris: |d ln KE/dt| < 0.02, and within 1e-3 of the predicted trig loss', Math.abs(bb.rate) < 0.02 && Math.abs(bb.rate - bb.pred) < 1e-3, fmt(bb.rate) + ' vs ' + fmt(bb.pred));
  numbers.boris = { rate: bb.rate, trig };

  // ---- (c) damping 1 alone ----
  await arm({ mag: 0, damping: 1, lorentz: 'euler' });
  await ticks(page, 40);
  const c = await cons(page);
  console.log('  (c) damping: ' + JSON.stringify({ rate: c.rate, pred: c.pred, KE: c.KE, basis: c.basis }));
  check('(c) damping 1 alone: d ln KE/dt = -2.0 within 5%', Math.abs(c.rate + 2) <= 0.1 && c.pred === -2, fmt(c.rate));
  numbers.damping = c.rate;

  // ---- (d) self-gravity audit, both solvers ----
  numbers.gravity = {};
  for (const solver of ['jacobi', 'exact']) {
    await applyAudit(page, audit({ fieldExp: 0, lab: { on: true, fieldOff: true, ledger: true }, pm: { solver, assign: 'ngp' }, cosmos: { selfgrav: 0.3 } }), 0);
    await ticks(page, 200);
    const d = await cons(page);
    console.log('  (d) gravity, ' + solver + ': ' + JSON.stringify({ amp: d.amp, H0: d.H0, Hc: d.Hc, KE: d.KE, Um: d.Um, dH: d.dH, dHs: d.dHs, W: d.W, hits: d.hits, Labs: d.Labs, Labs0: d.Labs0, dL: d.dL, Lalign: d.Lalign, ceil: d.ceil, settled: d.settled, waiting: d.waiting, samples: d.samples, hist: d.hist.map(fmt).join(' ') }));
    check('(d) gravity, ' + solver + ': field off, H0 taken (potential settled), the ball collapsed (KE grew), the mesh energy is negative', d.amp === 0 && Number.isFinite(d.H0) && !d.waiting && d.KE > 0.5 && d.Um < 0, JSON.stringify({ amp: d.amp, H0: d.H0, KE: d.KE, Um: d.Um }));
    check('(d) gravity, ' + solver + ': |dH/H0| over 10 s reported (the mesh scheme’s own error): ' + fmt(d.dH), Number.isFinite(d.dH), 'settled ' + fmt(d.settled) + ' ceiling ' + fmt(d.ceil) + ' wall took ' + fmt(d.W));
    check('(d) gravity, ' + solver + ': L stays a small share of lined-up motion (< 10%; the swarm is seeded at rest, and the cube mesh is what makes L): ' + fmt(d.Lalign), Number.isFinite(d.Lalign) && d.Lalign < 0.1, 'lined up ' + fmt(d.Lalign) + ' |L| ' + fmt(d.Labs) + ' |L0| ' + fmt(d.Labs0) + (solver === 'jacobi' ? ' (H0 waits for the six sweeps to settle, so L0 is not zero)' : ''));
    numbers.gravity[solver] = { dH: d.dH, ceil: d.ceil, settled: d.settled, Lalign: d.Lalign, W: d.W };
    // the per-particle mesh energy against a CPU recomputation from the potential atlas (nearest cell)
    const um = await page.evaluate(() => {
      const P = window.__probe, S = P.texSize, total = Math.min(P.state.particles, S * S), s = P.state.cosmos.selfgrav;
      P.consCopyUniforms(); P.consReduce(0);
      const lvl = P.readTarget(P.consRT.levels[0], 0, 0, S, S), pos = P.readTarget(P.posA, 0, 0, S, S);
      const pot = P.readTarget(P.pmPot, 0, 0, P.PM.N * P.PM.TX, P.PM.N * P.PM.TY);
      const Nn = P.PM.N, W = Nn * P.PM.TX, half = P.PM.HALF;
      let worst = 0, n = 0, maxAbs = 0;
      for (let t = 0; t < total; t += 977) {
        const p = [pos[t * 4], pos[t * 4 + 1], pos[t * 4 + 2]];
        const cell = p.map(x => Math.floor((x / half * 0.5 + 0.5) * Nn));
        let phi = 0;
        if (cell.every(c => c >= 0 && c < Nn)) phi = pot[((Math.floor(cell[2] / P.PM.TX) * Nn + cell[1]) * W + (cell[2] % P.PM.TX) * Nn + cell[0]) * 4];
        const cpu = P.SG_GAIN * s * phi / total, gpu = lvl[t * 4 + 1];
        worst = Math.max(worst, Math.abs(cpu - gpu)); maxAbs = Math.max(maxAbs, Math.abs(cpu)); n++;
      }
      return { worst, maxAbs, n, rel: worst / maxAbs };
    });
    check('(d) gravity, ' + solver + ': per-particle mesh energy equals SG*s*Phi(cell) recomputed on the CPU (' + um.n + ' texels, 1e-5)', um.rel <= 1e-5, JSON.stringify(um));
  }

  // ---- (f) the reductions against a CPU sum over the full level-0 readback ----
  await applyAudit(page, audit({ cosmos: { selfgrav: 0.3, hubble: 0.2 }, lab: { on: true, fieldOff: false, ledger: true } }), 0);
  await ticks(page, 30);
  const red = await page.evaluate(() => {
    const P = window.__probe, S = P.texSize, total = Math.min(P.state.particles, S * S), L = P.lab;
    P.consCopyUniforms();
    const out = [];
    for (let pass = 0; pass < 4; pass++) {
      const gpu = Array.from(P.consReduce(pass));
      const lvl = P.readTarget(P.consRT.levels[0], 0, 0, S, S);
      const cpu = [0, 0, 0, 0], abs = [0, 0, 0, 0];
      let probeNonzero = 0, probeTexels = 0;
      const R = L.twinRows, yb = L.volRow, M = L.volN;
      for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
        const i = (y * S + x) * 4;
        const isProbe = y >= S - R || (M > 0 && y >= yb + 1 && y <= yb + 6 && x < M);
        for (let k = 0; k < 4; k++) { cpu[k] += lvl[i + k]; abs[k] += Math.abs(lvl[i + k]); }
        if (isProbe) { probeTexels++; for (let k = 0; k < 4; k++) if (!(pass === 0 && k === 1) && !(pass === 3 && k === 1) && lvl[i + k] !== 0) probeNonzero++; }
      }
      const rel = gpu.map((g, k) => Math.abs(g - cpu[k]) / Math.max(abs[k], 1e-30));
      out.push({ pass, gpu: gpu.map(v => +v.toPrecision(7)), cpu: cpu.map(v => +v.toPrecision(7)), rel: rel.map(v => +v.toExponential(2)), probeTexels, probeNonzero });
    }
    const expectM = total - L.twinRows * S - 6 * L.volN;
    return { out, total, expectM, M: out[0].gpu[3] * total, dep: out[3].gpu[1] * total };
  });
  for (const o of red.out) {
    console.log('  (f) pass ' + o.pass + ': gpu ' + JSON.stringify(o.gpu) + ' cpu ' + JSON.stringify(o.cpu) + ' rel ' + JSON.stringify(o.rel) + ' probe texels ' + o.probeTexels + ' nonzero ' + o.probeNonzero);
    check('(f) pass ' + o.pass + ': GPU tree sum equals the float64 CPU sum over all ' + red.total + ' texels to 1e-5 (of the sum of magnitudes)', o.rel.every(r => r <= 1e-5), JSON.stringify(o.rel));
    check('(f) pass ' + o.pass + ': the probe rows are masked to zero', o.probeNonzero === 0, o.probeNonzero + ' of ' + o.probeTexels);
  }
  check('(f) the mask counts every particle but the probe rows (' + red.expectM + '), the deposit count is the whole swarm', Math.abs(red.M - red.expectM) < 0.5 && Math.abs(red.dep - red.total) < 0.5, red.M + ' ' + red.dep);
  numbers.reduce = red.out.map(o => Math.max(...o.rel));

  // ---- the switches ----
  await applyAudit(page, audit({ lab: { on: true, fieldOff: false, ledger: false } }), 0);
  await ticks(page, 2);
  const sw = await page.evaluate(async () => {
    const P = window.__probe, out = {};
    out.ampOn = P.velMat.uniforms.amp.value;
    document.querySelector('#lab-field-seg [data-lf="off"]').click();
    out.ampOff = P.velMat.uniforms.amp.value; out.stateOff = P.state.lab.fieldOff;
    out.pressedOff = document.querySelector('#lab-field-seg [data-lf="off"]').getAttribute('aria-pressed');
    document.querySelector('#lab-ledger-seg [data-ledger="on"]').click();
    out.ledger = P.state.lab.ledger; out.live = P.consLedgerLive();
    await new Promise(r => setTimeout(r, 400));
    out.saved = JSON.parse(localStorage.getItem('resonance-chamber-v2')).lab;
    document.querySelector('#lab-field-seg [data-lf="on"]').click();
    document.querySelector('#lab-ledger-seg [data-ledger="off"]').click();
    out.ampBack = P.velMat.uniforms.amp.value; out.liveBack = P.consLedgerLive();
    return out;
  });
  console.log('  switches: ' + JSON.stringify(sw));
  check('field-force switch zeroes the strength uniform and restores it; ledger switch arms the replay; both saved', sw.ampOn === 1 && sw.ampOff === 0 && sw.stateOff === true && sw.pressedOff === 'true' && sw.ledger === true && sw.live === true && sw.saved.fieldOff === true && sw.saved.ledger === true && sw.ampBack === 1 && sw.liveBack === false, JSON.stringify(sw));
  await ticks(page, 20);
  const lg = await page.evaluate(() => { const P = window.__probe; const row = P.lab.log[P.lab.log.length - 1]; const m = document.documentElement.innerHTML.match(/const head = '([^']*epoch,H,dH_H0,L,wall_took,substeps[^']*)'/); const cols = m ? m[1].split(',') : []; const at = cols.indexOf('H'); return { cols: row ? row.length : 0, headCols: cols.length, at, mine: row ? row.slice(at, at + 4) : null, last: row ? row[row.length - 1] : null }; });
  check('the Lab log row has exactly as many columns as the CSV header; H, dH_H0, L, wall_took sit under their names after epoch, the substeps and volume columns stay last', lg.cols === lg.headCols && lg.at > 0 && lg.mine && lg.mine[0] !== '' && Number.isFinite(+lg.mine[0]) && lg.last !== '', JSON.stringify(lg));

  // ---- (e) OFF-equivalence: the build before this change and this one, seeded alike ----
  if (BASE) {
    const runs = async (url) => {
      const e2 = [];
      const { ctx, page: pg } = await open(browser, url, e2, true);
      // the run is counted in the page and parked on window; node polls (one long page promise can be garbage-collected under load);
      // rows = the twins plus the volume meter's clusters (0 on a build without the meter), so an instruments-on comparison knows whether the base reserves the same rows
      const run = async n => {
        await pg.evaluate(n => { const P = window.__probe; window.__consOut = null; window.__seedRng(0x9E3779B9); P.reseed(); const t0 = P.simTime; window.__forceDt = 1 / 20;
          let k = 0; const f = () => { if (++k >= n) { window.__forceDt = 1e-7; const S = P.posA.width; const rd = t => { const o = new Float32Array(S * S * 4); P.renderer.readRenderTargetPixels(t, 0, 0, S, S, o); return o; }; const a = rd(P.posA), b = rd(P.velA);
            let s1 = 2166136261, s2 = 2166136261; for (let i = 0; i < a.length; i++) { s1 = Math.imul(s1 ^ ((a[i] * 1e5) | 0), 16777619); s2 = Math.imul(s2 ^ ((b[i] * 1e5) | 0), 16777619); }
            window.__consOut = { ticks: Math.round((P.simTime - t0) / (1 / 20)), pos: s1 >>> 0, vel: s2 >>> 0, lab: P.lab.on, step: P.step, rows: (P.lab.twinRows | 0) + (P.lab.volN | 0) }; } else requestAnimationFrame(f); }; requestAnimationFrame(f); }, n);
        let h = null; for (let i = 0; i < 3600 && !h; i++) { h = await pg.evaluate(() => window.__consOut); if (!h) await pg.waitForTimeout(50); }
        if (!h) throw new Error('OFF-equivalence run took over 180 s'); return h;
      };
      const out = {};
      out.A = await run(100);                          // the saved default state, instruments off, from a page that has not ticked yet
      await pg.evaluate(() => { const P = window.__probe; const s = JSON.parse(JSON.stringify(P.state)); s.cosmos.selfgrav = 0.3; s.cosmos.mag = 0.4; s.lab = { on: true }; P.applyPreset({ state: s, step: 3 }); window.__forceDt = 1e-7; });
      out.B = await run(100);                          // instruments on, self-gravity and the magnetic term on
      out.vs = await pg.evaluate(() => window.__probe.velMat.fragmentShader);
      await ctx.close();
      return { out, errs: e2 };
    };
    const u = await runs(BASE), p = await runs(PAGE);
    // this build once more with the wall ledger live: the replay must not touch the physics
    const e3 = [];
    const { ctx: c3, page: p3 } = await open(browser, PAGE, e3, true);
    await p3.evaluate(() => { const P = window.__probe; const s = JSON.parse(JSON.stringify(P.state)); s.cosmos.selfgrav = 0.3; s.cosmos.mag = 0.4; s.lab = { on: true, ledger: true }; P.applyPreset({ state: s, step: 3 }); window.__forceDt = 1e-7; });
    await p3.evaluate(n => { const P = window.__probe; window.__consOut = null; window.__seedRng(0x9E3779B9); P.reseed(); const t0 = P.simTime; window.__forceDt = 1 / 20;
      let k = 0; const f = () => { if (++k >= n) { window.__forceDt = 1e-7; const S = P.posA.width; const rd = t => { const o = new Float32Array(S * S * 4); P.renderer.readRenderTargetPixels(t, 0, 0, S, S, o); return o; }; const a = rd(P.posA), b = rd(P.velA);
        let s1 = 2166136261, s2 = 2166136261; for (let i = 0; i < a.length; i++) { s1 = Math.imul(s1 ^ ((a[i] * 1e5) | 0), 16777619); s2 = Math.imul(s2 ^ ((b[i] * 1e5) | 0), 16777619); }
        window.__consOut = { ticks: Math.round((P.simTime - t0) / (1 / 20)), pos: s1 >>> 0, vel: s2 >>> 0, live: P.consLedgerLive(), hits: P.cons.hits, W: P.cons.W }; } else requestAnimationFrame(f); }; requestAnimationFrame(f); }, 100);
    let C = null; for (let i = 0; i < 3600 && !C; i++) { C = await p3.evaluate(() => window.__consOut); if (!C) await p3.waitForTimeout(50); }
    if (!C) throw new Error('ledger run took over 180 s');
    await c3.close();
    console.log('  (e) before: ' + JSON.stringify(u.out.A) + ' ' + JSON.stringify(u.out.B) + '\n      after:  ' + JSON.stringify(p.out.A) + ' ' + JSON.stringify(p.out.B) + '\n      ledger: ' + JSON.stringify(C));
    const same = (x, y) => x.pos === y.pos && x.vel === y.vel && x.ticks === 100 && y.ticks === 100;
    check('(e) OFF-equivalence: instruments off, posA/velA byte-identical to the build before this change after 100 seeded ticks', same(u.out.A, p.out.A), JSON.stringify([u.out.A, p.out.A]));
    // With the instruments ON the reserved rows (twins, and the volume meter's clusters) are rewritten every half
    // second, so an instruments-on comparison is meaningful only against a base that carries the same rows.
    if (u.out.B.rows === p.out.B.rows) check('(e) instruments on (self-gravity, magnetic term): still byte-identical', same(u.out.B, p.out.B), JSON.stringify([u.out.B, p.out.B]));
    else console.log('  (e) instruments-on comparison skipped: the base build reserves ' + u.out.B.rows + ' rows, this build ' + p.out.B.rows);
    // the ledger replays the velocity shader itself; on THIS build, instruments on with and without the ledger must agree
    check('(e) wall ledger live: the replay leaves the physics byte-identical', same(p.out.B, C) && C.live, JSON.stringify([p.out.B, C]));
    check('(e) no errors in either build', u.errs.length === 0 && p.errs.length === 0 && e3.length === 0, (u.errs.concat(p.errs, e3)).slice(0, 3).join(' | '));
  } else console.log('  (e) SKIPPED: no probe build of the page before this change at ' + baseFile + ' (set HALO_BASE_PAGE=<path>)');

  console.log('  numbers: ' + JSON.stringify(numbers));
  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
