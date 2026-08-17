/* SITEWORK FIELD TOOLKIT — the trade config.
 *
 * TRADE #12, and the first one promoted with the BUILD ORDER exhausted. The
 * private ladder disposed of it in the same entry that shipped trade #11: the
 * count NOMINATES, the record DISPOSES, and sitework was the only remaining
 * candidate clearing both of the disqualifiers that killed the two nominees
 * ranked above masonry.
 *
 * HE OWNS THE EARLIEST GATE ON THE JOB, AND THREE SERVED KITS ALREADY COUNT
 * DOWN TO IT IN THEIR OWN WORDS. Backfill is position #1 on THREE shipped gate
 * ladders — electrical, plumbing and GC all open their milestone list with the
 * dirt going back — and each of those kits ships asks bound to it. Nothing
 * anywhere publishes the date. The man with the excavator is the only one who
 * has it, and until this kit he had no page to say it on. That is the same
 * condition that promoted concrete at #10 and masonry at #11, one gate earlier.
 *
 * A CLOSED DITCH DOES NOT REOPEN, AND THAT IS THE SECOND QUALIFICATION.
 * concrete/trade.js wrote the test while explaining why a ceiling is not a real
 * gate: "a wall can be cut, A CEILING CAN BE PULLED." A trench that has been
 * backfilled and compacted is not cut, pulled or cored — it is dug again, and
 * everything in it that was right the first time comes out with it. An unshot
 * line, a missing pull string, a stub two feet off, a tie-in nobody witnessed:
 * every one of them is free the morning before and a change order the morning
 * after.
 *
 * ASK-HEAVY, WHICH IS THE HALF MASONRY WAS HONEST ABOUT MISSING. The mason is
 * receiver-heavy and ask-light — chased by everybody, chasing few people back.
 * The dirt foreman is the opposite: he is on both ends every single day, and the
 * pre-backfill call is an ASK he sends out, not a record he keeps. That is why
 * the pinned tool here is a broadcast with a clock on it rather than a log.
 *
 * WHAT THIS TRADE IS NOT ALLOWED TO SHIP, decided before a line was written.
 * This is the sharpest refusal list in the program, sharper than masonry's, and
 * it is not negotiable by a later cycle:
 *   - NO trench protection in any form. No depth threshold, no slope ratio, no
 *     benching geometry, no soil classification (A/B/C), no tabulated data, no
 *     shield or shoring selection, no spoil setback, no "safe to enter", no
 *     competent-person determination. Not as a value, not as a default, not as
 *     a placeholder, not as a picker. Men die in trenches and the number is
 *     engineered off a soil that a page on a phone has never seen.
 *   - NO compaction specification: no proctor percentage, no lift thickness as
 *     a value, no moisture range, no passes-per-lift, no test frequency.
 *   - NO bedding or backfill class, no haunching detail, no cover depth
 *     minimum, no deflection limit, no separation or clearance distance between
 *     utilities, no thrust-block sizing, no test pressure or duration.
 *   - NO locate call, no ticket number issued by us, and nothing that could be
 *     read as a locate being current or a line being clear.
 * He states what HIS OWN plan, spec, geotech report and utility notes say. The
 * engineer of record, the geotech and the one-call centre own what it is
 * supposed to be. Every one of those refusals is a place where the honest tool
 * is a picker that structures what the USER types, and we ship that instead.
 *
 * NO FORK, VERIFIED RATHER THAN ASSUMED: concrete/items.js owns the slab, the
 * footing and the pour; its `excav` receiver is this crew, named from the other
 * side. Different act, different iron, different NAICS (238910 site prep vs
 * 238110 concrete). A dirt contractor digs, hauls, beds, lays pipe and puts it
 * back; a concrete crew forms and places. The two are on the phone with each
 * other constantly, which is the argument FOR the trade rather than against it.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the sitework kit.
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
  // loop knows which toolkit a request belongs to.
  slug: "sitework",

  name: "Sitework Field Toolkit",

  /* THE SIBLING RULE HOLDS HERE, unlike at #11: an icon is GEAR the trade
     carries, never the thing it builds. This trade's gear is the machine. There
     is no excavator, no hoe and no dozer in the set; the tractor is the only
     glyph in it that is a working machine a man sits in, and on a rack where
     every neighbour is a hand tool it reads as "the iron" at chip size.

     🚧 WAS THE OBVIOUS PICK AND IT IS THE WORST ONE ON THE BOARD. It is the
     generic construction glyph, and on a rack where all twelve chips are
     construction trades the generic one identifies nobody — it says
     "construction" to a man who is already looking at eleven construction kits.
     A rack chip has one job: the man whose trade it is finds it without
     reading. ⛏️ reads as mining and 🪣 is already the concrete kit. */
  icon: "🚜",

  // ONE WORD, like every sibling. GCs write "sitework" on the schedule, the
  // crew says "dirt", and the company on the truck says "excavating". Sitework
  // is the word that a foreman, a super and a PM all recognise as this scope.
  brandLead: "Sitework",
  brandTail: "Field Toolkit",

  /* THE ACCENT WAS MEASURED AND THE MEASUREMENT KILLED THE FIRST TWO PICKS.
     The rack was already eleven chips deep, so this ran the roofing/concrete/
     masonry precedent with a proper perceptual metric rather than hue spacing
     alone — CIELAB distance to all eleven shipped chips plus the commons grey,
     under the contrast bar, swept across the whole HSL solid.

     WHAT DIED, WITH NUMBERS:
     - BLUE at hue 224, the widest genuinely chromatic arc left on the wheel
       (200.8 electrical -> 247.3 framing, 46.5 degrees). It never clears the
       7:1 bar against the #242A31 nav: L66 4.06 · L70 4.78 · L74 5.63 · L78
       6.61. The only way up is L80+, which lands on framing's periwinkle — a
       fourth pale blue-violet. Blue fails for exactly the reason masonry
       recorded red failing: the blue channel carries 7% of luminance.
     - EARTH TONES, the obvious choice for a dirt trade. Brown IS plumbing's
       copper (hue 24.0) and a raw-clay red is the colour masonry already
       measured off the board.
     - HI-VIS YELLOW-GREEN, the vest: dE 27.8 from the GC lime and 30.5 from
       masonry's fluorescent line. Real separation, but it lands a third
       chip in a band that already carries two.

     WHAT SURVIVED: SAND. #FFDDA3 is dry fill in the sun and the dust behind a
     scraper, and it measures better than any of them — 11.12:1 on the nav (bar
     7), and CIELAB dE 32.8 from its nearest neighbour (the commons grey) and
     33.0 from the low-voltage coral. For scale, the CLOSEST PAIR ALREADY
     SHIPPING on this rack is GC lime against concrete green at dE 19.3. This
     chip is 1.7x more separated from everything than the tightest pair the rack
     already tolerates, and it sits 44.1 from the AV gold it shares a hue family
     with — the separation is in lightness and chroma, not hue, which is the
     axis that was still open.

     THE OTHER THREE BARS, hand-picked and measured, not computed at runtime
     (color-mix() is not safe on the old Android browsers these pages land on):
     accentInk on accent 12.42:1 (bar 9) · white on accentDeep 5.21:1 (bar 5). */
  accent: "#FFDDA3",
  accentInk: "#2A1F08",
  accentDeep: "#8A6718",
  accentTint: "#FFF6E4",

  // OPERATORS AND PIPELAYERS, and both words are load-bearing. The man in the
  // machine and the man in the ditch are different classifications doing
  // different work at the same moment, and a kit that folds them into "crew"
  // cannot count who actually stood when a tag gets written.
  chain: "operators and pipelayers / foremen and supers / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Operator / Pipelayer / Laborer"],
    ["project_manager", "Foreman / Lead"],
    ["leadership", "Super / PM / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. The call I make before the dirt goes back in",
  wishPurposeHint: "e.g. Four outfits have something in this trench and every one of them told me a different day. I want one list per run I can walk, tick what's in and what's still open, put a time on it, and send it to all of them — so nobody says later that nobody told him…"
};
