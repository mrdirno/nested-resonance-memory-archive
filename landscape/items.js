/* LANDSCAPE & IRRIGATION FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary that keeps a trade config from rotting (private roster, §THE
 * THREE ENGINES): trade.js = IDENTITY + COPY · tools.js = REGISTRY · this file
 * = the trade's VOCABULARY DATA. What goes through a sleeve, what a crossing
 * is under, what stops a planting, what came off a nursery truck and what was
 * wrong with it, the asks each outfit owes him. Never in the identity config,
 * never inline in a page.
 *
 * WHAT IS NOT IN HERE, AND WILL NOT BE — the refusal list from trade.js, in
 * its data form, because this is the file where a later cycle would be tempted
 * to add it: no precipitation or application rate, no run time, no watering
 * schedule · no pipe, valve, wire or sleeve SIZE we supply · no cover depth,
 * trench depth or separation · no backflow test value · no soil, amendment or
 * fertilizer rate · no planting depth, spacing or staking spec · no nursery
 * grading standard (he types what is ON THE TAG) · no slope or drainage number
 * · no tree-protection dimension · no plant-selection verdict. Every list
 * below is a list of THINGS HE MIGHT SAY, never a list of values he should
 * use. Where a number belongs, the field is empty and the placeholder tells
 * him it comes off his own plan sheet, his own submittal or his own tape.
 *
 * AND THE WORD THAT IS NOT IN HERE: "sprinkler". Twelve kits on this rack use
 * it to mean fire protection. This file says heads, valves, mainline, laterals,
 * drip, zones and the clock, and the only time the other word appears is inside
 * a man's own mouth as a thing he might say.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── WHERE I CROSS (shape #3 — shared/rowlog.js) ────────────────────────────
 * THE PINNED TOOL, and the one page on this hub that could not exist anywhere
 * else. He walks every place HIS pipe has to get under somebody else's
 * concrete, paving or wall BEFORE that work closes, and sends the man who is
 * pouring a block that pastes in beside his pour. Every value on a row is a
 * place he named, a thing he chose or a sleeve he is putting in off his own
 * submittal; the page supplies none of them. Concrete already wrote his ask
 * from its own side — "driveway and flatwork sleeves — irrigation, gas,
 * conduit — go in before I set forms" — and had to aim it at the plumber.
 * This is the letter back.
 */
window.TOOLKIT_ITEMS.crossings = {
  /* WHAT IS GOING THROUGH IT. The receiver reading "mainline + valve wire"
     knows instantly it is not a drain, which is the whole reason the axis
     exists. Spoken exactly like this on a job. */
  carries: [
    "Mainline",
    "Lateral",
    "Drip feed",
    "Valve wire",
    "Low-voltage / lighting",
    "Drain line",
    "Spare — empty",
    "Not decided yet"
  ],

  /* WHAT IT IS UNDER, as a crossing gets described standing at it. */
  unders: [
    "Driveway",
    "Walk / sidewalk",
    "Curb & gutter",
    "Patio / slab",
    "Wall footing",
    "Paving / asphalt",
    "Pavers on base",
    "Existing — cutting it"
  ],

  /* HOW HE LEFT IT MARKED, because a sleeve a finisher cannot find is a sleeve
     that gets kicked into the form and poured over. */
  marked: [
    "Painted & flagged",
    "Flagged only",
    "Not marked yet"
  ],

  /* THE GATE EACH ROW HAS TO BEAT — the other man's sequence words, because
     "ASAP" is not a date and "before you set forms" is. */
  gates: [
    "Before you set forms",
    "Before the pour",
    "Before the base rolls",
    "Before you pave",
    "Before backfill",
    "Before the wall goes up",
    "Punch — whenever it lands",
    "Not called yet"
  ],

  states: ["Sent", "Confirmed", "In — I saw it"]
};

/* ── OFF THE TRUCK (shape #3 — shared/rowlog.js) ────────────────────────────
 * A nursery semi gets signed for in the time it takes to walk it, and from
 * that signature forward every dead one is arguably his. This is what he
 * counts against his OWN slip, sent the same afternoon. It prices nothing,
 * grades nothing to any standard, and never says why a plant looks the way
 * it looks — it counts, and it says what the tag says.
 */
window.TOOLKIT_ITEMS.truck = {
  kinds: [
    "Trees — B&B",
    "Trees — container",
    "Shrubs",
    "Groundcover / flats",
    "Sod",
    "Soil / mulch / bark",
    "Boulders / stone / DG",
    "Pipe & fittings",
    "Valves / heads / boxes",
    "The clock / wire",
    "Drip / emitters",
    "Something else"
  ],

  /* WHAT IS WRONG WITH IT. "Short" and "not what I ordered" carry the slip;
     the rest is what he can see from the tailgate, in his words. */
  wrongs: [
    "Short — didn't come",
    "Short — partial count",
    "Not what I ordered",
    "Wrong size on the tag",
    "Rootbound / pot-bound",
    "Broken leader / limbs",
    "Dry — wilted on the truck",
    "Dumped, not set down",
    "Wet load — the soil's a bog",
    "Damaged / bent / cracked",
    "Not on my slip at all",
    "Came for another job"
  ],

  /* WHERE IT GOT FOUND, because a broken leader seen on the trailer and one
     found in staging on day six are two entirely different conversations
     and only one of them is the grower's. */
  found: [
    "On the truck, before I signed",
    "On the truck, after I signed",
    "In staging, same day",
    "In staging, later",
    "When I went to plant it"
  ],

  states: ["Sent", "Answered", "Replacement coming", "Landed"]
};

/* ── NOT READY TO PLANT (shape #2 — shared/note.js) ─────────────────────────
 * The bed note, and the twin of painting's Not Ready and doors' Not Ready To
 * Hang. The asymmetry that makes it necessary: a plant that goes into ground
 * that was not ready dies on HIS warranty, and he is the one digging it out
 * in July. Each stop carries the ASK under it, so the note reads as a list a
 * super can clear by lunch rather than a complaint.
 */
window.TOOLKIT_ITEMS.notready = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Owner's rep / construction manager",
    "Builder / site super",
    "Property / facility manager",
    "Landscape architect",
    "Another trade's foreman"
  ],

  stops: [
    {
      name: "Grade's been driven on — it's compacted and rutted",
      sub: "A rootball in that reads as my plant dying in July. Rip it and re-grade, or direct me in writing to plant it as it sits."
    },
    {
      name: "Rock, trash and busted block in the beds",
      sub: "Base rock, mortar, broken block and wire in the top foot. Whoever left it picks it, or tell me in writing it's mine and it's a change."
    },
    {
      name: "No topsoil — the import isn't here",
      sub: "What's there is subgrade. Tell me the day the soil lands, or say the word and we plant into what's there — in writing."
    },
    {
      name: "Grade's not to the plan — it won't drain, or it's high against the walk",
      sub: "What my level read is in the note beside the number I read off the plan. Whoever graded it fixes it, or direct me to plant to it and it becomes a tag."
    },
    {
      name: "No water on site — the POC isn't live",
      sub: "Nothing I put in the ground lives without it. Tell me the day the meter's set and the main's charged, or tell me who's watering by hand and who's paying for that."
    },
    {
      name: "Nothing at the clock — no power, no conduit",
      sub: "I can charge it and run it by hand, but nobody's watering nights. Tell me who's landing the circuit and when."
    },
    {
      name: "My sleeves never went in — the flatwork's poured",
      sub: "I sent the crossing list before forms. It's a bore or a saw cut now — say who owns that before I re-route."
    },
    {
      name: "Trades still parked and staged in my beds",
      sub: "A bed with a conex on it isn't a bed. Tell me the day it's actually mine, and keep the trucks off it after that."
    },
    {
      name: "Hardscape's not done — I can't grade to it",
      sub: "The curb, the walk or the wall my grade has to meet isn't there. Tell me the day, not the week."
    },
    {
      name: "Trees that were flagged to stay got hit",
      sub: "Roots cut, bark off, fill piled on the trunk. That's not mine and it's on the record today — somebody who can make that call needs to look at it."
    },
    {
      name: "Nobody's answered the substitution",
      sub: "The plant I can't get is holding the whole bed. Approve one or tell me to wait — in writing, with a date."
    },
    {
      name: "Wrong season — too hot, too cold or too wet to put this in",
      sub: "I'll plant it if you direct me to, in writing, and we both know what that means for what lives. Or give me the date and I'll hold the stock."
    }
  ],

  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};

/* ── SUB IT OR WAIT (shape #2 — shared/note.js) ─────────────────────────────
 * The substitution ASK, and the page that answers THEIR numbered schedule the
 * way painting's Color Lock answers the finish schedule: their line rides as
 * an address, what the grower said rides in the grower's words, what he CAN
 * get rides as he would order it, and the page makes no plant call.
 */
window.TOOLKIT_ITEMS.subs = {
  roles: [
    "Landscape architect / designer",
    "GC superintendent",
    "GC project manager",
    "Owner's rep",
    "Builder / site super",
    "Our own boss / PM"
  ],

  /* WHAT THE GROWER SAID — things a yard actually says on the phone. */
  said: [
    "Sold out through the season",
    "Only in a smaller size",
    "Only in a bigger size",
    "Available — weeks out",
    "Not grown in this region",
    "Nobody carries it under that name",
    "Have it, but it's rough"
  ],

  /* WHAT WAITING MOVES — the sequence consequence, in the words the super
     hears it in. */
  moves: [
    "The whole bed waits",
    "The tree row waits",
    "The rest goes in now, this comes later — a second trip",
    "The sod waits on the beds",
    "The walk waits on the trees",
    "Nothing moves — it's the last thing in"
  ],

  pics: ["Sent with photos of what I can get", "Photos on request", "Come look at the yard with me"]
};

/* ── WATER'S YOURS (shape #2 — shared/note.js) ──────────────────────────────
 * THE HANDBACK. The day the system is in and running the water becomes
 * somebody else's, and everything he planted lives or dies on what they do
 * with it. The page records what HE set the clock to in HIS words, copied off
 * the face — it recommends nothing — and hands the water, the backflow test
 * and the restriction calendar back to the people who own them. The code goes
 * by phone, never on the note.
 */
window.TOOLKIT_ITEMS.handover = {
  roles: [
    "Owner's rep",
    "Property manager",
    "GC superintendent",
    "Maintenance contractor",
    "Builder / homeowner's rep",
    "Our own boss / PM"
  ],

  running: [
    "Everything's in and running",
    "Running — some zones still off",
    "Charged — not programmed yet",
    "Not charged — no water yet",
    "Not charged — no power at the clock"
  ],

  asks: [
    { name: "Nobody kills the water without telling me", sub: "a valve shut at the backflow for a week in August is every plant on this job" },
    { name: "Nobody changes the clock without telling me", sub: "if it needs to change, call me and I'll change it — that's what the warranty rides on" },
    { name: "Tell me the day it goes off for a freeze or a restriction", sub: "before, not after" },
    { name: "Who waters the days we're not here", sub: "a name and a number, not 'the guys'" },
    { name: "Trucks and trades off the beds and the new sod", sub: "finish grade doesn't survive a lift or a pallet jack" },
    { name: "Call me before anyone mows the new sod", sub: "the first cut is ours — after that it's yours" },
    { name: "Who I call when a head's spraying the wall at six in the morning", sub: "a two-minute fix if I hear about it Monday, a stained wall if I hear about it in March" },
    { name: "The date the maintenance clock starts", sub: "off your contract, in your words — I'm not restating the term" },
    { name: "Who's got the backflow test and when it's due", sub: "the tester files it with the water purveyor — yours to schedule, not mine to certify" }
  ],

  pics: ["Sent with photos of the clock face", "Photos on request", "Walk it with me"]
};

/* ── BEFORE WE PLANT (the rough-in-request engine) ──────────────────────────
 * ONE MESSAGE PER OUTFIT, sent a week out, at the gate each outfit is already
 * counting down to. This is where the INTERFACE lives: concrete/items.js
 * ships "Irrigation / landscape" as a receiver, sitework/items.js ships
 * "Landscape / irrigation" AND "Irrigation" as what is in the ditch, gc ships
 * "Landscaping / hardscape" — three chips built for a man who, until this
 * page existed, had nowhere to answer from. The rows below are that answer.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before We Plant",
  eyebrow: "Landscape · you → everybody who owes you something",
  lede: "Everything in your beds is somebody else's work until a plant goes in it — after that it's yours, and it dies on your warranty. This is what has to be in, out, graded, charged, cleared and decided before the truck comes: who owes it, where, and the gate it has to beat. Walk the job once, tap the rows, send one message per outfit — a week out, while every line is still a conversation. The refusal is Not Ready To Plant; this page is how you never send it.",
  docSubject: "Before we plant — what I need out of your outfit",
  docSubjectWith: "Before we plant — what I need from {to}",
  closing: "That's my list before anything goes in the ground out there. If a line's wrong, or there's something in those beds you know that I don't, hit me back today — every one of these is a five-minute answer this week and a lost day the week my plants are on the truck. And the part nobody says out loud: a plant that goes into ground that wasn't ready dies on my warranty, and I'm the one digging it out in July explaining it. That's why I'm asking now.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set and <i>your</i> own approved submittals. This page sets no sleeve size, no cover depth, no pipe or wire size, no grade or slope number, no soil spec, no rate of anything and no plant call &mdash; your plans, your submittal and whoever stamps them own all of that. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and its revision is the whole argument. Name the L-sheet or the civil you took this off and the super works your list against his own set; leave it off and it's one landscaper's opinion until he re-walks it with you — the morning you were supposed to be planting.",
  phJob: "Willow Creek — Phase 2, Building C",
  phOff: "L-201 rev 2, C-301 rev 3",
  phFrom: "Ray T — Sierra Landscape & Irrigation",
  phArea: "west beds along the walk, and the drive crossing",
  areaLabel: "Bed / area",

  who: [
    { v: "gc", label: "GC super" },
    { v: "dirt", label: "Sitework / grading" },
    { v: "conc", label: "Concrete / flatwork" },
    { v: "paving", label: "Paving / striping" },
    { v: "mason", label: "Masonry / hardscape" },
    { v: "plumb", label: "Plumber" },
    { v: "ec", label: "Electrician" },
    { v: "la", label: "Landscape architect / designer" },
    { v: "grow", label: "Nursery / grower" },
    { v: "owner", label: "Owner / property manager" }
  ],

  milestones: [
    { v: "forms", label: "Before you set forms" },
    { v: "pour", label: "Before the pour" },
    { v: "backfill", label: "Before you backfill" },
    { v: "pave", label: "Before you pave" },
    { v: "grade", label: "Before fine grade" },
    { v: "trench", label: "Before we trench" },
    { v: "charge", label: "Before we charge it" },
    { v: "plant", label: "Before the plants land" },
    { v: "handover", label: "Before we hand it over" }
  ],

  asks: [
    { v: "sleeves", label: "Sleeves under the flatwork before forms", who: "conc", by: "forms", specs: [
      "Walk it with me and I'll paint where they go",
      "Leave them sticking out past the form so I can find them",
      "Capped both ends so they don't fill with mud",
      "Tell me the day you're forming, not the week",
      "If one lands in your steel, call me today — I'll move it"
    ] },
    { v: "pave", label: "Walk my sleeves before the base rolls", who: "paving", by: "pave", specs: [
      "Stubs marked past the edge of the base",
      "Tell me the day the base goes down and the day you pave",
      "Finish elevation at the curb and the walk, so my grade meets yours without a lip",
      "Once it's paved it's a saw cut — and an argument"
    ] },
    { v: "trench", label: "My pipe's in your ditch — call me before it goes back", who: "dirt", by: "backfill", specs: [
      "Backfill around my mainline with what I left, not the rock you dug out",
      "Let me see it in before you cover it",
      "Don't run the compactor over the crossing",
      "Tell me the day, so I'm standing there"
    ] },
    { v: "grade", label: "Fine grade with the rock and trash picked", who: "dirt", by: "grade", specs: [
      "Rough grade to the plan, topsoil back where you stripped it",
      "Nothing compacted where a rootball goes",
      "Your spoil pile gone before I mobilize",
      "Pick the base rock, the block and the wire out of the top foot",
      "Tell me the number you graded to and which sheet it came off"
    ] },
    { v: "poc", label: "The POC live and the backflow where the plan puts it", who: "plumb", by: "charge", specs: [
      "The meter set and the main charged before I fill anything",
      "The backflow where the plan puts it, at the height your submittal says",
      "Tell me who's pulling the backflow permit and who's testing it — it isn't me",
      "A hose bib I can reach for a tank"
    ] },
    { v: "power", label: "Power at the clock", who: "ec", by: "charge", specs: [
      "120 at the controller, on a circuit that isn't on the lighting timer",
      "A spare conduit from the clock to the first valve box",
      "Your site-lighting runs staked before I trench",
      "Tell me which pull box is yours, so I don't put a shovel through it"
    ] },
    { v: "chase", label: "A sleeve through the wall and my drip past the footing", who: "mason", by: "grade", specs: [
      "A chase through the wall where I marked it, before the block goes up",
      "My stub past the footing so I'm not coring your wall",
      "Weep holes left open — I'm draining behind it",
      "Tell me the day the wall goes up"
    ] },
    { v: "clear", label: "The beds and the lot actually mine", who: "gc", by: "plant", specs: [
      "Staging, trailers and trade parking out of my beds — and off them after",
      "Water I can fill a tank off of",
      "A route for a truck and a trailer to the beds",
      "Tell me the day the ground's mine, not the week",
      "Nobody drives on finish grade after me"
    ] },
    { v: "protect", label: "What's flagged to stay, stays", who: "gc", by: "grade", specs: [
      "Fence around the trees that stay before the machines show up",
      "Tell me who owns it if one gets hit",
      "Anything staked, flagged or fenced — say what it is before I grade to it"
    ] },
    { v: "sub", label: "An answer on the substitution, in writing", who: "la", by: "plant", specs: [
      "Approve one of the ones I can get, under your own number",
      "Or tell me to wait, and what I plant in the meantime",
      "The current rev of the schedule before the truck rolls",
      "A date, not 'we'll get back to you'"
    ] },
    { v: "stock", label: "A real availability the week before", who: "grow", by: "plant", specs: [
      "Stock tagged to my order, not pulled from whoever's on the truck",
      "What's actually on the truck versus what ships next week",
      "A delivery day I can put a crew against",
      "Tell me before you sub a size, not on the slip"
    ] },
    { v: "water", label: "Who holds the water after I leave", who: "owner", by: "handover", specs: [
      "Who has the controller, and who I call when a head's on the wall at six",
      "Who waters the days we're not here",
      "The date the maintenance clock starts, off the contract",
      "Tell me before anyone changes the clock"
    ] },
    { v: "answers", label: "The answers nobody's given yet", who: "gc", by: "plant", specs: [
      "Whether the mulch is mine or the owner's",
      "Where the sod ends and the seed starts",
      "Which existing plants are staying",
      "Any bed where the field and the plan disagree"
    ] }
  ]
};

/* ── WALK BACK (the reconcile engine) ───────────────────────────────────────
 * Somebody walked it and sent a list. The fourth rung is this trade's, and it
 * is the one that keeps the page honest: on a landscape punch a dying plant is
 * very often the CLOCK talking — a zone that is off, a controller somebody
 * changed, a restriction nobody passed on — and that answer lives with
 * whoever holds the controller, not with the man holding a shovel.
 */
window.TOOLKIT_ANSWER = {
  toolName: "Walk Back",
  eyebrow: "Landscape · them → you → back",
  lede: "The LA, the super or the owner's rep walked it and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll hit it, with a day on it · Done already · Not mine · It's the water — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll hit it line carries a day — hold me to it, and they land together on one trip instead of four drive-bys. Done already lines are just that — walk them tonight. Not mine is another outfit's work, or damage that landed after I finished, and those sit dated in my own log, which comes to you separately. It's the water is the one worth reading twice: it means the plant is telling you about the clock, not the planting — a zone that's off, a controller somebody changed, a restriction nobody told me about — and that answer lives with whoever holds the controller. Send it that way and it comes back faster than if I replace a plant that'll die the same way.",
  answers: ["We'll hit it", "Done already", "Not mine", "It's the water"],
  phJob: "Willow Creek — Phase 2, Building C",
  phTo: "Dana K — GC super",
  phFrom: "Ray T — Sierra Landscape & Irrigation",
  phOff: "landscape walk 9/12",
  paste: "Willow Creek Phase 2 — landscape punch — Sep 12\n\nJob: Willow Creek — Phase 2, Building C\nFrom: Dana K — GC super\n\n31. west bed — 3 shrubs dead along the walk\n32. zone 4 — heads throwing on the glass at the lobby\n33. lawn — sod seams open by the drive\n34. east bed — mulch thin, fabric showing\n35. tree row — two leaning, stakes loose\n36. valve box by the entry — lid's cracked\n37. drive island — plants look wilted\n38. swale — rock washed out at the inlet"
};

/* ── GETTING IN (the access engine) ─────────────────────────────────────────
 * An occupied campus, and the one trade whose work is the building's own
 * front yard. Every process the building owns comes back as a question aimed
 * at its owner: the water, the backflow test, the locates behind the meter,
 * the alarm on the back gate and the word to the tenants are theirs, and this
 * page never pretends otherwise.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Landscape · you → whoever holds the gate",
  lede: "Working a campus, a complex or a store that's open all day. They hold the gate, the water, the alarm on the back door and the phone that rings when a tenant's car takes a rock through the glass. Send the ask that gets a real yes before the trailer's loaded: which gate and the hours, where the trailer, the soil pile and the plant sit for a fortnight, where the water is, when a trencher or a blower can run, and what happens at the backflow while we're on it. Every heads-up on it ends by handing the process back to the man who owns it — in his building, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    "One day",
    "A few days running",
    "A couple of weeks",
    "Nights / off-hours only",
    "Whatever you'll give me"
  ],

  need: [
    { name: "The gate open and somebody to meet us the first morning", sub: "walk us in once — gate, route, water, where the pile goes — and after that we're repeatable" },
    { name: "A route a truck and a trailer can make", sub: "a trencher on a trailer doesn't turn where a car turns, and we'll be in and out all day" },
    { name: "Somewhere the soil, the mulch and the plant can sit", sub: "a pile and a couple of pallets, out of the way, for as long as the job runs — and the plant needs water where it sits" },
    { name: "Water we can reach", sub: "a hose bib, a quick-coupler or a fill point — plant that sits dry for two days is plant we replace" },
    { name: "Tell us where the green waste and the spoil go", sub: "or we bring a bin — tell us where it can sit" },
    { name: "Tell us when we can run a trencher, a blower or a saw", sub: "and when we can't — we'll build the day around it" },
    { name: "The clock and the backflow — where they are and who has the key", sub: "we'll need the water off and on more than once" },
    { name: "Tell us which lawns and paths people actually walk across", sub: "an open trench across a path at eight in the morning is on us — we'll plate it or fence it if you tell us where" },
    { name: "Somewhere the crew can park that isn't a tenant's spot", sub: "four trucks, and we'd rather not be towed" }
  ],

  heads: [
    { name: "The water will be off at the backflow valve while we work", sub: "tell me who charges it back and who tests it — that's the building's and the purveyor's, not ours" },
    { name: "A trench is going through a lawn or a path people use", sub: "tell us where you want it fenced, plated or flagged, and who warns the tenants" },
    { name: "A mower or a trencher throws rock", sub: "tell us which cars, windows and doors you want us to keep away from, and the hours" },
    { name: "Blowers, a saw and a compactor — it's loud", sub: "say which hours you'll take it" },
    { name: "We'll be digging near your lines", sub: "tell us who locates the private lines behind the meter; the one-call ticket covers the street, not your lighting or your old feed" },
    { name: "Heads may spray a walk or a window while we test", sub: "tell us if there's a window you don't want wet, and when" },
    { name: "Trees flagged to stay — we're working around them", sub: "if there's a protected tree or a permit on it, tell us who's watching it; that's the city's call and yours" },
    { name: "Somebody has to water what we put in on the days we're not here", sub: "tell us who — or we'll leave a tank and a list of our own visits" },
    { name: "We'll be here after hours some days", sub: "tell us what the alarm does on the back gate and who we call if we trip it" }
  ],

  phSite: "Oakridge Corporate Center — buildings A and B",
  phRoom: "the front beds, the drive island and the east lawn",
  phHow: "service gate off Pell Road, then the fire lane behind B",
  phScope: "re-do the entry beds and the drive island — four of us, a trencher and a skid steer, two weeks",
  phLoud: "the trencher and the saw the first three mornings, after eight",
  phTo: "Mara S — property manager, Oakridge",
  phMe: "Ray T — 559-555-0173",
  phCo: "Sierra Landscape & Irrigation",

  /* THE THREE FIELDS THE ENGINE REQUIRES, and the reason they are called out
     here rather than left to a copy: `closing` is CONCATENATED by the page
     (`G.closing.concat([...])`), so omitting it is not a missing sentence — it
     is a TypeError on load and a blank page at every width. mobile-watertight
     caught exactly that on the doors copy before it shipped. */
  warn: "<b>It&rsquo;s an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it &mdash; the water, the backflow test, the locates behind the meter, the alarm and the word to the tenants are the building&rsquo;s to run and to number, and we never will.",

  closing: [
    "This is an ask, not a booking — nothing gets scheduled until you answer. Wrong days? Name the ones your building can live with and we'll take them.",
    "Saying yes: tell me the gate, the window you're actually giving us, who meets us the first morning, where the pile and the plant sit, and where the water is — and the one that matters most, who charges the backflow back and who tests it, because it isn't us. If the answer on the locates behind your meter is a person, give me their name before our first day, not during it."
  ]
};

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Everything here is something the man PICKS,
 * and every `notin` line is a fence that keeps a tag from being read as a claim.
 *
 * BACKPORTED 2026-09-05 (C3711). The census on disk said eleven of seventeen
 * trades carried the extra-work tag and this one did not — a trade with no tag
 * has no way to write the one document that gets it paid for directed work.
 * The engine and the nine-slot `notin` skeleton are the rack's; the words are
 * this trade's, and `why` is where the trade actually lives.
 *
 * THE FENCE THAT MATTERS MOST is in `why` and in `notin`: nothing here asserts
 * CAUSE. A tag that says who caused a condition is a tag doing the engineer's
 * job. He writes what he was told and what his crew did; who caused what is
 * somebody else's call. */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC superintendent",
    "Our own general super",
    "Another trade's foreman working in our beds",
    "GC project manager",
    "Our PM or the office",
    "Landscape architect on site",
    "Builder's field super (tract or custom home)",
    "Owner's rep or property manager",
    "Homeowner",
    "City or agency inspector on site"
  ],
  "how": [
    { "v": "Face to face in the field" },
    { "v": "Text message" },
    { "v": "Phone call" },
    { "v": "Told to me at the morning huddle" },
    { "v": "Radio on the site channel" },
    { "v": "Email" },
    { "v": "Marked-up planting plan handed to me in the field" },
    { "v": "Flags or paint moved on the ground" },
    { "v": "Note left at the trailer" },
    { "v": "Written direction from our own office" }
  ],
  "why": [
    { "name": "Grade wasn't what we planted to", "sub": "Finish grade high, low or still moving when we got there. Told to plant anyway, or told to fix it first." },
    { "name": "Soil wouldn't take the plant", "sub": "Rock, rubble, clay or fill in the pit. Hand dug, augered, hauled out or amended past what we bid." },
    { "name": "Standing while somebody got out of our beds", "sub": "Crew on site and the plants off the truck and drying, waiting on the beds to be ours to work." },
    { "name": "Plant substituted at the nursery or in the field", "sub": "Size, species or container changed off the approved list on somebody's say-so. Re-tagged, re-staged or re-planted." },
    { "name": "Told to plant out of season or out of sequence", "sub": "Ahead of the hardscape, ahead of the irrigation, or in heat or cold we'd have called off." },
    { "name": "Irrigation point of connection moved", "sub": "The tie-in, the meter, the backflow or the sleeve wasn't where the plan or the site showed. New route, new trench, new mainline." },
    { "name": "Sleeves missing or not where they were shown", "sub": "Told to bore, saw-cut or route around hardscape that went in without our sleeves." },
    { "name": "Line in the ground nobody marked", "sub": "The trencher or the plow walked into it. Stopped, hand dug the mainline around it, and lost the day waiting on a locate." },
    { "name": "Told to water before it was ours to water", "sub": "Hand watering, hoses or a temporary line kept running on somebody's direction, before the start date we agreed to." },
    { "name": "Plant damaged after we set it", "sub": "Set, staked and watered, then run over, snapped, buried or driven around before we ever handed it off." },
    { "name": "Told to pull and replace what we already planted", "sub": "The direction, the count and the day we pulled them. No call from us on why they came out — that is somebody else's." },
    { "name": "Told to work the weather", "sub": "Keep planting, keep watering, cover it, or come back on a day we'd called off." },
    { "name": "Beds or edges changed after we laid them out", "sub": "Lines, radii or square footage moved after we set to the first ones." },
    { "name": "Told to keep it up while the job sat", "sub": "Mowing, weeding, re-mulching, blowing off the hardscape and cleaning up for owner walks, week after week, before the day it becomes theirs." },
    { "name": "Cleanup or re-grade behind somebody else", "sub": "Tracking, spoil, washout or stacked material left in our beds that we got told to deal with." }
  ],
  "notin": [
    { "name": "Not a price", "sub": "Hours, counts and conditions only. No rate, no total, no dollar figure anywhere on it." },
    { "name": "Not a change order and not a claim", "sub": "This says we were directed and what it took. It becomes a change when the offices paper it, and entitlement is their letter, not the foreman's." },
    { "name": "Not a question for the landscape architect, and not a design change", "sub": "Anything about the plan — species, size, spacing, the irrigation design — goes up through the GC on their form. Nothing here approves a substitution." },
    { "name": "Not the nursery tag or the delivery ticket", "sub": "We attach them by the numbers already printed on them. We never retype what's on them." },
    { "name": "Not the warranty start, and not a release", "sub": "The day it becomes theirs and who is watering from it are set where they were agreed. A tag doesn't move that date." },
    { "name": "Not the inspector's report", "sub": "He writes his own. We write what our crew was told and what our crew did." },
    { "name": "Not the GC's daily", "sub": "They keep theirs and number it. This is ours and it stands on its own." },
    { "name": "Not a finding of cause", "sub": "We write what we found and what we planted. Who caused what is a call other people make." },
    { "name": "Not a safety or incident report", "sub": "Injuries, near misses and equipment go on their own paper, right then, through the proper channel." },
    { "name": "Not turnover or acceptance", "sub": "Signing that you were told isn't accepting the work, releasing anybody, or agreeing it's done." }
  ],
  "classes": [
    "— class",
    "FOREMAN",
    "IRRIGATION TECH",
    "LABORER",
    "EQUIPMENT OPERATOR",
    "TREE CLIMBER"
  ],
  "pics": [
    { "v": "In this message — shot before we mulched it in" },
    { "v": "None" }
  ]
};

/* ── TAG_ES — the directed-work tag's vocabulary en español. ──────────────
 * Every entry carries its own en-twin — nothing paired by index, nothing that can
 * drift apart. The page composes what the document prints ("ES (EN)") from the
 * pair; a <select> value carries its twin itself, house style "MAYORDOMO (FOREMAN)".
 * Gated: tools/toolkit-gates/lang-layer.mjs asserts every twin matches an EN
 * option verbatim, on every page that mounts shared/lang.js. */
window.TOOLKIT_ITEMS.tag_es = {
  "classes": [
    { "es": "— clase", "en": "— class" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" },
    { "es": "TÉCNICO DE RIEGO (IRRIGATION TECH)", "en": "IRRIGATION TECH" },
    { "es": "PEÓN (LABORER)", "en": "LABORER" },
    { "es": "OPERADOR DE EQUIPO (EQUIPMENT OPERATOR)", "en": "EQUIPMENT OPERATOR" },
    { "es": "PODADOR / TREPADOR (TREE CLIMBER)", "en": "TREE CLIMBER" }
  ],
  "how": [
    { "es": "En persona, en el campo", "en": "Face to face in the field" },
    { "es": "Mensaje de texto", "en": "Text message" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me lo dijo en la junta de la mañana", "en": "Told to me at the morning huddle" },
    { "es": "Radio, en el canal de la obra", "en": "Radio on the site channel" },
    { "es": "Correo", "en": "Email" },
    { "es": "Plano de plantación marcado que me entregó en campo", "en": "Marked-up planting plan handed to me in the field" },
    { "es": "Banderas o pintura movidas en el terreno", "en": "Flags or paint moved on the ground" },
    { "es": "Nota dejada en el tráiler", "en": "Note left at the trailer" },
    { "es": "Orden por escrito de nuestra propia oficina", "en": "Written direction from our own office" }
  ],
  "notin": [
    { "es": "No es un precio", "sub": "Solo horas, cantidades y condiciones. Sin tarifa, sin total, sin ninguna cifra en dólares.", "en": "Not a price" },
    { "es": "No es un CO ni un reclamo", "sub": "Esto dice que nos ordenaron y qué tomó. Se vuelve cambio cuando las oficinas lo documentan, y el derecho a cobrarlo lo pone la carta de la oficina, no el mayordomo.", "en": "Not a change order and not a claim" },
    { "es": "No es pregunta para el arquitecto de paisaje, ni cambio de diseño", "sub": "Todo lo del plano — especie, tamaño, separación, el diseño del riego — sube por el GC en su formato. Nada de aquí aprueba una sustitución.", "en": "Not a question for the landscape architect, and not a design change" },
    { "es": "No es la etiqueta del vivero ni el ticket de entrega", "sub": "Los anexamos por los números que ya traen impresos. Nunca volvemos a escribir lo que dicen.", "en": "Not the nursery tag or the delivery ticket" },
    { "es": "No es el arranque de la garantía, ni una liberación", "sub": "El día en que pasa a ser de ellos y quién riega a partir de ahí se fijan donde se acordaron. Un vale no mueve esa fecha.", "en": "Not the warranty start, and not a release" },
    { "es": "No es el reporte del inspector", "sub": "Él escribe el suyo. Nosotros escribimos qué le ordenaron a nuestra cuadrilla y qué hizo nuestra cuadrilla.", "en": "Not the inspector's report" },
    { "es": "No es el reporte diario del GC", "sub": "Ellos llevan el suyo y le ponen número. Este es el nuestro y se sostiene solo.", "en": "Not the GC's daily" },
    { "es": "No dice quién tuvo la culpa", "sub": "Escribimos lo que encontramos y lo que plantamos. Quién causó qué es decisión de otros.", "en": "Not a finding of cause" },
    { "es": "No es reporte de seguridad ni de incidente", "sub": "Lesiones, casi-accidentes y equipo van en su propio papel, en el momento, por el canal que corresponde.", "en": "Not a safety or incident report" },
    { "es": "No es entrega ni aceptación", "sub": "Firmar que se lo ordenaron no es aceptar el trabajo, liberar a nadie, ni decir que ya quedó.", "en": "Not turnover or acceptance" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas antes de taparlo con mulch", "en": "In this message — shot before we mulched it in" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "El súper del GC", "en": "GC superintendent" },
    { "es": "Nuestro propio súper general", "en": "Our own general super" },
    { "es": "El mayordomo de otro oficio trabajando en nuestras camas", "en": "Another trade's foreman working in our beds" },
    { "es": "El PM del GC", "en": "GC project manager" },
    { "es": "Nuestro PM o la oficina", "en": "Our PM or the office" },
    { "es": "El arquitecto de paisaje en la obra", "en": "Landscape architect on site" },
    { "es": "El súper de campo del constructor (fraccionamiento o casa a la medida)", "en": "Builder's field super (tract or custom home)" },
    { "es": "El representante del dueño o el administrador de la propiedad", "en": "Owner's rep or property manager" },
    { "es": "El dueño de la casa", "en": "Homeowner" },
    { "es": "El inspector de la ciudad o de la agencia en la obra", "en": "City or agency inspector on site" }
  ],
  "why": [
    { "es": "El nivel no era el que nos dieron para plantar", "sub": "El nivel de acabado alto, bajo o todavía moviéndose cuando llegamos. Nos dijeron que plantáramos de todos modos, o que primero lo arregláramos.", "en": "Grade wasn't what we planted to" },
    { "es": "El suelo no aceptaba la planta", "sub": "Roca, escombro, barro o relleno en la cepa. Excavado a mano, con barrena, sacado o mejorado más allá de lo que cotizamos.", "en": "Soil wouldn't take the plant" },
    { "es": "Parados mientras alguien se salía de nuestras camas", "sub": "Cuadrilla en la obra y las plantas ya bajadas y secándose, esperando a que las camas fueran nuestras para trabajar.", "en": "Standing while somebody got out of our beds" },
    { "es": "Planta sustituida en el vivero o en campo", "sub": "El tamaño, la especie o el contenedor cambiaron respecto a la lista aprobada porque alguien lo dijo. Se volvió a etiquetar, a acomodar o a plantar.", "en": "Plant substituted at the nursery or in the field" },
    { "es": "Nos dijeron que plantáramos fuera de temporada o de secuencia", "sub": "Antes del hardscape, antes del riego, o con un calor o un frío que nosotros habríamos cancelado.", "en": "Told to plant out of season or out of sequence" },
    { "es": "El punto de conexión del riego se movió", "sub": "La conexión, el medidor, el backflow o el sleeve no estaban donde el plano o el sitio mostraban. Ruta nueva, zanja nueva, línea principal nueva.", "en": "Irrigation point of connection moved" },
    { "es": "Faltan sleeves o no están donde los marcaron", "sub": "Nos dijeron que barrenáramos, cortáramos con sierra o le diéramos la vuelta a hardscape que se puso sin nuestros sleeves.", "en": "Sleeves missing or not where they were shown" },
    { "es": "Línea en el terreno que nadie marcó", "sub": "La zanjadora o el arado le pegaron. Paramos, excavamos la línea principal a mano por un lado, y perdimos el día esperando el locate.", "en": "Line in the ground nobody marked" },
    { "es": "Nos dijeron que regáramos antes de que nos tocara", "sub": "Riego a mano, mangueras o una línea temporal que seguimos corriendo por orden de alguien, antes de la fecha de arranque que acordamos.", "en": "Told to water before it was ours to water" },
    { "es": "Planta dañada después de que la pusimos", "sub": "Puesta, estacada y regada, y luego la pisaron, la quebraron, la enterraron o le pasaron por encima antes de que la entregáramos.", "en": "Plant damaged after we set it" },
    { "es": "Nos dijeron que quitáramos y repusiéramos lo que ya habíamos plantado", "sub": "La orden, la cantidad y el día que las sacamos. Nosotros no decimos por qué salieron — eso le toca a otro.", "en": "Told to pull and replace what we already planted" },
    { "es": "Nos dijeron que le entráramos con el clima", "sub": "Seguirle plantando, seguirle regando, taparlo, o regresar un día que ya habíamos cancelado.", "en": "Told to work the weather" },
    { "es": "Camas o bordes cambiados después de que los trazamos", "sub": "Líneas, radios o metros cuadrados se movieron después de que ya habíamos trazado con los primeros.", "en": "Beds or edges changed after we laid them out" },
    { "es": "Nos dijeron que lo mantuviéramos mientras la obra estaba parada", "sub": "Cortar, deshierbar, reponer mulch, soplar el hardscape y limpiar para los recorridos del dueño, semana tras semana, antes del día en que pasa a ser de ellos.", "en": "Told to keep it up while the job sat" },
    { "es": "Limpieza o volver a nivelar detrás de alguien más", "sub": "Huellas, escombro, arrastre o material estibado que dejaron en nuestras camas y nos dijeron que lo resolviéramos.", "en": "Cleanup or re-grade behind somebody else" }
  ]
};
