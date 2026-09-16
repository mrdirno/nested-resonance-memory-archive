/* Drive the REAL doors pages and DO THE JOB THEY CLAIM — a render is not a feature.
 * First written at C3730 for the keying ASK (call-the-keying.html). _drive_paving.mjs cites
 * a `_drive_doors.mjs` as its harness; no such file was ever committed (it lived in a
 * dead cycle's scratch), so this is the first one on disk. Same harness as
 * _drive_siding.mjs.
 * Usage: node tools/toolkit-gates/_drive_doors.mjs [baseUrl]   (default: local file://)
 * Pass https://mrdirno.github.io/nested-resonance-memory-archive/ after the deploy. */
import { createRequire } from 'module';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');
const BASE = (process.argv[2] || 'file:///Volumes/dual/nested-resonance-memory-archive/').replace(/\/*$/, '/');
const b = await chromium.launch();
const fails = [], notes = [];
const ok = (c, m) => { (c ? notes : fails).push((c ? 'PASS  ' : 'FAIL  ') + m); };

async function page(path, w = 390) {
  const ctx = await b.newContext({ viewport: { width: w, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, locale: 'en-US' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  p.on('dialog', d => d.accept());
  await p.goto(BASE + path, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(450);
  return { p, ctx, errs };
}
const overflow = async p => p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
const preview = async p => (await p.textContent('#preview')) || '';

/* The no-clock clause family, verbatim from no-clock.mjs — asserted here on the one
 * document whose whole subject is a date with a consequence on it. */
const CLAUSES = [
  /\b(deemed|considered)\s+(to\s+be\s+)?(approved|accepted|final|complete|signed[-\s]?off)\b/i,
  /\b(approved|accepted|final)\b[^.!?]{0,70}\bif\s+(i|we)\s+(don'?t|do not)\s+hear\b/i,
  /\bif\s+(i|we)\s+(don'?t|do not)\s+hear[^.!?]{0,60}\b(i'?ll|we'?ll|i will|we will)\s+(proceed|assume|treat|take|go ahead)\b/i,
  /\bunless\s+(i|we)\s+hear[^.!?]{0,70}\b(approved|accepted|final|proceed|assume|go ahead)\b/i,
  /\bwithin\s+\d+\s+(business\s+)?days?\b[^.!?]{0,90}\b(approved|accepted|final|closed)\b/i,
  /\byour\s+silence\b/i,
  /\bno\s+(reply|response)\b[^.!?]{0,50}\b(approval|accepted|agreement|means yes)\b/i,
];

/* ── 1. SAY THE WORD — the keying ask, end to end ── */
{
  const { p, ctx, errs } = await page('doors/call-the-keying.html');
  ok((await p.title()).startsWith('Call The Keying'), 'call-the-keying: the tab carries the tool name');
  { const u = await preview(p); ok(!/\nTO\n/.test(u) && !/WHAT I'M HOLDING/.test(u) && /not a keying schedule/.test(u), 'call-the-keying: an untouched page carries no field block — only the name, the day and the fixed closing, like every sibling'); }

  await p.fill('[data-f="site"] input', 'Alder Creek Medical — 3rd floor TI');
  await p.click('[data-f="role"] button:has-text("GC superintendent")');
  await p.fill('[data-f="who"] input', 'Dana K. — GC super');
  await p.click('[data-f="when"] .nowbtn');
  await p.fill('[data-f="count"] input', '18 cylinders in the hardware cage on 3, still in the cartons — one per opening, two at the pairs');
  await p.fill('[data-f="rooms"] textarea', '301 through 312, both stair doors, and the two IT rooms — sixteen openings');
  await p.click('[data-f="came"] button:has-text("Construction cores in them")');
  const ticks = ["There's been no keying meeting", "Do we go on the construction key for now",
                 "Whose trip is the core swap", "Who takes the permanent cores and the control key"];
  for (const t of ticks) {
    const cb = p.locator(`[data-f="missing"] input[data-name="${t.replace(/"/g, '\\"')}"]`);
    ok(await cb.count() === 1, `call-the-keying: the tick exists — ${t}`);
    if (await cb.count()) await cb.check();
  }
  await p.fill('[data-f="extra"] textarea', "the IT rooms — somebody said they're on the owner's own system, and nobody's said who has it");
  await p.fill('[data-f="by"] input', '2026-09-25');
  await p.dispatchEvent('[data-f="by"] input', 'input');
  await p.fill('[data-f="cost"] textarea', 'the locks go on Friday with the temp cores in them so the floor locks');
  await p.click('[data-f="cost"] .chips button:has-text("re-coring is a second trip")');
  await p.click('[data-f="cost"] .seg button:has-text("Need it before they go on")');
  await p.fill('[data-f="lead"] input', 'keying department said three weeks after the meeting — and move-in is the 14th');
  await p.fill('[data-f="me"] input', 'R. Tolliver — 559-555-0173');
  await p.fill('[data-f="co"] input', 'Vantage Door & Hardware');
  await p.waitForTimeout(350);

  const doc = await preview(p);
  notes.push('  call-the-keying document: ' + doc.length + ' chars');
  ok(/^KEYING — WHAT I NEED DECIDED — decide by Fri, Sep 25\n/.test(doc), 'call-the-keying: the date rides in the title, as words');
  ok(/\nAlder Creek Medical — 3rd floor TI  ·  /.test(doc), 'call-the-keying: the job rides on the second line with the day');
  ok(/\nTO\nTo: GC superintendent\nName: Dana K\. — GC super\nSent: /.test(doc), 'call-the-keying: TO block — role, name, the self-stamped clock');
  ok(/\nWHAT I'M HOLDING\n18 cylinders in the hardware cage/.test(doc), 'call-the-keying: the count reaches the document');
  ok(/For: 301 through 312/.test(doc), 'call-the-keying: the openings ride as addresses');
  ok(/What came: cylinders came with construction cores in them/.test(doc), 'call-the-keying: the seg prints its doc form, not its button label');
  ok(/\nWHAT NOBODY'S TOLD ME\n- There's been no keying meeting \(the owner, the consultant and the distributor/.test(doc), 'call-the-keying: a tick prints with its reason under it');
  ok(/- Do we go on the construction key for now \(say the word:/.test(doc), 'call-the-keying: the say-the-word tick prints');
  ok(/- Whose trip is the core swap \(me, the distributor, or the owner's locksmith — say whose now, and whose scope it sits in/.test(doc), 'call-the-keying: the core-swap tick asks, it does not claim');
  ok(/- Who takes the permanent cores and the control key \(a name and a signature/.test(doc), 'call-the-keying: the control-key tick prints');
  ok(/the IT rooms — somebody said/.test(doc), "call-the-keying: the one that's not on the list reaches the document");
  ok(/\nTHE DATE, AND WHAT HAPPENS WITHOUT IT\nthe locks go on Friday with the temp cores in them so the floor locks re-coring is a second trip through every opening   \[ANSWER NEEDED BEFORE THE LOCKS GO ON\]\nLead time, their words: keying department said three weeks after the meeting — and move-in is the 14th/.test(doc),
     'call-the-keying: the impact line carries the sentence, the chip, the clock token and the lead time in THEIR words — and the heading prints ONCE');
  ok((doc.match(/THE DATE, AND WHAT HAPPENS WITHOUT IT/g) || []).length === 1, 'call-the-keying: the impact heading is not doubled (C3715 class)');
  ok(/\nFrom: R\. Tolliver — 559-555-0173\nCompany: Vantage Door & Hardware/.test(doc), 'call-the-keying: the sender block');
  ok(/I have to put these in by Fri, Sep 25 — what that day looks like with no answer is above, in my words/.test(doc), 'call-the-keying: the closing repeats the date the title carries and points at HIS impact line');
  ok(!/that's what they get anyway/.test(doc) && !/construction cores go in/.test(doc.split('\n\nReply with')[1] || ''), 'call-the-keying: the closing supplies no default the page cannot know (panel cut)');
  ok(!/\bpin\b/i.test(doc), 'call-the-keying: "pin" is not in the document — the keying department pins, the installer puts them in');
  ok(/not a keying schedule/.test(doc) && /I install to it/.test(doc), 'call-the-keying: the refusal is IN the document, one sentence, not the warn block');
  /* THE REFUSALS, measured on the artefact */
  ok(!/keyway/i.test(doc), 'call-the-keying: the document never says keyway');
  ok((doc.match(/bitting/gi) || []).length === 0, 'call-the-keying: the page itself never puts "bitting" in the document');
  ok(!/keyed[- ]alike/i.test(doc) && !/master key/i.test(doc), 'call-the-keying: no group and no master anywhere in the document');
  ok(!/\bmaster\b[^.\n]{0,20}\b(is|=|:)\s*[A-Z0-9]/.test(doc), 'call-the-keying: no master value');
  for (const re of CLAUSES) ok(!re.test(doc), 'call-the-keying: no-clock clause absent — ' + re.source.slice(0, 40));
  ok(/none of it is anybody agreeing to anything/.test(doc), 'call-the-keying: the closing says nothing here is anybody agreeing to anything');
  ok(!/if (i|we) (don'?t|do not) hear/i.test(doc), 'call-the-keying: no "if I don\'t hear back" construction');
  ok(/^4 open$/.test((await p.textContent('#count')) || ''), 'call-the-keying: the bar counts the open questions');
  ok(await overflow(p) <= 0, 'call-the-keying: no horizontal overflow at 390px, filled');

  /* Copy flashes, the draft survives a reload, Clear clears the ask and keeps the man */
  await p.click('#copy');
  await p.waitForTimeout(200);
  ok(/Copied|Select it/.test((await p.textContent('#copy')) || ''), 'call-the-keying: Copy answers (copied, or the non-secure fallback)');
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(500);
  const back = await preview(p);
  ok(/18 cylinders/.test(back) && /Fri, Sep 25/.test(back) && /ANSWER NEEDED BEFORE THE LOCKS GO ON/.test(back) && /three weeks after the meeting/.test(back), 'call-the-keying: the draft survives a reload — count, date, clock, lead time');
  await p.click('#clear');
  await p.waitForTimeout(300);
  const cleared = await preview(p);
  ok(!/18 cylinders/.test(cleared) && !/Fri, Sep 25/.test(cleared), 'call-the-keying: Clear actually clears');
  ok((await p.inputValue('[data-f="me"] input')) === 'R. Tolliver — 559-555-0173', 'call-the-keying: Clear never touches the man');
  ok(errs.length === 0, 'call-the-keying: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}
{
  const { p, ctx, errs } = await page('doors/call-the-keying.html', 320);
  ok(await overflow(p) <= 0, 'call-the-keying: no horizontal overflow at 320px');
  ok(errs.length === 0, 'call-the-keying@320: zero page errors');
  await ctx.close();
}

/* ── 2. THE HUB lists it, and the doorway version still stands ── */
{
  const { p, ctx, errs } = await page('doors/index.html');
  const n = await p.evaluate(() => document.querySelectorAll('a[href="call-the-keying.html"]').length);
  ok(n >= 1, `hub: Call The Keying is on the doors hub (${n} link(s))`);
  ok(errs.length === 0, 'hub: zero page errors');
  await ctx.close();
}
{
  const { p, ctx } = await page('doors/not-ready-to-hang.html');
  const has = await p.locator(`[data-f="stops"] input[data-name="Nobody's said what the keying is"]`).count();
  ok(has === 1, 'not-ready-to-hang: the doorway stop still stands — the ask did not swallow it');
  await ctx.close();
}

/* ── 3. THE SHELF: the turnover document no longer asks for bitting or a gap verdict ── */
{
  const { p, ctx, errs } = await page('doors/write-up.html');
  await p.fill('input[type="search"]', 'keying');
  await p.waitForTimeout(300);
  const first = p.locator('ul.lib li button').first();
  ok(await first.count() === 1, 'write-up: typing "keying" finds a document');
  const label = ((await first.textContent()) || '').trim();
  ok(/Keys, Cores/.test(label), `write-up: "keying" leads the turnover document ("${label.slice(0, 40)}")`);
  await first.click();
  await p.waitForTimeout(400);
  const block = (await p.textContent('pre.block')) || '';
  notes.push('  write-up block: ' + block.length + ' chars');
  ok(block.length > 3000, 'write-up: a real instruction block is emitted');
  ok(!/keyway and bitting/i.test(block) && !/by keyway/i.test(block), 'write-up: the turnover no longer asks for keys by keyway and bitting');
  ok(!/within tolerance/i.test(block) && !/gaps within/i.test(block), 'write-up: the turnover no longer asks for a gap verdict');
  ok(/never the bitting/i.test(block) || /never what is in it/i.test(block), 'write-up: the refusal replaced the ask, in the block a man pastes');
  ok(/certified inspector/i.test(block), 'write-up: the operated section says what it is not');
  ok(/watched close and latch/i.test(block), 'write-up: the labelled-leaf observation survived as an observation (panel)');
  ok(!/tag on the ring/i.test(block) && /by the count and the ring/i.test(block), 'write-up: keys by count and ring, never by the tag that carries the symbol (panel)');
  ok(/pulled construction cores went/i.test(block), 'write-up: the turnover asks where the pulled construction cores went (panel)');
  ok(errs.length === 0, 'write-up: zero page errors ' + errs.slice(0, 1));
  await ctx.close();
}

await b.close();
console.log(notes.join('\n'));
console.log(fails.join('\n'));
console.log(`\n_drive_doors — ${notes.filter(n => n.startsWith('PASS')).length} pass · ${fails.length} fail · base ${BASE}`);
process.exit(fails.length ? 1 : 0);
