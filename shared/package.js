/* FIELD TOOLKIT — SHAPE #5 ENGINE: THE RECKONING.
 *
 * av/AV_SOCIETY.md §THE THREE SHAPES names three; §THERE IS A FOURTH SHAPE names
 * the instruction block. This is the FIFTH, and it is the first thing on this
 * toolkit that is not a document you send UP a chain — it is one you send
 * SIDEWAYS, to your brother in another local, or to nobody at all because the
 * answer was for you.
 *
 * THE SHAPE: put a figure on the lines that apply to you, name a second column,
 * put figures on the same lines, read the difference. Every trade has one of
 * these — package vs package, bid vs bid, quoted hours vs burned hours. The first
 * instance is TOTAL PACKAGE.
 *
 * WHY AN ENGINE ON INSTANCE #1, when §THE THREE SHAPES says two instances is
 * where a shape is provable: the same reason shape #2 got one — this ships as
 * EIGHT configs in one cycle, one per trade, and eight hand-written line grids
 * drift inside a week. THE PANEL'S SHAPE SKEPTIC DISSENTED FROM THIS (2026-08-12,
 * 2/10: "no convergent evidence, no queued second instance — build one page, one
 * trade"). It was overruled on the standing breadth law (a refinement that lands
 * on one trade and leaves its siblings behind is half a refinement) and the
 * dissent is recorded in the book so that if the fleet-first call proves wrong,
 * the receipt is already paid for.
 *
 * WHAT THE ENGINE OWNS:
 *   · THE NUMBER IS THE TICK. There is no checkbox. A line with a figure on it
 *     is in the document and a blank line is not — one act instead of two, and
 *     it drops every unpicked value for free (§SCARS, A DEFAULT IS A CLAIM).
 *   · THE BASIS, STATED ONCE AND PRINTED EVERY TIME. Hourly and yearly figures
 *     are indistinguishable in a text field and differ by a factor of two
 *     thousand. The document says which one it is in its second line, always.
 *   · THREE LINE KINDS, because a package is not a column of like things:
 *       money — a figure in the basis. Sums into its group.
 *       pct   — a PERCENTAGE, resolved per column against THAT column's own
 *               wages. Not a nicety: working dues and most annuities run as a
 *               percent of gross, and a flat field for them lies precisely when
 *               two different wage rates are compared, which is the only time
 *               anyone opens this page. Panel finding from a working journeyman,
 *               2026-08-12: "it just sits there being wrong exactly when I
 *               compare two different wage rates, which is the entire point."
 *       aside — a figure with its OWN unit ("a day"), never summed, always
 *               printed. Per diem is real money and is not per-hour money;
 *               folding it into a package would be a lie and leaving it out
 *               loses every traveler.
 *   · FOUR BUCKETS: wages · fringes · what comes back out of the check · asides.
 *     TOTAL PACKAGE = wages + fringes, which is what the wage sheet means by it.
 *     Deductions show as NET ON THE CHECK and never touch the package —
 *     conflating those two is the commonest way this comparison is made wrong.
 *   · THE BLANK-LINE FLAG. If one column has a line filled and the other does
 *     not, the totals are not comparable and the page SAYS SO, next to the
 *     total and in the document. A confident total built on unacknowledged
 *     blanks is the single most likely way this tool produces a number someone
 *     takes into a real decision and is wrong (panel, safety lens, 2026-08-12;
 *     same rule as §THE RETURN LEG's dateless yes and the 2026-08-09 scar THE
 *     SUMMARY COUNTED ROWS THE DOCUMENT DID NOT CONTAIN).
 *   · THE TWO DISCLAIMERS, neither of which a caller can switch off: one on
 *     screen beside the totals, one inside the copied text. The copied block is
 *     the artifact that leaves the browser and reaches a business agent or a
 *     spouse, and it looks exactly like a wage sheet. It is one man's typing.
 *   · THE DOCUMENT, WRAP-TOLERANT. No aligned columns anywhere: a monospace
 *     block is mush in a proportional font and a text message is where this
 *     goes (§SCARS 2026-08-04, A COLUMN LOOKS TIDY IN THE PREVIEW AND ARRIVES AS
 *     MUSH). Every line reads "Label — Mine $48.50 · Theirs $52.10".
 *   · persistence WITH a synchronous flush · copy with the non-secure-context
 *     fallback · the self-aware date · re-render on the runtime's av:ready.
 *
 * TWO COLUMNS, NOT THREE. Three number fields plus a label do not fit a 320px
 * phone without shrinking each cell below a thumb, and the third column is
 * speculative where the second is the whole use case. Panel, shape lens.
 *
 * WHAT THE CALLER OWNS: every WORD — the groups, the reason line under each, the
 * seeded lines in that trade's own vocabulary, the basis default, the hours
 * prompt and the closing note. A package is not spoken the same way by an inside
 * wireman and a salaried super.
 *
 * NOT here, deliberately, and NOT a caller's option either: any rate, table or
 * figure we did not watch a man type. No wage data, no fund rates, no
 * cost-of-living index, no jurisdiction map, no example amount in a placeholder
 * (a seeded figure is a rate assertion wearing helper text), and no proper noun
 * of any union, contractor association, benefit fund or local number anywhere in
 * a seed list. The page seeds the CATEGORY NAMES his own stub already carries
 * and nothing else (§SAFETY).
 *
 * NO FORWARD PROJECTION AND NO EDITORIALISING, ever, in any caller: no rate of
 * return, no "worth $X at retirement", no vesting, and no column ever labelled
 * better, recommended or worse. The delta says MORE THAN and LESS THAN, because
 * that is arithmetic; anything warmer is advice.
 *
 * NO TELEMETRY ON THIS PAGE — not a variant counter, not an anonymous tally, not
 * "the most common comparison". The evo loop instruments CHOICES between
 * variants; a wage is not a variant, and every other tool's data is a cable spec
 * or a punch item. This page is exempt by design, and the exemption is written
 * here so a later cycle reads it before wiring one in.
 *
 * AND THE FEEDBACK PATH NEVER CARRIES STATE. shared/feedback.js builds its
 * payload only from its own form fields and must keep doing so on this page: an
 * "attach current state so I can debug it" convenience here would put a real
 * person's pay into the queue.
 *
 * Load AFTER the trade config and registry, alongside the shared runtime:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/package.js"></script>
 */
(function () {
  "use strict";

  var MAXCOL = 2;

  function byId(x) { return typeof x === "string" ? document.getElementById(x) : x; }
  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function trim(v) { return String(v == null ? "" : v).trim(); }

  /* A figure is what survives stripping what a thumb adds: a dollar sign, a
     comma, a stray space. NOTHING else is normalised — the raw string stays in
     the field exactly as typed (§SCARS, A PHONE DESTROYS AN IDENTIFIER). */
  function num(v) {
    var s = trim(v).replace(/[$,%\s]/g, "");
    if (!s) return null;
    var n = parseFloat(s);
    return isFinite(n) ? n : null;
  }
  /* TYPE 3% AND IT IS A PERCENT, on any line, whatever the line was declared as.
     Costs no new control and matches what a hand actually writes: some locals
     run the annuity off gross and some run it flat, and the seed list cannot
     know which one is in front of him. The declared `pct` kind still stands on
     its own for the lines that are always percentages. */
  function typedPct(v) { return /%\s*$/.test(trim(v)); }
  function money(n, dp) {
    if (n == null || !isFinite(n)) return "";
    var d = dp == null ? 2 : dp;
    return n.toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function todayStr() {
    return (window.AV && window.AV.todayStr)
      ? window.AV.todayStr()
      : new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function copyText(text, btn, label) {
    function flash(msg) {
      if (!btn) return;
      if (!btn.getAttribute("data-label")) btn.setAttribute("data-label", btn.textContent);
      btn.textContent = msg;
      setTimeout(function () { btn.textContent = btn.getAttribute("data-label"); }, 1800);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;left:8px;bottom:76px;width:calc(100% - 16px);height:38vh;z-index:99";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      if (ok) { ta.remove(); flash(label || "Copied"); }
      else { flash("Copy it manually"); ta.addEventListener("blur", function () { ta.remove(); }); }
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { flash(label || "Copied"); }, fallback);
    } else { fallback(); }
  }

  /* THE TWO LINES NO CALLER CAN SWITCH OFF. Three points, in the field's voice:
     these are self-reported, they are not take-home, and fringes do not behave
     like wages on overtime. */
  var SCREEN_WARN = "This is what YOU typed, added up. It doesn't know what's taxed, "
    + "what's vested, or that fringes usually get paid at straight time even on your "
    + "overtime hours. Check it against your own stub before you compare offers on it.";
  var DOC_WARN = [
    "Built from figures I typed in myself, off my own stub — not a wage sheet,",
    "not a take-home number, and not tax advice. Fringes are usually paid at",
    "straight time even on overtime hours, so this is not what lands in a check.",
    "Double-check it against your own agreement before anybody acts on it."
  ];

  function mount(cfg) {
    var host = byId(cfg.mount);
    if (!host) return null;

    var GROUPS = cfg.groups || [];
    var KEY = cfg.key || "toolkit-package";

    /* `vals` is line-id -> array of RAW strings, one per column. Raw, not parsed:
       what he typed is what he sees on the way back, and the parse happens once,
       at read time. */
    var S = {
      basis: cfg.basis === "yr" ? "yr" : "hr",
      cols: [{ name: "" }, null],
      vals: {},
      hours: "",
      custom: []
    };

    var els = {};
    var seq = 0;

    function allLines() {
      var out = [];
      GROUPS.forEach(function (g) {
        (g.lines || []).forEach(function (l) { out.push({ g: g, l: l }); });
        S.custom.forEach(function (c) { if (c.group === g.key) out.push({ g: g, l: c }); });
      });
      return out;
    }
    function nCols() {
      var n = 0;
      for (var i = 0; i < MAXCOL; i++) if (S.cols[i]) n = i + 1;
      return n;
    }
    function colName(i) {
      var c = S.cols[i];
      if (!c) return "";
      return trim(c.name) || (cfg.colHints && cfg.colHints[i]) || ("Column " + (i + 1));
    }
    function raw(id, i) {
      var a = S.vals[id];
      return a ? trim(a[i]) : "";
    }
    function val(id, i) { return num(raw(id, i)); }
    function hasAny(id) {
      for (var i = 0; i < MAXCOL; i++) if (S.cols[i] && raw(id, i)) return true;
      return false;
    }

    /* ---- THE MATH -------------------------------------------------------
     * Every figure is one the user typed, or the product of two he typed. A pct
     * line resolves against THAT column's wages — never against fringes, never
     * against another pct — so there is no order dependence and no cycle. */
    function isPct(r, i) { return r.l.kind === "pct" || typedPct(raw(r.l.id, i)); }
    function wagesOf(i) {
      var t = 0, any = false;
      allLines().forEach(function (r) {
        if (r.g.key !== "wages" || r.l.kind === "aside" || isPct(r, i)) return;
        var v = val(r.l.id, i);
        if (v != null) { t += v; any = true; }
      });
      return any ? t : null;
    }
    function lineAmount(r, i) {
      var v = val(r.l.id, i);
      if (v == null) return null;
      if (isPct(r, i)) {
        var w = wagesOf(i);
        return w == null ? null : (w * v / 100);
      }
      return v;
    }
    function sumGroup(key, i) {
      var t = 0, any = false;
      allLines().forEach(function (r) {
        if (r.g.key !== key || r.l.kind === "aside") return;
        var a = lineAmount(r, i);
        if (a != null) { t += a; any = true; }
      });
      return any ? t : null;
    }
    function totals(i) {
      var w = sumGroup("wages", i);
      var f = sumGroup("fringes", i);
      var b = sumGroup("back", i);
      var pkg = (w == null && f == null) ? null : (w || 0) + (f || 0);
      var net = (w == null) ? null : (w || 0) - (b || 0);
      return { wages: w, fringes: f, back: b, pkg: pkg, net: net };
    }

    /* THE BLANK-LINE FLAG. A line the OTHER column carries and this one does not
       makes the two totals different questions. Count them and say so. */
    function blanksIn(i) {
      if (nCols() < 2) return [];
      var out = [];
      allLines().forEach(function (r) {
        if (r.l.kind === "aside") return;
        if (raw(r.l.id, i)) return;
        for (var j = 0; j < nCols(); j++) {
          if (j !== i && raw(r.l.id, j)) { out.push(r.l.label); return; }
        }
      });
      return out;
    }
    function filled() {
      var n = 0;
      allLines().forEach(function (r) { if (hasAny(r.l.id)) n++; });
      return n;
    }
    function hoursNum() {
      var h = num(S.hours);
      return (h != null && h > 0) ? h : null;
    }

    var UNIT = function () { return S.basis === "hr" ? "an hour" : "a year"; };
    var DP = function () { return S.basis === "hr" ? 2 : 0; };

    /* ---- RENDER ---------------------------------------------------------- */
    function render() {
      host.innerHTML = "";
      els = {};

      /* THE BASIS — first thing on the page, because it is what makes every
         other number on it mean something. */
      var bcard = el("div", "card");
      var brow = el("div", "basis");
      brow.appendChild(el("span", "lab", cfg.basisLabel || "These figures are"));
      var seg = el("div", "seg");
      [["hr", cfg.basisHrLabel || "$ an hour"], ["yr", cfg.basisYrLabel || "$ a year"]].forEach(function (o) {
        var b = el("button", S.basis === o[0] ? "on" : "", o[1]);
        b.type = "button";
        b.setAttribute("aria-pressed", S.basis === o[0] ? "true" : "false");
        b.addEventListener("click", function () {
          if (S.basis === o[0]) return;
          S.basis = o[0];
          save(); render(); refresh();
        });
        seg.appendChild(b);
      });
      brow.appendChild(seg);
      bcard.appendChild(brow);

      /* THE COLUMNS. One is always there; the second arrives when he asks.
         The name is plain free text with no suggestion list — the moment we
         autocomplete real locals or shops we have compiled the directory this
         project refused to ship (§SAFETY). */
      var cols = el("div", "cols");
      for (var i = 0; i < MAXCOL; i++) {
        if (!S.cols[i]) continue;
        (function (i) {
          var cell = el("div", "cell");
          var lab = el("label", null, i === 0 ? (cfg.firstColLabel || "Yours") : (cfg.otherColLabel || "The other one"));
          lab.setAttribute("for", "pkcol" + i);
          var inp = el("input");
          inp.id = "pkcol" + i;
          inp.type = "text";
          inp.value = S.cols[i].name || "";
          inp.placeholder = (cfg.colHints && cfg.colHints[i]) || "Name it";
          inp.setAttribute("autocapitalize", "words");
          inp.setAttribute("autocorrect", "off");
          inp.setAttribute("autocomplete", "off");
          inp.setAttribute("spellcheck", "false");
          inp.addEventListener("input", function () {
            S.cols[i].name = inp.value;
            paintCaps(); queueSave(); refresh();
          });
          cell.appendChild(lab); cell.appendChild(inp);
          cols.appendChild(cell);
          if (i > 0) {
            var rm = el("button", "drop", "×");
            rm.type = "button";
            rm.title = "Drop this column";
            rm.setAttribute("aria-label", "Drop the second column");
            rm.addEventListener("click", function () {
              S.cols[i] = null;
              allLines().forEach(function (r) { if (S.vals[r.l.id]) S.vals[r.l.id][i] = ""; });
              save(); render(); refresh();
            });
            cols.appendChild(rm);
          }
        })(i);
      }
      bcard.appendChild(cols);
      if (nCols() < MAXCOL) {
        var add = el("button", "addcol", cfg.addColLabel || "＋ Put another one beside it");
        add.type = "button";
        add.addEventListener("click", function () {
          S.cols[1] = { name: "" };
          save(); render(); refresh();
          var f = document.getElementById("pkcol1");
          if (f) f.focus();
        });
        bcard.appendChild(add);
      }
      host.appendChild(bcard);

      /* THE LINES */
      GROUPS.forEach(function (g) {
        var card = el("div", "card" + (g.key === "back" || g.key === "aside" ? " grey" : ""));
        var h = el("div", "grph");
        h.appendChild(el("span", null, g.name));
        if (g.why) h.appendChild(el("span", "why", g.why));
        card.appendChild(h);

        var body = el("div", "grp");
        var rows = (g.lines || []).slice();
        S.custom.forEach(function (c) { if (c.group === g.key) rows.push(c); });
        rows.forEach(function (l) { body.appendChild(buildLine(g, l)); });
        card.appendChild(body);

        if (g.canAdd !== false) {
          var a = el("button", "addline", g.addLabel || "＋ Add a line of your own");
          a.type = "button";
          a.addEventListener("click", function () { addCustom(g); });
          card.appendChild(a);
        }
        host.appendChild(card);
      });

      /* HOURS — optional, blank, and the only denominator on the page. No
         example figure in the placeholder: a suggested number is a claim. */
      var hc = el("div", "card grey");
      var hh = el("div", "grph");
      hh.appendChild(el("span", null, cfg.hoursHead || "Your hours"));
      hh.appendChild(el("span", "why", cfg.hoursWhy || "Optional. Fill it in and the difference gets a yearly figure too."));
      hc.appendChild(hh);
      var hrow = el("div", "hours");
      var hcell = el("div", "cell");
      var hlab = el("label", null, cfg.hoursLabel || "Hours a year you actually work");
      hlab.setAttribute("for", "pkhours");
      var hin = el("input");
      hin.id = "pkhours";
      hin.type = "text";
      hin.inputMode = "decimal";
      hin.value = S.hours || "";
      hin.setAttribute("autocorrect", "off");
      hin.setAttribute("autocomplete", "off");
      hin.addEventListener("input", function () { S.hours = hin.value; queueSave(); refresh(); });
      hcell.appendChild(hlab); hcell.appendChild(hin);
      hrow.appendChild(hcell);
      hrow.appendChild(el("p", "note", cfg.hoursNote || "Put in what you really got last year, not a round number — rain, layoff and the slow month are the difference between a comparison and a daydream."));
      hc.appendChild(hrow);
      host.appendChild(hc);

      /* THE ANSWER */
      var tc = el("div", "card");
      var th = el("div", "grph");
      th.appendChild(el("span", null, cfg.totalsHead || "What it comes to"));
      tc.appendChild(th);
      var tot = el("div", "tot");
      tot.id = "pktot";
      tc.appendChild(tot);
      tc.appendChild(el("p", "selfrep", SCREEN_WARN));
      host.appendChild(tc);

      paintCaps();
    }

    function buildLine(g, l) {
      var wrap = el("div", "line");
      wrap.setAttribute("data-line", l.id);
      var lab = el("div", "lbl");
      lab.appendChild(el("span", null, l.label));
      var subTxt = l.sub || "";
      if (l.kind === "pct") subTxt = subTxt ? (subTxt + " — put it in as a %") : "put it in as a % of wages";
      if (l.kind === "aside" && l.unit) subTxt = subTxt ? (subTxt + " — " + l.unit + ", kept out of the package") : (l.unit + ", kept out of the package");
      if (subTxt) lab.appendChild(el("span", "sub", subTxt));
      if (l.custom) {
        var rm = el("button", "rm", "×");
        rm.type = "button";
        rm.setAttribute("aria-label", "Remove the " + l.label + " line");
        rm.addEventListener("click", function () {
          S.custom = S.custom.filter(function (c) { return c.id !== l.id; });
          delete S.vals[l.id];
          save(); render(); refresh();
        });
        lab.appendChild(rm);
      }
      wrap.appendChild(lab);

      var ins = el("div", "ins");
      els[l.id] = [];
      for (var i = 0; i < MAXCOL; i++) {
        if (!S.cols[i]) continue;
        (function (i) {
          var cell = el("div", "cell");
          var cap = el("span", "cap", colName(i));
          /* The unit shown on the field FOLLOWS WHAT IS IN IT. A money line with
             a trailing % typed into it is a percent, and leaving the "$" sitting
             in front of it renders "$ 3%" — two units on one figure, which is
             the kind of thing a man reads twice and then stops trusting. */
          var mw = el("div", "mw");
          var paintUnit = function (v) { mw.classList.toggle("pct", l.kind === "pct" || typedPct(v)); };
          paintUnit(raw(l.id, i));
          var inp = el("input");
          inp.type = "text";
          inp.inputMode = "decimal";
          inp.value = raw(l.id, i);
          inp.setAttribute("autocorrect", "off");
          inp.setAttribute("autocapitalize", "off");
          inp.setAttribute("autocomplete", "off");
          inp.setAttribute("aria-label", l.label + " — " + colName(i));
          inp.addEventListener("input", function () {
            if (!S.vals[l.id]) S.vals[l.id] = ["", ""];
            S.vals[l.id][i] = inp.value;
            wrap.classList.toggle("on", hasAny(l.id));
            paintUnit(inp.value);
            queueSave(); refresh();
          });
          mw.appendChild(inp);
          cell.appendChild(cap); cell.appendChild(mw);
          ins.appendChild(cell);
          els[l.id].push({ input: inp, cap: cap, col: i, label: l.label });
        })(i);
      }
      wrap.appendChild(ins);
      if (hasAny(l.id)) wrap.classList.add("on");
      return wrap;
    }

    function paintCaps() {
      Object.keys(els).forEach(function (id) {
        els[id].forEach(function (e) {
          e.cap.textContent = colName(e.col);
          e.input.setAttribute("aria-label", e.label + " — " + colName(e.col));
        });
      });
      var cs = host.querySelectorAll(".ins");
      for (var i = 0; i < cs.length; i++) cs[i].classList.toggle("nocap", nCols() < 2);
    }

    function addCustom(g) {
      var name = window.prompt(g.addPrompt || "What is the line called? Put it in however it reads on your stub.");
      if (name == null) return;
      name = trim(name).slice(0, 48);
      if (!name) return;
      seq++;
      var id = "x" + g.key + seq + "_" + String(seq * 7919 + (GROUPS.length * 131));
      /* A write-in in the asides group is an aside — it inherits the group's
         unit, because a line added under "per diem" is not per-hour money
         either. Everywhere else a write-in is a money line, and typing a
         trailing % still turns it into a percent. */
      S.custom.push({
        id: id, label: name, group: g.key, custom: true,
        kind: g.customKind || "money",
        unit: g.customKind === "aside" ? (g.unit || "") : ""
      });
      save(); render(); refresh();
    }

    /* ---- THE DOCUMENT ---------------------------------------------------
     * Wrap-tolerant on purpose: no aligned columns anywhere. This gets pasted
     * into a text message, and a monospace block in a proportional font is a
     * ragged mess that reads as sloppy work. */
    function asText() {
      var n = nCols();
      var L = [];
      L.push((cfg.docTitle || "TOTAL PACKAGE") + " — " + todayStr());
      var sub = [];
      if (cfg.docSub) sub.push(cfg.docSub);
      sub.push("figures are $ " + UNIT());
      L.push(sub.join("  ·  "));
      L.push("");

      /* THE ANSWER FIRST. He is sending this to make one point. */
      L.push((cfg.docTotalsHead || "WHAT IT COMES TO").toUpperCase());
      var t = [], i;
      for (i = 0; i < n; i++) t.push(totals(i));
      for (i = 0; i < n; i++) {
        if (t[i].pkg == null) { L.push(colName(i) + " — nothing on it yet"); continue; }
        L.push(colName(i) + " — $" + money(t[i].pkg, DP()) + " total package"
          + " (wages $" + money(t[i].wages || 0, DP())
          + " + fringes $" + money(t[i].fringes || 0, DP()) + ")");
        if (t[i].back != null) {
          L.push("   comes back out of the check: $" + money(t[i].back, DP())
            + "  →  net on the check $" + money(t[i].net, DP()));
        }
        var bl = blanksIn(i);
        if (bl.length) {
          L.push("   " + bl.length + (bl.length === 1 ? " line is" : " lines are")
            + " blank here that the other column has: " + bl.join(", ")
            + " — so these two totals are not answering the same question yet.");
        }
      }

      var h = hoursNum();
      if (n > 1 && t[0].pkg != null && t[1].pkg != null) {
        var d = t[1].pkg - t[0].pkg;
        var line;
        if (d === 0) line = colName(1) + " comes to the same as " + colName(0);
        else line = colName(1) + " is $" + money(Math.abs(d), DP()) + " " + UNIT()
          + (d > 0 ? " more than " : " less than ") + colName(0);
        if (h && S.basis === "hr") line += "  —  $" + money(Math.abs(d) * h, 0) + " a year at " + money(h, 0) + " hrs";
        if (h && S.basis === "yr") line += "  —  $" + money(Math.abs(d) / h, 2) + " an hour at " + money(h, 0) + " hrs";
        L.push(line);
      }
      L.push("");

      /* THE LINES */
      GROUPS.forEach(function (g) {
        var rows = [];
        allLines().forEach(function (r) {
          if (r.g.key === g.key && hasAny(r.l.id)) rows.push(r);
        });
        if (!rows.length) return;
        L.push(g.docName || String(g.name).toUpperCase());
        rows.forEach(function (r) {
          var parts = [];
          for (var i = 0; i < n; i++) {
            var rw = raw(r.l.id, i);
            if (!rw) { parts.push(colName(i) + " —"); continue; }
            if (isPct(r, i)) {
              var amt = lineAmount(r, i);
              parts.push(colName(i) + " " + num(rw) + "%" + (amt != null ? " ($" + money(amt, DP()) + ")" : ""));
            } else if (r.l.kind === "aside") {
              parts.push(colName(i) + " $" + money(num(rw), 2) + (r.l.unit ? " " + r.l.unit : ""));
            } else {
              parts.push(colName(i) + " $" + money(num(rw), DP()));
            }
          }
          L.push("  " + r.l.label + " — " + parts.join("  ·  "));
        });
        L.push("");
      });

      DOC_WARN.forEach(function (w) { L.push(w); });
      if (cfg.docFoot) { L.push(""); L.push(cfg.docFoot); }
      return L.join("\n").replace(/\n{3,}/g, "\n\n").trim() + "\n";
    }

    /* ---- REFRESH --------------------------------------------------------- */
    function refresh() {
      var n = nCols();
      var tot = document.getElementById("pktot");
      if (tot) {
        tot.innerHTML = "";
        var t = [], i;
        for (i = 0; i < n; i++) t.push(totals(i));
        var any = t.some(function (x) { return x.pkg != null; });
        if (!any) {
          tot.appendChild(el("p", "empty", cfg.emptyText || "Put a figure on the lines that apply to you. Blank lines stay off the sheet."));
        } else {
          tot.appendChild(totRow(cfg.wagesWord || "Wages", t, "wages", false));
          tot.appendChild(totRow(cfg.fringesWord || "Fringes", t, "fringes", false));
          tot.appendChild(totRow(cfg.totalWord || "Total package", t, "pkg", true));
          if (t.some(function (x) { return x.back != null; })) {
            tot.appendChild(totRow(cfg.backWord || "Comes back out", t, "back", false));
            tot.appendChild(totRow(cfg.netWord || "Net on the check", t, "net", false));
          }
          /* THE BLANK-LINE FLAG, on screen, beside the number it undermines. */
          for (i = 0; i < n; i++) {
            var bl = blanksIn(i);
            if (!bl.length) continue;
            var w = el("p", "gap");
            w.appendChild(el("b", null, colName(i) + ": " + bl.length + (bl.length === 1 ? " blank line" : " blank lines")));
            w.appendChild(document.createTextNode(" — " + bl.join(", ")
              + ". The other column has " + (bl.length === 1 ? "it" : "them") + ", so these two totals are not answering the same question yet."));
            tot.appendChild(w);
          }
          if (n > 1 && t[0].pkg != null && t[1].pkg != null) {
            var d = el("div", "delta");
            var diff = t[1].pkg - t[0].pkg;
            var p = el("p");
            var b = el("b", diff > 0 ? "up" : (diff < 0 ? "dn" : ""));
            b.textContent = (diff === 0 ? "" : (diff > 0 ? "+" : "−")) + "$" + money(Math.abs(diff), DP()) + " " + UNIT();
            p.appendChild(b);
            p.appendChild(document.createTextNode("  " + colName(1)
              + (diff === 0 ? " comes to the same as " : (diff > 0 ? " more than " : " less than ")) + colName(0)));
            var h = hoursNum();
            if (h && S.basis === "hr" && diff !== 0) p.appendChild(el("span", null, "  —  $" + money(Math.abs(diff) * h, 0) + " a year at " + money(h, 0) + " hrs"));
            if (h && S.basis === "yr" && diff !== 0) p.appendChild(el("span", null, "  —  $" + money(Math.abs(diff) / h, 2) + " an hour at " + money(h, 0) + " hrs"));
            d.appendChild(p);
            tot.appendChild(d);
          }
        }
      }
      var pv = byId(cfg.preview);
      if (pv) pv.textContent = asText();
      var ct = byId(cfg.count);
      if (ct) {
        var f = filled();
        ct.textContent = f === 0
          ? (cfg.countEmpty || "Nothing on it yet")
          : (f + (f === 1 ? " line" : " lines") + (nCols() > 1 ? " · two columns" : ""));
      }
    }

    function totRow(label, t, key, big) {
      var r = el("div", "totrow" + (big ? " big" : ""));
      r.appendChild(el("span", "rl", label));
      for (var i = 0; i < t.length; i++) {
        var c = el("span", "cell");
        var v = t[i][key];
        c.appendChild(document.createTextNode(v == null ? "—" : "$" + money(v, DP())));
        if (t.length > 1) c.appendChild(el("span", "u", colName(i)));
        r.appendChild(c);
      }
      return r;
    }

    /* ---- PERSISTENCE ----------------------------------------------------
     * A 250 ms debounce is not a save. This gets backgrounded by a phone call
     * in the middle of typing a wage sheet, so the draft flushes synchronously
     * on every way a tab can go away. Nothing here leaves the device. */
    var saveT = null;
    function queueSave() {
      if (saveT) clearTimeout(saveT);
      saveT = setTimeout(save, 250);
    }
    function save() {
      if (saveT) { clearTimeout(saveT); saveT = null; }
      try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* private mode */ }
    }
    function restore() {
      var stored = null;
      try { stored = localStorage.getItem(KEY); } catch (e) { return; }
      if (!stored) return;
      var d = null;
      try { d = JSON.parse(stored); } catch (e) { return; }
      if (!d || typeof d !== "object") return;
      if (d.basis === "hr" || d.basis === "yr") S.basis = d.basis;
      if (Array.isArray(d.cols)) {
        for (var i = 0; i < MAXCOL; i++) {
          S.cols[i] = (d.cols[i] && typeof d.cols[i] === "object") ? { name: String(d.cols[i].name || "") } : null;
        }
        if (!S.cols[0]) S.cols[0] = { name: "" };
      }
      if (d.vals && typeof d.vals === "object") {
        Object.keys(d.vals).forEach(function (k) {
          if (Array.isArray(d.vals[k])) {
            S.vals[k] = d.vals[k].slice(0, MAXCOL).map(function (v) { return String(v == null ? "" : v); });
          }
        });
      }
      if (typeof d.hours === "string") S.hours = d.hours;
      if (Array.isArray(d.custom)) {
        S.custom = d.custom.filter(function (c) { return c && c.id && c.label && c.group; })
          .map(function (c) {
            seq++;
            return {
              id: String(c.id), label: String(c.label), group: String(c.group), custom: true,
              kind: c.kind === "aside" ? "aside" : (c.kind === "pct" ? "pct" : "money"),
              unit: String(c.unit || "")
            };
          });
      }
    }
    function flush() { if (saveT) save(); }
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
    window.addEventListener("pagehide", flush);
    window.addEventListener("blur", flush);

    /* ---- WIRE UP --------------------------------------------------------- */
    restore();
    render();
    refresh();

    var copyBtn = byId(cfg.copy);
    if (copyBtn) copyBtn.addEventListener("click", function () {
      copyText(asText(), copyBtn, cfg.copiedLabel || "Copied");
    });
    if (copyBtn && window.ToolkitSend) ToolkitSend(copyBtn, asText, { after: byId(cfg.preview) });   // Send: the same asText(), through the share sheet (C3698)
    var clearBtn = byId(cfg.clear);
    if (clearBtn) clearBtn.addEventListener("click", function () {
      if (!window.confirm(cfg.clearConfirm || "Wipe every figure off this sheet?")) return;
      S.vals = {}; S.custom = []; S.hours = "";
      S.cols = [{ name: "" }, null];
      save(); render(); refresh();
    });

    /* The date in the document header is self-aware — the runtime resolves the
       real date because a job-site tablet's clock can be wrong. */
    document.addEventListener("av:ready", refresh);
    document.addEventListener("av:date", refresh);

    return { text: asText, refresh: refresh };
  }

  window.Package = { mount: mount };
})();
