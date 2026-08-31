"use strict";
/* Minimal MusicXML (partwise) parser — no deps, regex-streaming. Returns
   {parts:[{id,name,notes:[{qn,midi,durQn,voice,grace,dyn}] , keys:[{qn,fifths,mode}], meters:[{qn,num,den}]}]}
   qn = position in quarter notes from piece start (repeats ignored — we mine
   phrases, not form). backup/forward honored; chords keep the FIRST note. */
const STEP2PC = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const DYN = { ppp: .4, pp: .45, p: .55, mp: .62, mf: .7, f: .8, ff: .88, fff: .95, sf: .85, sfz: .85, fp: .75 };

function tag(block, name) {
  const m = block.match(new RegExp("<" + name + ">([^<]*)</" + name + ">"));
  return m ? m[1] : null;
}
function parseMxlXml(xml) {
  const parts = [];
  const plist = {};
  const plm = xml.match(/<score-part id="([^"]+)">[\s\S]*?<\/score-part>/g) || [];
  plm.forEach(b => {
    const id = b.match(/id="([^"]+)"/)[1];
    plist[id] = tag(b, "part-name") || id;
  });
  const pm = xml.match(/<part id="[^"]+">[\s\S]*?<\/part>/g) || [];
  pm.forEach(pb => {
    const id = pb.match(/<part id="([^"]+)">/)[1];
    const part = { id, name: plist[id] || id, notes: [], keys: [], meters: [] };
    let div = 480, cur = 0; /* cursor in QUARTER NOTES — divisions changes stay local (audit) */
    let dyn = .7;
    const measures = pb.match(/<measure[^>]*>[\s\S]*?<\/measure>/g) || [];
    measures.forEach(mb => {
      const mStart = cur;
      let mMax = cur; /* a measure ends at its FARTHEST voice, not its last-written one (audit) */
      /* one chunk walk: attributes, notes, backup, forward, directions in order */
      const toks = mb.match(/<(attributes|note|backup|forward|direction)[\s>][\s\S]*?<\/\1>/g) || [];
      toks.forEach(tk => {
        if (tk.startsWith("<attributes")) {
          const d = tag(tk, "divisions"); if (d) div = +d;
          const f = tk.match(/<fifths>(-?\d+)<\/fifths>/);
          if (f) part.keys.push({ qn: cur, fifths: +f[1], mode: (tag(tk, "mode") || "major"),
            hasMode: /<mode>/.test(tk) });
          const bt = tk.match(/<beats>(\d+)<\/beats>[\s\S]*?<beat-type>(\d+)<\/beat-type>/);
          if (bt) part.meters.push({ qn: cur, num: +bt[1], den: +bt[2] });
        } else if (tk.startsWith("<backup")) {
          cur -= +(tag(tk, "duration") || 0) / div;
        } else if (tk.startsWith("<forward")) {
          cur += +(tag(tk, "duration") || 0) / div;
        } else if (tk.startsWith("<direction")) {
          const dm = tk.match(/<dynamics>\s*<([a-z]+)\s*\/>/);
          if (dm && DYN[dm[1]] != null) dyn = DYN[dm[1]];
        } else { /* note */
          const dur = +(tag(tk, "duration") || 0);
          const isChord = tk.includes("<chord/>");
          const isRest = tk.includes("<rest");
          const isGrace = tk.includes("<grace");
          const isCue = tk.includes("<cue/>"); /* another instrument's reminder line — occupies time, is not this part's playing (audit) */
          if (!isRest && !isChord && !isCue) {
            const st = tag(tk, "step"), oc = tag(tk, "octave");
            if (st != null && oc != null) {
              const alt = +(tag(tk, "alter") || 0);
              const midi = 12 * (+oc + 1) + STEP2PC[st] + alt;
              const tieStop = /<tie type="stop"/.test(tk);
              const v = +(tag(tk, "voice") || 1);
              if (!tieStop)
                part.notes.push({ qn: cur, midi, durQn: dur / div, voice: v, grace: isGrace, dyn });
              else { /* extend ONLY the note whose sounding END lands here —
                        the true tie partner (audit: same-pitch-nearby matched wrong notes) */
                for (let i = part.notes.length - 1; i >= 0 && i > part.notes.length - 64; i--) {
                  const cand = part.notes[i];
                  if (cand.midi === midi && cand.voice === v &&
                      Math.abs((cand.qn + cand.durQn) - cur) < 1 / 64) { cand.durQn += dur / div; break; }
                }
              }
            }
          }
          if (!isChord && !isGrace) cur += dur / div;
        }
        if (cur > mMax) mMax = cur;
      });
      cur = Math.max(mMax, mStart); /* underfilled last voice must not drag time backwards */
    });
    part.notes.sort((a, b) => a.qn - b.qn);
    parts.push(part);
  });
  return { parts };
}
module.exports = { parseMxlXml };
