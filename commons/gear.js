/* THE COMMONS — the gear list. Data only; commons/index.html is the surface.
 *
 * WHAT THIS IS NOT. It is not a shopping list, an affiliate feed, or a catalog.
 * There are no brands, no model numbers, no prices, no specs, and no ratings —
 * on purpose, and it is the only reason a list like this can be trusted. Every
 * "must-have tools" page on the internet is somebody's commission; this one names
 * the THING and lets a crew buy whatever their shop buys.
 *
 * THE PARTITION. `t: ["universal"]` means every one of the six trades genuinely
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
window.COMMONS_TRADES = [
  { slug: "universal",   short: "Every trade",  name: "Every Trade",          color: "#FF6B1A" },
  { slug: "av",          short: "AV",           name: "AV",                   color: "#F0BE1E" },
  { slug: "plumbing",    short: "Plumbing",     name: "Plumbing",             color: "#C87137" },
  { slug: "electrical",  short: "Electrical",   name: "Electrical",           color: "#3FB6F5" },
  { slug: "hvac",        short: "HVAC/R",       name: "HVAC/R",               color: "#4FE0C0" },
  { slug: "low-voltage", short: "Low-voltage",  name: "Low-Voltage & Fire",   color: "#FF9E80" },
  { slug: "gc",          short: "GC / Super",   name: "GC & Site Super",      color: "#8CE86B" }
];

window.COMMONS_GEAR = [
  /* ---- the floor: all six trades, no exceptions ------------------------- */
  { id: "tape-measure", n: "Tape measure", t: ["universal"],
    w: "The hook is loose on purpose, so inside and outside both read true." },
  { id: "utility-knife", n: "Utility knife", t: ["universal"],
    w: "Opens boxes, scores drywall, strips jacket, trims foam. You'll grab it hourly." },
  { id: "multi-bit-driver", n: "Multi-bit screwdriver", t: ["universal"],
    w: "Bits and nut drivers in one handle. Kills the trip back downstairs." },
  { id: "drill-driver", n: "Cordless drill/driver", t: ["universal"],
    w: "Use the clutch and the side handle — a bit that catches will twist your wrist." },
  { id: "torpedo-level", n: "Torpedo level", t: ["universal"],
    w: "Nobody remembers your wiring. Everybody sees a crooked mount." },
  { id: "headlamp", n: "Headlamp", t: ["universal"],
    w: "Panels, ceilings, crawlspaces. Hands stay on the work instead of holding light." },
  { id: "ncvt", n: "Non-contact voltage tester", t: ["universal"],
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
  { id: "jab-saw", n: "Jab saw (drywall saw)", t: ["av", "plumbing", "electrical", "hvac", "low-voltage"],
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
  { id: "box-level", n: "Box level", t: ["gc"],
    w: "Punch walls and door frames with something the finish trades can't argue." },
  { id: "moisture-meter", n: "Moisture meter", t: ["gc"],
    w: "Screens framing and board before finishes go on. On slab it's a heads-up only." },
  { id: "keel", n: "Lumber crayon (keel)", t: ["gc"],
    w: "Marks wet concrete, dirty steel and rough lumber where a marker quits." },
  { id: "marking-paint", n: "Inverted marking paint wand", t: ["gc"],
    w: "Lays out and flags on dirt and slab so nobody claims surprise." },
  { id: "punch-tape", n: "Punch tape (blue painter's tape)", t: ["gc"],
    w: "Flags the defect where the trade finds it, no explanation needed." },
  { id: "two-way-radio", n: "Two-way radio", t: ["gc"],
    w: "Reaches the crane, the gate and every foreman without waiting on bars." }
];
