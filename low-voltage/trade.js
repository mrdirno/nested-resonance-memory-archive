/* LOW-VOLTAGE / SECURITY / FIRE FIELD TOOLKIT — the trade config.
 *
 * The FIFTH trade (av/AV_SOCIETY.md §TRADE EXPANSION). Same as trades #2-#4:
 * there is no copy of the runtime in this directory. shared/toolkit.js is
 * trade-agnostic and THIS file is the whole of what makes it the low-voltage
 * toolkit — name, brand, accent, handoff chain, role labels, wish prompts.
 * One runtime, many trades.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076 — a bounded
  // lowercase slug, NOT an enum, so a new trade needs no migration). This is how
  // the loop knows which toolkit a request belongs to. Matches the dir exactly.
  // "low-voltage", not "lv": the URL has to read like something, and a wish
  // arriving from a stranger's phone should name a trade a human recognises.
  slug: "low-voltage",

  name: "Low-Voltage Field Toolkit",
  icon: "📹",
  brandLead: "Low-Voltage",
  brandTail: "Field Toolkit",

  // THE ACCENT HAS A JOB, not just a look (§SCARS — "the trade accent is painted
  // on a dark bar"). It is painted onto the DARK steel nav (brand tail, the
  // favourite ★, focus rings, the bar's bottom rule) AND used as a button fill
  // that carries `accentInk` as its text. So it has to be LIGHT and high-chroma.
  // Measured against #242A31: 7.2:1 for the accent on the bar · 9.1:1 for
  // accentInk sitting on the accent.
  // Signal coral — the alarm/strobe end of the spectrum, which is this trade's
  // own colour, but LIGHT enough to read on dark steel where a fire-alarm red
  // would go muddy. Far enough around the wheel from AV yellow (#F0BE1E),
  // plumbing copper (#C87137), electrical blue (#3FB6F5) and HVAC mint (#4FE0C0)
  // to name the trade at a glance in a tab strip.
  accent: "#FF9E80",
  accentInk: "#2B0A02", // readable text ON the accent

  chain: "installers / foremen / PMs / commissioning",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Installer / Tech"],
    ["project_manager", "Foreman / PM"],
    ["leadership", "Owner / Office"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Pull sheet — cable type and count per run, off the same table as the device list",
  wishPurposeHint: "e.g. At the end of a 240-device job somebody has to hand the PM the device list, and it lives on a marked-up plan set and in my head. I want to log each one as I hang it — tag, where it is, what it homes back to, whether it's terminated or tested — and send a clean list plus something the office can paste into their spreadsheet, without a night in Excel…"
};
