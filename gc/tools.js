/* GC & SITE SUPER FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * The deploy asserts every `href` in this file resolves to a real page inside the
 * published artifact — a registry entry pointing at a page that does not exist
 * used to ship green and 404 in a super's hand. It also asserts this file EXISTS:
 * trade #5 was caught one gate short of publishing a working nav over an empty
 * hub because it had every other file and not this one.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /gc/
 *   desc      one line — what document/request it helps a real super produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Weather Day",
    href: "weather-day.html",
    desc: "You lost the day. Tick what it did, what it stopped and what it cost besides the hours, say what it pushes, and send your PM one thing he can answer in a thumb — before he writes the letter. Works the night before too, when the call still saves money.",
    chip: "#8CE86B",
    audience: "Supers → PM / office",
    pinned: true
  },
  {
    name: "T&M Tag",
    href: "tm-tag.html",
    desc: "Directed to do something that isn't in the contract. Paper it before you leave the gate — who directed it, what you did and where, crew and hours by classification, today only. Your log owns the number; this is the field record.",
    chip: "#2C6E1B",
    audience: "Super → CM / Owner's rep"
  },
  {
    name: "The Close-In List",
    href: "rough-in-request.html",
    desc: "Before you cover it, pour it or close the lid: what has to be IN, tested and signed off, who owes each one, and the gate. Send every sub his own list, then tick them off as they come back.",
    chip: "#1F5B8F",
    audience: "Super \u2192 every sub on the floor"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — daily, meeting notes, incident, delay notice, closeout. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it walking back to the trailer and get back something you can send out.",
    chip: "#4B3F8F",
    audience: "Supers · PEs · PMs"
  },
  {
    name: "What I’ll Get You",
    href: "answer-back.html",
    desc: "Your subs send you lists all day — access, cores, backing, power, dates. Paste one, tap each line to say will do / in already / can’t / need to know, put a date on the yesses, and answer the whole thing in one message.",
    chip: "#8A1C4B",
    audience: "GC → subs / owner vendors"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The salary is not the package. Put what you're on now next to the offer — bonus that actually landed, truck, phone, what they put in, what you pay back — and compare the whole thing.",
    chip: "#2E7D4F",
    audience: "Supers · PMs · anybody weighing an offer"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];