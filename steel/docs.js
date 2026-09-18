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
      "family": "directive",
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

  "overrides": {
    "delay-notice": {
      "name": "The Day We Couldn't Fly",
      "from": "the foreman on the ground",
      "to": "the GC super and our PM",
      "omit": "THE GATE IT COST AND THE CLOCK ON THE CRANE. \"We couldn't work\" is a sentence nobody can price. \"Crane on site 6:30, wind held the pick until 11, released for the day at 2 — the level-2 beams that were the day's set didn't go\" is a hold a super and the office can both read, and the crane clock is the number the day turns on.",
      "needs": ["who", "where"]
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
