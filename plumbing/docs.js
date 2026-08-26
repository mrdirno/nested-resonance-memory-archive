/* PLUMBING FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about plumbing work and nothing else.
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
  "trade": "commercial plumbing",
  "docs": [
    {
      "id": "flood-report",
      "name": "Flood Report (we broke a line)",
      "aka": [
        "flood report",
        "water damage report",
        "leak incident",
        "water event",
        "we broke a line",
        "we flooded it",
        "pipe let go",
        "water got out"
      ],
      "family": "incident",
      "from": "the plumbing foreman who was on site",
      "to": "my PM, the GC's super and the owner's rep",
      "why": "The first written account decides who pays for the drywall, the flooring and the tenant's downtime — write it before somebody else writes it for you.",
      "note": "narrative only — the office and the carrier own the claim number",
      "sections": [
        {
          "h": "WHAT LET GO AND WHERE",
          "r": "Site and building in the first line with the date, then floor, grid and room, then the exact component that let go — size, material, joint type — and what it was serving. No cause and no theory in this section."
        },
        {
          "h": "TIMELINE",
          "r": "Clock times only: found, who called who, when you got there, when it was isolated, when the water actually stopped, when the fans went in. Use the user's times exactly. Never round it to look better and never invent a time."
        },
        {
          "h": "HOW WE SHUT IT DOWN",
          "r": "Which valve, where it is, who closed it, whether it held or you had to go upstream. If a valve wouldn't close, was buried, or wasn't there at all — say so. That fact is worth money."
        },
        {
          "h": "WHAT GOT WET",
          "r": "Room by room, floor by floor, the ceiling and everything under it, contents and finishes. Include what was already stained or damaged before this. Never put a dollar figure on any of it — you're not the adjuster."
        },
        {
          "h": "WHAT WE DID TO GET THE WATER UP",
          "r": "Water pulled up, fans and dryers in and when, base pulled, tile lifted, tarps hung, who you called to dry it out and when they rolled in. Keep it factual and keep the times on it."
        },
        {
          "h": "WHO WE TOLD",
          "r": "Everybody on site and everybody notified — name, company, time, and how you reached them. Then close the letter with one flat line that this is a factual account and the cause hasn't been determined. No fault, no apology, no \"we should have,\" and never name another trade as the one who did it. That line gets no heading over it."
        }
      ],
      "omit": "The failed piece itself and where it is right now. Every one of these fights gets settled by the part — the split coupling, the burned fitting, the ring that never got crimped. If it went in the dumpster you've already lost the argument. Name who bagged it, when, what's written on the tag, and where it's sitting.",
      "halt": "Only stop and ask if the time the water was isolated is unknown or contradicted in the notes — every argument downstream hangs off that one number.",
      "facts": [
        "Building, floor, grid and room where it let go",
        "The component that let go: size, material, joint or connection type",
        "What system it was on, as the user states it",
        "Clock times: found / called / arrived / isolated / fans in",
        "Which valve was closed and exactly where it is",
        "Everybody on site and everybody notified, by name and time",
        "Every space that took water, including the floors below",
        "Photos taken and when — before and after the cleanup started",
        "Where the failed part is being kept and who bagged it",
        "Whether anybody else had worked on that piping before you"
      ],
      "secondary": [
        "the two-paragraph version for the GC's daily log",
        "the notification email to your own office",
        "a follow-up letter once the failed part has been looked at"
      ]
    },
    {
      "id": "line-strike",
      "name": "Line Strike Report (we hit something in the ground)",
      "aka": [
        "hit a line",
        "utility strike",
        "utility damage",
        "dig-in",
        "cut the fiber",
        "damaged conduit",
        "locate ticket",
        "811",
        "unmarked line"
      ],
      "family": "incident",
      "from": "the underground foreman",
      "to": "my PM, the GC's super and the owner of the line we hit",
      "why": "Whether you eat the utility's repair bill comes down to what was marked, how deep it was, and whether you measured it before the hole got closed.",
      "note": "narrative only — the utility's own damage form is theirs to number",
      "sections": [
        {
          "h": "TICKET AND MARKS",
          "r": "Site and address in the first line with the date and time of the strike, then the locate ticket number and the date it was called in, which utilities responded, what was marked and in what colors, and what came back clear or never showed at all. If there was no ticket, say that plainly — hiding it is worse."
        },
        {
          "h": "WHAT WE WERE DOING",
          "r": "The excavation: location by address, grid or station and offset, what we were installing, how we were digging — excavator, hand dig, vac truck, hydro, trencher — and who was running it and who was spotting."
        },
        {
          "h": "WHAT WE HIT",
          "r": "The line: type, size, material, direction of run, what it appeared to be feeding, and the damage itself — a nick, the jacket only, a full break. Describe what you can see. No theory about how it got there."
        },
        {
          "h": "WHAT HAPPENED NEXT",
          "r": "Clock times: contact, work stopped, who was called (the line owner, one-call, the GC, the owner), when they showed up, whether anybody lost service and who."
        },
        {
          "h": "CONDITION OF THE HOLE",
          "r": "That the excavation was left open, protected and barricaded for the line owner to look at. If it had to be closed — and on a live job the GC will push you to close it — name who directed it closed, their company and the time. Never backfill on your own say-so."
        },
        {
          "h": "PHOTOS",
          "r": "Say what's in each photo: the marks or the bare ground where there weren't any, the line lying in the trench, the damage itself, and a wide shot tying it back to the building or the station. Who shot them, when, and where the folder lives. The photos are the report; this section is the index."
        }
      ],
      "omit": "The depth from finish grade and the horizontal offset from the paint, measured with a tape while the line is still lying in the hole and with the tape in the frame. Nobody measures it — they call it in, take the chewing, and backfill. \"38 inches from finish grade, 6 foot 4 east of the nearest orange mark,\" with a photo of the tape, is usually the whole defense, and once the hole is closed there isn't one.",
      "halt": "Only stop and ask if there is neither a locate ticket number nor a clear statement that no ticket existed — that single fact decides who pays.",
      "facts": [
        "Locate ticket number and the date it was called in",
        "Which utilities responded and what colors were on the ground",
        "Exact excavation location: address, grid, station, offset",
        "What we were installing and how we were digging",
        "Who was running the machine and who was spotting",
        "Line type, size, material, direction of run and what it fed",
        "Depth from finish grade and offset from the nearest mark, off a tape",
        "Times: strike, work stopped, calls made, who responded",
        "Whether anybody lost service and who",
        "Whether the hole was left open, and who directed it closed if it wasn't",
        "What photos were taken, by whom, and when"
      ],
      "secondary": [
        "the same-day notification email to the line owner",
        "the paragraph for the GC's daily log",
        "a follow-up once the utility's repair crew has been out"
      ]
    },
    {
      "id": "ready-for-cover",
      "name": "Ready-for-Cover Letter (before the pour or the rock)",
      "aka": [
        "ready to cover",
        "pre-pour letter",
        "cover request",
        "ready for backfill",
        "under-slab sign-off",
        "before they close the wall",
        "buried work notice"
      ],
      "family": "verification",
      "from": "the rough-in foreman",
      "to": "the GC super and my PM",
      "why": "Once it's under the slab or behind the rock, the only version of what you installed is what you wrote down the day before.",
      "note": "narrative only — the inspector's card and the test log stay theirs",
      "sections": [
        {
          "h": "WHAT'S READY AND WHERE",
          "r": "Site and building in the first line with today's date, then the exact area being released — grid and column lines, floors, room numbers. Never \"the north side\" with no lines on it. If you can't bound it, you can't release it."
        },
        {
          "h": "WHAT'S IN THE GROUND / IN THE WALL",
          "r": "Short prose by AREA, not run by run: \"6-inch cast under the kitchen, hub and spigot, hung off the deck; 2-inch copper up the east wall.\" Sizes, materials, joint method and slope as measured. Never let this grow into a row-by-row table — the run log tool owns the row detail, and if this section turns into a form the letter quits being a letter."
        },
        {
          "h": "TEST STANDING RIGHT NOW",
          "r": "What section is under test, the medium, where the gauge is, the reading when it was filled, the reading right now, the clock time it went on and who witnessed it. Name the photo of the gauge and the time it was shot, so the photo is in the letter and not just in somebody's phone. Report only the user's numbers — never state what the pressure or the duration is supposed to be, and never write \"passed.\""
        },
        {
          "h": "INSPECTION AND WITNESS",
          "r": "What's been walked, by whom, on what date, and what's still pending. If a card was signed, name it the way the user named it. Never characterize a result the user didn't state."
        },
        {
          "h": "WHAT ISN'T DONE IN THIS AREA",
          "r": "Anything left out: a sleeve still pending, a fixture rough not set, a section left open for another trade, a hole left for a tie-in. Never blank if there's an open item."
        },
        {
          "h": "RELEASE",
          "r": "A plain statement that the area is released for cover as of a date and time, and that anything after that — another trade's penetration, a re-route, damage during the pour — is a separate ticket."
        }
      ],
      "omit": "The invert elevations at the tie-in points, off the rod, written into the letter. Everybody writes \"ready for cover\" and leaves the inverts on a markup that lives in a truck. When the next man comes to tie in and those numbers aren't in anybody's mail, the next version of that pipe is a jackhammer and it's on your bill.",
      "halt": "Only stop and ask if the area boundary can't be identified — you cannot release \"some of the underground.\" Everything else gets a <MISSING>.",
      "facts": [
        "Building, grid or column lines, floors and rooms in the area being released",
        "Systems installed: sizes, materials, joint method",
        "Slopes and invert elevations as measured, with units",
        "What section is on test, the medium, and where the gauge is",
        "Gauge reading at fill, reading now, the time it went on, hours elapsed",
        "Who witnessed it and their company",
        "Inspection date, who walked it, and what was signed — as the user states it",
        "The gauge photo: when it was shot and where it's stored",
        "Every open item in that area",
        "The date and time you're calling the area released"
      ],
      "secondary": [
        "the confirming memo after the pre-pour walk",
        "the photo index that ships with the as-built markup",
        "a re-release letter when the area gets opened back up"
      ]
    }
  ],
  "overrides": {
    "daily-report": {
      "name": "The Daily (what we put in, what stopped us)",
      "aka": [
        "daily report",
        "daily log",
        "field report",
        "DFR",
        "end of day",
        "what we did today",
        "foreman's daily"
      ],
      "why": "This is YOUR account, not the GC's numbered log — and it's the only dated record of who stopped you and who told you to do something extra.",
      "sections": [
        {
          "h": "AREAS AND CREW",
          "r": "Site and building first, then the date of the shift — that is how anybody finds this a year later. Then where the crew actually worked: floor, grid lines, riser, room numbers, and who was where, in short prose (\"me, Ruben and the apprentice on 3rd floor rough all day, two hours of it hunting a valve\"). Names and hours stay sentences by area, never a headcount table — the table is the GC's, the men and hours are ours and the office costs the job off this."
        },
        {
          "h": "WORK PUT IN",
          "r": "What physically got installed, set, tested or backfilled, by area and system, with sizes and quantities as the user stated them. Never \"continued rough-in\" with no location on it, and never a quantity we invented."
        },
        {
          "h": "WHAT STOPPED US OR SLOWED US",
          "r": "The specific condition, the area, and how long we sat. State the condition, never a man's character. This section RECORDS the hold — it is not the notice. The impact letter is the first written notice of it and the extra-work letter is why it isn't in our number; don't write the same paragraph into all three. If nothing stopped you, say so plainly — a blank here reads as \"nothing happened\" three months later."
        },
        {
          "h": "INSPECTIONS, TESTS AND COVER",
          "r": "What was inspected or witnessed and by whom, what went on test or came off test, and what got covered, poured or closed today. Readings and times exactly as the user recorded them. Never state what a pressure or a duration is supposed to be, and never write our own pass or fail."
        },
        {
          "h": "MATERIAL AND EQUIPMENT",
          "r": "What landed, what's short and holding you up, what's on rent and sitting. Short prose only — this is not the packing list or the rental log."
        },
        {
          "h": "TOMORROW",
          "r": "Where the crew goes, what has to be ready for them, and who owes it. One named person per item, never \"the GC.\""
        }
      ],
      "omit": "The verbal direction. Every foreman gets told \"while you're in there, just run one over to the mop sink\" and it never makes the daily. Ninety days later there's no ticket, no question written and no line in the log — so it's free work. One sentence with who said it, their company, what time and what area, and it's provable.",
      "halt": "Only stop and ask if the date of the shift is missing or contradicted — a daily with the wrong date on it is worse than no daily. Everything else gets a <MISSING> placeholder.",
      "facts": [
        "Date of the shift",
        "The weather, every day, whether it stopped you or not — nine dailies that mention the front is the only way you ever prove it",
        "Areas worked: building, floor, grid or column lines, riser, room numbers",
        "Who was on it and roughly how long, by area",
        "What got installed or set — system, size, material, quantity as counted",
        "Anything tested, witnessed, inspected or covered today, and by whom",
        "Any condition that stopped or slowed the crew, with how long",
        "Anyone who directed work outside the drawings — name, company, time",
        "Material short or delivered, and idle rented equipment",
        "Where the crew is going tomorrow and what has to be ready"
      ],
      "secondary": [
        "the two-line version for the GC's log notes box",
        "a weekly roll-up to your own PM",
        "the impact letter when today's blocker is still there tomorrow"
      ]
    },
    "service-writeup": {
      "name": "The Write-Up (found, did, still wrong)",
      "aka": [
        "service write-up",
        "work performed",
        "service report",
        "call notes",
        "what I did",
        "service ticket write-up",
        "invoice write-up"
      ],
      "why": "The prose you paste into your own work-performed field — not a replacement for it — that turns \"cleared stoppage\" into a bill nobody argues and a record that you warned them.",
      "sections": [
        {
          "h": "CALL AND ACCESS",
          "r": "Building and unit first, then the work order number and the date — that's the search key when somebody digs for this next year. Then who called, what they said was wrong in their words, when you got there, who let you in, and what was running or not running when you walked in. No diagnosis in this section."
        },
        {
          "h": "WHAT I FOUND",
          "r": "The condition in plain words: where, what material, what size, what state it was in, what came out of the line. Readings only as the tech took them, with his units. No cause, no blame, no code talk, no pass or fail language."
        },
        {
          "h": "WHAT I DID",
          "r": "The work performed in order — what you isolated and where, what you cut, what you installed with size and material, what you tested and how, what you put back in service. Never \"repaired leak\" with no location on it. Print every make and model exactly as the tech typed it, verbatim, including the model suffix; never suggest, substitute or complete one he did not give."
        },
        {
          "h": "WHAT'S STILL WRONG AND NOT INCLUDED",
          "r": "Conditions you found and did NOT fix, and why — not authorized, not in scope, needs a shutdown, needs parts, needs another trade. Say plainly it stays the owner's to deal with. Never leave this blank to make the call look clean."
        },
        {
          "h": "WHAT I RECOMMEND",
          "r": "What you'd do about it and what it takes — access, a shutdown window, bodies, lead time. No prices unless the user gave them, and no \"required\" or \"must be\" language."
        },
        {
          "h": "HOW I LEFT IT",
          "r": "The state of the building when you drove off: water on or off, gas on or off, appliances relit or tagged out, floor dry, gear left on site, area barricaded, and who you told before you left — by name and time."
        }
      ],
      "omit": "The valve you left in a non-normal position. Half of all callbacks are \"a plumber was here and now the third floor has no hot water.\" If you throttled a balancing valve, left a shutoff closed, tagged out a heater or shut a branch to isolate — that valve, where it is and the position you left it in has to be its own sentence, or the return trip is free and it's your fault.",
      "halt": "Stop and ask on two things only: whether the water was left ON or OFF when the tech drove away, and — if gas was involved at all — whether the appliances were relit or tagged out. Water off with nobody told is a callback; gas off with a pilot out and nobody told is a 2am phone call and the one thing on this call that can hurt somebody. Everything else takes a <MISSING>.",
      "facts": [
        "Date, time on site, time off",
        "Work order or ticket number as it exists in your own system",
        "Who reported it and their exact words",
        "Building, unit, floor, room, and the fixture or riser worked on",
        "Pipe size and material actually worked on",
        "Parts installed — size, type, material, and the make and model exactly as you read it off the box",
        "Any readings the tech took (pressure, temperature, footage down the line) with units",
        "What came out of the line and where it is now",
        "Every valve touched and the position it was left in",
        "Anything found and not repaired",
        "Who was told before you left, by name"
      ],
      "secondary": [
        "the short version for the work-performed box",
        "an email to the property manager on the deferred repair",
        "a callback summary when a second trip is needed"
      ]
    },
    "delay-notice": {
      "name": "Notice of Impact (we're being held up)",
      "aka": [
        "delay notice",
        "impact letter",
        "held up",
        "notice letter",
        "time impact",
        "can't proceed",
        "out of sequence",
        "stacked trades"
      ],
      "why": "You don't get paid for a hold you only mentioned in the trailer. Your contract sets your notice period — this is the dated record that you actually gave notice.",
      "sections": [
        {
          "h": "WHAT WE CAN'T DO AND WHERE",
          "r": "Site and building in the first line with today's date, then the specific work stopped or slowed by floor, grid, riser and system. Never \"we're being delayed on the project.\" This letter is the first written notice of the hold — the daily records it, this one gives notice of it."
        },
        {
          "h": "WHY",
          "r": "The condition in our way, stated flat as fact: what it is, where it is, whose work or whose answer it is. Name the condition, never a man's character, and never a cause you didn't see with your own eyes."
        },
        {
          "h": "WHAT WE'VE DONE AROUND IT",
          "r": "Whether it's still running today, and what we did to work around it — moved crews, resequenced, worked elsewhere. Working around it belongs in the notice, not in the argument later."
        },
        {
          "h": "WHAT IT'S COSTING RIGHT NOW",
          "r": "Bodies standing by or relocated, equipment on rent, remobilizing, out-of-sequence work, overtime being burned. Describe it. Never put a total dollar figure here unless the user gave one — costs are tracked and priced separately."
        },
        {
          "h": "WHAT WE NEED AND BY WHEN",
          "r": "The specific decision, area or access needed, from one named party, by one named date, to hold the sequence we're on. One date, one owner."
        },
        {
          "h": "WHAT HAPPENS IF WE DON'T GET IT",
          "r": "The mechanics of the slip in plain words: what activity moves, what gets done twice, what stacks on top of what. State it, never threaten. Close the letter with one flat line that we are not giving up time or cost on this and that we're tracking it separately from the date of this letter — no legalese, no \"please be advised,\" and no heading over it."
        }
      ],
      "omit": "The date the condition actually started, as separate from the date you're writing. Foremen write \"we've been held up in the east wing for a few weeks\" and hand the whole thing away — now the GC can argue you knew and sat on it. Put the start date in the first three lines and say plainly this is the first written notice of it.",
      "halt": "Only stop and ask if the date the condition began is unknown — everything in this letter hangs off that date.",
      "facts": [
        "Area and system affected: building, floor, grid, riser",
        "The specific condition blocking the work",
        "Date the condition began and whether it's still running today",
        "Any question, submittal or request already outstanding on it, by its own number",
        "Crew size affected and what they did instead",
        "Equipment on site sitting idle",
        "The specific thing needed, from whom, by what date",
        "What schedule activity it is and what it feeds",
        "Whether you raised it verbally before, when, and to whom"
      ],
      "secondary": [
        "a follow-up when the condition is still open a week later",
        "the closing letter when it finally clears, with the total days",
        "a short version for the GC's daily log"
      ]
    },
    "change-request": {
      "name": "Why It's Extra (the reason above the pricing)",
      "aka": [
        "change order write-up",
        "COR write-up",
        "PCO justification",
        "out of scope letter",
        "scope letter",
        "T&M cover letter",
        "not in our number",
        "backup letter"
      ],
      "why": "The pricing sheet is a column of numbers; the reason it's extra is a paragraph, and that paragraph is what gets it approved or bounced. The GC numbers his own change — we write the reason.",
      "sections": [
        {
          "h": "WHAT WE'RE BEING ASKED TO DO",
          "r": "Site, building and area in the first line with the date, then the work itself — what system, what sizes, what quantities, physically. Never lead with the contract argument."
        },
        {
          "h": "WHO DIRECTED IT AND WHEN",
          "r": "Name, title, company, date, and how it came — meeting, sketch, email, or verbally in the field. If it was verbal, say verbal and say plainly this letter is the confirmation of it."
        },
        {
          "h": "WHY IT ISN'T IN OUR NUMBER",
          "r": "The specific basis: the drawing and revision the bid was on and what it showed, the spec section, the exclusion in your own scope letter, or the field condition that didn't exist at bid. Cite the user's own documents by their own numbers only — never cite a code section, never invent a document number. This letter is not the delay notice; if it's also holding you up, that's a separate letter with its own date."
        },
        {
          "h": "WHAT'S DIFFERENT NOW",
          "r": "The delta side by side in prose — what was bid against what's being built. Sizes, routes, quantities, materials, sequence."
        },
        {
          "h": "TIME",
          "r": "Whether this moves the schedule and how, or one flat line that time is still being looked at and we're not giving it up. Never write \"no time impact\" unless the user said it."
        },
        {
          "h": "HOW WE'RE PROCEEDING",
          "r": "Either the work is on hold pending authorization, or it's going ahead on T&M at a named person's direction. One or the other, never ambiguous, never both."
        }
      ],
      "omit": "The rework you're about to eat twice. Everybody prices the new pipe and forgets the 40 feet of finished 4-inch that has to come back out, the wall that gets opened, the test you have to run again, the inspection you have to re-book and the day you lose waiting on it. Write the demo, the re-test and the re-inspection as their own lines or you're donating them.",
      "halt": "Only stop and ask if it isn't clear whether the work is on hold or already going ahead — the letter reads completely differently and it can't say both.",
      "facts": [
        "The added or changed work: location, system, sizes, quantities",
        "Who directed it — name, title, company, date, and how",
        "The drawing number and revision your bid was based on",
        "The document that shows the original scope, by its own number",
        "The field condition found, if that's the driver",
        "Installed work that has to come out or be redone",
        "Re-testing and re-inspection required",
        "Material lead time if it drives the schedule",
        "Whether the work is on hold or going ahead, and on whose direction"
      ],
      "secondary": [
        "a same-afternoon email confirming the verbal direction",
        "the short scope paragraph for the top of the pricing sheet",
        "a follow-up when the answer is still outstanding"
      ]
    },
    "damage-found": {
      "name": "Existing Conditions Letter (this was here before us)",
      "aka": [
        "pre-existing damage",
        "not our damage",
        "found condition letter",
        "existing pipe condition",
        "before we started",
        "we're not adopting this",
        "condition of existing"
      ],
      "why": "Everything wrong with the existing piping becomes yours the moment you touch the building, unless you wrote it down first.",
      "sections": [
        {
          "h": "WHERE WE ARE AND WHEN WE GOT HERE",
          "r": "Site, building, floor and room in the first line, then the date you first had access to that area and the date of these observations. The access date is the anchor for the whole letter."
        },
        {
          "h": "WHAT WE FOUND",
          "r": "The existing condition described physically: material, size, apparent age, corrosion, prior repairs, bellies and sags, missing or broken hangers, connections that don't match the drawings, active drips, ceiling and wall staining, already-damaged finishes. Describe what you can see with your eyes. Never estimate how much life is left in it and never call anything a code violation."
        },
        {
          "h": "WHY IT MATTERS TO OUR WORK",
          "r": "Plainly: what we're tying into, what we're expected to hang off of, what we're expected to reuse, and where the existing condition affects whether our new work holds up."
        },
        {
          "h": "WHAT WE ARE NOT TAKING ON",
          "r": "One flat paragraph that this condition isn't in our scope, we didn't cause it, and we're not standing behind existing material we tie into. No legalese."
        },
        {
          "h": "WHAT WE'D DO ABOUT IT",
          "r": "What you'd do if it were your building and roughly what it takes. Offer to price it. Never demand, never lecture."
        }
      ],
      "omit": "The date-stamped photos taken BEFORE your first day of work in that area — the stained ceiling tile, the rusted riser clamp, the cracked closet flange, the chipped lav that was already chipped — and the folder or album they live in, by its actual name, with who shot them and when. Nobody photographs the boring stuff on day one, and in month five the owner points at a stain you walked past forty times and it's yours. The letter is worth about a tenth of the photo behind it, so the letter has to say where the photo is.",
      "halt": "Only stop and ask if the date you first had access to the area is unknown — the whole letter is a race between that date and the damage.",
      "facts": [
        "Area: building, floor, room, grid",
        "The date you first had access and the date of these observations",
        "Existing material, size and system for everything you're tying into",
        "Each specific defect observed and exactly where it is",
        "Anything already leaking, stained or previously repaired",
        "What your scope makes you reuse, tie into or hang off of",
        "Photos taken, by whom, on what date, and the folder or album name they're in",
        "Who else was standing there when you saw it"
      ],
      "secondary": [
        "the walk record from the first walk of the area",
        "a price to correct the existing condition",
        "a follow-up when the condition gets worse during the job"
      ]
    },
    "handover": {
      "name": "Turnover Letter (system put in service)",
      "aka": [
        "turnover letter",
        "chlorination letter",
        "flush and disinfect",
        "startup letter",
        "put in service",
        "bac-t cover letter",
        "we put it in service"
      ],
      "why": "Proves the system was cleaned, filled and put in service on a named day by named people, and puts the handover in writing instead of leaving it to whoever remembers it later. It rides with the lab report; it is never a substitute for it.",
      "sections": [
        {
          "h": "WHAT WAS PUT IN SERVICE",
          "r": "Site and building in the first line with the date, then the system and its exact boundaries — which risers, which floors, from what point of connection to what termination. Never vague; the boundary is what you're standing behind."
        },
        {
          "h": "HOW IT WAS ISOLATED AND FILLED",
          "r": "What was valved off, what was capped, what was left open, how the line was filled and vented, and how the new work was kept separated from the existing."
        },
        {
          "h": "FLUSH AND DISINFECTION AS WE RAN IT",
          "r": "The sequence you actually ran: where solution went in, how it was pushed through, where it was drawn off, how it was neutralized and where it discharged — plus the concentration and dwell the crew wrote down, in their numbers and their units. Never supply a figure the crew didn't record, never say what it was supposed to be, and never write \"passed.\""
        },
        {
          "h": "SAMPLES",
          "r": "Who pulled samples, from which points, on what date, and which lab took them — and that the lab's own report goes with this letter. Never restate or characterize what the lab reported; that paper is theirs and it carries its own number."
        },
        {
          "h": "EQUIPMENT STARTED AND WHAT'S LEFT OFF",
          "r": "Every piece placed in operation — what, where, who started it, whether a factory rep was standing there — and then everything left off or partial: valves closed, balancing left where it is, equipment in hand, temporary connections still in, strainers still to be pulled and cleaned. This half is what prevents the callback. Never state a setting you weren't given."
        },
        {
          "h": "IN-SERVICE DATE AND WHO TOOK IT",
          "r": "The date and time the system was turned over, the name and title of who accepted it, and how they accepted it — in person, by email, on the walk."
        }
      ],
      "omit": "The sentence naming who operates and maintains the system from the in-service date forward. Everybody writes up the chlorination and skips that line — so when the building sits empty four months with dead legs and nobody flushing it, or a heater scales up on untreated water, it lands back on you. Name the date, name who took it, and say plainly that operating and maintaining it went with it.",
      "halt": "Only stop and ask if both the in-service date and who accepted the system are unknown — that pair is the entire point of this letter.",
      "facts": [
        "Exact extent of the system: building, risers, floors, point of connection to termination",
        "What was isolated, capped or left open",
        "Where solution was introduced and where it was drawn off",
        "What the crew wrote down for concentration and dwell, in their own numbers and units",
        "How and where it was neutralized and discharged",
        "Who pulled samples, from which points, on what date",
        "Which lab, and the report number so this letter points at it",
        "Equipment started, by whom, and anything left set where it is",
        "Every valve or device left in a non-normal position",
        "In-service date and time, and the name and title of who accepted it"
      ],
      "secondary": [
        "the transmittal email that carries the lab report up",
        "an O&M cover note for the closeout binder",
        "a confirmation to your own office that it's turned over"
      ]
    }
  },
  "drop": [],
  "vocab": [
    "sanitary tea -> sanitary tee",
    "why branch -> wye",
    "combo why -> combo wye",
    "pea trap -> P-trap",
    "close it flange -> closet flange",
    "a scutcheon -> escutcheon",
    "pecks -> PEX",
    "see PVC -> CPVC",
    "shed you'll forty -> Schedule 40",
    "no hub band -> no-hub band",
    "die electric union -> dielectric union",
    "T and P valve -> T&P relief valve",
    "pee are vee -> PRV",
    "vent through roof -> VTR",
    "in vert elevation -> invert elevation",
    "grease intercepter -> grease interceptor",
    "back water valve -> backwater valve",
    "flush ometer -> flushometer",
    "water hammer arrest her -> water hammer arrester",
    "tee em vee -> TMV",
    "re surk line -> recirc line",
    "trap prime her -> trap primer",
    "razor diagram -> riser diagram",
    "eight one one ticket -> 811 ticket"
  ],
  "reminders": [
    "When a test is described as holding -> remind them to shoot the gauge face legible, with a tape on the pipe and a grid line or column in frame, before anybody touches a valve. \"It was holding\" is not evidence; a readable gauge is.",
    "When covering, pouring, backfilling or closing a wall comes up -> remind them nothing gets buried until the inverts at the tie-ins and the photo coverage of that area exist. The next version of that pipe is a jackhammer.",
    "When any valve is left closed, throttled or tagged, or a gas appliance is left off -> remind them to name the valve or the appliance, where it is, and the person they told with the time. That one sentence is the difference between a billable trip and a free one.",
    "When a break, a flood or a failed part comes up -> remind them to bag and tag the piece and say in the document where it's stored. The part settles the claim; the paragraph doesn't.",
    "When somebody tells them to do work that isn't on the drawings -> remind them to write the name, title and time the same day, in the daily and in a confirming note. A verbal with no dated record is free work."
  ]
};
