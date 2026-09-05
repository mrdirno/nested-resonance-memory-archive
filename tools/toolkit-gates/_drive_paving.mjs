/* Drive the REAL paving pages and DO THE JOB THEY CLAIM — a render is not a feature.
 * Trade #17 stand-up drive (C3706). Same harness as _drive_doors.mjs.
 * Usage: node tools/toolkit-gates/_drive_paving.mjs [baseUrl]   (default: local file://)
 * Pass https://mrdirno.github.io/nested-resonance-memory-archive/ after the deploy. */
import { createRequire } from 'module';
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
/* The donor kit's words must not survive anywhere a man can read them. "plant" is
 * deliberately NOT on this list: an asphalt PLANT is this trade's own word. */
const DONOR = /landscape|irrigation|nursery|rootball|\bsod\b|backflow/i;

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

/* ── 1. DOESN'T FIT — the pinned page: lay a run out and read it back ── */
{
  const { p, ctx, errs } = await page('paving/doesnt-fit.html');
  await p.fill('#hJob', 'Willow Creek — Phase 2, north lot');
  await p.fill('#hOff', 'C-201 rev 3');
  await p.fill('#hFrom', 'Manny R — Blacktop Bros Paving');
  const typed = {
    mark:  await typeIn(p, 'mark', 'run along the north curb'),
    area:  await typeIn(p, 'area', 'north lot, rows A-B'),
    sheet: await typeIn(p, 'sheet', 'C-201 rev 3'),
    draws: await typeIn(p, 'draws', '14 stalls, the accessible pair at the east end'),
    found: await typeIn(p, 'found', '13 at the plan width — the pole base eats one'),
    way:   await chip(p, 'way', 'pole base'),
    ask:   await chip(p, 'ask', 'which one goes'),
  };
  notes.push('  doesnt-fit typed: ' + JSON.stringify(typed));
  ok(Object.values(typed).every(Boolean), 'doesnt-fit: every spec field exists on the bar (mark, area, sheet, draws, found, way, ask)');
  const badBefore = await p.evaluate(() => document.querySelectorAll('#bar .rl-bad').length);
  ok(badBefore === 0, `doesnt-fit: no field left invalid after a real thumb fills it (rl-bad=${badBefore})`);
  await p.click('#rlAdd');
  await p.waitForTimeout(350);
  const rows = await p.evaluate(() => document.querySelectorAll('#list .rl-row').length);
  ok(rows >= 1, `doesnt-fit: adding a spot produces a row (got ${rows})`);
  const preview = (await p.textContent('#preview')) || '';
  ok(/north curb/.test(preview), 'doesnt-fit: the spot reaches the document');
  ok(/Willow Creek/.test(preview), 'doesnt-fit: the job header reaches the document');
  ok(/C-201 rev 3/.test(preview), 'doesnt-fit: the sheet rides as an address');
  ok(/13 at the plan width/.test(preview), 'doesnt-fit: what the tape found reaches the document');
  ok(/14 stalls/.test(preview), 'doesnt-fit: what the sheet draws reaches the document, quoted');
  ok(/pole base/i.test(preview), 'doesnt-fit: what is in the way reaches the document');
  ok(/which one goes/i.test(preview), 'doesnt-fit: the ask reaches the document');
  ok(/count|dimension|slope|accessib/i.test(preview) && /no stall count|not a stall count|nothing here is a stall count|no count/i.test(preview),
     'doesnt-fit: the document states its own refusal (no count, dimension, slope or accessibility call of ours) in words');
  ok(!DONOR.test(preview), 'doesnt-fit: no donor-trade word in the document');
  ok(await overflow(p) <= 0, 'doesnt-fit: no horizontal overflow at 390px with a row on it');
  ok(errs.length === 0, 'doesnt-fit: zero page errors ' + errs.slice(0, 1));
  // persistence: reload and the row is still there
  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(450);
  const rowsAfter = await p.evaluate(() => document.querySelectorAll('#list .rl-row').length);
  ok(rowsAfter >= 1, `doesnt-fit: the walk survives a reload (rows=${rowsAfter})`);
  // ...and so does the job header (found missing by the trade #17 field drive: rows came back under an empty header)
  const hdr = await p.evaluate(() => [document.querySelector('#hJob').value, document.querySelector('#hOff').value, document.querySelector('#hFrom').value]);
  ok(hdr[0] === 'Willow Creek — Phase 2, north lot' && hdr[1] === 'C-201 rev 3' && /Manny R/.test(hdr[2]),
     `doesnt-fit: the job header survives the reload with the walk (${JSON.stringify(hdr)})`);
  notes.push('  doesnt-fit preview chars: ' + preview.length);
  await ctx.close();
}

/* ── 2. UNDER THE MAT — the letter back: one thing under the base ── */
{
  const { p, ctx, errs } = await page('paving/under-the-mat.html');
  await p.fill('#hJob', 'Willow Creek — Phase 2, north lot');
  await p.fill('#hFrom', 'Manny R — Blacktop Bros Paving');
  const typed = {
    mark:  await typeIn(p, 'mark', 'drive crossing by the dock'),
    area:  await typeIn(p, 'area', 'the drive to the loading dock'),
    whose: await chip(p, 'whose', 'Landscape'),
    what:  await chip(p, 'what', 'Sleeve'),
    told:  await typeIn(p, 'told', "Ray T's crossing list 9/12"),
    seen:  await chip(p, 'seen', 'Saw it in'),
    iron:  await chip(p, 'iron', 'To grade'),
    gate:  await chip(p, 'gate', 'base rolls'),
  };
  notes.push('  under-the-mat typed: ' + JSON.stringify(typed));
  ok(Object.values(typed).every(Boolean), 'under-the-mat: every spec field exists on the bar (mark, area, whose, what, told, seen, iron, gate)');
  await p.click('#rlAdd');
  await p.waitForTimeout(350);
  const preview = (await p.textContent('#preview')) || '';
  ok(/drive crossing by the dock/.test(preview), 'under-the-mat: the spot reaches the document');
  ok(/Ray T/.test(preview), 'under-the-mat: who told him reaches the document');
  ok(/sleeve/i.test(preview), 'under-the-mat: what it is reaches the document');
  ok(/saw it in/i.test(preview), 'under-the-mat: whether he saw it reaches the document');
  ok(/saw cut/i.test(preview), 'under-the-mat: the footer says what the mat costs once it is down');
  ok(/cover depth|sleeve size|separation/i.test(preview), 'under-the-mat: the document refuses the numbers it does not own, in words');
  ok(!/nursery|irrigation hand|rootball/i.test(preview), 'under-the-mat: no donor-trade word in the document');
  ok(await overflow(p) <= 0, 'under-the-mat: no horizontal overflow at 390px with a row on it');
  ok(errs.length === 0, 'under-the-mat: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

/* ── 3. NOT READY TO PAVE — tick a stop and read the note ── */
{
  const { p, ctx, errs } = await page('paving/not-ready-to-pave.html');
  await p.waitForTimeout(300);
  const ticked = await p.evaluate(() => {
    const btn = [...document.querySelectorAll('button, label, .tick')].find(x => /soft|pumps/i.test(x.textContent));
    if (btn) { btn.click(); return btn.textContent.trim().slice(0, 50); }
    return null;
  });
  await p.waitForTimeout(250);
  const prev = (await p.textContent('#preview')) || '';
  ok(!!ticked, 'not-ready-to-pave: a stop is tickable (' + ticked + ')');
  ok(/NOT READY TO PAVE/.test(prev), 'not-ready-to-pave: doc name is the trade’s own');
  ok(!/NOT READY TO PLANT/.test(prev), 'not-ready-to-pave: no donor-trade doc name survives');
  ok(/soft|pump/i.test(prev), 'not-ready-to-pave: the ticked stop reaches the note');
  ok(/PAVE\b/.test(prev) && /FIX/.test(prev), 'not-ready-to-pave: the two-button close (FIX / PAVE) is in the note');
  ok(!DONOR.test(prev), 'not-ready-to-pave: no donor-trade word in the note');
  ok(await overflow(p) <= 0, 'not-ready-to-pave: no horizontal overflow at 390px');
  ok(errs.length === 0, 'not-ready-to-pave: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

/* ── 4. LOT CLOSED TONIGHT — the closure note ── */
{
  const { p, ctx, errs } = await page('paving/lot-closed-tonight.html');
  await p.waitForTimeout(300);
  const body = await p.evaluate(() => document.body.innerText);
  ok(/LOT CLOSED TONIGHT|Lot Closed Tonight/.test(body), 'lot-closed: the page wears its own name');
  ok(!/THE WATER'S YOURS|WATER.S YOURS/i.test(body), 'lot-closed: no donor doc name survives');
  const ticked = await p.evaluate(() => {
    const btn = [...document.querySelectorAll('button, label, .tick')].find(x => /tenant/i.test(x.textContent));
    if (btn) { btn.click(); return btn.textContent.trim().slice(0, 50); }
    return null;
  });
  await p.waitForTimeout(250);
  const prev = (await p.textContent('#preview')) || '';
  ok(!!ticked, 'lot-closed: an ask is tickable (' + ticked + ')');
  ok(/tenant/i.test(prev), 'lot-closed: the ticked ask reaches the note');
  ok(/not a permit|not a traffic plan|not a traffic-control plan/i.test(prev), 'lot-closed: the note refuses to be a permit or a traffic plan, in words');
  ok(!DONOR.test(prev), 'lot-closed: no donor-trade word in the note');
  ok(await overflow(p) <= 0, 'lot-closed: no horizontal overflow at 390px');
  ok(errs.length === 0, 'lot-closed: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

/* ── 5. WALK BACK — the fourth rung this trade needed, tapped for real ── */
{
  const { p, ctx, errs } = await page('paving/answer-back.html');
  const body = await p.evaluate(() => document.body.innerText);
  ok(/It.s the plan/i.test(body), 'walk-back: the trade’s own fourth rung is on the glass');
  ok(!/It.s the water|not my call|need the room/i.test(body), 'walk-back: no donor rung survives on the glass');
  await p.fill('#bPaste', 'Willow Creek north lot — punch — Sep 12\n\nJob: Willow Creek\nFrom: Dana K — GC super\n\n31. dock — arrows point the wrong way\n32. stall 14 — short against the sheet\n33. cart corral — water sitting after the rain\n');
  await p.click('#bPasteGo');
  await p.waitForTimeout(400);
  const rows = await p.evaluate(() => document.querySelectorAll('#list .rl-row').length);
  ok(rows >= 3, `walk-back: the pasted punch lines up into rows (got ${rows})`);
  // tap the first row four times → the fourth rung
  for (let i = 0; i < 4; i++) { await p.locator('#list .rl-row').first().click(); await p.waitForTimeout(120); }
  const preview = (await p.textContent('#preview')) || '';
  ok(/It.s the plan/i.test(preview), 'walk-back: four taps land on "It’s the plan" and it reaches the document');
  ok(!DONOR.test(preview), 'walk-back: no donor-trade word in the document');
  ok(await overflow(p) <= 0, 'walk-back: no horizontal overflow at 390px');
  ok(errs.length === 0, 'walk-back: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

/* ── 6. HUB — every registered tool is reachable and the trade is itself ── */
{
  const { p, ctx, errs } = await page('paving/index.html');
  const hrefs = await p.evaluate(() => [...document.querySelectorAll('a[href$=".html"]')].map(a => a.getAttribute('href')));
  for (const want of ['doesnt-fit.html','under-the-mat.html','rough-in-request.html','answer-back.html','not-ready-to-pave.html',
                      'lot-closed-tonight.html','getting-in.html','write-up.html','total-package.html','credits.html'])
    ok(hrefs.includes(want), `hub links ${want}`);
  const first = await p.evaluate(() => { const a = document.querySelector('#grid a.tool'); return a ? a.getAttribute('href') : ''; });
  ok(first === 'doesnt-fit.html', `hub: the pinned page is first (${first})`);
  const t = await p.title();
  ok(/Paving/.test(t), 'hub title is the trade’s own: ' + t);
  /* The kit switcher and the audience tags legitimately name the neighbour
   * trades (a receiver chip IS the landscape guy) — the donor check on a hub is
   * the plate: the words this kit says about ITSELF. */
  const plate = await p.evaluate(() => (document.querySelector('.plate') || document.body).innerText);
  ok(!DONOR.test(plate), 'hub: no donor-trade word in the plate (h1 + lede)');
  const body = await p.evaluate(() => document.body.innerText);
  ok(!/\bpavers\b/i.test(body), 'hub: the name collision is honoured — "pavers" is masonry’s word and is not on this hub');
  const flag = await p.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--flag').trim().toUpperCase());
  ok(flag === '#FDF37A', `hub: --flag is the trade’s accent (${flag})`);
  ok(errs.length === 0, 'hub: zero page errors ' + errs.slice(0, 1));
  ok(await overflow(p) <= 0, 'hub: no horizontal overflow at 390px');
  await ctx.close();
}

/* ── 7. THE CONFIG-DRIVEN PAGES — load, own words, no donor words ── */
for (const [path, mustSay] of [
  ['paving/getting-in.html',       /ACCESS REQUEST/i],
  ['paving/rough-in-request.html', /Before I Roll/i],
  ['paving/write-up.html',         /Write-Up|write-up/i],
  ['paving/total-package.html',    /TOTAL PACKAGE|Total Package/i],
  ['paving/credits.html',          /Wall of Wishes/i],
]) {
  const { p, ctx, errs } = await page(path);
  await p.waitForTimeout(500);
  ok(errs.length === 0, `${path}: zero page errors on load ${errs.slice(0, 1)}`);
  const txt = await p.evaluate(() => document.body.innerText);
  ok(mustSay.test(txt), `${path}: renders its own content`);
  ok(/Paving/.test(await p.title()) || /credits/.test(path), `${path}: title is the trade's own`);
  ok(!/Landscape/.test(await p.title()), `${path}: no donor trade in the title`);
  /* Receiver lists name the neighbour trades on purpose; the plate is what this
   * page says about itself. */
  const plate = await p.evaluate(() => (document.querySelector('.plate') || document.body).innerText);
  ok(!DONOR.test(plate), `${path}: no donor-trade word in the plate (h1 + lede)`);
  ok(await overflow(p) <= 0, `${path}: no horizontal overflow at 390px`);
  await ctx.close();
}

/* ── 8. EVERY CONFIG THE PAGES DEREFERENCE MUST EXIST ── */
{
  const { p, ctx } = await page('paving/getting-in.html');
  const shape = await p.evaluate(() => {
    const g = window.TOOLKIT_GETIN || {};
    return { closingIsArray: Array.isArray(g.closing), hasWarn: typeof g.warn === 'string',
             hasPhCo: typeof g.phCo === 'string', needs: (g.need || []).length, heads: (g.heads || []).length,
             window: (g.closing || []).join(' ').includes("window you're actually giving us"),
             booking: (g.closing || []).join(' ').includes('ask, not a booking') };
  });
  ok(shape.closingIsArray, 'TOOLKIT_GETIN.closing is an array the page can concat');
  ok(shape.hasWarn && shape.hasPhCo, 'TOOLKIT_GETIN.warn and phCo are present');
  ok(shape.needs >= 8 && shape.heads >= 8, `TOOLKIT_GETIN has real needs/heads (${shape.needs}/${shape.heads})`);
  ok(shape.window && shape.booking, 'TOOLKIT_GETIN.closing carries the two sentences the gate reads by regex');
  await ctx.close();
}
{
  const { p, ctx } = await page('paving/rough-in-request.html');
  const shape = await p.evaluate(() => {
    const r = window.TOOLKIT_ROUGHIN || {}, a = window.TOOLKIT_ANSWER || {};
    return { name: r.toolName, asks: (r.asks || []).length, who: (r.who || []).length, ms: (r.milestones || []).length,
             routed: (r.asks || []).every(x => (r.who || []).some(w => w.v === x.who) && (r.milestones || []).some(m => m.v === x.by)),
             answers: a.answers || [] };
  });
  ok(shape.name === 'Before I Roll', `TOOLKIT_ROUGHIN.toolName is the trade's own (${shape.name})`);
  ok(shape.asks >= 10 && shape.who >= 8 && shape.ms >= 6, `TOOLKIT_ROUGHIN carries real asks/receivers/milestones (${shape.asks}/${shape.who}/${shape.ms})`);
  ok(shape.routed, 'every ask routes to a receiver and a milestone that exist');
  ok(shape.answers.length === 4 && /plan/i.test(shape.answers[3]), `TOOLKIT_ANSWER ships four rungs and the fourth is this trade's own (${shape.answers.join(' / ')})`);
  await ctx.close();
}

await b.close();
console.log(notes.join('\n'));
console.log('\n' + '='.repeat(60));
if (fails.length) { console.log(fails.join('\n')); console.log(`\n${fails.length} FAILING, ${notes.filter(n=>n.startsWith('PASS')).length} passing`); process.exit(1); }
console.log(`ALL ${notes.filter(n=>n.startsWith('PASS')).length} ASSERTIONS PASS — ${BASE}`);
