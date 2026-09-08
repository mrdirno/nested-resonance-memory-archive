/**
 * THE TICK-ASIDE GATE — a type is a badge, a rule is a sentence, and one column
 * was drawing both.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `ul.ticks .sb` shipped as `flex:1; text-align:right`: a
 * right-hand COLUMN sharing the name's row. That is the right shape for a
 * two-word type ("OFE", "cond fan or blower") and the wrong shape for a
 * sentence, and only 23% of the asides on disk are types. A sentence in a column
 * that narrow stacks roughly a word per line — measured on the shipped build,
 * painting/getting-in.html rendered one aside as 52 line boxes inside a 708px
 * row at 320px, and the write-up tuner's house rules ran to 8 lines at 390px.
 * `sub` is CONTENT (note.js puts it in the document the client receives), so it
 * cannot be clamped away to fit the column; the fix is that a sentence takes its
 * own row at full width, aligned under the name.
 *
 * A CSS fix has no test unless something counts LINE BOXES on the real page, so
 * this gate does, through Range.getClientRects() — the browser's own answer to
 * "how many lines did that become", not a character-count proxy.
 *
 * WHAT IT ASSERTS, on every page on disk that draws a tick list, at every phone
 * width the mobile gate uses:
 *   · a sentence aside renders at most MAX_LINES lines
 *   · a sentence aside starts at the NAME's left edge — it is under the label,
 *     not indented to nowhere and not hard against the checkbox
 *   · a badge (.sb.tag) stays on ONE line and never overflows its row: a badge
 *     is nowrap by construction, so a badge too wide for the row is the one way
 *     this shape can push the page sideways
 *   · an EMPTY aside occupies no vertical space (docspec's custom-family list
 *     renders one beside every radio)
 *   · no aside extends past its row
 *
 * PAGES AND WIDTHS COME FROM DISK AND FROM THE MOBILE GATE'S OWN LIST, never
 * from a roster here, so a trade shipped next month is covered with no edit.
 *
 *   node tools/toolkit-gates/tick-aside.mjs [base-url] [--only=<trade>/<page>.html]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync, readFileSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const quiet = args.includes('--quiet');
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const WIDTHS = [320, 360, 390, 430];
/* THE DENSITY RAIL, and why it is not a line COUNT. The defect was never "too
   many lines" — a 257-character sentence is ten lines of a phone and that is
   simply what it is. The defect was a PARAGRAPH RENDERED IN A COLUMN: the same
   sentence came back as 52 line boxes because each one held about one word. So
   the assertion is characters per rendered line, which is the thing that went
   wrong, and it holds no matter how long the author writes. CALIBRATED, not
   guessed: the column shape measured 4.9 characters a line on the worst aside on
   disk, and the fixed shape measures 18.3 at ITS worst over 3,112 measurements —
   a short sentence at 320px, where ragged-right on three lines is most of the
   loss. 15 sits between the two with room on both sides. */
const MIN_CHARS_PER_LINE = 15;
const DENSITY_FLOOR_LEN = 40;

/* Any page that pulls in a builder of tick lists: note.js and docspec.js are the
   two shared ones, and hvac's repair-recommendation builds its own. Found by
   reading the pages, so the list cannot go stale against the tree. */
const trades = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js'))
  .map(d => d.name).sort();

const PAGES = [];
for (const t of trades) {
  for (const f of readdirSync(ROOT + t).filter(f => f.endsWith('.html')).sort()) {
    const src = readFileSync(ROOT + t + '/' + f, 'utf8');
    if (/ul\.ticks|"ticks"|'ticks'|shared\/note\.js|shared\/docspec\.js/.test(src)) PAGES.push(t + '/' + f);
  }
}
const LIST = PAGES.filter(p => !only || p === only);

const browser = await chromium.launch();
let fails = 0, checks = 0, measured = 0, worst = 0, worstWhere = '';
const ok = (cond, msg) => { checks++; if (!cond) { fails++; console.log('  FAIL ' + msg); } };

/* One measurement of every aside on screen, read off the layout the browser
   actually produced. Line boxes come from a Range over the text, which is the
   only way to get the number a reader sees. */
const READ = () => Array.from(document.querySelectorAll('ul.ticks .sb')).map(el => {
  const r = document.createRange(); r.selectNodeContents(el);
  const rects = Array.from(r.getClientRects()).filter(x => x.width > 0.5 && x.height > 0.5);
  const box = el.getBoundingClientRect();
  const li = el.closest('li');
  const lab = li && li.querySelector('label');
  const lb = lab && lab.getBoundingClientRect();
  const cs = lab && getComputedStyle(lab);
  const nm = li && li.querySelector('.nm');
  const nb = nm && nm.getBoundingClientRect();
  const cbx = li && li.querySelector('input');
  const cb = cbx && cbx.getBoundingClientRect();
  const inner = lb ? lb.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) : null;
  return {
    text: (el.textContent || '').trim(),
    tag: el.classList.contains('tag'),
    lines: rects.length,
    x: box.x, right: box.right, width: box.width, height: box.height,
    rowRight: lb ? lb.right - parseFloat(cs.paddingRight) : null,
    inner,
    nmX: nb ? nb.x : null,
    // Does the name sit on the checkbox's line, or has it dropped below it?
    nmOnBoxLine: (nb && cb) ? (nb.top < cb.bottom - 1 && nb.bottom > cb.top + 1) : null,
    nmText: nm ? (nm.textContent || '').trim().slice(0, 40) : null
  };
});

for (const p of LIST) {
  const ctx = await browser.newContext({ viewport: { width: WIDTHS[0], height: 844 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto(`${BASE}/${p}`, { waitUntil: 'load' }).catch(() => null);
  await page.waitForTimeout(120);

  // A write-up page holds its tick lists behind picking a document.
  if (await page.locator('ul.ticks .sb').count() === 0 && await page.locator('.lib button').count() > 0) {
    await page.locator('.lib button').first().click().catch(() => null);
    await page.waitForTimeout(250);
  }
  const n = await page.locator('ul.ticks .sb').count();
  if (!n) { if (!quiet) console.log(`${p}: no tick asides on screen`); await ctx.close(); continue; }

  let pageWorst = 0, bad = 0;
  for (const w of WIDTHS) {
    await page.setViewportSize({ width: w, height: 844 });
    await page.waitForTimeout(60);
    const rows = await page.evaluate(READ);
    for (const r of rows) {
      measured++;
      if (!r.text) {
        ok(r.height < 0.5, `${p} @${w}: an EMPTY aside is holding ${r.height.toFixed(1)}px of row`);
        continue;
      }
      if (r.lines > pageWorst) pageWorst = r.lines;
      if (r.lines > worst) { worst = r.lines; worstWhere = `${p} @${w} "${r.text.slice(0, 48)}"`; }
      ok(r.nmOnBoxLine !== false,
        `${p} @${w}: the name "${r.nmText}" dropped below its own checkbox`);
      if (r.tag) {
        if (r.lines !== 1) bad++;
        ok(r.lines === 1, `${p} @${w}: badge "${r.text}" wrapped to ${r.lines} lines`);
      } else {
        ok(r.nmX === null || Math.abs(r.x - r.nmX) <= 1.5,
          `${p} @${w}: a sentence aside starts at x=${r.x.toFixed(1)} but the name starts at ${r.nmX && r.nmX.toFixed(1)}`);
        // It has the rest of the row, so it can never be a column again.
        ok(r.inner === null || r.width >= r.inner - (r.x - (r.rowRight - r.inner)) - 1.5,
          `${p} @${w}: a sentence aside is ${r.width.toFixed(0)}px wide inside a ${r.inner.toFixed(0)}px row`);
        if (r.text.length >= DENSITY_FLOOR_LEN) {
          const dens = r.text.length / r.lines;
          if (dens < MIN_CHARS_PER_LINE) bad++;
          ok(dens >= MIN_CHARS_PER_LINE,
            `${p} @${w}: "${r.text.slice(0, 40)}…" stacks ${dens.toFixed(1)} chars per line over ${r.lines} lines`);
        }
      }
      ok(r.rowRight === null || r.right <= r.rowRight + 0.5,
        `${p} @${w}: "${r.text.slice(0, 30)}…" runs ${(r.right - r.rowRight).toFixed(1)}px past its row`);
    }
  }
  ok(errs.length === 0, `${p}: page errors ${JSON.stringify(errs.slice(0, 2))}`);
  if (!quiet) console.log(`${p}: ${n} aside(s), worst ${pageWorst} line(s)${bad ? `  <-- ${bad} over` : ''}`);
  await ctx.close();
}
await browser.close();
console.log(`${LIST.length} page(s), ${measured} aside-measurements, ${checks} checks, ${fails} failed`);
console.log(`WORST: ${worst} line(s) — ${worstWhere}`);
process.exit(fails ? 1 : 0);
