'use strict';
/* Substeps Auto and the phase-space volume meter, against Liouville's theorem.
   Regimes with a known volume rate (field off, gravity off, a swarm at rest):
   (a) damping 1, no coupling: -3.0/s;
   (b) damping 0, coupling 0.4, exact rotation: 0;
   (c) same under Euler, 1 substep: +ln(1 + 0.21^2)/0.05 = +0.863/s;
   (d) coupling 3 under Euler with Auto: Auto (4), +ln(1 + 0.394^2)/0.0125 = +11.53/s;
   (e) Auto picks 1 at coupling 0.4; the button follows the slider; 'auto' survives a preset;
   (f) OFF-equivalence against an unpatched build when ../../_base exists. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const num = s => parseFloat(String(s).replace(/[^-0-9.]/g, ''));

const base = () => ({
  particles: 65536, stepsPerSec: 0.02, smooth: true, fieldForm: 'wells',
  fieldExp: -400,   // 10^-400 = 0: the field is off, the swarm rests where it was seeded
  damping: 1, quality: 0.5, colorMode: 0, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'pi' }, offsetMode: 'auto', strideIndex: 51,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false,
              equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 0, epoch: false, epochLen: 45, mag: 0,
            twist: false, aniso: 0, helix: 0, cascade: 'out', selfgrav: 0, gainloss: 0 },
  sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true,
           level: 0.5, register: -1, pitchSpace: 'shepard' },
  vessel: { form: 'off', gain: 1.2, radius: 0.62, girth: 0.02 },
  guides: false, autoOrbit: false, substeps: 1, lorentz: 'euler', lab: { on: true },
});

const launch = () => chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });

(async () => {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 120000 });
  check('boot', true);
  const frames = n => page.evaluate(n => new Promise(r => { let k = 0; const f = () => { if (++k >= n) r(); else requestAnimationFrame(f); }; requestAnimationFrame(f); }), n);
  await page.evaluate(() => { window.__forceDt = 1 / 20; });   // one tick per frame

  // run a state for `secs` of chamber time and read the meter
  const run = async (s, secs) => {
    await page.evaluate(st => { const P = window.__probe; P.applyPreset({ state: st, step: 5 }); P.reseed(); }, s);
    await frames(Math.round(secs * 20) + 2);
    return page.evaluate(() => { const P = window.__probe, L = P.lab; return {
      vol: L.vol, pred: L.volPred, local: L.volLocal, scored: L.volScored, N: L.volN,
      txt: document.getElementById('lab-vol').textContent.trim(),
      ptxt: document.getElementById('lab-vol-pred').textContent.trim(),
      ntxt: document.getElementById('lab-vol-n').textContent.trim(),
      stxt: document.getElementById('lab-vol-sub').textContent.trim(),
      lambda: L.lambda, sub: P.state.substeps, eff: P.effectiveSubsteps(),
      auto: document.querySelector('#substep-seg [data-sub="auto"]').textContent,
      prev: !!P.posPrev, usesPrev: !!P.posPrev && P.pointsMat.uniforms.posPrevTex.value === P.posPrev.texture,
      usesB: P.pointsMat.uniforms.posPrevTex.value === P.posB.texture }; });
  };
  const within = (v, target, tol) => Number.isFinite(v) && Math.abs(v - target) <= tol;

  // (a) damping only: -3 gamma
  const a = await run(base(), 12);
  console.log('  (a)', JSON.stringify(a));
  check('(a) damping 1, no coupling: measured -3.0/s within 10%', within(a.vol, -3.0, 0.3), a.vol);
  check('(a) predicted reads -3.000 /s', a.ptxt === '-3.000 /s', a.ptxt);
  check('(a) readout shows measured beside predicted', /\/s$/.test(a.txt) && /\/s$/.test(a.ptxt), a.txt + ' | ' + a.ptxt);
  check('(a) all 64 clusters scored', a.scored === 64 && a.N === 64 && a.ntxt === '64 of 64', a.ntxt);
  check('(a) substeps readout shows the count that ran', a.stxt === '1', a.stxt);
  check('(a) the twins still score (lambda finite)', Number.isFinite(a.lambda), a.lambda);

  // (b) frictionless exact rotation: 0
  const b = Object.assign(base(), { damping: 0, lorentz: 'boris' }); b.cosmos.mag = 0.4;
  const rb = await run(b, 12);
  console.log('  (b)', JSON.stringify(rb));
  check('(b) damping 0, coupling 0.4, exact rotation: |rate| <= 0.05/s', within(rb.vol, 0, 0.05), rb.vol);
  check('(b) predicted 0', rb.ptxt === '0.000 /s' || rb.ptxt === '-0.000 /s', rb.ptxt);

  // (c) frictionless Euler kick, one substep: +ln(1 + theta^2)/dt, theta = 0.4 * 10.5 * 0.05
  const c = Object.assign(base(), { damping: 0, lorentz: 'euler' }); c.cosmos.mag = 0.4;
  const rc = await run(c, 12);
  const th1 = 0.4 * 10.5 * 0.05, predC = Math.log(1 + th1 * th1) / 0.05;   // 0.863
  console.log('  (c)', JSON.stringify(rc), 'expected', predC.toFixed(4));
  check('(c) Euler kick at coupling 0.4, 1 substep: +0.86/s within 20%', within(rc.vol, predC, 0.2 * predC), rc.vol);
  check('(c) predicted matches the formula', within(rc.pred, predC, 1e-6), rc.pred);
  check('(c) measured and predicted agree within 5%', Math.abs(rc.vol - rc.pred) <= 0.05 * Math.abs(rc.pred), (rc.vol - rc.pred).toFixed(4));

  // (d) coupling 3 under Euler with Auto: four substeps, +ln(1 + theta^2)/(dt/4)
  const d = Object.assign(base(), { damping: 0, lorentz: 'euler', substeps: 'auto' }); d.cosmos.mag = 3;
  const rd = await run(d, 12);
  const th4 = 3 * 10.5 * 0.0125, predD = Math.log(1 + th4 * th4) / 0.0125;   // 11.53
  console.log('  (d)', JSON.stringify(rd), 'expected', predD.toFixed(4));
  check('(d) Auto at coupling 3 reads Auto (4) and runs 4 substeps', rd.auto === 'Auto (4)' && rd.sub === 'auto' && rd.eff === 4, rd.auto + ' ' + rd.eff);
  check('(d) rate +11.5/s within 20%', within(rd.vol, 11.5, 2.3), rd.vol);
  check('(d) predicted matches the formula', within(rd.pred, predD, 1e-6), rd.pred);
  check('(d) substeps readout says 4 (auto)', rd.stxt === '4 (auto)', rd.stxt);
  check('(d) Auto at 4 keeps a tick-start copy the renderer reads', rd.prev && rd.usesPrev, JSON.stringify({ prev: rd.prev, usesPrev: rd.usesPrev }));
  check('(d) Auto button pressed', (await page.getAttribute('#substep-seg [data-sub="auto"]', 'aria-pressed')) === 'true');

  // (e) Auto picks 1 at coupling 0.4, frees the copy; the slider relabels; 'auto' survives storage and a preset
  const e = Object.assign(base(), { damping: 0.5, lorentz: 'euler', substeps: 'auto' }); e.cosmos.mag = 0.4;
  const re = await run(e, 1);
  console.log('  (e)', JSON.stringify(re));
  check('(e) Auto at coupling 0.4 reads Auto (1) and runs 1 substep', re.auto === 'Auto (1)' && re.eff === 1, re.auto + ' ' + re.eff);
  check('(e) one effective substep uses the ping-pong partner and frees the copy', !re.prev && re.usesB, JSON.stringify({ prev: re.prev, usesB: re.usesB }));
  const table = await page.evaluate(() => [0, 0.4, 0.5, 0.6, 1, 2, 3].map(m => window.__probe.autoSubsteps(m)));
  check('(e) n = clamp(ceil(mag*10.5/20/0.25), 1, 4) at 0, 0.4, 0.5, 0.6, 1, 2, 3', JSON.stringify(table) === '[1,1,2,2,3,4,4]', JSON.stringify(table));
  await page.evaluate(() => { const el = document.getElementById('in-mag'); el.value = '3'; el.dispatchEvent(new Event('input', { bubbles: true })); });
  await frames(3);
  const relabel = await page.evaluate(() => ({ t: document.querySelector('#substep-seg [data-sub="auto"]').textContent, eff: window.__probe.effectiveSubsteps(), mag: window.__probe.state.cosmos.mag }));
  check('(e) moving the coupling slider to 3 relabels the button Auto (4)', relabel.t === 'Auto (4)' && relabel.eff === 4, JSON.stringify(relabel));
  await page.evaluate(() => document.querySelector('#substep-seg [data-sub="2"]').click());
  await frames(2);
  await page.evaluate(() => document.querySelector('#substep-seg [data-sub="auto"]').click());
  await frames(2);
  await page.waitForTimeout(600);   // saveState is debounced
  const persisted = await page.evaluate(() => ({ st: window.__probe.state.substeps, saved: JSON.parse(localStorage.getItem('resonance-chamber-v2')).substeps,
    pressed: document.querySelector('#substep-seg [data-sub="auto"]').getAttribute('aria-pressed'),
    two: document.querySelector('#substep-seg [data-sub="2"]').getAttribute('aria-pressed') }));
  check("(e) clicking Auto sets state 'auto', presses it alone, and stores 'auto'", persisted.st === 'auto' && persisted.saved === 'auto' && persisted.pressed === 'true' && persisted.two === 'false', JSON.stringify(persisted));
  const roundtrip = await page.evaluate(() => { const P = window.__probe; const s = JSON.parse(JSON.stringify(P.state)); P.applyPreset({ state: s, step: 5 }); return P.state.substeps; });
  check("(e) a preset captures 'auto' and brings it back", roundtrip === 'auto', roundtrip);
  const sanitized = await page.evaluate(() => { const P = window.__probe; const s = JSON.parse(JSON.stringify(P.state)); s.substeps = 'bogus'; P.applyPreset({ state: s, step: 5 }); return P.state.substeps; });
  check('(e) an unknown substeps value sanitizes to 1', sanitized === 1, sanitized);

  // the log carries the meter: two new columns, numeric when the meter reads
  await page.evaluate(st => { const P = window.__probe; P.applyPreset({ state: st, step: 5 }); P.reseed(); }, base());
  await frames(70);
  const [dl] = await Promise.all([
    page.waitForEvent('download', { timeout: 15000 }).catch(() => null),
    page.evaluate(() => document.getElementById('btn-lab-export').click()),   // the panel is closed: a JS click
  ]);
  if (dl) {
    const csv = fs.readFileSync(await dl.path(), 'utf8').trim().split('\n');
    const head = csv[0].split(','), last = csv[csv.length - 1].split(',');
    check('csv header ends substeps,vol_rate,vol_pred', head.slice(-3).join(',') === 'substeps,vol_rate,vol_pred', head.slice(-3).join(','));
    check('csv rows carry the meter (last row numeric, near -3)', last.length === head.length && within(parseFloat(last[head.length - 2]), -3, 0.3) && parseFloat(last[head.length - 1]) === -3, last.slice(-3).join(','));
  } else check('csv export produced a download', false);

  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  await browser.close();

  // (f) OFF-equivalence: seeded RNG, 100 fixed ticks, instruments off, substeps as found -> identical textures
  const baseBuild = path.resolve(__dirname, '../../_base/tests/halo/rc-test.html');
  if (fs.existsSync(baseBuild)) {
    // Seeded RNG with a re-seed hook: three.js draws Math.random() for every object id, so a sibling
    // patch that adds a material would shift the seed before the swarm is seeded. Both builds re-seed and
    // reseed() right before the 100 ticks. The run is polled from node in short evaluates (a single long
    // page promise can be garbage-collected under load).
    const seed = () => { let s = 424242; Math.random = () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; window.__seedRng = v => { s = v | 0; }; window.__forceDt = 1e-7; };
    const digest = async file => {
      const br = await launch(); const pg = await br.newPage();
      await pg.addInitScript(seed);
      await pg.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5, cosmos: { selfgrav: 0.3, mag: 0.4 }, lorentz: 'euler' })); } catch (e) {} });
      await pg.goto('file://' + file); await pg.waitForSelector('.boot.done', { timeout: 120000 });
      // count the ticks IN the page: the page's frame runs first in each animation-frame batch (it was
      // registered earlier), this callback runs after it, and freezes the clock the frame the 100th tick lands
      await pg.evaluate(() => { const P = window.__probe; window.__seedRng(0x9E3779B9); P.reseed(); window.__offT0 = P.simTime; window.__offDone = false; window.__forceDt = 1 / 20;
        const f = () => { if (P.simTime - window.__offT0 >= 100 * P.TICK - 1e-9) { window.__forceDt = 1e-7; window.__offDone = true; return; } requestAnimationFrame(f); };
        requestAnimationFrame(f); });
      for (let i = 0; i < 1200; i++) { if (await pg.evaluate(() => window.__offDone)) break; await pg.waitForTimeout(50); }
      const h = await pg.evaluate(() => { const P = window.__probe; window.__forceDt = 1e-7;
        const n = P.posA.width;
        const rd = (t) => { const o = new Float32Array(n * n * 4); P.renderer.readRenderTargetPixels(t, 0, 0, n, n, o); return o; };
        const a = rd(P.posA), b = rd(P.velA); let s1 = 0, s2 = 0;
        for (let i = 0; i < a.length; i++) { s1 = (s1 * 31 + (a[i] * 1e6 | 0)) | 0; s2 = (s2 * 31 + (b[i] * 1e6 | 0)) | 0; }
        return { ticks: Math.round((P.simTime - window.__offT0) / P.TICK), step: P.step, pos: s1, vel: s2, n, sub: P.state.substeps, lab: P.state.lab.on }; });
      await br.close(); return h;
    };
    const u = await digest(baseBuild), p = await digest(path.resolve(__dirname, 'rc-test.html'));
    check('(f) OFF-equivalence: unpatched and patched builds give identical posA/velA at 100 ticks', u.pos === p.pos && u.vel === p.vel && u.step === p.step && u.ticks === p.ticks && u.ticks === 100, JSON.stringify({ base: u, patched: p }));
  } else console.log('skip (f): no ../../_base build to compare against');

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
