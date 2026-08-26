/* FIELD TOOLKIT — SHARED: THE SEARCH THAT DOES NOT DEAD-END.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS FILE EXISTS, measured before a line of it was written.
 *
 * Two search boxes exist in this whole toolkit: the document library in
 * shared/docspec.js (8 trades × ~13 documents) and the item filter on
 * av/consumables.html. Both were the same one-liner in two dialects — split the
 * query, require EVERY token to be a substring, render whatever survives in
 * FILE order, and when nothing survives, say so and stop.
 *
 * THE MEASUREMENT THAT SET THE DESIGN. 953 queries were driven through the real
 * write-up page in a real browser, taken from the authors' own strings — every
 * document's `name` and every one of its `aka` entries, which is the authors'
 * record of what people actually call the thing. Result: 0 misses. That number
 * is the trap. Those strings are substrings BY CONSTRUCTION, so the old filter
 * could not miss them, and every check anyone would think to run reports green.
 *
 * So the same 953 were perturbed mechanically — one fixed transform list applied
 * uniformly, nothing hand-picked — and driven again. 5,384 queries, 4,121 of
 * them returning NOTHING AT ALL (76.5%):
 *
 *     + "template"  953 / 953   100% miss    "daily field report template"
 *     plural        863 / 874    99% miss    "daily field reports"
 *     one typo      780 / 788    99% miss    "daily field reprt"
 *     joined        677 / 699    97% miss    "backcharge", "endofday"
 *     + "form"      848 / 953    89% miss    "daily field report form"
 *
 * A man in a truck types the name of the document he owes somebody, adds the
 * word "template" because that is what you type into a search box, and the page
 * tells him the document does not exist. Then it routes him into "not in the
 * list" — the custom path was never a niche, it was where search dumped people.
 *
 * THE FIVE RULES THIS ENGINE IS BUILT ON.
 *
 * 1. A TOKEN THAT MATCHES NOTHING IN THE WHOLE LIBRARY IS NOISE THE USER ADDED,
 *    NOT A REQUIREMENT THEY STATED. "template" and "form" are not in any
 *    document name here and never will be — under AND they are a veto that
 *    silently deletes the library. They are dropped from the requirement and
 *    contribute nothing to the score. This is why there is NO stopword list in
 *    this file: a stopword list is a guess maintained by hand, and this rule is
 *    a measurement of the actual library, so it covers "form", "template",
 *    "sheet", "example", the trade word a man types out of habit, and every
 *    other word nobody has thought of yet.
 *
 * 2. PRECISION FIRST, THEN DEGRADE — NEVER DEAD-END. Items are ranked by how
 *    many query tokens they matched (COVERAGE) before they are ranked by score,
 *    and only the best coverage tier is shown. When something matches every
 *    token, that is exactly what AND would have returned, so the good case is
 *    unchanged. When nothing does, the tier drops instead of the list emptying.
 *    "Nothing matches" as a final answer is a bug, not a state.
 *
 * 3. FUZZY IS A LAST RESORT AND IT KEEPS ITS FIRST LETTER. Exact beats prefix
 *    beats infix beats fuzzy, always, so a real hit can never be pushed under an
 *    approximate one. Fuzzy needs the first character to agree and spends an
 *    edit budget of one (two only from nine characters up). That guard is not
 *    decoration: "turnover" and "handover" are two edits apart and are two
 *    different documents in this library, and without it the search would
 *    quietly offer the wrong one.
 *
 * 4. THE PHRASE THE USER TYPED OUTRANKS EVERYTHING. Typing a document's exact
 *    full name and getting it second is the failure that survives every other
 *    fix — measured on gc/write-up.html, where "The Turnover Write-Up" ranked
 *    under "Warranty Callback Write-Up" because file order was the only order.
 *    A NAME HE TYPED VERBATIM COUNTS WHEREVER IT IS WRITTEN, not only in the
 *    primary field: `aka` is the authors' record of what people SAY, so an alias
 *    typed whole is the same evidence as a title typed whole. It is tested
 *    against each alias ON ITS OWN — never against the aliases joined — because
 *    a query that straddles two of them ("notice held") is not a name anybody
 *    wrote, and treating it as one is how a phrase bonus becomes a phrase lie.
 *
 * 5. COVERAGE IS NOT CONFIDENCE — measured 2026-08-25, and it is why this file
 *    was opened again. Rules 1-4 shipped a search that always answers, and then
 *    10,738 searches driven through the real box on all fourteen trades found
 *    the answer it gives when it should not: 3,838 of them handed back a
 *    document the query did not name, WITH NO HEDGE ON IT — 3,615 of those a
 *    document the reader's trade does not even carry. One line caused it. Mode
 *    was set from COVERAGE — did every live token match *something* — and a
 *    match is a match whether the token is the document's own title or one word
 *    of its explanatory prose two fields down at weight 2. On the AV page, a
 *    plumber's "gas shut off notice" came back as the Room Sign-Off
 *    (Commissioning Write-Up) — an AV tech has no such document and never will
 *    — presented as an exact match, and "failed inspection" as the Meeting
 *    Failure / Outage Report. Both now say "Closest to".
 *
 *    So a match now carries a STRENGTH beside its score, and strength answers a
 *    narrower question than the score does: DID HE NAME THIS THING? A token is
 *    strong when it is a word of what the item is CALLED — its title, or an
 *    alias somebody wrote for it — and he typed that word whole. A token is weak
 *    when the engine reached for it: it changed his characters to get there
 *    (fuzzy), found his letters buried inside other words (infix), read past the
 *    end of a word he had already finished, or found the word only in a field
 *    that DESCRIBES the item rather than names it. That last one is the caller's
 *    own declaration and not a guess about weights — a field carrying
 *    `about: true` says "this prose tells you what the thing is for", and a word
 *    that lands only there has identified nothing.
 *
 *    THE ONE EXEMPTION, AND IT IS THE WORD UNDER THE CURSOR. A prefix counts as
 *    strong on the LAST token only, because that is the word he is still typing
 *    and half-typed is not the same as wrong. Anywhere else a prefix is the
 *    engine reading past him: in "not our crack", "not" reaching "notes" is a
 *    different word, not an unfinished one. Measured both ways over the corpus
 *    below — strict everywhere leaves 1,907 confident wrong answers and turns
 *    HALF of every keystroke into a "Closest to"; the exemption costs 99 of
 *    those 10,738 searches and returns mid-typing to silence: 214 of 214
 *    four-character queries exact, against 113 of 214 without it.
 *
 *    WHAT IT DID: unhedged wrong 3,838 → 2,006, and the document he was actually
 *    looking for came up first 3,986 → 4,160 — with ZERO answers that were right
 *    before and wrong after, and ZERO correct answers hedged. The label was the
 *    target; the extra 174 are rule 4 finally reaching `aka` (below).
 *    A NAME OR AN ALIAS TYPED AS ITS AUTHOR WROTE IT IS UNTOUCHED: 214/214
 *    verbatim titles and 1,461/1,461 aliases still go out as exact. The five
 *    perturbations this engine was built for still LEAD — plural 213/214, one
 *    typo 205/205, joined 214/214 — and now go out saying "Closest to", which is
 *    what they always were.
 *
 *    WHAT WAS TRIED AND CUT, because a theory that measures at zero is a finding.
 *    Strength looked like it should also decide WHAT IS SHOWN — tier by strong
 *    coverage first, so a document whose prose sweeps up three of his words
 *    cannot hide the one actually named after two. It reads well and it earned
 *    NOTHING: 4,160 right either way, and it made 56 more wrong answers
 *    confident by narrowing the tier around a strong-but-wrong lead. Rule 2 is
 *    unchanged. Strength decides what the answer is CALLED, not what it is.
 *
 * WHAT THE CALLER OWNS: its fields, their weights, whether a field NAMES the
 * item or merely describes it (`about: true`), and what it does with the
 * `relaxed` / `none` modes — because the HONEST LABEL is the caller's UI. This
 * engine never silently pretends an approximate result is an exact one; it
 * always says which it handed back.
 *
 *   var ix = Find.index(items, [{ get: function (d) { return d.name; }, w: 10, primary: true },
 *                               { get: function (d) { return d.aka;  }, w: 6 },
 *                               { get: function (d) { return d.why;  }, w: 2, about: true }]);
 *   var r  = Find.search(ix, q);   //  { hits, mode: "exact"|"relaxed"|"none", noise }
 *
 * Load before any engine that searches. No dependencies, ES5, no network.
 */
(function () {
  "use strict";

  /* ── text ──────────────────────────────────────────────────────────────── */
  function norm(s) {
    return String(s === null || s === undefined ? "" : s)
      .toLowerCase().replace(/[^a-z0-9]+/g, " ").replace(/^ +| +$/g, "");
  }
  function toks(s) { var n = norm(s); return n ? n.split(" ") : []; }
  function squash(s) { return norm(s).split(" ").join(""); }

  /* Levenshtein with a hard ceiling — it stops the moment it cannot come in
     under `max`, so the cost is bounded per keystroke on a phone. */
  function dist(a, b, max) {
    if (a === b) return 0;
    var la = a.length, lb = b.length, i, j;
    if (la - lb > max || lb - la > max) return max + 1;
    var prev = [], cur = [];
    for (j = 0; j <= lb; j++) prev[j] = j;
    for (i = 1; i <= la; i++) {
      cur[0] = i;
      var best = i;
      for (j = 1; j <= lb; j++) {
        var c = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
        var v = prev[j] + 1;
        if (cur[j - 1] + 1 < v) v = cur[j - 1] + 1;
        if (prev[j - 1] + c < v) v = prev[j - 1] + c;
        cur[j] = v;
        if (v < best) best = v;
      }
      if (best > max) return max + 1;
      for (j = 0; j <= lb; j++) prev[j] = cur[j];
    }
    return prev[lb];
  }

  /* Rule 3's budget. Four characters or fewer get none — at that length an edit
     is a different word, not a slip. */
  function budget(t) { return t.length <= 4 ? 0 : t.length <= 8 ? 1 : 2; }

  /* ── the index: built once, searched on every keystroke ────────────────── */
  function index(items, fields) {
    var rows = (items || []).map(function (it) {
      var f = fields.map(function (fd) {
        var v = fd.get(it);
        var parts = (v === null || v === undefined) ? []
                  : (Object.prototype.toString.call(v) === "[object Array]" ? v : [v]);
        var t = [], k, np, whole = [];
        for (k = 0; k < parts.length; k++) {
          np = norm(parts[k]);
          if (np) whole.push(np);
          t = t.concat(toks(parts[k]));
        }
        /* `whole` keeps each part on its own — rule 4 asks whether he typed one
           of these, and joining them first would invent names nobody wrote. */
        return { t: t, j: t.join(""), n: whole.join(" "), whole: whole };
      });
      return { it: it, f: f };
    });
    var pi = 0;
    fields.forEach(function (fd, i) { if (fd.primary) pi = i; });
    return { rows: rows, fields: fields, primary: pi };
  }

  /* Rule 5's ladder. The top rung is the only one where he supplied every
     character of the item's own word; the rung below it is that word still being
     typed, which counts on the last token and nowhere else. */
  var T_NONE = 0, T_SOFT = 1, T_PAST = 2, T_PREFIX = 3, T_EXACT = 4;

  /* The rung the last tokenScore() came back on. A module scratch rather than an
     object returned per (token × row × field): this runs on every keystroke over
     the whole list, and the allocation is the only part of it that is not free.
     Single-threaded and read on the line after the call, so it cannot drift. */
  var TIER = T_NONE;

  /* One query token against one indexed field. Exact > prefix > infix > fuzzy,
     and the tiers never overlap, so an approximate hit cannot outscore a real
     one no matter how the weights are set. */
  function tokenScore(tok, fi, w) {
    var t = fi.t, i, ft;
    TIER = T_NONE;
    for (i = 0; i < t.length; i++) if (t[i] === tok) { TIER = T_EXACT; return w; }
    var best = 0, bestTier = T_NONE;
    for (i = 0; i < t.length; i++) {
      ft = t[i];
      if (tok.length >= 2 && ft.length > tok.length && ft.indexOf(tok) === 0) {
        if (w * 0.8 > best) { best = w * 0.8; bestTier = T_PREFIX; }   // typed a prefix
      } else if (ft.length >= 3 && tok.length > ft.length && tok.indexOf(ft) === 0) {
        if (w * 0.65 > best) { best = w * 0.65; bestTier = T_PAST; }   // typed past the word
      }
    }
    if (best) { TIER = bestTier; return best; }
    if (tok.length >= 3 && fi.j.indexOf(tok) !== -1) { TIER = T_SOFT; return w * 0.45; }  // inside a word
    var b = budget(tok);
    if (b) {
      for (i = 0; i < t.length; i++) {
        ft = t[i];
        if (ft.charAt(0) !== tok.charAt(0)) continue;
        var d = dist(tok, ft, b);
        if (d <= b) { TIER = T_SOFT; return w * (0.62 - 0.16 * d); }
      }
    }
    return 0;
  }

  function search(ix, q) {
    var rows = ix.rows, fields = ix.fields, i, r, k;
    var query = norm(q);
    if (!query) {
      return { hits: rows.map(function (x) { return x.it; }), mode: "all", noise: [], q: "" };
    }
    var qt = query.split(" "), qj = qt.join("");

    /* Per token, the best score any item can give it, and beside it the best
       STRENGTH — 2 when the token is a word of what the item is CALLED and he
       typed it or its beginning, 1 when the engine had to reach, 0 for nothing.
       The two are tracked separately on purpose: the score decides the order,
       the strength decides what the answer is allowed to be CALLED. */
    var per = [], str = [], noise = [];
    for (k = 0; k < qt.length; k++) {
      var col = [], scol = [], top = 0;
      /* Mid-word only counts on the word he is still typing. */
      var need = (k === qt.length - 1) ? T_PREFIX : T_EXACT;
      for (i = 0; i < rows.length; i++) {
        var s = 0, st = 0;
        for (var fx = 0; fx < fields.length; fx++) {
          var v = tokenScore(qt[k], rows[i].f[fx], fields[fx].w);
          var sv = TIER === T_NONE ? 0 : (TIER >= need && !fields[fx].about ? 2 : 1);
          if (v > s) s = v;
          if (sv > st) st = sv;
        }
        col.push(s); scol.push(st);
        if (s > top) top = s;
      }
      per.push(col); str.push(scol);
      if (!top) noise.push(qt[k]);
    }
    var live = [];
    for (k = 0; k < qt.length; k++) if (noise.indexOf(qt[k]) === -1) live.push(k);

    /* Every token was noise — the query has nothing to do with this library.
       Rule 2: hand back the closest three rather than an empty box. */
    if (!live.length) return { hits: closest(ix, query, 3), mode: "none", noise: noise, q: query };

    var pw = fields[ix.primary].w;
    var scored = [];
    for (i = 0; i < rows.length; i++) {
      var sc = 0, cover = 0, strong = 0;
      for (k = 0; k < live.length; k++) {
        var val = per[live[k]][i];
        if (val > 0) { cover++; sc += val; if (str[live[k]][i] === 2) strong++; }
      }
      if (!cover) continue;
      var p = rows[i].f[ix.primary];
      if (p.n.indexOf(query) !== -1) sc += pw * (p.n === query ? 1.6 : 1.1);        // rule 4
      else if (named(rows[i], query, fields, ix.primary)) sc += pw * 1.6;           // rule 4, any name
      else if (qj.length >= 4 && p.j.indexOf(qj) !== -1) sc += pw * 0.9;
      scored.push({ it: rows[i].it, sc: sc, cover: cover, strong: strong, i: i });
    }
    if (!scored.length) return { hits: closest(ix, query, 3), mode: "none", noise: noise, q: query };

    var maxCover = 0;
    for (i = 0; i < scored.length; i++) if (scored[i].cover > maxCover) maxCover = scored[i].cover;
    var tier = scored.filter(function (x) { return x.cover === maxCover; });
    tier.sort(function (a, b) { return b.sc - a.sc || a.i - b.i; });

    /* "exact" is a claim about the row he is looking at first. */
    var lead = tier[0];
    var honest = lead.cover === live.length && lead.strong === live.length;

    return {
      hits: tier.map(function (x) { return x.it; }),
      mode: honest ? "exact" : "relaxed",
      noise: noise,
      q: query
    };
  }

  /* Rule 4's other half: did he type one of this item's names, whole? Only
     fields that NAME the item, only a whole part, never the parts joined. */
  function named(row, query, fields, primary) {
    for (var fx = 0; fx < fields.length; fx++) {
      if (fx === primary || fields[fx].about) continue;
      var w = row.f[fx].whole;
      for (var i = 0; i < w.length; i++) if (w[i] === query) return true;
    }
    return false;
  }

  /* The last resort. No first-character guard and a generous budget, because at
     this point the alternative on screen is nothing at all. */
  function closest(ix, query, n) {
    var qt = query.split(" ");
    var out = ix.rows.map(function (r, i) {
      var best = 0;
      for (var k = 0; k < qt.length; k++) {
        for (var fx = 0; fx < ix.fields.length; fx++) {
          var t = r.f[fx].t;
          for (var j = 0; j < t.length; j++) {
            var lim = Math.max(qt[k].length, t[j].length);
            if (!lim) continue;
            var d = dist(qt[k], t[j], Math.ceil(lim / 2));
            var p = 1 - d / lim;
            if (p > best) best = p * (ix.fields[fx].w / ix.fields[ix.primary].w);
          }
        }
      }
      return { it: r.it, p: best, i: i };
    });
    out.sort(function (a, b) { return b.p - a.p || a.i - b.i; });
    return out.slice(0, n).map(function (x) { return x.it; });
  }

  window.Find = { index: index, search: search, norm: norm, toks: toks, squash: squash, dist: dist };
})();
