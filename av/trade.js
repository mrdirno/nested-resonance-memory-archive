/* AV FIELD TOOLKIT — the trade config.
 *
 * ONE RUNTIME, MANY TRADES (av/AV_SOCIETY.md §TRADE EXPANSION). shared/toolkit.js
 * is trade-agnostic; THIS file is what makes it the AV toolkit. To stand up a new
 * trade, copy this file into <trade>/trade.js, change the values, and write that
 * trade's tools.js — never copy the runtime.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish (migration 076) — this is how the
  // loop knows which toolkit a request belongs to. Lowercase slug, matches the dir.
  slug: "av",

  name: "AV Field Toolkit",
  icon: "🧰",
  brandLead: "AV",          // rendered plain
  brandTail: "Field Toolkit", // rendered bold in the accent colour
  accent: "#F0BE1E",        // the AV flag yellow
  accentInk: "#231B00",     // readable text ON the accent
  // THE DEEP PAIR — the DARK and PALEST ends of this trade's own hue, added when
  // shape #2's engine (shared/note.js + shared/note.css) went to one stylesheet
  // across six trades. `accent` is light and high-chroma because it lives on the
  // dark nav; it cannot be a border, a heading or text on paper. `accentDeep` is
  // that job (white text on it clears 5:1) and `accentTint` fills the impact
  // block. Hand-picked, not computed — color-mix() is not safe on the old
  // Android browsers these pages land on.
  accentDeep: "#7A5A05",
  accentTint: "#FDF4DC",

  // Who this trade's handoff chain is — used in the wishing-well copy
  // ("the real terms, shortcuts and formats your ___ already use").
  chain: "techs / PMs / leadership",

  // The four VALUES are CHECK-constrained in the DB (migration 075); a trade may
  // relabel them but must keep tech / project_manager / leadership / other.
  roles: [
    ["tech", "AV Tech"],
    ["project_manager", "Project Manager"],
    ["leadership", "Leadership / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Cable-types picker — HDMI / patch / fiber",
  wishPurposeHint: "e.g. Pick the exact cables for a job and copy a clean spec to send my PM — HDMI (2.0/2.1, lengths), Cat patch (5e/6/6a), fiber (OM3/OM4/OS2, connector types)…"
};
