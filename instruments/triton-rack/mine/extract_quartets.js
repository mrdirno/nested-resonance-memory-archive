"use strict";
/* OpenScore StringQuartets (CC0) → melodic LDRP candidates.
   cello → bs (bass lines) · violin II + viola → cp (counter-lines) ·
   violin I → em (embellishment gestures: short runs and turns).
   Pitches stored as semitones-from-tonic (any-key/any-scale replay);
   timing is the score grid — feel comes from groove transfer at play time.
   Windows: 8 qn (32 sixteenth slots), slid by 4 qn, monophonic voice 1. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const { parseMxlXml } = require("./mxlparse");
const { packMel, unpackMel } = require("./ldrp");

const MAJ = [0, 2, 4, 5, 7, 9, 11], MIN = [0, 2, 3, 5, 7, 8, 10];
function keyAt(keys, qn) {
  let k = keys[0] || { fifths: 0, mode: "major" };
  for (const x of keys) { if (x.qn <= qn) k = x; else break; }
  const tonicPc = ((k.fifths * 7) % 12 + 12 + (k.mode === "minor" ? 9 : 0)) % 12;
  return { tonicPc, mode: k.mode === "minor" ? "minor" : "major", modeExplicit: !!k.hasMode };
}
/* MuseScore exports usually omit <mode> — infer per window: does the relative
   minor tonic (la) anchor the phrase more than the major tonic (do)?
   Anchors = first, last, longest, and lowest notes, duration-weighted. */
function inferMode(seg, majTonicPc) {
  if (!seg.length) return "major";
  const w = pc => {
    let v = 0;
    seg.forEach((n, i) => {
      if ((((n.midi - majTonicPc) % 12) + 12) % 12 !== pc) return;
      v += Math.min(4, n.durQn) + (i === 0 ? 1.5 : 0) + (i === seg.length - 1 ? 2.5 : 0);
    });
    return v;
  };
  /* la + its dominant (mi) vs do + its dominant (sol) */
  return (w(9) + w(4) * .4) > (w(0) + w(7) * .4) * 1.35 ? "minor" : "major";
}
function roleFor(name, idx) {
  const n = (name || "").toLowerCase();
  if (n.includes("cello") || n.includes("violonc")) return "bs";
  if (n.includes("viola")) return "cp";
  if (n.includes("violin")) return n.includes("ii") || n.includes("2") ? "cp" : "vln1";
  return idx === 3 ? "bs" : idx === 0 ? "vln1" : "cp";
}
function windows(notes, keys, kind, srcMeta, celloOnsets) {
  const out = [];
  if (!notes.length) return out;
  const endQn = notes[notes.length - 1].qn + 8;
  for (let q0 = 0; q0 < endQn; q0 += 4) {
    const seg = notes.filter(n => n.qn >= q0 && n.qn < q0 + 8 && !n.grace && n.voice === notes[0].voice);
    if (seg.length < 3 || seg.length > 26) continue;
    const key = keyAt(keys, q0);
    let mode = key.mode, tonicPc = key.tonicPc;
    if (!key.modeExplicit) {
      mode = inferMode(seg, key.tonicPc);
      if (mode === "minor") tonicPc = (key.tonicPc + 9) % 12; /* re-root on la */
    }
    const tonicRef = tonicPc + 48;
    const evs = [];
    let ok = true;
    for (const n of seg) {
      const step = Math.round((n.qn - q0) * 4);
      const deg = n.midi - tonicRef;
      if (step < 0 || step > 31 || deg < -24 || deg > 47) { ok = false; break; }
      evs.push({ step, deg, dur: Math.max(.25, Math.min(8.75, n.durQn * 4)), vel: n.dyn });
    }
    if (!ok || !evs.length) continue;
    /* dedup same-step (voice overlaps) keep first */
    const seen = new Set(), uniq = [];
    evs.forEach(e => { if (!seen.has(e.step)) { seen.add(e.step); uniq.push(e); } });
    if (uniq.length < 3) continue;
    /* stats for the curation court */
    const degs = uniq.map(e => e.deg);
    const span = Math.max(...degs) - Math.min(...degs);
    let stepwise = 0, leaps = 0, turns = 0;
    for (let i = 1; i < degs.length; i++) {
      const iv = Math.abs(degs[i] - degs[i - 1]);
      if (iv > 0 && iv <= 2) stepwise++; else if (iv > 4) leaps++;
      if (i >= 2 && Math.sign(degs[i] - degs[i - 1]) !== Math.sign(degs[i - 1] - degs[i - 2])) turns++;
    }
    const density = uniq.length / 8; /* notes per qn */
    const restFrac = 1 - Math.min(1, uniq.reduce((a, e) => a + Math.min(e.dur, 32 - e.step), 0) / 32);
    /* complementarity vs the cello in the same window (space for the low end) */
    let clash = 0;
    if (celloOnsets) {
      const cSteps = new Set(celloOnsets.filter(q => q >= q0 && q < q0 + 8).map(q => Math.round((q - q0) * 4)));
      clash = uniq.filter(e => cSteps.has(e.step)).length / uniq.length;
    }
    const offbeat = uniq.filter(e => e.step % 4 !== 0).length / uniq.length;
    out.push({
      kind, grid: 16, bars: 2, mode,
      src: srcMeta.src, work: srcMeta.work, composer: srcMeta.composer, lic: "CC0",
      e: packMel(uniq),
      stats: { n: uniq.length, span, stepwise: +(stepwise / Math.max(1, degs.length - 1)).toFixed(2),
        leaps, turns, density: +density.toFixed(2), restFrac: +restFrac.toFixed(2),
        clash: +clash.toFixed(2), offbeat: +offbeat.toFixed(2) }
    });
  }
  return out;
}
/* embellishment gestures from violin I: consecutive short-note runs of 4-9 notes */
function gestures(notes, keys, srcMeta) {
  const out = [];
  const line = notes.filter(n => !n.grace && n.durQn <= 0.75);
  let run = [];
  const flush = () => {
    if (run.length >= 4 && run.length <= 9) {
      const q0 = Math.floor(run[0].qn * 4) / 4;
      const key = keyAt(keys, q0);
      let mode = key.mode, tonicPc = key.tonicPc;
      if (!key.modeExplicit) {
        mode = inferMode(run, key.tonicPc);
        if (mode === "minor") tonicPc = (key.tonicPc + 9) % 12;
      }
      const tonicRef = tonicPc + 48;
      const evs = [];
      let ok = true;
      for (const n of run) {
        const step = Math.round((n.qn - q0) * 4);
        const deg = n.midi - tonicRef;
        if (step < 0 || step > 31 || deg < -24 || deg > 47) { ok = false; break; }
        evs.push({ step, deg, dur: Math.max(.25, Math.min(4, n.durQn * 4)), vel: n.dyn });
      }
      if (ok && evs.length >= 4) {
        const degs = evs.map(e => e.deg);
        const span = Math.max(...degs) - Math.min(...degs);
        const dir = degs[degs.length - 1] > degs[0] ? "up" : "down";
        const lenQn = run[run.length - 1].qn + run[run.length - 1].durQn - run[0].qn;
        if (lenQn <= 4.5)
          out.push({ kind: "em", grid: 16, bars: 2, mode,
            src: srcMeta.src, work: srcMeta.work, composer: srcMeta.composer, lic: "CC0",
            e: packMel(evs),
            stats: { n: evs.length, span, dir, lenQn: +lenQn.toFixed(2) } });
      }
    }
    run = [];
  };
  for (let i = 0; i < line.length; i++) {
    if (!run.length) { run.push(line[i]); continue; }
    const prev = run[run.length - 1];
    const gap = line[i].qn - (prev.qn + prev.durQn);
    if (gap <= 0.26 && line[i].qn - prev.qn >= 0.22 && line[i].qn - run[0].qn < 4.5) run.push(line[i]);
    else { flush(); run.push(line[i]); }
  }
  flush();
  return out;
}

function main() {
  const root = process.argv[2], outPath = process.argv[3];
  const files = cp.execSync(`find ${JSON.stringify(root)} -name "*.mxl"`).toString().trim().split("\n");
  const all = [];
  let parsed = 0, failed = 0;
  for (const f of files) {
    let xml;
    try { xml = cp.execSync(`unzip -p ${JSON.stringify(f)} -x "META-INF/*"`, { maxBuffer: 64 * 1024 * 1024 }).toString(); }
    catch (e) { failed++; continue; }
    let doc;
    try { doc = parseMxlXml(xml); } catch (e) { failed++; continue; }
    if (!doc.parts.length) { failed++; continue; }
    parsed++;
    const composer = (xml.match(/<creator type="composer">([^<]*)</) || [])[1] || "unknown";
    const work = (xml.match(/<work-title>([^<]*)</) || [])[1] || path.basename(f, ".mxl");
    const srcMeta = { src: "openscore-quartets:" + path.basename(f, ".mxl"), work, composer };
    const cello = doc.parts.find((p, i) => roleFor(p.name, i) === "bs");
    const celloOnsets = cello ? cello.notes.map(n => n.qn) : null;
    doc.parts.forEach((p, i) => {
      const role = roleFor(p.name, i);
      const keys = p.keys.length ? p.keys : [{ qn: 0, fifths: 0, mode: "major" }];
      if (role === "bs") all.push(...windows(p.notes, keys, "bs", srcMeta, null));
      else if (role === "cp") all.push(...windows(p.notes, keys, "cp", srcMeta, celloOnsets));
      else if (role === "vln1") all.push(...gestures(p.notes, keys, srcMeta));
    });
  }
  let bad = 0;
  all.forEach(c => { const u = unpackMel(c.e); if (!u.length || u.some(e => e.step < 0)) bad++; });
  fs.writeFileSync(outPath, JSON.stringify(all));
  const bytes = all.reduce((a, c) => a + c.e.length, 0);
  console.log(JSON.stringify({ files: files.length, parsed, failed, candidates: all.length,
    bs: all.filter(c => c.kind === "bs").length, cp: all.filter(c => c.kind === "cp").length,
    em: all.filter(c => c.kind === "em").length, roundtripFailures: bad,
    packedKB: +(bytes / 1024).toFixed(1) }));
}
main();
