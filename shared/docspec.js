/* FIELD TOOLKIT — SHAPE #4 ENGINE: THE INSTRUCTION BLOCK.
 *
 * av/AV_SOCIETY.md §THE GATE: "NEVER answer a NARRATIVE task with a multi-field
 * FORM — seven empty boxes on a phone lose to the notes app every time. If the
 * work is a PARAGRAPH, decline it or build the report-builder shape (an AI pass,
 * not more empty boxes)."
 *
 * That escape hatch had exactly ONE instance for two months: av/report-builder
 * .html, which turns the operator's own end-of-day AV daily into a role-tailored
 * AI setup. One instance is a page. This is the SECOND, and per §THE THREE SHAPES
 * the second instance is where the engine gets extracted — so it is extracted
 * here, and all six trades ship as configs in the same cycle rather than five
 * trades staying with nothing on the axis.
 *
 * WHAT THIS SHAPE IS. Not a form that produces a document. A form that produces
 * the INSTRUCTIONS that produce the document, forever. You pick the write-up you
 * are stuck with, answer four or five ticks, and get one block you paste into a
 * Gem / Project / Custom GPT ONCE. After that the job is: dump the mess, get the
 * document back clean. The page is used a handful of times per person; the block
 * it emits is used every day. That asymmetry is the whole design — it is why the
 * page can afford to ask a few real questions and why the block must be long and
 * exhaustive where the page is short.
 *
 * THE ISOMORPHISM (operator 2026-08-04: "the reports that stem from my own style,
 * to isomorphically map what would be useful for other documentation"). The
 * method here is EXTRACTION, not templating. av/report-builder.html carries one
 * working AV lead's actual daily-report prompt. Read it as a structure rather
 * than as content and it is eleven blocks, and every one of them generalises to
 * any document any trade has to write:
 *
 *     ROLE ................ who you are, what you convert, into what, for whom
 *     WHAT IT IS FOR ...... the one line that says what the document protects
 *     DEFAULTS ............ the facts it must stop re-asking for
 *     OPERATING PRINCIPLES  density · forwardable tone · never invent · plain text
 *     ATTRIBUTION ......... who the default actor is and when a name gets used
 *     INPUT HANDLING ...... fix the trade's dictation errors · group · strip venting
 *     CONTINUITY .......... delta only · carry blockers · escalate on the clock
 *     VALIDATION .......... the pre-flight facts, and the ONE halt condition
 *     THE OMITTED LINE .... the thing everyone leaves out, isolated so it cannot be
 *     REMINDERS ........... trigger-only protocol nudges, never nagging
 *     OUTPUT FORMAT ....... the spine, as the finished document's own headings
 *
 * Ten of those eleven are IDENTICAL for a plumber's back-charge notice and an AV
 * daily. Only the spine, the omitted line and the vocabulary change. So they are
 * the config, and everything else lives here once.
 *
 * THE HIGHEST-VALUE FIELD IN THE WHOLE LIBRARY IS `omit`. Anyone can list the
 * sections of an incident report. The reason a real hand's write-up survives a
 * dispute and a good writer's does not is one line that the good writer did not
 * know to include — the approval nobody wrote down, the pre-existing condition
 * nobody photographed, the date the clock actually started. Every document in
 * this library carries that line, and the engine gives it its own always-on
 * section in the emitted block so an AI cannot quietly drop it.
 *
 * WHAT THE ENGINE OWNS: the eleven blocks and their wording · the five family
 * spines for a document that is not in the library · search over the library ·
 * the picked-doc state · sticky DEFAULTS that survive across documents and
 * sessions (type your company once, ever) · local pick counts so a man's own
 * most-used documents float to the top · assembly, the live block, copy with the
 * non-secure-context fallback, and the platform setup steps.
 *
 * WHAT THE CALLER OWNS: every word of its own library. A trade's documents, in
 * that trade's names, with that trade's omitted lines, its dictation vocabulary
 * and its protocol reminders — window.TRADE_DOCS in <trade>/docs.js. It may also
 * override any field of any shared document by id, because "Daily Report" means
 * something slightly different to a super than to a service tech.
 *
 * NOT here, deliberately (§SAFETY): no code table, no threshold, no rating, no
 * pass/fail criterion and no sizing anywhere — not as a value, not as a hint, not
 * in a placeholder. The emitted block instructs the AI to record what the USER
 * measured and to write <MISSING> otherwise. It never supplies the number and it
 * never says whether a number is acceptable. Same rule for approvals: the block
 * tells it to record who approved and how, never to assume approval happened.
 *
 * Load AFTER the trade config, registry and doc library:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="docs.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *   <script src="../shared/docspec.js"></script>
 * with <link rel="stylesheet" href="../shared/note.css"> then docspec.css.
 */
(function () {
  "use strict";

  var TRADE = window.TOOLKIT_TRADE || {};
  var LIB = window.TRADE_DOCS || {};
  var KEY = "docspec:" + (TRADE.slug || "x");
  var USE = KEY + ":use";

  /* ── THE FIVE FAMILIES ──────────────────────────────────────────────────
   * Every write-up any of these trades has to produce is one of five, and each
   * family has its own spine and its own continuity rule. These are also the
   * fallback for a document that is not in the library: the man types what he
   * has to write, picks the family, and gets a real spine rather than a shrug.
   */
  var FAMILIES = {
    recurring: {
      name: "A report you send on a rhythm",
      hint: "daily, weekly, per-shift — it repeats, and each one should only carry what changed",
      delta: true,
      spine: [
        { h: "ACTION ITEMS", r: "grouped by who owns it; each one a task, decision or part needed, with a date" },
        { h: "WHAT CHANGED", r: "only what actually moved since the last one — never re-report finished work" },
        { h: "OPEN / BLOCKED", r: "what is stopped, who owns it, and the date it has been open since" },
        { h: "NEXT", r: "priorities in order for the next period" }
      ]
    },
    incident: {
      name: "A record of a thing that happened",
      hint: "damage, a near-miss, a failure, a conflict on site — written once, read years later",
      delta: false,
      spine: [
        { h: "WHAT HAPPENED", r: "plain sequence with times and dates; facts only, no characterisation of people" },
        { h: "CONDITION FOUND", r: "what the state actually was when you got there, including anything already wrong" },
        { h: "WHAT WE DID", r: "the actions taken, in order, and what state it was left in" },
        { h: "EVIDENCE", r: "photos, readings, tags, names of witnesses — what exists and where it is" },
        { h: "NOTIFIED", r: "who was told, when, and how (verbal / call / text / email)" },
        { h: "OPEN ITEMS", r: "what still has to happen and who owns it" }
      ]
    },
    verification: {
      name: "A record that something was tested or checked",
      hint: "startup, test, walk, inspection — its value is that a specific person can rely on it later",
      delta: false,
      spine: [
        { h: "SCOPE", r: "exactly what was tested and what was NOT — the boundary is the whole value" },
        { h: "CONDITIONS", r: "the state of the building/system while testing: what was energised, running, isolated, temporary" },
        { h: "WHAT WAS RECORDED", r: "the readings and results the user supplied, with units and where each was taken. Never a value the user did not state, never a judgement on whether a value is acceptable." },
        { h: "DEVIATIONS", r: "where installed reality differs from what was drawn or specified, with the reference" },
        { h: "NOT VERIFIED YET", r: "what could not be tested and why — this is the section that protects you" },
        { h: "OPEN ITEMS", r: "what has to happen before this can be relied on, with owner" }
      ]
    },
    notice: {
      name: "A letter that puts somebody on the clock",
      hint: "delay, back-charge, missing information, access — you need a decision or a thing, by a date",
      delta: false,
      spine: [
        { h: "WHAT WE NEED", r: "leads. The specific thing or decision, and the date it is needed by. One ask, not a list of grievances." },
        { h: "WHY, AND SINCE WHEN", r: "the facts and dates that got us here — no blame, no adjectives, no history lesson" },
        { h: "WHAT IT AFFECTS", r: "the concrete consequence: what work stops, what crew stands down, what date moves" },
        { h: "WHAT WE'VE DONE IN THE MEANTIME", r: "the work-arounds already run, so nobody can say we sat on it" },
        { h: "IF WE DON'T HAVE IT BY THEN", r: "the stated consequence — a date, a re-mobilisation, a change order. Factual, never a threat." }
      ]
    },
    minutes: {
      name: "A record of a conversation and what got decided",
      hint: "a call, a coordination meeting, a walk with the owner — the value is the decisions, not the discussion",
      delta: true,
      spine: [
        { h: "DECISIONS", r: "leads. What was decided, by whom, and effective when. Discussion that decided nothing does not appear." },
        { h: "WHO WAS THERE", r: "names and companies, and anyone who was expected and did not attend" },
        { h: "CHANGED FROM LAST TIME", r: "what reverses or supersedes something previously agreed — call it out, do not bury it" },
        { h: "ACTION ITEMS", r: "one owner and one date per item; no item without both" },
        { h: "NEEDS AN ANSWER BEFORE NEXT TIME", r: "the questions that will hold work if they stay open" }
      ]
    }
  };

  /* ── THE SHARED LIBRARY ─────────────────────────────────────────────────
   * The write-ups that four or more of the six trades all have to produce. They
   * belong here once; a trade that calls one of them something else, or wants a
   * different spine, overrides it by id in its own docs.js rather than forking.
   *
   * Every `omit` line below is the specific thing that costs money on THAT
   * document — not "add more detail".
   */
  var SHARED_DOCS = [
    {
      id: "daily-report",
      name: "Daily Field Report",
      aka: ["daily", "dfr", "end of day", "eod", "field report", "daily update"],
      family: "recurring",
      from: "the lead on the job",
      to: "my PM and the office",
      why: "The one your PM forwards. Written badly it becomes an argument later; written right it is the record of every day you were there.",
      omit: "The field audible — the thing you changed on the fly to keep moving. Parts robbed from another room, an approved hour of overtime, a substitution, an owner ask that was never on the drawings. Nobody writes it down the day it happens, and three months later there is no paper for the change order.",
      halt: "Only if this is the first report in the thread and there is no job number or site at all.",
      facts: ["date", "job number / site", "who was on it and how many hours", "what finished", "what is blocked"],
      secondary: ["a weekly rollup from the dailies in this thread", "a short client-facing version with the internal detail stripped"]
    },
    {
      id: "incident-report",
      name: "Incident / Near-Miss Report",
      aka: ["incident", "near miss", "accident", "injury", "damage", "safety report"],
      family: "incident",
      from: "the person who was there",
      to: "safety and my PM",
      why: "Written once, read by people who were not there, sometimes years later. The only version that survives is the one written the same day.",
      omit: "The condition that was already wrong before you got there, and the time you first reported it. Without that line every incident reads as if it started with you.",
      halt: "Never halt. If someone was hurt, write what is known and mark everything else <MISSING> — a late report is worse than an incomplete one.",
      facts: ["date and time", "exact location", "who was involved and who witnessed it", "what was damaged or who was hurt", "who was notified and when"],
      secondary: ["a notification email to the GC or owner", "a follow-up once the corrective action is done"]
    },
    {
      id: "damage-found",
      name: "Damage / Pre-Existing Condition Note",
      aka: ["damage", "pre-existing", "found damage", "prior damage", "not us"],
      family: "incident",
      from: "the person who found it",
      to: "the GC super and my PM",
      why: "You walked into something already broken. This is the note that means it is not yours when somebody goes looking for who to charge.",
      omit: "The timestamp and where the photos live. A description with no photo reference and no date is worth nothing in a back-charge meeting.",
      halt: "Never halt.",
      facts: ["date and time found", "exact location", "what the condition is", "photos taken", "who you told and how"],
      secondary: ["a short email to the super with the photos attached"]
    },
    {
      id: "delay-notice",
      name: "Delay / We're Held Up Notice",
      aka: ["delay", "held up", "stopped", "waiting on", "impact notice", "notice"],
      family: "notice",
      from: "the lead on the job",
      to: "the GC and my PM",
      why: "The clock only starts when somebody is told in writing. This is that.",
      omit: "The date you FIRST asked. Everyone writes the delay; almost nobody writes 'requested 07/22, no response as of 07/29', which is the only part that establishes how long it has actually been sitting.",
      halt: "Only if there is no stated thing you are waiting on.",
      facts: ["what you are waiting on", "who owes it", "the date you first asked", "what work is stopped", "the date you need it by"],
      secondary: ["a shorter version for a text message", "a follow-up that carries the original dates forward"]
    },
    {
      id: "change-request",
      name: "Extra Work / Change Write-Up",
      aka: ["change order", "co", "extra", "out of scope", "t and m narrative", "scope change"],
      family: "notice",
      from: "the lead on the job",
      to: "the GC and my PM",
      why: "The narrative that goes with the ticket. Prices are the office's job — this is the part that says why it is extra, which is the part that gets argued.",
      omit: "Who authorised it, when, and by what channel — verbal, call, text, email. That one line is the difference between a change order and a donation.",
      halt: "Only if the work being described is not stated at all.",
      facts: ["what was asked for and by whom", "when it was authorised and how", "what the contract scope actually said", "what it displaced"],
      secondary: ["a one-paragraph version to paste into the GC's change form"],
      note: "This is the narrative only — no prices, no rates, no hours priced out. The office owns the number."
    },
    {
      id: "service-writeup",
      name: "Service Call Write-Up",
      aka: ["service", "call", "repair", "service report", "work order narrative", "trouble call"],
      family: "incident",
      from: "the tech on the call",
      to: "dispatch and the customer",
      why: "The customer reads this and decides whether to pay for what comes next. It has to be honest, complete, and free of anything they cannot act on.",
      omit: "What you did NOT do and why — the part you could not get to, the thing you found that is outside this call. Leave it out and you own it by silence.",
      halt: "Only if there is no statement of what the complaint was.",
      facts: ["the complaint as reported", "what you found", "what you did", "what it is doing now", "what still needs doing"],
      secondary: ["a customer-facing version with the internal notes stripped", "a quote request to the office for the recommended follow-up"]
    },
    {
      id: "site-walk",
      name: "Site Walk / Survey Write-Up",
      aka: ["walk", "site visit", "survey", "site survey", "walkthrough", "pre-install walk"],
      family: "verification",
      from: "the person who walked it",
      to: "the office and estimating",
      why: "Everything you noticed on site, in a form somebody who was not there can price, schedule or order from.",
      omit: "Access and conditions — where you park, what hours you can work, what has to be escorted, what is not built yet. It never makes the notes and it is what blows the schedule.",
      halt: "Only if no site is identified.",
      facts: ["date and site", "who walked it with you", "what is existing", "what is not ready", "access and working hours"],
      secondary: ["a list of questions for the GC", "a short summary for estimating"]
    },
    {
      id: "handover",
      name: "Turnover / Handover Summary",
      aka: ["handover", "turnover", "closeout", "hand off", "handoff", "close out", "punch complete"],
      family: "verification",
      from: "the lead on the job",
      to: "the owner and their people",
      why: "The last document anyone reads, and the first one they blame. Written well it ends the job; written badly it brings you back for free.",
      omit: "The open items you are handing over KNOWN — with owner and date. A handover that reads as if everything is finished converts every leftover into warranty work.",
      halt: "Only if the system or area being handed over is not identified.",
      facts: ["what is being handed over", "what was tested and by whom", "what is still open", "what was given to them (keys, codes, manuals, spares)", "who to call"],
      secondary: ["an owner-facing version", "a punch list of what is left"]
    },
    {
      id: "look-ahead",
      name: "Look-Ahead / What We Need",
      aka: ["look ahead", "lookahead", "two week", "three week", "next week", "plan"],
      family: "recurring",
      from: "the lead on the job",
      to: "my PM and the office",
      why: "The one that stops the crew standing around next week. It is a request disguised as a schedule.",
      omit: "What has to be TRUE before each item can start — the other trade's work, the delivery, the inspection. A look-ahead with no preconditions is a wish list.",
      halt: "Only if no period is stated.",
      facts: ["the period", "crew count expected", "what is planned in order", "what has to arrive", "what other trades have to finish first"],
      secondary: ["a manpower request for the office", "a coordination note for the GC"]
    },
    {
      id: "toolbox-talk",
      name: "Toolbox Talk / Safety Meeting Note",
      aka: ["toolbox", "tool box talk", "safety meeting", "tailgate", "jha", "pre task"],
      family: "minutes",
      from: "the lead on the job",
      to: "safety and the office",
      why: "Five minutes of talking that has to exist on paper. Nobody wants to write it; everybody wants it to exist when something happens.",
      omit: "What was raised BY the crew and what you did about it. A talk that records only what you said reads as a lecture and proves nothing about the site.",
      halt: "Never halt.",
      facts: ["date", "topic", "who attended", "site conditions that day", "anything raised and what was done"],
      secondary: ["a month's talks rolled into one summary"]
    },
    {
      id: "meeting-minutes",
      name: "Coordination Meeting Notes",
      aka: ["minutes", "meeting", "coordination", "oac", "notes", "call notes"],
      family: "minutes",
      from: "the person taking notes",
      to: "everybody who was on it",
      why: "The version that goes out first becomes the truth. Send it the same day and it is yours.",
      omit: "Who was NOT there but is bound by it, and the date the notes go final if nobody objects. Without those two lines the notes are just your opinion of the meeting.",
      halt: "Only if no meeting date is given.",
      facts: ["date and who attended", "what was decided", "what was left open", "who owes what by when"],
      secondary: ["an action-items-only version for the crew"]
    }
  ];

  /* ── THE UNIVERSAL LAWS ─────────────────────────────────────────────────
   * Ten of the eleven blocks. These are the same for every document and every
   * trade, and they are the part that makes an emitted block production-grade
   * rather than "write me a report about my day".
   */
  var PRINCIPLES = [
    "Density over volume. Every line carries operational information. No filler, no apologies, no restating the instructions back to me.",
    "Forwardable tone. Write every line as if the person above me and the customer will both read it. When something is late or missing, state the facts, the dates and the impact, then make one specific ask. Never assign blame and never characterise people. (\"Requested 07/22, no response as of 07/29, holds the east rooms\" — not \"they are ignoring us.\")",
    "Never invent data. If a number, time, quantity, name, model, reading or approval was not given to you, do not fabricate it and do not estimate it. Write <MISSING> and add retrieving it to the open items.",
    "Never judge a value. If I give you a reading, a measurement or a result, record it exactly as given with its units. Do not say whether it is in range, acceptable, passing or to code — that is not yours and it is not mine to guess either.",
    "Plain text only. No emojis, no markdown styling, no bold, no citation brackets, no reference markers. It has to paste clean into email, a text message and a chat app."
  ];

  var ATTRIB = [
    "Default actor is the crew: \"Team completed X\" / \"The crew pulled X.\" Not \"I\".",
    "Name the lead only for: verification and sign-off, coordination with other companies, customer-facing decisions, and calls made in the field.",
    "Use first person only where I explicitly say I personally did it."
  ];

  var INPUT_RULES = [
    "Strip venting and emotion entirely. Translate frustrated or rambling input into flat, professional statements. Nothing emotional reaches the document.",
    "Translate vague asks into explicit action items with an owner and a date.",
    "Deduplicate. The same event often arrives twice — once dictated, once as a pasted text. Consolidate to one line. If two inputs conflict, use the most recent and flag the conflict as an open item.",
    "Fix my spelling, my punctuation and my dictation errors silently. Never comment on the correction and never show me a corrected-text section."
  ];

  var DELTA = [
    "Each one covers the DELTA: what changed and what blocks the next period. Compare against the immediately preceding document in this conversation and drop anything already reported finished. Never repeat prior completions unless I ask for a cumulative rollup.",
    "Carry every unresolved open item forward automatically, with the date it was first raised, until I say it is resolved.",
    "If an item owned by somebody else shows no movement for 48 hours or more, promote it to the top and add an action item asking for intervention. Measure the 48 hours by the dates on the documents in this thread, not by the clock.",
    "Carry the header forward from the preceding document. Never re-ask for anything already established in this thread.",
    "First one in a chat: treat the input as the baseline. If I paste a previous one, adopt its open items, dates and header as the prior state."
  ];

  var PLATFORMS = {
    gemini: { name: "Gemini Gem", where: "the Gem's “Instructions” box (Gem manager → New Gem)" },
    claude: { name: "Claude Project", where: "the Project's “Project instructions” (make a Project → Add instructions)" },
    gpt: { name: "Custom GPT", where: "the Custom GPT's “Instructions” (Explore GPTs → Create), or a Project's instructions" },
    other: { name: "your AI", where: "its system or custom-instructions field" }
  };

  /* Rules the user turns on and off. Locked ones cannot be turned off — they are
     the §SAFETY rail, not a preference. */
  var TOGGLES = [
    { id: "invent", label: "Never invent anything — write <MISSING> instead", sub: "and list it to chase", on: true, locked: true },
    { id: "judge", label: "Never call a reading good, bad, passing or to code", sub: "records what I measured, nothing more", on: true, locked: true },
    { id: "plain", label: "Plain text — no emojis, no markdown, no formatting", sub: "so it pastes clean into a text message", on: true },
    { id: "clientsafe", label: "Customer-safe wording", sub: "no internal blame, no other company named as at fault", on: true },
    { id: "co", label: "Flag anything that smells like extra work", sub: "who asked, when, how it was authorised", on: true },
    { id: "short", label: "Keep it short — a screen, not a page", sub: "for the ones that get read on a phone", on: false },
    { id: "email", label: "Also give me a one-line subject and a two-line email body", sub: "for sending it on", on: false }
  ];

  /* ── state ─────────────────────────────────────────────────────────────── */
  var S = {
    doc: null,        // picked doc id, or "__custom"
    customName: "",
    customFamily: "recurring",
    platform: "gemini",
    role: "",
    to: "",
    me: "", second: "", office: "", company: "",
    off: {},          // section headings the user turned off
    tog: {},          // toggle id -> bool
    extra: "",
    q: ""             // search text
  };

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var o = JSON.parse(raw);
        Object.keys(o || {}).forEach(function (k) { if (k in S) S[k] = o[k]; });
      }
    } catch (e) {}
    S.q = "";
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }

  function uses() { try { return JSON.parse(localStorage.getItem(USE) || "{}") || {}; } catch (e) { return {}; } }
  function bump(id) {
    try { var u = uses(); u[id] = (u[id] || 0) + 1; localStorage.setItem(USE, JSON.stringify(u)); } catch (e) {}
  }

  /* ── library assembly: shared + trade, with per-id overrides ───────────── */
  function library() {
    var ov = LIB.overrides || {};
    var out = SHARED_DOCS.map(function (d) {
      var o = ov[d.id];
      if (!o) return d;
      var m = {}; Object.keys(d).forEach(function (k) { m[k] = d[k]; });
      Object.keys(o).forEach(function (k) { m[k] = o[k]; });
      return m;
    });
    var drop = LIB.drop || [];
    out = out.filter(function (d) { return drop.indexOf(d.id) === -1; });
    return out.concat(LIB.docs || []);
  }

  function spineOf(doc) {
    if (doc.sections && doc.sections.length) return doc.sections;
    var f = FAMILIES[doc.family] || FAMILIES.recurring;
    return f.spine;
  }

  /* THE TWO ALWAYS-ON SECTIONS. The omitted line gets one because the whole
     library is built around it; open items gets one because a document that ends
     without "who owes what" is a story, not a request. */
  var LOCKED = [
    { h: "THE ONE NOBODY WRITES DOWN", r: "the line everyone leaves out, above — it gets its own line every time" },
    { h: "OPEN ITEMS", r: "what still has to happen, who owns it, and by when" }
  ];

  /* ONE assembly, used by the tick list AND the composer. They used to build the
     section list separately, which shipped OPEN ITEMS twice in the finished
     document for every incident- and verification-family write-up: the family
     spine already ends with it and the engine appended its own. A heading
     printed twice reads as two different lists to whoever receives it — the same
     class as the two-lists-under-one-heading scar. Dedupe on the normalised
     heading, first position wins, because the ORDER is the argument. */
  function sectionsOf(doc) {
    var out = spineOf(doc).filter(function (s) { return !isLocked(s.h); });
    /* LOCKED always sits LAST and always in this order. Deduping the other way
       round — first-wins over the concatenated list — kept the family spine's own
       trailing OPEN ITEMS in place and pushed the omitted line BELOW it, which
       buries the one section the whole library exists to protect. */
    return out.concat(LOCKED);
  }
  function isLocked(hdg) {
    var k = (hdg || "").toUpperCase().replace(/[^A-Z]/g, "");
    for (var i = 0; i < LOCKED.length; i++) {
      if (LOCKED[i].h.toUpperCase().replace(/[^A-Z]/g, "") === k) return true;
    }
    return false;
  }

  function byId(id) {
    var all = library();
    for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
    return null;
  }

  function current() {
    if (S.doc === "__custom") {
      var f = FAMILIES[S.customFamily] || FAMILIES.recurring;
      return {
        id: "__custom",
        name: S.customName || "Write-Up",
        family: S.customFamily,
        from: "", to: "",
        why: f.hint,
        omit: "The one fact that proves WHEN this started and WHO agreed to it. On almost every document in this trade, that is the line that is missing when it is needed.",
        halt: "Only if the input does not say what the document is about at all.",
        facts: ["date", "job or site", "who was involved"],
        sections: f.spine,
        secondary: []
      };
    }
    return S.doc ? byId(S.doc) : null;
  }

  /* ── THE COMPOSER — the eleven blocks ──────────────────────────────────── */
  function nz(v, fb) { v = (v || "").trim(); return v || fb; }

  function compose() {
    var d = current();
    if (!d) return "";
    /* THE TRADE WORD is declared, never derived. It used to be TRADE.name with
       " Field Toolkit" sliced off, which produced "a AV outfit" (wrong article)
       and left GC reading "a GC & Site Super Toolkit outfit" — the trade whose
       name does not end in the string being stripped. A config value cannot be
       recovered by cutting a different config value; §THE THREE SHAPES says the
       caller owns its own words, so it declares this one. */
    var tradeName = LIB.trade || "field";
    var fam = FAMILIES[d.family] || FAMILIES.recurring;
    var me = nz(S.me, "<my name>");
    var co = nz(S.company, "<my company>");
    var to = nz(S.to, d.to || "the office");
    /* TWO DIFFERENT THINGS, and conflating them printed "I am Whoever was on the
       call at <company>" into a production instruction block. `from` is the
       library's DESCRIPTION of who writes this document, shown on the library
       row; `pickedRole` is what THIS user tapped. The description can carry a
       clause and still read fine on a row; only the tapped value is short enough
       to go in a header line, so only it does. */
    var pickedRole = nz(S.role, "");
    var role = pickedRole || d.from || "the person who was there";
    var T = function (id) { var t = S.tog[id]; return t === undefined ? defOn(id) : !!t; };
    var L = [];

    L.push("ROLE");
    L.push("");
    L.push("You write the " + d.name + " for my company. I am " + role + " at " + co +
      "; we do " + tradeName + " work. You convert my messy field input — voice-to-text dictation, " +
      "half-finished notes, pasted texts, end-of-day brain dumps — into one finished " + d.name +
      " I can send to " + to +
      " without editing it. Output the document and nothing else: no preamble, no commentary, no explaining what you did.");
    L.push("");
    L.push("WHAT THIS DOCUMENT IS FOR");
    L.push("");
    L.push(d.why);
    if (d.note) L.push(d.note);
    L.push("");

    L.push("DEFAULTS");
    L.push("");
    L.push("- Me: " + me + (pickedRole ? " (" + pickedRole + ")" : ""));
    if (nz(S.second, "")) L.push("- Usually with me: " + S.second.trim());
    L.push("- Office / PM contact: " + nz(S.office, "<name>"));
    L.push("- Company: " + co);
    L.push("- Trade: " + tradeName);
    L.push("- Goes to: " + to);
    L.push("Use these whenever the day's input does not say otherwise. Never ask me for something already established in this conversation.");
    L.push("");

    L.push("OPERATING PRINCIPLES");
    L.push("");
    var pr = PRINCIPLES.slice();
    if (!T("plain")) pr.splice(4, 1);
    if (T("clientsafe")) pr.push("Customer-safe. Never name another company as being at fault and never put internal frustration on the page. State what happened and what is needed.");
    if (T("short")) pr.push("Keep it to one screen. If it does not change a decision, it does not go in.");
    pr.forEach(function (p, i) { L.push((i + 1) + ". " + p); });
    L.push("");

    L.push("ATTRIBUTION");
    L.push("");
    ATTRIB.forEach(function (a) { L.push("- " + a); });
    L.push("");

    L.push("INPUT HANDLING");
    L.push("");
    var n = 1;
    var vocab = (LIB.vocab || []);
    if (vocab.length) {
      L.push(n++ + ". Silently correct dictation and jargon errors to the proper " + tradeName +
        " terms. These are the ones my phone gets wrong: " + vocab.join("; ") +
        ". Correct anything else in the same spirit. Never mention the correction.");
    }
    L.push(n++ + ". Group scattered input into the sections of the output format below. If something does not fit a section, put it in the open items rather than dropping it.");
    INPUT_RULES.forEach(function (r) { L.push(n++ + ". " + r); });
    L.push("");

    if (fam.delta) {
      L.push("CONTINUITY");
      L.push("");
      DELTA.forEach(function (r, i) { L.push((i + 1) + ". " + r); });
      L.push("");
    } else {
      L.push("CONTINUITY");
      L.push("");
      L.push("This document stands alone — it is written once and read later by people who were not there. Do not write it as an update and do not assume the reader knows the job. Spell out the site, the date and the system every time.");
      L.push("If I paste an earlier version, treat it as prior state: keep its facts and dates, and mark clearly what has changed since.");
      L.push("");
    }

    L.push("VALIDATION");
    L.push("");
    L.push("Before you write, check the input for: " + (d.facts || []).join(", ") + ".");
    L.push("- No date given: use today's date. If you cannot know today's date, write <MISSING: date> and flag it.");
    L.push("- " + (d.halt || "Only halt if the input does not say what the document is about.") + " That is the ONLY reason to stop and ask me a question.");
    L.push("- Anything else missing: write the document anyway, put <MISSING> where the fact belongs, and list chasing it in the open items. A document with visible gaps is useful; a document that waits for me is not.");
    L.push("");

    L.push("THE LINE EVERYONE LEAVES OUT — NEVER DROP IT");
    L.push("");
    L.push(d.omit);
    L.push("Give this its own line in the finished document every single time. If my input does not cover it, write <MISSING> against it and put chasing it at the TOP of the open items — do not quietly leave it out because I did not mention it.");
    L.push("");

    if (T("co")) {
      L.push("EXTRA WORK — ISOLATE IT");
      L.push("");
      L.push("Anything in my input that is outside what we were originally there to do gets pulled into its own section, because it is billing evidence: work somebody else directed, materials used off another job, hours past the plan, a request that was not on the drawings, a substitution made to keep moving.");
      L.push("For each one: what changed, who asked for it, when, and how it was authorised (verbal / call / text / email). If the authorisation is not in my input, write <MISSING> and add it to the open items. Never assume approval happened.");
      L.push("Do not price anything. No rates, no totals, no hours priced out — the office owns the number, I own what happened.");
      L.push("");
    }

    var rem = (LIB.reminders || []);
    if (rem.length) {
      L.push("PROTOCOL REMINDERS (trigger only when relevant — never nag)");
      L.push("");
      rem.forEach(function (r) { L.push("- " + r); });
      L.push("");
    }

    L.push("OUTPUT FORMAT");
    L.push("");
    L.push("Output the document in a single plain-text code block, using exactly this structure. Leave out any section that is empty, except the last two, which always appear — write \"None\" if there is nothing. Keep both header lines even if a field is <MISSING>.");
    L.push("");
    L.push("[" + d.name.toUpperCase() + " | <JOB / SITE> | <MM/DD/YY>]");
    L.push("[" + (pickedRole ? pickedRole.toUpperCase() + ": " : "") + me.toUpperCase() +
      " | " + co.toUpperCase() + " | TO: " + to.toUpperCase() + "]");
    L.push("");
    sectionsOf(d).forEach(function (s) {
      if (!isLocked(s.h) && S.off[s.h]) return;
      L.push("=========================================");
      L.push(s.h);
      L.push("=========================================");
      if (s.h === LOCKED[0].h) {
        L.push("- <" + shortOmit(d.omit) + ". Write <MISSING> against it if I did not give it to you.>");
      } else if (s.h === LOCKED[1].h) {
        L.push("- <" + s.r + ". Write \"None\" if there is nothing.>");
      } else {
        L.push("- <" + s.r + ">");
      }
      L.push("");
    });

    L.push("SECONDARY REQUESTS");
    L.push("");
    var sec = (d.secondary || []).slice();
    if (T("email")) sec.push("a one-line subject and a two-line email body to send it with");
    sec.push("a rich-text or table version, outside the code block, if I ask for one");
    L.push("If I ask for it, you can also produce: " + sec.join("; ") + ". Every rule above still applies.");
    L.push("Never produce any of these unless I ask.");

    if (nz(S.extra, "")) {
      L.push("");
      L.push("EXTRA INSTRUCTIONS FROM ME — OBEY THESE TOO");
      L.push("");
      L.push(S.extra.trim());
    }

    return L.join("\n");
  }

  /* The omit line is a paragraph on the page and has to become a one-line prompt
     inside the output format. Cut at the first sentence or em-dash and trim —
     without the trim it printed "…and why . <MISSING>". */
  function shortOmit(t) {
    return (t || "").split(/(?:\.\s|\s—\s)/)[0].replace(/[\s.]+$/, "");
  }

  function defOn(id) {
    for (var i = 0; i < TOGGLES.length; i++) if (TOGGLES[i].id === id) return TOGGLES[i].on;
    return false;
  }

  function setupSteps() {
    var p = PLATFORMS[S.platform] || PLATFORMS.other;
    var d = current();
    var nm = d ? d.name : "document";
    var fam = d ? (FAMILIES[d.family] || FAMILIES.recurring) : FAMILIES.recurring;
    var steps = [
      "Open <b>" + p.name + "</b> and paste the block below into " + p.where + ". Name it “" + nm + "”.",
      fam.delta
        ? "Run <b>one chat per job.</b> Starting a new chat mid-job? Paste your last one in first so it keeps the running items."
        : "Start a <b>new chat for each one.</b> These stand alone — they do not need the history.",
      "<b>Then just dump.</b> Voice-to-text it in the truck, paste your texts, whatever you have. You get back one clean " + nm + ".",
      "Read it before you send it. Chase anything marked <code>&lt;MISSING&gt;</code> — that is the point of the marker."
    ];
    return steps;
  }

  /* ── UI ────────────────────────────────────────────────────────────────── */
  var el = {};
  function h(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt !== undefined && txt !== null) n.textContent = txt;
    return n;
  }

  function matches(d, q) {
    if (!q) return true;
    var hay = (d.name + " " + (d.aka || []).join(" ") + " " + (d.why || "")).toLowerCase();
    return q.toLowerCase().split(/\s+/).every(function (w) { return hay.indexOf(w) !== -1; });
  }

  function renderLibrary() {
    var box = el.lib;
    box.innerHTML = "";
    var all = library();
    var u = uses();
    var q = S.q.trim();
    var hits = all.filter(function (d) { return matches(d, q); });

    if (!q) {
      var mine = hits.filter(function (d) { return u[d.id]; })
        .sort(function (a, b) { return (u[b.id] || 0) - (u[a.id] || 0); }).slice(0, 3);
      if (mine.length) {
        box.appendChild(grp("Yours — most used"));
        mine.forEach(function (d) { box.appendChild(row(d)); });
        box.appendChild(grp("Everything else"));
        hits = hits.filter(function (d) { return mine.indexOf(d) === -1; });
      }
    }
    if (!hits.length) {
      var n = h("li", "none", "Nothing matches “" + q + "”. Use “not in the list” below — it still builds you a real one.");
      box.appendChild(n);
      return;
    }
    hits.forEach(function (d) { box.appendChild(row(d)); });

    function grp(t) { var li = h("li", "grp", t); return li; }
    function row(d) {
      var li = h("li", S.doc === d.id ? "on" : "");
      var b = h("button", null);
      b.type = "button";
      b.appendChild(h("span", "nm", d.name));
      b.appendChild(h("span", "wy", d.why));
      b.appendChild(h("span", "rt", (d.from ? d.from + " → " : "") + (d.to || "")));
      b.addEventListener("click", function () { pick(d.id); });
      li.appendChild(b);
      return li;
    }
  }

  function pick(id) {
    S.doc = id;
    S.off = {};
    var d = current();
    if (d && d.to && !S.to) S.to = d.to;
    if (id !== "__custom") bump(id);
    save();
    renderAll();
    if (el.tuneCard) el.tuneCard.scrollIntoView({ block: "start" });
  }

  function renderPicked() {
    var box = el.picked;
    box.innerHTML = "";
    var d = current();
    if (!d) { box.style.display = "none"; return; }
    box.style.display = "";
    var p = h("div", "picked");
    p.appendChild(h("h3", null, d.name));
    p.appendChild(h("span", "rt", (FAMILIES[d.family] || FAMILIES.recurring).name));
    if (d.why) p.appendChild(h("p", "wy", d.why));
    var chg = h("button", "chg", "Pick a different one");
    chg.type = "button";
    chg.addEventListener("click", function () {
      S.doc = null; save(); renderAll();
      if (el.libCard) el.libCard.scrollIntoView({ block: "start" });
    });
    p.appendChild(chg);
    box.appendChild(p);

    var o = h("div", "omit");
    o.appendChild(h("b", null, "The line everyone leaves out"));
    o.appendChild(h("p", null, d.omit));
    box.appendChild(o);
  }

  function field(label, key, ph, wide) {
    var f = h("div", "f" + (wide ? " span2" : ""));
    var l = h("label", null, label);
    f.appendChild(l);
    var i = document.createElement("input");
    i.type = "text"; i.value = S[key] || ""; i.placeholder = ph || ""; i.autocomplete = "off";
    i.addEventListener("input", function () { S[key] = i.value; save(); renderOut(); });
    f.appendChild(i);
    return f;
  }

  function seg(opts, get, set) {
    var s = h("div", "seg");
    opts.forEach(function (o) {
      var b = h("button", get() === o[0] ? "on" : "", o[1]);
      b.type = "button";
      b.addEventListener("click", function () { set(o[0]); save(); renderAll(); });
      s.appendChild(b);
    });
    return s;
  }

  function renderTune() {
    var box = el.tune;
    box.innerHTML = "";
    var d = current();
    if (!d) { el.tuneCard.style.display = "none"; el.outCard.style.display = "none"; return; }
    el.tuneCard.style.display = ""; el.outCard.style.display = "";

    /* who */
    box.appendChild(sub("Who is writing it, and who reads it"));
    var g1 = h("div", "hgrid");
    var roles = (TRADE.roles || []).map(function (r) { return [r[1], r[1]]; });
    if (roles.length) {
      var fr = h("div", "f span2");
      fr.appendChild(h("label", null, "You are"));
      fr.appendChild(seg(roles.slice(0, 4), function () { return S.role; }, function (v) { S.role = (S.role === v ? "" : v); }));
      g1.appendChild(fr);
    }
    g1.appendChild(field("Goes to", "to", d.to || "PM / office", true));
    box.appendChild(g1);

    /* defaults */
    box.appendChild(sub("Type these once — they stick for every document"));
    var g2 = h("div", "hgrid");
    g2.appendChild(field("Your name", "me", "name"));
    g2.appendChild(field("Usually with you", "second", "name (optional)"));
    g2.appendChild(field("Office / PM", "office", "name"));
    g2.appendChild(field("Company", "company", "company"));
    box.appendChild(g2);

    /* spine */
    box.appendChild(sub("What the finished document says, in order"));
    var ul = h("ul", "spine");
    sectionsOf(d).forEach(function (s) {
      var lock = isLocked(s.h);
      var li = h("li", lock ? "locked" : "");
      var lb = h("label");
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = lock ? true : !S.off[s.h];
      if (lock) cb.disabled = true;
      else cb.addEventListener("change", function () {
        if (cb.checked) delete S.off[s.h]; else S.off[s.h] = 1;
        save(); renderOut();
      });
      lb.appendChild(cb);
      var tx = h("div", "tx");
      tx.appendChild(h("span", "h", s.h));
      tx.appendChild(h("span", "r", s.r));
      lb.appendChild(tx);
      li.appendChild(lb);
      ul.appendChild(li);
    });
    box.appendChild(ul);

    /* toggles */
    box.appendChild(sub("House rules it follows"));
    var tl = h("ul", "ticks");
    TOGGLES.forEach(function (t) {
      var li = h("li");
      var lb = h("label");
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = (S.tog[t.id] === undefined) ? t.on : !!S.tog[t.id];
      if (t.locked) { cb.disabled = true; cb.checked = true; }
      cb.addEventListener("change", function () { S.tog[t.id] = cb.checked; save(); renderOut(); });
      lb.appendChild(cb);
      lb.appendChild(h("span", "nm", t.label));
      if (t.sub) lb.appendChild(h("span", "sb", t.sub));
      li.appendChild(lb);
      tl.appendChild(li);
    });
    box.appendChild(tl);

    /* platform + extra */
    box.appendChild(sub("Where you'll paste it"));
    box.appendChild(seg([["gemini", "Gemini"], ["claude", "Claude"], ["gpt", "ChatGPT"], ["other", "Other"]],
      function () { return S.platform; }, function (v) { S.platform = v; }));

    var fx = h("div", "f span2");
    fx.style.marginTop = "12px";
    fx.appendChild(h("label", null, "Anything else it should always do (optional)"));
    var ta = document.createElement("textarea");
    ta.value = S.extra || "";
    ta.placeholder = "e.g. always CC the super · we go by area not room number · put the PO number on every one · never mention the customer by name";
    ta.addEventListener("input", function () { S.extra = ta.value; save(); renderOut(); });
    fx.appendChild(ta);
    box.appendChild(fx);

    function sub(t) { return h("p", "subhead", t); }
  }

  function renderOut() {
    if (!current()) return;
    var txt = compose();
    el.out.textContent = txt;
    el.steps.innerHTML = setupSteps().map(function (s) { return "<li>" + s + "</li>"; }).join("");
    var words = txt ? txt.split(/\s+/).length : 0;
    el.count.textContent = words ? (words + " words — paste it in once, use it daily") : "";
  }

  function renderCustom() {
    var box = el.custom;
    box.innerHTML = "";
    var open = S.doc === "__custom";
    var b = h("button", "addrow", open ? "← Back to the list" : "Not in the list? Build one anyway");
    b.type = "button";
    b.addEventListener("click", function () {
      if (open) { S.doc = null; } else { S.doc = "__custom"; }
      save(); renderAll();
    });
    box.appendChild(b);
    if (!open) return;
    var g = h("div", "hgrid");
    g.style.marginTop = "10px";
    var f = h("div", "f span2");
    f.appendChild(h("label", null, "What is it called where you work?"));
    var i = document.createElement("input");
    i.type = "text"; i.value = S.customName; i.placeholder = "e.g. Pre-pour sign-off note";
    i.addEventListener("input", function () { S.customName = i.value; save(); renderPicked(); renderOut(); });
    f.appendChild(i);
    g.appendChild(f);
    var f2 = h("div", "f span2");
    f2.appendChild(h("label", null, "Which of these is it?"));
    var ul = h("ul", "ticks");
    Object.keys(FAMILIES).forEach(function (k) {
      var li = h("li");
      var lb = h("label");
      var r = document.createElement("input");
      r.type = "radio"; r.name = "fam"; r.checked = S.customFamily === k;
      r.addEventListener("change", function () { S.customFamily = k; S.off = {}; save(); renderAll(); });
      lb.appendChild(r);
      var tx = h("div", "tx");
      tx.appendChild(h("span", "nm", FAMILIES[k].name));
      lb.appendChild(tx);
      lb.appendChild(h("span", "sb", ""));
      li.appendChild(lb);
      ul.appendChild(li);
    });
    f2.appendChild(ul);
    g.appendChild(f2);
    box.appendChild(g);
  }

  function renderAll() {
    renderLibrary();
    renderCustom();
    renderPicked();
    renderTune();
    if (current()) renderOut();
    el.libCard.style.display = (S.doc && S.doc !== "__custom") ? "none" : "";
  }

  /* ── copy, with the non-secure-context fallback (§SCARS) ────────────────── */
  function copyText(text, btn, label) {
    var was = btn.textContent;
    function flash(msg) { btn.textContent = msg; setTimeout(function () { btn.textContent = was; }, 1800); }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;left:8px;right:8px;bottom:76px;width:calc(100% - 16px);height:40vh;z-index:99";
      document.body.appendChild(ta);
      ta.focus(); ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      if (ok) { ta.remove(); flash(label || "Copied"); }
      else { flash("Select it and copy"); ta.addEventListener("blur", function () { ta.remove(); }); }
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { flash(label || "Copied"); }, fallback);
    } else { fallback(); }
  }

  function wholeSetup() {
    var p = PLATFORMS[S.platform] || PLATFORMS.other;
    var d = current();
    return (d ? d.name.toUpperCase() : "WRITE-UP") + " — SETUP FOR " + p.name.toUpperCase() + "\n\n" +
      setupSteps().map(function (s, i) { return (i + 1) + ". " + s.replace(/<[^>]+>/g, ""); }).join("\n") +
      "\n\n--- PASTE EVERYTHING BELOW THIS LINE INTO " + p.name.toUpperCase() + " ---\n\n" + compose();
  }

  /* ── mount ─────────────────────────────────────────────────────────────── */
  function mount() {
    var app = document.getElementById("app");
    if (!app) return;
    load();

    el.libCard = h("div", "card");
    el.libCard.appendChild(h("h2", "blk", "1 · What are you stuck writing?"));
    var srch = h("div", "srch");
    var si = document.createElement("input");
    si.type = "search"; si.placeholder = "search — daily, delay, incident, handover…";
    si.setAttribute("aria-label", "Search documents");
    si.addEventListener("input", function () { S.q = si.value; renderLibrary(); });
    srch.appendChild(si);
    var x = h("button", "x", "×");
    x.type = "button"; x.setAttribute("aria-label", "Clear search");
    x.addEventListener("click", function () { si.value = ""; S.q = ""; renderLibrary(); si.focus(); });
    srch.appendChild(x);
    el.libCard.appendChild(srch);
    el.lib = h("ul", "lib");
    el.libCard.appendChild(el.lib);
    el.custom = h("div");
    el.custom.style.marginTop = "10px";
    el.libCard.appendChild(el.custom);
    app.appendChild(el.libCard);

    el.picked = h("div");
    app.appendChild(el.picked);

    el.tuneCard = h("div", "card");
    el.tuneCard.appendChild(h("h2", "blk", "2 · Make it yours"));
    el.tune = h("div");
    el.tuneCard.appendChild(el.tune);
    app.appendChild(el.tuneCard);

    el.outCard = h("div", "card");
    el.outCard.appendChild(h("h2", "blk", "3 · Set it up once"));
    el.steps = h("ol", "steps");
    el.outCard.appendChild(el.steps);
    var lbl = h("p", "subhead", "Your instructions — this is what you paste");
    el.outCard.appendChild(lbl);
    el.out = h("pre", "block");
    el.outCard.appendChild(el.out);
    app.appendChild(el.outCard);

    var heads = h("div", "card grey");
    var hd = h("div", "heads");
    hd.innerHTML = "<b>Before you lean on it — 30 seconds:</b><ul>" +
      "<li><b>It never makes anything up.</b> If a reading, a time, a serial or an approval was not in what you gave it, it writes <code>&lt;MISSING&gt;</code> and lists it to chase. Gaps stay visible instead of getting invented.</li>" +
      "<li><b>It never says a number is good, in range or to code.</b> It records what you measured. The call stays yours.</li>" +
      "<li><b>You still own what you send.</b> Read it before it goes out — your name is on it, not the AI's.</li>" +
      "<li><b>Don't paste anything into an AI you wouldn't put in an email</b> — badge numbers, customer-confidential detail, anyone's personal information. What you type on THIS page never leaves your phone; what you paste into the AI is a different decision.</li>" +
      "<li>If your AI caps how long instructions can be, a Gemini Gem or a Claude Project takes the most.</li>" +
      "</ul>";
    heads.appendChild(hd);
    app.appendChild(heads);

    /* bottom bar */
    var bar = h("div", "bar");
    el.count = h("div", "count", "Pick a document to start");
    bar.appendChild(el.count);
    var b2 = h("button", null, "Setup + block");
    b2.type = "button"; b2.id = "copyAll";
    b2.addEventListener("click", function () { if (current()) copyText(wholeSetup(), b2, "Copied"); });
    bar.appendChild(b2);
    var b1 = h("button", null, "Copy instructions");
    b1.type = "button"; b1.id = "copy";
    b1.addEventListener("click", function () { if (current()) copyText(compose(), b1, "Copied — go paste it in"); });
    bar.appendChild(b1);
    document.body.appendChild(bar);

    renderAll();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();

  window.DocSpec = { families: FAMILIES, shared: SHARED_DOCS, compose: compose };
})();
