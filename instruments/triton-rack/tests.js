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

/* ── suite 8: DD22 kit port (round 7) — fidelity gate + measured physics ── */
console.log("[8] dd22 kits");
{
  let dBad = 0;
  /* THE FIDELITY GATE: rebuild the whole DD22 block from the byte-identical
     donor with the same manifest and require the artifact to embed it EXACTLY.
     Any hand edit inside the block, any donor drift, any manifest slip fails
     here — the port stays verbatim by construction, provably. */
  let port = null;
  try { port = require("./mine/dd22_port.js"); } catch (e) { fail("dd22_port.js loads: " + e.message); dBad++; }
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
  }
  if (!rBad) ok("zip round-trip (both writers) + hostiles refused · drive law: unity at reference, saturates, ±2 domain · " +
    "import ranges clamped (absent fields refused) · stem parity: one duck law, one mastering gain");
}

console.log(errs ? "\nRESULT: " + errs + " ERROR(S)" : "\nRESULT: ALL GREEN");
process.exit(errs ? 1 : 0);
