/* LOW-VOLTAGE FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * The deploy asserts every `href` in this file resolves to a real page inside the
 * published artifact — a registry entry pointing at a page that does not exist
 * used to ship green and 404 in a tech's hand.
 *
 * THIS FILE WAS THE ONE MISSING PIECE OF TRADE #5 (found 2026-08-04 by the deploy
 * gate, before it ever shipped). `low-voltage/` had its config, its hub, its
 * vocabulary data, its credit ledger and a finished Device Checkout page — but no
 * registry. `index.html` reads `window.TOOLKIT_TOOLS || []` and the shared runtime
 * reads the same global for the nav dropdown, so without this file the trade would
 * have published a working nav over an EMPTY hub, with its only tool unreachable
 * from anywhere. That is the documented "registry global" trap, caught mechanically
 * this time instead of by someone opening the page.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /low-voltage/
 *   desc      one line — what document/request it helps a real tech produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Device Checkout",
    href: "device-checkout.html",
    desc: "Log what you put in, as you put it in — tag, type, location — and tap a row up through pulled, mounted, terminated, tested, programmed, verified. Copy what changed for the huddle, or hand the office the whole list for their spreadsheet.",
    chip: "#FF9E80",
    audience: "Installers → PM / office",
    pinned: true
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
