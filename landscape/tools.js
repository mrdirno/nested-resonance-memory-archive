/* LANDSCAPE & IRRIGATION FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /landscape/
 *   desc      one line — what document/request it helps a real crew produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight (§TRADE EXPANSION: an unnamed absence is a hole, a
 * named one is a decision):
 *   - THE YARD ORDER (checklist-request) — the shape-#1 pull list the counter
 *     can work from: pipe, fittings, valves, heads, wire, boxes, soil, mulch,
 *     sod, staples, stakes, in the counts he took off his own walk. It is the
 *     strongest unbuilt rung and the FIRST DEPTH rung, and it was deferred for
 *     the stand-up's window, not for doctrine — a pull list computes no flow,
 *     no pressure and no coverage, it ticks what his own sheet already names.
 *     Building it lights up checklist-request, jobcard, pickfilter and dropoff
 *     at once, which is the same tell doors wrote down: one rung, not four.
 *     painting/store-call.html is the page to isomorph (unit of issue, the
 *     batch that doesn't go back — tinted gallons there, live plant material
 *     here).
 *   - THE ZONE WALK (row-log) — one row per zone, what he SAW when he ran it.
 *     Deliberately folded into Water's Yours ("what's running, what isn't") and
 *     the write-up library ("What I Left Running") rather than shipped as its
 *     own page, because a page that logs heads and coverage zone by zone is
 *     one wish away from a coverage VERDICT, and the doctrine lens named that
 *     edge — no startup page, no coverage page, no audit page. A judged call,
 *     not a gap: if a wish asks for it, it ships as a record of what he saw
 *     and never of whether it is enough.
 *   - THE LANGUAGE LAYER (EN/ES) — shared/lang.js rides on the tag pages of
 *     twelve trades and this kit ships no tag (extra work lives in the
 *     write-up library, the creative and doors precedent). Its ES debt lands on
 *     Not Ready To Plant, the page a heavily Spanish-speaking crew opens
 *     standing in a bed at seven in the morning, and that is the first
 *     Lang.vocab candidate here.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and the one page on this hub that could not exist anywhere else.
    // Every other document this trade sends has a cousin on some other kit;
    // this one is the man whose pipe has to get UNDER somebody else's work
    // before that work closes, and the only irreversible gate he owns. Concrete
    // already wrote the ask from its side and had to aim it at the plumber.
    name: "Where I Cross",
    href: "where-i-cross.html",
    desc: "Walk every place your pipe has to get under somebody else's concrete, paving or wall before it closes, and send it to whoever's pouring — where it crosses in your words, what's going through it, what it's under, the sleeve you're putting in off your own submittal, how far it sticks out, and the gate it has to beat. One row per crossing, grouped by area, a block that pastes in beside their pour. After the pour it's a core drill, and it's your money.",
    chip: "#A1CB86",
    audience: "Foreman → concrete / paving / dirt / GC super",
    pinned: true
  },
  {
    name: "Before We Plant",
    href: "rough-in-request.html",
    desc: "Three kits on this board built you a chip and none of them could write you a line; this is you writing back. Walk the job a week out and send everybody who owes you something their own list — sleeves before forms, the trench backfilled around your pipe with what you left, fine grade with the rock and trash picked, the POC live and the backflow where the plan puts it, power at the clock, the beds cleared of trade parking, an answer on the substitution — each ask against your own gate, one message per outfit. The refusal is Not Ready To Plant; this page is how you never send it.",
    chip: "#A1CB86",
    audience: "Foreman → GC super / dirt / concrete / plumber / EC / LA / nursery"
  },
  {
    name: "Walk Back",
    href: "answer-back.html",
    desc: "The LA, the super or the owner's rep walked it and sent a list — plants leaning, three missing, a head on the glass, zone 4 won't come on. Paste it whole and go down it once: we'll hit it with a day on it, done already, not mine, or it's the water — and send back one message they can close from, under their own numbers. It's the water is the rung this trade needed: a plant that's dry is telling you about the clock, not the planting, and that answer lives with whoever holds the controller.",
    chip: "#A1CB86",
    audience: "Foreman → landscape architect / GC super / owner's rep"
  },
  {
    name: "Not Ready To Plant",
    href: "not-ready-to-plant.html",
    desc: "The grade's been driven on all winter, there's base rock and busted block in the beds, no topsoil, it won't drain, no water on site, nothing at the clock, your sleeves never went in and the flatwork's poured. Walk it before the truck comes, name what stops the planting in your own words, and send the two-button ask: fix it and tell me when, or direct me in writing to plant it as it sits — because a plant that goes in that ground is your warranty claim.",
    chip: "#A1CB86",
    audience: "Foreman → GC super / builder"
  },
  {
    name: "Off The Truck",
    href: "off-the-truck.html",
    desc: "A nursery semi gets signed for in the time it takes to walk it, and from that signature every dead one is arguably yours. Count what landed against your own slip the same afternoon: what the tag says, what's short, what's not what you ordered, what came rootbound or dry, and where you found it — because a broken leader seen on the trailer and one found in staging on day six are two different conversations. Grouped by delivery, tallied, TSV for the office. Counts, never dollars.",
    chip: "#A1CB86",
    audience: "Foreman → nursery / yard / your PM"
  },
  {
    name: "Sub It Or Wait",
    href: "sub-it-or-wait.html",
    desc: "You can't get it. Their schedule line rides as an address — sheet, key, the way their schedule says it — then what the grower told you in the grower's words, the two or three you can get with the size the way you'd order it, and the date the answer has to land before the whole planting sequence moves. Approve one in writing under your own number, or tell me to wait — and if it's wait, who's watering what's already in. Nothing here is a design call; the plant list stays theirs.",
    chip: "#A1CB86",
    audience: "Foreman → landscape architect / GC super / owner's rep"
  },
  {
    name: "Water's Yours",
    href: "waters-yours.html",
    desc: "The day it's in and running, the water becomes somebody else's — who has the controller and where it is, what you set the clock to in your own words copied off the face, what's running and what isn't, and the ask: nobody kills the water or changes the clock without telling me, tell me the day it goes off for a freeze or a restriction, who waters the days we're not here, trucks and trades off the beds, and the date the maintenance clock starts off your own contract. The code goes by phone, never on the note.",
    chip: "#A1CB86",
    audience: "Foreman → owner's rep / property manager / GC"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "Working a campus that's full all day — the ask to whoever holds the gate: which entrance and the hours, where the trailer, the soil pile and the plant sit for a fortnight, where the water is, when a trencher or a blower can run and when it can't, and the heads-ups: a mower throws rock, a trench is going through a lawn people walk on, and the water will be off at the backflow — tell me who charges it and who tests it, because it isn't us. Then put whatever they send back against what you asked, and it names what they never answered.",
    chip: "#A1CB86",
    audience: "Foreman → property manager / building engineer / GC super"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — the ground you were handed, the sleeves nobody put in, the day you couldn't plant, what you found when they died, the truck that came up short, what you left running, the trucks that drove across your finish grade → dictate the mess at the tailgate, get back something the office can forward. Set up every one you write in a single block, and it never states a rate, a run time or why a plant died.",
    chip: "#A1CB86",
    audience: "Foreman → office / GC"
  },
  {
    /* The spine tool that is not trade work — deeper chip, the masonry
       convention: this is the one page in the kit about the man, not the job. */
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, per diem — and put your real hours in, because a dollar an hour on a job where you planted the same bed twice is a different dollar.",
    chip: "#355226",
    audience: "Crew · irrigation hands · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
