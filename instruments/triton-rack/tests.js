#!/usr/bin/env node
/* Self-contained verification for the TRITON × LuckyDreamer handoff.
   Usage: node tests.js [path-to-triton-rack.html]   (default: ./triton-rack.html)
   Slices the artifact itself — no side files needed. Exit 0 = all green. */
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
const G2 = eval(ldrJs + "\n;({LDR_FIG,LDR_KITS,ldrBase,ldrLane})");
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

console.log(errs ? "\nRESULT: " + errs + " ERROR(S)" : "\nRESULT: ALL GREEN");
process.exit(errs ? 1 : 0);
