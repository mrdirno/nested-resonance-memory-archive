'use strict';
/* Author: Aldrin Payopay. GPL-3.0-only.
   Real WebGL regression tests of the observation protocol and its failure paths. */
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { chromium } = require('playwright');
let browser, passed = 0;
const check = (name, condition) => { assert.ok(condition, name); console.log('PASS '+name); passed++; };
(async () => {
  browser = await chromium.launch({executablePath:process.env.PW_CHROMIUM_PATH||undefined,
    args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page = await browser.newPage({viewport:{width:1280,height:800}});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{
    localStorage.setItem('resonance-chamber-v2', JSON.stringify({particles:4096, quality:0.4,
      cosmos:{epoch:false,hubble:0,mag:0.4,twist:false}, damping:0.3, stepsPerSec:0.25, smooth:false}));
    window.__forceDt=0.05;
  });
  await page.goto('file://'+path.join(__dirname,'rc-test.html'));
  await page.waitForSelector('.boot.done');
  await page.locator('#btn-open-bench').click();
  check('Observe opens the accessible bench', await page.locator('#session-seed').isVisible());
  await page.locator('#session-duration').fill('1');
  await page.locator('#session-seed').fill('12345');
  await page.locator('#btn-session-a').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status!=='running');
  let a=await page.evaluate(()=>__probe.benchRecord().runs[0]);
  check('A halts on exactly 20 ticks',a.status==='finished'&&a.ticks===20&&a.final.timeSeconds===1);
  const read=()=>page.evaluate(()=>{
    const P=__probe,S=P.texSize;
    return {p:Array.from(P.readTarget(P.posA,0,0,S,S)),v:Array.from(P.readTarget(P.velA,0,0,S,S))};
  });
  const first=await read();
  check('records a finite measurement with an explicit sample count',a.final.finite&&a.final.sampledParticles>0&&a.final.sampledParticles<=2048);
  await page.locator('#btn-session-replay').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status!=='running');
  assert.deepEqual(await read(),first); check('Repeat A reproduces every GPU position and velocity bit',true);
  await page.locator('#btn-session-b').click();
  await page.waitForFunction(()=>__probe.SESSION.b.status!=='running');
  const pair=await page.evaluate(()=>__probe.benchRecord());
  check('B changes only the magnetic integrator',pair.runs[1].recipe.state.lorentz==='boris');
  const ra=structuredClone(pair.runs[0].recipe),rb=structuredClone(pair.runs[1].recipe);
  rb.state.lorentz=ra.state.lorentz;assert.deepEqual(ra,rb);
  check('paired initial samples match',pair.comparison.sampledInitialStatesMatch);
  check('B endpoint responds to the integrator',pair.runs[0].final.sampleFingerprint!==pair.runs[1].final.sampleFingerprint);
  check('both arms stop on the same tick',pair.runs[1].ticks===20&&pair.runs[1].final.timeSeconds===1);
  // Actual browser download, then parse the downloaded record as an import.
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#btn-session-save').click()]);
  const saved=fs.readFileSync(await download.path(),'utf8');
  check('download carries build, initial recipe and both results',JSON.parse(saved).runs.length===2&&JSON.parse(saved).build);
  const roundTrip=await page.evaluate(text=>__probe.benchParseRecord(text),saved);
  assert.deepEqual(roundTrip,ra); check('saved record round-trips through strict recipe parser',true);
  await page.locator('#session-file').setInputFiles({name:'observation.json',mimeType:'application/json',buffer:Buffer.from(saved)});
  await page.waitForFunction(()=>__probe.SESSION.a.status==='finished'&&__probe.SESSION.b===null);
  assert.deepEqual(await read(),first); check('opening a saved observation replays the original full GPU state',true);
  const rejects=await page.evaluate(()=>{
    const record=__probe.benchRecord(), list=[];
    for(const mutation of [r=>r.build='wrong',r=>r.runs[0].recipe.seed=-1,r=>r.runs[0].recipe.ticks=1e9,
      r=>r.runs[0].recipe.state.particles=Infinity,r=>r.runs[0].recipe.state.cosmos.mag='bad']){
      const copy=JSON.parse(JSON.stringify(record));mutation(copy);
      try{__probe.benchParseRecord(JSON.stringify(copy));list.push(false);}catch{list.push(true);}
    }
    try{__probe.benchParseRecord(' '.repeat(1000001));list.push(false);}catch{list.push(true);}
    return list;
  });
  check('wrong build, invalid seed, excessive duration, malformed numbers and oversized imports rejected',rejects.every(Boolean));
  await page.locator('#session-duration').fill('10');
  await page.locator('#btn-session-a').click();
  await page.evaluate(()=>{__probe.state.damping=2;});
  await page.waitForFunction(()=>__probe.SESSION.a.status==='interrupted');
  check('a changed force invalidates the comparison',await page.evaluate(()=>__probe.SESSION.a.reason.includes('settings changed')));
  await page.locator('#btn-session-a').click();
  await page.evaluate(()=>__probe.reseed());
  check('reseed interrupts an active run',await page.evaluate(()=>__probe.SESSION.a.status==='interrupted'));
  // A warm self-gravity solve must not leak into the next A or B.
  await page.evaluate(()=>{__probe.state.cosmos.selfgrav=0.3;__probe.state.lab.on=true;});
  await page.locator('#session-duration').fill('1');
  await page.locator('#btn-session-a').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status==='finished');
  const gravityFirst=await read();
  await page.locator('#btn-session-replay').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status==='finished');
  assert.deepEqual(await read(),gravityFirst);check('self-gravity and Lab replay without old mesh or twin state',true);
  // The magnetic comparison must vanish when magnetic coupling is zero.
  await page.evaluate(()=>{__probe.state.cosmos.mag=0;});
  await page.locator('#btn-session-a').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status==='finished');
  const zeroField=await read();
  await page.locator('#btn-session-b').click();
  await page.waitForFunction(()=>__probe.SESSION.b.status==='finished');
  assert.deepEqual(await read(),zeroField);check('zero magnetic coupling is a full GPU negative control',true);
  const sanitized=await page.evaluate(()=>__probe.sanitizeState({stepsPerSec:0.02,fieldExp:-400,
    particles:NaN,damping:Infinity,constants:{a:'__proto__'},overlays:{c3:'false'}}));
  check('research hold rates and zero-field presets survive sanitization',sanitized.stepsPerSec===0.02&&sanitized.fieldExp===-400);
  check('nonfinite settings and prototype names normalize safely',Number.isFinite(sanitized.particles)&&Number.isFinite(sanitized.damping)&&sanitized.constants.a==='phi'&&!sanitized.overlays.c3);
  // A loop button can reset runtime phase even when its selected value stays the same.
  await page.evaluate(()=>{__probe.state.dimer.on=true;__probe.state.dimer.loop='cw';});
  await page.locator('#session-duration').fill('10');
  await page.locator('#btn-session-a').click();
  await page.waitForFunction(()=>__probe.SESSION.a.ticks>=5);
  await page.evaluate(()=>document.querySelector('#dimer-loop-seg button[data-loop="cw"]').click());
  check('restarting the selected dimer loop interrupts its active recipe',await page.evaluate(()=>__probe.SESSION.a.status==='interrupted'));
  await page.evaluate(()=>{__probe.state.offsetMode='manual';const e=document.getElementById('off-a');e.value='2147483648';e.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.locator('#session-duration').fill('1');
  await page.locator('#btn-session-a').click();
  await page.waitForFunction(()=>__probe.SESSION.a.status==='finished');
  const normalizedRecipe=await page.evaluate(()=>{const P=__probe;const r=P.benchParseRecord(JSON.stringify(P.benchRecord()));return {saved:r.state.offsets.a,executed:P.state.offsets.a};});
  check('large manual offsets execute and export the same importable recipe',normalizedRecipe.saved===2147483647&&normalizedRecipe.saved===normalizedRecipe.executed);
  // Narrow screen and keyboard activation of the new controls.
  await page.setViewportSize({width:390,height:844});
  check('mobile bench stays in the viewport',await page.locator('.observation-bench').evaluate(e=>{const r=e.getBoundingClientRect();return r.x>=0&&r.right<=innerWidth;}));
  await page.locator('#btn-session-tick').focus();
  const before=await page.evaluate(()=>__probe.simTime);
  await page.locator('#btn-session-tick').press('Space');
  const after=await page.evaluate(()=>__probe.simTime);
  check('keyboard tick advances once and remains paused',Math.abs(after-before-0.05)<1e-8&&await page.locator('#btn-play').getAttribute('aria-label')==='Play simulation');
  const shotDir=path.join(__dirname,'shots');fs.mkdirSync(shotDir,{recursive:true});
  await page.screenshot({path:path.join(shotDir,'observation-mobile.png')});
  await page.setViewportSize({width:1440,height:900});
  await page.screenshot({path:path.join(shotDir,'observation-desktop.png')});
  check('no JavaScript errors',errors.length===0);
  console.log(JSON.stringify({checks:passed,environment:pair.runs[0].environment,a:pair.runs[0].final,b:pair.runs[1].final}));
  const reduced=await browser.newPage({reducedMotion:'reduce'});
  await reduced.addInitScript(()=>localStorage.setItem('resonance-chamber-v2',JSON.stringify({particles:4096,quality:0.4})));
  await reduced.goto('file://'+path.join(__dirname,'rc-test.html'));await reduced.waitForSelector('.boot.done');
  check('reduced motion starts paused',await reduced.locator('#btn-play').getAttribute('aria-label')==='Play simulation');
  await browser.close();browser=null;
  console.log(passed+' observation checks passed');
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exitCode=1;});
