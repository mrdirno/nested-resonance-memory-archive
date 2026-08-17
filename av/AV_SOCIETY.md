# AV SOCIETY — the self-building AV Field Toolkit (loop doctrine)

The AV Field Toolkit builds itself: AV techs, PMs and leadership drop **wishes**
in the wishing well, and the P0 loop builds the ones that pass the bar into real
pages. This is the doctrine the loop reads every AV cycle. Live:
`https://mrdirno.github.io/nested-resonance-memory-archive/av/`.

## THE FLYWHEEL
`wish (well) → private queue (Supabase av_tool_requests) → loop builds the good
ones → new tool page ships → more people use it → more wishes`. The users are
prompting the system to build their own tools. Every tool here started as a wish.

## THE STRICT BAR (build it ONLY if ALL hold)
A wish gets granted only if a real tech/PM/owner would actually use it. Judge hard:
- **Practical, not theoretical** — a thing done on real jobs, not a concept.
- **Targeted & common** — one clear job, the stuff most people in AV deal with.
- **Speaks the trade's language** — real terms, part numbers, shortcuts, and the
  document formats techs / PMs / leadership already use. No made-up jargon.
- **Fewer steps** — it makes a real task *faster* and easier; it NEVER adds work
  or ceremony. Decreasing steps for everyone is the whole point.
- **Bridges the handoff** — helps send a clean request/spec up or down the chain
  (tech → PM → leadership and back), in what the receiver expects.
- **The test:** "would I actually use this to send something to my boss, PM, or
  techs?" If no, DECLINE with a one-line reason.

Good example (the operator's): a **cable-types picker** — HDMI (2.0/2.1, lengths),
Cat patch (5e/6/6a, shielded/UTP), fiber (OM3/OM4/OS2, LC/SC), pick the ones for a
job and copy a clean spec to the PM. Bad: anything "cute", a theoretical calculator
nobody asked for, or a tool that needs a login/among-us gimmick to feel clever.

## SEED ROSTER — "our own framework": build these out over time (well-empty cycles)
Don't only wait for wishes. When the well is empty, build the next tool from this
CURATED roster, chosen by leverage × how often a real crew needs it. Each is a
HYPOTHESIS — it ships only if it passes THE STRICT BAR above; drop any rung that
doesn't. Wishes RE-RANK and EXTEND this list (people "wishing better"). Keep
**Consumables pinned at #1 for now** (the operator's own; `pinned:true` in tools.js).
1. ~~**Cable-types picker**~~ — **SHIPPED 2026-08-04** as the **Cable & Adapter List**
   (`av/cable-list.html`), and it arrived as a WISH rather than a roster pick. 8 families
   (HDMI · patch · USB · adapters · audio · DP/legacy · fiber · rack power), each item
   carrying its own axes, plus clone-a-line, the shop's finish standard typed once, and a
   per-line alternate ask.
2. **Gear checklist by room type** — huddle / conference / boardroom / classroom → the kit to pull.
3. **Rack elevation / build note** — RU heights + gear → a rack elevation spec.
4. ~~**Connector & adapter finder**~~ — **DROPPED as scoped.** "Source X → display Y, what
   adapter?" is a RECOMMENDER, and §SAFETY forbids us answering it: we would be asserting
   an electrical/protocol claim (active vs passive, direction, HDCP) we cannot stand behind,
   on the exact question where being wrong costs a truck roll. The adapter FAMILIES now live
   as a picked category on the Cable & Adapter List, where the tech states the part. Re-scope
   or leave dropped — do not resurrect it as a recommender.
5. **Device-label / naming generator** — one consistent naming scheme across a job.
6. **Punch / deficiency list** — walk the room, list what's left → send the PM.
7. **Change-order / scope note** — an out-of-scope ask → a clean CO request.
8. **Site-survey checklist** — power / network / mounting / sightlines, before install.
9. **RMA / warranty request** — a failed unit → a complete RMA to send.
10. **Display size & viewing-distance** — room depth → recommended display size.
11. **AV network IP / VLAN planner** — assign device IPs cleanly for an AV subnet.
12. **Field Report Setup** — SHIPPED (`report-builder.html`): builds a role-tailored
    AI daily-report assistant to paste into Gemini/Claude/GPT. NEXT: a general
    ISOMORPHIC version — "type the document you want, get production-grade custom
    instructions for it" (apply the universal principles to ANY target) + a
    searchable template library.
13. **Room / equipment breakdown** — upload a spreadsheet / BOM / room schedule →
    a clean per-room-type equipment list, one per page (and, where feasible, a
    downloadable zip). Pure client-side parse; one of the biggest documentation
    time-sinks. Uploads never leave the browser.
14. **Bug / improve intake** — "wish it better" and "report a bug" are first-class
    in the well (a `kind` on every wish): people surface issues, the loop fixes and
    improves. Aldrin cannot work every hour — the well + loop are how the toolkit
    self-heals while he's up a ladder hanging TVs.

## NON-CLUTTERY — the discipline (operator 2026-08-03)
- **ONE job per tool.** If a tool tries to do two things, it is two tools.
- The hub stays a single clean ordered grid (pinned → favorites → rest). No feature
  bloat, no cute chrome, no walls of options. A crew opening it on a phone at a job
  site must be usable in seconds.
- Every roster rung AND every wish faces the SAME criteria: would a real tech/PM use
  this to send something to their boss/tech, FAST? If not, it does not ship.

## THE BUILD PROCESS (one wish per cycle, watertight)
1. `python3 /Volumes/dual/_vault/automation/scripts/av_wishing_well.py --list` —
   read new wishes (oldest first). Empty → do a self-directed toolkit/collage
   increment instead (COLLAGE_EVOLUTION.md), don't force it.
2. Pick the single highest-leverage wish that passes the bar. `--claim <id>`
   (new → building) so no other cycle double-builds it.
3. Build a **self-contained** page `av/<slug>.html` in the same field/industrial
   style, that **includes the shared runtime**:
   `<script src="tools.js"></script><script src="av.js"></script>` (so it gets the
   nav + wishing well + self-aware date for free — `AV.today()/AV.todayStr()`).
   Keep tool pages FLAT in `av/`. The output is copy-paste-able to chat/email.
4. Add one line to `av/tools.js` (the registry) — the hub grid + nav pick it up.
5. QC like the rest of the toolkit: `node --check` the inline JS, no third-party
   CDN / no origin-absolute paths, mobile-friendly, actually does the job. For a
   pure algorithm, a unit sweep (see fill.ts pattern).
6. Ship: commit BY PATHSPEC (never `git add -A`), push → the deploy runs (av/ is
   staged into the Pages artifact by deploy_bridge.yml). Verify LIVE (curl 200 +
   the page works). Then `--ship <id> --url <live-url>`.
7. If the wish fails the bar or is spam/honeypot: `--decline <id> --reason "..."`.

## CREDIT — the Wall of Wishes (living, un-erasable ledger)
Every built wish CREDITS the person who wished it, permanently. On ship, in the
SAME commit that ships the tool:
- Append ONE entry to `av/credits.json` (APPEND-ONLY — never rewrite or remove):
  `{ tool_name, tool_href, wisher, company, role, wished_date, shipped_date, shipped_commit }`
  (`shipped_commit` anchors the credit to a verifiable git object — fill it in a
  quick follow-up commit if you only get the SHA after committing).
- If the wisher chose ANONYMOUS (no name on the request), credit them as
  `"an anonymous AV <role>"` — honor the wish, protect the identity. Never invent a
  name; never publish the email (notification-only).
- Also add a one-line credit ON the tool page: "✦ Wished into existence by
  &lt;name / an anonymous AV tech&gt;." The credit thus lives in TWO committed places.
The immutability IS git — the ledger is public, hash-chained, forked and archived,
so a credit can never be quietly erased. `av/credits.html` renders the Wall. Only
the honored credit goes here — never request contents or the ranking.

## THE PANEL — a wish is judged by a panel, not one agent
"Only if our smartest AI panel deems it a good addition." Before building a
non-trivial wish, cast a small multi-agent JUDGE PANEL (a Workflow): 2–4 agents
scoring the wish independently against THE STRICT BAR from diverse lenses (a
working AV tech · a PM · a "would this actually get used / does it cut steps"
skeptic). Build only on panel agreement; otherwise `--decline` with the panel's
reason. The panel keeps the quality bar objective and defensible — and it is what
gives a Wall-of-Wishes credit its weight.

## SAFETY — non-negotiable (operator 2026-08-03: "emphasize safety and backup,
## look for edge cases that could screw us")
- **Only self-contained, client-side static tool pages.** NEVER build anything
  that collects passwords / payment / credentials, does server-side work, calls
  an external API with a secret, or stores PII beyond the well. No account
  creation. No money movement.
- **The queue is PRIVATE.** NEVER publish request contents, requester names /
  companies / emails, the ranking, or the demand data — anywhere. It is the moat
  and it is people's data. (RLS already blocks anon reads; the loop reads via the
  service role only.)
- **Liability guard.** A field-doc tool that ships a WRONG value (wrong cable,
  wrong rating) costs money on a real job. Any tool whose output feeds a purchase
  or a safety/compliance decision carries a short "double-check before you order /
  not a substitute for code or the manufacturer's spec" line. If a wish would need
  authoritative certified data we don't have, decline or scope it to "picker +
  double-check", never present guesses as fact.
- **Never impersonate** a real company, product line, or standards body.
- **One tool per cycle** — a flood of wishes can't spam the toolkit; the bar +
  this rate-limit keep quality up.
- **Back up before you touch data:** `av_wishing_well.py --dump` snapshots the
  whole queue to `automation/scripts/av_wishing_well_backups/`. The helper is
  non-destructive (status transitions only, never DELETE) and audits every action
  to `av_wishing_well_actions.log`. Supabase PITR is the second layer.
- **Fail-soft:** if the well/Supabase is unreachable, skip well-processing this
  cycle (the helper exits non-zero) — never hang, never guess, never lose a row.

## STRATEGY (private — do NOT expand here)
The open/closed call, monetization, moat and order-N consequences live in the
PRIVATE strategy note `operator/AV_TOOLKIT_STRATEGY.md` in the vault — NEVER copy
that into this public repo. One line that IS load-bearing for the loop: **open the
tool pages, keep the engine + the wishing-well demand data private** (RLS already
enforces the data half). Publish finished tools only — never request contents,
requesters, or the ranking.

## TRADE EXPANSION — this is the reference implementation of a TRADE TOOLKIT
(operator 2026-08-03) The whole structure — a clean hub, a handful of dead-practical
tools, a wishing well, this self-building loop, the credit ledger, the strict bar —
is TRADE-AGNOSTIC. The growth lever is to ISOMORPH it to other trades (plumbing,
electrical, HVAC, low-voltage, GC, fire/life-safety, …), each removing THAT trade's
own paperwork/communication friction. Mechanics:
- **Demand-driven.** Every wish carries a `trade`; when wishes from a new trade
  accumulate (or the operator names one), that trade is the next isomorph.
- **The isomorph** (a loop cycle or a small Workflow): create `<trade>/` beside
  `av/` with the SAME structure — hub + the shared runtime + a wishing well scoped
  to that trade + a seed roster of THAT trade's dead-practical tools in THAT trade's
  language + a credit ledger. GENERALIZE the shared runtime to read a per-trade
  config (name · slug · palette · registry) rather than fork it — one runtime, many
  trades — and stage each `<trade>/` into the Pages artifact + assert it, exactly as
  `av/` is. A top-level trades hub lists them.
- **AND THE COMMONS, IN THE SAME CYCLE — this list not naming it is how the hole got
  dug twice.** A new trade is not a directory, it is a MEMBERSHIP: `commons/commons.js`
  `COMMONS_TRADES` gets the chip, and `commons/gear.js` + `commons/tips.js` get rows
  somebody actually wrote for that trade, seeded by the same adversarial fan-out that
  seeded everyone else. Framing shipped 2026-08-09 with no chip at all; roofing shipped
  2026-08-12 WITH a chip and zero rows, and was swept into three universal rows by an
  unrelated commit four days later, which made it look served. Both were caught long
  after the trade was live, by somebody counting — never by the trade's own launch. The
  deploy now refuses a chip carrying fewer than six rows written for it, so this can
  fail the build instead of failing a roofer; that gate is the floor, and seeding the
  trade properly is the job.
- **Same bar, same safety, same ledger.** Every trade's tools face the identical
  "would a real &lt;trade&gt; pro use this to send their boss something, FAST?" test.
  The cross-trade demand DATA stays private (the moat); the pages stay open.
- **This is loop-as-a-service** (private strategy `operator/AV_TOOLKIT_STRATEGY.md`):
  the AV toolkit is the public reference implementation that proves the mechanism for
  every other trade. Isomorph only when the current toolkit is broad enough to copy
  well — expand deliberately, never half a trade at a time.

## THE THREE KINDS OF WISH — the toolkit self-heals (wired 2026-08-04)
The well takes three kinds, and the loop serves them in this order:
1. **`bug`** — a shipped tool is wrong. **This outranks everything.** Something
   already in someone's hands is giving them a bad answer on a real job, and a wrong
   value costs money. Fix it the same cycle.
2. **`improve`** — "wish it better". The people using a tool on a job are the ones who
   know it asks in the wrong order, misses a line, or doesn't talk like their crew.
   An improvement earns the same Wall-of-Wishes credit as a new tool.
3. **`new_tool`** — build something that doesn't exist yet.

`bug` and `improve` carry `about_tool` (the registry href), chosen from a picker of that
trade's own tools — a report that doesn't name its tool is refused at the form, because
one tap is the difference between actionable and useless. Read them with
`av_wishing_well.py --list [--trade <slug>] [--kind bug|improve|new_tool]`; the helper
sorts bug → improve → new_tool and shouts if any bug is open. This is what rung 14 of the
seed roster always promised: **the well + the loop are how the toolkit self-heals while
Aldrin is up a ladder hanging TVs.**

## THE GATE — a tool ships only if TICKING BEATS TYPING (2026-08-03)
The single most useful thing we know, found independently by five in-trade reviewers
during the plumbing expansion: **never answer a NARRATIVE task with a multi-field FORM.**
Their words — *"seven empty boxes on a phone lose to the notes app every time"*,
*"eight empty textareas is strictly worse than the one empty box he already has"*,
*"ship the typewriter, not the panel simulator"*.

The observation that settles it: this toolkit has shipped exactly ONE checklist and ONE
tool that dumps messy notes into an AI. It has never shipped a nine-box narrative form —
and a single round of roster research proposed more than a dozen of them.

- If the work is **already a list** — a pull list, findings by footage, punch by room,
  valves by tag, circuits by number, cable by run — **build it.**
- If the work is **a paragraph** — the daily, found/did/recommend, the callback story —
  **do not build a form.** Either decline it, or build the `report-builder.html` shape,
  which is the one narrative tool that works precisely because it adds an AI pass
  instead of adding empty boxes.

## THE SYSTEM OF RECORD — never compete with whoever owns and NUMBERS the document
Procore owns the RFI number and the daily log. ServiceTitan makes the call write-up a
mandatory field before the tech can close. Milestone/Genetec already export device data.
Bluebeam owns markup; the architect owns the hardware schedule; the AHJ owns the
inspection card. Competing with any of them = double entry = dead on contact, and it
fails worst for the biggest shops, who are the best users.

**Feeding survives.** The field-condition note that becomes the PM's RFI. The self-punch
that shortens the GC's punch list. The turnover that becomes the estimator's quote. Ask
before every build: *does the receiver have to key this into something else anyway?* If
yes, scope the tool to **what you send him**, never to the record of record — and never
let anyone believe our number is the official number.

## THE THREE SHAPES — build engines, not pages
Across five trades, every tool worth shipping is one of three shapes. Two of them are the
same widget wearing different words:

1. **CHECKLIST → a request UP the chain.** Categories → tick → qty + one to three
   modifiers → plain text. `av/consumables.html` and `plumbing/supply-house-order.html`
   are both this. The only per-trade variance is the item data and which modifier axes
   exist (AV: none · plumbing: size + config + unit-of-issue).
2. **THE NOTE.** An ordered set of short fields, one of which is the **impact line
   everyone omits** ("what work is stopped", "what fails if we don't"), an optional
   forget-list checklist, and a fixed closing ask the receiver can reply to. The
   directed-work ticket, the shutdown notice and the field RFI are all this one widget.
3. **THE ROW LOG.** An add-row bar with sticky fields (only one or two retyped per row),
   a grouped table, per-group tallies, and a **TSV copy that pastes into Excel** —
   because that output goes into an O&M manual or a spreadsheet, not into a chat message.

When you build the second instance of a shape, extract the engine. Two instances is where
a shape is provable; one is over-abstraction and five is five forks.

**Shape #1's engine now exists: `shared/checklist-request.js`** (extracted 2026-08-04, first
used by `av/cable-list.html`). It owns exactly the parts that were duplicated and drift when
forked — tick/expand state, per-category counts, qty + note, write-in rows, clone-a-line,
live preview, the count line, clear, walk-duration persistence, and copy WITH the
non-secure-context fallback. The CALLER owns the item data, the modifier axes each item
declares, the document wording, and its own CSS (the engine emits the class vocabulary the
existing pages already use, so adopting it is visually a no-op). Build the next instance of
shape #1 on this engine; `av/consumables.html` and `plumbing/supply-house-order.html` are
still the original forks and are the migration debt to retire when either is next touched.

**The FOURTH instance (`electrical/pull-list.html`, 2026-08-04) is what an engine is for:**
a whole trade shipped with no new mechanism — a config, a vocabulary file and a page. It
also proved where the engine was still assuming AV's habits, so five things are now OPT-IN
(every shipped page unchanged by default):
`qtyText` (a free-text Qty — "2 bx", "500 ft", "a case"; the number spinner is right for
"4 HDMI cables" and wrong for a trade that orders in mixed units on one list) ·
`writeinTextarea` (a multi-line write-in that turns a PASTED list into one row per line —
an `<input>` silently flattens a paste, which breaks the fastest way anyone actually uses
these pages) · `writeinQtyDefault` and a per-row `qtyDefault` carried through render,
clone AND restore · `docName` (a section can read as a PROMPT on screen and as a HEADING
in the sent document) · `hasLast`/`restoreLast` (Clear stashes the list it destroys, so
"start from last list" is one tap — the highest-value feature a foreman asked for, ranked
by him above twenty more picker items).

**SHAPE #2's ENGINE NOW EXISTS: `shared/note.js` + `shared/note.css`** (extracted
2026-08-05 at the second instance, exactly where this section says to extract it). The
first instance was `hvac/repair-recommendation.html`; the second was the directed-work
ticket, which the private ladder ranks #1 for electrical and low-voltage, #2 for
plumbing, #4 for GC, #6 for HVAC and #7 for AV — one rung, six trades, and forking it
six times is precisely the failure this rule exists to stop. So all six shipped as
CONFIGS in one cycle.

The engine RENDERS, which is the one way it differs from shape #1's. Shape #1's caller
keeps its own HTML and asks the engine to drive it; that holds at two callers and falls
apart at six, because six hand-written field blocks drift inside a week. So the caller
declares SECTIONS and FIELDS as data and the engine builds the DOM, owns the state,
assembles the document, persists the draft and copies it.

NINE FIELD KINDS cover all six trades with zero per-trade special-casing: `text` ·
`area` · `select` · `seg` (single pick, up to 5, re-tap to un-pick) · `pick` (single
pick past 5, as chips that WRAP — a segmented row past five is a wall) · `ticks` (the
forget-list, whose `sub` rides into the document in parentheses) · `impact` (the loud
block: append-only chips plus its own clock, because a consequence with no clock is a
shrug) · `clock` (stamps itself on first touch — the timestamp IS the tool) · `rows`
(repeatable crew/material/refrigerant lines, quantities only, and the engine performs no
arithmetic on them anywhere, ever).

**`shared/note.css` is ONE stylesheet for all six trades**, driven entirely by the
`--flag` / `--flag-ink` / `--deep` / `--tint` variables the runtime injects from
`trade.js`. Not one of the six pages carries a line of its own CSS. That required the
DEEP PAIR: `accent` is deliberately light and high-chroma because it lives on the dark
nav, which makes it useless as a border or as text on paper, so every trade now also
declares `accentDeep` (white text on it clears 5:1) and `accentTint`. Hand-picked and
contrast-checked per trade rather than computed — `color-mix()` is not safe on the old
Android browsers these pages land on.

WHAT DID **NOT** MOVE INTO IT: every word. The note's whole value is that it speaks one
trade's language — a super who reads "Please provide authorization for the additional
scope" knows in one line that no tradesman wrote it. The caller keeps the copy, the
field list and its order (the order IS the argument), and the trade's vocabulary in
`items.js`. Same boundary shape #1's engine draws.

## THERE IS A FOURTH SHAPE, AND §THE GATE ALREADY NAMED IT
§THE GATE says: if the work is a PARAGRAPH, decline it **or build the report-builder
shape (an AI pass, not more empty boxes)**. That escape hatch had exactly ONE instance
for two months — `av/report-builder.html`, the operator's own end-of-day AV daily turned
into a role-tailored AI setup. One instance is a page. The second is where the engine
gets extracted, so it was:

4. **THE INSTRUCTION BLOCK.** Not a form that produces a document — a form that produces
   the INSTRUCTIONS that produce the document, forever. Pick the write-up you are stuck
   with, answer four or five ticks, get one block you paste into a Gem / Project / Custom
   GPT **once**. After that the job is: dump the mess, get the document back clean.

**SHAPE #4'S ENGINE: `shared/docspec.js` + `shared/docspec.css`** (extracted 2026-08-05;
the sheet loads *after* `note.css` and adds only the library, the doc card, the spine
editor and the output block — the chrome is note.css, because a second stylesheet that
re-declares the chrome is a fork with extra steps).

**THE ISOMORPHISM IS THE METHOD, NOT TEMPLATING** (operator 2026-08-04: "the reports that
stem from my own style, to isomorphically map what would be useful for other
documentation"). Read `report-builder.html` as a STRUCTURE rather than as content and it
is ELEVEN BLOCKS — role · what it is for · defaults · operating principles · attribution ·
input handling · continuity · validation · **the omitted line** · protocol reminders ·
output format. **Ten of the eleven are identical** for a plumber's back-charge notice and
an AV daily. Only the spine, the omitted line and the vocabulary change. So those three
are the config and the other ten live in the engine once.

**THE HIGHEST-VALUE FIELD IN THE LIBRARY IS `omit`.** Anyone can list the sections of an
incident report. The reason a real hand's write-up survives a dispute and a good writer's
does not is one line the good writer did not know to include: the approval nobody wrote
down, the condition already wrong before he got there, the date the clock actually
started, what he did NOT do and why. Every document carries that line, and the engine
gives it **its own always-on heading** in the emitted block so an AI cannot quietly drop
it. "Add more detail" is not an omit line and does not belong in a library file.

**AND WE MEASURED IT — the 80 hand-written `omit` lines fall into FIVE OMISSION CLASSES**
(2026-08-15), each demanding a **concrete artefact**: **a date** (the day it started, not
the day you wrote it) · **a name** (who said go ahead, when, on what channel) · **a
before-value** (what was already wrong, the reading before you touched it) · **a
location** (where the photos and readings actually live) · **a named gap** (what you did
NOT do, by name). The fifth was **not** in the plan — the rung was recorded as four, and
classifying the corpus put "what you did NOT do" level with the biggest of them and made
it the single most common thing a RECURRING write-up leaves out ("where you COULDN'T
work", "the idle half of the job"). **The corpus outranks the plan.** Counts, per family:
recurring `notdone 3 · where 2 · who 2` (n=8) · incident `before 8 · notdone 6 · who 5`
(n=23) · notice `when 8 · who 4 · notdone 3` (n=26) · verification `notdone 7 · who 5 ·
where 3` (n=19) · minutes `when 2 · who 2` (n=4, tie broken by the spine: it already
carries WHO WAS THERE, so `when` is the class nothing else forces).

**AND THE LIMIT IS MEASURED TOO, not waved at.** By the shipped five, 12 of the 80 (15%)
name something no fixed class of missing FACT can express. The sharpest is
`av/theory-of-operation` — *"the design decisions that look like faults… so by month two
the help desk has logged them as defects"* — an omission of INTERPRETATION, not of a date,
a name, a place or a value. No tick list reaches that and neither would five fixed
sentences; the house-rules box is the only surface that does. That is the argument for
keeping it free text and keeping this ticks.

**A SECOND, INDEPENDENT CLASSIFICATION OF THE SAME 80 LINES WAS RUN WITHOUT SIGHT OF THE
FIVE, AND IT DERIVED SEVEN** — and it is written down here because it AGREES on four of
the five family seeds and DISAGREES on one, which is worth more than a confirmation. It
found `recurring → scope-boundary (5/8)`, `notice → first-notice date (7/26)`,
`verification → scope-boundary (9/19)`, `minutes → date (3/4)` — the same seeds we ship —
and for `incident` it found `scope 7 · time 6` where the hand count found `before 8`,
because **it has no prior-state class at all**: it splits "the condition already wrong
before you got there" into a boundary statement and a dated delta. That is a real
taxonomic fork, not a counting error, and `before` is kept for incident because our class
list HAS that class and those lines cluster in it — recorded so a later cycle can settle
it with usage instead of argument. It also names two classes the five do not carry: an
**undocumented CHANGE** (the substitution, the config left changed, the valve left
non-normal — 10 of 80) and a **quantified MEASUREMENT** (a number, its unit, and the datum
it was read from — 8 of 80). Both overlap the shipped five at the edges and neither is
added, because seven ticks is the "ten generic ones" the rung forbade. **THE EVO-LOOP
QUESTION, stated before the data so it counts as a prediction:** if people are reaching for
something the five do not have, the tick they pick will drift toward `before` and `where`
(the two nearest neighbours of CHANGE and MEAS) rather than toward the seeded class.

**FIVE FAMILIES cover every write-up all six trades produce** — the recurring report · the
incident record · the verification record · the notice that puts somebody on the clock ·
the minutes. Each has its own spine AND its own continuity rule (only `recurring` and
`minutes` get delta reporting; an incident record read three years later must never be
written as an update). The families are also the fallback: a document that is not in the
library gets a real spine from its family instead of a shrug — **and since 2026-08-15 a
real `omit`, `facts`, `why` and `secondary` too**, each seeded from the family rather than
hardcoded. The omit seed is **exactly one** class, because the MODE of the shipped library
is one line (75 of 80); the first draft seeded three off the MAX of the five documents
that ship a list, which is the wrong statistic. Whatever ships pre-ticked is what a man in
a hurry keeps, so the default biases DOWN and the other four are one tap away.

`<trade>/docs.js` is the fourth data file, same boundary as the other three: `trade.js` =
IDENTITY · `tools.js` = REGISTRY · `items.js` = picker VOCABULARY · `docs.js` = the
WRITE-UPS this trade actually has to produce, plus its dictation fixes and its
trigger-only protocol reminders. It carries `overrides` keyed by a SHARED document id, so
a trade says "the daily in MY words" without forking a document, and `trade` — the trade
word the block prints — is DECLARED there rather than derived from the toolkit name.


**SHAPE #3'S STYLESHEET NOW EXISTS TOO: `shared/rowlog.css`** (extracted 2026-08-05 at the
second instance, same rule, same place). The first row-log page carried ~130 lines of its
own `<style>` with one trade's coral hard-coded into a dozen rules; the second would have
copied it and six would have drifted inside a week. Every colour that belongs to a TRADE is
a runtime-injected variable; every colour that belongs to a STATE — a duplicate warning, a
flagged row, a destructive button — is fixed in the sheet, because those mean the same
thing in all six trades and painting them the trade colour makes the page say *brand* where
it needs to say *look at this*. `low-voltage/device-checkout.html` adopted it in the same
cycle and deleted its fork.

Shape #3's ENGINE grew four things at the boundary, all of them opt-in and all of them
no-ops for the first instance: **named document FILTERS** that AND together and compose
with the delta (a chase list's real message is *what is still open*, and a cross-boundary
list's is *his items only*) · **`groupName`**, because a config whose values are slugs was
printing `EC` and `ROCK` as the headings somebody else reads · **gated `learn` fields**,
so an ask can offer the sizes anybody would pick for it *merged with the ones he has typed
himself* · and a **scoped flagged block**, so the receiver filter reaches the part of the
document that used to ignore it.

**AT THE THIRD INSTANCE (`answer-back`, 2026-08-09) IT GREW FOUR MORE, same rule: every
one defaults to exactly what the first two instances already shipped.** ·
**`pasteKey`** — which field a bulk-pasted line lands in. Bulk paste was built for a column
of device tags so it wrote into the IDENTIFIER field, the only field a tag could be; a
reply pastes somebody else's PROSE and must never inherit the identifier's
uppercase-and-+1 keyboard. · **`statusWrap`** — the tap ladder cycles back to blank instead
of stopping at the top. The stop is right for a PROGRESS ladder (committed → in), where an
accidental second tap would destroy a fact somebody walked out and verified; it is wrong
for an ANSWER ladder, where the wrong rung is not progress lost but a wrong answer, and
making him open the pencil sheet to correct one tap is §THE GATE failing on its own
control. · **`statusDone`** — which rung wears the settled green edge, because on an answer
ladder that rung sits in the middle and the LAST one is a question still waiting on
somebody. · **`groupSort`** — a stated block order. Insertion order is fine for a log a man
keeps for himself and wrong for a DOCUMENT that crosses to another company, where *here is
what you're getting / here is what you're not* must read the same way every time.

**AT THE FOURTH INSTANCE IT GREW A SECOND SURFACE RATHER THAN A FIFTH FIELD KIND — THE
WALK (2026-08-10, opt-in `cfg.walk`, every page without it byte-identical).** Every row-log
page until now had exactly one surface: the pencil sheet, where a list is COMPOSED sitting
down. A list is also VERIFIED WALKING, and that half had nothing. Forty grouped rows on a
390px phone, read at arm's length with a light in the other hand and gloves on, is a
pinch-zoom and a lost place. So the walk is the same rows, one at a time, full screen, dark
on purpose — this is the one surface used out on the deck rather than in the van, where the
paper-white sheet the rest of the toolkit wears is a flashbulb — in type you can read
without stopping, behind two targets **96px tall**: more than double the 44px floor,
because this one is hit with a knuckle and not looked at.

Four things make it honest, and each is a rule for whatever mode is added here next:
· **IT WALKS `scopedRows()`**, so the filters the page already has ARE the walk — *"still
  open, for the electrician"* is Thursday morning and needed no new control — and the
  launcher NAMES the set it is about to walk, because walking a different list than the one
  he filtered is the same class of lie as counting rows the document does not contain
  (§SCARS 2026-08-09).
· **THE TWO BUTTONS ARE NOT SYMMETRIC AND MUST NOT BE.** The affirmative SETS the settled
  rung rather than advancing one step, so a double tap cannot walk a row past a rung nobody
  verified, and a man who taps twice has said the same true thing twice. The negative NEVER
  INVENTS A RUNG — on a row short of the settled one it writes **nothing at all**, because
  the only honest record of *"I looked and it wasn't there"* this page owns is that the row
  is STILL OPEN, and a "checked, absent" value is one no field here can carry. But on a row
  that ALREADY carries the settled rung it **retracts** it, one step down the declared
  ladder. Writing nothing there was the first version and it was wrong (§SCARS): down the
  ladder is not inventing, it is un-saying.
· **IT PRODUCES NO NEW DOCUMENT, ON PURPOSE.** It makes the one the page already sends TRUE
  — "still open" is only worth sending if somebody laid eyes on the list today, and the walk
  IS that act — so the end of it does exactly one thing: puts the page on STILL OPEN and
  takes him to the message. It never writes to the clipboard behind him.
· **EVERY CONTROL IS A REAL BUTTON AND EVERY ONE IS REACHABLE BY KEY** — arrows roam, Enter
  picks, Escape leaves, Tab is trapped. That is the operability the dialog owed anyway, and
  it is the only input model a screen with NO POINTER can offer, which is the half of this
  that outlives the phone it shipped on.

**WHERE IT DELIBERATELY DID NOT GO — the judgment, not an omission.** `answer-back` (all
seven trades) has a FOUR-WAY answer ladder, and a two-button walk can express exactly one of
the four; wiring it there would push a man toward whichever answer the button happens to
name. `device-checkout` has a six-rung ladder whose settled rung is the last of six, and a
binary tap that lands on VERIFIED asserts five steps nobody did. `whats-in-the-wall` is the
close miss and the named next rung: its settled rung is `Covered` while the rung a pre-rock
walk actually verifies is `In`, so it needs the walk to name its OWN rung *and* the end card
to count "at or past that rung" **by ladder index** — two changes, not one config line.
Written down here so the next cycle adds them deliberately instead of wiring the walk in and
shipping a wrong count.

Keep the boundary or the config rots: `trade.js` = IDENTITY + COPY · `tools.js` =
REGISTRY · `items.js` = that trade's VOCABULARY DATA (categories, size ladders, config
options, unit-of-issue sets). Size ladders and C×C/FIP/no-hub live in data — never in the
identity config and never inline in a tool page. **And a second tool may READ the first
tool's data rather than re-declare it:** `answer-back` offers its "when" chips off
`TOOLKIT_ROUGHIN.milestones`, because two lists of the same trade's gates is one list that
rots.

## THERE IS A FIFTH SHAPE, AND IT IS THE FIRST ONE THAT DOES NOT GO UP THE CHAIN
Every shape above produces a document you send UP a chain — a request to your PM, a note
to the super, a log for the O&M, an instruction block for your own AI. Shape #5 produces
one you send SIDEWAYS, to your brother in another local, or to nobody at all because the
answer was for you.

5. **THE RECKONING.** Two named columns, a list of lines in the trade's own vocabulary,
   a figure on the lines that apply, and the difference. Package vs package, bid vs bid,
   quoted hours vs burned hours, this month vs last. There is **no tick**: the figure IS
   the tick, which is one act instead of two and drops every unpicked value for free.

**SHAPE #5'S ENGINE: `shared/package.js` + `shared/package.css`** (2026-08-12; the sheet
loads *after* `note.css` and adds only the basis switch, the columns, the line grid and
the totals — the chrome is note.css). First instance: **TOTAL PACKAGE**, shipped as eight
configs in one cycle.

**THIS IS THE FIRST SHAPE THAT DOES ARITHMETIC, AND THAT IS WHY IT COULD NOT BE A ROW
LOG.** `shared/rowlog.js`'s header states as a designed boundary: *"NOT here, deliberately:
any computed quantity… The user states every value."* Every other trade's row log relies
on that staying true, so bending rowlog to sum a package would repeal the rule rather than
extend it. The line shape #5 draws instead: **the tool may add up figures it watched a man
type, and may multiply two of them together — and nothing else.** No rate, no table, no
index, no projection, no figure from us. Same §SAFETY, one floor down.

**THREE LINE KINDS, because a package is not a column of like things:** `money` (a figure
in the basis) · `pct` (a percentage resolved per column against THAT column's own wages) ·
`aside` (a figure with its own unit — "a day" — never summed, always printed). The `pct`
kind is a panel finding, not a refinement: a working journeyman killed the flat-dollar
dues line with *"it just sits there being wrong exactly when I compare two different wage
rates, which is the entire point of the tool."* A trailing `%` typed into ANY line makes it
a percent too, because the seed list cannot know whether his annuity is flat or off gross.

**FOUR BUCKETS AND ONE REFUSAL TO CONFLATE THEM:** wages · fringes · what comes back out ·
asides. TOTAL PACKAGE = wages + fringes, which is what a wage sheet means by it.
Deductions show as NET ON THE CHECK and never touch the package. Vacation gets a line in
BOTH the fringes and the deductions group on purpose — funded-on-top and deducted-from-gross
are the commonest way this comparison is made wrong, and two labelled lines teach it.

**THE BLANK-LINE FLAG IS THE HONESTY MECHANISM OF THIS SHAPE.** If one column carries a
line the other does not, the two totals are answering different questions, and the page
says so — on screen, next to the number it undermines, and in the document. A confident
total built on unacknowledged blanks is the single most likely way a comparison tool
produces a figure someone takes into a real decision and is wrong. Same rule as §THE
RETURN LEG's dateless yes and the 2026-08-09 scar THE SUMMARY COUNTED ROWS THE DOCUMENT
DID NOT CONTAIN.

**TWO DISCLAIMERS NO CALLER CAN SWITCH OFF** — one on screen beside the totals, one inside
the copied text. The copied block is the artifact that leaves the browser and reaches a
business agent or a spouse, and it looks exactly like the hall's own wage sheet. It is one
man's typing and it says so, every time, covering three points: self-reported, not
take-home, and fringes usually pay at straight time even on overtime.

**AND THE THINGS THIS SHAPE MAY NEVER DO,** written here rather than in one page's comment
because the next instance will be tempted by all of them: no proper noun of any union,
contractor association, benefit fund or local number in a seed list (only the CATEGORY
names a stub already carries — seeding one fund's real name is a claim about which
agreement he is under); no autocomplete on the column-name field (suggesting real locals
compiles the jurisdiction directory this project refused to ship); no example figure in a
placeholder (a suggested number is a rate assertion wearing helper text); no forward
projection of any kind; no column ever labelled better, worse or recommended — the delta
says MORE THAN and LESS THAN, because that is arithmetic and anything warmer is advice.

**AND NO TELEMETRY, EVER, ON A PAGE THAT HOLDS A WAGE.** The evo loop instruments CHOICES
between variants; a wage is not a variant. Every other tool's data is a cable spec or a
punch item. This shape is exempt by design, the feedback path must never attach page state
to a report, and both rules are written into the engine header so a later cycle reads them
before wiring one in for convenience.

## THERE IS A SIXTH SHAPE, AND ITS ADD-ROW BAR IS A STOPWATCH
Shape #3 is a row log of THINGS — devices, tags, punch items — and every one of its
mechanisms (bulk create, a tag-range generator, tap-to-advance, self-building axes,
grouping) exists because a man is walking a job typing identifiers. None of that applies
when the rows are MOMENTS. Forcing the hold test into shape #3 would have used about a
fifth of that engine and fought the rest, which is the tell that it is not the same shape.

6. **THE HOLD TEST.** Close a system, isolate it, watch a gauge, and be able to say
   afterwards what it read and WHEN. HVAC/R pulls a vacuum and watches the microns come
   back up; a plumber puts five pounds of air or ten foot of head on a rough-in and
   watches the needle stay put; gas piping, medical gas and a flood test on a deck are the
   same act. **The rows are not typed, they are TAPPED** — ticking beats typing taken
   literally — and the value is entirely that the clock fills the column a man otherwise
   reconstructs from memory two hours later, wrong, at a desk.

**SHAPE #6'S ENGINE: `shared/holdtest.js` + `shared/holdtest.css`** — built as an engine
on its FIRST instance, the same deliberate exception `shared/rowlog.js` took, because the
SECOND config shipped in the same cycle (`hvac/evac-record.html` and
`plumbing/its-holding.html`, 2026-08-14). A shape with two live configs on day one either
has an engine or has a fork, and the fork is invisible for about a week.

**EVERY STAMP IS AN ABSOLUTE EPOCH MILLISECOND, NEVER AN ACCUMULATING COUNTER.** This is
the one page in the toolkit DESIGNED to be backgrounded — the phone goes in a pocket while
a pump runs for forty minutes — so a counting timer is a page that lies the moment the
screen locks, and the synchronous flush on `visibilitychange`/`pagehide`/`blur` is not a
nicety here, it is the feature working at all. Verified on the live artifact: after a
flush and a cold reload the readout resumed at `00:32:45` from the real isolation stamp
and kept ticking.

**A CORRECTED TIME CAN NEVER PASS AS THE CLOCK'S.** The single claim this shape makes is
that the stamps are real, so the correction path — which must exist, because a man opens
the tool twenty minutes after he started the pump — brands its row **time typed in** on
the page AND in the document, permanently, with no config to switch it off. The honesty
clause at the foot of the document rewrites itself when any exist. A tool whose whole
premise is an automatic timestamp cannot ship a silent manual one.

**NO TARGET, NO VERDICT, AND THE ENGINE DOES NOT KNOW WHICH WAY IS GOOD.** No shop number,
no manufacturer number, no code table, no decay rate, no required duration, no pass. It
prints times, readings, and the signed delta between two numbers it watched the same man
enter — stated as `up 12 microns` / `down 2 psi` / `no change`, never as a judgement,
because a vacuum RISES when it leaks and a pressure test FALLS when it leaks and the
engine has no business guessing which trade it is in. Delta arithmetic is skipped entirely
when either value fails to parse: a range, a word, a blank all print as themselves.

WHAT THE CALLER OWNS: the MARKS (their words, their order, which carries a reading, which
one is the zero), the unit, the header fields, and the document's sentences. `zero` being
the SECOND mark for HVAC (a pump runs before anything is isolated) and the FIRST for
plumbing (pumped up and valved shut in one move) is one flag in a list — which is the
proof the engine is real and not a page with a config bolted on.

## FEEDBACK IS BUILT IN — the standard for everything we make (operator 2026-08-04)
> *"there's a lot of bugs still and people should be able to send the feedback so the
> loop cycles can address them. Make sure we have a solid scalable way of addressing
> open item wishes/feedback for ANYTHING. Standardize the process so anything that is
> made has this built in."*

**Every surface we publish carries a way to say it's broken.** Not a convention — an
assertion in the deploy. Collage Studio ran for months with no feedback path at all (a
grep for `feedback|bug|report|contact` across its entire source returned nothing), which
is exactly the gap a convention cannot catch.

**The drop-in is `shared/feedback.js`.** It is the trade wishing well with the trade
assumptions removed: dependency-free, framework-free, brings its own modal and markup.
Adding it to anything is TWO LINES:

```html
<script>window.FEEDBACK = { surface:"collage", name:"Collage Studio",
                            accent:"#7C3AED", areas:[{v:"export",label:"Export"}] };</script>
<script src="../shared/feedback.js"></script>
```

A surface that cannot spare two lines has not shipped. Set `trigger:false` and call
`Feedback.open("bug")` from your own button when the default floating trigger would
collide with your layout (Collage Studio does this — its canvas owns the top-right and
its dock owns the bottom, so the trigger lives in the topbar).

**ONE QUEUE, NO MIGRATION — this is what makes it scale.** It writes to the same
`av_tool_requests` table the trade wells write to. Migration 076 made `trade` a bounded
lowercase slug *deliberately* ("not an enum, so a new trade needs no migration") — which
means it was already a general SURFACE key. `surface:"collage"` inserts today, and so
will the tenth product. One queue · one helper (`av_wishing_well.py`) · one loop process ·
N surfaces. Read everything with `--list` unscoped; narrow with `--trade <surface>`.

**The three kinds and their ORDER are the point**, on every surface: `bug` (something in
someone's hands is wrong) outranks `improve` outranks `new_tool`. A bug picker that does
not name WHICH part is refused at the form — one tap is the difference between actionable
and useless, so every surface declares its own `areas`.

**Credentials are weight, never a login.** Role, company/local and "what you mostly use it
for" are optional, never required to send, and NEVER published — they tell the loop the
provenance of a correction and the context to build it in.

**What the loop owes back.** Reading the well is not the deliverable; closing it is. A
surface that collects feedback and never ships a fix has built a complaints box. Bugs are
fixed the cycle they are read.


## THE EXPANSION ORDER — BREADTH FIRST, EXTRACTION SECOND (operator 2026-08-04)
> *"obviously we're going to continue the expansion to empower every tradesman first,
> correct — then we can isomorphically extract from the most refined one; i assume it will
> be av because i'll know how to request it better. must be an active feedback loop and
> self refinement, self giving on your end."*

Read both halves literally.
- **FIRST, BREADTH.** Every trade family on the ladder gets a real toolkit before any trade
  already served gets polished. A trade with nothing is a whole population served by
  nothing. This is a standing priority, not a preference.
- **SECOND, EXTRACTION.** AV is the most refined trade because the operator is a working AV
  pro who uses these pages in the field and wishes in the open — the highest-fidelity signal
  this program has. So AV is refined deepest, and whatever it proves is then carried out to
  every other trade.
- **EXTRACTION IS SELF-GIVING AND IT RIDES ALONG.** Nobody files a wish for a backport, which
  is exactly why it is owed. **Standing rule: when a fix or a refinement lands on one trade,
  sweep every other trade for the same class in the same cycle.** A fix that lands on one
  trade and leaves its siblings broken is half a fix. Three of the four scars below were found
  by running that sweep once.
- **THE SAME MECHANIC AT THREE SCALES.** Take what is proven and carry it to everyone who does
  not have it yet — between TRADES (this section), between SPACES in the society world, and
  between INDUSTRIES (a company mapping its own internals onto our document schema).

## MOBILE-WATERTIGHT — the pre-ship gate (operator 2026-08-04)
> *"must be mobile friendly always — don't make anything that's gonna clip or alter if
> zoomed out on phone."*

These pages are used one-handed, on a phone, in a hallway, on a ladder, on a cracked screen
in bad light. Before ANY ship, drive the REAL page in a real browser at **320 / 360 / 390 /
430 px** and assert:
- `documentElement.scrollWidth <= clientWidth` **and** `body.scrollWidth <= clientWidth`
  (both — see the masking scar), and no element's right edge past the viewport;
- nothing clipped, truncated or overlapping; no fixed width or unbroken token that outgrows
  the viewport;
- tap targets **>= 44px**; the sticky nav never covers the content or the bottom action;
- the copy button reachable without a pinch; text still legible with OS text size bumped up.

A screenshot of a render is not this verification — do the job the page claims, at 390px,
and assert the numbers. An `<iframe>` at a fixed width is a faithful and much faster harness
than resizing the window (desktop Chrome will not go below ~500px).

## FIELD-COOL — the aesthetic bar, which is a quality bar (operator 2026-08-04)
> *"make it sick and cool like actual cool people who use this stuff, not something lame and
> corporate lol."*

The trade's own vocabulary and abbreviations, unapologetically · dense, fast, high-contrast,
built for a dirty screen · confident, plain-spoken copy with zero corporate hedging and no
enterprise-SaaS register · personality earned in the words, never cuteness bolted onto a
form · and still NON-CLUTTERY (one job per tool, usable in seconds). **The test:** a real
crew would screenshot it into the group chat unironically. If it reads like a compliance
portal it fails, and "clean" is not a defence.

## THE COMMONS — the human layer, and the only part that transcends every trade
(operator 2026-08-04) Four community-fed parts, all of which make the toolkit worth opening
when there is nothing to generate: **must-have gear** (the ubiquitous kit the field loves
across all trades, and "upload your favourite tools") · **field photos** of the real item, so
a picker SHOWS the thing instead of only naming it · **tips and tricks** from people who do
the work · **guides and short tutorial content**, the teaching layer. Contribution must cost
seconds and never an account.

**IMAGE RIGHTS + CONTRIBUTED CONTENT — the rail that makes this safe to build.** A picture is
a new data class, so the rules are explicit and not negotiable:
- **Origin.** Only images we may lawfully publish: public-domain/CC0 or an open licence whose
  terms we actually satisfy and attribute, our own photography, or a contributor's own photo
  with an explicit rights grant in the form copy. **Never** scrape or hotlink manufacturer
  marketing photos, never imply an endorsement, never let an image misrepresent a part.
- **Hosting.** Static Pages with no third-party CDN means an image is committed to the repo or
  served from our own storage — never a remote hotlink that can rot or be swapped under us.
- **Contributed photos.** Resize client-side before upload, **strip EXIF** (a jobsite photo
  carries GPS and a customer's address), moderate BEFORE anything renders publicly, and assume
  the worst upload will arrive. This does not weaken §SAFETY: a TOOL's working uploads still
  never leave the browser; a COMMONS contribution is a separate, consented, reviewed act.
- **Credentials.** A wisher's trade / union local / company / residential-vs-commercial context
  is WEIGHT for ranking a correction and CONTEXT for building it. It is never a login, never
  required, and — like the rest of the queue — **never published**.

**THE RUNGS, RANKED — and why the two the brief numbered are not the top two (2026-08-13).**
A three-lens panel scored the unbuilt parts and all three independently attacked the ordering:
*"it is in the founding brief" is not a rail.* The two unbuilt named parts are the two highest
-liability things on the site, and the candidate that is **not** in the brief scored above both.
1. **SEED EVERY CHIP FIRST.** A commons surface is offered from every other one, so a new
   surface handed to a trade with no rows multiplies the hole instead of filling it. No fourth
   surface while any chip is thin. (This is what shipped 2026-08-13; roofing was at zero.)
   Surface #3 landed 2026-08-14 seeded for all ten trades in its first commit and gated at the
   same per-trade floor as the other two — the deploy now parses the surface list out of the
   shipped engine, so surface #4 is coverage-gated the day it lands with no edit to the CI.
2. **ASK FOR IT RIGHT — the cross-trade name table. SHIPPED 2026-08-14 as `commons/names.html`,
   surface #3.** Scored 7-8 by two lenses; the only candidate a journeyman said he would forward.
   **THE OBJECTION WAS ANSWERED BY MAKING THE ROWS STOP BEING A PAGE.** The lens that voted it
   down was right that a synonym sitting in a list does no work, so `names.js` is not read as a
   page by anything except one of the three surfaces: it is an **ALIAS INDEX**, and every commons
   surface searches *through* it with the same `shared/find.js` this toolkit already measured on
   5,384 queries. Type **stinger** into the gear list and the extension cord comes up; type
   **marrette**, **zap strap**, **tick tracer**, **Stillie**, **knuckle buster** — none of those
   words exists anywhere in `gear.js`. The join is by folded object name (parentheticals dropped,
   anything after a comma dropped, plurals folded, both sides folded the same way) so two files
   written a week apart need not agree on ids. **A claim like that is one rename away from
   silently becoming false, so it is COUNTED in the deploy** — through the engine's own exported
   `Commons.aka`, never a second copy of the rule — and `tools/toolkit-gates/commons-names.mjs`
   derives every routing probe FROM THE DATA (every alias that is not already a substring of the
   gear page) and demands the right row on the real page. A word added next month is tested the
   day it lands. **The rails below are now the maintenance contract, not a proposal:** a row is
   ONE OBJECT under every name the field says
   for it, **never two names joined by a slash** — if the things either side would not both
   satisfy the same order, they are two rows. The plain generic prints first and is the name to
   ORDER by; a trademark is labelled as what people *say*, never as what to write down
   (`electrical/items.js` already set that precedent, and §SCARS "half a trade's vocabulary is
   somebody's trademark" is why it cannot be skipped). Every name carries WHO SAYS IT, and a
   regional word prints as *you might hear*, never as *it is called*. No row may separate
   near-names by size, depth, gang or rating — a name that needs a number to be right is
   certified data we do not ship. **The invisible failure to design against:** the table is
   evidence about the WORD and will be read as authority about the OBJECT; the fix is in the
   data shape (object-first, "same object" declared per row and checkable by a reviewer), never
   in the copy. The strongest objection on record, from the lens that voted it down: this
   project has met the translation problem twice and solved it both times as ROUTING INSIDE A
   TOOL — `av/items.js` writes its asks in the receiver's vocabulary, `docs.js` carries `aka`
   so a man finds his write-up by whatever his shop calls it — and a synonym that only sits in
   a list does no work. Answer that objection in the build or do not build it.
   **THE SHAPE THAT SHIPPED, because the rails live in it and not in the copy:** `o` is the
   object declared in one checkable clause (a reviewer can hold it against the aliases and say
   yes or no); every alias carries `k`, and `k` — not the writer — decides the framing, so a
   `tm` can only ever render as *a brand people say*, a `reg` only as *you might hear*, `sup` as
   *the counter says*, `say` as *the field says*; every row wears **ORDER IT AS** above the
   generic on every render, because a page that prints the generic as a heading and the aliases
   as a list of equals is a page that hands a man a trademark to put on a purchase order; and
   `no` is the near-miss guard — the rows that earn this page are the ones where the wrong word
   gets the wrong OBJECT walked over to you, which is a different failure from not knowing the
   word. *"Say snake on a mixed job and that is what walks over."* The gate enforces all of it
   mechanically, digits included.
2b. **JOB WORDS — a fourth surface for the words that are NOT objects. PANEL-REJECTED
   2026-08-16, and the ballot's own worked example is what killed it.** The observation
   underneath is correct and worth keeping: `names.js` is object-first by rail, so it
   structurally cannot hold *rough-in · top-out · dry-in · punch list · backcharge · T&M ·
   RFI · submittal · as-built · closeout · retainage · short-shipped · back-order*. The
   proposed surface was not that observation. Three lenses scored it **2 / 3 / 5** and all
   three refused it, on three independent grounds:
   - **IT IS THE FOURTH IMPLEMENTATION OF A SOLVED PROBLEM.** `shared/docspec.js` already
     carries `aka` for most of that word list, per trade, in production — *RFI* in `gc/docs.js`
     and `electrical/docs.js`, *punch list reply* in `framing/docs.js`, *backcharge* in
     `electrical/docs.js`, *closeout* in five trades, *change order* and *turnover* universal
     in `shared/docspec.js`. It is the identical feature and **more capable**, because it hands
     back the document's instruction block instead of a link to start over on another page.
     The genuine residual is *top-out · retainage · short-shipped* — zero hits tree-wide.
     **That is four rows, not a surface.**
   - **THE ROUTING TABLE WAS ASSERTED, NOT MEASURED.** Its headline example routed *closeout →
     `total-package`*. `total-package` is the **compensation comparison** tool — *"two offers,
     two shapes... see the real gap before you answer the email"* — on all eleven trades. There
     is no closeout tool; closeout is a document type inside `write-up`. A routing claim that
     points its lead case at the wrong building is a list with links glued on, which is the
     precise objection this axis has already survived once.
   - **THREE WORDS CANNOT SHIP AT ALL, AND NOT BECAUSE OF WORD COUNT.** `lien` is definitionally
     useless without a filing deadline, and statutory deadlines are a named forbidden class.
     `liquidated damages` cannot be explained without enforceability, which is contract law.
     `backcharge` was already banned as *content* twice, independently, by two trades that had
     never spoken — `av/items.js` (*"NO money, no backcharge, no 'who eats it'"*) and
     `framing/docs.js` (*"no backcharge language"*). And the protective rail — *"explain the
     word, never the procedure, never a number, never a deadline"* — **is not mechanically
     enforceable**: "check your state's lien deadline before you wait too long" carries no
     digit, no currency, no banned unit, and passes every gate that can be written for it. By
     the rule this book already applies to photos, a protection that cannot be enforced by
     shipped code scores as if it does not exist.
   **The re-pitch condition, falsifiable and small:** three-to-five words with zero coverage
   anywhere, added to an **existing** surface, attempted only after the cross-trade hole below
   is closed. Not a fourth surface, and not until that has been tried.
   **THE HOLE THE PANEL FOUND INSTEAD, and the named next rung on this axis:**
   `shared/docspec.js` is **trade-siloed by construction**. Every `write-up.html` loads its own
   trade's `docs.js` and nothing else, and `docspec.js` reads one global (`window.TRADE_DOCS`),
   so an AV tech who only knows *"punch list reply"* from a framing background gets nothing —
   that alias lives in `framing/docs.js` and is invisible on every other trade's page. **That is
   the same defect this cycle fixed one layer out**, and it is the same failure `names.js`'s own
   header names as its reason to exist: a man gets handed a word by somebody from another trade.
   The commons solved it (`commons.js` §THE HAND-OFF, *"Every trade searched, not just the one
   you picked — you heard it off somebody else"*); `docspec.js` never got the same treatment,
   despite being the older and more heavily used system. Fix it the way the commons did — a
   lightweight cross-reference on the graceful-failure path, off the same `shared/find.js` —
   never by loading ten trades' `TRADE_DOCS` onto every page.

3. **GUIDES — refuse as written.** A guide is a procedure, and this page's own header says
   "not a how-to". A tutorial forbidden to state a number, a step order or a safe condition is
   not a tutorial; what is left is an EXPLAINER (what a thing is and why it exists), which is
   shippable and is a different, smaller promise. And the teaching layer already ships where it
   works: `docs.js` teaches at the moment of use, and a second copy drifts.
4. **FIELD PHOTOS — deferred a third time, on purpose and with a harder reason.** There is no
   ingest: `shared/feedback.js` is a text-only POST with no file input. Client-side EXIF
   stripping and resizing are unenforceable by construction — the endpoint is reachable without
   our form — so the rail as written cannot be delivered in a browser. Moderation-before-render
   prevents publication and does nothing about CUSTODY, and custody is the liability: a jobsite
   photo carries a stranger's address, a face, a plate. A photo of the real item also puts a
   logo on the one page whose credibility claim is the absence of brands. If photos ever ship,
   v1 is **our own photography, committed, with no upload button at all** — and it must be
   named as that, not as "part 2 delivered".



## THE INTERFACE — the axis a single-actor tool cannot reach (opened 2026-08-05)
Every tool in this toolkit before the cross-boundary request served **one man sending
something UP his own chain**: his PM, his office, his super. That is not where the
friction on a real job is. The friction is at the **boundaries** — what the AV guy needs
from the electrician, what the HVAC foreman needs from the roofer, what the plumber needs
from the concrete crew, what nobody asks for until the drywall is already up.

**Nobody builds here, and the reason is the opportunity:** a cross-boundary document
belongs to no single company's software. Procore is the GC's. ServiceTitan is the service
shop's. Neither one is where a foreman texts another foreman the eleven things he needs
before Thursday.

**TWO THINGS MAKE AN INTERFACE TOOL DIFFERENT, and both are structural:**

1. **THE GATE — the deadline belongs to somebody else's schedule.** Ask for a back box the
   day after the board goes up and the answer is a change order and a patch. Ask for a
   sleeve after the pour and the answer is a core bit. So *needed-before* is not a field,
   it is a first-class **axis**: you group the whole list by it and read your own walk as a
   countdown. Six independent trade panels wrote their gates in their own words with no
   coordination and every one of them is a **milestone, never a date** — *"before rock goes
   up"*, *"before they backfill"*, *"before CMU caps out"*, *"before crane day"*, *"before
   frames get ordered"*. One panel said why out loud: **"I don't hand the super a calendar.
   I ask against his gates, because his schedule is the one that moves, not mine."**
2. **ONE WALK, N MESSAGES.** He walks the floor once and comes back with items for three
   different companies. Sending all of them one list is how all three ignore it. So the
   document narrows to a single receiver and addresses him by name, and the flagged block
   narrows with it — the electrician must never read the GC's problems in a message
   addressed to him.

**THE BARS DO NOT MOVE AT A BOUNDARY.** It must still be LIST-shaped (§THE GATE), and it
must still never compete with whoever owns and numbers the document (§THE SYSTEM OF
RECORD). The prune pass that cut these six vocabularies threw out, by name, everything
that was really an RFI to the engineer of record, a furnish-vs-install subcontract
question, a utility meter release, a special-inspection record, an as-built, and every
row with money on it. What survives is the ask itself: **ask for the hole; he buys the
pipe.**

**AND ONE RULE THE TRADES WROTE FOR US:** *"If I spec his material I own his warranty."*
That is the same instinct as §SAFETY arriving from the field instead of from us — which is
the strongest confirmation this doctrine has had.

### THE RETURN LEG — the half of every boundary nobody builds (added 2026-08-09)
The cross-boundary request has a **third** structural property, and it took a shipped tool
to see it: **it ends by asking for a reply that has nowhere to live.** Every request
document this toolkit produces closes with a line like *"anything on here you can't hit,
call me before you cover it"* — and then the reply is a text message with no structure,
*"yeah most of that's fine, the floor box is a problem, call me"*, in which every
commitment made is unfindable three months later when it matters.

**AN ANSWER IS NOT A SECOND REQUEST, and the difference decides the whole design.** A
request is COMPOSED: he walks the job and builds a list out of his own head, so intake is a
picker over his trade's vocabulary. An answer is ANSWERED: the list already exists,
somebody else wrote it, and the only thing this man adds is a verdict and a date per line.
So intake is a **paste**, the lead field is **his counterpart's own words kept verbatim**,
and the fast path is **tapping down a list** instead of adding to one.

**THREE RULES THAT ARE NOT OBVIOUS UNTIL YOU BUILD IT:**
1. **NEVER RE-PHRASE HIS ASK.** The moment the reply says something different from the
   request, the two documents stop being about the same items and cannot be laid beside
   each other. His line is stored untouched — which is why the row-log engine grew a
   nameable paste target rather than dropping his prose into the identifier axis that
   uppercases and +1s device tags.
2. **THE PARSER FAILS OPEN, ALWAYS.** An intake that guesses which pasted lines are asks
   has two failure modes and they are not symmetric: a junk row costs one tap to delete, a
   dropped ask is a commitment one company believes it has and the other never made. So
   the rules fire only on lines that are STRUCTURALLY not asks — a `Key:` header, a count,
   an ALL-CAPS group heading, our own sign-off block — never on prose, because a hand-typed
   ask *is* prose. Everything dropped is shown, with a button to put it back.
3. **THE LINE EVERYONE LEAVES OUT OF A REPLY IS THE DATE.** "Yeah we'll get it" is not
   something anybody can build a schedule on, and it is exactly what gets argued about
   later. So the page counts the dateless yesses and says so — in the UI where he can fix
   it, and deliberately NOT in the document, because publishing *"three of his six yesses
   are soft"* is his disclosure to make and not ours to volunteer.

**THE MIRROR IS NOW COMPLETE ON EVERY SERVED TRADE:** each one both asks (`rough-in-request`
and its six names) and answers (`answer-back`), because on a real job every trade is on both
ends of the boundary on the same day.

### THE THIRD MESSAGE — the loop closing on itself (added 2026-08-11)
Ask and answer shipped, and the loop still leaked, because **an answer arrives as one
message about twenty rows and the man who asked has to walk both lists by hand.** He reads
down the reply with his own page open on the other screen, ticks the eight he can find,
misses two — and never notices the three the other man said nothing at all about. Silence
is not a no and it is not a yes; it is the thing that shows up as a hole in a closed wall.

**IT IS AN INTAKE, NOT A FOURTH PAGE.** The rows already live on the request page and the
answer is about those rows. A separate page would need its own copy of them, and a second
copy of a list is a second version of the truth. So `shared/reconcile.js` mounts INTO
`<trade>/rough-in-request.html` — two lines per page, all seven at once.

**THE JOIN IS ON PROSE, AND THAT IS THE WHOLE PROBLEM.** A wrong join silently marks the
wrong item committed, which is worse than no automation at all. Four rules hold it up:

1. **PROPOSE, NEVER APPLY.** Nothing moves until he taps the button, every pair is on the
   glass — his line beside our row — before he does, and a pair we are not sure of comes in
   switched OFF and says *not sure it's the same one*.
2. **THE COMMON CASE IS NOT FUZZY AT ALL.** `answer-back` stores his counterpart's ask
   verbatim and never re-phrases it (§THE RETURN LEG rule 1), so when the other man used the
   toolkit the line coming home IS the line this page sent, character for character. That is
   an EXACT match and it is treated as one — **which is what makes the "never re-phrase his
   ask" rule pay for itself a second time.** Dice-scored fuzzy matching is the fallback for a
   hand-typed reply, and it is deliberately timid: high floor, and the runner-up must be
   clearly worse or nobody is sure of anything.
   **A ROW HAS MORE THAN ONE TRUE FORM**, because the document drops whichever axis it was
   grouped by. All four forms are offered to the matcher; without that, the exact match never
   fires and a perfectly clean round trip comes back entirely unsure.
3. **WE ONLY EVER TICK THE FIRST RUNG.** His answer is a claim by *him*. The top of this
   page's ladder is the requester having LAID EYES ON IT, and a text message is not eyes —
   so even *in already* ticks Committed and stops. The page says so where he can read it.
4. **NOTHING IS THROWN AWAY, AND A CLEAN TRIP MUST NOT LOOK LIKE A FAILURE.** Two different
   piles: lines of his we could not place (a real miss — read these, because one of them
   might be the answer to a row now sitting under *never mentioned*), and his header, counts
   and sign-off, which we recognised and stepped over. Merging them made a reply where every
   ask matched announce *"10 lines we couldn't place"*.

**AND THE OUTPUT NOBODY ELSE CAN COMPUTE — WHAT HE NEVER MENTIONED.** Only the page holding
the original list knows which asks came back unanswered, because only it knows what was
asked. It needs no join to be right (an unmatched row is unmatched), it is the reason to
open the intake at all, and it is scoped: if every row he answered belongs to one receiver,
the silence block narrows to that receiver and names him — reporting the GC's items as *"the
electrician never mentioned these"* would be the page inventing a grievance out of a filter
it forgot to apply.

**ONE MORE FIELD TRUTH, FOR FREE.** A committed row with no date attached is the thing that
gets argued about later, so a sure pair with nothing added reads **"no date on it"** — the
requester's half of the same rule `answer-back` already holds on the responder's side.

### THE VENDOR EDGE — the half that was unbuilt was never the list (settled 2026-08-14)
The roster had the supply-house / vendor edge ranked as *"the strongest unbuilt ASK
edge"* and read it as one page owed to nine trades. A panel of four field lenses and two
skeptics killed that in one line, **on disk**: six trades already ship that page under
their own names — `av/consumables`, `av/cable-list`, `electrical/pull-list`,
`framing/the-load`, `hvac/truck-stock`, `low-voltage/consumables`,
`plumbing/supply-house-order` — and `electrical/tools.js` has said *"copy it to the
warehouse **or the counter**"* since the day it landed. Nine pages would have split each
trade's item vocabulary across two files, and **one half goes stale**: the roofing-commons
scar with a purchase order attached.

**WHAT IS GENUINELY UNBUILT AT THIS BOUNDARY IS THE TRUCK, NOT THE LIST.** Three of the
four lenses said so unprompted, and the receiving lens said it hardest: the list is not
what fails. *"The flatbed with 20-footers and no boom, the drop at the front curb because
nobody said level 2 north stair, the driver with five more stops who takes the load
back"* — a real day of four men, and nothing on any order page could have prevented it.

**AND ITS ANSWER IS A FIELD, NOT A TOOL — which is the reusable finding.** The answer to
"how does the truck get in and where does it land" is *identical for every delivery to
that job from every vendor all year*, so putting it on the order means re-ticking it on
every order forever, which is the ceremony §THE GATE forbids. It ships as
`shared/dropoff.js`: one **sticky** block, typed once per job, mounted with two lines into
any page that already has a delivery mode, and no new storefront row. Ticks for where it
lands / how it comes off / when it can come, text only for what no picker can hold, a
`not before` clock because a truck at 6 when the gate opens at 7 blocks the street, and
**one line in the document every time it appears: it is an ask, not a booking** — a man who
ticks *boom · not before 7 · level 2* and taps Copy has put text on a clipboard, and the
failure is silent until four men are standing.

**THREE THINGS THE PANEL KILLED, keep them killed:** a per-line STOCK / SPECIAL-ORDER
axis splitting the message into *"pull this"* and *"tell me when"* — neither we nor he
knows what is on that shelf, and a guess wearing a heading is a guess presented as fact;
it survives as ONE SENTENCE asking for a **lead time** (never the word *quote*, which is
money and his PM's lane). A per-row **NO SUBS — CALL ME** flag — on a purchase document
that reads as a contractual term, and *"if I spec his material I own his warranty"* is
this program's own rule. A **branch picker** — a page that names real distributor
locations is impersonation with a shelf life.

**WHERE INTERFACE GOES NEXT:** (1) mount the drop-off block on the four order pages that
carry the typed half but not the ticks — `electrical/pull-list`, `low-voltage/consumables`,
`hvac/truck-stock`, `framing/the-load`. **This is now the strongest unbuilt INTERFACE rung
and it is an ENGINE job, not a mount:** `plumbing/supply-house-order.html` forks its own
Delivery/Will-call mode and the block hangs off that, while the other seven order pages are
pure `shared/checklist-request.js` configs and **that engine has no fulfilment axis at
all**. There is nothing on them for `Dropoff.mount` to attach to. ~~(2) The sub → owner
access / escort / badge request~~ — **SHIPPED 2026-08-15 as `<trade>/getting-in.html`, all
ten kits; see §GETTING IN below.** (3) The long-lead **gear chase** the electrical
lens proposed and which is a different document from an order: the same list sent six
times over four months, with a first-class *what I'm asking for* axis (a ship date ·
released · dimensions and weight · approved schedules · freight) because inside one
distributor those route to four different people. The ask/answer loop itself stays closed.
(4) **The forward leg on the new boundary.** Ten trades can now ask a building for a night,
and nothing reads the answer back the way `answer-back.html` reads a rough-in ask — the
owner boundary is served in one direction only, and the GC's copy is the one that gets
FORWARDED rather than sent.

## GETTING IN — the first tool aimed at a party that is not a trade (2026-08-15)

`<trade>/getting-in.html`, **all ten kits including creative** — one page file, ten
`TOOLKIT_GETIN` configs, shape #2 (`shared/note.js`). The ask a sub sends the OWNER'S side
— the building engineer, facilities, security, the school office, the man with the keys —
to get a crew into a room somebody else locks: the night, the rooms, what he has to open,
who's coming, and the heads-up that decides whether the crew finishes or gets walked out.

**WHY THIS BOUNDARY IS DIFFERENT FROM THE OTHER NINE.** Every INTERFACE tool before it
crosses to another TRADE, where being wrong costs an hour and a phone call. This one
crosses to the party that can leave four men and a truck of gear standing at a locked door
at six in the morning. Both field lenses independently ranked the same failure first, in
the same words: **not a date.** A text that says "tomorrow night" is read at 7am the next
morning and is already wrong.

### THE HANDBACK RULE — the reason this page exists at all

A skeptic given the program's own rules as weapons came back with a real kill: every noun
in the proposal — escort, badge, after-hours, freight, dock, hot work, power-down — already
has an owner and a **numbering authority** on the building side, and §THE SYSTEM OF RECORD
says never compete with whoever owns and numbers the document. Hot work has a Hot Work
Permit. A sprinkler main has an Impairment Permit and sometimes a call to the fire marshal.
Badging has a visitor-management system. Ticking a box called *hot work* manufactures the
belief that ticking it handled it, which is **worse than no tool**.

The answer is not to drop those from the page — undisclosed hot work near a detector is the
single fastest way onto a permanent do-not-use list, so silence is the worse failure. The
answer is that **none of them is a status. Every one of them ends in a question aimed back
at the man who owns the process:**

> - We have to touch the fire alarm *(tell me who puts the panel on test — we don't)*
> - A sprinkler head is in the way *(that's your impairment process — tell me how you run it)*
> - Something has to come off power *(your engineer throws it, not us — tell me the window)*
> - Hot work — torch or solder *(that's your permit — tell me how you want it done)*

That is §THE SYSTEM OF RECORD applied one level down, to a checkbox. It is asserted as a
RULE by `tools/toolkit-gates/getting-in.mjs`: any option naming a permitted activity must
carry a sub that addresses HIM, and the words that make a permit sound satisfied are banned
outright. A later cycle rewriting one of those into *"fire alarm coordinated"* would look
like a tidy-up and would be the defect.

### KILLED, AND STAYING KILLED

**Lockout/tagout and confined space** — execution procedures with joint signatures and
atmospheric records; their mere presence invites the belief that a tick covers them. **A
fire-watch tick** — the building's determination, never ours to declare; it survives only
inside the hot-work handback. **ICRA class I–IV logic** — encoding it fakes a process
nobody here has touched; the plain ask *"patient or clinical space next door — tell me what
you need from us before we start"* survives. **Any generated reference number, status field,
sent state or approved toggle** — this page has no channel back and will never know.
**Insurance limits, policy numbers, expiry dates** — money-adjacent, and myCOI owns it.
**A risk score computed off the ticks** — a JHA wearing a form calculation.

**WHAT SURVIVED THE COI CUT, and it is a judged call against the skeptic:** the ROUTING ask.
*"Tell me who gets our COI — if it isn't already on file"* carries no number, no limit, no
date and no money; it is a question about where to send a document, and the field lens
ranked a missing certificate the single biggest day-killer on this boundary.

### NAMES — the panel split three to one, and both halves were right

The receiving lens needs full legal names days ahead or no badge gets cut. The skeptic
wanted **no names at all**, because the whole mechanism of this program is *copy the output
and paste it somewhere*, and the natural paste target is a crew group chat — PII broadcast
with zero access control, by design, as the modal use of the Copy button. A jobsite phone
is also lost, handed to a new hire, and unmanaged.

So: **names are OPTIONAL rows, never required, and DOB / SSN / licence / badge numbers are
not fields and never will be.** Names are also the one thing Clear wipes while the sender
block stays. And the document spends a line saying so, but **only when names are actually
on it** — a standing sentence about dates of birth on an ask carrying no names is noise:

> Names only on here — no dates of birth, no ID numbers. If your badging needs those, send
> me your form or your portal and I'll do it there.

That line is worth more than the fields it replaces: it keeps the next round of badging in
HIS system, which is where it already lives.

### THE HEADING IS THE ASK

The receiving lens wrote it unprompted: he reads this on a lock screen between two other
jobs, and *"Hi, hope you're doing well"* sinks under the next five texts and gets answered
tomorrow. So the document opens with the two lines he triages on and nothing else:

```
ACCESS REQUEST — Sat, Aug 22  ·  6pm – 2am
Bishop Ranch 3  ·  Nights all week
```

**And there is deliberately NO "asked on" stamp.** Every other document in this program is
a record of something that already happened, so it dates itself. This one is about a night
that has not come yet, and the first live read of it put *"Sat, Aug 22"* on line one and
*"Aug 15, 2026"* on line two — a second date one line under the first is the exact
ambiguity the whole page exists to kill. The cadence went there instead.

### WHAT THE ENGINE GREW, all additive, all no-ops for the eleven older note pages

- **`kind: "date"`** — the phone's own date picker; state keeps raw ISO so it restores, the
  document prints the **weekday** beside it, because a weekday that disagrees with the
  number is the one typo a receiver catches.
- **`u.doc(id)`** on `subline` and `titleSuffix` — asks for the value the DOCUMENT would
  print rather than the value STATE holds. The spec pass on this engine had already flagged
  the gap: `get()` returns the raw read, so a heading needing the printed form had to
  re-derive it by hand.
- **`data-f="<field id>"`** on every field wrapper — so a gate drives a page by the id the
  config uses instead of by counting inputs or matching label prose. Matching on words means
  a gate silently stops testing a field the day somebody improves its label, which is the
  same class of drift as a hand-kept watch list, one layer out.

### CREATIVE IS NOT A RESKIN, AND THE PRODUCTION LENS ARGUED IT SHOULDN'T SHARE AN ENGINE

Its case: the container (when, where, how many, which door, which lift) is identical, but
the **payload** asks a different question. A contractor's disclosure answers *what system
are you touching and does it need a permit*. A crew's answers *what is going to appear in an
image that leaves this building, and what are you moving that has to go back exactly as
found*. Its own recommendation — *"share the atoms, not the assembly instructions"* — is
precisely this program's architecture: the engine is the atom, the `TOOLKIT_GETIN` config is
the assembly. So one engine, ten configs, and creative's heads-up list is genuinely its own
document: haze finding the fire alarm (handed back the same way hot work is), what's on
camera, what gets moved and restored, the generator's exhaust against their intakes, cable
across a threshold so a fire door can't close, the real headcount including client and cast,
asking THEM to hold their own noise during takes — the one disclosure in the whole program
that runs the opposite direction — and what "wrap" actually means.

**It is called Getting In, not "Shoot Day Confirm"** as the creative roster had it. *Confirm*
is the exact defect the page is built to prevent.

### THE GATES

- `tools/toolkit-gates/getting-in.mjs` — drives the real page at 390px, sets every field,
  and looks for each value BY VALUE in what the real Copy button puts on the clipboard;
  asserts the heading carries date + window + what it is; asserts every ticked option's
  **handback** survived into the message, because a tick that ships without its question is
  the defect; asserts the ask-not-a-booking line and the ask for the window he is *actually*
  granting; asserts the names-only line appears only with names on it; and asserts Clear
  takes the crew and leaves the sender block.
- `tools/toolkit-gates/note-live-fields.mjs` — **the BACKPORT**, and it is the same class the
  order engine was caught on: change ONE field, alone, on a wiped device, and the copied text
  must CHANGE. `docSkip` exempts a field BY NAME, read out of the page's own source, so an
  author cannot silence the gate without saying in the config that the omission was on
  purpose. Shape #2 cannot have the *drift* half of that bug — it binds `input` and `change`
  once, on the whole form, by delegation, so there is no second list — but it can still drop
  a field silently through a misspelled `kind` (BUILDERS returns undefined and the field
  vanishes with no warning), a colliding `id`, or a `docSkip` copied in from another page.

## MASONRY — trade #11, and the first family the promotion rule could NOT decide (2026-08-15)

**THE RULE THAT PROMOTED TRADES #7, #8 AND #10 STOPPED DISPOSING, AND THAT IS THE
FINDING.** Every previous family was chosen by one measure — the highest-count unserved
RECEIVER in the interface matrix — applied with no second criterion. Re-tallied off all
ten shipped `items.js` files rather than off the summary table, the count nominates
**steel** (four kits name it) over **masonry** (three) and **ceilings** (three). One of
four independent lenses declared "no taste was required at any step" and had still missed
`concrete/items.js` `{v:"steel", label:"Steel erector"}` — so its winner was not even tied
for first on the axis it called decisive. **A count that has to be recounted is a
nominator, not a judge.** From #11 on, the rule nominates and the record disposes.

**BOTH NOMINEES ABOVE MASONRY WERE KILLED BY SENTENCES THIS BOOK HAD ALREADY WRITTEN.**

- **CEILINGS owns the most-NAMED gate on the board** — the lid appears in all six trade
  gate ladders — and it lost anyway, because §ROOFING's second qualification is owning an
  IRREVERSIBLE gate, not a frequently-named one. `concrete/trade.js`, the config that
  promoted trade #10, says verbatim: *"a wall can be cut, A CEILING CAN BE PULLED, a roof
  can be flashed after the fact."* The program named the ceiling as its own counterexample
  to a one-way gate, in the text that promoted the last family. (The *other* half of the
  kill — that ACT is really the framing kit's crews — was REFUTED and should not be reused:
  `framing/items.js` declares `grid` "Grid / ceilings" as a RECEIVER with its own start
  date. The served kit that would supposedly absorb it treats it as another company.)
- **STEEL was pruned by name.** §THE INTERFACE records that the six-vocabulary prune threw
  out *"a special-inspection record"*. The bolt-up log, the weld map, the WPS and the mill
  cert ARE that record under IBC ch.17. The test that decides it: every trade touches
  certified data at its edges; the ones that die are the ones where it is the CENTRE.
  Second, half of steel is already served — `concrete/trade.js` defines its crew as "form
  setters, **rodbusters**, placers and finishers" and the commons chip reads "Concrete &
  Rebar". NAICS 238120 is one code for erection and rebar placement.

**WHY MASONRY, IN THE PROGRAM'S OWN TERMS.** Three kits name him as a receiver on disk
(electrical "Mason / CMU", plumbing "Mason", roofing "Mason / chimney") and **two of them
wrote his day into their own countdowns in their own words** — `electrical/items.js`
`{v:"cmucap", label:"Before CMU caps out"}` third of seven, `plumbing/items.js`
`{v:"block-up", label:"Before block goes up"}` third of eight — each carrying an ask bound
to it: *"Set my boxes as you lay it" · "Run my pipe up the cell" · "Leave the cell open
above my box" · "Don't grout the cell I'm in" · "Call me the morning of that lift" ·
"Sleeve laid in as you go up" · "Chase in the block for my stack" · "Knock-out at my paint
mark."* **Twelve spec lines aimed at a man with no page to answer them on** — the exact
condition `concrete/trade.js` gives as the reason trade #10 was promoted, one trade over.
He OWNS that gate rather than racing it: the mason sets the date everybody else counts to,
and a capped, grouted wall with a bond beam in it is a core bit through grout and rebar,
and on a structural wall a call to the engineer of record before anybody starts a saw.
No fork, verified rather than assumed: `concrete/items.js` returns ZERO hits for
cmu/mortar/brick/veneer/tuckpoint — every "block" in that file is `blockout` or `blocking`.

**THE DISSENT IS RECORDED AT FULL STRENGTH, because it is right about two things.**
Masonry is the SMALLEST working population of the three finalists, on work that is losing
ground to tilt-up and panel, and it is **receiver-heavy and ask-light** — he is chased by
everybody and chases comparatively few people back. That is why `rough-in-request.html`
here is deliberately shorter than concrete's fourteen rungs instead of padded to match: a
rung invented to fill a page is worse than a short page. And the runner-up was neither
finalist — it was **SITEWORK**, the only remaining candidate clearing both disqualifiers:
backfill is position #1 on three shipped ladders and a closed ditch does not reopen.

**THE ACCENT COULD NOT BE THE TRADE'S OWN COLOUR, AND THAT IS A MEASUREMENT.** Brick red
fails twice — it sits in the band low-voltage coral (14.2) and plumbing copper (24.0)
already crowd, and **red cannot clear the contrast bar at any lightness that is not a
pastel**: measured at hue 352 against the #242A31 nav, L50 3.64 · L55 3.76 · L60 4.02 ·
L65 4.48 · L70 5.12 · L75 6.03, never reaching 7. The only way there is L78+, which is a
rose sitting between roofing's pink and low-voltage's coral — a third pastel in a row. So
the accent goes to the TOOL instead of the material: the line, at hue 75.0, the middle of
the widest genuinely chromatic arc left (45.7 → 104.2, 58.5°). **The stale hue list nearly
took the decision:** it recorded the commons at hue 90, which is `#BABEB6` — a 4%-saturation
GREY. Treating a grey as occupying 90 degrees of the wheel is how a rack talks itself out
of its own widest opening.

**THE TRADE'S FOURTH REFUSAL.** Roofing refuses CAUSE and COVERAGE; concrete refuses those
and STRENGTH; masonry refuses all three and **BRACING AND LOADING**. A wall standing
without its diaphragm is the thing on this job that kills people, and it is engineered. A
foreman may write that a wall is standing, that it is not braced, and that he wants
somebody to come and look. He may not be led into writing a height, a spacing, a wind
figure, a duration, a restricted distance, or that a wall is safe to load, backfill
against or work under. **`wheres-the-wall.html` has no "it's fine" value on its don't-touch
axis at all** — a blank means he said nothing — and the document carries the guard in
words the config cannot switch off: *"A wall not named here is a wall I have said nothing
about."* That is THE INVERSE-CLAIM GUARD, and it is this trade's contribution to the
program: any list that names the dangerous items will be read as clearing the ones it
did not name.

**THE SEED ROSTER, from an 8-agent fan-out (four selection lenses → a synthesis arm that
never saw the build → three in-trade panels → a 20-year prune → a build spec).** Three
panels independently named the same three rungs. Shipped: `wheres-the-wall` (pinned) ·
`answer-back` · `rough-in-request` · `tm-tag` · `write-up` · `getting-in` ·
`total-package`. **THE ONE, chosen by the prune:** *"electrical and plumbing have been
ordering two other trades to count down to 'Before CMU caps out' and 'Before block goes
up' for months and nothing anywhere publishes the number they are counting to."*

**~~RANKED NEXT, AND NOT HALF-BUILT ON PURPOSE:~~ SHIPPED 2026-08-15: `yard-call`.** All
three panels named the afternoon material call unprompted — block by shape and cube,
mortar by the bag in a type HE states, sand by the yard, wire by the roll, lintels by
length, and which side of the building the forks put it on. It was held back as a
vocabulary build the size of the supply-house order, on the rule that **half a yard call is
worse than none**: a man who calls in an order off a list that is missing a line stops
opening the list. Built as the EIGHTH instance of shape #1 — 59 lines, seven sections —
and the hold was right about where the work was. **What it does that the other seven order
pages do not, and what the next one should steal:**
- **THE UNIT OF ISSUE IS ATTACHED TO THE NUMBER, not offered as a select.** "6 block" and
  "6 cube of block" are two different trucks. Each line declares the word the yard sells it
  in; a BARE number gets that word attached ("6 cube", "40 bags", "1 roll"), and anything
  written in words is left exactly as written ("half a cube"). The tool must never re-count
  a man's order, and a unit select on 59 lines is 59 taps nobody makes.
- **THE MESSAGE ENDS ON WHAT IS NOT ON IT.** The failure a yard call dies of is an ABSENT
  line, so the document closes by naming them — a line with no count, units with no mortar
  and no sand, a heavy line with no side — **as questions the yard man can answer**, never
  as corrections. He is allowed to order block on its own and the page does not get a vote.
  This is the forget-list from engine B arriving in shape #1 for the first time.
- **THE RUN.** Face units come out of a run and the colour moves run to run; a re-order
  that does not name what is already standing is how a wall gets a stripe that will not
  wash off. A flag on the lines it applies to, a passthrough field in the header, a
  gathered MATCH list, and a call-out when one exists without the other. Never a lookup —
  we hold nobody's lot numbers.
- **THE SIDE IS ONLY ON WHAT THE FORKS CARRY**, deliberately unlike `framing/the-load.html`
  where a boom truck sets every line. A drop select on a box of weeps is a control that
  teaches a man to skip controls.

**STILL OWED IN THIS KIT, in the prune's order:** `before-we-grout` as a ROW LOG (the
write-up library ships the narrative; the counted per-cell ledger is the receiving half of
the EC's and the plumber's live asks) · the panel/mock-up record (every colour, joint and
cleaning argument for a year resolves at one wall, and nothing in the program points at it
yet — the `yard-call` MATCH flag is now the first thing that would read it).

**KILLED BY THE PRUNE, do not resurrect:** `still-waiting-on` (a config flag — `shared/rowlog.js`
already ships named document filters for exactly this) · `hose-test` (the shape went
looking for a job; the owner's consultant runs it) · `whats-in-the-block` (answer-back's
yesses re-typed — a framer's backing is his OWN scope at dozens of points, a mason's
built-ins are almost entirely the EC's and the plumber's asks) · `what-we-opened` (counts
by elevation with the money stripped out is still a pay application) · `grout-day` (every
number on it is one we are forbidden to supply, leaving four ticks and eight empty boxes).

## CREATIVE — trade #9, and the first one that is not a construction trade (2026-08-13)

Stood up from a WISH, not from the researched ladder. The wish, verbatim: *"Tools for
creatives like the gen art collage maker striving to surpass capcut — what else creative
aspect can we revolutionize democratize […] follow the nursery algorithm […] nursery
algorithm is the marriage algorithm."*

**SAY THE HONEST THING FIRST, because the panel insisted on it:** the wisher asked to
surpass an EDITING PRODUCT, and this trade answers a different question. Collage Studio is
the answer to the CapCut half. This kit is the answer to the *"what else can we
democratize"* half — the paperwork **around** the edit, which is the half nobody is
building because a cross-boundary document belongs to no company's software. Pretending
otherwise would be the claim inflation the public discipline forbids.

**THE MARRIAGE ALGORITHM IS LITERALLY WHAT BUILT IT.** Nothing new was engineered. This
trade's week is the same five engines wearing different words: the round the client slid
past the deal is an extra-work tag; the wall of notes they emailed is somebody else's list
answered line by line; what they still owe you is a row log. That is the widest test
one-runtime-many-trades has had, and it passed on data alone.

**THE PANEL NARROWED IT BEFORE A LINE WAS WRITTEN** (3 independent lenses — a freelance
shooter/editor, a studio producer, an incumbent-naming skeptic — plus a synthesis pass).
Verdict: **BUILD_NARROWER**, unanimous. *"Creatives" is dead as a framing* — a photographer
hands off usage terms, a motion designer hands back source files, a print designer hands off
specs, and a page carrying CUTDOWN and VO SCRIPT bounces all three. The trade served is ONE
population: **the person who takes a client brief, shoots, cuts and delivers against a scope
with revision rounds, and who is also their own producer.**

**SHIPPED THIS CYCLE** (consensus 3/3 on both):
1. **Notes Back** (`notes-back.html`, shape #3) — the panel's #1 by a distance, scored
   9/9/7. Territory is strictly *the notes the review tool cannot see*: the payer never logs
   into the review platform, so half of small-shop notes arrive as an email paragraph, a doc
   or a call typed up after. And no review tool can say **that's an extra** — the judgment
   the user is avoiding, made one tap in the middle of the list they are already going down.
2. **That's Another Round** (`thats-another-round.html`, shape #2) — 9/7/6. The incumbent is
   not software, it is *writing nothing and eating the work*. The numbered invoice-tied
   change order belongs to whoever numbers it; this is the unnumbered, same-day heads-up.

**THE RANKED ROSTER, off the same panel** — build in this order, re-ranked by wishes:
3. **Still Waiting On** (row log) — ✅ **SHIPPED 2026-08-13** (`still-waiting-on.html`).
   The dated chase for what the client still owes. *Clipboard round-trip was named a SHIP
   GATE here* — no account and no server means the list lives in one browser, so pasting
   yesterday's block back must reload it or the phone→laptop switch loses everything and
   the tool is abandoned once. **Satisfying that gate is what exposed the program-wide
   defect** (§SCARS 2026-08-13): 21 row logs promised a backup the engine could not read.
   The gate was met in `shared/rowlog.js`, so every trade got the restore, not just this
   one. The build also added the axis the roster did not name — **what each thing is
   holding up**, which the panel's field lens called the half of this message nobody
   writes and the half that gets it answered.
4. **Before I Export** (checklist → request) — the deliverable questions answered before the
   render. It wins by ASKING and never asserting. Ratios and frame rates are safe as *user
   picks* (geometry and arithmetic the trade says out loud); codecs, bitrates, resolutions
   and platform names are not. **Now the top unbuilt rung on this trade.**
5. **Shoot Day Confirm** (checklist → request) — ⚠️ **HALF SHIPPED 2026-08-15** as
   `getting-in.html`, and the honest record is that it shipped the **venue half** — the ask
   that gets you into somebody else's building — not the whole rung. The half still unbuilt
   is the **participant-facing** one: the short "how the day goes" note to talent, a client
   coming to set, or a location owner (call time, where, how long, what happens, who to
   ask for). Every one of this trade's 4 tools and 13 documents points at a payer, a venue
   or the next editor; nothing points at the person who has to SHOW UP. Survives ONLY
   because it is deliberately **not a call sheet** and must never grow into one;
   StudioBinder owns and numbers that document.
6. **The Write-Up Setup** — ✅ **SHIPPED 2026-08-15** (`write-up.html` + `docs.js`), and it
   was never on this list, which is the finding. The panel that built this roster was asked
   what to BUILD NEW and answered well; **nobody asked what this trade was OWED.** Creative
   shipped with two of the five document engines and ran live carrying three of twelve
   shared modules while DOCS work landed on the other nine trades — a gap no ranked roster
   could surface, because a roster of ideas has no column for a sibling's engine you never
   inherited. The check that finds it is mechanical and takes one command: grep every
   trade for every `shared/*.js` it loads and read the holes. **Run it before ranking
   anything, on every trade, forever.** This cycle took creative from 3 of 12 shared
   modules to 5 (`docspec` and, riding with it, `find`). Still owed here: **`package`**
   (the total-package bundle every other trade ships) and **`reconcile`**; `checklist-request`
   and `pickfilter` land the day *Before I Export* ships.
Deferred with reasons: *What's in the drop* (folds into Before I Export as a second output
mode, not a sixth page) · *Turnover Sheet* (narrow — real only for a first job with a new
finisher) · *Booking Confirm* (a different boundary — hiring, not client delivery, and one
inch from rate data we cannot own).

**KILLED, so no later cycle resurrects them:** SOW / brief / treatment / proposal builder
(negotiated paragraphs, and Docs owns and numbers it) · delivery-spec or export-preset table
(the instant temptation and the fastest way to burn this audience — we do not own the data
and it changes quarterly) · anything near the player (timestamped comments, version compare,
review links) · shot list, budget, gear inventory, full call sheet · quote / rate calculator
/ "typical revision fee" (freelance numbers swing 4–5× by market; a low suggested figure gets
screenshotted back at the user by their own client) · numbered change order tied to invoicing
· music-licence, usage or release explainers (stating what a licence permits is legal advice)
· any editing feature the CapCut framing invites.

**THIS TRADE'S SAFETY EDGE IS NOT THE CONSTRUCTION ONE.** Nothing is rated or sized here
either, but the live wires are: no platform resolutions, bitrates, codecs, safe areas or
file-size caps · no licence or usage terms · no rate cards, day rates, kill fees or deposit
splits · **and no "standard number of rounds"**, which is the most tempting and the most
false. No brand names as data — no dropdown of platforms, NLEs, review tools or transfer
services. Licence and release appear as item NAMES and nowhere else. **Tone is a safety edge
here, not a preference:** a legalistic or passive-aggressive line costs this user their
client and they will blame the page — plain, warm, factual, ending in an option rather than
an ultimatum. One dialect throughout: US.

**THE LADDER BECAME DATA, AND THAT IS THE BACKPORT.** `answer-back.html` hardcoded its four
rungs, and this trade needs a fifth idea no construction kit has (*that's an extra*). A page
eight trades share may never be forked for a ninth, so the words moved to
`TOOLKIT_ANSWER.answers` in each trade's `items.js` and the page now reads **positions**:
[0] the promise that wants a date on it, [1] already settled, [2] declined, [3] blocked on
the other side. All nine pages carry the change; the eight that say nothing keep the exact
four rungs they always shipped. `creative/notes-back.html` diverges from its siblings **in
static prose only** (the construction copy addresses one man about another man; this trade's
counterpart is a client of unknown gender writing notes) — the JS is byte-identical and must
be swept as one.

**THE COMMONS FLOOR WAS A CLAIM, AND TRADE #9 MADE THREE ROWS FALSE.** `t: ["universal"]`
means *every* trade genuinely eats it. A cordless drill, a torpedo level and a non-contact
voltage tester do not ride in a camera bag, and neither do the tips "get the big stuff in
before the last opening closes", "shoot your work before it gets covered" (where SHOOT means
photograph — the word means the opposite thing to the new trade) or "check the revision, not
just the sheet number". All six were re-tagged to the eight construction trades rather than
deleted, and the two stale "six trades"/"seven trades" comments were de-numbered so they
cannot rot again.

**THE PARSER WAS DRIVEN AGAINST THIS TRADE'S REAL PASTE BEFORE SHIP, and it found the one
thing the layout gate cannot see.** Four inputs through `lineUp()` in isolation: the
placeholder example, a real client email, a numbered Word list, an exported comment row with
tabs. The three structured ones are clean and timecodes survive untouched in all four. The
EMAIL puts its SUBJECT, its greeting, its "thanks for v2!" and its sign-off in as note rows.
The subject was fixed (see §SCARS — `firstLineIsSubject`, and it lands in the restorable
skipped list rather than vanishing). **The greeting and the sign-off were left alone on
purpose.** The intake's hard invariant is
*never silently drop an ask*, and every rule it holds fires only on a line that is
STRUCTURALLY not one; a greeting rule is a PROSE rule, and a prose rule broad enough to eat
"Thanks!" is broad enough to eat a note. So the page now SAYS it in this trade's words — the
hello and the thanks land as rows, tap them away, we'd rather hand you one row too many than
lose one of theirs. **That is an EVO-LOOP hypothesis, not a solved problem:** if this trade
pastes once and never returns, the greeting noise is the first suspect and the honest fix is
a smarter intake, never a prose blacklist. Also noted: `HEAD_KEY` drops a line starting
`Re:`, which in a client thread is sometimes a real note — recoverable from the skipped list,
which is exactly what that list is for.

**FOUND BY THE GATE AND NOT FIXED THIS CYCLE, named so it is not lost:** on `credits.html`
the tool link inside a credit entry measures **153×16** — under the 44px tap floor, at every
width. It is not a creative defect: that page is byte-identical across all nine trades and
the link has been under the bar on AV's wall since the wall existed. It is also the awkward
case the floor was not written for — an inline link inside a running sentence, where making
the box 44px tall breaks the sentence around it. **That is a BACKPORT rung**, and it wants
the fix the hub cards already got (a real control beside the text, not a taller word), swept
to all nine at once. Deferred rather than bodged late in a cycle whose gate had already run.

**TWO OPEN RISKS, both named by the panel and both unresolved on purpose:**
- **Design register.** A layout a roofer reads as refreshingly blunt may read to this trade
  as broken. The shared engines own the pixels and forking their CSS is forbidden, so this
  cycle changed only the palette and the words. If the EVO LOOP shows this trade opening and
  bouncing, that is the hypothesis to test — not a licence to fork a stylesheet first.
- **Distribution.** Three lenses independently flagged that this trade has zero discovery
  overlap with the eight construction kits. A correct family with no distribution looks
  identical to a wrong family. Measure opens before funding a batch two.

## SCARS — what went wrong, so it does not go wrong twice
Append here when a cycle finds one. Each is a rule, not a story.

- **THE UI COPY WAS A PROMISE AND SIX PAGES BROKE IT IN THE SAME WORDS (2026-08-16).**
  Six order pages shipped a collapsed section headed **"typed once, saved on this phone"**
  over a hand-copied `var STICKY = [...]` / `var SKEY = "toolkit.<trade>.<page>.header.v1"`.
  The comment above it said the values were *"the same every morning for the life of a job."*
  The code remembered them for the life of a PHONE. A foreman on two jobs — the normal case,
  not the edge one — got ONE gate code, ONE signer and ONE PO across both, and whichever he
  typed last is what the next supplier read. **THE RULE: a sentence in shipped UI copy is an
  assertion about the code, and it gets a gate like any other.** The twenty lines were also
  the exact fork `shared/checklist-request.js` was extracted to stop, surviving in the one
  part of the page the engine never took over — so nothing was watching it.

- **THE PANEL KILLED THE GUARD I WAS ABOUT TO BUILD, WITH TWO SENTENCES FROM HIS OWN WEEK
  (2026-08-16).** The proposal was a staleness BANNER: notice the job name changed, print
  "filled in for <job>", offer a clear button. A two-job commercial foreman broke it before it
  existed — he types *"Meridian TI"* on day one and *"Meridian"* or *"435 Bryant"* on day
  forty (a mismatch that fires on nothing and trains him to tap past it), and he types
  *"warehouse"* out of habit while standing at the downtown job (a MATCH, silent, on the one
  case the guard exists to catch). **A guard that compares free text to free text is not a
  guard.** His replacement is the design that shipped: *"a banner has to be read and I won't
  always read it one-handed off a ladder at 6am. I will always notice the block change when
  I'm the one who tapped the job that changed it. Put the safety in the action I'm already
  taking, not in a warning stacked on top of it."* **THE RULE: prefer a guard the man
  EXECUTES over a guard he must READ.**

- **A SCOPE I INVENTED LIVED FOR ONE HOUR AND A GATE KILLED IT (2026-08-16).** The same
  foreman was right that `fHow` — delivered / will-call / the shop runs it out — must not
  travel with a JOB: *"that is a decision about this order... ask it fresh every single
  time."* So the first cut gave `shared/jobcard.js` a third scope, `fresh`, blanking it to the
  page default on load. `order-live-header.mjs` failed three pages in one run and the failure
  it names is **worse than the one being fixed**: a man picks will-call, ticks forty lines over
  twenty minutes, iOS evicts the tab, and he comes back to all forty lines intact and the
  delivery method silently back on "Deliver to site" — he would never look, because everything
  he actually worked on came back. **THE RULE: "not remembered across jobs" and "not
  remembered at all" are different requirements, and the second one loses work.** Its real
  home was neither scope: the engine's own `persistExtra`, reset by Clear. The `fresh` list is
  gone from the module and the reason is written where the next page will read it.

- **A COMMENT THAT WAS TRUE WHEN IT WAS WRITTEN GOES ON READING AS PERMISSION (2026-08-16).**
  `commons/tips.html` did not load `names.js`, and the tag was absent **deliberately, on a
  real measurement** written in a comment right where the tag would go: the alias index JOINS
  on an object's generic name, a tip is a sentence, and 0 of 147 tips carry one — so the join
  is worth exactly nothing there, and re-measuring today it still is. That call was correct
  the day it was made. It became wrong the day the HAND-OFF landed in the shared engine,
  because the hand-off needs NO join: it routes a man who typed a word this surface cannot
  answer to the table that owns it. Nobody re-read the comment, because the comment read as a
  current decision rather than as a decision with an expiry.
  **The cost fell hardest on the surface with the best excuse.** A zero join is precisely what
  makes tips the surface most likely to be handed a word it cannot answer, and it was the only
  one with no way out. 404 words the commons knows — measured on the shipped page, 24 probes:
  **11 dead-ended** ("Nothing on this page goes by that" for *stinger*, *snake*, *Channellocks*,
  *lav*) and **13 came back CONFIDENTLY WRONG** — *"Teflon tape"* matched a tip about tape and
  the page said **Matches**, which is the exact `zap strap → Wire strippers` failure the
  hand-off was built to kill, replayed on the surface the fix never reached.
  **THE RULE: a claim quantified over "every surface" is asserted on every surface, or it is
  asserted on none.** The deploy counted the join by loading all four data files into ONE
  synthetic window, where `names.js` is present by construction — so it could never see a real
  PAGE that omits the script tag, and every check stayed green for two days. `commons-names.mjs`
  drove the hand-off on `index.html` only, which graded it on the one surface that needed it
  least. Both now derive from `COMMONS_SURFACES`, and the deploy asserts the tag **on the real
  page with comments stripped** — because the reason this survived review is that `tips.html`
  *mentioned* `names.js`, in the comment explaining its absence. **A grep would have passed.**
  Verified firing on this exact defect and nothing else: 24/24 fail against the shipped page,
  0/24 against the fix, with the other 326 checks green in both states.

- **A MEASUREMENT THAT MOVES WITH THE DEFECT CANNOT MEASURE THE DEFECT (2026-08-15).**
  The nav dropdown was running off the right edge of the glass, so the runtime clamped it
  against `window.innerWidth - 8`. It read green by hand and stayed red in the gate. Under
  Chromium's mobile emulation `window.innerWidth` is the VISUAL viewport, and the visual
  viewport **grows to cover whatever runs off the side** — with the panel 8px over, the
  browser reported 368 against a 360px layout viewport, so the clamp corrected by exactly
  the amount that preserved the overflow, at every width, on every trade. **The rule: a
  clamp is written against the same quantity the assertion reads.** Both gates compare
  `documentElement.scrollWidth` to `documentElement.clientWidth`, so `clientWidth` is the
  limit — it is the layout viewport and it does not move. Note the direction is the
  OPPOSITE of the vertical question six lines away in the same function, where
  `innerHeight` is right precisely because it is the glass and `100vh` is not. **Same
  window object, two axes, two different correct answers — so name which viewport you mean
  every time, and never reason by symmetry from the other axis.**

- **A SHARED-LAYOUT FIX MOVES EVERY ELEMENT DOWNSTREAM OF IT, AND THE GATE THAT NAMED THE
  BUG IS NOT THE GATE THAT CATCHES WHAT YOU BROKE (2026-08-15).** Letting the trade word
  survive on the nav bar pushed the Tools button right on ten trades; the dropdown hangs
  `position:absolute; left:0` off that button with `min-width:250px`, so the panel started
  running off the glass — 2px on roofing at 360, 66px on electrical at 320 with the text
  bumped. **mobile-watertight passed all 107 pages at four widths while this was live**,
  because it had never opened the menu: the one state every page in the program shares was
  the one no reveal reproduced. `menu-reachability.mjs` caught it, and only because a gate
  that opens the menu happened to exist for an unrelated reason. **Two rules. (1) When you
  change something the shared runtime INJECTS, run every gate that touches that surface,
  not only the one that named the bug you set out to fix. (2) A page that a gate loads and
  leaves alone is not the page anybody uses — this is the third time that sentence has been
  written here, and the fix is the same each time: a REVEAL.** The Tools menu is now one,
  sampled at a hub and one tool page per trade rather than swept, because doubling the
  runtime of the gate that runs before every ship buys a gate nobody runs.

- **THE GATE MEASURED FIVE THINGS AND WAS STRUCTURALLY BLIND TO THE SIXTH (2026-08-15).**
  Ten of eleven kits rendered their own name as one letter and an ellipsis at 390px —
  "E...", "L...", "P..." — for the entire life of every page, with MOBILE-WATERTIGHT
  reporting PASS on all of them. Overflow could not see it (the word was CLIPPED instead
  of overflowing), tap targets could not (the brand holds 44px whether the word is there or
  not), and the three fixed-bar checks could not (the nav is sticky, not fixed). **Five
  correct measurements, one shared blind spot — and the blind spot was the only element in
  the toolkit that is ALLOWED to shrink.** The rule: **anything you deliberately let shrink
  needs its own assertion, because every other check is written for things that do not.**
  Now asserted: inside the nav bar, an element that clips its own overflow must have room
  for the text it contains. **Hiding a word outright is fine and is what the ladder does
  when the bar is out of room; half a word is a lie** — a fragment reads as a name, not as
  a truncation, which is worse than showing less.

- **A DEGRADATION LADDER ON A GUESSED BREAKPOINT IS A GUESS ABOUT A WORD YOU HAVE NOT
  WRITTEN YET (2026-08-15).** The nav gave everything up at 380px, so above that line
  nothing could give up anything and the bar took what it needed out of the trade name.
  A breakpoint cannot know the answer here: the deficit depends on the WORD ("AV" is 24px,
  "Low-Voltage" 111px), on whether the page carries the favourite star, and on the NEXT
  trade's name, which does not exist when the breakpoint is written. `creative/trade.js`
  reasoned in prose that *"'Electrical' (ten) is the measured worst case and fits"* — a
  claim the live page contradicted on all eleven kits. **The rule: when what fits depends
  on DATA the CSS cannot see, measure at runtime and let the ladder fall out of the
  measurement.** Two forced layout reads on a nav bar, before the first paint, then a
  ResizeObserver on the BAR rather than the window — because the OS text size going up
  changes the answer without the window ever resizing. Result: 0 of 88 states cut, 77 of 88
  now render the full word where 17 did, and the eleven that still hide it are the ones
  genuinely out of room. **And observe the element with `box: "border-box"`**: the classes
  the ladder sets change gap and side padding, so a content-box observer re-enters itself
  forever.

- **A ROADMAP IS NOT A RECORD — THE RANKED LIST SENT A CYCLE TO BUILD SOMETHING THAT HAD
  SHIPPED FOUR DAYS EARLIER (2026-08-15).** The private roster's INTERFACE ladder still
  ranked *THE THIRD MESSAGE* as "now the interesting one", with a full design brief and a
  named trap. It had shipped on 2026-08-11 as `shared/reconcile.js` — 38KB, loaded on nine
  `rough-in-request.html` pages, implementing every constraint the entry specified. The
  build was avoided by one line of the ship loop (*confirm the thing is not ALREADY SHIPPED
  before you build it*) and by nothing else; the roster, the book and the cycle log all
  still read as though it were owed. **The rule: whoever ships a rung strikes it in the
  ranked list IN THE SAME CYCLE.** A list that ranks what is unbuilt is asserting that
  everything on it is unbuilt, and a stale entry is not a missing update — it is a false
  statement that the next cycle acts on. The same pass found rung 1 half-struck: the
  supply-house edge was marked shipped, but what actually shipped answered a different
  question than the entry predicted, and nobody wrote down which half was still owed.
  **Corollary: strike it with what you LEARNED, not just a checkmark** — "shipped, and NOT
  as this entry predicted, and here is what is still owed" is the only form of the update
  that is worth reading a month later.

- **A HEADING THAT SAYS "ONE" ABOVE A LIST OF THREE, IN THE PART THAT SHIPS (2026-08-15).**
  `shared/docspec.js` pluralises the PROSE heading over the omitted lines — "THE LINES
  EVERYONE LEAVES OUT — NEVER DROP THEM" — and does not pluralise `LOCKED[0].h`, the
  heading inside the OUTPUT FORMAT block. So every multi-omit document in the library
  (framing's five, since the day arrays landed) has been emitting **"THE ONE NOBODY WRITES
  DOWN" followed by three bullets**, in the template that becomes the finished document
  somebody else reads. The instruction half was right and the product half was wrong, which
  is the worse half to get wrong. **The rule: when a string pluralises, find every place it
  is PRINTED, not every place it is computed** — the two headings live 60 lines apart and
  only one of them got the branch. Fixed at print time via `lockedHeading()`; `LOCKED[0].h`
  stays the canonical key because `isLocked()` and `S.off` both key off it. **Found by an
  adversarial reviewer cast on a DIFFERENT question, on a trade the cycle was not
  touching** — and then confirmed against the real page before a line was changed, because
  a reported defect that is only reasoned about is a rumour.

- **THE GATE THAT NEVER TAPPED (2026-08-15, second occurrence of the class).**
  `mobile-watertight.mjs` loaded every page and measured it **as it arrives**, and half of
  what these tools render only exists after a tap. That is how a fixed bar grew to a ninth
  of the glass on seven trades with every measurement green (§SCARS 2026-08-11), found by
  screenshotting production AFTER the ship. The class came back the moment a new control
  lived behind "Not in the list?". **The rule: a page loaded and left alone is not the page
  a man uses.** The gate now carries `REVEALS` — a named state, the pages it matches, and a
  snippet that gets there — re-loads per state (pass B leaves the root font bumped, and a
  state measured on top of that is measuring two things at once), and re-runs every
  measurement inside it. A page matching nothing costs exactly what it cost before. **Proved
  by negative control**, not by a green line: the reveal was deliberately pointed at a
  control that does not exist and the gate failed at all four widths.

- **THE MAX OF FIVE IS NOT THE MODE OF EIGHTY (2026-08-15).** The custom path's new omit
  ticks were first seeded THREE-per-family, reasoning that three is what the one trade
  author who wrote `omit` as a LIST chose, five times out of five. That is the MAX of the
  five documents that ship a list. The MODE of all eighty is **one**, 75 to 5 — and the
  doctrine, the file header and the shipped heading all say the word "ONE". **The rule:
  when you justify a default from the corpus, name which statistic you took and check it is
  the one the question asked for.** Seed reduced to one, the other four one tap away, and
  the reasoning is in the code beside the table. Also the standing bias: **whatever ships
  pre-ticked is what a man in a hurry keeps**, so a seeded default biases DOWN.

- **A MODE BUTTON WITH NOTHING BEHIND IT IS WORSE THAN NO BUTTON, BECAUSE HE TAPS IT
  (2026-08-14).** `plumbing/supply-house-order.html` shipped a two-state segment —
  **Will-call / Delivery** — for four months. Tapping Delivery changed one word of the
  message and collected **nothing**: no gate, no set location, no time window, no how it
  comes off the truck, no who's meeting it, no who signs. A man tapped it, read a message
  that said *Delivery* at the top, and sent it — and the seven answers that decide whether
  the truck comes back loaded were still a phone call at 6am, which is the call the page
  exists to prevent. The supply-house counter lens found it independently and said it
  best: *"a bare Delivery button with nothing behind it is worse than no button, because
  he taps it."* This is the roofing-commons scar with a truck attached — **a chip with
  nothing behind it is a lie told to one trade; a MODE with nothing behind it is a lie
  told to one man on one morning.** THE RULE: a control that changes the DOCUMENT must
  change the QUESTIONS. If tapping it does not add a field, remove it and print the word
  in prose. And its half-brother, from the same page: the callback cell. Four months of
  *"Ordered by: your name"* with no number on it, while all three engine-driven siblings
  asked for **name + cell** — so the one document built to stop a phone call made the
  counter go find the phone number, and the answer came back office → PM → him.
  **A BACKPORT SWEEP IS NOT OPTIONAL BECAUSE NOBODY FILES A WISH FOR "MY SIBLING PAGE IS
  BETTER THAN ME."**

- **A HAND-KEPT LIST THAT HAS TO AGREE WITH A HAND-WRITTEN FUNCTION WILL STOP AGREEING
  (2026-08-14).** Shape #1's engine took a `watch: [...]` array of the header ids to
  re-render on. The document was built by a separate hand-written `document()`. Nothing
  checked that the two named the same fields, and on **four of the five** engine-driven
  order pages they had drifted: a charge code, a hot flag and a delivery method were read
  into the sent text and missing from `watch`. The block on the glass under *"what you
  send"* — the one thing he proofreads — was a generation stale, while the copied text was
  right. Six pages, ten fields, invisible to every review because the OUTPUT was correct.
  THE RULE: **never make correctness depend on two hand-kept lists agreeing.** The fix was
  not to top up the array on four pages, it was to stop the array being the only source —
  the engine now binds every header control the house convention already names, and
  `watch` is for the exceptions. `input` AND `change`, which `shared/draft.js` had already
  written down three files away and the engine had half of. Asserted by
  `tools/toolkit-gates/order-live-header.mjs`, which decides whether a field is in the
  document by **changing it and reading what the real Copy button puts on the clipboard**
  — so it needs no list of its own and cannot drift either.

- **A LATENT OVERFLOW DOES NOT APPEAR, IT BECOMES VISIBLE (2026-08-14).** The plumbing
  order page's *Need by* segment — three buttons — has always had a min-content floor of
  about 200px against a 160px grid track. It passed the mobile gate at every width for
  months **because it happened to land in the LEFT column**, where 40px of overflow still
  fell inside the glass. Adding two header fields above it moved the same cell into the
  RIGHT column and the same 40px went off the screen. Nothing about the segment changed.
  THE RULE: when the mobile gate fails on a page you touched, **find out whether you built
  it or exposed it** — the fix for the second is at the thing that never fit, not at the
  edit that revealed it. A control that cannot fit a track does not get a track (`span2`).

- **A GUARD WRITTEN TO THE LETTER OF THE LAST SCAR IS SATISFIED BY THE NEXT ACCIDENT
  (2026-08-13).** Framing shipped 2026-08-09 with no commons chip at all; the cycle that
  found it wrote a gate — *"every trade chip lands on real content"* — and the gate asked
  `toBeGreaterThan(0)`. Roofing then shipped 2026-08-12 **with** a chip and **zero rows**,
  and four days later an unrelated commit widened three universal rows to the eight
  construction trades and swept roofing in. Three. Greater than zero. Green. The deploy
  agreed, because it counted the file (`n_gear >= 20`) and a file-wide total is not
  coverage. So a roofer tapped his own chip and was told his trade's gear is a cordless
  drill, a torpedo level and a non-contact voltage tester — **not one row in the entire
  commons had ever been written for him.** THE RULE: a gate must assert the THING, not the
  symptom the last defect happened to show. "Has rows" was the symptom; **"has rows somebody
  wrote for it"** is the thing, and it is measurable — a row written for a trade is tagged
  NARROWLY, a row a trade was swept into carries the whole board. Every honest trade carries
  7–22 such rows; roofing carried 0 on both surfaces. Corollary, and it is the expensive
  half: **a launch checklist that does not name a shared surface will not update it.**
  §TRADE EXPANSION listed the directory, the runtime, the well, the roster, the ledger and
  the Pages assertion, and never once said "and the commons" — so two trades in a row
  joined the program without joining it. Fixed in both places: the checklist names it, and
  the deploy refuses a chip with fewer than six rows written for it.

- **THE FILTER YOU ARE LOOKING THROUGH IS NOT THE PROVENANCE OF WHAT YOU PICKED
  (2026-08-13).** `commons/commons.js` rendered the floor plus your open chip, but the
  document stamped **that chip** on every pick you were carrying. Tick three rows under
  Electrical, tap Plumbing, and Copy produced `WHAT'S IN THE BAG — PLUMBING` over glow rods,
  lineman's pliers and wire strippers — the page telling somebody an electrician's tools
  were a plumber's. Two more defects lived in the same state: the picks stopped rendering
  but kept COUNTING, so the dock read "3 in your bag" over a screen with nothing ticked, and
  there was **no way to reach them to take them back out.** THE RULE: **one partition
  function, read by both the screen and the document** — they had two, and two will always
  drift. A label may only claim what the rows themselves carry: the trade name goes in the
  title only when a row in the list is actually that trade's, and anything outside the
  current view rides in its own named section, on screen and in the text. And the state was
  invisible to every gate we own, because `mobile-watertight` loads pages fresh and
  `commons-mobile` never leaves the chip it ticked on — **a gate that only ever grades the
  empty bag is grading a page nobody has.** `tools/toolkit-gates/commons-bag.mjs` now drives
  it: 18/18 fail against the shipped engine, 18/18 pass against the fix.

- **`.sub` ON A STRING IS NOT `undefined` — IT IS `String.prototype.sub`, AND IT IS TRUTHY
  (2026-08-13).** `shared/note.js` `buildTicks()` reads `var name = typeof it === "string" ?
  it : it.name` — the line is proof the engine means to accept a plain string — and then
  `var sub = (it && it.sub) || ""`. On a string primitive `.sub` resolves to the legacy
  `<sub>` wrapper method: truthy, and it stringifies to `function sub() { [native code] }`.
  For eight trades every caller happened to pass `{name, sub}` objects, so the string branch
  the engine advertises had never once been walked. Trade #9 walked it and the literal text
  **`(function sub() { [native code] })` rendered beside every option on the page and inside
  the message a client receives** — no error, no warning, and it survived `node --check`, a
  registry assertion and a full local deploy simulation, because none of those look at
  pixels. Two rules: **ask for the object before you ask for the property**
  (`typeof it === "object" && it.sub`), and **a branch no caller has ever taken is
  untested code no matter how long it has shipped** — the first trade to use a supported-but-
  unused input shape is the one that finds out. Only a browser found this. Fixed in the
  engine (render AND copy paths) so it cannot bite trade #10, and the data was moved to the
  house `{name, sub}` shape as well.
- **A PASTED SUBJECT LINE ANSWERED ITSELF AS A NOTE (2026-08-13).** `answer-back`'s intake
  drops line 1 as a subject only when the paste ALSO has a `Job:`/`To:` header — `hasHead`
  is the signal "this is one of OUR documents". Eight trades paste a document this program
  generated, so it always fired. Trade #9 pastes the CLIENT's own email, which has a subject
  and no header, so it never fired and *"Northgate — round 2 notes"* became an answerable
  row that shipped inside the reply the client reads. The fix is a trade saying which kind of
  message its intake is (`TOOLKIT_ANSWER.firstLineIsSubject`, default off), not a smarter
  guess. **The rule: an intake's assumptions about its input are a per-trade fact, not a
  universal one** — and check them the first time a trade's counterpart is somebody outside
  this program.
- **A SERVED SURFACE WITH NO `trade.js` READS AS UNSERVED DEMAND (2026-08-13).**
  `av_wishing_well.py --stats` derives the served-trade list from `<dir>/trade.js` on disk
  and prints *"wishes exist for trade(s) with NO toolkit on disk: collage — that is the
  §TRADE EXPANSION trigger"* every single cycle. **Collage is served** — it is the Vite app
  deployed at `/collage/`, and its 16 wishes are all shipped. It has no `trade.js` because it
  is not a field-toolkit trade, exactly like the commons. Acting on that banner would create
  a `collage/` trade dir that COLLIDES with the deployed app's path and 404s the editor.
  The rule: `trade.js` is the marker for *is this a FIELD TOOLKIT trade*, never for *is this
  surface served*. Read the banner as "a non-toolkit surface has wishes", which is normal.
- **TWO NAMES FOR ONE TOOL, SEPARATED BY AN APOSTROPHE (2026-08-13).** The storefront join
  matches a tool by NAME between the lane's `tools.js` and persona500's `fieldToolkits.ts`.
  Trade #9 shipped "That’s Another Round" with a typographic apostrophe in the registry and
  a straight one in the storefront, and the join reported the same tool as BOTH missing from
  the storefront and advertised-but-not-shipped. Nothing rendered wrong, and neither file
  looked wrong on its own. `check_field_toolkit_drift.ts` caught it in seconds — **run it
  every cycle that touches either file**, and copy tool names between the two by paste, never
  by retyping.

- **THE HARNESS CANNOT SEE WHAT ITS ENGINE DOES NOT DO (2026-08-10).** Headless
  Chromium has no collapsing URL bar, so in it `100vh === window.innerHeight`.
  iOS Safari freezes `vh` to the LARGE viewport while the glass shrinks by ~130px,
  and the Tools menu's `calc(100vh - 72px)` therefore built a menu taller than the
  screen and told the scroller it fit — cut off on EVERY page of EVERY trade, for
  as long as that line existed, with every mobile gate we own green the whole
  time. A viewport-unit bug is structurally invisible to a harness whose viewport
  has no browser chrome. RULE: to test a mobile-viewport condition you must
  SIMULATE the discrepancy the device actually has — run at the large viewport and
  override `innerHeight` to the real glass — and a green desktop run is not
  evidence about a phone. Sibling of "A CLIP IS NOT A SPILL": both are the gate
  measuring something adjacent to the thing that is broken.
- **A SIMULATION IS ONLY FAITHFUL FOR WHAT IT MODELS (2026-08-10).** The same
  `innerHeight` override that correctly exposes a `vh`-bound box LIES about a box
  bound by `position:fixed; inset:0`, because iOS shrinks the layout viewport with
  the toolbars but not `vh`. Run that way, the wishing well reported its send
  button "18.8px below the glass — UNREACHABLE"; tested the way it is actually
  bound, it is clear by 111.2px. One more cycle of trusting the harness and the
  demand funnel would have been "fixed" for a bug it never had. RULE: every case
  in a viewport gate declares how the box is BOUND and is tested that way, and a
  finding from a simulation is a hypothesis until the model is checked against the
  thing it claims to imitate.
- **GEOMETRIC OVERLAP IS NOT OCCLUSION — HIT-TEST BEFORE YOU RESERVE (2026-08-10).**
  Chasing the same bug, the first diagnosis was that consumables' 115px fixed
  action dock buried 95.4px of the open menu; the geometry said so on three pages.
  A screenshot said otherwise, and `elementFromPoint` confirmed it: the bar is
  z-index 40, every page dock measured 20-30, and the menu paints over all of
  them. Reserving space for the dock would have SHORTENED the menu on every tool
  page to dodge a collision that does not happen. RULE: before subtracting an
  obstruction, hit-test whether it is actually on top — and look at the render,
  because a rect intersection cannot see paint order.

- **A CLIP IS NOT A SPILL, and only one of them had a gate (2026-08-09).** Every
  mobile assertion this program owns looks for content sticking OUT — horizontal
  overflow, an element past the right edge, a tap target under 44px. Nothing was
  watching for content quietly cut OFF. The nav brand — the only thing on the bar
  that says which kit you are in — was hard-cut mid-word on FOUR of seven trades
  for their entire lives (/plumbing/ −13px, /electrical/ −28px, /low-voltage/
  −42px, /framing/ −92px, rendering as the two letters "FR"), and every gate was
  green the whole time. Found by putting eyes on the live page after the tests
  passed. **The rule: when a container has `overflow:hidden`, something must
  assert what it is hiding.** A fragment with no ellipsis reads as a name, not as
  a truncation, which is worse than showing nothing.

- **A HARDCODED COUNT IS A CHORE, NOT A GATE (2026-08-09).** kit-switcher.spec
  asserted `toBe(6)` and `toBe(5)` for the chips on a hub and in the nav. Trade #7
  turned **35 tests red on nothing but two integers**, on a change whose entire
  premise is that a new trade is one line in one array. A gate that has to be
  hand-edited every time the thing it counts grows will eventually be edited
  carelessly or switched off. Derive the expectation from the same source the
  code reads.

- **MEASURE THE TAP TARGET, NOT THE ELEMENT (2026-08-09).** A checkbox is 20px on
  every browser there is and cannot be grown without breaking its own rendering —
  but clicking its wrapping `<label>` toggles it, so the LABEL is the target. A
  new gate that measured the input reported 17 failures on framing, 14 on
  plumbing and 8 on electrical for controls that all clear 44px comfortably. A
  gate that cries wolf on three shipped trades gets switched off, which is worse
  than not having it.

- **BUILT, TESTED, AND IMPORTED BY NOTHING (2026-08-04).** `collage-studio/src/lib/exportLimits.ts`
  was 1,490 lines of exactly the right machinery — canvas-ceiling probe, one-pixel
  surface sentinel, blob validation, a tier ladder — with a 57-case self-test that
  passed, and a comment predicting the precise bug: *"drop this check and the
  black-JPEG bug returns unfixed on exactly the owner's platform."* `App.tsx`
  imported none of it. The owner then reported that exact bug. A module that is
  written, tested and unreferenced is not a fix; it is a fix-shaped file, and its
  green test suite makes it *look* handled on every future audit. **Rule:** a
  defensive module ships only with a call site. Before closing a defect, grep for
  an import of the thing you wrote — a passing unit test proves the logic, never
  the wiring. The one artifact-level assertion that would have caught it (read the
  exported PIXELS, not the fact an image appeared) is now `tests/e2e/export-integrity.spec.ts`.
- **A SWEEP THAT STOPS AT THE SURFACE IT COULD SEE (2026-08-04).** The previous
  cycle swept all six trades for 44px tap targets and fixed the hub cards' 28px
  favourite ★ — then shipped, with every control *inside* the shared wishing well
  still under the line: 37px inputs, 39px selects, 31px identity buttons, an 18px
  "Cancel". Same law, same file, same six trades, one layer deeper, missed because
  the sweep looked at the pages and not at the modal the pages open. **Rule:** a
  cross-trade sweep covers every state a surface can be IN, not every surface —
  open the modals, expand the folds, switch the kinds, then measure. And note
  `shared/feedback.js` had held the 44px line correctly the whole time: when two
  files implement one standard and only one is right, the other is not "also fine",
  it is the backport you have not done yet.

- **A DEFAULT IS A CLAIM (2026-08-04).** A write-in line inherited a real default on every
  axis, so a tech's hand-typed "USB-C 90° elbow, 1 ft" reached the counter as
  "USB-C 90° elbow, 1 ft, **3 ft** · **Finish cable — molded, low-profile shell**" — a line
  contradicting itself, carrying two attributes nobody picked. On a page whose whole
  promise is "everything here is what YOU picked", a pre-selected option is the tool
  putting words in the tech's mouth. **Rule:** any axis on a user-authored row leads with a
  neutral option, and the document drops every unpicked value. Never let a select's first
  option become an assertion.
- **CLEAR MUST ACTUALLY CLEAR (2026-08-04).** The engine's `clearAll()` called
  `localStorage.removeItem()` — and 250 ms later the debounced re-persist wrote the record
  straight back, because the caller's `persistExtra()` always returned an object and the
  engine only drops the record when there is genuinely nothing to save. **Rule:** a
  persisting caller returns `null` when its state is untouched, and any "clear" is verified
  by reading storage AFTER the debounce window, not by watching the screen go blank.
- **A BARE ISO DATE IS A CALENDAR DAY, NOT AN INSTANT (2026-08-04).** `new Date("2026-08-04")`
  parses as UTC midnight, so `credits.html` rendered every entry a day EARLY for anyone west
  of UTC — on the permanent public credit ledger, on its very first entry. **Rule:** split
  `YYYY-MM-DD` and build a local date. This bug hides until the data is non-empty; assume
  every date formatter has it until proven otherwise.
- **UNSHIPPED IS UNDELIVERED (2026-08-04).** A prior cycle wrote this tool — page, data and
  the extracted engine, all good work — and closed without committing. It was invisible to
  the well (the wish still read `new`), to git, and to the site. **Rule:** the cycle is not
  the build, it is the ship; claim the wish BEFORE building so the queue shows the work
  exists, and never close with the deliverable sitting in the working tree.
- **DIFF THE SERVED BYTES, NOT THE DISK FILE (2026-08-04).** After a data fix the page still
  showed the old behaviour; the disk file was correct and the browser had served a cached
  module. Two more minutes of re-reasoning and the correct fix would have been "reverted" as
  not working. **Rule:** when a verified fix appears not to land, fetch what the server
  actually served and compare it — before touching the code again.

- **A SHARED RUNTIME LINKS PAGES THE NEW TRADE DOES NOT HAVE (2026-08-04).** `buildBar()`
  unconditionally adds a "★ Wall of Wishes → credits.html" entry to the nav dropdown of
  EVERY page of EVERY trade. Plumbing shipped without `credits.html`, so for the whole life
  of the trade every plumbing user who opened the menu got a 404 — measured live:
  `/plumbing/credits.html` 404 while `/av/credits.html` 200. **Rule:** when the shared
  runtime references a per-trade page, that page joins the list every trade must carry, and
  the deploy asserts it. A capability added to the runtime is a debt owed by every trade.
- **STAGED IS NOT REGISTERED (2026-08-04).** `UIComponents.tsx` states in its own header
  that a staged directory and a TOOLS entry are *both* required — and only one direction was
  ever checked. `plumbing/` was staged by the workflow from the day it shipped but never
  added to the site-root registry, so the ONLY route to trade #2 anywhere on the site was a
  hand-wired link inside `av/index.html`. Verified against the DEPLOYED bundle, not the
  source: `./av/` 1 hit, `./plumbing/` 0 hits. **Rule:** an invariant stated in a comment is
  not enforced; assert BOTH directions in the deploy, against the built artifact.
- **THE NAV OVERFLOWED EVERY PHONE, ON EVERY PAGE (2026-08-04).** The sticky bar is a flex
  row holding two items that cannot shrink — the brand and the 158px "Wish for a tool" CTA,
  both `white-space:nowrap`. Measured in a real browser at a 390px viewport: bar content
  433px on `/av/`, 487px on `/av/consumables.html`, 489px on `/plumbing/` — so every page of
  every trade scrolled sideways on every phone, on the one surface whose whole promise is
  "usable one-handed at a job site". It survived because nobody had ever asserted it.
  **Rule:** the pre-ship mobile gate is mechanical and it runs at 320/360/390/430 — no page
  ships until `scrollWidth <= clientWidth` at all four. Priority when the bar cannot fit:
  the CTA never shrinks, the brand gives up its tail, then its word, keeping the icon.
- **DO NOT MASK AN OVERFLOW YOU COULD FIX (2026-08-04).** The first cut of the new Wall of
  Wishes carried `html,body{overflow-x:hidden}`. With it, `documentElement.scrollWidth` read
  a clean 390 while `body.scrollWidth` was 489 — the page measured perfect and was broken,
  and the gate above would have been blinded on exactly the defect it exists to catch.
  **Rule:** never `overflow-x:hidden` a layout bug; measure BOTH `documentElement` and
  `body`, and fix the cause.
- **HALF A TRADE'S VOCABULARY IS SOMEBODY'S TRADEMARK (2026-08-04).** Standing up electrical
  ran a safety audit over the item words, and it found four genericized marks already LIVE
  in `av/consumables.html` — wire nuts, Tek screws, Tapcons, zip ties — plus a bare brand
  used as a product label. The in-trade reviewer flagged the same words independently, in
  his own list, unprompted: *"everybody says it out loud; you can't print it."* Electrical
  is the worst offender of any trade (Romex, BX, Greenfield, Sealtite, Unistrut, Condulet,
  Wiremold, Minerallac, Caddy, Cadweld, Panduit, Tapcon, Sawzall, Noalox…), but no trade is
  clean. **Rule:** every trade's vocabulary data gets a generic-substitution pass before it
  ships, and "everybody says it" is the reason to CHECK a word, never the reason to print
  it. Twist-on wire connectors · cable ties · self-drilling screws · concrete screws ·
  anti-shorts · wedge anchors · strut · flex · conduit body · recip blades.
- **A HARDCODED FALLBACK RESURRECTS THE VALUE YOU JUST REMOVED (2026-08-04).** A pasted
  write-in line is supposed to arrive with an EMPTY quantity, because its own text already
  says "500' #12 THHN blue". The render honoured that — and `readLine()` then coerced the
  empty box back to `"1"` at the read site, so the document printed `1  500' #12 THHN blue`,
  a line arguing with itself. Fixing the render path was not enough: RESTORE built its own
  row definition and reintroduced the same "1" the moment the tech reopened the page.
  **Rule:** a fallback lives with the default it is defaulting to (stamp it on the row),
  never hardcoded where the value is read — and when you change how a row is built, walk
  ALL THREE constructors: render, clone, restore.
- **A LABEL IS ADDRESSED TO SOMEBODY (2026-08-04).** The write-in section is headed "What do
  you need?" — right on screen, where it is a question to the man holding the phone. It was
  also printing as a section heading inside the message he sends the warehouse, where it
  asks a question of someone who was never asked anything. **Rule:** when a label is a
  PROMPT, it needs a separate document name; the screen and the sent document have different
  readers and only one of them is being spoken to.
- **NEVER `nowrap` A STRING YOU DIDN'T AUTHOR (2026-08-04).** The hub's audience chip was
  `white-space:nowrap`, and its text comes from a `tools.js` registry entry someone edits
  later. "Electricians → Warehouse / Counter" pushed `/electrical/` to 328px in a 320px
  viewport — the whole new hub scrolling sideways on an iPhone SE, caused by a string in a
  data file. **Rule:** any text whose length is set by data must be allowed to wrap. The
  fix belongs in every trade's hub the same cycle, not just the one that surfaced it.
- **THE TRADE ACCENT IS PAINTED ON A DARK BAR (2026-08-04).** A trade's `accent` is not just
  a brand colour: the shared runtime paints it onto the dark steel nav (brand tail, the
  favourite ★, focus rings, the bar's bottom rule) AND uses it as a button fill carrying
  `accentInk` as text. A deep navy — the obvious "electrical" choice — would have made the
  nav unreadable on every page of the trade. The same audit found two places still assuming
  AV yellow: the nav dropdown's hover painted the accent under a hardcoded near-black, and
  the wish CTA's hover was a hardcoded lighter yellow for EVERY trade. **Rule:** a trade
  accent must be light and high-chroma enough to read on `#242A31`, text on the accent uses
  `accentInk` and never a literal, and a hover lifts the accent with a filter rather than
  naming a second colour.
- **THE CAMERA ROUND-TRIP EATS THE DRAFT (2026-08-04).** A page whose FIRST block is "shoot
  these now" has, on every single job, a first interaction of *tick, then leave for the camera*
  — and iOS backgrounds the browser the instant the camera opens, which can freeze a debounced
  save before it ever writes. A 250 ms debounce is not a save. **Rule:** any page that persists a
  draft flushes synchronously on `visibilitychange`, `pagehide` and `blur`, not only on a timer.
  A man who retypes a data plate once does not open the page again.
- **A PHONE DESTROYS AN IDENTIFIER (2026-08-04).** Model numbers, serials and part numbers are
  the exact strings autocorrect and autocapitalize are worst at, and the suffix IS the part — a
  family name is a phone call and a restock fee. **Rule:** every identifier field ships
  `autocapitalize="characters" autocorrect="off" spellcheck="false" autocomplete="off"`, and
  nothing normalises on the way out: never collapse internal spaces, strip dashes or slashes, or
  re-case what he typed. Watching a phone turn a model number into an English word is the moment
  a man closes a form for good.
- **A PLACEHOLDER IS THE BACK DOOR FOR CERTIFIED DATA (2026-08-04).** On a readings field, the
  seeded example `SC 3 (should be 10-12)` is a charging chart shipped as helper text — the
  single sneakiest surface on a page that bans certified data everywhere else. **Rule:** every
  example value in a placeholder shows something the tech MEASURED, never a normal, a range, a
  target or a "should be". The same rule killed an early draft that read `amps 41 vs 28.4 RLA`:
  the word *vs* is a comparison the page made, so it ships as `amps 41, plate RLA 28.4`.
- **A COLUMN LOOKS TIDY IN THE PREVIEW AND ARRIVES AS MUSH (2026-08-04).** A padded label column
  renders perfectly in the monospace preview box and turns ragged the instant it lands in the
  only place the document ever goes — a text message or an email, in a proportional font.
  **Rule:** documents use `Label: value` and ALL-CAPS section headings on their own line, which
  are the only formatting that survives an unknown font. Judge output in the medium it is pasted
  into, never in the preview that renders it.
- **THE FIRST LINE IS AN INBOX SEARCH KEY (2026-08-04).** A turnover gets approved six months
  after it is sent, and the estimator finds it by searching his mail for "Kroger 412" or "RTU-4".
  A document whose first line is its own title is unfindable. **Rule:** the site and the unit tag
  land in the first two lines — and that line has to DEGRADE, never emitting a bare " — — " when
  only one of them was filled.
- **NOT A SCAR — A CEILING TO REMEMBER (2026-08-04).** The electrical panel's synthesis
  argued that no axis may exceed **6 options**, because at 7 an inline chip row wraps, the
  control degrades to an iOS wheel, and ticking stops beating typing. It is right about chip
  rows and it does not apply to what shipped: shape #1's axes are native `<select>`s, which
  are the same one-tap-then-scroll interaction at 6 options or 11, so the ladders kept their
  real sizes (2-1/2 through 4 in pipe, 250–500 MCM lugs) instead of exiling them to the
  write-in. **Rule for whoever changes that control:** the moment an axis is rendered as
  chips or segments instead of a select, the 6-option ceiling becomes binding and the long
  ladders have to move or split.


- **A HARDCODED LITERAL IN THE SOURCE IS NOT WHAT THE PAGE RENDERS (2026-08-04).** Standing up
  trade #6 "found" a cross-trade bug: `credits.html` is byte-identical in every trade and its
  stylesheet hardcodes `--flag:#F0BE1E`, AV yellow — so on the face of it every non-AV Wall of
  Wishes rendered in the wrong trade's colour. Five files, one md5, one literal: the evidence
  looked airtight, and a full sweep-and-fix across six trades was already written and applied.
  It was WRONG. `shared/toolkit.js` injects `:root{--flag: TRADE.accent}` at runtime, and the
  live low-voltage page measured `--flag: #FF9E80` with the eyebrow, the empty-state button and
  the footer rule all painted coral. The whole fix was reverted. **Rule:** a CSS literal is a
  fallback, not a rendering — before claiming a style bug, read the COMPUTED value off the live
  page. This is the served-bytes scar pointed at the other end: there, disk was right and the
  browser was stale; here, disk was misleading and only the browser knew. Either way the
  artifact is the witness, and a sweep across six trades is exactly the size of mistake worth
  spending two minutes to not make.
- **NEVER HANG A STATE CHANGE OFF A SUCCESS BRANCH YOU KNOW CAN FAIL (2026-08-04).** The
  weather day's multi-day carry-forward — the single biggest gap the field panel named, the
  thing that makes day two and day three of a front get papered at all — stashed the finished
  note inside the clipboard `.then()`. Measured in a real browser: the clipboard promise
  rejects whenever the document is not focused, the `execCommand` fallback then fails too, and
  the stash never ran. So the feature died silently in exactly the environments the fallback
  exists for — a trailer on http, an in-app browser, an older phone. **Rule:** the user's PRESS
  is the intent; the capability's success is a separate question. Commit the state change on
  the gesture, and let the copy path only report whether it copied.
- **A FLEX ITEM WITH NO FLOOR BECOMES A COLUMN OF LETTERS (2026-08-04).** The fixed action bar
  held a status line plus two `white-space:nowrap` buttons. At 320px the buttons measured 283px
  inside a 292px content box, so the status line was handed a flex width of ZERO — and wrapped
  into a 92px vertical ribbon one character wide, inflating the bar to 112px and eating a third
  of the smallest phone's screen. The overflow gate passed the whole time: nothing overflowed
  horizontally, it just collapsed vertically. **Rule:** the mobile gate measures HEIGHT too. Any
  text sharing a row with `nowrap` siblings ships `white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis` so it can never be taller than one line, AND gets its own row below
  the breakpoint where the row stops fitting — two guards, because a media query alone leaves
  the ribbon one font-size away from returning. First fix made it WORSE (141px: the buttons
  wrapped onto separate rows), which is the tell that a wrapping bar needs a decided layout, not
  a nudge.
- **THE GATE ONLY GUARDS THE REPO IT LIVES IN (2026-08-04).** The toolkit repo's deploy asserts
  a trade is staged, registered, linked and that every registry href resolves — in both
  directions, on the built artifact. None of that can see the STOREFRONT, which lives in another
  repo. Low-voltage shipped 2026-08-04, went live at its own URL, and never got its entry in
  `persona500/src/data/fieldToolkits.ts` — so for its whole first day it was simultaneously live
  and advertised as "coming soon" in `NEXT_TRADES`, two lists disagreeing about the same trade.
  That is precisely the staged-but-unregistered failure the deploy gate was built to stop,
  reappearing one repo over where the gate has no reach. **Rule:** the manifest entry is part of
  the ship, not a follow-up — and when a list can empty out, its render sites degrade (an empty
  bench must not print "the 0 trades on the bench", and a "researched and queued:" heading must
  not stand over nothing).



### 2026-08-05 — A RESOLVING HREF DOES NOT MEAN A WORKING PAGE
The deploy asserted that every `tools.js` registry href resolved in the artifact. That
proves the page EXISTS. It does not prove the page WORKS. Shape #2's engine made six tool
pages depend on files in a *different* staged directory (`shared/note.js`,
`shared/note.css`), and a page whose engine 404s still returns 200 and still renders its
header — it looks alive in a curl and is a blank white card in a foreman's hand. Same
class as the staged-but-unregistered scar, one level down. **Rule:** the deploy now walks
every registry page's own `src=`/`href=` assets and fails if one is missing from the
artifact, is off-site, or is origin-absolute.

### 2026-08-05 — A docPrefix THAT ASSUMES ITS NEIGHBOUR
A crew row printed `× 1.5 hrs` — a multiplication sign with nothing on the left of it —
because the hours column carried `docPrefix: "× "` and the men column beside it was
blank. Half the columns on a row are blank half the time. **Rule:** every column of a
repeatable row must read on its own; a prefix or suffix may describe only its OWN value,
never its relationship to a sibling column.

### 2026-08-05 — TWO LISTS UNDER ONE HEADING READ AS ONE LIST
The first live drive of the note engine printed two men and a length of cable as a single
six-line block under `WHAT IT TOOK`, and nothing marked where the crew stopped and the
material started. A heading-less section did the same thing at the end, gluing `From:` on
to the last material line so it read as another material line. **Rule:** a labelled list
inside a section gets a blank line before it, and a section with no heading still gets its
own air. Fixed in the engine, so it is fixed in all six trades and every future one.

### 2026-08-05 — "CLEAR STORAGE, THEN RELOAD" IS A CIRCULAR TEST
Verifying a fresh page by clearing `localStorage` and calling `location.reload()` proves
nothing: the reload fires `pagehide`, the engine's flush-on-the-way-out handler runs, and
it writes the still-populated form straight back into the key that was just deleted. The
draft that "leaked" was the engine correctly refusing to lose a man's work. **Rule:** to
test a fresh page, use the page's own Clear (which empties the DOM *and* the key), or
open a new document — never clear-then-reload, and never diagnose a persistence bug from
that shape of test.


### 2026-08-05 — THE FIRST RENDER HAPPENS BEFORE THE ENGINE HANDS THE PAGE BACK
`var rl = RowLog.mount({... docHead: function(){ ...rl.rows()... } })`. `mount()` renders
once before it returns, so `rl` is still `undefined` inside that first `docHead` — it
threw, the exception escaped `mount()`, and **the entire page script died at that line.**
What shipped looked fine: the engine had already built its bar and attached its own
listeners, so rows added, chips lit, the tally counted. Everything the PAGE owned was
dead — no document in the preview, no receiver buttons, no defaults, no listeners — and
nothing in the console pointed at the config that caused it. Driving the real page at
390px found it in one pass; a screenshot never would have. **Rule:** any caller hook the
engine invokes during `mount()` must survive its own handle not existing yet. The first
instance guards this (`rl ? rl.group() : "floor"`) and that guard is the reason, not a
style. Reach for the rows through one `rowsNow()` helper that returns `[]` until the
engine is back.

### 2026-08-05 — THE HEADING IS A VALUE, AND SOMEBODY ELSE READS IT
Grouping by a coded axis printed the CODE. A cross-boundary request headed `EC — 2 ROWS`
and `ROCK — 4 ROWS` went to a foreman at another company, and the first line he reads is
the one the tool invented. **Rule:** if a field's stored value is a slug, the config owes
a `groupName` for it. Storing codes is right; showing them never is.

### 2026-08-05 — A SHARED BLOCK LEAKS ACROSS THE SCOPE THE DOCUMENT PROMISED
"Send to the electrician" filtered the rows and left the FLAGGED block drawing from every
row on the list — so the EC's message ended with the GC's blocking item on it. The block
was written when a row log had exactly one receiver, and it stayed correct until the day
a document had a scope. **Rule:** when you add a scope to a document, every section of
that document is in scope until you prove otherwise. Grep for the ones that read from the
whole collection rather than from what you just filtered.

### 2026-08-05 — A GATED FIELD THAT ONLY HALF REPAINTED
The engine repainted `chips` options when a gating select changed, but not `learn` ones —
so the ask-gated size picker stayed frozen on the previous pick's list and would have
attached a back-box spec to a conduit line. It was invisible until an ask actually gated a
learn field. **Rule:** when a mechanism applies to a family of field kinds, enumerate the
family, not the one you happen to be using.

### 2026-08-05 — 38px WAS UNDER THE BAR ON EVERY ROW-LOG CONTROL, IN THE SHIPPED PAGE
The first row-log page shipped chips at 38px and segmented buttons at 40px against a
stated 44px minimum, and it had been live and "verified" since. Nobody caught it because
the sweep that checked tap targets checked the tools that existed *then*. **Rule:** the
44px assertion belongs in the pre-ship drive of every page, not in a one-time audit — and
the reason it was cheap to fix this time is that there is now ONE stylesheet to fix it in.

### 2026-08-05 — A CONFIG VALUE CANNOT BE RECOVERED BY CUTTING A DIFFERENT CONFIG VALUE
Shape #4's engine needed the trade word for the line "we do ___ work" and derived it as
`TRADE.name` with `" Field Toolkit"` sliced off. It printed **"a AV outfit"** on five
trades (wrong article) and on the sixth it did not fire at all, because GC's name is "GC &
Site Super Toolkit" — the one trade whose name does not end in the string being stripped.
**Rule:** if the caller owns its words, it DECLARES the value. String surgery on a
neighbouring config field is a derivation that looks free and breaks on the first config
that does not match the pattern you had in your head.

### 2026-08-05 — TWO DIFFERENT THINGS UNDER ONE KEY, AND ONE OF THEM SHIPPED INTO A PROMPT
The library's `from`/`to` were written as ROW DESCRIPTIONS ("Whoever was on the call",
"Everyone who was there and everyone who was not") and then substituted as if they were
the user's ANSWERS. A production instruction block came out reading *"I am Whoever was on
the call at Bayline Integration"*. A field that reads fine in a list is not automatically
substitutable in a sentence. **Rule:** separate the descriptor from the value, or make the
descriptor terse enough to be both — and only the value the user actually tapped is ever
short enough for a header line.

### 2026-08-05 — THE ENGINE APPENDED A HEADING THE SPINE ALREADY HAD
Shape #4 appends two always-on sections after whatever spine a document declares. The
incident and verification family spines already ended in OPEN ITEMS, so every write-up in
those families shipped **OPEN ITEMS twice** — which reads to the receiver as two different
lists, the same class as the two-lists-under-one-heading scar above. The first fix was
worse: deduping first-wins kept the spine's copy in place and pushed **the omitted line
below it**, burying the one section the whole library exists to protect. **Rule:** when a
list is assembled from two sources, build it ONCE in a function both the UI and the
document use, and decide explicitly which source wins AND where it sits — dedupe order is
a content decision, not a detail.

### 2026-08-05 — THE ARM THAT WROTE THE LIBRARY IS NOT ALLOWED TO GRADE IT
43 documents came back from six working-pro passes, all plausible. A second, adversarial
pass — one 25-year skeptic per trade, told to default to dropping — **killed 27 of them**:
list-shaped things dressed as prose, second copies of documents the shared library already
carried, paperwork somebody else owns and numbers, and one outright certified-data leak (a
red-tag notice whose "WHY IT IS UNSAFE TO RUN" heading would have had an AI reaching for a
ppm number and a cause the tech never diagnosed). Not one of those was visible from
reading the first pass. **Rule:** persona proposes, generic disposes — and on this lane the
skeptic's kill list is the deliverable, not the loss. A section HEADING can violate
§SAFETY all by itself, before a single word of content exists.

### 2026-08-09 — THE SUMMARY COUNTED ROWS THE DOCUMENT DID NOT CONTAIN
`answer-back` heads its document with a rollup — *"4 lines — 1 will do · 1 in already · 1
can't · 1 need to know"* — and offers a **still owed** scope that drops the done and the
refused from the body. The rollup was built from `statusCounts()`, which counts EVERY row.
So the scoped copy went out reading *"1 in already · 1 can't"* directly above a list that
deliberately contained neither: a document that contradicts itself in its own first
paragraph, sent to another company, about commitments. Found by driving the real page and
reading what came out, not by reading the code — the code looks correct at both ends,
because each end is.
**Rule:** when a config has both a SCOPE and a SUMMARY, the summary is computed over the
scoped set, and the predicate that defines the scope is written ONCE and asked by both.
The first instance (`rough-in-request`) got away with it by SUPPRESSING its "still open"
line whenever a filter is active — a legitimate answer, and the reason the class did not
surface until a page wanted the rollup in both states. **Swept the same cycle:** all six
`rough-in-request` pages are filter-guarded, `device-checkout` declares no filters, so
`answer-back` was the only instance and it is fixed on all six.

### 2026-08-10 — THE FOCUS RING HANDED TAB A CONTROL THAT WAS NOT ON THE SCREEN
The walk's note field sits in the markup the whole time and only its wrapper carries
`hidden`, so the dialog's own focus trap — built from
`querySelectorAll("button:not([disabled]),input")` — put a `display:none` input in the ring.
`focus()` on a `display:none` element does not throw and does not move focus; it silently
does nothing, so Tab at that position leaves the active element on `<body>`, OUTSIDE a
dialog that advertises `aria-modal="true"`. That is the exact symptom of the 2026-08-06
scar, rebuilt one layer down by code written to satisfy it — and nothing on screen changes
when it happens, which is why it survives a look.
**Rule:** a focus ring is built from what is REACHABLE, never from what is PRESENT — filter
`el.closest("[hidden]")` out of it. And test it by ASSERTING `document.activeElement` after
N presses of Tab; a screenshot of a dialog cannot show you where focus went.

### 2026-08-10 — THE END CARD REPORTED THE LIST'S STATE AS IF IT WERE THE WALK
Found by an adversarial audit cast on the walk before it shipped, and confirmed by
measurement: four rows already `In`, tap **NOT YET four times**, and the end card reads
*"4 are in · 0 still open"* and offers no follow-up button. He walked the job saying **no**
to every row and the tool told him everything was in and handed him nothing to send. In the
mixed case it is worse: the *"what's still open"* message he then sends **omits the rows he
explicitly could not confirm**, because the scope predicate is `status !== "In"` and those
rows still said In. Root: `doneN` counted CURRENT STATUS across the walked ids, so it
reported the list, not the act — while the comment above it claimed it "says only what it
watched happen".
**Rule:** *a summary of an ACT is computed from the act, or the act must make the state
true.* Here the second is right and cheaper: a hold on a row that already carries the
settled rung now **retracts it one step down the declared ladder**, so the counts, the
document and the button all follow from one honest write. The "negative writes nothing"
principle survives intact for every row short of the settled rung — where it is still
exactly right.

### 2026-08-10 — THE PENCIL SHEET HOLDS A PHOTOGRAPH, AND SAVE PUTS IT BACK
Same audit, and this one is OLDER than the surface that exposed it. `commit()` does
`r.values = v` where `v` is read off the add/edit bar — a snapshot of the row taken when
the pencil opened. Repro, measured: open the pencil on row 1 · walk the list and mark it
IN · close · tap **Save** on the still-open editor → `status` is back to `""`. Field
verification destroyed, silently, with no warning. It is reachable from the tap ladder too
(advance to `Committed`, then Save, and it reverts), which is why it is written here as a
CLASS and not as a walk bug.
**Fixed for the walk:** `walkOpen` closes an open editor first — tapping "Walk it" is
leaving the edit, exactly as tapping anywhere else is. **STILL OWED, and named so the next
cycle can take it:** `commit()` should write only the fields that CHANGED in the bar since
the pencil opened, which fixes the tap-ladder instance too — and that change touches the
commit path of all 16 row-log pages, so it wants a gate across all of them, not a patch.

**PAID 2026-08-11** (`2a0948e0`). `startEditing` now snapshots the bar with `readBar()`
*after* `writeBar` — both sides of the diff read the same way, because a control that
normalises what it was handed has not made an edit — and `commit()` writes only the keys
whose bar value CHANGED. A field he never touched keeps whatever the row says NOW, and a
key that is not a bar field at all survives instead of being dropped, which the whole-object
assignment was also quietly doing. The gate the scar asked for is
`tools/toolkit-gates/rowlog-commit-merge` in shape — a repro that adds a row, opens the
pencil, advances the row underneath it, saves, and asserts the status survived: **16/16
row-log pages FAILED it before the change and 16/16 pass after**, re-run against the
deployed artifact on three trades. Worth keeping: the bug was found by an audit told to
REFUTE, and its fix was proved by running the old code back under the new test. A test
that passes on both is not evidence of anything.

### 2026-08-10 — A CLAIM THAT OUTLIVES THE THING IT CLAIMS
Three of one kind, all in the walk, all found by the same audit and all fixed before ship.
(a) The `keydown` listener was bound on the OVERLAY, so a tap on the row — the biggest
thing on the screen and deliberately not focusable — moved focus to `<body>` and the
Escape the page promises stopped working, while the dialog still advertised it. Bound on
`document` while open now. (b) The screen wake-lock was stored unconditionally when its
promise resolved, so closing the walk during that flight held the screen awake with no walk
on the glass and nothing left that could ever release it; and the *"screen held awake"* line
was never removed when the **UA** took the lock back on its own (tab hidden, screen asleep),
so the page kept claiming a capability it no longer had. (c) `focus()` on a control that has
since become `disabled` is a silent no-op, so a walk that settled every row in a "still
open" scope closed onto `<body>`.
**Rule:** every promise a surface makes — a key that works, a lock that is held, a place
focus lands — has to be re-checked at the moment it is CLAIMED, not at the moment it was
arranged. And each of the three is invisible to a screenshot, which is why the audit that
found them was told to REFUTE rather than to review.

### 2026-08-11 — MIN-HEIGHT WAS SET EVERYWHERE AND MIN-WIDTH NOWHERE
The operator's mobile bar has been standing since 2026-08-04 and says tap targets are at
least 44px. It lived in §MOBILE-WATERTIGHT as a rule, which is to say the twentieth page
forgot it. Written as an ASSERTION instead and pointed at every page on disk, it found
**41 of 52 LIVE pages failing**, and almost all of it one mistake: a control was given
`min-height:44px` and nothing at all on the other axis. **A tap target is judged on its
SHORTER side**, so height alone is half the measurement — and the narrow controls are the
ones tapped most, because the shortest labels are the settled answers ("In", "No", a bare
brand emoji). Three of the culprits were in SHARED files, so three edits swept 29 pages:
the nav brand (20.2px wide below 380px, where the word hides), the row-log status chip
(36.9px), and the write-up search clear (40×40, inset 2px inside a 48px field to look
tidy — the tidiness cost a tap target and bought nothing a thumb can feel).
**Two things worth keeping.** (a) Fixing only the breakpoint I had thought of — ≤380px —
still left **37 pages failing at 390px**, the width of the phone most of this trade is
holding, because the brand loses its TAIL at 560 and its WORD at 380 and between them it
is an icon and two letters. `min-width` belonged in the BASE rule, not in a media query
aimed at the case that occurred to me. (b) Widening the brand to a real 44px pushed the
sticky bar 4px past a 360px glass, and the fix was to make the wish button give up three
words below 380px — **something had to shrink and it was never going to be the thumb
target.** A gate that only measures is half a gate; it has to be run again after the fix,
because the fix is a layout change too.
**Rule:** every tap-target rule is about the SHORT SIDE, at EVERY width, and it belongs in
an assertion rather than a paragraph. `tools/toolkit-gates/mobile-watertight.mjs` derives
its page list from disk so a trade shipped next month is covered the day it lands. It is
also deliberately NOT maximal: inline links in prose are exempt (WCAG 2.5.8 exempts them
too) and text fields are reported rather than failed, because a gate that reports every
body-copy link is noise, and a noisy gate is one that stops being run.

### 2026-08-11 — A DATA FILE WROTE TO A SCHEMA THAT DOES NOT EXIST, AND THE PAGE WENT BLANK
`framing/docs.js` shipped five documents whose `omit` was a **list** where the engine
called `.split` on it. That is a `TypeError` inside `compose()`, which throws out of
`renderOut()` and out of `renderAll()`, so on the LIVE site every one of that trade's own
documents produced **an empty output block** — the one thing shape #4 exists to make. The
page did not look broken: the picked card rendered, the omitted line rendered (comma-joined,
because an array handed to `textContent` is), the tuner rendered. Only section 3 — the block
you paste into your AI — was blank, the bottom bar still read *"Pick a document to start"*,
and the library never collapsed, because the line that collapses it sits AFTER the line that
threw. Same file also set `family` to shared **document ids** (`handover`, `delay-notice`,
`change-request`), which `FAMILIES[f] || FAMILIES.recurring` swallowed whole — so a damage
letter read three years later was being written as a **delta against a previous one that
does not exist**, and the card called it *"a report you send on a rhythm"*.
**Why nothing caught it.** `node --check` passes: the file is valid JavaScript. The mobile
gate passes: the layout is watertight around an empty box. The deploy's asset asserts pass:
every dependency resolves. A screenshot passes: the page looks finished. **Every check we
had verified the container and none of them verified the contents.** A data file and its
engine have a contract, and this repo had written it down nowhere.
**The sweep found the same class twice more, and the second one is the instructive one.**
`low-voltage/inspection-deficiency-letter` was tagged `recurring` — a LEGAL family, so no
schema check could ever flag it — on a one-shot letter whose whole purpose is *"every device
you could not get to is yours until you name it in writing"*. Delta continuity tells the AI
to drop anything already reported: the second letter silently omits the devices named in the
first, and those devices are now his. `electrical/confirming-note` was tagged `minutes`,
which is **semantically correct** — it records a conversation and what got decided — but
minutes report deltas because a coordination meeting recurs, and a confirming note does not:
each one memorialises a DIFFERENT conversation. Re-familying it would have fixed the
behaviour by lying about what the document is, so the engine grew `standalone: true`
instead — the family keeps the label and the spine, the document keeps every fact every
time. The flag only ever moves TOWARD stand-alone; there is deliberately no way to force
delta on, because that is the direction that corrupts a record.
**Rule:** a fallback must fail in the SAFE direction. `FAMILIES[f] || FAMILIES.recurring`
chose the one fallback that turns an unknown into a document written as an update; the cost
of guessing stand-alone is a lost convenience, the cost of guessing recurring is a corrupted
record. And the contract is now asserted twice, in the two places that catch different
things: `tools/toolkit-gates/docspec-config.mjs` DRIVES every document in every trade
through the real page (113 checks — it fires on the pre-fix state with all three diagnoses:
the page error, the illegal family, and the omitted lines that never reached the block), and
the deploy asserts the schema statically over the staged artifact, parsing FAMILIES out of
the shipped engine rather than keeping a copy. Both discover trades from disk, so trade #8
is covered the day it lands. The half a gate cannot judge — a wrong-but-legal family — is
printed as a **DELTA ROSTER**: the complete list of documents written as an update, short
enough to read, and anything on it not written repeatedly about the SAME job is wrong.

### 2026-08-11 — THE FIXED BAR GREW, AND THREE MEASUREMENTS ALL SAID IT WAS FINE
Found by SCREENSHOTTING the live page after the fix above shipped — the fix was correct and
the bar under it was not. The word count is a flex child with `flex:1` (a **0 basis**)
sitting beside two nowrap buttons totalling 332px, in a bar whose inner width is 292px on a
320px phone. So it was handed **0px**, its text broke into **five stacked lines**, and the
fixed bar went from 62px to **97px on all seven trades** — a ninth of an 844px screen, gone,
permanently, on the surface every write-up page ends at. At 320 and 360px the box was
literally zero wide and the text drew outside it.
**The gate had three measurements and every one of them passed.** The page does not
overflow horizontally. No tap target shrank — the buttons are still 44px. The bar still
clears the last control; it just clears it from 35px lower down. **Nobody had asked how TALL
the bar was**, so a defect sitting on 56 pages was invisible to the gate written to catch
exactly this kind of thing. It was equally invisible to a render: the page looks fine until
you read the bar.
**The assertion is threshold-free, which is why it generalises.** Not "the bar must be under
N px" — *a LABEL in the action bar may not be taller than the tallest BUTTON in it.* Buttons
carry the 44px floor and set the bar's honest height; anything taller has wrapped, and
wrapping is the defect. Added to `mobile-watertight.mjs`, it **fires on the pre-fix state at
all four widths in the page's DEFAULT state** — meaning it was catchable from the day the
bar shipped — and it immediately found **two more pages of the same class**,
`av/cable-list.html` and `plumbing/supply-house-order.html`, wrapping to two lines at 320px.
Those two are the shape #1 forks §THE THREE SHAPES already names as migration debt, and they
carry their own copy of the chrome, which is exactly why one fix in the shared sheet did not
reach them. **BACKPORT RIDER: all three sites fixed in the same cycle, 56 pages, 0 failing.**
**Rule:** the bar is the ACTION surface, so the least valuable thing on it gives up its room
FIRST rather than growing the bar — `white-space:nowrap` + ellipsis is the universal guard in
`note.css`, and WHICH pages additionally hide the count, and below what width, belongs to
those pages (`docspec.css` hides it under 480px, because its two buttons are the widest pair
in the toolkit and its count cannot fit at any phone width). And: **a fix is not verified
until you have LOOKED at the thing you shipped.** Three gates passed this page in the same
session that a screenshot failed it.

### 2026-08-11 — TWO THINGS UNDER ONE NAME, AND `var` PICKED THE WRONG ONE
`shared/reconcile.js` computed where the other man's sign-off block starts and stored it in
`var tail`. Two hundred lines down, INSIDE the per-line callback, the same function declared
`var tail` for the half of a line that carries his answer. `var` hoists to the top of the
callback, so at the moment the cutoff was tested — `if (tail >= 0 && i >= tail)` — `tail`
was **`undefined` on every line**, the whole sign-off survived the parser, and our own
closing paragraph came back as a line to match against a foreman's rows. `node --check`
passes it, every browser runs it, and the symptom is one extra row in a report nobody has
read yet. **A shadowed variable does not fail — it silently reads `undefined` and takes the
false branch.** The name is the fix: the outer one became `signOff`, which is what it is.
The class is already in this file one floor up (*two different things under one key*); this
is the same law inside a single function, and the reason it was caught in ten minutes rather
than in a field report is that the join has a unit sweep that runs the REAL module —
`tools/toolkit-gates/reconcile-join.mjs`, which found this on its first execution along with
two more: a one-line reply being eaten by the "first line is a subject" rule, and a header
key without its colon (`^off\b`) eating *"Off the main tee · hold a full tile"*, a real ask
in two of the seven vocabularies. **All three were invisible to every gate we own** — they
are logic, not pixels, and nothing but an assertion was ever going to see them.

### 2026-08-11 — THE SWITCH SAID "NOT SURE" AND WAS ALREADY THROWN
`shared/reconcile.js` shipped with its safety property stated in its own header —
*"a pair we are not sure of comes in switched OFF and says so"* — and the surface
computed `on = chosen[id] !== false`. An id nobody has touched is **not** `false`, so
EVERY pair defaulted on, the fuzzy ones included. The *"not sure it's the same one"*
tag rendered perfectly, one centimetre from a switch that was already thrown, and a
hand-typed reply half-resembling a row was one tap on the big yellow button away from
marking that row committed — **the exact failure the whole design exists to make
unreachable.**

Nothing could see it. The pure-logic sweep passed: `pair()` returns `sure:false`
correctly and the surface simply ignored the flag. The mobile gate passed: the switch
is 44px either way. The round trip passed: a clean round trip is *all* exact matches,
so the unsure branch never rendered once in any verification that had been run. **The
property was only ever tested by the sentence that claimed it.**

Two rules out of it. **ONE: a default that is a safety property gets ONE function that
computes it, read by the renderer, the tally and the toggle alike** — three call sites
each re-deriving `!== false` is three chances to disagree, and they did. **TWO: a
property you write in a header comment is a property you must be able to FAIL.**
`tools/toolkit-gates/reconcile-surface.mjs` now drives the states a happy path never
reaches — the unsure pair, the reply that says neither yes nor no, the disabled button
that has to say *which* zero it means — and asserts that an unvouched pair cannot reach
storage. The lesson generalises past this page: **every "we would never…" in this book
is a gate that has not been written yet.**

### 2026-08-11 — A RATIO WAS ALLOWED TO SAY TWO ROOMS WERE THE SAME ROOM
An adversarial audit of the freshly shipped reconcile join, run against the file on
disk with every finding reproduced rather than argued. **Seven defects, in a module
that had already passed an 87-check logic sweep, a 56-page mobile gate, a live
end-to-end round trip and a live injection test.** The classes are worth more than the
list:

**A SIMILARITY SCORE IS NOT AN IDENTITY.** Dice was allowed to grant `sure` at 0.75.
A row of N tokens whose line differs in k of them scores `1 − k/N`, and every row in
this toolkit is 8–14 tokens — room · ask · spec · height · gate · trade — **so a
12-token row tolerated THREE wrong tokens and still cleared the bar.** One wrong room
number scored 0.917, arrived switched on, and hid his line because the pair was "sure".
*The more detail a man put on a row, the more wrong tokens the ratio forgave.* Certainty
now requires a **unique exact** match; everything else is a proposal with his raw line
on the glass. **And exact was not enough on its own:** the four matching forms exist
precisely because the document drops the grouped axis, so the form with the ROOM dropped
makes the same device in three rooms one identical string — answered *will do, will do,
can't*, **which room he refused is not in his message**, and the greedy sort was handing
it out by row id. An exact match against more than one row is now sure of none of them.

**A PROSE RULE APPLIED TO A DOCUMENT WILL EAT THE DOCUMENT.** The sign-off detector fired
on the first disclaimer-shaped line ANYWHERE and cut from that paragraph to the end —
and `av/items.js` ships the spec *"Walk the wall with me before anybody roughs it"*, two
taps to put on a list. A reply carrying that row parsed to **zero** answers, and the page
told a foreman the other company had never mentioned any of them. **A dropped answer is
not a missing feature, it is a false accusation against another company.** The sign-off
is now only ever the LAST block. Same class, one floor down: `Call me: 555-0134` in a
signature satisfied "this looks like one of our documents" and the subject rule ate the
first of three answers.

**A BATCH WRITE FROM A PHOTOGRAPH WALKS THE LIST BACKWARD.** He opens the card, walks the
job, settles a row by hand — and Apply then pushed **In**, a thing somebody went and
looked at, back down to **Committed**, a claim somebody else made, silently, under a
message reading "ticked 3 rows". This is `rowlog.js`'s own pencil-sheet scar at list
scale. The guard went into the **ENGINE**, not the caller: the ladder is monotone, so the
only place that can say so for every caller there will ever be is the code that owns the
ladder. `applyValues` never demotes, never blanks a stated rung, and closes the pencil
only when the open row is in the batch.

**AND THE GATE CAUGHT THIS BOOK'S OWN SCAR IN ITS OWN SETUP** — `localStorage.clear()`
then reload, which is circular because the reload fires `pagehide` and the engine flushes
the still-in-memory rows straight back (§SCARS 2026-08-05). It showed up as two rows and
an "already in" tag on a list that had just been emptied. **A scar you have written down
is not a scar you have stopped making.**

**THE RULE:** *ship, then send somebody to break it, then gate what they broke.* The
audit ran against the shipped artefact while the cycle was still open, and every finding
became a check — `reconcile-join` 87 → 104, plus the surface gate. It found nothing on
injection, which is the other half of what an audit is for: knowing which parts are
actually sound.

### 2026-08-13 — THE FORM ASKED FOR THE ONE THING THE PAGE ALREADY KNEW
Wish `da36b663`: *"has no wish it better button that users can use to make a wish."*
Measured on LIVE production at `/av/cable-list.html` before touching anything: the
bar's only CTA read **"✦ WISH FOR A TOOL"**, the well opened on `kind=new_tool`, and
the `about_tool` select was **hidden and empty**. Saying *this page is broken* cost
four controls and a hunt through a dropdown for the name of the page you were already
standing on — while `currentTool()` sat two functions away in the same file, already
being used **by that same bar** to render the ★ that favourites that exact page.

**The runtime knew. The well never asked.** That is the generalisable one: a form
field asking for something the page can already answer is not a small friction, it is
**double entry**, and this one sat on the single funnel the whole program runs on.
Every future form gets the question *what does the page already know?* before it gets
a field. THE GATE says ticking beats typing; we were charging four taps for a fact we
had.

**Two smaller lessons, both worth the keystrokes.**

**ONE — A DEFAULT CAN ARGUE WITH ITS OWN RANKING.** The queue ranks `bug > improve >
new_tool` because something already in someone's hands beats an idea, and the well
opened on the *lowest* of the three everywhere, taxing the two higher ones three
controls each. `shared/feedback.js` — the newer, more refined sibling — has opened on
`kind="bug"` since the day it shipped. The refinement existed in this repo for over a
week and never walked next door. **That is exactly what the BACKPORT axis is for, and
nobody files a wish for it.**

**TWO — CLEARING A FIELD SILENTLY RETARGETS THE ANSWER.** `new_tool` is about no
existing tool, so switching to it must blank `about_tool`. Switching back restored
**the page in the address bar** — so *improve → pick `write-up` → new_tool → improve*
came back pointing at `cable-list`, and a bug report would have been **filed against a
tool that never had the defect**, costing a cycle chasing it. A pick the user made
outranks the page they are on, and it has to survive the round trip. Found by driving
the real sheet through the state machine; `node --check` passed, the 75-page mobile
gate passed, and both would have passed forever. **A restore path is a state machine,
and a state machine is only ever tested by walking it backwards.**

### 2026-08-13 — A COMMENT CLAIMED THE COVERAGE, AND THE COVERAGE WAS NEVER THERE
`shared/checklist-request.js` opens by naming the two pages it was extracted from —
`av/consumables.html` and `plumbing/supply-house-order.html` — and its persistence
block names them a second time, as pages it *drives*: *"this engine drives
av/consumables, av/cable-list, plumbing/supply-house-order and electrical/pull-list.
Fixing it in the engine fixes all four at once."* **It never drove either of the two
it was extracted from.** The siblings got the engine; the originals stayed forks —
and not debounce-only, which is the scar that paragraph is about. **No save at all.**
Reload the tab and a twenty-minute walk down the van and across two floors was gone,
on the page this whole kit's shape #1 was proved on.

**The generalisable one: a comment that describes a coverage answers the audit
question before the audit reaches the disk.** Anyone checking "is persistence
handled?" reads that paragraph, sees four page names, and stops. The truth was one
`grep -c localStorage` away and it took an axis sweep to run it — 52 of 55 tool pages
kept what a man typed, and the three that did not included the flagship. **Rule: a
file may describe what it DOES; it may never describe who USES it.** That list goes
stale the moment someone forgets to migrate a caller, and a stale list is worse than
no list because it reads as a completed audit. Derive coverage from disk or do not
claim it.

**AND THE SAME CYCLE'S GATE CAUGHT THE SEQUEL, which is the scar underneath the
scar.** The first pass folded the whole header into the draft record, so `snapshot()`
returned an object whenever the jobsite was filled — and **Clear could not clear**: the
wipe landed, the pending debounce fired 250 ms later, and the record came straight
back. That is verbatim §SCARS 2026-08-04 *"clear must actually clear"*, rediscovered
by a new engine written by someone who had just read it. **A scar in the book does not
protect a file that did not exist when it was written.** What caught it was the
assertion reading STORAGE after the debounce window rather than watching the screen go
blank — the exact test that scar prescribes. **The fix is also the better tool:** the
jobsite, the man's name and the account are their own sticky record now, untouched by
Clear, because clearing a *list* must never cost him a field he already typed.

### 2026-08-13 — THE BACKUP WE TOLD HIM TO KEEP COULD NOT BE PUT BACK
Twenty-one shipped row-log pages across nine trades carried a sentence in their own
words: *"the spreadsheet copy is every row with a tab between the columns, and it's
also your backup: this lives in this browser on this phone."* `low-voltage/device-checkout`
went further and gave advice — *"send yourself the spreadsheet copy at the end of a big
day. A browser you haven't opened in a couple of weeks can clear it out, and a new phone
definitely will."* Every word of that was TRUE, and every word of it was about KEEPING a
copy. `shared/rowlog.js` had a TSV **writer and no reader**. There was no path, anywhere
in the program, to put one back.

**A backup you cannot restore is a receipt for one**, and the man who takes the advice is
precisely the man who finds out on the new phone — with the walk already gone. It is the
same class as the three pages that kept nothing (2026-08-13, above) and it hid the same
way: the sentence describing the capability reads exactly like the capability.

**The fix is a reader in the engine, so all twenty-one got it in one commit** and a page
shipped next month gets it with no edit. It ADDS and never replaces — the restoring case
is an empty list on a new device where add and replace are identical, and the other case
is a list with work on it where replace destroys that work for a convenience. Clear stays
the only control that can lose anything. It reads the HEADER rather than column order,
because the file went to a spreadsheet and came back with columns moved, hidden and added.

**AND THE SHEET IS WRITTEN IN LABELS WHILE THE ROW STORES VALUES.** The gate caught this
on nine of the twenty-one: configs that keep `{v, label}` options store `"gc"` and print
`"GC super"` through the column's own `value` function, so a reader writing the cell back
raw filled the field with a label nothing matched. On `rough-in-request` — eight trades —
the column that came back blank was **WHAT'S NEEDED**, which is the entire document. A
picked axis now resolves through its own option list in both directions, in passes,
because one axis gates another. The nine pages each name which field their computed
column came from; a column that names no field is still dropped rather than guessed.

### 2026-08-13 — A GOOD FEATURE WAS CALLING A THIRD PARTY ON EVERY PAGE LOAD
An end-to-end drive of a new page reported one stray console error. The stray error was
`shared/toolkit.js` doing `fetch("https://worldtimeapi.org/api/ip")` **on every page load
of all 76 pages of all nine trades** — an unconsented request to somebody else's server,
to an endpoint that is by design an IP lookup, fired from pages that tell a man in their
own warn block that what he types stays in this browser. The rail is *no external API, no
third-party CDN*.

**It survived because everything about it looked right.** The intent was real and good —
the clock on a job-site tablet can be wrong and a date is load-bearing on nearly every
document this program makes. The request is invisible: the page renders correctly, no
error is shown, and nobody reviewing a diff of a tool page would ever see it. **The
second source in the same function already did the job**: a HEAD against our own origin
returns a `Date` header from a clock the user is already trusting to serve the page. Same
answer, one round trip shorter, discloses nothing that asking for the page did not.
Removing the third party cost this program **no capability at all** — verified, not
assumed: `av:date` still fires with the right date and the document still stamps it.

That is the part worth keeping: the nicety that breaks a rail is never announced as one,
and it is usually powering something you would defend. So the rule stopped being a
sentence — `tools/toolkit-gates/no-third-party.mjs` loads all 76 pages with nothing
touched and fails on any request that leaves the origin.

### 2026-08-13 — TWO GATES, TWO PAGE SETS, AND THE PAGES IN THE GAP
`rowlog-commit-merge` reported `could not add a row` on `roofing/whats-open.html` — a
SHIPPED page — and had been doing so since that page launched. Two blind spots stacked:
its filler dispatched `input` but never `blur`, so a `learn` axis (whose real value lives
in a hidden field written only by the blur handler) stayed empty; and its scope was
`#rlAdd.closest('div')`, which resolves to `.rl-lead`, so a page whose required fields are
the lead PLUS a select down in `.rl-grid` never got the select filled. Every page that
passed happened to have all its required fields in the lead row — which is how a scope
that narrow reported green for weeks. Both fixed; the gate now covers 21/21 and protects
the page it had been silently skipping. **A gate that cannot drive a page is not covering
it**, and "2 FAILURES" at the bottom of a run is only useful if somebody reads it.
`no-third-party` was given `mobile-watertight`'s exact discovery for the same reason —
two gates disagreeing about what "every page" means is how a page ends up green on the
list nobody was looking at.

### 2026-08-14 — THE ENGINE THAT SAT FINISHED-LOOKING IN A DEAD SESSION'S TREE
The session that built `shared/find.js` died between build and ship: the engine, the
docspec wiring and eight include lines sat uncommitted, and NOTHING pointed at them —
the well was empty, the `--status building` sweep was clean (no wish had been claimed),
and the dead session's model-ledger row made the next session's append silently no-op,
which is how the orphan announced itself. Two rules out of it. **The tree is read before
the well:** uncommitted work in lane-owned paths is a claim by a dead sibling and gets
the building-wish treatment — finish it or release it — before anything new is claimed.
**Orphan work inherits zero trust from its own comments:** the header said "driven
through this page in a real browser," and that session may even have done it, but what
survives a dead session is the code, not the verification, so the full gate runs again
from zero on the inheritor's watch. (It did: 51 assertions, local and against
production, before the commit existed.)

### 2026-08-14 — THREE GATES, ONE BLIND SPOT, AND A COPY BUTTON OFF THE GLASS
Standing up trade #10 measured the shipped pages the way a new trade always does, and
the sweep came back with a defect on TEN trades at once: on every `write-up.html` the
PRIMARY "Copy instructions" button ran **27px off the right edge of a 320px screen**,
label truncated — the one control the whole page exists to deliver. `tools/toolkit-gates/
mobile-watertight.mjs` reported **PASS**, and so did every eyeball before it, because all
three of its measurements are structurally blind to the same thing. The bar is
`position:fixed`, so it never widens `documentElement.scrollWidth` — the OVERFLOW check
cannot see it. The button is 44px tall — the TAP check cannot see it. And
`elementFromPoint` at the bar still returns `#copy`, because 27px off the edge still
leaves 161px on it — the REACHABILITY check cannot see it either. Three correct
measurements with one shared hole: **nothing was measuring a fixed bar's own children
against the viewport.** A previous cycle had already fought this exact bar (hid the count
below 480px, trimmed the secondary's padding below 400px) and stopped when the visible
symptom went away rather than when the arithmetic closed: 14 + 136 + 9 + 188 + 14 = 361
against 320. The fix takes the last 41px out of horizontal padding and tracking only —
never the height, never the thumb target — and the ASSERTION went into the gate in the
same commit, negative-tested by reverting the CSS and confirming it fails with the exact
27px. A defect three gates cannot see comes back.

### 2026-08-14 — THE HALF-SWEPT 44px, FOUND BY THE TENTH TRADE
The same pass found the `.rm` delete control on the shape #1 order pages at **32 x 18px**
— on electrical, AV and plumbing, while HVAC, low-voltage and framing carried
`min-width:44px;min-height:44px` on the identical rule. One earlier cycle had fixed the
trades it happened to be standing in and left the siblings at 18px on the only control
that DELETES something. Same pass, same class: every header input on those pages measured
37.6px and every select 36.5px, on all seven, because they are one CSS rule copied seven
times and the tap law had only ever been enforced on hub cards. And `av/consumables.html`
— the page this book cites as its own quality bar, and the file
`shared/checklist-request.js` was extracted FROM — carried **sixty** controls under the
bar, because it kept its own CSS and every engine-era sweep went straight past it. **The
reference implementation is the file nobody re-measures.** Nobody files a wish for any of
this, which is exactly why the BACKPORT rider owns it.

### 2026-08-14 — THE REFINEMENT LANDED ON THE PAGE THAT NEEDED IT LEAST
`av/consumables.html` grew a `shared/find.js` filter and the cycle logged it as done. That
page holds **28 items**. The six pages driven by the engine it was extracted from hold
**35 to 151**, and not one of them had any way to narrow a list at all — the biggest list
in the toolkit was the one with the least help. The reason it looked finished is written
in the previous cycle's own line: the completeness check asked *how many `type="search"`
inputs exist on disk* and answered "exactly two", which is TRUE and is not the question.
Counting the instances of a thing you already built cannot find the pages that should have
had it. **A coverage check that enumerates what exists can only ever return what exists** —
it has to enumerate the pages that qualify and subtract.

### 2026-08-14 — THE ESCAPE HATCH WENT OUT WITH THE FILTER, AND MY OWN GATE COULD NOT SEE IT
The reference filter hid any section with items but none visible — correct for a category,
fatal for the write-in section, which is *where a man goes when the list does not have his
thing* and therefore exactly where a hard filter sends him. Add one write-in row, filter
for anything else, and the Add box left the page with its section. Fixed for every caller
in the extraction. **The part worth writing down is the gate:** the first version asserted
the hatch stays visible, ran green — and stayed green when the guard was deliberately
deleted. An EMPTY section is never hidden by an empty-section rule, so the assertion was
testing a case the bug cannot occur in. Only a MUTATION run exposed that; the gate now adds
a write-in row first and then filters past it, and fails red without the guard. A gate that
has never been run against the broken version is a gate with an unmeasured blind spot.

### 2026-08-14 — THE WIDEST THE BAR EVER GETS IS A STATE THE MOBILE GATE NEVER LOADS
`mobile-watertight` measures every page at four widths as it LOADS. "Check shown" only
exists after somebody types, so the three-control bar — the widest arrangement that row
ever holds, and the one most likely to push a 320px page sideways — was outside every
existing gate by construction. Nothing was broken this time; that is luck, not coverage.
The four-width overflow assertion now runs *inside* the pick-filter gate with the list
narrowed. **A gate bound to page-load cannot see a layout that only a user's fingers can
reach.**

### 2026-08-14 — THE STICKY BAR OWNED A HOLE NOBODY HAD MEASURED
The shared runtime injects a `position:sticky; top:0` nav on every page of every trade.
Measured live at 320 / 360 / 390 / 430 / 900px it is **62px at all five**, and
`scroll-padding-top` was **unset on every page of the whole site**. So every programmatic
`scrollIntoView({block:"start"})` and every `#anchor` jump landed its target's first 62px
*behind the nav* — the heading you were sent to, hidden by the thing that sent you.
`shared/docspec.js` does exactly that twice, which means the Write-Up Setup page on all
ten kits had been doing it since the day it shipped. **Nobody files a wish for this**: it
reads as "the page scrolled a bit wrong", it is invisible in a screenshot taken at rest,
and every gate we own measures a page as it LOADS. It surfaced only because a brand-new
page scrolled its own content into view during a build. **A sticky element owns the hole
it makes, and the file that injects the bar is the file that owes the offset** — one line
in `shared/toolkit.js`, live on all ten trades in the same push.

### 2026-08-14 — CLEARING STORAGE THEN RELOADING TESTS NOTHING
A verification step cleared `localStorage` and called `location.reload()` to get a clean
page. The page came back **fully populated**, and for a second that read as a persistence
bug. It is the opposite: the engine flushes synchronously on `pagehide`, so unloading
wrote the record straight back over the delete. The flush is doing precisely the job it
exists for — surviving the moment the tab goes away. **On any page with an unload flush,
the only honest way to clear it is the page's own control**, which is also the path a real
user takes and therefore the one worth testing. Doing it that way immediately proved the
two-tap arm and that "start the next one" keeps the job and the name.

### 2026-08-14 — THE TENTH TRADE GOT ITS CHIP AND NOT ITS DROPDOWN
`COMMONS_TRADES` was moved out of `gear.js` and into `commons.js` on 2026-08-11 for exactly
one reason, written in the comment above it: framing had shipped a toolkit and never been
added here, so a framer saw six chips and none of them was his. That fix worked and the rot
came back **one layer out**. Each surface spelled the same ten trades out AGAIN, by hand, in
its own `window.FEEDBACK` block — and concrete, trade #10, chip present, **eleven gear rows
and ten tips rows behind it**, was in neither copy. `shared/feedback.js` REQUIRES an area for
a `bug` or an `improve` (`if (kind !== "new_tool" && S.areas.length && !about)` blocks the
submit with *"Which part is broken?"*), so a concrete finisher who found one of his own rows
wrong had exactly two moves: **file it against another man's trade, or close the box** — and
the first one would have entered the queue as ground truth about a trade that never said it.
Both copies are deleted; `Commons.areas()` derives the list from the same array the chips come
from, and the deploy now fails any commons surface whose HTML hand-lists them.
**THE SHAPE, and it is the one worth carrying: moving a list to one place does not delete the
copies downstream, and a comment saying where the list lives is not a gate.** The previous fix
wrote that comment and shipped two hand-written copies past it.

### 2026-08-14 — THE INDEX ANSWERED CONFIDENTLY FOR A ROW THE PAGE DOES NOT HAVE
Found by driving the LIVE gear list after the deploy went green — every gate was passing,
and five of six probe words landed perfectly. The sixth: **"zap strap" returned "Matches:
Wire strippers."** No hedge, no fallback label. The alias index can only ever route to an
object the surface actually CARRIES, and the gear list is tools — cable ties and wire
connectors are consumables and have no row on it. So `find.js` dropped "zap" as noise
(rule 1, correctly), matched "strap" somewhere by infix, and came back at FULL COVERAGE,
which is `mode: "exact"` — so the honest-label branch never fired. **A fallback that
achieves full coverage on the surviving token is indistinguishable from a hit**, and the
gate could not see it either: routing probes are derived from aliases that DO join, so a
word with nothing to join to was never probed. "marrette" was labelled honestly and still
answered with a permanent marker.
**The fix is not a better guess, it is a hand-off:** when the name table knows the word and
this page has no row for it, that goes ABOVE the page's own results with the object named
and a link. Then the gate exposed the better version of the same bug — **"mud ring",
"plumber's tape" and "snake" each name TWO OR THREE different objects**, so handing him one
silently picks a side. A loaded word now always says it is loaded (*"Three things go by
that: Audio snake to live-sound crews; Hand drum auger to everybody; Fish tape to
electricians"*) **even when the page can answer some of them** — a partial answer to an
ambiguous question is the same lie in a smaller coat, and suppressing the notice because
the gear list happened to carry two of the three was the first thing the new gate caught.
**AND THE POSSESSIVE:** the fold split `'` into a word break, so "plumbers tape" and
"plumber's tape" folded differently and one of the two objects went missing for anyone who
types the way people actually type. Apostrophes are deleted, not broken on.

### 2026-08-15 — AN OVERRIDE INHERITS EVERY FIELD IT DOES NOT DECLARE, AND FIVE OF THEM PUT A GC IN THE BLOCK
`creative/docs.js` re-addressed eight shared documents for a trade with no jobsite, and its
own header said so: *"almost all of them change only the addressing, the name and the
reason."* That sentence was true about what the overrides DECLARED and false about what the
user got. `library()` merges field by field, so an override that names `name`, `to` and
`why` inherits everything else verbatim — and five of them shipped `secondary: ["a
one-paragraph version to paste into the GC's change form"]`, `from: "the lead on the job"`
(which the engine prints as the user's OWN ROLE in the block's first sentence) and an `omit`
ending *"worth nothing in a back-charge meeting"* into the instruction block a freelancer
pastes into their AI. **The library ROW looked completely re-addressed; the BLOCK still said
GC**, and the row is the only thing an author looks at.
**Nothing on the board could see it.** `node --check` passes, the docspec gate passes — it
asserts the block is non-empty and carries the eleven blocks and every omit line, not that
the words in them belong to this trade — mobile passes, and the page returns 200. The check
that found it is a **field-by-field walk of the MERGED library**, not the override: rebuild
what `library()` actually returns, then read every emitted string. Two more fell out of the
same walk: the ONE surviving shared document with no override at all (`meeting-minutes`,
reaching a freelancer as *"Coordination Meeting Notes"* with **"oac"** among its search
terms — the exact failure the other eight exist to prevent, sitting unnoticed in the middle
of the list that fixes it), and an override left declared for a document that had since been
DROPPED, which merges into nothing and reads as coverage.
**The rule: re-addressing a shared document means walking every field it OWNS — `from`,
`secondary`, `omit`, `halt`, `facts` — not the three that show on the row.** And a header
that claims the addressing is fixed is a claim about the block, not about the diff.

### 2026-08-15 — THE FIX I BROUGHT TO THE PANEL WAS THE ONE IT KILLED
The delta roster flagged `brief-recap` correctly, it was fixed with `standalone: true`, and
then the BACKPORT rider swept all eleven trades for the same class and surfaced one more
candidate: the shared `toolbox-talk`, minutes family, delta ON. The argument was clean —
each talk is a different topic with a different attendance list, so writing the second as an
update to the first risks dropping the evidence the record exists to hold, structurally the
same as `confirming-note`. **It was wrong, and only an adversarial pass reading the code
rather than the argument caught it.** `deltaOf()` has exactly TWO behavioural call sites;
attendance and topic are emitted **identically on both branches** (`WHO WAS THERE` is an
always-printed spine heading, `facts` is printed unconditionally by VALIDATION, and site and
date are in the mandatory header line), so the change bought nothing it claimed. What it
would have COST is precise: the standalone branch deletes *"Carry every unresolved open item
forward automatically, with the date it was first raised"* and the 48-hour escalation — on
the one shared document whose omitted line is *"what was raised BY the crew and what you did
about it"*, across all ten inheriting trades. Its paste rule is also a WIDER carry than
delta's (*"keep its facts and dates"*, unqualified, versus delta's enumerated open-items /
dates / header), so it would have made the contamination worse. **The precedent's own test
is whether the underlying EVENT recurs on the job, not whether each instance differs** — a
coordination meeting has a different agenda every time and still reports deltas. The
one-instance exception stays at one instance. **A rider that fires is not a rider that ships:
sweeping the class is mandatory, and finding nothing to fix is a valid result.**

### 2026-08-16 — THE INSTRUCTION THAT SAID "NEVER HALT" NAMED ITSELF THE ONLY REASON TO STOP
`emitValidation` composes an author's `halt` line with a fixed tail: *"That is the ONLY
reason to stop and ask me a question."* The tail was written for a halt that names a
condition (*"Only if the input does not say which room this is"*) and it reads correctly
there. **Nine of the 86 `halt` fields on disk say the opposite** — they open *"Never halt"* —
and three of those nine are in the SHARED library, so the composed line shipped on all
eleven trades: `- Never halt. That is the ONLY reason to stop and ask me a question.`
Measured against a golden snapshot: **34 of 225 blocks, every trade.** That line is the one
instruction deciding whether a man in a truck gets his report back or gets interrogated, and
a model resolving a contradiction on it is guessing.
**WHY NOTHING CAUGHT IT.** Both halves were individually correct and every structural check
passed: the block carried all eleven headings, the family was legal, the continuity rule
matched, every omit line arrived. Nothing was asserting anything about the *composed string*,
because the template half is in the engine and the other half is in eleven data files, and no
gate had ever read them joined. **It was found by reading the artefact the page emits, not
the code that emits it** — printed, read line by line, on a cycle that was building something
else entirely. The tail now stands down when the author already said it harder, and
`docspec-config.mjs` asserts the pair can never co-occur (proved by restoring the tail: 3
failures on `av` alone).
**THE CLASS, so it is not re-learned: a fixed sentence CONCATENATED onto author-written text
is an unchecked claim about what that text says.** Every place the engines do it — and they
do it in the VALIDATION tail, in the omitted-line follow-up and in SECONDARY REQUESTS — is a
place where a well-written config can produce a self-contradicting instruction. Gate the
JOINED string, never the two halves.

### 2026-08-16 — EVERY CONTROL PRESENT, REACHABLE AND 44px, AND THE FLOW STILL WRONG
THE DESK's "add another" button lives on the picked card, which sits BELOW the library in the
DOM. Tapping it opened the library ABOVE and scrolled him there — so the only way back out
was a button under fifteen document rows he had to scroll past. **Three gates said green and
all three were right:** nothing overflowed, the control was 44px, `elementFromPoint` returned
it. Reachability is not findability, and no measurement we own can tell the difference.
Caught by looking at a screenshot of the real page at 390px. The count and the way out now
sit at the top of the list, where the decision is being made. **A gate proves a control
exists; only eyes prove the order the controls are in.**

### 2026-08-16 — AN INVENTORY THAT READS THE DISK CANNOT SEE AN UNSHIPPED TRADE
A whole toolkit — `sitework/`, a hub and six tools — was built, and every count on this
lane called it SERVED. The live URL was a **404**. The dir was never `git add`ed, and
neither were the four edits that name it: the workflow's `TRADES` list, the `paths:`
trigger, the runtime's kit switcher, the commons chip. **The artifact IS the site**, so a
trade that exists only in a working tree is a trade nobody can open, and the bump's LIVE
STATE line reported twelve trades and 89 tools because it reads the DISK. It was wrong by
a whole trade and could not have been anything else: a disk-derived inventory measures
what was WRITTEN, and shipping is a different verb. Nothing failed — no red deploy, no
broken gate, no error anywhere — because nothing ran. **The failure mode of an unstaged
ship is silence, and silence reads identically to success on every instrument that does
not fetch the URL.** The BACKPORT half of the same batch was stranded with it: eleven
hubs' favourite star was the trade accent on near-white (masonry's #B9EE1B is unreadable
there), fixed on all twelve and live on none. Standing rule, and it is one line: **before
claiming any axis, `curl` the live URL of the last thing this lane says it shipped.** A
count is not a ship; a 200 is not a render; a render is not a feature.

### 2026-08-17 — A MIGRATION GATE THAT SEEDS ITS OWN FIXTURE TESTS THE SHAPE IT IMAGINED
`jobcard-scope.mjs` has asserted "nobody loses a gate code on the way in" since the day the
card shipped, and it asserted it by WRITING the legacy record itself:
`localStorage.setItem(legacyKey, JSON.stringify(seed))` — a flat id→value bag. That is what
the six hand-rolled pages wrote, and all six passed honestly. Point the same gate at a page
whose header was kept by `shared/draft.js` and it still passes — while every saved answer on
that phone is dropped, because `Draft.keep`'s only writer stores `{v, s}` and `adopt()` read
`old[id]` at the top level, found nothing, and declined **silently**. Green gate, empty card,
no error, and the man has no reason to look. **A fixture the gate invents tests the gate's
belief about the page. Seed what the PAGE actually writes — and when a codebase has more
than one persistence shape, seed EVERY shape and name it in the failure.** Proved by
disabling the unwrap: the flat seed stayed green and the draft-wrapped seed reported the
account, the PO and his name+cell all coming back empty. The same hole stands open for any
future card on `av/consumables.html` or `av/report-builder.html`, the two other `Draft`
headers — which is why the fix went into the module and the gate, not into the page.

### 2026-08-17 — REPLACING A MANUAL GUARD TURNS IT INTO A FOOT-GUN, AND ONLY EYES SAW IT
`shared/dropoff.js` shipped sticky with its own guard: a line reading *"filled in for
&lt;job&gt;"* and a button reading *"different job — clear this"*. Correct, while it was the
only guard there was. The moment the block became per-job, both inverted. The button now
destroys the answers of the job he is standing on — the exact thing the change was made to
protect — and the staleness line can no longer fire on a stale job at all, only on a
**rename**: he fixes a typo in the job name and the block tells him his gate code belongs to
somebody else. A false alarm on the one control whose entire value is being believed.
**Every gate passed** — the leak gate, the reload gate, the mobile gate, the third-party
gate — because all of them test behaviour and neither of these is a behaviour. Both are
CLAIMS, printed on the glass. Screenshotting the real page at 390px is what found them.
**The rule: when an automatic guard replaces a manual one, the manual one is not redundant,
it is WRONG — its words are now a lie and its action is now damage. Retire it in the same
change, or it outlives the problem it was for.** Same class as the `<summary>` on
`hvac/truck-stock.html` that promised "typed once, saved on this phone" about two fields
that had just stopped being saved on the phone.

### 2026-08-17 — THE GATE ENROLLED A PAGE ON THE STRENGTH OF A COMMENT
`jobcard-scope.mjs` finds its pages with `src.includes('shared/jobcard.js')`. The header fix
on `hvac/truck-stock.html` — a page that deliberately has NO job card, because a van is
restocked at the shop — was explained in a comment naming the module it was deliberately not
using. The gate enrolled the page and failed it for not rendering a chip it must never have.
Cheap to spot and worth the line, because the failure mode is not always this loud: a
substring that appears in PROSE is not evidence of a CAPABILITY. **Match on the call
(`JobCard.mount`), not on the mention.**

### 2026-08-17 — THE LIT STATE WAS DRAWN IN A COLOUR MEASURED AGAINST A DIFFERENT BACKGROUND
`.jc-chip.on` and `.do-chip.on` — the SELECTED job chip and the selected delivery chip —
drew their border and their inset ring in `var(--flag)`, the trade accent. Every accent on
this rack is chosen and measured against the DARK NAV at a 7:1 bar, which makes it a LIGHT
colour **by construction**; both chips are drawn on WHITE. Measured accent-against-white on
all twelve trades: **eleven land between 1.30:1 and 2.28:1**, and against the grey line the
lit state replaces (`--line #BABEB6`) the swap is 1.01–1.45:1 — a hue change with no
luminance step at all. The tint behind it adds 1.07–1.19:1. The whole lit state was resting
on bolder text. **The twelfth trade is plumbing at 3.58:1, and plumbing was the only trade
`shared/dropoff.js` had ever shipped on** — the one adopter was the one case that worked,
which is why four months of eyes on it found nothing.
Two lessons, and the second is the transferable one. First: a token's contrast is a property
of a PAIR, and carrying a token from the surface it was measured on to a different surface
carries none of the measurement with it. Second: **a shared component with ONE adopter has
not been tested, it has been sampled once** — the fix and its 11 failures only appeared when
a twelfth trade with the most extreme accent on the board mounted the same block.
Fixed in both shared modules as `var(--deep, var(--flag, …))` — `--deep` is the token every
trade already ships and it measures **5.21–8.46:1** against white on all twelve, so one
two-line change carried it to every trade at once instead of twelve page-local overrides.
The first draft WAS a page-local override on the new page, and deleting it was the fix.
Gated: `jobcard-scope.mjs` now asserts the lit chip against the unlit chip beside it at a
3:1 bar, **proved by reverting the shared rule — 6 of 7 job-card pages fail, plumbing passes.**

### 2026-08-17 — A GATE THAT FAILS ON SILENCE HAS NO WORD FOR "THERE WAS NOTHING TO ADOPT"
`jobcard-scope.mjs` fails any page whose `JobCard.mount` declares no `legacyKey`, and it is
right to: the check exists because a migration that silently declines loses a gate code a
foreman has had saved since June, and OMISSION is exactly how that goes missing. Then a page
was born WITH a card — no predecessor, nothing at an older key, nothing to lose — and the
gate had no way to hear that. The wrong fixes were both available and both bad: invent a
fake legacy key to satisfy the check, or teach the gate to guess which pages are new.
**The escape is an EXPLICIT `legacyKey: null` in the source, where a reviewer reads the claim
in the diff — and silence still fails.** A default that fails closed keeps its value only if
the exception has to be *stated*, never inferred.

## THE RATCHET
Each granted wish widens coverage of the real AV workflow. When a whole category is
covered, the toolkit trends toward the default field-AV utility layer, and the
open request/spec formats it standardizes become infrastructure others build on.
The same ratchet now runs per trade — and the ranked ladder for each one (which rung is
next, and the sharpening that must survive into the build) lives in the PRIVATE
`operator/TRADE_ROSTERS.md` in the vault, alongside the strategy note. Roadmap stays
private; the pages and this craft doctrine stay open.

## CYCLE LOG (append ONE line per toolkit cycle — tool · before→after · proof URL)
This file is the toolkit's evolvable BOOK, read by the P0 **Field Toolkit lane** every
cycle (the lane's STEP-0 ladder is: wishing well → trade expansion → seed roster →
collage → "no ship"). A cycle PASSES only on a SHIPPED + LIVE-VERIFIED tool. Append the
line here at CLOSE; keep it to one line. Never log request contents or requesters.

- `2026-08-03` — **Consumables List** shipped (`av/consumables.html`, pinned #1) · hub +
  shared runtime + wishing well stood up · https://mrdirno.github.io/nested-resonance-memory-archive/av/
- `2026-08-03` — **Field Report Setup** shipped (`av/report-builder.html`) — role-tailored
  AI daily-report setup, paste once into Gemini/Claude/GPT, use daily.
- `2026-08-03` — lane rewired: the P0 collage lane became the **Field Toolkit + Collage**
  lane. Before: trade expansion was invisible to the loop (AV was a bare "OR an AV toolkit
  tool" fallback under a Collage-branded lane, so the loop defaulted to CapCut work
  forever). After: a top-down STEP-0 ladder with TRADE EXPANSION at rung 2 and the SEED
  ROSTER at rung 3, `AV_SOCIETY.md` promoted to the lane's primary BOOK, and the
  Pages-artifact staging assertion made a ship gate for any new `<trade>/` dir.
- `2026-08-03` — **ONE RUNTIME, MANY TRADES.** `av/av.js` → `shared/toolkit.js`, now
  driven by a per-trade `window.TOOLKIT_TRADE` config; wishes carry `trade` (migration
  076); favorites namespaced per trade. A new trade is a config + a registry + pages.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/
- `2026-08-03` — **TRADE #2 IS LIVE: the Plumbing Field Toolkit**, with Supply House Order
  (config picker · unit-of-issue · COPPER/DWV split · zero computed quantities). Verified
  live in a real browser, 15 runtime + 15 functional checks.
  https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/
- `2026-08-04` — **THE FIRST WISH GRANTED: Cable & Adapter List** (`av/cable-list.html`,
  roster rung 1). Before: the well had a live request and no tool; shape #1 existed as two
  forked pages. After: the third instance is the FIRST on the extracted engine
  `shared/checklist-request.js`, and the Wall of Wishes has its first credit. 8 families ·
  61 items · clone-a-line for a second length · finish standard typed once per device ·
  per-line alternate ask · walk-duration persistence. Live-verified end to end (5-line
  order incl. clone + write-in + flagged alternate, byte-identical after reload, 0 overflow
  at 390 px, real-gesture copy).
  https://mrdirno.github.io/nested-resonance-memory-archive/av/cable-list.html
- `2026-08-04` — **[AXIS:BACKPORT] The Wall of Wishes reaches every trade, and the nav stops
  clipping on phones.** Before: `/plumbing/credits.html` 404 for every plumbing user who opened
  the nav menu; plumbing absent from the site-root registry (deployed bundle: `./plumbing/` 0
  hits) so trade #2 was unreachable from the front page; and the sticky bar overflowed EVERY
  page of EVERY trade on a phone (433/487/489px of content in a 390px viewport). After: one
  trade-generic `credits.html`, byte-identical in `av/` and `plumbing/` so the next trade copies
  it unchanged; plumbing registered and reachable; nav fits 320-430px with 44px tap targets, and
  the deploy now asserts per-trade `credits.html`/`credits.json`, that every `tools.js` registry
  href resolves in the artifact, and that a staged trade is registered (both directions).
  SWEPT: the bare-ISO-date scar fix carried into the backport rather than re-forked.
  Verified in a real browser, 8 pages x 4 widths, zero overflow.
  https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/credits.html
- `2026-08-04` — **[AXIS:BREADTH] TRADE #3 IS LIVE: the Electrical Field Toolkit**, seeded with
  the **Pull List**. Before: 2 trades / 4 tools, breadth debt of 4 families, and the checklist
  engine had never been asked to carry a trade it was not written for. After: 3 trades / 5 tools,
  and electrical shipped as a CONFIG — `trade.js` + `tools.js` + `items.js` + one page, zero new
  mechanism. A 20-year commercial foreman reviewed it before a line shipped and the review IS the
  page: write-in FIRST and largest, taking a pasted list one row per line ("nobody forgets the
  wire; what we forget is the fourteen-cent stuff that shuts a floor down"); the 42-line picker
  under it framed as a jog, partial by construction; **free-text Qty** ("2 bx", "500 ft", "a
  case"); a header remembered per device that Clear never wipes; **Start from last list**
  ("half of tomorrow's order is today's order"); one binary HOT — MEN STANDING; and a message
  that closes *"Field request — not a PO."* A safety audit ran beside him and set the data law:
  no ampacity/fill/ratings/code refs, no where-may-I-use-it adjectives, no axis pair that adds up
  to a code table, and NO pre-selected default anywhere. Engine gained five opt-ins (`qtyText`,
  `writeinTextarea`, `writeinQtyDefault`, `docName`, `hasLast`/`restoreLast`) with every shipped
  page unchanged. **BACKPORT RIDER FIRED, swept all three trades in the same cycle:** four
  genericized trademarks found LIVE in `av/consumables.html` (wire nuts · Tek screws · Tapcons ·
  zip ties) plus a bare brand label, all made generic; the hard-wired sibling footer links
  replaced by ONE `TRADES` list in the runtime (trade #4 is one line there); `.tag`'s `nowrap`
  fixed in every hub after it pushed a 320px viewport to 328; and two hardcoded-AV-yellow spots
  in the shared runtime made accent-aware. Deploy gained a both-directions check that the
  runtime's trade list matches the staged dirs. Verified on the LIVE page, doing the job end to
  end: 3-line paste → 3 rows with no invented qty, neutral axes dropped from the output, real
  click → clipboard → real ⌘V byte-identical to the preview, list stable across two reloads,
  32/32 overflow checks at 320/360/390/430 across all three trades.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/
- `2026-08-04` — **[AXIS:BREADTH] TRADE #4 IS LIVE: the HVAC/R Field Toolkit**, with **Repair
  Recommendation** — the turnover a commercial service tech sends the office from the roof so a
  quote can be written without a second trip or a phone call. Before: 3 trades, 5 tools, air-side
  and refrigeration served by nothing. After: 4 trades, 6 tools, and **shape #2 exists in shipped
  code for the first time** — THE NOTE (ordered short fields · the impact line everyone omits ·
  a forget-list · a fixed closing ask). One instance is a page; the engine gets extracted on the
  second, which the ladder says is the T&M ticket. A 5-agent panel (service tech · parts counter
  and dispatch · service manager who quotes off these all day → one 20-year field hand told to
  kill a third → synthesis) ran before a line shipped, and the kills ARE the page: **men / hours
  / trips KILLED** (the tech is estimating his own two hands, not mobilisation or the lift, and
  it is the line customers audit hardest — "two men" survives only as an ACCESS tick, because
  that is handling); **"called in as" KILLED** (§THE SYSTEM OF RECORD — ServiceTitan owns the
  call write-up and makes it mandatory; the WO number carries it); **six named photo slots cut to
  three and moved ABOVE the typing** ("three get shot; six is a form telling a man how to do his
  job" — and he is standing at the plate right now); severity + urgency + a same-trip checkbox
  **collapsed into ONE three-way** — DOWN · WILL FAIL · **WHILE WE'RE IN THERE**, that third
  bucket being both the same-trip flag and the highest-margin thing a tech can tick; "checked and
  fine" promoted from per-finding to per-VISIT (it is what keeps the job when the next vendor
  asks "did he even look at the drive", and what he *couldn't* check pre-sells the after-hours
  trip). Kept and sharpened: the plate typed and never decoded, volts/phase as one tap, the
  number off **that part** not the unit, and the consequence shipped as a PAIR — what breaks
  **and when**, because a consequence with no clock on it is a shrug. **BACKPORT RIDER FIRED,
  swept all four trades in the same cycle:** `.av-brand` — the home link on every page of every
  trade — measured 21px and now carries a 44px floor; and the 44px CTA floor, `accentInk` and the
  filter-based hover that electrical got at trade #3 were swept back into the av and plumbing
  hubs, which had never received any of the three. Verified in a real browser, doing the job end
  to end: 2 findings → a turnover a parts counter could fill, access subs riding into the
  document ("Boom / man lift (has to be rented)"), one tap = one chip append, draft surviving a
  reload; **0 horizontal overflow and 0 sub-44px controls at 320/360/390/430**, and every hub of
  every trade re-measured after the shared-runtime change.
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/
- `2026-08-04` — **[AXIS:COMMONS] Feedback is built in, everywhere.** Before: the wishing
  well lived inside shared/toolkit.js, welded to a trade's nav and registry, so Collage
  Studio — the surface with the most open bugs — had NO feedback path at all (grep for
  feedback|bug|report|contact across its whole source: zero hits). After: `shared/feedback.js`,
  the same well with the trade assumptions removed — dependency-free, framework-free, two
  lines to add to anything, writing to the SAME queue with no migration because `trade` was
  always a general surface key. Collage Studio carries it (topbar trigger, 10 real feature
  areas derived from src/lib, violet-matched), and the deploy now ASSERTS that every listed
  surface ships one. Verified in a real browser: bug-first ordering, area picker shows for
  bug and hides for a new-feature wish, validation fires with a human sentence, zero
  horizontal overflow and no control under 44px at 320/360/390/430.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- `2026-08-04` — **[AXIS:BREADTH] Trade #6 — GC & Site Super, and the breadth debt goes to
  ZERO.** Before: five trades live, GC the last family owed a toolkit; every trade in this
  program sent its paperwork UP to a super who had nothing of his own. After: `gc/` live —
  hub, config, registry, vocabulary data, credit ledger, and **THE WEATHER DAY**, the notice
  a super thumbs out at the gate. Built the way HVAC's was: three independent field lenses
  (a commercial building super · a 9-man owner-operator GC · the PM who RECEIVES it), each
  picking their one tool with no knowledge of the others — **all three picked the weather
  day** — then a 20-year superintendent told to kill a third. He killed 25 controls, and
  every single one was the same species: A NUMBER THAT INVITES AN ARGUMENT (trade-by-trade
  headcount, crew-hours lost, hours lost, days claimed, weather-days-so-far, show-up pay,
  every dollar box). So the page does **no arithmetic at all**, prints **no money**, and
  **never looks up the weather** — the measurement is one typed line with the source inside
  it, in his own mouth, and the page has no opinion about what counts as an unworkable day.
  It is addressed to the PM, not the owner, and that decision was made before a line was
  written because it changes every word: no reservation of rights, no days claimed, no
  signature line. Two things the panel called the biggest gaps shipped with it — the
  **multi-day front** (carry the last note forward, bump the date, name the previous notice
  BY DATE, never a running count) and the **night-before call** (same 15 controls sent
  forward; picking it swaps the head and the closing ask, no second page). Verified by doing
  the job end to end in a real browser, then at 320/360/390/430: zero horizontal overflow on
  all three GC pages, every tap target ≥44px. Storefront manifest updated the same cycle —
  and that is where the sweep found low-voltage had shipped the day before **without** its
  manifest entry, live at its own URL while the storefront still advertised it as "coming
  soon"; both trades are now entered and NEXT_TRADES is empty, with both render sites taught
  to degrade instead of printing "0 trades on the bench".
  **BACKPORT RIDER FIRED, swept to all six trades this cycle:** measuring the live hubs at
  320/360/390/430 caught the favourite ★ on every tool card shipping as a bare 28×28 icon
  button — the only control on a hub card, failing the 44px tap-target law on every trade at
  once, and invisible to the gate that does run because that gate is horizontal and this
  defect is a size rather than a spill. Now 44×44 on all six with the title gutter widened
  30→46px, verified live on every trade. (The rider also produced a NON-finding worth the
  same weight: a suspected cross-trade accent bug in `credits.html` was written, applied to
  six trades, then measured on the live page and REVERTED — the runtime already injects the
  trade accent. Filed as a scar; a sweep is exactly the size of mistake worth two minutes of
  verification.)
  https://mrdirno.github.io/nested-resonance-memory-archive/gc/

- `2026-08-04` — **[AXIS:WELL] the well got shorter, and the well itself got fixed.** A single
  wish carried two defects: Collage Studio's export returning black/partial images, and
  *"your something's broken or feedback stuff is too long it's cumbersome."* The form was
  10 field-groups (trade well: 11), 6–7 of them optional, all standing between a person and
  the Send button — and the proof it wasn't landing is in the queue itself, where that
  report arrived with the whole paragraph typed into the TITLE box. Now: kind → which tool →
  what → why → **SEND**, with everything optional behind one 44px fold that names CREDIT so
  nobody loses attribution by not tapping. Nothing removed, no value renamed, the credential
  weighting intact. **BACKPORT RIDER FIRED:** the shortening landed in BOTH wells —
  `shared/feedback.js` (collage + any surface) and `shared/toolkit.js` (all six trades) —
  and driving the real form surfaced a systemic 44px violation the previous cycle's sweep
  missed one layer down: every control in the trade well was undersized (37px inputs, 39px
  selects, 31px identity buttons, 18px Cancel) on all six trades at once. Fixed at the shared
  file, plus 16px inputs so iOS stops zooming the page on focus. Gated permanently by
  `tests/e2e/well-mobile.spec.ts` — 15/15 across av · plumbing · electrical × 320/360/390/430,
  asserting zero horizontal overflow, zero sub-44px controls in BOTH fold states, and that the
  fold stays collapsed by default. https://mrdirno.github.io/nested-resonance-memory-archive/av/
- `2026-08-05` — **[AXIS:DEPTH] THE DIRECTED-WORK TICKET LANDS ON ALL SIX TRADES, and
  shape #2's engine gets extracted at its second instance.** Before: 6 trades / 8 tools,
  five of them sitting on ONE tool each — a demo, not a toolkit — and shape #2 existed only
  as a page. After: 6 trades / **14 tools**, every trade carrying the one rung its own
  roster ranked at or near the top, built on `shared/note.js` + `shared/note.css` (nine
  field kinds · one stylesheet · six accents · not a line of CSS in any of the six pages).
  The WORDS came from six in-trade researchers and were then cut by six field hands from
  the same trades, and the cuts are the product: AV's role row died ("you are SENDING this
  to that man — a tap that tells the receiver his own job title is a tap nobody takes
  twice") and so did its best research line, "what it cost the room you were here for"
  ("that's a delay claim, and a super will not reply to a delay claim while you're standing
  next to him") — the low-voltage hand killed the same thing independently, in the same
  words. HVAC cut "— OUT OF SCOPE" off the heading (no tech has ever typed that into a text
  message) and put refrigerant on its own row by ASHRAE number, because it is the only
  thing off the truck that leaves no box behind. Plumbing added WHAT IS **NOT** IN THIS TAG
  — ceiling left open, sleeve in but no firestop, capped but not trimmed — which nobody
  else asked for and which is what stops a back-charge in April. Electrical's crew is class
  × men × hours × ST/OT/DT, four taps and zero typing. GC's quote-him-back-to-himself line
  died as "a deposition exhibit, not a tag". No rates, no totals, no arithmetic, no
  signature block on any of them. **BACKPORT RIDER FIRED, swept all six in the same cycle:**
  `plumbing/items.js` created — it was the only trade with no vocabulary file at all; the
  `accentDeep`/`accentTint` pair added to all six `trade.js` so one stylesheet can serve
  every trade; and the deploy now asserts every asset a registry tool page LOADS resolves in
  the artifact, is not off-site and is not origin-absolute (four new scars recorded above).
  Verified on the LIVE pages, all six driven end to end at 320/390/430: zero horizontal
  overflow, no tap target under 44px, the sticky bar never covering content, and the draft
  byte-identical through a reload including the three kinds that keep state in a closure.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/tm-tag.html

- **2026-08-05 — [AXIS:INTERFACE] THE CROSS-BOUNDARY REQUEST · 6 trades × 14 tools → 6 trades × 20 tools.**
  The first tool in this toolkit whose output leaves the company that made it, and the axis
  the LIVE STATE line had never once worked. One walk down a floor produces asks aimed at
  three different companies; every one of them carries a **gate that belongs to somebody
  else's schedule**, and the tool is built around that fact — group the list by WHO and you
  get one message per receiver, by WHEN and your own walk reads as a countdown. Tap a row
  when he commits, tap it again when you have seen it in; **Still open** is Thursday's
  follow-up and it composes with the receiver filter, so "still open, for the electrician"
  is one document. Vocabulary from six in-trade panels (one foreman per trade) then cut by
  a cross-trade skeptic: **96 asks, 558 spec phrasings, 49 receivers, 44 gates**, and what
  the skeptic removed is the point — every RFI-to-the-EOR, every furnish-vs-install
  question, the meter release, the special-inspection report, the as-built, and every row
  with money on it. It also found the missing ask in each trade: *keep my wall clear*
  (AV), *confirm the door swing before I rough the switch* (electrical), *the louver
  opening* (HVAC), *vents through the roof before dry-in* (plumbing), *grid layout* (LV),
  *the owner's own vendors* (GC). The GC's copy runs the other direction on purpose — it
  is the pre-cover call TO the subs, which is the same widget mirrored. **Shape #3's
  stylesheet extracted** at the second instance (`shared/rowlog.css`), and the engine grew
  named document filters, `groupName`, gated `learn` fields and a scoped flagged block.
  **BACKPORT RIDER FIRED, same cycle:** `low-voltage/device-checkout.html` migrated onto
  the shared sheet and deleted 125 lines of forked CSS, which is also how the 38px-tap-target
  scar got fixed on the page that had been shipping it. Five new scars above. Every page
  driven for real at 390px — zero horizontal overflow, nothing under 44px, and the document
  produced end to end.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/rough-in-request.html

- **2026-08-05 — [AXIS:DOCS] THERE IS A FOURTH SHAPE, AND ALL SIX TRADES GOT IT AT ONCE ·
  6 trades × 20 tools → 6 trades × 26 tools.** §THE GATE's escape hatch for paragraph work —
  "build the report-builder shape" — had exactly ONE instance for two months, on AV, which
  meant five trades had NOTHING on this axis. **Shape #4's engine extracted at the second
  instance** (`shared/docspec.js` + `shared/docspec.css`) and `<trade>/write-up.html` shipped
  live on av · electrical · plumbing · hvac · low-voltage · gc, plus the fourth data file
  `<trade>/docs.js`. The isomorphism is the method: `report-builder.html` read as a
  STRUCTURE is eleven blocks, and **ten of the eleven are the same** for a plumber's
  back-charge notice and an AV daily — so the spine, the omitted line and the vocabulary are
  the config and the other ten live in the engine once. **11 shared documents + 24
  trade-specific + 24 overrides** = 14–18 write-ups per trade, each one carrying the line
  everyone leaves out as its own always-on heading so an AI cannot drop it. Emits a
  1,500–1,900-word production instruction block you paste into a Gem/Project/Custom GPT once.
  **BACKPORT RIDER FIRED, same cycle** — this axis existed only on AV and now exists on all
  six, and the two locked §SAFETY laws (never invent → `<MISSING>`; never grade a reading as
  in-range/passing/to-code) ride in EVERY block on every trade, un-untickable. Adversarial
  pass killed **27 of 43** proposed documents including a certified-data leak in a red-tag
  notice. Four new scars above. Every page driven for real at 320/360/390/430px — zero
  horizontal overflow, nothing under 44px, and a document composed end to end on each trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- 2026-08-06 · **[AXIS:BACKPORT] `aria-modal` is a promise, not a behaviour — six trades get
  a real focus trap.** The rider fired from the COLLAGE lane: the trim sheet shipped there
  had a modal that declared itself modal and trapped nothing, and the toolkits have exactly
  that shape — the wishing well is injected by the SHARED runtime into every page of every
  trade, so one leak is 26 tool pages. **Measured on LIVE production before touching
  anything** (av hub, av/consumables, plumbing hub, hvac hub): **12 of 16 Tab stops landed
  OUTSIDE the open dialog** — on the nav, on the trigger button, and on a tool page on the
  user's own INPUT, i.e. typing into the document the sheet is covering. `aria-modal="true"`
  was already on the sheet and it tells assistive tech the rest of the page is inert; it
  does nothing whatsoever about where Tab goes. Escape already worked and was left alone.
  before→after: **12/16 stops escaping → 0 of 26, forwards AND backwards (Shift+Tab
  included), on all six trades plus a tool page, verified against the deployed site.** ONE
  handler in `shared/toolkit.js` covers every trade because the runtime is shared — which is
  the whole reason a new trade is a config and never a fork — and `shared/feedback.js`
  repeats it locally rather than importing, because that file is a standalone two-line
  drop-in by design and may not assume the toolkit runtime is on the page. Collapsed "more"
  fields and the honeypot are excluded from the ring, so the trap cannot park focus on
  something the user cannot see.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/

- 2026-08-06 · **no ship — operator directive preempted the axis work: the BUMP ITSELF was the
  deliverable.** Mid-cycle the operator ordered the cycle messages rewritten to "close to 100%
  signal to noise ratio", Musk/Jobs-style ("if you had to get x amount of things done during
  that cycle what would they be and then do it"), then sharpened it: it "needs to be perpetual
  ... not just a one off or you will not do it again and again". So the fix is a CONTROLLER, not
  a haircut. In the macOS P0 Operator app
  (/Volumes/CLAUDE-CODE/META-COMMAND-CENTER/_automation/helios_operator_p0.py — the .app in
  /Applications is a thin launcher): all four bump templates rewritten, plus
  field_toolkit_directive.py. Static prose on a toolkit bump **6,491 → 2,756 words (−58%)**;
  the collage template alone 4,366 → 1,987. The cut was not stylistic — an inventory found the
  template and the directive were stating **21 rules twice in the same bump** (the eight axes,
  mobile-watertight, field-cool, the storefront duty, the books), so the two now have a
  mechanical partition: **if a rule is in both, it stays in the TEMPLATE and is deleted from the
  DIRECTIVE**; the directive keeps only what CHANGES each cycle (LIVE STATE, trades owed,
  stalest axis) plus the three programs that live nowhere else (the evo loop, the feedback
  drop-in, the capability-surface scar). Two mechanisms are now welded into every bump so this
  cannot rot: **TRIAGE** — every cycle names X (1-3) things it will FINISH, ranked, in its first
  output, and finishes #1 before touching #2 — and the **SIGNAL METER**, which measures the bump
  it is printed inside (template · directive · context · codex words) against the last recorded
  sample and states the **RATCHET: the template may not grow**. A fixed ceiling was tried and
  rejected — it is a static guess a lane learns to ignore. The inventory also surfaced two live
  CONTRADICTIONS, both resolved: vault told the cycle to stamp model_id in a shutdown JSON that
  §1.6.5 pins to exactly three fields (the ledger row already records it), and the toolkit
  template told this lane to `npm run predeploy && git push` persona500 while its own closer
  said P5 owns that push (P5 owns it). TRIAGE also added to the Gemini and NRM operator apps —
  8 templates across 3 apps. Verified: py_compile + a new render_bump.py that lifts each
  template via `ast` and formats it with the real placeholder set (an unbalanced brace here
  kills a 3am cycle), all 8 render, 12 load-bearing probes present in the composed collage bump.
  OWED, unchanged and still the next rung: the confirmed short-audio trim defect in
  COLLAGE_EVOLUTION.md — a looping clip whose audio track ends inside the picture window loops
  the sound at the audio's period instead of the picture's (16 of 24 sampled instants play a
  tone under a picture the file has no sound for). BACKPORT rider: fired on the message system —
  the same TRIAGE block was swept into all 8 templates, not just the one the operator named.

  **SCAR — THE ANTI-FIXATION SIGNAL WAS A FIXATION GENERATOR (found and fixed the same
  cycle).** `field_toolkit_directive.axis_staleness()` reads the `[AXIS:*]` tags back out of
  the cycle log to name the stalest axis — but `cycle_log_lines()` opened only
  `av/AV_SOCIETY.md`, while the CLOSE contract routes a collage cycle's line to
  `tools/collage-studio/COLLAGE_EVOLUTION.md`. So every `[AXIS:COLLAGE]` tag ever written
  landed in a file the reader never opened, COLLAGE scored 999 = "never worked" forever, and
  the moment breadth debt hit 0 the stalest-axis rule picked COLLAGE **every** cycle. The
  mechanism built to prevent fixation was causing it, and it hid in plain sight because its
  output — "last worked never worked" — is exactly what a genuinely never-worked axis prints;
  six logged collage cycles said otherwise. Fixed by merging BOTH books on the leading ISO
  date. before→after: COLLAGE 999 → 0, and the due axis flips **COLLAGE → COMMONS, last worked
  13 lane-cycles ago** — the axis the operator called the one thing that transcends every
  trade, which the broken signal would have starved indefinitely.

  **SCAR — CUTTING FOR SIGNAL CUT 18 LOAD-BEARING RAILS; AN ADVERSARIAL AUDIT CAUGHT THEM
  BEFORE THE RELAUNCH.** Deleting hard is correct, and it is also how a safety rail disappears
  quietly. An independent audit diffed the rewritten templates against the pre-rewrite backup
  for dropped [CMD]/[MACHINE]/[SAFETY]/[GATE] items only, and returned **NOT SAFE**. The worst:
  vault's `carryover_drop_gate` escape ("an item untouched 3 cycles auto-drops and MUST be
  NAMED in the shutdown's `dropped` field, never a silent wipe") was cut from the only text
  documenting it — while `cycle_close.sh` Step 0.06 still runs that gate and `exit 1`s on a
  mass wipe, so a 3am cycle would hit a hard-blocked close with no in-bump pointer to what
  fired. Also restored: the SCAR-L1543 blast-radius bound that makes re-running
  close_p0_terminal.sh safe · cycle_phase.py's four verdicts · the MODEL ROUTING consumer
  (producer still alive at helios_operator_p0.py, consumer deleted) · `/field-toolkit` (the
  lane was ordered to edit fieldToolkits.ts and never told the surface it feeds) · the
  RE-GROUND "confirm it is not ALREADY SHIPPED" pre-check · "write the SCAR into §SCARS" ·
  the well's `about_tool` field · `min-width` in the mobile gate · the offline-export file
  names. The audit also caught THREE contradictions the rewrite itself introduced — MODEL
  CHECK and TRIAGE both claiming "your first output", FREE WILLY calling itself "#1" against a
  fixed a→b→c order, and an unrunnable `.../render_bump.py` path — all fixed. **The lesson is
  the procedure, not the list: a signal cut is not shippable on the cutter's own judgement.
  Inventory the load-bearing rules FIRST, then have a second pass try to prove you dropped
  one.** Restoration cost ~200 words, which is the "add back 10%" that tells you the delete
  went deep enough. Net after restoration: collage bump static prose **6,491 → 2,860 (−56%)**.

- 2026-08-07 · **[AXIS:COMMONS] TWENTY-SIX GENERATORS, AND NOWHERE TO GO WHEN YOU HAVE
  NOTHING TO GENERATE.** Before: every tool ever shipped here — all 26, across six trades —
  produces a document you SEND. Grep the whole site for a page that exists to be *read*:
  zero. COMMONS, the axis the operator called the one thing that transcends every trade, had
  been "worked" exactly once, and what shipped then was the feedback PLUMBING
  (`shared/feedback.js`) — not gear, not photos, not tips, not guides. After: **`/commons/`
  — WHAT'S IN THE BAG**, 68 pieces of gear the field actually reaches for, tagged by trade,
  ticked into a per-device bag and copied out as the list you hand the new guy who keeps
  asking what to buy. No brands, no specs, no prices, no affiliate anything — and the page
  says so in the masthead, because every other must-have-tools list on the internet is
  somebody's commission and refusing that is the only thing that makes this one worth
  reading.
  **THE AXIS SIGNAL SAID COLLAGE, AND THE AXIS SIGNAL WAS A STALE PROCESS.** The bump
  printed `STALEST-AXIS SIGNAL = COLLAGE — last worked never worked` for an axis carrying 10
  tags and the last FIVE commits. `field_toolkit_directive.axis_staleness()` on disk is
  correct and returns `COLLAGE 0 … COMMONS 17` — the 2026-08-06 both-books fix landed. The
  RUNNING launcher holds a pre-fix copy of the module, and per its own rules an edit only
  takes effect on operator relaunch, which must not happen mid-cycle (the startup sweep
  closes every P0-tagged terminal, including the live one). So the fix is real and the
  ARTIFACT serving it is stale — the same class as "the written fix never reached the
  bundle", one layer up. Followed disk truth, not the printout; obeying the printout would
  have made this the sixth consecutive collage cycle, which is the exact fixation the
  mechanism exists to prevent. **Operator: the P0 launcher needs a relaunch to pick this up.**
  **NOT A TRADE, ON PURPOSE.** `commons/` carries no `trade.js`: `served_trades()` and
  `av_wishing_well.py` both derive the trade list from `<dir>/trade.js` on disk, so a config
  here would report a seventh trade that does not exist and inflate breadth debt — corrupting
  the very signal this cycle just caught lying. It sits at the repo root beside the trades
  because no single trade owns it, and it carries `shared/feedback.js` (the standalone
  drop-in built for exactly this) instead of the trade runtime.
  **ONE EDIT, SIX TRADES — and verified, not assumed.** `shared/toolkit.js` links it from
  the nav dropdown of every page of every trade AND from every hub footer (the sibling list
  the hubs already render). Verified LIVE: **6/6 trades carry both links and `/commons/`
  returns 200**, plus a tool page. `deploy_bridge.yml` now stages AND asserts `commons/`,
  its data file and its deps — a nav entry with no per-trade guard is precisely the shape
  that hid a 404 behind `/plumbing/credits.html` for that toolkit's entire life.
  **THE CONTENT DID NOT SELF-CERTIFY.** Seven agents seeded (one per trade + universal),
  then THREE independent adversarial lenses cut it: **39 rejections across 74 candidates**,
  and the lenses caught *each other* — the journeyman's fix for lineman's pliers named a
  brand the rails lens forbids, and its fixes for the universal list were the specs the rails
  lens had just rejected, so the CRITICISM was taken and the WORDING was not. Real catches:
  "channel locks" leads with a live trademark; a non-contact tester was framed as proof a
  conductor is dead, which it never is; "linesman" is not how an electrician spells it; a
  handheld moisture reading was claimed to clear a slab; spade bits and the jab saw are not
  universal, because a site super does not bore studs.
  **SHIP GATE** (`tools/collage-studio/tests/e2e/commons-mobile.spec.ts`, new): 320/360/390/
  430 **and** 320px at a 22px root — zero horizontal overflow, nothing past the right edge,
  no control under 44px, the dock never covering the last row — and it DOES THE JOB, ticking
  real gear and reading the COPIED TEXT back. It found the footer's Field Toolkit link at
  **15px** on the first run: on a phone the way back to the toolkits was the most-tapped
  thing on the page and the smallest. **10/10 local, 10/10 against LIVE**; `well-mobile`
  regression 15/15 after the shared-runtime edit.
  **OWED, named rather than half-built:** contributed FIELD PHOTOS — EXIF stripping,
  client-side resize and moderation-before-render is a rights rail that deserves its own
  increment, not a ride on this one. Then tips, then guides.
  https://mrdirno.github.io/nested-resonance-memory-archive/commons/

- 2026-08-09 · **[AXIS:BACKPORT] THE WAY BETWEEN KITS WAS THE SMALLEST THING ON THE PAGE ·
  6 hubs → all 32 pages, 16.7px → 44px.** The previous cycle's backport sweep came back clean
  on the class it was hunting and MEASURED a different one on the way past, then filed it
  rather than half-landing it: the cross-trade footer links were **16.7px tall on every one of
  the six LIVE hubs, at 320/360/390/430, 7–8 per page** — 100% under the 44px law, on the one
  control whose entire job is moving a tradesperson between kits. Re-measured live before
  touching anything (eyes first): 16.7px, all six, all four widths, confirmed.
  **THE TAP TARGET WAS THE SMALLER HALF.** The switcher existed on the SIX HUBS ONLY. From any
  of the 26 TOOL pages there was no route to another kit at all — `buildBar()` gave every page
  All tools / Wall of Wishes / What's in the bag / its own tools / the wish, and never once
  named another trade. **Six pages out of thirty-two could reach the rest of the program**, and
  a fix scoped to "make the footer links bigger" would have shipped that gap intact.
  **ONE COMPONENT, TWO MOUNTS.** `kitChips(inNav)` + `mountKitBlock()` in shared/toolkit.js:
  a chip grid above the hub footer, and a SWITCH KIT section at the foot of the dropdown every
  page already carries. `inNav` decides exactly two things — whether the commons rides along
  (`kit:false`; the menu already carries "What's in the bag" three rows above) and which
  heading it wears. Everything else is one code path, so the footer and the menu cannot
  disagree about which kits exist.
  **AND IT RETIRED THE LAST FORK.** The trade LIST moved into the runtime at trade #3, but the
  RENDERER was still pasted into each hub — six copies of one eight-line function, the exact
  shape that once left /plumbing/ reachable from nowhere. Six copies → one; each hub keeps only
  `<span id="siblings">` as a mount marker. **Trade #7 is one line in TRADES and lights up both
  mounts on every page of every trade.**
  **THE COPY IS A GATE, NOT A PROMISE.** TRADES rows now carry each trade's `icon` and `accent`,
  which is duplication with eyes open: a `trade.js` only loads on its own pages, so /av/ cannot
  ask /plumbing/ what colour it is, and every cross-trade surface must hold a copy (the
  persona500 manifest already does, on the same terms). So each hub asserts its own row against
  its own trade.js — and the mutation proved the gate is SCOPED: drifting one accent turned
  **exactly one** of six tests red, on the right trade.
  **BACKPORT RIDER FIRED — AND THE SWEEP WAS THE FIX.** The footer's other links are the same
  class, and `.foot` is declared per page: **20 pages carry one, 12 with their own `.foot a`
  rule, every one at 16.7px.** One rule in the runtime — appended to `<head>` at boot, so it
  wins at equal specificity — beats twelve per-page copies and every page added later inherits
  it instead of re-earning it. All six trades swept in this cycle, not filed for the next one.
  **TWO NUMBERS DECIDED THE GEOMETRY.** 112px columns are not round: "ELECTRICAL" is the widest
  unbreakable label and a 104px column split it as ELECTRICA / L at 390px (MEASURED, and now a
  gate — a ONE-word label rendering on TWO lines means the word broke, while "GC & Super" keeps
  its space-wrap). And the dropdown had **no max-height at all**: a six-tool trade already ran
  past a 568px screen with nothing to scroll, before the switcher made it taller.
  **SHIP GATE** (`tools/collage-studio/tests/e2e/kit-switcher.spec.ts` + its config, new):
  6 trades × 4 widths — chip count, 44px on chips AND footer links, zero horizontal overflow,
  marker retired, block above the footer, accent/icon drift, `../slug/` hrefs, no self-link —
  plus a tool-page nav probe, a 320×568 "the last kit is scrollable-to" probe, and a
  CLICK-THROUGH that proves the chip lands you in the other kit and that the kit you land in
  offers the one you came from. **42/42 local, 42/42 against LIVE.** Watched RED on three
  deliberate breaks: shrunk chip 6/6 red, drifted accent 1/6 red, no mount 6/6 red.
  `well-mobile` regression 15/15. Deploy now parses the RUNTIME's own TRADES array and asserts
  every slug has a staged `index.html` — a chip with no directory is a 404 reachable from all
  32 pages, the /plumbing/credits.html hazard multiplied by the switcher. Build printed
  `kit switcher: 7 destinations, all staged`.
  **OWED, named rather than half-built:** `commons/index.html` hard-wires its way back as
  `../av/` and is the ONE page that does not load the shared runtime — so the commons cannot
  carry the switcher without either a fork or an AV-branded nav bar on a surface no trade owns.
  That is an increment, not a rider.
  **AND THE ANTI-FIXATION SIGNAL IS LYING AGAIN.** This bump printed
  `STALEST-AXIS SIGNAL = COLLAGE … last worked never worked` — the 999 signature the 2026-08-07
  entry above says was fixed by merging both books. Ground truth: `[AXIS:COLLAGE]` last appears
  2026-08-06, the two collage cycles since are tagged `[AXIS:WELL]`, and the last 8 commits are
  all collage — a K≥4 stalled route the signal was pointing straight back into. Took BACKPORT
  against the signal deliberately. The generator is NOT ON THIS DRIVE: a drive-wide `grep -rl
  'STALEST-AXIS'` over /Volumes/dual returns nothing, and no file named
  `field_toolkit_directive*` exists to depth 5. So the module the 2026-08-07 entry patched is
  not the code path that writes this bump, and patching a reader that cannot be found from here
  is not something a cycle can verify. **Next cycle will get the same false signal** — read the
  tags off both books yourself before believing the stalest-axis line.
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/

- 2026-08-09 · **[AXIS:INTERFACE] THE LIST HE SENT ENDED BY ASKING FOR A REPLY THAT HAD
  NOWHERE TO LIVE · 6 trades × 26 tools → 6 trades × 32 tools.** Every interface tool this
  toolkit has ever shipped sends an ASK across a boundary and closes by asking the other man
  to answer — and then the answer was a text message with no structure, *"yeah most of that's
  fine, the floor box is a problem, call me"*, in which every commitment made is unfindable in
  October. **`<trade>/answer-back.html` ships on all six** (av *Answer Back* · electrical
  *What I Can Hit* · plumbing *Yes, No, and When* · hvac *My Answer on Your List* · gc *What
  I'll Get You* · low-voltage *Got It / Can't / When*) — one page file, six configs, on the
  shape #3 engine. The private roster named this rung *"the first thing to look at when this
  axis comes up again"* and it was right: every served trade is now on BOTH ends of the
  boundary, which is the real state of a job.
  **AN ANSWER IS NOT A SECOND REQUEST, and that decides the design.** A request is COMPOSED
  (he walks the job, builds a list out of his own head, picks from his trade's vocabulary);
  an answer is ANSWERED — the list already exists, somebody else wrote it, and the only thing
  this man adds is a verdict and a date per line. So intake is a PASTE, the lead field is his
  counterpart's own words kept verbatim, and the fast path is tapping DOWN a list instead of
  adding to one.
  **THE PARSER FAILS OPEN BY CONSTRUCTION.** Its two failure modes are not symmetric: a junk
  row costs one tap to delete, a dropped ask is a commitment one company believes it has and
  the other never made. So it fires only on lines that are STRUCTURALLY not asks — a `Key:`
  header, a count, an ALL-CAPS group heading, and our own sign-off block found by STRUCTURE
  (the trailing block a matched disclaimer belongs to) rather than by guessing at prose,
  because a hand-typed ask *is* prose. Everything dropped is shown with a button to put it
  back; his numbering survives (*"the one I can't hit is 3"* is how this is actually said)
  while a bare bullet does not. And his `From:` becomes your `To:` — the conversation flipping
  is the whole tool in one line.
  **THE OMITTED LINE HERE IS THE DATE.** "Yeah we'll get it" is not something anybody can
  build a schedule on and it is exactly what gets argued about later, so the page counts the
  dateless yesses — in the UI where he can fix it, and deliberately NOT in the document,
  because *"three of his six yesses are soft"* is his disclosure to make, not ours to
  volunteer.
  **THE ENGINE GREW FOUR OPT-INS, every one a no-op for the two configs that predate them**
  (§THE THREE SHAPES): `pasteKey` · `statusWrap` · `statusDone` · `groupSort` — and the
  "when" chips read `TOOLKIT_ROUGHIN.milestones` rather than re-declaring six lists of the
  same gates.
  Gates: **24/24 mobile-watertight** (6 trades × 320/360/390/430, a real request pasted and
  answered on each, the widest chip on screen, zero horizontal overflow, nothing under 44px,
  no page errors) · the job driven end to end (paste → tap → date → copy → still-owed scope →
  reload) · **LIVE ALL GREEN on production**, including all six hub cards · regression on the
  two older row-log configs, where `device-checkout` still STOPS at VERIFIED after six taps,
  proving `statusWrap` defaults off.
  **FOUND IN VERIFICATION, FIXED, AND SWEPT:** the head rollup counted every row while the
  still-owed scope showed a subset, so a scoped copy contradicted itself in its own first
  paragraph — in a document sent to another company, about commitments. New scar above.
  **BACKPORT RIDER FIRED, and the class came back clean:** all six `rough-in-request` pages
  guard the same shape by suppressing their summary line under a filter, and
  `device-checkout` declares no filters, so `answer-back` was the only instance — fixed on
  all six in the same cycle.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/answer-back.html

- 2026-08-09 · **[AXIS:BREADTH] TRADE #7 IS LIVE — FRAMING & DRYWALL, and it is the first
  trade the program CHOSE rather than inherited · 6 trades × 32 tools → 7 trades × 37 tools.**
  The researched five-trade ladder ran out at trade #6, so the next family had to be
  promoted rather than read off a list. It was not a guess. The INTERFACE MATRIX built in
  August names, per served trade, who each one chases — and the framer / drywall crew is
  named by **five of the six**: AV wants backing behind a TV and a wall left clear, EC wants
  his boxes not cut through, HVAC wants a louver opening, plumbing wants the wet wall furred
  out, LV wants blocking before rock. The most-requested-of party in the whole program was
  served by nothing, and every `rough-in-request` page we ship was pointing at a man with no
  toolkit. Every other candidate receiver was named twice or less.
  **THE PIN IS THE OTHER END OF OUR OWN ASK.** `framing/whats-in-the-wall.html` — the backing
  ledger, and the first place the ANSWER to a cross-boundary request has ever had anywhere to
  live. Backing is requested five ways (a text, a marked print, a guy pointing at a stud) and
  recorded zero. Every one of those conversations happens TWICE: once in June when he wants
  it, once in October when he swears it isn't there, and in October the man with the list
  wins. Its only real competitor is a can of keel on the stud, which loses for exactly one
  reason — the keel gets covered and the list doesn't. Two documents off one ledger: COME
  LOOK, scoped to one trade while the wall is still open, and the October message with the
  day each piece got covered. Plus the four standards in framing words — *Before I Close It*
  (this trade's ask is the mirror of everyone else's: **get out of my wall**), *What I'll Put
  In*, the *Extra Work Tag*, and *The Write-Up I Owe*.
  **THE ROSTER WAS RESEARCHED AND THEN ATTACKED.** 8-agent fan-out: four in-trade panels
  (commercial metal stud · residential wood · taper/ceilings · and the RECEIVING lens — the
  man who closes the wall) then three skeptics told to kill about a third. 19 candidates,
  which the skeptics independently diagnosed as **six documents wearing nineteen hats** — four
  backing registers, four order pages, four state-of-the-floor pages, two blame logs. All
  three picked the same pin unprompted. The blame logs died on the money bar and the
  certified-data bar; *Ready to Rock*, *Won't Fit* and *The Load* survived to the private
  roster as this trade's next rungs.
  **THE HEIGHT FIELD IS NAKED, AND THAT IS THE WHOLE SAFETY STORY OF THIS TRADE.** A mounting
  height is the most damaging number this toolkit could ever volunteer: it is buried behind
  rock before anybody notices it came from us and not the architect. No chips, no options, no
  seeded example, no digit in the placeholder, and the page says it out loud — *these are your
  numbers, we don't know them and we won't guess*. Gated, not trusted. Same reason the board
  brand every hand in this trade says a hundred times a day appears nowhere: it is board, it
  is rock, it is mud and bead and a lid.
  **SHIP GATE** (`tools/collage-studio/tests/e2e/backing-ledger.spec.ts` + its config, new):
  7 pages × 4 widths, 320px at a 22px root, and it **does the job** — walks a room, adds two
  pieces through the real bar, taps a row up the ladder, scopes the send to one trade, and
  reads the **clipboard** back. **32/32 local, 32/32 against LIVE.** Watched RED on two
  deliberate breaks (a seeded height placeholder; the wording bug it found).
  **IT FOUND TWO REAL BUGS AND ONE FALSE POSITIVE OF ITS OWN.** A man typing "48 to 84 off the
  floor" into a field labelled *how high off the floor* got "…off the floor off the floor" —
  on any other field a wart, on the height the page editing the one value it swore not to
  touch. "asked text" is not English. Both fixed at the source. And measuring a CHECKBOX
  reports 20px on every browser there is while the 44px+ LABEL wrapping it is what a thumb
  hits: naive measurement flagged 17 controls here, 14 on plumbing and 8 on electrical, all
  fine. A gate that cries wolf on three shipped trades gets switched off, so the probe
  measures the effective target.
  **AND THE GATE ITSELF WAS THE FIRST THING THE SEVENTH TRADE BROKE.** `kit-switcher.spec`
  hardcoded two integers — 6 chips on a hub, 5 in the nav — and turned **35 tests red on
  nothing but arithmetic**, on a change whose entire point is that a new trade is one line.
  Both are now derived from its own TRADES list. Trade #8 will not re-break it. 77/77 local
  and live; `well-mobile` 15/15 unmoved.
  https://mrdirno.github.io/nested-resonance-memory-archive/framing/

- 2026-08-09 · **[AXIS:BACKPORT] THE BAR NAMED THE KIT YOU WERE IN WITH TWO LETTERS ·
  4 of 7 kits, hard-cut, for their whole lives.** Found by LOOKING at the live page after
  every gate was already green. Trade #7's nav brand rendered as **"FR"** on a 390px phone —
  the one control on the bar whose entire job is telling a man which kit he is standing in.
  Measured across all seven: **/plumbing/ lost 13px of its word, /electrical/ 28px,
  /low-voltage/ 42px, framing 92px.**
  **THE MOBILE GATE COULD NOT SEE IT, AND THAT IS THE LESSON.** The defect is a CLIP, not a
  spill: `scrollWidth` never exceeded `clientWidth`, nothing rendered past the right edge,
  and the page was immaculate under every assertion we owned. Horizontal-overflow gates catch
  things that stick OUT. Nothing was watching for something quietly cut OFF.
  **TWO CAUSES.** The runtime's brand span could not shrink, so the PARENT's `overflow:hidden`
  did the cutting — and a fragment with no ellipsis does not read as a truncation, it reads
  as a name, which is strictly worse than showing less. The span now owns its own overflow:
  hard-cut measured **false on all seven** at 390 and 430. And framing's own `brandLead` was
  two words where every sibling ships one — the nav brand is the trade WORD, not the full name
  (GC has shipped "GC" against "GC & Site Super Toolkit" since it stood up). At "Framing" it
  measures 3px of overflow, which is the trailing space.
  **GATED:** kit-switcher.spec now asserts on every trade at every width that the brand either
  names the kit or says nothing — never a fragment.
  **BACKPORT RIDER FIRED:** the runtime fix lands on all seven trades at once, which is the
  only reason it was worth making rather than shortening one config string.
  **OWED, named rather than half-built:** at 390px electrical and low-voltage still ellipsize
  (27px and 40px short). Making them fit means taking width from the "Wish for a tool" CTA,
  which the runtime protects by explicit documented decision as the demand funnel. That is a
  judgement about the bar's priorities, not a bug fix.
  **AND THE CHECK THAT SAVED THE WHOLE SITE:** `node --check` on the runtime. The comment
  above the new rule used backticks inside a JS template literal and closed the CSS string. It
  would have shipped a dead runtime on **all 32 pages of all 7 trades**, and every one of them
  would still have returned 200.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/

- 2026-08-09 · **[AXIS:WELL] THE WALL OF WISHES CAME OFF THE NAV AND INTO THE WELL ·
  every non-trade surface now shows who wished it.** A Collage wisher asked to see "who wished it"
  inside the modal, "consistent cross apps." Trades already show it at `<trade>/credits.html` from
  the nav; `shared/feedback.js` — the well Collage and the commons carry, which has no nav — did
  not. It now renders an in-modal **Wall of Wishes** from the surface's own `credits.json`: one
  edit to the shared well lit up every non-trade surface at once, and it stays private-safe by only
  ever printing the already-anonymised credit name (unifying the trade `tool_name`/`wisher` and
  collage `capability`/`wisher_display` dialects in one renderer). The link self-reveals only when
  a ledger with ≥1 credit loads, so a surface without one simply never shows it. Verified live with
  Playwright at 320/360/390/430; all 7 trades' `credits.html` re-checked live → 200. Full write-up
  in the collage book.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-10 · **[AXIS:WELL] the colour dice (Collage Studio) — and the BACKPORT
  RIDER FIRED, MEASURED RATHER THAN ASSUMED.** The wish itself is a collage one
  and its write-up lives in the collage book; what belongs here is the class it
  exposed and the sweep that followed. THE CLASS: *a control row with a fixed
  number of 44px targets and no room for the next one.* Collage's full-bleed rail
  was six targets in 295 of the 304 pixels a 320px phone has — nine pixels from
  an overflow — so the seventh could not be added at any legal tap size, and the
  rail now wraps instead. SWEPT ALL 7 TRADES for the same class, on the LIVE
  site, in a real browser: 7 trades x 4 pages x {320, 390} = **56 measurements,
  zero horizontal overflow (`scrollWidth <= clientWidth` on both `documentElement`
  and `body`), and the smallest VISIBLE sticky-bar control anywhere is exactly
  44px.** CLEAN — the shared runtime already answers this class, by a different
  and better strategy than wrapping: `shared/toolkit.js` degrades the brand
  progressively (tail below 560px, word below 380px) and never shrinks the two
  things someone came to tap. That was already written down; it had not been
  re-measured since the trade count reached 7 and the tool count reached 37, and
  "documented as fixed" is not the same claim as "measured today". NOTE FOR THE
  NEXT CYCLE THAT SWEEPS: the first run of this sweep reported every page as a
  0px tap target — the probe was matching the closed tool dropdown's hidden
  links. A ruler that reads zero everywhere is a broken ruler, not 56 findings.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/
- `2026-08-10` — **[AXIS:WELL]** bug a596d8c9 from the field ("the tools modal
  when populated has no scroll so whatever is on the bottom gets cutoff",
  /av/consumables.html) · the Tools menu was bounded by `calc(100vh - 72px)`, and
  `100vh` is the LARGE viewport — on iOS Safari with the URL bar showing that is
  ~130px taller than the glass, so the menu was built taller than the screen and
  the scroller was then told it fit. **before→after: last row 110.4px BELOW the
  glass and unreachable at any scroll position → 15.6px clear**, measured at the
  794px large viewport with `innerHeight` reporting the real 664px glass (the
  condition headless Chromium cannot produce by itself, which is why every mobile
  gate we own was green). `sizeMenu()` now measures `window.innerHeight` on
  open/resize/orientationchange/scroll instead of trusting a unit; CSS keeps
  100vh→100dvh as the pre-JS fallback and adds `overscroll-behavior:contain`; a
  scroll cue answers the "no scroll" half of the report. NOT the cause, checked
  rather than assumed: consumables' 115px fixed dock overlaps the open menu, but
  the bar is z-index 40 vs docks 20-30, so the menu paints over it and reserving
  space would only have shortened the menu. **BACKPORT RIDER FIRED:** one shared
  runtime meant all 7 trades were cut off and all 7 are fixed by the one change,
  and the same bug class was swept across the other two overlays — the wishing
  well and the feedback drop-in on /commons/ and Collage — both CLEAN (send button
  clear by 111.2px / 4.2px / 73.8px). Two gates added, each deriving its page list
  from disk so a new trade is covered the day it lands:
  `tools/toolkit-gates/menu-reachability.mjs` (357 page×viewport checks over 51
  pages in 8 dirs, ordinary glass AND the iOS condition) and
  `overlay-reachability.mjs`. Credited on the Wall of Wishes.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/consumables.html
- 2026-08-10 · **[AXIS:WELL] A LIST WAS COMPOSED SITTING DOWN AND HAD NO SURFACE FOR THE
  HALF THAT HAPPENS WALKING · THE WALK LANDS ON ALL 7 TRADES AT ONCE.** Cleared a wish
  STRANDED in `status=building` since 2026-08-09 — an anonymous AV tech, from an iPhone,
  asking for a readout he could use with his hands full on a screen with no pointer. A
  previous cycle wrote the ENGINE half of it and died before wiring or shipping anything,
  so the queue read *served* while nothing was live and 390 lines sat uncommitted: the
  exact failure the STEP-0 stranded sweep exists to catch. **before→after:** a row-log
  page had ONE surface — the pencil sheet — and forty grouped rows on a 390px phone at
  arm's length was a pinch-zoom and a lost place → a second, opt-in surface (`cfg.walk`):
  full screen, dark on purpose, one row at a time, **96px** targets side by side,
  keyboard-operable end to end, screen wake-lock held only while it is open, wired into
  `<trade>/rough-in-request.html` on **all 7 trades** in the same cycle. It walks
  `scopedRows()`, so *"still open, for the electrician"* was already a walk and needed no
  new control; the affirmative SETS the settled rung instead of advancing (a double tap
  cannot walk a row past a rung nobody verified); a hold writes **nothing**, because
  still-open IS the honest record of "I looked and it wasn't there"; and the end of it
  produces no new document — it puts the page on STILL OPEN at the message and never
  writes the clipboard behind him. **FOUND AND FIXED BEFORE SHIP:** the dialog's own focus
  trap put the `display:none` note input in the Tab ring, so one Tab press dropped focus
  to `<body>` outside an `aria-modal` dialog — the 2026-08-06 scar rebuilt one layer down
  by the code written to satisfy it (§SCARS). **DECLINED DELIBERATELY, reasons written
  into §THE THREE SHAPES so the next cycle does not "helpfully" wire them:** `answer-back`
  (four-way ladder, two buttons can express one of four) · `device-checkout` (six rungs, a
  binary tap asserts five steps nobody did) · `whats-in-the-wall` (settled rung `Covered`
  ≠ the rung a pre-rock walk verifies, needs ladder-index counting first). **VERIFIED by
  driving the real page in a real browser and doing the job it claims** — 7 trades × 4
  widths {320, 360, 390, 430} × 40 assertions = **1,120 green**, including zero horizontal
  overflow with the overlay open, zoomed out to 67%, and at a 22px root font;
  `document.activeElement` asserted after ten Tab presses; the walk surviving a reload;
  the end-card counts checked against what the walk was actually told; and a
  separate gate asserting all **9** row-log pages that did NOT opt in are untouched. **Re-run
  against the LIVE site after deploy: 1,120 green, plus the 9-page opt-out gate.** THEN AN
  ADVERSARIAL AUDIT WAS CAST ON THE SHIPPED FEATURE AND EARNED ITS KEEP — two ship-blockers
  and four should-fixes, every one reproduced by measurement, every one fixed and turned
  into a regression assertion in the same cycle: a hold on a row that already said IN left
  the lie in the document and told him at the end that everything was in (it now RETRACTS
  one rung) · an open pencil sheet silently reverted the whole walk on Save (the walk closes
  it first; the older tap-ladder instance of that class is named in §SCARS as still owed) ·
  Escape died after a tap on the row itself · the wake lock leaked when the walk closed
  mid-request, and the "held awake" line outlived the UA taking the lock back · focus fell
  to `<body>` when the walk emptied its own scope and disabled the launcher it came in from.
  Suite after the fixes: **7 trades × 4 widths × 54 assertions = 1,512 green**, and
  `tools/toolkit-gates/overlay-reachability.mjs` now carries the walk as its third overlay
  (16 checks — and its "did it open" test moved from `offsetParent`, which is always null on
  a `position:fixed` box, to `getClientRects()`). **All of it re-run against the LIVE deploy
  after the fixes landed: 1,512 e2e green on all 7 trades, the 9-page opt-out gate clean,
  and 18 overlay-reachability checks PASS (the walk's action button clear of the glass by
  62px at both 390×664 and 320×480).** Credited on the
  Wall of Wishes and on all 7 pages.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/rough-in-request.html

- 2026-08-11 · **[AXIS:DEPTH] THREE TRADES COULD SEND A REQUEST, A NOTE AND A LOG — AND HAD
  NO WAY TO ORDER MATERIAL.** Shape #1 (checklist → a request) shipped in 3 of 7 kits;
  HVAC/R, low-voltage and framing each had the other three shapes plus one trade-specific
  tool, and no order page at all — the largest shape gap in the toolkit, and all three name
  their own on the private roster. Shipped all three: `hvac/truck-stock.html` (37 lines,
  8 sections), `low-voltage/consumables.html` (35, 8), `framing/the-load.html` (44, 9).
  **Zero engine code written** — three configs over `shared/checklist-request.js` plus each
  trade's vocabulary in `items.js`, which is the claim the engine was extracted to make and
  the first time it has been made three times at once. **The vocabulary was the work:** an
  in-trade panel per trade, then a second hand told to kill about a third — 169 proposed,
  116 kept, 53 killed — and it reads like the trade (BOARD, MUD, BEAD, a LID, never the
  manufacturer's name every framer says a hundred times a day; REFRIGERANT and a VALVE CORE
  at a SERVICE PORT, because HVAC's two most-said words are both trademarks). Each carries
  one thing the others do not: **truck-stock ships DEFAULT COUNTS** (a van restocks caps
  four at a time, not one of everything — the counts live in the data, and a page that
  starts every line at 1 makes a tech retype the count on every tick) and its header is a
  TRUCK, not a job; **the-load puts a DROP on every line** — the only order in the program
  that needs one — printed as `→ 3rd east` where a driver's eye lands, rolled up into a
  BY-DROP list because by-category is how the yard PULLS it and by-drop is how the driver
  SETS it, with un-dropped lines NAMED at the bottom rather than quietly printed; **shop
  list carries no device data at all**, because the head-end already exports it and
  re-typing it is double entry. Nothing rated anywhere — not in an option, not in a sub,
  not seeded in a placeholder, which is the back door this class of page leaks through.
  Verified by DOING THE JOB at 390px in a real browser and reading the CLIPBOARD, then
  re-run against the live deploy; neutrals checked against each page's own data rather than
  a pattern, because a regex for "em-dash then a question word" also matches a rule the page
  draws on purpose. Shape #1 now ships in **6 of 7** kits — GC is the seventh and correctly
  has none. · **BACKPORT RIDER FIRED TWICE, both swept across all trades in this cycle:**
  (1) the §SCARS 2026-08-10 pencil-photograph bug is **PAID** — `commit()` now writes only
  what CHANGED in the bar since the pencil opened, measured **16/16 row-log pages FAILING
  before → 16/16 after**, the gate-across-all-of-them the scar asked for, live-verified on
  three trades; (2) the operator's 44px tap-target law was being violated on **41 of 52 live
  pages** — new `tools/toolkit-gates/mobile-watertight.mjs`, three shared fixes sweeping 29
  pages plus six per-page, **41 failing → 0**. Gates: mobile-watertight 0/52 · menu-
  reachability PASS over 54 · overlay-reachability PASS.
  https://mrdirno.github.io/nested-resonance-memory-archive/framing/the-load.html

- 2026-08-11 · **[AXIS:COMMONS] THE COMMONS HAD ONE PAGE AND ONE OF THE SEVEN TRADES WAS
  NOT ON IT ·** `/commons/` 1 surface → **2**, gear 68 → **88 rows**, and a new
  **`/commons/tips.html` — LEARNED THE HARD WAY, 107 tips**, every trade seeing 28–41 of
  them. COMMONS was the stalest axis (last worked 2026-08-07, when the gear list shipped and
  named its own next steps: photos, then tips, then guides). Photos stay deferred **on
  purpose** — EXIF stripping, client-side resize and moderation-before-render is a rights
  rail that deserves its own increment, and half-building it was the temptation. So this
  cycle took TIPS, the content half of the axis, and paid a debt found on the way in.
  **THE DEBT: framing shipped a full toolkit on 2026-08-09 and the commons was never told.**
  Zero gear rows, no chip, not in `COMMONS_TRADES`. For two days a framer opened the page
  that calls itself *every trade* and found seven chips, none of them his — no error, no
  404, nothing to notice, which is why it survived two days of cycles. Fixed with 20 framing
  gear rows plus 3 shared rows re-tagged (the **drywall saw** was tagged to five trades and
  not to the one it is named after), and then fixed so it cannot recur: the deploy now
  parses `COMMONS_TRADES` out of the shipped engine and **refuses any staged toolkit with no
  chip**, and the ship gate **refuses any chip with no rows**. Both directions, because each
  alone leaves the other hole open. Proven, not assumed — the guard **fires on the pre-fix
  state** and passes on the fixed one.
  **SECOND INSTANCE OF A SHAPE, SO THE ENGINE CAME OUT** (§THE THREE SHAPES, applied to the
  commons for the first time). The picker — trade chips, the always-shown universal floor,
  tickable rows, per-device memory, the copy-out dock, the well — moved to
  `commons/commons.js` + `commons/commons.css`. A commons surface is now a masthead, a data
  file and a config object; tips.html is ~40 lines of config. Regression proof: the shipped
  gear page passed the **existing gate 10/10 unchanged** immediately after the extraction.
  Surface #3 (photos, guides) is now near-free, and the new `.rail` means adding one puts it
  on every other surface at once — asserted in the deploy the same way the kit switcher is.
  **THE TRADE FOLLOWS YOU ACROSS SURFACES** (shared view key, separate pick keys): a framer
  who picked framing on the bag is still a framer on the tips. Re-picking your trade on
  every page is the small tax that gets a page closed.
  **CONTENT DID NOT SELF-CERTIFY, AND THE LENSES DISAGREED TWICE.** 8 seed agents → 145
  candidates → 3 independent adversarial lenses → **23 of 130 tips cut**. The rails lens
  killed **nine safety rows the seeders had priced as MONEY** — refrigerant cylinders, gas
  flame-proving, energised rotation checks, shared neutrals, phase colours — the exact
  failure mode this page dies of. The two disagreements were the point: (1) the partition
  lens wanted *"ask what's in the slab before anybody shoots pins"* **widened** from framing
  to six trades; the rails lens **killed it** because it frames ASKING as the clearance step
  before shooting into post-tension, and a verbal answer is not a scan — rails won, and
  widening it would have multiplied the exposure sixfold (same class as the non-contact
  tester cut from gear.js in 2026-08); (2) the partition lens called the two control-line
  rows one duplicate, but the journeyman had already split them by TAG — a super's authority
  versus a layout hand's habit — and gc-only/framing-only means no reader ever meets both,
  which is the only thing the rule protects, so both stayed. The rails lens also caught
  seeder why-lines **citing internal source files**; none shipped. **A fan-out miss caught by
  reading it rather than trusting it:** the framing-GEAR agent's best lines were better than
  the ones written by hand (*"Snap blue — red is permanent, and it comes back through the
  painter's finish"*), so they were merged in, and its 15 rows were held OUT of the tips file
  — a gear row that leaks into a tips page is a page that lies about what it is.
  **SHIP GATE, now parameterised over both surfaces** (24/24, was 10/10 on one) — 320/360/
  390/430 plus 320px at a 22px root, zero overflow, nothing under 44px, the dock never
  covering the last row — and it DOES THE JOB: ticks real rows and reads the CLIPBOARD back,
  asserting the why-line rides along on tips (a tip with no reason attached gets ignored).
  New in it: **no trade chip may land on an empty page**, which is the framing hole expressed
  as the thing a user would actually feel. Site-wide `mobile-watertight` **56 pages, 0
  failing** (was 52 — the new page is globbed in, not listed). Copy sweeps clean: no brands,
  no torque/depth/slope/clearance figures anywhere in shipped copy, no code claims.
  **BACKPORT RIDER FIRED:** the missing-trade class was swept across the whole commons, not
  just patched for framing — both guards are trade-agnostic and will catch trade #8 on the
  day it ships.
  https://mrdirno.github.io/nested-resonance-memory-archive/commons/tips.html

- 2026-08-11 · **[AXIS:DOCS] THE PAGE RENDERED EVERYTHING EXCEPT THE THING IT IS FOR ·
  framing/write-up.html: 5 of 16 documents emitted an EMPTY block → 16/16 emit a real one.**
  Picked up as the stalest axis, and the axis turned out to be carrying a live P0 nobody had
  filed: `framing/docs.js` wrote `omit` as a LIST into an engine that called `.split` on it,
  so `compose()` threw and the instruction block — the only product shape #4 has — was blank
  on the live site for every framing-specific document. Proven at the artifact before a line
  was changed: `PAGEERROR: (t || "").split is not a function`, block length **0**, bar still
  reading *"Pick a document to start"*. Same file put shared DOCUMENT IDS in the `family`
  slot on all five, which the engine swallowed into `recurring` — a damage letter read years
  later was being written as a delta against a previous one that does not exist.
  **THE ENGINE GREW TWO THINGS RATHER THAN THE DATA BEING BENT TO IT.** `omit` may now be a
  LIST, because framing's author wrote three specific omission lines per document where the
  field was built for one, and that is better authoring than the field deserved — each gets
  its own bullet in the block AND its own bullet in the output format, so an AI cannot drop
  two of three. And `famOf()` fails toward STAND-ALONE, never toward delta: guessing
  stand-alone costs a convenience, guessing recurring corrupts a record.
  **BACKPORT RIDER FIRED, and it found the class twice more in two other trades** —
  `low-voltage/inspection-deficiency-letter` tagged `recurring` (a one-shot letter told to
  drop what it already reported, on the document whose point is that an unnamed device stays
  yours) → `notice`; and `electrical/confirming-note` tagged `minutes`, which is
  semantically RIGHT and behaviourally wrong, so the engine grew `standalone: true` and the
  document keeps both its true label and every fact. All 7 trades swept; 54 documents now
  match the engine.
  **ASSERTED IN TWO PLACES, EACH CATCHING WHAT THE OTHER CANNOT.**
  `tools/toolkit-gates/docspec-config.mjs` drives every document in every trade through the
  real page — 113 checks, 7 trades, 0 failing — asserting no throw, a non-empty block with
  all eleven blocks, a legal family, continuity that matches the document, and that EVERY
  omitted line reaches the block. It **fires on the pre-fix state with all three diagnoses**
  and its trade list comes from disk. The deploy asserts the same contract statically over
  the staged artifact, parsing FAMILIES out of the shipped engine rather than copying it
  (also proven to fire pre-fix, 5 violations, exit 1). The half no gate can judge — a
  wrong-but-LEGAL family — is printed as a **DELTA ROSTER**, now exactly the 28 documents
  that genuinely recur. Mobile: site-wide 56 pages 0 failing, plus the PICKED state (which
  the standing gate never reaches, because the omit list only exists after a pick) measured
  at 320/360/390/430 default and bumped — 40/40 clean.
  **THE PANEL EARNED ITS KEEP AND DISAGREED WITH THE PLAN.** Three lenses were cast on the
  DOCS increment I intended (making the "not in the list" path stop shrugging). The skeptic
  refused the brief and found this P0 independently; the PM lens found the family half from
  the data alone. Both ranked *fix the P0 + gate the contract* above the increment, so the
  increment did not ship and is not lost — see the named next rung below.
  **NEXT RUNG, RECORDED SO IT IS TAKEN DELIBERATELY:** `matches()` (docspec.js) ANDs every
  typed token against `name + aka + why`, so real document names miss and the empty state
  routes people into the custom path — the custom path is where SEARCH DUMPS PEOPLE, not a
  niche. Rank the search instead of the AND, show the closest three on a zero-match, and only
  then improve the custom path (four omission classes carrying a concrete artefact — a date,
  a name, a photo location, a before-value — not ten generic ones; no free-text heading,
  `S.extra` already exists; no keyword classifier, because a wrong family silently flips
  `delta` and the authors get that field wrong by hand).
  **AND THE BAR UNDER THE FIX WAS BROKEN TOO — found by SCREENSHOTTING the live page after
  it shipped.** The word count is a 0-basis flex child beside two nowrap buttons totalling
  332px in a 292px bar, so it got 0px, wrapped to FIVE lines and grew the fixed bar from
  62px to 97px on all seven trades — a ninth of the glass, permanently. All three of the
  mobile gate's measurements passed it: no overflow, no small tap target, the bar still
  cleared the last control (35px lower down). Nobody had asked how TALL the bar was. Now
  asserted threshold-free — a LABEL in the action bar may not be taller than the tallest
  BUTTON in it — which **fires on the pre-fix state at all four widths in the page's default
  state**, and which immediately found **two more pages of the same class**
  (`av/cable-list.html`, `plumbing/supply-house-order.html`, the two shape #1 forks that
  still carry their own chrome). **BACKPORT RIDER FIRED TWICE this cycle: once on the
  document contract across 7 trades, once on the bar across 3 sites.** 56 pages, 0 failing.
  https://mrdirno.github.io/nested-resonance-memory-archive/framing/write-up.html

- 2026-08-11 · **[AXIS:INTERFACE] THE LOOP ASKED AND ANSWERED AND LEFT THE MAN WHO ASKED
  READING TWO LISTS · THE THIRD MESSAGE, SHIPPED ON ALL SEVEN TRADES AT ONCE.** Before:
  `rough-in-request` sent the ask and `answer-back` sent the reply, and step three was a
  foreman with a text in one hand and his own list on the other screen, ticking twenty rows
  by hand — finding eight, missing two, and never noticing the three the other man said
  nothing at all about. After: `shared/reconcile.js`, mounted INTO the request page (two
  lines × 7 trades, never a fourth page — the rows are already there and a second copy of a
  list is a second version of the truth). Paste his reply; it pairs his lines to your rows,
  shows every pair before it moves anything, ticks only what you leave switched on, and
  stops at **Committed** because *In* is your own eyes and a message is not eyes. The join
  is EXACT on a clean round trip — `answer-back` stores the ask verbatim, so his line is
  our own line back, and a row is offered in **all four forms** the document could have
  printed it in (the grouped axis is dropped from the line, and the page cannot know which
  walk was copied); everything else is Dice-scored, timid, and shown switched OFF. **The
  block that is the reason to open it: WHAT HE NEVER MENTIONED** — computable only by the
  page that holds the original list, and narrowed to the one receiver when his reply is all
  one receiver's, so it can never report the GC's items as the electrician's silence. Also
  free: a committed row with no date reads *"no date on it"*. **A UNIT SWEEP OVER THE REAL
  MODULE FOUND THREE DEFECTS ON ITS FIRST RUN, none of them visible to any pixel gate we
  own** — a `var tail` inside the loop hoisting over the `var tail` outside it (the sign-off
  cutoff read `undefined` on every line), a one-line reply eaten by the "first line is a
  subject" rule, and a header key missing its colon (`^off\b`) eating *"Off the main tee"*.
  `tools/toolkit-gates/reconcile-join.mjs`, 87 checks. The deploy now asserts the whole loop
  per trade — ask, answer, and a reconcile that is both LOADED and MOUNTED. **BACKPORT
  RIDER: this landed on all seven trades in the same cycle, not on AV first** — the request
  page is one script block copied seven times, so a capability that lands on one is a
  capability six trades are behind on the same day. Verified LIVE by driving all three real
  pages end to end at 390px against the deployed site (4 asks composed → answered →
  reconciled → 3 Committed in storage, 0 pushed to In), plus all 7 trades' cards live; 56
  pages 0 failing on the mobile gate.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/rough-in-request.html

- 2026-08-11 · **[AXIS:INTERFACE] THE SWITCH SAID "NOT SURE" AND WAS ALREADY THROWN ·
  THE SAFETY PROPERTY THE THIRD MESSAGE RESTS ON WAS TRUE ONLY IN ITS OWN COMMENT.**
  Found by driving the two report states a clean round trip never reaches — the reply
  that says neither yes nor no, and the fuzzy pair — an hour after the feature shipped
  green through a 87-check logic sweep, a 56-page mobile gate, a live end-to-end round
  trip and a live injection test. Before: `on = chosen[id] !== false`, so every pair
  arrived switched ON, unsure ones included, and a hand-typed reply half-resembling a
  row was one tap from marking it committed. After: one `isOn()` computes the default
  (sure → on, unsure → **off**), read by the renderer, the tally and the toggle alike;
  `chosen` holds only explicit taps so his choices survive a rebuild; the disabled
  button now distinguishes *nothing left to tick* from *nothing vouched for yet*; and a
  pushback with no reason reads "he didn't say why" instead of echoing our own row back.
  **New permanent gate `tools/toolkit-gates/reconcile-surface.mjs`** — unsure arrives
  off, a verdict-less reply offers no apply button at all, an unvouched pair cannot
  reach storage, and the card mounts with no page error on every trade found on disk;
  green on the working tree AND against the deployed site. **The rule out of it, which
  is bigger than this page: every "we would never…" in this book is a gate that has not
  been written yet.**
  https://mrdirno.github.io/nested-resonance-memory-archive/av/rough-in-request.html

- 2026-08-11 · **[AXIS:INTERFACE] A RATIO WAS ALLOWED TO SAY TWO ROOMS WERE THE SAME
  ROOM · THE THIRD MESSAGE, AUDITED AND HARDENED WHILE THE CYCLE WAS STILL OPEN.**
  An adversarial audit of the shipped join reproduced **seven** defects against the file
  on disk. Before: Dice granted certainty at 0.75, and a real row is 8–14 tokens, so a
  12-token row forgave three wrong ones — one wrong room number scored 0.917, arrived
  switched ON, and hid his line; an exact match against three identical row-forms was
  handed out by row id; a disclaimer phrase inside a shipped SPEC string truncated the
  whole reply to zero answers and the page announced the other company had never
  mentioned any of them; Apply walked a verified **In** row back down to **Committed**.
  After: `sure` requires a **unique exact** match and nothing else, the sign-off is only
  ever the last block, `hasHead` needs real document structure, the engine's
  `applyValues` **cannot demote**, his flag reaches the pushback block instead of the
  couldn't-place drawer, the receiver is only named when it is true of every row shown,
  and a pasted email's no-break spaces no longer swallow his date. Gates: reconcile-join
  **87 → 104**, reconcile-surface extended — and the surface gate caught THIS BOOK'S
  2026-08-05 scar in its own setup (clear-then-reload is circular). Injection: clean, 0
  elements, 0 globals. Green on the tree AND against the deployed site.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/rough-in-request.html

- 2026-08-12 · **[AXIS:BREADTH] TRADE #8 IS LIVE — ROOFING, AND IT IS THE FIRST TRADE
  THAT OWNS A GATE INSTEAD OF RACING ONE · 7 trades × 40 tools → 8 trades × 45 tools.**
  Promoted by the INTERFACE MATRIX rule that promoted framing at #7 — the next family is
  whichever unserved party the most served trades already chase — and with the framer
  served, the roofer was the highest count left, named independently by electrical, HVAC
  and plumbing. The BUILD ORDER had nothing owed, so the rule, not the list, chose.
  **The axis signal was wrong and the tags are why.** The bump computed
  `STALEST = COLLAGE — last worked never worked` while `[AXIS:COLLAGE]` was stamped that
  same morning and the last **12 commits** were all collage. That is the second sighting
  of the 2026-08-09 blindness scar in this book, one floor down: the reader can only see
  tags it actually parses, and a lane that believes it has never touched its most-worked
  axis will keep working it. Ground truth taken by date across BOTH books: BACKPORT and
  BREADTH tied at 2026-08-09, everything else 08-10 or 08-11, collage 08-12.
  **A BACKPORT candidate died on inspection, and that is a result.** `report-builder.html`
  is AV-only and looked like the obvious carry-over, until `shared/docspec.js` turned out
  to already ship ROLE + CONTINUITY + a `daily-report` to all seven trades. Backporting it
  would have forked a page the engine had already generalised — the DOCS cycle of
  2026-08-05 had quietly paid that debt and nobody wrote it down.
  Seeded from a 4-lens × 3-skeptic roster fan-out (8 agents, 34 candidates, ~a third
  killed): commercial low-slope · residential steep · service/leak · and the RECEIVING
  lens answering as the GC, owner and neighbouring trades. Shipped: the four universals as
  configs on the shared engines (**Before I Open It** · **Extra Work Tag** · **What I'll
  Hit** · **Write-Up Setup**, the last carrying four roofing documents — leak-call
  findings, what came up under the old roof, that's-not-from-our-work, roof turnover) plus
  the signature tool.
  **THE SIGNATURE TOOL IS `whats-open.html` — "What's Open Tonight", and three of the four
  in-trade lenses proposed it unprompted** under three different names ("What's Open
  Tonight", "Dry Tonight", "What's Still Open"). Nothing else in the roster was named by
  three lenses, and the synthesis arm — which never saw the build — independently ranked
  it #1. Section by section at quitting time: how far it got on a 12-rung tap ladder, what
  is holding the water tonight, and **what is underneath the part that is still open**.
  The ladder IS the status, so the end-of-day job is literally tapping each section up to
  where it reached. Its honest competitor is the camera roll, not the notes app — the
  steep lens said "four photos in a text takes eleven seconds" — so it only earns its
  place by being faster and by carrying the three things a photo cannot.
  THREE THINGS THE VERIFICATION CHANGED, all found by driving the real page and none by
  reading it. **Lowercasing destroys an acronym:** "IT / server room" reached the document
  as "under it: it / server room" — the pronoun, on the one line the page exists to carry.
  Fixed with `soften()`, which passes through any value with an all-caps run; the BACKPORT
  RIDER FIRED and all seven siblings were swept for the class — only framing lowercases
  doc values at all and none of its pools carry acronyms, so the class was roofing-only
  and is now closed. **A date is not enough on this one document:** the roster's own
  sharpening said the argument is about one specific night, so this page — alone in the
  program — stamps a clock time. **`rl.restore()` is not optional:** the first draft
  omitted it and would have looked perfect on a fresh load while silently dropping the
  whole log every time he backgrounded the phone.
  NOT A SCAR, A PROBE THAT LIED: the first tap-target sweep reported 20 failures on
  `tm-tag.html` and the same class on all eight trades. The checkboxes are 20px and sit
  inside 44px labels — the label IS the target, measured at exactly 44.0. Measuring the
  control instead of its effective target would have "fixed" a law every trade already
  honours. The engine was right; the gate was wrong.
  Accent MEASURED, not eyeballed: marking-paint rose `#FF93C9` at hue 330°, dead in the
  only open arc left (247°→14°, 44.5° from its nearest neighbour) — 7.08:1 on the nav,
  9.09:1 for accentInk on the accent, 5.96:1 white on accentDeep, against bars of 7/9/5.
  Watertight at 320/360/390/430 and zoomed out: 7 pages × 4 widths, zero horizontal
  overflow, every effective tap target ≥ 44px, no page errors. Four sections added, the
  ladder tapped, the document read end to end at 390px.
  https://mrdirno.github.io/nested-resonance-memory-archive/roofing/

- 2026-08-12 · **[AXIS:COLLAGE] THE STRIP — the collage ruler stops measuring an empty ten
  seconds · a bar that knew only its own length → a bar that shows what is IN the take.**
  Well read UNSCOPED first and empty (0 new, 0 stranded in `building`, 19 shipped); breadth
  debt 0 with all 8 trades served; the bump named COLLAGE stalest and the collage ladder
  had already named this rung "the natural next one now that a ruler exists to draw them
  on". Under the playhead, on the playhead's own axis: CUT MARKS where the collage
  re-deals (each with its dissolve's real width) and one LANE per timed source showing the
  passes it makes, the last drawn short when the take ends mid-lap. Two features that were
  pure RELATIONSHIPS are visible for the first time — `march` over a 15s take draws two
  marks at 1/3 and 2/3, and one tap of beat-sync moves them to three at 4/15, 8/15, 12/15.
  **THIRD SIGHTING OF THE STALENESS-BLINDNESS SCAR, and this line exists to narrow it:**
  the bump again computed `STALEST = COLLAGE — last worked never worked` on a day whose
  four previous commits were all collage. The full detail lives in
  `tools/collage-studio/COLLAGE_EVOLUTION.md` (C156 + C156b) as the doctrine requires; this
  line is the date-and-tag the toolkit book's reader can actually parse.
  **TWO SCARS, one of them pre-existing and shipped two cycles ago.** SCAR-C156: everything
  drawn under a range input was positioned on the TRACK's width while the thumb travels
  `thumb/2 → width-thumb/2`, so the fade wedges have been out by up to half a thumb (6% of
  the take) since they shipped — `--range-thumb` is one token now. SCAR-C156b, found by the
  adversarial audit AFTER ship: three predicates answer "is the wall turning" and the strip
  read the wrong one, so a collage of videos (empty turn ring, never cuts) was drawn with
  two cut marks. Both fixed, both live-verified.
  **BACKPORT RIDER FIRED:** the axis class was swept across every trade — no trade toolkit
  page has a slider at all (`grep -rl 'type="range"' av/ electrical/ framing/ gc/ hvac/
  low-voltage/ plumbing/ roofing/ shared/` is empty), so the class cannot exist there; the
  five other collage ranges carry it inside `--fill` where it is bounded by `thumb/2` and
  therefore always hidden under the thumb, measured and deliberately left.
  Proof: 13 invariants, 19/19 mutations killed, e2e green on chromium + both WebKit
  projects and re-run GREEN AGAINST PRODUCTION (4/4), full chromium suite 149/149, 25/25
  unit sweeps tree-wide.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-12 · **[AXIS:WELL] FORTY-FIVE TOOLS AND NOT ONE OF THEM TOUCHED THE MONEY ·
  8 trades × 45 tools → 8 trades × 53 tools, and a fifth shape.** The well had two wishes,
  no bugs. The one taken asked for *"an organize consolidation of all Ibew agreements
  documents… map borders county jurisdictions… build a trade expert per local."* **The
  literal ask was refused and the refusal is the interesting half:** agreement text, wage
  tables and jurisdiction maps are authoritative data we do not have, cannot verify, and
  cannot keep current — and a stale rate on a phone is worse than no rate. What survived is
  the question underneath it, which the wisher put in his own second sentence: *why each
  trade gets what.* **TOTAL PACKAGE** — build your package line by line in your trade's
  words, put theirs in the column beside it, read the difference, send it. Every figure is
  one the user typed off his own stub; nothing is fetched and nothing leaves the device.
  Live on all eight kits in the same cycle, on one new engine (`shared/package.js`).
  **THE PANEL SPLIT, AND THE SPLIT IS THE RECORD.** A working journeyman scored it 7/10
  BUILD and named the real moments (the ratification-flyer napkin math, the book-out
  decision) — and killed the flat dues line: *"it just sits there being wrong exactly when
  I compare two different wage rates, which is the entire point of the tool."* Dues are a
  PERCENT of that column's own wages now, and a trailing `%` typed into any line works too.
  The safety lens returned eleven mandatory changes, all landed: no proper noun of a union,
  association, fund or local anywhere in a seed list; no autocomplete on the column field;
  no example figure in a placeholder; the blank-line flag; two un-switch-off-able
  disclaimers; MORE THAN / LESS THAN instead of anything that reads as advice; and no
  telemetry on a page that holds a wage. **The shape skeptic scored it 2/10 and said kill
  the columns, kill the engine, ship one page for one trade.** Overruled on the standing
  breadth law and recorded here so the receipt is paid if it was the wrong call — but it
  took two of its hits: THREE COLUMNS BECAME TWO (its 320px arithmetic was right), and the
  seed lists were cut to what a stub actually carries. **BACKPORT RIDER FIRED IN THE SAME
  CYCLE:** the wish arrived on the AV surface and shipped to all eight kits at once, AV and
  GC carrying an offer-shaped vocabulary (salary, bonus that actually landed, what the shop
  puts in) where the six union-hourly kits carry wages/fringes/dues/per-diem.
  Gate: 32 overflow assertions (8 trades × 320/360/390/430), zoom-out to 0.5, zero controls
  under 44px, zero page errors, draft survives a reload, and the arithmetic driven end to
  end in a real browser — 66.25 vs 71.65, delta $5.40/hr = $9,720 a year at 1,800 hrs, dues
  3% → $1.46 off 48.50 and 3.5% → $1.82 off 52.10.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/total-package.html
- `2026-08-13` — **[AXIS:WELL]** **CREATIVE FIELD TOOLKIT — trade #9** shipped from wish `3204d77c`, the first family here that is not a construction trade and the first stood up by a wish rather than off the ladder · **8 trades / 53 tools → 9 trades / 55 tools**. A 3-lens judge panel returned BUILD_NARROWER unanimously and killed "creatives" as a framing; what ships serves the one-person shop that shoots and cuts. **Notes Back** (shape #3 — the round of client notes the review tool never saw, answered line by line, carrying a rung no construction kit has: THAT'S AN EXTRA) and **That's Another Round** (shape #2 — the same-day out-of-scope heads-up, no price, ends in a choice). Hue 288.0°, the exact midpoint of the only arc wider than 62°; 7.88 / 10.74 / 7.39 on the three contrast bars. **BACKPORT RIDER FIRED, three times:** the four answer rungs, the boundary sentence and the intake's first-line assumption all became DATA across all nine `answer-back` pages with the shipped wording as the default (verified: no sibling declares any of them, so the eight are behaviour-identical); `shared/note.js` `buildTicks` was fixed on both the render and copy paths where `.sub` on a string primitive resolved to `String.prototype.sub` and printed `function sub() { [native code] }` into a client-facing message; and six commons rows a camera bag makes false left the `universal` floor. Gate: 24/24 overflow assertions clean (4 pages × 320/360/390/430, populated and empty), zero site console errors, root font bumped to 20px still clean, the paste driven end to end — 5 rows verbatim with timecodes intact and the subject line restorable — and both documents copied and read for price/fee/invoice/signature leakage. Two blockers found by the browser that every static check passed, both fixed and re-gated before ship. Storefront: entry live, drift checker clean, contract rebuilt (9 trades, 55 tools, 4 personas bound). https://mrdirno.github.io/nested-resonance-memory-archive/creative/
- `2026-08-13` — **[AXIS:WELL]** **THE WELL NOW OPENS ON THE PAGE YOU ARE STANDING ON**, from wish `da36b663` — *"has no wish it better button that users can use to make a wish"* · **before:** on all 73 tool pages of all 9 trades the bar's only CTA read "✦ WISH FOR A TOOL", the well opened on `kind=new_tool`, and `about_tool` was hidden and empty, so reporting a shipped tool broken cost four controls plus a dropdown hunt for the name of the page you were already on (measured live at `/av/cable-list.html`, not assumed) · **after:** on a TOOL page the CTA reads "✦ Wish it better", opens on `improve`, and arrives with `about_tool` already set to that page — one tap, then type; on a HUB or the Wall of Wishes nothing changes (`new_tool`, "✦ Wish for a tool"), because someone browsing a hub is shopping; the menu's "Wish for a tool" now says `new_tool` explicitly so a tool page can never lose the new-tool funnel by inheriting the page's default. **BACKPORT RIDER FIRED — structurally and by sweep:** the fix is 99 lines in `shared/toolkit.js`, the ONE runtime all nine trades load, so av · creative · electrical · framing · gc · hvac · low-voltage · plumbing · roofing landed in the same commit and were each asserted, not assumed (same-origin iframe probe, one tool page + hub/credits per trade); the sibling surfaces were swept too — `shared/feedback.js` already opened on the highest-ranked kind (`bug`) and needed nothing, which is where this refinement was borrowed FROM, and `commons` `areas` were checked against the 9 trades on disk and are complete. **FALSIFIABLE (EVO LOOP step c, written into the code):** if the `improve` default is right, improve+bug carrying an `about_tool` rise and new_tool wishes arrive from hubs; if the well goes quiet, or improve/bug name a tool the wisher was not on, the default is steering people instead of reading them — revert it. One defect caught by driving the real sheet that every static check passed: a user's explicit tool pick was silently replaced by the current page after a round trip through `new_tool`, which would have filed bug reports against the wrong tool (§SCARS 2026-08-13). Gate: `tools/toolkit-gates/mobile-watertight.mjs` 75 pages at 320/360/390/430px, default and bumped text, **0 failing**; the CTA got NARROWER, 161px → 149px. Out of lane and routed to P5 rather than acted on: the wish also names the Vibe Cards / founder page (persona500, not this repo) and asks whether a generator should be published at all instead of its output. https://mrdirno.github.io/nested-resonance-memory-archive/av/total-package.html
- `2026-08-13` — **[AXIS:BACKPORT]** **THE THREE PAGES THAT KEPT NOTHING** · **before:** of 55 live tool pages, 52 kept what a man typed and **three kept nothing at all** — `av/consumables.html` (the page shape #1 was proved on), `plumbing/supply-house-order.html` and `av/report-builder.html` had no save of any kind, so a reload cost the whole walk, the whole order, or the paragraph of house rules he had just written. Not "debounce-only" — the scar `shared/checklist-request.js` already carries. **No save.** · **after:** all three keep the work, through one new shape-agnostic `shared/draft.js` and **not one pixel moved** on any page. **HOW IT HID FOR WEEKS, and it is the scar worth having:** the engine's own header says it was extracted from those two pages and names them again as pages it *drives*. It never drove either. **A comment that describes coverage answers the audit question before the audit reaches the disk** — corrected to say what is true, and the fork debt left ON the roster rather than paid by pretending a rewrite is a fix. Migrating the flagship onto the engine would have risked its layout (its qty+note sit on the row; the engine hides them behind `.cfg`) and lost four behaviours the engine has no equivalent for — filter, check-shown, per-category All, the n/total tally. The defect was the SAVE, so the save is what got extracted. **THE GATE CAUGHT THE SEQUEL:** Clear wiped the list but the header kept `snapshot()` non-null, so the debounce rewrote the record a quarter-second after the wipe — §SCARS 2026-08-04 *"clear must actually clear"*, rediscovered inside a brand-new engine. Job / name / account are a **separate sticky record Clear never touches** now, which is the fix and the better tool at once. Clear also removes write-in rows outright, so **"start from last list"** ships in the same change: the only button that destroys a list is the one that keeps a copy of it. **BACKPORT RIDER FIRED — swept, not assumed:** every other persisting surface checked for the same class — `gc/weather-day` and `hvac/repair-recommendation` already carry the flush triad, `shared/docspec.js` writes synchronously on every keystroke so it has no pending timer to lose, `shared/toolkit.js` only stores favourites on tap. The class was exactly these three. Gate: **40 browser assertions, green on file:// AND re-run GREEN AGAINST PRODUCTION** — a real `page.reload()` so `pagehide` and the flush are what is under test; Clear verified by reading STORAGE after the debounce window; a fresh device via a new context, never clear-then-reload; the restore proved name-keyed by putting a write-in mid-list and asserting no quantity shifted. `mobile-watertight` 75 pages × 320/360/390/430 × default and bumped text, **0 failing**, and the new control measured at 44px with zero overflow at every width. Storefront unchanged — no new tool, no new trade. https://mrdirno.github.io/nested-resonance-memory-archive/av/consumables.html
- `2026-08-13` — **[AXIS:DEPTH]** **THE THIRD RUNG ON TRADE #9, AND THE BACKUP THAT COULD NOT BE PUT BACK** · **before:** `creative` was the thinnest kit on the board — 2 tools against 6–8 everywhere else, no row log at all, and the shape that covers "what the other side still owes you" missing from the one trade whose week is mostly that · **after:** **9 trades / 55 tools → 9 trades / 56 tools**, and `creative/still-waiting-on.html` ships as a CONFIG on `shared/rowlog.js` — zero new mechanism, which is the one-runtime-many-trades claim tested on the least construction-like trade there is. **THE PANEL DISPOSED OF ITS OWN BALLOT.** Three lenses scored a five-candidate slate (delivery note · offload log · shoot-day confirm · pack list · rate breakdown); the shape skeptic killed four from evidence on disk and then killed the ballot itself — *"the panel already answered it and this ballot is mis-ordered"* — pointing at the ranked roster this trade has carried in `tools.js` since it launched, which puts Still Waiting On above everything offered. It was right, and that is K2 working: the arm that generated the candidates does not get to grade them. The safety lens independently graded the winner of the ballot MEDIUM-HIGH and named the offload log the worst liability proposed in nine trades (a page printing OK TO FORMAT on a claim it cannot observe). **THE LINE THE PAGE EXISTS FOR CAME OFF THE PANEL VERBATIM:** an eleven-year one-person shop, on the record — every chase message ever written lists what the client owes and *not one in fifty says what it costs when their half isn't there*. So `holds` is a first-class axis, rides on every row of the document, builds the escalation filter, and the page counts (in the UI, never in the document) how many waiting rows say nothing about what they stop. **NO DAY MATH, refused twice:** parsing "on the call Tuesday" is the page guessing, and an elapsed-day count aimed at a client is the register this trade's tone rail exists to stop. **BACKPORT RIDER FIRED THREE TIMES, all swept and asserted, none of them wished for:** (1) 21 row-log pages across 9 trades told a man the spreadsheet copy "is also your backup" and the engine had a TSV **writer and no reader** — a reader now lives in `shared/rowlog.js` so all 21 got it in one commit, additive-only so nothing on screen can be lost by pasting, header-driven so a spreadsheet round trip survives moved columns, and label↔value resolved on picked axes after the gate caught nine pages restoring **WHAT'S NEEDED** blank; (2) `shared/toolkit.js` was calling `worldtimeapi.org/api/ip` **on every load of all 76 pages** — an unconsented third-party IP lookup on pages that promise the opposite, deleted, with the same-origin `Date` header proven to give the identical answer (`av:date` still fires, document still stamps); (3) `shared/feedback.js`'s repro placeholder invited exactly the paste that would carry a client's address and names off-device, reworded on all 76 at once. **GATES: two new, one repaired.** `rowlog-restore.mjs` drives the real add bar, clicks the page's own copy button over a trustworthy origin (file:// would silently exercise the fallback branch), throws the browser away, and re-imports into a FRESH CONTEXT — **21/21 byte-identical, additive, junk refused**. `no-third-party.mjs` loads all 76 untouched — **0 leaving the origin**. `rowlog-commit-merge` was found reporting `could not add a row` on the shipped `roofing/whats-open.html` since launch (never fired `blur`, and scoped to `.rl-lead`) — fixed, **21/21**, now covering the page it had been skipping. Plus `mobile-watertight` 76 pages × 320/360/390/430 × default and bumped text **0 failing**, and 25 assertions driving the real page end to end: the document verified for what it carries AND for what it must never carry (no price, no fee, no day count, no overdue register, no round count), the chase proven to drop what is already in hand, and the list proven to survive a real reload. Storefront: entry added to the persona500 manifest (P5 pushes). https://mrdirno.github.io/nested-resonance-memory-archive/creative/still-waiting-on.html

- `2026-08-13` — **[AXIS:COMMONS]** **A ROOFER TAPPED HIS OWN CHIP AND WAS HANDED A VOLTAGE TESTER** · **before:** roofing had a chip on both commons surfaces and **not one row in the entire commons had ever been written for it** — 3 "own" gear rows and 3 tips, every one of them a universal row an unrelated commit had widened to the eight construction trades, so his trade's gear read *cordless drill · torpedo level · non-contact voltage tester*. Siblings carried 7–22. Measured live before the fix, not assumed · **after:** **gear 3 own / 0 written → 21 / 18; tips 3 / 0 → 15 / 11**, seeded by the same adversarial fan-out that seeded every sibling — a seeder per surface, then a journeyman lens and a rails+partition lens cutting what it wrote. **THE PANEL REJECTED THE BALLOT AND WAS RIGHT.** The slate offered the two unbuilt parts of the founding brief (field photos, guides) plus a cross-trade name table; all three lenses independently attacked the ORDERING — *"it is in the founding brief" is not a rail* — and the shape skeptic found this hole instead and argued the decisive point: `COMMONS_SURFACES` puts every new surface in front of every reader, so shipping a third page hands the roofer a THIRD page with nothing on it. **You would be multiplying the hole.** Photos are deferred a third time on a harder reason than last time (`shared/feedback.js` is a text-only POST with no file input, so client-side EXIF-strip and resize are unenforceable by construction — and moderation prevents publication while doing nothing about CUSTODY); guides are refused as written (a guide is a procedure, and this page's own header says *not a how-to*); the name table's full rail set is now written into §THE COMMONS as rung 2 so it is not re-derived. **SIX ROWS AND THREE RE-TAGS DIED IN THE CUT:** the shingle ripper (a slate tool — on asphalt every man reaches for the flat bar he already carries, which was missing entirely), the core cutter (the consultant's test cut, and a row telling a crew to cut a hole in somebody's warranted roof), the moisture-meter re-tag — *the ncvt breach wearing a tag instead of a verb, because "the meter says dry" is the claim that leaves saturated board under a new roof* — and the fresh-air-intake tip. That last one names the pattern the height rail actually caught: almost nothing proposed said *be safe*, it **PRICED A SAFETY EXPOSURE AS MONEY** — a shutdown, a callback, a bare foot itemised beside a tire and a mower blade — which is worse than an honest safety tip because it teaches a reader to weigh a hazard as a cost he can eat. The subtlest instance survived a rewrite instead of dying: *"find out what the deck is"* had its reason pointed at a truck driving for material, and that is the fall-through question, so it now points at the approved submittal, which is where the number lives anyway. Both halves of the trade, because `roofing/items.js` makes that an invariant — the first seed came back commercial twice over, a bag with no hammer in it, and said mod bit *"gets welded"*; mod bit is **torched**, and that one word is how a roofer knows who wrote a page. **BACKPORT RIDER FIRED TWICE, all nine trades at once, in the one engine they share:** (1) the commons stamped **the chip you had open** onto every pick you were carrying — tick three rows under Electrical, tap Plumbing, and Copy produced `WHAT'S IN THE BAG — PLUMBING` over glow rods and lineman's pliers, while those picks stopped rendering and kept COUNTING, so the dock read "3 in your bag" over a screen with nothing ticked and no way to reach them; one partition function now feeds both the screen and the document, and anything outside the current view rides in its own named section. (2) **His own rows lead** — found by doing the job, not by a gate: sections render in FILE order and shared rows sit earlier in the file than any one trade's own, so the moment roofing was seeded the first four rows under "Roofing" were a drill, a level, a tester and a radio. Every count passed and the page still opened on somebody else's bag. **THE GATES THAT MISSED IT, AND THE ONE THAT COULD NOT SEE IT:** the ship gate written against the framing scar asked `toBeGreaterThan(0)` and the deploy counted the FILE (`n_gear >= 20`) — both green on an accident. Both now ask how many rows were **written for** the trade (a narrow tag list), verified firing on this exact defect and on nothing else. `tools/toolkit-gates/commons-bag.mjs` is new because every gate we owned loads the page fresh or never leaves the chip it ticked on: **18/18 fail against the shipped engine, 18/18 pass against the fix.** §TRADE EXPANSION now names the commons — framing joined the program with no chip, roofing joined with a chip and nothing behind it, and a checklist that does not name a shared surface will not update it. Gate: **commons e2e 24/24 and `commons-bag` 18/18 GREEN AGAINST PRODUCTION**, mobile-watertight 320/360/390/430 default and bumped on both surfaces, zero page errors, and the job driven end to end on the live site as a roofer. Storefront unchanged — no new tool, no new trade. https://mrdirno.github.io/nested-resonance-memory-archive/commons/
- `2026-08-14` — **[AXIS:DOCS]** **THE SEARCH THAT SAID "NO MATCHES" TO A TYPO, AND THE DEAD SESSION THAT HAD ALREADY KILLED IT** · **before:** both search boxes in the toolkit ANDed the typed tokens as raw substrings — the document library on all 8 `write-up` pages, and the item filter on `av/consumables.html` (whole-phrase `.includes`, stricter still) — and the measurement now in `shared/find.js`'s header says what that cost: all 953 queries built from the authors' own strings pass (substrings BY CONSTRUCTION — the green that means nothing), while 5,384 mechanical perturbations of the same strings missed 4,121 times (**76.5%**): +"template" 100% · plural 99% · one typo 99% · joined 97%. "daily field report template" returned an empty library on every trade and dumped the man into the custom path — which was never a niche, it was where search dumped people · **after:** `shared/find.js` live behind both — noise tokens are dropped instead of vetoing (NO stopword list: a token that scores zero across the whole library IS the measurement), coverage-tier degrade so "nothing matches" is a bug not a state, fuzzy last with a first-letter guard and an edit budget ("turnover" ≠ "handover"), the typed phrase outranks everything, and every approximate answer SAYS SO — "Closest to …" / "Nothing matched that — closest three", never a silent swap. **THIS CYCLE INHERITED THE BUILD FROM A SESSION THAT DIED BETWEEN BUILD AND SHIP** (§SCARS 2026-08-14): engine, docspec wiring and the eight include lines sat uncommitted; the well was empty and the building sweep clean, so only tree-before-well found it. Finished on top of the orphan: the mode-"all" honesty hole (a punctuation-only query labeled the FULL library "Closest to “!!!”" — the exact lie the modes exist to kill) and the port of the second box. **BACKPORT RIDER FIRED — instance list re-derived from disk, not trusted:** exactly two `type="search"` inputs exist across every page and shared module (`checklist-request.js` is tap-to-pick, not an instance), and the second, `av/consumables.html`, now runs the same engine with the same honest labels — indexed off the DOM so write-ins and killed rows stay searchable, rebuilt per keystroke because the item set changes under it, closest-three shown in place of a dead "No items match", `aria-live` on the label. Gate: **51 assertions, green local AND re-run GREEN AGAINST PRODUCTION** — rules 4/1/3 probed with SELF-DERIVED names on av + gc (exact full name #1 · "+ template" still #1 · one-typo rank 1), all 8 trades swept live for engine + honest label + closest-three, consumables driven end to end ("electrcal tape" → E-Tape, narrowed 1/28), mobile-watertight 320/360/390/430 ON the new closest-three state, zero page errors. Storefront unchanged — no new tool. https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- `2026-08-14` — **[AXIS:INTERFACE]** **THE DELIVERY BUTTON THAT COLLECTED NOTHING, AND THE PREVIEW THAT WAS A GENERATION STALE ON SIX PAGES** · **before:** the well was dry (0 new, 0 building) and every trade on the BUILD ORDER had a kit, so the stalest axis governed — INTERFACE, 14 lane-cycles cold. The roster ranked the supply-house / vendor edge as "the strongest unbuilt ASK edge, one page owed to nine trades." **A panel of four field lenses and two skeptics killed that premise on disk in one line:** six trades already ship that page under their own names, and `electrical/tools.js` has said *"copy it to the warehouse OR THE COUNTER"* since it landed. What was actually unbuilt was **the truck** — and `plumbing/supply-house-order.html` had shipped a **Delivery** button for four months that changed one word of the message and asked for nothing: no gate, no set location, no window, no how-it-comes-off, no who's-meeting-it, no signer. The counter lens, answering from the receiving end and with no idea we had that page open: *"a bare Delivery button with nothing behind it is worse than no button, because he taps it."* Same page, same read: **"Ordered by: your name"** with no cell on it, while all three engine-driven siblings ask for name + cell — the one document built to stop a phone call made the counter go find the number. · **after:** `shared/dropoff.js` — the jobsite delivery block as a **FIELD, not a tool**, two lines to mount, **no new storefront row**, and sticky because the answer is the same for every delivery to that job all year. Ticks for where it lands / how it comes off / when it can come, a `not before` clock (a truck at 6 when the gate opens at 7 blocks the street), text only for which stair, the gate code, who's meeting it and who signs — and **"it's an ask, not a booking"** printed in the document every time it appears, because a man who ticks *boom · not before 7 · level 2* and taps Copy can believe he has scheduled a crane. Plumbing also got the callback cell, PO split out of the "optional" box it shared with the account, and **who's picking it up** gated to will-call. Killed by the skeptics and staying killed: a per-line stock/special-order axis (a guess wearing a heading), a NO-SUBS row flag (a contractual term on a document neither company owns), a branch picker (impersonation with a shelf life) — the lead-time ask survives as one sentence, and the word is never *quote*. · **BACKPORT RIDER FIRED, and it is where the cycle's real damage was found:** sweeping every shape #1 page for the same class turned up a defect nobody could see because the OUTPUT was right — **`watch` was a hand-kept list that had to agree with a hand-written `document()`, and on four of the five engine pages it had drifted.** A charge code, a hot flag and a delivery method were in the sent text and out of the re-render, so the block labelled *"what you send"* — the one thing he proofreads — was stale until something else poked it. **10 fields across 5 pages.** Fixed in the ENGINE, not per page: it now binds every header control the house convention names, `watch` is for exceptions, and both `input` and `change` (which `shared/draft.js` had already written down three files away). · **GATES, and both are new and both were proved by reverting the fix:** `order-live-header.mjs` decides whether a field is in the document by **changing it and reading what the real Copy button puts on the clipboard** — no list of its own to drift — then re-checks each one ALONE through a real reload from a wiped device, and taps every segment button so a block that only exists in the other mode is not invisible to it (10 defects red before the fix, 0 after, 6 pages, 9 in-document controls on plumbing). `dropoff-block.mjs` drives the block the way a foreman does and asserts the OUTPUT: every chip and every typed line by value in the copied text, the ask-not-a-booking line present, the whole block **out** of the document when the mode is switched off, and everything back after a reload — plus a banned-word pass over its own chips for a capacity, a reach or a price. `mobile-watertight` **76 pages × 320/360/390/430 × default and bumped text — 0 failing**, after fixing an overflow this cycle EXPOSED rather than created (a 3-button segment with a ~200px floor in a 160px track had been safe only because it happened to sit in the left column). `no-third-party` 76/76 clean. Storefront unchanged — no new tool, no new trade, by the panel's own verdict. BACKPORT rider: **fired** (7 shape #1 pages swept; the class was the 5 engine pages + the plumbing fork). https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/supply-house-order.html
- `2026-08-14` — [AXIS:BREADTH] **TRADE #10 IS LIVE: the Concrete Field Toolkit** (6 tools) —
  promoted by the INTERFACE MATRIX rule for the third time, and this one the matrix had
  been pointing at since it was written: concrete is the ONLY unserved receiver named by
  two served trades independently (EC's sleeves/blockouts/pads/Ufer row, PC's
  sleeve-in-the-pour row), the GC's mirror row is literally "the pre-pour call", and the
  POUR is the earliest gate on FIVE of the six trade gate ladders — the one gate on a job
  that does not reopen. Before: five toolkits shipped a page asking this crew for
  something and the crew being asked had nothing. After: **Before the Pour** (pinned, the
  receiver side of that edge, with its answer-back and reconcile loop), **The Mix Order**
  (shape #1, 151 lines, and the first order page in the program that prints a ticked line
  BARE — `qtyDefault:""`, because "1 Soft ground" is the engine's own
  line-arguing-with-itself failure on the other side of the box), plus the T&M tag,
  write-up (8 docs + 2 overrides), and total package. Vocabulary from a 6-agent fan-out
  whose 25-year prune killed 64 of 215 order lines and a WHOLE CATEGORY — every admixture
  dose field — on the grounds that a dose field on a phone is a dose recommendation.
  Wired end to end: runtime TRADES, commons chip + 11 gear/10 tips rows written for it,
  UIComponents registry, deploy `paths:` + `TRADES`, persona500 manifest (10 kits, 62
  tools; `cement` DISPOSED OF as an include token — measured, it matches
  `law_enforcement_fitness_specialist`). BACKPORT RIDER FIRED, three times, all
  program-wide: the fixed-bar clipping on 10 trades + the gate assertion that catches it,
  the half-swept 44px `.rm` on 4 trades, and 60 sub-44px controls on `av/consumables.html`.
  84/84 pages pass the mobile gate at 320/360/390/430 · https://mrdirno.github.io/nested-resonance-memory-archive/concrete/
- `2026-08-14` — **[AXIS:BACKPORT]** **THE BIGGEST LIST IN THE TOOLKIT WAS THE ONE WITH NO WAY DOWN IT** · **before:** eight shape #1 pages ask a man to tick his way through a list, and their sizes read off `items.js` are `concrete/mix-order` **151 items / 12 sections** · `av/cable-list` 62 · `plumbing/supply-house-order` 53 · `framing/the-load` 44 · `electrical/pull-list` 42 · `hvac/truck-stock` 37 · `low-voltage/consumables` 35 — and the only one that could be narrowed was `av/consumables.html`, **the smallest at 28**. The refinement had landed on the page that needed it least and reached none of the seven that needed it most (§SCARS, and the completeness check that could not have found it) · **after:** `shared/pickfilter.js` + `shared/pickfilter.css`, extracted from that flagship and mounted by `shared/checklist-request.js` itself, so **all six engine pages landed in one commit**, the plumbing fork was wired the same way, and the flagship was MIGRATED ONTO IT — its own 25 lines of glue deleted, its markup and CSS untouched, the module ADOPTING `#q` / `#nomatch` / `#checkShown` so not a pixel moved. **TWO DOORS, BECAUSE THE PANEL SAID ONE WAS NOT ENOUGH.** A concrete finisher read the pages before a line was written and split the case exactly: on a parts list he already knows the word ("RJ45", "wall dogs") and typing beats everything; on a list he reads to REMEMBER he has nothing to type — *"I don't know I need a washout tub until I read it"* — and his friction is different, the sections are boxed to look like folders and **none of them folds**, so every trip scrolls past six he already handled. His ask, verbatim: *skip the scroll, don't page past nine sections to get to the tenth.* So the bar carries a typed filter AND a section picker, composing through one hide/show pass. It is a `<select>`, not the chips he asked for, and the reason is on disk: `concrete/items.js` names sections in prose — *"The walk before the mud rolls"* — and twelve of those as chips is a wall of text where the list used to be. **THE SKEPTIC OVERTURNED THE SCOPE AND WAS RIGHT:** the 2026-08-13 entry names **four** behaviours the engine lacks, not one, and shipping a strict subset of already-logged debt is the "a comment claimed the coverage" failure this book has caught twice. Filter, check-shown and the **n / total** section marker all ship (the marker reuses the `[data-n]` slot every page already styles — four pages' worth of parity, zero new CSS). The fourth, per-category **All**, is **REFUSED with a reason rather than silently dropped**: it is an ungated mass-tick, twelve of them permanently on screen, and on prose checklists ("The forget-list", 21 rows) it sends a document nobody meant to send — the section picker plus Check shown reaches the same action through one mechanism. **THREE DEFECTS FIXED ON THE FLAGSHIP BY BEING EXTRACTED FROM IT:** its write-in section vanished under a filter once it held a row (§SCARS); its "Check shown" sat on screen with an empty box, where *shown* means **all of them**, one thumb, no confirm — graded a bug by the finisher, and it now only exists while something is actually being held back, which is also the first time its label is true; and its filter box shipped at **14px**, under the 16px iOS line this book holds everywhere else, so focusing it zoomed the page the operator said must never zoom. **BACKPORT RIDER FIRED — every shape #1 page on the board, none left behind:** 6 engine pages + the plumbing fork + the flagship = **8 of 8**, and the class was re-derived from disk rather than trusted. One claim I brought to the panel was **KILLED as false**: two pages looked like they carried a dead 612-line engine include, and the skeptic proved the string only ever appears in prose comments — no include, no defect, not built against. **GATE: `tools/toolkit-gates/pickfilter.mjs` is new — 8 pages, 104 assertions, and PROVED RED BY FOUR MUTATIONS** before being trusted (hide rule deleted · hatch guard deleted · check-shown ungated · flagship back to 14px). It reads what the browser COMPUTED, never what class is on; every probe word is SELF-DERIVED from the page's own item names; it ticks a line, filters it off the glass and reads the real clipboard to prove **hiding is a view and ticking is the order**; and it re-measures overflow at 320/360/390/430 **while narrowed** — the widest that bar ever gets and a state `mobile-watertight` cannot reach, because that gate measures a page as it loads. `mobile-watertight` 84 pages × 4 widths × default and bumped text **0 failing**, `no-third-party` 84/84, `order-live-header` 7/7. Storefront unchanged — no new tool, no new trade. https://mrdirno.github.io/nested-resonance-memory-archive/concrete/mix-order.html
- `2026-08-14` — **[AXIS:DEPTH]** **THE ONE COLUMN A MAN RECONSTRUCTS FROM MEMORY TWO HOURS LATER, WRONG** ·
  **before:** the well was empty and no trade was owed, so the stalest axis governed. Every
  trade that closes a system and watches a gauge writes the same paper afterwards — at the
  shop, from memory — and **the times are the part that gets invented**. 62 tools, none of
  them touched it. **after:** SHAPE #6, THE HOLD TEST — a row log whose add-row bar is a
  **stopwatch**. `shared/holdtest.js` + `shared/holdtest.css`, built as an engine on its
  FIRST instance because the SECOND config shipped in the same cycle:
  `hvac/evac-record.html` (pump on · valved off · reading · off test, the roster's "best
  sleeper on all five rosters") and `plumbing/its-holding.html` (on test · reading ·
  **somebody looked at it** · off test — the roster's reframing as *the caption for the
  gauge photo*, carrying system, grid, medium and witnessed-by). The `zero` mark is #2 for
  HVAC and #1 for plumbing: one flag, not a fork. Every stamp is an **absolute epoch
  millisecond** — verified live, a cold reload resumed at `00:32:45` from the real
  isolation stamp and kept ticking — and a hand-corrected time is branded **time typed in**
  on the page and in the document, permanently, with the honesty clause rewriting itself.
  **No target, no verdict, and the engine refuses to know which direction is good**, because
  a vacuum rises when it leaks and a pressure test falls. **BACKPORT RIDER FIRED, and it
  found the widest-blast-radius defect of the cycle:** the sticky nav is 62px at every
  width and `scroll-padding-top` was unset site-wide, so every `scrollIntoView({block:
  "start"})` — including both of `shared/docspec.js`'s, i.e. the Write-Up Setup page on all
  ten kits — hid its target's first 62px behind the nav. Fixed in `shared/toolkit.js` where
  the bar is born; verified live on hvac, plumbing, electrical, roofing, concrete, creative
  and gc. Two scars written (the sticky hole; clearing storage then reloading tests
  nothing). Mobile gate: 0px overflow, no sub-44px target at 320/360/390/430 with the
  editor open and a 60-char unbroken token in a note. Deploy assert added: a page that
  loads `holdtest.js` and never mounts it now fails the build ·
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/evac-record.html ·
  https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/its-holding.html

- `2026-08-14` — **[AXIS:COMMONS] A SYNONYM THAT ONLY SITS IN A LIST DOES NO WORK, SO THE
  NAMES WERE NOT SHIPPED AS A LIST** · **before:** the commons had two surfaces and rung 2
  had been ranked, railed and left unbuilt, because the lens that voted it down was right —
  this project had met the translation problem twice and solved it both times as routing
  inside a tool, and a glossary page routes nothing. Separately, the two lists were **126
  gear rows and 135 tips**, second and third biggest on the whole site, and neither had any
  way to narrow them · **after:** `commons/names.html` is surface #3 — **91 rows, one OBJECT
  under every name the field says for it**, seeded for all ten trades in its first commit
  (9 universal; 9–15 written for each trade) — and the rows are an **ALIAS INDEX** the other
  surfaces search *through* with `shared/find.js`. Type **stinger**, **marrette**, **zap
  strap**, **tick tracer**, **Stillie**, **knuckle buster** into the GEAR list and the right
  row comes up; none of those words is anywhere in `gear.js`. **39 of 126 gear rows are now
  reachable by a word that is not on their page**, the deploy COUNTS that join through the
  engine's own exported `Commons.aka` so a rename cannot quietly un-hook it, and
  `tools/toolkit-gates/commons-names.mjs` derives a probe from **every alias that is not
  already a substring of the gear page — 134 of them, all green on the real page.**
  **THE PAGE'S BEST ROW IS A COLLISION IT DID NOT DUCK:** "stinger" is an extension cord on
  a set, a concrete vibrator in a pour, and a welder's electrode holder — and a concrete
  reader meets the first two on the same screen, so the vibrator's guard names both instead
  of the row being cut. Nine seeded passes and three adversarial lenses: **98 candidates →
  7 cut, 33 patched.** All three lenses independently found the same three same-object id
  collisions; two more came out of the AV pass duplicating the low-voltage pass. **THE RAILS
  LENS FOUND A CLASS, NOT A LIST:** `k:"reg"` prints as *you might hear*, which promises a
  PLACE, and **nineteen aliases** named a cohort — *some crews*, *older hands*, *overseas* —
  so it was flipped uniformly in one pass and the gate now bans the phrases outright rather
  than trusting a place allow-list that would reject the next real region. Four rows were
  renamed because the ORDER NAME may not carry slang or two objects (rail 1/2), and where
  the rename broke the fold-join, **the row takes the gear row's ID so the routing holds** —
  criticism taken, suggested wording not. `bounce-board` and `wire-scrim` died because their
  real vocabulary is four objects and a rating, and neither can be said inside the rails.
  **BACKPORT RIDER FIRED TWICE, both one layer out from a fix that already shipped:**
  (1) `COMMONS_TRADES` was centralised in 2026-08-11 so the framing-chip rot could not
  repeat — and each surface then spelled the same ten trades out AGAIN by hand in its own
  `window.FEEDBACK` block, so **concrete, trade #10, chip present and 21 rows behind it, was
  in neither copy**; `shared/feedback.js` REQUIRES an area for a bug or an improvement, so a
  concrete finisher who found one of his own rows wrong could only file it against another
  man's trade or close the box. Swept all ten trades and `shared/` — the class is confined to
  the commons, because trade pages take their well from the toolkit engine, which already
  derives. Both copies deleted for `Commons.areas()`, and the deploy now fails any commons
  surface whose HTML hand-lists them. (2) The pickfilter backport of 2026-08-13 reached every
  trade's list page and skipped the commons for the same reason — it is not a trade — leaving
  the site's second and third biggest lists unnarrowable; **all three surfaces now carry the
  search**, and `names.js` is deliberately NOT loaded on the tips because 0 of 135 tips name
  an object by its generic, so the tag would have been a routing claim with no work behind
  it. The deploy's per-surface coverage gate now parses `COMMONS_SURFACES` out of the shipped
  engine, so surface #4 is floor-gated the day it lands with no edit to the CI. Gates:
  **commons-names 287/287, commons-bag 27/27 across three surfaces, mobile-watertight
  320/360/390/430 default and bumped on all three, no third-party requests, zero page
  errors**, and the job driven end to end — ticked under one trade, searched a word from
  another, and the paste led every line with the order name. Storefront unchanged — no new
  tool, no new trade ·
  https://mrdirno.github.io/nested-resonance-memory-archive/commons/names.html

- `2026-08-14` — **[AXIS:COMMONS] THE WORD THAT MEANS THREE THINGS, ON A PAGE THAT ONLY HAD
  ONE OF THEM** · **before:** the name table shipped green an hour earlier, and driving the
  LIVE gear list found the one thing every gate agreed was fine: **"zap strap" answered
  "Matches: Wire strippers"** with no hedge, because the index can only route to objects
  that surface CARRIES and cable ties are consumables. Full coverage on the surviving token
  reads as an exact hit, so the honest-label branch never ran · **after:** when the name
  table knows a word this page cannot answer, the page **hands him off** — the object named,
  above its own guesses, with a link. And a LOADED word always says so: **"snake" is an
  audio snake, a hand drum auger and a fish tape**, "mud ring" and "plumber's tape" are two
  things each, and the notice fires **even when the page can answer some of them**, because
  a partial answer to an ambiguous question is the same lie in a smaller coat — which is
  exactly what the new gate caught when the first cut suppressed it. The gate derives its
  hand-off probes the same way it derives its routing probes: from every names row the gear
  list has NO row for. Also fixed: the fold broke on `'`, so "plumbers tape" and "plumber's
  tape" folded apart and one of the two objects vanished for anyone typing the way people
  type. **BACKPORT: the hand-off is in the shared engine, so it is live on all three commons
  surfaces at once, and surface #4 gets it for free.** Gates: commons-names **308/308**
  (134 routing probes + hand-off probes), commons-bag 27/27, mobile-watertight
  320/360/390/430 on all three, zero page errors ·
  https://mrdirno.github.io/nested-resonance-memory-archive/commons/

- `2026-08-15` — **[AXIS:DOCS]** **THE PATH SEARCH DUMPS YOU INTO HAD ONE SENTENCE FOR EIGHTY DOCUMENTS** · **before:** every write-up in the library carries a hand-written `omit` — the field this book calls the highest-value one in the whole toolkit, the line whose absence loses the back-charge meeting. The **custom path** — what a man reaches when what he has to write is not in the list, on all 9 trades — answered it with **one hardcoded sentence**, the same string in all nine, for all five families, and it claimed to be trade-specific ("on almost every document in **this trade**"). `facts` was three generic words feeding the AI's own pre-flight check, identical for a near-miss, a delay letter and a set of minutes; `why` was the family PICKER's blurb read out as a purpose statement; `secondary` was empty where every library document offers one or two. · **after:** five **OMISSION CLASSES**, each demanding a concrete artefact — a date · a name · a before-value · a location · a named gap — **derived by classifying all 80 shipped `omit` lines**, not by taste, with the per-family counts in the code beside the table. `facts`, `why` and `secondary` now come from the family, the same way `sections: f.spine` always did. **THE CORPUS OUTRANKED THE PLAN TWICE.** The rung was recorded as FOUR classes; classifying the corpus put *"what you did NOT do"* level with the biggest and made it the most common thing a RECURRING write-up misses ("where you COULDN'T work" · "the idle half of the job"), so it shipped as the fifth. And the seed was first written as THREE-per-family off the MAX of the five documents that ship a list — the MODE of all eighty is **one**, 75 to 5, which is also the word in the heading. Seeded to one, four one tap away, **because whatever ships pre-ticked is what a man in a hurry keeps**. **AN ADVERSARIAL PASS FOUND A LIVE DEFECT ON A TRADE THIS CYCLE WAS NOT TOUCHING:** the PROSE heading over multiple omitted lines pluralises; `LOCKED[0].h`, the heading inside the **OUTPUT FORMAT** — the part that becomes the document somebody else reads — never did, so framing's five multi-omit documents have been shipping **"THE ONE NOBODY WRITES DOWN" above three bullets** since arrays landed. Confirmed against the real page before a line was changed, then fixed at print time. **BACKPORT RIDER FIRED — swept, not assumed:** the engine is shared so all 9 write-up pages take the fix in one change; the multi-omit class was re-derived from disk (exactly framing's 5, all now correct); no library document ships an empty `omit`, so the empty-red-box path was unreachable until ticking to zero made it reachable — it now says the true thing instead of painting a warning frame with nothing in it. **Swept and NOT fixed, named so it is not lost:** `creative` is the one trade with no `docs.js` and no write-up page at all — a whole-trade DEPTH gap, not this class. **THE GATES GREW, AND ONE WAS PROVED BY NEGATIVE CONTROL.** `docspec-config.mjs` now drives the custom path through **all five families** (four were never exercised — harmless while they all emitted the same string, load-bearing the moment each has its own seed), and asserts: exactly one class seeded · seeds differ across families · the dead sentence never returns · unticking all says so · ticking all pluralises the shipping heading · and the class contract itself, that every line truncates under `shortOmit()`, which fails **silently**. `mobile-watertight.mjs` grew `REVEALS` — the second time a control that only exists after a tap escaped a green gate — re-loading per state and re-running every measurement inside it; **proved by pointing the reveal at a control that does not exist and watching it fail at all four widths.** Gates: **docspec 9 trades / 149 checks / 0 failing, and RE-RUN GREEN AGAINST PRODUCTION** · **mobile-watertight 87 pages × 320/360/390/430 × default and bumped, 0 failing**, the tick list re-measured in its revealed state, and the write-up pages re-run green against production too · the live page then DRIVEN end to end on hvac — a document that is not in the library ("Freeze-stat trip investigation"), incident family, seeded class correct, the per-family facts and purpose reaching the block, the plural heading correct with two ticked, zero page errors · eyes on the real page at 320 and 390, which is how the artefact badges were caught wrapping to four lines with every number green. **A SECOND, INDEPENDENT CLASSIFICATION of the same 80 lines, run blind to the five, agreed on 4 of the 5 family seeds and forked on `incident` — written into the doctrine above with the fork intact rather than smoothed away.** Storefront unchanged — no new tool, no new trade. https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- `2026-08-15` — **[AXIS:INTERFACE]** **THE DOOR THAT DOES NOT OPEN, AND THE TICK THAT PRETENDED IT HAD A PERMIT** · **before:** the well was dry (0 new, 0 building, every trade) and no family was owed, so the stalest axis governed — INTERFACE. **The ranked roster was WRONG, and step 0 of the ship loop is the only thing that caught it:** it still ranked *THE THIRD MESSAGE* as "now the interesting one" with a full design brief, and that rung had shipped four days earlier as `shared/reconcile.js`, 38KB, loaded on nine `rough-in-request.html` pages, implementing every constraint the entry named. The rung actually unbuilt was #2 — **sub → owner direct**, the access/escort/badge/after-hours ask, filed as *"small, and nobody owns it"*. It was right about the second half. · **after:** `<trade>/getting-in.html` on **all ten kits including creative** — one page file, ten `TOOLKIT_GETIN` configs, shape #2. The first tool in the program aimed at a party that is **not another trade**, and the only boundary where being wrong leaves four men and a truck of gear at a locked door instead of costing an hour. **A FOUR-LENS PANEL NEARLY KILLED IT, CORRECTLY:** the skeptic, handed this book's own rules as weapons, showed that every noun in the proposal — escort, badge, freight, hot work, power-down — already has an owner and a **numbering authority** on the building side, which §THE SYSTEM OF RECORD forbids competing with. **THE HANDBACK RULE IS WHY IT SURVIVED, and it is the cycle's real invention:** dropping those was the worse failure (undisclosed hot work near a detector is the fastest route onto a permanent do-not-use list), so **none of them is a status** — every permitted activity ends in a question aimed back at the man who owns the process, *"we have to touch the fire alarm (tell me who puts the panel on test — we don't)"*. That is §THE SYSTEM OF RECORD applied one level down, to a checkbox, and `getting-in.mjs` asserts it as a RULE so a later cycle cannot rewrite one into *"fire alarm coordinated"* and call it a tidy-up. **KILLED AND GATED AGAINST:** lockout/tagout and confined space · a fire-watch tick · ICRA class I–IV logic · any generated reference number, status field or approved toggle (this page has no channel back and will never know) · insurance limits and policy numbers · a risk score computed off the ticks. **NAMES SPLIT THE PANEL THREE TO ONE AND BOTH HALVES WERE RIGHT** — the receiving lens gets no badge cut without full legal names days ahead; the skeptic showed the modal use of a Copy button is a paste into a crew group chat. So names are OPTIONAL rows, DOB/SSN/licence/badge number are not fields and never will be, Clear takes the crew and leaves the sender block, and the document spends a line handing the badging form back to HIS system — **only when names are actually on it**. **THE HEADING IS THE ASK**, because the receiving lens wrote unprompted that he approves from a lock-screen preview: `ACCESS REQUEST — Sat, Aug 22 · 6pm–2am` / `Bishop Ranch 3 · Nights all week`, and **deliberately no "asked on" stamp** — the first live read of the real document put two different dates on lines one and two, which is the exact ambiguity the page exists to kill. **THE ENGINE GREW THREE ADDITIVE PRIMITIVES**, all no-ops for the eleven older note pages: `kind: "date"` (both field lenses ranked *"tomorrow"* first among things that cost a day — state keeps ISO so it restores, the document prints the **weekday** so a typo in the number has something to disagree with) · `u.doc(id)` on `subline`/`titleSuffix`, closing a gap the engine's own spec pass had already flagged · `data-f` on every field wrapper, so a gate drives a page by the id the config uses instead of matching label prose, **because matching on words means a gate silently stops testing a field the day somebody improves its label** — the same class as a hand-kept watch list, one layer out. **CREATIVE IS NOT A RESKIN:** its production lens argued the two documents should not share an engine, and its own principle — *share the atoms, not the assembly instructions* — is exactly this program's architecture, so it took the engine and got its own document: haze finding the fire alarm (handed back the way hot work is), what ends up on camera, furniture that goes back exactly as found, generator exhaust against their intakes, cable stopping a fire door closing, the real headcount including client and cast, and **asking THEM to hold their own noise during takes — the one disclosure in the whole program that runs the opposite direction**. It is called Getting In, **not "Shoot Day Confirm"** as the creative roster had it: *confirm* is the precise defect the page prevents. **BACKPORT RIDER FIRED, and it is the order engine's class asked of shape #2 in shape #2's own terms:** `note-live-fields.mjs` changes ONE field alone on a wiped device and requires the copied text to CHANGE, with `docSkip` exempting a field **BY NAME read out of the page's own source**, so an author cannot silence the gate without saying in the config that the omission was deliberate. **246 in-document fields across 20 pages, 0 defects** — shape #2 cannot have the *drift* half of that bug (one delegated listener on the whole form, no second list to fall out of step) but it can still drop a field through a misspelled `kind` (BUILDERS returns undefined and the field vanishes with no warning), a colliding `id`, or a `docSkip` copied in from another page, and that is now asserted rather than assumed. **SWEPT AND NOT FIXED, named so it is not lost:** `shared/dropoff.js` is mounted on ONE of the eight order pages — the other seven are pure `checklist-request.js` configs and **that engine has no fulfilment axis at all**, so there is nothing for `Dropoff.mount` to attach to; it is an ENGINE rung, not a rider, and it is now the strongest unbuilt INTERFACE work. **SCAR WRITTEN — A ROADMAP IS NOT A RECORD:** whoever ships a rung strikes it in the ranked list in the same cycle, and strikes it with what was LEARNED, not a checkmark. Gates: **getting-in 10/10 pages** (every value found by value in what the real Copy button put on the clipboard, every ticked option's handback present, the heading carrying date + window, the ask-not-a-booking line, the names-only line appearing only with names, Clear taking the crew) · **note-live-fields 246 fields / 20 pages** · **mobile-watertight 97 pages × 320/360/390/430 × default and bumped text, 0 failing** · **no-third-party 97/97**. Storefront: **10 entries added** to `fieldToolkits.ts`, one per trade, placement verified per-trade and the file re-parsed — P5 pushes it. https://mrdirno.github.io/nested-resonance-memory-archive/av/getting-in.html

- `2026-08-15` — **[AXIS:BREADTH]** **TWO TRADES HAVE BEEN COUNTING DOWN TO A NUMBER NOBODY
  PUBLISHES** · **before:** the well was dry (0 new, 0 building, every trade) and the roster's
  BUILD ORDER was exhausted, so the stalest axis governed — BREADTH, eight lane-cycles cold.
  `electrical/items.js` has shipped the milestone **"Before CMU caps out"** and
  `plumbing/items.js` **"Before block goes up"** since those kits landed, each binding an ask
  to it — *"Set my boxes as you lay it" · "Don't grout the cell I'm in" · "Sleeve laid in as
  you go up" · "Knock-out at my paint mark"*, twelve spec lines in all — and the crew being
  asked had **no page in the program at all**, while nothing anywhere published the course
  those two trades were counting to. · **after:** **MASONRY, trade #11**, whole: hub · trade
  config · registry · items.js · docs.js · credit ledger · 7 tools, pinned on
  `wheres-the-wall.html`, which is that number. Wired end to end and not merely staged —
  runtime TRADES, commons chip with **12 gear, 12 tips and 8 names rows written narrowly for
  it**, site-root registry, deploy paths + TRADES, persona500 manifest (11 kits, 81 tools).
  **THE PROMOTION RULE STOPPED DISPOSING AND THAT IS THE CYCLE'S REAL FINDING** — re-tallied
  off all ten shipped `items.js` files the count nominates **steel** (4) over masonry (3),
  and the lens that declared *"no taste was required at any step"* had missed
  `concrete/items.js` `{v:"steel", label:"Steel erector"}`. Steel was then killed by
  §THE INTERFACE's own prune (*"a special-inspection record"* — the bolt-up log and the weld
  map ARE that record, and it is steel's centre, not its edge), and ceilings by a sentence
  `concrete/trade.js` had already written while promoting trade #10: *"a wall can be cut, A
  CEILING CAN BE PULLED"*. From #11 the rule nominates and the record disposes; the dissent
  (masonry is the smallest population and is **receiver-heavy, ask-light**) is in §MASONRY at
  full strength, which is why its `rough-in-request` is deliberately shorter than concrete's
  fourteen rungs instead of padded to match. **THE ACCENT IS A MEASUREMENT, NOT A TASTE:**
  brick red cannot clear the 7:1 nav bar at ANY lightness that is not a pastel (hue 352,
  measured: L50 3.64 · L60 4.02 · L70 5.12 · L75 6.03), so the colour went to the trade's
  TOOL — the line — at hue 75.0, the middle of the widest genuinely chromatic arc; the stale
  hue list nearly stopped that by recording the commons at hue 90, which is a 4%-saturation
  GREY. **THE INVERSE-CLAIM GUARD is the trade's contribution to the program:** a list that
  names the walls nobody may touch WILL be read as clearing the ones it did not name, so the
  don't-touch axis has no "it's fine" value at all and every copy carries *"A wall not named
  here is a wall I have said nothing about."* **DRIVING THE REAL DOCUMENT FOUND TWO DEFECTS
  THE CODE READ FINE:** the most actionable line came out `Grid C 4 to 9 · course 14 · East
  elevation · top course` — four items, one separator, no way to tell where a wall ends — and
  the held copy said HELD ON SOMEBODY ELSE twice in one header line. Both fixed at print time.
  **BACKPORT RIDER FIRED TWICE, both program-wide and neither of them mine.** (1) `gear.js`
  shipped **two different objects under one id** — "Inverted marking paint wand" and "Marking
  paint" both `marking-paint`, both visible to a GC — and the engine keys picks BY ID, so
  ticking either rendered BOTH checked, put BOTH in the bag document, and made it impossible
  to remove one without the other. Renamed, and `commons-bag.mjs` now asserts row-id
  uniqueness on every surface — **proved by negative control, which is how I found that my
  own first cut of the assertion pushed the wrong shape and could never have fired.**
  (2) `mobile-watertight.mjs` had never measured **shape #3's pencil-open state on any of the
  26 row-log pages in the program** — a fresh row log is an add bar over an empty list, and
  the editor where a man changes what is holding a wall only exists after two taps. The
  reveal now drives it generically, and its page set is **read off what each page LOADS**
  rather than a name list, because the first cut carried a regex of names and missed
  `low-voltage/device-checkout.html`, 25 of 26. **Coverage proved by negative control: 104
  sentinel reports = 26 pages × 4 widths.** Gates: **wall-state 32/32** (new, and the
  inverse-claim assertion negative-tested by deleting the line and watching it fail) ·
  **mobile-watertight 106 pages × 320/360/390/430 × default and bumped, 0 failing, now
  including every row log's pencil state** · **rowlog-restore 26/26** · **note-live-fields
  271 fields / 22 pages** (which caught the real gap that `masonry/items.js` was missing the
  `why`, `notin`, `pics` and `classes` option lists three tm-tag fields consume) ·
  **docspec 10 trades / 167 checks** · **commons-bag 411 states** · **commons-names 321
  checks** · **no-third-party 106/106** · **menu-reachability 721 checks**. Storefront: one
  entry, 7 tools, accent identical to `trade.js`, `mason` tokens measured precision-1 against
  all 1,027 personas — P5 pushes it.
  https://mrdirno.github.io/nested-resonance-memory-archive/masonry/

- `2026-08-15` — **[AXIS:BACKPORT]** **THE TRADE WHOSE WEEK IS WRITING WAS THE ONE WITH NO WRITE-UPS** · **before:** the well was dry (0 new, 0 building, 23 shipped, every trade) and no family was owed, so the stalest axis governed — BACKPORT. The gap was not on any roster and took one command to find: grep every trade for every `shared/*.js` it loads. Ten trades carry **docspec · package · reconcile · find**; **creative carried none of the four** — `toolkit`, `note`, `rowlog`, and that is all, 3 of 12 shared modules — while the DOCS axis shipped work on the other nine. `creative/trade.js` NAMES the docspec among the five engines it inherits (*"this program owns five document ENGINES — the checklist→request, the note, the row log, the reconcile and the docspec"*) and shipped with two. The previous cycle had already swept it and named it (*"`creative` is the one trade with no `docs.js` and no write-up page at all"*); this is that debt paid. · **after:** `creative/docs.js` + `creative/write-up.html` + one registry line — **13 documents live**, 5 written for this trade (the cut note that goes out with every version · where the media is · what they approved and on which cut · handing a project to another editor · the recap after the kickoff call) and **all 8 surviving shared documents re-addressed**, because a freelancer who reads *"to: the GC super"* has been told in three words that the kit was not built for them. **THE FIRST `drop` IN THE PROGRAM — nine trades and none ever declared one — and the third drop is the finding:** `change-request` is dropped because this trade **already SHIPS that document as a page**. On the ten construction kits the pair coexists because a T&M tag is a signed TICKET with hours and materials on it, structurally a different artefact from a change NARRATIVE; here they are one artefact with two front doors, and §THE GATE says ONE job per tool. First time a shipped TOOL has displaced a shared DOCUMENT, which is a real measurement of how far the shared library actually carries into a trade that is not construction. **THE GATE'S DELTA ROSTER CAUGHT THE AUTHOR ON THE FIRST RUN:** `brief-recap` is minutes-shaped and does NOT recur, so the second one would have been written as an update to a different conversation — on the one document whose whole purpose is to be read months later to settle what was in scope. `standalone: true`, the engine's documented opt-out, second instance in the program. **BACKPORT RIDER FIRED — AND THE PANEL KILLED MY OWN FIX.** Swept all 11 trades for the same class; one other candidate surfaced, the SHARED `toolbox-talk`, and an adversarial pass reading the code rather than the argument **REFUTED it on mechanism**: `deltaOf()` has two behavioural call sites, attendance and topic are emitted identically on both branches (`WHO WAS THERE` is an always-printed spine heading, `facts` is printed unconditionally by VALIDATION), so the change bought nothing — while DELETING *"carry every unresolved open item forward, with the date it was first raised"* and the 48-hour escalation on the one document whose omitted line is *"what was raised BY the crew"*, across all 10 inheriting trades. **Not shipped. A rider that fires is not a rider that ships.** **AN ADVERSARIAL FAN-OUT (4 lenses: refute · safety · voice · product-coherence) FOUND SIX DEFECTS IN THE FIRST DRAFT, ALL FIXED BEFORE SHIP:** a **deemed-acceptance clause** (*"I'll work to it as written if I don't hear back"*) in the one file whose own rails ban consequence clauses · a **bare statement of legal effect** imported from construction (*"the clock only starts when somebody is told in writing"*) into a trade with no notice clause · **five overrides that declared `name`/`to`/`why` and INHERITED** `secondary: ["a one-paragraph version to paste into the GC's change form"]`, `from: "the lead on the job"` and an `omit` ending *"worth nothing in a back-charge meeting"* **straight into the pasted block, while the file's own header claimed the addressing was fixed** (§SCARS) · `media-report` prescribing a second copy its own `note` forbids · `meeting-minutes` the ONE shared document reaching this trade untouched, as *"Coordination Meeting Notes"* with **"oac"** in its search terms · **19 vocab pairs that corrected nothing** (*"rough cut -> rough cut"*) under the heading *"the ones my phone gets wrong"*. Two shipped-tool COLLISIONS were caught the same way and fixed in words, not by deletion: `delay-notice` carried **"waiting on"** in its `aka` — the name of a shipped page — and `look-ahead` had borrowed that page's own hook sentence verbatim. And `trade` was **"creative production"**, a services-page category nobody says; it now emits *"we do video work"*. **SWEPT AND NOT FIXED, named so it is not lost:** the engine's `Office / PM contact` default field label is a shared string that reads wrong for a one-person shop but right on ten construction kits — engine work, not a config fix; and **every trade's nav brand clips to one letter at 390px** (`clientW` 24px on creative, roofing and electrical alike) while `creative/trade.js` reasons in prose that *"'Electrical' (ten) is the measured worst case and fits"* — a claim the live page contradicts on all 11 kits, pre-existing and owed its own cycle. **THE ROSTER LESSON, ratcheted into §CREATIVE:** the panel that ranked this trade was asked what to BUILD NEW and answered well; **nobody asked what it was OWED**, and a roster of ideas has no column for a sibling's engine you never inherited. Run the module-adoption grep before ranking anything, forever. Gates, all re-run GREEN AGAINST PRODUCTION: **docspec 11 trades / 182 checks / 0 failing** locally and **14/14 on creative against the live site** · **mobile-watertight `creative/write-up.html` at 320/360/390/430 × default and bumped, live** · **no-third-party 107/107** · **menu-reachability 728 checks / 104 pages** · the MERGED library walked field-by-field for construction routing (the only check that could see the inheritance leak) · and the live page driven at 390px end to end — picked a document, block 12,354 chars, omit line present, *"we do video work"*, zero GC strings, zero page errors, zero overflow. Storefront: one line added to `creative`'s `tools[]` in `fieldToolkits.ts` — P5 pushes it. https://mrdirno.github.io/nested-resonance-memory-archive/creative/write-up.html

- `2026-08-15` — **[AXIS:BACKPORT]** **THE KIT YOU WERE STANDING IN WAS ONE LETTER AND AN
  ELLIPSIS** · **before:** the well was dry (0 new, 0 building, 23 shipped, every trade) and
  no family was owed, so the previous cycle's swept-and-not-fixed note governed: *"every
  trade's nav brand clips to one letter at 390px … pre-existing and owed its own cycle."*
  Measured rather than taken on trust — playwright over 11 trades × hub/tool × 320/360/390/
  430: **27 of 88 states rendered the trade word CUT**, and on a TOOL page at 390px the word
  got **24px of the 74–111px it wanted** — `/electrical/` read "E…", `/low-voltage/` "L…",
  `/plumbing/` "P…". At **430px, a big phone, seven kits were still cut.** Cause: the bar
  degraded on a GUESSED breakpoint (everything at 380px), so above that line nothing could
  give up anything and the bar took what it needed out of the one flex child that can
  shrink — the trade's own name, quietly, behind an ellipsis. · **after:** the ladder is
  MEASURED per page per width — two forced layout reads before the first paint, then a
  ResizeObserver on the BAR (not the window, because the OS text size changes the answer
  without the window ever resizing), giving up the CTA's three-word tail first and the trade
  word last, which is the order this file already argued for and never actually performed.
  **0 of 88 cut; 77 of 88 now render the full word where 17 did**; the 11 that still hide it
  are genuinely out of room, and `/av/` and `/gc/` keep their word at 320px where the old
  breakpoint hid every kit's whether it fitted or not. **BACKPORT RIDER: FIRED BY
  CONSTRUCTION** — one shared runtime, all 11 trades, 108 pages, same commit. **THE GATE
  HAD A HOLE AND TWO NEW ASSERTIONS CLOSE IT:** mobile-watertight measured overflow, tap
  targets, the fixed bar's height, its clipped children and what it covers, and passed every
  page of every trade while this shipped — five correct measurements, one shared blind spot,
  and the blind spot was the only element in the toolkit ALLOWED to shrink. Now asserted
  (hiding a word is honest, half a word is a lie), and negative-tested against the pre-fix
  runtime. **THE FIX THEN BROKE THE MENU, WHICH IS THE MORE USEFUL HALF:** a wider brand
  pushes the Tools button right, the dropdown hangs `left:0` off it at `min-width:250px`, and
  it ran off the glass on ten trades — caught by `menu-reachability`, NOT by the gate that
  named the original bug. Clamped, in two attempts that are both now §SCARS: written first
  against `innerWidth` (which under mobile emulation GROWS to cover the overflow, so it
  corrected by exactly the amount that preserved it) and then ordered after the max-height
  read (which consumes `innerHeight`, inflated by the browser ZOOMING OUT to fit the very
  panel that was overflowing — fixing the width left the menu 47px too tall). The Tools
  menu is now a mobile-watertight REVEAL, sampled per trade. Gates: **mobile-watertight 108
  pages × 320/360/390/430 × default and bumped text, menu open — 0 failing** ·
  **menu-reachability 735 checks / 105 pages PASS, zero horizontal overflow** · brand
  re-measured **against production: 0 of 88 cut**.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/

- `2026-08-15` — **[AXIS:DEPTH]** **THE LIST A MAN STOPS OPENING IS THE ONE MISSING THE LINE
  HE ORDERS FIRST** · **before:** DEPTH was the stalest axis at 8 lane-cycles, and the rung
  was not a matter of taste — `masonry/tools.js` shipped last week carrying a comment saying
  what was NOT in that commit and why. Three independent in-trade panels named the afternoon
  yard call unprompted; the 20-year prune ranked it first; it was held because *"half a yard
  call is worse than none."* · **after:** `masonry/yard-call.html` — **62 lines over seven
  sections**, the NINTH instance of shape #1, engine untouched. **Three mechanisms the other
  eight order pages do not have: (1) THE UNIT OF ISSUE IS ATTACHED TO THE NUMBER** rather
  than offered as a select — a bare number gets the yard's own word ("6 cube", "40 bags", "1
  bundle") and words he typed himself are left exactly as typed ("half a cube"), because the
  tool must never re-count a man's order and a unit select on 62 lines is 62 taps nobody
  makes. **(2) THE MESSAGE CLOSES ON WHAT IS NOT ON IT** — the failure a yard call dies of
  is an ABSENT line, so a line with no count and a heavy line with no side are named to the
  yard. **(3) THE RUN** — face units come out of a run and the colour moves run to run, so a
  per-line MATCH flag, a header passthrough, a gathered match list, and a call-out when one
  exists without the other. Never a lookup: we hold nobody's lot numbers. **A THREE-LENS
  ADVERSARIAL PANEL (safety · trade-voice · product-coherence) FOUND NINE REAL DEFECTS IN
  THE FIRST DRAFT AND ALL NINE ARE FIXED**, the sharpest being: **"THE LULL" printed as a
  sub-line in the one file whose own header bans that trademark by name** (and "Mortar net"
  one section down, which had survived the de-branding pass that fixed the wire two lines
  above it) · **ten block shapes and NO CORNER** — the first line of a real takeoff — while
  HEADER BLOCK, which veneer ties replaced decades ago, was on the list · **no silo**, which
  is how mud arrives on anything with real square footage · **joint reinforcement by the
  ROLL** when it is welded 9-gauge in straight lengths, with the sub-line hedging while the
  code committed to the wrong one · **the run silently discarded** when nothing was flagged
  MATCH · **write-ins treated as catalogue rows** by three separate checks · and **"block
  and no mud" printed in the OUTGOING MESSAGE**, which is a guess about a man's intent and
  becomes noise the yard learns to skim — moved to the glass, because the tool does not get
  a vote on what he orders. **BACKPORT RIDER: FIRED, and it found nothing to carry** — the
  unit-attach, the absent-line close and the MATCH flag are all NEW mechanisms with no
  sibling instance to sweep; they are written into §MASONRY and the private roster as what
  the NEXT order page should steal rather than re-derive. Gates: mobile-watertight (live and
  local) · order-live-header 8 pages · pickfilter 9 pages / 117 assertions · no-third-party
  108 pages · **and the page driven end to end at 390px AGAINST PRODUCTION: 20 assertions,
  0 page errors**, covering the unit attach, the words left alone, the match list, the
  inverse run case, both write-in exemptions, Clear and start-from-last. Storefront: one
  line in `masonry`'s `tools[]` in `fieldToolkits.ts` — P5 pushes it.
  https://mrdirno.github.io/nested-resonance-memory-archive/masonry/yard-call.html

- `2026-08-16` — **[AXIS:COMMONS] THE COMMENT EXPLAINING WHY THE TAG WAS ABSENT IS THE REASON
  A GREP NEVER CAUGHT IT** · **before:** `commons/tips.html` did not load `names.js`, so on one
  of three commons surfaces the alias index was dead and the cross-surface HAND-OFF never fired
  once. The omission was **deliberate and well-argued**, in a comment sitting exactly where the
  tag would go: the index JOINS on an object's generic name, a tip is a sentence, and 0 of 147
  tips carry one — re-measured this cycle, still 0, that half was never wrong. It became wrong
  the day the hand-off landed in the shared engine, because the hand-off needs **no join**: it
  routes a man who typed a word this surface cannot answer to the table that owns it. **The zero
  join is precisely what makes tips the surface most likely to be handed such a word, and it was
  the only one with no way out.** Measured on the shipped page, 24 probes over the 404 words the
  commons knows: **11 dead-ended** (*stinger · snake · Channellocks · lav* → "Nothing on this
  page goes by that") and **13 came back CONFIDENTLY WRONG** — *"Teflon tape"* matched a tip
  about tape and the page said **Matches**, the exact `zap strap → Wire strippers` failure the
  hand-off exists to kill, replayed on the surface the fix never reached · **after:** all three
  surfaces route; *marrette* → **He Means Twist-on wire connector**, *snake* → **Three Things Go
  By That**, and `qwertyuiop` still hands off to nothing, because a guess is not a hand-off.
  **THE GATES WERE GREEN FOR TWO DAYS AND COULD NOT HAVE BEEN OTHERWISE:** the deploy counted the
  join by loading all four data files into **one synthetic window**, where `names.js` is present
  by construction, so it could never see a real PAGE missing the tag; `commons-names.mjs` drove
  the hand-off on `index.html` alone, grading it on the surface that needed it least. Both now
  derive from `COMMONS_SURFACES` — surface #4 is covered the day it lands with no edit — and the
  deploy asserts the tag **on the real page with comments stripped**, because `tips.html` *did*
  mention `names.js`: in the comment explaining its absence. **A grep would have passed.**
  Fired 24/24 against the shipped page, 0/24 against the fix, other 326 checks green in both.
  **BACKPORT RIDER: FIRED, and it found one more.** A repo-wide sweep for the same class —
  a shared engine reading a `window.X` a page must supply — cleared every other consumer
  (`AV_TOOLS`, `TOOLKIT_TOOLS`, `TOOLKIT_TRADE`, `TRADE_DOCS`, `FEEDBACK`); the sweep's *own*
  first verdict was a false negative, because it substring-matched `names.js` inside the comment,
  which is the defect wearing the shape of the instrument. Inside `commons-names.mjs` the same
  rot had a second instance — the mobile block's typed `['index.html','tips.html','names.html']`
  — now derived too. `commons-bag.mjs` was already clean. **THE PANEL REJECTED THE BALLOT AGAIN
  AND KILLED MY OWN CANDIDATE WITH MY OWN EXAMPLE:** three lenses scored a fourth "JOB WORDS"
  surface **2 / 3 / 5** — most of that word list already ships as `docspec.js` `aka` entries per
  trade; three words (`lien`, `liquidated damages`, `backcharge`) cannot ship at all, the last of
  them already banned as content twice by two trades that never spoke; and the ballot's headline
  routing example, *closeout → `total-package`*, **points at the compensation-comparison tool**.
  Written into §THE COMMONS as rung 2b with a falsifiable re-pitch condition, along with the hole
  the panel found instead: `shared/docspec.js` is trade-siloed, so a man who knows *"punch list
  reply"* from framing gets nothing on any other trade's write-up — **the same defect this cycle
  fixed, one layer out.** That is the named next rung. Storefront unchanged — no new tool, no new
  trade. https://mrdirno.github.io/nested-resonance-memory-archive/commons/tips.html
- `2026-08-15` — **[AXIS:COLLAGE] EVERY GAIN IN COLLAGE STUDIO WAS A BOOLEAN WEARING A NUMBER'S
  CLOTHES** · **before:** the only two answers to "how loud is the music under the clips" were ALL
  and NOTHING — three call sites each wrote a hard `1` into a field already typed `number`
  (`describeAudioSources`: `wanted ? 1 : 0`, `soundtrackSource`: `t.muted ? 0 : 1`, `applyMutes`:
  `audible ? 1 : 0`) · **after:** THE LEVEL — `lib/level.ts`, a roster of five at −6 dB a step
  (100% → a 6% bed) on the sheet the trim and the speed already share, one `mixGain` both row
  emitters call, and one `livePath` that makes applying the level twice (element volume × the gain
  node it feeds — 25% would render as 6%) unrepresentable rather than merely fixed. Mute untouched
  and still owns 0. **Measured by decoding the exported MP4 and dividing one tone by another in the
  same file** — the true-peak limiter scales every sample by one scalar, so it cancels out of a
  ratio and nothing else: **music/clip 1.2912 → 0.3227 = 0.2499× (12.0 dB down)** against a nominal
  12.04, with the clip's own 440 Hz bin identical (0.08502) in both exports; the clip path measured
  on its own separate route at **0.2481×**. BACKPORT RIDER fired IN-TREE and found a live defect one
  cycle old: `emitStatus` de-dupes on a hand-enumerated signature, and both `level` AND `moving`
  (C159's drift-row gate) were missing from it — the value reached the file and the room while the
  control read back stale. NOTE FOR THE NEXT BUMP: C159 was also a COLLAGE cycle and logged only in
  `tools/collage-studio/COLLAGE_EVOLUTION.md`, so the axis parser could not see it and reported WELL
  as stalest while the well was dry. Collage cycles get a line HERE too, from now on.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- `2026-08-16` — **[AXIS:DOCS]** **NOBODY KEEPS A CUSTOM GPT PER DOCUMENT, SO THE SETUP THAT
  COVERED ONE NOW COVERS EVERY ONE HE WRITES** · **before:** `shared/docspec.js` emitted an
  instruction block for exactly ONE document, on all eleven trades, for two months. A lead
  writes a daily every day, an incident report four times a year and a delay letter when he
  has to — and nobody maintains three Gems. He sets up the daily; the other two stay
  unwritten. The page shipped a real answer to a third of the job. · **after:** **THE DESK** —
  up to six documents in one block. The split was stated in this engine's own header on day
  one and never acted on ("Ten of those eleven are IDENTICAL for a plumber's back-charge
  notice and an AV daily"): eight blocks emitted ONCE at the top, six emitted WHOLE per
  document, repeated on purpose because an AI that jumps to one document's section has to
  find everything that section needs inside it. **THE ROUTER IS THE LOAD-BEARING HALF** —
  given three formats and one dump a model does not pick wrong, it BLENDS, so his own first
  line beats anything inferred, `aka` (already in the library for search) gives it the words
  he says out loud, exactly one question back is allowed, and blending and multi-output are
  forbidden by name. Per-document recipients, per-document continuity, the mixed chat rule
  named per document in the setup steps, and the page states the block's CHARACTER COUNT
  rather than quoting an instruction-length limit for somebody else's product (§SAFETY: we do
  not ship authoritative data we do not have). **THE REFACTOR WAS PROVED BEFORE IT WAS
  WRITTEN.** Extracting emitters out of the shipped composer is exactly the change that
  quietly rewords a sentence, so 225 states — all 170 library documents and all 55
  custom-path states across 11 trades — were captured from the SHIPPED engine first:
  **225/225 byte-identical** after, block, setup steps and bar alike. **READING THE EMITTED
  BLOCK THEN FOUND A DEFECT LIVE ON EVERY TRADE** (§SCARS 2026-08-16): the VALIDATION tail
  was welded onto the nine `halt` fields that say *"Never halt"*, three of them SHARED —
  `- Never halt. That is the ONLY reason to stop and ask me a question.` on **34 of 225
  blocks, all 11 trades**. Fixed and measured: 191 blocks unchanged, 34 changed by exactly
  that one line, steps unchanged everywhere. **BACKPORT RIDER FIRED — swept, not assumed:**
  the engine is shared so all 11 write-up pages take both changes in one edit; the `halt`
  class was re-derived from disk (9 of 86 fields, listed in the scar) rather than trusted
  from the trade in hand. **GATES, EACH PROVED BY NEGATIVE CONTROL:** NEW
  `tools/toolkit-gates/docspec-desk.mjs` — 11 trades, 0 failing, **green local AND re-run
  GREEN AGAINST PRODUCTION** — goldens against itself IN-RUN so there is no fixture to rot
  (pick A, pick B, build the desk, take B out, and A's block must return BYTE FOR BYTE; each
  document's spine, checks and continuity rule inside the desk must be its own solo block's,
  byte for byte), plus shared-blocks-exactly-once, per-document-exactly-N, continuity correct
  INSIDE each section, the cap, and the mixed chat step — proved by making extras inherit the
  primary's continuity (caught, the 2026-08-11 class) and by emitting DEFAULTS per document
  (caught) · `docspec-config.mjs` **181 checks, 0 failing, live too**, now asserting the halt
  line cannot argue with itself (proved by restoring the tail: 3 failures on `av`) ·
  `mobile-watertight.mjs` grew the reveal **'a desk of four, mid-add'**, the only state where
  the extras list, its × buttons, the character-count caution and the "✓ in this setup" row
  label are all on glass at once, driven with the four LONGEST names each trade has —
  **108 pages × 320/360/390/430 × default and bumped, 0 failing**, proved by injecting
  min-width on a desk row and watching it fail at three widths · `no-third-party` 108 pages,
  0 requests. **EYES ON THE REAL PAGE CAUGHT WHAT NO GATE COULD** (§SCARS 2026-08-16):
  entering add mode put the only "Done" control below fifteen library rows. The live page was
  then driven end to end on **hvac** at 390 and 320 — three documents, router correct,
  per-document recipients correct, zero page errors. Storefront: no new tool, but the
  `Write-Up Setup` note on all 11 trades in `persona500/src/data/fieldToolkits.ts` now names
  the capability (P5 pushes that repo).
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/write-up.html

- `2026-08-16` — **[AXIS:INTERFACE]** **THE JOB CARD — a man with two jobs stops sending one
  job's gate code to the other job's supplier.** `shared/jobcard.js`, mounted on the five
  order pages that hand-copied the sticky header. **Before:** six pages shipped byte-identical
  `var STICKY = [...]` / `SKEY = "toolkit.<trade>.<page>.header.v1"` under a `<summary>`
  reading *"typed once, saved on this phone"* — one gate code, one signer, one PO per PHONE,
  and no staleness guard anywhere, while `shared/dropoff.js` had documented that exact hazard
  as its own rule #4 since 2026-08-14. **After:** every job is a chip; tapping one swaps the
  gate, the signer, the run and the PO in the boxes below; **a new job starts EMPTY**; the old
  per-page key is adopted so nobody loses an answer saved in June. **A 4-lens panel rewrote
  the design mid-cycle** (two-job foreman · service tech · supply-house dispatcher · a skeptic
  told to kill it): the proposed staleness BANNER was killed by the foreman breaking its
  string-match guard in both directions from his own week — *"put the safety in the action
  I'm already taking, not in a warning stacked on top of it"* (§SCARS ×3).
  **`fHow` was the live defect nobody had filed:** "how it gets here" had been sticky since
  those pages shipped, so a will-call from last Tuesday printed onto today's order. It is now
  per-LIST, reset by Clear — and the route there is the cycle's sharpest scar, because my first
  cut blanked it on load and `order-live-header.mjs` failed three pages in one run for a
  reason worse than the bug being fixed.
  **THE GATE THE SKEPTIC DEMANDED IS WRITTEN:** `tools/toolkit-gates/jobcard-scope.mjs` —
  5 pages, scopes derived from the module's own behaviour, asserting a new job starts empty ·
  job A's answers never reach job B's **copied document** · switching back restores · device
  fields do not move · survives a reload · the legacy key is adopted losslessly · and no
  `fresh:` scope ever returns. **Proved by injecting the leak** (a new card inheriting the old
  card's answers): 22 failures across 4 pages, then green on restore. Gates: `jobcard-scope`
  **PASS 5** · `order-live-header` **OK 8 order pages** (was FAIL 3 mid-cycle) ·
  `no-third-party` **108 pages, 0 requests** · `mobile-watertight` **PASS on all 5 changed
  pages** at 320/360/390/430 × default and bumped · plus a targeted chip-row drive at the same
  widths **with the longest job names a man actually types — 40 assertions, 0 defects**,
  proved by injecting `white-space:nowrap` and watching 20 fail at a real 40px overflow (the
  state `mobile-watertight` cannot reach, since it loads with empty storage and sees one blank
  chip).
  **AND EYES ON THE REAL PAGE CAUGHT WHAT NO GATE COULD, again.** Screenshotted at 390 with
  one job — the state almost everybody meets first — the row rendered a label and a lit chip
  carrying the full job name directly above a Job box repeating that same string verbatim: two
  identical lines stacked, on the best glass on the page, to choose between one option. The
  switcher now appears only when there is something to switch; at one job it is a single
  dashed `+ Another job` and nothing else, which still teaches the capability because the
  button says what it does. Storefront: no new tool; the five order-page notes in
  `persona500/src/data/fieldToolkits.ts` now name the capability (P5 pushes that repo).
  **BACKPORT RIDER FIRED** — the sweep is what found the shape: six trades carried the same
  fork, and `hvac/truck-stock.html` was deliberately NOT taken (the service-tech lens: a van
  is restocked at the shop, there is no truck arriving at a site, so a job picker there is
  ceremony), as was `plumbing/supply-house-order.html`, which forks a different mechanism
  (`Draft.fields`/`Draft.keep`) and is the named remainder.
  **LIVE-VERIFIED, all 5 pages on the real URL** after the deploy went green: `window.JobCard`
  present (the module reached the artifact), the fresh state renders exactly one dashed
  affordance and no label, a gate code typed on job A reaches the **copied document**, a new
  job opens **empty**, **neither of job A's answers appears in job B's copied document**,
  switching back restores, 0 page errors. A 200 is not a render and a render is not a feature;
  this drove the job the page claims.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/pull-list.html
- `2026-08-16` — [AXIS:BREADTH] **TRADE #12 IS ACTUALLY LIVE: the Sitework Field Toolkit.**
  Before: `sitework/` — hub, 6 tools, items vocabulary, credit ledger — sat UNCOMMITTED on
  disk while every disk-derived count called it served and the URL returned **404**; the
  workflow's `TRADES` list, the `paths:` trigger, `shared/toolkit.js`'s switcher entry, the
  commons chip and its 35 commons rows (11 gear · 14 tips · 10 names) were all stranded in
  the same unstaged batch. After: committed by pathspec, deploy green, **all 8 pages 200 and
  rendering**. `HELIOS-BRIDGE/App.tsx` was deliberately left out — its working-tree change
  imports an untracked component and staging it would have failed the vite build and taken
  the whole deploy, and this trade, down with it. **BACKPORT RIDER FIRED** — the favourite
  star's ON state was the trade accent on near-white across the rack; each hub now carries a
  `--deep` token (its own colour taken down to something legible) on `--tint`, swept and
  **verified live on all 12 hubs**, sitework included. **LIVE-VERIFIED at the artifact:** 8
  pages × 320/360/390/430px — 0 horizontal scroll, 0 overflow, 0 tap target under 44px, 0
  console errors; then the job itself on the LIVE URL — two runs logged into *Before We
  Close It* produce the quitting-time message with the "nobody touches" block, the
  when-the-dirt-goes-back line and the refusal paragraph, and an electrician's pasted list
  parses into 3 answerable rows in *What I'll Leave Open*. Storefront entry made TRUE in
  persona500 `fieldToolkits.ts` (accent `#FFDDA3` identical to `trade.js`, 6 tools,
  match tokens MEASURED against all 1,027 persona ids — `grading` and `operator` killed for
  hitting sports personas). P5 owns pushing that repo.
  https://mrdirno.github.io/nested-resonance-memory-archive/sitework/

- `2026-08-17` — **[AXIS:BACKPORT]** **THE PAGE HOLDING THE ONLY REAL GATE CODE WAS THE ONE
  STILL GUARDING IT WITH A BUTTON HE HAS TO REMEMBER TO PRESS.** The well was dry (0 new, 0
  building, all trades) and no family is owed, so the stalest axis governed — and the
  previous cycle had named this cycle's work itself: five order pages got `shared/jobcard.js`
  and `plumbing/supply-house-order.html` was left as "the named remainder", because it forks
  `Draft.fields`/`Draft.keep`. **The remainder was bigger than the fork.** The gate code on
  that page is not in the header at all — it is in the `shared/dropoff.js` block, sticky
  since it shipped, keyed to the PHONE, guarded by a notice and a manual clear button: the
  exact shape the foreman panel killed three days later when it designed the card. Mounting
  the card alone would have swapped the account and the PO and left the gate code sitting
  there — a page that LOOKS job-aware while the one answer a truck is dispatched on stays
  per-phone, which `jobcard-scope.mjs` already calls strictly worse than the sticky header it
  replaced. **So: both, or neither.** `shared/dropoff.js` now takes a key per JOB (`rekey`,
  saving the job he is leaving before loading the one he arrives at); **job #1 keeps the
  original key, so no phone with a saved gate code is migrated at all**; under a card it
  drops the "filled in for &lt;job&gt;" line and re-words its clear button (§SCARS ×2).
  **A 3-lens panel (a two-job plumber · a supply-house counterman · a skeptic told to kill
  it) moved two scopes I had wrong:** `fAcct` rides the JOB here — alone among the six pages
  with a card, because none of the others send anything to a counter that BILLS, and the
  counterman priced it, *"a GC-furnished job billed to THEIR account, a warranty pull kept
  off billable job cost, service kept apart from new-construction — several times a week"* —
  and `fPick` rides THE ORDER, where the tech put it (*"whoever's free to run the counter
  today, not last month's name"*). The skeptic returned BUILD-NARROWER on three conditions
  and independently found the `{v,s}` adoption hole; all three were already in the tree, and
  its fourth objection — that a page must not run `Draft.keep` beside the card, since the
  card assigns `el.value` and fires no event — is why the parallel writer was **deleted**,
  not left running. **`hvac/truck-stock.html` still gets no card** (a van is restocked at the
  shop; both field lenses re-confirmed the picker is ceremony there) — **but the picker was
  never the only fix, and skipping the page skipped the bug**: `fHow` and `fCharge` were
  sticky forever, so a will-call from a fortnight ago and last month's Warranty code printed
  onto today's restock. The tech found his *"at 6:40 with a hot call waiting on a contactor
  sitting on a shelf nobody sent anywhere."* Both now ride the list by the `pull-list`
  mechanism verbatim — default pre-captured, `touched` including them, restored on reload,
  reset by Clear — and the `<summary>` promising "typed once, saved on this phone" changed
  with the code. **BACKPORT RIDER FIRED:** swept all 12 trades for the class. 5 pages already
  carried the card, 2 fixed here, `hvac/repair-recommendation` clean (`fBy`/`fCo` are both
  device), `av/cable-list` clean (header rides the list, `fFinish` device-keyed under its own
  key), `av/consumables` deliberately left (its only sticky value is the job NAME, in a box
  at the top of the glass — no secret behind a drawer) and named as the remainder. Gates:
  `jobcard-scope` **PASS 6** — extended so the drop-off ids are leak-tested (they are not
  `f`-fields and scope-derivation cannot see them) and so it seeds **both** legacy shapes;
  **proved by injecting the leak, 12 failures**, and by disabling the unwrap, 3 more —
  `order-live-header` **OK 8** · `dropoff-block` **OK** · `no-third-party` **116 pages, 0
  requests** · `mobile-watertight` **PASS** both changed pages. **LIVE-VERIFIED on the real
  URL:** job A's PO, account, gate code and signer all reach the counter's document; job B
  opens **empty** on all four with his name+cell kept; **none of job A's four appears in job
  B's copied document**; switching back restores all four; it survives a reload; truck-stock
  keeps a changed how/charge across a reload and Clear puts both back and they stay back; 0
  page errors. Storefront: no new tool, the plumbing note in `fieldToolkits.ts` now names the
  capability (P5 pushes that repo).
  https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/supply-house-order.html

- `2026-08-17` — **[AXIS:DEPTH] THE THINNEST TRADE ON THE RACK GOT THE PAGE ITS OWN REGISTRY
  HAD NAMED, AND BUILDING IT PROVED A SHARED CONTROL HAD BEEN UNREADABLE ON ELEVEN TRADES** ·
  `sitework/what-goes-in.html` — **12 trades / 89 tools → 12 trades / 90 tools**, sitework
  6 → 7. Well empty (0 new, 0 building), breadth debt paid, DEPTH stalest by 9 lane-cycles;
  sitework had exactly ONE trade-specific tool and `sitework/tools.js` named THE MATERIAL
  CALL in its own source as one of two rungs it was deliberately not building yet. **The
  tenth instance of shape #1: 78 items over eight sections** — the largest picker on the rack
  (`pickfilter` gate) — pipe by the JOINT or the FOOT, fittings, structures BY THE MARK,
  stone by the TON or the LOAD, and the section that costs a re-dig: fabric, tape and tracer
  by the ROLL. **The differentiator was not the shape and not the size ladder.** It is that
  this order's SECOND READING is the list of what gets BURIED — derived from the item data
  (`ditch: true`), never tapped, only a WRITE-IN carries the tick because a line he typed is
  a sentence only he can classify — ending on *"once it's backfilled it doesn't come back
  out."* Every other order page on the rack is short a line and somebody drives to the
  counter; short a line here is a re-dig. Masonry's RUN mechanism was **stolen rather than
  re-derived** per the private record's instruction, as the TIE-IN — flag + header
  passthrough + the call-out when one exists without the other, **including the inverse case
  masonry's own first draft dropped on the floor**. The delivery half took `shared/dropoff.js`
  (chips, per-job key, the ask-not-a-booking line) instead of hand-rolling seven fields the
  way the page built the day after that engine was extracted did. **BACKPORT RIDER FIRED, and
  it was the bigger half of the cycle:** building for the palest accent on the board exposed
  that `.jc-chip.on` and `.do-chip.on` drew the SELECTED state's border and ring in
  `var(--flag)` — a token measured against the DARK NAV, therefore light by construction,
  drawn on WHITE. Measured across all twelve trades: **eleven between 1.30:1 and 2.28:1**,
  the border swap carrying 1.01–1.45:1 against the grey it replaces and the tint 1.07–1.19:1
  — the lit state was resting on bolder text alone, on the control that answers WHICH JOB AM
  I WRITING A GATE CODE INTO. **Plumbing at 3.58:1 is the twelfth, and plumbing was the only
  trade the drop-off block had ever shipped on.** Fixed once in each shared module as
  `var(--deep, var(--flag, …))` — 5.21–8.46:1 on all twelve — instead of twelve page-local
  overrides; the first draft's page-local override was DELETED and its removal is what proves
  the shared fix. Gates: `jobcard-scope` **PASS 7**, extended with a lit-vs-unlit chip
  assertion at a 3:1 bar and **proved by reverting the shared rule — 6 of 7 pages fail** — and
  taught that an explicit `legacyKey: null` is how a page born with a card says it has no
  predecessor, while silence still fails · `order-live-header` **OK 9** (15 header controls,
  11 in the document) · `dropoff-block` **OK 2** · `pickfilter` **OK 10, 130 assertions** ·
  `mobile-watertight` **117 pages, 0 failing** · `no-third-party` clean. **VERIFIED AT THE
  ARTIFACT, 64 assertions on the real page:** the job driven end to end at 390px — a bare
  `20` printing as `20 joints` and a bare `1` as `1 ea` while a pasted line goes exactly as
  written, the buried list carrying pipe + fitting + the ticked write-in, the tie-in block
  carrying what's in the ground, three defect questions naming only catalogue rows and never
  the write-in, the glass-only pair question staying off the message, the clipboard matching
  the preview byte for byte, all of it surviving a reload, and a will-call carrying **no gate
  code** — plus 320/360/390/430px populated and with the OS text size bumped, and zero page
  errors. Storefront: entry added to `fieldToolkits.ts`, contract rebuilt (**12 trades, 90
  tools**) and `--check` in sync; P5 pushes that repo.
  https://mrdirno.github.io/nested-resonance-memory-archive/sitework/what-goes-in.html
