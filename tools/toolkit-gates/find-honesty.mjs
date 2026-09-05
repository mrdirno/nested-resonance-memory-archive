/**
 * THE HONEST LABEL GATE — is "exact" a claim this engine is entitled to make?
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. `shared/find.js` is loaded by 29 pages — every trade's
 * write-up library, the three commons surfaces, and twelve item filters — and
 * every one of them renders its heading off ONE field: `mode`. Until 2026-08-25
 * `mode` was set from COVERAGE, so a query whose every word landed somewhere,
 * anywhere, at any strength, came back labelled "exact". Driven through the real
 * boxes: 3,838 of 10,738 searches handed back a document the query did not name
 * with no hedge on it. A plumber's "gas shut off notice" typed on the AV page
 * came back as the Room Sign-Off (Commissioning Write-Up), as an exact match.
 * Fixed, that is 2,027 — and the fix's own first draft broke the ROW while it
 * was correcting the LABEL, which is why class G below exists.
 *
 * WHAT THIS GATE ASSERTS, and every probe is DERIVED FROM THE SURFACE'S OWN DATA
 * so a row added next month is tested the day it lands:
 *
 *   A  VERBATIM   an item's own name, typed as its author wrote it, LEADS and is
 *                 NOT hedged. The good case may not move.
 *   B  ALIAS      an authored alias, typed whole, is NOT hedged — `aka` is a name
 *                 somebody wrote, not a guess the engine made.
 *   C  PROSE      a query built ONLY from words that exist nowhere in any name or
 *                 alias on the surface — words that live in a field the caller
 *                 declared `about: true` — is ALWAYS hedged. This is the defect.
 *   D  TYPO       one edit inside a name is the engine changing his characters:
 *                 the item still leads, and the label says "Closest to".
 *   E  JOINED     a name with the spaces taken out is found inside other words:
 *                 leads, and hedged.
 *   F  TYPING     a name truncated mid-word is the word under his cursor, not a
 *                 wrong word — it LEADS and is NOT hedged. The one exemption,
 *                 and the reason mid-typing is not a wall of "Closest to".
 *   G  TITLE       a word in THIS item's title and in no other item's title leads
 *                  THIS item, whatever else carries it as a nickname. Rule 4's
 *                  phrase bonuses are the only thing holding that up, and A and B
 *                  are both blind to their ordering — they type whole strings.
 *   H  CHROME     a WHOLE name plus a word this surface does not carry — the
 *                 "washout template" case — LEADS its item and is NOT hedged.
 *                 Rule 1 exists for that word; deleting it is not a reason to
 *                 doubt the answer, and the note under the rows already says so.
 *   J  FRAGMENT   a PIECE of a name plus the same proven-absent word IS hedged.
 *                 He named part of a thing and a word that is nowhere here, and
 *                 what came back is not what he asked for.
 *
 * H AND J ARE ONE PAIR AND THAT IS THE POINT. Same surface, same dropped word,
 * one letter of difference in what survived — so nothing about the CHROME-ness
 * of the deletion can explain the split, only WHOLENESS can. J is red against
 * rule 5's engine (verified by restoring it, not by argument) and H is red
 * against the predicate a panel reached for first, `live.length <= noise.length`,
 * which counts words instead of asking whether they are a name: 371 of 7,064.
 *
 * C, D and E are RED against the engine as it shipped before this gate existed;
 * A, B and F are green on both and are here to catch the overcorrection. Verified
 * red by restoring the previous shared/find.js — not by argument. G was added
 * after an adversarial read found a lead flip that A through F structurally
 * cannot see, and it was verified red on that exact draft before it was trusted.
 *
 *   node tools/toolkit-gates/find-honesty.mjs [base-url]
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

/* The words a search box teaches people to add. Not a stopword list — this file
   ships none and shared/find.js says why — but the class rule 1 was written for,
   and every one of them is put to the ENGINE below before it is used. */
const CHROME = ['template', 'form', 'sheet', 'example', 'pdf', 'blank', 'printable'];

let checked = 0, failing = 0;
const fail = (m) => { console.log('  FAIL  ' + m); failing++; };
const ok = () => { checked++; };

/* The two adapters. Each hands back the same shape — every probe below is
   written once and runs against a document library and a commons surface
   without knowing which it is. */
const DOCSPEC = {
  input: 'input[type=search][aria-label="Search documents"]',
  data: () => {
    if (!window.DocSpec) return null;
    return {
      /* The pooled vocabulary is searchable on the page, so it names documents
         here even though no author on this trade wrote it. */
      vocab: Object.keys(window.DOCS_POOL || {}).reduce(
        (a, k) => a.concat(window.DOCS_POOL[k] || []), []),
      items: window.DocSpec.library().map(d => ({
        key: d.id, name: d.name,
        aka: (d.aka || []).slice(),
        about: [d.why || '']
      }))
    };
  },
  probe: (q) => {
    const si = document.querySelector('input[type=search][aria-label="Search documents"]');
    const ul = document.querySelector('ul.lib');
    si.value = q; si.dispatchEvent(new Event('input', { bubbles: true }));
    const kids = [...ul.children];
    const g = kids.find(li => li.className === 'grp');
    const s = g ? (g.textContent || '') : '';
    const hedged = /^Closest to/.test(s) || /^Nothing matched/.test(s);
    const row = kids.find(li => li.className !== 'grp' && li.className !== 'none');
    return { lead: row ? ((row.querySelector('.nm') || {}).textContent || '') : '', hedged };
  }
};

const COMMONS = {
  input: '#q',
  data: () => {
    const rows = window.__FH_ROWS;
    if (!rows || !rows.length) return null;
    /* EVERY COMMONS SURFACE SEARCHES THROUGH THE NAME TABLE, so a word can name
       a row here without appearing on the row. "london" and "philadelphia" are
       brick-trowel patterns in commons/names.js and nowhere in gear.js — class C
       would call them prose and the engine would be right to disagree. */
    const vocab = [];
    (window.COMMONS_NAMES || []).forEach(r => {
      vocab.push(r.n);
      (r.a || []).forEach(x => vocab.push(x.n));
    });
    return {
      vocab: vocab,
      items: rows.map(r => ({
        key: r.id, name: r.n,
        aka: (r.a || []).map(x => x.n),
        about: [r.o || '', r.w || '']
      }))
    };
  },
  probe: (q) => {
    const si = document.getElementById('q');
    si.value = q; si.dispatchEvent(new Event('input', { bubbles: true }));
    /* The results section is the last one rendered — a hand-off, when there is
       one, is pushed in front of it and is a different claim entirely. */
    const secs = [...document.querySelectorAll('#sections section.sec')];
    const host = secs[secs.length - 1];
    if (!host) return { lead: '', hedged: false };
    const note = (host.querySelector('.secnote') || {}).textContent || '';
    /* The two sentences commons/commons.js writes for relaxed and for none. They
       are matched by their own text on purpose: this gate is asserting what the
       READER is told, so if that copy is rewritten the gate must be re-pointed at
       the new words rather than quietly passing on a stale regex. */
    const hedged = /Nothing here is called exactly that/.test(note) ||
                   /Nothing on this page goes by that/.test(note);
    const nm = host.querySelector('li.item .nm');
    return { lead: nm ? (nm.textContent || '').replace(/\s+/g, ' ').trim() : '', hedged };
  }
};

/* ── the probes, all built from the surface's own strings ─────────────────── */
const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/^ +| +$/g, '');
const toks = s => { const n = norm(s); return n ? n.split(' ') : []; };

function buildProbes(items, vocab, extra) {
  const absent = (extra && extra.absent) || [];
  const frags = (extra && extra.frags) || [];
  /* Every word that is part of what SOMETHING on this surface is CALLED. A word
     outside this set can only be reached through an `about` field. */
  const named = new Set();
  const namedToks = items.map(it => [it.name].concat(it.aka).map(toks).filter(a => a.length));
  namedToks.forEach(sets => sets.forEach(a => a.forEach(t => named.add(t))));
  (vocab || []).forEach(v => toks(v).forEach(t => named.add(t)));

  /* WHICH ITEMS COULD HE HAVE MEANT. A probe may only assert which row LEADS
     when exactly one item on the surface is named in a way that covers every
     word he typed — "meeting" is an alias of the minutes AND a word in the
     Toolbox Talk's title, so it is evidence about the label and about nothing
     else. `pfx` asks the same question of a half-typed last word. */
  function owners(q, pfx) {
    const qt = toks(q); if (!qt.length) return 0;
    const head = pfx ? qt.slice(0, -1) : qt, tail = pfx ? qt[qt.length - 1] : null;
    let n = 0;
    for (let i = 0; i < items.length; i++) {
      const hit = namedToks[i].some(a => head.every(t => a.indexOf(t) !== -1) &&
        (!tail || a.some(t => t.indexOf(tail) === 0)));
      if (hit) n++;
    }
    return n;
  }

  const P = [];
  items.forEach((it, idx) => {
    const nf = norm(it.name);
    const sole = owners(it.name, false) === 1;
    if (nf) {
      P.push({ cls: 'A', q: it.name, want: sole ? it.key : null, hedged: false });
      const tk = nf.split(' ');
      /* D — one edit inside the longest word, which is a slip, not a word. It
         has to survive the fuzzy budget to be a probe at all: below six letters
         the edited word gets no budget, so it is dropped as noise and the engine
         is being asked a different question than the one written here. */
      let li = 0; tk.forEach((w, i) => { if (w.length > tk[li].length) li = i; });
      if (tk[li].length >= 6) {
        const w = tk[li], h = Math.floor(w.length / 2), sl = w.slice(0, h) + w.slice(h + 1);
        /* Rule 3 ranks a real prefix above a spelling guess ON PURPOSE, so when
           the slip happens to start somebody else's word the row it leads with
           is the rule working, not the label failing. Assert the label only. */
        const collides = items.some((o, j) => j !== idx && namedToks[j].some(a =>
          a.some(t => t.length >= 3 && (sl.indexOf(t) === 0 || t.indexOf(sl) === 0))));
        P.push({ cls: 'D', q: tk.map((x, i) => i === li ? sl : x).join(' '),
                 want: (sole && !collides) ? it.key : null, hedged: true });
      }
      /* E — the spaces taken out, which only an infix can find.
         UNLESS THE JOINED FORM IS A WORD SOMEBODY AUTHORED (found 2026-09-04,
         trade #17): the paving names row "String line" carries the alias
         "stringline" — the paver operator's one word for the wire the machine's
         sensor rides — and this probe asked the engine to HEDGE on a term rule B
         two lines down asserts must be EXACT. The gate contradicted itself on one
         row and called the honest label a defect. When the joined form is an
         authored name or alias on any item, B owns the question and E has none. */
      if (tk.length > 1) {
        const joined = tk.join('');
        const authored = items.some(o => norm(o.name) === joined || o.aka.some(a => norm(a) === joined));
        if (!authored) P.push({ cls: 'E', q: joined, want: sole ? it.key : null, hedged: true });
      }
      /* F — the word under the cursor: cut the last word short. */
      const last = tk[tk.length - 1];
      if (last.length >= 4 && nf.length > 5) {
        const q = tk.slice(0, -1).concat(last.slice(0, Math.max(2, last.length - 2))).join(' ');
        P.push({ cls: 'F', q: q, want: owners(q, true) === 1 ? it.key : null, hedged: false });
      }
    }
    it.aka.forEach(a => {
      if (!norm(a)) return;
      P.push({ cls: 'B', q: a, want: owners(a, false) === 1 ? it.key : null, hedged: false });
    });

    /* H — THE WORD A SEARCH BOX TAUGHT HIM TO ADD, on a name he typed whole.
       THE TRAILING SPACE IS LOAD-BEARING ON H AND J BOTH: while the last word is
       still under his thumb the engine will neither name it nor hedge on it (the
       `say` block in shared/find.js), so without the separator these two probes
       ask a question rule 6 has deliberately declined to answer.
       The engine proved these words land nowhere on this surface (see `absent`
       below), so rule 1 deletes them and rule 6 has to decide whether that is a
       reason to doubt the row. It is not: what survived is the entire name of
       the thing he is looking at. */
    if (nf) absent.forEach(w => {
      if (nf.indexOf(w) !== -1) return;
      P.push({ cls: 'H', q: it.name + ' ' + w + ' ', want: sole ? it.key : null, hedged: false });
    });

    /* G — A TITLE OUTRANKS A NICKNAME. A word that appears in THIS item's title
       and in no other item's title belongs to this item, however many other rows
       carry it as an alias. Rule 4 hands out a phrase bonus per row and the sizes
       of those bonuses are the only thing keeping that true: set the "he typed a
       whole alias" bonus equal to the "he typed the whole title" one and the AV
       page starts answering "damage" with the Incident / Near-Miss Report while
       the Damage Note sits underneath it — labelled exact, because the LABEL was
       right and the ROW was wrong. Neither A nor B can see that: A types the
       whole title and B the whole alias, and a bonus inversion only shows when a
       single word is claimed by both. */
    nf && nf.split(' ').forEach(t => {
      if (t.length < 4) return;
      const mine = items.filter((o, j) => toks(o.name).indexOf(t) !== -1);
      if (mine.length !== 1 || mine[0].key !== it.key) return;
      P.push({ cls: 'G', q: t, want: it.key, hedged: false });
    });

    /* C — two words that live ONLY in this item's prose. Nothing on the surface
       is CALLED either of them, so no answer to this query is the thing he
       named, and the engine may not say it is. */
    const prose = [];
    it.about.forEach(s => toks(s).forEach(t => {
      if (t.length >= 5 && !named.has(t) && prose.indexOf(t) === -1) prose.push(t);
    }));
    if (prose.length >= 2) P.push({ cls: 'C', q: prose.slice(0, 2).join(' '), want: null, hedged: true });
  });

  /* J — THE HALF HE LOST. One word of a name that nothing here is wholly CALLED,
     plus the same proven-absent word H uses. Whatever leads, he did not name it:
     he named a piece of it and a word this surface does not have. The row is not
     asserted — only the label, which is the one thing rule 6 changes. */
  frags.forEach(f => absent.forEach(w => {
    P.push({ cls: 'J', q: f + ' ' + w + ' ', want: null, hedged: true });
  }));
  return P;
}

async function run(page, label, adapter, url, prep) {
  await page.goto(url, { waitUntil: 'load' });
  if (prep) await page.evaluate(prep);
  const got = await page.evaluate(adapter.data);
  if (!got || !got.items) { fail(label + ' — no data on the page (engine or data file missing)'); return; }
  const items = got.items;
  /* THE ENGINE PICKS THE WORDS, NOT THE GATE — the same rule find-noise.mjs
     already runs on. "Not in a name" is the weaker condition, because prose
     fields and a pooled alias index are in there too; mode "none" is the engine
     itself reporting that every token of that query reached nothing. The
     fragments come out of the index the page built, so a field nobody told this
     gate about still counts. */
  const extra = await page.evaluate(({ sel, chrome, own }) => {
    const si = document.querySelector(sel);
    if (!si || !window.Find) return { absent: [], frags: [] };
    /* ONE KEYSTROKE BUILDS MORE THAN ONE INDEX. Every commons surface searches
       its own rows AND the cross-page name table (commons/commons.js
       `handoff.ix`), so taking "the index" means taking whichever happened to
       run last — which on tips.html is the alias table, and every word this
       gate then proved absent was proved absent from the wrong page. So all of
       them are kept and the one holding THIS surface's first row is the one
       used, which is a fact rather than an ordering assumption. */
    const seen = [];
    const real = window.Find.search;
    window.Find.search = function (ix, q) { if (seen.indexOf(ix) === -1) seen.push(ix); return real.apply(this, arguments); };
    si.value = 'zz'; si.dispatchEvent(new Event('input', { bubbles: true }));
    window.Find.search = real;
    si.value = ''; si.dispatchEvent(new Event('input', { bubbles: true }));
    /* CONTAINS, not equals — shared/pickfilter.js indexes a row's whole <li>
       text as its primary field, so a name is a substring of it, never the
       string itself. Same rule in tools/toolkit-gates/find-noise.mjs. */
    const holds = (ix) => !!own && ix.rows.some(r => r.f[ix.primary].whole.some(w => w.indexOf(own) !== -1));
    const IX = seen.filter(holds)[0] || null;
    if (!IX) return { absent: [], frags: [] };
    const absent = chrome.filter(w => real(IX, w).mode === 'none');
    /* Every string this surface is CALLED, exactly as the index holds it. */
    const whole = new Set();
    IX.rows.forEach(r => IX.fields.forEach((fd, fx) => {
      if (!fd.about) r.f[fx].whole.forEach(x => x && whole.add(x));
    }));
    const frags = [];
    IX.rows.forEach(r => r.f[IX.primary].whole.forEach(n => String(n).split(' ').forEach(t => {
      if (t.length >= 4 && !whole.has(t) && frags.indexOf(t) === -1) frags.push(t);
    })));
    return { absent: absent.slice(0, 2), frags: frags.slice(0, 3) };
  }, { sel: adapter.input, chrome: CHROME, own: norm(items[0] && items[0].name) });
  const probes = buildProbes(items, got.vocab, extra);
  if (!probes.length) { fail(label + ' — built no probes'); return; }
  const byKey = {}; items.forEach(it => { byKey[it.key] = it.name; });
  const out = await page.evaluate(([probes, src]) => {
    const probe = eval('(' + src + ')');
    return probes.map(p => {
      const r = probe(p.q);
      return Object.assign({}, p, { got: r.hedged, lead: r.lead });
    });
  }, [probes, adapter.probe.toString()]);

  const cls = {};
  out.forEach(r => {
    cls[r.cls] = cls[r.cls] || { n: 0, bad: 0 };
    cls[r.cls].n++;
    const want = r.hedged, got = r.got;
    if (got !== want) {
      cls[r.cls].bad++;
      if (cls[r.cls].bad <= 2) fail(label + ' [' + r.cls + '] "' + r.q + '" → ' +
        (got ? 'hedged' : 'presented as EXACT') + ', expected ' + (want ? 'hedged' : 'exact') +
        ' — lead "' + r.lead + '"');
    } else if (r.lead && r.want && byKey[r.want] &&
               norm(r.lead).indexOf(norm(byKey[r.want])) === -1 && r.cls !== 'C') {
      /* Leading the wrong row is a separate failure from labelling it wrong, and
         only the classes that name a specific item can assert it. */
      cls[r.cls].bad++;
      if (cls[r.cls].bad <= 2) fail(label + ' [' + r.cls + '] "' + r.q + '" led with "' + r.lead +
        '", wanted "' + byKey[r.want] + '"');
    } else ok();
  });
  console.log('  ' + label.padEnd(24) +
    Object.keys(cls).sort().map(k => k + ' ' + (cls[k].n - cls[k].bad) + '/' + cls[k].n).join('  '));
}

const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', e => fail('PAGE ERROR ' + e.message));

console.log('THE HONEST LABEL — ' + BASE);
for (const t of TRADES) await run(page, t + '/write-up', DOCSPEC, BASE + '/' + t + '/write-up.html');
for (const [file, global] of [['index.html', 'COMMONS_GEAR'], ['tips.html', 'COMMONS_TIPS'], ['names.html', 'COMMONS_NAMES']]) {
  await run(page, 'commons/' + file, COMMONS, BASE + '/commons/' + file,
    new Function('window.__FH_ROWS = window.' + global + ' || [];'));
}
await browser.close();

console.log('\n  checks ' + checked + '  failing ' + failing);
process.exit(failing ? 1 : 0);
