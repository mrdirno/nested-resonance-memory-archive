/* ROOFING FIELD TOOLKIT — the trade config.
 *
 * TRADE #8, and the SECOND one promoted rather than inherited. The original
 * five-trade build order ran out at trade #6; framing was promoted at #7 by the
 * INTERFACE MATRIX rule — the next family is whichever unserved party the most
 * served trades already chase. On that same table the roofer is named by three
 * served trades independently (EC, HVAC, PC), the highest count left once the
 * framer was served, and the rule is applied here exactly as it was written.
 *
 * IT IS ALSO THE SHAPE THIS PROGRAM IS ALREADY GOOD AT. Every other trade races
 * a gate somebody else owns. The roofer OWNS one — DRY-IN — and the whole job
 * waits on it. A trade whose calendar is a gate other people are counting down
 * to is a trade whose paperwork is all deadlines and handoffs, which is what the
 * four shared engines emit.
 *
 * ONE FAMILY, TWO HALVES, ON PURPOSE — the framing precedent, applied again.
 * Commercial low-slope (single-ply, mod-bit, BUR, tapered insulation, edge metal)
 * and residential steep-slope (shingle, metal, tile, underlayment, flashing) are
 * one population here. Where the halves differ the DATA carries both words. A
 * page that speaks only low-slope tells half this trade it was not written for
 * them, and the reverse is just as true.
 *
 * WHY THIS TRADE GETS THE HARDEST SAFETY EDGE IN THE PROGRAM. Roofing is a
 * WARRANTY-AND-LITIGATION trade. An assembly detail that LOOKS authoritative on
 * a phone — an uplift rating, a fastener pattern, a slope minimum, a listed
 * assembly, a warranty term — is not a helpful default here, it is evidence in
 * somebody's lawsuit. Nothing in this toolkit rates, sizes, specifies or grades
 * anything. The roofer states what is there; the manufacturer's spec, the
 * approved detail and the AHJ own what it is supposed to be. See items.js.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the roofing kit.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to.
  slug: "roofing",

  name: "Roofing Field Toolkit",

  // A LADDER, not a house. Every sibling's icon is the GEAR the trade carries
  // (🧰 🔧 ⚡ ❄️ 📹 🦺 🪚), never the thing it builds — a house glyph would be the
  // only building on the rack and would read as "real estate" at chip size.
  icon: "🪜",

  // ONE WORD, like every sibling — the nav brand is the trade WORD, not the full
  // name. "Roofing" is seven characters, the same as "Framing", which was
  // measured live at 390px and fits every phone the program supports.
  brandLead: "Roofing",
  brandTail: "Field Toolkit",

  /* MARKING-PAINT ROSE. Layout on a white membrane is snapped and sprayed in
     fluorescent pink or orange because nothing else shows on white TPO in full
     sun — it is the one colour this trade puts on a roof on purpose. Orange was
     gone (low-voltage coral #FF9E80, plumbing copper #C87137), so this takes the
     pink.
     IT IS ALSO THE ONLY BAND LEFT, and that was measured, not eyeballed. Hues in
     the program: low-voltage 14.2° · plumbing 24.0° · AV 45.7° · commons 90.0° ·
     GC 104.2° · HVAC/R 166.8° · electrical 200.8° · framing 247.3°. The single
     open arc runs 247°→14° and this sits at 330°, dead in it — 44.5° from its
     nearest neighbour, wider than the 21.7° that already separates plumbing from
     AV.
     CONTRAST MEASURED AGAINST THE THREE BARS THIS PROGRAM HOLDS, not guessed:
     accent on the #242A31 nav 7.08:1 (bar 7) · accentInk sitting on the accent
     9.09:1 (bar 9) · white on accentDeep 5.96:1 (bar 5). Hand-picked rather than
     computed at runtime — color-mix() is not safe on the old Android browsers
     these pages land on. */
  accent: "#FF93C9",
  accentInk: "#260817",
  accentDeep: "#B03171",
  accentTint: "#FBE6F1",

  chain: "roofers and service techs / foremen and leads / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Roofer / Mechanic / Service"],
    ["project_manager", "Foreman / Lead"],
    ["leadership", "Super / PM / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Penetration count — pipe boots, curbs, drains, pitch pans",
  wishPurposeHint: "e.g. Walk the roof once and send the office a real count of every penetration by type and size, instead of guessing off the plan and eating the difference on change orders…"
};
