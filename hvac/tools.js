/* HVAC/R FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * The deploy asserts every `href` in this file resolves to a real page inside the
 * published artifact — a registry entry pointing at a page that does not exist
 * used to ship green and 404 in a tech's hand.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /hvac/
 *   desc      one line — what document/request it helps a real tech produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Repair Recommendation",
    href: "repair-recommendation.html",
    desc: "You found it, you're not fixing it today. Send the office what it takes to quote it without calling you back — unit tag, what's on the plate, the part off the dead component, what happens if they sit on it, and how you're getting up there.",
    chip: "#4FE0C0",
    audience: "Tech → Service manager",
    pinned: true
  },
  {
    name: "T&M Tag",
    href: "tm-tag.html",
    desc: "Outside the agreement, and you need it in writing before you put a wrench on it. Tag it at the unit — who told you, what you found, whether it's down right now, crew, material, and refrigerant on its own line by ASHRAE number.",
    chip: "#0C7A66",
    audience: "Tech → Site contact / Service manager"
  },
  {
    name: "The By-Others List",
    href: "rough-in-request.html",
    desc: "Disconnects, whips, curbs, dunnage, condensate, controls power \u2014 everything on your unit that somebody else owes you. Sorted by who owes it and the gate it has to beat, then chased till it's in.",
    chip: "#1F6F5C",
    audience: "HVAC \u2192 EC / GC / plumber / roofer"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — service call, startup, incident, delay notice, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it at the unit and get back something the customer can read.",
    chip: "#4B3F8F",
    audience: "Techs · service managers"
  },
  {
    name: "My Answer on Your List",
    href: "answer-back.html",
    desc: "The GC, the EC or the controls house sent you a list. Paste it, tap each line to say will do / in already / can’t / need to know, put a date on the yesses, and send one answer back instead of a phone call nobody wrote down.",
    chip: "#8A1C4B",
    audience: "HVAC → EC / GC / PC / controls"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
