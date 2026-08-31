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

  /* layout: 4U dimensions + touch law at design scale */
  const dims = await page.evaluate(() => {
    const u = document.getElementById("ldru");
    const ids = ["dreamPlay", "dreamDice", "ldrSave"];
    const r = {};
    ids.forEach(id => { const e = document.getElementById(id);
      r[id] = e ? { w: e.offsetWidth, h: e.offsetHeight } : null; });
    const tiles = [...document.querySelectorAll("#ldrStrip .l4tile")];
    return { uw: u.offsetWidth, uh: u.offsetHeight,
      pads: r, tiles: tiles.length,
      dreamTiles: document.querySelectorAll("#ldrStrip .l4tile.dream").length,
      figTiles: document.querySelectorAll("#ldrStrip .l4tile.fig").length,
      tileMin: Math.min(...tiles.map(t => Math.min(t.offsetWidth, t.offsetHeight))),
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
  if (dims.dreamTiles !== 7) fail("dream tiles " + dims.dreamTiles);
  if (dims.figTiles !== 51) fail("figure tiles " + dims.figTiles);
  if (dims.tileMin < 120) fail("tile min dimension " + dims.tileMin);
  if (dims.dreamTiles === 7 && dims.figTiles === 51 && dims.tileMin >= 120)
    ok("strip: 7 dream pads + 51 figure tiles, all >=120px");
  ok("scope canvas " + dims.scope.w + "x" + dims.scope.h);

  /* behavior: PLAY powers + conducts; readout and LEDs go live */
  await page.click("#dreamPlay");
  await page.waitForTimeout(2500);
  const st1 = await page.evaluate(() => ({
    on: DREAM.on, powered: state.powered, seed: DREAM.seed, bar: DREAM.bar,
    readout: document.getElementById("ldrReadout").textContent,
    drums: document.getElementById("led-drums").classList.contains("on"),
    voices: activeVoices, engine: LDR.engine, fallbacks: LDR.fallbacks,
    bufs: LDR_BUFS.size, live: document.querySelectorAll("#ldrStrip .l4tile.dream.live").length }));
  if (!st1.on || !st1.powered) fail("PLAY did not start (on=" + st1.on + " powered=" + st1.powered + ")");
  else if (st1.bar < 1) fail("transport on but bars not advancing (bar " + st1.bar + ")");
  else if (st1.voices < 1) fail("transport on but nothing sounding");
  else ok("PLAY conducts · bar " + st1.bar + " · voices " + st1.voices);
  if (!/#\d+ · \w+ \d\/8 · ♩\d+/.test(st1.readout)) fail("readout: '" + st1.readout + "'");
  else ok("readout live: " + st1.readout);
  if (!st1.drums) fail("drums LED dark during performance");
  else ok("part LEDs live");
  if (st1.engine !== "phys") fail("engine not phys: " + st1.engine);
  if (st1.fallbacks) fail(st1.fallbacks + " mapping fallbacks fired");
  if (st1.bufs < 3) fail("physics buffers not rendering (" + st1.bufs + ")");
  else ok("physics engine live · " + st1.bufs + " buffers cached · 0 fallbacks");
  if (st1.live !== 1) fail("live dream tile count " + st1.live);

  /* dice mid-performance: bar-quantized swap applies, transport never drops */
  await page.click("#dreamDice");
  await page.waitForFunction(() => DREAM.on && !DREAM.pending, { timeout: 9000 });
  await page.waitForTimeout(200);
  const st2 = await page.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed }));
  if (!st2.on) fail("DICE killed the performance");
  else if (st2.seed === st1.seed) fail("DICE applied nothing (seed unchanged " + st2.seed + ")");
  else ok("DICE swaps on the bar line (seed " + st1.seed + " → " + st2.seed + ")");

  /* HALF-DICE: rhythm section survives, harmony re-rolls, lands on the bar */
  await page.waitForFunction(() => DREAM.on && !DREAM.pending, { timeout: 9000 });
  const preHalf = await page.evaluate(() => ({ fig: DREAM.p.fig, kit: DREAM.p.kit,
    bass: DREAM.p.bass, chord: DREAM.p.chord, lead: DREAM.p.lead }));
  await page.click("#ldrHalf");
  await page.waitForFunction(() => !DREAM.pending, { timeout: 9000 });
  await page.waitForTimeout(250);
  const postHalf = await page.evaluate(() => ({ on: DREAM.on, fig: DREAM.p.fig, kit: DREAM.p.kit,
    bass: DREAM.p.bass, chord: DREAM.p.chord, lead: DREAM.p.lead, name: DREAM.p.name }));
  if (!postHalf.on) fail("HALF-DICE stopped the transport");
  else if (postHalf.fig !== preHalf.fig || postHalf.kit !== preHalf.kit) fail("HALF-DICE touched the rhythm section");
  else if (!/half-cut$/.test(postHalf.name)) fail("HALF-DICE did not apply by the bar (name: " + postHalf.name + ")");
  else ok("HALF-DICE: rhythm held (" + postHalf.fig + "), harmony re-rolled (" +
    preHalf.bass + "/" + preHalf.chord + "/" + preHalf.lead + " → " +
    postHalf.bass + "/" + postHalf.chord + "/" + postHalf.lead + ")");

  /* crate: pin the current take, dice away, replay it note-for-note by seed */
  const pin1 = await page.evaluate(() => { const s = DREAM.seed; cratePin();
    return { s, n: LDR_CRATE.length, tile: !!document.querySelector('#ldrStrip .l4tile.crate') }; });
  if (pin1.n !== 1 || !pin1.tile) fail("pin did not crate the take " + JSON.stringify(pin1));
  await page.click("#dreamDice");
  await page.waitForTimeout(2600);
  await page.evaluate(() => document.querySelector('#ldrStrip .l4tile.crate').scrollIntoView({ inline: "center" }));
  await page.click('#ldrStrip .l4tile.crate[data-c="0"]');
  await page.waitForFunction(s => DREAM.seed === s && !DREAM.pending, pin1.s, { timeout: 9000 });
  const rep = await page.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed, fig: DREAM.p.fig }));
  if (!rep.on || rep.seed !== pin1.s) fail("crate replay seed " + rep.seed + " ≠ pinned " + pin1.s);
  else ok("crate: pinned #" + pin1.s + " replayed exactly (" + rep.fig + ")");

  /* hostile crate import: name is HTML — must render inert */
  const xss = await page.evaluate(async () => {
    const payload = JSON.stringify({ v: 1, crate: [{ v: 1, seed: 1,
      name: "<img src=x onerror=window.__xss=1>",
      p: JSON.parse(JSON.stringify(DREAMS[0])) }] });
    const got = crateParse(payload);
    if (got && got.length) { LDR_CRATE.push(got[0]); ldr4Build(); }
    await new Promise(r => setTimeout(r, 350));
    const fired = !!window.__xss;
    const img = !!document.querySelector("#ldrStrip .l4tile.crate img");
    if (got && got.length) { LDR_CRATE.pop(); ldr4Build(); }
    return { parsed: got ? got.length : -1, fired, img };
  });
  if (xss.parsed !== 1) fail("hostile crate entry did not parse as expected (" + xss.parsed + ")");
  else if (xss.fired || xss.img) fail("XSS: imported crate name executed/rendered as HTML");
  else ok("hostile crate name renders inert (escaped)");

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

  /* figure tile takes over: manual rhythm, dream stops */
  await page.evaluate(() => { document.querySelector('#ldrStrip .l4tile.fig[data-f="bembe"]').scrollIntoView(); });
  await page.click('#ldrStrip .l4tile.fig[data-f="bembe"]');
  await page.waitForTimeout(1500);
  const st3 = await page.evaluate(() => ({ dream: DREAM.on, ldr: LDR.on, fig: LDR.fig,
    onTile: document.querySelectorAll("#ldrStrip .l4tile.fig.on").length }));
  if (st3.dream) fail("dream still on after figure pick");
  if (!st3.ldr || st3.fig !== "bembe") fail("figure engine not running: " + JSON.stringify(st3));
  else ok("figure tile takes over: bembe on the physics engine");
  if (st3.onTile !== 1) fail("figure tile highlight count " + st3.onTile);

  /* SAVE: jam a note over the running figure, bounce offline, verify both files */
  await page.evaluate(async () => { noteOn(72, .85); await new Promise(r => setTimeout(r, 420)); noteOff(72); });
  await page.waitForTimeout(400);
  const takeInfo = await page.evaluate(() => ({ n: TAKE.ev.length, on: TAKE.on,
    you: TAKE.ev.filter(e => e.role === "you").length,
    youDur: (TAKE.ev.find(e => e.role === "you") || {}).dur }));
  if (takeInfo.n < 5 || takeInfo.you < 1 || !takeInfo.on) fail("take log thin " + JSON.stringify(takeInfo));
  else if (!(takeInfo.youDur > 0.2 && takeInfo.youDur < 1.5)) fail("player note duration not captured: " + takeInfo.youDur);
  else ok("take rolls: " + takeInfo.n + " events, player note held " + takeInfo.youDur.toFixed(2) + "s");
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

  /* power-off disarms WRITE and pauses the tape */
  await page.evaluate(() => { state.write = true; powerOff(); });
  const poff = await page.evaluate(() => ({ write: state.write, take: TAKE.on, kept: TAKE.ev.length }));
  if (poff.write || poff.take) fail("powerOff left WRITE/tape armed " + JSON.stringify(poff));
  else if (poff.kept < 5) fail("powerOff destroyed the saveable take");
  else ok("powerOff disarms WRITE, pauses the tape, keeps the take saveable");
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
