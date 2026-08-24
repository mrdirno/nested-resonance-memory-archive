/* THE COMMONS — the gear list. Data only; commons/index.html is the surface.
 *
 * WHAT THIS IS NOT. It is not a shopping list, an affiliate feed, or a catalog.
 * There are no brands, no model numbers, no prices, no specs, and no ratings —
 * on purpose, and it is the only reason a list like this can be trusted. Every
 * "must-have tools" page on the internet is somebody's commission; this one names
 * the THING and lets a crew buy whatever their shop buys.
 *
 * THE PARTITION. `t: ["universal"]` means EVERY trade in the program genuinely
 * carries it — that is the whole thesis of a commons, and the bar is strict: a
 * site super does not bore studs, so spade bits and the jab saw are NOT universal
 * however many installers carry them. Everything else is tagged with the trades
 * that reach for it, and a tool three trades reach for is ONE row with three tags,
 * never three rows. (Glow rods came back from three separate trade lists under
 * three names; that is a shared tool, not three tools.)
 *
 * THE WHY LINE has to earn its place or the whole page is a listicle. It is
 * journeyman-to-apprentice: the reason this thing is in the bag, in the trade's
 * own words, under about fourteen. It may NOT state a spec, a size, a rating, a
 * price or a proportion as authoritative; may NOT say a step is required or
 * prescribe a procedure; and may NOT frame a tool as proof of a safe condition.
 * (A non-contact tester says "maybe hot" — it never says dead. The line that said
 * it did got cut by two independent reviewers, which is exactly why there are
 * reviewers.)
 *
 * PROVENANCE. Seeded 2026-08-07 by a fan-out — one pass per trade plus a universal
 * pass — then cut by three independent adversarial lenses: a journeyman rejecting
 * anything that reads like a listicle, a rails reviewer rejecting brands / specs /
 * safety-and-code claims / paperwork, and a placement reviewer enforcing the
 * partition above. 39 rejections across 74 candidates; the lenses also caught each
 * other (the journeyman's fix for lineman's pliers named a brand, which the rails
 * lens forbids, and its fixes for the universal list were specs the rails lens had
 * just rejected — so the CRITICISM was taken and the suggested wording was not).
 * The seed is the floor, not the ceiling: the field corrects it through the "add
 * gear" well on the page, and a correction from someone who does the work outranks
 * anything here.
 */
/* COMMONS_TRADES moved to commons.js when the tips surface landed — both
 * surfaces partition by the same trades, and keeping the list in ONE data file
 * is how framing shipped a toolkit on 2026-08-09 and never got a chip here. */

window.COMMONS_GEAR = [
  /* ---- the floor: all six trades, no exceptions ------------------------- */
  { id: "tape-measure", n: "Tape measure", t: ["universal"],
    w: "The hook is loose on purpose, so inside and outside both read true." },
  { id: "utility-knife", n: "Utility knife", t: ["universal"],
    w: "Opens boxes, scores drywall, strips jacket, trims foam. You'll grab it hourly." },
  { id: "multi-bit-driver", n: "Multi-bit screwdriver", t: ["universal"],
    w: "Bits and nut drivers in one handle. Kills the trip back downstairs." },
  /* NOT universal any more: trade #9 (creative) is a bag of camera, grip and
     audio, and none of these three ride in it. Left as "universal" they would
     have told a shooter the shared floor of this program includes a drill and a
     voltage tester, which is the exact lie the strict `universal` bar exists to
     prevent. Re-tagged to the eight construction trades rather than deleted. */
  { id: "drill-driver", n: "Cordless drill/driver", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    w: "Use the clutch and the side handle — a bit that catches will twist your wrist." },
  { id: "torpedo-level", n: "Torpedo level", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    w: "Nobody remembers your wiring. Everybody sees a crooked mount." },
  { id: "headlamp", n: "Headlamp", t: ["universal"],
    w: "Panels, ceilings, crawlspaces. Hands stay on the work instead of holding light." },
  { id: "ncvt", n: "Non-contact voltage tester", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    w: "Lights up beside an energized conductor. First pass only — it never proves dead." },
  { id: "dikes", n: "Diagonal cutters (dikes)", t: ["universal"],
    w: "Every install ends in trimming zip ties. Don't do it with a knife." },
  { id: "adjustable-wrench", n: "Adjustable wrench", t: ["universal"],
    w: "Pull toward the movable jaw and re-snug every bite, or you round the nut." },
  { id: "step-ladder", n: "Step ladder", t: ["universal"],
    w: "Fiberglass, because sooner or later you'll set it under a live panel." },
  { id: "extension-cord", n: "Extension cord", t: ["universal"],
    w: "A thin cord starves a saw motor. Bring the heavy one, and bring length." },
  { id: "marker", n: "Permanent marker", t: ["universal"],
    w: "Label both ends of every run. Unlabeled cable becomes somebody's whole afternoon." },

  /* ---- shared: more than one trade reaches for it, so it is ONE row ----- */
  { id: "jab-saw", n: "Jab saw (drywall saw)", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "framing"],
    w: "Cuts an access hole in drywall anywhere. No power, no cord." },
  { id: "spade-auger-bits", n: "Spade & auger bits", t: ["av", "plumbing", "electrical", "low-voltage"],
    w: "Somebody has to put the hole through the stud. Usually you." },
  { id: "glow-rods", n: "Glow rods (fish sticks)", t: ["av", "low-voltage", "electrical"],
    w: "Pushes a string above the grid so you lift two tiles instead of ten." },
  { id: "punch-down", n: "Impact punch-down tool", t: ["av", "low-voltage"],
    w: "Seats and trims the conductor in one hit. Hand-pushing buys you callbacks." },
  { id: "cable-tester", n: "Wiremap cable tester with remotes", t: ["av", "low-voltage"],
    w: "Prove the run before the ceiling closes, not after go-live." },
  { id: "coax-compression", n: "Coax compression tool & prep stripper", t: ["av", "low-voltage"],
    w: "Seats an end that will not back out behind a camera months later." },
  { id: "tubing-cutter", n: "Tubing cutter, full-size & close-quarters", t: ["plumbing", "hvac"],
    w: "A square cut is why the joint holds. The stubby one saves you inside a wall." },

  /* ---- AV ---------------------------------------------------------------- */
  { id: "test-pattern-gen", n: "Video test pattern generator", t: ["av"],
    w: "Settles it fast: bad source, bad cable or bad display." },
  { id: "cage-nut-tool", n: "Cage nut tool", t: ["av"],
    w: "Racks a full stack of gear without shredding your fingertips on the rails." },
  { id: "panel-lifters", n: "Panel suction cup lifters", t: ["av"],
    w: "Frameless glass gives you nothing to grab. Cups put handles on the panel." },
  { id: "usb-serial", n: "USB-to-serial console kit", t: ["av"],
    w: "Plenty of processors and DSPs on site still only take a serial console." },
  { id: "spl-meter", n: "SPL meter", t: ["av"],
    w: "Puts a number on the room when somebody says it's too loud." },
  { id: "hole-cutter", n: "Adjustable ceiling speaker hole cutter", t: ["av"],
    w: "Clean cut-ins for in-ceilings instead of butchering tile with a jab saw." },

  /* ---- plumbing ---------------------------------------------------------- */
  { id: "tongue-groove-pliers", n: "Tongue-and-groove pliers", t: ["plumbing"],
    w: "Traps, slip nuts, packing nuts. Carry two sizes and trim goes fast." },
  { id: "pipe-wrenches", n: "Pipe wrenches, matched pair", t: ["plumbing"],
    w: "Threaded steel doesn't budge until you back one wrench against the other." },
  { id: "basin-wrench", n: "Basin wrench", t: ["plumbing"],
    w: "The only thing that reaches the faucet nuts behind a mounted sink." },
  { id: "solder-torch", n: "Soldering torch kit", t: ["plumbing"],
    w: "Sweat a joint anywhere: torch, striker, flux and solder ride together." },
  { id: "press-tool", n: "Press tool with jaw set", t: ["plumbing"],
    w: "No flame, no draining the line. That's why it lives in the van." },
  { id: "pex-tool", n: "PEX crimp or cinch tool", t: ["plumbing"],
    w: "Whichever system your supply house stocks — and carry its go/no-go gauge." },
  { id: "closet-auger", n: "Closet auger", t: ["plumbing"],
    w: "Shaped for the toilet trap so you clear it without pulling the bowl." },
  { id: "drum-auger", n: "Hand drum auger", t: ["plumbing"],
    w: "Kitchen and lav stoppages you clear right at the trap arm, no machine." },
  { id: "pipe-dope", n: "Pipe dope & thread tape", t: ["plumbing"],
    w: "Sealant for tapered pipe threads. It rides in the bag with the fittings." },

  /* ---- electrical -------------------------------------------------------- */
  { id: "lineman-pliers", n: "Lineman's pliers", t: ["electrical"],
    w: "Cuts, twists, pulls. Your hand defaults to it." },
  { id: "wire-strippers", n: "Wire strippers", t: ["electrical"],
    w: "Nicked strands snap off in the box later. Strip clean, move on." },
  { id: "clamp-meter", n: "Clamp meter", t: ["electrical"],
    w: "Reads load current on a conductor without breaking a single connection." },
  { id: "fish-tape", n: "Fish tape", t: ["electrical"],
    w: "Gets a pull string through conduit when you can't see the far end." },
  { id: "conduit-bender", n: "Hand conduit bender", t: ["electrical"],
    w: "Offsets, 90s and saddles bent on the spot instead of waiting on fittings." },
  { id: "knockout-punch", n: "Knockout punch set", t: ["electrical"],
    w: "Clean round holes in panel steel where a hole saw just wanders." },
  { id: "mc-cutter", n: "Armored cable cutter", t: ["electrical"],
    w: "Cuts the spiral without a hacksaw chewing the conductors underneath." },
  { id: "circuit-tracer", n: "Circuit tracer", t: ["electrical"],
    w: "Finds the right breaker without shutting down half an occupied building." },

  /* ---- HVAC/R ------------------------------------------------------------ */
  { id: "manifold-gauges", n: "Manifold gauge set", t: ["hvac"],
    w: "Pressure reads back as saturation temperature — that's where superheat and subcooling come from." },
  { id: "vacuum-pump", n: "Vacuum pump", t: ["hvac"],
    w: "Moisture and air left in a system will kill the compressor." },
  { id: "micron-gauge", n: "Micron gauge", t: ["hvac"],
    w: "Gauges read empty long before a system is dry. This one doesn't lie." },
  { id: "charging-scale", n: "Refrigerant charging scale", t: ["hvac"],
    w: "Weigh the charge in. Topping off by feel is how callbacks start." },
  { id: "recovery-machine", n: "Refrigerant recovery machine", t: ["hvac"],
    w: "Pulls the existing charge into a cylinder before the system gets opened." },
  { id: "leak-detector", n: "Electronic leak detector", t: ["hvac"],
    w: "Finds in minutes the leak you'd chase all afternoon with bubbles." },
  { id: "nitrogen-reg", n: "Nitrogen regulator & tank", t: ["hvac"],
    w: "Puts dry nitrogen on the line at a pressure you set, instead of shop air." },
  { id: "brazing-torch", n: "Brazing torch kit", t: ["hvac"],
    w: "Refrigerant line gets brazed, not soldered — different filler, different heat." },
  { id: "valve-core-tool", n: "Valve core removal tool", t: ["hvac"],
    w: "Takes the cores out so the evacuation isn't breathing through the valve." },
  { id: "flaring-tool", n: "Flaring & swaging tool set", t: ["hvac"],
    w: "A clean flare is the difference between a sealed joint and a slow leak." },

  /* ---- low-voltage & fire ------------------------------------------------ */
  { id: "tone-probe", n: "Tone generator & probe", t: ["low-voltage"],
    w: "Traces the one cable you need out of a bundle of two hundred." },
  { id: "modular-crimper", n: "Modular crimper", t: ["low-voltage"],
    w: "Field-ends a plug when no factory patch cord will reach." },
  { id: "jacket-stripper", n: "Round-cable jacket stripper", t: ["low-voltage"],
    w: "Rings the jacket clean; a blade eventually nicks a conductor." },
  { id: "vfl", n: "Visual fault locator", t: ["low-voltage"],
    w: "Shows the break or the tight bend instead of guessing at splices." },
  { id: "test-pole", n: "Telescoping detector test pole", t: ["low-voltage"],
    w: "Reaches a head from the floor instead of dragging the ladder around." },
  { id: "test-magnet", n: "Detector test magnet", t: ["low-voltage"],
    w: "Actuates a detector's own built-in test point during a scheduled test." },

  /* ---- GC & site super --------------------------------------------------- */
  { id: "laser-distance", n: "Laser distance meter", t: ["gc"],
    w: "Dimension a whole floor alone, no helper holding the dumb end." },
  { id: "rotary-laser", n: "Rotary laser with receiver & grade rod", t: ["gc"],
    w: "Shoot your own elevations before the pour instead of trusting somebody's word." },
  { id: "open-reel-tape", n: "Open-reel long tape", t: ["gc"],
    w: "Control lines and building dimensions don't fit on a pocket tape." },
  { id: "measuring-wheel", n: "Measuring wheel", t: ["gc"],
    w: "Walk off trench, paving and fence runs faster than the argument takes." },
  { id: "box-level", n: "Box level", t: ["gc", "framing"],
    w: "Punch walls and door frames with something the finish trades can't argue." },
  { id: "moisture-meter", n: "Moisture meter", t: ["gc"],
    w: "Screens framing and board before finishes go on. On slab it's a heads-up only." },
  { id: "keel", n: "Lumber crayon (keel)", t: ["gc", "framing"],
    w: "Marks wet concrete, dirty steel and rough lumber where a marker quits." },
  /* ID RENAMED 2026-08-15, and it was a live defect on a shipped surface, found
     while standing up trade #11 and belonging to nobody. This row and "Marking
     paint" further down BOTH carried id "marking-paint", and both are visible to
     a GC. The engine keys picks by id (commons.js: `picks.push(g.id)`,
     `picked(g.id)`), so on the GC chip ticking either one rendered BOTH as
     checked, put BOTH in the bag document, and made it impossible to remove one
     without the other — and the search index maps by id too, so a query could
     route to the wrong object. They are two objects: this is the WAND, the other
     is the paint. Anybody who had the wand ticked will find the can ticked
     instead once, which is strictly better than a pick that cannot be undone. */
  { id: "marking-paint-wand", n: "Inverted marking paint wand", t: ["gc"],
    w: "Lays out and flags on dirt and slab so nobody claims surprise." },
  { id: "punch-tape", n: "Punch tape (blue painter's tape)", t: ["gc"],
    w: "Flags the defect where the trade finds it, no explanation needed." },
  { id: "two-way-radio", n: "Two-way radio", t: ["gc", "roofing"],
    /* "every foreman" was the super's word; a man on a deck who cannot see the
       ground needs this more than the super does. */
    w: "Reaches the crane, the hoist and the gate without waiting on bars." },

  /* ---- framing & drywall -------------------------------------------------
   * Added 2026-08-11. The trade shipped a full toolkit on 2026-08-09 and this
   * list was never told, so for two days a framer opened the page that calls
   * itself "every trade" and found seven chips, none of them his. The deploy
   * now refuses a toolkit with no chip and the ship gate refuses a chip with no
   * rows, because nothing about that failure was visible — no error, no 404,
   * just a trade quietly absent from the commons. */
  { id: "rafter-square", n: "Rafter square", t: ["framing"],
    w: "Squares a cut and steps out an angle without doing the math twice." },
  { id: "chalk-line", n: "Chalk line (chalk box)", t: ["framing", "roofing", "concrete"],
    /* Was "Snap blue — red is permanent…the painter's finish": an instruction, and
       BACKWARDS for the trade that snaps more line than any other. A roofer has no
       painter, and blue will not survive dew on an open deck. States the trade-off
       instead of prescribing one side of it. */
    w: "Permanent chalk comes back through whatever goes over it. That is the whole decision." },
  { id: "dry-line", n: "String line (dry line)", t: ["framing"],
    w: "A wall can read plumb at every stud and still be bowed. The line shows it." },
  { id: "aviation-snips", n: "Aviation snips, left, right & straight", t: ["framing", "roofing"],
    w: "Carry all three. The wrong pair curls the cut into your hand and burrs the edge." },
  { id: "stud-crimper", n: "Stud crimper", t: ["framing"],
    w: "Locks stud into track with nothing left proud on the flange for board to rock on." },
  { id: "powder-tool", n: "Powder-actuated fastening tool", t: ["framing"],
    w: "Puts track down on slab and deck. Dead weight without the right pins and the matching loads." },
  { id: "framing-hammer", n: "Framing hammer, milled face", t: ["framing"],
    w: "The milled face bites the head instead of skidding off it." },
  { id: "framing-nailer", n: "Framing nailer", t: ["framing"],
    w: "Wood goes together as fast as you can set the next piece." },
  { id: "screw-gun", n: "Drywall screw gun with depth nose", t: ["framing"],
    w: "The nose sets the dimple. A drill breaks the paper and the taper finds every one." },
  { id: "collated-gun", n: "Collated screw gun", t: ["framing"],
    w: "Hangs board standing up instead of one screw at a time out of a pouch." },
  { id: "drywall-tsquare", n: "Drywall T-square", t: ["framing"],
    w: "Scores a whole sheet in one pass. A cut that isn't square becomes the taper's problem." },
  { id: "cutout-router", n: "Drywall cut-out router", t: ["framing"],
    w: "Hang the sheet whole and find the box after — measuring every cut-out is how they land wrong." },
  { id: "foot-lift", n: "Drywall foot lift (board lifter)", t: ["framing"],
    w: "Levers the sheet tight to the one above, so the gap ends up down at the floor." },
  { id: "drywall-lift", n: "Drywall lift", t: ["framing"],
    w: "Holds a lid tight to the framing while you screw it. Beats two men and a cracked sheet." },
  { id: "drywall-rasp", n: "Drywall rasp", t: ["framing"],
    w: "Takes the last hair off a cut that won't drop in, instead of cutting a fresh sheet." },
  { id: "stilts", n: "Drywall stilts", t: ["framing"],
    w: "Walk the whole lid instead of moving a bench all day. The bench move is the time." },
  { id: "taping-knives", n: "Taping knives & mud pan", t: ["framing"],
    w: "Every coat goes on wider than the last, so you carry the set and not one favorite." },
  { id: "pole-sander", n: "Pole sander", t: ["framing"],
    w: "Reaches the ceiling and the top of the wall without dragging a bench around." },
  { id: "rake-light", n: "Work light on a stand", t: ["framing"],
    w: "Rake it across the wall and you find the ridges before the painter does." },
  { id: "locking-pliers", n: "Locking pliers", t: ["framing", "roofing"],
    w: "Holds two pieces of steel together while your other hand drives the screw." },

  /* ---- roofing ------------------------------------------------------------
     Added 2026-08-13, and later than framing's late. Roofing shipped a full
     toolkit on 2026-08-12 WITH a chip on this page and zero rows behind it, and
     four days later an unrelated commit widened three universal rows to the eight
     construction trades and swept it in — so the ship gate, which asks only for
     "more than zero rows of its own", went green on an accident. A roofer tapped
     his own chip and was told his trade's gear is a cordless drill, a torpedo
     level and a non-contact voltage tester. §SCARS 2026-08-13.

     BOTH HALVES, because `roofing/items.js` makes that an invariant: commercial
     low-slope (welder, probe, stand-up gun, ISO knife, cut saw, torch) and
     residential steep-slope (shovel, flat bar, hatchet, magnet), metal on both.
     The first seed came back commercial twice over — a bag with no hammer in it —
     and the journeyman lens caught it.

     WHAT THE LENSES KILLED, so nobody re-proposes it: the shingle ripper (a slate
     tool; on asphalt every man reaches for the flat bar he already carries), the
     core cutter (the consultant's test cut, not the crew's — and a row telling a
     crew to cut a hole in somebody's warranted roof is the wrong row), the seam
     roller as its own row (folded into the welder it never leaves), and two
     re-tags: keel, because a roofer marks with the chalk box and the paint can,
     and the moisture meter, which is the ncvt breach wearing a tag instead of a
     verb — "the meter says dry" is exactly the claim that leaves saturated board
     under a new roof. Everything the height rail took is listed in §SCARS: harness,
     jacks, ladder hooks, boots, the deck probe. Nothing on this page holds a man.

     THE HATCHET SHIPS WITHOUT ITS GAUGE. The gauge's whole value is an exposure,
     and this file prints no exposure. A row whose reason cannot be stated is not a
     row; a row whose reason must be stated as a number is somebody else's file. */
  { id: "tear-off-shovel", n: "Tear-off shovel (roofing spade)", t: ["roofing"],
    w: "The notches bring the nails up with the course. A square shovel leaves them." },
  { id: "flat-bar", n: "Flat bar", t: ["roofing"],
    w: "Pulls the nail the shovel walked past, and lifts a course to get under." },
  { id: "roofing-hatchet", n: "Roofing hatchet or hammer", t: ["roofing"],
    w: "Hammer, blade and nail puller on one handle. Your hand never leaves it." },
  { id: "hook-blades", n: "Hook blades", t: ["roofing"],
    w: "Cuts on the pull through shingle and membrane, without the tip finding the deck." },
  { id: "hand-seamer", n: "Hand seamer", t: ["roofing"],
    w: "Bends and locks metal up on the roof, not down at the brake." },
  { id: "hand-riveter", n: "Hand riveter", t: ["roofing"],
    w: "Holds corners and splices in light metal where a screw has nothing to bite." },
  { id: "standup-gun", n: "Stand-up screw gun", t: ["roofing"],
    w: "Drives plates standing up instead of crawling a whole section on your knees." },
  { id: "iso-knife", n: "Insulation knife (ISO knife)", t: ["roofing"],
    w: "Cuts the full thickness around a curb. A utility knife only scores and snaps." },
  /* The welder and the roller only ever exist together — same call as the solder
     torch and the compression tool, which ship as one row each. */
  { id: "hand-welder", n: "Hot-air hand welder and seam roller", t: ["roofing"],
    w: "The automatic runs the field. The details are yours, and heat alone doesn't close a seam." },
  /* It finds skips. It does NOT say a seam is good — the non-contact tester says
     "maybe hot" and never "dead", and this is the same sentence one trade over. */
  { id: "seam-probe", n: "Seam probe", t: ["roofing"],
    w: "Catches skips your eye slides past. Finding none doesn't make the seam good." },
  { id: "roof-cutter", n: "Roof cutter (cut saw)", t: ["roofing"],
    w: "Cuts the old roof into strips so it comes off in pieces, not acres." },
  /* Single-ply is WELDED; mod bit is TORCHED. The seed said "mod bit gets welded
     with flame" and that one word is how a roofer knows who wrote a page. */
  { id: "roofing-torch", n: "Roofing torch kit", t: ["roofing"],
    w: "Torch-down mod bit — the torch, the hose and the regulator ride together." },
  { id: "rolling-magnet", n: "Rolling magnet", t: ["roofing"],
    w: "Tear-off throws nails into grass and driveway. You find them or the tires do." },
  /* Says an unweighted tarp travels. Never says a weighted one stays. */
  { id: "tarps", n: "Tarps and the weight for them", t: ["roofing", "gc"],
    w: "Weather doesn't wait on the forecast. A tarp with nothing on it travels." },

  /* ---- creative / video: the one-person shop's bag -------------------------
     Trade #9, and the first bag on this page that is not a construction bag.
     Where a jobsite row is about the tool, nearly every row here is about the
     SPARE — this trade's whole failure mode is a thing that works until the one
     take you cannot shoot again. Nothing here names a brand, a format, a codec
     or a rating (creative/items.js §safety), and the two paper rows are item
     NAMES only: what a release or a licence actually covers is not ours to say. */
  { id: "spare-batteries", n: "Spare batteries & the charger", t: ["creative"],
    w: "Two on the camera is one. The interview always runs longer than the schedule said." },
  { id: "more-cards", n: "More cards than the day needs", t: ["creative"],
    w: "A card fails once in a career, on the day nobody can be brought back." },
  { id: "offload-drives", n: "Reader and two drives to offload to", t: ["creative"],
    w: "Copy twice before you leave the location. A card is not a backup and neither is one drive." },
  { id: "two-lavs", n: "Two lav kits, and spares for both", t: ["creative"],
    w: "Bring the second one for a one-person interview. It is what saves the take when the first buzzes." },
  { id: "headphones", n: "Closed-back headphones", t: ["creative"],
    w: "You cannot hear a buzz on the camera speaker. Wear them on every take, not just the first." },
  { id: "nd-filters", n: "ND filters", t: ["creative"],
    w: "Outside at midday you are either stopped down to nothing or shooting at the wrong shutter." },
  { id: "gaff-tape", n: "Gaff tape & camera tape", t: ["creative"],
    w: "Comes off the client's wall clean. The silver stuff takes paint with it and you buy the wall." },
  { id: "sandbags", n: "Sandbags", t: ["creative"],
    w: "A stand with a light up high and nothing on the leg is the one thing on set that hurts somebody." },
  { id: "clamps", n: "A-clamps and a grip clamp", t: ["creative"],
    w: "Holds the flag, the cable, the blind that keeps blowing into frame. You will use every one." },
  { id: "bounce", n: "Bounce and negative fill", t: ["creative"],
    w: "Taking light off one side does more for a face than adding another light to it." },
  { id: "spare-plate", n: "Spare quick-release plate", t: ["creative"],
    w: "The plate is always on the other camera, at home, on the desk. Keep one taped in the bag." },
  { id: "lens-cloth-blower", n: "Blower, cloth and wipes", t: ["creative"],
    w: "One speck on the front element sits in every frame of the day and nobody catches it on the flip-out." },
  { id: "paper-releases", n: "Printed releases", t: ["creative"],
    w: "Signed on the day or not at all — chasing one afterwards is how a shot leaves the cut. What it covers is between the client and their lawyer, not this page." },
  { id: "sync-clap", n: "Something to clap for sync", t: ["creative"],
    w: "A slate, or your hands in frame. Beats scrubbing two waveforms at midnight." },

  /* ---- concrete: trade #10 ---------------------------------------------- */
  { id: "come-along-rake", n: "Concrete rake (come-along)", t: ["concrete"],
    w: "You pull mud, you don't shovel it. A square shovel in a placement is a man working twice as hard for half as far." },
  { id: "bull-float", n: "Bull float and handles", t: ["concrete"],
    w: "Bring the second handle section. The one pour you can't reach the middle of is the one you'll remember." },
  { id: "hand-float-trowel", n: "Hand float and steel trowel", t: ["concrete"],
    w: "Mag first, steel after. Reaching for the steel too early is the mistake that shows up in the finish forever." },
  { id: "edger-groover", n: "Edger and groover", t: ["concrete"],
    w: "The two passes nobody sees you make and everybody sees you skip. Keep both in the bucket, not in the truck." },
  { id: "rebar-tie-tool", n: "Rebar tie tool", t: ["concrete"],
    w: "A twister or a tie gun. Pliers work until about the two hundredth tie, and then your hand is done for the week." },
  { id: "knee-boards", n: "Knee boards", t: ["concrete"],
    w: "How you get back out onto a slab that won't hold you yet. Two of them, and you move the one behind you." },
  { id: "rubber-boots-gloves", n: "Rubber boots and gloves", t: ["concrete"],
    w: "Wet concrete is caustic and it does not hurt until hours later. Leather boots wick it straight to your skin — rinse anything that gets in." },
  { id: "screed-straightedge", n: "Screed straightedge", t: ["concrete"],
    w: "Magnesium, and longer than you think you need. A short one rides the high spots and puts a wave in the floor." },
  { id: "concrete-vibrator", n: "Concrete vibrator", t: ["concrete"],
    w: "For consolidating, not for moving mud sideways. Dragging a pour with the stick is how you leave a rock pocket at the bottom of a wall." },
  { id: "marking-paint", n: "Marking paint", t: ["concrete", "gc"],
    w: "Layout, wash-out, keep-off, and where the truck backs in. Everything you say once and then have to say again all day." },

  /* ---- masonry: trade #11 ------------------------------------------------
     THE TROWEL ROW IS WHY THIS BLOCK IS TAGGED THE WAY IT IS. Before this
     trade shipped, the only trowel in the whole program was "Hand float and
     steel trowel" tagged concrete — a DIFFERENT OBJECT. Say "trowel" on a
     mixed job and the finisher's steel one or the tile man's notched one walks
     over; the brick trowel is the third thing with that name, which is exactly
     the near-miss commons/names.js exists for. */
  { id: "brick-trowel", n: "Brick trowel", t: ["masonry"],
    w: "London or Philadelphia, and the length is a lifetime argument. Say trowel on a mixed job and the finisher's or the tile man's walks over." },
  { id: "mason-line-blocks", n: "Mason's line, blocks and pins", t: ["masonry"],
    w: "The leads are yours; everything between them belongs to the line. Carry spare — the one that snaps is always on the longest wall." },
  { id: "line-twig", n: "Line twigs", t: ["masonry"],
    w: "The clip that holds a long line off the course in the middle. Without one the line bellies and nobody sees it until it is tooled." },
  { id: "jointers", n: "Jointers — concave, V, raked, weathered", t: ["masonry"],
    w: "The profile comes off the approved panel, not out of your bag. Carry more than one, and carry a slicker for the head joints." },
  { id: "story-pole", n: "Story pole (course rod)", t: ["masonry"],
    w: "Marked once for the job, and every lead comes off the same stick. Coursing arguments start the day somebody reaches for a tape instead." },
  { id: "tuckpointer", n: "Tuckpointer and pointing trowel", t: ["masonry"],
    w: "Two widths of the same idea. Grinding out is the loud half; getting mud back in without smearing the face is the half anybody can see afterwards." },
  { id: "mud-boards", n: "Mud boards and tubs", t: ["masonry"],
    w: "Boards go where the layers are, not where the mixer is. A tender's whole day is the boards staying full and the mud staying live." },
  { id: "brick-hammer-set", n: "Brick hammer, brick set and a plugging chisel", t: ["masonry"],
    w: "A cut you make at the wall beats a walk to the saw. The plugging chisel is what gets one unit out without wrecking the three around it." },
  { id: "mason-level", n: "Mason's level — a short one and a long one", t: ["masonry"],
    w: "Plumb, level and the twist in one read. A short level on a lead is how a wall gets built dead wrong and perfectly straight." },
  { id: "corner-poles", n: "Corner poles", t: ["masonry"],
    w: "Runs a whole lift without hand-building leads. On any wall long enough to argue about, it pays for the tender's trip to the truck." },
  { id: "grinder-shroud-vac", n: "Grinder with a dust shroud and vac, and spare blades", t: ["masonry", "concrete"],
    w: "Grinding out is the repair and the dust is what gets you shut down on an occupied building. Joints eat blades faster than anybody budgets." },
  { id: "wash-down-kit", n: "Wash-down kit — brushes, barrel and a pump sprayer", t: ["masonry"],
    w: "Cleaning is a scheduled operation, not a broom at the end. Whatever you wash with, try it on the panel first — the wall you learn on is the wall you own." },

  /* ---- sitework: trade #12 -----------------------------------------------
     THE ONLY BAG ON THIS RACK WHERE HALF THE GEAR IS FOR MARKING THE GROUND
     rather than working it. A dirt hand's day is decided by whether the right
     things are painted, flagged, staked and written on before a bucket moves,
     and by whether he can still find them after a rain and a scraper pass. The
     4-gas monitor is on this list and it is the one row on the whole commons
     that says out loud what it does NOT do. */
  /* WAS `marking-paint`, WHICH concrete AND gc ALREADY OWNED — two different
     rows under one id since trade #12 shipped. The bag keys picks by id, so a
     man who ticked one was silently carrying both and could remove neither;
     `commons-bag.mjs` has been failing on it and nothing in CI runs that gate.
     Swept while standing up trade #13, along with the same class in gear.js. */
  { id: "marking-paint-locates", n: "Marking paint in a colour the locators didn't use, and a spare case", t: ["sitework"],
    w: "You white-line your dig before you call it in, then re-mark it every time the rain takes it. Paint over somebody's locate marks and the next man digs to the wrong line." },
  { id: "pin-flags", n: "Pin flags, whiskers and flagging tape", t: ["sitework"],
    w: "Paint washes off and gets scraped away. A flag stands up out of the mud, and a stub nobody flagged is two hours of hand digging in three months." },
  { id: "lath-keel-hatchet", n: "Lath, keel and a hatchet", t: ["sitework"],
    w: "You reset more stakes than the surveyor ever does, and whatever isn't written on the lath gets remembered wrong." },
  { id: "probe-rod", n: "Probe rod", t: ["sitework"],
    w: "Feels for the top of a pipe, the top of rock and the soft spot before the bucket finds it for you." },
  { id: "sharpshooter", n: "Sharpshooter and a round point", t: ["sitework"],
    w: "Every machine job ends with a man in the hole with a shovel, and hand work near a live line needs one that cuts rather than one that pushes." },
  { id: "digging-bar", n: "Digging bar", t: ["sitework"],
    w: "Roots, rock and pry work the hoe can't do without breaking something more expensive than the bar." },
  { id: "grade-rod", n: "Grade rod, and a cut stick you cut yourself", t: ["sitework"],
    w: "Every argument about grade ends the second somebody puts a rod on it — and yours is the one you trust in a ditch at half four." },
  { id: "laser-receiver", n: "Laser receiver and a pocket of batteries", t: ["sitework"],
    w: "A dead receiver stops the whole run, the rover dies mid-afternoon, and there is never a spare on the job." },
  { id: "gasket-lube", n: "Gasket lube, spare gaskets and a clean rag", t: ["sitework"],
    w: "A dry gasket rolls, and a rolled gasket is a failed test three weeks later that nobody can explain." },
  { id: "test-plugs", n: "Test plug set and a fat marker", t: ["sitework"],
    w: "Cap and mark every open end at quitting time. A rock in the line at four o'clock is a mandrel that won't pull in three weeks." },
  { id: "gas-monitor", n: "4-gas monitor", t: ["sitework"],
    w: "You carry your own and you bump-test it. It does not make the entry call for you — the competent person on site does, in front of the actual hole, and no page ever will." },

  /* ---- flooring: trade #13 -----------------------------------------------
     Written for the crew that arrives after everybody else has demobbed. Half
     this list is here because a floor mechanic spends his day KNEELING, and the
     other half is because his whole trade is decided by what the substrate is
     doing — which is why the straightedge and his own meter are on it and no
     number they read is anywhere in this program. */
  { id: "knee-pads", n: "Knee pads you can actually wear all day", t: ["flooring"],
    w: "You are on your knees eight hours. The cheap ones slide, cut off the circulation behind your knee, and you take them off by ten — which is how guys end up needing a surgeon at fifty." },
  /* NOT `hook-blades` — roofing already owns that id, and the bag keys picks BY
     ID, so a second row under the same id ticks both and lets you remove
     neither (the defect this cycle found sitting on `marking-paint`). Same
     tool, genuinely different advice: the roofer's point is the tip finding his
     deck, the floor guy's is that a dull blade shows at every seam. */
  { id: "hook-blade-change", n: "Hook blades, and more of them than you think", t: ["flooring"],
    w: "A dull blade tears the backing instead of cutting it, and a torn cut shows at every seam. Change it far more often than feels reasonable — the blade is the cheapest thing on the job." },
  { id: "straightedge", n: "A long straightedge you trust", t: ["flooring", "concrete"],
    w: "Lay it on the slab before you agree to a start date. What you can see under it is the argument, and once you have covered it nobody can ever see it again." },
  { id: "own-meter", n: "Your own moisture meter, and your own probes", t: ["flooring"],
    w: "Somebody else's number over the phone is not a reading. Take your own, photograph the meter with the room in the frame, and write down where you stood — the slab cannot be re-tested once it is covered." },
  { id: "floor-roller", n: "A floor roller, sectioned so you can carry it", t: ["flooring"],
    w: "The bond happens under the roller, not under the trowel. A one-piece roller is the tool you leave in the van, and a floor that never got rolled is a callback with your name on it." },
  { id: "undercut-saw", n: "Undercut saw", t: ["flooring"],
    w: "Every jamb, every casing, every door stop. Cutting the floor to fit the trim instead of the trim to fit the floor is what makes a job look like it was done by somebody's cousin." },
  { id: "tapping-block", n: "Tapping block, pull bar and spacers", t: ["flooring"],
    w: "The last row is where you find out the wall is not straight. Beat a plank with a scrap of the plank and you own the damaged edge you just made." },
  { id: "seam-kit", n: "Seam iron, tape and sealer — the whole kit, together", t: ["flooring"],
    w: "An unsealed seam is a callback, not a style choice, and the one job you left the sealer at the shop is the one with a seam down the middle of a corridor." },
  { id: "layout-chalk", n: "Chalk line, and chalk in a colour that comes back up", t: ["flooring"],
    w: "Red chalk under a light-coloured floor telegraphs through and stays there. Blue or white, and snap the line for the field before you open the first box." },

  /* ---- painting: trade #14 -----------------------------------------------
     THE BAG WHERE HALF THE GEAR EXISTS TO CATCH A MISTAKE WHILE IT IS STILL
     WET. A run caught wet is a rag; found dry it is sand, prime and repaint —
     so the rags ride by the case, the raking light runs the five-o'clock
     inspection before the sun does, and the razor kit takes the tape line
     back off the glass. Seeded by three-voice fan-out, curated at stand-up. */
  { id: "five-in-one", n: "5-in-1", t: ["painting"],
    w: "Opens cans, digs cracks, spreads patch, squeezes covers dry, seats lids — the tool your hand reaches for a hundred times a day without asking. Leave it home once and your hand spends the whole day telling you about it." },
  { id: "sash-brush", n: "The angled sash nobody else touches", t: ["painting"],
    w: "A new brush fights you; one washed and spun a hundred times lays the line right where you look. That's why it rides in its keeper away from the crew bucket, and why it doesn't get lent — to anybody." },
  { id: "extension-pole", n: "Extension pole, one that locks tight", t: ["painting"],
    w: "Half of what a green hand climbs a ladder for, you roll from the floor — and your shoulders are the ones still working in twenty years. The bargain pole that slips a quarter turn mid-stroke is how you learn why the old hands paid up." },
  { id: "tape-two-widths", n: "Good tape, two widths", t: ["painting"],
    w: "Wide for masking off, narrow for tight cuts and curves — and the delicate stuff for anything painted inside a month. Cheap tape bills you twice: once when the line bleeds, again when it pulls last week's finish off on the way out." },
  { id: "rags-by-the-case", n: "Rags by the case, one damp in your back pocket", t: ["painting"],
    w: "A run caught wet is a wipe; found dry it's sand, prime, repaint and a touch-up that flashes in low light. Buy them like they're free, because the day you start rationing rags the job starts showing it." },
  { id: "wet-film-gauge", n: "Wet film gauge", t: ["painting"],
    w: "The data sheet calls the build; the gauge tells you whether you're hitting it while the coat's still wet enough to fix. Your eye is free, and it flatters whoever's holding the gun — right up to the day another man's gauge reads your work." },
  { id: "pot-hook", n: "Pot hook", t: ["painting"],
    w: "Hangs the cut pot off the rung so one hand minds the ladder and the other runs the brush. Every crew that skips them has the same story, and it ends on the customer's carpet." },
  { id: "strainers", n: "Strainers, a stack", t: ["painting"],
    w: "Any can that's been opened before gets strained — no exceptions, no matter how clean it looks. The chunk you skip finds the tip mid-pass at the top of the ladder, or rides the roller into the middle of the biggest wall in the house." },
  { id: "spinner", n: "Spinner", t: ["painting"],
    w: "Ten seconds down inside an empty bucket and a washed cover's ready for tomorrow instead of stiff by Monday; brushes come back the same way. Pays for itself in covers the first month — and you only ever spin one outside the bucket once." },
  { id: "razor-scraper", n: "Razor kit — scraper and a box of fresh blades", t: ["painting"],
    w: "A fresh blade takes drips and overspray off glass like they never happened; a tired one scratches the customer's window into the punch list. It also scores every tape line before the pull, so the tape doesn't decide where your paint ends." },
  { id: "canvas-drops", n: "Canvas drops, runners for the walk paths", t: ["painting"],
    w: "Canvas drinks a drip and stays put; plastic slides under a ladder foot and keeps every drop wet all day for your boot to find. Cover the path from the door to the work, because the floor you didn't drop is the only part of the job the customer remembers." },
  { id: "raking-light", n: "A light to rake the walls", t: ["painting"],
    w: "Overhead light forgives everything; a hard light raked down the wall calls out the holidays, the flashed patch and the fat edge while there's still paint in the pot. The low sun through the customer's window runs the same inspection at five o'clock, whether you did or not." }
];
