"use strict";
/* Assemble the final embedded library from the court's picks.
   Usage: node assemble_library.js court_picks.json out_library.js
   court_picks.json = [{bucket, r:{picks:[{i,name,tags,why}],...}}]
   Every pick re-passes the mechanical fidelity gate before embedding. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const sl = JSON.parse(fs.readFileSync(path.join(__dirname, "shortlist.json")));
const court = JSON.parse(fs.readFileSync(process.argv[2]));

/* 1. collect picks, dedup by packed events (two judges can't pick twins) */
const sel = [], seenE = new Set(), names = new Set();
for (const { bucket, r } of court) {
  if (!r || !r.picks) continue;
  for (const p of r.picks) {
    const c = (sl[bucket] || [])[p.i];
    if (!c) continue;
    if (seenE.has(c.e)) continue;
    seenE.add(c.e);
    const clean = x => String(x || "").replace(/[<>&\\"]/g, "").slice(0, 24);
    let nm = clean(p.name) || "untitled";
    let k = 2; while (names.has(nm)) nm = (clean(p.name) || "untitled").slice(0, 21) + " " + (k++);
    names.add(nm);
    sel.push({ bucket, i: p.i, name: nm, tags: (p.tags || []).slice(0, 4).map(clean), c });
  }
}
/* 2. mechanical fidelity gate on EVERY pick */
fs.writeFileSync(path.join(__dirname, "final_sel.json"), JSON.stringify(sel.map(s => ({ bucket: s.bucket, i: s.i }))));
const gate = JSON.parse(cp.execSync(`node ${JSON.stringify(path.join(__dirname, "verify_phrase.js"))} ${JSON.stringify(path.join(__dirname, "final_sel.json"))}`, { maxBuffer: 16e6 }).toString());
const failKeys = new Set((gate.failures || []).map(f => f.bucket + "#" + f.i));
const kept = sel.filter(s => !failKeys.has(s.bucket + "#" + s.i));

/* 3. build the compact embedded records */
const out = kept.map(s => {
  const c = s.c;
  const rec = { n: s.name, k: c.kind, b: c.bars, e: c.e, src: c.src, tg: s.tags };
  if (c.kind === "dr") {
    rec.s = (c.style || "").split("/")[0];
    rec.bpm = c.bpm; rec.dm = c.drummer;
    if (c.fill) rec.fl = 1;
  } else {
    rec.md = c.mode; rec.cp = (c.composer || "").split(",")[0];
  }
  return rec;
});
/* deterministic order: kind, then style/mode, then name */
out.sort((a, b) => (a.k + (a.s || a.md || "") + a.n).localeCompare(b.k + (b.s || b.md || "") + b.n));
const js = JSON.stringify(out);
fs.writeFileSync(process.argv[3], js);
console.log(JSON.stringify({
  picked: sel.length, gated: gate, embedded: out.length,
  kinds: { dr: out.filter(r => r.k === "dr" && !r.fl).length, fill: out.filter(r => r.fl).length,
    bs: out.filter(r => r.k === "bs").length, cp: out.filter(r => r.k === "cp").length,
    em: out.filter(r => r.k === "em").length },
  bytesKB: +(js.length / 1024).toFixed(1)
}));
