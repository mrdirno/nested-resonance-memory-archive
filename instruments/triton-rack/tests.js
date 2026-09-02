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
if (Object.keys(LDR_FIG).length < 51) fail("figures " + Object.keys(LDR_FIG).length + " (floor 51)"); else ok(Object.keys(LDR_FIG).length + " figures (floor 51)");
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
const G3 = eval(dreamJs + "\n;({mulberry,chordTones,DREAMS,dreamPickSurprise,romanFor,chordLabel,theoryData,figAnalysis,voiceLead,sectFor,SECT_CFG,PROG_BANK,chordSpecFor,labelTones,TH_IV,hv,hash01,valueNoise1,wander,humanTime,humanVel,HUM_COUPLE,HUM_LOOSE,LEAD_CELLS,CONTOURS,hookMake,hookBar,hookRealize,bassMake,LOCKS,lockMerge,presetValidate,presetParse,TRAITS,candDrums,candBass,candChords,candLead,FORMATS,candFor,composeP,DREAM,PHRASES,PHRASE_IDX,phrasePick,ldrpUnpackDrum,ldrpUnpackMel,ldrpGrooveField,ldrpFitScale,LDRP2KIT,LDRP_LANES})");
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
{ /* the song avatar: five trait slots, prebuilt pieces, composed honestly */
  let aBad = 0;
  if (!(Array.isArray(G3.TRAITS) && G3.TRAITS.length === 5)) { fail("five traits, no more"); aBad++; }
  for (let s = 1; s <= 40; s++) {
    const d = G3.candDrums(G3.mulberry(s));
    if (!LDR_FIG[d.fig] || PROGRAMS[d.kit].cat !== "DRUMS" || !(d.tempo >= 40 && d.tempo <= 300) ||
        !(d.seed >= 1) || !d.name) { fail("drummer card " + s + " invalid"); aBad++; }
    d.comps.forEach(c => { const r = ldrBase(c);
      if (!LDR_FIG[r.id] || LDR_FIG[r.id].grid !== LDR_FIG[d.fig].grid) { fail("drummer comps " + s); aBad++; } });
    const b = G3.candBass(G3.mulberry(s * 7 + 1));
    if (!(b.root >= 40 && b.root <= 49) || PROGRAMS[b.bass].cat !== "BASS" || !SCALES_OK(b.scale)) { fail("bass card " + s); aBad++; }
    const c = G3.candChords(G3.mulberry(s * 13 + 2), b);
    const bk = G3.PROG_BANK.find(x => x.name === c.progName);
    if (!bk || bk.scale !== b.scale || bk.prog !== c.prog || !PROGRAMS[c.chord]) { fail("chords card " + s + " off the bank"); aBad++; }
    const l = G3.candLead(G3.mulberry(s * 17 + 3));
    if (!PROGRAMS[l.lead] || !(l.lseed >= 1)) { fail("lead card " + s); aBad++; }
  }
  function SCALES_OK(x){ return x === "minor" || x === "major"; }
  if (!(G3.FORMATS.length === 3 && G3.FORMATS.every(f => ["loop", "arc", "song"].includes(f.format)))) { fail("formats"); aBad++; }
  const d1 = JSON.stringify(G3.candDrums(G3.mulberry(9))), d2 = JSON.stringify(G3.candDrums(G3.mulberry(9)));
  if (d1 !== d2) { fail("cards not deterministic per stream"); aBad++; }
  /* composition: honest mutes, kept overrides, the drummer is the clock */
  const kd = G3.candDrums(G3.mulberry(4)), kb = G3.candBass(G3.mulberry(5)),
        kc = G3.candChords(G3.mulberry(6), kb), kl = G3.candLead(G3.mulberry(7));
  const p0 = G3.composeP([null,null,null,null,null], kd, 0);
  if (!(p0.muteBass && p0.muteChord && p0.muteLead && p0._building && p0._seed === kd.seed &&
        p0.fig === kd.fig)) { fail("stage-0 compose " + JSON.stringify({m:p0.muteBass,b:p0._building})); aBad++; }
  const p1 = G3.composeP([kd,null,null,null,null], kb, 1);
  if (!(!p1.muteBass && p1.muteChord && p1.root === kb.root && p1.bseed === kb.bseed &&
        p1.fig === kd.fig && p1._seed === kd.seed)) { fail("stage-1 compose"); aBad++; }
  const p2 = G3.composeP([kd,kb,null,null,null], kc, 2);
  if (!(!p2.muteChord && p2.muteLead && p2.progName === kc.progName && p2.root === kb.root)) { fail("stage-2 compose"); aBad++; }
  const pF = G3.composeP([kd,kb,kc,kl,G3.FORMATS[1]], null, 5);
  if (!(pF && !pF.muteBass && !pF.muteChord && !pF.muteLead && pF.format === "arc" && !pF._building &&
        pF.lseed === kl.lseed && G3.presetValidate({name:"t",seed:kd.seed,p:JSON.parse(JSON.stringify(pF))})))
    { fail("full compose not keepable"); aBad++; }
  if (G3.composeP([null,null,null,null,null], null, 1) !== null) { fail("compose without a drummer"); aBad++; }
  /* the shape governs the sections; auditioning holds a steady groove */
  const keep = G3.DREAM.p;
  G3.DREAM.p = { _building: true };
  if (G3.sectFor(9) !== "GROOVE" || G3.sectFor(30) !== "GROOVE") { fail("building must hold GROOVE"); aBad++; }
  G3.DREAM.p = { format: "loop" };
  if (G3.sectFor(9) !== "GROOVE" || G3.sectFor(37) !== "GROOVE") { fail("loop shape"); aBad++; }
  G3.DREAM.p = { format: "song" };
  for (let b = 0; b < 120; b++) if (!G3.SECT_CFG[G3.sectFor(b)]) { fail("song shape invalid at bar " + b); aBad++; }
  G3.DREAM.p = keep;
  if (!aBad) ok("the song avatar: 5 trait slots, valid prebuilt cards (drummers/low end/changes/voice), honest mutes, drummer = clock, shapes govern sections");
}
{ /* round 5 — the phrase library: LDRP decode, scale-fit, groove field,
     library-backed cards, preset law over phrase refs, headroom staging */
  let rBad = 0;
  const A36 = "0123456789abcdefghijklmnopqrstuvwxyz";
  const e1 = v => A36[Math.max(0, Math.min(35, Math.round(v)))];
  const e2 = v => A36[(v / 36) | 0] + A36[v % 36];
  const packD = evs => evs.map(e => e2(e.step) + e1(e.dev * 36 + 18) + G3.LDRP_LANES[e.lane] + e1(e.vel * 35)).join("");
  const packM = evs => evs.map(e => e2(e.step) + e2(e.deg + 24) + e1(Math.min(35, e.dur * 4)) + e1(e.vel * 35)).join("");
  /* decode round-trip within encoder quanta */
  const dIn = [{step:0,dev:.11,lane:0,vel:.9},{step:4,dev:-.14,lane:3,vel:.3},{step:33,dev:.02,lane:1,vel:1}];
  const dOut = G3.ldrpUnpackDrum(packD(dIn));
  dIn.forEach((e,i)=>{ const u=dOut[i];
    if (!(u && u.step===e.step && u.lane===e.lane && Math.abs(u.dev-e.dev)<1/36 && Math.abs(u.vel-e.vel)<1/34))
      { fail("drum decode "+i); rBad++; } });
  const mIn = [{step:0,deg:0,dur:1,vel:.7},{step:6,deg:-5,dur:.5,vel:.55},{step:30,deg:14,dur:2,vel:.8}];
  const mOut = G3.ldrpUnpackMel(packM(mIn));
  mIn.forEach((e,i)=>{ const u=mOut[i];
    if (!(u && u.step===e.step && u.deg===e.deg && Math.abs(u.dur-e.dur)<.26 && Math.abs(u.vel-e.vel)<1/34))
      { fail("mel decode "+i); rBad++; } });
  /* scale-fit: in-scale stays; chromatics fold IN; octaves preserved */
  const MINOR=[0,2,3,5,7,8,10];
  if (G3.ldrpFitScale(3,MINOR)!==3 || G3.ldrpFitScale(15,MINOR)!==15) { fail("fitScale identity"); rBad++; }
  const f4=G3.ldrpFitScale(4,MINOR); /* major third folds to a minor-scale tone */
  if (MINOR.indexOf(((f4%12)+12)%12)<0) { fail("fitScale fold"); rBad++; }
  const f16=G3.ldrpFitScale(16,MINOR);
  if (!(f16>=12&&f16<24&&MINOR.indexOf(f16-12)>=0)) { fail("fitScale octave"); rBad++; }
  /* groove field: per-step medians, nulls where the player never lands */
  const gf=G3.ldrpGrooveField([{step:0,dev:.1},{step:0,dev:.3},{step:0,dev:.2},{step:5,dev:-.1}],16);
  if (!(Math.abs(gf[0]-.2)<1e-9 && Math.abs(gf[5]+.1)<1e-9 && gf[3]===null)) { fail("groove field"); rBad++; }
  /* a synthetic library lights the lib branches of every candidate */
  const baseLen=G3.PHRASES.length;
  G3.PHRASES.push(
    {n:"Test Pocket",k:"dr",b:2,s:"funk",bpm:96,dm:"drummer1",src:"t:dr",tg:[],e:packD(dIn)},
    {n:"Test Fill",k:"dr",b:1,fl:1,s:"funk",bpm:96,dm:"drummer1",src:"t:fl",tg:[],e:packD(dIn.slice(0,2))},
    {n:"Test Low",k:"bs",b:2,md:"minor",cp:"T",src:"t:bs",tg:[],e:packM(mIn)},
    {n:"Test Counter",k:"cp",b:2,md:"minor",cp:"T",src:"t:cp",tg:[],e:packM(mIn)},
    {n:"Test Lick",k:"em",b:2,md:"minor",cp:"T",src:"t:em",tg:[],e:packM(mIn.slice(0,2))});
  G3.PHRASE_IDX.dr.push(baseLen); G3.PHRASE_IDX.fill.push(baseLen+1);
  G3.PHRASE_IDX.bs.push(baseLen+2); G3.PHRASE_IDX.cp.push(baseLen+3); G3.PHRASE_IDX.em.push(baseLen+4);
  let libD=null, libB=null, libC=null, libL=null;
  for (let s=1; s<=80 && !(libD&&libB&&libC&&libL); s++) {
    const d=G3.candDrums(G3.mulberry(s*3)); if (d.dlib!=null&&!libD) libD=d;
    const b=G3.candBass(G3.mulberry(s*5)); if (b.blib!=null&&!libB) libB=b;
    if (b.scale==="minor"){ const c=G3.candChords(G3.mulberry(s*7),b); if (c.clib!=null&&!libC) libC=c; }
    const l=G3.candLead(G3.mulberry(s*11)); if (l.elibs&&!libL) libL=l;
  }
  if (!libD||!(LDR_FIG[libD.fig]&&LDR_FIG[libD.fig].grid===16&&libD.comps.length===0&&libD.hum===1))
    { fail("library drummer card"); rBad++; }
  if (!libD||G3.PHRASES[libD.dlib].k!=="dr") { fail("dlib kind"); rBad++; }
  if (!libB||G3.PHRASES[libB.blib].k!=="bs") { fail("blib kind"); rBad++; }
  if (libB&&libB.scale==="minor"&&G3.PHRASES[libB.blib].md!=="minor") { fail("blib mode-match when the mode bucket exists"); rBad++; }
  if (!libC||libC.chordStyle!=="counter"||G3.PHRASES[libC.clib].k!=="cp") { fail("counter card"); rBad++; }
  if (!libL||!libL.elibs.every(i=>G3.PHRASES[i].k==="em")) { fail("embellish bag"); rBad++; }
  /* the refs ride composeP into a keepable preset; hostile refs are refused */
  if (libD&&libB&&libC&&libL) {
    const pL=G3.composeP([libD,libB,libC,libL,G3.FORMATS[0]],null,5);
    if (!(pL.dlib===libD.dlib&&pL.blib===libB.blib&&pL.clib===libC.clib&&
          JSON.stringify(pL.elibs)===JSON.stringify(libL.elibs))) { fail("lib refs through composeP"); rBad++; }
    const ent=JSON.parse(JSON.stringify({name:"t",seed:1,p:pL}));
    if (!G3.presetValidate(ent)) { fail("lib preset validates"); rBad++; }
    const evil=JSON.parse(JSON.stringify(ent)); evil.p.dlib=libB.blib; /* kind mismatch */
    if (G3.presetValidate(evil)) { fail("kind-mismatched dlib accepted"); rBad++; }
    const oob=JSON.parse(JSON.stringify(ent)); oob.p.elibs=[99999];
    if (G3.presetValidate(oob)) { fail("out-of-range elib accepted"); rBad++; }
  }
  G3.PHRASES.length=baseLen;
  G3.PHRASE_IDX.dr.pop(); G3.PHRASE_IDX.fill.pop(); G3.PHRASE_IDX.bs.pop(); G3.PHRASE_IDX.cp.pop(); G3.PHRASE_IDX.em.pop();
  /* dynamic headroom: pure staging table — more parts, more headroom */
  const mixJs = slice("const MIX_BUS_TRIM", "function mixApplyStage");
  const stageFor = eval(mixJs + "\n;mixStageFor");
  const limBase = eval(mixJs + "\n;MIX_LIM_BASE");
  let prevC=1;
  for (let n=1;n<=5;n++){ const st=stageFor(n);
    if (!(st.chord>0&&st.chord<=prevC+1e-9&&st.bass>0&&st.lead>0&&st.lim>0&&st.lim<=limBase+1e-3))
      { fail("stage table at n="+n); rBad++; }
    prevC=st.chord; }
  if (!(stageFor(5).chord<stageFor(1).chord && stageFor(5).lim<stageFor(2).lim)) { fail("staging never yields headroom"); rBad++; }
  if (!rBad) ok("round 5: LDRP decodes within quanta, scale-fit folds chromatics, groove field medians, library cards + preset law over phrase refs, headroom staging table");
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
  if (Object.keys(LDR_RECIPE).length < 25) fail("recipes " + Object.keys(LDR_RECIPE).length + " (floor 25)");
  if (Object.keys(LDR_MAP).length < 51) fail("map entries " + Object.keys(LDR_MAP).length + " (floor 51)");
  if (Object.keys(LDR_MAP).length !== Object.keys(LDR_FIG).length) fail("map entries " + Object.keys(LDR_MAP).length + " vs figures " + Object.keys(LDR_FIG).length);
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
    /* walk tracks as EVENTS (round 9: a byte scan counted VLQ deltas of 2048+
       ticks as note-ons — the old pins passed by fixture luck) */
    const W = smfWalk(u);
    if (W.err) fail("SMF walk: " + W.err);
    let o = W.end, tempoMetas = W.tempoMetas, meterMetas = W.meterMetas, progCh = W.progCh,
      on9 = W.on[9] || 0, off9 = W.off[9] || 0, on0 = W.on[0] || 0, off0 = W.off[0] || 0, walked = W.tracks;
    if (W.unmatched) fail(W.unmatched + " note-ons never closed (stuck notes in the score)");
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

/* ── suite 8: DD22 kit port (round 7) — fidelity gate + measured physics ── */
console.log("[8] dd22 kits");
{
  let dBad = 0;
  /* THE FIDELITY GATE: rebuild the whole DD22 block from the byte-identical
     donor with the same manifest and require the artifact to embed it EXACTLY.
     Any hand edit inside the block, any donor drift, any manifest slip fails
     here — the port stays verbatim by construction, provably. */
  let port = null;
  const donorHere = fs.existsSync(__dirname + "/mine/dd22_port.js") && fs.existsSync(__dirname + "/dreamdrummer_22.html");
  if (!donorHere) ok("fidelity gate SKIPPED — mine/dd22_port.js + dreamdrummer_22.html are not beside tests.js (a handoff-zip run; the repo carries them)");
  else try { port = require("./mine/dd22_port.js"); } catch (e) { fail("dd22_port.js loads: " + e.message); dBad++; }
  if (port) {
    try {
      const donor = fs.readFileSync(__dirname + "/dreamdrummer_22.html", "utf8");
      const block = port.buildBlock(donor);
      if (s.indexOf(block) < 0) { fail("embedded DD22 block is NOT the donor-derived block"); dBad++; }
      else ok(port.MANIFEST.length + " donor slices byte-identical in the artifact (" + block.length + " bytes)");
    } catch (e) { fail("fidelity gate: " + e.message); dBad++; }
  }
  const ddJs = slice("/*DD22-BEGIN*/", "const LOCKS={");
  const G8 = eval(ddJs + "\n;({DD22,DD_KIT_NAMES,DD_ZONE2SLOT,DD_LAYERS})");
  const D = G8.DD22;
  /* one shelf, three copies, zero drift */
  const bankKeys = Object.keys(D.KITBANK).filter(k => k !== "_base").sort().join(",");
  if (G8.DD_KIT_NAMES.slice().sort().join(",") !== bankKeys ||
      D.KIT_NAMES.join(",") !== G8.DD_KIT_NAMES.join(","))
    { fail("kit name lists disagree with the bank"); dBad++; }
  else ok(G8.DD_KIT_NAMES.length + " kits: " + G8.DD_KIT_NAMES.join(" "));
  /* zone map: 12 zones, all land on real slots, the core drums where they must */
  const Z = G8.DD_ZONE2SLOT;
  if (Z.length !== 12 || !Z.every(v => Number.isInteger(v) && v >= 0 && v <= 11)) { fail("zone map shape"); dBad++; }
  if (Z[0] !== 0 || Z[1] !== 1 || Z[6] !== 2 || Z[10] !== 3 || Z[8] !== 2 || Z[3] !== 4 || Z[2] !== 8)
    { fail("core zone routing (kick/snare/hats/clap/rim)"); dBad++; }
  if (new Set(Z).size < 10) { fail("zone map collapses slots"); dBad++; }
  /* deep-merge: preset states only what it changes, the base fills the rest,
     arrays replace whole, the base object never mutates */
  const baseKnock = D.KITBANK._base.kick.knockHz;
  const tp = D.kitPatch("trapK"), hp = D.kitPatch("hyphyK"), af = D.kitPatch("afroK");
  if (tp.kick.bend !== 3.4 || tp.kick.knockHz !== 240 || tp.kick.tuned !== 1) { fail("trapK merge"); dBad++; }
  if (hp.clap.tailDec !== 0.22 || hp.lvl[4] !== 0.7) { fail("hyphyK merge"); dBad++; }
  if (af.toms.length !== 3 || af.toms[0].hz !== 96 || af.toms[0].decay !== 0.5) { fail("afroK toms merge"); dBad++; }
  if (D.KITBANK._base.kick.knockHz !== baseKnock || D.KITBANK._base.toms[0].hz === 96)
    { fail("merge mutated the base"); dBad++; }
  /* measured physics at 44.1k — the numbers, not the vibes */
  const sr = 44100;
  const pk = h => { let p = 0; for (let i = 0; i < h.L.length; i++) { const v = Math.max(Math.abs(h.L[i]), Math.abs(h.R[i])); if (v > p) p = v; } return p; };
  const tail = (h, t) => { const a = Math.floor(t * sr); let e = 0, n = 0;
    for (let i = a; i < Math.min(a + 4410, h.L.length); i++) { e += h.L[i] * h.L[i]; n++; } return n ? Math.sqrt(e / n) : 0; };
  const finite = h => { for (let i = 0; i < h.L.length; i++) if (!isFinite(h.L[i]) || !isFinite(h.R[i])) return false; return true; };
  const nk = D.renderHit("neptune", 0, 1, sr), tk = D.renderHit("trapK", 0, 1, sr);
  if (!finite(nk) || !finite(tk)) { fail("kick render NaN"); dBad++; }
  if (!(pk(nk) > 0.3 && pk(nk) < 1.45)) { fail("neptune kick peak " + pk(nk).toFixed(3)); dBad++; }
  if (!(tail(tk, 0.5) > 5e-3)) { fail("trapK 808 has no 0.5s tail (" + tail(tk, 0.5).toExponential(1) + ")"); dBad++; }
  if (!(tail(nk, 0.5) < 1e-3)) { fail("neptune kick rings like an 808"); dBad++; }
  if (!(tk.L.length > nk.L.length * 2)) { fail("trapK sub not longer than neptune"); dBad++; }
  const hc = D.renderHit("houseK", 2, 0.85, sr), ho = D.renderHit("houseK", 3, 0.85, sr);
  if (!(hc.L.length < ho.L.length)) { fail("closed hat outlives open hat"); dBad++; }
  /* stereo: the kit pans its lanes — a tomH buffer must actually lean */
  const th = D.renderHit("neptune", 7, 0.85, sr);
  { let el = 0, er = 0; for (let i = 0; i < th.L.length; i++) { el += th.L[i] * th.L[i]; er += th.R[i] * th.R[i]; }
    if (!(er > el * 1.1)) { fail("tomH pan not in the buffer"); dBad++; } }
  /* the choke rule survives the port: a closed hat silences the open one */
  { const kit = new D.Kit(sr, D.makeRng(7), D.tables());
    kit.setPatch(D.kitPatch("ewf"));
    kit.trig(3, 0.9);
    if (!kit.v[3].busy()) { fail("open hat not busy after trig"); dBad++; }
    kit.trig(2, 0.9);
    if (!kit.v[3].choking) { fail("closed hat does not choke the open hat"); dBad++; } }
  /* determinism: the bake is seeded — same request, same samples */
  { const a = D.renderHit("boombap", 1, 0.85, sr), b = D.renderHit("boombap", 1, 0.85, sr);
    let same = a.L.length === b.L.length;
    if (same) for (let i = 0; i < a.L.length; i += 7) if (a.L[i] !== b.L[i]) { same = false; break; }
    if (!same) { fail("bake not deterministic"); dBad++; } }
  /* preset law: dkit must name a shelf kit or the preset is refused */
  { const kd = G3.candDrums(G3.mulberry(4)), kb = G3.candBass(G3.mulberry(5)),
      kc = G3.candChords(G3.mulberry(6), kb), kl = G3.candLead(G3.mulberry(7));
    const base = G3.composeP([kd, kb, kc, kl, { kind: "shape", format: "loop" }], null, 5);
    const mk = d => { const p = JSON.parse(JSON.stringify(base)); if (d !== undefined) p.dkit = d; else delete p.dkit; return { name: "t", seed: 1, p }; };
    if (!G3.presetValidate(mk())) { fail("dkit-less preset refused"); dBad++; }
    if (!G3.presetValidate(mk("hyphyK"))) { fail("valid dkit refused"); dBad++; }
    if (G3.presetValidate(mk("nope"))) { fail("unknown dkit accepted"); dBad++; }
    if (G3.presetValidate(mk(5))) { fail("numeric dkit accepted"); dBad++; } }
  /* the deal: library drummers draw DD kits deterministically and evenly-ish */
  { const seen = new Set(); let withKit = 0, lib = 0;
    for (let sd = 1; sd <= 160; sd++) { const d = G3.candDrums(G3.mulberry(sd));
      if (d.dlib == null) continue; lib++;
      if (d.dkit != null) { withKit++;
        if (G8.DD_KIT_NAMES.indexOf(d.dkit) < 0) { fail("card drew unknown kit " + d.dkit); dBad++; break; }
        seen.add(d.dkit);
        if (d.desc.indexOf("DD·") < 0) { fail("dkit card hides its kit in desc"); dBad++; break; } } }
    if (!(lib > 20 && withKit > lib * 0.3 && withKit < lib * 0.8)) { fail("dkit draw rate off (" + withKit + "/" + lib + ")"); dBad++; }
    if (seen.size < 6) { fail("kit draw not spread (" + seen.size + " kits)"); dBad++; }
    const c = G3.candDrums(G3.mulberry(11));
    if (c.dkit) { const p = G3.composeP([c, null, null, null, null], null, 5, true);
      const p2 = G3.composeP([c, null, null, null, null], null, 1);
      if (p2 && p2.dkit !== c.dkit) { fail("composeP drops dkit"); dBad++; } } }
  if (!dBad) ok("fidelity gate + merge + physics (808 tail, choke, pan, determinism) + preset law + deal");
}

/* ── suite 9: DD22 style engine (cycle 37) — 17 drum languages, realized ── */
console.log("[9] dd22 styles");
{
  let sBad = 0;
  const ddJs = slice("/*DD22-BEGIN*/", "const LOCKS={");
  const G9 = eval(ddJs + "\n;({DD22})");
  const D = G9.DD22;
  const bell = LDR_FIG.bembe.hits;
  if (D.KSTYLE_KEYS.length !== 17) { fail("style count " + D.KSTYLE_KEYS.length); sBad++; }
  /* every style's kit must exist on the shelf */
  D.KSTYLE_KEYS.forEach(k => { const dk = D.STYLE2KIT[k];
    if (!dk || D.KIT_NAMES.indexOf(dk) < 0) { fail(k + " has no shelf kit"); sBad++; } });
  /* every plan: zones/vels bounded, perc names are REAL ported physics */
  const recipes = G2.LDR_RECIPE;
  D.KSTYLE_KEYS.forEach(k => {
    const pl = D.kRealize(k, G3.mulberry(42), bell);
    if (!pl || !(pl.grid === 16 || pl.grid === 12)) { fail(k + " grid"); sBad++; return; }
    pl.kit.forEach(e => {
      if (!(e.zone >= 0 && e.zone <= 11 && e.vel > 0 && e.vel <= 1.3 &&
            e.step > -1 && e.step < 2 * pl.grid + 1)) { fail(k + " kit event out of law"); sBad++; } });
    pl.perc.forEach(e => {
      if (!recipes[e.name]) { fail(k + " perc name '" + e.name + "' has no physics"); sBad++; } });
    pl.sub.forEach(e => {
      if (!(e.note >= -24 && e.note <= 24 && e.dur > 0)) { fail(k + " sub event out of law"); sBad++; } });
  });
  /* deterministic per seed */
  { const a = JSON.stringify(D.kRealize("trap", G3.mulberry(7), bell)),
        b = JSON.stringify(D.kRealize("trap", G3.mulberry(7), bell));
    if (a !== b) { fail("realizer not deterministic"); sBad++; } }
  /* dembow's law: the cell loops verbatim — every canonical kick step
     present, no adds (varying it un-writes the genre) */
  { const pl = D.kRealize("dembow", G3.mulberry(3), bell);
    const want = D.KPAT.dembowKick.map(h => h[0]).join(",");
    const got = pl.kit.filter(e => e.zone === 0).map(e => e.step).join(",");
    if (got !== want) { fail("dembow kick varied (" + got + ")"); sBad++; } }
  /* the swing is IN the steps: house at MPC 56 moves only the 2nd 16th of
     each 8th pair, by (56-50)*0.04 = 0.24 steps */
  { const pl = D.kRealize("house", G3.mulberry(5), bell);
    const hats = pl.kit.filter(e => e.zone === 6 || e.zone === 10);
    const swung = hats.filter(e => Math.abs(e.step % 1 - 0.24) < 1e-9);
    const straightOdd = hats.filter(e => e.step % 2 === 1);
    if (!swung.length) { fail("house hats not swung"); sBad++; }
    if (straightOdd.length) { fail("house 2nd-16th hat left on the grid"); sBad++; } }
  /* drill's signature: slides happen, and they glide between DIFFERENT notes */
  { let slides = 0, dup = 0;
    for (let sd = 1; sd <= 30; sd++) {
      const pl = D.kRealize("drill", G3.mulberry(sd * 13), bell);
      let prev = null;
      pl.sub.forEach(e => { if (e.slide) { slides++; if (prev && prev.note === e.note) dup++; } prev = e; });
    }
    if (!slides) { fail("drill never slides in 30 seeds"); sBad++; }
    if (dup) { fail("slide between identical notes"); sBad++; } }
  /* fills: the cut empties, the roll accelerates toward the arrival */
  { if (D.kFill("cut", G3.mulberry(1), 16) !== null) { fail("cut fill not a cut"); sBad++; }
    const r = D.kFill("rolls32", G3.mulberry(1), 16);
    for (let i = 1; i < r.length; i++) if (r[i].vel <= r[i - 1].vel) { fail("roll not a crescendo"); sBad++; break; }
    const t = D.kFill("toms", G3.mulberry(1), 16);
    if (!(t[0].slot === 9 && t[t.length - 1].slot === 5)) { fail("tom fill not descending"); sBad++; } }
  /* the deal: style cards appear, name their lineage, validate as presets */
  { let styled = 0; const seen = new Set(); let firstCard = null;
    for (let sd = 1; sd <= 200; sd++) { const d = G3.candDrums(G3.mulberry(sd * 7 + 1));
      if (d.dsty != null) { styled++;
        if (D.KSTYLE_KEYS.indexOf(d.dsty) < 0) { fail("unknown style " + d.dsty); sBad++; break; }
        if (d.dkit !== D.STYLE2KIT[d.dsty]) { fail("style card wears wrong kit"); sBad++; break; }
        seen.add(d.dsty); if (!firstCard) firstCard = d; } }
    if (!(styled > 15)) { fail("style cards too rare (" + styled + "/200)"); sBad++; }
    if (seen.size < 8) { fail("style draw not spread (" + seen.size + ")"); sBad++; }
    if (firstCard) {
      const p = G3.composeP([firstCard, null, null, null, { kind: "shape", format: "loop" }], null, 5);
      if (!p || p.dsty !== firstCard.dsty) { fail("composeP drops dsty"); sBad++; }
      else {
        if (!G3.presetValidate({ name: "t", seed: 1, p: JSON.parse(JSON.stringify(p)) })) { fail("style preset refused"); sBad++; }
        const bad = JSON.parse(JSON.stringify(p)); bad.dsty = "polka";
        if (G3.presetValidate({ name: "t", seed: 1, p: bad })) { fail("unknown dsty accepted"); sBad++; }
      }
    } }
  if (!sBad) ok("17 languages realize (zones/physics/sub in law) · dembow verbatim · MPC swing in the steps · drill slides · fills · deal + preset law");
}

/* ── suite 10: round 8 — the three-door save's pure parts, measured ─────── */
console.log("[10] save doors + drive law");
{
  let rBad = 0;
  /* zip round-trip: BOTH writers (house zipStore, donor encodeZipStore) must
     be readable by the new store-only reader, byte-exact, CRC-verified */
  const exJs = slice("/*EXPORT-UTILS-BEGIN*/", "/*EXPORT-UTILS-END*/");
  const collected = [];
  class FakeBlob { constructor(parts) { let len = 0;
    const flat = parts.map(p => p instanceof Uint8Array ? p : new Uint8Array(p));
    flat.forEach(p => len += p.length);
    this.bytes = new Uint8Array(len); let o = 0;
    flat.forEach(p => { this.bytes.set(p, o); o += p.length; }); } }
  const G10 = (function (Blob) { return eval(exJs + "\n;({crc32:typeof crc32!=='undefined'?crc32:CRC_T&&null,zipStore,zipReadStore})"); })(FakeBlob);
  /* eval sandbox note: zipStore closes over the local FakeBlob via the param name */
  const enc = s => new TextEncoder().encode(s);
  const projTxt = JSON.stringify([{ name: "t #1", seed: 1, p: {} }]);
  {
    const files = [{ name: "mix.wav", data: enc("RIFF-not-really") },
      { name: "stems/drums.wav", data: enc("RIFF-d") },
      { name: "project.json", data: enc(projTxt) }];
    const wrote = (function () { const B = FakeBlob;
      /* re-eval zipStore with Blob bound to the collector */
      const f = new Function("files", "Blob", "crc32", exJs + "\n;return zipStore(files);");
      return f(files, FakeBlob, null); })();
    const bytes = wrote.bytes;
    const rd = G10.zipReadStore(bytes);
    if (!rd || Object.keys(rd).length !== 3) { fail("house zip round-trip lost entries"); rBad++; }
    else if (new TextDecoder().decode(rd["project.json"]) !== projTxt) { fail("project.json bytes differ"); rBad++; }
    else if (new TextDecoder().decode(rd["stems/drums.wav"]) !== "RIFF-d") { fail("stem bytes differ"); rBad++; }
    /* hostiles: truncated, garbage, deflate-marked entries never crash, never lie */
    if (G10.zipReadStore(bytes.subarray(0, 40)) !== null) { fail("truncated zip accepted"); rBad++; }
    if (G10.zipReadStore(enc("PK\x03\x04 but nothing real here at all — junk")) !== null) { fail("garbage zip accepted"); rBad++; }
    const bad = bytes.slice();               /* mark entry 0 as deflate in the central dir */
    { const dv = new DataView(bad.buffer);
      let eo = -1; for (let i = bad.length - 22; i >= 0; i--) if (dv.getUint32(i, true) === 0x06054b50) { eo = i; break; }
      const cd = dv.getUint32(eo + 16, true); dv.setUint16(cd + 10, 8, true); }
    const rd2 = G10.zipReadStore(bad);
    if (rd2 && rd2["mix.wav"]) { fail("deflate entry silently 'decoded'"); rBad++; }
  }
  /* the donor writer's zips read back too (session zips are one family) */
  {
    const ddJs = slice("/*DD22-BEGIN*/", "const LOCKS={");
    const D = eval(ddJs + "\n;DD22");
    const buf = D.encodeZipStore([{ name: "a.txt", data: enc("alpha") }, { name: "b/c.bin", data: enc("beta") }]);
    const rd = G10.zipReadStore(new Uint8Array(buf));
    if (!rd || new TextDecoder().decode(rd["a.txt"]) !== "alpha" || new TextDecoder().decode(rd["b/c.bin"]) !== "beta")
      { fail("donor-writer zip unreadable"); rBad++; }
  }
  /* the drive law, measured at the curve (round 8): reference parity at bus
     0.5, saturation instead of endpoint clamping, and a musical k range */
  {
    const dJs = slice("const DRIVE_HEADROOM", "function buildGraph");
    const G = eval(dJs + "\n;({DRIVE_HEADROOM,driveCurve})");
    const curveAt = (c, bus) => { const x = bus * G.DRIVE_HEADROOM;   /* shaper input */
      const i = Math.round((x + 1) / 2 * (c.length - 1)); return c[i]; };
    const c2 = G.driveCurve(.2), c0 = G.driveCurve(.02), cMax = G.driveCurve(1);
    if (Math.abs(curveAt(c2, .5) - .5) > .01) { fail("drive .2 not unity at reference bus .5 (" + curveAt(c2, .5).toFixed(3) + ")"); rBad++; }
    if (Math.abs(curveAt(c0, .5) - .5) > .01) { fail("drive .02 not unity at reference"); rBad++; }
    if (!(curveAt(c2, .3) < .55)) { fail("drive .2 still a clipper at bus .3 (" + curveAt(c2, .3).toFixed(3) + " — old law gave ~1.0)"); rBad++; }
    if (!(Math.abs(c2[c2.length - 1]) < 1)) { fail("curve rails at the endpoint — clamp, not saturation"); rBad++; }
    for (let i = 1; i < c2.length; i++) if (c2[i] < c2[i - 1]) { fail("curve not monotone"); rBad++; break; }
    if (!(curveAt(cMax, 2) / curveAt(c0, 2) < .999)) { fail("k law dead — max drive saturates no harder than min"); rBad++; }
    /* the endpoint clamp is survivable: a bus peak of 2 lands ON the curve */
    if (!(curveAt(c2, 2) > curveAt(c2, 1.2))) { fail("headroom domain not covering bus 2"); rBad++; }
  }
  /* import range law: stock programs pass, runaways are refused */
  {
    const bankJs = slice("/*BANKB-BEGIN*/", "/*BANKB-END*/");
    const GB = eval(bankJs + "\n;({progValidate})");
    if (!GB.progValidate(PROGRAMS[5])) { fail("stock program refused by range law"); rBad++; }
    const mut = k => { const m = JSON.parse(JSON.stringify(PROGRAMS[5])); k(m); return m; };
    if (GB.progValidate(mut(m => m.fx.delay.fb = 1.2))) { fail("runaway delay fb accepted"); rBad++; }
    if (GB.progValidate(mut(m => m.fx.drive = 2.5))) { fail("drive 2.5 accepted"); rBad++; }
    if (GB.progValidate(mut(m => m.filter.reso = 30))) { fail("reso 30 accepted"); rBad++; }
    if (GB.progValidate(mut(m => { if (m.osc && m.osc[0]) m.osc[0].lvl = 5; }))) { fail("osc lvl 5 accepted"); rBad++; }
    let anyFb = 0; PROGRAMS.forEach(p => { if (p.fx && p.fx.delay && p.fx.delay.fb > .85) anyFb++; });
    if (anyFb) { fail(anyFb + " stock programs exceed the fb range the law enforces"); rBad++; }
    /* the ||0 bypass: an ABSENT fb used to validate as 0 while applyFXP
       assigned undefined to an AudioParam (TypeError, half-staged FX) */
    if (GB.progValidate(mut(m => delete m.fx.delay.fb))) { fail("absent fb accepted (||0 bypass)"); rBad++; }
    if (GB.progValidate(mut(m => delete m.fx.drive))) { fail("absent drive accepted"); rBad++; }
    if (GB.progValidate(mut(m => delete m.filter.reso))) { fail("absent reso accepted"); rBad++; }
    if (GB.progValidate(mut(m => m.fx.delay.time = 4))) { fail("non-string delay time accepted"); rBad++; }
    /* round 9 (the attacker lens): the WHOLE stock bank passes the widened law, and
       the four blockers it found are refused at the gate */
    const refused = PROGRAMS.filter(p => !GB.progValidate(p)).map(p => p.id);
    if (refused.length) { fail("stock programs refused by the widened range law: " + refused.join(" ")); rBad++; }
    const hostileP = [
      ["cat markup", m => m.cat = "<img src=x onerror=1>"],
      ["tempo −120", m => m.tempo = -120],
      ["tempo 1e308", m => m.tempo = 1e308],
      ["arpDefault oct 1e9", m => m.arpDefault = { on: true, patt: "UP", reso: "16", gate: .5, oct: 1e9, latch: true }],
      ["arpDefault patt junk", m => m.arpDefault = { on: true, patt: "EXPLODE", reso: "16", gate: .5, oct: 1, latch: true }],
      ["NaN attack", m => m.aEG.a = NaN],
      ["sustain 40", m => m.aEG.s = 40],
      ["detune 1e9", m => { if (m.osc && m.osc[0]) m.osc[0].det = 1e9; }],
      ["osc oct 40", m => { if (m.osc && m.osc[0]) m.osc[0].oct = 40; }],
      ["lfo rate 1e6", m => m.lfo.rate = 1e6],
      ["filter cutoff 1e9", m => m.filter.cutoff = 1e9],
      ["filter type junk", m => m.filter.type = "hp99"],
      ["vox f1 string", m => m.vox = { f1: "x", f2: 900 }],
      ["mono string", m => m.mono = "yes"]];
    hostileP.forEach(([nm, f]) => { if (GB.progValidate(mut(f))) { fail("range law accepts " + nm); rBad++; } });
    /* the wave lookup is an own-key lookup */
    if (!/hasOwnProperty\.call\(WAVES,w\)/.test(s)) { fail("wave lookup still a bare bracket (constructor throws in spawnVoice)"); rBad++; }
    if (!/if\(!\(stepLen>=\.005\)/.test(s)) { fail("arp scheduler has no spin guard"); rBad++; }
    if (!/CAT:\$\{esc\(cur\.cat\)\}/.test(s)) { fail("cat reaches the LCD unescaped"); rBad++; }
  }
  /* stem parity (round 8): one duck law and one mastering gain across every
     pass, so the stems in a session zip sum back to its mix */
  {
    const sj = slice("/* every kick-class hit in the take", "async function renderPass");
    const G = eval(sj + "\n;({duckKeysFor})");
    const evs = [
      { role: "dd", zone: 0, vel: .9, t: 0 },        /* DD kick — keys */
      { role: "dd", zone: 0, vel: .3, t: .5 },       /* too soft — no key */
      { role: "dd", zone: 6, vel: .9, t: .25 },      /* hat — no key */
      { role: "kit", note: 48, vel: .9, t: 1 },      /* TRITON kick lane — keys */
      { role: "kit", note: 50, vel: .9, t: 1.25 },   /* snare lane — no key */
      { role: "perc", name: "surdo", vel: .8, t: 2 },/* low drum — keys */
      { role: "perc", name: "clave", vel: .8, t: 2.5 },
      { role: "bass", note: 40, vel: .9, t: 3 }];
    const keys = G.duckKeysFor(evs);
    if (keys.length !== 3) { fail("duck keys wrong (" + keys.length + " of 3): " + JSON.stringify(keys)); rBad++; }
    else if (!(keys[0].t === 0 && keys[1].t === 1 && keys[2].t === 2)) { fail("duck key times wrong " + JSON.stringify(keys)); rBad++; }
    else if (!keys.every(k => k.d > 0 && k.d <= 1)) { fail("duck key depth out of law"); rBad++; }
    /* the keys derive from the WHOLE take, so a lane-only stem list yields
       the same automation the mix has — that is the parity claim */
    const bassOnly = evs.filter(e => e.role === "bass");
    if (G.duckKeysFor(bassOnly).length !== 0) { fail("bass-only pass keys itself"); rBad++; }
    const mj = slice("/* mastering trim: lift a quiet bounce", "/* the stem groups");
    const wavStub = "function wavStereo24(L,R,sr){return {len:L.length,pk:L.reduce((a,x)=>Math.max(a,Math.abs(x)),0)};}\n";
    const GM = eval(wavStub + mj + "\n;({masterize})");
    const mk = (amp, n) => ({ sampleRate: 44100, length: n,
      _c: [new Float32Array(n).fill(amp), new Float32Array(n).fill(amp)],
      getChannelData(i) { return this._c[i]; } });
    const loud = GM.masterize(mk(.30, 1000));          /* the mix */
    const quiet = GM.masterize(mk(.02, 1000), loud.g); /* a sparse stem, mix's gain */
    const quietSolo = GM.masterize(mk(.02, 1000));     /* what the old law did */
    if (!(Math.abs(quiet.g - loud.g) < 1e-9)) { fail("stem did not take the mix's gain"); rBad++; }
    else if (!(quietSolo.g > loud.g * 2)) { fail("solo-normalized stem is not the divergence the fix removes"); rBad++; }
    else if (!(quiet.bytes.pk < quietSolo.bytes.pk * .5)) { fail("stem gain law has no audible effect"); rBad++; }
    /* a stem whose own peak beats the mix's must not be pushed into the
       writer's clamp — the reported peak is PRE-clamp, so it can convict */
    const hotStem = GM.masterize(mk(.9, 1000), loud.g);
    if (!(hotStem.pk <= .98 + 1e-6)) { fail("hot stem clips at the mix's gain (pk " + hotStem.pk.toFixed(3) + ")"); rBad++; }
    if (!(loud.pk > 0 && loud.pk <= .98 + 1e-6)) { fail("mix peak not reported/in law (" + loud.pk + ")"); rBad++; }
  }
  /* the insert is level-neutral: drive changes TIMBRE, not loudness (round 8).
     The wet/dry law is READ OUT OF applyFXP — re-implementing it here would
     test this file against itself and pass no matter what ships. */
  {
    const dJs = slice("const DRIVE_HEADROOM", "function buildGraph");
    const G = eval(dJs + "\n;({DRIVE_HEADROOM,driveCurve})");
    const fxJs = slice("function applyFXP(p,force)", "function midiHz");
    const gainStub = () => ({ gain: { value: 0, setTargetAtTime() {} } });
    const nodes = { shaper: { curve: null }, dWet: gainStub(), dDry: gainStub(),
      cSend: gainStub(), rSend: gainStub(), dSend: gainStub(),
      dlyL: { delayTime: { setTargetAtTime() {}, setValueAtTime() {} } }, dlyR: { delayTime: { setTargetAtTime() {}, setValueAtTime() {} } },
      fbA: gainStub(), fbB: gainStub() };
    const applyFXP = new Function("p", "force", "ctx", "shaper", "dWet", "dDry", "cSend", "rSend",
      "dSend", "dlyL", "dlyR", "fbA", "fbB", "driveCurve", "delayBeats", "VERB", "VERB_PIN", "exporting",
      fxJs.replace(/^function applyFXP\(p,force\)\s*\{/, "") .replace(/\}\s*$/, "") + "\nreturn {w:dWet.gain.value,d:dDry.gain.value};");
    const readPair = a => applyFXP({ fx: { drive: a, reverb: .3, chorus: .2, delay: { fb: .3, send: .2, time: "8" } } },
      false, { currentTime: 0 }, nodes.shaper, nodes.dWet, nodes.dDry, nodes.cSend, nodes.rSend, nodes.dSend,
      nodes.dlyL, nodes.dlyR, nodes.fbA, nodes.fbB, G.driveCurve, () => .25, { pct: 50 }, null, false);
    const wet = (a, bus) => { const c = G.driveCurve(a), x = bus * G.DRIVE_HEADROOM;
      const i = Math.round((Math.max(-1, Math.min(1, x)) + 1) / 2 * (c.length - 1)); return c[i]; };
    const insert = (a, bus) => { const pr = readPair(a); return pr.d * bus + pr.w * wet(a, bus); };
    [0, .2, .28, .55, 1].forEach(a => {
      const at = insert(a, .5), clean = insert(0, .5);
      const dB = 20 * Math.log10(at / clean);
      if (!(Math.abs(dB) < .35)) { fail("drive " + a + " is " + dB.toFixed(2) + " dB off clean at the reference bus"); rBad++; }
    });
    /* and it must still SATURATE — level-neutral must not mean transparent */
    if (!(insert(1, 2) < insert(0, 2) * .8)) { fail("max drive does not compress the top"); rBad++; }
  }
  /* preset law: own-keys only, and the strings the engine flashes/splits */
  {
    const kd = G3.candDrums(G3.mulberry(4)), kb = G3.candBass(G3.mulberry(5)),
      kc = G3.candChords(G3.mulberry(6), kb), kl = G3.candLead(G3.mulberry(7));
    const base = G3.composeP([kd, kb, kc, kl, { kind: "shape", format: "loop" }], null, 5);
    const mkP = f => { const p = JSON.parse(JSON.stringify(base)); f(p); return { name: "t", seed: 1, p }; };
    if (!G3.presetValidate(mkP(() => {}))) { fail("real preset refused by the round-8 law"); rBad++; }
    ["constructor", "toString", "__proto__", "hasOwnProperty"].forEach(k => {
      if (G3.presetValidate(mkP(p => p.fig = k))) { fail("prototype key accepted as a figure: " + k); rBad++; }
      if (G3.presetValidate(mkP(p => p.scale = k))) { fail("prototype key accepted as a scale: " + k); rBad++; }
    });
    if (G3.presetValidate(mkP(p => p.name = 42))) { fail("non-string song name accepted"); rBad++; }
    if (G3.presetValidate(mkP(p => p.name = "x".repeat(65)))) { fail("overlong song name accepted"); rBad++; }
    if (G3.presetValidate(mkP(p => p.chordStyle = "explode"))) { fail("unknown chordStyle accepted"); rBad++; }
    /* round 9 (the attacker lens): comps are own figure keys on the figure's grid,
       kit is an integer, leadOct is bounded — each used to reach the conductor */
    if (G3.presetValidate(mkP(p => p.comps = ["constructor"]))) { fail("prototype key accepted as a comp"); rBad++; }
    if (G3.presetValidate(mkP(p => p.comps = ["__proto__+3"]))) { fail("prototype key with rotation accepted as a comp"); rBad++; }
    if (G3.presetValidate(mkP(p => p.comps = ["not-a-figure"]))) { fail("unknown comp accepted"); rBad++; }
    if (G3.presetValidate(mkP(p => p.kit = "63"))) { fail("string kit index accepted"); rBad++; }
    if (G3.presetValidate(mkP(p => p.leadOct = 1e9))) { fail("leadOct 1e9 accepted"); rBad++; }
    if (G3.presetValidate(mkP(p => p.leadOct = "12"))) { fail("string leadOct accepted"); rBad++; }
    if (!G3.presetValidate(mkP(p => p.leadOct = 24))) { fail("legal leadOct refused"); rBad++; }
    if (G3.presetValidate(mkP(p => p.extraKick = "yes"))) { fail("non-boolean extraKick accepted"); rBad++; }
    if (!/esc\(c\.roman\)/.test(s)) { fail("theory bar prints roman unescaped"); rBad++; }
    if (!/try\{ dreamScheduleBar\(/.test(s)) { fail("a bar that cannot be scheduled still spins the tick"); rBad++; }
  }
  if (!rBad) ok("zip round-trip (both writers) + hostiles refused · drive law: unity at reference, saturates, ±2 domain · " +
    "import ranges clamped (absent fields refused) · stem parity: one duck law, one mastering gain");
}


/* ── suite 12: the bank court (round 9) ────────────────────────────── */
console.log("[12] bank court");
{
  let rBad = 0;
  /* the saturator headroom law: every satCurve now spans ±SAT_HEADROOM of its
     input through mkSat's pre-trim; inside ±1 the transfer is the OLD curve
     exactly, beyond it satSoft's own knee continues instead of the clamp */
  const satJs = slice("function satSoft", "function limitCurve");
  const GS = eval(satJs + "\n;({satSoft,satCurve,SAT_HEADROOM})");
  const H = GS.SAT_HEADROOM, k = 1.25, c = GS.satCurve(k), m = Math.abs(GS.satSoft(k));
  if (!(H >= 2)) { fail("SAT_HEADROOM " + H + " — the tube's domain does not cover a vel-1 triad (measured input pk 1.42)"); rBad++; }
  const at = u => c[Math.round((u / H + 1) / 2 * (c.length - 1))];   /* u = saturator input, pre-trim */
  let worst = 0;
  for (let u = -1; u <= 1.0001; u += .05) worst = Math.max(worst, Math.abs(at(u) - GS.satSoft(u * k) / m));
  if (worst > 2e-3) { fail("headroom changed the transfer inside ±1 (max err " + worst.toFixed(4) + ")"); rBad++; }
  if (!(at(1.4) > at(1) && at(1.4) < 1.2)) { fail("past 1 the curve must keep rising smoothly toward satSoft's asymptote (" + at(1).toFixed(3) + " → " + at(1.4).toFixed(3) + ")"); rBad++; }
  for (let i = 1; i < c.length; i++) if (c[i] < c[i - 1]) { fail("sat curve not monotone"); rBad++; break; }
  if (!(c.length >= 4096)) { fail("curve resolution halved by the wider domain"); rBad++; }
  const mk = /function mkSat\(k\)\{[^]*?pre\.gain\.value=1\/SAT_HEADROOM/.test(s);
  if (!mk) { fail("mkSat does not carry the 1/SAT_HEADROOM pre-trim"); rBad++; }
  /* every saturator goes through mkSat — the only bare satCurve() is mkSat's own */
  const mkBody = s.slice(s.indexOf("function mkSat(k)"), s.indexOf("}", s.indexOf("function mkSat(k)")) + 1);
  const bare = (s.match(/\.curve=satCurve\(/g) || []).length - (mkBody.match(/\.curve=satCurve\(/g) || []).length;
  if (bare) { fail(bare + " saturator(s) still take satCurve without the pre-trim"); rBad++; }
  if (!/glue\.connect\(tubeS\.in\)/.test(s)) { fail("master tube not fed through its headroom trim"); rBad++; }
  /* the bank law the court wrote: a bandpass of Q ≥ 3 in front of a sine-led
     oscillator set passes < −20 dB off-centre — three programs sat 25 dB
     under the bank and were inaudible. Data, so a data law. */
  PROGRAMS.forEach(p => {
    if (p.cat === "DRUMS" || !p.filter || p.filter.type !== "bp") return;
    /* sine-LED: sines carry at least half the oscillator level (noise through a
       narrow band is a whistle by design — A104 — and stays legal) */
    const tot = Array.isArray(p.osc) ? p.osc.reduce((a, o) => a + (o.lvl || 0), 0) : 0;
    const sine = Array.isArray(p.osc) ? p.osc.filter(o => o.w === "sine").reduce((a, o) => a + (o.lvl || 0), 0) : 0;
    const sineLed = tot > 0 && sine >= tot * .5;
    if (sineLed && p.filter.reso >= 3) { fail(p.id + " " + p.name + ": bandpass Q " + p.filter.reso + " on a sine-led program (the inaudible-program trap)"); rBad++; }
  });
  /* the bell law and the formant makeup exist where the voice is built */
  const svJs = slice("function spawnVoice", "/* ---- drums ---- */");
  if (!/_bellParts\?\s*1\/Math\.sqrt\(Math\.max\(1,_lvlSum\)\)/.test(svJs)) { fail("bell partial-sum law (sqrt) missing from spawnVoice"); rBad++; }
  if (!/g1\.gain\.value=\.9\*VOX_MAKEUP/.test(svJs) || !/gd\.gain\.value=\.12\*VOX_MAKEUP/.test(svJs)) { fail("VOX formant makeup missing"); rBad++; }
  const vm = eval(slice("const VOX_MAKEUP=", ";") + ";VOX_MAKEUP");
  if (!(vm >= 2 && vm <= 3)) { fail("VOX_MAKEUP " + vm + " outside the measured window (2.5 put the family on the median)"); rBad++; }
  if (!rBad) ok("saturator headroom ±" + H + " (transfer inside ±1 unchanged, max err " + worst.toExponential(1) + ", knee continues past 1) · no bandpass-on-sine traps · bell sqrt law · VOX makeup ×" + vm);
}

/* a small SMF-1 event walker: deltas as VLQ, meta/sysex lengths honoured,
   running status supported, note-on/off paired per (channel, note) */
function smfWalk(u) {
  const r = { err: null, tracks: 0, tempoMetas: 0, meterMetas: 0, progCh: 0, on: {}, off: {}, unmatched: 0, end: 14 };
  try {
    const ntrk = (u[10] << 8) | u[11]; let o = 14;
    for (let k = 0; k < ntrk; k++) {
      if (String.fromCharCode(u[o], u[o+1], u[o+2], u[o+3]) !== "MTrk") { r.err = "track " + k + " header"; return r; }
      const len = (u[o+4] << 24) | (u[o+5] << 16) | (u[o+6] << 8) | u[o+7];
      let i = o + 8; const end = i + len; let status = 0; const open = {};
      while (i < end) {
        let d = 0; do { d = (d << 7) | (u[i] & 0x7f); } while (u[i++] & 0x80);
        let b = u[i];
        if (b === 0xFF) { const type = u[i+1]; i += 2; let L = 0; do { L = (L << 7) | (u[i] & 0x7f); } while (u[i++] & 0x80);
          if (type === 0x51 && L === 3) r.tempoMetas++; if (type === 0x58 && L === 4) r.meterMetas++; i += L; continue; }
        if (b === 0xF0 || b === 0xF7) { i++; let L = 0; do { L = (L << 7) | (u[i] & 0x7f); } while (u[i++] & 0x80); i += L; continue; }
        if (b & 0x80) { status = b; i++; }
        const hi = status & 0xF0, ch = status & 0x0F;
        if (hi === 0xC0 || hi === 0xD0) { if (hi === 0xC0) r.progCh++; i += 1; continue; }
        const n = u[i], v = u[i+1]; i += 2;
        if (hi === 0x90 && v > 0) { r.on[ch] = (r.on[ch] || 0) + 1; open[ch + ":" + n] = (open[ch + ":" + n] || 0) + 1; }
        else if (hi === 0x80 || (hi === 0x90 && v === 0)) { r.off[ch] = (r.off[ch] || 0) + 1; if (open[ch + ":" + n]) open[ch + ":" + n]--; else r.unmatched++; }
      }
      for (const k2 in open) r.unmatched += open[k2];
      o = end; r.tracks++;
    }
    r.end = o;
  } catch (e) { r.err = String(e && e.message || e); }
  return r;
}

/* ── suite 13: the song, not the search (round 10) ─────────────────── */
console.log("[13] song bounce");
{
  let rBad = 0;
  /* the composed song's length is the shape's own section list */
  const sj = slice("const SONG_BARS=", "async function exportTake(");
  const G = eval(sj.slice(0, sj.indexOf("function songEvents")) + "\n;({SONG_BARS,songBars})");
  const secJs = slice("function sectFor(bar)", "const SECT_CFG=");
  const lists = [...secJs.matchAll(/\[("[A-Z]+",?)+\]/g)].map(m => m[0].split(",").length);
  if (lists.length !== 2 || !lists.every(n => n === 8)) { fail("sectFor section lists changed (" + lists.join("/") + ") — SONG_BARS must follow"); rBad++; }
  if (G.SONG_BARS.song !== 4 + 8 * 8 || G.SONG_BARS.arc !== 4 + 8 * 8) { fail("SONG_BARS does not cover intro + every section once (" + JSON.stringify(G.SONG_BARS) + ")"); rBad++; }
  if (!(G.SONG_BARS.loop >= 20 && G.SONG_BARS.loop <= 68)) { fail("loop bounce length out of sense (" + G.SONG_BARS.loop + ")"); rBad++; }
  if (G.songBars({ format: "nope" }) !== G.songBars({ format: "loop" }) || G.songBars(null) !== G.songBars({ format: "loop" })) { fail("songBars has no default"); rBad++; }
  /* ROUND 11 — THE ENDING: one bar past the shape; only a composition arms it */
  const G2 = eval(sj.slice(0, sj.indexOf("function songEvents")) + "\n;({END_BARS})");
  if (!(G2.END_BARS >= 1 && G2.END_BARS <= 2)) { fail("END_BARS out of sense (" + G2.END_BARS + ")"); rBad++; }
  if (G.songBars({ format: "song" }) !== G.SONG_BARS.song + G2.END_BARS || G.songBars({ format: "loop" }) !== G.SONG_BARS.loop + G2.END_BARS) { fail("songBars does not add the ending"); rBad++; }
  const SF = eval("(function(){ const DREAM={p:null,_outroAt:null}; " + secJs + "; return {sectFor, set:v=>{ DREAM._outroAt=v; }, setP:p=>{ DREAM.p=p; }}; })()");
  SF.setP({ format: "song" }); SF.set(null);
  if ([...Array(300).keys()].some(b => SF.sectFor(b) === "END")) { fail("the room's conductor reaches END without _outroAt"); rBad++; }
  SF.set(68);
  if (SF.sectFor(68) !== "END" || SF.sectFor(69) !== "END" || SF.sectFor(67) === "END" || SF.sectFor(3) !== "INTRO" || SF.sectFor(67) !== "LIFT") { fail("END does not sit exactly at _outroAt (" + [67, 68, 69].map(SF.sectFor).join("/") + ")"); rBad++; }
  SF.setP({ format: "loop" }); SF.set(36);
  if (SF.sectFor(36) !== "END" || SF.sectFor(35) !== "GROOVE") { fail("a loop has no ending"); rBad++; }
  const cfg = slice("const SECT_CFG={", "};");
  if (!/END:\{comps:0,bass:1,lead:0/.test(cfg)) { fail("SECT_CFG has no END (comps 0 · bass 1 · lead 0)"); rBad++; }
  const dsb = slice("function dreamScheduleBar(", "setInterval(()=>{");
  const endBlk = dsb.slice(dsb.indexOf("if(isEnd){"), dsb.indexOf("DREAM._barLen=barLen; DREAM._barStart=at; return;"));
  if (!endBlk || endBlk.length < 200) { fail("dreamScheduleBar has no END block that returns before the drums"); rBad++; }
  else {
    if (!/kitZone\(P\.kit,z,/.test(endBlk) || !/\[\[0,[.\d]+\],\[1,[.\d]+\],\[4,[.\d]+\]\]/.test(endBlk)) { fail("the ending hit is not kick+snare+crash on the one"); rBad++; }
    if (!/spawnVoice\(PROGRAMS\[P\.bass\],bassRoot,[^;]*hold,DREAM\.pans\.bass\)/.test(endBlk)) { fail("the ending does not hold the bass root"); rBad++; }
    if (!/tones\.forEach\(\(n,i\)=>spawnVoice\(PROGRAMS\[P\.chord\],n,[^;]*hold,DREAM\.pans\.chord\)\)/.test(endBlk)) { fail("the ending does not hold the tonic voicing"); rBad++; }
    if (/PROGRAMS\[P\.lead\]/.test(endBlk)) { fail("the ending plays a lead"); rBad++; }
    if (!/hold=barLen\*1\.\d+/.test(endBlk)) { fail("the ending's hold does not reach past the bar line"); rBad++; }
    const drumsAfter = dsb.indexOf("if(P.dsty&&typeof DD22");
    if (!(drumsAfter > dsb.indexOf("if(isEnd){"))) { fail("the END block sits after the drums — the last bar would still groove"); rBad++; }
  }
  if (!/const base=isEnd\? tonicBase : chordSpecFor/.test(dsb) || !/const nextBase=\(isEnd\|\|toEnd\)\? tonicBase : chordSpecFor/.test(dsb)) { fail("the ending is not the scale's I / the bar before does not hear it coming"); rBad++; }
  if (!/chordSpecFor\(P\.scale,0,P\.root\+12\)\.tones/.test(dsb)) { fail("tonicBase is not degree 0 of the scale (prog[0] is not always I — jazz ii-V-I)"); rBad++; }
  if (!/phraseBar%8===7\|\|toEnd\)/.test(dsb)) { fail("the figure path does not fill into the ending"); rBad++; }
  const se11 = slice("function songEvents(p)", "function ddWarmDone(");
  if (!/DREAM\._outroAt=N-END_BARS;/.test(se11) || !/outroAt:DREAM\._outroAt/.test(se11) || !/DREAM\._outroAt=S\.outroAt;/.test(se11)) { fail("songEvents does not arm/snapshot/restore _outroAt"); rBad++; }
  const arms = [...s.matchAll(/DREAM\._outroAt=(?!null|S\.outroAt|N-END_BARS)/g)].length;
  if (arms) { fail("something outside the composition arms _outroAt (" + arms + ")"); rBad++; }
  if (!/DREAM\._outroAt=null; setPlayUI\(false\)/.test(slice("function dreamStop(silent)", "function dreamDraw") || slice("function dreamStop(silent)", "}\n"))) { fail("dreamStop does not clear _outroAt"); rBad++; }
  /* every hit path logs-then-returns when DRY, so a composition plays nothing */
  const sv = slice("function spawnVoice", "/* ---- drums ---- */");
  if (!/takeLog\(prog,note,vel,when,dur,dest\) : null;\s*\n\s*if\(typeof DRY!=="undefined"&&DRY\) return null;/.test(sv)) { fail("spawnVoice does not return DRY after logging"); rBad++; }
  const dh = slice("function ddHit(", "function kitZone(");
  if (!/if\(typeof DRY!=="undefined"&&DRY\)\{ if\([^}]*takeLogD\(kitName,zone,vel,when,o\.layerVel\); return true; \}/.test(dh)) { fail("ddHit does not log-and-return DRY"); rBad++; }
  const ds = slice("function ddSub(", "/*TAKE-CODEC-BEGIN*/");
  if (!/if\(typeof DRY!=="undefined"&&DRY\)\{ if\(!o\._q\) takeLogD8\(/.test(ds)) { fail("ddSub does not log-and-return DRY"); rBad++; }
  const dp = slice("function drumHitP(", "function ldrPlayFig(");
  if (!/takeLogP\(name,vel,when,\{[^}]*\}\);\s*\n\s*if\(typeof DRY!=="undefined"&&DRY\) return true;/.test(dp)) { fail("drumHitP does not log-and-return DRY"); rBad++; }
  if (!/if\(!\(typeof DRY!=="undefined"&&DRY\)\)\{ ldrPulse\(at\); pulseAt\(at\); \}/.test(s)) { fail("a composed bar still arms UI pulse timers"); rBad++; }
  /* the doors: song by default, the jam on request, the score composes too */
  const dr = slice("function doorsRender()", "function saveScoreOnly(");
  if (!/on\("svMix",\(\)=>exportTake\("mix","song"\)\)/.test(dr) || !/on\("svSession",\(\)=>exportTake\("session","song"\)\)/.test(dr)) { fail("MIX/SESSION do not bounce the song"); rBad++; }
  if (!/id="svJam"/.test(dr) || !/on\("svJam",\(\)=>exportTake\("mix","take"\)\)/.test(dr)) { fail("the jam (as played) is not one tap away"); rBad++; }
  if (!/kind=kind\|\|"mix"; src=src\|\|"song";/.test(s)) { fail("exportTake does not default to the song"); rBad++; }
  if (!/src=src\|\|"song";\s*\n\s*let evs=null;/.test(s)) { fail("the SCORE door does not compose the song"); rBad++; }
  /* the composition restores what it touched */
  const se = slice("function songEvents(p)", "function ddWarmDone(");
  ["TAKE.ev=S.ev", "DREAM.rng=S.rng", "DREAM.pans=S.pans", "state.tempo=S.tempo", "DRY=false; DUCK_MUTE=false"].forEach(k => { if (se.indexOf(k) < 0) { fail("songEvents does not restore " + k); rBad++; } });
  if (!/delete pp\._building/.test(se)) { fail("a try-on at SAVE time would bounce as a steady groove (the shape must apply)"); rBad++; }
  /* a composition INSIDE an export must still reach the tape: every logger's
     export gate yields to DRY (mutation-found: the first song bounce fell back
     to the jam because exporting was already true) */
  ["function takeLog(", "function takeLogP(", "function takeLogD(", "function takeLogD8(", "function takeLogMix("].forEach(fn => {
    const i = s.indexOf(fn), body = s.slice(i, i + 500);
    if (!/exporting&&!\(typeof DRY!=="undefined"&&DRY\)\) return( null)?;/.test(body)) { fail(fn + " export gate does not yield to DRY"); rBad++; } });
  if (!/if\(!\(typeof DRY!=="undefined"&&DRY\)\) mixApplyStage\(s,when\);/.test(s)) { fail("a composition moves the live console"); rBad++; }
  /* after an export the console heals to the STANDING song's chord program (verbSet's law), not the player's patch */
  const heals = (s.match(/if\(state\.powered\)\{ if\(typeof DREAM!=="undefined"&&DREAM\.p\) applyFXP\(PROGRAMS\[DREAM\.p\.chord\]\); else if\(cur\) applyFX\(\); \}/g) || []).length;
  if (heals < 2) { fail("export heal does not prefer the standing song (" + heals + " of 2 exits)"); rBad++; }
  /* the verify fleet's four: a composition leaves the dialed VERB alone (and restores it), arms no readout timers, sizes a shape-less song as the loop it is labelled, and never flushes the live duck */
  if (!/verbSet==="function"&&!\(typeof DRY!=="undefined"&&DRY\)\) verbSet\(p\.verb\)/.test(s)) { fail("a DRY composition resets the VERB decision"); rBad++; }
  if (!/verb:\(typeof VERB!=="undefined"\)\?VERB\.pct:null\}/.test(se) || !/VERB\.pct!==S\.verb&&typeof verbSet==="function"\) verbSet\(S\.verb\)/.test(slice("function songEvents(p)", "function ddWarmDone("))) { fail("songEvents does not restore the VERB decision"); rBad++; }
  if (!/if\(!\(typeof DRY!=="undefined"&&DRY\)\) setTimeout\(\(\)=>\{ if\(!DREAM\.on\) return;/.test(s)) { fail("a composed bar arms the readout timer"); rBad++; }
  if (!/if\(!pp\.format\) pp\.format="loop";/.test(slice("function songEvents(p)", "function ddWarmDone("))) { fail("a shape-less song composes as an arc but is sized as a loop"); rBad++; }
  if (!/DREAM\.bar!==DREAM\._duckFlushed&&MIX&&MIX\._ctx===ctx&&!\(typeof DRY!=="undefined"&&DRY\)\)\{/.test(s)) { fail("a composition can flush the live duck automation"); rBad++; }
  if (!rBad) ok("SONG_BARS follows sectFor (loop " + G.SONG_BARS.loop + " · arc/song " + G.SONG_BARS.song + " · +" + G2.END_BARS + " ending bar, armed only by the composition, the tonic on the one held) · every hit path logs-and-returns DRY · doors bounce the song, JAM the take · composition restores the performance");
}

/* ── suite 11: the take in the zip + the address (round 9) ─────────── */
console.log("[11] take codec + address");
(async () => {
  let rBad = 0;
  const ownKeys = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  /* the take codec, in a sandbox that binds exactly what it references */
  const codecJs = slice("/*TAKE-CODEC-BEGIN*/", "/*TAKE-CODEC-END*/");
  const bankJs = slice("/*BANKB-BEGIN*/", "/*BANKB-END*/");
  const GB = eval(bankJs + "\n;({progValidate})");
  const ddJs = slice("/*DD22-BEGIN*/", "const LOCKS={");
  const GD = eval(ddJs + "\n;({DD_KIT_NAMES})");
  const TC = new Function("PROGRAMS", "DD_KIT_NAMES", "LDR_RECIPE", "progValidate",
    codecJs + "\n;return {takeSerialize,takeDeserialize,TAKE_MAX_EV,TAKE_MAX_SEC};")(PROGRAMS, GD.DD_KIT_NAMES, G2.LDR_RECIPE, GB.progValidate);
  const drumsIdx = PROGRAMS.findIndex(p => p.cat === "DRUMS");
  const foreign = JSON.parse(JSON.stringify(PROGRAMS[5])); foreign.name = "Foreign Pad";
  const evs = [
    { t: 0.5, role: "you", prog: PROGRAMS[5], note: 60, vel: .8, dur: 1.2, tempo: 100 },
    { t: 0.25, role: "bass", prog: PROGRAMS[7], note: 40, vel: .9, dur: .5, tempo: 100 },
    { t: 0, role: "kit", prog: PROGRAMS[drumsIdx], note: 48, vel: 1, dur: .12, tempo: 100 },
    { t: 1, role: "perc", name: "surdo", vel: .7, dur: .12, tempo: 100, pitch: 1.1, mute: .9, layerVel: .6 },
    { t: 1.5, role: "dd", kit: "neptune", zone: 0, vel: .95, dur: .12, tempo: 100 },
    { t: 2, role: "dd8", kit: "trapK", note: 36, vel: .8, dur: .4, slide: .1, from: 38, tempo: 100 },
    { t: 2.5, role: "mix", s: { bass: .9, chord: .8, lead: .85, lim: .8 }, tempo: 100, dur: 0 },
    { t: 3, role: "lead", prog: foreign, note: 72, vel: .6, dur: .3, tempo: 100 }];
  const ser = TC.takeSerialize(evs);
  const back = TC.takeDeserialize(JSON.parse(JSON.stringify(ser)));
  if (!back || back.length !== evs.length) { fail("take round-trip lost events (" + (back && back.length) + ")"); rBad++; }
  else {
    if (!(back[0].role === "kit" && back[1].role === "bass" && back[2].role === "you")) { fail("restored take not sorted by time"); rBad++; }
    const you = back.find(e => e.role === "you");
    if (you.prog !== PROGRAMS[5]) { fail("bank program not restored by identity (index ride)"); rBad++; }
    const ld = back.find(e => e.role === "lead");
    if (!ld.prog || ld.prog.name !== "Foreign Pad" || ld.prog === foreign) { fail("foreign program not restored as a validated copy"); rBad++; }
    const d8 = back.find(e => e.role === "dd8");
    if (!(d8.kit === "trapK" && d8.from === 38 && Math.abs(d8.slide - .1) < 1e-9)) { fail("dd8 fields lost " + JSON.stringify(d8)); rBad++; }
    const pc = back.find(e => e.role === "perc");
    if (!(pc.name === "surdo" && pc.pitch === 1.1 && pc.mute === .9 && pc.layerVel === .6)) { fail("perc fields lost"); rBad++; }
    const mx = back.find(e => e.role === "mix");
    if (!(mx.s && mx.s.lim === .8 && mx.dur === 0)) { fail("mix stage lost"); rBad++; }
    if (ser.ev.some(e => ownKeys(e, "prog"))) { fail("serialized take carries program objects for bank programs"); rBad++; }
  }
  /* hostiles: every refusal is the whole take, never a guess */
  const H = f => { const o = JSON.parse(JSON.stringify(ser)); f(o); return TC.takeDeserialize(o); };
  const refuse = (name, f) => { if (H(f) !== null) { fail("take hostile accepted: " + name); rBad++; } };
  refuse("version 2", o => o.v = 2);
  refuse("NaN time", o => o.ev[0].t = NaN);
  refuse("time past the cap", o => o.ev[0].t = TC.TAKE_MAX_SEC + 1);
  refuse("unknown role", o => o.ev[0].role = "sidechain");
  refuse("prototype perc name", o => { o.ev[3].name = "constructor"; });
  refuse("unknown dd kit", o => { o.ev[4].kit = "zzz"; });
  refuse("dd zone 12", o => { o.ev[4].zone = 12; });
  refuse("program index 999", o => { o.ev[2].pi = 999; });
  refuse("note 128", o => { o.ev[2].note = 128; });
  refuse("foreign program past the range law", o => { o.ev[7].p.fx.delay.fb = 1.2; });
  refuse("kit role on a non-drum program", o => { o.ev[0].pi = 5; o.ev[0].role = "kit"; });
  refuse("float zone", o => { o.ev[4].zone = 1.5; });
  /* out-of-range OPTIONAL fields are dropped, never passed through */
  { const r = H(o => { o.ev[5].from = 999; o.ev[3].pitch = 40; o.ev[3].layerVel = -1; });
    const d8 = r && r.find(e => e.role === "dd8"), pc = r && r.find(e => e.role === "perc");
    if (!r || d8.from !== undefined || pc.pitch !== 1 || pc.layerVel !== undefined) { fail("out-of-range optional field passed through " + JSON.stringify({ from: d8 && d8.from, pitch: pc && pc.pitch, lv: pc && pc.layerVel })); rBad++; } }
  { const o = JSON.parse(JSON.stringify(ser)); const big = []; for (let i = 0; i <= TC.TAKE_MAX_EV; i++) big.push(o.ev[2]); o.ev = big;
    if (TC.takeDeserialize(o) !== null) { fail("take hostile accepted: " + (TC.TAKE_MAX_EV + 1) + " events"); rBad++; } }
  if (TC.takeDeserialize("[]") !== null || TC.takeDeserialize(null) !== null) { fail("non-object take accepted"); rBad++; }
  /* the tape's own laws (round 9, the correctness lens): a hold is closed by
     its VOICE (a COMBI's layers share a key), and an edited working program
     rides as a frozen copy while an unedited one rides as the bank object */
  {
    const tapeJs = slice("let _frozenProg=", "function takeLogP(");
    const st = { userSlot: null, progIdx: 5, tempo: 100 };
    const TK = { on: true, t0: 0, ev: [], open: {}, gen: 0 };
    const mk = new Function("TAKE", "state", "PROGRAMS", "DREAM", "ctx", "takeTrim", "cur", "exporting",
      tapeJs + "\n;return {takeLog,takeCloseEv,takeProgFor,setCur:c=>{cur=c;},setNow:t=>{ctx.currentTime=t;}};");
    const ctx = { currentTime: 0 };
    const cur = JSON.parse(JSON.stringify(PROGRAMS[5]));
    const TP = mk(TK, st, PROGRAMS, { pans: null }, ctx, () => {}, cur, false);
    if (TP.takeProgFor(cur) !== PROGRAMS[5]) { fail("unedited working program not logged as the bank object"); rBad++; }
    cur.fx.drive = .77;
    const fz = TP.takeProgFor(cur);
    if (fz === cur || fz === PROGRAMS[5] || fz.fx.drive !== .77) { fail("edited working program not frozen"); rBad++; }
    if (TP.takeProgFor(cur) !== fz) { fail("frozen copy not stable across notes of one edit generation"); rBad++; }
    cur.fx.drive = .5;
    if (TP.takeProgFor(cur) === fz) { fail("a new edit did not make a new frozen copy"); rBad++; }
    /* two layers on ONE key: closing by voice closes the right one */
    const e1 = TP.takeLog(PROGRAMS[0], 60, .8, 0, null, null), e2 = TP.takeLog(PROGRAMS[3], 60, .8, 0, null, null);
    if (!e1 || !e2 || TK.open[60].length !== 2) { fail("open holds not tracked per event (" + JSON.stringify(TK.open) + ")"); rBad++; }
    else {
      TP.setNow(.9); TP.takeCloseEv(e2);
      if (!(e2.dur > .85 && e2.dur < .95) || e1.dur !== null) { fail("close-by-voice closed the wrong layer " + JSON.stringify([e1.dur, e2.dur])); rBad++; }
      TP.setNow(1.4); TP.takeCloseEv(e1);
      if (!(e1.dur > 1.35) || TK.open[60]) { fail("second layer not closed / open list not cleared"); rBad++; }
      TP.takeCloseEv(e1); if (e1.dur > 1.45) { fail("closing twice re-patched the duration"); rBad++; }
    }
  }
  /* library phrases keep their 16-step shape inside a 12-pulse bar; the conducted figure plays the song's kit */
  const libSites = (s.match(/at\+p0\*stepM\+gfs\(p0\)/g) || []).length;
  if (libSites !== 3) { fail("library phrase sites on the bar-mapped step: " + libSites + " of 3"); rBad++; }
  if (!/ldrPlayFig\(P\.fig,f,0,at,step,C\.mainVel,humK,"fig",\{kit:P\.kit,conducted:true\}\)/.test(s)) { fail("the conducted figure does not carry the song\x27s kit"); rBad++; }
  if (!/dd8:38/.test(s)) { fail("808 line previews as piano in a DAW"); rBad++; }
  if (!/const t0=DREAM\.next-\.1; TAKE\.ev\.forEach\(e=>\{ e\.t=0; \}\); TAKE\.t0=t0;/.test(s)) { fail("the tape\x27s zero is not the first downbeat (replays jitter in time)"); rBad++; }
  /* the performance lens (round 9): the render instantiates voices in windows at
     the render clock's checkpoints; the tape trims with hysteresis; no dead nodes;
     no wall-clock timers offline from the TRITON kit either */
  const rp = slice("async function renderPass(", "/* mastering trim:");
  if (!/const WIN=RENDER_WIN/.test(rp) || !/oc\.suspend\(t0\)\.then/.test(rp) || !/schedUpTo\(t0\+WIN\+\.25\)/.test(rp)) { fail("renderPass does not instantiate voices in windows at render-clock checkpoints"); rBad++; }
  if (/for\(let i=0;i<evs\.length;i\+\+\)\{\s*const e=evs\[i\];/.test(rp)) { fail("renderPass still instantiates the whole take before startRendering"); rBad++; }
  if (!/const f2=single\? null : ctx\.createBiquadFilter\(\)/.test(s)) { fail("second filter pole built for single-pole programs"); rBad++; }
  if (!/const needLFO=!!\(prog\.lfo\.pitch\|\|prog\.lfo\.filter\|\|prog\.lfo\.amp\|\|prog\.vox\|\|MODW>0\)/.test(s)) { fail("LFO built for programs that never use it"); rBad++; }
  if (!/if\(!\(typeof exporting!=="undefined"&&exporting\)\) setTimeout\(v\.kill,1400\)/.test(s)) { fail("drumHit arms wall-clock kill timers during a render"); rBad++; }
  /* the kit bake runs off the main thread, from the DD22 block's own verbatim source, with a main-thread fallback */
  const wj = slice("function ddWorker()", "function takeLogD(");
  if (!/new Worker\(/.test(wj) || !/DD22-BEGIN/.test(wj) || !/DD22\.renderHit\(j\.kit,j\.slot,j\.layer,j\.sr\)/.test(wj)) { fail("DD22 bake does not run in a worker from the block's own source"); rBad++; }
  if (!/const sync=\(\)=>/.test(wj) || !/ddBake\(kit,s,l,sr\)/.test(wj)) { fail("DD22 bake has no main-thread fallback"); rBad++; }
  if (/n<2/.test(wj)) { fail("fallback still bakes two cold hits in one macrotask"); rBad++; }
  {
    const trimJs = slice("function takeTrim()", "/* round 9 (the court): the tape logged");
    const TK = { on: true, t0: 0, ev: [], open: {}, gen: 0 };
    const trim = new Function("TAKE", trimJs + "\n;return takeTrim;")(TK);
    for (let i = 0; i < 2100; i++) TK.ev.push({ t: i * .25, role: "you" });   /* 0..525 s — past the 480+30 hysteresis mark */
    trim(); const t0a = TK.t0, n0 = TK.ev.length;
    if (!(t0a > 0 && TK.ev[TK.ev.length - 1].t <= 480.001)) { fail("takeTrim did not trim a 500 s take to 480 (" + TK.t0 + ")"); rBad++; }
    for (let k = 1; k <= 20; k++) { TK.ev.push({ t: TK.ev[TK.ev.length - 1].t + .5, role: "you" }); trim(); }
    if (TK.t0 !== t0a) { fail("takeTrim rewrote the take again within the 30 s hysteresis window"); rBad++; }
    for (let k = 1; k <= 60; k++) { TK.ev.push({ t: TK.ev[TK.ev.length - 1].t + .5, role: "you" }); trim(); }
    if (!(TK.t0 > t0a)) { fail("takeTrim never trimmed again past the hysteresis window"); rBad++; }
  }
  /* the address: preset-law JSON → deflate → base64url, and back through the SAME gate */
  const addrJs = slice("/*ADDR-BEGIN*/", "/*ADDR-END*/");
  const A = new Function("presetParse", addrJs + "\n;return {addrEncode,addrDecode,b64uEnc,b64uDec,bytesThrough,ADDR_MAX,ADDR_INFLATE_MAX};")(G3.presetParse);
  const kd = G3.candDrums(G3.mulberry(11)), kb = G3.candBass(G3.mulberry(12)),
    kc = G3.candChords(G3.mulberry(13), kb), kl = G3.candLead(G3.mulberry(14));
  const p = G3.composeP([kd, kb, kc, kl, { kind: "shape", format: "song" }], null, 5);
  delete p._seed; p.verb = 60;
  const entry = { name: (p.name || "dream").slice(0, 34) + " #4242", seed: 4242, p };
  if (!G3.presetValidate(entry)) { fail("test entry does not pass the preset law"); rBad++; }
  const addr = await A.addrEncode([entry]);
  const jsonLen = JSON.stringify([entry]).length;
  if (!/^p=[A-Za-z0-9_-]+$/.test(addr)) { fail("address not deflate/base64url: " + addr.slice(0, 20)); rBad++; }
  if (!(addr.length < jsonLen)) { fail("address longer than the JSON it carries (" + addr.length + " vs " + jsonLen + ")"); rBad++; }
  const dec = await A.addrDecode("#" + addr);
  if (!(dec.length === 1 && dec[0].seed === 4242 && JSON.stringify(dec[0].p) === JSON.stringify(p))) { fail("address does not regrow the entry"); rBad++; }
  const raw = "j=" + A.b64uEnc(new TextEncoder().encode(JSON.stringify([entry])));
  const decJ = await A.addrDecode(raw);
  if (!(decJ.length === 1 && decJ[0].seed === 4242)) { fail("raw (j=) address does not decode"); rBad++; }
  /* hostiles */
  const bad = async (name, h) => { const r = await A.addrDecode(h); if (!Array.isArray(r) || r.length) { fail("address hostile accepted: " + name); rBad++; } };
  await bad("wrong kind", "#x=" + addr.slice(2));
  await bad("not base64", "#p=!!!not base64!!!");
  await bad("garbage bytes", "#p=" + A.b64uEnc(new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])));
  await bad("length%4==1", "#p=" + addr.slice(2, 2 + (Math.floor(addr.length / 4) * 4 - 3)));
  await bad("over the cap", "#p=" + "A".repeat(A.ADDR_MAX + 8));
  await bad("prototype figure", "#j=" + A.b64uEnc(new TextEncoder().encode(JSON.stringify([{ name: "x", seed: 1, p: Object.assign({}, p, { fig: "constructor" }) }]))));
  { /* an inflate bomb stops at the cap instead of filling the tab */
    const zeros = new Uint8Array(4 * 1024 * 1024);
    const cs = new CompressionStream("deflate"); const w = cs.writable.getWriter(); w.write(zeros); w.close();
    const parts = []; const rd = cs.readable.getReader();
    for (;;) { const { value, done } = await rd.read(); if (done) break; parts.push(value); }
    let n = 0; parts.forEach(x => n += x.length); const z = new Uint8Array(n); let o = 0; parts.forEach(x => { z.set(x, o); o += x.length; });
    const bomb = "#p=" + A.b64uEnc(z);
    if (!(bomb.length < A.ADDR_MAX)) { fail("bomb test is not under the hash cap (" + bomb.length + ")"); rBad++; }
    else await bad("inflate bomb (4 MB from " + z.length + " bytes)", bomb);
    /* the CAP must be what stops it — a JSON parse failing on 4 MB of zeros
       would pass the line above with the cap removed (mutation-found) */
    const capped = await A.bytesThrough(z, new DecompressionStream("deflate"), A.ADDR_INFLATE_MAX);
    if (capped !== null) { fail("inflate cap did not stop the bomb (" + (capped && capped.length) + " bytes came out)"); rBad++; }
    const uncapped = await A.bytesThrough(z, new DecompressionStream("deflate"), 1 << 30);
    if (!(uncapped && uncapped.length === zeros.length)) { fail("bytesThrough is broken (" + (uncapped && uncapped.length) + ")"); rBad++; }
  }
  if (A.b64uDec("abcde") !== null) { fail("base64url length%4==1 accepted"); rBad++; }
  if (!rBad) ok("take codec: all 9 roles round-trip, bank programs by index, foreign programs re-validated, 14 hostiles refused · " +
    "address: " + addr.length + " chars for " + jsonLen + " bytes of song, regrows through the preset law, 7 hostiles + inflate bomb refused");
  console.log(errs ? "\nRESULT: " + errs + " ERROR(S)" : "\nRESULT: ALL GREEN");
  process.exit(errs ? 1 : 0);
})().catch(e => { fail("suite 11 threw: " + (e && e.stack || e)); console.log("\nRESULT: " + errs + " ERROR(S)"); process.exit(1); });

