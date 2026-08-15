/* FIELD TOOLKIT — THE HOLD TEST ENGINE.
 *
 * av/AV_SOCIETY.md §THE THREE SHAPES names three: the checklist → request, the
 * note, and the row log. This is a row log whose ADD-ROW BAR IS A STOPWATCH, and
 * that one difference is the entire product: the rows are not typed, they are
 * TAPPED, and the clock fills the column a man would otherwise reconstruct from
 * memory two hours later, wrong, at a desk.
 *
 * THE JOB IT DOES, in every trade that has it: put a medium into a closed system,
 * ISOLATE it, watch a gauge, and be able to say afterwards what it read and WHEN.
 * HVAC/R pulls a vacuum and watches the microns come back up. A plumber puts five
 * pounds of air or ten feet of head on a rough-in and watches the needle stay put.
 * Gas piping, medical gas, a flood test on a deck — same act, same document, one
 * engine, and the trade's own words come from the config.
 *
 * BUILT AS AN ENGINE ON ITS FIRST INSTANCE, the same deliberate exception
 * shared/rowlog.js took, and for the same reason: the second config shipped in
 * the SAME cycle. A shape with two live configs on day one either has an engine
 * or has a fork, and the fork is invisible for about a week.
 *
 * WHAT THE ENGINE OWNS — the parts that rot the moment this is forked:
 *   · THE SELF-FILLING CLOCK. Every stamp is an ABSOLUTE epoch millisecond, never
 *     an accumulating counter. This is a page that gets backgrounded for forty
 *     minutes while a pump runs — a setInterval that counts is a page that lies
 *     the moment the phone locks. Elapsed is always recomputed from Date.now().
 *   · THE RUNNING READOUT, which recovers from a cold start: reopen the tab two
 *     hours later and it is still counting from the real isolation stamp.
 *   · A CORRECTED TIME CAN NEVER PASS AS THE CLOCK'S. The one claim this tool
 *     makes is that the stamps are real. A stamp typed in afterwards — and it has
 *     to be typeable, because a man opens the tool twenty minutes after he
 *     started the pump — is flagged in the log AND in the document, forever, with
 *     no way to switch it off.
 *   · NO VERDICT, EVER. The engine prints times, readings and the signed delta
 *     between two numbers a man typed. It does not know a target, a standard, a
 *     pass, a fail, a decay rate or an acceptable rise, and it never will
 *     (av/AV_SOCIETY.md §SAFETY). The trade holds those numbers; a web page
 *     asserting them is a liability wearing a helpful face.
 *   · Delta arithmetic ONLY between two values the tool watched the same man
 *     enter, and nothing at all when either fails to parse as a number.
 *   · persistence with a SYNCHRONOUS flush · the plain-text document · copy with
 *     the non-secure-context fallback · re-render on the runtime's av:ready.
 *
 * WHAT THE CALLER OWNS: the MARKS (their words, their order, which one carries a
 * reading, which one starts the hold), the unit, the header fields, and the
 * sentences of the document. The engine assembles state; the page writes prose.
 *
 * A MARK:
 *   { key, label, hint, value, once, zero, end, repeat, runLabel, holdLabel, note }
 *   value    this mark carries a reading off the gauge (required to stamp it)
 *   once     it can only happen once in a test (pump on, valved off, test off)
 *   zero     THE moment the hold starts — everything after it is measured from it
 *   end      the test is closed; the clock stops counting
 *   repeat   it happens as many times as he taps it (a reading, a note)
 *   runLabel what the big clock says while this mark is the latest one (pre-hold)
 *   holdLabel what the big clock says once the `zero` mark is stamped
 *   note     tapping it opens the row's note straight away
 *
 * Load AFTER the trade config and registry, alongside the shared runtime:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/holdtest.js"></script>
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c];
    });
  }

  function todayStr() {
    return (window.Toolkit && window.Toolkit.todayStr)
      ? window.Toolkit.todayStr()
      : new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function timeStr(t) {
    return new Date(t).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  }
  function dayStr(t) {
    return new Date(t).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
  }
  function dayKey(t) {
    var d = new Date(t);
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
  }

  /* The running readout: HH:MM:SS, hours uncapped. A vacuum pulled overnight is
     "14:22:07", not "02:22:07" — a wrapped clock on this page is a wrong record. */
  function fmtClock(ms) {
    if (!(ms > 0)) ms = 0;
    var s = Math.floor(ms / 1000);
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return p(h) + ":" + p(m) + ":" + p(ss);
  }

  /* The document's span, in the words a man would say out loud. Seconds matter on
     the running clock and never in the record — nobody writes "31 minutes and
     four seconds" on a test. */
  function fmtSpan(ms) {
    if (!(ms > 0)) return "under a minute";
    var mins = Math.floor(ms / 60000);
    if (mins < 1) return "under a minute";
    if (mins === 1) return "1 minute";
    if (mins < 60) return mins + " minutes";
    var h = Math.floor(mins / 60), m = mins % 60;
    var out = h + (h === 1 ? " hour" : " hours");
    if (m) out += " " + m + (m === 1 ? " minute" : " minutes");
    return out;
  }

  /* NOTHING NORMALISES ON THE WAY OUT. A reading ships back character for
     character — this only decides whether arithmetic is honest here. A blank, a
     range ("480-500"), a word ("pegged") all parse to null and the delta is
     simply not printed rather than guessed at. */
  function num(v) {
    var s = String(v == null ? "" : v).trim();
    if (!s) return null;
    if (!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(s)) return null;
    var n = parseFloat(s);
    return isFinite(n) ? n : null;
  }

  /* datetime-local speaks LOCAL wall time with no zone, so both directions have
     to go through the local parts explicitly — new Date(string) on a bare
     "2026-08-14T09:41" is treated as local by modern engines but the round trip
     through UTC is the classic way this silently shifts a stamp by the offset. */
  function toLocalInput(t) {
    var d = new Date(t);
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate())
      + "T" + p(d.getHours()) + ":" + p(d.getMinutes());
  }
  function fromLocalInput(s) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(String(s || ""));
    if (!m) return null;
    var d = new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], 0, 0);
    return isFinite(d.getTime()) ? d.getTime() : null;
  }

  function copyText(t, btn) {
    function flash(msg) {
      if (!btn) return;
      var old = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", old);
      btn.textContent = msg;
      setTimeout(function () { btn.textContent = btn.getAttribute("data-label") || old; }, 1500);
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

  function joinDots(parts) {
    return parts.filter(function (x) { return x != null && String(x).trim() !== ""; }).join(" · ");
  }

  function mount(cfg) {
    var $ = function (s) { return typeof s === "string" ? document.querySelector(s) : s; };
    var elClock = $(cfg.clock), elBar = $(cfg.bar), elLog = $(cfg.log);
    var elPrev = cfg.preview ? $(cfg.preview) : null;
    var btnCopy = cfg.copyBtn ? $(cfg.copyBtn) : null;

    var MARKS = cfg.marks || [];
    var rows = [];          // {id, k, t, v, note, typed}
    var editing = null;     // row id open in the editor
    var seq = 1;
    var tickTimer = null;

    function markOf(k) {
      for (var i = 0; i < MARKS.length; i++) if (MARKS[i].key === k) return MARKS[i];
      return null;
    }
    function labelOf(k) { var m = markOf(k); return m ? m.label : k; }
    function unit() { return cfg.unitOf ? String(cfg.unitOf() || "").trim() : String(cfg.unit || "").trim(); }

    function sorted() {
      return rows.slice().sort(function (a, b) { return a.t - b.t || a.id - b.id; });
    }
    function firstOf(pred) {
      var s = sorted();
      for (var i = 0; i < s.length; i++) if (pred(s[i])) return s[i];
      return null;
    }
    function lastOf(pred) {
      var s = sorted();
      for (var i = s.length - 1; i >= 0; i--) if (pred(s[i])) return s[i];
      return null;
    }
    function zeroRow() { return firstOf(function (r) { var m = markOf(r.k); return m && m.zero; }); }
    function endRow() { return lastOf(function (r) { var m = markOf(r.k); return m && m.end; }); }
    function stamped(k) { return rows.some(function (r) { return r.k === k; }); }

    /* THE NEXT MARK — the page knows what comes next, so the man does not have to
       find it. Before the hold starts it is the first thing he has not done yet;
       once it is holding it is the reading, forever, because that is the only
       thing he does for the next half hour. Nothing is ever BLOCKED by this: every
       other mark stays on the page underneath. */
    function nextMark() {
      if (endRow()) return null;
      if (zeroRow()) {
        for (var i = 0; i < MARKS.length; i++) if (MARKS[i].repeat && MARKS[i].value) return MARKS[i];
      }
      for (var j = 0; j < MARKS.length; j++) if (MARKS[j].once && !stamped(MARKS[j].key)) return MARKS[j];
      return null;
    }

    /* ── state ─────────────────────────────────────────────────────────────── */
    function stamp(m, at, opts) {
      var r = {
        id: seq++,
        k: m.key,
        t: at,
        v: (opts && opts.v != null) ? String(opts.v) : "",
        note: "",
        typed: !!(opts && opts.typed)
      };
      rows.push(r);
      return r;
    }

    function removeRow(id) {
      rows = rows.filter(function (r) { return r.id !== id; });
      if (editing === id) editing = null;
    }

    /* ── render ────────────────────────────────────────────────────────────── */
    function ctx() {
      var z = zeroRow(), e = endRow(), s = sorted();
      var lastRead = lastOf(function (r) { return num(r.v) != null; });
      var zn = z ? num(z.v) : null, ln = lastRead ? num(lastRead.v) : null;
      return {
        rows: s,
        total: s.length,
        zero: z, end: e, last: lastRead,
        unit: unit(),
        today: todayStr(),
        held: z ? ((e ? e.t : Date.now()) - z.t) : 0,
        delta: (z && lastRead && lastRead !== z && zn != null && ln != null) ? (ln - zn) : null,
        anyTyped: s.some(function (r) { return r.typed; })
      };
    }

    function renderClock() {
      if (!elClock) return;
      var c = ctx(), z = c.zero, e = c.end, s = c.rows;
      var state, big, since = "", idle = false;

      if (!s.length) {
        idle = true;
        state = cfg.idleState || "Not started";
        big = cfg.idleText || "Tap the first mark when you start. From then on the clock fills itself — you never type a time.";
      } else if (e) {
        state = (markOf(e.k) && markOf(e.k).label) || "Closed";
        big = z ? fmtClock(e.t - z.t) : fmtClock(e.t - s[0].t);
        since = z
          ? "From <b>" + esc(labelOf(z.k).toLowerCase()) + "</b> at " + esc(timeStr(z.t))
            + " to " + esc(timeStr(e.t)) + " — held <b>" + esc(fmtSpan(e.t - z.t)) + "</b>."
          : "Closed " + esc(timeStr(e.t)) + ".";
      } else if (z) {
        var zm = markOf(z.k);
        state = (zm && zm.holdLabel) || "Holding";
        big = fmtClock(Date.now() - z.t);
        var bits = [];
        bits.push("Since <b>" + esc(labelOf(z.k).toLowerCase()) + "</b> at " + esc(timeStr(z.t))
          + (z.v ? " at <b>" + esc(z.v) + (c.unit ? " " + esc(c.unit) : "") + "</b>" : ""));
        if (c.last && c.last !== z) {
          bits.push("last read <b>" + esc(c.last.v) + (c.unit ? " " + esc(c.unit) : "") + "</b>"
            + (c.delta != null ? " (" + esc(deltaWord(c.delta)) + ")" : ""));
        }
        since = bits.join(" · ") + ".";
      } else {
        var lastRow = s[s.length - 1], lm = markOf(lastRow.k);
        state = (lm && lm.runLabel) || labelOf(lastRow.k);
        big = fmtClock(Date.now() - lastRow.t);
        since = "Since " + esc(labelOf(lastRow.k).toLowerCase()) + " at " + esc(timeStr(lastRow.t)) + ".";
      }

      elClock.className = "ht-clock" + (idle ? " ht-idle" : "");
      elClock.innerHTML =
        '<span class="ht-state">' + esc(state) + "</span>" +
        '<span class="ht-el">' + esc(big) + "</span>" +
        (since ? '<span class="ht-since">' + since + "</span>" : "");
    }

    /* The delta is arithmetic on two numbers HE typed, and it is stated as a
       direction and a size — never as a judgement. A vacuum rises when it leaks
       and a pressure test falls when it leaks, so the engine cannot know which
       direction is bad and does not pretend to. */
    function deltaWord(d) {
      var u = unit();
      if (d === 0) return "no change";
      var mag = Math.abs(Math.round(d * 1000) / 1000);
      return (d > 0 ? "up " : "down ") + mag + (u ? " " + u : "");
    }

    function renderBar() {
      if (!elBar) return;
      var c = ctx(), nm = nextMark(), u = c.unit;
      var needsVal = MARKS.some(function (m) { return m.value; });
      var html = "";

      if (needsVal) {
        html += '<div class="ht-val"><label for="htVal">' + esc(cfg.valueLabel || "Off the gauge")
          + (u ? ' <i class="ht-unit">' + esc(u) + "</i>" : "") + "</label>"
          + '<input type="text" id="htVal" inputmode="decimal" autocomplete="off" autocorrect="off" spellcheck="false"'
          + ' placeholder="' + esc(cfg.valuePlaceholder || "the number you are looking at") + '"></div>';
      }

      if (nm) {
        html += '<button type="button" class="ht-go" data-mark="' + esc(nm.key) + '">'
          + "<b>" + esc(nm.label) + "</b>"
          + '<span>' + esc(nm.hint || (nm.value ? "stamps the time and this reading" : "stamps the time")) + "</span>"
          + "</button>";
      }

      var others = MARKS.filter(function (m) { return m !== nm; });
      if (others.length) {
        html += '<div class="ht-others">';
        others.forEach(function (m) {
          var done = m.once && stamped(m.key);
          var when = done ? lastOf(function (r) { return r.k === m.key; }) : null;
          html += '<button type="button" class="ht-mark' + (done ? " done" : "") + '" data-mark="' + esc(m.key) + '"'
            + (done ? " disabled" : "") + ">"
            + "<b>" + esc(m.label) + "</b>"
            + "<span>" + esc(done && when ? "done " + timeStr(when.t) : (m.hint || (m.value ? "with a reading" : "stamps the time"))) + "</span>"
            + "</button>";
        });
        html += "</div>";
      }

      html += '<p class="ht-say" id="htSay"></p>';
      elBar.innerHTML = html;
    }

    function rowHTML(r, prev, c) {
      var m = markOf(r.k) || { label: r.k };
      var cls = "ht-row" + (m.zero ? " zero" : "") + (m.end ? " ended" : "");
      var meta = [];
      if (c.zero && r.t > c.zero.t) meta.push(fmtSpan(r.t - c.zero.t) + " after " + labelOf(c.zero.k).toLowerCase());
      if (c.zero && r !== c.zero && num(r.v) != null && num(c.zero.v) != null) {
        var d = num(r.v) - num(c.zero.v);
        meta.push('<span class="' + (d >= 0 ? "up" : "dn") + '">' + esc(deltaWord(d)) + "</span>");
      }
      if (!c.zero && prev) meta.push(fmtSpan(r.t - prev.t) + " after " + labelOf(prev.k).toLowerCase());
      if (r.note) meta.push(esc(r.note));

      return '<div class="' + cls + '" data-id="' + r.id + '">'
        + '<div class="ht-body">'
        + '<span class="ht-t">' + esc(timeStr(r.t)) + "</span>"
        + '<span class="ht-name">' + esc(m.label) + "</span>"
        + (r.v ? '<span class="ht-read">' + esc(r.v) + (c.unit ? " " + esc(c.unit) : "") + "</span>" : "")
        + (r.typed ? '<span class="ht-typed">time typed in</span>' : "")
        + (meta.length ? '<span class="ht-meta">' + meta.join(" · ") + "</span>" : "")
        + "</div>"
        + '<button type="button" class="ht-pen" data-edit="' + r.id + '" aria-label="Fix this mark">✎</button>'
        + "</div>";
    }

    function editHTML(r, c) {
      return '<div class="ht-edit" data-editrow="' + r.id + '">'
        + '<div class="hgrid">'
        + '<div><label for="htET">Time</label><input type="datetime-local" id="htET" value="' + esc(toLocalInput(r.t)) + '"></div>'
        + '<div><label for="htEV">Reading' + (c.unit ? " (" + esc(c.unit) + ")" : "")
        + '</label><input type="text" id="htEV" inputmode="decimal" autocomplete="off" autocorrect="off" spellcheck="false" value="' + esc(r.v) + '"></div>'
        + '<div class="wide"><label for="htEN">Note</label><input type="text" id="htEN" autocomplete="off" value="' + esc(r.note) + '" placeholder="anything worth remembering about this one"></div>'
        + "</div>"
        + '<p class="note" style="margin:0 0 9px">Change the time and this mark is labelled <b>time typed in</b> on the record from then on — on the page and in what you send. That label is the point: the rest of these stamps are the clock’s word, and this one is yours.</p>'
        + '<div class="ht-acts">'
        + '<button type="button" class="btn" data-done="1">Done</button>'
        + '<button type="button" class="btn del" data-del="' + r.id + '">Delete this mark</button>'
        + "</div></div>";
    }

    function renderLog() {
      if (!elLog) return;
      var c = ctx();
      if (!c.total) {
        elLog.innerHTML = '<p class="ht-empty">' + esc(cfg.emptyText || "Nothing marked yet.") + "</p>";
        return;
      }
      var out = "", prev = null, lastDay = null;
      c.rows.forEach(function (r) {
        var k = dayKey(r.t);
        if (lastDay !== null && k !== lastDay) out += '<p class="ht-daysep">' + esc(dayStr(r.t)) + "</p>";
        lastDay = k;
        if (editing === r.id) out += editHTML(r, c);
        else out += rowHTML(r, prev, c);
        prev = r;
      });
      elLog.innerHTML = out;
    }

    /* ── the document ──────────────────────────────────────────────────────── */
    function doc() {
      var c = ctx();
      var out = [];
      if (cfg.docHead) out.push(String(cfg.docHead(c)));
      out.push("");

      if (!c.total) {
        out.push("Nothing marked yet.");
      } else {
        var prev = null, lastDay = null;
        c.rows.forEach(function (r) {
          var k = dayKey(r.t);
          if (lastDay !== null && k !== lastDay) { out.push(""); out.push("-- " + dayStr(r.t) + " --"); }
          lastDay = k;
          var bits = [timeStr(r.t), labelOf(r.k)];
          if (r.v) bits.push(r.v + (c.unit ? " " + c.unit : ""));
          if (c.zero && r.t > c.zero.t) bits.push(fmtSpan(r.t - c.zero.t) + " after " + labelOf(c.zero.k).toLowerCase());
          else if (!c.zero && prev) bits.push(fmtSpan(r.t - prev.t) + " after " + labelOf(prev.k).toLowerCase());
          if (c.zero && r !== c.zero && num(r.v) != null && num(c.zero.v) != null) {
            bits.push(deltaWord(num(r.v) - num(c.zero.v)));
          }
          if (r.typed) bits.push("time typed in");
          if (r.note) bits.push(r.note);
          out.push(joinDots(bits));
          prev = r;
        });

        if (c.zero && c.last && c.last !== c.zero) {
          out.push("");
          out.push(labelOf(c.zero.k) + " at " + timeStr(c.zero.t)
            + (c.zero.v ? " at " + c.zero.v + (c.unit ? " " + c.unit : "") : "")
            + ". Last reading " + timeStr(c.last.t) + " at " + c.last.v + (c.unit ? " " + c.unit : "")
            + " — " + fmtSpan(c.last.t - c.zero.t) + " later"
            + (c.delta != null ? ", " + deltaWord(c.delta) : "") + ".");
        }
      }

      out.push("");
      /* THE HONESTY LINE. Not switchable, not configurable, and it ships on every
         copy from every trade: the whole value of this document is that a reader
         can tell what the phone did from what the person did. */
      out.push("Every time above is this phone’s clock at the moment the mark was tapped"
        + (c.anyTyped ? ", except the ones marked “time typed in”, which were corrected by hand" : "")
        + ". Every reading is what was read off the gauge and typed in. Nothing here was measured by the phone, and nothing here says the test passed or failed — that call belongs to whoever ran it.");
      if (cfg.docFoot) { out.push(""); out.push(String(cfg.docFoot(c))); }
      return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
    }

    function renderPreview() {
      if (elPrev) elPrev.textContent = doc();
    }

    function render() {
      renderClock();
      renderBar();
      renderLog();
      renderPreview();
    }

    /* ── persistence ───────────────────────────────────────────────────────
       A 250 ms DEBOUNCE IS NOT A SAVE. This is the one page in the toolkit that
       is DESIGNED to be backgrounded — the phone goes in a pocket while a pump
       runs — so the flush on visibilitychange / pagehide / blur is not a nicety
       here, it is the feature working at all. */
    var saveTimer = null;
    function persistNow() {
      if (!cfg.persistKey) return;
      try {
        var extra = cfg.persistExtra ? cfg.persistExtra() : null;
        if (!rows.length && !extra) { localStorage.removeItem(cfg.persistKey); return; }
        localStorage.setItem(cfg.persistKey, JSON.stringify({ v: 1, rows: rows, extra: extra }));
      } catch (e) { /* private mode, quota — the page still works, it just forgets */ }
    }
    function schedulePersist() {
      if (saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(function () { saveTimer = null; persistNow(); }, 250);
    }
    function flush() { if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; } persistNow(); }
    document.addEventListener("visibilitychange", function () {
      flush();
      if (!document.hidden) render();   // back from a locked screen: the clock has moved
    });
    window.addEventListener("pagehide", flush);
    window.addEventListener("blur", flush);

    function restore() {
      var raw = null;
      try { raw = cfg.persistKey ? localStorage.getItem(cfg.persistKey) : null; } catch (e) { raw = null; }
      if (raw) {
        try {
          var d = JSON.parse(raw);
          if (d && Array.isArray(d.rows)) {
            rows = d.rows.filter(function (r) {
              return r && typeof r.t === "number" && isFinite(r.t) && markOf(r.k);
            }).map(function (r) {
              return { id: seq++, k: r.k, t: r.t, v: r.v == null ? "" : String(r.v), note: r.note == null ? "" : String(r.note), typed: !!r.typed };
            });
          }
          if (d && cfg.onRestoreExtra) cfg.onRestoreExtra(d.extra || null);
        } catch (e) { /* a corrupt draft is a fresh page, never a broken one */ }
      }
      render();
      startTick();
    }

    /* One timer for the whole page, and it repaints ONLY the readout — a full
       re-render every second would blow away a half-typed reading. */
    function startTick() {
      if (tickTimer) clearInterval(tickTimer);
      tickTimer = setInterval(renderClock, 1000);
    }

    /* ── events ────────────────────────────────────────────────────────────── */
    function say(msg, kind) {
      var el = document.querySelector("#htSay");
      if (!el) return;
      el.textContent = msg || "";
      el.className = "ht-say" + (kind ? " " + kind : "");
      if (msg) setTimeout(function () { if (el.textContent === msg) { el.textContent = ""; el.className = "ht-say"; } }, 2600);
    }

    function tap(key) {
      var m = markOf(key);
      if (!m) return;
      var input = document.querySelector("#htVal");
      var v = input ? input.value.trim() : "";
      /* A READING MARK REQUIRES ITS READING — a "Reading" row with no number is
         a row that says nothing. `soft` is the exception, and it exists for
         exactly one case: taking it OFF test. The last number is the money
         number and he should have it, but the gauge is sometimes already bled
         off when he gets back to it, and refusing to close the test then is the
         page arguing with the job. */
      if (m.value && !m.soft && !v) {
        say(cfg.needValue || "Type the reading first, then tap it.", "bad");
        if (input) input.focus();
        return;
      }
      var r = stamp(m, Date.now(), { v: m.value ? v : "" });
      if (input && m.value) { input.value = ""; input.blur(); }
      if (m.note) editing = r.id;
      if (cfg.onChange) cfg.onChange();
      schedulePersist();
      render();
      say(m.label + " — " + timeStr(r.t), "ok");
      if (m.note) {
        var n = document.querySelector("#htEN");
        if (n) n.focus();
      }
    }

    if (elBar) {
      elBar.addEventListener("click", function (e) {
        var b = e.target.closest("[data-mark]");
        if (b && !b.disabled) tap(b.getAttribute("data-mark"));
      });
      /* Enter in the reading box = the next mark. A man with one hand on a valve
         and a keyboard already open should not have to go find a button. */
      elBar.addEventListener("keydown", function (e) {
        if (e.key !== "Enter") return;
        if (!e.target || e.target.id !== "htVal") return;
        e.preventDefault();
        var nm = nextMark();
        if (nm) tap(nm.key);
      });
    }

    if (elLog) {
      elLog.addEventListener("click", function (e) {
        var pen = e.target.closest("[data-edit]");
        if (pen) { editing = +pen.getAttribute("data-edit"); render(); return; }
        var del = e.target.closest("[data-del]");
        if (del) {
          removeRow(+del.getAttribute("data-del"));
          if (cfg.onChange) cfg.onChange();
          flush(); render(); return;
        }
        if (e.target.closest("[data-done]")) { editing = null; render(); return; }
      });
      elLog.addEventListener("input", function (e) {
        var box = e.target.closest("[data-editrow]");
        if (!box) return;
        var id = +box.getAttribute("data-editrow");
        var r = null;
        for (var i = 0; i < rows.length; i++) if (rows[i].id === id) r = rows[i];
        if (!r) return;
        if (e.target.id === "htEV") r.v = e.target.value;
        else if (e.target.id === "htEN") r.note = e.target.value;
        else if (e.target.id === "htET") {
          var t = fromLocalInput(e.target.value);
          if (t != null && t !== r.t) { r.t = t; r.typed = true; }
        }
        if (cfg.onChange) cfg.onChange();
        schedulePersist();
        renderClock();
        renderPreview();
      });
      /* The log only re-lays-out when the editor closes: repainting it on every
         keystroke would move the box out from under his thumb mid-word. */
      elLog.addEventListener("change", function (e) {
        if (e.target.id === "htET") render();
      });
    }

    if (btnCopy) {
      btnCopy.addEventListener("click", function () { copyText(doc(), btnCopy); });
    }

    /* The runtime paints the trade colours and the nav after boot; re-render so a
       page restored before av:ready is not left showing stale words. */
    document.addEventListener("av:ready", function () { render(); });

    return {
      render: render,
      restore: restore,
      doc: doc,
      count: function () { return rows.length; },
      rows: function () { return sorted(); },
      schedulePersist: schedulePersist,
      flush: flush,
      /* Clears the MARKS and leaves the header alone — "next system, same job" is
         what actually happens on a roof, and making him retype his own name and
         his own gauge to log the second unit is how a tool gets closed. */
      clearMarks: function () {
        rows = []; editing = null;
        flush(); render();
        if (cfg.onChange) cfg.onChange();
      }
    };
  }

  window.HoldTest = { mount: mount, esc: esc, todayStr: todayStr, copyText: copyText, fmtSpan: fmtSpan, joinDots: joinDots };
})();
