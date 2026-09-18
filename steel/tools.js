/* STEEL & MISC METALS FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /steel/
 *   desc      one line — what document/request it helps a real crew produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight (§TRADE EXPANSION: an unnamed absence is a hole, a
 * named one is a decision):
 *
 *   - NOT READY TO SET (shape #2, shared/note.js) — SHIPPED C3738 as
 *     not-ready-to-set.html, the go/no-go the foreman sends the ONE morning the
 *     crane's already on the clock and the site isn't ready: anchor bolts not set
 *     or nobody's shot them, embeds not cast, the deck below not poured, no pad
 *     for the crane, laydown blocked, a line over the swing nobody de-energized,
 *     the approved set out of date. Deferred ONE cycle when the kit stood up (the
 *     ask pages getting-in and Before I Set had to be live first, or it'd be three
 *     lists of the same blockers to keep in step); those shipped, so this did.
 *     The overlap held to a distinction, not a merge: Before I Set is the week-out
 *     ask, getting-in is the occupied-site ask, this is 6 a.m. with the iron on
 *     the truck. It cites the certified record (the bolt shot, the cure, the
 *     capacity) and never restates it, the way every steel page does.
 *
 *   - THE MISC-METALS & EMBED ORDER (shape #1, shared/checklist-request.js) —
 *     the loose lintels, angle, embeds, plates, anchor bolts, deck screws and
 *     welding consumables he calls the shop or the supplier for. Deferred
 *     because half its vocabulary is a material grade and a size, which is
 *     refusal 1 and refusal 6 — it ships WRITE-IN-FIRST with a short forget-it
 *     picker (the electrical/pull-list shape), never a full product picker, and
 *     that build is its own careful cycle.
 *
 *   - WHAT WAS UNDER IT / THE FIELD-CONDITION FINDINGS (shape #3) — the row log
 *     for what the field didn't match on the stamped set: an embed cast wrong,
 *     a bolt pattern off, a beam short. Named rather than built because the
 *     honest version is a FINDING with a photo handed to the detailer, and the
 *     line between that and "this weld is bad / this connection won't hold" is
 *     refusal 5 — it gets built deliberately, with the write-up library's CAUSE
 *     and VERDICT refusals wired in, not bolted on in a hurry.
 *
 *   - THE LANGUAGE LAYER (EN/ES) — shared/lang.js rides on the tag pages of the
 *     kits that ship a directed-work tag. This kit ships no tag this cycle, so
 *     its ES debt lands with the findings page, on that page — never on a page
 *     that never asked for it (the mistake paving's registry recorded).
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and the one page on this hub that could not exist anywhere else.
    // Five kits route asks at steel and there was no steel/ for any of them to
    // land on. This is the ledger where they land — and the deck pours once.
    name: "Before the Deck Pours",
    href: "before-the-deck-pours.html",
    desc: "Every embed, clip, sleeve, opening, anchor bolt and dunnage stand somebody else needs in your steel before the deck closes over it. One row per leave-out: whose it is, which column line, whether it's on the drawing, set, set-and-tied, not coming, or already poured over, and the gate it has to beat. Sent to the super and every outfit on it, grid by grid, while it's still a clip and a drawing. After the deck's screwed off and the pour goes green it's a core bit through cured concrete and a field weld an inspector has to sign — and it looks like your steel held them up.",
    chip: "#B4C9CF",
    audience: "Foreman → GC super / EC / mech / plumber / mason / concrete / LV",
    pinned: true
  },
  {
    name: "Before I Set",
    href: "rough-in-request.html",
    desc: "You're setting iron everybody's work lands in, in a window that shuts when the deck pours. Walk it a week out and send each outfit its own list — the anchor bolts set to the template, the embeds and weld clips located off their sheet, the dunnage and openings framed, the hanger steel where their hangers land, the loose lintels before the head course, the approved set and the open RFIs from the detailer — each ask against your own gate, one message per outfit, all off THEIR stamped drawing and never a spec of yours. The refusal is telling the super the deck closed on him; this page is how you never send it.",
    chip: "#B4C9CF",
    audience: "Foreman → GC super / concrete / EC / mech / plumber / mason / LV / detailer / CM"
  },
  {
    name: "Not Ready to Set",
    href: "not-ready-to-set.html",
    desc: "The crane's booked and the iron's on the truck, and one of the things that had to be ready — the anchor bolts nobody shot, the embeds that never got cast, the deck below that isn't poured, a crane that can't get set up, a laydown that's still full, a line over the swing nobody de-energized — isn't. Walk the pick before you call the iron up, name what stops the set in your own words, and send the two-button ask: clear it and tell me when, or direct me in writing to fly it as it sits. It states no torque, no bolt tension, no capacity and no survey number — it hands whoever runs the job the choice, on the record, because a crane day doesn't come back and iron you set on somebody else's condition is on your record.",
    chip: "#B4C9CF",
    audience: "Foreman → GC super / concrete foreman / crane outfit / CM / building engineer"
  },
  {
    name: "Walk Back",
    href: "answer-back.html",
    desc: "The super, the detailer or the inspector walked the steel and sent a list — clips missing at a beam, an anchor bolt off the column, a rail base not set, an opening not framed. Paste it whole and go down it once: we'll set it with a day on it, already in, not mine, or it's the detail — and send back one message they can close from, under their own numbers. It's the detail is the rung this trade needed: half of what gets flagged is how the connection is drawn on the approved set, and field-modifying engineered steel is a marked-up sheet back through the engineer, never a fix on a walk.",
    chip: "#B4C9CF",
    audience: "Foreman → GC super / detailer / inspector / owner"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "Setting iron on a site somebody else runs, with a crane that swings over their building and a welder that throws sparks near their people — the ask to whoever holds it: the pad and the swing, laydown for the steel, the truck route and the turnaround, power for the welder, the approved set and the control lines, a flagger if the boom's near a road, and which days. And the heads-ups: a boom over an occupied building, overhead power lines in the swing, a lane closure, hot work near their people, roof access — each handed back to whoever owns the permit, the power-down and the fire watch, because near a crane and a utility's lines you own none of it.",
    chip: "#B4C9CF",
    audience: "Foreman → CM / property manager / building engineer / GC super"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — what the field didn't match on the stamped set, the day the crane couldn't fly, the embed that was cast wrong before you got there, the RFI you're still waiting on, the area you were directed to set anyway → dictate the mess at the gang box, get back something the detailer and the office can forward. Set up every one you write in a single block, and it never states a torque, a weld size, a material grade, a capacity or a cause, and never says a connection holds.",
    chip: "#B4C9CF",
    audience: "Foreman → office / detailer / GC / EOR-through-the-office"
  },
  {
    /* The spine tool that is not trade work — deeper chip, the masonry
       convention: this is the one page in the kit about the man, not the job. */
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are the weather's and the crane's. Put yours next to theirs line by line — wages, fringes, dues, per diem, the travel, the truck — and put your real hours in, because a dollar an hour on a trade that stops for wind, stops for the crane and works off the ground is a different dollar than the same dollar on a bench.",
    chip: "#2C4A54",
    audience: "Ironworkers · connectors · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
