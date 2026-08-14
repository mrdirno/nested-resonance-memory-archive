/* CONCRETE FIELD TOOLKIT — the trade config.
 *
 * TRADE #10, and the THIRD one promoted by the INTERFACE MATRIX rule rather than
 * inherited from the original five-trade build order. The rule: the next family
 * is whichever unserved party the most served trades already chase. Concrete is
 * the only unserved receiver named by TWO served trades independently — the
 * electrician (sleeves, blockouts, housekeeping pads, pre-pour walk, the ground)
 * and the plumber (sleeve in the pour, blockout, pre-pour walk, pad) — and the
 * GC's mirror row is literally "the pre-pour call".
 *
 * IT IS ALSO THE EARLIEST GATE IN THE ENTIRE PROGRAM. Read the gate ladders in
 * the matrix: AV opens with `pour`. HVAC opens with `pour`. LV opens with `pour`.
 * EC and PC open with `backfill · slab`. GC opens with `backfill · pour`. Six of
 * six trades count down to this crew's day, and it is the FIRST thing on five of
 * those six ladders. Every other toolkit in this program has been building the
 * request half of a boundary whose receiver had nothing.
 *
 * AND IT IS THE ONE GATE THAT DOES NOT REOPEN. A wall can be cut, a ceiling can
 * be pulled, a roof can be flashed after the fact. After the truck washes out,
 * every miss is a core drill, an epoxy dowel or a change order — which is exactly
 * why five trades independently built a page to chase this crew and why the crew
 * itself had no way to answer.
 *
 * ONE FAMILY, TWO HALVES, ON PURPOSE — the framing and roofing precedent applied
 * a third time. RESIDENTIAL FLATWORK (footings, slab-on-grade, driveways, wet
 * screed, broom finish, the short load) and COMMERCIAL STRUCTURAL (grade beams,
 * walls, columns, elevated decks, pour strips, the pump) are one population here,
 * and the crew inside it is one crew: form setters, rodbusters, placers and
 * finishers. Where the halves differ the DATA carries both words. A page that
 * speaks only one of them tells half this trade it was not written for them.
 *
 * WHY THIS TRADE GETS THE SAME HARD EDGE AS ROOFING, FOR A DIFFERENT REASON.
 * Roofing is a warranty trade; concrete is a STRUCTURAL trade, and a slab that
 * fails is a deposition. A strength, a slump, an air content, a bar size, a lap,
 * a cover, a cure time, an admixture dosage or a joint spacing that LOOKS
 * authoritative on a phone is not a helpful default here — it is somebody's
 * exhibit, and it is somebody else's stamp. Nothing in this toolkit rates, sizes,
 * doses, spaces or specifies anything. The man states what HE has off HIS
 * approved mix design and HIS structural drawings; the engineer of record, the
 * mix submittal, the testing lab and the AHJ own what it is supposed to be.
 * See items.js.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the concrete kit.
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
  slug: "concrete",

  name: "Concrete Field Toolkit",

  // A LADDER, NOT A HOUSE — the sibling rule: every icon is the GEAR the trade
  // carries (🧰 🔧 ⚡ ❄️ 📹 🦺 🪚 🪜 🎬), never the thing it builds. A brick would
  // read as masonry and a slab does not have a glyph. The five-gallon bucket is
  // the one object on every pour there has ever been — water, tie wire, hand
  // tools, patch, washout — and no sibling is close to it at chip size.
  icon: "🪣",

  // ONE WORD, like every sibling. "Concrete" is eight characters; "Electrical"
  // is ten and has shipped at 390px since trade #3.
  brandLead: "Concrete",
  brandTail: "Field Toolkit",

  /* GREEN, AND IT IS THIS TRADE'S OWN WORD. Concrete that has set and has not
     cured is GREEN — you do not load it, you do not strip it, you green-cut it.
     No other trade on this rack uses the word for a state of its own material,
     and it beats the alternatives honestly: the trade's material is grey (the
     commons already owns the grey band and an accent needs chroma), its chalk is
     blue (electrical, 200.8 degrees) and its cones are orange (low-voltage coral
     and plumbing copper, 14.2 and 24.0).

     THE HUE WAS MEASURED, NOT EYEBALLED — the roofing precedent, run again with
     ten chips on the rack. Hues in the program: low-voltage 14.2 · plumbing 24.0
     · AV 45.7 · commons 90.0 · GC 104.2 · HVAC/R 166.8 · electrical 200.8 ·
     framing 247.3 · creative 288.0 · roofing 330.0. The widest open arc left runs
     104.2 -> 166.8 at 62.6 degrees and this sits at 135.2, dead in the middle of
     it: 31.0 degrees off GC and 31.6 off HVAC/R, wider than the 21.7 that already
     separates plumbing from AV and three times the 9.8 between low-voltage and
     plumbing. It is also a full step DARKER than the GC lime (HSL L 0.51 against
     0.66), so the two do not read as one chip on a phone in the sun.

     CONTRAST MEASURED AGAINST THE THREE BARS THIS PROGRAM HOLDS, not guessed:
     accent on the #242A31 nav 7.67:1 (bar 7) · accentInk sitting on the accent
     9.56:1 (bar 9) · white on accentDeep 5.90:1 (bar 5). Hand-picked rather than
     computed at runtime — color-mix() is not safe on the old Android browsers
     these pages land on. */
  accent: "#2DD758",
  accentInk: "#03190B",
  accentDeep: "#12742B",
  accentTint: "#E3F8E9",

  chain: "form setters, rodbusters, placers and finishers / foremen and leads / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Finisher / Form setter / Rodbuster"],
    ["project_manager", "Foreman / Lead"],
    ["leadership", "Super / PM / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Pour card — trucks, times and yardage as they land",
  wishPurposeHint: "e.g. Write down every truck as it comes in — ticket, time on site, time discharged, what we added — so the yardage argument three weeks from now is a document instead of two memories…"
};
