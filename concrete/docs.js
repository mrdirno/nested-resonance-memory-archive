/* CONCRETE FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what is
 * different about concrete work and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS RATED, SIZED, DOSED, TIMED OR JUDGED. No strength, no slump, no
 *     air, no bar size, no lap, no cover, no cure time, no joint spacing, no
 *     acceptance criterion, no "should be" — not as a value, not as a hint, not
 *     in a placeholder. The hand states what he placed and what he saw; nobody
 *     here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *
 * WHY THIS LIBRARY GETS THE THIRD REFUSAL. Roofing's documents refuse CAUSE and
 * COVERAGE. Concrete's refuse those two and one more: STRENGTH. A concrete
 * write-up is read by structural engineers, testing labs, carriers and lawyers,
 * and the single most dangerous sentence a foreman can be led into writing is
 * that the concrete had reached something, was ready for something, or was fine.
 * He may say what he placed, when he placed it, what he saw and what he was told.
 * He may not be made to say that it was strong enough, that a joint is
 * acceptable, or why it cracked. Every document below leans on the engine's
 * standing "never invent, never grade" laws and says its own refusal in its own
 * words.
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
  "trade": "concrete",
  "docs": [
    {
      "id": "pour-record",
      "name": "Pour Record",
      "aka": [
        "pour record",
        "placement record",
        "pour report",
        "what we poured",
        "pour card",
        "placement log",
        "we poured today"
      ],
      "family": "verification",
      "from": "the foreman who ran the placement",
      "to": "our office and the GC super",
      "why": "The only account of what went in, where it started and where it stopped, written by the man who was standing there. It gets read a year later by somebody looking at a crack, and by then everybody's memory has an opinion.",
      "note": "Ticket numbers and lab numbers are referenced, never retyped. The plant owns its ticket and the lab owns its report; this document points at them.",
      "omit": "Where the placement started and where it stopped, and what got left out on purpose — blockouts, pour strip, the bay that got deferred. Everybody writes the date. Almost nobody writes the line on the floor, so when a crack shows up months later there's nothing in the file that says whose pour it was even in.",
      "halt": "Never halt. If the pour is still going, write what is known, mark the rest <MISSING>, and send it — a late pour record is worse than an incomplete one.",
      "facts": [
        "the date and the placement",
        "where it started and where it stopped",
        "the mix design number off your own submittal",
        "crew and equipment on the ground",
        "the ticket numbers, not their contents"
      ],
      "sections": [
        {
          "h": "What and where",
          "r": "Call it what the job calls it and what the set calls it — footing, grade beam, wall, column, slab on grade, housekeeping pad, deck, topping, pour strip, curb, drive — and pin it: grid, column line, footing mark, station or address. Pour number or pour area if the job runs them."
        },
        {
          "h": "Where it started and where it stopped",
          "r": "Bay by bay, wall by wall. Name every blockout, pour strip and section left open on purpose. If a joint or keyway got formed at the stopping line, say where it sits."
        },
        {
          "h": "Mix, steel and what we buried",
          "r": "Call the mix by the name it goes by on this job. Don't write strength, slump or air from memory — the ticket carries that. Say the steel, dowels, chairs and dobies were set to the field set in hand, and list every embed, sleeve, blockout, anchor bolt template and waterstop that went under it or through it, and whose work each one is."
        },
        {
          "h": "Crew, equipment and the clock",
          "r": "Who placed and who finished, how it went in (chute, boom, line pump, buggy, wheel, hand-carry), how much the crew counted, first load discharged, last load discharged, finishers off. Short load, gap between trucks, load sent back — write what happened, plain."
        },
        {
          "h": "Finish and what we left on it",
          "r": "How it got finished — wet screed, bull float, broom, trowel, exposed, seeded, rubbed — and what was on it when the crew walked: cure, cover, blankets, plastic, sand, barricade, tape, cones. If the crew is asking who's calling the saw cuts and when, ask it here as a request."
        },
        {
          "h": "Tickets and photos attached, not retyped",
          "r": "List the delivery tickets by the numbers already on them and attach them. Same for any cylinders the tech took. Don't restate the plant's paper or the lab's paper. Photo list says what each frame shows and where it was shot from."
        }
      ]
    },
    {
      "id": "pre-pour-readiness",
      "name": "Pre-Pour Walk",
      "aka": [
        "pre-pour walk",
        "pre pour",
        "ready to pour",
        "pour walk",
        "readiness",
        "walk before the pour"
      ],
      "family": "verification",
      "from": "the foreman who walked it",
      "to": "the GC super, and every trade with something in this pour",
      "why": "The last look anybody gets at what is about to go under concrete. Half of what is in this document belongs to somebody else, and after the pour nobody can see any of it.",
      "note": "This records what was walked. It is not an inspection, it does not approve anybody's work, and it never states what a thing was supposed to be.",
      "omit": "The list of other people's work about to go under the concrete — sleeves, conduit, under-slab utilities, vapor barrier and its penetrations, embeds, hold-downs, anchor bolt templates, dowels, waterstop — and who walked it and told us it was set. Once it's covered it's gone, and \"you poured over my sleeve\" has no answer without that line.",
      "halt": "Only if the placement it covers is not stated at all.",
      "facts": [
        "the placement and the date",
        "what of ours is ready",
        "whose work is about to be buried",
        "what is not ready",
        "who walked it"
      ],
      "sections": [
        {
          "h": "The pour this covers",
          "r": "Name it and its limits the same way the pour record will, the day and window it's going, and how it's going in."
        },
        {
          "h": "Ours, and it's ready",
          "r": "What our crew has done: forms, bracing, shoring, screeds and wet screed pins, steel tied, chairs and dobies set, keyway and waterstop in, blockouts framed, dowels set, access route and washout spot."
        },
        {
          "h": "Theirs, and we're about to bury it",
          "r": "Every item belonging to somebody else that this pour covers or encases, and for each one whether that party walked it and told us it's set. Where nobody walked it, say so and ask for the walk before we order trucks."
        },
        {
          "h": "Not ready, or not what we expected",
          "r": "What we found on the walk that isn't right — grade soft or wet, water in the forms, embeds missing, layout that doesn't match the set in hand, access blocked, somebody still working in our footprint. Describe the condition. No fault, no fix proposed."
        },
        {
          "h": "When we have to know",
          "r": "Ask for the specific items to be released or corrected, and say when our crew has to know in order to hold or turn loose the trucks and the pump. That's our decision point, not a deadline we're putting on anybody."
        },
        {
          "h": "Who walked it",
          "r": "Who came from each party, who was asked and didn't show, and the photo list with locations."
        }
      ]
    },
    {
      "id": "directed-work-confirmation",
      "name": "Directed Work Confirmation",
      "aka": [
        "directed work",
        "told to do it",
        "verbal direction",
        "confirmation letter",
        "field direction",
        "he told me to"
      ],
      "family": "notice",
      "from": "the foreman who was directed",
      "to": "whoever gave the direction, copy to the GC and our PM",
      "why": "A conversation on a form deck becomes a record the same day or it becomes two people remembering it differently in November.",
      "note": "Narrative only. No rate, no total, no hours priced out — the tag carries the counts and the office owns the number.",
      "omit": "The line that says you asked for it in writing and what came back — \"I asked for written direction on the twelfth; as of this letter I still don't have it.\" Every one of these names who gave the direction. Almost none record the ask for paper and the silence after it, which is the whole reason the letter exists.",
      "halt": "Only if there is no stated direction and no person who gave it.",
      "facts": [
        "who gave the direction and when",
        "how it arrived",
        "what you understood you were told to do",
        "what your crew actually did",
        "whether you asked for it in writing"
      ],
      "sections": [
        {
          "h": "The direction, in their words",
          "r": "Who gave it, their job, when, where, and how it came — face to face at the pour, radio, phone, text, email, marked-up set, paint on the grade. What was actually said, as close as the foreman can get it, and say whether you're quoting or paraphrasing."
        },
        {
          "h": "What we understood we were told to do",
          "r": "The work as our crew took it, in field terms, tied to a location — grid, footing mark, bay, level, station, address. If it's not clear, say what isn't and ask them to confirm it."
        },
        {
          "h": "How it's different from what we came to do",
          "r": "What the crew was manned, formed and set up for, and how the direction changes it — extra pours, resequencing, re-set layout, re-tied steel, added dig, standby, protection, working a day we'd called off. Describe the difference. Argue nothing and put no number on it."
        },
        {
          "h": "What we did",
          "r": "Went ahead, held, or partly went ahead, and when. If we went ahead with responsibility still open, one plain line: performed as directed, responsibility not agreed."
        },
        {
          "h": "We asked for it in writing",
          "r": "Who we asked, when, how, and what's come back — including nothing. Then ask again inside the letter."
        },
        {
          "h": "Field facts attached",
          "r": "The tag, the photo log, crew and equipment counts, hours, quantities, and any pour record or notice already in the file for that spot. Quantities and conditions only — no rates, no totals anywhere in this letter."
        }
      ]
    },
    {
      "id": "conditions-notice",
      "name": "Not What We Came For (Grade and Bottom)",
      "aka": [
        "differing conditions",
        "not as shown",
        "subgrade",
        "bad dirt",
        "rock",
        "found in the hole",
        "unforeseen"
      ],
      "family": "notice",
      "from": "the foreman on the hole",
      "to": "the GC super and our PM",
      "why": "The hole is open for one afternoon. A condition nobody wrote down while it was open is a condition that never existed.",
      "note": "States what was seen and what the crew did. It never states a cause, never grades the material, and never says what the design should have been.",
      "omit": "The line that pins the condition to a place and a time while it was still open — footing mark, grid, station or address, what day and what hour, who saw it standing there, and that the crew stopped and called before covering it. A picture of mud with nothing in the frame to locate it proves nothing to anybody.",
      "halt": "Only if the condition itself is not described.",
      "facts": [
        "where — footing mark, grid, station or address",
        "what you found",
        "what you came expecting off the set",
        "what the crew did when they found it",
        "who you called and when"
      ],
      "sections": [
        {
          "h": "Where we were working",
          "r": "Name the hole or the subgrade by footing mark, grid, pier, grade beam run, station, pad or address, and what was going in it that day."
        },
        {
          "h": "What we found",
          "r": "Field words only — soft, pumping, wet, running, sloughing, bottom below what the set showed, rock, an old footing or slab, a wall, a line in the trench. How it showed itself: what the machine did, what the bottom did underfoot, what came up on the bucket."
        },
        {
          "h": "What we came expecting",
          "r": "What the field set or the layout handed to the crew showed at that spot, plain, and name the sheet. Don't interpret it and don't guess why it's different."
        },
        {
          "h": "What the crew did when we found it",
          "r": "Stopped or kept going, who got told, what time, how, and what came back. If we were told to keep going, say who said it and what they said."
        },
        {
          "h": "What it's doing to our work",
          "r": "Field facts only: extra dig, extra mud, extra forming, hand work, crew standing, iron sitting, pour split, days moved. Quantities, hours and conditions — no prices."
        },
        {
          "h": "The ask",
          "r": "Ask somebody to come look while it's still open, and ask for written direction on how to go. Say when the hole has to get covered or the crew has to move — that's our constraint, stated as ours."
        }
      ]
    },
    {
      "id": "weather-protection-notice",
      "name": "Weather Day and Protection",
      "aka": [
        "weather day",
        "rained out",
        "cold",
        "blankets",
        "protection",
        "froze",
        "we covered it"
      ],
      "family": "incident",
      "from": "the foreman",
      "to": "the GC super and our PM",
      "why": "Everybody logs the weather day. Almost nobody logs the tending — the trips back at night and on the weekend to check it, re-lay it, pump it off and finally pull it — which is the part that costs a crew and never appears on anybody's paper.",
      "note": "Records what the crew saw and did. It never states whether the concrete was harmed, and it never grades what came out of it.",
      "omit": "The tending. The trips back at night, on the weekend and before shift to check it, re-lay it, pump it off, re-anchor it and finally pull it, and the men who made those trips. Everybody logs the weather day. Nobody logs the days of babysitting the cover, which is where the hours actually went.",
      "halt": "Never halt. Write the day, mark the rest <MISSING>, send it.",
      "facts": [
        "the date and what the weather did",
        "who made the call",
        "what went down and whose it was",
        "every trip back, and who made it",
        "what you are asking for"
      ],
      "sections": [
        {
          "h": "The day and what it hit",
          "r": "Date, the placement or area, and what was scheduled that the weather touched — a pour, a strip, saw cuts, a finish, backfill."
        },
        {
          "h": "What the crew saw",
          "r": "The way it looked on the ground: water in the forms or on the grade, mud, wind across a fresh finish, sun and drying, cold on green work, ice, rain during finishing. What we saw — no readings off anybody's gauge and no reading of the forecast."
        },
        {
          "h": "Who made the call",
          "r": "We called it off, we were told to keep going, or we were told to come back — who said it, when, how — and what our own read was at that moment. If the two didn't match, say so plain and leave the argument out."
        },
        {
          "h": "What went down and whose it was",
          "r": "Cover, blankets, plastic, sand, heat, shade, wind break, barricade — where it went, who called for it, and whose material it was."
        },
        {
          "h": "Every trip back",
          "r": "Date, time, who went, what they found, what they did — re-laid, re-anchored, pumped off, added, pulled. Log the removal the same way. This is the part that gets left out of every one of these."
        },
        {
          "h": "What we're asking for",
          "r": "Direction on keeping protection on it and who carries it from here, and as field fact, what days got lost, moved or worked."
        }
      ]
    },
    {
      "id": "strip-and-shore-notice",
      "name": "Strip, Shore and What Got Loaded On It",
      "aka": [
        "strip",
        "stripping",
        "shores",
        "reshore",
        "forms out",
        "release",
        "loaded the deck"
      ],
      "family": "notice",
      "from": "the foreman",
      "to": "the GC super and our PM",
      "why": "Forms and shores stay up until the person who owns that call says otherwise, and meanwhile somebody is stacking material on a deck that is still holding itself up on posts.",
      "note": "This asks for a release. It never states that the concrete has reached anything, and it never sets its own date for a strip — that call belongs to whoever owns it on your job.",
      "omit": "What got set on the slab or deck before we were turned loose to strip — material stacked, stock landed, a lift rolled on, equipment traffic — who put it there and when. A deck loaded while it's still green and still shored is nobody's fault in the file unless somebody wrote down who put the load on it.",
      "halt": "Only if it is not stated what is coming down or staying up.",
      "facts": [
        "what is coming down or staying up",
        "why it is still standing",
        "the release you are asking for and from whom",
        "what is sitting on it right now",
        "what the face looked like on strip"
      ],
      "sections": [
        {
          "h": "What's coming down or staying up",
          "r": "By grid, bay, level, pour number or address — wall forms, column forms, deck forms, edge forms, blockout forms, shoring, reshoring — and whether the crew is stripping, leaving it standing, or holding for direction."
        },
        {
          "h": "Why it's still standing",
          "r": "If forms, shoring or bracing are staying up past our pour, say whose ask that is and what it's held for — somebody's inspection, a walk, a test, a follow-on trade, a hold called at the trailer. Name who asked and when."
        },
        {
          "h": "The release we're asking for",
          "r": "Ask in writing for release to strip from the party who owns that call on this job, and give our own constraint — men scheduled, equipment scheduled, the next pour this feeds. Put no strength, no age and no criterion in this letter; that call isn't ours to supply."
        },
        {
          "h": "What's sitting on it right now",
          "r": "What's gone on top of the slab or deck since we poured: stacked material, landed stock, a lift, equipment, traffic, another trade working. Who put it there, when, what our crew saw. This is the part everybody skips and then needs."
        },
        {
          "h": "What the face looked like on strip",
          "r": "Observation only: honeycomb, form marks, tie holes, snap ties, blowouts, edges, blockout corners, joint faces. What our crew intends to handle as its own work, and what we're asking somebody to come look at before anybody touches it."
        }
      ]
    },
    {
      "id": "cold-joint-notice",
      "name": "Stopped Pour / Cold Joint",
      "aka": [
        "cold joint",
        "stopped pour",
        "truck never came",
        "joint",
        "we had to stop",
        "short load"
      ],
      "family": "incident",
      "from": "the foreman who was at the face",
      "to": "the GC super and our PM",
      "why": "A joint the drawing does not show now exists in the structure. Written that day it is a record; written when somebody finally asks, it is a reconstruction.",
      "note": "Records where the joint is and what happened. It never states whether the joint is acceptable, what treatment it needs, or who is responsible — those are the engineer's and the office's.",
      "omit": "The call log — who you called the minute the concrete stopped coming, what time, and what they said back — written down before the joint existed instead of rebuilt after. Every one of these names where the joint is. Almost none show the crew raised it while there was still time to keep it from being one.",
      "halt": "Never halt. Write where it is and when it happened, mark the rest <MISSING>, and send it before you go home.",
      "facts": [
        "where the joint is",
        "what time the concrete stopped coming",
        "every call you made and what came back",
        "what you did at the face",
        "what you are asking for"
      ],
      "sections": [
        {
          "h": "Where it stopped",
          "r": "Name the pour, then pin the stopping line: grid, bay, wall, lift, station or address, and where in the section it sits. Footing, grade beam, wall, column, deck, slab on grade or topping."
        },
        {
          "h": "Why the concrete quit coming",
          "r": "What the crew saw or was told: trucks quit showing, short load, pump plugged or down, boom had to move, line washed out, access blocked, power or safety hold, told to hold. Don't grade anybody's performance and don't name a party at fault."
        },
        {
          "h": "The clock and every call out",
          "r": "Time the last load discharged, then every call, radio call and text — time, who, what came back — and the time concrete started again or the pour got shut down. This gets written the same day, before memory smooths it out."
        },
        {
          "h": "What we did at the face, and how we left it",
          "r": "Face squared or cut back, roughened, keyway formed, bars or dowels left running through, waterstop handled, joint cleaned, cover placed. What got finished, what was left green, what protection went on it, what's left to place on the other side. What was done — never what should be done."
        },
        {
          "h": "What we're asking for",
          "r": "Ask that somebody come look at the joint and send direction back on how they want it handled, and say the crew is holding for that. Don't propose a treatment, a repair or an opinion on what it'll carry."
        }
      ]
    },
    {
      "id": "damage-reply",
      "name": "Not Our Work — Damage and Crack Reply",
      "aka": [
        "not our work",
        "crack",
        "damage",
        "they say it's ours",
        "somebody drove on it",
        "chipped it"
      ],
      "family": "incident",
      "from": "the foreman or the PM who went and looked",
      "to": "whoever raised it, copy to the GC and our PM",
      "why": "Somebody has put your name on something. The reply that wins is not the one that argues hardest about the crack — it is the one that establishes when the work left your hands and who has had it since.",
      "note": "States what was placed, what was seen, and when it left your hands. It never asserts what caused a crack and never says who pays — a concrete foreman cannot know the first and does not decide the second.",
      "omit": "The handoff line: the last date and hour our crew was on that work, what shape it was in when we walked, what protection we left, and who had the area after us. Everybody argues the crack and forgets to establish when the work left our hands — the only fact in the whole letter we actually own.",
      "halt": "Only if it is not stated what came in.",
      "facts": [
        "what came in and when you went and looked",
        "what you placed there and when",
        "what you saw on the walk",
        "the last date your crew was on it",
        "who has had the area since"
      ],
      "sections": [
        {
          "h": "What came in, and when we went and looked",
          "r": "What we got — photo, punch item, email, phone call — who sent it, the date it came, and the date and hour our people physically went out and looked."
        },
        {
          "h": "What we placed there",
          "r": "Our scope at that spot: what we formed, what we placed, when, how it was finished, what we left on it for protection. Point at the pour record and photo log for that pour by their dates. Facts about our own work only."
        },
        {
          "h": "What we saw on the walk",
          "r": "Field words: where it is, which way it runs, whether it runs through a joint or dies at one, surface or full depth as far as you can see, spalling, chipping, tire tracks, saw or score marks, gouges, stains, broken edge, movement at an edge. Describe it. Don't diagnose it."
        },
        {
          "h": "The line we don't cross",
          "r": "This letter never states a cause. Not that the grade failed, not that the design is short, not that a trade overloaded it, not that somebody's machine did it — a concrete hand can't know any of that. What we saw goes in as a dated observation: what was parked on it, stacked on it, cut into it, and what the surface looked like at the time. Anything about cause is a question we're asking, never an answer we're giving."
        },
        {
          "h": "When it left our hands, and who's had it since",
          "r": "Last date and hour our crew worked there, what shape it was in then, what cover, barricade or protection we left standing, who we told it was ready or handed it to, and who's had access since as far as our people saw."
        },
        {
          "h": "What we're asking for",
          "r": "Ask that the parties who determine cause come look, ask that it be protected in the meantime so there's still something to look at, and say what our crew will do at direction while cause is still open — performed at direction, responsibility not agreed."
        }
      ]
    }
  ],
  "overrides": {
    "delay-notice": {
      "name": "We Got Held",
      "omit": "Who and what actually stood — the men by name and classification, the iron by piece, the pump and the trucks ordered and where they went — and what the crew would have been doing instead. \"We were held from morning to noon\" with no names and no idled equipment is a sentence nobody can check and nobody can act on.",
      "sections": [
        {
          "h": "The hold and the clock",
          "r": "What was being held and where, the time the crew was ready, the time the hold started, the time it turned loose or the crew went home. Who called it, or who we were waiting on."
        },
        {
          "h": "Why we couldn't go",
          "r": "Field terms: another trade still in our footprint, embeds or sleeves not set, layout not released, grade not ready, road blocked, pump or boom couldn't set, forms held for somebody else's look, inspection not made yet."
        },
        {
          "h": "Who and what stood",
          "r": "The men who stood and their classifications, the equipment idled by piece, the pump and trucks ordered, held, turned loose or sent back. Counts of men, counts of hours, counts of pieces. No rates, no totals."
        },
        {
          "h": "What we were set up to do",
          "r": "The work the crew was manned, formed and geared up for in that window, so the hold reads against something real."
        },
        {
          "h": "Who we told",
          "r": "Who got told at the time, when, how, what came back, and whether we asked to be turned loose or moved somewhere else and what came of it."
        }
      ],
      "facts": [
        "what you were held by and who owns it",
        "the clock — when the crew got there and when it went",
        "the men, by name and classification, who stood",
        "the iron, the pump and the trucks that stood",
        "who you told, and when"
      ]
    },
    "daily-report": {
      "omit": "WHAT WENT IN THE GROUND TODAY AND WHAT IS UNDER IT. Every other trade's daily can leave the day at \"we got this far\". A concrete daily that does not say what was placed, where the placement started and stopped, and whose work went under it is missing the only lines anybody comes back for — and unlike a wall or a ceiling, nobody can open it up and look."
    }
  },
  "drop": [],
  "vocab": [
    "ess oh gee -> SOG",
    "slab on grade -> slab-on-grade",
    "grade beam -> grade beam",
    "stem wall -> stem wall",
    "pea gravel -> pea gravel",
    "three quarter rock -> 3/4 rock",
    "lean mix -> lean mix",
    "mud slab -> mud slab",
    "dobie -> dobie",
    "chair -> chair",
    "tie wire -> tie wire",
    "rodbuster -> rodbuster",
    "top mat -> top mat",
    "you fer -> Ufer",
    "yoofer -> Ufer",
    "wire mesh -> mesh",
    "dowel basket -> dowel basket",
    "water stop -> waterstop",
    "key way -> keyway",
    "block out -> blockout",
    "box out -> boxout",
    "weld plate -> weld plate",
    "embed -> embed",
    "anchor bolt -> anchor bolt",
    "hold down -> hold-down",
    "pee tee -> PT",
    "post tension -> post-tensioned",
    "re shore -> reshore",
    "pour strip -> pour strip",
    "closure strip -> closure strip",
    "cold joint -> cold joint",
    "control joint -> control joint",
    "saw cut -> saw cut",
    "early entry -> early-entry saw",
    "green cut -> green cut",
    "wet screed -> wet screed",
    "bull float -> bull float",
    "fresno -> fresno",
    "power trowel -> power trowel",
    "ride on -> ride-on trowel",
    "broom finish -> broom finish",
    "hard trowel -> hard trowel",
    "dry shake -> dry shake",
    "cure and seal -> cure-and-seal",
    "curing compound -> curing compound",
    "vapor barrier -> vapour barrier",
    "boom pump -> boom pump",
    "line pump -> line pump",
    "power buggy -> power buggy",
    "short load -> short load",
    "wash out -> washout",
    "batch plant -> batch plant",
    "dispatch -> dispatch",
    "ticket -> delivery ticket",
    "cylinder -> cylinder",
    "break -> break test",
    "ay hitch jay -> AHJ",
    "ee oh are -> EOR"
  ],
  "reminders": [
    "When a placement, a pour or a slab is described -> remind them to say where it STARTED and where it STOPPED, and what was deliberately left out — a blockout, a pour strip, a deferred bay. Everybody writes the date. Almost nobody writes the line on the floor, and the line on the floor is what the crack question turns on years later.",
    "When another trade's sleeves, conduit, embeds, hold-downs, anchor bolts, dowels, waterstop, ground or under-slab work comes up -> remind them to name whose it is and that it was walked before it was covered. This is the only document that will ever show it existed; concrete is the one gate on a job that does not reopen.",
    "When a delivery ticket, a lab report, a break result, an inspection or a mix submittal comes up -> remind them to reference it by its own number and NEVER to retype what is on it. The plant owns its ticket, the lab owns its report and the inspector owns his — retyping somebody else's numbers into our letter is how a transcription error becomes our statement.",
    "When water, retarder, accelerator or anything else added on the ground comes up -> remind them to record WHO called for it and at what time, and never to state whether it was acceptable. It is the first question asked when a cylinder comes back low, and the only wrong answer is that nobody wrote it down.",
    "When a crack, a chip, a scale, a wheel track or any damage to placed work comes up -> remind them to establish the LAST DATE their crew was on that work, what protection they left, and who has had the area since — and never to state a cause. A concrete hand may say what he placed and what he saw. He may not be made to say why it cracked.",
    "When stripping, shoring, reshoring, backfill, saw cutting, loading or driving on placed work comes up -> remind them to name the person whose call that is on this job and to ask for the release in writing. Never let the document state that the concrete has reached anything or is ready for anything — that is a strength statement and it is not ours to make.",
    "When yards, loads, trucks, square feet or lineal feet are mentioned -> remind them to state the unit they actually counted in and never to convert between units in the document. A conversion nobody checked is how an order and a claim both go wrong."
  ]
};
