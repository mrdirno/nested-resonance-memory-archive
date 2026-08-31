"use strict";
/* Minimal Standard MIDI File parser — no deps. Returns {division, tracks:[events]}
   where events = {tick, type, ch, a, b} for channel msgs and {tick, type:'tempo', usPerQn}
   for tempo metas. Enough for Groove MIDI (format 0/1, notes + tempo + meter). */
function parseMidi(buf) {
  if (buf.toString("latin1", 0, 4) !== "MThd") throw new Error("not SMF");
  const hdrLen = buf.readUInt32BE(4);
  const format = buf.readUInt16BE(8), ntrks = buf.readUInt16BE(10), division = buf.readUInt16BE(12);
  if (division & 0x8000) throw new Error("SMPTE division unsupported");
  let off = 8 + hdrLen;
  const tracks = [];
  for (let t = 0; t < ntrks; t++) {
    if (buf.toString("latin1", off, off + 4) !== "MTrk") throw new Error("bad track @" + off);
    const len = buf.readUInt32BE(off + 4);
    const end = off + 8 + len;
    let p = off + 8, tick = 0, running = 0;
    const ev = [];
    while (p < end) {
      let d = 0;
      for (;;) { const b = buf[p++]; d = (d << 7) | (b & 0x7f); if (!(b & 0x80)) break; }
      tick += d;
      let st = buf[p];
      /* meta/sysex must NOT become running status (audit: a channel event
         using running status after a meta was reparsed as a bogus meta) */
      if (st < 0x80) { st = running; } else { p++; if (st < 0xf0) running = st; }
      if (st === 0xff) {
        const type = buf[p++]; let mlen = 0;
        for (;;) { const b = buf[p++]; mlen = (mlen << 7) | (b & 0x7f); if (!(b & 0x80)) break; }
        if (type === 0x51 && mlen === 3) ev.push({ tick, type: "tempo", usPerQn: (buf[p] << 16) | (buf[p + 1] << 8) | buf[p + 2] });
        else if (type === 0x58 && mlen >= 2) ev.push({ tick, type: "meter", num: buf[p], den: 1 << buf[p + 1] });
        p += mlen;
      } else if (st === 0xf0 || st === 0xf7) {
        let mlen = 0;
        for (;;) { const b = buf[p++]; mlen = (mlen << 7) | (b & 0x7f); if (!(b & 0x80)) break; }
        p += mlen;
      } else {
        const hi = st & 0xf0, ch = st & 0x0f;
        if (hi === 0xc0 || hi === 0xd0) { ev.push({ tick, type: hi, ch, a: buf[p++] }); }
        else { const a = buf[p++], b = buf[p++]; ev.push({ tick, type: hi, ch, a, b }); }
      }
    }
    tracks.push(ev);
    off = end;
  }
  return { format, division, tracks };
}
/* flatten to note-ons with seconds, applying the tempo map (single map from all tracks) */
function midiNotes(m) {
  const tempos = [];
  m.tracks.forEach(tr => tr.forEach(e => { if (e.type === "tempo") tempos.push(e); }));
  tempos.sort((a, b) => a.tick - b.tick);
  if (!tempos.length || tempos[0].tick > 0) tempos.unshift({ tick: 0, usPerQn: 500000 });
  const t2s = tick => {
    let s = 0, last = tempos[0], i = 1;
    for (; i < tempos.length && tempos[i].tick <= tick; i++) { s += (tempos[i].tick - last.tick) / m.division * last.usPerQn / 1e6; last = tempos[i]; }
    return s + (tick - last.tick) / m.division * last.usPerQn / 1e6;
  };
  const notes = [];
  m.tracks.forEach(tr => tr.forEach(e => {
    if (e.type === 0x90 && e.b > 0) notes.push({ t: t2s(e.tick), tick: e.tick, qn: e.tick / m.division, note: e.a, vel: e.b, ch: e.ch });
  }));
  notes.sort((a, b) => a.t - b.t);
  return notes;
}
module.exports = { parseMidi, midiNotes };
