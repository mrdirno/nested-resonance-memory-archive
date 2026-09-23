/* AV FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about AV work and nothing else.
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
  "trade": "AV integration",
  "docs": [
    {
      "id": "commissioning-report",
      "name": "Room Sign-Off (Commissioning Write-Up)",
      "aka": [
        "commissioning report",
        "cx report",
        "system test report",
        "startup report",
        "system checkout",
        "sign off",
        "sat",
        "site acceptance test",
        "proof of performance",
        "performance verification"
      ],
      "family": "verification",
      "from": "the tech who signed the room off",
      "to": "the client's tech contact and the consultant",
      "why": "Proves the room worked the day you left it, in your words — and names, out loud, everything you could not run.",
      "note": "Narrative only. If the consultant has their own sign-off form, this goes with it — their form is theirs and we don't retype it.",
      "sections": [
        {
          "h": "ROOM, SYSTEM AND DATE TESTED",
          "r": "Site and room in the first two lines — as the drawings label it and as the client calls it — then system type (single display, dual, divisible, boardroom, training), the date, who tested, and the drawing or scope revision you tested against. If there isn't one, write tested against <MISSING> and carry on. Never test against memory."
        },
        {
          "h": "EVERY PATH I ACTUALLY RAN",
          "r": "One line per path, source to destination, picture and sound, for every one you personally put a signal through: table cable, wireless share, room PC, near-end and far-end on a real call, each display, each combine state. List what you ran. Never imply full-matrix coverage you didn't execute."
        },
        {
          "h": "AUDIO — WHAT I SET AND WHAT I READ",
          "r": "Gain structure through the chain, mic coverage checked seat by seat, EQ moves and why, AEC and the reference confirmed on a real call, mute and logic verified, levels at the listening positions. Every number here is one you personally read, with where you read it. Never a comparison word — no \"within\", no \"meets\", no \"should be\", no target, no pass and no fail. You print the reading; grading it is not yours and it isn't mine to guess either."
        },
        {
          "h": "PICTURE — WHAT EACH DISPLAY DID",
          "r": "Resolution and rate confirmed at each display, scaling behavior, HDCP path, camera framing and presets, tracking behavior, and the delay you actually saw on a live call. Observed behavior only — never a datasheet claim written up as a test result."
        },
        {
          "h": "CONTROL, NETWORK AND WHO OWNS THE ACCOUNT",
          "r": "One line per control you exercised: power on and off, source select, volume and mute, camera, combine and uncombine, privacy, occupancy or schedule, shutdown and re-wake — and name any that doesn't work the way it's drawn. Then what the room joins to, the ports confirmed, and who owns the room account. Never write a password, PIN, key or tech-page code here; say the credential exists and who holds it."
        },
        {
          "h": "WITNESSED BY",
          "r": "Who from the client or the consultant stood there, what they watched run, and what they said they accepted, with the date. Names only — never invent a signature block or an approval nobody gave."
        }
      ],
      "omit": "What you could NOT test, and why. The far-end call you never placed because their side wasn't ready, the combine you never ran because the operable wall wasn't in, the room PC that never showed up. It gets left out because the report is supposed to look clean — then it fails in front of a VP and it's a warranty callback instead of their own open item. If it wasn't tested, it goes in by name.",
      "needs": ["notdone"],
      "halt": "Only if you can't tell which room this is. Everything else gets <MISSING> and goes in the open items.",
      "facts": [
        "room name (drawings and client) and system type",
        "date tested and who tested it",
        "who watched it",
        "the drawing or scope revision tested against, if there is one",
        "every source-to-destination path actually run",
        "the readings you took and where you took them",
        "display resolutions and rates confirmed",
        "every control function exercised",
        "what could not be tested, and why"
      ],
      "secondary": [
        "a sign-off letter for the client",
        "a tuning write-up for a room the client says sounds bad",
        "a re-test write-up after a punch item is corrected"
      ]
    },
    {
      "id": "theory-of-operation",
      "name": "How This Room Works",
      "aka": [
        "theory of operation",
        "system description",
        "narrative of operation",
        "sequence of operations",
        "soo",
        "closeout narrative",
        "as-built narrative",
        "room documentation",
        "how it works"
      ],
      "family": "verification",
      "from": "the lead who built the room",
      "to": "their help desk and the next tech",
      "why": "So whoever inherits this room in two years can run it and fix it without calling you for free.",
      "sections": [
        {
          "h": "ROOM, SITE AND WHAT IT'S FOR",
          "r": "Site and room in the first two lines. Capacity, what a normal meeting in here looks like, and what the room is meant to do — local presentation, video call, divisible training, overflow. Plain English, written for somebody who is not an AV tech."
        },
        {
          "h": "WHERE PICTURE AND SOUND COME FROM AND GO",
          "r": "Signal flow by FUNCTION, in order: table input, wireless share, room PC, camera, mics, DSP, amp, speakers, displays. One short paragraph per path. Model numbers are not the language here, and a block diagram is not a substitute for this section."
        },
        {
          "h": "HOW IT TURNS ON AND OFF, AND WHAT THE PANEL DOES",
          "r": "What triggers power-on, occupancy or schedule behavior, warm-up delays, the auto-shutdown timer and what resets it — state every deliberate delay so nobody logs it as a fault. Then the panel: what the user taps and what it actually commands underneath, and only for the controls that generate calls. A page-by-page dump of every button is a document nobody opens. Say a tech page or PIN-protected page exists; never print the PIN."
        },
        {
          "h": "COMBINE AND UNCOMBINE",
          "r": "If this room divides: what happens on combine — which panel takes control, what happens to mics and speakers in the joined space, which camera wins, what the other panel shows, and how it recovers if the wall gets moved with the system powered. This is where every divisible room breaks. Be exact, or leave this section out entirely."
        },
        {
          "h": "WHAT THE ROOM NEEDS FROM THE NETWORK",
          "r": "What has to be reachable for the room to work, who owns each of those things, and the symptom users will report when it isn't reachable. Requirements and ownership only — no credentials, no keys, no addressing that changes."
        },
        {
          "h": "WHEN IT MISBEHAVES — START HERE",
          "r": "The three or four real failures for THIS room: what the user sees, and the first two things to check, written so a tier-1 help desk person can do them. Top of the tree only, never a full troubleshooting tree. Close it with who to call for what once warranty is over."
        }
      ],
      "omit": "The design decisions that look like faults. The intentional delay, the local speaker muting on a call, the input that deliberately doesn't auto-switch because the client asked for that, the mic that gates, the display held on. Nobody writes them down, so by month two the help desk has logged them as defects and you're driving out under warranty to explain a feature.",
      "needs": ["none"],
      "halt": "Only if this is a divisible or multi-mode room and you can't tell from what I gave you how it's meant to behave in each mode — describing the wrong combine logic is worse than describing none.",
      "facts": [
        "room name and capacity",
        "every mode the room supports",
        "every source and where it lands",
        "power-on trigger and shutdown timer",
        "the panel controls that actually generate calls",
        "combine and uncombine behavior if it divides",
        "what the room reaches on the network and who owns it",
        "the behaviors that are intentional and look like faults",
        "who to call for what after warranty"
      ],
      "secondary": [
        "a one-page quick-start for the table or the wall",
        "a tier-1 help desk script for this room type",
        "a floor-by-floor summary for a facilities team taking over a lot of rooms"
      ]
    },
    {
      "id": "outage-report",
      "name": "Meeting Failure / Outage Report",
      "aka": [
        "outage",
        "outage report",
        "failure report",
        "what happened report",
        "incident report",
        "post mortem",
        "rca",
        "root cause",
        "the board meeting went down"
      ],
      "family": "incident",
      "from": "the lead on the account",
      "to": "the client's sponsor and their IT lead",
      "why": "The room failed in front of leadership. This is the document that decides whether you keep the account, and it has to survive being read by somebody angry.",
      "sections": [
        {
          "h": "THE ROOM, THE DAY, AND WHAT THE USERS SAW",
          "r": "Site, room, date and time in the first two lines, then one paragraph: what the meeting was, what it was for, and what the people in it experienced. Written for somebody senior who wasn't there. No jargon, no defending ourselves, no blame — and don't list who was in the room by name."
        },
        {
          "h": "TIMELINE",
          "r": "Clock times from first symptom to restored or meeting ended: onset, when it was reported, when we were notified, when we responded, what was tried. Times from records only — never an estimated time dressed up as a logged one."
        },
        {
          "h": "WHAT ACTUALLY BROKE",
          "r": "The finding: plain language first, tech terms second. If it isn't confirmed, write not confirmed and say only what you have evidence for. Never write a theory as a finding, and never a cause that wasn't in my input."
        },
        {
          "h": "WHAT WE RULED OUT, AND HOW",
          "r": "The things everybody assumed it was, and the evidence that says otherwise. This is what stops the room getting blamed for the network, or the network for the room."
        },
        {
          "h": "HOW WE GOT IT RUNNING AGAIN",
          "r": "What was done during and after, and anything left in a temporary state. If it's a workaround and not a fix, use the word workaround."
        },
        {
          "h": "WHAT CHANGES SO IT DOESN'T HAPPEN AGAIN",
          "r": "One line each with a named owner and a date, split honestly between our side and theirs — including the gap that let it run this long: no room check before the meeting, a change nobody told us about, a known problem nobody funded. Own our half in plain words. Never a list where every action belongs to them."
        }
      ],
      "omit": "What changed in the days before it. The firmware push, the switch config change, the new laptop image, the certificate that rolled, the platform update that landed overnight, the room somebody power-cycled at night. Nobody asks both sides that question, so the write-up says intermittent and the same failure is back in a month. Ask both sides, and write the answer down even when it's \"nothing that we know of\".",
      "needs": ["before", "change"],
      "halt": "Only if you can't tell from what I gave you whether the cause is confirmed or still a theory.",
      "facts": [
        "site, room, date and time of the event",
        "what the meeting was and what it was for",
        "what the users experienced",
        "when it was reported and when we were notified",
        "logged times for each step",
        "what is confirmed versus what is still a theory",
        "what changed on both sides in the days before",
        "what was done to get it running, and whether that's a fix or a workaround",
        "corrective actions with owners and dates"
      ],
      "secondary": [
        "a short summary for when it's the third time this room has gone down",
        "a what-we're-doing-about-it note for the client",
        "an internal note for the service team"
      ]
    }
  ],
  "overrides": {
    "site-walk": {
      "name": "Site Walk / As-Found Write-Up",
      "aka": [
        "walk",
        "site walk",
        "site visit",
        "survey",
        "site survey",
        "existing conditions",
        "as-found",
        "pre-install walk",
        "pre-bid walk",
        "walkthrough",
        "field verification"
      ],
      "why": "Everything you noticed in that room, in a form somebody who wasn't there can price, schedule and order from — and it locks in what the room actually was the day you walked it.",
      "sections": [
        {
          "h": "ROOM, SITE AND DATE WALKED",
          "r": "Site, building, floor and room in the first two lines — as the client calls it AND as the drawings label it — then the date, who walked it with you, and who let you in. This is how anybody finds this in their mail a year later. No conclusions in this section."
        },
        {
          "h": "WHAT'S THERE NOW",
          "r": "Existing gear by type and where it lives, what still works, what's dead, and whose it is — client-owned, ours, or abandoned in place. Describe what you can see. Never write a model number you couldn't read off the plate."
        },
        {
          "h": "WALLS, CEILING, GLASS AND SIGHTLINES",
          "r": "Construction at every place something gets mounted: drywall and stud, glass, block, metal stud, hard lid or ACT grid and the grid size, open plenum, floor boxes and poke-throughs, AFF heights. Then the viewing side: farthest seat, glare, windows and shades, ceiling clutter fighting you (sprinklers, diffusers, lighting, life-safety), hard surfaces and noise sources. What you found only — never say a wall will hold anything, never put a rating on it, and don't promise a display size or a coverage."
        },
        {
          "h": "POWER, PATHWAY AND NETWORK AS FOUND",
          "r": "Receptacles and whether they're dedicated or switched, conduit, sleeves and back boxes present, tray, drops present and whether you tested them live or only looked at them, where the rack is and whose rack it is, distance to the IDF. Say tested or say observed — never blur the two."
        },
        {
          "h": "ACCESS, HOURS AND SITE RULES",
          "r": "Dock, elevator, COI, badging, escort, work hours, noise restrictions, lift access and floor protection, and whether the room is occupied. This is what eats the schedule — be blunt and specific."
        },
        {
          "h": "WHAT I'M ASSUMING",
          "r": "Every assumption you're carrying forward out of this walk, one per line, each with the name of the person who has to confirm it. Assumptions only — no prices, no line items, no \"we'll take care of it\". You walked it; you don't set the scope."
        }
      ],
      "omit": "The stuff you couldn't get to. The ceiling tile you couldn't lift because the room was in use, the IDF nobody had a key for, the wall you never opened, the question nobody answered. It reads like an admission so nobody writes it — and three months later the mount lands on grouted block or the run is longer than bid and it's your money. One line each, with the name of who has to close it.",
      "needs": ["who", "notdone"],
      "halt": "Only if you can't tell which physical room this is — no room name, number, floor or building. Everything else gets <MISSING> and a note on who has to fill it.",
      "facts": [
        "room name as the client says it AND as the drawings label it",
        "date walked and who walked it with you",
        "who let you in or escorted",
        "ceiling type and height at each device location",
        "wall construction everywhere something gets mounted",
        "whether drops and receptacles were tested live or only observed",
        "farthest seat",
        "everything you could not physically get to",
        "photos taken and roughly what each shows"
      ],
      "secondary": [
        "a walk summary for estimating before a bid",
        "an as-found letter when you're inheriting somebody else's install",
        "what the install crew needs to know about getting in"
      ]
    },
    "service-writeup": {
      "name": "Service Call Write-Up — Ticket Narrative",
      "aka": [
        "service",
        "service ticket",
        "trouble call",
        "work order narrative",
        "fsr",
        "field service report",
        "closing notes",
        "call write-up",
        "site visit notes"
      ],
      "why": "Dispatch, the next tech and the customer all read this, and the hours bill off it. It's the narrative you paste into the shop's ticket — that system owns the ticket number and the mandatory fields, and we never invent either.",
      "sections": [
        {
          "h": "CALL, SITE AND ROOM",
          "r": "Site and room in the first two lines so this is findable later, their ticket or WO number if you were given one, date, arrive and depart, who let you in, who reported it. Never invent a ticket number."
        },
        {
          "h": "WHAT THEY SAID WAS WRONG",
          "r": "The symptom in the caller's own words, when it started, every time or intermittent, and what changed recently on their side — an IT push, a room reconfig, a new laptop fleet, furniture moved. Their words. Your diagnosis does not go here."
        },
        {
          "h": "WHAT I FOUND",
          "r": "The condition you observed, in order: what you could reproduce and what you couldn't, link and indicator states, what the DSP, the processor and the codec actually showed on screen, versions as found. Every value is one you personally read — never a number you didn't take."
        },
        {
          "h": "WHAT I DID",
          "r": "The fix or the workaround in sequence: what you touched and in what order, and any part swapped with old serial and new serial. If you rebooted it and it cleared, say exactly that — don't dress a power cycle up as a repair."
        },
        {
          "h": "HOW I PROVED IT'S FIXED",
          "r": "The test you ran in front of somebody: a real call placed, far-end confirmed, every mic, every display, source switching, combine state. Name who watched it. If you couldn't prove it, say so and say why."
        },
        {
          "h": "BILLABLE OR NOT, AND WHY",
          "r": "Travel, on-site hours, after-hours, parts, and the one line saying what we're calling this — warranty, contract or T&M — and what makes it that. Hours exactly as recorded. No rates, no totals, no arithmetic."
        }
      ],
      "omit": "The last-known-good — what you changed and left changed. The trim you nudged, the preset you overwrote, the firmware you bumped, the reservation you added, the port you moved. Six weeks later nobody can tell the original fault from your fix, and the second truck roll gets eaten as warranty. Before value beside the after value, in the same sentence, every time.",
      "needs": ["before", "change"],
      "halt": "Only if you can't tell whether this call is warranty, contract-covered or billable T&M — that one line decides who pays. Everything else gets <MISSING>.",
      "facts": [
        "site and room as the client names it",
        "arrive and depart times",
        "the reported symptom in the caller's words",
        "whether you reproduced it",
        "every setting changed, before value and after value",
        "any part swapped, old serial and new serial",
        "firmware or version as found",
        "who watched the proof-out",
        "what's still open and whose ball it is",
        "warranty, contract or T&M"
      ],
      "secondary": [
        "the failure write-up for an RMA — symptom, what you tried, serial, install date; whoever's form it is owns the number",
        "a plain-English summary email for the client contact",
        "a no-access / nothing-found letter when you got turned away at the door"
      ]
    },
    "delay-notice": {
      "aka": [
        "delay",
        "held up",
        "stopped",
        "waiting on",
        "impact notice",
        "notice",
        "delay notice",
        "backorder",
        "backordered",
        "remobilization"
      ],
      /* PHRASES, NOT ALIASES (2026-09-23). Each led the wrong document here — "room not
         ready" and "not ready" the Look-Ahead, "no access" the Site Walk, "ceiling not
         closed" the Service Call, "port activation" the Daily Field Report — and as
         aliases on this shared id their words would pool onto delay-notice on every
         shelf that carries it. A phrase is routed whole and never pooled
         (shared/docspec.js, phrased()). Same for "owner furnished", "painted over" and
         "rough in" below. "sent home" is NOT here, on measurement: as a delay phrase it
         took "guy got hurt sent home", "hurt sent home" and "sent home hurt" off the
         incident report and made "sent home injured" an exact, one-row Delay Notice.
         A man sent home hurt owes the incident report first; "sent home" still leads
         the Toolbox Talk here, the one AV miss this rung chose to keep. */
      "phrases": ["room not ready", "not ready", "no access", "ceiling not closed", "port activation"],
      "from": "the lead tech on site",
      "to": "the GC super, or the client's project lead when we're direct, and my PM",
      "why": "You showed up and the room couldn't take you: no grid, no power, no drop or network, no millwork, no way in, or the owner's gear isn't here — the room's not ready and you got turned away. Written the same day, it's their hold. Not written, it's a day you didn't show. Our own gear on backorder goes on this notice too — before the date slips, not after.",
      "omit": "The date you first asked, and the trip it already wasted. Everybody writes \"waiting on network\". Almost nobody writes \"port activation and VLAN requested from IT 07/22, drops still dead 07/29, crew of two left site 09:40, told the super 09:35\". The first-asked date says how long it has really been sitting, and the time you left and who you told is the whole claim for the return trip.",
      "needs": ["when", "who"],
      "facts": [
        "what the room was missing — grid, power, a live drop, millwork, blocking, a way in — or the gear that isn't here",
        "who owes it, by name or by company",
        "the date you first asked, and how",
        "what you could not do because of it",
        "if you left site: the time, and who you told before you left",
        "the date you need it by to hold the install"
      ],
      "note": "Facts and dates only — never whose fault. A trip charge or a remobilization is the office's number; this is the dated paper it stands on.",
      "secondary": [
        "a two-line text to the super before you pull out of the lot",
        "a follow-up that carries the first-asked date forward",
        "the ask to IT, written so it pastes straight into their ticket"
      ]
    },
    "change-request": {
      "name": "Extra Work Write-Up — Adds, Moves & Changes",
      "aka": [
        "change order",
        "co",
        "extra",
        "out of scope",
        "t and m narrative",
        "scope change",
        "relocate",
        "relocation",
        "ofe",
        "ofci",
        "revised drawings",
        "moves adds changes"
      ],
      "phrases": ["owner furnished"],
      "to": "the GC's PM or the client's project lead, and my PM",
      "why": "The narrative that rides with the ticket. A display added, a mic moved, a poke-through in the wrong place after the furniture changed, owner-furnished gear you're now told to make work, a drawing revision that landed after rough-in. Prices are the office's — this is the part that says why it's extra, which is the part that gets argued.",
      "omit": "Who said yes, when, and on what channel — and everything the change drags along. An added display is never just the display: it's the pull, the mount, a switcher output and the extender, the control programming, the EDID, the DSP if it carries sound, and a re-test of the whole room. Write only the hardware and the change order pays for the bracket while the programming, the DSP time and the second commissioning pass get eaten.",
      "needs": ["when", "who"],
      "facts": [
        "what was asked for, by whom, and where in the room",
        "when it was authorized, and by what channel",
        "the drawing revision or scope line you were building to",
        "what it drags along — pulls, programming, DSP, a re-test",
        "what it displaced or held up"
      ],
      "secondary": [
        "a one-paragraph version to paste into the GC's change form",
        "a heads-up to the office that programming and DSP time ride with this one"
      ]
    },
    "handover": {
      "name": "Turnover — Warranty Starts",
      "aka": [
        "handover",
        "turnover",
        "closeout",
        "hand off",
        "handoff",
        "close out",
        "punch complete",
        "punch",
        "punch list",
        "spares"
      ],
      "from": "the lead who built the rooms",
      "to": "the client's facilities or IT lead, and whoever runs their help desk",
      "why": "The last thing anybody reads on the job and the first thing they blame. Written right it ends the install on the record — what they got, whose account the licenses and subscriptions sit on, what's still open, and the day our warranty starts. Written as if everything is finished, every leftover comes back to you as free warranty.",
      "omit": "The day OUR warranty starts, as a calendar date, and who on their side took the rooms — plus the day they actually started using them. \"Upon completion\" lets the client decide when completion was, and three weeks of meetings in rooms nobody signed for become three weeks of warranty calls on your truck. Say it's ours: the makers' warranties run from their own ship or registration dates, and a turnover that doesn't say so makes every dead display yours.",
      "needs": ["when", "who"],
      "sections": [
        {
          "h": "ROOMS AND DATES",
          "r": "Site and rooms as the client calls them and as the drawings label them; the turnover date; the date our warranty starts, and where that date comes from — the contract, your PM or the client's written acceptance; the date they started using each room, if earlier. Never a date you worked out yourself."
        },
        {
          "h": "WHO WAS TRAINED",
          "r": "Who, on what, and when — and who was supposed to be there and wasn't."
        },
        {
          "h": "WHAT WE HANDED OVER",
          "r": "As-builts, manuals, spares, remotes, rack keys, and where the final DSP, control and codec files are kept and who has a copy. Say a password, PIN or a room account's sign-in exists and who holds it; never the value."
        },
        {
          "h": "ACCOUNTS AND RENEWALS",
          "r": "Every license and subscription the rooms need to keep working: whose account it's on and the date it renews. Nothing about what it costs."
        },
        {
          "h": "STILL OPEN",
          "r": "Each open item with an owner and a date. Nothing reads as finished that isn't."
        },
        {
          "h": "WHO TO CALL",
          "r": "For what, during our warranty and after it."
        }
      ],
      "facts": [
        "the rooms or systems turned over, as the client names them",
        "the date our warranty starts, as a calendar date, and where that date comes from — the makers' warranties run from their own dates",
        "who on their side took the rooms",
        "the date they started using the rooms, if before turnover",
        "who was trained, on what, and when",
        "what was handed over — as-builts, manuals, spares, remotes, rack keys",
        "where the final DSP, control and codec files are kept, and who has a copy",
        "whose account the licenses and subscriptions sit on, and when each one renews",
        "what's still open, with an owner and a date",
        "who to call for what"
      ],
      "note": "A password, PIN, license key, tech-page code or a room account's sign-in never goes in this document — say it exists and who holds it. How long the warranty runs and what it covers is the office's letter; this gives it the dates.",
      "secondary": [
        "a version for the client's help desk",
        "the punch on its own, with an owner and a date on each line",
        "a one-page who-to-call sheet for the room"
      ]
    },
    "damage-found": {
      "aka": [
        "damage",
        "pre-existing",
        "found damage",
        "prior damage",
        "not us",
        "doa"
      ],
      "phrases": ["painted over"],
      "from": "the tech who found it",
      "to": "the GC super and my PM",
      "why": "Something reached your gear before you did — cracked in the carton, dead on arrival, backbox buried behind somebody's finish, painted over, cut after it was in. This is the dated, photographed note that says it was that way when you found it, before anybody goes looking for who to charge.",
      "omit": "The serial, the date it came in, and where the carton is right now. A cracked display or a dead amp out of the box gets claimed off those three, and they're the first things gone — the carton's in the dumpster by lunch and nobody wrote the serial before it went up the wall. Without them the replacement comes out of your margin.",
      "needs": ["when", "where"],
      "facts": [
        "the date and time found",
        "the room, and exactly where in it",
        "what the damage is, and the last time anybody saw it whole — received, unboxed, installed — if you know",
        "for gear: the serial, the date it came in, and whether the carton was kept",
        "for freight: who signed for it, and whether the damage was written on the delivery receipt",
        "photos taken, and where they live",
        "who you told and how"
      ],
      "note": "Say what you found and photograph it. Never write who did it or whose fault it is — who pays is the office's call, off this dated record.",
      "secondary": [
        "a note to the office for the freight claim or the RMA — serial, date received, carton kept or not; whoever's form it is owns the number"
      ]
    },
    "look-ahead": {
      "name": "Look-Ahead — What Has To Be True First",
      "aka": [
        "look ahead",
        "lookahead",
        "two week",
        "three week",
        "next week",
        "plan",
        "programming"
      ],
      "phrases": ["rough in"],
      "from": "the lead tech",
      "to": "my PM, the office and the GC super",
      "why": "The one that stops the crew standing in a room that can't take them next week. On AV it's the install sequence — rough-in, trim-out, programming and commissioning, room by room, with the manpower, the receiving and the gear it takes — and what has to be true before each one: open for rough, closed and painted for trim, furniture in, power on, ports active, gear here.",
      "omit": "What has to be TRUE before each room can start, and who makes it true. Trim before paint's done and you're back to re-hang it; ceiling mics before the grid's in is a second trip; programming before IT has the drops live and the room account made is a tech sitting in a chair on the clock. A look-ahead with no preconditions is a wish list — on AV it's a wish list and a second trip.",
      "needs": ["notdone", "who"],
      "facts": [
        "the period",
        "techs expected, and who's programming",
        "the rooms in order, and the phase each is in — rough, trim, rack, program, commission, train",
        "the gear that has to arrive and be received",
        "what has to be true first — grid, walls, ceiling, paint, furniture, power, live drops, room accounts made",
        "who owns each of those"
      ],
      "secondary": [
        "a manpower request for the office",
        "the ask to IT — drops, VLANs and room accounts, each by date",
        "a coordination note for the GC super"
      ]
    }
  },
  "drop": [],
  "vocab": [
    "villain -> VLAN",
    "platinum rated -> plenum-rated",
    "fandom power -> phantom power",
    "docking -> ducking",
    "gnome -> NOM (number of open mics)",
    "condo -> conduit",
    "surface loop -> service loop",
    "edit -> EDID",
    "scalar -> scaler",
    "co deck -> codec",
    "loss of sink -> loss of sync",
    "peatsy -> PTZ",
    "a easy -> AEC (acoustic echo canceller)",
    "idea f -> IDF",
    "ignore m p -> IGMP",
    "far and -> far-end",
    "near and -> near-end",
    "are you -> RU (rack unit)",
    "dee ess pee -> DSP",
    "ex el are -> XLR",
    "cat six a -> Cat6A",
    "po e -> PoE",
    "a f f -> AFF (above finished floor)",
    "tea and em -> T&M"
  ],
  "reminders": [
    "When anything goes above a ceiling or inside a wall -> shoot the photo with the tile out and a tape in frame BEFORE it closes. Once the grid is back in, the only record is your word.",
    "When a DSP file, control code, firmware or preset gets changed -> write the before value beside the after value in the same sentence. That pair is what makes the next fault diagnosable instead of a second truck roll.",
    "When you get sent home, turned away, or the room isn't ready -> name the person you told and the time you told them, before you leave the parking lot. That sentence is the whole claim.",
    "When a password, PIN, a room account's sign-in, license key or tech-page code comes up -> it does not go in the document. Say the credential exists and who holds it, nothing more.",
    "When a room gets handed over, 'they've already started using it', or a device gets added or moved -> put the warranty start date in as a calendar date, and say whether programming, DSP changes and a re-test pass are included. Those are the two lines that get eaten silently."
  ]
};
