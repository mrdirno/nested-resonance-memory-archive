/* PLUMBING FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /plumbing/
 *   desc      one line — what document/request it helps a real plumber produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Supply House Order",
    href: "supply-house-order.html",
    desc: "Build it on the tailgate — qty, unit, size and fitting config on every line, so the counter pulls the right part the first time. Will-call goes out under a name; a delivery carries the gate, the window, where it lands and who signs, typed once for the job.",
    chip: "#C87137",
    audience: "Plumbers → Counter",
    pinned: true
  },
  {
    name: "T&M Tag",
    href: "tm-tag.html",
    desc: "Not on your prints? Write the tag before you roll — who told you, why it's outside your contract, crew and material as counts, and what is NOT in this tag. Reads in the same order as the yellow copy so you're not writing the job twice.",
    chip: "#7A3F12",
    audience: "Foreman → Super / PM"
  },
  {
    name: "Hole & Backing List",
    href: "rough-in-request.html",
    desc: "Every sleeve, blockout, chase, core and backing another outfit has to leave you before you can rough it in \u2014 with the pour, the block and the dry-in it has to beat. One walk, one message each.",
    chip: "#7A3D14",
    audience: "PC \u2192 GC / concrete / framer / EC"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — daily, incident, delay notice, service call, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the truck and get back something the office can forward.",
    chip: "#4B3F8F",
    audience: "Foremen · service · PMs"
  },
  {
    name: "Yes, No, and When",
    href: "answer-back.html",
    desc: "The GC or another trade sent you a list of what they need out of you. Paste it, tap each line to say will do / in already / can’t / need to know, put a date on the yesses, and send one answer back before the pour instead of after it.",
    chip: "#8A1C4B",
    audience: "PC → GC / EC / other subs"
  },
  {
    name: "It’s Holding",
    href: "its-holding.html",
    desc: "Five pounds of air, ten foot of head, whatever you put on it. Tap ON TEST and the clock starts itself — readings, who looked at it, when it came off. Copy the caption that goes under the photo of the gauge.",
    chip: "#7A3F12",
    audience: "PC → GC / inspector / the office file"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package. Put yours next to theirs line by line — wages, fringes, dues, per diem — and get the real gap instead of an argument about the headline number.",
    chip: "#2E7D4F",
    audience: "JWs · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];