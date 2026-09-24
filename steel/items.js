/* STEEL & MISC METALS FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * trade.js is IDENTITY AND COPY, tools.js is the REGISTRY, and this file is the
 * trade's WORDS — what he picks from, in the order he'd say them. Nothing here
 * is a spec, a dimension, a torque, a weld size, a material grade or a capacity,
 * because trade.js refuses all of those and a picker is where a refusal quietly
 * dies if nobody is watching it.
 *
 * EVERY LIST BELOW WAS WRITTEN AGAINST TWO QUESTIONS the panel put on the
 * record: (1) is this the certified record wearing a coordination hat? — if a
 * line needed a torque, a weld map, a WPS, a mill cert or a capacity to be
 * useful, it was cut; and (2) is this the ERECTOR's crane-day scope rather than
 * the EMBEDS / MISC-METALS scope this kit is drawn around? — the raising gang's
 * own coordination lives in getting-in as a section, never in the leave-out
 * ledger. What is left is the one thing steel never had: its own half of a
 * conversation five other trades are already having at it.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── BEFORE THE DECK POURS (shape #3 — shared/rowlog.js) ─────────────────────
 * THE PINNED TOOL, and the page that answers the panel's own objection. Five
 * shipped kits route asks AT steel — embeds and weld clips (electrical), loose
 * lintels and angle and embeds/plates/anchor bolts (masonry), roof-opening cut
 * and a dunnage stand (hvac), steel-for-hangers and roof-drain openings
 * (plumbing), embeds/anchor-bolts/templates and the elevated deck (concrete).
 * Every one of them lands IN his steel or his deck, and there was no steel/ on
 * the rack for any of it to land on. This is the ledger where it does: one row
 * per leave-out somebody else needs in the iron before the deck closes over it.
 *
 * WHOSE it is, WHAT it is, which column line, whether it is on-the-drawing / set
 * / set-and-tied / not-coming / poured-over, and the GATE it has to beat. Once
 * the deck is screwed off and the pour goes green, a missed embed is a core bit
 * through cured concrete and a field weld to an inspector's cert — so it is
 * walked while it is still a clip and a drawing.
 *
 * WHAT IT NEVER CARRIES, and the refusal list is why: no torque, no weld size or
 * map, no WPS, no mill cert, no capacity, no material grade, no embed tolerance
 * as a value, and no verdict that a connection holds or a weld is good. "Set and
 * tied in" is an OBSERVATION with a photo behind it — a man stood at it and
 * looked — never a call that it is right. That is refusal 1 and refusal 5, and
 * there is no field on this page shaped to hold either.
 */
window.TOOLKIT_ITEMS.leaveout = {
  /* WHOSE IT IS — the five outfits that already route asks to steel on the rack,
     plus the ones a real deck picks up. "Don't know whose" earns its slot: a
     clip welded on a column from a phase nobody documented is somebody's, and
     the row with no owner is the one that gets covered. */
  whose: [
    "Electrician",
    "HVAC / mechanical",
    "Plumber",
    "Concrete / rebar",
    "Mason",
    "Low-voltage / fire",
    "Detailer / fabricator",
    "GC / super",
    "Ours — our own iron",
    "Don't know whose"
  ],

  /* WHAT IT IS — the embeds-and-misc-metals vocabulary, named the way it gets
     named standing on the deck. Every one is a LEAVE-OUT: a thing that has to be
     in, on or through the steel before it is covered. No sizes, no grades. */
  whats: [
    "Embed plate / weld plate",
    "Weld clip / connection clip",
    "Anchor bolts / setting template",
    "Loose lintel / loose angle",
    "Sleeve / pipe penetration",
    "Deck or slab opening / block-out",
    "Roof-drain opening",
    "Dunnage / equipment stand",
    "Hanger steel / support steel",
    "Pour stop / edge angle / closure",
    "Bent plate / knife plate / gusset",
    "Rail post base / bollard / misc",
    "Something else — I'll type it"
  ],

  /* WHERE — steel says it by the grid, not the room. A column line is an address
     everybody on the job shares; "the northeast corner" is one man's guess. */
  faces: [
    "Column line / grid",
    "Between two columns — the bay",
    "The deck / this level",
    "A beam or a girder",
    "Slab edge / perimeter",
    "A stair or a shaft opening",
    "The whole level / area"
  ],

  /* WHAT HE FOUND — every one is something he SAW. There is no "good weld" and no
     "in tolerance" in this list on purpose: "set and tied in" is "somebody set it
     and I saw it and photographed it", never a verdict that it is right, which is
     refusal 5 and is the inspector's call. [0] is the default and it is the one
     that is only a drawing so far. */
  states: [
    "On the drawing — nothing set yet",
    "Set, not welded or tied in yet",
    "Set and tied in — I saw it",
    "Not coming — they say they don't need it",
    "Deck's closing / poured over — found it after"
  ],

  /* WHAT HE NEEDS DECIDED — every one hands the decision to the outfit that owns
     the leave-out or to the man who runs the job. "A drawing or a dimension off
     the approved set" is the one that keeps him honest: he places off THEIR
     sheet, never off his own guess. */
  asks: [
    "Get it to me before I set that bay",
    "Set it or weld it before the deck closes",
    "Give me a location off the approved set — I'm not guessing it",
    "Tell me in writing it isn't coming and I'll deck over it",
    "Walk the deck with me before it pours",
    "It's in — I'm decking over it, no action"
  ],

  /* THE GATE — the irreversible moments, in the order they happen, in the crew's
     own words. These are the `by:` markers five kits already gate their asks to:
     crane day, the set, the deck screwed off, the pre-pour walk, the pour, the
     bond beam. A date slips; a pour does not un-pour. */
  gates: [
    "Before crane day / before I fly it",
    "Before I set that bay",
    "Before the deck gets screwed off",
    "Before the pre-pour walk",
    "Before the deck pours",
    "Before the bond beam / head course",
    "Before the steel's covered"
  ],

  sent: ["Sent", "Answered", "Set — I saw it in"]
};

/* ── BEFORE I SET (the cross-boundary ASK — shared/note.js) ──────────────────
 * The ask half of the loop the deploy asserts as a pair. Steel is the hub of
 * the frame: everybody's embeds go into it and everybody's hangers come off it,
 * and every one of those is owed in a window that shuts when the deck pours.
 * This is steel finally composing its own side of the five conversations the
 * rack already routes AT it. Every spec is WHO / WHERE / GATE off THEIR approved
 * drawing — never a size, a grade, a weld or a load of ours.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before I Set",
  eyebrow: "Steel · you → everybody whose work lands in your iron",
  lede: "The frame closes onto a deck and the deck pours once. Every embed, clip, sleeve, opening and hanger somebody else needs in the steel is a ten-minute job while it's a drawing and a core bit through cured concrete after. This is what you need placed, located, framed and answered before you set and before the deck goes off: whose it is, where on the grid, and the gate it has to beat. Walk it a week out, tap the rows, send one message per outfit. The refusal is telling the super the deck closed on him; this page is how you never send it.",
  docSubject: "Before I set — what I need out of your outfit",
  docSubjectWith: "Before I set — what I need from {to}",
  closing: "That's my list before I set that area and close the deck. If a line's wrong, or there's something you need in my steel that isn't on it, hit me back today — it's a clip and a drawing this week and a saw cut and a field weld next week. Everything on here I place or frame off YOUR approved sheet; I set nothing off memory and I move nothing that's on a stamped drawing without a marked-up sheet back from the detailer.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> own walk and the approved set. This page sets no torque, no weld size, no bolt tension, no material grade and no capacity &mdash; the shop drawing and the engineer own all of that, and it cites the sheet, never restates it. It gives no connection detail and no erection sequence of ours. It never says a connection holds, a weld is good, a bolt is tight or the steel is safe to load. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work or to change a stamped drawing.</b>",
  offHint: "The approved erection set and its revision is half the argument. Name the sheet you took this off and the detailer and the super can work your list against the stamped drawings; leave it off and it's one foreman's memory until somebody re-walks the deck with you — the morning the crane's already booked.",
  phJob: "Building C — structural steel + misc metals",
  phOff: "S-401 rev 2, erection dwgs E-1 thru E-6",
  phFrom: "Ray T — Kingpost Erectors",
  phArea: "the second level, lines 4 through 7",
  areaLabel: "Area / grid lines",
  areaHint: "Type the area the way the crew says it — a level, a grid range, a bay — and it becomes a button for the rest of the walk.",
  specLabel: "What exactly",
  phSpec: "or type your own",
  specHint: "Pick what you need above and the usual lines show up here — yours, off the approved set, never a spec of ours.",
  placeLabel: "Where on the grid",
  phPlace: "at line C-5, top of steel · or: every column on line 4",
  phNote: "anything that won't fit above — the sheet it's detailed on, whose embed it is, what's waiting on an RFI",
  phTel: "the number they answer from the deck",
  docBoundary: "place and frame them off your own approved set before you set, and change nothing on a stamped drawing without a marked-up sheet back.",

  who: [
    { v: "gc", label: "GC super" },
    { v: "conc", label: "Concrete / rebar" },
    { v: "ec", label: "Electrician" },
    { v: "mech", label: "HVAC / mechanical" },
    { v: "plumb", label: "Plumber" },
    { v: "mason", label: "Mason" },
    { v: "lv", label: "Low-voltage / fire" },
    { v: "detail", label: "Detailer / fabricator" },
    { v: "owner", label: "Owner / CM" }
  ],

  milestones: [
    { v: "crane", label: "Before crane day" },
    { v: "set", label: "Before I set that bay" },
    { v: "deck", label: "Before the deck's screwed off" },
    { v: "prepour", label: "Before the pre-pour walk" },
    { v: "pour", label: "Before the deck pours" },
    { v: "cover", label: "Before the steel's covered" }
  ],

  asks: [
    { v: "set", label: "The approved set, the lines and the laydown", who: "gc", by: "crane", specs: [
      "The current approved erection set and every open RFI answer, by sheet number — I set off the stamped drawing, not the emailed sketch",
      "Control lines and a benchmark I can pull from, so my column lines and everybody's embeds land off the same reference",
      "Crane access, a pad it can set on, and laydown for the iron off the trucks — that's its own section on my access ask",
      "The pour schedule per level, so I know which deck closes when and what has to be in it first"
    ] },
    { v: "bolts", label: "Anchor bolts, templates and the pre-pour walk", who: "conc", by: "prepour", specs: [
      "Anchor bolts set to the template off the same control lines, and braced so they don't walk when you vibrate",
      "Grout pockets and base-plate grout ready when I call for it — I'm not setting a column on a bolt that isn't there",
      "Walk the pre-pour with me: I check my bolts and embeds while it's still green, because after it sets it's a saw",
      "Elevated deck screwed off, edges closed and my penetrations framed before you tie the top mat"
    ] },
    { v: "embeds", label: "Embeds, weld clips and stub-ups clear", who: "ec", by: "deck", specs: [
      "Every embed and weld clip located off the approved sheet before I set that bay — give me the sheet, I'll place to it",
      "Conduit stub-ups clear of my base plates and my column lines, or tell me where they land so I don't set on them",
      "Anything that welds to my steel, show me the detail sheet — I weld to the stamped drawing, never a field call",
      "Power we can reach for the welder, or tell me I'm bringing a machine"
    ] },
    { v: "dunnage", label: "Dunnage, stands and deck openings", who: "mech", by: "deck", specs: [
      "Dunnage and equipment-stand locations off your drawing before the deck closes — the loads and the sizes are yours to state, I set what your sheet says",
      "Every roof or deck opening you need cut, located off the approved set, so I frame it in the deck and don't burn it after",
      "Tell me what's hanging off my steel later so I leave the clips for it now",
      "If a unit moved since the last set, tell me before I frame the opening, not after"
    ] },
    { v: "hangers", label: "Hanger steel, sleeves and roof-drain openings", who: "plumb", by: "deck", specs: [
      "Hanger-steel and support locations off your drawing so I put the steel where your hangers land",
      "Sleeves and pipe penetrations located before the deck closes — a sleeve now is a core bit later",
      "Roof-drain openings located off the approved set and I'll frame them in the deck",
      "Anything through the slab edge, tell me before I set the pour stop"
    ] },
    { v: "lintels", label: "Loose lintels, angle and the bond beam", who: "mason", by: "cover", specs: [
      "The loose-lintel and loose-angle schedule off the approved set, and I'll have them on site before your head course",
      "Tell me when the bond beam and the head course land so my embeds and plates are in the wall first",
      "Where my steel bears on your wall, walk it once — I'd rather sort the bearing than the blame",
      "Anything that embeds in the CMU, give me the sheet and the course it lands on"
    ] },
    { v: "backing", label: "Backing and supports above the deck", who: "lv", by: "cover", specs: [
      "Backing, sleeves and support-steel locations above the deck before it's closed and covered",
      "Anything fire-related that lands on my steel, give me the detail sheet — I place to the stamped drawing, never a field call",
      "Tell me what's coming later so I leave the clip now instead of drilling a finished assembly"
    ] },
    { v: "rfi", label: "The drawings, the RFIs and what changed", who: "detail", by: "set", specs: [
      "The current approved shop and erection drawings, and every open RFI answer by number — I'm waiting on some before I can set",
      "Any field condition that doesn't match the stamped set comes to you and the GC on a marked-up sheet — I don't cut or re-detail on a say-so",
      "If a connection or an embed changed, send the revised sheet before I set to it, not after",
      "Tell me which sheet governs when two disagree"
    ] },
    { v: "access", label: "The pad, the laydown and the crane day", who: "owner", by: "crane", specs: [
      "The crane pad, the swing area and laydown for the iron on the day you give me — that's coordinated on my access ask, one page",
      "Overhead clear of power lines in the swing — a line in it is killed by the utility, on its own paper, before we swing; that's never mine to call",
      "The route the trucks take in and where they turn around with forty feet of steel on the trailer",
      "Who I meet the first morning to walk the pad, the laydown and the lines"
    ] }
  ]
};

/* ── WALK BACK (the reconcile engine) ───────────────────────────────────────
 * The answer half of the loop. The fourth rung is this trade's own and it is the
 * one that keeps the page honest: on a steel walk, a large share of what gets
 * flagged is not a miss, it is how the connection is DETAILED on the approved
 * drawings — a plate where the sheet puts it, a bolt pattern the engineer drew,
 * an embed at the dimension the stamped set gives. Steel cannot field-modify
 * engineered iron on somebody's say-so; a change is a marked-up sheet back
 * through the detailer and the engineer. It is not a refusal and not a
 * commitment — it is an ask pointed at the approved set.
 * shared/reconcile.js classifies "its the detail" as "ask".
 */
window.TOOLKIT_ANSWER = {
  toolName: "Walk Back",
  eyebrow: "Steel · them → you → back",
  lede: "The super, the detailer or the inspector walked the steel and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll set it, with a day on it · Already in · Not mine · It's the detail — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll set it line carries a day — hold me to it, and they land together instead of a return trip per bolt. Already in is just that — go stand at it. Not mine is another outfit's work — a rodbuster's bar, an embed that was concrete's to set, a clip that welds to somebody else's steel — and those sit dated in my own log, which comes to you separately. It's the detail is the one worth reading twice: it means what you're looking at is how the connection is drawn on the approved set — the plate, the bolt pattern, the embed dimension the stamped drawing gives. I don't field-modify engineered steel on a walk; changing it is a marked-up sheet back through the detailer and the engineer, and that's their call, not mine. Tell me which way the sheet comes back and I'll set to it.",
  answers: ["We'll set it", "Already in", "Not mine", "It's the detail"],
  phJob: "Building C — structural steel",
  phTo: "Dana K — GC super",
  phFrom: "Ray T — Kingpost Erectors",
  phOff: "steel walk 9/12, off S-401 rev 2",
  paste: "Building C — steel walk — Sep 12\n\nJob: Building C — structural steel\nFrom: Dana K — GC super\n\n14. line 4 — two weld clips missing at the beam for the mechanical dunnage\n15. line C-5 — anchor bolts look off the column, plate hanging over\n16. level 2 — roof-drain opening not framed, plumbing's waiting\n17. line 6 — knife plate at the girder doesn't match the sheet\n18. stair 2 — rail post base not set, guard's open\n19. line 3 — embed for the mason's lintel not in, head course this week\n20. deck — three sleeves not through before you closed it"
};

/* ── GETTING IN (the access engine) ─────────────────────────────────────────
 * Steel works over other people's heads and next to their power, and the crane
 * day is the one moment on this rack that a whole building organizes around. So
 * the raising gang's coordination — the pad, the swing, the laydown, the lift —
 * lives HERE as its own section rather than in the leave-out ledger, per the
 * kit's scope rule. Every process the building or the utility runs comes back as
 * a handback: the lane closure, the power-down on the overhead lines, the
 * hot-work permit for the welding, roof access — each is theirs to run and to
 * number, and this page never pretends otherwise.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Steel · you → whoever holds the site",
  lede: "Setting iron on a site somebody else runs, with a crane that swings over their building and a welder that throws sparks near their people. They hold the lane, the laydown, the power lines, the hot-work permit and the phone that rings when a boom goes up over the sidewalk. Send the ask that gets a real yes before the crane's booked: the pad and the swing, laydown for the steel, the route the trucks take, power for the welder, the approved set and the control lines — and which days. Every heads-up on it hands the process back to whoever owns it — on his site and near the utility's lines, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    "Crane day — one lift",
    "A few days setting",
    "A week or more on the steel",
    "Early starts only",
    "Whatever you'll give me"
  ],

  need: [
    { name: "A pad and a swing area for the crane by the hour you name", sub: "level ground it can set and swing on, clear of parking — one car in the swing is a day the crane sits and I still pay for it" },
    { name: "Laydown for the iron off the trucks", sub: "somewhere close to the pick, out of the way, where nobody moves it overnight — forty-foot steel doesn't get shuffled twice" },
    { name: "The route the trucks take in, and where they turn around", sub: "a trailer of steel needs the gate, the turn and the overhead checked before it shows, not while it's blocking the road" },
    { name: "Power we can reach for the welder", sub: "a real feed or tell me it's a machine, and I'll plan the noise and the fuel around your hours" },
    { name: "The stamped set and the control lines", sub: "the sealed erection drawings and a benchmark I pull from — I set off the drawing, not the sketch, and off your line, not my guess" },
    { name: "A flagger or a spotter if the crane's near people or a road", sub: "tell me if it's yours or mine, because a boom over a sidewalk needs somebody whose only job is watching it" },
    { name: "Somewhere the crew stages and gears up", sub: "a spot for the gang box, the bottles and the leads that isn't under the swing" },
    { name: "Somebody to meet us the first morning", sub: "walk the pad, the laydown, the lines and the swing once — after that we're repeatable" }
  ],

  heads: [
    { name: "The crane sets up and the boom swings over the building", sub: "tell me who owns the lift plan and the crane permit and who clears the swing area of people — a boom over an occupied building is coordinated by whoever runs the site, never on my say-so" },
    { name: "There are overhead power lines in the swing or on the truck route", sub: "tell me who's getting the line killed, and when — a covered line is still a hot line, and killing it and saying so is the line owner's, on its own paper; my crane does not swing near it until they have" },
    { name: "A lane, a sidewalk or a drive under the crane needs a closure while we lift", sub: "tell me who owns the closure and the permit — I'll cone and barricade what you tell me to, where you tell me, and the notice is yours to run" },
    { name: "The welder and the torch are hot work near their people", sub: "tell me who owns the hot-work permit and the fire watch and which hours you'll take the sparks and the smoke — the permit is the building's, never a checkbox on my page" },
    { name: "We may need roof or deck access to set or tie off", sub: "tell me who owns access and whether anybody has to be with us — I'm not stepping onto a deck or a roof on my own say-so" },
    { name: "The impact wrench, the grinder and the welder run most of the day", sub: "tell me which hours you'll take it and which side of the building sleeps, takes calls or has a fresh-air intake" },
    { name: "Steel gets craned over a space that's occupied or open below", sub: "tell me who clears the floor below the pick and who tells the people under it — nothing swings over that floor until it's clear and whoever cleared it says so; a name on this page isn't a clear floor" },
    { name: "A trailer of steel sits in the gate or the lane while we pick it clean", sub: "tell me who owns the gate and the traffic control for a delivery that can't move until the crane empties it — forty feet of iron doesn't pull out fast" },
    { name: "Fall-protection anchors may have to go into your structure", sub: "tell me who owns the structure we tie to and who signs off on an anchor point — I'm not drilling a tie-off into somebody's building on my own call" }
  ],

  phSite: "Building C — 120 Harbor",
  phRoom: "the north half, lines 1 through 7",
  phHow: "in off Harbor, past the gate, laydown on the east lot",
  phScope: "set structural steel and misc metals, north half — crane day Tuesday, a crew of five, a welder and a machine",
  phLoud: "the crane, the impact wrench and the welder, most of the day",
  phTo: "Marcus D — CM",
  phMe: "Ray T — 559-555-0143",
  phCo: "Kingpost Erectors",

  /* THE THREE FIELDS THE ENGINE REQUIRES. `closing` is CONCATENATED by the page
     (`G.closing.concat([...])`), so omitting it is a TypeError on load and a
     blank page at every width, not a missing sentence. */
  warn: "<b>It&rsquo;s an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation, a lift plan or an approval, and every heads-up on it hands the process back to whoever owns it &mdash; the lane closure, the crane permit, the power-down on the overhead lines, the hot-work permit and the fire watch, roof access and clearing the floor below a pick are the site&rsquo;s and the utility&rsquo;s to run and to number, and we never will.",

  closing: [
    "This is an ask, not a booking — nothing gets craned until you answer. Wrong days? Name the ones the site can live with and we'll take them.",
    "Saying yes: tell me the gate, the window you're actually giving us, who meets us the first morning, where the pad and the laydown go, and where the power and the control lines are — and the ones that matter most, who owns the closure, the power-down on any overhead line, and the hot-work permit for the welding, because none of those is ours to issue. If a boom swings over any floor, it's cleared and whoever cleared it has said so before we pick — a name isn't a clear floor."
  ]
};

/* ── NOT READY TO SET (shape #2 — shared/note.js) ───────────────────────────
 * THE GO/NO-GO, and the twin of paving's Not Ready To Pave and doors' Not Ready
 * To Hang — steel's own, sent the ONE morning the crane's already on the clock.
 * Before I Set is the week-out ask; getting-in is the occupied-site ask. This is
 * neither: it is 6 a.m., the iron's on the truck, a crane and a raising gang are
 * on standby whether it flies or not, and one of the things that had to be ready
 * isn't. He walks the pick, names what stops the set IN HIS WORDS, and sends the
 * only ask that matters — fix it and tell me who and when, or give me a NEW DAY
 * for the crew and the crane, in writing. There is NO fly-it-as-it-sits reply
 * (C3749): a hot line, an anchor bolt, an embed, the deck below and a detail that
 * doesn't match clear with whoever owns them, never on a super's written go — and
 * no stop below may ask for one. A crane day does not come back, and iron set on
 * a condition somebody else owned is on HIS record; this note is what the hold
 * stood on.
 *
 * WHAT IT NEVER CARRIES — the same refusal list every steel page stands on. No
 * torque, no bolt tension, no weld size, no capacity, no survey elevation, no
 * tolerance as a value, and no verdict that a connection is ready to load or a
 * bolt is right. "Nobody's shot the bolts to line and grade" is a COORDINATION
 * fact — the shot is somebody else's number and this page never states it. Every
 * stop is a condition with the ASK riding under it, so the note reads as a list a
 * super can clear by lunch, not a complaint — and the wind call and the level
 * reading are HIS, in free text, with no threshold of ours behind either.
 */
window.TOOLKIT_ITEMS.notready = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Concrete foreman (bolts / embeds / the deck)",
    "Owner's rep / construction manager",
    "Building / facility manager",
    "The crane / rigging outfit",
    "Detailer / engineer, through the office",
    "Another trade's foreman"
  ],

  stops: [
    {
      name: "Anchor bolts aren't set — I've nothing to land on",
      sub: "The columns land on them and they're not in, or not where the base plate wants them. Whoever set them brings them in off the approved anchor-bolt plan; a bolt fixed or moved comes back on the engineer's paper, not somebody's say-so, before a column lands on it."
    },
    {
      name: "Bolts are in, but nobody's shot them to line and grade",
      sub: "I'm not dropping a column onto bolts nobody's confirmed — that shot is the surveyor's number, not mine, and I don't state it. Tell me who's confirming them and when."
    },
    {
      name: "The embeds or plates I weld to aren't cast, or they moved",
      sub: "The clips and the beam seats land on somebody's embed and it's not in the concrete, or it's not where the set puts it. Whoever cast it owns it — off their sheet — and a fix is a revised detail back through the detailer and the engineer, not a field-fit on a tag."
    },
    {
      name: "The deck or slab I set off isn't poured, or isn't cured",
      sub: "I can't land the next tier or a column off a floor that isn't there yet. Tell me the day it's poured, and the day the engineer's release to load it comes back on paper — the day, not the week; whether it's cured to carry is the engineer's call, not mine or yours."
    },
    {
      name: "The crane can't get set up — no pad, soft ground, radius not clear",
      sub: "A crane that can't set where the pick needs it doesn't fly the steel. Tell me who's getting the mats down and the setup clear, and by when — the iron's on the truck at six either way."
    },
    {
      name: "Laydown's blocked — nowhere to land the iron in the pick",
      sub: "The steel's coming off the truck and there's nowhere in reach of the hook to set it down. Tell me the day the yard's actually mine, and keep it clear after that."
    },
    {
      name: "Power lines over the swing, still hot",
      sub: "The boom or the load could reach the line and nobody's had it de-energized. Killing it is the utility's, on its own paper — a spotter keeps a clearance, he doesn't make one. I own none of it, and I don't fly under a hot line."
    },
    {
      name: "No approved erection set, or the wrong rev, for this pick",
      sub: "I'm not flying iron off a sheet the engineer already changed. Send me the rev I'm erecting to and a name who answers when it doesn't fit."
    },
    {
      name: "The control lines or the benchmark aren't set",
      sub: "I set to line and grade and I've got no line to set to. Tell me who's shooting the control and when — that's the surveyor's, not mine."
    },
    {
      name: "The crane and the trucks can't get in — access is blocked",
      sub: "A loaded truck and a crane don't turn where a pickup turns. Tell me who moves the fence, the trailer or the pile, and by when."
    },
    {
      name: "Wind's over the limit, or it's coming — my call, my words",
      sub: "I'm not flying iron in this wind, and here's what I saw. No threshold of mine is on this note; the crane order stands or cancels on what I'm telling you now."
    },
    {
      name: "Hot work near their people, no fire watch or permit",
      sub: "I'm welding and burning near an occupied space and there's no watch and no hot-work permit. Whoever holds the building arranges both before I strike an arc."
    },
    {
      name: "What's in front of me isn't how it's detailed",
      sub: "The connection, the plate or the bolt pattern doesn't match the stamped set, and I don't field-modify engineered steel on a walk. It's a marked-up sheet back through the detailer and the engineer — their call, not a fix on crane morning."
    }
  ],

  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};
