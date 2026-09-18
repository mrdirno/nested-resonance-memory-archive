/* STEEL & MISC METALS FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the shared library and
 * every universal law in it; this file owns what is different about steel work
 * and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS TORQUED, TENSIONED, SIZED, RATED, GRADED, OR JUDGED. No torque
 *     value, no weld size or map, no bolt tension, no capacity, no material
 *     grade, no embed tolerance, no plumb/level number, no verdict that a
 *     connection holds or a weld is good — not as a value, not as a hint, not in
 *     a placeholder. The foreman states what he SAW and what the SHEET SAID;
 *     nobody here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *
 * WHY THIS TRADE'S LIBRARY LEANS SO HARD ON THE ENGINE'S "NEVER GRADE" LAW.
 * Steel write-ups get read by detailers, engineers of record, special
 * inspectors, carriers and lawyers, and the one place a certified number leaks
 * in is through the AI when it is asked to write a steel letter. So every
 * document below adds the refusals this trade specifically needs — CAUSE (whose
 * fault the mismatch is) and ADEQUACY (whether the steel holds) — and says so in
 * its own words. A foreman may say what he found and what he was told. He may
 * not be made to say who is at fault or whether it works.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TRADE_DOCS = {
  "trade": "steel",
  "docs": [
    {
      "id": "field-vs-set",
      "name": "What the Field Didn't Match",
      "aka": [
        "field condition",
        "doesn't match the drawing",
        "differing condition",
        "rfi backup",
        "field fit",
        "doesn't fit",
        "field conflict",
        "interference",
        "as-built doesn't match",
        "conflict with the set"
      ],
      "family": "notice",
      "from": "the foreman on the steel",
      "to": "our detailer and PM, and through them the GC and the engineer of record",
      "why": "The only record of what the field actually was on the day it didn't match the stamped set. It is read by the detailer writing the RFI and later by whoever decides who pays for the fix.",
      "note": "This is the FIELD RECORD behind an RFI or a change request — it is not the RFI and not the fix. The detailer owns the RFI number and the engineer owns the resolution; this states what is there, never what to do about it.",
      "omit": "THE SHEET AND DETAIL NUMBER IT DOESN'T MATCH, AND THE DIMENSION OFF YOUR OWN TAPE, separately from the drawing's. \"It doesn't fit\" is nothing a detailer can draw a fix from. \"Detail 6/S-501 shows the clip at top of steel and it's low off my tape, at column C-4, photo attached\" is.",
      "needs": ["where"],
      "halt": "Never halt. Write what is known, mark the rest <MISSING>, photograph it and send it — a field conflict found and not sent is the one that gets built wrong.",
      "facts": ["the date and the area or grid line", "the sheet and detail it's off", "what the drawing shows", "what the field actually is, off your own tape", "who you told and when"],
      "sections": [
        {
          "h": "WHAT THE SHEET SHOWS, AND WHAT'S THERE",
          "r": "Two answers, in that order, never collapsed. The sheet: the drawing number, the detail, and what it calls for, quoted as it reads. The field: what is actually there, off your own tape, and the reference you measured from — a column line, a benchmark. Photograph it with something fixed in frame. Never re-draw the connection and never say which one is right — that is the engineer's."
        },
        {
          "h": "WHAT IT STOPS OR HOLDS",
          "r": "What you can't set, weld or close until it's answered, and the gate it's holding — the crane, the deck, the pour. Plainly, so the detailer knows how fast the RFI has to move. Never a fix, never a capacity call, never \"it'll work anyway.\""
        },
        {
          "h": "WHAT I DIDN'T CHECK",
          "r": "The part that protects you. What you couldn't reach, couldn't get a tape on, or couldn't see behind other work. If you didn't measure it, say you didn't measure it."
        },
        {
          "h": "WHAT I'M NOT SAYING",
          "r": "Two refusals, stated on purpose, because both get read into a steel letter that leaves them out. This does not say the connection is inadequate or unsafe, and it does not say whose fault the mismatch is — the fabricator's, the field's, or the drawing's. If you were asked for either, write that you were asked and that it needs the engineer and the office."
        },
        {
          "h": "WHAT HAS TO HAPPEN NEXT",
          "r": "One line: the RFI answer or the marked-up sheet has to come back before the gate. Name the gate and the date. Never let \"we'll figure it in the field\" be the plan on engineered steel."
        }
      ],
      "secondary": ["a short RFI-request line for the detailer with the sheet and detail number on it", "the same conflict stated for the GC's log with the internal detail stripped"]
    },
    {
      "id": "found-before-i-set",
      "name": "What I Found Before I Set",
      "aka": [
        "found before i set",
        "pre-set walk",
        "bolts are off",
        "anchor bolts off",
        "embed check",
        "walk before setting",
        "bolt pattern",
        "it was like that before i set",
        "found it at the bolts"
      ],
      "family": "verification",
      "from": "the foreman walking it before the crane",
      "to": "the GC super and our PM, and through them whoever set the bolts",
      "why": "The only record of what the bolts and embeds looked like the morning you went to set, before your steel covered them. Read later by whoever decides whether a set problem started before you got there.",
      "note": "Narrative and counts only, off your own tape, never a tolerance call. If it's out enough to stop you, that's a come-ask-me, not a fix you make.",
      "omit": "WHICH ONES, WHERE, AND WHAT YOU SAW off your own tape, against the column line, photographed. \"The bolts are off\" stops nobody's clock. \"Column line C-4, the pattern looks rotated and one bolt's short of the plate off my tape, photo attached\" is a row concrete and the GC can act on before the crane sits.",
      "needs": ["where", "count"],
      "halt": "Only if there is no job or area at all. Otherwise write it, photograph it, and send it before you set — after your column's on it, nobody can see what was under it.",
      "facts": ["the date and the area or column line", "what you were setting to", "what you found, off your own tape", "how many and where", "who you told and when"],
      "sections": [
        {
          "h": "WHAT I FOUND, WHERE, AND HOW MANY",
          "r": "One line per column line or embed. What it is — a bolt pattern that looks rotated, a plate hanging over, a bolt short of the plate, an embed not where the sheet puts it, no grout under the base — then WHERE off the column line, then WHAT you saw off your own tape. Photograph each with the line marked. Never a tolerance number and never \"out of spec\" — what you saw, in your words."
        },
        {
          "h": "WHAT IT STOPS",
          "r": "What you can't set on it and the gate it's holding — the crane's booked, the bay's next — so whoever owns the bolts knows how fast this has to move. Never a fix and never a call that it's unsafe."
        },
        {
          "h": "WHAT I'M NOT SAYING",
          "r": "This does not say the bolts are out of tolerance, the pour is bad, or whose fault it is — those are the engineer's and the surveyor's, off their own instruments. I'm saying what I saw and that I stopped and asked before I set."
        },
        {
          "h": "WHAT HAS TO HAPPEN NEXT",
          "r": "Who's looking at it, and whether I'm holding the crane on it. One owner, one date."
        }
      ],
      "secondary": ["a one-line hold to the crane coordinator naming the gate", "the same finding for the GC's log"]
    },
    {
      "id": "directed-to-set",
      "name": "Directed to Set It Anyway",
      "aka": [
        "directed to set",
        "told to set it",
        "set under protest",
        "confirm in writing",
        "go ahead and set",
        "told to keep going",
        "proceed under direction",
        "set it anyway"
      ],
      "family": "notice",
      "from": "the foreman who was told to keep going",
      "to": "our PM and the GC super, on the record",
      "why": "The record that you raised it, named the condition, and were directed to set anyway — dated, before your steel covered it. It is the backup a change request or a claim is built on later.",
      "note": "This states that you were directed and by whom, and what the condition was — never that the direction was wrong, and never what it will cost. The office owns the price and the change number.",
      "omit": "WHO DIRECTED YOU, WHEN, AND HOW — a name, a time, and whether it was verbal, texted or on a sheet. \"They told me to keep going\" is not a record. \"Super D, 7:15 at the gang box, verbal, asked to confirm in writing\" is.",
      "needs": ["when", "who"],
      "halt": "Only if there is no condition named — a directed-to-proceed with nothing you flagged first is just a day's work.",
      "facts": ["the date and time", "who directed you and how", "the condition you flagged first", "the area or grid line", "what you did after"],
      "sections": [
        {
          "h": "WHAT I FLAGGED, AND WHEN",
          "r": "The condition you raised before you set — the open RFI, the embed not in, the bolt off, the drawing that didn't match — and the time you raised it, off your leave-out or field-condition record if you have one. Point to it."
        },
        {
          "h": "WHO DIRECTED ME TO SET IT",
          "r": "The name, the time, and how — verbal at the gang box, a text, a marked sheet. If it was verbal, this document is the ask to confirm it in writing, and it says so."
        },
        {
          "h": "WHAT I DID",
          "r": "What you set and where, plainly, so the record shows the steel went in under direction and not on your own call. Never a verdict that it's fine and never that it isn't — you did what you were directed to do."
        },
        {
          "h": "WHAT I'M NOT SAYING",
          "r": "This does not say the direction was wrong, the steel is inadequate, or what the fix will cost. It says you raised it, you were told to proceed, and here's the dated record."
        }
      ],
      "secondary": ["a one-line written-confirmation request to whoever directed you", "the dated entry for our own change-order file"]
    }
  ],

  "drop": [],

  /* ── OVERRIDES — the shared documents, re-addressed to steel (measured at the
   * real search box, C3737). Steel stood up as trade #19 carrying ONE override
   * (delay-notice); the other ten shared documents rendered in the rack's generic
   * voice, and a steel foreman's own words landed on the wrong shelf — "erection
   * sequence" and "next lift" handed back the Service Call, "crane access" and
   * "laydown" the Extra Work letter, "topped out" the Service Call, "bolt up" the
   * Extra Work letter, "dropped a load" and "fall" the Service Call. These
   * re-address the erection lifecycle in the foreman's voice and route his words
   * to the document he means. Every one still obeys this file's rails: `reminders`
   * below keeps torque, weld size, capacity, tolerance, grade and CAUSE out of
   * whatever the AI writes on ALL of them, so none carries a graded value. Sections
   * come from the family spine in shared/docspec.js, same as on every trade. */
  "overrides": {
    "delay-notice": {
      "name": "The Day We Couldn't Fly",
      "from": "the foreman on the ground",
      "to": "the GC super and our PM",
      "omit": "THE GATE IT COST AND THE CLOCK ON THE CRANE. \"We couldn't work\" is a sentence nobody can price. \"Crane on site 6:30, wind held the pick until 11, released for the day at 2 — the level-2 beams that were the day's set didn't go\" is a hold a super and the office can both read, and the crane clock is the number the day turns on.",
      "needs": ["who", "where"]
    },
    "daily-report": {
      "from": "the foreman on the steel",
      "to": "our PM and the office, and the GC's daily",
      "why": "The one your PM forwards and the GC pastes into his own. On steel it is the record of what got set, what got bolted up and welded out, and what is holding the next lift — the trail the whole sequence gets read back through.",
      "omit": "THE THING YOU CHANGED TO KEEP THE HOOK MOVING — a piece flown out of sequence, a bolt bag robbed off another bay, an approved hour nobody logged, a connection made up a different way to fly the next one. Nobody writes it the day it happens, and at the change meeting three months on there is no paper for it.",
      "note": "\"Bolted up\" and \"welded out\" state the crew's work for the day, not that a joint is complete, sound or accepted — inspection is the special inspector's and the CWI's.",
      "needs": ["who", "change"],
      "facts": ["the date and the area or grid line", "the raising gang and their hours", "what got set, bolted up and welded out", "what is left loose, unmade or unwelded", "what is holding the next lift", "crane hours, and the hours the hook stood idle"],
      "aka": ["daily", "dfr", "end of day", "eod", "field report", "daily update", "erection daily", "what we set", "pieces set", "bolt up", "bolted up", "made up", "welded out", "set today", "crane time", "decking"]
    },
    "look-ahead": {
      "from": "the foreman on the steel",
      "to": "our PM and the GC, and the crane coordinator",
      "why": "The one that keeps the raising gang and the crane from standing. On steel it is the sequence — which picks fly in what order next, and what has to be true before each one: the bolts in, the embeds set, the deck below poured, the crane's road clear.",
      "omit": "WHAT HAS TO BE TRUE BEFORE EACH LIFT — the other trade's work, the survey, the delivery, the released RFI. A sequence with no preconditions is a wish list, and on steel it is the wish list that puts the crane on the ground.",
      "needs": ["notdone"],
      "facts": ["the period", "the raising gang expected", "the picks planned, in order", "what has to be shaken out and staged", "what has to be set, poured or released first"],
      "aka": ["look ahead", "lookahead", "two week", "three week", "next week", "plan", "sequence", "erection sequence", "raising sequence", "next lift", "lift plan", "what's ready to set", "what has to be in before we fly"]
    },
    "site-walk": {
      "from": "the foreman or PM walking it before the iron",
      "to": "our office, and the crane coordinator",
      "why": "Everything you saw before the steel shows up, in a form somebody who was not there can plan the crane and the shakeout from. On steel the walk is the ground and the air: where the crane sets, what it reaches, what it swings under, and where the iron lands.",
      "omit": "ACCESS AND THE OVERHEAD — where the crane sets and what it swings under, where the trucks turn and lay down, the power line nobody drew, and what is NOT built yet that a pick has to clear. It never makes the notes, and it is what grounds the crane on the day.",
      "needs": ["when", "where", "notdone"],
      "facts": ["the date and the site", "who walked it", "where the crane can set and what it reaches", "where steel can be shaken out and staged", "what is overhead, and what is not built yet"],
      "aka": ["walk", "site visit", "survey", "site survey", "walkthrough", "pre-erection walk", "crane access", "crane pad", "where the crane sits", "laydown", "laydown area", "shakeout", "shake out", "shakeout walk", "overhead line", "access for the crane"]
    },
    "handover": {
      "name": "Topped Out — Turning the Frame Over",
      "from": "the foreman on the steel",
      "to": "the GC and our PM, and whoever takes the frame next",
      "why": "The last thing read on the steel and the first thing blamed. Written right it ends our scope on the frame — set, bolted up, welded out, the punch named and owned. Written as if it is all finished, every loose bolt and every touch-up becomes warranty.",
      "omit": "THE PUNCH YOU ARE HANDING OVER KNOWN — the loose bolts, the missing clips, the coating touch-up — each with an owner and a date. A turnover that reads as if the frame is complete adopts every one of them.",
      "needs": ["when", "who", "notdone"],
      "facts": ["the area or the frame being turned over", "what is set, bolted up and welded out", "what is still loose, unmade or missing a clip", "the coating touch-up left, and who owns it", "what the inspector still has open, and who you told"],
      "note": "Never write that a connection, a weld or the frame is adequate, complete, sound or good — state what is set, bolted up and welded out, and what the special inspector and the CWI still have open. Completeness and adequacy are the EOR's and the inspector's, off their own record.",
      "secondary": ["a version for the GC and the next trade", "the punch on its own, with an owner and a date on each line"],
      "aka": ["handover", "turnover", "closeout", "hand off", "handoff", "close out", "punch complete", "punch", "punch list", "topping out", "frame complete", "final bolt-up", "touch up", "touch-up paint", "turned it over"]
    },
    "damage-found": {
      "from": "the foreman who found it",
      "to": "the GC super and our PM, and our detailer",
      "why": "You found steel that was cut, burned, bent or welded to — in the yard, in shipping, or by another trade after it was set. This is the dated, photographed record that it was that way when you found it, before anyone goes looking for who pays.",
      "omit": "THE DATE, THE GRID LINE OR PIECE MARK, AND WHERE THE PHOTOS LIVE. A description with no mark, no date and no photo reference is nothing in a back-charge meeting.",
      "needs": ["when", "where"],
      "facts": ["the date and time found", "the grid line or piece mark", "what was cut, burned, bent or welded to", "photos taken, and where they live", "who you told and how"],
      "note": "Say what you found and photograph it. Never write who cut it or whose fault it is — who pays is the office's and the EOR's, off this dated record.",
      "aka": ["damage", "pre-existing", "found damage", "prior damage", "damaged beam", "bent in the yard", "coating holiday", "they burned my steel", "they cut my beam", "welded to my steel"]
    },
    "incident-report": {
      "aka": ["incident", "near miss", "accident", "injury", "safety report", "dropped load", "dropped a load", "a load came down", "fall", "fell", "struck by", "caught between", "flash burn", "hit by the load"]
    },
    "service-writeup": {
      "name": "Misc-Metals Come-Back — What I Found When I Went Back",
      "from": "the man who went back",
      "to": "our office, and the GC or the building",
      "why": "The misc-metals come-back — a rail that worked loose, a gate that dropped, a stair that moved, a bollard somebody backed into. What you found when you went back, what you did, and what is still open.",
      "omit": "WHAT YOU DID NOT DO, AND WHY — the anchor you could not reach, the second rail you did not open, the thing you found that is outside this call. Leave it out and you own it by silence.",
      "needs": ["notdone"],
      "facts": ["the call as it came in", "what you found at the piece", "what you did", "what it is doing now", "what is still open"],
      "aka": ["service", "call", "repair", "service report", "work order narrative", "trouble call", "came back", "callback", "rail came loose", "handrail loose", "gate dropped", "stair moved", "bollard hit"]
    }
  },

  "vocab": [
    "done age -> dunnage",
    "gus it -> gusset",
    "night plate -> knife plate",
    "sheer tab -> shear tab",
    "camber -> camber",
    "fay ing -> faying",
    "eee oh are -> EOR",
    "are eff eye -> RFI",
    "double bee ell -> double bottom chord",
    "base plate -> base plate",
    "bond beam -> bond beam",
    "head course -> head course",
    "spud wrench -> spud wrench",
    "drift pin -> drift pin",
    "misc metals -> misc metals",
    "colour -> color"
  ],

  /* ── REMINDERS — trigger-only, never nagging ──────────────────────────────
   * The block is what talks to the AI, and an AI asked to write about steel is
   * exactly where a torque, a weld size, a capacity or a "the connection is
   * fine" walks in on its own. trade.js and items.js keep the numbers off the
   * pages; these keep them, and the verdicts, out of the documents the AI
   * writes.
   */
  "reminders": [
    "When torque, bolt tension, snug-tight, turn-of-nut, pretension, TC bolts, a calibrated wrench or a bolt-up log comes up -> remind them that the value and the method live on the stamped set and in the special inspector's record, quoted by sheet number if at all. Never let the document supply a torque, a tension, a method, or say a joint was properly tightened.",
    "When a weld, weld size, a fillet, penetration, a weld map, a WPS, a welder cert or an inspection comes up -> remind them to record what was done and what they saw, in plain words. Never let the document supply a weld size, restate a WPS, say a weld is good, sound or complete, or reproduce the weld map — that is the CWI's and the engineer's record.",
    "When capacity, load, a rating, 'will it hold', safe to load, safe to stand on, a moment or a reaction comes up -> remind them that adequacy is the engineer's, off the stamped drawing. The foreman records what is there and what he was told; the document never says a member, a connection or a deck holds, is adequate, or is safe to load.",
    "When a material grade, A36, A992, a mill cert, a heat number, a coating spec, galvanizing thickness or paint DFT comes up -> remind them that the grade and the coating are the fabricator's and the spec's, cited by name if at all. Never let the document state a grade as a value, confirm a coating thickness, or say material met a spec.",
    "When tolerance, plumb, level, out-of-plumb, sweep, camber or a survey reading comes up -> remind them to record what they saw off their own tape, beside the reference they measured from, <MISSING> if not measured. Never let the document supply a tolerance, say a member is in or out of tolerance, or say the steel is plumb — the surveyor's instruments and the engineer own that call.",
    "When cause, fault, whose miss, or who pays comes up -> remind them that the document states what was found and who was told, never who is at fault or what it costs. Fabrication, field or drawing — the office and the engineer decide, and the write-up is the dated record they decide from.",
    "When the crane, a pick, rigging, a lift plan, a de-energize or an overhead line comes up -> remind them that the lift plan, the crane permit and the power-down are the site's and the utility's, recorded as facts observed. Never let the document supply a rigging capacity, say a pick was safe, or state a line was de-energized on the crew's own say-so."
  ]
};
