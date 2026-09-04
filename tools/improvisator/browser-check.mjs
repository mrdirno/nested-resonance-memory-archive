/* Improvisator ∞ — browser gates.
   Everything here is measured in a real Chromium against the real page: the
   things a headless kernel run cannot see, chiefly whether the three renderings
   of one seed are the same performance.

     node tools/improvisator/browser-check.mjs [file]

   Author: Aldrin Payopay */

import { writeFileSync, existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const FILE = path.resolve(process.argv[2] || 'tools/improvisator/improvisator-infinite.html');
const SEED = process.env.IMPROV_SEED || 'grey-rain-0001';
const OUT = process.env.IMPROV_OUT || '/tmp';

/* ---------- finding playwright and chromium ------------------------------ */

const require_ = createRequire(import.meta.url);
function resolvePlaywright () {
  const tries = [process.env.PLAYWRIGHT_CORE, 'playwright-core',
                 path.resolve('node_modules/playwright-core')].filter(Boolean);
  for (const t of tries) { try { return require_.resolve(t); } catch (_) {} }
  throw new Error('playwright-core not found; set PLAYWRIGHT_CORE to its directory');
}
function resolveChromium () {
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, '/opt/pw-browsers'].filter(Boolean);
  const names = ['chromium-1194/chrome-linux/chrome', 'chromium/chrome-linux/chrome'];
  for (const r of roots) for (const n of names) {
    const p = path.join(r, n); if (existsSync(p)) return p;
  }
  for (const r of roots) {
    try {
      const { readdirSync } = require_('node:fs');
      for (const d of readdirSync(r)) {
        const p = path.join(r, d, 'chrome-linux', 'chrome');
        if (existsSync(p)) return p;
      }
    } catch (_) {}
  }
  return undefined;
}
const { chromium } = require_(resolvePlaywright());

/* ---------- MIDI parsing ------------------------------------------------- */

function parseMidi (bytes) {
  let p = 0;
  const u32 = () => { const v = (bytes[p] << 24 | bytes[p + 1] << 16 | bytes[p + 2] << 8 | bytes[p + 3]) >>> 0; p += 4; return v; };
  const u16 = () => { const v = bytes[p] << 8 | bytes[p + 1]; p += 2; return v; };
  const tag = () => { const s = String.fromCharCode(bytes[p], bytes[p + 1], bytes[p + 2], bytes[p + 3]); p += 4; return s; };
  if (tag() !== 'MThd') throw new Error('not a MIDI file');
  const hdr = u32(); const format = u16(); const ntrk = u16(); const ppq = u16();
  p += hdr - 6;
  const tracks = [];
  for (let t = 0; t < ntrk; t++) {
    if (tag() !== 'MTrk') throw new Error('track ' + t + ' has no MTrk');
    const len = u32(); const end = p + len;
    const ev = []; let tick = 0, running = 0;
    while (p < end) {
      let d = 0, b;
      do { b = bytes[p++]; d = (d << 7) | (b & 0x7f); } while (b & 0x80);
      tick += d;
      let st = bytes[p];
      if (st & 0x80) p++; else st = running;
      running = st;
      const hi = st & 0xf0;
      if (st === 0xff) { const type = bytes[p++]; let l = 0, c; do { c = bytes[p++]; l = (l << 7) | (c & 0x7f); } while (c & 0x80);
        ev.push({ tick, meta: type, data: bytes.slice(p, p + l) }); p += l; }
      else if (hi === 0x80 || hi === 0x90 || hi === 0xa0 || hi === 0xb0 || hi === 0xe0) {
        ev.push({ tick, status: st, a: bytes[p], b: bytes[p + 1] }); p += 2;
      } else if (hi === 0xc0 || hi === 0xd0) { ev.push({ tick, status: st, a: bytes[p] }); p += 1; }
      else throw new Error('unknown status 0x' + st.toString(16) + ' at ' + p);
    }
    p = end; tracks.push(ev);
  }
  return { format, ppq, tracks };
}

/* ---------- WAV ---------------------------------------------------------- */

function readWav (buf) {
  let o = 12, fmt = null, data = null;
  while (o + 8 <= buf.length) {
    const id = buf.toString('ascii', o, o + 4), sz = buf.readUInt32LE(o + 4);
    if (id === 'fmt ') fmt = { ch: buf.readUInt16LE(o + 10), rate: buf.readUInt32LE(o + 12), bits: buf.readUInt16LE(o + 22) };
    if (id === 'data') data = buf.subarray(o + 8, o + 8 + sz);
    o += 8 + sz + (sz & 1);
  }
  const n = data.length / (fmt.bits / 8) / fmt.ch;
  const ch = [];
  for (let c = 0; c < fmt.ch; c++) ch.push(new Float64Array(n));
  for (let i = 0; i < n; i++) for (let c = 0; c < fmt.ch; c++)
    ch[c][i] = data.readInt16LE((i * fmt.ch + c) * 2) / 32768;
  return { ...fmt, n, ch };
}
const db = x => 20 * Math.log10(Math.max(x, 1e-12));

/* ---------- the run ------------------------------------------------------ */

const fails = [];
const fail = (g, m) => { fails.push(g); console.log('  ' + g.padEnd(16) + 'FAIL — ' + m); };
const pass = (g, m) => console.log('  ' + g.padEnd(16) + 'PASS — ' + m);

const browser = await chromium.launch({
  executablePath: resolveChromium(),
  args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio', '--no-sandbox'],
});
const ctx = await browser.newContext();
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

/* Capture every Blob the page hands to createObjectURL, which is how both
   exports leave the page. */
await page.addInitScript(() => {
  window.__blobs = [];
  const real = URL.createObjectURL.bind(URL);
  URL.createObjectURL = x => { if (x instanceof Blob) window.__blobs.push(x); return real(x); };
});

console.log('IMPROVISATOR BROWSER REPORT');
console.log('  file            ' + FILE);
console.log('  seed            ' + SEED);

const t0 = Date.now();
await page.goto('file://' + FILE + '#seed=' + encodeURIComponent(SEED), { waitUntil: 'load' });
await page.waitForFunction(() => window.IMPROV, null, { timeout: 30000 });
await page.waitForFunction(() => {
  const p = document.getElementById('prep');
  return !p || !p.classList.contains('show');
}, null, { timeout: 300000 }).catch(() => {});
const bankMs = Date.now() - t0;
/* The page is an IIFE, so nothing is on window: everything below is read from
   the DOM, the same surface a listener has. */
const prepDone = await page.evaluate(() => {
  const p = document.getElementById('prep');
  return !p || !p.classList.contains('show');
});
console.log('  bank            ' + (prepDone ? 'ready' : 'still preparing') + ' after ' + (bankMs / 1000).toFixed(1) + ' s');

/* --- ONE RENDERER: the same code must turn a bar into engine calls for the
   transport and for the offline bounce, or a seed means two performances. --- */
{
  const src = readFileSync(FILE, 'utf8');
  const renderers = (src.match(/function\s+renderBar\s*\(/g) || []).length;
  const inlinePlay = (src.match(/\.play\(\s*e\.pitch/g) || []).length;
  if (renderers === 1 && inlinePlay <= 1)
    pass('ONE RENDERER', 'a single renderBar() turns a bar into engine calls; ' + inlinePlay + ' call site');
  else
    fail('ONE RENDERER', 'found ' + renderers + ' renderBar() definitions and ' + inlinePlay +
      ' places that schedule a bar by hand — the transport and the bounce can drift apart');
}

/* --- it plays --- */
await page.click('#playButton');
await page.waitForTimeout(6000);
const live = await page.evaluate(() => {
  const t = id => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
  return { status: t('statusText'), chord: t('harmony'), role: t('roleLabel'), voices: t('voiceLabel'), key: t('keyLabel'),
           tempo: t('tempoLabel'), time: t('timecode'), bar: t('barLabel') };
});
console.log('  after 6 s live  ' + Object.entries(live).filter(([, v]) => v).map(([k, v]) => k + ' ' + JSON.stringify(v)).join(' · '));
const advanced = live.time && /00:00:0[1-9]|00:00:[1-9]/.test(live.time);
if (live.status !== 'playing' || !advanced)
  fail('PLAYS', 'after six seconds the status is ' + JSON.stringify(live.status) + ' and the clock reads ' + JSON.stringify(live.time));
else pass('PLAYS', 'status "playing", clock at ' + live.time + ', chord ' + JSON.stringify(live.chord));

/* --- MIDI --- */
await page.evaluate(() => { window.__blobs.length = 0; });
await page.keyboard.press('m');
const midiB64 = await page.waitForFunction(() => {
  const b = window.__blobs.find(x => /midi|octet/.test(x.type));
  if (!b) return null;
  if (!window.__mp) { window.__mp = b.arrayBuffer().then(ab => {
    const u = new Uint8Array(ab); let s = '';
    for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192));
    window.__m = btoa(s); }); return null; }
  return window.__m || null;
}, null, { timeout: 60000, polling: 300 }).then(h => h.jsonValue()).catch(() => null);

if (!midiB64) fail('MIDI', 'pressing M produced no file');
else {
  const bytes = Buffer.from(midiB64, 'base64');
  try {
    const m = parseMidi(bytes);
    let on = 0, off = 0, unmatched = 0, cc64 = 0, tempo = 0;
    const held = new Map();
    for (const tr of m.tracks) for (const e of tr) {
      if (e.meta === 0x51) tempo++;
      if (!e.status) continue;
      const hi = e.status & 0xf0, ch = e.status & 0x0f;
      if (hi === 0xb0 && e.a === 64) cc64++;
      if (hi === 0x90 && e.b > 0) { on++; const k = ch + ':' + e.a; held.set(k, (held.get(k) || 0) + 1); }
      if (hi === 0x80 || (hi === 0x90 && e.b === 0)) {
        off++; const k = ch + ':' + e.a;
        if (!held.get(k)) unmatched++; else held.set(k, held.get(k) - 1);
      }
    }
    for (const v of held.values()) unmatched += v;
    console.log('  midi            ' + (bytes.length / 1024).toFixed(0) + ' kB, format ' + m.format +
                ', ' + m.tracks.length + ' tracks, ' + m.ppq + ' ppq');
    console.log('  notes           ' + on + ' on / ' + off + ' off, ' + unmatched + ' unmatched · ' +
                cc64 + ' CC64 · ' + tempo + ' tempo metas');
    if (unmatched || !on || !tempo) fail('MIDI', unmatched + ' unmatched notes, ' + on + ' note-ons, ' + tempo + ' tempo events');
    else pass('MIDI', 'every note paired, tempo map present');
    writeFileSync(path.join(OUT, 'improvisator-check.mid'), bytes);
  } catch (err) { fail('MIDI', 'could not parse the exported file: ' + err.message); }
}

/* --- bounce --- */
async function bounce (label) {
  await page.evaluate(() => { window.__blobs.length = 0; window.__wp = null; window.__w = null; });
  await page.keyboard.press('b');
  const b64 = await page.waitForFunction(() => {
    const b = window.__blobs.find(x => x.type === 'audio/wav');
    if (!b) return null;
    if (!window.__wp) { window.__wp = b.arrayBuffer().then(ab => {
      const u = new Uint8Array(ab); let s = '';
      for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192));
      window.__w = btoa(s); }); return null; }
    return window.__w || null;
  }, null, { timeout: 900000, polling: 500 }).then(h => h.jsonValue());
  const buf = Buffer.from(b64, 'base64');
  writeFileSync(path.join(OUT, 'improvisator-' + label + '.wav'), buf);
  return readWav(buf);
}

const w = await bounce('check');
{
  let peak = 0, sum = 0, clipped = 0;
  const L = w.ch[0], R = w.ch[1] || w.ch[0];
  for (let i = 0; i < w.n; i++) {
    const a = Math.abs(L[i]), b = Math.abs(R[i]);
    if (a > peak) peak = a; if (b > peak) peak = b;
    if (a >= 0.9999 || b >= 0.9999) clipped++;
    sum += (L[i] * L[i] + R[i] * R[i]) / 2;
  }
  const rms = Math.sqrt(sum / w.n);
  let quiet = 0; const win = Math.floor(w.rate * 0.05);
  for (let i = 0; i + win < w.n; i += win) {
    let s = 0; for (let j = i; j < i + win; j++) s += L[j] * L[j];
    if (db(Math.sqrt(s / win)) < -66) quiet++;
  }
  console.log('  bounce          ' + (w.n / w.rate).toFixed(1) + ' s @ ' + w.rate + ' Hz × ' + w.ch.length + 'ch');
  console.log('  peak            ' + db(peak).toFixed(1) + ' dBFS      rms ' + db(rms).toFixed(1) +
              ' dBFS      crest ' + (db(peak) - db(rms)).toFixed(1) + ' dB');
  console.log('  clipped         ' + clipped + '      quiet windows ' + quiet);
  if (peak < 0.02) fail('BOUNCE', 'the offline render is silent (peak ' + db(peak).toFixed(1) + ' dBFS)');
  else if (clipped > 0) fail('BOUNCE', clipped + ' clipped samples');
  else pass('BOUNCE', 'audio present, no clipping, peak ' + db(peak).toFixed(1) + ' dBFS');
}

/* --- repeatability: the same seed must bounce the same take --- */
{
  const w2 = await bounce('check2');
  const n = Math.min(w.n, w2.n);
  let sd2 = 0, sa = 0, dpk = 0;
  for (let i = 0; i < n; i++) {
    const e = w.ch[0][i] - w2.ch[0][i];
    sd2 += e * e; sa += w.ch[0][i] * w.ch[0][i];
    if (Math.abs(e) > dpk) dpk = Math.abs(e);
  }
  const rel = db(Math.sqrt(sd2 / n)) - db(Math.sqrt(sa / n));
  console.log('  repeatability   two bounces differ by ' + rel.toFixed(1) + ' dB rms (peak ' + db(dpk).toFixed(1) + ' dBFS)');
  if (rel > -60) fail('REPEATABLE', 'two bounces of one seed differ by ' + rel.toFixed(1) + ' dB — a per-note value is not following the seed');
  else pass('REPEATABLE', 'two bounces of one seed are the same take to ' + rel.toFixed(1) + ' dB');
}

/* --- errors --- */
console.log('  script errors   ' + (errors.length ? errors.slice(0, 4).join(' | ') : 'none'));
if (errors.length) fail('NO ERRORS', errors.length + ' console/page errors');
else pass('NO ERRORS', 'no console or page errors across the whole run');

await browser.close();
console.log('');
if (fails.length) { console.log('  verdict         FAIL — ' + fails.join(', ')); process.exit(1); }
console.log('  verdict         PASS');
