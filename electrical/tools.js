/* ELECTRICAL FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * The deploy asserts every `href` in this file resolves to a real page inside the
 * published artifact — a registry entry pointing at a page that does not exist
 * used to ship green and 404 in an electrician's hand.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /electrical/
 *   desc      one line — what document/request it helps a real electrician produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Pull List",
    href: "pull-list.html",
    desc: "Type what you already know you need, then tick down the forget-list — mud rings by depth, anti-shorts, locknuts, ground pigtails, long 6-32s. Copy it to the warehouse or the counter and get it on the truck.",
    chip: "#3FB6F5",
    audience: "Field → Warehouse",
    pinned: true
  },
  {
    name: "T&M Ticket",
    href: "tm-ticket.html",
    desc: "Directed work that isn't on your prints. Ticket it before you pull off — who directed it, what you had us do, why it's an extra, men and hours by classification and ST/OT/DT. No rates, no totals, no fake signature line.",
    chip: "#0A5C87",
    audience: "Foreman → Super / GC PM"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
