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
        rows.forEach(function (r) { if (r.id === editingId) { r.values = v; r.t = ++touch; } });
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
      bar.querySelector("#rlEditing").hidden = false;
      bar.querySelector("#rlAdd").textContent = "Save";
      bar.querySelector("#rlNext").hidden = true;
      bar.classList.add("is-editing");
      paintFlags(); warnDuplicate(); render();
      try { bar.scrollIntoView({ block: "nearest" }); } catch (e) {}
    }
    function stopEditing(restore) {
      editingId = null;
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
    function tsv() {
      var cols = cfg.tsvColumns || FIELDS.map(function (f) { return { label: f.label, key: f.key }; });
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

    buildBar();
    render();
    if (copyBtn) copyBtn.addEventListener("click", function () {
      copyText(text(), copyBtn, cfg.onFlash);
      copiedAt = touch;               // everything after this is the next delta
      persistNow(); render();
    });
    if (tsvBtn) tsvBtn.addEventListener("click", function () { copyText(tsv(), tsvBtn, cfg.onFlash); });
    document.addEventListener("av:ready", function () { render(); });

    return {
      rows: function () { return rows.slice(); },
      count: function () { return rows.length; },
      newCount: function () { return deltaRows().length; },
      flaggedCount: function () { return flagged().length; },
      text: text, tsv: tsv, render: render, restore: restore, clearAll: clearAll,
      persist: persistNow, schedulePersist: schedulePersist,
      addRange: addRange, addPasted: addPasted,
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
