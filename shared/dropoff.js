/* THE DROP-OFF — the jobsite delivery block, as a FIELD and never as a tool.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS IS NOT A PAGE, and the panel that decided it (2026-08-14, four field
 * lenses + two skeptics, av/AV_SOCIETY.md §THE PANEL):
 *
 * The proposal was a supply-house order page on every trade. The use skeptic
 * killed it on disk in one line — five trades already ship that page under their
 * own names (pull-list, truck-stock, shop list, consumables, supply-house-order),
 * and electrical/tools.js has said "copy it to the warehouse OR THE COUNTER" since
 * the day it landed. What is genuinely unbuilt at that boundary is not the list.
 * It is the TRUCK:
 *
 *   "The flatbed with 20-footers and no boom, the drop at the front curb because
 *    nobody said 'level 2, north stair, in off Elm past the gate,' the driver with
 *    five more stops who takes the load back. That is a real day of four men."
 *
 * And its answer is IDENTICAL for every delivery to that job from every vendor all
 * year — so making a man re-tick it on every order is the ceremony §THE STRICT BAR
 * forbids. It is one STICKY block, typed once per job, riding on every material
 * document the trade already sends. A field. Not a tool. No new storefront row.
 *
 * FOUR RULES IT IS BUILT ON, three of them from the skeptics:
 *
 *  1. TICKING BEATS TYPING (§THE GATE). Where it lands, when it can come, and how
 *     it gets off the truck are CHIPS. Text is only for what no picker can hold —
 *     which floor and which stair, the gate and how to get in, who is meeting it,
 *     who signs — and three of those four are already proved as fields on
 *     electrical/pull-list.html.
 *  2. IT IS AN ASK, NOT A BOOKING. A foreman who ticks "boom · before 7 · level 2
 *     north stair" and taps Copy can believe he has scheduled a crane. He has put
 *     text on a clipboard. The block says so, in the document, every time.
 *  3. NOTHING RATED, NOTHING PRICED, NO COMPANY NAMED. No weights, no capacities,
 *     no reach, no equipment spec, no branch picker, no carrier — this block
 *     describes a place and a time and never a machine's rating (§SAFETY).
 *  4. STICKY, BUT NEVER SILENTLY STALE. A gate code that outlives the job is how a
 *     truck gets sent to last month's address, so the block carries its own
 *     "different job — clear it" and says which job it was filled in for.
 *
 * HOW YOU ADD IT — the drop-in shape shared/feedback.js set as the house standard:
 *
 *     <div id="dropoff"></div>                         <!-- where it renders -->
 *     <script src="../shared/dropoff.js"></script>
 *     var drop = Dropoff.mount({
 *       mount: "dropoff",
 *       key: "toolkit.plumbing.supplyHouseOrder.dropoff.v1",
 *       jobField: "fJob",          // so it can say which job it was filled in for
 *       onChange: refresh          // the page re-renders its own preview
 *     });
 *     drop.show(mode === "Delivery");        // the page owns when it is relevant
 *     ... and in the document builder:  out += drop.text();
 *
 * It brings its own markup and its own <style>, and both are written in the class
 * vocabulary every toolkit page already ships (.head/.hgrid/.f/.seg) against that
 * trade's own CSS variables — so it lands in the trade's palette with no per-page
 * CSS and no per-trade fork.
 */
(function () {
  "use strict";

  var CSS = [
    '.do-wrap{display:none}',
    '.do-wrap.on{display:block}',
    '.do-chips{display:flex;flex-wrap:wrap;gap:6px}',
    '.do-chip{font:inherit;font-size:13px;line-height:1.2;min-height:44px;padding:8px 11px;cursor:pointer;',
    '  background:#fff;border:1px solid var(--line,#BABEB6);border-radius:2px;color:var(--muted,#5D656E);',
    '  display:inline-flex;align-items:center;text-align:left}',
    '.do-chip.on{background:var(--tint,#F1F1EC);border-color:var(--flag,#5D656E);color:var(--ink,#12161A);font-weight:600;',
    '  box-shadow:inset 0 0 0 1px var(--flag,#5D656E)}',
    '.do-chip:focus-visible{outline:2px solid var(--flag,#5D656E);outline-offset:2px}',
    '.do-when{display:flex;gap:6px;align-items:center;flex-wrap:wrap}',
    /* 44px on the clock, not the 38px the text fields inherit: this one is a
       discrete tap target with a stepper inside it, and it is the control a man
       reaches for with a glove on at 6am. */
    '.do-when input[type=time]{flex:0 1 140px;min-width:118px;min-height:44px}',
    '.do-note{font-size:12px;color:var(--muted,#5D656E);margin:9px 0 0}',
    '.do-clear{background:none;border:0;padding:0 4px;min-height:44px;font:inherit;font-size:12px;',
    '  color:var(--muted,#5D656E);text-decoration:underline;cursor:pointer}',
    '.do-head{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:0 0 9px}',
    '.do-head b{font-family:var(--cond,inherit);text-transform:uppercase;letter-spacing:.05em;font-size:15px}',
    '.do-head span{font-family:var(--mono,monospace);font-size:10px;letter-spacing:.12em;text-transform:uppercase;',
    '  color:var(--muted,#5D656E)}'
  ].join('');

  /* THE CHIP AXES. Every option is a PLACE, a CLOCK or a pair of HANDS — never a
   * capacity, a reach, a weight or a piece of equipment by name. "Boom truck" is
   * how a load gets off a flatbed and every hand says it; it is not a rating.
   * The wording is deliberately the field's, not a dispatcher's. */
  var AX = [
    /* EVERY CHIP IS AN ANSWER, NEVER A PROMPT. "Upstairs — say which floor" read
     * fine on the glass and then printed into his message as though he had said
     * it, which is the page putting words in his mouth in front of a vendor. The
     * chip says the place; the line under it is where he says which one. */
    { k: 'land', label: 'Where it lands', wide: true,
      opts: ['Ground — laydown or driveway', 'Inside, ground floor', 'Upstairs',
             'Basement', 'On the roof', 'Job trailer / gang box', 'Curb is fine — we\'ll move it'] },
    { k: 'off', label: 'How it comes off the truck',
      opts: ['Forklift on site', 'Piggyback on the truck', 'Boom or crane', 'By hand off the tail'] },
    { k: 'win', label: 'When it can come',
      opts: ['Any time', 'Morning', 'Afternoon'] }
  ];

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  function mount(cfg) {
    var host = typeof cfg.mount === 'string' ? document.getElementById(cfg.mount) : cfg.mount;
    if (!host) return null;

    if (!document.getElementById('do-css')) {
      var st = document.createElement('style');
      st.id = 'do-css';
      st.textContent = CSS;
      document.head.appendChild(st);
    }

    var id = function (s) { return 'do-' + s; };
    host.className = 'do-wrap';
    host.innerHTML =
      '<div class="head">'
      + '<p class="do-head"><b>How the truck gets in and where it lands</b>'
      + '<span id="' + id('for') + '"></span>'
      /* THE OLD GUARD, WORDED FOR THE PAGE IT IS ON. Without a job card this
       * button is the only fix a stale gate code has, and "different job" is
       * exactly what it means. With one, the words are a lie — a different job
       * has its own block now — and the button becomes a foot-gun: he taps it on
       * the job he is standing on and destroys the answers that are correct.
       * Same escape hatch, honest label. */
      + '<button type="button" class="do-clear" id="' + id('clr') + '" hidden>'
      + (cfg.perJob ? 'clear this job&rsquo;s answers' : 'different job &mdash; clear this')
      + '</button></p>'
      + '<div class="hgrid">'
      + AX.map(function (a) {
          return '<div class="f' + (a.wide ? ' span2' : '') + '"><label>' + esc(a.label) + '</label>'
            + '<div class="do-chips" data-ax="' + a.k + '">'
            + a.opts.map(function (o) {
                return '<button type="button" class="do-chip" data-v="' + esc(o) + '">' + esc(o) + '</button>';
              }).join('')
            + '</div></div>';
        }).join('')
      /* NOT BEFORE is its own control and not a chip, because it is the one answer
       * on this block that is a number: a truck at 6 when the gate opens at 7
       * blocks the street and gets sent away loaded. */
      + '<div class="f"><label>Not before</label><div class="do-when">'
      + '<input id="' + id('nb') + '" type="time" aria-label="Not before"></div></div>'
      /* THE SET LOCATION IN HIS OWN WORDS. A chip can say "upstairs"; only he can
       * say "3rd east, off the north stair, not the lobby" — and that sentence is
       * the difference between a delivery and two men carrying pipe up a
       * stairwell for an hour. */
      + '<div class="f span2"><label>Exactly where <i>(the driver reads this one)</i></label>'
      + '<input id="' + id('where') + '" type="text" autocomplete="off" placeholder="3rd floor east, off the north stair — not the lobby"></div>'
      + '<div class="f span2"><label>Gate / how the truck gets in <i>(the line the whole load lands on)</i></label>'
      + '<input id="' + id('gate') + '" type="text" autocomplete="off" placeholder="Gate 4 off Cedar, code 1180 — dock open till 2, no trucks in the alley before 7"></div>'
      + '<div class="f"><label>Who\'s meeting it <i>(name + cell)</i></label>'
      + '<input id="' + id('meet') + '" type="text" autocomplete="off" placeholder="Sal — 209-555-0166"></div>'
      + '<div class="f"><label>Signs for it if I\'m not there</label>'
      + '<input id="' + id('sign') + '" type="text" autocomplete="off" placeholder="Hector — 209-555-0188"></div>'
      + '<div class="f span2"><div class="do-chips" data-ax="call">'
      + '<button type="button" class="do-chip" data-v="Call me when you\'re 20 out">Call me when you&rsquo;re 20 out</button>'
      + '</div></div>'
      + '</div>'
      + '<p class="do-note">Typed once &mdash; it rides on every delivery to this job. It&rsquo;s an <b>ask</b>, not a booking: nothing here holds a truck, a boom or a time.</p>'
      + '</div>';

    var el = {};
    ['nb', 'where', 'gate', 'meet', 'sign', 'for', 'clr'].forEach(function (k) { el[k] = document.getElementById(id(k)); });

    var TEXT = ['nb', 'where', 'gate', 'meet', 'sign'];
    var state = { land: '', off: '', win: '', call: '', nb: '', where: '', gate: '', meet: '', sign: '', job: '' };

    /* THE KEY IS A VARIABLE, and rule #4 above is the reason. This block was
     * built sticky because its answers are the same all year — and then guarded
     * against the one failure that makes sticky dangerous with a line of text and
     * a button he has to press. shared/jobcard.js was written three days later
     * on exactly that lesson, and its panel threw the button out: a foreman
     * one-handed off a ladder at 6am does not read a notice and does not press a
     * clear button, and the string compare behind the notice cannot fire when he
     * types "warehouse" out of habit at the downtown job. So a page that has a
     * job card hands this block a key PER JOB, the answers travel with the job
     * that owns them, and the guard becomes the tap he was making anyway. A page
     * without one passes a single key and nothing changes for it. */
    var KEY = cfg.key;

    function save() {
      var any = AX.concat([{ k: 'call' }]).some(function (a) { return state[a.k]; })
        || TEXT.some(function (k) { return state[k]; });
      try {
        if (any) localStorage.setItem(KEY, JSON.stringify({ v: 1, s: state }));
        else localStorage.removeItem(KEY);
      } catch (e) {}
      paint();
      if (cfg.onChange) cfg.onChange();
    }

    /* WHICH JOB IT WAS FILLED IN FOR is shown, not guessed at. The block is sticky
     * on purpose — the answer does not change all year — and the failure that
     * makes sticky dangerous is a gate code outliving the job. So it names the job
     * it was filled in for and offers the only honest fix: clear it. */
    function paint() {
      var any = state.land || state.off || state.win || state.call || TEXT.some(function (k) { return state[k]; });
      el.clr.hidden = !any;
      var now = cfg.jobField ? (document.getElementById(cfg.jobField) || {}).value : '';
      now = (now || '').trim();
      /* THE STALENESS LINE IS OFF UNDER A JOB CARD, and not because it is
       * redundant — because it becomes WRONG. Per-job keys mean the name stamped
       * on this record is this job's own earlier name, so the only way the
       * compare can fire is a RENAME: he fixes a typo, and the block tells him
       * his gate code was filled in for a different job. A false alarm on the
       * one control whose whole value is being believed. The chip he tapped is
       * the guard now (shared/jobcard.js: the picker IS the guard). */
      if (!cfg.perJob && any && state.job && now && state.job !== now) {
        el['for'].textContent = 'filled in for ' + state.job;
      } else {
        el['for'].textContent = '';
      }
    }

    host.addEventListener('click', function (e) {
      var c = e.target.closest('.do-chip');
      if (c) {
        var box = c.parentNode, k = box.getAttribute('data-ax');
        var was = c.classList.contains('on');
        [].forEach.call(box.querySelectorAll('.do-chip'), function (x) { x.classList.remove('on'); });
        if (!was) c.classList.add('on');
        state[k] = was ? '' : c.getAttribute('data-v');
        stamp();
        save();
        return;
      }
      if (e.target === el.clr) {
        [].forEach.call(host.querySelectorAll('.do-chip.on'), function (x) { x.classList.remove('on'); });
        TEXT.forEach(function (k) { el[k].value = ''; });
        Object.keys(state).forEach(function (k) { state[k] = ''; });
        save();
      }
    });

    function stamp() {
      if (!cfg.jobField) return;
      var j = (document.getElementById(cfg.jobField) || {}).value;
      if (j && j.trim()) state.job = j.trim();
    }

    TEXT.forEach(function (k) {
      /* Both events, for the reason shared/draft.js already wrote down: `input`
       * misses a control in some engines and `change` misses every keystroke. */
      el[k].addEventListener('input', function () { state[k] = el[k].value; stamp(); save(); });
      el[k].addEventListener('change', function () { state[k] = el[k].value; stamp(); save(); });
    });

    /* PAINT THE GLASS FROM `state`, ALWAYS — never only the keys a record
     * happens to carry. On the way in those are the same thing; on a job switch
     * it is the whole difference, because the answers the OTHER job never gave
     * have to come off the screen rather than linger under a lit chip. */
    function dress() {
      TEXT.forEach(function (k) { el[k].value = state[k] || ''; });
      [].forEach.call(host.querySelectorAll('.do-chips'), function (box) {
        var k = box.getAttribute('data-ax');
        [].forEach.call(box.querySelectorAll('.do-chip'), function (c) {
          c.classList.toggle('on', c.getAttribute('data-v') === state[k]);
        });
      });
    }

    function load() {
      try {
        var raw = localStorage.getItem(KEY);
        if (raw) {
          var p = JSON.parse(raw);
          if (p && p.s) {
            Object.keys(state).forEach(function (k) { if (p.s[k] != null) state[k] = p.s[k]; });
          }
        }
      } catch (e) {}
      dress();
    }

    load();
    paint();

    return {
      show: function (on) { host.classList.toggle('on', !!on); },
      /* SWITCHING JOBS. The page calls this from the job card's onApply, so what
       * is on the glass always belongs to the chip that is lit. The ORDER is the
       * safety property, and it is the one shared/jobcard.js already uses: save
       * the job he is LEAVING first, or the job he arrives at inherits whatever
       * was still in the boxes — which is the leak, wearing the fix's clothes. */
      rekey: function (k) {
        if (!k || k === KEY) return;
        save();
        KEY = k;
        Object.keys(state).forEach(function (n) { state[n] = ''; });
        load();
        paint();
        if (cfg.onChange) cfg.onChange();
      },
      /* The block as it reads in the sent document. Empty when he has said
       * nothing — a heading with nothing under it is noise in a message somebody
       * has to read at 6am. */
      text: function () {
        var lines = [];
        if (state.gate) lines.push('Getting in: ' + state.gate);
        var when = [];
        if (state.win) when.push(state.win);
        if (state.nb) when.push('not before ' + state.nb);
        if (when.length) lines.push('When: ' + when.join(', '));
        var set = [];
        if (state.land) set.push(state.land);
        if (state.where) set.push(state.where);
        if (set.length) lines.push('Set it: ' + set.join(', '));
        if (state.off) lines.push('Off the truck: ' + state.off);
        if (state.meet) lines.push('Meeting the truck: ' + state.meet);
        if (state.sign) lines.push('Signs for it if I\'m not there: ' + state.sign);
        if (state.call) lines.push(state.call + '.');
        if (!lines.length) return '';
        return '\n\nHOW IT GETS IN AND WHERE IT LANDS\n' + lines.map(function (l) { return '- ' + l; }).join('\n')
          + '\n(That\'s what we need, not a booking — tell me if any of it doesn\'t work.)';
      },
      state: function () { return state; }
    };
  }

  window.Dropoff = { mount: mount };
})();
