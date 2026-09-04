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

/* --- SAMPLE RATE: the piano must not be tuned by whatever device is plugged
   in. The bank renders at a rate fixed when the page loads and the playback
   context is created later; a buffer declared at a literal rate is reinterpreted
   if the two disagree, which puts the whole instrument 1.47 semitones sharp
   between 44.1 and 48 kHz. --- */
{
  const src = readFileSync(FILE, 'utf8');
  const literal = [...src.matchAll(/createBuffer\s*\([^)]*?,\s*(\d{4,6})\s*\)/g)].map(m => m[1]);
  const rateAtPlayback = await page.evaluate(() => {
    const C = window.AudioContext || window.webkitAudioContext;
    const c = new C(); const r = c.sampleRate; c.close(); return r;
  });
  console.log('  context rate    ' + rateAtPlayback + ' Hz');
  if (literal.length)
    fail('SAMPLE RATE', 'a buffer is declared at the literal rate ' + literal.join(', ') +
      ' instead of the rate its samples were rendered at');
  else pass('SAMPLE RATE', 'every buffer is declared at the rate its data was rendered at');
}

/* --- NO ENGINE STATE: nothing a note sounds like may come from how long the
   engine has been running. The felt noise under a hammer and under the pedal
   used to be drawn from a stream the engine advanced per event, so an engine
   that had been playing for an hour and the brand-new one bounceWav builds made
   different sound from identical events -- the bounce was not a recording of
   what you had been listening to. --- */
{
  const src = readFileSync(FILE, 'utf8');
  const body = f => {
    const at = src.indexOf('Engine.prototype.' + f + ' = function');
    if (at < 0) return null;
    const end = src.indexOf('\n};', at);
    return src.slice(at, end < 0 ? at + 4000 : end);
  };
  const problems = [];
  for (const f of ['play', 'pedalMechanic', 'release', 'damp']) {
    const b = body(f);
    if (b === null) { problems.push('Engine.' + f + ' not found'); continue; }
    if (/\brng\b|Math\.random/.test(b)) problems.push('Engine.' + f + ' draws from a random stream per event');
  }
  const seeds = [...src.matchAll(/new K\.RNG\(([^)]*)\)/g)].map(m => m[1].trim());
  console.log('  engine seeds    ' + (seeds.length ? seeds.join(', ') : 'none'));
  if (problems.length) fail('NO ENGINE STATE', problems.join('; '));
  else pass('NO ENGINE STATE', 'no per-event value comes from the engine\'s own running state');
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

/* --- CHARACTERS: every button has to apply, and none may throw. The build this
   started from declared LOCKED_PERFORMANCE inside the kernel's closure and
   never exported it, so applyPreset threw a ReferenceError on every click: all
   eight buttons were inert, the key label never moved, and the active state
   stayed on the first one. Nothing in the page surfaced it. --- */
{
  const names = await page.$$eval('.preset', bs => bs.map(x => x.dataset.preset));
  const before = errors.length;
  const seen = new Set();
  const problems = [];
  for (const n of names) {
    await page.click('.preset[data-preset="' + n + '"]');
    await page.waitForTimeout(150);
    const st = await page.evaluate(() => ({
      key: (document.getElementById('keyLabel') || {}).textContent,
      active: [...document.querySelectorAll('.preset')].filter(b => b.classList.contains('active'))
                .map(b => b.dataset.preset).join(','),
      melody: (document.getElementById('melodyValue') || {}).textContent,
      motion: (document.getElementById('motionValue') || {}).textContent,
    }));
    if (st.active !== n) problems.push(n + ' did not become the active character (active=' + st.active + ')');
    seen.add(st.key + '|' + st.melody + '|' + st.motion);
  }
  const threw = errors.slice(before);
  console.log('  characters      ' + names.length + ' buttons, ' + seen.size + ' distinct states');
  if (threw.length) problems.push('threw: ' + threw[0].slice(0, 100));
  if (seen.size < names.length - 1) problems.push('only ' + seen.size + ' of ' + names.length +
    ' buttons produce a distinct key and posture');
  if (problems.length) fail('CHARACTERS', problems.slice(0, 3).join(' | '));
  else pass('CHARACTERS', 'all ' + names.length + ' character buttons apply, none throws, ' +
    seen.size + ' distinct states');
}

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
    let on = 0, off = 0, unmatched = 0, tempo = 0, timesig = 0, firstTick = Infinity, badText = 0;
    const cc64ByChannel = new Map(), noteChannels = new Set(), overlaps = [];
    const held = new Map(), sounding = new Map();
    for (const tr of m.tracks) {
      /* per track, in time order, so an overlap is a real overlap */
      const seq = [...tr].sort((a, b) => a.tick - b.tick);
      for (const e of seq) {
        if (e.meta === 0x51) tempo++;
        if (e.meta === 0x58) timesig++;
        if ((e.meta === 0x01 || e.meta === 0x06 || e.meta === 0x03) && e.data &&
            [...e.data].includes(0x3f)) badText++;
        if (!e.status) continue;
        const hi = e.status & 0xf0, ch = e.status & 0x0f;
        if (hi === 0xb0 && e.a === 64) cc64ByChannel.set(ch, (cc64ByChannel.get(ch) || 0) + 1);
        if (hi === 0x90 && e.b > 0) {
          on++; noteChannels.add(ch);
          if (e.tick < firstTick) firstTick = e.tick;
          const k = ch + ':' + e.a;
          if (sounding.get(k)) overlaps.push(k + ' at tick ' + e.tick);
          sounding.set(k, true);
          held.set(k, (held.get(k) || 0) + 1);
        }
        if (hi === 0x80 || (hi === 0x90 && e.b === 0)) {
          off++; const k = ch + ':' + e.a;
          sounding.set(k, false);
          if (!held.get(k)) unmatched++; else held.set(k, held.get(k) - 1);
        }
      }
    }
    for (const v of held.values()) unmatched += v;
    const pedalChannels = [...cc64ByChannel.keys()].sort();
    const missingPedal = [...noteChannels].filter(c => !cc64ByChannel.has(c));
    console.log('  midi            ' + (bytes.length / 1024).toFixed(0) + ' kB, format ' + m.format +
                ', ' + m.tracks.length + ' tracks, ' + m.ppq + ' ppq, first note at tick ' + firstTick);
    console.log('  notes           ' + on + ' on / ' + off + ' off, ' + unmatched + ' unmatched · CC64 on channels [' +
                pedalChannels.join(',') + '] · ' + tempo + ' tempo · ' + timesig + ' time signature');
    const problems = [];
    if (unmatched) problems.push(unmatched + ' unmatched notes');
    if (!on) problems.push('no notes');
    if (!tempo) problems.push('no tempo map');
    if (!timesig) problems.push('no time signature, though the composer writes 3/4 and 5/4 bars');
    if (missingPedal.length) problems.push('channels ' + missingPedal.join(',') + ' carry notes but no pedal');
    if (overlaps.length) problems.push(overlaps.length + ' notes retrigger a pitch already sounding on the same channel (' + overlaps[0] + ')');
    if (badText) problems.push(badText + ' text metas contain a literal "?" where a non-ASCII character was flattened');
    if (firstTick > m.ppq * 8) problems.push('the file opens with ' + (firstTick / m.ppq).toFixed(0) + ' beats of silence');
    if (problems.length) fail('MIDI', problems.join('; '));
    else pass('MIDI', 'notes paired, tempo and meter present, pedal on every channel that carries notes, no retriggers, no lost characters');
    writeFileSync(path.join(OUT, 'improvisator-check.mid'), bytes);
  } catch (err) { fail('MIDI', 'could not parse the exported file: ' + err.message); }
}

/* --- bounce --- */
async function bounce (label, key) {
  await page.evaluate(() => { window.__blobs.length = 0; window.__wp = null; window.__w = null; });
  await page.keyboard.press(key || 'b');
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

/* --- LONG BOUNCE: a minute judges a texture, four judge a movement, and the
   long one has to stay linear. Scheduling a whole take before startRendering
   never lets a finished voice leave the graph, so the cost grows with the
   length: measured, the same four minutes takes 255 seconds that way -- slower
   than simply recording it -- against 42 with the render suspended every eight
   seconds. --- */
{
  const t0 = Date.now();
  const w4 = await bounce('long', 'Shift+B');
  const secs = w4.n / w4.rate;
  const wall = (Date.now() - t0) / 1000;
  console.log('  long bounce     ' + secs.toFixed(0) + ' s of music rendered in ' + wall.toFixed(1) +
              ' s (' + (secs / wall).toFixed(1) + 'x realtime)');
  if (secs < 200) fail('LONG BOUNCE', 'Shift+B produced ' + secs.toFixed(0) + ' s, not four minutes');
  else if (secs / wall < 1.5) fail('LONG BOUNCE', 'four minutes took ' + wall.toFixed(0) +
    ' s to render (' + (secs / wall).toFixed(1) + 'x realtime) — the offline render is not linear in the length');
  else pass('LONG BOUNCE', 'four minutes rendered at ' + (secs / wall).toFixed(1) + 'x realtime');
}

/* --- LAYOUT: every control has to be tappable at every size, with the settings
   panel open and shut. The panel opening squeezes the stage, and the play
   button sits above the console in paint order, so this is where a control
   ends up under another one and takes its taps. --- */
{
  const problems = [];
  /* Portrait AND landscape, and the short desktop windows an ordinary machine
     produces once a menu bar, browser chrome, a bookmarks bar and a dock are
     taken out of the screen. Six of these ten had an unreachable play button. */
  for (const [w, h, label] of [
    [320, 568, 'iPhone SE'], [568, 320, 'iPhone SE landscape'],
    [360, 640, 'small phone'], [390, 844, 'phone'], [844, 390, 'phone landscape'],
    [812, 375, 'iPhone X landscape'], [740, 420, 'small window'],
    [768, 1024, 'tablet'], [1440, 700, 'short desktop'], [1440, 900, 'desktop'],
  ]) {
    await page.setViewportSize({ width: w, height: h });
    await page.waitForTimeout(200);
    for (const open of [false, true]) {
      if (open) { await page.click('#settingsToggle').catch(() => {}); await page.waitForTimeout(220); }
      /* A control counts as reachable if a user can get to it: scroll it into
         view the way a browser does, then check that a tap at its centre lands
         on it. Both the stage and the console scroll, so testing without
         scrolling would condemn controls that are perfectly usable — and
         testing only the initial position would miss the ones that are not. */
      const r = await page.evaluate(async () => {
        const out = {}; const vw = innerWidth, vh = innerHeight;
        const ids = ['playButton', 'exportMidi', 'exportWav', 'newButton',
                     'tonicSelect', 'modeSelect', 'settingsToggle'];
        for (const id of ids) {
          const e = document.getElementById(id); if (!e) continue;
          let b = e.getBoundingClientRect();
          if (b.width === 0 || b.height === 0) continue;           /* deliberately hidden */
          if (b.width < 24 || b.height < 20) { out[id] = 'only ' + Math.round(b.width) + 'x' + Math.round(b.height) + ' px'; continue; }
          e.scrollIntoView({ block: 'center', inline: 'nearest' });
          await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
          b = e.getBoundingClientRect();
          if (b.bottom < 0 || b.top > vh || b.right < 0 || b.left > vw) { out[id] = 'cannot be scrolled into view'; continue; }
          const cx = Math.min(vw - 1, Math.max(1, b.left + b.width / 2));
          const cy = Math.min(vh - 1, Math.max(1, b.top + b.height / 2));
          const t = document.elementFromPoint(cx, cy);
          if (t && !e.contains(t) && !t.contains(e))
            out[id] = 'covered by ' + (t.id || t.className || t.tagName);
        }
        if (document.documentElement.scrollWidth > vw + 1) out.page = 'scrolls sideways';
        return out;
      });
      for (const [k, v] of Object.entries(r))
        problems.push(label + (open ? ' (panel open)' : '') + ' ' + k + ': ' + v);
      if (open) { await page.click('#settingsToggle').catch(() => {}); await page.waitForTimeout(150); }
    }
  }
  await page.setViewportSize({ width: 1280, height: 800 });
  if (problems.length) fail('LAYOUT', problems.slice(0, 4).join(' | ') + (problems.length > 4 ? ' …' + problems.length : ''));
  else pass('LAYOUT', 'every control is reachable at ten viewport sizes, panel open and shut');
}

/* --- KEYBOARD: a control that works with a mouse has to work with a keyboard.
   Space is how a focused button is activated; taking it globally made every
   character button mouse-only. And the `r` shortcut checked an inline style
   that the stylesheet never sets, so it started a real recording on a narrow
   window where the record button is hidden and there is no way to stop it. --- */
{
  const problems = [];
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.waitForTimeout(200);
  await page.evaluate(() => { const b = document.querySelector('.preset:not(.active)'); b && b.focus(); });
  const before = await page.evaluate(() => document.getElementById('statusText').textContent);
  const target = await page.evaluate(() => document.activeElement.dataset.preset);
  await page.keyboard.press('Space');
  await page.waitForTimeout(300);
  const after = await page.evaluate(() => ({
    status: document.getElementById('statusText').textContent,
    active: [...document.querySelectorAll('.preset')].filter(b => b.classList.contains('active'))
              .map(b => b.dataset.preset).join(','),
  }));
  if (after.status !== before) problems.push('space on a focused button toggled the transport instead of pressing it');
  if (after.active !== target) problems.push('space on a focused character button did not select it');

  await page.evaluate(() => document.activeElement.blur());
  await page.keyboard.press('Space');
  await page.waitForTimeout(400);
  const playing = await page.evaluate(() => document.getElementById('statusText').textContent);
  if (playing === before) problems.push('space with nothing focused did not reach the transport');
  await page.keyboard.press('Space');
  await page.waitForTimeout(300);

  await page.setViewportSize({ width: 500, height: 800 });
  await page.waitForTimeout(250);
  await page.evaluate(() => document.activeElement.blur());
  await page.keyboard.press('r');
  await page.waitForTimeout(400);
  const rec = await page.evaluate(() => document.getElementById('statusText').textContent);
  if (/record/i.test(rec)) problems.push('r started a recording at 500 px wide, where the record button is hidden');
  await page.setViewportSize({ width: 1280, height: 800 });

  if (problems.length) fail('KEYBOARD', problems.join(' | '));
  else pass('KEYBOARD', 'space activates the focused control and reaches the transport only when nothing is focused; r respects a hidden button');
}

/* --- errors --- */
console.log('  script errors   ' + (errors.length ? errors.slice(0, 4).join(' | ') : 'none'));
if (errors.length) fail('NO ERRORS', errors.length + ' console/page errors');
else pass('NO ERRORS', 'no console or page errors across the whole run');

await browser.close();
console.log('');
if (fails.length) { console.log('  verdict         FAIL — ' + fails.join(', ')); process.exit(1); }
console.log('  verdict         PASS');
