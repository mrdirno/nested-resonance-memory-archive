/**
 * THE MOBILE-WATERTIGHT GATE
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * Encodes the operator's standing ship gate (2026-08-04): "must be mobile
 * friendly always — don't make anything that's gonna clip or alter if zoomed out
 * on phone." av/AV_SOCIETY.md §MOBILE-WATERTIGHT states it as a rule; a rule
 * that lives only in a document is a rule the twentieth page forgets. This is
 * the rule as an ASSERTION, run over every toolkit page derived from disk, so a
 * trade shipped next month is covered the day it lands with no edit here.
 *
 * WHAT IT MEASURES, and why each one is here rather than eyeballed:
 *  · HORIZONTAL OVERFLOW — scrollWidth vs clientWidth on the documentElement.
 *    This is the defect the operator named. A screenshot cannot show it: the
 *    page looks fine and the content is simply off to the right of the glass.
 *    Reported WITH THE CULPRIT — the widest element that starts inside the
 *    viewport and ends outside it — because "something overflows by 14px" costs
 *    an hour and "the .hgrid at line N overflows by 14px" costs a minute.
 *  · TAP TARGETS — every control a thumb has to hit, measured at >= 44px on its
 *    short side. A control that is 38px tall passes every visual review ever
 *    held and fails in a glove (§SCARS 2026-08-05, which found exactly that on
 *    every row-log control in a SHIPPED page).
 *  · THE STICKY BAR vs THE ACTION UNDER IT — the fixed bottom bar carries Copy,
 *    and a page whose LAST control cannot be scrolled out from under it is a page
 *    whose product cannot be reached. Measured SCROLLED TO THE BOTTOM and only
 *    there: a control passing under the bar mid-scroll is what a fixed bar is
 *    for, and flagging it would be the gate crying wolf on correct behaviour.
 *    At the bottom of the page there is nowhere left to scroll, so anything the
 *    bar still covers is covered for good — hit-tested with elementFromPoint,
 *    because what the thumb actually hits is the only question that matters.
 *  · ZOOMED OUT / TEXT BUMPED — the operator's exact words were "don't make
 *    anything that's gonna clip or alter if zoomed out on phone". Pinch-zoom does
 *    not change the layout viewport, so resizing cannot simulate it and neither
 *    can faking visualViewport.scale — both measure nothing new, and a check that
 *    measures nothing new is worse than no check because it reports green. What
 *    ACTUALLY breaks in that family is a layout pinned in fixed px meeting text
 *    it did not budget for, so that is what is reproduced: the root font size
 *    bumped the way the OS accessibility setting bumps it, then overflow
 *    re-asserted. Plus the viewport meta itself — a page carrying
 *    user-scalable=no is a page that cannot be zoomed at all, which is the same
 *    complaint one layer up.
 *  · THE STATES A TAP OPENS — see REVEALS below. A page loaded and left alone is
 *    not the page a man uses, and half of what these tools render only exists
 *    after a tap. Everything above is measured again in each revealed state.
 *
 *   node tools/toolkit-gates/mobile-watertight.mjs [base-url] [--only=slug/page.html]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

/* The widths the operator named, and they are not arbitrary: 320 is the
 * smallest phone still in service, 360 is the median Android, 390 is the
 * current iPhone, 430 is the largest. A page that is watertight at all four is
 * watertight. */
const WIDTHS = [320, 360, 390, 430];
const MIN_TAP = 44;

const DIRS = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js'))
  .map(d => d.name)
  .concat(existsSync(ROOT + 'commons') ? ['commons'] : [])
  .sort();

const PAGES = only ? [only] : DIRS.flatMap(dir =>
  readdirSync(ROOT + dir).filter(f => f.endsWith('.html')).sort().map(f => `${dir}/${f}`));

/* ── REVEALED STATES ─────────────────────────────────────────────────────
 * A page loaded and left alone is not the page a man uses. Half of what these
 * tools render only exists after a tap, and this gate measured none of it —
 * which is how a fixed bar grew to a ninth of the glass on seven trades and
 * every measurement here still reported green (§SCARS 2026-08-11: "the standing
 * gate never reaches [the omit list], because the omit list only exists after a
 * pick"). That was found by screenshotting production AFTER the ship. This is
 * the second time the class has escaped, so it stops being a thing to remember.
 *
 * Each entry names a state, matches the pages it applies to, and runs INSIDE
 * the page to get there. The page is re-loaded per state, because pass B leaves
 * a bumped root font behind and a state measured on top of it is measuring two
 * things at once. A page that matches nothing is measured exactly as before —
 * one load, no cost.
 */
const REVEALS = [
  {
    name: 'custom path, every omitted line ticked',
    match: /\/write-up\.html$/,
    /* The custom path is the graceful failure of search and it carries the
       widest control on the page: a tick row whose label and artefact badge sit
       on one line. Ticking them ALL is the worst case, and the worst case is
       the only one worth measuring. */
    run: () => {
      const btn = [...document.querySelectorAll('button')].find(b => /Not in the list/i.test(b.textContent));
      if (!btn) return 'no "not in the list" control';
      btn.click();
      const inp = document.querySelector('#app input[type=text]');
      if (!inp) return 'custom path rendered no name field';
      inp.value = 'Confined space entry and rescue-plan sign-off';
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelectorAll('#app input[type=checkbox]').forEach(cb => {
        if (cb.disabled || cb.checked) return;
        cb.click();
      });
      return null;
    },
  },
];

/* Runs INSIDE the page. Returns findings, never throws — a gate that dies on one
 * page tells you nothing about the other thirty. */
const MEASURE = (MIN_TAP) => {
  const out = { overflow: null, taps: [], soft: [], covered: [], grew: [], clipped: [] };
  const de = document.documentElement;
  const vw = de.clientWidth;

  if (de.scrollWidth > vw) {
    // Name the culprit: the element that starts inside the glass and ends outside
    // it, deepest in the tree (the innermost one is the one you edit).
    let worst = null;
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      if (r.left >= vw) return;                    // entirely off-screen, not the cause
      const over = Math.round(r.right - vw);
      if (over <= 0) return;
      const depth = (function d(e, n) { while (e.parentElement) { e = e.parentElement; n++; } return n; })(el, 0);
      if (!worst || over > worst.over || (over === worst.over && depth > worst.depth)) {
        worst = {
          over, depth,
          sel: el.tagName.toLowerCase()
            + (el.id ? '#' + el.id : '')
            + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
          text: (el.textContent || '').trim().slice(0, 40),
        };
      }
    });
    out.overflow = { scrollWidth: de.scrollWidth, clientWidth: vw, by: de.scrollWidth - vw, culprit: worst };
  }

  const CONTROLS = 'button, a[href], input:not([type=hidden]), select, textarea, summary, [role=button], label.hot, label.row';
  const seen = new Set();
  document.querySelectorAll(CONTROLS).forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;                 // not on screen
    if (el.closest('[hidden]') || getComputedStyle(el).visibility === 'hidden') return;
    /* WCAG 2.5.8 exempts a target that sits INLINE IN A SENTENCE, and it is right
     * to: a link inside a paragraph cannot be 44px without wrecking the prose it
     * lives in, and nobody taps it blind. Without this the gate reports every
     * body-copy link on every page and becomes noise — and a noisy gate is one
     * that gets skipped, which is worse than not having it. */
    if (el.tagName === 'A' && getComputedStyle(el).display === 'inline'
        && el.closest('p, li, .credit, .lede, .warn')) return;
    // A checkbox inside a >=44px label is reachable by the label; judge the label.
    const lab = el.closest('label');
    const box = (lab && lab.getBoundingClientRect().height >= r.height) ? lab.getBoundingClientRect() : r;
    const short = Math.min(box.width, box.height);
    if (short >= MIN_TAP - 0.5) return;
    const sel = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '')
      + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : '');
    const key = sel + '|' + Math.round(short);
    if (seen.has(key)) return;
    seen.add(key);
    const hit = { sel, short: Math.round(short * 10) / 10, text: (el.textContent || el.value || '').trim().slice(0, 30) };
    /* TWO CLASSES, and collapsing them would make the gate unusable. A BUTTON,
     * link or summary is hit ONCE, blind, often with a glove — under 44px it is
     * a miss and that is a hard fail. A TEXT FIELD is aimed at deliberately, is
     * usually inside a labelled block much taller than itself, and every one of
     * the toolkit's ~37.6px fields comes from one shared rule; failing them
     * would fail every page ever shipped here, which is a gate nobody can run
     * and therefore a gate that stops being run. Reported, not fatal. */
    const soft = /^(input|select|textarea)$/.test(el.tagName.toLowerCase())
      && !/^(checkbox|radio|button|submit)$/.test(el.type || '');
    (soft ? out.soft : out.taps).push(hit);
  });

  /* THE BOTTOM BAR vs WHAT IS UNDER IT. Hit-test the real document at each
   * control's own centre: whatever elementFromPoint returns is what the thumb
   * hits. If that is the fixed bar and the control is not inside it, the control
   * is unreachable — which is the whole product on a page whose output is Copy. */
  const bar = document.querySelector('.bar, .rl-bar, [data-fixed-bar]');
  if (bar && getComputedStyle(bar).position === 'fixed') {
    /* THE BAR MUST NOT GROW. Everything else here asks whether the bar covers
     * something; nothing asked how TALL it had got. On every write-up page the
     * word count was a flex child with a 0 basis sitting beside two nowrap
     * buttons totalling 332px, so it was handed 0px, broke into FIVE stacked
     * lines and pushed the fixed bar from 62px to 97px — a ninth of an 844px
     * phone, gone, permanently, on all seven trades. None of the three
     * measurements above sees it: the page does not overflow, no tap target
     * shrank, and the bar still cleared the last control (it just cleared it
     * from 35px lower down).
     *
     * The assertion is threshold-free on purpose: a LABEL in the action bar may
     * not be taller than the tallest BUTTON in it. Buttons carry the 44px floor
     * and set the bar's honest height; anything taller than them has wrapped,
     * and wrapping is the defect. */
    const kids = [...bar.children];
    const btns = kids.filter(k => k.matches('button, a[href], [role=button]') || k.querySelector('button'));
    const tallestBtn = btns.reduce((m, b) => Math.max(m, b.getBoundingClientRect().height), 0);
    if (tallestBtn > 0) {
      kids.forEach(k => {
        if (btns.includes(k)) return;
        const h = k.getBoundingClientRect().height;
        if (h > tallestBtn + 1) {
          out.grew.push({
            sel: k.tagName.toLowerCase() + (k.className && typeof k.className === 'string' ? '.' + k.className.trim().split(/\s+/).join('.') : ''),
            h: Math.round(h), btn: Math.round(tallestBtn),
            text: (k.textContent || '').trim().slice(0, 40),
          });
        }
      });
    }

    /* THE FIXED BAR'S OWN CHILDREN vs THE GLASS. Added 2026-08-14 after the
       primary "Copy instructions" button on every trade's write-up page was
       found running 27px off the right edge at 320px — with this gate reporting
       PASS, because all three checks above are structurally blind to it:
       a fixed bar never widens documentElement.scrollWidth, so the OVERFLOW
       check cannot see it; the button was 44px tall, so the TAP check cannot see
       it; and elementFromPoint at the bar still returned the button, because 27px
       off the edge still leaves 161px on it, so the COVERAGE check cannot see it
       either. Three correct measurements, one shared blind spot. The bar carries
       the product of every page in this toolkit, so a control clipped there is
       the whole page clipped. */
    [...bar.children].forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      const over = Math.round(r.right - vw);
      if (over > 0 || r.left < -0.5) {
        out.clipped.push({
          sel: el.tagName.toLowerCase() + (el.id ? '#' + el.id : el.className ? '.' + String(el.className).split(' ')[0] : ''),
          over: over > 0 ? over : Math.round(-r.left),
          side: over > 0 ? 'right' : 'left',
          text: (el.textContent || el.value || '').trim().slice(0, 30),
        });
      }
    });

    // Scrolled to the very bottom there is nowhere left to go, so whatever the
    // bar still covers HERE is covered permanently.
    window.scrollTo(0, document.documentElement.scrollHeight);
    const atBottom = Math.abs(window.scrollY + window.innerHeight - document.documentElement.scrollHeight) < 2;
    if (atBottom) {
      document.querySelectorAll(CONTROLS).forEach(el => {
        if (bar.contains(el)) return;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        const cy = r.top + r.height / 2, cx = r.left + r.width / 2;
        if (cy < 0 || cy > window.innerHeight) return;            // still above the glass
        const hit = document.elementFromPoint(cx, cy);
        if (hit && bar.contains(hit)) {
          out.covered.push({
            sel: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
            text: (el.textContent || el.value || '').trim().slice(0, 30),
          });
        }
      });
    }
    window.scrollTo(0, 0);
  }

  /* A page that forbids zoom fails the operator's rule at the source. */
  const mv = document.querySelector('meta[name=viewport]');
  const c = mv ? (mv.getAttribute('content') || '') : '';
  if (!mv) out.viewport = 'no <meta name=viewport> at all';
  else if (/user-scalable\s*=\s*(no|0)/i.test(c)) out.viewport = 'user-scalable=no — the page cannot be zoomed';
  else if (/maximum-scale\s*=\s*(1(\.0+)?|0?\.\d+)\b/i.test(c)) out.viewport = 'maximum-scale caps zoom at 1×';
  else if (!/width\s*=\s*device-width/i.test(c)) out.viewport = 'viewport is not width=device-width: ' + c;
  return out;
};

const browser = await chromium.launch();
let failures = 0, checked = 0, softTotal = 0;

for (const page of PAGES) {
  const url = `${BASE}/${page}`;
  const bad = [];
  const soft = new Set();

  /* The default state always runs; a page that has a hidden state runs again in
     it. `null` reveal = load and leave alone, exactly what this gate always did. */
  const STATES = [{ name: '', run: null }]
    .concat(REVEALS.filter(r => r.match.test('/' + page)).map(r => ({ name: r.name, run: r.run })));

  for (const width of WIDTHS) {
    const ctx = await browser.newContext({
      viewport: { width, height: 780 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
    });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(String(e)));

    for (const state of STATES) {
      /* Re-loaded per state on purpose: pass B leaves the root font bumped, and
         a revealed state measured on top of that is measuring two things at once
         and can only report the wrong one. */
      try {
        await p.goto(url, { waitUntil: 'load', timeout: 30000 });
      } catch (e) {
        bad.push(`${width}px — could not load: ${e.message.split('\n')[0]}`);
        break;
      }
      await p.waitForTimeout(350);            // the shared runtime paints the nav
      const where = state.name ? ` · ${state.name}` : '';
      if (state.run) {
        let why = null;
        try { why = await p.evaluate(state.run); }
        catch (e) { why = e.message.split('\n')[0]; }
        if (why) { bad.push(`${width}px${where} — COULD NOT REACH THE STATE: ${why}`); continue; }
        await p.waitForTimeout(250);
      }

      /* PASS A at the OS default, PASS B with the root text bumped the way the
       * accessibility setting bumps it. B re-asserts overflow only — tap targets
       * only grow with the text, and the bottom bar was already judged in A. */
      for (const bump of [null, '20px']) {
        if (bump) {
          await p.addStyleTag({ content: `html{font-size:${bump} !important}` });
          await p.waitForTimeout(120);
        }
        const r = await p.evaluate(MEASURE, MIN_TAP);
        const tag = `${width}px${where}${bump ? ` · text bumped to ${bump}` : ''}`;
        if (r.overflow) {
          const c = r.overflow.culprit;
          bad.push(`${tag} — HORIZONTAL OVERFLOW by ${r.overflow.by}px (scrollWidth ${r.overflow.scrollWidth} > clientWidth ${r.overflow.clientWidth})`
            + (c ? `\n              culprit: ${c.sel} runs ${c.over}px past the glass  "${c.text}"` : ''));
        }
        if (bump) continue;
        if (r.viewport) bad.push(`${tag} — VIEWPORT: ${r.viewport}`);
        r.taps.forEach(t => bad.push(`${tag} — TAP TARGET ${t.short}px < ${MIN_TAP}px: ${t.sel}  "${t.text}"`));
        r.covered.forEach(c => bad.push(`${tag} — UNREACHABLE, the fixed bar covers it at the bottom of the page: ${c.sel}  "${c.text}"`));
        r.clipped.forEach(c => bad.push(`${tag} — CLIPPED IN THE FIXED BAR: ${c.sel} runs ${c.over}px past the ${c.side} edge of the glass  "${c.text}"`));
        r.grew.forEach(g => bad.push(`${tag} — the fixed bar GREW: ${g.sel} is ${g.h}px tall beside ${g.btn}px buttons, so it wrapped and the bar ate the extra. "${g.text}"`));
        r.soft.forEach(t => soft.add(`${t.sel} ${t.short}px  "${t.text}"`));
      }
    }
    if (errs.length) bad.push(`${width}px — pageerror: ${errs.join(' | ')}`);
    await ctx.close();
  }

  checked++;
  softTotal += soft.size;
  if (bad.length) {
    failures++;
    console.log(`\nFAIL  ${page}`);
    // One line per DISTINCT finding — the same overflow at four widths is one bug.
    [...new Set(bad)].forEach(b => console.log('      ' + b));
  } else {
    console.log(`PASS  ${page}${soft.size ? `   (${soft.size} field(s) under ${MIN_TAP}px — reported, not fatal)` : ''}`);
  }
  if (process.env.SHOW_SOFT && soft.size) [...soft].forEach(s => console.log('      soft: ' + s));
}

await browser.close();
console.log(`\n${checked} page(s) checked at ${WIDTHS.join('/')}px, default and bumped text — ${failures} failing`
  + (softTotal ? `, ${softTotal} soft field-height report(s) (SHOW_SOFT=1 to list)` : ''));
process.exit(failures ? 1 : 0);
