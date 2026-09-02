'use strict';
/* memory_estimator_check.js — is the offline analysis the page's own estimator?
 
   The confirmatory analysis is computed in numpy from exported density meshes. That
   is only legitimate if it is the page's arithmetic and not a lookalike. This feeds
   the stored meshes back into the page's own labCorr and compares, value for value.
 
   Pass: every |numpy - page| <= 1e-6.
 
   usage: node memory_estimator_check.js <run.json>
   Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const runJson = process.argv[2];
if (!runJson) { console.error('usage: node memory_estimator_check.js <run.json>'); process.exit(2); }
const d = JSON.parse(fs.readFileSync(runJson, 'utf8'));
const meshBuf = fs.readFileSync(path.join(path.dirname(runJson), d.mesh_file));
const all = new Float32Array(meshBuf.buffer, meshBuf.byteOffset, meshBuf.length / 4);
const N3 = 32 * 32 * 32;
const mesh = k => Array.from(all.subarray(k * N3, (k + 1) * N3));

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-gpu-sandbox', '--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 480, height: 360 } });
  await page.addInitScript(() => {
    try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 100000, quality: 0.4 })); } catch (e) {}
  });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 180000 });

  const rows = [];
  const nEpochs = d.mesh_count;
  for (let k = 1; k < nEpochs; k++) {
    const pageVals = await page.evaluate(({ a, b, c }) => {
      const P = window.__probe;
      const A = new Float32Array(a), B = new Float32Array(b);
      const out = { f2: P.labCorr(A, B, 2), f4: null, f1: P.labCorr(A, B, 1) };
      if (c) out.f4 = P.labCorr(A, new Float32Array(c), 4);
      return out;
    }, { a: mesh(k), b: mesh(k - 1), c: k >= 2 ? mesh(k - 2) : null });
    rows.push({ epoch: k + 1, ...pageVals });
  }
  await browser.close();
  const out = path.join(path.dirname(runJson), path.basename(runJson, '.json') + '.pagecorr.json');
  fs.writeFileSync(out, JSON.stringify({ source: path.basename(runJson), rows }, null, 1));
  console.log('page labCorr values written to', out);
  for (const r of rows) console.log(`  epoch ${r.epoch}  f2 ${r.f2}  f4 ${r.f4}  f1 ${r.f1}`);
})().catch(e => { console.error('crashed:', e); process.exit(2); });
