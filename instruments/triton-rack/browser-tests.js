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

  /* layout: the song-avatar face — rail, hand, four buttons, engine folded */
  const dims = await page.evaluate(() => {
    const u = document.getElementById("ldru");
    const ids = ["dreamPlay", "dreamDice", "ldrSave", "ldrKeep"];
    const r = {};
    ids.forEach(id => { const e = document.getElementById(id);
      r[id] = e ? { w: e.offsetWidth, h: e.offsetHeight } : null; });
    const th = document.getElementById("ldrTheory");
    return { uw: u.offsetWidth, uh: u.offsetHeight,
      pads: r,
      rail: document.querySelectorAll("#traitRail .trSlot").length,
      prompt: !!document.querySelector("#handRow .hdone"),
      cards0: document.querySelectorAll("#handRow .hcard").length,
      engineFolded: getComputedStyle(document.getElementById("unitScale")).display === "none" &&
        getComputedStyle(document.querySelector(".tabs")).display === "none",
      toggle: !!document.getElementById("engineToggle"),
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
  ["dreamPlay", "dreamDice", "ldrSave", "ldrKeep"].forEach(id => {
    const p = dims.pads[id];
    if (!p || p.w < 120 || p.h < 120) fail(id + " under touch law: " + JSON.stringify(p));
    else ok(id + " " + p.w + "px"); });
  if (dims.rail !== 5) fail("trait rail slots " + dims.rail);
  else if (!dims.prompt || dims.cards0 !== 0) fail("boot state not the press-play prompt");
  else ok("avatar rail: 5 trait slots + press-play prompt");
  if (!dims.engineFolded || !dims.toggle) fail("engine room not folded away " + JSON.stringify({ f: dims.engineFolded, t: dims.toggle }));
  else ok("engine room folded to one link — no scroll-select UX");
  if (!dims.theory || dims.theory.w < 700 || dims.theory.h < 40) fail("theory bar missing/small " + JSON.stringify(dims.theory));
  else if (dims.thKey !== "—" || dims.thNow !== "press play") fail("theory bar idle text: '" + dims.thKey + "' / '" + dims.thNow + "'");
  else ok("theory bar idle: " + dims.theory.w + "x" + dims.theory.h + " · 'press play'");
  if (!dims.hint) fail("MIDI keyboard hint missing");
  if (dims.leftovers.length) fail("removed surfaces still present: " + dims.leftovers.join(","));
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

  /* the mix rack: strips wired, and the kick keys a real duck (probed in the
     quiet just after boot — figure warm-renders would eat the window later) */
  const duck = await page.evaluate(async () => {
    const wired = !!(MIX && MIX.kit && MIX.bass && MIX.chord && MIX.lead) && drumOut() === MIX.kit.in;
    drumHitP("surdo", 1, 0, {});     /* cache-warm: the miss renders synchronously */
    await new Promise(r => setTimeout(r, 150));
    drumHitP("surdo", 1, ctx.currentTime + .10, {});
    let dipped = 1; const t0 = performance.now();
    while (performance.now() - t0 < 1400) {
      dipped = Math.min(dipped, MIX.chord.duck.gain.value);
      await new Promise(r => setTimeout(r, 8));
    }
    await new Promise(r => setTimeout(r, 600));
    return { wired, dipped, back: MIX.chord.duck.gain.value };
  });
  if (!duck.wired) fail("mix rack not wired " + JSON.stringify(duck));
  else if (!(duck.dipped < .95)) fail("the kick does not duck the chords (gain " + duck.dipped.toFixed(3) + ")");
  else if (!(duck.back > .985)) fail("the duck never recovers (gain " + duck.back.toFixed(3) + ")");
  else ok("mix rack: 4 role strips + kick-keyed duck (dip " + duck.dipped.toFixed(2) + " → back " + duck.back.toFixed(3) + ")");

  /* behavior: PLAY powers + conducts; readout goes live */
  await page.click("#dreamPlay");
  /* a library drummer plays kit-role events; a curated one perc-role — both are drums */
  await page.waitForFunction(() => typeof DREAM !== "undefined" && DREAM.on && DREAM.bar >= 2 &&
    TAKE.ev.filter(e => e.role === "perc" || e.role === "kit" || e.role === "dd").length >= 10, { timeout: 25000 });
  await page.waitForTimeout(250);
  const st1 = await page.evaluate(() => ({
    on: DREAM.on, powered: state.powered, seed: DREAM.seed, bar: DREAM.bar,
    readout: document.getElementById("ldrReadout").textContent,
    voices: activeVoices, engine: LDR.engine, fallbacks: LDR.fallbacks,
    lib: DREAM.p && (DREAM.p.dlib != null || DREAM.p.dsty != null),
    bufs: LDR_BUFS.size }));
  if (!st1.on || !st1.powered) fail("PLAY did not start (on=" + st1.on + " powered=" + st1.powered + ")");
  else if (st1.bar < 1) fail("transport on but bars not advancing (bar " + st1.bar + ")");
  else if (st1.voices < 1) fail("transport on but nothing sounding");
  else ok("PLAY conducts · bar " + st1.bar + " · voices " + st1.voices);
  if (!/#\d+ · \w+ \d\/8 · ♩\d+/.test(st1.readout)) fail("readout: '" + st1.readout + "'");
  else ok("readout live: " + st1.readout);
  if (st1.engine !== "phys") fail("engine not phys: " + st1.engine);
  if (st1.fallbacks) fail(st1.fallbacks + " mapping fallbacks fired");
  /* a LIBRARY drummer plays kit voices, not LDR physics — buffers come later */
  if (!st1.lib && st1.bufs < 3) fail("physics buffers not rendering (" + st1.bufs + ")");
  else ok((st1.lib ? "library take live · " : "physics engine live · ") + st1.bufs + " buffers cached · 0 fallbacks");

  /* stage 0 — THE DRUMMER: three prebuilt players dealt, one live, honest mutes */
  const stg0 = await page.evaluate(() => ({ stage: BUILD.stage,
    cards: document.querySelectorAll("#handRow .hcard").length,
    live: document.querySelectorAll("#handRow .hcard.live").length,
    muteBass: DREAM.p.muteBass, muteChord: DREAM.p.muteChord, muteLead: DREAM.p.muteLead,
    thKey: document.getElementById("thKey").textContent,
    thNow: document.getElementById("thNow").textContent }));
  if (stg0.stage !== 0 || stg0.cards !== 3 || stg0.live !== 1) fail("drum deal wrong " + JSON.stringify(stg0));
  else if (!(stg0.muteBass && stg0.muteChord && stg0.muteLead)) fail("future traits sound before they exist");
  else if (stg0.thKey !== "—" || stg0.thNow !== "drums first") fail("theory bar invents a key at the drum stage ('" + stg0.thKey + "'/'" + stg0.thNow + "')");
  else ok("stage 0: three drummers dealt, one live, future traits muted, theory honest");

  /* the clock probe measures the FIGURE engine — make sure a curated (not
     library) drummer is live; the library path has its own probe later */
  await page.evaluate(() => {
    for (let t = 0; t < 12; t++) {
      /* dsty players swing on purpose (MPC math) — they are not clock evidence */
      const i = BUILD.hand.findIndex(c => c && c.dlib == null && c.dsty == null);
      if (i >= 0) { if (i !== BUILD.live) auditionCard(i); return; }
      dreamDice();
    }
  });
  await page.waitForFunction(() => DREAM.on && !DREAM.pending && DREAM.p.dlib == null && !DREAM.p.dsty, undefined, undefined, { timeout: 25000 });
  const tSwap = await page.evaluate(() => ctx.currentTime - TAKE.t0);
  /* the clock on the tape: correlated, not white — grid-aware, humanity-aware.
     Wait for enough FIGURE-lane tape first (after any drummer swap — earlier
     events belong to another figure and tempo): a sparse figure needs bars */
  await page.waitForFunction(t0 => {
    const P = TAKE.ev.filter(e => e.t > t0 && e.role === "perc" && (e.ln ? e.ln === "fig" : true) && e.vel >= 0.3);
    return P.length >= 20;
  }, tSwap, { timeout: 60000 }).catch(() => {});
  const clk = await page.evaluate(t0 => {
    const f = LDR_FIG[DREAM.p.fig];
    const step = (60 / state.tempo) / (f.grid / 4);
    /* one limb, one wave: the main figure rides the kit-wave, companions the
       perc-wave; a shared recipe NAME interleaves both waves under one name
       and reads anti-correlated — so measure the figure lane (ln tag) alone */
    const fresh = TAKE.ev.filter(e => e.t > t0);
    const tagged = fresh.filter(e => e.role === "perc" && e.ln === "fig");
    /* a kit-lane figure (marchTwoBeat, caixa, cavacha…) logs as role kit, not
       perc — the clock law holds on any lane, so measure whichever the figure rides */
    const perc = fresh.filter(e => e.role === "perc"), kitL = fresh.filter(e => e.role === "kit");
    const all = tagged.length ? tagged : (perc.length >= 8 ? perc : kitL);
    const byName = {};
    all.forEach(e => { const k = e.name || ("kit" + e.note); (byName[k] = byName[k] || []).push(e); });
    const P = (Object.values(byName).sort((a, b) => b.length - a.length)[0] || [])
      .filter(e => e.vel >= 0.3)   /* roll grace-notes are off-grid ON PURPOSE — not clock evidence */
      .sort((a, b) => a.t - b.t);
    if (P.length < 8) return { n: P.length };
    const raw = P.map(e => e.t % step);
    const med = raw.slice().sort((a, b) => a - b)[raw.length >> 1];
    const dev = raw.map(x => { let d = x - med; if (d > step / 2) d -= step; if (d < -step / 2) d += step; return d; });
    const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
    const m = mean(dev), sd = Math.sqrt(mean(dev.map(x => (x - m) * (x - m))));
    let n1 = 0, d1 = 0; for (let i = 0; i + 1 < dev.length; i++) n1 += (dev[i] - m) * (dev[i + 1] - m);
    dev.forEach(x => d1 += (x - m) * (x - m));
    return { n: P.length, hum: DREAM.p.hum, sdMs: sd * 1000,
      maxMs: Math.max(...dev.map(Math.abs)) * 1000, lag1: d1 ? n1 / d1 : 0 };
  }, tSwap);
  if (clk.n < 8) fail("too few figure hits to measure the clock (" + clk.n + ")");
  else if (!(clk.sdMs >= 0 && clk.sdMs < 14)) fail("clock breadth off: sd " + clk.sdMs.toFixed(2) + "ms");
  else if (!(clk.maxMs < 60)) fail("clock outlier " + clk.maxMs.toFixed(1) + "ms");
  /* lag-1 on n events carries ~±1/√n noise, and a SPARSE figure samples the
     wander field at wide intervals — small samples in the human sd band pass
     on breadth; the correlation bar binds only once the sample can carry it */
  else if (clk.hum >= .5 && !(clk.sdMs > 0.3) )
    fail("human drummer reads as a machine (hum " + (+clk.hum).toFixed(2) + ", sd " + clk.sdMs.toFixed(2) + "ms)");
  else if (clk.hum >= .5 && clk.n >= 24 && !(clk.lag1 > 0.12))
    fail("human drummer reads as white jitter (hum " + (+clk.hum).toFixed(2) + ", sd " + clk.sdMs.toFixed(2) + ", lag-1 " + clk.lag1.toFixed(2) + ", n " + clk.n + ")");
  else ok("the drummer's clock on tape: hum " + (+clk.hum).toFixed(2) + " · " + clk.sdMs.toFixed(1) + "ms sd · lag-1 " + clk.lag1.toFixed(2));

  /* ROLL deals a fresh hand without dropping the transport */
  const hand0 = await page.evaluate(() => BUILD.hand.map(c => c.name).join("|"));
  await page.click("#dreamDice");
  await page.waitForFunction(() => DREAM.on && !DREAM.pending, undefined, { timeout: 12000 });
  const roll1 = await page.evaluate(() => ({ on: DREAM.on, stage: BUILD.stage,
    names: BUILD.hand.map(c => c.name).join("|"), live: BUILD.live }));
  if (!roll1.on) fail("ROLL killed the performance");
  else if (roll1.names === hand0) fail("ROLL dealt the same hand");
  else if (roll1.stage !== 0 || roll1.live !== 0) fail("ROLL state off " + JSON.stringify(roll1));
  else ok("ROLL: fresh hand of drummers, transport never dropped");

  /* the build: hear it, keep it, next trait deals itself — five taps to a song */
  const keepLive = async () => {
    await page.evaluate(() => { const c = document.querySelector("#handRow .hcard.live"); if (c) c.click(); });
    await page.waitForFunction(() => !DREAM.pending, undefined, { timeout: 15000 });
    await page.waitForTimeout(120);
  };
  /* audition drummer card 1, then keep it */
  await page.click('#handRow .hcard[data-c="1"]');
  await page.waitForFunction(() => !DREAM.pending, undefined, { timeout: 12000 });
  const audA = await page.evaluate(() => ({ live: BUILD.live, fig: DREAM.p.fig, want: BUILD.hand[1].fig }));
  if (audA.live !== 1 || audA.fig !== audA.want) fail("audition did not swap the drummer in " + JSON.stringify(audA));
  else ok("tap to hear: card 2's drummer swapped in on the bar (" + audA.fig + ")");
  await keepLive();                       /* -> stage 1, low end auto-auditioning */
  const stg1 = await page.evaluate(() => ({ stage: BUILD.stage, kept0: BUILD.kept[0] && BUILD.kept[0].name,
    muteBass: DREAM.p.muteBass, muteChord: DREAM.p.muteChord,
    key: document.getElementById("thKey").textContent,
    thNow: document.getElementById("thNow").textContent }));
  if (stg1.stage !== 1 || !stg1.kept0) fail("keep did not advance to the low end " + JSON.stringify(stg1));
  else if (stg1.muteBass || !stg1.muteChord) fail("low-end mutes wrong " + JSON.stringify(stg1));
  else if (!/^[A-G]#? (MAJOR|MINOR)$/.test(stg1.key) || stg1.thNow !== "key set · changes next")
    fail("theory bar at the low end: '" + stg1.key + "'/'" + stg1.thNow + "'");
  else ok("tap again to keep: THE LOW END dealt itself, bass live, key honest (" + stg1.key + ")");
  await keepLive();                       /* -> stage 2, changes auto-auditioning */
  await page.waitForFunction(() => DREAM.on && !DREAM.p.muteChord, undefined, { timeout: 15000 });
  await page.waitForFunction(() => TAKE.ev.filter(e => e.role === "chord").length >= 5, undefined, { timeout: 40000 });
  const stg2 = await page.evaluate(() => ({ stage: BUILD.stage,
    cells: document.querySelectorAll("#thProg .thCell").length, prog: DREAM.p.prog.length,
    pn: document.getElementById("thProgName").textContent, pnWant: DREAM.p.progName || "" }));
  if (stg2.stage !== 2 || stg2.cells !== stg2.prog || stg2.cells < 2) fail("changes stage theory " + JSON.stringify(stg2));
  else if (stg2.pn !== stg2.pnWant) fail("progression name mismatch '" + stg2.pn + "'");
  else ok("THE CHANGES: named progression live, " + stg2.cells + " cells (" + stg2.pn + ")");
  const hum = await page.evaluate(() => {
    const ch = TAKE.ev.filter(e => e.role === "chord").sort((a, b) => a.t - b.t);
    if (ch.length < 3) return { n: ch.length };
    const t0c = ch[0].t, cl = ch.filter(e => e.t - t0c < 0.1);
    const spread = Math.max(...cl.map(e => e.t)) - t0c;
    const vels = new Set(ch.map(e => e.vel.toFixed(3))).size;
    return { n: ch.length, cn: cl.length, spread, vels };
  });
  if (hum.n < 3) fail("no chord events on the tape (" + hum.n + ")");
  else if (!(hum.cn >= 2 && hum.spread > 0.002 && hum.spread < 0.09))
    fail("chord cluster not humanly rolled (" + hum.cn + " notes, " + (hum.spread * 1000).toFixed(1) + "ms)");
  else if (hum.vels < 2) fail("chord dynamics flat (" + hum.vels + " velocity values)");
  else ok("the hand on the tape: chords roll " + (hum.spread * 1000).toFixed(1) + "ms · " + hum.vels + " velocity shades");
  await keepLive();                       /* -> stage 3, the voice auto-auditioning */
  await page.waitForFunction(() => DREAM.on && !DREAM.p.muteLead, undefined, { timeout: 15000 });
  await page.waitForFunction(() => TAKE.ev.filter(e => e.role === "lead").length >= 2, undefined, { timeout: 40000 });
  const hk = await page.evaluate(() => {
    const L = TAKE.ev.filter(e => e.role === "lead").sort((a, b) => a.t - b.t);
    const beat = 60 / state.tempo;
    let gaps = 0;
    for (let i = 1; i < L.length; i++) if (L[i].t - L[i - 1].t > beat * 1.2) gaps++;
    const drums = TAKE.ev.filter(e => e.role === "perc" || e.role === "kit" || e.role === "dd").length;
    return { stage: BUILD.stage, n: L.length, gaps, drums, hook: !!DREAM.hook,
      elibs: !!(DREAM.p && DREAM.p.elibs && DREAM.p.elibs.length),
      contour: DREAM.hook && DREAM.hook.contour };
  });
  /* trait 3 speaks one of two ways: the curated HOOK engine, or a library
     EMBELLISH bag (round 5) — gestures at phrase ends, silence otherwise */
  if (hk.stage !== 3 || (!hk.hook && !hk.elibs)) fail("THE EMBELLISH stage broken " + JSON.stringify(hk));
  /* one bar of one cell (4 notes) legitimately has no internal phrase gap —
     require a breath only once a HOOK line is long enough to owe one
     (a gesture bag breathes by construction: silence surrounds each lick) */
  else if (hk.hook && !hk.elibs && hk.n >= 5 && hk.gaps < 1) fail("the lead never breathes (0 rests across " + hk.n + " notes)");
  else if (hk.n > hk.drums) fail("lead outruns the drums — arpeggiator behavior (" + hk.n + " vs " + hk.drums + ")");
  else ok("THE EMBELLISH: " + (hk.elibs ? "library gestures speak sparsely" : "the hook speaks") +
    " — " + hk.n + " notes, " + hk.gaps + " breaths" + (hk.contour ? ", contour '" + hk.contour + "'" : ""));
  await keepLive();                       /* -> stage 4, the shape */
  const stg4 = await page.evaluate(() => ({ stage: BUILD.stage,
    names: BUILD.hand.map(c => c.format).join("|"), live: BUILD.live }));
  if (stg4.stage !== 4 || stg4.names !== "loop|arc|song") fail("THE SHAPE hand wrong " + JSON.stringify(stg4));
  else ok("THE SHAPE: loop · arc · song on the table");
  await page.click('#handRow .hcard[data-c="1"]');   /* hear ARC */
  await page.waitForFunction(() => !DREAM.pending, undefined, { timeout: 12000 });
  await keepLive();                       /* -> done */
  const done = await page.evaluate(() => ({ stage: BUILD.stage,
    doneCard: !!document.querySelector("#handRow .hdone"),
    railDone: document.querySelectorAll("#traitRail .trSlot.done").length,
    fmt: DREAM.p.format, building: !!DREAM.p._building,
    mutes: [DREAM.p.muteBass, DREAM.p.muteChord, DREAM.p.muteLead].some(Boolean),
    name: DREAM.p.name, on: DREAM.on }));
  if (done.stage !== 5 || !done.doneCard || done.railDone !== 5) fail("the song never stood " + JSON.stringify(done));
  else if (done.fmt !== "arc" || done.building || done.mutes || !done.on)
    fail("finished song state wrong " + JSON.stringify(done));
  else ok("SONG STANDING after 5 traits: " + done.name + " · shape " + done.fmt + " · full band, still rolling");

  /* remix: tap a filled trait — it reopens with the kept pick first, band still up */
  await page.evaluate(() => { document.querySelector('#traitRail .trSlot[data-t="0"]').click(); });
  await page.waitForTimeout(200);
  const rmx = await page.evaluate(() => ({ stage: BUILD.stage, live: BUILD.live,
    first: BUILD.hand[0] && BUILD.hand[0].name, kept: BUILD.kept[0] && BUILD.kept[0].name,
    on: DREAM.on, muteLead: DREAM.p.muteLead }));
  if (rmx.stage !== 0 || rmx.first !== rmx.kept || rmx.live !== 0) fail("remix reopen wrong " + JSON.stringify(rmx));
  else if (!rmx.on || rmx.muteLead) fail("remix dropped the band " + JSON.stringify(rmx));
  else ok("remix: THE DRUMMER reopened with the kept player in hand, full band still under it");
  await page.evaluate(() => { const c = document.querySelector("#handRow .hcard.live"); if (c) c.click(); });
  await page.waitForFunction(() => BUILD.stage === 5, undefined, { timeout: 12000 });
  await page.waitForFunction(() => !DREAM.pending, undefined, { timeout: 12000 });
  ok("re-keep: one tap and the song stands again");

  /* BREAK-lite: an un-kept audition must not outlive a trait jump — the rail
     is the avatar, so the ear gets the kept avatar back on the bar */
  const stray = await page.evaluate(() => {
    document.querySelector('#traitRail .trSlot[data-t="3"]').click();      /* reopen THE VOICE */
    const alt = BUILD.hand.findIndex((c, i) => i !== BUILD.live);
    document.querySelector('#handRow .hcard[data-c="' + alt + '"]').click(); /* audition, do NOT keep */
    const heardAlt = (DREAM.pending || DREAM.p).lead === BUILD.hand[alt].lead;
    document.querySelector('#traitRail .trSlot[data-t="0"]').click();      /* jump away mid-audition */
    const pend = DREAM.pending || DREAM.p;
    return { heardAlt, keptBack: pend.lead === BUILD.kept[3].lead && !pend.muteLead,
      live: BUILD.live, first: BUILD.hand[0] === BUILD.kept[0] };
  });
  if (!stray.heardAlt) fail("voice audition did not reach the ear " + JSON.stringify(stray));
  else if (!stray.keptBack) fail("stray audition outlives a trait jump — rail and ear disagree " + JSON.stringify(stray));
  else if (stray.live !== 0 || !stray.first) fail("jump landed wrong " + JSON.stringify(stray));
  else ok("trait jump mid-audition: the un-kept voice is dropped, the kept avatar sounds again");
  /* BREAK-lite: stage-4 hands are FORMATS verbatim — jumping to the shape must
     light the KEPT format, not card 0 */
  const shape = await page.evaluate(() => {
    document.querySelector('#traitRail .trSlot[data-t="4"]').click();
    return { live: BUILD.live, want: BUILD.hand.indexOf(BUILD.kept[4]),
      names: BUILD.hand.map(c => c.format).join("|") };
  });
  if (shape.names !== "loop|arc|song" || shape.live !== shape.want || shape.live < 0)
    fail("shape jump lights the wrong card " + JSON.stringify(shape));
  else ok("shape jump lights the kept format (card " + (shape.live + 1) + ")");
  await page.evaluate(() => { const c = document.querySelector("#handRow .hcard.live"); if (c) c.click(); });
  await page.waitForFunction(() => BUILD.stage === 5 && !DREAM.pending, undefined, { timeout: 12000 });

  /* round 5 — THE RACK SHELF: kept traits materialize as 2U units; patching
     is dice/prev/next on the unit, never a list */
  const rack = await page.evaluate(() => ({
    units: document.querySelectorAll("#rackShelf .rku").length,
    meters: document.querySelectorAll("#rackShelf canvas.rkmeter").length,
    labels: [...document.querySelectorAll("#rackShelf .rklab")].map(x => x.textContent) }));
  if (rack.units !== 4 || rack.meters !== 4) fail("rack shelf wrong " + JSON.stringify(rack));
  else if (rack.labels[2] !== "THE COUNTER" || rack.labels[3] !== "THE EMBELLISH")
    fail("rack labels " + JSON.stringify(rack.labels));
  else ok("the rack shelf: 4 kept traits as 2U units with meters (" + rack.labels.join(" · ") + ")");
  const rkOps = await page.evaluate(() => {
    const bass0 = BUILD.kept[1].bass, name2 = BUILD.kept[2].name;
    document.querySelector('.rku[data-slot="1"] .rkbtn[data-act="next"]').click();
    document.querySelector('.rku[data-slot="2"] .rkbtn.rkroll').click();
    return { bass0, name2, bass1: BUILD.kept[1].bass, name2b: BUILD.kept[2].name,
      pend: !!DREAM.pending, on: DREAM.on };
  });
  await page.waitForFunction(() => !DREAM.pending, undefined, { timeout: 15000 });
  const rkAfter = await page.evaluate(() => ({ pBass: DREAM.p.bass, pOn: DREAM.on,
    catOk: PROGRAMS[BUILD.kept[1].bass].cat === "BASS" }));
  if (rkOps.bass1 === rkOps.bass0 || !rkAfter.catOk) fail("rack voice ‹›  did not move within the drawer " + JSON.stringify(rkOps));
  else if (rkOps.name2b === rkOps.name2) fail("rack ◇ dealt the same take");
  else if (!rkOps.on || !rkAfter.pOn || rkAfter.pBass !== rkOps.bass1) fail("rack patch not live on the bar " + JSON.stringify(rkAfter));
  else ok("rack patching: ‹› walked the bass drawer, ◇ re-dealt the counter, all on the bar");
  /* round 5 — DYNAMIC HEADROOM: the console re-staged as parts stacked, the
     move rides the tape, and the full band carries less per-role gain */
  const stage = await page.evaluate(() => ({
    mixEvs: TAKE.ev.filter(e => e.role === "mix").length,
    lastS: (TAKE.ev.filter(e => e.role === "mix").slice(-1)[0] || {}).s,
    chordIn: MIX.chord.in.gain.value,
    want: mixStageFor(4).chord }));
  if (stage.mixEvs < 2) fail("headroom staging never logged to the tape (" + stage.mixEvs + ")");
  else if (!stage.lastS || Math.abs(stage.lastS.chord - stage.want) > 1e-6)
    fail("full-band stage wrong " + JSON.stringify(stage.lastS));
  else if (!(stage.chordIn < 0.78)) fail("chord strip not re-staged (gain " + stage.chordIn.toFixed(3) + ")");
  else ok("dynamic headroom: " + stage.mixEvs + " console moves on the tape · chord strip at " +
    stage.chordIn.toFixed(2) + " under the full band");

  /* round 6 — GAIN STAGING: the master chain must run clean under the full
     band (the raw bus once peaked 3.26 and the tube stage hard-clamped) */
  const stagingClean = await page.evaluate(async () => {
    const taps = { tube: window._chain.tube, limOut: window._mixTap, dest: master };
    const ans = {}; for (const k in taps) { const a = ctx.createAnalyser(); a.fftSize = 2048; taps[k].connect(a); ans[k] = a; }
    const buf = new Float32Array(2048);
    const st = {}; for (const k in ans) st[k] = { peak: 0, hot: 0, n: 0 };
    const t0 = performance.now();
    while (performance.now() - t0 < 6000) {
      for (const k in ans) { ans[k].getFloatTimeDomainData(buf); const s = st[k];
        for (let i = 0; i < buf.length; i += 2) { const v = Math.abs(buf[i]);
          if (v > s.peak) s.peak = v; if (v >= 0.985) s.hot++; s.n++; } }
      await new Promise(r => setTimeout(r, 40));
    }
    const o = {}; for (const k in st) o[k] = { peak: +st[k].peak.toFixed(3), pctHot: +(100 * st[k].hot / st[k].n).toFixed(3) };
    for (const k in ans) try { taps[k].disconnect(ans[k]); } catch (_) {}
    o.vol = state.volume;
    return o;
  });
  if (stagingClean.tube.pctHot > 0.25) fail("tube stage clamping (" + JSON.stringify(stagingClean.tube) + ")");
  else if (stagingClean.limOut.pctHot > 0.1) fail("limiter flat-topping (" + JSON.stringify(stagingClean.limOut) + ")");
  else if (stagingClean.dest.peak > 0.95) fail("destination too hot (" + JSON.stringify(stagingClean.dest) + ")");
  else ok("gain staging clean under the full band: tube pk " + stagingClean.tube.peak +
    " · out pk " + stagingClean.dest.peak + " · 0 flat-tops @ vol " + stagingClean.vol);
  /* ROUND 10 — THE SONG, NOT THE SEARCH: MIX bounces the final selections
     arranged from the top (intro + the shape's sections), not the take with
     its auditioning; deterministic; the player's search notes stay out */
  {
    const comp = await page.evaluate(() => { const verb0 = VERB.pct; const a = songEvents(DREAM.p), b = songEvents(DREAM.p); window._verbHeld = VERB.pct === verb0;
      const key = e => [+e.t.toFixed(4), e.role, e.note != null ? e.note : (e.zone != null ? e.zone : e.name || ""), +(e.vel || 0).toFixed(4)].join("|");
      const same = a && b && a.evs.length === b.evs.length && a.evs.every((e, i) => key(e) === key(b.evs[i]));
      return { ok: !!a, bars: a && a.bars, seconds: a && a.seconds, n: a && a.evs.length, format: a && a.format, same, want: songBars(DREAM.p),
        roles: a ? [...new Set(a.evs.map(e => e.role))] : [], takeLen: TAKE.ev.length, takeT0: TAKE.t0, dreamBar: DREAM.bar, on: DREAM.on }; });
    const verbHeld = await page.evaluate(() => window._verbHeld);
    if (!comp.ok || comp.bars !== comp.want || !(comp.n > comp.bars * 4)) fail("song composition wrong " + JSON.stringify(comp));
    else if (!verbHeld) fail("the composition moved the dialed VERB");
    else if (!comp.same) fail("the song composes differently twice");
    else if (comp.roles.includes("you")) fail("the song bounce carries the search (you-role events)");
    else ok("the song composes DRY: " + comp.bars + " bars (" + comp.format + "), " + comp.n + " events, " + comp.seconds.toFixed(1) + " s, deterministic, roles " + comp.roles.join("/") + " — the live take untouched (" + comp.takeLen + " events)");
    await page.evaluate(() => { saveMenu(); });
    await page.waitForFunction(() => !!document.getElementById("svMix"), undefined, undefined, { timeout: 5000 }).catch(() => {});
    const dlS = downloads.length;
    await page.click("#svMix");
    await page.waitForFunction(() => exporting, undefined, { timeout: 5000 }).catch(() => {});
    await page.waitForFunction(() => !exporting, undefined, { timeout: 300000 });
    await page.waitForTimeout(900);
    const sb = await page.evaluate(() => window._lastBounce);
    const wavS = downloads.slice(dlS).find(d => d.suggestedFilename().endsWith(".wav"));
    if (!sb || sb.src !== "song" || sb.youN !== 0) fail("MIX did not bounce the song " + JSON.stringify(sb));
    else if (!wavS || /-jam/.test(wavS.suggestedFilename())) fail("song MIX produced no WAV (" + (wavS && wavS.suggestedFilename()) + ")");
    else {
      const os4 = require("os"), fs4 = require("fs"), pj4 = require("path").join;
      const wp4 = pj4(os4.tmpdir(), "tr-song.wav"); await wavS.saveAs(wp4);
      const w4 = fs4.readFileSync(wp4); const dataAt = w4.indexOf("data") + 8; const sr4 = w4.readUInt32LE(24); const secs = (w4.length - dataAt) / (3 * 2 * sr4); /* the WAV's own rate — this Chromium runs at 44.1 k */
      if (!(secs >= sb.seconds && secs < sb.seconds + 12)) fail("song WAV length " + secs.toFixed(1) + " s vs composed " + sb.seconds + " s (+tail)");
      else ok("MIX renders the SONG: " + sb.bars + " bars, " + secs.toFixed(1) + " s of WAV for " + sb.seconds.toFixed(1) + " s composed (" + wavS.suggestedFilename() + ")");
    }
  }

  /* round 6 — VERB: one reverb decision, 10% steps, live on the send */
  const verb = await page.evaluate(() => {
    const fx = PROGRAMS[DREAM.p.chord].fx.reverb;
    const r0 = { pct: VERB.pct, lbl: document.getElementById("verbPct").textContent, send: +rSend.gain.value.toFixed(4) };
    document.querySelector('#verbCtl .vbtn[data-d="-1"]').click();
    const r1 = { pct: VERB.pct, send: +rSend.gain.value.toFixed(4) };
    document.querySelector('#verbCtl .vbtn[data-d="1"]').click();
    document.querySelector('#verbCtl .vbtn[data-d="1"]').click();
    const r2 = { pct: VERB.pct, lbl: document.getElementById("verbPct").textContent, send: +rSend.gain.value.toFixed(4) };
    verbSet(50);
    return { fx, r0, r1, r2 };
  });
  if (verb.r0.pct !== 50 || verb.r0.lbl !== "50%" || Math.abs(verb.r0.send - verb.fx * .5) > 1e-3)
    fail("VERB default wrong " + JSON.stringify(verb));
  else if (verb.r1.pct !== 40 || Math.abs(verb.r1.send - verb.fx * .4) > 1e-3)
    fail("VERB − did not step the send " + JSON.stringify(verb.r1));
  else if (verb.r2.pct !== 60 || verb.r2.lbl !== "60%" || Math.abs(verb.r2.send - verb.fx * .6) > 1e-3)
    fail("VERB + did not step the send " + JSON.stringify(verb.r2));
  else ok("VERB: 50% default halves the program send · − to 40% · + to 60%, live each step");

  /* ── round 8: the saws, measured clean. The program insert was tanh(13x)
     — a hard clipper — fed by an untrimmed bus that a saw chord drove to
     2-4; every brass/lead saw ships drive>0, so the wet path flat-topped
     under chords. Now: osc-stack normalization, a ±2 headroom domain, and
     a k law that saturates instead of railing. Convict on numbers. ── */
  const saw = await page.evaluate(async () => {
    dreamStop(true);
    await new Promise(r => setTimeout(r, 400));
    if (ctx.state !== "running") { try { await ctx.resume(); } catch (_) {} }
    const fb = new Float32Array(2048), fs = new Float32Array(2048);
    const mkAn = node => { const an = ctx.createAnalyser(); an.fftSize = 2048; node.connect(an); return an; };
    const meas = async (anA, anB, ms, domain) => {
      let pkA = 0, pkB = 0, hotB = 0, nB = 0, rmsB = 0, overA = 0, nA = 0;
      const t0 = performance.now();
      while (performance.now() - t0 < ms) {
        anA.getFloatTimeDomainData(fb); anB.getFloatTimeDomainData(fs);
        for (let i = 0; i < fb.length; i++) { const a = Math.abs(fb[i]); if (a > pkA) pkA = a;
          /* past the curve's domain is where WebAudio clamps to the endpoint —
             the actual clipping mechanism, counted at its own cause */
          if (domain && a >= domain) overA++; nA++; }
        for (let i = 0; i < fs.length; i++) { const a = Math.abs(fs[i]); if (a > pkB) pkB = a;
          if (a >= .985) hotB++; nB++; rmsB += fs[i] * fs[i]; }
        await new Promise(r => setTimeout(r, 12));
      }
      return { pkA: +pkA.toFixed(3), pkB: +pkB.toFixed(3),
        over: +(overA / Math.max(1, nA)).toFixed(5),
        gainDb: +(20 * Math.log10(Math.max(1e-9, pkB) / Math.max(1e-9, pkA))).toFixed(2),
        hot: +(hotB / Math.max(1, nB)).toFixed(5), rms: +Math.sqrt(rmsB / Math.max(1, nB)).toFixed(4) };
    };
    /* 1 — the fortissimo saw chord through the insert (Sforzando Brass, drive .2).
       Tap the insert's OUTPUT (post = wet+dry), not the shaper: the curve's
       own reference normalization bounds the shaper at ~0.6 for any input,
       so a "does it rail" check there can never fail — a rubber stamp. The
       dry leg has no shaper, so post is the honest, unbounded node. */
    state.mode = "PROG"; setProgram(6); state.arp.on = false;
    const anBus = mkAn(window._progTap.bus), anShp = mkAn(window._progTap.post);
    [60, 64, 67].forEach(n => _midiInject([0x90, n, 127]));
    await new Promise(r => setTimeout(r, 300));
    /* the shaper sees bus*DRIVE_HEADROOM, so a bus past ±1/DRIVE_HEADROOM is
       past the curve and gets endpoint-clamped — that IS the distortion.
       Read the constant, never hardcode it: the gate must track the law. */
    const chord = await meas(anBus, anShp, 2200, 1 / DRIVE_HEADROOM);
    [60, 64, 67].forEach(n => _midiInject([0x80, n, 0]));
    await new Promise(r => setTimeout(r, 500));
    /* 2 — the drive-0 saw pad under a latched STRUM: the master tube's turn */
    setProgram(39);
    state.arp.on = true; state.arp.patt = "STRUM"; state.arp.reso = "16"; state.arp.latch = true;
    const anTube = mkAn(window._chain.glue), anOut = mkAn(window._chain.tube);
    [55, 62, 67, 71].forEach(n => _midiInject([0x90, n, 120]));
    await new Promise(r => setTimeout(r, 400));
    const strum = await meas(anTube, anOut, 4200);
    state.arp.on = false; state.arp.latch = false; allNotesOff();
    try { window._progTap.bus.disconnect(anBus); window._progTap.shaper.disconnect(anShp);
      window._chain.glue.disconnect(anTube); window._chain.tube.disconnect(anOut); } catch (_) {}
    return { chord, strum, voicesLeft: activeVoices };
  });
  if (!(saw.chord.pkA > 0.4)) fail("saw chord probe made no signal (bus pk " + saw.chord.pkA + ")");
  else if (saw.chord.over !== 0)
    fail("the saw chord drives past the curve's domain — endpoint clamp, i.e. the old clipping (" +
      (saw.chord.over * 100).toFixed(2) + "% of samples |bus|≥2)");
  /* post is an unclamped SUM (the dry leg has no shaper), so a peak above 1
     there is not clipping — busTrim and the master chain take it from here,
     and round 6's gates already police that end. What post DOES prove is
     the round-8 law: the insert must not INFLATE the signal (the old
     clipper ran a saw chord +4.8 dB hot). Measure the ratio it passes. */
  else if (!(saw.chord.gainDb > -3 && saw.chord.gainDb < 1.5))
    fail("the insert is not level-neutral on a saw chord (" + saw.chord.gainDb.toFixed(2) +
      " dB bus→post; the old clipper ran about +4.8)");
  else if (!(saw.chord.rms > 0.015)) fail("drive went dead — wet path silent (rms " + saw.chord.rms + ")");
  else ok("saw chord clean through the insert: bus pk " + saw.chord.pkA + " (0% past the curve domain) → post pk " +
    saw.chord.pkB + " · " + saw.chord.gainDb.toFixed(2) + " dB, level-neutral · wet alive (rms " + saw.chord.rms + ")");
  if (!(saw.strum.pkA > 0.15)) fail("STRUM probe made no signal (tube-in pk " + saw.strum.pkA + ")");
  else if (!(saw.strum.hot <= 0.01))
    fail("saw pad STRUM still flat-tops the tube (" + (saw.strum.hot * 100).toFixed(2) + "% ≥.985)");
  else ok("saw pad under latched STRUM: tube-in pk " + saw.strum.pkA + " → tube-out pk " + saw.strum.pkB +
    " · " + (saw.strum.hot * 100).toFixed(2) + "% hot (≤1% law)");

  /* round 5 — THE LIBRARY: mined human playing, embedded with provenance */
  const lib = await page.evaluate(() => ({ n: PHRASES.length,
    dr: PHRASE_IDX.dr.length, fill: PHRASE_IDX.fill.length,
    bs: PHRASE_IDX.bs.length, cp: PHRASE_IDX.cp.length, em: PHRASE_IDX.em.length,
    srcOk: PHRASES.every(p => /^(groove-midi:|openscore-quartets:)/.test(p.src)),
    named: PHRASES.every(p => p.n && p.n.length >= 3),
    decodable: PHRASES.every(p => (p.k === "dr" ? ldrpUnpackDrum(p.e) : ldrpUnpackMel(p.e)).length > 0) }));
  if (lib.n < 150 || !lib.dr || !lib.fill || !lib.bs || !lib.cp || !lib.em) fail("library thin " + JSON.stringify(lib));
  else if (!lib.srcOk || !lib.named || !lib.decodable) fail("library provenance/naming/decode holes " + JSON.stringify(lib));
  else ok("the library: " + lib.n + " human phrases embedded (" + lib.dr + " grooves · " + lib.fill +
    " fills · " + lib.bs + " bass · " + lib.cp + " counters · " + lib.em + " licks), every src labeled");
  /* a library-led song: groove field on, counter sparse, embellish mostly silence */
  const libSong = await page.evaluate(() => {
    const r = mulberry(4242);
    let d = null; for (let k = 0; k < 300 && (!d || d.dlib == null); k++) d = candDrums(r);
    let b = null; for (let k = 0; k < 300 && (!b || b.blib == null); k++) b = candBass(r);
    let c = null; for (let k = 0; k < 600 && (!c || c.clib == null); k++) c = candChords(r, b);
    let l = null; for (let k = 0; k < 300 && (!l || !l.elibs); k++) l = candLead(r);
    if (!d || d.dlib == null || b.blib == null || c.clib == null || !l.elibs) return { bad: true };
    BUILD.kept = [d, b, c, l, FORMATS[0]]; BUILD.stage = 5; BUILD.hand = []; BUILD.live = -1;
    const p = composeP(BUILD.kept, null, 5);
    if (DREAM.on) { DREAM.pending = p; } else startWith(p, true);
    builderRender(); rackRender();
    return { name: PHRASES[d.dlib].n, style: PHRASES[d.dlib].s, fill: d.flib != null };
  });
  if (libSong.bad) fail("library cards would not deal");
  else ok("library song standing: " + libSong.name + " (" + libSong.style + ")" + (libSong.fill ? " with a paired fill" : ""));
  await page.waitForFunction(() => !DREAM.pending && DREAM.gfield, undefined, undefined, { timeout: 25000 });
  const t0lib = await page.evaluate(() => ({ n: TAKE.ev.length, t: ctx.currentTime }));
  /* a library drummer may wear a DD22 kit — its hits log as "dd", same drums */
  await page.waitForFunction(t0 =>
    TAKE.ev.filter(e => (e.role === "kit" || e.role === "dd") && e.t > (t0.t - TAKE.t0)).length > 40, t0lib, { timeout: 90000 });
  const libTape = await page.evaluate(t0 => {
    const beat = 60 / state.tempo;
    const bars = Math.max(1, (ctx.currentTime - t0.t) / (beat * 4));
    const since = e => e.t > (t0.t - TAKE.t0);
    const kitN = TAKE.ev.filter(e => (e.role === "kit" || e.role === "dd") && since(e)).length;
    const chordN = TAKE.ev.filter(e => e.role === "chord" && since(e)).length;
    const leadN = TAKE.ev.filter(e => e.role === "lead" && since(e)).length;
    return { gf: !!DREAM.gfield, bars: +bars.toFixed(1), kitPerBar: +(kitN / bars).toFixed(1),
      chordPerBar: +(chordN / bars).toFixed(1), leadPerBar: +(leadN / bars).toFixed(1) };
  }, t0lib);
  if (!libTape.gf) fail("groove field missing under a library drummer");
  else if (libTape.kitPerBar < 6) fail("library drums too thin (" + libTape.kitPerBar + "/bar)");
  else if (libTape.chordPerBar > 7) fail("the counter is not sparse (" + libTape.chordPerBar + "/bar — no space left for a vocalist)");
  else if (libTape.leadPerBar > 3.5) fail("embellishments crowd the song (" + libTape.leadPerBar + "/bar)");
  else ok("the library band on tape: " + libTape.kitPerBar + " drum hits/bar · counter " +
    libTape.chordPerBar + "/bar · licks " + libTape.leadPerBar + "/bar — the middle stays open");
  /* the library song stays LIVE: the handoff, bounce and KEEP tests below
     now run against a library-backed dream — presets carry phrase refs */

  /* figure chip mid-dream: transport hands off, the tape keeps rolling (BREAK fix) */
  await page.evaluate(() => document.body.classList.add("engineOpen"));
  await page.waitForTimeout(120);
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
  /* round 8: SAVE stops the track FIRST (the donor renders on an isolated
     engine; ours swaps the graph — so it stops), then opens the three doors */
  await page.click("#ldrSave");
  const doors = await page.evaluate(() => ({ dream: DREAM.on, ldr: LDR.on, take: TAKE.on,
    n: ["svMix", "svScore", "svSession", "svLink", "svJam"].filter(id => !!document.getElementById(id)).length,
    evs: TAKE.ev.length, arp: state.arp.on, voices: activeVoices }));
  if (doors.dream || doors.ldr || doors.take || doors.arp) fail("SAVE did not stop the track " + JSON.stringify(doors));
  else if (doors.n !== 5) fail("the five doors did not open (" + doors.n + "/5)");
  else ok("SAVE stops the track, keeps the take (" + doors.evs + " events), opens MIX · SCORE · SESSION · LINK · JAM");
  /* round 9 (the performance lens): the render must instantiate voices in
     windows — count the voices standing when startRendering is called */
  await page.evaluate(() => { window._lazy = { atStart: -1, total: 0, last: TAKE.ev.reduce((m, e) => Math.max(m, e.t), 0),
      late: TAKE.ev.filter(e => e.role !== "mix" && e.t >= RENDER_WIN + .25).length };
    /* every hit path counts: synth voices, DD kit hits, the 808 line, the physics percussion */
    const sv = spawnVoice; spawnVoice = function () { window._lazy.total++; return sv.apply(this, arguments); };
    const dh = ddHit; ddHit = function () { window._lazy.total++; return dh.apply(this, arguments); };
    const ds = ddSub; ddSub = function () { window._lazy.total++; return ds.apply(this, arguments); };
    const dp = drumHitP; drumHitP = function () { window._lazy.total++; return dp.apply(this, arguments); };
    const sr0 = OfflineAudioContext.prototype.startRendering;
    OfflineAudioContext.prototype.startRendering = function () { if (window._lazy.atStart < 0) window._lazy.atStart = window._lazy.total; return sr0.apply(this, arguments); }; });
  await page.click("#svJam"); /* round 10: the as-played take is the JAM door; MIX is the song */
  await page.waitForFunction(() => exporting, undefined, { timeout: 5000 }).catch(() => {});
  await page.waitForFunction(() => !exporting, undefined, { timeout: 180000 });
  await page.waitForTimeout(900);
  const jam = await page.evaluate(() => window._lastBounce);
  if (!jam || jam.src !== "take" || !(jam.youN > 0)) fail("JAM did not bounce the take as played " + JSON.stringify(jam));
  else ok("JAM bounces the take as played (" + jam.n + " events, " + jam.youN + " of them yours)");
  const lazy = await page.evaluate(() => window._lazy);
  if (!(lazy.total > 0) || lazy.atStart < 0) fail("lazy-render probe saw no render (" + JSON.stringify(lazy) + ")");
  else if (lazy.late > 0 && !(lazy.atStart <= lazy.total - lazy.late)) fail("the render instantiated voices past the first window before startRendering (" + lazy.atStart + " of " + lazy.total + ", " + lazy.late + " past the window, take " + lazy.last.toFixed(1) + " s)");
  else if (lazy.late === 0) ok("lazy render: take " + lazy.last.toFixed(1) + " s fits one window — " + lazy.atStart + " of " + lazy.total + " hits standing at startRendering (windowing not exercised by this take)");
  else ok("lazy render: " + lazy.atStart + " of " + lazy.total + " hits standing at startRendering, " + lazy.late + " instantiated at checkpoints (take " + lazy.last.toFixed(1) + " s, windows of " + 4 + " s)");
  const newDls = downloads.slice(dl0);
  const wavD = newDls.find(d => d.suggestedFilename().endsWith(".wav"));
  const midD = newDls.find(d => d.suggestedFilename().endsWith(".mid"));
  if (!wavD || !midD) fail("SAVE downloads missing: " + JSON.stringify(newDls.map(d => d.suggestedFilename())));
  else {
    const os = require("os"), fs = require("fs"), pj = require("path").join;
    const wp = pj(os.tmpdir(), "tr-take.wav"), mp = pj(os.tmpdir(), "tr-take.mid");
    await wavD.saveAs(wp); await midD.saveAs(mp);
    const w = fs.readFileSync(wp), m = fs.readFileSync(mp);
    let peak = 0, sq = 0, ns = 0;
    for (let i = 44; i < Math.min(w.length - 3, 44 + 48000 * 6 * 8); i += 3) {
      let v = (w[i] | (w[i + 1] << 8) | (w[i + 2] << 16)); if (v & 0x800000) v -= 0x1000000;
      const a = Math.abs(v); if (a > peak) peak = a;
      const x = v / 8388607; sq += x * x; ns++;
    }
    const rms = Math.sqrt(sq / Math.max(1, ns));
    const rmsDb = 20 * Math.log10(Math.max(1e-9, rms));
    const crest = 20 * Math.log10(Math.max(1e-9, (peak / 8388607) / Math.max(1e-9, rms)));
    const okWav = w.slice(0, 4).toString() === "RIFF" && w.slice(8, 12).toString() === "WAVE" && w.length > 150000;
    const hasYou = m.includes(Buffer.from("YOU"));
    /* walk events (round 9): a byte scan counted VLQ deltas as note-ons */
    let ons = 0, unmatched = 0; { const ntrk = (m[10] << 8) | m[11]; let o = 14;
      for (let k = 0; k < ntrk && o + 8 <= m.length; k++) { const len = (m[o+4] << 24) | (m[o+5] << 16) | (m[o+6] << 8) | m[o+7];
        let i = o + 8; const end = i + len; let status = 0; const open = {};
        while (i < end) { do {} while (m[i++] & 0x80); let x = m[i];
          if (x === 0xFF) { i += 2; let L = 0; do { L = (L << 7) | (m[i] & 0x7f); } while (m[i++] & 0x80); i += L; continue; }
          if (x === 0xF0 || x === 0xF7) { i++; let L = 0; do { L = (L << 7) | (m[i] & 0x7f); } while (m[i++] & 0x80); i += L; continue; }
          if (x & 0x80) { status = x; i++; } const hi = status & 0xF0, ch = status & 0x0F;
          if (hi === 0xC0 || hi === 0xD0) { i += 1; continue; }
          const n = m[i], v = m[i+1]; i += 2;
          if (hi === 0x90 && v > 0) { ons++; open[ch + ":" + n] = (open[ch + ":" + n] || 0) + 1; }
          else if (hi === 0x80 || (hi === 0x90 && v === 0)) { if (open[ch + ":" + n]) open[ch + ":" + n]--; else unmatched++; } }
        for (const q in open) unmatched += open[q]; o = end; } }
    if (unmatched) fail("score has " + unmatched + " unmatched note-ons/offs (stuck notes)");
    if (!okWav) fail("bounced JAM WAV malformed/short (" + w.length + " bytes)");
    else if (peak < 80000) fail("bounced WAV is near-silent (peak " + peak + " of 8388607)");
    else if (!(rmsDb > -24 && rmsDb < -8)) fail("master loudness off target: RMS " + rmsDb.toFixed(1) + " dBFS");
    else if (!(crest > 4 && crest < 20)) fail("master crest factor off: " + crest.toFixed(1) + " dB");
    else if (m.slice(0, 4).toString() !== "MThd" || !hasYou || ons < 3)
      fail("bounced MIDI bad (MThd:" + m.slice(0, 4) + " YOU:" + hasYou + " ons:" + ons + ")");
    else ok("SAVE bounce mastered: peak " + (peak / 8388607).toFixed(2) + " FS · RMS " + rmsDb.toFixed(1) +
      " dBFS · crest " + crest.toFixed(1) + " dB + MIDI with YOU track (" + ons + " note-ons)");
  }
  const still = await page.evaluate(() => ({ dream: DREAM.on, ldr: LDR.on, take: TAKE.on, evs: TAKE.ev.length }));
  if (still.dream || still.ldr || still.take) fail("the track restarted itself after the render " + JSON.stringify(still));
  else if (still.evs < 5) fail("the render consumed the take (" + still.evs + " events left)");
  else ok("the track stays stopped after the render; the take survives for another door (" + still.evs + " events)");

  /* round-5 save fix: the bounce stays on the face as tap-to-download chips —
     a real gesture beats blocked programmatic downloads on every platform */
  const chips = await page.evaluate(() => {
    const a = [...document.querySelectorAll("#ldrSaveLbl a.dlchip")];
    return { n: a.length, blob: a.every(x => x.href.startsWith("blob:")),
      names: a.map(x => x.getAttribute("download")), out: !!SAVE_OUT };
  });
  if (chips.n !== 2 || !chips.blob || !chips.out) fail("save chips missing " + JSON.stringify(chips));
  else if (!/\.wav$/.test(chips.names[0]) || !/\.mid$/.test(chips.names[1])) fail("save chip names wrong " + JSON.stringify(chips.names));
  else ok("the bounce waits on the face: ⤓ WAV · ⤓ MIDI chips, tap to download");
  const dlChip = downloads.length;
  await page.click("#ldrSaveLbl a.dlchip");
  await page.waitForTimeout(900);
  if (downloads.length <= dlChip) fail("tapping a save chip downloaded nothing");
  else ok("chip tap re-downloads the take (" + downloads[downloads.length - 1].suggestedFilename() + ")");

  /* the duck must survive the bounce's MIX swap-and-restore (surdo cached now;
     the figure engine is quieted so the poll loop isn't starved) */
  const duck2 = await page.evaluate(async () => {
    ldrToggle(false);
    await new Promise(r => setTimeout(r, 350));
    const wired = !!(MIX && MIX.kit && MIX.chord) && drumOut() === MIX.kit.in;
    if (ctx.state !== "running") { try { await ctx.resume(); } catch (_) {} }
    /* the render clock can stall right after the heavy offline bounce — wait
       for it to actually run, or .value reads a frozen 1.0 forever */
    const ctA = ctx.currentTime;
    for (let w = 0; w < 100 && ctx.currentTime - ctA < .05; w++) await new Promise(r => setTimeout(r, 30));
    /* Chromium freezes a SILENT subtree's params — the duck only matters when
       the chords carry signal, so probe with a quiet pad sounding through the
       chord strip (the honest scenario) */
    const pn = ctx.createStereoPanner ? ctx.createStereoPanner() : ctx.createGain();
    pn.connect(MIX.chord.in);
    spawnVoice(PROGRAMS[36], 60, .3, ctx.currentTime + .02, 6, pn);
    await new Promise(r => setTimeout(r, 200));
    /* the poll can miss a ~60ms dip if the main thread hiccups right there —
       the duck itself is deterministic, so give the MEASUREMENT three swings.
       Instrumented: count mixDuck arrivals, and if the wire stays flat try a
       DIRECT param schedule to split "call lost" from "param dead". */
    let duckCalls = 0;
    const origDuck = mixDuck;
    mixDuck = function (a, b) { duckCalls++; return origDuck(a, b); };
    let dipped = 1; const ct0 = ctx.currentTime;
    for (let att = 0; att < 3 && !(dipped < .95); att++) {
      drumHitP("surdo", 1, ctx.currentTime + .10, {});
      const t0 = performance.now();
      while (performance.now() - t0 < 1400) {
        dipped = Math.min(dipped, MIX.chord.duck.gain.value);
        await new Promise(r => setTimeout(r, 8));
      }
    }
    mixDuck = origDuck;
    let directDip = null;
    if (!(dipped < .95)) {
      const g = MIX.chord.duck.gain;
      try { g.setTargetAtTime(.5, ctx.currentTime + .05, .004); g.setTargetAtTime(1, ctx.currentTime + .4, .11); } catch (_) {}
      directDip = 1;
      const t1 = performance.now();
      while (performance.now() - t1 < 900) {
        directDip = Math.min(directDip, g.value);
        await new Promise(r => setTimeout(r, 8));
      }
      try { g.cancelScheduledValues(0); g.setValueAtTime(1, ctx.currentTime); } catch (_) {}
    }
    return { wired, dipped, state: ctx.state, ctAdv: +(ctx.currentTime - ct0).toFixed(2),
      duckCalls, directDip: directDip == null ? undefined : +directDip.toFixed(3),
      mctx: MIX._ctx === ctx, dOn: DREAM.on, lOn: LDR.on };
  });
  if (!duck2.wired) fail("mix rack lost after the bounce restore " + JSON.stringify(duck2));
  else if (!(duck2.dipped < .95) && duck2.ctAdv < 1)
    fail("render clock stalled after the bounce — duck unmeasurable " + JSON.stringify(duck2));
  else if (!(duck2.dipped < .95)) fail("duck dead after the bounce " + JSON.stringify(duck2));
  else ok("mix rack + duck survive the bounce restore (dip " + duck2.dipped.toFixed(2) + ")");

  /* ── DD22 (round 7): a DreamDrummer language on a DreamDrummer kit, live ──
     Force a knock/hyphyK drummer alone (no bass kept, so the 808 line carries
     the low end), verify: buffers bake off the hit path, kit hits land as
     role "dd" through the kit strip, the 808 line logs "dd8", the limiter
     stays inside the round-6 ceiling, and the drums drawer walks the shelf. */
  await page.evaluate(() => {
    dreamStop(true);
    window._keptSnap = BUILD.kept.slice();   /* the full song comes back before KEEP */
    const cat = PROGRAMS.map((p, i) => ({ p, i })).filter(x => x.p.cat === "DRUMS").map(x => x.i);
    const fig16 = Object.keys(LDR_FIG).find(k => LDR_FIG[k].grid === 16);
    window._ddCard = { kind: "drums", name: "Hyphy · the Bay", desc: "probe", fig: fig16,
      comps: [], kit: cat[0], tempo: 100, hum: .18, extraKick: false,
      dsty: "knock", dkit: "hyphyK", seed: 777 };
    const p = composeP([window._ddCard, null, null, null, { kind: "shape", format: "loop" }], null, 5);
    startWith(p, true);
  });
  await page.waitForFunction(() => DREAM.on && DREAM.p && DREAM.p.dsty === "knock" && DREAM.bar >= 2, undefined, undefined, { timeout: 25000 });
  await page.waitForFunction(() => TAKE.ev.filter(e => e.role === "dd").length >= 6, undefined, undefined, { timeout: 40000 })
    .catch(() => {});
  const dd1 = await page.evaluate(async () => {
    /* peak at the kit strip AND at the limiter while the language plays */
    const anK = MIX.kit.an;
    const anL = ctx.createAnalyser(); anL.fftSize = 2048;
    window._chain.lim.connect(anL);
    /* float taps (round 10): the 8-bit analyser saturated at 127/128 = .992 and could
       not tell the limiter's soft ceiling (.999 since the round-9 tube headroom) from a clamp;
       the law is the round-6 one — no flat-tops at the limiter's output */
    const bK = new Float32Array(anK.fftSize), bL = new Float32Array(anL.fftSize);
    let pkK = 0, pkL = 0, hotL = 0, nL = 0;
    const t0 = performance.now();
    while (performance.now() - t0 < 2600) {
      anK.getFloatTimeDomainData(bK); anL.getFloatTimeDomainData(bL);
      for (let i = 0; i < bK.length; i++) { const v = Math.abs(bK[i]); if (v > pkK) pkK = v; }
      for (let i = 0; i < bL.length; i += 2) { const v = Math.abs(bL[i]); if (v > pkL) pkL = v; if (v >= .999) hotL++; nL++; }
      await new Promise(r => setTimeout(r, 12));
    }
    const hotPctL = nL ? 100 * hotL / nL : 0;
    try { window._chain.lim.disconnect(anL); } catch (_) {}
    const dd = TAKE.ev.filter(e => e.role === "dd");
    const d8 = TAKE.ev.filter(e => e.role === "dd8");
    const kitFall = TAKE.ev.filter(e => e.role === "kit");
    const bufs = []; DD_BUFS.forEach((v, k) => bufs.push(k));
    const zones = [...new Set(dd.map(e => e.zone))].sort((a, b) => a - b);
    /* the writer: dd → GM drums ch10, the 808 line → the bass channel */
    const mev = takeToMidiEvents(TAKE.ev);
    const gm = mev.filter(e => e.role === "dd" && e.ch === 9).length;
    const bch = mev.filter(e => e.role === "dd8" && e.ch === 1).length;
    return { on: DREAM.on, bar: DREAM.bar, dd: dd.length, d8: d8.length, kitFall: kitFall.length,
      bufs: bufs.length, zones, pkK: +pkK.toFixed(3), pkL: +pkL.toFixed(3), hotPctL: +hotPctL.toFixed(3),
      gm, bch, muteBass: DREAM.p.muteBass,
      warmDone: Object.keys(DD_WARM).some(k => k.indexOf("hyphyK") === 0 && DD_WARM[k].done) };
  });
  if (!dd1.on) fail("DD probe: dream not running " + JSON.stringify(dd1));
  else if (dd1.dd < 6) fail("DD kit hits not landing (dd " + dd1.dd + ", fallback kit " + dd1.kitFall + ", bufs " + dd1.bufs + ")");
  else if (!dd1.bufs) fail("no DD buffers baked");
  else if (!(dd1.pkK > 0.02)) fail("DD kit silent at the strip (pk " + dd1.pkK + ")");
  else if (!(dd1.pkL <= 1.0) || dd1.hotPctL > 0.1) fail("DD kit flat-tops the limiter (lim pk " + dd1.pkL + ", " + dd1.hotPctL.toFixed(3) + "% at the ceiling)");
  else ok("DD22 live: " + dd1.dd + " dd hits (zones " + dd1.zones.join("/") + ") · " + dd1.bufs +
    " buffers · strip pk " + dd1.pkK + " · lim pk " + dd1.pkL);
  if (!dd1.muteBass) fail("DD probe composed a bass from nothing");
  else if (dd1.d8 < 1) fail("the 808 line never fired with the low end open (d8 " + dd1.d8 + ")");
  else if (!dd1.bch) fail("808 line missing from the bass channel in the writer");
  else ok("the 808 line carries the low end: " + dd1.d8 + " dd8 notes → MIDI ch2 (" + dd1.bch + "), kit → GM ch10 (" + dd1.gm + ")");

  /* the drums drawer spans the shelf: ‹ › walk TRITON kits AND DD kits */
  const drawer = await page.evaluate(() => {
    const kept0 = BUILD.kept[0];
    BUILD.kept[0] = window._ddCard;
    rackRender();
    const shown = (document.querySelector('#rackShelf .rku[data-slot="0"] .rkvoice') || {}).textContent;
    rackCycle(0, 1);
    const next = BUILD.kept[0].dkit;
    for (let i = 0; i < 40 && BUILD.kept[0].dkit; i++) rackCycle(0, 1); /* walk off the shelf end */
    const backToTriton = !BUILD.kept[0].dkit && PROGRAMS[BUILD.kept[0].kit].cat === "DRUMS";
    rackCycle(0, -1);
    const wrapBack = BUILD.kept[0].dkit;
    BUILD.kept[0] = kept0; rackRender();
    return { shown, next, backToTriton, wrapBack };
  });
  if (drawer.shown !== "DD·HYPHYK") fail("rack does not show the DD kit (" + drawer.shown + ")");
  else if (drawer.next !== "boombap") fail("› did not walk the shelf (" + drawer.next + ")");
  else if (!drawer.backToTriton) fail("shelf end did not wrap to the TRITON kits");
  else if (drawer.wrapBack !== "cine") fail("‹ did not wrap back onto the shelf (" + drawer.wrapBack + ")");
  else ok("drums drawer: ‹ › one ring over TRITON kits + DD shelf (DD·HYPHYK → boombap → … → TRITON → ‹ cine)");

  /* ROUND 9 — THE BANK COURT, standing: every program rendered offline at C4
     vel 1 through its own insert; momentary loudness (400 ms) must sit in the
     family, and the hottest chords must meet the master tube's KNEE, not the
     clamp. Slow-attack programs (attack > .8 s) are reported, not judged. */
  const bank = await page.evaluate(async () => {
    if (DREAM.on) dreamStop(true);
    const CEIL = master.gain.value;
    const mom = (f, sr) => { const w = Math.round(.4 * sr); let best = 0, acc = 0;
      for (let i = 0; i < f.length; i++) { acc += f[i] * f[i]; if (i >= w) acc -= f[i - w] * f[i - w]; if (i >= w - 1 && acc > best) best = acc; }
      return 20 * Math.log10(Math.sqrt(best / w) + 1e-9); };
    /* every program over ITS OWN window (renderPlan: slow attacks get their rise),
       capped at 8 s; MOTION FX are effects by design and are reported, not judged */
    const rows = [], slow = [];
    for (let i = 0; i < PROGRAMS.length; i++) { const p = PROGRAMS[i]; if (p.cat === "DRUMS") continue;
      const plan = renderPlan(p); const tot = Math.min(8, plan.total), hold = Math.min(plan.hold, tot - .5);
      const f = await renderNote(JSON.parse(JSON.stringify(p)), 60, 1, { hold, total: tot });
      const m = +mom(f, 48000).toFixed(1);
      if (p.cat === "MOTION") { slow.push(p.id + " " + m); continue; }
      rows.push({ id: p.id, name: p.name, mom: m }); }
    rows.sort((a, b) => a.mom - b.mom);
    const med = rows[Math.floor(rows.length / 2)].mom;
    const flat = [];
    for (const id of ["A071", "A021", "A028", "A038"]) { const prog = JSON.parse(JSON.stringify(PROGRAMS.find(p => p.id === id)));
      const evs = [60, 64, 67].map(n => ({ t: .1, role: "you", prog, note: n, vel: 1, dur: 1.5, tempo: 100 }));
      const buf = await renderPass(evs, "BANK", 0, 100, [], prog); const L = buf.getChannelData(0);
      let pk = 0; for (let i = 0; i < L.length; i++) pk = Math.max(pk, Math.abs(L[i]));
      let n = 0; for (let i = 0; i < L.length; i++) if (Math.abs(L[i]) >= .999 * pk) n++;
      flat.push({ id, pkc: +(pk / CEIL).toFixed(3), flat: +(100 * n / L.length).toFixed(3) }); }
    return { n: rows.length, med, lo: rows.slice(0, 4), hi: rows.slice(-4), slow, flat,
      vox: rows.filter(r => /^A0(05|35|36|85|86)$/.test(r.id)).map(r => r.mom),
      fixed: rows.filter(r => /^A(047|077|119)$/.test(r.id)).map(r => r.id + " " + r.mom) };
  });
  const under = bank.lo.filter(r => r.mom < bank.med - 12), over = bank.hi.filter(r => r.mom > bank.med + 8);
  const hotFlat = bank.flat.filter(f => f.flat > .01 || f.pkc > 1.0);
  if (!(bank.n >= 100)) fail("bank court rendered only " + bank.n + " programs");
  else if (!(bank.med >= -13 && bank.med <= -8)) fail("bank median moved (" + bank.med + " dB momentary at C4 vel 1)");
  else if (under.length) fail("programs more than 12 dB under the bank: " + under.map(r => r.id + " " + r.name + " " + r.mom).join(", "));
  else if (over.length) fail("programs more than 8 dB over the bank: " + over.map(r => r.id + " " + r.name + " " + r.mom).join(", "));
  else if (!bank.vox.every(v => v > bank.med - 6)) fail("VOX family still under the bank (" + bank.vox.join("/") + " vs median " + bank.med + ")");
  else if (hotFlat.length) fail("hot chords still clamp the master tube: " + hotFlat.map(f => f.id + " flat " + f.flat + "% pkc " + f.pkc).join(", "));
  else ok("bank court: " + bank.n + " programs, median " + bank.med + " dB, floor " + bank.lo[0].id + " " + bank.lo[0].mom + " / ceiling " + bank.hi[3].id + " " + bank.hi[3].mom +
    " · VOX " + bank.vox.join("/") + " · re-voiced " + bank.fixed.join(", ") + " · hot triads flat " + bank.flat.map(f => f.flat + "%").join("/") + " (MOTION FX reported, not judged: " + bank.slow.join(" ") + ")");

  /* ROUND 9 — THE BAKE OFF THE MAIN THREAD: a cold DD22 kit warms in a worker;
     the longest main-thread task while it bakes must stay under the
     conductor's 220 ms lookahead (the court measured a 465 ms block) */
  const bake = await page.evaluate(async () => {
    const kit = "cine"; const sr = ctx.sampleRate;
    for (const k of DD_BUFS.keys()) if (k.startsWith(kit + "|")) DD_BUFS.delete(k);
    delete DD_WARM[kit + "|" + sr];
    let longest = 0, tasks = 0; const po = new PerformanceObserver(l => l.getEntries().forEach(en => { tasks++; longest = Math.max(longest, en.duration); }));
    try { po.observe({ entryTypes: ["longtask"] }); } catch (_) { return { unsupported: true }; }
    const t0 = performance.now(); ddWarm(kit);
    while (!(DD_WARM[kit + "|" + sr] && DD_WARM[kit + "|" + sr].done) && performance.now() - t0 < 20000) await new Promise(r => setTimeout(r, 25));
    await new Promise(r => setTimeout(r, 60)); po.disconnect();
    let baked = 0; for (const k of DD_BUFS.keys()) if (k.startsWith(kit + "|")) baked++;
    return { ms: Math.round(performance.now() - t0), baked, longest: Math.round(longest), tasks, worker: !!DD_WK, dead: DD_WK_DEAD };
  });
  if (bake.unsupported) ok("bake probe: longtask observer unsupported here (skipped)");
  else if (!(bake.baked >= 36)) fail("cold kit did not bake in the worker (" + JSON.stringify(bake) + ")");
  else if (!bake.worker || bake.dead) fail("kit bake fell back to the main thread " + JSON.stringify(bake));
  else if (bake.longest > 220) fail("kit bake blocked the main thread " + bake.longest + " ms (lookahead 220)");
  else ok("cold kit (cine) baked off the main thread: " + bake.baked + " buffers in " + bake.ms + " ms, longest main-thread task " + bake.longest + " ms");

  /* THE SESSION DOOR (round 8): stems + mix + score + project.json, one
     reloadable zip — rendered with the track stopped, then loaded BACK */
  const ddSeed = await page.evaluate(() => DREAM.seed);
  const dlDD = downloads.length;
  let zipEntries = null; /* round 9: the take probe reads the same zip */
  await page.click("#ldrSave");
  const ddDoors = await page.evaluate(() => ({ dream: DREAM.on, sv: !!document.getElementById("svSession") }));
  if (ddDoors.dream || !ddDoors.sv) fail("session door not offered on a stopped track " + JSON.stringify(ddDoors));
  await page.click("#svSession");
  await page.waitForFunction(() => exporting, undefined, { timeout: 5000 }).catch(() => {});
  await page.waitForFunction(() => !exporting, undefined, { timeout: 900000 });
  await page.waitForTimeout(900);
  const ddSave = await page.evaluate(() => ({ lbl: document.getElementById("ldrSaveLbl").textContent }));
  const ddZip = downloads.slice(dlDD).find(d => /-session\.zip$/.test(d.suggestedFilename()));
  let zipPath = null;
  if (!ddZip || /FAILED/.test(ddSave.lbl)) fail("SESSION render failed (" + ddSave.lbl + ")");
  else {
    const os3 = require("os"), fs3 = require("fs"), pj3 = require("path").join;
    zipPath = pj3(os3.tmpdir(), "tr-session.zip");
    await ddZip.saveAs(zipPath);
    const buf = fs3.readFileSync(zipPath);
    /* store-only unzip, harness side: EOCD → central directory walk */
    const dv = new DataView(buf.buffer, buf.byteOffset, buf.length);
    let eo = -1; for (let i = buf.length - 22; i >= 0; i--) if (dv.getUint32(i, true) === 0x06054b50) { eo = i; break; }
    const entries = {};
    if (eo >= 0) { const n = dv.getUint16(eo + 10, true); let o = dv.getUint32(eo + 16, true);
      for (let k = 0; k < n; k++) { const csz = dv.getUint32(o + 20, true), nl = dv.getUint16(o + 28, true),
          el = dv.getUint16(o + 30, true), cl = dv.getUint16(o + 32, true), off = dv.getUint32(o + 42, true);
        const nm = buf.slice(o + 46, o + 46 + nl).toString();
        const lnl = dv.getUint16(off + 26, true), lel = dv.getUint16(off + 28, true);
        entries[nm] = buf.slice(off + 30 + lnl + lel, off + 30 + lnl + lel + csz);
        o += 46 + nl + el + cl; } }
    const names = Object.keys(entries);
    zipEntries = entries;
    const stems = names.filter(n => n.startsWith("stems/"));
    const pj = entries["project.json"] ? JSON.parse(entries["project.json"].toString()) : null;
    const wavPk = b => { if (!b || b.slice(0, 4).toString() !== "RIFF") return -1;
      let pk = 0; const at = b.indexOf("data") + 8;
      for (let i = at; i + 2 < b.length; i += 3 * 7) {
        const v = ((b[i + 2] << 16) | (b[i + 1] << 8) | b[i]) << 8 >> 8;
        const a = Math.abs(v / 8388608); if (a > pk) pk = a; } return pk; };
    const mixPk = wavPk(entries["mix.wav"]);
    const stemPks = stems.map(n => wavPk(entries[n]));
    /* the WRITER clamps, so a peak read back from the bytes can never exceed
       full scale — a clip check there is vacuous. The engine reports its
       PRE-clamp peaks; those are the honest numbers. */
    const truePk = await page.evaluate(() => window._mastPk || {});
    const overs = Object.keys(truePk).filter(k => truePk[k] > 0.999);
    if (!entries["mix.wav"] || !entries["take.mid"] || !pj) fail("session zip incomplete: " + names.join(", "));
    else if (stems.length < 2) fail("session zip has no stems (" + names.join(", ") + ")");
    else if (!(mixPk > 0.02)) fail("session mix.wav is silence (pk " + mixPk.toFixed(3) + ")");
    else if (!stemPks.every(p => p > 0.005)) fail("a stem is silent (" + stemPks.map(p => p.toFixed(3)).join("/") + ")");
    else if (overs.length) fail("clipped before the writer clamped it: " + overs.map(k => k + " " + truePk[k].toFixed(3)).join(", "));
    else if (Object.keys(truePk).length < stems.length + 1) fail("engine did not report a peak per rendered file " + JSON.stringify(truePk));
    else if (entries["take.mid"].slice(0, 4).toString() !== "MThd") fail("session take.mid malformed");
    else if (!Array.isArray(pj) || !pj.length || pj[0].seed !== ddSeed) fail("project.json wrong (" + JSON.stringify(pj && pj[0] && pj[0].seed) + " vs " + ddSeed + ")");
    else ok("SESSION zip: " + stems.length + " stems (" + stems.map(s => s.slice(6, -4)).join("/") + ") + mix (pk " +
      mixPk.toFixed(2) + ", true pk " + (truePk["mix.wav"] || 0).toFixed(3) + ", none clipped pre-writer) + score + project.json (seed #" + pj[0].seed + ")");
  }

  /* THE PROJECT COMES BACK: LOAD of a bare project.json (the zip minus its
     take) validates through the preset law and stands the song up PLAYING —
     round 9 gives a zip WITH a take a different law (stopped, doors open),
     probed below */
  let projPath = null;
  if (zipPath && zipEntries && zipEntries["project.json"]) {
    projPath = require("path").join(require("os").tmpdir(), "tr-project.json");
    require("fs").writeFileSync(projPath, zipEntries["project.json"]);
  }
  if (projPath) {
    const pre = await page.evaluate(() => ({ n: PRESETS.length, dream: DREAM.on }));
    await page.setInputFiles("#projFile", projPath);
    await page.waitForFunction(s => DREAM.on && DREAM.seed === s, ddSeed, { timeout: 20000 }).catch(() => {});
    const post = await page.evaluate(() => ({ n: PRESETS.length, on: DREAM.on, seed: DREAM.seed,
      dsty: DREAM.p && DREAM.p.dsty, kept: !!BUILD.kept[0],
      chip: !!document.querySelector("#ldrPresets .pchip4[data-k]"),
      load: !!document.getElementById("ldrLoad") }));
    if (!post.on || post.seed !== ddSeed) fail("loaded project did not stand up (" + JSON.stringify(post) + ")");
    else if (post.n <= pre.n - 1 || !post.chip || !post.load) fail("loaded project not on the ★ rail " + JSON.stringify(post));
    else if (post.dsty !== "knock" || !post.kept) fail("loaded project lost its language/rail (" + JSON.stringify(post) + ")");
    else ok("LOAD: project.json reloads — song #" + post.seed + " (" + post.dsty + ") standing, ★ rail carries it");
    await page.evaluate(() => dreamStop(true));
  }

  /* ROUND 9 — THE TAKE RIDES IN THE ZIP: take.json is the performance in the
     take codec's shape; LOAD brings it back STOPPED under its song's console
     with the doors open, and PLAY regrows the song fresh */
  let addrHash = null;
  if (zipPath && zipEntries) {
    const tj = zipEntries["take.json"] ? JSON.parse(zipEntries["take.json"].toString()) : null;
    const roles = tj ? [...new Set(tj.ev.map(e => e.role))] : [];
    if (!tj || tj.v !== 1 || !(tj.n > 0) || tj.ev.length !== tj.n) fail("session zip carries no take.json (" + JSON.stringify(tj && { v: tj.v, n: tj.n }) + ")");
    else if (!roles.includes("dd") || !roles.includes("mix")) fail("take.json lacks the roles the take had (" + roles.join(",") + ")");
    else if (tj.ev.some(e => e.prog)) fail("take.json carries program objects for bank programs");
    else {
      ok("take.json: " + tj.n + " events, roles " + roles.join("/") + ", bank programs by index");
      /* the wrong zip must not: LOAD the same zip while a DIFFERENT song plays → the take replaces the performance, stopped */
      await page.evaluate(() => { const p = composeP(BUILD.kept, null, 5); if (p) startWith(p, true); });
      await page.waitForFunction(() => DREAM.on && TAKE.ev.length >= 4, undefined, undefined, { timeout: 20000 }).catch(() => {});
      await page.setInputFiles("#projFile", zipPath);
      await page.waitForFunction(() => !DREAM.on && TAKE.ev.length > 0 && !!document.getElementById("svLink"), undefined, undefined, { timeout: 20000 }).catch(() => {});
      const rs = await page.evaluate(() => ({ on: DREAM.on, takeOn: TAKE.on, n: TAKE.ev.length, seed: DREAM.seed,
        staged: !!(DREAM.staged && DREAM.staged._seed === DREAM.seed), pending: !!DREAM.pending,
        doors: ["svMix", "svScore", "svSession", "svLink", "svJam"].filter(id => !!document.getElementById(id)).length,
        chord: DREAM.p && DREAM.p.chord, lcd: (document.getElementById("lcd") || {}).textContent || "",
        progs: TAKE.ev.filter(e => e.prog).every(e => PROGRAMS.indexOf(e.prog) >= 0) }));
      if (rs.on || rs.takeOn || rs.pending) fail("restored take did not stop the transport " + JSON.stringify(rs));
      else if (rs.n !== tj.n || rs.seed !== ddSeed || !rs.staged) fail("take not restored under its song (" + JSON.stringify(rs) + ")");
      else if (rs.doors !== 5) fail("doors not open on the restored take (" + rs.doors + ")");
      else if (!rs.progs) fail("restored events do not reference bank programs by identity");
      else {
        ok("LOAD with take: stopped, " + rs.n + " events back under song #" + rs.seed + ", staged for PLAY, 5 doors open");
        /* the SCORE door bounces the restored performance — instant, no render */
        const dlS = downloads.length;
        await page.click("#svScore"); await page.waitForTimeout(700);
        const mid = downloads.slice(dlS).find(d => d.suggestedFilename().endsWith(".mid"));
        if (!mid) fail("SCORE door silent on a restored take"); else ok("SCORE door bounces the restored take (" + mid.suggestedFilename() + ")");
        /* PLAY regrows the staged song: fresh take, same seed, staged consumed */
        const genBefore = await page.evaluate(() => TAKE.ev.length);
        await page.click("#dreamPlay");
        await page.waitForFunction(s => DREAM.on && DREAM.seed === s, ddSeed, { timeout: 20000 }).catch(() => {});
        const pl = await page.evaluate(g => ({ on: DREAM.on, seed: DREAM.seed, staged: !!DREAM.staged, takeOn: TAKE.on, fresh: TAKE.ev.length < g && TAKE.t0 > 0,
          doors: !!document.getElementById("svMix"), dsty: DREAM.p && DREAM.p.dsty }), genBefore);
        if (!pl.on || pl.seed !== ddSeed || pl.staged || !pl.takeOn || !pl.fresh || pl.doors) fail("PLAY did not regrow the staged song " + JSON.stringify(pl));
        else ok("PLAY regrows the staged song #" + pl.seed + " (" + pl.dsty + "): fresh take, doors cleared");
        await page.waitForFunction(() => TAKE.ev.length >= 6, undefined, undefined, { timeout: 20000 }).catch(() => {});
        /* THE LINK DOOR: the song's address into the URL bar */
        await page.click("#ldrSave");
        await page.waitForFunction(() => !!document.getElementById("svLink"), undefined, undefined, { timeout: 5000 }).catch(() => {});
        await page.click("#svLink");
        await page.waitForFunction(() => /^#(p|j)=/.test(location.hash), undefined, undefined, { timeout: 5000 }).catch(() => {});
        const lk = await page.evaluate(() => ({ hash: location.hash, lbl: (document.getElementById("ldrSaveLbl") || {}).textContent || "",
          staged: !!DREAM.staged, on: DREAM.on }));
        if (!/^#p=[A-Za-z0-9_-]+$/.test(lk.hash)) fail("LINK door wrote no address (" + lk.hash.slice(0, 24) + ")");
        else if (lk.hash.length > 2000) fail("address is not compact (" + lk.hash.length + " chars)");
        else if (lk.staged || lk.on) fail("LINK restaged its own song " + JSON.stringify({ staged: lk.staged, on: lk.on }));
        else { addrHash = lk.hash; ok("LINK: address in the URL bar, " + lk.hash.length + " chars (" + lk.lbl.slice(0, 40) + ")"); }
      }
    }
  }
  /* ROUND 9 — THE TOUCH LAW AT PHONE SCALE: the ★ rail, ⤒ LOAD and the door
     chips must be real tap targets on a 390 px phone (the face's own law:
     ≥45 px; the court measured 7-8 px), and the strip must not run into the
     rack shelf below */
  {
    const pp = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const pErr = []; pp.on("pageerror", e => pErr.push(e.message));
    await pp.goto("file://" + path); await pp.waitForTimeout(500);
    await pp.evaluate(() => { quickBoot(); const kd = candDrums(mulberry(3)), kb = candBass(mulberry(4)), kc = candChords(mulberry(5), kb), kl = candLead(mulberry(6));
      BUILD.kept = [kd, kb, kc, kl, FORMATS[0]]; BUILD.stage = 5; builderRender(); rackRender();
      const p = composeP(BUILD.kept, null, 5); startWith(p, true); });
    await pp.waitForFunction(() => TAKE.ev.length > 6, undefined, undefined, { timeout: 15000 }).catch(() => {});
    await pp.evaluate(() => { PRESETS = [1, 2, 3].map(i => ({ name: "kept song number " + i, seed: i, p: {} })); presetRender(); saveMenu(); });
    await pp.waitForTimeout(250);
    const ph = await pp.evaluate(() => {
      const box = e => { const r = e.getBoundingClientRect(); return { w: +r.width.toFixed(1), h: +r.height.toFixed(1), top: +r.top.toFixed(0), bottom: +r.bottom.toFixed(0), right: +r.right.toFixed(0) }; };
      const chips = [...document.querySelectorAll("#ldrPresets .pchip4, #ldrSaveLbl .dlchip")].map(box);
      const face = box(document.getElementById("ldru")), scaleBox = box(document.getElementById("ldrScale")), shelf = box(document.getElementById("rackScale"));
      const pads = [...document.querySelectorAll("#dreamPlay,#dreamDice,#ldrSave,#ldrKeep")].map(box);
      return { phone: document.body.classList.contains("phone"), n: chips.length, minH: Math.min(...chips.map(c => c.h)), minW: Math.min(...chips.map(c => c.w)),
        maxRight: Math.max(...chips.map(c => c.right)), stripBottom: Math.max(...chips.map(c => c.bottom)), boxBottom: scaleBox.bottom, shelfTop: shelf.top,
        padMin: Math.min(...pads.map(p => p.h)), faceW: face.w, vw: document.documentElement.clientWidth };
    });
    if (!ph.phone || ph.n < 6) fail("phone strip missing " + JSON.stringify(ph));
    else if (!(ph.minH >= 44 && ph.minW >= 44)) fail("phone tap targets under the law: min " + ph.minW + "×" + ph.minH + " px");
    else if (ph.maxRight > ph.vw + 1) fail("phone strip overflows the viewport (" + ph.maxRight + " > " + ph.vw + ")");
    else if (ph.stripBottom > ph.boxBottom + 1 || ph.stripBottom > ph.shelfTop - 4) fail("phone strip runs into the rack shelf " + JSON.stringify({ strip: ph.stripBottom, box: ph.boxBottom, shelf: ph.shelfTop }));
    else if (!(ph.padMin >= 45)) fail("phone pads under the law (" + ph.padMin + ")");
    else ok("phone scale (390 px): " + ph.n + " chips ≥ " + ph.minW + "×" + ph.minH + " px in a strip under the face, pads " + ph.padMin + " px, nothing overlaps the shelf");
    if (pErr.length) fail("phone page errors: " + pErr.join(" | "));
    await pp.close();
  }

  /* THE ADDRESS REGROWS THE SONG in a fresh page: staged on the rail, PLAY starts it; hostiles say so and load nothing */
  if (addrHash) {
    const p2 = await browser.newPage({ viewport: { width: 1100, height: 900 } });
    const p2errs = []; p2.on("pageerror", e => p2errs.push(e.message));
    await p2.goto("file://" + path + addrHash);
    await p2.waitForFunction(() => !!DREAM.staged, undefined, undefined, { timeout: 8000 }).catch(() => {});
    const st = await p2.evaluate(() => ({ staged: !!DREAM.staged, seed: DREAM.staged && DREAM.staged._seed, on: DREAM.on,
      chips: document.querySelectorAll("#ldrPresets .pchip4[data-k]").length, kept: !!BUILD.kept[0],
      lbl: (document.getElementById("ldrSaveLbl") || {}).textContent || "", powered: state.powered }));
    if (!st.staged || st.seed !== ddSeed) fail("address did not stage its song " + JSON.stringify(st));
    else if (st.on || st.powered) fail("address started audio without a gesture " + JSON.stringify(st));
    else if (!st.chips || !st.kept || !/ADDRESS LOADED/.test(st.lbl)) fail("address not on the rail / not announced " + JSON.stringify(st));
    else {
      await p2.click("#dreamPlay");
      await p2.waitForFunction(s => DREAM.on && DREAM.seed === s, ddSeed, { timeout: 20000 }).catch(() => {});
      const go = await p2.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed, dsty: DREAM.p && DREAM.p.dsty, staged: !!DREAM.staged }));
      if (!go.on || go.seed !== ddSeed || go.staged) fail("PLAY did not start the addressed song " + JSON.stringify(go));
      else ok("ADDRESS: a fresh page regrows song #" + go.seed + " (" + go.dsty + ") on PLAY — the rail carries it, nothing played before the gesture");
      /* the regrow is CONTENT, not a seed: two replays of the same song (after
         the first run has baked its kit) must log the same events */
      const snap = async () => { await p2.waitForFunction(() => TAKE.ev.length >= 24, undefined, undefined, { timeout: 30000 }).catch(() => {});
        return p2.evaluate(() => TAKE.ev.slice(0, 24).map(e => [+e.t.toFixed(3), e.role, e.note != null ? e.note : (e.zone != null ? e.zone : e.name || ""), +(e.vel || 0).toFixed(3), e.prog ? PROGRAMS.indexOf(e.prog) : -1].join("|"))); };
      await snap(); await p2.evaluate(() => dreamStop(true));
      await p2.click("#ldrPresets .pchip4[data-k]"); const r2 = await snap(); await p2.evaluate(() => dreamStop(true));
      await p2.click("#ldrPresets .pchip4[data-k]"); const r3 = await snap(); await p2.evaluate(() => dreamStop(true));
      const diff = r2.filter((x, i) => x !== r3[i]).length;
      if (r2.length < 24 || diff) fail("the address does not regrow the same song twice (" + diff + " of " + r2.length + " events differ)");
      else ok("regrow is content-exact: two replays of #" + go.seed + " log the same first " + r2.length + " events (t, role, note, vel, program)");
    }
    if (p2errs.length) fail("address page errors: " + p2errs.join(" | "));
    await p2.close();
    /* hostiles */
    const b64u = s => Buffer.from(s).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    for (const [nm, h] of [["garbage", "#p=AAAAAAAA"], ["prototype figure", "#j=" + b64u(JSON.stringify([{ name: "x", seed: 1, p: { fig: "constructor" } }]))]]) {
      const p3 = await browser.newPage(); const e3 = []; p3.on("pageerror", e => e3.push(e.message));
      await p3.goto("file://" + path + h); await p3.waitForTimeout(600);
      const r3 = await p3.evaluate(() => ({ staged: !!DREAM.staged, n: PRESETS.length, pwned: !!window.__pwned,
        lbl: (document.getElementById("ldrSaveLbl") || {}).textContent || "" }));
      if (r3.staged || r3.n || r3.pwned || e3.length) fail("hostile address (" + nm + ") got through " + JSON.stringify(r3) + " " + e3.join("|"));
      else if (!/DID NOT LOAD/.test(r3.lbl)) fail("hostile address (" + nm + ") refused silently");
      await p3.close();
    }
    ok("hostile addresses refused aloud (garbage, prototype figure), nothing staged, no page errors");
    /* a VALID song wearing hostile strings must reach every sink ESCAPED — the
       old gate used an invalid entry, so the name never reached a sink (a gate
       that cannot fail, round 9's correctness lens) */
    const hostileEntry = await page.evaluate(() => { const kd = candDrums(mulberry(21)), kb = candBass(mulberry(22)), kc = candChords(mulberry(23), kb), kl = candLead(mulberry(24));
      const p = composeP([kd, kb, kc, kl, FORMATS[0]], null, 5); delete p._seed; p.verb = 50;
      p.name = "<img src=x onerror=window.__pwned=1>"; p.progName = "<b onmouseover=window.__pwned=2>x</b>";
      return { name: "<img src=x onerror=window.__pwned=3>", seed: 9191, p }; });
    { const px = await browser.newPage({ viewport: { width: 1100, height: 900 } }); const ex = []; px.on("pageerror", e => ex.push(e.message));
      await px.goto("file://" + path + "#j=" + b64u(JSON.stringify([hostileEntry])));
      await px.waitForFunction(() => !!DREAM.staged, undefined, undefined, { timeout: 8000 }).catch(() => {});
      await px.click("#dreamPlay");
      await px.waitForFunction(() => DREAM.on && TAKE.ev.length > 3, undefined, undefined, { timeout: 20000 }).catch(() => {});
      await px.evaluate(() => { document.body.classList.add("engineOpen"); render(); });
      const hx = await px.evaluate(() => ({ staged: DREAM.seed === 9191, pwned: window.__pwned || 0,
        imgs: document.querySelectorAll("img, b[onmouseover]").length,
        chip: (document.querySelector("#ldrPresets .pchip4[data-k]") || {}).textContent || "",
        keep: keepSerialize(PRESETS), lcd: (document.getElementById("lcd") || {}).innerHTML || "",
        lbl: (document.getElementById("ldrSaveLbl") || {}).innerHTML || "", th: (document.getElementById("thProgName") || {}).innerHTML || "" }));
      await px.evaluate(() => dreamStop(true));
      const rawIn = [hx.lcd, hx.lbl, hx.th].some(h => /<img\s|<b onmouseover/.test(h)) || /<img src=x onerror/.test(hx.keep);
      if (!hx.staged) fail("hostile-string song did not stand (" + JSON.stringify({ seed: hx.staged }) + ")");
      else if (hx.pwned || hx.imgs || rawIn) fail("hostile strings reached a sink raw " + JSON.stringify({ pwned: hx.pwned, imgs: hx.imgs, rawIn }));
      else if (hx.chip.indexOf("<img") < 0) fail("rail chip does not show the escaped name (" + hx.chip + ")");
      else ok("hostile strings in a VALID song: name/progName/p.name escaped at the rail, the LCD, the save label, the theory bar and the KEEP copy — nothing fired");
      if (ex.length) fail("hostile-string page errors: " + ex.join(" | "));
      await px.close(); }
  }

  /* hand the stage back to the full song before KEEP, then stop the dream —
     the baseline enters KEEP with the conductor off (powerOff never clears
     DREAM.on, and a live flag makes setProgram skip arp defaults later) */
  await page.evaluate(() => { if (window._keptSnap) BUILD.kept = window._keptSnap.slice();
    builderRender(); rackRender();
    const p = composeP(BUILD.kept, null, 5); if (p) startWith(p, true); });
  await page.waitForFunction(() => DREAM.on && !DREAM.pending && DREAM.bar >= 1, undefined, undefined, { timeout: 20000 });
  await page.waitForFunction(() => TAKE.ev.length >= 10, undefined, undefined, { timeout: 30000 }).catch(() => {});
  await page.evaluate(() => dreamStop(true));
  await page.waitForTimeout(200);

  /* KEEP: the file saves a copy of ITSELF carrying the dream — then that copy
     must boot clean and play its preset */
  const kitOpts = await page.evaluate(() => document.getElementById("ldrKit").options.length);
  const dlK = downloads.length;
  await page.click("#ldrKeep");
  await page.waitForTimeout(1200);
  const keepD = downloads.slice(dlK).find(d => d.suggestedFilename().endsWith(".html"));
  if (!keepD) fail("KEEP produced no file");
  else {
    const os2 = require("os"), fs2 = require("fs"), pj2 = require("path").join;
    const kp = pj2(os2.tmpdir(), "tr-kept.html");
    await keepD.saveAs(kp);
    const src = fs2.readFileSync(kp, "utf8");
    const hasPreset = /"seed":\s*\d+/.test(src) && src.indexOf('id="tritonPresets"') >= 0;
    const hasRings = src.indexOf("═══ end rings ═══") >= 0;
    if (!hasPreset || !hasRings) fail("kept copy incomplete (preset " + hasPreset + ", rings " + hasRings + ")");
    else {
      const page2 = await browser.newPage({ viewport: { width: 1100, height: 900 } });
      const errs2 = [];
      page2.on("console", m => { if (m.type() === "error") errs2.push(m.text()); });
      page2.on("pageerror", e => errs2.push("pageerror: " + e.message));
      await page2.goto("file://" + kp);
      await page2.waitForTimeout(800);
      const boot2 = await page2.evaluate(() => ({
        presets: typeof PRESETS !== "undefined" ? PRESETS.length : -1,
        chips: document.querySelectorAll("#ldrPresets .pchip4[data-k]").length,
        loadDoor: !!document.getElementById("ldrLoad"),
        kitOpts: document.getElementById("ldrKit").options.length,
        tabOn: !!document.querySelector(".tab.on") && !!document.querySelector(".pane.on"),
        powered: state.powered, lcdOff: document.getElementById("lcd").classList.contains("off") }));
      const real2 = errs2.filter(e => !/Web MIDI|requestMIDIAccess|favicon/.test(e));
      /* round 8: the rail may carry MORE than the kept song (a loaded
         project rides along) plus the ⤒ LOAD door — count law, not 1 */
      if (boot2.presets < 1 || boot2.chips !== boot2.presets || !boot2.loadDoor) fail("kept copy lost its preset " + JSON.stringify(boot2));
      else if (boot2.kitOpts !== kitOpts) fail("kept copy doubled its kit options (" + boot2.kitOpts + " vs " + kitOpts + ")");
      else if (!boot2.tabOn) fail("kept copy boots with no active tab/pane — the lower UI is blank");
      else if (boot2.powered || !boot2.lcdOff) fail("kept copy boots powered-on " + JSON.stringify(boot2));
      else if (real2.length) fail("kept copy console: " + real2.slice(0, 3).join(" | "));
      else {
        /* KEEP pushes the current song LAST — replay THAT chip (the rail
           may also carry a loaded project up front, round 8) */
        await page2.evaluate(() => { const cs = document.querySelectorAll("#ldrPresets .pchip4[data-k]");
          cs[cs.length - 1].click(); });
        await page2.waitForFunction(() => DREAM.on && DREAM.bar >= 6, undefined, { timeout: 30000 });
        const play2 = await page2.evaluate(() => ({ on: DREAM.on, seed: DREAM.seed,
          name: DREAM.p && DREAM.p.name, hook: !!DREAM.hook,
          elibs: !!(DREAM.p && DREAM.p.elibs && DREAM.p.elibs.length),
          rail: document.querySelectorAll("#traitRail .trSlot.done").length,
          stage: BUILD.stage }));
        const kept = await page.evaluate(() => PRESETS[PRESETS.length - 1] && PRESETS[PRESETS.length - 1].seed);
        /* a library song carries an EMBELLISH bag instead of a drawn hook */
        if (!play2.on || play2.seed !== kept || (!play2.hook && !play2.elibs))
          fail("kept preset replays wrong world (" + play2.seed + " vs " + kept + ", hook " + play2.hook + ", elibs " + play2.elibs + ")");
        else if (play2.rail !== 5 || play2.stage !== 5)
          fail("kept copy's avatar rail not rebuilt (" + play2.rail + " slots, stage " + play2.stage + ")");
        else ok("KEEP: the file rewrote itself — copy boots clean, chip replays seed #" +
          play2.seed + " (" + play2.name + "), avatar rail rebuilt · remixable");
      }
      await page2.close();
    }
  }

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
