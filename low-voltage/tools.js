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
  },
  {
    name: "T&M Tag",
    href: "tm-tag.html",
    desc: "Not on our prints, or the ceiling closed on us. Get it on a tag before you're off that floor — who told you, why it's an extra, where it stands, and the men and hours it burned. A heads-up you can reply to, not a claim. En español también.",
    chip: "#9A3312",
    audience: "Tech / lead → GC super / our PM"
  },
  {
    name: "Who Owes Me What",
    href: "rough-in-request.html",
    desc: "Backing before rock, boxes and pathway from the EC, a tile held at every device, the frame prepped before it's ordered. Who owes it, where it is, and the gate it has to beat \u2014 chased till it's in.",
    chip: "#9A3312",
    audience: "LV \u2192 GC / EC / drywall / ceilings"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — daily, test record, incident, delay notice, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dictate it in the van and get back something you can forward.",
    chip: "#4B3F8F",
    audience: "Techs · leads · PMs"
  },
  {
    name: "Got It / Can’t / When",
    href: "answer-back.html",
    desc: "The GC, the EC or the door hardware guy sent you a list. Paste it, tap each line to say got it / in already / can’t / need to know, put a day on the ones you’re taking, and send one answer back.",
    chip: "#8A1C4B",
    audience: "LV → GC / EC / doors / ceilings"
  },
  {
    name: "Shop List",
    href: "consumables.html",
    desc: "The fourteen-cent stuff that stops a floor. Nobody forgets the cable \u2014 what ends a day is no hooks, no anchors, no blanks. Type what you know, tick the forget-list, send it up so the crew keeps pulling.",
    chip: "#9A3312",
    audience: "Installer \u2192 Shop / lead"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package. Put yours next to theirs line by line — wages, fringes, dues, per diem — because LV rates sit all over the map and the fringes are where two jobs actually separate.",
    chip: "#4B3F8F",
    audience: "Installers · leads · anybody weighing a move"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask that gets you into a building's own security world — the night, the rooms, who's coming, and the heads-up the panel room needs before your work sets off what you're there to fix. It's an ask, not a booking, and it says so.",
    chip: "#2B6CB0",
    audience: "LV → building engineer / facilities / security"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];