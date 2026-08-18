/* FIELD TOOLKIT — SHAPE #2 ENGINE: THE NOTE.
 *
 * av/AV_SOCIETY.md §THE THREE SHAPES: "THE NOTE — an ordered set of short fields,
 * one of which is the impact line everyone omits, an optional forget-list
 * checklist, and a fixed closing ask the receiver can reply to. The directed-work
 * ticket, the shutdown notice and the field RFI are all this one widget."
 *
 * And: "When you build the second instance of a shape, extract the engine. Two
 * instances is where a shape is provable; one is over-abstraction and five is
 * five forks."
 *
 * Shape #2 had exactly ONE live instance — hvac/repair-recommendation.html — and
 * the private ladder named the second one: the directed-work ticket, which is the
 * #1 rung on electrical and low-voltage, #2 on plumbing, #4 on GC, #6 on HVAC and
 * #7 on AV. Six trades, one widget, five different words for it. Forking that six
 * times is exactly the failure this file exists to prevent, so the engine is
 * extracted HERE, at the second instance, and all six ship as configs.
 *
 * THE DIFFERENCE FROM SHAPE #1's ENGINE: shape #1's caller keeps its own HTML and
 * asks the engine to drive it. That works when there are two callers. At six it
 * does not — six hand-written field blocks drift within a week. So this engine
 * RENDERS: the caller declares SECTIONS and FIELDS as data, the engine builds the
 * DOM, owns the state, assembles the document, persists the draft and copies it.
 *
 * WHAT THE CALLER OWNS, always:
 *   · every WORD. The note's whole value is that it speaks one trade's language —
 *     a super who reads "Please provide authorization for the additional scope"
 *     knows in one line that no tradesman wrote it. The engine never writes copy.
 *   · the FIELD LIST and its order. What is load-bearing on an electrical T&M
 *     ticket is not what is load-bearing on a low-voltage one (theirs is nearly
 *     always caused by another trade), and the order IS the argument.
 *   · the trade's VOCABULARY (items.js) — reason chips, classifications, the
 *     forget-list.
 *   · the closing ask, which is fixed text, never a field.
 *
 * WHAT THE ENGINE OWNS (the parts that were duplicated in the first instance and
 * would drift the moment a second existed):
 *   field rendering for nine kinds · the neutral-option rule (a default is a
 *   claim) · segment re-tap-to-unpick · tick `sub` riding into the document ·
 *   the IMPACT block with append-only chips and its clock · repeatable ROWS ·
 *   the self-stamping clock · sticky fields that survive Clear · the live
 *   preview and count · draft persistence INCLUDING the flush-on-the-way-out
 *   (a man who loses a draft to the camera app does not come back) · Clear that
 *   actually clears · copy WITH the non-secure-context fallback · and document
 *   assembly that survives a text message.
 *
 * NOT here, deliberately: any computed value, rate, total, price, duration
 * arithmetic or "in range" of any kind (av/AV_SOCIETY.md §SAFETY). The user
 * states the facts; the engine only makes sure they arrive with their labels
 * attached and nothing he did not say gets added.
 *
 * Load AFTER the trade config and registry, alongside the shared runtime:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="items.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/note.js"></script>
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }
  function byId(x) { return typeof x === "string" ? document.getElementById(x) : x; }
  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function trim(v) { return String(v == null ? "" : v).trim(); }

  /* A NEUTRAL option leads with an em-dash and means NOBODY PICKED IT. A value
   * nobody picked must never reach the receiver — on a directed-work ticket an
   * unpicked default becomes a claim the tradesman never made, and he is the one
   * who has to defend it. (§SCARS — a default is a claim.) */
  function isNone(v) { return !v || String(v).charAt(0) === "—"; }
  function picked(v) { return isNone(trim(v)) ? "" : trim(v); }

  /* The DATE is self-aware — the shared runtime resolves it from public sources
   * because a job-site phone or tablet clock can be flat wrong, and a directed-work
   * ticket dated wrong is worth nothing. The TIME OF DAY comes off the device: it
   * is the best available, and it is what he would have written on the tag anyway. */
  function todayStr() {
    return (window.Toolkit && window.Toolkit.todayStr)
      ? window.Toolkit.todayStr()
      : new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }
  function stampNow() {
    var t = "";
    try {
      t = new Date().toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    } catch (e) { t = ""; }
    return t ? (todayStr() + ", " + t) : todayStr();
  }

  /* Copy that survives a job site: the async Clipboard API needs a secure context,
   * and a browser on a site tablet behind a captive portal may not have one.
   * Failing silently there is the whole product broken. */
  function copyText(text, btn, label, failLabel) {
    function flash(msg) {
      if (!btn) return;
      var was = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", was);
      btn.textContent = msg;
      setTimeout(function () { btn.textContent = btn.getAttribute("data-label"); }, 1800);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", "");
      ta.style.position = "fixed"; ta.style.top = "-1000px";
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      flash(ok ? (label || "Copied. Go send it.") : (failLabel || "Select it and copy"));
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { flash(label || "Copied. Go send it."); }, fallback);
    } else fallback();
  }

  /* ── document assembly ─────────────────────────────────────────────────────
   * NO COLUMN ALIGNMENT, on purpose (carried from the first instance). A padded
   * label column looks tidy in a monospace preview and turns to ragged mush the
   * moment it lands in a text message, which is the only place this document ever
   * goes. `Label: value` survives every font. Headings are ALL CAPS on their own
   * line — the one piece of formatting that is proportional-font proof. */
  function joinDot(a) { return a.filter(Boolean).join("  ·  "); }

  function mount(cfg) {
    var form = byId(cfg.form || "form");
    if (!form) return null;

    var state = {};          // fieldId -> value (strings), plus rows arrays
    var nodes = {};          // fieldId -> {kind, def, read(), write(v), clear()}
    var order = [];          // fieldIds in render order
    var sections = [];       // {def, node, fieldIds}
    var stamped = false;     // has the self-filling clock fired this session

    var STICKY_KEY = cfg.key + ".me";
    var DRAFT_KEY = cfg.key;

    /* ── field builders ────────────────────────────────────────────────────── */

    function wrapField(def, control, extraCls) {
      var f = el("div", "f" + (def.span === false ? "" : " span2") + (extraCls ? " " + extraCls : ""));
      /* THE FIELD ID REACHES THE DOM so a gate can drive this page by the name
       * the config uses instead of by counting inputs or matching label prose.
       * Matching on words means a gate silently stops testing a field the day
       * somebody improves its label — which is the same class of drift as a
       * hand-kept watch list, one layer out. */
      if (def.id) f.setAttribute("data-f", def.id);
      if (def.label) {
        var lab = el("label");
        lab.appendChild(document.createTextNode(def.label + " "));
        if (def.hint) { var i = el("i", null, def.hint); lab.appendChild(i); }
        f.appendChild(lab);
      }
      f.appendChild(control);
      return f;
    }

    /* A phone destroys a model number, a panel tag or a drawing reference:
     * autocorrect turns it into an English word and that is the moment a man
     * closes a form for good. `caps:true` on any field that carries an identifier. */
    function harden(inp, def) {
      inp.setAttribute("autocomplete", "off");
      if (def.caps) {
        inp.setAttribute("autocapitalize", "characters");
        inp.setAttribute("autocorrect", "off");
        inp.setAttribute("spellcheck", "false");
      }
    }

    function buildText(def) {
      var inp = el("input");
      inp.type = def.numeric ? "text" : "text";
      if (def.numeric) inp.setAttribute("inputmode", "decimal");
      if (def.ph) inp.placeholder = def.ph;
      harden(inp, def);
      nodes[def.id] = {
        kind: "text", def: def, elem: inp,
        read: function () { return trim(inp.value); },
        write: function (v) { inp.value = v == null ? "" : v; },
        clear: function () { inp.value = ""; }
      };
      return wrapField(def, inp);
    }

    /* A REAL DATE, BECAUSE "TOMORROW" IS NOT ONE. The receiving end of every
     * access ask this engine now writes ranks a non-date FIRST among the things
     * that cost it a day: a text that says "tomorrow night" is read at 7am the
     * next morning and is already wrong, and "8/19" from a man in a truck can
     * arrive as 19/8. So the control is the phone's own date picker and the
     * document prints the WEEKDAY with it — the receiver checks a calendar, and
     * a weekday that disagrees with the number is the one typo he will catch.
     * State keeps the raw ISO so it restores; only the document sees the words. */
    function fmtDate(v) {
      var p = String(v || "").split("-");
      if (p.length !== 3) return trim(v);
      var d = new Date(+p[0], +p[1] - 1, +p[2]);
      if (isNaN(d.getTime())) return trim(v);
      return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
    }

    function buildDate(def) {
      var inp = el("input");
      inp.type = "date";
      harden(inp, def);
      nodes[def.id] = {
        kind: "date", def: def, elem: inp,
        read: function () { return trim(inp.value); },
        write: function (v) { inp.value = v == null ? "" : v; },
        clear: function () { inp.value = ""; },
        docValue: function () { return fmtDate(inp.value); }
      };
      return wrapField(def, inp);
    }

    function buildArea(def) {
      var ta = el("textarea");
      ta.rows = def.rows || 2;
      if (def.ph) ta.placeholder = def.ph;
      harden(ta, def);
      nodes[def.id] = {
        kind: "area", def: def, elem: ta,
        read: function () { return trim(ta.value); },
        write: function (v) { ta.value = v == null ? "" : v; },
        clear: function () { ta.value = ""; }
      };
      return wrapField(def, ta);
    }

    function buildSelect(def) {
      var s = el("select");
      (def.options || []).forEach(function (o) {
        var v = typeof o === "string" ? o : o.v;
        var opt = el("option", null, v);
        opt.value = v;
        s.appendChild(opt);
      });
      nodes[def.id] = {
        kind: "select", def: def, elem: s,
        read: function () { return picked(s.value); },
        write: function (v) { if (v != null) s.value = v; },
        clear: function () { s.selectedIndex = 0; }
      };
      return wrapField(def, s);
    }

    /* SEGMENTS: never more than 5 or the row wraps into a wall and ticking stops
     * beating typing (§SCARS — the 6-option ceiling binds the moment an axis is
     * rendered as chips or segments instead of a select). Tap the picked one again
     * to UN-pick it: nothing here is pre-selected, so nothing may be un-un-pickable. */
    function buildSeg(def) {
      var box = el("div", "seg" + (def.hotable === false ? "" : " hotseg"));
      var cur = "";
      (def.options || []).forEach(function (o) {
        var v = typeof o === "string" ? o : o.v;
        var b = el("button", null, v);
        b.type = "button";
        b.setAttribute("data-v", v);
        if (o && o.hot) b.setAttribute("data-hot", "1");
        b.addEventListener("click", function () {
          cur = (cur === v) ? "" : v;
          Array.prototype.forEach.call(box.children, function (c) {
            c.classList.toggle("on", c.getAttribute("data-v") === cur);
          });
          render();
        });
        box.appendChild(b);
      });
      nodes[def.id] = {
        kind: "seg", def: def, elem: box,
        read: function () { return cur; },
        docValue: function () {
          for (var i = 0; i < (def.options || []).length; i++) {
            var o = def.options[i];
            if ((typeof o === "string" ? o : o.v) === cur) return (o && o.doc) || cur;
          }
          return cur;
        },
        write: function (v) {
          if (!v) return;
          var b = box.querySelector('button[data-v="' + String(v).replace(/"/g, '\\"') + '"]');
          if (b) b.click();
        },
        clear: function () {
          cur = "";
          Array.prototype.forEach.call(box.children, function (c) { c.classList.remove("on"); });
        }
      };
      return wrapField(def, box);
    }

    /* PICK — a single choice out of MORE than five, rendered as chips that wrap
     * instead of a segmented row that turns into a wall (§SCARS — the 6-option
     * ceiling binds the moment an axis is rendered as segments). Same semantics as
     * a segment otherwise: nothing pre-selected, tap the picked one again to
     * un-pick. It exists because the single highest-value axis on a directed-work
     * ticket — WHO DIRECTED IT — has seven or eight real answers in most trades
     * (AV alone gets directed by the GC super, the GC's PM, the owner's IT, the
     * end user standing in the room, the consultant, facilities and the EC's
     * foreman), and which seat he sits in decides where the extra even goes. */
    function buildPick(def) {
      var box = el("div", "pick");
      var cur = "";
      (def.options || []).forEach(function (o) {
        var v = typeof o === "string" ? o : o.v;
        var b = el("button", null, v);
        b.type = "button";
        b.setAttribute("data-v", v);
        if (o && o.hot) b.setAttribute("data-hot", "1");
        b.addEventListener("click", function () {
          cur = (cur === v) ? "" : v;
          Array.prototype.forEach.call(box.children, function (c) {
            c.classList.toggle("on", c.getAttribute("data-v") === cur);
          });
          render();
        });
        box.appendChild(b);
      });
      nodes[def.id] = {
        kind: "pick", def: def, elem: box,
        read: function () { return cur; },
        docValue: function () {
          for (var i = 0; i < (def.options || []).length; i++) {
            var o = def.options[i];
            if ((typeof o === "string" ? o : o.v) === cur) return (o && o.doc) || cur;
          }
          return cur;
        },
        write: function (v) {
          if (!v) return;
          var b = box.querySelector('button[data-v="' + String(v).replace(/"/g, '\\"') + '"]');
          if (b) b.click();
        },
        clear: function () {
          cur = "";
          Array.prototype.forEach.call(box.children, function (c) { c.classList.remove("on"); });
        }
      };
      return wrapField(def, box);
    }

    /* TICK LISTS — the forget-list. The `sub` goes into the DOCUMENT, not just onto
     * the screen: on the first instance, "Boom / man lift" without "has to be
     * rented" was the cost signal deleted. */
    function buildTicks(def) {
      var ul = el("ul", "ticks");
      (def.options || []).forEach(function (it) {
        var name = typeof it === "string" ? it : it.name;
        /* `.sub` ON A STRING IS NOT undefined — IT IS String.prototype.sub, the
           legacy <sub> wrapper, and it is TRUTHY. This branch has always claimed
           to accept a plain string (the line above proves it), and every caller
           for eight trades happened to pass {name, sub} objects, so the string
           path was never walked until trade #9 did. It rendered the literal text
           "function sub() { [native code] }" beside every option on the page AND
           inside the copied message a client receives. Ask for the object before
           asking for the property. */
        var sub = (it && typeof it === "object" && it.sub) || "";
        var li = el("li");
        var lab = el("label");
        var cb = el("input");
        cb.type = "checkbox";
        cb.setAttribute("data-name", name);
        cb.addEventListener("change", render);
        lab.appendChild(cb);
        lab.appendChild(el("span", "nm", name));
        if (sub) lab.appendChild(el("span", "sb", sub));
        li.appendChild(lab);
        ul.appendChild(li);
      });
      function names() {
        return Array.prototype.slice.call(ul.querySelectorAll("input:checked"))
          .map(function (cb) { return cb.getAttribute("data-name"); });
      }
      nodes[def.id] = {
        kind: "ticks", def: def, elem: ul,
        read: names,
        docLines: function () {
          return names().map(function (nm) {
            for (var i = 0; i < (def.options || []).length; i++) {
              var it = def.options[i];
              if ((typeof it === "string" ? it : it.name) === nm) {
                /* `doc` on a tick option replaces the WHOLE printed line — same
                   contract seg and pick have always had. First use: a bilingual
                   page printing "ES (EN)" so the receiver up the chain can read
                   what the sender ticked. Absent, nothing changes. */
                if (it && typeof it === "object" && it.doc) return it.doc;
                /* Same String.prototype.sub trap as buildTicks above — this is
                   the copy path, where it reached the client. */
                return nm + (it && typeof it === "object" && it.sub ? " (" + it.sub + ")" : "");
              }
            }
            return nm;
          });
        },
        write: function (v) {
          (v || []).forEach(function (nm) {
            var cb = ul.querySelector('input[data-name="' + String(nm).replace(/"/g, '\\"') + '"]');
            if (cb) cb.checked = true;
          });
        },
        clear: function () {
          Array.prototype.forEach.call(ul.querySelectorAll("input"), function (cb) { cb.checked = false; });
        }
      };
      var f = el("div", "f span2");
      if (def.id) f.setAttribute("data-f", def.id);
      if (def.label) {
        var lab2 = el("label");
        lab2.appendChild(document.createTextNode(def.label + " "));
        if (def.hint) lab2.appendChild(el("i", null, def.hint));
        f.appendChild(lab2);
      }
      f.appendChild(ul);
      return f;
    }

    /* THE IMPACT LINE — the field the whole document exists for, and the one
     * everybody leaves off. It is the only thing on the page that is visually
     * louder than what surrounds it. The chips APPEND (they never replace and
     * nothing is pre-selected), because a chip is a jog, not an answer: the
     * tradesman's own words after the chip are what makes the super believe it.
     * The optional clock rides beside it because A CONSEQUENCE WITHOUT A CLOCK IS
     * A SHRUG — carried verbatim from the first instance's field review. */
    function buildImpact(def) {
      var box = el("div", "impact");
      var lab = el("label", null, def.label || "");
      box.appendChild(lab);
      if (def.hint) box.appendChild(el("p", "hint", def.hint));
      var ta = el("textarea");
      ta.rows = def.rows || 2;
      if (def.ph) ta.placeholder = def.ph;
      harden(ta, def);
      box.appendChild(ta);

      if (def.chips && def.chips.length) {
        var chips = el("div", "chips");
        if (def.chipHint) chips.appendChild(el("span", "chiphint", def.chipHint));
        def.chips.forEach(function (c) {
          var b = el("button", null, c);
          b.type = "button";
          b.addEventListener("click", function () {
            var cur = trim(ta.value);
            ta.value = cur ? (cur.replace(/\s*$/, "") + " " + c) : c;
            ta.focus();
            render();
          });
          chips.appendChild(b);
        });
        box.appendChild(chips);
      }

      var clockCur = "";
      var seg = null;
      if (def.clock && def.clock.length) {
        seg = el("div", "seg");
        seg.style.marginTop = "9px";
        def.clock.forEach(function (o) {
          var v = typeof o === "string" ? o : o.v;
          var b = el("button", null, v);
          b.type = "button";
          b.setAttribute("data-v", v);
          if (o && o.hot) b.setAttribute("data-hot", "1");
          b.addEventListener("click", function () {
            clockCur = (clockCur === v) ? "" : v;
            Array.prototype.forEach.call(seg.children, function (c) {
              c.classList.toggle("on", c.getAttribute("data-v") === clockCur);
            });
            render();
          });
          seg.appendChild(b);
        });
        box.appendChild(seg);
      }

      nodes[def.id] = {
        kind: "impact", def: def, elem: box,
        read: function () { return { text: trim(ta.value), clock: clockCur }; },
        write: function (v) {
          if (!v) return;
          ta.value = v.text || "";
          if (v.clock && seg) {
            var b = seg.querySelector('button[data-v="' + String(v.clock).replace(/"/g, '\\"') + '"]');
            if (b) b.click();
          }
        },
        clear: function () {
          ta.value = ""; clockCur = "";
          if (seg) Array.prototype.forEach.call(seg.children, function (c) { c.classList.remove("on"); });
        }
      };
      var f = el("div", "f span2");
      /* data-f, SAME AS EVERY OTHER BUILDER — and this was the one that never
       * had it. wrapField() sets it for the eight kinds that go through it, and
       * buildTicks and buildRows set it inline because they build their own
       * wrapper; buildImpact builds its own wrapper too and was the only one
       * that forgot. It stayed invisible for a reason worth writing down: NO
       * CONFIG ON ANY OF THE THIRTEEN TRADES HAD EVER DECLARED kind:"impact".
       * The engine's loudest field — the one §THE THREE SHAPES says the whole
       * document exists for — shipped unexecuted, while gc/weather-day.html and
       * hvac/repair-recommendation.html each hand-rolled their own .impact div
       * beside it. So note-live-fields.mjs, which drives a page BY THIS
       * ATTRIBUTE, could not have tested an impact field even if one existed.
       * Found standing up trade #13, whose pinned tool is the first live use.
       * (§SCARS — a gate that cannot see a field is not covering it.) */
      if (def.id) f.setAttribute("data-f", def.id);
      f.appendChild(box);
      return f;
    }

    /* THE CLOCK THAT FILLS ITSELF. The private ladder's sleeper finding, carried
     * across from the evac-record rung: the timestamp IS the tool. A directed-work
     * ticket lives or dies on WHEN he was told, and nobody types a time. So it
     * stamps itself the first moment the man touches the page, and stays editable
     * because he is often writing this twenty minutes after the super walked off. */
    function buildClock(def) {
      var row = el("div", "clockrow");
      var inp = el("input");
      inp.type = "text";
      inp.placeholder = def.ph || "stamps itself when you start";
      inp.setAttribute("autocomplete", "off");
      var b = el("button", "nowbtn", def.nowLabel || "Now");
      b.type = "button";
      b.addEventListener("click", function () { inp.value = stampNow(); render(); });
      row.appendChild(inp);
      row.appendChild(b);
      nodes[def.id] = {
        kind: "clock", def: def, elem: inp,
        read: function () { return trim(inp.value); },
        write: function (v) { inp.value = v == null ? "" : v; },
        clear: function () { inp.value = ""; },
        stamp: function () { if (!trim(inp.value)) inp.value = stampNow(); }
      };
      return wrapField(def, row);
    }

    /* REPEATABLE ROWS — this is where TICKING BEATS TYPING actually lands on a
     * T&M ticket. Crew and material are ALREADY LISTS on the real tag, so they get
     * built as a list: one compact row per man or per item, each column a picker
     * or a stepper wherever it can be. QUANTITIES ONLY — there is no rate column,
     * no total column and no arithmetic anywhere in here, on purpose and forever
     * (§SAFETY, and the roster's hardest rule: the second this page prices
     * anything, the super stops signing and the tradesman owns the number). */
    function buildRows(def) {
      var wrapEl = el("div", "rows");
      var list = el("div", "rowlist");
      wrapEl.appendChild(list);
      var add = el("button", "addrow", def.addLabel || "+ Add");
      add.type = "button";
      add.addEventListener("click", function () { addRow(); render(); });
      wrapEl.appendChild(add);

      function addRow(vals) {
        var r = el("div", "row");
        var cells = {};
        (def.cols || []).forEach(function (c) {
          var cell = el("div", "cell" + (c.wide ? " wide" : ""));
          var ctl;
          if (c.kind === "select") {
            ctl = el("select");
            (c.options || []).forEach(function (o) {
              var opt = el("option", null, o);
              opt.value = o;
              ctl.appendChild(opt);
            });
          } else if (c.kind === "stepper") {
            ctl = el("input");
            ctl.type = "text";
            ctl.setAttribute("inputmode", "decimal");
            ctl.setAttribute("autocomplete", "off");
            if (c.ph) ctl.placeholder = c.ph;
          } else {
            ctl = el("input");
            ctl.type = "text";
            ctl.setAttribute("autocomplete", "off");
            if (c.caps) {
              ctl.setAttribute("autocapitalize", "characters");
              ctl.setAttribute("autocorrect", "off");
              ctl.setAttribute("spellcheck", "false");
            }
            if (c.ph) ctl.placeholder = c.ph;
          }
          ctl.setAttribute("aria-label", c.label || c.id);
          if (vals && vals[c.id] != null) ctl.value = vals[c.id];
          cells[c.id] = ctl;
          cell.appendChild(ctl);
          r.appendChild(cell);
        });
        var rm = el("button", "rm", "×");
        rm.type = "button";
        rm.setAttribute("aria-label", def.rmLabel || "Take this line off");
        rm.addEventListener("click", function () {
          list.removeChild(r);
          if (!list.children.length) addRow();
          render();
        });
        r.appendChild(rm);
        r._cells = cells;
        list.appendChild(r);
        return r;
      }

      function readRows() {
        return Array.prototype.slice.call(list.children).map(function (r) {
          var o = {};
          (def.cols || []).forEach(function (c) {
            var v = trim(r._cells[c.id].value);
            o[c.id] = isNone(v) ? "" : v;
          });
          return o;
        }).filter(function (o) {
          return (def.cols || []).some(function (c) { return o[c.id]; });
        });
      }

      nodes[def.id] = {
        kind: "rows", def: def, elem: wrapEl,
        read: readRows,
        docLines: function () {
          return readRows().map(function (o) {
            var parts = (def.cols || []).map(function (c) {
              if (!o[c.id]) return "";
              return (c.docPrefix || "") + o[c.id] + (c.docSuffix || "");
            }).filter(Boolean);
            return parts.join(def.docJoin || " — ");
          });
        },
        write: function (v) {
          list.innerHTML = "";
          (v && v.length ? v : [null]).forEach(function (o) { addRow(o); });
        },
        clear: function () { list.innerHTML = ""; addRow(); }
      };
      addRow();
      var f = el("div", "f span2");
      if (def.id) f.setAttribute("data-f", def.id);
      if (def.label) {
        var lab3 = el("label");
        lab3.appendChild(document.createTextNode(def.label + " "));
        if (def.hint) lab3.appendChild(el("i", null, def.hint));
        f.appendChild(lab3);
      }
      f.appendChild(wrapEl);
      return f;
    }

    var BUILDERS = {
      text: buildText, area: buildArea, select: buildSelect, seg: buildSeg,
      pick: buildPick, ticks: buildTicks, impact: buildImpact, clock: buildClock,
      rows: buildRows, date: buildDate
    };

    /* ── render the page from the spec ─────────────────────────────────────── */
    (cfg.sections || []).forEach(function (sec) {
      var card = el("section", "card" + (sec.tone ? " " + sec.tone : ""));
      if (sec.title) {
        var h = el("h2", "blk");
        h.appendChild(document.createTextNode(sec.title));
        if (sec.why) h.appendChild(el("span", "why", sec.why));
        card.appendChild(h);
      }
      var grid = el("div", "hgrid");
      card.appendChild(grid);
      var ids = [];
      (sec.fields || []).forEach(function (def) {
        if (def.subhead) {
          card.appendChild(el("p", "subhead", def.subhead));
          grid = el("div", "hgrid");
          card.appendChild(grid);
        }
        var build = BUILDERS[def.kind];
        if (!build) return;
        grid.appendChild(build(def));
        nodes[def.id].section = sec;
        order.push(def.id);
        ids.push(def.id);
      });
      form.appendChild(card);
      sections.push({ def: sec, node: card, ids: ids });
    });

    /* ── STICKY — the answers that are identical on every ticket he ever writes.
     * They survive Clear, because making a man retype his own name and company on
     * every extra is how a tool gets abandoned in week two. */
    var stickyIds = order.filter(function (id) { return nodes[id].def.sticky; });
    (function loadSticky() {
      var s = {};
      try { s = JSON.parse(localStorage.getItem(STICKY_KEY) || "{}"); } catch (e) { s = {}; }
      stickyIds.forEach(function (id) { if (s[id] != null) nodes[id].write(s[id]); });
    })();
    function saveSticky() {
      var s = {};
      stickyIds.forEach(function (id) { s[id] = nodes[id].read(); });
      try { localStorage.setItem(STICKY_KEY, JSON.stringify(s)); } catch (e) {}
    }

    /* ── reading the state ─────────────────────────────────────────────────── */
    function get(id) {
      var n = nodes[id];
      if (!n) return "";
      var v = n.read();
      return typeof v === "string" ? v : v;
    }
    function docVal(id) {
      var n = nodes[id];
      if (!n) return "";
      if (n.docValue) return n.docValue();
      var v = n.read();
      return typeof v === "string" ? v : "";
    }
    function snapshot() {
      var s = {};
      order.forEach(function (id) { s[id] = nodes[id].read(); });
      return s;
    }
    function hasContent(v) {
      if (v == null) return false;
      if (typeof v === "string") return !!trim(v) && !isNone(v);
      if (Object.prototype.toString.call(v) === "[object Array]") return v.length > 0;
      if (typeof v === "object") return !!(trim(v.text) || v.clock);
      return false;
    }
    function isTouched(s) {
      return order.some(function (id) {
        if (nodes[id].def.sticky) return false;   // a saved name is not a started ticket
        if (nodes[id].kind === "clock") return false; // nor is a clock that stamped itself
        return hasContent(s[id]);
      });
    }

    /* ── the document ──────────────────────────────────────────────────────── */
    function fieldLines(id) {
      var n = nodes[id], def = n.def, out = [];
      if (def.docSkip) return out;
      if (n.kind === "ticks" || n.kind === "rows") {
        var lines = n.docLines();
        if (!lines.length) return out;
        if (def.docLabel) out.push(def.docLabel + ":");
        lines.forEach(function (l) { out.push("- " + l); });
        return out;
      }
      if (n.kind === "impact") {
        var v = n.read();
        if (!trim(v.text) && !v.clock) return out;
        var head = (def.docLabel ? def.docLabel + ": " : "") + trim(v.text);
        if (v.clock) {
          // THE CLOCK RIDES IN THE LINE AS A SCANNABLE TOKEN, not as the sentence
          // the on-screen button spells out — the receiver triages off the bracket.
          var tok = v.clock;
          for (var i = 0; i < (def.clock || []).length; i++) {
            var o = def.clock[i];
            if ((typeof o === "string" ? o : o.v) === v.clock) { tok = (o && o.docToken) || v.clock; break; }
          }
          head = trim(head) ? (head + "   [" + tok.toUpperCase() + "]") : ("[" + tok.toUpperCase() + "]");
        }
        out.push(head);
        return out;
      }
      var val = docVal(id);
      if (!val) return out;
      out.push(def.docLabel ? (def.docLabel + ": " + val) : val);
      return out;
    }

    function buildDoc() {
      /* `u.doc(id)` is how a heading or a subline asks for the value the DOCUMENT
       * would print rather than the value STATE holds. They are the same string
       * for every kind but `date`, where state is ISO so it can restore and the
       * document is "Sat, Aug 22" — and the top of this document is the one line
       * the receiver triages off a lock screen, so it has to be the words. */
      var u = { today: todayStr, doc: docVal };
      var head = cfg.docName || "";
      if (cfg.titleSuffix) {
        var suf = trim(cfg.titleSuffix(get, u));
        if (suf) head += " — " + suf;
      }
      var out = head;

      if (cfg.subline) {
        var sub = trim(cfg.subline(get, u));
        if (sub) out += "\n" + sub;
      }

      sections.forEach(function (s) {
        var body = [];
        s.ids.forEach(function (id) {
          var lines = fieldLines(id);
          if (!lines.length) return;
          /* A LABELLED LIST INSIDE A SECTION GETS AIR. Two `- ` lists back to back
           * under one heading read as one list: the first live drive of this engine
           * printed two men and a length of cable as a single six-line block, and a
           * super reading it on a phone cannot tell where the crew stops and the
           * material starts. A blank line before each labelled group fixes it in
           * every trade at once. */
          var labelled = nodes[id].def.docLabel &&
            (nodes[id].kind === "ticks" || nodes[id].kind === "rows");
          if (labelled && body.length) body.push("");
          lines.forEach(function (l) { body.push(l); });
        });
        if (!body.length) return;
        /* A SECTION WITHOUT A HEADING STILL GETS ITS OWN AIR. The sender block
         * has no heading — "From: …" glued onto the last line of the material
         * list reads as another material line, which is exactly the kind of mush
         * that makes a receiver stop trusting the document. */
        out += (out ? "\n\n" : "") + (s.def.docHead ? s.def.docHead + "\n" : "") + body.join("\n");
      });

      (cfg.closing || []).forEach(function (c) {
        var line = typeof c === "function" ? c(get) : c;
        if (trim(line)) out += "\n\n" + line;
      });

      return out.replace(/\n{3,}/g, "\n\n").trim();
    }

    /* ── persist ───────────────────────────────────────────────────────────────
     * §SCARS — CLEAR MUST ACTUALLY CLEAR: a persisting page returns null when its
     * state is untouched, or the debounced write resurrects the record 250ms after
     * the user cleared it. */
    var saveT = null;
    function persist() {
      var s = snapshot();
      try {
        if (isTouched(s)) localStorage.setItem(DRAFT_KEY, JSON.stringify(s));
        else localStorage.removeItem(DRAFT_KEY);
      } catch (e) {}
    }
    function flush() {
      if (saveT) { clearTimeout(saveT); saveT = null; }
      persist();
    }

    var previewEl = byId(cfg.preview || "preview");
    var countEl = byId(cfg.count || "count");

    function render() {
      var doc = buildDoc();
      if (previewEl) previewEl.textContent = doc;
      var s = snapshot();
      if (countEl) {
        countEl.textContent = cfg.count_ ? cfg.count_(get, s)
          : (cfg.countLabel ? cfg.countLabel(get, s, isTouched(s))
            : (isTouched(s) ? (cfg.startedLabel || "Started") : (cfg.emptyLabel || "Nothing on it yet")));
      }
      saveSticky();
      if (saveT) clearTimeout(saveT);
      saveT = setTimeout(persist, 250);
    }

    /* THE CLOCK FILLS ITSELF on the first real interaction — not on load, because
     * a page opened in a truck at 6am and used at 2pm would stamp the wrong time,
     * and not never, because nobody types a timestamp. */
    function stampClocks() {
      if (stamped) return;
      stamped = true;
      order.forEach(function (id) { if (nodes[id].stamp) nodes[id].stamp(); });
    }
    form.addEventListener("input", function () { stampClocks(); render(); });
    form.addEventListener("change", function () { stampClocks(); render(); });
    form.addEventListener("click", function (e) {
      if (e.target && e.target.tagName === "BUTTON") stampClocks();
    });

    /* THE CAMERA / PHONE-CALL ROUND-TRIP EATS THE DRAFT. On a directed-work ticket
     * the man very often stops mid-page to photograph the condition or to call the
     * office, and iOS backgrounds the browser instantly — which can freeze the
     * 250ms debounce before it ever writes. Flush synchronously on the way out.
     * A man who retypes a ticket once does not open the page again. */
    ["visibilitychange", "pagehide", "blur"].forEach(function (ev) {
      window.addEventListener(ev, flush);
    });

    /* ── restore ───────────────────────────────────────────────────────────── */
    (function boot() {
      var s = null;
      try { s = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null"); } catch (e) { s = null; }
      if (s) {
        order.forEach(function (id) {
          if (s[id] == null) return;
          if (nodes[id].def.sticky && !hasContent(s[id])) return;
          nodes[id].write(s[id]);
        });
        stamped = true;   // a restored draft already carries its own stamp
      }
      render();
    })();

    /* ── copy + clear ──────────────────────────────────────────────────────── */
    var copyBtn = byId(cfg.copy || "copy");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        copyText(buildDoc(), copyBtn, cfg.copiedLabel, cfg.copyFailLabel);
      });
    }
    var clearBtn = byId(cfg.clear || "clear");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        if (!confirm(cfg.clearConfirm || "Clear this one? Your name and company stay.")) return;
        order.forEach(function (id) {
          if (nodes[id].def.sticky) return;
          nodes[id].clear();
        });
        stamped = false;
        try { localStorage.removeItem(DRAFT_KEY); } catch (e) {}
        render();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }

    return { get: get, doc: buildDoc, render: render, flush: flush };
  }

  window.Note = { mount: mount, esc: esc, todayStr: todayStr, stampNow: stampNow, copyText: copyText, joinDot: joinDot };
})();
