/* THE COMMONS ENGINE — one picker, many surfaces.
 *
 * WHY THIS EXISTS. The commons shipped as one page (the gear list) with its
 * engine inline. The second surface — the tips — is the SAME SHAPE: filter by
 * trade, always show the universal floor, tick rows, copy the picks out as
 * something you can paste to somebody. The toolkit book's rule for the second
 * instance of a shape is EXTRACT THE ENGINE, never fork a third page. So a
 * commons surface is now a masthead, a data file and a config object; the
 * picker, the trade partition, the per-device memory and the copy-out live
 * here and get fixed once for everyone.
 *
 * THE COMMONS IS NOT A TRADE. It carries no trade.js on purpose: served_trades()
 * and av_wishing_well.py both derive the trade list from <dir>/trade.js on disk,
 * so a config here would report a trade that does not exist and inflate breadth
 * debt. It carries shared/feedback.js — the standalone drop-in — instead of the
 * trade runtime.
 *
 * COMMONS_TRADES LIVES HERE, NOT IN A DATA FILE. It used to sit in gear.js,
 * where the second surface could not see it and — worse — where nothing tied it
 * to the trades that actually have toolkits. Framing shipped 2026-08-09 and this
 * list was never told: for two days a framer opening the commons saw six chips
 * and none of them were his. The deploy now asserts this list against the trades
 * the runtime actually switches to, so that specific rot fails the build.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.COMMONS_TRADES = [
  { slug: "universal",   short: "Every trade",  name: "Every Trade",          color: "#FF6B1A" },
  { slug: "av",          short: "AV",           name: "AV",                   color: "#F0BE1E" },
  { slug: "plumbing",    short: "Plumbing",     name: "Plumbing",             color: "#C87137" },
  { slug: "electrical",  short: "Electrical",   name: "Electrical",           color: "#3FB6F5" },
  { slug: "hvac",        short: "HVAC/R",       name: "HVAC/R",               color: "#4FE0C0" },
  { slug: "low-voltage", short: "Low-voltage",  name: "Low-Voltage & Fire",   color: "#FF9E80" },
  { slug: "gc",          short: "GC / Super",   name: "GC & Site Super",      color: "#8CE86B" },
  { slug: "framing",     short: "Framing",      name: "Framing & Drywall",    color: "#B7ADFF" },
  { slug: "roofing",     short: "Roofing",      name: "Roofing",              color: "#FF93C9" },
  { slug: "creative",    short: "Creative",     name: "Creative / Video",     color: "#EDA5FF" }
];

/* The surfaces of the commons, in reading order. The nav dropdown on every page
 * of every trade links "the commons" as ONE destination, so without this rail a
 * reader who landed on the gear list had no way to discover the tips existed.
 * Adding a surface here puts it on every other surface at once. */
window.COMMONS_SURFACES = [
  { href: "index.html", label: "What's in the bag" },
  { href: "tips.html",  label: "Learned the hard way" }
];

window.Commons = (function () {
  "use strict";

  var TRADES = window.COMMONS_TRADES;
  var SURFACES = window.COMMONS_SURFACES;
  /* The trade filter is SHARED across surfaces on purpose — a plumber who picked
   * plumbing on the gear list is still a plumber when he opens the tips. The
   * picks are not shared: a bag and a handoff list are different things. */
  var VIEWKEY = "commons.view.v1";

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  };

  function mount(cfg) {
    var ROWS = cfg.rows || [];
    var KEY = cfg.pickKey;

    /* ---- the picks: per-device, no login. Same reasoning as the toolkit's
     * favorites — an account is a step, and a step is why nobody uses it. ---- */
    function loadPicks() {
      try {
        var raw = JSON.parse(localStorage.getItem(KEY) || "[]");
        return Array.isArray(raw) ? raw.filter(function (x) { return typeof x === "string"; }) : [];
      } catch (e) { return []; }
    }
    function savePicks(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
    var picks = loadPicks();
    var picked = function (id) { return picks.indexOf(id) !== -1; };

    function loadView() {
      try {
        var v = localStorage.getItem(VIEWKEY);
        return v && TRADES.some(function (t) { return t.slug === v; }) ? v : "universal";
      } catch (e) { return "universal"; }
    }
    var view = loadView();

    /* ---- the rail: where else the commons goes ---- */
    function buildRail() {
      var box = $("rail");
      if (!box) return;
      box.textContent = "";
      SURFACES.forEach(function (s) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = s.href;
        a.textContent = s.label;
        if (s.href === cfg.surface) a.setAttribute("aria-current", "page");
        li.appendChild(a);
        box.appendChild(li);
      });
    }

    /* ---- chips ---- */
    function buildChips() {
      var box = $("chips");
      box.textContent = "";
      TRADES.forEach(function (t) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "chip";
        b.setAttribute("aria-pressed", String(t.slug === view));
        b.style.setProperty("--tradecol", t.color);
        b.innerHTML = '<span class="dot"></span>' + esc(t.short);
        b.addEventListener("click", function () {
          view = t.slug;
          try { localStorage.setItem(VIEWKEY, view); } catch (e) {}
          buildChips();
          render();
        });
        box.appendChild(b);
      });
    }

    var tradeOf = function (slug) {
      return TRADES.filter(function (x) { return x.slug === slug; })[0];
    };

    /* ---- THE PARTITION — ONE function, and the screen and the document both
     * read it. They used to disagree, and the disagreement shipped a lie.
     *
     * The screen showed the floor plus your trade. The document stamped THE CHIP
     * YOU HAD OPEN onto everything you were carrying. So: tick three electrical
     * rows, tap Plumbing, and the counter still said 3 while nothing on screen
     * was ticked — the picks were real, invisible, and impossible to take back
     * out — and Copy produced WHAT'S IN THE BAG — PLUMBING over glow rods,
     * lineman's pliers and wire strippers. The page told somebody those were a
     * plumber's tools. (§SCARS 2026-08-13.)
     *
     * The bag stays CROSS-TRADE, which was never the bug: a super carries three
     * trades' gear on purpose and dropping his picks on a chip tap would be the
     * silent data loss this book already has a scar for. What changes is that a
     * picked row is never invisible and never mislabelled — anything outside the
     * current view rides in its own section, on screen and in the document. ---- */
    function partition(v) {
      var uni = [], own = [], away = [];
      ROWS.forEach(function (g) {
        if (g.t.indexOf("universal") !== -1) uni.push(g);
        else if (g.t.indexOf(v) !== -1) own.push(g);
        else if (picked(g.id)) away.push(g);
      });
      /* HIS OWN ROWS FIRST, and this was found by doing the job rather than by
       * any gate. A section rendered in FILE order, and rows shared with several
       * trades sit earlier in the file than any one trade's own — so the moment
       * roofing was seeded, the first four rows under "Roofing" were still a
       * cordless drill, a torpedo level, a voltage tester and a radio, with the
       * eighteen written for him below them. Every count passed. The page still
       * opened on somebody else's bag. Narrow tag list = written for this trade,
       * so it leads; the sort is stable, so file order survives inside each band. */
      own.sort(function (a, b) { return a.t.length - b.t.length; });
      return { uni: uni, own: own, away: away };
    }

    /* "in your bag" / "to pass on" — the surface already names its own picks, so
     * a third surface gets this section with no config of its own. */
    var awayTitle = function () { return "Also " + cfg.pickLabel; };
    var awayTrades = function (rows) {
      var seen = [];
      rows.forEach(function (g) {
        g.t.forEach(function (sl) {
          if (sl !== "universal" && seen.indexOf(sl) === -1) seen.push(sl);
        });
      });
      return seen.map(function (sl) { var t = tradeOf(sl); return t ? t.name : sl; });
    };

    /* ---- what shows for the current view: the universal floor is ALWAYS shown,
     * because that is the whole thesis of a commons — what every trade shares is
     * the point, and a plumber who only sees plumbing learned nothing. ---- */
    function sectionsFor(v) {
      var p = partition(v);
      var out = [{ slug: "universal", title: cfg.floor.title, note: cfg.floor.note, items: p.uni }];
      if (v !== "universal") {
        var t = tradeOf(v);
        out.push({
          slug: v,
          title: (t ? t.name : v) + " " + cfg.own.suffix,
          note: cfg.own.note,
          items: p.own
        });
      }
      if (p.away.length) {
        out.push({
          slug: "away",
          title: awayTitle(),
          /* Names what the rows ARE, never where he was standing when he ticked
           * them: he picked under ONE chip, and a row can carry several trades.
           * Getting that backwards would be a smaller version of the same lie
           * this section exists to fix. */
          note: "These belong to " + awayTrades(p.away).join(", ") +
                ". They ride in the list you copy, and this is where you take them back out.",
          items: p.away
        });
      }
      return out;
    }

    function render() {
      var host = $("sections");
      host.textContent = "";
      var secs = sectionsFor(view), total = 0;

      secs.forEach(function (s) {
        total += s.items.length;
        if (!s.items.length) return;
        var sec = document.createElement("section");
        sec.className = "sec";

        var head = document.createElement("div");
        head.className = "sechead";
        head.innerHTML = "<h2>" + esc(s.title) + "</h2>" +
                         '<span class="count">' + s.items.length + " " + esc(cfg.countNoun) + "</span>";
        sec.appendChild(head);

        var note = document.createElement("p");
        note.className = "secnote";
        note.textContent = s.note;
        sec.appendChild(note);

        var ul = document.createElement("ul");
        ul.className = "gear";
        s.items.forEach(function (g) { ul.appendChild(row(g)); });
        sec.appendChild(ul);
        host.appendChild(sec);
      });

      $("none").style.display = total ? "none" : "block";
      tally();
    }

    function row(g) {
      var li = document.createElement("li");
      li.className = "item" + (picked(g.id) ? " on" : "");

      var lab = document.createElement("label");
      lab.className = "lab";

      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = picked(g.id);
      cb.addEventListener("change", function () {
        if (cb.checked) { if (!picked(g.id)) picks.push(g.id); }
        else { picks = picks.filter(function (x) { return x !== g.id; }); }
        savePicks(picks);
        li.className = "item" + (cb.checked ? " on" : "");
        tally();
      });

      var txt = document.createElement("div");
      txt.className = "txt";
      var tags = g.t.filter(function (x) { return x !== "universal"; }).map(function (sl) {
        var t = TRADES.filter(function (x) { return x.slug === sl; })[0];
        return '<span class="tag">' + esc(t ? t.short : sl) + "</span>";
      }).join("");
      txt.innerHTML = '<div class="nm">' + esc(g.n) + "</div>" +
                      '<p class="why">' + esc(g.w) + "</p>" +
                      (tags ? '<div class="tags">' + tags + "</div>" : "");

      lab.appendChild(cb);
      lab.appendChild(txt);
      li.appendChild(lab);
      return li;
    }

    function tally() {
      var n = picks.length;
      $("cnt").textContent = String(n);
      $("cntlbl").textContent = cfg.pickLabel;
      $("copy").disabled = n === 0;
    }

    /* ---- the handoff: the reason this is a tool and not a blog post. What a
     * journeyman actually does with this is paste it to somebody. ---- */
    function pickedText() {
      var mine = function (a) { return a.filter(function (g) { return picked(g.id); }); };
      var p = partition(view);
      var uni = mine(p.uni), own = mine(p.own), away = p.away; /* away is picks-only already */
      var t = tradeOf(view);
      /* The trade name goes in the title only when a row in the list is actually
       * that trade's. Stamping the open chip on a list containing none of its
       * rows is the same lie one line higher up. */
      var named = t && t.slug !== "universal" && own.length > 0;
      var lines = [cfg.copy.title + (named ? " — " + t.name.toUpperCase() : ""), ""];

      var block = function (head, rows) {
        if (!rows.length) return;
        if (lines[lines.length - 1] !== "") lines.push("");
        lines.push(head);
        rows.forEach(function (g) { lines.push(cfg.copy.line(g)); });
      };

      block("EVERY TRADE", uni);
      block(named ? t.name.toUpperCase() : "TRADE-SPECIFIC", own);
      block((awayTitle() + " — " + awayTrades(away).join(", ")).toUpperCase(), away);

      lines.push("");
      lines.push(cfg.copy.footer(uni.length + own.length + away.length));
      return lines.join("\n");
    }

    function copyOut() {
      var txt = pickedText(), btn = $("copy"), old = btn.textContent;
      var done = function (ok) {
        btn.textContent = ok ? "✓ Copied" : "Select & copy";
        setTimeout(function () { btn.textContent = old; }, 1900);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(function () { done(true); }, function () { fallback(txt, done); });
      } else { fallback(txt, done); }
    }

    function fallback(txt, done) {
      var ta = document.createElement("textarea");
      ta.value = txt;
      ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;left:8px;bottom:74px;width:calc(100% - 16px);height:36vh;z-index:99";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      if (ok) { document.body.removeChild(ta); done(true); }
      else { done(false); setTimeout(function () { if (ta.parentNode) document.body.removeChild(ta); }, 9000); }
    }

    $("copy").addEventListener("click", copyOut);
    $("clr").addEventListener("click", function () {
      picks = []; savePicks(picks); render();
    });
    var add = $("addbtn");
    if (add) {
      add.addEventListener("click", function () {
        if (window.Feedback && window.Feedback.open) window.Feedback.open(cfg.addKind || "new_tool");
      });
    }

    if (cfg.voice === "sentence") document.body.classList.add("voice-sentence");

    buildRail();
    buildChips();
    render();
  }

  return { mount: mount };
})();
