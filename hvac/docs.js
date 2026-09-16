/* HVAC/R FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about HVAC and refrigeration work and nothing else.
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
  "trade": "HVAC and refrigeration",
  "docs": [
    {
      "id": "red-tag-notice",
      "name": "Red Tag — Equipment I Took Out of Service",
      "aka": [
        "red tag",
        "condemned it",
        "shut down notice",
        "unsafe condition letter",
        "gas shut off notice",
        "locked it out",
        "danger tag",
        "took it out of service"
      ],
      "family": "notice",
      "from": "the tech who shut it down",
      "to": "the building owner or property manager",
      "why": "Puts in writing that you took the unit out of service, what you found, and that leaving it off is now their call and not yours.",
      "note": "narrative only — the tag on the unit and the utility's or fire department's own paperwork are not this",
      "sections": [
        {
          "h": "UNIT I TOOK OUT OF SERVICE",
          "r": "Building and address, the date, unit tag, where it sits, and what space or tenant it serves. Then what you physically did — gas valve closed, disconnect opened and tagged, breaker off, stat isolated. Not 'shut the unit down'."
        },
        {
          "h": "WHAT I FOUND",
          "r": "The defect in plain words and exactly where it is. Only what you saw and what your own instrument read, with the instrument named. No target, no range, no typical, no rule of thumb — not even in brackets. Nothing here grades your reading."
        },
        {
          "h": "WHY I SHUT IT OFF",
          "r": "Your call, in your own words: what you saw and that you were not willing to leave it running. Do not reach for a limit, an acceptable level, a code section or an automatic verdict. You are stating a decision you made, not a finding against somebody's standard."
        },
        {
          "h": "WHAT THE SPACE IS WITHOUT NOW",
          "r": "What loses heat or cooling, whether anybody is in it, and whether temporary equipment is wanted. If it's occupied, say so in the first line of this block."
        },
        {
          "h": "WHAT IT TAKES TO PUT IT BACK",
          "r": "Repair or replace, what has to happen first, and who is allowed to pull the tag. Say flat that the tag stays until that work is done and your shop clears it."
        },
        {
          "h": "IF SOMEBODY PULLS THE TAG",
          "r": "One flat paragraph: if anyone restores power or gas before the work is done, it is not on you and not on your company. Factual. No threats and no lawyer talk."
        }
      ],
      "omit": "The time you shut it off and the name of the human you handed it to — title, phone or in person, plus anybody you tried and couldn't reach. A red tag with no time and no named person turns into 'we were never told' the second a tenant freezes, and if you closed the gas valve, write that you closed the gas valve.",
      "needs": ["when", "who", "change"],
      "halt": "Only stop and ask if it isn't clear what you physically did to take it out of service — gas off, disconnect open, breaker off, locked — because that one sentence carries the whole document.",
      "facts": [
        "Building, address and the date",
        "Unit tag, where it sits, and what space or tenant loses heat or cooling",
        "What you found and how you found it — visual, combustion analyzer, leak detector, camera, manometer, pressure test",
        "Any reading you took and what you took it with — your number, nothing graded",
        "What you physically did: gas valve closed, disconnect open, breaker off, tagged, locked",
        "The time you shut it off",
        "Who you told, their title and how, plus anybody you tried and couldn't reach",
        "Whether the space is occupied and whether temporary equipment is wanted"
      ],
      "secondary": [
        "the short text you send the property manager right then",
        "a heads-up email to your service manager"
      ]
    },
    {
      "id": "compressor-failure-report",
      "name": "Compressor Failure Narrative — For the Warranty Claim",
      "aka": [
        "comp failure write up",
        "warranty narrative",
        "burnout report",
        "compressor claim",
        "failed comp story",
        "warranty write up",
        "what killed the compressor",
        "compressor changeout",
        "comp changeout"
      ],
      "family": "incident",
      "from": "the tech who changed the compressor",
      "to": "the warranty desk",
      "why": "The paragraph that gets the claim paid instead of denied, because it shows you found what killed it and didn't just hang a new one on the same problem.",
      "note": "narrative only — the claim form, its fields and its claim number belong to the warranty desk",
      "sections": [
        {
          "h": "UNIT AND COMPRESSOR",
          "r": "One line, not a paragraph: site, date, unit tag, and the failed and replacement compressor serials. You already typed the plate into their form and nobody wants it twice. If a serial is unreadable, write unreadable — never guess one."
        },
        {
          "h": "WHAT IT WAS DOING WHEN I GOT THERE",
          "r": "What the call came in as and what the unit was doing when you walked up. Locked rotor, open windings, tripped on the internal, grounded, running and not pumping — say which, and say what you measured to get there. Your numbers, nothing graded."
        },
        {
          "h": "WHAT KILLED IT",
          "r": "The cause you found, not the symptom, and what you found it with. If you genuinely don't know, write unknown and list what you ruled out — an honest undetermined beats a guess the teardown contradicts. Don't call the part defective or worn out by design; say what you found."
        },
        {
          "h": "OIL AND ACID",
          "r": "What the oil looked and smelled like, what the acid test showed, whether the suction line and accumulator were contaminated, and how far the burn travelled. Your test and your call — nothing here says pass or fail."
        },
        {
          "h": "STARTUP AFTER REPAIR",
          "r": "The readings after it ran and the ambient you took them in, plus what mode you left it in. Every value is yours. No target, no range, no typical, no rule of thumb — not even in brackets."
        },
        {
          "h": "PARTS RETURN",
          "r": "One line: where the old comp went, the return reference if they issued you one, whether you kept an oil sample, and the ship date. Never invent a return number or a claim number — those come from them. Leave it blank if you don't have it."
        }
      ],
      "omit": "Proof you fixed the CAUSE and not just the compressor: drier changed, lines flushed, metering device checked or replaced, contactor and electrical corrected, condenser cleaned, charge weighed in instead of gauged in — and what you deliberately left alone. Claims die on the sentence you didn't write; 'replaced compressor, evacuated, charged' with no drier in it reads to the desk like the next one is already coming.",
      "needs": ["change", "notdone"],
      "halt": "Only stop and ask if there is no model and serial off the failed compressor at all, because the claim can't be filed without it.",
      "facts": [
        "Site, date and unit tag",
        "Failed compressor model and serial, and the replacement's",
        "How old the unit is or when it was started, if you know",
        "Electrical readings off the failed comp — windings, to ground, amps at failure. Your numbers, nothing graded",
        "What the oil and the acid test showed, and what you tested with",
        "Every part you replaced and every part you deliberately did not",
        "Post-repair readings and the outdoor ambient when you took them",
        "Where the old compressor went and any return reference they gave you"
      ],
      "secondary": [
        "a plain paragraph for the customer on what failed and why",
        "an internal note to the service manager if this site keeps eating compressors"
      ]
    },
    {
      "id": "refrigerant-leak-narrative",
      "name": "Leak Found and Repaired — Write-Up for the Customer",
      "aka": [
        "leak repair write up",
        "found the leak",
        "loss of charge report",
        "leak search narrative",
        "gas loss write up",
        "low on charge write up",
        "leak repair report",
        "refrigerant leak",
        "refrigerant",
        "lost its charge"
      ],
      "family": "incident",
      "from": "the tech who chased the leak",
      "to": "the customer or property manager paying for it",
      "why": "Says why the unit went flat, what you actually fixed, and what happens if it goes flat again, so a second leak isn't automatically yours.",
      "note": "the leak search and the repair — a straight recharge with nothing found goes on the service write-up",
      "sections": [
        {
          "h": "UNIT AND WHY WE WERE THERE",
          "r": "Building and address, the date, unit tag, refrigerant type off the plate, and the complaint: low on charge, iced up, tripping on low pressure, short cycling, not holding box temp."
        },
        {
          "h": "CHARGE FOUND AND CHARGE PUT BACK",
          "r": "What was in it when you got there, what you recovered, what you weighed in, and the nameplate charge. All measured, all yours — never fill one in off a chart and never back-figure one from the others. If it wasn't measured, write that it wasn't measured. No leak rate, no percentage of charge, no yearly loss figure: that number carries a regulatory trigger and it lives in your shop's compliance system, not in this letter."
        },
        {
          "h": "HOW I FOUND IT AND WHERE",
          "r": "How you searched — detector, bubbles, dye, nitrogen and soap, standing pressure — and every place you found it, exactly where. If you pressure tested, give your pressure and your hold time. Say if you think there are more you couldn't get to."
        },
        {
          "h": "WHAT I REPAIRED",
          "r": "The physical repair: brazed, section replaced, cores replaced, coil replaced, line re-supported. Whether you purged with nitrogen while brazing, whether you pressure tested after, what vacuum you pulled and whether it held. Your numbers."
        },
        {
          "h": "WHY IT LEAKED AND WHAT I EXPECT NEXT",
          "r": "Why it went, in your own words and in field words — what you actually saw at the leak, not a cause picked off a list. Then the honest forecast: whether this coil or this system is going to leak again, and what that means for repair against replace. This is where you cover yourself on the callback."
        },
        {
          "h": "WHAT I COULDN'T CHECK",
          "r": "Buried linesets, coils you can't get behind, rack sections under load, joints inside a sealed cabinet. Say it plainly instead of letting the silence imply you checked it."
        }
      ],
      "omit": "One flat sentence saying whether the leak was REPAIRED or only LOCATED. Customers hear 'we fixed the leak' when you meant 'we topped it off until the coil comes in' — three weeks later the recharge is on your dime because nothing in writing said different.",
      "needs": ["none"],
      "halt": "Only stop and ask if it isn't clear whether the leak was actually repaired or the system was just recharged, because the whole liability turns on which one this is.",
      "facts": [
        "Building, address, date, unit tag and refrigerant type off the plate",
        "Nameplate charge, weight recovered and weight charged back in — measured, not guessed",
        "How you searched and where you searched",
        "Exact leak location or locations you found",
        "Standing pressure and hold time, if you tested",
        "What vacuum you pulled and whether it held",
        "Readings after the repair and the ambient you took them in",
        "Anything you could not get to or verify"
      ],
      "secondary": [
        "a repair-against-replace paragraph for the owner",
        "a heads-up to the salesman if the coil is on borrowed time"
      ]
    },
    {
      "id": "temp-excursion-report",
      "name": "Box Went Warm — What Happened and When",
      "aka": [
        "product loss report",
        "box went down",
        "temp excursion",
        "cooler down report",
        "freezer failure write up",
        "food loss letter",
        "case out of temp",
        "rack alarm write up"
      ],
      "family": "incident",
      "from": "the refrigeration tech who caught the call",
      "to": "the store manager",
      "why": "The clock that decides whether the product loss gets paid, and whether the failure lands on the equipment, the store, or you.",
      "note": "narrative only — the loss claim form is the store's and the insurer's to fill out",
      "sections": [
        {
          "h": "STORE, BOX AND WHAT'S IN IT",
          "r": "Store and address, the date, which box or case, what rack or condensing unit feeds it, which suction group, and roughly what product is in it. One block per box if more than one went out — never blend them."
        },
        {
          "h": "TIMELINE",
          "r": "Times in order, each one with where it came from: when you were called, when you were dispatched, when you got there, when it came back to temp. Say the source — dispatch, controller history, your phone. Write approx. if it's approximate. Never quietly estimate."
        },
        {
          "h": "TEMPERATURES",
          "r": "Product temp and box or discharge air temp when you got there and after recovery, and how each was taken — probe, IR, the store's own controller log. Every temperature is yours. Nothing here says what is safe to hold and nothing here says pass or fail. No target, no range, no typical, no rule of thumb, not even in brackets."
        },
        {
          "h": "WHAT I FOUND WRONG",
          "r": "What you actually found on the mechanical or control side and what reading confirmed it. What you found — not what you assume, and not a cause picked off a list."
        },
        {
          "h": "WHAT I DID AND HOW I LEFT IT",
          "r": "The repair, anything temporary — spare condensing unit, ice, product moved to another box — how it's running now, and what's still on order."
        },
        {
          "h": "THE PRODUCT",
          "r": "What you saw about the product, and who decided to keep it or dump it, by name and title. Say plainly that the store made that call and you did not. You report temperatures; you don't condemn food."
        }
      ],
      "omit": "The alarm history — when the box first alarmed against when a human actually called it in, whether the dialer or the monitoring was even working, and whether alarms had been silenced or setpoints widened. Loss claims live or die in that gap. If you don't write that it alarmed at 11pm and nobody called until 7am, the whole loss defaults onto the last man who touched the equipment, which is you.",
      "needs": ["when", "count", "change"],
      "halt": "Only stop and ask if you have neither an arrival time nor a time it came back to temp, because an excursion write-up with no clock in it is useless to everybody who reads it.",
      "facts": [
        "Store, address and the date",
        "Box or case ID, the rack or condensing unit feeding it, and the suction group",
        "When you were called, dispatched, on site, and when it came back to temp — with the source of each",
        "Product temp and air temp at arrival and after recovery, and how each was taken",
        "What you found wrong and the reading that confirmed it",
        "Whether monitoring and alarming were working, and whether any setpoints or alarms had been changed",
        "Temporary measures taken and what's still on order",
        "Name and title of whoever decided to keep it or dump it"
      ],
      "secondary": [
        "a times-only version the store can hand its adjuster",
        "a note to the account manager if this store keeps going down"
      ]
    },
    {
      "id": "comfort-complaint-investigation",
      "name": "Hot Call — What I Measured and What It Actually Is",
      "aka": [
        "hot call",
        "cold call",
        "no cooling in 210",
        "too hot too cold",
        "comfort complaint",
        "nothing found wrong",
        "third trip same suite",
        "tenant says it's hot"
      ],
      "family": "verification",
      "from": "the tech sent back on it",
      "to": "the property manager who has to answer the tenant",
      "why": "Proves the equipment is doing its job when the building isn't, so you stop getting sent back for free.",
      "note": "for the repeat call — third trip, same suite, same complaint. A one-off goes on the service write-up",
      "sections": [
        {
          "h": "THE SUITE AND THE COMPLAINT",
          "r": "Building and address, the date, the suite and tenant, which unit or zone serves it, the complaint in their words, what time of day it happens, and whether it's every day or only some days. If it's only afternoons on the west side, that sentence goes right here."
        },
        {
          "h": "WHAT I MEASURED",
          "r": "Space temp and where you stood, stat or sensor reading, supply and return at the unit and at the diffuser, air at the register, filter and coil condition, static if you took it, damper and economizer position, setpoints and schedule as actually programmed. Every number is yours and nothing here grades it — no target, no range, no typical, no rule of thumb, not even in brackets."
        },
        {
          "h": "WHAT THE EQUIPMENT IS DOING",
          "r": "The call on the machine in one line before you explain it: making split or not, staging or not, air at the box or not, economizer working or stuck."
        },
        {
          "h": "WHAT'S ACTUALLY CAUSING IT",
          "r": "When the machine is doing its job, say what in the space is doing it — what you saw with your own eyes, not a cause off a list and not a guess. Say it plainly without insulting anybody."
        },
        {
          "h": "WHAT WOULD ACTUALLY FIX IT",
          "r": "Split it three ways: what a service call can do, what is a project, and what belongs to the tenant or the landlord. Be specific — 'move the sensor off the west wall' beats 'improve control'. No prices."
        },
        {
          "h": "WHAT I DID THIS TRIP",
          "r": "What you adjusted, cleaned or reprogrammed, what the space read when you walked out, and whether the tenant was told and by who."
        }
      ],
      "omit": "Outdoor ambient and the time of day beside every space temperature you wrote down, plus what was going on in the room — people, glass, lights, doors propped. '76 in the suite' proves nothing. '76 in the suite, 97 outside, 3:40pm, full sun, 22 people in an open plan' is the write-up that ends the callback cycle.",
      "needs": ["when", "count"],
      "halt": "Only stop and ask if there is no measured space temperature at all, because a comfort complaint with no temperature in it is just an opinion.",
      "facts": [
        "Building, address, date, suite and tenant, and which unit or zone serves it",
        "The complaint in their words and when it happens",
        "Outdoor ambient and the time you took each reading",
        "Space temp, stat or sensor reading, and where each was taken",
        "Supply and return at the unit and at the diffuser",
        "Air at the register or static, if you took it, plus filter and coil condition",
        "Setpoints and schedule as actually programmed, and damper or economizer position",
        "What's going on in the space: people, glass, equipment load, blocked diffusers, propped doors, where the sensor sits"
      ],
      "secondary": [
        "a paragraph the property manager can forward straight to the tenant",
        "a TAB scope so a balancer can get out here"
      ]
    },
    {
      "id": "startup-narrative",
      "name": "Startup Narrative — What It Was Started Under and What Isn't Right",
      "aka": [
        "startup write up",
        "start up letter",
        "startup deficiency list",
        "commissioning narrative",
        "start-up narrative",
        "SU write up",
        "what it was started under"
      ],
      "family": "verification",
      "from": "the startup tech",
      "to": "the GC's project manager",
      "why": "Puts on paper what was and wasn't right the day the equipment first ran, so nobody gets to rewrite that day twelve months later.",
      "note": "narrative only — the manufacturer's startup form and the commissioning agent's reports stay theirs",
      "sections": [
        {
          "h": "UNIT AND DATE STARTED",
          "r": "Job and address, unit tag, model and serial, the date and time it was first started, and who was standing there. One block per unit — never blend two units into one narrative."
        },
        {
          "h": "CONDITIONS AT STARTUP",
          "r": "The honest state of the building that day: permanent or temporary power, measured voltage and phase, duct complete or open, filters in or not, ceiling in or out, controls live or in hand, water treatment in or not, building closed in or not. This paragraph is the whole reason the document exists, and it goes above the readings, not under them."
        },
        {
          "h": "THE READINGS I'M CITING",
          "r": "Only the readings you are actually leaning on here — the ones that back a deficiency or prove what it was doing. The full grid already went on their startup sheet field for field and nobody is retyping it. Every value is yours; no target, no range, no typical, no rule of thumb, not even in brackets, and nothing here says whether it passes."
        },
        {
          "h": "DEFICIENCIES AND WHO OWNS EACH",
          "r": "What is wrong right now and whose it is: shipping damage, missing parts, wrong voltage supplied, curb not sealed, duct not connected, condensate not run, no disconnect, controls not terminated, sensors not in. What it takes to close each one, and a name against it."
        },
        {
          "h": "HOW IT WAS LEFT",
          "r": "Running or shut down, what mode, setpoints, what you locked out and why, and whether you handed it to the GC or left it off and secured."
        }
      ],
      "omit": "Everything you could NOT verify that day and why — heat not run in July, economizer not proved with dead controls, no load to test against, drive not commissioned — plus what you'd need on a return trip to close each one. Silence reads as verified, and twelve months later the packed coil and the gone bearings become yours.",
      "needs": ["notdone"],
      "halt": "Only stop and ask if you can't tell whether the unit was actually started and run or only powered up and looked at, because those are two different documents.",
      "facts": [
        "Job, address, unit tag, model and serial off the plate",
        "Date and time it was first started, and who was there",
        "Permanent or temporary power, and measured voltage on each leg",
        "Whether filters were in and whether the duct was complete and connected",
        "The readings you're citing, plus the ambient when you took them",
        "Every deficiency found and the name that owns it",
        "Anything you could not verify and why",
        "How the unit was left and who you handed it to"
      ],
      "secondary": [
        "a deficiency-only email to the GC",
        "the cover note that goes with the manufacturer's startup paperwork"
      ]
    },
    {
      "id": "temp-conditioning-release",
      "name": "Temp Heat Letter — Running the New Units for the GC",
      "aka": [
        "temp heat letter",
        "temp heat release",
        "running the units for the GC",
        "temporary conditioning letter",
        "construction heat letter",
        "temp cooling letter",
        "early startup letter"
      ],
      "family": "notice",
      "from": "the mechanical foreman",
      "to": "the GC",
      "why": "Lets the GC run your new equipment for temporary conditioning without the coils and the clean-up quietly becoming yours.",
      "sections": [
        {
          "h": "WHAT THEY WANT TO RUN AND WHY",
          "r": "Job and address, the date, which units, what for — drywall, mud and tape, flooring, paint — and the date range they want. Name who asked, by name and company."
        },
        {
          "h": "WHAT HAS TO BE TRUE BEFORE IT RUNS",
          "r": "Numbered plain sentences: construction filtration in, returns ducted or filtered, permanent power at the right voltage and phase, condensate run and trapped, gas piping tested, and a named man on the GC's side. Never name a filter rating or a MERV number — you say what filter goes in it. Spec his material and you own his warranty."
        },
        {
          "h": "WHAT WE WILL AND WON'T STAND BEHIND",
          "r": "Flat sentences on your own position: dirt, packed filters, plugged wheels and damage from running in an unfinished building are not our repair and they come back billable. Don't state what the manufacturer's coverage does or when it starts — that is theirs to say, and if it matters, get it from them in writing."
        },
        {
          "h": "WHAT WE'LL DO AT TURNOVER, AND WHOSE NUMBER IT'S IN",
          "r": "New filters, coil clean, belts, blower wheel clean, re-check the charge, re-commission — then say straight whether that is in your base number or extra. This is the sentence that becomes a change order."
        },
        {
          "h": "IF IT RUNS ANYWAY WITHOUT THIS",
          "r": "What you'll actually do if it runs with open duct or nobody changes a filter: put it in writing the day you see it, say whether you shut them down or keep going, and say the clean-up and the repairs go on a ticket. Say it now, not at turnover."
        }
      ],
      "omit": "Who buys and changes the construction filters, how often, and who logs it — by name, not by company. Everybody agrees temp heat is fine and nobody names a filter owner. At turnover you're pulling packed filters and plugged blower wheels out of six units and eating a coil clean that was never in your number.",
      "needs": ["who", "count"],
      "halt": "Only stop and ask if it isn't stated whether it will run on permanent or temporary power, because that one fact changes both the risk and the letter.",
      "facts": [
        "Job, address and the date",
        "Unit tags they want to run and what the temp conditioning is for",
        "The date range asked for, and who asked, by name and company",
        "Permanent or temporary power, and confirmed voltage and phase",
        "Whether construction filtration is on site and who supplies it",
        "Whether the duct is complete or the returns are open",
        "Whether condensate is run and trapped and gas piping is tested",
        "What your contract already includes for turnover cleaning and filters"
      ],
      "secondary": [
        "a short email version for the GC to acknowledge back",
        "a filter-change reminder note to hand the site super"
      ]
    }
  ],
  "overrides": {
    "service-writeup": {
      "name": "Service Call Write-Up — What I Found, What I Did",
      "aka": [
        "ticket write up",
        "service ticket narrative",
        "call write up",
        "what I did on the call",
        "the narrative box",
        "job story",
        "tech notes",
        "no heat",
        "no cool",
        "no cooling",
        "iced up",
        "first trip",
        "recharge",
        "topped it off",
        "service call",
        "trouble call"
      ],
      "why": "The narrative that goes in the ticket box — what the unit was doing, what you did about it, and what is still open, in words the customer can still read a year from now.",
      "sections": [
        {
          "h": "UNIT AND WHY I WAS THERE",
          "r": "Building and address, the date, unit tag and where it sits, and the complaint the way it was called in. One block per unit — never blend two units into one write-up."
        },
        {
          "h": "WHAT IT WAS DOING WHEN I GOT THERE",
          "r": "What you walked up to: running, locked out, iced, tripped, no call for cooling, nobody home. What you saw, not what you figured on the drive over."
        },
        {
          "h": "WHAT I FOUND",
          "r": "What you found and what you found it with, instrument named. Every reading is yours and nothing here grades it — no target, no range, no typical, no rule of thumb, not even in brackets."
        },
        {
          "h": "WHAT I DID ABOUT IT",
          "r": "Parts on and parts off, what you cleaned, what you adjusted, what you reprogrammed. Say what you left running and in what mode."
        },
        {
          "h": "HOW IT WAS WHEN I LEFT",
          "r": "Operating condition when you walked away, what the space or the box was reading, and who on site you told, by name."
        }
      ],
      "omit": "What you did NOT do, and why — the part on order, the second unit you never opened, the roof hatch you couldn't get to, the check you couldn't finish because the store wouldn't let you shut the case down. The customer remembers the sentence you left out, and next trip it turns into the thing you missed.",
      "needs": ["notdone"],
      "halt": "Only stop and ask if it isn't clear whether the unit was left running or left down, because everybody who reads this needs that in the first line.",
      "facts": [
        "Building, address and the date",
        "Unit tag and where it sits, plus the complaint as called in",
        "What it was doing when you walked up",
        "What you found and what you found it with — your readings",
        "Parts on, parts off, and what you cleaned or adjusted",
        "How it was left: running or down, and in what mode",
        "Who on site you told, by name",
        "Anything you could not do, and why"
      ],
      "secondary": [
        "the short text you send the property manager the same day",
        "a heads-up to the service manager if this is the second call on the same unit"
      ]
    },
    "damage-found": {
      "name": "It Was Like That When I Got Here — The Unit Before I Touched It",
      "aka": [
        "pre-existing",
        "already like that",
        "not us",
        "previous contractor",
        "somebody else's work",
        "existing condition",
        "before I touched it",
        "found it this way",
        "found damage",
        "prior damage",
        "damage"
      ],
      "from": "the tech who opened the unit",
      "to": "the property manager or the GC's super, and my own service manager",
      "why": "Puts on paper what the equipment was like before you put a hand on it — the burned contactor, the kinked lineset, the coil somebody else cut, the missing disconnect, the readings as found — so the next failure on that unit is not automatically yours.",
      "note": "the condition you FOUND, not a repair you made or a recommendation — those go on the service write-up and the repair recommendation; on startup day, shipping and site damage goes on the Startup Narrative. This is the photo-with-words you send before you start",
      "sections": [
        {
          "h": "UNIT AND WHEN I OPENED IT",
          "r": "Building and address, the date and time, unit tag, where it sits, and why you were there. Then the sentence this whole document hangs on: what you found, exactly as found, before you did anything to it. One block per unit — never blend two units."
        },
        {
          "h": "WHAT WAS ALREADY LIKE THAT",
          "r": "Each thing, where it is, and how you can tell it was there before you: a contactor pitted black, a lineset kinked at the wall, a coil cut and taped, a condensate line run uphill, a disconnect gone, a flue pulled apart, a splice hanging outside the box. Say what you saw. Do not say who did it and do not call it wrong against a standard — only that it was like this when you got here."
        },
        {
          "h": "THE READINGS AS FOUND",
          "r": "Only the readings that prove the condition was there before you — taken before you touched anything, what you took them with, and the ambient. The rest of the trip's readings go on the service write-up. No target, no range, no typical, no rule of thumb — not even in brackets. Nothing here grades your number."
        },
        {
          "h": "PHOTOS",
          "r": "Where the photos are — how many, taken when, and where they live — so the picture that proves this can be found in a year, not described from memory. If there are no photos, say so."
        },
        {
          "h": "WHAT I DID AND DID NOT TOUCH",
          "r": "What you were there to do — one line, and the write-up of it is on the ticket, not here. Then, plainly, what you left exactly as found and why — not in scope, not authorized, unsafe to run, waiting on a decision. A condition you found and did not write down is a condition you own."
        },
        {
          "h": "WHO I TOLD",
          "r": "Who you showed or told, by name and title, how, and when — before you started. If nobody was available, say who you tried."
        }
      ],
      "omit": "THE READINGS AND THE PHOTO TIMESTAMPS FROM BEFORE YOU TOUCHED IT, and the name of the person you told BEFORE you started. 'The compressor was already grounded' is a claim; 'grounded to case on arrival at 10:12, photo 3, told Marcus at the desk at 10:20' is a record. Without the before-value and the name, the next tech's finding on that unit is yours by silence.",
      "needs": ["before", "when", "who"],
      "halt": "Only stop and ask if it isn't clear what you found versus what you did — this document is the found condition only, and mixing in your repair turns your own evidence into an admission.",
      "facts": [
        "Building, address, date and time, and the unit tag",
        "Why you were there, and what the call came in as",
        "Each condition you found already there, and exactly where",
        "How you can tell it was there before you — corrosion, dust, tape, age, the previous tag",
        "The readings as found, what you took them with, and the ambient",
        "Where the photos are, how many, and when they were taken",
        "What you deliberately left as found, and why",
        "Who you told, by name and title, how, and when"
      ],
      "secondary": ["the short text you send the property manager with the photos before you start", "a heads-up to the office if this unit is going to be a fight"]
    },
    "change-request": {
      "name": "Why It's Extra — The Reason, Not the Number",
      "aka": [
        "extra",
        "extra work",
        "change order",
        "co",
        "COR",
        "out of scope",
        "not in our number",
        "not on the drawings",
        "why it's extra",
        "T and M narrative",
        "scope change",
        "change order write up"
      ],
      "from": "the mechanical foreman or the lead tech",
      "to": "the GC's PM, or the property manager who holds the agreement",
      "why": "The T&M tag gets the yes at the unit; this is the paragraph that gets the number paid two weeks later — what you found, why it isn't in the agreement or the drawings, and what it takes beyond the tag, in a form the PM can forward without calling you.",
      "note": "the reason, not the price and not the approval — the tag's GO/HOLD reply with a name and a time is the approval and the pricing sheet has the numbers. This letter carries neither",
      "sections": [
        {
          "h": "WHAT WE FOUND OR WERE ASKED TO DO",
          "r": "Job or site and address, the date, the unit tag or the area, then the work itself, physically: what you found on the roof or in the mechanical room, or what you were asked to add. Quantities and sizes as you know them. Never lead with the contract argument."
        },
        {
          "h": "WHO DIRECTED IT AND WHEN",
          "r": "Name, title, company, the date, and how it came — a walk, a text, an email, or verbally at the unit. If verbal, say verbal and say plainly this letter confirms it. If nobody directed it yet and you are asking, say that instead."
        },
        {
          "h": "WHY IT ISN'T IN OUR NUMBER",
          "r": "The specific basis: the drawing and revision the bid was on and what it showed, your own scope letter's exclusion, the agreement's list of covered equipment, or the field condition that was not there at bid — the curb that doesn't match the unit, the existing duct that doesn't match the new unit's connections, the gas line that isn't there, the electrical that isn't ours. Cite their documents by their own numbers only. Never cite a code section and never invent a document number."
        },
        {
          "h": "WHAT IT TAKES",
          "r": "Point at the T&M tag or tags by date — the men, hours, refrigerant and material are on the tag and do not get typed twice. Here only what no tag carries: the crane pick, the lift, the second trip, the controls point — and what you have to undo, recover, re-evacuate or re-start to do it."
        },
        {
          "h": "WHAT HAPPENS IF WE DON'T",
          "r": "The flat consequence: the unit sits, the space stays down, the startup slips, temp heat runs longer. No pressure language — one sentence of what is true."
        },
        {
          "h": "HOW WE'RE PROCEEDING",
          "r": "Either on hold pending the yes, or going ahead on T&M at a named person's direction. One or the other. Never both and never ambiguous."
        }
      ],
      "omit": "THE WORK YOU HAVE TO UNDO OR REDO TO DO THE EXTRA, on its own lines — the recovery and the re-evacuation, the second crane pick, the controls point that has to be re-commissioned, the startup you have to run again, the temp filters you go through twice. Everybody prices the new curb adapter and eats the two days of pulling the unit back off it.",
      "needs": ["count"],
      "halt": "Only stop and ask if it isn't clear whether the work is on hold or already going ahead — the letter reads completely differently and it can't say both.",
      "facts": [
        "Job or site, address, the date, and the unit tag or area",
        "What you found or were asked to do, physically, with quantities and sizes as known",
        "Who directed it — name, title, company, date, and how",
        "The drawing number and revision the bid was on, or the agreement's covered-equipment list, by its own number",
        "The field condition that drives it, if that's the reason",
        "The date of each T&M tag that carries the men, hours, refrigerant and material",
        "What has to come back out, be recovered, re-evacuated, re-tested or re-started",
        "What happens to the schedule or the space if it isn't done",
        "Whether the work is on hold or going ahead, and on whose direction"
      ],
      "secondary": ["the same-afternoon text confirming the verbal at the unit", "a one-paragraph version to paste into the GC's change form", "the short scope paragraph for the top of the pricing sheet"]
    },
    "handover": {
      "name": "Turned Over Running — The Day It Becomes Theirs",
      "aka": [
        "handover",
        "turnover",
        "closeout",
        "hand off",
        "handoff",
        "close out",
        "punch complete",
        "owner training",
        "warranty registration",
        "turned it over",
        "handed it over running",
        "O and M turnover"
      ],
      "from": "the mechanical foreman or the startup tech",
      "to": "the GC's PM and the owner's facilities lead",
      "why": "Fixes the day the equipment stopped being yours: what was running and in what mode, who has the controls and the keys, what paperwork changed hands, when filters and maintenance became theirs, and what is still open — so a filter nobody changed in month four does not come back as your compressor in month nine.",
      "note": "narrative only — the manufacturer's warranty registration, the commissioning agent's report and the GC's closeout log stay theirs; the day a unit was first run is the Startup Narrative, not this",
      "sections": [
        {
          "h": "WHAT IS BEING TURNED OVER, AND WHEN",
          "r": "Job and address, the date, the units by tag, and the areas or systems they serve. Say plainly what is NOT in this turnover — a unit still on temp power, a zone with controls not terminated, a chiller waiting on water treatment — because a list that reads complete turns each of them into warranty work."
        },
        {
          "h": "HOW IT WAS RUNNING WHEN I LEFT",
          "r": "Per unit: running or off, what mode, setpoints and schedule as programmed, what was locked out and why. New filters in or not, belts, condensate trapped and primed, charge as left. Every value is yours and nothing here grades it — no target, no range, no typical, no rule of thumb, not even in brackets."
        },
        {
          "h": "THE CLOCK",
          "r": "The date your labor warranty starts and ends. For the equipment: the date it was registered and where the registration lives — never its start, its end or what it requires; that is the manufacturer's to say. The date filter changes and maintenance became theirs, and who you told, by name."
        },
        {
          "h": "WHO HAS WHAT",
          "r": "What physically changed hands and to whom, by name, on what date: that the controls logins and codes were handed over — to whom and on what date, never the codes themselves — thermostat locks, panel and roof hatch keys, O&M manuals, as-builts or the controls points list, startup sheets, spare filters and belts, the refrigerant record. Training given — to whom, how long, what was covered."
        },
        {
          "h": "OPEN, AND KNOWN",
          "r": "Everything still open with its owner and date — a part on order with its lead time, a startup that could not be finished without load, a controls point waiting on the integrator, a punch item that belongs to another trade. Known and written is a punch list; found later is a callback."
        }
      ],
      "omit": "THE DATE FILTERS AND MAINTENANCE BECAME THEIRS AND WHO WAS TOLD, by name. Everybody writes the units and the setpoints; nobody writes 'filters and maintenance are the owner's from 03/14, our labor warranty runs from 03/14, equipment registered 03/14 with the confirmation in the job folder, told Dana Reyes, facilities.' Nine months later a packed filter, a plugged coil and a failed compressor are yours because no paper says which day they stopped being.",
      "needs": ["when", "who"],
      "halt": "Only stop and ask if you can't tell whether the units were handed over running or left off and secured — the two are different documents.",
      "facts": [
        "Job, address, the date, and every unit tag being turned over",
        "What each unit was doing when you left: mode, setpoints, schedule, lockouts",
        "Filters and belts as left, condensate as left, charge as left — your readings",
        "The date your labor warranty starts and ends; the date the equipment was registered and where",
        "The date maintenance and filters become theirs, and who you told",
        "What physically changed hands, to whom, on what date",
        "Who was trained, for how long, on what",
        "What is still open, who owns it, and any part on order with its lead time"
      ],
      "secondary": ["a one-paragraph email the PM can forward to the owner", "the note to the office with the registration confirmation and where the O&M binders went"]
    }
  },
  "drop": [],
  "vocab": [
    "condescending unit -> condensing unit",
    "condensor -> condenser",
    "texting valve -> TXV",
    "tee ex vee -> TXV",
    "are four ten a -> R-410A",
    "four fifty four bee -> R-454B",
    "our twenty two -> R-22",
    "are tee you -> RTU",
    "site glass -> sight glass",
    "liquid line dryer -> liquid line drier",
    "monometer -> manometer",
    "condensation line -> condensate line",
    "pee trap -> P-trap",
    "walking cooler -> walk-in cooler",
    "walking freezer -> walk-in freezer",
    "shiv -> sheave",
    "braised -> brazed",
    "crank case heater -> crankcase heater",
    "set point -> setpoint",
    "dead band -> deadband",
    "in thal pee -> enthalpy",
    "see eff em -> CFM",
    "lock out tag out -> lockout/tagout",
    "make up air unit -> makeup air unit (MAU)"
  ],
  "reminders": [
    "When a compressor changeout is mentioned -> ask whether the liquid line drier was replaced and whether an acid test was run, and get both into the narrative before it goes to the warranty desk.",
    "When a red tag, a closed gas valve or a lockout is mentioned -> ask for the time and the name of the person you told, and write what you physically did — valve closed, disconnect open, breaker off — not 'shut the unit down'.",
    "When the word contractor turns up anywhere near a contactor -> ask which one he means. Never swap it silently; 'contactor' in the wrong place in a letter going to the GC is worse than the typo.",
    "When a space temperature is given -> ask for the outdoor ambient and the time of day it was taken, or the reading proves nothing three months from now.",
    "When the GC wants to run the new units for temp heat -> ask who buys and changes the construction filters, how often, and whether the turnover coil clean is in the base number or extra."
  ]
};
