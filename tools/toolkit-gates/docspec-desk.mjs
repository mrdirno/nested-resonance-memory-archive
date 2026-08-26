/**
 * THE DESK GATE — more than one document in one setup, driven through the real page.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. THE DESK (2026-08-16) lets a man put every document he
 * actually writes into ONE instruction block instead of keeping a Custom GPT
 * per document, which nobody does. To get there the composer was split: eight
 * blocks emitted once at the top, six emitted whole per document. That split is
 * the risk. Two things can go wrong and neither is visible in a screenshot:
 *
 *   1. THE ONE-DOCUMENT BLOCK DRIFTS. The single-document path is the shipped
 *      product on eleven trades. Extracting emitters out of it so a second
 *      document could reuse them is exactly the refactor that quietly changes a
 *      sentence, and the page looks identical either way.
 *   2. A DOCUMENT'S OWN RULES CHANGE WHEN IT RIDES IN A DESK. This is the
 *      2026-08-11 class again: a stand-alone record that picks up the DELTA
 *      continuity rule is a damage letter instructed to drop "anything already
 *      reported finished". In a desk the two rules sit in the same block, four
 *      hundred lines apart, which is the easiest place in the program to cross
 *      them.
 *
 * SO IT GOLDENS AGAINST ITSELF, IN-RUN — no committed fixture, nothing to
 * regenerate, and it cannot rot:
 *
 *   · pick A alone            → soloA
 *   · pick B alone            → soloB
 *   · pick A, add B           → desk
 *   · take B out again        → must be soloA BYTE FOR BYTE
 *   · desk's section for B    → its spine, its checks, its continuity rule and
 *                               its omitted lines must be soloB's, byte for byte
 *
 * The last one is the whole invariant in one sentence: adding a second document
 * does not change what the first one produces, and a document in a desk is the
 * same document.
 *
 * IT ALSO ASSERTS what only exists in the desk:
 *   · the ROUTER is present and names every document
 *   · the blend prohibition is present — given three formats and one dump, a
 *     model's failure is not picking wrong, it is welding two together
 *   · each shared block appears EXACTLY ONCE and each per-document block
 *     exactly N times (a duplicated DEFAULTS is a contradiction, not a typo)
 *   · continuity is right INSIDE each document's own section, checked against
 *     deltaOf() read out of the shipped engine
 *   · the cap holds at DocSpec.maxDocs
 *   · the setup steps name both chat rules when the desk is mixed — the step
 *     that tells him to paste his last one in is the step that corrupts a
 *     record written once, if it is given for the wrong document
 *
 * TRADES COME FROM DISK, never from a list here.
 *
 *   node tools/toolkit-gates/docspec-desk.mjs [base-url] [--only=<trade>]
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

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js')
                              && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name)
  .filter(t => !only || t === only)
  .sort();

const RULE = '----------------------------------------------------------------------';
const SHARED_ONCE = ['ROLE', 'WHICH ONE I AM ASKING FOR', 'DEFAULTS', 'OPERATING PRINCIPLES',
                     'ATTRIBUTION', 'INPUT HANDLING'];
const PER_DOC = ['WHAT THIS DOCUMENT IS FOR', 'CONTINUITY', 'VALIDATION', 'OUTPUT FORMAT',
                 'SECONDARY REQUESTS'];
const DELTA_TELL = 'covers the DELTA';
const ALONE_TELL = 'This document stands alone';

/* Runs INSIDE the page. Returns state rather than throwing — one bad trade must
   not blind the gate to the other ten. */
const DRIVE = (plan) => {
  const q = (s) => [...document.querySelectorAll(s)];
  const rowFor = (name) => q('.lib button').find(b => (b.querySelector('.nm') || {}).textContent === name);
  const block = () => (document.querySelector('pre.block') || {}).textContent || '';
  const steps = () => q('ol.steps li').map(l => l.textContent);
  const addBtn = () => q('.desk button.addrow')[0];
  const backBtn = () => q('button.chg')[0];
  const out = { err: null };

  try {
    // ---- solo A
    let r = rowFor(plan.a); if (!r) { out.err = `no library row for ${plan.a}`; return out; }
    r.click();
    out.soloA = block();
    out.soloASteps = steps();

    // ---- solo B (pick a different one)
    backBtn().click();
    r = rowFor(plan.b); if (!r) { out.err = `no library row for ${plan.b}`; return out; }
    r.click();
    out.soloB = block();

    // ---- back to A, then ADD B
    backBtn().click();
    rowFor(plan.a).click();
    addBtn().click();                                   // enter add mode; library reopens
    const rb = rowFor(plan.b);
    if (!rb) { out.err = 'add mode rendered no library row for ' + plan.b; return out; }
    rb.click();
    out.desk = block();
    out.deskSteps = steps();
    out.deskCount = window.DocSpec.picked().map(d => d.name);

    // ---- the cap: keep adding everything in the library
    const all = window.DocSpec.library().map(d => d.name);
    for (const n of all) { const b = rowFor(n); if (b && !b.disabled) b.click(); }
    out.capped = window.DocSpec.picked().length;
    out.max = window.DocSpec.maxDocs;

    // ---- back to exactly A, and the block must be soloA again
    while (window.DocSpec.picked().length > 1) {
      const name = window.DocSpec.picked()[1].name;
      const b = rowFor(name);
      if (!b) break;
      b.click();
      if (window.DocSpec.picked().some(d => d.name === name)) break;   // did not come out
    }
    const done = q('.desk button.addrow')[0];
    if (done) done.click();                              // leave add mode
    out.backToSolo = block();
    out.backCount = window.DocSpec.picked().length;
  } catch (e) {
    out.err = 'driver threw: ' + e.message + ' @ ' + (e.stack || '').split('\n')[1];
  }
  return out;
};

/* The slice of the desk that belongs to one document, header line excluded. */
function deskSection(desk, i, n, name) {
  const head = `DOCUMENT ${i + 1} OF ${n} — ${name.toUpperCase()}`;
  const at = desk.indexOf(head);
  if (at === -1) return null;
  const next = i + 2 <= n ? desk.indexOf(`DOCUMENT ${i + 2} OF ${n} — `, at) : -1;
  return desk.slice(at + head.length, next === -1 ? desk.length : next);
}

/* THE SPINE ONLY. The two header lines of an OUTPUT FORMAT carry the recipient,
   and an extra document deliberately carries its OWN — his typed "Goes to"
   answers for the one he was looking at when he typed it. Everything from the
   first ===== rule down is the part that must never differ. */
function spineOf(text) {
  const a = text.indexOf('OUTPUT FORMAT');
  if (a === -1) return null;
  const first = text.indexOf('=========================================', a);
  const end = text.indexOf('SECONDARY REQUESTS', a);
  if (first === -1 || end === -1) return null;
  return text.slice(first, end);
}
/* The VALIDATION check list, whichever shape it is in — one comma-joined line or
   one bullet per fact — read up to the bullet that always follows it. */
function factsChunk(t) {
  const m = String(t || '').match(/Before you write, check the input for:[\s\S]*?(?=\nWHEN SOMETHING ON THAT LIST|\n- No date given)/);
  return m ? m[0] : null;
}

function chunk(text, head, until) {
  const a = text.indexOf(head);
  if (a === -1) return null;
  const b = text.indexOf(until, a + head.length);
  return text.slice(a, b === -1 ? text.length : b);
}
const count = (hay, needle) => hay.split(needle).length - 1;
/* A HEADING IS A WHOLE LINE, and counting '\nROLE\n' misses the one at the very
   top of the block — which is every ROLE there has ever been. Line-exact, so
   first line and last line count like any other. */
const headings = (text, h) => text.split('\n').filter(l => l === h).length;

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await ctx.newPage();

let checked = 0, failing = 0;
const fails = [];

for (const trade of TRADES) {
  const url = `${BASE}/${trade}/write-up.html`;
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));

  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.lib button', { timeout: 15000 });

  /* THE PAIR IS CHOSEN TO BE THE HARD ONE: one document that reports deltas and
     one that stands alone, because crossing those two is the defect this gate
     exists for. A trade whose library is all one kind gets the first two. */
  const plan = await page.evaluate(() => {
    const L = window.DocSpec.library();
    const d = L.find(x => window.DocSpec.deltaOf(x));
    const s = L.find(x => !window.DocSpec.deltaOf(x));
    const pair = (d && s) ? [d, s] : L.slice(0, 2);
    return { a: pair[0] && pair[0].name, b: pair[1] && pair[1].name,
             mixed: !!(d && s),
             meta: pair.map(x => ({ name: x.name, delta: window.DocSpec.deltaOf(x),
                                    omits: window.DocSpec.omitLines(x) })) };
  });

  console.log(`\n${trade} — ${plan.a}  +  ${plan.b}${plan.mixed ? '  (mixed continuity)' : ''}`);
  if (!plan.a || !plan.b) {
    checked++; failing++;
    fails.push({ trade, bad: ['library has fewer than two documents — a desk cannot be built'] });
    continue;
  }

  const before = errs.length;
  const r = await page.evaluate(DRIVE, plan);
  const bad = [];
  if (r.err) bad.push(r.err);
  if (errs.length > before) bad.push('page error: ' + errs.slice(before).join(' | '));

  if (!r.err) {
    const n = 2;
    // ── 1. the solo block is not a desk
    if (/WHICH ONE I AM ASKING FOR|DOCUMENT 1 OF/.test(r.soloA)) {
      bad.push('one picked document emitted a DESK block — the router leaked into the single-document path');
    }
    // ── 2. the router
    if (!r.desk.includes('WHICH ONE I AM ASKING FOR')) bad.push('the desk carries no router');
    if (!r.desk.includes('NEVER blend two of them')) {
      bad.push('the desk does not forbid BLENDING — the one failure mode a multi-format prompt actually has');
    }
    [plan.a, plan.b].forEach(nm => {
      if (!r.desk.includes(nm)) bad.push(`the router never names "${nm}"`);
    });
    if (r.deskCount.length !== 2) bad.push(`adding one document produced ${r.deskCount.length} in the desk, not 2`);

    // ── 3. shared once, per-document N times
    SHARED_ONCE.forEach(h => {
      const c = headings(r.desk, h);
      if (c !== 1) bad.push(`shared block "${h}" appears ${c} time(s) in a 2-document desk, not exactly 1`);
      if (headings(r.soloA, h) !== (h === 'WHICH ONE I AM ASKING FOR' ? 0 : 1)) {
        bad.push(`shared block "${h}" appears ${headings(r.soloA, h)} time(s) in a ONE-document block`);
      }
    });
    PER_DOC.forEach(h => {
      const c = headings(r.desk, h);
      if (c !== n) bad.push(`per-document block "${h}" appears ${c} time(s) in a ${n}-document desk, not ${n}`);
    });
    if (count(r.desk, '\nDOCUMENT ') !== n) {
      bad.push(`the desk carries ${count(r.desk, '\nDOCUMENT ')} document headers, not ${n}`);
    }

    // ── 4. each document's own section is that document, unchanged
    const solos = { [plan.a]: r.soloA, [plan.b]: r.soloB };
    plan.meta.forEach((m, i) => {
      const sec = deskSection(r.desk, i, n, m.name);
      if (!sec) { bad.push(`no "DOCUMENT ${i + 1} OF ${n}" section for ${m.name}`); return; }

      // continuity, inside its OWN section
      const isDelta = sec.includes(DELTA_TELL), isAlone = sec.includes(ALONE_TELL);
      if (m.delta && !(isDelta && !isAlone)) {
        bad.push(`${m.name} reports deltas but its desk section does not carry the delta continuity rule`);
      }
      if (!m.delta && !(isAlone && !isDelta)) {
        bad.push(`${m.name} stands alone but its desk section tells the AI to write it as an UPDATE`
          + ' — the 2026-08-11 defect class, now inside a block that holds both rules at once');
      }
      // every omitted line reaches its own section
      const dropped = (m.omits || []).filter(o => !sec.includes(o.slice(0, 40)));
      if (dropped.length) {
        bad.push(`${dropped.length} of ${m.omits.length} omitted line(s) never reached ${m.name}'s desk section`);
      }
      // the spine, the checks and the continuity text are byte-identical to solo
      const solo = solos[m.name];
      const pairs = [
        ['OUTPUT FORMAT spine', spineOf(sec), spineOf(solo)],
        ['CONTINUITY', chunk(sec, '\nCONTINUITY\n', '\nVALIDATION\n'), chunk(solo, '\nCONTINUITY\n', '\nVALIDATION\n')],
        /* THE CHECK LIST IS A LIST NOW (2026-08-25), not one comma-joined line.
           This pair used to read `check the input for: .*` — a single-line match
           that silently stopped matching the moment the facts became bullets,
           and reported "could not read it out of both blocks" on all 14 trades.
           Anchored on the bullet that always follows instead, so it reads either
           shape and keeps asserting the thing that matters: a document's checks
           are byte-identical whether it rides alone or in a desk. */
        ['the facts it checks for', factsChunk(sec), factsChunk(solo)],
      ];
      pairs.forEach(([what, inDesk, inSolo]) => {
        if (inDesk == null || inSolo == null) { bad.push(`${m.name}: could not read ${what} out of both blocks`); return; }
        if (inDesk !== inSolo) {
          bad.push(`${m.name}: ${what} DIFFERS between its own setup and the desk`
            + ` — a document in a desk must be the same document`);
        }
      });
    });

    // ── 5. the cap
    if (r.capped > r.max) bad.push(`the desk grew to ${r.capped} documents past a cap of ${r.max}`);
    if (r.capped < 2) bad.push(`adding every document in the library left ${r.capped} in the desk`);

    // ── 6. taking the second one out gives back exactly what he had
    if (r.backCount !== 1) {
      bad.push(`taking the extras out left ${r.backCount} document(s) in the desk, not 1`);
    } else if (r.backToSolo !== r.soloA) {
      bad.push('adding a document and taking it out again did NOT restore the original block byte for byte');
    }

    // ── 7. the chat rule, when the desk is mixed
    if (plan.mixed) {
      const step = (r.deskSteps || [])[1] || '';
      if (!/One chat per job/i.test(step) || !/new chat each time/i.test(step)) {
        bad.push('the desk mixes a recurring report with a stand-alone record and the chat step gives ONE rule'
          + ` — "${step.slice(0, 80)}…"`);
      }
      [plan.a, plan.b].forEach(nm => {
        if (!step.includes(nm)) bad.push(`the mixed chat step does not say which rule "${nm}" takes`);
      });
    }
  }

  checked++;
  if (bad.length) {
    failing++;
    fails.push({ trade, bad });
    console.log('  ** FAIL');
    bad.forEach(b => console.log(`     ${b}`));
  } else {
    console.log(`  ok — router, ${plan.mixed ? 'mixed ' : ''}continuity, spines identical to solo, cap ${r.max}, removal restores byte-for-byte`);
  }
}

await browser.close();
console.log(`\nDESK GATE — ${checked} trade(s), ${failing} failing.`);
if (failing) {
  fails.forEach(f => console.log(`  ${f.trade}: ${f.bad.join(' | ')}`));
  process.exit(1);
}
console.log('THE DESK HOLDS. One document emits what it always did; a document in a desk is the same document.');
