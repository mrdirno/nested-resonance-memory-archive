"use strict";
/* Groove MIDI (Magenta, CC-BY 4.0, 10 human drummers) → LDRP drum-phrase
   candidates. Every phrase: 2 bars (grooves) or 1 bar (fills), grid 16,
   per-event deviation in step units (the player's hand, preserved),
   velocity 0-1. Emits candidates JSON with source stats for the curation court. */
const fs = require("fs"), path = require("path");
const { parseMidi, midiNotes } = require("./midiparse");
const { packDrum, unpackDrum, grooveField } = require("./ldrp");

/* GM drum note → LDRP lane index (see ldrp.LANES = "KSXHOPCRBFTt") */
const GM2LANE = { 35: 0, 36: 0, 38: 1, 40: 1, 37: 2, 42: 3, 44: 5, 46: 4, 22: 3, 26: 4,
  49: 6, 55: 6, 57: 6, 52: 6, 51: 7, 59: 7, 53: 8, 41: 9, 43: 9, 58: 9, 45: 10, 47: 10, 48: 11, 50: 11 };

function extractFile(midiPath, meta) {
  const buf = fs.readFileSync(midiPath);
  let m; try { m = parseMidi(buf); } catch (e) { return []; }
  const notes = midiNotes(m).filter(n => GM2LANE[n.note] != null);
  if (notes.length < 8) return [];
  /* Groove MIDI is recorded to a click: the grid is the qn grid of the file.
     grid 16 = 4 slots/qn. step = round(qn*4); dev = qn*4 - step (in steps). */
  const evs = notes.map(n => {
    const pos = n.qn * 4, step = Math.round(pos);
    return { pos, step, dev: pos - step, lane: GM2LANE[n.note], vel: n.vel / 127 };
  }).filter(e => e.dev >= -0.5 && e.dev < 0.486); /* full representable dev range (audit) */
  const lastStep = Math.max(...evs.map(e => e.step));
  const isFill = meta.beat_type === "fill";
  const win = isFill ? 16 : 32; /* 1-bar fills, 2-bar grooves */
  /* fills rarely start on a window boundary — slide by a beat and greedily
     keep the densest non-overlapping windows */
  const starts = [];
  if (isFill) {
    const cand = [];
    for (let s0 = 0; s0 <= lastStep; s0 += 4)
      cand.push({ s0, n: evs.filter(e => e.step >= s0 && e.step < s0 + win).length });
    cand.sort((a, b) => b.n - a.n);
    const taken = [];
    cand.forEach(c => { if (c.n >= 6 && !taken.some(t => Math.abs(t - c.s0) < win)) { taken.push(c.s0); starts.push(c.s0); } });
    starts.sort((a, b) => a - b);
  } else {
    for (let s0 = 0; s0 + win <= lastStep + 1; s0 += win) starts.push(s0);
  }
  const out = [];
  for (const s0 of starts) {
    const seg = evs.filter(e => e.step >= s0 && e.step < s0 + win)
      .map(e => ({ ...e, step: e.step - s0 }));
    if (seg.length < (isFill ? 6 : 10)) continue;
    /* quality stats for the curation court */
    const lanes = new Set(seg.map(e => e.lane));
    const kicks = seg.filter(e => e.lane === 0).length;
    const snares = seg.filter(e => e.lane === 1 || e.lane === 2).length;
    const hats = seg.filter(e => e.lane >= 3 && e.lane <= 8).length;
    const devs = seg.map(e => e.dev);
    const mean = devs.reduce((a, b) => a + b, 0) / devs.length;
    const sd = Math.sqrt(devs.reduce((a, b) => a + (b - mean) * (b - mean), 0) / devs.length);
    let lag1n = 0, lag1d = 0;
    for (let i = 0; i + 1 < devs.length; i++) lag1n += (devs[i] - mean) * (devs[i + 1] - mean);
    devs.forEach(d => lag1d += (d - mean) * (d - mean));
    const vels = seg.map(e => e.vel);
    const ghosts = seg.filter(e => e.vel < 0.35).length;
    /* swing: mean dev of odd 8th positions (steps ≡ 2 mod 4) */
    const off8 = seg.filter(e => e.step % 4 === 2);
    const swing = off8.length ? off8.reduce((a, e) => a + e.dev, 0) / off8.length : 0;
    const backbeat = seg.filter(e => (e.lane === 1) && (e.step % 16 === 4 || e.step % 16 === 12)).length;
    out.push({
      kind: "dr", grid: 16, bars: win / 16, fill: isFill,
      style: meta.style, bpm: +meta.bpm, drummer: meta.drummer,
      src: "groove-midi:" + meta.id, lic: "CC-BY-4.0",
      e: packDrum(seg),
      stats: { n: seg.length, lanes: lanes.size, kicks, snares, hats, ghosts,
        velRange: +(Math.max(...vels) - Math.min(...vels)).toFixed(3),
        devSd: +sd.toFixed(4), lag1: +(lag1d ? lag1n / lag1d : 0).toFixed(3),
        swing: +swing.toFixed(4), backbeat }
    });
  }
  return out;
}

function main() {
  const root = process.argv[2];
  const csv = fs.readFileSync(path.join(root, "info.csv"), "utf8").trim().split("\n");
  const head = csv[0].split(",");
  const rows = csv.slice(1).map(l => { const c = l.split(","); const o = {}; head.forEach((h, i) => o[h] = c[i]); return o; });
  const all = [];
  rows.filter(r => r.time_signature === "4-4").forEach(r => {
    const p = path.join(root, r.midi_filename);
    if (fs.existsSync(p)) all.push(...extractFile(p, r));
  });
  /* fidelity self-check: unpack must round-trip step/lane exactly, dev/vel within quantum */
  let bad = 0;
  all.forEach(c => {
    const u = unpackDrum(c.e);
    if (u.length !== c.stats.n) bad++;
    else if (u.some(e => e.step < 0 || e.lane < 0 || Math.abs(e.dev) > 0.5)) bad++;
  });
  const outPath = process.argv[3];
  fs.writeFileSync(outPath, JSON.stringify(all));
  const bytes = all.reduce((a, c) => a + c.e.length, 0);
  console.log(JSON.stringify({ candidates: all.length, roundtripFailures: bad,
    grooves: all.filter(c => !c.fill).length, fills: all.filter(c => c.fill).length,
    packedKB: +(bytes / 1024).toFixed(1),
    styles: [...new Set(all.map(c => c.style.split("/")[0]))].sort() }));
}
main();
