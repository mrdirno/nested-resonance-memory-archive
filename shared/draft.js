/* FIELD TOOLKIT — SHARED: THE DRAFT KEEPER.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS FILE EXISTS, and it is an accusation before it is an engine.
 *
 * shared/checklist-request.js opens with: "Shape #1 had TWO live instances —
 * av/consumables.html and plumbing/supply-house-order.html — ... This file is
 * that engine, extracted at the point where a third and fourth instance were
 * about to be forked." Its persistence block goes further and names them again:
 * "this engine drives av/consumables, av/cable-list, plumbing/supply-house-order
 * and electrical/pull-list. Fixing it in the engine fixes all four at once."
 *
 * IT NEVER DROVE EITHER OF THE TWO IT WAS EXTRACTED FROM. The engine shipped to
 * the siblings — cable-list, pull-list, the-load, truck-stock, the low-voltage
 * shop list — and the two originals stayed forks. Measured on disk: of 55 live
 * tool pages, 52 keep what a man types and THREE do not — av/consumables.html
 * (the page this whole kit's shape #1 was proved on), plumbing/supply-house-order.html,
 * and av/report-builder.html. Not "debounce-only", which is the scar the engine
 * already carries. No save at all. Reload the tab and a twenty-minute walk is gone.
 *
 * Nobody files a wish for this: the man who lost the list does not report a bug,
 * he stops opening the page. Which is the definition of the BACKPORT axis.
 *
 * WHY A NEW ENGINE RATHER THAN MIGRATING THE TWO FORKS ONTO THE OLD ONE.
 * Migrating is a refactor with a layout blast radius on the page the book calls
 * the quality bar — av/consumables lays its qty+note out on the row itself, the
 * engine hides them behind .cfg until a line is ticked, and its filter,
 * check-shown, per-category All and n/total tally have no engine equivalent.
 * That trade is: risk the flagship's layout to deliver persistence. The defect is
 * persistence. So the SAVE is what gets extracted — once, shared, shape-agnostic —
 * and no page moves a pixel. The fork debt is real and stays on the roster; it is
 * not paid by pretending a rewrite is a fix.
 *
 * WHAT THIS OWNS — every one of these is a scar in av/AV_SOCIETY.md §SCARS, and
 * a page that hand-rolls a save gets to rediscover all four:
 *
 *  · THE FLUSH TRIAD ("the camera round-trip eats the draft", 2026-08-04). A
 *    250 ms debounce is not a save. iOS backgrounds the tab the instant a man
 *    leaves for the camera, a phone call or the next app, and a timer that has
 *    not fired dies with it. Write SYNCHRONOUSLY on visibilitychange (the one
 *    that fires on iOS), pagehide (a real navigation) and blur (focus leaving to
 *    another app on desktop).
 *  · NULL MEANS DELETE ("clear must actually clear", 2026-08-04). A caller whose
 *    snapshot always returns an object cannot be cleared: removeItem lands, the
 *    pending debounce fires 250 ms later and writes the record straight back. So
 *    snapshot() returning null is the ONLY way a record is dropped, and the
 *    contract is stated at the top of every caller.
 *  · KEYED BY NAME, NEVER BY POSITION (shared/checklist-request.js §PERSISTENCE).
 *    Clones and write-ins shift indices, and a restore keyed on position silently
 *    reassigns a tech's quantities to the wrong line — a wrong order that reads
 *    as a right one. The callers here match rows by their visible name and take
 *    each row once.
 *  · STORAGE CAN THROW. Private mode, a full quota, a locked-down job-site
 *    browser. Every read and write is wrapped; a page that cannot save must still
 *    work, because the copy button is the product and the draft is the courtesy.
 *
 * WHAT IT DOES NOT OWN: what a draft IS. The caller writes snapshot()/apply()
 * over its own DOM in its own vocabulary. This file never touches an element.
 *
 * Load before the page's own script:
 *   <script src="../shared/draft.js"></script>
 */
(function () {
  "use strict";

  /* One tool, one key, and the shape version rides INSIDE the record rather than
   * in the key. Bumping `v` when a snapshot's shape changes makes an old draft
   * unreadable-and-dropped instead of half-applied, which is the failure that
   * looks like data corruption to the man holding the phone. */
  function keep(cfg) {
    var key = cfg.key;
    var ver = cfg.v || 1;
    var dead = !key || typeof cfg.snapshot !== "function" || typeof cfg.apply !== "function";
    var timer = null;
    var api;

    function put(k, s) {
      try { localStorage.setItem(k, JSON.stringify({ v: ver, s: s })); } catch (e) {}
    }
    function drop(k) {
      try { localStorage.removeItem(k); } catch (e) {}
    }
    function read(k) {
      var raw = null;
      try { raw = localStorage.getItem(k); } catch (e) { return null; }
      if (!raw) return null;
      var p;
      try { p = JSON.parse(raw); } catch (e) { return null; }
      if (!p || p.s == null) return null;
      // A record written by an older shape is not a draft, it is a hazard.
      if ((p.v || 1) !== ver) return null;
      return p.s;
    }

    /* The write. A snapshot that throws must not take the page down with it —
     * losing one save is a courtesy lost; an exception here kills every handler
     * downstream of the render that called it. */
    function write() {
      if (dead) return;
      var s;
      try { s = cfg.snapshot(); } catch (e) { return; }
      if (s == null) drop(key);
      else put(key, s);
    }

    function save() {
      if (dead) return;
      clearTimeout(timer);
      timer = setTimeout(write, 250);
    }

    function flush() {
      if (dead) return;
      clearTimeout(timer);
      try { write(); } catch (e) {}
    }

    if (!dead) {
      document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "hidden") flush();
      });
      window.addEventListener("pagehide", flush);
      window.addEventListener("blur", flush);
    }

    /* ── YESTERDAY'S LIST ──────────────────────────────────────────────────────
     * "Half of tomorrow's order is today's order." — a commercial foreman, on
     * av/cable-list. Clear is the only thing that ever destroys a draft, so Clear
     * is where the copy is kept: one slot, overwritten each time. Opt in with
     * `last: true`; a page whose draft is a set of preferences rather than a
     * day's work has nothing to start from and should leave it off. */
    var LAST = cfg.last && key ? key + ".last" : null;

    function hasLast() {
      if (!LAST) return false;
      try { return !!localStorage.getItem(LAST); } catch (e) { return false; }
    }
    function restoreLast() {
      if (!LAST) return false;
      var s = read(LAST);
      if (s == null) return false;
      try { cfg.apply(s); } catch (e) { return false; }
      save();
      return true;
    }

    /* CLEAR, in the one order that works (shared/checklist-request.js clearAll):
     * write what is about to die → copy it to the last slot → let the page wipe
     * its own DOM → drop the record. Cancelling the timer first is what stops the
     * pending debounce from resurrecting the list a quarter-second later; the
     * snapshot going null after the wipe is what stops the NEXT one. */
    function clear(wipe) {
      if (dead) { if (wipe) wipe(); return; }
      clearTimeout(timer);
      if (LAST) { write(); try { var raw = localStorage.getItem(key); if (raw) localStorage.setItem(LAST, raw); } catch (e) {} }
      if (wipe) { try { wipe(); } catch (e) {} }
      drop(key);
    }

    api = {
      save: save, flush: flush, clear: clear,
      hasLast: hasLast, restoreLast: restoreLast,
      restored: false
    };

    if (!dead) {
      var s0 = read(key);
      if (s0 != null) {
        try { cfg.apply(s0); api.restored = true; } catch (e) { api.restored = false; }
      }
      if (api.restored && cfg.onRestored) { try { cfg.onRestored(); } catch (e) {} }
    }
    return api;
  }

  /* ── THE FLAT CASE ─────────────────────────────────────────────────────────
   * A page whose whole state is a handful of controls with ids — a settings
   * form, a prompt builder — needs snapshot/apply that are pure boilerplate, and
   * boilerplate copied three times is the fork this file exists to prevent.
   *
   * Returns { snapshot, apply, watch } for a list of element ids. Defaults are
   * captured AT CALL TIME, which must therefore be after the page has set them:
   * a field still holding exactly what it was born with is not something a man
   * typed, and saving it would resurrect a stale default on top of a new one. */
  function fields(ids) {
    var defs = {};
    function el(id) { return document.getElementById(id); }
    function get(e) { return e.type === "checkbox" ? !!e.checked : e.value; }
    function set(e, v) { if (e.type === "checkbox") e.checked = !!v; else e.value = v; }

    ids.forEach(function (id) { var e = el(id); if (e) defs[id] = get(e); });

    return {
      snapshot: function () {
        var out = {}, touched = false;
        ids.forEach(function (id) {
          var e = el(id);
          if (!e) return;
          var v = get(e);
          out[id] = v;
          if (v !== defs[id]) touched = true;
        });
        return touched ? out : null;
      },
      apply: function (s) {
        ids.forEach(function (id) {
          var e = el(id);
          if (e && s[id] != null) set(e, s[id]);
        });
      },
      /* Bind every field to a save. Both events, because `input` misses a
       * <select> in some engines and `change` misses every keystroke in a
       * textarea — the one place a man types a paragraph he will not retype. */
      watch: function (fn) {
        ids.forEach(function (id) {
          var e = el(id);
          if (!e) return;
          e.addEventListener("input", fn);
          e.addEventListener("change", fn);
        });
      }
    };
  }

  window.Draft = { keep: keep, fields: fields };
})();
