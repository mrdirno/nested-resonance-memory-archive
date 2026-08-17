/* SITEWORK FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /sitework/
 *   desc      one line — what document/request it helps a real dirt hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight:
 *   - ~~THE MATERIAL CALL~~ — SHIPPED 2026-08-17 as `what-goes-in.html`, the
 *     tenth instance of shape #1 and the vocabulary build this note said it was:
 *     69 lines over seven sections, six units of issue that are not
 *     interchangeable, a fittings vocabulary per material, and structures that
 *     arrive by mark. WHAT THE BUILD LEARNED, kept instead of a checkmark: the
 *     differentiator was not the shape and not the size ladder, it was that the
 *     ORDER'S SECOND READING is the list of what gets BURIED — derived from the
 *     item data (`ditch`), never tapped — because every other order page on the
 *     rack is short a line and somebody drives to the counter, and short a line
 *     here is a re-dig. Masonry's RUN mechanism was stolen rather than
 *     re-derived, as the tie-in, INCLUDING the inverse case its first draft
 *     dropped. Both generalise to any trade whose order is consumed
 *     irreversibly.
 *   - THE WRITE-UP LIBRARY (docs.js). Its own document-spec vocabulary build,
 *     and shared/docspec.js has a contract the deploy asserts — a half-written
 *     library fails it, correctly. It is now the strongest unbuilt rung in this
 *     kit, and this is the ONLY trade of twelve without a write-up page. Not a
 *     fork of anything: a config of an engine that already ships.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the reason this trade is on the rack. electrical, plumbing
    // and gc all ship "before backfill" as the FIRST rung of their own gate
    // ladder — three whole trades counting down to a moment nothing on the job
    // publishes. The man closing it is the only one who has the time.
    name: "Before We Close It",
    href: "before-we-close.html",
    desc: "Run by run at quitting time — what's open, what's in it, what's holding it, and the time the dirt goes back. Tap each run up the ladder and send one message to everybody with something in that ditch. Three trades have been counting down to your backfill since the job started; this is the first page that gives them the time.",
    chip: "#FFDDA3",
    audience: "Foreman → super / EC / plumber / gas / LV",
    pinned: true
  },
  {
    // THE MATERIAL CALL, and it is the second rung this kit ships because it is
    // the one a dirt foreman opens most days. Everything else here is a message
    // he sends when something happens; this is the one he sends because it is
    // three o'clock.
    name: "What Goes In The Ground",
    href: "what-goes-in.html",
    desc: "Tomorrow's pipe, fittings, structures, stone, tape and tracer — off a list instead of off your memory. Count it the way you say it: 20 joint, 4 ton, 2 roll. Everything that gets buried comes out at the bottom of the message on its own, because a short count anywhere else is a trip to the counter and a short count here is a re-dig.",
    // Its own step on this kit's ladder — the other six are #FFDDA3 / #F2C97F /
    // #E0B368 / #CFA96B / #8A6718 / #7A5A16 and this sits in the one gap left.
    chip: "#B98F42",
    audience: "Foreman → the yard / the pipe supplier"
  },
  {
    name: "Before We Dig",
    href: "rough-in-request.html",
    desc: "Everything another outfit owes you before you break ground — the marks, the locates in hand, the grade to work to, the structures and pipe on site, the route in, the say-so on what happens to the spoil — with the gate each one has to beat. Walk it once, tap the rows, send one message per trade.",
    chip: "#F2C97F",
    audience: "Foreman → GC / survey / utility owner / suppliers"
  },
  {
    name: "What I'll Leave Open",
    href: "answer-back.html",
    desc: "The electrician or the plumber sent you a list of what has to be in this trench before it closes. Paste it, tap each line will do / in already / can't / need to know, and put the TIME on every yes — because a date doesn't help a man whose conduit has to be in before seven.",
    chip: "#E0B368",
    audience: "Foreman → EC / PC / GC"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Hit rock, found a line nobody marked, hauled off material nobody said was bad, or stood by while another outfit got out of your ditch? Write the tag before the dirt goes back — who told you, what came up, why it's outside your contract, crew, iron and material as counts, and what is NOT in this tag.",
    chip: "#8A6718",
    audience: "Foreman → super / PM"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "The ask you send whoever holds the gate — the day, the route in for a lowboy and a machine, where the spoil stacks, where the import lands, and the heads-up that keeps a float sitting outside a locked gate with a hoe on it. It's an ask, not a booking, and it says so.",
    chip: "#CFA96B",
    audience: "Sitework → GC / building engineer / property manager"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and the hours are not a given. Put yours next to theirs line by line — wages, fringes, dues, travel, per diem — and put your real hours in, because a dollar an hour on a spring you couldn't get in the ground is a different dollar.",
    chip: "#7A5A16",
    audience: "Operators · pipelayers · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];
