/* CONCRETE FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /concrete/
 *   desc      one line — what document/request it helps a real concrete hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the reason this trade exists on the rack. Five served
    // trades already ship a page that asks THIS crew for sleeves, blockouts,
    // pads, embeds and a pre-pour walk. Until now the crew being asked had
    // nothing to walk the deck with and nothing to send back.
    name: "Before the Pour",
    href: "rough-in-request.html",
    desc: "Everything another outfit owes you before the truck shows up — sleeves, blockouts, embeds, anchor bolts, the ground, the under-slab, the pads — with the gate each one has to beat. Walk it once, tap the rows, send one message per trade. After the washout it's a core drill.",
    chip: "#2DD758",
    audience: "Foreman → EC / PC / mech / GC / steel",
    pinned: true
  },
  {
    name: "The Mix Order",
    href: "mix-order.html",
    desc: "The call you make at four o'clock and always half-forget a line of. Tick the placement, the delivery, the pump, the gear and the forget-list, put YOUR figures off YOUR approved mix design on it, and read the plant one order that doesn't come back as a question.",
    chip: "#12742B",
    audience: "Foreman → batch plant / dispatch / the pumper"
  },
  {
    name: "What I'll Set",
    href: "answer-back.html",
    desc: "The EC, the plumber or the GC sent you a list of what has to be in this pour. Paste it, tap each line will do / already in / can't / need to know, put a date on the yesses, and send one answer back — before the steel gets covered instead of after.",
    chip: "#1E9E45",
    audience: "Foreman → EC / PC / mech / GC"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Told to dig it deeper, re-set what somebody moved, or stand by while another trade finished? Write the tag before you place — who told you, what came up, why it's outside your contract, crew and material as counts, and what is NOT in this tag. Once it's covered, the evidence is under six inches of mud.",
    chip: "#0B5220",
    audience: "Foreman → super / PM"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — the pour record, the stopped-pour notice, the crack that isn't yours, subgrade not as shown, the weather day, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the truck.",
    chip: "#4B3F8F",
    audience: "Foremen · supers · PMs"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, per diem — and put your real hours in, because a dollar an hour on a winter you didn't pour is a different dollar.",
    chip: "#0B5220",
    audience: "Hands · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
