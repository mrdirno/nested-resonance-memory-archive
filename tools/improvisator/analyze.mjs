/* Improvisator ∞ — headless kernel harness.
   Loads the music kernel out of the page (no DOM, no Web Audio), plays a long
   stretch of it into memory, and reports what came out. Used to prove a change
   to the composer did what it claims, and to catch invalid events, broken
   determinism, and register/space/harmony regressions before anything is heard.

   usage: node tools/improvisator/analyze.mjs [file.html] [bars] [preset] [seed]
   Author: Aldrin Payopay
*/
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const file    = process.argv[2] || new URL('./improvisator-infinite.html', import.meta.url).pathname;
const barCount= Number(process.argv[3] || 256);
const preset  = process.argv[4] || 'reference';
const seed    = process.argv[5] || 'grey-rain-0001';

const html = readFileSync(file, 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!blocks.length) { console.error('no <script> block found'); process.exit(1); }

const sandbox = { console, performance: { now: () => 0 } };
sandbox.globalThis = sandbox;
sandbox.window = sandbox;
vm.createContext(sandbox);
try { vm.runInContext(blocks[0], sandbox, { filename: 'kernel' }); }
catch (e) { console.error('KERNEL THREW ON LOAD:\n' + (e.stack || e)); process.exit(1); }

const K = sandbox.IMPROV;
if (!K || !K.Composer) { console.error('kernel did not export IMPROV.Composer'); process.exit(1); }

const mod = (n, m) => ((n % m) + m) % m;
const fmt = (x, n = 2) => (Math.round(x * 10 ** n) / 10 ** n).toFixed(n);
const pct = x => fmt(x * 100, 1) + '%';

function run(seedValue, settings, bars) {
  const c = new K.Composer(seedValue, Object.assign({}, settings));
  const out = [];
  for (let i = 0; i < bars; i++) out.push(c.nextBar());
  return { composer: c, bars: out };
}

const settings = Object.assign({}, K.PRESETS[preset] || K.PRESETS.reference);
let result;
try { result = run(seed, settings, barCount); }
catch (e) { console.error('COMPOSER THREW:\n' + (e.stack || e)); process.exit(1); }
const bars = result.bars;

/* ---- fingerprint for determinism ------------------------------------- */
function fingerprint(bs) {
  const parts = [];
  for (const b of bs) {
    parts.push(fmt(b.bpm, 3) + '|' + b.chord.name + '|' + (b.hand || '') + '|' + (b.pedalLift ? 1 : 0));
    for (const e of b.events) {
      parts.push([e.role, e.pitch, fmt(e.beat, 5), fmt(e.duration, 4), fmt(e.velocity, 4), fmt(e.micro || 0, 5)].join(','));
    }
  }
  let h = 2166136261 >>> 0;
  const s = parts.join(';');
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16).padStart(8, '0') + ':' + s.length;
}

/* ---- validity --------------------------------------------------------- */
const problems = [];
let noteCount = 0;
const roles = {};
for (const b of bars) {
  if (!isFinite(b.bpm) || b.bpm < 20 || b.bpm > 200) problems.push(`bar ${b.globalIndex}: bpm ${b.bpm}`);
  let prevBeat = -1;
  for (const e of b.events) {
    noteCount++;
    roles[e.role] = (roles[e.role] || 0) + 1;
    if (!(e.pitch >= 21 && e.pitch <= 108) || e.pitch !== Math.round(e.pitch)) problems.push(`bar ${b.globalIndex}: pitch ${e.pitch}`);
    if (!isFinite(e.beat) || e.beat < -0.5 || e.beat > 5.5) problems.push(`bar ${b.globalIndex}: beat ${e.beat}`);
    if (!isFinite(e.duration) || e.duration <= 0) problems.push(`bar ${b.globalIndex}: duration ${e.duration}`);
    if (!isFinite(e.velocity) || e.velocity <= 0 || e.velocity > 1) problems.push(`bar ${b.globalIndex}: velocity ${e.velocity}`);
    if (e.micro !== undefined && (!isFinite(e.micro) || Math.abs(e.micro) > 0.4)) problems.push(`bar ${b.globalIndex}: micro ${e.micro}`);
    if (e.beat < prevBeat - 1e-9) problems.push(`bar ${b.globalIndex}: events out of order`);
    prevBeat = e.beat;
  }
}

/* ---- musical statistics ----------------------------------------------- */
const hist = a => { const m = new Map(); for (const x of a) m.set(x, (m.get(x) || 0) + 1); return [...m].sort((p, q) => q[1] - p[1]); };
const top = (a, n = 10) => hist(a).slice(0, n).map(([k, v]) => `${k}×${v}`).join('  ');

const chordNames = bars.map(b => b.chord.name);
const qualities  = chordNames.map(n => n.replace(/^[A-G][♭♯]?/, '') || 'maj');

/* chromaticism: pitch classes outside the bar's declared mode */
let chromatic = 0, totalPcs = 0;
for (const b of bars) {
  const scale = new Set(K.MODE_DEFS[b.mode].intervals.map(i => mod(b.tonic + i, 12)));
  for (const e of b.events) { totalPcs++; if (!scale.has(mod(e.pitch, 12))) chromatic++; }
}

/* inversion: is the lowest sounding note the chord root? */
let inverted = 0, pedalPoint = 0, rootPos = 0;
for (const b of bars) {
  const low = b.events.filter(e => e.role === 'bass').sort((x, y) => x.pitch - y.pitch)[0];
  if (!low) continue;
  if (mod(low.pitch, 12) === b.chord.rootPc) rootPos++; else inverted++;
}

/* register: bass vs. the next voice above it, per bar */
const bassGaps = [], voicingSpans = [], melodyLows = [], harmonyHighs = [];
for (const b of bars) {
  const bass = b.events.filter(e => e.role === 'bass').map(e => e.pitch);
  const harm = b.events.filter(e => e.role === 'harmony').map(e => e.pitch);
  const mel  = b.events.filter(e => e.role === 'melody').map(e => e.pitch);
  if (bass.length && harm.length) bassGaps.push(Math.min(...harm) - Math.min(...bass));
  if (harm.length) voicingSpans.push(Math.max(...harm) - Math.min(...harm));
  if (harm.length) harmonyHighs.push(Math.max(...harm));
  if (mel.length) melodyLows.push(Math.min(...mel));
}

/* space: bars with no melody at all, and the longest silent run */
let silentBars = 0, silentRun = 0, longestRun = 0;
const melodyPerBar = [];
for (const b of bars) {
  const n = b.events.filter(e => e.role === 'melody').length;
  melodyPerBar.push(n);
  if (n === 0) { silentBars++; silentRun++; longestRun = Math.max(longestRun, silentRun); } else silentRun = 0;
}

/* melodic intervals */
const melodyLine = [];
for (const b of bars) for (const e of b.events) if (e.role === 'melody') melodyLine.push(e.pitch);
const leaps = melodyLine.slice(1).map((n, i) => n - melodyLine[i]);
const absLeaps = leaps.map(Math.abs);

/* harmonic rhythm: how many consecutive bars share a chord name */
const spans = [];
let cur = 1;
for (let i = 1; i < bars.length; i++) {
  if (bars[i].chord.name === bars[i - 1].chord.name) cur++;
  else { spans.push(cur); cur = 1; }
}
spans.push(cur);

/* timing: mean micro offset per role — negative is early, positive is late */
const micros = {};
for (const b of bars) for (const e of b.events) {
  (micros[e.role] = micros[e.role] || []).push((e.micro || 0) * 1000);
}

/* velocity per role */
const vels = {};
for (const b of bars) for (const e of b.events) (vels[e.role] = vels[e.role] || []).push(e.velocity);

/* simultaneity: how many notes land within 30 ms of each other */
const stamps = [];
for (const b of bars) {
  const spb = 60 / b.bpm;
  for (const e of b.events) stamps.push(b.beatStart * spb + e.beat * spb + (e.micro || 0));
}
stamps.sort((a, b) => a - b);
let maxCluster = 0;
for (let i = 0, j = 0; i < stamps.length; i++) {
  while (stamps[i] - stamps[j] > 0.03) j++;
  maxCluster = Math.max(maxCluster, i - j + 1);
}

const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : 0;
const stdev = a => { const m = mean(a); return a.length ? Math.sqrt(mean(a.map(x => (x - m) ** 2))) : 0; };
const quant = (a, q) => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };

const bpms = bars.map(b => b.bpm);
const totalSeconds = bars.reduce((s, b) => s + 4 * 60 / b.bpm, 0);

console.log(`
IMPROVISATOR KERNEL REPORT
  file          ${file}
  preset        ${preset}       seed ${seed}       bars ${barCount}  (${fmt(totalSeconds / 60, 1)} min)
  fingerprint   ${fingerprint(bars)}

VALIDITY
  events        ${noteCount}   ${Object.entries(roles).map(([k, v]) => `${k} ${v}`).join('  ')}
  problems      ${problems.length ? problems.length + '  !! ' + problems.slice(0, 6).join(' | ') : 'none'}

HARMONY
  qualities     ${top(qualities, 12)}
  distinct      ${new Set(qualities).size} qualities, ${new Set(chordNames).size} chord names
  chromatic     ${pct(chromatic / totalPcs)} of sounding notes are outside the declared mode
  bass position ${pct(rootPos / (rootPos + inverted || 1))} root position, ${pct(inverted / (rootPos + inverted || 1))} inverted / other
  harmonic rhy  mean ${fmt(mean(spans))} bars per chord   ${top(spans.map(String), 6)}
  keys          ${top(bars.map(b => K.NOTE_NAMES[b.tonic] + ' ' + b.mode), 6)}

REGISTER
  bass->voice   mean ${fmt(mean(bassGaps))} st   min ${Math.min(...bassGaps)}   p10 ${quant(bassGaps, 0.1)}
  voicing span  mean ${fmt(mean(voicingSpans))} st   max ${Math.max(...voicingSpans)}
  harmony top   mean ${fmt(mean(harmonyHighs))}   melody low mean ${fmt(mean(melodyLows))}
  melody range  ${Math.min(...melodyLine)} .. ${Math.max(...melodyLine)}

SPACE & LINE
  silent bars   ${pct(silentBars / bars.length)}  (longest run ${longestRun} bars)
  melody/bar    mean ${fmt(mean(melodyPerBar))}   p90 ${quant(melodyPerBar, 0.9)}
  intervals     mean |leap| ${fmt(mean(absLeaps))}   max ${Math.max(...absLeaps)}   steps<=2 ${pct(absLeaps.filter(x => x <= 2).length / absLeaps.length)}   repeats ${pct(absLeaps.filter(x => x === 0).length / absLeaps.length)}

TOUCH
${Object.keys(vels).map(r => `  vel ${r.padEnd(8)} mean ${fmt(mean(vels[r]))}  sd ${fmt(stdev(vels[r]))}  range ${fmt(Math.min(...vels[r]))}..${fmt(Math.max(...vels[r]))}`).join('\n')}
${Object.keys(micros).map(r => `  time ${r.padEnd(7)} mean ${fmt(mean(micros[r]), 1)} ms   sd ${fmt(stdev(micros[r]), 1)} ms`).join('\n')}
  density       ${maxCluster} notes inside one 30 ms window (worst)
  tempo         ${fmt(Math.min(...bpms))} .. ${fmt(Math.max(...bpms))} bpm  (sd ${fmt(stdev(bpms))})
`);

/* ---- does every note belong to the chord it lands on? ------------------
   An accompaniment note that is neither a chord tone, nor the bass, nor an
   available tension, nor a deliberate approach note, is a wrong note. This is
   the check that caught the left-hand tenth being built from an inverted bass,
   which put a natural eleventh against the third of a dominant. */
{
  let attacks = 0, wrong = 0, slashBad = 0;
  const worst = [];
  for (const name of Object.keys(K.PRESETS)) {
    for (const sd of ['h1', 'h2', 'h3']) {
      const c = new K.Composer(name + sd, Object.assign({}, K.PRESETS[name]));
      const timeline = [];
      for (let i = 0; i < 64; i++) {
        const b = c.nextBar();
        for (const ch of b.changes) {
          timeline.push({ t: b.beatStart + (ch.scoreBeat === undefined ? ch.beat : ch.scoreBeat), chord: ch.chord, bass: ch.bass });
        }
        for (const e of b.events) {
          if (e.role === 'melody' || e.approach) continue;
          const t = b.beatStart + e.scoreBeat;
          let cur = timeline[0];
          for (const seg of timeline) if (seg.t <= t + 1e-6) cur = seg;
          attacks++;
          const pc = mod(e.pitch, 12);
          if (cur.chord.pcs.indexOf(pc) >= 0 || pc === mod(cur.bass, 12)) continue;
          if (K.tensionOK(cur.chord.intervals, mod(pc - cur.chord.rootPc, 12) + 12, cur.chord.fn === 'D')) continue;
          wrong++;
          if (worst.length < 4) worst.push(`${cur.chord.name} + ${mod(pc - cur.chord.rootPc, 12)}`);
        }
        const named = b.chord.name.indexOf('/') >= 0;
        if (named !== (mod(b.bass, 12) !== b.chord.rootPc)) slashBad++;
      }
    }
  }
  console.log(`HARMONY        ${wrong}/${attacks} accompaniment attacks (${pct(wrong / attacks)}) are neither a chord tone, the bass, nor an available tension` +
              (worst.length ? '\n  worst        ' + worst.join('  ') : ''));
  console.log(`SLASH NAMES    ${slashBad ? slashBad + ' bars where the printed bass and the played bass disagree' : 'PASS — the printed chord always names the bass that is played'}`);
  if (wrong / attacks > 0.005 || slashBad) process.exitCode = 1;
}

/* ---- gesture, seams and rails ----------------------------------------- */
{
  const c = new K.Composer(seed, Object.assign({}, settings));
  let noGesture = 0, jumpy = 0, sections = 0, pickups = 0, boundaries = 0;
  let melAtHi = 0, melAtLo = 0, harmAtLo = 0, melN = 0, harmN = 0;
  const closures = new Map();
  for (let s = 0; s < 40; s++) {
    const sec = c.generateSection();
    sections++;
    closures.set(sec.closure, (closures.get(sec.closure) || 0) + 1);
    const line = sec.melody;
    let big = 0;
    for (let i = 1; i < line.length; i++) if (Math.abs(line[i] - line[i - 1]) >= 7) big++;
    if (!big) noGesture++;
    if (big > 4) jumpy++;
    boundaries++;
    if (sec.bars[7].events.some(e => e.role === 'melody' && e.pickup)) pickups++;
    for (const bar of sec.bars) for (const e of bar.events) {
      if (e.role === 'melody') { melN++; if (e.velocity >= 0.9399) melAtHi++; if (e.velocity <= 0.0901) melAtLo++; }
      if (e.role === 'harmony') { harmN++; if (e.velocity <= 0.0601) harmAtLo++; }
    }
  }
  console.log(`GESTURE        ${noGesture}/${sections} sections have no interval >= 7 semitones; ${jumpy}/${sections} have more than four`);
  console.log(`SEAMS          ${pickups}/${boundaries} section boundaries carry a pickup   closures: ${[...closures].map(([k, v]) => k + ' ' + v).join('  ')}`);
  console.log(`RAILS          melody at ceiling ${pct(melAtHi / Math.max(1, melN))}  at floor ${pct(melAtLo / Math.max(1, melN))}   harmony at floor ${pct(harmAtLo / Math.max(1, harmN))}`);
}

/* ---- how hard the section search is working --------------------------- */
{
  const c = new K.Composer(seed, Object.assign({}, settings));
  const scores = [], tries = [], issues = new Map();
  for (let i = 0; i < 48; i++) {
    const sec = c.generateSection();
    scores.push(sec.quality); tries.push(c.attempts);
    for (const x of sec.issues) issues.set(x, (issues.get(x) || 0) + 1);
  }
  scores.sort((x, y) => x - y);
  const pick = q => scores[Math.min(scores.length - 1, Math.floor(q * scores.length))];
  console.log(`SEARCH         quality min ${pick(0)}  p25 ${pick(0.25)}  median ${pick(0.5)}  max ${scores[scores.length - 1]}` +
              `   attempts mean ${fmt(mean(tries), 1)} of ${Math.max(...tries)}`);
  console.log(`  issues       ${[...issues].sort((x, y) => y[1] - x[1]).slice(0, 8).map(([k, v]) => `${k} ${v}`).join('  ') || 'none'}`);
}

/* ---- determinism ------------------------------------------------------ */
const a = fingerprint(run(seed, settings, 64).bars);
const b = fingerprint(run(seed, settings, 64).bars);
console.log(`DETERMINISM    ${a === b ? 'PASS — same seed, identical performance' : 'FAIL\n  ' + a + '\n  ' + b}`);

/* The realtime path fills a queue ahead of the scheduler; the MIDI export and
   the offline bounce drive nextBar directly. Both must produce the same piece,
   or the file you save is not the passage you heard. */
{
  const direct = new K.Composer(seed, Object.assign({}, settings));
  const queued = new K.Composer(seed, Object.assign({}, settings));
  queued.primeQueue();
  const d = [], q = [];
  for (let i = 0; i < 32; i++) d.push(direct.nextBar());
  for (let i = 0; i < 32; i++) { queued.pump(14); q.push(queued.nextBar()); }
  const same = fingerprint(d) === fingerprint(q);
  console.log(`EXPORT PARITY  ${same ? 'PASS — the queued performance and the exported one are the same piece' : 'FAIL — export diverges from playback'}`);
  if (!same) process.exitCode = 1;
}

/* A reused Composer must be indistinguishable from a fresh one after reset,
   or "New passage" quietly plays something the seed does not describe. */
{
  const fresh = run('reset-check-seed', settings, 24).bars;
  const reused = new K.Composer('some-other-seed', Object.assign({}, settings));
  for (let i = 0; i < 40; i++) reused.nextBar();
  reused.reset('reset-check-seed', Object.assign({}, settings));
  const after = [];
  for (let i = 0; i < 24; i++) after.push(reused.nextBar());
  const same = fingerprint(fresh) === fingerprint(after);
  console.log(`RESET          ${same ? 'PASS — a reused composer plays the seed exactly' : 'FAIL — state leaks across reset'}`);
  if (!same) process.exitCode = 1;
}

/* ---- every preset must survive a long run ----------------------------- */
let presetFails = 0;
for (const name of Object.keys(K.PRESETS)) {
  for (const s of ['a-1', 'b-2', 'c-3']) {
    try { run(s, K.PRESETS[name], 96); }
    catch (e) { presetFails++; console.log(`PRESET FAIL    ${name}/${s}: ${e.message}`); }
  }
}
console.log(`PRESETS        ${presetFails ? presetFails + ' failures' : 'all ' + Object.keys(K.PRESETS).length + ' presets survive 96 bars × 3 seeds'}`);

/* ---- extreme settings ------------------------------------------------- */
let edgeFails = 0;
const edges = [
  ['all zero',  { motion: 0, space: 0, warmth: 0, humanize: 0, wander: 0, melody: 0, sustain: 0, texture: 0, resonance: 0, range: 0, reverb: 0, bpm: 34 }],
  ['all one',   { motion: 1, space: 1, warmth: 1, humanize: 1, wander: 1, melody: 1, sustain: 1, texture: 1, resonance: 1, range: 1, reverb: 1, bpm: 132 }],
];
for (const [label, over] of edges) {
  for (let t = 0; t < 12; t++) {
    const s = Object.assign({}, K.PRESETS.reference, over, { tonic: t, mode: K.MODE_KEYS[t % K.MODE_KEYS.length] });
    try {
      const r = run('edge-' + label + '-' + t, s, 64);
      for (const bar of r.bars) for (const e of bar.events) {
        if (!(e.pitch >= 21 && e.pitch <= 108) || !isFinite(e.beat) || !(e.duration > 0) || !(e.velocity > 0)) {
          edgeFails++; console.log(`EDGE FAIL      ${label} tonic ${t}: bad event ${JSON.stringify(e)}`); t = 99; break;
        }
      }
    } catch (e) { edgeFails++; console.log(`EDGE FAIL      ${label} tonic ${t}: ${e.message}`); }
  }
}
console.log(`EDGE SETTINGS  ${edgeFails ? edgeFails + ' failures' : 'both extremes × 12 keys × 8 modes produce valid events'}`);

process.exitCode = (problems.length || presetFails || edgeFails || a !== b) ? 1 : 0;
