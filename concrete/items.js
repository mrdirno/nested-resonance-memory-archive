/* CONCRETE FIELD TOOLKIT — VOCABULARY DATA.
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Classifications,
 * reason lists, gate ladders and pick options live HERE — never in the identity
 * config and never inline in a tool page.
 *
 * TWO HARD INVARIANTS (§SAFETY), and concrete carries the sharpest version of the
 * second one in the whole program:
 *
 *   ZERO BRAND NAMES. No manufacturer, no product line, no proprietary admixture,
 *   no pump brand, no ready-mix company. It is a BOOM PUMP and a LINE PUMP; it is
 *   a RETARDER and an ACCELERATOR; it is CURE COMPOUND, never a trade name.
 *
 *   NOTHING IS RATED, SIZED, SPACED, DOSED OR GRADED. No strength, no slump
 *   figure, no air content, no bar size, no lap, no cover, no cure time, no
 *   temperature limit, no admixture dosage, no joint spacing, no thickness — not
 *   as a value, not as a default, not as a greyed placeholder next to a chip.
 *   A PLACEHOLDER IS A RECOMMENDATION. Concrete is a STRUCTURAL trade and a slab
 *   that fails is a deposition: a number that looks authoritative on a phone is
 *   somebody's exhibit, and it is somebody else's stamp. The man states what HE
 *   has off HIS approved mix design and HIS structural drawings; the engineer of
 *   record, the mix submittal, the testing lab and the AHJ own what it should be.
 *
 *   THE PRUNE PANEL PROVED THE RULE RATHER THAN OBEYING IT. A 25-year concrete
 *   superintendent cut 64 of 215 proposed order lines (30%) and took a WHOLE
 *   CATEGORY with them — "admixtures and additions", seventeen lines, every one a
 *   dose field, on the grounds that "a dose field on a phone is a dose
 *   recommendation". Strength called for, air content, aggregate size,
 *   water-cement ratio, fibre dosage, delivery temperature and haul-time limit
 *   went the same way: design numbers nobody recites to dispatch, and a box for
 *   them invites a foreman to state the wrong one. What survived on the mix line
 *   is the one number that does the work — YOUR MIX DESIGN NUMBER — and the two
 *   things a super really does say, with no amount attached.
 *
 * BOTH HALVES, EVERYWHERE. Residential flatwork says FOOTING, SLAB ON GRADE,
 * DRIVEWAY, WET SCREED, BROOM FINISH, SHORT LOAD; commercial structural says
 * GRADE BEAM, ELEVATED DECK, POUR STRIP, SHORES AND RESHORES, BOOM PUMP. Both are
 * printed throughout on purpose — a page that speaks only one of them tells half
 * this trade family it was not written for them.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Everything here is something the man PICKS,
 * and every `notin` line is a fence that keeps a tag from being read as a claim.
 *
 * THE PANEL'S SHARPEST CUT IS IN `why`: "re-pour or repair CAUSED by others" was
 * reworded off the word caused, because a tag that asserts cause is a tag doing
 * the engineer's job and the boundaries forbid it. He writes what he was told and
 * what his crew did; who caused what is somebody else's call.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC superintendent",
    "Our own general super",
    "Another trade's foreman working in our footprint",
    "GC project manager",
    "Our PM or the office",
    "Builder's field super (tract or custom home)",
    "Grading contractor's superintendent",
    "Homeowner",
    "Owner's rep",
    "Jurisdiction inspector on site"
  ],
  "how": [
    {
      "v": "Face to face at the pour"
    },
    {
      "v": "Text message"
    },
    {
      "v": "Phone call"
    },
    {
      "v": "Told to me at the morning huddle"
    },
    {
      "v": "Radio on the site channel"
    },
    {
      "v": "Email"
    },
    {
      "v": "Marked-up set handed to me in the field"
    },
    {
      "v": "Stakes or paint moved on the grade"
    },
    {
      "v": "Note left on the forms"
    },
    {
      "v": "Written direction from our own office"
    }
  ],
  "why": [
    {
      "name": "Soft or wet grade",
      "sub": "Dirt wouldn't hold the crew, the iron or the forms. Told to go anyway, or told to stand while they worked it."
    },
    {
      "name": "Standing while another trade finished in our way",
      "sub": "Crew, pump and trucks on site, waiting on somebody else to get out of our footprint."
    },
    {
      "name": "Sleeves and embeds late or wrong",
      "sub": "Somebody else's sleeves, conduit, hold-downs or embeds showed up after we were formed and tied, or didn't match what we built to. Forms and steel opened back up."
    },
    {
      "name": "Steel moved after it was tied",
      "sub": "Told to add, move, pull or re-tie after the mat or the cage was done and walked."
    },
    {
      "name": "Layout moved after we built to it",
      "sub": "Lines, offsets or elevations changed after we set to the first ones."
    },
    {
      "name": "Bottom kept going down",
      "sub": "Dug past what the set showed. More mud and more forming than the footing on paper."
    },
    {
      "name": "Rock",
      "sub": "Couldn't dig it with what's on site. Footing, pier or grade beam bottom changed."
    },
    {
      "name": "Old concrete nobody told us about",
      "sub": "Footing, slab, wall or pad sitting in our line that wasn't on anything we bid."
    },
    {
      "name": "Line in the trench nobody marked",
      "sub": "Live or dead utility we found ourselves. Work stopped, hand dug, or went around it."
    },
    {
      "name": "Told to work the weather",
      "sub": "Keep going, pump the forms out, cover it, or come back on a day we'd called off."
    },
    {
      "name": "Babysitting protection somebody else called for",
      "sub": "Blankets, plastic, sand, heat, shade or barricade we put down, kept checking, and pulled on somebody's say-so."
    },
    {
      "name": "Couldn't get the truck or the boom to it",
      "sub": "Buggied, wheeled or hand-carried it, or one pour turned into two, because access changed after we set up."
    },
    {
      "name": "Tear-out or re-pour of work we already placed",
      "sub": "Work we placed got driven on, loaded, cut or wrecked before we ever handed it off."
    },
    {
      "name": "Cleanup or re-finish behind somebody else",
      "sub": "Washout, slurry, tracking or stacking left on our finish that we got told to deal with."
    }
  ],
  "notin": [
    {
      "name": "Not a price",
      "sub": "Hours, counts and conditions only. No rate, no total, no dollar figure anywhere on it."
    },
    {
      "name": "Not a change order and not a claim",
      "sub": "This says we were directed and what it took. It becomes a change when the offices paper it, and entitlement is their letter, not the foreman's."
    },
    {
      "name": "Not a question for the engineer, and not a design change",
      "sub": "Anything about the design goes up through the GC on their form. Nothing here approves moving steel, changing a mix, or leaving the set in hand."
    },
    {
      "name": "Not the plant's ticket or the lab's report",
      "sub": "We attach them by the numbers already printed on them. We never retype what's on them."
    },
    {
      "name": "Not the inspector's report",
      "sub": "He writes his own. We write what our crew was told and what our crew did."
    },
    {
      "name": "Not the GC's daily",
      "sub": "They keep theirs and number it. This is ours and it stands on its own."
    },
    {
      "name": "Not a finding of cause",
      "sub": "We write what we saw and what we placed. Who caused what is a call other people make."
    },
    {
      "name": "Not a safety or incident report",
      "sub": "Injuries, near misses and equipment go on their own paper, right then, through the proper channel."
    },
    {
      "name": "Not turnover or acceptance",
      "sub": "Signing that you were told isn't accepting the work, releasing anybody, or agreeing it's done."
    }
  ],
  "classes": [
    "— class",
    "JOURNEYMAN",
    "APPRENTICE",
    "FOREMAN",
    "FINISHER",
    "OPERATOR"
  ],
  "pics": [
    {
      "v": "In this message — shot before we covered it"
    },
    {
      "v": "None"
    }
  ]
};

/* ── THE CROSS-BOUNDARY ASK (shape #3 — shared/rowlog.js) ──────────────────
 * The vocabulary for rough-in-request.html — "Before the Pour".
 *
 * THIS IS THE PAGE THE WHOLE PROGRAM WAS POINTING AT. Five served trades already
 * ship a rough-in-request that ASKS this crew for a sleeve, a blockout, a
 * housekeeping pad, an embed or a pre-pour walk. Until this file existed, the
 * crew being asked had no page of its own — it could receive the ask and never
 * make one, on the one gate that does not reopen.
 *
 * THE GATES ARE A REAL COUNTDOWN, earliest first, and they are this trade's own
 * words: dig, base, under-slab, forms, sleeves, steel, the walk, the pour, green,
 * strip, backfill. `who` and `by` are the USUAL aim and the USUAL gate — they
 * only ever fill a field left empty and never overwrite a pick (§SCARS — a
 * default is a claim).
 *
 * WHAT THE PANEL KILLED, AND WHY IT MATTERS HERE: "ready-mix dispatch" was cut
 * as a receiver on this page, because everything a foreman says to dispatch is
 * yardage, mix and spacing — numbers, which belong on the order page where the
 * man states his own, not on a request page aimed at another trade. The testing
 * lab went the same way: he does not direct the crew and the crew does not
 * direct him.
 *
 * The bars hold exactly as they do on the other nine: no size, no strength, no
 * spacing, no cover, no cure time, no code reference and no money. Every spec is
 * a PHRASING he picks.
 */
window.TOOLKIT_ROUGHIN = {
  "toolName": "Before the Pour",
  "eyebrow": "Concrete · you → everybody who owes you something in this pour",
  "lede": "Everything another outfit has to have in, out, set or signed before the truck rolls — who owes it, where it is, and the gate it has to beat. One walk, one message each.",
  "docSubject": "Before the pour — what I need out of your trade",
  "docSubjectWith": "Before the pour — what I need from {to}",
  "closing": "That's my list for this pour. If a line on here is wrong, or you've got something going in that I didn't put on it, hit me back today and we'll walk it together — once the mud's down it's a core drill.",
  "warn": "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set. This page sizes nothing, specs nothing, doses nothing and grades nothing &mdash; no strength, no slump, no bar size, no cover, no cure time &mdash; and it doesn't know what the structural drawings, the approved mix design, the engineer of record or the AHJ require. Verify all of it against your own approved set. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  "offHint": "The structural sheet and its revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you the morning of the pour.",
  "phJob": "Riverside MOB",
  "phOff": "S-201 rev 3",
  "phFrom": "Mike R — Vega Concrete",
  "phArea": "Grid C-4 to C-7, ramp footings",
  "areaLabel": "Grid / footing mark / area",
  "who": [
    {
      "v": "gc",
      "label": "GC super"
    },
    {
      "v": "plumb",
      "label": "Plumber"
    },
    {
      "v": "excav",
      "label": "Dirt guy / grading"
    },
    {
      "v": "elec",
      "label": "Electrician"
    },
    {
      "v": "rebar",
      "label": "Rebar foreman"
    },
    {
      "v": "survey",
      "label": "Surveyor"
    },
    {
      "v": "steel",
      "label": "Steel erector"
    },
    {
      "v": "mech",
      "label": "HVAC / sheet metal"
    },
    {
      "v": "pump",
      "label": "Pump operator"
    },
    {
      "v": "irr",
      "label": "Irrigation / landscape"
    },
    {
      "v": "owner",
      "label": "Owner / homeowner"
    }
  ],
  "milestones": [
    {
      "v": "dig",
      "label": "Dig signed off"
    },
    {
      "v": "base",
      "label": "Base in and rolled"
    },
    {
      "v": "underslab",
      "label": "Under-slab trades out"
    },
    {
      "v": "forms",
      "label": "Forms up and braced"
    },
    {
      "v": "sleeves",
      "label": "Sleeves and embeds in"
    },
    {
      "v": "steel",
      "label": "Steel tied"
    },
    {
      "v": "prepour",
      "label": "Pre-pour walk"
    },
    {
      "v": "pour",
      "label": "Pour day"
    },
    {
      "v": "green",
      "label": "Green — cutting"
    },
    {
      "v": "strip",
      "label": "Strip forms"
    },
    {
      "v": "backfill",
      "label": "Backfill"
    }
  ],
  "asks": [
    {
      "v": "prepour",
      "label": "Pre-pour walk",
      "who": "gc",
      "by": "prepour",
      "specs": [
        "Set the walk the day before, not pour morning — anything we find pour morning is a cancelled truck and a lost day.",
        "I want everybody with something in this pour on that walk: their sleeves, their embeds, their ground, their pads.",
        "Bring the print you're working off. I'll bring mine and we'll compare them in the field, not over the phone.",
        "After the walk the deck is closed. Anything anybody adds after that, I hear it from you before I release trucks.",
        "If the walk or the inspection slips, call me before you call anybody else and I'll hold the trucks."
      ]
    },
    {
      "v": "access",
      "label": "Truck route, pump and washout",
      "who": "gc",
      "by": "prepour",
      "specs": [
        "Walk the truck route with me — where they come in, where they turn around, where they stack up so we're not blocking the whole job.",
        "Tell me where the pump sets and whether we're running boom or line, and keep that spot clear the day before, not pour morning.",
        "Look up with me — power lines, canopies, tree limbs. A boom can't swing under any of it.",
        "I need a washout spot you're okay with and I need to know who's hauling it off.",
        "Residential: cars out of the driveway, gate open wide, neighbors told the night before."
      ]
    },
    {
      "v": "clear",
      "label": "Clear the pour area",
      "who": "gc",
      "by": "prepour",
      "specs": [
        "Everything that isn't ours comes off the deck the night before — cords, ladders, gang boxes, staged pipe and conduit.",
        "After the walk nothing gets stored in the pour area. If it's sitting there pour morning my guys set it off in the dirt.",
        "Scaffold legs, jacks and shore posts standing in the pour — tell me now if they're staying and I'll box them out.",
        "Keep foot traffic off us while we're wet screeding and floating. One boot print in a broom finish is a callback.",
        "If your crew has to be in the pour area on pour day, come see me first and I'll tell you when there's a window."
      ]
    },
    {
      "v": "grade",
      "label": "Dig, base and grade",
      "who": "excav",
      "by": "dig",
      "specs": [
        "Footings and grade beams dug clean and to grade, spoil pulled back far enough that I can set forms and still get a truck by.",
        "Tell me when subgrade is compacted and signed off. I'm not forming on soft dirt.",
        "Base in, rolled and to grade before my flatwork crew shows. If it's coming up short I'd rather hear it now than pour morning.",
        "Soft spot, water or muck in the bottom — call me before you cover it, not after we're formed and tied.",
        "Keep the pad drained. If it rains I need somewhere for the water to go so we're not pumping footings out at daylight."
      ]
    },
    {
      "v": "underslab",
      "label": "Under-slab rough",
      "who": "plumb",
      "by": "underslab",
      "specs": [
        "Tell me the day your under-slab rough is done and tested so I can bring base in and get out of your way.",
        "Your ditch gets backfilled and compacted before base goes over it. I'm not chasing your trench after the mud is down.",
        "Whoever cuts the vapor barrier patches it and tapes it back before we cover it.",
        "Stub-ups capped and standing where they land on the print you're actually working off. If that print changed, show me before I set forms.",
        "Once base is in and rolled, nobody trenches back through it without walking it with me first."
      ]
    },
    {
      "v": "sleeves",
      "label": "Sleeves and blockouts",
      "who": "plumb",
      "by": "sleeves",
      "specs": [
        "Every sleeve and blockout you need through this pour is in, braced and marked before we cover it. After that it's a core drill.",
        "Walk it with me and paint or flag your locations so my crew doesn't move something they think is trash.",
        "Sleeves tied off and capped so they don't float on us or fill up with mud.",
        "Sleeve landing in the middle of the steel — show me today and take it to the GC. I'm not cutting bar on the deck.",
        "Driveway and flatwork sleeves — irrigation, gas, conduit — go in before I set forms, not after somebody remembers them."
      ]
    },
    {
      "v": "layout",
      "label": "Layout and control lines",
      "who": "survey",
      "by": "forms",
      "specs": [
        "I need control lines and a benchmark I can pull everything off of before I set forms.",
        "Mark your offsets where my forms won't cover them, and tell me what the marks mean.",
        "If the building moved on the pad, I need that before we form, not after we're tied.",
        "Come back and check my forms before we tie steel. I'd rather you find it than the inspector.",
        "Give me finish grade at the edges so my flatwork drains where it's supposed to drain."
      ]
    },
    {
      "v": "rebar",
      "label": "Steel, chairs and delivery",
      "who": "rebar",
      "by": "steel",
      "specs": [
        "Tell me the day steel lands so I've got forms up and somewhere to lay it down out of the mud.",
        "Chairs, dobies and tie wire come with the bar. I don't want to send a man to town on pour week.",
        "Short a bundle or a bend, call me the day you find out, not the day of the walk.",
        "How many hands you're bringing and what day they start, so I know if I'm holding the pour on you.",
        "Anything in the field that doesn't match what you were given comes to me and the GC. I'm not cutting bar on somebody's say-so."
      ]
    },
    {
      "v": "ground",
      "label": "The ground and the bonding",
      "who": "elec",
      "by": "steel",
      "specs": [
        "Ufer in the footing and tied to the steel before we cover it. Once mud's on it, it's gone.",
        "Show me where the tail comes out so my form crew and my strip crew leave it alone.",
        "Any bonding that lands on the steel goes on before we start tying the top mat.",
        "Flag it and protect it. If it gets bent into the pour I'm not chipping my footing back open for it.",
        "If it moves to a different footing than the one we walked, tell me before I close forms."
      ]
    },
    {
      "v": "weather",
      "label": "Rain, cold and late trucks",
      "who": "gc",
      "by": "pour",
      "specs": [
        "Forecast turns, I need your call the night before. I can cancel trucks or I can pour — I can't do both at seven in the morning.",
        "Plastic and blankets on site before pour day, not sent for after it starts coming down.",
        "If we get rained on mid-pour, let's agree now where we stop instead of deciding it standing in it.",
        "Cold night coming — tell me who's covering it and who's pulling blankets, so it doesn't end up uncovered by somebody hunting for tools.",
        "If trucks run late or I bring a load in behind to finish, I'll call you the minute I know so you can move whoever's waiting."
      ]
    },
    {
      "v": "protect",
      "label": "Off the green concrete",
      "who": "gc",
      "by": "strip",
      "specs": [
        "Keep everybody off it until I say it's ready. Green doesn't care whose truck it is.",
        "No cutting, coring, shooting or drilling into my pour without coming to me first.",
        "Tell me when you need it stripped and who's waiting on backfill so I can line my crew up.",
        "Backfill goes in when I release the walls, not when the dirt guy gets bored.",
        "Somebody chips it or drops a load on it, tell me the same day. I'd rather fix it than find it."
      ]
    },
    {
      "v": "embeds",
      "label": "Embeds, anchor bolts, templates",
      "who": "steel",
      "by": "prepour",
      "specs": [
        "Embeds, plates and anchor bolts on site and set before the pre-pour walk, not riding in on the truck that morning.",
        "Templates set and braced so bolts don't walk on us when we vibrate.",
        "Set your embeds off the same control lines I'm pulling from so we're not arguing about an inch of nothing.",
        "If your bolts come with a setting drawing, walk it with me at the forms. I'd rather find the conflict now than after we strip.",
        "Send a man to the pour to check your plates and bolts while it's still green. Once it sets, it's a saw."
      ]
    },
    {
      "v": "deck",
      "label": "Elevated deck",
      "who": "steel",
      "by": "steel",
      "specs": [
        "Deck screwed off, edges closed and your penetrations framed before we start tying the top mat.",
        "Tell me who's sweeping the deck and when. I want it clean the night before, not at daylight.",
        "Nobody moves shoring or reshores until I release it, and that includes sliding one post to get a lift through.",
        "Any hoisting over the deck on pour day gets coordinated with me. I've got a boom and a crew up there.",
        "Cable up, edge protection on and every hole covered before my guys walk it in the dark."
      ]
    },
    {
      "v": "pads",
      "label": "Housekeeping pads and bases",
      "who": "mech",
      "by": "forms",
      "specs": [
        "Want housekeeping pads under your units, give me locations and outlines before I set forms. A pad poured with the slab beats one glued on later.",
        "Tell me what's coming up out of the pad — conduit, drain, anchors — so nobody's drilling into it after.",
        "If your unit grew, tell me before the pour. I'd rather move a form than break out a pad.",
        "Anchors set in the pour with a template, or drilled after — pick one and tell me which, because they're different days for me.",
        "Anything that has to sit dead flat for a rail or a skid, say it at the walk and I'll set my screeds for it."
      ]
    }
  ]
};

/* ── THE RETURN LEG (shape #3 — shared/rowlog.js) ─────────────────────────
 * The vocabulary for answer-back.html. Every served trade is on BOTH ends of the
 * boundary, and on this trade the two ends are the same afternoon: the concrete
 * foreman chases six outfits for what goes IN the pour, and the same six send him
 * a list of what they need him to leave, box out, set or hold.
 *
 * The `paste` sample is a REAL-SHAPED list, deliberately messy in the way the
 * ones he gets are: a header, blank lines, and rows that are locations first.
 */
window.TOOLKIT_ANSWER = {
  "toolName": "What I'll Set",
  "eyebrow": "Concrete · them → you → back",
  "lede": "Somebody sent you a list — sleeves, blockouts, embeds, pads, a marked-up foundation plan typed out. Line it up, give each one a yes, a no, or a question, and a date on every yes, then send it back in one message.",
  "docSubject": "what I'll set",
  "closing": "That's the yes, the no, and the when. Anything I flagged I need a location or a detail on before we tie the top mat — once the mud's on it, every one of these is a core drill in finished work.",
  "phJob": "Riverside MOB",
  "phTo": "Danny — EC foreman",
  "phFrom": "Mike R — Vega Concrete",
  "phOff": "S-201 rev 3",
  "paste": "Riverside MOB — footings and slab items — Aug 14\n\nJob: Riverside MOB\nFrom: Danny — EC foreman\n\nGrid C-5 · Ufer in the footing, need it tied to the steel before you cover\nGrid C-4 to C-7 · 4 sleeves through the grade beam, marked in orange\nSlab east half · 2 housekeeping pads at the gear, not on the plan yet\nGrid D-2 · our conduit stub-ups are in, don't move them"
};

/* ── THE ORDER (shape #1 — shared/checklist-request.js) ───────────────────
 * The vocabulary for mix-order.html — the four o'clock call to the batch plant
 * and the pump company, which is the one call in this trade that is made from
 * memory every single time and half-forgets a line every single time.
 *
 * THE MOST IMPORTANT THING IN THIS BLOCK IS WHAT IS NOT IN IT. Every numeric
 * field ships EMPTY: no default, no greyed example, no "typical" anything. The
 * mix line prompts him to STATE his own figures and never supplies one, and the
 * whole "admixtures and additions" category the draft proposed was deleted
 * outright — seventeen dose fields, and a dose field on a phone is a dose
 * recommendation. The plant doses off the approved design.
 *
 * The `sub` under an item is a PROMPT, never a value: "off your approved
 * submittal", "your figure", "your number off your own takeoff". If a sub ever
 * grows a number in it, that is the bar breaking, not the copy improving.
 */
window.TOOLKIT_ITEMS.cats = [
  {
    "id": "need",
    "name": "What you're ordering",
    "docName": "THE ORDER",
    "hint": "Type it, or paste the whole thing — one line each, in your own words and your own units. Yardage, loads, hose, gear. Then scroll the list below and catch what you'd have found out at six in the morning.",
    "writein": true,
    "items": []
  },
  {
    "id": "placement",
    "name": "What you're pouring",
    "docName": "THE PLACEMENT",
    "hint": "Tick the placement first. The plant batches a footing different than a deck, and the pumper sets up different for a wall than for flatwork.",
    "items": [
      {
        "n": "Footings",
        "sub": "spread or continuous, and your count"
      },
      {
        "n": "Slab on grade",
        "sub": "one shot or split into strips"
      },
      {
        "n": "Foundation wall / stem wall",
        "sub": "and how many lifts you're taking it in"
      },
      {
        "n": "Driveway, approach, sidewalk",
        "sub": "and whether you're working in the street for any of it"
      },
      {
        "n": "Patio and flatwork",
        "sub": "give it to dispatch in yards, not square feet"
      },
      {
        "n": "Equipment pad / housekeeping pad",
        "sub": "say up front it's a short one"
      },
      {
        "n": "Stairs, landings, ramp",
        "sub": "slow placement — space the trucks out for it"
      },
      {
        "n": "Curb and gutter, valley pan",
        "sub": "and how much of it is hand work"
      },
      {
        "n": "Elevated deck",
        "sub": "metal deck, pan, or formed soffit — say which"
      },
      {
        "n": "Columns and pilasters",
        "sub": "and whether they're going through the pump"
      },
      {
        "n": "Grade beam",
        "sub": "on its own, or tying pier to pier"
      },
      {
        "n": "Retaining or shear wall",
        "sub": "formed one side or both"
      },
      {
        "n": "Piers, drilled shafts, caissons",
        "sub": "your count, and whether it's going down a tremie"
      },
      {
        "n": "Topping slab / overlay",
        "sub": "over deck or over an existing slab"
      },
      {
        "n": "Pour strip / closure strip",
        "sub": "the one you left out last time"
      },
      {
        "n": "Mud slab / seal slab",
        "sub": "lean placement going under something else"
      }
    ]
  },
  {
    "id": "mix",
    "name": "The mix — off your own paper",
    "docName": "THE MIX — MY FIGURES, OFF MY OWN SUBMITTAL",
    "hint": "One number does the work on this call: your mix design number. The plant pulls the rest off your approved submittal. This page carries no figures and never will — the number that matters is the one on your paper, said out loud in your own voice.",
    "items": [
      {
        "n": "Mix design number",
        "sub": "off your approved submittal — the number dispatch pulls it up by"
      },
      {
        "n": "Pump mix or chute mix",
        "sub": "tell them it's going through a pump so they batch it to move"
      },
      {
        "n": "Slump you're asking for",
        "sub": "your figure, and say whether that's at the truck or on the far end of the hose"
      },
      {
        "n": "Nothing goes in the truck on site unless I call for it",
        "sub": "the ask you make when you place the order"
      },
      {
        "n": "Retarder or accelerator for the day",
        "sub": "tell the plant what the weather's doing — they dose it off your design, not off the chute"
      },
      {
        "n": "Ice or hot water for the weather",
        "sub": "ask for it when you order, not the morning of"
      },
      {
        "n": "Fiber in it or not",
        "sub": "yes or no — the amount is the design's business"
      },
      {
        "n": "Lightweight or normal weight",
        "sub": "which one your design calls — it changes the pump"
      },
      {
        "n": "Integral color",
        "sub": "off the submittal, and the whole placement out of the same batch"
      }
    ]
  },
  {
    "id": "delivery",
    "name": "Delivery — yards, times, and the truck plan",
    "docName": "DELIVERY",
    "hint": "This is the half of the 4pm call dispatch actually writes down. Get it out in one breath and nobody calls you back.",
    "items": [
      {
        "n": "Total yards",
        "sub": "your number off your own takeoff"
      },
      {
        "n": "What time you want the first truck on site",
        "sub": "not the time you want to start placing"
      },
      {
        "n": "Spacing between trucks",
        "sub": "the interval you're asking for, off how fast your crew really places"
      },
      {
        "n": "Job name and address the way the plant has it",
        "sub": "so nobody batches to the wrong job across town"
      },
      {
        "n": "Which gate the trucks use",
        "sub": "cross street, gate code, and who's standing there to open it"
      },
      {
        "n": "Site contact and cell",
        "sub": "who dispatch calls when a driver's circling"
      },
      {
        "n": "Who's calling for the next truck",
        "sub": "one voice all day — name and cell on the order"
      },
      {
        "n": "How many trucks the site holds at once",
        "sub": "so they don't stack five in the street"
      },
      {
        "n": "Short load",
        "sub": "say it when you order, not when it shows up"
      },
      {
        "n": "Yards on the first load",
        "sub": "if you're taking a partial to get the crew started"
      },
      {
        "n": "Who makes the cut-off call",
        "sub": "and whether you want the last one held instead of cut"
      },
      {
        "n": "Hold the last truck",
        "sub": "keep one loaded — I'll call it in or cut it"
      },
      {
        "n": "Which plant it's coming out of",
        "sub": "and how far out they are"
      },
      {
        "n": "Weekend or off-hours pour",
        "sub": "say it when you place the order, not the morning of"
      },
      {
        "n": "Weather call",
        "sub": "who cancels, and by when you'll know"
      },
      {
        "n": "Who's taking tickets at the truck",
        "sub": "a name on the ground so drivers aren't hunting"
      }
    ]
  },
  {
    "id": "pump",
    "name": "The pump call",
    "docName": "THE PUMP",
    "hint": "Reach, setup, and time are yours to state. Nobody sizes this from an office — they size it off what you tell them you can see.",
    "items": [
      {
        "n": "Boom pump or line pump",
        "sub": "which one you're asking for"
      },
      {
        "n": "Where the pump sets",
        "sub": "and whether the outriggers have room to come all the way out"
      },
      {
        "n": "How far and how high you have to reach",
        "sub": "measured from where the pump can actually sit, not from the form"
      },
      {
        "n": "What time you want the pump on the ground",
        "sub": "set up and primed before the first truck shows"
      },
      {
        "n": "Ground under the pump",
        "sub": "hard, soft, over a vault, over a lid, over fresh backfill — say it"
      },
      {
        "n": "Overhead lines and swing room",
        "sub": "wires, limbs, canopy, scaffold, deck edge, the neighbor's roof"
      },
      {
        "n": "Hose on the ground",
        "sub": "how many sticks to reach the far corner"
      },
      {
        "n": "Reducer and end hose",
        "sub": "what you want on the end so your crew can handle it"
      },
      {
        "n": "Prime",
        "sub": "who's mixing it and who's catching it out the end"
      },
      {
        "n": "Hopper man and grate",
        "sub": "who's on the hopper picking rocks"
      },
      {
        "n": "Line route on a deck pour",
        "sub": "where the hose runs and what it lays on"
      },
      {
        "n": "If the pump goes down",
        "sub": "chute, buggies, or a second unit"
      },
      {
        "n": "Pump operator's cell",
        "sub": "in your phone before the day starts"
      }
    ]
  },
  {
    "id": "gear",
    "name": "Placing gear on the ground",
    "docName": "PLACING GEAR — ON THE GROUND",
    "hint": "Count what's actually on this job, not what's on a shelf at the yard.",
    "items": [
      {
        "n": "Vibrators",
        "sub": "your count, plus the spare that saves the pour"
      },
      {
        "n": "Bull floats, fresnos, and handles",
        "sub": "count the handles too — that's what goes missing"
      },
      {
        "n": "Hand floats, edgers, groovers, trowels",
        "sub": "enough for the finish crew you actually have"
      },
      {
        "n": "Power trowels",
        "sub": "walk-behind or ride-on — your count"
      },
      {
        "n": "Rakes, come-alongs, shovels",
        "sub": "and one more than you think"
      },
      {
        "n": "Wet screed and screed pins",
        "sub": "how you're setting grade before the crew starts"
      },
      {
        "n": "Roller or truss screed",
        "sub": "and who sets the rails"
      },
      {
        "n": "Laser and grade rod",
        "sub": "who's shooting and who's holding"
      },
      {
        "n": "Power buggies",
        "sub": "your count, and fuel for all of them"
      },
      {
        "n": "Wheelbarrows and ramp planks",
        "sub": "and the route they run"
      },
      {
        "n": "Chutes and extra chute sections",
        "sub": "how many extra to reach"
      },
      {
        "n": "Scaffold, planks, and ladders at the form",
        "sub": "so a man can reach the top of the wall with a vibrator"
      }
    ]
  },
  {
    "id": "site",
    "name": "What the plant and the pumper have to know about the site",
    "docName": "THE SITE — WHAT THE DRIVER AND THE PUMPER NEED",
    "hint": "Say all of it on the phone. Nobody wants to find it out with a loaded truck sitting out front.",
    "items": [
      {
        "n": "Access road in",
        "sub": "gravel, dirt, paved, one lane"
      },
      {
        "n": "Where trucks stage",
        "sub": "where they line up, where they wait, where they don't"
      },
      {
        "n": "Back-in only, no turnaround",
        "sub": "say it or you'll get a driver stuck sideways"
      },
      {
        "n": "Soft ground",
        "sub": "mats, plates, or rock before a loaded truck goes in"
      },
      {
        "n": "Slope the trucks sit on",
        "sub": "and which way the chute has to swing"
      },
      {
        "n": "Low clearance",
        "sub": "canopy, deck above, limbs, wires across the drive"
      },
      {
        "n": "Vaults, septic, lids, fresh backfill",
        "sub": "what won't hold a loaded truck or an outrigger"
      },
      {
        "n": "Washout",
        "sub": "where it is, who dug it, and who fills it back in"
      },
      {
        "n": "Water on site",
        "sub": "hose bib, water truck, or nothing at all"
      },
      {
        "n": "Working in the street",
        "sub": "flagger, cones, and whether the permit's in your hand"
      },
      {
        "n": "Neighbors and start-time limits",
        "sub": "noise on the street before daylight"
      },
      {
        "n": "Hot day",
        "sub": "shade, fogging, and how early you want the first truck to beat the heat"
      },
      {
        "n": "Cold morning",
        "sub": "blankets on site, ground thawed, ice and frost off the forms and steel"
      },
      {
        "n": "Night pour",
        "sub": "lights on the deck, on the pump, and on the finish"
      },
      {
        "n": "Wind",
        "sub": "what it does to the surface and what it does to a boom"
      }
    ]
  },
  {
    "id": "walk",
    "name": "The walk before the mud rolls",
    "docName": "THE WALK BEFORE THE POUR",
    "hint": "The walk you do the afternoon before, so the 4pm call is the only call you have to make.",
    "items": [
      {
        "n": "Forms set, braced, and oiled",
        "sub": "ties snugged where they blew out last time"
      },
      {
        "n": "Steel tied and clean",
        "sub": "no mud on the bars, no trash in the bottom of the form"
      },
      {
        "n": "Chairs and dobies",
        "sub": "under the steel everywhere it wants to lay down"
      },
      {
        "n": "Base compacted and wet down",
        "sub": "rock spread and shot to grade before anybody shows"
      },
      {
        "n": "Vapor barrier",
        "sub": "lapped, taped, and patched where it got walked through"
      },
      {
        "n": "Grade stakes, benchmark, and control marks",
        "sub": "one datum, everybody working off it"
      },
      {
        "n": "Bulkheads and stop-ends",
        "sub": "set where you'd stop if you lost a truck"
      },
      {
        "n": "Mesh",
        "sub": "and who's pulling it up as you place"
      },
      {
        "n": "Blockouts and boxouts",
        "sub": "every one boxed, braced, and marked so nobody buries it"
      },
      {
        "n": "Sleeves and penetrations",
        "sub": "everything the other trades come back through"
      },
      {
        "n": "Embeds, weld plates, anchor bolts",
        "sub": "set, shot, and braced hard enough they don't move under a vibrator"
      },
      {
        "n": "Dowels and dowel baskets",
        "sub": "at the cold joint and wherever the next pour ties in"
      },
      {
        "n": "Keyway",
        "sub": "in and clean"
      },
      {
        "n": "Waterstop",
        "sub": "continuous through the joint, nothing kinked"
      },
      {
        "n": "Deck blown out, edge form and pour stop set",
        "sub": "and the strip you're deliberately leaving out"
      },
      {
        "n": "Shores and reshores in",
        "sub": "and staying in through this placement"
      },
      {
        "n": "PT tendons walked",
        "sub": "chaired, pulled clear, nothing laying on them"
      }
    ]
  },
  {
    "id": "finish",
    "name": "The finish the crew has to be ready for",
    "docName": "THE FINISH",
    "hint": "Finish drives crew size, the tool list, and how long you're standing there after the last truck pulls out.",
    "items": [
      {
        "n": "Broom finish",
        "sub": "and which way you're pulling it"
      },
      {
        "n": "Hard trowel",
        "sub": "and how many machines and men that really takes"
      },
      {
        "n": "Float finish",
        "sub": "and where it stops"
      },
      {
        "n": "Chamfer and edge detail",
        "sub": "and who's running the edger"
      },
      {
        "n": "Scratch or rake finish",
        "sub": "if something's going on top of it later"
      },
      {
        "n": "Stamped or textured",
        "sub": "mats and release, and who's laying and pulling them"
      },
      {
        "n": "Colored",
        "sub": "integral, shake, or applied — say which so the crew brings the right tools"
      },
      {
        "n": "Exposed aggregate",
        "sub": "who's spraying the retarder and who's washing it off"
      },
      {
        "n": "Salt finish",
        "sub": "and who's got the salt"
      },
      {
        "n": "Dry shake hardener",
        "sub": "who's spreading it and who's floating it in"
      },
      {
        "n": "Rubbed wall or sack rub after strip",
        "sub": "count it as its own day"
      },
      {
        "n": "Form finish left as it comes off",
        "sub": "and whether tie holes get patched"
      },
      {
        "n": "Straightedge walk",
        "sub": "who walks it before the crew leaves the slab"
      }
    ]
  },
  {
    "id": "after",
    "name": "After the last truck — cure, joints, protection",
    "docName": "AFTER THE LAST TRUCK",
    "hint": "Half of what goes wrong on a slab goes wrong after everybody went home.",
    "items": [
      {
        "n": "How you're curing it",
        "sub": "wet cure, cure compound, cure and seal, or blankets"
      },
      {
        "n": "Saw cutting",
        "sub": "who's cutting, and you make the call on the ground when it's ready"
      },
      {
        "n": "Early-entry saw or wet saw",
        "sub": "which one you're running"
      },
      {
        "n": "Joint layout the way you've marked it",
        "sub": "off your drawings, walked and marked before the mud"
      },
      {
        "n": "Where you stop if a truck doesn't show",
        "sub": "the cold joint you'd rather pick than get handed"
      },
      {
        "n": "Isolation and expansion joint material",
        "sub": "in before the pour, not chased after"
      },
      {
        "n": "Burlap and plastic",
        "sub": "and who's coming back to keep it wet"
      },
      {
        "n": "Green slab protection",
        "sub": "barricades, tape, and nobody driving across it"
      },
      {
        "n": "Overnight watch",
        "sub": "who's coming back, and when"
      },
      {
        "n": "Who's stripping forms, and when",
        "sub": "so the crew shows up for it"
      },
      {
        "n": "Sealer or topping coming later",
        "sub": "so the finish you give today suits it"
      }
    ]
  },
  {
    "id": "crew",
    "name": "Who's on the ground",
    "docName": "WHO'S ON THE GROUND",
    "hint": "Names and cells. Most pours that go sideways go sideways because nobody knew who to call.",
    "items": [
      {
        "n": "Crew count for the placement",
        "sub": "placers separate from finishers"
      },
      {
        "n": "Finishers",
        "sub": "your count, and whether they're staying past the last truck"
      },
      {
        "n": "Who runs it if you step away",
        "sub": "say the name to the crew before the first truck"
      },
      {
        "n": "Man on the hopper and man on the washout",
        "sub": "named before the pump primes"
      },
      {
        "n": "Water truck or water man",
        "sub": "and where he fills"
      },
      {
        "n": "Cleanup and washdown laborer",
        "sub": "the one who keeps the drive clean so you're welcome back"
      },
      {
        "n": "Flagger or traffic control",
        "sub": "if any part of this is in the street"
      },
      {
        "n": "Backup hand on call",
        "sub": "if it runs long or somebody doesn't show"
      }
    ]
  },
  {
    "id": "forget",
    "name": "The forget-list",
    "docName": "THE FORGET-LIST",
    "hint": "None of it comes on the truck. Every one of them has stopped a pour cold.",
    "items": [
      {
        "n": "Fuel",
        "sub": "buggies, trowels, saw, generator — cans filled the night before"
      },
      {
        "n": "Spare vibrator and a spare head",
        "sub": "the first one always dies on the biggest pour"
      },
      {
        "n": "Form oil and a sprayer that works",
        "sub": "checked, not assumed"
      },
      {
        "n": "Extra chairs and dobies",
        "sub": "you always come up short in the last corner"
      },
      {
        "n": "Tie wire and a spare tie tool",
        "sub": "for the fix you find on the walk"
      },
      {
        "n": "Extra hose, clamps, gaskets, spare reducer",
        "sub": "the parts that blow at the worst possible time"
      },
      {
        "n": "Curing compound and a second sprayer",
        "sub": "on site before the pour, not sent for after"
      },
      {
        "n": "Blankets counted",
        "sub": "with your own eyes, not remembered from last winter"
      },
      {
        "n": "Poly and tape",
        "sub": "vapor barrier patches and rain cover, same roll"
      },
      {
        "n": "Saw blades",
        "sub": "a fresh one and a spare in the truck"
      },
      {
        "n": "Straightedge and kneeboards",
        "sub": "loaded the night before"
      },
      {
        "n": "Chalk line, marking paint, keel, tape",
        "sub": "the stuff that's always in somebody else's truck"
      },
      {
        "n": "Lights and cords",
        "sub": "if the finish runs past dark"
      },
      {
        "n": "A decent broom",
        "sub": "not the one with three bristles left"
      },
      {
        "n": "Bagged mix for a patch",
        "sub": "for the little piece nobody counted"
      },
      {
        "n": "Rags, bucket, and a brush for the embeds",
        "sub": "get the mud off the plates before it sets up"
      },
      {
        "n": "Washout tub and a trash barrel",
        "sub": "so nobody rinses out where you're about to finish"
      },
      {
        "n": "Gloves, boots, glasses",
        "sub": "the crew that quits early is the one that got burned"
      },
      {
        "n": "Drinking water and shade",
        "sub": "not just water for the slab"
      },
      {
        "n": "First aid and eyewash",
        "sub": "where somebody can find it fast"
      },
      {
        "n": "A shaded spot out of traffic for the cylinder box",
        "sub": "where a buggy won't clip it"
      }
    ]
  }
];

/* The write-in row's modifier axes. A pasted line already carries its own count
 * ("14 yd for the ramp footings"), so the axes answer the two questions that
 * actually come back: what unit that number is in, and WHO the line is for —
 * this one page produces an order that gets read out to two different companies
 * and a rental counter. §THE NEUTRAL: every axis leads with an em-dash option,
 * and a value nobody picked never reaches the plant.
 */
window.TOOLKIT_ITEMS.writeinAx = [
  {
    "k": "unit",
    "label": "Unit",
    "opts": [
      "— what unit —",
      "yards",
      "loads",
      "trucks",
      "each",
      "lineal feet",
      "square feet",
      "sticks of hose",
      "rolls",
      "bags"
    ]
  },
  {
    "k": "calledto",
    "label": "Called to",
    "opts": [
      "— who gets this line —",
      "Batch plant",
      "Pump company",
      "Rental yard",
      "Supply house",
      "My crew",
      "Saw crew",
      "The GC"
    ],
    "wide": true
  }
];
