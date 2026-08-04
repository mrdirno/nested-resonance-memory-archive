/* HVAC/R FIELD TOOLKIT — the trade config.
 *
 * The FOURTH trade (av/AV_SOCIETY.md §TRADE EXPANSION). Same as trades #2 and #3:
 * there is no copy of the runtime in this directory. shared/toolkit.js is
 * trade-agnostic and THIS file is the whole of what makes it the HVAC toolkit —
 * name, brand, accent, handoff chain, role labels, wish prompts. One runtime,
 * many trades.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to. Lowercase, matches the dir.
  // "hvac", not "hvacr": it is what people type and what the URL has to read like.
  // The visible brand carries the /R, because in commercial the refrigeration
  // guys are half the trade and a toolkit that forgets them is an air-side toy.
  slug: "hvac",

  name: "HVAC/R Field Toolkit",
  icon: "❄️",
  brandLead: "HVAC/R",
  brandTail: "Field Toolkit",

  // THE ACCENT HAS A JOB, not just a look (§SCARS — "the trade accent is painted
  // on a dark bar"). It is painted onto the DARK steel nav (brand tail, the
  // favourite ★, focus rings, the bar's bottom rule) AND used as a button fill
  // that carries `accentInk` as its text. So it has to be LIGHT and high-chroma.
  // Measured against #242A31: 8.8:1 for the accent on the bar · 9.8:1 for
  // accentInk sitting on the accent.
  // Gauge mint — the cold side of the trade, and far enough around the wheel from
  // AV yellow (#F0BE1E), plumbing copper (#C87137) and electrical blue (#3FB6F5)
  // to name the trade at a glance in a tab strip.
  accent: "#4FE0C0",
  accentInk: "#052622", // readable text ON the accent

  chain: "techs / service managers / dispatch",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Service Tech / Refrig"],
    ["project_manager", "Service Manager / Dispatch"],
    ["leadership", "Owner / Office"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Evac record — micron readings with the clock filling itself",
  wishPurposeHint: "e.g. I find something on a PM that we're not fixing today, and the office has to quote it. I need to send the unit tag, what's actually on the data plate, the part off the failed component, what happens if they sit on it, and how we're getting up there — from the roof, in about a minute, without a phone call the next day…"
};
