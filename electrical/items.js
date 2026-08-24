/* ELECTRICAL FIELD TOOLKIT — VOCABULARY DATA (the pull list).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Size ladders and
 * type sets live HERE — never in the identity config, never inline in a page.
 *
 * THIS FILE IS A FORGET-LIST, NOT A CATALOG. It is capped on purpose. A commercial
 * foreman reviewing it put the reason better than a spec could: "Nobody forgets the
 * wire. What we forget is the fourteen-cent stuff that shuts a floor down." Anything
 * big, obvious or spec'd — wire, pipe, gear, fixtures, panels, breakers — belongs in
 * the write-in box at the top of the page, which takes a pasted list one per line.
 * Every line below earns its place by being something that stops a crew when it is
 * not on the truck.
 *
 * FIVE HARD INVARIANTS. The first four are safety rules (§SAFETY); the fifth is why
 * anyone would use it:
 *
 *  1. ZERO CERTIFIED DATA. No ampacity, no conduit or box fill, no ratings, no
 *     listings, no code article or table numbers, no torque. Not as a value, not as
 *     a hint, not in a placeholder. A pull list structures what a man PICKS.
 *  2. NO WHERE-MAY-I-USE-IT ADJECTIVES. Labels are bare stock nouns — "cover",
 *     "connector", "box". A stock type letter (EMT, MC, LT, LB, THHN) names the
 *     shelf and is fine; EXPANDING one into what it is rated for, or where it may
 *     be used, is not. If it goes outside, he types "goes outside" in the note.
 *  3. THE ADJACENCY TRAP. An axis may only describe the object's OWN dimensions —
 *     never what goes inside it or next to it. Wire size + breaker size is
 *     ampacity; pipe size + conductor count is fill; box size + device count is box
 *     fill. Each field alone is innocent, and the pair is a code table we computed.
 *     (A split bolt or a lug carries a wire size as its OWN catalog size. That is
 *     the part's name for itself, not a calculation about what may land in it.)
 *  4. NO PRE-SELECTED DEFAULT, ANYWHERE. A default IS a recommendation. Every axis
 *     opens on a neutral, and the page drops any neutral so nothing he did not pick
 *     can reach the warehouse. Same reason there are no suggested quantities, no
 *     "a strap every 10 feet", and no job-type presets: that is support spacing, a
 *     takeoff, and a sufficiency claim, in that order.
 *  5. ZERO BRAND NAMES — and in this trade that is harder than it sounds, because
 *     half the vocabulary is genericized trademarks. The names below are the
 *     generic every counter still recognises: twist-on connectors (not the mark),
 *     cable ties, self-drillers, wedge anchors, drop-ins, anti-shorts, strut, flex,
 *     LT, conduit bodies, concrete screws, recip blades.
 *
 * WORDS ARE THE TRADE'S OWN. "Pipe", never "raceway". "Light", never "luminaire".
 * "Mud ring", never "plaster ring". "J-box", "4-square", "the big square",
 * "all-thread", "donuts", "bugs", "minis". A page that says raceway tells an
 * electrician in one word that nobody who built it has ever stood on a deck.
 */
window.TOOLKIT_ITEMS = (function () {
  "use strict";

  /* ── size ladders — the sizes people actually say, in the order they say them ── */
  var TRADE_SIZE = ["1/2 in", "3/4 in", "1 in", "1-1/4 in", "1-1/2 in", "2 in", "2-1/2 in", "3 in", "4 in"];
  var FLEX_SIZE  = ["3/8 in", "1/2 in", "3/4 in", "1 in", "1-1/4 in", "1-1/2 in", "2 in"];
  var ROD_SIZE   = ["1/4-20", "3/8-16", "1/2-13", "5/8-11"];
  var ANCHOR_DIA = ["1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in"];
  var ANCHOR_LEN = ["1-3/4 in", "2-1/4 in", "3 in", "3-3/4 in", "4-1/2 in", "5-1/2 in", "7 in"];
  var CON_SCREW  = ["3/16 x 1-1/4", "3/16 x 1-3/4", "3/16 x 2-1/4", "1/4 x 1-3/4", "1/4 x 2-1/4", "1/4 x 3", "1/4 x 4"];
  var TOGGLE_SZ  = ["1/8 in", "3/16 in", "1/4 in", "3/8 in"];
  var BOX_SIZE   = ["4 in sq", "4-11/16 in sq"];
  // DEPTH, not gang, is the axis that stops a floor. A wrong-depth mud ring means
  // every device on that wall waits for somebody to drive.
  var RING_DEPTH = ["flat", "1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "1 in", "1-1/4 in"];
  var KO_SIZE    = ["1/2 in", "3/4 in", "1 in", "1-1/4 in", "1-1/2 in", "2 in"];
  var LUG_SIZE   = ["#10", "#8", "#6", "#4", "#2", "1/0", "2/0", "4/0", "250 MCM", "350 MCM", "500 MCM"];
  var GANG       = ["1-gang", "2-gang", "3-gang", "4-gang"];
  var TIE_LEN    = ["4 in", "8 in", "11 in", "14 in", "24 in"];
  var HOLESAW    = ["7/8 in", "1-1/8 in", "1-3/8 in", "1-3/4 in", "2 in", "2-1/2 in", "3 in", "4 in"];
  var DRILL_DIA  = ["3/16 in", "1/4 in", "5/16 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "1 in"];
  var SCREW_LEN  = ["1/2 in", "3/4 in", "1 in", "1-1/2 in", "2 in", "3 in"];

  /* ── THE NEUTRAL ────────────────────────────────────────────────────────────
   * Every axis leads with one of these and the page drops any value starting with
   * an em-dash. Two rules ride on it at once: a pre-selected default would be the
   * tool recommending a size, and a printed value nobody chose would be the tool
   * putting words in a man's message. The neutral text is written as the QUESTION
   * so the prompt is sitting right there on the line he just ticked. */
  function n(q) { return "— " + q + " —"; }

  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }
  // Size axes are all keyed "size" on purpose: the page prints that one axis right
  // after the item name ("mud rings, 5/8 in") because that is how it is read aloud.
  function size(list, q) { return ax("Size", [n(q || "pick the size")].concat(list)); }

  var cats = [
    /* ── 1 · THE WAY IN. First section, biggest thing on the page, and the only one
     * with no items: you already know most of what you need, so type it or paste it.
     * The picker underneath is the jog for what you would have forgotten. ─────── */
    {
      id: "need",
      name: "What do you need?",
      // On screen it is a question to him. In the message it is a heading a
      // warehouse guy reads, and he was never asked anything.
      docName: "The main stuff",
      chip: "#12699F",
      hint: "Type it, or paste your whole list — one per line. Quantities however you say them: 500 ft, 2 bx, a case, (6).",
      writein: true,
      items: []
    },

    {
      id: "box",
      name: "Boxes, rings & covers",
      chip: "#2E64C8",
      items: [
        { n: "Mud rings", sub: "DEPTH IS THE ONE THAT KILLS YOU",
          ax: [size(RING_DEPTH, "how deep"), ax("Gang", [n("gang")].concat(["1-gang", "2-gang", "3-gang", "4-gang"]))] },
        { n: "Square boxes", sub: "4-SQUARE / THE BIG SQUARE",
          ax: [size(BOX_SIZE, "which square"), ax("Depth", [n("depth"), "1-1/2 in", "2-1/8 in"])] },
        // One line, because it is one trip and one reason: an open hole the
        // inspector will find. Flat blanks, raised covers and KO seals get pulled
        // together or forgotten together.
        { n: "Blank covers & KO plugs", sub: "NOBODY HAS ONE ON THE TRUCK",
          ax: [size(KO_SIZE, "plug size"), ax("Cover fits", [n("fits what"), "4-square", "4-11/16", "octagon", "raised"], true)] },
        { n: "Oct boxes & bar hangers", sub: "4-IN OCTS, FIXTURE STUDS, ROUND COVERS", ax: [] }
      ]
    },

    {
      id: "fit",
      name: "Fittings — couplings, connectors, locknuts",
      chip: "#12699F",
      hint: "Two lines for pipe fittings, not forty. If you need a wall of options, type it up top instead — it's faster.",
      items: [
        { n: "EMT couplings", sub: "SAY WHICH",
          ax: [size(TRADE_SIZE), ax("Type", [n("set-screw or compression"), "set-screw", "compression"], true)] },
        { n: "EMT connectors", sub: "SAY WHICH",
          ax: [size(TRADE_SIZE), ax("Type", [n("set-screw or compression"), "set-screw", "compression"], true)] },
        { n: "Locknuts", sub: "THE ONE YOU'RE ALWAYS OUT OF", ax: [size(TRADE_SIZE)] },
        { n: "Bushings", sub: "PLASTIC · INSULATED METAL · GROUNDING W/ LAY-IN LUG",
          ax: [size(TRADE_SIZE), ax("Type", [n("which bushing"), "plastic", "insulated metal", "grounding"], true)] },
        { n: "Chase nipples & donuts", sub: "REDUCING WASHERS", ax: [size(TRADE_SIZE)] },
        { n: "MC / flex / LT connectors", sub: "SNAP-IN, SCREW-IN, STRAIGHT OR 90",
          ax: [size(FLEX_SIZE), ax("Type", [n("which one"), "MC snap-in", "MC screw-in", "flex", "LT", "90"], true)] },
        { n: "Anti-shorts", sub: "MC BUSHINGS — BY THE BAG", ax: [] }
      ]
    },

    {
      id: "term",
      name: "Terminations & grounds",
      chip: "#7A3FA8",
      items: [
        { n: "Twist-on connectors", sub: "THE TWIST-ONS",
          ax: [ax("Color", [n("which color"), "grey", "blue", "orange", "yellow", "red", "tan", "green"])] },
        { n: "Push-in / lever connectors", sub: "SAY HOW MANY PORTS",
          ax: [ax("Ports", [n("ports"), "2", "3", "4", "5"])] },
        { n: "Ground pigtails", sub: "PRE-STRIPPED, SCREW ON THE END", ax: [] },
        { n: "Green ground screws", sub: "10-32 — BY THE BAG", ax: [] },
        { n: "Split bolts", sub: "BUGS", ax: [size(LUG_SIZE, "which size")] },
        { n: "Lugs & crimps", sub: "SAY THE HOLE COUNT — AND BRING THE DIE",
          ax: [size(LUG_SIZE, "which size"), ax("Type", [n("mech or compression"), "mechanical", "compression", "ground bar", "bonding jumper"], true)] }
      ]
    },

    {
      id: "strap",
      name: "Straps, strut & anchors",
      chip: "#2E7D4F",
      hint: "Nobody forgets the strut. They forget what holds it up.",
      items: [
        { n: "Pipe straps", sub: "ONE-HOLE / TWO-HOLE / STANDOFF",
          ax: [size(TRADE_SIZE), ax("Type", [n("which strap"), "one-hole", "two-hole", "standoff"], true)] },
        { n: "Strut straps", sub: "MINIS", ax: [size(TRADE_SIZE)] },
        { n: "Strut nuts, all-thread & rod hardware", sub: "SPRING NUTS, 10-FT STICKS, COUPLINGS, END CAPS, WASHERS",
          ax: [size(ROD_SIZE, "which thread")] },
        { n: "Beam clamps & hanger clips", sub: "C-CLAMPS, PURLIN CLAMPS, BAR HANGERS",
          ax: [ax("Grabs", [n("grabs what"), "beam flange", "rod", "T-bar grid", "purlin", "stud"], true)] },
        { n: "Wedge anchors", sub: "CONCRETE STUD ANCHORS",
          ax: [size(ANCHOR_DIA, "diameter"), ax("Length", [n("how long")].concat(ANCHOR_LEN))] },
        { n: "Drop-ins + the setting tool", sub: "FLUSH, THREADED FOR ROD — BRING THE SETTER",
          ax: [size(ROD_SIZE, "which thread")] },
        { n: "Concrete screws", sub: "NO SHIELD", ax: [size(CON_SCREW, "which size")] },
        { n: "Toggles & wall anchors", sub: "SPRING · STRAP · PLASTIC", ax: [size(TOGGLE_SZ)] },
        { n: "Self-drillers & drive pins", sub: "SELF-TAPPERS, HEX HEAD · PINS FOR THE GAS TOOL",
          ax: [ax("Length", [n("how long")].concat(SCREW_LEN))] }
      ]
    },

    {
      id: "tape",
      name: "Tape, seal & fire",
      chip: "#C4342B",
      items: [
        { n: "Vinyl tape", sub: "3/4 IN — ROLL OR SLEEVE", ax: [] },
        { n: "Phase tape", sub: "THE WHOLE COLOR SET",
          ax: [ax("Color", [n("which colors"), "black", "red", "blue", "brown", "orange", "yellow", "grey", "white", "green", "the full set"], true)] },
        { n: "Firestop caulk & putty pads", sub: "RED CAULK, TUBES, PADS — AND A GUN THAT WORKS", ax: [] },
        { n: "Cable ties", sub: "SAY BLACK OR NATURAL", ax: [size(TIE_LEN, "how long")] },
        { n: "Markers, labels & wire markers", sub: "FINE + FAT TIP, PAINT PEN, LABEL CARTRIDGE", ax: [] },
        { n: "Pull line & wire lube", sub: "PULL STRING, FLAT TAPE, SOAP, FISH LEADER, BASKET GRIP", ax: [] }
      ]
    },

    {
      id: "bits",
      name: "Tools, bits & blades",
      chip: "#1B1B1B",
      hint: "Half of what stops a crew isn't material. The bit that snapped at 9 AM is the classic hour in the truck.",
      items: [
        { n: "Hole saws, arbor, pilot & step bits", sub: "THE PILOT IS WHAT BREAKS", ax: [size(HOLESAW, "which size")] },
        { n: "Masonry bits", sub: "HAMMER BITS — SAY THE LENGTH IN THE NOTE", ax: [size(DRILL_DIA, "diameter")] },
        { n: "Recip & hacksaw blades", sub: "SAY WOOD, METAL OR DEMO",
          ax: [ax("Cut", [n("cutting what"), "wood", "metal", "demo", "carbide"], true)] },
        { n: "Batteries & charger", sub: "SAY THE PLATFORM IN THE NOTE", ax: [] }
      ]
    },

    {
      id: "else",
      name: "Everything else",
      chip: "#5D656E",
      items: [
        { n: "Whips & flex", sub: "FIXTURE WHIPS, 3/8 + 1/2 FLEX, STRAIGHT AND 90", ax: [size(FLEX_SIZE)] },
        { n: "In-use covers & gaskets", sub: "BUBBLE COVERS — SAY THE GANG",
          ax: [ax("Gang", [n("gang"), "1-gang", "2-gang"])] },
        { n: "Wall plates", sub: "SAY MATERIAL + COLOR IN THE NOTE",
          ax: [size(GANG, "how many gang"), ax("Opening", [n("what opening"), "toggle", "duplex", "rocker", "blank", "combo"], true)] },
        // THREAD, not just length. Both reviewers named the three separately and
        // for different jobs: 6-32 longs for deep boxes and extension rings, 8-32
        // for the bigger covers, 10-32 green for grounds. A length with no thread
        // is a bag of the wrong screw.
        { n: "Device & plate screws", sub: "THE LONGS — 1-1/2, 2, 3 IN",
          ax: [ax("Thread", [n("which thread"), "6-32", "8-32", "10-32"]),
               ax("Length", [n("how long")].concat(SCREW_LEN))] },
        { n: "Lockout locks & tags", sub: "LOCKS, HASPS, TAGS", ax: [] },
        { n: "Temp power odds", sub: "CORD CAPS, FEMALE ENDS, GFCI PIGTAILS, CORDS, STRING LIGHTS", ax: [] }
      ]
    }
  ];

  return {
    cats: cats,
    /* THE WRITE-IN CARRIES ONE OPTIONAL AXIS AND NO SIZE FIELD. An earlier plan gave
     * it size + category, which is wrong for how it is actually used: the fast path
     * is PASTING a list whose lines already carry their own sizes ("500' #12 THHN
     * blue"), and making a man set two dropdowns on each of twelve pasted lines is
     * precisely the friction the write-in exists to delete. One neutral tag, for
     * when he wants the warehouse to know which pile a line belongs in. */
    writeinAx: [ax("Where it goes", [
      n("tag it, if you want"),
      "Boxes, rings & covers", "Fittings", "Terminations & grounds",
      "Straps, strut & anchors", "Tape, seal & fire", "Tools, bits & blades", "Everything else"
    ], true)]
  };
})();

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-ticket.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working ELECTRICAL hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · CREW IS FOUR TAPS AND ZERO TYPING. A foreman does not write men's names on a
   *    T&M ticket, he writes "2 JW — 6.0 h ST". So the crew row is classification ×
   *    men × hours × ST/OT/DT, all four on one physical row, and the page does NO
   *    arithmetic on them — no man-hours, no total, no extension, ever.
   *  · ST / OT / DT · JW · APP · GF go on the page FLAT, never expanded. A page that
   *    writes "Journeyman Wireman (JW)" tells a foreman nobody who built it has
   *    bent a piece of pipe.
   *  · HALF THE COUNTRY SAYS TAG AND HALF SAYS TICKET. The heading says TICKET; the
   *    copy never fights a man who calls it a tag.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "Super",
    "GC PM / PE",
    "Owner / tenant rep",
    "Our PM / GF",
    "Another sub's foreman",
    "Somebody else"
  ],
  "how": [
    {
      "v": "Told me on site"
    },
    {
      "v": "Phone"
    },
    {
      "v": "Text"
    },
    {
      "v": "Email"
    }
  ],
  "why": [
    {
      "name": "Not on the prints"
    },
    {
      "name": "Existing conditions",
      "sub": "not what the prints show"
    },
    {
      "name": "Conflict — duct / pipe / sprinkler in our way"
    },
    {
      "name": "Owner / tenant asked for it"
    },
    {
      "name": "RFI / ASI changed it"
    },
    {
      "name": "Tear-out — work already in"
    },
    {
      "name": "Sent us back after we were done"
    },
    {
      "name": "Temp power / temp lights / GC hookup"
    }
  ],
  "classes": [
    "— class",
    "JW",
    "APP",
    "FOREMAN",
    "GF"
  ],
  "shift": [
    "— ST",
    "ST",
    "OT",
    "DT"
  ],
  "stands": [
    {
      "v": "Finished it"
    },
    {
      "v": "Coming back — new ticket tomorrow"
    },
    {
      "v": "Still stopped — men standing",
      "hot": 1
    }
  ]
};


/* ── THE CROSS-BOUNDARY REQUEST — what this crew needs OUT of somebody else ───
 *
 * The toolkit's first tool whose output leaves the company that made it
 * (av/AV_SOCIETY.md §THE INTERFACE). Every tool before it served one man sending
 * something UP his own chain. This is what he sends SIDEWAYS.
 *
 * Written by a foreman in THIS trade and then cut by a cross-trade skeptic who
 * has watched all six trades ask for things and watched half those asks ignored.
 * The cuts are §SAFETY and §THE SYSTEM OF RECORD, not taste:
 *   · anything that was really an RFI, a change order, a submittal or a permit
 *     item is GONE — those are numbered in somebody else's system and a second
 *     number nobody honours is worse than no number;
 *   · nothing asserts a size, a rating, a depth, a fill, a load, a required
 *     height or a listed assembly. Every spec below is a PHRASING he picks;
 *   · no money, ever. Put a price on a row and every foreman stops reading;
 *   · no calendar dates — you ask against HIS gates, because his schedule is the
 *     one that moves. That is why `milestones` is the load-bearing axis here.
 *
 * `who` and `by` on an ask are the USUAL aim and the USUAL gate. They only ever
 * fill a field left empty and never overwrite a pick (§SCARS — a default is a
 * claim).
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "What I Need List",
  eyebrow: "Electrical · you → the other trades",
  lede: "What I need from the other guys before it gets buried - pads, sleeves, backing, cores, trenching, curbs. Sorted by who I'm asking and which gate it has to beat.",
  docSubject: "What we need before it gets buried",
  docSubjectWith: "What we need from {to}",
  closing: "Push back on anything you can't hit - give me a date and I'll mark it committed. What I don't hear back on gets chased Monday, and once it's covered it's a core.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> prints. This page sizes nothing — no wire, no pipe, no pad, no depth, no fill — it sets no heights, and it doesn't know what the code, the engineer or the inspector requires. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C",
  phOff: "E-201 rev 3",
  phFrom: "Dave — Local 3",
  phArea: "Rm 214 — then it's a button",
  areaLabel: "Room / area / gridline",

  who: [
    { v: "gc", label: "GC Super" },
    { v: "conc", label: "Concrete" },
    { v: "framer", label: "Framer" },
    { v: "mech", label: "Mechanical" },
    { v: "mason", label: "Mason / CMU" },
    { v: "dirt", label: "Dirt / Site" },
    { v: "steel", label: "Steel" },
    { v: "roofer", label: "Roofer" }
  ],

  // EARLIEST FIRST — this is the order a job actually closes up in, and it is
  // why grouping by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "backfill", label: "Before they backfill" },
    { v: "slab", label: "Before the slab pour" },
    { v: "cmucap", label: "Before CMU caps out" },
    { v: "deckpour", label: "Before the deck pour" },
    { v: "dryin", label: "Before roof dry-in" },
    { v: "rock", label: "Before rock goes up" },
    { v: "lid", label: "Before the lid closes" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "backing", label: "Backing / blocking", who: "framer", by: "rock", specs: [
      "Ply backing - panel or gear",
      "Ply backing - TV / display bracket",
      "Solid blocking between the studs",
      "Backing for a heavy fixture",
      "Backing outside - wall pack / camera",
      "Backing for EV charger / disconnect",
      "Backing full height at my mark"
    ] },
    { v: "swing", label: "Door swing", who: "framer", by: "rock", specs: [
      "Confirm the swing before I rough the switch",
      "Frame's flipped from the plan — tell me now",
      "Mark the swing on the deck",
      "Pair of doors — tell me which leaf is active"
    ] },
    { v: "core", label: "Core drill", who: "gc", by: "rock", specs: [
      "Core thru the slab - I'll mark it",
      "Core thru the deck from above",
      "Core thru the CMU wall",
      "Core thru the curb / footing",
      "Core and patch it back",
      "Wet core - protect what's below",
      "Scan it first, then core"
    ] },
    { v: "holdoff", label: "Hold off closing", who: "gc", by: "rock", specs: [
      "Don't rock this wall yet - not roughed",
      "Leave the last sheet off for me",
      "Hold the lid - I'm still above it",
      "Hold till my rough inspection clears",
      "Call me before you close it",
      "Leave the grid open in this room"
    ] },
    { v: "accesspanel", label: "Access panel", who: "gc", by: "lid", specs: [
      "Panel in the hard lid at my J-box",
      "Panel in the wall at my junction",
      "Panel at the driver / power supply",
      "Panel at the disconnect above",
      "Lay-in tile is fine - just mark it",
      "Size it to my mark, not the standard"
    ] },
    { v: "sleeves", label: "Sleeves", who: "conc", by: "slab", specs: [
      "Sleeve thru the wall at my mark",
      "Sleeve thru the footing / grade beam",
      "Sleeve thru the deck before the pour",
      "Sleeve thru the rated wall - I'll firestop",
      "Extra sleeve - leave me a spare",
      "Cap it so it don't fill with mud",
      "Sleeve up thru the roof deck"
    ] },
    { v: "blockboxes", label: "Boxes in the block", who: "mason", by: "cmucap", specs: [
      "Set my boxes as you lay it",
      "Run my pipe up the cell",
      "Leave the cell open above my box",
      "Don't grout the cell I'm in",
      "Pipe under the bond beam",
      "Call me the morning of that lift"
    ] },
    { v: "blockout", label: "Blockout / opening", who: "conc", by: "slab", specs: [
      "Blockout in the slab at my mark",
      "Opening in the wall for my gear",
      "Recess for a flush panel",
      "Knockout for the duct bank",
      "Opening for the pull section",
      "Leave the form open - I'll fill it"
    ] },
    { v: "pad", label: "Housekeeping pad", who: "conc", by: "slab", specs: [
      "Pad for the switchgear / main",
      "Pad for the transformer outside",
      "Pad for the generator",
      "Pad for the ATS / disconnect stand",
      "Pour around my stub-ups"
    ] },
    { v: "prepour", label: "Pre-pour walk", who: "conc", by: "slab", specs: [
      "Walk my underslab with me first",
      "Call me the day before you pour",
      "Watch my stubs - don't bend 'em",
      "Let me set floor boxes to grade",
      "Screed to my box, don't bury it",
      "Call me if you have to move a stub"
    ] },
    { v: "trench", label: "Trench / dig", who: "dirt", by: "backfill", specs: [
      "Trench from the utility to the building",
      "Trench for the site lights",
      "Trench for the gate / card reader",
      "Bore under the drive - no open cut",
      "Saw cut and patch the asphalt",
      "Backfill after my inspection, not before",
      "Sand bedding and my warning tape"
    ] },
    { v: "roofpen", label: "Roof pen / curb", who: "roofer", by: "dryin", specs: [
      "Curb for my rooftop gear",
      "Pitch pocket for my conduit",
      "Pen thru the deck, you flash it",
      "Hold the roof open till I'm up",
      "Sleeve up before you dry in",
      "Walk pad out to my disconnect"
    ] },
    { v: "scan", label: "X-ray / scan it", who: "gc", by: "rock", specs: [
      "Scan it before anybody cores",
      "PT slab - scan it, don't guess",
      "Mark the rebar and my pipe below",
      "Occupied below - scan and shore",
      "After hours, tenant's still in there"
    ] },
    { v: "conflict", label: "Conflict - move it", who: "mech", by: "lid", specs: [
      "Your duct is in my rack",
      "Your pipe is over my gear",
      "Keep the front of my panel clear",
      "Your hanger's landing on my pipe",
      "Reroute above my tray",
      "Let's walk it and swap elevations"
    ] },
    { v: "embeds", label: "Embeds / weld clips", who: "steel", by: "deckpour", specs: [
      "Weld clips for my gear hangers",
      "Embed plate in the wall for my rack",
      "Weld my strut before they spray",
      "Angle across the joists to hang from",
      "Don't cut my sleeve out of the deck"
    ] },
    { v: "ufer", label: "Ufer / ground", who: "conc", by: "slab", specs: [
      "Tie my ufer to the bottom steel",
      "Leave my ground tail out of the pour",
      "Ground ring in before you backfill",
      "Don't cut my ground wire - call me",
      "Call me before you tie the footing steel"
    ] }
  ]
};


/* THE RETURN LEG (answer-back.html) — the reply to somebody else's cross-boundary
 * request. The ENGINE is shared/rowlog.js and the PAGE owns the mechanics; this
 * block is only the words this trade says, plus the four placeholders that make
 * the example on screen look like this trade's own job.
 *
 * The gates it offers for "when" are NOT here on purpose: they are
 * TOOLKIT_ROUGHIN.milestones above, and one list that two tools read cannot
 * drift out of step with itself.
 */
window.TOOLKIT_ANSWER = {
  toolName: "What I Can Hit",
  eyebrow: "Electrical · them → you → back",
  lede: "Every trade on the job sends the electrician a list. Line his up, say what you can hit and when, flag what you can’t, and send it back in one message.",
  docSubject: "what I can hit off your list",
  closing: "That’s what I can hit off your list. Anything under CAN’T or NEED TO KNOW, get me an answer and I’ll work it into the same rough — chasing it after the walls close costs both of us.",
  phJob: "Building C", phTo: "Rico — Acme AV", phFrom: "Dave — Local 3", phOff: "AV-101 rev 2",
  paste: "Building C — what we need from the electrician — Aug 9\n\nJob: Building C\nFrom: Rico — Acme AV\n\nCR-204 · back box + 2-gang mud ring · 60 AFF · before rock\nCR-204 · 1in conduit to the ceiling above the rack · before rock\nBoard room · dedicated 20A at the credenza · before trim"
};


/* GETTING IN (getting-in.html) — ported from AV, same shape and same rules. The
 * locked room is the gear room here, not an IDF, and "something has to come off
 * power" already fit this trade before anybody touched it, so it stayed as-is.
 * Three heads-up items didn't earn their place — hot work/torch-or-solder, the
 * sprinkler head, the patient/clinical flag — swapped for what actually stops
 * an electrician at a locked door: a real outage, live work in the gear room,
 * and temp power off the building's own service. One need got added too: the
 * panel schedule. Every swap still hands the permit back to whoever owns it.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Electrical · you → whoever holds the keys",
  lede: "You need into a room somebody else locks — usually the gear room too. Send the ask that gets a yes on the first try — the night, the rooms, who’s coming, and the heads-up that stops a crew getting walked out at nine.",
  docName: "ACCESS REQUEST",

  /* HOW OFTEN, and it is chips rather than a segment on purpose: four options in
     a segment on a 320px phone is the overflow the mobile gate caught last time. */
  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "Nights all week" },
    { v: "Ongoing — I’ll flag changes" }
  ],

  /* WHAT I AM ASKING HIM TO DO. Every one of these is a thing a man on his end
     physically does; none of them is a fact about us. The words are the ones a
     foreman says out loud, not the ones a visitor-management portal uses. */
  need: [
    { name: "Doors unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The freight elevator" },
    { name: "The dock" },
    { name: "Somewhere to put the van" },
    { name: "The room cleared", sub: "off the calendar, desks empty" },
    { name: "The electrical room / gear room open too", sub: "not just the room we’re working in" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "The panel schedule, if you have one", sub: "so we’re not tracing breakers all night" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" }
  ],

  /* BEFORE YOU SAY YES. The top of this list is a courtesy; the bottom of it is
     the reason a crew gets thrown off a site for good. Read the subs: the last
     five do not report a state, they ask him how he wants it run. */
  heads: [
    { name: "It’ll be loud", sub: "anchors, cores — say the word and we’ll move it later" },
    { name: "Dust", sub: "coring and cutting — tell me what barrier you want up" },
    { name: "Ceiling tiles out", sub: "I’ll tell you which corridor and for how long" },
    { name: "Working over your furniture", sub: "lift or ladder above desks" },
    { name: "The corridor gets tight", sub: "gear staged while we’re in" },
    { name: "We’ll set off motion and door contacts", sub: "after hours, moving between rooms" },
    { name: "We have to touch the fire alarm", sub: "tell me who puts the panel on test — we don’t" },
    { name: "A real outage — not just a circuit", sub: "tell me what actually goes dark and for how long" },
    { name: "Something has to come off power", sub: "your engineer throws it, not us — tell me the window" },
    { name: "We’ll have the gear room open and live", sub: "arc-flash boundary roped off — tell me if your people need in while we’re there" },
    { name: "We’re pulling temp power off your service", sub: "tell me where you want us tapping and if it needs its own meter" }
  ],

  phSite: "Building C",
  phRoom: "Elec Rm 2B",
  phHow: "basement, past the loading dock",
  phScope: "swapping the panel and re-terminating the feeders",
  phLoud: "hammer drill for the strut, about an hour",
  phTo: "Frank — chief engineer",
  phMe: "Dave R — 415-555-0148",
  phCo: "Bayview Electric",

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
    { "es": "— clase (class)", "en": "— class" },
    { "es": "OFICIAL (JW)", "en": "JW" },
    { "es": "APRENDIZ (APP)", "en": "APP" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" },
    { "es": "MAYORDOMO GENERAL (GF)", "en": "GF" }
  ],
  "how": [
    { "es": "Me lo dijo en la obra", "en": "Told me on site" },
    { "es": "Llamada", "en": "Phone" },
    { "es": "Texto", "en": "Text" },
    { "es": "Correo", "en": "Email" }
  ],
  "roles": [
    { "es": "El súper", "en": "Super" },
    { "es": "PM / PE del GC", "en": "GC PM / PE" },
    { "es": "El dueño / rep del inquilino", "en": "Owner / tenant rep" },
    { "es": "Nuestro PM / GF", "en": "Our PM / GF" },
    { "es": "El mayordomo de otro sub", "en": "Another sub's foreman" },
    { "es": "Otra persona", "en": "Somebody else" }
  ],
  "shift": [
    { "es": "— ST", "en": "— ST" },
    { "es": "ST", "en": "ST" },
    { "es": "OT", "en": "OT" },
    { "es": "DT", "en": "DT" }
  ],
  "stands": [
    { "es": "Lo terminamos", "en": "Finished it" },
    { "es": "Regresamos — ticket nuevo mañana", "en": "Coming back — new ticket tomorrow" },
    { "es": "Sigue detenido — hombres parados", "en": "Still stopped — men standing" }
  ],
  "why": [
    { "es": "No está en los planos", "en": "Not on the prints" },
    { "es": "Condiciones existentes", "sub": "no es lo que muestran los planos", "en": "Existing conditions" },
    { "es": "Conflicto — ducto / tubería / sprinkler estorbando", "en": "Conflict — duct / pipe / sprinkler in our way" },
    { "es": "Lo pidió el dueño / inquilino", "en": "Owner / tenant asked for it" },
    { "es": "Lo cambió un RFI / ASI", "en": "RFI / ASI changed it" },
    { "es": "Demo — trabajo ya instalado", "en": "Tear-out — work already in" },
    { "es": "Nos regresaron cuando ya habíamos terminado", "en": "Sent us back after we were done" },
    { "es": "Corriente temporal / luces temporales / conexión para el GC", "en": "Temp power / temp lights / GC hookup" }
  ]
};
