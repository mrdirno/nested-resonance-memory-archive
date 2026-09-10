/* Drive the REAL siding pages and DO THE JOB THEY CLAIM — a render is not a feature.
 * Trade #18 stand-up drive (C3726). Same harness as _drive_paving.mjs.
 * Usage: node tools/toolkit-gates/_drive_siding.mjs [baseUrl]   (default: local file://)
 * Pass https://mrdirno.github.io/nested-resonance-memory-archive/ after the deploy.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { createRequire } from 'module';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');
const BASE = (process.argv[2] || 'file:///Volumes/dual/nested-resonance-memory-archive/').replace(/\/*$/, '/');
const b = await chromium.launch();
const fails = [], notes = [];
const ok = (c, m) => { (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };

async function page(path, w = 390) {
  const ctx = await b.newContext({ viewport: { width: w, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.goto(BASE + path, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  return { p, ctx, errs };
}
const overflow = async p => p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
/* The donor kit's words must not survive anywhere a man can read them. The donor
 * for every page in this kit is PAVING. "wall" and "trim" are ours; "mat", "lot",
 * "striper", "curb" and "the plant" are the words that would prove a bad copy. */
const DONOR = /\bmat\b|striper|sealcoat|asphalt|\bthe plant\b|stall count|birdbath/i;

const typeIn = async (p, key, value) => {
  const sel = `#bar [data-for="${key}"] input.rl-in, #bar [data-for="${key}"] textarea.rl-in`;
  const el = p.locator(sel).first();
  if (!(await el.count())) return false;
  await el.click(); await el.fill(value); await el.blur();
  return true;
};
const chip = async (p, key, label) => {
  const host = p.locator(`#bar [data-for="${key}"]`).first();
  if (!(await host.count())) return false;
  const btn = host.getByRole('button', { name: label, exact: false }).first();
  if (!(await btn.count())) return false;
  await btn.click();
  return true;
};

/* ── 1. THROUGH MY WALL — the pinned page. Walk an elevation and read it back ── */
{
  const { p, ctx, errs } = await page('siding/through-my-wall.html');
  await p.fill('#hJob', '412 Marchmont — full re-side');
  await p.fill('#hOff', 'A-201 rev 3, and what each outfit told me');
  await p.fill('#hFrom', 'Dale W — Rivet Exteriors');
  await p.fill('#hTel', '559-555-0143');
  const typed = {
    mark:  await typeIn(p, 'mark', 'left of the rear door, under the deck'),
    face:  await chip(p, 'face', 'Rear'),
    whose: await chip(p, 'whose', 'HVAC'),
    what:  await chip(p, 'what', 'line set'),
    told:  await typeIn(p, 'told', 'Ana C, mechanical — Tuesday at the tailgate'),
    state: await chip(p, 'state', 'Marked only'),
    ask:   await chip(p, 'ask', 'Get it through before I close'),
    gate:  await chip(p, 'gate', 'Before I close this elevation'),
  };
  notes.push('  through-my-wall typed: ' + JSON.stringify(typed));
  ok(Object.values(typed).every(Boolean), 'through-my-wall: every field exists on the bar (mark, face, whose, what, told, state, ask, gate)');
  const badBefore = await p.evaluate(() => document.querySelectorAll('#bar .rl-bad').length);
  ok(badBefore === 0, `through-my-wall: no field left invalid after a real thumb fills it (rl-bad=${badBefore})`);
  await p.click('#rlAdd');
  await p.waitForTimeout(350);

  // a SECOND hole on the same elevation — the sticky fields are the whole ergonomic claim
  await typeIn(p, 'mark', 'right of the rear door, above the bib');
  await chip(p, 'whose', 'Electrician');
  await chip(p, 'what', 'Light block');
  await chip(p, 'state', 'Through, nothing on it');
  await chip(p, 'ask', 'Tell me where you want it');
  const stickyFace = await p.evaluate(() => {
    const h = document.querySelector('#bar [data-for="face"]');
    const on = h && h.querySelector('button.on, button[aria-pressed="true"]');
    return on ? on.textContent.trim() : '';
  });
  ok(/rear/i.test(stickyFace), `through-my-wall: the elevation stays picked for the next hole (sticky = "${stickyFace}")`);
  await p.click('#rlAdd');
  await p.waitForTimeout(350);

  const rows = await p.evaluate(() => document.querySelectorAll('#list .rl-row').length);
  ok(rows >= 2, `through-my-wall: two holes on one elevation produce two rows (got ${rows})`);
  const preview = (await p.textContent('#preview')) || '';
  ok(/rear door/.test(preview), 'through-my-wall: the spot reaches the document');
  ok(/412 Marchmont/.test(preview), 'through-my-wall: the job header reaches the document');
  ok(/A-201 rev 3/.test(preview), 'through-my-wall: the set rides as an address');
  ok(/Ana C/.test(preview), 'through-my-wall: the name of whoever told him reaches the document');
  ok(/line set/i.test(preview), 'through-my-wall: what the hole is reaches the document');
  ok(/light block/i.test(preview), 'through-my-wall: the second hole reaches the same document');
  ok(/before I close this elevation/i.test(preview), 'through-my-wall: the gate reaches the document');
  ok(/2 holes/i.test(preview) && /elevation/i.test(preview), 'through-my-wall: the count line names holes and elevations');
  ok(/not a hole size|no hole size|hole size/i.test(preview) && /flashing detail/i.test(preview),
     'through-my-wall: the document states its own refusal (no hole size, clearance, flashing detail, sealant) in words');
  ok(/weathertight/i.test(preview), 'through-my-wall: the document refuses the weathertight verdict in words');
  ok(!DONOR.test(preview), 'through-my-wall: no donor-trade word in the document');
  ok(await overflow(p) <= 0, 'through-my-wall: no horizontal overflow at 390px with rows on it');
  ok(errs.length === 0, 'through-my-wall: zero page errors ' + errs.slice(0, 1));

  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(500);
  const rowsAfter = await p.evaluate(() => document.querySelectorAll('#list .rl-row').length);
  ok(rowsAfter >= 2, `through-my-wall: the walk survives a reload (rows=${rowsAfter})`);
  const hdr = await p.evaluate(() => ['#hJob','#hOff','#hFrom','#hTel'].map(s => document.querySelector(s).value));
  ok(hdr[0] === '412 Marchmont — full re-side' && /A-201/.test(hdr[1]) && /Dale W/.test(hdr[2]) && /0143/.test(hdr[3]),
     `through-my-wall: the job header survives the reload with the walk (${JSON.stringify(hdr)})`);
  notes.push('  through-my-wall preview chars: ' + preview.length);
  notes.push('\n----- THE DOCUMENT A SIDING LEAD WOULD SEND -----\n' + preview + '\n-----------------------------------------------\n');
  await ctx.close();
}

/* ── 2. WALL'S NOT READY — the refusal, and its two-button ask ── */
{
  const { p, ctx, errs } = await page('siding/not-ready-to-side.html');
  const boxes = await p.$$('[data-f="stops"] li input, .ticks li input');
  ok(boxes.length >= 12, `not-ready-to-side: the stops list is real (${boxes.length} conditions)`);
  for (let i = 0; i < Math.min(3, boxes.length); i++) await boxes[i].click();
  await p.waitForTimeout(300);
  const body = await p.evaluate(() => document.body.innerText);
  ok(/reply FIX/i.test(body), 'not-ready-to-side: the FIX button word is on the page');
  ok(/reply CLOSE/i.test(body), "not-ready-to-side: the trade's own second button is CLOSE, not the donor's PAVE");
  ok(!/reply PAVE/i.test(body), 'not-ready-to-side: the donor two-button word is gone');
  ok(!DONOR.test(body), 'not-ready-to-side: no donor-trade word anywhere a man can read it');
  ok(await overflow(p) <= 0, 'not-ready-to-side: no horizontal overflow at 390px');
  ok(errs.length === 0, "not-ready-to-side: zero page errors " + errs.slice(0, 1));
  await ctx.close();
}

/* ── 3. THE BOUNDARY LOOP — ask -> answer, and the fourth rung classified ── */
{
  const { p, ctx, errs } = await page('siding/rough-in-request.html');
  const shape = await p.evaluate(() => {
    const r = window.TOOLKIT_ROUGHIN || {}, a = window.TOOLKIT_ANSWER || {};
    return { name: r.toolName, asks: (r.asks || []).length, who: (r.who || []).length, ms: (r.milestones || []).length,
             routed: (r.asks || []).every(x => (r.who || []).some(w => w.v === x.who) && (r.milestones || []).some(m => m.v === x.by)),
             answers: a.answers || [] };
  });
  ok(shape.name === 'Before I Close It', `TOOLKIT_ROUGHIN.toolName is the trade's own (${shape.name})`);
  ok(shape.asks >= 10 && shape.who >= 8 && shape.ms >= 6, `TOOLKIT_ROUGHIN carries real asks/receivers/milestones (${shape.asks}/${shape.who}/${shape.ms})`);
  ok(shape.routed, 'every ask routes to a receiver and a milestone that exist');
  ok(shape.answers.length === 4 && /wall/i.test(shape.answers[3]),
     `TOOLKIT_ANSWER ships four rungs and the fourth is this trade's own (${shape.answers.join(' / ')})`);
  const mounted = await p.evaluate(() => !!document.querySelector('[id*="econcile"], .rc, .reconcile') || /Reconcile\.mount/.test(document.documentElement.innerHTML));
  ok(mounted, 'rough-in-request: the reconcile card is mounted, so an answer has somewhere to land');
  ok(errs.length === 0, 'rough-in-request: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}
{
  const { p, ctx, errs } = await page('siding/answer-back.html');
  /* THE FOURTH RUNG HAS TO BE IN THE ENGINE, not just in the config: a rung missing
     from reconcile.js VERDICTS classifies as NOTHING, and every answer on this trade
     comes back reading "didn't say yes or no" while the page looks completely normal.
     Assert it against the shipped module the page actually loaded. */
  const rungs = await p.evaluate(() => (window.TOOLKIT_ANSWER || {}).answers || []);
  /* file:// cannot fetch a sibling file, so read the module the page named:
     off disk locally, over the network against a deployed base. */
  /* reconcile.js is loaded by rough-in-request (the page an answer lands on), not by
     answer-back — so resolve it against the BASE rather than off this page's scripts.
     file:// cannot fetch a sibling file, so read it off disk locally and over the
     network against a deployed base. */
  const engineUrl = BASE + 'shared/reconcile.js';
  const engine = engineUrl.startsWith('file:')
    ? readFileSync(fileURLToPath(engineUrl), 'utf8')
    : await (await p.request.get(engineUrl)).text();
  const norm = x => String(x).toLowerCase().replace(/[^a-z ]/g, '');
  const unclassified = rungs.filter(r => !engine.includes('"' + norm(r) + '"'));
  ok(engine.length > 0 && unclassified.length === 0,
     `answer-back: every rung is classified in reconcile.js VERDICTS (unclassified: ${JSON.stringify(unclassified)})`);
  notes.push('  answer rungs: ' + JSON.stringify(rungs));
  ok(errs.length === 0, 'answer-back: zero page errors ' + errs.slice(0, 1));
  const note = await p.evaluate(() => document.body.innerText);
  ok(/it.s the wall/i.test(note), "answer-back: the tap instruction teaches this trade's fourth rung");
  ok(!/it.s the plan/i.test(note), "answer-back: the donor's fourth rung is gone from the instructions");
  await ctx.close();
}

/* ── 4. THE WRITE-UP SHELF — the block a man pastes into his AI ── */
{
  const { p, ctx, errs } = await page('siding/write-up.html');
  const lib = await p.evaluate(() => {
    const d = window.TRADE_DOCS || {};
    return { trade: d.trade, n: (d.docs || []).length, ids: (d.docs || []).map(x => x.id),
             fams: [...new Set((d.docs || []).map(x => x.family))] };
  });
  ok(lib.n === 6, `write-up: the trade ships its own document library (${lib.n} documents)`);
  ok(lib.trade === 'siding and exterior trim', `write-up: the trade word is the trade's own ("${lib.trade}")`);
  ok(lib.fams.every(f => ['recurring','incident','verification','notice','minutes'].includes(f)),
     `write-up: every family is one the engine declares (${lib.fams.join(', ')})`);
  const body = await p.evaluate(() => document.body.innerText);
  ok(!/\[object Object\]/.test(body), 'write-up: no stringified object anywhere on the shelf');
  ok(errs.length === 0, 'write-up: zero page errors ' + errs.slice(0, 1));
  ok(await overflow(p) <= 0, 'write-up: no horizontal overflow at 390px');
  await ctx.close();
}

/* ── 5. THE HUB — the kit is reachable and wears its own colour ── */
{
  const { p, ctx, errs } = await page('siding/index.html');
  const hub = await p.evaluate(() => ({
    flag: getComputedStyle(document.documentElement).getPropertyValue('--flag').trim().toUpperCase(),
    accent: (window.TOOLKIT_TRADE || {}).accent,
    cards: document.querySelectorAll('#grid .tool').length,
    pinnedFirst: (document.querySelector('#grid .tool .tool-name') || {}).textContent,
    /* #siblings is a MOUNT MARKER the runtime REMOVES — count what it actually
       inserted instead, which is one relative link per sibling kit plus the commons. */
    siblings: [...document.querySelectorAll('a[href^="../"]')].length,
    hasSiding: !!document.querySelector('a[href="../siding/"]') || location.pathname.includes('/siding/'),
  }));
  ok(hub.flag === String(hub.accent).toUpperCase(), `hub wears its own colour (--flag ${hub.flag} = accent ${hub.accent})`);
  ok(hub.cards === 7, `hub renders every registry entry (${hub.cards} cards)`);
  ok(/Through My Wall/i.test(hub.pinnedFirst || ''), `the pinned tool is first on the hub ("${hub.pinnedFirst}")`);
  ok(hub.siblings >= 17, `the kit switcher offers every sibling (${hub.siblings} relative links)`);
  ok(errs.length === 0, 'hub: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

await b.close();
console.log(notes.join('\n'));
console.log('\n' + '='.repeat(60));
if (fails.length) { console.log(fails.join('\n')); console.log(`\n${fails.length} FAILING, ${notes.filter(n=>n.startsWith('PASS')).length} passing`); process.exit(1); }
console.log(`ALL ${notes.filter(n=>n.startsWith('PASS')).length} ASSERTIONS PASS — ${BASE}`);
