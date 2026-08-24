/* FRAMING & DRYWALL FIELD TOOLKIT — VOCABULARY DATA.
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Classifications,
 * reason lists, gate ladders and pick options live HERE — never in the identity
 * config and never inline in a tool page.
 *
 * TWO HARD INVARIANTS (§SAFETY), and this trade puts the sharpest edge on both:
 *
 *   ZERO BRAND NAMES. Every hand in this trade says one manufacturer's name a
 *   hundred times a day instead of the word "board". That is exactly why the word
 *   is checked and never printed. It is BOARD and it is ROCK; it is MUD, never
 *   joint compound; it is BEAD, never accessories.
 *
 *   NOTHING IS COMPUTED, SIZED OR RATED. No hour rating, no listed assembly, no
 *   STC number, no limiting height, no gauge-vs-span, no screw spacing, no
 *   nailing pattern, no R-value, and above all NO MOUNTING HEIGHT — not as a
 *   value, not as a default, not as a greyed placeholder beside a chip. A
 *   placeholder IS a recommendation. Heights are the single most dangerous number
 *   in this trade's paperwork because a wrong one is buried behind rock, so every
 *   page that takes one prints the same plain line: these are your numbers, we
 *   don't know them and we won't guess.
 *
 * BOTH WORDS, EVERYWHERE. Commercial says BACKING, the wood side says BLOCKING,
 * and they are the same thing. Both are printed throughout on purpose — a page
 * that says only one of them tells half this trade family it wasn't written for
 * them.
 */

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Everything here is something the man PICKS,
 * never something the page decides. No rates, no totals, no arithmetic.
 *
 *  · WHAT IS **NOT** IN THIS TAG is the field this trade fights about hardest,
 *    and its lines are specific to closing walls: a cut-in is not the patch, the
 *    patch is not the tape and sand, and none of the three is the second side
 *    that was always contract.
 *  · SAY TAG OR EXTRA, NEVER FORM. "Get a tag on it." "That's an extra."
 *  · THE ORDER OF THE OUTPUT IS THE ORDER OF THE YELLOW COPY. The triplicate book
 *    is contractual and is never going away, so this page only survives if he can
 *    read it straight off while he fills the paper one (§THE SYSTEM OF RECORD).
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC super",
    "GC assistant super / field engineer",
    "GC PM",
    "Our GF or PM",
    "Owner's rep / facilities",
    "Architect or engineer in the field",
    "Another trade's foreman",
    "Inspector"
  ],
  "how": [
    { "v": "Told me on the walk" },
    { "v": "Text / email" },
    { "v": "Phone call" },
    { "v": "Marked-up print handed to me" },
    { "v": "Said it in the trailer meeting" }
  ],
  "why": [
    { "name": "Not on my set" },
    { "name": "Drawing changed after I framed it" },
    { "name": "Backing nobody asked for before the wall closed", "sub": "it's a cut-in now" },
    { "name": "Another trade's work is in my wall line" },
    { "name": "Damage by others — we opened and closed it" },
    { "name": "Existing conditions", "sub": "not what the as-builts show" },
    { "name": "Inspector wouldn't pass it as drawn" },
    { "name": "Told to work out of sequence" },
    { "name": "Held for somebody, then told to close it anyway" }
  ],
  "notin": [
    { "name": "This tag is the cut-in only", "sub": "not the contract rock on that wall" },
    { "name": "Patch, tape and sand not included", "sub": "after your guy comes back through" },
    { "name": "No lift, scaffold or stilt time", "sub": "unless it's listed below" },
    { "name": "Not the backing already on the original list" },
    { "name": "Not the second-side close — that's contract" },
    { "name": "No stand-by hours for the crew that waited" },
    { "name": "Not a delay claim and not a schedule impact" },
    { "name": "No scrap haul or cleanup for another trade's mess" }
  ],
  "classes": ["— class", "JOURNEYMAN", "APPRENTICE", "FOREMAN"],
  "pics": [
    { "v": "In this message — shot before we closed it" },
    { "v": "None" }
  ]
};


/* ── THE CROSS-BOUNDARY ASK (shape #3 — shared/rowlog.js) ──────────────────
 * The vocabulary for rough-in-request.html — "Before I Close It".
 *
 * THIS TRADE'S ASK IS THE MIRROR OF EVERY OTHER TRADE'S. The other six ask
 * somebody to leave them a hole, a sleeve or a piece of wood. This crew asks
 * everybody to GET OUT OF THE WALL, because it is the one trade that performs
 * the irreversible act: closing it. So the gates below are not generic
 * milestones, they are the countdown to a wall that cannot be reopened without
 * a saw, and the closing line of the document says so.
 *
 * The bars hold exactly as they do on the other six: no size, no height, no
 * rating, no code reference and no money. Every spec is a PHRASING he picks.
 * `who` and `by` are the USUAL aim and the USUAL gate — they only ever fill a
 * field left empty and never overwrite a pick (§SCARS — a default is a claim).
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before I Close It",
  eyebrow: "Framing & drywall · you → the trades in your wall",
  lede: "Everything that has to be in, marked, moved or sized before this wall or this lid closes — who owes it, where it is, and the gate it has to beat.",
  docSubject: "Before we close it — what I need out of your trade",
  docSubjectWith: "Before we close it — what I need from {to}",
  closing: "That's what I need in before it closes. Text me back what you'll hit and what you won't — while it's still an open wall. After we rock it, it's a cut-in and a patch, and that's a tag for somebody.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> walls. This page sizes nothing, sets no height, rates no assembly and doesn't know what the code, the architect or the engineer requires &mdash; verify all of that against your own set. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C",
  phOff: "A-501 rev 3",
  phFrom: "Mike — Apex Interiors",
  phArea: "L3 west — then it's a button",
  areaLabel: "Level / room / column line",

  who: [
    { v: "gc-super", label: "GC super" },
    { v: "ec", label: "EC foreman" },
    { v: "mech", label: "Mech / HVAC" },
    { v: "plumber", label: "Plumber / sprinkler" },
    { v: "lv", label: "LV / fire alarm" },
    { v: "av", label: "AV" },
    { v: "casework", label: "Casework" },
    { v: "doors", label: "Doors & hardware" },
    { v: "grid", label: "Grid / ceilings" },
    { v: "painter", label: "Painter" }
  ],

  /* EARLIEST FIRST — this is the order a wall actually disappears in, and it is
     why grouping by "When" reads as a countdown instead of a pile. NOT the GC's
     schedule milestones: dry-in and hoist are somebody else's gates. These are
     the ones this crew is standing in front of. */
  milestones: [
    { v: "layout", label: "Before we snap layout" },
    { v: "studs", label: "Before we stand studs" },
    { v: "soffit", label: "Before we frame the soffit" },
    { v: "inspect", label: "Before frame inspection" },
    { v: "one-side", label: "Before we close one side" },
    { v: "second-side", label: "Before second side goes on" },
    { v: "lid", label: "Before the lid closes" },
    { v: "grid-start", label: "Before the grid guy starts" },
    { v: "tape", label: "Before we tape" },
    { v: "paint", label: "Before it goes to paint" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "get-out", label: "Get out of my wall", who: "ec", by: "one-side", specs: [
      "Rough done in these walls so I can one-side them",
      "Cable off the stud face — it belongs in the punch-outs",
      "Nothing running flat across the flanges where my screws go",
      "Pipe or duct is proud of the face — back it up or I furr it",
      "Pull your gang boxes and carts out of the rooms we're rocking",
      "Tell me the day you're out and I'll put it on the rock list"
    ] },
    { v: "backing-size", label: "Backing — give me a size and a height", who: "av", by: "studs", specs: [
      "What it's for, how wide, how high off the floor — bottom and top",
      "Weight of what's hanging on it, so I put in the right thing",
      "Give me a range and I'll run it continuous, easier for both of us",
      "Wood or steel — tell me which you want to hit",
      "Send it as one list, not four texts across three weeks",
      "Mark the wall and I'll shoot it off your mark"
    ] },
    { v: "come-look", label: "Come look before I close it", who: "av", by: "one-side", specs: [
      "Two minutes at the wall now, or a cut-in and a patch later",
      "Walk the floor with me Thursday morning before we hang",
      "It's in where you asked — confirm it and I'll close it",
      "Photo's coming — tell me yes or tell me today"
    ] },
    { v: "rings", label: "Rings and boxes on my layout", who: "ec", by: "one-side", specs: [
      "Ring depth for my layer count, flush to the face of board",
      "On my layout — a few inches off the stud costs me two cuts",
      "Tell me the ring depth so my cut-out man cuts it right the first time",
      "Rings on before I rock, not while my hangers are standing there",
      "Don't cut or notch my studs — find me and we'll header it"
    ] },
    { v: "wall-depth", label: "Tell me the wall depth you need", who: "plumber", by: "layout", specs: [
      "If it's a big stack I'm furring it out — I need to know before I lay out",
      "Carrier is landing where my stud goes — one of us moves",
      "Confirm the wet wall before I snap it, not after I stand it",
      "Tell me now if anything is wall-hung and heavy",
      "Panel deeper than my wall — it moves or I furr the whole run"
    ] },
    { v: "duct-elev", label: "Final duct elevation before I frame it", who: "mech", by: "soffit", specs: [
      "I build the box around your duct and I only build it once",
      "Duct and hangers out of my wall line",
      "Trunk in the chase and insulated before I rock the chase",
      "Boxes, dampers and valves located before rock",
      "Sleeves and openings in the liner side — that's a one-shot wall"
    ] },
    { v: "access", label: "Access panel — where and what size", who: "mech", by: "lid", specs: [
      "Where you need to get back in, and how big, before the lid",
      "At the valve, the damper, the cleanout — name each one",
      "In the lid, not in my finished wall",
      "Big enough for an arm and a wrench",
      "Give me the whole list at once, not one a week",
      "After it's closed it's a cut-in and a patch"
    ] },
    { v: "above-lid", label: "Everything above the lid done and signed", who: "gc-super", by: "lid", specs: [
      "Inspected and signed before I frame it, not after",
      "Tested and holding — I'm not opening a lid to chase a weep",
      "Drops at final ceiling height and armovers set",
      "Anything above it complete, or tell me and I'll hold it",
      "Cover-up sign-off before I close it"
    ] },
    { v: "hold-it", label: "Tell me what to hold open", who: "gc-super", by: "one-side", specs: [
      "Which walls stay open and who told me — in writing, today",
      "Hold the second side till your gear lands",
      "Leave the opening for equipment that won't fit through a door",
      "If you need it held past Thursday, say so before the load comes",
      "Anything held with no date on it becomes my production problem"
    ] },
    { v: "dimension", label: "I need a dimension", who: "gc-super", by: "layout", specs: [
      "Standing at the line and it doesn't fit — I need a number today",
      "Two dimensions on the set disagree with each other",
      "Ceiling height and exactly where the hard lid stops",
      "Confirm the wall type before I stand it",
      "Get it answered before I stock the floor, not after"
    ] },
    { v: "frames", label: "Frames on site and right", who: "doors", by: "studs", specs: [
      "On site by the date I frame that opening",
      "Right handing for the wall I'm building",
      "Right throat — the wrong one doesn't go on this wall",
      "Anchors in the box with the frame",
      "Knock-down or welded — tell me before my crew opens it",
      "Any change to an opening in writing, before I've framed it"
    ] },
    { v: "casework", label: "Where the uppers land", who: "casework", by: "studs", specs: [
      "Where they land and how high — I'll run continuous instead of a cleat",
      "Filler and scribe conditions before I stand the wall",
      "Anything heavy and wall-hung is backing, not a cleat in the rock",
      "Send the elevation and I'll back the whole run"
    ] },
    { v: "grid-line", label: "Where your grid meets my lid", who: "grid", by: "grid-start", specs: [
      "Ceiling height and where the hard lid stops",
      "Where your mains land so my hangers aren't fighting your wire",
      "Don't hang grid off my soffit framing without asking",
      "Tell me your start date so my lids are done ahead of you"
    ] },
    { v: "clear-floor", label: "Clear the floor for the load", who: "gc-super", by: "one-side", specs: [
      "Boom or hoist window, and the rooms empty when it lands",
      "A route in — I'm not carrying a floor of board down a corridor",
      "Nothing stacked on my layout lines",
      "Dumpster and a scrap route before we start hanging",
      "Temp heat and light before I put a taper in there"
    ] },
    { v: "insulation", label: "Batts and safing before I close", who: "gc-super", by: "second-side", specs: [
      "Batts in the walls on my rock list before I close them",
      "Head of wall and safing before the second side",
      "Say clearly which of us owns the caulk at the deck",
      "Tell me the night before if you can't hit it"
    ] },
    { v: "call-it", label: "Call the inspection", who: "gc-super", by: "inspect", specs: [
      "Get it called and signed — I can't close a wall on a maybe",
      "Walk it with me first so nothing gets kicked back",
      "Tell me the time so I've got a man there",
      "Signed sticker, not a verbal"
    ] }
  ]
};


/* ── THE RETURN LEG (answer-back.html) ────────────────────────────────────
 * The reply to somebody else's cross-boundary request. The ENGINE is
 * shared/rowlog.js; this block is only the words this trade says.
 *
 * For THIS trade the return leg is the busiest page on the hub, because five of
 * the six other toolkits point their ask at this crew. The list he pastes here
 * is very often one of ours, generated on another trade's hub.
 *
 * The gates it offers for "when" are NOT here on purpose: they are
 * TOOLKIT_ROUGHIN.milestones above, and one list that two tools read cannot
 * drift out of step with itself.
 */
window.TOOLKIT_ANSWER = {
  toolName: "What I'll Put In",
  eyebrow: "Framing & drywall · them → you → back",
  lede: "Somebody sent you a list — backing, holds, access, keep-out. Line it up, give each one a yes, a no, or a question, and a date on every yes, then send it back in one message.",
  docSubject: "what I'll put in",
  closing: "That's the yes, the no, and the when. Anything I flagged I need a size or a height on before that wall closes — once it's rocked, it's a cut-in and a patch and we're both writing a tag.",
  phJob: "Building C", phTo: "Dave — AV foreman", phFrom: "Mike — Apex Interiors", phOff: "A-501 rev 3",
  paste: "Building C — backing we need — Aug 9\n\nJob: Building C\nFrom: Dave — AV foreman\n\nRm 314 · backing behind the TV on the north wall\nRm 316 · same, and leave the wall open till my box is in\nCorr 3C · plywood at the rack wall, floor to 8"
};


/* ── THE BACKING LEDGER (whats-in-the-wall.html) ──────────────────────────
 * The vocabulary for this trade's SIGNATURE tool, and the one page on the whole
 * program that no other trade could write.
 *
 * WHY IT IS THE PIN. Five of the six shipped toolkits name this crew as the
 * party they chase for backing. Every one of those conversations happens TWICE:
 * once in June when the AV foreman wants it, and once in October when he swears
 * it was never put in. In October the man with the list wins, and until now
 * there was no list — backing gets ASKED five ways (a text, a marked print, a
 * guy pointing at a stud) and RECORDED zero. Its only real competitor is a can
 * of keel on the stud, which loses for exactly one reason: the keel gets covered
 * and the list doesn't.
 *
 * THE HEIGHT FIELD IS THE DANGEROUS ONE and it is deliberately naked — no
 * options, no chips, no placeholder number, no example. A seeded "48" here is a
 * mounting-height recommendation for a television, published by people who have
 * never seen the wall, and it would be buried behind rock before anybody caught
 * it (§SAFETY). He types his numbers or the field stays empty.
 */
window.TOOLKIT_BACKING = {
  toolName: "What's In The Wall",
  eyebrow: "Framing & drywall · what went in, before it disappears",
  lede: "Log the backing and blocking as it goes in — what it's for, what went in, who asked, how high. Then send one message that says what's behind that rock, and that anything not on the list isn't in there.",
  docSubject: "backing and blocking — what's in the wall",
  docSubjectWith: "backing in — {to}",
  closing: "Walk it with me before we close it. After we rock it, it's a cut-in and a patch.",
  warn: "<b>These are your numbers.</b> We don't know them and we won't guess &mdash; nothing on this page sets a height, a size, a fastener or a spacing, and nothing here is a code reference or an approved detail. It's a record of what <i>you</i> put in and who asked for it.",
  phJob: "Building C",
  phOff: "A-501 rev 3 — or off their texts and wall marks",
  phFrom: "Mike — Apex Interiors",
  phArea: "L3 west — then it's a button",

  /* WHAT IT'S FOR — in field words, both halves of the family. Commercial rows
     first because that is where the volume is, residential right behind. The AV
     spec word "display" is banned on purpose: it is a TV. */
  purpose: [
    "TV / monitor",
    "Projector or screen",
    "Marker board / tack board",
    "Casework & uppers",
    "Wall-hung sink or carrier",
    "Grab bar",
    "Urinal screen / partition",
    "Mirror & toilet accessories",
    "Handrail",
    "Corner guard",
    "Head-end / rack plywood",
    "Access panel frame",
    "Door stop / holder",
    "Shelf & rod",
    "Closet shelving",
    "Towel bar / bath accessory",
    "Cabinet cleat",
    "Fire extinguisher cabinet",
    "Signage",
    "Equipment somebody's hanging"
  ],

  /* WHAT WENT IN. Both vocabularies again — ply and 2x on the wood side, cee and
     strap on the commercial side. No thickness is implied by any label; the size
     is typed on the row. */
  went_in: [
    "Plywood",
    "Full-height plywood",
    "Fire-retardant treated plywood",
    "2x flat",
    "2x on edge",
    "Cee laid flat between studs",
    "Doubled studs",
    "Flat strap",
    "Backing plate",
    "Continuous backing the whole run",
    "Blocking between studs",
    "Header",
    "Nailer",
    "Nothing yet — held for a size"
  ],

  /* WHO ASKED. Field tallies say "plumber", never "PC" — contract abbreviations
     belong in the trailer. "Off the print" is a real answer and the most common
     one on a job with a backing sheet. */
  asked_by: [
    "AV",
    "LV / fire alarm",
    "EC",
    "Plumber",
    "HVAC",
    "Sprinkler",
    "Casework",
    "Doors & hardware",
    "GC super",
    "Owner / tenant",
    "Off the print"
  ],

  how_asked: [
    "On the walk",
    "Text",
    "Email",
    "Marked print",
    "On the backing sheet",
    "Marked on the wall"
  ],

  /* THE LADDER. Three rungs and the last one is the one that matters: COVERED
     stamps the day the wall closed, which is the whole evidentiary point of the
     ledger. It does NOT wrap — a covered wall does not go back to asked. */
  status: ["Asked", "In", "Covered"],

  flags: ["Need a size", "Need a height", "Can't — tell me where else"]
};

/* ── THE LOAD (shape #1 — shared/checklist-request.js) ─────────────────────
 * The vocabulary for the-load.html. Written by a panel of commercial metal-stud
 * framers, residential wood framers and a taper, then cut by a second: 64 lines
 * proposed, 44 kept, 20 killed.
 *
 *  · THE DROP IS ON EVERY LINE, and it is the reason this page exists. No other
 *    trade's order needs it: this material arrives on a boom truck through a
 *    window opening, and WHERE IT GOES is the field that decides whether the
 *    order was any good. Board on the wrong floor is a day gone.
 *  · MIXED UNITS ON ONE LIST — lift, bundle, stick, sheet, box, bag, roll. The
 *    quantity is free text for exactly that reason; a number spinner is a desk
 *    person's idea of how a load is counted.
 *  · THE VOCABULARY GATE HERE IS SHARPER THAN ANY OTHER TRADE'S. Every hand
 *    alive says one manufacturer's name instead of the word BOARD, a hundred
 *    times a day. That is the reason to check the word and never the reason to
 *    print it. It is board, it is mud (never joint compound), it is bead (never
 *    accessories), it is a lid. And GRID is never a location — grid is the
 *    ceiling contractor's act on this trade, and using it for a column line is
 *    the fastest tell on a page that no framer wrote it.
 *  · BOTH WORDS, EVERYWHERE: BACKING is commercial, BLOCKING is the wood side,
 *    they are the same thing, and printing only one tells half this trade
 *    family the page was not written for them.
 *  · NOTHING RATED. No span or gauge-to-height tables, no shear or hold-down
 *    callouts, no fastener schedules, no assembly numbers. Sizes come off HIS
 *    plans; the page carries what he picks and recommends nothing.
 */
(function () {
  "use strict";
  /* §THE NEUTRAL — every axis leads with one, written as the QUESTION, and the
   * page drops any value starting with an em-dash. A pre-selected default would
   * be the tool choosing for him; a printed value nobody picked would be the tool
   * putting words in his message. */
  function n(q) { return "\u2014 " + q + " \u2014"; }
  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }
  window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

  window.TOOLKIT_ITEMS.cats = [
    {
      id: "need",
      name: "What do you need on the truck?",
      docName: "The main stuff",
      hint: "Type it, or paste your whole list — one line each, and say where it goes. Count it however you say it: 2 lifts, 60 sht, 8 bx, a pallet.",
      writein: true,
      items: []
    },
    {
      id: "steel",
      name: "Studs, track & plate",
      docName: "Studs, track & plate",
      hint: "Steel and wood on one list — it's one crew. Widths and lengths come off your plans; this page doesn't know your job and won't guess.",
      items: [
        { n: "Studs — steel", sub: "SAY THE GAUGE AND THE LENGTH WITH THE COUNT",
          ax: [
            ax("Size", [n("which width")].concat(["1-5/8 in", "2-1/2 in", "3-5/8 in", "4 in", "6 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Track", sub: "SAY THE GAUGE — AND SAY IF IT'S A LIFT OR LOOSE STICKS",
          ax: [
            ax("Size", [n("which width")].concat(["1-5/8 in", "2-1/2 in", "3-5/8 in", "4 in", "6 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Deep-leg track", sub: "SLIP TRACK — TOP OF WALL AT THE DECK, NOT YOUR BOTTOM TRACK",
          ax: [
            ax("Size", [n("which width")].concat(["1-5/8 in", "2-1/2 in", "3-5/8 in", "4 in", "6 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "2x studs & plate", sub: "PRE-CUTS OR STICKS — SAY WHICH AND HOW LONG",
          ax: [
            ax("Size", [n("which size")].concat(["2x4", "2x6", "2x8", "2x10", "2x12"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Flat strap & bridging", sub: "AND THE BRIDGING CLIPS — SAY THE WIDTH AND GAUGE WITH THE COUNT",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "board",
      name: "Board",
      docName: "Board",
      hint: "Say the length. A truck of 8s when you wanted 12s is a wall full of butt joints and a week of taping.",
      items: [
        { n: "5/8 board", sub: "MOST OF WHAT'S ON THE TRUCK — SAY IF YOU WANT IT 54 WIDE",
          ax: [
            ax("Size", [n("how long")].concat(["8 ft", "9 ft", "10 ft", "12 ft", "14 ft", "16 ft"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "1/2 board", sub: "LIDS AND THE LIGHT WALLS",
          ax: [
            ax("Size", [n("how long")].concat(["8 ft", "9 ft", "10 ft", "12 ft", "14 ft", "16 ft"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Green board", sub: "MOISTURE BOARD — WET WALLS AND BEHIND THE TILE MAN",
          ax: [
            ax("Size", [n("how thick")].concat(["1/2 in", "5/8 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Cement board", sub: "TILE BACKER — AND IT NEEDS ITS OWN SCREWS",
          ax: [
            ax("Size", [n("how thick")].concat(["1/4 in", "1/2 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Shaftliner", sub: "SHAFT WALLS — THE LINER, NOT BOARD",
          ax: [
            ax("Size", [n("how long")].concat(["8 ft", "10 ft", "12 ft", "14 ft", "16 ft"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "mud",
      name: "Mud & tape",
      docName: "Mud & tape",
      hint: "It's mud. A box, a bucket and a bag are three different pallets — say which.",
      items: [
        { n: "All-purpose mud", sub: "THE HEAVY ONE — BEDDING TAPE AND BEAD",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["boxes", "buckets", "bags"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Lightweight mud", sub: "THE LIGHT ONE — COATS AND SKIM",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["boxes", "buckets", "bags"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Hot mud", sub: "SETTING — SAY WHICH ONE WITH THE COUNT",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Paper tape", sub: "IT'S WHAT GOES IN THE FLATS",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["rolls", "boxes"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Mesh tape", sub: "STICKY — PATCHES AND CEMENT BOARD",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Texture", sub: "SAY THE PATTERN WITH THE COUNT",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["bags", "buckets"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "bead",
      name: "Bead",
      docName: "Bead",
      hint: "Bead — never accessories. Say the length; a corner spliced because the yard sent 8s is a callback.",
      items: [
        { n: "Corner bead", sub: "SAY METAL, PAPER-FACED OR VINYL WITH THE COUNT",
          ax: [
            ax("Size", [n("how long")].concat(["8 ft", "9 ft", "10 ft", "12 ft"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Bullnose", sub: "AND THE 3-WAY CAPS — NOBODY ORDERS THE CAPS",
          ax: [
            ax("Size", [n("how long")].concat(["8 ft", "9 ft", "10 ft", "12 ft"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "L-bead", sub: "WHERE BOARD DIES INTO SOMETHING ELSE",
          ax: [
            ax("Size", [n("which size")].concat(["1/2 in", "5/8 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "J-bead", sub: "SLIPS OVER THE EDGE — NOT THE SAME STICK AS L",
          ax: [
            ax("Size", [n("which size")].concat(["1/2 in", "5/8 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Tear-away bead", sub: "THE ONE WITH THE LEG YOU RIP OFF — AT THE DECK AND THE FRAMES",
          ax: [
            ax("Size", [n("which size")].concat(["1/2 in", "5/8 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Off-angle & flex bead", sub: "ANYTHING THAT ISN'T A 90 — ARCHES AND THE 3-WAYS",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "fast",
      name: "Screws, pins & nails",
      docName: "Screws, pins & nails",
      hint: "No schedules on here — you know yours. This is the count and where it lands.",
      items: [
        { n: "Board screws — fine", sub: "FOR STEEL — LOOSE BOX OR COLLATED, SAY WHICH",
          ax: [
            ax("Size", [n("how long")].concat(["1 in", "1-1/8 in", "1-1/4 in", "1-5/8 in", "2 in", "2-1/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Board screws — coarse", sub: "FOR WOOD — LOOSE BOX OR COLLATED, SAY WHICH",
          ax: [
            ax("Size", [n("how long")].concat(["1 in", "1-1/8 in", "1-1/4 in", "1-5/8 in", "2 in", "2-1/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Framing screws", sub: "PANCAKES, WAFERS, HEX SELF-DRILLERS — SAY WHICH WITH THE COUNT",
          ax: [
            ax("Size", [n("how long")].concat(["7/16 in", "1/2 in", "3/4 in", "1 in", "1-1/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Pins, loads & fuel", sub: "FOR THE GUN — SEND ALL THREE OR SEND NONE",
          ax: [
            ax("Size", [n("how long")].concat(["1/2 in", "5/8 in", "3/4 in", "1 in", "1-1/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Nails — sticks and coils", sub: "SAY THE GUN WITH THE COUNT",
          ax: [
            ax("Size", [n("how long")].concat(["1-1/2 in", "2 in", "2-3/8 in", "3 in", "3-1/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "guts",
      name: "Backing, blocking & insulation",
      docName: "Backing, blocking & insulation",
      hint: "Backing on the commercial side, blocking on the wood side — same thing. It all has to be on the floor before anybody closes a wall.",
      items: [
        { n: "Backing plywood", sub: "BLOCKING PLY — THE WALL CLOSES FRIDAY WHETHER IT'S THERE OR NOT",
          ax: [
            ax("Size", [n("how thick")].concat(["1/2 in", "5/8 in", "3/4 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Sound batts", sub: "SAY THE WIDTH WITH THE COUNT — WRONG WIDTH AND IT WON'T STAY IN",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["bags", "bundles"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Mineral wool", sub: "SAFING — THE DECK AND THE SLAB EDGE",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["bags", "bundles"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Sound caulk", sub: "THE BLACK GOO",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["tubes", "sausages"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Firestop caulk", sub: "THE RED ONE — NOT THE SAME TUBE AS SOUND CAULK",
          ax: [
            ax("Unit", [n("how's it coming")].concat(["tubes", "sausages"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "lid",
      name: "Lids, soffits & channel",
      docName: "Lids, soffits & channel",
      hint: "It's a lid. Channel, angle and the wire the whole thing hangs off.",
      items: [
        { n: "Hat channel", sub: "FURRING CHANNEL — SAME THING",
          ax: [
            ax("Size", [n("which size")].concat(["7/8 in", "1-1/2 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Resilient channel", sub: "RC — AND IT BENDS IF YOU STACK ANYTHING ON IT",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Black iron", sub: "COLD-ROLLED CHANNEL — THE RUNNERS",
          ax: [
            ax("Size", [n("which size")].concat(["3/4 in", "1-1/2 in", "2 in"])),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Wall angle", sub: "L-ANGLE — WALLS, LIDS AND KICKERS",
          ax: [
            ax("Size", [n("which size")].concat(["1 x 1", "1-1/2 x 1-1/2", "2 x 2", "2 x 3"]), true),
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Tie wire & hanger wire", sub: "SEND MORE THAN YOU THINK — SAY WHICH ONE WITH THE COUNT",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    },
    {
      id: "burn",
      name: "The stuff that runs out",
      docName: "The stuff that runs out",
      hint: "Small, cheap, and it stops a whole floor at nine in the morning. It's meant to be partial.",
      items: [
        { n: "Knife blades", sub: "THE FIRST THING TO GO", qtyDefault: "1 bx",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Screw bits & dimplers", sub: "GONE BY LUNCH", qtyDefault: "1 bx",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Sanding — screens, sponges & pole heads", sub: "THE POLE HEAD IS THE ONE THAT BREAKS",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Chalk & keel", sub: "BLUE CHALK, LUMBER CRAYON, STRING LINE",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Shims", sub: "PLASTIC — FOR TRACK AND FRAMES",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Poly, rosin paper & masking", sub: "FLOOR PROTECTION AND THE DUST WALL",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] },
        { n: "Dust masks, gloves & plugs", sub: "AND GLASSES — THE GANG BOX IS ALWAYS EMPTY", qtyDefault: "1 bx",
          ax: [
            ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
          ] }
      ]
    }
  ];

  window.TOOLKIT_ITEMS.writeinAx = [
    ax("Drop", [n("where's it going")].concat(["Ground floor", "2nd floor", "3rd floor", "4th or higher — say which", "Basement", "Outside — laydown or driveway", "Gang box / job trailer", "Split it — see the note"]), true)
  ];
})();


/* ── GETTING IN (getting-in.html) — shape #2, shared/note.js ──────────────
 * Ported from AV's, same shape. AV chases a locked room; this trade chases
 * the building's patience — it's the loudest crew in the building and the
 * one that shows up with the most material behind it. Four heads-up lines
 * swap for real ones: loud all day, a powder-actuated gun on the deck, dust
 * through the whole floor, board staged in a corridor for days. `run`,
 * `closing` and `warn` are AV's, unchanged.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Framing · you → whoever holds the keys",
  lede: "You’re the loudest crew this building will host, and the one that shows up with the most material behind it. Send the ask that gets a yes on the first try — the route in, where it stages, how loud and for how long, and the heads-up that keeps your name off the complaint list.",
  docName: "ACCESS REQUEST",

  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "Nights all week" },
    { v: "Ongoing — I’ll flag changes" }
  ],

  need: [
    { name: "Doors unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The freight elevator" },
    { name: "The dock" },
    { name: "A route in that isn’t through the lobby", sub: "hoist, stairwell, or a window opening — tell me which one’s ours" },
    { name: "Somewhere to put the van" },
    { name: "Somewhere to stage material for the run", sub: "not just the room we’re working in — board and studs sit there for days" },
    { name: "The room cleared", sub: "off the calendar, desks empty" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" }
  ],

  heads: [
    { name: "It’ll be loud, and it runs all day", sub: "cutting, nailing, sanding — tell me the hours you need it quiet" },
    { name: "Dust — the whole floor, not just this room", sub: "there’s a saw station running somewhere on your floor — tell me if you want a barrier or the return shut down" },
    { name: "Ceiling tiles out", sub: "I’ll tell you which corridor and for how long" },
    { name: "Working over your furniture", sub: "lift or ladder above desks" },
    { name: "Material staged in the corridor for days", sub: "board, studs and bead sit there till we rock it — tell me where you’d rather it wait" },
    { name: "We’ll set off motion and door contacts", sub: "after hours, moving between rooms" },
    { name: "Powder-actuated shots into the deck", sub: "sounds like something worse than it is — comes in bursts, floor to floor" },
    { name: "We have to touch the fire alarm", sub: "tell me who puts the panel on test — we don’t" },
    { name: "A sprinkler head is in the way", sub: "that’s your impairment process — tell me how you run it" },
    { name: "Something has to come off power", sub: "your engineer throws it, not us — tell me the window" },
    { name: "Patient or clinical space next door", sub: "tell me what you need from us before we start" }
  ],

  phSite: "Building C",
  phRoom: "Suite 300",
  phHow: "3rd flr, off the freight lobby",
  phScope: "framing walls and hanging board for the tenant build-out",
  phLoud: "boom truck and track shots first thing, saws running all day, quiet by 4",
  phTo: "Gary — building engineer",
  phMe: "Mike R — 415-555-0172",
  phCo: "Apex Interiors",

  closing: [
    "This is an ask, not a booking — nobody rolls until you reply. Wrong night? Tell me which one works and we’ll take it.",
    "Saying yes: tell me the window you’re actually giving us and who’s meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It’s a request, not a permit and not a booking.</b> Anything on the heads-up list that needs a permit, a panel on test or a fire watch is theirs to issue and theirs to number — this page just tells them it’s coming and asks how they want it run. And check your contract before you send it: plenty of them say you don’t talk to the building direct. If yours does, send this to your GC and let him forward it — same words, right chain."
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
    { "es": "— clase", "en": "— class" },
    { "es": "OFICIAL (JOURNEYMAN)", "en": "JOURNEYMAN" },
    { "es": "APRENDIZ (APPR)", "en": "APPRENTICE" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" }
  ],
  "how": [
    { "es": "Me lo dijo en el recorrido", "en": "Told me on the walk" },
    { "es": "Texto / correo", "en": "Text / email" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me entregó un plano marcado", "en": "Marked-up print handed to me" },
    { "es": "Lo dijo en la junta del tráiler", "en": "Said it in the trailer meeting" }
  ],
  "notin": [
    { "es": "Este vale es solo el corte", "sub": "no la tablaroca de contrato en ese muro", "en": "This tag is the cut-in only" },
    { "es": "Parche, tape y lijado no incluidos", "sub": "después de que la gente de usted vuelva a pasar", "en": "Patch, tape and sand not included" },
    { "es": "Sin horas de lift, andamio ni zancos", "sub": "a menos que esté abajo en la lista", "en": "No lift, scaffold or stilt time" },
    { "es": "No el backing que ya estaba en la lista original", "en": "Not the backing already on the original list" },
    { "es": "No el cierre del segundo lado — eso es contrato", "en": "Not the second-side close — that's contract" },
    { "es": "Sin horas de espera para la cuadrilla que esperó", "en": "No stand-by hours for the crew that waited" },
    { "es": "No es reclamo por retraso ni impacto al programa", "en": "Not a delay claim and not a schedule impact" },
    { "es": "Sin acarreo de basura ni limpieza del tiradero de otro contratista", "en": "No scrap haul or cleanup for another trade's mess" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas antes de cerrarlo", "en": "In this message — shot before we closed it" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "Súper del GC", "en": "GC super" },
    { "es": "Asistente del súper del GC / ingeniero de campo", "en": "GC assistant super / field engineer" },
    { "es": "PM del GC", "en": "GC PM" },
    { "es": "Nuestro GF o PM", "en": "Our GF or PM" },
    { "es": "Rep del dueño / facilities", "en": "Owner's rep / facilities" },
    { "es": "Arquitecto o ingeniero en campo", "en": "Architect or engineer in the field" },
    { "es": "Mayordomo de otro contratista", "en": "Another trade's foreman" },
    { "es": "Inspector", "en": "Inspector" }
  ],
  "why": [
    { "es": "No está en mis planos", "en": "Not on my set" },
    { "es": "Cambió el plano después de que lo armé", "en": "Drawing changed after I framed it" },
    { "es": "Backing que nadie pidió antes de cerrar el muro", "sub": "ahora es un corte", "en": "Backing nobody asked for before the wall closed" },
    { "es": "Hay trabajo de otro contratista en la línea de mi muro", "en": "Another trade's work is in my wall line" },
    { "es": "Daño por otros — nosotros lo abrimos y lo cerramos", "en": "Damage by others — we opened and closed it" },
    { "es": "Condiciones existentes", "sub": "no es lo que muestran los as-builts", "en": "Existing conditions" },
    { "es": "El inspector no lo pasó como está dibujado", "en": "Inspector wouldn't pass it as drawn" },
    { "es": "Me mandaron trabajar fuera de secuencia", "en": "Told to work out of sequence" },
    { "es": "Lo dejamos abierto para alguien, y luego me mandaron cerrarlo de todos modos", "en": "Held for somebody, then told to close it anyway" }
  ]
};
