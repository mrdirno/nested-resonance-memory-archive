/* SITEWORK FIELD TOOLKIT — THE TRADE'S VOCABULARY.
 *
 * `trade.js` = IDENTITY + COPY · `tools.js` = REGISTRY · this file = the WORDS.
 * Categories, option lists, ask lines, ladders. Nothing here is a runtime and
 * nothing here is a number we supply.
 *
 * WHERE THESE WORDS CAME FROM. Three independent in-trade lenses — a mass-ex and
 * grading foreman, an underground utility foreman, and a GC super who ran
 * electrical for ten years and whose own conduit lives in the ditch — each wrote
 * this trade's vocabulary with no sight of the others, and a 20-year dirt hand
 * was then told to kill about a third. The convergence is the finding: all three
 * produced the SAME gate ladder with backfill at its centre, and all three named
 * rock, water, unsuitables, an unmarked line, standby and a re-dig as the six
 * things that put a dirt crew outside its contract. Those six are the top of
 * `tag.why` because three witnesses put them there, not because they read well.
 *
 * THE REFUSAL IS THE DESIGN, and in this trade it is stricter than anywhere else
 * on the rack. Nothing in this file is:
 *   · a soil class, a slope, a bench, a shore, a shield, a setback, a depth
 *     threshold, or any word that could be read as "safe to enter";
 *   · a compaction spec — no proctor, no lift as a value, no moisture, no passes;
 *   · a bedding or backfill class, a cover depth, a separation distance, a
 *     thrust block, a test pressure or a test duration;
 *   · a locate, a ticket number, or any claim that a mark is current or correct.
 * Every one of those is a place where the honest tool structures what the USER
 * states off his own plan, spec, geotech report or utility notes. A later cycle
 * that adds one is not filling a gap; it is the defect this file was built to
 * refuse. Men die in trenches, and the number is engineered off a soil that a
 * page on a phone has never seen.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── THE EXTRA WORK TAG (shape #2 — shared/note.js) ────────────────────────
 * Who directed it, what came up, why it is outside the contract, and the line
 * everybody argues about later: what is NOT in this tag. Counts only — men,
 * hours, loads and material as quantities. No rates, no totals, and no signature
 * line, because a copy-paste block cannot be signed and a dirt foreman spots it
 * instantly.
 *
 * DIFFERING SITE CONDITIONS IS THIS TRADE'S WHOLE EXTRA-WORK STORY, which is why
 * this list looks nothing like the mason's. Rock, water, unsuitables and a line
 * nobody marked are not "changes" anybody directed — they are what the ground
 * turned out to be, and the tag exists to put a date and a witness on them the
 * day they were still visible. Once the dirt is back, nobody can see what he was
 * standing in.
 */
window.TOOLKIT_ITEMS.tag = {
  roles: [
    "GC superintendent",
    "Our own general super",
    "GC project manager",
    "Our PM or the office",
    "Another trade's foreman in our ditch",
    "The surveyor or the engineer's rep on site",
    "Owner's rep or construction manager",
    "Builder's field super (tract or custom home)",
    "Homeowner",
    "Utility owner's inspector on site",
    "Jurisdiction inspector on site"
  ],
  how: [
    { v: "Face to face at the ditch" },
    { v: "Text message" },
    { v: "Phone call" },
    { v: "Told to me at the morning huddle" },
    { v: "Radio on the site channel" },
    { v: "Email" },
    { v: "Marked-up set handed to me in the field" },
    { v: "Paint or stakes changed on the ground" },
    { v: "A different trade told me he'd cleared it" }
  ],
  /* WHY IT IS OUTSIDE THE CONTRACT. Every line is a CONDITION he picks, not a
     characterisation of anybody, and not one of them puts a price, a cause or a
     verdict on the page. The first six are the ones all three panels wrote. */
  "why": [
    {
      "name": "Rock — the bucket quit going down",
      "sub": "Had to work it with something that isn't what we bid, or go at it a different way, to get to the bottom we were given."
    },
    {
      "name": "Water in the hole",
      "sub": "Pumped it, hauled it wet, worked it twice, or dried it back before anything could go in."
    },
    {
      "name": "Unsuitables — it wouldn't hold",
      "sub": "Wet, mucky or trashy dirt that would not stand up. Told to dig it out and put something back, or told to work it anyway."
    },
    {
      "name": "A line in the ground nobody marked",
      "sub": "Not on the plan and not in the paint. Stopped, hand dug to find it, stood by, or worked around it."
    },
    {
      "name": "The marks were off",
      "sub": "Dug where the paint said and it was not there — or it was, and not where it was shown. Hand digging and time nobody bid."
    },
    {
      "name": "Old work nobody told us about",
      "sub": "Slab, footing, tank, debris or an abandoned line in our dig that was not on anything we bid."
    },
    {
      "name": "Bottom kept going down",
      "sub": "Dug past what the set showed us to get to what somebody on site called for."
    },
    {
      "name": "Standing while another outfit got out of our ditch",
      "sub": "Crew and iron on site, waiting on somebody else to finish in the hole we were manned for."
    },
    {
      "name": "Held it open for a test, a shot or a look",
      "sub": "Ready to close and told to leave it while somebody else got here — a surveyor, a lab, an inspector, an owner."
    },
    {
      "name": "Re-dug a run we had already closed",
      "sub": "Dirt was back in and somebody's work was not. Opened it up again on a say-so."
    },
    {
      "name": "Grade or layout moved after we built to it",
      "sub": "Stakes gone, offsets changed, or a new set landed after we had already worked to the first one."
    },
    {
      "name": "Dirt in or dirt out nobody bid",
      "sub": "Import hauled in or spoil hauled off that was not in the scope, or a stockpile moved twice because the plan for it changed."
    },
    {
      "name": "Access or the haul route changed after we mobed",
      "sub": "Different gate, longer haul, plates, a detour or hours we did not have when we priced the move-in."
    },
    {
      "name": "Told to work the weather",
      "sub": "Keep going, pump it, tarp it, or come back on a day we had called off."
    }
  ],
  /* WHAT IS NOT IN THIS TAG. The line everybody argues about later, and the
     reason the tag survives being read by an office: it says out loud what it is
     not. Three panels independently wrote the lab, the surveyor and the locate
     ticket into this list — in this trade, the documents that surround the work
     all belong to somebody else, and saying so is what keeps this one usable. */
  "notin": [
    {
      "name": "Not a price",
      "sub": "Hours, loads and counts only. No rate, no total, no dollar figure anywhere on it."
    },
    {
      "name": "Not a change order and not a claim",
      "sub": "This says we were directed and what it took. It becomes a change when the offices paper it, and entitlement is their letter, not the foreman's."
    },
    {
      "name": "Not the lab's report",
      "sub": "Density, moisture and soils are their gauge and their number. We write that we stood by; we never write whether it passed."
    },
    {
      "name": "Not the surveyor's as-built",
      "sub": "He shoots it, he stamps it and he numbers it. All we say is what we could not cover until he did."
    },
    {
      "name": "Not a locate and not a ticket",
      "sub": "The one-call centre owns that number and owns its clock. Nothing here renews one, clears one, or says a mark is good."
    },
    {
      "name": "Not a call on whether the hole was safe to be in",
      "sub": "That is the competent person, on site, in person, in front of the actual soil. It is not a line on a phone and it is not on this tag."
    },
    {
      "name": "Not a design change",
      "sub": "Bottom, bedding, box, slope, backfill — none of it gets decided here. Anything about the design goes up through the GC on their form."
    },
    {
      "name": "Not a damage claim",
      "sub": "A line that got hit goes on the utility's own paper, right then, through their process. It does not ride on this."
    },
    {
      "name": "Not the environmental paper",
      "sub": "Contaminated or regulated material rides on its own manifest with its own people, and we do not retype what is printed on it."
    },
    {
      "name": "Not the GC's daily",
      "sub": "They keep theirs and number it. This is ours and it stands on its own."
    },
    {
      "name": "Not a finding of cause",
      "sub": "We write what we dug and who told us to dig it. Why something failed, settled or was where it was is a call other people make."
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
  /* THE CLASSIFICATIONS. OPERATOR and PIPELAYER are both on this list and it is
     not a courtesy — the man in the machine and the man in the ditch are
     different classifications doing different work at the same moment, and a tag
     that cannot name them cannot count who actually stood. */
  "classes": [
    "— class",
    "OPERATOR",
    "PIPELAYER",
    "LABORER",
    "FOREMAN",
    "TRUCK DRIVER",
    "GRADE CHECKER",
    "APPRENTICE"
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

/* ── BEFORE WE DIG (shape #3 — shared/rowlog.js) ───────────────────────────
 * THE ASK HALF OF THE BOUNDARY, and it is DELIBERATELY SHORT.
 *
 * THE PRUNE KILLED THIS PAGE OUTRIGHT and the kill was half right, so half of it
 * was taken. Its argument, verbatim: "Two broadcast tools on one kit and neither
 * gets used — a crew learns one page or none, and the one that matters is the
 * one nobody else can write." What it was actually objecting to was DUPLICATION:
 * the first cut of this list carried eight asks gated at `backfill` — your
 * conduit in, your stubs capped, the shot before I cover, sleeves through the
 * footing, somebody standing here when it goes back — and every one of those is
 * the pinned tool's job, said to everybody at once instead of one outfit at a
 * time. They were cut, not reworded.
 *
 * So the two documents on this kit have DISJOINT jobs and share no line:
 *   before-we-close.html  — what YOU need out of MY hole, before it shuts.
 *   this page             — what I need from YOU before the machine starts.
 * Every ask below is gated at `mobe`, `dig`, `pipe` or `tiein`. If a later cycle
 * adds one gated at `backfill`, it has re-opened the exact overlap the prune
 * killed the page for.
 *
 * THE MILESTONES ARE THIS TRADE'S OWN LADDER, not the GC's, and they are the
 * prune's nine — merged from three independent panels that each wrote the same
 * spine. Three shipped kits (electrical, plumbing, gc) open their own ladder
 * with the SEVENTH rung on this one.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before We Dig",
  eyebrow: "Sitework · you → everybody who owes you something before the machine starts",
  lede: "Everything that has to be called in, marked, staked, delivered, cleared or decided before you break ground. Who owes it, where it is, and the gate it has to beat. One walk, one message each.",
  docSubject: "Before we dig — what I need out of your outfit",
  docSubjectWith: "Before we dig — what I need from {to}",
  closing: "That's my list before we start. If a line on here is wrong, or there's something out there you know about that I don't, hit me back today — everything on this list is cheap this week and expensive the morning the machine is sitting on it.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set. This page slopes nothing, benches nothing, shores nothing, classes no soil, beds nothing, compacts nothing and locates nothing &mdash; and it doesn't know what the plans, the geotech report, the utility owner, the engineer of record or the AHJ require. Verify all of it against your own approved set, and whether a hole can be worked in is the competent person's call on site, in front of the actual soil, not a page's. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet, the profile and its revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you the morning you're supposed to be digging.",
  phJob: "Willow Creek — Phase 2",
  phOff: "C-401 rev 3",
  phFrom: "Ray T — Delgado Excavating",
  phArea: "SS main, MH-3 to MH-4",
  areaLabel: "Run / line / area",
  who: [
    { v: "gc", label: "GC super" },
    { v: "survey", label: "Surveyor / layout" },
    { v: "elec", label: "Electrician" },
    { v: "plumb", label: "Plumber / mechanical" },
    { v: "lv", label: "Low-voltage / comms" },
    { v: "gas", label: "Gas / utility owner" },
    { v: "conc", label: "Concrete / flatwork" },
    { v: "lab", label: "Testing lab / geotech" },
    { v: "sprink", label: "Fire / sprinkler contractor" },
    { v: "land", label: "Landscape / irrigation" },
    { v: "paving", label: "Paving / base" },
    { v: "owner", label: "Owner / owner's vendor" },
    { v: "supply", label: "Supplier / yard" }
  ],
  milestones: [
    { v: "mobe", label: "Before we roll in" },
    { v: "strip", label: "Before we strip" },
    { v: "cut", label: "Before we cut" },
    { v: "dig", label: "Before we open ground" },
    { v: "pipe", label: "Before pipe goes in" },
    { v: "tiein", label: "Before we tie in" },
    { v: "backfill", label: "Before we backfill" },
    { v: "bluetop", label: "Before we blue-top" },
    { v: "demob", label: "Before the hoe leaves" }
  ],
  asks: [
    { v: "locates", label: "The locates, and who called them", who: "gc", by: "dig", specs: [
      "Tell me who called the ticket and when, and get me the copy — I am not digging off a mark somebody says is out there.",
      "Private lines are not on a public ticket. Site lighting, irrigation, the owner's old feed, anything behind the meter — who is locating those, and when?",
      "If a mark and the plan disagree, that comes to me before the machine does, not while I am sitting on it.",
      "Tell me what you want potholed and who is standing there when I do it."
    ] },
    { v: "layout", label: "Layout, control and the bench", who: "survey", by: "dig", specs: [
      "Give me the control and the benchmark you want me working off, and tell me which set they came from.",
      "Stakes, offsets and the cut sheet in my hand before the machine tracks off the trailer — an offset I have to guess at is a re-dig.",
      "If the alignment moved on the last set, tell me before I open ground, not after.",
      "Tell me who is re-shooting it when my stakes get run over, because they will."
    ] },
    { v: "plan", label: "The set I am actually digging to", who: "gc", by: "dig", specs: [
      "Confirm the sheet and the revision. A superseded profile costs a day and a saw cut, and it has happened to everybody.",
      "Anything on this run dimensioned to something not built yet, flag it now.",
      "If there is a soils report or a geotech recommendation I am supposed to be working to, I want the copy in my hand rather than a sentence about it.",
      "Tell me who answers a question at seven in the morning when the ground is not what the sheet says."
    ] },
    { v: "strip", label: "What comes off, and what stays", who: "gc", by: "strip", specs: [
      "Once the topsoil is off, anything staked, fenced, growing or sitting there is gone. Walk it with me and say what stays.",
      "Tell me where the topsoil goes and whether you want it back — that is a pile that sits somewhere for months.",
      "Trees, fence, irrigation, a neighbour's line: if it is protected, it gets flagged by whoever cares about it, today.",
      "Anything you need at OLD grade — a shot, a photo, a tie — get it before we cut, because after that it does not exist."
    ] },
    { v: "spoil", label: "Where the spoil goes and where the import lands", who: "gc", by: "mobe", specs: [
      "Say the stockpile location and say it once — a pile moved twice is a day of a machine's life.",
      "Tell me what is coming off this site and what is coming in, and who is paying attention to which.",
      "If any of it is suspect, tell me before it is on a truck — that material has its own paper and its own people.",
      "Somewhere the trucks can turn around without going through somebody's finished work."
    ] },
    { v: "access", label: "The route in, the gate and the hours", who: "gc", by: "mobe", specs: [
      "A lowboy needs a gate, a turn and something to sit on. Tell me which entrance and how early it is open.",
      "Overhead is the one nobody thinks about until a boom is under it — tell me what is over my haul route.",
      "Who owns the traffic control, the plates and the closure if I am working in a public way? That is yours to number, not mine.",
      "Tell me who else is working over or under me that week so we are not both there."
    ] },
    { v: "water", label: "Where the water goes", who: "gc", by: "dig", specs: [
      "Tell me the discharge point you are giving me and who cleared it, because a hole takes water whether anybody planned for it or not.",
      "If there is a filter, a bag or a tank I am supposed to be using, tell me before I need it and not while it is running.",
      "Tell me who owns the stormwater paper and who walks it, because that inspection is on their form and their name is on it, not mine.",
      "If we are dewatering, say who is watching what it does to everybody else's hole."
    ] },
    { v: "material", label: "Pipe, structures and castings on site", who: "supply", by: "pipe", specs: [
      "On the ground and staged before I open it, by mark, and tell me what is actually on the truck versus what ships that week.",
      "Castings and rings with the structures, not a week behind them — I am not sitting on an open hole waiting on a lid.",
      "If a piece came damaged or is the wrong mark, I would rather lose it on the ground than in the ditch.",
      "Tell me where you are setting it, because a load dropped wherever the truck stopped gets moved by the crew that was meant to be laying."
    ] },
    { v: "shutdown", label: "The shutdown and who loses service", who: "gc", by: "tiein", specs: [
      "Say the day and the window, and say who loses water, flow or power while we are in there.",
      "Everybody affected has to be told by somebody with the authority to tell them — that is not the man in the ditch.",
      "Tell me who is turning the valve or pulling the plug, because it is not going to be me on my own.",
      "If it slides, I need to know before my crew and my pump are sitting on it."
    ] }
  ]
};

/* ── WHAT I'LL LEAVE OPEN (shape #3 — the RETURN LEG) ──────────────────────
 * The mirror. Three served kits ship a page that sends this crew a list; this is
 * the page he answers it on. The one field that makes it this trade's rather
 * than a reskin is the WHEN: a yes on this document carries the TIME the dirt
 * goes back, because that is the only number the other man can plan around.
 */
window.TOOLKIT_ANSWER = {
  toolName: "What I'll Leave Open",
  eyebrow: "Sitework · them → you → back",
  lede: "The electrician or the plumber sent you a list of what has to be in this trench before it closes — conduit, stubs, sleeves, a marked-up plan typed out. Line it up, give each one a yes, a no or a question, and put the TIME on every yes. Then send back one answer he can work to.",
  docSubject: "what I'll leave open",
  closing: "That's the yes, the no, and the time. Anything I flagged I need a location or an answer on before we get there. I can leave any of it open while it's open, and none of it after the dirt goes back — tell me the time you need and I'll hold it.",
  phJob: "Willow Creek — Phase 2",
  phTo: "Danny — EC foreman",
  phFrom: "Ray T — Delgado Excavating",
  phOff: "E-101 rev 2",
  paste: "Willow Creek Phase 2 — site duct bank — Aug 16\n\nJob: Willow Creek Phase 2\nFrom: Danny — EC foreman\n\nMH-3 to MH-4 · our 4in duct bank is in the same ditch, needs to stay open till Thursday\nAt the building · two stubs coming up inside the footprint, marked in orange\nAcross the drive · tracer wire tail has to come up where we can clip on it\nSouth pad · empty conduit for site lighting — needs string in it before you cover"
};

/* ── BEFORE WE CLOSE IT (shape #3 — the pinned tool) ───────────────────────
 * THE ONE DOCUMENT ON THIS JOB NOBODY ELSE CAN WRITE. electrical/items.js,
 * plumbing/items.js and gc/items.js have each been telling a whole trade to
 * count down to "before backfill" since those kits shipped, and nothing anywhere
 * publishes the time. This does.
 *
 * THE INVERSE-CLAIM GUARD, inherited from masonry and sharper here: a list that
 * names the runs nobody may touch will be read as clearing the runs it did not
 * name. So the `touches` axis has NO "it's fine" value, a blank means he said
 * nothing, and the document footer says so in words the page does not let you
 * configure away.
 *
 * AND THE HARDER GUARD, WHICH IS THIS TRADE'S ALONE: not one value on `touches`
 * is a permission. Every one of them is a refusal or a come-ask-me with a
 * handback. There is no "shored", no "sloped", no "OK to enter" and there never
 * may be — the man who decides a trench can be entered is the competent person
 * standing in front of the actual soil, and no chip on a phone can be that.
 */
window.TOOLKIT_DITCH = {
  toolName: "Before We Close It",
  eyebrow: "Sitework · you → everybody with something in the ditch",
  lede: "Run by run at quitting time: what's open, what's in it, what's holding it, and the time the dirt goes back. Tap each run up the ladder and send one message. Three other trades have been counting down to your backfill since the job started — this is the first page that gives them the time.",
  docSubject: "before we close it",

  /* THE LADDER, and it does NOT wrap: a run does not go back to not-dug, and the
     pencil is the correction path. "Shot" sits before "backfilled" on purpose —
     it is the last thing that has to happen while the ditch is still a ditch,
     and it is the one everybody forgets until the closeout meeting. */
  states: [
    { v: "notdug", label: "Not dug yet" },
    { v: "open", label: "Open — dug to grade" },
    { v: "pipe", label: "Pipe / conduit in" },
    { v: "tied", label: "Tied in" },
    { v: "tested", label: "Tested" },
    { v: "shot", label: "Shot — as-built taken" },
    { v: "backfilled", label: "Backfilled" },
    { v: "graded", label: "Graded out" },
    { v: "off", label: "Off it" }
  ],
  /* STILL OPEN runs from OPEN to short of BACKFILLED — there is a hole in the
     ground and the dirt has not gone back. That is what four other outfits are
     racing, and it is declared here ONCE, by value, so the header count, the
     filter and the footer call-out can never disagree. */
  openFrom: "open",
  openTo: "backfilled",

  /* WHAT IS IN THE DITCH — the seed list for a learn axis, never a closed set.
     A receiver reading "storm + EC duct" knows instantly that his water line is
     not in that one, which is the whole reason this axis exists. */
  ins: [
    { v: "storm", label: "Storm" },
    { v: "san", label: "Sanitary" },
    { v: "water", label: "Water" },
    { v: "fire", label: "Fire main" },
    { v: "gas", label: "Gas" },
    { v: "primary", label: "Electric — primary" },
    { v: "secondary", label: "Electric — secondary / site lighting" },
    { v: "duct", label: "EC duct bank" },
    { v: "comms", label: "Comms / innerduct" },
    { v: "irr", label: "Irrigation" },
    { v: "drain", label: "Roof drain / area drain" },
    { v: "sleeves", label: "Sleeves only" },
    { v: "cut", label: "Nothing — it's a cut" }
  ],

  holds: [
    { v: "going", label: "Nothing — we're going" },
    { v: "locate", label: "Locates or the ticket" },
    { v: "marks", label: "Marks don't match the ground" },
    { v: "rock", label: "Rock" },
    { v: "water", label: "Water in the hole" },
    { v: "unsuit", label: "Unsuitables — it won't hold" },
    { v: "unknown", label: "Something down there nobody marked" },
    { v: "trade", label: "Another outfit's work in it" },
    { v: "shot", label: "Waiting on the shot" },
    { v: "lab", label: "Waiting on the lab to stand here" },
    { v: "insp", label: "Waiting on an inspection" },
    { v: "material", label: "Pipe, structures or castings short" },
    { v: "grade", label: "A grade or an alignment nobody's answered" },
    { v: "layout", label: "Stakes or layout" },
    { v: "shutdown", label: "The shutdown or the tie-in window" },
    { v: "access", label: "Access, plates or traffic control" },
    { v: "spoil", label: "Nowhere to put the spoil" },
    { v: "weather", label: "Weather" },
    { v: "iron", label: "Machine down" },
    { v: "men", label: "Manpower" }
  ],

  /* WHAT NOBODY TOUCHES. Every value is a REFUSAL or a NOTICE WITH A HANDBACK.
     Not one of them is a permission, a depth, a slope, a class, a duration or a
     clearance. THERE IS DELIBERATELY NO "it's fine" AND NO "safe to enter" VALUE
     ON THIS AXIS — if a later cycle adds one, that is the defect this page was
     designed around and not a tidy-up. */
  touches: [
    { v: "open", label: "It's open — nobody drives it or crosses it" },
    { v: "edge", label: "Stay off the edge and off the spoil side" },
    { v: "exposed", label: "There's a line exposed in it — nobody swings near it" },
    { v: "nobody", label: "Nobody in this trench but my crew — come see me" },
    { v: "plates", label: "The plates and the fence are ours — call before anybody moves one" },
    { v: "pump", label: "The pump stays running — don't switch it off" },
    { v: "notshot", label: "Not shot yet — don't cover any of it" },
    { v: "notdone", label: "Not tied in yet — nothing gets used" },
    { v: "stakes", label: "Don't pull the stakes or the offsets" },
    { v: "nostack", label: "Don't stack or set anything on this ground" }
  ],

  nexts: [
    { v: "dig", label: "Keep digging it" },
    { v: "pipe", label: "Lay pipe in it" },
    { v: "tie", label: "Tie it in" },
    { v: "test", label: "Test it" },
    { v: "shoot", label: "Get it shot" },
    { v: "close", label: "Put the dirt back" },
    { v: "grade", label: "Grade it out" },
    { v: "trade", label: "Waiting on another outfit" },
    { v: "mat", label: "Waiting on material" },
    { v: "none", label: "Nothing on it tomorrow" }
  ],

  flags: ["Closing it in the morning", "Nobody goes near it"],

  phJob: "Willow Creek — Phase 2",
  phFrom: "Ray — Delgado Excavating",
  phNum: "(209) 555-0148",

  closing: "That's where the dirt got to today, in my words. Anything listed as held is stopped on somebody else — ring me and I'll tell you what it's stopped on, because a date doesn't help a man whose conduit has to be in before the machine starts.",
  open: "Anything of yours that has to be in one of those — conduit, pipe, a stub, a sleeve, tracer, a shot, a photo — get it in or ring me before that time. Once it's closed and rolled it isn't a phone call, it's an excavator, and it's a brand new trench through work that's already in.",
  /* NOT CONFIGURABLE IN SPIRIT: the second sentence is the inverse-claim guard,
     the third is the money/quantity refusal, and the first is the one that keeps
     a man out of a hole this page has no business talking about. All three print
     on every document. */
  warn: "<b>Nothing on this page classes a soil, slopes, benches, shores or shields a trench, or says a trench is safe to enter or to work in.</b> A run not named here is a run I have said nothing about. No count on it is a quantity in place, a percent complete or a price, and nothing on it is a locate, an as-built or a compaction record."
};

/* ── GETTING IN (shape #2) ─────────────────────────────────────────────────
 * The one boundary in the program where the receiver is not another trade, and
 * the only one where being wrong leaves a crew and a load standing at a locked
 * gate. For this trade the load is a lowboy with a machine on it, which is the
 * most expensive thing in the program to leave sitting.
 *
 * Every heads-up option ends in a QUESTION aimed back at whoever owns the
 * process — they are handbacks, not statuses. If a later cycle rewrites one into
 * "dig permit obtained", that is the defect, not a tidy-up.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Sitework · you → whoever holds the keys",
  lede: "You need a lowboy, a machine and a truck onto ground somebody else locks — and then you need somewhere to put the spoil for a fortnight. Send the ask that gets a yes before the float is loaded: the route in, the gate, where the pile goes, who's coming, and the heads-up that keeps an excavator sitting outside a fence on a Monday morning.",
  docName: "ACCESS REQUEST",

  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "A week or two" },
    { v: "Ongoing — I'll flag changes" }
  ],

  need: [
    { name: "Gate unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The route in", sub: "wide enough for a lowboy and a truck, and a turn at the end of it" },
    { name: "What's overhead on that route", sub: "a boom or a raised bed finds it before I do" },
    { name: "Where the spoil goes", sub: "somewhere it can sit for the length of the job without being moved twice" },
    { name: "Where the import lands", sub: "and whether a truck can get to it in the wet" },
    { name: "Somewhere to park the iron overnight", sub: "and whether it's yours to say or the neighbours'" },
    { name: "Water on site", sub: "for dust, and where we're allowed to draw it" },
    { name: "Where the water goes", sub: "if the hole makes any — tell me the discharge point you're giving me" },
    { name: "Somewhere to wash out", sub: "a spot you're okay with, and who hauls it off" },
    { name: "Nobody there — we'll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "iron moving in before anyone's normally there" },
    { name: "Tell me who gets our COI", sub: "if it isn't already on file" }
  ],

  heads: [
    { name: "It'll be loud, and it starts early", sub: "a machine and trucks from first light — say the word and we'll move the window" },
    { name: "There'll be dust", sub: "we run water on it — tell me what's downwind, what your intakes are, and what you want covered" },
    { name: "The ground will shake a bit", sub: "trucks and a machine near the building — tell me what's sensitive and who owns it" },
    { name: "There'll be an open hole on your property", sub: "nobody but my crew goes in it or near the edge, and the barricade stays where I put it — who do you want that told to?" },
    { name: "A lowboy is coming in and it can't back up far", sub: "tell me the entrance you want it using before it's on the street outside" },
    { name: "There'll be a pile of dirt for a while", sub: "tell me where it can sit and whether anything is going to be parked next to it" },
    { name: "Trucks will track dirt onto the road", sub: "we'll sweep it — tell me if there's a rule about that here and who enforces it" },
    { name: "We may need something powered down or a valve turned", sub: "tell me who owns that switch and what notice they need. It isn't us" },
    { name: "We'll be in and out of a public way", sub: "tell me who owns the closure and the permit for it — that's yours to number, not ours" },
    { name: "Something we dig up may need somebody else's people", sub: "if it's regulated material it rides on its own paper — tell me who you'd call" }
  ],

  phSite: "Bishop Ranch 3",
  phRoom: "North lot — behind the loading dock",
  phHow: "south gate off Camino, past the dock, straight onto the lot",
  phScope: "trenching the new service run — machine, truck and a crew of four",
  phLoud: "machine and trucks from 7am, done mid-afternoon",
  phTo: "Ray — property manager",
  phMe: "Ray T — 209-555-0148",
  phCo: "Delgado Excavating",

  closing: [
    "This is an ask, not a booking — nothing rolls until you reply. Wrong day? Tell me which one works and we'll take it.",
    "Saying yes: tell me the window you're actually giving us, where the pile can sit, and who's meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It's a request, not a permit and not a booking.</b> Anything on the heads-up list that needs a permit, a lane closure, a fire watch or a utility shutdown is theirs to issue and theirs to number — this page just tells them it's coming and asks how they want it run. And check your contract before you send it: plenty of them say you don't talk to the building direct. If yours does, send this to your GC and let him forward it — same words, right chain."
};

/* ── THE MATERIAL CALL (shape #1 — shared/checklist-request.js) ─────────────
 * The TENTH instance of checklist → a request, and `sitework/tools.js` shipped
 * this trade naming it as one of the two rungs it was deliberately NOT building
 * yet: "a VOCABULARY BUILD the size of the supply-house order and the yard call
 * — units of issue that are not interchangeable, a fittings vocabulary per
 * material, and structures that arrive by mark."  That is what this block is.
 * Masonry's yard call set the bar it has to clear and stated it in one line: a
 * man who calls in an order off a list that is MISSING a line stops opening the
 * list.  Half an order page is worse than none.
 *
 * WHAT THIS TRADE'S ORDER HAS THAT NO SIBLING'S DOES:
 *
 *  1. IT GOES IN A HOLE THAT DOES NOT REOPEN.  Every other order page on the
 *     rack is short a line and somebody drives to the counter.  Short a line
 *     here and the choice is stand the crew down or bury the job without it —
 *     and `trade.js` already wrote the test: "a wall can be cut, a ceiling can
 *     be pulled", a backfilled trench is DUG AGAIN.  So the buried lines are
 *     marked in the DATA (`ditch: true`), and the page gathers them into a
 *     second reading the counter cannot skim past.  Tracer wire and detectable
 *     tape are the two cheapest lines in this whole file and the two that cost
 *     the most to leave off, because there is no adding them later at any price.
 *
 *  2. THE TIE-IN.  Masonry's page proved the RUN mechanism — a per-line flag,
 *     a header passthrough, and a call-out when one exists without the other —
 *     and the private record's instruction was that the next order page should
 *     STEAL it rather than re-derive it.  Its isomorph here is the tie-in: a
 *     fitting that lands on somebody else's forty-year-old pipe has to match
 *     what is actually in the ground, which is cast, clay, AC, DI or PVC and is
 *     not always what the as-built says.  The wrong transition coupling does not
 *     cost a trip, it costs the shutdown.
 *
 *  3. THE UNIT OF ISSUE, third instance and lifted verbatim.  Pipe leaves by
 *     the JOINT or by the FOOT and those are two different trucks; stone by the
 *     TON or the LOAD; fabric, tape and tracer by the ROLL; a frame and cover
 *     and an accessory pack by the SET.  A bare number gets the yard's own word
 *     attached to it and anything he wrote in words is left exactly as he wrote
 *     it — the tool never re-counts a man's order.
 *
 * NOTHING SPEC'D, and this file's refusal list at the top governs every line
 * below it without exception.  No pipe class, no pressure class, no wall
 * thickness, no gauge, no bedding or backfill class, no cover, no separation, no
 * thrust block, no test pressure, no compaction, no sling rating, and NOTHING
 * about trench protection in any form.  Where a spec decides it, the line says
 * so and holds an empty box.  Every size on this page is a NOMINAL DIAMETER he
 * read off his own plan and nothing else.
 */
(function () {
  "use strict";

  /* §THE NEUTRAL — every axis leads with one, written as the QUESTION, and the
   * page drops any value starting with an em-dash. A pre-selected default would
   * be the tool choosing for him; a printed value nobody picked would be the
   * tool putting words in his message. */
  function n(q) { return "— " + q + " —"; }
  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }

  /* WHERE IT GOES, and it is not a floor and not a side of a building. A dirt
   * job has no building yet. Pipe wants STRINGING along the run so the crew
   * handles it once; structures want to land inside the boom's reach of the
   * hole they drop into; stone wants to be somewhere a loader can get a bucket
   * into without crossing the open trench. A load put down in the wrong place
   * on a dirt job is not carried twice — it is picked up with a machine, which
   * is a man and an hour. */
  var DROPS = ["String it along the run",
               "Next to the hole — as close as the boom gets",
               "Stockpile / laydown",
               "On the haul-road side, clear of the run",
               "At the gate — we'll move it",
               "By the trailer",
               "In the yard — we're picking this one up",
               "Split it — see the note"];
  function where() { return ax("Where", [n("where does it go")].concat(DROPS), true); }

  /* NOMINAL DIAMETER OFF HIS OWN PLAN. Not a class, not a wall thickness, not a
   * pressure rating, not a cover. Two ladders because a 3/4 in service tap and a
   * 42 in storm run are not on the same list, and one combined ladder would be
   * the wall of options §THE GATE forbids. */
  var MAIN = ["4 in", "6 in", "8 in", "10 in", "12 in", "15 in", "18 in", "21 in",
              "24 in", "30 in", "36 in", "42 in", "48 in",
              "Bigger — see the note", "More than one size — see the note"];
  var SVC = ["3/4 in", "1 in", "1-1/4 in", "1-1/2 in", "2 in", "3 in", "4 in", "6 in",
             "More than one size — see the note"];
  function dia() { return ax("Size", [n("what size")].concat(MAIN)); }
  function svc() { return ax("Size", [n("what size")].concat(SVC)); }

  /* The one flag that repeats: this piece lands on somebody else's pipe. */
  function tie() { return [{ k: "tie", label: "Ties into what's already in" }]; }

  window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

  window.TOOLKIT_ITEMS.mat = {
    drops: DROPS,

    cats: [
      {
        id: "call",
        name: "What are you calling in?",
        docName: "The call",
        hint: "Paste your whole list if you keep one — one line each. Count it the way you say it: 20 joint, 300 ft, 4 ton, 2 roll. Then set where it goes on the heavy stuff, and tick anything that's going in the hole.",
        writein: true,
        items: []
      },

      {
        id: "pipe",
        name: "Pipe",
        docName: "Pipe",
        hint: "By the JOINT or by the FOOT — say which, because twenty joints and twenty feet are two different trucks. The class, the wall and the joint are off YOUR plan; type them in the note. This page doesn't pick one.",
        items: [
          { n: "Gravity sewer pipe — PVC", sub: "BY THE JOINT — SAY THE CLASS AND THE LAYING LENGTH OFF YOUR PLAN", unit: "joint", ditch: true,
            notePlaceholder: "the class, the joint and the laying length your plan calls for — gasketed or solvent",
            flags: tie(), ax: [dia(), where()] },
          { n: "Storm pipe — dual-wall corrugated HDPE", sub: "BY THE JOINT — SAY PERFORATED OR SOLID, AND HOW THE ENDS GO TOGETHER", unit: "joint", ditch: true,
            notePlaceholder: "perforated or solid, and what you want on the ends",
            flags: tie(), ax: [dia(), where()] },
          { n: "Storm pipe — reinforced concrete", sub: "BY THE JOINT — SAY THE CLASS AND THE JOINT OFF YOUR PLAN, AND WHAT'S SETTING IT", unit: "joint", ditch: true,
            notePlaceholder: "the class and the joint off your plan — and say what's on site to set it",
            flags: tie(), ax: [dia(), where()] },
          { n: "Storm pipe — corrugated metal", sub: "BY THE JOINT — SAY THE GAUGE AND THE COATING OFF YOUR PLAN, AND THE BANDS WITH IT", unit: "joint", ditch: true,
            notePlaceholder: "gauge, coating and how many bands",
            ax: [dia(), where()] },
          { n: "Water main — PVC pressure pipe", sub: "BY THE JOINT — SAY THE PRESSURE CLASS OFF YOUR PLAN", unit: "joint", ditch: true,
            notePlaceholder: "the pressure class off your plan — this page doesn't pick one",
            flags: tie(), ax: [dia(), where()] },
          { n: "Water main — ductile iron", sub: "BY THE JOINT — SAY THE CLASS AND THE LINING OFF YOUR PLAN", unit: "joint", ditch: true,
            notePlaceholder: "class, lining, and push-on or mechanical joint",
            flags: tie(), ax: [dia(), where()] },
          { n: "HDPE — fused", sub: "BY THE JOINT OR THE COIL — SAY WHO'S FUSING IT AND WHOSE MACHINE IS COMING", unit: "joint", ditch: true,
            notePlaceholder: "who fuses it, whose machine, and when it lands",
            ax: [dia(), where()] },
          { n: "Service line — poly tubing", sub: "BY THE COIL — SAY THE ROLL LENGTH", unit: "coil", ditch: true,
            flags: tie(), ax: [svc(), where()] },
          { n: "Service line — copper", sub: "BY THE COIL OR THE STICK", unit: "coil", ditch: true,
            flags: tie(), ax: [svc(), where()] },
          { n: "Underdrain / perforated pipe", sub: "BY THE JOINT — SAY SOCKED OR BARE", unit: "joint", ditch: true,
            notePlaceholder: "socked or bare, and which way the holes face",
            ax: [dia(), where()] },
          { n: "Sleeve / casing pipe", sub: "BY THE JOINT OR BY THE FOOT — SAY WHAT'S GOING THROUGH IT", unit: "joint", ditch: true,
            notePlaceholder: "what runs through it, and the spacers and end seals if you want them",
            ax: [dia(), where()] },
          { n: "Conduit for the site electrical", sub: "BY THE STICK — IF IT'S IN YOUR SCOPE. IF IT ISN'T, SAY WHOSE IT IS", unit: "stick", ditch: true,
            notePlaceholder: "whose scope it is, and whether the sweeps and glue come with it",
            ax: [svc(), where()] }
        ]
      },

      {
        id: "fit",
        name: "Fittings, gaskets & lube",
        docName: "Fittings, gaskets & lube",
        hint: "The line that stops a crew is never the pipe — it's the one fitting. And nothing goes together without gaskets and lube, which is the thing nobody puts on the list. Tick TIES INTO on anything landing on pipe that's already in the ground, and say what that is in the header.",
        items: [
          { n: "Bends", sub: "EACH — SAY THE DEGREE AND WHAT'S ON EACH END", unit: "ea", ditch: true,
            notePlaceholder: "the degree, and bell/spigot or MJ on each end",
            flags: tie(), ax: [dia(), where()] },
          { n: "Wyes", sub: "EACH — SAY THE SIZE ON THE BRANCH TOO", unit: "ea", ditch: true,
            notePlaceholder: "branch size and which way it turns",
            flags: tie(), ax: [dia(), where()] },
          { n: "Tees", sub: "EACH — SAY THE SIZE ON THE BRANCH TOO", unit: "ea", ditch: true,
            notePlaceholder: "branch size and what's on the branch end",
            flags: tie(), ax: [dia(), where()] },
          { n: "Reducers / increasers", sub: "EACH — SAY BOTH SIZES", unit: "ea", ditch: true,
            notePlaceholder: "both sizes, in the order the flow goes",
            flags: tie(), ax: [dia(), where()] },
          { n: "Couplings", sub: "EACH — SAY IF IT'S JOINING TWO OF THE SAME OR TWO DIFFERENT THINGS", unit: "ea", ditch: true,
            flags: tie(), ax: [dia(), where()] },
          { n: "Transition / shielded coupling", sub: "EACH — THE ONE FOR TYING INTO SOMETHING THAT ISN'T WHAT YOU'RE LAYING. SAY WHAT'S ON BOTH SIDES", unit: "ea", ditch: true,
            notePlaceholder: "what's on each side — cast, clay, AC, DI, PVC — and the size of each",
            flags: tie(), ax: [dia(), where()] },
          { n: "Caps & plugs", sub: "EACH — FOR THE END YOU'RE STOPPING AT AND FOR THE TEST", unit: "ea", ditch: true,
            ax: [dia(), where()] },
          { n: "Mechanical joint accessory packs", sub: "BY THE SET — GLAND, GASKET, BOLTS. A JOINT WITHOUT ONE IS A JOINT YOU CAN'T MAKE", unit: "set", ditch: true,
            flags: tie(), ax: [dia(), where()] },
          { n: "Restraint / retainer glands", sub: "EACH — SAY WHAT IT'S GOING ON", unit: "ea", ditch: true,
            flags: tie(), ax: [dia(), where()] },
          { n: "Gaskets", sub: "BY THE SET, AND ORDER SPARES — THEY GET CUT, THEY GET DROPPED IN THE MUD AND THEY GET LOST", unit: "set", ditch: true,
            notePlaceholder: "what pipe they're for, and how many spares",
            ax: [dia()] },
          { n: "Pipe lube", sub: "BY THE BUCKET — COUNT IT. NOBODY HAS EVER ORDERED ENOUGH OF THIS", unit: "ea", ditch: true },
          { n: "Solvent cement & primer", sub: "BY THE CAN — SAY THE SIZE OF CAN AND WHAT IT'S FOR", unit: "ea", ditch: true },
          { n: "Saddles / tapping tee", sub: "EACH — SAY WHAT PIPE IT'S GOING ON, NOT WHAT YOU WISH IT WAS", unit: "ea", ditch: true,
            notePlaceholder: "what the existing pipe actually is, and its outside diameter if you've got it",
            flags: tie(), ax: [dia(), where()] },
          { n: "Boots for the structure connection", sub: "EACH — THE PIECE THAT MAKES THE PIPE-TO-STRUCTURE JOINT. ONE PER PIPE, PER STRUCTURE", unit: "ea", ditch: true,
            notePlaceholder: "which structure, and how many pipes come into it",
            ax: [dia()] }
        ]
      },

      {
        id: "str",
        name: "Structures, castings & valves",
        docName: "Structures, castings & valves",
        hint: "BY THE MARK off your plan — MH-4, CB-7, DI-2. A structure ordered as \"a manhole\" is a structure somebody guessed at. And the barrel and the casting are two orders that don't always come on the same truck.",
        items: [
          { n: "Manhole — base & barrel", sub: "BY THE MARK — SAY THE DEPTH TO INVERT OFF YOUR PLAN AND WHICH KNOCKOUTS", unit: "ea", ditch: true,
            notePlaceholder: "the mark off your plan, depth to invert, and which pipes come in at what angle",
            ax: [dia(), where()] },
          { n: "Manhole cone / top slab", sub: "EACH — SAY WHICH ONE OFF YOUR PLAN", unit: "ea", ditch: true,
            ax: [dia(), where()] },
          { n: "Grade rings / adjustment", sub: "EACH — COUNT THEM. THIS IS THE LINE THAT GETS FORGOTTEN AND IT'S THE ONE THAT SETS THE RIM", unit: "ea", ditch: true,
            notePlaceholder: "how much you're making up, in your own words",
            ax: [where()] },
          { n: "Frame & cover", sub: "BY THE SET — SAY WHAT'S CAST IN THE LID: SEWER, STORM, WATER, DRAIN", unit: "set",
            notePlaceholder: "what's cast in the lid, and whether it's bolted",
            ax: [where()] },
          { n: "Catch basin / inlet", sub: "BY THE MARK", unit: "ea", ditch: true,
            notePlaceholder: "the mark off your plan, and which pipes come into it",
            ax: [dia(), where()] },
          { n: "Grate / inlet casting", sub: "BY THE SET — SAY WHICH ONE, AND WHETHER IT SITS IN A CURB OR IN A FIELD", unit: "set",
            ax: [where()] },
          { n: "Area drain / yard box", sub: "EACH", unit: "ea", ditch: true, ax: [dia(), where()] },
          { n: "Cleanout & frame", sub: "EACH — AT GRADE, WHERE YOUR PLAN SHOWS IT", unit: "ea", ditch: true,
            ax: [svc(), where()] },
          { n: "Gate valve", sub: "EACH — SAY THE ENDS OFF YOUR PLAN", unit: "ea", ditch: true,
            notePlaceholder: "the ends off your plan, and which way it opens if the owner cares",
            flags: tie(), ax: [dia(), where()] },
          { n: "Valve box & lid", sub: "BY THE SET — THE BOX AND THE LID ARE TWO PARTS AND ONE OF THEM ALWAYS SHOWS UP MISSING", unit: "set", ditch: true,
            ax: [where()] },
          { n: "Hydrant assembly", sub: "EACH — SAY WHAT'S IN THE ASSEMBLY AND WHAT ISN'T", unit: "ea", ditch: true,
            notePlaceholder: "shoe, barrel, valve, boot — say what's included and what you're ordering separately",
            flags: tie(), ax: [dia(), where()] },
          { n: "Tapping sleeve & valve", sub: "BY THE SET — FOR THE TIE-IN. SAY WHAT THE EXISTING MAIN ACTUALLY IS", unit: "set", ditch: true,
            notePlaceholder: "what the existing main is and its outside diameter — and who's making the tap",
            flags: tie(), ax: [dia(), where()] },
          { n: "Corp stop, curb stop & box", sub: "EACH — SAY THE SIZE AND WHAT THE MAIN IS", unit: "ea", ditch: true,
            flags: tie(), ax: [svc(), where()] },
          { n: "Meter box", sub: "EACH — SAY WHOSE STANDARD IT'S TO. THAT'S THEIRS TO APPROVE, NOT OURS", unit: "ea", ditch: true,
            ax: [where()] }
        ]
      },

      {
        id: "rock",
        name: "Stone, sand & fill",
        docName: "Stone, sand & fill",
        hint: "By the TON or by the YARD, and they are not the same number — say which one you mean. If it's coming off a particular pit, say so; if somebody else is hauling it, say who.",
        items: [
          { n: "Bedding stone", sub: "BY THE TON — SAY THE SIZE YOUR PLAN CALLS FOR. THIS PAGE DOESN'T PICK ONE", unit: "ton", ditch: true,
            notePlaceholder: "the size off your plan, in your own words",
            ax: [where()] },
          { n: "Backfill material over the pipe", sub: "BY THE TON — OFF YOUR PLAN AND YOUR GEOTECH, NOT OFF THIS PAGE", unit: "ton", ditch: true,
            notePlaceholder: "what your plan calls for — this page doesn't specify it",
            ax: [where()] },
          { n: "Drain rock", sub: "BY THE TON", unit: "ton", ditch: true, ax: [where()] },
          { n: "Sand", sub: "BY THE TON OR THE YARD — SAY WHICH", unit: "ton", ditch: true, ax: [where()] },
          { n: "Crushed base", sub: "BY THE TON — SAY THE SPEC OFF YOUR PLAN", unit: "ton", ax: [where()] },
          { n: "Import fill", sub: "BY THE LOAD OR THE YARD — SAY WHERE IT'S COMING FROM AND WHO'S TESTING IT", unit: "load", ditch: true,
            notePlaceholder: "the source, and who's taking the samples",
            ax: [where()] },
          { n: "Riprap", sub: "BY THE TON — SAY THE SIZE OFF YOUR PLAN", unit: "ton", ax: [where()] },
          { n: "Bagged mix for a collar", sub: "BY THE BAG", unit: "bag", ditch: true, ax: [where()] },
          { n: "Cold patch / temporary surfacing", sub: "BY THE TON OR THE BAG — FOR WHAT YOU'RE PUTTING BACK BEFORE YOU LEAVE TONIGHT", unit: "ton",
            ax: [where()] }
        ]
      },

      {
        id: "wrap",
        name: "Fabric, tape & tracer",
        docName: "Fabric, tape & tracer",
        hint: "By the ROLL — and this is the section that costs a re-dig. Tracer wire and detectable tape are the two cheapest lines on the whole call and the only two you cannot add once the dirt is back.",
        items: [
          { n: "Detectable warning tape", sub: "BY THE ROLL — SAY THE COLOUR FOR WHAT'S UNDER IT, AND THE FOOTAGE ON A ROLL", unit: "roll", ditch: true,
            notePlaceholder: "what it's going over, the colour, and the footage per roll",
            ax: [where()] },
          { n: "Tracer wire", sub: "BY THE ROLL — AND THE SPLICES AND ACCESS BOXES WITH IT. A WIRE NOBODY CAN GET A SIGNAL ONTO IS A WIRE YOU DIDN'T INSTALL", unit: "roll", ditch: true,
            notePlaceholder: "the gauge and jacket off your plan, and the footage per roll",
            ax: [where()] },
          { n: "Tracer splice kits & connectors", sub: "COUNT THEM — ONE PER SPLICE PLUS THE ONES YOU'LL DROP", unit: "ea", ditch: true },
          { n: "Tracer access boxes", sub: "EACH — THE END THAT MAKES THE WIRE WORTH INSTALLING", unit: "ea", ditch: true, ax: [where()] },
          { n: "Marker balls / markers", sub: "EACH — SAY WHAT UTILITY THEY'RE FOR", unit: "ea", ditch: true },
          { n: "Filter fabric / geotextile", sub: "BY THE ROLL — SAY WOVEN OR NON-WOVEN AND THE ROLL WIDTH", unit: "roll", ditch: true,
            notePlaceholder: "woven or non-woven, and the roll width and length",
            ax: [where()] },
          { n: "Geogrid", sub: "BY THE ROLL — SAY THE ROLL SIZE", unit: "roll", ditch: true, ax: [where()] },
          { n: "Silt fence", sub: "BY THE ROLL — AND THE STAKES WITH IT", unit: "roll", ax: [where()] },
          { n: "Erosion blanket / wattle", sub: "BY THE ROLL — SAY THE LENGTH AND THE STAPLES", unit: "roll", ax: [where()] },
          { n: "Inlet protection", sub: "EACH — ONE FOR EVERY STRUCTURE YOU JUST SET", unit: "ea", ax: [where()] },
          { n: "Poly & concrete washout", sub: "BY THE ROLL — SAY WHAT SIZE", unit: "roll", ax: [where()] },
          { n: "Marker posts", sub: "BY THE BUNDLE — SAY THE COLOUR AND WHAT GOES ON THE DECAL", unit: "bundle", ax: [where()] }
        ]
      },

      {
        id: "crew",
        name: "What the crew needs to put it in",
        docName: "What the crew needs to put it in",
        hint: "Half a call is the half nobody writes down. Pipe on the ground with nothing to cut it, lube it or shoot grade with is a morning gone and a machine sitting.",
        items: [
          { n: "Pipe saw + blades", sub: "SAY WHAT YOU'RE CUTTING — THE BLADE FOR DUCTILE ISN'T THE BLADE FOR PVC",
            notePlaceholder: "what you're cutting, and how many blades" },
          { n: "Laser, grade rod, bench", sub: "SAY WHAT'S COMING AND WHOSE IT IS", ax: [where()] },
          { n: "Marking paint & keel", sub: "BY THE CASE — SAY THE COLOUR", unit: "ea" },
          { n: "Shovels, bars, tampers", sub: "COUNTS ONLY" },
          { n: "Compactor — jumping jack or plate", sub: "SAY DELIVERED OR YOU'RE PICKING IT UP. HOW IT'S RUN IS OFF YOUR OWN PLAN AND YOUR GEOTECH, NOT OFF THIS PAGE",
            notePlaceholder: "which one, when it lands and when it leaves", ax: [where()] },
          { n: "Pump & hose for the water", sub: "SAY THE HOSE LENGTH AND WHERE IT'S DISCHARGING — THAT PART IS SOMEBODY'S PERMIT, NOT OURS",
            notePlaceholder: "size, hose length, and where it goes — and who owns that permission", ax: [where()] },
          { n: "Fuel & DEF", sub: "SAY WHAT AND HOW MUCH" },
          { n: "Chokers, slings, lift hooks", sub: "FOR THE STRUCTURES — SAY WHAT YOU'RE PICKING. THE RATING IS OFF THE TAG ON THE SLING, NEVER OFF THIS PAGE",
            notePlaceholder: "what you're picking, and how many legs" },
          { n: "Road plates", sub: "COUNTS ONLY — SAY WHAT THEY'RE COVERING AND WHO'S SETTING THEM", unit: "ea", ax: [where()] },
          { n: "Cones, barricades, signs", sub: "COUNTS ONLY — THE TRAFFIC PLAN IS SOMEBODY'S TO NUMBER AND IT ISN'T THIS PAGE", ax: [where()] },
          { n: "Poly & sandbags for overnight", sub: "COUNTS ONLY", ax: [where()] },
          { n: "Water for the dust", sub: "SAY WHO'S BRINGING IT AND HOW OFTEN" }
        ]
      },

      {
        id: "back",
        name: "What goes back, and what you're picking up",
        docName: "What goes back, and what you're picking up",
        hint: "The half of the call that's worth money and never gets made. Pipe you didn't lay, empty reels and the plates still sitting on the road are all somebody's deposit and all of it is on your job.",
        items: [
          { n: "Take the leftover pipe back", sub: "SAY ROUGHLY HOW MANY JOINTS AND WHETHER ANY OF IT'S BEEN CUT", unit: "joint" },
          { n: "Take the empty pallets and reels back", sub: "COUNTS ONLY", unit: "ea" },
          { n: "Pick up the plates", sub: "WHEN THE ROAD'S BACK — SAY WHEN THAT IS" },
          { n: "Pick up the compactor / the pump", sub: "WHEN YOU'RE DONE WITH IT" },
          { n: "Credit the fittings we didn't open", sub: "SAY WHAT'S STILL IN THE BOX — AN OPENED BOX ISN'T GOING BACK" }
        ]
      }
    ],

    /* A pasted line gets the same controls as a picked one. The DITCH flag is on
     * the write-in and NOT on the picked rows, and that asymmetry is deliberate:
     * a catalogue line already knows whether it gets buried (`ditch` on the item,
     * above), but a line he typed is a sentence only he can classify. It is
     * OFFERED, never demanded — masonry's page wrote the rule that a write-in is
     * his sentence and not our row, and a page that scolds a man for not
     * classifying his own note is a page he stops pasting into. */
    writeinAx: [where()],
    writeinFlags: [{ k: "ditch", label: "Goes in the ditch" }]
  };
})();

/* ── TAG_ES — the directed-work tag's vocabulary en español (2026-08-23). ─────
 *
 * Every entry carries its own en-twin — nothing paired by index, nothing that can
 * drift apart. The page composes what the document prints ("ES (EN)") from the
 * pair; a <select> value carries its twin itself, house style "MAYORDOMO (FOREMAN)".
 * Gated: tools/toolkit-gates/lang-layer.mjs asserts every twin matches an EN
 * option verbatim, on every page that mounts shared/lang.js. */
window.TOOLKIT_ITEMS.tag_es = {
  "classes": [
    { "es": "— clase (class)", "en": "— class" },
    { "es": "OPERADOR (OPERATOR)", "en": "OPERATOR" },
    { "es": "TUBERO (PIPELAYER)", "en": "PIPELAYER" },
    { "es": "PEÓN (LABORER)", "en": "LABORER" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" },
    { "es": "CHOFER (TRUCK DRIVER)", "en": "TRUCK DRIVER" },
    { "es": "CHECADOR DE NIVEL (GRADE CHECKER)", "en": "GRADE CHECKER" },
    { "es": "APRENDIZ (APPRENTICE)", "en": "APPRENTICE" }
  ],
  "how": [
    { "es": "En persona, en la zanja", "en": "Face to face at the ditch" },
    { "es": "Mensaje de texto", "en": "Text message" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me lo dijeron en la junta de la mañana", "en": "Told to me at the morning huddle" },
    { "es": "Radio, en el canal de la obra", "en": "Radio on the site channel" },
    { "es": "Correo", "en": "Email" },
    { "es": "Planos marcados que me entregaron en campo", "en": "Marked-up set handed to me in the field" },
    { "es": "Cambiaron la pintura o las estacas en el terreno", "en": "Paint or stakes changed on the ground" },
    { "es": "Los de otra compañía me dijeron que ya estaba autorizado", "en": "A different trade told me he'd cleared it" }
  ],
  "notin": [
    { "es": "No es un precio", "sub": "Solo horas, viajes y cantidades. Sin tarifa, sin total y sin un solo dólar en ninguna parte.", "en": "Not a price" },
    { "es": "No es un CO ni un reclamo", "sub": "Esto dice que nos lo ordenaron y qué tomó. Se vuelve cambio cuando las oficinas lo ponen en papel, y el derecho a cobrarlo sale de la carta de ellos, no del mayordomo.", "en": "Not a change order and not a claim" },
    { "es": "No es el reporte del laboratorio", "sub": "Densidad, humedad y suelos son el aparato de ellos y el número de ellos. Nosotros escribimos que estuvimos parados esperando; nunca escribimos si pasó o no.", "en": "Not the lab's report" },
    { "es": "No es el as-built del topógrafo", "sub": "Él lo levanta, él lo sella y él le pone número. Nosotros solo decimos qué no pudimos tapar hasta que él vino.", "en": "Not the surveyor's as-built" },
    { "es": "No es un locate ni un ticket", "sub": "El número y el plazo son del 811. Nada de aquí renueva un ticket, libera uno, ni dice que una marca esté buena.", "en": "Not a locate and not a ticket" },
    { "es": "No es decisión de si la zanja era segura para meterse", "sub": "Eso es de la persona competente, en la obra, en persona, frente al suelo de verdad. No es una línea en un teléfono y no va en este vale.", "en": "Not a call on whether the hole was safe to be in" },
    { "es": "No es un cambio de diseño", "sub": "Fondo, cama, caja, pendiente, relleno — nada de eso se decide aquí. Lo que sea de diseño sube por el GC en su formato.", "en": "Not a design change" },
    { "es": "No es un reclamo por daño", "sub": "Una línea a la que le pegaron va en el papel de la compañía de servicios, ahí mismo, por su proceso. No va montada en esto.", "en": "Not a damage claim" },
    { "es": "No es el papel ambiental", "sub": "El material contaminado o regulado va en su propio manifiesto con su propia gente, y nosotros no volvemos a escribir lo que ya viene impreso ahí.", "en": "Not the environmental paper" },
    { "es": "No es el reporte diario del GC", "sub": "Ellos llevan el suyo y le ponen número. Este es el nuestro y se sostiene solo.", "en": "Not the GC's daily" },
    { "es": "No es un dictamen de causa", "sub": "Escribimos qué excavamos y quién nos ordenó excavarlo. Por qué algo falló, se asentó o estaba donde estaba, eso lo deciden otros.", "en": "Not a finding of cause" },
    { "es": "No es un reporte de seguridad ni de incidente", "sub": "Lesiones, casi-accidentes y equipo van en su propio papel, ahí mismo, por el canal que toca.", "en": "Not a safety or incident report" },
    { "es": "No es entrega ni aceptación", "sub": "Firmar que se le avisó no es aceptar el trabajo, liberar a nadie, ni decir que ya quedó.", "en": "Not turnover or acceptance" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas antes de tapar", "en": "In this message — shot before we covered it" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "Súper del GC", "en": "GC superintendent" },
    { "es": "Nuestro súper general", "en": "Our own general super" },
    { "es": "PM del GC", "en": "GC project manager" },
    { "es": "Nuestro PM o la oficina", "en": "Our PM or the office" },
    { "es": "Mayordomo de otro oficio en nuestra zanja", "en": "Another trade's foreman in our ditch" },
    { "es": "El topógrafo o el representante del ingeniero en la obra", "en": "The surveyor or the engineer's rep on site" },
    { "es": "Representante del dueño o el CM", "en": "Owner's rep or construction manager" },
    { "es": "Súper de campo del builder (fraccionamiento o casa custom)", "en": "Builder's field super (tract or custom home)" },
    { "es": "El dueño de la casa", "en": "Homeowner" },
    { "es": "Inspector de la compañía de servicios en la obra", "en": "Utility owner's inspector on site" },
    { "es": "Inspector de la ciudad o del condado en la obra", "en": "Jurisdiction inspector on site" }
  ],
  "why": [
    { "es": "Roca — el bote ya no bajó", "sub": "Tuvimos que trabajarla con algo que no cotizamos, o de otra manera, para llegar al fondo que nos dieron.", "en": "Rock — the bucket quit going down" },
    { "es": "Agua en la zanja", "sub": "La bombeamos, la sacamos mojada, la trabajamos dos veces, o la dejamos secar antes de poder meter nada.", "en": "Water in the hole" },
    { "es": "Material malo — no aguantaba", "sub": "Tierra mojada, lodosa o con basura que no se sostenía. Nos ordenaron sacarla y meter otra cosa, o trabajarla así como estaba.", "en": "Unsuitables — it wouldn't hold" },
    { "es": "Una línea enterrada que nadie marcó", "sub": "No estaba en el plano ni en la pintura. Paramos, escarbamos a mano para hallarla, esperamos, o le sacamos la vuelta.", "en": "A line in the ground nobody marked" },
    { "es": "Las marcas estaban mal", "sub": "Excavamos donde decía la pintura y no estaba — o estaba, pero no donde la marcaron. Escarbar a mano y tiempo que nadie cotizó.", "en": "The marks were off" },
    { "es": "Obra vieja que nadie nos avisó", "sub": "Losa, zapata, tanque, escombro o una línea abandonada en nuestra excavación que no venía en nada de lo que cotizamos.", "en": "Old work nobody told us about" },
    { "es": "El fondo siguió bajando", "sub": "Excavamos más abajo de lo que marcaban los planos para llegar a lo que alguien en la obra pidió.", "en": "Bottom kept going down" },
    { "es": "Parados mientras otra compañía salía de nuestra zanja", "sub": "Cuadrilla y máquina en la obra, esperando a que otro terminara en la zanja para la que ya teníamos la gente.", "en": "Standing while another outfit got out of our ditch" },
    { "es": "La dejamos abierta para una prueba, un levantamiento o una revisión", "sub": "Lista para tapar y nos dijeron que la dejáramos hasta que llegara alguien — el topógrafo, el laboratorio, un inspector, el dueño.", "en": "Held it open for a test, a shot or a look" },
    { "es": "Volvimos a abrir un tramo que ya habíamos tapado", "sub": "La tierra ya estaba adentro y el trabajo de alguien no. Lo abrimos otra vez porque alguien lo dijo.", "en": "Re-dug a run we had already closed" },
    { "es": "El nivel o el trazo cambió después de que ya lo habíamos hecho", "sub": "Estacas que ya no estaban, offsets cambiados, o un juego de planos nuevo que llegó cuando ya habíamos trabajado con el primero.", "en": "Grade or layout moved after we built to it" },
    { "es": "Tierra que entró o salió sin cotizar", "sub": "Material de banco que se trajo o sobrante (spoils) que se sacó sin estar en el alcance, o un stockpile que se movió dos veces porque cambió el plan.", "en": "Dirt in or dirt out nobody bid" },
    { "es": "El acceso o la ruta de acarreo cambió después de movilizarnos", "sub": "Otro portón, acarreo más largo, placas, un desvío u horas que no teníamos cuando cotizamos la movilización.", "en": "Access or the haul route changed after we mobed" },
    { "es": "Nos ordenaron trabajar con mal tiempo", "sub": "Seguirle, bombear, tapar con lona, o regresar un día que ya habíamos cancelado.", "en": "Told to work the weather" }
  ]
};
