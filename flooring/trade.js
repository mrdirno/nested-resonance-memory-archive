/* FLOORING FIELD TOOLKIT — the trade config.
 *
 * TRADE #13, and the first one the COUNTING RULE could not have produced.
 *
 * HOW IT WAS CHOSEN. §MASONRY set the method at #11 — "the rule NOMINATES, the
 * record DISPOSES" — and this is the cycle where the two disagreed completely.
 * Re-counted off every served kit's own `who[]` roster rather than off the
 * matrix summary, the nominators were steel 4 (dead: the bolt-up log, weld map,
 * WPS and mill cert ARE the IBC ch.17 special-inspection record), ceilings 3
 * (dead: ruled a DEPTH rung inside framing), fire/sprinkler 3, doors/frames 3.
 * FLOORING WAS NOMINATED BY NOBODY — zero, the same as glazing, insulation and
 * demo — because a receiver roster can only name a party you hand paperwork to,
 * and this trade arrives after all twelve served kits have gone home.
 *
 * A FOUR-LENS PANEL SCORED IT ANYWAY AND CAME BACK 3-1 FOR THE TRADE WITH NO
 * VOTES, and the fourth lens was the SKEPTIC, whose job was to kill: "I could
 * not kill it." All four independently killed the top live nominee, fire
 * protection, on the same rule that killed steel — for a sprinkler contractor
 * the certified record IS the deliverable (the NFPA 13 hydraulic calc is sealed
 * by a NICET III or a PE, the Contractor's Material and Test Certificate is a
 * form written into the standard, and the ITM report is already owned and
 * numbered by inspection software). What survived the refusal list there was a
 * head-and-fitting order: one page, not a family.
 *
 * WHAT THE COUNT COULD NOT SEE, AND IT IS ON DISK. Three shipped kits already
 * count down to this man's gate IN THEIR OWN WORDS — `av/items.js` "Before
 * floor goes down", `gc/items.js` "Before floors go down" (the LAST rung its
 * gate ladder has) and again "Walk it with me before tile goes in",
 * `low-voltage/items.js` "Before tile goes in" — and NOT ONE of the twelve has
 * a flooring receiver in any roster. Three trades name the moment; nobody can
 * address the man. That is the same condition that promoted sitework at #12,
 * read off the opposite end of the job: the dirt crew owns the EARLIEST gate,
 * the floor crew owns the LAST one, and neither date was ever published.
 *
 * GLUE DOES NOT REOPEN, AND THAT IS THE SECOND QUALIFICATION. concrete/trade.js
 * wrote the test — "a wall can be cut, A CEILING CAN BE PULLED" — and sitework
 * answered it with a backfilled trench. This is harder than both. A bonded floor
 * is not cut, pulled or dug: it is demolished, and the substrate underneath it
 * is somebody else's ninety-day-old mistake that the man who covered it now owns.
 * He is the last trade in the building and the only one whose work permanently
 * seals another company's defect.
 *
 * KILL A SURVIVED STRUCTURALLY, NOT BY DISCIPLINE, and that distinction is the
 * whole reason this trade is buildable where sprinkler is not. Flooring's
 * numbers are not code tables — they are MANUFACTURER WARRANTY TERMS, and they
 * disagree with each other: one adhesive states one maximum RH, the next states
 * another, and the mill's installation instructions in the box override both.
 * There is no number for us to supply even if we wanted to. So every page here
 * takes the reading HE took and the limit HE read off the pail, prints both,
 * and never says whether he may install. Same posture as concrete's mix order.
 *
 * WHAT THIS TRADE IS NOT ALLOWED TO SHIP, decided before a line was written and
 * not negotiable by a later cycle:
 *   - NO moisture limit as a value. No RH percentage, no calcium-chloride
 *     lbs/1000sf, no pH figure, no "acceptable" range, not as a default, not as
 *     a placeholder, not in a picker. He types what the bucket and the mill's
 *     instructions say, and the page prints his number beside his limit.
 *   - NO flatness or levelness tolerance. No fraction in ten feet, no FF/FL
 *     number, no gap under a straightedge as an allowance. FF/FL is the concrete
 *     sub's ASTM E1155 record and the flatness spec is his own contract line.
 *   - NO acclimation period, temperature range or ambient-humidity range as a
 *     value, and no "conditioned and operational" determination.
 *   - NO product data of any kind: wear-layer thickness, DCOF or slip number,
 *     radiant-flux class, flame-spread or fire rating, expansion-gap dimension,
 *     fastener or nail schedule, underlayment rating, IIC/STC sound rating,
 *     seam-sealer type, trowel notch as a spec.
 *   - NO subfloor construction spec: joist spacing, panel thickness, screw
 *     pattern, patch depth, or a moisture-mitigation system by name or mil.
 *   - NO warranty interpretation. This kit never says a warranty is void. It
 *     lets him state what his own instructions require and what he measured,
 *     which is the honest half and the half that actually holds up.
 *   - NO "safe to install", "ready", "acceptable" or "passing" determination in
 *     any form. The whole product is the man refusing to make that call alone.
 * Every one of those is a place where the honest tool is a picker that
 * structures what the USER states off his own submittal, his own instructions
 * and his own meter. A later cycle that adds one is not filling a gap; it is
 * the defect this file was built to refuse.
 *
 * NO FORK, VERIFIED RATHER THAN ASSUMED. concrete/ serves the crew that PLACED
 * the slab and its family ends at the finish; the slab argument happens ninety
 * days later with a different company holding the meter. framing/ works the
 * vertical plane and demobs before the material even lands. The near-miss is
 * framing, the kit that absorbed ceilings — and ceilings died as a family
 * because it is the same company, same guys, one more page. This is a separate
 * contract, a separate crew, a separate supply channel (the DEALER, not the
 * supply house) and a separate month.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the flooring kit.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to. Matches the dir exactly.
  slug: "flooring",

  name: "Flooring Field Toolkit",

  /* THE SIBLING RULE: an icon is GEAR the trade carries, never the thing it
     builds. 🪵 and 🧱 are the thing it builds (and the second is masonry's
     chip anyway). The STRAIGHTEDGE is the one tool on a floor van that decides
     whether the day happens — laid across a slab, the gap under it is the whole
     argument this kit exists to send — and it is the only glyph in the set that
     reads as a rule rather than a ruler at chip size. 📐 is a drafting square
     and reads as an office. Neither 📏 nor 📐 is on the rack. */
  icon: "📏",

  // ONE WORD, like every sibling. The GC writes "flooring" on the schedule, the
  // crew says "floors", and the company on the truck says "floor covering".
  // Flooring is the word a foreman, a super and a dealer all recognise.
  brandLead: "Flooring",
  brandTail: "Field Toolkit",

  /* THE ACCENT WAS MEASURED AGAINST A RACK THAT IS NOW TWELVE CHIPS DEEP, with
     the same method masonry and sitework used: CIELAB distance to every shipped
     chip plus the commons grey, under the 7:1 contrast bar on the #242A31 nav,
     swept across the whole HSL solid (18,800 candidates cleared both bars).

     WHAT DIED, WITH NUMBERS:
     - PURE GREEN at hue 120 scored the single widest gap on the board (dE 40.0)
       and is the worst chip on it. The rack already carries concrete #2DD758,
       gc #8CE86B and masonry #B9EE1B; a fourth green identifies nobody, which
       is the objection sitework recorded against hi-vis yellow-green and it is
       stronger here by one chip.
     - EVERY WARM OPTION. Hues 14 to 45 already carry four chips (low-voltage
       coral 14, plumbing copper 24, sitework sand 36, av gold 45). Wood tone,
       the obvious pick for a flooring trade, lands inside that band and its two
       nearest neighbours are 11 degrees apart. There is no room.
     - BLUE at 224 for the same reason sitework recorded: 6.06 on the nav at
       L74, and the only way over the bar lands on framing's periwinkle.
     - PALE MAGENTA at 308 (dE 31.0, a real number) — but roofing 330 and
       creative 289 already bracket it, and a third pale magenta between two
       pale magentas is the ceilings mistake in colour.

     WHAT SURVIVED: WET SLAB. #8FECFF is hue 190, the one genuinely open arc
     left on the wheel (hvac mint 166 → electrical blue 200), and it separates
     from both by CHROMA rather than hue, which is the axis that was still free.
     And the semantic is the trade's whole gate rather than decoration: this is
     the one trade on the rack whose day is decided by how wet the concrete is.

     MEASURED, hand-picked, not computed at runtime (color-mix() is not safe on
     the old Android browsers these pages land on):
       accent on nav        10.76:1  (bar 7)
       accentInk on accent  12.30:1  (bar 9)
       white on accentDeep   5.84:1  (bar 5)
     CIELAB dE to its three nearest neighbours: electrical 31.0 · commons 31.7 ·
     hvac 32.9. For scale, the CLOSEST PAIR ALREADY SHIPPING is gc lime against
     concrete green at 19.3, so this chip sits 1.6x further from everything than
     the tightest pair the rack already tolerates. */
  accent: "#8FECFF",
  accentInk: "#04222B",
  accentDeep: "#0E6E86",
  accentTint: "#E6FAFF",

  // INSTALLERS AND MECHANICS, and the second word is load-bearing. A floor
  // mechanic and a helper are different classifications doing different work on
  // the same knee pads, and the man who owns the truck is very often the same
  // man kneeling on it — which is why the top rung says owner and lead in one
  // breath rather than pretending there is an office.
  chain: "installers and helpers / lead mechanics / the dealer, the GC and the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Installer / Mechanic / Helper"],
    ["project_manager", "Lead mechanic / Crew lead"],
    ["leadership", "Owner / Dealer / PM"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. The letter I send when the slab isn't ready",
  wishPurposeHint: "e.g. I walk in Monday, the slab reads wet, and if I glue over it the mill walks away from the warranty and the tear-out is on me. I want to put my readings, the limit off my own bucket and what it costs to sit today into one message, and end it with give me the go in writing or tell me who's grinding — because after I spread glue nobody gets the slab back…"
};
