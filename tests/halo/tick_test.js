'use strict';
/* Fixed-tick, interpolation, Boris toggle, float deposit: boot-level checks. */
const { chromium } = require('playwright');
const path = require('path');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  check('boot', true);
  const frames = n => page.evaluate(n => new Promise(r => { let k = 0; const f = () => { if (++k >= n) r(); else requestAnimationFrame(f); }; requestAnimationFrame(f); }), n);

  // natural ticking
  const t0 = await page.evaluate(() => window.__probe.simTime);
  await frames(10);
  const t1 = await page.evaluate(() => window.__probe.simTime);
  check('sim time advances in ticks of 1/20', t1 > t0 && Math.abs(((t1 - t0) / 0.05) - Math.round((t1 - t0) / 0.05)) < 1e-6, (t1 - t0).toFixed(3));

  // a 60 Hz machine: 120 frames -> 2.0 s of simulation
  await page.evaluate(() => { window.__forceDt = 1 / 60; });
  await frames(2);
  const a0 = await page.evaluate(() => window.__probe.simTime);
  const lerps = [];
  for (let i = 0; i < 24; i++) { await frames(1); lerps.push(await page.evaluate(() => window.__probe.pointsMat.uniforms.uLerp.value)); }
  await frames(120 - 24);
  const a1 = await page.evaluate(() => window.__probe.simTime);
  check('60 Hz: 120 frames advance 2.0 s (+-2 ticks: accumulator phase and read timing)', Math.abs((a1 - a0) - 2.0) <= 0.101, (a1 - a0).toFixed(3));
  check('60 Hz: renderer interpolates between ticks', lerps.some(v => v > 0.2 && v < 0.8), lerps.map(v => v.toFixed(2)).join(' '));

  // a 25 Hz machine: sim keeps level with the clock (two ticks on some frames)
  await page.evaluate(() => { window.__forceDt = 0.04; });
  await frames(2);
  const b0 = await page.evaluate(() => window.__probe.simTime);
  await frames(50);
  const b1 = await page.evaluate(() => window.__probe.simTime);
  check('25 Hz: 50 frames advance 2.0 s (+-2 ticks)', Math.abs((b1 - b0) - 2.0) <= 0.101, (b1 - b0).toFixed(3));

  // a slow machine: one tick per frame, sim time falls behind rather than spiralling
  await page.evaluate(() => { window.__forceDt = 0.3; });
  await frames(2);
  const c0 = await page.evaluate(() => window.__probe.simTime);
  await frames(10);
  const c1 = await page.evaluate(() => window.__probe.simTime);
  check('slow frames: 10 frames advance exactly 0.5 s', Math.abs((c1 - c0) - 0.5) < 1e-6, (c1 - c0).toFixed(3));
  await page.evaluate(() => { window.__forceDt = 1 / 60; });

  // substeps 4 -> dedicated tick-start texture
  await page.evaluate(() => document.querySelector('#substep-seg [data-sub="4"]').click());
  await frames(8);
  const sub = await page.evaluate(() => { const P = window.__probe; return { s: P.state.substeps, prev: !!P.posPrev, w: P.posPrev && P.posPrev.width, ts: P.texSize, uses: P.pointsMat.uniforms.posPrevTex.value === (P.posPrev && P.posPrev.texture) }; });
  check('substeps 4 keeps a tick-start copy', sub.s === 4 && sub.prev && sub.w === sub.ts && sub.uses, JSON.stringify(sub));
  await page.evaluate(() => document.querySelector('#substep-seg [data-sub="1"]').click());
  await frames(8);
  const sub1 = await page.evaluate(() => { const P = window.__probe; return { prev: !!P.posPrev, uses: P.pointsMat.uniforms.posPrevTex.value === P.posB.texture }; });
  check('substeps 1 uses the ping-pong partner and frees the copy', !sub1.prev && sub1.uses, JSON.stringify(sub1));

  // Boris toggle
  await page.evaluate(() => document.querySelector('#lorentz-seg [data-lor="boris"]').click());
  await frames(3);
  await page.waitForTimeout(600);   // saveState is debounced
  const bor = await page.evaluate(() => { const P = window.__probe; return { st: P.state.lorentz, u: P.velMat.uniforms.uBoris.value, pressed: document.querySelector('#lorentz-seg [data-lor="boris"]').getAttribute('aria-pressed'), saved: JSON.parse(localStorage.getItem('resonance-chamber-v2')).lorentz }; });
  check('exact rotation selected, uniform and storage follow', bor.st === 'boris' && bor.u === 1 && bor.pressed === 'true' && bor.saved === 'boris', JSON.stringify(bor));
  await page.evaluate(() => document.querySelector('#lorentz-seg [data-lor="euler"]').click());

  // float deposit
  await page.evaluate(() => { const P = window.__probe; const s = JSON.parse(JSON.stringify(P.state)); s.cosmos.selfgrav = 0.3; P.applyPreset({ state: s, step: 3 }); });
  await frames(4);
  const dep = await page.evaluate(() => { const P = window.__probe; return { type: P.pmDens && P.pmDens.texture.type, F: THREE.FloatType }; });
  check('particle-mesh targets are full float where the GPU blends float', dep.type === dep.F, JSON.stringify(dep));

  // instruments come up with the new readouts
  await page.evaluate(() => document.querySelector('#sw-lab').click());
  await frames(2);
  await page.evaluate(() => { window.__forceDt = 0; });   // real clock again
  const tt = Date.now();
  let lam = '–', clamp = '–', pairs = '–';
  while (Date.now() - tt < 30000) {
    await page.waitForTimeout(500);
    [lam, clamp, pairs] = await page.evaluate(() => ['lab-lambda', 'lab-clamp', 'lab-pairs'].map(id => document.getElementById(id).textContent));
    if (/\/s/.test(lam) && /%/.test(clamp)) break;
  }
  check('lyapunov, ceiling share and scored/pairs readouts live', /\/s/.test(lam) && /%/.test(clamp) && /% of/.test(pairs), `${lam} | ${clamp} | ${pairs}`);
  check('two-back stat present', !!(await page.$('#lab-ret2')));
  await page.screenshot({ path: path.join(__dirname, 'shots', '81-tick-build.png') });
  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
