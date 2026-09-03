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
 * THE SIX RULES THIS ENGINE IS BUILT ON.
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
 *    WHAT IT DID: unhedged wrong 3,838 → 2,027, and the document he was actually
 *    looking for came up first 3,986 → 4,139 — with ZERO answers that were right
 *    before and wrong after, and ZERO correct answers hedged. The label was the
 *    target; the extra 153 are rule 4, which had two bugs of its own and gave
 *    them both up under an adversarial read (see the ladder in the code).
 *    A NAME OR AN ALIAS TYPED AS ITS AUTHOR WROTE IT IS UNTOUCHED: 214/214
 *    verbatim titles and 1,461/1,461 aliases still go out as exact. The five
 *    perturbations this engine was built for still LEAD — plural 213/214, one
 *    typo 205/205, joined 214/214 — and now go out saying "Closest to", which is
 *    what they always were.
 *
 *    AND THE LABEL IS NOT THE ONLY THING THAT HAS TO BE TRUE. A word in an item's
 *    TITLE outranks the same word used as somebody's nickname for a different
 *    item — "toolbox" is the Toolbox Talk even where another document answers to
 *    it, and "damage" is the Damage Note. BOTH WORKED EXAMPLES HERE WERE REWRITTEN
 *    2026-09-02 and the reason is worth keeping: they used to read "damage … even
 *    though the Incident Report answers to it" and "safety is the Toolbox Talk /
 *    Safety Meeting Note". The shelf gate retired the first — the Incident Report
 *    no longer answers to "damage" at all, so the tie this rule was resolving does
 *    not exist — and renaming that document to stop its title eating "meeting" on
 *    16 shelves took "safety" out of a TITLE, which flipped the second. "safety"
 *    is now a declared alias there rather than an accident of the name. A comment
 *    that names a behaviour is a claim; these two had quietly stopped being true.
 *    That is rule 4's ladder below, and it
 *    is asserted per surface rather than reasoned about: an honest label over the
 *    wrong row is a better-dressed version of the same failure.
 *
 *    WHAT WAS TRIED AND CUT, because a theory that measures at zero is a finding.
 *    Strength looked like it should also decide WHAT IS SHOWN — tier by strong
 *    coverage first, so a document whose prose sweeps up three of his words
 *    cannot hide the one actually named after two. It reads well and it earned
 *    NOTHING: 4,160 right either way, and it made 56 more wrong answers
 *    confident by narrowing the tier around a strong-but-wrong lead. Rule 2 is
 *    unchanged. Strength decides what the answer is CALLED, not what it is.
 *
 * 6. COVERAGE OF WHAT SURVIVED IS NOT COVERAGE OF WHAT HE TYPED — measured
 *    2026-08-28, and it is the other half of rule 5. Rule 5 stopped the engine
 *    calling a match exact when it had REACHED for the words; rule 1 is still
 *    free to DELETE one and then be graded on what is left. "Inspection Note" on
 *    the AV page keeps `note`, answers with the Damage / Pre-Existing Condition
 *    Note, and passes every clause above with a clean sheet, because `inspection`
 *    was never in the arithmetic. Driven over 72,138 searches on all 31 surfaces
 *    that load this file: 3,125 handed back a row the query did not name with no
 *    hedge on it.
 *
 *    THE DISCRIMINATING FACT IS NOT HOW MANY WORDS SURVIVED. The predicate a
 *    panel reached for first was `live.length <= noise.length` — half or less of
 *    what he typed survived — and counting cannot tell the whole name of a thing
 *    from a piece of one. It hedges "Washout template": a one-word row name plus
 *    the word a search box taught him to add, which is the exact class rule 1
 *    exists for. Measured, that predicate costs 371 of 7,064 name-plus-chrome
 *    searches — the cure becoming the disease. The question is whether what
 *    SURVIVED is a WHOLE NAME of the row he is being shown. In "Washout
 *    template" the survivor is the entire name and the deletion was chrome; in
 *    "Inspection Note" the survivor is a fragment of a longer name and the
 *    deletion was the word that discriminates.
 *
 *    AND IT FIRES ON WHAT MAY BE SAID OUT LOUD, NOT ON EVERY DROPPED TOKEN.
 *    A one-character token can only match exactly, so the first letter of every
 *    word after the first is noise for one keystroke; the `say` block below
 *    already holds that back from the sentence for exactly that reason, and the
 *    label has to make the same trade or the two contradict each other. Firing
 *    on raw `noise` instead costs 11,306 of 21,017 mid-typing keystrokes — 53.8%
 *    of every word boundary flips the heading to "Closest to" and back, under his
 *    thumb, on the default way this box is used. A word we will not NAME is not
 *    a word we may HEDGE on; the moment a separator says he is finished with it,
 *    we do both.
 *
 *    WHAT IT DID: unhedged wrong 3,125 -> 675. Diffed query by query rather than
 *    totalled: 2,450 answers newly hedged and EVERY ONE OF THEM over a lead the
 *    query had not named — zero right answers hedged. A name or an alias typed as
 *    its author wrote it, 7,417/7,417 exact, unmoved. That name plus a search-box
 *    word, 7,064/7,064 exact, unmoved. Mid-typing, 14,762 of 21,017 exact,
 *    unmoved. And the LEAD ROW never moves — 41,194 correct leads before and
 *    after, 0 right-to-wrong and 0 wrong-to-right, because rule 6 decides what
 *    the answer is CALLED and never what it is.
 *    `tools/toolkit-gates/find-honesty.mjs` classes H and J are that pair
 *    standing on one surface: the same proven-absent word attached to a WHOLE
 *    name (stays exact, class H) and to a FRAGMENT of one (hedges, class J). J is
 *    0/108 against the engine before this change; H is 1,402/1,468 against the
 *    counting predicate. Both red-verified by restoring the code, not argued.
 *
 *    AND RULE 6 IMMEDIATELY CAUGHT SOMETHING RULE 4 HAD BEEN HIDING. The ladder
 *    was graded on the RAW query with the deleted word still in it, so it handed
 *    out no phrase bonus at all the moment one word was dropped and the row
 *    actually CALLED "Drywall lift" lost the lead on "Drywall lift template" to a
 *    longer row that beat it on weight. An honest label pointed straight at it:
 *    the heading went to "Closest to" and was RIGHT, because the row underneath
 *    was wrong. Rule 4 now reads the same live query rule 6 does — under the same
 *    separator gate, for the reason written beside it.
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
  /* The query exactly as he typed it, for the one job the normalized copy cannot
     do: hand a dropped word back in his own characters. */
  var RAW = "";
  /* How long a trailing token may be before the engine stops calling it "the
     word under his thumb". Below this, a token that matches nothing is a word in
     progress and is held back; at this length and above, nothing in the library
     begins with it or contains it, so it is a word this page does not have.
     Rule 7 in search() carries the measurement. */
  var UNDER_THUMB = 3;

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
    RAW = String(q || "");
    var qt = query.split(" ");

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

    /* WHAT MAY BE NAMED OUT LOUD, which is not the same set as what was dropped.
       The scorer already exempts the last token from strictness because it is the
       word under his cursor (`need` above), and the sentence has to make the same
       trade or it contradicts the engine it reports on: a one-character token has
       no prefix path in tokenScore() at all, so the first letter of every word
       after the first is noise for one keystroke. Naming it makes the line appear
       on "1/4 drill b" and vanish on "1/4 drill bi" — text flickering under his
       thumb on essentially every two-word query, which is the default way this
       box is used. So the trailing token is held back while he is still on it.

       RULE 7. HELD BACK IS NOT THE SAME AS FINISHED, AND THE HOLD-BACK'S OWN
       STATED COST WAS MEASURED WRONG. It read "a last word that really does
       match nothing goes unnamed until he types a space", as though the only
       casualty were a sentence. It is not: `say` empty makes rule 6's clause
       VACUOUS, so the label goes out as "exact" as well. Driven over 41,516
       searches on 33 surfaces, 3,181 answers were exact ONLY because the
       hold-back had emptied `say`, and 453 of them were a document this surface
       does not carry. "pipe wrenches" and "pipe lube" on av/write-up come back
       as the Damage / Pre-Existing Condition Note, labelled exact, with no
       sentence naming the word that was thrown away — the exact failure rule 6
       was written to end, walking in through the door rule 6 left open.

       SO THE HOLD-BACK IS THRESHOLDED, AND THE THRESHOLD IS EVIDENCE, NOT TASTE.
       He is "still on" a word only while the engine cannot yet tell: at one
       character there is no prefix path, at two the prefix path is live, and at
       three both prefix and infix are live. A trailing token of three characters
       that matched NOTHING begins no word and sits inside no word anywhere in
       this library, so it is not a word in progress — it is a word this page
       does not have, and it may be named and hedged on. Measured at that
       threshold: 451 of the 453 hedged, and on the KEYSTROKE corpus — every own
       name typed one character at a time, 13,659 queries, which is the only
       place a label can flicker — the cost is ZERO. Verbatim names 586/586 and
       authored aliases 864/864 unmoved; whole-name-plus-chrome 248/248 on the
       document libraries and 60/60 on the commons unmoved, because what survived
       is still the whole name of the row and rule 6 says so. */
    var say = noise;
    if (noise.length && qt.length > 1 && noise.indexOf(qt[qt.length - 1]) !== -1 &&
        qt[qt.length - 1].length < UNDER_THUMB && /[A-Za-z0-9]$/.test(RAW)) {
      say = [];
      for (k = 0; k < qt.length - 1; k++) if (noise.indexOf(qt[k]) !== -1) say.push(qt[k]);
    }

    /* Every token was noise — the query has nothing to do with this library.
       Rule 2: hand back the closest three rather than an empty box. */
    if (!live.length) return { hits: closest(ix, query, 3), mode: "none", noise: noise, noiseRaw: raws(say), q: query };

    /* WHAT HE ACTUALLY ASKED FOR, once rule 1 has taken its cut. Rule 4's ladder
       below and rule 6's label above both grade against THIS and not against the
       raw query, and they have to agree or the page contradicts itself: the
       ladder was reading `query` with the deleted word still in it, so "Drywall
       lift template" matched no name, drew NO phrase bonus at all, and the row
       actually CALLED "Drywall lift" lost the lead to a longer row that outscored
       it on raw weight. Bare "Drywall lift" led correctly, so one dropped word
       moved the answer — the exact thing tools/toolkit-gates/find-noise.mjs N7
       forbids, sitting on rows N7 never probed. Found by rule 6's own gate: the
       label went honest and the honesty pointed at the row. */
    var liveQ = [], lqi;
    for (lqi = 0; lqi < live.length; lqi++) liveQ.push(qt[live[lqi]]);
    /* AND ONLY ONCE A SEPARATOR SAYS HE IS FINISHED WITH THE DROPPED WORD, which
       is the same gate rule 6 stands on and it is not symmetry for its own sake.
       Mid-word, the remainder of "the d" is the bare word `the`, and handing
       rung 2 a single common word makes it fire on every title that happens to
       contain it while a row answering through an alias gets nothing: measured,
       149 mid-typing keystrokes changed which row led, all of them for the
       worse. While the word is under his thumb the ladder reads what he typed,
       exactly as it always has. */
    var lq = say.length ? liveQ.join(" ") : query;
    var lqj = say.length ? liveQ.join("") : qt.join("");

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
      /* RULE 4'S LADDER, AND EVERY RUNG OF IT IS LOAD-BEARING. He typed the whole
         title > the title SAYS that word > a nickname says it > the spaces-out
         form. Two things about this were wrong and each one cost real answers:
           · the nickname rung was written at 1.6, the same as the whole title,
             which put it ABOVE a title that says the word — "damage" on the AV
             page answered with the Incident / Near-Miss Report while the Damage
             Note sat underneath, labelled exact.
           · the title rung tested `indexOf`, a RAW SUBSTRING, so "co" matched
             inside "condition" and the Damage Note outranked the Change Write-Up
             whose nickname is literally CO. A phrase bonus that fires on two
             letters buried in a longer word is not evidence about a phrase, so
             the test is now at word boundaries, which is what it always meant. */
      if (p.n === lq) sc += pw * 1.6;                                               // rule 4
      else if ((" " + p.n + " ").indexOf(" " + lq + " ") !== -1) sc += pw * 1.4;
      else if (named(rows[i], lq, fields, ix.primary)) sc += pw * 1.2;              // rule 4, any name
      else if (lqj.length >= 4 && p.j.indexOf(lqj) !== -1) sc += pw * 0.9;
      scored.push({ it: rows[i].it, sc: sc, cover: cover, strong: strong, i: i });
    }
    if (!scored.length) return { hits: closest(ix, query, 3), mode: "none", noise: noise, noiseRaw: raws(say), q: query };

    var maxCover = 0;
    for (i = 0; i < scored.length; i++) if (scored[i].cover > maxCover) maxCover = scored[i].cover;
    var tier = scored.filter(function (x) { return x.cover === maxCover; });
    tier.sort(function (a, b) { return b.sc - a.sc || a.i - b.i; });

    /* "exact" is a claim about the row he is looking at first. */
    var lead = tier[0];

    /* RULE 6. COVERAGE OF WHAT SURVIVED IS NOT COVERAGE OF WHAT HE TYPED, and
       that is the other half of the same honesty rule 5 started. Rule 1 deletes
       a token that matches nothing here, and then the two clauses above ask
       whether the lead covered THE SURVIVORS — so "Inspection Note" on the AV
       page keeps `note`, answers it with the Damage / Pre-Existing Condition
       Note, and every check it is put to comes back clean. He named a document
       this library does not carry and was told he had an exact match.
       Measured over 17,910 cross-surface searches on fifteen trades: 7,736 came
       back having quietly deleted a word and 4,012 of those said EXACT.

       THE DISCRIMINATING FACT IS NOT HOW MANY WORDS SURVIVED. A three-lens panel
       reached for `live.length <= noise.length` and that predicate is dead: it
       hedges "Washout template" — a ONE-WORD document name plus the word a
       search box taught him to add — because it counts, and counting cannot tell
       the whole name of a thing from a piece of one. The question is whether
       what SURVIVED is a WHOLE NAME of the row he is being shown. In "Washout
       template" the survivor is the entire name and the deletion was chrome; in
       "Inspection Note" the survivor is a fragment of a longer name and the
       deletion was the word that discriminates. The engine already knows how to
       ask that — it is rule 4's `named()`, widened by one line to look at the
       primary field too.

       AND IT FIRES ON `say`, NOT ON `noise`, WHICH IS THE SAME TRADE THE
       SENTENCE ALREADY MAKES. A one-character token can only match exactly, so
       the first letter of every word after the first is noise for one keystroke:
       demoting on it would flip the heading to "Closest to" on "damage n" and
       back on "damage no", under his thumb, on the default way this box is used.
       A word we will not NAME out loud is not a word we may HEDGE on, and the
       moment a separator says he is finished with it we do both. */
    var honest = lead.cover === live.length && lead.strong === live.length &&
                 (!say.length || wholeName(rows[lead.i], lq, fields, ix.primary));

    return {
      hits: tier.map(function (x) { return x.it; }),
      mode: honest ? "exact" : "relaxed",
      noise: noise,
      noiseRaw: raws(say),
      q: query
    };
  }

  /* Rule 6's question, and rule 4's with the primary field put back. `named()`
     below skips the primary because rule 4's ladder has already tested it two
     rungs higher and a second bonus for the same evidence would double-count it.
     Rule 6 is asking a different question — is this row CALLED that — and the
     title is the first name a thing has. */
  function wholeName(row, query, fields, primary) {
    var w = row.f[primary].whole, i;
    for (i = 0; i < w.length; i++) if (w[i] === query) return true;
    return named(row, query, fields, primary);
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


  /* ── ADMITTING WHAT WAS THROWN AWAY ──────────────────────────────────────
   * Rule 1 drops a token that matches nothing in the library, and for
   * "template" and "form" that is exactly right — he added a word a search box
   * taught him to add. For a CONTENT word it is the search lying by omission:
   * "AHJ nuisance letter" on the AV page keeps only `letter`, answers that, and
   * says exact. Driven over 21,372 cross-surface searches, 3,631 came back
   * exact having quietly dropped a word, and 3,409 of those kept HALF OR LESS
   * of what he typed.
   *
   * THE SENTENCE LIVES HERE, WITH THE RULE THAT CAUSES IT. It shipped first as
   * four inline lines in commons/commons.js and the other 26 surfaces that share
   * this engine said nothing at all; a second copy is how the two drift, so
   * there is one and the callers ask for it. Three things the inline copy got
   * wrong and could not have seen alone, because one surface's data does not
   * contain them:
   *   · PLURAL. "nothing here uses that word" over three dropped words.
   *   · DUPLICATES. "USB-A -> USB-B" drops `usb` twice and printed it twice.
   *   · HIS CASE. He typed AHJ; the array holds the normalized `ahj`, and
   *     handing back a mangled version of his own word is a weaker admission
   *     than handing back the word. Recovered from the raw query, never
   *     reconstructed, so what he sees is a slice of what he typed.
   */
  /* SEPARATORS, and everything else is part of a word. `norm()` keeps only
     [a-z0-9], so it shreds an accented word — café indexes as `caf`, résumé as
     `r` + `sum` — and this file ships beside a Spanish vocabulary block that two
     trades authored on purpose (sitework/items.js, electrical/items.js §TAG_ES).
     Handing that man back “caf” dressed up as the word he typed is worse than
     handing him nothing, so a recovered token EXPANDS over anything that is not
     a separator until it is the whole word again. A fraction is one thing a
     tradesman types as one thing, so a slash between two digits is not a
     separator either — otherwise "3/4 EMT strap" reports “3”, “4” and “EMT” and
     buries the only word he would recognise under two bare digits. */
  function isSep(str, i) {
    var c = str.charAt(i);
    if (!c) return true;
    if (c === "/" && /[0-9]/.test(str.charAt(i - 1) || "") && /[0-9]/.test(str.charAt(i + 1) || "")) return false;
    return /[\s!-\/:-@\[-`{-~]/.test(c);
  }

  function raws(noise) {
    var seen = {}, out = [], i, k, t, at, a, b, w;
    var low = RAW.toLowerCase();
    for (i = 0; i < noise.length; i++) {
      t = noise[i];
      if (!t) continue;
      at = -1;
      /* The occurrence that is a whole word wins; failing that the first one,
         because a token normalized out of a longer word is still inside it. */
      for (k = low.indexOf(t); k !== -1; k = low.indexOf(t, k + 1)) {
        if (at === -1) at = k;
        if (isSep(RAW, k - 1) && isSep(RAW, k + t.length)) { at = k; break; }
      }
      if (at === -1) { w = t; }
      else {
        a = at; b = at + t.length;
        while (a > 0 && !isSep(RAW, a - 1)) a--;
        while (b < RAW.length && !isSep(RAW, b)) b++;
        w = RAW.slice(a, b);
      }
      /* Deduped on what he SEES, not on the token: résumé shreds into two
         tokens that both expand back to the one word, and naming it twice is
         the defect this de-duplication exists to prevent. */
      k = w.toLowerCase();
      if (seen[k]) continue;
      seen[k] = 1;
      out.push(w);
    }
    return out;
  }

  /* The caller renders this; it never decides whether the answer was good. The
     document IS usually what he asked for and the label is the label's job --
     this only names what the engine deleted and lets him judge it. Silent on
     "none", where the heading has already told him nothing matched and saying it
     twice reads as a broken sentence. */
  function dropped(res) {
    if (!res || res.mode === "none" || res.mode === "all") return "";
    var n = res.noiseRaw || res.noise || [];
    if (!n.length) return "";
    return "Ignored \u201C" + n.join("\u201D, \u201C") + "\u201D \u2014 nothing here uses " +
           (n.length === 1 ? "that word." : "those words.");
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

  window.Find = { index: index, search: search, norm: norm, toks: toks, squash: squash,
                  dist: dist, dropped: dropped,
                  /* Rule 7's line, exported so tools/toolkit-gates/find-noise.mjs
                     probes either side of THIS number and never a copy of it. */
                  underThumb: UNDER_THUMB };
})();
