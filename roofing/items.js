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


/* ── GETTING IN (shape #2 — shared/note.js) ─────────────────────────────────
 * GETTING IN, ported to roofing — same shape and same handback rule as AV's;
 * see that header for the design rationale. What's different is where this
 * trade's fence actually sits: almost everything it needs is OUTSIDE and
 * ABOVE, so the ask leans on the hatch, the ladder or stair to it, the lot
 * for the truck, and the hoist or crane window — not a locked door. It's
 * also the trade whose work most literally rains on somebody through a
 * ceiling, and whose smoke and fumes go straight into the building's own
 * intakes, so the heads-up list trades AV's ceiling tiles and furniture for
 * falling debris, closed-off ground, intake smoke, de-powered rooftop
 * units, open weather, and the hatch itself staying open.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Roofing · you → whoever holds the keys",
  lede: "You need onto a roof somebody else has to open up. Send the ask that gets a yes on the first try — the night, the section, who’s coming, and the heads-up that keeps a crew from getting turned away at the gate.",
  docName: "ACCESS REQUEST",

  // HOW OFTEN — unchanged from AV; chips rather than a segment for the same
  // mobile-overflow reason.
  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "Nights all week" },
    { v: "Ongoing — I’ll flag changes" }
  ],

  // WHAT I AM ASKING HIM TO DO. Kept AV’s universal asks; swapped the rack
  // room / IDF line for this trade’s real second door — the roof itself —
  // and added one genuinely roofing ask: where the dumpster or chute sits.
  need: [
    { name: "Doors unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The freight elevator" },
    { name: "The dock" },
    { name: "Somewhere to put the van" },
    { name: "Somewhere to set the dumpster or the chute", sub: "close enough we’re not carrying tear-off across the lot" },
    { name: "The room cleared", sub: "off the calendar, desks empty" },
    { name: "The roof hatch or penthouse door unlocked too", sub: "not just the ladder or stair up to it" },
    { name: "Nobody there — we’ll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "we’ll be moving through zones" },
    { name: "Tell me who gets our COI", sub: "if it isn’t already on file" }
  ],

  // BEFORE YOU SAY YES. Kept the universal ones that still apply — loud,
  // dust, a tight route, an alarm — and dropped ceiling tiles and furniture,
  // which don’t happen on a roof. Everything else is this trade’s own: what
  // falls, what has to be roped off underneath, where the smoke goes, what
  // goes off power, what the weather can do to an open roof, and the hatch
  // itself. The last three hand a real permit back, same rule as AV’s.
  heads: [
    { name: "It’ll be loud", sub: "tear-off, hoist and compressors — say the word and we’ll shift the noisy part" },
    { name: "Dust and grit off the tear-off", sub: "tell me if anything downwind needs covering" },
    { name: "The stairwell or hatch route gets tight", sub: "material staged there while we’re moving it up" },
    { name: "We’ll trip the roof door or motion alarm", sub: "coming and going through the hatch after hours" },
    { name: "Things come off the edge — tools, old material, debris", sub: "tell me who’s keeping people clear of the drop zone" },
    { name: "The ground under us has to be closed off", sub: "tell me how you want that stretch roped or barricaded" },
    { name: "Smoke and fumes will pull into your roof intakes", sub: "tell me if you want those units shut down or covered while we run" },
    { name: "Rooftop units go off power while we’re working around them", sub: "your tech throws the disconnect, not us — tell me the window" },
    { name: "The roof’s open tonight and it might rain", sub: "tell me if you want us to seal early or hold off starting" },
    { name: "Hot work — torch or kettle", sub: "that’s your permit — tell me how you want it run" },
    { name: "Roof access — the hatch stays open while we’re up", sub: "tell me if you want it manned or chained open" }
  ],

  phSite: "Building B",
  phRoom: "Section C",
  phHow: "roof hatch off the top-floor corridor",
  phScope: "tearing off Section C and setting new membrane",
  phLoud: "tear-off and hoist, quiet by 11",
  phTo: "Carl — building engineer",
  phMe: "Ray — 415-555-0198",
  phCo: "Summit Roofing",

  closing: [
    "This is an ask, not a booking — nobody rolls until you reply. Wrong night? Tell me which one works and we’ll take it.",
    "Saying yes: tell me the window you’re actually giving us and who’s meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It’s a request, not a permit and not a booking.</b> Anything on the heads-up list that needs a permit, a panel on test or a fire watch is theirs to issue and theirs to number — this page just tells them it’s coming and asks how they want it run. And check your contract before you send it: plenty of them say you don’t talk to the building direct. If yours does, send this to your GC and let him forward it — same words, right chain."
};

/* ── THE MATERIAL ORDER (shape #1 — shared/checklist-request.js) ───────────
 * The vocabulary for order-the-load.html. The TENTH instance of the checklist →
 * request shape and ROOFING'S FIRST — every other material trade in the program
 * calls its yard off a list; the roofer was still calling it off memory. Nothing
 * here is decided by the page: he picks the line, he says the count, he says the
 * colour off his own submittal. The two hard invariants at the top of this file
 * bind every line below — no square footage figured, no fastener length or
 * pattern or density, no R-value, no slope, no exposure, no uplift, no warranty
 * term, and no brand as a word we print. Where a spec decides it, the line says
 * so and holds an empty box.
 *
 * WHAT THIS ONE DOES THAT THE OTHER NINE DO NOT:
 *
 *  · THE UNIT LEAVES THE YARD WELDED TO THE NUMBER. Field goes by the SQUARE,
 *    shingle by the BUNDLE, membrane and underlayment by the ROLL, edge metal by
 *    the STICK, boots and vents EACH, nails and plates by the BOX, adhesive by the
 *    PAIL, sealant by the TUBE, board by the BOARD. "3 shingle" and "3 square of
 *    shingle" are two different trucks. Qty is free text because a roofer says
 *    "three square" and "half a bundle"; a bare number gets his own word attached
 *    and anything he wrote in words is left exactly as he wrote it.
 *
 *  · THE COLOUR / PROFILE / LOT IS THE ONE A SECOND ORDER CANNOT GUESS. Field,
 *    cap and the metal that shows all come in a colour, and the colour moves lot
 *    to lot. A re-supply that pulls a different lot puts a stripe on a finished
 *    roof that no wash takes off — the roofing twin of the mason's run. It is a
 *    FLAG on the lines it applies to and a passthrough field in the header, never
 *    a lookup: we do not hold anybody's colour lots.
 *
 *  · WHERE IT LANDS IS ROOF OR GROUND, not which side of a building. A square set
 *    on the wrong slope is a square carried up a ladder by hand. The axis is
 *    roof-loaded (which slope) vs a ground drop — and "spread it, don't stack one
 *    spot" is the roofer's own word to the driver, never this page rating a deck.
 *
 *  · THE ABSENT LINE IS A DRY-IN, NOT A CORRECTION. Field with no underlayment,
 *    shingle with no starter or no cap, a roof with no edge metal, membrane with
 *    nothing to fasten or bond it — those are the lines a roofer forgets and finds
 *    out about at noon. They go on the GLASS as a question he answers by looking,
 *    never in the message: the yard is not told a man's roof is short a course.
 */
(function () {
  "use strict";
  /* §THE NEUTRAL — every axis leads with one, written as the QUESTION, and the
   * page drops any value starting with an em-dash. A pre-selected default would be
   * the tool choosing for him; a printed value nobody picked would be the tool
   * putting words in his order. */
  function n(q) { return "— " + q + " —"; }
  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }
  /* WHERE IT LANDS. Roof or ground — and if it's the roof, which slope, because a
   * square on the wrong elevation is carried by hand. "Spread it, don't stack one
   * spot" is HIS instruction to the driver; this page rates no deck and sets no
   * load. Label key resolves to "whereitlands" — order-the-load.html reads it. */
  var DROPS = ["On the roof — front / street slope", "On the roof — back slope",
               "On the roof — the section we're on", "On the roof — at the ridge",
               "On the roof — spread it, don't stack one spot",
               "Ground — driveway / laydown", "Ground — around back",
               "Ground — closest gate to the ladder", "Split it — see the note"];
  function drop() { return ax("Where it lands", [n("roof or ground")].concat(DROPS), true); }
  /* The one flag that repeats: this colour/lot has to match what is already on the
   * roof. On field, on cap, on the metal and the vents that show. */
  function matchLot() { return [{ k: "lot", label: "Colour / lot has to match the roof" }]; }

  window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

  window.TOOLKIT_ITEMS.load = {
    drops: DROPS,

    cats: [
      {
        id: "list",
        name: "What are you ordering?",
        docName: "The order",
        hint: "Paste your takeoff if you keep one — one line each. Count it the way you say it: 30 square, 12 roll, 4 boxes, a pail. Then set where it lands on the heavy stuff below.",
        writein: true,
        items: []
      },

      {
        id: "field",
        name: "Field — what goes down",
        docName: "Field",
        hint: "The roof itself, by the SQUARE or the ROLL. Say the colour and the profile off your submittal on anything that shows, and tick MATCH if it has to line up with what's already on the roof.",
        items: [
          { n: "Architectural / laminate shingle", sub: "BY THE SQUARE", unit: "sq",
            flags: matchLot(), notePlaceholder: "colour and profile off the approved submittal, and the lot if you've got the ticket",
            ax: [drop()] },
          { n: "3-tab shingle", sub: "BY THE SQUARE", unit: "sq",
            flags: matchLot(), notePlaceholder: "colour off the submittal",
            ax: [drop()] },
          { n: "Designer / luxury shingle", sub: "BY THE SQUARE — SAY THE BUNDLE COUNT, IT'S NOT ALWAYS THREE", unit: "sq",
            flags: matchLot(), notePlaceholder: "colour and line off the submittal, and bundles per square",
            ax: [drop()] },
          { n: "Metal panel / standing-seam", sub: "BY THE PANEL — LENGTH AND COLOUR OFF YOUR ORDER, THIS PAGE WON'T CUT IT", unit: "panel",
            flags: matchLot(), notePlaceholder: "colour, profile and the panel lengths off your order",
            ax: [drop()] },
          { n: "Tile — concrete or clay", sub: "BY THE SQUARE OR THE PIECE — SAY WHICH, AND THE PROFILE",
            flags: matchLot(), notePlaceholder: "profile and colour off the submittal, and field vs trim pieces",
            ax: [drop()] },
          { n: "Wood shake / shingle", sub: "BY THE SQUARE OR THE BUNDLE — SAY WHICH, AND CEDAR OR THE TREATED KIND",
            flags: matchLot(), notePlaceholder: "shake or shingle, cedar or fire-treated, and the grade off your set",
            ax: [drop()] },
          { n: "TPO / PVC membrane", sub: "BY THE ROLL — SAY THE COLOUR AND THE WIDTH, NOT THE THICKNESS", unit: "roll",
            flags: matchLot(), notePlaceholder: "colour and width off your set — the thickness is the spec's, not this page's",
            ax: [drop()] },
          { n: "EPDM membrane", sub: "BY THE ROLL — SAY THE WIDTH", unit: "roll",
            notePlaceholder: "width off your set, and black or the other one",
            ax: [drop()] },
          { n: "Mod-bit cap sheet", sub: "BY THE ROLL — SAY THE GRANULE COLOUR IF IT'S EXPOSED", unit: "roll",
            flags: matchLot(), notePlaceholder: "colour if it shows, and torch, cold or self-adhered off your set",
            ax: [drop()] },
          { n: "Mod-bit / BUR base ply", sub: "BY THE ROLL", unit: "roll",
            notePlaceholder: "which ply and how it attaches, off your set",
            ax: [drop()] }
        ]
      },

      {
        id: "underlay",
        name: "Underlayment & leak barrier",
        docName: "Underlayment & leak barrier",
        hint: "What dries the deck in under the field. Nobody covers a roof without it — how much and where is off your set and the code, not off this page.",
        items: [
          { n: "Synthetic underlayment", sub: "BY THE ROLL", unit: "roll", ax: [drop()] },
          { n: "Felt — 15 lb", sub: "BY THE ROLL", unit: "roll", ax: [drop()] },
          { n: "Felt — 30 lb", sub: "BY THE ROLL", unit: "roll", ax: [drop()] },
          { n: "Ice & water / leak barrier", sub: "BY THE ROLL — EAVES, VALLEYS, PENETRATIONS OFF YOUR SET", unit: "roll",
            notePlaceholder: "where it goes is off your set and the code — this page just orders the roll",
            ax: [drop()] },
          { n: "Base sheet — mechanically attached", sub: "BY THE ROLL", unit: "roll", ax: [drop()] }
        ]
      },

      {
        id: "starter",
        name: "Starter, hip & ridge",
        docName: "Starter, hip & ridge",
        hint: "The first course and the last one. A shingle order with no starter and no cap is a re-trip to the yard by noon — tick MATCH on the cap, it's the same colour argument as the field.",
        items: [
          { n: "Starter strip", sub: "BY THE BUNDLE", unit: "bundle", ax: [drop()] },
          { n: "Hip & ridge cap", sub: "BY THE BUNDLE — SAME COLOUR AS THE FIELD", unit: "bundle",
            flags: matchLot(), notePlaceholder: "colour to match the field off the submittal",
            ax: [drop()] },
          { n: "Ridge cap — metal", sub: "BY THE STICK OR THE PIECE — COLOUR OFF YOUR ORDER", unit: "stick",
            flags: matchLot(), notePlaceholder: "colour and length off your order",
            ax: [drop()] }
        ]
      },

      {
        id: "metal",
        name: "Edge metal & flashing",
        docName: "Edge metal & flashing",
        hint: "Everything bent, cut or formed. What shows comes in a colour — tick MATCH on it. Sizes and gauges are off your set; this page carries what you write and sizes nothing.",
        items: [
          { n: "Drip edge", sub: "BY THE STICK — SAY THE FACE AND THE COLOUR", unit: "stick",
            flags: matchLot(), notePlaceholder: "colour and face off your order — the gauge is the spec's",
            ax: [drop()] },
          { n: "Gravel stop / edge metal", sub: "BY THE STICK — LOW-SLOPE PERIMETER", unit: "stick",
            flags: matchLot(), notePlaceholder: "profile and colour off your order",
            ax: [drop()] },
          { n: "Coping", sub: "BY THE STICK — LENGTH AND COLOUR OFF THE SHOP DRAWING", unit: "stick",
            flags: matchLot(), notePlaceholder: "length, colour and the corners off the shop drawing",
            ax: [drop()] },
          { n: "Counter-flashing / reglet", sub: "BY THE STICK", unit: "stick",
            notePlaceholder: "profile off your set", ax: [drop()] },
          { n: "Step flashing", sub: "BY THE BOX OR THE BUNDLE — SAY WHICH",
            notePlaceholder: "size off your set, and box or bundle", ax: [drop()] },
          { n: "Valley metal", sub: "BY THE STICK — SAY W-VALLEY OR OPEN, AND COLOUR IF IT SHOWS", unit: "stick",
            notePlaceholder: "profile, and colour if it's an open valley",
            ax: [drop()] },
          { n: "Pipe boots / jack flashing", sub: "EACH — SAY THE PIPE SIZE, THIS PAGE WON'T", unit: "ea",
            notePlaceholder: "the pipe sizes you've got, and lead, rubber or the retrofit kind",
            ax: [drop()] },
          { n: "Pitch pan", sub: "EACH — SAY IF YOU NEED THE POURABLE FILLER TOO", unit: "ea",
            ax: [drop()] },
          { n: "Kickout / diverter flashing", sub: "EACH", unit: "ea", ax: [drop()] },
          { n: "Termination bar", sub: "BY THE STICK — LOW-SLOPE", unit: "stick", ax: [drop()] },
          { n: "Snow guard / snow rail", sub: "EACH OR BY THE STICK — SAY WHICH, AND COLOUR IF IT SHOWS",
            flags: matchLot(), notePlaceholder: "the profile and the spacing off your set — this page won't lay them out",
            ax: [drop()] },
          { n: "Flat / coil stock", sub: "BY THE ROLL OR THE SHEET — SAY WHICH, AND THE COLOUR",
            flags: matchLot(), notePlaceholder: "gauge and colour off your order — for the pieces you brake on site",
            ax: [drop()] }
        ]
      },

      {
        id: "fasten",
        name: "Fasteners & plates",
        docName: "Fasteners & plates",
        hint: "How it stays on. The LENGTH, the pattern and the density are off your set and your uplift detail — name them in your words; this page won't put a number in your mouth.",
        items: [
          { n: "Coil nails", sub: "BY THE BOX — LENGTH OFF YOUR SET", unit: "bx",
            notePlaceholder: "the length your set calls for, in your words — this page doesn't size it" },
          { n: "Cap nails", sub: "BY THE BOX", unit: "bx",
            notePlaceholder: "length off your set" },
          { n: "Hand-drive roofing nails", sub: "BY THE BOX", unit: "bx",
            notePlaceholder: "length off your set" },
          { n: "Insulation / membrane screws", sub: "BY THE BOX — SAY THE DECK YOU'RE INTO", unit: "bx",
            notePlaceholder: "length and the deck (steel, wood, concrete) — the pattern is off your set" },
          { n: "Plates / insulation plates", sub: "BY THE BOX", unit: "bx" },
          { n: "Cap staples", sub: "BY THE BOX", unit: "bx" }
        ]
      },

      {
        id: "acc",
        name: "Adhesive, sealant & the rest",
        docName: "Adhesive, sealant & the rest",
        hint: "What bonds it, seals it and lets a man walk it. The stuff you're always one pail short of at four o'clock.",
        items: [
          { n: "Bonding adhesive", sub: "BY THE PAIL — MEMBRANE", unit: "pail",
            notePlaceholder: "which one your membrane calls for — the wrong one is a warranty argument" },
          { n: "Seam / cover tape", sub: "BY THE ROLL", unit: "roll" },
          { n: "Lap / water cut-off sealant", sub: "BY THE TUBE", unit: "tube" },
          { n: "Flashing cement / mastic", sub: "BY THE PAIL OR THE TUBE — SAY WHICH" },
          { n: "Roof primer", sub: "BY THE PAIL", unit: "pail" },
          { n: "Sealant / caulk", sub: "BY THE TUBE — SAY THE COLOUR IF IT SHOWS", unit: "tube",
            notePlaceholder: "colour if it's exposed" },
          { n: "Pourable pitch-pan filler", sub: "SAY HOW MANY POCKETS", unit: "ea" },
          { n: "Cants", sub: "BY THE PIECE — LOW-SLOPE", unit: "ea", ax: [drop()] },
          { n: "Walk pad / walkway", sub: "BY THE ROLL OR THE PIECE — SAY WHICH",
            ax: [drop()] }
        ]
      },

      {
        id: "iso",
        name: "Insulation & board",
        docName: "Insulation & board",
        hint: "Low-slope. Thickness, R-value and the tapered slope are off your set and your tapered plan — this page orders the board and specs none of it.",
        items: [
          { n: "ISO board", sub: "BY THE BOARD — THICKNESS OFF YOUR SET, NOT AN R-VALUE", unit: "board",
            notePlaceholder: "the thickness your set calls for, in your words — no R-value from this page",
            ax: [drop()] },
          { n: "Cover board", sub: "BY THE BOARD", unit: "board",
            notePlaceholder: "which one your set calls for, and the thickness",
            ax: [drop()] },
          { n: "Tapered — a package off your plan", sub: "BY THE SQUARE — THE SLOPE IS YOUR TAPERED PLAN'S, NOT THIS PAGE'S",
            notePlaceholder: "the tapered plan or the area — the slope and the layout come off that plan",
            ax: [drop()] },
          { n: "Recovery / fanfold board", sub: "BY THE BOARD OR THE BUNDLE — SAY WHICH", unit: "board",
            ax: [drop()] }
        ]
      },

      {
        id: "vent",
        name: "Ventilation",
        docName: "Ventilation",
        hint: "What lets it breathe. How much is off your set — this page counts the pieces, it doesn't figure the net free area.",
        items: [
          { n: "Ridge vent", sub: "BY THE STICK OR THE ROLL — SAY WHICH", unit: "stick",
            notePlaceholder: "which kind, off your set", ax: [drop()] },
          { n: "Box / turtle vents", sub: "EACH — SAY THE COLOUR IF IT SHOWS", unit: "ea",
            flags: matchLot(), notePlaceholder: "colour if it's on a visible slope",
            ax: [drop()] },
          { n: "Off-ridge / low-profile vent", sub: "EACH", unit: "ea", ax: [drop()] },
          { n: "Turbine", sub: "EACH", unit: "ea", ax: [drop()] },
          { n: "Powered / solar vent", sub: "EACH", unit: "ea", ax: [drop()] },
          { n: "Soffit / intake vent", sub: "BY THE PIECE — SAY THE LENGTH", unit: "ea",
            notePlaceholder: "length, and colour if it shows" },
          { n: "Gable vent", sub: "EACH — SAY THE COLOUR IF IT SHOWS", unit: "ea",
            flags: matchLot(), notePlaceholder: "colour if it shows" }
        ]
      },

      {
        id: "deliver",
        name: "The lift, and what goes back",
        docName: "The lift, and what goes back",
        hint: "The half of the order nobody makes. A boom window you didn't ask for is a crew standing on the ground, and empties on the lawn are a callback you gave yourself.",
        items: [
          { n: "Boom / conveyor / crane time", sub: "SAY WHEN YOU NEED IT AND HOW LONG",
            notePlaceholder: "when it lands, how long, and who's flagging the ground" },
          { n: "Ground protection / driveway plywood", sub: "IF THE TRUCK'S ON THE DRIVE" },
          { n: "Take the empty pallets / cores back", sub: "SAY ROUGHLY HOW MANY", unit: "ea" },
          { n: "Take the leftover material back", sub: "SAY WHAT IT IS AND IF IT'S BEEN RAINED ON" },
          { n: "Dumpster / disposal", sub: "SAY THE SIZE AND WHEN — IF THE YARD HANDLES IT" }
        ]
      }
    ],

    /* A pasted line gets the same landing as a picked one — a write-in is where
     * the odd item lands ("6 square of the discontinued colour"), and it is the
     * line most likely to end up on the wrong slope if nobody says where it goes. */
    writeinAx: [drop()]
  };
})();

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
    { "es": "Me lo dijo en el techo", "en": "Told me on the roof" },
    { "es": "Texto / correo", "en": "Text / email" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me entregó el plano del techo marcado", "en": "Marked-up roof plan handed to me" },
    { "es": "Lo dijo en la junta del tráiler", "en": "Said it in the trailer meeting" }
  ],
  "notin": [
    { "es": "Solo reparación del deck", "sub": "no el sistema de techo que va encima", "en": "Deck repair only" },
    { "es": "Solo el cut-off temporal", "sub": "el tie-in permanente va aparte", "en": "Temporary cut-off only" },
    { "es": "No el tear-off que ya está en el contrato", "en": "Not the tear-off already in contract" },
    { "es": "Sin re-inspección ni recorrido de garantía después", "en": "No re-inspection or warranty walk after this" },
    { "es": "Sin horas de grúa, malacate ni loader", "sub": "a menos que esté abajo en la lista", "en": "No crane, hoist or loader time" },
    { "es": "Sin horas de espera de la cuadrilla que se quedó parada", "en": "No stand-by hours for the crew that waited" },
    { "es": "Sin dumpster extra ni tirar lo que salió", "en": "No extra dumpster or disposal for what came off" },
    { "es": "No es reclamo por atraso ni impacto al programa", "en": "Not a delay claim and not a schedule impact" },
    { "es": "Sin protección interior, plafón ni tablaroca", "en": "No interior protection, ceiling or drywall work" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas en el deck abierto", "en": "In this message — shot on the open deck" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "Súper del GC", "en": "GC super" },
    { "es": "PM del GC", "en": "GC PM" },
    { "es": "Nuestro GF o PM", "en": "Our GF or PM" },
    { "es": "Rep del dueño / administrador del edificio", "en": "Owner's rep / property manager" },
    { "es": "Ingeniero del edificio", "en": "Building engineer" },
    { "es": "Arquitecto, ingeniero o consultor de techos", "en": "Architect, engineer or roof consultant" },
    { "es": "Rep de campo del fabricante", "en": "Manufacturer's field rep" },
    { "es": "Dueño de la casa", "en": "Homeowner" },
    { "es": "Mayordomo de otro contratista", "en": "Another trade's foreman" }
  ],
  "why": [
    { "es": "No está en nuestro scope", "en": "Not in our scope" },
    { "es": "Se encontró después del tear-off", "sub": "nadie lo podía ver cuando se cotizó", "en": "Found it after tear-off" },
    { "es": "El deck salió malo abajo", "en": "Deck came up bad underneath" },
    { "es": "Aislante mojado — más del allowance", "en": "Wet insulation — more than the allowance" },
    { "es": "Una capa extra que nadie avisó", "en": "Extra layer nobody disclosed" },
    { "es": "Condiciones existentes", "sub": "no lo que muestran los as-builts ni el plano del techo", "en": "Existing conditions" },
    { "es": "Otro contratista dejó trabajo donde va mi techo", "en": "Another trade's work is on my roof line" },
    { "es": "Daño de otros que tuvimos que reparar para seguir", "en": "Damage by others we had to repair to keep going" },
    { "es": "Nos mandaron trabajar fuera de secuencia", "en": "Told to work out of sequence" },
    { "es": "No nos dejaron subir al techo, y luego que repusiéramos el día", "en": "Held off the roof, then told to make the day up" },
    { "es": "Cut-off de emergencia por agua — nos agarró la lluvia", "en": "Emergency water cut-off — weather moved on us" }
  ]
};
