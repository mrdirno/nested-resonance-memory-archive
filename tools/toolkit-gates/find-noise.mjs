/**
 * THE DROPPED-WORD GATE — when this engine deletes one of his words, does the
 * page he is looking at say so?
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `shared/find.js` rule 1 removes any query token that matches
 * nothing on the surface and answers with what is left. For "template" and
 * "form" that is the whole point. For a CONTENT word it is a lie by omission,
 * and the shape of this corpus is that the token which SURVIVES is the generic
 * head noun ("note", "letter", "record", "strap") while the token DELETED is the
 * one that discriminates ("inspection", "AHJ", "nuisance", "EMT") — because a
 * generic noun is on many rows and a modifier is on none.
 *
 * Measured 2026-08-26 by driving 21,372 cross-surface searches through the real
 * pages: 3,631 came back mode="exact" with a non-empty `noise`, and 3,409 of
 * those (93.9%) kept HALF OR LESS of what was typed. One surface said so —
 * commons/commons.js, four inline lines. The other 26 said nothing at all.
 *
 * WHAT THIS GATE ASSERTS. Every probe is built from the surface's OWN strings
 * plus a token proven absent from that surface, so a row added next month is
 * tested the day it lands and no probe is hand-written:
 *
 *   N1  SAID          a name of this surface's own + one proven-absent word ->
 *                     the page NAMES that word back. This is the defect.
 *   N2  SILENT        the same name with NO added word -> no sentence at all.
 *                     The good case may not move.
 *   N3  HIS CASE      the added word typed in CAPITALS comes back in CAPITALS.
 *                     Handing a man a mangled copy of his own word is a weaker
 *                     admission than handing him the word.
 *   N4  PLURAL        one dropped word says "that word"; two say "those words".
 *   N5  ONCE          a word he repeated is named ONCE, not twice.
 *   N6  QUIET ON NONE  a query where NOTHING landed stays silent — the heading
 *                     already said so and saying it twice reads as broken.
 *   N7  NOT A HEDGE   adding a dropped word may not change which row LEADS.
 *                     The answer is still his; only the admission is new.
 *   N8  WHOLE WORD    an accented word comes back WHOLE. `norm()` keeps only
 *                     [a-z0-9], so it shreds "café" to the token `caf` — and
 *                     two trades ship a Spanish vocabulary block on purpose.
 *                     Handing that man "caf" dressed up as his own word is a
 *                     worse admission than the mangled token was.
 *   N9  HIS CURSOR    the word he is STILL TYPING is not named. A one-character
 *                     token can only match exactly, so the first letter of every
 *                     word after the first is noise for one keystroke: naming it
 *                     makes the line appear on "drill b" and vanish on "drill
 *                     bi". It IS named the moment a separator says he is done.
 *
 * N1, N3, N4 and N5 are RED against the engine as it shipped (verified by
 * restoring the previous shared/find.js + the three renderers, not by argument).
 * N2, N6 and N7 are green on both and are here to catch the overcorrection.
 *
 *   node tools/toolkit-gates/find-noise.mjs [base-url]
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
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name).sort();

/* The twelve tap-to-tick lists are named in each trade's registry, not by a
   filename convention — a hard list here would go stale the day a trade adds
   one, so it is derived from what actually loads the engine. */
const PICK = [];
for (const t of readdirSync(ROOT, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name)) {
  let files = [];
  try { files = readdirSync(ROOT + t); } catch { continue; }
  for (const f of files) {
    if (!f.endsWith('.html')) continue;
    const { readFileSync } = await import('fs');
    const src = readFileSync(ROOT + t + '/' + f, 'utf8');
    if (/pickfilter\.js/.test(src)) PICK.push(t + '/' + f);
  }
}
PICK.sort();

const SURFACES = TRADES.map(t => ({ url: t + '/write-up.html', kind: 'docspec', id: t + '/write-up' }))
  .concat(PICK.map(p => ({ url: p, kind: 'pick', id: p.replace('.html', '') })))
  .concat(['index', 'tips', 'names'].map(n => ({ url: 'commons/' + n + '.html', kind: 'commons', id: 'commons/' + n })));

/* ── the three adapters. Each hands back the same shape, so every probe below
      is written once and does not know which surface it is standing on. ────── */
const AD = {
  docspec: {
    input: `document.querySelector('input[type=search][aria-label="Search documents"]')`,
    names: `window.DocSpec.library().map(function(d){return d.name;})`,
    /* The note is marked by ATTRIBUTE, not by class: every other gate on this
       page finds the leading row by skipping `grp` and `none`. */
    read: `(function(){var u=document.querySelector('ul.lib');
      return { note:(u.querySelector('li[data-drop]')||{}).textContent||'',
               lead:(u.querySelector('li .nm')||{}).textContent||'' };})()`
  },
  pick: {
    input: `document.querySelector('input[type=search]')`,
    names: `[].map.call(document.querySelectorAll('#list li.item .name'),function(e){return (e.textContent||'').replace(/\\s+/g,' ').trim();}).filter(Boolean)`,
    read: `(function(){var l=document.querySelector('#nomatch, .pf-none');
      var v=[].filter.call(document.querySelectorAll('#list li.item'),function(e){return !e.classList.contains('is-hidden');});
      return { note:l?(l.textContent||''):'', lead:v.length?((v[0].querySelector('.name')||{}).textContent||''):'' };})()`
  },
  commons: {
    input: `document.getElementById('q')`,
    /* Each commons surface loads its own row file; `names.js` is loaded by all
       three as the alias index, so it is only the source when it is the only
       one present. Reading a global that does not exist is how this adapter
       returned [] and quietly covered 26 of the 29 it printed. */
    names: `((window.COMMONS_GEAR||window.COMMONS_TIPS||window.COMMONS_NAMES||[]).map(function(r){return r.n;}))`,
    read: `(function(){var s=document.querySelectorAll('#sections section.sec');var h=s[s.length-1];
      if(!h)return {note:'',lead:''};
      return { note:(h.querySelector('.secnote')||{}).textContent||'',
               lead:((h.querySelector('li.item .nm')||{}).textContent||'').replace(/\\s+/g,' ').trim() };})()`
  }
};

let checked = 0, failing = 0;
const seen = {};
/* NO SILENT CAPS. This gate printed "29 surfaces" while its commons adapter read
   a global no page defines, so three of them contributed zero checks and nothing
   said so. A surface that runs no probe is a RED, not a quiet pass. */
const covered = {};
const fail = (cls, m) => { console.log('  FAIL  ' + cls + '  ' + m); failing++; seen[cls] = (seen[cls] || 0) + 1; };
const ok = (cls) => { checked++; seen[cls] = seen[cls] || 0; };

const SAYS = /Ignored\s+“/;
const words = (note) => {
  const m = note.match(/Ignored\s+((?:“[^”]*”(?:,\s*)?)+)/);
  if (!m) return null;
  return (m[1].match(/“([^”]*)”/g) || []).map(s => s.slice(1, -1));
};

const browser = await chromium.launch();
const page = await browser.newPage();
const errs = [];
page.on('pageerror', e => errs.push(e.message));

/* Every alphanumeric token that appears ANYWHERE in any surface's own names, so
   a probe word can be proven absent from a surface rather than assumed absent. */
const surfaceToks = {};
const allNames = new Set();
for (const s of SURFACES) {
  await page.goto(BASE + '/' + s.url, { waitUntil: 'load' });
  const ns = await page.evaluate(AD[s.kind].names);
  ns.forEach(n => allNames.add(n));
  surfaceToks[s.id] = new Set();
  ns.forEach(n => String(n).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(' ')
    .forEach(t => t && surfaceToks[s.id].add(t)));
}
/* A word is only usable as a probe if the ENGINE agrees it lands nowhere, which
   is a stronger condition than "not in a name" — prose fields are indexed too. */
const POOL = [...new Set([...allNames].flatMap(n =>
  String(n).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(' ')))]
  .filter(t => t.length >= 4 && !/^\d+$/.test(t));

console.log('THE DROPPED-WORD GATE  ·  ' + SURFACES.length + ' surfaces  ·  base ' + BASE + '\n');

for (const s of SURFACES) {
  await page.goto(BASE + '/' + s.url, { waitUntil: 'load' });
  const r = await page.evaluate(({ ad, pool }) => {
    const si = eval(ad.input);
    if (!si) return { err: 'no search input' };

    /* THE ENGINE PICKS THE PROBE WORDS, NOT THE GATE. "not in any name" is the
       weaker condition — prose fields are indexed too, and a word this surface
       carries only in a description would produce a false red. So the page's own
       index is captured off a real keystroke and asked directly: mode "none" is
       the engine reporting that every token reached nothing. */
    /* ONE KEYSTROKE BUILDS MORE THAN ONE INDEX, and taking whichever ran LAST
       took the wrong one. Every commons surface searches its own rows AND the
       cross-page name table (commons/commons.js `handoff.ix`), so on three of
       the surfaces below every word this gate "proved absent" was proved absent
       from the alias table instead of from the page under test — a probe word
       that may be sitting in plain sight on the row being probed. Found
       2026-08-28 while building find-honesty.mjs classes H and J on the same
       capture, and swept into both files in the same cycle. All of them are kept
       and the one holding THIS surface's own first name is the one used, which
       is a fact about the index rather than an assumption about call order. */
    const seen = [];
    const real = window.Find.search;
    window.Find.search = function (ix, q) { if (seen.indexOf(ix) === -1) seen.push(ix); return real.apply(this, arguments); };
    si.value = 'zz'; si.dispatchEvent(new Event('input', { bubbles: true }));
    window.Find.search = real;
    si.value = ''; si.dispatchEvent(new Event('input', { bubbles: true }));
    const own = window.Find.norm((eval(ad.names) || [])[0] || '');
    /* CONTAINS, not equals: shared/pickfilter.js indexes the whole <li> text as
       its primary field, so the row's own name is a SUBSTRING of it and never the
       string itself. Equality passed on the document libraries and the commons
       and skipped all thirteen tap-to-tick lists. */
    const holds = (ix) => !!own && ix.rows.some(r => r.f[ix.primary].whole.some(w => w.indexOf(own) !== -1));
    const IX = seen.filter(holds)[0] || null;
    if (!IX) return { err: 'index not captured' };
    /* Kept for the N9/N10 pair below, which has to ask the engine whether it
       DROPS a fragment before that fragment can test the hold-back. */
    window.__NIX = IX;

    const absent = [];
    for (const w of pool) {
      if (absent.length >= 24) break;
      if (real(IX, w).mode === 'none') absent.push(w);
    }
    return { names: eval(ad.names), absent: absent };
  }, { ad: AD[s.kind], pool: POOL });
  if (r && r.err) { console.log('  SKIP  ' + s.id + ' — ' + r.err); continue; }
  if (r.absent.length < 2) { console.log('  SKIP  ' + s.id + ' — no two words this surface does not carry'); continue; }

  const names = r.names.slice(0, 6);
  const absent = r.absent;

  for (const nm of names) {
    /* Two proven-absent words, and they must also be absent from EACH OTHER'S
       page-level index once the engine has spoken — checked live below. */
    const cand = absent.filter(w => !String(nm).toLowerCase().includes(w));
    if (cand.length < 2) continue;
    const res = await page.evaluate(({ ad, nm, w1, w2 }) => {
      const si = eval(ad.input);
      const read = (q) => { si.value = q; si.dispatchEvent(new Event('input', { bubbles: true })); return eval(ad.read); };
      return {
        base:   read(nm),
        one:    read(nm + ' ' + w1 + ' '),
        oneUp:  read(nm + ' ' + w1.toUpperCase() + ' '),
        two:    read(nm + ' ' + w1 + ' ' + w2 + ' '),
        dupe:   read(nm + ' ' + w1 + ' ' + w1 + ' '),
        junk:   read('qzxjv wkbfp')
      };
    }, { ad: AD[s.kind], nm, w1: cand[0], w2: cand[1] });

    const w1 = cand[0], w2 = cand[1];
    const at = s.id + '  “' + nm + '”';

    // N2 SILENT — the good case may not move.
    if (SAYS.test(res.base.note)) fail('N2', at + ' — its own name alone printed “' + res.base.note.trim() + '”');
    else ok('N2');

    // N1 SAID + N3 HIS CASE + N4 PLURAL + N5 ONCE + N7 NOT A HEDGE.
    const wOne = words(res.one.note);
    if (!wOne) { fail('N1', at + ' + “' + w1 + '” — page said nothing. note=' + JSON.stringify(res.one.note)); }
    else if (wOne.map(x => x.toLowerCase()).indexOf(w1) === -1) fail('N1', at + ' + “' + w1 + '” — named ' + JSON.stringify(wOne) + ' instead');
    else ok('N1');

    if (wOne) {
      if (!/nothing here uses that word\./.test(res.one.note)) fail('N4', at + ' — one dropped word did not say “that word”: ' + JSON.stringify(res.one.note.trim()));
      else ok('N4');
    }
    const wUp = words(res.oneUp.note);
    if (wUp && wUp.indexOf(w1.toUpperCase()) === -1) fail('N3', at + ' + “' + w1.toUpperCase() + '” — came back as ' + JSON.stringify(wUp));
    else if (wUp) ok('N3');

    const wTwo = words(res.two.note);
    if (wTwo && wTwo.length >= 2) {
      if (!/nothing here uses those words\./.test(res.two.note)) fail('N4', at + ' — two dropped words did not say “those words”: ' + JSON.stringify(res.two.note.trim()));
      else ok('N4');
    }
    const wDup = words(res.dupe.note);
    if (wDup) {
      const c = wDup.map(x => x.toLowerCase()).filter(x => x === w1).length;
      if (c > 1) fail('N5', at + ' + “' + w1 + '” twice — named it ' + c + ' times: ' + JSON.stringify(res.dupe.note.trim()));
      else ok('N5');
    }
    if (wOne && res.base.lead && res.one.lead !== res.base.lead)
      fail('N7', at + ' — adding a word that matches nothing MOVED the answer: “' + res.base.lead + '” -> “' + res.one.lead + '”');
    else ok('N7');

    // N6 QUIET ON NONE.
    if (SAYS.test(res.junk.note)) fail('N6', s.id + ' — a query where nothing landed still printed “' + res.junk.note.trim() + '”');
    else ok('N6');

    /* N8 + N9 exist because a three-lens read found both classes on the shipped
       draft while every probe above stayed green. The accented probe is built by
       putting an accent INTO a proven-absent word, so it is still derived from
       the surface's own data and still proven absent by the engine. */
    const acc = await page.evaluate(({ ad, nm, w1 }) => {
      const si = eval(ad.input);
      const read = (q) => { si.value = q; si.dispatchEvent(new Event('input', { bubbles: true })); return eval(ad.read); };
      /* An accent glued to a word the engine has already proven absent: norm()
         shreds it back to that same token, so what the sentence prints is a
         direct test of whether the whole word was recovered. */
      const a = 'ñ' + w1;
      return { word: a, acc: read(nm + ' ' + a + ' '), mid: read(nm + ' ' + w1), done: read(nm + ' ' + w1 + ' ') };
    }, { ad: AD[s.kind], nm, w1 });

    const wAcc = words(acc.acc.note);
    if (!wAcc) fail('N8', at + ' + “' + acc.word + '” — page said nothing');
    else if (wAcc.indexOf(acc.word) === -1)
      fail('N8', at + ' + “' + acc.word + '” — came back shredded as ' + JSON.stringify(wAcc));
    else ok('N8');

    /* ── N9 + N10 ARE ONE PAIR, AND THE NUMBER BETWEEN THEM IS THE ENGINE'S ──
       shared/find.js holds a trailing token back WHILE IT COULD STILL BE A WORD
       IN PROGRESS, and names it once it cannot be one. Until 2026-09-03 there was
       no "once": the hold-back ran to the next separator, and because `say` empty
       also makes rule 6's clause vacuous, 453 answers that named a document the
       page does not carry went out labelled EXACT with no sentence at all — the
       failure rule 6 exists to end, through the door rule 6 left open.
       `Find.underThumb` is where that line now sits, so this gate probes one
       character either side of the ENGINE'S constant rather than a 3 written
       here, and moving the constant re-points both probes. A fragment is only a
       test of the hold-back if the engine actually DROPS it — at two characters
       the prefix path is live, so "da" on a page that carries "damage" is a word
       this page has — so every candidate is put to the engine first. */
    const thr = await page.evaluate(({ ad, nm, w1, pool }) => {
      const si = eval(ad.input);
      const read = (q) => { si.value = q; si.dispatchEvent(new Event('input', { bubbles: true })); return eval(ad.read); };
      const U = window.Find.underThumb;
      const drops = (frag) => {
        const r = window.Find.search(window.__NIX, nm + ' ' + frag);
        return !!r && (r.noise || []).indexOf(window.Find.norm(frag)) !== -1;
      };
      /* ANY proven-absent word will do for the under-the-line probe, and taking
         only the first one skipped four surfaces that happen to carry a word
         starting "da" — the head has to be one the ENGINE drops, so the search
         runs over every word it already proved absent. */
      let f = null;
      for (const w of [w1].concat(pool)) {
        for (let n = 1; n < U; n++) { const c = w.slice(0, n); if (drops(c)) { f = c; break; } }
        if (f) break;
      }
      return { U: U, frag: f, under: f ? read(nm + ' ' + f) : null,
               /* NOT GUARDED ON `U`, AND THE RED TEST IS WHY. Gating this probe on
                  w1.length >= U made the whole class VANISH the moment the engine's
                  line moved above the probe word — reverting the constant left this
                  file printing GREEN with N10 absent from the summary, which is the
                  silent cap N0 exists to forbid. The promise being asserted is that
                  a trailing word this page does not have is named without waiting
                  for a separator; if the engine's line sits above that word, the
                  promise is FALSE and this must be RED, not skipped. */
               line: drops(w1) ? read(nm + ' ' + w1) : null };
    }, { ad: AD[s.kind], nm, w1, pool: r.absent });

    if (thr.frag === null) console.log('  SKIP  N9   ' + at + ' — no head of “' + w1 + '” under ' + thr.U + ' chars that the engine drops');
    else if (SAYS.test(thr.under.note))
      fail('N9', at + ' — named “' + thr.frag + '” while he was still typing it: ' + JSON.stringify(thr.under.note.trim()));
    else ok('N9');
    if (!SAYS.test(acc.done.note))
      fail('N9', at + ' — “' + w1 + '” stayed unnamed after he finished the word: ' + JSON.stringify(acc.done.note.trim()));
    else ok('N9');

    if (thr.line === null) console.log('  SKIP  N10  ' + at + ' — “' + w1 + '” is shorter than the engine\'s ' + thr.U + '-character line');
    else {
      const wl = words(thr.line.note);
      if (!wl) fail('N10', at + ' — “' + w1 + '” begins no word on this page and was not named without a separator: ' + JSON.stringify(thr.line.note.trim()));
      else if (wl.map(x => x.toLowerCase()).indexOf(w1.toLowerCase()) === -1)
        fail('N10', at + ' — named ' + JSON.stringify(wl) + ' instead of “' + w1 + '”');
      else ok('N10');
    }
    covered[s.id] = (covered[s.id] || 0) + 1;
    break;   // one name per surface is enough for the mechanical classes
  }
}
await browser.close();

const bare = SURFACES.filter(s => !covered[s.id]).map(s => s.id);
if (bare.length) { console.log('  FAIL  N0  ' + bare.length + ' surface(s) ran NO probe: ' + bare.join(', ')); failing += bare.length; seen.N0 = bare.length; }
else seen.N0 = 0;

console.log('\n  by class: ' + Object.keys(seen).sort().map(k => k + ' ' + (seen[k] ? 'FAIL×' + seen[k] : 'ok')).join('  ·  '));
if (errs.length) { console.log('  PAGE ERRORS ' + errs.length + ': ' + errs.slice(0, 3).join(' | ')); failing += errs.length; }
console.log('\n' + (failing ? '  RED  ' + failing + ' failing / ' + (checked + failing) + ' checks'
                            : '  GREEN  ' + checked + ' checks'));
process.exit(failing ? 1 : 0);
