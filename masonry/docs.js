/* MASONRY FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what is
 * different about masonry work and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS RATED, SIZED, SPACED, TIMED OR JUDGED. No mortar type, no
 *     proportion, no bar size, lap or cover, no bearing length, no joint or tie
 *     spacing, no lift height, no protection temperature, no cure time, no
 *     acceptance criterion, no "should be" — not as a value, not as a hint, not
 *     in a placeholder. The layer states what he laid and what he saw; nobody
 *     here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *
 * THE FOURTH REFUSAL, AND IT IS THIS TRADE'S. Roofing's documents refuse CAUSE
 * and COVERAGE. Concrete's refuse those and STRENGTH. Masonry's refuse all three
 * and one more: BRACING AND LOADING. A wall standing without its diaphragm is
 * the thing on this job that kills people, and it is engineered — a foreman may
 * write that a wall is standing, that it is not braced, and that he wants
 * somebody to come and look at it. He may NOT be led into writing a height, a
 * spacing, a wind figure, a duration, a restricted distance, or that a wall is
 * safe to load, to backfill against or to work under. Every document below
 * leans on the engine's standing "never invent, never grade" laws and states
 * its own refusal in its own words.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work")
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TRADE_DOCS = {
  "trade": "masonry",
  "docs": [
    {
      "id": "wall-record",
      "name": "The Wall Record",
      "aka": [
        "wall record",
        "what we laid",
        "lay record",
        "wall report",
        "what went in the wall",
        "we laid today",
        "lift record"
      ],
      "family": "verification",
      "from": "the foreman who ran the wall",
      "to": "our office and the GC super",
      "why": "The only account of what went into a wall, written by the man who was standing on it. Once it caps and grouts, nobody can open it up and look — so this is read a year later by somebody arguing about a box, a sleeve, an anchor or a lintel, and by then everybody's memory has an opinion.",
      "note": "Submittal numbers, delivery tickets and inspection reports are referenced, never retyped. The supplier owns his ticket, the lab owns its report; this document points at them.",
      "omit": "What of somebody else's work got built into this wall, and at what course. Everybody writes how far they got. Almost nobody writes that the electrician's boxes at grid 5 went in at the ninth course and which cells were left open for him — and that is the only line that answers \"you laid past my stub\" a month later, when the wall is grouted and the answer costs a core bit.",
      "needs": ["who", "count"],
      "halt": "Never halt. If the lift is still going, write what is known, mark the rest <MISSING>, and send it — a late wall record is worse than an incomplete one.",
      "facts": [
        "the date and the wall",
        "the course or height it started and finished at",
        "what of somebody else's work went in, and at what course",
        "which cells were left open, and for whom",
        "crew and material on the ground"
      ],
      "sections": [
        {
          "h": "Which wall and how far",
          "r": "Call it what the job calls it and what the set calls it — elevation, gridline, wall mark, stair, shaft, chimney, veneer bay — and say the course or height it started at and the course or height it finished at. Say whether it capped out."
        },
        {
          "h": "What we built in for somebody else",
          "r": "Every box, sleeve, stub, chase, embed, plate, anchor, joist pocket, lintel, bond beam pocket, blockout and hollow metal frame that went into this wall, whose work each one is, and the course it landed at. Say which cells were left open, for whom, and whether that is in writing anywhere."
        },
        {
          "h": "Material and crew",
          "r": "Units, mortar and sand as counts in the units they came in — cubes, bags, yards, rolls, pieces. Who laid, who tended, who was on the stage. State the mortar type and the mix only as the thing you were working to off your own approved submittal; never write a proportion or a strength from memory."
        },
        {
          "h": "What we found and what we left",
          "r": "Anything not as shown — footing high or low, dowel out of a cell, a dimension that doesn't close, a frame not on site. What was on the wall when the crew walked: cover, protection, the stage, barricade. If the wall is standing and not braced, say so and ask who is coming to look. Never write a bracing figure and never write that it is safe."
        },
        {
          "h": "Tickets and photos attached, not retyped",
          "r": "List delivery tickets by the numbers already on them and attach them. Photo list says what each frame shows and where it was shot from — flashing, weeps, ties and anything about to be covered by veneer get their own frames, because that is the only look anybody gets."
        }
      ]
    },
    {
      "id": "pre-grout-walk",
      "name": "Before We Grout",
      "aka": [
        "before we grout",
        "pre grout walk",
        "grout day walk",
        "before the grout",
        "last look before grout",
        "cells walk"
      ],
      "family": "verification",
      "from": "the foreman who walked it",
      "to": "the GC super, and every trade with something in this wall",
      "why": "The last look anybody gets at what is in the cells. Half of what is in this document belongs to somebody else, and after the grout nobody can see any of it — the answer becomes a core bit through grout and rebar, and on a structural wall a call to the engineer before anybody starts a saw.",
      "note": "This records what was walked. It is not an inspection, it does not approve anybody's work, and it never states what a thing was supposed to be. The special inspector and the testing agency own their record; this is not it and must never be believed to be it.",
      "omit": "The list of other people's work about to be closed in — conduit up the cells, boxes, sleeves, stubs, embeds, anchors, dowels — and who walked it and told us it was set. Once the cells are full it is gone, and \"you grouted my cell\" has no answer without that line and the name of the man who cleared it.",
      "needs": ["who"],
      "halt": "Only if the wall it covers is not named at all.",
      "facts": [
        "the wall and the lifts this covers",
        "what of ours is ready",
        "whose work is about to be closed in",
        "what is not ready",
        "who walked it and who cleared it"
      ],
      "sections": [
        {
          "h": "The wall this covers",
          "r": "Name it and its limits the same way the wall record does, the day the grout is going, and how it is going in — by hand, by pump, by truck."
        },
        {
          "h": "Ours, and it's ready",
          "r": "What our crew has done: laid to course, cleanouts closed or open, bond beam formed, steel set to the field set in hand, cells free of droppings, the stage clear, access for the truck or the pump, somewhere to wash out."
        },
        {
          "h": "Theirs, and we're about to close it in",
          "r": "Every item belonging to somebody else in these cells, and for each one whether that party walked it and told us it is set. Where nobody walked it, say so and ask for the walk before grout is ordered. Name the cells that are supposed to stay open and who asked for them."
        },
        {
          "h": "Not ready, or not what we expected",
          "r": "What the walk found that isn't right — steel not where the set shows it, a cell blocked, a cleanout that won't close, somebody still working in the wall, an inspection not called. Describe the condition. No fault, no fix proposed, no acceptance."
        },
        {
          "h": "Who walked it and who was told",
          "r": "Who was on the walk, from which company, and who cleared their own work. Who is calling the inspection and when. What was said and by whom, so the record is not one man's memory."
        }
      ]
    },
    {
      "id": "not-as-shown",
      "name": "Not As Shown",
      "aka": [
        "not as shown",
        "doesn't match the drawings",
        "found condition",
        "footing is off",
        "dowels are wrong",
        "dimension doesn't work",
        "not what's on the set"
      ],
      "family": "notice",
      "from": "the foreman on the wall",
      "to": "the GC super, copy our PM",
      "why": "The condition you are standing in front of is not the condition on the set, and you are the last person who can say so before you build it in. A wall laid to a wrong dimension is not a punch item, it is a demolition.",
      "note": "This describes a condition and asks a question. It never proposes the fix, never states what the condition should be, and never says whose fault it is. What the drawings require belongs to the engineer of record and the architect.",
      "omit": "What work of yours is STOPPED and at what course, and what you will keep doing in the meantime. A notice that describes a bad footing and does not say \"I am stopped at the third course on the east elevation and I have moved two layers to the stair\" gets read as information rather than as something that has to be answered today.",
      "needs": ["count", "notdone"],
      "halt": "Only if the condition itself is not described.",
      "facts": [
        "where it is, by wall and course",
        "what you actually found, measured or seen",
        "what it does not agree with, by sheet and revision",
        "what work of yours is stopped and at what course",
        "who you told and when"
      ],
      "sections": [
        {
          "h": "Where and what",
          "r": "The wall, the gridline, the elevation and the course or height. What is actually there, in plain field terms — footing high, low or out of line, dowel out of a cell or bent, opening in the wrong place, a dimension that doesn't close, an embed missing, a frame that doesn't match the opening."
        },
        {
          "h": "What it doesn't agree with",
          "r": "The sheet and revision you are working to, and what it shows. Say what set you have in hand and when you got it. If you have two sets that disagree, say that instead — it is a different problem and a more urgent one."
        },
        {
          "h": "What's stopped and what isn't",
          "r": "What you cannot lay and at what course you stop, what you have moved the crew to, and what happens to the schedule if the answer takes days. Counts of men and hours only. No rates, no totals, no delay claim."
        },
        {
          "h": "The question, and who owns it",
          "r": "Ask it plainly and address it to whoever owns the answer. Say out loud that you are not proposing a fix and will not decide this one on the wall — if it is structural it belongs to the engineer of record, and you want the answer in writing before the next lift."
        },
        {
          "h": "Told, and when",
          "r": "Who was told at the time, when, how, and what came back. Photos of the condition with something in frame that establishes where it is."
        }
      ]
    },
    {
      "id": "stopped-on-this-wall",
      "name": "We're Stopped On This Wall",
      "aka": [
        "stopped",
        "we're stopped",
        "can't lay past",
        "held on this wall",
        "waiting on",
        "stopped at course"
      ],
      "family": "notice",
      "from": "the foreman on the wall",
      "to": "the GC super, copy whoever owns what you're waiting on",
      "why": "You cannot lay past an opening that isn't there, a lintel that hasn't shipped or a box that hasn't been marked. Said at the right course it costs somebody a phone call; said at the head course it costs a lift.",
      "note": "This says what you are waiting on and at what course you stop. It is not a delay claim, it puts no money on anything, and it does not say what it will cost.",
      "omit": "THE COURSE. Everybody writes what they are waiting on and everybody writes a date. The course is the only number that tells the other man how long he actually has — \"I stop at the head course and I am at eight foot\" is a deadline he can work to, and \"we need it soon\" is not.",
      "needs": ["count"],
      "halt": "Only if what you are waiting on is not named.",
      "facts": [
        "the wall and the course you stop at",
        "what you're waiting on, by mark or by name",
        "who owns it",
        "where the crew goes in the meantime",
        "who you told and when"
      ],
      "sections": [
        {
          "h": "The wall and the course",
          "r": "Which wall, and the course or height you stop at. Say where you are now, so the reader knows how much time he has. Say when you expect to reach the stopping course if the crew keeps going."
        },
        {
          "h": "What we're waiting on",
          "r": "Name it by mark where it has one — frame, lintel, angle, sill, cap, embed, anchor, precast piece — or by what it is: a marked-out box, a sleeve location, a dimension, a control line, layout, an inspection, access, hoisting, the stage. Say who owns it."
        },
        {
          "h": "What we're doing instead",
          "r": "Where the crew moves to and for how long, and what runs out when. Counts of men only. If nothing else is available to work, say that plainly — it is a fact, not a claim."
        },
        {
          "h": "What we need and by when",
          "r": "The one thing that turns this loose, said as a course rather than a date wherever it can be. Ask for the answer in writing and say who you need it from."
        },
        {
          "h": "Told, and when",
          "r": "Who was told at the time, when, how, and what came back — including anything you were told verbally that you are now putting in writing."
        }
      ]
    },
    {
      "id": "left-standing",
      "name": "What We Left Standing",
      "aka": [
        "left standing",
        "wall left up",
        "what we left",
        "unbraced wall",
        "nobody touch it",
        "what we covered"
      ],
      "family": "notice",
      "from": "the foreman leaving the wall",
      "to": "the GC super, copy every trade working near it",
      "why": "A wall that is standing but not finished is not somebody else's to load, to backfill against, to stack on, to hang from or to work under, and the man who laid it is the only one who knows which walls those are. Written the day you leave it, not the day something happens.",
      "note": "This states what is standing and what nobody does to it, and it hands every engineered question back. It never states a bracing height, a spacing, a wind figure, a distance, a duration or a release, and it never says a wall is safe. If somebody wants a wall released, that is the engineer of record's call and this document says so.",
      "omit": "WHO OWNS THE BRACING AND WHO IS ALLOWED TO MOVE IT. Every notice like this says the wall is unbraced. Almost none of them name the man on your crew whose call that is — so the framer who needs an aisle moves a brace at seven in the morning, and there was never anybody to ask.",
      "needs": ["who"],
      "halt": "Only if no wall is identified.",
      "facts": [
        "which walls are standing and to what course",
        "what protection was left on them",
        "what nobody does to them",
        "who on our crew owns the bracing call",
        "who was told"
      ],
      "sections": [
        {
          "h": "What's standing",
          "r": "Each wall by its own name and the course or height it is at. Say whether it is capped, grouted, or neither, in your words — not as a status anybody else can rely on."
        },
        {
          "h": "What we left on it",
          "r": "Cover, protection, barricade, tape, cones, the stage. Where the cells are still open, say so, because rain into open cells is a stain on a face somebody has already washed."
        },
        {
          "h": "What nobody does to it",
          "r": "Plainly, one line each: don't load it, don't backfill against it, don't stack against it, nothing hangs off it, don't cut it, leave the stage where it is. Do not write a number next to any of these and do not write that anything is safe."
        },
        {
          "h": "Bracing, and it is ours",
          "r": "If a wall is not braced, say it is not braced and ask for whoever needs to look at it to come and look. Name the man on your crew who owns that call and say that nobody else moves, removes or alters a brace — not the framer who needs an aisle, not the super who needs a photo. Never write a height, a spacing, a distance, a wind figure or a duration: that is engineered and it is not ours to state."
        },
        {
          "h": "Who was told",
          "r": "Who got this, when, and how, including the other trades working near it. Say plainly that a wall not named here is a wall you have said nothing about."
        }
      ]
    },
    {
      "id": "damage-reply",
      "name": "The Crack That Isn't Ours",
      "aka": [
        "crack",
        "cracked wall",
        "not our crack",
        "damage reply",
        "spall",
        "staining",
        "efflorescence",
        "they say we broke it"
      ],
      "family": "incident",
      "from": "the foreman who went and looked",
      "to": "the GC super and our PM",
      "why": "Somebody has pointed at a crack, a spall, a chipped arris or a stain on masonry and said it is yours. This is the record of what you actually found when you went and looked, written the same day, before the wall gets touched.",
      "note": "It records what was seen. It never states a cause, never grades the wall, and never says the work is acceptable or unacceptable. Cracking, spalling and staining in masonry have several causes, most of them owned by somebody else, and a foreman who is led into naming one has made his company's case for it.",
      "omit": "THE LAST DATE YOUR CREW WAS ON THAT WORK, AND WHO HAS HAD THE AREA SINCE. Everybody photographs the crack. Almost nobody writes the date they were last on it and the list of trades that have worked around it since — and without those two lines there is nothing at all between your company and the claim.",
      "needs": ["when", "who"],
      "halt": "Only if the location is not stated.",
      "facts": [
        "the date you went and looked",
        "the exact location, by wall and course",
        "what you actually saw",
        "the last date your crew was on that work",
        "who has had the area since, and who told you"
      ],
      "sections": [
        {
          "h": "What was reported and by whom",
          "r": "Who said it, when, how, and exactly what they said — in their words, not summarised. Say what you were asked to do about it."
        },
        {
          "h": "What we found",
          "r": "The wall, the elevation, the course or height, and what is actually there — described, not diagnosed. Where it runs and where it stops. Whether it goes through the joint or through the unit. What the face looks like. No cause, no age, no verdict, and no opinion about whether it matters."
        },
        {
          "h": "When we were last on it, and who has been since",
          "r": "The date your crew last worked that wall and what you left it in. Then everybody who has worked in, on, around, above or below it since, as far as you know, and how you know — including any loading, backfilling, cutting, coring, hanging or equipment near it."
        },
        {
          "h": "Evidence",
          "r": "Photos with something in frame that establishes where each one was taken, and the dates. Any earlier photos of that wall you already have. Names of anybody who saw it with you."
        },
        {
          "h": "What we've asked for",
          "r": "Say that you are not stating a cause and will not, that anything structural belongs to the engineer of record, and ask that nothing be repaired, cut, ground out, washed or covered until whoever owns that decision has looked at it. Say who you told and when."
        }
      ]
    }
  ],
  "overrides": {
    "delay-notice": {
      "name": "We Got Held",
      /* AKA TRIMMED 2026-09-02. "stopped" and "waiting on" are shared aliases on
         this document AND on `stopped-on-this-wall` above, so on a mason's shelf
         one word pointed at two documents. He was already getting the right one
         first — the wall notice is what a mason means — so the general notice
         gives the words up rather than competing for them. It keeps everything
         a man reaches for when the hold is NOT a wall: a submittal, a decision,
         an inspection, a hoist. */
      "aka": ["delay", "delay notice", "held up", "impact notice", "notice"],
      "omit": "Who and what actually stood — the layers and tenders by name and classification, the stage and the forklift, the mud that was mixed and went off — and what the crew would have been doing instead. \"We were held from morning to noon\" with no names and nothing idled is a sentence nobody can check and nobody can act on.",
      "needs": ["who", "count", "notdone"],
      "sections": [
        {
          "h": "The hold and the clock",
          "r": "What was being held and where, the time the crew was ready, the time the hold started, the time it turned loose or the crew went home. Who called it, or who we were waiting on."
        },
        {
          "h": "Why we couldn't go",
          "r": "Field terms: another trade still in our wall, frames or lintels not on site, layout not released, footing or dowels not right, the stage not up or not released, access or hoisting blocked, mud on the ground with nowhere to lay it, an inspection not made."
        },
        {
          "h": "Who and what stood",
          "r": "The layers and tenders who stood and their classifications, the equipment idled by piece, the mud mixed that went off, the material on the ground that could not be laid. Counts of men, counts of hours, counts of pieces. No rates, no totals."
        },
        {
          "h": "What we were set up to do",
          "r": "The wall the crew was manned, staged and stocked for in that window, and the course it would have reached, so the hold reads against something real."
        },
        {
          "h": "Who we told",
          "r": "Who got told at the time, when, how, what came back, and whether we asked to be turned loose or moved somewhere else and what came of it."
        }
      ],
      "facts": [
        "what you were held by and who owns it",
        "the clock — when the crew got there and when it went",
        "the layers and tenders, by name, who stood",
        "the stage, the forklift and the mud that stood",
        "who you told, and when"
      ]
    },
    "daily-report": {
      "omit": "THE COURSE EVERY WALL GOT TO, AND WHAT WENT INTO IT. Every other trade's daily can leave the day at \"we got this far\". A masonry daily that does not say the course each wall reached and whose work got built into it is missing the two lines anybody comes back for — and once the wall caps and grouts, nobody can open it up and look.",
      "needs": ["who", "count"],
    }
  },
  "drop": [],
  "vocab": [
    "see em you -> CMU",
    "cinder block -> block",
    "concrete block -> block",
    "block out -> blockout",
    "bond beam -> bond beam",
    "lintel block -> lintel block",
    "sash block -> sash block",
    "half high -> half-high",
    "jamb block -> jamb block",
    "bull nose -> bullnose",
    "split face -> split-face",
    "ground face -> ground face",
    "burnished block -> burnished block",
    "cell -> cell",
    "web -> web",
    "wythe -> wythe",
    "with -> wythe",
    "collar joint -> collar joint",
    "head joint -> head joint",
    "bed joint -> bed joint",
    "lead -> lead",
    "twig -> line twig",
    "line block -> line block",
    "story pole -> story pole",
    "course rod -> course rod",
    "corner pole -> corner pole",
    "mud -> mortar",
    "type ess -> Type S",
    "type en -> Type N",
    "mortar joint -> mortar joint",
    "tuck point -> tuckpoint",
    "tuck pointing -> tuckpointing",
    "re point -> repoint",
    "grind out -> grind out",
    "slick -> slicker",
    "striking iron -> jointer",
    "thumb print -> thumbprint",
    "ladder wire -> ladder wire",
    "truss wire -> truss wire",
    "joint reinforcement -> joint reinforcement",
    "wall tie -> wall tie",
    "brick tie -> veneer tie",
    "weep -> weep",
    "weep hole -> weep",
    "thru wall -> through-wall flashing",
    "through wall -> through-wall flashing",
    "flashing -> flashing",
    "cavity -> cavity",
    "clean out -> cleanout",
    "hollow metal -> hollow metal",
    "aitch em -> HM",
    "loose lintel -> loose lintel",
    "angle iron -> loose angle",
    "soldier course -> soldier course",
    "rowlock -> rowlock",
    "soap -> soap",
    "queen closer -> queen closer",
    "effloresce -> efflorescence",
    "eff -> efflorescence",
    "cube -> cube",
    "strap -> strap",
    "mud board -> mud board",
    "tender -> tender",
    "layer -> layer",
    "ay hitch jay -> AHJ",
    "ee oh are -> EOR"
  ],
  "reminders": [
    "When a wall, a lift or a day's laying is described -> remind them to say the COURSE or height it started at and the course it finished at, not just how far they got. It is the number two other trades on the job are counting down to, and it is the number nobody writes.",
    "When somebody else's box, sleeve, stub, conduit, embed, anchor, dowel, lintel or frame comes up -> remind them to name whose it is and the COURSE it went in at, and to say which cells were left open and for whom. This is the only document that will ever show it existed, because once the wall caps and grouts the answer is a core bit through grout and rebar.",
    "When mortar, grout, mix or material comes up -> remind them that mortar and grout are different materials on different days and must never be swapped in the sentence, and to state the type only as the thing they were working to off their own approved submittal. Never write a proportion, a strength or a lift height.",
    "When a wall left standing, bracing, a brace, backfilling, loading, stacking, hanging or working under a wall comes up -> remind them to say what nobody does to it, to name the man on their own crew who owns the bracing call, and to hand every engineered question back. NEVER let the document carry a bracing height, spacing, distance, wind figure, duration or release, and never let it say a wall is safe. That is the one on this job that kills people and it is not ours to state.",
    "When a crack, a spall, a chipped arris, a stain or efflorescence comes up -> remind them to establish the LAST DATE their crew was on that work and who has had the area since, and never to state a cause. A mason may say what he laid and what he saw. He may not be made to say why it cracked or why it stained.",
    "When a delivery ticket, a submittal, an inspection, a prism, a mortar cube or a grout sample comes up -> remind them to reference it by its own number and NEVER to retype what is on it. The supplier owns his ticket, the testing agency owns its report and the special inspector owns his — retyping somebody else's numbers into our letter is how a transcription error becomes our statement.",
    "When cubes, bags, yards, rolls, pieces, squares or square feet are mentioned -> remind them to state the unit they actually counted in and never to convert between units in the document. Block comes by the cube, mortar by the bag, sand by the yard, wire by the roll and lintels by length — a conversion nobody checked is how an order and a claim both go wrong.",
    "When the panel, the mock-up, color, blend, joint profile or cleaning comes up -> remind them to point at the approved panel rather than describing what it should look like, and to say who signed it off and when. The panel is the only thing anybody can stand in front of a year later."
  ]
};
