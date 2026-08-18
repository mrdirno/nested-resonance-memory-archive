/* GC & SITE SUPER FIELD TOOLKIT — the trade's VOCABULARY DATA.
 *
 * §THE THREE SHAPES keeps this boundary or the config rots:
 *   trade.js  = IDENTITY + COPY
 *   tools.js  = REGISTRY
 *   items.js  = THIS — the trade's vocabulary (who is on the job, what is in the
 *               wall, what has to be signed off before it closes).
 * Never inline any of it in a tool page and never smuggle it into trade.js.
 *
 * TRADEMARK PASS APPLIED (§SCARS — "half a trade's vocabulary is somebody's
 * trademark"). Everything below is a generic trade or scope word. Deliberately
 * NOT here even though supers say them out loud every day: brand names for
 * board, tape, anchors, blades, sealants and firestop products. Every line names
 * WORK, not a product.
 *
 * NOTHING HERE IS CERTIFIED DATA (§SAFETY). There are no code references, no
 * inspection requirements, no clearances, no ratings and no "required by" claims.
 * These are memory joggers for a super who already knows his job — the page
 * organises what HE ticks, and it never asserts what a jurisdiction wants.
 */

/* ── WHO IS ON THE JOB ──────────────────────────────────────────────────────
 * The subs a super chases, in the words he uses on the radio — "the mechanical
 * guy", "fire protection", "low-vol". Ordered roughly the way a building goes
 * together, not alphabetically, because that is the order he walks it.
 * `wall` marks the trades that have work INSIDE a wall or a slab, which is the
 * set that matters when something is about to be covered up. */
window.GC_SUBS = [
  { id: "earthwork",   name: "Earthwork / excavation" },
  { id: "siteutil",    name: "Site utilities / underground",  wall: true },
  { id: "concrete",    name: "Concrete / flatwork",           wall: true },
  { id: "masonry",     name: "Masonry",                       wall: true },
  { id: "steel",       name: "Steel / misc metals",           wall: true },
  { id: "framing",     name: "Framing / carpentry",           wall: true },
  { id: "plumbing",    name: "Plumbing",                      wall: true },
  { id: "mechanical",  name: "Mechanical / HVAC",             wall: true },
  { id: "sheetmetal",  name: "Sheet metal",                   wall: true },
  { id: "controls",    name: "Controls / BAS",                wall: true },
  { id: "electrical",  name: "Electrical",                    wall: true },
  { id: "fireprot",    name: "Fire protection / sprinkler",   wall: true },
  { id: "firealarm",   name: "Fire alarm",                    wall: true },
  { id: "lowvolt",     name: "Low-voltage / data",            wall: true },
  { id: "security",    name: "Security / access control",     wall: true },
  { id: "av",          name: "AV",                            wall: true },
  { id: "elevator",    name: "Elevator" },
  { id: "insulation",  name: "Insulation",                    wall: true },
  { id: "firestop",    name: "Firestopping / fireproofing",   wall: true },
  { id: "waterproof",  name: "Waterproofing",                 wall: true },
  { id: "drywall",     name: "Drywall / taping" },
  { id: "ceilings",    name: "Acoustical ceilings" },
  { id: "doors",       name: "Doors / frames / hardware" },
  { id: "glazing",     name: "Glass & glazing" },
  { id: "millwork",    name: "Millwork / casework" },
  { id: "flooring",    name: "Flooring" },
  { id: "painting",    name: "Painting" },
  { id: "specialties", name: "Specialties / accessories" },
  { id: "roofing",     name: "Roofing" },
  { id: "landscape",   name: "Landscaping / hardscape" },
  { id: "signage",     name: "Signage" }
];

/* ── WHAT IS IN THE WALL ────────────────────────────────────────────────────
 * The pre-cover forget-list, grouped by whose work it is. This is the load-
 * bearing content of the whole page: a super does not forget that plumbing has
 * rough in the wall, he forgets the ONE line item on somebody else's list —
 * which is why the list is per-trade and why BACKING has its own long tail.
 *
 * Each entry: sub id it belongs to · the line as a super would say it.
 * `hot` marks the ones that most often come back out of a closed wall. */
window.GC_INWALL = [
  { sub: "plumbing",   line: "Supply rough in and tested",            hot: true },
  { sub: "plumbing",   line: "Waste & vent rough in and tested",      hot: true },
  { sub: "plumbing",   line: "Carriers / fixture supports set" },
  { sub: "plumbing",   line: "Hose bibbs, floor drains, cleanouts" },
  { sub: "plumbing",   line: "Insulation on the lines that need it" },

  { sub: "electrical", line: "Boxes set and at the right height",     hot: true },
  { sub: "electrical", line: "Raceway / conduit in the wall" },
  { sub: "electrical", line: "Homeruns pulled" },
  { sub: "electrical", line: "Grounding / bonding in place" },
  { sub: "electrical", line: "Anything feeding equipment on the wall" },

  { sub: "mechanical", line: "Duct in the wall / chase" },
  { sub: "mechanical", line: "Refrigerant lines and condensate",      hot: true },
  { sub: "mechanical", line: "Sleeves and louvre openings" },
  { sub: "controls",   line: "Control wire and sensor boxes" },

  { sub: "fireprot",   line: "Drops and armovers roughed" },
  { sub: "fireprot",   line: "Standpipe / riser work in the wall" },
  { sub: "firealarm",  line: "Device boxes and conduit",              hot: true },
  { sub: "lowvolt",    line: "Rings and pull string" },
  { sub: "lowvolt",    line: "Conduit stubs out of the wall" },
  { sub: "security",   line: "Door position / reader rough" },
  { sub: "av",         line: "Boxes, conduit and slack behind displays" },

  /* BACKING is the single most expensive thing to forget: nothing about a closed
   * wall says whether there is wood behind it, and every one of these lands
   * MONTHS later when a finish trade shows up with nothing to screw to. */
  { sub: "framing",    line: "Backing — wall-mounted displays / monitors", hot: true },
  { sub: "framing",    line: "Backing — casework and shelving",            hot: true },
  { sub: "framing",    line: "Backing — grab bars and toilet accessories", hot: true },
  { sub: "framing",    line: "Backing — handrails and guardrails" },
  { sub: "framing",    line: "Backing — mirrors, boards, corner guards" },
  { sub: "framing",    line: "Backing — extinguisher cabinets, door stops" },
  { sub: "framing",    line: "Backing — equipment the owner is furnishing" },
  { sub: "framing",    line: "Blocking at heads, jambs and bracing" },

  { sub: "insulation", line: "Batt / sound attenuation in" },
  { sub: "insulation", line: "Vapor barrier where it belongs" },
  { sub: "firestop",   line: "Penetrations sealed" },
  { sub: "waterproof", line: "Wet-wall protection in" },
  { sub: "steel",      line: "Embeds, clips and misc metal set" }
];

/* ── WHAT IS IN THE SLAB ────────────────────────────────────────────────────
 * The pre-pour version. Same idea, different burial. A miss here is a saw and a
 * patch at best, a core through somebody's conduit at worst. */
window.GC_INSLAB = [
  { sub: "plumbing",   line: "Underslab waste in and tested",        hot: true },
  { sub: "plumbing",   line: "Water / gas underslab" },
  { sub: "electrical", line: "Underslab conduit and stub-ups",       hot: true },
  { sub: "electrical", line: "Floor boxes set to finish" },
  { sub: "electrical", line: "Grounding electrode / ground ring" },
  { sub: "lowvolt",    line: "Conduit and pull string underslab" },
  { sub: "mechanical", line: "Radiant tubing / underslab duct" },
  { sub: "concrete",   line: "Sleeves and blockouts",                hot: true },
  { sub: "concrete",   line: "Vapor barrier in and patched" },
  { sub: "concrete",   line: "Reinforcing, dowels and chairs" },
  { sub: "steel",      line: "Embeds, anchor bolts, weld plates",    hot: true },
  { sub: "siteutil",   line: "Anything crossing under the pour" }
];

/* ── WHAT HAS TO BE SIGNED OFF ──────────────────────────────────────────────
 * Sign-offs the super needs IN HAND before he lets anything close. Named the way
 * a super names them and NOTHING MORE: this page never says which are required,
 * by whom, or in what order — that is the AHJ's call and the job's, and it
 * changes by jurisdiction. He ticks the ones his job has. */
window.GC_SIGNOFFS = [
  "Rough plumbing",
  "Rough electrical",
  "Rough mechanical",
  "Framing / structural",
  "Fire alarm rough",
  "Sprinkler rough / hydro",
  "Insulation",
  "Special inspection",
  "Owner / architect walk",
  "Our own QC walk"
];

/* ── THE WEATHER DAY ────────────────────────────────────────────────────────
 * Vocabulary for gc/weather-day.html. Lives here and not in the page, same
 * boundary the other five trades keep.
 *
 * Designed by a three-lens field panel (commercial super · small-shop GC owner ·
 * the PM who RECEIVES it) and then cut by a 20-year superintendent instructed to
 * kill a third. He killed more than a third — 25 controls — and every one of the
 * kills was the same species: A NUMBER THAT INVITES AN ARGUMENT. Trade-by-trade
 * headcount, crew-hours lost, hours lost, days claimed, weather-days-so-far,
 * show-up pay, dollar figures. In his words: "the minute I print a man-hour
 * number I have to defend it, and I made it up at the gate."
 *
 * So THIS PAGE DOES NO ARITHMETIC AT ALL, and it prints no money. What survived
 * is what the office cannot reconstruct from its own records: what he SAW, what
 * it STOPPED, what it COST BESIDES THE HOURS, and what it PUSHES.
 *
 * AND IT NEVER FETCHES WEATHER. No forecast, no station, no radar. The day this
 * page prints 0.3 in off an airport station while the gauge at the trailer read
 * 1.4, it has handed the owner's rep a document with the super's own name on it
 * that argues against him. The measurement is one typed line with the source
 * inside it. No thresholds either — the page has no opinion about what counts as
 * an unworkable day. His contract has one; a web page does not get to read it
 * to him. (§SAFETY — never ship authoritative data we do not have.)            */

/* Non-printing shot list. It is a NUDGE, not a manifest: the photos ride in the
 * same message as the paste, so listing which ones he attached, next to the ones
 * he attached, is noise. Three items, top of the page, because Tuesday's mud
 * cannot be re-photographed on Wednesday — Wednesday is sunny and the pad looks
 * fine, and the owner's rep will say so. */
window.GC_WEATHER_SHOTS = [
  "Wide shot with something you can name in it — the gate, the tower, the address",
  "The work that stopped, sitting empty — the hole, the forms, the deck",
  "Your gauge, or the phone screen, held up on site"
];

/* THE CALL — single-select. Picking the first flips the whole document forward
 * to a night-before call, which is the cheapest day on the job: the only weather
 * message that saves money BEFORE it is spent. Same 15 controls, sent forward,
 * no second page. */
window.GC_WEATHER_CALL = [
  { id: "tomorrow", line: "Calling it for tomorrow — don't load the trucks", ahead: true },
  { id: "never",    line: "Never started — called it before shift" },
  { id: "gate",     line: "Sent them home at the gate" },
  { id: "pulled",   line: "Started, then pulled the plug" },
  { id: "partial",  line: "Partial — outside down, inside kept going" },
  { id: "reopen",   line: "Held it, then back in it — reopened" }
];

/* Twelve, not twenty-four. The panel proposed three separate wind entries and
 * four separate cold ones; the super cut them because "wind — crane's down" is
 * not a condition, it is what stopped, and it already lives on the other list.
 * 'Ground already saturated' is the highest-value line here: it turns a quarter
 * inch of rain into a legitimate lost day, and no super types it on his own. */
window.GC_WEATHER_COND = [
  "Rain — steady all shift",
  "Rain — on and off, never got a window",
  "Downpour / thunderstorm",
  "Lightning in the area — everybody off the steel and out of the lifts",
  "Ground already saturated — still drying out from the last one",
  "Standing water — the deck, the pad, the hole",
  "Mud — can't get equipment in",
  "High wind",
  "Snow or ice",
  "Froze overnight / too cold to place",
  "Extreme heat",
  "Smoke / air quality"
];

/* ACTIVITIES, NOT TRADES. The scheduler works off activities — "deck pour" is a
 * bar on his chart, "concrete guys" is not. 'Inspection — didn't happen' stays
 * on the list because that reschedule is days lost BECAUSE of the rain rather
 * than to it, and it is the highest-value tick on the page. */
window.GC_WEATHER_STOPPED = [
  "Deck or slab pour",
  "Footings, forms and rebar",
  "Pump, crane or lift picks",
  "Excavation, trench or backfill",
  "Grading and compaction — the subgrade",
  "Steel, truss or panel set",
  "Exterior framing and sheathing",
  "Roofing / dry-in",
  "Waterproofing, sealants, exterior paint",
  "Site concrete, paving, striping, landscape",
  "Anything outside the building line or in a lift",
  "Inspection — didn't happen"
];

/* Everybody claims the labor and nobody claims these. Ten items and NOT ONE
 * DOLLAR FIELD — a price box turns a 6 a.m. guess into the number the owner
 * anchors on forever. */
window.GC_WEATHER_COST = [
  "Pump on site, no pour — show-up charge",
  "Concrete cancelled or short load",
  "Crane or operated rental rescheduled",
  "Rented equipment sat — standby",
  "Delivery turned around — restock or redelivery",
  "Testing lab / special inspector showed for nothing",
  "Dewatering — pumping the hole out",
  "Re-grade and re-compact the subgrade",
  "Re-protect or re-cover work already done",
  "Reinspection — back on his list"
];

/* ONE list, not two. Mitigation and phone calls are the same reflex, and the
 * PM's first question every single time is "does the concrete sub know? did you
 * call the pump?" — so the calls he already made belong beside what he did.
 * Deliberately absent: "working Saturday to get it back". That is a Saturday
 * committed in writing before anybody has talked about who pays for it, and you
 * never print an offer nobody asked you for. */
window.GC_WEATHER_DID = [
  "Called it before shift — nobody drove in",
  "Cancelled the pour the night before",
  "Told the subs working today",
  "Told the subs scheduled tomorrow",
  "Turned the pump around",
  "Released the crane and the operator",
  "Cancelled the concrete",
  "Called the testing lab / inspector off",
  "Moved everybody I could to interior work",
  "Squeegeed and pumped the deck",
  "Covered and protected what was open",
  "Ran dewatering / sump",
  "Reset the erosion control and the street",
  "Rescheduled the deliveries"
];

/* Three, and the third one is the point. "Don't know" IS the honest answer at
 * 6 a.m., and a super forced to fake a critical-path call just leaves the whole
 * field blank. Note what is NOT here: the panel proposed "not on the critical
 * path — we'll absorb it", and that got cut. Observing there is float is an
 * observation; "we'll absorb it" is the day given away in a heading token, and
 * it gets quoted back at him in March. */
window.GC_WEATHER_PATH = [
  "On the critical path",
  "Not on the critical path — it's got float",
  "Don't know — schedule guy needs to look"
];

/* ── WHERE ──────────────────────────────────────────────────────────────────
 * How a super says a location, most-used first. He types the specifics; these
 * are the shapes he types them into, so the picker never fights his job's own
 * naming. */
window.GC_AREA_HINTS = [
  "Level 3 — north corridor",
  "Rooms 214–222",
  "Grid C-4 to F-4",
  "Unit 12 stack",
  "West wing restrooms",
  "Kitchen / back of house",
  "Elevator lobby, all floors",
  "Pour 4 — south half"
];

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working GC hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · WHAT THE IN-TRADE REVIEWER KILLED, so it does not crawl back in: the QUOTE
   *    LINE. Quoting a man back to himself, in a message addressed to him, and
   *    asking him to reply OK to it is a deposition exhibit, not a tag — no super
   *    presses send on that with the CM standing three feet away, and the day he
   *    would is the day he should be calling his PM instead.
   *  · THE GC IS USUALLY THE ONE RECEIVING THESE, so this one points the other way:
   *    it is what the SUPER sends UP to the CM or the owner's rep, never down to a
   *    sub. Procore owns the PCO number and the daily log (§THE SYSTEM OF RECORD) —
   *    so the tag carries no number and says so out loud.
   *  · SUB CREW IS A CLASSIFICATION. Half of what a super gets directed into is
   *    somebody else's crew standing there on his say-so, and if the tag can't
   *    carry that line it does not carry the extra.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "CM",
    "Owner's rep",
    "Their PM",
    "Architect / EOR",
    "Inspector / AHJ",
    "Somebody else"
  ],
  "how": [
    {
      "v": "Verbal — this tag is the paper"
    },
    {
      "v": "Phone"
    },
    {
      "v": "You sent it — I'll forward it"
    }
  ],
  "why": [
    {
      "name": "Not on the contract drawings"
    },
    {
      "name": "RFI answer / ASI / bulletin after buyout"
    },
    {
      "name": "Plans vs. existing — field conflict"
    },
    {
      "name": "Unforeseen",
      "sub": "buried, hidden, as-builts wrong"
    },
    {
      "name": "Owner add — asked for it on the spot"
    },
    {
      "name": "AHJ / inspector made us"
    },
    {
      "name": "Working around another prime / owner's vendor"
    },
    {
      "name": "You said OT / extra crew to hold the date"
    }
  ],
  "classes": [
    "— class",
    "SUPER",
    "FOREMAN",
    "CARP",
    "LAB",
    "OPER",
    "APPR",
    "SUB — ELEC",
    "SUB — MECH",
    "SUB — PLUMB",
    "SUB — FIRE SPRINK",
    "SUB — CONC",
    "SUB — STEEL",
    "SUB — DRYWALL",
    "SUB — SITE"
  ],
  "stands": [
    {
      "v": "Done today"
    },
    {
      "v": "Still going — new tag tomorrow"
    }
  ]
};

/* ── THE SAME VOCABULARY, EN ESPAÑOL (wish 2026-08-17: "Todo en Español para los
 * Latinos", tm-tag.html) ───────────────────────────────────────────────────────
 * US-jobsite Spanish, not textbook: vale, cuadrilla, mayordomo (the foreman —
 * NEVER the superintendent, who stays "el súper"), tablaroca, rociadores. Usted
 * register throughout — this document goes UP the chain.
 *
 * SHAPE: every entry carries its own `en` twin, so the page can translate a
 * saved pick when the language flips WITHOUT pairing two lists by index — an
 * index pairing is drift with a delay on it. `en` must equal the string in
 * TOOLKIT_ITEMS.tag above, verbatim; a mismatch fails soft (the pick survives
 * untranslated, the document still prints).
 *
 * THE DOCUMENT STAYS READABLE AT THE TOP OF THE CHAIN (the panel's one binding
 * change, all three lenses): in Spanish mode the page prints picked options as
 * "ES (EN)" — composed FROM these pairs — because a T&M tag outlives the text
 * thread: pay apps, CO backup, the AP clerk in March. The crew classes carry
 * the pairing inside the token itself, so the select and the document agree.  */
window.TOOLKIT_ITEMS.tag_es = {
  "roles": [
    { "es": "CM", "en": "CM" },
    { "es": "Rep del dueño", "en": "Owner's rep" },
    { "es": "El PM de ellos", "en": "Their PM" },
    { "es": "Arquitecto / EOR", "en": "Architect / EOR" },
    { "es": "Inspector / AHJ", "en": "Inspector / AHJ" },
    { "es": "Otra persona", "en": "Somebody else" }
  ],
  "how": [
    { "es": "De palabra — este vale es el papel", "en": "Verbal — this tag is the paper" },
    { "es": "Por teléfono", "en": "Phone" },
    { "es": "Usted lo mandó — se lo reenvío", "en": "You sent it — I'll forward it" }
  ],
  "why": [
    { "es": "No está en los planos del contrato", "en": "Not on the contract drawings" },
    { "es": "Respuesta de RFI / ASI / boletín después del buyout", "en": "RFI answer / ASI / bulletin after buyout" },
    { "es": "Planos vs. existente — conflicto en campo", "en": "Plans vs. existing — field conflict" },
    { "es": "Imprevisto", "sub": "enterrado, escondido, as-builts mal", "en": "Unforeseen" },
    { "es": "Extra del dueño — lo pidió ahí mismo", "en": "Owner add — asked for it on the spot" },
    { "es": "El inspector / AHJ nos obligó", "en": "AHJ / inspector made us" },
    { "es": "Trabajando alrededor de otro prime / proveedor del dueño", "en": "Working around another prime / owner's vendor" },
    { "es": "Usted dijo OT / más cuadrilla para sostener la fecha", "en": "You said OT / extra crew to hold the date" }
  ],
  "classes": [
    { "es": "— clase", "en": "— class" },
    { "es": "SUPER", "en": "SUPER" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" },
    { "es": "CARP", "en": "CARP" },
    { "es": "LAB", "en": "LAB" },
    { "es": "OPER", "en": "OPER" },
    { "es": "APRENDIZ (APPR)", "en": "APPR" },
    { "es": "SUB — ELEC", "en": "SUB — ELEC" },
    { "es": "SUB — MECÁNICO (MECH)", "en": "SUB — MECH" },
    { "es": "SUB — PLOMERÍA (PLUMB)", "en": "SUB — PLUMB" },
    { "es": "SUB — ROCIADORES (FIRE SPRINK)", "en": "SUB — FIRE SPRINK" },
    { "es": "SUB — CONCRETO (CONC)", "en": "SUB — CONC" },
    { "es": "SUB — ACERO (STEEL)", "en": "SUB — STEEL" },
    { "es": "SUB — TABLAROCA (DRYWALL)", "en": "SUB — DRYWALL" },
    { "es": "SUB — SITIO (SITE)", "en": "SUB — SITE" }
  ],
  "stands": [
    { "es": "Terminado hoy", "en": "Done today" },
    { "es": "Sigue — mañana otro vale", "en": "Still going — new tag tomorrow" }
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
  toolName: "The Close-In List",
  eyebrow: "GC · you → your subs",
  lede: "Before I cover it, pour it, or close the lid — here's what's got to be IN, tested, and signed off, who owes me each one, and the gate it has to beat. Miss the gate and somebody's coring concrete.",
  docSubject: "Close-in list — what has to be in before we cover",
  docSubjectWith: "Close-in list — what we need from {to}",
  closing: "That's the list for this area. Text me back what's in, what's coming, and the day. Anything I don't hear on by the gate, I'm covering — call me before then, not after.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> walked and typed. This page inspects nothing, tests nothing and signs nothing off — it doesn't know what the code, the engineer, the inspector or your contract requires. It's the call you're making to your subs, not a record of inspection, and <b>nothing on it approves anybody's work or authorizes extra work.</b>",
  offHint: "Name the area and the sheet you walked it off, and nobody argues later about which wall you meant.",
  phJob: "Building C",
  phOff: "A-201 rev 4",
  phFrom: "Ken — site super",
  phArea: "Level 2 east — then it's a button",
  areaLabel: "Area / grid",

  who: [
    { v: "ec", label: "Electrical" },
    { v: "pc", label: "Plumbing" },
    { v: "mech", label: "Mechanical" },
    { v: "sprink", label: "Fire Sprinkler" },
    { v: "lv", label: "Low Voltage/FA" },
    { v: "framer", label: "Framer" },
    { v: "conc", label: "Concrete/Rebar" },
    { v: "roofer", label: "Roofer" },
    { v: "vendor", label: "Owner vendor / rep" }
  ],

  // EARLIEST FIRST — this is the order a job actually closes up in, and it is
  // why grouping by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "backfill", label: "Before backfill" },
    { v: "pour", label: "Before the pour" },
    { v: "dryin", label: "Before dry-in" },
    { v: "insul", label: "Before we insulate" },
    { v: "rock", label: "Before we rock" },
    { v: "lid", label: "Before ceiling closes" },
    { v: "floors", label: "Before floors go down" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "vendorrough", label: "Vendor rough points", who: "vendor", by: "pour", specs: [
      "Walk it with me and mark your stub-ups",
      "Field-verify before we pour, not off the cut sheet",
      "Your rough points on the deck in paint",
      "If your rep hasn't walked it, it's not going in"
    ] },
    { v: "roughin", label: "Rough-in done", who: "ec", by: "rock", specs: [
      "Every box in this wall, both sides",
      "Home runs pulled and landed",
      "Pipe hung, strapped, and capped",
      "Duct in and hung off the structure",
      "Whips and disconnects at the equipment",
      "Nothing left to add after I rock"
    ] },
    { v: "backing", label: "Backing in the wall", who: "framer", by: "rock", specs: [
      "Grab bars and toilet accessories",
      "TVs, monitors, and mounts",
      "Upper cabinets and countertops",
      "Handrail and guardrail backing",
      "Wall-hung fixtures and carriers",
      "Mark it on the stud so I can see it",
      "Backing plan's marked, follow it"
    ] },
    { v: "photos", label: "Photos before I cover", who: "ec", by: "rock", specs: [
      "Every wall, before the rock goes on",
      "Tape in the shot off a column line",
      "Room number written on the wall",
      "Send them to me, don't just take them"
    ] },
    { v: "signoff", label: "Rough signed off", who: "ec", by: "insul", specs: [
      "Your inspection, your call, you schedule it",
      "Send me a photo of the signed card",
      "Punch your own rough before he shows",
      "No sign-off, no rock, that's the rule"
    ] },
    { v: "test", label: "Test it and hold it", who: "pc", by: "rock", specs: [
      "On the gauge and holding till I cover",
      "Water test the drains, top to bottom",
      "Air on it, gauge stays on the riser",
      "Hydro on and holding",
      "Picture of the gauge with the date",
      "Don't drop the test to move a ladder"
    ] },
    { v: "holes", label: "Seal what you cut", who: "ec", by: "rock", specs: [
      "Every hole you made, you pack",
      "Both sides of the wall, not just the front",
      "Sleeves packed before I close it up",
      "Head-of-wall where you cut the track",
      "Photo with the wall tag in the frame",
      "If I rock it, you're cutting it back open"
    ] },
    { v: "access", label: "Access doors called", who: "mech", by: "lid", specs: [
      "Tell me where before I close the lid",
      "Valves, dampers, and cleanouts",
      "Mark it on the wall in keel",
      "Tell me the size you need, I'll order it",
      "If you don't call it, it's not there"
    ] },
    { v: "grid", label: "Above the grid is done", who: "mech", by: "lid", specs: [
      "Everything above the tile is complete",
      "Hangers off the structure, not my duct",
      "Insulation and vapor barrier wrapped",
      "Devices dropped per the ceiling plan",
      "Your trash off the tile and out",
      "Walk it with me before tile goes in"
    ] },
    { v: "drops", label: "Drops set to ceiling", who: "sprink", by: "lid", specs: [
      "Drops cut to the finish ceiling",
      "Heads centered in the tile",
      "Mains hung and braced off structure",
      "Escutcheons after paint, not before",
      "Hydro on and holding till I close"
    ] },
    { v: "lvrough", label: "Rings, boxes, string", who: "lv", by: "rock", specs: [
      "Ring and pull string at every device",
      "Backbox set for the head-end / IDF",
      "Conduit stubbed above the ceiling",
      "Sleeve through the wall where it crosses",
      "Match the field, not the old plan"
    ] },
    { v: "indeck", label: "In the deck", who: "pc", by: "pour", specs: [
      "Sleeves in, capped, and marked",
      "Conduit tied off, not to my rebar",
      "Stub-ups staked and painted",
      "Blockouts and box-outs framed",
      "Sleeve through the footing / grade beam",
      "Photos and dimensions before the mud truck"
    ] },
    { v: "embeds", label: "Embeds and bolts set", who: "conc", by: "pour", specs: [
      "Anchor bolts templated and tied",
      "Embed plates flush and level",
      "Hold-downs in where the drawing shows",
      "Weld plates for the stair and canopy",
      "Surveyed before you leave the deck"
    ] },
    { v: "ug", label: "Underground in", who: "pc", by: "backfill", specs: [
      "In, shot, and located before we cover",
      "Tie-in to the main is made",
      "Dimension off a hard point, not a stake",
      "Boots and wrap at the penetrations",
      "Protected before the dirt comes back",
      "Looked at before anybody backfills"
    ] },
    { v: "curbs", label: "Curbs and penetrations", who: "mech", by: "dryin", specs: [
      "Curbs set, squared, and shimmed",
      "All holes through the deck, done",
      "Coordinated with the roofer's flashing",
      "Pipe supports set on the roof, not later",
      "No new holes after we dry in"
    ] },
    { v: "floorbox", label: "Floor boxes flush", who: "ec", by: "floors", specs: [
      "Set to the finish floor, not the deck",
      "I'll give you the floor build-up — set to it, not to the deck",
      "Covered and taped before the pour-back",
      "Poke-thru cores drilled and sealed",
      "Flat enough for the flooring guy"
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
  toolName: "What I’ll Get You",
  eyebrow: "GC · your subs → you → back",
  lede: "Your subs send you lists all day — access, cores, backing, power, dates. Line one up, say what you’ll get them and when, and answer the whole thing in one message.",
  docSubject: "what I’ll get you off your list",
  closing: "That’s what I’ll get you and when. Anything under CAN’T or NEED TO KNOW, bring it to the morning huddle and we’ll sort it there instead of trading texts all week.",
  phJob: "Building C", phTo: "Sal — Local 38", phFrom: "Ken — site super", phOff: "P-201 rev 2",
  paste: "Building C — holes and backing — Aug 9\n\nJob: Building C\nFrom: Sal — Local 38\n\nLevel 2 · core through the deck at gridline D before we set carriers\nRestroom 210 · backing in the wet wall before rock\nSite · after-hours access Saturday for the tie-in"
};


/* GETTING IN — every other trade fills this out for its OWN guys; the GC
 * fills it out for a SUB's. `co` below is HIS outfit vouching for the ask,
 * not the crew's — sender and the people walking through the door are two
 * different companies, so whose crew it is has to ride in `scope`, never in
 * his own hands (see phScope). He's also the party every other trade's copy
 * of this page gets forwarded TO, so the wording has to hold up when he's
 * relaying somebody else's ask upward without retyping it.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "GC · you → the owner / building",
  lede: "Your sub needs into space the owner locks. Send the ask that gets a yes on the first try — the night, the rooms, whose crew it is, and the heads-up that stops them getting walked out at nine.",
  docName: "ACCESS REQUEST",

  /* HOW OFTEN — unchanged from AV. Same overflow reason: four in a segment on
     a 320px phone is the mobile gate’s own kill. */
  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "Nights all week" },
    { v: "Ongoing — I’ll flag changes" }
  ],

  /* WHAT I AM ASKING HIM TO DO. AV’s 11 universal asks, unchanged, plus the
     one swap this trade needs: a GC rarely needs a single ancillary closet
     opened (AV’s rack room / IDF) — he needs the whole assigned space, because
     the crew he’s bringing works across it, not in one room. And one addition
     AV never needed: a body from the owner’s side to walk it before the crew
     starts, because the GC is the one who answers for what shape the space
     was in before his sub touched it. */
  need: [
    { name: "Doors unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The freight elevator" },
    { name: "The dock" },
    { name: "Somewhere to put the van" },
    { name: "The room cleared", sub: "off the calendar, desks empty" },
    { name: "The floor / suite / tenant space", sub: "not just the one room — the crew’s working across it" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "Somebody from your side to walk it with us first", sub: "before the crew starts" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" }
  ],

  /* BEFORE YOU SAY YES. Six of AV’s 11 are universal and stay word for word.
     Four are swapped for a GC’s real ones — several subs on site at once and
     the real headcount, the owner’s own staff and furniture still in the
     space, noise that runs the whole floor for days rather than a two-hour
     burst, and one sub touching a life-safety system without the GC knowing
     in advance which one it’ll be. That last one still hands the permit back
     exactly the way AV’s fire-alarm and sprinkler lines did — never a state,
     always a question aimed at the man who owns the process. */
  heads: [
    { name: "It’ll be loud — for days, not hours", sub: "demo or framing running the whole floor — tell me if there’s a day it can’t happen" },
    { name: "Dust", sub: "coring and cutting — tell me what barrier you want up" },
    { name: "Ceiling tiles out", sub: "I’ll tell you which corridor and for how long" },
    { name: "Their staff — and their stuff — still in there", sub: "people working beside us, their furniture and equipment in the way — tell me what to protect" },
    { name: "The corridor gets tight", sub: "gear staged while we’re in" },
    { name: "Several of our subs in there at once", sub: "the real headcount’s higher than it looks — I’ll give you the number, not just one crew’s" },
    { name: "One of our subs has to touch the fire alarm or a sprinkler head", sub: "tell us who puts it on test and how you want it run" },
    { name: "Something has to come off power", sub: "your engineer throws it, not us — tell me the window" },
    { name: "Hot work — torch or solder", sub: "that’s your permit — tell me how you want it done" },
    { name: "Patient or clinical space next door", sub: "tell me what you need from us before we start" }
  ],

  phSite: "Northgate Business Park",
  phRoom: "Suite 214",
  phHow: "2nd flr — through the north stair, not the lobby",
  phScope: "our electrical sub pulling new circuits into the suite",
  phLoud: "core drill for about 2 hours, wrapped by 9",
  phTo: "Priya — owner’s rep",
  phMe: "Ken R — 415-555-0119",
  phCo: "Highline Construction",

  closing: [
    "This is an ask, not a booking — nobody rolls until you reply. Wrong night? Tell me which one works and we’ll take it.",
    "Saying yes: tell me the window you’re actually giving us and who’s meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It’s a request, not a permit and not a booking.</b> Anything on the heads-up list that needs a permit, a panel on test or a fire watch is theirs to issue and theirs to number — this page just tells them it’s coming and asks how they want it run. And check your contract before you send it: plenty of them say you don’t talk to the building direct. If yours does, send this to your GC and let him forward it — same words, right chain."
};
