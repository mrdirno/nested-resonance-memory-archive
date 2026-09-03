'use strict';
/* Mode dimer (tests/halo/dimer_test.js).
   (a) OFF-equivalence: with the dimer off, posA and velA after exactly 100 seeded ticks are
       byte-identical to a build without this change (RC_BASE=<path to its rc-test.html>, or
       ../../_base/tests/halo/rc-test.html); Chladni and wells forms, self-gravity 0.3, coupling 0.4;
   (b) the CPU pair reproduces the analytic eigenvalues and the closed-form evolution: k = 1,
       g = 0.5 splits by 2 sqrt(0.75); g = 1 coalesces to 1e-6 and grows secularly (ratio (1+t)^2/t^2);
       fidelity to exp(-i H t) above 1 - 1e-6 at 10 s, below and above the exceptional point;
   (c) the loop: clockwise vs counter-clockwise end more than 10x apart in |a1|^2/|a2|^2, from
       (1, 0), (0, 1) and a circular start alike; the flat (no gain) control returns an eigenstate
       with overlap above 95%; the readouts say so;
   (d) the particles follow: 10 s with the pair held on partner 1 vs partner 2, the density mesh's
       m-projection (computed here, from the raw mesh) sits on the cos vs the sin partner, in both
       forms, and the page's own "matter on partner 1" agrees with the share the weights ask for;
   (e) the controls: switch, sliders, loop buttons, the experiment button, a preset round trip. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const launch = () => chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });

const base = () => ({
  particles: 65536, stepsPerSec: 0.02, smooth: false, fieldForm: 'wells', fieldExp: 0, damping: 3,
  quality: 0.5, colorMode: 1, base: 10, constants: { a: 'phi', b: 'phi', c: 'pi' }, offsetMode: 'auto', strideIndex: 51,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false, equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45, mag: 0, twist: false, aniso: 0, helix: 0, cascade: 'out', selfgrav: 0, gainloss: 0 },
  sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true, level: 0.5, register: -1, pitchSpace: 'shepard' },
  vessel: { form: 'off', gain: 1.2, radius: 0.62, girth: 0.02 },
  guides: false, autoOrbit: false, substeps: 1, lorentz: 'euler', lab: { on: false },
  dimer: { on: true, kappa: 1, gamma: 0, delta: 0, loop: 'off' }
});

// ---- closed form for the traceless 2x2: exp(-i H t) = cos(L t) I - i sin(L t)/L H, L^2 = k^2 + (D/2 + i g)^2
const C = { mul: (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]], add: (a, b) => [a[0] + b[0], a[1] + b[1]],
  scale: (a, s) => [a[0] * s, a[1] * s], sqrt: z => { const r = Math.hypot(z[0], z[1]); return [Math.sqrt(Math.max(0, (r + z[0]) / 2)), (z[1] < 0 ? -1 : 1) * Math.sqrt(Math.max(0, (r - z[0]) / 2))]; },
  cos: z => [Math.cos(z[0]) * Math.cosh(z[1]), -Math.sin(z[0]) * Math.sinh(z[1])], sin: z => [Math.sin(z[0]) * Math.cosh(z[1]), Math.cos(z[0]) * Math.sinh(z[1])],
  div: (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; } };
function exact(k, g, D, t, a0) {   // a0 = [[re, im], [re, im]] -> unit state at time t
  const H = [[[D / 2, g], [k, 0]], [[k, 0], [-D / 2, -g]]];
  const L = C.sqrt([k * k + D * D / 4 - g * g, D * g]);
  let U;
  if (Math.hypot(L[0], L[1]) < 1e-9) U = [[[1, 0], [0, 0]], [[0, 0], [1, 0]]].map((row, i) => row.map((e, j) => C.add(e, C.mul([0, -t], H[i][j]))));
  else { const c = C.cos(C.scale(L, t)), s = C.div(C.sin(C.scale(L, t)), L); U = [[c, [0, 0]], [[0, 0], c]].map((row, i) => row.map((e, j) => C.add(e, C.mul(C.mul([0, -1], s), H[i][j])))); }
  const a = [C.add(C.mul(U[0][0], a0[0]), C.mul(U[0][1], a0[1])), C.add(C.mul(U[1][0], a0[0]), C.mul(U[1][1], a0[1]))];
  const n = Math.hypot(a[0][0], a[0][1], a[1][0], a[1][1]);
  return [a[0][0] / n, a[0][1] / n, a[1][0] / n, a[1][1] / n];
}
const fidelity = (u, v) => { const re = u[0] * v[0] + u[1] * v[1] + u[2] * v[2] + u[3] * v[3], im = u[0] * v[1] - u[1] * v[0] + u[2] * v[3] - u[3] * v[2]; return re * re + im * im; };
const share = a => a[0] * a[0] + a[1] * a[1];
const ratio = a => share(a) / Math.max(1e-300, a[2] * a[2] + a[3] * a[3]);

(async () => {
  // ---- (a) OFF-equivalence -----------------------------------------------------------------
  const baseBuild = process.env.RC_BASE || path.resolve(__dirname, '../../_base/tests/halo/rc-test.html');
  if (fs.existsSync(baseBuild)) {
    const seeded = () => { let a = 424242; Math.random = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; window.__seedRng = s => { a = s | 0; }; window.__forceDt = 1e-7; };
    const digest = async (file, saved) => {
      const br = await launch(); const pg = await br.newPage(); const errs = []; pg.on('pageerror', e => errs.push(e.message));
      await pg.addInitScript(seeded);
      await pg.addInitScript(s => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify(s)); } catch (e) {} }, saved);
      await pg.goto('file://' + file); await pg.waitForSelector('.boot.done', { timeout: 120000 });
      // read back through the probe's readTarget when it has one, else straight off the renderer (an older probe build)
      const h = await pg.evaluate(() => new Promise((res, rej) => { const P = window.__probe; window.__seedRng(0x9E3779B9); P.reseed(); const t0 = P.simTime; window.__forceDt = 1 / 20;
        const rd = t => { const n = t.width; if (P.readTarget) return P.readTarget(t, 0, 0, n, n); const o = new Float32Array(n * n * 4); P.renderer.readRenderTargetPixels(t, 0, 0, n, n, o); return o; };
        let k = 0; const f = () => { try { if (++k >= 100) { window.__forceDt = 1e-7; const a = rd(P.posA), b = rd(P.velA);
          let s1 = 2166136261, s2 = 2166136261; for (let i = 0; i < a.length; i++) { s1 = Math.imul(s1 ^ ((a[i] * 1e5) | 0), 16777619); s2 = Math.imul(s2 ^ ((b[i] * 1e5) | 0), 16777619); }
          res({ ticks: Math.round((P.simTime - t0) / (1 / 20)), step: P.step, pos: s1 >>> 0, vel: s2 >>> 0, n: P.posA.width, form: P.state.fieldForm, dimer: P.state.dimer ? P.state.dimer.on : 'absent' }); } else requestAnimationFrame(f); } catch (e) { rej(e); } }; requestAnimationFrame(f); }));
      await br.close(); return { ...h, errs };
    };
    for (const form of ['chladni', 'wells']) {
      const saved = { particles: 65536, quality: 0.5, fieldForm: form, cosmos: { selfgrav: 0.3, mag: 0.4, hubble: 0.3 }, lorentz: 'euler' };
      const u = await digest(baseBuild, saved), p = await digest(path.resolve(__dirname, 'rc-test.html'), saved);
      console.log('  (a) ' + form, JSON.stringify({ base: u, patched: p }));
      check('(a) OFF-equivalence, ' + form + ' form: posA and velA byte-identical after 100 seeded ticks, dimer off', u.pos === p.pos && u.vel === p.vel && u.ticks === 100 && p.ticks === 100 && p.dimer === false && p.errs.length === 0, u.pos + '/' + u.vel + ' vs ' + p.pos + '/' + p.vel);
    }
  } else console.log('skip (a): no build without this change to compare against (set RC_BASE=<rc-test.html of a build with mesh + integ only>)');

  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(() => { window.__forceDt = 1e-7; try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 120000 });
  check('boot', true);
  const frames = n => page.evaluate(n => new Promise(r => { let k = 0; const f = () => { if (++k >= n) r(); else requestAnimationFrame(f); }; requestAnimationFrame(f); }), n);
  const load = (s, step) => page.evaluate(([st, k]) => { const P = window.__probe; P.applyPreset({ state: st, step: k }); P.reseed(); }, [s, step]);
  // the pair alone: N ticks of the CPU integrator, no GPU in between (dimerTick advances the pair by one tick each call)
  const pairRun = (n, a0) => page.evaluate(([n, a0]) => { const P = window.__probe, D = P.dimer; if (a0) { D.a = a0.slice(); D.startA = a0.slice(); D.theta = 0; D.last = null; }
    for (let i = 0; i < n; i++) P.dimerTick(); P.dimerDraw(); return { a: D.a.slice(), last: D.last ? JSON.parse(JSON.stringify(D.last)) : null, eig: D.eig.slice(), ep: D.ep, live: D.live.slice(), theta: D.theta, loops: D.loops }; }, [n, a0 || null]);

  // ---- (b) eigenvalues and the closed form --------------------------------------------------
  await load(base(), 1);
  const e1 = await page.evaluate(() => window.__probe.dimerEig(1, 0.5, 0)), e2 = await page.evaluate(() => window.__probe.dimerEig(1, 1, 0)), e3 = await page.evaluate(() => window.__probe.dimerEig(1, 1.5, 0));
  check('(b) k=1 g=0.5: eigenvalues +-0.866 real, splitting 2 sqrt(0.75)', Math.abs(2 * e1[0] - 2 * Math.sqrt(0.75)) < 1e-9 && Math.abs(e1[1]) < 1e-12, e1.join(','));
  check('(b) k=1 g=1: the two eigenvalues coalesce (|E| < 1e-6)', Math.hypot(e2[0], e2[1]) < 1e-6, e2.join(','));
  check('(b) k=1 g=1.5: eigenvalues +-1.118 i (growth above the point)', Math.abs(e3[0]) < 1e-12 && Math.abs(Math.abs(e3[1]) - Math.sqrt(1.25)) < 1e-9, e3.join(','));
  const setPair = (kappa, gamma, delta, loop) => page.evaluate(([k, g, d, L]) => { const P = window.__probe; Object.assign(P.state.dimer, { on: true, kappa: k, gamma: g, delta: d, loop: L }); }, [kappa, gamma, delta, loop]);
  for (const [k, g, D] of [[1, 0.5, 0], [1, 1, 0], [1, 1.5, 0], [1, 0.3, 1.2], [2, 1, -0.5]]) {
    await setPair(k, g, D, 'off');
    const r = await pairRun(200, [1, 0, 0, 0]);
    const ex = exact(k, g, D, 10, [[1, 0], [0, 0]]);
    const F = fidelity(r.a, ex);
    check(`(b) pair (k,g,D)=(${k},${g},${D}): after 10 s the CPU state matches exp(-iHt) (fidelity > 1 - 1e-6)`, F > 1 - 1e-6, 'fidelity ' + F.toFixed(9) + ' share ' + share(r.a).toFixed(6) + ' vs ' + share(ex).toFixed(6));
    check(`(b) pair (k,g,D)=(${k},${g},${D}): readout eigenvalues = formula`, Math.abs(r.eig[0] - (await page.evaluate(p => window.__probe.dimerEig(...p), [k, g, D]))[0]) < 1e-12);
  }
  await setPair(1, 1, 0, 'off');
  const ep = await pairRun(200, [1, 0, 0, 0]);
  check('(b) at the exceptional point from (1,0): secular growth, |a1|^2/|a2|^2 = (11/10)^2 at 10 s', Math.abs(ratio(ep.a) - 1.21) < 1e-6 && Math.abs(ep.a[0] * ep.a[2] + ep.a[1] * ep.a[3]) < 1e-9, ratio(ep.a).toFixed(6));
  check('(b) at the exceptional point the readout says distance 0', ep.ep < 1e-12 && (await page.evaluate(() => document.getElementById('lab-dimer-ep').textContent)) === '0.000');
  const trace = async () => page.evaluate(() => { const P = window.__probe, D = P.dimer; D.a = [1, 0, 0, 0]; const s = []; for (let i = 0; i < 400; i++) { P.dimerTick(); s.push(D.a[0] * D.a[0] + D.a[1] * D.a[1]); } return s; });
  await setPair(1, 0, 0, 'off');
  const hh = await trace(), imin = hh.indexOf(Math.min(...hh.slice(0, 60)));
  check('(b) k=1 g=0 (Hermitian): |a1|^2 = cos^2(k t), empty at t = pi/2 = 1.57 s and back to 1 at pi', Math.abs((imin + 1) / 20 - Math.PI / 2) <= 0.05 && Math.abs(hh[62] - 1) < 1e-3, ((imin + 1) / 20).toFixed(2) + ' s, share at 3.15 s ' + hh[62].toFixed(5));
  await setPair(1, 0.5, 0, 'off');
  const hg = await trace();
  let dev = 0; for (let i = 0; i < 400; i++) dev = Math.max(dev, Math.abs(hg[i] - share(exact(1, 0.5, 0, (i + 1) / 20, [[1, 0], [0, 0]]))));
  const L = Math.sqrt(0.75), T = Math.PI / L, per = [];   // the share repeats every pi/E = 3.63 s: compare each tick with the tick one period on (interpolated)
  for (let i = 0; i + T * 20 + 1 < 400; i++) { const j = i + T * 20, j0 = Math.floor(j), f = j - j0; per.push(Math.abs(hg[i] - (hg[j0] * (1 - f) + hg[j0 + 1] * f))); }
  check('(b) k=1 g=0.5: the whole 20 s share trace matches the closed form (max deviation < 1e-6)', dev < 1e-6, dev.toExponential(2));
  check('(b) k=1 g=0.5: the share repeats every pi/E = 3.63 s (E = 0.866; interpolated mismatch < 3e-3)', Math.max(...per) < 3e-3, Math.max(...per).toExponential(2));

  // ---- (c) the loop ------------------------------------------------------------------------
  const runLoop = async (kind, a0) => { await setPair(1, 0, 0, kind); return pairRun(400, a0); };   // 400 ticks = 20 s = one loop
  const cw = {}, ccw = {};
  for (const [name, a0] of [['(1,0)', [1, 0, 0, 0]], ['(0,1)', [0, 0, 1, 0]], ['circular', [Math.SQRT1_2, 0, 0, Math.SQRT1_2]]]) {
    cw[name] = await runLoop('cw', a0); ccw[name] = await runLoop('ccw', a0);
    const rr = ratio(cw[name].a) / ratio(ccw[name].a);
    console.log(`  (c) from ${name}: cw share ${share(cw[name].a).toFixed(4)} (ratio ${ratio(cw[name].a).toFixed(3)})  ccw share ${share(ccw[name].a).toFixed(4)} (ratio ${ratio(ccw[name].a).toFixed(3)})  ratio-of-ratios ${rr.toFixed(1)}x`);
    check(`(c) from ${name}: clockwise ends on partner 1 (share 0.858 +- 0.02), counter-clockwise on partner 2 (0.158 +- 0.02)`, Math.abs(share(cw[name].a) - 0.858) < 0.02 && Math.abs(share(ccw[name].a) - 0.158) < 0.02, share(cw[name].a).toFixed(4) + ' / ' + share(ccw[name].a).toFixed(4));
    check(`(c) from ${name}: the two directions differ by more than 10x in |a1|^2/|a2|^2`, rr > 10, rr.toFixed(1) + 'x');
    check(`(c) from ${name}: one loop completed and recorded`, cw[name].loops >= 1 && cw[name].last && cw[name].last.loop === 'cw' && Math.abs(cw[name].last.share - share(cw[name].a)) < 1e-12 && ccw[name].last && ccw[name].last.loop === 'ccw', JSON.stringify(cw[name].last));
  }
  const th = 0.5 * Math.atan2(2, 2), ePlus = [Math.cos(th), 0, Math.sin(th), 0];   // the partner-1-heavy eigenstate at the loop's start (D = 2k, g = 0)
  const flat = await runLoop('flat', ePlus);
  check('(c) flat control (no gain) from the eigenstate: returns with overlap > 95%', flat.last && flat.last.loop === 'flat' && flat.last.back > 0.95, flat.last ? flat.last.back.toFixed(4) : 'no loop');
  check('(c) flat control keeps the share within 5% (0.854 -> ' + share(flat.a).toFixed(3) + ')', Math.abs(share(flat.a) - share(ePlus)) < 0.05);
  const txt = await page.evaluate(() => ({ loop: document.getElementById('lab-dimer-loop').textContent, a1: document.getElementById('lab-dimer-a1').textContent, seq: document.getElementById('dm-a1').textContent, circle: document.getElementById('dm-circle').textContent }));
  check('(c) the Lab readout reports the flat loop with its expectation', /flat #\d+: back to its start \d+% \(expected above 95%/.test(txt.loop), txt.loop);
  await runLoop('cw', null);
  const txt2 = await page.evaluate(() => document.getElementById('lab-dimer-loop').textContent);
  check('(c) the Lab readout reports the clockwise loop beside the expected 0.85', /clockwise #\d+: partner 1 share 0\.8\d \(expected 0\.85\)/.test(txt2), txt2);
  check('(c) the pair readouts show the shares to three places', /^0\.\d{3}$/.test(txt.a1) && /^0\.\d{3}$/.test(txt.seq), txt.a1 + ' ' + txt.seq);

  // ---- (d) the particles follow -------------------------------------------------------------
  // The partner figures evaluated here from the raw mesh (P_l^m by the same recurrence, no page code):
  // wells: the m-th azimuthal moment per ring, real-axis power (cos partner) vs imaginary-axis power (sin partner);
  // Chladni: density-weighted <S1^2> vs <S2^2>; the matter avoids the figure it feels.
  const projection = () => page.evaluate(() => {
    const P = window.__probe, rho = P.labReadDensity(), M = P.modeB, N = P.PM.N, cell = 2 * P.PM.HALF / N, h = N / 2;
    const EXT = 15, rmin = EXT * 0.3, rmax = EXT * 0.97, NR = 16, l = M.l, m = M.m, m2 = M.m2;
    const rad = P.radialProfile(l, M.n), RN = P.RAD_N;
    const plm = (L, mm, ct, st) => { let pmm = 1; for (let i = 1; i <= mm; i++) pmm *= (2 * i - 1) * st; if (L === mm) return pmm; let prev = pmm, cur = ct * (2 * mm + 1) * pmm; for (let LL = mm + 2; LL <= L; LL++) { const nxt = (ct * (2 * LL - 1) * cur - (LL + mm - 1) * prev) / (LL - mm); prev = cur; cur = nxt; } return cur; };
    const wells = P.state.fieldForm === 'wells', tw = P.velMat.uniforms.uTwist.value.y;
    const re = new Float64Array(N * NR), im = new Float64Array(N * NR); let A1 = 0, A2 = 0, W = 0;
    for (let k = 0; k < N; k++) for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const w = rho[(k * N + j) * N + i]; if (!(w > 0)) continue;
      const x = (i + 0.5 - h) * cell, y = (j + 0.5 - h) * cell, z = (k + 0.5 - h) * cell, r = Math.hypot(x, y, z);
      if (r < rmin || r > rmax) continue;
      const phi = Math.atan2(z, x), ct = y / r, st = Math.max(1e-4, Math.sqrt(1 - ct * ct));
      const rb = Math.min(NR - 1, Math.floor((r - rmin) / (rmax - rmin) * NR));
      re[j * NR + rb] += w * Math.cos(m * phi - tw); im[j * NR + rb] += w * Math.sin(m * phi - tw);
      const u = Math.min(1, r / EXT) * (RN - 1), i0 = Math.floor(u), i1 = Math.min(i0 + 1, RN - 1), jr = rad[i0 * 2] + (rad[i1 * 2] - rad[i0 * 2]) * (u - i0);
      const Pm = jr * P.schmidt(l, m) * plm(l, m, ct, st), Pm2 = jr * P.schmidt(l, m2) * plm(l, m2, ct, st);
      const S1 = Pm * Math.cos(m * phi - tw) - Pm2 * Math.sin(m2 * phi - tw), S2 = Pm * Math.sin(m * phi - tw) + Pm2 * Math.cos(m2 * phi - tw);
      A1 += w * S1 * S1; A2 += w * S2 * S2; W += w;
    }
    let Cp = 0, Sp = 0; for (let i = 0; i < N * NR; i++) { Cp += re[i] * re[i]; Sp += im[i] * im[i]; }
    return { mode: [M.n, M.l, M.m, M.m2], ringCos: Cp / (Cp + Sp), chladniShare: A2 / (A1 + A2), W, seen: P.dimer.share, asked: P.dimer.sharePred,
      txt: document.getElementById('lab-dimer-share').textContent, wells };
  });
  const hold = async (form, a0, delta) => {   // a stationary pair at large detuning: k = 0.2, D = +-6 keeps (1,0) or (0,1) put (share 0.9989 / 0.0011)
    const s = base(); s.fieldForm = form; s.lab = { on: true }; s.dimer = { on: true, kappa: 0.2, gamma: 0, delta, loop: 'off' };
    await load(s, 1);
    await page.evaluate(a0 => { const P = window.__probe; P.dimer.a = a0.slice(); P.dimerDraw(); }, a0);
    await page.evaluate(() => { window.__forceDt = 1 / 20; });
    await frames(202);   // 10 s of chamber time, one tick per frame
    await page.evaluate(() => { window.__forceDt = 1e-7; });
    return projection();
  };
  const m1 = await hold('wells', [1, 0, 0, 0], 6), m2 = await hold('wells', [0, 0, 1, 0], -6);
  console.log('  (d) wells, partner 1:', JSON.stringify(m1)); console.log('  (d) wells, partner 2:', JSON.stringify(m2));
  check('(d) wells: the figure has an azimuthal partner (m >= 1)', m1.mode[2] >= 1, m1.mode.join('/'));
  check('(d) wells, pair on partner 1: the density\'s m-moment lies on the real (cos) axis (ring power share > 0.8)', m1.ringCos > 0.8, m1.ringCos.toFixed(3));
  check('(d) wells, pair on partner 2: the density\'s m-moment lies on the imaginary (sin) axis (ring power share < 0.2)', m2.ringCos < 0.2, m2.ringCos.toFixed(3));
  check('(d) wells: the page\'s "matter on partner 1" agrees with the share asked (within 0.1, both states)', Math.abs(m1.seen - m1.asked) < 0.1 && Math.abs(m2.seen - m2.asked) < 0.1 && m1.asked > 0.99 && m2.asked < 0.01, m1.seen.toFixed(3) + '/' + m1.asked.toFixed(3) + ' ' + m2.seen.toFixed(3) + '/' + m2.asked.toFixed(3));
  check('(d) wells: the readout shows seen beside asked', /^\d\.\d\d \/ \d\.\d\d$/.test(m1.txt), m1.txt);
  const c1 = await hold('chladni', [1, 0, 0, 0], 6), c2 = await hold('chladni', [0, 0, 1, 0], -6);
  console.log('  (d) chladni, partner 1:', JSON.stringify(c1)); console.log('  (d) chladni, partner 2:', JSON.stringify(c2));
  check('(d) Chladni, pair on partner 1: the matter avoids figure 1 (<S2^2>/(<S1^2>+<S2^2>) > 0.7, computed here)', c1.chladniShare > 0.7, c1.chladniShare.toFixed(3));
  check('(d) Chladni, pair on partner 2: the matter avoids figure 2 (share < 0.3, computed here)', c2.chladniShare < 0.3, c2.chladniShare.toFixed(3));
  check('(d) Chladni: the page\'s "matter on partner 1" agrees with the share asked (within 0.15, both states)', Math.abs(c1.seen - c1.asked) < 0.15 && Math.abs(c2.seen - c2.asked) < 0.15, c1.seen.toFixed(3) + '/' + c1.asked.toFixed(3) + ' ' + c2.seen.toFixed(3) + '/' + c2.asked.toFixed(3));
  check('(d) Chladni: the test-side projection and the page\'s reading agree within 0.05', Math.abs(c1.chladniShare - c1.seen) < 0.05 && Math.abs(c2.chladniShare - c2.seen) < 0.05, (c1.chladniShare - c1.seen).toFixed(3) + ' ' + (c2.chladniShare - c2.seen).toFixed(3));

  // ---- (e) the controls ----------------------------------------------------------------------
  await load(base(), 1);
  const ui = await page.evaluate(() => {
    const P = window.__probe, out = {};
    const uni = () => P.velMat.uniforms.uDimer.value.toArray();
    out.onAtLoad = P.state.dimer.on; out.uniOn = uni();
    document.getElementById('sw-dimer').click(); out.offAfterClick = P.state.dimer.on; out.uniOff = uni(); out.sw = document.getElementById('sw-dimer').getAttribute('aria-pressed');
    document.getElementById('sw-dimer').click(); out.onAgain = P.state.dimer.on; out.aReset = P.dimer.a.slice();
    const k = document.getElementById('in-dimer-kappa'); k.value = '2.5'; k.dispatchEvent(new Event('input', { bubbles: true })); out.kappa = P.state.dimer.kappa; out.kappaTxt = document.getElementById('val-dimer-kappa').textContent;
    const g = document.getElementById('in-dimer-gamma'); g.value = '-1.5'; g.dispatchEvent(new Event('input', { bubbles: true })); out.gamma = P.state.dimer.gamma;
    const d = document.getElementById('in-dimer-delta'); d.value = '3'; d.dispatchEvent(new Event('input', { bubbles: true })); out.delta = P.state.dimer.delta; out.deltaTxt = document.getElementById('val-dimer-delta').textContent;
    document.querySelector('#dimer-loop-seg [data-loop="ccw"]').click(); out.loop = P.state.dimer.loop; out.pressed = [...document.querySelectorAll('#dimer-loop-seg button')].map(b => b.dataset.loop + '=' + b.getAttribute('aria-pressed')).join(' ');
    return out;
  });
  await page.waitForTimeout(500);   // the save is debounced by 250 ms
  ui.saved = await page.evaluate(() => JSON.parse(localStorage.getItem('resonance-chamber-v2')).dimer);
  Object.assign(ui, await page.evaluate(() => {
    const P = window.__probe, out = {};
    // a preset round trip keeps the pair's settings
    const p = { state: JSON.parse(JSON.stringify(P.state)), step: 3 }; document.querySelector('#dimer-loop-seg [data-loop="off"]').click(); P.applyPreset(p); out.roundTrip = JSON.stringify(P.state.dimer);
    // the experiment
    document.querySelector('#lab-exp-seg [data-exp="dimer"]').click(); out.exp = JSON.stringify(P.state.dimer); out.expForm = P.state.fieldForm; out.expRate = P.state.stepsPerSec; out.expLab = P.state.lab.on; out.expStep = P.step; out.expMode = P.modeB ? [P.modeB.n, P.modeB.l, P.modeB.m, P.modeB.m2] : null;
    out.hint = document.getElementById('lab-exp-hint').textContent; out.expPressed = document.querySelector('#lab-exp-seg [data-exp="dimer"]').getAttribute('aria-pressed');
    out.help = !!document.querySelector('h3') && [...document.querySelectorAll('h3')].some(h => /mode dimer/i.test(h.textContent));
    return out;
  }));
  console.log('  (e)', JSON.stringify(ui));
  check('(e) switch: off clears the uniform (x = 0), on sets it (x = 1) and resets the pair to (1, 0)', ui.onAtLoad === true && ui.uniOn[0] === 1 && ui.offAfterClick === false && ui.uniOff.every(v => v === 0) && ui.sw === 'false' && ui.onAgain === true && ui.aReset.join(',') === '1,0,0,0');
  check('(e) sliders set kappa, gamma, delta and their readouts', ui.kappa === 2.5 && ui.gamma === -1.5 && ui.delta === 3 && ui.kappaTxt === '2.50 /s' && ui.deltaTxt === '3.0 /s', ui.kappaTxt + ' ' + ui.deltaTxt);
  check('(e) loop buttons set the loop and aria-pressed', ui.loop === 'ccw' && ui.pressed === 'off=false cw=false ccw=true flat=false', ui.pressed);
  check('(e) the state is saved with the pair', ui.saved && ui.saved.kappa === 2.5 && ui.saved.loop === 'ccw');
  check('(e) a preset round trip keeps the pair\'s settings', ui.roundTrip === JSON.stringify({ on: true, kappa: 2.5, gamma: -1.5, delta: 3, loop: 'ccw' }), ui.roundTrip);
  check('(e) the experiment loads a Chladni figure with two azimuthal orders held still, instruments on, the loop clockwise, the sliders at the loop\'s start point', ui.exp === JSON.stringify({ on: true, kappa: 1, gamma: 0, delta: 2, loop: 'cw' }) && ui.expForm === 'chladni' && ui.expRate === 0.02 && ui.expLab === true && ui.expStep === 1 && ui.expMode && ui.expMode[2] >= 1 && ui.expMode[3] >= 1 && ui.expMode[2] !== ui.expMode[3], JSON.stringify(ui.expMode) + ' ' + ui.exp);
  check('(e) the experiment hint states the prediction, the measured numbers and the caution', /0\.85/.test(ui.hint) && /0\.15/.test(ui.hint) && /95%/.test(ui.hint) && /reseed/i.test(ui.hint) && /measured/i.test(ui.hint) && ui.expPressed === 'true');
  check('(e) the help text has a mode dimer section', ui.help);
  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
