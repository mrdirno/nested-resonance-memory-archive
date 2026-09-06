/* PLUMBING FIELD TOOLKIT — the trade config.
 *
 * The SECOND trade (av/AV_SOCIETY.md §TRADE EXPANSION). Note what is NOT here:
 * a copy of the runtime. shared/toolkit.js is trade-agnostic and this file is the
 * whole of what makes it the plumbing toolkit — name, brand, accent, handoff
 * chain, role labels, wish prompts. One runtime, many trades.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to.
  slug: "plumbing",

  name: "Plumbing Field Toolkit",
  icon: "🔧",
  brandLead: "Plumbing",
  brandTail: "Field Toolkit",
  accent: "#CE7F4B",    // copper
  accentInk: "#1A0E05", // readable text ON the copper
  // THE DEEP PAIR — the DARK and PALEST ends of this trade's own hue, added when
  // shape #2's engine (shared/note.js + shared/note.css) went to one stylesheet
  // across six trades. `accent` is light and high-chroma because it lives on the
  // dark nav; it cannot be a border, a heading or text on paper. `accentDeep` is
  // that job (white text on it clears 5:1) and `accentTint` fills the impact
  // block. Hand-picked, not computed — color-mix() is not safe on the old
  // Android browsers these pages land on.
  accentDeep: "#7A3F12",
  accentTint: "#FBEFE3",

  chain: "plumbers / foremen / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Plumber / Service Tech"],
    ["project_manager", "Foreman / PM"],
    ["leadership", "Owner / Office"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Shutdown notice — what's off, where, when, who to call",
  wishPurposeHint: "e.g. Standing at the valve I need to send the GC and the building engineer a water shutdown notice — affected areas, isolation point, times, and a callback number — without going back to the truck to edit last month's email…"
};
