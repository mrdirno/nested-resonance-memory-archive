/* PLUMBING FIELD TOOLKIT — VOCABULARY DATA.
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Classifications,
 * reason lists, size ladders and configuration options live HERE — never in the
 * identity config and never inline in a tool page.
 *
 * TWO HARD INVARIANTS (§SAFETY): ZERO BRAND NAMES, and NOTHING IS COMPUTED OR
 * RATED. Every value below is something the tradesman PICKS — no sizing, no
 * ratings, no code references, no rates and no totals, not as a value, not as a
 * hint, not in a placeholder.
 *
 * This trade stood up before the boundary existed, so its FIRST tool still
 * carries its data inline. That is the migration debt, to be retired the next
 * time that page is touched.
 */

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working PLUMBING hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · WHAT IS **NOT** IN THIS TAG is the field this trade fights about and no other
   *    trade asked for. Ceiling left open, slab cored, sleeve in but firestop still
   *    to do, capped and holding but not trimmed — naming it the day it happened is
   *    what stops it being back-charged three months later.
   *  · SAY TAG, NEVER TICKET OR FORM. "Get a tag on it." "He signed the tag." "The
   *    yellow copy." T&M is never spelled out and extra work is "an extra".
   *  · THE ORDER OF THE OUTPUT IS THE ORDER OF THE YELLOW COPY. The triplicate book
   *    is contractual and is never going away, so this page only survives if he can
   *    read it straight off while he fills the paper one — otherwise it is a third
   *    form and it is dead on contact (§THE SYSTEM OF RECORD).
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "Super",
    "GC PM",
    "Owner / tenant",
    "Our PM",
    "Another sub's foreman",
    "Somebody else"
  ],
  "how": [
    {
      "v": "Face to face at the work"
    },
    {
      "v": "On the phone"
    },
    {
      "v": "Text / email"
    },
    {
      "v": "Field order / marked print"
    }
  ],
  "why": [
    {
      "name": "Not on my prints"
    },
    {
      "name": "Owner / tenant change after rough"
    },
    {
      "name": "Existing conditions",
      "sub": "not what the as-builts show"
    },
    {
      "name": "Rotted existing — had to replace it to tie in"
    },
    {
      "name": "Another trade in my way — moved it or stood by"
    },
    {
      "name": "Damage by others — we fixed it"
    },
    {
      "name": "Inspector wouldn't pass it as drawn"
    },
    {
      "name": "Emergency — leak / main stopped up"
    }
  ],
  "notin": [
    {
      "name": "Ceiling / wall left open",
      "sub": "put-back + paint not mine"
    },
    {
      "name": "Slab cored",
      "sub": "patch not mine"
    },
    {
      "name": "Sleeve in — firestop still to do"
    },
    {
      "name": "Not tested yet"
    },
    {
      "name": "Capped and holding — still needs trim"
    },
    {
      "name": "Needs a come-back to finish"
    }
  ],
  "classes": [
    "— class",
    "JOURNEYMAN",
    "APPRENTICE",
    "FOREMAN"
  ],
  "pics": [
    {
      "v": "In this message — shot before we closed it"
    },
    {
      "v": "None"
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
  toolName: "Hole & Backing List",
  eyebrow: "Plumbing · you → the other trades",
  lede: "Everything another outfit has to dig, pour, lay in, back, or energize before I can rough it in — who owes it, where it is, and the gate it has to beat.",
  docSubject: "Holes and backing — what we need before it's covered",
  docSubjectWith: "Holes and backing — what we need from {to}",
  closing: "That's what I need from you before it closes up. Text me back what you'll hit and what you won't — if one of these ain't happening, tell me now while it's still cheap to fix.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> drawings. This page sizes nothing — no pipe, no sleeve, no core, no pad, no depth — it sets no invert and no slope, and it doesn't know what the code, the engineer or the inspector requires. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The sheet and revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C",
  phOff: "P-201 rev 2",
  phFrom: "Sal — Local 38",
  phArea: "Rm 118 — then it's a button",
  areaLabel: "Room / area / gridline",

  who: [
    { v: "gc-super", label: "GC super" },
    { v: "concrete", label: "Concrete" },
    { v: "framer", label: "Framer/drywall" },
    { v: "ec", label: "EC foreman" },
    { v: "mason", label: "Mason" },
    { v: "sitework", label: "Dirt guy" },
    { v: "steel", label: "Steel guys" },
    { v: "roofer", label: "Roofer" }
  ],

  // EARLIEST FIRST — this is the order a job actually closes up in, and it is
  // why grouping by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "backfill", label: "Before they backfill" },
    { v: "slab-pour", label: "Before the slab pour" },
    { v: "block-up", label: "Before block goes up" },
    { v: "deck-pour", label: "Before the deck pour" },
    { v: "dryin", label: "Before roof dry-in" },
    { v: "walls-close", label: "Before walls close" },
    { v: "ceiling-close", label: "Before ceiling closes" },
    { v: "startup", label: "Before startup" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "sleeve-pour", label: "Sleeve in the pour", who: "concrete", by: "slab-pour", specs: [
      "PVC sleeve — I'll drop them on site",
      "Galv sleeve — you furnish",
      "Sleeve one size up off my pipe",
      "Stub it above the slab so I can find it",
      "Cap or tape it so it don't fill",
      "Set to my paint mark, not the plan"
    ] },
    { v: "backing", label: "Backing for carriers", who: "framer", by: "walls-close", specs: [
      "Backing for a wall-hung closet carrier",
      "Backing for the lav carrier",
      "Backing for the urinal",
      "Backing for grab bars",
      "Backing for the drinking fountain",
      "Backing for the wall-hung sink",
      "Double the studs where the carrier lands"
    ] },
    { v: "blockout", label: "Blockout in the slab", who: "concrete", by: "slab-pour", specs: [
      "Blockout for the closet riser",
      "Blockout at my floor drain",
      "Trench drain blockout — I set the frame",
      "Pit for the grease interceptor",
      "Elevator sump pit",
      "Depress the slab at the shower pan",
      "Box it out — I'll patch it after"
    ] },
    { v: "sleeve-block", label: "Sleeve in the block", who: "mason", by: "block-up", specs: [
      "Sleeve laid in as you go up",
      "Chase in the block for my stack",
      "Leave the cell open — don't grout it",
      "Knock-out at my paint mark",
      "Sleeve through the knee wall",
      "Sleeve I can seal after"
    ] },
    { v: "chase", label: "Fur out the wet wall", who: "framer", by: "walls-close", specs: [
      "Fur it out — my closet bend won't fit",
      "Deeper wall behind the water closets",
      "Wider chase for the stack",
      "No stud where my riser lands",
      "Chase runs floor to deck, don't stop it",
      "Furring on the block for my drops"
    ] },
    { v: "core", label: "Core it for me", who: "gc-super", by: "walls-close", specs: [
      "Scan it first — I'm not hitting cable",
      "Core the slab at my mark",
      "Core the deck from below",
      "Core through the block wall",
      "Wet core — bring a vac and a plug",
      "Patch it back once I'm through",
      "Get it cored before they rock"
    ] },
    { v: "vtr", label: "Vents through the roof", who: "roofer", by: "dryin", specs: [
      "Sleeve my vents before you dry in",
      "You flash them, I'll set the stack",
      "Don't roof over my openings",
      "Vent's got to clear the curb — walk it with me"
    ] },
    { v: "pre-pour", label: "Pre-pour walk", who: "concrete", by: "slab-pour", specs: [
      "Walk it with me before you place",
      "Don't pour till I check my stubs",
      "Give me the pour date — I'll be there",
      "Morning of, before the mud shows up",
      "Nobody moves my stubs after I leave",
      "Let me brace my risers first"
    ] },
    { v: "dirt", label: "Dig and bed my trench", who: "sitework", by: "backfill", specs: [
      "Dig to my paint and flags",
      "Sand or fines in the bottom, no rock",
      "Leave it open till I'm inspected",
      "Shore it — it's deep and it's wet",
      "Backfill in lifts, don't dump it on me",
      "Haul the spoils off, no room to pile",
      "Pump it down — I'm standing in water"
    ] },
    { v: "power", label: "Power to my equipment", who: "ec", by: "walls-close", specs: [
      "Circuit and disconnect at the unit",
      "Just a whip — I'll land it myself",
      "Hard-wired, not cord and plug",
      "Receptacle at the unit for the pump",
      "Power for the recirc pump",
      "Power for my controls only",
      "Get it in your rough — it's in a wall"
    ] },
    { v: "hold-open", label: "Leave me an opening", who: "gc-super", by: "walls-close", specs: [
      "Hold the wall till my heater's in",
      "Hold the door frame — unit won't fit",
      "Leave the last block course out",
      "Ceiling stays open over my unit",
      "Keep the rigging path clear",
      "Leave a knockout panel I can rock later"
    ] },
    { v: "access", label: "Access panel", who: "gc-super", by: "ceiling-close", specs: [
      "Access at my cleanout",
      "Access at the shutoff valve",
      "Access at the mixing valve",
      "Access at the tub waste",
      "Access at the backflow",
      "In the lid, not in the wall",
      "Big enough for my arm and a wrench"
    ] },
    { v: "pad", label: "Housekeeping pad", who: "concrete", by: "walls-close", specs: [
      "Pad under the water heater",
      "Pad under the booster skid",
      "Pad for the duplex pump set",
      "Pad under the softener and filters",
      "Curb the pad — it's a wet room",
      "Pad set to my equipment feet",
      "Pour it before I set, I'm not shimming"
    ] },
    { v: "steel-support", label: "Steel for my hangers", who: "steel", by: "deck-pour", specs: [
      "Angle across the joists for my riser",
      "Trapeze steel over my rack",
      "Weld me a clip on the column",
      "Inserts in the pour where I marked",
      "Kicker at my stack so it don't walk",
      "Something to hang the offset off"
    ] },
    { v: "roof-drain", label: "Roof drain openings", who: "steel", by: "deck-pour", specs: [
      "Open the deck at each drain",
      "Overflow opening beside the primary",
      "Frame it in the joists, not on my line",
      "Sump pan set at the drain",
      "Leave it open till my body's in",
      "Blockout in the pour at my drains"
    ] },
    { v: "energize", label: "Power on for startup", who: "ec", by: "startup", specs: [
      "Need it hot — vendor's here to fire it",
      "Breaker's off, need it turned on",
      "It's landed but not energized",
      "Label the disconnect so nobody kills it",
      "Temp power on the pump till permanent",
      "Need it hot to fill and test"
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
  toolName: "Yes, No, and When",
  eyebrow: "Plumbing · them → you → back",
  lede: "The GC or another trade sent you a list. Line it up, give each one a yes, a no, or a question — and a date on every yes — then send it back in one message.",
  docSubject: "my answer on your list",
  closing: "That’s the yes, the no, and the when. Anything I flagged I need back from you before the pour, not after — once that slab is down we’re both talking about a core bit.",
  phJob: "Building C", phTo: "Ken — site super", phFrom: "Sal — Local 38", phOff: "A-201 rev 4",
  paste: "Building C — close-in list — Aug 9\n\nJob: Building C\nFrom: Ken — site super\n\nLevel 2 · all your sleeves in before Thursday’s pour\nRestroom 210 · carriers set and backing in before rock\nRoof · vents through before dry-in"
};

/* GETTING IN (getting-in.html) — ported from AV's reference block with the
 * shape, handback rules and no-channel-back discipline untouched; only the
 * words change. The locked room becomes the mechanical room / riser closet,
 * not the rack room / IDF. The heads-up list trades AV's fire-alarm-panel
 * touch and bare power-down for this trade's own: restrooms out of service, a
 * sprinkler head OR MAIN in the way, water going off to a riser or the whole
 * building, and hot work named for what it actually is here — torch or solder
 * on copper. `run`, `closing` and `warn` carry over verbatim; a line that
 * already works doesn't get rewritten.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Plumbing · you → whoever holds the keys",
  lede: "You need into a room somebody else locks. Send the ask that gets a yes on the first try — the night, the rooms, who’s coming, and the heads-up that stops a crew getting turned away at the door.",
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
    { name: "The mechanical room / riser closet open too", sub: "not just the room we’re working in" },
    { name: "Somebody who knows where the shutoffs are", sub: "the as-builts don’t match what’s in the wall" },
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
    { name: "Restrooms out of service", sub: "tell me which ones you can be without, and for how long" },
    { name: "A sprinkler head or main is in the way", sub: "that’s your impairment process — tell me how you run it" },
    { name: "Water’s going off — a riser or the whole building", sub: "tell me how much notice you need and I’ll hold to the window" },
    { name: "Hot work on copper — torch or solder", sub: "that’s your permit — tell me how you want it done" },
    { name: "Patient or clinical space next door", sub: "tell me what you need from us before we start" }
  ],

  phSite: "Riverside Medical Center",
  phRoom: "Mech 2B",
  phHow: "basement level, past the boiler room",
  phScope: "re-piping the domestic riser from the basement to the 4th floor",
  phLoud: "core drilling about 2 hrs, done by 9",
  phTo: "Carlos — building engineer",
  phMe: "D. Okafor — 415-555-0177",
  phCo: "Harbor Mechanical",

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
    { "es": "OFICIAL (JOURNEYMAN)", "en": "JOURNEYMAN" },
    { "es": "APRENDIZ (APPRENTICE)", "en": "APPRENTICE" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" }
  ],
  "how": [
    { "es": "En persona, en el trabajo", "en": "Face to face at the work" },
    { "es": "Por teléfono", "en": "On the phone" },
    { "es": "Texto / correo", "en": "Text / email" },
    { "es": "Orden de campo / plano marcado", "en": "Field order / marked print" }
  ],
  "notin": [
    { "es": "Plafón / pared quedaron abiertos", "sub": "reponer y pintar no me toca", "en": "Ceiling / wall left open" },
    { "es": "Losa coreada", "sub": "el parche no me toca", "en": "Slab cored" },
    { "es": "Sleeve puesto — falta el firestop", "en": "Sleeve in — firestop still to do" },
    { "es": "Todavía sin probar", "en": "Not tested yet" },
    { "es": "Con tapón y aguantando — falta el trim", "en": "Capped and holding — still needs trim" },
    { "es": "Hay que regresar para terminar", "en": "Needs a come-back to finish" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas antes de cerrar", "en": "In this message — shot before we closed it" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "El súper", "en": "Super" },
    { "es": "PM del GC", "en": "GC PM" },
    { "es": "Dueño / inquilino", "en": "Owner / tenant" },
    { "es": "Nuestro PM", "en": "Our PM" },
    { "es": "Mayordomo de otro sub", "en": "Another sub's foreman" },
    { "es": "Otra persona", "en": "Somebody else" }
  ],
  "why": [
    { "es": "No está en mis planos", "en": "Not on my prints" },
    { "es": "Cambio del dueño / inquilino después del rough-in", "en": "Owner / tenant change after rough" },
    { "es": "Condiciones existentes", "sub": "no es lo que traen los as-builts", "en": "Existing conditions" },
    { "es": "Lo existente podrido — hubo que cambiarlo para entroncar", "en": "Rotted existing — had to replace it to tie in" },
    { "es": "Otro contratista estorbando — lo movimos o esperamos parados", "en": "Another trade in my way — moved it or stood by" },
    { "es": "Daño de otros — lo arreglamos nosotros", "en": "Damage by others — we fixed it" },
    { "es": "El inspector no lo pasó como está en el plano", "en": "Inspector wouldn't pass it as drawn" },
    { "es": "Emergencia — fuga / drenaje principal tapado", "en": "Emergency — leak / main stopped up" }
  ]
};
