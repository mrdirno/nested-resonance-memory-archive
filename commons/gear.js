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
  { id: "marking-paint", n: "Inverted marking paint wand", t: ["gc"],
    w: "Lays out and flags on dirt and slab so nobody claims surprise." },
  { id: "punch-tape", n: "Punch tape (blue painter's tape)", t: ["gc"],
    w: "Flags the defect where the trade finds it, no explanation needed." },
  { id: "two-way-radio", n: "Two-way radio", t: ["gc"],
    w: "Reaches the crane, the gate and every foreman without waiting on bars." },

  /* ---- framing & drywall -------------------------------------------------
   * Added 2026-08-11. The trade shipped a full toolkit on 2026-08-09 and this
   * list was never told, so for two days a framer opened the page that calls
   * itself "every trade" and found seven chips, none of them his. The deploy
   * now refuses a toolkit with no chip and the ship gate refuses a chip with no
   * rows, because nothing about that failure was visible — no error, no 404,
   * just a trade quietly absent from the commons. */
  { id: "rafter-square", n: "Rafter square", t: ["framing"],
    w: "Squares a cut and steps out an angle without doing the math twice." },
  { id: "chalk-line", n: "Chalk line (chalk box)", t: ["framing"],
    w: "Snap blue — red is permanent, and it comes back through the painter's finish." },
  { id: "dry-line", n: "String line (dry line)", t: ["framing"],
    w: "A wall can read plumb at every stud and still be bowed. The line shows it." },
  { id: "aviation-snips", n: "Aviation snips, left, right & straight", t: ["framing"],
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
  { id: "locking-pliers", n: "Locking pliers", t: ["framing"],
    w: "Holds two pieces of steel together while your other hand drives the screw." },

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
    w: "A slate, or your hands in frame. Beats scrubbing two waveforms at midnight." }
];
