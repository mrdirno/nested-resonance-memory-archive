/* CREATIVE FIELD TOOLKIT — the trade config.
 *
 * TRADE #9, and the first one that is not a construction trade. It was not
 * promoted off the INTERFACE MATRIX like framing and roofing — it arrived as a
 * WISH, and the wish is the highest rung there is:
 *
 *   "Tools for creatives like the gen art collage maker striving to surpass
 *    capcut — what else creative aspect can we revolutionize democratize […]
 *    follow the nursery algorithm […] nursery algorithm is the marriage
 *    algorithm."
 *
 * THE MARRIAGE IS THE POINT. This program owns five document ENGINES — the
 * checklist→request, the note, the row log, the reconcile and the docspec —
 * extracted from eight construction trades. A creative's week is the SAME five
 * documents wearing different words: the kit you pull before a shoot is a
 * consumables list; the round the client slid past the deal is an extra-work
 * tag; the four things you are waiting on before you can deliver is a row log;
 * the wall of notes they emailed you is somebody else's list to answer line by
 * line. Nothing new had to be built to serve this trade. That is the whole
 * claim of one runtime, many trades, and this is its widest test.
 *
 * WHO THIS IS. The one-person shop and the small studio: freelance shooters,
 * editors, motion and graphic designers, photographers, the content person
 * inside a marketing team. NOT the studio system — a show with a UPM, a post
 * supervisor and a delivery spec from a network already has software that owns
 * and NUMBERS every document, and this program never competes with whoever owns
 * the document. This is for the person who is also their own producer.
 *
 * WHAT IT MUST NEVER DO, and the edge is sharper here than it looks. A creative
 * page that "helps" by printing a delivery spec, a codec, a bitrate, a platform's
 * current maximum, a licence term, a usage window or a day rate is asserting an
 * external standard we do not hold and cannot stand behind — and every one of
 * those changes without telling us. The user states the spec; the client's own
 * delivery sheet, the platform's own docs and the licence they actually bought
 * own what it is supposed to be. See items.js.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the creative kit.
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
  // loop knows which toolkit a request belongs to. Lowercase slug, matches the dir.
  slug: "creative",

  name: "Creative Field Toolkit",

  /* THE GEAR, NOT THE OUTPUT — the sibling law (🧰 🔧 ⚡ ❄️ 📹 🦺 🪚 🪜). A film
     strip or a paint palette would be the thing this trade MAKES, which is the
     mistake the roofing config caught itself making with a house glyph. A slate
     is a tool you carry, hand somebody and shoot. 📹 was already spent on
     low-voltage, where a camera means CCTV. */
  icon: "🎬",

  // ONE WORD, like every sibling — the nav brand is the trade WORD. "Creative"
  // is eight characters; "Electrical" (ten) is the measured worst case and fits.
  brandLead: "Creative",
  brandTail: "Field Toolkit",

  /* GEL PURPLE, and it is the last wide band on the wheel. Hues already spent:
     low-voltage 14.2° · plumbing 24.0° · AV 45.7° · commons 90.0° · GC 104.2° ·
     HVAC/R 166.8° · electrical 200.8° · framing 247.3° · roofing 330.0°. The one
     arc wider than 62° runs 247.3°→330.0° (82.7°) and this sits at 288.0°, its
     exact midpoint — 40.7° off framing and 42.0° off roofing, both wider than the
     21.7° that already separates plumbing from AV.
     It is also the one colour this trade owns on purpose: a purple gel on the
     background light is the single most-used look in the small-shop toolkit,
     and no crew has ever hung one on a jobsite.
     CONTRAST MEASURED AGAINST THE THREE BARS THIS PROGRAM HOLDS, not guessed:
     accent on the #242A31 nav 7.88:1 (bar 7) · accentInk sitting on the accent
     10.74:1 (bar 9) · white on accentDeep 7.39:1 (bar 5) · accentDeep as text on
     the #FBFBF8 paper 7.12:1. Hand-picked rather than computed at runtime —
     color-mix() is not safe on the old Android browsers these pages land on. */
  accent: "#EDA5FF",
  accentInk: "#190022",
  accentDeep: "#8B12B4",
  accentTint: "#F8EAFD",

  chain: "shooters and editors / producers and creative leads / the client",

  /* The four VALUES are CHECK-constrained in the DB (migration 075) — relabelled
     for this trade, but the values stay tech / project_manager / leadership /
     other. "Tech" is the person with their hands on the timeline or the camera,
     which is the same role every other kit gives it. */
  roles: [
    ["tech", "Shooter / Editor / Designer"],
    ["project_manager", "Producer / Creative lead"],
    ["leadership", "Studio owner / Freelance principal"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. Round tag — what they asked for after sign-off",
  wishPurposeHint: "e.g. The client keeps sliding “one small thing” in after the round we agreed on, and I never write it down until I'm three days over. Tag it the day they ask — who asked, what it actually was, and what it did to the delivery date…"
};
