/* FLOORING FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /flooring/
 *   desc      one line — what document/request it helps a real floor hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, in the prune's own ranking, so the
 * next cycle does not read the gaps as oversights. All three are CONFIGS of
 * engines that already ship — none of them is new code:
 *
 *   1. WHAT IT READ (shape #3, shared/rowlog.js) — THE STRONGEST UNBUILT RUNG.
 *      He tests, writes the numbers on a scrap of drywall, and the scrap goes in
 *      the dumpster; what the rep gets is a phone photo of a meter face with no
 *      room, no date and no probe number. Once adhesive is spread that slab can
 *      never be tested again, so this log is the only artefact that still exists
 *      ninety days later — the exhibit behind the pinned letter. Add-row bar with
 *      meter and material sticky, grouped by area with a count per area, the
 *      limit off his own pail printed beside every line, and TSV so the rep and
 *      the super paste it into their sheet instead of squinting at handwriting.
 *      It is deliberately NOT half-built here: the pinned letter already carries
 *      the readings for ONE morning, and the log is the different job of carrying
 *      them for a month. It also has the longest refusal list in the kit — no
 *      threshold ever, and no label: never pass, fail, high, low or in-spec.
 *   2. THE DEALER CALL (shape #1, shared/checklist-request.js) — the page he
 *      opens most days, and the one that ruins a corridor forever. Three panels
 *      wrote it independently. It is a vocabulary build the size of the
 *      supply-house order (roll goods, carpet tile, plank and sheet, adhesive,
 *      base and trim, sundries — each with colour and dye lot, will-call or
 *      delivered, and the day it has to be ON the job rather than shipped), and
 *      the thing that would make it this trade's page rather than a supply-house
 *      form is the ORDER'S SECOND READING: everything that has to come off the
 *      same run — fills, transitions, stair parts, and the attic stock that is in
 *      the spec and never called in until close-out, by which time the run is
 *      gone. Derived from the item data, never tapped. Half-building that is
 *      worse than not building it, which is why it is not here.
 *   3. THE WRITE-UP LIBRARY (docs.js + write-up.html, shared/docspec.js). Its own
 *      document-spec vocabulary build, and the deploy asserts a contract that a
 *      half-written library correctly fails. Sitework shipped without it too and
 *      it is now owed on two trades. The prune put four separate panel proposals
 *      inside it rather than on the hub — the exclusions-and-clarifications
 *      sheet, the prep write-up that becomes the PCO backup, the shading call
 *      that is not a defect, and the substrate excluded from his warranty when he
 *      was directed to proceed anyway — because a second docspec engine on one
 *      rack is exactly the duplication that step exists to catch.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the reason this trade is on the rack. Five separate
    // panel proposals collapsed into this one letter — the largest convergence
    // the roster exercise produced. Named for the ASK rather than the condition:
    // "the floor's not ready" is a complaint, and the same sentence ending in
    // "give me the go in writing" is a document.
    name: "Give Me The Go",
    href: "give-me-the-go.html",
    desc: "The slab reads wet, the heat never ran, or the schedule and the plan don't agree — and he says put it in, we hand over Friday. Write it down before you spread glue: what you're standing on, what you measured, what your own instructions require, and what it costs you to sit. Ends the only way it ends — give me the go in writing, or tell me who's fixing it and by when.",
    chip: "#8FECFF",
    audience: "Lead → GC super / builder / dealer",
    pinned: true
  },
  {
    // The rung that closes a loop three other kits opened. av, gc and
    // low-voltage each write "before floor goes down" as a gate on their own
    // ladder, and none of the twelve has a flooring receiver in any roster.
    // Sending this publishes the date they have all been counting to.
    name: "Before It Goes Down",
    href: "rough-in-request.html",
    desc: "Everything another outfit owes you before you can start — the slab ground and patched, heat on and holding, old goods out, the room actually clear, jambs undercut, material on site and sitting in the space — with the gate each one has to beat. Walk it once, tap the rows, send one message per outfit.",
    chip: "#6FDCF5",
    audience: "Lead → GC / builder / other trades / dealer"
  },
  {
    name: "Punch Back",
    href: "answer-back.html",
    desc: "You're last in, so every list on the job ends up on you. Paste theirs, answer every line in their order — will do with a day on it, in already, not mine, or damage — needs a ticket instead of a punch item. Their numbers and their wording ride straight back, because their system owns the list.",
    chip: "#4FC8E6",
    audience: "Lead → GC super / builder / property manager"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Ground it, skimmed it, pulled cutback, undercut fourteen jambs, moved a fridge, or stood in the corridor because the room wasn't clear? Prep is where the whole margin lives and it's the work that never gets written down. Write the tag the day it happened — who told you, why it's outside your number, crew and material as counts, and what is NOT in this tag. En español también.",
    chip: "#2FA8C9",
    audience: "Lead → super / PM / the dealer who sold it"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask you send whoever holds the keys — the day, the route a twelve-foot roll can actually take, the freight lift and who holds the key, somewhere the material can sit in the space it's going into, and the one nobody else on this rack has to ask for: the building at temperature days before you get there. It's an ask, not a booking, and it says so.",
    chip: "#0E6E86",
    audience: "Flooring → GC / building engineer / property manager"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, travel, per diem — and put your real hours in, because a dollar an hour on a month you spent waiting on somebody else's building is a different dollar.",
    chip: "#0B5568",
    audience: "Installers · mechanics · leads · anybody weighing a move"
  },
  {
    // The write-up library (shape #4, shared/docspec.js). Not a form that makes a
    // document — a form that makes the AI SETUP that makes the document, forever.
    // Four panel proposals live inside it as documents: the exclusions sheet, the
    // prep write-up (PCO backup), the shading call, and the directed-to-proceed
    // record — plus the day report and the eight shared write-ups a floor sub
    // sends. It grades nothing: your reading prints beside your own limit and it
    // never says which one wins.
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — what your number didn't cover, the prep that becomes the change order, the shading call somebody's calling a defect, the day they told you to put it in anyway, the day report, turnover. Pick the one you're stuck with and get the exact instructions to paste into your AI once. Then dump the mess in the truck and get back something you can send. Never grades a reading, never calls a floor a defect — it writes down what you measured and what you did.",
    chip: "#3FB8D8",
    audience: "Lead → GC / dealer / office / customer"
  },
  {
    // Shape #3 (shared/rowlog.js), the strongest unbuilt rung in this kit's own
    // prune (§1 above). The pinned letter carries the readings for one morning;
    // this carries them for a month, and it is the only artefact that survives
    // the glue. Meter, limit and material carry row to row; grouped by area with
    // a count per area; the limit off his own pail beside every line; TSV out.
    // Longest refusal list in the kit — no threshold ever, and no label: never
    // pass, fail, high, low or in-spec. His number prints beside his own limit
    // and a human compares them.
    name: "What It Read",
    href: "what-it-read.html",
    desc: "Every moisture reading, by area, with the limit off your own pail beside each one. The scrap of drywall goes in the dumpster and the slab gets glued — this is the record still here ninety days later when the floor cups and everyone wants to know who owns it. Copy it for a spreadsheet. It never passes or fails a number: your reading prints beside your own limit and a human compares them.",
    chip: "#1C93B0",
    audience: "Lead / mechanic → your own file, the GC, the mill rep"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
