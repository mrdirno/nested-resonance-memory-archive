'use strict';
/* Do the instruments measure? Three regimes with known signs:
   (a) a settled figure (frozen mode, damping 2.5) must give lambda < 0;
   (b) a nearly frictionless bouncing swarm must give lambda > 0;
   (c) Spinning Chladni with epochs every 6 s must produce a memory index
       after the first zoom-out, and the spectrum must populate.
   Plus: substeps 3x runs without error, export downloads a csv (ring 10). */
const { chromium } = require('playwright');
const path = require('path');

const base = () => ({
  particles: 120000, stepsPerSec: 2, smooth: true, fieldForm: 'chladni',
  fieldExp: 0, damping: 2.5, quality: 0.5, colorMode: 0, base: 10,
  constants: { a: 'phi', b: 'phi', c: 'pi' }, offsetMode: 'auto', strideIndex: 51,
  overlays: { c3: false, c6: false, lattice: false, spiral: false, fifths: false,
              equal: false, trefoil: false, torus: false, hopf: false },
  centers: { on: false, count: 3, period: 24, gain: 1 },
  cosmos: { boundary: 'reflect', hubble: 0.3, epoch: false, epochLen: 45, mag: 0.6,
            twist: true, aniso: 0, helix: 0, cascade: 'out', selfgrav: 0, gainloss: 0 },
  sound: { voice: 'bridge', type: 'usim', omega: 0.7, omegaDigits: true,
           level: 0.5, register: -1, pitchSpace: 'shepard' },
  vessel: { form: 'off', gain: 1.2, radius: 0.62, girth: 0.02 },
  guides: false, autoOrbit: false, substeps: 1, lab: { on: true },
});

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 1100, height: 760 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.addInitScript(() => {
    try { localStorage.setItem('resonance-chamber-v2',
      JSON.stringify({ particles: 120000, quality: 0.5 })); } catch (e) {}
  });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  await page.waitForTimeout(1500);
  const fails = [];
  const check = (n, c, d) => { console.log((c ? 'ok: ' : 'FAIL: ') + n + (c ? '' : ' — ' + (d || ''))); if (!c) fails.push(n); };

  const run = async (s, secs) => {
    await page.evaluate(st => {
      window.__probe.applyPreset({ state: st, step: 5 });
      window.__probe.reseed();
      window.__t0 = window.__probe.simTime;
    }, s);
    const t0 = Date.now();
    for (;;) {
      const el = await page.evaluate(() => window.__probe.simTime - window.__t0);
      if (el >= secs || Date.now() - t0 > 240000) break;
      await page.waitForTimeout(1200);
    }
    return page.evaluate(() => ({
      lambda: document.getElementById('lab-lambda').textContent.trim(),
      mem: document.getElementById('lab-mem').textContent.trim(),
      ret: document.getElementById('lab-ret').textContent.trim(),
      epochs: document.getElementById('lab-epochs').textContent.trim(),
      lpre: document.getElementById('lab-lpre').textContent.trim(),
      lreal: document.getElementById('lab-lreal').textContent.trim(),
      pairs: document.getElementById('lab-pairs').textContent.trim(),
      ret2: document.getElementById('lab-ret2').textContent.trim(),
      clamp: document.getElementById('lab-clamp').textContent.trim(),
      fps: document.getElementById('ro-fps').textContent.trim(),
    }));
  };
  const num = s => parseFloat(String(s).replace(/[^-0-9.]/g, ''));

  // open the Lab panel so the readouts are live in the DOM
  await page.keyboard.press('7');
  await page.waitForTimeout(300);
  check('lab panel opens', await page.evaluate(() => !!document.querySelector('#panel-lab.open')));
  check('instruments switch present', !!(await page.$('#sw-lab')));

  // (a) a point attractor: wells, frozen mode, nothing else acting -> lambda < 0
  const a = Object.assign(base(), { fieldForm: 'wells', stepsPerSec: 0.02 });
  a.cosmos.hubble = 0; a.cosmos.mag = 0; a.cosmos.twist = false;
  const ra = await run(a, 16);
  console.log('  point attractor:', JSON.stringify(ra));
  check('point attractor: lambda finite', Number.isFinite(num(ra.lambda)), ra.lambda);
  check('point attractor: lambda < 0', num(ra.lambda) < 0, ra.lambda);
  // at field strength 1 the wells are overdamped (k < gamma^2/4), so a pair
  // contracts at -k/gamma, about -0.3/s, not at -gamma/2; measured -0.328
  check('point attractor: wall-free meter reads a real contraction (< -0.15/s)', num(ra.lambda) < -0.15, ra.lambda);
  check('point attractor: nothing on the force ceiling', num(ra.clamp) < 5, ra.clamp);
  check('pairs reported', num(ra.pairs) > 300, ra.pairs);
  check('spectrum populated (realized l)', Number.isFinite(num(ra.lreal)), ra.lreal);

  // (b) nearly frictionless bouncing gas: lambda > 0
  const b = Object.assign(base(), { damping: 0.3 });
  b.cosmos.hubble = 0; b.cosmos.mag = 0; b.cosmos.twist = false;
  const rb = await run(b, 16);
  console.log('  gas:', JSON.stringify(rb));
  check('bouncing gas: lambda > 0', num(rb.lambda) > 0, rb.lambda);

  // (c) Spinning Chladni with short epochs: memory after the first zoom-out
  const c = Object.assign(base(), { fieldExp: 2, damping: 1, stepsPerSec: 0.5,
    constants: { a: 'phi', b: 'phi', c: 'phi' }, strideIndex: 0, substeps: 2 });
  c.cosmos = Object.assign(c.cosmos, { hubble: 1.2, epoch: true, epochLen: 10, mag: 0.4,
    twist: true, aniso: 0.55, helix: 0.8, cascade: 'out', selfgrav: 0.3 });
  const rc = await run(c, 33);   // three zoom-outs at the 10 s floor: the two-back control needs the third
  console.log('  spinning+epochs+substeps2+selfgrav:', JSON.stringify(rc));
  check('memory index present after a zoom-out', Number.isFinite(num(rc.mem)), rc.mem);
  check('memory in range', num(rc.mem) >= -1 && num(rc.mem) <= 1, rc.mem);
  check('epochs counted', num(rc.epochs) >= 2, rc.epochs);
  check('retained memory recorded', Number.isFinite(num(rc.ret)), rc.ret);
  check('two-back control recorded after the third zoom-out', Number.isFinite(num(rc.ret2)), rc.ret2);
  check('two-back in range', num(rc.ret2) >= -1 && num(rc.ret2) <= 1, rc.ret2);
  check('force-ceiling share reported', /%/.test(rc.clamp), rc.clamp);
  check('scored share format', /\d+% of \d+/.test(rc.pairs.replace(/,/g, '')), rc.pairs);
  check('epochs counted three', num(rc.epochs) >= 3, rc.epochs);
  check('substeps 2x ran (fps readout live)', Number.isFinite(num(rc.fps)), rc.fps);
  await page.screenshot({ path: path.join(__dirname, 'shots', '82-lab-panel.png') });

  // export saves a real file in any browser (ring 10): a download event + a 'Saved N rows' status
  const [labDl] = await Promise.all([
    page.waitForEvent('download', { timeout: 15000 }).catch(() => null),
    page.click('#btn-lab-export'),
  ]);
  await page.waitForTimeout(800);
  const st = (await page.textContent('#lab-export-status')).trim();
  check('lab export downloads a csv', !!labDl && /\.csv$/.test(labDl.suggestedFilename()), labDl && labDl.suggestedFilename());
  check('lab export reports saved rows', /^Saved [\d,]+ rows\.$/.test(st), st);

  // instruments off leaves nothing running
  await page.click('#sw-lab');
  await page.waitForTimeout(300);
  check('instruments toggle off', (await page.getAttribute('#sw-lab', 'aria-pressed')) === 'false');

  const real = errs.filter(e => !/SwiftShader|GroupMarker|fallback|deprecat|GPU stall|ERR_CONNECTION|fonts.googleapis/i.test(e));
  check('no page errors', real.length === 0, real.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fails.length ? '\n' + fails.length + ' FAILURES' : '\nLAB TEST PASSED');
  process.exit(fails.length ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
