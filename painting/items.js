/* PAINTING FIELD TOOLKIT — THE TRADE'S VOCABULARY.
 *
 * `trade.js` = IDENTITY + COPY · `tools.js` = REGISTRY · this file = the WORDS.
 * Categories, option lists, ask lines, ladders. Nothing here is a runtime and
 * nothing here is a number we supply.
 *
 * WHERE THESE WORDS CAME FROM. Three independent in-trade lenses — a 25-year
 * working foreman, a four-man shop's owner-operator, and the GC super who
 * chases paint crews daily — each wrote this trade's tool set with no sight of
 * the others, and a 20-year prune then killed two thirds of the union. The
 * convergence is the finding: all three named the store call, the room that
 * is not ready, the after-final damage record and the color nobody will put
 * in writing — those are the pages, because three witnesses put them there.
 *
 * THE REFUSAL IS THE DESIGN (trade.js carries the full list). Nothing in this
 * file is:
 *   · a spread rate, a coverage figure, or gallons-per-anything;
 *   · a film build, a dry/recoat/cure time, a pot life;
 *   · a temperature, humidity, dew-point or moisture threshold;
 *   · a prep-grade requirement or any wording that reads as "surface ready";
 *   · a product system, a brand, a color, a tint formula, or a base FOR a
 *     product — sheen words and tint-base words appear only as the trade's
 *     own vocabulary for what HE already picked off HIS schedule;
 *   · a lead/RRP determination, a VOC ruling, or an exposure number.
 * Every one of those is a place where the honest tool structures what the USER
 * states off his own schedule, submittal, can and data sheet. A later cycle
 * that adds one is not filling a gap; it is the defect this file was built to
 * refuse.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── THE STORE CALL (shape #1 — shared/checklist-request.js) ────────────────
 * The 6:30 text to the paint counter, pulled and at will-call before the truck
 * arrives. Two mechanisms stolen rather than re-derived, per the record:
 *
 *  · THE SECOND READING IS THE TINT LIST — sitework's buried-list mechanism
 *    with the shaker where the ditch was. A short line anywhere else is a trip
 *    back to the counter; a line tinted wrong is gallons that cannot go back
 *    on the shelf. So every line the DATA marks `tint: true` is gathered
 *    under one heading the counter cannot skim past. Derived, never tapped —
 *    only a WRITE-IN carries the tick, because a line he typed is a sentence
 *    only he can classify.
 *
 *  · THE BATCH IS MASONRY'S RUN. Touch-up and added rooms have to come out of
 *    the same batch as what is already on the wall, or the wall gets a stripe
 *    at four o'clock that nobody can wash off. A FLAG on the lines it applies
 *    to, a passthrough in the header, and a call-out when one exists without
 *    the other — including the inverse, where he typed what has to match and
 *    flagged nothing.
 *
 * THE PAINT LINES CARRY NO PRODUCT. The row is the surface he is buying for;
 * the note is where HIS schedule's product, color name and number go, exactly
 * as the submittal prints them. Sheen and tint-base ride as axes because they
 * are the two words the counter asks for back — they are his picks, and the
 * neutral leads every list so a value nobody chose never reaches the desk.
 */
(function () {
  "use strict";
  function n(q) { return "— " + q + " —"; }
  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }
  /* SHEEN IS VOCABULARY, NOT A SPEC. These are the words the wall gets argued
     in and the counter repeats back; which one is RIGHT lives on his schedule
     and this page does not know it. */
  function sheen() {
    return ax("Sheen", [n("which sheen — off your schedule"),
      "Flat", "Matte", "Eggshell", "Satin", "Semi-gloss", "Gloss", "Two sheens — see the note"]);
  }
  /* The tint base is the counter's own question — "what base am I pulling?" —
     and the answer is printed on his schedule or his last can. Words, not a
     formula: the formula belongs to the shaker. */
  function base() {
    return ax("Base", [n("which base — off the schedule or the last can"),
      "White / base 1", "Base 2 / midtone", "Base 3 / deep", "Base 4 / ultra-deep", "Clear / accent", "It's on the note"]);
  }
  function tapeW() { return ax("Width", [n("which width"), "3/4 in", "1 in", "1.5 in", "2 in", "Mixed — see the note"]); }
  function paperW() { return ax("Width", [n("which width"), "6 in", "9 in", "12 in", "18 in"]); }
  function nap() { return ax("Nap", [n("which nap"), "1/4 in", "3/8 in", "1/2 in", "3/4 in", "1-1/4 in", "Mixed — see the note"]); }
  function brushW() { return ax("Width", [n("which width"), "1.5 in", "2 in", "2.5 in", "3 in", "4 in"]); }
  function grit() { return ax("Grit", [n("which grit"), "80", "100", "120", "150", "180", "220", "320", "Assorted — see the note"]); }
  /* The one flag that repeats: this has to come out of the batch that is
     already on the wall. */
  function matchBatch() { return [{ k: "batch", label: "Same batch — has to match what's up" }]; }

  window.TOOLKIT_ITEMS.store = {
    /* Ends-on-absence, the masonry steal: when a whole category is empty, the
       message closes on the question instead of the silence. At most two fire,
       and only for categories a real run through the store forgets. */
    absences: [
      { cat: "mask", q: "No tape or paper on this call — you covered from the last run?" },
      { cat: "app", q: "No covers or brushes on here — the wet ones spun and ready?" },
      { cat: "clean", q: "No rags on this call — there's never enough rags." }
    ],

    cats: [
      {
        id: "call",
        name: "What are you calling in?",
        docName: "The call",
        hint: "Paste your whole list if you keep one — one line each, counted the way you say it: 2 gal, 1 five, 3 qt, a case. Then tick Gets tinted on anything the shaker touches, and Same batch on anything that has to match a wall.",
        writein: true,
        items: []
      },

      {
        id: "paint",
        name: "The paint — off YOUR schedule",
        docName: "The paint",
        hint: "The row is the surface. The product line, the color name and the number go in the note, EXACTLY as your schedule or your last can prints them — this page picks no product and holds no color. Sheen and base are the two words the desk asks back; answer them here so the phone doesn't ring.",
        items: [
          { n: "Interior — walls", sub: "BY THE GAL OR THE FIVE — PRODUCT + COLOR NAME AND NUMBER IN THE NOTE, OFF YOUR SCHEDULE", unit: "gal", tint: true,
            notePlaceholder: "product line, color name + number, exactly as the schedule prints them",
            flags: matchBatch(), ax: [sheen(), base()] },
          { n: "Interior — ceilings", sub: "BY THE GAL OR THE FIVE — SAY IF IT'S THE SAME WHITE AS LAST TIME OR OFF THE SCHEDULE", unit: "gal", tint: true,
            notePlaceholder: "the ceiling white you're running, off the schedule or the last can",
            flags: matchBatch(), ax: [sheen(), base()] },
          { n: "Interior — doors, frames & trim", sub: "BY THE GAL OR THE QUART — THE ENAMEL OFF YOUR SCHEDULE, IN THE NOTE", unit: "gal", tint: true,
            notePlaceholder: "the trim enamel and color, exactly as the schedule prints it",
            flags: matchBatch(), ax: [sheen(), base()] },
          { n: "Exterior — body", sub: "BY THE FIVE — PRODUCT + COLOR IN THE NOTE, AND SAY WHAT IT'S GOING OVER IN YOUR OWN WORDS", unit: "five", tint: true,
            notePlaceholder: "product, color name + number — and what it's going over, your words",
            flags: matchBatch(), ax: [sheen(), base()] },
          { n: "Exterior — trim & doors", sub: "BY THE GAL — PRODUCT + COLOR IN THE NOTE", unit: "gal", tint: true,
            notePlaceholder: "product and color off your schedule",
            flags: matchBatch(), ax: [sheen(), base()] },
          { n: "Primer — tinted toward the topcoat", sub: "BY THE GAL OR THE FIVE — SAY WHICH TOPCOAT IT'S UNDER, THE DESK TINTS TOWARD IT", unit: "gal", tint: true,
            notePlaceholder: "which color it's going under — the desk gray-tints toward it",
            ax: [base()] },
          { n: "Primer / sealer — straight, no tint", sub: "BY THE GAL OR THE FIVE — THE ONE OFF YOUR SUBMITTAL, NAMED IN THE NOTE", unit: "gal",
            notePlaceholder: "the primer your submittal names — this page doesn't pick one" },
          { n: "Stain-blocking / bonding primer", sub: "BY THE CAN — SAY WHAT'S BLEEDING OR WHAT IT HAS TO GRAB, IN YOUR WORDS", unit: "ea",
            notePlaceholder: "what it's for — the water stain, the knots, the glossy frame — your words" },
          { n: "Specialty — dryfall, DTM, epoxy, elastomeric", sub: "BY NAME OFF YOUR SUBMITTAL — THIS PAGE PICKS NO SYSTEM AND NEVER WILL", unit: "five", tint: true,
            notePlaceholder: "the system exactly as your submittal names it, and the color",
            ax: [sheen()] },
          { n: "Stain / clear — rails, doors, feature wood", sub: "BY THE CAN — NAME AND SHEEN OFF YOUR SCHEDULE, AND SAY INTERIOR OR EXTERIOR", unit: "ea", tint: true,
            notePlaceholder: "the stain or clear off your schedule, and what it's going on",
            ax: [sheen()] }
        ]
      },

      {
        id: "prep",
        name: "Prep & patch",
        docName: "Prep & patch",
        hint: "The stuff the walls eat before the first gallon opens. Counted in the unit the store sells it in — say it with the number.",
        items: [
          { n: "Lightweight spackle / patch", sub: "BY THE TUB — SMALL FOR THE POUCH, BIG FOR THE CART", unit: "ea" },
          { n: "Setting-type compound", sub: "BY THE BAG — SAY THE WORKING TIME PRINTED ON THE ONE YOU RUN", unit: "bag",
            notePlaceholder: "the one you run — say the number printed on the bag, it's the store's word not ours" },
          { n: "Painter's caulk", sub: "BY THE CASE — THE PAINTABLE ONE YOU ALREADY RUN, NAMED IN THE NOTE", unit: "case",
            notePlaceholder: "the one you run — and say if any of it needs to be the exterior grade" },
          { n: "Wood filler / putty", sub: "BY THE CAN", unit: "ea" },
          { n: "Glazing putty / patch for the steel door", sub: "BY THE CAN — SAY WHAT IT'S FIXING", unit: "ea" },
          { n: "Sandpaper", sub: "BY THE SLEEVE — GRIT ON THE LINE", unit: "sleeve", ax: [grit()] },
          { n: "Sanding sponges", sub: "BY THE BOX", unit: "box", ax: [grit()] },
          { n: "Pole-sander sheets / discs", sub: "BY THE BOX — SAY WHICH HEAD THEY FIT IN THE NOTE", unit: "box", ax: [grit()] },
          { n: "Cleaner / TSP substitute", sub: "BY THE JUG", unit: "ea" },
          { n: "Deglosser", sub: "BY THE CAN — FOR WHAT WON'T GET SANDED", unit: "ea" },
          { n: "Tack cloths", sub: "BY THE BOX", unit: "box" }
        ]
      },

      {
        id: "mask",
        name: "Tape, paper & plastic",
        docName: "Tape, paper & plastic",
        hint: "Wide for the mask-off, narrow for the tight cuts, delicate for anything painted inside a month — cheap tape bills you twice.",
        items: [
          { n: "Tape — the everyday", sub: "BY THE SLEEVE — WIDTH ON THE LINE", unit: "sleeve", ax: [tapeW()] },
          { n: "Tape — delicate, for fresh finish", sub: "BY THE SLEEVE — GOES ON ANYTHING PAINTED THIS MONTH", unit: "sleeve", ax: [tapeW()] },
          { n: "Masking paper", sub: "BY THE ROLL — WIDTH ON THE LINE", unit: "roll", ax: [paperW()] },
          { n: "Masking film — the hand-masker rolls", sub: "BY THE ROLL — SAY WHICH MASKER IT FEEDS", unit: "roll" },
          { n: "Plastic sheeting", sub: "BY THE ROLL — SAY THE SIZE PRINTED ON THE ONE YOU WANT", unit: "roll",
            notePlaceholder: "the size off the shelf tag — it's the store's number, not ours" },
          { n: "Canvas drops", sub: "EACH — SAY THE SIZE, AND RUNNERS FOR THE WALK PATHS", unit: "ea" },
          { n: "Rosin / floor paper", sub: "BY THE ROLL", unit: "roll" },
          { n: "Carpet film / floor protection", sub: "BY THE ROLL — SAY CARPET OR HARD FLOOR, THEY'RE DIFFERENT ROLLS", unit: "roll" }
        ]
      },

      {
        id: "app",
        name: "Covers, brushes & poles",
        docName: "Covers, brushes & poles",
        hint: "Covers by the nap, brushes by the width. The sash you guard isn't on this list — this is the crew stock that walks off jobs.",
        items: [
          { n: "Roller covers — 9 in", sub: "BY THE EACH OR THE CASE — NAP ON THE LINE", unit: "ea", ax: [nap()] },
          { n: "Roller covers — 4 in / mini", sub: "BY THE EACH — NAP ON THE LINE", unit: "ea", ax: [nap()] },
          { n: "Roller covers — 18 in", sub: "BY THE EACH — FOR THE BIG WALLS, NAP ON THE LINE", unit: "ea", ax: [nap()] },
          { n: "Roller frames", sub: "EACH — SAY 9 / 4 / 18 IN THE NOTE", unit: "ea" },
          { n: "Brushes — angled sash", sub: "EACH — WIDTH ON THE LINE", unit: "ea", ax: [brushW()] },
          { n: "Brushes — chip / throwaway", sub: "BY THE BOX", unit: "box" },
          { n: "Extension poles", sub: "EACH — SAY THE REACH YOU NEED IN THE NOTE", unit: "ea" },
          { n: "Trays, liners & grids", sub: "BY THE EACH — GRIDS FOR THE FIVES, LINERS BY THE SLEEVE", unit: "ea" },
          { n: "Buckets — empty fives with lids", sub: "EACH — FOR BOXING", unit: "ea" },
          { n: "5-in-1s / pot hooks / spinners", sub: "EACH — THE HAND STUFF THAT GROWS LEGS", unit: "ea" }
        ]
      },

      {
        id: "rig",
        name: "For the rig",
        docName: "For the rig",
        hint: "Tips and filters are YOUR sizes off your own sheet — say the number you already run, this page doesn't size a tip and never will.",
        items: [
          { n: "Spray tips", sub: "EACH — SAY YOUR SIZE, THE NUMBER YOU ALREADY RUN", unit: "ea",
            notePlaceholder: "the tip numbers you run — yours, off your own sheet" },
          { n: "Gun filters", sub: "BY THE PACK — SAY THE MESH YOU RUN", unit: "pack",
            notePlaceholder: "the mesh you run, off the last pack" },
          { n: "Pump / manifold filters", sub: "EACH — SAY THE RIG THEY FIT", unit: "ea" },
          { n: "Strainer bags — for the fives", sub: "BY THE BAG — ANY CAN THAT'S BEEN OPEN GETS STRAINED", unit: "bag" },
          { n: "Cone strainers", sub: "BY THE BOX", unit: "box" },
          { n: "Throat seal / pump armor", sub: "BY THE BOTTLE", unit: "ea" },
          { n: "Airless hose / whip", sub: "BY THE LENGTH — SAY WHAT IT'S GOT TO REACH", unit: "ea" },
          { n: "Gun / tip guard spares", sub: "EACH — SAY WHICH GUN IN THE NOTE", unit: "ea" }
        ]
      },

      {
        id: "clean",
        name: "Cleanup, rags & site",
        docName: "Cleanup, rags & site",
        hint: "Rags like they're free, because the day you ration rags the job starts showing it.",
        items: [
          { n: "Rags", sub: "BY THE CASE", unit: "case" },
          { n: "Mineral spirits / thinner", sub: "BY THE CAN — FOR CLEANUP, SAY THE SIZE", unit: "ea" },
          { n: "Denatured alcohol", sub: "BY THE CAN", unit: "ea" },
          { n: "Trash bags — contractor", sub: "BY THE BOX", unit: "box" },
          { n: "Gloves", sub: "BY THE BOX — SAY THE SIZES YOUR CREW ACTUALLY WEARS", unit: "box" },
          { n: "Suits / coveralls", sub: "EACH — SAY SIZES, FOR SPRAY DAYS", unit: "ea" },
          { n: "Booties", sub: "BY THE BOX — FOR THE OCCUPIED SIDE", unit: "box" },
          { n: "Razor blades / scraper blades", sub: "BY THE BOX — FRESH BLADES, THE GLASS PAYS FOR TIRED ONES", unit: "box" },
          { n: "WET PAINT signs & caution tape", sub: "BY THE EACH / THE ROLL — THE SIGN IS CHEAPER THAN THE HANDPRINT", unit: "ea" }
        ]
      }
    ],

    /* A write-in is his sentence. It carries no axes — the sentence already
       says the sheen if the sheen matters — and both flags, because only he
       knows whether the line he typed dies at the shaker or has to match. */
    writeinAx: [],
    writeinFlags: [
      { k: "tint", label: "Gets tinted" },
      { k: "batch", label: "Same batch — has to match what's up" }
    ]
  };
})();

/* ── NOT READY (shape #2 — shared/note.js) — THE PINNED TOOL ────────────────
 * The receiver behind the gate ten of thirteen kits count down to. Sent from
 * the doorway BEFORE the crew sets up, because the trade's own law is that
 * commencement is acceptance: the first coat converts every other trade's
 * defect into the painter's defect, forever. Every entry is a CONDITION he
 * picks, in his words — never a verdict on anybody's work, never a reading
 * this page supplied, and never the word "failed". The closing is the
 * two-button ask: FIX it and tell me when, or tell me in writing to PROCEED
 * over it as-is — and it gets coated, noted.
 */
window.TOOLKIT_ITEMS.notready = {
  roles: [
    "GC superintendent",
    "GC project manager",
    "Our own boss / PM",
    "Builder's field super (tract or custom)",
    "Owner's rep / construction manager",
    "Homeowner",
    "Property / facility manager",
    "Another trade's foreman"
  ],
  /* WHAT STOPS PAINT. The first four are the ones all three panels wrote.
     Each sub is the ASK — what clears it — so the note reads as a list a
     super can action by lunch, not a complaint. */
  stops: [
    {
      name: "Mud's not done — or still soft",
      sub: "Tape, bed or skim still going, or the last coat's still dark. Tell me when the tapers are actually out and it's dry to sand."
    },
    {
      name: "Sanding's not done — ridges under a light",
      sub: "A raking light shows ridges, tool marks or fuzz. Whoever owns the sanding finishes it, or tell me in writing it's mine and it becomes a tag."
    },
    {
      name: "Another trade's still in the room",
      sub: "Bodies, ladders, cords or an active work front where my crew is supposed to roll. Tell me when they're out — 'they're almost done' starts the clock, it doesn't clear the room."
    },
    {
      name: "The room's a warehouse",
      sub: "Material stacked on my walls or filling my floor. It moves, or the rooms swap — say which."
    },
    {
      name: "Dings and gouges that aren't mine",
      sub: "Damage in the substrate before I ever opened a can — logged with photos. Whoever owns it fixes it, or direct me in writing and it becomes patch-and-charge."
    },
    {
      name: "Dust and debris nobody cleaned",
      sub: "Floors and ledges carrying dust that will end up in my finish. Broom-clean is the handoff — tell me when it's had one."
    },
    {
      name: "No heat, no air moving",
      sub: "The space has no heat or no air movement, as I found it. My product's own data sheet talks about conditions — I need the building holding what it needs, and I'll say what that is off my own sheet."
    },
    {
      name: "My meter reads over my own limit",
      sub: "My reading and my limit off my own product data, both written in the note with where each came from. I don't make the call alone — that's why both numbers go on the record."
    },
    {
      name: "No color or sheen answer for these areas",
      sub: "The schedule's silent, or somebody changed it verbally and nothing's in writing. Color Lock is sitting ready — confirm it and these rooms go back on the board."
    },
    {
      name: "Sequence is backwards",
      sub: "I'm being asked to finish ahead of trades that are still cutting, drilling or hanging. Tell me the sequence you actually want, and what happens to my finish if they come back through it."
    },
    {
      name: "Exterior — weather's on it",
      sub: "Rain, dew or a surface I can see is wet. When it's dry as my own data sheet talks about, we roll — that's a today call, not a schedule slip."
    },
    {
      name: "No light or power to work by",
      sub: "Temporary light or power is down in my rooms. Paint by phone-flashlight is how holidays happen — tell me when it's back."
    }
  ],
  pics: ["Sent with photos", "Photos on request", "Come look with me"]
};

/* ── COLOR LOCK (shape #2 — shared/note.js) ─────────────────────────────────
 * The day-before-the-gun confirmation. It ANSWERS the finish schedule's own
 * numbering — his dated copy, quoted — and never re-authors it. The impact
 * line is the tint: gallons are non-returnable the moment the shaker runs.
 */
window.TOOLKIT_ITEMS.colorlock = {
  whosaid: [
    "The approved finish schedule — I'm confirming before I tint",
    "Designer, on site",
    "Architect's rep",
    "Owner / owner's rep",
    "GC super, relaying somebody",
    "Tenant / homeowner",
    "A voicemail I'm not tinting off of"
  ],
  surfaces: [
    { name: "Walls" },
    { name: "Ceilings" },
    { name: "Doors & frames" },
    { name: "Trim & base" },
    { name: "Accent / feature" },
    { name: "Exterior — body" },
    { name: "Exterior — trim" },
    { name: "Rails / metals" }
  ]
};

/* ── COAT COUNT (shape #3 — shared/rowlog.js) ───────────────────────────────
 * The 3:30 production diary that is also the March-callback defense. The
 * ladder is FACTS about the wall — which coat is on it — never a verdict:
 * there is no "done", no "approved", no "ready" on this ladder or anywhere
 * else on the page. Batch numbers ride per area because that pair IS the
 * future touch-up, and the empties with the numbers on them leave in the
 * dumpster.
 */
window.TOOLKIT_ITEMS.coatcount = {
  surfaces: [
    "Walls",
    "Ceiling",
    "Doors & frames",
    "Trim & base",
    "Accent / feature",
    "Exterior — body",
    "Exterior — trim",
    "Rails / metals",
    "Floor / deck coating"
  ],
  /* The one-way ladder of facts a wall walks up. "Touched up" is last because
     it happens after final, and it is a fact about the wall, not a verdict on
     the touch-up. */
  coats: ["Spot-primed", "Primed", "1st coat", "2nd coat", "Final", "Touched up"]
};

/* ── THE DING LEDGER (shape #3 — shared/rowlog.js) ──────────────────────────
 * The last-trade tax, made billable. Every mark found after final coat is a
 * row with a date — because without the date, every mark in the building is
 * a painting punch item. WHO is recorded as what was OBSERVED in the room,
 * never as an accusation: "their scaffold was in it" is a fact, "they did it"
 * is an argument, and Unknown is an honest answer. Tallies are counts and
 * hours, never dollars — the office owns the number.
 */
window.TOOLKIT_ITEMS.ding = {
  kinds: [
    "Scuff / rub",
    "Gouge / dig",
    "Corner bead hit",
    "Door or frame edge chewed",
    "Tape pulled my finish",
    "Overspray / splatter — not ours",
    "Texture / mud repair through my finish",
    "Silicone or adhesive on finish",
    "Anchor / screw holes after final",
    "Water stain",
    "Scorch / burn",
    "Handprints / boot marks"
  ],
  /* What was IN the room when it was found — observed, not accused. The list
     is the trades that work after or over finish paint, plus the honest one. */
  seen: [
    "Unknown — found it",
    "Flooring / base in it",
    "Doors & hardware in it",
    "Electrical trim-out in it",
    "Plumbing trim-out in it",
    "HVAC trim / grilles in it",
    "Fire sprinkler trim in it",
    "Low-voltage / security in it",
    "Casework / millwork in it",
    "Appliance / equipment set in it",
    "GC's own labor in it",
    "Movers / owner's vendor in it",
    "Occupied — public traffic"
  ],
  /* The repair CALL is factual — what it takes, not whose fault: a touch-up
     that flashes is a whole wall, and saying so up front is the craft. */
  fixes: ["Touch-up", "Whole wall — it'll flash", "Prime + repaint", "Not called yet"],
  /* The one-rung-at-a-time lifecycle: logged (blank) → sent → repaired. */
  states: ["Sent", "Repaired"]
};

/* ── BEFORE PAINT (shape #3 — the cross-boundary ask) ──────────────────────
 * The fourteenth vocabulary on the one widget the INTERFACE MATRIX found:
 * ten kits write "before paint" into their own gate ladders, and this is the
 * painter standing behind the words — the ask he sends a week out so the
 * doorway refusal (not-ready.html, the morning-of note) never has to be sent.
 * Keep that line bright: not-ready is AT the door, this page is AHEAD of it.
 *
 * Panel-cut 2026-08-24 (C3654): two in-trade lenses (occupied repaint · new
 * construction) + the receiving desk, merged by a skeptic holding trade.js's
 * refusal list. The refusal survives here: no finish level, no prep grade, no
 * film/dry/cure number, and nothing that reads as "surface was ready" — the
 * smooth-wall level stays a number on THEIR sheet, named, never stated. */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before Paint",
  eyebrow: "Painting · you → everybody who owes you a wall",
  lede: "Every surface in the building is somebody else's work until your primer hits it — after that it's yours. This is everything that has to be sanded, cleared, lit, running and decided before a can gets opened: who owes it, which rooms, and the gate it has to beat. Walk the floor once, tap the rows, send one message per outfit — a week out, while every line is still a conversation. The morning-of refusal at the door is Not Ready's job; this page is what keeps you off it.",
  docSubject: "Before paint — what I need out of your outfit",
  docSubjectWith: "Before paint — what I need from {to}",
  closing: "That's my list before a can gets opened up there. If a line's wrong, or there's something in those rooms you know that I don't, hit me back today — every one of these is a five-minute answer this week and somebody's whole morning the week my crew is masked up in it. And the part nobody likes said out loud: primer buries whatever's still wrong under it, and from that morning it stops being yours and starts being mine. That's why I'm asking now.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set and <i>your</i> own approved submittals. This page sets no film build, no dry or recoat time, no temperature or moisture number, no finish level, no prep grade and no product data, and it never says a surface is ready &mdash; your spec, your data sheets and whoever inspects own all of that. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The finish schedule and its rev is the whole argument. Name the sheet you took this off and the super works your list against his own set; leave it off and it's one painter's opinion until he re-walks it with you — the morning you were supposed to be spraying.",
  phJob: "Alder Creek Medical — 3rd floor TI",
  phOff: "A-601 finish schedule rev 3",
  phFrom: "Sal M — Madrigal Painting Co",
  phArea: "3rd floor — rooms 301 to 318 and both corridors",
  areaLabel: "Room / area",

  who: [
    { v: "gc", label: "GC super" },
    { v: "tape", label: "Drywall / tapers" },
    { v: "mech", label: "Mech / HVAC" },
    { v: "ec", label: "EC foreman" },
    { v: "plumb", label: "Plumber" },
    { v: "fire", label: "Fire sprinkler" },
    { v: "doors", label: "Doors / millwork" },
    { v: "grid", label: "Ceilings / grid" },
    { v: "floor", label: "Flooring" },
    { v: "owner", label: "Owner / property manager" },
    { v: "clean", label: "Final clean" }
  ],

  /* HIS ladder, not the GC's. It starts where tint becomes irreversible
     ("the shaker only turns one direction") and ends at the walk. The answer
     page reuses these words as its when-buttons, so the ladder is the pair's
     shared vocabulary — one list, two pages. */
  milestones: [
    { v: "order", label: "Before the shaker runs" },
    { v: "mask", label: "Before we mask" },
    { v: "prime", label: "Before primer" },
    { v: "finish", label: "Before finish coats" },
    { v: "enamel", label: "Before the enamel" },
    { v: "final", label: "Before final coat" },
    { v: "touchup", label: "Before touch-up" },
    { v: "walk", label: "Before the walk" }
  ],

  asks: [
    { v: "sched", label: "The finish schedule, confirmed at its rev", who: "gc", by: "order", specs: [
      "Confirm the schedule and the revision before anything tints — the shaker only turns one direction, and a corridor off a superseded sheet is the most expensive kind of nobody's-fault.",
      "Anywhere the sheet is silent — accent walls, closet interiors, rail metals, the elevator returns — I need an answer on paper, not in a hallway. A verbal color gets written down and confirmed before tint; that's what my Color Lock note is for.",
      "Sheen reads like color on a big wall. If anybody has been promised a different sheen anywhere, I want the sheet changed before finish coats, not a punch line after them.",
      "Tell me who has the last word when the designer and the schedule disagree — one name. I tint to paper, not to a phone call."
    ] },
    { v: "walls", label: "The walls I'm coating over", who: "tape", by: "prime", specs: [
      "Tape, bed and skim done, sanded, and the dust knocked down — tell me the day the tapers are actually out of my rooms, because 'they're just doing closets' means they're not out.",
      "Walk it with me under a raking light before I prime — a ridge your light finds this week is a sander; the same ridge under my finish coat is a repaint.",
      "If the schedule calls a smooth-wall level anywhere — it's got a number on your sheet, not mine — show me which walls, because who sands last changes and I'm not guessing at it.",
      "Some of it will read after primer anyway: pops, ridges, fuzzed tape. Tell me today who comes back for point-up and how fast, because my finish coats sit parked behind that man.",
      "If the last skim's still dark, say so and the room slides a day — that's cheaper than primer over soft mud, which is a callback with both our names on it."
    ] },
    { v: "clear", label: "The room clear, and the day it's clear", who: "gc", by: "mask", specs: [
      "Out means out — no stock leaning on my walls, no lift parked in the middle, nobody working overhead while my crew masks below. A half-clear room gets painted twice and paid once, and I've stopped doing that.",
      "Give me the actual day and I'll hold crew for it. Give me a maybe and they're on another job, and getting a paint crew back mid-swing is a week, not a phone call.",
      "Walk it with me before we mask. Anything already busted in a wall gets a name on it that isn't mine — after primer nobody can see whose it was.",
      "Broom-clean is the handoff — rolling over a floor of drywall dust puts that dust up the pole and into my wet film. Tell me whose broom, because it shouldn't be a brush hand's.",
      "If it slides, tell me the day before, not the morning of — the morning-of version of this conversation is a Not Ready note sent from the doorway, and nobody enjoys those."
    ] },
    { v: "light", label: "Light to cut a line by, power to run a rig", who: "ec", by: "prime", specs: [
      "Temporary light in every room I coat — I cut lines by what I can see, and a wall cut in by droplight gets judged by daylight. If the temps come down before my final, tell me what replaces them.",
      "Power that holds when the rig kicks — tell me which circuit is mine and I'll stay off the rest. A breaker that trips mid-wall leaves a lap I have to chase, and that's both of us working late.",
      "Plates, covers, thermostats and devices — tell me what comes off and whose hands take it off, because I don't unscrew another man's device and I'm not the one who puts it back. Anything trimmed early gets cut around, and cut-around always looks like cut-around.",
      "If cans and fixtures hang before ceilings get sprayed, somebody bags them — tell me who bags and who wipes, because overspray on a new fixture is an argument I'd rather schedule than have."
    ] },
    { v: "air", label: "The building running, so film can cure", who: "mech", by: "prime", specs: [
      "Tell me the day the permanent system is on and holding. My data sheet talks about conditions and I work to my sheet — but no sheet on earth fixes a shell that goes cold all night, and film that goes on in one does what cold film does.",
      "Temp heat that dies at four is not the building running. If that's what we've got, say so in writing and I'll put on the record what my own sheet needs next to what the space is actually doing.",
      "Air moving matters as much as heat — dead air dries slow and shows every lap. Tell me what runs while we coat, what shuts down overnight, and who I call when the floor feels different on Monday.",
      "If the system runs while I spray, your returns and filters are in the conversation — tell me who's protecting them, because overspray through an air handler is a conversation nobody wants to own.",
      "Weekends: tell me who's watching it, because a system that trips Friday night costs me Monday's coat."
    ] },
    { v: "dust", label: "Nobody cuts on my finish days", who: "gc", by: "finish", specs: [
      "The day a room gets finish coat, nobody grinds, saws or sands anywhere the air reaches it — dust rides the air into wet film and the wall comes out gritty, and gritty means sand it and coat it again.",
      "Fireproofing patch, insulation blowing and slab grinding on my floor get scheduled around my coat days — tell me their weeks and I'll build mine, but one of us has to say it out loud first.",
      "Tack-and-sweep ahead of finish coats is somebody's scope — name whose, and when. My crew can do it, but that's a decision we make this week, not one you discover later.",
      "If a trade has to cut in a finished room, they tell me before the saw spins — a drop and a vacuum is five minutes ahead of time, and a repaint after."
    ] },
    { v: "doors", label: "Doors — hung, flat, and when hardware lands", who: "doors", by: "enamel", specs: [
      "Hung or laid flat? Spraying slabs flat in an empty room is one kind of day; brushing them hung in the opening is three. Tell me which I'm getting and the day the last one lands.",
      "Hardware goes on after enamel — locksets hung early get masked, masked hardware gets argued about, and the argument outlives the job. If prefit forces it, tell me now.",
      "Prefinished doors change my count to frames-only — say so before I order, not when the first slab shows up already sealed.",
      "Hinge-side chew the week after doors swing isn't mine — every mark after final goes in my dated ledger with a photo, so tell your hangers the frames are finished the day they start swinging metal."
    ] },
    { v: "caulk", label: "Who caulks what — before it's argued at the walk", who: "gc", by: "enamel", specs: [
      "Somebody owns the paintable caulk at trim, base and frames, and somebody owns the wet-area silicone — name both, because 'the painter caulks' and 'the carpenter caulks' are both true on every job until the gap shows at the walk.",
      "Silicone anywhere paint has to land is a stop — paint won't hold on it and I won't chase it. If another outfit already ran a bead ahead of me, I need who and with what, in writing, off their own tube.",
      "Nail holes and pin holes in trim: filled by whoever shot them or filled by me — either answer works, but it's a different week and a different count, so pick one now."
    ] },
    { v: "spray", label: "Spray days — the floor is mine", who: "gc", by: "prime", specs: [
      "A spray day is a closed floor: my crew only, because the fog goes everywhere the air goes and everything that can't leave gets covered. Put the window on your schedule as a closed floor, not as 'painters up there somewhere.'",
      "Cords, boxes and tools left in my rooms get covered over or carried out — masking around a gang box is how a gang box turns the ceiling color.",
      "Sprinkler heads and detectors get protected while I spray and stripped the same day — tell me who on your side checks behind me before the floor opens, because that check is worth two people, and tell the fire guys it's happening.",
      "Give me the truth about who else needs the floor that day — one man walking through wet fog ruins his jacket and my day, and the story gets told for a year."
    ] },
    { v: "after", label: "After final, the room changes owners", who: "gc", by: "touchup", specs: [
      "The morning my final coat dries, every ladder, cart, glove and door swing on this floor is on finished work — say that in your meeting, out loud, the day it happens.",
      "Corner protection in corridors while trim-out runs is somebody's scope — name it, because bare outside corners in a hallway full of carts is a repaint by Friday and a mystery by Monday.",
      "I keep a dated ding ledger from final coat on — every mark, photo, room, and what was in it when I found it. The trades that don't want to be in it should hear it exists before they're in it.",
      "Tell me who calls a floor done taking damage, because touch-up happens once — after the last cart leaves, not after each trade in turn."
    ] },
    { v: "walk", label: "One touch-up, one list, one walk", who: "gc", by: "walk", specs: [
      "One touch-up pass per floor, off one list, after trim-out is out — piecemeal 'hit this while you're here' burns a crew and closes nothing, and I'll keep answering it with dates instead of drive-bys.",
      "Touch-up comes out of the batch already on the wall — that's why my coat diary carries batch numbers by area. Where a batch is gone, a dab will flash and the honest fix is corner to corner, and I'll say so before the roller does.",
      "Walk it in the light the space will actually live in — a flashlight held flat finds texture on the moon, and that's not the standard either of our contracts names.",
      "Give me the walk date early and hold it — touch-up and the walk are the last two dates my crew's week hangs on, and when they move, my next job hears about it."
    ] }
  ]
};

/* ── WALK BACK (shape #3 — the RETURN LEG) ─────────────────────────────────
 * PAINT IS WHAT A WALK SEES, so every blue-tape list lands on the painter —
 * including the lines that aren't paint. The two answers he always needs and
 * never gets to give cleanly: "that's another trade's work wearing my color"
 * and "that mark landed after my final coat — it's in the ding ledger with a
 * date, and it isn't a punch item." Their line text and their numbers ride
 * back verbatim, because their system owns the list and closes it.
 *
 * answers[] is POSITIONAL (the engine reads positions, never words):
 * [0] the promise that wants a day on it · [1] settled · [2] declined —
 * not this trade's to fix · [3] blocked on their side (clear the room and it
 * moves). The tap-note and the no-date nag in answer-back.html are baked
 * prose and MUST say these same words — tools/toolkit-gates/answer-tapnote.mjs
 * asserts the pair, because flooring shipped eleven days of buttons its own
 * lede contradicted. */
window.TOOLKIT_ANSWER = {
  toolName: "Walk Back",
  eyebrow: "Painting · them → you → back",
  lede: "The super, the designer or the property manager walked it and sent you a list. Paste the whole thing and go down it once — tap each line through the four answers: We'll hit it, with a day on it · Done already · Not paint · Need the room — then send back one message they can close items from, in their order, under their own numbers. Their words ride back exactly as they wrote them.",
  docSubject: "your walk, answered",
  closing: "That's every line on your list, answered in your order with your numbers, so it closes clean on your side. Every We'll hit it line carries a day — hold me to it, and they land together on the touch-up pass, not one drive-by at a time. Done already lines are just that — walk them tonight. Not paint isn't ducking: it's another trade's work wearing my color, or a mark that landed after my final coat — those already sit in my ding ledger with a date and a photo, and that page comes to you separately, dates and counts, not punch items. Need the room lines move the day you clear the room — name the day and they come off both our lists. One more worth your minute: fresh touch-up reads different under morning light than under a work lamp. Look in daylight before you call one back.",
  answers: ["We'll hit it", "Done already", "Not paint", "Need the room"],
  phJob: "Alder Creek Medical — 3rd floor TI",
  phTo: "Dana K — GC super",
  phFrom: "Sal M — Madrigal Painting Co",
  phOff: "blue-tape walk 8/21",
  paste: "Alder Creek Medical 3rd floor — paint blue-tape — Aug 21\n\nJob: Alder Creek Medical — 3rd floor TI\nFrom: Dana K — GC super\n\n18. Rm 304 — roller marks on the accent wall by the window\n19. Rm 306 — cut line wavy at the ceiling, north wall\n20. Corr 3C — scuffs both sides by the elevator, cart height\n21. Rm 309 — gouge in the drywall behind the door stop\n22. Rm 311 — enamel missed the top edge of the closet door\n23. Rm 312 — accent wall reads a different sheen than the sample\n24. Rm 315 — paint on the sprinkler escutcheon at the door\n25. Rm 318 — furniture in, walls behind the desks not reachable"
};

/* ── GETTING IN (shape #2 — the INTERFACE rung) ────────────────────────────
 * The same page as the other thirteen kits and the only tool in the program
 * aimed at a party that is not another trade. THE HEADS-UP TICKS ARE NOT
 * DISCLOSURES, THEY ARE HANDBACKS: every one ends in a question aimed back at
 * the man who owns the process. A later cycle that rewrites one into a status
 * ("panel on test arranged", "tenants notified") is writing the defect this
 * page was designed around, not tidying it up.
 *
 * This trade's version is not a reskin. Repaint lives at night in buildings
 * that are full all day — the two asks nobody else on the rack has to make
 * are the SMELL (it rides the return air and meets the eight o'clocks) and
 * SPRAY FOG (a fine mist at the ceiling where the smoke heads live). Both
 * hand the building its own moves by name and claim none of them. */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Painting · you → whoever holds the keys",
  lede: "Night and weekend work in a building somebody else runs — they hold the keys, the alarm, the freight lift, and the phone that rings when a tenant smells paint at eight on Monday. Send the ask that gets a real yes before the van is loaded: the door and the hours, who meets you, where wash-up water goes, what goes on test and whose hands put it there. Every heads-up on it ends by handing the process back to the man who owns it — in his building, you don't own any of it.",
  docName: "ACCESS REQUEST",

  run: [
    { v: "Just that night" },
    { v: "A few nights running" },
    { v: "Weekends only" },
    { v: "Every night till it's painted — I'll flag changes" }
  ],

  need: [
    { name: "The door unlocked and somebody to meet us the first night", sub: "walk us in once — door, lights, freight, panel — and after that we're repeatable" },
    { name: "The night desk holding our names", sub: "crew list and company at the desk before the first shift, checked against the men who show — and tell me what changes on your end if a man swaps out mid-week" },
    { name: "Badges or keys for the run", sub: "for the names below — and say how you want them back at the end" },
    { name: "Us off the alarm for the window", sub: "or the code and the arm-up drill when we leave — and tell me who arms it back, because it won't be us" },
    { name: "The freight lift on service, with pads", sub: "pails, ladders and the rig cart ride it all night — who holds the key, and the name that answers if it faults at 2am" },
    { name: "The route in, walked once", sub: "ladders and planks don't turn every corner — show us the way you want us using and what gets covered along it" },
    { name: "Somewhere the van sits all night", sub: "close enough to carry fives from, and whatever placard keeps it from being tagged or towed while we're upstairs" },
    { name: "Lights and air on our floor, on our hours", sub: "timers and setbacks are yours — tell us who overrides them at night, because the switch on the wall usually isn't it" },
    { name: "A slop sink or washout you're okay with", sub: "rollers and guns wash out every night — say where wash-up water goes and where it never goes; we don't guess in your building" },
    { name: "A room that locks for paint and gear between nights", sub: "one that holds heat, out of tenant sight — gallons that freeze overnight are gone, and ladders in a corridor at nine is your phone ringing" },
    { name: "The restroom you want a night crew using", sub: "name it and we're in no other" },
    { name: "Where empties, stripped masking and trash go", sub: "your dumpster or our haul-off — say which; it fills faster than anybody expects" },
    { name: "Our COI to the right desk before night one", sub: "who gets it and the exact additional-insured wording you want — the paper has to beat the crew to the desk, or the desk turns the crew around" },
    { name: "The way back out at end of shift", sub: "the door we leave by and how it locks behind the last man — nobody wants a propped door with our name on it" }
  ],

  heads: [
    { name: "You will smell us — low-odor is never no-odor", sub: "it rides the return air and meets the eight o'clocks — tell me which tenants get warned, who warns them, the hour you want us capped and gone, and what you want us saying to anyone who catches us in the hall" },
    { name: "Spray fog reads as smoke", sub: "the nights we spray, a fine mist hangs at the ceiling where your smoke heads live — the panel on test, a head bagged and unbagged are your building's moves, not ours. Tell me who makes them, when it all comes back live, and who I call if a head trips anyway" },
    { name: "We don't paint sprinkler heads and we don't hang plastic from pipe", sub: "if a head or escutcheon needs a guard while we spray, tell me whose hands put it on and take it off — and who gets the call the second anything on a sprinkler line takes a knock, because that phone call beats a flooded suite by hours" },
    { name: "The rig and the air movers run on your power", sub: "tell me which circuits you want us on and who resets a breaker at midnight — we don't go hunting in your electrical rooms" },
    { name: "We may need more air, or less", sub: "spraying wants exhaust, drying wants movement, and the system is yours — tell me who makes that change at night, and what I do if the floor goes dead still at midnight" },
    { name: "Walls stay wet after we leave", sub: "wet-paint signs and a tape line where your people walk at six — tell me where you want them, who warns the morning cleaners, and who says when the signs come down" },
    { name: "Sanding and the compressor carry through a slab", sub: "tell me the hours noise is okay, which neighbors count, and who fields the first complaint so it isn't a surprise to either of us" },
    { name: "Ladders, planks and hose in your corridors", sub: "exits and paths stay open — tell me any door that can never be blocked, and who looks at our layout if your building wants eyes on it" },
    { name: "We move nothing that belongs to a tenant", sub: "pictures, shelves, coat hooks — down before we arrive or that wall doesn't get painted. Tell me who takes them down and who puts them back" },
    { name: "Old, peeling layers in an older building stop us", sub: "the testing and the call on old paint belong to certified people — tell me who you'd call and what the building already knows, because it isn't us" },
    { name: "If your building papers after-hours work", sub: "permit, work order, engineer's sign-off, whatever your house runs on — tell me who pulls it and what you need from us to move it" },
    { name: "If something goes wrong at 2am", sub: "a leak we find, a door that won't lock, somebody on the floor who shouldn't be — give me the one number you want called first" }
  ],

  phSite: "The Aldrich Building — floors 5 and 6",
  phRoom: "corridors, elevator lobbies and stair doors, 5 and 6",
  phHow: "loading dock off Pell Alley, freight to 5",
  phScope: "repaint corridor walls, doors and frames — three of us, rollers and brushes, one small airless for the lobbies, pails and ladders in on carts, four nights",
  phLoud: "sanding the first two nights after nine, the sprayer in the lobbies Friday night",
  phTo: "Mara S — building manager, the Aldrich",
  phMe: "Sal M — 559-555-0173",
  phCo: "Madrigal Painting Co",

  closing: [
    "This is an ask, not a booking — nothing loads until you answer. Wrong nights? Name the ones your building can live with and we'll take them.",
    "Saying yes: tell me the window you're actually giving us, the door, who meets us the first night, where material sits between nights, and where wash-up water goes — and if the answer on the alarm or the smoke heads is a person, give me their name before our first night, not during it."
  ],

  warn: "<b>It's an ask, not a booking.</b> This page has no channel back &mdash; it puts text on your clipboard and that is all it does. Nothing on it is a permit, a reservation or an approval, and every heads-up on it ends by handing the process back to whoever owns it &mdash; the panel, the alarm, the air and the word to the tenants are the building's to run and to number, and we never will."
};

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Everything here is something the man PICKS,
 * and every `notin` line is a fence that keeps a tag from being read as a claim.
 *
 * BACKPORTED 2026-09-05 (C3711). The census on disk said eleven of seventeen
 * trades carried the extra-work tag and this one did not — a trade with no tag
 * has no way to write the one document that gets it paid for directed work.
 * The engine and the nine-slot `notin` skeleton are the rack's; the words are
 * this trade's, and `why` is where the trade actually lives.
 *
 * THE FENCE THAT MATTERS MOST is in `why` and in `notin`: nothing here asserts
 * CAUSE. A tag that says who caused a condition is a tag doing the engineer's
 * job. He writes what he was told and what his crew did; who caused what is
 * somebody else's call. */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "GC superintendent",
    "Our own general super",
    "Another trade's foreman working in our area",
    "GC project manager",
    "Our PM or the office",
    "Builder's field super (tract or custom home)",
    "Architect or designer on a walk",
    "Owner's rep or property manager",
    "Homeowner",
    "Building engineer or facilities (occupied building)"
  ],
  "how": [
    { "v": "Face to face on the walk" },
    { "v": "Text message" },
    { "v": "Phone call" },
    { "v": "Told to me at the morning huddle" },
    { "v": "Radio on the site channel" },
    { "v": "Email" },
    { "v": "Marked-up finish schedule handed to me in the field" },
    { "v": "Punch item assigned to us in the app" },
    { "v": "Note or tape left on the wall" },
    { "v": "Written direction from our own office" }
  ],
  "why": [
    { "name": "Substrate wasn't ready and we were told to go", "sub": "Patch, texture, joints or bare spots still on the wall when we got there. Prepped past what we bid, or coated over it on somebody's say-so." },
    { "name": "Color changed after the mockup was approved", "sub": "New color, new sheen or a new product after we'd bought and cut in." },
    { "name": "Told to add coats", "sub": "Went back over it beyond the coats we carried, on somebody's say-so. How many, where, and who said so — the call on why is the office's and the maker's." },
    { "name": "Told to paint out of sequence", "sub": "Ahead of the finish trades, ahead of the flooring, or after the casework and fixtures were in and had to be cut around." },
    { "name": "Standing while another trade finished in our area", "sub": "Crew masked off and standing, rig and material in the room, waiting on it to be ours to work." },
    { "name": "Damage after we finished the room", "sub": "Finished and walked, then scuffed, hand-printed, booted at the base or tape-lifted before we ever handed it off." },
    { "name": "Touch-up that turned into a re-coat", "sub": "Spot work that wouldn't hold — flashing, burnished sheen or a color that wouldn't blend — so the wall or the run went whole." },
    { "name": "Told to work the conditions", "sub": "Spray or roll in heat, cold, damp or dust we'd have called off, or fans, heat and cover we put in and kept running." },
    { "name": "Masking and protection somebody else called for", "sub": "Paper, plastic, floor cover and barricade we put down, kept up and pulled on somebody's say-so." },
    { "name": "What we found wasn't what we bid", "sub": "Old coating, wallpaper, adhesive, rust or a surface that wouldn't take ours. Stripped, sealed or primed past the bid." },
    { "name": "Told to match something nobody could give us", "sub": "No color, no product and no record, so it went to draw-downs and site samples until somebody picked." },
    { "name": "Access changed after we set up", "sub": "Lift, scaffold, staging or a shutdown window moved after we'd planned the reach." },
    { "name": "Occupied-space rules added after we started", "sub": "Off-hours, low-odor product, containment or a smaller crew called for after we were mobilized." },
    { "name": "Told to coat what was never on the schedule", "sub": "Doors and frames, exposed deck and structure, mechanical, piping, handrails — \"while you're in there, shoot it.\" Not on the finish schedule we bid." },
    { "name": "Second trip to a room somebody re-opened", "sub": "Signed off, then cut into, patched or re-worked. Back to prime, cut and re-coat a room we had already finished." }
  ],
  "notin": [
    { "name": "Not a price", "sub": "Hours, counts and conditions only. No rate, no total, no dollar figure anywhere on it." },
    { "name": "Not a change order and not a claim", "sub": "This says we were directed and what it took. It becomes a change when the offices paper it, and entitlement is their letter, not the foreman's." },
    { "name": "Not a question for the architect, and not a spec change", "sub": "Anything about the product, the system or the coat count goes up through the GC on their form. Nothing here approves a substitution." },
    { "name": "Not the finish schedule or the product data sheet", "sub": "They own the color numbers, the product and the coat count. We attach them by what's already printed on them." },
    { "name": "Not a coverage or warranty opinion", "sub": "Whether a coating holds is the manufacturer's call and the office's letter. We write what we were told and what we put on." },
    { "name": "Not the inspector's report", "sub": "He writes his own. We write what our crew was told and what our crew did." },
    { "name": "Not the GC's daily", "sub": "They keep theirs and number it. This is ours and it stands on its own." },
    { "name": "Not a finding of cause", "sub": "We write what we found and what we coated. Who caused what is a call other people make." },
    { "name": "Not a safety or incident report", "sub": "Injuries, near misses and equipment go on their own paper, right then, through the proper channel." },
    { "name": "Not turnover or acceptance", "sub": "Signing that you were told isn't accepting the work, releasing anybody, or agreeing it's done." }
  ],
  "classes": [
    "— class",
    "JOURNEYMAN",
    "APPRENTICE",
    "FOREMAN",
    "SPRAY MAN",
    "PAPERHANGER"
  ],
  "pics": [
    { "v": "In this message — shot before we coated over it" },
    { "v": "None" }
  ]
};

/* ── TAG_ES — the directed-work tag's vocabulary en español. ──────────────
 * Every entry carries its own en-twin — nothing paired by index, nothing that can
 * drift apart. The page composes what the document prints ("ES (EN)") from the
 * pair; a <select> value carries its twin itself, house style "MAYORDOMO (FOREMAN)".
 * Gated: tools/toolkit-gates/lang-layer.mjs asserts every twin matches an EN
 * option verbatim, on every page that mounts shared/lang.js. */
window.TOOLKIT_ITEMS.tag_es = {
  "classes": [
    { "es": "— clase", "en": "— class" },
    { "es": "OFICIAL (JOURNEYMAN)", "en": "JOURNEYMAN" },
    { "es": "APRENDIZ (APPRENTICE)", "en": "APPRENTICE" },
    { "es": "MAYORDOMO (FOREMAN)", "en": "FOREMAN" },
    { "es": "PISTOLERO (SPRAY MAN)", "en": "SPRAY MAN" },
    { "es": "INSTALADOR DE TAPIZ (PAPERHANGER)", "en": "PAPERHANGER" }
  ],
  "how": [
    { "es": "En persona, en el recorrido", "en": "Face to face on the walk" },
    { "es": "Mensaje de texto", "en": "Text message" },
    { "es": "Llamada", "en": "Phone call" },
    { "es": "Me lo dijo en la junta de la mañana", "en": "Told to me at the morning huddle" },
    { "es": "Radio, en el canal de la obra", "en": "Radio on the site channel" },
    { "es": "Correo", "en": "Email" },
    { "es": "Schedule de acabados marcado que me entregó en campo", "en": "Marked-up finish schedule handed to me in the field" },
    { "es": "Punto de punch list asignado a nosotros en la app", "en": "Punch item assigned to us in the app" },
    { "es": "Nota o cinta dejada en la pared", "en": "Note or tape left on the wall" },
    { "es": "Orden por escrito de nuestra propia oficina", "en": "Written direction from our own office" }
  ],
  "notin": [
    { "es": "No es un precio", "sub": "Solo horas, cantidades y condiciones. Sin tarifa, sin total, sin ninguna cifra en dólares.", "en": "Not a price" },
    { "es": "No es un CO ni un reclamo", "sub": "Esto dice que nos ordenaron y qué tomó. Se vuelve cambio cuando las oficinas lo documentan, y el derecho a cobrarlo lo pone la carta de la oficina, no el mayordomo.", "en": "Not a change order and not a claim" },
    { "es": "No es pregunta para el arquitecto, ni cambio de especificación", "sub": "Todo lo del producto, el sistema o el número de manos sube por el GC en su formato. Nada de aquí aprueba una sustitución.", "en": "Not a question for the architect, and not a spec change" },
    { "es": "No es el schedule de acabados ni la ficha técnica del producto", "sub": "Ellos son los dueños de los números de color, del producto y del número de manos. Los anexamos por lo que ya traen impreso.", "en": "Not the finish schedule or the product data sheet" },
    { "es": "No es una opinión de cobertura ni de garantía", "sub": "Si una pintura aguanta lo dice el fabricante y la carta de la oficina. Nosotros escribimos qué nos ordenaron y qué aplicamos.", "en": "Not a coverage or warranty opinion" },
    { "es": "No es el reporte del inspector", "sub": "Él escribe el suyo. Nosotros escribimos qué le ordenaron a nuestra cuadrilla y qué hizo nuestra cuadrilla.", "en": "Not the inspector's report" },
    { "es": "No es el reporte diario del GC", "sub": "Ellos llevan el suyo y le ponen número. Este es el nuestro y se sostiene solo.", "en": "Not the GC's daily" },
    { "es": "No dice quién tuvo la culpa", "sub": "Escribimos lo que encontramos y lo que pintamos. Quién causó qué es decisión de otros.", "en": "Not a finding of cause" },
    { "es": "No es reporte de seguridad ni de incidente", "sub": "Lesiones, casi-accidentes y equipo van en su propio papel, en el momento, por el canal que corresponde.", "en": "Not a safety or incident report" },
    { "es": "No es entrega ni aceptación", "sub": "Firmar que se lo ordenaron no es aceptar el trabajo, liberar a nadie, ni decir que ya quedó.", "en": "Not turnover or acceptance" }
  ],
  "pics": [
    { "es": "En este mensaje — tomadas antes de pintar encima", "en": "In this message — shot before we coated over it" },
    { "es": "Ninguna", "en": "None" }
  ],
  "roles": [
    { "es": "El súper del GC", "en": "GC superintendent" },
    { "es": "Nuestro propio súper general", "en": "Our own general super" },
    { "es": "El mayordomo de otro oficio trabajando en nuestra área", "en": "Another trade's foreman working in our area" },
    { "es": "El PM del GC", "en": "GC project manager" },
    { "es": "Nuestro PM o la oficina", "en": "Our PM or the office" },
    { "es": "El súper de campo del constructor (fraccionamiento o casa a la medida)", "en": "Builder's field super (tract or custom home)" },
    { "es": "El arquitecto o el diseñador en un recorrido", "en": "Architect or designer on a walk" },
    { "es": "El representante del dueño o el administrador de la propiedad", "en": "Owner's rep or property manager" },
    { "es": "El dueño de la casa", "en": "Homeowner" },
    { "es": "El ingeniero del edificio o mantenimiento (edificio ocupado)", "en": "Building engineer or facilities (occupied building)" }
  ],
  "why": [
    { "es": "La superficie no estaba lista y nos dijeron que le entráramos", "sub": "Resane, textura, juntas o partes desnudas todavía en la pared cuando llegamos. Preparamos más allá de lo que cotizamos, o pintamos encima porque alguien lo dijo.", "en": "Substrate wasn't ready and we were told to go" },
    { "es": "El color cambió después de aprobar la muestra", "sub": "Color nuevo, brillo nuevo o producto nuevo después de que ya habíamos comprado y recortado.", "en": "Color changed after the mockup was approved" },
    { "es": "Nos dijeron que le diéramos más manos", "sub": "Le volvimos a dar más manos de las que traíamos, porque alguien lo dijo. Cuántas, dónde y quién lo dijo — el porqué lo dicen la oficina y el fabricante.", "en": "Told to add coats" },
    { "es": "Nos dijeron que pintáramos fuera de secuencia", "sub": "Antes de los oficios de acabado, antes del piso, o después de que ya estaban la carpintería y las luminarias y hubo que recortar alrededor.", "en": "Told to paint out of sequence" },
    { "es": "Parados mientras otro oficio terminaba en nuestra área", "sub": "Cuadrilla ya con todo tapado y parada, equipo y material en el cuarto, esperando a que fuera nuestro para trabajar.", "en": "Standing while another trade finished in our area" },
    { "es": "Daño después de que terminamos el cuarto", "sub": "Terminado y revisado, y luego lo rayaron, lo mancharon de manos, lo patearon en el rodapié o la cinta se llevó la pintura antes de que lo entregáramos.", "en": "Damage after we finished the room" },
    { "es": "Retoque que se volvió otra mano", "sub": "Trabajo por puntos que no aguantaba — se marcaba, se quemaba el brillo o el color no empataba — así que se fue la pared o el tramo completo.", "en": "Touch-up that turned into a re-coat" },
    { "es": "Nos dijeron que le entráramos con las condiciones", "sub": "Pistola o rodillo con calor, frío, humedad o polvo que habríamos cancelado, o ventiladores, calor y cubiertas que pusimos y mantuvimos corriendo.", "en": "Told to work the conditions" },
    { "es": "Enmascarado y protección que pidió alguien más", "sub": "Papel, plástico, cartón para el piso y barricada que pusimos, mantuvimos y quitamos porque alguien lo dijo.", "en": "Masking and protection somebody else called for" },
    { "es": "Lo que encontramos no era lo que cotizamos", "sub": "Pintura vieja, tapiz, pegamento, óxido o una superficie que no aceptaba la nuestra. Se removió, se selló o se le dio primer más allá de la cotización.", "en": "What we found wasn't what we bid" },
    { "es": "Nos dijeron que igualáramos algo que nadie nos pudo dar", "sub": "Sin color, sin producto y sin registro, así que se fue a drawdowns y pruebas en obra hasta que alguien escogió.", "en": "Told to match something nobody could give us" },
    { "es": "El acceso cambió después de que nos instalamos", "sub": "La canastilla, el andamio, el área de material o la ventana de cierre se movieron después de que ya habíamos planeado el alcance.", "en": "Access changed after we set up" },
    { "es": "Reglas de espacio ocupado agregadas después de empezar", "sub": "Horario fuera de turno, producto de bajo olor, confinamiento o una cuadrilla más chica que pidieron después de que ya estábamos movilizados.", "en": "Occupied-space rules added after we started" },
    { "es": "Nos dijeron que pintáramos lo que nunca estuvo en el schedule", "sub": "Puertas y marcos, losa y estructura expuesta, mecánico, tubería, barandales — \"ya que anda ahí, écheselo.\" No venía en el schedule de acabados que cotizamos.", "en": "Told to coat what was never on the schedule" },
    { "es": "Segundo viaje a un cuarto que alguien volvió a abrir", "sub": "Ya entregado, y luego lo cortaron, lo resanaron o lo rehicieron. Regresamos a dar primer, recortar y volver a pintar un cuarto que ya habíamos terminado.", "en": "Second trip to a room somebody re-opened" }
  ]
};

/* ── THE WET AREA NOTICE (shape #2 — shared/note.js) ────────────────────────
 * THE RUNG THIS FILE'S OWN REGISTRY CALLED "the strongest unbuilt rung in the
 * kit" FOR FOUR CYCLES. The 20-year prune kept it as the seventh tool and
 * stand-up shipped six, so it stood in tools.js as a written-down deferral —
 * which is the only reason it survived to be built instead of being rediscovered
 * as a gap.
 *
 * IT IS THE ONLY PAGE IN THIS KIT THAT POINTS OUT. Every other tool here is the
 * painter receiving — the room that is not ready, the punch list walked back,
 * the ding somebody else put in his finish. This one is the painter TELLING the
 * building something, and it is the one document a paint crew sends on an
 * occupied job and has never once written down.
 *
 * THE PRUNE FOLDED TWO PAGES INTO THIS ONE, and the merge is the design:
 * closed-for-spray and closed-while-wet are ONE closure with ONE receiver, and
 * the "recoat clock" is not a second page — it IS this notice's window lines.
 * Two pages would have been the same door twice.
 *
 * WHERE THE SECOND INSTANCE RULE LANDED. paving/lot-closed-tonight.html is the
 * same class one trade over — an area closed, a re-entry line, one receiver —
 * and it is already a CONFIG of shape #2's engine. So this is a config too, and
 * §THE THREE SHAPES' extract-at-two never fires: the engine came out at the
 * directed-work ticket in August and both closures are callers of it. What is
 * NOT shared is every word below, which is the whole point of that boundary.
 *
 * THE REFUSAL THAT DEFINES THE PAGE, and it is sharper here than anywhere else
 * in the kit. trade.js bans clock numbers (no dry-to-touch, dry-to-recoat, full
 * cure, pot life) and bans exposure numbers (no PEL, no respirator selection, no
 * ventilation rate). A wet-area notice is exactly where a lazy build would ship
 * both. So:
 *   · THE WINDOW IS THREE FREE-TEXT LINES, typed off HIS data sheet, in HIS
 *     words. The registry wrote the target sentence four cycles ago — "walls
 *     closed 2:40 · doors swing at 6 · nobody blue-tapes till Friday" — and
 *     that is a man stating what he is telling them, not a table. The moment
 *     any of the three became a picker with hours in it, this page would be a
 *     recoat schedule with our name on it.
 *   · NOTHING HERE SAYS THE AIR IS CLEAR. When a space can be breathed, what
 *     the ventilation has to do and what anybody wears are his safety plan's,
 *     his SDS's and the building's. The occupied-day lines below are therefore
 *     ASKS AIMED AT WHOEVER OWNS THE EQUIPMENT — the same rule getting-in.html
 *     already runs on the panel, the air and the alarm — never an instruction
 *     this page issues and never a duration it supplies.
 *   · AND NO RELEASE. "Touchable" and "workable" are scheduling statements he
 *     is making about his own finish. Neither is an occupancy call, and the
 *     page says so in the document itself, not only in the warn block.
 *
 * WHAT IT DELIBERATELY DOES NOT DUPLICATE: getting-in.html owns access, keys,
 * the lift, the washout and where paint sleeps between shifts, so no ask below
 * touches any of them; docs.js owns the delay NARRATIVE (`delay-notice`) and the
 * daily's clear-by line, which is the write-up you dictate later. This is the
 * two-minute send you write at the door, at the moment you close it.
 */
window.TOOLKIT_ITEMS.closure = {
  /* WHO HOLDS THE AREA once the tape goes up. "The building" is not a name and
     cannot answer at six in the morning. */
  roles: [
    "GC superintendent",
    "Building engineer",
    "Property manager",
    "Facilities / maintenance",
    "Owner's rep",
    "The tenant contact",
    "Our own boss / PM"
  ],

  /* WHAT PUT THE TAPE UP, the way he says it on the phone. Spray and wet are one
     list because they are one closure — the merged page the prune called for. */
  kinds: [
    "Spraying — walls and ceilings",
    "Spraying — doors, frames and trim",
    "Rolling and cutting — walls still wet",
    "Enamel — wet doors and frames",
    "Floor coating — wet floor, nobody on it",
    "Stain and lacquer — wet millwork",
    "Wallcovering — wet paste and seams"
  ],

  /* THE OCCUPIED-DAY ASKS. Every one is aimed at the man who owns the thing
     being asked about — nothing here directs anybody's equipment, and nothing
     here sets a time for it. Seven, and the ones that died are as load-bearing
     as the ones that lived: keys, the lift, the washout and where the rig sleeps
     are getting-in.html's job, and putting them here would be that page again. */
  asks: [
    { name: "Tell the people in this building — you, not me", sub: "a name and a time it went out; somebody walking a wet corridor at seven is not a thing I can fix with a sign" },
    { name: "The air handler for this area off while I'm in it — and back on when you say", sub: "whoever runs it runs it. Tell me who and when — I'm not touching your equipment and I'm not setting the times" },
    { name: "The intakes and returns in this area sealed", sub: "tell me who does it and when it comes off. If it's mine to do, say so in writing and I'll tell you exactly what I covered" },
    { name: "Clear the floor before I close it", sub: "carts, stock, somebody's ladder — whatever is still in there when I close it is in there wet until the window's up" },
    { name: "Nobody opens this door till I say", sub: "the signs and the tape are mine to hang; the door is yours to hold. A door swung into wet enamel at six is the whole run again" },
    { name: "Other trades out of this area for the window", sub: "tell me who's still scheduled in it — I'll work around them or you move them, but not both at five o'clock" },
    { name: "Who I call if it has to open early", sub: "a name and a number tonight, not a policy tomorrow. If you have to have it back, I'd rather move than find out" }
  ],

  /* WHAT IT COSTS IF SOMEBODY WALKS IT. Chips are a jog for the sentence he
     writes after them — the line this trade has always eaten in silence, because
     a footprint in a wet floor coating is not a touch-up and never was. */
  costs: [
    "the whole run goes again, not a touch-up",
    "my crew comes back off another job",
    "it's the full room, not the one wall",
    "the batch won't match by then",
    "the floor goes back on your schedule, not mine",
    "this pushes the turnover"
  ],

  pics: ["Sent with photos of the signs and tape", "Photos on request", "Walk it with me before it opens"]
};
