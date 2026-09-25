/* SIDING & EXTERIORS FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /siding/
 *   desc      one line — what document/request it helps a real crew produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight (§TRADE EXPANSION: an unnamed absence is a hole, a
 * named one is a decision):
 *
 *   - THE COIL & TRIM ORDER (shape #1, shared/checklist-request.js) — BUILT
 *     C3749 as counter-call.html, "The Counter Call"; that cycle died before its
 *     commit, C3750 ran a five-lens audit and fixed its confirmed findings and
 *     died before its commit too, and C3751 shipped it after an independent
 *     re-verification (av/AV_SOCIETY.md, C3750 and C3751). Deferred at stand-up for
 *     the window, not for doctrine, and marked FIRST RUNG FOR #19; #19 (steel)
 *     came and went and C3738 took steel's own first rung, so it stood overdue
 *     for five days until the stalest axis landed on it. A four-lens panel (the
 *     siding lead · the counter man · doctrine · the skeptic) scored it
 *     6 · 7 · 7 · 6 and renamed it: the working title printed bare "trim" in
 *     every page's Tools menu and bare "coil" beside HVAC's, and the rack
 *     already had the family (The Yard Call, The Dealer Call, The Store Call).
 *     It shipped WRITE-IN-FIRST with a 27-line forget-it jog, as this note
 *     said it would — and the named list itself was corrected on the way in:
 *     "starter" became "siding starter strip" (a counter with a roofing desk
 *     hands you the shingle one), "soffit" became the eave soffit, "hangers"
 *     became hangers for the gutter, and the ferrule left the picker with its
 *     spike (refusal 2 names nail types). Why each line is or is not on it
 *     lives above TOOLKIT_ITEMS.order in items.js; the page's own words are
 *     asserted by tools/toolkit-gates/counter-call.mjs.
 *
 *   - THE EXTRA WORK TAG (shape #2, shared/note.js) — thirteen of seventeen
 *     kits carry it and this one does not, on purpose for one cycle: this
 *     trade's directed work arrives inside the TEAR-OFF (rot behind the wall,
 *     a window nobody flashed, three stubs to move) and the honest version of
 *     that document is a FINDING with a photograph, not a ticket. Building the
 *     tag before the findings page exists would put the rot on a ticket, which
 *     is where a "what caused it" sentence gets written by accident — refusal
 *     7. The findings page goes first; the tag rides on it.
 *
 *   - WHAT WAS UNDER IT (shape #3) — the tear-off findings row log, one row per
 *     place he opened the wall and found something: where, how big off his own
 *     tape, what it looked like, photographed, and whether it stops him. It is
 *     the trade's own document and no sibling has it. Named here rather than
 *     built because it and the tag are ONE rung, not two, and shipping half of
 *     the pair is how a page ends up asserting cause.
 *
 *   - THE LANGUAGE LAYER (EN/ES) — shared/lang.js rides on the tag pages of
 *     thirteen trades. This kit ships no tag this cycle (above), so its ES debt
 *     has nowhere to land that would not be a page that never asked for it —
 *     which is exactly the mistake paving's registry recorded and C3711 paid
 *     off. It lands with the tag, on the tag.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and the one page on this hub that could not exist anywhere else.
    // Twelve kits count down to a wall closing and every one of them means the
    // INSIDE face. The outside face closes once too, and after it does, every
    // hole is a cut in finished siding.
    name: "Through My Wall",
    href: "through-my-wall.html",
    desc: "Everything somebody else needs through your wall before you close it. One row per hole: whose it is, what it is — a dryer vent, a line set, a hose bib, a light block, a camera, the meter — which elevation and a corner you can point at, whether it's marked, through, or through with flashing on it, and the gate it has to beat. Sent to the super and every outfit on it, elevation by elevation, while it's still a drill. After the corners go on it's a hole saw through a finished wall, a patch and a joint the owner sees from the driveway — and it looks like your work from the street.",
    chip: "#FEC8CC",
    audience: "Lead → GC super / HVAC / electrician / plumber / LV / gas / owner",
    pinned: true
  },
  {
    name: "Wall's Not Ready",
    href: "not-ready-to-side.html",
    desc: "No wrap on it, or it's torn. Windows in and never flashed. Sheathing loose, gaps, nothing to nail the corners to. You took the old wall off and there's rot behind it. Nobody's picked a colour. The grade's at the sheathing and there's nowhere to start. Walk it before the crew climbs, name what stops the wall in your own words, and send the two-button ask: fix it and tell me when, or direct me in writing to close it as it sits, where that call is theirs to make — because once it's closed, whatever's behind it is behind it, and the man who closed it owns how it looks.",
    chip: "#FEC8CC",
    audience: "Lead → GC super / PM / owner / architect"
  },
  {
    name: "Before I Close It",
    href: "rough-in-request.html",
    desc: "You're between dry-in and paint and everybody owes you something in a window that shuts once. Walk it a week out and send each outfit its own list — every vent, line set, bib, box and stub through the wall, the windows in and flashed, blocking where the corners and the bands land, the colour and the trim package decided in writing, the roof dried in above you, your elevation clear of cars and something to stand a jack on — each ask against your own gate, one message per outfit. The refusal is Wall's Not Ready; this page is how you never send it.",
    chip: "#FEC8CC",
    audience: "Lead → GC super / mech / EC / plumber / LV / gas / roofer / window / framer / painter / owner"
  },
  {
    name: "Walk Back",
    href: "answer-back.html",
    desc: "The super, the owner or the designer walked the house and sent a list — courses wavy under the deck door, J short at the rake, a light block proud of the band, two courses off colour. Paste it whole and go down it once: we'll hit it with a day on it, done already, not mine, or it's the wall — and send back one message they can close from, under their own numbers. It's the wall is the rung this trade needed: half of what gets written down is the substrate coming through the cladding, and hanging it again the same way puts it back.",
    chip: "#FEC8CC",
    audience: "Lead → GC super / owner / architect / designer"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "Working the outside of a building full of people — the ask to whoever holds it: which elevations and which days, the cars off the wall by an hour you name, ground that takes a jack or tell me it's a lift, where the trailer, the brake and the bin go, water and power, which doors people actually use, the gate code and the dog. And the heads-ups: jacks going up outside somebody's window, a walk under us that needs a closure, the meter coming off the wall, roof access to tie staging, a saw that runs all day — each one handed back to whoever owns it. Then put what they sent back against what you asked, and it names what they never answered.",
    chip: "#FEC8CC",
    audience: "Lead → owner / property manager / building engineer / GC super"
  },
  {
    name: "The Counter Call",
    href: "counter-call.html",
    desc: "Tomorrow's material called into the counter off your takeoff, not off your memory. Paste your lines the way you'd text them — the siding in your own words, with SAME LOT ticked where it has to come off the lot already on the wall — then run down what's never on the truck: siding starter strip, corners, J-channel, utility, F-channel, the eave soffit, blocks and hoods for every hole, trim coil with its back said, the downspout elbows and end caps. The colours of the house and the lot on its wall are typed once per job and ride every top-up. It counts nothing for you: a line with no count, a bare number on something sold two ways, an end cap with no hand or a piece that shows with no colour goes in the message as the counter's question, before it's a callback at three. Deliver it or will-call; field request, not a PO.",
    chip: "#FEC8CC",
    audience: "Lead → the supply house counter / their dispatch"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — what was behind the old wall, the elevation you were handed, the window that was never flashed, the day you couldn't hang, the walk that came back about the wall and not the siding, the hole somebody cut in your finished elevation, the house you handed back → dictate the mess at the truck, get back something the office can forward. Set up every one you write in a single block, and it never states a fastener, a gap, a clearance, a gutter size or a cause.",
    chip: "#FEC8CC",
    audience: "Lead → office / GC / owner"
  },
  {
    /* The spine tool that is not trade work — deeper chip, the masonry
       convention: this is the one page in the kit about the man, not the job. */
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are the weather's. Put yours next to theirs line by line — wages, fringes, dues, per diem, the truck — and put your real hours in, because a dollar an hour on a trade that stops for rain and stops for cold is a different dollar than the same dollar indoors.",
    chip: "#6E1F29",
    audience: "Installers · leads · owner-operators · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
