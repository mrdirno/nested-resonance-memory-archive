/* FIELD TOOLKIT — SHAPE #1 ENGINE: CHECKLIST → A REQUEST.
 *
 * av/AV_SOCIETY.md §THE THREE SHAPES: "When you build the second instance of a
 * shape, extract the engine. Two instances is where a shape is provable; one is
 * over-abstraction and five is five forks."
 *
 * Shape #1 had TWO live instances — av/consumables.html and
 * plumbing/supply-house-order.html — built as independent files that had
 * nonetheless converged on the same seven functions (itemHTML · refresh · asText ·
 * lineText · addWriteIn · flash · copy-with-fallback). That convergence IS the
 * proof the shape is real, and the debt the doctrine names. This file is that
 * engine, extracted at the point where a third and fourth instance were about to
 * be forked.
 *
 * WHAT VARIES PER TOOL, and therefore what the caller owns:
 *   · the ITEM DATA (categories, items) — a trade's vocabulary, never the engine's
 *   · the MODIFIER AXES per item — AV consumables have none, plumbing has
 *     size + config + unit, cables have type + length + ends. So axes are a LIST
 *     the item declares, not three hardcoded selects.
 *   · the LINE and DOCUMENT text — how a line reads to a counter is not how it
 *     reads to an electrician. The engine assembles state; the caller writes words.
 *   · the CSS — every page keeps its own <style> and its own palette. The engine
 *     emits the SAME class vocabulary both live pages already use (.cat/.item/
 *     .cfg/.f/.tick/.i-qty/.i-note/.addrow), so adopting it is a no-op visually.
 *
 * WHAT THE ENGINE OWNS (the parts that were duplicated and drift when forked):
 *   tick/expand state · per-category counts · qty+note plumbing · write-in rows ·
 *   live preview · the count line · clear · copy WITH the non-secure-context
 *   fallback (a job-site browser may not give a secure context, and failing
 *   silently there is the whole product broken) · the self-aware date · re-render
 *   on the shared runtime's av:ready.
 *
 * NOT here, deliberately: any computed quantity, size, rating or equivalence.
 * The user states the numbers; the engine only makes sure they arrive with their
 * units attached (av/AV_SOCIETY.md §SAFETY).
 *
 * Load AFTER the trade config and registry, alongside the shared runtime:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/checklist-request.js"></script>
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }
  function opts(a, sel) {
    return (a || []).map(function (o) {
      return '<option' + (o === sel ? " selected" : "") + ">" + esc(o) + "</option>";
    }).join("");
  }
  function byId(x) { return typeof x === "string" ? document.getElementById(x) : x; }

  /* What a fresh Qty box starts at. "1" is right for a picker line — ticking it
   * means at least one. It is WRONG for a pasted write-in, whose text usually
   * carries its own count ("500' #12 THHN blue"), where a leading 1 prints a line
   * that contradicts itself. So the item def may override the tool, and the tool
   * may override the engine. */
  function qtyDefault(it, cfg) {
    if (it && it.qtyDefault != null) return it.qtyDefault;
    if (cfg && cfg.qtyDefault != null) return cfg.qtyDefault;
    return "1";
  }

  /* The date is self-aware — the shared runtime resolves the real date from public
   * sources, because a phone or job-site tablet clock can be flat wrong. */
  function todayStr() {
    return (window.Toolkit && window.Toolkit.todayStr)
      ? window.Toolkit.todayStr()
      : new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  /* Copy that survives a job site: the async Clipboard API needs a secure context,
   * so fall back to a real, visible selection rather than failing silently. */
  function copyText(t, btn, onFlash) {
    function flash(msg) {
      if (onFlash) return onFlash(msg);
      if (!btn) return;
      var was = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", was);
      btn.textContent = msg;
      setTimeout(function () { btn.textContent = was; }, 1600);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = t;
      ta.style.cssText = "position:fixed;left:8px;bottom:70px;width:calc(100% - 16px);height:38vh;z-index:99";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      if (ok) { ta.remove(); flash("Copied"); }
      else { flash("Copy it manually"); ta.addEventListener("blur", function () { ta.remove(); }); }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { flash("Copied"); }, fallback);
    } else { fallback(); }
  }

  /* ── one item row: the tick, and the modifier strip that only appears once the
   * line is actually ON the list (an unticked line shows no controls at all —
   * that is what keeps a 60-item page readable on a phone). ─────────────────── */
  function itemHTML(it, cfg, removable) {
    var ax = (it.ax || []).map(function (a) {
      var cls = "f" + (a.wide ? " wide" : "");
      return '<div class="' + cls + '"><label>' + esc(a.label) + "</label>"
        + '<select class="i-ax" data-k="' + esc(a.k) + '">' + opts(a.opts, a.def) + "</select></div>";
    }).join("");
    var flags = (it.flags || []).length
      ? '<div class="f flags" style="flex:1 1 100%">' + it.flags.map(function (f) {
          // A `fixed` flag is a QUESTION the tool refuses to let you switch off —
          // the post-tension-deck scan ask is the example. It prints every time.
          return '<label class="flag' + (f.fixed ? " fixed" : "") + '"><input type="checkbox" class="i-flag" data-k="'
            + esc(f.k) + '"' + (f.def ? " checked" : "") + (f.fixed ? " disabled" : "")
            + "><span>" + esc(f.label) + "</span></label>";
        }).join("") + "</div>"
      : "";
    /* QTY IS A NUMBER FOR SOME TRADES AND A PHRASE FOR OTHERS. A number spinner is
     * right for "4 HDMI cables". It is wrong for a trade that orders in mixed
     * units on the same list — an electrician's own words for this were "make Qty
     * a FREE TEXT field so I can type '2 bx', '500 ft', 'a case'; the number input
     * with min=1 step=1 is a desk person's idea". Opt-in per tool, so no page that
     * already ships changes behaviour. */
    var qty = it.noQty ? "" :
      '<div class="f qty"><label>Qty</label>'
      // data-def carries the row's own default so readLine can fall back to IT
      // rather than to a hardcoded "1". A hardcoded fallback silently resurrected
      // the 1 on every pasted write-in line whose text already said "500'".
      + (cfg.qtyText
        ? '<input class="i-qty" type="text" data-def="' + esc(qtyDefault(it, cfg)) + '" value="' + esc(qtyDefault(it, cfg)) + '" autocomplete="off" spellcheck="false">'
        : '<input class="i-qty" type="number" inputmode="numeric" min="1" step="1" data-def="' + esc(qtyDefault(it, cfg)) + '" value="' + esc(qtyDefault(it, cfg)) + '">')
      + "</div>";
    var note = (it.note === false) ? "" :
      '<div class="f" style="flex:1 1 100%"><input class="i-note note" type="text" placeholder="'
      + esc(it.notePlaceholder || cfg.notePlaceholder || "Note — anything odd about this one") + '" autocomplete="off"></div>';
    // THE CLONE. The normal case for a cable order is the SAME item at two or three
    // lengths ("4× HDMI 15 ft AND 2× HDMI 6 ft"). One config strip per line cannot
    // express that, so the tech abandons the tool and types it — the shape fails its
    // own gate on its most common use. One tap fixes it.
    var clone = cfg.cloneLabel
      ? '<button type="button" class="clonebtn">' + esc(cfg.cloneLabel) + "</button>"
      : "";
    return '<li class="item">'
      + '<label class="row"><input type="checkbox" class="tick"><span class="name">' + esc(it.n) + "</span>"
      + (it.sub ? '<span class="sub">' + esc(it.sub) + "</span>" : "")
      + (removable ? '<button type="button" class="rm" title="Remove">&times;</button>' : "")
      + "</label>"
      + '<div class="cfg">' + qty + ax + flags + note + clone + "</div></li>";
  }

  /* ── read one ticked <li> back into a plain object the caller can format ───── */
  function readLine(li) {
    var axv = {}, fl = {};
    [].forEach.call(li.querySelectorAll(".i-ax"), function (s) { axv[s.getAttribute("data-k")] = s.value; });
    // A disabled checkbox still reports .checked, which is exactly what a `fixed`
    // flag needs — the question prints whether or not anyone could have unticked it.
    [].forEach.call(li.querySelectorAll(".i-flag"), function (c) { fl[c.getAttribute("data-k")] = c.checked; });
    var q = li.querySelector(".i-qty");
    var n = li.querySelector(".i-note");
    return {
      name: li.querySelector(".name").textContent,
      qty: q ? (q.value.trim() || (q.getAttribute("data-def") || "")) : "",
      note: n ? n.value.trim() : "",
      ax: axv,
      flags: fl,
      el: li
    };
  }

  /* Copy the LIVE values across, not the markup. cloneNode carries the `selected`
   * and `checked` ATTRIBUTES (i.e. the defaults), never what the user actually
   * picked — so a naive cloneNode silently resets every axis to its first option. */
  function copyValues(from, to) {
    var fs = from.querySelectorAll(".i-ax"), ts = to.querySelectorAll(".i-ax");
    for (var i = 0; i < fs.length && i < ts.length; i++) ts[i].value = fs[i].value;
    var ff = from.querySelectorAll(".i-flag"), tf = to.querySelectorAll(".i-flag");
    for (var j = 0; j < ff.length && j < tf.length; j++) tf[j].checked = ff[j].checked;
    var fn = from.querySelector(".i-note"), tn = to.querySelector(".i-note");
    if (fn && tn) tn.value = fn.value;
  }

  function mount(cfg) {
    var list = byId(cfg.list);
    if (!list) throw new Error("checklist-request: no list element");
    var preview = byId(cfg.preview);
    var countEl = byId(cfg.count);
    var copyBtn = byId(cfg.copy);
    var clearBtn = byId(cfg.clear);
    var data = cfg.data || [];

    // Every <li> remembers the item definition it was rendered from, so a clone is
    // rebuilt from the DEF (correct markup, correct axes) and then given the live
    // values — never cloneNode'd, which would reset every select to its default.
    var defOf = new WeakMap();

    list.innerHTML = data.map(function (cat) {
      return '<section class="cat" data-id="' + esc(cat.id) + '" style="--chip:' + esc(cat.chip || "#5D656E") + '">'
        + "<h2>" + esc(cat.name) + '<span class="n" data-n></span></h2>'
        + (cat.hint ? '<p class="cathint">' + esc(cat.hint) + "</p>" : "")
        + '<ul class="items">' + (cat.items || []).map(function (i) { return itemHTML(i, cfg, false); }).join("") + "</ul>"
        + (cat.writein
          ? '<div class="addrow">'
            /* A ONE-LINE INPUT CANNOT TAKE A PASTED LIST. Browsers flatten a
             * multi-line paste into an <input>, so "paste your whole list, one per
             * line" — which is how a foreman already keeps it, in his notes app —
             * silently arrives as one run-on row. Opt in to a textarea and each
             * line becomes its own row. Enter then means newline, so Add is the
             * button (or ⌘/Ctrl+Enter). */
            + (cfg.writeinTextarea
              ? '<textarea class="wi-input" rows="2" spellcheck="false" placeholder="'
                + esc(cfg.writeinPlaceholder || "Anything else — type it and hit Add") + '"></textarea>'
              : '<input class="wi-input" type="text" placeholder="'
                + esc(cfg.writeinPlaceholder || "Anything else — type it and hit Add") + '" autocomplete="off">')
            + '<button type="button" class="addbtn wi-add">Add</button></div>'
          : "")
        + "</section>";
    }).join("");

    // Bind each rendered <li> back to its definition (same order as rendered).
    data.forEach(function (cat) {
      var lis = list.querySelectorAll('.cat[data-id="' + cat.id + '"] > ul.items > li.item');
      (cat.items || []).forEach(function (it, i) { if (lis[i]) defOf.set(lis[i], it); });
    });

    /* ── write-ins: same row shape, same axes as a normal line, removable ───── */
    var wiSection = list.querySelector(".cat .wi-add") ? list.querySelector(".wi-add").closest(".cat") : null;
    if (wiSection) {
      var wiUL = wiSection.querySelector("ul.items");
      var wiInput = wiSection.querySelector(".wi-input");
      var addWriteIn = function () {
        var raw = wiInput.value;
        // One row per line when the caller opted into the textarea; otherwise the
        // whole value is one row exactly as before.
        var vals = (cfg.writeinTextarea ? raw.split(/\r?\n/) : [raw])
          .map(function (s) { return s.trim(); })
          .filter(function (s) { return s.length; });
        if (!vals.length) { wiInput.focus(); return; }
        vals.forEach(function (v) {
          var wiDef = { n: v, ax: cfg.writeinAx || [], flags: cfg.writeinFlags || [],
                        qtyDefault: cfg.writeinQtyDefault };
          wiUL.insertAdjacentHTML("beforeend", itemHTML(wiDef, cfg, true));
          var li = wiUL.lastElementChild;
          defOf.set(li, wiDef);
          li.querySelector(".tick").checked = true;
          li.classList.add("is-checked");
        });
        wiInput.value = ""; wiInput.focus(); refresh();
      };
      wiSection.querySelector(".wi-add").addEventListener("click", addWriteIn);
      wiInput.addEventListener("keydown", function (e) {
        if (e.key !== "Enter") return;
        // In a textarea Enter is a NEWLINE — that is the whole point of the
        // multi-line box. ⌘/Ctrl+Enter is the commit.
        if (cfg.writeinTextarea && !(e.metaKey || e.ctrlKey)) return;
        e.preventDefault(); addWriteIn();
      });
    }

    /* ── segmented header controls: <div class="seg" id="x"><button data-v=…> ── */
    var segState = {};
    (cfg.segments || []).forEach(function (s) {
      var el = byId(s.id);
      if (!el) return;
      var initial = el.querySelector("button.on");
      segState[s.key] = s.def || (initial ? initial.getAttribute("data-v") : "");
      el.addEventListener("click", function (e) {
        var b = e.target.closest("button");
        if (!b) return;
        [].forEach.call(el.querySelectorAll("button"), function (x) { x.classList.toggle("on", x === b); });
        segState[s.key] = b.getAttribute("data-v");
        if (s.onChange) s.onChange(segState[s.key]);
        refresh();
      });
    });

    /* ── live state ───────────────────────────────────────────────────────── */
    list.addEventListener("change", function (e) {
      if (e.target.classList.contains("tick")) {
        var li = e.target.closest(".item");
        li.classList.toggle("is-checked", e.target.checked);
        // A shape that stamps each line with WHERE it applies needs the stamp to
        // land the moment the line is ticked — retyping the room on every line is
        // the friction the tool exists to delete.
        if (cfg.onTick) cfg.onTick(li, e.target.checked);
      }
      refresh();
    });
    list.addEventListener("input", refresh);
    list.addEventListener("click", function (e) {
      var b = e.target.closest(".rm");
      if (b) { e.preventDefault(); b.closest(".item").remove(); refresh(); return; }
      var c = e.target.closest(".clonebtn");
      if (c) {
        e.preventDefault();
        var src = c.closest(".item");
        var def = defOf.get(src) || { n: src.querySelector(".name").textContent, ax: [] };
        src.insertAdjacentHTML("afterend", itemHTML(def, cfg, true));
        var dup = src.nextElementSibling;
        defOf.set(dup, def);
        copyValues(src, dup);
        dup.querySelector(".tick").checked = true;
        dup.classList.add("is-checked");
        var qi = dup.querySelector(".i-qty");
        if (qi) { qi.value = qtyDefault(def, cfg); }
        refresh();
        // Land the thumb on the axis the clone exists to change (the first one).
        var first = dup.querySelector(".i-ax");
        if (first) first.focus();
      }
    });
    (cfg.watch || []).forEach(function (id) {
      var el = byId(id);
      if (el) el.addEventListener("input", refresh);
    });

    function sections() {
      return data.map(function (cat) {
        var sec = list.querySelector('.cat[data-id="' + cat.id + '"]');
        var on = [].slice.call(sec.querySelectorAll(".item.is-checked"));
        // docName lets a section read one way on screen and another in the sent
        // document. The write-in section's heading is a PROMPT ("What do you
        // need?") — printing that as a heading in a message to the warehouse is
        // the tool talking to the wrong person.
        return { id: cat.id, name: cat.name, docName: cat.docName || cat.name, lines: on.map(readLine) };
      }).filter(function (s) { return s.lines.length; });
    }
    function tickedCount() { return list.querySelectorAll(".item.is-checked").length; }

    function text() {
      var secs = sections();
      return cfg.document({
        sections: secs,
        count: tickedCount(),
        seg: segState,
        today: todayStr(),
        line: cfg.line
      });
    }

    function refresh() {
      data.forEach(function (cat) {
        var sec = list.querySelector('.cat[data-id="' + cat.id + '"]');
        var n = sec.querySelectorAll(".item.is-checked").length;
        sec.querySelector("[data-n]").textContent = n ? n : "";
      });
      var n = tickedCount();
      if (countEl) {
        countEl.textContent = cfg.countLabel
          ? cfg.countLabel(n)
          : (n ? n + " line" + (n === 1 ? "" : "s") + " on the list" : "Nothing on the list yet");
      }
      if (preview) preview.textContent = text();
      if (cfg.onRefresh) cfg.onRefresh(n);
      schedulePersist();
    }

    /* ── PERSISTENCE ───────────────────────────────────────────────────────────
     * These are WALK-DURATION tools: a lead ticks lines room by room over twenty
     * minutes, phone in one hand. iOS will evict a background tab in that window,
     * and a tool that loses the walk is worse than the paper it replaced. So the
     * ticked state is written on every change and restored on load.
     *
     * Serialized by (category, item NAME, occurrence) rather than by DOM index,
     * because clones and write-ins shift indices — a restore keyed on position
     * silently reassigns a tech's values to the wrong line. On restore, a name with
     * no free row left is REBUILT (that is what a clone is), and a name that is not
     * in the category at all comes back as a write-in. */
    var persistTimer = null;
    function persist() {
      if (!cfg.persistKey) return;
      var payload = { v: 1, cats: {}, extra: cfg.persistExtra ? cfg.persistExtra() : null };
      data.forEach(function (cat) {
        var sec = list.querySelector('.cat[data-id="' + cat.id + '"]');
        var rows = [].slice.call(sec.querySelectorAll(".item.is-checked")).map(function (li) {
          var l = readLine(li);
          return { n: l.name, qty: l.qty, ax: l.ax, flags: l.flags, note: l.note };
        });
        if (rows.length) payload.cats[cat.id] = rows;
      });
      try {
        if (Object.keys(payload.cats).length || payload.extra) {
          localStorage.setItem(cfg.persistKey, JSON.stringify(payload));
        } else {
          localStorage.removeItem(cfg.persistKey);
        }
      } catch (e) {}
    }
    function schedulePersist() {
      if (!cfg.persistKey) return;
      clearTimeout(persistTimer);
      persistTimer = setTimeout(persist, 250);
    }

    /* A 250 ms DEBOUNCE IS NOT A SAVE (§SCARS "the camera round-trip eats the
     * draft", 2026-08-04). iOS backgrounds the tab the instant a man leaves for
     * the camera, a phone call, or the next app — and a timer that has not fired
     * yet dies with it, silently, taking the walk he just did. That scar was
     * found and fixed on ONE page (hvac/repair-recommendation.html) and left
     * every checklist tool on three other trades still debounce-only: fixing it
     * in the engine fixes every page the engine drives at once — which is the
     * whole reason the engine exists.
     *
     * WHAT THAT SENTENCE USED TO CLAIM, and it was false for weeks: "this engine
     * drives av/consumables, av/cable-list, plumbing/supply-house-order and
     * electrical/pull-list." It drives cable-list and pull-list. It has NEVER
     * driven either of the two pages it was extracted FROM — they stayed forks,
     * with no save at all, and this comment is why nobody noticed. A file that
     * describes a coverage it does not have is worse than a file with no comment:
     * it answers the audit question before the audit reaches the disk. Their
     * persistence now comes from shared/draft.js; the fork itself is still owed.
     * Flush SYNCHRONOUSLY on the three events that actually precede an eviction.
     * `visibilitychange` is the one that fires on iOS; `pagehide` covers a real
     * navigation; `blur` covers focus leaving to another app on desktop. */
    function flushPersist() {
      if (!cfg.persistKey) return;
      clearTimeout(persistTimer);
      // Defensive: a flush can arrive before the first render (a tab backgrounded
      // during load). Losing the write is correct there; throwing is not.
      try { persist(); } catch (e) {}
    }
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flushPersist();
    });
    window.addEventListener("pagehide", flushPersist);
    window.addEventListener("blur", flushPersist);

    function applyValues(li, row) {
      [].forEach.call(li.querySelectorAll(".i-ax"), function (s) {
        var v = row.ax ? row.ax[s.getAttribute("data-k")] : null;
        if (v == null) return;
        // An option the user picked before may not exist in this render (a room
        // that has not been re-added yet). Carry it anyway rather than drop it.
        if (![].some.call(s.options, function (o) { return o.value === v; })) {
          s.appendChild(h_option(v));
        }
        s.value = v;
      });
      [].forEach.call(li.querySelectorAll(".i-flag"), function (c) {
        var v = row.flags ? row.flags[c.getAttribute("data-k")] : null;
        if (v != null && !c.disabled) c.checked = !!v;
      });
      var q = li.querySelector(".i-qty");
      if (q && row.qty) q.value = row.qty;
      var n = li.querySelector(".i-note");
      if (n && row.note) n.value = row.note;
      li.querySelector(".tick").checked = true;
      li.classList.add("is-checked");
    }
    function h_option(v) {
      var o = document.createElement("option");
      o.value = v; o.textContent = v;
      return o;
    }

    function restore(key) {
      if (!cfg.persistKey) return false;
      var raw = null;
      try { raw = localStorage.getItem(key || cfg.persistKey); } catch (e) { return false; }
      if (!raw) return false;
      var p;
      try { p = JSON.parse(raw); } catch (e) { return false; }
      if (!p || !p.cats) return false;
      if (cfg.onRestoreExtra && p.extra) cfg.onRestoreExtra(p.extra);
      var any = false;
      data.forEach(function (cat) {
        var rows = p.cats[cat.id];
        if (!rows || !rows.length) return;
        var sec = list.querySelector('.cat[data-id="' + cat.id + '"]');
        var ul = sec.querySelector("ul.items");
        var used = [];
        rows.forEach(function (row) {
          var li = [].slice.call(ul.querySelectorAll("li.item")).filter(function (x) {
            return x.querySelector(".name").textContent === row.n && used.indexOf(x) === -1;
          })[0];
          if (!li) {
            // No free row with that name left: it was a clone, or a write-in.
            var def = null;
            (cat.items || []).forEach(function (it) { if (it.n === row.n) def = it; });
            // Same shape a live write-in gets, qty default included — without it a
            // restored pasted line comes back wearing a "1" the man never typed.
            if (!def) def = { n: row.n, ax: cfg.writeinAx || [], flags: cfg.writeinFlags || [],
                              qtyDefault: cfg.writeinQtyDefault };
            ul.insertAdjacentHTML("beforeend", itemHTML(def, cfg, true));
            li = ul.lastElementChild;
            defOf.set(li, def);
          }
          used.push(li);
          applyValues(li, row);
          any = true;
        });
      });
      return any;
    }

    /* ── YESTERDAY'S LIST ──────────────────────────────────────────────────────
     * "Half of tomorrow's order is today's order. 'Start from last list' is worth
     * more to me than twenty more picker items." — a commercial foreman, on this
     * exact page. Clear is the only thing that ever destroys a list, so Clear is
     * where the copy gets kept: one slot, overwritten each time. */
    var LAST_KEY = cfg.persistKey ? cfg.persistKey + ".last" : null;
    function stashLast() {
      if (!LAST_KEY) return;
      try {
        var raw = localStorage.getItem(cfg.persistKey);
        if (raw) localStorage.setItem(LAST_KEY, raw);
      } catch (e) {}
    }
    function hasLast() {
      if (!LAST_KEY) return false;
      try { return !!localStorage.getItem(LAST_KEY); } catch (e) { return false; }
    }
    function restoreLast() {
      if (!LAST_KEY) return false;
      // Strip the current list first, or a restore stacks on top of what is there.
      [].forEach.call(list.querySelectorAll(".item .rm"), function (b) { b.closest(".item").remove(); });
      [].forEach.call(list.querySelectorAll(".tick"), function (t) {
        t.checked = false; t.closest(".item").classList.remove("is-checked");
      });
      var ok = restore(LAST_KEY);
      refresh();
      return ok;
    }

    function clearAll() {
      // The list about to be destroyed is the one worth keeping — stash before wipe.
      persist();
      stashLast();
      // Clones and write-ins are removable rows — clearing must actually remove
      // them, not just untick them, or the next list starts with yesterday's
      // duplicates sitting unticked in the middle of it.
      [].forEach.call(list.querySelectorAll(".item .rm"), function (b) { b.closest(".item").remove(); });
      [].forEach.call(list.querySelectorAll(".tick"), function (t) {
        t.checked = false; t.closest(".item").classList.remove("is-checked");
      });
      [].forEach.call(list.querySelectorAll(".i-qty"), function (q) { q.value = qtyDefault(null, cfg); });
      [].forEach.call(list.querySelectorAll(".i-note"), function (x) { x.value = ""; });
      try { if (cfg.persistKey) localStorage.removeItem(cfg.persistKey); } catch (e) {}
      if (cfg.onClear) cfg.onClear();
      refresh();
    }
    if (clearBtn) clearBtn.addEventListener("click", clearAll);

    if (copyBtn) copyBtn.addEventListener("click", function () { copyText(text(), copyBtn, cfg.onFlash); });

    var restored = restore();
    if (restored && cfg.onRestored) cfg.onRestored();
    refresh();
    // The shared runtime resolves the true date asynchronously — re-render when it lands.
    document.addEventListener("av:ready", refresh);
    document.addEventListener("av:date", refresh);

    /* An axis whose option list is built by the USER at runtime (the locations on
     * this job, the rooms on this floor). Rewrites every select for that axis —
     * including clones and write-ins added since — and PRESERVES what each line
     * already had picked, because a tech who adds a fifth room must not lose the
     * four lines he already stamped. */
    function setAxOptions(k, list_, keepDefault) {
      [].forEach.call(list.querySelectorAll('.i-ax[data-k="' + k + '"]'), function (s) {
        var had = s.value;
        s.innerHTML = opts(list_);
        if (had && list_.indexOf(had) !== -1) s.value = had;
        else if (keepDefault) s.value = keepDefault;
      });
      refresh();
    }

    return {
      refresh: refresh, text: text, sections: sections, seg: segState,
      setAxOptions: setAxOptions, clearAll: clearAll, restored: restored,
      hasLast: hasLast, restoreLast: restoreLast,
      copy: function () { copyText(text(), copyBtn, cfg.onFlash); }
    };
  }

  window.ChecklistRequest = { mount: mount, esc: esc, todayStr: todayStr, copyText: copyText };
})();
