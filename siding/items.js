/* SIDING & EXTERIORS FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary the ladder set at trade #2 and this file keeps: trade.js is
 * IDENTITY AND COPY, tools.js is the REGISTRY, and this file is the trade's
 * WORDS — what he picks from, in the order he'd say them. Nothing here is a
 * spec, a dimension, a clearance, a fastener or a rating, because trade.js
 * refuses all of those and a picker is where a refusal quietly dies if nobody
 * is watching it.
 *
 * EVERY LIST BELOW WAS WRITTEN AGAINST ONE QUESTION, which the doctrine lens
 * put on the record at the panel: CAN ROOFING ALREADY WRITE THIS? Where the
 * answer was yes, the line was cut. That is why nothing here names drip edge,
 * step or counter flashing, ice-and-water, the roof-to-wall detail or a shingle
 * course: roofing/ ships pages for all of it. This kit stops at the wall.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── THROUGH MY WALL (shape #3 — shared/rowlog.js) ──────────────────────────
 * THE PINNED TOOL, and the page that answers the panel's own objection.
 * Twelve shipped kits count down to a wall closing — "Before rock goes up",
 * "Before the wall closes", "Before second side goes on", "Before we close one
 * side" — and every one of them means the INSIDE face, because the inside face
 * is where the rock hangs and the inspector looks. The OUTSIDE face closes
 * too. It closes once. And every hole anybody needs through it after that is a
 * cut, a patch and a caulk joint the owner can see from the driveway.
 *
 * So: one row per penetration somebody else needs through his wall before he
 * closes it. Whose it is, what it is, which elevation and a corner you can
 * point at, whether it is marked, through, or through AND flashed, and the
 * gate it has to beat. Sent to the super and to every outfit on it, elevation
 * by elevation, while it is still a drill and not a saw.
 *
 * WHAT IT NEVER CARRIES, and the refusal list is why: no hole size, no
 * spacing, no clearance to anything, no flashing detail of ours, no sealant
 * call and no verdict that a penetration is or is not weathertight. The row
 * says what he was told, what he saw with his own eyes, and what he needs
 * decided. Flashed or not flashed is an OBSERVATION with a photo behind it,
 * never an assessment.
 */
window.TOOLKIT_ITEMS.wall = {
  /* WHOSE IT IS. These are the outfits that actually come back wanting a hole,
     in roughly the order they show up. "Don't know whose" is not filler — it
     is the most useful row on a re-side, where a stub sticking out of the
     sheathing belongs to somebody who left in 1994. */
  whose: [
    "HVAC / mechanical",
    "Electrician",
    "Plumber",
    "Low-voltage / alarm / camera",
    "Gas / propane",
    "Roofer",
    "Solar",
    "Owner / homeowner",
    "GC / super",
    "Ours — our own work",
    "Don't know whose"
  ],

  /* WHAT IT IS, named the way it gets named standing at the wall with a hole
     saw in your hand. The receiver reading "line set" knows exactly which
     elevation and exactly how annoyed to be. */
  whats: [
    "Dryer / bath / range vent",
    "HVAC line set",
    "Fresh-air or combustion intake",
    "Flue / vent termination",
    "Condensate line",
    "Hose bib",
    "Meter, service or mast",
    "Receptacle / GFCI",
    "Light block or fixture",
    "Camera / doorbell / keypad",
    "Panel, disconnect or box",
    "Gas line / regulator",
    "Louvre or wall vent",
    "Anchor, ledger or attachment",
    "Sign, address or house numbers",
    "An old one being abandoned",
    "Something else — I'll type it"
  ],

  /* WHERE, and it is the half people leave off. An elevation on its own is a
     quarter of a house; an elevation plus something that will still be there
     in March is an address. */
  faces: [
    "Front",
    "Left",
    "Right",
    "Rear",
    "Gable end",
    "Dormer",
    "Porch / entry",
    "Garage",
    "Under the eave / soffit",
    "The whole elevation"
  ],

  /* WHAT HE FOUND, and every one of these is something he SAW. There is no
     "correct" and no "compliant" in this list on purpose: "in and flashed" is
     "there is flashing on it and here is the photograph", never a verdict that
     the flashing is right, which is refusal 4 and is somebody else's call. */
  states: [
    "Marked only — nothing through yet",
    "Through, nothing on it yet",
    "Through, and there's flashing on it",
    "Not coming — they say they don't need it",
    "Already closed over — found it after"
  ],

  /* WHAT HE NEEDS DECIDED. Every one hands the decision to the outfit that
     owns the hole or to the man who runs the job; none of them is his. "Tell
     me in writing it isn't coming" is the one that saves him in March. */
  asks: [
    "Get it through before I close this elevation",
    "Put the flashing on it before I close",
    "Tell me where you want it — I'll block behind it now",
    "Tell me in writing it isn't coming and I'll close",
    "Come look at it with me",
    "It's in and I'm closing over it — no action"
  ],

  /* THE GATE. Not a date — the thing that happens after which it stops being a
     drill. Written as the crew says it, because a date slips and a gate does
     not: nobody argues about when "the corners went on". */
  gates: [
    "Before we wrap it",
    "Before I close this elevation",
    "Before the corners and bands go on",
    "Before the soffit closes",
    "Before the gutter goes up",
    "Before the staging comes down",
    "Before paint"
  ],

  sent: ["Sent", "Answered", "Done — I saw it in"]
};

/* ── WALL'S NOT READY (shape #2 — shared/note.js) ───────────────────────────
 * The refusal. Every trade on this rack has one and they are all the same
 * widget; the trade lives in the STOPS, and this one has two that no sibling
 * has. The first is the tear-off: he is the only man on the rack whose job
 * routinely starts by removing the outside of a building and finding out what
 * is behind it. The second is the year the house was built, and it is handled
 * the way trade.js refusal 6 demands — he never says what a surface is, only
 * what the OWNER told him and that the testing and the certified firm are
 * somebody else's to hold.
 */
window.TOOLKIT_ITEMS.notready = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Owner / homeowner",
    "Owner's rep / construction manager",
    "Architect / designer",
    "Another trade's foreman"
  ],

  stops: [
    {
      name: "No weather barrier on it, or it's torn and nobody's fixed it",
      sub: "I'm not hanging a wall over that and owning what happens behind it. Tell me who's wrapping it and the day it's done, or direct me in writing to side over it as it sits."
    },
    {
      name: "Windows are in and nobody's flashed them",
      sub: "Once my trim and my J go on, that's a tear-out to get back to it. Tell me who's flashing them and when — or tell me in writing to close around them the way they are."
    },
    {
      name: "Sheathing's not on, not fastened off, or there are gaps",
      sub: "What's under it telegraphs through it — I can't hang a flat wall on a wall that isn't. Tell me who's closing it out and the day."
    },
    {
      name: "No nailers or blocking where the trim lands",
      sub: "Corners, bands, the frieze, the fascia, a light block — every one of them needs something behind it. Tell me who's putting it in, or I'm nailing to air and we both know how that ends."
    },
    {
      name: "Took the old wall off and there's rot behind it",
      sub: "Here's where it is, how big it is off my tape, and what it looked like — photographed. What caused it and what it needs is not my call. Tell me who's looking at it and whether I'm stopped on that elevation."
    },
    {
      name: "The rough-ins aren't through the wall yet",
      sub: "Every one that comes after I close is a cut in a finished wall and a joint you can see from the driveway. My list is in the message. Tell me the day the last one's through."
    },
    {
      name: "There's no room at the bottom — the grade or the slab is at the sheathing",
      sub: "I'm not starting a wall where I've got nowhere to start it. That's a decision above my pay grade about the grade or the flashing — tell me who's making it."
    },
    {
      name: "The roof isn't dried in above me",
      sub: "Water coming down the wall while I close it is water inside the wall afterwards. Tell me the day the roof's on and I'll put my crew where it's dry until then."
    },
    {
      name: "Nobody's decided the colour, the profile or the trim package",
      sub: "I can't order coil, cut trim or start a corner without it, and a change after I've started is a re-order and a re-start. Tell me who decides and when — in writing, with the selection on it."
    },
    {
      name: "The set I've got isn't current, or there are no elevations",
      sub: "I'm not laying a wall out off a sheet somebody's already changed. Send the rev I'm building to and a name who answers when the elevation doesn't match the house."
    },
    {
      name: "The house is old and nobody's said who's testing before we cut",
      sub: "The owner tells me the house is from <year>. I'm not the man who says what's on that wall or whether it's fine to cut, sand or pull — that's a test and a certified outfit, and neither is mine. Tell me who holds it and I'll stand my crew down until you do."
    },
    {
      name: "I can't get a jack or a lift to the wall",
      sub: "Soft ground, a slope, cars, a deck, somebody's material stacked on my elevation. Tell me who's clearing it and the day, because a wall I can't stand at is a wall I can't hang."
    },
    {
      name: "Somebody else's staging or material is on my elevation",
      sub: "Tell me whose and when it moves. I'll work another face in the meantime and I'll tell you which one, so nobody's waiting on the wrong answer."
    },
    {
      name: "No power on site for the saw and the shear",
      sub: "Tell me who's getting a temp panel or a generator on it and by when — I can bring a machine, but not for free and not by surprise."
    },
    {
      name: "Weather — my call, my words",
      sub: "I'm not hanging a wall today, and here's what I saw. No threshold of mine is on this note; I'm telling you now so the schedule moves with a day's notice instead of at seven tomorrow."
    }
  ],

  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};

/* ── BEFORE I CLOSE IT (the cross-boundary ASK) ─────────────────────────────
 * The ask half of the loop the deploy asserts as a pair. He is between dry-in
 * and paint on the outside of a building, and everybody who owes him something
 * owes it in a window that shuts once.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before I Close It",
  eyebrow: "Siding · you → everybody who owes you something",
  lede: "The outside of the building closes once. After the wrap, the corners and the courses go on, every hole anybody still needs is a cut in a finished wall, a patch and a caulk joint the owner can see from the driveway — and the man who gets blamed for it is the one who closed it. This is what has to be through, flashed, blocked, decided and off your elevation before you start hanging: who owes it, where on the house, and the gate it has to beat. Walk it once a week out, tap the rows, send one message per outfit. The refusal is Wall's Not Ready; this page is how you never send it.",
  docSubject: "Before I close it — what I need out of your outfit",
  docSubjectWith: "Before I close it — what I need from {to}",
  closing: "That's my list before I start closing that elevation. If a line's wrong, or there's something you need through my wall that isn't on it, hit me back today — every one of these is a ten-minute answer this week and a hole saw through finished siding next month. And the part nobody says out loud: once it's closed, whatever went in after me looks like my work from the street. That's why I'm asking now instead of after.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> own walk and <i>your</i> own contract. This page sets no fastener, no spacing, no gap, no clearance to grade, to a roof or to a deck, and no exposure &mdash; the printed installation instructions you were handed own all of that, and on most of what you hang the warranty is written against them by name. It sizes no gutter and no downspout. It states no flashing detail and no sealant. It never says a wall, a penetration or an elevation is weathertight, correct or complete. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The elevation sheet and its revision is half the argument. Name the set you took this off and the super can work your list against his own; leave it off and it's one siding lead's opinion until somebody re-walks the house with you — the morning the crew was supposed to be hanging.",
  phJob: "412 Marchmont — full re-side",
  phOff: "A-201 rev 3, A-401 rev 2",
  phFrom: "Dale W — Rivet Exteriors",
  phArea: "the rear elevation and the two gables",
  areaLabel: "Elevation / area",
  areaHint: "Type the elevation the way the crew says it and it becomes a button for the rest of the walk.",
  specLabel: "What exactly",
  phSpec: "or type your own",
  specHint: "Pick what you need above and the usual lines show up here — yours, off your own walk, never a spec of ours.",
  placeLabel: "Where on the elevation",
  phPlace: "left of the rear door, under the deck · or: the whole gable",
  phNote: "anything that won't fit above — whose stub it is, who else is on that wall, what's already closed",
  phTel: "the number they answer from the job",
  docBoundary: "check them against your own set before you start hanging.",

  who: [
    { v: "gc", label: "GC super" },
    { v: "mech", label: "HVAC / mechanical" },
    { v: "ec", label: "Electrician" },
    { v: "plumb", label: "Plumber" },
    { v: "lv", label: "Low-voltage / alarm" },
    { v: "gas", label: "Gas / propane" },
    { v: "roof", label: "Roofer" },
    { v: "window", label: "Window supplier / glazier" },
    { v: "framer", label: "Framer / carpenter" },
    { v: "paint", label: "Painter" },
    { v: "owner", label: "Owner / homeowner" }
  ],

  milestones: [
    { v: "wrap", label: "Before we wrap it" },
    { v: "close", label: "Before I close the elevation" },
    { v: "corners", label: "Before the corners go on" },
    { v: "soffit", label: "Before the soffit closes" },
    { v: "gutter", label: "Before the gutter goes up" },
    { v: "staging", label: "Before the staging comes down" },
    { v: "paint", label: "Before paint" }
  ],

  asks: [
    { v: "rough", label: "Everything through my wall before I close it", who: "gc", by: "close", specs: [
      "Every vent, line set, hose bib, box and stub through the sheathing before I start hanging that elevation",
      "Whatever isn't coming, tell me in writing and I'll close over it",
      "A name per outfit I can text directly, so I'm not routing four holes through you",
      "Walk the elevation with me once before I start — ten minutes now, a saw cut later"
    ] },
    { v: "lineset", label: "Line sets, vents and terminations", who: "mech", by: "close", specs: [
      "Line sets, condensate and every termination through the wall before I close that elevation",
      "Tell me where you want it and I'll block behind it while the wall's open",
      "If it's changing location, tell me before the wrap goes on, not after the corners",
      "Say clearly which of us is putting the flashing on it — I'd rather it be settled than assumed"
    ] },
    { v: "elec", label: "Boxes, blocks, the meter and the service", who: "ec", by: "close", specs: [
      "Every receptacle, fixture box and disconnect through and located before I close",
      "Tell me where the light blocks go and I'll put backing in for them now",
      "The meter, the mast and the service: tell me who's pulling it off the wall, when, and who puts it back",
      "Anything you're abandoning, pull it and tell me — I'm not siding around a dead stub"
    ] },
    { v: "hosebib", label: "Hose bibs, stubs and anything abandoned", who: "plumb", by: "close", specs: [
      "Hose bibs and any wall penetration through before I start that face",
      "Old stubs from the last life of this house: pulled and capped, or tell me they're staying",
      "Tell me before the corners go on if a bib is moving"
    ] },
    { v: "cams", label: "Cameras, doorbell, keypad and the wire", who: "lv", by: "close", specs: [
      "Every camera, doorbell and keypad location marked before I close, and the wire through",
      "Tell me where you want backing and I'll put it in while the wall's open",
      "If the owner hasn't picked locations yet, tell me who's chasing that — I'm not guessing on a finished wall"
    ] },
    { v: "gasline", label: "The gas line, the regulator and the meter", who: "gas", by: "close", specs: [
      "The line, the regulator and the meter set and located before I close that elevation",
      "Tell me who's moving it if it's moving, and the day",
      "Whatever clearance you need around it is yours to state — tell me and I'll trim to it"
    ] },
    { v: "dryin", label: "Dried in above me before I start", who: "roof", by: "wrap", specs: [
      "The roof on and dried in above the elevation before I close it underneath",
      "Tell me the day you're off the wall so my staging isn't fighting yours",
      "Where your work lands on my wall, walk it with me once — I'd rather sort the order than the blame"
    ] },
    { v: "windows", label: "Windows in, and flashed", who: "window", by: "wrap", specs: [
      "Units set, fastened and flashed before I bring trim to them",
      "Any unit that's back-ordered: tell me now so I frame the opening and skip it, instead of finding out at the corner",
      "Tell me who's warranting the install so I know whose walk it is when water shows up"
    ] },
    { v: "backing", label: "Nailers, blocking and a flat wall", who: "framer", by: "wrap", specs: [
      "Backing where the corners, the bands, the frieze and the fascia land",
      "Sheathing on and fastened off, and tell me about anything you know is out of plane before I find it",
      "Blocking for a light, a camera, an address block or anything the owner's hanging on my wall later"
    ] },
    { v: "colour", label: "The colour, the profile and the trim package", who: "owner", by: "wrap", specs: [
      "The selection in writing before I order coil and cut trim",
      "Tell me who signs off on it, because a change after we start is a re-order and a re-start",
      "Anything going on the wall later — lights, numbers, a mount — tell me now and I'll back it"
    ] },
    { v: "paintorder", label: "Who's coating what, and when", who: "paint", by: "staging", specs: [
      "Tell me what's coming pre-finished and what you're coating on the wall",
      "If you need me to leave the staging up, say so before I strike it — after that it's a re-set",
      "Cut lines at the trim: settle who owns them before either of us starts"
    ] },
    { v: "access", label: "My elevation clear, and something to stand on", who: "gc", by: "wrap", specs: [
      "The elevation clear of cars, material and other people's staging on the day you give me",
      "Ground I can set a jack on, or tell me it's a lift and who's paying for it",
      "Somewhere for the tear-off to go, and the day the bin lands",
      "Temp power for the saw and the shear, or tell me I'm bringing a machine"
    ] }
  ]
};

/* ── WALK BACK (the reconcile engine) ───────────────────────────────────────
 * The answer half of the loop. The fourth rung is this trade's own and it is
 * the one that makes the page honest: on an exterior walk, half of what gets
 * written down is the WALL telegraphing through the cladding — a bowed stud, a
 * sheathing joint, a corner out of plumb, a plane that was never flat. Hanging
 * the siding differently does not make it go away, and the fix is a framing and
 * sheathing decision that belongs to whoever owns the wall. It is not a refusal
 * and not a commitment; it is an ask pointed at the substrate.
 * shared/reconcile.js classifies it "ask".
 */
window.TOOLKIT_ANSWER = {
  toolName: "Walk Back",
  eyebrow: "Siding · them → you → back",
  lede: "The super, the owner or the designer walked the house and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll hit it, with a day on it · Done already · Not mine · It's the wall — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll hit it line carries a day — hold me to it, and they land together on one trip instead of four drive-bys. Done already lines are just that — walk them this evening. Not mine is another outfit's work, or damage that landed after we were off that elevation, and those sit dated in my own log, which comes to you separately. It's the wall is the one worth reading twice: it means what you're looking at is what's UNDER the cladding coming through it — a stud that's proud, a sheathing joint, a corner that isn't plumb, a plane that was never flat. Hanging it again the same way puts it back. Making it go away is a decision about the wall, and that's the framer's, the GC's and the owner's to make together — tell me which way you want it and I'll hang to it.",
  answers: ["We'll hit it", "Done already", "Not mine", "It's the wall"],
  phJob: "412 Marchmont — full re-side",
  phTo: "Priya N — GC super",
  phFrom: "Dale W — Rivet Exteriors",
  phOff: "exterior walk 4/18",
  paste: "412 Marchmont — exterior walk — Apr 18\n\nJob: 412 Marchmont — full re-side\nFrom: Priya N — GC super\n\n22. rear — courses look wavy under the deck door, whole run\n23. left gable — J-channel short at the rake, gap you can see\n24. front — light block sits proud of the band, owner noticed\n25. right — downspout dumps onto the walk, splashing the wall\n26. rear — corner post scuffed, looks like a ladder\n27. front porch — soffit panel not seated at the return\n28. left — old hose bib stub still sticking out through the new wall\n29. right gable — two courses look off colour against the rest"
};

/* ── GETTING IN (the access engine) ─────────────────────────────────────────
 * The one trade on this rack whose whole job happens on the outside of a
 * building that people are living or working in, from a jack or a lift, over
 * their walk and their cars and their windows. Every process the building or
 * the owner runs comes back as a question aimed at its owner — the closure,
 * the power down, the notice, the parking, the dog and the gate are theirs,
 * and this page never pretends otherwise.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Siding · you → whoever holds the building",
  lede: "Working the outside of a building that's full of people all day. They hold the parking, the doors, the notice, the gate code and the phone that rings when a jack goes up outside somebody's window at seven. Send the ask that gets a real yes before the coil is ordered: which elevations and the days, where the trailer and the brake sit, ground that takes a jack, water and power, where the tear-off goes, and which doors and windows people actually use. Every heads-up on it ends by handing the process back to the man who owns it — on his building, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    "One day",
    "A few days running",
    "A week or more",
    "Early starts only",
    "Whatever you'll give me"
  ],

  need: [
    { name: "The elevation clear of cars by the hour you name", sub: "one car under the wall is an elevation I can't stage, and a day I still pay for" },
    { name: "Ground that takes a jack, or tell me it's a lift", sub: "soft, sloped, a deck, a bed of shrubs — walk it with me and say which, because that changes what shows up on the truck" },
    { name: "Where the trailer, the brake and the coil sit", sub: "off the elevation, out of the way, and somewhere nobody moves it overnight" },
    { name: "Somewhere the tear-off goes, and the day the bin lands", sub: "or tell me we're hauling it — either way I need the spot before the first wall comes off" },
    { name: "Power we can reach for the saw and the shear", sub: "a real outlet or a temp panel; tell me if it's a generator and I'll plan the noise around your hours" },
    { name: "Water we can reach", sub: "a hose bib is enough — cutting fibre cement wet is quieter and cleaner for everybody" },
    { name: "Which doors and paths people actually use", sub: "not the ones on the plan — the worn ones; that's where debris lands and where somebody walks under the wall" },
    { name: "The gate code, the dog, and who's home", sub: "or a name and a number — the answer is different on an occupied house than on a job site and I'd rather ask than find out" },
    { name: "Somebody to meet us the first morning", sub: "walk us round once — parking, water, power, where the bin goes — and after that we're repeatable" },
    { name: "Where we can leave staging up overnight", sub: "and whether you want it struck at the end of each day, because that's another half-hour off both ends and I'd rather agree it now than argue it Friday" }
  ],

  heads: [
    { name: "Pump jacks or staging go up the wall and stay up", sub: "tell me which windows and doors that sits over, and who tells the people behind them" },
    { name: "A walk, a drive or a patio under us needs a closure while we're on the wall", sub: "tell me who owns the closure and the notice — I'll cone what you tell me to cone, and the barricades go where you want them" },
    { name: "The service and the meter may have to come off the wall", sub: "tell me who owns the power down and who throws it back, because that's your electrician's and the utility's, never ours" },
    { name: "We may need roof access to set or tie staging", sub: "tell me who owns roof access and whether anybody has to be with us — I'm not stepping onto it on my own say-so" },
    { name: "The saw and the shear run most of the day, and the saw is dusty", sub: "tell me which hours you'll take it and which side of the building sleeps or takes calls" },
    { name: "Tear-off drops debris and nails under the wall", sub: "tell me where you want people kept off and who puts the sign on it; we sweep and magnet at the end of every day either way" },
    { name: "Dust and cutting near an open window or a fresh-air intake", sub: "tell me which windows and intakes you want us to work around, and who tells the people inside to keep them shut" },
    { name: "An old wall coming off a house of a certain age", sub: "tell me the year you have for it and who holds the testing and the certified outfit — that call isn't mine to make or to guess, and my crew stands down until you name it" },
    { name: "Something on the wall gets pulled and put back — lights, numbers, a mount, a rail", sub: "tell me what you want reused and what you want replaced, and who's buying the replacement" },
    { name: "The weather turns and we come off the wall", sub: "tell me who I call at six in the morning, and who tells the people inside it's off" }
  ],

  phSite: "412 Marchmont",
  phRoom: "rear elevation and the two gables",
  phHow: "side gate off the driveway, past the meter",
  phScope: "tear off and re-side the rear and both gables — four of us, jacks and a brake",
  phLoud: "the saw and the shear, most of the day",
  phTo: "Marcus D — owner",
  phMe: "Dale W — 559-555-0143",
  phCo: "Rivet Exteriors",

  /* THE THREE FIELDS THE ENGINE REQUIRES. `closing` is CONCATENATED by the page
     (`G.closing.concat([...])`), so omitting it is not a missing sentence — it
     is a TypeError on load and a blank page at every width. */
  warn: "<b>It&rsquo;s an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it &mdash; the closure, the notice, the parking, the power down, roof access and any testing on an old wall are the building&rsquo;s to run and to number, and we never will. Nothing here says what's on a wall or whether it's safe to cut it: that is a test and a certified outfit, and neither is ours.",

  closing: [
    "This is an ask, not a booking — nothing gets scheduled until you answer. Wrong days? Name the ones the building can live with and we'll take them.",
    "Saying yes: tell me the gate, the window you're actually giving us, who meets us the first morning, where the trailer and the bin go, and where the water and the power are — and the one that matters most, who tells the people inside, because it isn't us. If the answer on an old wall is a name, give it to me before we take anything off, not during."
  ]
};
