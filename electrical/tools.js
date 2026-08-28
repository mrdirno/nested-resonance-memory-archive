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
    desc: "Directed work that isn't on your prints. Ticket it before you pull off — who directed it, what you had us do, why it's an extra, men and hours by classification and ST/OT/DT. No rates, no totals, no fake signature line. En español también.",
    chip: "#0A5C87",
    audience: "Foreman → Super / GC PM"
  },
  {
    name: "What I Need List",
    href: "rough-in-request.html",
    desc: "What you need out of the other guys before it gets buried \u2014 pads, sleeves, backing, cores, trenching, curbs. Every line carries who owes it and which gate it has to beat, and you send each trade his list only.",
    chip: "#C7511F",
    audience: "EC \u2192 GC / concrete / framer / steel"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — daily, incident, delay notice, service call, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the truck and get back something the office can forward.",
    chip: "#4B3F8F",
    audience: "Foremen · service · PMs"
  },
  {
    name: "What I Can Hit",
    href: "answer-back.html",
    desc: "AV, mechanical, the fitters and the GC all send you a list. Paste it, tap each line to say will do / in already / can’t / need to know, put a date on the yesses, and send one answer back instead of six texts.",
    chip: "#8A1C4B",
    audience: "EC → AV / HVAC / PC / GC"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package. Put yours next to theirs line by line — wages, fringes, dues, per diem — and send the real difference to whoever is asking you to drive.",
    chip: "#2E64C8",
    audience: "JWs · foremen · anybody thinking of booking out"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask you send the building engineer to get a crew into a locked gear room — the night, the rooms, who's coming, and the heads-up that keeps you from getting turned away at the door. It's an ask, not a booking, and it says so. Then put whatever they send back against what you asked, and it names what they never answered — because “yeah that’s fine” is not an answer to eight things.",
    chip: "#B8860B",
    audience: "Electrical → building engineer / facilities / security"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];