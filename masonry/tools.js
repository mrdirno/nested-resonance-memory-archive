/* MASONRY FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /masonry/
 *   desc      one line — what document/request it helps a real mason produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * THE YARD CALL WAS THE LINE THIS FILE SHIPPED WITHOUT, AND IT IS PAID.
 * The first commit named it here — three independent in-trade panels named the
 * afternoon material call unprompted, the 20-year prune kept it first, and it
 * was held back because "a checklist-request the size of the supply-house order
 * is a vocabulary build in its own right, and half a yard call is worse than
 * none: a man who calls in an order off a list that is missing a line stops
 * opening the list." Built 2026-08-15 as the ninth instance of shape #1: 62
 * lines across seven sections, the unit of issue attached to every bare number,
 * and the message ending on what is NOT on the call.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the reason this trade is on the rack. electrical/items.js
    // ships "Before CMU caps out" and plumbing/items.js ships "Before block goes
    // up" — two whole trades counting down to a number nothing on the job has
    // ever published. The man standing on the wall is the only one who has it.
    name: "Where The Wall's At",
    href: "wheres-the-wall.html",
    desc: "Wall by wall at quitting time — the course each one got to, what's holding it, which cells are still open and what nobody touches. Tap each wall up the ladder and send one message. Two other trades have been counting down to your cap out for months; this is the first page that gives them the number.",
    chip: "#B9EE1B",
    audience: "Foreman → super / EC / plumber",
    pinned: true
  },
  {
    // The one every mason makes and nobody writes down. Its whole job is to be
    // COMPLETE — the unit of issue on every line, and a message that ends by
    // naming what is missing rather than shipping short.
    name: "The Yard Call",
    href: "yard-call.html",
    desc: "Tomorrow's material off a list instead of off your memory — block by the cube, mud by the bag, sand by the yard, wire by the roll, and which side of the building the forks set it on. Put a bare number in and the yard's own word comes with it. The message closes by naming what you didn't put on it.",
    chip: "#8AB50E",
    audience: "Foreman / tender → the supply house"
  },
  {
    name: "What I'll Build In",
    href: "answer-back.html",
    desc: "The electrician or the plumber sent you a list of what has to go in this wall. Paste it, tap each line will do / already in / can't / need to know, and put the COURSE on every yes — because a date doesn't help a man whose box is at ten foot and whose wall is at four.",
    chip: "#799C11",
    audience: "Foreman → EC / PC / GC"
  },
  {
    name: "Before It Goes Up",
    href: "rough-in-request.html",
    desc: "Everything another outfit owes you before you get on the wall — layout and a control line, the footing and the dowels, frames, lintels, embeds, precast, the stage — with the course each one has to beat. Walk it once, tap the rows, send one message per trade.",
    chip: "#99C70F",
    audience: "Foreman → GC / steel / HM / concrete"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Told to cut in an opening nobody drew, break out a lift and re-lay it, or stand by while another trade got out of your wall? Write the tag before you lay past it — who told you, what came up, why it's outside your contract, crew and material as counts, and what is NOT in this tag. En español también.",
    chip: "#4C5F11",
    audience: "Foreman → super / PM"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — the wall you were stopped on, the lift you had to break out, the crack that isn't yours, the weather day, the efflorescence letter, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the truck.",
    chip: "#4B3F8F",
    audience: "Foremen · supers · PMs"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask you send whoever holds the gate — the day, the route in, where the cubes land, and the heads-up that keeps a load sitting at a locked gate on the forks. It's an ask, not a booking, and it says so. Then put whatever they send back against what you asked, and it names what they never answered — because “yeah that’s fine” is not an answer to eight things.",
    chip: "#C6DE7C",
    audience: "Masonry → building engineer / facilities / property manager"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, per diem — and put your real hours in, because a dollar an hour on a winter you couldn't lay is a different dollar.",
    chip: "#566C13",
    audience: "Layers · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
