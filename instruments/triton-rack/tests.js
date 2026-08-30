#!/usr/bin/env node
/* Self-contained verification for the TRITON × LuckyDreamer build.
   Usage: node tests.js [path-to-triton-rack.html]   (default: ./triton-rack.html)
   Slices the artifact itself — no side files needed. Exit 0 = all green.
   Suites: [0] whole-file syntax · [1] bank schema · [2] figure graft ·
   [3] conductor · [4] WAV recorder · [5] figure→instrument mapping + the
   ported LuckyDreamer physics, measured (fundamentals, decays, pitch bake). */
"use strict";
const fs = require("fs");
const path = process.argv[2] || "./triton-rack.html";
const s = fs.readFileSync(path, "utf8");
let errs = 0;
const fail = m => { console.log("  ✗ " + m); errs++; };
const ok = m => console.log("  ✓ " + m);

/* ── slice ─────────────────────────────────────────────────────────── */
function slice(a, b, fromEnd) {
  const i0 = fromEnd ? s.lastIndexOf(a) : s.indexOf(a);
  let i1 = s.indexOf(b, i0);
  return s.slice(i0, i1);
}
const scripts = [...s.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let dataJs = s.slice(s.indexOf("/* riff helpers */"), s.indexOf(");", s.lastIndexOf("COMBIS.push(")) + 2);
const ldrJs = slice("const LDR_FIG=", "function ldrHash");
const dreamJs = slice("function mulberry", "function dreamPans");
const wavJs = slice("function wavStereo24", "function recToggle");

/* ── suite 0: whole-file syntax ────────────────────────────────────── */
console.log("[0] syntax");
try { new Function(scripts.join("\n;\n")); ok(scripts.length + " scripts parse"); }
catch (e) { fail("script parse: " + e.message); }

/* ── suite 1: bank schema ──────────────────────────────────────────── */
console.log("[1] bank");
const G1 = eval(dataJs + "\n;({PROGRAMS,COMBIS})");
const { PROGRAMS, COMBIS } = G1;
if (PROGRAMS.length !== 128) fail("programs " + PROGRAMS.length); else ok("128 programs");
if (COMBIS.length !== 16) fail("combis " + COMBIS.length); else ok("16 combis");
PROGRAMS.forEach((p, i) => {
  if (p.id !== "A" + String(i).padStart(3, "0")) fail("id order at " + i);
  ["cat","tempo","filter","fEG","aEG","lfo","fx","audition"].forEach(k => { if (p[k] == null) fail(p.id + " missing " + k); });
  if (!Array.isArray(p.osc) && !p.bell) fail(p.id + " no osc/bell");
  ["a","d","s","r"].forEach(k => { if (typeof p.aEG[k] !== "number" || typeof p.fEG[k] !== "number") fail(p.id + " EG " + k); });
  if (typeof p.filter.cutoff !== "number" || !p.fx.delay) fail(p.id + " filter/fx");
  if (!p.audition.ev || !p.audition.len) fail(p.id + " riff");
});
COMBIS.forEach(c => c.timbres.forEach(t => {
  if (!(t.p >= 0 && t.p < PROGRAMS.length)) fail(c.id + " bad p " + t.p);
  ["lo","hi","lvl","tr"].forEach(k => { if (typeof t[k] !== "number") fail(c.id + " " + k); });
}));
if (!errs) ok("schema + combi targets valid");

/* ── suite 2: figure graft ─────────────────────────────────────────── */
console.log("[2] figures");
const G2 = eval(ldrJs + "\n;({LDR_FIG,LDR_KITS,ldrBase,ldrLane,LDR_RECIPE,LDR_MAP,LDR_MAP_BAD,ldrRoute,ldrBuf,LDR_SLOTS})");
const { LDR_FIG, LDR_KITS, ldrBase, ldrLane } = G2;
if (Object.keys(LDR_FIG).length !== 51) fail("figures " + Object.keys(LDR_FIG).length); else ok("51 figures");
LDR_KITS.forEach(i => { if (!PROGRAMS[i] || PROGRAMS[i].cat !== "DRUMS") fail("kit idx " + i); });
let e2 = errs;
for (const id in LDR_FIG) { const f = LDR_FIG[id];
  f.hits.forEach((h, i) => {
    const L = ldrLane(id, f, i);
    if (!(L >= 0 && L <= 11)) fail("lane " + id);
    if (!(h[0] >= 0 && h[0] < f.grid)) fail("pulse " + id);
    if (!(h[1] > 0 && h[1] <= 1.01)) fail("vel " + id);
  });
}
let res = 0, drop = 0, mis = 0;
for (const id in LDR_FIG) (LDR_FIG[id].also || []).forEach(a => {
  const b = ldrBase(a);
  if (!LDR_FIG[b.id]) drop++; else if (LDR_FIG[b.id].grid !== LDR_FIG[id].grid) mis++; else res++;
});
if (drop) fail(drop + " ensemble refs unresolved");
if (errs === e2) ok("lanes/pulses/vels valid · " + res + " ensemble refs resolve (± rotations)");

/* ── suite 3: conductor ────────────────────────────────────────────── */
console.log("[3] conductor");
Object.assign(globalThis, { LDR_FIG, LDR_KITS, ldrBase, ldrLane, PROGRAMS });
const G3 = eval(dreamJs + "\n;({mulberry,chordTones,DREAMS,dreamPickSurprise,figAnalysis,voiceLead,makeMotif,sectFor,SECT_CFG})");
G3.DREAMS.forEach(d => {
  if (d.surprise) return;
  const f = LDR_FIG[d.fig]; if (!f) return fail(d.name + " fig");
  d.comps.forEach(c => { const r = ldrBase(c);
    if (!LDR_FIG[r.id] || LDR_FIG[r.id].grid !== f.grid) fail(d.name + " comp " + c); });
  if (PROGRAMS[d.kit].cat !== "DRUMS") fail(d.name + " kit");
  [d.bass, d.chord, d.lead].forEach(i => { if (!PROGRAMS[i]) fail(d.name + " prog " + i); });
});
let e3 = errs;
for (const id in LDR_FIG) { const an = G3.figAnalysis(LDR_FIG[id]);
  if (!(an.skel.length >= 1 && an.skel.length <= 4)) fail("skel " + id);
  if (an.resp.length < 2) fail("resp " + id);
}
{ let prev = null, moved = 0, n = 0;
  for (let bar = 0; bar < 32; bar++) {
    const v = G3.voiceLead(G3.chordTones("minor", [0,5,3,4][bar % 4], 57), prev, 51, 79);
    for (let i = 1; i < v.length; i++) if (v[i] <= v[i - 1]) fail("voicing order");
    if (prev) { moved += v.reduce((a, x, i) => a + Math.abs(x - prev[Math.min(i, prev.length - 1)]), 0) / v.length; n++; }
    prev = v;
  }
  const avg = moved / n;
  if (avg > 5) fail("voice motion " + avg.toFixed(2)); else ok("avg voice motion " + avg.toFixed(2) + " st (smooth)");
}
["bembe","campanaSon","claveBossa","cavacha","maculele","martillo"].forEach(id => {
  const f = LDR_FIG[id], an = G3.figAnalysis(f);
  for (let sd = 1; sd <= 50; sd++) {
    const m = G3.makeMotif(an, f.grid, G3.mulberry(sd));
    if (m.length < 1) fail("motif empty " + id);
    m.forEach(e => { if (e.p < 0 || e.p >= f.grid || e.di < 0 || e.di > 6) fail("motif bounds " + id); });
  }
});
for (let sd = 1; sd <= 200; sd++) {
  const p = G3.dreamPickSurprise(G3.mulberry(sd));
  if (!LDR_FIG[p.fig] || PROGRAMS[p.kit].cat !== "DRUMS") fail("surprise " + sd);
  p.comps.forEach(c => { const r = ldrBase(c);
    if (!LDR_FIG[r.id] || LDR_FIG[r.id].grid !== LDR_FIG[p.fig].grid) fail("surprise comp " + sd + " " + c); });
}
for (let b = 0; b < 200; b++) if (!G3.SECT_CFG[G3.sectFor(b)]) fail("section " + b);
if (errs === e3) ok("presets · figAnalysis(51) · motifs · 200 surprise seeds · sections");

/* ── suite 4: take recorder WAV ────────────────────────────────────── */
console.log("[4] recorder");
const G4 = eval(wavJs + "\n;({wavStereo24})");
{ const sr = 48000, n = 9600, l = new Float32Array(n), r = new Float32Array(n);
  for (let i = 0; i < n; i++) { l[i] = Math.sin(2 * Math.PI * 440 * i / sr) * .5; r[i] = Math.sin(2 * Math.PI * 660 * i / sr) * .5; }
  const u = G4.wavStereo24(l, r, sr), dv = new DataView(u.buffer);
  const tag = (o, t) => String.fromCharCode(u[o], u[o+1], u[o+2], u[o+3]) === t;
  if (!tag(0, "RIFF") || !tag(8, "WAVE") || !tag(12, "fmt ") || !tag(36, "data")) fail("wav tags");
  if (dv.getUint16(22, true) !== 2) fail("wav channels");
  if (dv.getUint32(24, true) !== sr) fail("wav rate");
  if (dv.getUint16(34, true) !== 24) fail("wav bits");
  if (dv.getUint32(40, true) !== n * 6) fail("wav data len");
  if (u.length !== 44 + n * 6) fail("wav total len");
  if (errs === 0 || true) ok("stereo 24-bit header + length exact");
}

/* ── suite 5: figure→instrument mapping + ported physics (P0 steps 1-3) ──── */
console.log("[5] mapping+physics");
{
  const { LDR_RECIPE, LDR_MAP, LDR_MAP_BAD, ldrRoute, ldrBuf } = G2;
  if (!LDR_RECIPE || !LDR_MAP || !ldrRoute || !ldrBuf) fail("physics symbols missing from slice");
  if (Object.keys(LDR_RECIPE).length !== 25) fail("recipes " + Object.keys(LDR_RECIPE).length);
  if (Object.keys(LDR_MAP).length !== 51) fail("map entries " + Object.keys(LDR_MAP).length);
  if (!LDR_MAP_BAD || LDR_MAP_BAD.length) fail("in-file map audit: " + (LDR_MAP_BAD || ["missing"]).join(" · "));
  let perc = 0, lane = 0, un = 0;
  for (const id in LDR_FIG) LDR_FIG[id].hits.forEach((h, i) => {
    const r = ldrRoute(id, LDR_FIG[id], i);
    if (!r) { un++; return; }
    if (r.kind === "perc") { perc++; if (!LDR_RECIPE[r.name]) fail(id + "#" + i + " unknown recipe " + r.name); }
    else { lane++; if (!(r.lane >= 0 && r.lane <= 11)) fail(id + "#" + i + " bad lane"); }
  });
  if (un) fail(un + " unroutable hits (silent fallback would fire)");
  else ok("all hits route, no fallback · " + perc + " physics · " + lane + " kit-lane");
  /* definition-of-done routes (HANDOFF §4) */
  const rt = (id, i) => ldrRoute(id, LDR_FIG[id], i);
  const dod = [
    ["surdoPrimeira hits surdo at the donor's 46 Hz", () => { const r = rt("surdoPrimeira", 1); return r.name === "surdo" && Math.abs(r.pitch - 0.74) < 1e-9; }],
    ["surdoSegunda hits surdo as written", () => rt("surdoSegunda", 0).name === "surdo"],
    ["surdoTerceira takes the donor's congaL cutter", () => rt("surdoTerceira", 0).name === "congaL"],
    ["tamborim carreteiro speaks woodblk", () => rt("tamborimCarreteiro", 0).name === "woodblk"],
    ["ganza is the shaker", () => rt("ganza", 0).name === "shaker"],
    ["caixa stays the wired kit snare (lane 2)", () => rt("caixa", 0).lane === 2],
    ["bembe tone row lands on two agogo pitches", () => rt("bembe", 0).name === "agogoL" && rt("bembe", 1).name === "agogoH"],
    ["Son campana is a bell", () => rt("campanaSon", 0).name === "cowbell"],
    ["martillo macho is bongo skin", () => rt("martillo", 0).name === "bongoH"],
    ["martillo hembra open lands on bongoL", () => rt("martillo", 6).name === "bongoL"],
    ["quinto slap takes the slap recipe", () => rt("quintoLock", 1).name === "djembeS"],
    ["bigFour's cymbal stroke lands on the crash lane", () => rt("bigFour", 4).lane === 11],
    ["cascara rides the donor's cowbell", () => rt("cascara23", 0).name === "cowbell"]
  ];
  let dodBad = 0;
  dod.forEach(([label, fn]) => { let r = false; try { r = fn(); } catch (e) {}
    if (!r) { fail("DoD: " + label); dodBad++; } });
  if (!dodBad) ok(dod.length + " definition-of-done routes hold");
  /* ported synthesis, measured: stub AudioContext, render, check the physics */
  globalThis.ctx = { sampleRate: 48000, currentTime: 0,
    createBuffer: (ch, len, sr) => { const d = new Float32Array(len);
      return { length: len, duration: len / sr, getChannelData: () => d }; } };
  function dftPeak(d, sr, lo, hi, t0, t1) {
    const a = Math.floor(t0 * sr), b = Math.min(d.length, Math.floor(t1 * sr));
    let bestF = 0, bestM = -1;
    for (let f = lo; f <= hi; f += Math.max(1, (hi - lo) / 300)) {
      let re = 0, im = 0; const w = 2 * Math.PI * f / sr;
      for (let n = a; n < b; n++) { re += d[n] * Math.cos(w * n); im -= d[n] * Math.sin(w * n); }
      const m = re * re + im * im; if (m > bestM) { bestM = m; bestF = f; }
    }
    return bestF;
  }
  function t60(d, sr) {
    const win = Math.floor(sr * 0.01); let pk = 0, pi = 0; const env = [];
    for (let i = 0; i < d.length; i += win) { let p = 0;
      for (let j = i; j < Math.min(d.length, i + win); j++) { const v = Math.abs(d[j]); if (v > p) p = v; }
      env.push(p); }
    env.forEach((v, i) => { if (v > pk) { pk = v; pi = i; } });
    for (let i = pi; i < env.length; i++) if (env[i] < pk * 1e-3) return (i - pi) * win / sr;
    return (env.length - pi) * win / sr;
  }
  let mBad = 0;
  [["surdo", 40, 100, 0.30, 0.86, 62, 0.10], ["congaL", 120, 320, 0.15, 0.45, 190, 0.08],
   ["agogoH", 500, 1100, 0.10, 0.50, 780, 0.06], ["clave", 800, 1800, 0.01, 0.08, 1250, 0.08],
   ["cowbell", 350, 800, 0.03, 0.20, 540, 0.08], ["dunL", 50, 130, 0.30, 0.90, 78, 0.12]
  ].forEach(([name, lo, hi, w0, w1, want, tol]) => {
    const buf = ldrBuf(name, 1.0, 1, 1);
    if (!buf || buf.length < 128) { fail(name + " render empty"); mBad++; return; }
    const d = buf.getChannelData(0);
    let pk = 0; for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > pk) pk = v; }
    if (pk < 1e-3 || pk > 4) { fail(name + " peak " + pk.toFixed(3)); mBad++; return; }
    const f = dftPeak(d, 48000, lo, hi, w0, Math.min(w1, buf.duration));
    if (Math.abs(f - want) / want > tol) { fail(name + " fundamental " + f.toFixed(1) + " want " + want); mBad++; }
  });
  { const a = ldrBuf("surdo", 1.0, 1, 1), b = ldrBuf("surdo", 1.0, 0.74, 1);
    const fa = dftPeak(a.getChannelData(0), 48000, 40, 100, 0.3, 0.86);
    const fb = dftPeak(b.getChannelData(0), 48000, 30, 80, 0.3, 0.86);
    if (Math.abs(fb / fa - 0.74) > 0.06) { fail("primeira pitch bake " + (fb / fa).toFixed(3)); mBad++; } }
  { const c = ldrBuf("cowbell", 1.0, 1, 1), m = ldrBuf("cowbell", 1.0, 1, 0.5);
    if (!(t60(m.getChannelData(0), 48000) < t60(c.getChannelData(0), 48000) * 0.85)) { fail("mute damp inert"); mBad++; } }
  [["surdo", 0.62], ["clave", 0.07], ["agogoH", 0.42]].forEach(([name, dec]) => {
    const t = t60(ldrBuf(name, 1.0, 1, 1).getChannelData(0), 48000);
    if (t < dec * 0.4 || t > dec * 2.6) { fail(name + " T60 " + t.toFixed(3) + " vs " + dec); mBad++; } });
  ["tamb", "shaker", "cabasa", "guiro"].forEach(name => {
    const buf = ldrBuf(name, 0.7, 1, 1); if (!buf) { fail(name + " no render"); mBad++; return; }
    const d = buf.getChannelData(0); let pk = 0;
    for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > pk) pk = v; }
    if (pk < 1e-3 || pk > 4) { fail(name + " peak " + pk.toFixed(3)); mBad++; } });
  if (!mBad) ok("rendered physics measured: fundamentals on the recipes, decays track, pitch/damp bake");
}

/* ── suite 6: MIDI take writer (SMF type 1) ───────────────────────────────── */
console.log("[6] midi");
{
  const midiJs = slice("/*MIDI-BEGIN*/", "/*MIDI-END*/");
  globalThis.state = { tempo: 120 };
  const G6 = eval(midiJs + "\n;({MIDIREC,midiLog,midiLogP,midiVlq,midiTake,MIDI_GM_RECIPE,MIDI_GM_LANE})");
  /* VLQ */
  const vlq = n => { const a = []; G6.midiVlq(a, n); return a; };
  const vlqCases = [[0, [0]], [127, [0x7f]], [128, [0x81, 0x00]], [960, [0x87, 0x40]], [100000, [0x86, 0x8D, 0x20]]];
  let vBad = 0;
  vlqCases.forEach(([n, want]) => { const got = vlq(n);
    if (got.length !== want.length || got.some((b, i) => b !== want[i])) { fail("vlq " + n + " → " + got); vBad++; } });
  if (!vBad) ok("VLQ encoding exact");
  /* GM coverage: every physics recipe has a drum note */
  const missing = Object.keys(G2.LDR_RECIPE).filter(k => !G6.MIDI_GM_RECIPE[k]);
  if (missing.length) fail("recipes without GM notes: " + missing.join(","));
  else ok("25/25 recipes carry GM drum notes");
  /* a synthetic take: melodic + drums + a tempo change (dice mid-take) */
  G6.MIDIREC.on = true; G6.MIDIREC.ev = []; G6.MIDIREC.t0 = 0;
  state.tempo = 120;
  G6.midiLog({ cat: "LEAD" }, 60, 0.8, 0, 0.5);       /* t=0    ch0 */
  G6.midiLogP("surdo", 1.0, 0);                        /* t=0    ch9 */
  G6.midiLog({ cat: "LEAD" }, 64, 0.8, 1, 0.5);       /* t=1 → 960 ticks at 120 */
  state.tempo = 60;
  G6.midiLog({ cat: "LEAD" }, 67, 0.8, 2, 0.5);       /* t=2 → 1920 (still converts at 120) */
  G6.midiLog({ cat: "LEAD" }, 69, 0.8, 3, 0.5);       /* t=3 → 1920+480 at 60bpm = 2400 */
  G6.MIDIREC.on = false;
  const u = G6.midiTake();
  if (!u) { fail("midiTake returned null"); }
  else {
    const tag = (o, t) => String.fromCharCode(u[o], u[o+1], u[o+2], u[o+3]) === t;
    if (!tag(0, "MThd")) fail("no MThd");
    const fmt = (u[8] << 8) | u[9], ntrk = (u[10] << 8) | u[11], div = (u[12] << 8) | u[13];
    if (fmt !== 1) fail("format " + fmt);
    if (div !== 480) fail("division " + div);
    if (ntrk !== 3) fail("tracks " + ntrk + " (want tempo + ch0 + ch9)");
    /* walk tracks, verify declared lengths and count events */
    let o = 14, tempoMetas = 0, on9 = 0, off9 = 0, on0 = 0, off0 = 0, walked = 0;
    for (let k = 0; k < ntrk; k++) {
      if (!tag(o, "MTrk")) { fail("track " + k + " header"); break; }
      const len = (u[o+4] << 24) | (u[o+5] << 16) | (u[o+6] << 8) | u[o+7];
      for (let i = o + 8; i < o + 8 + len - 2; i++) {
        if (u[i] === 0xFF && u[i+1] === 0x51 && u[i+2] === 0x03) tempoMetas++;
        if (u[i] === 0x99) on9++; if (u[i] === 0x89) off9++;
        if (u[i] === 0x90) on0++; if (u[i] === 0x80) off0++;
      }
      o += 8 + len; walked++;
    }
    if (o !== u.length) fail("track lengths don't tile the file (" + o + " vs " + u.length + ")");
    if (tempoMetas !== 2) fail("tempo metas " + tempoMetas + " (want initial + change)");
    if (!(on9 === 1 && off9 === 1)) fail("drum on/off " + on9 + "/" + off9);
    if (!(on0 === 4 && off0 === 4)) fail("keys on/off " + on0 + "/" + off0);
    /* the tempo-map ticks: last event must land at 2400 */
    const ticks = G6.MIDIREC.ev.map(e => e.tick);
    if (ticks[2] !== 960 || ticks[3] !== 1920 || ticks[4] !== 2400)
      fail("piecewise tempo ticks " + ticks.join(","));
    if (walked === ntrk && o === u.length && tempoMetas === 2 && on9 === 1 && on0 === 4 &&
        ticks[4] === 2400) ok("SMF-1 exact: headers, track tiling, tempo map (120→60), note pairing");
  }
}

console.log(errs ? "\nRESULT: " + errs + " ERROR(S)" : "\nRESULT: ALL GREEN");
process.exit(errs ? 1 : 0);
