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
  var VERDICTS = {
    "will do": "yes",
    "in already": "in",
    "cant": "no",
    "cannot": "no",
    "need to know": "ask"
  };

  /* Tuned to the failure that costs something. A missed pair costs one tap on a
   * row he can see; a wrong pair marks an item committed that nobody committed
   * to. So SURE is high, the MARGIN insists the runner-up is clearly worse, and
   * anything between MIN and SURE is shown switched off. */
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
    var hit = -1, i;
    for (i = 0; i < lines.length; i++) if (DISCLAIM.test(lines[i].trim())) { hit = i; break; }
    if (hit < 0) return -1;
    var j = hit;
    while (j > 0 && lines[j - 1].trim() !== "") j--;
    return j;
  }

  function parseAnswer(text) {
    var raw = String(text == null ? "" : text).split(/\r?\n/);
    /* A PASTE IS ONLY A MESSAGE IF IT LOOKS LIKE ONE. Without this the first
     * line of a one-line reply — "back box CR-204 60 aff — yeah thursday" — is
     * thrown away as a subject, and the man who pasted his answer gets an empty
     * report. (Found by the gate on its first run, which is what it is for.) */
    var hasHead = raw.some(function (l) { return KEYLINE.test(l.trim()) || HEADING.test(l.trim()); });
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
      if (KEYLINE.test(t) || ONLIST.test(t) || COUNTLINE.test(t) || RULELINE.test(t) || DISCLAIM.test(t)) { dropped.push(t); return; }

      /* HIS LINE, THEN A DASH, THEN HIS ANSWER — that is answer-back's row and
       * the dash is the seam between what we asked for and what he committed
       * to. Split on the FIRST one: everything left of it is our words coming
       * home, which is exactly what the join wants. */
      var body = t.replace(/^[-–—•*]\s+/, "");
      var seam = body.indexOf(" — ");
      if (seam < 0) seam = body.indexOf(" - ");
      var ask = seam > -1 ? body.slice(0, seam).trim() : body;
      var tail = seam > -1 ? body.slice(seam + 3).trim() : "";

      /* Grouped by anything other than his answer, the rung rides IN the line
       * instead of in the heading above it. Read it off the end of the ask so
       * the verdict is right either way. */
      var own = "";
      var m = /\s*[·|]\s*([A-Za-z][A-Za-z' ]{1,14})\s*$/.exec(ask);
      if (m && verdictOf(m[1])) { own = verdictOf(m[1]); ask = ask.slice(0, m.index).trim(); }

      out.push({
        ix: ix++, raw: t, ask: ask, tail: tail,
        verdict: own || verdict, flagged: flagged
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
    var best = {}, second = {};
    cands.forEach(function (c) {
      var b = best[c.lineIx];
      if (!b || c.score > b.score) { second[c.lineIx] = b || null; best[c.lineIx] = c; }
      else if (!second[c.lineIx] || c.score > second[c.lineIx].score) second[c.lineIx] = c;
    });

    cands.sort(function (a, b) {
      return (b.score - a.score) || (a.rowId - b.rowId) || (a.lineIx - b.lineIx);
    });

    var usedRow = {}, usedLine = {}, pairs = [];
    cands.forEach(function (c) {
      if (usedRow[c.rowId] || usedLine[c.lineIx]) return;
      usedRow[c.rowId] = 1; usedLine[c.lineIx] = 1;
      var sec = second[c.lineIx];
      var sure = c.exact || (c.score >= SCORE.SURE && (!sec || (c.score - sec.score) >= SCORE.MARGIN));
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

      var yes = [], push = [], quiet = [], mute = [];
      joined.pairs.forEach(function (p) {
        var r = byId[p.rowId], l = byIx[p.lineIx];
        var item = { row: r, line: l, sure: p.sure, exact: p.exact, score: p.score };
        if (l.flagged || l.verdict === "no" || l.verdict === "ask") push.push(item);
        else if (l.verdict === "yes" || l.verdict === "in") yes.push(item);
        else mute.push(item);                       // he wrote back, but said neither
      });

      /* NARROW THE SILENCE TO THE MAN WHO ANSWERED. One walk, N messages: this
       * list holds asks for three companies, and reporting the GC's items as
       * "the electrician never mentioned these" is the page inventing a
       * grievance. If every row he DID answer belongs to one receiver, the
       * unanswered block is scoped to that receiver and says whose it is. */
      var scopes = {}, nScope = 0, scope = "";
      joined.pairs.forEach(function (p) {
        var s = (byId[p.rowId] || {}).scope || "";
        if (!s || scopes[s]) return;
        scopes[s] = 1; nScope++; scope = s;
      });
      var scoped = nScope === 1 ? scope : "";

      joined.unmatched.forEach(function (id) {
        var r = byId[id];
        if (!r || r.settled) return;                 // already answered or already in
        if (scoped && r.scope && r.scope !== scoped) return;
        quiet.push(r);
      });

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

    function pairHTML(item, tickable) {
      var on = tickable ? chosen[item.row.id] !== false : false;
      var tag = "";
      if (item.line.verdict === "in") tag = '<span class="rc-tag">he says it\'s in</span>';
      if (!item.sure) tag += '<span class="rc-tag rc-warn">not sure it\'s the same one</span>';
      if (!tickable && item.row.settled) tag += '<span class="rc-tag">already ' + esc(String(item.row.row.values[cfg.commitKey || "status"] || "").toLowerCase()) + '</span>';
      /* THE EVIDENCE, SHOWN EXACTLY WHEN IT IS NEEDED. On a pair we are unsure
       * of, his whole line is the only way to judge whether it is the same
       * item, so it goes on the glass. On a sure pair it is our own line coming
       * home and repeating it says nothing — what is worth a line there is what
       * he ADDED, and when he added nothing the missing thing is the date.
       * Everybody leaves the date out of a reply and it is exactly what gets
       * argued about later. */
      var his = !item.sure ? item.line.raw
        : (item.line.tail || (item.line.verdict === "yes" ? "no date on it" : (item.row.sub || "")));
      var inner =
        '<span class="rc-mark" aria-hidden="true">' + (tickable ? (on ? "✓" : "○") : "·") + '</span>'
        + '<span class="rc-txt"><span class="rc-main">' + esc(item.row.label) + '</span>'
        + '<span class="rc-sub">' + esc(his) + tag + '</span></span>';
      if (!tickable) return '<div class="rc-pair rc-static">' + inner + "</div>";
      return '<button type="button" class="rc-pair' + (on ? " on" : "") + '" data-tick="' + item.row.id + '" aria-pressed="'
        + (on ? "true" : "false") + '">' + inner + "</button>";
    }

    function ticked(rep) {
      return rep.yes.filter(function (i) { return chosen[i.row.id] !== false && !i.row.settled; });
    }

    function paint() {
      if (!report) { out.innerHTML = ""; return; }
      var rep = report, html = [];
      var n = ticked(rep).length;

      if (rep.yes.length) {
        html.push('<div class="rc-block"><h3 class="rc-h">' + esc(W.yesHead || "He's doing these")
          + ' <span class="rc-n">' + rep.yes.length + "</span></h3>");
        html.push(rep.yes.map(function (i) { return pairHTML(i, !i.row.settled); }).join(""));
        html.push('<div class="outrow" style="margin-top:9px"><button type="button" class="btn flag" id="rcApply"'
          + (n ? "" : " disabled") + '>'
          + (n ? "Tick " + plural(n, "row") + " " + commitLabel.toLowerCase() : "Nothing left to tick")
          + "</button></div>");
        html.push('<p class="note" style="margin:8px 0 0">We only ever tick <b>' + esc(commitLabel)
          + "</b>. " + esc(W.onlyFirst || "The top of your ladder is you laying eyes on it, and a message isn't eyes.")
          + " Tap a row to leave it out.</p></div>");
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
      card.scrollIntoView({ block: "start" });
    });

    out.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-tick]") : null;
      if (!b) return;
      var id = Number(b.getAttribute("data-tick"));
      chosen[id] = chosen[id] === false;
      paint();
    });

    return { report: function () { return report; }, refresh: function () { if (report) { report = build(lastText); paint(); } } };
  }

  window.Reconcile = {
    mount: mount, parse: parseAnswer, pair: pair,
    norm: norm, tokens: tokens, VERDICTS: VERDICTS, SCORE: SCORE
  };
})();
