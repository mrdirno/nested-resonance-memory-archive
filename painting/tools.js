/* PAINTING FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /painting/
 *   desc      one line — what document/request it helps a real paint hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 *
 * WHAT THIS KIT DELIBERATELY SHIPPED WITHOUT, so the next cycle does not read
 * the gap as an oversight:
 *   - THE WET AREA NOTICE (the-note) — the 20-year prune KEPT it as the kit's
 *     seventh tool and stand-up shipped six: the painter's shutdown notice
 *     posted the other direction — area closed for spray or closed while wet,
 *     the no-touch and re-entry clocks as HIS stated lines off HIS own data
 *     sheet ("walls closed 2:40 · doors swing at 6 · nobody blue-tapes till
 *     Friday"), the occupied-day fields (intakes sealed, RTU off as directed,
 *     clear-the-floor), one receiver. The prune folded Spray Notice and the
 *     Recoat Clock INTO it, so build it as the merged page: closed-for-spray
 *     and closed-while-wet are one closure with one receiver, and the re-entry
 *     clock IS the notice's window lines. Its narrative half already lives in
 *     docs.js (the delay notice and the daily's clear-by line) — the note is
 *     the two-minute send. This is the strongest unbuilt rung in the kit.
 *   - THE LANGUAGE LAYER (EN/ES) — the tag pages carried Spanish to every
 *     trade at C3650 through shared/lang.js; this kit shipped no tag (the
 *     prune folded the extra-work story into the write-up library), so its ES
 *     debt lands on the pinned tool instead: Not Ready is the page a
 *     heavily Spanish-speaking trade opens at a doorway, and it is the first
 *     candidate for Lang.vocab treatment when the layer next expands.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TOOLS = [
  {
    // PINNED, and it is the reason this trade is on the rack. Ten of thirteen
    // kits write "before paint" into their own vocabulary — av and framing as
    // literal gate values — and nothing stood behind the gate. This is the
    // receiver materializing: the note from the doorway, at the exact moment
    // the finish sequence turns irreversible, because commencement is
    // acceptance and the first coat makes every condition under it the
    // painter's, forever.
    name: "Not Ready",
    href: "not-ready.html",
    desc: "The super says the rooms are ready. They aren't. Walk them before the crew sets up, name what stops paint in your own words — mud still soft, trades still in it, dings that aren't yours, your reading beside your own limit — and send the two-button ask: FIX it and tell me when, or direct me in writing to coat it as it sits. The first coat makes it mine; this is the record it wasn't.",
    chip: "#29FF29",
    audience: "Foreman → GC super",
    pinned: true
  },
  {
    name: "The Store Call",
    href: "store-call.html",
    desc: "The 6:30 text to the paint desk — your schedule's paint with sheen and base answered, the sundries off a list instead of off your memory, counted the way you say it: 2 gal, 1 five, a case. Everything the shaker touches gathers at the bottom where the desk can't skim past it, and anything that has to match what's up says so with the batch.",
    chip: "#29FF29",
    audience: "Foreman → Paint counter"
  },
  {
    name: "Coat Count",
    href: "coat-count.html",
    desc: "The 3:30 diary that wins the March callback: every coat as a row — where, which surface, which coat, what went on out of which batch, what your own meter read. The empties with the batch numbers leave in the dumpster tonight; this stays, and filtered to the visible film it's the touch-up map.",
    chip: "#29FF29",
    audience: "Foreman → the file / the office"
  },
  {
    name: "The Ding Ledger",
    href: "ding-ledger.html",
    desc: "From final coat to turnover, every ladder in the building lands on your finish — and without a date on each mark, every scuff is your punch item. Log the dings the day you find them: room, what got hit, who was in it as you saw it, the fix it takes. Grouped by trade, the tallies write your PM's back-charge for him — counts, never dollars.",
    chip: "#29FF29",
    audience: "Foreman → super / your PM"
  },
  {
    name: "Color Lock",
    href: "color-lock.html",
    desc: "Somebody picked a color standing in a hallway, and gallons get tinted on that sentence. Write it down while everyone still agrees it was said — who, the exact name, number, base and sheen as given, what schedule line it replaces, how much of the old is already up — and get CONFIRMED in writing before the shaker runs.",
    chip: "#29FF29",
    audience: "Foreman → designer / GC / owner"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The write-ups you put off — the wall you were told to coat anyway, the walk after final before the trades come back, who picked that color, the daily, the day you couldn't roll → dictate the mess at the tailgate, get back something the office can forward. Set up every one you write in a single block, and it never sets a number or says a surface was ready.",
    chip: "#29FF29",
    audience: "Lead → office / GC"
  }
];
