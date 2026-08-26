/* FLOORING FIELD TOOLKIT — THE TRADE'S VOCABULARY.
 *
 * `trade.js` = IDENTITY + COPY · `tools.js` = REGISTRY · this file = the WORDS.
 * Categories, option lists, ask lines, ladders. Nothing here is a runtime and
 * nothing here is a number we supply.
 *
 * WHERE THESE WORDS CAME FROM. Three independent in-trade lenses — a commercial
 * lead mechanic in a nine-man shop, a one-truck owner-operator who bids it,
 * lays it and invoices it at nine at night, and the RECEIVING lens (the GC super
 * and the dealer who get his paperwork) — each wrote this trade's vocabulary
 * with no sight of the others, and a 20-year prune was then told to kill about a
 * third. It killed more than half: 24 candidate tools collapsed into 7
 * documents, and the largest convergence in the pile by a mile was FIVE separate
 * names for one letter — "Can't Lay On That", "Floor's Not Ready", "Before I
 * Glue", "Going Over It" and "Give Me The Go". Five witnesses to one document is
 * the strongest signal this exercise can produce, and it is the pinned tool.
 *
 * THE REFUSAL IS THE DESIGN, and this trade's list is the longest on the rack
 * because every argument it has is about a number somebody else owns. Nothing in
 * this file is:
 *   · a moisture value — no RH percentage, no calcium-chloride lbs/1000sf, no
 *     pH, no wood-to-subfloor differential. Not as a default, not as a
 *     placeholder, not as an option in a picker;
 *   · a pass / fail / ready / acceptable / safe-to-install determination, in any
 *     wording, anywhere. His reading prints beside the limit he typed off his
 *     own pail, and the page never says which one wins;
 *   · a flatness or levelness tolerance — no fraction in ten feet, no FF/FL
 *     number, no gap under a straightedge as an allowance;
 *   · an acclimation period, temperature range or ambient-humidity range as a
 *     value, and no "conditioned and operational" call;
 *   · product data of any kind: coverage rate, spread rate, trowel notch, square
 *     feet per carton, open time, cure or traffic-ready hours, rolling-load
 *     limit, wear layer, DCOF, flame spread, IIC/STC, expansion gap, fastener
 *     schedule, underlayment rating;
 *   · estimating math: no waste factor, no roll-width yield, no pattern-repeat
 *     math, no seam layout, and no conversion of square feet into cartons, rolls
 *     or pails. The wrong conversion is either a short room or a delamination;
 *   · a determination on 9x9s, cutback, mastic or pre-1978 material. Never
 *     "contains asbestos", never "safe to go over", never an abatement or
 *     encapsulation method. The only line this kit ships is: suspect material,
 *     stopped, notify;
 *   · a manufacturing-versus-installation defect ruling, and no appearance
 *     acceptance criteria — gap, seam, bow-and-skew, shading, telegraphing —
 *     from CRI, NWFA, ASTM or any mill;
 *   · warranty language. It never restates one, never declares one void or
 *     intact, and never generates a mill claim form;
 *   · a number another party's software owns and issues: no RFI number, no CO or
 *     PCO number, no punch item number, no order or acknowledgment number.
 * He states what HIS OWN submittal, HIS OWN installation instructions and HIS
 * OWN meter say. The mill, the adhesive maker, the independent testing agency
 * and the architect own what it is supposed to be. Every one of those refusals
 * is a place where the honest tool structures what the USER states, and we ship
 * that instead. A later cycle that adds one is not filling a gap; it is the
 * defect this file was built to refuse.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── THE EXTRA WORK TAG (shape #2 — shared/note.js) ────────────────────────
 * PREP IS WHERE THE ENTIRE MARGIN LIVES AND IT IS THE WORK THAT NEVER GETS
 * WRITTEN DOWN. Grind, skim, fill the joints, pull cutback, fourteen jambs, two
 * more risers than the plan drew, a fridge nobody moved, a dumpster nobody
 * rented — the crew does it because the floor has to go down that week, and
 * sixty days later the PM says he never authorised it. At nine at night it goes
 * out as "extras, about eight hundred" and gets talked down to four, because
 * nothing is itemised and nothing is dated.
 *
 * Counts only — men, hours and material as quantities. No rates, no totals and
 * no signature line, because a copy-paste block cannot be signed and a floor
 * mechanic spots it instantly. And the tag carries no number: the GC's system
 * and the dealer's system own CO and PCO numbering, and a made-up number is how
 * a ticket gets thrown out.
 */
window.TOOLKIT_ITEMS.tag = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "The dealer who sold the job",
    "Our own owner or lead",
    "Builder's field super (tract or custom home)",
    "Homeowner",
    "Property manager or facilities",
    "Owner's rep or construction manager",
    "Another trade's foreman in my room",
    "Designer or the owner's finish rep",
    "Tenant or the store manager"
  ],

  how: [
    "Face to face in the room",
    "Text message",
    "Phone call",
    "Told to me at the morning huddle",
    "Email",
    "Marked-up finish plan handed to me",
    "A punch-walk list I was handed",
    "The super told me to keep going and he'd sort it",
    "Another trade told me it had been cleared"
  ],

  /* WHY IT IS OUTSIDE THE CONTRACT. Every line is a CONDITION he picks, not a
     characterisation of anybody, and not one of them puts a price, a cause or a
     verdict on the page. The first six are the ones all three panels wrote
     independently, which is why they are at the top. */
  why: [
    { name: "Prep nobody bid",
      sub: "Grinding, shot blasting, skimming, filling joints and cracks, or a self-leveler pour to get a floor that was handed to me as-is into something my material can go over." },
    { name: "Old goods and what was stuck to them",
      sub: "Tear-out, and then the adhesive under it. Scraping cutback is a day nobody costs, and on old resilient it stops being my call at all." },
    { name: "Told to go over readings I flagged",
      sub: "I wrote it up, I was directed to proceed anyway, and this tag is the date that happened. Nothing here says what the readings mean." },
    { name: "The room was not clear on the day",
      sub: "Trades still in it, material stacked on my floor, a lift parked in the middle, furniture nobody moved. Crew stood, or came back." },
    { name: "Doors, jambs and thresholds",
      sub: "Undercutting, pulling and rehanging, saddles and transitions at openings that were not in my scope and are in my way." },
    { name: "Moving somebody else's things",
      sub: "Furniture, appliances, fixtures, racking, files, a piano. It got moved because the floor could not go down around it." },
    { name: "More of it than the plan drew",
      sub: "Extra risers, an extra closet, a landing, a room that changed finish, a jog that is not on the sheet I bid off." },
    { name: "Different material than I bid",
      sub: "A substitution, a product change or a lot change directed after my number went in. Not a complaint — a date and a fact." },
    { name: "Repairing damage that was already there",
      sub: "Somebody else's damage to the substrate or to work already down, that had to be made right before I could carry on." },
    { name: "Working around them instead of through it",
      sub: "Phased, nights, weekends, half a corridor at a time, or in an occupied space — the same square feet costing twice the hours." },
    { name: "Trip charge — I came and could not work",
      sub: "Loaded, drove, walked it, could not start. The day is gone whether anybody wanted it to be or not." }
  ],

  /* WHAT IS NOT IN THIS TAG. The line nobody writes and everybody argues about
     in April. Naming it the day it happened is what stops it becoming a
     back-charge. */
  notin: [
    { name: "Anywhere but the area named above" },
    { name: "The material itself", sub: "unless a line above says it" },
    { name: "Any moisture mitigation", sub: "that is its own scope and its own product" },
    { name: "Protection after we leave", sub: "and who covers it, and with what" },
    { name: "Final clean, seal or wax" },
    { name: "Base, trim and transitions in this area" },
    { name: "Coming back to fix what somebody walks on tomorrow" },
    { name: "Anything a different room needs" }
  ],

  pics: [
    { v: "Yes — before it was covered" },
    { v: "Yes — and after" },
    { v: "No" }
  ],

  classes: [
    "Mechanic / installer",
    "Helper",
    "Lead / foreman",
    "Prep hand — grinder or leveler",
    "Tear-out"
  ]
};

/* ── BEFORE IT GOES DOWN (shape #3 — the return-leg request page) ───────────
 * THE ARGUMENT FOR THIS WHOLE TRADE, MADE AS A TOOL. Three shipped kits already
 * count down to this man's gate in their own words — av/items.js "Before floor
 * goes down", gc/items.js "Before floors go down" (the LAST rung its gate ladder
 * has) and again "Walk it with me before tile goes in", low-voltage/items.js
 * "Before tile goes in" — and NOT ONE of the twelve has a flooring receiver in
 * any roster. Three trades name the moment; nobody can address the man, and
 * nobody has ever published what has to be true first.
 *
 * SENDING IT PUBLISHES HIS MOBILISATION DATE, which is exactly the date those
 * three kits have been counting to. And when the room is not clear on the day,
 * the same ticked list is the exhibit.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before It Goes Down",
  eyebrow: "Flooring · you → everybody who owes you something in this room",
  lede: "Everything that has to be out, off, on, patched, undercut or decided before you can start — and before you glue. Who owes it, which room, and the gate it has to beat. Walk it once, tap the rows, send one message per outfit.",
  docSubject: "Before it goes down — what I need out of your outfit",
  docSubjectWith: "Before it goes down — what I need from {to}",
  closing: "That's my list before we start. If a line on here is wrong, or there's something in that room you know about that I don't, hit me back today — every one of these is cheap this week and gone the morning my crew is standing in the corridor with the material already on the job.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set and <i>your</i> own installation instructions. This page sets no moisture limit, no flatness tolerance, no acclimation window, no temperature and no product data, and it doesn't know what your mill, your adhesive maker, the architect or the spec require &mdash; verify all of it against your own submittal and the instructions in the box. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The finish schedule and its revision is the whole argument — naming the sheet you took this off is the difference between a request the super works to and one you re-walk with him the morning you were supposed to be laying.",
  phJob: "Northgate Medical — 2nd floor",
  phOff: "A-601 finish schedule rev 4",
  phFrom: "Marco V — Vela Floor Covering",
  phArea: "Corridor 2A — rooms 210 to 224",
  areaLabel: "Room / area",

  who: [
    { v: "gc", label: "GC super" },
    { v: "builder", label: "Builder / homeowner" },
    { v: "conc", label: "Concrete / slab" },
    { v: "framer", label: "Framer / drywall" },
    { v: "painter", label: "Painter" },
    { v: "mech", label: "Mech / HVAC" },
    { v: "ec", label: "EC foreman" },
    { v: "plumb", label: "Plumber" },
    { v: "doors", label: "Doors / millwork" },
    { v: "tile", label: "Tile setter" },
    { v: "dealer", label: "Dealer / distributor" },
    { v: "owner", label: "Owner / property manager" },
    { v: "clean", label: "Final clean" }
  ],

  /* HIS ladder, not the GC's. It ends where nothing reopens. */
  milestones: [
    { v: "measure", label: "Before we measure" },
    { v: "order", label: "Before material ships" },
    { v: "deliver", label: "Before material lands" },
    { v: "mobe", label: "Before we mobilise" },
    { v: "prep", label: "Before we prep" },
    { v: "glue", label: "Before glue goes down" },
    { v: "base", label: "Before base and trim" },
    { v: "handover", label: "Before we hand it over" }
  ],

  asks: [
    { v: "slab", label: "The floor I'm actually going over", who: "gc", by: "prep", specs: [
      "Broom clean and empty, with the joints, cracks and core holes filled by whoever owns that — I am not patching a slab on the day and calling it mobilisation.",
      "Tell me what came off it and what is still stuck to it. Old adhesive is a different day than a bare slab, and I would rather find that this week.",
      "If it is old resilient or black mastic, stop and tell me — that is the owner's survey and somebody else's licence, and nobody on my crew touches it until you say.",
      "Walk it with me with a straightedge before you hand it over. What is under it is invisible the day after I cover it, and after that it is mine."
    ] },
    { v: "readings", label: "Who is testing it, and when", who: "gc", by: "prep", specs: [
      "Tell me who is doing the moisture testing and when, because the results decide whether my material can go down at all.",
      "If the spec calls for an independent agency, that is not me — tell me who you hired and get me the report, not a number over the phone.",
      "Whatever it reads, I need it in writing before my crew is on the job, not while they are standing on it.",
      "If it comes back outside what my own instructions allow, tell me today who is handling mitigation and whose scope it is. It is not in mine unless it says so."
    ] },
    { v: "heat", label: "Heat, air and the building running", who: "mech", by: "deliver", specs: [
      "Tell me the day the permanent system is on and holding, because my material has to sit in the space it is going into and so does the adhesive.",
      "Temp heat that goes off at night is not the building running — if that is what we have, say so, and I will write down what we are doing instead.",
      "Whatever your instructions and mine say about conditions, we are both working to a number somebody else set. Send me yours and I will send you mine.",
      "Tell me who is watching it over the weekend, because a system that trips on Saturday costs me Monday."
    ] },
    { v: "clear", label: "The room clear, and the day it's clear", who: "gc", by: "mobe", specs: [
      "Nobody overhead and nobody in it. I cannot lay a floor under a man on a ladder, and I will not have his drops on my finished work.",
      "Material, gang boxes, carts and the lift out of the room — not pushed to one end, out. Half a room laid twice is a whole room paid once.",
      "Give me the actual day and I will hold my crew for it. Give me a maybe and I will book them somewhere else, and that is worse for both of us.",
      "If it slides, tell me the day before, not the morning of. My crew is booked and the material is already sitting in your building."
    ] },
    { v: "wet", label: "Wet trades done overhead", who: "gc", by: "glue", specs: [
      "Paint, texture, drywall and anything else that drips is finished and dry before I start — my floor is the last surface in that room and it collects everything.",
      "Tell me who is touching up after me, because somebody will, and I would rather know his name now.",
      "If they have to come back over my floor, tell me what is protecting it and who is putting it down.",
      "The base line matters: tell me whether they are cutting to the floor or to the base, because that changes what I do at the wall."
    ] },
    { v: "doors", label: "Doors, jambs and thresholds", who: "doors", by: "glue", specs: [
      "Tell me who is undercutting the jambs, and when. It is a real day of work and it is nobody's scope until somebody says it.",
      "Doors off the hinges or on? If they are on, they get planed or they drag, and neither one is free.",
      "Saddles, thresholds and transitions at every opening — tell me who supplies them and who sets them.",
      "If anything is getting rehung after me, tell me who, because that is a man with a drill standing on new work."
    ] },
    { v: "power", label: "Power, light and water in the room", who: "ec", by: "prep", specs: [
      "Tell me what I have got. A grinder and a vac is not something you run off an extension cord out of the corridor.",
      "Light to see a seam by. Work lights in the ceiling grid do not reach a floor at eight in the morning with the blinds shut.",
      "If there is dust, tell me who has to be warned and what the building wants covered — that is your call to make and it goes on your paper.",
      "Somewhere to fill a bucket and somewhere to wash out that you are okay with."
    ] },
    { v: "material", label: "Material on site, and where it sits", who: "dealer", by: "deliver", specs: [
      "On the floor it is going on, in the conditions it is going into, and long enough before we start that it is not still cold when we open it.",
      "One run for the whole area — if part of it is a different lot, tell me before it ships, not when I open the second pallet in the middle of a corridor.",
      "Tell me where it lands and whether it can get there. A pallet on a dock is not a pallet in the room, and I am not the freight elevator.",
      "Attic stock is in the spec and it is never on the truck. Put it on this order or tell me it is not coming."
    ] },
    { v: "schedule", label: "What goes where — the finish schedule", who: "gc", by: "measure", specs: [
      "Confirm the schedule and the revision. A superseded finish sheet is a corridor in the wrong product and it is nobody's mistake to fix cheaply.",
      "If the schedule and the plan hatch disagree, that comes to me before I order, not after it is cut.",
      "Tell me who decides direction, start point and where a seam is allowed to land, because that is a decision somebody makes once and everybody lives with.",
      "Anything picked but not released — tell me now. A colour on hold is a lead time nobody is counting."
    ] },
    { v: "moving", label: "Furniture, appliances and what's in the way", who: "owner", by: "mobe", specs: [
      "Tell me who moves it and where it goes, because the floor does not go down around a fridge and neither does the base.",
      "Anything disconnected — appliances, a toilet, a rack — needs somebody licensed to pull it and put it back. That is not us.",
      "Tell me what is fragile and what is the owner's, and get a photo of it before anybody touches it.",
      "If it is coming back the same day, say so, because that changes how much of the room I open at once."
    ] },
    { v: "protect", label: "Protection after, and who owns it", who: "gc", by: "handover", specs: [
      "Tell me who is covering it and with what, and whether that is in my number or yours. Whoever it is, it is a real cost and it belongs to somebody.",
      "How long until other trades are back on it, and are they on it with carts, ladders and scissor lifts?",
      "Tell me who signs it off and when, because after that walk everything on it is a callback instead of a punch item.",
      "Final clean: tell me who does it and what they are using, because the wrong thing on a new floor is a warranty conversation nobody wants."
    ] }
  ]
};

/* ── PUNCH BACK (shape #3 — the RETURN LEG) ────────────────────────────────
 * FLOORING IS LAST IN, SO EVERY LIST ON THE JOB ENDS UP ON HIM. A forty-line
 * walk list pastes in at four on a Friday; he says "we'll take care of it" and
 * has just accepted all forty, or somebody retypes the whole thing into an
 * email at nine at night, misses four lines, and retention sits on one
 * unanswered item.
 *
 * THE TWO ANSWERS HE NEVER GETS TO GIVE AND ALWAYS NEEDS: "that one is the tile
 * guy's", and "that is damage, not a punch item — I need a ticket." Their line
 * text and their numbers ride through verbatim, because their system owns the
 * list and closes it, and retyping their items is the double entry that would
 * kill this page.
 */
window.TOOLKIT_ANSWER = {
  toolName: "Punch Back",
  eyebrow: "Flooring · them → you → back",
  lede: "The super, the builder or the property manager walked it and sent you a list. Paste it, answer every line in their order — Will do, with a day on it, In already, Not mine, or Damage — needs a ticket — and send back one answer they can close items off.",
  docSubject: "punch list, answered",
  answers: ["Will do", "In already", "Not mine", "Damage — needs a ticket"],
  closing: "That's every line on your list answered in your order and with your numbers. Anything marked Will do carries a day — where that day is a material lead time, the pencil says so. Anything marked Damage — needs a ticket happened after my work went in, and it moves when your ticket does — it isn't a punch item.",
  phJob: "Northgate Medical — 2nd floor",
  phTo: "Dave R — GC super",
  phFrom: "Marco V — Vela Floor Covering",
  phOff: "punch walk 8/14",
  paste: "Northgate Medical 2nd floor — flooring punch — Aug 14\n\nJob: Northgate Medical\nFrom: Dave R — GC super\n\n12. Corridor 2A — seam lifting outside 214\n13. Rm 216 — base not caulked at the door\n14. Rm 218 — plank scuffed by south window\n15. Rm 220 — transition strip missing at the tile\n16. Rm 224 — dark mark on carpet under the window\n17. Corridor 2A — reducer loose at the elevator lobby"
};

/* ── GETTING IN (shape #2 — the INTERFACE rung) ────────────────────────────
 * The same page as the other twelve kits and the only tool in the program aimed
 * at a party that is not another trade. THE HEADS-UP TICKS ARE NOT DISCLOSURES,
 * THEY ARE HANDBACKS: every one of them ends in a question aimed back at the man
 * who owns the process. A later cycle that rewrites one of them into a status
 * ("dust control arranged", "elevator booked") is writing the defect this page
 * was designed around, not tidying it up.
 *
 * This trade's version is not a reskin. What comes in the door is different —
 * twelve-foot rolls that do not go round a corner, pails, and a grinder that
 * makes the whole floor a dust problem — and the one ask nobody else on the rack
 * has to make is for the building to be at temperature days before he arrives.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Flooring · you → whoever holds the keys",
  lede: "You need twelve-foot rolls, pallets of plank and a grinder into a space somebody else locks — and the building has to be running before any of it is worth doing. Send the ask that gets a yes before the truck is loaded: the route in, the lift, the day, who's coming, and the heads-up that keeps a crew of four sitting in a van outside a locked lobby at six in the morning.",
  docName: "ACCESS REQUEST",

  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "A week or two" },
    { v: "Ongoing — I'll flag changes" }
  ],

  need: [
    { name: "Gate or lobby unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The route in", sub: "a twelve-foot roll does not go round a corner or up a switchback stair — tell me the way that works" },
    { name: "The freight lift, and its inside dimensions", sub: "and whether it is padded, and who holds the key" },
    { name: "Somewhere to lay material down", sub: "in the space it is going into, for as long as it has to sit there" },
    { name: "The building at temperature before we get there", sub: "tell me the day it is on and holding — material that has not been in the space is not ready to go down" },
    { name: "Power we can actually run a grinder off" },
    { name: "Somewhere to fill a bucket and wash out", sub: "a spot you're okay with, and who hauls it off" },
    { name: "A dumpster, or where the old floor goes", sub: "tear-out fills one faster than anybody expects" },
    { name: "Parking for a van and a box truck", sub: "close enough to carry rolls from" },
    { name: "Nobody there — we'll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "crews moving in before anyone's normally there" },
    { name: "Tell me who gets our COI", sub: "if it isn't already on file" }
  ],

  heads: [
    { name: "Grinding makes dust through the whole floor", sub: "we run it on a vac — tell me what's downwind, what your intakes are, who has to be told, and what you want sealed off" },
    { name: "Adhesive and seam sealer have a smell", sub: "it carries further than the room — tell me who to warn, and whether anything has to be shut down or run harder while we're on it" },
    { name: "The floor is out of service while it goes down and after", sub: "tell me how long you need it back in and who decides that, because we don't" },
    { name: "There'll be pallets and rolls sitting in the space for days", sub: "that's the material conditioning — tell me where it can sit without being moved twice" },
    { name: "Tear-out is loud and it starts early", sub: "say the word and we'll move the window" },
    { name: "We may find old material under the floor", sub: "if it looks like the old stuff we stop and nobody touches it — tell me who you'd call and whose survey it is. It isn't ours" },
    { name: "We need something powered down, moved or disconnected", sub: "an appliance, a fixture, a rack — tell me who owns that and what notice they need. It isn't us" },
    { name: "Trades walking on a new floor is the whole problem", sub: "tell me who's coming back in behind us, when, and who owns protecting it" },
    { name: "We'll be in and out of the lobby with material", sub: "tell me the door you want us using and the hours, before a truck is on the street outside" },
    { name: "Somebody has to hold the lift for the rolls", sub: "tell me who, and whether that's a call you make or one we make to somebody else" }
  ],

  phSite: "Bishop Ranch 3",
  phRoom: "2nd floor — corridor 2A and rooms 210-224",
  phHow: "loading dock off the north side, freight lift to 2",
  phScope: "tear out the old carpet and lay LVT — four of us, a grinder and about forty pallets' worth over three days",
  phLoud: "tear-out from 7am, grinding the middle of the day",
  phTo: "Ray — property manager",
  phMe: "Marco V — 209-555-0148",
  phCo: "Vela Floor Covering",

  closing: [
    "This is an ask, not a booking — nothing rolls until you reply. Wrong day? Tell me which one works and we'll take it.",
    "Saying yes: tell me the window you're actually giving us, where the material can sit, and who's meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It's an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it, because the building owns and numbers all of that and we never will."
};

/* ── TAG_ES — the directed-work tag's vocabulary en español (2026-08-23). ─────
 *
 * Every entry carries its own en-twin — nothing paired by index, nothing that can
 * drift apart. The page composes what the document prints ("ES (EN)") from the
 * pair; a <select> value carries its twin itself, house style "MAYORDOMO (FOREMAN)".
 * Gated: tools/toolkit-gates/lang-layer.mjs asserts every twin matches an EN
 * option verbatim, on every page that mounts shared/lang.js. */
window.TOOLKIT_ITEMS.tag_es = {
  "classes": [
    { "es": "Instalador (Mechanic / installer)", "en": "Mechanic / installer" },
    { "es": "Ayudante (Helper)", "en": "Helper" },
    { "es": "Mayordomo (Lead / foreman)", "en": "Lead / foreman" },
    { "es": "Prep — pulidora o leveler (Prep hand — grinder or leveler)", "en": "Prep hand — grinder or leveler" },
    { "es": "Demolición (Tear-out)", "en": "Tear-out" }
  ],
  "how": [
    { "es": "En persona, en el cuarto", "en": "Face to face in the room" },
    { "es": "Mensaje de texto", "en": "Text message" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me lo dijeron en la junta de la mañana", "en": "Told to me at the morning huddle" },
    { "es": "Correo", "en": "Email" },
    { "es": "Plano de acabados marcado que me entregaron", "en": "Marked-up finish plan handed to me" },
    { "es": "Una lista de punch que me entregaron", "en": "A punch-walk list I was handed" },
    { "es": "El súper me dijo que siguiera y que él lo arreglaba", "en": "The super told me to keep going and he'd sort it" },
    { "es": "Otro contratista me dijo que ya estaba autorizado", "en": "Another trade told me it had been cleared" }
  ],
  "notin": [
    { "es": "Cualquier área que no sea la nombrada arriba", "en": "Anywhere but the area named above" },
    { "es": "El material en sí", "sub": "a menos que una línea de arriba lo diga", "en": "The material itself" },
    { "es": "Cualquier mitigación de humedad", "sub": "eso es un alcance aparte y un producto aparte", "en": "Any moisture mitigation" },
    { "es": "La protección después de que nos vamos", "sub": "y quién lo tapa, y con qué", "en": "Protection after we leave" },
    { "es": "Limpieza final, sellador o cera", "en": "Final clean, seal or wax" },
    { "es": "Base, molduras y transiciones en esta área", "en": "Base, trim and transitions in this area" },
    { "es": "Regresar a arreglar lo que alguien pise mañana", "en": "Coming back to fix what somebody walks on tomorrow" },
    { "es": "Cualquier cosa que necesite otro cuarto", "en": "Anything a different room needs" }
  ],
  "pics": [
    { "es": "Sí — antes de que se tapara", "en": "Yes — before it was covered" },
    { "es": "Sí — y después", "en": "Yes — and after" },
    { "es": "No", "en": "No" }
  ],
  "roles": [
    { "es": "Súper del GC", "en": "GC superintendent" },
    { "es": "PM del GC", "en": "GC project manager" },
    { "es": "El dealer que vendió el trabajo", "en": "The dealer who sold the job" },
    { "es": "Nuestro patrón o nuestro mayordomo", "en": "Our own owner or lead" },
    { "es": "Súper de campo del builder (fraccionamiento o casa custom)", "en": "Builder's field super (tract or custom home)" },
    { "es": "El dueño de la casa", "en": "Homeowner" },
    { "es": "Property manager o los de mantenimiento", "en": "Property manager or facilities" },
    { "es": "Representante del dueño o construction manager", "en": "Owner's rep or construction manager" },
    { "es": "El mayordomo de otro contratista en mi cuarto", "en": "Another trade's foreman in my room" },
    { "es": "Diseñador o el representante de acabados del dueño", "en": "Designer or the owner's finish rep" },
    { "es": "El inquilino o el gerente de la tienda", "en": "Tenant or the store manager" }
  ],
  "why": [
    { "es": "Prep que nadie cotizó", "sub": "Pulir, shot blast, skim, llenar juntas y grietas, o un colado de self-leveler para dejar un piso que me entregaron tal como estaba listo para recibir mi material.", "en": "Prep nobody bid" },
    { "es": "El piso viejo y lo que traía pegado", "sub": "Tear-out, y luego el adhesivo de abajo. Raspar cutback es un día que nadie cotiza, y en vinil viejo ya deja de ser decisión mía por completo.", "en": "Old goods and what was stuck to them" },
    { "es": "Me ordenaron instalar encima de lecturas que yo reporté", "sub": "Lo escribí, me ordenaron seguir de todos modos, y este vale es la fecha en que pasó. Nada aquí dice qué significan las lecturas.", "en": "Told to go over readings I flagged" },
    { "es": "El cuarto no estaba libre ese día", "sub": "Cuadrillas todavía adentro, material apilado en mi piso, un lift estacionado en medio, muebles que nadie movió. La cuadrilla se quedó parada, o regresó.", "en": "The room was not clear on the day" },
    { "es": "Puertas, jambas y umbrales", "sub": "Hacer undercut, quitar y volver a colgar, saddles y transiciones en vanos que no estaban en mi alcance y me estorban.", "en": "Doors, jambs and thresholds" },
    { "es": "Mover cosas de otros", "sub": "Muebles, electrodomésticos, fixtures, racks, archiveros, un piano. Se movió porque el piso no se podía poner rodeándolo.", "en": "Moving somebody else's things" },
    { "es": "Más de lo que dibujó el plano", "sub": "Escalones de más, un clóset de más, un descanso, un cuarto que cambió de acabado, un quiebre que no está en la hoja con la que coticé.", "en": "More of it than the plan drew" },
    { "es": "Material distinto al que coticé", "sub": "Una sustitución, un cambio de producto o un cambio de lote ordenado después de que entregué mi presupuesto. No es queja — es una fecha y un hecho.", "en": "Different material than I bid" },
    { "es": "Reparar daño que ya estaba", "sub": "Daño de alguien más al subfloor o al trabajo ya puesto, que se tuvo que arreglar antes de que yo pudiera seguir.", "en": "Repairing damage that was already there" },
    { "es": "Trabajar alrededor de ellos y no de corrido", "sub": "Por fases, de noche, fines de semana, medio pasillo a la vez, o en un espacio ocupado — los mismos pies cuadrados costando el doble de horas.", "en": "Working around them instead of through it" },
    { "es": "Cargo por viaje — vine y no pude trabajar", "sub": "Cargué, manejé, lo caminé, no pude empezar. El día se fue, lo haya querido alguien o no.", "en": "Trip charge — I came and could not work" }
  ]
};


/* ─────────────────────────────────────────────────────────────────────────────
 * THE DEALER CALL — this trade's order vocabulary (shape #1, the ELEVENTH
 * instance). `flooring/tools.js` §2 held this rung open with the reason written
 * on it: "a vocabulary build the size of the supply-house order… half-building
 * that is worse than not building it."
 *
 * TWO THINGS IN HERE ARE NOT IN THE OTHER TEN ORDER DATASETS:
 *
 *   `run: true` ON AN ITEM IS DERIVED, NOT TAPPED. masonry/items.js made the
 *   same idea a CHECKBOX (`matchRun()`) because a mason genuinely has back-up
 *   wythe that matches nothing. Flooring has no such line: a plank carton, a
 *   stair nose and a T-mold in one area all come off one run whether or not
 *   anybody ticks a box, and sitework/items.js already wrote why that has to be
 *   read off the data — "asking a man to classify forty lines he already
 *   classified by picking them is the ceremony §THE GATE forbids." Only a
 *   WRITE-IN carries the tick, because a line he typed is a sentence only he
 *   can classify.
 *
 *   `atticable: true` IS THE SECOND HALF OF THE SAME READING and it is what
 *   makes this page this trade's rather than a supply-house form. Attic stock
 *   is in the spec, it is called in at close-out, and by close-out the run is
 *   gone — so the page raises it AT THE ORDER, once, as a question. It is on
 *   the goods, not on the trim: nobody has ever been asked for attic stock in
 *   stair nose.
 *
 * NOTHING HERE IS A NUMBER WE SUPPLY. No square feet per carton, no coverage,
 * no spread rate, no trowel notch, no waste factor and no conversion of
 * anything into anything. The `unit` key is the word the DEALER SELLS IN — it
 * is attached to a bare number and never to his own words — and it is left OFF
 * every line whose unit genuinely varies (solid wood by the carton or the
 * bundle, base by the coil or the four-foot, broadloom cut or full roll),
 * because a page that prints the wrong unit of issue orders the wrong truck.
 *
 * THAT RULE IS NOW MECHANICAL, because the first draft of this file BROKE IT SIX
 * TIMES while stating it three paragraphs up: "Wedges / shims — BY THE BAG OR
 * THE BUNDLE" carried `unit: "bag"`, so a bare 10 printed "10 bag" on a line
 * whose own words say bundle is just as likely. THE RULE: if the first clause of
 * a line's `sub` names two containers with an OR, that line carries NO unit —
 * asserted in the page's own drive, so it cannot rot back.
 * ───────────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  function n(s) { return "— " + s + " —"; }
  function ax(label, opts, wide) { return { k: label.toLowerCase().replace(/[^a-z]/g, ""), label: label, opts: opts, wide: !!wide }; }

  /* WHERE IT LANDS. Not a side of a building — this trade is inside, and the
   * only question that has ever mattered on a flooring delivery is WHICH FLOOR
   * and whether it goes in the space or sits on the dock. A roll of broadloom
   * that lands at the dock of a four-storey job is a second crew for a day. */
  var DROPS = [
    "Ground floor / the dock",
    "Up — say which floor in the note",
    "In the space it's going",
    "Staging room / the room we're using",
    "Garage",
    "Job trailer / conex",
    "Split it — see the note"
  ];
  function where() { return ax("Set it", [n("where it lands")].concat(DROPS), true); }

  /* A SIZE LADDER, not product data — the width he ASKS FOR, the same class of
   * vocabulary as plumbing's C×C/FIP ladder. Nothing here says what any roll
   * yields, and this file does no roll-width math of any kind. */
  function width() {
    return ax("Width", [n("which width"), "12 ft", "15 ft", "13 ft 2 in", "6 ft", "6 ft 6 in",
                        "Full roll — whatever it is", "Cut — say the length in the note"]);
  }

  var W = [where()];

  /* THE RUN IS NOT ONE RUN, and the first draft of this file said it was.
   * "A plank carton, a stair nose, a T-mold and a coil of base all come off one
   * run" is true of the first three and FALSE of the fourth: on a commercial job
   * the base is Roppe or Burke or Johnsonite, picked to COORDINATE by colour, and
   * on a carpet or tile job it is guaranteed to be another maker because the
   * mills do not make base at all. Printing it under the plank's lot number sends
   * a counter hunting for that number in a catalogue it does not appear in.
   *   FIELD — the goods and the mouldings the same mill wraps to go with them.
   *           They come off the lot he reads off his own carton.
   *   ACCESSORY — base, corners, cove cap, saddles, vents. These have a real
   *           matching problem and it is a DIFFERENT one: every coil on the job
   *           has to match every OTHER coil, off a lot he usually does not hold.
   * Two blocks, two sentences, one field. */
  function goods(name, sub, unit, extra) {
    var o = { n: name, sub: sub, run: "field", atticable: true, ax: extra || W };
    if (unit) o.unit = unit;
    return o;
  }
  function trim(name, sub, unit, fam) {
    var o = { n: name, sub: sub, run: fam || "field" };
    if (unit) o.unit = unit;
    return o;
  }
  /* THREE MORE KEYS THAT ARE READ OFF THE ITEM, for the same reason `run` is.
   * The first draft of this page decided all three with REGEXES ON THE ITEM
   * NAME, and both of the regexes were wrong against this very file — which is
   * the argument for the data, made by the data:
   *   /tape/  also matched "Masking / painter's tape" and "Duct tape" in
   *           SUNDRIES, so a man with forty cartons of plank, a roll of masking
   *           tape and NO adhesive was told nothing. The check died silently in
   *           exactly the case it exists for.
   *   /tile/  also matched "Carpet tile", which nobody has ever grouted, so a
   *           carpet-tile order was asked "Tile and no grout — on purpose?" —
   *           a page that does not know the trade, which is the FIELD-COOL bar
   *           failing out loud.
   * `holds` is what actually holds a floor DOWN — seam tape and seam sealer are
   * not on it, because a seam is a joint and not a bond, and tackless IS, because
   * a stretch-in carpet needs no adhesive and must not be nagged for one. */
  function holds(o) { o.holds = true; return o; }
  function grouted(o) { o.grouted = true; return o; }
  function isgrout(o) { o.grout = true; return o; }

  function plain(name, sub, unit, axes) {
    var o = { n: name, sub: sub };
    if (unit) o.unit = unit;
    if (axes) o.ax = axes;
    return o;
  }

  window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

  window.TOOLKIT_ITEMS.call = {
    drops: DROPS,

    /* A WRITE-IN IS HIS SENTENCE. It carries the run tick — and only the run
     * tick — because the odd line he types ("the border tile off the lobby
     * submittal") is exactly the one that has to match, and he is the only one
     * who can say so. */
    writeinFlags: [{ k: "run", label: "Has to come off the same run" }],
    writeinAx: [where()],

    cats: [
      {
        id: "call",
        name: "What are you calling in?",
        docName: "The call",
        hint: "Paste your whole list if you keep one — one line each. Count it the way the dealer sells it: 40 carton, 3 rolls, 6 pails, 2 bags. Tick the run box on anything that has to match, then set the run and the day below.",
        writein: true,
        items: []
      },

      {
        id: "goods",
        name: "What's going on the floor",
        docName: "Goods",
        hint: "Everything in here comes off a run, and the page gathers it at the bottom on its own. Colour and pattern go in the note, off the approved submittal — this page holds nobody's colour names.",
        items: [
          goods("Plank — LVP / LVT", "BY THE CARTON — colour and pattern in the note, off the submittal", "carton"),
          goods("Rigid core — SPC / WPC", "BY THE CARTON", "carton"),
          goods("Laminate", "BY THE CARTON", "carton"),
          goods("Engineered wood", "BY THE CARTON", "carton"),
          goods("Solid hardwood", "SAY CARTON OR BUNDLE — species, width and grade in the note", null, W),
          grouted(goods("Porcelain / ceramic tile", "BY THE CARTON — size and finish in the note", "carton")),
          grouted(goods("Natural stone tile", "SAY CARTON, CRATE OR PALLET — a stone lot moves more than a tile lot does", null, W)),
          goods("Carpet tile", "BY THE CARTON — colour and the lay direction in the note", "carton"),
          goods("Broadloom carpet", "SAY THE WIDTH AND WHETHER IT'S A CUT OR THE ROLL", null, [width(), where()]),
          goods("Sheet vinyl", "SAY THE WIDTH AND THE CUT", null, [width(), where()]),
          goods("Sheet rubber / sport floor", "SAY THE WIDTH AND THE CUT", null, [width(), where()]),
          goods("Entry / walk-off", "SAY THE SIZE AND WHETHER IT'S CUT TO THE WELL", null, W),
          goods("VCT — vinyl composition tile", "BY THE CARTON — colour and pattern in the note", "carton"),
          goods("Stair carpet / runner", "SAY THE WIDTH AND THE CUT", null, [width(), where()])
        ]
      },

      {
        id: "trim",
        name: "The edges, the fills and the stairs",
        docName: "Trim, fills and stair parts",
        /* THE HALF THAT GETS FORGOTTEN, and the reason the page exists. A man
         * orders forty cartons and calls the stair nose in three weeks later,
         * off a run that is gone. */
        hint: "The half nobody calls in with the goods. All of it has to come off the SAME run as the field material — order it now or it never matches.",
        items: [
          trim("Stair nose", "PER PIECE — say the length", "ea"),
          trim("Stair tread", "PER PIECE", "ea"),
          trim("Riser", "PER PIECE", "ea"),
          trim("Stringer / skirt", "PER PIECE", "ea"),
          trim("Reducer", "PER PIECE", "ea"),
          trim("T-mold", "PER PIECE", "ea"),
          trim("End cap / square nose", "PER PIECE", "ea"),
          trim("Threshold / saddle", "PER PIECE — say the width of the opening in the note", "ea", "base"),
          trim("Transition / edge profile", "PER PIECE — say the profile and the finish", "ea"),
          trim("Quarter round / shoe", "SAY PIECES OR FOOTAGE — it goes exactly how you say it"),
          trim("Wall base", "SAY COIL OR FOUR-FOOT, AND THE COLOUR", null, "base"),
          trim("Base corners — inside / outside", "PER PIECE — say how many of each", "ea", "base"),
          trim("Cove cap / cap strip", "SAY PIECES OR FOOTAGE", null, "base"),
          trim("Vents / registers to match", "PER PIECE — say the duct size in the note", "ea", "base"),
          /* WELD ROD IS RUN-BEARING AND IT IS NOT AN ADHESIVE. A welded seam in a
           * hospital corridor is colour-matched rod off the sheet's own run — the
           * page shipped sheet vinyl and sheet rubber for a day with no way to
           * call the rod that closes them. */
          trim("Weld rod / heat-weld rod", "BY THE COIL OR THE BOX — colour to match the sheet"),
          trim("Filler / putty — matched", "PER TUBE OR TUB"),
          trim("Trim / touch-up kit", "PER KIT", "kit")
        ]
      },

      {
        id: "stick",
        name: "What holds it down",
        docName: "Adhesive and fasteners",
        hint: "Name the adhesive off the spec or off the last job — this page has no coverage rate, no spread rate and no opinion about which one goes with what.",
        items: [
          holds(plain("Adhesive", "BY THE PAIL — name it in the note", "pail")),
          holds(plain("Pressure-sensitive adhesive", "BY THE PAIL", "pail")),
          holds(plain("Epoxy / urethane adhesive", "BY THE UNIT — say A+B or a single", "unit")),
          holds(plain("Spray adhesive", "BY THE CAN", "can")),
          holds(plain("Double-face tape", "BY THE ROLL", "roll")),
          plain("Seam tape", "BY THE ROLL", "roll"),
          plain("Seam sealer", "BY THE TUBE OR THE BOTTLE"),
          holds(plain("Tackless / tack strip", "BY THE BUNDLE", "bundle")),
          holds(plain("Carpet staples", "BY THE BOX", "bx")),
          holds(plain("Cleats / flooring nails", "BY THE BOX — say the length", "bx")),
          /* NAIL-DOWN CLEATS DO NOT FASTEN A SHEET OF BACKER, and the category is
           * called fasteners. */
          holds(plain("Backer-board / underlayment screws", "BY THE BOX — say the length", "bx")),
          holds(plain("Thin-set / mortar", "BY THE BAG — say modified or not, and the colour", "bag")),
          isgrout(plain("Grout", "BY THE BAG — sanded or unsanded, and the colour, in the note", "bag")),
          plain("Grout sealer", "BY THE BOTTLE OR THE JUG"),
          plain("Silicone / colour-matched caulk", "BY THE TUBE — say the colour it has to match", "tube")
        ]
      },

      {
        id: "under",
        name: "What goes under it",
        docName: "Under it",
        hint: "Prep and underlayment. Nothing here says what any of it is rated for, how thick it goes or how long it takes — that is off your own bag and your own submittal.",
        items: [
          plain("Underlayment / pad", "BY THE ROLL", "roll", W),
          plain("Acoustic / sound mat", "BY THE ROLL", "roll", W),
          plain("Moisture barrier film", "BY THE ROLL", "roll", W),
          plain("Crack-isolation / uncoupling membrane", "BY THE ROLL", "roll", W),
          plain("Cement board", "BY THE SHEET", "sheet", W),
          plain("Underlayment panel / plywood", "BY THE SHEET — say the thickness", "sheet", W),
          plain("Patch / skimcoat", "BY THE BAG", "bag", W),
          plain("Self-leveler", "BY THE BAG", "bag", W),
          plain("Primer", "BY THE PAIL OR THE JUG"),
          plain("Moisture mitigation — 2-part system", "BY THE KIT OR THE UNIT — name it in the note, off your own spec"),
          plain("Rosin / builder's paper", "BY THE ROLL", "roll")
        ]
      },

      {
        id: "sundry",
        name: "What the crew burns through",
        docName: "Sundries",
        hint: "The jog, not a catalog — it is the short line on tape and blades that sends somebody back at ten in the morning.",
        items: [
          plain("Utility blades", "BY THE BOX", "bx"),
          plain("Hook blades", "BY THE BOX", "bx"),
          plain("Trowel", "SAY THE NOTCH YOU WANT — your call, off your own adhesive", "ea"),
          plain("Mixing paddle", "EACH", "ea"),
          plain("Buckets", "EACH", "ea"),
          plain("Roller — say weight, and rent or buy", "EACH", "ea"),
          plain("Kneeler board", "EACH", "ea"),
          plain("Knee pads", "PER PAIR", "pair"),
          plain("Chalk / chalk line", "EACH", "ea"),
          plain("Spacers", "BY THE BAG — say the size", "bag"),
          plain("Wedges / shims", "BY THE BAG OR THE BUNDLE"),
          plain("Masking / painter's tape", "BY THE ROLL", "roll"),
          plain("Duct tape", "BY THE ROLL", "roll"),
          plain("Rags", "BY THE BOX OR THE BAG"),
          plain("Sanding screen / paper", "BY THE BOX", "bx"),
          plain("Undercut / jamb saw blade", "EACH", "ea"),
          plain("Diamond blade — wet saw", "EACH — say the size", "ea"),
          plain("Vacuum bags / filters", "BY THE BOX", "bx"),
          plain("Ram board / floor protection", "BY THE ROLL", "roll", W),
          plain("Contractor bags", "BY THE BOX", "bx"),
          plain("Marker / silver pencil", "EACH", "ea")
        ]
      },

      {
        id: "back",
        name: "What goes back on the same truck",
        docName: "Going back",
        hint: "Say it now and it rides back with the driver. Say it at close-out and it is a second trip and a restock argument.",
        items: [
          plain("Full unopened cartons back", "SAY HOW MANY AND OFF WHICH RUN — an open carton is not a return", "carton"),
          plain("A roll to go back", "SAY THE WIDTH AND WHAT'S LEFT ON IT"),
          plain("Pallets / empties", "SAY HOW MANY", "pallet"),
          plain("Came wrong — going back", "SAY WHAT CAME AND WHAT IT WAS SUPPOSED TO BE")
        ]
      }
    ]
  };
})();
