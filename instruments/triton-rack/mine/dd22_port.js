#!/usr/bin/env node
/* dd22_port.js — cycle 36: port dreamdrummer_22's DRUM KITS into triton-rack.html
 *
 * The port is VERBATIM BY CONSTRUCTION: this script slices exact line ranges
 * out of the byte-identical donor (dreamdrummer_22.html, same directory) and
 * assembles them into one namespaced IIFE (`DD22`) injected between
 * /*DD22-BEGIN*​/ ... /*DD22-END*​/ markers in the artifact. Only two lines are
 * transformed — the kit patch bank's IIFE head/tail, rewrapped from an object
 * property into a named var — and the fidelity gate in tests.js re-derives
 * every slice from the donor and byte-compares it against what is embedded.
 *
 * Sliced donor systems (KNOCK-SEAM sections, line ranges verified 2026-08-31):
 *   00-atoms      numbers/rng/DCBlock/OnePole/SVF/Biquad/Reson/sat curves/AD/
 *                 pan/fft/fast-sine
 *   01-organelles ModalBank + MODES (measured body physics)
 *   01b-studio    Comp, Sat (tube/tape/fuzz + auto-gain), Transient, EQ3,
 *                 ParaComp (the parallel "goes harder" bus)
 *   02-keys       band-limited wavetable set (MetalVoice reads it)
 *   03b-drums     KickVoice (4-band 808 + harmonic restoration), SnareVoice
 *                 (8-wire bank), MetalVoice (6-osc hat circuit), TunedDrum
 *                 (modal membrane w/ Duffing sag), ShakeVoice, ClapVoice
 *   03c-kits      KIT_SLOTS + Kit (12 voices into ONE bus: EQ→tube→parallel
 *                 compression — "a kit is not twelve voices, it is a BUS")
 *   04-patches    the kit bank: neptune/timb/ewf/trapK/hyphyK/boombap/afroK/
 *                 latinK/houseK/softK/cine
 *
 * Usage:  node dd22_port.js           # inject/refresh the DD22 block
 *         require(...)                 # exports MANIFEST + slice helpers
 */
"use strict";
const fs = require("fs");
const path = require("path");

const DIR = path.join(__dirname, "..");
const DONOR = path.join(DIR, "dreamdrummer_22.html");
const ART = path.join(DIR, "triton-rack.html");

/* 1-based inclusive donor line ranges. head/tail replace the FIRST/LAST line
   of the slice (the only transformation in the whole port). */
const MANIFEST = [
  { name: "atoms-numbers",       a: 446,  b: 460 },
  { name: "atoms-rng",           a: 462,  b: 500 },
  { name: "atoms-dcblock",       a: 524,  b: 534 },
  { name: "atoms-onepole",       a: 536,  b: 550 },
  { name: "atoms-svf",           a: 552,  b: 579 },
  { name: "atoms-biquad",        a: 581,  b: 629 },
  { name: "atoms-reson",         a: 631,  b: 665 },
  { name: "atoms-sat-curves",    a: 775,  b: 790 },
  { name: "atoms-ad",            a: 914,  b: 950 },
  { name: "atoms-pan-fft",       a: 985,  b: 1018 },
  { name: "atoms-fastmath",      a: 1032, b: 1044 },
  { name: "organelles-modal",    a: 1222, b: 1304 },
  { name: "studio-comp",         a: 1953, b: 1994 },
  { name: "studio-sat-transient",a: 2050, b: 2153 },
  { name: "studio-eq3",          a: 2155, b: 2173 },
  { name: "studio-paracomp",     a: 2230, b: 2253 },
  { name: "keys-wavetables",     a: 2320, b: 2392 },
  { name: "drums-voices",        a: 3161, b: 3777 },
  { name: "kits-slots",          a: 3795, b: 3795 },
  { name: "kits-kit",            a: 3800, b: 3891 },
  { name: "patches-kitbank",     a: 4298, b: 4438,
    head: "var DD_KITBANK = (function () {", tail: "})();" },
  { name: "rhythm-metric",       a: 4862, b: 4887 },
  { name: "grooves-grammar",     a: 5726, b: 6258 },
  { name: "export-crc32",        a: 7354, b: 7368 },
  { name: "export-zipstore",     a: 7501, b: 7534 }
];

/* sanity anchors: the first line of each range must look like this (prefix
   match) — a donor edit that shifts lines fails loudly, never silently */
const ANCHORS = {
  "export-crc32": "/* ── CRC-32",
  "export-zipstore": "/* ── ZIP, store-only",
  "rhythm-metric": "function metricWeights",
  "grooves-grammar": "/*<<<KNOCK-SEAM:knock/k05-grooves.js>>>*/",
  "atoms-numbers": "var TAU",
  "atoms-rng": "/* ── deterministic randomness",
  "atoms-dcblock": "/* ── DC blocker",
  "atoms-onepole": "/* ── one-pole filters",
  "atoms-svf": "/* ── state variable filter",
  "atoms-biquad": "/* ── RBJ biquad",
  "atoms-reson": "/* ── two-pole resonator",
  "atoms-sat-curves": "/* ── saturation",
  "atoms-ad": "function AD(sr)",
  "atoms-pan-fft": "/* ── stereo placement",
  "atoms-fastmath": "var CR = 16;",
  "organelles-modal": "function ModalBank(sr, n)",
  "studio-comp": "/* ── compressor",
  "studio-sat-transient": "/* ── saturation, properly",
  "studio-eq3": "/* ── three-band channel EQ",
  "studio-paracomp": "/* ── parallel compression",
  "keys-wavetables": "/* ── shared wavetable set",
  "drums-voices": "/*<<<KNOCK-SEAM:src/03b-drums.js>>>*/",
  "kits-slots": "var KIT_SLOTS",
  "kits-kit": "/* ── the drum kit",
  "patches-kitbank": "kit: (function () {"
};

function sliceDonor(donorLines, m) {
  const first = donorLines[m.a - 1];
  const want = ANCHORS[m.name];
  if (want && !first.trimStart().startsWith(want) && !first.startsWith(want))
    throw new Error("anchor drift at " + m.name + " (line " + m.a + "): " + JSON.stringify(first.slice(0, 60)));
  const lines = donorLines.slice(m.a - 1, m.b).slice();
  if (m.head) lines[0] = m.head;
  if (m.tail) lines[lines.length - 1] = m.tail;
  return lines.join("\n");
}

/* the adapted glue that lives INSIDE the IIFE (clearly not donor code) */
const GLUE = `
/* ═══ adapted glue — NOT donor code (everything above this line is sliced
   verbatim from dreamdrummer_22.html by mine/dd22_port.js) ═══
   kitPatch() mirrors the donor's getPatch() clone/merge logic exactly, minus
   the family lookup and the TONE_TRIM axis (keys-only in the donor).
   renderHit() bakes ONE hit of one kit slot offline through the kit's own
   bus (EQ → tube → parallel compression), exactly as the donor mixes it —
   the same bake-to-buffer pattern the round-3 perc port (ldrBuf) proved. */
var KIT_NAMES = ["neptune","timb","ewf","trapK","hyphyK","boombap","afroK","latinK","houseK","softK","cine"];
function cloneVal(v){
  if (Array.isArray(v)) { var a=[]; for (var i=0;i<v.length;i++) a.push(cloneVal(v[i])); return a; }
  if (v && typeof v === "object") { var o={}; for (var k in v) o[k]=cloneVal(v[k]); return o; }
  return v;
}
function kitPatch(name){
  var base = DD_KITBANK._base, p = DD_KITBANK[name] || {}, out = {}, k;
  for (k in base) out[k] = cloneVal(base[k]);
  for (k in p) {
    if (p[k] && typeof p[k] === "object" && !Array.isArray(p[k]) && out[k] && typeof out[k] === "object" && !Array.isArray(out[k])) {
      for (var q in p[k]) out[k][q] = cloneVal(p[k][q]);
    } else out[k] = cloneVal(p[k]);
  }
  return out;
}
var _tables = null;
function tables(){ return _tables || (_tables = buildWavetables()); }
function seedFor(s){ var h=2166136261; for (var i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619); } return h>>>0; }
function renderHit(name, slot, vel, sr){
  var kit = new Kit(sr, makeRng(seedFor(name+"|"+slot+"|"+vel)), tables());
  kit.setPatch(kitPatch(name));
  kit.trig(slot, vel);
  var cap = Math.ceil(sr*4.5), N=512;
  var L=new Float32Array(cap), R=new Float32Array(cap), n=0;
  var lb=new Float32Array(N), rb=new Float32Array(N);
  while (n<cap){
    var m=Math.min(N,cap-n), i;
    for (i=0;i<m;i++){ lb[i]=0; rb[i]=0; }
    kit.render(lb,rb,m);
    L.set(lb.subarray(0,m),n); R.set(rb.subarray(0,m),n); n+=m;
    if (!kit.busy()) break;
  }
  var end=n-1; while (end>64 && Math.abs(L[end])<1e-4 && Math.abs(R[end])<1e-4) end--;
  var len=Math.max(64, Math.min(n, end+800));
  return { L:L.slice(0,len), R:R.slice(0,len) };
}
/* ═══ the style engine (round 7, cycle 37) — adapted glue over the donor's
   grammar data. The CELLS (KPAT/KPAT12) and the STYLES (gens, swing, feel
   numbers, lineage) are the donor's, verbatim above; kRealize() walks them
   with this file's helpers into one deterministic 2-bar plan on TRITON kit
   zones + this file's LDR_RECIPE percussion names + an abstract 808 line
   (semitone offsets, re-rooted to the song at play time — any key, any
   scale, the round-5 law). Swing is baked into the step values per the
   donor's measured MPC math: only the 2nd 16th of each 8th pair moves, and
   the kick may carry its own ratio (dual swing, Frane 2017). */
var STYLE2KIT = { knock:"hyphyK", crunk:"trapK", bounce:"hyphyK", miami:"trapK",
  dembow:"latinK", drill:"trapK", trap:"trapK", foot:"houseK", gogo:"ewf",
  line:"afroK", jungle:"neptune", piano:"softK", batucada:"afroK",
  bell:"afroK", house:"houseK", bap:"boombap", funk:"ewf" };
function kRealize(styleKey, rng, bellHits){
  var st = KSTYLES[styleKey]; if (!st) return null;
  var g = st.gens, steps2 = st.div === 3 ? 24 : 32, beats2 = st.beats * 2;
  var out = { grid: steps2/2, kit: [], sub: [], perc: [],
    subReg: g.sub ? g.sub.reg : null, subGap: g.sub ? (g.sub.phraseGap||0) : 0,
    hum: st.hum, fill: st.fill, label: st.label, place: st.place };
  /* swing:0 in the style data flags a MACHINE (the donor: "machine genres
     stay machines on purpose") — it is NOT MPC 0%, which kswing() would
     read as minus two steps */
  var sw = st.swing ? kswing(st.swing) : 0;
  var swK = (st.kickSwing !== undefined && st.kickSwing) ? kswing(st.kickSwing) : sw;
  var sfor = function(stp,lane){ var s2=lane==="kick"?swK:sw;
    return (Math.round(stp)%2===1)? stp+s2 : stp; };
  var kp = g.kick.pat12? KPAT12[g.kick.pat12] :
           g.kick.patAB? KPAT[g.kick.patAB[rng()<.5?0:1]] : KPAT[g.kick.pat];
  if (kp) kOrnament(kp, rng, g.kick).forEach(function(e){
    out.kit.push({ step:sfor(e.step,"kick"), vel:e.vel, zone:0 }); });
  if (g.kick.bigFour!==undefined) out.kit.push(   /* bass drum and cymbal together */
    { step:g.kick.bigFour, vel:1, zone:0 }, { step:g.kick.bigFour, vel:.7, zone:4 });
  var taken = {};
  out.kit.forEach(function(e){ taken[Math.round(e.step)]=1; });
  var sn = g.snare||{};
  if (sn.pat && KPAT[sn.pat]) KPAT[sn.pat].forEach(function(h){
    out.kit.push({ step:sfor(h[0],"snare"), vel:h[1], zone:1 }); taken[h[0]]=1; });
  (sn.at||[]).forEach(function(s){ out.kit.push({ step:sfor(s,"snare"), vel:sn.vel||.9, zone:1 }); taken[s]=1; });
  (sn.clapAt||[]).forEach(function(s,i){
    var stp=(sn.shiftP&&sn.shiftTo&&rChance(rng,sn.shiftP))? sn.shiftTo[i] : s;
    out.kit.push({ step:sfor(stp,"snare"), vel:sn.clapVel||.8, zone:3 }); taken[stp]=1; });
  (sn.rim||[]).forEach(function(s){ if(!sn.rimP||rChance(rng,sn.rimP))
    out.kit.push({ step:sfor(s,"snare"), vel:.5+.2*rng(), zone:2 }); });
  if (sn.caixa) KPAT.telecoteco.forEach(function(h){
    out.kit.push({ step:sfor(h[0],"snare"), vel:h[1]*.8, zone:1 }); });
  if (sn.ghosts) kGhosts(steps2, beats2, rng, taken, sn.ghosts).forEach(function(e){
    out.kit.push({ step:e.step, vel:e.vel, zone:1 }); });
  var ht = g.hat||{};
  if (!ht.none) kHats(steps2, beats2, rng, ht).forEach(function(e){
    out.kit.push({ step:sfor(e.step,"hat"), vel:e.vel, zone:e.slot===3?10:6 }); });
  /* the 808 line, stored as OFFSETS: re-rooted to the song's tonic at play
     time, clamped back into the style's register there */
  if (g.sub && g.sub.steps){
    var abs = {}; for (var q in g.sub) abs[q]=g.sub[q]; abs.reg=[-24,24];
    out.sub = kSubLine(steps2, rng, abs, 0);
  }
  var plan = [];
  (g.perc||[]).concat(g.aux||[]).forEach(function(e){
    var pat = e[1];
    if (typeof pat === "string" && pat !== "BELL") pat = KPAT12[pat] || KPAT[pat] || [];
    if (e[0]==="rim"){ (pat||[]).forEach(function(h){ if(e[2]||rChance(rng,.6))
      out.kit.push({ step:h[0], vel:h[1], zone:2 }); }); return; }
    if (e[0]==="DJEMBE"){ (pat||[]).forEach(function(h){
      var nm = h[2]==="B"?"djembeB":h[2]==="S"?"djembeS":"djembeT";
      if (e[2]||rChance(rng,.7)) out.perc.push({ step:h[0], vel:h[1]*(0.85+0.3*rng()), name:nm }); });
      return; }
    if (pat==="BELL"){ /* the timeline: the host hands in its own bembe bell */
      (bellHits||[]).forEach(function(h){
        out.perc.push({ step:h[0], vel:h[1], name:"agogoH" });
        out.perc.push({ step:h[0]+steps2/2, vel:h[1]*.94, name:"agogoH" }); });
      return; }
    plan.push([e[0], pat, e[2]]);
  });
  kPlanHits(plan, steps2, rng, 0.5).forEach(function(e){
    out.perc.push({ step:e.step, vel:e.vel, name:e.perc, bend:e.bend }); });
  out.kit.sort(function(a,b){ return a.step-b.step; });
  out.perc.sort(function(a,b){ return a.step-b.step; });
  return out;
}
/* phrase-end fills by the style's own device — adapted from the donor's fill
   grammar: every fill is an acceleration toward an arrival (kRoll's law),
   landing ON the next downbeat. 'cut' returns null: the field empties. */
function kFill(type, rng, perBar){
  if (type==="cut") return null;
  if (type==="rolls32") return kRoll(perBar-4, 4, 2, .25, .95, 1);
  if (type==="rollbar") return kRoll(0, perBar, 1, .2, .9, 1);
  if (type==="rolls16") return kRoll(perBar-4, 4, 1, .25, .9, 1);
  if (type==="stutter") return kRoll(perBar-2, 2, 2, .5, .9, 0);
  var out=[], i;
  if (type==="toms"){ var z=[9,7,5];
    for (i=0;i<6;i++) out.push({ step:perBar-6+i, vel:.55+.07*i, slot:z[Math.floor(i/2)] }); }
  else if (type==="chop") [[perBar-6,.9],[perBar-5,.3],[perBar-3,.85],[perBar-2,.4],[perBar-1,.7]]
    .forEach(function(p){ out.push({ step:p[0], vel:p[1], slot:1 }); });
  else if (type==="djembe") for (i=0;i<6;i++)
    out.push({ step:perBar-6+i, vel:.5+.08*i, perc:i%3===2?"djembeS":"djembeT" });
  return out;
}
return { KIT_NAMES:KIT_NAMES, KIT_SLOTS:KIT_SLOTS, KITBANK:DD_KITBANK,
         kitPatch:kitPatch, renderHit:renderHit, Kit:Kit, makeRng:makeRng, tables:tables,
         KPAT:KPAT, KPAT12:KPAT12, KSTYLES:KSTYLES, KSTYLE_KEYS:KSTYLE_KEYS,
         STYLE2KIT:STYLE2KIT, kRealize:kRealize, kFill:kFill, kswing:kswing,
         metricWeights:metricWeights, crc32:crc32, encodeZipStore:encodeZipStore };
`;

function buildBlock(donorText) {
  const donorLines = donorText.split("\n");
  const parts = MANIFEST.map(m =>
    "/* —— dd22 slice: " + m.name + " (donor L" + m.a + "-" + m.b + ") —— */\n" +
    sliceDonor(donorLines, m));
  return "/*DD22-BEGIN*/\n" +
    "/* ═══ DD22 KIT ENGINE — dreamdrummer_22's drum kits, loadable on the\n" +
    "   TRITON (round 7). Sliced VERBATIM from the byte-identical donor in\n" +
    "   this directory by mine/dd22_port.js; the fidelity gate in tests.js\n" +
    "   re-derives every slice from the donor and byte-compares. One IIFE so\n" +
    "   donor globals never touch this file's. ═══ */\n" +
    "const DD22=(function(){\n\"use strict\";\n" +
    parts.join("\n") + "\n" + GLUE + "})();\n" +
    "/*DD22-END*/";
}

function inject() {
  const donor = fs.readFileSync(DONOR, "utf8");
  const art = fs.readFileSync(ART, "utf8");
  const block = buildBlock(donor);
  let out;
  if (art.includes("/*DD22-BEGIN*/")) {
    const a = art.indexOf("/*DD22-BEGIN*/");
    const bTag = "/*DD22-END*/";
    const b = art.indexOf(bTag);
    if (b < 0) throw new Error("DD22-BEGIN without DD22-END");
    out = art.slice(0, a) + block + art.slice(b + bTag.length);
  } else {
    const anchor = "const LOCKS={key:false,rhythm:false};";
    const i = art.indexOf(anchor);
    if (i < 0) throw new Error("injection anchor not found");
    out = art.slice(0, i) + block + "\n" + art.slice(i);
  }
  fs.writeFileSync(ART, out);
  console.log("DD22 block injected: " + block.length + " bytes, " +
    MANIFEST.length + " slices, artifact now " + out.length + " bytes");
}

module.exports = { MANIFEST, ANCHORS, sliceDonor, buildBlock, GLUE };
if (require.main === module) inject();
