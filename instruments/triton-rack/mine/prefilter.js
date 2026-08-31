"use strict";
/* Mechanical pre-filter: 184k candidates → shortlist per bucket for the
   curation court. Scores are structural (dynamics present, feel present,
   space present, complementarity) — the court does the musical judging. */
const fs = require("fs");
const drums = JSON.parse(fs.readFileSync("drum_candidates.json"));
const mel = JSON.parse(fs.readFileSync("quartet_candidates.json"));

function styleFamily(s) { return (s || "").split("/")[0]; }

const buckets = {};
const put = (key, c, score) => { (buckets[key] = buckets[key] || []).push({ ...c, score: +score.toFixed(3) }); };

drums.forEach(c => {
  const s = c.stats;
  if (c.fill) {
    if (s.n < 8 || s.velRange < 0.25) return;
    const toms = 1; /* fills judged by court; structural floor only */
    const score = s.velRange * 2 + Math.min(s.n, 20) / 20 + (s.lanes >= 4 ? .5 : 0)
      + (s.devSd > 0.01 && s.devSd < 0.12 ? .6 : 0);
    put("dr-fill", c, score);
  } else {
    if (s.lanes < 3 || s.velRange < 0.2) return;
    if (s.devSd < 0.005 || s.devSd > 0.14) return;
    const score = s.velRange + Math.min(s.ghosts, 6) / 6 + Math.min(s.backbeat, 4) / 4
      + (Math.abs(s.lag1) < 1 ? Math.max(0, s.lag1) : 0)
      + (s.hats >= 8 ? .4 : 0) + (s.kicks >= 2 && s.kicks <= 12 ? .3 : 0);
    put("dr-" + styleFamily(c.style), c, score);
  }
});

mel.forEach(c => {
  const s = c.stats;
  if (c.kind === "bs") {
    if (s.density > 2.4 || s.span < 4) return;
    const score = s.stepwise + Math.min(s.span, 17) / 17 + (s.density >= .5 && s.density <= 1.8 ? .8 : 0)
      + (s.offbeat >= .1 ? .3 : 0) + Math.min(s.turns, 6) / 12;
    put("bs-" + c.mode, c, score);
  } else if (c.kind === "cp") {
    /* THE COUNTER: sparse, complementary, singable — space for a vocalist */
    if (s.density > 1.6 || s.clash > 0.6 || s.span < 3 || s.span > 19) return;
    const score = (1 - s.clash) * 1.2 + s.stepwise + (s.restFrac >= .1 ? .6 : 0)
      + (s.density <= 1.1 ? .6 : .2) + Math.min(s.offbeat, .6) + Math.min(s.turns, 5) / 10;
    put("cp-" + c.mode, c, score);
  } else if (c.kind === "em") {
    if (s.span < 4 || s.lenQn > 3.5) return;
    const score = Math.min(s.span, 14) / 14 + (s.n >= 5 ? .5 : .2) + (s.lenQn <= 2.2 ? .5 : 0);
    put("em-" + c.mode + "-" + s.dir, c, score);
  }
});

/* per-bucket: sort by score, cap per source-file (diversity), take top N */
const TOP = { dr: 40, bs: 60, cp: 70, em: 40 };
const shortlist = {};
Object.entries(buckets).forEach(([k, arr]) => {
  arr.sort((a, b) => b.score - a.score);
  const perSrc = {}, keep = [];
  const cap = TOP[k.slice(0, 2)] || 40;
  for (const c of arr) {
    const srcKey = c.src + "|" + (c.drummer || c.composer || "");
    perSrc[srcKey] = (perSrc[srcKey] || 0) + 1;
    if (perSrc[srcKey] > 3) continue;
    keep.push(c);
    if (keep.length >= cap) break;
  }
  shortlist[k] = keep;
});
fs.writeFileSync("shortlist.json", JSON.stringify(shortlist));
const counts = {};
Object.entries(shortlist).forEach(([k, v]) => counts[k] = v.length);
console.log(JSON.stringify({ buckets: counts,
  total: Object.values(shortlist).reduce((a, v) => a + v.length, 0) }));
