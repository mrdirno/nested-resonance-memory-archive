/* ROOFING FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /roofing/
 *   desc      one line — what document/request it helps a real roofer produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the only tool in the program that has to be used at a
    // specific hour. Three of the four in-trade panels proposed it independently
    // (2026-08-12) — the strongest convergence in the roster fan-out.
    name: "What's Open Tonight",
    href: "whats-open.html",
    desc: "Section by section at quitting time — how far it got, what's holding the water tonight, and what's underneath the part that's still open. Tap each section up the ladder and send it before you're off the ladder.",
    chip: "#FF93C9",
    audience: "Foreman → super / owner / PM",
    pinned: true
  },
  {
    // ROOFING'S FIRST material order — the tenth instance of the checklist→request
    // shape (av/AV_SOCIETY.md §THE THREE SHAPES). Every other material trade calls
    // its yard off a list; the roofer was still calling it off memory. items.js
    // owns the vocabulary, order-the-load.html owns the words and the two readings
    // (the colour/lot match, and the dry-in questions on the glass).
    name: "Order The Load",
    href: "order-the-load.html",
    desc: "Tomorrow's load called into the yard off a list, not off your memory — field by the square, membrane by the roll, edge metal by the stick, boots by the piece, and whether each lands on the roof or on the ground. Put a bare number in and the yard's own word comes with it; tick the colour that has to match the roof so the re-supply doesn't come back a different lot and stripe the slope.",
    chip: "#9B2F5E",
    audience: "Foreman / roofer → the supply house"
  },
  {
    name: "Before I Open It",
    href: "rough-in-request.html",
    desc: "Everything that has to be off, set, moved or owned before you open a section — and before you cover one. Every curb, sleeve, post and drain another outfit owes you, with the gate it has to beat. One walk, one message each.",
    chip: "#A42E69",
    audience: "Foreman → GC / mech / EC / owner"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Found it after tear-off? Write the tag standing on the open deck — who told you, what came up, why it's outside your contract, crew and material as counts, and what is NOT in this tag. Once the new roof is over it, the evidence is gone. En español también.",
    chip: "#C4426F",
    audience: "Foreman → super / PM"
  },
  {
    name: "What I'll Hit",
    href: "answer-back.html",
    desc: "The mech contractor, the GC or the owner sent you a list of what they need off you. Paste it, tap each line to say will do / already done / can't / need to know, put a date on the yesses, and send one answer back before you cover that section.",
    chip: "#8A1C4B",
    audience: "Foreman → GC / mech / EC / owner"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — leak calls, wet insulation, the weather day, the not-from-our-work reply, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the truck.",
    chip: "#4B3F8F",
    audience: "Foremen · service · PMs"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line, then put your real hours in — a dollar an hour on a rained-out year is a different dollar.",
    chip: "#8A1C4B",
    audience: "Hands · foremen · anybody weighing a move"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask you send whoever holds the keys to get a crew onto the roof — the hatch, the ladder, the lot for the truck, the hoist or crane window, and the heads-up that keeps everybody underneath clear. It's an ask, not a booking, and it says so. Then put whatever they send back against what you asked, and it names what they never answered — because “yeah that’s fine” is not an answer to eight things.",
    chip: "#D6528E",
    audience: "Roofing → building engineer / facilities / property manager"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];