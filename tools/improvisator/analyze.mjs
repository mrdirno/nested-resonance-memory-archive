/* Improvisator ∞ — kernel analysis and gates.
   Loads the two logic <script> blocks out of the page and runs the composer
   headlessly, so every claim about the music is a measurement rather than a
   listen. Exits non-zero if a gate fails.

     node tools/improvisator/analyze.mjs [file] [--bars N] [--seed S] [--preset P]

   Author: Aldrin Payopay */

import { loadKernel, run, fingerprintBar, fingerprint, tensionOK, isDominantName } from './kernel.mjs';

/* ---------- small stats -------------------------------------------------- */

const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
const sd = a => { if (a.length < 2) return 0; const m = mean(a); return Math.sqrt(mean(a.map(x => (x - m) * (x - m)))); };
const pct = (a, p) => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * p))]; };
const pc = (n, d) => d ? (100 * n / d).toFixed(1) + '%' : 'n/a';
function tally (xs) { const m = new Map(); for (const x of xs) m.set(x, (m.get(x) || 0) + 1); return m; }
function topOf (m, n) {
  return [...m.entries()].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0])))
    .slice(0, n).map(([k, v]) => k + '×' + v).join('  ');
}

/* ---------- the report --------------------------------------------------- */

const argv = process.argv.slice(2);
const flag = (name, dflt) => { const i = argv.indexOf('--' + name); return i >= 0 ? argv[i + 1] : dflt; };
const FILE = argv.find(a => !a.startsWith('--') && !argv[argv.indexOf(a) - 1]?.startsWith('--'))
          || 'tools/improvisator/improvisator-infinite.html';
const BARS = Number(flag('bars', 256));
const SEED = flag('seed', 'grey-rain-0001');
const PRESET = flag('preset', 'reference');

const K = loadKernel(FILE);
const fails = [];
const fail = (gate, msg) => { fails.push(gate); console.log(gate.padEnd(14) + msg); };
const pass = (gate, msg) => console.log(gate.padEnd(14) + 'PASS — ' + msg);

const main = run(K, { seed: SEED, preset: PRESET, bars: BARS });
const events = main.bars.flatMap(b => b.events.map(e => ({ ...e, bar: b })));
const minutes = main.bars.reduce((t, b) => t + b.durationSeconds, 0) / 60;

console.log('IMPROVISATOR KERNEL REPORT');
console.log('  file          ' + FILE);
console.log('  build         soul v' + K.SOUL_VERSION + ' · ' + K.SOUL_BUILD);
console.log('  preset        ' + PRESET + '       seed ' + SEED + '       bars ' + BARS +
            '  (' + minutes.toFixed(1) + ' min)');
console.log('  fingerprint   ' + (K.hashString(fingerprint(main.bars)) >>> 0).toString(16));

/* --- validity --- */
const roles = tally(events.map(e => e.role));
const bad = [];
for (const e of events) {
  if (!Number.isFinite(e.pitch) || e.pitch < 12 || e.pitch > 108) bad.push('pitch ' + e.pitch);
  if (!Number.isFinite(e.beat) || e.beat < -0.01) bad.push('beat ' + e.beat);
  if (!Number.isFinite(e.duration) || e.duration <= 0) bad.push('duration ' + e.duration);
  if (!Number.isFinite(e.velocity) || e.velocity <= 0 || e.velocity > 1) bad.push('velocity ' + e.velocity);
  if (!Number.isFinite(e.micro) || Math.abs(e.micro) > 0.5) bad.push('micro ' + e.micro);
}
console.log('\nVALIDITY');
console.log('  events        ' + events.length + '   ' + [...roles.entries()].map(([k, v]) => k + ' ' + v).join('  '));
console.log('  problems      ' + (bad.length ? bad.slice(0, 6).join(', ') + (bad.length > 6 ? ' …' + bad.length : '') : 'none'));

/* --- harmony --- */
const names = tally(main.bars.map(b => b.chord.name));
const quals = tally(main.bars.map(b => b.chord.baseName || b.chord.name.replace(/\/.*$/, '')));
let outside = 0, sounding = 0;
for (const b of main.bars) {
  const scale = new Set(K.MODE_DEFS[b.mode].intervals.map(p => (p + b.tonic) % 12));
  for (const e of b.events) { sounding++; if (!scale.has(((e.pitch % 12) + 12) % 12)) outside++; }
}
const rhythm = tally(main.bars.map(b => b.chord.name));
console.log('\nHARMONY');
console.log('  qualities     ' + topOf(quals, 12));
console.log('  distinct      ' + quals.size + ' qualities, ' + names.size + ' chord names');
console.log('  chromatic     ' + pc(outside, sounding) + ' of sounding notes are outside the declared mode');
console.log('  keys          ' + topOf(tally(main.bars.map(b => K.NOTE_NAMES[b.tonic] + ' ' + b.mode)), 8));

/* --- register --- */
const bassEv = events.filter(e => e.role === 'bass');
const harmEv = events.filter(e => e.role === 'harmony');
const melEv = events.filter(e => e.role === 'melody');
const gaps = [];
for (const b of main.bars) {
  const lo = b.events.filter(e => e.role === 'bass').map(e => e.pitch);
  const up = b.events.filter(e => e.role !== 'bass').map(e => e.pitch);
  if (lo.length && up.length) gaps.push(Math.min(...up) - Math.max(...lo));
}
console.log('\nREGISTER');
console.log('  bass->voice   mean ' + mean(gaps).toFixed(2) + ' st   min ' + Math.min(...gaps) +
            '   p10 ' + pct(gaps, 0.10));
console.log('  harmony top   mean ' + mean(main.bars.map(b => {
  const h = b.events.filter(e => e.role === 'harmony').map(e => e.pitch); return h.length ? Math.max(...h) : NaN;
}).filter(Number.isFinite)).toFixed(2) +
  '   melody low mean ' + mean(main.bars.map(b => {
  const m = b.events.filter(e => e.role === 'melody').map(e => e.pitch); return m.length ? Math.min(...m) : NaN;
}).filter(Number.isFinite)).toFixed(2));
console.log('  melody range  ' + (melEv.length ? Math.min(...melEv.map(e => e.pitch)) + ' .. ' + Math.max(...melEv.map(e => e.pitch)) : 'none'));

/* --- space and line --- */
const silent = main.bars.filter(b => !b.events.some(e => e.role === 'melody')).length;
let runNow = 0, runMax = 0;
for (const b of main.bars) { if (!b.events.some(e => e.role === 'melody')) { runNow++; runMax = Math.max(runMax, runNow); } else runNow = 0; }
const melBar = main.bars.map(b => b.events.filter(e => e.role === 'melody').length);
const line = melEv.map(e => e.pitch);
const steps = [];
for (let i = 1; i < line.length; i++) steps.push(line[i] - line[i - 1]);
console.log('\nSPACE & LINE');
console.log('  silent bars   ' + pc(silent, main.bars.length) + '  (longest run ' + runMax + ' bars)');
console.log('  melody/bar    mean ' + mean(melBar).toFixed(2) + '   p90 ' + pct(melBar, 0.90));
console.log('  intervals     mean |leap| ' + mean(steps.map(Math.abs)).toFixed(2) +
            '   max ' + (steps.length ? Math.max(...steps.map(Math.abs)) : 0) +
            '   steps<=2 ' + pc(steps.filter(x => Math.abs(x) <= 2 && x !== 0).length, steps.length) +
            '   repeats ' + pc(steps.filter(x => x === 0).length, steps.length));

/* --- touch --- */
console.log('\nTOUCH');
for (const [name, set] of [['bass', bassEv], ['harmony', harmEv], ['melody', melEv]]) {
  if (!set.length) { console.log('  ' + name.padEnd(12) + 'no events'); continue; }
  const v = set.map(e => e.velocity), t = set.map(e => (e.micro || 0) * 1000);
  console.log('  vel ' + name.padEnd(9) + 'mean ' + mean(v).toFixed(2) + '  sd ' + sd(v).toFixed(2) +
              '  range ' + Math.min(...v).toFixed(2) + '..' + Math.max(...v).toFixed(2) +
              '   time mean ' + mean(t).toFixed(1) + ' ms  sd ' + sd(t).toFixed(1) + ' ms');
}
const bpms = main.bars.map(b => b.bpm);
console.log('  tempo         ' + Math.min(...bpms).toFixed(2) + ' .. ' + Math.max(...bpms).toFixed(2) +
            ' bpm  (sd ' + sd(bpms).toFixed(2) + ')');

/* --- rudiments --- */
/* Across every preset, because a rudiment can be reachable only at settings
   the reported preset does not use — and the bass family is named on the
   events rather than on the bar, which an earlier version of this report
   missed entirely and so declared eight rudiments dead that were not. */
{
  const seen = new Map();
  const note = id => { if (id) seen.set(id, (seen.get(id) || 0) + 1); };
  for (const preset of Object.keys(K.PRESETS)) {
    for (const sd5 of ['a-1', 'b-2', 'c-3']) {
      for (const b of run(K, { seed: sd5, preset, bars: 96 }).bars) {
        note(b.melodyRudiment && b.melodyRudiment.id);
        note(b.timingRudiment && b.timingRudiment.id);
        note(b.hand);
        note(b.pedal && b.pedal.id);
        for (const e of b.events) if (e.role === 'bass') note(e.gesture);
      }
    }
  }
  const never = K.RUDIMENTS.filter(r => !seen.has(r.id));
  const byFamily = new Map();
  for (const r of K.RUDIMENTS) {
    const k = r.family;
    const v = byFamily.get(k) || { used: 0, total: 0 };
    v.total++; if (seen.has(r.id)) v.used++;
    byFamily.set(k, v);
  }
  console.log('\nRUDIMENTS');
  console.log('  used          ' + seen.size + ' of ' + K.RUDIMENTS.length +
              '   ' + [...byFamily.entries()].map(([k, v]) => k + ' ' + v.used + '/' + v.total).join('  '));
  const rare = [...seen.entries()].sort((a, b) => a[1] - b[1]).slice(0, 4);
  console.log('  rarest        ' + rare.map(([k, v]) => k + '×' + v).join('  '));
  console.log('  never fired   ' + (never.length ? never.map(r => r.id).join(' ') : 'none'));
  if (never.length > 2) fail('VOCABULARY', never.length + ' of ' + K.RUDIMENTS.length +
    ' rudiments are never selected at any preset or seed: ' + never.map(r => r.id).join(' '));
}

/* ================= gates ================================================= */
console.log('');

/* NO REPEAT — the invariant the owner asked for. No event may be a machine-made
   copy of another: no echo role, no voice carried across a bar line. */
{
  const echoes = events.filter(e => e.role === 'echo').length;
  const carried = main.bars.reduce((n, b) => n + (Array.isArray(b.carriedVoices) ? b.carriedVoices.length : (b.carriedVoices || 0)), 0);
  if (echoes || carried) fail('NO REPEAT', echoes + ' echo events and ' + carried +
    ' voices carried across a bar line — a sounding note must be struck, never inherited');
  else pass('NO REPEAT', 'no echo role and no voice carried across a bar line in ' + events.length + ' events');
}

/* HARMONY — an accompaniment attack is a chord tone, the bass, or an available
   tension. The one exception is the idiom: a short approach note in the bass
   that leans into the next bar's root. Anything else, and anything HELD, is a
   wrong note. Measured across every preset, not just the one being reported,
   because the bass rudiments that produce approach tones do not fire at all
   settings. */
{
  let wrong = 0, total = 0, approaches = 0;
  const worst = [];
  for (const preset of Object.keys(K.PRESETS)) {
    for (const sd3 of ['a-1', 'b-2', 'c-3']) {
      const r = run(K, { seed: sd3, preset, bars: 120 });
      for (let bi = 0; bi < r.bars.length; bi++) {
        const b = r.bars[bi], next = r.bars[bi + 1];
        const pcs = b.chord.pcs.map(p => ((p % 12) + 12) % 12);
        const domRoot = isDominantName(b.chord.name) ? ((b.chord.rootPc % 12) + 12) % 12 : null;
        for (const e of b.events) {
          if (e.role === 'melody') continue;
          total++;
          const p = ((e.pitch % 12) + 12) % 12;
          if (pcs.includes(p)) continue;
          if (tensionOK(pcs, p, domRoot)) continue;
          /* An approach note: short, near the end of the bar, and a step from
             the root that is about to arrive. */
          const short = e.duration <= 0.62;
          const late = e.beat >= b.meter - 1.2;
          const leansIn = next && Math.min(
            Math.abs(((p - next.chord.rootPc) % 12 + 12) % 12),
            12 - Math.abs(((p - next.chord.rootPc) % 12 + 12) % 12)) <= 2;
          if (short && late && leansIn) { approaches++; continue; }
          wrong++;
          if (worst.length < 4) worst.push(preset + ' ' + b.chord.name + ' + ' + K.NOTE_NAMES[p] +
            ' for ' + e.duration.toFixed(2) + ' beats (' + (e.gesture || e.role) + ')');
        }
      }
    }
  }
  const rate = total ? wrong / total : 0;
  const line = wrong + '/' + total + ' accompaniment attacks (' + (100 * rate).toFixed(2) +
               '%) are neither a chord tone, the bass, nor an available tension; ' +
               approaches + ' short approach notes allowed' + (worst.length ? '\n              worst ' + worst.join('; ') : '');
  if (rate > 0.001) fail('HARMONY', line); else console.log('HARMONY'.padEnd(14) + line);
}

/* TEXTURE — two things a listener notices before anything else: whether the
   bottom of the piano is muddy, and whether the tune is on top. Both measured
   at simultaneity across every preset, because both are about notes sounding
   together rather than notes written near each other. */
{
  let mud = 0, pairs = 0, buried = 0, structural = 0;
  const worst = [];
  for (const preset of Object.keys(K.PRESETS)) {
    for (const sd4 of ['a-1', 'b-2', 'c-3']) {
      for (const b of run(K, { seed: sd4, preset, bars: 96 }).bars) {
        const times = [...new Set(b.events.map(e => Math.round(e.beat * 24) / 24))];
        for (const t of times) {
          const on = b.events.filter(e => e.beat <= t + 1e-6 && e.beat + e.duration > t + 1e-6)
                             .slice().sort((x, y) => x.pitch - y.pitch);
          for (let i = 1; i < on.length; i++) {
            pairs++;
            const gap = on[i].pitch - on[i - 1].pitch;
            if (gap > 0 && gap < K.lowIntervalFloor(on[i - 1].pitch)) {
              mud++;
              if (worst.length < 3) worst.push(preset + ' ' + b.chord.name + ' ' +
                on[i-1].role + ' ' + on[i-1].pitch + ' + ' + on[i].role + ' ' + on[i].pitch + ' (gap ' + gap + ')');
            }
          }
        }
        for (const m of b.events) {
          if (m.role !== 'melody' || m.duration < 0.75 || m.velocity < 0.34) continue;
          structural++;
          const t = m.beat + 1e-6;
          if (b.events.some(e => e.role !== 'melody' && e.pitch > m.pitch &&
                                 e.beat <= t && e.beat + e.duration > t)) buried++;
        }
      }
    }
  }
  const mudRate = mud / pairs, buriedRate = buried / structural;
  console.log('TEXTURE'.padEnd(14) + 'muddy simultaneous pairs ' + mud + '/' + pairs +
              ' (' + (100 * mudRate).toFixed(2) + '%)   structural melody notes under the accompaniment ' +
              buried + '/' + structural + ' (' + (100 * buriedRate).toFixed(2) + '%)');
  if (mudRate > 0.04) fail('TEXTURE', 'the bottom of the instrument is muddy in ' +
    (100 * mudRate).toFixed(2) + '% of simultaneous pairs: ' + worst.join('; '));
  else if (buriedRate > 0.10) fail('TEXTURE', (100 * buriedRate).toFixed(2) +
    '% of structural melody notes have an accompaniment note sounding above them');
}

/* DETERMINISM — one seed, one performance. */
{
  const a = fingerprint(run(K, { seed: SEED, preset: PRESET, bars: 96 }).bars);
  const b = fingerprint(run(K, { seed: SEED, preset: PRESET, bars: 96 }).bars);
  if (a !== b) {
    const la = a.split('\n'), lb = b.split('\n');
    const i = la.findIndex((x, j) => x !== lb[j]);
    fail('DETERMINISM', 'the same seed played two different performances, first differing at bar ' + i);
  } else pass('DETERMINISM', 'same seed, identical performance');
}

/* RESET — a composer told to play a seed again plays it again. */
{
  const s = Object.assign({}, K.PRESETS[PRESET]);
  const c = new K.Composer(SEED, s);
  const first = []; for (let i = 0; i < 48; i++) first.push(fingerprintBar(c.nextBar()));
  c.reset(SEED, s);
  const again = []; for (let i = 0; i < 48; i++) again.push(fingerprintBar(c.nextBar()));
  if (first.join('\n') !== again.join('\n'))
    fail('RESET', 'a reused composer did not replay the seed (first differs at bar ' +
      first.findIndex((x, j) => x !== again[j]) + ')');
  else pass('RESET', 'a reused composer plays the seed exactly');
}

/* ONE PIECE — the page renders a seed three ways: through the transport, which
   plays sections pumped into a queue ahead of time; through the offline bounce,
   which builds a fresh composer and takes bars straight from it; and into a
   MIDI file. If pumping the queue changes the music, those are three different
   performances wearing the same seed. */
{
  const s = Object.assign({}, K.PRESETS[PRESET]);
  const straight = new K.Composer(SEED, s);
  const a = [];
  for (let i = 0; i < 64; i++) a.push(fingerprintBar(straight.nextBar()));

  const queued = new K.Composer(SEED, s);
  const b = [];
  for (let i = 0; i < 64; i++) {
    /* pump at an irregular rhythm, the way a frame loop actually does */
    if (i % 3 === 0) queued.pump(12);
    if (i % 7 === 0) queued.pump(20);
    b.push(fingerprintBar(queued.nextBar()));
  }
  const at = a.findIndex((x, i) => x !== b[i]);
  if (at >= 0) fail('ONE PIECE', 'the queued performance and the un-queued one differ from bar ' + at +
    ' — how far ahead the composer runs is changing what it writes');
  else pass('ONE PIECE', 'queued or not, a seed is one performance (64 bars compared)');

  /* And the search itself must not spend the player's randomness. */
  const easy = new K.Composer(SEED, s);
  const hard = new K.Composer(SEED, s);
  hard.validateSection = function (sec) { const v = K.Composer.prototype.validateSection.call(this, sec);
                                          return { score: Math.min(v.score, 87), issues: v.issues }; };
  const ea = [], ha = [];
  for (let i = 0; i < 24; i++) { ea.push(fingerprintBar(easy.nextBar())); ha.push(fingerprintBar(hard.nextBar())); }
  const differ = ea.filter((x, i) => x !== ha[i]).length;
  console.log('SEARCH'.padEnd(14) + 'quality ' + (main.composer.lastQuality ?? '?') +
              ' after ' + (main.composer.attempts ?? '?') + ' of ' + (K.SEARCH_BUDGET ?? '?') + ' attempts' +
              '   forcing every attempt to run changes ' + differ + '/24 bars');
}

/* PRESETS — every character survives a long run at several seeds. */
{
  const broken = [];
  for (const name of Object.keys(K.PRESETS)) {
    for (const sd2 of ['a-0001', 'b-0002', 'c-0003']) {
      try {
        const r = run(K, { seed: sd2, preset: name, bars: 96 });
        const ev = r.bars.flatMap(b => b.events);
        if (!ev.length) { broken.push(name + '/' + sd2 + ': no events'); continue; }
        for (const e of ev) if (!Number.isFinite(e.pitch) || !Number.isFinite(e.beat) || !(e.velocity > 0)) {
          broken.push(name + '/' + sd2 + ': invalid event'); break;
        }
      } catch (err) { broken.push(name + '/' + sd2 + ': ' + err.message); }
    }
  }
  if (broken.length) fail('PRESETS', broken.slice(0, 4).join(' | '));
  else pass('PRESETS', 'all ' + Object.keys(K.PRESETS).length + ' presets survive 96 bars × 3 seeds');
}

/* EDGE SETTINGS — both extremes of every continuous control, in every key and
   mode, still produce a playable bar. */
{
  const keys = Object.keys(K.PRESETS.reference).filter(k => typeof K.PRESETS.reference[k] === 'number' && k !== 'tonic' && k !== 'bpm');
  const broken = [];
  for (const extreme of [0, 1]) {
    const base = Object.assign({}, K.PRESETS.reference);
    for (const k of keys) base[k] = extreme;
    for (let tonic = 0; tonic < 12; tonic++) {
      for (const mode of K.MODE_KEYS) {
        try {
          const r = run(K, { seed: 'edge-' + extreme + '-' + tonic + '-' + mode, preset: 'reference',
                             bars: 8, settings: Object.assign({}, base, { tonic, mode }) });
          const ev = r.bars.flatMap(b => b.events);
          if (!ev.length) { broken.push(extreme + '/' + tonic + '/' + mode + ': silent'); continue; }
          for (const e of ev) if (!Number.isFinite(e.pitch) || !(e.velocity > 0) || !Number.isFinite(e.micro)) {
            broken.push(extreme + '/' + tonic + '/' + mode + ': invalid'); break;
          }
        } catch (err) { broken.push(extreme + '/' + tonic + '/' + mode + ': ' + err.message); }
      }
    }
  }
  if (broken.length) fail('EDGE SETTINGS', broken.slice(0, 4).join(' | ') + (broken.length > 4 ? ' …' + broken.length : ''));
  else pass('EDGE SETTINGS', 'both extremes × 12 keys × ' + K.MODE_KEYS.length + ' modes produce valid events');
}

/* PRESET IDENTITY — a character button must actually change the performance.
   Measured through characterSettings(), which is what the page applies, not
   through the raw preset table: the page used to overwrite every musical
   dimension with the reference posture, so eight buttons produced the same
   player in eight keys. Two characters that differ only in a label are a lie
   in the interface. */
{
  const rows = [];
  for (const name of Object.keys(K.PRESETS)) {
    const settings = K.characterSettings(name);
    const r = run(K, { seed: 'identity-0001', preset: name, bars: 48, settings });
    const ev = r.bars.flatMap(b => b.events);
    const mel = ev.filter(e => e.role === 'melody');
    rows.push({
      name,
      body: JSON.stringify(Object.keys(settings).filter(k => k !== 'tonic' && k !== 'mode')
        .sort().map(k => k + '=' + settings[k])),
      notes: ev.length,
      melody: mel.length,
      tonics: new Set(r.bars.map(b => b.tonic)).size,
      voices: (ev.filter(e => e.role === 'harmony').length / r.bars.length).toFixed(1),
    });
  }
  const bodies = new Map();
  for (const r of rows) bodies.set(r.body, [...(bodies.get(r.body) || []), r.name]);
  const collapsed = [...bodies.values()].filter(g => g.length > 1);
  if (collapsed.length) fail('PRESET IDENTITY', collapsed.map(g => g.join('=')).join(' | ') +
    ' — these characters differ only in key and mode; every other setting is identical');
  else pass('PRESET IDENTITY', 'each of the ' + rows.length + ' characters has settings of its own');
  console.log('  per character ' + rows.map(r => r.name.slice(0, 4) + ' ' + r.notes + 'n/' + r.melody + 'm').join('  '));

  /* And they must sound different, not merely be configured differently. */
  const spread = Math.max(...rows.map(r => r.melody)) / Math.max(1, Math.min(...rows.map(r => r.melody)));
  if (spread < 1.4) fail('PRESET IDENTITY', 'the busiest character carries only ' + spread.toFixed(2) +
    'x the melody of the sparsest — the settings differ but the music does not');
}

console.log('');
if (fails.length) { console.log(fails.length + ' GATE' + (fails.length > 1 ? 'S' : '') + ' FAILED: ' + fails.join(', ')); process.exit(1); }
console.log('all gates pass');
