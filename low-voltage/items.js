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
