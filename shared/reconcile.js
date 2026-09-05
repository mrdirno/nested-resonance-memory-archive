/* FIELD TOOLKIT — THE THIRD MESSAGE: reconciling an answer against the list that asked for it.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * av/AV_SOCIETY.md §THE INTERFACE. The cross-boundary loop shipped in two
 * halves and stopped one message short of closing:
 *
 *   1. I walk the job and send you a list          → <trade>/rough-in-request.html
 *   2. You answer it line by line and send it back → <trade>/answer-back.html
 *   3. ...and then I sit there with your reply in one hand and my own list on
 *      the other screen, reading down both, tapping my rows one at a time.
 *
 * Step 3 is the one nobody builds, and it is where the loop leaks. Twenty asks
 * come back as one message; he ticks the eight he can find, misses two, and
 * never notices the three items the other man said nothing at all about — which
 * are the only three that matter, because silence is not a no and it is not a
 * yes, it is the thing that shows up as a hole in a closed wall.
 *
 * THIS IS AN INTAKE, NOT A FOURTH PAGE. The rows already live on the request
 * page and the answer is about those rows; a separate page would need its own
 * copy of them, and a second copy of a list is a second version of the truth.
 *
 * THE JOIN IS THE WHOLE PROBLEM, AND IT IS A JOIN ON PROSE.
 * A wrong join silently marks the wrong item committed, which is worse than no
 * automation at all — so three rules hold the design up:
 *
 *   · PROPOSE, NEVER APPLY. Nothing on the list moves until he taps the button,
 *     and every pair is on the glass, his line beside our row, before he does.
 *     A pair we are not sure of comes in switched OFF and says so.
 *   · THE COMMON CASE IS NOT FUZZY AT ALL. answer-back stores his counterpart's
 *     ask verbatim and never re-phrases it, so when the other man used the
 *     toolkit the line coming back IS the line this page sent, character for
 *     character. That is an EXACT match and it is treated as one. Fuzzy scoring
 *     is the fallback for a hand-typed reply, and it is deliberately timid.
 *   · WE ONLY EVER TICK THE FIRST RUNG. His answer is a claim by him. The top of
 *     this page's ladder is the requester having LAID EYES ON IT, and a text
 *     message is not eyes. Even "in already" ticks Committed and stops there.
 *     (§SCARS — a default is a claim.)
 *
 * AND THE OUTPUT NOBODY ELSE CAN COMPUTE: what he never mentioned. Only the
 * page holding the original list knows which asks came back unanswered, because
 * only it knows what was asked. That block is free, it needs no join to be
 * right — an unmatched row is unmatched — and it is the reason to open this.
 *
 * Client-side only, dependency-free, nothing leaves the browser, nothing is
 * stored: his message is another company's document and it stays in the box.
 *
 * TWO LINES TO ADD IT TO A ROW-LOG REQUEST PAGE:
 *   <script src="../shared/reconcile.js"></script>
 *   Reconcile.mount({ after: ..., rows: ..., matchText: ..., onApply: ... });
 */
(function () {
  "use strict";

  /* ── THE VERDICT VOCABULARY ───────────────────────────────────────────────
   * These are answer-back's ladder, not a trade's words: the four rungs are the
   * ENGINE's and every trade ships the same four (the trade owns the words
   * AROUND them, never the rungs). Naming them here is a coupling between two
   * files, so a gate asserts it rather than a comment hoping for the best —
   * tools/toolkit-gates/reconcile-join.mjs reads answer-back's ANSWERS array off
   * disk and fails if any rung lands here unclassified. */
  /* THE LADDER IS PER-TRADE NOW, AND THIS MAP HAD NOT BEEN TOLD. answer-back
   * reads POSITIONS, never words — [0] is the promise that wants a date, [1] is
   * already settled, [2] is declined, [3] is blocked on the other side — so a
   * trade may say all four in its own vocabulary. `creative` did, and not one of
   * its four rungs was classified here, which made every answer a creative sent
   * read to the requester as "he didn't say yes or no": the exact silent failure
   * the classification exists to prevent. It survived because
   * reconcile-join.mjs read this ladder off the page with a regex that a later,
   * correct refactor stopped matching — a gate failing on its own wrapper while
   * quietly running none of its real checks. Both are fixed in the same cycle;
   * the gate now derives every trade's ladder off disk, so the NEXT trade that
   * renames a rung fails the gate instead of failing a stranger. */
  var VERDICTS = {
    "will do": "yes",
    "in already": "in",
    "cant": "no",
    "cannot": "no",
    "need to know": "ask",
    // creative/items.js — same four positions, the trade's own words.
    "doing it": "yes",
    "already in": "in",
    "thats an extra": "no",   // [2] is DECLINED: not committed under this list
    "need from you": "ask",
    // flooring/items.js — the punch-back rungs (answers[] landed 2026-08-24).
    "not mine": "no",                // [2] declined: another trade's line
    "damage needs a ticket": "ask",  // [3] blocked on their side: moves when the ticket does
    // painting/items.js — the walk-back rungs, same four positions.
    "well hit it": "yes",
    "done already": "in",
    "not paint": "no",               // [2] declined: another trade's work wearing paint
    "need the room": "ask",          // [3] blocked on their side: moves the day the room clears
    // doors/items.js — the punch-back rungs. [0] and [1] are shared with painting
    // and [2] with flooring; only the fourth is new, and it is new because this
    // trade needed a rung the other thirteen did not. An installer standing at an
    // opening frequently CANNOT say yes: what is being asked for is a hardware or
    // label question whose answer lives in the approved submittal and with the
    // people who stamp it. That is not a refusal and it is not a commitment — it
    // is an ask pointed at somebody else, which is exactly position [3].
    "not my call": "ask",
    // landscape/items.js — the walk-back rungs. [0], [1] and [2] are shared
    // with painting and doors; only the fourth is new. On a landscape punch a
    // dying plant is very often the CLOCK talking — a zone that is off, a
    // controller somebody changed, a restriction nobody passed on — and that
    // answer lives with whoever holds the controller, not with the man holding
    // the shovel. Not a refusal, not a commitment: an ask pointed elsewhere.
    "its the water": "ask",
    // paving/items.js — the walk-back rungs. [0], [1] and [2] are shared with
    // painting, doors and landscape; only the fourth is new. On a lot punch a
    // stall count, an arrow, a fire-lane length or an accessible pair the
    // owner wants moved is the SHEET talking — a plan question that lives with
    // the civil and the owner who stamp it, not with the man holding the
    // striper. Not a refusal, not a commitment: an ask pointed elsewhere.
    "its the plan": "ask"
  };

  /* MIN is the floor for PROPOSING a pair at all. There is deliberately no score
   * that grants certainty — see `sure` in pair(). SURE survives only as the bar
   * for "this is unambiguously the same row" in the flagged-duplicate pass.
   *
   * WHY NO FUZZY PATH TO SURE (found by an adversarial audit, 2026-08-11): Dice
   * has no notion of an IDENTIFYING token. A row of N tokens whose line differs
   * in k of them scores 1 - k/N, and every real row here is 8-14 tokens long —
   * room, ask, spec, height, milestone, trade. So a 12-token row tolerated THREE
   * wrong tokens and still cleared 0.75. One wrong room number — CR-208 answered
   * against a CR-206 row A never asked about — scored 0.917, arrived switched ON,
   * and hid his line because the pair was "sure". The more detail a man puts on a
   * row, the more wrong tokens the ratio would forgive. A ratio cannot tell the
   * difference between a typo and a different room, so it does not get a vote. */
  var SCORE = { MIN: 0.45, SURE: 0.75, MARGIN: 0.12 };

  function norm(s) {
    return String(s == null ? "" : s)
      .toLowerCase()
      .replace(/[‘’']/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }
  function tokens(s) {
    var seen = {}, out = [];
    norm(s).split(" ").forEach(function (t) { if (t && !seen[t]) { seen[t] = 1; out.push(t); } });
    return out;
  }
  function verdictOf(s) {
    var n = norm(s);
    return Object.prototype.hasOwnProperty.call(VERDICTS, n) ? VERDICTS[n] : "";
  }

  /* ── READING HIS MESSAGE ──────────────────────────────────────────────────
   * The drop rules fire only on lines that are STRUCTURALLY not an ask — a
   * `Key:` header, a count line, a group heading, the sign-off. They never fire
   * on prose, because a hand-typed ask IS prose.
   *
   * This parser is allowed to be gentler than answer-back's, and the asymmetry
   * is the point: over there a dropped line is a commitment one company thinks
   * it has and the other never made. Here a line that survives and matches
   * nothing lands in "couldn't place it", visible, having changed nothing. So
   * when in doubt, keep it and show it. */
  var HEADING = /^(.+?)\s+[—-]\s+(\d+)\s+ROWS?$/i;
  var FLAGHEAD = /^flagged\s*[—-]\s*\d+\s*$/i;
  /* THE COLON IS LOAD-BEARING. Without it `^off\b` eats "Off the main tee ·
   * hold a full tile", which is a real ask in two of the six vocabularies —
   * and a dropped ask here becomes a row this page reports as never mentioned,
   * which is a claim about the other company that isn't true. Our own headers
   * all carry the colon; the one that doesn't gets its own rule. */
  var KEYLINE = /^(job|to|from|cc|bcc|off|call me|still open|subject|date|sent|re|attn)\s*:\s?/i;
  var ONLIST = /^on your list off\b/i;
  var COUNTLINE = /^\d+\s+(lines?|items?|rows?)\b/i;
  var RULELINE = /^[-=_·•*~]{3,}$/;
  /* Only OUR OWN sign-off shapes, matched narrowly — the same list answer-back
   * uses, plus the two lines that close an ANSWER rather than a request (this
   * parser reads the other direction). A broad prose rule would eat "GC says
   * that one is a change order", which is an ask carrying the most important
   * qualifier a man can put on it. */
  var DISCLAIM = /(not an rfi|isn'?t an rfi|isn'?t a change order|not a change order|doesn'?t authori[sz]e|does not authori[sz]e|against your own set|before anybody roughs|verify (it|them|that) before|no price on it|doesn'?t change anybody|nothing here changes)/i;

  /* THE SIGN-OFF IS TWO LINES AND ONLY ONE OF THEM IS RECOGNISABLE — the first
   * is a per-trade sentence a foreman wrote ("anything you can't hit, call me
   * before you cover it"), and there is no pattern to match arbitrary prose on
   * that would not also eat a hand-typed ask. But the STRUCTURE is fixed: the
   * closing block is emitted after a blank line and runs to the end. So once one
   * line proves this is one of our documents, everything from that block's start
   * is tail. Lifted whole from answer-back's parser, where it was already paid
   * for — a second solution to a solved problem is a second thing to maintain. */
  function tailStart(lines) {
    /* THE FIRST DISCLAIM HIT ANYWHERE USED TO CUT THE DOCUMENT FROM THAT
     * PARAGRAPH TO THE END, and inside a document that paragraph is a GROUP
     * HEADING — so one row killed every answer under it. It is not theoretical:
     * `av/items.js` ships the spec "Walk the wall with me before anybody roughs
     * it", two taps to put on a list, and it matches /before anybody roughs/.
     * A reply carrying that row parsed to ZERO answers and the page told a
     * foreman the other company had never mentioned any of them.
     *
     * The sign-off is not "a paragraph containing a disclaimer". It is THE LAST
     * BLOCK, always, in both documents this parser reads. So look at that block
     * and nowhere else: a disclaimer sentence in the middle of a message is a
     * man talking, not our footer. */
    var end = lines.length - 1;
    while (end >= 0 && lines[end].trim() === "") end--;
    if (end < 0) return -1;
    var start = end;
    while (start > 0 && lines[start - 1].trim() !== "") start--;
    for (var i = start; i <= end; i++) if (DISCLAIM.test(lines[i].trim())) return start;
    return -1;
  }

  /* Grouped by anything other than his answer, the rung rides IN the line
   * instead of in the heading above it. Read it off the end of the ask so the
   * verdict is right either way. Shared by every candidate split of a line. */
  function readOwn(ask, tail) {
    var own = "";
    var m = /\s*[·|]\s*([A-Za-z][A-Za-z' ]{1,14})\s*$/.exec(ask);
    if (m && verdictOf(m[1])) { own = verdictOf(m[1]); ask = ask.slice(0, m.index).trim(); }
    return { ask: ask, tail: tail, own: own };
  }

  function parseAnswer(text) {
    /* A PASTED EMAIL DOES NOT CARRY THE SPACES IT LOOKS LIKE IT CARRIES. Mail
     * clients wrap an em dash in NO-BREAK SPACE so it never starts a line, and
     * `indexOf(" — ")` then misses the seam entirely: his date ends up inside
     * the ask, the pair still matches, and the page prints "no date on it" over
     * a line that says Thursday. Every unicode space becomes a plain one first. */
    var raw = String(text == null ? "" : text)
      .replace(/[\u00A0\u2007\u202F\u2000-\u200A\u205F\u3000]/g, " ")
      .split(/\r?\n/);
    /* A PASTE IS ONLY A MESSAGE IF IT LOOKS LIKE ONE. Without this the first
     * line of a one-line reply — "back box CR-204 60 aff — yeah thursday" — is
     * thrown away as a subject, and the man who pasted his answer gets an empty
     * report. (Found by the gate on its first run, which is what it is for.) */
    /* "THIS PASTE IS ONE OF OUR DOCUMENTS" HAS A STRUCTURE, not just a keyword.
     * `raw.some(KEYLINE)` was true for a bare three-line reply that happened to
     * end with "Call me: 555-0134", and the subject rule below then ate the
     * first of his three answers. Our documents are: subject, blank, `Key:`
     * lines — or they carry group headings. Nothing else counts. */
    var hasHead = (function () {
      for (var i = 0; i < raw.length; i++) {
        if (HEADING.test(raw[i].trim())) return true;
        if (raw[i].trim() !== "") continue;
        var j = i + 1;
        while (j < raw.length && raw[j].trim() === "") j++;
        if (j < raw.length && KEYLINE.test(raw[j].trim())) return true;
      }
      return false;
    })();
    /* NOT `tail` — the loop below declares its own `tail` for the half of a line
     * that carries his answer, and a `var` inside the callback hoists over this
     * one, so the cutoff read `undefined` on every line and the whole sign-off
     * block survived. Two different things under one name (§SCARS). */
    var signOff = tailStart(raw);
    var out = [], dropped = [], verdict = "", flagged = false, ix = 0, seenFirst = false;

    raw.forEach(function (line, i) {
      var t = String(line).replace(/\s+$/, "").trim();
      if (!t) return;
      if (signOff >= 0 && i >= signOff) { dropped.push(t); return; }

      /* THE FIRST LINE OF ONE OF OUR DOCUMENTS IS A SUBJECT — "Building C — my
       * answer on your list — Aug 11" — built for an inbox search in October. */
      var first = !seenFirst; seenFirst = true;
      if (first && hasHead && t.indexOf(" — ") > -1 && !HEADING.test(t)) { dropped.push(t); return; }

      var h = HEADING.exec(t);
      if (h) { verdict = verdictOf(h[1]); flagged = false; dropped.push(t); return; }
      if (FLAGHEAD.test(t)) { verdict = ""; flagged = true; dropped.push(t); return; }
      /* DISCLAIM is NOT in this list, deliberately. It is a prose rule, and a
       * prose rule applied line by line drops the same real asks the tail rule
       * above used to drop wholesale — "walk the wall with me before anybody
       * roughs it" is a spec this toolkit ships, not our sign-off. Its only job
       * is recognising the final block. */
      if (KEYLINE.test(t) || ONLIST.test(t) || COUNTLINE.test(t) || RULELINE.test(t)) { dropped.push(t); return; }

      /* HIS LINE, THEN A DASH, THEN HIS ANSWER — that is answer-back's row and
       * the dash is the seam between what we asked for and what he committed
       * to. Split on the FIRST one: everything left of it is our words coming
       * home, which is exactly what the join wants. */
      var body = t.replace(/^[-–—•*]\s+/, "");
      /* THE SEAM IS NOT ALWAYS THE FIRST DASH (found 2026-09-04, trade #17, by
       * an adversarial drive of the round trip). A request line is our own
       * words coming home, and our own words carry em dashes: "The set I'm
       * paving to — sheet and rev" is one paving ask; painting ships 39 specs
       * with one, framing 21, av 13 — every trade on the rack. Split on the
       * FIRST dash and the ask comes home cut in half, the join scores it
       * against a row it half-matches, and an answer that said Thursday lands
       * as "couldn't place" or "not sure" — silently, on the loop this page
       * exists for. So EVERY seam is offered: the first stays the default (a
       * line with one dash is unchanged), and pair() below adopts whichever
       * split a row actually matches, character for character where it can. */
      var seams = [], sep = " — ", at = body.indexOf(sep);
      if (at < 0) { sep = " - "; at = body.indexOf(sep); }
      while (at > -1) { seams.push(at); at = body.indexOf(sep, at + sep.length); }
      var splits = seams.length
        ? seams.map(function (k) { return readOwn(body.slice(0, k).trim(), body.slice(k + sep.length).trim()); })
        : [readOwn(body, "")];
      /* AND THE LINE UNCUT. Grouped by date the answer rides in the heading and
       * the line carries no tail at all — so a dash inside our own words is the
       * only dash on the line, and the one cut on offer is the wrong one. The
       * whole line is a candidate too; a row that matches it whole wins. */
      if (seams.length) splits.push(readOwn(body, ""));
      var first = splits[0];

      out.push({
        ix: ix++, raw: t, ask: first.ask, tail: first.tail,
        verdict: first.own || verdict, flagged: flagged,
        /* Every other way this line could be cut, for the join to try. */
        alts: splits.slice(1).map(function (sp) { return { ask: sp.ask, tail: sp.tail, verdict: sp.own || verdict }; })
      });
    });

    return { lines: out, dropped: dropped };
  }

  /* ── THE JOIN ─────────────────────────────────────────────────────────────
   * Dice over the two token sets, which is symmetric on purpose: containment
   * alone lets a two-word row ("sleeve") swallow any line that happens to say
   * sleeve, and on a real list there are six of those in six rooms. Dice
   * punishes the short row for everything the line says that it does not.
   *
   * Then two guards no score can provide:
   *   · an EXACT normalised match is not a guess and skips the margin test;
   *   · every row and every line is claimed once, best pair first, so one
   *     strong line cannot take three rows with it.
   */
  function pair(rowsIn, lines) {
    var cands = [];
    /* A LINE WITH MORE THAN ONE DASH IS CUT WHERE A ROW SAYS IT IS CUT. Before
     * any scoring, each line tries every split parseAnswer offered against
     * every form of every row; the split with the best score wins the line
     * (an exact match wins outright), and the default first-dash split is
     * kept when nothing beats it — so a line with one dash behaves exactly as
     * before. Done as a pass of its own so the pairing below sees one ask per
     * line, never a moving target. */
    var rowForms = (rowsIn || []).map(function (r) {
      return (Array.isArray(r.text) ? r.text : [r.text])
        .filter(function (s) { return s && String(s).trim(); })
        .map(function (s) { return { toks: tokens(s), n: norm(s) }; })
        .filter(function (f) { return f.toks.length; });
    });
    (lines || []).forEach(function (l) {
      if (!l.alts || !l.alts.length) return;
      var options = [{ ask: l.ask, tail: l.tail, verdict: l.verdict }].concat(l.alts);
      var bestIx = 0, best = -1;
      options.forEach(function (o, oi) {
        var L = tokens(o.ask); if (!L.length) return;
        var set = {}; L.forEach(function (t) { set[t] = 1; });
        var nl = norm(o.ask), top = 0;
        rowForms.forEach(function (forms) {
          forms.forEach(function (f) {
            if (f.n === nl) { top = 1; return; }
            var hit = 0; f.toks.forEach(function (t) { if (set[t]) hit++; });
            var sc = (2 * hit) / (f.toks.length + L.length);
            if (sc > top) top = sc;
          });
        });
        if (top > best) { best = top; bestIx = oi; }
      });
      if (bestIx > 0) { var w = options[bestIx]; l.ask = w.ask; l.tail = w.tail; l.verdict = w.verdict; }
    });
    (rowsIn || []).forEach(function (r) {
      /* A ROW HAS MORE THAN ONE TRUE FORM. The document drops whichever axis it
       * is grouped by, because that axis is already the heading above the line
       * — so the same row reads three different ways depending on how the list
       * was grouped the day it was sent, and the page cannot know which one the
       * other man is holding. Every form it could have taken is offered; the
       * best one wins, and one of them is usually his line character for
       * character. Without this the exact match never fires and every pair on a
       * perfectly clean round trip comes back "not sure". */
      var forms = (Array.isArray(r.text) ? r.text : [r.text])
        .filter(function (s) { return s && String(s).trim(); })
        .map(function (s) { return { toks: tokens(s), n: norm(s) }; })
        .filter(function (f) { return f.toks.length; });
      if (!forms.length) return;

      (lines || []).forEach(function (l) {
        var L = tokens(l.ask);
        if (!L.length) return;
        var set = {}; L.forEach(function (t) { set[t] = 1; });
        var nl = norm(l.ask), score = 0, exact = false;
        forms.forEach(function (f) {
          if (f.n === nl) exact = true;
          var hit = 0;
          f.toks.forEach(function (t) { if (set[t]) hit++; });
          var s = (2 * hit) / (f.toks.length + L.length);
          if (s > score) score = s;
        });
        if (exact) score = 1;
        if (score < SCORE.MIN) return;
        cands.push({ rowId: r.id, lineIx: l.ix, score: score, exact: exact });
      });
    });

    /* The runner-up FOR THIS LINE, measured across every row — including rows
     * another line will end up claiming. That over-states the ambiguity a
     * little and it over-states it in the safe direction: an unsure pair is
     * shown switched off, never dropped. */
    /* HOW MANY ROWS MATCH THIS LINE EXACTLY. More than one is not a near miss —
     * it is the SAME STRING, and no amount of scoring can separate them.
     * It happens on the most ordinary list there is: `matchText` offers a form
     * with the ROOM dropped (the document drops whichever axis it was grouped
     * by), so the same device at the same height in three different rooms
     * produces three identical strings. Answered "will do, will do, can't",
     * WHICH ROOM HE REFUSED IS NOT IN HIS MESSAGE — and the greedy sort would
     * have handed it out by row id and called all three exact and sure. */
    var exactCount = {};
    cands.forEach(function (c) { if (c.exact) exactCount[c.lineIx] = (exactCount[c.lineIx] || 0) + 1; });

    cands.sort(function (a, b) {
      return (b.score - a.score) || (a.rowId - b.rowId) || (a.lineIx - b.lineIx);
    });

    var usedRow = {}, usedLine = {}, pairs = [];
    cands.forEach(function (c) {
      if (usedRow[c.rowId] || usedLine[c.lineIx]) return;
      usedRow[c.rowId] = 1; usedLine[c.lineIx] = 1;
      /* ONE ROW, ONE LINE, CHARACTER FOR CHARACTER — that is the only thing this
       * page is willing to call certain, and it is not a compromise: it is the
       * normal case, because answer-back stores the ask verbatim. Everything
       * else is a proposal he has to look at and switch on himself. */
      var sure = c.exact && exactCount[c.lineIx] === 1;
      pairs.push({ rowId: c.rowId, lineIx: c.lineIx, score: c.score, exact: c.exact, sure: sure });
    });

    var unplaced = (lines || []).filter(function (l) { return !usedLine[l.ix]; }).map(function (l) { return l.ix; });
    var unmatched = (rowsIn || []).filter(function (r) { return !usedRow[r.id]; }).map(function (r) { return r.id; });
    return { pairs: pairs, unplaced: unplaced, unmatched: unmatched };
  }

  /* ── THE SURFACE ──────────────────────────────────────────────────────────
   * Builds its own card and inserts it after the list it is about, so adding
   * this to a page is a script tag and a mount call. */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : (many || one + "s")); }
  function firstForm(t) { return Array.isArray(t) ? (t[0] || "") : (t || ""); }

  function mount(cfg) {
    cfg = cfg || {};
    var host = typeof cfg.after === "string" ? document.querySelector(cfg.after) : cfg.after;
    if (!host || !host.parentNode) return null;

    var W = cfg.words || {};
    var commitLabel = cfg.commitLabel || "Committed";
    var report = null, chosen = {};

    var card = el("section", "card rc-card");
    card.id = "rcCard";
    card.innerHTML =
      '<h2>' + esc(W.title || "He answered") + ' <span class="why">— ' + esc(W.why || "paste his reply, we line it up against your list") + '</span></h2>'
      + '<details class="more rc-intake" id="rcIntake" open style="margin-top:0;border-top:0;padding-top:0">'
      + '<summary id="rcIntakeSum">Paste his answer</summary>'
      + '<p class="note" style="margin:10px 0 8px">' + esc(W.lede || "Paste the whole thing — header, sign-off, all of it. We match it to the rows you already sent him, tick nothing until you say so, and tell you what he never mentioned.") + '</p>'
      + '<textarea id="rcPaste" placeholder="' + esc(W.placeholder || "Building C — my answer on your list — Aug 11\n\nWILL DO — 2 ROWS\nCR-204 · back box + mud ring · 4-11/16 sq · 60 AFF — Thursday\nCR-204 · conduit to the ceiling · 1in — with the crew Tuesday") + '"></textarea>'
      + '<div class="outrow" style="margin:8px 0 0"><button type="button" class="btn" id="rcGo">Line it up</button></div>'
      + '</details>'
      + '<p class="note" id="rcMsg" style="margin:10px 0 0" hidden></p>'
      + '<div id="rcOut"></div>';
    host.parentNode.insertBefore(card, host.nextSibling);

    var $ = function (s) { return card.querySelector(s); };
    var out = $("#rcOut"), msg = $("#rcMsg");

    function say(html) { msg.innerHTML = html; msg.hidden = !html; }

    function rowsFor() {
      return (cfg.rows ? cfg.rows() : []).map(function (r) {
        return {
          id: r.id,
          text: cfg.matchText ? cfg.matchText(r.values, r) : "",
          label: (cfg.label ? cfg.label(r.values, r) : "") || firstForm(cfg.matchText ? cfg.matchText(r.values, r) : ""),
          sub: cfg.sub ? cfg.sub(r.values, r) : "",
          settled: cfg.settled ? !!cfg.settled(r.values, r) : false,
          scope: cfg.scopeOf ? cfg.scopeOf(r.values, r) : "",
          row: r
        };
      });
    }

    function build(text) {
      var parsed = parseAnswer(text);
      var rws = rowsFor();
      var joined = pair(rws, parsed.lines);
      var byId = {}, byIx = {};
      rws.forEach(function (r) { byId[r.id] = r; });
      parsed.lines.forEach(function (l) { byIx[l.ix] = l; });

      /* ── HIS FLAG IS PRINTED TWICE AND THE QUIETER COPY WAS WINNING ──────
       * answer-back emits a flagged row in its answer block AND again under
       * FLAGGED. Two lines, one row, and a 1:1 join hands the row to whichever
       * scored higher — which is the plain body line, because the flagged copy
       * carries an extra word. So the flag itself ("Not mine", "Not on my set")
       * dropped into the couldn't-place drawer, and the single loudest thing a
       * reply can say — THAT ISN'T MY SCOPE, YOU ASKED THE WRONG COMPANY —
       * never reached "he pushed back on these".
       * Re-run the same join, one row against one line, rather than inventing a
       * second notion of "these are the same item". */
      var flagFor = {};
      joined.unplaced.slice().forEach(function (ix) {
        var l = byIx[ix];
        if (!l || !l.flagged) return;
        for (var k = 0; k < joined.pairs.length; k++) {
          var pr = joined.pairs[k];
          if (flagFor[pr.rowId]) continue;
          var r = byId[pr.rowId];
          var probe = pair([{ id: r.id, text: r.text }], [l]);
          if (probe.pairs.length && probe.pairs[0].score >= SCORE.SURE) {
            flagFor[pr.rowId] = l;
            joined.unplaced = joined.unplaced.filter(function (x) { return x !== ix; });
            break;
          }
        }
      });

      var yes = [], push = [], quiet = [], mute = [];
      joined.pairs.forEach(function (p) {
        var r = byId[p.rowId], l = byIx[p.lineIx];
        var fl = flagFor[p.rowId] || (l.flagged ? l : null);
        var item = {
          row: r, line: fl || l, sure: p.sure, exact: p.exact, score: p.score,
          flagWord: fl ? String(fl.ask).split(" · ")[0] : ""
        };
        if (fl || l.verdict === "no" || l.verdict === "ask") push.push(item);
        else if (l.verdict === "yes" || l.verdict === "in") yes.push(item);
        else mute.push(item);                       // he wrote back, but said neither
      });

      /* ── NARROW THE SILENCE TO WHAT HE WAS ACTUALLY ASKED ────────────────
       * One walk, N messages: this list holds asks for three companies, so a
       * reply from one of them says nothing about the other two, and printing
       * their rows as HIS silence is the page inventing a grievance out of a
       * filter it forgot to apply.
       * A SET, not a single scope. The old all-or-nothing collapsed the moment
       * one line crossed trades — one "is that mine or the GC's?" and the GC's
       * unanswered rows landed in the electrician's silence. Now: a row is his
       * silence only if he answered something for that receiver. */
      var scopeSet = {}, scopeList = [];
      joined.pairs.forEach(function (p) {
        var s = (byId[p.rowId] || {}).scope || "";
        if (!s || scopeSet[s]) return;
        scopeSet[s] = 1; scopeList.push(s);
      });

      joined.unmatched.forEach(function (id) {
        var r = byId[id];
        if (!r || r.settled) return;                 // already answered or already in
        if (scopeList.length && r.scope && !scopeSet[r.scope]) return;
        quiet.push(r);
      });

      /* NAMING HIM IS A CLAIM ABOUT EVERY ROW IN THE BLOCK. "…and they're all on
       * the electrician's list" was printed whenever one receiver appeared among
       * the PAIRS, while the block itself deliberately keeps rows with no
       * receiver at all — so a row on nobody's list was announced as being on
       * his. Say his name only when it is true of every row shown. */
      var scoped = (scopeList.length === 1 && quiet.length
        && quiet.every(function (r) { return r.scope === scopeList[0]; })) ? scopeList[0] : "";

      return {
        yes: yes, push: push, mute: mute, quiet: quiet,
        /* TWO DIFFERENT THINGS, AND MERGING THEM MADE A CLEAN ROUND TRIP READ
         * AS A FAILURE: "10 lines we couldn't place" on a reply where every
         * single ask matched, because his header and our own sign-off counted
         * as misses. UNPLACED is a line of his we could not match to anything
         * you asked for — the only one that means something is wrong. SKIPPED
         * is the chrome we recognised and stepped over. Both are shown, because
         * a real answer misread as a header turns into a row this page reports
         * as never mentioned, which is a false claim about another company —
         * but only the first one is allowed to look like a miss. */
        unplaced: joined.unplaced.map(function (i) { return byIx[i].raw; }),
        skipped: parsed.dropped,
        lines: parsed.lines.length,
        scopeName: scoped && cfg.scopeName ? cfg.scopeName(scoped) : ""
      };
    }

    /* THE DEFAULT IS THE SAFETY PROPERTY, so it lives in one function and is
     * read everywhere. A pair we are SURE of comes in switched on — that is the
     * clean round trip, and making a man re-tick twenty exact matches is the
     * "ticking beats typing" law failing on its own surface. A pair we are NOT
     * sure of comes in switched OFF, because the whole design rests on a wrong
     * join never being able to reach the list unless he put it there himself.
     * `chosen` only ever holds what he EXPLICITLY toggled, so his choices
     * survive a rebuild and the default still applies to everything else. */
    function isOn(item) {
      if (!item) return false;
      var v = chosen[item.row.id];
      return v === undefined ? !!item.sure : v !== false;
    }
    function pairOf(id) {
      if (!report) return null;
      return report.yes.filter(function (i) { return i.row.id === id; })[0] || null;
    }

    function pairHTML(item, tickable) {
      var on = tickable ? isOn(item) : false;
      var tag = "";
      if (item.flagWord) tag = '<span class="rc-tag rc-warn">' + esc(item.flagWord) + "</span>";
      else if (item.line.verdict === "in") tag = '<span class="rc-tag">he says it\'s in</span>';
      if (!item.sure) tag += '<span class="rc-tag rc-warn">not sure it\'s the same one</span>';
      if (!tickable && item.row.settled) tag += '<span class="rc-tag">already ' + esc(String(item.row.row.values[cfg.commitKey || "status"] || "").toLowerCase()) + '</span>';
      /* THE EVIDENCE, SHOWN EXACTLY WHEN IT IS NEEDED. On a pair we are unsure
       * of, his whole line is the only way to judge whether it is the same
       * item, so it goes on the glass. On a sure pair it is our own line coming
       * home and repeating it says nothing — what is worth a line there is what
       * he ADDED, and when he added nothing the missing thing is the date.
       * Everybody leaves the date out of a reply and it is exactly what gets
       * argued about later. */
      var his = item.line.tail;
      if (!item.sure) his = item.line.raw;
      else if (item.flagWord) his = item.line.raw;
      else if (!his) {
        /* WHAT HE LEFT OUT IS THE ACTIONABLE HALF, and it is a different thing
         * on each rung. Echoing our own row back at him here says nothing; the
         * gap says what to chase. */
        his = item.line.verdict === "yes" ? "no date on it"
          : item.line.verdict === "no" ? "he didn't say why"
            : item.line.verdict === "ask" ? "he didn't say what he needs"
              : (item.row.sub || "");
      }
      var inner =
        '<span class="rc-mark" aria-hidden="true">' + (tickable ? (on ? "✓" : "○") : "·") + '</span>'
        + '<span class="rc-txt"><span class="rc-main">' + esc(item.row.label) + '</span>'
        + '<span class="rc-sub">' + esc(his) + tag + '</span></span>';
      if (!tickable) return '<div class="rc-pair rc-static">' + inner + "</div>";
      return '<button type="button" class="rc-pair' + (on ? " on" : "") + '" data-tick="' + item.row.id + '" aria-pressed="'
        + (on ? "true" : "false") + '">' + inner + "</button>";
    }

    function ticked(rep) {
      return rep.yes.filter(function (i) { return isOn(i) && !i.row.settled; });
    }

    function paint() {
      if (!report) { out.innerHTML = ""; return; }
      var rep = report, html = [];
      var n = ticked(rep).length;

      if (rep.yes.length) {
        html.push('<div class="rc-block"><h3 class="rc-h">' + esc(W.yesHead || "He's doing these")
          + ' <span class="rc-n">' + rep.yes.length + "</span></h3>");
        html.push(rep.yes.map(function (i) { return pairHTML(i, !i.row.settled); }).join(""));
        /* A DISABLED CONTROL HAS TO SAY WHY. Zero ticked means one of two
         * completely different things — every pair is already on the list, or
         * every pair is one we are not sure of and he has not vouched for any
         * of them yet — and "nothing left to tick" is a lie in the second. */
        var offer = rep.yes.filter(function (i) { return !i.row.settled; }).length;
        html.push('<div class="outrow" style="margin-top:9px"><button type="button" class="btn flag" id="rcApply"'
          + (n ? "" : " disabled") + '>'
          + (n ? "Tick " + plural(n, "row") + " " + esc(commitLabel.toLowerCase())
            : (offer ? "Tap the ones that are really yours" : "Nothing left to tick"))
          + "</button></div>");
        var unsure = rep.yes.filter(function (i) { return !i.sure && !i.row.settled; }).length;
        html.push('<p class="note" style="margin:8px 0 0">We only ever tick <b>' + esc(commitLabel)
          + "</b>. " + esc(W.onlyFirst || "The top of your ladder is you laying eyes on it, and a message isn't eyes.")
          + " Tap a row to leave it out"
          + (unsure ? ", or to vouch for one of the <b>" + unsure + "</b> we couldn't be sure of" : "")
          + ".</p></div>");
      }

      if (rep.push.length) {
        html.push('<div class="rc-block rc-block-warn"><h3 class="rc-h">' + esc(W.pushHead || "He pushed back on these")
          + ' <span class="rc-n">' + rep.push.length + "</span></h3>");
        html.push(rep.push.map(function (i) { return pairHTML(i, false); }).join(""));
        html.push('<p class="note" style="margin:8px 0 0">' + esc(W.pushNote || "Nothing gets ticked here — these are yours to move. Open the row and flag it if it's holding you up.") + "</p></div>");
      }

      if (rep.mute.length) {
        html.push('<div class="rc-block"><h3 class="rc-h">' + esc(W.muteHead || "He wrote back on these, but didn't say yes or no")
          + ' <span class="rc-n">' + rep.mute.length + "</span></h3>");
        html.push(rep.mute.map(function (i) { return pairHTML(i, false); }).join(""));
        html.push('<p class="note" style="margin:8px 0 0">Read them yourself and tap your own rows &mdash; a commitment is not something we guess out of a sentence.</p></div>');
      }

      if (rep.quiet.length) {
        html.push('<div class="rc-block rc-block-quiet"><h3 class="rc-h">' + esc(W.quietHead || "He never mentioned these")
          + ' <span class="rc-n">' + rep.quiet.length + "</span></h3>");
        html.push(rep.quiet.map(function (r) {
          return '<div class="rc-pair rc-static"><span class="rc-mark" aria-hidden="true">·</span>'
            + '<span class="rc-txt"><span class="rc-main">' + esc(r.label) + "</span>"
            + (r.sub ? '<span class="rc-sub">' + esc(r.sub) + "</span>" : "") + "</span></div>";
        }).join(""));
        html.push('<p class="note" style="margin:8px 0 0"><b>' + esc(W.quietNote
          || "Silence is not a yes.") + "</b> " + esc(rep.scopeName
            ? "Nothing in his reply lines up with these, and they're all on " + rep.scopeName + "'s list. That's the message you send next."
            : "Nothing in his reply lines up with these. That's the message you send next.") + "</p></div>");
      }

      if (rep.unplaced.length || rep.skipped.length) {
        html.push('<details class="more rc-block"><summary>'
          + (rep.unplaced.length
            ? "Show the " + plural(rep.unplaced.length, "line") + " we couldn't place"
            : "Show the " + plural(rep.skipped.length, "header line") + " we stepped over")
          + "</summary>");
        if (rep.unplaced.length) {
          html.push('<p class="note" style="margin:10px 0 6px">His words, with nothing on your list to match them to. <b>Read these before you trust the blocks above:</b> if one of them is really an answer, the row it belongs to is sitting under &ldquo;never mentioned&rdquo; and shouldn\'t be.</p>'
            + '<pre class="plain">' + esc(rep.unplaced.join("\n")) + "</pre>");
        }
        if (rep.skipped.length) {
          html.push('<p class="note" style="margin:10px 0 6px">' + (rep.unplaced.length ? "And his " : "His ")
            + "header, his counts and the sign-off &mdash; recognised and stepped over, never an ask. Nothing was thrown away.</p>"
            + '<pre class="plain">' + esc(rep.skipped.join("\n")) + "</pre>");
        }
        html.push("</details>");
      }

      out.innerHTML = html.join("");
      var apply = out.querySelector("#rcApply");
      if (apply) apply.addEventListener("click", doApply);
    }

    function doApply() {
      if (!report) return;
      var list = ticked(report);
      if (!list.length) return;
      var n = cfg.onApply ? cfg.onApply(list.map(function (i) { return i.row.id; })) : 0;
      /* THE ROWS MOVED, SO THE REPORT IS ABOUT A LIST THAT NO LONGER EXISTS —
       * rebuild it off the rows as they are NOW rather than repainting a
       * photograph. (§SCARS — a claim that outlives the thing it claims.) */
      report = build(lastText);
      paint();
      say("<b>Ticked " + plural(n, "row") + " " + esc(commitLabel.toLowerCase()) + ".</b> "
        + (report.quiet.length ? "Still nothing back on " + plural(report.quiet.length, "item") + " — that's the follow-up." : "Everything he answered is on the list."));
    }

    var lastText = "";
    $("#rcGo").addEventListener("click", function () {
      var raw = $("#rcPaste").value;
      if (!raw.trim()) { say("<b>Nothing pasted yet.</b> Paste his reply in the box above."); return; }
      lastText = raw;
      chosen = {};
      report = build(raw);
      var matched = report.yes.length + report.push.length + report.mute.length;
      if (!matched && !report.quiet.length) {
        report = null; paint();
        say("<b>Nothing in that lines up with your list.</b> If he re-typed it in his own words instead of answering the list you sent, there's nothing here to match — read it and tap your own rows.");
        return;
      }
      paint();
      var bits = [];
      if (matched) bits.push("<b>" + matched + " of his lines lined up</b>");
      if (report.quiet.length) bits.push("<b>" + plural(report.quiet.length, "item") + " he never mentioned</b>");
      say(bits.join(" · ") + ". Nothing has changed on your list yet.");
      $("#rcIntake").open = false;
      /* CENTRE, never "start": every page of every trade wears a sticky bar, and
       * a card scrolled to the top of the viewport is a card whose heading is
       * under it (§SCARS — the sticky nav eats what it lands on). The MESSAGE is
       * what he needs to read first, and it is one line tall, so centring that
       * puts the report immediately under it. */
      msg.scrollIntoView({ block: "center" });
    });

    out.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-tick]") : null;
      if (!b) return;
      var id = Number(b.getAttribute("data-tick"));
      chosen[id] = !isOn(pairOf(id));
      paint();
    });

    /* THE REPORT IS A PHOTOGRAPH OF THE LIST AND THE LIST MOVES UNDER IT — he
     * walks the job with the card open, settles a row by hand, and the card is
     * still offering it. The page wires this to the engine's onChange so the
     * two stay married. Guarded: paint() never triggers a render, but a caller
     * that re-enters would rebuild forever. */
    var refreshing = false;
    return {
      report: function () { return report; },
      refresh: function () {
        if (!report || refreshing) return;
        refreshing = true;
        try { report = build(lastText); paint(); } finally { refreshing = false; }
      }
    };
  }

  window.Reconcile = {
    mount: mount, parse: parseAnswer, pair: pair,
    norm: norm, tokens: tokens, VERDICTS: VERDICTS, SCORE: SCORE
  };
})();
