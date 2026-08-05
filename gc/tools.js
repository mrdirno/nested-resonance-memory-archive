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
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
