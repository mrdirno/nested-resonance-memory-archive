"use strict";
/* LDRP1 — LuckyDreamer phrase format. One phrase = tiny JSON wrapper + packed
   event string. The point: human playing, compressed far below MIDI, key/scale
   agnostic (melodic pitches stored as semitones-from-tonic; timing stored as
   grid step + signed deviation so the feel survives any tempo).

   Packed alphabet: base-36 chars 0-9a-z.
   DRUM event   (5 ch): step(2) dev(1: 1/36-step units, +18 bias) lane(1) vel(1)
   MELODIC event(6 ch): step(2) pitch(2: semis-from-tonic +24 bias) dur(1: 1/4-steps, 35=long) vel(1)
   step = index into grid*bars slots. Phrase kinds: dr drums · bs bass · cp counterpoint · em embellishment.
   Lanes (drums): K kick S snare X sidestick H hat-closed O hat-open P hat-pedal
                  C crash R ride B ride-bell F floor-tom T mid-tom t high-tom */
const A36 = "0123456789abcdefghijklmnopqrstuvwxyz";
const LANES = "KSXHOPCRBFTt";
const enc1 = v => A36[Math.max(0, Math.min(35, Math.round(v)))];
const enc2 = v => { v = Math.max(0, Math.min(1295, Math.round(v))); return A36[(v / 36) | 0] + A36[v % 36]; };
const dec1 = c => A36.indexOf(c);
const dec2 = s => A36.indexOf(s[0]) * 36 + A36.indexOf(s[1]);

function packDrum(events) { /* [{step,dev,lane,vel(0-1)}] dev in steps (-0.5..0.5) */
  return events.map(e =>
    enc2(e.step) + enc1(e.dev * 36 + 18) + LANES[e.lane] + enc1(e.vel * 35)).join("");
}
function unpackDrum(s) {
  const out = [];
  for (let i = 0; i + 5 <= s.length; i += 5)
    out.push({ step: dec2(s.slice(i, i + 2)), dev: (dec1(s[i + 2]) - 18) / 36,
      lane: LANES.indexOf(s[i + 3]), vel: dec1(s[i + 4]) / 35 });
  return out;
}
function packMel(events) { /* [{step,deg(semis from tonic),dur(steps),vel(0-1)}] */
  return events.map(e =>
    enc2(e.step) + enc2(e.deg + 24) + enc1(Math.min(35, e.dur * 4)) + enc1(e.vel * 35)).join("");
}
function unpackMel(s) {
  const out = [];
  for (let i = 0; i + 6 <= s.length; i += 6)
    out.push({ step: dec2(s.slice(i, i + 2)), deg: dec2(s.slice(i + 2, i + 4)) - 24,
      dur: dec1(s[i + 4]) / 4, vel: dec1(s[i + 5]) / 35 });
  return out;
}
/* the groove template: median deviation per step of a drum phrase — the field
   the whole band rides ("quantized to the human played rhythm track") */
function grooveField(drumEvents, slots) {
  const per = Array.from({ length: slots }, () => []);
  drumEvents.forEach(e => { if (e.step < slots) per[e.step].push(e.dev); });
  return per.map(a => { if (!a.length) return null;
    const s = a.slice().sort((x, y) => x - y); return s[s.length >> 1]; });
}
/* scale-fit: fold a semis-from-tonic degree into a target scale, preserving
   contour — out-of-scale chromatics snap to the nearest scale tone below */
function fitScale(deg, scaleIvs) { /* scaleIvs e.g. [0,2,4,5,7,9,11] */
  const oct = Math.floor(deg / 12), pc = ((deg % 12) + 12) % 12;
  if (scaleIvs.includes(pc)) return deg;
  for (let d = 1; d <= 6; d++) {
    if (scaleIvs.includes(((pc - d) + 12) % 12)) return oct * 12 + ((pc - d) + 12) % 12;
    if (scaleIvs.includes((pc + d) % 12)) return oct * 12 + (pc + d) % 12;
  }
  return deg;
}
if (typeof module !== "undefined") module.exports = { A36, LANES, packDrum, unpackDrum, packMel, unpackMel, grooveField, fitScale, enc1, enc2, dec1, dec2 };
