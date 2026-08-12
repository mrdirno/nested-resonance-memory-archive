/* ROOFING FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about roofing work and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS RATED, SIZED, SLOPED, THRESHOLDED OR JUDGED. No uplift value, no
 *     listed assembly, no fastener pattern, no slope minimum, no R-value, no
 *     warranty term, no acceptance criterion, no "should be" — not as a value,
 *     not as a hint, not in a placeholder. The roofer states what he found;
 *     nobody here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *
 * WHY THIS TRADE'S LIBRARY IS THE MOST DANGEROUS ONE IN THE PROGRAM, and what
 * that changed. Roofing write-ups are read by carriers, adjusters, manufacturers'
 * warranty departments and lawyers. The 4-lens roster fan-out (2026-08-12) put it
 * exactly: a block that tells a model to write a roofing letter is where the
 * certified data leaks in — not through the page, through the AI. So every
 * document below leans on the engine's standing "never invent, never grade" laws
 * and adds the two refusals this trade specifically needs: CAUSE and COVERAGE.
 * A roofer may say what he saw and what he did. He may not be made to say what
 * caused it or who pays for it, and the documents say so in their own words.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work")
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 */
window.TRADE_DOCS = {
  "trade": "roofing",
  "docs": [
    {
      "id": "leak-call-findings",
      "name": "Leak Call — What I Found",
      "aka": [
        "leak call",
        "leak report",
        "service call",
        "where is it coming in",
        "water intrusion",
        "roof leak",
        "investigation",
        "trouble call"
      ],
      "family": "verification",
      "from": "the service tech who went up",
      "to": "the property manager or building engineer, and our service coordinator",
      "why": "The only record of what the roof looked like on the day water was coming in. It is read months later by somebody deciding whether to repair or replace, and sometimes by somebody deciding who pays.",
      "note": "Narrative only. If the customer has their own service-ticket number, this goes with it — their ticket is theirs and we do not retype it.",
      "omit": "WHERE IT SHOWED UP INSIDE, separately from where you found it up top. They are almost never the same place, and the write-up that only names the roof spot is the one that gets read next year as proof you fixed the wrong thing.",
      "halt": "Never halt. If water is actively coming in, write what is known, mark the rest <MISSING>, and send it — a late leak report is worse than an incomplete one.",
      "facts": ["date and time you were on it", "the address and which roof area", "where it showed up inside", "what you found up top", "what you did today and whether it is temporary"],
      "sections": [
        {
          "h": "WHERE IT SHOWED UP INSIDE, AND WHERE I FOUND IT",
          "r": "Two separate answers, in that order, and never collapsed into one. Inside: the room, the ceiling grid or the wall, and who showed you. Up top: the roof area, and the distance and direction from something permanent — a drain, a curb, a wall, a grid line. If you could not correlate the two, write that plainly; an honest \"could not correlate\" is worth more than a guess that gets quoted back."
        },
        {
          "h": "WHAT THE ROOF ACTUALLY LOOKED LIKE",
          "r": "What you saw, in your words: condition of the membrane or the field, seams, flashings, terminations, penetrations, drains, ponding, debris, prior repairs, foot traffic, other trades' work sitting on it. Say how old and how many layers only if you actually determined it. NEVER a rating, an R-value, a slope, a fastening pattern, or a comparison to what the assembly is supposed to be."
        },
        {
          "h": "WHAT I DID TODAY, AND WHETHER IT HOLDS",
          "r": "The actions in order, and then the sentence everyone needs: is this temporary or permanent. If it is temporary, say what it is (patch, cut-off, plate, tarp, sealant) and that it needs a permanent repair — and say what weather it will and will not survive in plain language, not as a guarantee."
        },
        {
          "h": "WHAT I COULD NOT CHECK",
          "r": "The part that protects you. What was inaccessible, under water, under snow, under somebody's equipment, or dark. If you did not open it up, say you did not open it up. If you did not test it, say so."
        },
        {
          "h": "WHAT I AM NOT SAYING",
          "r": "Two refusals, stated on purpose, because both get read into a leak report that leaves them out. This does not determine the CAUSE of the leak and it does not determine who is RESPONSIBLE or whether anything is covered. If you were asked for either, write that you were asked and that it needs the office, the manufacturer or the consultant."
        },
        {
          "h": "WHAT HAS TO HAPPEN NEXT",
          "r": "One list, each item with an owner and a date. If the roof needs to be opened up to find it, say that is the next step and what it costs to do — do not let \"monitor it\" be the whole plan when it is going to rain again."
        }
      ],
      "secondary": ["a short message to the tenant or the occupant, with the internal detail stripped", "a leak history rollup from the previous calls in this thread"]
    },
    {
      "id": "found-under-it",
      "name": "What Came Up Under the Old Roof",
      "aka": [
        "tear off findings",
        "wet insulation",
        "bad deck",
        "deck report",
        "extra layer",
        "unforeseen",
        "differing conditions",
        "what we found",
        "supplement"
      ],
      "family": "notice",
      "from": "the foreman standing on the open deck",
      "to": "our PM and estimator, and through them the GC or the owner",
      "why": "It is the only window there will ever be. Once the new roof is over it, the evidence is gone and the conversation about who pays is unwinnable.",
      "note": "This is the FIELD RECORD that substantiates a change request — it is not the change order. The GC's log owns the number and our office owns the price.",
      "omit": "THE COUNT AND THE LOCATION, area by area, and the date you found each one. \"There was a lot of wet insulation\" is not a claim anybody can price. Six areas with squares and grid lines is.",
      "halt": "Only if this is the first one in the thread and there is no job or address at all.",
      "facts": ["date found", "the job and which roof area or slope", "what came up and how much of it", "what it stops you doing", "who you told and when"],
      "sections": [
        {
          "h": "WHAT CAME UP, WHERE, AND HOW MUCH",
          "r": "One line per area. What it is — wet insulation, rusted or rotted deck, an extra layer nobody disclosed, no nailer, failed fasteners, deteriorated blocking, saturated lightweight — then WHERE, off something permanent, then HOW MUCH in the count you actually took: squares, sheets, boards, linear feet, each. State the units you counted in. Never estimate a quantity you did not walk."
        },
        {
          "h": "WHY NOBODY COULD SEE IT BID DAY",
          "r": "One or two facts, not an argument. It was under the existing roof / it was not on the plan or the as-builts / the test cuts did not land here / the area was covered by somebody's equipment. This is the section that separates a differing condition from something you should have caught, so keep it factual and dated."
        },
        {
          "h": "WHAT IT STOPS, AND WHAT WE DID SO IT DIDN'T STOP EVERYTHING",
          "r": "The concrete consequence — this section cannot be insulated, this slope cannot be papered, this area cannot be dried in tonight — and then the work-around you already ran, so nobody can say you sat on it. Include what you did to keep the building protected in the meantime."
        },
        {
          "h": "THE DECISION I NEED, AND BY WHEN",
          "r": "One ask, with a date, and the date is real because the roof is open. What you need decided or authorised, who has to decide it, and what happens to the schedule and the exposure if the answer comes after that date. State it as a fact, never as a threat."
        },
        {
          "h": "WHAT THIS DOCUMENT IS NOT",
          "r": "It is not a price, not a change order and not a supplement — those come from the office. It also does not specify the repair: what the deck needs, how it should be fastened, or how far past the damage to go is the engineer's or the manufacturer's call, and this document does not answer it."
        }
      ],
      "secondary": ["a photo-log caption list, one line per photo, keyed to the areas above", "a short message to the GC asking for a walk before we cover it"]
    },
    {
      "id": "not-from-our-work",
      "name": "That's Not From Our Work",
      "aka": [
        "not our leak",
        "not our damage",
        "callback",
        "denial",
        "pre-existing",
        "wear and tear",
        "ponding",
        "response to a claim",
        "back-charge reply"
      ],
      "family": "notice",
      "from": "the foreman or service manager who went and looked",
      "to": "the GC, the owner, the property manager or the homeowner who is pointing at us",
      "why": "Somebody has decided the water is your fault. This is the one document that has to be calm, dated, specific, and completely free of the word \"we\" as a defence.",
      "note": "Answer the accusation that was actually made, on the area it was made about. Do not tour the whole roof.",
      "omit": "WHAT YOU DID CHECK AND FIND, before the part where you say it is not yours. A reply that only denies reads as a brush-off; a reply that shows the walk, names the area, and then draws the boundary reads as a professional record.",
      "halt": "Never halt. If the facts are thin, write what you verified and mark the rest <MISSING> — a defensive letter that arrives three weeks late has already lost.",
      "facts": ["date you looked", "the area or slope in question", "what you were told the problem was", "what you actually found", "what part of it IS ours, if any"],
      "sections": [
        {
          "h": "WHAT WE WERE TOLD, AND WHEN",
          "r": "Their words, close to verbatim, with the date and who said it. Never a characterisation of the person and never the word \"claims\"."
        },
        {
          "h": "WHAT WE WENT AND CHECKED",
          "r": "Date you were on it, who went, what you looked at and how — visual, water test, opened it up, moisture reading. Say what you did NOT check, in the same breath, so the boundary is on the page before your conclusion is."
        },
        {
          "h": "WHAT WE FOUND",
          "r": "Facts only, in the roofer's own words, with locations. Conditions, prior repairs, other trades' work on the roof, penetrations somebody else made, mechanical discharge, debris, blocked drains, damage with a direction to it. No adjectives, no theory."
        },
        {
          "h": "WHERE OUR WORK STARTS AND STOPS",
          "r": "The boundary, stated flatly: this area, this scope, these dates. If part of what they are pointing at IS ours, say so first and say what you will do about it — a letter that concedes the true part is the only kind that gets believed about the rest."
        },
        {
          "h": "WHAT WE ARE NOT DETERMINING",
          "r": "State it out loud, because a reply that leaves it out gets read as if it did determine it: this does not establish the cause of the water and it does not determine responsibility or coverage. Those need the manufacturer, the consultant, the engineer or the carrier, and this document does not substitute for any of them."
        },
        {
          "h": "WHAT WE SUGGEST HAPPENS NEXT",
          "r": "One constructive step with an owner — a joint walk, a test cut, opening it up, the manufacturer's rep. Never end on the denial; end on the thing that resolves it."
        }
      ],
      "secondary": ["a two-line email version for forwarding", "a joint-walk request with two proposed dates"]
    },
    {
      "id": "roof-turnover",
      "name": "Roof Turnover — It's Yours Now",
      "aka": [
        "turnover",
        "closeout",
        "handover",
        "final walk",
        "completion",
        "warranty start",
        "it's done"
      ],
      "family": "verification",
      "from": "the foreman who finished it",
      "to": "the GC, the owner's rep or the building engineer",
      "why": "The day this goes out is the day the roof stops being a construction site and starts being somebody's building. Everything not written down here becomes your problem the first time somebody walks on it.",
      "note": "This is our field turnover. The manufacturer's warranty and any owner's acceptance form are theirs and are not retyped here — this goes with them.",
      "omit": "WHO IS ALLOWED ON THE ROOF NOW AND HOW THEY CALL YOU. Every finished roof gets walked on within a fortnight by somebody with a drill, and the turnover that never named a procedure is the one that turns into a warranty argument.",
      "halt": "Only if this is the first document in the thread and there is no job or address at all.",
      "facts": ["completion date", "the job and which roof areas are being turned over", "what is complete and what is not", "who walked it and when", "who to call before anybody goes on the roof"],
      "sections": [
        {
          "h": "WHAT IS BEING TURNED OVER, AND WHAT IS NOT",
          "r": "Areas or slopes by the name the drawings use, with the completion date on each. Then, separately and just as plainly, what is NOT included — an area still open, a tie-in waiting on another trade, metal on backorder, a penetration somebody has not set. The boundary is the whole value of this document."
        },
        {
          "h": "WHAT WAS WALKED, BY WHOM",
          "r": "Date, who was there, what was walked, and anything that was expected to be walked and was not. If a manufacturer's inspector or a consultant walked it, say so and say what they said only if you have it in writing — never characterise a verbal."
        },
        {
          "h": "WHAT IS STILL OPEN",
          "r": "Punch items with an owner and a date each, plus anything you are waiting on somebody else for. If a punch item belongs to another trade, name the trade, not a person's shortcomings."
        },
        {
          "h": "NOBODY ON THIS ROOF WITHOUT A CALL",
          "r": "The procedure, in one short paragraph: who to call before anybody goes up, what needs protection under foot traffic, and the plain fact that other trades cutting, welding, dragging or setting equipment on a finished roof creates damage that is a repair and not a punch item. State the request; never state a warranty term or a consequence you are not the one who decides."
        },
        {
          "h": "WHAT THIS DOCUMENT IS NOT",
          "r": "It is not the warranty, it does not state a warranty period or its terms, and it does not certify performance. It records what was installed, what was walked, and what was left open."
        }
      ],
      "secondary": ["a short owner-facing version with the punch list stripped", "a maintenance-reminder note for the building engineer"]
    }
  ],

  /* Two shared documents that land differently on a roof. Overrides, not forks —
     each one restates only the field that changes and inherits everything else
     from the shared library (§THE THREE SHAPES). */
  "overrides": {
    "daily-report": {
      "omit": "WHAT IS OPEN TONIGHT AND WHAT IS UNDER IT. Every other trade's daily can leave the day at \"we got this far\". A roofing daily that does not say which sections are still open, what is temporarily holding the water, and what is in the space underneath is missing the only line anybody will look for at 2am when it starts raining."
    },
    "delay-notice": {
      "omit": "THE WEATHER FACTS, dated and specific to this roof, and what you did with the crew. \"Rained out\" is not a delay notice. What came in, when, what it did to an open section, what you had to re-do or re-dry, whether the crew was sent home or moved, and what is still exposed because of it — that is the notice."
    }
  },

  "vocab": [
    "eye ess oh -> ISO",
    "eye and double you -> I&W",
    "ice and water shield -> ice-and-water",
    "tee pee oh -> TPO",
    "ee pee dee em -> EPDM",
    "pee vee see membrane -> PVC membrane",
    "mod bit -> modified bitumen",
    "beer roof -> BUR",
    "built up roof -> built-up roof",
    "cover board -> coverboard",
    "term bar -> termination bar",
    "counter flashing -> counterflashing",
    "kick out -> kick-out flashing",
    "pipe boot -> pipe boot",
    "pitch pan -> pitch pocket",
    "scupper -> scupper",
    "sump -> sumped drain",
    "over flow -> overflow drain",
    "tapered eye so -> tapered ISO",
    "vapor retarder -> vapour retarder",
    "night seal -> night seal",
    "water cut off -> water cut-off",
    "dried in -> dried-in",
    "dry in -> dry-in",
    "squares -> squares",
    "sheathing -> sheathing",
    "purlin -> purlin",
    "nailer -> nailer",
    "sleeper -> sleeper",
    "dunnage -> dunnage",
    "walk pad -> walkway pad",
    "hip and ridge -> hip-and-ridge",
    "drip and rake -> drip and rake edge",
    "starter course -> starter course",
    "cap sheet -> cap sheet",
    "granular surface -> granulated surface",
    "self adhered -> self-adhered",
    "torch down -> torch-applied",
    "hot mop -> hot-applied",
    "roof loader -> roof loader",
    "ay hitch jay -> AHJ"
  ],

  "reminders": [
    "When a section is described as open, torn off, tarped, temporarily sealed or dried in -> remind them to say what is UNDERNEATH it — occupied space, a finished ceiling, a gear room, stock — and who inside the building was told, with the time. The roofing document that names the state and not the exposure is the one that gets read out loud after the water comes in.",
    "When a leak, a callback or water inside comes up -> remind them to record where it showed up INSIDE separately from where they found it up top, and to say plainly whether what they did is temporary. Never let the document state a cause; cause is the office, the consultant or the manufacturer.",
    "When wet insulation, bad deck, an extra layer or any tear-off discovery comes up -> remind them to count it and locate it BEFORE it gets covered, and to say the date. Once the new roof is over it the evidence is gone and nobody can price it.",
    "When another trade's work, equipment, welding, grease, foot traffic or a new penetration on a finished roof comes up -> remind them to date it, locate it, name the trade and not a person, and say who they told. This is the difference between a repair somebody owes and a punch item nobody pays for.",
    "When the crew opens more roof than it can close, or weather is forecast against an open section -> remind them to name who owns the call to stop and who inside the building gets rung when it turns. A roofing document with no phone number on it is not a plan.",
    "When squares, sheets, boards, rolls, pails or linear feet are mentioned -> remind them to state the unit they actually counted in and never to convert between units in the document. A conversion nobody checked is how an order and a claim both go wrong."
  ]
};
