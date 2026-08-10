/**
 * OVERLAY REACHABILITY SWEEP — the BACKPORT rider for bug a596d8c9.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * The Tools menu was cut off on a phone because its height came from 100vh (the
 * LARGE viewport) instead of the glass. Two other overlays ship on these pages
 * and could hold the same class of bug, so they are swept the same way rather
 * than reasoned about: the WISHING WELL (.av-modal/.av-sheet, on every page of
 * every trade) and the FEEDBACK drop-in (.fb-wrap/.fb-sheet, on /commons/ and
 * Collage Studio).
 *
 * The test is the one that matters: can you still reach the SEND button — the
 * control the whole demand loop depends on?
 *
 * ONE SUBTLETY, AND IT DECIDES WHAT EACH CASE MAY ASSERT. Faking innerHeight at a
 * large viewport reproduces iOS ONLY for boxes sized by a vh unit, because vh is
 * what iOS freezes to the large viewport. A box sized by `position:fixed; inset:0`
 * is sized by the LAYOUT viewport, which iOS shrinks with the toolbars — so for
 * those the faithful test is simply a small viewport, and running them under the
 * override reports a failure that cannot happen on a real phone. Measured: the
 * well's send button read "18.8px below the glass" under the override and is in
 * fact clear, because .av-modal carries no vh at all. Each case therefore declares
 * how it is BOUND, and is tested that way.
 *
 *   node tools/toolkit-gates/overlay-reachability.mjs [base-url]
 */
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const BASE = process.argv[2] || 'file://' + ROOT;

const CASES = [
  // bound:'layout' -> sized by position:fixed inset:0; a small viewport IS the iOS case
  { page: 'av/consumables.html', overlay: 'the wishing well', bound: 'layout', open: '.av-req-btn', sheet: '.av-sheet', send: '.av-send' },
  { page: 'av/index.html', overlay: 'the wishing well', bound: 'layout', open: '.av-req-btn', sheet: '.av-sheet', send: '.av-send' },
  { page: 'plumbing/tm-tag.html', overlay: 'the wishing well', bound: 'layout', open: '.av-req-btn', sheet: '.av-sheet', send: '.av-send' },
  { page: 'gc/index.html', overlay: 'the wishing well', bound: 'layout', open: '.av-req-btn', sheet: '.av-sheet', send: '.av-send' },
  // bound:'vh' -> .fb-sheet is max-height:min(92vh,100%); needs the large-viewport override
  { page: 'commons/index.html', overlay: 'the feedback drop-in', bound: 'vh', openFn: "window.Feedback && Feedback.open('bug')", sheet: '.fb-sheet', send: '.fb-send' },
  // Collage Studio is a built bundle whose modules will not load over file://, so
  // this case only runs when a real base URL is given (i.e. against the deploy).
  { page: 'collage/', overlay: 'the feedback drop-in', bound: 'vh', liveOnly: true, openFn: "window.Feedback && Feedback.open('bug')", sheet: '.fb-sheet', send: '.fb-send' },
];
// vh-bound: large viewport (what 100vh sees) paired with the glass (what the eye sees).
// layout-bound: the glass IS the viewport, which is what iOS does to fixed overlays.
const VH_VPS = [{ w: 390, h: 794, glass: 664 }, { w: 320, h: 580, glass: 480 }];
const LAYOUT_VPS = [{ w: 390, h: 664 }, { w: 320, h: 480 }];

const b = await chromium.launch();
const fails = [];
let checked = 0;

const LOCAL = BASE.startsWith('file://');
for (const c of CASES) {
  if (c.liveOnly && LOCAL) { console.log(`  skip  ${c.page} — needs a served base URL (built bundle)`); continue; }
  for (const vp of (c.bound === 'vh' ? VH_VPS : LAYOUT_VPS)) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h }, isMobile: true, hasTouch: true });
    if (vp.glass) await ctx.addInitScript(g => { Object.defineProperty(window, 'innerHeight', { get: () => g, configurable: true }); }, vp.glass);
    const p = await ctx.newPage();
    await p.goto(BASE + c.page, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(200);
    if (c.openFn) {
      const ok = await p.evaluate(fn => { try { return !!eval(fn) || true; } catch (e) { return false; } }, c.openFn);
      if (!ok) { fails.push(`${c.page}: could not open ${c.overlay}`); await ctx.close(); continue; }
    } else {
      const opener = await p.$(c.open);
      if (!opener) { fails.push(`${c.page}: opener ${c.open} not found`); await ctx.close(); continue; }
      await opener.click();
    }
    await p.waitForTimeout(250);

    const r = await p.evaluate(sel => {
      const glass = window.innerHeight;
      const sheet = document.querySelector(sel.sheet);
      if (!sheet || !sheet.offsetParent) return { missing: true };
      // scroll whatever actually scrolls — the sheet or its overlay wrapper
      const scroller = sheet.scrollHeight > sheet.clientHeight + 1 ? sheet : sheet.parentElement;
      scroller.scrollTop = scroller.scrollHeight;
      const send = document.querySelector(sel.send);
      const sb = send ? send.getBoundingClientRect() : null;
      const de = document.documentElement;
      return {
        glass,
        sendFound: !!send,
        sendBottom: sb ? +sb.bottom.toFixed(1) : null,
        sendTop: sb ? +sb.top.toFixed(1) : null,
        over: sb ? +(sb.bottom - glass).toFixed(1) : null,
        hOverflow: de.scrollWidth - de.clientWidth,
      };
    }, c);

    checked++;
    const where = `${c.page} @${vp.w}x${vp.h}${vp.glass ? ` glass ${vp.glass} [vh-sim]` : ' [layout]'} — ${c.overlay}`;
    if (r.missing) { fails.push(`${where}: overlay did not open`); }
    else if (!r.sendFound) { fails.push(`${where}: send control not found`); }
    else {
      const bad = [];
      if (r.over > 0) bad.push(`send button ${r.over}px below the glass — UNREACHABLE`);
      if (r.sendTop < 0) bad.push(`send button ${-r.sendTop}px above the glass`);
      if (r.hOverflow > 0) bad.push(`${r.hOverflow}px horizontal overflow`);
      if (bad.length) fails.push(`${where}: ${bad.join('; ')}`);
      else console.log(`  PASS  ${where}: send button clear by ${Math.abs(r.over)}px`);
    }
    await ctx.close();
  }
}

await b.close();
console.log(`\noverlay-reachability: ${checked} check(s) — base ${BASE}`);
if (fails.length) { console.log(`\n${fails.length} FAILURE(S):`); fails.forEach(f => console.log('  FAIL ' + f)); process.exit(1); }
console.log('PASS — every overlay\'s send control stays on the glass, each tested the way it is actually bound.');
