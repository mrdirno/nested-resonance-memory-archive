/* MASONRY FIELD TOOLKIT — the trade config.
 *
 * TRADE #11, and the FOURTH promoted by the INTERFACE MATRIX rule rather than
 * inherited from the original five-trade build order. Three served kits name
 * this crew as a receiver in their own `who[]` arrays on disk — electrical
 * ("Mason / CMU"), plumbing ("Mason") and roofing ("Mason / chimney") — and TWO
 * of them wrote his day into their own countdowns in their own words:
 *   electrical/items.js  { v: "cmucap",   label: "Before CMU caps out" }   3rd of 7
 *   plumbing/items.js    { v: "block-up", label: "Before block goes up" }  3rd of 8
 * Each of those milestones carries an ask bound to it — EC's `blockboxes`
 * ("Set my boxes as you lay it" · "Run my pipe up the cell" · "Leave the cell
 * open above my box" · "Don't grout the cell I'm in" · "Pipe under the bond
 * beam" · "Call me the morning of that lift") and PC's `sleeve-block` ("Sleeve
 * laid in as you go up" · "Chase in the block for my stack" · "Leave the cell
 * open — don't grout it" · "Knock-out at my paint mark"). Twelve spec lines
 * aimed at a man with no page to answer them on. That is the exact condition
 * concrete/trade.js gives as the reason trade #10 was promoted, one trade over.
 *
 * HE OWNS THE GATE, HE DOES NOT RACE IT. Every other trade counts down to
 * BLOCK UP / CMU CAPS OUT; the mason sets the date. Once the wall caps and the
 * bond beam grouts, a box, a sleeve, a conduit stub or a lintel pocket is a
 * core bit through grout and rebar — and on a structural wall, a call to the
 * engineer of record before anybody starts a saw.
 *
 * THE COUNT DID NOT PICK THIS TRADE ON ITS OWN, AND THE RECORD SHOULD SAY SO.
 * Re-tallied off all ten shipped items.js files, STEEL is named by four kits
 * and masonry by three. Steel was killed on §THE INTERFACE's own prune, which
 * threw out "a special-inspection record" by name: the bolt-up/torque log, the
 * weld map, the WPS and the mill cert ARE that record, and they are not steel's
 * edge case, they are its centre. Ceilings was killed by a sentence this
 * program had already written — concrete/trade.js says "a wall can be cut, A
 * CEILING CAN BE PULLED" while explaining what an irreversible gate is, and
 * ceilings' whole case was owning the most-NAMED gate rather than a one-way
 * one. Both kills are recorded in av/AV_SOCIETY.md with the dissent intact:
 * masonry is the smallest working population of the three and it is
 * receiver-heavy / ask-light, which is a real weakness of this kit and not a
 * thing to paper over.
 *
 * NO FORK, VERIFIED RATHER THAN ASSUMED: concrete/items.js returns ZERO hits
 * for cmu / mortar / brick / veneer / tuckpoint — every "block" in that file is
 * `blockout` or `blocking`. Different NAICS (238140 vs 238110), different local
 * (BAC vs OPCMIA), different act: a mason lays cured units in mortar, a
 * finisher places plastic concrete.
 *
 * WHAT THIS TRADE IS NOT ALLOWED TO SHIP, decided before a line was written and
 * for the same reason concrete killed every admixture dose field. Mortar TYPE
 * (M/S/N/O) and C270 proportions · grout lift heights · rebar size, lap and
 * cover · lintel bearing length · joint-reinforcement spacing · cold-weather
 * protection temperatures · rated-wall assembly numbers · the silica table for
 * tuckpointing · and above all CONSTRUCTION-PHASE WALL BRACING HEIGHT, which is
 * engineered, kills people when it is wrong, and would become a bracing DESIGN
 * the moment it was a field on a phone. Not as a value, not as a default, not
 * as a placeholder. He states what he has off his own submittal and his own
 * drawings; the engineer of record owns what it is supposed to be.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the masonry kit.
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
  slug: "masonry",

  name: "Masonry Field Toolkit",

  /* THE ONE PLACE THE SIBLING RULE BENDS, AND IT BENDS ON ITS OWN AUTHOR'S
     WORDS. Every icon on this rack is GEAR the trade carries (🧰 🔧 ⚡ ❄️ 📹 🦺
     🪚 🪜 🎬 🪣), never the thing it builds — a rule written into
     concrete/trade.js, in a sentence that also says "a brick would read as
     masonry and a slab does not have a glyph." It conceded this glyph to this
     trade while explaining why it could not have one of its own.

     The bend is forced, not preferred. A mason's gear is a trowel, a line and
     blocks, a jointer, a story pole and a bolster — not one of them has a glyph
     in the set. 🔨 exists and a brick hammer is real gear, but at chip size it
     reads as carpentry to everyone who is not holding one. A rack chip has one
     job: the man whose trade it is finds it without reading. */
  icon: "🧱",

  // ONE WORD, like every sibling. "Masonry" is seven characters; "Electrical"
  // is ten and has shipped at 390px since trade #3.
  brandLead: "Masonry",
  brandTail: "Field Toolkit",

  /* THE TRADE'S OWN COLOUR IS NOT AVAILABLE, AND THAT IS A MEASUREMENT, NOT A
     PREFERENCE. Brick red is the obvious accent and it fails twice. It collides
     with the band this rack already crowds — low-voltage coral at hue 14.2 and
     plumbing copper at 24.0, which is itself a fired-clay brown — and, more
     decisively, RED CANNOT CLEAR THE CONTRAST BAR AT ALL. Measured across the
     whole lightness range at hue 352 against the #242A31 nav: L50 3.64 · L55
     3.76 · L60 4.02 · L65 4.48 · L70 5.12 · L75 6.03. It never reaches 7, and
     the only way to get there is L78+, which is a pale rose sitting between
     roofing's pink (330.0, L79) and low-voltage's coral (14.2, L75) — a third
     pastel in a row, which is the one outcome the rack cannot afford. The
     trade's other materials are grey (block, mortar) and buff (sand); the
     commons owns the grey band and an accent needs chroma.

     SO THE ACCENT GOES TO THE TOOL INSTEAD OF THE MATERIAL: the LINE. A mason
     builds the leads and then works to the line, and line comes in fluorescent.

     THE HUE WAS MEASURED, NOT EYEBALLED — the roofing and concrete precedent,
     run again with eleven chips on the rack. Hues in the program: low-voltage
     14.2 · plumbing 24.0 · AV 45.7 · GC 104.2 · concrete 135.2 · HVAC/R 166.8 ·
     electrical 200.8 · framing 247.3 · creative 288.0 · roofing 330.0 (the
     commons chip is #BABEB6 — nominally hue 90 but 4% saturation, a grey, and
     treating a grey as occupying 90 degrees of the wheel is how a rack talks
     itself out of its widest opening). That leaves 45.7 -> 104.2 at 58.5
     degrees as the widest genuinely chromatic arc on the circle, and this sits
     at 75.0, dead in the middle: 29.3 off AV and 29.2 off GC, wider than the
     21.7 that already separates plumbing from AV and three times the 9.8
     between low-voltage and plumbing. It is also a full step darker than the GC
     lime (HSL L 0.52 against 0.66) and far more saturated than the AV gold is
     green, so no two of the three read as one chip on a phone in the sun.

     CONTRAST MEASURED AGAINST THE THREE BARS THIS PROGRAM HOLDS, not guessed:
     accent on the #242A31 nav 10.55:1 (bar 7) · accentInk sitting on the accent
     11.74:1 (bar 9) · white on accentDeep 5.92:1 (bar 5). Hand-picked rather
     than computed at runtime — color-mix() is not safe on the old Android
     browsers these pages land on. */
  accent: "#B9EE1B",
  accentInk: "#1C2405",
  accentDeep: "#566C13",
  accentTint: "#F3FAE1",

  // LAYERS AND TENDERS, and the second word is not decoration. The tender mixes
  // the mud and keeps the layers stocked; he is not a helper and he is not an
  // apprentice, and a kit that calls him one is not written for this crew.
  chain: "layers and tenders / foremen and leads / the office",

  // The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
  // for this trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Layer / Tender / Pointer"],
    ["project_manager", "Foreman / Lead"],
    ["leadership", "Super / PM / Owner"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Lift card — what has to be in this wall before I cap it",
  wishPurposeHint: "e.g. Four trades want something in this wall and every one of them told me on a different day, on the phone, at a different course. I want one list per wall I can walk with, tick as I lay, and send back so nobody says later that they told me…"
};
