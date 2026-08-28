/**
 * THE SAY-LIST GATE — the half of the write-up page a human reads, driven through
 * the real page on every document of every trade.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `facts` is authored per document — 214 documents, 661 distinct
 * strings — and for the whole life of this engine it reached exactly one reader:
 * the model, inside a 9,500-character block a man pastes into a Gem once. Nobody
 * ever looked at it, so it rotted where nothing could see it, and the rot shipped:
 *
 *   1. FIVE FRAMING DOCUMENTS AUTHOR NO `facts` AT ALL. The block read
 *      "Before you write, check the input for: ." — an empty check, live, on the
 *      one instruction that decides whether his report comes back full of holes.
 *      Every existing gate passed it: node --check passes (valid JS), the docspec
 *      gate passes (all eleven blocks present, non-empty), the mobile gate passes
 *      (a watertight layout around a broken sentence), a screenshot passes.
 *   2. A FACT MAY BE A SENTENCE. .join(", ") held while every author wrote short
 *      noun phrases and turned to mush the first time one did not:
 *      hvac/compressor-failure-report emitted a 600-character run-on in which
 *      "…amps at failure. Your numbers, nothing graded, What the oil…" reads as
 *      an instruction, then a fragment, then a new list item, in one line.
 *   3. THE HALT TAIL REPEATED THE AUTHOR'S OWN VERB. Fourteen documents across
 *      hvac, low-voltage and plumbing author "Only STOP AND ASK if …", and the
 *      engine appended "That is the ONLY reason to stop and ask me a question."
 *
 * So this gate does what nothing did before: it reads the say-list as a PERSON,
 * on every document, and it reads the VALIDATION block the same list feeds.
 *
 * WHAT IT ASSERTS, per document, per trade:
 *   · the say-list renders, and carries at least three lines. A document that
 *     tells a man to "just dump it" and names nothing is the empty check again,
 *     wearing a card.
 *   · the document authors `facts` OF ITS OWN. factsOf() falls back to the
 *     family so a page served from a branch that skipped this gate still says
 *     something — but the fallback is a BELT, and a gate that accepts it is
 *     measuring its own safety net. This assertion exists because the first
 *     draft of this file did exactly that: deleting framing's five `facts` back
 *     out, the state that actually shipped, left the gate GREEN.
 *   · the card's rendered lines and the emitted block's check bullets are the
 *     same strings, in the same order, line by line — DOM against composed
 *     text, which is the only reason the card can be trusted as the thing he
 *     says. (The first draft compared factsOf(d) to factsOf(d) via the DOM and
 *     could not fail; an adversarial pass caught it. A gate that compares the
 *     engine to itself proves nothing about what shipped.)
 *   · the block NEVER emits the empty check ("check the input for: ." with
 *     nothing under it) — defect 1, asserted directly.
 *   · every fact is emitted as its OWN line — defect 2. A fact containing a
 *     sentence-ending period is legal; a fact SHARING a line with another is not.
 *   · the halt bullet never says "stop and ask" twice — defect 3 — AND never
 *     loses its exclusivity to the fix for it. Suppressing the generic tail for
 *     an author who used the verb is lossless for 21 of the 22 halts that do,
 *     because they also say "only"; `gc/impact-notice` does not, and dropping
 *     the tail there made the one halt in the program with TWO conditions read
 *     as a licence to interrogate about anything. Adversarial pass, not this
 *     gate — which is why it is asserted now.
 *   · the card's cue and the BLOCK's CONTINUITY agree about the same document.
 *     Comparing the rendered cue to sayCue(d) was the second tautology; what is
 *     real is that a stand-alone record is never cued to drop what already
 *     finished while the block tells the AI the opposite (the 2026-08-11 class
 *     arriving on a new surface).
 *   · the CUSTOM path, all five families: it renders, each family gives a
 *     DIFFERENT list, the cue follows the family, and the seeded lines SAY they
 *     are a seed — `library()` never returns the custom document, so every
 *     assertion above is blind to the path search dumps people into.
 *   · the copy control copies EXACTLY what is on screen plus the omitted line,
 *     numbered the way the card numbers it, carrying none of the block's own
 *     headings. A copy button that quietly ships a different list than the one
 *     he read is worse than no copy button.
 *
 * Findings are collected, never thrown: a gate that dies on one document tells
 * you nothing about the other two hundred.
 */
import { createRequire } from 'node:module';
import { readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../..');
const BASE = process.env.TOOLKIT_BASE_URL || ('file://' + REPO);

/* TRADES COME FROM DISK, NEVER FROM A LIST HERE (2026-08-28). This file shipped
   with the roster typed out, at fourteen. `doors` landed as the fifteenth trade
   with a full write-up library and this gate never once ran on it — a hardcoded
   roster does not fail when a trade is added, it goes SILENTLY BLIND, and its
   own green is the thing that hides it. Every sibling gate in this directory
   (docspec-desk, docs-pool, find-noise, build-docsindex) already derives from
   disk; this was the one that did not. The negative control is the roster
   itself: delete a trade directory and the count drops. */
const TRADES = readdirSync(REPO + '/', { withFileTypes: true })
  .filter(d => d.isDirectory()
            && existsSync(REPO + '/' + d.name + '/trade.js')
            && existsSync(REPO + '/' + d.name + '/docs.js')
            && existsSync(REPO + '/' + d.name + '/write-up.html'))
  .map(d => d.name)
  .sort();
if (!TRADES.length) { console.error('FAIL: no trade with a write-up library found under ' + REPO); process.exit(1); }

/* Runs INSIDE the page. Picks one document and reports what BOTH readers got. */
const EXERCISE = (name) => {
  const out = { err: null };
  try {
    const btn = [...document.querySelectorAll('.lib button')]
      .find(b => (b.querySelector('.nm') || {}).textContent === name);
    if (!btn) { out.err = 'no library row rendered for this document'; return out; }
    btn.click();
  } catch (e) { out.err = 'click threw: ' + e.message; return out; }
  try {
    const say = document.querySelector('.say');
    out.hasSay = !!say;
    out.lis = say ? [...say.querySelectorAll('li')].map(l => l.textContent) : [];
    out.cue = say ? (say.querySelector('.cue') || {}).textContent || '' : '';
    out.copyLabel = say ? (say.querySelector('.saycopy') || {}).textContent || '' : '';
    out.block = (document.querySelector('pre.block') || {}).textContent || '';
    const d = window.DocSpec.library().find(x => x.name === name);
    out.facts = d ? window.DocSpec.factsOf(d) : [];
    out.ownFacts = d ? ((d.facts || []).length) : 0;
    out.omits = d ? window.DocSpec.omitLines(d) : [];
    out.delta = d ? window.DocSpec.deltaOf(d) : null;
    out.expectCue = d ? window.DocSpec.sayCue(d) : '';
  } catch (e) { out.err = 'introspection threw: ' + e.message; }
  return out;
};

/* THE COPY CONTROL, DRIVEN. Not "does a button exist" — what does it put on the
   clipboard. Read back through a stubbed clipboard so the assertion is on the
   STRING, which is the thing a foreman forwards to three leads. */
const DRIVE_COPY = () => new Promise((resolve) => {
  let captured = null;
  const real = navigator.clipboard;
  try {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: (t) => { captured = t; return Promise.resolve(); } }
    });
  } catch (e) { resolve({ err: 'could not stub clipboard: ' + e.message }); return; }
  const b = document.querySelector('.saycopy');
  if (!b) { resolve({ err: 'no copy control' }); return; }
  b.click();
  setTimeout(() => {
    try { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: real }); } catch (e) {}
    resolve({ text: captured });
  }, 60);
});

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await ctx.newPage();

let checked = 0, failing = 0, docs = 0;
const fails = [];
const noOwn = [];
const bump = (t, id, msg) => { failing++; fails.push(`${t}/${id}: ${msg}`); };

for (const trade of TRADES) {
  const url = `${BASE}/${trade}/write-up.html`;
  const errs = [];
  const onErr = e => errs.push(e.message);
  page.on('pageerror', onErr);
  await page.goto(url);
  await page.waitForTimeout(250);
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(250);

  const lib = await page.evaluate(() => window.DocSpec.library().map(d => ({ id: d.id, name: d.name })));
  if (!lib.length) { bump(trade, '-', 'library rendered empty'); page.off('pageerror', onErr); continue; }

  for (const doc of lib) {
    docs++;
    const r = await page.evaluate(EXERCISE, doc.name);
    if (r.err) { bump(trade, doc.id, r.err); continue; }

    /* 1. THE CARD EXISTS AND SAYS SOMETHING */
    checked++;
    if (!r.hasSay) { bump(trade, doc.id, 'no say-list rendered'); continue; }
    checked++;
    if (r.lis.length < 3) bump(trade, doc.id, `say-list has ${r.lis.length} line(s) — under three it is the empty check wearing a card`);

    /* THE BELT IS NOT ALLOWED TO BE LOAD-BEARING, AND THIS GATE'S OWN NEGATIVE
       CONTROL IS WHY IT SAYS SO. First pass, this was a printed NOTE rather than
       a failure. Deleting framing's five `facts` back out — the exact state that
       shipped — left the gate GREEN, because factsOf()'s family fallback caught
       it before any assertion could see it. A gate measuring its own safety net
       gates nothing (§SCARS 2026-08-24). The fallback exists for a page served
       from a branch that skipped this file; HERE, a document that names nothing
       of its own is the defect, and the family's five generic lines are not an
       answer to "what do I say about THIS document". */
    checked++;
    if (!r.ownFacts) {
      noOwn.push(`${trade}/${doc.id}`);
      bump(trade, doc.id, 'authors NO facts of its own — the block shipped "check the input for: ." and the card would name nothing. The family fallback is the belt, not a substitute for authoring');
    }

    /* 2. BOTH READERS SEE THE SAME LIST — CARD DOM vs COMPOSED BLOCK TEXT.
       THE FIRST DRAFT OF THIS WAS A TAUTOLOGY AND AN ADVERSARIAL PASS CALLED IT.
       It compared `.say li` (written by renderSay from factsOf(d)) against
       factsOf(d) called by the test — one function, one input, and textContent
       round-trips a string exactly, so it could not fail short of a browser bug,
       while this file's header claimed it proved the card and the block agree.
       The two readers are the DOM and the COMPOSED STRING, so those are what get
       compared: what a man reads on the page against what the AI is told to check
       for, line by line, not by count. */

    /* 3. THE EMPTY CHECK IS DEAD (defect 1) */
    checked++;
    if (/check the input for:\s*\.?\s*\n\s*\n/.test(r.block) || /check the input for:\s*\.\s*$/m.test(r.block)) {
      bump(trade, doc.id, 'the block emits an EMPTY check line — "check the input for:" with nothing under it');
    }

    /* 4. ONE FACT, ONE LINE (defect 2) — AND THE SAME LINES AS THE CARD */
    checked++;
    const vm = r.block.match(/Before you write, check the input for:\n([\s\S]*?)\n\nWHEN SOMETHING ON THAT LIST/);
    if (!vm) bump(trade, doc.id, 'VALIDATION check list not found in the emitted block');
    else {
      const lines = vm[1].split('\n').filter(Boolean);
      const bad = lines.filter(l => !l.startsWith('- '));
      if (bad.length) bump(trade, doc.id, `${bad.length} check line(s) not bulleted: ${JSON.stringify(bad[0]).slice(0, 80)}`);
      const blockFacts = lines.map(l => l.replace(/^- /, ''));
      checked++;
      if (blockFacts.length !== r.lis.length) {
        bump(trade, doc.id, `the card shows ${r.lis.length} line(s), the block checks ${blockFacts.length} — a fact that shares a line is a fact an AI can drop half of`);
      } else {
        checked++;
        const diverged = blockFacts.map((b, i) => [b, r.lis[i]]).filter(([b, c]) => b !== c);
        if (diverged.length) {
          bump(trade, doc.id, `line ${blockFacts.indexOf(diverged[0][0]) + 1} differs between the two readers — card ${JSON.stringify(diverged[0][1]).slice(0, 60)} vs block ${JSON.stringify(diverged[0][0]).slice(0, 60)}`);
        }
      }
    }

    /* 4b. THE RULES ARE NOT MISTAKEN FOR MORE FACTS. Bulleting the facts made
       them typographically identical to the three missing-input RULES that
       follow, and one blank line is not a boundary. */
    checked++;
    if (r.block.indexOf('WHEN SOMETHING ON THAT LIST IS NOT IN MY INPUT:') === -1) {
      bump(trade, doc.id, 'the missing-input rules follow the fact list with nothing separating them — a model reads "- No date given: use today\'s date" as another thing to check for');
    }

    /* 5. THE HALT NEVER SAYS IT TWICE (defect 3) */
    checked++;
    /* THE HALT IS THE SECOND OF THREE BULLETS, ALWAYS — so take it by POSITION,
       never by guessing its first word. The first draft matched an alternation
       of opening words (Only|Never|The notes|He wants|…) and therefore never saw
       `plumbing/service-writeup`, whose author opens with "Stop and ask on two
       things only:". A gate that identifies a line by how its authors happen to
       start their sentences goes blind the day one of them starts differently,
       and it goes blind SILENTLY — the assertion simply does not run. */
    const grp = r.block.match(/WHEN SOMETHING ON THAT LIST IS NOT IN MY INPUT:\n([\s\S]*?)\n\n/);
    const bullets = grp ? grp[1].split('\n').filter(l => l.startsWith('- ')) : [];
    checked++;
    if (bullets.length !== 3) bump(trade, doc.id, `the missing-input group has ${bullets.length} bullet(s), not 3 — the halt cannot be read by position`);
    const haltLine = bullets[1] || '';
    if (haltLine) {
      const n = (haltLine.match(/stop and ask/gi) || []).length;
      if (n > 1) bump(trade, doc.id, `the halt bullet says "stop and ask" ${n} times in one sentence`);
      /* AND IT STILL HAS TO BE EXCLUSIVE. Suppressing the generic tail for an
         author who already used the verb is lossless only where he also said
         "only" — 21 of the 22 do. `gc/impact-notice` uses the verb, names two
         conditions and never claims exclusivity, and the first draft of the
         suppression silently turned the one halt in the program with two
         conditions into a licence to ask about anything (found by an adversarial
         pass, not by this gate — which is why it is now asserted). The bullet
         must claim exclusivity in SOME words, whoever supplied them. */
      checked++;
      if (!/\bonly\b|\bnever halt\b/i.test(haltLine)) {
        bump(trade, doc.id, `the halt bullet names a condition but never says it is the ONLY one — "${haltLine.slice(2, 70)}…"`);
      }
    }

    /* 6. THE CUE MATCHES THE DOCUMENT'S OWN CONTINUITY RULE.
       The `r.cue !== r.expectCue` compare that stood here was the second
       tautology — sayCue(d) rendered, against sayCue(d) called. What is NOT a
       tautology is the direction: a stand-alone record must never be cued to
       drop what already finished, and the cue on the card must agree with the
       CONTINUITY block the AI is given, which is composed independently. */
    checked++;
    const cueSaysDelta = /CHANGED since the last one/.test(r.cue);
    const blockSaysDelta = /Each one covers the DELTA/.test(r.block);
    if (cueSaysDelta !== blockSaysDelta) {
      bump(trade, doc.id, `the card cues ${cueSaysDelta ? 'a DELTA' : 'a whole record'} and the block's CONTINUITY says the opposite — the man and the AI are being told different things about the same document`);
    }
    checked++;
    if (!r.delta && /CHANGED since the last one/.test(r.cue)) {
      bump(trade, doc.id, 'a STAND-ALONE record is cued with "only what changed" — the record somebody reads years later, told to drop its own facts');
    }
  }

  /* 6b. THE CUSTOM PATH, ALL FIVE FAMILIES. library() never returns the custom
        pseudo-document, so every assertion above is blind to the path a man
        reaches when what he has to write is not in the list — which is where
        search dumps people, and which renders a FAMILY's generic facts under a
        confident heading. Asserted here: it renders, each family gives a
        DIFFERENT list (five families seeding one list is one hardcoded sentence
        wearing a heading), the cue follows the family, and the seed says it is
        a seed. */
  const cust = await page.evaluate(() => {
    const out = [];
    const open = [...document.querySelectorAll('button')].find(b => /Not in the list/i.test(b.textContent));
    if (!open) return { err: 'no custom-path control' };
    open.click();
    const inp = document.querySelector('#app input[type=text]');
    if (!inp) return { err: 'custom path rendered no name field' };
    inp.value = 'Confined space entry and rescue-plan sign-off';
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    const fams = Object.keys(window.DocSpec.families);
    for (let i = 0; i < fams.length; i++) {
      const rs = [...document.querySelectorAll('#app input[type=radio]')];
      if (!rs[i]) return { err: `family #${i + 1} has no control` };
      if (!rs[i].checked) rs[i].click();
      const say = document.querySelector('.say');
      if (!say) return { err: `family ${fams[i]}: no say-list on the custom path` };
      out.push({
        fam: fams[i],
        lis: [...say.querySelectorAll('li')].map(l => l.textContent),
        cue: (say.querySelector('.cue') || {}).textContent || '',
        seed: (say.querySelector('.seedwhy') || {}).textContent || ''
      });
    }
    return { out };
  });
  checked++;
  if (cust.err) bump(trade, '__custom', cust.err);
  else {
    cust.out.forEach(c => {
      checked++;
      if (c.lis.length < 3) bump(trade, '__custom', `family ${c.fam}: say-list has ${c.lis.length} line(s)`);
      checked++;
      if (!c.seed) bump(trade, '__custom', `family ${c.fam}: seeded family facts shown with no line saying they are a seed — the omission tick two controls over discloses exactly this`);
    });
    checked++;
    const sigs = new Set(cust.out.map(c => c.lis.join('|')));
    if (sigs.size < 3) bump(trade, '__custom', `${cust.out.length} families produce only ${sigs.size} distinct say-list(s) — a family that does not change the list is a hardcoded sentence wearing a heading`);
    checked++;
    const cueSigs = new Set(cust.out.map(c => c.cue));
    if (cueSigs.size < 2) bump(trade, '__custom', 'every family gets the same continuity cue on the custom path');
  }
  /* Back to a clean state before the copy check below. */
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(200);

  /* 7. THE COPY CONTROL SHIPS WHAT HE READ — once per trade, on the last picked
        document, which is the state the loop above leaves the page in. */
  const last = lib[lib.length - 1];
  const rr = await page.evaluate(EXERCISE, last.name);
  const cp = await page.evaluate(DRIVE_COPY);
  checked++;
  if (cp.err) bump(trade, last.id, 'copy control: ' + cp.err);
  else if (typeof cp.text !== 'string' || !cp.text) bump(trade, last.id, 'copy control put nothing on the clipboard');
  else {
    const want = rr.lis.concat(rr.omits);
    const missing = want.filter(l => cp.text.indexOf(l) === -1);
    if (missing.length) bump(trade, last.id, `copy omits ${missing.length} line(s) the card shows: ${JSON.stringify(missing[0]).slice(0, 80)}`);
    if (cp.text.indexOf(last.name) === -1) bump(trade, last.id, 'the copied list never names the document it is for');
    /* It must be a LIST he can read, not the block. If the copy ever grows past
       what is on the card plus the omitted line, it has become a second block. */
    /* A LINE COUNT IS THE WEAK HALF OF THIS ASSERTION — the strong half is that
       none of the BLOCK's own headings can appear. The copy is a text message,
       not a setup; if it ever grows an OUTPUT FORMAT it has quietly become the
       thing the bar at the bottom already copies. */
    const lines = cp.text.split('\n').filter(Boolean);
    if (lines.length > want.length + 5) bump(trade, last.id, `copy carries ${lines.length} lines for a ${want.length}-line card — it has become a second block`);
    const blockOnly = ['OUTPUT FORMAT', 'OPERATING PRINCIPLES', 'INPUT HANDLING', 'VALIDATION', 'ATTRIBUTION']
      .filter(hdr => cp.text.indexOf(hdr) !== -1);
    if (blockOnly.length) bump(trade, last.id, `copy carries the block's own ${blockOnly[0]} heading — this is a text message, not a setup`);
    /* Every line he reads is numbered; every line he sends must be too, or the
       two are not the same list. */
    const unnumbered = want.filter(l => cp.text.indexOf(l) !== -1 && !new RegExp('\\n\\d+\\. ' + l.slice(0, 24).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test('\n' + cp.text));
    if (unnumbered.length) bump(trade, last.id, `${unnumbered.length} copied line(s) are not numbered the way the card numbers them`);
  }

  page.off('pageerror', onErr);
  if (errs.length) bump(trade, '-', `page errors: ${errs.slice(0, 2).join(' | ')}`);
}

await browser.close();

console.log(`\nSAY-LIST GATE — ${TRADES.length} trades / ${docs} documents / ${checked} checks / ${failing} failing`);
if (noOwn.length) {
  console.log(`\n  ${noOwn.length} document(s) author NO facts of their own and fell back to their family's:`);
  noOwn.forEach(n => console.log('   · ' + n));
}
if (failing) { console.log('\nFAILING:'); fails.forEach(f => console.log('  ✗ ' + f)); process.exit(1); }
console.log('  ✓ every document names what to say, and both readers see the same list.\n');
