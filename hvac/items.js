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
