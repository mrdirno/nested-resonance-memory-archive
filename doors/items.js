/* DOORS & HARDWARE FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary that keeps a trade config from rotting (private roster, §THE
 * THREE ENGINES): trade.js = IDENTITY + COPY · tools.js = REGISTRY · this file
 * = the trade's VOCABULARY DATA. Categories, condition lists, hand values, the
 * asks each outfit owes him. Never in the identity config, never inline in a
 * page.
 *
 * WHAT IS NOT IN HERE, AND WILL NOT BE — the refusal list from trade.js, in
 * its data form, because this is the file where a later cycle would be tempted
 * to add it: no clearance, gap or undercut value · no fire label rating or
 * label-to-assembly crosswalk · no closer spring size, sweep, latch or
 * backcheck setting · no hardware set CONTENTS (a set number rides as an
 * ADDRESS only) · no door schedule columns · no keying, bitting or
 * keyed-alike structure · no ADA force, height or clearance · no anchor,
 * fastener or grout schedule · no rough-opening dimension we supply · no
 * voltage, wire size or device model at an electrified opening. Every list
 * below is a list of THINGS HE MIGHT SAY, never a list of values he should
 * use. Where a number belongs, the field is empty and the placeholder tells
 * him it comes off his own tape or his own approved shop drawing.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── BEFORE THEY SHIP (shape #3 — shared/rowlog.js) ─────────────────────────
 * THE PINNED TOOL, and the one page on this hub that could not exist anywhere
 * else. He walks the openings with a tape BEFORE frames are welded and sends
 * the distributor what the field actually is. Every value on a row is a
 * reading he took or a word he chose; the page supplies neither, and it
 * restates no column of the architect's schedule. The opening number is an
 * ADDRESS — that is the whole legal shape of this kit.
 */
window.TOOLKIT_ITEMS.openings = {
  /* HANDING IS THE #1 THING THAT COMES BACK WRONG, and it comes back wrong
     because it is decided standing in the opening, not at a desk. The four
     values are the trade's own and are spoken exactly like this. No
     definition rides with them: a man who needs the definition should not be
     calling the hand, and printing one here would be this page deciding. */
  hands: ["LH", "RH", "LHR", "RHR", "Pair — active LH", "Pair — active RH", "Not called yet"],

  /* WHAT THE OPENING IS MADE OF, as a wall gets described at the opening. */
  walls: [
    "CMU — grouted",
    "CMU — hollow",
    "Stud + gyp, one layer each side",
    "Stud + gyp, two layers one side",
    "Stud + gyp, two layers both sides",
    "Shaftwall",
    "Existing — cut into",
    "Poured concrete",
    "Not called yet"
  ],

  /* WHAT HE FOUND THAT THE SCHEDULE CANNOT KNOW. Every one of these is a
     field condition, never a verdict, and never a dimension we supplied. */
  finds: [
    "Wall is thicker than the throat I've got",
    "Wall is thinner than the throat I've got",
    "Opening's out of plumb",
    "Opening's out of square",
    "Head is low",
    "Rough opening is tight",
    "Rough opening is wide — needs a dutchman",
    "It swings the other way in the field",
    "There's no room for the leaf to stand open",
    "Something's in the swing",
    "Floor is out at the sill",
    "Two floor finishes meet under it",
    "Existing frame staying — new leaf only",
    "Nothing in the way — it's clean"
  ],

  /* THE GATE EACH ROW HAS TO BEAT — the trade's own sequence words, because
     "ASAP" is not a date and "before drywall" is. */
  gates: [
    "Before the mason lays past it",
    "Before the wall closes",
    "Before the floor goes in",
    "Before paint",
    "Before the ceiling closes",
    "Before the LV guy pulls his wire",
    "Punch — whenever it lands",
    "Not called yet"
  ],

  states: ["Sent", "Confirmed", "Ordered"]
};

/* ── CAME OFF THE TRUCK (shape #3 — shared/rowlog.js) ───────────────────────
 * The delivery gets signed for in the time it takes to walk a flatbed, and
 * from that signature forward every dent is arguably his. This is what he
 * counts against his OWN packing slip, sent the same afternoon. It prices
 * nothing, faults nobody and grades no finish — it counts.
 */
window.TOOLKIT_ITEMS.truck = {
  kinds: [
    "Frame — knock-down",
    "Frame — welded",
    "Leaf — hollow metal",
    "Leaf — wood",
    "Leaf — aluminum / glass",
    "Sidelite / transom frame",
    "Hinges",
    "Lockset / cylinder",
    "Exit device",
    "Closer",
    "Strike",
    "Threshold / weatherstrip",
    "Mullion",
    "Kick / armor plate",
    "Loose hardware carton",
    "Something else"
  ],

  /* WHAT IS WRONG WITH IT. "Wrong hand" and "short" carry the schedule; the
     rest are physical and he can see them from the tailgate. */
  wrongs: [
    "Short — didn't come",
    "Short — partial count",
    "Wrong hand",
    "Wrong size",
    "Wrong finish",
    "Wrong prep — or no prep",
    "Bent / racked",
    "Dented",
    "Scratched / finish damaged",
    "Wet / rusted",
    "Broken glass",
    "Carton opened, contents missing",
    "Not on my slip at all",
    "Came for another job"
  ],

  /* WHERE IT GOT FOUND, because a dent found on the truck and a dent found
     three weeks later in the stack are two entirely different conversations
     and only one of them is the carrier's. */
  found: [
    "On the truck, before I signed",
    "On the truck, after I signed",
    "In the stack, same day",
    "In the stack, later",
    "When I went to hang it"
  ],

  states: ["Sent", "Answered", "Replacement coming", "Landed"]
};

/* ── NOT READY TO HANG (shape #2 — shared/note.js) ──────────────────────────
 * The doorway note, and the twin of painting's Not Ready one trade later. The
 * asymmetry that makes it necessary: a leaf hung to a frame that is wrong, or
 * hung into a room that is not finished, gets adjusted twice and blamed once.
 * Each stop carries the ASK under it, so the note reads as a list a super can
 * clear by lunch rather than a complaint.
 */
window.TOOLKIT_ITEMS.nothang = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Owner's rep / construction manager",
    "Property / facility manager",
    "Another trade's foreman",
    "The distributor's inside man"
  ],

  stops: [
    {
      name: "Frame's not grouted",
      sub: "It moves when I lean on it, so anything I hang to it moves later. Tell me when it's grouted and set, or direct me in writing to hang to it as it stands."
    },
    {
      name: "Frame's out — plumb, square or twisted",
      sub: "What I measured is in the note beside what my own shop drawing says. Whoever set it fixes it, or tell me in writing to hang to it and it becomes a tag."
    },
    {
      name: "Frame's in the wrong opening — or the wrong hand",
      sub: "It doesn't match the mark it's standing in. Somebody needs to say which is right, the frame or the plan, before I put a leaf on it."
    },
    {
      name: "Floor's not in",
      sub: "The finish floor changes what the bottom of this leaf has to be. Hang it now and I'm back to pull it — tell me when the floor's down, or tell me in writing to hang and come back."
    },
    {
      name: "Two floor finishes and no threshold answer",
      sub: "Carpet one side, tile the other, and nothing says what happens at the line. I need that answered before the leaf goes on."
    },
    {
      name: "Wall's not painted",
      sub: "Paint after hardware means somebody masks my finish or gets paint on it — and the one they get paint on is always the lever. Say which order you want, in writing."
    },
    {
      name: "No power or wire at an electrified opening",
      sub: "Nothing's landed at the frame. I'll hang the leaf, but the head end isn't testable and I'm not the one who makes it work — tell me who's landing it and when."
    },
    {
      name: "Hardware's not here",
      sub: "The leaf can go on; the opening can't close out. What's missing is on my shortage list and it's already gone to the supplier — this is the schedule half of it."
    },
    {
      name: "Corridor's blocked — I can't get the leaf to it",
      sub: "Material, scaffold or another crew between me and the opening. Tell me when it's walkable and I'll take that floor in one pass instead of three."
    },
    {
      name: "Room's still occupied by another trade",
      sub: "Bodies and ladders where I'm setting. Once a leaf is on, everybody's cart hits it — tell me when they're out."
    },
    {
      name: "Nobody's said what the keying is",
      sub: "I have cylinders and no direction. Give me an answer or say the word and construction cores go in — coming back to re-core later is its own trip."
    },
    {
      name: "Existing opening — what's staying isn't decided",
      sub: "Nobody's said whether the frame stays or goes. That answer changes what I order, not just what I hang."
    }
  ],

  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};

/* ── SET IT FOR ME (the rough-in-request engine) ────────────────────────────
 * ONE MESSAGE PER OUTFIT, sent a week out, at the gate each outfit is already
 * counting down to. This is where the INTERFACE lives: low-voltage/items.js
 * ships `doorprep` with `who: "doors"` — electric hinge, raceway in the leaf,
 * frame prepped for the strike, header for the mag, mullion for the reader —
 * an ask aimed at this trade that, until this page existed, had nowhere to be
 * answered. The EC/LV rows below are that ask, answered from this side.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Set It For Me",
  eyebrow: "Doors · you → everybody who owes you an opening",
  lede: "Every opening in the building is somebody else's work until a leaf goes on it — after that it is yours, and it gets adjusted twice and blamed once. This is what has to be set, grouted, cleared, floored, wired and decided before a leaf comes off the cart: who owes it, which openings, and the gate it has to beat. Walk the floor once, tap the rows, send one message per outfit — a week out, while every line is still a conversation. The doorway refusal is Not Ready To Hang; this page is how you never send it.",
  docSubject: "Before I hang — what I need out of your outfit",
  docSubjectWith: "Before I hang — what I need from {to}",
  closing: "That's my list before a leaf goes on up there. If a line's wrong, or there's something at those openings you know that I don't, hit me back today — every one of these is a five-minute answer this week and a return trip the week my hardware is on the cart. And the part nobody likes said out loud: once a leaf is hung and adjusted, everything wrong behind it reads as my work, and I am the one standing there with a screwdriver explaining it. That's why I'm asking now.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set and <i>your</i> own approved shop drawings. This page sets no rough-opening dimension, no anchor or grout requirement, no plumb tolerance, no clearance or undercut, no closer setting, no label value and no keying &mdash; your submittal, your drawings and whoever inspects own all of that. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The opening numbers off your own approved shop drawings are the whole argument. Name the sheet you took this from and the super works your list against his own set; leave it off and it's one installer's opinion until he re-walks it with you — the morning you were supposed to be hanging.",
  phJob: "Alder Creek Medical — 3rd floor TI",
  phOff: "approved HM shop drawings, sheet 3, rev 2",
  phFrom: "Ray T — Vantage Door & Hardware",
  phArea: "3rd floor — openings 301 through 318 and both stair doors",
  areaLabel: "Opening / area",

  who: [
    { v: "gc", label: "GC super" },
    { v: "mason", label: "Mason" },
    { v: "framer", label: "Framer / drywall" },
    { v: "concrete", label: "Concrete / flatwork" },
    { v: "ec", label: "Electrician" },
    { v: "lv", label: "Low-voltage / access control" },
    { v: "flooring", label: "Flooring" },
    { v: "painter", label: "Painter" },
    { v: "hm", label: "Distributor / hollow metal supplier" }
  ],

  milestones: [
    { v: "lay", label: "Before you lay past it" },
    { v: "close", label: "Before the wall closes" },
    { v: "floor", label: "Before the floor goes in" },
    { v: "paint", label: "Before paint" },
    { v: "lid", label: "Before the ceiling closes" },
    { v: "hang", label: "Before I hang" },
    { v: "punch", label: "Before the walk" }
  ],

  asks: [
    { v: "set", label: "Frames set where they're marked", who: "mason", by: "lay", specs: [
      "Set to the marks, not to the wall you built",
      "Grout them solid — I'm hanging to them",
      "Leave the spreaders on till it's grouted",
      "Tell me the day each floor's frames are in",
      "If one won't fit the wall, call me before you make it fit"
    ] },
    { v: "framed", label: "Rough openings framed and true", who: "framer", by: "close", specs: [
      "Framed to my approved shop drawings, not to a rule of thumb",
      "Plumb and square before the rock goes on",
      "Backing where a closer or a holder lands",
      "Don't rock past a frame that isn't set",
      "Tell me the openings you had to move, and where to"
    ] },
    { v: "anchors", label: "Anchors and blockouts I can't add later", who: "concrete", by: "close", specs: [
      "Blockouts at the openings on my drawings",
      "Sill condition where the frame lands on slab",
      "Tell me before you pour, not after",
      "Anything cored later comes out of somebody's day"
    ] },
    { v: "power", label: "Power landed at the electrified openings", who: "ec", by: "close", specs: [
      "Pipe into the frame, hinge side",
      "Pipe to the strike jamb",
      "Up the header for anything mounted there",
      "Get it in before the frame gets grouted",
      "Tell me which openings you're feeding — I'll tell you which ones my submittal says are electrified"
    ] },
    { v: "prep", label: "The head-end answers I need to prep for", who: "lv", by: "close", specs: [
      "Tell me which openings get a reader, a release or a position switch",
      "Which leaf carries the transfer device",
      "Where you want the wire to come out",
      "Who lands it, and who terminates it",
      "Say it before frames are welded — after that it's a field cut"
    ] },
    { v: "floorin", label: "Floor in, or a straight answer about it", who: "flooring", by: "floor", specs: [
      "Finish floor down before I hang, or tell me it isn't coming",
      "Tell me where two finishes meet under an opening",
      "Tell me the day, not the week",
      "If I hang before you, I'm coming back — say who owns that trip"
    ] },
    { v: "paint", label: "Painted before hardware goes on", who: "painter", by: "paint", specs: [
      "Frames and leaves coated before I hang hardware",
      "Tell me which openings you're doing last",
      "If it's going on after, say so — somebody's masking my finish",
      "Nobody wipes a lockset with a rag off the paint bucket"
    ] },
    { v: "clear", label: "The floor walkable and the openings clear", who: "gc", by: "hang", specs: [
      "A route I can carry a leaf down",
      "Rooms clear of the other trades that day",
      "Somewhere the leaves and cartons can sit dry",
      "Tell me when a floor is actually mine for a day"
    ] },
    { v: "short", label: "What's still not here", who: "hm", by: "hang", specs: [
      "Confirm what's shipping and when",
      "The shortage list I already sent, answered line by line",
      "Tell me what's on backorder before it's the last opening",
      "Ship the openings that are blocking the walk-through first"
    ] },
    { v: "decide", label: "The answers nobody's given yet", who: "gc", by: "hang", specs: [
      "Keying direction, or say the word and construction cores go in",
      "What happens at the thresholds where two finishes meet",
      "Which existing frames are staying",
      "Any opening where the field and the plan disagree"
    ] }
  ]
};

/* ── PUNCH BACK (the reconcile engine) ──────────────────────────────────────
 * Somebody walked it and sent a list. The fourth rung is this trade's, and it
 * is the one that keeps the page honest: an installer frequently CANNOT say
 * yes at an opening, because what is being asked for is a hardware or label
 * question that belongs to his submittal and the people who stamp it.
 */
window.TOOLKIT_ANSWER = {
  toolName: "Punch Back",
  eyebrow: "Doors · them → you → back",
  lede: "The super, the architect or the owner's rep walked the openings and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll hit it, with a day on it · Done already · Not mine · Not my call — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll hit it line carries a day — hold me to it, and they land together on one trip instead of four drive-bys. Done already lines are just that — walk them tonight. Not mine is another outfit's work or damage that landed after I hung and adjusted the opening, and those sit dated in my own log, which comes to you separately. Not my call is the one worth reading twice: it means the answer lives in the approved hardware submittal or with the people who stamp it, not with me at the opening — send it that way and it comes back faster than if I guess at it here.",
  answers: ["We'll hit it", "Done already", "Not mine", "Not my call"],
  phJob: "Alder Creek Medical — 3rd floor TI",
  phTo: "Dana K — GC super",
  phFrom: "Ray T — Vantage Door & Hardware",
  phOff: "openings walk 8/21",
  paste: "Alder Creek Medical 3rd floor — door punch — Aug 21\n\nJob: Alder Creek Medical — 3rd floor TI\nFrom: Dana K — GC super\n\n41. 304 — leaf won't latch, catches the strike\n42. 306 — closer slams it\n43. 308 — frame's marked up, needs touch-up\n44. 309 — hinge screws stripped, top hinge\n45. 311 — leaf drags the carpet\n46. 312 — wrong lever finish, doesn't match the rest of the floor\n47. 315 — no cylinder in it yet\n48. 3C stair — leaf and frame tags don't read the same"
};

/* ── GETTING IN (the access engine) ─────────────────────────────────────────
 * An occupied building, and the one trade whose work is the building's own
 * security. Every process the building owns comes back as a question aimed at
 * its owner: the alarm, the access system, the cores and the keys are theirs,
 * and this page never pretends otherwise.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Doors · you → whoever holds the keys",
  lede: "Changing the doors on a building somebody else runs, while people are still in it. They hold the alarm, the access system, the freight lift and the phone that rings when a tenant's badge stops working on Monday. Send the ask that gets a real yes before the van is loaded: the door and the hours, who meets you, which openings go out of service and for how long, what happens to the alarm while a leaf is off its frame, and who takes the cores and the keys at the end of the night. Every heads-up on it ends by handing the process back to the man who owns it — in his building, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    "One night",
    "A few nights running",
    "Weekend",
    "Days, off-hours only",
    "Whatever you'll give me"
  ],

  need: [
    { name: "The door unlocked and somebody to meet us the first night", sub: "walk us in once — door, freight, laydown, panel — and after that we're repeatable" },
    { name: "Freight lift and a route we can carry a leaf down", sub: "leaves come in flat and they don't fit a passenger car" },
    { name: "Somewhere the leaves and cartons can sit dry", sub: "between shifts, out of the way, and where nobody borrows the hardware" },
    { name: "Doors unlocked", sub: "nobody has to stay" },
    { name: "Tell us which openings we're allowed to have off at once", sub: "so a stairwell or an exit route is never the one we've got apart" },
    { name: "Who's taking the cores and the keys at the end of the night", sub: "we don't want to be the ones holding them, and neither do you" },
    { name: "Power at the openings you want done live", sub: "if anything on them is electrified" },
    { name: "Somewhere we can cut, and a way to get the dust out", sub: "a leaf that has to be trimmed on site gets trimmed somewhere — tell us where, or we will make our own choice and you will not like it" },
    { name: "Tell us where a cart can sit on each floor", sub: "leaves travel flat on a cart and the cart has to stop somewhere that is not a fire exit" }
  ],

  heads: [
    { name: "An opening will be off its frame for part of the night", sub: "tell us what that means for your alarm, your access system and your after-hours procedure — they're yours, and you make the call" },
    { name: "We'll set off door-forced and door-held alarms", sub: "your dispatch sees them start to finish — tell us if you want them warned first" },
    { name: "A badge reader or a strike may be down while we work an opening", sub: "if that changes who can get where in your building, we need your direction before we start" },
    { name: "There'll be drilling and hammering at the frames", sub: "loud, and it carries — say which hours you'll take it" },
    { name: "Existing cores are coming out", sub: "tell us who receives them and whether anything goes back in tonight" },
    { name: "Patient or clinical space next door", sub: "tell me what you need from us before we start" },
    { name: "An opening may stand with no lockset in it for part of the night", sub: "we can hold it, sheet it or post somebody — tell us which one your building wants, because that is a security call and it is yours" },
    { name: "We will be propping doors open while we carry leaves through", sub: "if that matters to how your building holds air, or to what your alarm does, say so before the first night" }
  ],

  phSite: "The Aldrich Building — floors 5 and 6",
  phRoom: "corridor and stair doors, 5 and 6 — twenty-two openings",
  phHow: "loading dock off Pell Alley, freight to 5",
  phScope: "replace corridor and stair leaves and hardware — three of us, carts and hand tools, one core drill, four nights",
  phLoud: "drilling at the frames the first two nights after nine",
  phTo: "Mara S — building manager, the Aldrich",
  phMe: "Ray T — 559-555-0173",
  phCo: "Vantage Door & Hardware",

  /* THE THREE FIELDS THE ENGINE REQUIRES, and the reason they are called out
     here rather than left to a copy: `closing` is CONCATENATED by the page
     (`G.closing.concat([...])`), so omitting it is not a missing sentence — it
     is a TypeError on load and a blank page at every width. mobile-watertight
     caught exactly that on this file before it shipped. */
  warn: "<b>It&rsquo;s an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it &mdash; the alarm, the access system, the cores and the word to the tenants are the building&rsquo;s to run and to number, and we never will.",

  closing: [
    "This is an ask, not a booking — nothing gets ordered or scheduled until you answer. Wrong nights? Name the ones your building can live with and we'll take them.",
    "Saying yes: tell me the window you're actually giving us, the door, who meets us the first night, where the leaves and cartons sit between nights, and how many openings you'll let us have apart at once — and the one that matters most, who receives the cores and the keys at the end of each night. If the answer on the alarm or the access system is a person, give me their name before our first night, not during it."
  ]
};

/* ─────────────────────────────────────────────────────────────────────────────
 * THE LONG POLE — doors & hardware (2026-09-01). A config on shape #3.
 *
 * THE PANEL CALLED THIS THE STRONGEST YES OF THE FOUR, and for a reason that is
 * this trade's alone: the "four different people inside one house" claim, which
 * every other trade's version treats as one desk with four latencies, is here
 * LITERALLY four shops — the hollow-metal detailer, the hardware writer, the
 * wood plant and the glass shop — sitting under one order number and answering
 * on four different clocks. So the ask is not a nicety on this kit; it is the
 * routing, and asking the wrong shop is the whole reason email six exists.
 *
 * WHERE IT SITS BESIDE `before-they-ship.html`, and the boundary is worth
 * writing down because the two pages are one letter apart in a hurry:
 * `before-they-ship` is the FIELD MEASURE going out BEFORE anything is welded —
 * your tape, your words, the hand it really swings. This page is what happens
 * AFTER the order exists: the metal is somewhere and you need one fact back.
 * The first is a measurement you are sending; the second is a question you are
 * asking. Neither one numbers anything, and the architect's hardware schedule is
 * still the architect's — this page holds no set numbers, no keying and no
 * finish codes, because copying that schedule is the kill this trade lost to
 * twice (§DOORS).
 * ───────────────────────────────────────────────────────────────────────────── */
window.TOOLKIT_LONGPOLE = {
  toolName: "The Long Pole",
  eyebrow: "Doors & hardware · what sets your date → the distributor who owns the order",
  lede: "What sets your date &mdash; frames, doors, hardware, glass &mdash; in one list. Then <b>one message that asks one question</b> about the few lines it&rsquo;s actually about, so it lands on the right shop instead of the front desk.",

  warn: "<b>This is your own note of what you are chasing and what you were last told &mdash; and that is all it is.</b> There is no money on it, no running count of anything, and no arithmetic: a dated list of the dates somebody gave you is a claim document, and this is not one. <b>The hardware schedule is the architect's, the set numbers are his, and the submittal log is the GC's</b> &mdash; none of them are copied here. Their order number rides on a line as an <i>address</i>, so he knows which job you mean before he goes looking. <b>It lives in this browser, on this device, and nowhere else</b>: nothing typed here is sent anywhere, which also means a new phone starts empty. The spreadsheet copy is your backup.",

  poHint: "Your PO and their order number are an <b>address</b> &mdash; they tell him which of your jobs this is, and which of his four shops has it, before he goes looking. They are not a record of anything; whatever your office runs on owns that.",

  items: [
    "The hollow metal frames",
    "The hollow metal doors",
    "The wood doors",
    "The hardware",
    "The electrified hardware",
    "The access control prep",
    "The storefront",
    "The aluminum frames",
    "Fire-rated glass",
    "The exit devices",
    "The closers",
    "The lite kits and louvers",
    "Thresholds and weatherstrip",
    "The borrowed lites",
    "The coiling doors",
    "The lead-lined openings"
  ],

  /* SIX QUESTIONS, AND ON THIS KIT THEY ARE THE ROUTING. The fourth one names
     the shop out loud because that is the whole trick: one order number, four
     shops, four clocks, and a man who asks the front desk for "an update" gets
     the slowest of the four or none of them. */
  asks: [
    "Anything you still need from us — dimensions, the hand, the wall",
    "Frame sizes and prep off the approved set",
    "Whether you've got the approved sets and released off them",
    "A ship week — and which of your shops it's sitting in",
    "How it comes and who offloads it",
    "Whether you can hold it — we've nowhere dry to put it"
  ],

  states: ["Asked", "Nothing back", "They told me something", "It's here"],

  holds: [
    "Setting frames",
    "Closing the wall",
    "Taping",
    "Painting the frames",
    "Hanging doors",
    "The hardware install",
    "Access control terminations",
    "The fire marshal walk",
    "The punch walk",
    "Turning it over",
    "The certificate of occupancy walk"
  ],

  flags: ["This one first", "This is the one that moves the date"],

  labItem: "What you're chasing",
  labAsk: "What you need from him on this one",
  labHolds: "What it holds up",
  labGate: "The date it has to beat — or the one it must not beat",
  labTold: "Last thing you were told — their words, and who said it",
  labRef: "Their order number",
  labWho: "Who you're asking",
  groupAskLabel: "What you need",

  docSubject: "what I'm chasing",
  poLabel: "Our PO",
  docStoppingHead: "The ones actually stopping work",
  docStoppingLede: "These are the ones that are actually stopping work — the rest I can live with for now.",
  docOneThing: "Just the one thing this time, on",

  opening: "Short list of what I'm chasing on this job. Nothing here is a problem yet — I'd just rather none of it turn into the reason we slip.",

  closing: "If any of these are stuck on your end, tell me which one and I'll work the schedule around it — and if it's in a different shop than I think it is, say so and I'll ask the right person next time. If you put out a status report on this job, put me on the list and I'll stop emailing you.",
  docBoundary: "That's my own note of what I'm chasing and what I was last told, in my words. It isn't a claim, there's no day count on it, and nothing on it changes what we agreed.",

  phJob: "Rosewood ES",
  phPo: "the number on your end",
  phFrom: "you / your shop",
  phItem: "what it is — then it's a button",
  phAsk: "— what you need on this one",
  phGate: "“before the walls close” · “not before we’re dried in”",
  phTold: "“Lena, 6/12 — week of the 18th”",
  phRef: "so he doesn’t have to go look",
  phWho: "the name on the order acknowledgment",

  askNeutral: "— pick the one thing this message asks for",
  askStopping: "The ones stopping work",
  askAll: "Everything on the list — my own record",
  askHintNone: "<b>Pick one.</b> A message that asks five things gets one of them answered — usually the easiest one, three days later. Ask for the one you actually need this week and send the rest next time.",
  askHintPicked: "That is the whole message: one question, and the lines it's about. He answers one thing today instead of picking through five and going quiet.",

  emptyText: "Nothing on the list yet. Put in the first thing you're chasing — what it is, and what you actually need out of him on it."
};
