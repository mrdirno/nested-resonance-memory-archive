/* FRAMING & DRYWALL FIELD TOOLKIT — the trade config.
 *
 * TRADE #7, and the first one NOT on the original five-trade build order
 * (av/AV_SOCIETY.md §TRADE EXPANSION). It was promoted by an INTERFACE EDGE
 * discovered from the trades already served: five of the six shipped toolkits
 * name the framer / drywall crew as the party they chase — AV wants backing and
 * a wall left clear, EC wants his boxes not cut, HVAC wants a louver opening,
 * plumbing wants the wet wall furred out, low-voltage wants blocking before
 * rock. The most-named receiver in the whole program was served by nothing, and
 * every rough-in-request page we ship points at a man with no toolkit.
 *
 * ONE FAMILY, TWO HALVES, ON PURPOSE. Commercial metal stud and residential wood
 * framing are one sub on most jobs and one population here. Where the halves
 * differ the DATA carries both words — blocking (wood) and backing (commercial)
 * are the same thing and both are printed everywhere, because a page that says
 * only one of them tells half this trade it was not written for them.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the framing
 * toolkit.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to.
  slug: "framing",

  name: "Framing & Drywall Field Toolkit",
  icon: "🪚",
  // ONE WORD, like every sibling — the nav brand is the trade WORD, not the full
  // name (GC ships "GC" against a name of "GC & Site Super Toolkit"). MEASURED
  // LIVE at 390px: "Framing & Drywall" rendered as "FR". At 83px "Framing" is
  // the same width as "Plumbing" and fits on every phone the program supports.
  brandLead: "Framing",
  brandTail: "Field Toolkit",

  /* CHALK-LINE BLUE, pushed to the indigo end. The snap line is the first thing
     that exists on a bare floor and the chalk box is the one tool both halves of
     this family carry. Straight cyan-blue is electrical (#3FB6F5), so this sits
     in the violet-blue band, the only hue family the program had left: AV gold
     #F0BE1E · plumbing copper #C87137 · electrical #3FB6F5 · HVAC/R mint #4FE0C0
     · low-voltage coral #FF9E80 · GC safety green #8CE86B · commons grey #BABEB6.
     MEASURED, not eyeballed: accent 7.1:1 on the #242A31 nav · accentInk 9.0:1
     sitting on the accent · white on accentDeep 8.5:1, well clear of the 5:1 the
     deep pair exists to hold. Hand-picked rather than computed — color-mix() is
     not safe on the old Android browsers these pages land on. */
  accent: "#B7ADFF",
  accentInk: "#14103A",
  accentDeep: "#4A3BA8",
  accentTint: "#EFEDFF",

  chain: "framers, hangers and tapers / leads and foremen / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Framer / Hanger / Taper"],
    ["project_manager", "Foreman / Lead"],
    ["leadership", "GF / PM / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Bead & trim picker — corner, bullnose, L, J, reveal",
  wishPurposeHint: "e.g. Tell the yard exactly what bead and how many sticks per floor in one text instead of three phone calls — types, lengths, and which corners they're for…"
};
