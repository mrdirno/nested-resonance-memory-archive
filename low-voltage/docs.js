/* LOW-VOLTAGE FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about low-voltage work and nothing else.
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
  "trade": "low-voltage systems",
  "docs": [
    {
      "id": "inspection-deficiency-letter",
      "name": "Inspection Deficiency Letter",
      "aka": [
        "deficiency letter",
        "def list",
        "annual inspection findings",
        "ITM write-up",
        "test and inspect letter",
        "the letter that goes with the inspection report"
      ],
      "family": "notice",
      "from": "the tech who ran the inspection",
      "to": "the property manager",
      "why": "Every device you could not get to is yours until you name it in writing.",
      "note": "Narrative only — the inspection report owns the device list and its numbering. This letter rides with it and never rebuilds it.",
      "sections": [
        {
          "h": "BUILDING, DATE AND THE REPORT THIS GOES WITH",
          "r": "First two lines: building name and address, and the dates you were on site. Then the system, where the panel is, and the inspection report this letter rides with — its date and how it is filed — so a manager searching his mail a year from now lands on both. Never renumber that report and never restate it device by device."
        },
        {
          "h": "WHAT DID NOT WORK",
          "r": "One line per finding, only the ones he has to make a decision about: the device or point AS IT IS LABELLED IN THE FIELD, where it physically is, and what it did or did not do. Do not reproduce the report's device list — it is already in his file. No readings nobody handed you, no pass, no fail, no to-code."
        },
        {
          "h": "WHAT IT MEANS IN PLAIN WORDS",
          "r": "For each one, the job that point is not doing right now, said the way an owner talks: the floor with no horn, the room with nothing looking at it, the signal that is not reaching the monitoring center. Nothing beyond that. Never write unsafe, never write violation, never name a code, never guess at a fine."
        },
        {
          "h": "HOW WE LEFT THE SYSTEM",
          "r": "Normal, in trouble, or with something disabled, bypassed or on test — say which, name the point, and say whether it is still that way as you write. If it was left off normal, say plainly that the out-of-service notice goes with this letter. This letter states the condition and points at that notice; it never tries to be it."
        },
        {
          "h": "WHAT WE NEED FROM YOU",
          "r": "Access dates, a decision, a PO, a person to meet — each with a name and a by-when. No prices, and no repair scope the office has not quoted."
        }
      ],
      "omit": "The no-access list, one at a time — 'Unit 214, tenant would not open, 3/12, called twice' — instead of 'some units were inaccessible'. A year on, the device that failed is always the one nobody could reach, and a letter that says the building was inspected says you reached all of it.",
      "needs": ["when", "where", "notdone"],
      "halt": "Only stop and ask if you cannot tell which building and which system the notes are about. Everything else, dates included, gets <MISSING>.",
      "facts": [
        "building name and address",
        "the dates you were on site",
        "the system and where the panel is",
        "the inspection report this letter rides with — its date and where it is filed",
        "each finding: field label, where it is, what it did",
        "every point or area you could not get to, and who turned you away",
        "the state the panel was left in, and whether anything is still bypassed or on test"
      ],
      "secondary": [
        "a quote request to our own office off the same findings",
        "a short cover email to the property manager",
        "a follow-up letter once the repairs are done"
      ]
    },
    {
      "id": "nuisance-alarm-letter",
      "name": "Nuisance Alarm Letter",
      "aka": [
        "false alarm letter",
        "unwanted alarm report",
        "repeat alarm history",
        "why does it keep going off",
        "false alarm fee response",
        "AHJ nuisance letter"
      ],
      "family": "notice",
      "from": "the service tech",
      "to": "the property manager",
      "why": "By trip three somebody has to put in writing what the tech actually saw, or you own it forever.",
      "sections": [
        {
          "h": "THE BUILDING AND THE TRIPS WE ARE TALKING ABOUT",
          "r": "First two lines: building name and address, and the span of dates these trips cover. Then the system, where the panel is, and the site or account number as the customer's own paper carries it — never one we made up. Say how many trips, so the reader can see this is trip four and not trip one."
        },
        {
          "h": "WHAT WE FOUND EACH TIME",
          "r": "Each trip in order by date: what the tech was told, what he found, what he did. The trips where he found nothing get written the same as the rest — a trip that found nothing is evidence, not a gap."
        },
        {
          "h": "WHAT WE SAW ON THE DEVICE AND AROUND IT",
          "r": "Only what the tech saw with his own eyes once he had it open or stood under it, and what the panel printed — quoted in the panel's own words. Never a cause he did not name himself, never a claim about how old the device is or how it was made, never a spacing or coverage claim, never a reading nobody handed you."
        },
        {
          "h": "WHAT HAS ALREADY BEEN DONE",
          "r": "Cleaned, swapped, re-sited, reprogrammed, isolated — each with the date and who did it. This is the section that stops the reader asking why we have not tried anything."
        },
        {
          "h": "WHAT WE ARE ASKING FOR, AND WHO HAS TO SAY YES",
          "r": "The one thing we want done next, who has to approve it — the owner, the tenant, the AHJ, a permit — and by when. Say plainly what we are not allowed to do on our own. No prices, and no threat about the contract."
        }
      ],
      "omit": "The panel's own event history, pulled and quoted — date, clock time and the point or zone exactly as it prints, one line per event. Everybody writes 'the customer says it trips at night.' The history is free, it is the only proof the alarms ever happened, and it rolls over and is gone the day somebody clears it.",
      "needs": ["when", "where", "count"],
      "halt": "Only stop and ask if the notes never say whether these events were ALARMS, TROUBLES or SUPERVISORIES. That is three different letters and you cannot pick for him.",
      "facts": [
        "building name and address, and the span of dates",
        "each event: date, time, point or zone off the panel history",
        "whether each one was an alarm, a trouble or a supervisory",
        "what was found on every trip, the empty ones included",
        "what the tech saw with his own eyes, and what the panel printed",
        "what has already been tried, with dates",
        "the one thing we are asking for, and who has to approve it"
      ],
      "secondary": [
        "a short cover note to the fire department contact",
        "a quote request for the work we are asking for",
        "a trip-by-trip history for the service manager"
      ]
    },
    {
      "id": "pretest-ready-letter",
      "name": "Pre-Test Complete / Ready For Acceptance Test",
      "aka": [
        "pretest letter",
        "ready for the fire marshal",
        "acceptance test request",
        "ready for inspection",
        "schedule the AHJ",
        "system is ready letter"
      ],
      "family": "verification",
      "from": "the foreman who ran the pretest",
      "to": "our PM and the GC",
      "why": "It is the paper that says we are ready, and it names the things that will not run if they call the inspector anyway.",
      "note": "Narrative only — the inspector's office owns the acceptance record and its numbering.",
      "sections": [
        {
          "h": "BUILDING, PERMIT AND WHAT WE ARE OFFERING",
          "r": "First two lines: building name and address, and the permit or case number exactly as the GC or the inspector's office wrote it — never one of ours, never invented. Then exactly which part is being offered: whole building, a phase, floors, one tenant space. Half a building pretested is not a building pretested."
        },
        {
          "h": "WHAT WE RAN, AND WHEN",
          "r": "The dates, who ran it, what was operated, and who stood there and watched it. A count or a share of the system goes in only if the tech gave you one, in his words. Never work one out, and never claim anything was covered beyond what he said."
        },
        {
          "h": "WHAT IS COMPLETE AND WORKING",
          "r": "By floor or by subsystem, in the tech's own words, and only what he named. No pass, no fail, no readings nobody handed you. This letter does not replace the inspector's own record and never carries his numbering."
        },
        {
          "h": "THE INTERLOCKS WE COULD NOT RUN",
          "r": "One line each, and ONLY the ones the tech named: what could not be demonstrated, why not, and the trade and company that owns it. Never name an interlock nobody has on this job — the GC will use that line to say we were never ready."
        },
        {
          "h": "WHAT HAS TO BE TRUE ON TEST DAY",
          "r": "The building conditions, not the people: ceilings closed, power on and staying on, access and keys, escort, elevators running. Say how long the walk takes so nobody puts it at three in the afternoon."
        },
        {
          "h": "WHAT WE ARE ASKING FOR",
          "r": "One ask, one date: schedule on or after it, or tell us in writing to walk it as-is knowing the interlocks above will not run. Nothing else in this section."
        }
      ],
      "omit": "Every other trade that has to be standing in the building on test day, named by trade and by company. Nobody writes 'the elevator mechanic has to be here', so recall never gets demonstrated, the walk fails, and it lands on the fire alarm contractor's card — a re-inspection and two weeks, for somebody else's man not being there.",
      "needs": ["who"],
      "halt": "Only stop and ask if you cannot tell whether the pretest has actually been run or is still planned. Never write up a test that has not happened.",
      "facts": [
        "building name and address",
        "the permit or case number as the GC or the inspector's office wrote it",
        "exactly what scope is being offered",
        "pretest dates, who ran it, who watched",
        "what was operated, and any count the tech stated himself",
        "every interlock the tech named that could not be run, and whose trade owns it",
        "the building conditions needed on test day",
        "which trades and companies have to be there",
        "the date we are asking for, and who schedules it"
      ],
      "secondary": [
        "a short scheduling email to the GC",
        "the trade list on its own, sent to the super",
        "a re-offer letter once the missing trades are done"
      ]
    },
    {
      "id": "ahj-correction-response",
      "name": "Correction Notice Response",
      "aka": [
        "answering the fire marshal",
        "correction letter",
        "re-inspection request",
        "violation response",
        "notice of correction reply"
      ],
      "family": "verification",
      "from": "the foreman who did the corrections",
      "to": "the permit holder and the inspector",
      "why": "Answer his list in his order with his numbers, or you get the same list back.",
      "sections": [
        {
          "h": "THE NOTICE WE ARE ANSWERING",
          "r": "First two lines: building name and address, and the permit or case number exactly as HE wrote it. Then his name and the date of his notice. His paper owns the numbering — we quote it and never renumber it."
        },
        {
          "h": "ITEM BY ITEM",
          "r": "One short paragraph per item, in HIS order, none skipped: his item number, enough of his own words to know which item it is, what was done, who did it, and the date it was done. Quote his description, not any code section he cited — if his wording is only a code cite, use his item number on its own. If an item is not clear, say we are asking him to clarify it; never answer a question he did not ask."
        },
        {
          "h": "STILL OPEN",
          "r": "His number, what is holding it — a part, access, another trade — and the date it will be done. A date, not ASAP."
        },
        {
          "h": "RE-INSPECTION",
          "r": "What we are asking him to walk, on or after a date, who to call for access and keys, and how long the walk takes. Never assume he will take photos instead of walking it."
        }
      ],
      "omit": "The items that are NOT ours — answered anyway, with the trade and the company that owns each one and who is answering it. An unanswered item on his list reads as 'not corrected' no matter whose scope it was, and the whole re-inspection gets pushed over somebody else's damper.",
      "needs": ["who", "notdone"],
      "halt": "Only stop and ask if you do not have the inspector's own item numbers — without his numbering this cannot be answered against his list, and it is worth going and getting the notice. If it comes in as a phone photo, read the numbers off the photo and quote them as they sit: never re-sequence them, never tidy them up.",
      "facts": [
        "building name and address",
        "the permit or case number as he wrote it",
        "the inspector's name and the date of his notice",
        "his item numbers and his own wording",
        "what was done for each item, by whom, on what date",
        "which items belong to another trade, and who is answering them",
        "which items are still open and the date they will be done",
        "the date we want the re-inspection, and who has access"
      ],
      "secondary": [
        "a cover email to the permit holder or GC",
        "a chase list of the items other trades still owe",
        "a second response after the next walk"
      ]
    }
  ],
  "overrides": {
    "daily-report": {
      "name": "Daily Field Report",
      "aka": [
        "daily",
        "dfr",
        "end of day",
        "eod",
        "field report",
        "daily update",
        "what we got done today"
      ],
      "why": "The one your PM forwards. On this trade it is also the only record of what got buried today — once the lid is up nobody can go back and look.",
      "sections": [
        {
          "h": "SITE, DATE AND WHO WAS ON IT",
          "r": "First two lines: building or site and the date. Then the job number, who was there and how many hours each. A PM finds this a year later by searching the site name, not by searching 'daily'."
        },
        {
          "h": "WHAT WE PULLED, TERMINATED AND TESTED — BY AREA",
          "r": "By floor, room or area as it is labelled in the field, and devices by their field tags. Write what he said it did; never write pass, fail, in range or to code, and never a count he did not give you."
        },
        {
          "h": "WHAT WE COULD NOT GET TO, AND WHY",
          "r": "Locked rooms, no grid, no power, another trade standing in it, a tenant who would not open. Name the area, the reason, and who holds the key."
        },
        {
          "h": "WHAT IS ON TEST OR LEFT BYPASSED RIGHT NOW",
          "r": "Any point disabled, jumpered, or an account left on test — named, with the clock time it went that way. Carry it forward on every daily until it is back to normal. The day it stops appearing is the day it becomes somebody's surprise."
        },
        {
          "h": "WHAT WE NEED TOMORROW",
          "r": "Access, another trade's work, a delivery, a decision — each with who owes it and the date we asked."
        }
      ],
      "omit": "What got covered over today — the ceiling that closed, the wall that got rocked, the trench backfilled over our pathway — with the time and where the photo lives. Everything else on this report can be rebuilt next week. That cannot.",
      "needs": ["when", "where"],
      "halt": "Only if this is the first report in the thread and there is no job number or site at all.",
      "facts": [
        "date",
        "job number / site",
        "who was on it and how many hours",
        "what got pulled, terminated or tested, and where",
        "what could not be reached and why",
        "anything left on test, bypassed or on a temporary program",
        "what we need tomorrow and who owes it"
      ],
      "secondary": [
        "a weekly rollup from the dailies in this thread",
        "a short version for the GC with the internal detail stripped"
      ]
    },
    "service-writeup": {
      "name": "Service Call Write-Up",
      "aka": [
        "service",
        "call",
        "trouble call",
        "service report",
        "work order narrative",
        "repair",
        "trouble ticket narrative"
      ],
      "why": "The customer reads this and decides whether to pay for what comes next. On a life-safety system it is also the only paper that says what state you left the panel in.",
      "sections": [
        {
          "h": "SITE, DATE AND THE TICKET",
          "r": "First two lines: building name and address, and the date you were on site. Then the system, the panel location, and the ticket number as dispatch numbers it — quoted, never renumbered. This is the story that goes with the ticket; it never retypes what the ticket already holds."
        },
        {
          "h": "WHAT IT WAS DOING WHEN WE GOT THERE",
          "r": "The complaint in the customer's own words, and what the panel or head end was actually showing — quoted off the display or the history word for word, point address and all. Not tidied up, not paraphrased."
        },
        {
          "h": "WHAT WE DID",
          "r": "In the order it happened, in plain words: what was checked, what was opened, what was swapped, what was reprogrammed. Record what he measured exactly as he gave it, units and all; never say whether it was good, bad or to code."
        },
        {
          "h": "HOW WE LEFT IT",
          "r": "Normal, in trouble, or with something disabled, bypassed, jumpered or on test — say which, name the point, and say whether it is still that way as you write. If the account is still on test, say who at the monitoring center has it and that the call to take it off is still owed."
        },
        {
          "h": "WHAT STILL NEEDS DOING",
          "r": "What is left, who has to approve it, and what has to be true before we can come back — access, a part, another trade. No prices."
        }
      ],
      "omit": "The point you did not get to, and why — the locked tenant space, the hard lid nobody would open, the thing you found on another zone that is not on this ticket. Silence on it reads as 'he checked it and it was fine', and the next man inherits it as yours.",
      "needs": ["notdone"],
      "halt": "Only if there is no statement of what the complaint was.",
      "facts": [
        "site, date, and the ticket number as dispatch wrote it",
        "the complaint as reported",
        "what the panel or head end was showing, word for word",
        "what you did",
        "what it is doing now",
        "the state you left the system in, and anything still bypassed or on test"
      ],
      "secondary": [
        "a customer-facing version with the internal notes stripped",
        "a quote request to the office for the follow-up"
      ]
    }
  },
  "drop": [],
  "vocab": [
    "nack -> NAC",
    "slick -> SLC",
    "enunciator -> annunciator",
    "supervisor signal -> supervisory signal",
    "duck detector -> duct detector",
    "f a c p -> FACP",
    "e o l -> EOL",
    "age h jay -> AHJ",
    "firewatch -> fire watch",
    "wiggen -> Wiegand",
    "proxy card -> prox card",
    "r e x / rex -> REX",
    "n v r / envy are -> NVR",
    "d marc / dee mark / demark -> demarc",
    "i d f -> IDF",
    "m d f -> MDF",
    "cat six a -> Cat6A",
    "cat six -> Cat6",
    "punch down -> punch-down",
    "s m / m m -> singlemode / multimode"
  ],
  "reminders": [
    "A cable, a reading or a device is about to disappear behind somebody else's work — a hard lid going up, rock going on, a slab poured, a trench backfilled -> remind me to get the photo and the cable label recorded before it closes, and where the photos live.",
    "Devices are tested -> remind me to say WHICH ones, and which ones could not be reached and why. A test record with no boundary is worthless.",
    "Anything is left on a temporary program or a default password, or keys, installer codes or admin logins change hands -> remind me to name it, date it and record who took it in the open items — and never to type the actual code into the document.",
    "Anything is bypassed, disabled, jumpered or put on test -> remind me to write the clock time, the name at the monitoring center and the reference number they gave me, and to set my own reminder for the call that takes it back off.",
    "An acceptance test, fire marshal walk or inspection date comes up -> remind me to name every trade that has to be standing there for the interlocks. A recall that never gets run lands on our card, not theirs."
  ]
};
