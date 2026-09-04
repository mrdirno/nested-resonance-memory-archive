/* Improvisator ∞ — browser proof.
   Loads the page in headless Chromium, watches for script errors, drives the
   real transport for a few seconds, then renders the offline bounce and
   measures the audio that actually comes out: peak, RMS, clipping, silence.
   Nothing here is simulated — it is the same code path a listener hears.

   usage: node tools/improvisator/browser-check.mjs [file.html] [out.wav]
   Author: Aldrin Payopay
*/
import { chromium } from 'playwright-core';
import { resolve } from 'node:path';
import { writeFileSync } from 'node:fs';

const file = resolve(process.argv[2] || 'tools/improvisator/improvisator-infinite.html');
const outWav = process.argv[3] || null;   /* the page bounces a fixed 60 s */
/* Pin the seed so a before/after pair is the same piece played two ways. */
const seed = process.env.IMPROV_SEED || '';
const EXEC = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const browser = await chromium.launch({
  executablePath: EXEC,
  args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio', '--no-sandbox'],
});
const ctx = await browser.newContext({ acceptDownloads: true });
const page = await ctx.newPage();

const errors = [], warnings = [];
page.on('pageerror', e => errors.push('pageerror: ' + (e && e.message)));
page.on('console', m => {
  if (m.type() === 'error') errors.push('console.error: ' + m.text());
  if (m.type() === 'warning') warnings.push(m.text());
});

/* capture the export blob instead of letting it hit the disk */
await page.addInitScript(() => {
  window.__blobs = [];
  const real = URL.createObjectURL.bind(URL);
  URL.createObjectURL = b => { if (b instanceof Blob) window.__blobs.push(b); return real(b); };
});

await page.goto('file://' + file + (seed ? '#seed=' + encodeURIComponent(seed) : ''), { waitUntil: 'load' });
await page.waitForFunction(() => window.IMPROV && window.IMPROV.Composer, null, { timeout: 15000 });

/* the piano bank renders in idle frames; wait for it to finish */
const bankMs = Date.now();
await page.waitForFunction(() => {
  const b = document.getElementById('prep');
  return b && !b.classList.contains('show');
}, null, { timeout: 240000 }).catch(() => {});
const bankReady = await page.evaluate(() => {
  const f = document.getElementById('prepFill');
  return f ? f.style.width : 'unknown';
});

/* drive the real transport */
await page.click('#playButton');
await page.waitForTimeout(6000);
const live = await page.evaluate(() => ({
  bar: (document.getElementById('barLabel') || {}).textContent,
  chord: (document.getElementById('harmony') || {}).textContent,
  key: (document.getElementById('keyLabel') || {}).textContent,
  tempo: (document.getElementById('tempoLabel') || {}).textContent,
  ringing: (document.getElementById('voiceLabel') || {}).textContent,
  time: (document.getElementById('timecode') || {}).textContent,
  status: (document.getElementById('statusText') || {}).textContent,
}));
await page.click('#playButton');

/* offline bounce — the same Engine and the same events, rendered to a buffer */
await page.evaluate(s => { window.dispatchEvent(new Event('focus')); }, null);
await page.keyboard.press('b');
const wavB64 = await page.waitForFunction(() => {
  const b = window.__blobs.find(x => x.type === 'audio/wav');
  if (!b) return null;
  if (!window.__wavPromise) {
    window.__wavPromise = b.arrayBuffer().then(ab => {
      const u = new Uint8Array(ab);
      let s = '';
      for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192));
      window.__wav = btoa(s);
    });
    return null;
  }
  return window.__wav || null;
}, null, { timeout: 180000, polling: 500 }).then(h => h.jsonValue()).catch(() => null);

const notices = await page.evaluate(() => (document.getElementById('notice') || {}).textContent);
await browser.close();

console.log(`
IMPROVISATOR BROWSER REPORT
  file            ${file}${seed ? '\n  seed            ' + seed : ''}
  bank            ${bankReady} rendered in ${((Date.now() - bankMs) / 1000).toFixed(1)} s
  after 6 s live  ${live.bar} · ${live.chord} · ${live.key} · ${live.tempo} · ${live.ringing} · ${live.time} · "${live.status}"
  last notice     ${notices}
  script errors   ${errors.length ? errors.length + '\n    ' + errors.slice(0, 10).join('\n    ') : 'none'}`);

if (!wavB64) {
  console.log('  bounce          FAILED — no WAV produced');
  process.exitCode = 1;
} else {
  const buf = Buffer.from(wavB64, 'base64');
  if (outWav) writeFileSync(outWav, buf);
  const sr = buf.readUInt32LE(24), ch = buf.readUInt16LE(22);
  const n = (buf.length - 44) / 2 / ch;
  let peak = 0, sum = 0, clipped = 0, dc = 0, silent = 0;
  const window = Math.floor(sr * 0.05);
  let winPeak = 0, winCount = 0;
  for (let i = 0; i < n; i++) {
    const v = buf.readInt16LE(44 + i * ch * 2) / 32768;
    const a = Math.abs(v);
    if (a > peak) peak = a;
    if (a > winPeak) winPeak = a;
    if (a >= 0.9995) clipped++;
    sum += v * v; dc += v;
    if ((i + 1) % window === 0) { if (winPeak < 0.0005) silent++; winCount++; winPeak = 0; }
  }
  const rms = Math.sqrt(sum / n), db = x => (20 * Math.log10(Math.max(1e-9, x))).toFixed(1);
  console.log(`  bounce          ${(n / sr).toFixed(1)} s @ ${sr} Hz × ${ch}ch, ${(buf.length / 1048576).toFixed(1)} MB
  peak            ${db(peak)} dBFS      rms ${db(rms)} dBFS      crest ${(20 * Math.log10(peak / rms)).toFixed(1)} dB
  clipped samples ${clipped}${clipped ? '  !!' : ''}
  dc offset       ${(dc / n).toExponential(2)}
  silence         ${silent}/${winCount} of the 50 ms windows are below -66 dBFS${outWav ? '\n  written         ' + outWav : ''}`);
  const bad = clipped > 0 || peak < 0.02 || silent / winCount > 0.35 || errors.length;
  console.log(`  verdict         ${bad ? 'FAIL' : 'PASS'}`);
  process.exitCode = bad ? 1 : 0;
}
