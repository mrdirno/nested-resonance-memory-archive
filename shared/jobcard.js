/* THE JOB CARD — two live jobs, one phone, and the answers that belong to each.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHAT WAS ON DISK BEFORE THIS FILE, and it was on disk SIX TIMES:
 *
 *   var STICKY = ["fJob", "fBy", "fHow", "fAccess", "fSigner", "fCharge", "fPO"];
 *   var SKEY = "toolkit.<trade>.<page>.header.v1";
 *
 * Twenty byte-identical lines hand-copied into concrete/mix-order, electrical/
 * pull-list, framing/the-load, hvac/truck-stock, low-voltage/consumables and
 * masonry/yard-call — the exact fork shared/checklist-request.js was extracted
 * to stop, living in the one part of those pages the engine never took over.
 * Its own comment says the right thing: "the answers that are the same every
 * morning for the life of a job." The code does not do what the comment says.
 * It remembers the answers for the life of a PHONE.
 *
 * THE PANEL THAT REDESIGNED IT (2026-08-16, four lenses — a two-job commercial
 * foreman, a service tech, a supply-house dispatcher, and a skeptic told to kill
 * it; av/AV_SOCIETY.md §THE PANEL). The proposal put to them was a staleness
 * BANNER: notice the job name changed, say "filled in for <job>", offer a clear
 * button. The foreman killed the banner and gave us the shape instead:
 *
 *   "A banner has to be read and I won't always read it one-handed off a ladder
 *    at 6am. I will always notice the block change when I'm the one who tapped
 *    the job that changed it. Put the safety in the action I'm already taking,
 *    not in a warning stacked on top of it."
 *
 * And he broke the name-match guard before it was built. He types the job box
 * differently every week — "Meridian TI" on day one, "Meridian" or "435 Bryant"
 * on day forty — and, worse, types "warehouse" out of habit while standing at
 * the downtown job. A string compare calls that a MATCH and stays silent, which
 * is the one case that had to fire. A guard that compares free text to free text
 * is not a guard.
 *
 * SO THE PICKER IS THE GUARD. Every job is a chip. Tapping one swaps the gate
 * code, the signer and the cost code in front of him, in the fields he is about
 * to send. He is not asked to notice anything: he did it.
 *
 * TWO SCOPES, and getting them wrong is the whole failure:
 *
 *  · perJob  — travels with the job and NOTHING else. Gate code, who signs,
 *              cost code, PO. The warehouse's gate code has no business being on
 *              a downtown order.
 *  · device  — the same on every job on this phone. "Requested by" is him.
 *
 * THERE WAS A THIRD SCOPE FOR ABOUT AN HOUR AND A GATE KILLED IT. The foreman
 * was right that "how it gets here" (delivered / will-call / the shop runs it
 * out) does not belong on a job — "that is a decision about this order, not a
 * fact about the job... ask it fresh every single time" — and it had been in all
 * six STICKY lists since those pages shipped. So the first cut gave it a `fresh`
 * scope: blanked to the page's default on every load.
 *
 * tools/toolkit-gates/order-live-header.mjs failed that on three pages in one
 * run, and the failure it names is worse than the one being fixed: a field
 * printed in the document has to survive a reload. A man picks will-call, ticks
 * forty lines over twenty minutes, iOS evicts the tab, and he comes back to all
 * forty lines intact and the delivery method silently back on "Deliver to site".
 * He would never look, because everything he actually worked on came back.
 *
 * The right home was neither scope: it rides THE LIST, in the engine's own
 * `persistExtra`, reset by Clear — the one action that means "different order".
 * Not remembered across jobs, not lost across a reload. This module holds no
 * `fresh` list, and the reason is written here so the next page does not invent
 * one again.
 *
 * A NEW JOB STARTS EMPTY. That is the safety property, and it is why "+ New job"
 * is a deliberate tap rather than something inferred from him editing the name
 * box. Typing in the name box RENAMES the job he is on — which is what a man
 * fixing a typo means — and can never silently mint a second card carrying the
 * first one's gate code.
 *
 * NOTHING IS LOST ON THE WAY IN. Each page hands over its old per-page key; the
 * first mount adopts it as job #1, keeps the device fields, and drops the `fresh`
 * ones on the floor. A man who has had a gate code saved since June opens the
 * page and it is still there, now sitting on a chip with his job's name on it.
 *
 * HOW YOU ADD IT — the drop-in shape shared/feedback.js set as the house
 * standard, and it degrades to nothing if the script is absent:
 *
 *     <div id="jobcard"></div>
 *     <script src="../shared/jobcard.js"></script>
 *     JobCard.mount({
 *       mount: "jobcard",
 *       trade: "electrical",
 *       nameField: "fJob",                                  // labels the chip
 *       perJob: ["fAccess", "fSigner", "fCharge", "fPO"],
 *       device: ["fBy"],
 *       legacyKey: "toolkit.electrical.pullList.header.v1",  // adopted once
 *       onApply: function () { api.refresh(); }              // repaint the preview
 *     });
 *
 * It brings its own markup and its own <style>, written in the class vocabulary
 * every toolkit page already ships against that trade's CSS variables, so it
 * lands in the trade's palette with no per-page CSS and no per-trade fork.
 *
 * NOT HERE, DELIBERATELY: any account, any sync, any network. The cards are on
 * this phone and they never leave it (§SAFETY). A job card is a gate code and a
 * man's cell number — the two things this program will never put on a wire.
 */
(function () {
  "use strict";

  /* SIX CARDS IS THE CEILING, oldest-touched dropped first. Not an arbitrary
   * number: the chip row has to stay one thumb-scan on a 320px screen, and the
   * foreman who defined this shape runs "two, maybe three live jobs at once."
   * Six is double his worst week and still fits without a scroller. */
  var MAX_JOBS = 6;

  var CSS = [
    '.jc{margin:0 0 12px}',
    '.jc-row{display:flex;flex-wrap:wrap;gap:6px;align-items:stretch}',
    '.jc-chip{font:inherit;font-size:13px;line-height:1.25;min-height:44px;padding:8px 12px;cursor:pointer;',
    '  background:#fff;border:1px solid var(--line,#BABEB6);border-radius:2px;color:var(--muted,#5D656E);',
    '  display:inline-flex;align-items:center;text-align:left;max-width:100%;white-space:normal;',
    '  overflow-wrap:anywhere}',
    /* THE LIT CHIP IS DRAWN IN `--deep`, NOT `--flag`, AND THE NUMBERS ARE WHY.
     * This rule read `border-color:var(--flag)` + the same colour as an inset
     * ring for its whole life. `--flag` is the trade ACCENT, and every accent on
     * this rack is picked and measured against the DARK NAV (bar 7:1) — which
     * makes it, by construction, a LIGHT colour, and this chip is drawn on
     * WHITE. Measured accent-against-white across all twelve trades: masonry
     * 1.37 · sitework 1.30 · gc 1.51 · hvac 1.65 · av 1.74 · creative 1.84 ·
     * concrete 1.91 · framing 2.01 · low-voltage 2.01 · roofing 2.05 ·
     * electrical 2.28 — and plumbing 3.58. ELEVEN OF TWELVE under 3:1, and the
     * twelfth is the only trade the sibling block shipped on, which is exactly
     * why nobody caught it. Against the grey it replaces (--line #BABEB6) the
     * swap is 1.01–1.45:1 on those eleven: a hue change with no luminance step
     * at all, invisible in sun, on a dirty screen, or to anyone with a colour
     * vision deficiency. The tint behind it adds 1.07–1.19:1. So the lit state
     * was resting on darker, bolder TEXT alone.
     * That is not cosmetic on THIS control. This chip is WHICH JOB AM I ON, and
     * the answers behind it are a gate code and a PO. `--deep` is the token
     * every trade already ships for the dark half of its accent and it measures
     * 5.21–8.46:1 against white on all twelve — a real luminance step, in the
     * trade's own colour, with no new token and no per-trade fork. The fallback
     * chain keeps a page that somehow ships without `--deep` exactly where it
     * was. */
    '.jc-chip.on{background:var(--tint,#F1F1EC);border-color:var(--deep,var(--flag,#5D656E));color:var(--ink,#12161A);',
    '  font-weight:600;box-shadow:inset 0 0 0 1px var(--deep,var(--flag,#5D656E))}',
    '.jc-chip:focus-visible{outline:2px solid var(--deep,var(--flag,#5D656E));outline-offset:2px}',
    '.jc-new{border-style:dashed}',
    '.jc-lab{font-family:var(--mono,monospace);font-size:10px;letter-spacing:.12em;text-transform:uppercase;',
    '  color:var(--muted,#5D656E);margin:0 0 6px;display:block}',
    '.jc-note{font-size:12px;color:var(--muted,#5D656E);margin:7px 0 0}',
    '.jc-drop{background:none;border:0;padding:0 4px;min-height:44px;font:inherit;font-size:12px;',
    '  color:var(--muted,#5D656E);text-decoration:underline;cursor:pointer}'
  ].join('');

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }
  function $(id) { return document.getElementById(id); }

  function mount(cfg) {
    var host = typeof cfg.mount === 'string' ? $(cfg.mount) : cfg.mount;
    if (!host) return null;

    var KEY = 'toolkit.' + cfg.trade + '.jobcard.v1';
    var PER = (cfg.perJob || []).slice();
    var DEV = (cfg.device || []).slice();
    var NAME = cfg.nameField;

    if (!document.getElementById('jc-css')) {
      var st = document.createElement('style');
      st.id = 'jc-css';
      st.textContent = CSS;
      document.head.appendChild(st);
    }

    /* ── the store ─────────────────────────────────────────────────────────── */
    var store = { v: 1, seq: 0, cur: '', device: {}, jobs: [] };

    function read() {
      var raw = null;
      try { raw = localStorage.getItem(KEY); } catch (e) { return false; }
      if (!raw) return false;
      var p;
      try { p = JSON.parse(raw); } catch (e) { return false; }
      if (!p || !p.jobs) return false;
      store = {
        v: 1,
        seq: p.seq || p.jobs.length,
        cur: p.cur || '',
        device: p.device || {},
        jobs: p.jobs.slice(0, MAX_JOBS)
      };
      return true;
    }

    function write() {
      try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
    }

    /* ADOPTING THE OLD KEY. The page kept one flat bag of field values under its
     * own name. It becomes job #1 wearing whatever was in the name box, the
     * device fields come across as device fields, and the `fresh` ones are left
     * behind — the whole point of calling them fresh. Read once and never again:
     * the old key is left on the device untouched, because a man who somehow
     * lands back on an older build should still find his gate code there. */
    function adopt() {
      if (!cfg.legacyKey) return false;
      var raw = null;
      try { raw = localStorage.getItem(cfg.legacyKey); } catch (e) { return false; }
      if (!raw) return false;
      var old;
      try { old = JSON.parse(raw); } catch (e) { return false; }
      if (!old || typeof old !== 'object') return false;

      /* THE OTHER SHAPE THIS CODEBASE WRITES. Six pages hand-rolled the sticky
       * header as a flat bag of field ids, which is what the lines below read.
       * A page that kept the same header through shared/draft.js wrapped it —
       * {v:1, s:{fJob:"…", fPO:"…"}} — so a flat read finds nothing, adopt()
       * returns false, and a PO he has had saved since spring is dropped on his
       * first load of the new build. Silently: he does not get an error, he gets
       * an empty box, and the only man who notices is the one whose order goes
       * out without the number his office needs.
       *
       * So the unwrap lives HERE and not in a per-page shim, because a shim is
       * the fork this module was extracted to stop. The guard is exact rather
       * than hopeful — the top level holds NONE of the ids we came for, and `s`
       * is an object — so a flat bag that happens to carry an `s` key is never
       * mistaken for a wrapper. */
      var want = PER.concat(DEV).concat(NAME ? [NAME] : []);
      var flat = want.some(function (id) { return old[id] != null; });
      if (!flat && old.s && typeof old.s === 'object') old = old.s;

      DEV.forEach(function (id) { if (old[id]) store.device[id] = old[id]; });

      var f = {}, any = false;
      PER.forEach(function (id) { if (old[id]) { f[id] = old[id]; any = true; } });
      var nm = (old[NAME] || '').trim();
      if (!nm && !any) return false;

      store.seq = 1;
      store.jobs = [{ id: 'j1', name: nm, at: 1, f: f }];
      store.cur = 'j1';
      write();
      return true;
    }

    function cur() {
      for (var i = 0; i < store.jobs.length; i++) {
        if (store.jobs[i].id === store.cur) return store.jobs[i];
      }
      return null;
    }

    /* THE CHIP'S WORDS. A card with no name yet is not "Untitled" — that is
     * software vocabulary and it reads as a bug. It is the job he has not named,
     * and saying so is honest and one tap from fixed. */
    function label(j) {
      var n = (j.name || '').trim();
      return n || 'This job — name it';
    }

    /* ── the fields ────────────────────────────────────────────────────────── */
    function setVal(id, v) {
      var el = $(id);
      if (!el) return;
      /* A <select> can only hold an option it has. Carrying a value from a card
       * saved when the list was different would silently land on option zero,
       * which prints a delivery method he never picked. */
      if (el.tagName === 'SELECT') {
        var ok = [].some.call(el.options, function (o) { return o.value === v; });
        if (!ok) return;
      }
      el.value = v == null ? '' : v;
    }

    function apply() {
      var j = cur();
      PER.forEach(function (id) { setVal(id, j && j.f ? j.f[id] : ''); });
      DEV.forEach(function (id) { setVal(id, store.device[id] || ''); });
      if (NAME) setVal(NAME, j ? (j.name || '') : '');
      paint();
      if (cfg.onApply) cfg.onApply();
    }

    function collect() {
      var j = cur();
      if (j) {
        j.f = j.f || {};
        PER.forEach(function (id) { var el = $(id); if (el) j.f[id] = el.value; });
        if (NAME) {
          var nel = $(NAME);
          if (nel) j.name = nel.value;
        }
        j.at = ++store.seq;
      }
      DEV.forEach(function (id) { var el = $(id); if (el) store.device[id] = el.value; });
      write();
      paint();
    }

    /* ── the chips ─────────────────────────────────────────────────────────────
     * A PICKER WITH ONE THING IN IT IS NOT A PICKER, IT IS CHROME. Seen on the
     * real page at 390px before this shipped: with one job, the row rendered a
     * label, a lit chip carrying the full job name, and the Job box directly
     * underneath repeating that same string verbatim. Two identical lines
     * stacked, on the most valuable glass on the page, to let him choose between
     * one option. Most men have one job most of the time, so that was the state
     * almost everybody would meet first.
     *
     * So the switcher appears when there is something to switch. At one job the
     * block is a single dashed affordance and nothing else — which still teaches
     * the capability, because the button says what it does. The moment he taps
     * it the first job's chip appears beside the new one and the row becomes the
     * picker it was always going to be. */
    function paint() {
      var many = store.jobs.length > 1;
      var room = store.jobs.length < MAX_JOBS;
      host.className = 'jc';
      host.innerHTML =
        (many ? '<span class="jc-lab">' + esc(cfg.label || 'Job') + '</span>' : '')
        + '<div class="jc-row" role="group" aria-label="' + esc(cfg.label || 'Job') + '">'
        + (many
            ? store.jobs.map(function (j) {
                return '<button type="button" class="jc-chip' + (j.id === store.cur ? ' on' : '') + '"'
                  + ' data-j="' + esc(j.id) + '"'
                  + (j.id === store.cur ? ' aria-current="true"' : '') + '>' + esc(label(j)) + '</button>';
              }).join('')
            : '')
        + (room
            ? '<button type="button" class="jc-chip jc-new" data-new="1">+ '
              + (many ? 'New job' : 'Another job') + '</button>'
            : '')
        + '</div>'
        + (many
            ? '<p class="jc-note">Tapping a job swaps the gate, who signs and the cost code below it.'
              + ' <button type="button" class="jc-drop" data-drop="1">Finished with this one &mdash; drop it</button></p>'
            : '');
    }

    host.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b || !host.contains(b)) return;

      if (b.getAttribute('data-new')) {
        /* SAVE THE ONE HE IS LEAVING FIRST. Minting the new card before
         * collecting would hand the next job whatever is still on the glass. */
        collect();
        if (store.jobs.length >= MAX_JOBS) {
          store.jobs.sort(function (a, c) { return (a.at || 0) - (c.at || 0); });
          store.jobs.shift();
        }
        var id = 'j' + (++store.seq);
        store.jobs.push({ id: id, name: '', at: store.seq, f: {} });
        store.cur = id;
        write();
        apply();
        /* Land the thumb in the box the new card exists to have filled. */
        var nel = NAME ? $(NAME) : null;
        if (nel) { nel.focus(); }
        return;
      }

      if (b.getAttribute('data-drop')) {
        var j = cur();
        if (!j) return;
        store.jobs = store.jobs.filter(function (x) { return x.id !== j.id; });
        store.cur = store.jobs.length ? store.jobs[store.jobs.length - 1].id : '';
        if (!store.jobs.length) {
          store.seq++;
          store.jobs = [{ id: 'j' + store.seq, name: '', at: store.seq, f: {} }];
          store.cur = store.jobs[0].id;
        }
        write();
        apply();
        return;
      }

      var jid = b.getAttribute('data-j');
      if (jid && jid !== store.cur) {
        collect();
        store.cur = jid;
        write();
        apply();
      }
    });

    /* ── wiring ────────────────────────────────────────────────────────────── */
    var loaded = read();
    if (!loaded) {
      if (!adopt()) {
        store.seq = 1;
        store.jobs = [{ id: 'j1', name: '', at: 1, f: {} }];
        store.cur = 'j1';
      }
    }
    if (!store.jobs.length) {
      store.seq = 1;
      store.jobs = [{ id: 'j1', name: '', at: 1, f: {} }];
      store.cur = 'j1';
    }
    if (!cur()) store.cur = store.jobs[0].id;

    /* BOTH EVENTS, for the reason shared/draft.js already wrote down: `input`
     * misses a <select> in some engines and `change` misses every keystroke. */
    PER.concat(DEV).concat(NAME ? [NAME] : []).forEach(function (id) {
      var el = $(id);
      if (!el) return;
      el.addEventListener('input', collect);
      el.addEventListener('change', collect);
    });

    apply();

    return {
      apply: apply,
      collect: collect,
      /* What the page needs when it wants to name the card in its own copy. */
      current: function () { var j = cur(); return j ? { id: j.id, name: j.name } : null; },
      count: function () { return store.jobs.length; }
    };
  }

  window.JobCard = { mount: mount };
})();
