/* ROOFING FIELD TOOLKIT — VOCABULARY DATA.
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Classifications,
 * reason lists, gate ladders and pick options live HERE — never in the identity
 * config and never inline in a tool page.
 *
 * TWO HARD INVARIANTS (§SAFETY), and roofing puts the sharpest edge in the whole
 * program on the second one:
 *
 *   ZERO BRAND NAMES. This trade says one membrane manufacturer's name instead of
 *   the word "membrane" and one underlayment brand instead of "synthetic". That
 *   is exactly why the word is checked and never printed. It is MEMBRANE and it
 *   is CAP; it is ISO, never a trade name; it is I&W, never the brand everybody
 *   says.
 *
 *   NOTHING IS RATED, SIZED, SLOPED, SPACED OR GRADED. No uplift rating, no
 *   listed assembly, no fastener length, no fastener or plate density, no
 *   perimeter or corner enhancement, no slope minimum, no R-value, no crown or
 *   sump dimension, no exposure, no nailing pattern, no warranty term — not as a
 *   value, not as a default, not as a greyed placeholder next to a chip. A
 *   PLACEHOLDER IS A RECOMMENDATION. Roofing is a warranty-and-litigation trade:
 *   an assembly number that looks authoritative on a phone is not a helpful
 *   default here, it is somebody's exhibit. Every page that takes a number prints
 *   the same plain line: these are your numbers off your approved detail, we
 *   don't know them and we won't guess.
 *
 *   THE PANEL SAID IT PLAINEST (4-lens roster fan-out, 2026-08-12): every ask on
 *   the cross-boundary list "wants a number welded to it — curb height above
 *   finished roof, how far a penetration has to sit off a wall". It never gets
 *   one here. He states the ask; the approved detail states the number.
 *
 * BOTH HALVES, EVERYWHERE. Commercial low-slope says SECTION, ISO, COVER BOARD,
 * MEMBRANE, TERM BAR; residential steep-slope says SLOPE, DECK, SYNTHETIC, I&W,
 * CAP. Both are printed throughout on purpose — a page that speaks only one of
 * them tells half this trade family it was not written for them.
 */

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Everything here is something the man PICKS,
 * never something the page decides. No rates, no totals, no arithmetic.
 *
 *  · WHAT IS **NOT** IN THIS TAG is the field this trade fights about hardest,
 *    and its lines are roofing-specific: the deck repair is not the roof over it,
 *    a temporary cut-off is not the permanent tie-in, and neither is the
 *    warranty inspection that has to happen after.
 *  · THE TAG IS WRITTEN ON THE OPEN DECK. That is the whole reason it exists —
 *    once the new roof is over the bad deck, the evidence is gone and the
 *    argument is unwinnable (all three field lenses said this independently).
 *  · SAY TAG or EXTRA, never FORM.
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC super",
    "GC PM",
    "Our GF or PM",
    "Owner's rep / property manager",
    "Building engineer",
    "Architect, engineer or roof consultant",
    "Manufacturer's field rep",
    "Homeowner",
    "Another trade's foreman"
  ],
  "how": [
    { "v": "Told me on the roof" },
    { "v": "Text / email" },
    { "v": "Phone call" },
    { "v": "Marked-up roof plan handed to me" },
    { "v": "Said it in the trailer meeting" }
  ],
  "why": [
    { "name": "Not in our scope" },
    { "name": "Found it after tear-off", "sub": "nobody could see it bid day" },
    { "name": "Deck came up bad underneath" },
    { "name": "Wet insulation — more than the allowance" },
    { "name": "Extra layer nobody disclosed" },
    { "name": "Existing conditions", "sub": "not what the as-builts or the roof plan show" },
    { "name": "Another trade's work is on my roof line" },
    { "name": "Damage by others we had to repair to keep going" },
    { "name": "Told to work out of sequence" },
    { "name": "Held off the roof, then told to make the day up" },
    { "name": "Emergency water cut-off — weather moved on us" }
  ],
  "notin": [
    { "name": "Deck repair only", "sub": "not the roof assembly going over it" },
    { "name": "Temporary cut-off only", "sub": "the permanent tie-in is separate" },
    { "name": "Not the tear-off already in contract" },
    { "name": "No re-inspection or warranty walk after this" },
    { "name": "No crane, hoist or loader time", "sub": "unless it's listed below" },
    { "name": "No stand-by hours for the crew that waited" },
    { "name": "No extra dumpster or disposal for what came off" },
    { "name": "Not a delay claim and not a schedule impact" },
    { "name": "No interior protection, ceiling or drywall work" }
  ],
  "classes": ["— class", "JOURNEYMAN", "APPRENTICE", "FOREMAN"],
  "pics": [
    { "v": "In this message — shot on the open deck" },
    { "v": "None" }
  ]
};


/* ── THE CROSS-BOUNDARY ASK (shape #3 — shared/rowlog.js) ──────────────────
 * The vocabulary for rough-in-request.html — "Before I Open It".
 *
 * THIS TRADE ASKS AT TWO DIFFERENT DOORS AND BOTH ARE REAL. Before he can OPEN a
 * section he needs everybody's gear off it and somebody to own the weather call;
 * before he can COVER it he needs every curb, sleeve, post, drain and conduit
 * set, because after the membrane goes down every one of those is a cut in a
 * finished roof. Three of the four in-trade lenses proposed exactly this page
 * unprompted, and two of them named it "Before I Cover It".
 *
 * THE GATES ARE A REAL COUNTDOWN, not generic milestones — and the ladder below
 * merges both halves of the family in the order the panels gave them, low-slope
 * and steep-slope, earliest first. `who` and `by` are the USUAL aim and the
 * USUAL gate — they only ever fill a field left empty and never overwrite a pick
 * (§SCARS — a default is a claim).
 *
 * The bars hold exactly as they do on the other seven: no size, no height, no
 * rating, no slope, no spacing, no code reference and no money. Every spec is a
 * PHRASING he picks.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before I Open It",
  eyebrow: "Roofing · you → the trades on your roof",
  lede: "Everything that has to be off, set, moved or owned before you open a section — and before you cover one. Who owes it, where it is, and the gate it has to beat.",
  docSubject: "Before we open it — what I need out of your trade",
  docSubjectWith: "Before we open it — what I need from {to}",
  closing: "That's what I need before we're on that section. Text me back what you'll hit and what you won't — while it's still covered. Once it's open, the weather owns the schedule and everything after that is a tag for somebody.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> roof plan. This page sizes nothing, sets no height, slopes nothing, rates no assembly and doesn't know what the code, the manufacturer's detail, the architect or the engineer requires &mdash; verify all of that against your own approved set. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The roof plan and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building B",
  phOff: "A-201 rev 2",
  phFrom: "Ray — Summit Roofing",
  phArea: "Section 2, north half — then it's a button",
  areaLabel: "Section / slope / grid line",

  who: [
    { v: "gc-super", label: "GC super" },
    { v: "mech", label: "Mech / HVAC" },
    { v: "ec", label: "EC foreman" },
    { v: "plumber", label: "Plumber" },
    { v: "sheetmetal", label: "Sheet metal" },
    { v: "owner", label: "Owner's rep / engineer" },
    { v: "solar", label: "Solar" },
    { v: "gutter", label: "Gutter / siding" },
    { v: "mason", label: "Mason / chimney" },
    { v: "framer", label: "Framer / carpenter" },
    { v: "other", label: "Somebody else" }
  ],

  // EARLIEST FIRST, merged from all four lenses' gate ladders. Low-slope and
  // steep-slope words both appear on purpose — see the header.
  milestones: [
    { v: "mobilize", label: "Before we mobilize" },
    { v: "hoist", label: "Before hoist or crane day" },
    { v: "tearoff", label: "Before we tear off this section" },
    { v: "deck", label: "Before the deck's signed off" },
    { v: "nailers", label: "Before nailers and blocking go in" },
    { v: "curbs", label: "Before curbs and sleepers are set" },
    { v: "insulation", label: "Before insulation goes down" },
    { v: "membrane", label: "Before the membrane or field goes on" },
    { v: "flash", label: "Before we flash it" },
    { v: "tonight", label: "Before we seal it up tonight" },
    { v: "dryin", label: "Before dry-in" },
    { v: "edge", label: "Before edge metal and coping" },
    { v: "inspect", label: "Before the inspection walk" },
    { v: "turnover", label: "Before we turn the roof over" }
  ],

  // Ordered by how often it comes up on a real roof, not alphabetically.
  asks: [
    { v: "get-off", label: "Get off my roof section", who: "gc-super", by: "tearoff", specs: [
      "Everything your trade has stored on this section moved before we open it",
      "Tell me the day you're clear and I'll put it on the tear-off list",
      "Nobody back on this section until I call it — it's open deck",
      "Your material and carts staged somewhere that isn't my lay-down",
      "Who's the one phone number if it starts raining while it's open"
    ] },
    { v: "penetrations", label: "Set it before I cover it", who: "mech", by: "insulation", specs: [
      "Every curb, sleeve, post and stanchion set at final height before we insulate",
      "Nothing coming through this deck after the membrane goes down",
      "Gas line, conduit and refrigerant off the deck and up on supports",
      "Tell me what's still coming so I can leave it open instead of cutting it in",
      "Anything abandoned — pull it and I'll close the hole while I'm there",
      "Walk it with me before I insulate, not after"
    ] },
    { v: "deck-ready", label: "Deck ready to roof", who: "gc-super", by: "deck", specs: [
      "Deck complete, fastened off and swept before we start",
      "Every opening framed and the framing signed off",
      "Bad deck flagged and repaired, or tell me it's on my tag",
      "Blocking, nailers and edge wood in before I can terminate",
      "Tell me who's calling the deck inspection and when"
    ] },
    { v: "access", label: "Access, lay-down and the dumpster", who: "gc-super", by: "mobilize", specs: [
      "Where the load lands and where the dumpster sits",
      "Roof access — hatch, ladder or stair, and who has the key",
      "The crane or loader window, and who's flagging it",
      "Protection under the work — what's inside and who covers it",
      "Hours we're allowed to make noise, torch or run odor"
    ] },
    { v: "weather-call", label: "Who owns the weather call", who: "gc-super", by: "tearoff", specs: [
      "How much we open in a day and who signs off on it",
      "Who makes the call to stop and who I ring when it turns",
      "Where the temporary protection lives and who pays to set it",
      "If it comes in overnight, who's inside at 6am and who calls me"
    ] },
    { v: "off-the-finished", label: "Off my finished roof", who: "gc-super", by: "turnover", specs: [
      "Nobody on the finished membrane without a call to me first",
      "Walk pads or protection under anybody working up there",
      "No welding, cutting or grinding over my roof — or I need it protected",
      "Grease, solvent and hood discharge kept off the membrane",
      "Anything dropped or dragged on it is a repair, not a punch item"
    ] },
    { v: "existing", label: "What's up there now", who: "owner", by: "mobilize", specs: [
      "Tell me what's live on this roof and what's abandoned",
      "Anything on it that has to stay running while we're working",
      "Who owns the array, the dish and the sign, and who takes them off",
      "Any warranty on the existing roof I'd be voiding",
      "Where the as-builts or the last roof plan are, if there are any"
    ] },
    { v: "drains", label: "Drains, scuppers and the water", who: "plumber", by: "insulation", specs: [
      "Drains and overflows clear and free before we start",
      "Who's setting the new drain bodies and when",
      "Where the water is supposed to go while we're open",
      "Anything plumbed through this roof that isn't on my plan"
    ] },
    { v: "steep-clear", label: "Off the slope before we tear", who: "solar", by: "tearoff", specs: [
      "Array off before we tear, and who owns the penetrations when it goes back",
      "Gutters pulled before we set the metal",
      "Mast, dish and cable dropped, and who reattaches",
      "Anything on the wall that has to come off for the kick-out",
      "Chimney work done before we flash it, not after"
    ] }
  ]
};


/* ── THE RETURN LEG (shape #3 — shared/rowlog.js) ─────────────────────────
 * The vocabulary for answer-back.html. Every served trade is on BOTH ends of the
 * boundary and roofing is no exception — the roofer receives the mechanical
 * contractor's curb list, the GC's close-in list and the owner's punch, and today
 * he answers all three with a phone call nobody wrote down.
 *
 * The `paste` sample is a REAL-SHAPED list, deliberately messy in the way the
 * ones he gets are: a header, blank lines, and rows that are locations first.
 */
window.TOOLKIT_ANSWER = {
  toolName: "What I'll Hit",
  eyebrow: "Roofing · them → you → back",
  lede: "Somebody sent you a list — curbs, close-in, punch, a marked-up roof plan typed out. Line it up, give each one a yes, a no, or a question, and a date on every yes, then send it back in one message.",
  docSubject: "what I'll hit",
  closing: "That's the yes, the no, and the when. Anything I flagged I need a location or a detail on before we cover that section — once the membrane's down, every one of these is a cut in a finished roof.",
  phJob: "Building B", phTo: "Dan — mech foreman", phFrom: "Ray — Summit Roofing", phOff: "A-201 rev 2",
  paste: "Building B — curbs and roof items — Aug 12\n\nJob: Building B\nFrom: Dan — mech foreman\n\nSection 2 · 4 curbs set, need them flashed before we set units\nSection 2 · gas line off the deck at the north wall\nSection 3 · 2 new sleeves coming through, not on the plan yet\nSection 1 · our guys need back on the finished roof Thursday"
};


/* ── THE NIGHT SEAL (whats-open.html) ─────────────────────────────────────
 * The vocabulary for this trade's SIGNATURE tool, and the one page on the whole
 * program no other trade could write.
 *
 * WHY IT IS THE PIN. Every other trade in this program races a gate somebody
 * else owns. The roofer OWNS one, and he re-owns it every single evening: the
 * building is either watertight tonight or it is not, and if it is not, somebody
 * has to know exactly which part and exactly what is under it. THREE OF THE FOUR
 * in-trade lenses proposed this page independently, under three different names
 * — "What's Open Tonight" (commercial low-slope), "Dry Tonight" (service), and
 * "What's Still Open" (residential steep) — which is the strongest convergence
 * in the entire roster fan-out.
 *
 * THE HONEST COMPETITOR IS THE CAMERA ROLL, NOT THE NOTES APP, and the steep
 * lens said so out loud: "four photos in a text takes eleven seconds." So this
 * page only earns its place by being FASTER than four photos and by carrying the
 * thing photos cannot — the state word, the count, and what is UNDER the part
 * that is still open. It stays a tap ladder for exactly that reason: pick a
 * section, tap how far it got, tap what's protecting it. No typing required to
 * produce a sendable message.
 *
 * NOTHING HERE IS A RATING OR AN ASSURANCE. "Dried in" is what HE says he did,
 * not a certification that the building is dry, and the document says so in its
 * own closing line. The page never grades the seal and never promises a roof
 * will hold — it records what was done and what is exposed.
 */
window.TOOLKIT_NIGHTSEAL = {
  toolName: "What's Open Tonight",
  eyebrow: "Roofing · end of day → the super, the owner, your own PM",
  lede: "Section by section at quitting time: how far it got, what's holding the water tonight, and what's underneath the part that's still open. One message, before you're off the ladder.",
  docSubject: "roof status tonight",
  closing: "That's the roof at quitting time. Anything listed OPEN or TEMPORARY is not finished work — if it comes in overnight, call me before anybody starts pulling ceiling.",
  phJob: "Building B",
  phFrom: "Ray — Summit Roofing",
  phArea: "Section 2, north half",
  areaLabel: "Section / slope / elevation",

  // HOW FAR IT GOT. The tap ladder, in build order — low-slope and steep-slope
  // words together, because one crew is often doing both on the same address.
  states: [
    { v: "not-started", label: "Not opened — still the old roof" },
    { v: "torn", label: "Torn off — bare deck" },
    { v: "deck-repair", label: "Deck open — repairs going in" },
    { v: "vapor", label: "Vapor retarder down" },
    { v: "iso", label: "Insulation / cover board down" },
    { v: "underlay", label: "Underlayment / I&W down" },
    { v: "loose", label: "Membrane loose-laid, not secured" },
    { v: "secured", label: "Membrane secured, seams not run" },
    { v: "welded", label: "Seams welded / field on" },
    { v: "flashed", label: "Flashed — curbs and penetrations in" },
    { v: "dried-in", label: "Dried in" },
    { v: "complete", label: "Complete — edge metal on" }
  ],

  // WHAT IS HOLDING THE WATER TONIGHT. This is the field the whole page exists
  // for and the one nobody writes down.
  seal: [
    { v: "none", label: "Nothing — it's open" },
    { v: "night-seal", label: "Night seal run at the edge" },
    { v: "cutoff", label: "Temporary water cut-off" },
    { v: "tarp", label: "Tarped and weighted" },
    { v: "papered", label: "Papered / dried in, no metal" },
    { v: "plated", label: "Plated and sealed over the opening" },
    { v: "tied", label: "Tied into the existing roof" },
    { v: "permanent", label: "Permanent — nothing temporary left" }
  ],

  // WHAT IS UNDERNEATH THE OPEN PART. The reason the message goes to the owner
  // and the building engineer and not only to our own PM.
  under: [
    { v: "unoccupied", label: "Nothing under it / unoccupied" },
    { v: "occupied", label: "Occupied space" },
    { v: "ceiling", label: "Finished ceiling" },
    { v: "electrical", label: "Electrical or gear room" },
    { v: "it", label: "IT / server room" },
    { v: "kitchen", label: "Kitchen or food service" },
    { v: "stock", label: "Stock, product or storage" },
    { v: "attic", label: "Attic / open framing" },
    { v: "living", label: "Living space" },
    { v: "unknown", label: "Don't know what's under it" }
  ],

  // WHAT HE CARRIES TO TOMORROW. Optional, tapped, never typed.
  next: [
    { v: "finish-seal", label: "Finish sealing this section first thing" },
    { v: "pull-tarp", label: "Pull the tarp and keep going" },
    { v: "weather-hold", label: "Weather hold — not opening more" },
    { v: "waiting-trade", label: "Waiting on another trade" },
    { v: "waiting-material", label: "Waiting on material" },
    { v: "inspection", label: "Inspection before we cover it" },
    { v: "nothing", label: "Nothing — carry on" }
  ]
};
