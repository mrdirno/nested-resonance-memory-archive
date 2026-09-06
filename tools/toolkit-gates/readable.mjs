/**
 * THE READABLE GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS, and it is not a hypothetical: a wish arrived on 2026-09-06
 * that said, in full, *"the background is light and the text is light — need to
 * create a scar or a ring for this issue."* It was cast at a page this lane does
 * not push, so it could not be served where it was aimed. But the class it names
 * had never been measured HERE, on 187 pages across 17 trades, by any of the 37
 * gates that ran before every ship. The first sweep found 505 unreadable text
 * elements. The worst was 1.74:1 — white on the AV yellow — on a shipped page's
 * primary Copy button, which is the control the whole product exists to reach.
 *
 * A screenshot cannot catch this and neither can a review: low contrast reads as
 * "clean" to anyone who already knows what the word says. It only fails in the
 * one place this toolkit is used — a dirty screen in the sun, held at arm's
 * length, by someone who has never seen the page before. FIELD-COOL says
 * "high-contrast, built for a dirty screen in bad light". This is that sentence
 * as an assertion.
 *
 * WHAT IT MEASURES
 *  · RENDERED TEXT — every visible element that owns a text node, its computed
 *    colour composited over its EFFECTIVE background (walking ancestors through
 *    transparent backgrounds, compositing alpha and inherited opacity the way the
 *    compositor does), against the WCAG 2.1 relative-luminance ratio. 4.5:1 for
 *    body text, 3:1 for large text (>=24px, or >=18.66px at weight >=700) — the
 *    same split WCAG uses, because a 30px headline at 3.2:1 genuinely is legible
 *    and failing it would be the gate crying wolf.
 *  · PLACEHOLDERS — measured through ::placeholder, separately, because a
 *    placeholder IS the instruction on half these forms ("what the job is, the
 *    way they say it") and it is the single most common home of grey-on-white.
 *  · THE STATES A TAP OPENS — a page loaded and left alone is not the page a man
 *    uses. The 1.74:1 button above only exists after a tap on some pages; the
 *    on-state of a segmented control does not exist at load at all. This gate
 *    would have passed the worst defect in the program if it only measured load.
 *  · THE PALETTE ITSELF, with no browser — every trade.js is read off disk and
 *    its `accent` is checked against the steel bar it prints on and its
 *    `accentDeep` against the zinc footer it prints on. This is the half that
 *    covers a trade shipped next month BEFORE anybody renders it: a bad accent
 *    is caught at the config, which is the only place it can be fixed once.
 *
 * WHAT IT DOES NOT CLAIM. Text over a background IMAGE or gradient has no single
 * background colour, so a ratio against the resolved chain would be a number that
 * looks like a measurement and is not one. Those are counted and named as
 * UNMEASURED rather than passed — an honest gap beats a green tick.
 *
 *   node tools/toolkit-gates/readable.mjs [base-url] [--only=slug/page.html]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy:
 * the deployed bundle has been wrong while the source was right (§SCARS), so the
 * only run that proves a ship is the one against the artifact.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync, readFileSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

/* WCAG 2.1 AA. Not a house number — the one threshold with twenty years of
   evidence under it, and the one an accessibility complaint will be measured
   against if this toolkit ever gets one. */
const AA_TEXT = 4.5;
const AA_LARGE = 3.0;

/* ONE WIDTH, NOT FOUR. Contrast does not change with the viewport — colour is
   colour. mobile-watertight sweeps four widths because LAYOUT changes; sweeping
   them here would quadruple the runtime of a gate that has to run before every
   ship and measure the identical numbers four times. 390 is the current iPhone,
   so it is the width the revealed states are reached at. */
const WIDTH = 390;

const DIRS = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js'))
  .map(d => d.name)
  .concat(existsSync(ROOT + 'commons') ? ['commons'] : [])
  .sort();

/* --only takes a comma-separated list, not one page: a colour defect is a CLASS,
   and checking a fix means re-driving the handful of pages that carried it, not
   one of them or all 187. */
const PAGES = only ? only.split(',').map(s => s.trim()).filter(Boolean) : DIRS.flatMap(dir =>
  readdirSync(ROOT + dir).filter(f => f.endsWith('.html')).sort().map(f => `${dir}/${f}`));

/* Sampled per trade, for the one state every page shares — see the same reasoning
   in mobile-watertight.mjs. The dropdown is injected by the shared runtime and is
   the same on every page of a trade; a hub and one tool page per trade is the
   informative sample, and sweeping it would double the runtime for no new colour. */
const MENU_SAMPLE = new Set(DIRS.flatMap(dir => {
  const files = readdirSync(ROOT + dir).filter(f => f.endsWith('.html')).sort();
  const tool = files.find(f => f !== 'index.html');
  return [`${dir}/index.html`, tool && `${dir}/${tool}`].filter(Boolean);
}));
const IS_MENU_SAMPLE = { test: s => MENU_SAMPLE.has(s.replace(/^\//, '')) };
const EVERY_PAGE = { test: () => true };

/* ── REVEALED STATES ─────────────────────────────────────────────────────
 * Generic on purpose. A roster of page names rots the moment a page ships
 * (§SCARS — the row-log regex that missed low-voltage/device-checkout, 25 of 26).
 * Each reveal here finds its own targets in the DOM, so a tool built next month
 * is measured in its revealed states on the day it lands with no edit here.
 */
const REVEALS = [
  {
    name: 'the Tools menu open',
    match: IS_MENU_SAMPLE,
    run: () => {
      const btn = document.querySelector('.av-menu > button');
      if (!btn) return null;
      btn.click();
      return document.querySelector('.av-menu[open] .av-drop') ? null : 'the Tools button did not open the menu';
    },
  },
  {
    name: 'every toggle turned on',
    match: EVERY_PAGE,
    /* THE STATE THAT CARRIES THE WORST COLOUR IN THE PROGRAM. A segmented
       control's chosen option is the one element that gets the trade's accent as
       a BACKGROUND, and a light accent under light text is the exact defect the
       wish named. At load, no option may be on at all. Every toggle is turned on
       rather than a sample: they are cheap, they are the point, and which one is
       on changes nothing else on the page.

       Buttons are only clicked when they already have a sibling that carries the
       house `on` class — that is what makes a row of buttons a SEGMENTED CONTROL
       rather than a row of actions, and clicking actions blind is how a gate
       opens a confirm dialog and hangs the run. */
    run: () => {
      const groups = new Set();
      document.querySelectorAll('button.on, .seg button, [role="tab"]').forEach(b => groups.add(b.parentElement));
      let n = 0;
      groups.forEach(g => {
        if (!g) return;
        const kids = [...g.children].filter(k => k.tagName === 'BUTTON' || k.getAttribute?.('role') === 'tab');
        if (kids.length < 2) return;
        kids.forEach(k => { if (!k.disabled) { try { k.click(); n++; } catch (e) { /* a control that will not take a click is not this gate's finding */ } } });
      });
      return null;                    // a page with no segmented control reveals nothing, and that is fine
    },
  },
  {
    name: 'the wish panel open',
    match: EVERY_PAGE,
    /* SHIPPED ON EVERY SURFACE (§FEEDBACK IS BUILT IN) AND CARRYING ITS OWN
       PALETTE — shared/feedback.js declares --fb-muted, --fb-paper and friends
       independently of the page's tokens, so it is the one place in the program
       where fixing the shared palette fixes nothing. It is also the form a person
       uses to report that they cannot read something, which would be a poor place
       to be unreadable. */
    run: () => {
      const t = [...document.querySelectorAll('a,button')].find(e => /wish it better|wish|feedback/i.test(e.textContent || ''));
      if (!t) return null;
      t.click();
      return null;
    },
  },
];

/* ── THE MEASUREMENT, RUN IN THE PAGE ──────────────────────────────────── */
const MEASURE = ([needText, needLarge]) => {
  const srgb = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = ([r, g, b]) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
  const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1]; return (hi + 0.05) / (lo + 0.05); };
  const parse = s => {
    const m = String(s || '').match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  };
  /* fg over bg. The compositor's own arithmetic; anything else is a guess. */
  const over = (fg, bg) => (fg[3] >= 1 ? fg.slice(0, 3) : [0, 1, 2].map(i => fg[i] * fg[3] + bg[i] * (1 - fg[3])));

  /* THE EFFECTIVE BACKGROUND. Walks up through every transparent ancestor,
     composites semi-transparent ones onto what is behind them, and reports
     whether an IMAGE was in the chain — because a gradient has no one colour and
     saying otherwise would be inventing a measurement. Ends at white, which is
     what a browser paints behind an unpainted root. */
  const bgOf = el => {
    let n = el, img = false;
    while (n && n.nodeType === 1) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') img = true;
      const c = parse(cs.backgroundColor);
      if (c && c[3] > 0) {
        if (c[3] >= 1) return { col: c.slice(0, 3), img };
        const up = bgOf(n.parentElement || document.documentElement);
        return { col: over(c, up.col), img: img || up.img };
      }
      n = n.parentElement;
    }
    return { col: [255, 255, 255], img };
  };

  /* Inherited opacity multiplies down the tree and the compositor applies it to
     the finished element, so the text a person actually sees is the colour at
     the product of every opacity above it. Reading only the element's own
     opacity is how a .5-on-.5 label measures as fully opaque. */
  const effOpacity = el => { let o = 1, n = el; while (n && n.nodeType === 1) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return o; };

  const near = el => {
    const bits = [el.tagName.toLowerCase()];
    if (el.id) bits.push('#' + el.id);
    if (typeof el.className === 'string' && el.className.trim()) bits.push('.' + el.className.trim().split(/\s+/).slice(0, 2).join('.'));
    return bits.join('');
  };

  const out = { fails: [], unmeasured: 0, seen: 0 };
  const consider = (el, kind, colorStr, sample) => {
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const op = effOpacity(el);
    if (op < 0.05) return;                       // not rendered in any meaningful sense
    /* WCAG 1.4.3 exempts an INACTIVE component by name, and it is right to: a
       disabled Send at .45 opacity is supposed to read as unavailable, and a gate
       that failed it would be demanding the greyed-out state stop looking greyed
       out. Exempted here rather than silently passed, so nobody has to wonder
       later whether it was measured. */
    if (el.closest('[disabled],[aria-disabled="true"],fieldset:disabled')) return;
    const fg = parse(colorStr);
    if (!fg) return;
    const bg = bgOf(el);
    out.seen++;
    if (bg.img) { out.unmeasured++; return; }    // named, never silently passed
    const eff = over([fg[0], fg[1], fg[2], fg[3] * op], bg.col);
    const cr = ratio(eff, bg.col);
    const size = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = size >= 24 || (bold && size >= 18.66);
    const need = large ? needLarge : needText;
    if (cr + 0.005 < need) {
      out.fails.push({
        kind, cr: Math.round(cr * 100) / 100, need, size: Math.round(size * 10) / 10, bold,
        sel: near(el),
        fg: `rgb(${eff.map(Math.round).join(',')})`,
        bg: `rgb(${bg.col.map(Math.round).join(',')})`,
        text: String(sample || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 56),
      });
    }
  };

  for (const el of document.querySelectorAll('body *')) {
    const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.replace(/\s+/g, ' ').trim().length > 1);
    if (own.length) consider(el, 'text', getComputedStyle(el).color, own.map(n => n.textContent).join(' '));
    if ((el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') && el.placeholder) {
      const ph = getComputedStyle(el, '::placeholder').color;
      if (ph) consider(el, 'placeholder', ph, el.placeholder);
    }
  }
  return out;
};

/* ── THE PALETTE, READ OFF DISK ─────────────────────────────────────────
 * The half of this gate that needs no browser and no page. Every trade declares
 * `accent` (which prints as text on the steel bar) and `accentDeep` (which prints
 * as text on the zinc footer). Checking the CONFIG catches a bad trade the day it
 * is written rather than the day somebody renders it — and it is the only check
 * that a trade with no pages yet can still fail.
 */
const STEEL = '#242A31', ZINC = '#D7DAD3', PAPER = '#FBFBF8';
const hex = h => { const s = h.replace('#', ''); return [0, 2, 4].map(i => parseInt(s.slice(i, i + 2), 16)); };
const srgb = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
const lumOf = ([r, g, b]) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
const cr = (a, b) => { const l1 = lumOf(hex(a)), l2 = lumOf(hex(b)); const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1]; return (hi + 0.05) / (lo + 0.05); };

function paletteReport() {
  const bad = [];
  let n = 0;
  for (const dir of DIRS) {
    const f = ROOT + dir + '/trade.js';
    if (!existsSync(f)) continue;
    const src = readFileSync(f, 'utf8');
    const grab = k => (src.match(new RegExp(k + '\\s*:\\s*["\']([#0-9A-Fa-f]{4,9})["\']')) || [])[1];
    const accent = grab('accent'), deep = grab('accentDeep');
    if (!accent) continue;
    n++;
    const a = cr(accent, STEEL);
    if (a < AA_TEXT) bad.push(`${dir}: accent ${accent} on the steel bar is ${a.toFixed(2)}:1, under ${AA_TEXT} — the eyebrow and the brand print in it`);
    if (deep) {
      const d = cr(deep, ZINC);
      if (d < AA_TEXT) bad.push(`${dir}: accentDeep ${deep} on the zinc footer is ${d.toFixed(2)}:1, under ${AA_TEXT} — every "Wish it better" link prints in it`);
      const p = cr(deep, PAPER);
      if (p < AA_TEXT) bad.push(`${dir}: accentDeep ${deep} on paper is ${p.toFixed(2)}:1, under ${AA_TEXT}`);
    }
    /* WHITE ON THE ACCENT IS NEVER RIGHT IN THIS PROGRAM and the numbers are not
       close: measured across all seventeen trades, white on a flag-coloured
       surface runs 1.15:1 to 3.21:1 and INK runs 5.66:1 to 15.82:1. Asserted here
       so the next person who reaches for color:#fff on a flag button is told why
       before they ship it, not after. */
    if (cr('#FFFFFF', accent) >= AA_TEXT) bad.push(`${dir}: accent ${accent} is dark enough for white text — the shared rules assume ink on flag; check the flag-backed controls by hand`);

    /* THE SAME ACCENT, SPELLED OUT IN THREE PLACES. trade.js owns it, but the
       shared runtime's TRADES roster (which paints the "other kits" list on every
       page of every trade) and commons' trade roster (the identity dot) each keep
       their own copy. Fixing plumbing's accent in C3716 meant editing all three by
       hand, and nothing would have said a word if one had been missed — the trade
       would simply have shown two different identities in two places, one of them
       the colour that was measured and one of them not. A colour nobody checked is
       exactly what this gate exists for, so the copies are made to agree here. */
    for (const [file, re] of [
      ['shared/toolkit.js', new RegExp(`slug:\\s*["']${dir}["'][^}]*?accent:\\s*["'](#[0-9A-Fa-f]{6})["']`)],
      ['commons/commons.js', new RegExp(`slug:\\s*["']${dir}["'][^}]*?color:\\s*["'](#[0-9A-Fa-f]{6})["']`)],
    ]) {
      if (!existsSync(ROOT + file)) continue;
      const m = readFileSync(ROOT + file, 'utf8').match(re);
      if (m && m[1].toUpperCase() !== accent.toUpperCase()) {
        bad.push(`${dir}: ${file} says the accent is ${m[1]}, ${dir}/trade.js says ${accent} — one of them is painting a colour nobody measured`);
      }
    }
  }
  return { n, bad };
}

/* ── RUN ────────────────────────────────────────────────────────────────── */
console.log(`THE READABLE GATE — ${PAGES.length} page(s) at ${WIDTH}px, ${AA_TEXT}:1 body / ${AA_LARGE}:1 large\nbase: ${BASE}\n`);

const pal = paletteReport();
if (pal.bad.length) {
  console.log(`FAIL  the palette (${pal.n} trade config(s) read off disk)`);
  pal.bad.forEach(b => console.log('      ' + b));
} else {
  console.log(`PASS  the palette — ${pal.n} trade config(s), accent on steel and accentDeep on zinc both clear ${AA_TEXT}:1`);
}

const browser = await chromium.launch();
let checked = 0, failures = 0, unmeasured = 0, samples = 0;
const classes = new Map();

for (const page of PAGES) {
  const url = `${BASE}/${page}`;
  const bad = new Set();
  const ctx = await browser.newContext({ viewport: { width: WIDTH, height: 800 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.addInitScript(() => { navigator.share = () => Promise.resolve(); });
  const STATES = [{ name: '', run: null }].concat(REVEALS.filter(r => r.match.test('/' + page)).map(r => ({ name: r.name, run: r.run })));

  for (const state of STATES) {
    /* Re-loaded per state: a revealed state stacked on the previous one measures
       two things at once and can only report the wrong one. */
    try { await p.goto(url, { waitUntil: 'load', timeout: 30000 }); }
    catch (e) { bad.add(`could not load: ${e.message.split('\n')[0]}`); break; }
    await p.waitForTimeout(320);                 // the shared runtime paints the nav and the footer
    if (state.run) {
      let why = null;
      try { why = await p.evaluate(state.run); } catch (e) { why = e.message.split('\n')[0]; }
      if (why) { bad.add(`COULD NOT REACH THE STATE (${state.name}): ${why}`); continue; }
      await p.waitForTimeout(220);
    }
    let r;
    try { r = await p.evaluate(MEASURE, [AA_TEXT, AA_LARGE]); }
    catch (e) { bad.add(`measurement failed${state.name ? ` (${state.name})` : ''}: ${e.message.split('\n')[0]}`); continue; }
    unmeasured += r.unmeasured;
    samples += r.seen;
    const where = state.name ? ` · ${state.name}` : '';
    for (const f of r.fails) {
      bad.add(`${f.cr}:1 (needs ${f.need}) ${f.kind === 'placeholder' ? 'PLACEHOLDER ' : ''}${f.sel} at ${f.size}px${f.bold ? ' bold' : ''}${where}\n              ${f.fg} on ${f.bg}   "${f.text}"`);
      const k = `${f.sel}|${f.fg}|${f.bg}`;
      if (!classes.has(k)) classes.set(k, { ...f, pages: new Set() });
      classes.get(k).pages.add(page);
    }
  }
  await ctx.close();

  checked++;
  if (bad.size) { failures++; console.log(`\nFAIL  ${page}`); [...bad].forEach(b => console.log('      ' + b)); }
  else console.log(`PASS  ${page}`);
}
await browser.close();

if (classes.size) {
  console.log(`\n── ${classes.size} DISTINCT CLASS(ES), worst first — fix the class, not the page ──`);
  [...classes.values()].sort((a, b) => a.cr - b.cr).forEach(c =>
    console.log(`${String(c.cr).padStart(6)}:1  ${c.sel}  ${c.fg} on ${c.bg}  ×${c.pages.size} page(s)   "${c.text}"`));
}
console.log(`\n${checked} page(s) checked, ${samples} text sample(s) measured — ${failures} failing`
  + (unmeasured ? `, ${unmeasured} over a background image and NOT measured (see the header)` : '')
  + (pal.bad.length ? `; the palette FAILS on ${pal.bad.length} config point(s)` : ''));
process.exit(failures || pal.bad.length ? 1 : 0);
