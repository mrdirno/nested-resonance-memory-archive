'use strict';
/* Author: Aldrin Payopay. GPL-3.0-only.
 * Ring 20: a PRESET that names no camera must keep the viewer's framing.
 *
 * Ring 19 fixed applyScenario and REPORTED a second live path with the identical
 * defect: applyPreset(), the chokepoint the Lab experiments (runLabExperiment) and
 * the From-text preset import both call. applyPreset rebuilds state from p.state, so
 * state.cam becomes p.state.cam; it restored the camera ONLY inside
 * `if (p.cam && Number.isFinite(+p.cam.az))`. runLabExperiment passes cam=null for the
 * four lab buttons whose base scenario carries no camera -- fieldonly, borisvseuler,
 * gravity (base 'default') and dimer (base 'chladni') -- and a hand-written From-text
 * preset can omit cam too. In those cases the viewer's state.cam dropped to the DEFAULTS
 * auto-fit sentinel {0.7854, 0.6155, 0, user:false}: az/el/dist survive a frame in the
 * live camera, but cam.user drops true->false, so the framing is refit on the next resize
 * (resize -> fitDefaultView when !cam.user) and no longer saved on reload (flushState
 * saves cam only when cam.user). The page's own invariant, now in applyScenario, is:
 * a wholesale reassignment that NAMES a camera flies to it; one that names NONE keeps the
 * viewer's framing. Ring 20 puts that invariant at the applyPreset chokepoint.
 *
 * This test covers the CLASS, not one instance: both real lab buttons (a no-cam base and
 * a cam-bearing base), the probe/From-text applyPreset path directly, and the two guards
 * a "preserve" fix could break -- a cam-bearing preset must still fly, and a viewer who
 * never took the camera (user:false) must NOT be falsely pinned to an auto-fit sentinel.
 *
 * state.cam only tracks the live camera inside flushState() and only while cam.user is
 * true, so a pagehide event is dispatched to force that sync deterministically wherever a
 * flown-to camera must be read back -- no reliance on the debounced saveCamSoon timer.
 *
 * Ring 23 pins the two instances Ring 20 left "covered by class, not pinned by instance"
 * for a later ring: (6) the `gravity` lab button BY NAME -- the field-off, energy-audit arm
 * of the base-'default' triad, covered by class via borisvseuler (same base) but never
 * clicked -- must itself preserve the viewer framing; and (7) a RELOAD-AND-RESTORE round
 * trip -- a preserved (cam.user) framing is persisted by flushState and comes back on the
 * next boot. The seed is now conditional (only-if-absent, the cam_check idiom) so a
 * persisted cam survives a reload instead of being clobbered; the never-orbited guard (8)
 * boots in a new browser context, whose storage starts empty, so it is always a fresh page.
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
  await page.addInitScript(() => { try { if (!localStorage.getItem('resonance-chamber-v2')) localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.waitForTimeout(600);
  check('boot', true);

  const audit = await page.evaluate(() => ({
    hasApplyPreset: typeof window.__probe.applyPreset === 'function',
    defCam: JSON.parse(JSON.stringify(window.__probe.DEFAULTS.cam)),
    buttons: Array.from(document.querySelectorAll('[data-exp]')).map(b => b.dataset.exp).sort(),
  }));
  check('page exposes applyPreset; DEFAULTS.cam.user is false (the silent reset target)',
    audit.hasApplyPreset && audit.defCam && audit.defCam.user === false, JSON.stringify(audit.defCam));
  check('the four no-camera lab buttons this ring names are all present',
    ['borisvseuler', 'dimer', 'fieldonly', 'gravity'].every(k => audit.buttons.includes(k)), audit.buttons.join(','));

  // Set the camera where a visitor chose, deterministically, then force state.cam to catch
  // up to the live camera via flushState (pagehide) before reading a baseline.
  const setViewer = async (az, el, dist) => {
    await page.evaluate(([a, e, d]) => window.__probe.look(a, e, d), [az, el, dist]);
    await page.waitForTimeout(120);
    await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
    return page.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state.cam)));
  };
  const camNow = () => page.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state.cam)));
  const flushed = async () => { await page.evaluate(() => window.dispatchEvent(new Event('pagehide'))); return camNow(); };

  // ---- direction 1: a no-camera LAB BUTTON must PRESERVE the viewer's framing (end to end) ----
  const b1 = await setViewer(1.234, 0.321, 52);
  check("viewer camera set, marked as the user's, synced into state (baseline)",
    b1.user === true && near(b1.az, 1.234, 1e-3) && near(b1.dist, 52, 1e-3), JSON.stringify(b1));
  await page.evaluate(() => document.querySelector('[data-exp="borisvseuler"]').click());   // base 'default' -> cam=null
  await page.waitForTimeout(400);
  const a1 = await camNow();
  check('borisvseuler (Boris vs Euler audit) kept the viewer in control of the camera (user stays true)',
    a1.user === true, JSON.stringify(a1));
  check('borisvseuler kept the viewer framing, not the DEFAULTS sentinel (az/el/dist held)',
    near(a1.az, b1.az, 0.02) && near(a1.el, b1.el, 0.02) && near(a1.dist, b1.dist, 1), JSON.stringify(a1) + ' vs ' + JSON.stringify(b1));

  // ---- direction 2: a SECOND no-camera lab button, a different base scenario ('chladni') ----
  const b2 = await setViewer(2.1, -0.24, 44);
  await page.evaluate(() => document.querySelector('[data-exp="dimer"]').click());   // base 'chladni' -> cam=null
  await page.waitForTimeout(400);
  const a2 = await camNow();
  check('dimer (encircle the exceptional point) also preserves the framing (a different no-cam base)',
    a2.user === true && near(a2.az, b2.az, 0.02) && near(a2.dist, b2.dist, 1), JSON.stringify(a2) + ' vs ' + JSON.stringify(b2));

  // ---- direction 3: the From-text / probe path -- applyPreset with NO cam, over a preset that
  //      even carries a bogus baked camera; the viewer's framing must win, not the preset's ----
  const b3 = await setViewer(0.9, 0.5, 30);
  await page.evaluate(() => {
    const st = JSON.parse(JSON.stringify(window.__probe.DEFAULTS));
    st.cam = { az: 9.9, el: 1.0, dist: 99, user: true };   // a saved-in preset camera the fix must NOT adopt when p.cam is absent
    window.__probe.applyPreset({ state: st, step: 0 });    // no p.cam -> the From-text-without-camera case
  });
  await page.waitForTimeout(200);
  const a3 = await camNow();
  check('applyPreset with no camera keeps the VIEWER framing, not the DEFAULTS sentinel and not the preset’s baked cam',
    a3.user === true && near(a3.az, b3.az, 0.02) && near(a3.dist, b3.dist, 1) && !near(a3.dist, 99, 1), JSON.stringify(a3) + ' vs ' + JSON.stringify(b3));

  // ---- direction 4 (guard): a preset that NAMES a camera must still fly to it ----
  await setViewer(2.4, 0.15, 61);
  await page.evaluate(() => {
    const st = JSON.parse(JSON.stringify(window.__probe.DEFAULTS));
    window.__probe.applyPreset({ state: st, step: 0, cam: { az: 0.6, el: 1.15, dist: 24 } });
  });
  await page.waitForTimeout(200);
  const a4 = await flushed();
  check('a camera-bearing preset still flies to its own camera, not the preserved one',
    a4.user === true && near(a4.az, 0.6, 0.03) && near(a4.dist, 24, 0.6), JSON.stringify(a4));

  // ---- direction 5 (guard): a cam-bearing LAB BUTTON (disc, base razordisc) still flies ----
  await setViewer(1.0, -0.3, 20);
  await page.evaluate(() => document.querySelector('[data-exp="disc"]').click());   // base razordisc cam=[0.6,1.3,34]
  await page.waitForTimeout(300);
  const a5 = await flushed();
  check('the disc lab button still flies to its scenario camera, not the viewer’s previous one',
    a5.user === true && near(a5.az, 0.6, 0.05) && near(a5.dist, 34, 1), JSON.stringify(a5));

  // ---- direction 6 (pin by instance): the `gravity` lab button, BY NAME. It is the field-off,
  //      energy-audit arm of the base-'default' triad; direction 1 drives that base via borisvseuler,
  //      so gravity is covered by CLASS but never clicked. Pin it: clicking gravity must itself keep
  //      the viewer framing, so stepping between the triad's members stays under one comparison frame. ----
  const bG = await setViewer(0.42, -0.11, 37);
  await page.evaluate(() => document.querySelector('[data-exp="gravity"]').click());   // base 'default' -> cam=null
  await page.waitForTimeout(400);
  const aG = await camNow();
  check('gravity (energy audit, field-off arm of base default) preserves the viewer framing by instance (user stays true, az/el/dist held)',
    aG.user === true && near(aG.az, bG.az, 0.02) && near(aG.el, bG.el, 0.02) && near(aG.dist, bG.dist, 1), JSON.stringify(aG) + ' vs ' + JSON.stringify(bG));

  // ---- direction 7 (round-trip): a PRESERVED viewer framing must survive a reload. flushState
  //      persists state.cam only while cam.user is true, and the page restores it on boot. Ring 20
  //      drove the preserve invariant but never reloaded to verify the framing comes back. Conditional
  //      seeding (above) leaves a persisted cam intact across the reload. ----
  const bR = await setViewer(1.111, 0.222, 47);
  const storedR = await page.evaluate(() => { try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).cam; } catch (e) { return null; } });
  check('flushState persisted the viewer framing into storage as the user’s (the save half of the round-trip)',
    !!storedR && storedR.user === true && near(storedR.az, 1.111, 1e-3) && near(storedR.dist, 47, 1e-3), JSON.stringify(storedR));
  await page.reload();
  await page.waitForSelector('.boot.done', { timeout: 90000 });
  await page.waitForTimeout(700);
  // Whether the SAVE survives a file:// reload is a browser/OS fact, not the page's: measured
  // 2026-09-09, a file:// reload preserves localStorage on macOS and did not on ubuntu-latest
  // (smoke.js names the same fact). Assert the RESTORE only where the store actually came back, so
  // a storage quirk cannot masquerade as a page regression; report the outcome either way.
  const survivedR = await page.evaluate(() => { try { const s = JSON.parse(localStorage.getItem('resonance-chamber-v2')); return !!(s && s.cam && s.cam.user); } catch (e) { return false; } });
  const aR = await camNow();
  if (!survivedR) {
    console.log('skip: preserved framing restore — the browser dropped file:// localStorage on this reload (storage quirk, not the page)');
    check('with the store dropped, the page boots fresh (cam.user=false), not a false restore', aR.user === false, JSON.stringify(aR));
  } else {
    check('after a reload the preserved framing is restored (user stays true, az/el/dist come back)',
      aR.user === true && near(aR.az, bR.az, 1e-3) && near(aR.el, bR.el, 1e-3) && near(aR.dist, bR.dist, 1e-3), JSON.stringify(aR) + ' vs ' + JSON.stringify(bR));
  }

  // ---- direction 8 (guard): a viewer who never took the camera must NOT be falsely preserved ----
  // A never-orbited viewer is a fresh browser profile, so this direction boots in a NEW browser
  // context, whose storage starts empty. It used to reset storage and reload the page above, which
  // raced: on ubuntu-latest a file:// reload once handed back the framing an earlier step had saved
  // (2026-09-23, "a fresh, never-orbited page boots with cam.user=false" failed; the re-run passed).
  // A no-cam lab button before any orbit must leave user=false, not pin an auto-fit sentinel as
  // "the user's".
  await page.close();
  const freshContext = await browser.newContext({ viewport: { width: 900, height: 640 } });
  const freshPage = await freshContext.newPage();
  freshPage.on('pageerror', e => errs.push(e.message));
  freshPage.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await freshPage.addInitScript(() => { try { if (!localStorage.getItem('resonance-chamber-v2')) localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await freshPage.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await freshPage.waitForSelector('.boot.done', { timeout: 90000 });
  await freshPage.waitForTimeout(500);
  const freshCam = () => freshPage.evaluate(() => JSON.parse(JSON.stringify(window.__probe.state.cam)));
  const fresh = await freshCam();
  check('a fresh, never-orbited page boots with cam.user=false', fresh.user === false, JSON.stringify(fresh));
  await freshPage.evaluate(() => document.querySelector('[data-exp="fieldonly"]').click());
  await freshPage.waitForTimeout(400);
  const a6 = await freshCam();
  check('a no-cam lab button on a never-orbited page leaves cam.user=false (no false preservation)',
    a6.user === false, JSON.stringify(a6));
  await freshContext.close();

  check('no console/page errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log('\n' + pass + ' passed, ' + fail + ' failed');
  await browser.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
