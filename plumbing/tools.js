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
    desc: "Build the will-call list on the tailgate — qty, size, material and fitting config on every line, so the counter pulls the right part the first time. Copy it straight into a text.",
    chip: "#C87137",
    audience: "Plumbers → Counter",
    pinned: true
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
