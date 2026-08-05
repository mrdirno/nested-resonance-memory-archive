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

  /* ── THE T&M TAG (shape #2 — shared/note.js) ──────────────────────────────
   * The directed-work ticket's vocabulary. Same boundary as everything above:
   * these are things a tech PICKS, never things this page decides. No rates, no
   * durations, no priced anything — the office owns the number and the tech owns
   * what happened.
   *
   * WHAT A WORKING AV LEAD CHANGED, before a line shipped:
   *  · WHOSE CALL IT WAS is the first field, not the last. AV gets directed by
   *    four different bosses on the same floor and the seat decides where the
   *    extra even goes: the GC super's call lands on the GC's CO log, the end
   *    user's goes straight to the owner and never touches the GC. A tag that
   *    doesn't say which gets routed wrong and sits for a month.
   *  · THE ROOM IS THE WAY THE DRAWINGS CALL IT. "Conference room" matches
   *    nothing — the GC has eleven and three are on another floor. CR-204 ties
   *    the extra to a scope line; "conference room" ties it to an argument.
   *  · THE IMPACT LINE IS NOT THE EXTRA. The extra is forty minutes. The cost is
   *    the room he was actually scheduled for and didn't finish — another
   *    mobilization, another badge, another after-hours window, and three weeks
   *    later AV gets blamed for that room being late too. Techs leave it off
   *    because at 4:45, with the super standing there, the favor feels small.
   *  · "THEIR GEAR, POWERED, NOT TESTED BY US" IN WRITING is the only thing
   *    between the tech and a free warranty roll the first time the client's own
   *    bar drops audio and everyone points at AV.
   */
  var TAG = {
    how: [
      { v: "Told me on site" }, { v: "Phone" }, { v: "Text" }, { v: "Email" }
    ],
    // what he was actually put on. Named as the thing the receiver watched him do
    // — "misc AV work" gets "that was in your scope" and dies on the spot.
    did: [
      { name: "Hung / installed their own gear", sub: "OFE" },
      { name: "Extra display + mount" },
      { name: "Pulled another cable" },
      { name: "Moved a device after rough-in" },
      { name: "Control program change" },
      { name: "Signage content / playlist" },
      { name: "Got it on their network", sub: "ports / VLAN" },
      { name: "Firmware + updates" },
      { name: "Extra training / walkthrough" },
      { name: "Demo + haul off the old gear" }
    ],
    // why it is not ours. Without this the tag is a work log; with it, it is a
    // claim — and it names whose ball got dropped before the argument starts.
    why: [
      { name: "Not on the AV drawings" },
      { name: "Not in the approved submittal" },
      { name: "Their gear, not our supply", sub: "OFE" },
      { name: "That room isn't in our contract" },
      { name: "Power / conduit", sub: "EC's scope" },
      { name: "No backing in the wall", sub: "GC's scope" },
      { name: "Network, ports, VLAN", sub: "owner IT's scope" },
      { name: "Added after sign-off" },
      { name: "Rework — somebody else's damage" }
    ],
    left: [
      { v: "Room's up and usable" },
      { v: "Temp — works, not final" },
      { v: "Room's down till we're back", hot: 1 },
      { v: "Their gear hung + powered, not tested by us" },
      { v: "Needs IT before it'll work", hot: 1 }
    ],
    // WHEN, never what it is worth. AV extras get shoved to nights by default —
    // the room is occupied all day and IT won't let you near the codec at 10am —
    // so "nights" is a fact about WHEN the work happened. The page never says
    // what a night hour is worth; it says it was a night hour. NEUTRAL FIRST.
    shift: ["— when", "Reg hours", "Nights", "Weekend"],
    // the lines that get left off and then get argued about
    gear: [
      { name: "Lift / ladder over 12 ft" },
      { name: "After hours", sub: "off our normal window" },
      { name: "Escort / badge / security" },
      { name: "Freight elevator window" },
      { name: "Core drill / anchors" },
      { name: "Have to come back to finish it" }
    ]
  };

  return {
    cats: cats,
    alt: ALT,
    // Axes a write-in line gets: a free length and a free finish, because a
    // write-in is usually "the odd one" and still has to arrive orderable —
    // both NEUTRAL-FIRST, so they are opted into, never assumed.
    writeinAx: [ax("Length", [NO_LEN].concat(LEN_HDMI)), ax("Finish", [NO_FIN].concat(FINISH), true)],
    writeinFlags: ALT,
    tag: TAG
  };
})();

/* ── THE CROSS-BOUNDARY REQUEST — what an AV crew needs OUT of somebody else ──
 *
 * The FIRST tool in this toolkit whose output leaves the company that made it
 * (av/AV_SOCIETY.md §THE INTERFACE). Everything before it served one man sending
 * something UP his own chain. This is what he sends SIDEWAYS, to the electrician,
 * the framer, the ceiling crew, the millwork shop.
 *
 * Written by an AV install foreman and then cut by a cross-trade skeptic. What
 * they refused to put in matters more than what they kept, and every one of these
 * is a §SAFETY line, not a taste call:
 *   · NO circuit sizes, wire sizes, conduit fill or box fill. We ask for a
 *     dedicated circuit and a pathway; the EC engineers it under his own stamp.
 *   · NO mounting heights on a menu. Heights come off the elevations and the
 *     room, and a number picked off a dropdown puts a box in the wrong wall.
 *     Height stays FREE TEXT on the row, on purpose.
 *   · NO fire ratings, listed assemblies or firestop products. We ask for a
 *     sleeve and we ask WHO OWNS the firestop. What's listed for that wall is
 *     the GC's business and the AHJ's, and asserting it here would be inventing
 *     certified data.
 *   · NO calendar dates. You do not hand a super your calendar — you ask against
 *     HIS gates ("before rock", "before the tile goes in"), because his schedule
 *     is the one that moves. That is why `milestones` is the load-bearing axis of
 *     the whole tool and not a nicety.
 *   · NO money, no backcharge, no "who eats it". The minute there is money in it
 *     it leaves this list and goes to the PM.
 *   · NO product or model numbers for the other trade to buy. Spec his material
 *     and you own his warranty. Ask for the hole; he buys the pipe.
 *
 * `who` and `by` on an ask are the USUAL aim and the USUAL gate. They only ever
 * fill a field he has left empty and never overwrite a pick (§SCARS — a default
 * is a claim).
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Rough-In Request",
  eyebrow: "AV · you → the other trades",
  lede: "Every box, sleeve, pathway, whip and pad you need out of somebody else's crew — sorted by who you're asking and which gate it has to beat. Text him his list, then chase it till it's in.",
  docSubject: "AV rough-in — what we need before it closes",
  docSubjectWith: "AV rough-in — what we need from {to}",
  closing: "Anything on here you can't hit, call me before you cover it — I'd rather move my device today than core your floor and open your wall later.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> drawings. This page doesn't size a box, a raceway or a circuit, it doesn't set a mounting height, and it doesn't know what the code, the architect or the engineer requires — verify all of that against your own set. It's an ask, not an approved design, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The drawing and revision is the whole argument. \"Off AV-101 rev 2\" is the difference between a request the other foreman works to and one he re-walks with you next week.",
  phJob: "Building C", phOff: "AV-101 rev 2", phFrom: "Rico — Acme AV",
  phArea: "CR-204 — then it's a button", areaLabel: "Room / area",

  who: [
    { v: "ec", label: "Electrician" },
    { v: "gc", label: "GC super" },
    { v: "framer", label: "Framer / drywall" },
    { v: "it", label: "IT / cabling" },
    { v: "ceilings", label: "Ceilings (ACT)" },
    { v: "mill", label: "Millwork" },
    { v: "mech", label: "Mechanical" }
  ],

  // EARLIEST FIRST. This is the order a job actually closes up in, and it is why
  // grouping the list by "When" reads as a countdown instead of a pile.
  milestones: [
    { v: "pour", label: "Before the pour" },
    { v: "rock", label: "Before rock goes up" },
    { v: "ceiling", label: "Before ceiling closes" },
    { v: "paint", label: "Before paint" },
    { v: "floor", label: "Before floor goes down" },
    { v: "millwork", label: "Before millwork sets" },
    { v: "rack", label: "Before the rack lands" },
    { v: "trim", label: "Before we trim out" }
  ],

  // Ordered by how often it comes up on a real job, not alphabetically.
  asks: [
    { v: "backbox", label: "Back box", who: "ec", by: "rock", specs: [
      "Deep box + single-gang mud ring",
      "Deep box + 2-gang mud ring",
      "LV ring + pathway, no box needed",
      "Recessed AV box behind the display",
      "Two boxes, own rings, not ganged",
      "Set plumb and flush to finish face"
    ] },
    { v: "conduit", label: "Conduit / sleeve", who: "ec", by: "rock", specs: [
      "Stub to accessible ceiling + pull string",
      "Home run to the AV rack, no J-boxes",
      "Short sleeve through the wall, both sides",
      "Sweeps only — no LBs, we pull terminated",
      "Size per my markup, don't downsize it",
      "Pull string left long at both ends",
      "Firestop after our pull — you own it"
    ] },
    { v: "power", label: "Power", who: "ec", by: "rock", specs: [
      "Quad behind the display, clear of the mount",
      "Recept above ceiling at the projector",
      "Whip to the rack, leave tails long",
      "Dedicated circuit — nothing else on it",
      "Rack and displays on the same phase",
      "Iso ground pulled back to the panel",
      "Recept in the floor box, AV side"
    ] },
    { v: "wallclear", label: "Keep the wall clear", who: "gc", by: "rock", specs: [
      "Nothing in my display footprint — no switches, stats, strobes",
      "Sprinkler head and diffuser clear of the screen",
      "Light switch on the other side of the door",
      "Nothing lands on the niche wall — I'll spray the outline",
      "Walk the wall with me before anybody roughs it"
    ] },
    { v: "blocking", label: "Blocking / backing", who: "framer", by: "rock", specs: [
      "Plywood backer — we field-locate the mount",
      "Solid blocking at the mount points",
      "Backer full width, display may still shift",
      "Backing behind the wall speakers",
      "Backing for the camera shelf / mount"
    ] },
    { v: "ceilsupport", label: "Ceiling support", who: "ceilings", by: "ceiling", specs: [
      "Strut to structure at the projector",
      "Support off the deck, not off the grid",
      "Rod left long — we cut to height",
      "Strut above the tile at the speakers",
      "Support the camera mount off structure",
      "Brace and wire my devices same as yours"
    ] },
    { v: "datadrop", label: "Data drop", who: "it", by: "trim", specs: [
      "Drop at each display, both ends done",
      "Drop above ceiling at each camera",
      "Service loop left at the device",
      "Label to my numbering, not yours"
    ] },
    { v: "floorbox", label: "Floor box", who: "ec", by: "pour", specs: [
      "AV compartment separate from power",
      "Set flush to finish floor, not to slab",
      "Poke-thru under the table leg",
      "Trim ring to match the finish floor",
      "Conduit from the box out to the wall",
      "Deep enough for our plugs and slack",
      "Lid opens toward the table"
    ] },
    { v: "gridhold", label: "Grid + tile hold", who: "ceilings", by: "ceiling", specs: [
      "Hold a full tile at each speaker",
      "Keep my device off the main tee",
      "Grid layout per my ceiling markup",
      "Tile bridge / support at every cut",
      "You cut the tile, we set the device",
      "Keep the light out of that tile",
      "Sprinkler head clear of the screen"
    ] },
    { v: "millchase", label: "Millwork chase", who: "mill", by: "millwork", specs: [
      "Grommet in the table at my mark",
      "Chase down the table leg to the floor box",
      "Cutout in the credenza back panel",
      "Leave the back open — no fixed panel",
      "Vent it — gear lives in that cabinet",
      "Removable panel at the lectern",
      "Mic wells in the bench per my markup"
    ] },
    { v: "rackroom", label: "Rack room", who: "gc", by: "rack", specs: [
      "Pad poured and level before rack day",
      "Cooling on before the rack lands",
      "Plywood on the wall for our gear",
      "Door swing + clear path to get it in",
      "Ground bar in the closet",
      "Closet stays clean — not a storeroom"
    ] },
    { v: "accesspanel", label: "Access panel", who: "gc", by: "ceiling", specs: [
      "Access door at the screen pocket",
      "Access door at the projector lift",
      "Hinged door, not a cut-and-patch",
      "Big enough for a hand and a tool",
      "Locate to my markup before the lid"
    ] },
    { v: "roughopening", label: "Rough opening", who: "framer", by: "rock", specs: [
      "Niche R.O. per my markup",
      "Screen pocket in the hard lid",
      "Rough it big — we shim to the frame",
      "Drywall return, no bullnose at the edge",
      "Don't finish inside — we cover it",
      "Hold the R.O. till I hand you the frame"
    ] },
    { v: "shadetie", label: "Shade / light tie", who: "ec", by: "ceiling", specs: [
      "Pair from the lighting panel to the rack",
      "Control pair to the shade motors",
      "Power in the shade pocket",
      "Pathway to the keypad location",
      "Pathway to the shade controller location"
    ] },
    { v: "core", label: "Core drill", who: "gc", by: "floor", specs: [
      "Scan it before you cut",
      "Core + sleeve, we pull after",
      "Core under the table, not the aisle",
      "Sleeve stands proud of the finish floor",
      "Firestop and patch after our pull",
      "Coordinate the core with the floor below"
    ] },
    { v: "paintfirst", label: "Paint before we hang", who: "gc", by: "paint", specs: [
      "Finish paint the wall before we mount",
      "Paint the full wall — don't cut around us",
      "Inside of the niche painted flat black",
      "Let it cure before we hang steel on it"
    ] }
  ]
};
