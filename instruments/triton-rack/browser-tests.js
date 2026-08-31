"use strict";
/* 4U face smoke test in real headless Chromium: layout law, wiring, no console errors.
   Needs: npm i playwright-core + a Chromium (edit executablePath below). Run: node browser-tests.js */
let chromium;
try { ({ chromium } = require("playwright-core")); }
catch (e) {
  try { ({ chromium } = require(require("path").join(process.cwd(), "node_modules", "playwright-core"))); }
  catch (e2) { console.error("browser-tests: `npm i playwright-core` here or in your cwd first"); process.exit(2); }
}
const path = __dirname + "/triton-rack.html";
(async () => {
  const fs = require("fs");
  const exe = process.env.CHROMIUM ||
    ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "/opt/pw-browsers/chromium"]
      .find(p => { try { return fs.existsSync(p); } catch (_) { return false; } });
  if (!exe) { console.error("browser-tests: no Chromium found — set CHROMIUM=/path/to/chrome"); process.exit(2); }
  const browser = await chromium.launch({
    executablePath: exe,
    args: ["--autoplay-policy=no-user-gesture-required", "--no-sandbox", "--mute-audio"]
  });
  let errs = 0;
  const fail = m => { console.log("  ✗ " + m); errs++; };
  const ok = m => console.log("  ✓ " + m);
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 } });
  const downloads = [];
  page.on("download", d => downloads.push(d));
  const consoleErrs = [];
  page.on("console", m => { if (m.type() === "error") consoleErrs.push(m.text()); });
  page.on("pageerror", e => consoleErrs.push("pageerror: " + e.message));
  await page.goto("file://" + path);
  await page.waitForTimeout(600);

  /* layout: 4U dimensions + touch law at design scale; face is PLAY·DICE·SAVE */
  const dims = await page.evaluate(() => {
    const u = document.getElementById("ldru");
    const ids = ["dreamPlay", "dreamDice", "ldrSave"];
    const r = {};
    ids.forEach(id => { const e = document.getElementById(id);
      r[id] = e ? { w: e.offsetWidth, h: e.offsetHeight } : null; });
    const th = document.getElementById("ldrTheory");
    return { uw: u.offsetWidth, uh: u.offsetHeight,
      pads: r,
      theory: th ? { w: th.offsetWidth, h: th.offsetHeight } : null,
      thKey: (document.getElementById("thKey") || {}).textContent,
      thNow: (document.getElementById("thNow") || {}).textContent,
      hint: !!document.getElementById("ldrMidiHint"),
      leftovers: ["ldrStrip", "ldrHalf", "ldrRec", "dreamPreset"]
        .filter(id => document.getElementById(id)),
      scope: (c => ({ w: c.width, h: c.height }))(document.getElementById("dreamScope")) };
  });
  if (dims.uw !== 960 || dims.uh !== 540) fail("4U design size " + dims.uw + "x" + dims.uh);
  else ok("4U face 960x540");
  if (dims.pads.dreamPlay.w < 160 || dims.pads.dreamPlay.h < 160) fail("PLAY under 160: " + JSON.stringify(dims.pads.dreamPlay));
  else ok("PLAY " + dims.pads.dreamPlay.w + "px");
  ["dreamDice", "ldrSave"].forEach(id => {
    const p = dims.pads[id];
    if (!p || p.w < 120 || p.h < 120) fail(id + " under touch law: " + JSON.stringify(p));
    else ok(id + " " + p.w + "px"); });
  if (!dims.theory || dims.theory.w < 700 || dims.theory.h < 60) fail("theory bar missing/small " + JSON.stringify(dims.theory));
  else if (dims.thKey !== "—" || dims.thNow !== "press play") fail("theory bar idle text: '" + dims.thKey + "' / '" + dims.thNow + "'");
  else ok("theory bar idle: " + dims.theory.w + "x" + dims.theory.h + " · 'press play'");
  if (!dims.hint) fail("MIDI keyboard hint missing");
  if (dims.leftovers.length) fail("removed surfaces still present: " + dims.leftovers.join(","));
  else ok("face is PLAY·DICE·SAVE only (strip/HALF/REC/preset-select gone)");
  ok("scope canvas " + dims.scope.w + "x" + dims.scope.h);

  /* hardware MIDI on a cold page: the wire boots the unit and makes a voice */
  const mi0 = await page.evaluate(async () => {
    window._midiInject([0x90, 60, 96]);
    await new Promise(r => setTimeout(r, 250));
    const s = { powered: state.powered, ctx: !!ctx, ctxState: ctx ? ctx.state : "none",
      voices: activeVoices, nudge: document.getElementById("audioNudge").classList.contains("on") };
    window._midiInject([0x80, 60, 0]);
    return s;
  });
  if (!mi0.powered || !mi0.ctx) fail("MIDI note did not boot the unit " + JSON.stringify(mi0));
  else if (mi0.voices < 1) fail("MIDI note made no voice (" + mi0.voices + ")");
  else ok("hardware MIDI boots the unit cold (ctx " + mi0.ctxState + ", " + mi0.voices + " voice)");
  if (mi0.nudge !== (mi0.ctxState === "suspended")) fail("audio nudge disagrees with ctx.state " + JSON.stringify(mi0));

  /* the suspended-audio law: nudge shows, one tap anywhere clears it */
  const nud = await page.evaluate(async () => {
    ctxEnsure(true);
    const on1 = document.getElementById("audioNudge").classList.contains("on");
    document.body.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
    await new Promise(r => setTimeout(r, 250));
    return { on1, on2: document.getElementById("audioNudge").classList.contains("on"),
      armed: !!ctxEnsure._armed };
  });
  if (!nud.on1 || nud.on2 || nud.armed) fail("suspended-audio nudge arm/clear broken " + JSON.stringify(nud));
  else ok("audio nudge: shows while stuck, one tap clears and disarms");

  /* pedal, bend and panic ride the same wire */
  const ped = await page.evaluate(() => {
    _midiInject([0xB0, 64, 127]); const a = SUS;
    _midiInject([0xB0, 64, 0]);   const b = SUS;
    _midiInject([0xE0, 0, 96]);   const bend = BENDC;
    _midiInject([0xE0, 0, 64]);
    return { a, b, bend };
  });
  if (!(ped.a === true && ped.b === false)) fail("sustain pedal path " + JSON.stringify(ped));
  else if (!(ped.bend > 90 && ped.bend < 110)) fail("pitch bend path " + ped.bend);
  else ok("sustain pedal + pitch bend ride the hardware wire");

  /* behavior: PLAY powers + conducts; readout goes live */
  await page.click("#dreamPlay");
  await page.waitForTimeout(2500);
  const st1 = await page.evaluate(() => ({
    on: DREAM.on, powered: state.powered, seed: DREAM.seed, bar: DREAM.bar,
    readout: document.getElementById("ldrReadout").textContent,
    voices: activeVoices, engine: LDR.engine, fallbacks: LDR.fallbacks,
    bufs: LDR_BUFS.size }));
  if (!st1.on || !st1.powered) fail("PLAY did not start (on=" + st1.on + " powered=" + st1.powered + ")");
  else if (st1.bar < 1) fail("transport on but bars not advancing (bar " + st1.bar + ")");
  else if (st1.voices < 1) fail("transport on but nothing sounding");
  else ok("PLAY conducts · bar " + st1.bar + " · voices " + st1.voices);
  if (!/#\d+ · \w+ \d\/8 · ♩\d+/.test(st1.readout)) fail("readout: '" + st1.readout + "'");
  else ok("readout live: " + st1.readout);
  if (st1.engine !== "phys") fail("engine not phys: " + st1.engine);
  if (st1.fallbacks) fail(st1.fallbacks + " mapping fallbacks fired");
  if (st1.bufs < 3) fail("physics buffers not rendering (" + st1.bufs + ")");
  else ok("physics engine live · " + st1.bufs + " buffers cached · 0 fallbacks");

  /* theory bar: the Improvisator cheat sheet tracks the running progression */
  const th1 = await page.evaluate(() => ({
    cells: document.querySelectorAll("#thProg .thCell").length,
    prog: DREAM.p.prog.length,
    key: document.getElementById("thKey").textContent,
    now: document.querySelectorAll("#thProg .thCell.now").length,
    thNow: document.getElementById("thNow").textContent,
    romans: [...document.querySelectorAll("#thProg .thCell b")].map(b => b.textContent) }));
  if (th1.cells !== th1.prog || th1.cells < 2) fail("theory cells " + th1.cells + " ≠ prog " + th1.prog);
  else if (!/^[A-G]#? (MAJOR|MINOR)$/.test(th1.key)) fail("theory key: '" + th1.key + "'");
  else if (th1.now !== 1) fail("theory 'now' highlight count " + th1.now);
  else if (!/^now [A-G]#?(maj7|m7♭5|mMaj7|m7|dim7|sus4|7|\+|m)? · [A-G]/.test(th1.thNow)) fail("theory now text: '" + th1.thNow + "'");
  else ok("theory bar live: " + th1.key + " · " + th1.romans.join("–") + " · " + th1.thNow);

  /* the human hand reaches the tape: pad chords roll, dynamics breathe */
  const hum = await page.evaluate(() => {
    const ch = TAKE.ev.filter(e => e.role === "chord").sort((a, b) => a.t - b.t);
    if (ch.length < 4) return { n: ch.length };
    const c0 = ch.slice(0, 4).map(e => e.t);
    const spread = Math.max(...c0) - Math.min(...c0);
    const vels = new Set(ch.map(e => e.vel.toFixed(3))).size;
    return { n: ch.length, spread, vels };
  });
  if (hum.n < 4) fail("no chord events on the tape (" + hum.n + ")");
  else if (!(hum.spread > 0.003 && hum.spread < 0.09)) fail("pad chord not humanly rolled (spread " + (hum.spread * 1000).toFixed(1) + "ms)");
  else if (hum.vels < 2) fail("chord dynamics flat across bars (" + hum.vels + " velocity values)");
  else ok("the hand reaches the tape: pad rolled " + (hum.spread * 1000).toFixed(1) + "ms · " + hum.vels + " chord velocity shades");

  /* dice mid-performance: bar-quantized swap applies, transport never drops */
  await page.click("#dreamDice");
  await page.waitForFunction(() => DREAM.on && !DREAM.pending, { timeout: 9000 });
  await page.waitForTimeout(200);
  const st2 = await page.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed,
    cells: document.querySelectorAll("#thProg .thCell").length, prog: DREAM.p.prog.length,
    key: document.getElementById("thKey").textContent,
    pn: document.getElementById("thProgName").textContent,
    pnWant: DREAM.p.progName || "" }));
  if (!st2.on) fail("DICE killed the performance");
  else if (st2.seed === st1.seed) fail("DICE applied nothing (seed unchanged " + st2.seed + ")");
  else if (st2.cells !== st2.prog) fail("theory bar stale after DICE (" + st2.cells + " cells vs prog " + st2.prog + ")");
  else if (st2.pn !== st2.pnWant) fail("progression name mismatch: '" + st2.pn + "' vs '" + st2.pnWant + "'");
  else ok("DICE swaps on the bar line (seed " + st1.seed + " → " + st2.seed + ") · theory follows (" + st2.key +
    (st2.pn ? " · " + st2.pn : "") + ")");

  /* figure chip mid-dream: transport hands off, the tape keeps rolling (BREAK fix) */
  await page.click('.tab[data-pane="rhythm"]');
  await page.waitForTimeout(150);
  const hand = await page.evaluate(async () => {
    const n0 = TAKE.ev.length, t0 = TAKE.t0;
    const chip = document.querySelector('.pchip.fig[data-f="yoruba"]');
    chip.scrollIntoView(); chip.click();
    await new Promise(r => setTimeout(r, 900));
    return { n0, t0, n1: TAKE.ev.length, t1: TAKE.t0,
      dream: DREAM.on, ldr: LDR.on, take: TAKE.on, fig: LDR.fig };
  });
  if (hand.dream || !hand.ldr || hand.fig !== "yoruba" || !hand.take) fail("figure handoff broken " + JSON.stringify(hand));
  else if (hand.n1 < hand.n0 || hand.t1 !== hand.t0) fail("figure pick wiped the rolling take (" + hand.n0 + "→" + hand.n1 + ")");
  else ok("figure chip mid-dream: transport hands off, tape keeps rolling (" + hand.n0 + "→" + hand.n1 + " events)");
  await page.evaluate(() => { ldrToggle(false); });
  await page.waitForTimeout(200);

  /* Bank B: WRITE on the unit — ENTER, dial a slot, ENTER */
  await page.evaluate(() => { dreamStop(); state.mode = "PROG"; setProgram(12); });
  await page.click("#entBtn");
  const wr1 = await page.evaluate(() => lcd.textContent.indexOf("WRITE PROGRAM") >= 0);
  if (!wr1) fail("ENTER did not open the write screen");
  await page.click('#unit .btn.nav[data-nav="up"]');   /* dial to B001 */
  await page.click("#entBtn");
  await page.waitForTimeout(950);
  const wr2 = await page.evaluate(() => ({ slot1: !!USER_BANK[1], id: USER_BANK[1] && USER_BANK[1].id,
    curId: cur.id, chip: !!document.querySelector('.pchip[data-u="1"]'),
    count: document.getElementById("bankCount").textContent }));
  if (!wr2.slot1 || wr2.id !== "B001" || wr2.curId !== "B001") fail("write flow " + JSON.stringify(wr2));
  else if (!wr2.chip || wr2.count !== "1") fail("written program not surfaced " + JSON.stringify(wr2));
  else ok("Bank B: wrote " + wr2.id + " from the unit, chip + count live");
  const bankJson = await page.evaluate(() => JSON.stringify({ v: 1, bank: USER_BANK }));
  const wr3 = await page.evaluate(j => { const got = bankParse(j); return got && got[1] && got[1].id; }, bankJson);
  if (wr3 !== "B001") fail("bank export/import round-trip: " + wr3);
  else ok("Bank B: file round-trip holds");

  /* hostile bank import: slot name is HTML — must render inert in the patch pane */
  const bxss = await page.evaluate(async () => {
    const keep = USER_BANK[1];
    const entry = JSON.parse(JSON.stringify(keep));
    entry.name = "<img src=x onerror=window.__bx=1>";
    const bank = []; bank[1] = entry;
    const got = bankParse(JSON.stringify({ v: 1, bank }));
    if (!got || !got[1]) return { parsed: false };
    USER_BANK[1] = got[1]; buildPatchPane();
    await new Promise(r => setTimeout(r, 350));
    const fired = !!window.__bx;
    const img = !!document.querySelector('#patchList .pchip[data-u="1"] img');
    USER_BANK[1] = keep; buildPatchPane(); updatePatchChips();
    return { parsed: true, fired, img };
  });
  if (!bxss.parsed) fail("hostile bank entry did not parse (validator over-rejects)");
  else if (bxss.fired || bxss.img) fail("XSS: imported Bank B name executed/rendered as HTML");
  else ok("hostile Bank B name renders inert (escaped)");

  /* figure pick from the Rhythm pane: manual physics engine takes the transport */
  await page.click('.tab[data-pane="rhythm"]');
  await page.waitForTimeout(200);
  await page.evaluate(() => { document.querySelector('.pchip.fig[data-f="bembe"]').scrollIntoView(); });
  await page.click('.pchip.fig[data-f="bembe"]');
  await page.waitForTimeout(1500);
  const st3 = await page.evaluate(() => ({ dream: DREAM.on, ldr: LDR.on, fig: LDR.fig,
    onChip: document.querySelectorAll(".pchip.fig.on").length }));
  if (st3.dream) fail("dream still on after figure pick");
  if (!st3.ldr || st3.fig !== "bembe") fail("figure engine not running: " + JSON.stringify(st3));
  else ok("Rhythm pane figure pick: bembe on the physics engine");
  if (st3.onChip !== 1) fail("figure chip highlight count " + st3.onChip);

  /* SAVE: jam a note from the MIDI wire over the running figure, bounce, verify */
  await page.evaluate(async () => { _midiInject([0x90, 72, 108]);
    await new Promise(r => setTimeout(r, 420)); _midiInject([0x80, 72, 0]); });
  await page.waitForTimeout(400);
  const takeInfo = await page.evaluate(() => ({ n: TAKE.ev.length, on: TAKE.on,
    you: TAKE.ev.filter(e => e.role === "you").length,
    youDur: (TAKE.ev.find(e => e.role === "you") || {}).dur }));
  if (takeInfo.n < 5 || takeInfo.you < 1 || !takeInfo.on) fail("take log thin " + JSON.stringify(takeInfo));
  else if (!(takeInfo.youDur > 0.2 && takeInfo.youDur < 1.5)) fail("player note duration not captured: " + takeInfo.youDur);
  else ok("take rolls: " + takeInfo.n + " events, hardware-wire note held " + takeInfo.youDur.toFixed(2) + "s");
  const dl0 = downloads.length;
  await page.click("#ldrSave");
  await page.waitForFunction(() => exporting, { timeout: 5000 }).catch(() => {});
  await page.waitForFunction(() => !exporting, { timeout: 60000 });
  await page.waitForTimeout(900);
  const newDls = downloads.slice(dl0);
  const wavD = newDls.find(d => d.suggestedFilename().endsWith(".wav"));
  const midD = newDls.find(d => d.suggestedFilename().endsWith(".mid"));
  if (!wavD || !midD) fail("SAVE downloads missing: " + JSON.stringify(newDls.map(d => d.suggestedFilename())));
  else {
    const os = require("os"), fs = require("fs"), pj = require("path").join;
    const wp = pj(os.tmpdir(), "tr-take.wav"), mp = pj(os.tmpdir(), "tr-take.mid");
    await wavD.saveAs(wp); await midD.saveAs(mp);
    const w = fs.readFileSync(wp), m = fs.readFileSync(mp);
    let peak = 0;
    for (let i = 44; i < Math.min(w.length - 3, 44 + 48000 * 6 * 8); i += 3) {
      let v = (w[i] | (w[i + 1] << 8) | (w[i + 2] << 16)); if (v & 0x800000) v -= 0x1000000;
      const a = Math.abs(v); if (a > peak) peak = a;
    }
    const okWav = w.slice(0, 4).toString() === "RIFF" && w.slice(8, 12).toString() === "WAVE" && w.length > 150000;
    const hasYou = m.includes(Buffer.from("YOU"));
    let ons = 0; for (let i = 0; i < m.length - 2; i++) if ((m[i] & 0xF0) === 0x90 && m[i + 2] > 0) ons++;
    if (!okWav) fail("bounced WAV malformed/short (" + w.length + " bytes)");
    else if (peak < 80000) fail("bounced WAV is near-silent (peak " + peak + " of 8388607)");
    else if (m.slice(0, 4).toString() !== "MThd" || !hasYou || ons < 3)
      fail("bounced MIDI bad (MThd:" + m.slice(0, 4) + " YOU:" + hasYou + " ons:" + ons + ")");
    else ok("SAVE bounce: WAV " + (w.length / 1024 | 0) + " KB (peak " + (peak / 8388607).toFixed(2) +
      " FS) + MIDI with YOU track (" + ons + " note-ons)");
  }
  const still = await page.evaluate(() => ({ ldr: LDR.on, take: TAKE.on }));
  if (!still.ldr || !still.take) fail("bounce killed the transport " + JSON.stringify(still));
  else ok("transport and tape survive the bounce");

  /* power-off disarms WRITE, pauses the tape, resets controllers, clears the nudge */
  await page.evaluate(() => { state.write = true; _midiInject([0xB0, 64, 127]); ctxEnsure(true); powerOff(); });
  const poff = await page.evaluate(() => ({ write: state.write, take: TAKE.on, kept: TAKE.ev.length,
    sus: SUS, bend: BENDC, armed: !!ctxEnsure._armed,
    nudge: document.getElementById("audioNudge").classList.contains("on") }));
  if (poff.write || poff.take) fail("powerOff left WRITE/tape armed " + JSON.stringify(poff));
  else if (poff.kept < 5) fail("powerOff destroyed the saveable take");
  else if (poff.sus || poff.bend !== 0) fail("controller state survived the power cycle " + JSON.stringify(poff));
  else if (poff.nudge || poff.armed) fail("powerOff left the audio nudge armed " + JSON.stringify(poff));
  else ok("powerOff disarms WRITE + nudge, resets controllers, keeps the take saveable");
  await page.evaluate(() => quickBoot());
  await page.waitForTimeout(300);

  /* STRUM: factory default on Nylon Dream, cycles after CHORD, and sounds */
  const strum = await page.evaluate(() => {
    state.mode = "PROG"; setProgram(31);
    const patt0 = state.arp.patt, on0 = state.arp.on;
    state.arp.patt = "CHORD"; PPAGES.PROG[2][0].set(1); const afterChord = state.arp.patt;
    PPAGES.PROG[2][0].set(1); const wrap = state.arp.patt;
    state.arp.patt = patt0;
    return { patt0, on0, afterChord, wrap };
  });
  if (strum.patt0 !== "STRUM" || !strum.on0) fail("Nylon Dream STRUM default " + JSON.stringify(strum));
  else if (strum.afterChord !== "STRUM" || strum.wrap !== "UP") fail("STRUM cycle " + JSON.stringify(strum));
  else ok("STRUM: factory default + parameter cycle");
  const strumV = await page.evaluate(async () => {
    /* isolate: stop the manual rhythm engine and let its tails die, so the
       voices counted here are the strum's own */
    LDR.on = false; allNotesOff();
    await new Promise(r => setTimeout(r, 1600));
    const s0 = arpStep, v0 = activeVoices;
    noteOn(60, .8); noteOn(64, .8); noteOn(67, .8);
    await new Promise(r => setTimeout(r, 700));
    const v = activeVoices, steps = arpStep - s0;
    noteOff(60); noteOff(64); noteOff(67);
    state.arp.on = false; allNotesOff();
    return { v0, v, steps };
  });
  if (strumV.steps < 1) fail("STRUM scheduler never stepped");
  else if (strumV.v <= strumV.v0) fail("STRUM added no voices (before " + strumV.v0 + ", during " + strumV.v + ")");
  else if (strumV.v > 70) fail("voice accounting leak: " + strumV.v + " active (cap is 62)");
  else ok("STRUM plays (" + strumV.steps + " steps, " + strumV.v0 + "→" + strumV.v + " voices, cap honored)");

  /* audition improviser: two passes schedule, no errors */
  await page.evaluate(() => { setProgram(0); });
  await page.click("#audBtn");
  await page.waitForTimeout(1200);
  const audOn = await page.evaluate(() => ({ on: state.audition, v: activeVoices, pass: audPass }));
  await page.click("#audBtn");
  if (!audOn.on || audOn.pass < 1) fail("audition improviser inert " + JSON.stringify(audOn));
  else ok("audition improviser live (pass " + audOn.pass + ")");

  /* mobile scale: fit() keeps physical touch targets >= 44px */
  await page.setViewportSize({ width: 380, height: 800 });
  await page.waitForTimeout(400);
  const mob = await page.evaluate(() => {
    const r = document.getElementById("dreamPlay").getBoundingClientRect();
    const d = document.getElementById("dreamDice").getBoundingClientRect();
    const body = document.body.scrollWidth;
    return { play: r.width, dice: d.width, hscroll: body > window.innerWidth + 2 };
  });
  if (mob.play < 44) fail("phone PLAY " + mob.play.toFixed(1) + "px < 44");
  else ok("phone PLAY " + mob.play.toFixed(1) + "px, DICE " + mob.dice.toFixed(1) + "px");
  if (mob.hscroll) fail("page scrolls horizontally on phone");

  const realErrs = consoleErrs.filter(e => !/Web MIDI|requestMIDIAccess|favicon/.test(e));
  if (realErrs.length) fail("console: " + realErrs.slice(0, 4).join(" | "));
  else ok("zero console errors");

  await page.setViewportSize({ width: 1100, height: 900 });
  await page.waitForTimeout(300);
  await page.screenshot({ path: __dirname + "/4u-face.png", clip: { x: 0, y: 60, width: 1000, height: 640 } });
  await browser.close();
  console.log(errs ? "\nUI SMOKE: " + errs + " ERROR(S)" : "\nUI SMOKE: ALL GREEN");
  process.exit(errs ? 1 : 0);
})().catch(e => { console.error("HARNESS FAIL: " + e.message); process.exit(1); });
