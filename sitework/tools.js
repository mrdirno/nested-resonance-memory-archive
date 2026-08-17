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
 *   - THE MATERIAL CALL (pipe, fittings, structures, rock, bedding sand, fabric,
 *     tape and tracer, plates). It is the ninth instance of shape #1 and it is a
 *     VOCABULARY BUILD the size of the supply-house order and the yard call —
 *     units of issue that are not interchangeable (joints, each, ton, yard,
 *     roll, bundle), a fittings vocabulary per material, and structures that
 *     arrive by mark. Masonry's yard call is the record on this: half an order
 *     list is worse than none, because a man who calls one in off a list missing
 *     a line stops opening the list.
 *   - THE WRITE-UP LIBRARY (docs.js). Its own document-spec vocabulary build,
 *     and shared/docspec.js has a contract the deploy asserts — a half-written
 *     library fails it, correctly.
 * Both are the strongest unbuilt rungs in this kit. Neither is a fork of
 * anything: they are configs of engines that already ship.
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
