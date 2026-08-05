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
