'use strict';
/* Author: Aldrin Payopay. GPL-3.0-only.
   Exercise the served production page without the test-build probe.
   HALO_URL must name the intended local preview or deployed release. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {chromium}=require('playwright');
const target=process.env.HALO_URL;
if(!target) throw new Error('Set HALO_URL to the page to verify.');
const out=path.resolve(process.env.HALO_LIVE_RECEIPTS||path.join(__dirname,'workspace/live'));
fs.mkdirSync(out,{recursive:true});
let browser;
(async()=>{
  browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>localStorage.setItem('resonance-chamber-v2',JSON.stringify({particles:1048576,quality:0.7})));
  const response=await page.goto(target);assert.equal(response.status(),200);
  const sourceSha256=crypto.createHash('sha256').update(await response.body()).digest('hex');
  await page.waitForSelector('.boot.done',{timeout:120000});
  assert.equal(await page.evaluate(()=>typeof window.__probe),'undefined');
  await page.getByRole('button',{name:'Observe',exact:true}).click();
  await page.getByRole('spinbutton',{name:'Particle seed',exact:true}).fill('12345');
  await page.getByRole('spinbutton',{name:'Chamber seconds',exact:true}).fill('2');
  await page.getByRole('button',{name:'Run A · current settings',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('session-status').textContent.includes('Run A stopped at exactly 40 ticks'),{},{timeout:120000});
  await page.getByRole('button',{name:'Run B · other magnetic step',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('session-status').textContent.includes('Run B stopped at exactly 40 ticks'),{},{timeout:120000});
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Save observation',exact:true}).click()]);
  const record=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
  assert.equal(record.runs.length,2);
  assert.ok(record.runs.every(r=>r.status==='finished'&&r.ticks===40&&r.final.finite&&r.recipe.state.particles===1048576));
  assert.ok(record.comparison.sampledInitialStatesMatch);
  await page.screenshot({path:path.join(out,'results.png')});
  await page.locator('#panel-lab').evaluate(e=>{e.scrollTop=0;});
  await page.screenshot({path:path.join(out,'desktop.png')});
  await page.setViewportSize({width:390,height:844});
  const inBounds=await page.locator('.observation-bench').evaluate(e=>{const r=e.getBoundingClientRect();return r.x>=0&&r.right<=innerWidth;});
  assert.ok(inBounds);
  await page.screenshot({path:path.join(out,'mobile.png')});
  assert.deepEqual(errors,[]);
  const receipt={url:target,observedAt:new Date().toISOString(),sourceSha256,probeAbsent:true,
    browser:browser.version(),renderer:'Chromium SwiftShader',pageErrors:errors,mobileInBounds:inBounds,
    observation:record,passed:true};
  fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({passed:true,url:target,sourceSha256,particles:1048576,ticksPerArm:40,receiptDirectory:out}));
  await browser.close();browser=null;
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exitCode=1;});
