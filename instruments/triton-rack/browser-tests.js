"use strict";
/* 4U face smoke test in real headless Chromium: layout law, wiring, no console errors.
   Needs: npm i playwright-core + a Chromium (edit executablePath below). Run: node browser-tests.js */
const { chromium } = require("playwright-core");
const path = __dirname + "/triton-rack.html";
(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--autoplay-policy=no-user-gesture-required", "--no-sandbox", "--mute-audio"]
  });
  let errs = 0;
  const fail = m => { console.log("  ✗ " + m); errs++; };
  const ok = m => console.log("  ✓ " + m);
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 } });
  const consoleErrs = [];
  page.on("console", m => { if (m.type() === "error") consoleErrs.push(m.text()); });
  page.on("pageerror", e => consoleErrs.push("pageerror: " + e.message));
  await page.goto("file://" + path);
  await page.waitForTimeout(600);

  /* layout: 4U dimensions + touch law at design scale */
  const dims = await page.evaluate(() => {
    const u = document.getElementById("ldru");
    const ids = ["dreamPlay", "dreamDice", "ldrRec"];
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
  ["dreamDice", "ldrRec"].forEach(id => {
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

  /* dice mid-performance: bar-quantized swap, still running */
  await page.click("#dreamDice");
  await page.waitForTimeout(2200);
  const st2 = await page.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed }));
  if (!st2.on) fail("DICE killed the performance");
  else ok("DICE swaps seamlessly (seed " + st1.seed + " → " + st2.seed + ")");

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

  /* record 1s take: UI mirrors */
  await page.click("#ldrRec");
  await page.waitForTimeout(900);
  const recOn = await page.evaluate(() => ({ on: REC.on,
    pad: document.getElementById("ldrRec").classList.contains("rec"),
    fab: document.getElementById("fabRec").classList.contains("rec") }));
  if (!recOn.on || !recOn.pad || !recOn.fab) fail("record UI not mirrored " + JSON.stringify(recOn));
  else ok("record: 4U pad and dock mirror");
  await page.click("#ldrRec");
  await page.waitForTimeout(300);

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
