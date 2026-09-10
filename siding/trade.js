/* SIDING & EXTERIORS FIELD TOOLKIT — the trade config.
 *
 * TRADE #18, AND THE FIRST ONE PICKED BY BEING VETOED BY NOBODY RATHER THAN BY
 * WINNING A LENS. Four independent lenses — a field hand, a population count,
 * the doctrine lens that reads the book, and the boundary lens that reads every
 * shipped items.js — scored three candidates and came back:
 *
 *     EXTERIORS     66 · 76 · 61 · 33   sum 236   vetoed by NOBODY
 *     FINAL CLEAN   31 · 41 · 84 · 46   sum 202   VETOED by the field hand
 *     INSULATION    78 · 45 · 34 · 24   sum 181   VETOED by doctrine
 *
 * It was first on exactly one lens and second on two. Every other candidate
 * took a veto, and both vetoes were substantive rather than taste:
 *
 *   THE FIELD HAND KILLED FINAL CLEAN: "no gate, no irreversible moment, one
 *   document a week and it's an invoice." He looked for a milestone rung naming
 *   a clean across all 17 kits and found zero. And the boundary it would serve
 *   is already served from the sending side — flooring/items.js:201 and
 *   painting/items.js:468 both carry { v: "clean", label: "Final clean" }, so a
 *   flooring or painting foreman can already address the cleaner today.
 *
 *   DOCTRINE KILLED INSULATION, and the reasoning is the one that matters for
 *   every future pick: the refusal list takes the CORE rather than the edge.
 *   The insulation certificate is a posted, regulated instrument and the AHJ
 *   owns the card; the bag count needs a coverage table and an R-value; safing's
 *   entire value is a listed system number — the same rule that killed steel at
 *   #13 and fire protection with it. What survives the refusal is the generic
 *   rack. Its kill-in-waiting is "just put the R-value in", and unlike paving's
 *   ADA number, an insulator cannot quote a sheet instead: the R-value IS his
 *   document. Recorded, because insulation is a real trade and a later cycle
 *   will want to re-hear it — it needs a document class we do not have yet.
 *
 * THE TWO DISSENTS ARE THIS DIRECTORY'S DESIGN CONSTRAINTS, not footnotes:
 *
 *   THE FIELD HAND (66, second) refused the candidate AS BRIEFED: "it isn't one
 *   trade. Seamless gutter runs coil off a machine and does four houses a day;
 *   siding is on one house for a week; trim is interior. One items.js cannot be
 *   three crews' own words." His fix is this kit's scope, taken whole: SIDING &
 *   TRIM is the spine, GUTTERS ride as a section inside it, and the interior
 *   trim carpenter is not this man — he is framing's.
 *
 *   DOCTRINE (61, second) named the real risk: "three of its four documents are
 *   already written on a neighbour's kit — roofing/items.js:699 'Soffit /
 *   intake vent', :231 'Gutters pulled before we set the metal' — picking it at
 *   #18 buys a kit whose best three pages exist next door." So every page here
 *   had to answer one question first: can roofing already write this? The
 *   pinned page is the one where the answer is no, and the material order and
 *   the tear-off findings are scoped to the WALL, never to the roof edge.
 *
 * THE BOUNDARY LENS PUT IT THIRD (33) AND THAT IS NOT A KILL — it is the
 * flooring condition. flooring/trade.js:11 records the precedent in its own
 * words: "FLOORING WAS NOMINATED BY NOBODY — zero, the same as glazing,
 * insulation and demo — because a receiver roster can only name a party you
 * hand paperwork to." Flooring shipped at #13 with zero votes and a skeptic who
 * said "I could not kill it." This trade has ONE chip on the whole rack
 * (roofing/items.js:147 `{ v: "gutter", label: "Gutter / siding" }`) with no
 * ask routed to it, and roofing/items.js:231 — "Gutters pulled before we set
 * the metal" — is a line of exteriors work bundled into a letter addressed to
 * the SOLAR contractor, because there was nobody else to send it to.
 *
 * AND THE THING THE COUNT COULD NOT SEE, which is what actually justifies the
 * pick: between the framer closing the wall and the painter coating it, NOTHING
 * ON THE RACK OWNS THE OUTSIDE OF THE BUILDING. Grep framing/items.js for
 * sheathing, housewrap, weather barrier, WRB, siding — it returns empty. Twelve
 * kits count down to a wall closing ("Before rock goes up", "Before the wall
 * closes", "Before second side goes on", "Before we close one side") and every
 * one of them means the INSIDE face. The outside face closes too, it closes
 * once, and no hub owned that day.
 *
 * WHO HE IS. The crew hanging the outside of the building: fibre cement, vinyl,
 * engineered wood, board-and-batten, panel and lap, the trim that goes with it —
 * corners, bands, frieze, rake, fascia, soffit — and the seamless gutter hand
 * who comes off the same truck on a lot of outfits and off his own on the rest.
 * Residential re-side and new construction, light commercial, three or four on
 * a crew, pump jacks or a lift, a brake in the driveway and a coil trailer. He
 * works between DRY-IN and PAINT, outdoors, in whatever the weather is doing.
 *
 * WHAT THIS HUB IS NOT, decided before a line was written:
 *   - NOT THE ROOF. Drip edge, starter, step and counter flashing, ice-and-
 *     water, the roof-to-wall detail: roofing/ owns all of it and ships pages
 *     for it. This kit stops at the wall and says so on every page that gets
 *     near the edge.
 *   - NOT INTERIOR TRIM. Base, case, crown and the door jambs are the framing
 *     and carpentry kit's. "Trim" in this directory means EXTERIOR trim.
 *   - NOT STUCCO, EIFS OR PLASTER. A different trade with a different failure
 *     mode and a wet-set schedule; it took a boundary veto at #17 and it is not
 *     quietly absorbed here.
 *   - NOT WINDOWS. He flashes and trims AROUND them and is forever the man who
 *     gets blamed for them; the glazier and the window supplier own the unit,
 *     the warranty and the installation instructions. This kit gives him the
 *     words to say what he found, never a call on somebody else's unit.
 *   - NOT THE MAINTENANCE / REPAIR ROUTE. The one-square repair, the storm
 *     chase, the insurance scope: an adjuster's numbered document and a route
 *     sheet, scoped out the way landscape scoped out the spray log and paving
 *     scoped out the striping route.
 *
 * THE NAME COLLISIONS, and they are rules for every word in this directory:
 *   - "SOFFIT" on this rack already means framing's INTERIOR dropped soffit
 *     (framing/items.js:141, :189, :242, :656) and roofing's intake vent
 *     (roofing/items.js:699). Ours is the EXTERIOR soffit under the eave, and
 *     it is never written bare — it is "the eave soffit" or "soffit and fascia".
 *   - "GUTTER" on this rack already means concrete's and paving's CURB AND
 *     GUTTER (concrete/items.js:614, paving/items.js:195) and landscape's
 *     street gutter. Ours is always "the gutter" with a downspout in the same
 *     breath, or "eavestrough" where his crew says that.
 *   - "TRIM" is framing's interior trim unless the word EXTERIOR is on it.
 *   - "PANEL" is electrical's load centre on twelve kits. Ours is a siding
 *     panel and never appears bare.
 *   - "LEADER" is electrical's fish leader (electrical/items.js:191) and
 *     landscape's broken plant leader. Say DOWNSPOUT.
 *
 * THE HARD REFUSAL — not negotiable by a later cycle:
 *   1.  NO WIND OR DESIGN-PRESSURE RATING, exposure category, or "rated for"
 *       statement of any kind, for cladding, trim, gutter or fastener.
 *   2.  NO FASTENER SCHEDULE — no nail type, length, gauge, spacing, edge
 *       distance, penetration depth or pattern, and no "how many per board".
 *       The manufacturer's published instructions own that, and on most of this
 *       trade's products the warranty is written against them by name.
 *   3.  NO MANUFACTURER INSTALL SPEC RESTATED AS OURS — no expansion gap, butt
 *       gap, overlap, exposure, course height, clearance to grade, to a roof,
 *       to a deck or to a hard surface. A picker structures what HE reads off
 *       HIS printed instructions, cited as an address, and never our number.
 *   4.  NO FLASHING DETAIL, pan detail, sill-pan geometry or WRB lap sequence
 *       of ours. He photographs and describes what is there or is not there.
 *   5.  NO GUTTER OR DOWNSPOUT SIZING, no rainfall intensity, no roof-area-to-
 *       outlet math, no hanger spacing, no slope-per-foot. That is a published
 *       table and an engineered calculation, and it is not ours.
 *   6.  NO LEAD DETERMINATION AND NO ASBESTOS DETERMINATION, PERMANENTLY. This
 *       trade tears the outside off houses built before 1978 and off houses
 *       wearing asbestos-cement shingles, and nothing on any page may say a
 *       surface is or is not lead-bearing, is or is not asbestos, is safe to
 *       cut, sand or remove, or that a job is or is not RRP work. The page
 *       records the year the OWNER states, what the SURFACE looks like, and
 *       that testing and the certified firm are somebody else's — always.
 *   7.  NO MOISTURE, ROT OR STRUCTURAL VERDICT. "The sheathing is rotten and
 *       the framing is gone" is an engineer's and an inspector's call. He says
 *       where he found it, how big it is off his own tape, what it looked like,
 *       and photographs it. He never says why it happened or who caused it.
 *   8.  NO MOULD CALL of any kind, and no remediation instruction.
 *   9.  NO CODE CALL, clearance requirement, permit determination or inspection
 *       verdict. The AHJ owns the card.
 *   10. NO WARRANTY STATEMENT — never that an install is or is not warrantable,
 *       compliant, or that a manufacturer will or will not honour anything.
 *   11. NO PRICE, RATE, UNIT COST, SQUARE COUNT DERIVED FROM A DRAWING, OR
 *       INVOICE. Counts are counts he typed off his own tape.
 *   12. NO RELEASE VERDICT, EVER: nothing says the wall is closed, complete,
 *       weathertight, water-tight or accepted.
 * Every refusal above is a place where the honest tool is a picker that
 * structures what the USER states off his own tape, his own printed
 * instructions, his own eyes and his own contract. We ship that, every time.
 *
 * THE HONEST DEMERITS, written at stand-up so no later cycle rediscovers them:
 *   (1) TWO CREWS, and the field hand said so before it was picked: the siding
 *       crew is on one house for a week and the seamless gutter hand does four
 *       houses a day. Gutters ride as a section here and that is a compromise,
 *       not a solution; if a gutter wish ever arrives, it is the trigger to ask
 *       whether he is his own trade rather than to bolt a second voice onto
 *       this one.
 *   (2) ONE ORPHAN CHIP on the entire rack, and its owner (roofing) already
 *       speaks half this vocabulary. Every page had to clear "can roofing
 *       already write this?" and two candidate pages were cut when it could.
 *   (3) THE HEADCOUNT IS A RECONSTRUCTION. The population lens put this first
 *       and then named its own weakest input: there is no clean occupation code
 *       for a siding installer — they sit across carpenters, roofers, sheet
 *       metal and labourers — so its 100k-180k is a reconstruction and the
 *       midpoint was carrying the argument. It said so; it is recorded here.
 *   (4) HIS GATE IS OWNED AT THE BOTTOM AND BORROWED AT THE TOP. "Before we
 *       side it" is nobody's rung on any shipped ladder; dry-in is roofing's
 *       day and he waits on it. What he owns is the closing: after the wall is
 *       on, every hole through it is a cut, a patch and a caulk joint you can
 *       see from the driveway.
 *   (5) THE FIRST WISH WILL BE A NUMBER. "How far off the grade", "how much
 *       gap", "what size gutter", "how many nails" — every one of them is
 *       refusal 2, 3 or 5, and the answer is permanently no.
 *
 * Note what is NOT here: a copy of the runtime. shared/toolkit.js is
 * trade-agnostic and this file is the whole of what makes it the siding kit.
 *
 * Load order on every page:
 *   <script src="trade.js"></script>
 *   <script src="tools.js"></script>
 *   <script src="../shared/toolkit.js"></script>
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_TRADE = {
  // Goes into the `trade` column on every wish — this is how the loop knows
  // which toolkit a request belongs to.
  slug: "siding",

  name: "Siding & Exteriors Field Toolkit",

  /* THE SIBLING RULE: an icon is GEAR the trade carries, never the thing it
     builds. The brake and the aviation snips are what this crew actually
     carries and neither has a glyph, so it falls to the hammer — and the pair
     reads right, because framing took the SAW. A house or a wall would be the
     thing he builds; a ladder is roofing's chip already. */
  icon: "🔨",

  // ONE WORD, like every sibling. The schedule says "siding", the super says
  // "my siding guy", the sub agreement says "siding and exterior trim". Never
  // "exteriors" alone — that is a category, not a trade anybody calls himself.
  brandLead: "Siding",
  brandTail: "Field Toolkit",

  /* THE ACCENT, AND THE FIRST CHIP ON THIS RACK PICKED BY HUE BAND ALONE.
     Eighteen chips deep, this ran the doors/landscape/paving precedent — CIELAB
     distance to every shipped chip plus the 7:1 bar against the #242A31 nav,
     swept across the whole HSL solid — and the sweep came back with a finding
     rather than a colour: THE RACK IS FULL. At a chroma that still reads as a
     colour, the widest gap anywhere in the solid is dE2000 18.0, against a rack
     whose OWN widest existing pair is 17.7. There is no open corner left; there
     are only gaps the same size as the ones already there.

     So it was picked on the hue histogram instead, which is unambiguous. Sorted
     by hue, the eighteen chips leave exactly four gaps over 30 degrees, and
     three of them sit BETWEEN two chips of the same family (concrete's green to
     hvac's teal; framing's periwinkle to creative's orchid; creative's orchid
     to roofing's pink). The fourth is 44 degrees wide, it wraps 330 to 14, and
     it is the one band this rack has never had: RED. This chip is the only red
     on the board.

     It is deliberately a PALE, chalky, clay red rather than a saturated one,
     and that is a usability call rather than taste: the accent paints the well
     button and the left border of every card, and a saturated red button reads
     as a warning in a kit whose whole job is to send somebody a calm message.

     THE BARS, hand-picked and measured, not computed at runtime (color-mix()
     is not safe on the old Android browsers these pages land on):
       accent on the #242A31 nav   9.89:1  (bar 7)
       accentInk on accent        12.28:1  (bar 9)
       white on accentDeep        11.11:1  (bar 5)
       chroma                       20.5   (above doors' 16.2, the rack's lowest)
       dE2000 to nearest chip       16.2   (roofing; rack median pair is 12.3)

     AND A CORRECTION FOR EVERY CHIP NOTE ABOVE THIS ONE: the dE figures this
     book has been recording — 28.9, 29.1, 31.0, 34.6, 40.0 — are dE76, not
     dE2000, and no chip note ever said which. Measured in dE2000 the rack's
     tightest pair is concrete/gc at 7.9 and its widest is electrical/flooring
     at 17.7; paving's celebrated "29.1 to av's gold" is 15.1, which is
     mid-pack rather than a record. Nothing shipped is wrong — the ordering the
     old numbers produced is broadly the same — but a 29 that is really a 15
     invites the next cycle to think it has room it does not have. State the
     metric. */
  accent: "#FEC8CC",
  accentInk: "#2A0E10",
  accentDeep: "#6E1F29",
  accentTint: "#FFF1F2",

  // THE CREW AND THE LEAD, because on most outfits the owner is on the wall.
  // The office is where the change order goes, not where the message is
  // written — and on a re-side the receiver is frequently the HOMEOWNER, which
  // is the one thing that makes this chain different from every sibling's.
  chain: "the crew / the lead / the owner or the GC",

  // The four VALUES are CHECK-constrained in the DB — relabelled for this
  // trade, but the values stay tech / project_manager / leadership / other.
  roles: [
    ["tech", "Installer / crew"],
    ["project_manager", "Lead / foreman"],
    ["leadership", "Owner / estimator"],
    ["other", "Other"]
  ],

  wishTitleHint: "e.g. The list of holes everybody needs through my wall before I close it",
  wishPurposeHint: "e.g. We wrapped and started hanging on Tuesday and on Thursday the HVAC guy showed up wanting a line set and a dryer vent through the elevation I'd already closed, and the electrician wanted two more receptacles and a light block. Every one of those is now a cut in finished siding and a caulk joint the owner can see from the driveway. I want one page where I walk it before I close and write down every hole somebody else needs, whose it is, where it is off a corner I can point at, and whether it's in and flashed or just marked — and send it to the super and every one of them, so nobody can say they told me…"
};
