/* LOW-VOLTAGE / SECURITY / FIRE — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary that keeps a trade config from rotting (roster research, five
 * trades): trade.js = IDENTITY + COPY · tools.js = REGISTRY · items.js = the
 * trade's VOCABULARY DATA. Size ladders, option sets and category lists belong
 * in data — never in the identity config, never inline in a page.
 *
 * TWO PASSES RAN OVER EVERY WORD IN THIS FILE BEFORE IT SHIPPED, and both are
 * standing requirements for anything added to it later:
 *
 * 1. THE GENERIC-SUBSTITUTION PASS (§SCARS "half a trade's vocabulary is
 *    somebody's trademark"). Low-voltage says more registered marks per sentence
 *    than any trade shipped so far, and every one of them is spoken as a common
 *    noun on site. None of them are in here. The ones deliberately kept OUT:
 *    the fire-alarm panel brands, the video and access head-end brands, the prox
 *    credential brands, the strut / beam-clip / wire-hanger brands, the locking
 *    and exit-device brands, the label-printer brands, the tester brands, and
 *    the spreadsheet whose name nearly ended up on our own second copy button.
 *    "Everybody says it out loud" is the reason to CHECK a word, never the
 *    reason to print it.
 *
 *    Deliberately NOT genericised, because over-correcting here makes the page
 *    sound like nobody who built it has stood on a lift: the standards
 *    designations and the trade's real shorthand — IDF/MDF, head end, home run,
 *    AFF, SLC/NAC/IDC, REX, PoE, prox, addressable, conventional, grid ceiling,
 *    hard lid, J-hook, mud ring. Those are the trade's own words, owned by
 *    nobody.
 *
 * 2. THE CERTIFIED-DATA PASS (§SAFETY). Every option here is a BARE STOCK NOUN.
 *    No parenthetical carries a rating, a coverage, a spacing, a frequency, a
 *    read range or a listing — a picker option is us ASSERTING the attribute,
 *    and the moment "Strobe" becomes "Strobe (75cd)" we have shipped a listed
 *    table we do not have. There is no candela ladder in this file and there
 *    never will be: it presents as an obvious size picker and IS the listed set.
 */

/* SUBSYSTEM gates TYPE. "Type" across all of low-voltage is forty-odd options,
 * which is a scroll wheel on every single row. Seven subsystems is deliberately
 * a native <select> — the six-option chip ceiling applies to inline chip rows,
 * and a select is exempt by construction. Set once for a job; it rides on every
 * row so the spreadsheet and the mount list know which trade you are in. */
window.LV_SUBSYSTEMS = [
  { v: "video",     label: "Video" },
  { v: "access",    label: "Access control" },
  { v: "fire",      label: "Fire alarm" },
  { v: "intrusion", label: "Intrusion" },
  { v: "wireless",  label: "Wireless / DAS" },
  { v: "audio",     label: "Audio / paging" },
  { v: "nurse",     label: "Nurse call" }
];

/* TYPE, per subsystem, six chips maximum so the row of chips never wraps into a
 * wheel. Stock nouns only.
 *
 * ACCESS IS DELIBERATELY DIFFERENT: one row is one OPENING, not one device. A
 * door is a reader, a contact, a request-to-exit, a strike or a mag, sometimes a
 * push-to-exit and an operator — six devices that get installed, terminated and
 * tested as a unit and are argued about as a unit. Six rows per door on a 60-door
 * job is 360 rows to say what 60 rows say better, so the axis names what the
 * opening DOES, not what parts are in it. */
window.LV_TYPES = {
  video:     ["Dome", "Bullet", "Turret", "Multi-sensor", "Fisheye", "PTZ"],
  access:    ["In only", "In / out", "Monitor only", "Auto operator", "Intercom", "Turnstile"],
  fire:      ["Smoke", "Heat", "Duct smoke", "Pull station", "Horn/strobe", "Module"],
  intrusion: ["Keypad", "Motion", "Contact", "Glass break", "Hold-up"],
  wireless:  ["Access point", "Antenna", "Bridge"],
  audio:     ["Ceiling speaker", "Horn speaker", "Speaker/strobe", "Intercom", "Volume control"],
  nurse:     ["Patient station", "Dome light", "Bath pull", "Staff station", "Emergency station"]
};

/* MOUNT — six universal values that cover a dome, an access point, a speaker, a
 * smoke, a strobe and a reader all at once, because a camera guy says "in the
 * grid" and a fire guy says "ceiling" and they are pointing at the same hole.
 * Resist the urge to fork this per subsystem; the one place it genuinely forks
 * is a card reader on a storefront mullion, so ACCESS gets a seventh chip.
 * NO HEIGHTS. Not as a value, not as a default, not as a placeholder example —
 * the prescribed heights are a code table and a seeded "82 (should be 80-96)" is
 * that table shipped as helper text. */
window.LV_MOUNTS = ["Grid ceiling", "Hard lid", "Wall", "Pendant", "Corner", "Surface / box"];
window.LV_MOUNT_ACCESS_EXTRA = "Mullion";

/* THE STATUS LADDER. Six honest states, in the order the work actually happens.
 * PULLED leads because on a low-voltage job the cable is at the location, coiled
 * and labelled, months before the device exists — and it is the most-tracked
 * state on the job.
 *
 * Tapping a row advances it ONE STEP, which is why six is safe: a row renders
 * exactly one chip (where it is now), never the whole ladder, so this can never
 * wrap into a wheel however long the ladder gets.
 *
 * These are STAGES OF INSTALL, and nothing here is a certification. "Verified"
 * means the image came up, the card opened the door, the horn and strobe fired —
 * his own check of his own work. The acceptance test is witnessed by the AHJ,
 * recorded on a form owned and numbered by the fire alarm contractor of record,
 * and this page will never look like that form. */
window.LV_STATUS = ["PULLED", "MOUNTED", "TERMINATED", "TESTED", "PROGRAMMED", "VERIFIED"];

/* FLAGS ARE NOT LADDER STEPS. A device is blocked AT a stage — mounted but the
 * grid isn't in, terminated but on the punch — and folding the two together
 * loses which stage it stalled at, which is the only thing the foreman is
 * actually being asked. A flag rides alongside the status, and every flagged
 * line prints in its own section at the end of the document whether or not it
 * changed. That section is the most valuable thing this tool produces and it is
 * what gets read first at the 7am huddle. */
window.LV_FLAGS = ["PUNCH", "BLOCKED", "HOLD"];

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working LOW-VOLTAGE hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · OUR EXTRAS ARE ALMOST ALWAYS SOMEBODY ELSE'S CONDITION. Ceiling closed on us,
   *    no ply, no backing, nothing roughed in, IDF isn't ready, our cable torn out
   *    by others — that is what the reason list is made of, and it is why the
   *    closing line asks WHO IS FIXING THE CONDITION. Without that we write the
   *    same tag again next week.
   *  · IT HAS TO LAND AS A HEADS-UP, NOT A CLAIM. The reviewer's kill risk was the
   *    super's face changing on the spot and his own PM telling him to quit sending
   *    letters to the GC. So: no number, no quote-him-back-to-himself line, and a
   *    closing ask a man can answer with two words.
   *  · MEN AND HOURS ARE NEVER MULTIPLIED. They print side by side exactly as
   *    tapped. No man-hour figure, no total, no rate, no classification column.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC super",
    "Our PM",
    "The EC's foreman",
    "Owner's IT",
    "Another sub",
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
      "name": "Not on our prints — you asked for it"
    },
    {
      "name": "Ceiling closed on us"
    },
    {
      "name": "No ply / no backing"
    },
    {
      "name": "Nothing roughed in",
      "sub": "no pipe, no box, no power"
    },
    {
      "name": "IDF's not ready"
    },
    {
      "name": "Our cable / hooks torn out by others"
    }
  ],
  "stands": [
    {
      "v": "Done — nothing left on it"
    },
    {
      "v": "Temp — has to come back out"
    },
    {
      "v": "Trip back to finish — we're off that floor",
      "hot": 1
    },
    {
      "v": "Still stopped — can't finish till it's fixed",
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
  toolName: "Who Owes Me What",
  eyebrow: "Low-voltage · you → the other trades",
  lede: "Everything I need from somebody else before it gets buried — who I'm asking, where it is, and the gate it has to beat. Walk the job, tick it, paste it to his phone.",
  docSubject: "What we need before it's covered",
  docSubjectWith: "What we need from {to}",
  closing: "Mark what you can hit and shoot it back — anything you can't, tell me today. I'd rather move a device now than core a finished wall later.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> drawings. This page sizes nothing — no box, no pathway, no battery, no circuit — it sets no device height and no spacing, and it doesn't know what the code, the engineer or the fire marshal requires. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C",
  phOff: "T-201 rev 3",
  phFrom: "Ray — Sentinel Systems",
  phArea: "Corr 2E — then it's a button",
  areaLabel: "Room / area",

  who: [
    { v: "gc", label: "GC super" },
    { v: "ec", label: "EC foreman" },
    { v: "drywall", label: "Drywall/framers" },
    { v: "ceiling", label: "Ceiling / grid" },
    { v: "doors", label: "Door hardware" },
    { v: "mech", label: "Mech / duct" },
    { v: "sprink", label: "Sprinkler fitter" },
    { v: "elev", label: "Elevator" }
  ],

  // EARLIEST FIRST — this is the order a job actually closes up in, and it is
  // why grouping by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "pour", label: "Before the pour" },
    { v: "frames", label: "Before frames get ordered" },
    { v: "rock", label: "Before rock goes up" },
    { v: "lid", label: "Before the hard lid" },
    { v: "tile", label: "Before tile goes in" },
    { v: "trim", label: "Before we trim out" },
    { v: "ahj", label: "Before the fire marshal walk" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "backing", label: "Backing & blocking", who: "drywall", by: "rock", specs: [
      "Ply — I'll spray the outline on the studs",
      "Blocking between studs, flat to the face",
      "Strut across the studs",
      "Ply the whole wall in the closet",
      "Backing behind the panel, I'll mark it",
      "Backing both sides of the door",
      "Wide enough I can shift it a stud"
    ] },
    { v: "boxring", label: "Box & ring", who: "ec", by: "rock", specs: [
      "LV ring only — no box",
      "Single gang + mud ring",
      "Double gang + mud ring",
      "4-square + ring, deep as you got",
      "Box + blank cover till we trim",
      "Mullion box — the narrow one"
    ] },
    { v: "stubsleeve", label: "Stub & sleeve", who: "ec", by: "rock", specs: [
      "Stub above the ceiling, bushed",
      "Stub + pull string, cap it",
      "Sleeve through the wall where I sprayed",
      "Two stacked — one's never enough",
      "Through the rated wall, you firestop",
      "Home run all the way to the IDF",
      "Sweeps, no hard 90s"
    ] },
    { v: "power", label: "Power at the device", who: "ec", by: "tile", specs: [
      "Quad above the ceiling for the injector",
      "Receptacle over the door for the operator",
      "Whip to the gate operator",
      "Unswitched — not on the light circuit",
      "Not on the occ sensor",
      "Land it in the box we're mounting to"
    ] },
    { v: "holdopen", label: "Leave it open", who: "ceiling", by: "tile", specs: [
      "Leave these tiles out till we're up",
      "Don't load tile over the corridor yet",
      "Call me before you close this wall",
      "Rock one side, leave the other for now",
      "Skip the lid over the head end",
      "Give me a day in there before you close"
    ] },
    { v: "gridlay", label: "Grid layout", who: "ceiling", by: "tile", specs: [
      "Grid per my ceiling markup",
      "Hold a full tile at each device",
      "Keep my device off the main tee",
      "You cut the tile, we set the device",
      "Tile bridge at every cut"
    ] },
    { v: "doorprep", label: "Door & frame prep", who: "doors", by: "frames", specs: [
      "Electric hinge on that leaf",
      "Raceway in the door for the loop",
      "Frame prepped for the strike",
      "Header prepped for the mag",
      "Mullion prepped for the reader",
      "Prep for a contact in the frame",
      "Tell me before it goes to the shop"
    ] },
    { v: "pipedoor", label: "Pipe to the door", who: "ec", by: "frames", specs: [
      "Conduit into the frame, hinge side",
      "Pipe to the strike jamb",
      "Both jambs — reader side and strike side",
      "Up the header, out above the ceiling",
      "Get it in before they grout the frame",
      "Stub to the frame, string in it"
    ] },
    { v: "accesspanel", label: "Access panel", who: "drywall", by: "lid", specs: [
      "Access door in the lid at the device",
      "Access over the head end / the mag",
      "Big enough to get a hand and a tool in",
      "You cut it, I'll locate it",
      "Where I sprayed the X",
      "Hinged, not a cut-out we lose"
    ] },
    { v: "headend", label: "Head-end power", who: "ec", by: "trim", specs: [
      "Dedicated circuit to the rack",
      "Quad in the closet, on the ply",
      "Off the emergency panel",
      "Land it before we set the head end",
      "Ground bar in the closet, bonded by you"
    ] },
    { v: "closet", label: "Closet ready", who: "gc", by: "trim", specs: [
      "Ply on two walls, painted or not",
      "Door on it with a core in it",
      "Cooling on before we power up",
      "Floor sealed — no rock dust",
      "Lights working in there",
      "Nobody else stores material in it"
    ] },
    { v: "duct", label: "Duct smokes set", who: "mech", by: "lid", specs: [
      "Cut and mount it, we'll wire it",
      "We furnish, you install",
      "Call me when the unit's set",
      "Leave me access to it after the lid",
      "Don't close the shaft till we're in",
      "Tell me where the starter lands"
    ] },
    { v: "core", label: "Core drill", who: "gc", by: "lid", specs: [
      "Core the deck, closet to closet",
      "Core the wall above the ceiling",
      "Scan it before you core",
      "You core, we sleeve and firestop",
      "Keep it out of the finished side",
      "One hole, where I sprayed it"
    ] },
    { v: "flowtamper", label: "Flow & tamper", who: "sprink", by: "ahj", specs: [
      "Flow switch set — call me when",
      "Tampers on before the test",
      "Box or slack left at the switch",
      "Tell me when the PIV goes in",
      "Don't cover the riser till we're in",
      "Do 'em all in one trip if you can"
    ] },
    { v: "poursleeve", label: "Sleeves for the pour", who: "ec", by: "pour", specs: [
      "Sleeves in the deck where I marked",
      "Stub-ups at the guard desk",
      "Pipe out to the gate before paving",
      "Pull box at the gate",
      "Sweeps under the drive",
      "Stub up in the pole base",
      "Cap and mark so we find them"
    ] },
    { v: "elevator", label: "Elevator car pull", who: "elev", by: "trim", specs: [
      "Traveler pair for the car camera",
      "Reader pathway into the cab",
      "Box in the car canopy",
      "Term point in the machine room",
      "Term point in the machine room for recall",
      "Before the car gets finished"
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
  toolName: "Got It / Can’t / When",
  eyebrow: "Low-voltage · them → you → back",
  lede: "The GC, the EC or the door guy sent you a list. Line it up, tap each line got it or can’t, put a day on the ones you’re taking, and send it back.",
  docSubject: "what we can hit off your list",
  closing: "That’s what we can hit. The flagged ones I need an answer on before the ceiling closes — after that it’s a lift, a tile and an argument.",
  phJob: "Building C", phTo: "Ken — site super", phFrom: "Ray — Sentinel Systems", phOff: "A-201 rev 4",
  paste: "Building C — close-in list — Aug 9\n\nJob: Building C\nFrom: Ken — site super\n\nLevel 2 · your backing in before rock at every reader\nDoors 210/211 · frame prep confirmed before the frames get ordered\nIDF 2 · head-end power and ground before we set the rack"
};

/* ── THE SHOP LIST (shape #1 — shared/checklist-request.js) ────────────────
 * The vocabulary for consumables.html. Written by a panel of low-voltage,
 * security and fire-alarm hands, then cut by a second one: 50 lines proposed,
 * 35 kept, 15 killed, and a whole section with them.
 *
 *  · IT IS THE FOURTEEN-CENT STUFF THAT STOPS A FLOOR. Nobody forgets the
 *    cable. What ends a day is no J-hooks, no anchors, no blank plates — so the
 *    picker is the forget-list and the write-in is the way in.
 *  · FREQUENCY IS THE PRODUCT. This is the highest-traffic rung on the whole
 *    low-voltage roster, which means FAST beats complete. Axes are used only
 *    where the shop genuinely pulls the wrong thing without one.
 *  · MATERIAL ONLY, NEVER DEVICE DATA. The head-end already exports IP, MAC and
 *    firmware; a page that re-types it is double entry (§THE SYSTEM OF RECORD).
 *  · NOTHING RATED. No cable-fill, no battery calcs, no code thresholds, and
 *    the page never says which cable type is REQUIRED anywhere — the man picks
 *    the type, the page carries it.
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
      name: "What do you need?",
      docName: "The main stuff",
      hint: "Type it, or paste your whole list — one per line. Quantities however you say them: 2 boxes, a case, 1000 ft, (4).",
      writein: true,
      items: []
    },
    {
      id: "hook",
      name: "Hooks, rings & holding it up",
      docName: "Hooks & support",
      hint: "Nobody forgets the cable. What stops a floor is what holds it up.",
      items: [
        { n: "J-hooks", sub: "SAY THE SIZE AND WHAT IT SCREWS TO" },
        { n: "Bridle rings & saddles", sub: "SCREW-IN, AND THE ONES WITH THE SADDLE" },
        { n: "Grid clips, beam clamps & rod hangers", sub: "T-BAR · PURLIN · THREADED ROD" },
        { n: "Hook-and-loop roll", sub: "THE FUZZY ROLL — NOT TAPE, NOT TIES" },
        { n: "Cable ties & sticky backs", sub: "SAY BLACK OR NATURAL — AND THE TIE MOUNTS" }
      ]
    },
    {
      id: "term",
      name: "Ends, jacks & plates",
      docName: "Ends, jacks & plates",
      hint: "If it doesn't match what's already in the wall it's the wrong one. Say the cable.",
      items: [
        { n: "RJ45 plugs & boots", sub: "PASS-THROUGH OR NOT — SOLID OR STRANDED",
          ax: [
            ax("Cable", [n("which cable")].concat(["Cat5e", "Cat6", "Cat6A"]), true)
          ] },
        { n: "Jacks & inserts", sub: "SAY THE COLOR AND IF IT'S SHIELDED — IT'S NEVER THE ONE ON THE TRUCK",
          ax: [
            ax("Cable", [n("which cable")].concat(["Cat5e", "Cat6", "Cat6A"]), true)
          ] },
        { n: "Coax ends", sub: "F OR BNC — COMPRESSION OR CRIMP, SAY WHICH",
          ax: [
            ax("Coax", [n("which coax")].concat(["RG6", "RG59", "RG11"]))
          ] },
        { n: "Beanies, butts & spades", sub: "THE LITTLE B-CONNECTORS — AND THE CRIMPS FOR DOOR HARDWARE" },
        { n: "Faceplates", sub: "SAY HOW MANY PORTS AND WHAT COLOR" },
        { n: "Blanks — inserts & plates", sub: "THE PUNCH LIST IS MADE OF OPEN HOLES" },
        { n: "Mud rings & old-work brackets", sub: "LV RINGS — AND THE SURFACE BISCUITS WHERE THERE'S NO BOX" }
      ]
    },
    {
      id: "rack",
      name: "Rack, closet & pathway",
      docName: "Rack & closet",
      items: [
        { n: "Rack screws & cage nuts", sub: "SAY THE THREAD — GUESS WRONG AND THE RACK SITS" },
        { n: "Patch cords", sub: "SAY THE LENGTH AND THE COLOR — THAT'S THE WHOLE ORDER",
          ax: [
            ax("Cable", [n("which cable")].concat(["Cat5e", "Cat6", "Cat6A"]), true)
          ] },
        { n: "Lacing bars & D-rings", sub: "AND THE SCREWS THAT GO WITH THEM" },
        { n: "Wire duct, loom & surface raceway", sub: "SLOTTED DUCT — AND THE COVER THAT WALKS OFF" }
      ]
    },
    {
      id: "fire",
      name: "Firestop, sleeves & seal",
      docName: "Firestop & sleeves",
      items: [
        { n: "Firestop caulk", sub: "RED TUBES — AND A GUN THAT WORKS" },
        { n: "Putty pads", sub: "FOR THE BOXES WE LEFT BEHIND US" },
        { n: "Sleeves, grommets & bushings", sub: "THROUGH THE WALL, AND OFF THE SHARP EDGE" },
        { n: "Duct seal", sub: "THE STUB-UPS AND THE HOLE THROUGH THE OUTSIDE WALL" }
      ]
    },
    {
      id: "label",
      name: "Labels & marking",
      docName: "Labels & marking",
      items: [
        { n: "Label printer cartridges", sub: "SAY WHICH PRINTER — HALF THE TAPES DON'T FIT" },
        { n: "Self-lam wraps & flag labels", sub: "THE ONES THAT SURVIVE A PULL" },
        { n: "Blank tags & write-on labels", sub: "FOR WHEN THE PRINTER DIES AT 10 AM" },
        { n: "Markers & a paint pen", sub: "FINE AND FAT — AND ONE WHITE" }
      ]
    },
    {
      id: "anchor",
      name: "Anchors, screws & bits",
      docName: "Anchors, screws & bits",
      items: [
        { n: "Self-drillers", sub: "SELF-TAPPERS — HEX HEAD, FOR STUD AND STRUT" },
        { n: "Wall anchors & toggles", sub: "STRAP · SPRING · PLASTIC" },
        { n: "Concrete screws", sub: "NO SHIELD — SAY THE LENGTH" },
        { n: "Drive pins & fuel", sub: "PINS FOR THE GAS TOOL — ONE WITHOUT THE OTHER IS NOTHING" },
        { n: "Drill bits & hole saws", sub: "THE PILOT IS WHAT BREAKS" }
      ]
    },
    {
      id: "truck",
      name: "Batteries, tape & truck stuff",
      docName: "Batteries, tape & truck stuff",
      items: [
        { n: "Batteries — AA, AAA, 9V", sub: "THE TESTER, THE TONER, THE REMOTE" },
        { n: "Panel batteries", sub: "SAY THE SIZE OFF THE OLD ONE" },
        { n: "Canned smoke", sub: "EMPTY BY LUNCH ON A WALK-TEST" },
        { n: "Tape", sub: "E-TAPE, GAFF, PAINTER'S — SAY THE COLORS" },
        { n: "Knife blades & jacket strippers", sub: "HOOK BLADES — AND THE ONE THAT RINGS ROUND CABLE" },
        { n: "Pull string, flat line & lube", sub: "FISH STICKS, BASKET GRIP, SOAP" }
      ]
    }
  ];

  window.TOOLKIT_ITEMS.writeinAx = [
    ax("Where it goes", [n("where does it go")].concat(["Hooks & support", "Ends, jacks & plates", "Rack & closet", "Firestop & sleeves", "Labels & marking", "Anchors, screws & bits", "Batteries, tape & truck stuff"]), true)
  ];
})();


/* GETTING IN (getting-in.html) — av's shape #2 engine, this trade's words.
 * AV can trip a motion sensor walking through after hours; this trade IS
 * the motion sensor, the door contact and the camera. So `need` swaps AV's
 * borrowed "rack room / IDF" for the head end / MDF, and adds the one ask
 * AV never has to make: somebody on THEIR side to watch a door or a camera
 * while we test it. `heads` trades four of AV's entries for the alarms this
 * trade actually sets off — each still hands the process back to whoever
 * runs that system, never reports a state of ours.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Low-voltage · you → whoever holds the keys",
  lede: "You need into rooms already wired to call somebody — the panel, the doors, the cameras — before you’ve even started the work. Send the ask that gets a yes on the first try: the night, the rooms, who’s coming, and the heads-up that keeps your own work off tonight’s alarm log.",
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
    { name: "Somewhere to put the van" },
    { name: "The room cleared", sub: "off the calendar, desks empty" },
    { name: "The head end / panel room open too", sub: "not just the room we’re working in" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" },
    { name: "Their security or IT on standby", sub: "we can’t test a door or a camera without somebody watching it on their side" }
  ],

  heads: [
    { name: "It’ll be loud", sub: "anchors, cores — say the word and we’ll move it later" },
    { name: "Dust", sub: "coring and cutting — tell me what barrier you want up" },
    { name: "Ceiling tiles out", sub: "I’ll tell you which corridor and for how long" },
    { name: "Working over your furniture", sub: "lift or ladder above desks" },
    { name: "Cameras will be down while we’re on them", sub: "blind spot in your coverage till we bring them back — tell me if that’s a problem for tonight" },
    { name: "We’ll set off door-forced and door-held alarms", sub: "your dispatch sees them start to finish — tell me if you want us to warn them first" },
    { name: "We have to touch the fire alarm", sub: "tell me who puts the panel on test — we don’t" },
    { name: "The access-control system will be in a test state", sub: "cards may not open what they should till we’re clear — tell me if anybody needs a door live before then" },
    { name: "Something has to come off power", sub: "your engineer throws it, not us — tell me the window" },
    { name: "We’ll be working in the same closet as the fire panel", sub: "not touching it — tell me if you want somebody with us in there" },
    { name: "Patient or clinical space next door", sub: "tell me what you need from us before we start" }
  ],

  phSite: "Crown Point Plaza",
  phRoom: "MDF 2",
  phHow: "2nd flr, past the security desk",
  phScope: "adding two door readers and terminating back to the head end",
  phLoud: "coring the mullion for the reader, about an hour, done by 8",
  phTo: "Priya — director of security",
  phMe: "Ray M — 415-555-0198",
  phCo: "Sentinel Systems",

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
  "how": [
    { "es": "Me lo dijo en la obra", "en": "Told me on site" },
    { "es": "Teléfono", "en": "Phone" },
    { "es": "Texto", "en": "Text" },
    { "es": "Correo", "en": "Email" }
  ],
  "roles": [
    { "es": "El súper del GC", "en": "GC super" },
    { "es": "Nuestro PM", "en": "Our PM" },
    { "es": "El mayordomo de los eléctricos", "en": "The EC's foreman" },
    { "es": "El IT del dueño", "en": "Owner's IT" },
    { "es": "Otro sub", "en": "Another sub" },
    { "es": "Otra persona", "en": "Somebody else" }
  ],
  "stands": [
    { "es": "Terminado — no queda nada", "en": "Done — nothing left on it" },
    { "es": "Temporal — hay que quitarlo después", "en": "Temp — has to come back out" },
    { "es": "Hay que regresar a terminar — ya salimos de ese piso", "en": "Trip back to finish — we're off that floor" },
    { "es": "Sigue parado — no se termina hasta que lo arreglen", "en": "Still stopped — can't finish till it's fixed" }
  ],
  "why": [
    { "es": "No está en nuestros planos — usted lo pidió", "en": "Not on our prints — you asked for it" },
    { "es": "Nos cerraron el plafón", "en": "Ceiling closed on us" },
    { "es": "Sin plywood / sin backing", "en": "No ply / no backing" },
    { "es": "Nada de rough-in", "sub": "sin tubería, sin caja, sin corriente", "en": "Nothing roughed in" },
    { "es": "El IDF no está listo", "en": "IDF's not ready" },
    { "es": "Otros nos arrancaron el cable / los J-hooks", "en": "Our cable / hooks torn out by others" }
  ]
};
