/* FRAMING & DRYWALL FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about framing and drywall work and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. This trade's exposure is the worst on
 *     the site — every hand alive says one company's name instead of the word
 *     "board". It is board. It is rock. It is mud, and bead, and a lid.
 *   · NOTHING IS RATED, SIZED, THRESHOLDED OR JUDGED. No hour rating, no listed
 *     assembly, no STC, no limiting height, no gauge chart, no screw spacing, no
 *     nailing pattern, no finish-level definition — not as a value, not as a
 *     hint, not in a placeholder. The hand states what he built; nobody here
 *     grades it against a standard.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 */
window.TRADE_DOCS = {
  "trade": "commercial framing and drywall",

  "docs": [
    {
      "id": "backing-closeout",
      "name": "Backing Closeout (what went in, before anybody asks)",
      "aka": [
        "backing letter",
        "blocking record",
        "what's in the wall letter",
        "backing closeout",
        "we put the backing in",
        "backing turnover"
      ],
      "family": "verification",
      "from": "the framing/drywall foreman who closed the walls",
      "to": "our PM, the GC super, and the trade that asked — for the closeout file",
      "why": "Six trades ask this crew for backing and none of them keep a record of what they asked for. Months later the argument is one word against another, and the only thing that settles it is a dated list written while the wall was still open.",
      "note": "a record of what was built, not an approval of anything — the heights and sizes are the ones we were given",
      "sections": [
        { "h": "AREA AND WHAT IT COVERS", "r": "Site and building in the first line with the date, then exactly which floors, areas, rooms or column lines this letter covers and which it does not. A closeout letter with a fuzzy boundary gets read as covering the whole job." },
        { "h": "WHAT WE WERE WORKING OFF", "r": "The backing sheet and its revision if there was one, and plainly say so if there wasn't — 'off their texts, emails and marks on the wall' is an honest answer and it is the one that matters later. List who sent asks and how they arrived." },
        { "h": "WHAT WENT IN", "r": "By room or wall: what it is for, what was installed, how high off the floor bottom to top, how wide, and who asked for it. Every dimension exactly as the user states it. Never state what a height should have been and never convert or round a number the user gave." },
        { "h": "WHAT WE WERE NEVER GIVEN", "r": "The asks that arrived with no size, no height or no location, who was asked for it, when, and how many times. This is the section that decides who pays for a cut-in, so it names dates and it names companies — never a person's character." },
        { "h": "WHAT IS NOT IN THESE WALLS", "r": "Say it in one plain sentence: anything not on this list is not in that wall. Then name any area deliberately left open and who told us to leave it." },
        { "h": "WHAT WE NEED BACK", "r": "One named person, one action, one date. Usually: walk it before we close, or confirm this list against yours." }
      ],
      "omit": [
        "the day each wall actually got covered — the date is the whole evidentiary point and it is the first thing left out",
        "which asks arrived with no height on them, and how many times we chased the number",
        "the boundary sentence — a list with no 'anything not on here isn't in there' reads as a partial record and gets used as one"
      ]
    },
    {
      "id": "damage-reply",
      "name": "It Wasn't Us (a punch item for damage somebody else opened)",
      "aka": [
        "damage response",
        "not our damage",
        "punch list reply",
        "somebody cut my wall",
        "cut and patch response",
        "who opened this"
      ],
      "family": "incident",
      "from": "the framing/drywall foreman",
      "to": "the GC super, cc our PM",
      "why": "This trade closes the walls, so every hole anybody cuts afterwards lands on our punch list by default. The reply has to be written the day it is found, before the surface is patched and the evidence is gone.",
      "note": "no money words, ever — this letter records a condition, it does not price it or claim it",
      "sections": [
        { "h": "WHERE AND WHEN", "r": "Site, building, floor, room or column line, and the date the condition was found — plus the date that area was handed over or last walked clean, if it is known. The gap between those two dates is the whole argument." },
        { "h": "WHAT THE CONDITION IS", "r": "Plainly: what was cut, opened, broken or dirtied, roughly how big, in what surface, and what stage that surface was at — bare board, taped, sanded, painted. Never guess at a cause and never name a man." },
        { "h": "WHAT IS IN IT OR AROUND IT", "r": "What was found in the opening — pipe, cable, duct, a device, nothing. This is how the condition gets attributed without accusing anybody: describe what is in the hole and let the reader draw the line." },
        { "h": "PHOTOS", "r": "State that photos are attached and what each one shows, with the room and a fixed reference in frame. Say if any surface was patched before the photo was taken." },
        { "h": "WHAT HAPPENS NEXT AND WHAT IT NEEDS", "r": "What has to happen for the surface to be right again, in scope terms only — cut back, back it, patch, tape, sand, texture, prime — and who needs to authorise it. No hours, no rates, no totals, no backcharge language. If it is going to be an extra, say only that a tag will follow." },
        { "h": "THE ASK", "r": "One named person, one decision, one date. Usually: tell us whose it is and whether to proceed." }
      ],
      "omit": [
        "the date that area was last walked clean — without it there is no before, only an after",
        "what was found inside the opening, which is the only attribution the letter can honestly make",
        "the sentence saying this is not a price and not a claim — its absence turns a condition report into a demand"
      ]
    },
    {
      "id": "held-up",
      "name": "We're Held Up (and the wall can't close)",
      "aka": [
        "held up notice",
        "we can't close",
        "waiting on other trades",
        "impact notice",
        "can't rock it",
        "out of sequence"
      ],
      "family": "notice",
      "from": "the framing/drywall foreman or GF",
      "to": "the GC super and our PM",
      "why": "Closing a wall is the one irreversible act on an interior, so this crew is held up more often than anybody and looks slower than anybody. The notice is what converts 'the drywall guys are behind' into 'these four walls are open and here is who owes what'.",
      "note": "a notice of a condition and what we did about it — not a claim, not a schedule submission, no numbers on it",
      "sections": [
        { "h": "WHAT IS OPEN AND WHERE", "r": "Site and date first. Then exactly which walls, lids or areas cannot close, by room or column line, and which side. Precision here is the difference between a notice and a complaint." },
        { "h": "WHAT IT IS WAITING ON", "r": "For each area: what has to be in before it can close and which trade owes it. State it as a condition, never as a character judgement, and name companies rather than men." },
        { "h": "WHEN WE ASKED AND HOW", "r": "The dates we raised it, how — walk, text, email, the request list we sent — and what we were told. Nothing here is an accusation; it is a timeline." },
        { "h": "WHAT WE DID INSTEAD", "r": "Where the crew went, what we closed that we could, and what we resequenced to keep working. This is the section that separates a notice from an excuse, and it is the one most often left out." },
        { "h": "WHAT WE NEED DECIDED", "r": "One named person, one decision, one date. Usually: get the trade in by a day, or tell us to close it and accept the cut-ins. Say plainly that closing it early means a cut-in and a patch later — with no price attached to the sentence." }
      ],
      "omit": [
        "what the crew did instead — without it the letter reads as a crew standing around, which is the opposite of its purpose",
        "the date each area was first raised, which is the only thing that makes this a notice rather than a grievance",
        "the specific decision being asked for, so it gets filed instead of answered"
      ]
    },
    {
      "id": "wont-fit",
      "name": "Won't Fit (the wall the drawings can't build)",
      "aka": [
        "won't fit",
        "dimension conflict",
        "it doesn't work",
        "layout conflict",
        "the wall doesn't fit",
        "clash at layout"
      ],
      "family": "notice",
      "from": "the layout man or foreman, at the line",
      "to": "the GC super — who turns it into the RFI in their system, where the number lives",
      "why": "The layout crew is the first trade to find out the drawings do not close, and it is found standing on the floor with a crew waiting. Written in five minutes it is a question; written next week it is a change order.",
      "note": "this is the note the GC turns into an RFI — we never number it and never call it one",
      "sections": [
        { "h": "WHERE", "r": "Site, floor, room or column line, and the date and time it was found. Time matters here: a crew is standing." },
        { "h": "WHAT THE DRAWINGS SHOW", "r": "Which sheets and revisions, and what each one says about this location. If two sheets disagree, say which two and quote both — the disagreement IS the question." },
        { "h": "WHAT IS ACTUALLY THERE", "r": "The field condition as measured or observed, in the user's own numbers. Never a number this document generated, and never a tolerance or a code reference." },
        { "h": "WHY IT DOESN'T CLOSE", "r": "One plain sentence a super can read on a phone. No theory about who drew it wrong." },
        { "h": "WHAT WE'D DO IF NOBODY TELLS US", "r": "The option that keeps the crew moving, stated as a proposal and clearly marked as needing a yes. Offering one is how a same-day answer happens; presenting it as a decision already made is how it becomes our liability." },
        { "h": "WHEN WE NEED IT", "r": "One named person, one answer, one time — usually today, because the crew is standing." }
      ],
      "omit": [
        "the sheet numbers and revisions, without which the question cannot be answered by anyone",
        "the field measurement, so the answer comes back based on the drawing that is already wrong",
        "the time of day and what the crew is doing meanwhile, which is what makes it urgent instead of routine"
      ]
    },
    {
      "id": "precon-scope",
      "name": "What We Carry (and the gaps we found in the documents)",
      "aka": [
        "scope letter",
        "pre-con letter",
        "clarifications",
        "inclusions and exclusions",
        "what we carry",
        "scope gaps"
      ],
      "family": "notice",
      "from": "our PM or GF, with the field foreman's input",
      "to": "the GC PM, cc the super who will run the job",
      "why": "Almost every extra this trade writes for a year traces back to something nobody clarified before the first wall went up — who owns the caulk at the deck, who backs the casework, who patches after the other trades. Writing it down once at the start is cheaper than tagging it twelve times.",
      "note": "scope language only — the bid number and any pricing belong to the office, and never appear in this letter",
      "sections": [
        { "h": "WHAT THIS COVERS", "r": "Site, the documents and revisions this letter is written against, and the date. A scope letter against an unnamed document set clarifies nothing." },
        { "h": "WHAT WE CARRY", "r": "The work we are performing, by area and by system, in plain scope terms. No quantities we did not take off and no prices." },
        { "h": "WHAT WE DON'T", "r": "The specific items commonly assumed to be ours and are not, each in one line. Be concrete — this section is only useful when it names the actual arguments." },
        { "h": "GAPS WE FOUND IN THE DOCUMENTS", "r": "Places where the set is silent, contradicts itself, or assigns work to nobody. State the sheets, state what is missing, and ask who owns it. Never assert what the code or the standard requires." },
        { "h": "WHAT WE NEED TO AGREE BEFORE WE START", "r": "The handful of decisions that will otherwise become extras — cut and patch after others, backing with no size given, temp heat before finishing, protection of finished surfaces, scrap and access. One named person and one date for the lot." }
      ],
      "omit": [
        "the revision numbers of the documents the letter is written against, which is what makes an exclusion enforceable",
        "the gaps section entirely — most scope letters list inclusions and exclusions and never say what the set failed to assign",
        "a date by which the open items need answering, so the letter is read once and never actioned"
      ]
    }
  ],

  "overrides": {
    "daily-report": {
      "name": "The Daily (what we closed, what stopped us)",
      "why": "This is YOUR account, not the GC's numbered log — and for this trade it is the only dated record of which walls closed on which day, which is the fact every later argument turns on.",
      "sections": [
        { "h": "AREAS AND CREW", "r": "Site and building first, then the date of the shift. Then where the crew actually worked — floor, area, column lines, room numbers — and who was where, in short prose by area (\"me and four framers on 3 west all day, two of them pulled to the shaft in the afternoon\"). Men and hours stay sentences by area, never a headcount table: the table is the GC's, the men and hours are ours and the office costs the job off this." },
        { "h": "WHAT WENT UP, WHAT CLOSED", "r": "What physically got laid out, stood, backed, hung, taped or closed today, by area, with the user's own quantities. NAME EVERY WALL OR LID THAT GOT COVERED TODAY AND WHICH SIDE — that is the single most valuable line this trade writes, and it is the one nobody writes. Never \"continued framing\" with no location on it, and never a quantity we invented." },
        { "h": "WHAT STOPPED US OR SLOWED US", "r": "The specific condition, the area, and how long we sat — waiting on rough, waiting on an answer, a floor full of somebody else's material, no heat. State the condition, never a man's character. This section RECORDS the hold; the held-up notice is the first written notice of it. Don't write the same paragraph into both. If nothing stopped you, say so plainly — a blank here reads as \"nothing happened\" three months later." },
        { "h": "INSPECTIONS, SIGN-OFFS AND COVER", "r": "What was walked, inspected or signed off today and by whom — frame inspection, pre-cover, above-ceiling. Times and names exactly as recorded. Never write our own pass or fail and never state what an inspection requires." },
        { "h": "MATERIAL, LOADS AND EQUIPMENT", "r": "What landed and where it got dropped, what's short and holding you up, what's on rent and sitting. Short prose — this is not the packing list." },
        { "h": "TOMORROW", "r": "Where the crew goes, what has to be ready for them, and who owes it. One named person per item." }
      ]
    }
  },

  "drop": [],

  /* What this trade dictates that a phone reliably gets wrong. Left side is what
     the phone hears, right side is what he said. No brand names on either side. */
  "vocab": [
    "shear rock -> shaft liner",
    "shaft wall liner -> shaftliner",
    "see channel -> cee channel",
    "hat channel -> hat channel",
    "resilient channel -> resilient channel",
    "cold rolled -> cold-rolled channel",
    "deflection track -> deflection track",
    "slip clip -> slip clip",
    "bull nose -> bullnose",
    "jay bead -> J-bead",
    "el bead -> L-bead",
    "tear away bead -> tear-away bead",
    "control joint -> control joint",
    "hot mud -> hot mud",
    "all purpose -> all-purpose mud",
    "top and bottom track -> top and bottom track",
    "kicker -> kicker",
    "head of wall -> head of wall",
    "saphing -> safing",
    "on center -> on center",
    "sixteen oh see -> 16 on center",
    "twenty four oh see -> 24 on center",
    "three five eighths -> 3-5/8",
    "five eighths -> 5/8",
    "ninety two five eighths -> 92-5/8",
    "el vee el -> LVL",
    "eff arr tee ply -> fire-retardant treated plywood",
    "hollow metal frame -> HM frame",
    "kay dee frame -> KD frame",
    "throat -> throat",
    "handing -> handing",
    "cut in -> cut-in",
    "furr it out -> fur it out",
    "furdown -> furdown",
    "soffit -> soffit",
    "bulkhead -> bulkhead",
    "hard lid -> hard lid",
    "skim coat -> skim coat",
    "point up -> point up",
    "level four -> L4 finish",
    "level five -> L5 finish"
  ],

  "reminders": [
    "When backing or blocking is mentioned -> remind them to say WHO ASKED for it, HOW HIGH off the floor bottom to top, and WHAT DAY the wall got covered. Those three facts are the entire value of a backing record and all three are routinely left out. Never suggest a height.",
    "When closing a wall, rocking, or covering comes up -> remind them to name the wall or lid and WHICH SIDE, and the date. 'We rocked 3 west' is not a record; '3 west, corridor side, both sides on 314-318, Thursday' is.",
    "When damage to finished work comes up -> remind them to photograph it before anything is patched, with the room number and a fixed reference in frame, and to state the date that area was last walked clean. Without the earlier date there is no before.",
    "When another trade is described as being in the way or late -> remind them to write the CONDITION and the AREA and never the man. A sentence about a person gets forwarded; a sentence about an open wall gets answered.",
    "When a dimension conflict or a wall that won't fit comes up -> remind them to quote the sheet numbers AND revisions of every drawing involved, and to say what time it was found and what the crew is doing meanwhile. That is what gets a same-day answer instead of an RFI number.",
    "When a finish level is mentioned -> it is fine to record which level was specified or agreed. Never state what a level requires, never grade the work against it, and never reproduce anybody's published definition.",
    "When hours, men or quantities come up -> counts only. No rates, no totals, no square footage the document worked out. The office owns the number.",
    "When a held wall is described -> remind them to name who told them to hold it and the day they were told. A verbal hold with no name on it becomes this crew's production problem three weeks later."
  ]
};
