/* AV FIELD TOOLKIT — VOCABULARY DATA (cables & adapters).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Length ladders,
 * spec tiers and connector families live HERE — never in the identity config and
 * never inline in a tool page.
 *
 * TWO HARD INVARIANTS, both of them safety rules (§SAFETY):
 *
 *  1. ZERO BRAND NAMES. Not one, anywhere in this file. The tech types whose
 *     finish cable his shop runs into a single header field; the tool repeats his
 *     words back. That one rule makes it structurally impossible for this page to
 *     impersonate a product line or to imply that two manufacturers' parts are
 *     equivalent.
 *  2. NOTHING IS COMPUTED OR RATED. Every value below is something a tech PICKS.
 *     No ampacity, no bandwidth-vs-length limit, no "this cable will do 4K at that
 *     distance". The one place the data leans on knowledge is a plain-language
 *     `sub` hint on a line where the wrong part is famously ordered (a one-way
 *     adapter, a charge-only cord) — a wrong-order preventer written on the line,
 *     the same register as "double-check before you order", never a rule engine.
 *
 * ORDERED IN THE UNITS THEY ARE BOUGHT IN: copper patch in feet, fiber in metres,
 * long AOC in feet with the metric length in parentheses because that is how the
 * part is listed. Do not normalize this — it is how a counter looks it up.
 */
window.TOOLKIT_ITEMS = (function () {
  "use strict";

  /* ── length ladders — real stocked lengths, not a range generator ────────── */
  var LEN_HDMI = ["3 ft", "6 ft", "9 ft", "10 ft", "12 ft", "15 ft", "20 ft", "25 ft", "30 ft", "35 ft", "50 ft", "1 ft"];
  var LEN_ACTIVE = ["25 ft", "30 ft", "35 ft", "50 ft", "60 ft", "75 ft", "100 ft"];
  var LEN_AOC = ["15 ft", "25 ft", "33 ft (10 m)", "50 ft", "66 ft (20 m)", "100 ft (30 m)", "130 ft (40 m)", "165 ft (50 m)", "200 ft (60 m)", "250 ft", "300 ft (100 m)"];
  var LEN_PATCH = ["6 in", "1 ft", "2 ft", "3 ft", "5 ft", "7 ft", "10 ft", "14 ft", "15 ft", "20 ft", "25 ft", "30 ft", "50 ft", "75 ft", "100 ft"];
  var LEN_USB = ["3 ft", "6 ft", "10 ft", "15 ft", "16 ft (5 m)", "25 ft", "32 ft (10 m)", "50 ft (15 m)", "65 ft (20 m)", "100 ft (30 m)", "1 ft"];
  var LEN_USB_SHORT = ["1 ft", "3 ft", "6 ft", "10 ft", "15 ft"];
  var LEN_AUD = ["3 ft", "6 ft", "10 ft", "15 ft", "20 ft", "25 ft", "50 ft", "100 ft", "1.5 ft"];
  var LEN_AUX = ["1.5 ft", "3 ft", "6 ft", "10 ft", "15 ft", "25 ft"];
  var LEN_DP = ["3 ft", "6 ft", "10 ft", "15 ft", "25 ft"];
  var LEN_DP_AOC = ["33 ft (10 m)", "50 ft", "100 ft (30 m)", "165 ft (50 m)"];
  var LEN_VGA = ["3 ft", "6 ft", "10 ft", "15 ft", "25 ft", "50 ft"];
  var LEN_DVI = ["3 ft", "6 ft", "10 ft", "15 ft"];
  var LEN_FIB = ["1 m", "2 m", "3 m", "5 m", "7 m", "10 m", "15 m", "20 m", "30 m", "50 m", "0.5 m", "custom — note the length"];
  var LEN_PWR = ["2 ft", "3 ft", "4 ft", "6 ft", "8 ft", "10 ft", "15 ft", "1 ft"];
  var LEN_PIG = ["1 ft", "3 ft", "6 ft"];
  var FORM_ADPT = ["Adapter only (no cable)", "4 in pigtail", "6 in", "8 in", "1 ft"];

  /* ── shared value sets ───────────────────────────────────────────────────── */
  // FINISH is the operator's headline axis: grade + connector PROFILE, which is
  // what actually decides whether the cable fits behind a flush display or through
  // a mount's pass-through. No brand — see invariant 1.
  var FINISH = [
    "Finish cable — molded, low-profile shell",
    "Standard install cable",
    "Rack jumper / patch",
    "Ultra-thin / flexible (tight pass-through)",
    "Right-angle end",
    "Locking / retention shell",
    "Plenum jacket (CMP)",
    "Match what's installed"
  ];
  var SPEC_HDMI = [
    "2.0 · 18 Gbps (4K60)",
    "2.1 · 48 Gbps (Ultra High Speed)",
    "Premium Certified · 18 Gbps",
    "Standard / 1080p only",
    "Match what's on the job"
  ];
  var SPEC_DP = ["DP 1.2 (4K60)", "DP 1.4 (8K / DSC)", "DP 2.1", "n/a (VGA / DVI)", "Match the device"];
  var CAT_PATCH = [
    "Cat6 U/UTP",
    "Cat5e U/UTP",
    "Cat6 F/UTP (shielded)",
    "Cat6A U/UTP",
    "Cat6A S/FTP (shielded)",
    "Match the panel / what's installed"
  ];
  // Colours mean something on a rack — but the convention is PER SHOP. Ship the
  // colours that are stocked; NEVER ship a meaning. What blue vs yellow means on
  // this job goes in the note.
  var COLOR = ["Blue", "White", "Gray", "Black", "Red", "Yellow", "Green", "Orange", "Purple", "Pink", "Whatever's in stock"];
  var SPEED_USB = [
    "USB 2.0 (480 Mbps)",
    "5 Gbps — USB 3.2 Gen 1",
    "10 Gbps — USB 3.2 Gen 2",
    "20 Gbps — USB 3.2 Gen 2×2",
    "USB4 / Thunderbolt (40 Gbps)",
    "CHARGE ONLY — no data",
    "Match the device"
  ];
  var BUILD_USB = ["Passive", "Active / repeater (powered)", "AOC / fiber", "Right-angle end", "Locking / screw-down", "Plenum jacket (CMP)"];
  var BUILD_AUD = ["Standard", "Star-quad", "Right-angle end", "Low-profile / thin"];
  var FIB_TYPE = ["OM3 (aqua)", "OM4", "OM5 (lime)", "OS2 single-mode (yellow)", "Match what's installed"];
  var FIB_CONN = ["LC–LC duplex", "LC–SC", "SC–SC", "LC–ST", "MPO–MPO", "Match the panel"];
  var GAUGE = ["16 AWG", "18 AWG", "14 AWG", "Match what's in the rack"];

  /* ── THE NEUTRAL ───────────────────────────────────────────────────────────
   * A write-in is a line the tech typed HIMSELF, and he usually types the length
   * into it ("USB-C 90° elbow, 1 ft"). If its axes then default to a real value,
   * the tool APPENDS a second length and a finish he never picked, and what the
   * counter reads is a line contradicting itself. So every write-in axis leads
   * with a neutral, and the page drops any value that starts with an em-dash.
   * The rule this enforces is the one the page is built on: nothing printed is
   * ever something the tech did not pick. */
  var NO_LEN = "— no length —";
  var NO_FIN = "— as typed —";

  function ax(label, opts, wide) { return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide }; }
  var AX_FINISH = ax("Finish", FINISH, true);
  var AX_LEN = function (l) { return ax("Length", l); };

  // Every line can be flagged for an alternate. This is the honest form of the
  // operator's "check for an alternative finish cable": we do NOT ship a
  // cross-reference claiming brand X = brand Y (we cannot stand behind that), so
  // the toggle turns the ask into the request a supplier can actually answer.
  var ALT = [{ k: "alt", label: "Want an alternate priced", def: false }];

  function I(n, axes, sub) { return { n: n, ax: axes, flags: ALT, sub: sub || "" }; }

  var cats = [
    { id: "hdmi", name: "HDMI", chip: "#2E64C8", items: [
      I("HDMI A–A", [AX_LEN(LEN_HDMI), ax("Spec", SPEC_HDMI, true), AX_FINISH]),
      I("HDMI A–A — active / powered", [AX_LEN(LEN_ACTIVE), ax("Spec", SPEC_HDMI, true), AX_FINISH], "directional"),
      I("HDMI AOC / fiber A–A", [AX_LEN(LEN_AOC), ax("Spec", SPEC_HDMI, true), AX_FINISH], "directional — source end marked"),
      I("HDMI A → mini (type C)", [AX_LEN(LEN_HDMI), ax("Spec", SPEC_HDMI, true), AX_FINISH]),
      I("HDMI A → micro (type D)", [AX_LEN(LEN_HDMI), ax("Spec", SPEC_HDMI, true), AX_FINISH]),
      I("HDMI wall-plate / panel pigtail", [AX_LEN(LEN_PIG), ax("Spec", SPEC_HDMI, true), AX_FINISH], "A female → A male")
    ]},

    { id: "patch", name: "Network / patch cords", chip: "#2E7D4F", items: [
      I("Patch cord (RJ45–RJ45)", [AX_LEN(LEN_PATCH), ax("Category", CAT_PATCH, true), ax("Color", COLOR)]),
      I("Patch cord — slim body", [AX_LEN(LEN_PATCH), ax("Category", CAT_PATCH, true), ax("Color", COLOR)], "28 AWG, dense panel"),
      I("Patch cord — angled / right-angle boot", [AX_LEN(LEN_PATCH), ax("Category", CAT_PATCH, true), ax("Color", COLOR)]),
      I("Console cable (RJ45 → USB-C / DB9)", [AX_LEN(["6 ft", "10 ft"]), ax("Color", COLOR)])
    ]},

    { id: "usb", name: "USB", chip: "#7A3FA8", items: [
      I("USB-A → USB-B (device)", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-A → USB-B 3.0 (blue)", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-A → USB-C", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-C → USB-C", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)], "say the wattage in the note if it has to charge"),
      I("USB-C → USB-B", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-C → USB-B 3.0 (blue)", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-A → micro-B", [AX_LEN(LEN_USB_SHORT), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-A → mini-B", [AX_LEN(LEN_USB_SHORT), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)]),
      I("USB-A → USB-A extension", [AX_LEN(LEN_USB), ax("Speed", SPEED_USB, true), ax("Build", BUILD_USB)])
    ]},

    { id: "adapt", name: "Adapters & dongles", chip: "#C87137", items: [
      I("USB-C → HDMI", [ax("Form", FORM_ADPT, true)]),
      I("USB-C multiport dongle", [ax("Form", FORM_ADPT, true)], "HDMI + USB-A + PD"),
      I("USB-C → DisplayPort", [ax("Form", FORM_ADPT, true)]),
      I("USB-C → RJ45", [ax("Form", FORM_ADPT, true)]),
      I("Mini-DP → HDMI", [ax("Form", FORM_ADPT, true)]),
      I("DisplayPort → HDMI (active)", [ax("Form", FORM_ADPT, true)], "one-way part — HDMI→DP is a different device"),
      I("HDMI → VGA (active)", [ax("Form", FORM_ADPT, true)], "one-way part — with 3.5 mm audio out"),
      I("HDMI coupler (F–F)", [ax("Form", FORM_ADPT, true)]),
      I("HDMI right-angle / swivel adapter", [ax("Form", FORM_ADPT, true)]),
      I("HDMI A → mini / micro adapter", [ax("Form", FORM_ADPT, true)]),
      I("USB-A ↔ USB-C adapter", [ax("Form", FORM_ADPT, true)]),
      I("RJ45 coupler (inline joiner)", [ax("Form", FORM_ADPT, true)]),
      I("XLR turnaround (M–M / F–F)", [ax("Form", FORM_ADPT, true)])
    ]},

    { id: "audio", name: "Audio", chip: "#B0201A", items: [
      I("XLR M–F (mic cable)", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("XLR M → 1/4\" TRS", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("1/4\" TRS – TRS (balanced)", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("1/4\" TS (instrument)", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("3.5 mm TRS – TRS (aux)", [AX_LEN(LEN_AUX), ax("Build", BUILD_AUD, true)]),
      I("3.5 mm TRS → dual RCA", [AX_LEN(LEN_AUX), ax("Build", BUILD_AUD, true)]),
      I("3.5 mm TRS → dual 1/4\" TS", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("3.5 mm TRS → dual XLR M", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("RCA pair (stereo)", [AX_LEN(LEN_AUD), ax("Build", BUILD_AUD, true)]),
      I("Toslink / optical", [AX_LEN(LEN_AUX), ax("Build", BUILD_AUD, true)])
    ]},

    { id: "dpleg", name: "DisplayPort & legacy video", chip: "#3A4A57", items: [
      I("DisplayPort – DisplayPort", [AX_LEN(LEN_DP), ax("Spec", SPEC_DP, true), AX_FINISH]),
      I("DisplayPort AOC / fiber", [AX_LEN(LEN_DP_AOC), ax("Spec", SPEC_DP, true), AX_FINISH], "directional"),
      I("Mini-DP → DisplayPort", [AX_LEN(LEN_DP), ax("Spec", SPEC_DP, true), AX_FINISH]),
      I("Mini-DP → HDMI", [AX_LEN(LEN_DP), ax("Spec", SPEC_DP, true), AX_FINISH]),
      I("DisplayPort → HDMI", [AX_LEN(LEN_DP), ax("Spec", SPEC_DP, true), AX_FINISH], "one-way part — HDMI→DP is a different, active device"),
      I("USB-C → DisplayPort", [AX_LEN(LEN_DP), ax("Spec", SPEC_DP, true), AX_FINISH]),
      I("VGA HD15 M–M", [AX_LEN(LEN_VGA), AX_FINISH]),
      I("VGA + 3.5 mm audio combo", [AX_LEN(LEN_VGA), AX_FINISH]),
      I("DVI-D dual-link", [AX_LEN(LEN_DVI), AX_FINISH]),
      I("DVI-D → HDMI", [AX_LEN(LEN_DVI), AX_FINISH])
    ]},

    { id: "fiber", name: "Fiber patch cords", chip: "#D98B00", items: [
      I("Duplex patch cord", [AX_LEN(LEN_FIB), ax("Fiber", FIB_TYPE, true), ax("Connectors", FIB_CONN, true)]),
      I("Simplex patch cord", [AX_LEN(LEN_FIB), ax("Fiber", FIB_TYPE, true), ax("Connectors", FIB_CONN, true)]),
      I("Armored patch cord", [AX_LEN(LEN_FIB), ax("Fiber", FIB_TYPE, true), ax("Connectors", FIB_CONN, true)])
    ]},

    { id: "power", name: "Power cords (rack)", chip: "#5D656E", items: [
      I("IEC C13 → C14 jumper", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("IEC C13 → C14, right-angle C13", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("IEC C13 → C14, locking", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("IEC C13 → 5-15P (wall)", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("IEC C19 → C20", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("IEC C19 → 5-20P", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)]),
      I("5-15 extension cord (SJT)", [AX_LEN(LEN_PWR), ax("Gauge", GAUGE, true), ax("Color", COLOR)])
    ]},

    { id: "writein", name: "Write-ins", chip: "#5D656E", writein: true, items: [] }
  ];

  return {
    cats: cats,
    alt: ALT,
    // Axes a write-in line gets: a free length and a free finish, because a
    // write-in is usually "the odd one" and still has to arrive orderable —
    // both NEUTRAL-FIRST, so they are opted into, never assumed.
    writeinAx: [ax("Length", [NO_LEN].concat(LEN_HDMI)), ax("Finish", [NO_FIN].concat(FINISH), true)],
    writeinFlags: ALT
  };
})();
