'use strict';
/* Author: Aldrin Payopay. GPL-3.0-only.
 * Ring 19: a scenario preset that names no camera must keep the viewer's framing.
 *
 * applyScenario() rebuilds state from DEFAULTS, then re-applies the settings that
 * "stay with the viewer" -- particles, quality, colorMode, guides, sacred, the mesh
 * choices (pm) and sound. Before the ring-19 fix the viewer's CAMERA was not on that
 * list, so the scenarios whose patch omits `cam` (formation, chladni, orbitals, magnet,
 * closed) reset state.cam to DEFAULTS. The visible az/el/dist survive one frame in the
 * live camera, but state.cam.user drops true->false, and once the framing is no longer
 * the user's it is refit on the next resize (chamber.html: resize -> fitDefaultView when
 * !cam.user) and no longer saved on reload (flushState saves cam only when cam.user).
 * A scenario that DOES carry a cam array (all the others) must still fly to it.
 *
 * state.cam only tracks the live camera inside flushState() and only while cam.user is
 * true, so a pagehide event is dispatched to force that sync deterministically before the
 * baseline is read -- no reliance on the debounced saveCamSoon timer.
 */
const { chromium } = require('playwright');
const path = require('path');
let pass = 0, fail = 0;
const check = (name, ok, info) => { if (ok) pass++; else fail++; console.log((ok ? 'PASS ' : 'FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); };
const near = (a, b, tol) => typeof a === 'number' && typeof b === 'number' && Math.abs(a - b) <= tol;

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 900, height: 640 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.waitForTimeout(600);
  check('boot', true);

  // The set of scenarios whose patch names no camera of its own, read from the page itself.
  // If the page adds or removes one, this audit fails, so the mechanism checks below cannot
  // silently test a stale list and a re-introduced no-cam scenario cannot slip past the gate.
  const EXPECTED_NO_CAM = ['closed', 'chladni', 'formation', 'magnet', 'orbitals'].sort();
  const audit = await page.evaluate(() => {
    const S = window.__probe.SCENARIOS || {};
    const keys = Object.keys(S);
    return {
      total: keys.length,
      noCam: keys.filter(k => !Array.isArray(S[k].cam)).sort(),
      withCam: keys.filter(k => Array.isArray(S[k].cam)).length,
      defCam: JSON.parse(JSON.stringify(window.__probe.DEFAULTS.cam)),
    };
  });
  check('page exposes SCENARIOS; DEFAULTS.cam.user is false (the silent reset target)',
    audit.defCam && audit.defCam.user === false, JSON.stringify(audit.defCam));
  check('exactly five of ' + audit.total + ' scenarios carry no camera (closed/chladni/formation/magnet/orbitals)',
    JSON.stringify(audit.noCam) === JSON.stringify(EXPECTED_NO_CAM), audit.noCam.join(','));

  // ---- direction 1: a no-camera scenario must PRESERVE the viewer's framing ----
  // Put the camera where a visitor chose, deterministically, through the probe's own hook,
  // then force state.cam to catch up to the live camera via flushState (pagehide).
  await page.evaluate(() => window.__probe.look(1.234, 0.321, 52));
  await page.waitForTimeout(120);
  await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
  const before = await page.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state.cam)));
  check("viewer camera set, marked as the user's, and synced into state",
    before.user === true && near(before.az, 1.234, 1e-3) && near(before.dist, 52, 1e-3), JSON.stringify(before));

  await page.evaluate(() => window.__probe.applyScenario('magnet'));   // magnet carries no cam of its own
  await page.waitForTimeout(500);
  const afterNoCam = await page.evaluate(() => ({
    cam: JSON.parse(JSON.stringify(window.__probe.state.cam)),
    centersOn: !!(window.__probe.state.centers && window.__probe.state.centers.on),
    form: window.__probe.state.fieldForm,
  }));
  check('the no-camera scenario actually applied (magnet turns emitter centers on)',
    afterNoCam.centersOn === true, JSON.stringify({ centersOn: afterNoCam.centersOn, form: afterNoCam.form }));
  check('a no-camera scenario keeps the viewer in control of the camera (user flag stays true)',
    afterNoCam.cam.user === true, JSON.stringify(afterNoCam.cam));
  check('a no-camera scenario keeps the viewer framing, not DEFAULTS (az/el/dist held)',
    near(afterNoCam.cam.az, before.az, 0.02) && near(afterNoCam.cam.el, before.el, 0.02) && near(afterNoCam.cam.dist, before.dist, 1),
    JSON.stringify(afterNoCam.cam) + ' vs ' + JSON.stringify(before));

  // ---- direction 2: a scenario that names a camera must still fly to it (guard the fix) ----
  await page.evaluate(() => window.__probe.look(2.4, 0.15, 61));
  await page.waitForTimeout(150);
  await page.evaluate(() => window.__probe.applyScenario('spinchladni'));   // spinchladni cam = [0.739, 0.708, 38.8]
  // flyTo animates (~900 ms nominal) but is frame-rate driven, so a fixed wait under-waits on a
  // slow runner (measured on ubuntu swiftshader: the fly was only ~55% done at 1300 ms, az 0.877
  // en route to 0.739). Poll until the animated camera has actually landed on its target, with a
  // generous ceiling; on a genuine no-arrival the ceiling lapses and the assertion below reports it.
  await page.waitForFunction(() => {
    const c = window.__probe && window.__probe.state && window.__probe.state.cam;
    return !!c && Math.abs(c.az - 0.739) <= 0.03 && Math.abs(c.dist - 38.8) <= 0.6;
  }, { timeout: 20000, polling: 100 }).catch(() => {});
  const afterCam = await page.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state.cam)));
  check('a camera-bearing scenario still flies to its own camera, not the preserved one',
    afterCam.user === true && near(afterCam.az, 0.739, 0.03) && near(afterCam.dist, 38.8, 0.6), JSON.stringify(afterCam));

  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log('\n' + pass + ' passed, ' + fail + ' failed');
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
