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
  accent: "#C87137",    // copper
  accentInk: "#1A0E05", // readable text ON the copper

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
