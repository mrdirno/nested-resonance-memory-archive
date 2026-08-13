/* FIELD TOOLKIT — SHAPE #3 ENGINE: THE ROW LOG.
 *
 * av/AV_SOCIETY.md §THE THREE SHAPES. Shape #1 (checklist → request) and shape #2
 * (the note) are shipped. This is #3, and it is the largest cluster the five-trade
 * roster research found: every trade has at least one row log.
 *
 * Built as an ENGINE on its FIRST instance rather than its second — a deliberate
 * exception to "two instances is where a shape is provable" — because five
 * independent trade rosters converged on the identical widget with no
 * coordination, and the trade it ships in has a second config queued directly
 * behind the first. Building the first as a page would guarantee the fork.
 *
 * WHAT THE ENGINE OWNS — the parts that drift the moment a shape is forked:
 *   · ONE-AT-A-TIME ADD with sticky carry-forward and a +1 tag bump
 *   · BULK CREATE — a tag-range generator and a pasted column. This is a SHIP
 *     GATE, not a nicety: a man does not type 240 rows on a phone one at a time,
 *     so without it the tool is a slower notes app.
 *   · TAP-TO-ADVANCE — tapping a row moves it one step up the status ladder.
 *     That is the literal expression of "ticking beats typing" on a long list,
 *     and it dodges the six-option axis ceiling for free: the row renders ONE
 *     chip (its current state), never the whole ladder, so it cannot wrap.
 *   · FLAGS as a separate toggle, never a ladder step — a blocked device is
 *     blocked AT some stage, and collapsing the two loses which one.
 *   · SELF-BUILDING AXES — floors, areas and panel names are LEARNED from what he
 *     types and become taps. A guessed list is always wrong: a hospital runs
 *     B / G / 1 / 2 / M / PH / Roof and we cannot know that.
 *   · grouping with a switchable axis · per-group counts · the status rollup
 *   · persistence WITH a synchronous flush · the delta since the last copy
 *   · NAMED DOCUMENT FILTERS (added at the second instance, the cross-boundary
 *     request): a row log that tracks somebody ELSE's work is a chase list, and
 *     the message he sends on day two is not the list, it is WHAT IS STILL OPEN.
 *     `cfg.filters` composes with the delta and touches the DOCUMENT only.
 *   · A NAMEABLE PASTE TARGET AND AN ANSWER LADDER (added at the third
 *     instance, the RETURN LEG — the reply to a cross-boundary request).
 *     `cfg.pasteKey` says which field a bulk-pasted line lands in, because the
 *     line pasted there is somebody else's prose and not a device tag;
 *     `cfg.statusWrap` lets the tap cycle back to blank, because an ANSWER is a
 *     choice and a wrong choice must be reachable without the pencil sheet; and
 *     `cfg.statusDone` says which rung wears the settled colour, because on an
 *     answer ladder that rung is not the last one. All three default to the
 *     behaviour the first two instances already shipped.
 *   · A BATCH WRITE FROM OUTSIDE THE BAR (`applyValues`, added at the fifth
 *     instance — the reconcile intake). The other man's answer to a
 *     cross-boundary request comes back as ONE message covering twenty rows,
 *     and ticking twenty rows by hand is this engine's own law failing at the
 *     scale it was written for. One call, one render, one save.
 *   · the plain-text document · the TSV · copy with the non-secure-context
 *     fallback · the self-aware date · re-render on the runtime's av:ready.
 *
 * WHAT THE CALLER OWNS: the FIELDS (a trade's vocabulary is never the engine's),
 * which field gates which other field's options, the WORDS of the document, and
 * the CSS. The engine assembles state; the page writes sentences.
 *
 * NOT here, deliberately: any computed quantity, rating, spacing, distance limit,
 * load, fill or count-per-circuit, and no denominator the tool did not watch a
 * man enter. The user states every value (av/AV_SOCIETY.md §SAFETY).
 *
 * SCARS BUILT IN FROM LINE ONE, because they were already paid for elsewhere:
 *   · A DEFAULT IS A CLAIM — every select leads with a neutral option, bulk rows
 *     land with a BLANK status, and the document drops every unpicked value.
 *   · A 250 ms DEBOUNCE IS NOT A SAVE — the draft flushes synchronously on
 *     visibilitychange / pagehide / blur. This is a walk-the-job tool and the
 *     camera, the phone call and the lock screen all background the tab.
 *   · A PHONE DESTROYS AN IDENTIFIER — identifier fields ship with autocorrect
 *     and autocapitalize off, and NOTHING normalises on the way out.
 *
 * Load AFTER the trade config and registry, alongside the shared runtime:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/rowlog.js"></script>
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }
  function byId(x) { return typeof x === "string" ? document.querySelector(x) : x; }

  function todayStr() {
    return (window.Toolkit && window.Toolkit.todayStr)
      ? window.Toolkit.todayStr()
      : new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  /* Copy that survives a job site: the async Clipboard API needs a secure
   * context and a job-site browser may not give one. Failing silently there is
   * the whole product broken, so fall back to a real, visible selection. */
  function copyText(t, btn, onFlash) {
    function flash(msg) {
      if (onFlash) return onFlash(msg, btn);
      if (!btn) return;
      var old = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", old);
      btn.textContent = msg;
      setTimeout(function () { btn.textContent = old; }, 1500);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = t; ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:92%;height:44%;z-index:9999";
      document.body.appendChild(ta);
      ta.select(); ta.setSelectionRange(0, ta.value.length);
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      flash(ok ? "Copied" : "Select & copy");
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(t).then(function () { flash("Copied"); }, fallback);
    } else fallback();
  }

  /* Model numbers, device tags and part numbers are exactly what autocorrect and
   * autocapitalize are worst at, and the suffix IS the tag. Watching a phone turn
   * a device tag into an English word is the moment a man closes a form for good. */
  var ID_ATTRS = ' autocapitalize="characters" autocorrect="off" spellcheck="false" autocomplete="off"';

  /* The +1 accelerator. CAM-104 -> CAM-105, D.1.12 -> D.1.13, 004 -> 005.
   * Offered as a TAP, never auto-filled: a tag the tool wrote and the man did not
   * read is a wrong tag on somebody's real drawing. He triggers it; he can type
   * over it; the engine never enforces a sequence. */
  function nextIdent(v) {
    var m = /^(.*?)(\d+)(\D*)$/.exec(String(v == null ? "" : v));
    if (!m) return null;
    var d = m[2], n = String(parseInt(d, 10) + 1);
    while (n.length < d.length) n = "0" + n;      // 004 -> 005, never 5
    return m[1] + n + m[3];
  }

  function mount(cfg) {
    var bar = byId(cfg.bar), listEl = byId(cfg.list);
    var tallyEl = byId(cfg.tally), previewEl = byId(cfg.preview);
    var copyBtn = byId(cfg.copyBtn), tsvBtn = byId(cfg.tsvBtn);
    if (!bar || !listEl) throw new Error("RowLog.mount: bar and list are required");

    var FIELDS = cfg.fields || [];
    var STATUS = cfg.statusOrder || [];
    var FLAGS = cfg.flagValues || [];
    var GROUPS = cfg.groupOptions || [{ key: FIELDS[0] && FIELDS[0].key, label: "Group" }];

    var rows = [];          // {id, t, values:{}, flag:""}
    var seq = 1, touch = 1, copiedAt = 0;
    var editingId = null;
    /* WHAT THE BAR SAID WHEN THE PENCIL OPENED (§SCARS 2026-08-10 — "the pencil
     * sheet holds a photograph, and Save puts it back"). The edit bar is a
     * SNAPSHOT of a row, and while it sits open the row underneath it can still
     * move: the tap ladder advances it, the walk settles it. Saving the whole
     * snapshot back therefore un-did field verification silently. So commit()
     * needs to know what he actually CHANGED, which is the diff against this. */
    var editingSnap = null;
    var sticky = {};
    var learned = {};       // {fieldKey: [values he has actually typed]}
    var groupKey = GROUPS[0].key;
    var deltaOnly = false;
    var filterKeys = [];    // [] = the whole list; see docRows()

    function field(k) { for (var i = 0; i < FIELDS.length; i++) if (FIELDS[i].key === k) return FIELDS[i]; return null; }
    function ctl(k) { return bar.querySelector('[data-k="' + k + '"]'); }

    /* Options for a field can depend on another field (subsystem gates type, an
     * ASK gates the specs anybody would pick for it), so they are resolved at
     * render time, never frozen at mount.
     *
     * The THIRD argument is what he has already typed into a `learn` field. A
     * caller that supplies presets would otherwise SHADOW them — the preset list
     * wins and his own words disappear the moment the gating field changes — so
     * the caller gets both lists and decides the merge. Callers that ignore it
     * behave exactly as before. */
    function optionsOf(f, cur) {
      if (typeof cfg.optionsFor === "function") {
        var o = cfg.optionsFor(f.key, cur || readBar(), (learned[f.key] || []).slice());
        if (o) return o;
      }
      if (f.input === "learn") return (learned[f.key] || []);
      return f.options || [];
    }

    /* ── the add / edit bar ───────────────────────────────────────────────────
     * The identifier leads with the primary button beside it: type the tag, press
     * add. Everything else already carries the last answer, so device #2 on the
     * same floor is two interactions, not eleven. */
    function fieldHTML(f) {
      var id = "rl_" + f.key;
      var lab = '<label class="rl-lab" for="' + id + '">' + esc(f.label)
        + (f.sticky ? ' <i class="rl-carry">carries</i>' : "") + "</label>";
      if (f.input === "select") {
        return '<div class="rl-f' + (f.wide ? " rl-wide" : "") + '" data-for="' + esc(f.key) + '">' + lab
          + '<select id="' + id + '" data-k="' + esc(f.key) + '" class="rl-in"></select></div>';
      }
      if (f.input === "chips" || f.input === "learn") {
        return '<div class="rl-f rl-wide" data-for="' + esc(f.key) + '">' + lab
          + '<input type="hidden" data-k="' + esc(f.key) + '">'
          + (f.input === "learn"
            ? '<input class="rl-in rl-learn" data-learn="' + esc(f.key) + '" type="text"' + ID_ATTRS
              + ' placeholder="' + esc(f.placeholder || "") + '">' : "")
          + '<div class="rl-chips" data-chips="' + esc(f.key) + '"></div></div>';
      }
      return '<div class="rl-f' + (f.wide ? " rl-wide" : "") + '" data-for="' + esc(f.key) + '">' + lab
        + '<input id="' + id + '" data-k="' + esc(f.key) + '" class="rl-in" type="text"'
        + (f.identifier ? ID_ATTRS : "")
        + ' placeholder="' + esc(f.placeholder || "") + '"></div>';
    }

    function buildBar() {
      var lead = FIELDS.filter(function (f) { return f.lead; });
      var rest = FIELDS.filter(function (f) { return !f.lead; });
      bar.innerHTML =
        '<div class="rl-lead">' + lead.map(fieldHTML).join("")
        + '<button type="button" class="rl-add" id="rlAdd">Add</button></div>'
        + '<div class="rl-next" id="rlNext" hidden></div>'
        + '<p class="rl-dupe" id="rlDupe" hidden></p>'
        + '<div class="rl-grid">' + rest.map(fieldHTML).join("") + "</div>"
        + '<div class="rl-editing" id="rlEditing" hidden>'
        + '<span class="rl-editlab">Editing this one</span>'
        + (FLAGS.length ? '<span class="rl-flags" id="rlFlags"></span>' : "")
        + '<button type="button" class="rl-mini" id="rlCancel">Cancel</button>'
        + '<button type="button" class="rl-mini rl-del" id="rlDelete">Delete</button>'
        + "</div>";

      bar.querySelector("#rlAdd").addEventListener("click", commit);
      bar.querySelector("#rlCancel").addEventListener("click", function () { stopEditing(true); });
      bar.querySelector("#rlDelete").addEventListener("click", function () {
        if (editingId == null) return;
        rows = rows.filter(function (r) { return r.id !== editingId; });
        stopEditing(true); render(); persistNow();
      });

      FIELDS.forEach(function (f) {
        var el = ctl(f.key);
        if (el && f.input !== "select" && f.input !== "chips" && f.input !== "learn") {
          el.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); commit(); } });
          if (f.identifier) el.addEventListener("input", warnDuplicate);
        }
        if (el && f.input === "select") el.addEventListener("change", function () {
          if (f.sticky) sticky[f.key] = el.value;
          // A gating field changes what the gated axis may offer — and that is as
          // true of a `learn` axis (presets for THIS pick, plus whatever he has
          // typed before) as it is of a fixed `chips` axis. Repainting only one of
          // the two shipped a gated learn field frozen on the previous pick's list.
          FIELDS.forEach(function (g) { if (g.input === "chips" || g.input === "learn") paintChips(g); });
        });
        var li = bar.querySelector('[data-learn="' + f.key + '"]');
        if (li) {
          li.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); learnFrom(f, li.value); } });
          li.addEventListener("blur", function () { learnFrom(f, li.value); });
        }
      });
      bar.addEventListener("click", function (e) {
        var c = e.target && e.target.closest ? e.target.closest(".rl-chip[data-v]") : null;
        if (!c) return;
        var k = c.parentNode.getAttribute("data-chips");
        var f = field(k); if (!f) return;
        var h = ctl(k);
        h.value = (h.value === c.getAttribute("data-v")) ? "" : c.getAttribute("data-v"); // tap again to unset
        if (f.sticky) sticky[k] = h.value;
        paintChips(f);
      });
      FIELDS.forEach(function (f) {
        if (f.input === "select") paintSelect(f);
        if (f.input === "chips" || f.input === "learn") paintChips(f);
      });
      paintFlags();
    }

    function paintSelect(f) {
      var el = ctl(f.key); if (!el) return;
      var had = el.value;
      // NEUTRAL FIRST OPTION, always. A pre-selected option is the tool putting
      // words in a man's mouth, and the document drops anything left on it.
      el.innerHTML = '<option value="">' + esc(f.neutral || "—") + "</option>"
        + optionsOf(f).map(function (o) {
          var v = typeof o === "string" ? o : o.v, l = typeof o === "string" ? o : (o.label || o.v);
          return '<option value="' + esc(v) + '">' + esc(l) + "</option>";
        }).join("");
      if (had) el.value = had;
    }
    function paintChips(f) {
      var box = bar.querySelector('[data-chips="' + f.key + '"]'); if (!box) return;
      var cur = ctl(f.key).value;
      var opts = optionsOf(f);
      box.innerHTML = opts.map(function (o) {
        var v = typeof o === "string" ? o : o.v, l = typeof o === "string" ? o : (o.label || o.v);
        return '<button type="button" class="rl-chip' + (v === cur ? " on" : "") + '" data-v="' + esc(v) + '">' + esc(l) + "</button>";
      }).join("") || '<span class="rl-hint">' + esc(f.emptyHint || "Type one above — it becomes a button after that.") + "</span>";
    }
    function learnFrom(f, raw) {
      var v = String(raw == null ? "" : raw).trim();
      if (!v) return;
      learned[f.key] = learned[f.key] || [];
      if (learned[f.key].indexOf(v) === -1) learned[f.key].push(v);
      ctl(f.key).value = v;
      if (f.sticky) sticky[f.key] = v;
      var li = bar.querySelector('[data-learn="' + f.key + '"]'); if (li) li.value = "";
      paintChips(f); persistNow();
    }
    function paintFlags() {
      var box = bar.querySelector("#rlFlags"); if (!box) return;
      var r = rows.filter(function (x) { return x.id === editingId; })[0];
      var cur = r ? (r.flag || "") : "";
      box.innerHTML = FLAGS.map(function (v) {
        return '<button type="button" class="rl-chip rl-flagchip' + (v === cur ? " on" : "") + '" data-flag="' + esc(v) + '">' + esc(v) + "</button>";
      }).join("");
      [].forEach.call(box.querySelectorAll("[data-flag]"), function (b) {
        b.addEventListener("click", function () {
          var row = rows.filter(function (x) { return x.id === editingId; })[0];
          if (!row) return;
          var v = b.getAttribute("data-flag");
          row.flag = (row.flag === v) ? "" : v;
          row.t = ++touch;
          paintFlags(); render(); persistNow();
        });
      });
    }

    function readBar() {
      var v = {};
      FIELDS.forEach(function (f) { var el = ctl(f.key); v[f.key] = el ? String(el.value).trim() : ""; });
      return v;
    }
    function writeBar(v) {
      FIELDS.forEach(function (f) {
        var el = ctl(f.key); if (!el) return;
        var val = v[f.key] == null ? "" : v[f.key];
        if (f.input === "select" && val) {
          var has = [].some.call(el.options, function (o) { return o.value === val; });
          if (!has) { var o = document.createElement("option"); o.value = val; o.textContent = val; el.appendChild(o); }
        }
        if ((f.input === "chips" || f.input === "learn") && val) {
          learned[f.key] = learned[f.key] || [];
          if (f.input === "learn" && learned[f.key].indexOf(val) === -1) learned[f.key].push(val);
        }
        el.value = val;
        if (f.input === "chips" || f.input === "learn") paintChips(f);
      });
    }
    function clearTransient() {
      FIELDS.forEach(function (f) {
        if (f.sticky) return;
        var el = ctl(f.key); if (el) el.value = "";
        if (f.input === "chips" || f.input === "learn") paintChips(f);
      });
    }
    function writeSticky() {
      FIELDS.forEach(function (f) {
        if (!f.sticky) return;
        var el = ctl(f.key); if (el && sticky[f.key] != null) el.value = sticky[f.key];
        if (f.input === "chips" || f.input === "learn") paintChips(f);
      });
    }

    var idField = FIELDS.filter(function (f) { return f.identifier; })[0];
    var required = FIELDS.filter(function (f) { return f.required; });

    /* WHERE A PASTED LINE LANDS. Bulk paste was built for a column of device
     * tags, so it wrote into the IDENTIFIER field — the only field a tag could
     * be. The return leg pastes somebody else's REQUEST, one ask per line, into
     * a field that is prose and must never carry the identifier's
     * uppercase-and-+1 behaviour. So the target is nameable. Unnamed, it is the
     * identifier, exactly as before. */
    var pasteField = (cfg.pasteKey
      && FIELDS.filter(function (f) { return f.key === cfg.pasteKey; })[0]) || idField;

    /* One tag logged twice and the PM goes back to his own spreadsheet forever.
     * A WARNING, never a block: a real job legitimately has D-214 on the door
     * schedule and D-214 as a tag on two leaves of a pair. */
    function warnDuplicate() {
      var box = bar.querySelector("#rlDupe"); if (!box || !idField) return;
      var v = String(ctl(idField.key).value).trim();
      var hit = v && rows.filter(function (r) { return r.id !== editingId && r.values[idField.key] === v; }).length;
      box.hidden = !hit;
      if (hit) box.textContent = "Heads up — " + v + " is already on the list" + (hit > 1 ? " (" + hit + "×)" : "") + ".";
    }

    function commit() {
      var v = readBar();
      var miss = required.filter(function (f) { return !v[f.key]; })[0];
      if (miss) {
        var el = ctl(miss.key);
        if (el) { try { el.focus(); } catch (e) {} }
        var wrap = bar.querySelector('[data-for="' + miss.key + '"]');
        if (wrap) { wrap.classList.add("rl-bad"); setTimeout(function () { wrap.classList.remove("rl-bad"); }, 900); }
        return;
      }
      if (editingId != null) {
        /* WRITE ONLY WHAT HE CHANGED IN THE BAR, never the whole snapshot. This
         * used to be `r.values = v`, and v is what the bar was handed when the
         * pencil opened — so any move the row made underneath it (a tap up the
         * ladder, a walk that settled it) was reverted by Save, with no warning
         * and nothing on screen to show it. Diffing against the snapshot means a
         * field he never touched keeps whatever the row says NOW, and a key that
         * is not a bar field at all survives instead of being dropped. */
        var snap = editingSnap || {};
        rows.forEach(function (r) {
          if (r.id !== editingId) return;
          var next = {};
          Object.keys(r.values).forEach(function (k) { next[k] = r.values[k]; });
          Object.keys(v).forEach(function (k) { if (v[k] !== snap[k]) next[k] = v[k]; });
          r.values = next; r.t = ++touch;
        });
        stopEditing(false);
      } else {
        rows.push({ id: seq++, t: ++touch, values: v, flag: "" });
      }
      FIELDS.forEach(function (f) { if (f.sticky) sticky[f.key] = v[f.key]; });
      offerNext(v);
      clearTransient();
      if (idField) { var fe = ctl(idField.key); if (fe) { try { fe.focus(); } catch (e) {} } }
      warnDuplicate();
      render(); persistNow();
    }

    function offerNext(v) {
      var box = bar.querySelector("#rlNext"); if (!idField || !box) return;
      var nxt = nextIdent(v[idField.key]);
      if (!nxt) { box.hidden = true; box.innerHTML = ""; return; }
      box.hidden = false;
      box.innerHTML = '<button type="button" class="rl-nextbtn">Next: <b>' + esc(nxt) + "</b></button>";
      box.querySelector("button").addEventListener("click", function () {
        var el = ctl(idField.key); if (!el) return;
        el.value = nxt; try { el.focus(); } catch (e) {}
        warnDuplicate();
        box.hidden = true; box.innerHTML = "";
      });
    }

    /* ── BULK CREATE — the ship gate ──────────────────────────────────────────
     * A man does not type 240 rows on a phone one at a time, which is to say he
     * does not use the tool at all. Two ways in, both landing rows with a BLANK
     * status (a bulk-created row has no claim on it yet) and with whatever the
     * pickers currently say.
     *   · a RANGE: prefix + first + last, zero-pad taken from the first number,
     *     so "CAM-" 201 → 248 is 48 rows in four taps. This one matters more than
     *     the paste, because pasting a column out of a spreadsheet on iOS is
     *     miserable.
     *   · a PASTED COLUMN: one tag per line, exactly as it left his spreadsheet.
     */
    function addRange(prefix, from, to, suffix) {
      var a = parseInt(from, 10), b = parseInt(to, 10);
      if (isNaN(a) || isNaN(b)) return 0;
      var pad = String(from).trim().length;
      var step = a <= b ? 1 : -1, n = 0, made = [];
      for (var i = a; step > 0 ? i <= b : i >= b; i += step) {
        var s = String(i); while (s.length < pad) s = "0" + s;
        made.push(String(prefix || "") + s + String(suffix || ""));
        if (++n > 2000) break;                        // a runaway range is a typo
      }
      return addTags(made);
    }
    function addPasted(text) {
      return addTags(String(text || "").split(/\r?\n/));
    }
    function addTags(tags) {
      if (!pasteField) return 0;
      var base = readBar(), n = 0;
      tags.forEach(function (tag) {
        var t = String(tag).trim();
        if (!t) return;
        var v = {};
        FIELDS.forEach(function (f) { v[f.key] = f.sticky ? (base[f.key] || "") : ""; });
        v[pasteField.key] = t;                         // NOT normalised, ever
        if (cfg.statusKey) v[cfg.statusKey] = "";      // a bulk row claims nothing
        rows.push({ id: seq++, t: ++touch, values: v, flag: "" });
        n++;
      });
      if (n) { render(); persistNow(); }
      return n;
    }

    function startEditing(id) {
      var r = rows.filter(function (x) { return x.id === id; })[0]; if (!r) return;
      editingId = id;
      writeBar(r.values);
      // Snapshot AFTER writeBar, off the bar itself rather than off r.values: the
      // diff in commit() is only honest if both sides were read the same way (a
      // control can normalise what it was handed, and that normalisation is not
      // an edit he made).
      editingSnap = readBar();
      bar.querySelector("#rlEditing").hidden = false;
      bar.querySelector("#rlAdd").textContent = "Save";
      bar.querySelector("#rlNext").hidden = true;
      bar.classList.add("is-editing");
      paintFlags(); warnDuplicate(); render();
      try { bar.scrollIntoView({ block: "nearest" }); } catch (e) {}
    }
    function stopEditing(restore) {
      editingId = null;
      editingSnap = null;
      bar.querySelector("#rlEditing").hidden = true;
      bar.querySelector("#rlAdd").textContent = "Add";
      bar.classList.remove("is-editing");
      var d = bar.querySelector("#rlDupe"); if (d) d.hidden = true;
      if (restore) { clearTransient(); writeSticky(); render(); }
    }

    /* TAP THE ROW = ADVANCE ONE STEP. The row shows exactly one chip, so this
     * control can never wrap to a wheel no matter how long the ladder is. It
     * stops at the top rather than wrapping to blank — a man who taps twice by
     * accident must never silently un-do a tested device.
     *
     * `statusWrap` OPTS OUT OF THAT STOP, and only a ladder that is really a
     * CHOICE should take it. A progress ladder (committed -> in) is monotone and
     * un-doing it by mistake destroys a fact somebody walked out and verified.
     * An ANSWER ladder (will do / can't / need to know) is categorical: picking
     * the wrong one is not progress lost, it is a wrong answer that has to be
     * reachable, and making a man open the pencil sheet to correct one tap is
     * the "ticking beats typing" law failing on its own control. Default off,
     * so every existing config keeps the stop. */
    function advance(id) {
      var r = rows.filter(function (x) { return x.id === id; })[0];
      if (!r || !cfg.statusKey || !STATUS.length) return;
      var i = STATUS.indexOf(r.values[cfg.statusKey]);
      if (i < STATUS.length - 1) { r.values[cfg.statusKey] = STATUS[i + 1]; r.t = ++touch; }
      else if (cfg.statusWrap) { r.values[cfg.statusKey] = ""; r.t = ++touch; }
      render(); persistNow();
    }

    /* WRITE TO ROWS FROM OUTSIDE THE BAR — added at the fifth instance, for the
     * reconcile intake (shared/reconcile.js, THE THIRD MESSAGE): the other man's
     * answer comes back as one message and ticking twenty rows by hand is the
     * "ticking beats typing" law failing at the scale it was written for.
     *
     * ONE CALL FOR THE WHOLE BATCH, so twenty rows are one render and one save
     * rather than twenty of each — and one UNDO-shaped fact for the man reading
     * the list afterwards.
     *
     * IT REFUSES A KEY THE CONFIG NEVER DECLARED. A caller that misspells the
     * status key would otherwise write a field nothing renders, nothing copies
     * and nothing can clear — a silent no-op that looks like a save.
     *
     * AND IT CLOSES THE PENCIL FIRST (§SCARS — the pencil sheet holds a
     * photograph and Save puts it back): a sheet left open over a row this just
     * moved would revert it on the next Save, with nothing on screen to show it. */
    function applyValues(list) {
      if (!list || !list.length) return 0;
      /* CLOSE THE PENCIL ONLY IF IT IS OPEN ON A ROW THIS BATCH TOUCHES.
       * stopEditing(true) throws away whatever is half-typed in the bar, and a
       * batch write to twenty OTHER rows has no business doing that to the note
       * he is in the middle of writing. */
      if (editingId != null && list.some(function (x) { return x && x.id === editingId; })) stopEditing(true);
      var n = 0;
      list.forEach(function (item) {
        if (!item || item.id == null || !item.values) return;
        var r = rows.filter(function (x) { return x.id === item.id; })[0];
        if (!r) return;
        var moved = false;
        Object.keys(item.values).forEach(function (k) {
          if (!field(k)) return;                       // not a declared field
          var next = item.values[k] == null ? "" : String(item.values[k]);
          var cur = String(r.values[k] == null ? "" : r.values[k]);
          if (cur === next) return;
          /* A BATCH WRITE MAY NEVER WALK A ROW BACK DOWN THE LADDER. The caller
           * holds a photograph of the list taken when its report was built, and
           * the list moves underneath it — he walks the job with the card open
           * and settles a row by hand. Applying that photograph then pushed a
           * row somebody had WALKED OUT AND VERIFIED ("In") back down to a claim
           * somebody else made about it ("Committed"), silently, with the
           * confirmation reading "ticked 3 rows". That is §SCARS' pencil-sheet
           * photograph at list scale, and the guard belongs HERE rather than in
           * any one caller: the ladder is monotone, so the engine that owns it
           * is the only place that can say so for every caller there will be. */
          if (cfg.statusKey && k === cfg.statusKey && STATUS.length) {
            var to = STATUS.indexOf(next), from = STATUS.indexOf(cur);
            if (to > -1 && from > -1 && to <= from) return;   // never demote, never re-state
            if (to < 0 && cur) return;                        // never blank a stated rung
          }
          r.values[k] = next; moved = true;
        });
        if (moved) { r.t = ++touch; n++; }
      });
      if (n) { render(); persistNow(); }
      return n;
    }

    /* ── the grouped list ─────────────────────────────────────────────────────
     * NOT a table. A real table cannot survive a 390px phone, and this is a phone
     * tool first: one dense line per row under an ALL-CAPS group heading. The
     * table exists only in the TSV the office pastes into a spreadsheet. */
    /* The heading is a VALUE, and a config whose values are slugs ("ec", "rock")
     * would put "EC" and "ROCK" at the top of a document somebody else reads.
     * cfg.groupName maps the stored value to the word for the man reading it;
     * without it the value IS the word, exactly as before. */
    function groupsOf(src) {
      var order = [], map = {};
      (src || rows).forEach(function (r) {
        var g = (r.values[groupKey] || "").trim() || (cfg.ungroupedLabel || "NOT SET");
        if (!map[g]) { map[g] = []; order.push(g); }
        map[g].push(r);
      });
      /* A row we hide is a row he loses: unset stays, last. Beyond that the
         blocks come out in the order the rows happened to be added — fine for a
         log somebody keeps, wrong for a DOCUMENT that crosses to another
         company, where "here is what you're getting / here is what you're not"
         should read the same way every time. `groupSort` is how a config states
         that order; without one, insertion order stands exactly as before. */
      order.sort(function (a, b) {
        var ua = (cfg.ungroupedLabel || "NOT SET"), ia = a === ua ? 1 : 0, ib = b === ua ? 1 : 0;
        if (ia !== ib) return ia - ib;
        return cfg.groupSort ? cfg.groupSort(a, b, groupKey) : 0;
      });
      return order.map(function (g) {
        var name = g;
        if (cfg.groupName && g !== (cfg.ungroupedLabel || "NOT SET")) name = cfg.groupName(g, groupKey) || g;
        return { name: name, value: g, rows: map[g] };
      });
    }

    function render() {
      var gs = groupsOf();
      listEl.innerHTML = rows.length
        ? gs.map(function (g) {
          return '<section class="rl-grp"><h3>' + esc(g.name) + ' <span class="rl-n">' + g.rows.length + "</span></h3>"
            + g.rows.map(rowHTML).join("") + "</section>";
        }).join("")
        : '<p class="rl-empty">' + esc(cfg.emptyText || "Nothing on the list yet.") + "</p>";
      renderTally(gs);
      walkSyncLauncher();
      if (previewEl) previewEl.textContent = text();
      if (cfg.onChange) cfg.onChange(rows.length);
    }

    function rowHTML(r) {
      var main = cfg.rowMain ? cfg.rowMain(r.values) : (r.values[FIELDS[0].key] || "");
      var sub = cfg.rowSub ? cfg.rowSub(r.values) : "";
      var st = cfg.statusKey ? (r.values[cfg.statusKey] || "") : "";
      /* THE GREEN EDGE MEANS SETTLED, NOT LAST. On a monotone ladder those are
       * the same value and the default is unchanged; on an answer ladder the
       * settled one sits in the middle ("in already") and the last is a
       * question, so painting the last green would put the done colour on the
       * one row still waiting on somebody. */
      var doneVal = cfg.statusDone || (STATUS.length ? STATUS[STATUS.length - 1] : "");
      var atTop = cfg.statusKey && st && st === doneVal;
      var last = STATUS.length && st === STATUS[STATUS.length - 1];
      return '<div class="rl-row' + (r.id === editingId ? " is-editing" : "") + (r.flag ? " has-flag" : "") + '">'
        + '<button type="button" class="rl-tap' + (atTop ? " at-top" : "") + '" data-adv="' + r.id + '"'
        + ' aria-label="' + esc((st ? st + " — " : "")
            + (last && cfg.statusWrap ? "tap to clear it" : "tap to move to the next step")) + '">'
        + '<span class="rl-txt"><b class="rl-main">' + esc(main) + "</b>"
        + (sub ? '<span class="rl-sub">' + esc(sub) + "</span>" : "") + "</span>"
        + '<span class="rl-st' + (st ? "" : " none") + '" data-st="' + esc(st) + '">' + esc(st || "—") + "</span>"
        + "</button>"
        + (r.flag ? '<span class="rl-flag" data-flag="' + esc(r.flag) + '">' + esc(r.flag) + "</span>" : "")
        + '<button type="button" class="rl-edit" data-edit="' + r.id + '" aria-label="Edit this one">&#9998;</button>'
        + "</div>";
    }
    listEl.addEventListener("click", function (e) {
      if (!e.target || !e.target.closest) return;
      var a = e.target.closest("[data-adv]"); if (a) return advance(parseInt(a.getAttribute("data-adv"), 10));
      var b = e.target.closest("[data-edit]"); if (b) return startEditing(parseInt(b.getAttribute("data-edit"), 10));
    });

    function statusCounts() {
      if (!cfg.statusKey) return [];
      var c = {};
      rows.forEach(function (r) { var v = r.values[cfg.statusKey]; if (v) c[v] = (c[v] || 0) + 1; });
      return STATUS.filter(function (s) { return c[s]; }).map(function (s) { return { name: s, n: c[s] }; });
    }
    function flagged() { return rows.filter(function (r) { return r.flag; }); }
    function deltaRows() { return rows.filter(function (r) { return r.t > copiedAt; }); }

    /* ── THE DOCUMENT FILTERS ─────────────────────────────────────────────────
     * A row log that tracks somebody ELSE'S work is a chase list, and the message
     * a man sends on day two is not the list — it is WHAT IS STILL OPEN. A row
     * log that crosses a COMPANY boundary needs the other half of the same idea:
     * one walk produces asks aimed at three different companies, and each of them
     * gets his own message, not everybody's list.
     *
     * So filters are NAMED, DECLARED BY THE CALLER, and several can be active at
     * once — they AND together and then compose with the delta. "Still open" and
     * "only the electrician" are two independent scopes on one list, and needing
     * both at the same time is the normal case, not the clever one.
     *
     * THEY TOUCH THE DOCUMENT ONLY, never the on-screen list. A row we hide on
     * screen is a row he loses (the same reason the ungrouped bucket stays last
     * instead of vanishing) — and the preview under the button already shows him
     * exactly what the button is about to copy. */
    function filterDefs() {
      if (!filterKeys.length || !cfg.filters) return [];
      return filterKeys.map(function (k) {
        return cfg.filters.filter(function (f) { return f.v === k; })[0];
      }).filter(Boolean);
    }
    /* SCOPED = who the document is FOR. DOC = that, narrowed again to what has
     * changed. The two are separate because the FLAGGED block belongs to the
     * first and not the second: a flagged line is the thing you most want the
     * receiver to see whether or not it changed since your last copy — but it
     * must still be HIS line. Drawing that block from every row is how the
     * electrician ends up reading the GC's problems in a message addressed to
     * him, which is the exact failure a cross-boundary tool cannot have.
     * With no filters declared, scopedRows() === rows and the first instance
     * behaves precisely as it did. */
    function scopedRows() {
      var src = rows;
      filterDefs().forEach(function (f) {
        if (typeof f.test === "function") src = src.filter(function (r) { return f.test(r.values, r); });
      });
      return src;
    }
    function docRows() {
      var src = scopedRows();
      if (deltaOnly) src = src.filter(function (r) { return r.t > copiedAt; });
      return src;
    }

    function renderTally(gs) {
      if (!tallyEl) return;
      if (!rows.length) { tallyEl.innerHTML = ""; return; }
      var none = cfg.statusKey ? rows.filter(function (r) { return !r.values[cfg.statusKey]; }).length : 0;
      var nf = flagged().length;
      tallyEl.innerHTML =
        '<b>' + rows.length + " " + esc(rows.length === 1 ? (cfg.noun || "row") : (cfg.nounPlural || "rows")) + "</b>"
        + '<span class="rl-tsep">·</span><span>' + gs.length + " " + esc(gs.length === 1 ? (cfg.groupNoun || "group") : (cfg.groupNounPlural || "groups")) + "</span>"
        + statusCounts().map(function (s) { return '<span class="rl-tchip" data-st="' + esc(s.name) + '">' + s.n + " " + esc(s.name.toLowerCase()) + "</span>"; }).join("")
        + (none ? '<span class="rl-tchip rl-tnone">' + none + " not started</span>" : "")
        + (nf ? '<span class="rl-tchip rl-tflag">' + nf + " flagged</span>" : "");
    }

    /* ── the document ─────────────────────────────────────────────────────────
     * ALL-CAPS headings on their own line and " · " separators. This lands in a
     * text message or an email in a proportional font, where a padded column
     * arrives as mush (§SCARS). One line per row: nine "Label: value" lines per
     * row across 240 rows is 2,000 lines in a message nobody reads.
     *
     * The primary document is the DELTA plus the counts plus every flagged line —
     * what a foreman is actually asked for at the 7am huddle. The full list is
     * the TSV. A primary button that produces something no human receives is a
     * dead button. */
    function text() {
      var src = docRows();
      var scopedFlagged = scopedRows().filter(function (r) { return r.flag; });
      var fds = filterDefs();
      var fd = fds.filter(function (f) { return f.emptyText; })[0] || fds[0] || null;
      var out = [];
      var ctx = {
        total: rows.length, shown: src.length, today: todayStr(),
        status: statusCounts(), flagged: scopedFlagged.length,
        deltaOnly: deltaOnly, filters: filterKeys.slice(),
        filterLabel: fds.map(function (f) { return f.label; }).join(", "),
        groupLabel: (GROUPS.filter(function (g) { return g.key === groupKey; })[0] || {}).label
      };
      var head = cfg.docHead ? cfg.docHead(ctx) : null;
      if (head) out.push(head);
      if (!src.length) {
        out.push("");
        // An EMPTY FILTERED DOCUMENT IS THE BEST NEWS THE TOOL EVER GIVES — every
        // item is in. Saying "nothing on the list yet" there would be a lie, so
        // the filter brings its own sentence for the case where it matched none.
        out.push(rows.length
          ? (fd && fd.emptyText ? fd.emptyText : (deltaOnly ? "Nothing new since the last copy." : "Nothing on the list yet."))
          : "Nothing on the list yet.");
      }
      groupsOf(src).forEach(function (g) {
        out.push("");
        out.push(String(g.name).toUpperCase() + " — " + g.rows.length + (g.rows.length === 1 ? " ROW" : " ROWS"));
        g.rows.forEach(function (r) { out.push(cfg.docRow ? cfg.docRow(r.values, r) : ""); });
      });
      var f = scopedFlagged;
      if (f.length) {
        out.push("");
        out.push("FLAGGED — " + f.length);
        f.forEach(function (r) { out.push(cfg.docFlagRow ? cfg.docFlagRow(r.values, r) : ""); });
      }
      var foot = cfg.docFoot ? cfg.docFoot(ctx) : null;
      if (foot) { out.push(""); out.push(foot); }
      return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
    }

    /* The office receiver wants it in a spreadsheet, so the SECOND button hands
     * him tab-separated rows — ALWAYS every row, never the delta, because this
     * button is also the only honest archive this tool has. */
    function tsvCols() {
      return cfg.tsvColumns || FIELDS.map(function (f) { return { label: f.label, key: f.key }; });
    }
    function tsv() {
      var cols = tsvCols();
      var lines = [];
      if (cfg.tsvPreamble) lines.push(String(cfg.tsvPreamble({ total: rows.length, today: todayStr() })).replace(/[\t\r\n]+/g, " "));
      lines.push(cols.map(function (c) { return c.label; }).join("\t"));
      rows.forEach(function (r) {
        lines.push(cols.map(function (c) {
          var v = c.value ? c.value(r.values, r) : r.values[c.key];
          // A stray tab shifts every column right and silently corrupts the sheet.
          return String(v == null ? "" : v).replace(/[\t\r\n]+/g, " ");
        }).join("\t"));
      });
      return lines.join("\r\n");
    }

    /* ── AND THE BACKUP CAN BE READ BACK ───────────────────────────────────────
     * TWENTY LIVE PAGES ACROSS NINE TRADES TOLD A MAN "the spreadsheet copy is
     * also your backup: this lives in this browser on this phone", and
     * low-voltage/device-checkout went further — "send yourself the spreadsheet
     * copy at the end of a big day. A browser you haven't opened in a couple of
     * weeks can clear it out, and a new phone definitely will." All true. All of
     * it advice to KEEP a copy. And this engine had a TSV writer and no reader,
     * so the copy he kept could not be put back. A backup you cannot restore is
     * not a backup, it is a receipt for one — and the man who took the advice is
     * exactly the man who finds out on the new phone. §SCARS.
     *
     * IT ADDS, IT NEVER REPLACES. The restoring case is an empty list on a new
     * device, where add and replace are the same thing; the other case is a list
     * with work already on it, where replace destroys that work to serve a
     * convenience. This log is the only record of the walk and it lives in one
     * browser (§TWO TAPS TO WIPE) — so the import has no destructive mode at
     * all, and Clear stays the one control that can lose anything.
     *
     * IT READS THE HEADER, NOT THE COLUMN ORDER. The file went to a spreadsheet
     * and came back; columns get moved, hidden and added there, and a positional
     * parse would silently write the note into the status. Every cell is placed
     * by the label above it, an unrecognised column is dropped rather than
     * guessed, and a header that matches nothing fails LOUDLY instead of
     * importing a page of blank rows.
     *
     * A CELL MAY ONLY BECOME A VALUE THE CONFIG DECLARED. A status rung the
     * ladder does not contain lands BLANK rather than as a rung nothing can
     * advance, and a keyless computed column (the flag) is recognised only when
     * its cell is one of the declared flag values. Nothing here invents a field.
     *
     * AND THE SHEET IS WRITTEN IN LABELS WHILE THE ROW STORES VALUES. Half the
     * configs in the program keep `{v, label}` options — the row holds "gc" and
     * the column prints "GC super" through its own `value` function — so a
     * reader that wrote the cell back raw would fill the field with a label
     * nothing matches, and the chip for it would render unpicked. The gate
     * caught this on nine shipped pages, where the column that came back blank
     * was WHAT'S NEEDED, i.e. the entire point of the document. So a picked axis
     * resolves its cell through that field's own option list, in BOTH
     * directions, and a cell that is not one of its options is dropped rather
     * than guessed. It re-resolves in passes because one axis gates another (the
     * ask decides which sizes exist), and a single pass would read the gated
     * field against the previous row's gate.
     */
    function normLab(s) {
      return String(s == null ? "" : s)
        .replace(/[‘’ʼ]/g, "'").replace(/[“”]/g, '"')
        .replace(/[–—]/g, "-").replace(/\s+/g, " ").trim().toLowerCase();
    }
    /* WHICH DECLARED OPTION IS THIS CELL? Matches the label OR the stored value,
       because the two configs in this program that keep plain-string options
       have them identical and the ones that keep `{v, label}` print the label.
       `cur` is the half-built row, so a gated axis is asked against ITS OWN
       row's gate rather than against whatever the bar happens to be holding. */
    function optionValue(f, cell, cur) {
      var opts = optionsOf(f, cur) || [], k = normLab(cell);
      for (var i = 0; i < opts.length; i++) {
        var o = opts[i];
        var val = typeof o === "string" ? o : o.v;
        var lab = typeof o === "string" ? o : (o.label || o.v);
        if (normLab(lab) === k || normLab(val) === k) return val;
      }
      return null;
    }
    function importTsv(text) {
      var raw = String(text == null ? "" : text).replace(/\r\n?/g, "\n").split("\n");
      var cols = tsvCols(), i, j;
      var want = {};
      cols.forEach(function (c) { want[normLab(c.label)] = c; });

      /* FIND THE HEADER, because line 1 is the preamble sentence on most of
         these pages and a spreadsheet may have added rows above it. Best match
         wins, and one lone matching column is not a header — that is a data row
         that happens to repeat a label. */
      var hdr = -1, best = 0;
      for (i = 0; i < raw.length && i < 12; i++) {
        var cells = raw[i].split("\t"), hit = 0;
        for (j = 0; j < cells.length; j++) if (want[normLab(cells[j])]) hit++;
        if (hit > best) { best = hit; hdr = i; }
      }
      if (hdr < 0 || best < 2) return { added: 0, rows: 0, reason: "no-header" };

      var map = raw[hdr].split("\t").map(function (lab) { return want[normLab(lab)] || null; });
      var made = 0, seen = 0;
      for (i = hdr + 1; i < raw.length; i++) {
        if (!raw[i].trim()) continue;
        seen++;
        var cells2 = raw[i].split("\t");
        var v = {}, flag = "", any = false, pend = [];
        for (j = 0; j < map.length; j++) {
          var col = map[j]; if (!col) continue;                    // a column we do not own
          var cell = String(cells2[j] == null ? "" : cells2[j]).trim();
          if (!cell) continue;
          var f = col.key ? field(col.key) : null;
          if (f) {
            /* A PICKED AXIS IS RESOLVED, A TYPED ONE IS NOT. Free text is his
               own words and nothing may edit it (§SAFETY); a chip or a select
               holds one of a declared set, and the sheet holds that set's
               labels. Gated axes wait for the axis that gates them. */
            if (f.input === "select" || f.input === "chips") pend.push({ f: f, cell: cell });
            else { v[col.key] = cell; any = true; }
          } else if (!col.key && FLAGS.indexOf(cell) > -1) {
            flag = cell; any = true;
          }
        }
        var guard = 0;
        while (pend.length && guard++ < 4) {
          var still = [];
          for (j = 0; j < pend.length; j++) {
            var hit = optionValue(pend[j].f, pend[j].cell, v);
            if (hit == null) { still.push(pend[j]); continue; }
            if (cfg.statusKey && pend[j].f.key === cfg.statusKey && STATUS.indexOf(hit) === -1) continue;
            v[pend[j].f.key] = hit; any = true;
          }
          if (still.length === pend.length) break;                 // nothing moved: the rest are not options
          pend = still;
        }
        if (!any) continue;
        FIELDS.forEach(function (f) { if (v[f.key] == null) v[f.key] = ""; });
        /* A LEARNED AXIS IS LEARNED FROM THE RESTORE TOO. The self-building
           chips are what make the second row two taps; coming back to a restored
           list with no buttons on it is the tool he left, minus its speed. */
        FIELDS.forEach(function (f) {
          if (f.input !== "learn" || !v[f.key]) return;
          learned[f.key] = learned[f.key] || [];
          if (learned[f.key].indexOf(v[f.key]) === -1) learned[f.key].push(v[f.key]);
        });
        rows.push({ id: seq++, t: ++touch, values: v, flag: flag });
        made++;
      }
      if (made) { if (editingId != null) stopEditing(true); render(); persistNow(); }
      return { added: made, rows: seen, reason: made ? "" : (seen ? "no-values" : "no-rows") };
    }

    /* ── persistence ──────────────────────────────────────────────────────────
     * A walk-the-job tool: a man logs devices over an hour with the phone in one
     * hand, and iOS evicts a background tab inside that window. Losing the walk
     * is worse than the marked-up plan set it replaced. */
    var pTimer = null;
    function persist() {
      if (!cfg.persistKey) return;
      var extra = cfg.persistExtra ? cfg.persistExtra() : null;
      try {
        if (rows.length || extra || Object.keys(learned).length) {
          localStorage.setItem(cfg.persistKey, JSON.stringify({
            v: 1, seq: seq, touch: touch, copiedAt: copiedAt, sticky: sticky,
            learned: learned, groupKey: groupKey, extra: extra,
            rows: rows.map(function (r) { return { id: r.id, t: r.t, values: r.values, flag: r.flag }; })
          }));
        } else {
          // CLEAR MUST ACTUALLY CLEAR (§SCARS): with nothing to save the record
          // goes away, and the caller returns null from persistExtra when its own
          // state is untouched or the debounce writes it straight back.
          localStorage.removeItem(cfg.persistKey);
        }
      } catch (e) {}
    }
    function persistNow() { clearTimeout(pTimer); persist(); }
    function schedulePersist() { if (!cfg.persistKey) return; clearTimeout(pTimer); pTimer = setTimeout(persist, 250); }
    // A 250 ms debounce is not a save (§SCARS "the camera round-trip eats the
    // draft"): flush on the three events that actually precede an eviction.
    function flushPersist() { if (!cfg.persistKey) return; clearTimeout(pTimer); try { persist(); } catch (e) {} }
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flushPersist(); });
    window.addEventListener("pagehide", flushPersist);
    window.addEventListener("blur", flushPersist);

    function restore() {
      if (!cfg.persistKey) return false;
      var raw = null;
      try { raw = localStorage.getItem(cfg.persistKey); } catch (e) { return false; }
      if (!raw) return false;
      var p; try { p = JSON.parse(raw); } catch (e) { return false; }
      if (!p) return false;
      if (cfg.onRestoreExtra && p.extra) cfg.onRestoreExtra(p.extra);
      rows = (p.rows || []).filter(function (r) { return r && r.values; })
        .map(function (r, i) { return { id: r.id != null ? r.id : i + 1, t: r.t || 1, values: r.values, flag: r.flag || "" }; });
      seq = p.seq || rows.length + 1;
      rows.forEach(function (r) { if (r.id >= seq) seq = r.id + 1; if (r.t > touch) touch = r.t; });
      touch = Math.max(touch, p.touch || 1);
      copiedAt = p.copiedAt || 0;
      sticky = p.sticky || {};
      learned = p.learned || {};
      if (p.groupKey && GROUPS.filter(function (g) { return g.key === p.groupKey; }).length) groupKey = p.groupKey;
      FIELDS.forEach(function (f) { if (f.input === "select") paintSelect(f); });
      writeSticky(); render();
      return rows.length > 0;
    }

    function clearAll() {
      rows = []; seq = 1; touch = 1; copiedAt = 0; sticky = {}; learned = {}; editingId = null;
      FIELDS.forEach(function (f) { var el = ctl(f.key); if (el) el.value = ""; });
      var nb = bar.querySelector("#rlNext"); if (nb) { nb.hidden = true; nb.innerHTML = ""; }
      stopEditing(false);
      FIELDS.forEach(function (f) { if (f.input === "chips" || f.input === "learn") paintChips(f); });
      render(); persistNow();
    }

    /* ── THE WALK ─────────────────────────────────────────────────────────────
     * Opt-in via `cfg.walk`. Added at the fourth instance, from a working AV
     * pro's wish for a readout he could use with his hands full.
     *
     * A list on this page is COMPOSED sitting down and VERIFIED walking, and
     * only the first of those had a surface. Forty grouped rows on a 390px
     * phone, read at arm's length with a flashlight in the other hand and
     * gloves on, is a pinch-zoom and a lost place. So the walk is the same
     * rows, one at a time, in type you can read without looking hard, behind
     * two targets big enough to hit with a knuckle.
     *
     * IT PRODUCES NO NEW DOCUMENT, ON PURPOSE. It makes the document this page
     * already sends TRUE: "still open" is only worth sending if somebody laid
     * eyes on the list today, and the walk IS that act. `walk.onDone` hands the
     * page the counts and the page decides what to do with them.
     *
     * THE TWO BUTTONS ARE NOT SYMMETRIC AND MUST NOT BE.
     *   · The affirmative SETS the settled rung — it does not advance one step —
     *     so a double tap cannot walk a row past a rung nobody verified, and a
     *     man who taps twice has said the same true thing twice.
     *   · The negative NEVER INVENTS A RUNG, and on a row that has not reached
     *     the settled one it writes nothing at all — the only honest record of
     *     "I looked and it wasn't there" this page owns is that the row is STILL
     *     OPEN, and a "checked, absent" value is one no field here can carry
     *     (§SCARS "A DEFAULT IS A CLAIM"). But on a row that ALREADY carries the
     *     settled rung it must RETRACT it, one step down the declared ladder.
     *     Writing nothing there was the first version of this and it was wrong:
     *     a man standing in front of a row that says IN, tapping NOT YET, is
     *     telling you it is not in — and leaving it settled put that lie in the
     *     document, dropped him from the "still open" message he then sent, and
     *     told him at the end of a walk of pure NOT YET that everything was in.
     *     Down the ladder is not inventing; it is un-saying.
     *
     * IT WALKS scopedRows(), so the filters the page already has ARE the walk —
     * "still open, for the electrician" is Thursday morning and needs no new
     * control. The launcher says which scope it is about to walk, because a
     * button that silently walks a different set than the one he filtered is
     * the same class of lie as a document that counts rows it does not contain.
     *
     * EVERY CONTROL IS A REAL FOCUSABLE BUTTON AND EVERY ONE IS REACHABLE BY
     * KEY — arrows roam, Enter picks, Escape leaves, Tab is trapped. That is
     * plain keyboard operability, which this page owed anyway (§SCARS
     * "`aria-modal` is a promise, not a behaviour"). It is also the only input
     * model a screen with no pointer can offer, which is why it is worth having
     * even where nobody is holding a keyboard.
     *
     * THE OVERLAY IS BOUND `position:fixed; inset:0` AND NEVER `100vh` (§SCARS
     * "THE HARNESS CANNOT SEE WHAT ITS ENGINE DOES NOT DO", 2026-08-10): iOS
     * freezes `vh` to the large viewport while the glass shrinks under it, so a
     * vh-bound full-screen surface is built taller than the phone it is on and
     * every headless gate stays green about it. */
    var walkWrap = null, walkGo = null, walkIds = [], walkIx = 0, walkLock = null, walkPrev = null;

    function walkOn() { return !!(cfg.walk && cfg.statusKey && STATUS.length); }
    function walkDoneVal() { return cfg.statusDone || STATUS[STATUS.length - 1]; }
    function walkRowById(id) { return rows.filter(function (x) { return x.id === id; })[0] || null; }
    function walkScopeLabel() {
      var fds = filterDefs().map(function (f) { return f.label; }).filter(Boolean);
      return fds.length ? fds.join(" · ") : (cfg.walk.allLabel || "the whole list");
    }
    function walkGroupOf(r) {
      var g = (r.values[groupKey] || "").trim();
      if (!g) return cfg.ungroupedLabel || "NOT SET";
      return (cfg.groupName ? cfg.groupName(g, groupKey) : g) || g;
    }

    /* The launcher is engine territory for the same reason the row tap is: it is
     * a control over the list, not a piece of the page's layout. One config key
     * lights it up; no page has to grow a button it would then have to style. */
    function walkMountLauncher() {
      if (!walkOn() || !listEl || !listEl.parentNode) return;
      var wbar = document.createElement("div");   // NOT `bar` — that is the add/edit bar
      wbar.className = "rl-walkbar";
      walkGo = document.createElement("button");
      walkGo.type = "button";
      walkGo.className = "rl-walkgo";
      walkGo.addEventListener("click", walkOpen);
      wbar.appendChild(walkGo);
      listEl.parentNode.insertBefore(wbar, listEl);
    }
    function walkSyncLauncher() {
      if (!walkGo) return;
      var n = scopedRows().length;
      var noun = n === 1 ? (cfg.noun || "row") : (cfg.nounPlural || "rows");
      walkGo.parentNode.hidden = !rows.length;
      walkGo.disabled = !n;
      walkGo.innerHTML = '<b>' + esc(cfg.walk.label || "Walk it") + "</b><span>"
        + (n ? n + " " + esc(noun) + " · " + esc(walkScopeLabel()) : esc(cfg.walk.emptyScope || "nothing in this scope"))
        + "</span>";
    }

    function walkBuild() {
      walkWrap = document.createElement("div");
      walkWrap.className = "rl-walk";
      walkWrap.hidden = true;
      walkWrap.setAttribute("role", "dialog");
      walkWrap.setAttribute("aria-modal", "true");
      walkWrap.setAttribute("aria-label", cfg.walk.label || "Walk the list");
      walkWrap.addEventListener("click", walkClick);
      document.body.appendChild(walkWrap);
    }

    function walkPaint() {
      var total = walkIds.length, r = null;
      /* A row can be deleted from the pencil sheet between two taps of a walk.
       * Skipping it is right; throwing on it would strand him mid-list. */
      while (walkIx < total && !(r = walkRowById(walkIds[walkIx]))) walkIx++;
      if (walkIx >= total) return walkPaintDone();

      var main = cfg.rowMain ? cfg.rowMain(r.values) : (r.values[FIELDS[0].key] || "");
      var sub = cfg.rowSub ? cfg.rowSub(r.values) : "";
      var st = r.values[cfg.statusKey] || "";
      var set = st === walkDoneVal();
      var noteKey = cfg.walk.noteKey;
      var note = noteKey ? (r.values[noteKey] || "") : "";

      walkWrap.innerHTML =
        '<div class="rl-wk-top">'
        + '<span class="rl-wk-ct">' + (walkIx + 1) + " <i>/</i> " + total + "</span>"
        + '<span class="rl-wk-scope">' + esc(walkScopeLabel()) + "</span>"
        + '<button type="button" class="rl-wk-x" data-wk="quit">Close</button>'
        + "</div>"
        + '<div class="rl-wk-prog"><i style="width:' + Math.round((walkIx / total) * 100) + '%"></i></div>'
        + '<div class="rl-wk-body"><div class="rl-wk-card">'
        + '<span class="rl-wk-grp">' + esc(walkGroupOf(r)) + "</span>"
        + '<b class="rl-wk-main">' + esc(main || "—") + "</b>"
        + (sub ? '<span class="rl-wk-sub">' + esc(sub) + "</span>" : "")
        + '<span class="rl-wk-st' + (set ? " is-set" : (st ? "" : " none")) + '">'
        + esc(st || cfg.walk.blankLabel || "not started") + "</span>"
        + (r.flag ? '<span class="rl-wk-flag">' + esc(r.flag) + "</span>" : "")
        + (note ? '<span class="rl-wk-note">' + esc(note) + "</span>" : "")
        + "</div></div>"
        + (noteKey
            ? '<div class="rl-wk-nrow" hidden><input type="text" class="rl-wk-nin" value="' + esc(note)
              + '" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="'
              + esc(cfg.walk.notePlaceholder || "two words about this one") + '"></div>'
            : "")
        + '<div class="rl-wk-acts">'
        + '<button type="button" class="rl-wk-yes' + (set ? " is-set" : "") + '" data-wk="yes">'
        + esc(cfg.walk.advance || ("Mark " + walkDoneVal())) + "</button>"
        + '<button type="button" class="rl-wk-no" data-wk="no">' + esc(cfg.walk.hold || "Not yet") + "</button>"
        + "</div>"
        + '<div class="rl-wk-mini">'
        + '<button type="button" class="rl-wk-m" data-wk="back"' + (walkIx ? "" : " disabled") + ">&#8592; Back</button>"
        + (noteKey ? '<button type="button" class="rl-wk-m" data-wk="note">Note</button>' : "")
        + (walkLock ? '<span class="rl-wk-awake">screen held awake</span>' : "")
        + "</div>";
      walkFocusPrimary();
    }

    /* The end of a walk is the only place this surface talks about the list as a
     * whole, and it says only what it watched happen: how many he walked, how
     * many carry the settled rung now, how many do not. No rate, no percentage
     * of a denominator nobody entered. */
    function walkPaintDone() {
      var scope = walkIds.map(walkRowById).filter(Boolean);
      var doneN = scope.filter(function (r) { return r.values[cfg.statusKey] === walkDoneVal(); }).length;
      var openN = scope.length - doneN;
      walkWrap.innerHTML =
        '<div class="rl-wk-top">'
        + '<span class="rl-wk-ct">' + scope.length + " <i>/</i> " + scope.length + "</span>"
        + '<span class="rl-wk-scope">' + esc(walkScopeLabel()) + "</span>"
        + '<button type="button" class="rl-wk-x" data-wk="quit">Close</button>'
        + "</div>"
        + '<div class="rl-wk-prog"><i style="width:100%"></i></div>'
        + '<div class="rl-wk-body"><div class="rl-wk-end">'
        + "<b>" + esc(cfg.walk.endTitle || "Walk done") + "</b>"
        + '<span class="rl-wk-endn"><i>' + doneN + "</i>" + esc(" " + (cfg.walk.endDone || ("now " + walkDoneVal().toLowerCase()))) + "</span>"
        + '<span class="rl-wk-endn' + (openN ? " is-open" : "") + '"><i>' + openN + "</i>"
        + esc(" " + (cfg.walk.endOpen || "still open")) + "</span>"
        + "</div></div>"
        + '<div class="rl-wk-acts rl-wk-acts1">'
        + (openN && cfg.walk.onDone
            ? '<button type="button" class="rl-wk-yes" data-wk="finish">' + esc(cfg.walk.doneLabel || "Send what's still open") + "</button>"
            : '<button type="button" class="rl-wk-yes" data-wk="quit">' + esc(cfg.walk.closeLabel || "Back to the list") + "</button>")
        + "</div>"
        + '<div class="rl-wk-mini">'
        + '<button type="button" class="rl-wk-m" data-wk="back">&#8592; Back</button>'
        + (openN && cfg.walk.onDone ? '<button type="button" class="rl-wk-m" data-wk="quit">Just close it</button>' : "")
        + "</div>";
      walkFocusPrimary();
    }

    function walkFocusPrimary() {
      var y = walkWrap.querySelector('[data-wk="yes"],[data-wk="finish"]') || walkWrap.querySelector("button");
      if (y) { try { y.focus(); } catch (e) {} }
    }

    function walkClick(e) {
      var b = e.target && e.target.closest ? e.target.closest("[data-wk]") : null;
      if (!b) return;
      var a = b.getAttribute("data-wk");
      if (a === "quit") return walkClose();
      if (a === "back") { if (walkIx > 0) walkIx--; return walkPaint(); }
      if (a === "note") {
        var row = walkWrap.querySelector(".rl-wk-nrow");
        if (!row) return;
        row.hidden = !row.hidden;
        if (!row.hidden) { var i = row.querySelector("input"); if (i) { i.focus(); walkBindNote(i); } }
        return;
      }
      if (a === "yes") {
        var r = walkRowById(walkIds[walkIx]);
        /* SET, never advance — see the header. Idempotent by construction. */
        if (r && r.values[cfg.statusKey] !== walkDoneVal()) {
          r.values[cfg.statusKey] = walkDoneVal();
          r.t = ++touch;
          persistNow();
        }
        walkIx++; return walkPaint();
      }
      if (a === "no") {
        var nr = walkRowById(walkIds[walkIx]);
        /* RETRACT, never invent — see the header. Only ever one step DOWN the
         * ladder the config declared, and only from the settled rung. */
        if (nr && nr.values[cfg.statusKey] === walkDoneVal()) {
          var di = STATUS.indexOf(walkDoneVal());
          nr.values[cfg.statusKey] = di > 0 ? STATUS[di - 1] : "";
          nr.t = ++touch;
          persistNow();
        }
        walkIx++; return walkPaint();
      }
      if (a === "finish") {
        var scope = walkIds.map(walkRowById).filter(Boolean);
        var doneN = scope.filter(function (x) { return x.values[cfg.statusKey] === walkDoneVal(); }).length;
        walkClose();
        if (cfg.walk.onDone) cfg.walk.onDone({ walked: scope.length, done: doneN, open: scope.length - doneN });
      }
    }

    function walkBindNote(input) {
      if (input.getAttribute("data-bound")) return;
      input.setAttribute("data-bound", "1");
      input.addEventListener("input", function () {
        var r = walkRowById(walkIds[walkIx]);
        if (!r) return;
        r.values[cfg.walk.noteKey] = input.value;
        r.t = ++touch;
        schedulePersist();
      });
    }

    function walkKey(e) {
      if (!walkWrap || walkWrap.hidden) return;
      if (e.key === "Escape") {
        e.preventDefault();
        /* Escape means "close the thing I opened last". Inside the note that is
         * the note row, not the walk — closing the whole surface because he
         * dismissed a text field is the control overshooting its own scope. */
        var nrow = walkWrap.querySelector(".rl-wk-nrow");
        if (nrow && !nrow.hidden && document.activeElement === nrow.querySelector("input")) {
          nrow.hidden = true;
          return walkFocusPrimary();
        }
        return walkClose();
      }
      /* THE NOTE FIELD IS IN THE MARKUP EVEN WHILE IT IS CLOSED, so a naive ring
       * hands Tab a `display:none` input, `focus()` quietly does nothing, and
       * focus falls out of a dialog that advertises `aria-modal` — the trap the
       * book already has a scar for, rebuilt one layer down. Anything under a
       * `[hidden]` ancestor is not in the ring. */
      var f = [].slice.call(walkWrap.querySelectorAll("button:not([disabled]),input"))
        .filter(function (el) { return !el.closest("[hidden]"); });
      if (!f.length) return;
      var i = f.indexOf(document.activeElement);
      if (e.key === "Tab") {
        e.preventDefault();
        return f[e.shiftKey ? (i <= 0 ? f.length - 1 : i - 1) : (i < 0 || i === f.length - 1 ? 0 : i + 1)].focus();
      }
      /* Arrows roam the controls — the pointerless input model. Inside a text
       * field they belong to the caret, so they are left alone there. */
      if (/^Arrow(Left|Right|Up|Down)$/.test(e.key)) {
        if (document.activeElement && document.activeElement.tagName === "INPUT") return;
        e.preventDefault();
        var fwd = e.key === "ArrowRight" || e.key === "ArrowDown";
        return f[i < 0 ? 0 : (fwd ? (i + 1) % f.length : (i - 1 + f.length) % f.length)].focus();
      }
    }

    /* Held only while the walk is open, released on the way out, and never
     * ANNOUNCED unless the request actually resolved — a line promising an awake
     * screen on a browser that has no such API is the page claiming a capability
     * it does not hold (§SCARS "A DEFAULT IS A CLAIM"). */
    function walkAwakeLine(on) {
      if (!walkWrap) return;
      var m = walkWrap.querySelector(".rl-wk-mini"), el = walkWrap.querySelector(".rl-wk-awake");
      if (!on) { if (el && el.parentNode) el.parentNode.removeChild(el); return; }
      if (!m || el || walkWrap.hidden) return;
      el = document.createElement("span");
      el.className = "rl-wk-awake";
      el.textContent = "screen held awake";
      m.appendChild(el);
    }
    function walkWake() {
      try {
        if (!navigator.wakeLock || !navigator.wakeLock.request) return;
        navigator.wakeLock.request("screen").then(function (s) {
          /* THE WALK CAN CLOSE WHILE THIS PROMISE IS STILL IN FLIGHT. Storing the
           * sentinel then would hold the screen awake with no walk on the glass,
           * and walkClose has already returned — so nothing would ever release
           * it, and the next open would orphan this one for the page's life. */
          if (!walkWrap || walkWrap.hidden) { try { s.release(); } catch (e) {} return; }
          walkLock = s;
          /* THE UA TAKES IT BACK ON ITS OWN — the tab hides, the screen sleeps.
           * The line goes with it. A claim that outlives the thing it claims is
           * the page asserting a capability it no longer holds. */
          s.addEventListener("release", function () { walkLock = null; walkAwakeLine(false); });
          walkAwakeLine(true);
        }, function () {});
      } catch (e) {}
    }
    function walkVis() {
      if (document.visibilityState === "visible" && walkWrap && !walkWrap.hidden && !walkLock) walkWake();
    }

    function walkOpen() {
      if (!walkOn()) return;
      /* AN OPEN PENCIL SHEET WOULD SILENTLY REVERT THE WHOLE WALK. The bar holds
       * a PHOTOGRAPH of the row taken when the pencil opened, and commit() writes
       * that photograph back wholesale — so Save, tapped after a walk, restores
       * the status every row had before he walked out and looked. Close the
       * editor first: tapping "Walk it" is leaving the edit, exactly as tapping
       * anywhere else is. (The same wholesale write is reachable from the tap
       * ladder and is older than this surface — §SCARS names it and its repro.) */
      if (editingId != null) stopEditing(true);
      walkIds = scopedRows().map(function (r) { return r.id; });
      if (!walkIds.length) return;
      walkIx = 0;
      if (!walkWrap) walkBuild();
      walkPrev = document.activeElement;
      walkWrap.hidden = false;
      document.documentElement.classList.add("rl-walking");
      walkPaint();
      walkWake();
      document.addEventListener("visibilitychange", walkVis);
      /* ON THE DOCUMENT, not on the overlay: the biggest thing on this screen is
       * the row itself, which is not focusable, so one tap on it moves focus to
       * <body> and a listener bound to the overlay stops hearing anything —
       * including the Escape the header promises. */
      document.addEventListener("keydown", walkKey, true);
    }
    function walkClose() {
      if (!walkWrap || walkWrap.hidden) return;
      walkWrap.hidden = true;
      document.documentElement.classList.remove("rl-walking");
      document.removeEventListener("visibilitychange", walkVis);
      document.removeEventListener("keydown", walkKey, true);
      if (walkLock) { try { walkLock.release(); } catch (e) {} walkLock = null; }
      persistNow(); render();
      /* The launcher he came in from may have just gone DISABLED — a walk that
       * settled every row in a "still open" scope empties that scope — and
       * focus() on a disabled control is a silent no-op that drops him on
       * <body>. Fall back to the thing the walk was for. */
      var back = (walkPrev && walkPrev.isConnected && !walkPrev.disabled) ? walkPrev
        : (copyBtn && !copyBtn.disabled ? copyBtn : null);
      if (back && back.focus) { try { back.focus(); } catch (e) {} }
    }

    buildBar();
    walkMountLauncher();
    render();
    if (copyBtn) copyBtn.addEventListener("click", function () {
      copyText(text(), copyBtn, cfg.onFlash);
      copiedAt = touch;               // everything after this is the next delta
      persistNow(); render();
    });
    if (tsvBtn) tsvBtn.addEventListener("click", function () { copyText(tsv(), tsvBtn, cfg.onFlash); });

    /* THE RESTORE MOUNTS ITSELF, on every page that already offers the copy.
     * The claim it repairs is printed on twenty pages across nine trades, and a
     * capability that needs twenty pages edited to appear is a capability
     * nineteen of them will be missing the next time somebody counts. So the
     * engine builds it wherever the spreadsheet button already is — no markup,
     * no config, no page to forget. `cfg.importBox` overrides the position for a
     * page whose layout wants it somewhere else; `cfg.importOff` opts out.
     * FOLDED SHUT: a man doing today's walk never needs it, and an open textarea
     * above his list would cost every page vertical space for a control used on
     * the day the phone died. */
    var impBox = cfg.importBox ? byId(cfg.importBox) : null;
    if (!impBox && tsvBtn && !cfg.importOff) {
      var anchor = previewEl || tsvBtn.parentNode;
      if (anchor && anchor.parentNode) {
        impBox = document.createElement("div");
        anchor.parentNode.insertBefore(impBox, anchor.nextSibling);
      }
    }
    if (impBox && !cfg.importOff) {
      var nP = cfg.nounPlural || "rows";
      impBox.innerHTML =
        '<details class="rl-imp"><summary class="rl-imp-sum">Put a saved copy back</summary>'
        + '<div class="rl-imp-body">'
        + '<p class="rl-imp-note">Paste a <b>spreadsheet copy</b> you saved earlier &mdash; the whole thing, including the row of column headings &mdash; and the ' + esc(nP)
        + ' come back onto this list. It <b>adds</b> to what is here; it never replaces it, so nothing on screen can be lost by pasting.</p>'
        + '<textarea class="rl-imp-ta" id="rlImpTa" rows="4" placeholder="paste the spreadsheet copy here" autocapitalize="none" autocorrect="off" spellcheck="false"></textarea>'
        + '<div class="rl-imp-act"><button type="button" class="rl-mini" id="rlImpGo">Put it back</button>'
        + '<span class="rl-imp-say" id="rlImpSay"></span></div>'
        + "</div></details>";
      var impTa = impBox.querySelector("#rlImpTa"), impSay = impBox.querySelector("#rlImpSay");
      impBox.querySelector("#rlImpGo").addEventListener("click", function () {
        var res = importTsv(impTa.value);
        /* IT SAYS WHAT IT DID, AND IT SAYS WHY IT DID NOTHING. A restore that
           silently no-ops on a man holding the only copy of his walk is the
           worst failure this control has, so every refusal names the fix. */
        if (res.added) {
          impSay.className = "rl-imp-say ok";
          impSay.textContent = "Put " + res.added + " " + (res.added === 1 ? (cfg.noun || "row") : nP) + " back.";
          impTa.value = "";
        } else {
          impSay.className = "rl-imp-say bad";
          impSay.textContent = res.reason === "no-header"
            ? "Couldn't find the row of column headings — paste the whole spreadsheet copy, not just the rows."
            : (res.reason === "no-rows" ? "Nothing under the headings to put back."
              : "Found the headings, but none of those rows had anything this page keeps.");
        }
      });
    }

    document.addEventListener("av:ready", function () { render(); });

    return {
      rows: function () { return rows.slice(); },
      count: function () { return rows.length; },
      newCount: function () { return deltaRows().length; },
      flaggedCount: function () { return flagged().length; },
      text: text, tsv: tsv, render: render, restore: restore, clearAll: clearAll,
      persist: persistNow, schedulePersist: schedulePersist,
      addRange: addRange, addPasted: addPasted, applyValues: applyValues, importTsv: importTsv,
      setGroup: function (k) { if (GROUPS.filter(function (g) { return g.key === k; }).length) { groupKey = k; render(); persistNow(); } },
      group: function () { return groupKey; },
      setDeltaOnly: function (b) { deltaOnly = !!b; render(); },
      deltaOnly: function () { return deltaOnly; },
      setFilter: function (k) { filterKeys = k ? (Array.isArray(k) ? k.slice() : [k]) : []; render(); },
      filter: function () { return filterKeys.slice(); },
      docCount: function () { return docRows().length; },
      copy: function () { if (copyBtn) copyBtn.click(); },
      copyTsv: function () { copyText(tsv(), tsvBtn, cfg.onFlash); }
    };
  }

  window.RowLog = { mount: mount, esc: esc, todayStr: todayStr, copyText: copyText, nextIdent: nextIdent };
})();
