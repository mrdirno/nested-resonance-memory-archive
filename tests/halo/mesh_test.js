'use strict';
/* Self-gravity mesh: the Exact solver and cloud-in-cell, checked against an
   independent JS reference solver (DST-I diagonalisation of the page's own
   operator: 7-point Laplacian in cell units, potential zero outside the mesh).
     1. solver equivalence on a frozen swarm density: Exact, Jacobi x6 from
        cold, x600, x2400 against the reference
     2. the force law cell by cell: a 1000-particle clump and a test particle
        in each cell along +x, potential column and F = dv/dt against the
        reference, under both solvers
     3. momentum: mirror pairs of clumps under both assignments, and a lone
        clump's self-force
     4. the eight cloud-in-cell weights of one particle sum to one
     5. the interface: state, uniform, storage, scenario/experiment swaps
     6. byte-equivalence of the as-found pair against a probe build of the
        page before this change (RC_BASE=<path>, else reported as skipped)
   Runs on the probe build (make_test_page.py first), SwiftShader. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const f3 = x => (typeof x === 'number' ? x.toExponential(2) : String(x));

const N = 32, EXTENT = 15, PM_HALF = EXTENT * 1.02, PM_CELL = 2 * PM_HALF / N, SG = 14, CELLS = N * N * N, TICK = 1 / 20;
const idx = (i, j, k) => (k * N + j) * N + i;
const at = (a, i, j, k) => (i < 0 || j < 0 || k < 0 || i >= N || j >= N || k >= N) ? 0 : a[idx(i, j, k)];
const cellCentre = c => (c + 0.5 - N / 2) * PM_CELL;            // world coordinate of the centre of cell c
const cont = U => (U / N - 0.5) * 2 * PM_HALF;                  // world coordinate of continuous cell coordinate U (cell i spans [i, i+1))

/* ---- reference solver: DST-I basis sin(pi (i+1)(k+1)/(N+1)) diagonalises the operator ---- */
const SIN = new Float64Array(N * N);
for (let a = 0; a < N; a++) for (let i = 0; i < N; i++) SIN[a * N + i] = Math.sin(Math.PI * (a + 1) * (i + 1) / (N + 1));
const LAM = new Float64Array(N);
for (let k = 0; k < N; k++) LAM[k] = 2 * Math.cos(Math.PI * (k + 1) / (N + 1)) - 2;
function dstAxis(src, axis) {
  const out = new Float64Array(CELLS), stride = axis === 0 ? 1 : axis === 1 ? N : N * N;
  for (let k = 0; k < N; k++) for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const a = axis === 0 ? i : axis === 1 ? j : k, base = idx(i, j, k) - a * stride;
    let s = 0;
    for (let m = 0; m < N; m++) s += SIN[a * N + m] * src[base + m * stride];
    out[idx(i, j, k)] = s;
  }
  return out;
}
const dst3 = a => dstAxis(dstAxis(dstAxis(a, 0), 1), 2);
function solveExact(delta) {
  const d = dst3(delta), c = Math.pow(2 / (N + 1), 3);
  for (let k = 0; k < N; k++) for (let j = 0; j < N; j++) for (let i = 0; i < N; i++)
    d[idx(i, j, k)] *= c / (LAM[i] + LAM[j] + LAM[k]);
  return dst3(d);
}
function laplacian(phi) {
  const out = new Float64Array(CELLS);
  for (let k = 0; k < N; k++) for (let j = 0; j < N; j++) for (let i = 0; i < N; i++)
    out[idx(i, j, k)] = at(phi, i + 1, j, k) + at(phi, i - 1, j, k) + at(phi, i, j + 1, k) + at(phi, i, j - 1, k)
      + at(phi, i, j, k + 1) + at(phi, i, j, k - 1) - 6 * phi[idx(i, j, k)];
  return out;
}
function jacobi(delta, sweeps, phi0) {
  let phi = phi0 ? Float64Array.from(phi0) : new Float64Array(CELLS);
  for (let s = 0; s < sweeps; s++) {
    const next = new Float64Array(CELLS);
    for (let k = 0; k < N; k++) for (let j = 0; j < N; j++) for (let i = 0; i < N; i++)
      next[idx(i, j, k)] = (at(phi, i + 1, j, k) + at(phi, i - 1, j, k) + at(phi, i, j + 1, k) + at(phi, i, j - 1, k)
        + at(phi, i, j, k + 1) + at(phi, i, j, k - 1) - delta[idx(i, j, k)]) / 6;
    phi = next;
  }
  return phi;
}
const maxAbs = a => { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i])); return m; };
const relMaxErr = (a, ref) => { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - ref[i])); return m / maxAbs(ref); };
// the page's contrast from a read-back density: src = rho * cells * 1024 / total - 1, exactly as the solve shader does
const contrast = (rho, total) => Float64Array.from(rho, r => r * CELLS * 1024 / total - 1);
// nearest-cell force from a potential column along x at cell (c,16,16)
const forceX = (phi, c, s) => -SG * s * (at(phi, c + 1, 16, 16) - at(phi, c - 1, 16, 16)) / (2 * PM_CELL);
const forceAt = (phi, i, j, k, s) => [
  -SG * s * (at(phi, i + 1, j, k) - at(phi, i - 1, j, k)) / (2 * PM_CELL),
  -SG * s * (at(phi, i, j + 1, k) - at(phi, i, j - 1, k)) / (2 * PM_CELL),
  -SG * s * (at(phi, i, j, k + 1) - at(phi, i, j, k - 1)) / (2 * PM_CELL)];

/* the quiet state: every prescribed force off, only the swarm's own gravity acts */
const QUIET = {
  stepsPerSec: 0.02, smooth: false, fieldForm: 'chladni', fieldExp: -12, damping: 0, quality: 0.5, colorMode: 0,
  centers: { on: false }, vessel: { form: 'off' }, guides: false, autoOrbit: false,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false, equal: false, trefoil: false, torus: false, hopf: false },
  cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45, mag: 0, twist: false, aniso: 0, helix: 0, cascade: 'out', selfgrav: 0.003, gainloss: 0 },
  substeps: 1, lorentz: 'euler', lab: { on: false }, sacred: 'off',
};
/* Spinning Chladni as the lab's spin experiment has it (self-gravity 0.45), at a headless count */
const SPIN = {
  particles: 250000, stepsPerSec: 0.5, smooth: true, fieldForm: 'chladni', fieldExp: 2, damping: 1, quality: 0.5, colorMode: 1, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'phi' }, offsetMode: 'auto', strideIndex: 0,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false, equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false }, vessel: { form: 'off' }, guides: false, autoOrbit: false,
  cosmos: { boundary: 'reflect', hubble: 1.2, epoch: true, epochLen: 10, mag: 0.4, twist: true, aniso: 0.55, helix: 0.8, cascade: 'out', selfgrav: 0.45, gainloss: 0 },
  substeps: 1, lorentz: 'euler', lab: { on: false }, sacred: 'off',
};

const LAUNCH = { executablePath: process.env.PW_CHROMIUM_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] };
const seededRandom = () => {
  let a = 0x9E3779B9;
  window.__seedRng = s => { a = s | 0; };   // three.js draws Math.random() for every object id, so the test re-seeds right before reseed()
  Math.random = function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  window.__forceDt = 1e-7;   // the frame loop stays alive but never accumulates a tick: only the test ticks
  try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {}
};
// helpers installed on the page: mesh readback, cold start, placing particles, ticking
const HELPERS = () => {
  const P = window.__probe;
  const cell = 2 * P.PM.HALF / P.PM.N;
  const M = window.__mesh = {
    cc: c => (c + 0.5 - P.PM.N / 2) * cell,                 // world coordinate of the centre of cell c
    cont: U => (U / P.PM.N - 0.5) * 2 * P.PM.HALF,          // world coordinate of continuous cell coordinate U
    readMesh(target) {
      const PM = P.PM, n = PM.N, W = n * PM.TX, H = n * PM.TY, raw = P.readTarget(target, 0, 0, W, H), out = new Array(n * n * n);
      for (let k = 0; k < n; k++) { const tc = k % PM.TX, tr = Math.floor(k / PM.TX);
        for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) out[(k * n + j) * n + i] = raw[((tr * n + j) * W + tc * n + i) * 4]; }
      return out;
    },
    clearPot() {
      const r = P.renderer, c = new THREE.Color(); r.getClearColor(c); const a = r.getClearAlpha();
      r.setClearColor(0x000000, 0);
      for (const t of [P.pmPot, P.pmPotB]) { r.setRenderTarget(t); r.clear(true, false, false); }
      r.setRenderTarget(null); r.setClearColor(c, a);
    },
    setup(patch) {
      const s = JSON.parse(JSON.stringify(P.DEFAULTS));
      const deep = (d, x) => { for (const k of Object.keys(x)) { if (x[k] && typeof x[k] === 'object' && !Array.isArray(x[k])) { if (!d[k]) d[k] = {}; deep(d[k], x[k]); } else d[k] = x[k]; } };
      deep(s, patch);
      P.applyPreset({ state: s, step: 0 });
      return P.texSize;
    },
    place(list) {   // particle i at list[i] (world xyz); every other texel parked outside the mesh; velocities zero; w channels kept as seeded
      const S = P.texSize, pos = P.readTarget(P.posA, 0, 0, S, S), vel = P.readTarget(P.velA, 0, 0, S, S);
      for (let t = 0; t < S * S; t++) { const q = list[t] || [20, 20, 20]; pos[t * 4] = q[0]; pos[t * 4 + 1] = q[1]; pos[t * 4 + 2] = q[2]; vel[t * 4] = 0; vel[t * 4 + 1] = 0; vel[t * 4 + 2] = 0; }
      for (let row = 0; row < S; row++) { P.writeRow(P.posA, row, pos.subarray(row * S * 4, (row + 1) * S * 4), S); P.writeRow(P.velA, row, vel.subarray(row * S * 4, (row + 1) * S * 4), S); }
    },
    read(target, indices) { const S = P.texSize, a = P.readTarget(target, 0, 0, S, S); return indices.map(i => [a[i * 4], a[i * 4 + 1], a[i * 4 + 2]]); },
    solve(n) { for (let i = 0; i < n; i++) P.pmSolve(); },
    tick(n) { for (let i = 0; i < n; i++) P.simTick(); },
    density() { P.pmDeposit(); P.renderer.setRenderTarget(null); return M.readMesh(P.pmDens); },
    hash() {   // FNV-1a over the bytes of both state textures, two seeds
      const S = P.texSize, out = [];
      for (const t of [P.posA, P.velA]) { const f = new Float32Array(S * S * 4); P.renderer.readRenderTargetPixels(t, 0, 0, S, S, f); const b = new Uint8Array(f.buffer);
        let h1 = 0x811c9dc5, h2 = 0x01000193; for (let i = 0; i < b.length; i++) { h1 = Math.imul(h1 ^ b[i], 0x01000193); h2 = Math.imul(h2 ^ b[i], 0x01000193) + 7 | 0; }
        out.push((h1 >>> 0).toString(16) + (h2 >>> 0).toString(16), f[0], f[4 * 1234 + 1], f[f.length - 2]); }
      return out;
    },
  };
  return true;
};

(async () => {
  const browser = await chromium.launch(LAUNCH);
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(seededRandom);
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.evaluate(HELPERS);
  await page.evaluate(([Q, S]) => { window.__QUIET = Q; window.__SPIN = S; }, [QUIET, SPIN]);
  check('boot (probe hooks present)', await page.evaluate(() => typeof window.__probe.pmSolve === 'function' && typeof window.__probe.pmDeposit === 'function'));

  /* ---- 0. the reference is a solution of the operator ---- */
  {
    const delta = new Float64Array(CELLS); let x = 12345;
    for (let i = 0; i < CELLS; i++) { x = (x * 1103515245 + 12345) & 0x7fffffff; delta[i] = x / 0x7fffffff - 0.5; }
    const phi = solveExact(delta), res = relMaxErr(laplacian(phi), delta);
    check('reference: DST-I solve satisfies the stencil, |L phi - delta| / |delta| < 1e-9', res < 1e-9, f3(res));
  }

  /* ---- 1. solver equivalence on a frozen swarm density ---- */
  console.log('\n[1] solver equivalence on a frozen Spinning Chladni swarm (250,000 particles, self-gravity 0.45, 3 s in)');
  {
    const r = await page.evaluate(() => {
      const P = window.__probe, M = window.__mesh;
      M.setup(window.__SPIN);
      M.tick(60);
      M.solve(1);                                   // the potential the page would use for the next tick: six sweeps, warm
      const live = M.readMesh(P.pmPot);
      M.solve(60);                                  // 360 more sweeps on the now-frozen density
      const live2 = M.readMesh(P.pmPot);
      const total = Math.min(P.state.particles, P.texSize * P.texSize);
      const rho = M.density();
      P.state.pm.solver = 'exact'; P.syncPm();
      M.solve(1);
      const exact = M.readMesh(P.pmPot);
      P.state.pm.solver = 'jacobi'; P.syncPm();
      M.clearPot(); M.solve(1);
      const j6 = M.readMesh(P.pmPot);
      M.solve(99);
      const j600 = M.readMesh(P.pmPot);
      M.solve(300);
      const j2400 = M.readMesh(P.pmPot);
      return { total, rho, live, live2, exact, j6, j600, j2400, potType: P.pmPot.texture.type, F: THREE.FloatType };
    }, undefined);
    const delta = contrast(r.rho, r.total), ref = solveExact(delta);
    const eExact = relMaxErr(r.exact, ref), e6 = relMaxErr(r.j6, ref), e600 = relMaxErr(r.j600, ref), e2400 = relMaxErr(r.j2400, ref);
    const j6ref = jacobi(delta, 6), e6stencil = relMaxErr(r.j6, j6ref), eLive = relMaxErr(r.live, ref);
    const m6 = dst3(r.j6)[0], mref = dst3(ref)[0];
    const mLive = dst3(r.live)[0], mLive2 = dst3(r.live2)[0], decay = (mLive2 - mref) / (mLive - mref), decayPred = Math.pow(Math.cos(Math.PI / 33), 360);
    console.log(`    max|delta| ${maxAbs(delta).toFixed(1)}  max|phi_ref| ${maxAbs(ref).toFixed(2)}  potential target ${r.potType === r.F ? 'float' : 'half-float'}`);
    console.log(`    live six sweeps (warm-started through 3 s of running): max|phi - phi_ref| / max|phi_ref| = ${f3(eLive)}; lowest-mode coefficient ${mLive.toFixed(1)} vs exact ${mref.toFixed(1)}; after 360 more sweeps on the frozen density the lowest-mode error is x${decay.toFixed(3)} (cos(pi/33)^360 = ${decayPred.toFixed(3)})`);
    check('the live lag decays at the slowest mode\'s rate (x0.20 per 360 sweeps): it is lag, not a defect', Math.abs(decay - decayPred) < 0.05, `${decay.toFixed(3)} vs ${decayPred.toFixed(3)}`);
    console.log(`    Exact        max|phi - phi_ref| / max|phi_ref| = ${f3(eExact)}`);
    console.log(`    Jacobi x6    ${f3(e6)}   (against a JS x6 from cold: ${f3(e6stencil)}; lowest-mode fraction ${(m6 / mref).toFixed(4)}, predicted 1 - cos(pi/33)^6 = ${(1 - Math.pow(Math.cos(Math.PI / 33), 6)).toFixed(4)})`);
    console.log(`    Jacobi x600  ${f3(e600)}`);
    console.log(`    Jacobi x2400 ${f3(e2400)}`);
    check('Exact solve matches the reference to 2e-3', eExact < 2e-3, f3(eExact));
    check('Jacobi x6 from cold reproduces the JS six sweeps (same stencil) to 1e-4', e6stencil < 1e-4, f3(e6stencil));
    check('Jacobi x6 from cold: lowest mode at 2.7% of exact (1 - cos(pi/33)^6)', Math.abs(m6 / mref - 0.0269) < 0.003, (m6 / mref).toFixed(4));
    // the slowest mode has time constant 221 sweeps (1.84 s at 120 sweeps/s): x600 still carries e^-2.7 = 6.6% of it, x2400 e^-10.9
    check('Jacobi x600 from cold: under 1e-2 of the reference (the slowest mode is only 93% converged there)', e600 < 1e-2, f3(e600));
    check('Jacobi x2400 from cold matches the reference to 2e-3', e2400 < 2e-3, f3(e2400));
    global.__solverAgree = { eLive, eExact, e600, e2400 };
  }

  /* ---- 2. the force law cell by cell ---- */
  console.log('\n[2] force law: 1000 particles in cell (16,16,16), one test particle in each cell (16+d,16,16)');
  const S_FORCE = 0.003;   // strongest kick (d = 1) ~149 of the 500 ceiling: a 3x margin, while d = 14 still moves 0.68 per second
  const forceLaw = async (solver, warm) => page.evaluate(([solver, warm, s]) => {
    const P = window.__probe, M = window.__mesh, cc = M.cc;
    M.setup(Object.assign({}, window.__QUIET, { particles: 1014, pm: { solver, assign: 'ngp' }, cosmos: Object.assign({}, window.__QUIET.cosmos, { selfgrav: s }) }));
    const list = []; for (let i = 0; i < 1000; i++) list.push([cc(16), cc(16), cc(16)]);
    for (let d = 1; d <= 14; d++) list.push([cc(16 + d), cc(16), cc(16)]);
    M.place(list);
    M.clearPot(); M.solve(warm);
    const phi = M.readMesh(P.pmPot);
    const pos0 = M.read(P.posA, [0])[0];
    M.tick(1);
    const ids = []; for (let d = 1; d <= 14; d++) ids.push(999 + d);
    return { phi, dv: M.read(P.velA, ids), dv0: M.read(P.velA, [0])[0], pos0, pos1: M.read(P.posA, [0])[0], sg: P.velMat.uniforms.uSelfGrav.value };
  }, [solver, warm, S_FORCE]);
  // the reference potential for exactly this density
  const cnt = new Float64Array(CELLS); cnt[idx(16, 16, 16)] = 1000; for (let d = 1; d <= 14; d++) cnt[idx(16 + d, 16, 16)] = 1;
  const deltaF = Float64Array.from(cnt, c => c * CELLS / 1014 - 1), refF = solveExact(deltaF), Q = deltaF[idx(16, 16, 16)];
  for (const [solver, warm, label] of [['jacobi', 400, 'Six sweeps, warm-started (400 solves = 2400 sweeps, particles held still)'], ['exact', 1, 'Exact']]) {
    const r = await forceLaw(solver, warm);
    console.log(`  ${label}:`);
    let colErr = 0, fErr = 0;
    console.log('     d   phi_gpu      phi_ref      F_measured   F_exact_discrete  F_continuum   meas/ref  meas/cont');
    for (let d = 0; d <= 14; d++) {
      const pg = r.phi[idx(16 + d, 16, 16)], pr = refF[idx(16 + d, 16, 16)];
      colErr = Math.max(colErr, Math.abs(pg - pr) / Math.abs(pr));
      if (d === 0) { console.log(`    ${String(d).padStart(2)}  ${pg.toFixed(3).padStart(10)}  ${pr.toFixed(3).padStart(10)}   (the clump itself)`); continue; }
      const Fm = r.dv[d - 1][0] / TICK, Fe = forceX(refF, 16 + d, S_FORCE), Fc = -SG * S_FORCE * Q / (4 * Math.PI * d * d) / PM_CELL;
      fErr = Math.max(fErr, Math.abs(Fm - Fe) / Math.abs(Fe));
      console.log(`    ${String(d).padStart(2)}  ${pg.toFixed(3).padStart(10)}  ${pr.toFixed(3).padStart(10)}  ${Fm.toFixed(4).padStart(11)}  ${Fe.toFixed(4).padStart(15)}  ${Fc.toFixed(4).padStart(12)}  ${(Fm / Fe).toFixed(5).padStart(8)}  ${(Fm / Fc).toFixed(3).padStart(8)}`);
    }
    const selfF = Math.hypot(r.dv0[0], r.dv0[1], r.dv0[2]) / TICK, moved = Math.hypot(r.pos1[0] - r.pos0[0], r.pos1[1] - r.pos0[1], r.pos1[2] - r.pos0[2]);
    console.log(`    clump: force on it ${selfF.toFixed(4)} (x ${(r.dv0[0] / TICK).toFixed(4)}: the 14 test particles' pull; reference ${forceX(refF, 16, S_FORCE).toFixed(4)}), moved ${moved.toExponential(2)} of a ${PM_CELL.toFixed(3)} cell in the tick`);
    check(`${solver}: potential column matches the reference cell by cell (rel err < 1e-3)`, colErr < 1e-3, f3(colErr));
    check(`${solver}: F = dv/dt matches -SG s (phi[c+1]-phi[c-1]) / (2 cell) of the reference for d = 1..14 (rel err < 1e-3)`, fErr < 1e-3, f3(fErr));
    check(`${solver}: the clump holds still (its own force < 1% of the d = 1 force, stays inside its cell)`, selfF < 0.01 * Math.abs(forceX(refF, 17, S_FORCE)) && moved < 0.01 * PM_CELL, `${selfF.toFixed(4)} vs ${Math.abs(forceX(refF, 17, S_FORCE)).toFixed(2)}, moved ${moved.toExponential(2)}`);
    check(`${solver}: strongest kick under the 500 ceiling`, Math.abs(r.dv[0][0] / TICK) < 500, (r.dv[0][0] / TICK).toFixed(1));
  }

  /* ---- 3. momentum ---- */
  console.log('\n[3] momentum: two equal clumps (500 each) placed as mirror images about the mesh centre');
  const S_MOM = 0.1;
  const momentum = async (assign, solver, p1, p2, lone, note) => {
    const r = await page.evaluate(([assign, solver, p1, p2, lone, s]) => {
      const P = window.__probe, M = window.__mesh;
      const run = list => {
        M.setup(Object.assign({}, window.__QUIET, { particles: 1000, pm: { solver, assign }, cosmos: Object.assign({}, window.__QUIET.cosmos, { selfgrav: s }) }));
        M.place(list); M.clearPot(); M.solve(solver === 'exact' ? 1 : 400); M.tick(1);   // six sweeps: 400 warm solves = 2400 sweeps first
        return M.read(P.velA, [0, 500]);
      };
      const pair = []; for (let i = 0; i < 500; i++) pair.push(p1); for (let i = 0; i < 500; i++) pair.push(p2);
      const solo = []; for (let i = 0; i < 500; i++) solo.push(lone);
      return { pair: run(pair), solo: run(solo) };
    }, [assign, solver, p1, p2, lone, S_MOM]);
    const F1 = r.pair[0].map(v => v / TICK), F2 = r.pair[1].map(v => v / TICK), Fl = r.solo[0].map(v => v / TICK);
    const asym = Math.abs(F1[0] + F2[0]) / Math.abs(F1[0]), selfRel = Math.hypot(...Fl) / Math.abs(F1[0]);
    console.log(`  ${assign} / ${solver}${note ? ' ' + note : ''}: F1 = (${F1.map(v => v.toFixed(4)).join(', ')})  F2 = (${F2.map(v => v.toFixed(4)).join(', ')})  |F1x+F2x|/|F1x| = ${f3(asym)};  lone clump at the centre: |F| = ${Math.hypot(...Fl).toExponential(2)} = ${(selfRel * 100).toFixed(3)}% of the pair force`);
    return { asym, selfRel, F1, F2, Fl };
  };
  // nearest cell: mirror cells are c and 31-c (cells 12 and 19, 7 apart); the lone clump in cell 16, half a cell off centre
  for (const solver of ['jacobi', 'exact']) {
    const r = await momentum('ngp', solver, [cellCentre(12), cellCentre(16), cellCentre(16)], [cellCentre(19), cellCentre(16), cellCentre(16)], [cellCentre(16), cellCentre(16), cellCentre(16)]);
    check(`nearest cell / ${solver}: F12 = -F21 to 1e-4 relative (mirror cells 12 and 19)`, r.asym < 1e-4, f3(r.asym));
    check(`nearest cell / ${solver}: lone clump's self-force < 1% of the pair force`, r.selfRel < 0.01, (r.selfRel * 100).toFixed(3) + '%');
  }
  { // the literal (16 +- 4) cells under nearest cell are NOT mirror images (16 is half a cell off the centre): report the wall's share
    const r = await momentum('ngp', 'exact', [cellCentre(12), cellCentre(16), cellCentre(16)], [cellCentre(20), cellCentre(16), cellCentre(16)], [cellCentre(16), cellCentre(16), cellCentre(16)], '(cells 12 and 20, not mirror images: the walls\' images differ)');
    console.log(`    -> that asymmetry, ${(r.asym * 100).toFixed(2)}%, is the box's, not the solver's: the same pair placed as mirror images cancels to 1e-4 above`);
  }
  // cloud-in-cell: continuous coordinates 16 +- 4 are exact mirror images; the lone clump at the exact centre shares 1/8 into each of eight cells
  for (const solver of ['jacobi', 'exact']) {
    const r = await momentum('cic', solver, [cont(12), 0, 0], [cont(20), 0, 0], [0, 0, 0]);
    check(`cloud-in-cell / ${solver}: F12 = -F21 to 1e-4 relative (16 +- 4 cells about the centre)`, r.asym < 1e-4, f3(r.asym));
    check(`cloud-in-cell / ${solver}: lone clump at the centre feels no self-force (< 1e-3 of the pair force)`, r.selfRel < 1e-3, (r.selfRel * 100).toExponential(2) + '%');
  }

  /* ---- 4. the eight weights ---- */
  console.log('\n[4] cloud-in-cell weights of one particle at cell coordinate (12.8, 7.6, 20.25)');
  {
    const U = [12.8, 7.6, 20.25];
    const r = await page.evaluate(U => {
      const P = window.__probe, M = window.__mesh, cont = M.cont;
      M.setup(Object.assign({}, window.__QUIET, { particles: 1000, pm: { solver: 'jacobi', assign: 'cic' }, cosmos: Object.assign({}, window.__QUIET.cosmos, { selfgrav: 0.1 }) }));
      M.place([[cont(U[0]), cont(U[1]), cont(U[2])]]);
      const cic = M.density();
      document.querySelector('#pm-assign-seg button[data-pmassign="ngp"]').click();
      const ngp = M.density();
      return { cic, ngp, assign: P.state.pm.assign, uCic: P.velMat.uniforms.uCic.value };
    }, U);
    const u = U.map(x => x - 0.5), b = u.map(Math.floor), f = u.map((x, i) => x - b[i]);
    const unit = r.cic.reduce((s, v) => s + v, 0);
    let wsum = 0, werr = 0, cells = [];
    for (let n = 0; n < 8; n++) {
      const k = [n & 1, (n >> 1) & 1, (n >> 2) & 1], w = k.reduce((p, kk, i) => p * (kk ? f[i] : 1 - f[i]), 1);
      const got = r.cic[idx(b[0] + k[0], b[1] + k[1], b[2] + k[2])] / unit;
      wsum += w; werr = Math.max(werr, Math.abs(got - w)); cells.push(`(${b[0] + k[0]},${b[1] + k[1]},${b[2] + k[2]}) ${got.toFixed(5)} vs ${w.toFixed(5)}`);
    }
    const others = r.cic.reduce((s, v, i) => { const [ci, cj, ck] = [i % N, Math.floor(i / N) % N, Math.floor(i / (N * N))]; return (ci - b[0] >= 0 && ci - b[0] <= 1 && cj - b[1] >= 0 && cj - b[1] <= 1 && ck - b[2] >= 0 && ck - b[2] <= 1) ? s : s + Math.abs(v); }, 0);
    console.log('    ' + cells.join('\n    '));
    console.log(`    total deposited ${unit.toExponential(6)} (one particle = ${(1 / 1024).toExponential(6)}), weights sum ${wsum.toFixed(6)}, mass outside the eight cells ${others}`);
    check('eight cells hold (1 - |frac|) products, sum 1 (rel 1e-4), nothing elsewhere', werr < 1e-4 && Math.abs(unit * 1024 - 1) < 1e-3 && others === 0, `max weight err ${f3(werr)}, total x1024 ${(unit * 1024).toFixed(6)}`);
    const ngpCell = r.ngp[idx(Math.floor(U[0]), Math.floor(U[1]), Math.floor(U[2]))], ngpTotal = r.ngp.reduce((s, v) => s + v, 0);
    check('back on nearest cell the whole particle sits in cell floor(U) = (12, 7, 20)', Math.abs(ngpCell * 1024 - 1) < 1e-3 && ngpCell === ngpTotal && r.assign === 'ngp' && r.uCic === 0, `${(ngpCell * 1024).toFixed(6)}`);
  }

  /* ---- 5. the interface ---- */
  console.log('\n[5] interface');
  {
    const seg = await page.evaluate(() => ({
      solver: [...document.querySelectorAll('#pm-solver-seg button')].map(b => [b.dataset.pmsolver, b.textContent.trim(), b.getAttribute('aria-pressed')]),
      assign: [...document.querySelectorAll('#pm-assign-seg button')].map(b => [b.dataset.pmassign, b.textContent.trim(), b.getAttribute('aria-pressed')]),
      pm: window.__probe.state.pm, def: window.__probe.DEFAULTS.pm }));
    check('two segs in the Cosmos panel with the labelled choices, as-found pair pressed', JSON.stringify(seg.solver.map(x => x[1])) === '["Six sweeps (as found)","Exact"]' && JSON.stringify(seg.assign.map(x => x[1])) === '["Nearest cell (as found)","Cloud-in-cell"]' && seg.solver[0][2] === 'true' && seg.assign[0][2] === 'true', JSON.stringify(seg));
    const where = await page.evaluate(() => { const row = document.querySelector('#in-selfgrav').closest('.slider-row'); let n = row.nextElementSibling, seen = []; while (n && seen.length < 3) { seen.push(n.id || (n.querySelector('.seg') || {}).id || n.tagName); n = n.nextElementSibling; }
      return { inCosmos: !!document.querySelector('#panel-cosmos #pm-solver-seg') && !!document.querySelector('#panel-cosmos #pm-assign-seg'), after: seen }; });
    check('they sit beside the self-gravity slider (its row, its note, then solver, then mesh)', where.inCosmos && where.after[1] === 'pm-solver-seg' && where.after[2] === 'pm-assign-seg', JSON.stringify(where));
    check('default state.pm = { solver: jacobi, assign: ngp }', seg.def.solver === 'jacobi' && seg.def.assign === 'ngp' && seg.pm.solver === 'jacobi' && seg.pm.assign === 'ngp', JSON.stringify(seg.pm));
    await page.evaluate(() => { document.querySelector('#pm-solver-seg button[data-pmsolver="exact"]').click(); document.querySelector('#pm-assign-seg button[data-pmassign="cic"]').click(); });
    await page.waitForTimeout(600);   // saveState is debounced
    const on = await page.evaluate(() => { const P = window.__probe; return { pm: P.state.pm, uCic: P.velMat.uniforms.uCic.value,
      pressed: [document.querySelector('#pm-solver-seg button[data-pmsolver="exact"]').getAttribute('aria-pressed'), document.querySelector('#pm-assign-seg button[data-pmassign="cic"]').getAttribute('aria-pressed')],
      saved: JSON.parse(localStorage.getItem('resonance-chamber-v2')).pm }; });
    check('clicks set state, uniform, aria-pressed and storage', on.pm.solver === 'exact' && on.pm.assign === 'cic' && on.uCic === 1 && on.pressed.join() === 'true,true' && on.saved.solver === 'exact' && on.saved.assign === 'cic', JSON.stringify(on));
    const swap = await page.evaluate(() => { const P = window.__probe; P.applyScenario('lacework'); const a = JSON.stringify(P.state.pm);
      document.querySelector('#lab-exp-seg button[data-exp="memory"]').click(); const b = JSON.stringify(P.state.pm); const lab = P.state.lab.on;
      P.applyScenario('jellyfish'); return { a, b, lab, c: JSON.stringify(P.state.pm), u: P.velMat.uniforms.uCic.value }; });
    check('a scenario swap and a lab experiment keep the mesh choices (like the render settings)', swap.a === '{"solver":"exact","assign":"cic"}' && swap.b === swap.a && swap.c === swap.a && swap.lab === true && swap.u === 1, JSON.stringify(swap));
    const preset = await page.evaluate(() => { const P = window.__probe; document.getElementById('preset-name').value = 'mesh test'; document.getElementById('btn-preset-save').click();
      const keys = Object.keys(localStorage).filter(k => (localStorage.getItem(k) || '').includes('"mesh test"'));
      const list = keys.length ? JSON.parse(localStorage.getItem(keys[0])) : []; const p = (Array.isArray(list) ? list : []).find(x => x.name === 'mesh test');
      const got = p && p.state && p.state.pm; P.applyPreset({ state: { pm: { solver: 'bogus', assign: 42 } }, step: 0 }); return { got, sanitized: P.state.pm, u: P.velMat.uniforms.uCic.value }; });
    check('a saved preset captures pm; a bad pm sanitises to the as-found pair', preset.got && preset.got.solver === 'exact' && preset.got.assign === 'cic' && preset.sanitized.solver === 'jacobi' && preset.sanitized.assign === 'ngp' && preset.u === 0, JSON.stringify(preset));
    // a browser that saved exact + cloud-in-cell comes back with them
    const ctx = await browser.newContext();
    const p2 = await ctx.newPage();
    await p2.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5, pm: { solver: 'exact', assign: 'cic' } })); } catch (e) {} });
    await p2.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
    await p2.waitForSelector('.boot.done', { timeout: 90000 });
    const back = await p2.evaluate(() => { const P = window.__probe; return { pm: P.state.pm, u: P.velMat.uniforms.uCic.value, pressed: document.querySelector('#pm-assign-seg button[data-pmassign="cic"]').getAttribute('aria-pressed') }; });
    check('saved choices survive a reload (state, uniform, button)', back.pm.solver === 'exact' && back.pm.assign === 'cic' && back.u === 1 && back.pressed === 'true', JSON.stringify(back));
    await ctx.close();
  }

  /* ---- 6. byte-equivalence of the as-found pair ---- */
  console.log('\n[6] byte-equivalence: seeded Math.random, 1/20 s frames, exactly 100 ticks, posA + velA hashed');
  const base = process.env.RC_BASE || path.join(__dirname, 'rc-base.html');
  const runOff = async (file, label) => {
    const ctx = await browser.newContext();
    const pg = await ctx.newPage();
    await pg.addInitScript(seededRandom);
    await pg.goto('file://' + path.resolve(file));
    await pg.waitForSelector('.boot.done', { timeout: 90000 });
    await pg.evaluate(HELPERS);
    await pg.evaluate(([Q, S]) => { window.__QUIET = Q; window.__SPIN = S; }, [QUIET, SPIN]);
    // one evaluate: re-seed, reseed the swarm, then exactly n frames of 1/20 s (the page ticks once per frame), then freeze again
    const run = n => pg.evaluate(n => new Promise(res => { const P = window.__probe; window.__seedRng(0x9E3779B9); P.reseed(); const t0 = P.simTime; window.__forceDt = 1 / 20;
      let k = 0; const f = () => { if (++k >= n) { window.__forceDt = 1e-7; res({ ticks: Math.round((P.simTime - t0) / (1 / 20)), h: window.__mesh.hash(), pm: JSON.stringify(P.state.pm || null), sg: P.state.cosmos.selfgrav }); } else requestAnimationFrame(f); }; requestAnimationFrame(f); }), n);
    const out = {};
    // A: the saved default state (Chladni, expansion, epochs, magnetic term; self-gravity off)
    out.A = await run(100);
    // B: Spinning Chladni with self-gravity 0.45 at 65,536 particles: deposit, six sweeps, gather every tick
    await pg.evaluate(() => { window.__mesh.setup(Object.assign({}, window.__SPIN, { particles: 65536 })); });
    out.B = await run(100);
    await ctx.close();
    console.log(`    ${label}: A ${out.A.ticks} ticks ${out.A.h[0]}/${out.A.h[4]}  B ${out.B.ticks} ticks ${out.B.h[0]}/${out.B.h[4]} (pm ${out.B.pm}, self-gravity ${out.B.sg}) sample ${out.B.h[1]},${out.B.h[2]},${out.B.h[3]}`);
    return out;
  };
  if (!fs.existsSync(base)) {
    console.log(`    SKIPPED: no probe build of the page before this change at ${base} (set RC_BASE=<path>)`);
    const mine = await runOff(path.join(__dirname, 'rc-test.html'), 'this build');
    check('this build ticks exactly 100 times per 100 frames in both runs', mine.A.ticks === 100 && mine.B.ticks === 100);
  } else {
    const b1 = await runOff(base, 'before, run 1'), b2 = await runOff(base, 'before, run 2'), mine = await runOff(path.join(__dirname, 'rc-test.html'), 'this build');
    const same = (x, y) => JSON.stringify(x.A.h) === JSON.stringify(y.A.h) && JSON.stringify(x.B.h) === JSON.stringify(y.B.h);
    check('the build before this change reproduces itself (seeded, 100 ticks)', same(b1, b2) && b1.A.ticks === 100 && b1.B.ticks === 100);
    check('as-found pair (six sweeps + nearest cell): posA and velA byte-identical to the build before this change, self-gravity off and on', same(b1, mine) && mine.A.ticks === 100 && mine.B.ticks === 100);
  }

  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
