'use strict';
/* Author: Aldrin Payopay. GPL-3.0-only. Sequential browser release gate.
   No retries: an intermittent failure remains a failure in its saved receipt. */
const {spawnSync} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const physics = process.argv.includes('--physics');
const suite = physics
  ? ['integ_test.js','mesh_test.js','conserve_test.js','dimer_test.js','bench_test.js']
  : ['tick_test.js','observation_test.js','lab_test.js','smoke.js'];
const out = path.resolve(process.env.HALO_RECEIPTS || path.join(__dirname,'workspace/release'));
fs.mkdirSync(out,{recursive:true});
const source=path.resolve(__dirname,'../../HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html');
const testPage=path.join(__dirname,'rc-test.html');
const sha=file=>fs.existsSync(file)?crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'):null;
const boundSource=fs.existsSync(testPage)?fs.readFileSync(testPage,'utf8').match(/^<!-- halo-test-source-sha256: ([a-f0-9]{64}) -->/):null;
const receipt={startedAt:new Date().toISOString(),sourceSha256:sha(source),testPageSha256:sha(testPage),node:process.version,
  playwright:require('playwright/package.json').version,suite:physics?'physics':'release',results:[]};
receipt.testPageMatchesSource=!!boundSource&&boundSource[1]===receipt.sourceSha256;
if(!receipt.testPageMatchesSource) console.error('Test page does not match the current source. Run python3 make_test_page.py first.');
for (const file of receipt.testPageMatchesSource?suite:[]) {
  const start=Date.now();console.log('Running '+file);
  const run=spawnSync(process.execPath,[path.join(__dirname,file)],{cwd:__dirname,encoding:'utf8',
    timeout:15*60*1000,maxBuffer:16*1024*1024,env:process.env});
  fs.writeFileSync(path.join(out,file+'.log'),(run.stdout||'')+(run.stderr||'')+(run.error?'\n'+run.error.message:''));
  const result={test:file,exitCode:run.status,signal:run.signal,seconds:(Date.now()-start)/1000,passed:run.status===0&&!run.error};
  receipt.results.push(result);console.log(JSON.stringify(result));
  if (!result.passed) {process.exitCode=1;break;}
}
receipt.finishedAt=new Date().toISOString();receipt.sourceUnchanged=receipt.sourceSha256===sha(source);
receipt.testPageUnchanged=receipt.testPageSha256===sha(testPage);
receipt.passed=receipt.testPageMatchesSource&&receipt.sourceUnchanged&&receipt.testPageUnchanged&&receipt.results.length===suite.length&&receipt.results.every(r=>r.passed);
fs.writeFileSync(path.join(out,(physics?'physics':'release')+'.json'),JSON.stringify(receipt,null,2)+'\n');
if(!receipt.passed) process.exitCode=1;
console.log('Receipt: '+path.join(out,(physics?'physics':'release')+'.json'));
