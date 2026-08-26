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
 *
 * C, D and E are RED against the engine as it shipped before this gate existed;
 * A, B and F are green on both and are here to catch the overcorrection.
 * Verified red by restoring the previous shared/find.js — not by argument.
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

let checked = 0, failing = 0;
const fail = (m) => { console.log('  FAIL  ' + m); failing++; };
const ok = () => { checked++; };

/* The two adapters. Each hands back the same shape — every probe below is
   written once and runs against a document library and a commons surface
   without knowing which it is. */
const DOCSPEC = {
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
    const hedged = /Nothing matched all of that/.test(note) || /Nothing on this page goes by that/.test(note);
    const nm = host.querySelector('li.item .nm');
    return { lead: nm ? (nm.textContent || '').replace(/\s+/g, ' ').trim() : '', hedged };
  }
};

/* ── the probes, all built from the surface's own strings ─────────────────── */
const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/^ +| +$/g, '');
const toks = s => { const n = norm(s); return n ? n.split(' ') : []; };

function buildProbes(items, vocab) {
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
      /* E — the spaces taken out, which only an infix can find. */
      if (tk.length > 1) P.push({ cls: 'E', q: tk.join(''), want: sole ? it.key : null, hedged: true });
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

    /* C — two words that live ONLY in this item's prose. Nothing on the surface
       is CALLED either of them, so no answer to this query is the thing he
       named, and the engine may not say it is. */
    const prose = [];
    it.about.forEach(s => toks(s).forEach(t => {
      if (t.length >= 5 && !named.has(t) && prose.indexOf(t) === -1) prose.push(t);
    }));
    if (prose.length >= 2) P.push({ cls: 'C', q: prose.slice(0, 2).join(' '), want: null, hedged: true });
  });
  return P;
}

async function run(page, label, adapter, url, prep) {
  await page.goto(url, { waitUntil: 'load' });
  if (prep) await page.evaluate(prep);
  const got = await page.evaluate(adapter.data);
  if (!got || !got.items) { fail(label + ' — no data on the page (engine or data file missing)'); return; }
  const items = got.items;
  const probes = buildProbes(items, got.vocab);
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
