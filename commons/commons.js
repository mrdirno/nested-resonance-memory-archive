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
  { slug: "creative",    short: "Creative",     name: "Creative / Video",     color: "#EDA5FF" },
  { slug: "concrete",    short: "Concrete",     name: "Concrete & Rebar",     color: "#2DD758" },
  { slug: "masonry",     short: "Masonry",      name: "Masonry & Brick",      color: "#B9EE1B" },
  { slug: "sitework",    short: "Sitework",     name: "Sitework & Underground", color: "#FFDDA3" },
  { slug: "flooring",    short: "Flooring",     name: "Flooring & Tile",      color: "#8FECFF" },
  { slug: "painting",    short: "Painting",     name: "Painting",             color: "#29FF29" }
];

/* The surfaces of the commons, in reading order. The nav dropdown on every page
 * of every trade links "the commons" as ONE destination, so without this rail a
 * reader who landed on the gear list had no way to discover the tips existed.
 * Adding a surface here puts it on every other surface at once. */
/* `data` and `rows` are not used by this file — they are here so the DEPLOY can
 * derive its per-surface coverage gate from the shipped engine instead of a
 * hand-written pair list in the workflow. A surface added here next month is
 * gated the day it lands, with no edit to the CI. */
window.COMMONS_SURFACES = [
  { href: "index.html", label: "What's in the bag",    data: "gear.js",  rows: "COMMONS_GEAR",  noun: "gear" },
  { href: "tips.html",  label: "Learned the hard way", data: "tips.js",  rows: "COMMONS_TIPS",  noun: "tips" },
  { href: "names.html", label: "Ask for it right",     data: "names.js", rows: "COMMONS_NAMES", noun: "name" }
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

  /* ---- THE FEEDBACK AREAS, DERIVED — never hand-listed again ---------------
   * Each surface used to spell this list out in its own <script> block. The
   * tenth trade shipped a toolkit on 2026-08-14, was added to COMMONS_TRADES so
   * it got its chip here, and was in NEITHER dropdown. feedback.js REQUIRES an
   * area for a bug or an improvement, so a concrete finisher could tick concrete
   * rows and then had exactly two ways to report one of them wrong: file it
   * against somebody else's trade, or close the box. Same rot as the framing
   * chip and the roofing rows, one layer out — a hand-written copy of a list
   * that already exists is a scar with a date on it. The deploy now refuses a
   * commons surface that hand-lists them. */
  function areas() {
    return TRADES.map(function (t) { return { v: t.slug, label: t.name }; });
  }

  /* ---- THE ALIAS INDEX — why the name table is not a glossary --------------
   *
   * names.js is the only data file here whose rows ARE words. Left as its own
   * page it would be a synonym list, and the panel that ranked it said exactly
   * what is wrong with that: this project has met the translation problem twice
   * and solved it both times as ROUTING INSIDE A TOOL — av/items.js writes its
   * asks in the receiver's vocabulary, shared/docspec.js carries `aka` so a man
   * finds his write-up by whatever his shop calls it — and a synonym that only
   * sits in a list does no work.
   *
   * So the names are not a page, they are an INDEX, and EVERY commons surface
   * searches through it. Type "marrette", "zap strap" or "stinger" into the gear
   * list and the right row comes up, though not one of those words appears
   * anywhere in gear.js. One file of words, every surface findable by them,
   * through the same shared/find.js the toolkit already measured on 5,384
   * queries.
   *
   * THE JOIN is by id first, then by the object's plain name — two data files
   * written a week apart will not agree on ids. Both sides fold the same way:
   * parentheticals dropped ("Diagonal cutters (dikes)"), anything after a comma
   * dropped ("Pipe wrenches, matched pair"), plurals folded. A symmetric fold
   * can only ever join two phrases that were already the same phrase. */
  function fold(s) {
    var base = String(s == null ? "" : s).replace(/\(.*?\)/g, " ").split(",")[0];
    /* The apostrophe is DELETED, not turned into a break: nobody types it. He
     * writes "plumbers tape" and the row says "plumber's tape" — split on the
     * apostrophe those are "plumber s tape" and "plumbers tape", which fold to
     * different things, and the second of the two objects that word names went
     * missing. Same for lineman's, painter's, plumber's. */
    var t = base.toLowerCase().replace(/['’]/g, "").replace(/[^a-z0-9]+/g, " ").replace(/^ +| +$/g, "");
    if (!t) return "";
    return t.split(" ").map(function (w) {
      return w.replace(/ies$/, "y").replace(/(ch|sh|s|x|z)es$/, "$1").replace(/([^s])s$/, "$1");
    }).join(" ");
  }

  /* Built on FIRST USE, never at load: this file is loaded before its data files
   * on every surface, so an index built here at evaluation time would be built
   * out of an empty window and would be silently, permanently empty. Mount runs
   * after the last <script>, which is the earliest honest moment. */
  var _aliases = null;
  function aliasMap() {
    if (_aliases) return _aliases;
    var map = {};
    (window.COMMONS_NAMES || []).forEach(function (r) {
      var words = (r.a || []).map(function (x) { return x.n; }).filter(Boolean);
      if (!words.length) return;
      [r.id, fold(r.n)].forEach(function (k) {
        if (k) map[k] = (map[k] || []).concat(words);
      });
    });
    _aliases = map;
    return map;
  }

  /* Every word the field says for this row's object, from any trade, deduped. */
  function akaOf(r) {
    var m = aliasMap();
    var all = (r.a || []).map(function (x) { return x.n; })
      .concat(m[r.id] || [], m[fold(r.n)] || []);
    var seen = {}, out = [];
    all.forEach(function (w) {
      var k = fold(w);
      if (!w || seen[k]) return;
      seen[k] = 1; out.push(w);
    });
    return out;
  }

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

    /* ---- the search: ONE box, EVERY trade, through the alias index ----------
     * The chip filter answers "what does my trade carry". The box answers the
     * other question, the one that has no home anywhere else on the site: "he
     * said a word at me and I do not know what he wants." So the box deliberately
     * IGNORES the chip and searches all ten trades — you heard the word from
     * somebody else, that is the whole reason you are typing it — and the section
     * says so out loud rather than letting the reader assume the filter applied.
     * Tapping a chip clears the box, because that is a man asking to browse. */
    var q = "", ix = null;
    if (window.Find && $("q")) {
      ix = window.Find.index(ROWS, [
        { get: function (r) { return r.n; },      w: 10, primary: true },
        { get: function (r) { return akaOf(r); }, w: 8 },
        /* The object clause and the why line DESCRIBE the row; they are not
           names for it. Rule 5 in find.js: a query that only reaches these is
           handed over as "Closest to", never as the thing he asked for. */
        { get: function (r) { return r.o || ""; }, w: 4, about: true },
        { get: function (r) { return r.w || ""; }, w: 3, about: true }
      ]);
    }

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
          clearQuery();
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

    /* find.js hands back WHICH KIND of answer it found, and its own contract says
     * the honest label is the caller's job. So the note never lets an approximate
     * result read as an exact one, and it names the words it threw away — a token
     * that matches nothing in the whole file is noise the reader added, and
     * silently deleting it is how a search box lies. */
    /* ---- THE HAND-OFF — found live, on the shipped page ---------------------
     * The alias index can only ever route to an object THIS surface carries, and
     * the gear list is tools: cable ties and wire connectors are consumables and
     * have no row on it. So "zap strap" dropped "zap" as noise, matched "strap"
     * somewhere by infix, came back at full coverage — and the page said
     * **"Matches: Wire strippers"** with total confidence to a man who asked for
     * cable ties. "marrette" was labelled honestly but answered with a permanent
     * marker. In both cases the commons KNOWS the word; the page he was standing
     * on just could not answer it.
     *
     * So when the name table knows the query and this surface has no row for it,
     * that goes at the TOP, above the surface's own guesses — and it never
     * suppresses a real hit, because it only fires when the joined row is absent
     * from the results. Routing in the other direction: the index sends the
     * reader to the page that can answer instead of guessing. */
    function handoff(hits) {
      if (cfg.surface === "names.html" || !window.Find) return null;
      var NAMES = window.COMMONS_NAMES || [];
      if (!NAMES.length) return null;
      if (!handoff.ix) {
        handoff.ix = window.Find.index(NAMES, [
          { get: function (r) { return r.n; }, w: 10, primary: true },
          { get: function (r) { return (r.a || []).map(function (x) { return x.n; }); }, w: 9 }
        ]);
      }
      /* AN EXACT WORD MAY BELONG TO MORE THAN ONE OBJECT, and on this page that
       * is not an edge case, it is the thesis. "mud ring" is a plaster ring to an
       * electrician and an open-back ring to a cabling tech; "plumber's tape" is
       * hanger strap to one man and PTFE to the next. Handing him ONE of them
       * silently picks a side, which is the same confident wrong answer this
       * hand-off exists to stop. So an exact hit on several rows returns all of
       * them and the page says the word is loaded. */
      var qf = fold(q), exact = [];
      NAMES.forEach(function (r) {
        var said = fold(r.n) === qf || (r.a || []).some(function (x) { return fold(x.n) === qf; });
        if (said) exact.push(r);
      });
      var rows = exact;
      if (!rows.length) {
        var f = window.Find.search(handoff.ix, q);
        if (f.mode === "none" || !f.hits.length) return null;   /* a guess is not a hand-off */
        rows = [f.hits[0]];
      }
      /* Suppress only when there is ONE thing it can mean and this page already
       * showed it. With a loaded word the suppression is the bug: "snake" is a
       * fish tape, a drum auger AND an audio snake, the gear list carries the
       * first two, and staying quiet tells a man who meant the third that he has
       * his answer. A partial answer to an ambiguous question is the same lie in
       * a smaller coat. */
      if (rows.length === 1) {
        var here = hits.some(function (g) {
          return g.id === rows[0].id || fold(g.n) === fold(rows[0].n);
        });
        if (here) return null;
      }
      return rows;
    }

    /* Who says the matching word for this row, so an ambiguous hand-off can say
       whose word it is rather than making him guess again. */
    function saidBy(row) {
      var qf = fold(q), hit = null;
      (row.a || []).forEach(function (x) { if (!hit && fold(x.n) === qf) hit = x; });
      return hit && hit.by ? hit.by : "";
    }

    function searchSections() {
      var r = window.Find.search(ix, q), note;
      if (r.mode === "none") {
        note = "Nothing on this page goes by that. The closest words here:";
      } else if (r.mode === "relaxed") {
        /* "relaxed" USED to mean only that some word of his did not land, so this
           line said so. Since 2026-08-25 it also covers a lead the engine had to
           REACH for — a typo it corrected, letters it found inside another word,
           a hit that is only in the prose — where every word did land and
           "nothing matched all of that" is simply false. One sentence has to be
           true of both, so it says what is true of both: nothing here is called
           this. The dropped words, when there are any, are named on the next line
           by their own sentence rather than smuggled into this one. */
        note = "Nothing here is called exactly that. Closest on what you typed:";
      } else {
        note = "Every trade searched, not just the one you picked — you heard it off somebody else.";
      }
      /* THE SENTENCE MOVED INTO shared/find.js (its §ADMITTING WHAT WAS THROWN
         AWAY). It shipped HERE first and then stayed here alone: the other 26
         surfaces loading the same engine dropped words in silence, 3,631 times
         over a cross-surface sweep. The four lines that stood here also got
         plural and repeated words wrong — neither of which this one surface's
         data ever produces, which is the whole argument against a copy per
         caller. Only worth saying when something DID match; the engine holds
         that rule now. */
      var drop = window.Find.dropped(r);
      if (drop) note += (note ? " " : "") + drop;
      var out = [];
      var send = handoff(r.hits);
      if (send && send.length === 1) {
        out.push({
          slug: "handoff",
          title: "He Means " + send[0].n,
          note: "Nothing on this page is called that — but the trades are, and “" + send[0].n +
                "” is the name to write down. The rest of the words for it are on the name table.",
          items: [],
          link: { href: "names.html", label: "Ask For It Right →" }
        });
      } else if (send) {
        var COUNT = ["", "", "Two", "Three", "Four", "Five"];
        out.push({
          slug: "handoff",
          title: (COUNT[send.length] || String(send.length)) + " Things Go By That",
          note: send.map(function (x) {
            var by = saidBy(x);
            return x.n + (by ? " to " + by : "");
          }).join("; ") + ". Different objects, same word — say which one you want.",
          items: [],
          link: { href: "names.html", label: "Ask For It Right →" }
        });
      }
      out.push({
        slug: "find",
        title: r.mode === "none" ? "Closest On This Page" : "Matches",
        note: note,
        items: r.hits
      });
      return out;
    }

    function render() {
      var host = $("sections");
      host.textContent = "";
      var secs = (q && ix) ? searchSections() : sectionsFor(view), total = 0;

      secs.forEach(function (s) {
        total += s.items.length;
        if (!s.items.length && !s.link) return;
        var sec = document.createElement("section");
        sec.className = "sec" + (s.link ? " sendon" : "");

        var head = document.createElement("div");
        head.className = "sechead";
        head.innerHTML = "<h2>" + esc(s.title) + "</h2>" +
                         (s.link ? "" : '<span class="count">' + s.items.length + " " + esc(cfg.countNoun) + "</span>");
        sec.appendChild(head);

        var note = document.createElement("p");
        note.className = "secnote";
        note.textContent = s.note;
        sec.appendChild(note);

        if (s.link) {
          var a = document.createElement("a");
          a.className = "btn";
          a.href = s.link.href;
          a.textContent = s.link.label;
          sec.appendChild(a);
        }

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
      /* A surface owns what sits under its own name — gear and tips are a name
       * and a reason, the name table is a name and every other name for it. The
       * escaper is handed over rather than re-implemented per surface. */
      var eye  = cfg.eyebrow ? cfg.eyebrow(g) : "";
      var body = cfg.body ? cfg.body(g, esc) : '<p class="why">' + esc(g.w) + "</p>";
      txt.innerHTML = (eye ? '<div class="nmeye">' + esc(eye) + "</div>" : "") +
                      '<div class="nm">' + esc(g.n) + "</div>" +
                      body +
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

    function clearQuery() {
      var box = $("q"), x = $("qx");
      q = "";
      if (box) box.value = "";
      if (x) x.hidden = true;
    }

    var qbox = $("q"), qx = $("qx");
    if (qbox && ix) {
      qbox.addEventListener("input", function () {
        q = qbox.value;
        if (qx) qx.hidden = !q;
        render();
      });
      /* A search box on a phone gets a submit, and the default is a page reload
       * that throws the query away. */
      qbox.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); qbox.blur(); }
      });
      if (qx) qx.addEventListener("click", function () {
        clearQuery(); qbox.focus(); render();
      });
    } else if (qbox) {
      /* find.js did not load. A dead box that eats what a man types is worse
       * than no box, so it removes itself rather than pretending. */
      var bar = qbox.parentNode;
      if (bar && bar.parentNode) bar.parentNode.removeChild(bar);
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

  return { mount: mount, areas: areas, aka: akaOf };
})();
