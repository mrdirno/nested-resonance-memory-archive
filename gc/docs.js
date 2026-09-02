/* GC & SITE SUPER TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about running the site and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS RATED, SIZED, THRESHOLDED OR JUDGED. No code reference, no
 *     acceptance criterion, no "should be" — not as a value, not as a hint, not
 *     in a placeholder. The tradesman states the reading; nobody here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work"). DECLARED,
 *            never derived from the toolkit name — that produced "a AV outfit" and
 *            broke outright on the one trade whose name does not end "Field Toolkit".
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 */
window.TRADE_DOCS = {
  "trade": "general contracting",
  "docs": [
    {
      "id": "rfi-question",
      "name": "The RFI Question",
      "aka": [
        "RFI",
        "request for information",
        "field question",
        "the question",
        "RFI body",
        "RFI write-up",
        "ask the architect"
      ],
      "family": "notice",
      "from": "the PE or super on the job",
      "to": "the architect and the EOR",
      "why": "A clear question with a proposal behind it comes back in days. A bare question sits three weeks and takes the schedule with it.",
      "note": "the body only — the number, the log and the ball-in-court belong to whatever system the job runs on",
      "sections": [
        {
          "h": "SUBJECT — JOB, AREA, ONE QUESTION",
          "r": "Job name and number, the date, and a subject line somebody finds six months later: area, system, conflict, eight words. One question per RFI — two questions in one body comes back half answered. We never invent an RFI number and we never call this the RFI itself."
        },
        {
          "h": "WHERE — SHEET, DETAIL, SPEC, LOCATION",
          "r": "Sheet number AND its revision or bulletin, the detail callout, the spec section, and the physical place by grid/level/room. Both the paper reference and the spot a man can stand on. A missing revision prints <MISSING>."
        },
        {
          "h": "WHAT WE FOUND IN THE FIELD",
          "r": "The condition as it is now, in plain words, with the dimensions HE measured. What is already installed and who installed it. Facts only — no opinion on whose fault it is."
        },
        {
          "h": "WHERE THE DRAWINGS AND THE FIELD DISAGREE",
          "r": "What the drawings and the spec call for at this location, and where it doesn't match what is there: the dimension doesn't close, two sheets disagree, there's no detail at this condition, it won't fit above the ceiling. Never a code interpretation and never a design we invented."
        },
        {
          "h": "WHAT IS STOPPED WHILE WE WAIT",
          "r": "The activity that can't proceed, the crew standing or about to be, the material that can't be released, the milestone behind it. No dollars — time and cost live in the extra work write-up, not in the question."
        },
        {
          "h": "ANSWER NEEDED BY — AND THE ACTIVITY BEHIND THE DATE",
          "r": "A date tied to a real activity, said out loud: by the 14th, because steel releases the 15th. A date with no activity behind it reads as the field being impatient."
        }
      ],
      "omit": "What you would do if it were up to you. A question with nothing proposed behind it hands the architect something he can answer with another question, and the pair of them eat three weeks. Write the resolution you propose — offered for him to accept or reject, never as a decision already made — and it comes back in days.",
      "needs": ["none"],
      "halt": "The notes are really a direction he was already given verbally, or he already built it and wants the RFI to cover him after the fact. Stop — that is a change write-up or a directed-work record, and dressing it up as a question is exactly what gets it denied.",
      "facts": [
        "sheet number AND its revision or bulletin, plus the spec section",
        "the location by grid / level / room number",
        "the dimension or condition he actually measured",
        "who installed what is already in place",
        "the activity that's stopped and the crew affected",
        "the date he needs it back and the activity that sets that date"
      ],
      "secondary": [
        "the chase note on an RFI that has gone quiet",
        "the field-condition note to the PM before it becomes an RFI",
        "the one-line item for the coordination notes"
      ]
    },
    {
      "id": "manpower-letter",
      "name": "The Manpower Letter",
      "aka": [
        "manpower letter",
        "failure to perform",
        "notice to comply",
        "cure notice",
        "non-performance letter",
        "get your men out",
        "short of men",
        "back-charge warning"
      ],
      "family": "notice",
      "from": "the super or PM on the job",
      "to": "the sub's PM and his owner, by name",
      "why": "The letter with a paper trail behind it puts men on the job. The one that arrives cold gets you a lawyer.",
      "sections": [
        {
          "h": "JOB, SUB, SCOPE, DATE",
          "r": "Job name and number, the subcontractor, their scope, the date, and in one line what is not happening. Addressed to a person at that company by name — never to whom it may concern."
        },
        {
          "h": "WHAT WAS AGREED",
          "r": "The dates off the schedule they were given and accepted, the manpower they committed and where they committed it — the meeting, the look-ahead, the email, each with its date. Their subcontract owns the remedies and the notice period; he supplies the article and we never cite one."
        },
        {
          "h": "WHAT IS ACTUALLY HAPPENING",
          "r": "Head counts HE counted, each with the date and the time he counted them, the days with nobody at all, and the areas untouched. Observed counts only — never a number a foreman gave him on the phone."
        },
        {
          "h": "WHAT IT IS HOLDING UP",
          "r": "The trades stacked behind him, the areas that can't close, the inspection that can't be called, the milestone. Name the companies standing."
        },
        {
          "h": "WHAT WE NEED, AND BY WHEN",
          "r": "A count of men, in a named area, by a date and a time. Not more manpower."
        },
        {
          "h": "IF IT DOES NOT HAPPEN",
          "r": "What the company does next, in his own subcontract's words — supplement the crew, engage others, back-charge the cost. Only the remedy that subcontract actually gives him, and he supplies it. No dollars, no threats, no adjectives."
        }
      ],
      "omit": "Every time you already asked, with its date and who you spoke to — the coordination meeting on the 3rd, the text on the 9th, the call on the 11th. A first-and-only letter reads like an ambush and the answer is always that nobody ever told them, which works, because there is nothing in the file behind it. That list is the entire reason the letter has teeth the day you supplement him.",
      "needs": ["when", "who"],
      "halt": "He wants the letter to terminate the sub, or to name a back-charge amount. Stop — termination and the number belong to the office and counsel, and a super's letter that names either one gets his own company sued instead of the sub.",
      "facts": [
        "the sub's company, and the person's name it is addressed to",
        "the schedule dates they were given and accepted",
        "head counts he observed, with the date and time counted",
        "every time he asked before, with the date and who he spoke to",
        "the trades and areas being held up",
        "the count of men, the area, and the date and time being demanded",
        "the remedy his subcontract actually gives him"
      ],
      "secondary": [
        "the back-charge transmittal once the work is supplemented",
        "two weeks of daily entries that feed this letter",
        "the escalation to the sub's owner when the PM stops answering"
      ]
    },
    {
      "id": "unforeseen-condition",
      "name": "Unforeseen Condition Notice",
      "aka": [
        "differing site condition",
        "DSC",
        "concealed condition",
        "we hit something",
        "unmarked utility",
        "dig-in",
        "found in the wall",
        "unforeseen"
      ],
      "family": "notice",
      "from": "the super on the job",
      "to": "the CM and the design team",
      "why": "Written the day you find it with the hole still open, it is a change. Written next week with it backfilled, it is yours.",
      "note": "narrative only — no day counts, no dollars, and no call on what it means under the contract",
      "sections": [
        {
          "h": "JOB, WHAT WE HIT, WHERE AND WHEN",
          "r": "Job name and number, what was found, the exact location by grid or station and the depth, and the date and clock time it was uncovered. The time matters as much as the day."
        },
        {
          "h": "WORK STOPPED — WHAT AND WHEN",
          "r": "What was stopped and at what time, and confirmation the condition is left exposed and undisturbed until somebody comes out. If it could NOT be left open — safety, traffic, water — say why, and say what was documented before it was covered."
        },
        {
          "h": "WHAT IT IS, AS FOUND",
          "r": "Material, size, condition, depth, live or abandoned as far as anybody can tell, and who has been asked to identify it — the utility, the owner's facilities man, a locate service. What HE observed and what HE measured. A guess never gets printed as a fact."
        },
        {
          "h": "WHO HAS BEEN CALLED",
          "r": "Everybody called, with the clock time: owner's rep, engineer, the utility or its emergency line, the locate service, safety."
        },
        {
          "h": "WHAT IS STOPPED AND WHAT IT PUSHES",
          "r": "Crews and equipment standing, the area shut down, the activities that can't start, the milestone behind them. Equipment idle — not equipment cost. No dollars here."
        },
        {
          "h": "WHAT WE NEED FROM YOU, AND WHEN",
          "r": "Somebody out to look at it, and a direction. The date and time he needs them there, and what stays standing until they show. Close by reserving time and cost under whatever notice article his contract requires — he supplies it."
        }
      ],
      "omit": "What the contract documents showed AT THIS LOCATION — the sheet and its revision, the geotech, the utility record — or that they showed nothing here at all. That one sentence is the whole reason this is a notice and not a work order, and it is the sentence everybody skips because they are busy photographing the pipe. Write what the paper showed here. Never conclude what it means.",
      "needs": ["ref", "where"],
      "halt": "Anything about it reads live, pressurized, energized, or like a tank, a drum, or unknown material. Stop — that is an evacuate-and-call, not a document. Nobody types a notice before the utility and the safety director have been called.",
      "facts": [
        "date and clock time it was uncovered",
        "location by grid or station, and the depth, measured",
        "what the sheets, the geotech or the utility records show at that location",
        "size, material and condition as found",
        "who was called and at what clock time",
        "photos with a tape and a grid line or station marker, shot before anything moved",
        "crews and equipment standing, and the milestone behind them"
      ],
      "secondary": [
        "the extra work write-up once direction comes back",
        "the daily entry that anchors the date",
        "the note asking the sub to document his own standby"
      ]
    }
  ],
  "overrides": {
    "daily-report": {
      "name": "The Daily",
      "aka": [
        "daily",
        "daily log",
        "field report",
        "superintendent's daily",
        "work performed today",
        "daily narrative",
        "super's log"
      ],
      "why": "The narrative half of the daily. The log the job runs on already owns weather, head count, deliveries, equipment on and off and visitors — this is the box none of those fields can fill, and it is the first thing anybody pulls a year later.",
      "sections": [
        {
          "h": "JOB, NUMBER AND THE DATE THE WORK HAPPENED",
          "r": "Job name and number, and the calendar date the WORK happened — never the date he is typing. That is the whole header. Weather, per-company head count, deliveries, equipment on and off and visitors are structured entries in the daily log the job runs on. They do not get retyped here."
        },
        {
          "h": "WORK PERFORMED — BY AREA",
          "r": "Prose, by the location the drawings name: level, grid, column line, room number. \"Rocked the east corridor, grids 4-7, Level 2\" — never \"drywall continued\". Every company gets its own sentence, in the order he walked it. If an inspector or somebody off the design team said something on site, it goes in the sentence for that area, in their words."
        },
        {
          "h": "TOMORROW",
          "r": "What is planned, and what has to land or be answered for it to happen. Short. Never a date somebody else controls."
        }
      ],
      "omit": "The idle half of the job. Every daily records what DID happen and never that the east half sat all day waiting on the electrician's rough — so when the schedule fight comes there is no entry to hang the day on, and no entry reads a year later as nothing happened. Name the crew, the area, the hours they stood and the one thing they were waiting on, on the day it happened.",
      "needs": ["who", "where", "count", "notdone"],
      "halt": "The notes mention an injury, a near miss, property damage or a utility strike. Stop and say so — that never gets summarized inside a daily. It needs its own write-up, because a half-sentence in a daily becomes the exhibit.",
      "facts": [
        "job name and job number",
        "the calendar date the work happened, not the date he is typing",
        "areas named the way the drawings name them — level, grid, column line, room",
        "which company did what, and where",
        "anything that stopped, and the one thing it was waiting on",
        "what an inspector or the design team said on site, in their words"
      ],
      "secondary": [
        "the Monday roll-up to the PM built from a week of dailies",
        "a one-paragraph state of the job for the owner",
        "the manpower-trend note when a sub's count keeps dropping"
      ]
    },
    "incident-report": {
      "name": "The Incident Write-Up",
      "aka": [
        "incident report",
        "injury report",
        "accident report",
        "near miss",
        "first report",
        "property damage",
        /* "dig-in" LIVES ON `unforeseen-condition`, NOT HERE (2026-09-02). It was on
           both, and a word on two documents is a shelf that cannot answer. A dig-in
           is genuinely both things, so the split is by what a super TYPES it for:
           he types "dig-in" to get paid for the hole, and this document stays
           reachable for the safety half by "utility strike", which means one thing
           and only here. */
        "utility strike"
      ],
      "why": "This paragraph outlives everybody on the job. Write what you saw, because it becomes the exhibit.",
      "sections": [
        {
          "h": "JOB, DATE, TIME AND WHERE",
          "r": "Job name and number, the calendar date, the clock time, the exact location by level/grid/room, and what happened in one sentence. The carrier's first report, the log the recordkeeper runs and the owner's incident form are owned and numbered by them — this is the narrative that gets pasted into all three, and it has to read the same in each."
        },
        {
          "h": "WHO WAS INVOLVED",
          "r": "Full name, employer, craft, how long he has been on this job, and his foreman. If somebody was hurt, what was hurt and what he said, in his words. No medical opinion and no guess at how bad it is."
        },
        {
          "h": "THE WORK AND THE CONDITIONS",
          "r": "The task being done at that moment, who directed it, the plan or permit it was working under, the tools and equipment in use. Then light, weather, surface, housekeeping, barricades and what PPE was on — observed and flat, no adjectives that assign blame. Anything second-hand is attributed to whoever said it."
        },
        {
          "h": "WHAT WE DID, WITH TIMES",
          "r": "Care given and by whom, when 911 or the clinic was called, when work stopped, when the area was secured, when equipment was tagged out and where it sits now. A clock time on every line. Then the immediate corrective action and the stand-down — what was done, never why it happened. No cause, no recordability call, no \"he should have\"."
        },
        {
          "h": "WHO WAS NOTIFIED AND WHEN",
          "r": "Every call with the clock time and the name: safety, the owner's rep, the sub's PM, the carrier, the utility."
        },
        {
          "h": "PHOTOS AND WHAT WAS PRESERVED",
          "r": "How many photos, of what, who has them, where they live. What was preserved, and what had already been cleaned up before he got there — say so if it had."
        }
      ],
      "omit": "Witness names and cell numbers taken the same day, including the ones who don't work for you. The traveling hand who saw the whole thing is off the job by Friday and in another state, and every version of the story after that is second-hand. Get the names and the numbers before the crew leaves for the day.",
      "needs": ["when", "who"],
      "halt": "Somebody left by ambulance, didn't come back, or lost a limb or an eye. Stop — call the safety director and the carrier and let them run it. Nothing gets drafted or sent before that call.",
      "facts": [
        "date and clock time",
        "exact location by level / grid / room",
        "full name, employer and foreman of everyone involved",
        "witness names and cell numbers, including non-employees",
        "the task being done and who directed it",
        "times for care, stop-work and every notification",
        "where the equipment and the photos are right now"
      ],
      "secondary": [
        "the two-line daily entry that points at this write-up without repeating it",
        "the stand-down note for the next morning",
        "the note asking the sub for his own write-up"
      ]
    },
    "change-request": {
      "name": "The Extra Work Write-Up",
      "aka": [
        "COR",
        "change order request",
        "PCO",
        "potential change order",
        "extra work",
        "out of scope",
        "entitlement letter",
        "T&M cover"
      ],
      "why": "Pricing gets checked line by line. Why it is extra is the half that gets argued, and this is that half.",
      "sections": [
        {
          "h": "JOB, DATE, AND WHO DIRECTED IT",
          "r": "Job name and number, the date, and one line naming the work. Then the direction behind it: the person, their company, the date and clock time, and whether it came as a written instruction, a marked-up sheet, an answered RFI, a meeting, or verbally on the floor. Their process owns the change number, the form and the log — we never assign one and we never call this a change order."
        },
        {
          "h": "WHAT THE BID SET SHOWED HERE",
          "r": "Sheet and revision, spec section, and what was on the bid set at this location. State it. No argument with it."
        },
        {
          "h": "WHAT IS DIFFERENT",
          "r": "The delta in field words: what we would have built against what we are being asked to build. If it is a quantity change, the quantities HE counted."
        },
        {
          "h": "WHAT IT TAKES TO DO IT",
          "r": "The added work as work — crews, trades, sequence, access, equipment, what gets torn out or redone, after hours or in an occupied space. The estimator owns every number with a dollar sign on it, and this document prints none."
        },
        {
          "h": "WHERE THE WORK STANDS",
          "r": "Not started, in progress under direction, or complete. If it is already done, the date it started and the notice that was given before it did."
        },
        {
          "h": "WHAT WE NEED FROM YOU, AND WHEN",
          "r": "One thing, one date, tied to a real activity: proceed, hold, or price and approve. Then what happens to the schedule if the answer is late."
        }
      ],
      "omit": "The time. Everybody prices the labor and the material and then leaves the schedule line blank or writes \"no impact\" to look easy to work with. Write the schedule line the day it goes out — which activity it lands on and what it interrupts — and when it isn't known yet, write it anyway: \"time impact not yet known; we are not giving up time on this change.\"",
      "needs": ["none"],
      "halt": "He wants the pricing itself — a number, a rate, a markup, a unit cost. Stop. We write the half that says why it is extra; the numbers come off the estimator's sheet and get pasted in.",
      "facts": [
        "who directed it: name, company, date, clock time, and written or verbal",
        "sheet and revision, and spec section, for what was bid",
        "the quantities or dimensions he measured",
        "whether the work is not started / in progress / complete",
        "the activity it lands on and what it interrupts",
        "the date he needs an answer"
      ],
      "secondary": [
        "the same-day note confirming a verbal direction",
        "the cover note when it proceeds on T&M tickets",
        "the follow-up on a COR that has been sitting"
      ]
    },
    "delay-notice": {
      "name": "The Impact Notice",
      "aka": [
        "notice of delay",
        "delay notice",
        "impact letter",
        "schedule impact",
        "papering it",
        "notice of impact"
      ],
      "why": "Somebody else's problem quietly becomes your delay the moment nobody writes it down. This is the writing down, same day, while it is still happening.",
      "sections": [
        {
          "h": "JOB, ISSUE, AREA, DATE IT STARTED",
          "r": "One line: job name and number, the issue, the area, and the date it started. Scope it to somebody else's issue — a late answer, denied or lost access, owner-furnished material that didn't land, another prime's work, an inspection nobody scheduled. Weather has its own notice and does not go in here."
        },
        {
          "h": "WHAT IS STOPPED RIGHT NOW",
          "r": "Named crews, named companies, exact areas by grid/level/room, and the activities that cannot proceed. Present tense — what is happening today, not what might."
        },
        {
          "h": "WHAT WE'VE DONE TO KEEP WORKING",
          "r": "Resequencing, crews moved to other areas, work-arounds, overtime already run — real actions with dates. A notice with no mitigation in it invites the free answer that we should have worked around it."
        },
        {
          "h": "WHAT IT PUSHES",
          "r": "The successor activities and the milestone, named the way the schedule names them. No day counts we calculated and no dollars — the scheduler owns the analysis and this document does no arithmetic."
        },
        {
          "h": "WHAT WE NEED, AND BY WHEN",
          "r": "One specific thing with a date tied to an activity: the answer, the access, the material, the direction. Then what happens to the milestone if that date slides."
        },
        {
          "h": "WHERE WE STAND",
          "r": "The reservation in his own contract's words — time and cost to be determined, rights reserved, notice given under the article his contract requires. He supplies the article number; we never cite one."
        }
      ],
      "omit": "The date and clock time you first knew, and every time you raised it before this letter. Everybody writes what happened; almost nobody writes \"first seen 0715 Tuesday the 12th, raised with you on site the same morning, again in the Thursday meeting.\" Without those lines a notice written the same day still reads like it sat.",
      "needs": ["when"],
      "halt": "The notes are really about weather, or they already have dollars and day counts attached. Stop and ask — a weather day is its own notice, and a priced claim belongs to the PM and counsel, not to something thumbed out in the truck.",
      "facts": [
        "the date and clock time first observed",
        "who was told before this letter, and when",
        "the crews and areas stopped, by company and by grid/level",
        "what was tried to work around it",
        "the successor activity or milestone affected",
        "the thing he needs and the date he needs it",
        "the notice article his contract requires, if he wants it cited"
      ],
      "secondary": [
        "the running update when the same issue is still open a week later",
        "the sub-facing version telling his own subs to document their standby",
        "the closing note when it clears"
      ]
    },
    "service-writeup": {
      "name": "Warranty Callback Write-Up",
      "aka": [
        "warranty call",
        "warranty response",
        "callback",
        "11-month walk item",
        "post-turnover call",
        "warranty vs damage"
      ],
      "why": "Says what you found, whose work it is, and on what basis you touched it — before somebody fixes it for free and sets that as the answer for the whole building.",
      "sections": [
        {
          "h": "BUILDING, DATE, WHO CALLED",
          "r": "Building and unit, who called and their number, what they reported in their own words, the date and clock time of the call, and the date and clock time he got there. The response time is half of what gets argued later."
        },
        {
          "h": "WHAT WE FOUND",
          "r": "The observed condition at the location: room, level, unit tag, elevation. The measurements HE took. What it is doing — not yet what he thinks put it there."
        },
        {
          "h": "WHAT HE RULED OUT",
          "r": "What he checked and eliminated, in his own words, and anything he was told by somebody else, kept separate and attributed to them. If the cause isn't known it says undetermined. A guess never gets printed as a finding, and nobody here hands him a list of causes to pick from."
        },
        {
          "h": "WHAT WE DID TODAY",
          "r": "The temporary fix, what was made safe, what was left running or shut down, and the condition the space was left in. If nothing was done, why."
        },
        {
          "h": "WHAT WE NEED FROM THE OWNER",
          "r": "Access, hours, shutdown windows, an escort, a decision — one thing, one date. Plus the standing request that they call us first, before somebody else opens it up."
        }
      ],
      "omit": "The one line saying whether you did that work as warranty, as chargeable, or as undetermined — written the day you did it. Roll a crew, fix it, say nothing about the basis, and you have answered the question for every other unit in the building; the next twenty calls come to you free. Even \"undetermined — we responded to protect the building and are reserving the question\" is an answer. HE states it. Nobody here decides coverage and nobody here quotes a term we were not handed.",
      "needs": ["none"],
      "halt": "There's water running, no heat in freezing weather, an odor of gas, or anything else putting the building or the people in it at risk. Stop — make the calls and get somebody moving. It gets written up after the building is safe.",
      "facts": [
        "who called, their number, and the clock time of the call",
        "the time he actually got there",
        "location by room / level / unit tag, and the condition observed",
        "the turnover date, if he has it",
        "which sub's work it is",
        "whether he is calling it warranty, chargeable, or undetermined",
        "what the owner has to provide for the permanent fix, and the date"
      ],
      "secondary": [
        "the note to the sub telling him to respond, with the date",
        "the 11-month walk transmittal",
        "the entry for the warranty log the office keeps"
      ]
    },
    "handover": {
      "name": "The Turnover Write-Up",
      "aka": [
        "turnover",
        "handover",
        "closeout",
        "close out",
        "beneficial occupancy",
        "area turnover",
        "hand off"
      ],
      "why": "The last thing anybody reads and the first thing they blame. What it has to settle is who owns the area between the walk and final.",
      "sections": [
        {
          "h": "JOB, AREA, DATE TURNED OVER",
          "r": "Job name and number, the area or system by the name the drawings give it, the date and clock time it changed hands, and who walked it, by name and company."
        },
        {
          "h": "WHAT IS GOING OVER — AND WHAT IS NOT",
          "r": "Name the areas and systems going over, and name the ones right alongside that are NOT. Anything not named gets assumed."
        },
        {
          "h": "WHAT WAS TESTED, AND WHO WATCHED IT",
          "r": "The test or demo, the date, and who witnessed it by name and company. Record what was witnessed and who signed. Never whether it passed."
        },
        {
          "h": "WHAT WENT WITH IT",
          "r": "Keys, cards, codes, O&Ms, attic stock, spares — what, how many, to whom by name, and the date they signed for them."
        },
        {
          "h": "WHO TO CALL",
          "r": "One name and number for the building, and who takes a call after hours. Plus the standing request that they call us first before somebody else opens it up."
        }
      ],
      "omit": "Who owns the area between the walk and final — access, protection and damage. The space goes over, the owner's people and their vendors start working in it, and every mark on it after that lands back on your punch list because nobody wrote down the day it stopped being yours to protect. Name the date it changed hands, who has access after that, and who is responsible for what happens in it.",
      "needs": ["when", "who"],
      "halt": "He wants this to stand as the certificate itself — substantial completion, beneficial occupancy, the C of O. Stop. Those get issued by other people on their own paper. This is the narrative of the walk and what went with it.",
      "facts": [
        "job and the area by the name the drawings give it",
        "the date and clock time it changed hands",
        "who walked it, by name and company",
        "what was witnessed and by whom",
        "what was handed over and who signed for it",
        "what is still open, who owes it, and when",
        "who has access to the area from that date, and who protects it"
      ],
      "secondary": [
        "the owner-facing version",
        "the punch list of what is left",
        "the note to the subs telling them the area is occupied"
      ]
    },
    "meeting-minutes": {
      "name": "OAC / Coordination Notes",
      "aka": [
        "minutes",
        "oac",
        "oac minutes",
        "coordination meeting",
        "sub meeting",
        "weekly notes",
        "progress meeting"
      ],
      "why": "Whichever version goes out first is the one everybody works off all week. Send it the same day.",
      "sections": [
        {
          "h": "JOB, MEETING, DATE, AND WHO WAS ON IT",
          "r": "Job name and number, which meeting it was (OAC, sub coordination, pre-install), the date, and everybody in the room by name and company. Then who was NOT there but is bound by what was decided, and the date these notes go final if nobody comes back on them."
        },
        {
          "h": "WHAT WAS DECIDED",
          "r": "One line per decision, who made it, and what changes on the floor because of it. Discussion that decided nothing does not appear. If the CM issues the minutes and numbers the items, use their numbers — we never renumber somebody else's log."
        },
        {
          "h": "WHERE WE DON'T AGREE",
          "r": "Anything said in the room that we do not accept, one flat sentence each, written the same day. Left out, it comes back as agreement."
        }
      ],
      "omit": "The date each open item was FIRST raised. Every set of minutes carries the item forward and re-stamps it with this week's date, so a thing that has been sitting since March reads two weeks old and nobody in the room ever sees how long it has actually been sitting. Carry the original date on every item, every week, until it closes.",
      "needs": ["when"],
      "halt": "Only if it isn't clear which meeting this was or when it happened.",
      "facts": [
        "job name and job number",
        "which meeting it was, and the date",
        "everybody in the room, by name and company",
        "who was not there but is bound by it",
        "each decision and who made it",
        "each open item, with the date it was FIRST raised",
        "the date the notes go final"
      ],
      "secondary": [
        "an action-items-only version for the crew",
        "the same items rolled forward into next week's agenda"
      ]
    }
  },
  "drop": [],
  "vocab": [
    "our-f-eye -> RFI",
    "ay-ess-eye -> ASI (architect's supplemental instruction)",
    "oh-ay-see -> OAC",
    "ay-aitch-jay -> AHJ",
    "ee-oh-are -> EOR (engineer of record)",
    "see-oh-are -> COR (change order request)",
    "sea of oh -> C of O",
    "tee-see-oh -> TCO",
    "see-ex -> Cx (commissioning)",
    "nick -> NIC (not in contract)",
    "el dees -> LDs (liquidated damages)",
    "low toe -> LOTO (lockout / tagout)",
    "swip -> SWPPP",
    "sub mittal -> submittal",
    "look ahead -> look-ahead",
    "back charge -> back-charge",
    "screwed -> screed",
    "in bed -> embed",
    "a grass -> egress",
    "sub straight -> substrate",
    "block out -> blockout",
    "sheer wall -> shear wall",
    "certain wall -> curtain wall",
    "de-mizing wall -> demising wall"
  ],
  "reminders": [
    "anything is about to get covered — backfill, a pour, rock, the lid, insulation -> remind him to shoot it with a tape and a grid line or column mark in the frame BEFORE it is covered; after that the only proof left is destructive",
    "a verbal direction from the owner, the architect, the CM or an inspector is mentioned -> remind him to confirm it in writing the same day, naming who said it, when, and where they were standing — a verbal nobody confirmed is unauthorized work",
    "a delay, a hold, a stop or a change comes up -> remind him to put the date and clock time he FIRST knew at the top of it, plus every time he has raised it since",
    "an injury, a near miss, property damage or a utility strike comes up -> remind him to get witness names and cell numbers before the crew leaves for the day, including the ones who don't work for us",
    "a scope is about to start over somebody else's work — rock over framing, flooring over slab, paint over rock -> remind him to get the installer's own words on whether he accepts what he is going onto, before he starts, not after"
  ]
};
