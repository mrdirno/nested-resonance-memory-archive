/* FIELD TOOLKIT — WHAT CAME BACK: the return leg of the ACCESS boundary.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * av/AV_SOCIETY.md §GETTING IN, §THE INTERFACE. The access loop shipped in ONE
 * direction. `getting-in.html` sends the ask to whoever holds the keys; what
 * comes back is a text message — "yeah that's fine, check in at the desk" — and
 * the foreman reads that as an answer to all eight things he asked for.
 *
 * THE PANEL KILLED THE OBVIOUS BUILD, AND IT WAS RIGHT TO (2026-08-28, four
 * lenses: a building engineer, a GC super, the foreman who SENDS these, and a
 * skeptic handed the program's own rules as weapons). The obvious build was a
 * page for the RECEIVER — paste the ask, tap each line, send back one answer.
 * Two independent kills landed on it and neither is fixable:
 *
 *   · THE ADOPTION KILL. The receiver is not our user and never will be. Across
 *     all fifteen kits this document is addressed to a building engineer, a chief
 *     engineer, a property manager, a director of security, an owner's rep — not
 *     one tradesman among them. The building engineer's own words: "I do not
 *     click links from contractors I don't personally know, on the phone that's
 *     tied to my building's systems." He hits reply and types. A tool whose whole
 *     value depends on a stranger adopting a habit is worth nothing to the man
 *     who already has the problem.
 *   · THE PERMIT KILL. `tools/toolkit-gates/getting-in.mjs` fails the build if
 *     the ask ever contains "approved", "confirmed", "booked", "scheduled" or
 *     "granted", because that page has no channel back and can never know. A
 *     receiver-side answer page exists precisely to BE the grant — and a tick
 *     next to "we have to touch the fire alarm" is then an approval manufactured
 *     by an interface instead of by the building's own numbered permit.
 *
 * So this is not that page. All four lenses, from four directions, converged on
 * the same surviving shape: the tool belongs on OUR side, it runs on the reply he
 * ALREADY got by whatever channel he got it, and its headline output is the one
 * thing only the page holding the original ask can compute —
 *
 *                        WHAT THEY NEVER ANSWERED.
 *
 * The foreman, unprompted, described this build before he was shown it: "assume
 * he keeps texting back 'yeah that's fine' forever, and build the tool on MY side
 * instead. Not 'he said no' — 'he said nothing about the freight elevator.'"
 *
 * AN INTAKE, NOT A FOURTH PAGE — the same law `shared/reconcile.js` was written
 * under. The ask already lives on getting-in.html; the answer is ABOUT those
 * ticks. A separate page would need its own copy of them, and a second copy of a
 * list is a second version of the truth. So the rows are not configured anywhere:
 * they ARE `TOOLKIT_GETIN.need` and `.heads`, exactly as ticked, which is also why
 * this ships to fifteen trades without one line of new per-trade vocabulary.
 *
 * TWO LADDERS, NEVER ONE — and this is the load-bearing rule, demanded as
 * BLOCKING by three of the four lenses independently. The logistics asks (doors,
 * escort, freight, dock, parking, the room, the alarm window) get a real answer
 * ladder. The flagged items that name a PERMITTED activity — fire alarm,
 * sprinkler, power down, hot work, clinical space — get a ladder with NO
 * AFFIRMATIVE RUNG AT ALL. They can only ever record who you were told to call.
 * The GC super's own scar: a one-word "yeah that's fine" meant to cover access
 * was read as covering the torch too, nobody called the alarm company, and the
 * floor evacuated at eleven at night. A tap that answers a logistics question and
 * a permit question with the same word is that failure with a UI on it.
 *
 * THE THREE LINES THAT ARE WORTH MORE THAN THE LIST. Two lenses named the same
 * missing sentence without conferring. The building engineer: "'Yeah Tuesday's
 * fine' is not an answer — it doesn't say whether fine means the 6pm he asked
 * for. Five guys standing at a locked door because 'fine' got treated as a real
 * answer is the single most expensive failure in this whole exchange." The
 * foreman: "the one line that changes what I do is a specific no, or a specific
 * name." So the brief opens with the window they ACTUALLY gave (printed against
 * the one you asked for, whenever the two differ), the person who will physically
 * be at that door, and their cell.
 *
 * AND IT GOES STALE. An answer collected Tuesday for a Saturday night is true
 * when it is sent and wrong four days later — a drill gets scheduled, the tenant
 * comes back, a temp covers the desk. This page cannot ping anybody and never
 * pretends to: it has no server and no channel. What it can do is know how old
 * the answer is and hand him the short same-day message to send himself.
 *
 * NOTHING HERE IS A PERMIT, A BOOKING OR AN APPROVAL, and the document says so
 * every single time it carries a flagged line. This is a crew brief. It records
 * what somebody told us. tools/toolkit-gates/what-came-back.mjs asserts all of
 * it, including that no affirmative rung can ever reach a permitted activity.
 *
 * TWO LINES TO ADD IT TO AN ACCESS-ASK PAGE:
 *   <script src="../shared/whatcameback.js"></script>
 *   WhatCameBack.mount({ after: ..., note: n, getin: G });
 */
(function () {
  "use strict";

  /* THE PERMITTED-ACTIVITY TEST, character for character the one
     tools/toolkit-gates/getting-in.mjs already enforces on the ask side. It is
     duplicated deliberately rather than imported: the ask page must run with or
     without this module, and a shared constant that only exists in the optional
     half is a rule that silently stops applying when the half is absent. The gate
     asserts the two copies agree, so a future edit to either one fails loudly. */
  var PERMITTED = /\b(hot work|fire alarm|sprinkler|power(ed)?[ -]?(down|off)?|torch|solder|clinical|patient|roof access|kettle|asbestos|regulated material|permit|impairment|panel on test|valve|closure)\b/i;

  /* THE LOGISTICS LADDER. Four rungs and a blank, and the blank is the point:
     an untapped row is NOT a no and NOT a yes, it is silence, and silence is what
     puts a crew at a locked door. Tapping wraps back to blank because an answer
     is a choice and a wrong choice has to be reachable without a reset. */
  var WAYS = [
    { k: "got",  label: "Got it",        hint: "what exactly they gave you",      tone: "yes" },
    { k: "open", label: "Already open",  hint: "nothing needed — it's never locked", tone: "in" },
    { k: "no",   label: "No",            hint: "what they said instead",          tone: "no" },
    { k: "else", label: "Not theirs",    hint: "who they sent you to",            tone: "ask" }
  ];

  /* THE FLAGGED LADDER — no affirmative, by design and by gate. There is no rung
     here that a foreman skimming a lock screen could read as clearance. The most
     this page will ever record about a permitted activity is the NAME of the man
     who owns the process, which is the only useful thing anybody can tell you
     about it in a text message anyway. */
  var FLAGS = [
    { k: "who", label: "They named who owns it", hint: "who to call, and their number", tone: "ask" },
    { k: "not", label: "Not that night",         hint: "what they said",                tone: "no" }
  ];

  var CSS =
    ".wcb{margin-top:18px}" +
    ".wcb h2{font-family:var(--cond);font-size:19px;letter-spacing:.01em;margin:0 0 3px;text-transform:uppercase}" +
    ".wcb .wcb-why{font-family:var(--sans);font-size:12px;font-weight:400;letter-spacing:0;text-transform:none;color:var(--muted)}" +
    ".wcb-card{background:var(--paper);border:1px solid var(--line);border-radius:3px;padding:13px 12px;margin:0 0 12px}" +
    ".wcb-note{font-size:12px;color:var(--muted);margin:8px 0 0;line-height:1.5}" +
    ".wcb-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}" +
    ".wcb-grid label{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);margin:0 0 4px}" +
    ".wcb-grid input{width:100%;min-height:44px;padding:10px;font:inherit;font-size:16px;border:1px solid var(--line);border-radius:3px;background:#fff;color:var(--ink)}" +
    ".wcb-ask{font-size:12px;color:var(--muted);margin:6px 0 0}" +
    ".wcb ul{list-style:none;margin:0;padding:0}" +
    ".wcb li{border-top:1px solid var(--line)}" +
    ".wcb li:first-child{border-top:0}" +
    ".wcb-row{display:flex;align-items:flex-start;gap:9px;width:100%;min-height:44px;padding:9px 0;background:none;border:0;font:inherit;color:inherit;text-align:left;cursor:pointer}" +
    ".wcb-row .wcb-nm{flex:1 1 auto;min-width:0;font-size:13px;overflow-wrap:anywhere}" +
    ".wcb-row .wcb-sb{display:block;font-size:11px;color:var(--muted);margin-top:2px;overflow-wrap:anywhere}" +
    ".wcb-chip{flex:0 0 auto;font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;padding:5px 7px;border-radius:3px;border:1px solid var(--line);color:var(--muted);background:#fff;white-space:nowrap;max-width:44vw;overflow:hidden;text-overflow:ellipsis}" +
    ".wcb-chip.on{background:var(--deep);border-color:var(--deep);color:#fff}" +
    ".wcb-chip.silent{border-style:dashed}" +
    ".wcb-chip.loud{background:var(--flag);border-color:var(--flag);color:var(--flag-ink)}" +
    ".wcb-said{width:100%;min-height:44px;padding:9px 10px;margin:0 0 9px;font:inherit;font-size:16px;border:1px solid var(--line);border-radius:3px;background:#fff;color:var(--ink)}" +
    ".wcb-empty{font-size:12px;color:var(--muted);padding:10px 0;margin:0}" +
    ".wcb-gap{background:var(--flag);color:var(--flag-ink);border-radius:3px;padding:11px 12px;margin:0 0 12px}" +
    ".wcb-gap b{display:block;font-family:var(--cond);font-size:16px;text-transform:uppercase;letter-spacing:.02em;margin-bottom:5px}" +
    ".wcb-gap ul{margin:0;padding:0}" +
    ".wcb-gap li{border:0;font-size:13px;padding:2px 0;overflow-wrap:anywhere}" +
    ".wcb-gap p{margin:7px 0 0;font-size:12px;line-height:1.5}" +
    ".wcb-stale{font-size:12px;color:var(--ink);background:var(--tint);border-left:3px solid var(--deep);padding:9px 10px;margin:0 0 12px;line-height:1.5}" +
    ".wcb-btns{display:flex;flex-wrap:wrap;gap:8px;margin:11px 0 0}" +
    ".wcb-btn{flex:1 1 auto;min-height:44px;padding:11px 13px;font:inherit;font-size:14px;font-weight:600;border-radius:3px;border:1px solid var(--deep);background:var(--deep);color:#fff;cursor:pointer}" +
    ".wcb-btn.ghost{background:#fff;color:var(--ink);border-color:var(--line)}" +
    ".wcb-pre{white-space:pre-wrap;overflow-wrap:anywhere;font-family:var(--mono);font-size:12px;line-height:1.5;background:var(--paper);border:1px solid var(--line);border-radius:3px;padding:11px;margin:11px 0 0}" +
    ".wcb-paste{width:100%;min-height:96px;padding:10px;font:inherit;font-size:16px;border:1px solid var(--line);border-radius:3px;background:#fff;color:var(--ink);resize:vertical}";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function clean(s) { return String(s == null ? "" : s).trim(); }

  /* THE JOIN, and it is deliberately the timid half of reconcile.js's. What comes
     back here is not another toolkit document, it is a sentence a man thumbed at a
     panel — so there is no fuzzy scoring at all. A pasted reply only ever SHOWS
     him the words beside his rows; it never moves a rung. Propose-never-apply, and
     here even the proposal is only ever a highlight, because the cost of a wrong
     join on this boundary is a crew rolling on an answer nobody gave. */
  function mentions(reply, name) {
    if (!reply) return false;
    var hay = reply.toLowerCase();
    var toks = String(name).toLowerCase().match(/[a-z]{4,}/g) || [];
    if (!toks.length) return false;
    var hit = 0;
    for (var i = 0; i < toks.length; i++) if (hay.indexOf(toks[i]) !== -1) hit++;
    return hit >= Math.max(1, Math.ceil(toks.length * 0.6));
  }

  function dayCount(fromISO, toISO) {
    if (!fromISO || !toISO) return null;
    var a = new Date(fromISO + "T12:00:00"), b = new Date(toISO + "T12:00:00");
    if (isNaN(a) || isNaN(b)) return null;
    return Math.round((b - a) / 86400000);
  }
  function pretty(iso) {
    if (!iso) return "";
    var d = new Date(iso + "T12:00:00");
    if (isNaN(d)) return "";
    return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
  }
  function todayISO() {
    var d = new Date(), p = function (n) { return (n < 10 ? "0" : "") + n; };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate());
  }

  function copyText(txt, btn, done) {
    var back = btn.textContent;
    var ok = function () {
      btn.textContent = done || "Copied";
      setTimeout(function () { btn.textContent = back; }, 1800);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(ok, function () { fallback(txt, ok); });
    } else fallback(txt, ok);
  }
  function fallback(txt, ok) {
    var ta = document.createElement("textarea");
    ta.value = txt;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:0;left:0;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); ok(); } catch (e) { /* nothing else to try */ }
    document.body.removeChild(ta);
  }

  function mount(cfg) {
    cfg = cfg || {};
    var host = typeof cfg.after === "string" ? document.querySelector(cfg.after) : cfg.after;
    var note = cfg.note;
    if (!host || !host.parentNode || !note) return null;

    var st = document.createElement("style");
    st.textContent = CSS;
    document.head.appendChild(st);

    var KEY = "toolkit." + (cfg.slug || "av") + ".camehome.v1";
    var state = { window: "", who: "", cell: "", by: "", on: "", reply: "", rows: {} };
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var p = JSON.parse(raw);
        if (p && typeof p === "object") for (var k in state) if (p[k] != null) state[k] = p[k];
      }
    } catch (e) { /* a corrupt draft is not worth a broken page */ }

    var wrap = el("section", "wcb");
    wrap.id = "wcbCard";
    wrap.innerHTML =
      '<p class="section-label">Then they answered</p>' +
      '<div class="wcb-card">' +
        '<h2>What came back <span class="wcb-why">&mdash; whatever they sent you, against what you actually asked for</span></h2>' +
        '<p class="wcb-note" id="wcbLede">Nobody has to open anything for this to work. Take the text, the email or the phone call you already got, put the answer against the list you sent, and this tells you the one thing only your own ask can know &mdash; <b>what they never answered.</b> Silence is not a yes.</p>' +
        '<div class="wcb-grid" style="margin-top:12px">' +
          '<div><label for="wcbWin">The window they actually gave</label><input type="text" id="wcbWin" placeholder="6 to 11" autocomplete="off"></div>' +
          '<div><label for="wcbWho">Who&rsquo;s at the door</label><input type="text" id="wcbWho" placeholder="Manny &mdash; front desk" autocapitalize="words" autocomplete="off"></div>' +
          '<div><label for="wcbCell">Their number</label><input type="tel" id="wcbCell" placeholder="the one that rings at 6pm" autocomplete="off"></div>' +
          '<div><label for="wcbBy">Who answered you</label><input type="text" id="wcbBy" placeholder="Diane &mdash; building engineer" autocapitalize="words" autocomplete="off"></div>' +
          '<div><label for="wcbOn">When they answered</label><input type="date" id="wcbOn"></div>' +
        '</div>' +
        '<p class="wcb-ask" id="wcbAsk" hidden></p>' +
        '<p class="wcb-note"><b>A name and a number beat every tick on this page.</b> &ldquo;Approved&rdquo; from nobody is worth nothing at six on a Saturday when it&rsquo;s wrong and you need somebody to call.</p>' +
      '</div>' +
      '<div class="wcb-card">' +
        '<h2>Paste what they sent <span class="wcb-why">&mdash; optional; it just highlights, it never answers for you</span></h2>' +
        '<textarea class="wcb-paste" id="wcbPaste" placeholder="Sat is fine, 6 to 11 only, security has the fob, get me the COI by Friday. Freight is on recall for another tenant, use the passenger."></textarea>' +
        '<p class="wcb-note">We mark the lines their words look like they touched, so you can see the gaps faster. <b>Nothing here taps a row for you</b> &mdash; their sentence is a claim by them, and on this boundary a wrong guess is a crew at a locked door.</p>' +
      '</div>' +
      '<div class="wcb-card" id="wcbNeedCard">' +
        '<h2>What you asked them to do <span class="wcb-why">&mdash; tap a row to say what came back; tap past the end to clear it</span></h2>' +
        '<div id="wcbNeed"></div>' +
      '</div>' +
      '<div class="wcb-card" id="wcbHeadCard">' +
        '<h2>What you flagged <span class="wcb-why">&mdash; these can only ever record who owns it</span></h2>' +
        '<div id="wcbHead"></div>' +
        '<p class="wcb-note"><b>There is no &ldquo;yes&rdquo; on this list and there never will be.</b> A fire panel on test, a sprinkler impairment, a power-down and hot work are permits somebody on their side issues and numbers. Nothing you tap here is one, and this page will never print that one was. All it records is who they told you to call.</p>' +
      '</div>' +
      '<p class="section-label">The brief</p>' +
      '<div class="wcb-card">' +
        '<div id="wcbStale"></div>' +
        '<div id="wcbGap"></div>' +
        '<div class="wcb-btns">' +
          '<button type="button" class="wcb-btn" id="wcbCopy">Copy the brief</button>' +
          '<button type="button" class="wcb-btn ghost" id="wcbRe">Copy the day-of check</button>' +
        '</div>' +
        '<p class="wcb-note">The brief is what you send your own crew before they leave the shop. <b>The day-of check is the short one you send the building a couple of hours before you roll</b> &mdash; an answer given four days ago was true when they typed it, and a drill, a tenant coming back or a temp on the desk makes it wrong without anybody lying to you.</p>' +
        '<pre class="wcb-pre" id="wcbPre"></pre>' +
      '</div>';
    host.parentNode.insertBefore(wrap, host.nextSibling);

    var $ = function (s) { return wrap.querySelector(s); };
    var fields = { window: $("#wcbWin"), who: $("#wcbWho"), cell: $("#wcbCell"), by: $("#wcbBy"), on: $("#wcbOn") };
    var paste = $("#wcbPaste");

    /* THE HEADER FIELDS NEVER REBUILD THE LISTS. They are the three lines the
       panel said outrank the whole list, which means they are also the three a
       man types longest in — and a keystroke that tears down and re-renders two
       lists underneath him is how a page drops the caret out of a field on a
       phone. They move the brief and the gap block only. */
    Object.keys(fields).forEach(function (k) {
      fields[k].value = state[k] || "";
      fields[k].addEventListener("input", function () { state[k] = fields[k].value; save(); renderMeta(); });
    });
    paste.value = state.reply || "";
    var pasteT = null;
    paste.addEventListener("input", function () {
      state.reply = paste.value;
      save();
      clearTimeout(pasteT);
      pasteT = setTimeout(render, 140);
    });

    function save() {
      try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
    }
    window.addEventListener("pagehide", save);

    /* THE ROWS ARE THE ASK. Not a config, not a copy — the live ticks off the page
       above. Untick something on the ask and its answer row goes with it, because
       an answer to a question you are no longer asking is the second version of
       the truth this module exists to refuse. */
    function asked(id) {
      var v = note.get(id);
      return Array.isArray(v) ? v.slice() : [];
    }
    function subOf(id, name) {
      var opts = (cfg.getin && cfg.getin[id]) || [];
      for (var i = 0; i < opts.length; i++) {
        var o = opts[i];
        var nm = typeof o === "string" ? o : o.name;
        if (nm === name) return (o && typeof o === "object" && o.sub) || "";
      }
      return "";
    }

    function rowState(name) {
      var r = state.rows[name];
      if (!r || typeof r !== "object") return { k: "", said: "" };
      return { k: r.k || "", said: r.said || "" };
    }
    function setRow(name, patch) {
      var r = rowState(name);
      state.rows[name] = { k: patch.k != null ? patch.k : r.k, said: patch.said != null ? patch.said : r.said };
      save();
    }

    function ladderFor(name) { return PERMITTED.test(name) ? FLAGS : WAYS; }

    function buildList(hostEl, names, id) {
      hostEl.innerHTML = "";
      if (!names.length) {
        hostEl.appendChild(el("p", "wcb-empty", cfg.emptyLabel ||
          "Nothing ticked on the ask above yet — tick what you need from them and it shows up here to answer."));
        return;
      }
      var ul = el("ul");
      names.forEach(function (name) {
        var ladder = ladderFor(name);
        var cur = rowState(name);
        var idx = -1;
        for (var i = 0; i < ladder.length; i++) if (ladder[i].k === cur.k) idx = i;
        var rung = idx >= 0 ? ladder[idx] : null;

        var li = el("li");
        var btn = el("button", "wcb-row");
        btn.type = "button";
        var nm = el("span", "wcb-nm");
        nm.appendChild(document.createTextNode(name));
        var sub = subOf(id, name);
        if (sub) nm.appendChild(el("span", "wcb-sb", sub));
        btn.appendChild(nm);

        var chip = el("span", "wcb-chip" + (rung ? " on" : " silent") + (!rung ? " loud" : ""),
          rung ? rung.label : "Nothing said");
        btn.appendChild(chip);
        btn.setAttribute("aria-label", name + " — " + (rung ? rung.label : "nothing said"));
        btn.addEventListener("click", function () {
          var next = idx + 1;
          setRow(name, { k: next >= ladder.length ? "" : ladder[next].k });
          render();
        });
        li.appendChild(btn);

        if (rung) {
          var ta = el("input", "wcb-said");
          ta.type = "text";
          ta.value = cur.said;
          ta.placeholder = rung.hint;
          ta.setAttribute("aria-label", name + " — " + rung.hint);
          ta.addEventListener("input", function () { setRow(name, { said: ta.value }); renderDoc(); });
          li.appendChild(ta);
        }

        if (state.reply && mentions(state.reply, name)) {
          var hint = el("p", "wcb-note", "Their message looks like it touches this one.");
          hint.style.margin = "0 0 9px";
          li.appendChild(hint);
        }
        ul.appendChild(li);
      });
      hostEl.appendChild(ul);
    }

    /* ── THE DOCUMENT ────────────────────────────────────────────────────────
     * A crew brief, and it opens with the two lines the receiving lens and the
     * sending lens both named as the ones that decide whether the night happens.
     * Then the GAP, before anything that reads like good news. */
    function silent(names) {
      return names.filter(function (n) { return !rowState(n).k; });
    }

    function brief() {
      var need = asked("need"), heads = asked("heads");
      var day = clean(note.get("day")), win = clean(note.get("window")), site = clean(note.get("site"));
      var L = [];
      L.push("BEFORE WE ROLL" + (day ? "  ·  " + pretty(day) : ""));
      if (site) L.push(site);
      L.push("");

      var gave = clean(state.window);
      L.push("WHAT THEY GAVE US");
      if (gave) L.push("  Window: " + gave + (win && gave !== win ? "   (we asked for " + win + ")" : ""));
      else L.push("  Window: THEY NEVER SAID" + (win ? " — we asked for " + win : ""));
      var who = clean(state.who), cell = clean(state.cell);
      if (who || cell) L.push("  At the door: " + [who, cell].filter(Boolean).join(" — "));
      else L.push("  At the door: NOBODY NAMED — find out before the crew leaves");
      var by = clean(state.by), on = clean(state.on);
      if (by || on) L.push("  Answered by: " + [by, on ? pretty(on) : ""].filter(Boolean).join(", "));

      var gapNeed = silent(need), gapHead = silent(heads);
      if (gapNeed.length || gapHead.length) {
        L.push("");
        L.push("NOTHING SAID ABOUT THESE — " + (gapNeed.length + gapHead.length));
        gapNeed.concat(gapHead).forEach(function (n) { L.push("  · " + n); });
        L.push("Nobody said no to these. Nobody said yes either. Silence is not a yes — get an answer before the crew rolls.");
      }

      var flagged = heads.filter(function (n) { return rowState(n).k; });
      if (flagged.length) {
        L.push("");
        L.push("STILL ON THEIR PROCESS — " + flagged.length);
        flagged.forEach(function (n) {
          var r = rowState(n);
          if (r.k === "who") L.push("  · " + n + " — they pointed us at: " + (r.said || "SOMEBODY, BUT THEY NEVER SAID WHO"));
          else L.push("  · " + n + " — not that night" + (r.said ? ": " + r.said : ""));
        });
        L.push("Nothing on this list is a permit and nothing here says one was issued. Somebody on their side still runs their own process on every one of these — this only records what we were told.");
      }

      var answered = need.filter(function (n) { return rowState(n).k; });
      if (answered.length) {
        L.push("");
        L.push("WHAT THEY SAID, LINE BY LINE");
        answered.forEach(function (n) {
          var r = rowState(n);
          var lab = "";
          for (var i = 0; i < WAYS.length; i++) if (WAYS[i].k === r.k) lab = WAYS[i].label.toLowerCase();
          L.push("  · " + n + " — " + lab + (r.said ? ": " + r.said : " (they didn't say what)"));
        });
      }

      var age = dayCount(on, day);
      if (on && day && age !== null && age >= 1) {
        L.push("");
        L.push("This answer is " + age + " day" + (age === 1 ? "" : "s") + " older than the night" +
          " — they answered " + pretty(on) + ", we're in on " + pretty(day) + ". Re-confirm before anybody leaves the shop.");
      }
      L.push("");
      L.push("This is what we were told, written down. It is not a permit, not a booking and not an approval, and nobody on their side has seen this page.");
      return L.join("\n");
    }

    /* THE DAY-OF CHECK — the foreman's own ask, built the only honest way a page
       with no server can build it: it does not send anything and never claims to.
       It writes the short message HE sends, and it is short on purpose, because
       the whole point is that it gets answered from a lock screen in one line. */
    function reconfirm() {
      var need = asked("need"), heads = asked("heads");
      var day = clean(note.get("day")), site = clean(note.get("site"));
      var gaps = silent(need).concat(silent(heads));
      var L = [];
      L.push("QUICK ONE BEFORE WE ROLL" + (day ? "  ·  " + pretty(day) : "") + (site ? "  ·  " + site : ""));
      var gave = clean(state.window);
      L.push("");
      L.push([clean(state.by), "we're on for tonight" + (gave ? ", " + gave : "") + " — still good?"].filter(Boolean).join(" — "));
      if (gaps.length) {
        L.push("");
        L.push("Still nothing back on:");
        gaps.forEach(function (n) { L.push("  · " + n); });
      }
      var routed = heads.filter(function (n) { return rowState(n).k === "who"; });
      if (routed.length) {
        L.push("");
        routed.forEach(function (n) {
          var r = rowState(n);
          L.push("You pointed me at " + (r.said || "somebody on your side") + " for \u201c" + n + "\u201d — that's set on your end?");
        });
      }
      var cnt = clean(note.get("count"));
      var who = clean(state.who);
      L.push("");
      L.push((cnt ? cnt + " of us" : "We") + " will be at the door" + (who ? ", meeting " + who : "") + ". If anything moved, tell me now and we'll stand down before anybody leaves the shop.");
      return L.join("\n");
    }

    function renderDoc() { $("#wcbPre").textContent = brief(); }

    /* A REBUILD MUST NOT EAT THE CARET. The lists are torn down and re-rendered
       whenever a rung moves or a tick changes upstream, and the detail field a man
       is typing into lives INSIDE a row. Losing focus mid-word on a phone is the
       kind of defect that gets a tool closed and never reopened, so the active
       row's field and caret position are carried across the rebuild by name. */
    function renderLists() {
      var act = document.activeElement;
      var keep = null;
      if (act && act.classList && act.classList.contains("wcb-said")) {
        var li = act.closest("li");
        var nmEl = li && li.querySelector(".wcb-nm");
        if (nmEl) keep = { name: nmEl.firstChild.textContent, at: act.selectionStart };
      }
      var need = asked("need"), heads = asked("heads");
      buildList($("#wcbNeed"), need, "need");
      buildList($("#wcbHead"), heads, "heads");
      $("#wcbHeadCard").hidden = !heads.length;
      if (keep) {
        var lis = wrap.querySelectorAll("#wcbNeed li, #wcbHead li");
        for (var i = 0; i < lis.length; i++) {
          var n = lis[i].querySelector(".wcb-nm");
          var f = lis[i].querySelector(".wcb-said");
          if (n && f && n.firstChild.textContent === keep.name) {
            f.focus();
            try { f.setSelectionRange(keep.at, keep.at); } catch (e) { /* type may not support it */ }
            break;
          }
        }
      }
    }

    function renderMeta() {
      var need = asked("need"), heads = asked("heads");
      var win = clean(note.get("window"));
      var ask = $("#wcbAsk");
      if (win) { ask.textContent = "You asked for " + win + ". Put what they actually gave you above — a shorter window they never spelled out is the most expensive thing on this page."; ask.hidden = false; }
      else ask.hidden = true;

      var gaps = silent(need).concat(silent(heads));
      var g = $("#wcbGap");
      if (gaps.length) {
        g.innerHTML = '<div class="wcb-gap"><b>Nothing said about these — ' + gaps.length + '</b><ul>' +
          gaps.map(function (n) { return "<li>· " + esc(n) + "</li>"; }).join("") +
          '</ul><p>Silence is not a yes. Every one of these went out on your ask and came back untouched.</p></div>';
      } else if (need.length || heads.length) {
        g.innerHTML = '<div class="wcb-stale">Every line you sent has something against it. That is not the same as a good answer &mdash; read the brief before you send it.</div>';
      } else g.innerHTML = "";

      var age = dayCount(clean(state.on), clean(note.get("day")));
      var s = $("#wcbStale");
      if (age !== null && age >= 1) {
        s.innerHTML = '<div class="wcb-stale"><b>This answer is ' + age + ' day' + (age === 1 ? "" : "s") +
          ' older than the night.</b> It was true when they sent it. A drill, a tenant back in the space or a temp on the desk makes it wrong without anybody lying to you &mdash; send the day-of check.</div>';
      } else s.innerHTML = "";

      renderDoc();
    }

    function render() { renderLists(); renderMeta(); }

    $("#wcbCopy").addEventListener("click", function () { copyText(brief(), this, "Copied — send it to your crew"); });
    $("#wcbRe").addEventListener("click", function () { copyText(reconfirm(), this, "Copied — send it to them"); });
    if (window.ToolkitSend) { ToolkitSend($("#wcbCopy"), brief); ToolkitSend($("#wcbRe"), reconfirm); }   // Send: same brief()/reconfirm() (C3698)

    if (!state.on) { state.on = todayISO(); fields.on.value = state.on; }

    /* CLEAR HAS TO REACH THE ANSWER, and this is the defect the module's own
       opening argument would have shipped with. The ask's Clear wipes the night,
       the rooms and the ticks so a man can start the next job on the same phone.
       The answers lived in their own key and survived it — so re-ticking the same
       three asks for a DIFFERENT building brought back the last building's window,
       the last building's man at the door, and last week's rung on every row. That
       is precisely the second version of the truth this file refuses to be.
       Bound after the engine's own handler so it runs second, and it re-reads the
       ask rather than trusting the click: if the man cancelled the confirm, the
       day is still there and nothing here moves. */
    var clearBtn = document.getElementById("clear");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        setTimeout(function () {
          if (clean(note.get("day")) || asked("need").length || asked("heads").length) return;
          state.rows = {};
          ["window", "who", "cell", "by", "reply"].forEach(function (k) {
            state[k] = "";
            if (fields[k]) fields[k].value = "";
          });
          paste.value = "";
          state.on = todayISO();
          fields.on.value = state.on;
          save();
          render();
        }, 0);
      });
    }

    /* The ask page re-renders on every tick; the answer rows are its ticks, so
       this has to follow it. A MutationObserver on the ask's own lists is the
       only coupling that cannot go stale, because it watches the DOM the engine
       actually writes rather than an event the engine never promised. */
    var form = document.getElementById("form");
    if (form && window.MutationObserver) {
      var t = null;
      new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(render, 60);
      }).observe(form, { subtree: true, attributes: true, attributeFilter: ["checked"], childList: true });
      form.addEventListener("change", function () { setTimeout(render, 0); });
    }

    render();
    return { doc: brief, reconfirm: reconfirm, render: render };
  }

  window.WhatCameBack = { mount: mount, PERMITTED: PERMITTED, WAYS: WAYS, FLAGS: FLAGS };
})();
