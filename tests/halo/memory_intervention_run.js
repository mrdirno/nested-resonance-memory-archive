'use strict';
/* memory_intervention_run.js — one run of the Ring 30 registered intervention.

   This is tests/halo/memory_prereg_run.js (sha256 e0bc8f6b…, the harness every qualified
   run was made with) plus one hook, kept in its own file so the qualified harness stays
   byte-pinned. Everything that drives the page, stops it on exact ticks and exports the
   32^3 density meshes is that file's code, unchanged; the hook adds stops between ticks,
   which the page's physics never sees.

   At every boundary k = 1..EPOCHS-1 the harness, after its usual (a) relic export at tick
   200k-1 and (b) stop at tick 200k, steps one tick at a time until the page's zoom-out of
   boundary k has fired (tick 200k + d_k, d_k = 0..9: the page's clock drifts), then:
     (d) the hook reads the particle state (posA, velA: 2048 x 2048 float32 RGBA) and the
         self-gravity solver's warm start (pmPot: the 256 x 128 potential atlas) through the
         page's own measurement bus (__probe.readTarget), flips IEEE sign bits on a Uint32
         view (no float arithmetic), and writes back ROW BY ROW through __probe.writeRow —
         the call the page's Lab uses to re-pair its twins. (A single full-height upload via
         renderer.copyTextureToTexture honours the destination's flipY, true on a three r128
         render target, and lands the rows upside down; one row at a time is immune.)
         Every word written is read back and compared;
     (e) one more tick, and the state that tick consumed (posB/velB after the page's
         ping-pong swap) must be the state the hook wrote.

   --iv=identity       read and write back unchanged: the re-qualification path
   --iv=invert_all     point inversion of the whole carried state: (p, v) -> (-p, -v) for every
                       particle, and the potential permuted with it, cell (x,y,z) ->
                       (31-x,31-y,31-z) — an exact symmetry of the chamber's equations
   --iv=invert_matter  the same inversion of the particles only; the solver's warm start (the
                       potential of the pre-zoom relic, never rescaled by the page) is left
   No random draw reaches the chamber (three.js object ids consume Math.random, which the
   chamber never reads after seeding). Lab twin and volume-meter rows are inverted in place
   with every other texel, so pairs stay paired. The run is refused before it starts unless
   the page is on the registered path (self-gravity solver 'jacobi', deposit 'ngp'; mode
   dimer, centres, vessel and overlays off), and every hook re-checks the solver path. The
   mesh is written as <tag>.mesh.f32.partial and renamed only after every receipt and every
   record check (no page error, the condition applied, the zoom-out schedule, 23 hook
   records) has passed. A run that fails writes <tag>.void-<n>.json instead (schema
   halo-memory-intervention-void/1, which the frozen loader and the manifest builder both
   skip) with the failure kind ('refused' - the page is not the registered instrument or the run
   is off the registered path, before the first tick - 'receipt', 'schedule', 'record' or
   'crash'), the page errors, the hook records so far and the last completed boundary; its
   .partial mesh stays behind. The consumption receipt compares the next tick's input with the
   written state word for word.

   usage: node memory_intervention_run.js --iv=MODE --out=DIR + every flag of memory_prereg_run.js
          (--out is required here: the base harness's default is the recorded grid's directory)

   Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

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
const OUT = arg('out', null);   // required: the base harness defaults to the recorded grid's directory
if (!OUT) { console.error('--out=DIR is required'); process.exit(2); }
const SW = process.argv.includes('--sw');
const PRESET = arg('preset', 'spinchladni');   // 'default', or any data-scn scenario the page ships
// The digit-sequence position the drive starts from. 9028 is what the recorded
// grid ran under for the scenario arms (it comes from the page's `spin` bench
// recipe, not from the scenario button, which leaves step at 0).
const STEP = parseInt(arg('step', '9028'), 10);
const TICK = 0.05;

// --- similarity-group overrides (ring 19) -------------------------------------
// The chamber's force is a sum of terms whose parameters enter at known powers:
//   F = amp*fscale*field  +  uHubble*p*uAniso  +  uHelix*6*(-p.z,0,p.x)
//       - uSelfGrav*SG_GAIN*g/(2*PM_CELL)  +  uMag*30*cross(v,B),   amp = 10^fieldExp
// so cutting the drive is a coordinate change, not a preset swap. Until now the only
// way to cut it from here was to name a different scenario, and the one the pilot used
// (goldstair against spinchladni) moved many other keys at the same time. Each flag
// below moves one coordinate and nothing else.
// null means "leave the preset's own value alone": a run given none of these flags
// takes the same code path and records the same tag as every run made before them.
const numOv = k => {
  const v = arg(k, null);
  if (v === null) return null;
  const f = parseFloat(v);
  if (!Number.isFinite(f)) { console.error(`--${k}= needs a finite number, got "${v}"`); process.exit(2); }
  return f;
};
// Two more coordinates the exact time-rescaled image needs (ring 19): the integrator
// substep count, because the rescaled run is the base run integrated at a different
// step, and the field's twist, because a turning drive advances its phase on raw
// simulation time (omega * simTime) and so cannot be rescaled by any other flag.
// Both are null by default and touch nothing when absent.
const intOv = (k, lo, hi) => {
  const v = numOv(k);
  if (v === null) return null;
  if (!Number.isInteger(v) || v < lo || v > hi) { console.error(`--${k}= needs an integer in ${lo}..${hi}, got "${v}"`); process.exit(2); }
  return v;
};
const OV = { fieldExp: numOv('fieldexp'), damping: numOv('damping'), stepsPerSec: numOv('sps'),
             hubble: numOv('hubble'), helix: numOv('helix'), aniso: numOv('aniso'), mag: numOv('mag'),
             substeps: intOv('substeps', 1, 4), twist: intOv('twist', 0, 1) };
const OV_ON = Object.entries(OV).filter(([, v]) => v !== null);
const OV_TAG = OV_ON.length ? '_' + OV_ON.map(([k, v]) => `${k}${v}`).join('_') : '';

// --- the intervention (ring 30) -------------------------------------------------
const IVS = { identity: { chans: [], pot: false }, invert_all: { chans: [0, 1, 2], pot: true },
              invert_matter: { chans: [0, 1, 2], pot: false } };
const IV = arg('iv', null);
if (!(IV in IVS)) { console.error(`--iv= must be one of ${Object.keys(IVS).join(', ')}, got "${IV}"`); process.exit(2); }
// A failed run leaves evidence: its kind decides whether the registered re-issue rule applies
// (only a 'crash' with no page error may be re-issued, once, with the identical command).
const fail = (kind, msg) => Object.assign(new Error(msg), { kind });
const VOID = { errs: [], ilog: [], last: null, browser: null };
if (EPOCH_LEN !== 10 || EPOCHS > 24) { console.error('the registered zoom-out schedule covers 10 s epochs, at most 24'); process.exit(2); }
// Replayed from the page's drifting clock (all 2,124 lab-log rows, 236 per run, of the nine Ring 29 runs):
// the zoom-out of boundary k fires d_k ticks after tick 200k.
const ZOOM_D = [null, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9];
const SIM_DIGEST = '40bfdb685f82902a02df2494462e3020fd82e11147d380d19580937668915f6b';
const PAGE_SHA256 = '1a15b987ad60e8b037621c3c97304833b93adc18c275104033f19a54b2bf8413';

const TAG = `${PRESET}_sg${SG}_gl${GL}_seed${SEED}_n${N}_e${EPOCHS}${OV_TAG}_iv${IV}`;

// Runs inside the page, between ticks (no tick can run during a page.evaluate).
const hookFn = ({ chans, pot, k }) => {
  const P = window.__probe, S = P.texSize, n = S * S, NN = P.PM.N, TX = P.PM.TX, W = NN * TX, H = NN * P.PM.TY;
  // a MurmurHash3-style word hash: unlike FNV-1a over 32-bit words it is not blind to an even
  // number of sign-bit flips, so an inverted texture's hash differs from the original's
  const wh = u => { let h = 0x9747b28c | 0;
    for (let i = 0; i < u.length; i++) { let k = Math.imul(u[i], 0xcc9e2d51); k = (k << 15) | (k >>> 17); k = Math.imul(k, 0x1b873593);
      h ^= k; h = (h << 13) | (h >>> 19); h = (Math.imul(h, 5) + 0xe6546b64) | 0; }
    return h >>> 0; };
  const t0 = performance.now();
  const out = { k, simTime: P.simTime, epochN: P.epochN, step: P.step };
  for (const T of [P.posA, P.velA, P.pmPot]) if (T.texture.type !== THREE.FloatType) { out.fault = 'not a float target'; return out; }
  if (P.state.pm.solver !== 'jacobi' || P.state.pm.assign !== 'ngp') { out.fault = `solver path ${P.state.pm.solver}/${P.state.pm.assign}, registered jacobi/ngp`; return out; }
  const rho0 = P.labReadDensity();                         // the deposit of the state as found
  const pos = P.readTarget(P.posA, 0, 0, S, S), vel = P.readTarget(P.velA, 0, 0, S, S);
  // moments in float64, summed in texel order: angular momentum L = sum r x v, R = sum r, V = sum v
  const moments = () => { const m = [0, 0, 0, 0, 0, 0, 0, 0, 0];
    for (let i = 0; i < n; i++) { const b = 4 * i, x = pos[b], y = pos[b + 1], z = pos[b + 2], u = vel[b], v = vel[b + 1], w = vel[b + 2];
      m[0] += y * w - z * v; m[1] += z * u - x * w; m[2] += x * v - y * u; m[3] += x; m[4] += y; m[5] += z; m[6] += u; m[7] += v; m[8] += w; }
    return m; };
  let nonfinite = 0;
  for (const f of [pos, vel]) for (let i = 0; i < n; i++) for (let c = 0; c < 3; c++) if (!Number.isFinite(f[4 * i + c])) nonfinite++;
  const before = moments();
  for (const [name, f] of [['posA', pos], ['velA', vel]]) {
    const u = new Uint32Array(f.buffer), pre = wh(u);
    let changed = 0;
    for (let i = 0; i < u.length; i += 4) for (const c of chans) { u[i + c] = (u[i + c] ^ 0x80000000) >>> 0; changed++; }
    for (let r = 0; r < S; r++) P.writeRow(P[name], r, f.subarray(r * S * 4, (r + 1) * S * 4), S);
    const b = new Uint32Array(P.readTarget(P[name], 0, 0, S, S).buffer);
    let mism = 0; for (let i = 0; i < u.length; i++) if (b[i] !== u[i]) mism++;
    out[name] = { pre, post: wh(u), words_changed: changed, mismatched_words: mism };
  }
  const after = moments();
  // the state written, kept (page memory only) until the next tick's consumption check reads it
  window.__ivWritten = { posA: new Uint32Array(pos.buffer), velA: new Uint32Array(vel.buffer) };
  const neg = !!chans.length;
  // a self-check of the CPU transform (the GPU state is pinned by the word-for-word read-back);
  // NaN-robust, so a non-finite texel is counted and reported rather than voiding the run
  const same = (a, b) => a === b || (Number.isNaN(a) && Number.isNaN(b));
  out.moments = { nonfinite, L_before: before.slice(0, 3), L_after: after.slice(0, 3), R_before: before.slice(3, 6), R_after: after.slice(3, 6),
                  V_before: before.slice(6), V_after: after.slice(6),
                  ok: [0, 1, 2].every(i => same(after[i], before[i])) && [3, 4, 5, 6, 7, 8].every(i => same(after[i], neg ? -before[i] : before[i])) };
  // the solver's warm start: permuted whole-texel with the particles (invert_all) or left as it is
  const src = new Uint32Array(P.readTarget(P.pmPot, 0, 0, W, H).buffer), L = NN - 1;
  const at = (x, y, z) => ((Math.floor(z / TX) * NN + y) * W + (z % TX) * NN + x) * 4;
  const dst = new Uint32Array(src.length);
  for (let z = 0; z < NN; z++) for (let y = 0; y < NN; y++) for (let x = 0; x < NN; x++) {
    const s = pot ? at(L - x, L - y, L - z) : at(x, y, z), d = at(x, y, z);
    for (let ch = 0; ch < 4; ch++) dst[d + ch] = src[s + ch];
  }
  const df = new Float32Array(dst.buffer);
  for (let r = 0; r < H; r++) P.writeRow(P.pmPot, r, df.subarray(r * W * 4, (r + 1) * W * 4), W);
  const bk = new Uint32Array(P.readTarget(P.pmPot, 0, 0, W, H).buffer);
  let pm = 0; for (let i = 0; i < dst.length; i++) if (bk[i] !== dst[i]) pm++;
  out.pmPot = { pre: wh(src), post: wh(dst), mismatched_words: pm };
  // density receipt: the deposit of the written state against the particle map applied to the
  // deposit as found (cell-edge rounding may move a few particles one cell)
  const rho1 = P.labReadDensity();
  let sad = 0, cells = 0;
  for (let z = 0; z < NN; z++) for (let y = 0; y < NN; y++) for (let x = 0; x < NN; x++) {
    const j = neg ? ((L - z) * NN + (L - y)) * NN + (L - x) : (z * NN + y) * NN + x;
    const d = Math.abs(rho1[j] - rho0[(z * NN + y) * NN + x]);
    if (d) { sad += d; cells++; }
  }
  out.density = { sum_abs_diff: sad, cells_differing: cells, particles_moved_est: Math.round(sad * 1024 / 2) };
  out.ms = Math.round(performance.now() - t0);
  return out;
};
const consumedFn = () => {
  const P = window.__probe, S = P.texSize;
  const wh = u => { let h = 0x9747b28c | 0;
    for (let i = 0; i < u.length; i++) { let k = Math.imul(u[i], 0xcc9e2d51); k = (k << 15) | (k >>> 17); k = Math.imul(k, 0x1b873593);
      h ^= k; h = (h << 13) | (h >>> 19); h = (Math.imul(h, 5) + 0xe6546b64) | 0; }
    return h >>> 0; };
  const W = window.__ivWritten || {};
  const cmp = (a, b) => { if (!b || a.length !== b.length) return -1; let m = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) m++; return m; };
  const pB = new Uint32Array(P.readTarget(P.posB, 0, 0, S, S).buffer), vB = new Uint32Array(P.readTarget(P.velB, 0, 0, S, S).buffer);
  const res = { posB_mismatched_words: cmp(pB, W.posA), velB_mismatched_words: cmp(vB, W.velA) };
  delete window.__ivWritten;
  return { ...res, posB: wh(pB), velB: wh(vB),
           simTime: P.simTime, epochN: P.epochN };
};
const checkHook = (h, k, n) => {
  const bad = [], inv = IVS[IV].chans.length > 0;
  if (h.fault) return [h.fault];
  if (h.epochN !== k) bad.push(`epoch counter ${h.epochN} at the hook`);
  if (h.zoom_ticks_stepped !== ZOOM_D[k]) bad.push(`zoom-out after ${h.zoom_ticks_stepped} ticks, registered ${ZOOM_D[k]}`);
  for (const nm of ['posA', 'velA']) {
    if (h[nm].mismatched_words) bad.push(`${nm} read back ${h[nm].mismatched_words} words differently`);
    if (h[nm].words_changed !== (inv ? 3 * n : 0)) bad.push(`${nm} ${h[nm].words_changed} words changed`);
    if (!inv && h[nm].pre !== h[nm].post) bad.push(`identity changed ${nm}`);
    if (inv && h[nm].pre === h[nm].post) bad.push(`the inversion left the ${nm} hash unchanged`);
  }
  if (h.pmPot.mismatched_words) bad.push('potential read back differently');
  if ((h.pmPot.pre !== h.pmPot.post) !== IVS[IV].pot) bad.push('potential moved where it should not, or not where it should');
  if (!h.moments.ok) bad.push('moments not conserved/negated bit for bit');
  // n/256: a real write fault moves a large share of the particles; cell-edge rounding moves
  // few, but the three central planes of the 32-cell grid are cell edges, so a thin sheet on
  // one of them can put ~1,500 particles within rounding of an edge at full count
  if (inv ? h.density.particles_moved_est > n / 256 : h.density.cells_differing) bad.push(`density receipt ${h.density.particles_moved_est}`);
  if (!h.consumed || h.consumed.posB_mismatched_words !== 0 || h.consumed.velB_mismatched_words !== 0 ||
      h.consumed.posB !== h.posA.post || h.consumed.velB !== h.velA.post || h.consumed.epochN !== k)
    bad.push('the next tick did not consume the written state word for word');
  return bad;
};

const SW_ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'];
const GPU_ARGS = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-gpu-sandbox', '--no-sandbox'];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: SW ? SW_ARGS : GPU_ARGS,
  });
  VOID.browser = browser;
  const errs = VOID.errs;
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  // printed as they arrive too, so a run killed before its record is written still shows them
  page.on('pageerror', e => { errs.push(String(e.message).slice(0, 300)); console.error('[pageerror] ' + String(e.message).slice(0, 300)); });
  page.on('console', m => { if (m.type() === 'error') { errs.push('console: ' + m.text().slice(0, 200)); console.error('[console error] ' + m.text().slice(0, 200)); } });
  await page.addInitScript(n => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: n, quality: 0.5 })); } catch (e) {}
  }, N);
  const IDENT = (() => { try { return JSON.parse(require('child_process').execFileSync('python3',
      [path.resolve(__dirname, '..', '..', 'experiments', 'halo', 'instrument_identity.py'), path.resolve(__dirname, 'rc-test.html')],
      { encoding: 'utf8' })); } catch (e) { return null; } })();
  if (!IDENT || IDENT.sim_digest !== SIM_DIGEST || IDENT.whole_file_sha256 !== PAGE_SHA256)
    throw fail('refused', 'the test page is not the registered instrument (sim_digest 40bfdb68, page 1a15b987)');
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 300000 });
  await page.waitForTimeout(800);
  // Any scenario the page itself ships can be the arm, not just Spinning Chladni.
  // 'default' means the page's own DEFAULTS and clicks nothing. Every other value
  // must name a real data-scn button, so a typo fails loudly here instead of
  // silently recording the boot state under another scenario's name.
  if (PRESET !== 'default') {
    const clicked = await page.evaluate(p => {
      const b = document.querySelector(`[data-scn="${p}"]`);
      if (!b) return false;
      b.click();
      return true;
    }, PRESET);
    if (!clicked) {
      console.error(`no scenario button [data-scn="${PRESET}"] on the page`);
      await browser.close();
      process.exit(2);
    }
    await page.waitForTimeout(500);
  }

  const applied = await page.evaluate(({ n, seed, sg, gl, budget, epochLen, preset, step, ov }) => {
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
    // One coordinate each, applied last so nothing above can overwrite them. What
    // applyPreset then clamps or ignores is visible in `applied`, which is read back
    // off the page's own state rather than echoed from these flags.
    if (ov.fieldExp !== null) st.fieldExp = ov.fieldExp;
    if (ov.damping !== null) st.damping = ov.damping;
    if (ov.stepsPerSec !== null) st.stepsPerSec = ov.stepsPerSec;
    for (const k of ['hubble', 'helix', 'aniso', 'mag']) if (ov[k] !== null) st.cosmos[k] = ov[k];
    if (ov.substeps !== null) st.substeps = ov.substeps;
    if (ov.twist !== null) st.cosmos.twist = ov.twist === 1;
    st.lab = { on: true };
    window.__simStop = 0;
    window.__tickBudget = budget;
    window.__forceDt = budget * 0.05;
    // The digit-sequence position is NOT the scenario's. Clicking a data-scn
    // button leaves P.step at 0; the 9028 the recorded grid ran under comes from
    // the page's `spin` bench recipe, which names it explicitly. Reading P.step
    // here instead looked like the tidy generalisation and silently moved the
    // drive to a different digit position: a four-epoch A/B at 1,048,576
    // particles produced different meshes. So the step stays explicit, defaults
    // to the value the grid used, and is a flag. pageStep records what the click
    // actually left behind, so the difference stays visible in every run record.
    const stepNow = preset === 'default' ? 0 : step;
    const stepAfterClick = P.step;          // read BEFORE applyPreset overwrites it
    P.applyPreset({ state: st, step: stepNow });
    P.reseed();
    return { scenarioStep: stepNow, pageStep: stepAfterClick, particles: P.state.particles, texSize: P.texSize, simTime: P.simTime,
             cosmos: JSON.parse(JSON.stringify(P.state.cosmos)),
             lorentz: P.state.lorentz, substeps: P.state.substeps,
             smooth: P.state.smooth, damping: P.state.damping,
             stepsPerSec: P.state.stepsPerSec, fieldExp: P.state.fieldExp,
             pm: JSON.parse(JSON.stringify(P.state.pm)), dimer_on: !!(P.state.dimer && P.state.dimer.on),
             centers_on: !!(P.state.centers && P.state.centers.on), vessel_form: P.state.vessel ? P.state.vessel.form : null,
             overlays_on: Object.keys(P.state.overlays || {}).filter(k => P.state.overlays[k]),
             caps: P.caps() };
  }, { n: N, seed: SEED, sg: SG, gl: GL, budget: BUDGET, epochLen: EPOCH_LEN, preset: PRESET, step: STEP, ov: OV });

  if (applied.pm.solver !== 'jacobi' || applied.pm.assign !== 'ngp' || applied.dimer_on || applied.centers_on ||
      applied.vessel_form !== 'off' || applied.overlays_on.length) {
    throw fail('refused', `not the registered path (${JSON.stringify({ pm: applied.pm, dimer: applied.dimer_on,
      centers: applied.centers_on, vessel: applied.vessel_form, overlays: applied.overlays_on })})`);
  }
  console.log(`[${TAG}] ${applied.particles} particles, tex ${applied.texSize}, ` +
              `${applied.caps.renderer.slice(0, 40)}, pmDens ${applied.caps.pmDensType}, ` +
              `float_blend ${applied.caps.float_blend}`);

  const meshPath = path.join(OUT, TAG + '.mesh.f32');
  const meshPart = meshPath + '.partial';
  const meshFd = fs.openSync(meshPart, 'w');
  const rows = [];
  const ilog = VOID.ilog;
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

    // (c) step one tick at a time until boundary k's zoom-out has fired; (d) the hook;
    // (e) one more tick and the consumption receipt
    if (k < EPOCHS) {
      let stepped = 0;
      while (await page.evaluate(() => window.__probe.epochN) < k) {
        if (++stepped > 20) throw fail('schedule', `boundary ${k}: no zoom-out within 20 ticks`);
        await page.evaluate(() => { window.__simStop = window.__probe.simTime + window.__probe.TICK / 2; });
        await page.waitForFunction(() => window.__probe.simTime >= window.__simStop - 1e-9, null, { timeout: 600000, polling: 20 });
      }
      const h = await page.evaluate(hookFn, { chans: IVS[IV].chans, pot: IVS[IV].pot, k });
      h.zoom_ticks_stepped = stepped;
      await page.evaluate(() => { window.__simStop = window.__probe.simTime + window.__probe.TICK / 2; });
      await page.waitForFunction(() => window.__probe.simTime >= window.__simStop - 1e-9, null, { timeout: 600000, polling: 20 });
      h.consumed = await page.evaluate(consumedFn);
      ilog.push(h);
      const bad = checkHook(h, k, N);
      if (bad.length) throw fail('receipt', `boundary ${k}: ${bad.join('; ')}`);
    }
    VOID.last = { k, simTime: r.simTime, epochN: r.epochN };
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
  // The header comes from the page, never from a copy in this file. A copy is what
  // froze at 22 names when ring 13 widened the row to 28: every run recorded after
  // that published six unnamed columns, with 'substeps' naming a conservation value.
  const pageHead = await page.evaluate(() => window.__probe.LAB_LOG_HEAD || null);
  const csvCols = log.length ? log[0].split(',').length : 0;
  const csvHead = pageHead || '';
  if (csvHead && csvCols && csvHead.split(',').length !== csvCols) {
    throw new Error(`lab-log header names ${csvHead.split(',').length} columns but a row has ` +
                    `${csvCols}. Refusing to write a record whose header mislabels its own data.`);
  }
  if (!csvHead) console.warn('[warn] this page revision does not expose LAB_LOG_HEAD; csv_head is empty');
  // What made this run. Ring 17 spent seven controlled re-runs recovering one build
  // because no record named its instrument; ring 18 measured that a whole-file hash
  // over-reports (four page revisions, two behavioural classes) so the record pins the
  // BYTES and the REVISION, and experiments/halo/instrument_identity.py decides the
  // behavioural class from them. Schema stays halo-memory-prereg/1 on purpose: the
  // frozen scorer rejects any other string (memory_estimator_qualify.py:550) and it
  // must not be patched, so this is an added key, not a new schema.
  const sha256 = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
  const gitOut = a => { try { return require('child_process')
      .execFileSync('git', ['-C', path.resolve(__dirname, '..', '..')].concat(a),
                    { encoding: 'utf8' }).trim(); } catch (e) { return null; } };
  const instrument = {
    test_page: 'tests/halo/rc-test.html',
    test_page_sha256: sha256(path.resolve(__dirname, 'rc-test.html')),
    source_page: 'HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html',
    source_page_sha256: sha256(path.resolve(__dirname, '..', '..',
      'HELIOS-BRIDGE-ARCHIVE', 'HELIOS-V501-halo-resonance-chamber.html')),
    builder_sha256: sha256(path.resolve(__dirname, 'make_test_page.py')),
    harness: 'tests/halo/memory_intervention_run.js',
    harness_sha256: sha256(__filename),
    base_harness_sha256: sha256(path.resolve(__dirname, 'memory_prereg_run.js')),
    identity: IDENT,
    three_sha256: sha256(path.resolve(__dirname, 'three.min.js')),
    git_rev: gitOut(['rev-parse', 'HEAD']),
    git_dirty: (gitOut(['status', '--porcelain']) || '') !== '',
    playwright: require('playwright/package.json').version,
    browser: browser.version(),
    node: process.version,
  };
  const out = {
    tag: TAG, schema: 'halo-memory-prereg/1',
    params: { selfgrav: SG, gainloss: GL, seed: SEED, epochs: EPOCHS, particles: N,
              tick_budget: BUDGET, epoch_len: EPOCH_LEN, preset: PRESET,
              step: applied.scenarioStep,
              overrides: Object.fromEntries(OV_ON),
              backend: SW ? 'swiftshader' : 'gpu',
              intervention: { mode: IV, sign_flipped_channels: IVS[IV].chans, potential: IVS[IV].pot ? 'permuted with the particles' : 'left as it was',
                              boundaries: `1..${EPOCHS - 1}`, tick: 'right after the zoom-out tick of boundary k (200k + d_k)',
                              zoom_d_registered: ZOOM_D.slice(1, EPOCHS), lab_rows: 'transformed in place',
                              random: 'no random draw reaches the chamber (three.js object ids consume Math.random, which the chamber never reads after seeding)' } },
    applied, caps_end: capsEnd, mesh_file: path.basename(meshPath), mesh_n: 32, mesh_count: EPOCHS,
    csv_head: csvHead, csv_cols: csvCols, instrument,
    csv_rows: log, epochs: rows, intervention_log: ilog,
    wall_seconds: Math.round((Date.now() - wall0) / 1000), pageerrors: errs.slice(0, 10),
  };
  // the record checks, made here so that a record and a final-named mesh exist only for a run
  // that passed all of them (the grid re-checks every record as well)
  const rbad = [];
  if (errs.length) rbad.push(`${errs.length} page error(s)`);
  if (Math.abs(applied.cosmos.selfgrav - SG) > 1e-12 || applied.cosmos.gainloss !== GL) rbad.push('condition not applied');
  if (OV.fieldExp !== null && applied.fieldExp !== OV.fieldExp) rbad.push('fieldExp not applied');
  if (rows.some((r, i) => r.epochN !== (i + 1 <= 3 ? i + 1 : i))) rbad.push('zoom-out schedule differs');
  if (ilog.length !== EPOCHS - 1) rbad.push(`${ilog.length} hook records`);
  if (rbad.length) throw fail('record', rbad.join('; '));
  fs.writeFileSync(path.join(OUT, TAG + '.json'), JSON.stringify(out, null, 1));
  fs.renameSync(meshPart, meshPath);
  console.log(`[${TAG}] wrote ${TAG}.json + ${path.basename(meshPath)} ` +
              `(${EPOCHS} meshes, ${Math.round((Date.now() - wall0) / 1000)}s wall)`);
  await browser.close();
})().catch(async e => {
  console.error('crashed:', e);
  try {
    // repo-relative only: a void record is committed beside the runs, so no local path may leak
    const root = path.resolve(__dirname, '..', '..'), home = require('os').homedir();
    const clean = v => String(v).split(root).join('.').split(home).join('~').split('file://').join('');
    fs.mkdirSync(OUT, { recursive: true });
    let i = 1;
    while (fs.existsSync(path.join(OUT, `${TAG}.void-${i}.json`))) i++;
    fs.writeFileSync(path.join(OUT, `${TAG}.void-${i}.json`), JSON.stringify({
      schema: 'halo-memory-intervention-void/1', tag: TAG, mode: IV, attempt: i,
      kind: e && e.kind ? e.kind : 'crash', error: clean(e && e.message ? e.message : e).slice(0, 2000),
      pageerrors: VOID.errs.map(clean).slice(0, 20), last: VOID.last, intervention_log: VOID.ilog }, null, 1));
    console.error(`wrote ${TAG}.void-${i}.json`);
  } catch (w) { console.error('could not write the void record:', w); }
  try { if (VOID.browser) await VOID.browser.close(); } catch (w) {}
  process.exit(2);
});
