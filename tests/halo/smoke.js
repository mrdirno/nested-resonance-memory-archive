'use strict';
/* Headless smoke-drive of the Resonance Chamber: console errors, panels,
   vessels, scenarios, presets, sound toggle, screenshots. */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => {
    if (m.type() === 'error') errors.push('console: ' + m.text());
  });

  // small particle count + low quality so SwiftShader keeps up
  await page.addInitScript(() => {
    try {
      if (!localStorage.getItem('resonance-chamber-v2'))
        localStorage.setItem('resonance-chamber-v2',
          JSON.stringify({ particles: 20000, quality: 0.5 }));
    } catch (e) {}
  });

  const file = 'file://' + path.resolve(__dirname, 'rc-test.html');
  await page.goto(file);
  try {
    await page.waitForSelector('.boot.done', { timeout: 30000 });
  } catch (e) {
    console.log('BOOT FAILED; errors so far:', errors.slice(0, 6));
    console.log('boot text:', await page.textContent('#boot-inner').catch(() => '?'));
    throw e;
  }
  await page.waitForTimeout(2500);

  const shot = (name) => page.screenshot({ path: path.join(__dirname, 'shots', name) });
  const fails = [];
  const check = (name, cond, detail) => {
    if (cond) console.log('ok:', name);
    else { fails.push(name + (detail ? ' — ' + detail : '')); console.log('FAIL:', name, detail || ''); }
  };

  check('boot completed', true);
  check('particle readout populated',
    (await page.textContent('#ro-count')).trim() !== '–');

  // --- camera: auto-fit isometric default (1280x800: min axis vertical) ---
  const camText = async () => ({
    az: await page.textContent('#cam-az'),
    el: await page.textContent('#cam-el'),
    d: parseFloat(await page.textContent('#cam-d')),
  });
  let c0 = await camText();
  check('default az isometric 45deg', c0.az.trim() === '45\u00b0', c0.az);
  check('default el isometric ~35deg', /3[45]/.test(c0.el), c0.el);
  check('default dist fits sphere at 3/4 of min axis (~39.2)',
    Math.abs(c0.d - 39.2) < 1.2, String(c0.d));

  // first touch takes control and persists (drag, then reload)
  await page.mouse.move(640, 400);
  await page.mouse.down();
  await page.mouse.move(760, 340, { steps: 8 });
  await page.mouse.up();
  await page.mouse.wheel(0, -400);
  await page.waitForTimeout(2200);   // heartbeat save (0.5s) + debounces
  for (let i = 0; i < 20; i++) {     // wait until the inertia has settled (two equal reads)
    const p1 = await camText(); await page.waitForTimeout(500); const p2 = await camText();
    if (p1.az === p2.az && p1.el === p2.el && p1.d === p2.d) break;
  }
  await page.waitForTimeout(1500);   // storage commits are asynchronous in the browser
  const c1 = await camText();
  check('drag changed the camera', c1.az !== c0.az || Math.abs(c1.d - c0.d) > 0.5,
    JSON.stringify([c0, c1]));
  const storedCam = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).cam; }
    catch (e) { return null; }
  });
  check('camera pose stored with user flag', storedCam && storedCam.user === true,
    JSON.stringify(storedCam));
  await page.reload();
  await page.waitForSelector('.boot.done', { timeout: 30000 });
  await page.waitForTimeout(800);
  const c2 = await camText();
  check('camera persisted across reload (dist)',
    storedCam && Math.abs(c2.d - storedCam.dist) < 0.15,
    c2.d + ' vs stored ' + (storedCam && storedCam.dist));
  check('camera persisted across reload (az)',
    storedCam && Math.abs((parseFloat(c2.az) - (storedCam.az * 180 / Math.PI) % 360 + 540) % 360 - 180) < 1.5,
    c2.az + ' vs stored ' + (storedCam && (storedCam.az * 180 / Math.PI).toFixed(1)));

  // Reset view returns to auto framing
  await page.keyboard.press('5');
  await page.waitForTimeout(300);
  await page.click('#btn-cam-reset');
  await page.waitForTimeout(1100);
  const c3 = await camText();
  check('reset returns to fitted framing', Math.abs(c3.d - 39.2) < 1.2, String(c3.d));
  await page.keyboard.press('Escape');

  // default state: chladni, no centers (no vortexes) - read the live UI
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  const centersPressed = await page.getAttribute('#sw-centers', 'aria-pressed');
  await page.keyboard.press('Escape');
  await page.keyboard.press('1');
  await page.waitForTimeout(300);
  const chladniPressed = await page.getAttribute('#form-seg button[data-form="chladni"]', 'aria-pressed');
  await page.keyboard.press('Escape');
  const defaults = { centers: centersPressed, form: chladniPressed };
  await page.waitForTimeout(400);
  await shot('01-default-chladni.png');

  // panels 1..7 open
  for (const key of ['1', '2', '3', '4', '5', '6', '7']) {
    await page.keyboard.press(key);
    await page.waitForTimeout(250);
    const open = await page.evaluate(() =>
      !!document.querySelector('.panel.open'));
    check('panel ' + key + ' opens', open);
    await page.keyboard.press('Escape');
  }

  // Tools panel (key 8): the other pages in the archive, every link relative and in a new tab
  await page.keyboard.press('8');
  await page.waitForTimeout(300);
  const tools = await page.evaluate(() => {
    const p = document.getElementById('panel-tools');
    const links = p ? Array.from(p.querySelectorAll('a[href]')) : [];
    return {
      open: !!p && p.classList.contains('open') && getComputedStyle(p).visibility === 'visible',
      hrefs: links.map(a => a.getAttribute('href')),
      newTab: links.every(a => a.getAttribute('target') === '_blank' && /\bnoopener\b/.test(a.getAttribute('rel') || '')),
      titled: links.every(a => a.textContent.trim().length > 10),
    };
  });
  check('panel 8 (Tools) opens', tools.open);
  check('Tools panel lists at least 21 pages', tools.hrefs.length >= 21, String(tools.hrefs.length));
  check('every Tools link is a folder relative to the site root',
    tools.hrefs.length > 0 && tools.hrefs.every(h => h.startsWith('./') && h.endsWith('/')),
    tools.hrefs.filter(h => !(h.startsWith('./') && h.endsWith('/'))).join(' '));
  const trades = ['av', 'plumbing', 'electrical', 'hvac', 'low-voltage', 'gc', 'framing', 'roofing',
                  'creative', 'concrete', 'masonry', 'sitework', 'flooring', 'painting', 'doors', 'landscape'];
  const missingPages = ['archive/classic', 'archive', 'collage', 'collage-beta', 'commons', ...trades]
    .filter(s => !tools.hrefs.includes('./' + s + '/'));
  check('Tools panel links every sibling page and all 16 trades', missingPages.length === 0, missingPages.join(' '));
  check('every Tools link opens in a new tab (target _blank, rel noopener)', tools.newTab);
  check('every Tools card has a title and a sentence', tools.titled);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);
  check('Escape closes the Tools panel',
    await page.evaluate(() => !document.querySelector('.panel.open')));
  // the keyboard help names the new key
  await page.keyboard.press('i');
  await page.waitForTimeout(300);
  check('info dialog opens on I',
    await page.evaluate(() => document.getElementById('info-scrim').classList.contains('open')));
  const keyHelp = await page.textContent('#info-scrim .key-list');
  check('keyboard help lists 8 - Tools', /8/.test(keyHelp) && /Tools/.test(keyHelp),
    keyHelp.replace(/\s+/g, ' ').slice(0, 120));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // sound on: bridge + Shepard default; must not throw
  await page.click('#btn-audio');
  await page.waitForTimeout(800);
  check('audio toggled on',
    (await page.getAttribute('#btn-audio', 'aria-pressed')) === 'true');
  await page.keyboard.press('6');
  await page.waitForTimeout(300);
  const shepPressed = await page.getAttribute(
    '#space-seg button[data-space="shepard"]', 'aria-pressed');
  check('Shepard is the default pitch space', shepPressed === 'true');
  const rootLine = await page.textContent('#reg-root-line');
  await page.waitForTimeout(900);
  check('root readout live', /Hz/.test(await page.textContent('#reg-root-line')));
  await page.keyboard.press('Escape');

  // vessels: ring then vase, with screenshots after settling
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  await page.click('#vessel-seg button[data-vessel="ring"]');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(6000);
  await shot('02-vessel-ring.png');

  // ring parameter panel: radius + girth turn the thin ring into a torus tube
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  check('ring radius slider present', !!(await page.$('#in-vessel-radius')));
  check('ring girth slider present', !!(await page.$('#in-vessel-girth')));
  await page.evaluate(() => {
    const set = (id, v) => {
      const el = document.getElementById(id);
      el.value = v; el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    set('in-vessel-radius', '0.55');
    set('in-vessel-girth', '0.12');
  });
  await page.waitForTimeout(300);
  check('girth readout updates',
    (await page.textContent('#val-vessel-girth')).trim() === '0.12×R');
  check('radius readout updates',
    (await page.textContent('#val-vessel-radius')).trim() === '0.55×R');
  const vesselStored = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).vessel; }
    catch (e) { return null; }
  });
  check('ring params persisted',
    vesselStored && vesselStored.radius === 0.55 && vesselStored.girth === 0.12,
    JSON.stringify(vesselStored));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(7000);
  await shot('02b-vessel-ring-torus.png');

  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  await page.click('#vessel-seg button[data-vessel="vase"]');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(8000);
  await shot('03-vessel-vase.png');

  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  await page.click('#vessel-seg button[data-vessel="panel"]');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(6000);
  await shot('04-vessel-panel.png');

  // formation scenario: black-hole cores
  await page.keyboard.press('3');
  await page.waitForTimeout(200);
  await page.click('#vessel-seg button[data-vessel="off"]');
  await page.keyboard.press('1');
  await page.waitForTimeout(300);
  await page.click('#scenario-seg button[data-scn="formation"]');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(9000);
  await shot('05-formation-blackholes.png');

  // curated presets found by the search
  for (const [scn, wait, file] of [
      ['goldstair', 7000, '06-goldstair.png'],
      ['amphora', 8000, '07-amphora.png'],
      ['strobe', 5000, '08-strobe.png'],
      ['eventhorizon', 9000, '09-eventhorizon.png']]) {
    await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
    await page.keyboard.press('Escape');
    await page.keyboard.press('1');
    await page.waitForTimeout(300);
    const btn = await page.$('#scenario-seg2 button[data-scn="' + scn + '"]');
    check('preset button exists: ' + scn, !!btn);
    if (btn) {
      await btn.click();
      await page.waitForTimeout(300);
      const hint = await page.textContent('#scenario-hint');
      check('hint updates for ' + scn, hint.trim().length > 10, hint.slice(0, 60));
      await page.keyboard.press('Escape');
      await page.waitForTimeout(wait);
      await shot(file);
    }
  }

  // ringforge preset now ships a fat torus (girth 0.09)
  await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  await page.keyboard.press('Escape');
  await page.keyboard.press('1');
  await page.waitForTimeout(300);
  await page.click('#scenario-seg2 button[data-scn="ringforge"]');
  await page.waitForTimeout(400);
  await page.keyboard.press('Escape');
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  check('ringforge applies girth 0.09',
    (await page.textContent('#val-vessel-girth')).trim() === '0.09×R',
    await page.textContent('#val-vessel-girth'));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(8000);
  await shot('10b-ringforge-torus.png');

  // stair rework + new physics presets
  await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  await page.keyboard.press('Escape');
  await page.keyboard.press('1');
  await page.waitForTimeout(300);
  await page.click('#scenario-seg2 button[data-scn="goldstair"]');
  await page.waitForTimeout(400);
  await page.keyboard.press('Escape');
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  check('goldstair hides the geometry grid',
    (await page.getAttribute('#sw-guides', 'aria-pressed')) === 'false');
  await page.keyboard.press('Escape');
  await page.keyboard.press('4');
  await page.waitForTimeout(300);
  check('goldstair epoch length is 10 s',
    (await page.textContent('#val-epochlen')).trim() === '10 s');
  await page.keyboard.press('Escape');

  for (const [scn, wait, file] of [
      ['helix', 12000, '11-prismatic-helix.png'],
      ['cascade', 9000, '12-reverse-fractal.png']]) {
    await page.keyboard.press('1');
    await page.waitForTimeout(300);
    await page.click('#scenario-seg2 button[data-scn="' + scn + '"]');
    await page.waitForTimeout(300);
    check('hint updates for ' + scn,
      (await page.textContent('#scenario-hint')).trim().length > 10);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(wait);
    await shot(file);
  }
  await page.keyboard.press('4');
  await page.waitForTimeout(300);
  check('cascade preset selects Cascade in',
    (await page.getAttribute('#cascade-seg button[data-cascade="in"]', 'aria-pressed')) === 'true');
  const anisoShown = await page.textContent('#val-aniso');
  check('anisotropy slider reflects preset', anisoShown.trim() === '0.35', anisoShown);
  await page.keyboard.press('Escape');

  // second-wave row: every button present, applies, and updates the hint
  for (const scn of ['razordisc', 'knotmotor', 'pinwheel', 'hoopcatch',
                     'beadwork', 'rocker', 'conveyor']) {
    await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
    await page.keyboard.press('Escape');
    await page.keyboard.press('1');
    await page.waitForTimeout(250);
    const btn = await page.$('#scenario-seg3 button[data-scn="' + scn + '"]');
    check('wave-2 preset button: ' + scn, !!btn);
    if (btn) {
      await btn.click();
      await page.waitForTimeout(350);
      check('wave-2 hint for ' + scn,
        (await page.textContent('#scenario-hint')).trim().length > 20);
    }
    await page.keyboard.press('Escape');
  }
  // the Spinning Chladni family, including the user's own state
  for (const scn of ['spinchladni', 'hardprint', 'trueround',
                     'justarriving', 'stillspindle', 'spinexact']) {
    await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
    await page.keyboard.press('Escape');
    await page.keyboard.press('1');
    await page.waitForTimeout(250);
    const btn = await page.$('#scenario-seg4 button[data-scn="' + scn + '"]');
    check('family preset button: ' + scn, !!btn);
    if (btn) {
      await btn.click();
      await page.waitForTimeout(350);
      check('family hint for ' + scn,
        (await page.textContent('#scenario-hint')).trim().length > 20);
    }
    await page.keyboard.press('Escape');
  }
  // the two backreaction controls exist, apply, and persist
  await page.keyboard.press('4');
  await page.waitForTimeout(300);
  await page.evaluate(() => document.querySelector('[data-scn="spinexact"]').click());
  await page.waitForTimeout(400);
  const exact = await page.evaluate(() => ({ lor: window.__probe.state.lorentz, mag: window.__probe.state.cosmos.mag, u: window.__probe.velMat.uniforms.uBoris.value }));
  check('exact sibling selects the exact-rotation step at coupling 0.3', exact.lor === 'boris' && exact.mag === 0.3 && exact.u === 1, JSON.stringify(exact));
  check('self-gravity slider present', !!(await page.$('#in-selfgrav')));
  check('gain/loss slider present', !!(await page.$('#in-gainloss')));
  await page.evaluate(() => {
    const set = (id, v) => {
      const el = document.getElementById(id);
      el.value = v; el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    set('in-selfgrav', '0.45');
    set('in-gainloss', '0.35');
  });
  await page.waitForTimeout(450);
  check('self-gravity readout', (await page.textContent('#val-selfgrav')).trim() === '0.45×');
  check('gain/loss readout', /rate/.test(await page.textContent('#val-gainloss')));
  const cosStored = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).cosmos; }
    catch (e) { return null; }
  });
  check('backreaction settings persist',
    cosStored && cosStored.selfgrav === 0.45 && cosStored.gainloss === 0.35,
    JSON.stringify(cosStored));
  await page.waitForTimeout(3500);   // run with both on: must not throw
  await page.evaluate(() => {
    const set = (id, v) => {
      const el = document.getElementById(id);
      el.value = v; el.dispatchEvent(new Event('input', { bubbles: true }));
    };
    set('in-selfgrav', '0'); set('in-gainloss', '0');
  });
  await page.keyboard.press('Escape');

  // the Lab: substep seg applies + persists, instruments switch persists
  await page.keyboard.press('1');
  await page.waitForTimeout(250);
  await page.click('#substep-seg button[data-sub="2"]');
  await page.waitForTimeout(450);
  check('substeps 2x pressed',
    (await page.getAttribute('#substep-seg button[data-sub="2"]', 'aria-pressed')) === 'true');
  const subStored = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).substeps; }
    catch (e) { return null; }
  });
  check('substeps persisted', subStored === 2, String(subStored));
  await page.click('#substep-seg button[data-sub="1"]');
  // magnetic step: exact rotation selects, drives the uniform, persists
  await page.click('#lorentz-seg button[data-lor="boris"]');
  await page.waitForTimeout(450);
  check('exact-rotation step pressed',
    (await page.getAttribute('#lorentz-seg button[data-lor="boris"]', 'aria-pressed')) === 'true');
  const lorStored = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).lorentz; }
    catch (e) { return null; }
  });
  check('magnetic step persisted', lorStored === 'boris', String(lorStored));
  check('magnetic step uniform follows', (await page.evaluate(() => window.__probe.velMat.uniforms.uBoris.value)) === 1);
  await page.click('#lorentz-seg button[data-lor="euler"]');
  await page.waitForTimeout(100);
  check('euler step restored', (await page.evaluate(() => window.__probe.velMat.uniforms.uBoris.value)) === 0);
  await page.keyboard.press('Escape');
  await page.keyboard.press('7');
  await page.waitForTimeout(250);
  await page.click('#sw-lab');
  check('instruments on', (await page.getAttribute('#sw-lab', 'aria-pressed')) === 'true');
  let lamTxt = '';
  for (let i = 0; i < 160; i++) {          // the meter reports after ~1 s of SIM time (slow under load)
    await page.waitForTimeout(500);
    lamTxt = (await page.textContent('#lab-lambda')).trim();
    if (/\/s/.test(lamTxt)) break;
  }
  check('lyapunov readout live', /\/s/.test(lamTxt), lamTxt);
  const clampTxt = (await page.textContent('#lab-clamp')).trim();
  check('force-ceiling share readout live', /%/.test(clampTxt), clampTxt);
  check('scored share readout', /% of/.test((await page.textContent('#lab-pairs')).trim()));
  check('two-back memory stat present', !!(await page.$('#lab-ret2')));
  // experiments: one click loads the state, keeps the instruments on, writes the hint
  await page.click('#lab-exp-seg button[data-exp="disc"]');
  await page.waitForTimeout(600);
  const expState = await page.evaluate(() => ({ mag: window.__probe.state.cosmos.mag, lab: window.__probe.state.lab.on,
    hint: document.getElementById('lab-exp-hint').textContent, pressed: document.querySelector('#lab-exp-seg button[data-exp="disc"]').getAttribute('aria-pressed') }));
  check('experiment loads the Razor Disc with instruments on', expState.mag === 3 && expState.lab === true && expState.pressed === 'true', JSON.stringify(expState).slice(0, 120));
  check('experiment hint names the measurement', /86 measured/.test(expState.hint), expState.hint.slice(0, 80));
  await page.click('#lab-exp-seg button[data-exp="spin"]');
  await page.waitForTimeout(600);
  const spinState = await page.evaluate(() => ({ sg: window.__probe.state.cosmos.selfgrav, helix: window.__probe.state.cosmos.helix }));
  check('spin experiment sets self-gravity 0.45 on the user\'s state', spinState.sg === 0.45 && spinState.helix === 0.8, JSON.stringify(spinState));
  await page.click('#sw-lab');
  await page.keyboard.press('Escape');

  // the vessel radius must reach the vase, not only the ring (was a dead knob)
  await page.keyboard.press('3');
  await page.waitForTimeout(250);
  await page.click('#vessel-seg button[data-vessel="vase"]');
  await page.waitForTimeout(200);
  await page.evaluate(() => {
    const el = document.getElementById('in-vessel-radius');
    el.value = '0.40'; el.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await page.waitForTimeout(450);   // saveState is debounced 250 ms
  check('radius readout tracks the vase selection',
    (await page.textContent('#val-vessel-radius')).trim() === '0.40×R');
  const storedVase = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).vessel; }
    catch (e) { return null; }
  });
  check('vase radius persisted', storedVase && storedVase.radius === 0.4,
    JSON.stringify(storedVase));
  await page.click('#vessel-seg button[data-vessel="off"]');
  await page.keyboard.press('Escape');

  // --- sacred geometry: six folds at the top of the Overlays panel ---
  // A fold changes the picture, never the swarm. The readback runs inside the
  // animation frame right after the page has drawn (the drawing buffer is not
  // preserved): the 64x64 corner is dark when off and shows a mirrored copy of
  // the core when folded; top-to-bottom mirror pairs are exact for every fold
  // but Spiral.
  const sacredFrame = () => page.evaluate(() => new Promise(res => {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const gl = window.__probe.renderer.getContext();
      const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
      const px = new Uint8Array(W * H * 4);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px);
      const corner = [];
      for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
        const i = (y * W + x) * 4; corner.push(px[i] + px[i + 1] + px[i + 2]);
      }
      const grid = [];
      for (let y = 0; y < H; y += 4) for (let x = 0; x < W; x += 4) {
        const i = (y * W + x) * 4; grid.push(px[i] + px[i + 1] + px[i + 2]);
      }
      let flip = 0, n = 0;
      for (let y = 0; y < H / 2; y += 3) for (let x = 0; x < W; x += 3) {
        const a = (y * W + x) * 4, b = ((H - 1 - y) * W + x) * 4;
        flip += Math.abs(px[a] - px[b]) + Math.abs(px[a + 1] - px[b + 1]) + Math.abs(px[a + 2] - px[b + 2]);
        n++;
      }
      res({ W, H, corner, grid, flip: flip / (3 * n) });
    }));
  }));
  const countChanged = (a, b) => { let d = 0; for (let i = 0; i < a.length; i++) if (Math.abs(a[i] - b[i]) > 12) d++; return d; };
  const twoFrames = () => page.evaluate(() => new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res))));
  await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  await page.keyboard.press('Escape');
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  check('sacred seg has six folds', (await page.$$('#sacred-seg button')).length === 6);
  check('sacred starts off', (await page.evaluate(() => window.__probe.state.sacred)) === 'off');
  const offFrame = await sacredFrame();
  for (const mode of ['metatron', 'octopus', 'cubes', 'gasket', 'spiral']) {
    const errsBefore = errors.length;
    await page.click('#sacred-seg button[data-sacred="' + mode + '"]');
    await twoFrames();
    check('sacred ' + mode + ' sets the state',
      (await page.evaluate(() => window.__probe.state.sacred)) === mode);
    check('sacred ' + mode + ' is pressed',
      (await page.getAttribute('#sacred-seg button[data-sacred="' + mode + '"]', 'aria-pressed')) === 'true');
    const f = await sacredFrame();
    const corner = countChanged(f.corner, offFrame.corner);
    const frame = countChanged(f.grid, offFrame.grid) / f.grid.length;
    check('sacred ' + mode + ' changes the picture', corner > 40 || frame > 0.01,
      corner + ' corner pixels of 4096, ' + (100 * frame).toFixed(1) + '% of the frame');
    if (mode !== 'spiral')
      check('sacred ' + mode + ' is mirror-exact top to bottom', f.flip < 2,
        'mean |diff| ' + f.flip.toFixed(3) + ' (off: ' + offFrame.flip.toFixed(3) + ')');
    check('sacred ' + mode + ' throws nothing', errors.length === errsBefore,
      errors.slice(errsBefore, errsBefore + 2).join(' | '));
    if (mode === 'metatron') { await page.waitForTimeout(1200); await shot('13-sacred-metatron.png'); }
  }
  await page.waitForTimeout(450);   // saveState is debounced 250 ms
  const sacredStored = await page.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('resonance-chamber-v2')).sacred; }
    catch (e) { return null; }
  });
  check('sacred persisted', sacredStored === 'spiral', String(sacredStored));
  await page.click('#sacred-seg button[data-sacred="off"]');
  await twoFrames();
  check('sacred off again', (await page.evaluate(() => window.__probe.state.sacred)) === 'off');
  await page.keyboard.press('Escape');
  // --- end sacred geometry ---

  // preset save / load round trip, including camera + step
  await page.keyboard.press('1');
  await page.waitForTimeout(300);
  await page.click('#scenario-seg button[data-scn="formation"]');
  await page.waitForTimeout(600);
  await page.fill('#preset-name', 'smoke test');
  await page.click('#btn-preset-save');
  await page.waitForTimeout(200);
  check('preset saved', /Saved/.test(await page.textContent('#preset-status')));
  await page.click('#scenario-seg button[data-scn="chladni"]');
  await page.waitForTimeout(500);
  await page.selectOption('#preset-list', { label: 'smoke test' });
  await page.click('#btn-preset-load');
  await page.waitForTimeout(600);
  check('preset loaded', /Loaded/.test(await page.textContent('#preset-status')));
  const restored = await page.evaluate(() => {
    const s = JSON.parse(localStorage.getItem('resonance-chamber-v2'));
    return s.centers.on === true;   // formation had centers on
  });
  check('preset restored centers.on', restored);
  await page.click('#btn-preset-totext');
  const txt = await page.inputValue('#preset-text');
  check('preset to-text emits JSON with cam+step',
    (() => { try { const p = JSON.parse(txt); return p.cam && 'step' in p && p.state; } catch (e) { return false; } })());

  // export path: no viewer capability here -> a plain browser download must happen (ring 10)
  await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(200);
  await page.keyboard.press('3');
  await page.waitForTimeout(300);
  const [pointsDl] = await Promise.all([
    page.waitForEvent('download', { timeout: 20000 }).catch(() => null),
    page.click('#btn-export'),
  ]);
  await page.waitForTimeout(1500);
  const exportStatus = await page.textContent('#export-status');
  check('export downloads a csv without the viewer',
    !!pointsDl && pointsDl.suggestedFilename() === 'resonance-chamber-points.csv' && /^Saved [\d,]+ points/.test(exportStatus.trim()),
    (pointsDl && pointsDl.suggestedFilename()) + ' | ' + exportStatus.trim());

  check('defaults: centers off, chladni',
    defaults && defaults.centers === 'false' && defaults.form === 'true',
    JSON.stringify(defaults));

  const realErrors = errors.filter(e =>
    !/SwiftShader|GroupMarkerNotSet|Automatic fallback|WebGL.*deprecat|GPU stall|ERR_CONNECTION_RESET|ERR_TUNNEL|fonts.googleapis/i.test(e));
  check('no console/page errors', realErrors.length === 0,
    realErrors.slice(0, 4).join(' | '));

  await browser.close();
  console.log(fails.length ? '\n' + fails.length + ' FAILURES' : '\nSMOKE PASSED');
  process.exit(fails.length ? 1 : 0);
})().catch(e => { console.error('smoke crashed:', e); process.exit(2); });
