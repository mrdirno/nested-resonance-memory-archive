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
