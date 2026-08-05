/* ELECTRICAL FIELD TOOLKIT — the trade config.
 *
 * The THIRD trade (av/AV_SOCIETY.md §TRADE EXPANSION). Same as trade #2: there is
 * no copy of the runtime in this directory. shared/toolkit.js is trade-agnostic
 * and THIS file is the whole of what makes it the electrical toolkit — name,
 * brand, accent, handoff chain, role labels, wish prompts. One runtime, many
 * trades.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to. Lowercase, matches the dir.
  slug: "electrical",

  name: "Electrical Field Toolkit",
  icon: "⚡",
  brandLead: "Electrical",
  brandTail: "Field Toolkit",

  // THE ACCENT HAS A JOB, not just a look. It is painted onto the DARK steel nav
  // bar (brand tail, the favourite ★, focus rings, the bar's bottom rule) AND
  // used as a button fill that carries `accentInk` as its text. So it has to be
  // LIGHT and high-chroma, or the nav goes unreadable the moment the trade
  // changes — which is exactly what a deep navy would have done here.
  // 6.1:1 on the #242A31 bar · 7.1:1 for accentInk sitting on it.
  accent: "#3FB6F5",    // electric blue — distinct at a glance from AV yellow and plumbing copper
  accentInk: "#06212E", // readable text ON the accent
  // THE DEEP PAIR — the DARK and PALEST ends of this trade's own hue, added when
  // shape #2's engine (shared/note.js + shared/note.css) went to one stylesheet
  // across six trades. `accent` is light and high-chroma because it lives on the
  // dark nav; it cannot be a border, a heading or text on paper. `accentDeep` is
  // that job (white text on it clears 5:1) and `accentTint` fills the impact
  // block. Hand-picked, not computed — color-mix() is not safe on the old
  // Android browsers these pages land on.
  accentDeep: "#0A5C87",
  accentTint: "#E4F4FD",

  chain: "electricians / foremen / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Electrician / JW"],
    ["project_manager", "Foreman / GF"],
    ["leadership", "Owner / Office"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. T&M ticket — directed by, what I found, men and hours",
  wishPurposeHint: "e.g. The super pulls me off my work and tells me to do something that isn't on the drawings. I need to send it that same day with who directed it, when, what it stopped, and the men and hours — no prices, and something he can just reply APPROVED to…"
};
