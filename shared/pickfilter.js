/* FIELD TOOLKIT — SHARED: NARROW A TAP-TO-PICK LIST.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHAT WAS MEASURED BEFORE THIS FILE WAS WRITTEN. Seven pages in this toolkit
 * are shape #1 — a long tap-to-tick list that becomes a request you send. Their
 * item counts, read off `items.js` on disk rather than guessed:
 *
 *     concrete/mix-order.html            151 items / 12 categories
 *     av/cable-list.html                  62 /  9
 *     framing/the-load.html               44 /  9
 *     electrical/pull-list.html           42 /  8
 *     hvac/truck-stock.html               37 /  8
 *     low-voltage/consumables.html        35 /  8
 *     plumbing/supply-house-order.html    53 (fork)
 *
 * Not one of them had any way to narrow that list. The ONE page that did —
 * av/consumables.html, which grew a `shared/find.js` filter the cycle before —
 * is the SMALLEST list on the board at 28 items. The refinement landed on the
 * page that needed it least and never reached the six that needed it most.
 *
 * TWO DOORS, BECAUSE A CREW ARRIVES BY TWO ROADS. A concrete finisher read
 * these pages before this was built and drew the line exactly: on a parts list
 * he already knows the word — "RJ45", "wall dogs", "cable ties" — and typing it
 * is the fastest thing on the page. On a list he reads to REMEMBER ("I don't
 * know I need a washout tub until I read it") he has nothing to type, and his
 * friction is different: the categories are boxed to look like folders, none of
 * them folds, so every trip down the page scrolls past six sections he already
 * handled to reach the seventh. His own ask, verbatim: skip the scroll, don't
 * page past nine sections to get to the tenth.
 *
 * So this is ONE job — narrow the list — with two ways in:
 *   · TYPE IT   — shared/find.js, for the man who knows the word.
 *   · TAP IT    — one category, for the man who knows the aisle.
 * They compose (a category, then a word inside it) because they are the same
 * hide/show pass, and a picker that supported only one of them would still be
 * making half the crew scroll.
 *
 * THE CATEGORY CONTROL IS A <select>, NOT CHIPS. Chips were the shape asked
 * for and they are wrong here: `concrete/items.js` names its categories in
 * prose — "The walk before the mud rolls", "What the plant and the pumper have
 * to know about the site" — and twelve of those as chips is a wall of text
 * where the list used to be. A native select is one 44px control at any name
 * length, and on a phone it opens the OS picker, which is the best one-handed
 * list control either platform ships.
 *
 * "TICKING BEATS TYPING" IS NOT VIOLATED, and the man who owns that rail said
 * so himself: it forbids answering a tap-shaped job with a form. Nothing here
 * is required. Scroll and tap still works exactly as it did; this is a jog for
 * people in a hurry, and it only breaks the rail if typing becomes the only
 * door in. It is not.
 *
 * CHECK SHOWN ONLY EXISTS WHILE THE LIST IS NARROWED. On the flagship it is
 * always on screen, and with an empty box "shown" means ALL OF THEM — one fat
 * thumb beside the search bar ticks 28 lines today and would tick 151 here.
 * Graded a bug, not a nice-to-have, by the same finisher. The button appears
 * when a filter is actually holding rows back and is gone otherwise, which is
 * also the first time its label is true.
 *
 * THE HONEST LABEL IS THE CALLER'S UI (shared/find.js §WHAT THE CALLER OWNS).
 * An approximate answer always SAYS it is approximate — "Closest to …",
 * "Nothing matched that — closest three" — and a filter never dead-ends, so
 * "no items match" is not a state this can reach.
 *
 * THE WRITE-IN SECTION IS NEVER HIDDEN. It is where a man goes when the list
 * does not have his thing, which is exactly the moment a filter is narrowing
 * hardest. (The flagship hid it: add one write-in, filter for anything else,
 * and the section — Add box and all — vanished, because it had items and none
 * of them matched. Fixed here for everyone that mounts this.)
 *
 * HOW YOU ADD IT — the engine does it for you. `shared/checklist-request.js`
 * mounts this itself unless a tool passes `filter: false`. A fork mounts it
 * directly and may ADOPT its own controls instead of letting this render them:
 *
 *   PickFilter.mount({ list: "list" });                       // renders its own bar
 *   PickFilter.mount({ list: "list", input: "q",              // adopts existing markup
 *                      label: "nomatch", check: "checkShown" });
 *
 * Load AFTER shared/find.js. No other dependency, ES5, no network. Styles live
 * in shared/pickfilter.css — link it on any page that lets this render the bar.
 */
(function () {
  "use strict";

  function byId(x) { return typeof x === "string" ? document.getElementById(x) : (x || null); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }
  function arr(nl) { return [].slice.call(nl); }

  /* A section that hosts the "not in the list" escape hatch, or that a tool has
   * marked, is structural — it is never hidden by a filter. */
  var KEEP_DEFAULT = ".addrow, .addbar, .wi-add, [data-keep]";

  function mount(cfg) {
    cfg = cfg || {};
    var list = byId(cfg.list);
    if (!list) return null;
    /* No search engine on the page means no filter — the page behaves exactly as
     * it did before this file existed rather than half-working. */
    if (!window.Find) return null;

    var itemSel = cfg.itemSel || ".item";
    var catSel = cfg.catSel || ".cat";
    var hid = cfg.hiddenClass || "is-hidden";
    var keepSel = cfg.keepSel || KEEP_DEFAULT;

    var input = byId(cfg.input);
    var label = byId(cfg.label);
    var check = cfg.check === false ? null : byId(cfg.check);
    var sel = byId(cfg.cats);
    var rendered = false;

    /* ── the bar, when the page did not bring its own ─────────────────────── */
    if (!input) {
      var cats = arr(list.querySelectorAll(catSel)).filter(function (c) {
        return c.querySelectorAll(itemSel).length > 0 && !c.querySelector(keepSel);
      });
      var bar = document.createElement("div");
      bar.className = "pf-bar";
      bar.innerHTML =
        '<div class="pf-search">'
        + '<input class="pf-q" type="search" autocomplete="off" spellcheck="false" '
        + 'placeholder="' + esc(cfg.placeholder || "Filter the list") + '" '
        + 'aria-label="' + esc(cfg.placeholder || "Filter the list") + '"></div>'
        /* The category door is only worth a control when there is something to
         * choose between. Under four sections you can see them all anyway. */
        + (cats.length >= 4
          ? '<select class="pf-cat" aria-label="Show one section"><option value="">'
            + esc(cfg.allLabel || "The whole list") + "</option>"
            + cats.map(function (c) {
                var h = c.querySelector("h2, summary, h3");
                var name = h ? (h.getAttribute("data-name") || h.textContent) : c.getAttribute("data-id");
                return '<option value="' + esc(c.getAttribute("data-id") || "") + '">'
                  + esc(String(name).replace(/\s+/g, " ").trim()) + "</option>";
              }).join("")
            + "</select>"
          : "")
        /* Visibility is an inline style, not the `hidden` attribute: a page that
         * ADOPTS its own button has a class on it, and a class beats [hidden]. */
        + '<button type="button" class="pf-check" style="display:none">'
        + esc(cfg.checkLabel || "Check shown") + "</button>";
      list.parentNode.insertBefore(bar, list);
      input = bar.querySelector(".pf-q");
      sel = bar.querySelector(".pf-cat");
      check = cfg.check === false ? null : bar.querySelector(".pf-check");
      rendered = true;
    }
    if (!label) {
      label = document.createElement("p");
      label.className = "pf-none";
      label.setAttribute("aria-live", "polite");
      label.style.display = "none";
      list.parentNode.insertBefore(label, list.nextSibling);
    } else {
      label.setAttribute("aria-live", "polite");
    }
    /* THIS LABEL QUOTES WHAT HE TYPED BACK AT HIM, so he decides how long its
       longest word is. Set here rather than in pickfilter.css because half these
       pages ADOPT their own #nomatch and never load that file — a 54-character
       token pushed hvac/truck-stock 257px sideways at 320px wide, which is the
       mobile law, not a nicety. */
    label.style.overflowWrap = "anywhere";

    function items() { return arr(list.querySelectorAll(itemSel)); }

    /* ── the one pass everything goes through ─────────────────────────────── */
    var mode = "all", drop = "";
    function apply() {
      var q = (input.value || "").trim();
      var pick = sel ? sel.value : "";
      var all = items();

      /* The category door first: it is a hard restriction, not a ranking. */
      var pool = !pick ? all : all.filter(function (el) {
        var c = el.closest ? el.closest(catSel) : null;
        return c && c.getAttribute("data-id") === pick;
      });

      var show;
      drop = "";
      if (!q) {
        show = pool; mode = pick ? "cat" : "all";
      } else {
        /* Indexed off the DOM and rebuilt per keystroke, not off the data —
         * write-ins and removed rows stay honest that way. */
        /* THE RAW VALUE, NOT THE TRIMMED ONE, and the difference is one character
               that decides a sentence. `norm()` strips trailing separators, so this
               changes NOTHING about what matches — but shared/find.js reads the raw
               query to tell "he is still typing this word" from "he finished it", and
               a trimmed query can never say the second. Trimmed stays the display
               value, because a heading that quotes his trailing space is a typo. */
        var res = window.Find.search(
          window.Find.index(pool.map(function (el) { return { el: el }; }),
            [{ get: function (r) { return r.el.textContent; }, w: 1, primary: true }]), input.value);
        mode = res.mode === "all" ? (pick ? "cat" : "all") : res.mode;
        drop = window.Find.dropped(res);
        show = res.hits.map(function (r) { return r.el; });
      }

      /* Marked rather than searched: a 151-item list re-filtered on every
       * keystroke should not cost 151² comparisons to paint. */
      for (var i = 0; i < show.length; i++) show[i].__pfOn = 1;
      for (i = 0; i < all.length; i++) {
        all[i].classList.toggle(hid, !all[i].__pfOn);
        all[i].__pfOn = 0;
      }

      /* A section with nothing left in it is noise — unless it is the write-in
       * escape hatch, which is exactly where a hard filter sends people. */
      arr(list.querySelectorAll(catSel)).forEach(function (c) {
        if (c.querySelector(keepSel)) { c.classList.remove(hid); return; }
        var its = c.querySelectorAll(itemSel);
        var vis = arr(its).some(function (x) { return !x.classList.contains(hid); });
        c.classList.toggle(hid, its.length > 0 && !vis);
      });

      var narrowed = mode !== "all";
      if (check) check.style.display = narrowed ? "" : "none";
      /* THE THIRD REASON THIS LABEL EXISTS. It was built to say "closest" and
         "nothing matched", and it was HIDDEN for the case that needed it most:
         every word landed, the list narrowed, and one of his words had been
         deleted on the way. On a parts list that word is normally the part —
         type "3/4 EMT strap" where nothing is called EMT and you are looking at
         straps, filtered, with nothing on screen saying so. The engine owns the
         sentence (shared/find.js §ADMITTING WHAT WAS THROWN AWAY); this decides
         only whether it rides alone or after one of the other two. */
      var head = mode === "none"
        ? "Nothing matched that — closest three shown."
        : (mode === "relaxed" ? "Closest to “" + q + "” shown." : "");
      label.textContent = head + (head && drop ? " " : "") + drop;
      label.style.display = label.textContent ? "block" : "none";

      /* `show` is the set that survived the filter — an undeclared `on` sat here
         and would have thrown a ReferenceError the first time any page passed an
         onChange, which no page does yet, which is exactly why it went unseen. */
      if (cfg.onChange) cfg.onChange({ mode: mode, narrowed: narrowed, shown: show.length, total: all.length });
    }

    input.addEventListener("input", apply);
    input.addEventListener("search", apply);          // the native × in a type=search
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && input.value) { e.preventDefault(); input.value = ""; apply(); }
    });
    if (sel) sel.addEventListener("change", apply);
    if (check) {
      check.addEventListener("click", function () {
        /* Ticked HERE rather than by dispatching a change per row: a delegated
         * handler would re-render the whole list 151 times for one tap. The rows
         * are handed back instead, so the caller runs its per-tick hook and
         * re-renders ONCE. (The two live mass-tick controls in this toolkit both
         * set .checked directly and fire nothing at all, which silently defeats
         * shared/checklist-request.js's documented onTick stamp.) */
        var done = [];
        items().forEach(function (el) {
          if (el.classList.contains(hid)) return;
          var t = el.querySelector(".tick");
          if (!t || t.checked) return;
          t.checked = true;
          el.classList.add("is-checked");
          done.push(el);
        });
        if (cfg.onCheckShown) cfg.onCheckShown(done);
      });
    }

    apply();

    return {
      apply: apply,
      narrowed: function () { return mode !== "all"; },
      /* Used by Clear: a wiped list must not stay filtered down to three rows. */
      reset: function () { input.value = ""; if (sel) sel.value = ""; apply(); },
      rendered: rendered
    };
  }

  window.PickFilter = { mount: mount };
})();
