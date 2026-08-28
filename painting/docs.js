/* PAINTING FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about paint and nothing else.
 *
 * SHIPPED WITH THE TRADE, NOT AFTER IT. Sitework stood up at #12 with no
 * write-up page and flooring did the same at #13, and closing that debt took
 * the DOCS axis two more cycles. Fourteenth trade, fourteenth library, zero
 * cycles owed — the axis stays closed the day the kit lands.
 *
 * A COATED WALL CANNOT BE READ AGAIN, AND THAT IS WHAT SHAPES EVERY DOCUMENT
 * HERE. Sitework's library is built on "a compacted trench is dug again";
 * painting owns the same irreversibility one trade later and on every surface
 * in the building. The moment the first coat goes on, the substrate — the wet
 * mud, the reading his meter took, the ding that was already there — is gone
 * as evidence. And the moment the FINAL coat goes on, the direction reverses:
 * now it is his finish that every ladder, cart and glove in the building lands
 * on, and without a dated record every mark in the building is a painting
 * back-charge in April. Both gates need paper from the only crew that was
 * standing there on the day, which is why the three documents of this trade's
 * own are one from before the coat, one from after the last one, and the
 * verbal everybody acts on in between.
 *
 * THE REFUSAL IS THE DESIGN, carried whole from trade.js into the one place a
 * document can breach it — the block an AI reads. This file ships:
 *   - NO spread rate, coverage figure or gallons-per-area arithmetic;
 *   - NO film build: no DFT/WFT target, no volume solids, no wet-to-dry math;
 *   - NO clock numbers: no dry, recoat, topcoat, cure, pot-life or induction
 *     time — the window is HIS data sheet's, in his words;
 *   - NO application limits: no temperature, RH, dew-point or moisture
 *     threshold — his instruments' readings beside the limit off HIS OWN
 *     product data, source named, <MISSING> if it is not in hand;
 *   - NO prep verdicts: SSPC/NACE and finish-level designations ride as
 *     LABELS off his contract; whether a surface met one is the spec's and
 *     the inspector's call;
 *   - NO lead or RRP determination, ever — what the recognized kit or the lab
 *     report SAID may be quoted verbatim; "no lead" and "doesn't apply" may
 *     not be said here;
 *   - NO color-match, sheen-equivalence or tint-formula statement — name,
 *     number, base and sheen exactly as the named person stated them;
 *   - NO release verdict: nothing here ever says surface ready, Level 5
 *     achieved, holiday-free, matched, passed or punch complete.
 * Every document records what HE saw, what HIS instruments read, what HIS OWN
 * spec, schedule, submittal, can and data sheet say, and what he did — and
 * never says which one wins. The engine's two LOCKED toggles ("never invent",
 * "never judge a value") back this at the universal-law level; the
 * `reminders` below carry the painting-specific edge the locks cannot see.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work"). DECLARED,
 *            never derived from the toolkit name.
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TRADE_DOCS = {
  /* "painting" alone emits "we do painting work" — the schedule's word, the
     crew's word and the truck door's word are for once the same one. */
  "trade": "painting",

  "docs": [
    {
      "id": "coated-under-protest",
      "name": "You Told Me To Coat It",
      "aka": [
        "painted under protest",
        "directed to proceed",
        "surface objection",
        "not ready but painted",
        "coated anyway",
        "told to paint it",
        "wet walls painted",
        "bad substrate record",
        "painted over it",
        "proceed direction"
      ],
      "family": "notice",
      "from": "the painter who flagged it",
      "to": "the GC super and our PM",
      "why": "The moment there is paint on it, the substrate cannot be read again — the mud, the moisture, the mill glaze and the meter reading are all under the coat. If the objection, the readings and the direction to proceed do not carry a date from BEFORE the coat, then in April the defect has one owner: the last trade that touched it.",
      "note": "This records what was observed, what was measured and who directed the work — it never says the surface failed, passed or was unfit. The readings are the ones HIS instruments took; the limits beside them are the ones off HIS OWN product data or spec, with the source named; and the direction is quoted, not characterised. Whether the surface was acceptable is exactly the question this document refuses to answer, and that refusal is what makes it hold up.",
      "omit": "THE READING BESIDE THE LIMIT, AND WHERE EACH ONE CAME FROM. Everybody writes \"the walls were still wet.\" Almost nobody writes \"my meter read <what it read> at three spots by the window, the data sheet in my hand says <what it says>, I showed the super at 9:40 and was told to keep rolling.\" The first is an opinion a lawyer eats; the second is two numbers, two sources and a name.",
      "needs": ["who", "where", "count"],
      "halt": "Only if there is no statement of who directed the work to proceed — without the direction, this is a condition report, and the no-paint note already exists for that.",
      "facts": [
        "the areas, pinned so somebody can find them after the building is finished",
        "what was observed, in the painter's words, while it could still be seen",
        "what his own instruments read, spot by spot, and what limit sits beside each reading and off which document",
        "who directed the work to proceed, how, and the words used",
        "what got coated anyway, with what, and when"
      ],
      "sections": [
        {
          "h": "Where, and what I could still see",
          "r": "The rooms, walls or elevations by the names on the plan and the names the crew uses, pinned by floor and grid or by something findable in a year. Then the condition in plain painter's words while it was still visible: soft mud, ridges under a rake light, a wall that flashed at the primer, mill glaze, rust bleeding through, chalking, dust the vacuum never met. Photos listed by what each frame shows, shot with something fixed in frame — a door number, a window, a grid line — because a photo of a bare wall locates nothing."
        },
        {
          "h": "What I measured, and what my own paperwork says",
          "r": "Each reading as the instrument gave it — the meter, the thermometer, the hygrometer — with where and what time it was taken. Beside each one, the limit as written on the product data sheet, the spec or the submittal IN HAND, quoted with its source named. If the limit is not in hand, write <MISSING> and say so — never fill it from memory and never let the document supply one. State no conclusion about what the numbers mean; put them side by side and stop."
        },
        {
          "h": "Who I told, and what came back",
          "r": "Who was shown or told, by name and company, when, and how — at the wall, by text, on the phone. The words that came back as close to verbatim as memory allows, quoted and never characterised: \"schedule's the schedule, get it coated\" is a quote; \"he blew me off\" is an argument. If anything was offered — a fan, a day, a different product — record the offer and what happened to it."
        },
        {
          "h": "What went on anyway",
          "r": "What was applied over the condition: product and base exactly as the can and the approved schedule state them, batch numbers off the fives if kept, which coats, which areas, what time. The crew that applied it. Anything deliberately left uncoated, and why it was possible to leave it."
        },
        {
          "h": "What I need, and what this is not",
          "r": "One named person and one ask — usually that the direction be confirmed in writing, or that the areas be recorded as coated at direction. State plainly what this document is not: not a refusal to work, not a warranty statement, not a claim, and not an opinion on whether the surface was fit. It is the record of what was visible, what was measured and what was said, on the one day that record could still be made."
        }
      ]
    },
    {
      "id": "walk-after-final",
      "name": "The Walk After Final",
      "aka": [
        "final coat baseline",
        "signed off at final",
        "condition at turnover",
        "before the trades come back",
        "finish baseline",
        "post-final walk",
        "final walk record",
        "we walked it at final",
        "baseline walk",
        "hallway handover"
      ],
      "family": "verification",
      "from": "the lead who walked it",
      "to": "the GC super, our PM, and whoever takes the floor after us",
      "why": "After final coat the traffic reverses: every trade left in the building works AGAINST finished paint, and eight weeks later the walls carry every cart, ladder and door swing since. Without a dated record of what the finish looked like when the painters left it, every mark in the building reads as a painting punch item — and the touch-up truck, the mobilisation and the argument all land on the painter.",
      "note": "This is a condition record, not an acceptance. It never says punch complete, never says the work conforms, and never asks anybody to sign anything — it fixes WHAT the finish looked like and WHEN, names who saw it, and leaves acceptance to the people who own it. A pasted block cannot be signed, and the reply with its timestamp is the paper trail.",
      "omit": "WHO WAS INVITED TO WALK IT, AND WHO DID NOT COME. Everybody writes what rooms got finished. Almost nobody writes \"offered the walk Thursday 14:00, walked Friday 07:30 with the super's foreman, the flooring lead was told twice and did not come\" — and that is the entire document the day somebody's cart mark shows up in a hallway that was clean at final.",
      "needs": ["when", "who"],
      "halt": "Never halt. If rooms are missing or nobody came, record what was walked, mark the rest <MISSING> and send it — a thin baseline dated today beats a complete one dated after the dings.",
      "facts": [
        "the areas walked, by floor and room, and the date and time of the walk",
        "the condition of the finish in the painter's own words, area by area",
        "the photo list, each frame with something fixed in it",
        "who was invited, who actually walked, and when",
        "what the painters still owe, named plainly"
      ],
      "sections": [
        {
          "h": "What was walked, and when",
          "r": "The floors and rooms by the names on the plan, the date, the time, and the light it was walked under — daylight, temporaries, a rake light — because finish reads differently under each and the argument later is always about light. Say what was NOT walked and why: locked, occupied, another trade still in it."
        },
        {
          "h": "The finish, room by room",
          "r": "Condition in plain words, room by room or run by run: clean, ready, a known touch-up owed at the door frame, a spot the crew is coming back to. Sheen and color carried exactly as the approved schedule names them — never \"matched\" or \"close\". State what is present, never a grade or a verdict: this document has no word for acceptable."
        },
        {
          "h": "The photos",
          "r": "The frame list: what each photo shows and where it was shot from, with something fixed in frame — a door number, a switch bank, a window mullion. Wide shots for coverage of a wall, close shots only where something is being recorded on purpose. A hallway is one photo per direction per end, not forty thumbnails nobody will ever open."
        },
        {
          "h": "Who was invited, who came",
          "r": "Every outfit and person offered the walk, by name and company, when and how they were told, and what came back. Then who actually walked, and anything they pointed at, recorded as what they said rather than as agreed-to. Anybody told and absent is named plainly, with the times — and never characterised."
        },
        {
          "h": "What we still owe, and what happens next",
          "r": "The painter's own open items by room, named without shame — the touch-up at the stair nose, the closet that needs a second look. Then the line that gives the document its teeth, stated as fact and not as threat: from this date the finish is in the building's traffic, and marks found after it are dated after it."
        }
      ]
    },
    {
      "id": "who-picked-the-color",
      "name": "Who Picked The Color",
      "aka": [
        "color record",
        "the color call",
        "verbal color change",
        "sheen change record",
        "color direction",
        "designer said",
        "picked in the hallway",
        "color confirmation",
        "tint direction",
        "color lock"
      ],
      "family": "notice",
      "from": "the painter who was handed the change",
      "to": "whoever gave the direction, copy the GC super and our PM",
      "why": "The most re-litigated verbal in this trade is a color or sheen changed by somebody standing in a hallway — acted on the same afternoon, invisible on every official schedule, and remembered three different ways by three different people the day the owner walks it. Gallons get tinted on that sentence. This writes the sentence down while everyone still agrees it was said.",
      "note": "This records a direction, never a judgment: name, number, base and sheen ride EXACTLY as the person stated them, the schedule line it replaces is quoted from the approved schedule, and the document never says the new color matches anything, reads the same as anything, or is equivalent to anything across brands. It also never carries a tint formula — the counter owns the formula, the schedule owns the intent.",
      "omit": "WHAT IT REPLACES, AND HOW MUCH OF THE OLD ONE IS ALREADY ON THE WALL. Everybody writes the new color down. Almost nobody writes \"this displaces P-3 on the level 2 corridors, two of which are already at final in the old color\" — and that sentence is the entire cost conversation, named on the day instead of discovered at the walk.",
      "needs": ["count", "change"],
      "halt": "Only if there is no statement of who gave the direction. A color note with no name on it is a wish, and the schedule outranks a wish.",
      "facts": [
        "who gave the direction, standing where, when, and the words used",
        "the new color, number, base and sheen exactly as stated",
        "the approved schedule line it replaces, quoted",
        "which areas it applies to, and how much of the old is already applied",
        "the ask: confirm before we tint"
      ],
      "sections": [
        {
          "h": "Who said it, and what they said",
          "r": "The name, the company and the role — the designer, the owner's rep, the super, the tenant — where they were standing, the date and time, and the direction as close to their words as memory allows. If it came by text or email, quote it and say so. If it came through somebody else, name the chain: \"the super, relaying the designer\" is a different document from \"the designer\"."
        },
        {
          "h": "The color, exactly as given",
          "r": "Manufacturer's color name and number, base and sheen, exactly as stated — and if any of those four was NOT stated, write <MISSING> rather than filling it in. Never translate to another brand, never write \"or equal\", and never say it matches the carpet, the tile or anything else. If a physical sample or a drawdown exists, say where it is and who has it."
        },
        {
          "h": "What it replaces, and where things stand",
          "r": "The schedule line being displaced, quoted from the approved finish schedule by its own designation. The areas the change applies to, by room and floor. Then the standing count in plain terms: what is already primed, first-coated or at final in the OLD color, and what material is already tinted, on site or on order — as counts and areas, never as dollars."
        },
        {
          "h": "Confirm before we tint",
          "r": "The fixed close: one named person, asked to reply CONFIRMED before material is tinted or the change goes on a wall — and the plain statement of what happens without it: the crew keeps working to the approved schedule. State the real clock (the store run, the crew's sequence) as fact, not pressure. If the direction-giver cannot confirm scope or cost, say who can, and copy them."
        }
      ]
    }
  ],

  "drop": [],

  "overrides": {
    "daily-report": {
      "name": "The Day Report",
      "from": "the lead on the job",
      "to": "our office and the GC super",
      "omit": "WHAT GOT COATED, OVER WHAT, AND OUT OF WHICH CANS. Every other trade's daily can leave the day at \"we got this far\". A painting daily that does not say which areas took which coat, what they were coated over, and the product and batch off the fives is missing the lines the callback turns on — because once the next coat goes on, nobody can establish the layer order again. And the custody line nobody writes: which rooms were RELEASED to us today, and which we handed back.",
      "needs": ["who", "before", "where", "count"],
    },
    "delay-notice": {
      "name": "We're Rolling Nothing",
      "to": "the GC super and our PM",
      "omit": "THE ROOMS BY NAME, AND WHO OR WHAT WAS IN THEM. \"We couldn't get in\" is a sentence nobody can act on. \"Rooms 214 through 220 — the tapers' scaffold in 214 and 215, no color answer on the corridors, and my meter reading over my own limit in 218, source named\" is a list a super can clear by lunch.",
      "needs": ["who", "where"],
      "sections": [
        {
          "h": "The hold and the clock",
          "r": "What was ready to be painted and where, the time the crew was on the ground, the time the hold started, and the time it turned loose or the crew rolled up. Who called it, or who we were waiting on."
        },
        {
          "h": "Why we couldn't go",
          "r": "Field terms, room by room: areas not released, another trade still in our rooms, no color or sheen answer on record, substrate reading over the limit OFF OUR OWN product data with both numbers and the source stated, no heat or air movement in the space as observed, exterior weather as observed. Never a verdict that a room failed anything — what stood between the crew and the wall, plainly."
        },
        {
          "h": "Who and what stood",
          "r": "The painters and sprayers who stood, counted separately because they are different work. The rig idled — the airless, the lifts — by piece. Material staged that could not go on. Counts of people and hours, never rates and never totals."
        },
        {
          "h": "What we were set up to do",
          "r": "The areas that were next, in sequence, and what the day would have produced — so the cost of the hold reads as lost production, stated as areas and coats rather than as money."
        }
      ]
    },
    "damage-found": {
      "name": "It Was Like That When We Got There",
      "omit": "THE DATED PHOTO WITH SOMETHING FIXED IN FRAME, TAKEN BEFORE THE TAPE WENT UP. The gouge in the drywall, the scratched glass, the dented frame — found during mask-off and mentioned to nobody — becomes the painter's back-charge the day the tape comes down. A photo of the mark with a door number in frame, dated before the first coat, is the whole defence, and the walk that finds ten of them takes fifteen minutes.",
      "needs": ["when", "where"],
    },
    "handover": {
      "name": "The Turnover",
      "omit": "WHERE THE ATTIC STOCK PHYSICALLY IS, CAN BY CAN. Every turnover letter lists the colors. Almost none says \"four labeled gallons on the shelf in janitor 112, lids marked by room\" — and two years later the repaint quote starts with an archaeology project. Colors ride exactly as the approved schedule names them: name, number, base, sheen, by area — never a formula, and never a cross-brand equivalent.",
      "needs": ["where", "count"],
    }
  },

  "vocab": [
    "effervescence -> efflorescence",
    "die eff tea -> DFT",
    "vee oh sea -> VOC",
    "pee vee ay -> PVA",
    "al kid -> alkyd",
    "in tumescent -> intumescent",
    "elast a merrick -> elastomeric",
    "dry fall -> dryfall",
    "back roll -> back-roll",
    "back prime -> back-prime",
    "high build -> high-build",
    "block filler -> block filler",
    "brush and roll -> brush-and-roll",
    "tannin bleed -> tannin bleed",
    "flash point -> flash point",
    "off the fives -> off the fives",
    "hot dog roller -> hot-dog roller",
    "five in one -> 5-in-1",
    "colour -> color"
  ],

  /* ── REMINDERS — trigger-only, never nagging ──────────────────────────────
   * The block is what talks to the AI, and an AI asked to write about paint is
   * exactly where a coverage rate, a recoat time or a "surface was ready" walks
   * in on its own. trade.js and items.js keep the numbers off the pages; these
   * keep them, and the verdicts, out of the documents.
   */
  "reminders": [
    "When gallons, coverage, spread rate, how far it goes or a takeoff comes up -> remind them that gallons are counts the painter already decided and the document records them as counts. Never let it supply or compute square feet per gallon, size an order off an area, or check his number — the data sheet owns the rate and the estimator owns the takeoff.",
    "When mils, film build, DFT, WFT, solids or a gauge comes up -> remind them to record the reading as the gauge gave it, beside the target THE PAINTER states off his own approved submittal or data sheet with the source named, <MISSING> if it is not in hand. Never let the document supply either number, convert wet to dry, or say a build was achieved.",
    "When dry time, recoat, topcoat, cure, pot life or 'is it ready to hit again' comes up -> remind them that the window is the one on HIS OWN data sheet, stated in his words with the source named. The document may record the clock — when the coat went on, when it was touched — and never supplies a time, and never says it was ready.",
    "When moisture, humidity, RH, dew point, temperature or a meter comes up -> remind them to record what HIS instruments read, where and when, beside the limit off HIS OWN product data or spec with the source named, <MISSING> if not in hand. Never let the document supply a threshold, and never let it say a reading passed, failed or was close enough.",
    "When prep, sanding, grinding, SSPC, a profile, Level 4, Level 5 or 'ready for paint' comes up -> remind them that designations ride as LABELS exactly as his contract names them, and the document records what the crew did and what he saw. Never let it define what a grade requires, and never let it say a surface met one — the spec and the inspector own both halves.",
    "When lead, RRP, pre-1978, a test kit, abatement or containment comes up -> remind them to quote what the recognized kit or the lab report SAID, verbatim, and who ran it. Never let the document say there is no lead, that the rule does not apply, or that a practice was safe or compliant — the certified renovator, the assessor and the lab own every one of those calls.",
    "When a color, a sheen, a match, a touch-up reading different, or tint comes up -> remind them to carry name, number, base and sheen EXACTLY as stated by a named person, and what approved schedule line it replaces. Never let the document say two colors match, two sheens read the same, or one brand equals another — and never a tint formula. A touch-up reading different from the field is recorded as what was observed, never explained.",
    "When fireproofing, intumescent, a rating or an hourly assembly comes up -> remind them that the schedule and the rating belong to the approved submittal and the listed system. The painter may state the target as he reads it off that submittal, by name — the document never confirms a rating, computes a thickness, or says a member is covered.",
    "When spraying, overspray, masking, ventilation, a respirator or cartridges comes up -> remind them to record what protection and containment were IN USE as facts observed, and what HIS OWN safety plan and SDS call for, in his words. Never let the document select equipment, state an exposure number, or say a setup was adequate."
  ]
};
