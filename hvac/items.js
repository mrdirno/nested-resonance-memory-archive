/* HVAC/R FIELD TOOLKIT — VOCABULARY DATA (the repair recommendation).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Component lists,
 * refrigerant labels and the access forget-list live HERE — never in the identity
 * config, never inline in a tool page.
 *
 * FIVE HARD INVARIANTS. The first four are §SAFETY; the fifth is why a tech would
 * use it instead of the notes app.
 *
 *  1. ZERO CERTIFIED DATA. This trade is the worst offender available: no P/T
 *     relationship, no target superheat or subcool, no charge weights, no airflow
 *     or TESP targets, no delta-T "should be", no combustion or CO numbers, no
 *     leak-rate thresholds, no appliance-size cutoffs, no refrigerant-management
 *     trigger rates, no ampacity, no MOCP/MCA, no "in range" anywhere. Not as a
 *     value, not as a hint, not in a placeholder. This page structures what the
 *     TECH read and what the TECH decided. It never tells him a number.
 *  2. IT IS NOT A QUOTE AND NOT A DIAGNOSIS ENGINE. No prices, no rates, no
 *     totals, no labor hours priced, no part costs, no availability claims, no
 *     warranty determination, no cause-of-failure inference. A component picker
 *     names WHAT HE FOUND FAILED — it never suggests what probably failed.
 *  3. NO PRE-SELECTED DEFAULT, ANYWHERE. A default IS a claim, and on a turnover a
 *     claim nobody made becomes the estimator's assumption. Every picker opens on
 *     a neutral (any option leading with an em-dash) and the document drops every
 *     unpicked value.
 *  4. NOTHING OFF THE NAMEPLATE IS GUESSED. Make, model and serial are typed by
 *     the man standing at the plate, never inferred, never decoded — no tonnage
 *     from a model number, no year from a serial. Half the callbacks in this trade
 *     are a decoded model number that was decoded wrong.
 *  5. ZERO BRAND NAMES — and in this trade that is harder than it looks, because
 *     the two most-said words in it are trademarks. "Freon" is a trademark: the
 *     word is REFRIGERANT. "Schrader" is a trademark: the part is a VALVE CORE and
 *     the place is the SERVICE PORT. Also out: every compressor, valve, control and
 *     instrument maker, and VRV (use VRF). Refrigerant designations (R-410A, R-448A)
 *     are ASHRAE numbers, not brands, and are safe.
 *
 * WORDS ARE THE TRADE'S OWN. "Unit", never "equipment asset". "Turnover", never
 * "service opportunity". "Down", never "non-operational". "It's on the plate",
 * never "per the manufacturer's data". A page that says "HVAC system deficiency"
 * tells a tech in three words that nobody who built it has ever been on a roof.
 */
window.TOOLKIT_ITEMS = (function () {
  "use strict";

  /* ── what kind of unit — commercial service reality, air side AND refrigeration.
   * Refrigeration is half of commercial and gets forgotten by every tool built by
   * somebody who only knows rooftops. */
  var EQUIPMENT = [
    "— what kind of unit",
    "Packaged rooftop (RTU)",
    "Split system — condenser + air handler",
    "Heat pump — split",
    "Heat pump — packaged",
    "Air handler (AHU)",
    "Furnace / gas heat",
    "Mini-split / VRF",
    "Fan coil (FCU)",
    "VAV box",
    "Make-up air (MAU)",
    "Exhaust fan",
    "Chiller",
    "Cooling tower",
    "Boiler",
    "Computer room (CRAC / CRAH)",
    "Walk-in cooler",
    "Walk-in freezer",
    "Reach-in / prep table",
    "Display case",
    "Ice machine",
    "Rack / parallel system",
    "Condensing unit — refrigeration",
    "Unit cooler / evaporator",
    "Dehumidifier",
    "Other — see below"
  ];

  /* ── what failed. GROUPED, because a tech knows which side of the unit he is on
   * before he knows the part. Every line is a thing that actually gets turned over
   * — not a parts catalog, and never a symptom (a symptom goes in "what I found",
   * in his words). Optional on purpose: the required field is what he TYPED. */
  var COMPONENTS = [
    { group: "Electrical / controls", items: [
      "Contactor", "Run capacitor", "Start capacitor / hard-start kit", "Transformer",
      "Control board", "Defrost board / timer", "Relay", "Fuse / fuse block",
      "Disconnect", "High-pressure switch", "Low-pressure switch", "Pressure transducer",
      "Float switch / overflow safety", "Thermostat / controller", "Sensor — space, discharge or suction",
      "VFD / drive", "Motor starter / overload", "Wiring / connections — burnt"
    ]},
    { group: "Air side", items: [
      "Blower motor", "Blower wheel", "Condenser fan motor", "Fan blade", "Belt",
      "Sheave / pulley", "Bearings", "Motor mount / isolators", "Filters",
      "Evaporator coil — plugged", "Condenser coil — plugged", "Drain pan",
      "Condensate pump", "Drain line / trap", "Economizer — damper",
      "Economizer — actuator", "Damper linkage", "Curb, panels or gaskets",
      "Duct / flex — disconnected"
    ]},
    { group: "Refrigerant side", items: [
      "Compressor", "Reversing valve", "TXV / metering device", "EEV — valve or coil",
      "Liquid line drier", "Suction drier", "Liquid line solenoid", "Sight glass",
      "Service valve / valve core", "Head pressure control", "Crankcase heater",
      "Accumulator", "Receiver", "Oil separator", "Pressure regulator (EPR)",
      "Leak — evaporator coil", "Leak — condenser coil", "Leak — line set or fittings",
      "Line set / insulation"
    ]},
    { group: "Heat side", items: [
      "Ignitor", "Flame sensor", "Gas valve", "Inducer motor", "Pressure switch — inducer",
      "Rollout switch", "Limit switch", "Heat exchanger", "Burners / manifold",
      "Ignition control board", "Electric heat element", "Heat strip contactor",
      "Flue / vent"
    ]},
    { group: "Refrigeration", items: [
      "Unit cooler fan motor", "Defrost heater", "Defrost termination switch",
      "Door gasket", "Door / frame heater", "Drain line heater", "Case controller",
      "Hot gas / defrost valve", "Condensing unit fan motor"
    ]},
    { group: "Something else", items: [
      "Other — I typed it below"
    ]}
  ];

  /* ── volts / phase, off the plate. A top-five callback and it is ONE tap: the
   * office cannot pull a motor, a contactor or a transformer without it. Spoken
   * "two-oh-eight three-phase" / "four-sixty three" / "five seventy-five". */
  var VOLTS = [
    "— volts / phase",
    "115-1", "208/230-1", "208/230-3", "460-3", "575-3"
  ];

  /* ── refrigerant. ASHRAE designations only — the word "Freon" is a trademark and
   * never appears on this site. This is a LABEL for what is in the unit, never a
   * charge, a pressure or a threshold. */
  var REFRIGERANTS = [
    "— refrigerant (off the plate)",
    "R-410A", "R-22", "R-32", "R-454B", "R-448A", "R-449A", "R-404A",
    "R-407C", "R-134a", "R-513A", "R-744 (CO2)", "R-717 (ammonia)",
    "Not on the plate / unreadable",
    "N/A — no refrigerant"
  ];

  /* ── THE IMPACT LINE, ONE TAP. Five trades' worth of research say the same thing:
   * "what fails if it isn't done" is the single most-omitted field on a turnover,
   * and it is the one the estimator uses to sell the repair. Typing it is exactly
   * the friction that makes it get skipped at 4:45 on a Friday — so it gets chips.
   * Each one APPENDS to what he already wrote; nothing is pre-selected, because a
   * consequence nobody claimed must never reach the office. Capped at 6: past that
   * a chip row wraps into a wall and ticking stops beating typing. */
  var CONSEQUENCE_CHIPS = [
    "It stays down until this is fixed.",
    "It'll take the compressor out.",
    "They'll lose product.",
    "It'll trip again on the next hot day.",
    "They'll keep calling us back for the same thing.",
    "Nothing right now — but it won't hold."
  ];

  /* ── HOW WE GET TO IT — the forget-list, and the reason this page exists at all.
   * Access is what turns a $400 motor into a $2,400 job, and it is the thing the
   * office finds out about on the day of the repair instead of the day of the
   * quote. Ticking beats typing: fifteen boxes he scans in eight seconds. */
  /* `sub` is NOT decoration: it rides into the sent document in parentheses,
   * because "Boom / man lift" without "has to be rented" is the cost signal
   * deleted. So every sub here is worth sending, or it is empty. */
  var ACCESS = [
    { name: "Roof hatch",                    sub: "" },
    { name: "Ladder — extension",            sub: "not the one on the truck" },
    { name: "Roof access through the space", sub: "we go through the tenant" },
    { name: "Scissor lift",                  sub: "" },
    { name: "Boom / man lift",               sub: "has to be rented" },
    { name: "Crane pick",                    sub: "" },
    { name: "Two men just to get it up there", sub: "" },
    { name: "After hours only",              sub: "" },
    { name: "They have to shut it down",     sub: "line, case or the whole store" },
    { name: "Badge, escort or check-in",     sub: "" },
    { name: "Locked — keys are with them",   sub: "" },
    { name: "Confined space",                sub: "" },
    { name: "Lockout required",              sub: "" },
    { name: "Dog on site",                   sub: "" },
    { name: "Parking or the dock is a problem", sub: "" }
  ];

  /* ── what the office has to line up before anybody drives back. A forget-list,
   * and deliberately NOT priced: what has to happen, never what it costs.
   * "Two men" is NOT here — it is an ACCESS tick, because it is handling, not
   * labour hours, and the moment this page collects hours the tech is estimating
   * his own two hands and the customer anchors on it.
   * The last two came out of the panel and neither is obvious: warranty is a
   * documents question a tech should flag and never answer, and a replacement
   * quote goes to a completely different approver than a repair. */
  var NEEDS = [
    { name: "Part has to be ordered",             sub: "" },
    { name: "Recovery + recharge",                sub: "cylinder and scale on the truck" },
    { name: "Brazing — hot work permit",          sub: "" },
    { name: "Return trip",                        sub: "not getting done same-day" },
    { name: "Rental — lift or crane",             sub: "" },
    { name: "PO or sign-off before we go back",   sub: "" },
    { name: "Check warranty on this serial",      sub: "I'm not calling it" },
    { name: "It's been repaired before",          sub: "price a replacement too" }
  ];

  /* ── SHOOT THESE NOW. Three, not six: three get taken, six is a form telling a
   * man how to do his job. It sits at the TOP of the page because he is standing
   * at the plate right now and he will not climb back up for it. Nothing is
   * uploaded — he texts the photos with the paste, and a tool's uploads never
   * leave the browser anyway. */
  var PHOTOS = [
    { name: "The data plate",              sub: "the one that gets forgotten" },
    { name: "The failed part and its tag", sub: "" },
    { name: "The way up",                  sub: "shows the access" }
  ];

  return {
    equipment: EQUIPMENT,
    components: COMPONENTS,
    volts: VOLTS,
    refrigerants: REFRIGERANTS,
    consequenceChips: CONSEQUENCE_CHIPS,
    access: ACCESS,
    needs: NEEDS,
    photos: PHOTOS
  };
})();

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working HVAC hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · REFRIGERANT GETS ITS OWN ROW and never hides inside material. A contactor
   *    leaves a carton with a number printed on it; seven pounds of 448 leaves a
   *    lighter cylinder and the tech's memory, and by Thursday nobody can rebuild
   *    it. Type by ASHRAE number only (they are designations, not brands), pounds,
   *    and recovered vs added — no leak rate, no threshold, no trigger, ever.
   *  · THE HEADING IS JUST "T&M TAG". The in-trade reviewer cut "— OUT OF SCOPE"
   *    off it: no tech has ever typed those words into a text message, and it is
   *    the first two words that tell a super a system wrote this instead of the guy
   *    he was standing next to five minutes ago.
   *  · WHAT I FOUND HAS A WRITE-IN UNDER IT, always. On a roof with gloves on and
   *    the super waiting, the moment his finding isn't in the chip row and the
   *    keyboard comes up anyway, texting the super direct is faster than this page.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "Site contact / store mgr",
    "Facilities / building eng",
    "GC super",
    "Our dispatch / service mgr",
    "Owner / tenant",
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
  "found": [
    {
      "name": "Comp's grounded / locked rotor"
    },
    {
      "name": "Motor's shot",
      "sub": "cond fan or blower"
    },
    {
      "name": "Contactor / starter burnt up"
    },
    {
      "name": "It's leaking — low on charge"
    },
    {
      "name": "Board's dead — no control"
    },
    {
      "name": "Drain's plugged — water in the ceiling"
    },
    {
      "name": "Box is warming",
      "sub": "defrost or door heater"
    },
    {
      "name": "It's unsafe — I've got it locked out"
    }
  ],
  "why": [
    {
      "name": "Not in the PM — this is a repair"
    },
    {
      "name": "Not what the WO was written for"
    },
    {
      "name": "Was like that when we got here"
    },
    {
      "name": "Another trade got into it"
    },
    {
      "name": "Repair parts aren't in the agreement"
    },
    {
      "name": "Can't finish what I was sent for till this is done"
    }
  ],
  "right": [
    {
      "v": "It's down",
      "hot": 1
    },
    {
      "v": "Still running"
    },
    {
      "v": "Running, won't hold"
    },
    {
      "v": "Off and tagged — I shut it down",
      "hot": 1
    }
  ],
  "classes": [
    "— class",
    "TECH",
    "HELPER",
    "APPRENTICE"
  ],
  "refs": [
    "— type",
    "R-410A",
    "R-454B",
    "R-32",
    "R-448A",
    "R-449A",
    "R-404A",
    "R-134a",
    "R-22",
    "R-407C",
    "R-513A",
    "R-744 (CO2)",
    "R-717 (NH3)"
  ],
  "refdir": [
    "— which way",
    "Recovered",
    "Added"
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
  toolName: "The By-Others List",
  eyebrow: "HVAC/R · you → the other trades",
  lede: "Everything I need from somebody else before it gets covered up — who owes it, where it is, and what gate it has to beat. Not an RFI. It's the list I text the other foreman.",
  docSubject: "By others — what we need before it's covered",
  docSubjectWith: "By others — what we need from {to}",
  closing: "That's the whole list. Reply with what you can hit and what you can't — I'd rather move a hole on paper today than core it after you pour. Call me on anything that doesn't read right.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> drawings and off the nameplate. This page sizes nothing — no breaker, no whip, no pipe, no curb, no load — it asserts no clearance and no rating, and it doesn't know what the code, the engineer or the manufacturer requires. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C",
  phOff: "M-301 rev 2",
  phFrom: "Manny — Apex Mechanical",
  phArea: "RTU-4 — then it's a button",
  areaLabel: "Unit / area",

  who: [
    { v: "ec", label: "Electrician" },
    { v: "gc", label: "GC super" },
    { v: "pc", label: "Plumber" },
    { v: "roofer", label: "Roofer" },
    { v: "atc", label: "Controls / ATC" },
    { v: "fa", label: "Fire alarm" },
    { v: "steel", label: "Steel / dunnage" },
    { v: "framer", label: "Framer/drywall" },
    { v: "conc", label: "Concrete" }
  ],

  // EARLIEST FIRST — this is the order a job actually closes up in, and it is
  // why grouping by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "pour", label: "Before the pour" },
    { v: "deck", label: "Before deck goes on" },
    { v: "dryin", label: "Before roof dry-in" },
    { v: "crane", label: "Before crane day" },
    { v: "rock", label: "Before they rock it" },
    { v: "lid", label: "Before the ceiling closes" },
    { v: "startup", label: "Before startup" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "disc", label: "Disconnect at the unit", who: "ec", by: "startup", specs: [
      "I'll send the nameplate photo — you pick it",
      "Weatherproof, it's on the roof",
      "In sight of the unit, not behind it",
      "On a strut stand, not on the cabinet",
      "Reuse the one that's already there"
    ] },
    { v: "whip", label: "Whip to the unit", who: "ec", by: "startup", specs: [
      "Liquidtight, outdoor",
      "Long enough to reach the corner post",
      "Land it in the unit, don't leave it coiled",
      "Leave slack — it sits on isolators",
      "Through the curb, not over the roof",
      "Just stub it, I'll make the final"
    ] },
    { v: "tstat", label: "T-stat box + conduit", who: "ec", by: "rock", specs: [
      "Box and a stub above the ceiling",
      "Where I marked it, not where it's drawn",
      "Pull string left in the pipe",
      "Ring only, I'll trim it out",
      "Ganged with the light switch",
      "Sensor box, not a t-stat box"
    ] },
    { v: "cond", label: "Condensate tie-in", who: "pc", by: "lid", specs: [
      "Give me a stub I can trap off",
      "Indirect to the floor sink",
      "Primary and secondary, both stubbed",
      "I'm pumping to it — has to be up high"
    ] },
    { v: "pwr120", label: "Power for my controls", who: "ec", by: "lid", specs: [
      "Dedicated circuit, no taps off my unit",
      "Land it in my control panel",
      "For the condensate pump",
      "For the VFD or starter",
      "Voltage off my nameplate — I'll send it",
      "Homerun, don't daisy-chain the boxes"
    ] },
    { v: "access", label: "Access door for me", who: "gc", by: "lid", specs: [
      "Hard lid — I have to reach the box",
      "Lay-in tile is fine, just mark it",
      "In the wall at my damper",
      "Under the unit, not off to the side",
      "Big enough for my arm and a meter",
      "One at each box — I'll mark them"
    ] },
    { v: "block", label: "Blocking in the wall", who: "framer", by: "rock", specs: [
      "Behind the wall unit, before rock",
      "Solid backing, not just a stud",
      "I'll mark the height on the studs",
      "For the head — it's heavy, use plywood",
      "Bracket for the unit heater, up high",
      "Both sides — units are back to back"
    ] },
    { v: "curb", label: "Curb set + flashed", who: "roofer", by: "dryin", specs: [
      "Curb's set — needs flashing only",
      "You're setting it, curb's on site",
      "Flash it before we take rain",
      "Roof slopes here — pitched curb",
      "Cant and cap per your detail",
      "Don't close it till my duct drops in"
    ] },
    { v: "louver", label: "Louver opening", who: "framer", by: "rock", specs: [
      "R.O. per my markup, I'll paint it",
      "Don't close it till my duct's through",
      "Head and sill framed, not just cut",
      "Who's flashing it — you or the skin guy?"
    ] },
    { v: "core", label: "Core drill", who: "gc", by: "rock", specs: [
      "I'll mark it, you core it",
      "Scan it first — it's post-tension",
      "Line set and condensate, two holes",
      "Room for the pipe plus insulation",
      "Through the wall, not the deck",
      "Who's firestopping it, you or me?"
    ] },
    { v: "gas", label: "Gas to the unit", who: "pc", by: "startup", specs: [
      "Stub it at the curb, I'll take it in",
      "Drip leg and union at my connection",
      "Shutoff within reach of the unit",
      "Off the roof header that's already up",
    ] },
    { v: "opening", label: "Roof opening cut", who: "steel", by: "deck", specs: [
      "I'll lay it out, you cut it",
      "Frame it while the deck's still open",
      "Size off my shop drawing",
      "Supply and return, two holes",
      "Curb lands on it — keep it square",
      "Don't cut till I paint the layout"
    ] },
    { v: "ctlwire", label: "Controls wire to unit", who: "atc", by: "lid", specs: [
      "Get it in before the lid goes up",
      "Land it in my unit, I'll terminate",
      "You're pulling it, not me — confirm",
      "Sensor wire to the box I set",
      "It's pulled, just needs terminating",
      "Point-to-point before I start up"
    ] },
    { v: "fadet", label: "Duct detector wiring", who: "fa", by: "startup", specs: [
      "Detector's in the duct, needs wiring",
      "Land the shutdown at my unit",
      "Remote test switch — you place it",
      "Has to work before I can start up"
    ] },
    { v: "sleeve", label: "Sleeve/pad in the pour", who: "gc", by: "pour", specs: [
      "Sleeve for my line set",
      "Sleeve for the condensate run",
      "Pad under the unit — I'll mark it",
      "Pad wide enough to walk around it",
      "Leave the sleeve proud of the pour",
      "Call me the day before you pour"
    ] },
    { v: "dunnage", label: "Dunnage / stand", who: "steel", by: "crane", specs: [
      "Set it before crane day, not after",
      "I'll send you the unit footprint",
      "Level it — the roof isn't",
      "High enough to work under it",
      "Rails run the long way on the unit",
      "Isolators on top, I'll bring them"
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
  toolName: "My Answer on Your List",
  eyebrow: "HVAC/R · them → you → back",
  lede: "Somebody sent you a list — the GC, the EC, the controls guy. Line it up, say what you’ll hit and when, flag what you can’t, and send it back as one answer.",
  docSubject: "mechanical — my answer on your list",
  closing: "That’s my answer on the whole list. The flagged ones I need back from you — the unit doesn’t care whose gate it missed, and neither does the crane.",
  phJob: "Building C", phTo: "Dave — Local 3", phFrom: "Manny — Apex Mechanical", phOff: "E-201 rev 3",
  paste: "Building C — what we need from mechanical — Aug 9\n\nJob: Building C\nFrom: Dave — Local 3\n\nRoof · your unit weights and disconnect locations before we rough the whips\nMech 210 · t-stat box locations before rock\nRoof · confirm curb heights before dry-in"
};

/* ── THE VAN RESTOCK (shape #1 — shared/checklist-request.js) ──────────────
 * The vocabulary for truck-stock.html. Written by a panel of commercial service
 * and refrigeration hands, then cut by a second one told to kill about a third:
 * 55 lines proposed, 37 kept, 18 killed.
 *
 *  · THE CATEGORIES ARE SOMEBODY'S ACTUAL VAN, not a supply-house catalog. A
 *    tick that does not correspond to a bin on a truck is a tick nobody makes.
 *  · qtyDefault IS THE POINT OF THIS PAGE. A van does not restock one of
 *    everything — caps go four at a time, contactors two. Defaults are set the
 *    way a truck really fills and left OFF the lines that genuinely vary, which
 *    is the one thing this page has that a text message does not.
 *  · REFRIGERATION IS HALF OF COMMERCIAL and gets forgotten by every tool built
 *    by somebody who has only seen a rooftop. It gets its own section.
 *  · ZERO TRADEMARKS, and in this trade that is harder than it sounds: the two
 *    most-said words on the job are both trademarks. It is REFRIGERANT, and it
 *    is a VALVE CORE at a SERVICE PORT. Refrigerant DESIGNATIONS (R-410A,
 *    R-448A) are ASHRAE numbers, not brands, and are safe.
 *  · NOTHING RATED, EVER. No charge amounts, no leak-rate thresholds, no target
 *    superheat, no appliance-size cutoffs — not in an option, not in a sub, not
 *    seeded in a placeholder. What is on the plate gets TYPED by the man
 *    standing at the plate.
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
      hint: "Type it or paste your whole list — one per line. Quantities however you say them: 4, a bag, a case, 2 sticks.",
      writein: true,
      items: []
    },
    {
      id: "ctrl",
      name: "Caps, contactors & controls",
      docName: "Caps, contactors & controls",
      hint: "The cheap parts that keep a store closed. This is what the van eats fastest.",
      items: [
        { n: "Caps", sub: "MFD OFF THE OLD ONE GOES IN THE NOTE", qtyDefault: "4",
          ax: [
            ax("Cap", [n("which cap")].concat(["dual run", "single run", "start", "hard-start kit"]), true)
          ] },
        { n: "Contactors", sub: "POINTS PIT AND IT'S A NO-COOL AT 2 IN THE AFTERNOON", qtyDefault: "2",
          ax: [
            ax("Poles", [n("which poles")].concat(["1-pole", "2-pole", "3-pole"])),
            ax("Coil", [n("which coil")].concat(["24V", "120V", "line voltage"]))
          ] },
        { n: "Relays", sub: "FAN, BLOWER, AND SEQUENCERS FOR THE STRIP HEAT", qtyDefault: "2" },
        { n: "Transformers", sub: "SAY PRIMARY AND SECONDARY IN THE NOTE", qtyDefault: "2" },
        { n: "T-stat wire", sub: "AND A BAG OF WIRE NUTS, SPADES AND BUTTS", qtyDefault: "1 roll",
          ax: [
            ax("Wire", [n("which wire")].concat(["4-wire", "5-wire", "8-wire"]), true)
          ] }
      ]
    },
    {
      id: "sealed",
      name: "The sealed side",
      docName: "Refrigerant, driers & valve parts",
      hint: "Say the number, not the color of the jug.",
      items: [
        { n: "Refrigerant", sub: "BY THE NUMBER — SAY IT, DON'T GUESS IT",
          ax: [
            ax("Which", [n("which number")].concat(["R-410A", "R-22", "R-134a", "R-404A", "R-407C", "R-448A", "R-449A", "R-454B"]), true)
          ] },
        { n: "Nitro", sub: "BOTTLE SWAP — AND A REGULATOR IF MINE WALKED OFF", qtyDefault: "1 bottle" },
        { n: "Driers", qtyDefault: "2",
          ax: [
            ax("Size", [n("which size")].concat(["1/4 in", "3/8 in", "1/2 in", "5/8 in", "7/8 in"])),
            ax("Connection", [n("which connection")].concat(["sweat", "flare"]))
          ] },
        { n: "Valve cores & caps", sub: "BY THE BAG — THEY VANISH", qtyDefault: "1 bag" },
        { n: "Compressor oil", qtyDefault: "1 qt",
          ax: [
            ax("Oil", [n("which oil")].concat(["POE", "mineral", "AB"]), true)
          ] },
        { n: "Bubbles", sub: "SOAP FOR LEAKS — THE BOTTLE ALWAYS ENDS UP IN SOMEBODY ELSE'S TRUCK", qtyDefault: "1 bottle" }
      ]
    },
    {
      id: "braze",
      name: "Braze, tube & fittings",
      docName: "Braze, tube & fittings",
      hint: "Nobody has ever gotten to a braze and found the truck full.",
      items: [
        { n: "Braze rod", qtyDefault: "1 tube",
          ax: [
            ax("Rod", [n("which rod")].concat(["phos-copper", "15% silver", "45% silver"]), true)
          ] },
        { n: "Copper tube",
          ax: [
            ax("Size", [n("which size")].concat(["1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "7/8 in", "1-1/8 in"])),
            ax("Form", [n("which form")].concat(["soft roll", "hard — 20 ft", "hard — 10 ft"]), true)
          ] },
        { n: "Copper fittings", qtyDefault: "10",
          ax: [
            ax("Size", [n("which size")].concat(["1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "7/8 in", "1-1/8 in"])),
            ax("Fitting", [n("which fitting")].concat(["coupling", "90", "45", "tee", "reducer", "cap"]), true)
          ] },
        { n: "Torch fuel & tips", sub: "SWAP THE EMPTY B-TANK — AND A STRIKER", qtyDefault: "1 tank" },
        { n: "Sand cloth, flux & brushes", sub: "THE FIVE-MINUTE REASON A JOINT LEAKS", qtyDefault: "1 each" }
      ]
    },
    {
      id: "air",
      name: "Air side",
      docName: "Air side — belts, filters, gas heat",
      hint: "Half of tomorrow is a belt, a filter and a flame sensor.",
      items: [
        { n: "Belts", sub: "NUMBER'S ON THE OLD ONE — PUT IT IN THE NOTE", qtyDefault: "2" },
        { n: "Filters", sub: "SIZES IN THE NOTE — THE RACK NEVER MATCHES THE PRINT" },
        { n: "Motors", sub: "CONDENSER, BLOWER, CASE FAN — THE PLATE AND THE BLADE GO IN THE NOTE", qtyDefault: "1" },
        { n: "Igniters", sub: "THEY BREAK IF YOU LOOK AT THEM WRONG", qtyDefault: "2" },
        { n: "Flame sensors", sub: "AND A PAD TO SCUFF THE OLD ONE", qtyDefault: "2" }
      ]
    },
    {
      id: "ref",
      name: "Boxes & defrost",
      docName: "Refrigeration — boxes & defrost",
      hint: "Half of commercial is refrigeration, and it's the half that's down at 5 in the morning.",
      items: [
        { n: "Term & fan delay switches", sub: "DEFROST — SAY WHAT'S STAMPED ON THE OLD ONE", qtyDefault: "2" },
        { n: "Defrost timers", sub: "MECHANICAL AND ELECTRONIC", qtyDefault: "1" },
        { n: "Box controls & probes", sub: "AND THE CLIPS THAT HOLD THE PROBE", qtyDefault: "1" },
        { n: "Crankcase heaters", sub: "THE ONE THAT'S ALWAYS COOKED OFF", qtyDefault: "1" }
      ]
    },
    {
      id: "drain",
      name: "Drains, seal & tape",
      docName: "Drains, seal & tape",
      hint: "The callback that isn't a callback: water on somebody's floor.",
      items: [
        { n: "Condensate pumps", qtyDefault: "1" },
        { n: "Float & wet switches", sub: "CHEAPER THAN A CEILING", qtyDefault: "2" },
        { n: "PVC — pipe, fittings & glue",
          ax: [
            ax("Size", [n("which size")].concat(["1/2 in", "3/4 in", "1 in", "1-1/4 in"]))
          ] },
        { n: "Coil cleaner", qtyDefault: "1 gal",
          ax: [
            ax("Cleaner", [n("which cleaner")].concat(["evap / no-rinse", "condenser"]), true)
          ] },
        { n: "Foil tape", sub: "NOT THE CLOTH TAPE — IT FALLS OFF BY AUGUST", qtyDefault: "2 rolls" },
        { n: "Line insulation & glue", sub: "FOAM SLEEVE — THE ROOF EATS IT",
          ax: [
            ax("Size", [n("which size")].concat(["1/4 in", "3/8 in", "1/2 in", "5/8 in", "3/4 in", "7/8 in", "1-1/8 in"]))
          ] }
      ]
    },
    {
      id: "wear",
      name: "What wears out",
      docName: "Blades, bits & what wears out",
      hint: "Not material. Still the thing that ends the day at nine in the morning.",
      items: [
        { n: "Recip blades", sub: "METAL — THE BOX IS ALWAYS EMPTY", qtyDefault: "1 pk" },
        { n: "Nut driver bits & extensions", sub: "1/4 AND 5/16 — THE TWO THAT WALK OFF", qtyDefault: "1 pk" },
        { n: "Self-drillers & sheet metal screws", qtyDefault: "1 box" },
        { n: "Vacuum pump oil", sub: "AND A JUG TO DUMP THE OLD ONE IN", qtyDefault: "1 qt" },
        { n: "Wire ties, tape & markers", sub: "AND SOMETHING TO WRITE ON THE UNIT WITH", qtyDefault: "1 bag" },
        { n: "Gloves & batteries", sub: "METER, CAMERA, FLASHLIGHT", qtyDefault: "1 box" }
      ]
    }
  ];

  window.TOOLKIT_ITEMS.writeinAx = [
  ];
})();


/* GETTING IN (getting-in.html) — same boundary as AV's: the building engineer,
 * not another trade, and the same handback rule on every permit-adjacent tick.
 * What's actually this trade's own: the second locked space is the mechanical
 * room or penthouse, not a rack room, and four of the eleven heads-up ticks are
 * ours — roof access and the hatch, brazing (our hot work), a duct detector
 * sitting on the building's fire alarm, and the unit going down while we're on
 * it, because a service call that kills somebody's air for four hours is the
 * one heads-up this trade can't ship without.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "HVAC/R · you → whoever holds the keys",
  lede: "You need onto a roof or into a room somebody else locks. Send the ask that gets a yes on the first try — the night, the spaces, who’s coming, and the heads-up that stops a crew getting turned around at the door.",
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
    { name: "The mechanical room / penthouse open too", sub: "not just the space we’re working in" },
    { name: "Somebody who knows which unit’s which", sub: "the roof tag and the work order don’t always match" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" }
  ],

  /* BEFORE YOU SAY YES. The top of this list is a courtesy; the bottom of it is
     the reason a crew gets thrown off a site for good. Read the subs: the last
     four do not report a state, they ask him how he wants it run. */
  heads: [
    { name: "It’ll be loud", sub: "anchors, cores — say the word and we’ll move it later" },
    { name: "Dust", sub: "coring and cutting — tell me what barrier you want up" },
    { name: "Ceiling tiles out", sub: "I’ll tell you which corridor and for how long" },
    { name: "Working over your furniture", sub: "lift or ladder above desks" },
    { name: "The corridor gets tight", sub: "gear staged while we’re in" },
    { name: "We’ll set off motion and door contacts", sub: "after hours, moving between rooms" },
    { name: "The unit’s down while we’re on it", sub: "space runs without heat or cool till we’re back — tell me if that’s a problem" },
    { name: "Roof access", sub: "tell me which hatch and who walks it with us" },
    { name: "Something has to come off power", sub: "your engineer throws it, not us — tell me the window" },
    { name: "A duct detector on your fire alarm", sub: "tell me who puts the panel on test — we don’t" },
    { name: "Hot work — brazing", sub: "that’s your permit — tell me how you want it done" }
  ],

  phSite: "Building C",
  phRoom: "Mech Room 2",
  phHow: "basement, past the electrical room",
  phScope: "changing the compressor on the air handler",
  phLoud: "core drill for the new line set, maybe 20 min",
  phTo: "Ray — building engineer",
  phMe: "Manny R — 510-555-0148",
  phCo: "Apex Mechanical",

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
    { "es": "TÉCNICO (TECH)", "en": "TECH" },
    { "es": "AYUDANTE (HELPER)", "en": "HELPER" },
    { "es": "APRENDIZ (APPR)", "en": "APPRENTICE" }
  ],
  "found": [
    { "es": "Comp aterrizado / rotor trabado", "en": "Comp's grounded / locked rotor" },
    { "es": "Motor quemado", "sub": "ventilador del condensador o blower", "en": "Motor's shot" },
    { "es": "Contactor / arrancador quemado", "en": "Contactor / starter burnt up" },
    { "es": "Tiene fuga — le falta carga", "en": "It's leaking — low on charge" },
    { "es": "La tarjeta está muerta — sin control", "en": "Board's dead — no control" },
    { "es": "Drenaje tapado — agua en el plafón", "en": "Drain's plugged — water in the ceiling" },
    { "es": "La caja se está calentando", "sub": "defrost o calentador de puerta", "en": "Box is warming" },
    { "es": "No es seguro — lo tengo con lockout", "en": "It's unsafe — I've got it locked out" }
  ],
  "how": [
    { "es": "Me lo dijo en el sitio", "en": "Told me on site" },
    { "es": "Teléfono", "en": "Phone" },
    { "es": "Texto", "en": "Text" },
    { "es": "Correo", "en": "Email" }
  ],
  "refdir": [
    { "es": "— para dónde", "en": "— which way" },
    { "es": "Recuperado (Recovered)", "en": "Recovered" },
    { "es": "Agregado (Added)", "en": "Added" }
  ],
  "refs": [
    { "es": "— tipo", "en": "— type" },
    { "es": "R-410A", "en": "R-410A" },
    { "es": "R-454B", "en": "R-454B" },
    { "es": "R-32", "en": "R-32" },
    { "es": "R-448A", "en": "R-448A" },
    { "es": "R-449A", "en": "R-449A" },
    { "es": "R-404A", "en": "R-404A" },
    { "es": "R-134a", "en": "R-134a" },
    { "es": "R-22", "en": "R-22" },
    { "es": "R-407C", "en": "R-407C" },
    { "es": "R-513A", "en": "R-513A" },
    { "es": "R-744 (CO2)", "en": "R-744 (CO2)" },
    { "es": "R-717 (NH3)", "en": "R-717 (NH3)" }
  ],
  "right": [
    { "es": "Está parada", "en": "It's down" },
    { "es": "Sigue corriendo", "en": "Still running" },
    { "es": "Corre, pero no aguanta", "en": "Running, won't hold" },
    { "es": "Apagada y etiquetada — yo la apagué", "en": "Off and tagged — I shut it down" }
  ],
  "roles": [
    { "es": "Contacto del sitio / gerente de tienda", "en": "Site contact / store mgr" },
    { "es": "Facilities / ingeniero del edificio", "en": "Facilities / building eng" },
    { "es": "El súper del GC", "en": "GC super" },
    { "es": "Nuestro dispatch / gerente de servicio", "en": "Our dispatch / service mgr" },
    { "es": "Dueño / inquilino", "en": "Owner / tenant" },
    { "es": "Otra persona", "en": "Somebody else" }
  ],
  "why": [
    { "es": "No está en el PM — esto es reparación", "en": "Not in the PM — this is a repair" },
    { "es": "La WO no se escribió para esto", "en": "Not what the WO was written for" },
    { "es": "Así estaba cuando llegamos", "en": "Was like that when we got here" },
    { "es": "Otro oficio le anduvo moviendo", "en": "Another trade got into it" },
    { "es": "Las partes de reparación no están en el contrato", "en": "Repair parts aren't in the agreement" },
    { "es": "No puedo terminar lo que me mandaron a hacer hasta que esto quede", "en": "Can't finish what I was sent for till this is done" }
  ]
};
