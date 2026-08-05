/* GC / SITE SUPER FIELD TOOLKIT — the trade config.
 *
 * The SIXTH trade, and the last family owed one on the ladder (av/AV_SOCIETY.md
 * §TRADE EXPANSION, §THE EXPANSION ORDER: "every trade family on the ladder gets a
 * real toolkit before any trade already served gets polished"). Same as trades
 * #2-#5: there is no copy of the runtime in this directory. shared/toolkit.js is
 * trade-agnostic and THIS file is the whole of what makes it the GC toolkit —
 * name, brand, accent, handoff chain, role labels, wish prompts.
 * One runtime, many trades.
 *
 * WHY GC WENT LAST, ON PURPOSE. Every other trade sends its paperwork UP to the
 * GC. Build GC first and you are writing the receiving end of documents that do
 * not exist yet. Build it sixth and the whole ladder below it is already speaking
 * — which is also why this trade is where the INTERFACE axis finally has two real
 * ends to connect.
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
  slug: "gc",

  name: "GC & Site Super Toolkit",
  icon: "🦺",

  // "GC" and not "General Contracting": the nav bar is the single most
  // overflow-prone surface on a phone (§SCARS — the bar measured 433-489px in a
  // 390px viewport across every trade), and the brand is the piece that gives up
  // its tail first. A two-letter lead is the shortest true name this trade has,
  // and it is what a super types in a group chat.
  brandLead: "GC",
  brandTail: "Field Toolkit",

  // THE ACCENT HAS A JOB, not just a look (§SCARS — "the trade accent is painted
  // on a dark bar"). It is painted onto the DARK steel nav (brand tail, the
  // favourite ★, focus rings, the bar's bottom rule) AND used as a button fill
  // that carries `accentInk` as its text. So it has to be LIGHT and high-chroma.
  // Measured against the #242A31 bar: 9.28:1 for the accent on the bar · 10.6:1
  // for accentInk sitting on the accent.
  //
  // Hi-vis site green — the vest every super on every job is required to wear,
  // which makes it this trade's own colour rather than a colour assigned to it.
  // Placed at hue ~104°, deliberately between AV amber (46°) and HVAC mint (168°)
  // and far from plumbing copper (25°), electrical sky (199°) and LV coral (14°),
  // so six trades stay tellable apart at a glance in a tab strip.
  accent: "#8CE86B",
  accentInk: "#0C2405", // readable text ON the accent

  // Who the super is standing between. Every other trade in this toolkit sends
  // its paperwork UP to him; he sends his UP again, and sideways to the subs.
  chain: "supers / PMs / owners / subs",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Superintendent / Foreman"],
    ["project_manager", "PM / Estimator"],
    ["leadership", "Owner / Office"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Pre-cover notice — who has to be in the wall before it closes",
  wishPurposeHint: "e.g. I walk the building twice a day and the same three things stop work every time, and by the time I'm back in the trailer at 5 I'm typing the same message to the same four subs from memory. I want to stand in the room, tick what I saw, name who owns it and what it's holding up, and send one thing the PM can actually answer instead of a paragraph he has to call me about…"
};
