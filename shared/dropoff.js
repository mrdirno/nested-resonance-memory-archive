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
 * V2 (2026-08-19) — THE DISPATCHER'S THREE, AND THE LOAD CLASS. The receiving
 * lens on the 2026-08-16 panel (eighteen years building the next day's loads)
 * read v1's printed block and named what a driver and a load-builder each
 * needed from it, and the panel that scored v2 (dispatcher · two-class foreman ·
 * skeptic, av/AV_SOCIETY.md §THE PANEL) held it to these:
 *
 *  5. TWO READERS, ONE ORDER. The driver reads it at 5:50am with the truck
 *     already loaded; the load-builder read it last night. So the document goes
 *     gate → who to call when the gate fails → the paperwork → set-it location →
 *     who signs FIRST, and "off the truck" / "when" after — never the other way
 *     round, which is how v1 printed it.
 *  6. ONE CLOCK. `When: morning, not before 07:00` under a gate line that already
 *     said "no trucks before 7" is two clocks for one fact, and a driver trusts
 *     the wrong one after an edit. The not-before control is the only place a
 *     time lives, it prints ON the gate line, and the gate placeholder no longer
 *     teaches the double entry. "When it can come" is a dispatch WINDOW, printed
 *     lower down, and never carries a time.
 *  7. THE PAPERWORK LAYER. "To the foreman 'how you get in' IS the code. To me
 *     the code is step one of two" — a driver with the exact right code sat an
 *     hour because security wanted a COI that morning. So the block carries
 *     what the driver needs BEFORE the gate opens, as multi-select chips, and
 *     every one of them is an ASK aimed back at the supply house, never a
 *     status we could know (the getting-in handback rule, one level down:
 *     "COI on file — tell me if it isn't", not "COI: on file").
 *  8. THE LOAD CLASS. "Forklift on site" and "Boom or crane" are not real options
 *     for a box of J-hooks. For small goods the axis is not how it LIFTS, it is
 *     WHO TAKES CUSTODY — so `load: "small"` swaps the place/lift pair for one
 *     custody axis, and the free text under it stays, because chips have no
 *     grammar for "then", "unless" or "but call first".
 *  9. IT REPLACES, IT NEVER SITS BESIDE. Six order pages shipped a hand-rolled
 *     "how to get in" textarea and a signer box. Mounting this block beside them
 *     is two gate boxes on one page, worse than none — so a page that mounts it
 *     REMOVES those, and `seed` hands the block what the job card still holds
 *     from them (gate ← the old textarea, signer ← the old box), once, so a gate
 *     code typed in June is on the glass the first morning and never again asks
 *     to be typed. A seeded record is kept even when emptied: clearing the block
 *     must not resurrect the text he just cleared.
 *
 * HOW YOU ADD IT — the drop-in shape shared/feedback.js set as the house standard:
 *
 *     <div id="dropoff"></div>                         <!-- where it renders -->
 *     <script src="../shared/dropoff.js"></script>
 *     var drop = Dropoff.mount({
 *       mount: "dropoff",
 *       key: "toolkit.plumbing.supplyHouseOrder.dropoff.v1",
 *       jobField: "fJob",          // so it can say which job it was filled in for
 *       load: "truck",             // or "small" — a box, a bag, a reel (rule 8)
 *       perJob: true,              // under a job card: keyed per job via rekey()
 *       seed: function () {        // optional — what the job card still holds
 *         return { gate: jc.stash("fAccess"), sign: jc.stash("fSigner") };
 *       },
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
    '.do-bare{margin:9px 0 12px}',
    /* The gate textarea dresses itself: plumbing styles `.f input,.f select`
       and not textarea, and a box in the browser's default font beside the
       block's own inputs is the kind of seam a man reads as "broken". */
    '.do-wrap .f textarea{width:100%;font:inherit;font-size:14px;padding:8px 9px;border:1px solid var(--line,#BABEB6);',
    '  border-radius:2px;background:#fff;color:var(--ink,#12161A);min-height:44px;resize:vertical}',
    '.do-wrap .f textarea:focus{outline:2px solid var(--flag,#575E67);outline-offset:-1px}',
    '.do-chips{display:flex;flex-wrap:wrap;gap:6px}',
    '.do-chip{font:inherit;font-size:13px;line-height:1.2;min-height:44px;padding:8px 11px;cursor:pointer;',
    '  background:#fff;border:1px solid var(--line,#BABEB6);border-radius:2px;color:var(--muted,#575E67);',
    '  display:inline-flex;align-items:center;text-align:left}',
    /* DRAWN IN `--deep`, for the reason measured and written out in full at the
     * same rule in shared/jobcard.js: the accent is picked against the DARK nav,
     * so it is a light colour, and this chip is on WHITE — 1.30–2.28:1 on eleven
     * of the twelve trades, and the twelfth (plumbing, 3.58) is the only trade
     * this block had ever shipped on, which is why the defect survived. */
    '.do-chip.on{background:var(--tint,#F1F1EC);border-color:var(--deep,var(--flag,#575E67));color:var(--ink,#12161A);font-weight:600;',
    '  box-shadow:inset 0 0 0 1px var(--deep,var(--flag,#575E67))}',
    '.do-chip:focus-visible{outline:2px solid var(--deep,var(--flag,#575E67));outline-offset:2px}',
    '.do-when{display:flex;gap:6px;align-items:center;flex-wrap:wrap}',
    /* 44px on the clock, not the 38px the text fields inherit: this one is a
       discrete tap target with a stepper inside it, and it is the control a man
       reaches for with a glove on at 6am. */
    '.do-when input[type=time]{flex:0 1 140px;min-width:118px;min-height:44px}',
    '.do-note{font-size:12px;color:var(--muted,#575E67);margin:9px 0 0}',
    '.do-clear{background:none;border:0;padding:0 4px;min-height:44px;font:inherit;font-size:12px;',
    '  color:var(--muted,#575E67);text-decoration:underline;cursor:pointer}',
    '.do-head{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:0 0 9px}',
    '.do-head b{font-family:var(--cond,inherit);text-transform:uppercase;letter-spacing:.05em;font-size:15px}',
    '.do-head span{font-family:var(--mono,monospace);font-size:10px;letter-spacing:.12em;text-transform:uppercase;',
    '  color:var(--muted,#575E67)}'
  ].join('');

  /* THE CHIP AXES. Every option is a PLACE, a CLOCK, a pair of HANDS or a
   * QUESTION aimed back at the supply house — never a capacity, a reach, a
   * weight or a piece of equipment by name. "Boom truck" is how a load gets off
   * a flatbed and every hand says it; it is not a rating.
   * The wording is deliberately the field's, not a dispatcher's. */
  /* EVERY CHIP IS AN ANSWER, NEVER A PROMPT. "Upstairs — say which floor" read
   * fine on the glass and then printed into his message as though he had said
   * it, which is the page putting words in his mouth in front of a vendor. The
   * chip says the place; the line under it is where he says which one. */
  var AX_TRUCK = [
    { k: 'land', label: 'Where it lands', wide: true,
      opts: ['Ground — laydown or driveway', 'Inside, ground floor', 'Upstairs',
             'Basement', 'On the roof', 'Job trailer / gang box', 'Curb is fine — we\'ll move it'] },
    { k: 'off', label: 'How it comes off the truck',
      opts: ['Forklift on site', 'Piggyback on the truck', 'Boom or crane', 'By hand off the tail'] }
  ];
  /* SMALL GOODS (rule 8). A box of J-hooks does not "land" and nothing lifts it;
   * the whole question is whose hands it ends up in, and "left at the drop
   * point" is a different answer from "security signs for it" on the morning it
   * is not there. ONE axis, not two, because "with the super" is both a place
   * and a pair of hands and two axes would ask it twice. "Left at a drop point"
   * says nothing about a signature on purpose: the panel's foreman lens caught
   * the first wording ("— no signature needed") contradicting the signer box
   * still filled from a truck order in March, in the same printed message. The
   * sign field alone answers who signs. FOUR, not five: a fifth chip, "Inside at
   * the room — I'll say where", replaced no typing (the free-text line under it
   * already says which room) and sent a lone driver into a building with no
   * stated escort — the skeptic and the dispatcher killed it independently. */
  var AX_SMALL = [
    { k: 'hand', label: 'Who takes it / where it goes', wide: true,
      opts: ['Hand it to me or my guy — call first', 'Left at a drop point',
             'With the super / job trailer', 'Security / front desk'] }
  ];
  var AX_WIN = { k: 'win', label: 'When it can come', opts: ['Any time', 'Morning', 'Afternoon'] };
  /* THE PAPERWORK LAYER (rule 7). Multi-select, because a site that wants a COI
   * usually wants the sign-in too. Every chip ends aimed at HIM — the supply
   * house — as a thing to have or to tell us, never as a status this page could
   * know. "COI on file" alone would read as a tick that handled it. */
  /* "Before the gate", never "before the gate OPENS" — "opens" is a time word a
   * few lines under the one clock (panel, dispatcher). The two that cost the
   * supply house LEAD TIME (a certificate, a carrier on the GC's list) sit
   * together at the front, the three the driver does at the gate after. And the
   * COI line is an ASK before it is anything else: "COI on file — tell me if it
   * isn't" skims as "COI on file" — the exact tick-that-sounds-satisfied the
   * getting-in handback rule banned (panel, skeptic). */
  var AX_PAPER = { k: 'paper', label: 'Before the gate — what your driver needs', sub: 'tick any that apply', wide: true, multi: true,
    opts: ['Tell me if our COI isn\'t on file with you yet', 'Tell me who\'s hauling — only approved carriers get in',
           'Driver signs in at the trailer / security', 'Hard hat + vest past the gate',
           'Site orientation before the first drop'] };

  function axes(load) {
    return (load === 'small' ? AX_SMALL : AX_TRUCK).concat([AX_WIN, AX_PAPER]);
  }

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

    var LOAD = cfg.load === 'small' ? 'small' : 'truck';
    var AX = axes(LOAD);
    var MULTI = {};
    AX.forEach(function (a) { if (a.multi) MULTI[a.k] = true; });

    var id = function (s) { return 'do-' + s; };
    function chips(a) {
      /* Every other row on this block is pick-one, and a man trained by four of
       * them taps "hard hat", watches it light, and walks away believing he
       * answered — so the one multi row SAYS it is one (panel, foreman lens). */
      return '<div class="f' + (a.wide ? ' span2' : '') + '"><label>' + esc(a.label) + (a.sub ? ' <i>(' + esc(a.sub) + ')</i>' : '') + '</label>'
        + '<div class="do-chips" data-ax="' + a.k + '"' + (a.multi ? ' data-multi="1"' : '') + '>'
        + a.opts.map(function (o) {
            return '<button type="button" class="do-chip" data-v="' + esc(o) + '"' + (a.multi ? ' aria-pressed="false"' : '') + '>' + esc(o) + '</button>';
          }).join('')
        + '</div></div>';
    }
    host.className = 'do-wrap';
    host.innerHTML =
      /* `bare` drops the block's own card. A page that mounts it INSIDE its
       * header's "typed once, saved with this job" drawer — where the textarea it
       * replaced used to live — already has the card; a second border inside the
       * first is a box in a box. */
      '<div class="' + (cfg.bare ? 'do-bare' : 'head') + '">'
      + '<p class="do-head"><b>' + (LOAD === 'small' ? 'How it gets in and who takes it' : 'How the truck gets in and where it lands') + '</b>'
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
      /* THE GATE FIRST, because it is the first thing the driver reads (rule 5),
       * and its placeholder carries no time (rule 6): the clock is the control
       * under it, and an example that typed "before 7" here taught the double
       * entry the dispatcher named. */
      + '<div class="f span2"><label>Gate / how the ' + (LOAD === 'small' ? 'driver' : 'truck') + ' gets in <i>(the line the whole ' + (LOAD === 'small' ? 'order' : 'load') + ' lands on)</i></label>'
      /* A TEXTAREA, NOT A LINE: "Dock off Cedar till 2, then gate 4 — call when
       * you're 20 out, IDF 3 is badge-only" is a four-clause sentence, and the
       * box that replaced a 2-row textarea must not shrink the one answer the
       * chips cannot carry into a line that scrolls sideways (panel, foreman). */
      + '<textarea id="' + id('gate') + '" rows="2" autocomplete="off" placeholder="Gate 4 off Cedar, code 1180 — dock open till 2, in off Elm past the trailer"></textarea></div>'
      /* NOT BEFORE is its own control and not a chip, because it is the one answer
       * on this block that is a number: a truck at 6 when the gate opens at 7
       * blocks the street and gets sent away loaded. It is also the ONLY clock. */
      + '<div class="f"><label>Not before <i>(the one clock on this block)</i></label><div class="do-when">'
      + '<input id="' + id('nb') + '" type="time" aria-label="Not before"></div></div>'
      + '<div class="f"><label>Who\'s meeting it <i>(the driver calls this if the gate\'s wrong &mdash; name + cell)</i></label>'
      + '<input id="' + id('meet') + '" type="text" autocomplete="off" placeholder="Sal — 209-555-0166"></div>'
      /* THE PLACE CHIPS, THEN THE PLACE IN HIS OWN WORDS, ADJACENT. A chip can
       * say "upstairs"; only he can say "3rd east, off the north stair, not the
       * lobby" — and that sentence is the difference between a delivery and two
       * men carrying pipe up a stairwell for an hour. Chips never replace this
       * line (rule 8): "till 2, then gate 4" is a sequence and "IDF 3 is
       * badge-only" is an exception, and no picker has a grammar for either. */
      + chips(AX[0])
      + '<div class="f span2"><label>Exactly where <i>(the driver reads this one)</i></label>'
      + '<input id="' + id('where') + '" type="text" autocomplete="off" placeholder="'
      + (LOAD === 'small' ? 'IDF 3, 3rd floor east — it\'s badge-only, call first' : '3rd floor east, off the north stair — not the lobby') + '"></div>'
      + AX.slice(1).map(chips).join('')
      + '<div class="f"><label>Signs for it if I\'m not there</label>'
      + '<input id="' + id('sign') + '" type="text" autocomplete="off" placeholder="Hector — 209-555-0188"></div>'
      + '<div class="f"><div class="do-chips" data-ax="call">'
      + '<button type="button" class="do-chip" data-v="Call me when you\'re 20 out">Call me when you&rsquo;re 20 out</button>'
      + '</div></div>'
      + '</div>'
      + '<p class="do-note">Typed once &mdash; it rides on every delivery to this job. It&rsquo;s an <b>ask</b>, not a booking: nothing here holds a truck, a boom or a time.</p>'
      + '</div>';

    var el = {};
    ['nb', 'where', 'gate', 'meet', 'sign', 'for', 'clr'].forEach(function (k) { el[k] = document.getElementById(id(k)); });

    var TEXT = ['nb', 'where', 'gate', 'meet', 'sign'];
    var CHIP = AX.map(function (a) { return a.k; }).concat(['call']);
    function blank() {
      var s = { nb: '', where: '', gate: '', meet: '', sign: '', job: '' };
      CHIP.forEach(function (k) { s[k] = MULTI[k] ? [] : ''; });
      return s;
    }
    var state = blank();
    function has(k) { var v = state[k]; return MULTI[k] ? !!(v && v.length) : !!v; }
    function anySet() {
      return CHIP.some(has) || TEXT.some(function (k) { return !!state[k]; });
    }

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
    /* SEEDED ONCE, KEPT FOREVER (rule 9). `seeded` is stamped on a record the
     * moment `cfg.seed` filled it; from then on the record is written even when
     * it is empty, because a removed key would look like a never-seen job and
     * re-seed the very text he just cleared. */
    var seeded = false;

    function save() {
      var any = anySet();
      try {
        if (any || seeded) localStorage.setItem(KEY, JSON.stringify({ v: 2, s: state, m: seeded ? 1 : 0 }));
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
      var any = anySet();
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
        if (MULTI[k]) {
          /* A multi chip toggles ITSELF and leaves its siblings alone; the state
           * is the list of lit chips in the order they are drawn, so the printed
           * line reads the same every time whatever order he tapped them in. */
          c.classList.toggle('on', !was);
          c.setAttribute('aria-pressed', was ? 'false' : 'true');
          state[k] = [].map.call(box.querySelectorAll('.do-chip.on'), function (x) { return x.getAttribute('data-v'); });
        } else {
          [].forEach.call(box.querySelectorAll('.do-chip'), function (x) { x.classList.remove('on'); });
          if (!was) c.classList.add('on');
          state[k] = was ? '' : c.getAttribute('data-v');
        }
        stamp();
        save();
        return;
      }
      if (e.target === el.clr) {
        [].forEach.call(host.querySelectorAll('.do-chip.on'), function (x) {
          x.classList.remove('on');
          if (x.hasAttribute('aria-pressed')) x.setAttribute('aria-pressed', 'false');
        });
        TEXT.forEach(function (k) { el[k].value = ''; });
        state = blank();
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
          var v = c.getAttribute('data-v');
          var on = MULTI[k] ? (state[k] || []).indexOf(v) !== -1 : v === state[k];
          c.classList.toggle('on', on);
          if (c.hasAttribute('aria-pressed')) c.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
      });
    }

    function take(p) {
      Object.keys(state).forEach(function (k) {
        if (p[k] == null) return;
        if (MULTI[k]) state[k] = Array.isArray(p[k]) ? p[k].slice() : (p[k] ? [String(p[k])] : []);
        else state[k] = typeof p[k] === 'string' ? p[k] : '';
      });
    }

    function load() {
      var found = false;
      seeded = false;
      try {
        var raw = localStorage.getItem(KEY);
        if (raw) {
          var p = JSON.parse(raw);
          if (p && p.s) { found = true; take(p.s); seeded = !!p.m; }
        }
      } catch (e) {}
      /* A NEVER-SEEN JOB ASKS THE PAGE WHAT IT ALREADY KNOWS (rule 9). Only when
       * no record exists under this key — a record that is empty was emptied on
       * purpose and stays that way. */
      if (!found && cfg.seed) {
        var s = null;
        try { s = cfg.seed(); } catch (e) { s = null; }
        if (s && typeof s === 'object') {
          var got = false;
          TEXT.forEach(function (k) { if (s[k] && typeof s[k] === 'string' && s[k].trim()) { state[k] = s[k]; got = true; } });
          if (got) {
            seeded = true;
            try { localStorage.setItem(KEY, JSON.stringify({ v: 2, s: state, m: 1 })); } catch (e) {}
          }
        }
      }
      dress();
    }

    load();
    paint();

    /* THE ONE CLOCK, printed where the driver reads the gate (rule 6). */
    function gateLine() {
      var g = [];
      if (state.gate) g.push(state.gate);
      if (state.nb) g.push('not before ' + state.nb);
      return g.length ? 'Getting in: ' + g.join(' · ') : '';
    }

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
        state = blank();
        load();
        paint();
        if (cfg.onChange) cfg.onChange();
      },
      /* The block as it reads in the sent document. Empty when he has said
       * nothing — a heading with nothing under it is noise in a message somebody
       * has to read at 6am. DRIVER LINES FIRST, dispatch lines after (rule 5). */
      text: function () {
        var lines = [];
        var gl = gateLine();
        if (gl) lines.push(gl);
        if (state.meet) lines.push('Gate\'s wrong or nobody\'s there — call: ' + state.meet);
        /* THE PAPERWORK RIDES WITH THE GATE, not at the bottom with the load-
         * builder's lines: it is the second half of getting in (the dispatcher's
         * "the code is step one of two"), and two of three lenses moved it here. */
        if (state.paper && state.paper.length) lines.push('Before the gate: ' + state.paper.join(' · '));
        var set = [];
        if (LOAD === 'small') {
          if (state.hand) set.push(state.hand);
          if (state.where) set.push(state.where);
          if (set.length) lines.push('Who takes it: ' + set.join(', '));
        } else {
          if (state.land) set.push(state.land);
          if (state.where) set.push(state.where);
          if (set.length) lines.push('Set it: ' + set.join(', '));
        }
        if (state.sign) lines.push('Signs for it if I\'m not there: ' + state.sign);
        if (LOAD !== 'small' && state.off) lines.push('Off the truck: ' + state.off);
        if (state.win) lines.push('When: ' + state.win);
        if (state.call) lines.push(state.call + '.');
        if (!lines.length) return '';
        return '\n\n' + (LOAD === 'small' ? 'HOW IT GETS IN AND WHO TAKES IT' : 'HOW IT GETS IN AND WHERE IT LANDS') + '\n'
          + lines.map(function (l) { return '- ' + l; }).join('\n')
          + '\n(That\'s what we need, not a booking — tell me if any of it doesn\'t work.)';
      },
      state: function () { return state; },
      load: function () { return LOAD; }
    };
  }

  window.Dropoff = { mount: mount };
})();
