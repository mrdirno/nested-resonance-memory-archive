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
 * AND THE DOCUMENT THAT IS *NOT* IN THE LIBRARY GETS ONE TOO (2026-08-15). For
 * months the custom path — the graceful failure of search, and the only path a
 * man reaches when what he has to write has no entry — answered that field with
 * a single hardcoded sentence, the same string on all nine trades and all five
 * families, while claiming to be about "this trade". It now picks from five
 * OMISSION CLASSES derived by classifying every one of the 80 hand-written
 * `omit` lines on disk, each demanding a concrete artefact: a date · a name · a
 * before-value · a location · a named gap. See §THE OMISSION CLASSES below for
 * the counts, the per-family seed, and the 15% of real lines no fixed class can
 * reach. `facts`, `why` and `secondary` on that same object were shrugging for
 * the same reason and now come from the family too.
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
 *   <script src="../shared/find.js"></script>
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
      why: "It repeats, so its whole value is the trail. Each one is worth only what it says CHANGED, and read end to end they are the record of every day you were there.",
      facts: ["the date", "the job or site", "who was on it", "what actually moved since the last one", "what is stopped, and who owns it"],
      secondary: ["a rollup across several of these", "a shorter version for whoever only needs the headline"],
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
      why: "Written once and read by people who were not there, sometimes years later. The only version that survives is the one written the same day.",
      facts: ["the date and time", "the exact location", "who was involved and who saw it", "what the state already was when you got there", "who was told, when, and how"],
      secondary: ["a short notification message to send with it", "a follow-up once the corrective action is done"],
      delta: false,
      spine: [
        { h: "WHAT HAPPENED", r: "plain sequence with times and dates; facts only, no characterization of people" },
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
      why: "Somebody is going to lean on this later. Its whole value is that it says exactly what was checked, exactly what was not, and which of the two anybody is relying on.",
      facts: ["the date and who did it", "what was tested and what was NOT", "the readings you took and where you took each one", "what could not be checked, and why"],
      secondary: ["a one-page summary for whoever signs it", "the open items on their own, as a punch list"],
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
      why: "The clock only starts when somebody is told in writing with a date on it. This is that letter, and it asks for one thing.",
      facts: ["what you need, and the date you need it by", "who owes it", "the date you first asked", "what work it is holding"],
      secondary: ["a short version for a text message", "a follow-up that carries the original dates forward"],
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
      why: "Nobody remembers the discussion and everybody argues the decisions. This is the record of what got decided, who owns it, and by when.",
      facts: ["the date and who was there", "what was decided, and by whom", "each action item, its owner and its date", "what is still open"],
      secondary: ["a short email body to circulate it with", "just the action items, as a list"],
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

  /* ── THE OMISSION CLASSES — the custom path only ────────────────────────
   * §THE HIGHEST-VALUE FIELD IN THE LIBRARY IS `omit`. Every one of the 80
   * documents on disk carries a hand-written one naming the specific thing that
   * costs money on THAT document. The custom path — the one a man reaches when
   * what he has to write is not in the library — carried a single generic
   * sentence standing in for all 80, identical on every trade and every family,
   * and it even claimed to be trade-specific ("on almost every document in this
   * trade") while being the same string in all nine.
   *
   * These are the classes those 80 lines actually fall into. Each one demands a
   * CONCRETE ARTEFACT he has to physically supply — a date, a name, a place a
   * file lives, a value from before, a thing named that he did not touch. That
   * is the whole bar: "add more detail" is not an omit line, and a tick list of
   * ten soft ones is the generic sentence with extra steps.
   *
   * THE FIFTH ONE WAS NOT IN THE PLAN. The rung was recorded as FOUR — a date,
   * a name, a photo location, a before-value. Classifying the 80 shipped lines
   * put "what you did NOT do, by name" level with the biggest of them and made
   * it the single most common thing a RECURRING document leaves out ("where you
   * COULDN'T work", "the idle half of the job"). The corpus outranks the plan.
   *
   * NO KEYWORD CLASSIFIER, and this is a rule not a shortcut: nothing here reads
   * the document NAME he typed. The family is picked by hand because guessing it
   * silently flips `delta`, and an incident record written as an update to a
   * previous one that does not exist is the §SCARS 2026-08-11 defect.
   *
   * WHAT THESE CANNOT REACH, MEASURED RATHER THAN WAVED AT: 12 of the 80 shipped
   * lines (15%) name something no fixed class of MISSING FACT can express. The
   * sharpest is av/theory-of-operation — "the design decisions that look like
   * faults... so by month two the help desk has logged them as defects" — where
   * the omission is an INTERPRETATION, not a date, a name, a place or a value.
   * The rest are mostly a reference class in the notice family (the sheet number
   * and revision a letter is written against, 4 of 26). A tick list does not
   * reach any of them and neither would five fixed sentences; the house-rules
   * box is the only surface that does, which is one more reason it stays free
   * text and this stays ticks.
   */
  /* ── THE ARTEFACT VOCABULARY — what actually SATISFIES an omitted line ──
   * (2026-08-28)
   *
   * The five classes below each carry an `artefact` string, and for the whole
   * life of this engine that string reached ONE surface: the tick list on the
   * CUSTOM path — the path a man reaches when his document is NOT in the
   * library. The 231 documents that ARE in the library, the ones everybody
   * actually opens, printed their hand-written `omit` line and never once said
   * what would satisfy it. Both readers were left to infer it, and both infer
   * it wrong in the same direction:
   *
   *   · THE MODEL writes a fluent sentence on the topic. hvac/red-tag-notice
   *     says "the time you shut it off and the name of the human you handed it
   *     to"; what comes back is "the unit was taken out of service and the
   *     property manager was notified." The heading is there, the sentence is
   *     there, no <MISSING> anywhere — and the only two facts that survive a
   *     dispute, the clock time and the name, are not in it. Nothing in this
   *     engine ever told it that a sentence is not the artefact.
   *   · THE MAN cannot see it either, and this is the harder half: he KNOWS he
   *     handed it to Denise at 2:40, so he reads her name into a sentence that
   *     does not contain it. A field foreman named this failure unprompted as
   *     the one he cannot catch by eye, on the document where it costs the most.
   *
   * So the artefact stops being decoration on a tick list and becomes a
   * DECLARED REQUIREMENT of every omitted line in the library — authored beside
   * the line as `needs`, emitted to the model as a demand, and printed for the
   * man in the red frame before he opens his mouth. §SHAPE #4 HAS TWO READERS
   * wrote the rule three days before this: "any field authored into one of these
   * libraries whose only consumer is a machine is on the clock."
   *
   * SEVEN, NOT FIVE, AND THE FORK IT SETTLES IS ON RECORD. The 2026-08-15 blind
   * re-classification of the same corpus derived SEVEN classes and named the two
   * extra: an undocumented CHANGE (the substitution, the setting left changed,
   * the valve left non-normal — 10 of 80) and a quantified MEASUREMENT (a number,
   * its unit, and the datum it was read from — 8 of 80). Both were refused, and
   * the stated reason was that "seven ticks is the ten generic ones the rung
   * forbade" — a decision about a TICK LIST, where every extra row is a row a man
   * in a hurry has to read. This is not a tick list. Nothing here is ticked;
   * `needs` is authored once by whoever writes the document. The constraint that
   * capped the vocabulary at five was a UI constraint, and it has been silently
   * governing a DATA vocabulary that has no UI. So the tick list stays at five,
   * exactly as decided, and the authored vocabulary is seven — and re-counted
   * over all 142 distinct omit lines on disk, `count` is the third most demanded
   * artefact in the whole library. It was not a rounding error; it was invisible.
   *
   * AND `none` IS A REAL VALUE, NOT A FAILURE TO CLASSIFY. The 2026-08-15 cycle
   * measured that 15% of the shipped lines name something no fixed class of
   * missing FACT can express — av/theory-of-operation's "the design decisions
   * that look like faults" is an omission of INTERPRETATION. Forcing those into
   * a class would put a confident demand under a line that cannot satisfy it,
   * which is the same lie as an empty check. They declare `none`, the block asks
   * for the line without naming an artefact, and the card says so in words.
   */
  var ARTEFACTS = {
    when:    { demand: "a date or a clock time", short: "the time",        miss: "the date or time" },
    who:     { demand: "a name",                 short: "the name",        miss: "the name" },
    before:  { demand: "a before-value",         short: "the before-value", miss: "what it was before" },
    where:   { demand: "a location",             short: "the location",    miss: "where it is" },
    count:   { demand: "a number with its unit", short: "the number",      miss: "the number" },
    change:  { demand: "what you left changed",  short: "what changed",    miss: "what was changed" },
    notdone: { demand: "a named gap",            short: "the named gap",   miss: "what was not done" },
    /* THE EIGHTH, AND THE CORPUS FORCED IT THE SAME WAY THREE TIMES. A document
       and its revision — the sheet, the bulletin, the proposal's scope line, the
       packing list, the approved version a yes was given against. The 2026-08-15
       blind pass hit it and filed it unreachable ("the sheet number and revision
       a letter is written against, 4 of 26"); of the two blind passes run over
       the full 142 this cycle, one pushed it into `none` and the other into
       `where`. Both are wrong in opposite directions and the wrongness is
       legible: a sheet number is the most concrete artefact in the whole corpus,
       so `none` is a shrug — and "say the actual A LOCATION" under "the sheet
       numbers and revisions" names the wrong kind of thing. Eight lines demand
       it, and framing/wont-fit is the whole argument: "the sheet numbers and
       revisions, WITHOUT WHICH THE QUESTION CANNOT BE ANSWERED BY ANYONE." */
    ref:     { demand: "the document and its revision", short: "the document",
                                                                              miss: "which document and revision" }
  };

  /* THE DEMAND, IN WORDS, FOR BOTH READERS FROM ONE PLACE. The card and the
     block must never be able to name different artefacts for the same line —
     that is the tautology trap the say-list gate fell into, so they call this. */
  function demandOf(ids) {
    var parts = [];
    for (var i = 0; i < (ids || []).length; i++) {
      var a = ARTEFACTS[ids[i]];
      if (a && parts.indexOf(a.demand) < 0) parts.push(a.demand);
    }
    if (!parts.length) return "";
    if (parts.length === 1) return parts[0];
    return parts.slice(0, -1).join(", ") + " and " + parts[parts.length - 1];
  }

  var OMIT_CLASSES = [
    {
      id: "when",
      label: "The date it actually started",
      artefact: "a date",
      line: "The date this actually started — not the date I am writing it up. The day the condition first existed, the day I first asked, the day somebody was first told. It is the only line that establishes how long a thing has really been sitting, and it is the first one left out."
    },
    {
      id: "who",
      label: "Who said go ahead, and how",
      artefact: "a name",
      line: "Who authorized it, when, and by what channel — verbal, call, text or email. A name with a time on it is the difference between a change order and a donation; \"they said it was fine\" is not one."
    },
    {
      id: "before",
      label: "What it was like before I touched it",
      artefact: "a before-value",
      line: "The condition that was already wrong before I got there, and the reading or count from before anything changed. Without it there is no before, only an after, and the whole thing reads as though it started with me."
    },
    {
      id: "where",
      label: "Where the photos and readings are",
      artefact: "a location",
      line: "Where the photos, readings and tags actually live, how many there are, and what each one shows. A description with no photo reference and no timestamp is worth nothing in a back-charge meeting, and anything that got covered over is gone for good."
    },
    {
      id: "notdone",
      label: "What I did NOT do, and why",
      artefact: "a named gap",
      line: "What I did not do, by name, and why — what I could not get to, what I never tested, where I could not work and what stopped me. Left out I own it by silence, and it is the first section cut for looking clean."
    }
  ];

  /* WHICH ONE STARTS TICKED, PER FAMILY — and it is ONE.
   *
   * The first draft seeded THREE, on the reasoning that three is what the trade
   * author who wrote `omit` as a LIST chose, five times out of five. That is the
   * MAX of five documents; the MODE of all eighty is one, by 75 to 5. The
   * heading this feeds is the word "ONE", the doctrine in this file's own header
   * is "the ONE line", and whatever ships pre-ticked is what a man in a hurry
   * keeps — so the default biases DOWN and the other four are one tap away.
   *
   * Each pick is the most common class among the shipped `omit` lines OF THAT
   * FAMILY, counted by hand over all eighty:
   *   recurring    notdone 3 · where 2 · who 2      (n=8)
   *   incident     before 8 · notdone 6 · who 5     (n=23)
   *   notice       when 8 · who 4 · notdone 3       (n=26)
   *   verification notdone 7 · who 5 · where 3      (n=19)
   *   minutes      when 2 · who 2                   (n=4 — see below)
   *
   * MINUTES IS A TIE AT n=4 AND THE TIEBREAK IS STATED, not hidden: `who` loses
   * because the minutes SPINE already carries WHO WAS THERE "and anyone who was
   * expected and did not attend", and an omit line that repeats a section
   * heading protects nothing. `when` — the date an item was FIRST raised, the
   * deadline to disagree — appears nowhere in that spine.
   *
   * `who` and `where` win no family and are the strongest runners-up in three,
   * which is the argument for a tick list rather than five fixed sentences.
   *
   * IT IS A PRIOR AND THE PAGE SAYS SO. Library documents in a family are the
   * COMMON ones; a custom document is by definition an uncommon one. He can tick
   * and untick every one, and an untouched tick follows the seed the way an
   * untouched TOGGLE follows `on`.
   */
  var FAM_OMIT = {
    recurring:    ["notdone"],
    incident:     ["before"],
    notice:       ["when"],
    verification: ["notdone"],
    minutes:      ["when"]
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
      needs: ["who", "change"],
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
      needs: ["when", "before"],
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
      needs: ["when", "where"],
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
      needs: ["when"],
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
      omit: "Who authorized it, when, and by what channel — verbal, call, text, email. That one line is the difference between a change order and a donation.",
      needs: ["when", "who"],
      halt: "Only if the work being described is not stated at all.",
      facts: ["what was asked for and by whom", "when it was authorized and how", "what the contract scope actually said", "what it displaced"],
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
      needs: ["notdone"],
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
      needs: ["when", "where", "notdone"],
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
      needs: ["when", "who", "notdone"],
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
      needs: ["notdone"],
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
      needs: ["none"],
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
      needs: ["when", "who"],
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
    "Forwardable tone. Write every line as if the person above me and the customer will both read it. When something is late or missing, state the facts, the dates and the impact, then make one specific ask. Never assign blame and never characterize people. (\"Requested 07/22, no response as of 07/29, holds the east rooms\" — not \"they are ignoring us.\")",
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
    { id: "co", label: "Flag anything that smells like extra work", sub: "who asked, when, how it was authorized", on: true },
    { id: "short", label: "Keep it short — a screen, not a page", sub: "for the ones that get read on a phone", on: false },
    { id: "email", label: "Also give me a one-line subject and a two-line email body", sub: "for sending it on", on: false }
  ];

  /* ── THE DESK: MORE THAN ONE DOCUMENT IN ONE SETUP (2026-08-16) ─────────
   * For two months this engine emitted a setup for exactly ONE document. That
   * is not how anybody's paperwork works. A lead writes a daily every day, an
   * incident report four times a year and a delay letter when he has to — and
   * the setup this page hands him covers one of the three. Nobody keeps three
   * Custom GPTs. He sets up the daily and the other two stay unwritten, which
   * means the page shipped a real answer to a third of the job.
   *
   * The fix was already stated in this file's own header and never acted on:
   * "Ten of those eleven [blocks] are IDENTICAL for a plumber's back-charge
   * notice and an AV daily. Only the spine, the omitted line and the vocabulary
   * change." If that is true — and the eleven blocks below are the proof — then
   * a second document costs only the parts that differ. So the block splits:
   *
   *   ONCE, at the top ...... ROLE · the ROUTER · DEFAULTS · OPERATING
   *                           PRINCIPLES · ATTRIBUTION · INPUT HANDLING ·
   *                           EXTRA WORK · PROTOCOL REMINDERS
   *   ONCE PER DOCUMENT ..... WHAT THIS DOCUMENT IS FOR · CONTINUITY ·
   *                           VALIDATION · the line everyone leaves out ·
   *                           OUTPUT FORMAT · SECONDARY REQUESTS
   *
   * The per-document half is deliberately WHOLE and repeated rather than
   * factored — this is a prompt, not code, and an AI that jumps to one section
   * must find everything that section needs inside it.
   *
   * THE ROUTER IS THE LOAD-BEARING PART, and the failure mode it exists for is
   * BLENDING: given three formats and one dump, a model will happily produce a
   * daily with an incident's evidence section welded on. So the router names the
   * documents with the words he actually says for them (`aka`, already in the
   * library for search), gives his own first line priority over anything the
   * model infers, permits exactly one question back, and forbids blending and
   * multi-output outright.
   *
   * ONE DOCUMENT STILL EMITS EXACTLY WHAT IT EMITTED BEFORE, byte for byte —
   * compose() dispatches to the untouched single-document composer, and
   * tools/toolkit-gates/docspec-desk.mjs holds it to a golden snapshot taken
   * from the shipped engine across all 170 library documents and all 55
   * custom-path states before a line of this was written.
   *
   * THE CAP IS SIX and it is not tidiness: some AIs cap how long instructions
   * can be, and the page says the character count out loud rather than quoting
   * a limit for somebody else's product that we cannot verify and that changes.
   */
  var MAX_DOCS = 6;

  /* ── state ─────────────────────────────────────────────────────────────── */
  var S = {
    doc: null,        // primary picked doc id, or "__custom"
    more: [],         // THE DESK: additional library doc ids, in the order he added them
    customName: "",
    customFamily: "recurring",
    platform: "gemini",
    role: "",
    to: "",
    me: "", second: "", office: "", company: "",
    off: {},          // section headings the user turned off
    tog: {},          // toggle id -> bool
    comit: {},        // custom path: omission class id -> bool. UNSET = follow the family seed.
    extra: "",
    q: "",            // search text
    adding: false     // THE DESK: the library is open to ADD a second document
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
    S.adding = false;
    /* A STORED LIST IS UNTRUSTED INPUT, and this one outlives the library it
       points into: a document dropped from a trade's docs.js leaves a dead id in
       somebody's localStorage forever. byId() returns null for it, and an
       unfiltered null reached compose() as `d.name`. Sanitised on load AND
       re-filtered in picked(), because the library is also re-derived there. */
    if (!Array.isArray(S.more)) S.more = [];
    S.more = S.more.filter(function (id, i) {
      return typeof id === "string" && id !== "__custom" && id !== S.doc && S.more.indexOf(id) === i;
    }).slice(0, MAX_DOCS - 1);
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

  /* ── THE FAMILY, RESOLVED SAFELY ────────────────────────────────────────
   * The family drives the CONTINUITY RULE, so an unknown one must never resolve
   * to a family that reports deltas. framing/docs.js declared `family:
   * "handover"` — a shared DOCUMENT ID, not a family — on all five of its
   * documents, and the old `FAMILIES[f] || FAMILIES.recurring` turned every one
   * of them into a document written as an UPDATE to the last one. §THE THREE
   * SHAPES says it plainly: an incident record read three years later must never
   * be written as an update. A damage letter that opens by dropping "anything
   * already reported finished" is the one document in the library that has to
   * carry every fact every time.
   *
   * So the fallback is asymmetric ON PURPOSE. Falling back to stand-alone costs
   * a recurring report its delta convenience — an inconvenience. Falling back to
   * recurring corrupts a record somebody relies on years later — a defect. The
   * gate (tools/toolkit-gates/docspec-config.mjs) refuses an unknown family
   * outright; this is the belt underneath it, because a trade shipped from a
   * branch that skipped the gate still must not emit a lie.
   */
  var UNKNOWN_FAMILY = {
    name: "A record written once",
    hint: "written once and read later",
    delta: false,
    spine: FAMILIES.incident.spine
  };
  var warned = {};
  function famOf(doc) {
    var f = doc && doc.family;
    if (f && FAMILIES[f]) return FAMILIES[f];
    var k = String(f);
    if (!warned[k] && window.console && console.warn) {
      warned[k] = 1;
      console.warn("[docspec] unknown family " + JSON.stringify(f) + " on document " +
        JSON.stringify(doc && doc.id) + " — treating it as stand-alone. Valid: " +
        Object.keys(FAMILIES).join(", "));
    }
    return UNKNOWN_FAMILY;
  }

  /* ── ONE DOCUMENT MAY OPT OUT OF ITS FAMILY'S CONTINUITY RULE ───────────
   * The family gives a document its spine AND its continuity rule, and for
   * eleven of the twelve shared documents those two travel together. The
   * exception found on the sweep is `electrical/confirming-note` — "a verbal
   * instruction is worth nothing in April; this is the ten-line email that makes
   * it worth something, sent the same hour". It is genuinely MINUTES-shaped: it
   * records a conversation and what got decided. But minutes report DELTAS,
   * because a coordination meeting recurs — and a confirming note does not.
   * Each one memorialises a DIFFERENT conversation, so writing the second as an
   * update to the first drops the facts of the first and carries open items
   * across from a conversation that has nothing to do with it. The page was
   * also telling him to run one chat per job and paste the last one in, which is
   * precisely how that corruption happens.
   *
   * Re-familying it to a delta-false family would fix the behavior by lying
   * about what the document is — the card would call a confirming note "a record
   * of a thing that happened". So the family keeps the label and the spine, and
   * a document may say `standalone: true` to keep every fact every time. The
   * flag only ever moves toward stand-alone; there is deliberately no way to
   * force delta ON, because that is the direction that corrupts a record.
   */
  function deltaOf(doc) {
    if (doc && doc.standalone === true) return false;
    return !!famOf(doc).delta;
  }

  /* ── THE OMITTED LINE, WHICH MAY BE A LIST ──────────────────────────────
   * `omit` is the highest-value field in the library (§THE FOURTH SHAPE), and
   * framing/docs.js writes THREE specific omission lines per document where the
   * field was built for one. That is better authoring, not a mistake — three
   * named lines are three the AI cannot quietly drop — but it shipped as an
   * ARRAY into shortOmit(), which called .split on it. compose() threw, and the
   * entire product of the page (the block you paste into your AI) rendered
   * EMPTY for all five of that trade's documents, on the live site, silently:
   * the picked card appeared, the tuner appeared, and the one thing the page
   * exists to produce was blank (§SCARS 2026-08-11).
   *
   * Both shapes are legal now and every trade may use either. The gate
   * exercises EVERY document in EVERY trade through the real page, so a third
   * shape cannot ship the same way this one did.
   */
  function omitLines(d) {
    var o = d && d.omit;
    if (Array.isArray(o)) {
      return o.filter(function (x) { return typeof x === "string" && x.trim(); });
    }
    if (typeof o === "string" && o.trim()) return [o];
    return [];
  }

  /* ── WHAT SATISFIES EACH OF THOSE LINES ─────────────────────────────────
   * `needs` MIRRORS THE SHAPE OF `omit`, and that is a contract the gate holds
   * rather than a convention: a string omit takes a flat array of artefact ids,
   * a list omit takes one array PER LINE, in the same order. Anything else and
   * the demand under line two would describe line one — a confident sentence
   * pointing at the wrong fact, which is worse than no sentence at all.
   *
   * IT RETURNS ONE ENTRY PER OMIT LINE, ALWAYS, so no caller has to index-guard.
   * An unauthored line comes back `[]`, which every reader treats as "ask for
   * the line, name no artefact" — the honest degrade, identical to `none`.
   * That is a BELT, not a licence: tools/toolkit-gates/docspec-needs.mjs fails
   * the build on a library document that authors `omit` without `needs`, for the
   * reason the say-list gate learned the hard way — a gate that accepts its own
   * fallback is measuring its safety net (§SCARS 2026-08-24).
   */
  function needsOf(d) {
    var lines = omitLines(d);
    var n = d && d.needs;
    var out = [];
    var perLine = Array.isArray(n) && n.length && Array.isArray(n[0]);
    for (var i = 0; i < lines.length; i++) {
      var row = perLine ? n[i] : (i === 0 && Array.isArray(n) ? n : null);
      row = Array.isArray(row) ? row : [];
      /* `none` is EXCLUSIVE and is not an artefact. It reaches here as an empty
         demand, which is exactly what an unauthored line reaches here as — and
         they are not the same thing to the GATE, which reads d.needs directly. */
      out.push(row.filter(function (k) { return !!ARTEFACTS[k]; }));
    }
    return out;
  }

  /* ── WHAT HE HAS TO SAY, WHICH IS THE HALF THAT WAS ONLY EVER TOLD TO THE AI ──
   * (2026-08-25) `facts` is authored per document — 214 documents, 661 distinct
   * strings — and until this cycle it reached exactly one reader: the model, in
   * the VALIDATION block of a 9,500-character setup a man pastes into a Gem once
   * and never opens again. The person whose job it is to SUPPLY those facts was
   * never shown them. The engine's own instructions then bill him for it: every
   * fact he did not say comes back <MISSING>, and the omitted line — the field
   * this program is built around — comes back <MISSING> at the TOP of the open
   * items BY DESIGN, because he was never told to say it while he was talking.
   *
   * So the same authored data now renders on the page as the say-list, and the
   * only thing it adds is the continuity cue, which is the one thing that is
   * true of the FAMILY rather than the document: a recurring report is worth
   * what CHANGED, and a stand-alone record is read by somebody who was not
   * there. Both sentences are compressions of the CONTINUITY block this engine
   * already emits — no new claim, no new authored content.
   *
   * THE FALLBACK IS ASYMMETRIC, the same way famOf()'s is. A document with no
   * facts of its own inherits its FAMILY's, because the failure it replaces
   * shipped live: five framing documents author none, and the block read
   * "Before you write, check the input for: ." — an empty check on the one
   * instruction that decides whether his report comes back full of holes.
   * Inheriting a family's five generic facts is worse than five authored ones
   * and enormously better than nothing, and the gate refuses the empty case
   * outright so the belt is never load-bearing.
   */
  function factsOf(d) {
    var own = (d && d.facts) || [];
    own = own.filter(function (x) { return typeof x === "string" && x.trim(); });
    if (own.length) return own;
    return (famOf(d).facts || []).slice();
  }

  /* TWO FORMS, ONE SOURCE. On the CARD the cue trails the list it belongs to, so
     it opens with an ellipsis and continues the thought. In the COPY there is a
     blank line before it and it is the last thing in a text message somebody
     else opens cold — and the first draft simply stripped the "…", leaving a
     forwarded message ending in a lowercase "and only what CHANGED…" with no
     antecedent. A sentence that only parses when glued to the thing above it
     cannot be sent on its own. Same words, two endings, one place to change. */
  var CUES = {
    delta: ["only what CHANGED since the last one — you do not have to re-say what already finished.",
            "Only what CHANGED since the last one — you do not have to re-say what already finished."],
    once:  ["say it whole. Whoever reads this was not there, and may be reading it years from now.",
            "Say it whole. Whoever reads this was not there, and may be reading it years from now."]
  };
  function sayCue(d) { return "…and " + CUES[deltaOf(d) ? "delta" : "once"][0]; }
  function sayCueSentence(d) { return CUES[deltaOf(d) ? "delta" : "once"][1]; }

  function spineOf(doc) {
    if (doc.sections && doc.sections.length) return doc.sections;
    return famOf(doc).spine;
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
  /* THE HEADING THAT SHIPS. The prose block above pluralises ("THE LINES
     EVERYONE LEAVES OUT — NEVER DROP THEM"); the OUTPUT FORMAT heading — the one
     that ends up in the finished document somebody else reads — did not, so all
     five of framing's own documents have been shipping three bullets under the
     word "ONE" since the day multi-omit landed. Found by an adversarial pass on
     a trade this cycle was not touching, and confirmed against the real page.
     LOCKED[0].h stays the canonical key, because isLocked() and S.off both key
     off it; only the PRINTED form moves. */
  function lockedHeading(hdg, n) {
    if (hdg === LOCKED[0].h && n > 1) return "THE ONES NOBODY WRITES DOWN";
    return hdg;
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

  /* ── THE OMISSION TICKS (custom path) ───────────────────────────────────
   * UNSET follows the family seed; SET is his. Exactly the rule TOGGLES already
   * uses (`S.tog[id] === undefined ? t.on : ...`), for exactly the same reason:
   * a control he has never touched should move when the thing it depends on
   * moves, and one he HAS touched should not be silently overwritten. So
   * changing family re-seeds the ticks he left alone and keeps the ones he set —
   * unlike `S.off`, which is wiped on a family change because the SPINE it keys
   * off is a different list of headings afterwards.
   */
  function omitSeed(fam) { return FAM_OMIT[fam] || FAM_OMIT.recurring; }
  function comitOn(id, fam) {
    var v = S.comit[id];
    if (v === undefined) return omitSeed(fam).indexOf(id) !== -1;
    return !!v;
  }
  function customOmits(fam) {
    var out = [];
    OMIT_CLASSES.forEach(function (c) { if (comitOn(c.id, fam)) out.push(c.line); });
    return out;
  }

  function current() {
    if (S.doc === "__custom") {
      var fk = FAMILIES[S.customFamily] ? S.customFamily : "recurring";
      var f = FAMILIES[fk];
      return {
        id: "__custom",
        name: S.customName || "Write-Up",
        family: fk,
        from: "", to: "",
        /* `sections: f.spine` was the one field on this object already doing the
           right thing, and it is the pattern the rest now follow. `why` was the
           family PICKER's blurb read out as a purpose statement; `facts` — which
           feeds the VALIDATION block, i.e. what the AI is told to check the input
           for before it writes — was three generic words, the same three for a
           near-miss, a delay letter and a set of minutes; `secondary` was empty
           where every library document offers one or two. All three shrugged for
           the same reason `omit` did, and all three had a family to ask. */
        why: f.why || f.hint,
        omit: customOmits(fk),
        halt: "Only if the input does not say what the document is about at all.",
        facts: f.facts || ["date", "job or site", "who was involved"],
        sections: f.spine,
        secondary: (f.secondary || []).slice()
      };
    }
    return S.doc ? byId(S.doc) : null;
  }

  /* THE DESK, RESOLVED. Primary first — it is the one he tuned — then the extras
     in the order he added them. Dead ids are dropped here as well as on load
     because the library is re-derived on every call and a trade may drop a
     document between the two. */
  function picked() {
    var out = [];
    var seen = {};
    var p = current();
    if (p) { out.push(p); seen[p.id] = 1; }
    (S.more || []).forEach(function (id) {
      if (seen[id]) return;
      var d = byId(id);
      if (d) { out.push(d); seen[id] = 1; }
    });
    return out.slice(0, MAX_DOCS);
  }
  function inDesk(id) {
    return S.doc === id || (S.more || []).indexOf(id) !== -1;
  }

  /* ── THE COMPOSER — the eleven blocks ──────────────────────────────────── */
  function nz(v, fb) { v = (v || "").trim(); return v || fb; }

  /* ONE DOCUMENT OR THE DESK. The single-document path below is untouched and
     must stay byte-identical — tools/toolkit-gates/docspec-desk.mjs holds it to
     a snapshot of the shipped engine. */
  function compose() {
    var ds = picked();
    if (!ds.length) return "";
    return ds.length === 1 ? composeOne(ds[0]) : composeDesk(ds);
  }

  /* ── THE BLOCKS, EXTRACTED SO THE DESK COULD REUSE THEM ─────────────────
   * 2026-08-16. Every string in these emitters is the one the single-document
   * composer has been shipping since the engine landed — they were lifted out
   * of it, not rewritten, so that adding a second document did not fork the
   * composer inside its own file (§THE THREE SHAPES: the second instance is
   * where the engine gets extracted). tools/toolkit-gates/docspec-desk.mjs
   * holds the one-document output to a golden snapshot taken from the shipped
   * engine across all 170 library documents and all 55 custom-path states
   * BEFORE the extraction, which is the only thing that makes it safe.
   *
   * WHICH BLOCKS ARE SHARED AND WHICH REPEAT PER DOCUMENT is not a style call —
   * it is the split this file's header claimed on day one and never used: the
   * ten that do not depend on the document go once at the top, and the six that
   * do go whole, per document, repeated. Repeated on purpose: this is a prompt,
   * and an AI that jumps to one document's section has to find everything that
   * section needs inside it.
   */
  function emitDefaults(L, ctx) {
    L.push("DEFAULTS");
    L.push("");
    L.push("- Me: " + ctx.me + (ctx.pickedRole ? " (" + ctx.pickedRole + ")" : ""));
    if (nz(S.second, "")) L.push("- Usually with me: " + S.second.trim());
    L.push("- Office / PM contact: " + nz(S.office, "<name>"));
    L.push("- Company: " + ctx.co);
    L.push("- Trade: " + ctx.tradeName);
    L.push("- " + (ctx.multi ? "Usually goes to" : "Goes to") + ": " + ctx.to);
    if (ctx.multi) L.push("Each document below names who that one goes to when it is somebody else.");
    L.push("Use these whenever the day's input does not say otherwise. Never ask me for something already established in this conversation.");
    L.push("");
  }

  function emitPrinciples(L, T) {
    L.push("OPERATING PRINCIPLES");
    L.push("");
    var pr = PRINCIPLES.slice();
    if (!T("plain")) pr.splice(4, 1);
    if (T("clientsafe")) pr.push("Customer-safe. Never name another company as being at fault and never put internal frustration on the page. State what happened and what is needed.");
    if (T("short")) pr.push("Keep it to one screen. If it does not change a decision, it does not go in.");
    pr.forEach(function (p, i) { L.push((i + 1) + ". " + p); });
    L.push("");
  }

  function emitAttrib(L) {
    L.push("ATTRIBUTION");
    L.push("");
    ATTRIB.forEach(function (a) { L.push("- " + a); });
    L.push("");
  }

  function emitInput(L, tradeName, multi) {
    L.push("INPUT HANDLING");
    L.push("");
    var n = 1;
    var vocab = (LIB.vocab || []);
    if (vocab.length) {
      L.push(n++ + ". Silently correct dictation and jargon errors to the proper " + tradeName +
        " terms. These are the ones my phone gets wrong: " + vocab.join("; ") +
        ". Correct anything else in the same spirit. Never mention the correction.");
    }
    L.push(n++ + ". Group scattered input into the sections of the output format " +
      (multi ? "for the document I am asking for" : "below") +
      ". If something does not fit a section, put it in the open items rather than dropping it.");
    INPUT_RULES.forEach(function (r) { L.push(n++ + ". " + r); });
    L.push("");
  }

  function emitContinuity(L, d) {
    if (deltaOf(d)) {
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
  }

  function emitValidation(L, d, onlyReason) {
    L.push("VALIDATION");
    L.push("");
    /* ONE PER LINE, NOT COMMA-JOINED (2026-08-25). `facts` was authored as short
       noun phrases and emitted with .join(", "), which held for the short ones
       and turned to mush the moment an author wrote a SENTENCE. On the real page
       hvac/compressor-failure-report emitted a 600-character run-on in which
       "…amps at failure. Your numbers, nothing graded, What the oil and the acid
       test showed…" reads as an instruction, a fragment and a new list item, all
       inside one line. The corpus is the argument: 661 distinct fact strings
       across 214 documents, from 4 characters to 240. A list is the only shape
       that carries both, it is the shape emitOmit() already uses for exactly
       this reason, and an AI cannot half-drop a bulleted item the way it can
       drop a clause. */
    var fx = factsOf(d);
    L.push("Before you write, check the input for:");
    fx.forEach(function (f) { L.push("- " + f); });
    L.push("");
    /* THE SECOND GROUP HAS TO SAY IT IS A DIFFERENT GROUP. Bulleting the facts
       (above) made them look exactly like the three rules that follow, which are
       not things to check for — they are what to DO about a thing that is not
       there. One blank line is not a boundary a model can be relied on to read,
       and "check the input for … - No date given: use today's date" is a list
       with an instruction sitting in it. So the rules get their own stem. */
    L.push("WHEN SOMETHING ON THAT LIST IS NOT IN MY INPUT:");
    L.push("- No date given: use today's date. If you cannot know today's date, write <MISSING: date> and flag it.");
    /* "NEVER HALT. THAT IS THE ONLY REASON TO STOP." Found 2026-08-16 by reading
       the block the page actually emits rather than the code that emits it. The
       tail sentence was written for a halt that names a condition ("Only if the
       input does not say which room this is") and it has been welded onto the
       nine documents whose authors said the opposite — three of them in the
       SHARED library, so it shipped on all eleven trades, on the one instruction
       that decides whether a man in a truck gets his report or gets interrogated.
       A model resolving that contradiction either way is guessing, and half the
       guesses are the wrong half. An author who wrote "Never halt" already stated
       the rule harder than the generic tail does, so the tail stands down. */
    var halt = d.halt || "Only halt if the input does not say what the document is about.";
    /* THE TAIL STANDS DOWN A SECOND WAY, BUT THE EXCLUSIVITY NEVER DOES
       (2026-08-25). The 2026-08-16 rule above silences the tail for an author who
       wrote "Never halt". Reading the real page found the mirror case: TWENTY-TWO
       halts across gc, hvac, low-voltage and plumbing already contain the verb
       ("Only stop and ask if …"), so the bullet shipped saying stop-and-ask twice
       in one sentence, which reads as two rules to a model deciding whether to
       interrogate a man in a truck.

       The first draft of this suppressed the tail on the verb alone — and an
       adversarial pass caught what that costs. TWENTY-ONE of the twenty-two also
       say "only", so dropping the tail is lossless. `gc/impact-notice` does not:
       "…Stop and ask — a weather day is its own notice, and a priced claim
       belongs to the PM and counsel." Verb, condition, no EXCLUSIVITY — and
       exclusivity is the whole reason the tail exists. Suppressing it there
       silently converted the one halt in the program that names two conditions
       into a licence to ask about anything.

       So the test is on what the sentence CLAIMS, not on which words it uses:
       the tail stands down only when the author has already made the rule
       exclusive. Where he used the verb without the exclusivity, it is supplied
       in words that do not repeat him. */
    var saysStop = /\bstop and ask\b|\bask me\b/i.test(halt);
    var saysOnly = /\bonly\b/i.test(halt);
    var tail = "";
    if (/^\s*Never\s+halt\b/i.test(halt)) tail = "";
    else if (saysStop && saysOnly) tail = "";
    else if (saysStop) tail = " That is the only thing you may come back to me about.";
    else tail = " " + onlyReason;
    L.push("- " + halt + tail);
    L.push("- Anything else missing: write the document anyway, put <MISSING> where the fact belongs, and list chasing it in the open items. A document with visible gaps is useful; a document that waits for me is not.");
    L.push("");
  }

  /* WHAT TO WRITE WHEN THE ARTEFACT IS NOT IN HIS INPUT. Named per artefact
     rather than as a bare <MISSING>, because the whole failure this closes is a
     gap that reads as an answer: "<MISSING>" under a line demanding two things
     does not say WHICH of the two is missing, and the man chasing it tomorrow
     has to re-read the source line to find out. One token per artefact. */
  /* The tokens alone, for the OUTPUT FORMAT placeholder, where the surrounding
     sentence is already the instruction and a second one would not fit inside a
     bracket the finished document has to read as a single field. */
  function missTokens(ids) {
    var toks = [];
    for (var i = 0; i < (ids || []).length; i++) {
      var a = ARTEFACTS[ids[i]];
      if (a && toks.indexOf("<MISSING: " + a.miss + ">") < 0) toks.push("<MISSING: " + a.miss + ">");
    }
    return toks.length ? toks.join(" / ") : "<MISSING>";
  }

  function missClause(ids) {
    var toks = [];
    for (var i = 0; i < (ids || []).length; i++) {
      var a = ARTEFACTS[ids[i]];
      if (a && toks.indexOf("<MISSING: " + a.miss + ">") < 0) toks.push("<MISSING: " + a.miss + ">");
    }
    if (!toks.length) return "";
    return "Where my input does not give you one, write " + toks.join(" / ") +
           " against that part rather than writing around it.";
  }

  /* A document may name more than one. Each gets its own bullet here AND its
     own bullet in the output format below, because the whole point of this
     block is that an AI cannot quietly drop the line nobody writes down —
     and a list folded into one paragraph is a list it can drop half of. */
  function emitOmit(L, omits, needs) {
    L.push(omits.length > 1 ? "THE LINES EVERYONE LEAVES OUT — NEVER DROP THEM"
                            : "THE LINE EVERYONE LEAVES OUT — NEVER DROP IT");
    L.push("");
    /* THE DEMAND RIDES WITH THE LINE IT BELONGS TO (2026-08-28). "Never drop it"
       was the only instruction here, and a model does not drop it — it ANSWERS
       it, fluently, with none of the facts in the answer. hvac/red-tag-notice
       asks for "the time you shut it off and the name of the human you handed it
       to" and gets back "the unit was taken out of service and the property
       manager was notified": heading present, sentence present, no <MISSING>
       anywhere, and both facts gone. So each line now states what would satisfy
       it and what to write when the input does not carry it. A line whose
       `needs` is `none` — the measured 15% whose omission is an interpretation
       rather than a missing fact — gets no demand, because a confident artefact
       demand under a line that cannot satisfy one is the empty check again. */
    if (omits.length > 1) {
      omits.forEach(function (o, i) {
        L.push("- " + o);
        var dm = demandOf((needs || [])[i]);
        if (dm) L.push("  Not satisfied by a sentence about it: this one has to carry " + dm +
                       ". " + missClause((needs || [])[i]));
      });
    } else if (omits.length) {
      L.push(omits[0]);
      var dm0 = demandOf((needs || [])[0]);
      if (dm0) {
        L.push("");
        var many0 = ((needs || [])[0] || []).length > 1;
        L.push("This is not satisfied by a sentence about it. It has to carry " + dm0 +
               (many0 ? " — actual ones, out of my input. " : " — an actual one, out of my input. ") +
               missClause((needs || [])[0]));
      }
    }
    L.push(omits.length > 1
      ? "Give each of these its own line in the finished document every single time. Where my input does not cover one, write <MISSING> against it and put chasing it at the TOP of the open items — do not quietly leave it out because I did not mention it."
      : "Give this its own line in the finished document every single time. If my input does not cover it, write <MISSING> against it and put chasing it at the TOP of the open items — do not quietly leave it out because I did not mention it.");
    L.push("");
  }

  function emitExtraWork(L) {
    L.push("EXTRA WORK — ISOLATE IT");
    L.push("");
    L.push("Anything in my input that is outside what we were originally there to do gets pulled into its own section, because it is billing evidence: work somebody else directed, materials used off another job, hours past the plan, a request that was not on the drawings, a substitution made to keep moving.");
    L.push("For each one: what changed, who asked for it, when, and how it was authorized (verbal / call / text / email). If the authorization is not in my input, write <MISSING> and add it to the open items. Never assume approval happened.");
    L.push("Do not price anything. No rates, no totals, no hours priced out — the office owns the number, I own what happened.");
    L.push("");
  }

  /* A REMINDER IS A STRING OR A {when, say} PAIR, and the emitter has to read
     both. Fourteen libraries write the string form; doors (trade #15) wrote
     the pair form — `{ when: "label", say: "…" }` — and for five days every
     one of its reminders reached the pasted block as "- [object Object]",
     found at trade #16's stand-up by the writer copying the doors shape. No
     gate read the reminder lines. The pair form is the better one (the
     trigger word is data, not prose), so it renders as "When <trigger> comes
     up: <say>" and the string form is byte-identical to what it always was. */
  function reminderLine(r) {
    if (r && typeof r === "object") {
      var w = String(r.when || "").trim(), say = String(r.say || "").trim();
      if (w && say) return "When " + w + " comes up: " + say;
      return say || w;
    }
    return String(r == null ? "" : r);
  }

  function emitReminders(L) {
    var rem = (LIB.reminders || []).map(reminderLine).filter(function (x) { return x; });
    if (!rem.length) return;
    L.push("PROTOCOL REMINDERS (trigger only when relevant — never nag)");
    L.push("");
    rem.forEach(function (r) { L.push("- " + r); });
    L.push("");
  }

  /* `useOff` is the section tick list, and it only ever applies to the document
     he is looking at. The others in a desk ship with their full spine — he tunes
     the one he writes daily and the four-times-a-year ones arrive whole, which
     is the right default for a document he does not have memorised. */
  function emitOutputFormat(L, d, omits, ctx, useOff) {
    L.push("OUTPUT FORMAT");
    L.push("");
    L.push("Output the document in a single plain-text code block, using exactly this structure. Leave out any section that is empty, except the last two, which always appear — write \"None\" if there is nothing. Keep both header lines even if a field is <MISSING>.");
    L.push("");
    L.push("[" + d.name.toUpperCase() + " | <JOB / SITE> | <MM/DD/YY>]");
    L.push("[" + (ctx.pickedRole ? ctx.pickedRole.toUpperCase() + ": " : "") + ctx.me.toUpperCase() +
      " | " + ctx.co.toUpperCase() + " | TO: " + (ctx.docTo || ctx.to).toUpperCase() + "]");
    L.push("");
    sectionsOf(d).forEach(function (s) {
      if (useOff && !isLocked(s.h) && S.off[s.h]) return;
      L.push("=========================================");
      L.push(lockedHeading(s.h, omits.length));
      L.push("=========================================");
      if (s.h === LOCKED[0].h) {
        if (omits.length) {
          /* THE PLACEHOLDER NAMES THE ARTEFACT TOO (2026-08-28). This is the
             half of the contract that ends up INSIDE the finished document, so
             it is the last instruction standing between the demand and a fluent
             sentence. `<MISSING>` alone was ambiguous under a line demanding two
             things; the per-artefact token says which half is gone. */
          var nd = needsOf(d);
          omits.forEach(function (o, i) {
            var dm = demandOf(nd[i]);
            L.push("- <" + shortOmit(o) +
              (dm ? " — carrying " + dm + ". Write " + missTokens(nd[i]) +
                    " against whichever I did not give you."
                  : ". Write <MISSING> against it if I did not give it to you.") + ">");
          });
        } else {
          L.push("- <the line everyone leaves out on this document. Write <MISSING> if I did not give it to you.>");
        }
      } else if (s.h === LOCKED[1].h) {
        L.push("- <" + s.r + ". Write \"None\" if there is nothing.>");
      } else {
        L.push("- <" + s.r + ">");
      }
      L.push("");
    });
  }

  function emitSecondary(L, d, T) {
    L.push("SECONDARY REQUESTS");
    L.push("");
    var sec = (d.secondary || []).slice();
    if (T("email")) sec.push("a one-line subject and a two-line email body to send it with");
    sec.push("a rich-text or table version, outside the code block, if I ask for one");
    L.push("If I ask for it, you can also produce: " + sec.join("; ") + ". Every rule above still applies.");
    L.push("Never produce any of these unless I ask.");
  }

  /* THE TRADE WORD is declared, never derived. It used to be TRADE.name with
     " Field Toolkit" sliced off, which produced "a AV outfit" (wrong article)
     and left GC reading "a GC & Site Super Toolkit outfit" — the trade whose
     name does not end in the string being stripped. A config value cannot be
     recovered by cutting a different config value; §THE THREE SHAPES says the
     caller owns its own words, so it declares this one.

     TWO DIFFERENT THINGS live in `role`, and conflating them printed "I am
     Whoever was on the call at <company>" into a production instruction block.
     `from` is the library's DESCRIPTION of who writes this document, shown on
     the library row; `pickedRole` is what THIS user tapped. The description can
     carry a clause and still read fine on a row; only the tapped value is short
     enough to go in a header line, so only it does. */
  function ctxOf(d, multi) {
    var pickedRole = nz(S.role, "");
    return {
      multi: !!multi,
      tradeName: LIB.trade || "field",
      me: nz(S.me, "<my name>"),
      co: nz(S.company, "<my company>"),
      to: nz(S.to, (d && d.to) || "the office"),
      pickedRole: pickedRole,
      role: pickedRole || (d && d.from) || "the person who was there"
    };
  }

  function emitExtra(L) {
    if (!nz(S.extra, "")) return;
    L.push("");
    L.push("EXTRA INSTRUCTIONS FROM ME — OBEY THESE TOO");
    L.push("");
    L.push(S.extra.trim());
  }

  function composeOne(d) {
    if (!d) return "";
    var ctx = ctxOf(d, false);
    var omits = omitLines(d);
    var T = function (id) { var t = S.tog[id]; return t === undefined ? defOn(id) : !!t; };
    var L = [];

    L.push("ROLE");
    L.push("");
    L.push("You write the " + d.name + " for my company. I am " + ctx.role + " at " + ctx.co +
      "; we do " + ctx.tradeName + " work. You convert my messy field input — voice-to-text dictation, " +
      "half-finished notes, pasted texts, end-of-day brain dumps — into one finished " + d.name +
      " I can send to " + ctx.to +
      " without editing it. Output the document and nothing else: no preamble, no commentary, no explaining what you did.");
    L.push("");
    L.push("WHAT THIS DOCUMENT IS FOR");
    L.push("");
    L.push(d.why);
    if (d.note) L.push(d.note);
    L.push("");

    emitDefaults(L, ctx);
    emitPrinciples(L, T);
    emitAttrib(L);
    emitInput(L, ctx.tradeName, false);
    emitContinuity(L, d);
    emitValidation(L, d, "That is the ONLY reason to stop and ask me a question.");
    emitOmit(L, omits, needsOf(d));
    if (T("co")) emitExtraWork(L);
    emitReminders(L);
    emitOutputFormat(L, d, omits, ctx, true);
    emitSecondary(L, d, T);
    emitExtra(L);

    return L.join("\n");
  }

  /* ── THE DESK — one setup, every document he actually writes ─────────────
   * See §THE DESK at the top of this file for why. The shape:
   *
   *   ROLE → THE ROUTER → the eight shared blocks → one whole section per
   *   document → his own extra instructions, once.
   *
   * THE ROUTER IS THE PART THAT EARNS THIS. Hand a model three output formats
   * and one dump and the failure is not that it picks wrong — it is that it
   * BLENDS, and emits a daily with an incident's evidence section welded on.
   * So: his own first line beats anything inferred, `aka` gives it the words he
   * actually says out loud, exactly one question back is allowed, and blending
   * and multi-output are forbidden by name.
   */
  var RULE = "----------------------------------------------------------------------";

  function routerNames(d) {
    /* The words he SAYS for it, not the words we filed it under. `aka` already
       exists for search; four is where a router line stops being a hint and
       starts being a wall of synonyms. */
    var a = (d.aka || []).filter(function (x) { return typeof x === "string" && x.trim(); });
    return a.slice(0, 4);
  }

  function composeDesk(ds) {
    var primary = ds[0];
    var ctx = ctxOf(primary, true);
    var T = function (id) { var t = S.tog[id]; return t === undefined ? defOn(id) : !!t; };
    var n = ds.length;
    var L = [];

    L.push("ROLE");
    L.push("");
    L.push("You write the paperwork for my company. I am " + ctx.role + " at " + ctx.co +
      "; we do " + ctx.tradeName + " work. You convert my messy field input — voice-to-text dictation, " +
      "half-finished notes, pasted texts, end-of-day brain dumps — into one finished document I can " +
      "send on without editing it. There are " + n + " documents you write for me; every one of them " +
      "has its own section further down. Output the document and nothing else: no preamble, no " +
      "commentary, no explaining what you did.");
    L.push("");

    L.push("WHICH ONE I AM ASKING FOR");
    L.push("");
    L.push("The " + n + " documents you write for me:");
    ds.forEach(function (d, i) {
      L.push((i + 1) + ". " + d.name + " — " + shortOmit(d.why || "") + ".");
      var a = routerNames(d);
      if (a.length) L.push("   I might call it: " + a.join(", ") + ".");
    });
    L.push("");
    L.push("Every dump I send you is ONE of these.");
    L.push("- If the first line of my input names one, that wins over anything you work out for yourself.");
    L.push("- Otherwise match what I sent against the list above and use the closest one.");
    L.push("- If two of them genuinely fit, ask me which one and nothing else. One word back from me is enough — do not ask me anything else in the same breath.");
    L.push("- NEVER blend two of them into one document. A daily with an incident report's sections welded on is not either document and it is worse than both.");
    L.push("- NEVER write more than one from a single dump unless I ask for both by name.");
    L.push("- Once you know which one it is, follow THAT document's section below exactly — its checks, its line everyone leaves out, and its output format. Everything above applies to all of them.");
    L.push("");

    emitDefaults(L, ctx);
    emitPrinciples(L, T);
    emitAttrib(L);
    emitInput(L, ctx.tradeName, true);
    if (T("co")) emitExtraWork(L);
    emitReminders(L);

    L.push(RULE);
    L.push("The rest of this is one section per document. The dashed rules are for");
    L.push("you to read — they never appear in anything you write.");
    L.push(RULE);
    L.push("");

    ds.forEach(function (d, i) {
      var omits = omitLines(d);
      /* He typed "Goes to" while looking at the primary, so his answer owns that
         one. The others carry the recipient their own library entry names, and
         fall back to his if the entry does not name one. */
      var dctx = {
        multi: true, tradeName: ctx.tradeName, me: ctx.me, co: ctx.co,
        to: ctx.to, pickedRole: ctx.pickedRole, role: ctx.role,
        docTo: i === 0 ? ctx.to : nz(d.to, ctx.to)
      };
      L.push("DOCUMENT " + (i + 1) + " OF " + n + " — " + d.name.toUpperCase());
      L.push(RULE);
      L.push("");
      L.push("WHAT THIS DOCUMENT IS FOR");
      L.push("");
      L.push(d.why);
      if (d.note) L.push(d.note);
      L.push("Goes to: " + dctx.docTo + ".");
      L.push("");
      emitContinuity(L, d);
      emitValidation(L, d, "That is the ONLY reason to stop and ask me a question about this one.");
      emitOmit(L, omits, needsOf(d));
      emitOutputFormat(L, d, omits, dctx, i === 0);
      emitSecondary(L, d, T);
      L.push("");
      if (i < n - 1) { L.push(RULE); }
    });

    emitExtra(L);

    return L.join("\n");
  }

  /* The omit line is a paragraph on the page and has to become a one-line prompt
     inside the output format. Cut at the first sentence or em-dash and trim —
     without the trim it printed "…and why . <MISSING>". */
  function shortOmit(t) {
    /* String() rather than (t || "") — the old form fed whatever it was given
       straight to .split, so an `omit` that was a LIST threw a TypeError inside
       compose(), and the page rendered its output block EMPTY on the live site
       (§SCARS 2026-08-11). Callers now pass one line at a time via omitLines();
       this coercion is the second belt, not the fix. */
    return String(t == null ? "" : t).split(/(?:\.\s|\s—\s)/)[0].replace(/[\s.]+$/, "");
  }

  function defOn(id) {
    for (var i = 0; i < TOGGLES.length; i++) if (TOGGLES[i].id === id) return TOGGLES[i].on;
    return false;
  }

  function esc(t) {
    return String(t == null ? "" : t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function setupSteps() {
    var p = PLATFORMS[S.platform] || PLATFORMS.other;
    var d = current();
    var ds = picked();
    var nm = d ? d.name : "document";
    var fam = d ? famOf(d) : FAMILIES.recurring;

    /* THE DESK CHANGES THE CHAT RULE, and getting it wrong is the one thing on
       this list that corrupts a document rather than annoying him. A recurring
       report wants one chat per job so it can report deltas; a record written
       once and read years later must never be written as an update. A desk can
       hold both, so when it does, the step names which are which instead of
       picking one rule and being wrong about half of them. */
    if (ds.length > 1) {
      var delta = ds.filter(function (x) { return deltaOf(x); });
      var alone = ds.filter(function (x) { return !deltaOf(x); });
      var chat;
      if (!alone.length) {
        chat = "Run <b>one chat per job.</b> Starting a new chat mid-job? Paste your last one in first so it keeps the running items.";
      } else if (!delta.length) {
        chat = "Start a <b>new chat for each one.</b> These stand alone — they do not need the history.";
      } else {
        chat = "<b>One chat per job</b> for the ones that build on each other (" +
          esc(delta.map(function (x) { return x.name; }).join(", ")) + "). A <b>new chat each time</b> for " +
          esc(alone.map(function (x) { return x.name; }).join(", ")) +
          " — those get read years later and must never come out written as an update.";
      }
      return [
        "Open <b>" + esc(p.name) + "</b> and paste the block below into " + p.where +
          ". Name it “" + esc(nz(LIB.trade, "Field")) + " write-ups”.",
        chat,
        "<b>Then just dump.</b> Say which one you want in the first line — “daily”, “incident”, whatever you call it — then the mess. Voice-to-text it in the truck, paste your texts, whatever you have.",
        "Read it before you send it. Chase anything marked <code>&lt;MISSING&gt;</code> — that is the point of the marker."
      ];
    }

    var steps = [
      "Open <b>" + p.name + "</b> and paste the block below into " + p.where + ". Name it “" + nm + "”.",
      (d ? deltaOf(d) : fam.delta)
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

  /* SEARCH LIVES IN shared/find.js NOW, and the reason is measured (see that
     file's header). What stood here ANDed every typed token as a substring over
     name + aka + why and rendered the survivors in FILE ORDER. Driven through
     this page in a real browser: 953 queries built from the authors' own strings
     missed 0 times — and 5,384 mechanical perturbations of those same strings
     missed 4,121 times (76.5%). "daily field report template" returned nothing
     on all eight trades. So did one typo, and a plural, 99% of the time.
     The index is built once — LIB does not change after load. */
  var IX = null;

  /* THE POOLED VOCABULARY. Eight of these documents live on all thirteen trades
     and every trade RENAMED them — `delay-notice` goes by seven names across the
     rack — and each trade's author wrote his own `aka`, his record of what people
     actually SAY for it. So the search on any one page knew ONE man's words for a
     document thirteen men named. Measured through this box on the real pages, 733
     unambiguous terms x 13 trades: 1,083 searches returned a DIFFERENT document
     for one the reader's own library was holding, and 512 of those carried no
     hedge at all — "somebody got hurt" handing back the Damage / Pre-Existing
     Condition Note as an exact match, "first aid" handing back the Turnover
     Summary.

     shared/docsindex.js is the union of every name and `aka` anybody wrote,
     GENERATED from these same thirteen libraries and diffed by the deploy. It is
     added ONLY to documents the trade already carries, so this can never put a
     document on a page that did not have it and never changes a block: the man
     gets thirteen authors' words for his own shelf. It degrades to nothing if the
     file is absent, and the deploy asserts the tag on the real page. */
  function poolTerms(d) {
    var P = window.DOCS_POOL, extra = P && P[d.id];
    if (!extra || !extra.length || !window.Find) return [];
    var have = {}, mine = [d.name].concat(d.aka || []), i;
    for (i = 0; i < mine.length; i++) have[window.Find.norm(mine[i])] = 1;
    return extra.filter(function (t) { return !have[window.Find.norm(t)]; });
  }

  /* Copies, never a mutation: library() hands back the live merged rows and
     compose() reads `aka` to build the ROUTER line a man pastes into his AI.
     Widening the SEARCH must not widen what the document tells him it is called. */
  function pooled(lib) {
    return lib.map(function (d) {
      var extra = poolTerms(d);
      if (!extra.length) return d;
      var c = {}, k;
      for (k in d) if (Object.prototype.hasOwnProperty.call(d, k)) c[k] = d[k];
      c.aka = (d.aka || []).concat(extra);
      c.poolOnly = extra;
      return c;
    });
  }

  function findIx() {
    if (!IX) IX = window.Find.index(pooled(library()), [
      { get: function (d) { return d.name; }, w: 10, primary: true },
      { get: function (d) { return d.aka || []; }, w: 6 },
      /* PROSE, NOT A NAME — rule 5. A word that lands only here has not
         identified a document, so the answer goes out labelled "Closest to". */
      { get: function (d) { return d.why || ""; }, w: 2, about: true }
    ]);
    return IX;
  }

  function renderLibrary() {
    var box = el.lib;
    box.innerHTML = "";
    var u = uses();
    var q = S.q.trim();
    /* THE RAW VALUE, NOT THE TRIMMED ONE, and the difference is one character
       that decides a sentence. `norm()` strips trailing separators, so this
       changes NOTHING about what matches — but shared/find.js reads the raw
       query to tell "he is still typing this word" from "he finished it", and
       a trimmed query can never say the second. Trimmed stays the display
       value, because a heading that quotes his trailing space is a typo. */
    var res = window.Find.search(findIx(), S.q);
    var hits = res.hits.slice();

    if (!q || res.mode === "all") {
      /* mode "all" is a query that normalized to nothing ("!!!") — labeling the
         full library "Closest to" would be the exact lie the modes exist to kill. */
      var mine = hits.filter(function (d) { return u[d.id]; })
        .sort(function (a, b) { return (u[b.id] || 0) - (u[a.id] || 0); }).slice(0, 3);
      if (mine.length) {
        box.appendChild(grp("Yours — most used"));
        mine.forEach(function (d) { box.appendChild(row(d)); });
        box.appendChild(grp("Everything else"));
        hits = hits.filter(function (d) { return mine.indexOf(d) === -1; });
      }
    } else if (res.mode !== "exact") {
      /* NEVER SILENTLY PASS OFF AN APPROXIMATE HIT AS AN EXACT ONE. The engine
         reports which it handed back and the label says so out loud. */
      box.appendChild(grp(res.mode === "none" ? "Nothing matched that — closest three"
                                             : "Closest to “" + q + "”"));
    } else if (poolHit(hits[0], q)) {
      /* HE TYPED SOMEBODY ELSE'S WORD FOR HIS OWN DOCUMENT, and the page should
         say so rather than let him think that is what his trade's page calls it.
         The same rule the commons name table already holds one floor down: every
         name carries WHO SAYS IT, so a word that works is never mistaken for the
         word to write down. It is not a hedge — the document IS his and the match
         IS exact — which is why it is a heading and not a "Closest to". */
      box.appendChild(grp("Another trade's name for it"));
    }
    /* WHAT THE ENGINE DELETED, SAID OUT LOUD — and it has to sit ABOVE the rows,
       because a man who reads the answer first has already decided. Rule 1
       drops a token that names nothing in this library; on a document library
       the surviving word is very often the generic half ("note", "letter",
       "record") and the dropped half is what he was actually after — typing
       "Inspection Note" here keeps `note`, hands back a note, and said EXACT.
       This is not a hedge and it may not read as one: the heading above still
       makes whatever claim it is entitled to make, and this only names the
       words that never reached it. */
    var drop = window.Find.dropped(res);
    if (drop) {
      /* class is exactly "none" and the marker is an ATTRIBUTE: every gate this
         page already has finds the leading row by skipping `grp` and `none`, and
         a third class name would have made this note look like a document to all
         of them. */
      var dl = h("li", "none", drop);
      dl.setAttribute("data-drop", "1");
      box.appendChild(dl);
    }
    if (!hits.length) {
      box.appendChild(h("li", "none", "Use “not in the list” below — it still builds you a real one."));
      return;
    }
    hits.forEach(function (d) { box.appendChild(row(d)); });
    if (q && res.mode === "none") {
      box.appendChild(h("li", "none", "Not one of those? Use “not in the list” below — it still builds you a real one."));
    }

    function grp(t) { var li = h("li", "grp", t); return li; }
    /* True only when the WHOLE query is a pooled name — the unambiguous case. A
       partial or fuzzy overlap is not evidence about which vocabulary he used. */
    function poolHit(d, query) {
      if (!d || !d.poolOnly || !window.Find) return false;
      var k = window.Find.norm(query);
      return !!k && d.poolOnly.some(function (t) { return window.Find.norm(t) === k; });
    }
    function row(d) {
      var mine = inDesk(d.id);
      var li = h("li", mine ? "on" : "");
      var b = h("button", null);
      b.type = "button";
      b.appendChild(h("span", "nm", d.name));
      b.appendChild(h("span", "wy", d.why));
      /* IN ADD MODE THE ROW HAS TO SAY WHAT TAPPING IT DOES, because in this
         mode a tap is a toggle and the row already in the setup is the one he is
         most likely to tap by accident. */
      if (S.adding && mine) {
        b.appendChild(h("span", "rt in", d.id === S.doc ? "✓ the one you're tuning"
                                                        : "✓ in this setup — tap to take it out"));
      } else if (S.adding && picked().length >= MAX_DOCS) {
        b.appendChild(h("span", "rt", "setup is full — take one out first"));
        b.disabled = true;
      } else {
        b.appendChild(h("span", "rt", (d.from ? d.from + " → " : "") + (d.to || "")));
      }
      b.addEventListener("click", function () { pick(d.id); });
      li.appendChild(b);
      return li;
    }
  }

  function pick(id) {
    /* IN ADD MODE THE SAME ROW MEANS SOMETHING ELSE. One list, two jobs: tapping
       a row picks the document he is tuning, or adds a second one to the desk.
       The row says which — a ✓ and "in this setup" — because a control that
       looks identical in two modes is how you get a man wondering why his daily
       just became a delay letter. */
    if (S.adding && id !== "__custom") {
      if (id === S.doc) return;                       // the main one; × it from the card
      var at = S.more.indexOf(id);
      if (at !== -1) S.more.splice(at, 1);
      else if (picked().length < MAX_DOCS) { S.more.push(id); bump(id); }
      save();
      renderAll();
      return;
    }
    S.doc = id;
    S.off = {};
    /* Promoting a document that is already an extra would print it twice. */
    var was = S.more.indexOf(id);
    if (was !== -1) S.more.splice(was, 1);
    var d = current();
    if (d && d.to && !S.to) S.to = d.to;
    if (id !== "__custom") bump(id);
    save();
    renderAll();
    if (el.tuneCard) el.tuneCard.scrollIntoView({ block: "start" });
  }

  /* ── THE SAY-LIST, ON THE PAGE ──────────────────────────────────────────
   * The block goes into his AI once. THIS is what he looks at every time, so it
   * is plain text he can read at arm's length on a dirty screen and copy to the
   * three guys who also have to write one. No inputs, no ticks, nothing to
   * operate — the whole shape is "say these, then talk".
   *
   * It sits ABOVE the omitted line on purpose and does not repeat it: the omit
   * box directly below is the last item of this list, wearing the treatment it
   * has always worn. Printing it twice would teach him the list is padding.
   */
  function renderSay(d) {
    var box = h("div", "say");
    var fx = factsOf(d);
    box.appendChild(h("b", null, "Say this when you dump it"));
    /* NO <MISSING> IN THIS SENTENCE. It was written here first, and a foreman
       reading the card cold said the angle brackets read as a broken page, not
       as English — he has never seen the token do its job yet. It earns itself
       later, inside a finished document, where one look teaches it. And the
       screenshot path is not hypothetical: this card gets sent to three leads
       who never opened the page, so its first ten seconds cannot be spent on
       notation. */
    box.appendChild(h("p", "sub", "The block below sets your AI up once. This is the part you actually " +
      "have to do — anything you skip comes back with a blank where the answer should be."));
    /* NUMBERED, NOT BULLETED. Eleven dots is a stack you eyeball; eleven numbers
       tell a man rattling this off in a truck that he is on 6 of 11. plumbing
       carries eleven, electrical fifteen. */
    var ul = h("ol", null);
    fx.forEach(function (f) { ul.appendChild(h("li", null, f)); });
    box.appendChild(ul);
    box.appendChild(h("p", "cue", sayCue(d)));

    /* SAY WHERE THESE CAME FROM ON THE CUSTOM PATH. current() seeds the custom
       pseudo-document's `facts` straight off the FAMILY, so this list is what
       every document of that kind needs — not a claim about HIS. The omission
       tick two controls over already discloses exactly this ("Ticked from what
       the other write-ups of this kind were missing. Yours may be different.")
       and the say-list shipped the same boilerplate with a confident heading and
       no such line. A seeded control that does not say it is a seed reads as a
       verdict we do not have. */
    if (d.id === "__custom") {
      box.appendChild(h("p", "seedwhy", "These are what every " +
        famOf(d).name.replace(/^A /, "").toLowerCase() + " needs. Yours will have more — say those too."));
    }

    /* The copy is the point of the control, not a convenience: a foreman with
       three leads sends them this list, and none of them has to open the page.
       It copies WHAT IS ON SCREEN plus the omitted line, because on paper the
       omitted line is the last thing to say and the box below is only a box. */
    var cp = h("button", "saycopy", "Send this to your guys");
    cp.type = "button";
    cp.addEventListener("click", function () {
      /* NUMBERED HERE TOO, AND THE OMITTED LINES STAY MARKED. The card gives the
         omitted line a red frame and its own heading; a flat dash-list in a text
         message throws both away and buries the highest-value field of the whole
         library among the routine ones. It keeps its heading and it keeps its
         place — last, and numbered on from the facts, because it is not a
         footnote, it is the thing to say. */
      var n = 0;
      var lines = ["Before you write the " + d.name + ", say:"];
      fx.forEach(function (f) { lines.push(++n + ". " + f); });
      var om = omitLines(d);
      if (om.length) {
        lines.push("");
        lines.push(om.length > 1 ? "The ones everybody leaves out — say these too:"
                                 : "The one everybody leaves out — say it too:");
        /* THE DEMAND RIDES INTO THE GROUP CHAT TOO. Three leads get this
           message and never open the page, so a list that names the line and
           drops what satisfies it hands them the exact failure the demand
           exists to close — a fluent sentence, and nothing in it. */
        var cn = needsOf(d);
        om.forEach(function (o, i) {
          var dm = demandOf(cn[i]);
          lines.push(++n + ". " + o + (dm ? "  (say the actual " + dm + " — not a sentence about it)" : ""));
        });
      }
      lines.push("");
      lines.push(sayCueSentence(d));
      var txt = lines.join("\n");
      copyText(txt, cp, "Copied — paste it in the group chat");
    });
    box.appendChild(cp);
    return box;
  }

  function renderPicked() {
    var box = el.picked;
    box.innerHTML = "";
    var d = current();
    if (!d) { box.style.display = "none"; return; }
    box.style.display = "";
    var p = h("div", "picked");
    p.appendChild(h("h3", null, d.name));
    p.appendChild(h("span", "rt", famOf(d).name));
    if (d.why) p.appendChild(h("p", "wy", d.why));
    var chg = h("button", "chg", "Pick a different one");
    chg.type = "button";
    chg.addEventListener("click", function () {
      S.doc = null; S.adding = false; save(); renderAll();
      if (el.libCard) el.libCard.scrollIntoView({ block: "start" });
    });
    p.appendChild(chg);
    box.appendChild(p);

    /* One line stays a paragraph; several become a real list. Handing an ARRAY
       to textContent joined them with commas — "…only an after,what was found
       inside the opening…" — which reads as one run-on sentence and buries the
       second and third lines, the exact opposite of what this block is for. */
    box.appendChild(renderSay(d));

    var omits = omitLines(d);
    var nds = needsOf(d);
    var o = h("div", "omit");
    o.appendChild(h("b", null, omits.length > 1 ? "The lines everyone leaves out"
                                                : "The line everyone leaves out"));
    /* THE DEMAND, FOR THE MAN, BEFORE HE OPENS HIS MOUTH (2026-08-28). The line
       itself has been on this card since the say-list shipped; what would
       SATISFY it never has, on any of the 231 library documents — only on the
       custom path nobody reaches. A foreman's own words for why the line alone
       is not enough: he knows he handed it to Denise at 2:40, so he reads her
       name into a sentence that does not contain it, every time. Naming the
       artefact is the only thing that survives that. Same source as the block —
       demandOf() — so the two readers can never be told different things. */
    function demandRow(ids) {
      var dm = demandOf(ids);
      var r = h("p", "needs");
      if (dm) {
        /* THE STEM TAKES THE ARTICLE, BECAUSE THE DEMANDS CARRY ONE. First draft
           read "Say the actual" and rendered "Say the actual a date or a clock
           time, a name and …" on every card in the program — broken English on
           the one line the whole library is built around, caught by looking at
           the real page rather than by any assertion, because a gate comparing
           the card against the block passes a stem that is wrong on BOTH.
           "It has to carry" is also the block's own verb, so the two readers are
           told the same thing in the same words. */
        r.appendChild(h("span", "nk", "It has to carry"));
        r.appendChild(document.createTextNode(" " + dm + " — not a sentence about it."));
      } else {
        r.appendChild(h("span", "nk nk-open", "In your own words"));
        r.appendChild(document.createTextNode(" — no one fact settles this one."));
      }
      return r;
    }
    if (omits.length > 1) {
      var oul = h("ul", null);
      omits.forEach(function (t, i) {
        var li = h("li", null, t);
        li.appendChild(demandRow(nds[i]));
        oul.appendChild(li);
      });
      o.appendChild(oul);
    } else if (omits.length) {
      o.appendChild(h("p", null, omits[0]));
      o.appendChild(demandRow(nds[0]));
    } else {
      /* `omits[0] || ""` painted an EMPTY red box — a warning frame with nothing
         in it, which reads as a rendering failure. Unreachable while every
         library document carried a line; the custom path can now be ticked down
         to none, so it says the true thing instead, and matches word for word
         what compose() puts in the block on the same state. */
      o.appendChild(h("p", null, "Nothing ticked. The block will still ask your AI for the line " +
        "everyone leaves out — but naming it yourself is what makes it come back every time."));
    }
    box.appendChild(o);
    box.appendChild(renderDesk(d));
  }

  /* ── THE DESK, ON THE PAGE ──────────────────────────────────────────────
   * Nobody keeps three Custom GPTs. The whole point of this control is that the
   * documents a man writes four times a year ride into the same setup as the one
   * he writes every day, so they stop being the ones he never gets to.
   */
  function renderDesk(primary) {
    var box = h("div", "desk");
    var extras = picked().slice(1);
    var full = picked().length >= MAX_DOCS;

    if (extras.length) {
      box.appendChild(h("h4", null, "Also in this setup"));
      var ul = h("ul", "deskl");
      extras.forEach(function (d) {
        var li = h("li");
        var tx = h("div", "tx");
        tx.appendChild(h("span", "nm", d.name));
        var oms = omitLines(d);
        tx.appendChild(h("span", "wy", oms.length
          ? "Won't drop: " + shortOmit(oms[0])
          : (d.why || "")));
        li.appendChild(tx);
        var x = h("button", "x", "×");
        x.type = "button";
        x.setAttribute("aria-label", "Take " + d.name + " out of this setup");
        x.addEventListener("click", function () {
          var at = S.more.indexOf(d.id);
          if (at !== -1) S.more.splice(at, 1);
          save(); renderAll();
        });
        li.appendChild(x);
        ul.appendChild(li);
      });
      box.appendChild(ul);
    }

    var add = h("button", "addrow" + (S.adding ? " on" : ""),
      S.adding ? "← Done adding" : (extras.length ? "+ Add another one" : "+ Also set up another one you write"));
    add.type = "button";
    if (full && !S.adding) { add.disabled = true; add.textContent = "Six is the most one setup should carry"; }
    add.addEventListener("click", function () {
      S.adding = !S.adding;
      S.q = "";
      renderAll();
      var t = S.adding ? el.libCard : el.outCard;
      if (t) t.scrollIntoView({ block: "start" });
    });
    box.appendChild(add);

    /* SAY WHAT THE TICK LIST APPLIES TO. It applies to the document he is
       looking at, and the others arrive with their full spine — which is the
       right default for a document he writes four times a year, but only if the
       page says so instead of letting him find out in the block. */
    box.appendChild(h("p", "seedwhy", extras.length
      /* SAY WHOSE LIST IT IS, AND HOW TO GET ANOTHER ONE. The say-list (2026-08-25)
         is the second thing on this page that belongs to the PRIMARY document
         only, and a man with six in his desk has no reason to guess that picking
         a different one is how he sees what to say for it. */
      ? "One block covers all " + picked().length + ". Your AI works out which one you want from what you " +
        "say at the top of your dump. The say-list above and the tick list below are " + primary.name +
        "'s — the others come with their full spine. Pick a different one to see what to say for it."
      : "Write more than one? Put them in the same block — you paste it in once and your AI covers all of them."));
    return box;
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
    var nOmit = omitLines(d).length;
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
      tx.appendChild(h("span", "h", lockedHeading(s.h, nOmit)));
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
    /* Short on purpose. The long version ("paste it in once, use it daily")
       wrapped to four lines in the fixed bar on a phone and squeezed the two
       buttons beside it — the bar is the action surface, not a place for copy. */
    var words = txt ? txt.split(/\s+/).length : 0;
    var n = picked().length;
    el.count.textContent = words ? (words + " words · " + (n > 1 ? n + " documents" : "paste once")) : "";

    /* SAY THE NUMBER, NEVER SOMEBODY ELSE'S LIMIT. Instruction-length caps are a
       third-party product detail that changes and that we cannot verify, and
       §SAFETY says we do not ship authoritative data we do not have. So the page
       states the one number it actually knows — how long the block is — names
       the failure, and gives the fix. */
    if (el.cap) {
      if (n > 1) {
        el.cap.style.display = "";
        el.cap.textContent = txt.length.toLocaleString() + " characters, covering " + n +
          " documents. Some AIs cap how long instructions can be — if yours cuts it off, " +
          "take one out here and give that one a setup of its own.";
      } else {
        el.cap.style.display = "none";
        el.cap.textContent = "";
      }
    }
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
    /* `docname` is a HOOK, not a style. The tuner also renders text inputs, so
       "the first text input in #app" is the custom name field only when nothing
       is picked — which is exactly the state a gate arrives in LAST, after it
       has exercised every document in the library. */
    i.type = "text"; i.className = "docname";
    i.value = S.customName; i.placeholder = "e.g. Pre-pour sign-off note";
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

    /* THE OMITTED LINE, PICKED INSTEAD OF SHRUGGED. Every library document
       arrives with a hand-written one; this path had a single generic sentence
       for all of them. Ticks, not a text box — §THE GATE, and `S.extra` is
       already the place for a sentence only he could write. */
    var f3 = h("div", "f span2");
    var lab3 = h("label", null, "What does this one usually leave out?");
    f3.appendChild(lab3);
    /* `omitpick` is a HOOK, not a style: the tuner's house-rule toggles are also
       a ul.ticks, so a gate that wants THESE ticks would otherwise have to match
       their label text, and a check that breaks when copy is edited is a check
       nobody keeps. */
    var ul3 = h("ul", "ticks omitpick");
    var fam = FAMILIES[S.customFamily] ? S.customFamily : "recurring";
    OMIT_CLASSES.forEach(function (c) {
      var li = h("li");
      var lb = h("label");
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = comitOn(c.id, fam);
      cb.addEventListener("change", function () {
        S.comit[c.id] = cb.checked; save(); renderPicked(); renderOut();
      });
      lb.appendChild(cb);
      lb.appendChild(h("span", "nm", c.label));
      lb.appendChild(h("span", "sb", c.artefact));
      li.appendChild(lb);
      ul3.appendChild(li);
    });
    f3.appendChild(ul3);
    /* SAY WHERE THE TICKS CAME FROM. They are seeded from what the write-ups of
       THIS FAMILY on disk were actually missing — a prior, not a fact about his
       document, and a page that presents a prior as a fact is lying quietly. */
    f3.appendChild(h("p", "seedwhy",
      "Ticked from what the other write-ups of this kind were missing. Yours may be different."));
    g.appendChild(f3);
    box.appendChild(g);
  }

  function renderAll() {
    renderLibrary();
    renderCustom();
    renderPicked();
    renderTune();
    if (current()) renderOut();
    el.libCard.style.display = (S.doc && S.doc !== "__custom" && !S.adding) ? "none" : "";
    /* The custom path builds the ONE document that is not in the library, and it
       owns the primary slot. Offering it while adding a second would promise a
       second custom document the state cannot hold, so it is not offered. */
    if (el.custom) el.custom.style.display = S.adding ? "none" : "";
    if (el.libHead) {
      el.libHead.textContent = S.adding ? "+ What else do you write?"
                                        : "1 · What are you stuck writing?";
    }
    if (el.libDone) {
      el.libDone.innerHTML = "";
      el.libDone.style.display = S.adding ? "" : "none";
      if (S.adding) {
        var n = picked().length;
        el.libDone.appendChild(h("span", null, n + (n === 1 ? " document" : " documents") + " in this setup"));
        var db = h("button", null, "Done");
        db.type = "button";
        db.addEventListener("click", function () {
          S.adding = false; renderAll();
          if (el.outCard) el.outCard.scrollIntoView({ block: "start" });
        });
        el.libDone.appendChild(db);
      }
    }
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
    var n = picked().length;
    var title = n > 1 ? nz(LIB.trade, "FIELD").toUpperCase() + " WRITE-UPS — " + n + " DOCUMENTS"
                      : (d ? d.name.toUpperCase() : "WRITE-UP");
    return title + " — SETUP FOR " + p.name.toUpperCase() + "\n\n" +
      setupSteps().map(function (s, i) { return (i + 1) + ". " + s.replace(/<[^>]+>/g, ""); }).join("\n") +
      "\n\n--- PASTE EVERYTHING BELOW THIS LINE INTO " + p.name.toUpperCase() + " ---\n\n" + compose();
  }

  /* ── mount ─────────────────────────────────────────────────────────────── */
  function mount() {
    var app = document.getElementById("app");
    if (!app) return;
    load();

    el.libCard = h("div", "card");
    el.libHead = h("h2", "blk", "1 · What are you stuck writing?");
    el.libCard.appendChild(el.libHead);
    /* THE WAY OUT OF ADD MODE HAS TO BE WHERE HE IS. The add control lives on
       the picked card, which sits BELOW the library — so entering add mode put
       the only "done" button under fifteen documents he would have to scroll
       past. Caught by looking at the real page at 390px, not by any gate: every
       control was present, reachable and 44px, and the flow was still wrong. */
    el.libDone = h("div", "libdone");
    el.libCard.appendChild(el.libDone);
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
    el.cap = h("p", "cap");
    el.cap.style.display = "none";
    el.outCard.appendChild(el.cap);
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

  /* THE VERIFY SURFACE. tools/toolkit-gates/docspec-config.mjs reads the FAMILIES
     and the merged LIBRARY out of the shipped engine rather than keeping its own
     copy of either — a gate that hardcodes the thing it is checking drifts from
     it and then reports green on the day it matters.

     IT IS EXPORTED BEFORE THE MOUNT, AND THE MOUNT IS GUARDED, so the merge rule
     can be read in plain node with a synthetic window and NO DOM. That is not
     tidiness: shared/docsindex.js is a GENERATED artifact derived from this very
     merge, and the only way its correctness claim cannot rot is for the deploy to
     REGENERATE it from the staged files and refuse a diff. A deploy that needs a
     browser to do that would not do it, and a generator that re-implemented the
     merge would be the second copy of the rule this file already refuses to keep. */
  window.DocSpec = { families: FAMILIES, shared: SHARED_DOCS, library: library,
                     omitLines: omitLines, famOf: famOf, deltaOf: deltaOf, compose: compose,
                     /* The artefact half, exported so tools/toolkit-gates/docspec-needs.mjs
                        reads the SHIPPED vocabulary and the SHIPPED resolver rather than
                        keeping a second copy of either beside it. */
                     artefacts: ARTEFACTS, needsOf: needsOf, demandOf: demandOf,
                     omitClasses: OMIT_CLASSES, famOmit: FAM_OMIT, shortOmit: shortOmit,
                     picked: picked, maxDocs: MAX_DOCS, pooled: pooled, poolTerms: poolTerms,
                     factsOf: factsOf, sayCue: sayCue, sayCueSentence: sayCueSentence,
                     /* The REAL search index, so a gate can ask the engine what it did
                        instead of rebuilding the field spec beside it and drifting. */
                     findIx: findIx };

  if (typeof document === "undefined") return;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
