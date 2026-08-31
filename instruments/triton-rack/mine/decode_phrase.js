"use strict";
/* Court tool: render shortlist phrases human-readable for judging.
   Usage: node decode_phrase.js <bucket> [start] [count]   — from shortlist.json
   Drums print as a 32-slot piano-roll of lanes; melodic as степ/degree/dur rows. */
const fs = require("fs");
const { unpackDrum, unpackMel, LANES } = require("./ldrp");
const sl = JSON.parse(fs.readFileSync(__dirname + "/shortlist.json"));
const bucket = process.argv[2], start = +(process.argv[3] || 0), count = +(process.argv[4] || 10);
const arr = sl[bucket] || [];
const out = [];
arr.slice(start, start + count).forEach((c, i) => {
  const id = bucket + "#" + (start + i);
  if (c.kind === "dr") {
    const evs = unpackDrum(c.e);
    const slots = c.bars * 16;
    const rows = {};
    evs.forEach(e => {
      const ch = LANES[e.lane];
      rows[ch] = rows[ch] || Array(slots).fill("·");
      rows[ch][e.step] = e.vel > .7 ? "X" : e.vel > .38 ? "x" : "◦";
    });
    const grid = Object.entries(rows).map(([ch, r]) =>
      ch + " " + r.map((v, s) => (s % 4 === 0 ? "" : "") + v).join("")).join("\n");
    out.push(`${id} · ${c.style} · ♩${c.bpm} · ${c.drummer} · score ${c.score}` +
      ` · devSd ${c.stats.devSd} lag1 ${c.stats.lag1} ghosts ${c.stats.ghosts} vr ${c.stats.velRange}\n${grid}`);
  } else {
    const evs = unpackMel(c.e);
    const line = evs.map(e => `${e.step}:${e.deg >= 0 ? "+" : ""}${e.deg}(${e.dur})${e.vel > .75 ? "!" : ""}`).join(" ");
    out.push(`${id} · ${c.kind} ${c.mode || ""} · ${c.composer || ""} · score ${c.score}` +
      ` · ${JSON.stringify(c.stats)}\n  ${line}`);
  }
});
console.log(out.join("\n---\n"));
