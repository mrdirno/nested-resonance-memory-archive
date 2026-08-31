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
const wavJs = slice("function wavStereo24", "function ldrDownload");

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
const G3 = eval(dreamJs + "\n;({mulberry,chordTones,DREAMS,dreamPickSurprise,romanFor,chordLabel,theoryData,figAnalysis,voiceLead,sectFor,SECT_CFG,PROG_BANK,chordSpecFor,labelTones,TH_IV,hv,hash01,valueNoise1,wander,humanTime,humanVel,HUM_COUPLE,HUM_LOOSE,LEAD_CELLS,CONTOURS,hookMake,hookBar,hookRealize,bassMake,LOCKS,lockMerge,presetValidate,presetParse})");
let e3 = errs; /* snapshot BEFORE the preset checks, so their failures gate the summary */
G3.DREAMS.forEach(d => {
  if (d.surprise) return;
  const f = LDR_FIG[d.fig]; if (!f) return fail(d.name + " fig");
  d.comps.forEach(c => { const r = ldrBase(c);
    if (!LDR_FIG[r.id] || LDR_FIG[r.id].grid !== f.grid) fail(d.name + " comp " + c); });
  if (PROGRAMS[d.kit].cat !== "DRUMS") fail(d.name + " kit");
  [d.bass, d.chord, d.lead].forEach(i => { if (!PROGRAMS[i]) fail(d.name + " prog " + i); });
});
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
{ /* the hook: drawn once, Q≠A, cells breathe, notes on the chord map, cadences voice-led */
  let hBad = 0;
  for (const grid of [12, 16]) {
    const h1 = G3.hookMake(42, grid), h2 = G3.hookMake(42, grid), h3 = G3.hookMake(43, grid);
    if (JSON.stringify(h1) !== JSON.stringify(h2)) { fail("hook not deterministic (" + grid + ")"); hBad++; }
    if (JSON.stringify(h1) === JSON.stringify(h3)) { fail("hook ignores seed (" + grid + ")"); hBad++; }
    if (h1.qi === h1.ai) { fail("Q and A must differ"); hBad++; }
    (G3.LEAD_CELLS[grid] || []).forEach((c, i) => {
      const sound = c.reduce((a, e) => a + Math.min(e.l, grid - e.p), 0);
      if (!(c.length <= 4 && sound <= grid * .72)) { fail("cell " + grid + "/" + i + " leaves no space (" + sound.toFixed(1) + ")"); hBad++; }
      for (let k = 1; k < c.length; k++) if (c[k].p <= c[k - 1].p) { fail("cell order " + grid + "/" + i); hBad++; }
      c.forEach(e => { if (e.p < 0 || e.p >= grid || e.l <= 0) { fail("cell bounds " + grid + "/" + i); hBad++; } });
    });
    const tones = G3.chordSpecFor("minor", 0, 57).tones, next = G3.chordSpecFor("minor", 4, 57).tones;
    const out = G3.hookRealize(h1.q, tones, next, h1);
    if (out.length !== h1.q.length) { fail("realize dropped notes"); hBad++; }
    const map = new Set();
    [0, 1, 2, 3].forEach(k => { map.add(tones[k]); map.add(tones[k] + 12); });
    [tones[0] + h1.color, tones[0] + h1.color + 12].forEach(x => map.add(x));
    out.forEach(e => {
      const okN = map.has(e.note) || (e.cad != null && Math.abs(e.note - e.cad) === 1);
      if (!okN) { fail("lead note off the map: " + e.note); hBad++; }
      if (e.cad != null) {
        const inNext = [0, 1, 2, 3].some(k => e.cad === next[k] || e.cad === next[k] + 12);
        if (!inNext) { fail("cadence target " + e.cad + " not in the next chord"); hBad++; }
      }
    });
    /* phrase grammar: BREAK fragments, bar2 answers with the other cell */
    const b0 = G3.hookBar(h1, 0, "GROOVE"), b2 = G3.hookBar(h1, 2, "GROOVE"), bk = G3.hookBar(h1, 1, "BREAK");
    if (b0.cell === b2.cell) { fail("answer bar re-states the question"); hBad++; }
    if (!(bk.dev === "fragment" && bk.cell.length <= 2)) { fail("BREAK does not fragment"); hBad++; }
  }
  const cs = new Set(); for (let s = 1; s <= 40; s++) cs.add(G3.hookMake(s, 16).contour);
  if (cs.size < 3) { fail("contour variety " + cs.size); hBad++; }
  if (!hBad) ok("the hook: deterministic identity, Q≠A, cells ≤72% air-time, notes on the chord map, cadences voice-led, BREAK fragments");
}
{ /* the bass cell: figure-anchored, chord-relative pool, opens and resolves home */
  let bBad = 0;
  const f = LDR_FIG["bembe"], an = G3.figAnalysis(f);
  const b1 = G3.bassMake(9, an, f.grid), b2 = G3.bassMake(9, an, f.grid);
  if (JSON.stringify(b1) !== JSON.stringify(b2)) { fail("bass cell not deterministic"); bBad++; }
  const POOL = [0, 7, 10, 12, 3, 5, -2];
  let opens = 0, openHome = 0;
  for (let s = 1; s <= 60; s++) {
    const b = G3.bassMake(s, an, f.grid);
    if (!(b.fires.length >= 1 && b.fires.length <= 6)) { fail("bass density " + b.fires.length); bBad++; }
    if (b.fires[0] > f.grid * .25) { fail("bass never opens (seed " + s + ")"); bBad++; }
    if (b.fires.length !== b.degs.length) { fail("bass cell shape"); bBad++; }
    b.degs.forEach(d => { if (POOL.indexOf(d) < 0) { fail("bass degree " + d); bBad++; } });
    for (let k = 1; k < b.fires.length; k++) if (b.fires[k] <= b.fires[k - 1]) { fail("bass order"); bBad++; }
    b.fires.forEach((p, i) => { if (p < f.grid * .2) { opens++; if (b.degs[i] === 0) openHome++; } });
  }
  if (!(opens > 0 && openHome / opens >= .5)) { fail("open-home intent missing (" + openHome + "/" + opens + ")"); bBad++; }
  if (!bBad) ok("the bass cell: deterministic, anchored on the figure, degrees in the pool, opens home " + (100 * openHome / opens | 0) + "%");
}
{ let sBad = 0;
  for (let sd = 1; sd <= 200; sd++) {
    const p = G3.dreamPickSurprise(G3.mulberry(sd));
    if (!LDR_FIG[p.fig] || PROGRAMS[p.kit].cat !== "DRUMS") fail("surprise " + sd);
    p.comps.forEach(c => { const r = ldrBase(c);
      if (!LDR_FIG[r.id] || LDR_FIG[r.id].grid !== LDR_FIG[p.fig].grid) fail("surprise comp " + sd + " " + c); });
    const bk = G3.PROG_BANK.find(b => b.name === p.progName);
    if (!bk || bk.prog !== p.prog || bk.scale !== p.scale) sBad++;
  }
  if (sBad) fail("surprise progressions not drawn from the bank (" + sBad + "/200)");
  else ok("DICE draws named progressions from the bank, scale-matched (200 seeds)");
}
for (let b = 0; b < 200; b++) if (!G3.SECT_CFG[G3.sectFor(b)]) fail("section " + b);
{ let tBad = 0;
  const VALID = ["", "maj7", "7", "m7", "m7\u266d5", "dim7", "mMaj7", "+", "m", "sus4"];
  G3.DREAMS.filter(d => !d.surprise).forEach(d => {
    const cells = G3.theoryData(d);
    if (cells.length !== d.prog.length) { fail("theory cells " + d.name); tBad++; }
    cells.forEach(c => {
      const mm = c.name.match(/^([A-G]#?)(.*)$/);
      if (!mm || VALID.indexOf(mm[2]) < 0) { fail("chord name " + c.name); tBad++; }
      if (c.tones.split(" ").length !== 4) { fail("tones " + c.tones); tBad++; }
      if (!c.roman) tBad++;
    });
  });
  if (G3.chordLabel("minor", 0, 45).name !== "Am7") { fail("A minor i should spell Am7"); tBad++; }
  if (G3.chordLabel("major", 4, 36).name !== "G7") { fail("C major V should spell G7"); tBad++; }
  if (G3.chordLabel("major", 0, 48).name !== "Cmaj7") { fail("C major I should spell Cmaj7"); tBad++; }
  if (G3.chordLabel("major", 6, 48).name !== "Bm7\u266d5") { fail("C major vii should spell Bm7\u266d5"); tBad++; }
  if (G3.romanFor(0, "minor") !== "i" || G3.romanFor(4, "major") !== "V" ||
      G3.romanFor(6, "major") !== "vii\u00b0") { fail("roman numerals wrong"); tBad++; }
  if (!tBad) ok("theory bar: romans + chord spelling (Am7 / G7 / Cmaj7 / Bm7\u266d5) across all dreams");
}
{ /* the progression bank \u2014 every entry structurally sound, the set functionally honest */
  let pBad = 0;
  const isSpec = ch => ch && typeof ch === "object" && Number.isInteger(ch.r) && ch.r >= 0 && ch.r <= 11 &&
    Array.isArray(ch.iv) && ch.iv.length === 4 && ch.iv.every((v, i) => Number.isInteger(v) && (i === 0 || v > ch.iv[i - 1])) &&
    typeof ch.roman === "string" && ch.roman.length > 0;
  G3.PROG_BANK.forEach(b => {
    if (!b.name || ["major", "minor"].indexOf(b.scale) < 0) { fail("bank entry " + b.name); pBad++; }
    if (!Array.isArray(b.prog) || b.prog.length < 4) { fail("bank prog short " + b.name); pBad++; }
    b.prog.forEach(ch => {
      if (typeof ch === "number" ? !(Number.isInteger(ch) && ch >= 0 && ch <= 6) : !isSpec(ch))
        { fail("bank chord " + b.name + " " + JSON.stringify(ch)); pBad++; }
    });
  });
  const majN = G3.PROG_BANK.filter(b => b.scale === "major").length;
  const minN = G3.PROG_BANK.filter(b => b.scale === "minor").length;
  if (majN < 4 || minN < 4) { fail("bank pools thin: " + majN + " major / " + minN + " minor"); pBad++; }
  const blues = G3.PROG_BANK.find(b => b.name === "12-bar blues");
  if (!blues || blues.prog.length !== 12 ||
      !blues.prog.every(ch => isSpec(ch) && ch.iv.join() === "0,4,7,10"))
    { fail("12-bar blues must be 12 bars of dominants"); pBad++; }
  /* the harmonic-minor V7: a chord the scale doesn't own, spelled and voiced right */
  const sp = G3.chordSpecFor("minor", { r: 7, iv: G3.TH_IV.d7, roman: "V7" }, 45);
  if (sp.tones.join() !== "52,56,59,62" || sp.roman !== "V7") { fail("V7 spec tones " + sp.tones.join()); pBad++; }
  const lb = G3.labelTones(sp.tones);
  if (lb.name !== "E7" || lb.tones !== "E G# B D") { fail("V7 label " + lb.name + " / " + lb.tones); pBad++; }
  /* named progressions realize to their textbook changes in A minor / C major */
  const names = (scale, root, prog) => G3.theoryData({ scale, root, prog }).map(c => c.name).join(" ");
  const bank = n => G3.PROG_BANK.find(b => b.name === n).prog;
  if (names("minor", 45, bank("andalusian")) !== "Am7 G7 Fmaj7 E7")
    { fail("andalusian: " + names("minor", 45, bank("andalusian"))); pBad++; }
  if (names("minor", 45, bank("minor ii-V-i")) !== "Bm7\u266d5 E7 Am7 Am7")
    { fail("minor ii-V-i: " + names("minor", 45, bank("minor ii-V-i"))); pBad++; }
  if (names("minor", 45, bank("dorian vamp")) !== "Am7 D7 Am7 D7")
    { fail("dorian vamp: " + names("minor", 45, bank("dorian vamp"))); pBad++; }
  if (names("major", 48, bank("jazz ii-V-I")) !== "Dm7 G7 Cmaj7 Cmaj7")
    { fail("jazz ii-V-I: " + names("major", 48, bank("jazz ii-V-I"))); pBad++; }
  /* the upgraded dream carries the cadence */
  const gua = G3.DREAMS.find(d => d.name === "Guaguanc\u00f3 Deep");
  if (!gua || gua.progName !== "andalusian" || !isSpec(gua.prog[3]) || gua.prog[3].roman !== "V7")
    { fail("Guaguanc\u00f3 Deep should cadence on a real V7"); pBad++; }
  /* voice leading stays smooth through borrowed chords (24 bars of blues) */
  { let prev = null, moved = 0, n = 0;
    for (let bar = 0; bar < 24; bar++) {
      const t = G3.chordSpecFor("major", blues.prog[bar % 12], 55).tones;
      const v = G3.voiceLead(t, prev, 49, 77);
      for (let i = 1; i < v.length; i++) if (v[i] <= v[i - 1]) { pBad++; }
      if (prev) { moved += v.reduce((a, x, i) => a + Math.abs(x - prev[Math.min(i, prev.length - 1)]), 0) / v.length; n++; }
      prev = v;
    }
    if (moved / n > 5) { fail("blues voice motion " + (moved / n).toFixed(2)); pBad++; }
  }
  if (!pBad) ok("progression bank: " + G3.PROG_BANK.length + " named changes (blues 12 bars of dominants, andalusian Am7 G7 Fmaj7 E7, minor ii-V-i, dorian) \u2014 specs sound, voices lead");
}
{ /* the drummer's clock: keyed, correlated, role-coupled, capped, hum-scaled */
  let cBad = 0;
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  const sd = a => { const m = mean(a); return Math.sqrt(mean(a.map(x => (x - m) * (x - m)))); };
  const lag1 = a => { const m = mean(a); let n = 0, d = 0;
    for (let i = 0; i + 1 < a.length; i++) n += (a[i] - m) * (a[i + 1] - m);
    for (const x of a) d += (x - m) * (x - m); return d ? n / d : 0; };
  const w1 = [], w2 = [];
  for (let b = 0; b < 256; b++) { w1.push(G3.wander(1234, b * .25)); w2.push(G3.wander(1234, b * .25)); }
  if (JSON.stringify(w1) !== JSON.stringify(w2)) { fail("wander not keyed/deterministic"); cBad++; }
  if (!w1.every(x => Math.abs(x) <= 3.05)) { fail("wander exceeds its bound"); cBad++; }
  if (!(lag1(w1) > .8)) { fail("wander not correlated (lag-1 " + lag1(w1).toFixed(2) + ")"); cBad++; }
  const off = role => { const o = []; for (let b = 0; b < 400; b++) o.push(G3.humanTime(77, role, b * .5, .15, 1)); return o; };
  const kitO = off("kit"), leadO = off("lead"), bassO = off("bass");
  [[kitO, "kit"], [leadO, "lead"], [bassO, "bass"]].forEach(([o, r]) => {
    if (!o.every(x => Math.abs(x) <= .15 * .333 + 1e-9)) { fail(r + " clock exceeds a third of a step"); cBad++; } });
  if (!(sd(leadO) > sd(kitO) * 1.25)) { fail("lead should float freer than the kit (" +
    sd(leadO).toFixed(4) + " vs " + sd(kitO).toFixed(4) + ")"); cBad++; }
  if (!(lag1(kitO) > .5)) { fail("kit clock not correlated (lag-1 " + lag1(kitO).toFixed(2) + ")"); cBad++; }
  if (Math.abs(G3.humanTime(77, "kit", 10, .15, 0)) > 1e-12) { fail("hum=0 must be machine-tight"); cBad++; }
  const v = []; for (let b = 0; b < 200; b++) v.push(G3.humanVel(77, "chord", b * .5, 1));
  if (!v.every(x => x > .8 && x < 1.2)) { fail("velocity breath out of range"); cBad++; }
  if (!(lag1(v) > .5)) { fail("velocity breath not correlated"); cBad++; }
  if (G3.hv(1.7) !== 1 || G3.hv(-2) !== .05) { fail("hv clamp"); cBad++; }
  if (!cBad) ok("the drummer's clock: keyed 1/f wander (lag-1 " + lag1(w1).toFixed(2) +
    "), kit tight / lead free (sd ×" + (sd(leadO) / sd(kitO)).toFixed(2) + "), ±⅓-step cap, hum=0 = machine");
}
{ /* locks: surgical halves; presets: hostile-file law */
  let lBad = 0;
  const cur = JSON.parse(JSON.stringify(G3.DREAMS[0]));   /* Bembé Rising */
  const nu0 = JSON.parse(JSON.stringify(G3.DREAMS[2]));   /* Son Nocturne */
  const kMerged = G3.lockMerge(JSON.parse(JSON.stringify(nu0)), cur, { key: true, rhythm: false });
  if (!(kMerged.scale === cur.scale && kMerged.root === cur.root &&
        JSON.stringify(kMerged.prog) === JSON.stringify(cur.prog) && kMerged.fig === nu0.fig &&
        kMerged.kit === nu0.kit)) { fail("key lock leaks: " + JSON.stringify({ s: kMerged.scale, f: kMerged.fig })); lBad++; }
  const rMerged = G3.lockMerge(JSON.parse(JSON.stringify(nu0)), cur, { key: false, rhythm: true });
  if (!(rMerged.fig === cur.fig && rMerged.kit === cur.kit && rMerged.tempo === cur.tempo &&
        rMerged.scale === nu0.scale && rMerged.root === nu0.root)) { fail("rhythm lock leaks"); lBad++; }
  const free = G3.lockMerge(JSON.parse(JSON.stringify(nu0)), cur, { key: false, rhythm: false });
  if (free.fig !== nu0.fig || free.scale !== nu0.scale) { fail("no-lock merge mutated the roll"); lBad++; }
  /* presets */
  const mkP = () => ({ name: "take one", seed: 42, p: JSON.parse(JSON.stringify(G3.DREAMS[0])) });
  if (!G3.presetValidate(mkP())) { fail("real preset refused"); lBad++; }
  const bads = [
    (e => { e.p.fig = "notafigure"; return e; })(mkP()),
    (e => { e.p.scale = "phrygian"; return e; })(mkP()),
    (e => { e.p.tempo = 999; return e; })(mkP()),
    (e => { e.name = "x".repeat(64); return e; })(mkP()),
    (e => { e.seed = -3; return e; })(mkP()),
    (e => { e.p.prog = [{ r: 99, iv: [0, 4, 7, 10], roman: "?" }]; return e; })(mkP()),
    (e => { e.p.kit = 0; return e; })(mkP()),
    (e => { e.p.comps = ["<img onerror=x>", 2]; return e; })(mkP()),
  ];
  bads.forEach((b, i) => { if (G3.presetValidate(b)) { fail("hostile preset " + i + " accepted"); lBad++; } });
  const mixedJson = JSON.stringify([mkP(), bads[0], mkP(), "junk"]);
  if (G3.presetParse(mixedJson).length !== 2) { fail("presetParse filter"); lBad++; }
  if (G3.presetParse("not json").length !== 0) { fail("presetParse garbage"); lBad++; }
  if (G3.presetParse(JSON.stringify(Array.from({ length: 12 }, mkP))).length !== 8) { fail("presetParse cap"); lBad++; }
  if (!lBad) ok("locks are surgical (key holds harmony, rhythm holds groove); presets validate, filter hostiles, cap at 8");
}
{ const audJs = slice("/*AUDVARY-BEGIN*/", "/*AUDVARY-END*/");
  const A = eval(audJs + "\n;({audVary})");
  const riff = { len: 8, ev: [[0, 60, .5, .8], [1, 64, .5, .7], [2, 67, .5, .9], [3, 72, 1, .6]] };
  let aBad = 0;
  for (let p = 1; p <= 40; p++) {
    const ev = A.audVary(riff, G3.mulberry(7919 * p + 1));
    if (ev.length < 4 || ev.length > 5) aBad++;
    ev.forEach(e => { if (e[0] < 0 || e[3] < 0.1 - 1e-9 || e[3] > 1 + 1e-9) aBad++; });
  }
  const a1 = JSON.stringify(A.audVary(riff, G3.mulberry(8)));
  const a2 = JSON.stringify(A.audVary(riff, G3.mulberry(8)));
  const a3 = JSON.stringify(A.audVary(riff, G3.mulberry(9)));
  if (a1 !== a2) aBad++;
  if (a1 === a3) aBad++;
  if (aBad) fail("audition improviser: " + aBad + " violations");
  else ok("audition improviser: bounded, deterministic per pass, different across passes");
}
if (errs === e3) ok("presets · figAnalysis(51) · motifs · 200 surprise seeds · sections");

/* ── suite 4: take recorder WAV ────────────────────────────────────── */
console.log("[4] recorder");
const e4 = errs;
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
  if (errs === e4) ok("stereo 24-bit header + length exact");
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
  const G6 = eval(midiJs + "\n;({TAKE,takeStart,takeStop,takeLog,takeLogP,takeClose,takeToMidiEvents,midiVlq,midiTake,MIDI_GM_RECIPE,MIDI_GM_LANE})");
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
  /* a synthetic take: player + drums + a tempo change (dice mid-take) */
  globalThis.ctx = globalThis.ctx || { currentTime: 0 };
  ctx.currentTime = 0;
  G6.takeStart();
  state.tempo = 120;
  G6.takeLog({ cat: "LEAD" }, 60, 0.8, 0, 0.5);        /* t=0    you */
  G6.takeLogP("surdo", 1.0, 0, {});                     /* t=0    perc→ch9 */
  G6.takeLog({ cat: "LEAD" }, 64, 0.8, 1, 0.5);        /* t=1 → 960 ticks at 120 */
  state.tempo = 60;
  G6.takeLog({ cat: "LEAD" }, 67, 0.8, 2, 0.5);        /* t=2 → 1920 (still converts at 120) */
  G6.takeLog({ cat: "LEAD" }, 69, 0.8, 3, 0.5);        /* t=3 → 1920+480 at 60bpm = 2400 */
  /* a HELD note: logged open, patched on release with the real duration */
  G6.takeLog({ cat: "KEYBOARD" }, 72, 0.8, 3.2, null);
  ctx.currentTime = 3.95;
  G6.takeClose(72);
  const held = G6.TAKE.ev[G6.TAKE.ev.length - 1];
  if (!(held.dur > 0.7 && held.dur < 0.8)) fail("held-note duration not patched: " + held.dur);
  else ok("held player note closes with its true duration (" + held.dur.toFixed(2) + "s)");
  G6.takeStop();
  const mapped = G6.takeToMidiEvents(G6.TAKE.ev);
  const u = G6.midiTake(mapped);
  if (!u) { fail("midiTake returned null"); }
  else {
    const tag = (o, t) => String.fromCharCode(u[o], u[o+1], u[o+2], u[o+3]) === t;
    if (!tag(0, "MThd")) fail("no MThd");
    const fmt = (u[8] << 8) | u[9], ntrk = (u[10] << 8) | u[11], div = (u[12] << 8) | u[13];
    if (fmt !== 1) fail("format " + fmt);
    if (div !== 480) fail("division " + div);
    if (ntrk !== 3) fail("tracks " + ntrk + " (want tempo + YOU + drums)");
    /* walk tracks, verify declared lengths and count events */
    let o = 14, tempoMetas = 0, meterMetas = 0, progCh = 0, on9 = 0, off9 = 0, on0 = 0, off0 = 0, walked = 0;
    for (let k = 0; k < ntrk; k++) {
      if (!tag(o, "MTrk")) { fail("track " + k + " header"); break; }
      const len = (u[o+4] << 24) | (u[o+5] << 16) | (u[o+6] << 8) | u[o+7];
      for (let i = o + 8; i < o + 8 + len - 2; i++) {
        if (u[i] === 0xFF && u[i+1] === 0x51 && u[i+2] === 0x03) tempoMetas++;
        if (u[i] === 0xFF && u[i+1] === 0x58 && u[i+2] === 0x04) meterMetas++;
        if (u[i] === 0xC0) progCh++;
        if (u[i] === 0x99) on9++; if (u[i] === 0x89) off9++;
        if (u[i] === 0x90) on0++; if (u[i] === 0x80) off0++;
      }
      o += 8 + len; walked++;
    }
    if (o !== u.length) fail("track lengths don't tile the file (" + o + " vs " + u.length + ")");
    if (tempoMetas !== 2) fail("tempo metas " + tempoMetas + " (want initial + change)");
    if (meterMetas !== 1) fail("meter meta missing (donor writer carries 4/4)");
    if (progCh !== 1) fail("GM preview program changes " + progCh + " (want 1 on the YOU track)");
    if (!(on9 === 1 && off9 === 1)) fail("drum on/off " + on9 + "/" + off9);
    if (!(on0 === 5 && off0 === 5)) fail("player on/off " + on0 + "/" + off0);
    const ticks = mapped.map(e => e.tick);
    if (ticks[2] !== 960 || ticks[3] !== 1920 || ticks[4] !== 2400)
      fail("piecewise tempo ticks " + ticks.join(","));
    if (walked === ntrk && o === u.length && tempoMetas === 2 && meterMetas === 1 &&
        progCh === 1 && on9 === 1 && on0 === 5 && ticks[4] === 2400)
      ok("SMF-1 exact: headers, tiling, tempo map (120→60), meter, GM preview, note pairing");
  }
  /* lead-in silence must survive, so the .mid lines up with the paired .wav */
  ctx.currentTime = 0;
  G6.takeStart(); state.tempo = 120;
  G6.takeLogP("clave", 0.8, 0.5, {});
  G6.takeStop();
  const m2 = G6.takeToMidiEvents(G6.TAKE.ev);
  G6.midiTake(m2);
  if (m2[0].tick !== 480) fail("lead-in dropped: first tick " + m2[0].tick + " (want 480)");
  else ok("lead-in preserved: 0.5 s of silence = 480 ticks @120");
}

/* ── suite 7: User Bank B (validator + file round-trip) ──────────────────── */
console.log("[7] bank B");
{
  const bankJs = slice("/*BANKB-BEGIN*/", "/*BANKB-END*/");
  const G7 = eval(bankJs + "\n;({progValidate,bankParse})");
  let bBad = 0;
  [0, 15, 63, 99, 127].forEach(i => { if (!G7.progValidate(PROGRAMS[i])) { fail("real program " + i + " refused"); bBad++; } });
  const mut1 = JSON.parse(JSON.stringify(PROGRAMS[5])); delete mut1.aEG;
  if (G7.progValidate(mut1)) { fail("missing aEG accepted"); bBad++; }
  const mut2 = JSON.parse(JSON.stringify(PROGRAMS[5])); mut2.filter.cutoff = "loud";
  if (G7.progValidate(mut2)) { fail("string cutoff accepted"); bBad++; }
  const mut3 = JSON.parse(JSON.stringify(PROGRAMS[5])); delete mut3.audition;
  if (G7.progValidate(mut3)) { fail("missing audition accepted"); bBad++; }
  const mut4 = JSON.parse(JSON.stringify(PROGRAMS[5])); mut4.osc = [{ w: {}, lvl: 0.5 }];
  if (G7.progValidate(mut4)) { fail("non-string osc wave accepted"); bBad++; }
  const mut5 = JSON.parse(JSON.stringify(PROGRAMS[5])); delete mut5.tempo;
  if (G7.progValidate(mut5)) { fail("missing tempo accepted"); bBad++; }
  const bank = new Array(16).fill(null);
  bank[3] = JSON.parse(JSON.stringify(PROGRAMS[7]));
  bank[9] = JSON.parse(JSON.stringify(PROGRAMS[40]));
  const parsed = G7.bankParse(JSON.stringify({ v: 1, bank }));
  if (!parsed || parsed.length !== 16 || parsed.filter(Boolean).length !== 2 ||
      parsed[3].id !== "B003" || parsed[9].id !== "B009") { fail("bank round-trip"); bBad++; }
  const dirty = new Array(20).fill(null);
  dirty[0] = JSON.parse(JSON.stringify(PROGRAMS[1]));
  dirty[2] = { name: "junk" };
  dirty[17] = JSON.parse(JSON.stringify(PROGRAMS[2]));   /* beyond 16 — must drop */
  const p2 = G7.bankParse(JSON.stringify({ v: 1, bank: dirty }));
  if (!p2 || p2.length !== 16 || p2.filter(Boolean).length !== 1) { fail("dirty bank filter"); bBad++; }
  if (G7.bankParse("]nope") !== null) { fail("garbage json accepted"); bBad++; }
  if (!bBad) ok("real programs pass, mutants/junk/overflow refused, slot ids stamped");
}

console.log(errs ? "\nRESULT: " + errs + " ERROR(S)" : "\nRESULT: ALL GREEN");
process.exit(errs ? 1 : 0);
