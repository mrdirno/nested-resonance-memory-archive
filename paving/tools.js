/* PAVING & STRIPING FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /paving/
 *   desc      one line — what document/request it helps a real crew produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight (§TRADE EXPANSION: an unnamed absence is a hole, a
 * named one is a decision):
 *   - THE LOAD LOG (row-log) — one row per truck off the plant: ticket number,
 *     time in, where it went down. It is the page every paving foreman keeps
 *     on the back of a ticket already, and it is NOT built, on purpose. The
 *     plant ticket is the numbered record and the scale is the system of
 *     record; a tally of tickets on our page is one wish away from a YIELD
 *     verdict — tons over area, "we're short a load", "the base is high" — and
 *     the doctrine lens named that edge in the panel (refusal 1 and 6 in
 *     trade.js). A judged call, not a gap: if a wish asks for it, it ships as
 *     a list of ticket numbers as addresses and never as arithmetic on them.
 *   - THE DAY RATE / T&M TICKET — electrical's engine, the sheet a crew signs
 *     when the super says "just do it and we'll sort it out." A rained-out
 *     half day with eighteen loads cancelled at the plant is exactly that
 *     sheet, and it was deferred for the stand-up's window, not for doctrine:
 *     it prices nothing, it counts men and hours and equipment in his own
 *     words. Building it lights up jobcard and the write-up library's "the day
 *     we couldn't pave" at once — one rung, not two.
 *   - THE LANGUAGE LAYER (EN/ES) — shared/lang.js rides on the tag pages of
 *     twelve trades and this kit ships no tag. The striping crew is heavily
 *     Spanish-speaking and its ES debt lands on Not Ready to Pave, the page a
 *     foreman opens standing on a wet base at six in the morning with the
 *     plant on the other line, and that is the first Lang.vocab candidate here.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and the one page on this hub that could not exist anywhere else.
    // Three of the four lenses named it independently: the man laying a plan
    // out on a finished surface with a tape and a chalk box, finding the sheet
    // and the lot don't agree, and needing a decision before paint — because
    // after paint it is a grind-out. It carries no count, no dimension and no
    // accessibility call of its own; that was the doctrine lens's condition.
    name: "Doesn't Fit",
    href: "doesnt-fit.html",
    desc: "You laid it out off the sheet and the lot disagrees — thirteen at the plan's width where it draws fourteen, the pole base eats one, the accessible pair lands on the hydrant, there's a lip at the walk. One row per place it doesn't fit: what the sheet draws there, quoted, what your tape found, what's in the way, and what you need decided — which one goes, shift the run, move the pair, re-draw it, or paint it as drawn in writing. Sent to the super, the civil or the owner before paint hits the mat. It's their count and their call; after paint it's a grind-out and an argument.",
    chip: "#FDF37A",
    audience: "Foreman / striper → GC super / civil / owner",
    pinned: true
  },
  {
    name: "Under the Mat",
    href: "under-the-mat.html",
    desc: "Landscape already wrote you a letter about his sleeves; this is you writing back to everybody. One row per thing somebody else has under your base before it rolls — whose it is, what it is, who told you and off which list, whether you saw it in and capped or only heard about it, and whether the iron's to grade or sitting low where it'll be under the mat. Grouped by area, a gate on every row, sent before the trucks are ordered. After the mat it's a saw cut, and you both know whose day that costs.",
    chip: "#FDF37A",
    audience: "Foreman → landscape / LV / electrician / plumber / sitework / GC super"
  },
  {
    name: "Before I Roll",
    href: "rough-in-request.html",
    desc: "You're the last trade on the lot and everybody owes you something. Walk it a week out and send each outfit their own list — the base proof-rolled with the soft spots named, the curb in and cured so the mat meets it without a lip, every lid and box raised to grade, the sleeves and the gate pipe in, the cars and the conex off your section, the set you're paving to and who answers at six, the lab called, the striping sheet at the current rev — each ask against your own gate, one message per outfit. The refusal is Not Ready to Pave; this page is how you never send it.",
    chip: "#FDF37A",
    audience: "Foreman → GC super / dirt / concrete / landscape / EC / LV / plumber / civil / lab / owner"
  },
  {
    name: "Walk Back",
    href: "answer-back.html",
    desc: "The super, the owner or the property manager walked the lot and sent a list — arrows backwards at the dock, the accessible symbol faded, a birdbath by the cart corral, seal tracked into the lobby, stall 14 short. Paste it whole and go down it once: we'll hit it with a day on it, done already, not mine, or it's the plan — and send back one message they can close from, under their own numbers. It's the plan is the rung this trade needed: a stall count, an arrow or a fire-lane length is a question for the civil and the owner, not for the man holding the striper.",
    chip: "#FDF37A",
    audience: "Foreman / striper → GC super / owner / property manager"
  },
  {
    name: "Not Ready to Pave",
    href: "not-ready-to-pave.html",
    desc: "The base pumps under the truck, the curb isn't cured, the lids are still low, somebody's still trenching across your section, there's a conex and six cars on it, the haul route's blocked and nobody's called the lab — and you've got a crew standing and loads ordered off the plant for six a.m. Walk it before the first truck, name what stops the paving in your own words, and send the two-button ask: fix it and tell me when, or direct me in writing to pave it as it sits — because a mat over a soft base is your warranty, and this note is the record of what was under it.",
    chip: "#FDF37A",
    audience: "Foreman → GC super / PM / owner's rep / civil"
  },
  {
    name: "Lot Closed Tonight",
    href: "lot-closed-tonight.html",
    desc: "You're sealing or striping half an occupied lot tonight and two hundred people park there. The notice to whoever runs it: which sections close and which stay open, the fire lane that stays open the whole time, where the cones and tape go, when cars can come back in your own words off your own sheet, and the asks — you tell the tenants, not me; a car still on it at seven, who moves it; the doors people actually use; nobody pulls a cone before I say; who I call at five if it rained. A notice, not a permit and not a traffic plan — those are theirs to hold.",
    chip: "#FDF37A",
    audience: "Striper / foreman → property manager / GC super / owner's rep"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "Working a lot that's full all day — the ask to whoever holds it: which sections empty of cars and by what hour, a route a dump truck and a paver actually make, where the rig and the trucks stage, where the sweepings go, which entrances stay open, and the heads-ups: we're closing a section — tell me who owns the closure and the tenant notice; the torch is running on the crack fill — who's your fire watch; the blower runs the first two hours. Then put whatever they send back against what you asked, and it names what they never answered.",
    chip: "#FDF37A",
    audience: "Foreman / striper → property manager / building engineer / GC super"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Told to pave over something you'd have called out, stand while somebody cleared the lot, or come back after the window moved? Write the tag before the mat cools — who told you, what came up, why it's outside your contract, crew and material as counts, and what is NOT in this tag. Once it's rolled, nobody can see what was under it. En español también.",
    chip: "#5E5300",
    audience: "Foreman → GC super / PM"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — the base you were handed, what was under your mat when it rolled, the day you couldn't pave, the layout that didn't fit and who decided, the car that drove on fresh seal, the paint tracked into the lobby, the lot you handed back → dictate the mess at the tailgate, get back something the office can forward. Set up every one you write in a single block, and it never states a temperature, a density, a count or a cure time.",
    chip: "#FDF37A",
    audience: "Foreman → office / GC / owner"
  },
  {
    /* The spine tool that is not trade work — deeper chip, the masonry
       convention: this is the one page in the kit about the man, not the job. */
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are the weather's. Put yours next to theirs line by line — wages, fringes, dues, per diem — and put your real hours in, because a dollar an hour on a job you paved at night is a different dollar than the same dollar on a day lot.",
    chip: "#5E5300",
    audience: "Crew · stripers · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
