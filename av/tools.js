/* AV FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request. The hub grid and the per-page nav dropdown both read this list, so a
 * new entry appears everywhere at once — no other file to touch.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /av/ (keep tool pages flat in av/)
 *   desc      one line — what document/request it helps a real tech/PM produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to (e.g. "Techs → PM")
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.AV_TOOLS = [
  {
    name: "Consumables List",
    href: "consumables.html",
    desc: "Field-stock checklist — tick what you're out of, set counts, copy the request straight into chat or email for your PM.",
    chip: "#F0BE1E",
    audience: "Techs → PM",
    pinned: true
  },
  {
    name: "Cable & Adapter List",
    href: "cable-list.html",
    desc: "Pick the cables and adapters for the job — length, spec and finish on every line — and copy a clean order for your PM or the counter. Say once whose finish cable you run, and flag any line you want an alternate priced on.",
    chip: "#2E7D4F",
    audience: "Techs → PM / Warehouse"
  },
  {
    name: "Field Report Setup",
    href: "report-builder.html",
    desc: "Turn your end-of-day mess into one clean report your PM can forward — build a role-tailored AI setup, paste it into Gemini/Claude/GPT once, use it daily.",
    chip: "#2E64C8",
    audience: "Leads · PMs · Cx"
  }
  // The loop appends new tools here as it builds them from wishing-well requests.
];
