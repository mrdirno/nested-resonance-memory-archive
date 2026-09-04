/* Improvisator ∞ — browser proof.
   Loads the page in headless Chromium, watches for script errors, drives the
   real transport for a few seconds, then renders the offline bounce and
   measures the audio that actually comes out: peak, RMS, clipping, silence.
   Nothing here is simulated — it is the same code path a listener hears.

   usage: node tools/improvisator/browser-check.mjs [file.html] [out.wav]
   Author: Aldrin Payopay
*/
/* playwright-core is a dev dependency, not part of the page. Resolve it from
   the usual place, or from PLAYWRIGHT_CORE when it lives outside the repo. */
const pw = await (async () => {
  const paths = [];
  if (process.env.PLAYWRIGHT_CORE) paths.push(process.env.PLAYWRIGHT_CORE);
  paths.push('playwright-core');
  for (const p of paths) {
    try { const m = await import(p); return m.chromium ? m : m.default; } catch (_) {}
  }
  console.error('playwright-core not found. npm i playwright-core, or set PLAYWRIGHT_CORE to its index.js');
  process.exit(2);
})();
const chromium = pw.chromium;
import { resolve } from 'node:path';
import { writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const file = resolve(process.argv[2] || 'tools/improvisator/improvisator-infinite.html');
const outWav = process.argv[3] || null;   /* the page bounces a fixed 60 s */
/* Pin the seed so a before/after pair is the same piece played two ways. */
const seed = process.env.IMPROV_SEED || '';
/* Playwright's own browser download, wherever this machine put it. */
const EXEC = process.env.CHROMIUM_PATH || (() => {
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, '/opt/pw-browsers'].filter(Boolean);
  for (const r of roots) {
    try {
      for (const d of readdirSync(r)) {
        if (!d.startsWith('chromium-')) continue;
        const c = join(r, d, 'chrome-linux', 'chrome');
        if (existsSync(c)) return c;
      }
    } catch (_) {}
  }
  return undefined;
})();

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

/* The MIDI export, through the page's own button, parsed back from the bytes
   it actually writes. */
await page.click('#exportMidi');
const midiB64 = await page.waitForFunction(() => {
  const b = window.__blobs.find(x => x.type === 'audio/midi');
  if (!b) return null;
  if (!window.__midiPromise) {
    window.__midiPromise = b.arrayBuffer().then(ab => {
      const u = new Uint8Array(ab);
      let s = '';
      for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192));
      window.__midi = btoa(s);
    });
    return null;
  }
  return window.__midi || null;
}, null, { timeout: 60000, polling: 300 }).then(h => h.jsonValue()).catch(() => null);

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

/* ---- the exported MIDI must be a well-formed file of the same performance -- */
if (!midiB64) {
  console.log('  midi            FAILED — no MIDI produced');
  process.exitCode = 1;
} else {
  const m = Buffer.from(midiB64, 'base64');
  let ok = m.toString('ascii', 0, 4) === 'MThd';
  const fmt = ok ? m.readUInt16BE(8) : -1, ntrk = ok ? m.readUInt16BE(10) : 0, ppq = ok ? m.readUInt16BE(12) : 0;
  let off = 14, on = 0, offs = 0, cc = 0, dangling = 0, tempos = 0, badTrack = false;
  const open = new Map();
  for (let t = 0; t < ntrk && !badTrack; t++) {
    if (m.toString('ascii', off, off + 4) !== 'MTrk') { badTrack = true; break; }
    const len = m.readUInt32BE(off + 4), end = off + 8 + len;
    let p = off + 8, run = 0;
    while (p < end) {
      let d = 0, byte;
      do { byte = m[p++]; d = (d << 7) | (byte & 0x7f); } while (byte & 0x80);
      let st = m[p];
      if (st & 0x80) { p++; run = st; } else st = run;
      if (st === 0xff) {
        const type = m[p++];
        let l = 0, by; do { by = m[p++]; l = (l << 7) | (by & 0x7f); } while (by & 0x80);
        if (type === 0x51) tempos++;
        p += l;
      } else if ((st & 0xf0) === 0x90) {
        const n = m[p++], v = m[p++];
        if (v > 0) { on++; const k = (st & 0xf) + ':' + n; open.set(k, (open.get(k) || 0) + 1); }
        else { offs++; const k = (st & 0xf) + ':' + n; const c0 = open.get(k) || 0; if (c0 <= 0) dangling++; else open.set(k, c0 - 1); }
      } else if ((st & 0xf0) === 0x80) {
        const n = m[p++]; p++;
        offs++; const k = (st & 0xf) + ':' + n; const c0 = open.get(k) || 0; if (c0 <= 0) dangling++; else open.set(k, c0 - 1);
      } else if ((st & 0xf0) === 0xb0) { const c1 = m[p++]; p++; if (c1 === 64) cc++; }
      else if ((st & 0xf0) === 0xc0 || (st & 0xf0) === 0xd0) p += 1;
      else p += 2;
    }
    off = end;
  }
  for (const [, v] of open) if (v > 0) dangling += v;
  const bad = !ok || badTrack || fmt !== 1 || on === 0 || dangling > 0 || cc === 0 || tempos === 0;
  console.log(`  midi            ${(m.length / 1024).toFixed(0)} kB, format ${fmt}, ${ntrk} tracks, ${ppq} ppq
  notes           ${on} on / ${offs} off, ${dangling} unmatched${dangling ? '  !!' : ''}
  pedal + tempo   ${cc} CC64 events across the lanes, ${tempos} tempo changes
  midi verdict    ${bad ? 'FAIL' : 'PASS'}`);
  if (bad) process.exitCode = 1;
}

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
