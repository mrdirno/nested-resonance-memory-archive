"use strict";
/* Mechanical fidelity gate: for every phrase in a selection file, re-derive
   from the RAW source (Groove MIDI file / OpenScore .mxl) and confirm the
   packed LDRP events reproduce source events exactly (within encoder quanta)
   at SOME window offset — the offset is re-discovered, not trusted.
   Usage: node verify_phrase.js <selection.json>
   selection.json = [{bucket, i}] — indices into shortlist.json buckets. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const { parseMidi, midiNotes } = require("./midiparse");
const { parseMxlXml } = require("./mxlparse");
const { unpackDrum, unpackMel } = require("./ldrp");
const GROOVE_ROOT = path.join(__dirname, "..", "groove", "groove");
const OSQ_ROOT = "/home/user/aim-qmul/osq/scores";
const GM2LANE = { 35: 0, 36: 0, 38: 1, 40: 1, 37: 2, 42: 3, 44: 5, 46: 4, 22: 3, 26: 4,
  49: 6, 55: 6, 57: 6, 52: 6, 51: 7, 59: 7, 53: 8, 41: 9, 43: 9, 58: 9, 45: 10, 47: 10, 48: 11, 50: 11 };
const DEV_TOL = 1 / 36 / 2 + 1e-6, VEL_TOL = 1 / 35 / 2 + 1e-6;

const sl = JSON.parse(fs.readFileSync(path.join(__dirname, "shortlist.json")));
const sel = JSON.parse(fs.readFileSync(process.argv[2]));
const infoRows = (() => {
  const csv = fs.readFileSync(path.join(GROOVE_ROOT, "info.csv"), "utf8").trim().split("\n");
  const head = csv[0].split(",");
  const map = {};
  csv.slice(1).forEach(l => { const c = l.split(","); const o = {}; head.forEach((h, j) => o[h] = c[j]); map[o.id] = o; });
  return map;
})();
const mxlCache = {};
function mxlDoc(base) {
  if (mxlCache[base]) return mxlCache[base];
  const f = cp.execSync(`find ${JSON.stringify(OSQ_ROOT)} -name ${JSON.stringify(base + ".mxl")}`).toString().trim().split("\n")[0];
  if (!f) throw new Error("source mxl not found: " + base);
  const xml = cp.execSync(`unzip -p ${JSON.stringify(f)} -x "META-INF/*"`, { maxBuffer: 64 * 1024 * 1024 }).toString();
  return (mxlCache[base] = parseMxlXml(xml));
}
/* try one window offset: do ALL phrase events match a source event exactly? */
function drumsMatchAt(evs, srcByStep, s0) {
  return evs.every(e => (srcByStep[s0 + e.step] || []).some(n =>
    GM2LANE[n.note] === e.lane &&
    Math.abs((n.qn * 4 - Math.round(n.qn * 4)) - e.dev) < DEV_TOL &&
    Math.abs(n.vel / 127 - e.vel) < VEL_TOL));
}
function melMatchAt(evs, notes, q0steps) {
  /* derive the phrase's tonicRef from its first event, then demand all match */
  const first = evs[0];
  const cands = notes.filter(n => Math.round(n.qn * 4) === q0steps + first.step);
  return cands.some(anchor => {
    const tonicRef = anchor.midi - first.deg;
    return evs.every(e => notes.some(n =>
      Math.round(n.qn * 4) === q0steps + e.step && n.midi === tonicRef + e.deg));
  });
}

let pass = 0, fail = 0;
const failures = [];
for (const { bucket, i } of sel) {
  const c = (sl[bucket] || [])[i];
  if (!c) { fail++; failures.push({ bucket, i, why: "missing candidate" }); continue; }
  try {
    if (c.kind === "dr") {
      const row = infoRows[c.src.replace("groove-midi:", "")];
      const m = parseMidi(fs.readFileSync(path.join(GROOVE_ROOT, row.midi_filename)));
      const notes = midiNotes(m).filter(n => GM2LANE[n.note] != null);
      const srcByStep = {};
      notes.forEach(n => { const s = Math.round(n.qn * 4); (srcByStep[s] = srcByStep[s] || []).push(n); });
      const evs = unpackDrum(c.e);
      const maxStep = Math.max(...Object.keys(srcByStep).map(Number));
      let found = false;
      for (let s0 = 0; s0 <= maxStep && !found; s0 += 4) found = drumsMatchAt(evs, srcByStep, s0);
      if (found) pass++; else { fail++; failures.push({ bucket, i, src: c.src, why: "no window reproduces the phrase" }); }
    } else {
      const doc = mxlDoc(c.src.replace("openscore-quartets:", ""));
      const evs = unpackMel(c.e);
      let found = false;
      for (const p of doc.parts) {
        if (found) break;
        const notes = p.notes;
        if (!notes.length) continue;
        const maxQ = Math.round((notes[notes.length - 1].qn) * 4);
        for (let q0 = 0; q0 <= maxQ && !found; q0 += 16) found = melMatchAt(evs, notes, q0);
        /* gestures start on any quarter, windows on 4-qn boundaries */
        if (!found && c.kind === "em")
          for (let q0 = 0; q0 <= maxQ && !found; q0 += 1) found = melMatchAt(evs, notes, q0);
      }
      if (found) pass++; else { fail++; failures.push({ bucket, i, src: c.src, why: "no part/window reproduces the phrase" }); }
    }
  } catch (err) { fail++; failures.push({ bucket, i, why: String(err.message).slice(0, 80) }); }
}
console.log(JSON.stringify({ pass, fail, failures: failures.slice(0, 20) }));
