/* PAVING & STRIPING FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary that keeps a trade config from rotting (private roster, §THE
 * THREE ENGINES): trade.js = IDENTITY + COPY · tools.js = REGISTRY · this file
 * = the trade's VOCABULARY DATA. What is in the way of a stall, what is under
 * his base and whose it is, what stops a paving day, what he is closing
 * tonight and who has to hear it, the asks each outfit owes him before he
 * rolls. Never in the identity config, never inline in a page.
 *
 * WHAT IS NOT IN HERE, AND WILL NOT BE — the refusal list from trade.js, in
 * its data form, because this is the file where a later cycle would be tempted
 * to add it: no mix design, mix or lay-down temperature, density, compaction
 * number, thickness, lift or tonnage-per-area (the lab and the plant own those;
 * the ticket rides as an address) · no accessible-stall COUNT, stall or aisle
 * DIMENSION, slope limit, sign height or symbol spec, and no stall-count table
 * of any kind (the page says what the SHEET draws and what HIS TAPE found, and
 * asks who decides) · no fire-lane length, width or marking (the fire
 * marshal's) · no traffic-control, flagger or lane-closure plan (an engineered,
 * permitted document — we ask WHO holds it and stop) · no cure time,
 * open-to-traffic time, sealcoat product, rate, paint spec or dry time (his
 * own spec sheet, in his words) · no scale ticket, load-to-yield math or price
 * · no verdict that a subgrade, base or lift passed anything · no proof-roll
 * verdict beyond "here is what I saw where the truck sat" · no tow list, plate
 * list or tenant roster · no weather threshold · no slope number for a
 * birdbath · and no release, ever: nothing here says a lot is open, accepted,
 * complete or warrantable. Every list below is a list of THINGS HE MIGHT SAY,
 * never a list of values he should use. Where a number belongs, the field is
 * empty and the placeholder tells him it comes off his own sheet, his own tape
 * or his own ticket.
 *
 * AND THE WORD THAT IS NOT IN HERE AS A NAME: "paver". On this rack a paver is
 * the masonry brick — landscape/items.js says "Pavers on base" and means the
 * hardscape. The machine is "the paver" only inside a sentence that makes it a
 * machine ("a loaded truck and the paver"); the brand word is PAVING, the
 * surface is THE MAT, the plan side is THE LAYOUT, and the man is the paving
 * crew or the striper. Twelve kits use "sprinkler" to mean fire protection, so
 * the lawn heads on the islands are "the irrigation" here, same as landscape.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── DOESN'T FIT (shape #3 — shared/rowlog.js) ──────────────────────────────
 * THE PINNED TOOL, and the one page on this hub no other trade could write.
 * The striping sheet was drawn on a lot that did not have a pole base in it
 * yet, or a hydrant, or a curb return that came in a foot long. He lays it
 * out with a chalk box and a wheel and finds out. Every row is a place the
 * SHEET and the LOT disagree — the sheet quoted, the tape his — sent to the
 * super, the civil or the owner BEFORE paint hits the mat, because after
 * paint it is a grind-out and an argument. The page carries no stall count,
 * no dimension, no aisle width, no slope and no accessibility call of its
 * own: it structures what the sheet says and what he found, and asks which
 * one goes. Doctrine named the count table the kill-in-waiting; this is the
 * page built so it can never appear.
 */
window.TOOLKIT_ITEMS.layout = {
  /* WHAT IS IN THE WAY, standing at it. The receiver reading "light pole
     base" knows the count is short by exactly one and why. */
  ways: [
    "Light pole base",
    "Hydrant / FDC",
    "Lid / valve box / cleanout",
    "Curb return / island",
    "Wheel stop / bollard",
    "Sign post",
    "A grade the sheet doesn't show",
    "Water sitting",
    "A lip at the walk",
    "The building / column",
    "Nothing — the count's just off"
  ],

  /* WHAT HE NEEDS DECIDED. Every one of these hands the decision to the man
     who stamps the sheet; none of them is a decision of his. "Paint it as
     drawn — in writing" is the one that saves him in the meeting. */
  asks: [
    "Tell me which one goes",
    "Shift the run — your call which way",
    "Move the accessible pair — your call where",
    "Re-draw it and send me the rev",
    "Paint it as drawn — in writing",
    "Come look at it with me"
  ],

  states: ["Sent", "Answered", "Painted as answered"]
};

/* ── UNDER THE MAT (shape #3 — shared/rowlog.js) ────────────────────────────
 * The letter back. landscape/items.js wrote "Walk my sleeves before the base
 * rolls" and aimed it at a chip called paving; sitework built a "Paving /
 * base" chip whose nine asks never routed to anybody; low-voltage's "Pipe out
 * to the gate before paving" went to the electrician. Every one of them was
 * a man with something under HIS base and nowhere to hear back from. This is
 * one row per thing somebody else has under his mat before it rolls — whose
 * it is, what it is, who told him, whether he saw it, and whether the iron is
 * to grade. It says nothing about cover depth, separation or sleeve size;
 * it says what he was told and what he saw with his own eyes.
 */
window.TOOLKIT_ITEMS.under = {
  /* WHOSE IT IS — the chips the other kits already built, answered from this
     side. "Don't know whose" is honest and it is the row that matters most. */
  whose: [
    "Landscape / irrigation",
    "Low-voltage / gate",
    "Electrician / site lights",
    "Plumber / utilities",
    "Storm / sewer",
    "Water / valve boxes",
    "Gas",
    "Survey monument",
    "Concrete / curb",
    "Don't know whose"
  ],

  /* WHAT IT IS, the way it gets named standing on the base. */
  whats: [
    "Sleeve",
    "Conduit / bore",
    "Pipe / main",
    "Stub-up",
    "Lid / manhole",
    "Valve box",
    "Cleanout",
    "Pull box",
    "Pole base",
    "Monument / pin"
  ],

  /* WHETHER HE SAW IT. "Told, not seen" is the whole reason the axis exists:
     a sleeve on somebody's list and a sleeve he watched go in and get capped
     are two different amounts of trust, and only one of them survives a
     roller. */
  seen: [
    "Saw it in, capped",
    "Marked on the base",
    "Told, not seen",
    "Nobody's said"
  ],

  /* THE IRON — lids, boxes and rings against the finished mat. A lid under the
     mat is a saw cut in a month; a lid proud of it is a lip and a plow blade.
     Whose job it is to raise it is a question, never a claim of his. */
  iron: [
    "To grade",
    "Not raised — needs a riser",
    "Low — it'll be under the mat",
    "High — a lip",
    "Not mine to raise"
  ],

  /* THE GATE EACH ROW HAS TO BEAT — his own sequence words, the ones the
     other kits count down to. "Before the mat cools" is the last honest one. */
  gates: [
    "Before the base rolls",
    "Before we prime",
    "Before we pave",
    "Before the mat cools",
    "Punch — whenever it lands",
    "Not called yet"
  ],

  states: ["Sent", "Confirmed", "In — I saw it"]
};

/* ── NOT READY TO PAVE (shape #2 — shared/note.js) ──────────────────────────
 * The section note, and the twin of landscape's Not Ready To Plant and doors'
 * Not Ready To Hang. The asymmetry that makes it necessary: a mat over a base
 * that was soft is HIS warranty, and the plant does not take the loads back.
 * Each stop carries the ASK under it, so the note reads as a list a super can
 * clear by lunch rather than a complaint — and not one of them carries a
 * number, because the string line reading is his and the sheet's callout is
 * the sheet's, and both go in the measured section in his words.
 */
window.TOOLKIT_ITEMS.notready = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Owner's rep / construction manager",
    "Property / facility manager",
    "Civil / engineer",
    "Another trade's foreman"
  ],

  stops: [
    {
      name: "The base is soft — it pumps under the truck",
      sub: "I watched it move where the water truck sat, and that's the whole of what I'm saying. Whoever built it fixes it, or the lab calls it, or direct me in writing to pave it as it sits."
    },
    {
      name: "Base not to grade against the curb — high or low",
      sub: "What my string line read off the curb is in the note, beside what the sheet says. Whoever graded it brings it in, or tell me to pave to it and it becomes a tag."
    },
    {
      name: "Curb & gutter not in, or not cured",
      sub: "I can't roll a mat against a form. Tell me the day the curb's in and the day I can put a roller beside it — the day, not the week."
    },
    {
      name: "Lids, boxes and monuments not to grade",
      sub: "Every one that's low is under my mat and a saw cut in a month. Tell me who's raising the iron and when, or tell me in writing which ones I'm paving over."
    },
    {
      name: "Sleeves and crossings not in — somebody's still trenching",
      sub: "I've got the crossing lists. A trench through my base after I roll is a patch with my name on it. Tell me the day the last one's in and capped."
    },
    {
      name: "Cars, a conex and dumpsters still on my section",
      sub: "A section with a conex on it isn't a section. Tell me the day it's actually mine, and keep everything off it after that."
    },
    {
      name: "No set, or the wrong rev, for the layout",
      sub: "I'm not laying out off a sheet the civil already changed. Send me the rev I'm painting to, and a name who answers when it doesn't fit."
    },
    {
      name: "Nobody's called the lab",
      sub: "The density number is theirs, not mine, and a lift nobody tested is an argument I don't want to have in March. Tell me who's calling them and that they're on site the day I roll."
    },
    {
      name: "Wet base, or rain on the way — my call, my words",
      sub: "I'm not paving today, and here's what I saw. No threshold of mine is on this note; the plant order stands or cancels on what I'm telling you now."
    },
    {
      name: "The trucks can't get in — the haul route's blocked",
      sub: "A loaded truck doesn't turn where a pickup turns. Tell me who moves the fence, the trailer or the pile, and by when."
    },
    {
      name: "A utility trench still settling in my section",
      sub: "It's not mine and it'll show through the mat by winter. Whoever dug it compacts it and says so, or the lab says so, or direct me in writing to pave over it."
    },
    {
      name: "The walk got poured high — a lip nobody will take",
      sub: "My mat meets the walk where the walk is. Tell me whether that's a grind, a re-pour or a taper in writing, and whose day it is."
    },
    {
      name: "Sealcoat: it's too green to seal",
      sub: "Off my spec sheet, in my words — not a number of mine. Tell me the day you want me back and I'll hold the rig."
    },
    {
      name: "Power / gate: the pole bases aren't in",
      sub: "A pole base cored through a finished mat is a patch and an argument. Tell me the day the electrician's done with the bases and the conduit."
    }
  ],

  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};

/* ── LOT CLOSED TONIGHT (shape #2 — shared/note.js) ─────────────────────────
 * THE NOTICE. On an occupied lot his cones decide where two hundred people
 * park tonight, and the one thing he can never be is surprised at seven when
 * a car is sitting on wet seal. The page records what HE is closing, which
 * sections, and when cars come back IN HIS WORDS off his own spec sheet — it
 * states no cure time and no product — and hands the tenant notice, the tow
 * list, the fire lane and the road plan back to the people who own them. It
 * is a notice, not a permit and not a traffic plan.
 */
window.TOOLKIT_ITEMS.closure = {
  roles: [
    "Property manager",
    "GC superintendent",
    "Owner's rep",
    "Building engineer",
    "Tenant contact",
    "Our own boss / PM"
  ],

  /* WHAT IS CLOSING, the way he says it on the phone. */
  kinds: [
    "Sealcoat",
    "Striping / layout",
    "Paving — a section",
    "Patching / crack fill",
    "Seal + stripe, two nights"
  ],

  asks: [
    { name: "Tell the tenants — you, not me", sub: "a name and a time it went out, so nobody's surprised at seven" },
    { name: "A car still on it at seven — who moves it", sub: "the tow list is yours, and so is the call; give me a name I can ring, not a policy" },
    { name: "The entrances you want kept open, by name", sub: "and I'll cone the rest — tell me which one the delivery trucks use" },
    { name: "The doors people actually use — seal tracks", sub: "tell me which doors, and who's putting a sign on them; a lobby with seal on the tile is a bad morning for both of us" },
    { name: "Where the trucks and the rig stage", sub: "somewhere the neighbors won't call about at nine at night" },
    { name: "Nobody pulls a cone before I say", sub: "a cone that walks at midnight is a car on wet seal at six, and it's yours" },
    { name: "The irrigation on the islands off tonight", sub: "a head that comes on at two in the morning washes the seal off the row beside it — tell me who's got the clock" },
    { name: "Who I call at five in the morning if it rained", sub: "the night's off, the cones stay or come in, and somebody has to tell the tenants which — a name and a number" },
    { name: "The fire lane stays open the whole time", sub: "tell me the fire marshal's contact and what he wants kept open — that's yours, and nothing here marks a fire lane" }
  ],

  pics: ["Sent with photos of the cones", "Photos on request", "Walk it with me"]
};

/* ── BEFORE I ROLL (the rough-in-request engine) ────────────────────────────
 * ONE MESSAGE PER OUTFIT, sent a week out, at the gate each outfit is already
 * counting down to. This is where the INTERFACE lives: landscape/items.js
 * ships "Paving / striping" as a receiver and wrote him a letter, sitework
 * ships "Paving / base" as an orphan chip, low-voltage aims "pipe out to the
 * gate before paving" at the EC, electrical says "saw cut and patch the
 * asphalt" — four kits built for a man who, until this page existed, had
 * nowhere to answer from. He is on the job LAST; everybody owes him
 * something, and the rows below are that list.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before I Roll",
  eyebrow: "Paving · you → everybody who owes you something",
  lede: "You're the last man on the job, and everything under your base is somebody else's work until the mat goes over it — after that it's yours, and it's a saw cut. This is what has to be in, raised, cured, cleared and decided before the plant ships the first load: who owes it, where, and the gate it has to beat. Walk the section once, tap the rows, send one message per outfit — a week out, while every line is still a conversation and the plant order is still a phone call. The refusal is Not Ready To Pave; this page is how you never send it.",
  docSubject: "Before I roll — what I need out of your outfit",
  docSubjectWith: "Before I roll — what I need from {to}",
  closing: "That's my list before a load leaves the plant for that section. If a line's wrong, or there's something under my base you know about that I don't, hit me back today — every one of these is a five-minute answer this week and a cancelled plant order the morning my trucks are lined up. And the part nobody says out loud: a mat over a base that wasn't ready is my warranty, and I'm the one saw-cutting it next spring explaining it. That's why I'm asking now.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set and <i>your</i> own contract. This page sets no mix, no lay-down temperature, no density, no thickness and no tonnage &mdash; the lab and the plant own those. It carries no accessible-stall count, no stall or aisle dimension and no slope &mdash; the sheet and the people who stamp it own that. It states no cure time and no open-to-traffic time &mdash; your own spec sheet does, in your words. And it never says a subgrade, a base or a lift passed anything: that's the lab's numbered report and the civil's call. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and its revision is the whole argument. Name the civil and the striping sheet you took this off and the super works your list against his own set; leave it off and it's one paving foreman's opinion until he re-walks it with you — the morning the trucks were supposed to be rolling.",
  phJob: "Willow Creek — Phase 2, north lot",
  phOff: "C-301 rev 2, C-201 rev 3",
  phFrom: "Manny R — Blacktop Bros Paving",
  phArea: "north lot and the drive to the loading dock",
  areaLabel: "Section / area",
  /* THE REST OF THE BAR IN HIS WORDS (2026-09-04). The shared request page
     asked every trade for a "Room / area", a "Size / type" and a "Height / run
     — 60 AFF · or: to the ceiling above the rack": AV's bar showing through on
     a page a paving foreman sends. These are the same fields with this trade's
     labels on them; the engine page falls back to its own words when a key is
     absent, so a kit that never sets them is unchanged. */
  areaHint: "Type the section the way the crew says it and it becomes a button for the rest of the walk.",
  specLabel: "What exactly",
  phSpec: "or type your own",
  specHint: "Pick what you need above and the usual lines show up here — yours, off your set, never a spec of ours.",
  placeLabel: "Where on the section",
  phPlace: "north end, by the second light pole · or: the whole drive aisle",
  phNote: "anything that won't fit above — what's in the way, whose trench it is, who else is in that section",
  phTel: "the number they ring from the lot",
  docBoundary: "check them against your own set before the base rolls.",

  who: [
    { v: "gc", label: "GC super" },
    { v: "dirt", label: "Sitework / grading" },
    { v: "conc", label: "Concrete / curb" },
    { v: "land", label: "Landscape / irrigation" },
    { v: "ec", label: "Electrician / site lights" },
    { v: "lv", label: "Low-voltage / gate" },
    { v: "plumb", label: "Plumber / utilities" },
    { v: "civil", label: "Civil / engineer" },
    { v: "lab", label: "Testing lab" },
    { v: "owner", label: "Owner / property manager" }
  ],

  milestones: [
    { v: "base", label: "Before the base rolls" },
    { v: "prime", label: "Before we prime" },
    { v: "pave", label: "Before we pave" },
    { v: "cool", label: "Before the mat cools" },
    { v: "stripe", label: "Before we stripe" },
    { v: "open", label: "Before it opens" },
    { v: "seal", label: "Before we seal" }
  ],

  asks: [
    { v: "proof", label: "Subgrade proof-rolled, with the soft spots named and who's fixing them", who: "dirt", by: "base", specs: [
      "Walk it with me behind the loaded truck — I'll flag where it moves",
      "Tell me who's digging out the soft spots and the day they're done",
      "Tell me the day the lab's looking at it — the pass is theirs, not mine",
      "Your spoil and your pile off my section before the base truck comes"
    ] },
    { v: "curb", label: "Curb & gutter in and cured so the mat meets it without a lip", who: "conc", by: "base", specs: [
      "Tell me the day, not the week",
      "The day I can put a roller against it, off your own cure — I'm not stating it",
      "Forms and stakes pulled and the base back against the gutter",
      "If a return came in long or short, tell me today — the layout's drawn against it"
    ] },
    { v: "iron", label: "Every lid, valve box, cleanout and monument raised to grade", who: "plumb", by: "base", specs: [
      "Tell me who's raising the iron — you, the utility, or me on a ticket",
      "Rings and risers on site before the base rolls, not the morning we pave",
      "Paint every one you own on the base so my raker sees it",
      "The water valve is the purveyor's — tell me who's touching it, because it isn't me"
    ] },
    { v: "sleeves", label: "Sleeves in, capped and marked past the base edge — I've got your list, walk it with me", who: "land", by: "base", specs: [
      "Every stub sticking out past the base edge and flagged",
      "Capped both ends so the roller doesn't fill it with fines",
      "Your crossing list against my walk — if one's missing, today",
      "Once it's paved it's a bore, and it's your money"
    ] },
    { v: "gate", label: "Pipe to the gate and the pull box in before the base rolls", who: "lv", by: "base", specs: [
      "The gate loop and the conduit to the operator in and marked",
      "The pull box lid to grade — tell me if that's yours or the EC's",
      "Tell me the day it's in, and I'll walk it with you before I roll"
    ] },
    { v: "poles", label: "Pole bases and the site-light conduit in before the base rolls", who: "ec", by: "base", specs: [
      "Every pole base poured and the conduit stubbed before the base truck comes",
      "Paint your runs on the base — a shovel through your feed is on whoever didn't mark it",
      "If a base lands in a stall on the sheet, tell the civil today — it's a Doesn't Fit row already",
      "Tell me which pull box is yours, and that the lid's to grade"
    ] },
    { v: "set", label: "The set I'm paving to — sheet and rev, and who answers at six in the morning", who: "gc", by: "pave", specs: [
      "The current civil and the current striping sheet, by rev, before the trucks are ordered",
      "A name and a cell that answers at six, not an office at nine",
      "Anything the field and the sheet disagree on that you already know about",
      "Tell me whether the mulch pile, the conex and the trailer are moving, and when"
    ] },
    { v: "clear", label: "Cars, dumpsters, the conex and trade trucks off my section — and a day it stays off", who: "owner", by: "pave", specs: [
      "Tell me the day the section's actually mine, not the week",
      "The tow list is yours — give me a name who moves a car at six",
      "Nobody drives on it until I say, in my words off my sheet — not a time of mine on paper",
      "Tell the tenants; you, not me"
    ] },
    { v: "haul", label: "The haul route — where the trucks come in, turn and stage, and who moves the fence", who: "gc", by: "pave", specs: [
      "A route a loaded truck and the paver make, with a place to turn around",
      "Tell me who moves the fence panel and the gate, and that they're there at six",
      "Where the trucks wait so the plant's first load isn't sitting — the mat behind me is the clock",
      "Tell me who owns the road closure or the lane out on the street, if there is one — that plan isn't mine"
    ] },
    { v: "lab", label: "The lab on site the day I roll — tell me who's calling them", who: "lab", by: "pave", specs: [
      "Tell me who's calling you and who's paying — it isn't me unless my contract says so",
      "Be there when the first truck dumps, not at noon",
      "The density number is yours, not mine; I want it in writing the same day",
      "Tell me before I leave the job if a lift didn't make it"
    ] },
    { v: "stripe", label: "The striping sheet at the current rev before paint, and a name who decides when it doesn't fit", who: "civil", by: "stripe", specs: [
      "The current rev of the striping sheet, in my hand, before I chalk a line",
      "A name that answers the same day when the tape and the sheet disagree",
      "The accessible pair is yours to place — I lay it out first and I want the nod before the rest",
      "Whatever the fire marshal wants for the fire lane, in writing from him — it isn't mine to draw"
    ] },
    { v: "open", label: "Who's walking it before it opens, and what the closure says to tenants", who: "owner", by: "open", specs: [
      "A name walking it with me before a cone comes in",
      "What you're telling the tenants and when — I'll send the sections and the night, you send the notice",
      "Who I call at five in the morning if it rained",
      "Nothing I send says the lot's open or accepted — you say that, in your words"
    ] }
  ]
};

/* ── WALK BACK (the reconcile engine) ───────────────────────────────────────
 * Somebody walked it and sent a list. The fourth rung is this trade's, and it
 * is the one that keeps the page honest: on a lot punch, a stall count, an
 * arrow, a fire-lane length or an accessible pair the owner wants moved is a
 * PLAN question — it lives with the civil and the owner, not with the man
 * holding the striper. It is not a refusal and not a commitment; it is an ask
 * pointed at the sheet. shared/reconcile.js classifies it "ask".
 */
window.TOOLKIT_ANSWER = {
  toolName: "Walk Back",
  eyebrow: "Paving · them → you → back",
  lede: "The super, the owner's rep or the property manager walked the lot and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll hit it, with a day on it · Done already · Not mine · It's the plan — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll hit it line carries a day — hold me to it, and they land together on one trip instead of four drive-bys. Done already lines are just that — walk them tonight. Not mine is another outfit's work, or damage that landed after I finished, and those sit dated in my own log, which comes to you separately. It's the plan is the one worth reading twice: it means the line is asking me to change what the sheet draws — a stall count, an arrow, where the accessible pair sits, how long the fire lane runs — and that answer lives with the civil, the owner and the fire marshal, not with the man holding the striper. Send it that way and it comes back faster than if I paint something nobody stamped.",
  answers: ["We'll hit it", "Done already", "Not mine", "It's the plan"],
  phJob: "Willow Creek — Phase 2, north lot",
  phTo: "Dana K — GC super",
  phFrom: "Manny R — Blacktop Bros Paving",
  phOff: "lot walk 9/12",
  paste: "Willow Creek Phase 2 — lot punch — Sep 12\n\nJob: Willow Creek — Phase 2, north lot\nFrom: Dana K — GC super\n\n41. dock — arrows painted backwards, trucks coming in the wrong way\n42. east end — accessible symbol faded already, can barely see it\n43. cart corral — water sitting after the rain, birdbath\n44. lobby — seal tracked in on the tile by the north door\n45. row C — stall 14 short, a compact can't get in\n46. drive — cold joint open along the loading dock\n47. north entrance — cones still out, tenants asking\n48. islands — seal on the curb face by the pharmacy"
};

/* ── GETTING IN (the access engine) ─────────────────────────────────────────
 * An occupied lot, and the one trade whose work is where the tenants park.
 * Every process the building owns comes back as a question aimed at its
 * owner: the closure, the tenant notice, the tow list, the fire lane, the
 * road plan, the power at the pole and the water valve in the section are
 * theirs, and this page never pretends otherwise.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Paving · you → whoever holds the lot",
  lede: "Working a lot that's full of somebody's cars all day. They hold the gate, the tenants, the tow list and the phone that rings when a car drives through wet seal at seven. Send the ask that gets a real yes before the plant order goes in: which sections and the nights, where a loaded truck turns and the rig stages, which doors people actually use, where the sweepings go, and what happens on the street if the trucks need a lane. Every heads-up on it ends by handing the process back to the man who owns it — on his lot, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    "One night",
    "Two nights running",
    "A few days",
    "Nights / off-hours only",
    "Whatever you'll give me"
  ],

  need: [
    { name: "The section actually empty of cars by the hour you name", sub: "one car left on it is a section I can't seal, and a night I still bill" },
    { name: "The tow list is yours — a name who moves a car", sub: "not a policy, a person with a phone who's awake at seven" },
    { name: "A route a loaded dump truck and the paver make", sub: "a truck doesn't turn where a car turns, and it'll be in and out all shift" },
    { name: "Where the truck and the rig stage", sub: "out of the way, off the section, and somewhere the neighbors won't ring about" },
    { name: "Water we can reach for the rig", sub: "a hose bib or a hydrant meter that's yours to arrange — we bring the hose" },
    { name: "Where the sweepings and the millings go", sub: "or we haul them — tell us where a bin can sit for a night" },
    { name: "Which doors people actually use", sub: "not the ones on the plan — the ones with a worn path to them; that's where seal tracks in" },
    { name: "Somebody to meet us the first night", sub: "walk us in once — gate, route, water, where the cones go — and after that we're repeatable" },
    { name: "The entrances you want kept open, by name", sub: "and which one the delivery trucks use, because that's the one that gets driven through" }
  ],

  heads: [
    { name: "We're closing a section of the lot", sub: "tell me who owns the closure and the tenant notice, and what the fire marshal wants kept open — the fire lane's yours to name, not mine to mark" },
    { name: "The torch is running on the crack fill", sub: "tell me where you don't want it and who your fire watch is — that's yours to set, and there's an extinguisher beside it either way" },
    { name: "The sealcoat rig's engine and a blower run all shift", sub: "tell me which hours you'll take it, and which side of the building sleeps" },
    { name: "The mat's hot and the seal's wet — a door that opens onto it tracks", sub: "tell me which doors people use and who's putting a sign on them" },
    { name: "Trucks backing across the lot with a spotter", sub: "tell me where you don't want them, and the hours" },
    { name: "The seal and the paint smell — at a door or an intake", sub: "tell me which intakes and doors you want us to stay off, and who tells the tenants" },
    { name: "A road closure or a lane out on the street for the trucks", sub: "we don't hold that plan or that permit — tell me who does, and how you want the trucks to come in" },
    { name: "A valve box or a lid in the section gets covered while we seal", sub: "tell me who owns each lid and which ones you want kept clear — the water valve is the purveyor's, not ours to touch" },
    { name: "The site lights or the gate powered down while we pave at the pole base", sub: "tell me who owns the power-down and who throws it back — that's your electrician's, not ours" },
    { name: "Cones and tape go where the cars actually go, not where the plan says", sub: "tell me how you want the doors people use kept open, and who walks it with me before I pull a cone" },
    { name: "It rains — the night's off and the lot's back to you", sub: "tell me who I call at five in the morning, and who tells the tenants it's off" }
  ],

  phSite: "Oakridge Corporate Center — north lot",
  phRoom: "the north half, rows A–D",
  phHow: "service drive off Pell Road, behind B",
  phScope: "seal and stripe the north half — four of us, the rig and the striper, two nights",
  phLoud: "the blower and the rig, first two hours of each night",
  phTo: "Mara S — property manager, Oakridge",
  phMe: "Manny R — 559-555-0188",
  phCo: "Blacktop Bros Paving & Striping",

  /* THE THREE FIELDS THE ENGINE REQUIRES, and the reason they are called out
     here rather than left to a copy: `closing` is CONCATENATED by the page
     (`G.closing.concat([...])`), so omitting it is not a missing sentence — it
     is a TypeError on load and a blank page at every width. mobile-watertight
     caught exactly that on the doors copy before it shipped. */
  warn: "<b>It&rsquo;s an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it &mdash; the closure, the tenant notice, the tow list, the fire lane, the road plan and the power at the pole are the building&rsquo;s to run and to number, and we never will. Nothing here says when cars can come back: that's on your sheet in your words, sent the night we close.",

  closing: [
    "This is an ask, not a booking — nothing gets scheduled until you answer. Wrong nights? Name the ones your lot can live with and we'll take them.",
    "Saying yes: tell me the gate, the window you're actually giving us, who meets us the first night, where the truck and the rig stage, and where the water is — and the one that matters most, who moves a car at seven and who tells the tenants, because it isn't us. If the answer on the road closure is a person, give me their name before our first night, not during it."
  ]
};
