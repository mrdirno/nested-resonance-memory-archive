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
