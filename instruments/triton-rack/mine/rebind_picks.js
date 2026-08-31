"use strict";
/* The court judged shortlist_v1; the pipeline was then FIXED (audit) and
   re-extracted. Re-bind each pick to the corrected candidate for the same
   source material: exact packed match first, else same src + best event
   overlap (>=70%). A pick whose corrected form fell out of the new
   shortlist is appended to its bucket so the court's taste outranks the
   mechanical pre-filter. Unmatched picks are dropped (reported).
   Output: court_picks_rebound.json + updated shortlist.json. */
const fs = require("fs");
const { unpackDrum, unpackMel } = require("./ldrp");
const v1 = JSON.parse(fs.readFileSync("shortlist_v1.json"));
const sl = JSON.parse(fs.readFileSync("shortlist.json"));
const court = JSON.parse(fs.readFileSync("court_picks.json"));
const drums = JSON.parse(fs.readFileSync("drum_candidates.json"));
const mel = JSON.parse(fs.readFileSync("quartet_candidates.json"));
const poolFor = kind => kind === "dr" ? drums : mel;

function evKey(c) {
  const evs = c.kind === "dr" ? unpackDrum(c.e) : unpackMel(c.e);
  return evs.map(e => c.kind === "dr" ? e.step + ":" + e.lane : e.step + ":" + e.deg);
}
function overlap(a, b) {
  const B = new Set(b);
  const hit = a.filter(x => B.has(x)).length;
  return hit / Math.max(a.length, b.length);
}
let exact = 0, fuzzy = 0, appended = 0, dropped = 0;
const out = [];
for (const { bucket, r } of court) {
  if (!r || !r.picks) continue;
  const picks = [];
  for (const p of r.picks) {
    const c1 = (v1[bucket] || [])[p.i];
    if (!c1) { dropped++; continue; }
    /* 1. exact packed match inside the new bucket */
    let ni = (sl[bucket] || []).findIndex(c => c.e === c1.e && c.src === c1.src);
    if (ni >= 0) { exact++; picks.push({ ...p, i: ni }); continue; }
    /* 2. best-overlap same-src candidate anywhere in the corrected pool */
    const k1 = evKey(c1);
    let best = null, bestOv = 0;
    for (const c of poolFor(c1.kind)) {
      if (c.src !== c1.src || c.kind !== c1.kind || !!c.fill !== !!c1.fill) continue;
      const ov = overlap(k1, evKey(c));
      if (ov > bestOv) { bestOv = ov; best = c; }
    }
    if (best && bestOv >= 0.7) {
      let idx = (sl[bucket] || []).findIndex(c => c.e === best.e && c.src === best.src);
      if (idx < 0) { sl[bucket] = sl[bucket] || []; sl[bucket].push({ ...best, score: 0 }); idx = sl[bucket].length - 1; appended++; }
      fuzzy++; picks.push({ ...p, i: idx });
    } else dropped++;
  }
  out.push({ bucket, r: { ...r, picks } });
}
fs.writeFileSync("court_picks_rebound.json", JSON.stringify(out));
fs.writeFileSync("shortlist.json", JSON.stringify(sl));
console.log(JSON.stringify({ exact, fuzzy, appended, dropped,
  total: out.reduce((a, b) => a + b.r.picks.length, 0) }));
