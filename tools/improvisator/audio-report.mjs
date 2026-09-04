/* Improvisator ∞ — what the bounce actually sounds like, in numbers.
   Reads a 16-bit WAV and reports level, balance, stereo width, band energy and
   onset density, so a claim about the sound can be checked instead of asserted.

   usage: node tools/improvisator/audio-report.mjs a.wav [b.wav]
   Author: Aldrin Payopay
*/
import { readFileSync } from 'node:fs';

function load(path) {
  const b = readFileSync(path);
  if (b.toString('ascii', 0, 4) !== 'RIFF') throw new Error(path + ': not a RIFF file');
  let off = 12, fmt = null, data = null;
  while (off + 8 <= b.length) {
    const id = b.toString('ascii', off, off + 4), size = b.readUInt32LE(off + 4);
    if (id === 'fmt ') fmt = { ch: b.readUInt16LE(off + 10), sr: b.readUInt32LE(off + 12), bits: b.readUInt16LE(off + 22) };
    if (id === 'data') data = { start: off + 8, size: Math.min(size, b.length - off - 8) };
    off += 8 + size + (size & 1);
  }
  if (!fmt || !data || fmt.bits !== 16) throw new Error(path + ': need 16-bit PCM');
  const frames = Math.floor(data.size / 2 / fmt.ch);
  const L = new Float32Array(frames), R = new Float32Array(frames);
  for (let i = 0; i < frames; i++) {
    L[i] = b.readInt16LE(data.start + i * fmt.ch * 2) / 32768;
    R[i] = fmt.ch > 1 ? b.readInt16LE(data.start + i * fmt.ch * 2 + 2) / 32768 : L[i];
  }
  return { L, R, sr: fmt.sr, frames };
}

/* one-pole band splits — enough to say "is the low end eating the mix" */
function bands(x, sr) {
  const out = { low: 0, mid: 0, high: 0 };
  let lp1 = 0, lp2 = 0, hp = 0, prev = 0;
  const aLow = Math.exp(-2 * Math.PI * 250 / sr);
  const aMid = Math.exp(-2 * Math.PI * 2500 / sr);
  for (let i = 0; i < x.length; i++) {
    lp1 = lp1 * aLow + x[i] * (1 - aLow);           /* < 250 Hz */
    lp2 = lp2 * aMid + x[i] * (1 - aMid);           /* < 2.5 kHz */
    hp = x[i] - lp2;                                 /* > 2.5 kHz */
    out.low += lp1 * lp1; out.mid += (lp2 - lp1) * (lp2 - lp1); out.high += hp * hp;
    prev = x[i];
  }
  const t = out.low + out.mid + out.high || 1;
  return { low: out.low / t, mid: out.mid / t, high: out.high / t };
}

/* spectral centroid via zero-crossing-weighted energy — cheap and monotonic */
function centroid(x, sr) {
  let num = 0, den = 0;
  for (let i = 1; i < x.length; i++) {
    const d = x[i] - x[i - 1];
    num += d * d; den += x[i] * x[i];
  }
  return den > 0 ? (sr / (2 * Math.PI)) * Math.sqrt(num / den) : 0;
}

/* Onsets. A pedalled piano's sustain smears low-frequency energy, so the
   attacks are counted on the high-passed signal where the hammer transient
   lives, against a running mean of that same band. */
function onsets(x, sr) {
  const a = Math.exp(-2 * Math.PI * 1200 / sr);
  const hp = new Float32Array(x.length);
  let lp = 0;
  for (let i = 0; i < x.length; i++) { lp = lp * a + x[i] * (1 - a); hp[i] = x[i] - lp; }
  const hop = Math.floor(sr * 0.008), win = hop * 2;
  const env = [];
  for (let i = 0; i + win < hp.length; i += hop) {
    let s = 0; for (let j = i; j < i + win; j++) s += hp[j] * hp[j];
    env.push(Math.sqrt(s / win));
  }
  let peak = 0; for (const v of env) if (v > peak) peak = v;
  const floor = peak * 0.012;
  let count = 0, avg = 0, held = 0;
  for (let i = 1; i < env.length; i++) {
    avg = avg * 0.90 + env[i] * 0.10;
    if (held > 0) { held--; continue; }
    if (env[i] > avg * 1.5 && env[i] > env[i - 1] * 1.25 && env[i] > floor) { count++; held = 2; }
  }
  return { count, perMinute: count / (x.length / sr) * 60, env };
}

function report(path) {
  const { L, R, sr, frames } = load(path);
  const mono = new Float32Array(frames), side = new Float32Array(frames);
  let peak = 0, sum = 0, clipped = 0;
  for (let i = 0; i < frames; i++) {
    mono[i] = (L[i] + R[i]) / 2; side[i] = (L[i] - R[i]) / 2;
    const a = Math.max(Math.abs(L[i]), Math.abs(R[i]));
    if (a > peak) peak = a;
    if (a >= 0.9995) clipped++;
    sum += mono[i] * mono[i];
  }
  const rms = Math.sqrt(sum / frames);
  let sideE = 0, midE = 0;
  for (let i = 0; i < frames; i++) { sideE += side[i] * side[i]; midE += mono[i] * mono[i]; }
  const b = bands(mono, sr), on = onsets(mono, sr);

  /* short-term loudness spread: how much the piece breathes */
  const blockN = Math.floor(sr * 0.4);
  const blocks = [];
  for (let i = 0; i + blockN < frames; i += blockN) {
    let s = 0; for (let j = i; j < i + blockN; j++) s += mono[j] * mono[j];
    blocks.push(20 * Math.log10(Math.max(1e-7, Math.sqrt(s / blockN))));
  }
  blocks.sort((p, q) => p - q);
  const q = f => blocks[Math.min(blocks.length - 1, Math.floor(f * blocks.length))];
  const db = x => (20 * Math.log10(Math.max(1e-9, x))).toFixed(1);

  return {
    path, seconds: frames / sr, sr,
    peak: db(peak), rms: db(rms), crest: (20 * Math.log10(peak / rms)).toFixed(1), clipped,
    width: (sideE / (midE || 1)).toFixed(3),
    low: (b.low * 100).toFixed(1), mid: (b.mid * 100).toFixed(1), high: (b.high * 100).toFixed(1),
    centroid: centroid(mono, sr).toFixed(0),
    onsetsPerMin: on.perMinute.toFixed(0),
    dynQuiet: q(0.05).toFixed(1), dynLoud: q(0.95).toFixed(1),
    dynRange: (q(0.95) - q(0.05)).toFixed(1),
  };
}

const rows = process.argv.slice(2).map(report);
const cols = ['seconds', 'peak', 'rms', 'crest', 'clipped', 'width', 'low', 'mid', 'high', 'centroid', 'onsetsPerMin', 'dynQuiet', 'dynLoud', 'dynRange'];
const labels = {
  seconds: 'length s', peak: 'peak dBFS', rms: 'rms dBFS', crest: 'crest dB', clipped: 'clipped',
  width: 'side/mid', low: '<250Hz %', mid: '250-2.5k %', high: '>2.5k %', centroid: 'centroid Hz',
  onsetsPerMin: 'attacks/min', dynQuiet: 'p5 loud dB', dynLoud: 'p95 loud dB', dynRange: 'dyn range dB',
};
console.log('\nAUDIO REPORT');
rows.forEach((r, i) => console.log(`  [${i}] ${r.path}`));
console.log('');
console.log('  ' + 'metric'.padEnd(14) + rows.map((_, i) => `[${i}]`.padStart(12)).join(''));
for (const c of cols) console.log('  ' + labels[c].padEnd(14) + rows.map(r => String(r[c]).padStart(12)).join(''));
console.log('');
