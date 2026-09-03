"use strict";
/* Two clumps in orbit, Save NPZ, OFF-equivalence, and the periodic-box growth rates.
   node bench_test.js                         the test build (rc-test.html, SwiftShader)
   BENCH_URL=http://127.0.0.1:8123/... PW_CHANNEL=chrome node bench_test.js   the served page in real Chrome
   OFF-equivalence runs when ../../_base/tests/halo/rc-test.html (a probe build of the page without this
   change) exists, or RC_BASELINE=<path> names one. Writes only under shots/ (git-ignored). */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const URL_ = process.env.BENCH_URL || ('file://' + path.resolve(__dirname, 'rc-test.html'));
const served = !!process.env.BENCH_URL;
const shots = path.join(__dirname, 'shots');
fs.mkdirSync(shots, { recursive: true });
const EXP = path.resolve(__dirname, '..', '..', 'experiments', 'halo');
const f3 = v => (typeof v === 'number' ? v.toFixed(3) : String(v));

async function launch() {
  if (process.env.PW_CHANNEL) return chromium.launch({ channel: process.env.PW_CHANNEL, headless: true });
  return chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
}

/* OFF-equivalence digest: seeded Math.random before load, re-seeded right before reseed() (three.js draws
   Math.random() for every object id), exactly 100 ticks of 1/20 s, then posA and velA hashed byte for byte. */
async function digest(browser, file, preset) {
  const ctx = await browser.newContext();
  const pg = await ctx.newPage({ viewport: { width: 800, height: 600 } });
  await pg.addInitScript(() => {
    let s = 424242;
    Math.random = () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    window.__seedRng = v => { s = v | 0; };
    window.__forceDt = 1e-7;
  });
  await pg.addInitScript(p => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify(p)); } catch (e) {} }, preset);
  await pg.goto('file://' + file);
  await pg.waitForSelector('.boot.done', { timeout: 120000 });
  // re-seed, reseed the swarm, then exactly 100 frames of 1/20 s (the page ticks once per frame; the
  // test's frame callback runs right after the page's), freeze, and hash in that same frame. The result
  // is parked on window and polled from node: one long page promise can be garbage-collected under load.
  await pg.evaluate(() => {
    const P = window.__probe; window.__offOut = null; window.__seedRng(0x9E3779B9); P.reseed(); const t0 = P.simTime; window.__forceDt = 1 / 20;
    let k = 0;
    const f = () => {
      if (++k < 100) { requestAnimationFrame(f); return; }
      window.__forceDt = 1e-7;
      const n = P.posA.width, out = { ticks: Math.round((P.simTime - t0) / P.TICK), step: P.step, n, sg: P.state.cosmos.selfgrav, particles: P.state.particles };
      for (const [key, t] of [['pos', P.posA], ['vel', P.velA]]) {
        const fl = new Float32Array(n * n * 4); P.renderer.readRenderTargetPixels(t, 0, 0, n, n, fl); const b = new Uint8Array(fl.buffer);   // renderer readback: present on every probe build
        let h1 = 0x811c9dc5, h2 = 0x01000193;
        for (let i = 0; i < b.length; i++) { h1 = Math.imul(h1 ^ b[i], 0x01000193); h2 = Math.imul(h2 ^ b[i], 0x01000193) + 7 | 0; }
        out[key] = (h1 >>> 0).toString(16) + (h2 >>> 0).toString(16); out[key + 'First'] = [fl[0], fl[1], fl[2]].map(v => +v.toFixed(4));
      }
      window.__offOut = out;
    };
    requestAnimationFrame(f);
  });
  let h = null;
  for (let i = 0; i < 3600 && !h; i++) { h = await pg.evaluate(() => window.__offOut); if (!h) await pg.waitForTimeout(50); }
  if (!h) throw new Error('100 frames took over 180 s');
  await ctx.close();
  return h;
}

(async () => {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 760 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });   // a root-absolute script tag cannot resolve under file://
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto(URL_);
  await page.waitForSelector('.boot.done', { timeout: 120000 });
  await page.waitForTimeout(1000);
  check('boot', true, URL_);
  await page.keyboard.press('7');
  await page.waitForTimeout(300);
  check('lab panel opens', await page.evaluate(() => !!document.querySelector('#panel-lab.open')));
  const probe = await page.evaluate(() => !!window.__probe);
  if (probe) await page.evaluate(() => { window.__forceDt = 1 / 20; });   // one tick per frame in the test build

  // ---- (c) Save NPZ in a state with self-gravity on (the spin experiment), then load it with numpy
  await page.click('#lab-exp-seg button[data-exp="spin"]');
  await page.waitForTimeout(2500);
  // #btn-npz sits in the Vessel & export panel (closed here): a programmatic click, as a user's would be after opening it
  const [dl] = await Promise.all([
    page.waitForEvent('download', { timeout: 20000 }).catch(() => null),
    page.evaluate(() => document.getElementById('btn-npz').click()),
  ]);
  await page.waitForTimeout(500);
  const npzStatus = (await page.textContent('#export-status')).trim();
  check('Save NPZ downloads resonance-chamber-snapshot.npz', !!dl && dl.suggestedFilename() === 'resonance-chamber-snapshot.npz', (dl && dl.suggestedFilename()) + ' | ' + npzStatus);
  check('Save NPZ says what it saved, in one plain sentence', /^Saved .* meta\.json\. Load it with numpy\.$/.test(npzStatus), npzStatus);
  let npzPath = null;
  if (dl) { npzPath = path.join(shots, 'bench-snapshot.npz'); await dl.saveAs(npzPath); }
  if (npzPath) {
    const r = spawnSync('python3', [path.join(EXP, 'load_chamber_npz.py'), npzPath], { encoding: 'utf8' });
    console.log((r.stdout || '').trim().split('\n').map(l => '    ' + l).join('\n'));
    if (r.stderr && r.stderr.trim()) console.log('    stderr: ' + r.stderr.trim().split('\n').slice(-3).join(' | '));
    let j = null;
    try { j = JSON.parse((r.stdout || '').trim().split('\n').pop()); } catch (e) {}
    check('numpy loads the NPZ: positions (N,3), velocities (N,3), density and potential (32,32,32), all finite', r.status === 0 && !!j && j.finite && j.shapes_ok, 'exit ' + r.status + ' ' + JSON.stringify(j && { particles: j.particles, finite: j.finite }));
    check('histogram density on the page\'s grid agrees with the exported density (r > 0.99)', !!j && j.correlation > 0.99, j && f3(j.correlation));
    check('meta.json carries the step, the time, the constants, the ceiling and the force formula', !!j && j.meta_ok, j && JSON.stringify(j.meta_keys));
  }
  const [dl2] = await Promise.all([
    page.waitForEvent('download', { timeout: 20000 }).catch(() => null),
    page.click('#btn-lab-npz'),
  ]);
  await page.waitForTimeout(300);
  check('the Lab panel has the same Save NPZ button', !!dl2 && dl2.suggestedFilename() === 'resonance-chamber-snapshot.npz', (await page.textContent('#lab-export-status')).trim());

  // ---- (a) the orbit experiment: ten seconds under six sweeps, ten under Exact, against the numpy twin
  const twinRun = spawnSync('python3', [path.join(EXP, 'orbit_twin.py'), '--json'], { encoding: 'utf8', timeout: 600000 });
  let twin = null;
  try { twin = JSON.parse((twinRun.stdout || '').trim().split('\n').pop()); } catch (e) {}
  console.log('  numpy twin: ' + (twin ? JSON.stringify({ Tpred: twin.Tpred, vcirc: twin.vcirc, Fr: twin.Fr, band: twin.band, exact: twin.phases.exact && { ratio: twin.phases.exact.ratio, drift: twin.phases.exact.drift, merge: twin.phases.exact.merge, jumps: twin.phases.exact.jumps }, jacobi: twin.phases.jacobi && { ratio: twin.phases.jacobi.ratio, merge: twin.phases.jacobi.merge } }) : 'did not run: ' + (twinRun.stderr || '').trim().split('\n').pop()));
  check('the numpy twin runs (experiments/halo/orbit_twin.py)', !!twin, 'exit ' + twinRun.status);
  await page.click('#lab-exp-seg button[data-exp="orbit"]');
  await page.waitForTimeout(300);
  const start = JSON.parse(await page.getAttribute('#orbit-group', 'data-result'));
  const t0 = Date.now();
  let res = start;
  while (!res.done && res.valid && Date.now() - t0 < 300000) {
    await page.waitForTimeout(500);
    res = JSON.parse(await page.getAttribute('#orbit-group', 'data-result'));
  }
  const st = await page.evaluate(() => ({ particles: window.__probe ? window.__probe.state.particles : null, lab: window.__probe ? window.__probe.state.lab.on : null,
    solver: window.__probe && window.__probe.state.pm ? window.__probe.state.pm.solver : null,
    cards: ['orbit-T-j', 'orbit-T-e', 'orbit-Tpred', 'orbit-ratio-j', 'orbit-ratio-e', 'orbit-band', 'orbit-drift-j', 'orbit-drift-e', 'orbit-merge', 'orbit-jumps', 'orbit-centre', 'orbit-time'].map(id => document.getElementById(id).textContent),
    pred: document.getElementById('orbit-pred').textContent.trim(), verdict: document.getElementById('orbit-verdict').textContent.trim(),
    hint: document.getElementById('lab-exp-hint').textContent.trim(), field: document.getElementById('val-field').textContent,
    visible: document.getElementById('orbit-group').style.display !== 'none',
    pressed: document.querySelector('#lab-exp-seg button[data-exp="orbit"]').getAttribute('aria-pressed') }));
  console.log('  start: ' + JSON.stringify({ Tpred: start.Tpred, vcirc: start.vcirc, Fr: start.Fr, FA: start.FA, FB: start.FB, band: start.band, jumpsPred: start.jumpsPred, residual: start.residual, modeCheck: start.modeCheck, weight: start.weight, total: start.total, phases: start.phases }));
  console.log('  end:   ' + JSON.stringify({ t: res.t, done: res.done, valid: res.valid, note: res.note, results: res.results }));
  console.log('  cards: ' + st.cards.join(' | '));
  console.log('  pred:  ' + st.pred);
  console.log('  verdict: ' + st.verdict);
  const J = res.results.jacobi || {}, E = res.results.exact || {};
  check('orbit: the group shows, the button is pressed, 1,024 particles, instruments off, field label says off', st.visible && st.pressed === 'true' && (st.particles === null || st.particles === 1024) && (st.lab === null || st.lab === false) && /off/.test(st.field), JSON.stringify({ visible: st.visible, pressed: st.pressed, particles: st.particles, lab: st.lab, field: st.field }));
  check('orbit: the page\'s exact solve checks out (residual < 1e-9, modes = grid)', start.residual < 1e-9 && start.modeCheck < 1e-9, JSON.stringify({ residual: start.residual, modeCheck: start.modeCheck }));
  check('orbit: prediction from the page\'s own DST-I: F = 14.58 on the clump at cell 20, v = 7.47, T = 3.218 s (the numpy oracle)', Math.abs(start.Fr - 14.582) < 0.01 && Math.abs(start.vcirc - 7.468) < 0.005 && Math.abs(start.Tpred - 3.218) < 0.003, JSON.stringify({ Fr: start.Fr, vcirc: start.vcirc, Tpred: start.Tpred }));
  if (twin) {
    check('orbit: the page\'s prediction matches the numpy twin (T_pred, v, F to 1e-3 relative; band to 0.01)', Math.abs(start.Tpred / twin.Tpred - 1) < 1e-3 && Math.abs(start.Fr / twin.Fr - 1) < 1e-3 && Math.abs(start.band[0] - twin.band[0]) < 0.01 && Math.abs(start.band[1] - twin.band[1]) < 0.01, JSON.stringify({ page: [start.Tpred, start.Fr, start.band], twin: [twin.Tpred, twin.Fr, twin.band] }));
  }
  check('orbit: both runs finished, valid, ten seconds each', res.done && res.valid && Math.abs(J.t - 10) < 1e-6 && (!res.hasPm || Math.abs(E.t - 10) < 1e-6), JSON.stringify({ done: res.done, valid: res.valid, note: res.note, tj: J.t, te: E.t }));
  check('orbit: the clumps stayed rigid (spread 0) and started 7.65 apart', J.spread === 0 && (!res.hasPm || E.spread === 0) && Math.abs(J.sep0 - 8 * 0.95625) < 1e-3, JSON.stringify({ spreadJ: J.spread, spreadE: E.spread, sep0: J.sep0 }));
  check('orbit, six sweeps: the pair merges within the run (the falsifier fires)', Number.isFinite(J.merge) && J.merge < 10, 'merge ' + J.merge + ' s, orbits ' + f3(J.orbits));
  if (twin && twin.phases.jacobi) check('orbit, six sweeps: the numpy twin merges too (same operator, same start)', Number.isFinite(twin.phases.jacobi.merge), 'twin merge ' + twin.phases.jacobi.merge + ' s, page ' + J.merge + ' s');
  if (res.hasPm) {
    check('orbit, exact: no merge in 10 s, more than two orbits', !Number.isFinite(E.merge) && E.orbits > 2, JSON.stringify({ merge: E.merge, orbits: E.orbits }));
    check('orbit, exact: the period sits inside the cell-jump band (ratio in [band] +- 0.02)', E.ratio >= start.band[0] - 0.02 && E.ratio <= start.band[1] + 0.02, JSON.stringify({ T: E.T, Tpred: start.Tpred, ratio: E.ratio, band: start.band }));
    check('orbit, exact: nothing on the force ceiling, drift under one cell per orbit', E.clamp === 0 && Math.abs(E.drift) < 0.95625, JSON.stringify({ clamp: E.clamp, drift: E.drift }));
    check('orbit, exact: cell jumps per tick near the expected 0.78 (0.39 cells per tick per clump)', Math.abs(E.jumps - start.jumpsPred) < 0.25, JSON.stringify({ jumps: E.jumps, expected: start.jumpsPred, ticks: E.ticks }));
    if (twin && twin.phases.exact) check('orbit, exact: the page and the numpy twin agree (ratio within 0.1, both no merge, jumps within 0.15)', Math.abs(E.ratio - twin.phases.exact.ratio) < 0.1 && !Number.isFinite(twin.phases.exact.merge) && Math.abs(E.jumps - twin.phases.exact.jumps) < 0.15, JSON.stringify({ page: [E.ratio, E.drift, E.jumps], twin: [twin.phases.exact.ratio, twin.phases.exact.drift, twin.phases.exact.jumps] }));
    check('orbit: the viewer\'s solver choice comes back at the end', st.solver === null || st.solver === 'jacobi', String(st.solver));
    check('orbit: the verdict names the solver as the cause', /trails the moving clumps/.test(st.verdict) && /kept orbiting/.test(st.verdict), st.verdict.slice(0, 120));
  }
  check('orbit: measured and predicted side by side on the cards (period, ratio, band, jumps expected)', st.cards[2].endsWith(' s') && /\d\.\d\d–\d\.\d\d/.test(st.cards[5]) && /expected/.test(st.cards[9]), st.cards.slice(0, 6).join(' | '));
  await page.screenshot({ path: path.join(shots, '90-bench-orbit.png') });

  // loading another experiment ends it cleanly
  await page.click('#lab-exp-seg button[data-exp="spin"]');
  await page.waitForTimeout(800);
  const after = JSON.parse(await page.getAttribute('#orbit-group', 'data-result'));
  check('orbit: loading another experiment leaves it stopped', !after.on, JSON.stringify({ on: after.on, done: after.done }));

  const real = errs.filter(e => !/SwiftShader|GroupMarker|fallback|deprecat|GPU stall|ERR_CONNECTION|fonts\.googleapis|favicon/i.test(e));
  check('no page errors', real.length === 0, real.slice(0, 3).join(' | '));
  await browser.close();

  // ---- (b) OFF-equivalence: a build without this change and this one, byte for byte after 100 seeded ticks
  const baseBuild = process.env.RC_BASELINE || path.resolve(__dirname, '../../_base/tests/halo/rc-test.html');
  if (!served && fs.existsSync(baseBuild)) {
    const br = await launch();
    const mine = path.resolve(__dirname, 'rc-test.html');
    const cases = [
      ['the saved default state (chladni, expansion, epochs, coupling)', { particles: 65536, quality: 0.5 }],
      ['self-gravity 0.3, coupling 0.4, expansion 0.3 (the mesh path runs every tick)', { particles: 65536, quality: 0.5, cosmos: { selfgrav: 0.3, mag: 0.4, hubble: 0.3 }, lorentz: 'euler' }],
    ];
    for (const [name, preset] of cases) {
      const a = await digest(br, baseBuild, preset), a2 = await digest(br, baseBuild, preset), b = await digest(br, mine, preset);
      console.log('  ' + name + ': base ' + a.pos + '/' + a.vel + ' (again ' + a2.pos + '/' + a2.vel + ') patched ' + b.pos + '/' + b.vel + ' ticks ' + [a.ticks, a2.ticks, b.ticks] + ' first ' + JSON.stringify(b.posFirst));
      check('OFF-equivalence, ' + name + ': the build without this change reproduces itself', a.pos === a2.pos && a.vel === a2.vel && a.ticks === 100, JSON.stringify({ ticks: [a.ticks, a2.ticks] }));
      check('OFF-equivalence, ' + name + ': patched == unpatched after 100 ticks (posA and velA byte-identical)', a.pos === b.pos && a.vel === b.vel && b.ticks === 100 && a.step === b.step, JSON.stringify({ base: [a.pos, a.vel], patched: [b.pos, b.vel], ticks: [a.ticks, b.ticks] }));
    }
    await br.close();
  } else console.log('  (OFF-equivalence needs a probe build of the page without this change at ../../_base/tests/halo/rc-test.html or RC_BASELINE=<path>; skipped)');

  // ---- (d) the periodic-box growth rates
  const jeans = path.join(EXP, 'jeans_dispersion.py');
  if (fs.existsSync(jeans)) {
    const r = spawnSync('python3', [jeans], { encoding: 'utf8', timeout: 900000 });
    console.log((r.stdout || '').trim().split('\n').map(l => '    ' + l).join('\n'));
    if (r.status !== 0) console.log('    stderr: ' + (r.stderr || '').trim().split('\n').slice(-5).join(' | '));
    let j = null;
    try { j = JSON.parse(fs.readFileSync(path.join(EXP, 'results', 'jeans_dispersion.json'), 'utf8')); } catch (e) {}
    const m1 = j && j.modes.find(x => x.m === 1);
    check('jeans_dispersion.py runs and writes results/jeans_dispersion.json', r.status === 0 && !!j, 'exit ' + r.status);
    check('jeans: m = 1 growth rate within 3% of the prediction', !!m1 && Math.abs(m1.ratio - 1) < 0.03, m1 && JSON.stringify({ meas: m1.omega_meas, pred: m1.omega_pred, ratio: m1.ratio }));
    check('jeans: every mode reproducible across seeds (spread < 1%) and the rates fall with m as both predictions say', !!j && j.modes.every(x => x.ratio_spread < 0.01) && j.modes.every((x, i, a) => i === 0 || x.omega_meas < a[i - 1].omega_meas), j && j.modes.map(x => x.m + ':' + x.ratio.toFixed(3) + '/' + x.ratio_cell.toFixed(3)).join(' '));
    check('jeans: the deposit of a per-cell displacement reads sin k and of a smooth one 2 sin(k/2) (m = 8: 1.00 vs 1.41), so the per-cell prediction is the dynamics\' own', !!j && j.modes.every(x => Math.abs(x.flux_cell_measured - x.flux_cell) < 0.03 && Math.abs(x.flux_smooth_measured - x.flux_smooth) < 0.03), j && j.modes.map(x => x.m + ':' + x.flux_cell_measured.toFixed(3) + '/' + x.flux_smooth_measured.toFixed(3)).join(' '));
    const d8 = j && j.dense_check && j.dense_check.find(x => x.m === 8);
    check('jeans: at 64 particles per cell m = 8 reads the per-cell prediction within 2% (D = 0.5, not 0.71)', !!d8 && Math.abs(d8.ratio_cell - 1) < 0.02, d8 && JSON.stringify({ ratio_cell: d8.ratio_cell, ratio_smooth: d8.ratio }));
  }

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
