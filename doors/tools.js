/* DOORS & HARDWARE FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /doors/
 *   desc      one line — what document/request it helps a real door hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight (§TRADE EXPANSION: an unnamed absence is a hole, a
 * named one is a decision):
 *   - THE KEYING ASK (the-note) — the strongest unbuilt rung, and it was kept
 *     by the prune. He is holding forty-odd cylinders and nobody has told him
 *     keyed-alike groups, masters, or whether the construction cores come out
 *     — and the load-bearing line is the one nobody writes: DECIDE BY THIS
 *     DATE OR THESE GO IN CONSTRUCTION CORES AND RE-CORING IS A SEPARATE
 *     TRIP. Ships as the ASK only. The keying SCHEDULE is the consultant's
 *     document and is on this kit's permanent refusal list, so the page must
 *     never grow a groups table — build the note, never the schedule.
 *     Its half-measure already exists: "Nobody's said what the keying is" is
 *     a stop on Not Ready To Hang, which is the doorway version, not the ask.
 *   - HUNG AND ADJUSTED (row-log) — the openings-complete-by-floor count the
 *     super keeps asking for, and his own punch before the architect walks.
 *     Deferred at stand-up because Punch Back already answers somebody else's
 *     list and this is the same rows aimed the other way; it earns its page
 *     the first time a wish asks for a progress count, not before.
 *   - NO SHAPE #1 PAGE, AND THAT IS ONE DECISION RATHER THAN FOUR GAPS. The
 *     module-adoption grep reads this kit at 7 of the 12 shared modules its
 *     siblings carry, missing `checklist-request`, `dropoff`, `jobcard` and
 *     `pickfilter` — but all four ride on ONE page type, the material list
 *     (electrical/pull-list, flooring/dealer-call, framing/the-load,
 *     low-voltage/consumables, concrete/mix-order), and this kit ships none.
 *     THE REASON IS THE REFUSAL LIST: the obvious doors material list is the
 *     hardware, and hardware arrives as SETS somebody else numbers — building
 *     a picker for it would rebuild the consultant's document, which is the
 *     one thing this trade is not allowed to do.
 *     THE PAGE THAT IS STILL THERE, and it is the next DEPTH rung: the JOB BOX,
 *     the small stuff no set covers and every opening eats — shims, hinge and
 *     machine screws in the sizes he actually drives, silencers, filler and
 *     reinforcing plates, touch-up, blades, bits, taps. Generic, bought at a
 *     counter, owned by nobody, and it is the forget-list shape the flagship
 *     `av/consumables` already proves. Building it lights up all four missing
 *     modules at once, which is the tell that it is one rung and not four.
 *   - THE LANGUAGE LAYER (EN/ES) — shared/lang.js rides on the tag pages of
 *     twelve trades and this kit ships no tag (extra work is folded into the
 *     write-up library, the creative precedent). Its ES debt therefore lands
 *     on Not Ready To Hang, the page a heavily Spanish-speaking crew opens
 *     standing at an opening, and that is the first Lang.vocab candidate here.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and the one page on this hub that could not exist anywhere else.
    // Every other document this trade sends has a cousin on some other kit;
    // this one is the field walking back at the schedule before steel is cut,
    // and it is the whole answer to the objection that beat this trade twice:
    // it reproduces no column of the architect's document, it carries his own
    // tape readings, and the opening number rides as an ADDRESS.
    name: "Before They Ship",
    href: "before-they-ship.html",
    desc: "Walk the openings with a tape before frames get welded and send the distributor what the field actually is — the hand it really swings, the wall you really have, what's in the way, and the gate each one has to beat. One row per opening, grouped by floor, and a block that pastes straight in beside their own order. Your tape, your words; nobody's schedule gets re-typed.",
    chip: "#B7BEDC",
    audience: "Lead → distributor / inside sales",
    pinned: true
  },
  {
    name: "Set It For Me",
    href: "rough-in-request.html",
    desc: "Five kits on this board write doors into their own gate ladders; this is the door hand standing behind the words. Walk the floor a week out and send everybody who owes you an opening their own list — frames set where they're marked and grouted, rough openings true, blockouts before the pour, pipe into the frame before it's grouted, floor down, painted before hardware — each ask against your own gate, one message per outfit. The doorway refusal is Not Ready To Hang; this page is how you never send it.",
    chip: "#B7BEDC",
    audience: "Lead → GC super / mason / framer / EC / low-voltage"
  },
  {
    name: "Punch Back",
    href: "answer-back.html",
    desc: "The super walked the openings and sent a list. Paste it whole and go down it once — we'll hit it with a day on it, done already, not mine, not my call — and send back one message under their own numbers their side can close from. Not my call is the rung this trade needed: some answers live in the approved hardware submittal and with the people who stamp it, and saying so beats guessing at an opening.",
    chip: "#B7BEDC",
    audience: "Lead → GC super / architect / owner's rep"
  },
  {
    name: "Came Off The Truck",
    href: "came-off-the-truck.html",
    desc: "A flatbed gets signed for in the time it takes to walk it, and from that signature every dent is arguably yours. Count what landed against your own slip and send it the same afternoon: mark number, what came, what's wrong with it, and where you found it — because a dent found on the truck and a dent found three weeks later in the stack are two different conversations. Grouped by delivery, tallied, TSV for the office. Counts, never dollars.",
    chip: "#B7BEDC",
    audience: "Lead → distributor / your PM"
  },
  {
    name: "Not Ready To Hang",
    href: "not-ready-to-hang.html",
    desc: "Frame's not grouted, floor's not in, wall's not painted, nothing landed at the electrified openings — and a leaf hung to that gets adjusted twice and blamed once. Walk it before the cart comes off the truck, name what stops the hang in your own words, and send the two-button ask: fix it and tell me when, or direct me in writing to hang it as it stands.",
    chip: "#B7BEDC",
    audience: "Lead → GC super"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "Changing the doors on a building somebody else runs, while people are still in it — the ask to whoever holds the keys: the door and the hours, the freight, where leaves sleep between shifts, how many openings you're allowed to have apart at once, and who takes the cores at the end of the night. The alarm, the access system and the keys are theirs; every heads-up on this page ends by handing the process back to the man who owns it. Then put whatever they send back against what you asked, and it names what they never answered — because “yeah that’s fine” is not an answer to eight things.",
    chip: "#B7BEDC",
    audience: "Lead → property manager / building engineer"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — frames set wrong and nobody owning it, the opening you were told to hang anyway, the truck that came up short, what your number didn't cover, the day you couldn't hang, your own walk before the architect's → dictate the mess at the tailgate, get back something the office can forward. Set up every one you write in a single block, and it never states a label, a clearance or a setting.",
    chip: "#B7BEDC",
    audience: "Lead → office / GC"
  },
  {
    /* The spine tool that is not trade work — deeper chip, the masonry
       convention: this is the one page in the kit about the man, not the
       opening. */
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, per diem — and put your real hours in, because a dollar an hour on a job where you hung every opening twice is a different dollar.",
    chip: "#2F3C63",
    audience: "Installers · hardware hands · leads · anybody weighing a move"
  },
  {
    name: "The Long Pole",
    href: "long-pole.html",
    desc: "Frames, doors, hardware and glass in one list, with what each one holds up and the date it has to beat. One order number sits over four different shops on four different clocks — so the message asks ONE question, and it names which shop you are asking.",
    chip: "#8A6A2F",
    audience: "Lead / PM → the shop inside the house that has it"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
