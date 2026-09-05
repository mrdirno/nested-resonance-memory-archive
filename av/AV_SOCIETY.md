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

**THE PANEL THAT SCORED SEND (C3698, recorded by C3699).** Three lenses, independently:
**7 / 3 / 7.** Recorded with the 3 intact, because a 3 is a dissent and this book is where
dissents live: the panel did **not** agree that Send was worth building — one lens was
unconvinced of the value. What all three agreed on was the DESIGN, and that agreement
survives as the rules in `shared/toolkit.js`'s header, each written as the failure it
prevents (the payload is exactly `{ text }` · `share()` is called synchronously inside the
tap · Cancel does nothing · the button is ABSENT where the API is absent, never hidden).
The argument itself was never written down — that cycle ended before its CLOSE
(§SCARS 2026-09-03) — so what survives is the verdict, not the reasoning. **And the 3 is a
countable question rather than a matter of taste:** Send and Copy are two doors to the same
document, which is exactly the CHOICE §THE EVO LOOP says to instrument. It is not
instrumented today. That is the named next rung, and until it is counted the dissent stands
unanswered.

**A LENS WILL HAND YOUR OWN PROMPT BACK AS A CITATION (C3702).** The skeptic that
voted to KILL *What's in the Drop* rested part of its verdict on this: *"§THE
SYSTEM OF RECORD names 'a delivery receipt' by name as one of the four document
types this book forbids competing with."* It does not. `grep -i "delivery
receipt"` over this file returns nothing — the phrase came out of the QUESTION it
was asked, and came back wearing the book's authority. Its conclusion survived
anyway, because a second lens reached the same place from a different direction;
had the conclusion rested on the citation alone, a real page would have been
killed on a rule that does not exist.

**So: check a lens's citations against the file before you act on them.** It costs
one grep. A panel cannot self-detect this failure — the lens is not lying, it is
reading its own brief back — and the more precisely you frame a question, the more
of your own framing comes back as evidence.

**AND RECORD THE SPREAD, NOT THE AVERAGE.** *What's in the Drop* scored **7 / 6 /
2**. The 2 is why two of the rung's three named parts are not on the shipped page,
and the strongest signal the exercise produced was the skeptic and the working
editor **agreeing on the one thing worth building while disagreeing about
everything else**. A panel that comes back unanimous was probably asked badly.

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
- **AND THE SITE-ROOT REGISTRY, WHICH THIS LIST DID NOT NAME EITHER (found at trade #13).**
  `HELIOS-BRIDGE/components/UIComponents.tsx` carries the TOOLS list the site root renders,
  and a trade staged into the artifact with no entry there is a whole toolkit nothing at the
  root links to. The deploy asserts it — *"trade 'X' is staged but has NO entry in the
  site-root TOOLS registry"* — and it caught flooring on its first push, which is the assert
  working and this checklist failing. **That makes FOUR lists a trade has to join and one
  directory it has to be: `TRADES` + the `paths:` trigger in the workflow, the runtime's own
  `TRADES` array in `shared/toolkit.js`, `COMMONS_TRADES` with real rows behind it, and this
  one.** Every one of them is asserted in CI, so none of them can rot silently — but a
  checklist that omits one still costs a red deploy, and this is the second time that omission
  has been the story of a stand-up.
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
- **AND THE GENERATED INDEX, WHICH IS NOT A LIST YOU JOIN BUT AN ARTIFACT YOU
  REBUILD — found at trade #15, by a red deploy.** `shared/docsindex.js` is
  DERIVED from every trade's `docs.js`, and the deploy asserts it with
  `build-docsindex.mjs --check`: *"shared/docsindex.js is stale against the
  thirteen staged libraries."* A fifteenth library makes it stale by existing, so
  a stand-up that writes a perfect `docs.js` and pushes still goes red. Run
  `node tools/toolkit-gates/build-docsindex.mjs` (no flag) and commit the result.
  The four lists above are things a trade JOINS; this is the first thing on the
  checklist that has to be REGENERATED, which is exactly why it was the one that
  got missed — every other item fails a grep, and this one only fails a rebuild.
- **AND THE THREE BOUNDARY PAGES, OR THE DEBT NAMED IN THE STAND-UP ENTRY — found
  at trade #14.** A construction trade joins the boundary it was built to serve:
  `rough-in-request` + `answer-back` + `getting-in`, each a config on the shared
  engine, panel-cut in the trade's own words. Painting stood up 2026-08-24 with six
  tools and none of the three — unnamed, so the only construction kit that could not
  send an ask, answer a list or ask a building for a night looked complete on every
  count. The deploy already asserts the ask⇒answer pair; `boundary-titles.mjs` now
  asserts the page copies wear their own names in the two lines the runtime never
  touches (<title> and the apple-title), and `answer-tapnote.mjs` asserts the tap
  instructions say the words the trade's answers[] actually ships. A stand-up that
  deliberately defers a boundary page writes the deferral into its cycle entry, the
  way flooring's DOCS debt was named — an unnamed absence is how this hole got dug.
- **AND THE HUB'S `:root`, WHICH IS COPIED WITH THE SIBLING'S COLOUR IN IT — found at trade
  #16, five days after trade #15 shipped wearing painting's green.** `--flag`, `--flag-ink`,
  `--tint` and `--deep` in `<trade>/index.html` are the trade's accent pair from `trade.js`,
  and the deploy now asserts `--flag` equals the accent per staged trade. Set all four before
  the h1.
- **AND THE PHRASES THE GATES READ OUT OF A CONFIG'S PROSE — found at trade #16.** Three gates
  read a trade's own words by regex: `getting-in.mjs` wants "the window you're actually giving
  us" in the closing and at least one heads-up naming a PERMITTED activity (valve · closure ·
  power down · hot work · fire alarm …); `answer-tapnote.mjs` wants all four rungs verbatim in
  the tap instruction; `boundary-titles.mjs` wants `<title>` and the apple-title to be the
  config's `toolName`. Copy the sibling's sentence where a gate names one, then localize
  around it — a paraphrase fails the build.
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

**AND SINCE 2026-08-28 EVERY LINE IN THE LIBRARY DECLARES WHAT WOULD SATISFY IT.** The
five classes each carry an `artefact` string — "a date", "a name", "a before-value", "a
location", "a named gap" — and for the whole life of this engine that string rendered at
exactly ONE call site: the tick list on the CUSTOM path, the path a man reaches only when
his document is not in the library. All 231 library documents printed their hand-written
line and never said what would answer it. The failure that closes is not a dropped
heading, it is a FLUENT SENTENCE: `hvac/red-tag-notice` asks for *"the time you shut it
off and the name of the human you handed it to"* and gets back *"the unit was taken out of
service and the property manager was notified"* — heading present, sentence present, no
`<MISSING>` anywhere, both facts gone. **A working foreman named that as the one failure
he cannot catch by eye, and said why: he KNOWS he handed it to Denise at 2:40, so he reads
her name into a sentence that does not contain it.** So `needs` is authored beside `omit`
on every document, shape-mirrored, emitted to the model as a demand with a per-artefact
`<MISSING: the name>` token, and printed for the man in the red frame before he opens his
mouth. §SHAPE #4 HAS TWO READERS had written the rule three days earlier: *any field
authored into one of these libraries whose only consumer is a machine is on the clock.*

**THE VOCABULARY IS EIGHT, AND THE TICK LIST IS STILL FIVE — the constraint that capped it
was a UI constraint on a UI this data has never had.** The 2026-08-15 pass below derived
SEVEN and refused the two extras because *"seven ticks is the ten generic ones the rung
forbade"* — true of a tick list, where every row is a row a man in a hurry must read, and
irrelevant to a field authored once by whoever writes the document. Re-counted over all
142 distinct lines: `count` (a number with its unit) is demanded by **30** of them, fifth
of eight. It was never a rounding error; it was invisible. **The eighth was forced by the
corpus three separate times:** a DOCUMENT AND ITS REVISION — the sheet, the bulletin, the
proposal's scope line, the packing list, the version a yes was given against. The
2026-08-15 pass hit it and filed it unreachable (*"the sheet number and revision a letter
is written against, 4 of 26"*); of the two blind passes run over the full 142 this cycle,
one pushed it into `none` and the other into `where`, and both are legibly wrong — a sheet
number is the most concrete artefact in the corpus, so `none` is a shrug, and *"say the
actual A LOCATION"* under *"the sheet numbers and revisions"* names the wrong kind of
thing. `framing/wont-fit` is the whole argument: *"the sheet numbers and revisions,
WITHOUT WHICH THE QUESTION CANNOT BE ANSWERED BY ANYONE."*

**THE SETTLED COUNTS over 142 distinct lines** (241 merged across 15 trades): `when` 63 ·
`who` 52 · `where` 44 · `notdone` 41 · `count` 30 · `before` 16 · `change` 10 · `ref` 8 ·
`none` 11. **A line may demand more than one and most do** — 50 demand one, 57 two, 29
three, 6 four — which is itself the finding, because the omitted line that costs the most
is almost never one fact. `none` at 11 of 142 (8%) is the honest floor, and it is a real
value, not a failure to classify: forcing an interpretation-shaped omission into a fact
class puts a confident demand under a line that cannot satisfy one.

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

### SHAPE #4 HAS TWO READERS, AND FOR THREE MONTHS IT ONLY SERVED ONE (2026-08-25)
The block is written for the MACHINE and it is allowed to be dense — 9,500 characters a
man pastes in once. But the setup is once and the DICTATION is every time, and the whole
chain fails at the same place: he talks, and whatever he did not say comes back
`<MISSING>`. Every document in the library already names what he has to say — `facts`,
authored per document — and it was only ever emitted INTO the block, addressed to the AI.

So shape #4 renders TWO artefacts off one authored library:

  · **THE BLOCK** — for the model, pasted once, dense on purpose.
  · **THE SAY-LIST** — for the man, on the page, read every time. Numbered, in the
    trade's own words, with the omitted line as its last item and one control that
    copies it to the group chat. It is the only part of this page that still works
    when his AI does not.

**THE RULE THIS SETTLES, and it is not about `facts`:** any field authored into one of
these libraries whose only consumer is a machine is on the clock. Nobody proofreads a
string nobody reads — three live defects were sitting in `facts` and every gate we had
passed all three (§SCARS 2026-08-25 C3658). Either put it in front of a person, or gate
its SHAPE and not just its presence. "It reaches the block" is not proofreading.

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

**THE EVO LOOP'S STEP (a) HAS NEVER SHIPPED, AND THE REASON IS STRUCTURAL, NOT
NEGLECT (measured 2026-08-26, C3673).** The directive has carried "INSTRUMENT
anything that offers a CHOICE… record which variant was actually used, as an
anonymous COUNT" on every bump since 2026-08-04. Twenty-two days later a grep for
counting code across `av/*.js` and `shared/*.js` returns **nothing**, and the
cycle logs contain no instrumented surface. The other steps HAVE fired — the
2026-08-13 entry writes a falsifiable step-(c) prediction straight into the code —
so it is step (a) alone that is stuck, and this is why: **a count on a
self-contained client-side page has no sink.** §SAFETY forbids a server, an
external API and a third-party CDN, so an anonymous tally lands in that one
browser's `localStorage` and is never read by anybody. It is not a measurement;
it is a number in a drawer on a phone.

**THE ONE SINK THAT ALREADY EXISTS IS THE WELL.** `shared/toolkit.js` already
posts to the wishing well when a user opts in, which is the only consented
channel off these pages. A variant count could ride it as an explicit, opt-in
line the wisher can see before it goes — never a silent beacon, which would
violate the rail below and the trust the whole rack runs on. **Nobody should
build that on a hunch; it is written here so the next cycle inherits the
diagnosis instead of re-deriving the silence.** Until then, revealed preference
on this rack is measurable only through what the WELL says, and stated
preference is all we have — which is a limit worth knowing rather than a program
worth pretending to run.

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
   ~~**THE HOLE THE PANEL FOUND INSTEAD, and the named next rung on this axis:**
   `shared/docspec.js` is trade-siloed by construction … an AV tech who only knows "punch list
   reply" from a framing background GETS NOTHING.~~ **STRUCK 2026-08-23, and struck with what it
   taught rather than a checkmark.** Half of it shipped as `shared/docsindex.js`; the other half
   was killed 3–0 by a judge panel, and BOTH halves corrected the rung as written:
   - **"Gets nothing" was false.** 9,529 searches driven through the real box: **zero dead ends**
     (§SCARS). `find.js` never returns nothing — the rung had been filed in the shape of the
     commons tips surface it was isomorphed from, and that surface's defect did not survive the
     crossing. The real one was a **confident wrong document**: 1,083 for a document his own
     library was HOLDING, 512 of them unhedged.
   - **WHAT SHIPPED — the pooled vocabulary, and the reason it is safe is the reason it is
     small.** Eight documents live on all thirteen trades and every trade RENAMED them
     (`delay-notice`: 7 names). `shared/docsindex.js` unions every name and `aka` anybody wrote
     and adds them ONLY to trades that already carry that document, so it can never introduce a
     document and the **57 single-trade documents can never push a word anywhere**. Rails: one
     meaning rack-wide (engine's own normalizer), a near-name quarantine (`"not us"`/`"notes"`,
     `"what we said"`/`"what we laid"`), 2+ carriers, and a deploy that regenerates and refuses a
     diff. Result 1,083 → 36 · unhedged 512 → 23.
   - **WHAT WAS REFUSED, on mechanism — the cross-trade HAND-OFF the rung above actually
     describes.** Routing a man to the trade that owns a document his own kit does not carry
     targets the bigger number (5,644) and was scored **5 / 1 / 2**. It cannot be built here,
     and the reason is not taste: **every block introduces the reader in the OWNING trade's
     words** — sitework's A Line Got Hit opens *"I am the foreman who was on the machine or in
     the hole; we do sitework and underground utility work."* Today he gets a wrong document in
     his own voice and rejects it in seconds; routed, he gets a plausible document in the wrong
     voice that he asked for by name. Whether **this** man may author **this** document depends
     on his licence and his subcontract, which a client-side static page will never hold. **The
     re-pitch condition, falsifiable:** it becomes buildable the day a document declares itself
     trade-neutral in its own data (an authored `portable` flag, not a derived one) AND the
     ROUTER line stops naming the owning trade — until then the honest version is TEXT naming
     the trade that writes it, never a link to the instrument.
   - ~~**THE NAMED NEXT RUNG IS ONE LAYER DOWN AGAIN, and it is not a COMMONS rung.**
     `find.js` sets `mode = "exact"` when every LIVE query token was covered, not when the
     match was strong.~~ **SHIPPED 2026-08-25 (C3659), and the rung was right about the
     mechanism and low about the size.** It is **29** pages that share the engine, not 16, and
     re-measured on fourteen trades the class is **3,838 of 10,738**, not 3,161. A match now
     carries a STRENGTH beside its score — strong only when the token is a word of what the
     item is CALLED and he typed it whole (a prefix counts on the last token, the word under
     his cursor, and nowhere else) — and `mode` is a claim about the row he sees first.
     **3,838 → 2,027 unhedged wrong, his own document first 3,986 → 4,139, zero regressions,
     zero correct answers hedged.** The `about: true` field flag is the caller's own
     declaration that a field DESCRIBES rather than NAMES; rule 4 also stopped ignoring `aka`,
     which is where the 153 extra right answers came from. Gate `find-honesty.mjs`, 6,492
     checks, every probe derived from the surface's own strings.
   - **THE NAMED NEXT RUNG, and it is the other half of the same honesty:** rule 1 drops a
     token that matches nothing in the library as noise the user added, which is right for
     *"template"* and *"form"* and **silently wrong for a content word**. *"AHJ nuisance
     letter"* on the AV page keeps only *letter*, answers that, and still says exact — and
     that mechanism is **most of the ~2,027 that remain** (1,925 of them are multi-word
     queries). **THE SHAPE IS ALREADY BUILT AND SHIPPED, one floor down:** `commons/commons.js`
     renders *Ignored "guard" — nothing here uses that word* off the `noise` array the engine
     has always returned. `shared/docspec.js` and `shared/pickfilter.js` ignore it. The rung is
     to carry that line to the other 26 surfaces — **not** to demote the answer, because the
     document IS what he asked for and the extra word was chrome; the honest move is to name
     what was dropped and let him judge it. **THE FALSIFIER WAS RUN BEFORE THE RUNG WAS
     WRITTEN DOWN, not after: 1,707 of the 2,006 — 85.1% — carry a non-empty `noise`.**
     (Measured on the draft before rule 4 was re-laddered; the class did not move and the
     total settled at 2,027.)
     *"answering the fire marshal"* keeps only *the*, drops *answering, fire, marshal*, and
     returns the Service Call Write-Up as an exact match. Measured through the engine's own
     result object (`DocSpec.findIx()` is exported for exactly this, so a gate never rebuilds
     the field spec beside it), and it returned **2,006 independently of the DOM sweep that
     returned 2,006** — two paths, one number.
     **SHIPPED 2026-08-26 (C3661), and the rung was right about the mechanism and wrong about
     the reason.** `Find.dropped(res)` now lives in `shared/find.js` — the file that decides
     what to delete owns the sentence that admits it — and all three renderers call it, so
     26 surfaces that said nothing now name the word. Re-driven at the DOM: **3,631 → 3,360
     saying so (92.5%)**, the remaining 271 held back BY DESIGN (below), and **0 of 2,557**
     searches that dropped nothing gained a sentence. Moving the sentence into the engine also
     fixed three things the four inline lines in `commons.js` had wrong and could not have
     seen alone, because one surface's data does not contain them: plural over two dropped
     words, a word he repeated printed twice, and his own capitalisation (he types **AHJ**,
     the array holds `ahj`). Gate `find-noise.mjs`, **318 checks over all 29 surfaces**, every
     class red-verified.
   - **THE RUNG'S OWN REASONING WAS FALSIFIED IN THE MEASURING, and the honest version is
     smaller.** It said *"the document IS what he asked for and the extra word was chrome."*
     Over 21,372 cross-surface searches, **3,409 of the 3,631 (93.9%) kept HALF OR LESS of
     what he typed** — the survivor is normally the generic head noun (*note, letter, record,
     strap*) and the deletion is the word that discriminates (*inspection, AHJ, nuisance,
     EMT*), because a generic noun sits on many rows and a modifier sits on none. Rule 1 is
     preferentially deleting the high-information token. **Cite that as the SHAPE of the
     defect, never as an incidence rate** — the corpus is built to over-represent it, and on
     its OWN page a surface drops nothing at all (920 of 923 own-name searches come back exact
     with an empty `noise`), which is why the line is silent almost all the time.
   - ~~**THE NAMED NEXT RUNG — demote the LABEL, and the panel's own predicate is already
     dead.**~~ **SHIPPED 2026-08-28 (C3678) as RULE 6, and the rung was right about the
     mechanism, right to kill the counting predicate, and WRONG about what to fire on.**
     The predicate that shipped is `honest = … && (!say.length || wholeName(lead, liveQuery))`
     — `say`, not `noise`, and the difference is 11,306 keystrokes. `say` is the engine's
     existing hold-back for the word still under his thumb; firing on raw `noise` instead
     demotes on the first letter of every word after the first, so the heading flips to
     "Closest to" and back on **3,456 of 21,017** mid-typing queries against 14,762 with the
     hold-back — text flickering under his thumb on the default way this box is used. A word
     we will not NAME out loud is not a word we may HEDGE on. `wholeName` is rule 4's
     `named()` with the primary field put back, because the title is the first name a thing
     has. **Driven over 72,138 searches on all 31 surfaces that load the engine: unhedged
     wrong 3,125 → 675.** Diffed query by query rather than totalled — **2,450 newly hedged,
     every one over a lead the query had not named, ZERO right answers hedged** — and the
     lead row never moved: 41,194 correct leads before and after, 0 right→wrong, 0
     wrong→right. Good cases unmoved: verbatim name or alias **7,417/7,417**, that name plus
     a search-box word **7,064/7,064**, mid-typing **14,762/21,017**.
     **THE COUNTING PREDICATE IS DEAD ON THE FULL RACK, AND BIGGER THAN THE 72 THIS RUNG
     PREDICTED:** `live.length <= noise.length` costs **371 of 7,064** name-plus-chrome
     searches and 809 mid-typing ones. The rung was measured on 14 trades and one class of
     surface; the rack is 31 surfaces and includes one-word gear names, where the cure is the
     disease. **AND RULE 6 IMMEDIATELY CAUGHT WHAT RULE 4 HAD BEEN HIDING:** rule 4's phrase
     ladder was graded on the RAW query with the deleted word still in it, so *"Drywall lift
     template"* drew no phrase bonus at all and the row actually CALLED **Drywall lift** lost
     the lead to a longer row that beat it on weight — one dropped word MOVING the answer,
     which is exactly what `find-noise.mjs` N7 forbids, sitting on rows N7 never probed. The
     honest label pointed at it: the heading went to "Closest to" and was RIGHT, because the
     row underneath was wrong. Rule 4 now reads the same live query under the same separator
     gate; ungated it cost **149 mid-typing leads** and that number is why the gate is there.
     **THE GATE:** `find-honesty.mjs` **8,472 checks, 0 failing** (was 6,492), with two new
     classes that are ONE PAIR — same surface, same proven-absent word, one attached to a
     WHOLE name (H, stays exact) and one to a FRAGMENT of a name (J, hedges), so nothing about
     the chrome-ness of the deletion can explain the split and only wholeness can. Both
     red-verified by restoring code: **J 0/108** against the pre-change engine, **H
     1,402/1,468** against the counting predicate.
     ~~**the dead version, kept because the falsifier in it is the reason the shipped
     predicate is shaped the way it is:**~~
     Three lenses scored it independently; **two voted to demote** and lens 2 gave the
     predicate `noise.length > 0 && live.length <= noise.length` (live ≤ half). The falsifier
     was run before the rung was written down, not after, and it is TWO numbers, not one:
     against own-page item names the demote costs **0 of 920** — lens 1's stated fear that
     *"Closest to becomes the app's normal voice"* is measurably false, because a man typing
     his own page's name has no dropped word to demote on. But against **his own name plus the
     word a search box taught him to add** (*template · form · sheet · example · pdf · blank ·
     printable*, the exact class rule 1 exists for) it costs **72 of 1,838 (3.9%)**, and all 72
     are the same shape: a ONE-WORD item name plus one chrome word, `live 1 / total 2`.
     *"Washout template"* would be hedged. **That is the cure becoming the disease, and it
     kills the ratio.** The discriminating fact is not how many words survived but whether the
     survivors are a WHOLE NAME of the lead row: in *"Washout template"* the survivor is the
     entire name and he added chrome; in *"Inspection Note"* the survivor is a fragment of
     *Damage / Pre-Existing Condition Note* and he named a piece. **The engine already computes
     this** — rule 4's `named()` asks exactly "did he type one of this item's names, whole?" —
     so the rung is `honest = … && (noise.length === 0 || named(lead, liveQuery))`, and it must
     ship with the 0/72 pair re-measured against it, plus `find-honesty.mjs` (6,492 checks) and
     the *"Another trade's name for it"* heading, which lives in the same `else if` chain that
     a demote would swallow.
   - **THE RESIDUAL, named so it is not re-derived:** a hyphenated part designator still reports
     in pieces — *"USB-A → USB-B"* prints `Ignored “USB”, “A”, “B”`. The fraction case was fixed
     (a slash between two digits is not a separator, so *"3/4 EMT strap"* now prints `Ignored
     “EMT”` and not two bare digits), but a hyphen is genuinely ambiguous — *Pre-Existing* is
     two words and *USB-A* is one — and no rule that was tried tells them apart.
   - ~~**THE NAMED NEXT RUNG — rule 6 only fires when rule 1 DELETED something, and the same
     lie is available with nothing deleted.**~~ Of the **675** unhedged-wrong answers left after
     rule 6, **322 (47.7%) are queries where the surface has no row called that at all** and
     nothing was dropped: every word he typed IS a word of some row's name here, each one at
     full strength, and no row is CALLED any of what he typed. *"cut in"* and *"pipe wrenches"*
     on `av/write-up` come back as the Damage / Pre-Existing Condition Note, presented as an
     exact match, with an empty `noise`. 497 of the 675 are multi-word. The shape of the fix is
     obvious and that is exactly why it needs its falsifier run FIRST: dropping the `!say.length`
     guard and asking `wholeName` on every query would hedge **class F** — the word under his
     cursor, *"daily field repo"*, which is not a whole name and never will be — so the rung is
     not "extend rule 6", it is **find the condition that separates a lead he has half-typed
     from a lead he has not named at all**, and the number to beat is 322 hedged against 0 of
     class F and 0 of the 14,762 mid-typing exacts. **A CAVEAT ON THE OTHER 353, so it is not
     re-derived as a defect:** 136 of them are the measuring instrument, not the engine —
     *"damage"* is scored WRONG because the harness credits the first row carrying the word and
     the Damage Note carries it in its TITLE while the Incident Report carries it as a nickname,
     which is the ordering `find-honesty.mjs` class G already asserts is correct.
   - **SHIPPED 2026-09-03 (C3700) AS RULE 7 — the rung was right that the label lies with an
     empty sentence, and WRONG about why it is empty. Its own worked example gave it away.**
     *"pipe wrenches"* on `av/write-up` was filed as *"nothing was dropped"*. A word WAS
     dropped — `wrenches` — and the reason it left no trace is the MID-WORD HOLD-BACK: the
     engine will not name a token it thinks is still under his thumb, `say` goes empty, and
     **`say` empty makes rule 6's clause vacuous**, so the label goes out exact as well. Rule 6
     did not leave a hole beside itself; it left the door it stands in unlocked. Driven over
     **41,516 searches on 33 surfaces**, 3,181 answers were exact ONLY because the hold-back
     had emptied `say`, and the decomposition of the 623 unhedged-wrong is not the one the rung
     wrote down: **453 (72.7%) ride the hold-back · 124 (19.9%) really did drop nothing · 46
     got past rule 6 on a real name.** The 322/47.7% split does not reproduce.
   - **THE THRESHOLD IS EVIDENCE, NOT TASTE, and that is the whole rung.** "Still on a word"
     is a claim the engine can check: at one character `tokenScore()` has no prefix path at
     all (which is the real flicker window, and the reason C3678's `1/4 drill b` case is
     genuine), at two the prefix path is live, at three both prefix and infix are. A trailing
     token of **three** characters that matched NOTHING begins no word and sits inside no word
     anywhere in the library — it is not a word in progress, it is a word this page does not
     have, so it may be named and hedged on. `var UNDER_THUMB = 3` in `shared/find.js`, one
     clause on the hold-back, nothing else touched.
   - **THE NUMBERS, AND THE COST BAR WAS PRE-REGISTERED BEFORE THE PREDICATE WAS WRITTEN:**
     zero on the KEYSTROKE corpus — every own name typed one character at a time, **13,659
     queries, 12,813 of them exact, which is the only place a label can flicker.** Delivered:
     **unhedged-wrong 623 → 172**, and diffed query by query rather than totalled — **759 newly
     hedged (451 wrong answers + 308 below), 0 newly UNhedged, and the lead row moved 0 times
     in 41,516 searches.** Good cases unmoved: verbatim name **586/586**, authored alias
     **864/864**, mid-typing **12,813/12,813**, whole-name-plus-chrome **248/248** on the
     document libraries and **60/60** on the commons. The 451 was PREDICTED from the baseline
     run through the engine's own exported `wholeName` and then RETURNED by the patched
     engine's diff — two paths, one number, and the same for the 308.
   - **THE 308 IS NOT A COST, IT IS A TRANSITION REMOVED — and it names the next rung.** All
     308 sit on the twelve-plus tap-to-tick lists, and on those surfaces the FINISHED form of
     the identical query (*name* + *template* + a space) is **already hedged 272 of 280
     today**. The change moves the flip from the space to the third character of a word that
     was never here; the count of transitions goes from one to none. It rides a defect it did
     not create, below.
   - **THE NAMED NEXT RUNG, and it is bigger than the 124 this cycle left behind: rule 6 is
     STRUCTURALLY BLIND on every pick surface.** `shared/pickfilter.js` indexes a row's whole
     `<li>` textContent as its ONE primary field, so `wholeName()` — "is this row wholly
     CALLED that" — can never be true there, and rule 6 hedges a man who typed an item's exact
     name plus the word a search box taught him to add. Measured: class H **8/280 exact on the
     pick surfaces against 248/248 on the document libraries and 60/60 on the commons**, so
     **272 false hedges** on the shape rule 6 was explicitly written to leave alone. The fix is
     a field spec, not a predicate — declare the row's NAME as the primary field and the `<li>`
     text as `about: true` — and it moves ranking on fourteen surfaces, so it ships with its
     own lead-movement diff or not at all.
   - **AND THE 124 THAT REALLY DID DROP NOTHING, named with the number that killed the obvious
     fix so it is not re-derived.** Every word he typed is a word of SOMETHING's name here at
     full strength and no row is called any of it; 67 of the 124 are single-word, where the
     honest label is exact (he typed a word of the title — `find-honesty.mjs` class G asserts
     that ordering is correct). The candidate was **RUN**: hedge unless the tokens are a
     contiguous whole-word run inside ONE naming part of the lead, last token allowed to prefix
     while under his cursor. It was written into the engine, measured, and **taken back out:
     it hedges 31 of the 124 and costs 24 mid-typing keystrokes** — *"What Was I"* on
     `sitework/write-up` leads *What Was Already Like That When We Got Here* and RUN calls it
     not-named — against a pre-registered bar of ZERO on that corpus. **A weaker variant, BAG
     (same words, any order, one name), was measured in the same run and is worse: it sees 17.**
     The rung is still "find the condition that separates a lead he has half-typed from a lead
     he has not named at all", and RUN is now on the record as not being it.

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

**WHERE INTERFACE GOES NEXT:** ~~(1) mount the drop-off block on the four order pages that
carry the typed half but not the ticks~~ — **SHIPPED 2026-08-19, and NOT as this entry
predicted.** It was never an engine job: the block mounts INSIDE the page's own "typed once,
saved with this job" drawer, `bare`, and hides behind the page's existing `fHow` select
(delivery → on; will-call / set-aside / restock → off and out of the document), or is
declared always-on where a truck is always coming (`framing/the-load`, `masonry/yard-call`).
What it WAS is a REPLACE, not a mount — the 2026-08-16 panel's line: six order pages already
shipped the hand-rolled half (`fAccess` textarea + `fSigner`, and on two of them `fMeet`),
and a block beside them is two gate boxes on one page. So the boxes LEFT those pages, the
job card grew `carry:` (kept, never painted) + `stash()`, and the block seeds itself from
what the card still holds — once, and a seeded record is written even when emptied, because
a cleared block must never get its June gate code back. **The block itself is v2 now**, held
to the receiving lens's three: driver lines first (gate → who to call when the gate's wrong
→ the paperwork → where it lands → who signs; off-the-truck and the window after), the
not-before control as the ONE clock printed on the gate line (the placeholder stopped
teaching the double entry), and the PAPERWORK layer as multi-select chips that ASK the
supply house rather than claim a status ("Tell me if our COI isn't on file with you yet" —
the getting-in handback rule one level down, asserted ask-first by the gate). And a second
LOAD CLASS: `load:"small"` swaps where-it-lands / how-it-lifts for one custody axis (handed
off · left at a drop point · with the super · security) — "'Forklift on site' is not a real
option for a box of J-hooks." **Six of the eight order pages now carry the block** (plumbing,
sitework, electrical, low-voltage, framing, masonry). **Named remainder, by decision:**
`concrete/mix-order` is NOT a flatbed — a ready-mix truck is chute / pump / washout and its
"Getting in, staging and washout" textarea is the right shape until a concrete lens says
otherwise; `hvac/truck-stock` is a van restocked at the shop (panel, do not mount); `av/consumables`
and `av/cable-list` never carried a delivery half at all and get one only if a wish asks.
The weight band on the heaviest piece stays OUT — still the operator's call. ~~(2) The sub → owner
access / escort / badge request~~ — **SHIPPED 2026-08-15 as `<trade>/getting-in.html`, all
ten kits; see §GETTING IN below.** ~~(3) The long-lead **gear chase**~~ — **SHIPPED 2026-09-01 as
`<trade>/long-pole.html` on four kits; see §THE LONG POLE below. And the entry above was
wrong about the two things that mattered most, which is why the ship loop reads the roster
before it builds and not after.** It ranked a *what I'm asking for* axis (ship date ·
released · dimensions and weight · approved schedules · freight) and a status ladder to
carry it. **A four-lens panel scored it 8 / 7 / 8 / 2 and killed the ladder unanimously**:
*released*, *in fabrication* and *shipped* are not facts the user holds — they are
hearsay, third-hand and weeks stale, and rendering one in confident type with a settled
edge is a clearance manufactured by an interface. And the AXIS was right in its list and
wrong in its framing: the sending lens — *"email six braids five questions and the reader
answers one; breaking the braid is the page's whole job"* — and the RECEIVING desk,
answering with no idea we had the page open — *"all five boxes ticked on all forty lines
is not an ask, it's a survey, and it goes to the bottom"* — arrived at the same shape from
opposite ends. It is not an axis you tick. **It is the message's spine, and the message
carries exactly one of them.**
~~(4) **The forward leg on the new boundary.** Ten trades can now ask a building for a night,
and nothing reads the answer back the way `answer-back.html` reads a rough-in ask — the
owner boundary is served in one direction only, and the GC's copy is the one that gets
FORWARDED rather than sent.~~ — **SHIPPED 2026-08-28 (C3675) as `shared/whatcameback.js` on
every `getting-in.html`; see §GETTING IN → THE RETURN LEG. This line outlived its ship by a
week, which is the roadmap-is-not-a-record scar one more time.**
~~(5) **The owner's vendors** — the most expensive miss on any close-in list per the matrix:
kitchen, med-gas, signage, EVSE, owner AV/FF&E all show up after the pour asking where
their stub is.~~ — **SHIPPED 2026-09-05 (C3707) as `gc/by-others.html`; see §BY OTHERS
below.** What INTERFACE has left is, for the first time, nothing the matrix names — the next
rung on this axis comes from a wish or from the EVO loop, not from the roster.

## THE LONG POLE — one question, and no rung of it is hearsay (2026-09-01)

`<trade>/long-pole.html` on **electrical · HVAC · plumbing · doors** — one page file, four
`TOOLKIT_LONGPOLE` configs, shape #3 (`shared/rowlog.js`), **no new mechanism**. The gear
that sets your date, in one list; then one message that asks ONE question about the few
lines it is actually about, instead of a sixth *"any update?"* that asks five and gets one
of them answered.

**THE PANEL IS THE ENTRY.** Four lenses, scored independently, no coordination: a
commercial EC project manager (8), the project-management desk at a distributor answering
from the RECEIVING end (7), a mechanical PM as the generalization lens (8), and a skeptic
handed this book as weapons (2, KILL AS PROPOSED). Three of the four wanted the page. All
four killed the design it was proposed with, and the skeptic was right about the half that
would have shipped a defect.

**1. EVERY RUNG IS HIS OWN ACT OR HIS OWN EYES.** The ladder is `Asked → Nothing back →
They told me something → It's here`, and that is the whole correction. *Nothing back* earns
its own rung because it is the fact that turns a chase into a record and it is a fact he
owns — he asked, and nobody answered. What the factory said lives in `told`: free text,
THEIR words, with a name on it, and it is never a state, never parsed, never counted. The
same verbs are LEGAL in `asks`, because a question aimed back at the man who owns the
process is §GETTING IN's handback rule one level down — *"have you got the approved set,
and did you release off it?"* is a question; a box reading APPROVED is a second submittal
log and dead on contact.

**2. THE QUESTION IS THE SUBJECT LINE.** Not a spine printed above the list — LINE ONE, the
only line a lock-screen preview is guaranteed to show, which is where the receiving desk
said he triages from. `Rosewood ES — anything you still need from us — Sep 1, 2026`. Under
it, *"Just the one thing this time, on 2 of these:"* and the two lines. The ask list is
ordered by **how fast the answer comes back, cheapest first**, and that ordering is the
page's only real intelligence — it came from the receiving desk unprompted: *"he asks the
expensive question when he needed the cheap one. Say 'pouring 10/14, need pad dims and
weight on MSB-1' and you get it this afternoon. Say 'any update' and you wait three days
for a paragraph."* Dimensions and weight are in his own file. A ship date is not; he has to
go ask a factory and relay it back.

**AND THE FIRST QUESTION ON EVERY KIT IS THE ONE NOBODY WRITES: *anything you still need
from us*.** Both field lenses named it independently — a large share of stalls are the
vendor waiting on OUR colour selection, OUR field dimension, OUR signature, or a credit
hold nobody phones about, and nothing in a chase ever asks. It is the same class as the
`holds` line, and it is asserted as `asks[0]` by the gate.

**3. `told` HOLDS ONE VALUE AND KEEPS NO HISTORY, and this is the sharpest thing the panel
changed.** A dated, formatted, repeatable *"here is what you told me and when"*, regenerated
six times over four months with a TSV export, is a delay-claim exhibit — and this program
bans backcharge-adjacent content outright (two framing tools died on it). The receiving desk
named the price the user pays for it: *"my answers get vaguer. 'Week of the 14th' becomes
'Q4, subject to factory confirmation, no commitment.' You made the record look like
discovery and you got worse information for it."* So the field is overwritten. **A field
holding one sentence cannot become an exhibit, because there is no history in it to paste.**
If he needs that record, his office's system owns it. The gate overwrites `told` and
requires the previous value to be gone from the message, the spreadsheet copy AND storage.

**THE RECEIVING DESK'S OWN WORD, AND IT IS LOAD-BEARING: *promised* is banned outright.**
The field is what he was **last told**. Turning a window into a date, or *tracking* and
*should* into *will*, is the thing that makes a chase a claim.

**WHAT THE MECHANICAL LENS ADDED THAT ELECTRICAL COULD NOT SEE.** His gear rolls in a door
on a pallet jack any Tuesday; HVAC's goes up by crane, shares that crane with steel and
glazing, and has to land AFTER the curbs are set and BEFORE dry-in and the screen wall. So
**"do not ship before" is as load-bearing as "must be here by"** — a unit that arrives early
is laydown storage, insurance and a second rig on six thousand pounds — and *"hold it,
we're not ready"* is a question a mechanical PM asks monthly that the roadmap's vocabulary
had nowhere to put. Start-up is its own lead time and its own question, because warranty
does not commence until it happens. Doors got the trade whose *"four different people inside
one house"* is literal rather than a metaphor for four latencies — hollow-metal detailer,
hardware writer, wood plant, glass shop, one order number, four clocks — so its fourth ask
names the shop out loud.

**WHERE IT SITS BESIDE `doors/before-they-ship.html`**, because the two are one letter apart
in a hurry: *before-they-ship* is the FIELD MEASURE going out before anything is welded —
your tape, your words, the hand it really swings. *The Long Pole* is what happens after the
order exists: the metal is somewhere and you need one fact back. A measurement you are
sending, versus a question you are asking.

**FOUR TRADES AND NOT SIXTEEN, and the exclusions were unanimous where they mattered.** The
EC lens and the mechanical lens independently produced the same list — electrical, HVAC,
plumbing, doors YES; masonry small (cast stone and brick blend, a three-item list); av and
low-voltage at half intensity, one PO rather than six sends; roofing, sitework, flooring a
*material availability* variant with no release step; framing, concrete, painting NO
(commodity, days out, or on a shelf); creative already served by `still-waiting-on`.
**And GC gets it never, from both of them, unprompted: he OWNS and NUMBERS the procurement
log, so a GC copy is the textbook double-entry death.** Landscape is a trap worth writing
down — a specimen tree is a genuine six-to-twelve-MONTH hold, but the vocabulary is tagging,
dig window and season, not release and freight. That is a different page or none.

**KILLED AND STAYING KILLED:** any lead-time table (wrong for his manufacturer this quarter,
and pasting it makes him look stupid to his own PM) · a manufacturer, distributor, rep
agency or branch as a picker or a seed — impersonation with a shelf life, and it turns his
chase into a spec · weights and dimensions of our own · a submittal number, PO or
sales-order number as CONTENT (they ride as an ADDRESS, the `before-they-ship` rule) · any
elapsed-day count, overdue label or promised-versus-actual delta, including parsing his own
free-text dates · money and the word *quote*. All gated in
`tools/toolkit-gates/long-pole.mjs`, **445 checks across four trades**.


## BY OTHERS — the owner's vendors, one message each, and the rep on it (2026-09-05)

`gc/by-others.html` — one page, one `TOOLKIT_BYOTHERS` config, shape #3 (`shared/rowlog.js`),
**no new mechanism**. Everything on the job marked BY OTHERS / NIC / OFCI that still needs a
hole in the super's slab or a box in his wall: one row per piece, the vendor's name as the
receiver, one message per vendor — the sheet, the walk, the crate — before the gate.

**THE PANEL IS THE ENTRY, AND IT WAS NOT UNANIMOUS.** Four lenses, independent: a GC super
(7, BUILD_WITH_CHANGES), the PM at a foodservice equipment contractor answering from the
RECEIVING end (7, BUILD_WITH_CHANGES), an owner's rep who holds the OFCI matrix and is the
person this message gets forwarded through (7, BUILD_WITH_CHANGES), and a skeptic handed
this book as weapons (5, EXTEND THE CLOSE-IN LIST INSTEAD — *"I went to kill it and the page
is mostly already built"*). The 5 is recorded intact: the skeptic was right that every
MECHANISM exists on `gc/rough-in-request.html`, and wrong that it is the same JOB — the
Close-In List's row is an area keyed to a sub who has to DO something under contract; this
row is a PIECE keyed to a company outside the contract who has to TELL the super something,
with a different ladder, a different closing, a receiver he has to name, a rep he has to cc,
and a per-send gate day the sub-facing page must never carry. Bolting all of that onto the
Close-In List is §FIELD-COOL's *"if it does two things it is two tools"* — the skeptic's own
citation, cutting the other way. What the skeptic's cut DID decide: the gates are
`TOOLKIT_ROUGHIN.milestones`, read at load — one list, two tools, or they drift — and the
Close-In List's own "Vendor rough points" ask stays exactly as it was, the trip-wire on the
sub list. The page reads the Close-In List's gates and adds nothing to it.

**1. THE ONE THING ALL FOUR NAMED FIRST: THE VENDOR'S NAME IS THE RECEIVER.** The Close-In
List's "Owner vendor / rep" is one bucket for five companies. *"One list to the cooler guy,
the hood guy and the sign guy is the same as sending it to nobody"* (the super); *"I only
read the lines with my name on them and I miss the one that mattered"* (the receiving desk).
So the vendor is typed once, learned, becomes a button AND the To: line, and a message never
goes to more than one of them — asserted BY VALUE: the other vendor's name and rows must be
ABSENT from the message. **And the field is never seeded.** A manufacturer, distributor or
rep agency in a seed is impersonation with a shelf life (§SCARS, the branch picker), and the
names on the owner's matrix change every job; the gate counts the chips under the vendor
field before a man types one and requires zero.

**2. THE REP IS ON IT, AND SHE IS THE To: WHEN THERE IS NO NAME YET.** Three lenses,
independently: he has no contract with the kitchen guy, so his text alone sits behind the
jobs where the man asking is the one paying; with the owner's rep cc'd it moves to the top,
and *"the rep sees that the GC asked before the pour, which ends the 'who never coordinated'
argument later."* And the super's own line, the one he would fight for: *"half the time I
don't have the vendor's name until three weeks after the pour, and the only message that
produces him is the one to her."* So `To:` offers each named vendor, then the rep — the
roll-up of everything still open, by vendor, with the nameless pieces under their own
heading and one ask on those: *who's your person on it, and a day they can walk it with my
plumber — the name is the whole ask.* The owner's rep scored it 7 because she has never once
received the document it produces, and wanted it on every job.

**3. ASK FOR THE DOCUMENT, NOT THE PARAGRAPH — the receiving desk changed the asks.** The
roadmap's lead ask was *"where it lands and what it needs — power / water / drain / gas /
data / vent / floor sink or depression / blocking."* The receiving desk killed it as the
lead in one line: *"that asks me to re-derive my equipment schedule in a text. I will say
'it's on the drawings' and stop answering. The answer to that question is a document that
already exists — ask for the document."* The ask that gets a PDF back in an hour is *send
me the rough-in sheet you already sent the architect — sheet and rev, or tell me it isn't
drawn yet.* The asks are ordered by his own timings, cheapest first — which of these are
yours (one line, an hour; *"the most common answer I give"*) · the sheet and rev (a PDF, an
hour) · a name and a day to walk it (a day) · heaviest piece, biggest crate, the opening it
needs (an hour off the cut sheet) · and the service list LAST, for the piece that has no
sheet. The gate asserts the sheet is asked before "where it lands", and that the page names
the set the super is building off (*"I'm building off P-101 rev 4 and I've never seen
yours"* — his line, so the vendor can say in one text whose set is stale). **Pieces ride by
their tag off the equipment schedule** (K-4, OF-14) and the owner's room number — the
owner's rep's blocking demand, and her reason: *"it is the first GC document that reads my
numbering back to me."*

**4. THE GATE'S DAY IS A FACT ON LINE ONE, TYPED ONCE, NEVER ON A ROW.** §THE INTERFACE's law
is *a milestone, never a date*, and the rows keep it. But the owner's vendor is not on the
GC's schedule — *"'before the pour' means nothing to me; 'slab pours Sep 5' I can act on"* —
so three lenses independently asked for the day to be typed once at send time, in the
subject line, as a fact he is telling them rather than a deadline he is giving them. It
lives in the Send card, rides on line one verbatim, is on no row, in no spreadsheet column,
and nothing counts from it. And the SEND date is NOT on line one: the super killed *"Sep 5
hanging off the subject with no noun"* — his phone stamps the text; that line is for the man
reading it. His own record (the "everything on the list" copy) keeps today's date, because
that one is his.

**5. KILLED, AND STAYING KILLED, each by name in `tools/toolkit-gates/by-others.mjs`:** the
**"Nothing back"** rung — three lenses in the same words, *a lateness label wearing a
status; nobody's act and nobody's eyes; blank-after-Asked already says it* · **"on the
owner's schedule, not mine"** in the closing — all four: *who-eats-it with the dollar sign
filed off* · a **"this is the one that moves the date"** flag — the owner's rep: *printed to
an outside vendor that is "your piece is delaying my job", the opening line of a delay
exhibit* — so there is ONE flag, *This one first*, and it says what the super needs ·
**"when you set it / when you need the room"** as an ask — the receiving desk (*"the owner
tells me when I set; wrong receiver"*) and the skeptic (*no close-in gate above it, and it is
the one ask that turns the row into a delivery chase for gear the GC never bought — the long
pole in a hat, which the GC gets never*) · **"anything you still need from us"** as a ROW
ask — open-ended, gets silence; it lives in the closing, where the gate requires it ·
**copier and vending** in the seed (no hole in the slab or the wall, no gate, no row) ·
**med-gas outlets and access control** in the seed — the owner's rep: on every hospital job
those are the furnish-vs-install fight, and *"the page must not pretend to settle it"*; a
super can still type them, and then it is his call · and **"core drill" in the SENT
document** — both receiving lenses: *"I forward that to the owner's rep with 'your GC is
threatening me' and now it's a fight instead of an answer; nine times out of ten the hole in
his set is nobody's doing but the trailer's."* The consequence survives as a fact about the
gate — *what I don't have before the gate isn't in it* — and "core drill" stays in the page's
own copy to the super, where it is his word.

**THE LADDER IS `Asked → Got it → It's in`, and blank is *not sent yet*.** Every rung is his
own act or his own eyes (§THE LONG POLE's law, gated against factory verbs AND against
"nothing back"). *Got it* is his sheet in your hand OR his marks on your deck — the walk
folded into one rung on the super's word. "Not theirs" is not a rung: it is the answer the
receiving desk gives most, and it is his act to open the pencil and put the right name on
the row, which keeps everything else. `told` holds one value and keeps no history — the
long pole's exhibit rule, asserted the same way (gone from the message, the spreadsheet copy
AND storage).

**WHY GC ONLY.** The sub's path to the owner's vendor goes through the GC: the EC asks the GC
on the Close-In List, the GC asks the vendor here. No other kit carries this page unless a
wish says a sub talks to the owner's vendor direct. The rider sweep over every kit's
`rough-in-request` receivers found nine owner-class buckets, and all but GC's are the OWNER
himself — property manager, homeowner, owner's rep — one party, correctly one bucket;
sitework's "Owner / owner's vendor" is the only other mixed one, and its asks to it are
owner asks. The "one bucket, five companies" defect was GC's alone.

**GATES:** `by-others.mjs`, 198 checks — the static bans over the config (no factory verb,
no "nothing back", one flag with no schedule word, the killed asks absent, the sheet before
the paragraph, the closing carrying the sheet-and-rev line and the whose-is-it line and the
half nobody writes, no gate list of its own, no no-gate seed, no real house, no claim word)
and the drive at 390: two vendors, a nameless row and a row already in; Dave's message
carries only Dave's open rows, by tag, with the rep cc'd and the set named, and none of Lou's,
none of the nameless, none of the one already in; the day on line one and on no row; Lou's
message the mirror; the roll-up to the rep with all four open pieces, by vendor, the
nameless under NOT SET, the one already in absent; his own record with today's date and every
row; `told` overwritten in message, spreadsheet and storage; the ladder to the top and one
past; reload; Clear taking the rep and the day with it; four widths and the 44px floor.
**AND THE GATE'S OWN VALUES HID TWO DEFECTS THE PLACEHOLDER'S WORDS EXPOSED** (the C3706
rule, one page later: a gate that fabricates its inputs owes a second pass over the real
ones). Driven with the page's own example words — the rep typed as *"Priya — owner's rep"*
the way the placeholder teaches — the cc line printed *owner's rep* twice, and the vendor
message printed *asked* on every row: the super's own rung, which is his record and not the
vendor's business, and on the skeptic's read a record of when you asked. The gate's rep was
*"Priya, owner rep"* and its rows were tags, so it saw neither. Both fixed, both asserted
now — the tag is appended only when his words don't carry it, and the rung prints on the
roll-up to the rep (she needs to see which ones he asked direct) and on no row to the
vendor himself.

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

### THE RETURN LEG — shipped 2026-08-28 (C3675), and NOT as the page the roadmap predicted

`shared/whatcameback.js`, mounted as an INTAKE on all fifteen `getting-in.html` pages —
two lines added to one page file, **zero new per-trade vocabulary**, because the rows are
not configured anywhere: they ARE this trade's `TOOLKIT_GETIN.need` and `.heads`, exactly
as ticked. Untick an ask and its answer row goes with it.

The private roster had ranked this rung as *"nothing yet reads an access ask back in the
way `answer-back.html` reads a rough-in ask."* A four-lens panel (a building engineer, a
GC super, the foreman who SENDS these, and a skeptic handed the program's own rules as
weapons) **killed that build twice over**, and the two kills are worth keeping because
they generalise to every future INTERFACE rung aimed off this toolkit's own population:

- **THE ADOPTION KILL — the receiver is not our user and never will be.** Grep every
  kit's `phTo`: building engineer, chief engineer, property manager, director of
  security, owner's rep. Not one tradesman, and even the GC kit sends its copy to the
  owner's rep. The building engineer's own words: *"I do not click links from
  contractors I don't personally know, on the phone that's tied to my building's
  systems."* He hits reply and types, in forty-five seconds. **Nobody outside this
  toolkit's population has ever been asked to tap a button in this program, and that is
  not an oversight — it is the load-bearing reason these tools get opened at all.**
- **THE PERMIT KILL.** `getting-in.mjs` fails the build if the ask ever says "approved",
  "confirmed", "granted". A receiver-side answer page exists precisely to BE the grant,
  and a tick beside *"we have to touch the fire alarm"* is then an approval manufactured
  by an interface instead of by the building's own numbered permit. The GC super's scar:
  a one-word *"yeah that's fine"* meant to cover access got read as covering the torch
  too, nobody called the alarm company, and the floor evacuated at eleven at night.

All four lenses then converged, independently, on the same surviving shape — **it runs on
our side, on the reply he ALREADY got by whatever channel he got it.** The foreman
described the build before he was shown it: *"assume he keeps texting back 'yeah that's
fine' forever, and build the tool on MY side instead. Not 'he said no' — 'he said nothing
about the freight elevator.'"* That is `shared/reconcile.js`'s own best output — what he
never mentioned — moved to the boundary where silence costs a crew at a locked door.

**THE FOUR RULES IT SHIPPED UNDER, each demanded as BLOCKING by a lens:**

1. **TWO LADDERS, NEVER ONE.** The logistics asks get a real answer ladder — *Got it ·
   Already open · No · Not theirs* — and every flagged line naming a PERMITTED activity
   gets a ladder with **no affirmative rung at all**: *They named who owns it · Not that
   night*, and nothing else, ever. The most this page will ever record about hot work is
   the name of the man who owns the process. A future cycle giving the flagged list a
   "got it" rung to make it consistent with the other list would look like a tidy-up and
   would be the defect. `tools/toolkit-gates/what-came-back.mjs` drives every permitted
   line through its ENTIRE ladder and fails on any rung that reads as an affirmative.
2. **SILENCE IS THE DEFAULT AND IT PRINTS FIRST.** An untapped row is not a no and not a
   yes. `NOTHING SAID ABOUT THESE` leads the brief, above anything that reads like good
   news, and carries the sentence that is the whole finding: *silence is not a yes.*
3. **THE WINDOW THEY ACTUALLY GAVE, AND A NAME AT THE DOOR.** The receiving and sending
   lenses named the same missing sentence without conferring. The brief opens with the
   window they gave printed **against the one we asked for**, plus who will physically be
   at that door and their cell. *"Five guys standing at a locked door because 'fine' got
   treated as a real answer is the single most expensive failure in this whole exchange."*
4. **AN ANSWER GOES STALE, AND THE PAGE CANNOT PING ANYBODY.** It has no server and never
   pretends otherwise. What it does is know the answer is four days older than the night
   and hand him **the day-of check** — the short message HE sends, listing only what is
   still silent and what he was told to go chase.

Nothing it emits is a permit, a booking or an approval, and the document says so every
time it carries a flagged line. The gate bans the grant words from both documents.

**AND CLEAR HAS TO REACH THE ANSWER** — the defect this module's own opening argument
would have shipped with. The ask's Clear wipes the night, the rooms and the ticks so a man
starts the next job on the same phone; the answers lived in their own key and survived it,
so re-ticking the same three asks for a DIFFERENT building brought back the last
building's window, the last building's man at the door, and last week's rung on every row.
That is exactly the second version of the truth the intake-not-a-page rule exists to
refuse, arriving through the back door. The hook is bound after the engine's own handler
and **re-reads the ask rather than trusting the click**, so a cancelled confirm moves
nothing. Asserted, and the assertion was proved to bite by removing the fix and watching
it fail on all five fields plus *"a re-ticked ask came back already answered."*

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
4. **Before I Export** (checklist → request) — ✅ **SHIPPED 2026-08-29** as
   `creative/before-i-export.html`, and the panel that graded it did not agree with the
   roster or with itself. It wins by ASKING and never asserting — but the FRAME the roster
   implied was killed by the field lens before a line was written: *"'What shape do you
   need?' asked the night before a render tells a client you cut the whole thing without
   knowing — that's not diligence, that's a confession."* The page therefore opens with
   STATEMENTS (what the cut already is, every picker starting neutral) and asks only under a
   second heading. The roster's own sorter — *does it decide the render* — was killed too:
   it flagged fifteen of twenty-two, and *"fifteen of twenty-two flagged means nothing is
   flagged."* The sorter that shipped is **do I have to open the project again.** **AND THE
   ONE THE ROSTER GOT BACKWARDS:** *What's in the drop* was deferred here as *"a second
   output mode, not a sixth page"* — the boundary lens showed that is wrong in one word. It
   is not a second MODE; it is the other side of the render, addressed to a different
   moment. **It shipped as its own page on the same engine on 2026-09-03 — see #8, and read
   what the panel took off it before believing this paragraph.**
5. ~~**Shoot Day Confirm**~~ → see below; the participant half is still owed and now sits
   behind *What's in the drop*.
6. **Shoot Day Confirm** (checklist → request) — ⚠️ **HALF SHIPPED 2026-08-15** as
   `getting-in.html`, and the honest record is that it shipped the **venue half** — the ask
   that gets you into somebody else's building — not the whole rung. The half still unbuilt
   is the **participant-facing** one: the short "how the day goes" note to talent, a client
   coming to set, or a location owner (call time, where, how long, what happens, who to
   ask for). Every one of this trade's 4 tools and 13 documents points at a payer, a venue
   or the next editor; nothing points at the person who has to SHOW UP. Survives ONLY
   because it is deliberately **not a call sheet** and must never grow into one;
   StudioBinder owns and numbers that document.
7. **The Write-Up Setup** — ✅ **SHIPPED 2026-08-15** (`write-up.html` + `docs.js`), and it
   was never on this list, which is the finding. The panel that built this roster was asked
   what to BUILD NEW and answered well; **nobody asked what this trade was OWED.** Creative
   shipped with two of the five document engines and ran live carrying three of twelve
   shared modules while DOCS work landed on the other nine trades — a gap no ranked roster
   could surface, because a roster of ideas has no column for a sibling's engine you never
   inherited. The check that finds it is mechanical and takes one command: grep every
   trade for every `shared/*.js` it loads and read the holes. **Run it before ranking
   anything, on every trade, forever.** This cycle took creative from 3 of 12 shared
   modules to 5 (`docspec` and, riding with it, `find`). `checklist-request` and
   `pickfilter` landed with *Before I Export* on 2026-08-29, taking this kit to **10 of the 12
   shared modules**. **`package` IS NOT A HOLE HERE AND THAT IS NOW ON THE RECORD** rather
   than rediscovered every sweep: Total Package is a WAGES-AND-FRINGES reckoning, and this
   trade's own rails ban rate cards, day rates, kill fees and deposit splits outright — the
   one absence on this kit with a reason, which is a decision, not a gap. `reconcile` is
   already here (`notes-back`). What remains genuinely absent is construction furniture:
   `jobcard`, `dropoff`, `holdtest`, `draft` — a freelancer has no job trailer, no gate code
   and no test port.
8. **What's in the Drop** (checklist → a message that asks for nothing) — ✅ **SHIPPED
   2026-09-03** as `creative/whats-in-the-drop.html`, and **the panel scored it 7 / 6 / 2
   with one lens voting to KILL.** The page is smaller than the rung because of the 2.
   **"WHO SIGNED" IS NOT A BLOCK** — the receiving lens ranked it above the
   deemed-acceptance clause as the riskiest thing in the proposal, because *"Approved by
   [name] on [date]" is a signature*: written by one party, and the moment the client
   forwards it, the OTHER party's name is on an approval record that exists nowhere else.
   It survives as ONE header field in the sender's own first person — *the last yes I've
   got from your side is …* — printed after the lists rather than under the heading (read
   first it puts the receiver in auditor mode before he has opened a file) and never
   without the invitation to correct it. The word *approved* appears nowhere on the page
   and the drive asserts it. **THE WORD "DELIBERATELY" WENT WITH IT:** *"nobody says
   deliberately about something they're volunteering out of generosity — you say it when
   you're pre-empting a complaint."* Same family as *per scope*, and both are now in the
   banned list the drive checks. **THE SIBLING'S ASK-COUNT BRAKE DID NOT COME ACROSS** —
   this page asks the client for nothing, so there was nothing to count and porting the
   mechanism would have been cargo-cult. What it brakes instead is **the FENCE**: it
   counts absences against inclusions and says on the glass when the message has stopped
   being a delivery and started being a list of upsells. Both dissenting lenses reached
   that failure from opposite ends. **AND THE DISSENT'S OWN GROUND IS RECORDED BECAUSE IT
   IS RIGHT:** a transfer page already lists the FILES. What nothing anywhere generates is
   **ABSENCE** — the skeptic called it *"the one inch of real territory"* and the working
   editor called it *"drop that line and this is just a nicer-looking here-you-go"*, which
   is the strongest agreement this exercise can produce, since they agreed while
   disagreeing about everything else.
9. ~~**Shoot Day Confirm — the participant half**~~ → still owed, and now the top unbuilt
   rung on this trade (see #6). Nothing in this kit points at the person who has to SHOW UP.

Deferred with reasons: *Turnover Sheet* (narrow — real only for a first job with a new
finisher) · *Booking Confirm* (a different boundary — hiring, not client delivery, and one
inch from rate data we cannot own).

**THE ENTRY THAT USED TO STAND HERE CONTRADICTED THE PARAGRAPH FOUR LINES ABOVE IT FOR
FIVE DAYS, and an adversarial lens found it, not a gate.** Item 4 said *What's in the drop*
was *"not a second MODE… its own page"*; this list still said it *"folds into Before I
Export as a second output mode, not a sixth page"*. Both were in §CREATIVE, both were read
every cycle, and the roadmap comment in `creative/tools.js` had already moved past both.
**A ROADMAP IS NOT A RECORD (§SCARS 2026-08-15) covers striking a rung when it ships; it
did not cover striking the DEFERRAL when the deferral is reversed**, and a reversal leaves
two live entries where a ship leaves one. Whoever reverses a deferral deletes it in the
same edit.

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

### 2026-09-05 (C3708) — SIXTEEN SHELVES OUTVOTED THE SEVENTEENTH'S AUTHOR ON HIS OWN PAGE
`shared/docsindex.js` is generated from the SHARED documents' names and akas and
lent back to every trade that carries the document — "the man gets seventeen
authors' words for his own shelf". The guard in `poolTerms()` asked one question:
does the RECEIVING document already have this word? It could not see the rest of
the shelf, and it structurally cannot see the part that matters, because **every
trade-specific document is invisible to the generator** — the pool is built from
the shared eleven, so a word written on `the-day-we-couldnt-pave` is not in the
pool's world at all.

What that costs showed up the first time this rung was worked. Paving's author
moved `"delay"` onto his own lost-day document and off the general notice —
masonry's 2026-09-02 reasoning exactly, the trade's own document owns the word a
man in that trade means. Typing `"delay"` still led the general notice. Removing
`"delay notice"` too did not fix it either. The word was coming back from
**sixteen other shelves**, which had voted it onto `delay-notice`, and the pool
was handing it to a document whose own `aka` and name no longer carried a trace
of it.

**A CLAIM BEATS A LOAN.** `poolTerms()` now reads what the whole MERGED shelf's
own authors claim and refuses to lend a word another document there already owns.
A term claimed twice on one shelf is left alone — that is the shelf gate's
assertion A and not this rail's business. The pool exists to widen a man's
vocabulary; it was never entitled to narrow his author's.

**AND THE GATE FOR IT WAS GREEN WHILE THE DEFECT WAS LIVE.** The new pool-gate
assertion passed on its first run *and* passed with the engine guard deliberately
removed, while the shelf gate went correctly red beside it. It was reading
`out.poolOnly` — the engine's own answer — from a position in the page script
where that object had not been filled yet, so its "was this term lent?" test was
always false and it could only ever report success. This is SCAR-C3702 again in a
new costume: **a probe whose verdict depends on the value it is supposed to
audit.** The reason it was caught at all is that the control was run against the
real engine with the fix backed out, rather than against a re-authored fixture.
**Run the negative control by breaking the SHIPPED code, not by simulating the
break** — a fixture proves the detector can fire, and only backing out the fix
proves it fires on THIS defect. Guard off: red. Guard on: green.

### 2026-09-05 (C3707) — A FILTER APPLIED FROM onChange IS A LOOP WITH NO FLOOR, AND THE MOUNT GUARD WAS IN THE COMMENT
`by-others.html`'s `syncSelects()` ended by calling `applyFilters()`, which called
`rl.setFilter(...)` unconditionally. `setFilter()` renders; `render()` fires
`cfg.onChange`; `onChange` is `syncSelects`. The page's own gate blew the stack on
its first run (`RangeError: Maximum call stack size exceeded`) and the list on
screen stopped following the roll-up's grouping because the render that would
have painted it never finished. The sibling page (`long-pole.html`) never had
this bug because its `syncAskSelect` re-applies the filter ONLY when the pick was
invalidated — a floor I copied the shape of and not the reason for. The fix is the
rule: **an onChange handler may call the engine's `setFilter` / `setGroup` /
`render` only after proving the state changed** — here, the wanted filter keys
compared to `rl.filter()` first, and a handler that changes a value INSIDE the
same key list (the vendor, the question) renders explicitly once, itself.

And the same page, the same hour, hit the class this book has recorded three
times: the engine renders once inside `mount()`, before `rl` exists, and
`onChange` runs in that render. The guard (`if (!rl) return`) was in the file —
in a COMMENT above `rowsNow()`, copied from the sibling — and not in the two
functions that needed it. The page shipped its engine perfectly and every word
this file owned was dead: no To-select, no listeners, no restore, and Add still
worked, which is exactly why it looks fine. Rule: **the guard goes in every
function `onChange` can reach, not in the one that was copied.** Both were caught
by the drive, not by `node --check` — a page that dies at mount is syntactically
perfect.

### 2026-09-05 (C3707) — "COMMIT BY PATHSPEC" MEANS `git commit -- <paths>`, NOT `git add <paths> && git commit`
The working tree is shared with other lanes, and the index is too. This cycle's
`git add` named five files; the commit that followed carried **86** — the
archive-stewardship lane had staged eighty-one of its own between the cycle's
first `git status` and its commit, and `git commit` with no pathspec commits the
index, all of it. Caught by reading `--stat` before the push, undone with
`git reset --soft HEAD~1` (which puts every one of their entries back exactly as
staged) and redone as `git commit -- <the five>`, which commits those paths and
leaves the rest of the index alone. Rule: **on a shared index, name the paths on
the COMMIT, and read the stat before you push** — a `git add` by pathspec proves
nothing about what the next `git commit` will take.


### 2026-09-04 (C3706) — THE SEAM WAS THE FIRST DASH, AND EVERY TRADE'S OWN WORDS CARRY A DASH
`shared/reconcile.js` split every pasted answer line at the FIRST " — ": his line,
a dash, his answer. A request line is OUR words coming home, and our words carry
em dashes — paving's "The set I'm paving to — sheet and rev", and behind it
painting's 39 specs, framing's 21, av's 13, every kit on the rack. Split there
and the ask comes home cut in half, the join half-matches it, and an answer that
said Thursday lands as "couldn't place" or "not sure" — silently, on the return
leg, the loop the boundary pages exist for. The trade #17 field drive found it by
DOING the round trip (rough-in → answer-back → reconcile) with the trade's real
asks; 5 of 12 lost their answer. `reconcile-join.mjs` had been green the whole
time (135 checks) because every one of its rows was SYNTHETIC, joined with the
dash by the gate itself — a gate that fabricates its rows cannot see what the
real vocabulary does to them.

**THE FIX IS IN THE ENGINE, NOT IN 24 REWORDS.** parseAnswer offers every seam
(and the line uncut, because grouped by date the answer rides in the heading and
the line has no tail), and pair() adopts whichever cut a row matches, character
for character where it can; a line with one dash is unchanged. **THE CONTROL
READS THE RACK:** section 16 of the gate loads every trade's items.js off disk,
drives its real asks through the real module grouped both ways, and REQUIRES
dashed asks to exist — 217 checks, and a control that found nothing to test
would fail. Rule: a gate that fabricates its inputs owes a second pass over the
real ones.

### 2026-09-04 (C3706) — AN OVERRIDE THAT RAN BEFORE THE MOUNT WAS DEAD ON SIXTEEN TRADES FOR ITS WHOLE LIFE
`rough-in-request.html` read `areaLabel` and `phArea` out of the trade's config
and applied them with `querySelector('label[for="rl_area"]')` — BEFORE
`RowLog.mount()` had rendered `#bar`. Both queries returned null on every trade,
every day: all sixteen kits set the key, and not one of them ever reached the
glass — landscape's "Bed / area" was "Room / area", doors' "Opening / area" too,
and a paving foreman was asked for a room number and a "Height / run — 60 AFF ·
to the ceiling above the rack" on the page that sends his most important list.
Found by the field-driver auditor reading the bar, not by any gate (a label is not
a value; nothing asserts a label). The fields[] config now reads the trade's
words at mount (areaLabel · phArea · areaHint · specLabel · phSpec · specHint ·
placeLabel · phPlace · phNote · phTel · docBoundary), the patch is gone, and a
probe read "Bed / area", "Section / area", "Opening / area" off four hubs. Rule:
a querySelector patch applied "after render" is a smell — put the words where the
engine reads them.

### 2026-09-04 (C3706) — A DYING CYCLE LEFT A TRADE HALF-REGISTERED IN THREE SHARED FILES AND A STUB, WITH NO VERDICT ON DISK
C3705 added `paving` to `shared/toolkit.js` TRADES, `commons/commons.js`
COMMONS_TRADES and the deploy's TRADES + paths, wrote `paving/credits.*`, and
died. No hub, no tool, no panel, no roster line, no log line — and had those
three config lines ridden anybody's `git add`, every hub's kit switcher would have
linked a 404 and the deploy would have gone red on the missing hub. The next
cycle could not tell a considered write-in from a whim: the roster had paving at
41-55 as a write-in for #16, nothing more. Rule: **a stand-up's FIRST write is the
panel verdict into the roster, and the config lines land in the same commit as
the hub — never before it.** This cycle ran the panel before touching the stub,
and the stub's choice survived it on the merits (70 · 70 · 62 · 78).

### 2026-09-04 (C3706) — THE BRIEF'S GREP TALLY OVER-COUNTED, AND A LENS CORRECTED THE BRIEF
The candidate notes handed to the #17 panel said insulation appeared on seven
kits and exteriors on four — a grep over `*/items.js` for stems like `insul` and
`gutter`. The doctrine lens re-grepped and found THREE and ONE: hvac's hits are
line-set insulation, roofing's its own iso, masonry's cell fill; framing's soffit
is interior, concrete's gutter is curb-and-gutter, landscape's is the street. A
noisy tally in a brief comes back wearing the panel's authority (§THE PANEL,
C3702, the same mechanism from the other side). Rule: a count in a brief is a
structured tally with its query written down, or it says "a guess".

### 2026-09-04 (C3706) — A GATE'S OWN TWO RULES CONTRADICTED ON ONE ROW
`find-honesty.mjs` probes a name with its spaces taken out (JOINED) and wants
the engine to HEDGE; two lines down it probes every authored alias and wants
EXACT. The paving names row "String line" carries the alias "stringline" — the
paver operator's one word for the wire the machine's sensor rides — and the gate
called the honest label a defect. The JOINED probe now yields when the joined
form is a word somebody authored. Checked as a control: the check count did not
drop, because the alias probe already asked that question.

### 2026-09-03 (C3702) — THE APPEND MATCHED AN ANCHOR IT HAD ALREADY PASSED, AND `node --check` CALLED THE RESULT GOOD
A patch that added a data block to `creative/items.js` found its END anchor with
`s.index('id: "out"')` — a string that already existed **earlier** in the file, in
the sibling `beforeExport` block. End came before start, the slice duplicated 338
lines, and `window.TOOLKIT_ITEMS.theDrop` was assigned **twice**. Every check
passed: a second assignment to the same key is legal JavaScript, so `node --check`
was green, and the file on disk contained the corrected draft. The PAGE served the
first one, because the last assignment wins.

**Found by driving the real page and reading the item names off the DOM** — the
tick list showed the item the corrected data had removed. Nothing else would have
caught it: not the parse, not a diff read at a glance (338 added lines look like
338 added lines), and not the gates, which would have passed a coherent older
page.

**THE RULE, and it is two greps rather than a new tool.** When you patch by
anchor: assert the anchor is UNIQUE or that `end > start`, and after writing,
assert the file declares each top-level key exactly once —
`grep -c "TOOLKIT_ITEMS.<key> = {"` must return 1. A parse check cannot see a
duplicate. A count can.

### 2026-09-03 (C3702) — A GATE THAT WAS GREEN ON ITS FIRST RUN, AND THE CONTROL FOUND THE HOLE THE GREEN WAS HIDING
`no-clock.mjs` shipped and returned **118 documents driven, 0 carrying a clock**
on its first run. §SCARS 2026-08-28 already says an assertion never run as a
control is a guess dressed as a gate, so a real deemed-acceptance clause was
planted. It fired red on `creative/whats-in-the-drop.html`, on two independent
patterns.

**The SECOND plant is the finding.** Aimed at `plumbing/items.js`, it landed at
the wrong offset — inside `tag_es`, the trade's SPANISH vocabulary — and the gate
**stayed green on a page that was carrying the clause**. Twelve pages on this rack
load `shared/lang.js` and hold a second document behind `localStorage`'s
`toolkit.lang`, and the gate had only ever opened the first one. It now drives
every bilingual page twice and names the tongue in the failure; re-planted in a
row the ES document actually renders, it goes red on `[es]` while the EN twin
stays green.

**The control did not confirm the gate. It corrected it** — which is the only
reason to run one, and the reason a green first run is a question rather than a
result.

### 2026-09-03 (C3702) — THE BOOK CONTRADICTED ITSELF INSIDE ONE SECTION FOR FIVE DAYS, AND A LENS FOUND IT, NOT A GATE
§CREATIVE item 4 said *What's in the drop* was *"not a second MODE… its own page
on the same engine"*. Four lines below, the **Deferred with reasons** list still
said it *"folds into Before I Export as a second output mode, not a sixth page"*.
Both sentences were in the same section, both were read every cycle, and
`creative/tools.js` had already moved past both.

**A ROADMAP IS NOT A RECORD (§SCARS 2026-08-15) covers striking a rung when it
SHIPS. It did not cover striking a DEFERRAL when the deferral is REVERSED** — and
a reversal leaves two live entries where a ship leaves one, because the deferral
lives in a different list from the rung. Whoever reverses a deferral deletes it in
the same edit.

### 2026-09-03 (C3702) — THE BOOK OWES A BACKPORT RUNG THE GATE HAS EXEMPTED SINCE BEFORE THE RUNG WAS WRITTEN
§CREATIVE carries, as a named-so-it-is-not-lost BACKPORT rung: *"on `credits.html`
the tool link inside a credit entry measures 153×16 — under the 44px tap floor, at
every width"*, wanting *"a real control beside the text, not a taller word"*, swept
to every trade at once. Measured this cycle: `mobile-watertight` **passes
`credits.html` locally and live**, and has since **2026-08-10**, when the
tap-target check gained the WCAG 2.5.8 exemption for a target that sits inline in
a sentence — whose selector list names `.credit` explicitly, and which the credit
line matches twice over (it is also an `li`).

So the page, the gate and WCAG all agree, and the only thing that disagrees is the
book. **It is recorded as a DECISION rather than an owed rung**: an inline link in
running prose cannot be made 44px without wrecking the sentence around it, which
is exactly why the standard exempts it. What stays true is the underlying
observation — that link is the ONLY door from the wall to the tool. **If it is
ever built, it is built as a real control BESIDE the sentence, which takes it out
of the exemption and puts it under the gate.** Named here so the next module sweep
stops re-deriving a defect its own instrument says is not one.


### 2026-09-03 (C3700) — A PROBE WHOSE EXISTENCE DEPENDED ON THE VALUE IT ASSERTS, SO REVERTING THE CODE MADE THE GATE GO QUIET INSTEAD OF RED
`find-noise.mjs` class N10 asserts that a trailing word this page does not have is NAMED
without waiting for a separator — the promise rule 7 shipped. The first draft built the probe
as `(w1.length >= U && drops(w1)) ? read(...) : null`, reading `U` from the engine's own
`Find.underThumb` so the gate would follow the constant instead of hardcoding a 3. That is the
right instinct and it produced a gate that **cannot fail**: set the constant back to the
pre-change behaviour and `w1.length >= 99` is false, the probe is never built, N10 disappears
from the `by class:` summary, and the file prints **GREEN 363 checks**. The revert it exists to
catch is the exact input that silences it.
**THE RULE: a probe may read a constant to decide WHAT to type, never to decide WHETHER to
run.** N10 is now gated only on `drops(w1)` — a question about the DATA — and if the engine's
line sits above the probe word the promise is false and the gate is RED, which is what N0
("a surface that runs no probe is a RED, not a quiet pass") already says one level up.
**AND IT WAS FOUND BY RESTORING CODE, NOT BY READING IT.** The pair is red-verified in both
directions on the same 33 surfaces: engine at `UNDER_THUMB = 99` (the old unconditional
hold-back) → **N10 FAIL×33**, N9 green; engine at `0` (no hold-back at all, gate line forced to
3) → **N9 FAIL×33**, N10 green; engine at 3 → **GREEN 396 checks**. A gate nobody has watched
fail is a gate nobody has tested, and this one had already passed once while asserting nothing.


### 2026-09-03 (C3699) — A FINISHED RACK-WIDE FEATURE SAT IN THE WORKING TREE OVERNIGHT, CITING TWO SECTIONS OF THIS BOOK THAT DID NOT EXIST
C3698 built SEND end to end — the helper in `shared/toolkit.js`, one registration line in
each of six engines, four hand-written pages, a 349-line parity gate, an assertion in the
deploy, and the change to the mobile ship gate that keeps the bar measured in the state a
phone is actually in. Then it stopped. **No commit, no push, no cycle-log line.** Under six
hours later `git status` was the only thing on this machine that knew.

**Every rail we own watches the artifact, and the artifact is downstream of a commit.** The
deploy assertion it wrote fires on a push. The gate it wrote fires when a person types its
name. `mobile-watertight` is a PRE-SHIP gate and nothing was shipping. The books are the
system of record and the book said nothing. **A working tree is the one place in this system
where finished work and no work at all look identical.**

**The tell that survived, and it is the transferable part.** The runtime header cites
`av/AV_SOCIETY.md §THE PANEL, C3698` for the panel that scored the design, and `§SCARS
C3698` for the measurement that killed its first placement. Grep this book for `C3698`
before this entry: **zero hits.** Code that forward-references a record nobody wrote reads
exactly like code that cites one — the pointer has the same shape either way, and only
following it tells them apart. **A cross-reference from code into a book is a claim, and it
rots in the direction of looking true.** Both sections now exist, written from what C3698
left on disk and labelled with what it measured versus what this cycle measured.

**THE RULE THIS BUYS.** The well's `--claim` goes stale after 24 hours because a claimed and
abandoned wish looks served. A working tree has no such alarm, so the discipline is applied
by hand: **ship it or revert it inside the cycle that wrote it.** Half-shipped is the only
state this lane cannot see. And the first act of the cycle that finds one is to VERIFY, not
to trust — C3699 re-ran the gate from zero rather than believing a header that said it had
passed.

### 2026-09-02 (C3698) — SEND'S FIRST PLACEMENT WAS THE FIXED BAR, AND ONE MEASUREMENT KILLED IT
Recorded here from `shared/toolkit.js`'s own header, because the cycle that measured it
ended before it could write the entry its code already cited. **These numbers are C3698's;
C3699 did not re-measure the killed placement** — what C3699 measured is the placement that
shipped.

The obvious build puts Send beside Copy everywhere. On roughly half this rack Copy lives in
a fixed bottom bar, and that bar is a CLOSED BUDGET: at 320px a fourth control pushed one of
the others past the glass on **25 of 50 bar pages**, and the count readout — the label that
tells a man how many items he is about to send — collapsed to **0–23px on 44 of them**. None
of that is visible in a desktop screenshot.

So placement became a decision the runtime makes per page instead of a constant, and
fixed-ness is **READ off computed style up the tree, never guessed from a class name**:
`av/consumables.html` keeps its Copy in a `.dock`, not a `.bar`, and a class list would have
put Send straight back into the one place the measurement forbids. Copy in the flow gets
Send beside it; Copy in a fixed bar gets Send in-flow, full width, directly under the
document preview he just read — and the bar keeps its budget. A fixed-bar Copy with no
preview to anchor to mounts **nothing**, rather than clip the one button every page is built
around. `tools/toolkit-gates/send-is-copy.mjs` asserts both placements and that no
`.tk-send` ever sits inside anything `position: fixed`.

### 2026-09-02 (C3697) — THE RAIL EXISTED ONE LAYER DOWN, SO NOBODY BUILT IT WHERE THE WORDS ARE WRITTEN
`shared/docsindex.js` has refused, since the day it was generated, to POOL a term that
means two different documents — its own header says so, names the count (35 refused), and
the deploy regenerates the file and rejects a diff so the claim cannot rot. That rail is
real, it works, and it looks like coverage. **It is not.** Pooling is the last step: it
decides which of one trade's words get lent to another trade. Nothing at all stood between
an AUTHOR and a word that already meant something else **on the same shelf**, and the shelf
is the only thing a man ever sees.

What that cost, measured on the merged libraries the pages actually render:

- **19 ambiguous whole terms across 16 shelves.** `"damage"` alone on **12 of them** — an
  alias on `incident-report` AND on `damage-found`, whose NAME opens with the word. The pool
  had refused to lend `"damage"` to anybody for exactly this reason, correctly, while the
  shared library shipped it on both documents to twelve trades.
- **21 authored aliases, of 1,707 probed at the real search box, handed back a DIFFERENT
  document than the one their author wrote them on.** `"meeting"` on **16 of 16** — an alias
  on `meeting-minutes`, eaten every time by *"Toolbox Talk / Safety Meeting Note"*, because a
  NAME outranks an alias and that name carried the word. Every man on the rack who typed the
  most obvious word for *"I need the minutes"* got the safety talk.

**Neither is visible to any gate that existed.** `docspec-config` drives every document and
passes — each one composes. `find-honesty` drives the same box and passes — the LABEL is
honest either way, because "exact" is a TRUE statement about a tie. `mobile-watertight`
passes — the layout is watertight around the wrong answer. **A tie is not an error to any
check that grades one document at a time.** Only asking the SHELF to name one document per
word can see it, which is `tools/toolkit-gates/docs-shelf.mjs`, written this cycle.

**THE GENERAL FORM, and it is the part worth carrying:** when a rail is enforced at the
last layer of a pipeline, every layer above it looks covered and none of them is. Ask of
every rail we own — where is this ENFORCED, and is that the same place the thing is
WRITTEN? If not, the gap between them is unguarded and has been the whole time.

**AND THE FIX PAID FOR ITSELF AT THE LAYER BELOW.** With the authoring ambiguity gone the
pool could stop refusing: **302 → 304 pooled terms, 35 → 33 refusals.** `"damage"` is now
lent to all 13 trades holding `damage-found`, and `"call notes"` to `meeting-minutes`. A
rail that had been silently eating two good terms for months was not the problem; what it
was protecting against was.

### 2026-09-01 (C3692) — A BLOCK UNDER A FILTERED LIST NAMED A ROW THE LIST DID NOT SHOW, ON A LIVE PAGE, FOR WEEKS
`shared/rowlog.js` ships NAMED DOCUMENT FILTERS so a chase list can send a man only what is
still open and only what is HIS. The engine's own blocks obey that scope, and its comment
says why: *"a man must never read somebody else's problem inside a message addressed to
him."* A page's OWN `docFoot` is the one place that discipline can be lost, because it is
hand-written per page and the engine hands it the filter keys in `ctx` that it is free to
ignore.

**`framing/whats-in-the-wall.html` ignored them, and the drive that proved it took four
minutes.** Scoped to *not covered yet*, the document printed `1 PIECE OF 2 — NOT COVERED
YET` and one row — and then, underneath, **"STILL NEED FROM YOU — I can't put these in until
somebody gives me a number"** naming a piece that was **Covered**. It was already in the
wall. It was not in the body. The AV contractor reading it got a demand for a size on
something buried, **with no line above it to argue with**. And a flag does not clear itself
when a row goes in, so that piece had been asking for its size in every copy since the day
it was covered.

**The fix is two things and only one of them is the scope.** The block's own sentence — *"I
can't put these in until somebody gives me a number"* — is FALSE for a covered row under any
filter, so `stillOpen` belongs in the predicate regardless. Then the filters, so a filter
added to that page later narrows the block with it instead of quietly outrunning it.

**AND THE OPPOSITE CASE IS ALSO REAL, WHICH IS WHY THE RULE IS "SCOPE IT OR SAY SO."**
`roofing/whats-open.html` prints **OPEN OVER SOMEBODY — ring me before anybody starts
pulling ceiling** off every row on the roof. Narrowing a hazard list to whatever filter he
happened to leave on is the worse failure, so that block keeps its reach and now carries the
disclosure in its heading — *"every one on the roof tonight, not just the ones above"* —
which is what `masonry/wheres-the-wall.html` has done since it shipped. Its neighbouring
sentence, *"Everything **above** with a seal on it is TEMPORARY"*, was the part that had to
narrow: a sentence about what is above has to be true of what is above.

Gated at authoring time in `tools/toolkit-gates/foot-scope.mjs` — a page declaring
`filters:` whose `docFoot` reaches for the whole row set must narrow it by the filters the
engine handed it, or say so in the printed text. **6 filtered row logs, 2 were failing.**

### 2026-09-01 (C3692) — THE GATE FIRED ON THE SENTENCE THAT EXPLAINED THE RULE, AND THE SENTENCE CHANGED
`long-pole.mjs` reads each trade's config blind and fails on a claim word wherever it finds
one. Its first run went red twice on `electrical/items.js` — the warn block was disavowing
two banned words **by printing them**: *"no day count, no 'overdue'"* and *"a dated list of
what somebody promised you is a claim document."* The tempting fix is an exemption for the
warn block. **A rule that has to exempt the sentence explaining the rule is a rule with a
hole in it**, and the hole is exactly the size of the next author who writes a paragraph
about what the page does not do. The prose changed instead: *"no money on it, no running
count of anything, and no arithmetic: a dated list of the dates somebody gave you is a claim
document, and this is not one."* Same meaning, and the gate stays blind.

### 2026-09-01 (C3692) — A BLOCK THAT REPEATS THE BODY IS PADDING, AND IT TEACHES A MAN TO SKIM
Found on the new page's first real drive and swept straight back into the page it was copied
from. `THE ONES ACTUALLY STOPPING WORK:` under a message already narrowed to one question
listed **exactly the two rows above it** — the same message printed twice. The rule is that
it earns its place when it is a STRICT SUBSET of what the copy contains, and disappears when
it would only repeat it. `creative/still-waiting-on.html` had the same shape on its *"the
ones stopping work"* scope, where the block was the entire body, and it was the page this
one was built from.


### 2026-09-01 (C3681) — A HUB COPIED FROM A SIBLING KEEPS THE SIBLING'S COLOUR IN ITS :root, AND NOTHING ASSERTED IT FOR FIVE DAYS
Every hub is stood up by copying a sibling's `index.html` and patching the lines somebody
remembers — the title, the h1, the lede, the folder link. The `:root` block carries
`--flag`, `--tint` and `--deep`, and they are the sibling's. `doors/index.html` shipped at
C3674 with painting's `#29FF29` on its well button, its eyebrow and its focus rings, and wore
it until the trade #16 backport sweep compared every hub's `--flag` against its own
`trade.js` accent: fifteen matched, doors did not. Nothing in the deploy read the hub's
stylesheet; the trade's accent lived in one file and the hub's colour in another, and the
two were only ever equal by hand. **FIX:** `doors/index.html` wears `#B7BEDC`, and
`deploy_bridge.yml` asserts, per staged trade, that the hub's `--flag` hex equals the
`trade.js` accent hex. **THE RULE:** a value that lives in two files is asserted equal or it
is two values. §TRADE EXPANSION now names the `:root` block.

### 2026-09-01 (C3681) — THE ENGINE READ REMINDERS AS STRINGS, A TRADE WROTE THEM AS PAIRS, AND THE PASTED BLOCK SAID "[object Object]" FOR FIVE DAYS
`shared/docspec.js` emitted `PROTOCOL REMINDERS` with `"- " + r`. Fourteen libraries write
reminders as strings. `doors/docs.js` wrote them as `{ when: "label", say: "…" }` — the
better shape, the trigger word as data — and every one of doors' five reminders reached the
block a man pastes into his AI as `- [object Object]`. The block was non-empty, carried all
eleven headings, and passed `docspec-config`; the layout was watertight around it; no gate
read a reminder line. Found by the C3681 docs writer copying the doors shape for landscape,
who reported it instead of matching it silently. **FIX:** `reminderLine()` renders both
forms ("When <trigger> comes up: <say>"), the string form byte-identical to before; and
`docspec-config` fails any block carrying `[object Object]`. **THE CLASS:** a gate that asserts
presence and length is satisfied by a stringified object — assert the one string that can
only come from a bug.

### 2026-09-01 (C3681) — TWO PHRASES THE GETTING-IN GATE READS BY REGEX WERE PARAPHRASED AT STAND-UP, AND THE PAGE FAILED ON BOTH
`getting-in.mjs` asserts the closing asks him to state "the window you're actually giving
us" (regex), and that at least ONE heads-up option classifies as a PERMITTED activity (hot
work · fire alarm · sprinkler · power down · torch · valve · closure · …) so the handback
rule runs at all — the comment on that check names flooring and sitework as the two trades
that looked clean for weeks while it ran zero assertions. Landscape's copy said "the hours
you're actually giving us" and named the water shutdown without the word VALVE; both failed.
Neither is a defect in the page — they are a CONTRACT between a config's prose and a gate's
vocabulary, and a paraphrase at stand-up breaks it silently. **FIX:** "the window you're
actually giving us" verbatim; "the water will be off at the backflow valve while we work".
**THE RULE FOR THE NEXT STAND-UP:** copy the sibling's sentence where a gate names one, then
localize AROUND it. The gate's failure message quotes the phrase; read it before rewriting.

### 2026-08-29 (C3679) — THE CHROME WAS ASSEMBLED BEFORE THE PRODUCT, SO A BUG IN A LABEL FROZE THE DOCUMENT
`shared/checklist-request.js` built the bottom-bar count line and THEN the document:
`countEl.textContent = cfg.countLabel(n)` ran a line above `preview.textContent = text()`.
Both are caller code, and the eleventh instance of the shape passes a `countLabel` that
counts a SUBSET of the ticked rows — which threw on the engine's own first render (the
label ran through an `api` that mount() had not returned yet). The exception aborted
`refresh()` one line before the preview was written, so the page sat there saying
**"(nothing on it yet)"** with the list filling up behind it, and the only symptom was a
document that never changed. That is precisely what
`tools/toolkit-gates/order-live-header.mjs` exists to catch — *"the block he PROOFREADS is
a generation stale"* — reached through a LABEL instead of through a header field, which is
a door that gate does not watch. **The document is the product and the count is chrome, so
the product is written first**; a caller bug in the chrome can no longer freeze the
product. One line moved, thirteen sibling pages inherit it, and the page-side fix is the
other half: read the ticked rows off the DOM rather than through an API that does not
exist until after the first render.

### 2026-08-29 (C3679) — THE GATE BLAMED THE BAR FOR A PANEL'S OWN CLIP EDGE, AND I NEARLY "FIXED" THE PAGE
`tools/toolkit-gates/mobile-watertight.mjs` failed the new page at all four widths:
*"UNREACHABLE, the fixed bar covers it"* on two trade chips in the Tools menu. Three things
were true and only the third mattered. **(1) It was not a new defect.** That gate samples
ONE tool page per trade and picks it ALPHABETICALLY (`files.find(f => f !== 'index.html')`
over a sorted list), so a page beginning with **b** became the first `creative/` page ever
measured with the menu open — `creative/getting-in.html` has carried the identical two rows
since 2026-08-13. **A sample keyed on a filename re-draws itself every time a file is
added, and the page that inherits the seat inherits the blame.** **(2) The fix I wrote
first was a regression.** I bounded the dropdown's height by the fixed action bar — and
then measured the stacking rather than assuming it: the nav is `z-index:40`, the bar is
`30`, so **the panel already paints OVER the bar** and a probe inside the restored panel
returns the panel's own grid, not the bar. The "fix" only shrank the menu by 64px and
clipped MORE of it. Reverted to a zero-line diff. **(3) The real defect was in the gate.**
Its coverage check probes an element's CENTRE with `elementFromPoint`, and at a scrolling
panel's bottom edge a 44px row is painted for 21px with its centre one pixel past the clip
— so the honest answer to *what is at that pixel* is whatever is behind the panel, and the
verdict *"the bar covers it"* is a wrong reading of a true measurement. Driven to prove it:
the row reports 749–793 against a panel box ending at 706, is not the element painted at
its own centre, and after one `scrollIntoView` sits at 406–450 and hit-tests as itself. The
check now skips a control only when THE PROBE POINT falls outside an ancestor that
genuinely scrolls, and **the skip is red-verified rather than argued**: a control planted
under the bar with no scrolling ancestor still fails at all four widths, in both states.
**The general form: a gate that measures a POINT can be right about the pixel and wrong
about the cause. Before changing the page, check whether the instrument is asking the
question its verdict claims to answer** — and note that `menu-reachability.mjs` already
owns that question properly and was green throughout (tightest clearance 15.5px).

### 2026-08-28 (C3677) — A GATE THAT FINDS ITS PAGES BY SHAPE IS BLIND TO THE PAGE MISSING THE SHAPE
The sibling of the scar below it, one layer down and harder to see, because there is no
roster to audit. `tools/toolkit-gates/order-live-header.mjs` — the gate named THE PREVIEW
IS THE DOCUMENT — finds shape #1 pages by probing for `#list` + `#preview` + `#copy` +
`#clear`, and its header is proud of it: *"No per-page field list, no roster to update. A
trade shipped next month is covered the day it lands."* It is also the reason the gate
could never see `av/consumables.html`, **the only order page on the rack with no preview at
all** — the one page whose defect was the exact thing being probed for. For its whole life
the gate printed `OK — 12 order page(s)` and there were thirteen. **Its green was never a
pass on that page; it was a smaller number, and nobody reads a number for what is missing
from it.** Proved by control: deleting the new `#preview` drops the gate straight back to
twelve and it still exits 0. **A discovery predicate that requires the feature under test
cannot fail the page that lacks it.** The general form: when a gate finds its own subjects,
the count it prints is an assertion too — print the denominator you expect, or find the
subjects by something the defect cannot delete (here: a `#list` + `#copy` page IS an order
page, whether or not it has a preview).

### 2026-08-28 (C3677) — AN ASSERTION THAT WAS NEVER RUN AS A CONTROL IS A GUESS DRESSED AS A GATE
The new "what Clear spares must survive a reload" half of `order-live-header.mjs` was
written specifically to catch the cheap fix for `av/cable-list.html` — leave its job and its
name in the LIST record and just stop wiping them in `onClear`. That mutation was applied on
purpose and **the assertion went green.** `shared/draft.js` `clear` drops the record and the
page's own refresh re-saves it a quarter-second later off the very fields Clear was meant to
forget, so the values do come back. The reasoning was clean, the sentence in the comment was
persuasive, and it was wrong — and **only running it against the thing it was supposed to
catch found that out.** The real invariant was then MEASURED rather than argued: across all
twelve other pages, everything spared by Clear lives in `toolkit.<trade>.jobcard.v1`, a
`…dropoff.v1`, or the page's own `…header.v1` — **never in the list record**. That became
clause 2, which fails the same mutation with 2 defects. **Write the control before the
comment. A gate whose negative control has never been run has an unknown false-negative
rate, and the comment above it is the most convincing thing in the file.**

### 2026-08-28 (C3677) — shared/jobcard.js IS KEYED PER TRADE AND `adopt()` RUNS ONCE PER STORE, NOT ONCE PER PAGE
Found by the judge panel, NOT fixed — recorded so the next mount does not walk into it.
`KEY = 'toolkit.' + cfg.trade + '.jobcard.v1'`, and all eleven live mounts are eleven
distinct trades, so one trade has always meant one carded page. `adopt()` runs only when
`read()` returns nothing (jobcard.js:411) — **once, on whichever page of that trade is
opened first.** The day any trade gets a SECOND carded page, the two mounts share one store
and only one `legacyKey` is ever honoured: whichever page he opens first wins, and the other
page's saved answers are dropped in silence, against the module's own written promise
*"NOTHING IS LOST ON THE WAY IN."* Worse in the direction that ships damage: if the page
that wins is the one holding a stale value, that stale value is promoted to job #1 and
painted onto the sibling page too. The fix when it is needed is per-legacy-key adoption
("has THIS key been adopted"), not "is the store empty" — and it is a change to a module
eleven pages depend on, so it does not ride along with a mount. Two smaller traps in the
same area, also from the panel: `legacyKey` is a SINGLE slot while a page can have several
legacy keys (`av/cable-list.html` has three), and `adopt()` reads only a flat id-bag or
draft.js's `{v,s}` — it **cannot** read `shared/checklist-request.js`'s list record, whose
header lives under `.extra` with renamed short keys, so a `legacyKey` pointed at a
`persistKey` compiles, runs, adopts nothing, and reports nothing.

### 2026-08-28 (C3677) — A FIELD NOBODY BOUND, BECAUSE THERE WAS NOTHING ON THE GLASS TO REPAINT
`av/consumables.html` bound no listener to `.qty` or `.note` — not a regression, a page that
never needed one: the only readout was a count in the dock, and a count moves when a line
goes on or off, never when a number inside it changes. **Putting the document on the glass
created a defect that the same change also exposed**, and it exposed it in the worst
possible place — the LAST thing he edits before Copy. Driven at 390px the block read
`Wall Dogs x1` while the copy button sent `Wall Dogs x8`. The general form is worth keeping:
**adding a live view to a page retroactively promotes every unbound input into a bug**, and
the ones that bite are the ones edited last. New gate `row-live-line.mjs` covers the row half
`order-live-header.mjs` skips by design; the other twelve pages were swept in the same cycle
and are green, because the engine already re-renders on its own row controls.


### 2026-08-28 (C3676) — A HARDCODED TRADE ROSTER DOES NOT FAIL WHEN A TRADE LANDS, IT GOES BLIND
`tools/toolkit-gates/docspec-say.mjs` shipped with its roster typed out, at fourteen.
`doors` landed as the fifteenth trade with a full write-up library, and this gate — the one
whose entire job is reading the say-list on **every document of every trade** — never once
ran on it. It kept printing a green summary with a number in it, and the number was the
number of trades it had been told about, not the number on disk. Every sibling gate in the
directory (`docspec-desk`, `docs-pool`, `find-noise`, `build-docsindex`) already derives
from `readdirSync`; this was the one that did not. **A gate with a typed roster reports on
what it was told, and its green is indistinguishable from coverage.** Fixed by derivation;
the count moved 14 → 15, documents 214 → 231, checks 2,978 → 3,213, still 0 failing —
doors was clean, which is exactly why nothing would ever have surfaced it.

### 2026-08-28 (C3676) — THE FIRST DRAFT OF AN ASSERTION COMPARED VALUES WHERE THE DEFECT IS STRUCTURAL
The new artefact gate asserts that a trade overriding a SHARED `omit` must not inherit the
shared demand. First draft tested it by VALUE — *the omit moved and the needs did not* —
and its first run went red on **fourteen documents that are all correct**: `creative`'s
damage-found says *"THE DATE, THE TIME, AND WHERE THE PHOTOS ARE"* where the shared line
says *"the timestamp and where the photos live"*, which is the same two artefacts in that
trade's own words. **Two differently-worded lines demanding the same thing is the library
working, not a leak.** The leak is that an override rewrites `omit` and never declares
`needs` **as a key**, so `library()`'s key-by-key merge silently hands it a demand authored
for the sentence it replaced — and every word on the page is well-formed. The test moved
onto `Object.hasOwnProperty` against the raw `TRADE_DOCS.overrides` map, under the merge,
and stays red for the mirror defect (a `needs` declared for an `omit` the override does not
own). Deleting creative's one line proves it. The rule: **when a wrong value and a right
value are indistinguishable, the assertion belongs on the KEY, not the value.**

### 2026-08-28 (C3676) — A GATE COMPARING TWO READERS PASSES A STEM THAT IS WRONG ON BOTH
The artefact demand renders in two places from one source, and the gate asserts the card's
DOM carries the same string the block does. Green. The card read: **"Say the actual a date
or a clock time, a name and what you left changed."** The demands are authored as noun
phrases WITH their articles, because the block's sentence — *"it has to carry a date or a
clock time"* — needs them; the card's stem prepended a second article and shipped broken
English on the one line the whole library is built around, on every trade. **An
agreement assertion cannot see an error the two sides share.** Caught by looking at the
rendered frame at 390px, not by any check. The stem is now the block's own verb ("It has to
carry"), so the two readers are told the same thing in the same words and the articles land
once.

### 2026-08-28 (C3675) — A GATE THAT SAID "EVERY PERMIT HANDS BACK" WHILE ASSERTING NOTHING ON TWO TRADES

`tools/toolkit-gates/getting-in.mjs` enforces the HANDBACK RULE — any option naming a
permitted activity must end in a question aimed at the man who owns the process — and it
had been printing **"15 page(s) clean: every permit hands back"** while running **zero**
handback assertions on flooring and sitework.

The rule only fires on an option the `PERMITTED` regex classifies, and it classified none
of theirs. Both trades write their permit lines in words the list never named: *"We need
something **powered down**, moved or disconnected"* — the `\b` after `power` does not match
`powered` — *"**regulated material** rides on its own paper"*, and *"who owns the closure
and **the permit** for it"*. Both trades hand back correctly; the authors wrote them well.
That is exactly what made it invisible: **the gate was never wrong, it was silent**, and a
silent zero reads identically to a clean pass.

It surfaced only because a NEW gate needed the same classification and reported those two
trades as *untestable* rather than clean. **The fix is not the wider regex** (though it is
wider now, and `permit`, `impairment`, `regulated material`, `panel on test`, `valve` and
`closure` are in it). The fix is that the gate now PRINTS what it actually asserted, per
trade — `av:5 · concrete:4 · creative:1 · … · flooring:1 · sitework:1` — and **fails on a
zero**. A gate that finds nothing to check must say so out loud. This is the second time
this program has been bitten by a gate quietly running none of its real checks; the first
was `reconcile-join.mjs` failing on its own wrapper (C3654).

**And the same trap caught the new gate on its first run**, which is why it is one scar and
not two: `what-came-back.mjs` shipped with its own hardcoded THIRD copy of the rule it was
checking, so it reported flooring and sitework untestable while the module classified them
correctly. It now parses the test out of `shared/whatcameback.js` at run time. **A gate must
never carry its own copy of the rule it is asserting.**

### 2026-08-28 (C3675) — THE MOBILE SHIP GATE STOPPED THREE TRADES SHORT, AND THE OUTPUT LOOKED COMPLETE

`mobile-watertight.mjs` is the gate the ship loop names as THE mobile ship gate. It opens a
fresh browser context per page per width — around 600 across the toolkit — and somewhere
past the thirteenth trade the browser went down under them. The run then died on
`page.waitForTimeout: Target page, context or browser has been closed`, **three trades short
of the end**: plumbing, roofing and sitework were never measured.

It never reported a false pass — it crashed with a non-zero exit — but a wall of `PASS`
lines ending without a summary is not something a person reads as *"the last three trades
were not checked."* It was reproducible before and after this cycle's changes, at the same
position, which is how it was identified as pre-existing rather than caused.

Two small fixes: the context now closes in a `finally` so a throw cannot leak it, and a
dead browser is relaunched and the page retried instead of ending the sweep. **A gate that
stops early is worse than a gate that fails, because a fail gets read.**

**VERIFIED, and the attribution is narrower than the fix.** The sweep now runs to the end:
**152 pages at 320/360/390/430px in both text sizes, 0 failing**, including the 30 pages
across plumbing, roofing and sitework it had never reached. It needed **zero relaunches**
to do it — so on the evidence of one clean run the decisive change is the guaranteed
context close, not the relaunch guard. The guard stays because it costs nothing and turns
the remaining failure mode from a dead sweep into a named line, but it is not what fixed
this and the book should not pretend it was.

### 2026-08-26 (C3673) — THE SAME MISTAKE, TWICE, IN ONE PAGE: masonry's MIGRATION WIRING ON A PAGE WITH NOTHING TO MIGRATE

The scar below says a mechanism ported without its reason is ported wrong. Here is
the *second* instance of it in the same file, and this one a GATE caught rather
than a person. `flooring/dealer-call.html` shipped its first hour carrying
masonry's job-card wiring verbatim: a **`legacyKey`** naming
`toolkit.flooring.dealerCall.header.v1` — **a store that has never existed**,
because this page was born today with the card and the drop-off block already in
it — and a list of fields to **carry** across from old header boxes that were
never on it.

`tools/toolkit-gates/dropoff-block.mjs` reads the page's SOURCE for a carry
declaration and treats it as a claim: *old boxes moved into the block.* It then
seeds the pre-block storage shape and drives the migration. There was no
migration to drive, so the block held no state, so its clear button stayed hidden,
so the gate timed out on a click. **The failure message was about a button and the
defect was about a claim.** `painting/store-call.html` — the sibling that was
also born with a card — had already written the correct form and the reason:
`legacyKey: null`, *"NOTHING TO ADOPT… declared rather than omitted, because
jobcard-scope.mjs fails a page that is SILENT about its predecessor."*

**AND THE COMMENT EXPLAINING THE FIX RE-TRIPPED THE GATE.** Writing
`` `carry: ["fPick"]` `` into the apology comment put the exact string
`carry: [` back in the source the gate greps. **A gate that reads source text
cannot tell a confession from a declaration** — the sentence was rephrased. Worth
knowing before the next page documents what it removed.

### 2026-08-26 (C3673) — A NEW JOB INHERITED THE LAST JOB'S ANSWER ON NINE PAGES, AND THE FIRST TEST OF IT ACCUSED THE WRONG COMPONENT

**THE BUG.** `shared/jobcard.js`'s `setVal()` guarded a `<select>` against a
stored value its option list no longer has — a good guard, with its reason in the
comment. But it **could not tell "no answer" from "an answer this list cannot
hold", and bailed on both.** A new job's `f` is `{}`, so every per-job select was
handed `undefined`, hit the guard, and **kept the previous job's selection on
screen** — where it then rode into the sent document as the new job's own answer.
Measured A/B on the real page: without the fix a fresh job reads *"On this order —
off this run"* and *"Shop stock"*; with it, *"— nothing said —"* and *"Job"*. The
engine's own line 66 states the invariant that was being broken: **"A NEW JOB
STARTS EMPTY. That is the safety property."**

**BACKPORT — 9 of the 10 job-card pages carry the class**, `fCharge` on concrete ·
electrical · framing · low-voltage · masonry · painting · roofing · sitework, plus
`fAttic` here. An empty value now resets to the option the markup marks selected
(option zero only if none is named); the unholdable-value case still bails, which
is what the original guard was for.

**AND THE TEST WAS WRONG BEFORE THE CODE WAS RIGHT.** Driven with a Playwright
`.click()`, "+ Another job" appeared to do **nothing** — no second job, no chip —
on this page AND on painting, which reads exactly like a live engine defect on
every card in the program, and was written up as one. It is not. The card's
`collect()` calls `paint()`, which replaces `host.innerHTML`; a locator resolved a
moment earlier is clicking a **detached node** and the handler never runs.
Dispatching the click from inside the page creates the job correctly every time.
**A test that drives a self-re-rendering control through a stale handle
manufactures a product bug out of its own race** — and the near-miss here was
reporting it, which would have sent a future cycle hunting a defect that is not
there.

### 2026-08-26 (C3673) — A MECHANISM STOLEN WITHOUT ITS REASON IS STOLEN WRONG, AND IT TOOK A FIELD HAND TO SAY SO

The private record's instruction for `flooring/dealer-call.html` was verbatim:
"steal masonry's RUN mechanism and sitework's buried-second-reading rather than
re-deriving them." Both were stolen. **One of them was stolen wrong, and it was
the half I was most confident about.**

**WHAT WAS STOLEN RIGHT.** masonry made the run a **TICK** (`matchRun()`), and
copying that would have been the ceremony §THE GATE forbids: a mason genuinely
has back-up wythe that matches nothing, so his tick carries information; a floor
hand has no line that comes off no run, so the same tick is forty taps that say
what picking the line already said. `run` moved onto the ITEM, sitework's rule.
That call was correct and the page is better for it.

**WHAT WAS STOLEN WRONG.** The same confidence carried masonry's *sentence*
across with the mechanism — "a plank carton, a stair nose, a T-mold and a coil of
base in one area all come off one run" — and it went into the page header, into
`items.js`, and into the block the whole page exists for. **A 20-year flooring
lens killed the fourth item in that list in one line:** on a commercial job the
base is Roppe or Burke or Johnsonite, picked to *coordinate by colour*, and on a
carpet or tile job it is **guaranteed** to be another maker because the mills do
not make base at all. Printing a coil of base under `Run / dye lot / batch:
4471-B` sends a counter hunting for a plank lot number in the base catalogue.

**63 GREEN ASSERTIONS AT THE ARTIFACT DID NOT SEE IT**, and could not have: every
one of them asserted that the block gathered what the data said to gather. The
data was wrong, so the gate was green on a wrong answer. **A gate proves the code
matches the data; only somebody who has stood at the counter can say the data
matches the world.**

**THE FIX IS THE FINDING.** The run is not one run — it is one run PER PRODUCT
FAMILY. `run: "field"` (26 lines: the goods and the mouldings the same mill wraps
to go with them) and `run: "base"` (5 lines: base, corners, cove cap, saddles,
vents — which have a real matching problem and it is a *different* one, every coil
matching every other coil off a lot he usually does not hold). Two blocks, two
sentences, one field. **The page is now right about something a supply-house form
has never been right about**, and it got there by being wrong in public first.

**THE RULE, for the next mechanism anybody lifts off a sibling trade:** port the
MECHANISM and re-derive the CLAIM. The mechanism is code and it travels; the
claim is about a trade and it does not.

### 2026-08-26 (C3673) — THE RULE WAS IN THE FILE'S OWN HEADER AND THE FILE BROKE IT SIX TIMES

`flooring/items.js` states, three paragraphs above the data: the `unit` key is
"left OFF every line whose unit genuinely varies… because a page that prints the
wrong unit of issue orders the wrong truck." **Six lines then carried one anyway**
— `Wedges / shims` said *"BY THE BAG OR THE BUNDLE"* and carried `unit: "bag"`, so
a bare 10 printed **"10 bag"** on a line whose own words say bundle is just as
likely; the same on `Rags`, `Filler / putty`, `Seam sealer`, `Grout sealer` and
`Primer`. Twelve lines in the file use the "X OR Y" phrasing and **six got it
right and six got it wrong**, which is the signature of a rule that lives only in
prose. A safety lens found them by reading the header and then reading the data.

**A PROSE RULE IS A COIN FLIP AT SCALE.** The rule is now mechanical and asserted
in the page's own drive: *if the first clause of a line's `sub` names two
containers with an OR, that line carries NO unit.* Eight more lines were flattening
a real container word to a generic `ea` (`BY THE CAN` → "2 ea", `PER PAIR` → "2 ea"
— a dealer reading "2 ea" on knee pads ships one pair short) and now print `can`,
`kit`, `pair`, `tube`, `unit`, `sheet`. **All 13 units in the data are driven at
the artifact**, because masonry once shipped a line saying "BY THE SET" that its
own table could not attach "set" to a number.

### 2026-08-26 (C3673) — A REGEX ON AN ITEM NAME IS A CLASSIFIER NOBODY MAINTAINS

The page's on-glass hints classified lines with `/tape/`, `/tile/` and `/grout/`
against the item NAME. **Both of the interesting ones were already wrong against
the very file they ran on**, on the day they were written:

* `/tape/` also matched **"Masking / painter's tape"** and **"Duct tape"** in
  SUNDRIES, so a man with forty cartons of plank, a roll of masking tape and **no
  adhesive** was told nothing. The check died silently in the exact case it exists
  for — a false NEGATIVE, the kind nobody ever reports.
* `/tile/` also matched **"Carpet tile"**, which nobody has ever grouted, so a
  carpet order got asked *"Tile and no grout — on purpose?"*. That is the
  FIELD-COOL bar failing out loud: a page that does not know the trade.

Both were found by grepping the regexes over the data rather than by reading them,
and the fix is the page's own doctrine applied to itself: `holds`, `grouted` and
`grout` are keys on the ITEM now, for the same reason `run` is. **The refinement
that matters is in `holds`:** seam tape and seam sealer are NOT on it (a seam is a
joint, not a bond) and tackless IS (a stretch-in carpet needs no adhesive and must
not be nagged for one) — a distinction a regex on the word "tape" can never hold.

### 2026-08-26 (C3673) — THE ENGINE MARKS A CLONE THE SAME WAY IT MARKS A WRITE-IN

`shared/checklist-request.js:312` clones a row with `itemHTML(def, cfg, true)` —
`removable: true` — so **a cloned CATALOGUE row gets the same `.rm` button a
write-in has**, and every sibling order page detects write-ins with
`l.el.querySelector(".rm")`. On those pages it costs nothing: their run flag is a
tick the clone copies. On a page whose second reading is read off the DATA, a
cloned row read as a write-in falls back to a `flags.run` catalogue items do not
have — so **"+ another length" on a stair nose, the most natural thing anyone
would ever add to this page, would silently drop that line out of the one block
the page exists for.**

This page ships no clone button, so the defect was **latent** — precisely §SCARS
2026-08-25's class, *a fix that activates a latent defect*, seen from the other
end: **a defect planted for a later, reasonable change to activate.** Keyed on
catalogue membership (`!CAT[l.name]`) instead, a clone is a catalogue row forever,
and the one edge it introduces resolves the way it should — he typed "Stair nose",
it IS a stair nose, it joins the run. **Verified by injecting the engine's own
clone button and driving it**, since the page has none to click.

### 2026-08-26 (C3661) — FOUR, AND THREE OF THEM ARE THE SAME SHAPE: THE GATE I WROTE COULD NOT SEE THE CLASS I BROKE

1. **A GATE THAT PRINTS A COUNT IS MAKING A CLAIM ABOUT COVERAGE.** `find-noise.mjs` printed
   *"29 surfaces"* and ran **26**. Its commons adapter read `window.__FH_ROWS`, a global that
   exists nowhere in this repository — `find-honesty.mjs` sets it for itself — so `names` came
   back `[]`, the probe loop never entered, and three surfaces contributed **zero checks while
   printing no skip line and no error.** Green on 208 checks. The fix is not the adapter, it is
   class **N0**: a surface that ran no probe is a RED. Any gate that iterates a list must assert
   it *reached* every item, because "no failures" and "no checks" render identically.

2. **I ECHOED THE USER'S OWN WORD INTO THE LAYOUT AND HANDED HIM THE HORIZONTAL SCROLLBAR.**
   The sentence quotes what he typed, so *he* chooses how long its longest word is. A
   54-character token pushed `hvac/truck-stock` **257px sideways at 320px**. Anything that
   prints a raw query needs `overflow-wrap:anywhere`, and the sweep for the class found it
   **already live** in the `Closest to “…”` heading on all 14 write-up pages — a defect that had
   shipped and was invisible because nobody had measured that page with a long word in the box.
   Measuring a NEW thing found an OLD one; that is the argument for measuring at the artifact.

3. **"HANDING BACK A SLICE OF WHAT HE TYPED" IS ONLY TRUE IF THE SLICE IS A WORD.** The recovery
   step was written to show him his own capitalisation and it did — but `norm()` shreds an
   accented word at the accent, so *café* became the token `caf`, and the page then said
   `Ignored “caf”`, presenting a fragment **as if it had been deliberately recovered**. That is
   worse than the mangled token alone, because it wears the authority of the fix. Found by the
   lens that went and read `items.js` and noticed two trades ship Spanish vocabulary on purpose.
   **A feature whose whole claim is honesty fails hardest when it is confidently half-right.**

4. **THE FIX FOR THE FLICKER DEPENDED ON A SIGNAL EVERY CALLER WAS ALREADY DESTROYING.** Holding
   back the word under his cursor needs to know when he finished it, and the only evidence is a
   trailing separator — which `shared/docspec.js` and `shared/pickfilter.js` both `.trim()` away
   before the engine ever sees the query. The rule was correct, tested green in a Node harness,
   and was a **no-op on all 26 real pages**; the gate only caught it because N9 asserts the word
   IS named after the separator, not merely that it is silent before. **An exemption gate that
   only tests the silent half passes on a feature that is silent always.**

### 2026-08-26 (C3660) — THE PANEL SAW THE THING I HAD ALREADY DECIDED NOT TO CHASE
MINERALIA-016 wished *"Needs to look real"* on the engine page. Five failures, and
four of them are one class: **I trusted my own eye at the exact points where I had
made a judgement call, and every one of those calls was wrong.**

  1. **I LOOKED AT THE WORST ARTIFACT IN THE FRAME AND MOVED ON.** Reading the first
     contact sheet I noted a large grey grain in MARBLE 48213 — *"reads as a 3D ball,
     could be a large calcite grain, not obviously wrong, let me not chase it"* — and
     went to work on the boundaries instead. THREE blind readers, independently, named
     that grain the single most damning thing in the whole set: a lit sphere with a
     specular highlight, which transmitted light cannot produce. Worse, it was a
     REGRESSION I had just caused — killing the ring motif removed the texture that had
     been masking the smooth radial gradient underneath. **The moment you notice
     something and decide it is not worth chasing is the exact moment the panel is for.
     Cast it on the AFTER, not only on the BEFORE.**
  2. **A FIX THAT MEASURES ZERO IS NOT A FIX, HOWEVER RIGHT ITS PHYSICS.** The shared
     medium warp — one band-limited field displacing the coordinates both growth fronts
     are measured in, so a boundary between two crystals that nucleated at different
     instants wanders — is physically correct and I could *see* it working. Three
     metrics said it changed nothing, and a blind forensics reader said boundaries were
     still *"exactly straight line segments meeting at sharp vertices"*. It was shipped
     at 2.0px of throw on a ~35px grain. Raised to 4.6px (|dW/dr| 0.88, under the fold
     bound of 1) and the complaint class disappeared. **"I can see it in the render" is
     not a measurement, and a correct mechanism tuned to zero amplitude is decoration.**
  3. **THREE METRICS, BUILT AND CUT, ALL MEASURING THE WRONG THING.** Isoperimetric
     `P/(2*sqrt(pi*A))` tracked grain ELONGATION — basalt's plagioclase laths scored
     HIGHEST and the sutured quartzite scored near the bottom, the exact inverse of the
     prediction. RMS deviation from a whole-contact line fit was dominated by the kinks
     where the active Wulff face changes, which both versions have identically. Local
     facet spread had a noise floor of **0.20 on segments that are exactly straight**,
     swamping a ~20° signal. Only MOTIF LOAD survived, because it counts the named
     defect directly. **Read the metric against a NEGATIVE CONTROL — input you already
     know is straight — before you trust any delta it reports.**
  4. **`|0` IS NOT `Math.floor`.** Truncation is toward zero, so `p|0` folds `-1..1`
     into index 0. The twin-lamella index used it, so **every twinned grain in every
     plate ever rendered carried a double-width lamella straight down its middle** — a
     defect nobody reported because it reads as "a pattern", which is precisely what
     made the hatch look like wallpaper. Found only by rewriting the line for another
     reason. BACKPORT swept: the class does not exist in the field toolkit (zero `|0`
     sites — those pages are document tools, not numeric graphics), and a scan of the
     sibling card engines for `|0` feeding a parity or index test with a possibly-negative
     input returned only minified vendor bundles.
  5. **`git add <path>` DOES NOT MAKE THE COMMIT ABOUT `<path>`.** persona500's index
     already held **100 files staged by another lane**, so adding one file by pathspec
     produced a 101-file staged set, and the commit message would have claimed all of it.
     The pre-commit hook (the entire site verification suite) ran long and timed out,
     which is the only reason it did not land. Backed out with `git restore --staged`,
     index returned to exactly the 100 it held before. **In a shared tree, read
     `git diff --cached --name-only | wc -l` BEFORE `git commit`, not after — and
     committing in a lane that is not yours was the overstep underneath it.**


### 2026-08-25 (C3659) — THE NUMBER WAS TRUE AND THE SENTENCE UNDER IT WAS NOT
Three separate ways this cycle nearly shipped a false statement on the back of a real
measurement. They are one class: **an aggregate licenses an aggregate claim and nothing
smaller**, and every one of them was caught by a different instrument than the one that
produced the number.

  1. **THE EXAMPLE IN THE HEADER WAS A CASE THE CYCLE DID NOT FIX.** `shared/find.js`
     was written with *"AHJ nuisance letter came back as the Damage / Pre-Existing
     Condition Note, presented as an exact match"* as the illustrating defect. The
     measurement said 3,838 unhedged wrong answers and the fix took them to 2,006, so
     the sentence read as obviously covered. It is not: that query is in the **residual**
     — its extra words are dropped by rule 1 as noise, and the one live word genuinely
     names a document — so the shipped file would have pointed at its own defect and
     called it fixed. Found by SCREENSHOTTING the real page at 390px to see the new
     heading, and there was no heading. The replacement (*"gas shut off notice" → Room
     Sign-Off (Commissioning Write-Up)* on the AV page) was pulled from the flipped set,
     not from memory. **A worked example is a claim about ONE query and has to be
     re-driven, even when the aggregate it illustrates is real.**
  2. **A DATA-DERIVED GATE'S FIRST RED INDICTS THE PROBE, NOT THE CODE.**
     `find-honesty.mjs` builds every probe out of the surface's own strings, which is what
     makes it survive a row added next month — and its first run produced 19 failures of
     which **16 were the probe being wrong**: `"meeting"` is an alias of the minutes AND a
     word in the Toolbox Talk's title, so it names two rows and is evidence about the
     label only; `"clmp meter"` deletes a character from a five-letter word, which leaves
     four, which gets no fuzzy budget, so the token is dropped and the engine is being
     asked a different question than the one written down; `"london philadelphia"` are
     brick-trowel patterns in `commons/names.js`, and every commons surface searches
     THROUGH that table, so they are names and not prose. Had the engine been "fixed"
     to make those green it would have been bent to satisfy a bad question.
     **The tell is that the failures cluster on the probe generator's assumptions, not on
     the classes the defect predicts.** The three that were real all sat in C/D/E, which
     is exactly where the negative control said they would be.
  3. **THE THEORY THAT READS BEST CAN MEASURE AT ZERO, AND IT ALMOST SHIPPED.** The
     obvious companion to the fix was to let strength decide WHAT IS SHOWN as well as what
     it is called — tier by strong coverage first, so a document whose prose sweeps up
     three of his words cannot hide the one actually named after two of them. It was
     written, commented and working. Ablated: **4,160 right answers with it and 4,160
     without**, and it made **56 more wrong answers confident** by narrowing the tier
     around a strong-but-wrong lead. It is not in the shipped file. The same run killed a
     second assumption: making a prefix weak EVERYWHERE scores better on complete queries
     (1,907 vs 2,006) and turns **half of every keystroke into a "Closest to"** — 113 of
     214 four-character queries hedged, against 214 of 214 clean with the last-token
     exemption. **Neither of those was decidable by reading the code, and both were
     decided in one run each.**
  4. **THE NEGATIVE-CONTROL DANCE EATS ANY EDIT YOU MAKE WHILE IT IS RUNNING, and it ate
     the fix for scar 1.** Proving a gate red means `cp fix backup && cp old engine && run
     && cp backup engine` — and that last copy is a **time machine to whenever the backup
     was taken**. The corrected worked example was written into the header AFTER the backup
     and BEFORE a later ablation, so a routine restore silently put the false sentence back.
     Caught by grepping the file for the string that was supposed to be in it, which is the
     only reason it is not in this commit. **The rule: a restore-from-backup is a WRITE, so
     re-verify the file after every one, and re-take the backup the moment the working file
     changes.** Cheaper still — and what should have happened — swap the engine with `git
     stash`/`git checkout` so the "backup" is the working tree itself and cannot go stale.
  5. **AN HONEST LABEL OVER THE WRONG ROW IS THE SAME FAILURE IN A BETTER SUIT, AND THE
     GATE COULD NOT SEE IT.** The first draft of the fix gave "he typed a whole ALIAS" the
     same rule-4 bonus as "he typed the whole TITLE" — 1.6 — which put a nickname ABOVE a
     title that says the word. On the AV page `damage` started answering with the **Incident
     / Near-Miss Report** while the Damage / Pre-Existing Condition Note sat underneath it,
     **labelled exact**, which is the precise failure the cycle was opened to kill. Nine
     documents lost their own word; on the commons, `snake` — the word `commons.js` names as
     the entire thesis of its hand-off — flipped off the Audio snake. **5,093 gate checks were
     green over it, and so was a 10,738-query sweep**, because both measure whether the LABEL
     is entitled and the corpus's own notion of "right" was already alias-shaped. Every probe
     class A-F types a WHOLE STRING; a bonus inversion only shows when a SINGLE WORD is
     claimed by a title on one row and a nickname on another. Found by an adversarial read
     that was asked to break the diff rather than confirm it, and the second defect it found
     was underneath the first: the title rung tested a RAW SUBSTRING, so `co` matched inside
     "condition" and the Damage Note outranked the Change Write-Up whose nickname is literally
     CO. **The fix is not a tuned constant** — the first attempt was, and the window between
     the two failures was 1.3 to 1.5 wide, which is a fragility, not a fix. The title test now
     matches at WORD BOUNDARIES, which is what a phrase bonus always meant, and the ladder is
     ordered whole-title > the title says it > a nickname says it > spaces-out. **New probe
     class G, 1,000+ checks: a word in THIS item's title and in no other item's title leads
     THIS item, whatever else answers to it — verified red on that exact draft before it was
     trusted.** The same read also found a `ReferenceError` waiting in `shared/pickfilter.js`
     (`on.length`, `on` declared nowhere) that no page has triggered only because no page
     passes `onChange` yet; fixed in the same commit. **The lesson is about the SHAPE of a
     gate, not about a constant: a suite whose every probe is a whole authored string cannot
     see a ranking rule, and "measured, gated and green" was true of all of it.**


### 2026-08-25 (C3658) — DATA WITH ONLY A MACHINE FOR A READER ROTS, AND NOTHING LOOKS AT IT
`facts` is authored on every document in the library — 214 documents, 661 distinct
strings — and for the whole life of this engine it reached exactly ONE reader: the
model, inside VALIDATION, inside a 9,500-character block a man pastes into a Gem once
and never opens again. No human being had cause to look at it after the day it was
typed. Three separate defects were sitting in it, live, and the class is the same in
all three: **a field nobody reads is a field nobody proofreads.**

  1. **FIVE FRAMING DOCUMENTS AUTHOR NO `facts` AT ALL.** The block shipped
     `Before you write, check the input for: .` — an empty check, on the one
     instruction that decides whether his report comes back full of holes.
  2. **A FACT MAY BE A SENTENCE, AND `.join(", ")` CANNOT CARRY ONE.** It held
     while every author wrote short noun phrases and turned to mush the first time
     one did not: `hvac/compressor-failure-report` emitted a 600-character run-on
     where *"…amps at failure. Your numbers, nothing graded, What the oil…"* reads
     as an instruction, then a fragment, then a new list item, inside one line.
  3. **ONE FACT WAS ADDRESSED TO THE MODEL, NOT THE MAN.** `plumbing/service-writeup`
     item six ended *"The write-up prints what he typed, verbatim … it never
     suggests, substitutes or completes one he didn't give"* — an OUTPUT RULE
     wearing the shape of a thing he says out loud.

**EVERY EXISTING GATE PASSED ALL THREE.** `node --check` passes (valid JavaScript).
The docspec gate passes (all eleven blocks present, non-empty, family legal, every
`omit` line reaching the block). The mobile gate passes — a watertight layout around
a broken sentence. A screenshot passes. Only a HUMAN READER catches these, and the
program had arranged for there never to be one.

**THE RULE.** Any authored field whose only consumer is a machine is on the clock.
Either put it in front of a person on the page — which is what the say-list does, and
which is how all three were found within minutes of it rendering — or gate its SHAPE,
not just its presence. "It reaches the block" is not proofreading.

### 2026-08-25 (C3658) — A GATE THAT COMPARES THE ENGINE TO ITSELF PROVES NOTHING
The say-list gate's central claim, in its own header, was *"every line the card shows
reaches the emitted block, and every fact the block checks reaches the card — the two
readers see the SAME list."* It asserted this by reading `.say li` out of the DOM and
comparing it to `window.DocSpec.factsOf(d)` called by the test. But the DOM was
populated by `renderSay()` calling **that same function on that same input**, and
`textContent` round-trips a string exactly — so the comparison could not fail short of
a browser bug. The cue check was the same shape: `sayCue(d)` rendered, against
`sayCue(d)` called. **Two of the gate's assertions were structurally incapable of
failing, and the one check that did touch the emitted block compared bullet COUNT and
never a single string.** A genuine divergence between what the card shows a man and
what the block tells his AI to check for would have passed, green, silently.

Found by an adversarial pass, not by the four negative controls that ran before it —
because a negative control asks *"can this gate fail?"* and both of these could, on a
defect injected into the shared function. **A tautology hides from its own negative
control whenever the control edits the thing BOTH sides read.** The test is not "does
it go red when I break the code"; it is "**do the two sides of this compare come from
different places**". Now: the card's rendered DOM against the COMPOSED BLOCK TEXT, line
by line, in order — two artefacts built by different code paths. Proved by rendering
the card one character short of the block: 214 failing.

### 2026-08-25 (C3658) — A GATE THAT FINDS A LINE BY HOW ITS AUTHORS START SENTENCES GOES BLIND SILENTLY
The say-list gate located the halt bullet with `/- (?:Only|Never|The notes|He wants|Anything
about it)[^\n]*/` — an alternation of the opening words the corpus happened to use. One
author does not: `plumbing/service-writeup` opens *"Stop and ask on two things only:"*.
That document's halt was never matched, so **both** halt assertions simply did not run on
it — no failure, no skip message, nothing. The gate reported 21 doublings where the merged
libraries hold 22.

**A missed match is indistinguishable from a passed assertion**, which is the whole
problem: the count printed in this book's own draft was wrong, twice, from two different
readings — a source grep said 14 (it missed the shared library's per-trade overrides) and
the gate said 21. The halt is structurally the SECOND of three bullets under
`WHEN SOMETHING ON THAT LIST IS NOT IN MY INPUT:`, so it is now taken by POSITION, and the
group's bullet count is itself asserted so the position cannot drift unnoticed. Rule:
locate a line by its STRUCTURE, never by the words an author chose — and when a gate
cannot find what it was told to check, that is a failure, not a silence.

### 2026-08-25 (C3658) — SUPPRESSING A REPEATED VERB TOOK THE EXCLUSIVITY WITH IT
Twenty-two halts already contain "stop and ask", so the engine appending *"That is the
ONLY reason to stop and ask me a question."* made the bullet say it twice. The fix
suppressed the tail whenever the author's own words carried the verb — which is
lossless for **21 of the 22**, because they also say *"Only stop and ask if …"*.
`gc/impact-notice` is the twenty-second: *"The notes are really about weather, or they
already have dollars and day counts attached. Stop and ask — a weather day is its own
notice, and a priced claim belongs to the PM and counsel."* Verb, two conditions, **no
exclusivity**. Suppressing the tail there converted the one halt in the program that
names two conditions into a licence to interrogate about anything.

**The test was on the WORDS the author used; it had to be on what the sentence CLAIMS.**
The tail now stands down only where the author already made the rule exclusive, and
where he used the verb without it, exclusivity is supplied in words that do not repeat
him. Two counts were wrong in the first draft's own comment as well — *fourteen across
three trades*, from a source grep; the artifact says **twenty-two across four**, because
the grep missed the shared library's per-trade overrides. **The block is the ground
truth about the block, every time.**

### 2026-08-25 (C3658) — THE GATE MEASURED ITS OWN SAFETY NET AND CALLED IT GREEN
`factsOf()` was written with an asymmetric fallback: a document with no `facts` of its
own inherits its FAMILY's, so a page served from a branch that skipped the gate still
says something instead of emitting an empty check. Sound belt. Then the new gate's
first negative control — delete framing's five `facts` back out, restoring EXACTLY the
state that had been live — came back **GREEN, 1,940 checks, 0 failing.** The fallback
caught the defect before any assertion could see it, and the gate's own header claimed
"the gate refuses the empty case outright so the belt is never load-bearing." That
sentence was false at the moment it was written.

Same family as *A GATE LEFT RED BY THE CYCLE THAT REDDENED IT* (2026-08-24) and *A GATE
THAT NEEDS THE FIX TO RUN CANNOT PROVE THE FIX* (2026-08-25, C3657), and worse in kind
than either: this gate was green for the right-looking reason. **A belt written in the
same cycle as its gate will hide the defect from the gate unless the gate is aimed
UNDER it.** The assertion is now on `d.facts` — the authoring — not on `factsOf()`, the
resolution. Rule: when a fix adds a fallback, the gate asserts the thing BEFORE the
fallback, and the negative control deletes the authored data, not the fallback.

### 2026-08-25 (C3657) — A TRUE-SOUNDING TOAST IS HOW A DEFECT SURVIVES A MONTH
Card Studio's handoff said "Picture placed from persona500 - ready to print" while the
picture rendered **0.00% visible** under a template's artwork. Every word was true: it
WAS placed, it WAS full-card, it WAS ready to print. The element bookkeeping agreed —
`x:0 y:0 w:85.6 h:53.98 fit:cover`, one element added, `S.sel` set, an ack posted. The
only thing that disagreed was the card, and nothing measured the card. The rule this
mints: **a message that reports an ACTION must be earned by the RESULT, not by the
action succeeding.** Where a placement can land somewhere the eye cannot reach, the gate
measures RENDERED PIXELS through the same renderer that prints — KILL-TEST 5 does, and
the 0% it found had been shipping under a green message and a green KILL-TEST 1, which
only ever ran against a blank face. A control case that cannot fail is not coverage.

### 2026-08-25 (C3657) — "BOTTOM OF THE STACK" IS A RULE ABOUT TEXT, APPLIED TO EVERYTHING
`placeFullCard` unshifted to index 0 with the comment "a full-card image dropped on top
would hide the text." That reasoning is correct and it is *narrow*: it was written for a
card carrying a NAME. Applied to a card carrying full-bleed ART it inverts — the picture
is what gets hidden, and 47 of the shipped templates are exactly one opaque full-card
image. A placement rule stated as a POSITION ("bottom") silently assumes what else is on
the face; stated as a RELATION ("above anything that covers the card, below everything
else") it holds in both worlds and reduces to the old behaviour when nothing covers. When
a comment justifies a constant with one scenario, that is the scenario it was tested in —
ask what the OTHER faces carry before trusting it.

### 2026-08-25 (C3657) — A FIX THAT ACTIVATES A LATENT DEFECT IS HALF A FIX
Making the picture visible was the whole ask, and it armed something that had been
unreachable: the deck's fronts carry their tap-mark colour HARDCODED, each measured once
by hand against its own baked artwork (leviathan-front ships `marks/tap-white.png` because
its art is dark). Cover that art with an arbitrary photo and the measurement is stale — a
white mark on a pale picture is a mark nobody can find. It could not fire before, because
before, nothing ever actually changed what was visible. The rule: **when a fix makes a
previously-dead path live, that path is part of the fix's blast radius and gets answered
in the same change** — here `faceLum()` lifted out of `tapMarkElement` and `retintTapMarks()`
re-measuring after every placement, with the mark hidden for the sample or it measures its
own ink. A judge panel found this; the implementer had not.

### 2026-08-25 (C3657) — A GATE THAT NEEDS THE FIX TO RUN CANNOT PROVE THE FIX
KILL-TEST 5's strongest case sweeps every template carrying full-card art. Its first draft
enumerated them by calling the app's own `coversCard()` — a function the fix INTRODUCES —
so against pristine HEAD that case reported "0 templates" and failed for the wrong reason:
not "the pictures were hidden" but "the helper does not exist." A red proof that fails
because the harness cannot run is not a red proof. The predicate is now spelled out inside
the test, and the same case reads all 47 templates at 0% against pristine and 47/47 clear
against the fix. **A gate's discriminating case may not depend on the code it discriminates.**

### 2026-08-24 (C3655) — A GATE LEFT RED BY THE CYCLE THAT REDDENED IT GATES NOTHING
Pangea's own killtest read 40/41 when C3655 picked it up — red since 45bcc6fc11 rewrote
the modal's carry line ("Opens your picture in Card Studio, ready to print") without
running the page's killtest, which still asserted the OLD copy ("opens blank, travels as
PNG"). Every later cycle inherits a red that is not theirs, and a gate that is already
red cannot catch the next defect — the whole point of the 41st assertion is lost the day
one stale FAIL is normal. The rule: the cycle that changes a page's COPY runs that page's
killtest in the same cycle, and a red you inherit gets dated (`git log -S`) before it
gets fixed — C3655 dated this one to a pushed commit, updated the assertion to the new
copy's honesty contract, and left the gate 41/41. Sibling lesson, same cycle: the
live-blades branch of the tuft pass consumes two extra rf() per blade, so a repaint with
`live:null` shears the foreground layout off the hung plate — any repaint of a
motion-composed plate passes a THROWAWAY live score (same stream spend), never null; the
lean-in bakes that rule in at Lean.settle().

### 2026-08-24 (C3654) — A MEMBERSHIP THE CHECKLIST DOESN'T NAME IS THE COMMONS HOLE, DUG A THIRD TIME
Painting stood up at C3653 with six tools, every gate green — and none of the three
boundary pages, unnamed. The only construction kit that could not send an ask, answer a
list or ask a building for a night looked complete on every count we run, because the
counts count what exists. Framing joined with no commons chip; roofing joined with a chip
and nothing behind it; painting joined outside the boundary: three different surfaces, one
failure — §TRADE EXPANSION's checklist is the only place a stand-up learns what a trade IS,
and a membership it does not name will be missing and invisible. The boundary pages are on
the checklist now, with the rule that a deliberate deferral is WRITTEN into the stand-up
entry the way flooring's DOCS debt was. An unnamed absence is not a decision, it is a hole.

### 2026-08-24 (C3654) — A PAGE COPIED PER TRADE WEARS THE DONOR'S NAME IN THE LINES THE RUNTIME NEVER TOUCHES
The boundary pages are one file copied per trade; the config swaps the on-page text at
load, so a stand-up patches what a reader sees and skips what a TAB shows. Swept at C3654:
sitework's rough-in wore MASONRY's <title> over CONCRETE's apple-title while its own config
said "Before We Dig"; sitework's answer page wore masonry's title too; three trades'
home-screen names said concrete's "What I'll Set"; flooring's getting-in description was
concrete's truck-and-pump under a page about twelve-foot rolls and a freight lift. Nothing
on the glass was wrong, so no eyes and no gate ever met the defect — it lived in bookmarks,
tab bars and link previews. `boundary-titles.mjs` now derives the truth from each trade's
own config and was proved red on the shipped sitework title before being trusted. The
class, one sentence: the donor's name survives wherever the runtime doesn't reach.

### 2026-08-24 (C3654) — AN ENGINE OPT-IN THAT ONLY ONE CONFIG EVER TOOK IS A PROMISE NOBODY CHECKS
`answers[]` — the answer page's own trade-vocabulary override, positional by design — had
exactly one taker (creative) since it was built. Flooring's page promised four trade rungs
in its lede, its registry desc, its storefront note and the items.js design comment ("the
two answers he never gets to give"), and shipped the default buttons for eleven days:
the override was simply absent, so every consistency gate passed, because a gate can only
check what exists and the lede's promise was the one witness no machine read. The half that
is machine-checkable is now checked: `answer-tapnote.mjs` asserts the baked tap instructions
say the words the config ships (proved red by injection), and `reconcile-join`'s vocabulary
check — which already existed and caught all six new rungs before ship — closes the loop's
far end, because a rung VERDICTS cannot classify turns a real answer into "didn't say yes
or no" one page over. The ledes stay human-read; that is named here, not solved.

### 2026-08-27 (C3674) — A CONFIG WITH A MISSING KEY IS NOT A MISSING SENTENCE, IT IS A BLANK PAGE
`doors/getting-in.html` is a copy of a shared engine page driven entirely by
`TOOLKIT_GETIN`. The new config was written by hand from the donor's shape and came
out with fourteen of its seventeen keys — every visible one. The three it missed
were `phCo`, `warn` and `closing`, and `closing` is the one the page CONCATENATES:
`G.closing.concat([...])`. An absent key is `undefined`, `undefined.concat` throws,
and the page rendered NOTHING at 320, 360, 390 and 430px. It was in the commit.

WHAT DID NOT CATCH IT, and this is the part worth keeping. `node --check` passed —
the syntax was perfect. The items.js file parsed and every key I *had* written held
good copy. The hand-written drive test passed 34 assertions and never opened this
page, because I wrote assertions for the pages I had authored and treated the three
config-only pages as already-working copies. Every consistency gate that reads
CONTENT was green, because a gate can only check what exists, and the failure was a
thing that did not exist. `mobile-watertight` caught it, on the strength of one
rule: it reads `pageerror`, so it does not need to know what the page was for.

THE CLASS, in one sentence: **when a page dereferences config, a missing key fails
LOUDER than a wrong value and is harder to see, because the wrong value is on the
glass and the missing key is a blank screen.** The generalisation that shipped with
the fix: after writing any new trade's `items.js`, DIFF ITS CONFIG KEY SETS against
the same configs on three or four sibling trades and treat any key the siblings all
share as required. That took one command and found the bug in the two other configs'
worth of surface area I had not yet checked (both were complete). The doors drive
test now opens every config-driven page and asserts `closing` is an array before it
asserts anything about words.

### 2026-08-27 (C3674) — A COUNT OF MENTIONS MEASURES WHO TRIPS OVER YOU, NOT WHO YOU WRITE TO
The #15 shortlist was opened with a keyword scan across all fourteen kits, and it ranked ELEVATOR
first: 16 mentions in 11 kits, the broadest reach on the board. Pulling the actual context killed
it — "freight elevator's ours 7 to 9", "elevator recall on test", "scuffs by the elevator, cart
height", "the elevator returns" to paint. Eleven of the eleven kits mean the elevator as a BUILDING
OBJECT or a piece of hoisting logistics; exactly one names the mechanic as a person who has to show
up. The who[] roster count, which reads the receivers a kit actually addresses, put elevator at 1.
This is the second consecutive stand-up where the count-first instrument nominated the wrong trade
(#14's was doors-by-supply-loop), and the rule is now general: **a mention measures how much other
trades trip over your work; only a receiver entry measures whether anybody sends you mail.** Run
the who[] tally before the keyword scan, not after it.

### 2026-08-27 (C3674) — I CAST A PANEL ON A SHORTLIST THAT WAS MISSING THE FRONT-RUNNER
Four lenses went out on twelve candidates, and doors — the trade the private ladder had recorded as
the STANDING FRONT-RUNNER for #15, in writing, with its re-hearing already done — was not on the
list, along with ceilings and steel. The record was read four tool-calls later. The correction went
out mid-flight by message and every lens answered it, so nothing was lost but the cost was real:
one lens ranked doors without ever having been asked about it in its first pass, and the panel's
verdict had to be read across two rounds instead of one. **RE-GROUND MEANS THE ROSTER BEFORE THE
PANEL, NOT ALONGSIDE IT.** The build loop's step 0 says read the BOOK for the rung you took before
you build; this cycle proves it also applies before you SPEND — a fan-out is a commitment, and
casting one against a shortlist you have not yet checked against the record is the same class of
waste as building a tool that already shipped.

### 2026-08-27 (C3674) — A PAGE COPIED FROM A SIBLING BRINGS ITS SIBLING'S STORAGE KEY
`doors/not-ready-to-hang.html` was built from `painting/not-ready.html`, and every visible string
was swapped — title, apple-title, eyebrow, h1, lede, warn, closing, every placeholder. What survived
was one line of script: `var KEY = "toolkit.painting.notready.v1"`. Two trades would have shared one
saved note, and the symptom would have been a painter opening his doorway note and finding a door
hand's openings in it — on a page whose entire purpose is a dated record of what was wrong before
work started. No gate covers this: the key is invisible on the glass, it is not a title, and both
pages work perfectly in isolation. It was found by grepping the new directory for the DONOR TRADE'S
NAME rather than for anything about the feature — the same sweep that found a donor comment and a
donor lede in two other files. **Grep a new trade directory for the donor's name before you ship
it, and read every hit — the runtime reaches the copy, it does not reach the keys.**

### 2026-08-24 (C3653) — A REQUIRED CHIP THAT STICKS IS A FIELD THAT CLEARS ITSELF
`painting/coat-count.html` shipped its coat picker as `input:"chips", required:true, sticky:true`
and the restore gate skipped the page at 2 of 3 rows: chips TOGGLE, and a sticky chip arrives at
the next row already lit — so the one tap that fills every other field turns this one OFF, and
the row is refused for missing the thing the tap just removed. No sibling carries the combo
(swept all 13 the same cycle: zero `required` chips anywhere; the non-sticky variant on the ding
ledger is safe because a cleared field can only be turned on). The class: `required` guards what
a row must SAY; `sticky` preserves what a hand just DID; on a toggling control the two guards
fight, and the machine driver that taps once per row is exactly a thumb in a glove. A chips
field may be required or sticky, never both — and the gate that found it is the reason a new
trade runs the whole battery before it ships, not after.

### 2026-08-23 (C3650) — THE GATE ASSERTED THE FORMAT FROM MEMORY, AND THE ENGINE'S OWN COMPOSER DISAGREED
The first full run of `lang-layer.mjs` failed 7 of 12 pages for "the ES (EN) composition did not
reach the document" — and every one was a tick that carries a `sub`, which `Lang.tick` prints as
"es — sub (en)", exactly as the first instance had for five days. The gate was written from the
simplest case and it flagged the engine's documented behaviour. An assertion about a composed
value is derived from the composer (or made by calling it), never from a remembered example; the
fix was one line and the lesson is the class: when a gate fails on the data the engine was built
for, suspect the gate first, on the evidence, before touching the engine.

### 2026-08-23 (C3650) — A BAR LABEL IS GEOMETRY, AND TWO NATIVE JUDGES PASSED A STRING 2.5× WIDER THAN ITS BOX
Every count label the panel returned was correct Spanish and none of them fit: the bar's count
box is 94px at 390px (80 on electrical), "1 hombre en el vale" needs 147px, and gc's
first-instance "1 línea de cuadrilla en el vale" needs 239px — it had shipped truncated to
"1 LÍNEA DE C…" and nothing caught it, because the count is `text-overflow:ellipsis` by design
and an ellipsis is neither overflow nor a clipped tap target, the only things the mobile gate
measures. A translator sees words; a box sees pixels. A string that lives in a measured box gets
a character budget in the brief (≤ 12 here) and a measurement before ship — and that
measurement found the ENGLISH "Nothing on it yet" (131px) has never fit the box either (named
remainder, C3650 cycle line).

### 2026-08-23 (C3650) — A TRADE CLONED FROM ITS NEIGHBOUR KEPT THE NEIGHBOUR'S EXAMPLES, AND ONLY A TRANSLATOR NOTICED
`sitework/tm-tag.html` was cloned from masonry's and four of its placeholders were still
masonry's — "180 pc 8 in block · 14 bags mortar · 1 yd sand · 2 pc lintel", "third lift",
"re-laid three courses" — on a page for a crew that lays pipe. It passed every gate for a week,
because a placeholder is not in the document and no gate reads an example for trade sense. The
Spanish it produced is what surfaced it: the trade judge would not put block on a sitework page.
A page cloned from a sibling diffs its `ph:` lines against the sibling before it ships, and a
long placeholder shared verbatim by two trades is a defect until proven a job name — the sweep
is nine lines of Python and it found exactly those four and nothing else.

### 2026-08-23 (C3649) — THE WISH'S URL WAS THE WELL'S OWN HANDWRITING, AND TWO LENSES AND I READ IT AS A VISITOR
The vibe-cards deck stamps `page_url: location.href + '#' + address` on every wish it sends, so
whoever serves the wish can re-grow the picture the wisher was looking at. Wish `e6f1af4d` arrived
carrying `deck/#fo|seed=4211|…`, and the proposal built a whole JS doorway to catch "visitors landing
on that hash" — regex, hashchange, three engines' grammars, a kill-test with 29 assertions. Two judges
scored it 8 and 6. The third grepped the well, found the stamp, and scored it 3: nobody had ever stood
at that URL. The deck had never read its fragment, nothing printed points a `fo|` address at it, and
the only place the string exists is the row in the queue. **A page_url in a wish is what the PAGE
wrote, not where the PERSON was.** The AV well's `about_tool` / page fields are written the same way.
Before reading any page_url as a landing, grep the SENDER for how the field is built. What shipped was
the unanimous core — the static link that carries the address, the dead button fixed at its source,
and a gate for the class — and the doorway is a dead branch in the deck's RING 4 with its trigger
named. Cost of the misread if unjudged: stranger input parsed into an href, on a public page, for
traffic that does not occur. K2 held because the panel is not ceremony.

### 2026-08-23 (C3649) — A GATE THAT READS THE DIARY PASSES THE THING IT WAS WRITTEN FOR
`tools/verify_fragments.mjs` (vibe-cards) resolves every `href="…#frag"` against the target page's
ids. Its first run, on the build that still had the dead `../deck/#panel-fo` link, printed
"every in-site fragment resolves." The deck's RING 2 change log — an HTML comment — says
`id="panel-fo"` in prose, so the deleted section was "found." Comments, `<script>` and `<style>` are
not places a fragment can land; the gate strips all three now. The lesson is the E1 discipline
itself: run the new gate on the artifact that is KNOWN broken before trusting a green — the
observation that had to fail, and did not, is the only thing that caught it.

### 2026-08-23 (C3647) — THE ANTI-FIXATION MECHANISM WENT BLIND AGAIN, THE OTHER WAY
The bump's LIVE STATE told this cycle **"STALEST-AXIS SIGNAL = DEPTH — last
worked 14 lane-cycle(s) ago"**. DEPTH had shipped in each of the two cycles
immediately before it.

`field_toolkit_directive.py` opened both books with `.read(400000)`. The books
are APPEND-ONLY and §CYCLE LOG is the LAST section of each, so the day
`av/AV_SOCIETY.md` crossed 400,000 characters the parser stopped seeing its
newest lines — **and only its newest lines**. Measured at the fix: the file is
472,507 chars (72,507 invisible, the last ~15 cycle-log entries) and
`COLLAGE_EVOLUTION.md` had crossed too, at 401,166. The true staleness, once the
whole file is read: **COLLAGE 22 cycles, BACKPORT 15, BREADTH 12, INTERFACE 6,
WELL 5, DOCS 2, COMMONS 1, DEPTH 0.**

This is the SECOND time this mechanism has failed, in the second way, for the
same underlying reason both times: **a blind reader's output is indistinguishable
from a truthful one.** In 2026-08-06 it read only one of the two books, so
COLLAGE scored "never worked" forever and was picked every cycle. Today it reads
both and TRUNCATES them, so the axis worked most recently reads as the one worked
least. A mechanism whose whole job is to prevent fixation was generating one, in
silence, in both directions.

**A BYTE CAP ON A FILE THAT GROWS FOREVER IS A DEADLINE, NOT A GUARD.** The
fix is `read_book()` (one helper, both readers — the private roster's reader had
the identical cap and is 55KB today, i.e. the same failure with a later date on
it) plus the NEGATIVE CONTROL the first fix never had: the check suite now
asserts that the LAST tagged line physically present in each book is inside what
`cycle_log_lines()` actually returns. A truncating reader passes every other
check in that suite.

Append here when a cycle finds one. Each is a rule, not a story.

- **A BUILD THAT FINISHED ON DISK IS NOT A SHIP, AND ITS OWN COMMENT WILL TELL YOU IT WAS
  (2026-08-23).** `sitework/docs.js` (40KB, 15 documents) and `sitework/write-up.html` were
  written by a concurrent peer session at 13:07 and never committed. That session then wrote
  into `sitework/tools.js`: *"SHIPPED 2026-08-22 … it closed the DOCS axis: thirteen trades,
  thirteen libraries, none left owed."* The peer died before `git add`. Eleven hours later the
  live URL was **404**, the book's previous entry said the axis had reached the last trade, and
  the bump's own LIVE STATE line — which reads `tools.js` off DISK — counted **98 tools when the
  artifact served 97**. Every instrument in the loop agreed with the file that was never pushed.
  The rule: **a registry line is a claim about the artifact, so check it against the artifact.**
  Sweep every trade's `tools.js` and curl every `href` against the live site — 13 trades, 98
  pages, derived from disk, never a typed list. It is the only check that can see this class,
  because the page, the registry, the gates and the book all live on the same side of the push.
  Sweeping the wells for a dead cycle's CLAIM was already doctrine; a dead cycle's BUILD needed
  its own instrument.

- **THE ROSTER PREDICTED THE WRONG FAILURE MODE, AND THE PREDICTION WAS THE OLD FIX'S SHAPE
  (2026-08-23).** The named next COMMONS rung read: *"`shared/docspec.js` is trade-siloed, so a
  man who knows 'punch list reply' from framing GETS NOTHING on any other trade's write-up."*
  Measured through the real search box, 733 unambiguous terms × 13 trades = **9,529 searches:
  ZERO dead ends.** `shared/find.js` never returns nothing — that is rule 2 of its own header,
  written eight days earlier. The rung had been filed in the shape of the surface it was
  isomorphed FROM (the commons tips page, which really did dead-end), and the shape did not
  survive the crossing. The real failure was the opposite and worse: a **confident wrong
  document**. The rule: **a rung inherited from a sibling surface names a HYPOTHESIS, not a
  defect — re-measure it on the surface you are about to change before you design the fix**,
  because a fix aimed at a dead end does nothing about a confident answer.

- **A NUMBER THAT IS A FUNCTION OF THE SCHEMA IS NOT A MEASUREMENT (2026-08-23).** This cycle
  took "**70.6% of searches return a confidently wrong document**" to its own judge panel. The
  refute lens killed it with arithmetic: 5,644 of the 6,727 misses are queries naming a document
  the reader's trade does not carry, and that cell equals Σ(13 − k) over terms — **a closed form
  in "57 of 69 documents live on one trade", computable without running a single search.** It
  measures the library's SHAPE, not the search's quality, and it carried 84% of the claimed
  failure mass. Worse, the label was wrong too: the page already prints *"Closest to …"* on an
  approximate hit, so only **3,360** of the misses were handed over unhedged. The honest pair,
  and the only two numbers this book should quote: the **in-library miss rate, 1,083 / 3,885 =
  27.9%**, and its unhedged half, **512**. The rule: **before a headline number leaves a cycle,
  ask what it would be if the code were perfect.** If it barely moves, it is describing the data
  model, and the panel will find that faster than you will.

- **A NEW LIBRARY DOCUMENT COLLIDES WITH A SHIPPED TOOL, NOT JUST ANOTHER DOCUMENT
  (2026-08-22).** flooring's `directed-to-proceed` write-up and the PINNED `give-me-the-go.html`
  tool are one job with two front doors — a floor not ready per your own instructions and you
  are told to install over it anyway. The author's own design comment proved the collision
  check ran only against §SAFETY (the warranty-void edge) and the other library documents;
  nobody asked whether a shipped TOOL already owned the trigger, even though its `aka` carried
  "they said go". An adversarial panel's collision lens caught it. The rule: §THE GATE's "one
  job per tool" is CROSS-SHAPE. When a `docs.js` document lands on a served trade, walk that
  trade's `tools.js` and steer past any tool whose trigger it shares — the `delay-notice`→
  `give-me-the-go` note is the template — the same way documents already steer past each other.

- **A DEAD CYCLE'S HALF-BUILD AND A LIVE PEER BOTH READ AS "ALREADY TRACKED" — VERIFY THE
  CONTENT, NOT `git status` (2026-08-22).** `flooring/write-up.html` and `sitework/write-up.html`
  sat untracked since a cycle died between build and ship (no `docs.js`, a literal
  `LEDE_PLACEHOLDER` on sitework) — the 2026-08-14 pattern, seen only because tree-before-well
  looked. Mid-build a concurrent peer session in the same repo read the in-progress flooring
  work as that orphan and briefly committed+reset it, so for one window `git ls-files` showed
  `flooring/docs.js` TRACKED and `git status` showed it UNCHANGED while `ls` showed the 33KB
  working file. The rule: after any git-state surprise on a shared repo, confirm the working
  tree by GREPPING the file for the edits you made, never by trusting `git status` alone — and
  split the work by message before committing (peer took sitework, this took flooring, zero
  collision).

- **A FIELD THAT SHIPS ON ONE PAGE WHILE ITS SIBLINGS CARRY THE HAND-ROLLED VERSION IS NOT
  SHIPPED, IT IS A FORK WITH A BETTER HEADER (2026-08-19).** `shared/dropoff.js` landed on
  plumbing on 2026-08-14 and sat for five days beside five order pages still printing
  `fAccess`/`fSigner` free text — the exact class the rider exists for, and the roster's own
  "single most concrete unbuilt thing". The rule: when a shared block REPLACES something, the
  replace IS the ship; count the pages still carrying the old shape in the cycle-log line
  and name each one taken or not taken by decision. And carry the old answers over — the
  card keeps the boxes that left (`carry:`), the block seeds from them ONCE, and a seeded
  record persists even empty, or clearing it resurrects the very text he just cleared
  (caught by writing the gate before the page: 2 pages × 2 storage shapes, mutant-killed).

- **A PLACEHOLDER TEACHES THE DOUBLE ENTRY (2026-08-19).** The gate line's example text read
  "… no trucks in the alley before 7" under a control labelled *Not before* — so the block
  printed `When: morning, not before 07:00` beneath a gate line that already said "before
  7": two clocks for one fact, and a driver trusts the wrong one after an edit (the
  receiving lens). If a control owns a fact, no example anywhere on the page may model that
  fact in prose. The one clock now prints ON the gate line, and the gate asserts `When:`
  never carries a time.

- **A CHIP THAT CONTRADICTS A FIELD STILL PRINTED IS A CHIP THAT LIES LATER (2026-08-19).**
  "Drop point — no signature needed" shipped in the first cut beside a sticky *Signs for it*
  box still holding a name from a truck order in March — one message, two answers. The
  foreman lens caught it before ship. A chip may not carry a claim that another field on the
  same block answers; it says the place ("Left at a drop point") and the field says who signs.

- **A TICK MUST ASK BEFORE IT STATES (2026-08-19, the handback rule one level down).** "COI on
  file — tell me if it isn't" skims as "COI on file" — a status this page can never know,
  wearing the ask as a tail. The skeptic's shape is the rule: the ask LEADS ("Tell me if our
  COI isn't on file with you yet"), and `dropoff-block.mjs` fails any paperwork chip whose
  status word precedes its "tell me". Same for "approved carriers": ask first.

- **THE WATERTIGHT GATE HAD NEVER MEASURED THE BLOCK — THIRD INSTANCE OF THE CLASS
  (2026-08-19).** The drop-off block lives inside a closed `<details>` on four pages and
  behind a Delivery tap on two; `mobile-watertight.mjs` loads and leaves alone, so its twenty
  chips, the 2-row textarea and the multi row were sized at 320px by nobody until a revealed
  state was written (opens the drawer, walks the mode controls until `#dropoff` is on, lights
  a multi chip). Proved by an injected 600px chip failing at 320 in that state and nowhere
  else. When a shared block is MOUNTED somewhere new, ask which gates can SEE it there.

- **NEVER READ AN ANIMATED PROPERTY THE SAME INSTANT YOU CAUSED IT TO CHANGE (2026-08-18).**
  The tap-badge gate clicked a card and read the badge's `::after` opacity in the very next
  evaluate: it got `1` — the `.25s` transition had not left its first frame — and printed a
  FAIL against a rule that worked. The wrong next move was "fix" the working CSS; the diff of
  the two suspects settled it (the same rule read `0` after a 400ms settle, and the wide-deck
  badges, never flipped, rendered white in the same run). A gate that asserts a transitioned
  or animated value must wait out the declared duration first — and when a gate and the page
  disagree, suspect the gate's CLOCK before the page's CODE.

- **A GATE CAN GO BLIND WHILE LOOKING RED, AND THAT IS WORSE THAN GOING GREEN (2026-08-17).**
  `reconcile-join.mjs` read answer-back's verdict ladder out of the shipped page with
  `/var ANSWERS = \[([^\]]+)\]/` and then classified every rung against `reconcile.js`
  VERDICTS. A later cycle correctly made the ladder per-trade — `var ANSWERS = (A.answers &&
  A.answers.length === 4) ? A.answers.slice() : [...]` — and the regex stopped matching. The
  gate printed **1 FAILED of 99** and stayed that way, which reads as one cosmetic assertion
  about a source line. **Everything that mattered was inside `if (m)` and had not run since.**
  When it was repaired to derive the fallback literal AND every trade's own declared ladder off
  disk, it found on the first run that `creative` had renamed all four rungs — "Doing it",
  "Already in", "That's an extra", "Need from you" — and **not one was classified**, so every
  answer a creative sent came back to the requester as *"he didn't say yes or no."* THE RULE:
  **a gate that fails must fail LOUDLY ABOUT ITS OWN COVERAGE, not about a wrapper** — if
  reading the input fails, that is `checks = 0` for that section and it must say so. And this
  is §SCARS' own "matching on words" one layer out: matching on SOURCE SHAPE rots the day
  somebody improves the source, and the fix is the same fix — derive from data, never from
  how the data happens to be written today.

- **THE DEPLOY RUNS NONE OF THE TOOLKIT GATES (2026-08-17).** `deploy_bridge.yml` asserts the
  artifact hard — the three trade lists against each other, the commons chip coverage, the
  docspec contract, the feedback drop-in — and greps `tools/toolkit-gates/` **zero times**.
  Every browser gate in that directory is a local pre-ship gate somebody has to remember to
  run. Two live defects were found sitting on main this cycle purely because a stand-up
  happened to run them: two different `commons/gear.js` rows under one id `marking-paint`
  (the bag keys picks by id, so ticking one ticked both and neither could be removed alone),
  and a digit — "811" — in a `names.js` row on a page whose rail 4 refuses digits outright.
  Both had been shipping since trade #12. Not fixed by making CI slower: **recorded so the
  next cycle knows the green deploy is not evidence the gates passed.** Run them.

- **AN ENGINE FIELD NOBODY EVER DECLARED IS UNTESTED CODE WEARING A FEATURE'S CLOTHES
  (2026-08-17).** `shared/note.js` has shipped `buildImpact` since shape #2 was extracted, and
  `note.css` has styled `.impact` the whole time — the field §THE THREE SHAPES names as the
  reason the note exists (*"ordered short fields, ONE OF WHICH IS THE IMPACT LINE EVERYONE
  OMITS"*). Across twelve trades and twenty-odd note pages, **not one config ever wrote
  `kind: "impact"`**, and the two pages that wanted it — `gc/weather-day.html` and
  `hvac/repair-recommendation.html` — hand-rolled their own div beside it. Trade #13's pin is
  the first live use, and it immediately surfaced that `buildImpact` is the only builder that
  constructs its own wrapper and **never set `data-f`**, so `note-live-fields.mjs` — which
  drives a page by exactly that attribute — could never have covered it. THE RULE: **when a
  shared engine offers a capability no caller uses, that is not a spare part, it is an
  unexercised path**; either a config uses it or the gate must assert its absence, because the
  day somebody finally reaches for it they are the one who finds the bug.


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

### 2026-08-17 — A MOBILE GATE THAT MEASURES THE PAGE AT REST HAS NEVER OPENED A PANEL
Vibe Cards' `verify_mobile.mjs` — a fresh implementation of THIS toolkit's watertight gate,
credited as such in its own header — reported `/studio/` green at 320/360/390/430 the whole
time two of that app's controls did nothing on a phone. It was not wrong. It measures the
page **at rest**, and both defects existed only in a state it never enters: "Start from a
template" focused a `<select>` sitting in a rail that is a *sheet*, down and `display:none`,
so `focus()` landed on nothing, `showPicker()` threw, and the ping animated a border with no
pixels behind it — the element measured **0×0**; and the wish popover was `position:absolute
right:0` inside a wrapper the width of its own button, correct against a desktop bar pinned
to the right edge and **186px off the left** of a 390px phone. A panel is only wrong once it
is OPENED. **This toolkit already knew that** — `menu-reachability.mjs` and
`overlay-reachability.mjs` are exactly this check, and the sweep this cycle confirms
`.av-drop` lands inside the glass on all twelve trades at 320 and 390 with its first link
answering `elementFromPoint`. The capability existed and did not travel to the sibling app,
which is L3177 pointed the other way: **we re-derived a gate we already own, in a repo that
had copied everything about it except the part that catches this.**

### 2026-08-17 — ON THE SCREEN IS NOT THE SAME AS REACHABLE, AND A SCREENSHOT CANNOT TELL THEM APART
The first cut of that fix pinned both popovers to the bottom edge of the viewport. Rect
inside the viewport: yes, at all four widths, both engines. The **Send** button was
underneath the phone dock, and then underneath a raised rail's scrim — correctly sized,
fully painted, and the tap that submits a wish would instead have dismissed it and discarded
what was typed. A screenshot showed a working panel. What caught it was
`document.elementFromPoint` on the button's centre asserting the hit is the button:
**the only honest question is whether the finger reaches the element or something on top of
it.** The rails had solved this already by sitting ON the dock rather than at the edge; the
fix now uses their offset and closes any raised sheet, because one sheet at a time is a rule
this app already enforced among its rails and had never applied to its bar.

### 2026-08-17 — THE GATE PRINTED PASS OVER ZERO CHECKS, AND THE GIVEAWAY WAS IN ITS OWN OUTPUT
Found by running `menu-reachability.mjs` against the live site during the backport sweep and
pasting the base URL **without its trailing slash**. Pages are fetched as `BASE + page` with
a repo-relative path, so every URL became `…/nested-resonance-memory-archiveav/index.html`,
every page 404'd, every page reported no Tools menu — and the gate printed
`0 page x viewport checks over 0 toolkit pages (117 page(s) carry no Tools menu)`, then
**PASS, exit 0**. With the slash: **798 checks over 114 pages, PASS, tightest clearance
15.5px at masonry/answer-back.html @320x480.** Same command, same site, same day; the only
difference between measuring everything and measuring nothing was one character, and the
green line was identical. The tell was already being printed and ignored:
`tightest clearance: Infinitypx (undefined)` — a value that cannot survive a single real
measurement. **An empty finding-list from a gate that never looked is indistinguishable from
one that looked everywhere, unless the gate refuses to pass on zero.** Fixed twice over:
the base is normalised so the slash cannot be forgotten, and `checked === 0` now FAILS with
the malformed URL printed in the message. Pages that legitimately carry no menu are already
counted in `skipped`, so the only state rejected is having measured NOTHING — which also
covers a renamed selector and a host too slow for the 120ms settle. Proven by removing the
normalisation and re-running the exact command that had passed: it now fails.

### 2026-08-17 — THE COMMENT THAT DOCUMENTED THE BUTTON CLOSED ITSELF AND TOOK THE HANDLER WITH IT

The /gt/ card's wish script carried a block comment quoting the Content-Range header
value `*/0` — and `*/` is `*/` wherever it appears, so the comment ended mid-sentence,
the leftover prose was parsed as code, the SyntaxError killed the whole IIFE, and the
button a printed card points at did nothing when tapped. GT-001 had ZERO wishes ever;
every deploy was green; the wisher's report ("I hit the button and nothing happens")
was the first signal, ~2 months in. Worse: the first diagnosis blamed the visible
suspect — a silent `length<2` guard — and only extracting the script for a routine
`node --check` exposed the real killer. TWO laws: (1) prose inside a block comment is
CODE the moment it contains `*/` — write `*\/`; (2) a page's inline scripts must be
PARSE-GATED at build time (vibe-cards: `build_site.py::check_page_scripts`, HTMLParser
extraction — regex extraction false-positives on minified React whose strings contain
`"<script><\/script>"`). The archive is clean (125 pages, 117 blocks checked) and its
gates should grow the same check the day a new inline script lands.

### 2026-08-18 — TRANSLATE ON THE WAY IN, NEVER ON THE WAY OUT
The toolkit's first bilingual page (gc/tm-tag.html) flips language by reload, and its
first build translated the saved picks BEFORE calling location.reload(). Every free-text
field survived the flip and every picked label arrived untranslated — because the note
engine flushes on pagehide/visibilitychange, both of which fire DURING the reload, so
the exit flush re-persisted the untranslated state on top of the remapped draft a
millisecond after the remap wrote it. The e2e caught it; a screenshot never would have —
the ES page and the EN page each looked perfect alone. The fix is a direction, not a
patch: a page that rewrites its own persisted draft around a reload must do it AT BOOT
of the NEXT load, where nothing else is still writing — and a boot-side remap is
idempotent (same-tongue picks pass through), which an exit-side one can never be.

### 2026-08-23 — THE COPY-BUTTON WORD IS PART OF THE BAR GEOMETRY, AND A LONGER ONE OUTGREW A MEASURED THRESHOLD
The fixed action bar hides its line-count label below a MEASURED width (`@media (max-width:356px)`), and that number was calibrated against masonry's "Copy the call" — a four-letter final word. Roofing's material order (`order-the-load.html`) shipped its first draft with the same bar carrying "Copy the **order**": one letter wider, ~8px more button, and at 360px — just above the 356 threshold — the count "Nothing on it yet" no longer fit beside the two buttons, wrapped to 46px, and grew the fixed bar 2px, which mobile-watertight (correctly) fails as a bar that GREW. The trap: the threshold reads like a property of the COUNT text, but it is a property of the WHOLE bar, and the copy word is a load-bearing input to it. Two ways out — match the proven four-letter word ("Copy the **load**") so the geometry is masonry's unchanged, or re-measure and move the threshold. Took the first; the word is roofing-true and the constant stays honest. LESSON: when you isomorph a page whose fixed-bar threshold was MEASURED, the button LABELS are part of what was measured — change the words and the number is no longer yours.

### 2026-08-25 — THE FALLBACK OPENED A TAB THAT WAS STRUCTURALLY INCAPABLE OF RECEIVING ANYTHING
"Open in Card Studio" on bifurcata/leviathan/pangea was one compound guard —
`if (cell && !busy && !batch) { var w = window.open(...); if (w) { ...handoff... } }` —
and its own comment named the escape: "a blocked popup (w null) falls through to the
anchor's href opening the studio - the fallback." But that anchor carries
`rel="noopener"`. The tab it opens has **no `window.opener`**, so the sender can never
postMessage into it and the studio can never announce readiness back: the fallback was a
tab that is structurally incapable of doing the one job the door exists for. Blank
forever, and — because the handler never reached `preventDefault` — no toast either. THREE
legs fell through it, not one: no cell, a cut already in flight, and the blocked pop-up.
The everyday leg is the middle one, because the door closes the modal the instant it is
tapped: a hand that comes back for another world taps again while the first cut still
holds `busySave`, and gets a second blank tab. Filed twice in three minutes by the same
thumb ("this one didn't go to card studio but others did"; "it didn't take at first, then
I exited, clicked it again and it took"). LESSON: a fallback is only a fallback if it can
still do the job. `rel="noopener"` is not a detail of the anchor — it is a statement that
this path can never carry a handoff, so every branch that lands on it must either be a
branch where no handoff was wanted, or must speak.

### 2026-08-25 — THE COMMENT SAID WE ANSWER THE READY PING, AND THE LISTENER ARMED AFTER THE RENDER
The studio side had just fixed exactly this (`dee4922`: "the listener now arms at PARSE,
top-level, before boot() is even called") and published the contract in its own comment:
"On arm the studio posts a content-free {vibeReady:1} to its opener: today's senders
ignore it; tomorrow's post the card on it instead of polling blind." The sender was then
written to honour it — `if (ev.data.vibeReady) post();` — and documented it as field
lesson one. It never fired. `window.addEventListener('message', onMsg)` sat inside
`rd.onload`, i.e. after the FileReader, which is after the whole 2066×1319 WebGL cut. The
studio's two ready pings land at parse (~0.5s) and boot-end (~1–3s); the sender's ears
went on tens of seconds later. Both pings were missed on every handoff that ever ran, and
the loop fell back to the blind 500ms poll the contract existed to retire. Same defect,
same handshake, opposite side, written by the hand that had just fixed the first one.
LESSON: a listener's ARM TIME is part of its contract. When you write "we answer X", the
gate to write is "was the ear open when X was sent" — not "does a handler for X exist".

### 2026-08-25 — I POKED A GLOBAL THAT DID NOT EXIST, AND THE GATE PASSED IDENTICALLY AGAINST BOTH BUILDS
The first draft of the door gate entered the busy state by `page.evaluate(() => { window.busySave = true })`.
These pages' JS lives inside `(function(){ ... })()`, so `busySave` is not a global: the
assignment quietly minted a NEW property the page never reads, the tap took the happy
path, and RED and GREEN printed byte-identical failures — a gate that told the two states
apart in neither direction. The only thing that caught it was a fail-loud guard written on
a hunch (`if (typeof window[f] !== 'boolean') return null` → the assertion printed `null`).
A second draft then entered the busy state honestly, by tapping the door, reopening the
modal and tapping again — and STILL tested nothing, because the cut resolves in about a
second in this harness, so the second tap landed on an idle page. Only a synchronous
double `.click()` in one gesture reproduces the state a thumb reaches. LESSON: a gate that
reaches into internals is testing the internals it imagined. Drive the surface, and prove
the RED before trusting the GREEN — a gate that fails the same way against both builds is
not a red gate, it is a broken one.

### 2026-08-25 — I WROTE THE MECHANISM INTO A COMMENT BEFORE I MEASURED IT
Noticing that pangea's `#toast` lacked the `max-width:calc(100vw - 28px)` its two siblings
carry, I shipped the cap plus a comment explaining that without it "a long line grows to
the viewport PLUS its own 28px of padding and pushes the document wider than the screen at
320px." Then I measured. `scrollWidth === clientWidth` at 320/360/390/430 on all three
pages, pristine included: the box is centred with `left:50%` and shrink-to-fits, so its
available width is the space from the 50% mark to the right edge — half the viewport — and
it never gets near the cap. The cap I added was inert and the reason I gave for it was
false. The real defect was the opposite one: at 320px a 122-character message rendered
160px wide and TEN LINES tall on every page. The fix is `width:max-content` (ask for the
line's true width, then let max-width clamp it): 160×161px → 292×82px, still no overflow.
LESSON: a comment that explains a mechanism is a CLAIM, and this book's comments are read
as fact by the next cycle. Measure first, or write nothing.

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

- **[AXIS:WELL] 2026-08-17 — Card Studio, reachable on a phone.** Two wishes, same defect
  reported 95 minutes apart, both served. *Before:* "Start from a template" pointed at a
  `<select>` inside a sheet that is down — measured **0×0**, and `showPicker()` does not
  exist on the engine the report came from; the wish popover opened at **L-186** on a 390px
  screen, and the Open menu at L-62 with it. *After:* the button raises the Card sheet
  through the same `openSheet()` the dock calls and scrolls the picker into view; both
  popovers are viewport-pinned bottom sheets lifted clear of the keyboard and sitting on the
  dock; opening either closes a raised rail so its scrim cannot swallow **Send**. **Proof:**
  new standing harness `tools/verify_phone_reach.mjs` — **24 findings** on the shipped code
  at `96b231b`, **0** on HEAD, **0 against the live site**, WebKit *and* Chromium at
  320/360/390/430, asserting `elementFromPoint` on Send and not just its rect; the repo's own
  `verify_mobile.mjs` still watertight on every page and `verify.mjs` 15/15. Recorded as a
  claim/could-have-failed/observed/limits entry in that repo's `docs/EVALS.md` §5 — with the
  wish text **removed** on a follow-up commit, because quoting it published queue contents
  the standard that repo ships says to keep private. **BACKPORT rider: FIRED** — swept the
  same class (`.av-drop`, the one absolutely-positioned panel in `shared/toolkit.js`) across
  **all twelve trades live at 320 and 390px**: inside the glass everywhere, no sideways
  scroll, first link hit-testable, worst margin 8px on electrical/low-voltage. Nothing to
  carry back: `sizeMenu()` already clamps that left edge and `menu-reachability.mjs` already
  guards it. The debt ran the other way, and this cycle paid it. **The sweep did turn up one
  thing:** running that gate live with the base URL missing its trailing slash printed
  `0 page x viewport checks over 0 toolkit pages` and then **PASS, exit 0** — with the slash,
  798 checks over 114 pages, tightest clearance 15.5px at `masonry/answer-back.html @320x480`.
  Base now normalised and `checked === 0` now FAILS; proven by removing the normalisation and
  re-running the command that had passed.
  https://mrdirno.github.io/vibe-cards/studio/

- `2026-08-17` — **[AXIS:BREADTH]** **TRADE #13 IS THE FLOORING FIELD TOOLKIT — the first
  family the counting rule could not have produced.** · **before:** both wells dry for this
  lane (the AV well 0 new / 0 building every trade; the vibe-cards well being actively drained
  by the persona500 lane, which shipped out of that pool five minutes before this cycle
  started and had 20+ uncommitted files in that repo — claiming there is a collision, not a
  service), no trade owed, stalest axis BREADTH at 10 lane-cycles. **§MASONRY set the method
  at #11 — "the rule NOMINATES, the record DISPOSES" — and this is the cycle where the two
  disagreed completely.** Re-counted off every served kit's own `who[]` roster rather than off
  the matrix summary: steel 4 (dead by name — the bolt-up log, weld map, WPS and mill cert ARE
  the IBC ch.17 special-inspection record), ceilings 3 (dead — ruled a DEPTH rung inside
  framing), fire/sprinkler 3, doors/frames 3. **FLOORING SCORED ZERO**, alongside glazing,
  insulation and demo, because a receiver roster can only name a party you hand paperwork to
  and this trade arrives after all twelve served kits have gone home. · **after:** `flooring/`
  live — hub + **6 tools** + vocabulary + credit ledger, `TRADES`, the `paths:` trigger, the
  runtime switcher entry, the commons chip and **26 commons rows** (9 gear · 9 tips · 8 names).
  **A FOUR-LENS PANEL CAME BACK 3-1 FOR THE TRADE WITH NO VOTES, AND THE FOURTH LENS WAS THE
  SKEPTIC, WHOSE JOB WAS TO KILL: *"I could not kill it."*** All four independently killed the
  top live nominee on the rule that killed steel — for a sprinkler contractor the certified
  record IS the deliverable (NFPA 13 hydraulic calc sealed by a NICET III or PE, the
  Contractor's Material and Test Certificate written into the standard, the ITM report already
  owned and numbered by inspection software); what survived its refusal list was a
  head-and-fitting order, one page, not a family. **KILL A SURVIVES HERE STRUCTURALLY RATHER
  THAN BY DISCIPLINE, which is the whole reason this trade is buildable and sprinkler is not:**
  flooring's numbers are not code tables, they are MANUFACTURER WARRANTY TERMS that disagree
  with each other, so there is no number to supply even if we wanted to. Every page takes the
  reading HE took and the limit HE typed off HIS own pail, prints both, and never says which
  wins. **THE ARGUMENT WAS THEN VERIFIED OFF DISK RATHER THAN TAKEN FROM THE PANEL:** three
  shipped kits already count down to this man's gate in their own words — `av/items.js`
  *"Before floor goes down"*, `gc/items.js` *"Before floors go down"* (**the LAST rung its gate
  ladder has**) and again *"Walk it with me before tile goes in"*, `low-voltage/items.js`
  *"Before tile goes in"* — and **grepping every `who[]` on the rack returns no flooring
  receiver at all**: `floor` appears only as a GATE and as `floorbox`, an electrical device.
  Three trades name the moment; **not one of them can address the man.** That is the sitework
  condition read off the opposite end of the job — the dirt crew owns the earliest gate, the
  floor crew the last — and **glue does not reopen** is harder than a backfilled trench: a
  bonded floor is not cut, pulled or dug, it is demolished, and the substrate under it is
  somebody else's ninety-day-old mistake that the man who covered it now owns. **THE PIN IS
  `give-me-the-go.html`, AND IT IS FIVE PROPOSALS COLLAPSED INTO ONE** — a 24-candidate roster
  from three independent in-trade lenses went through a 20-year prune that killed more than
  half, and the largest convergence in the pile by a mile was five separate names for one
  letter (*Can't Lay On That · Floor's Not Ready · Before I Glue · Going Over It · Give Me The
  Go*). It is named for the ASK, not the condition, deliberately: *"the floor's not ready"* is
  a complaint and the same sentence ending in *"give me the go in writing"* is a document, and
  that difference is the product. It offers BOTH doors — proceed in writing, or tell me who is
  fixing it and by when — because a refusal with one door gets a floor guy replaced instead of
  answered. **FIRST LIVE USE OF `kind:"impact"` IN THE PROGRAM, AND STANDING IT UP FOUND A
  DEFECT IN A PATH THAT HAD NEVER EXECUTED.** `shared/note.js` has shipped `buildImpact` since
  shape #2 was extracted and `note.css` has styled `.impact` the whole time; **no config on any
  of twelve trades had ever declared it**, while `gc/weather-day.html` and
  `hvac/repair-recommendation.html` each hand-rolled their own `.impact` div beside it. It is
  the one builder that makes its own wrapper and **never set `data-f`** — so
  `note-live-fields.mjs`, which drives a page BY THAT ATTRIBUTE, could not have tested an
  impact field even if one had existed. Fixed in the engine, for every trade. **BACKPORT RIDER
  FIRED THREE TIMES, on three independent classes, none of them the one I went looking for —
  and two were RED ON MAIN with nothing in CI to catch them, because the deploy runs NONE of
  the toolkit gates.** (1) `commons/gear.js` carried **two different rows under the id
  `marking-paint`** (concrete+gc's, and sitework's) since trade #12; the bag keys picks BY ID,
  so a man who ticked one was silently carrying both and could remove neither —
  `commons-bag.mjs` had been failing on it and nothing ran it. (2) `commons/names.js` rail 4
  refuses a digit in any string (*a name that needs a number to be right is certified data*)
  and the sitework `the-ticket` row has been failing it on **"811"** since #12; now spelled
  *eight-one-one*, which is also what a crew says out loud. (3) **THE SHARPEST ONE:
  `reconcile-join.mjs` had gone BLIND while looking red.** It read answer-back's ladder with
  `/var ANSWERS = \[([^\]]+)\]/`; a later, correct refactor made the ladder per-trade
  (`(A.answers && A.answers.length === 4) ? A.answers.slice() : [...]`) and the regex stopped
  matching — `ok(!!m)` went red, which reads as one cosmetic failure, but **every real check
  was inside `if (m)` and none of them had been running.** Repaired to derive the fallback
  literal AND every trade's own declared ladder off disk, it immediately found that
  **`creative` renamed all four rungs — "Doing it" · "Already in" · "That's an extra" · "Need
  from you" — and not one was classified in `reconcile.js` VERDICTS**, so every answer a
  creative sent read to the requester as *"he didn't say yes or no"*. Both fixed; the gate now
  fails the NEXT trade that renames a rung instead of failing a stranger. Exactly the class
  §SCARS already records one layer down — matching on words means a gate stops testing the day
  somebody improves the wording — and this is that class matching on SOURCE SHAPE. **THE
  ACCENT WAS MEASURED AGAINST A TWELVE-CHIP RACK** and the measurement killed the obvious
  picks: pure green scored the single widest gap on the board (dE 40.0) and is the worst chip
  on it (the rack already carries three greens); every warm option lands inside a band that
  already holds four chips, which is where wood tone would have gone; blue fails at 6.06 on
  the nav exactly as sitework recorded. **WET SLAB #8FECFF survived** — hue 190, the one open
  arc left (hvac mint 166 → electrical blue 200), separating by CHROMA rather than hue: nav
  **10.76:1**, accentInk **12.30:1**, white on accentDeep **5.84:1**, and dE **31.0 / 31.7 /
  32.9** to its three nearest neighbours against a rack whose tightest shipping pair is gc
  against concrete at **19.3**. The semantic is the trade's gate rather than decoration — this
  is the one trade on the rack whose day is decided by how wet the concrete is. **DELIBERATELY
  NOT SHIPPED, in the prune's own ranking so the next cycle does not read them as oversights:**
  `what-it-read` (the readings row log — the exhibit behind the pin, and the strongest unbuilt
  rung), `dealer-call` (a vocabulary build the size of the supply-house order, whose
  differentiator is the ORDER'S SECOND READING — everything that has to come off the same run,
  including the attic stock that is in the spec and never called in until the run is gone), and
  the write-up library, now owed on two trades. **GATES, all re-run green:** mobile-watertight
  **125 pages × 320/360/390/430 × default and bumped, 0 failing** (all 8 flooring pages
  individually too) · note-live-fields **334 fields / 27 pages** · getting-in **13/13 kits** ·
  no-third-party **125/125** · commons-names **374 checks** and commons-bag **472 states, 0
  failing** (was 470/1) · reconcile-join **110 checks** (was 99, of which the 5 that mattered
  were dead) · rowlog-restore 31/31 · rowlog-commit-merge · reconcile-surface · pickfilter ·
  menu-reachability · overlay-reachability · docspec 11 trades / 181 checks. **THEN THE JOB
  ITSELF, DRIVEN ON THE REAL PAGE AT 390px:** the letter filled the way a mechanic fills it —
  two conditions ticked, a reading row (location · method · his value, no threshold anywhere),
  his own limit typed off his pail, the impact line with a chip appended to his own sentence
  and the clock stamping `[ANSWER NEEDED TODAY]` — produced a 1,490-character document carrying
  every one of 14 required elements, and **asserted NOT to contain** pass, fail, safe to
  install, acceptable, in-spec, an RH percentage, lbs/1000sf or a flatness fraction. Zero page
  errors on all 8. Storefront entry made TRUE in persona500 `fieldToolkits.ts` — 13 toolkits
  now, accent `#8FECFF` identical to `trade.js`, 6 tools, and match tokens MEASURED against
  all 1,027 persona ids: bare `floor` hits `casino_floor_manager`, bare `hardwood` is
  basketball slang against a corpus carrying EIGHT basketball personas, and bare `tile` is a
  substring of textile — all three killed, `red_carpet` excluded ahead of the drift. P5 owns
  pushing that repo. **THE FIRST PUSH WAS REFUSED BY THE DEPLOY, AND THE REFUSAL IS THE
  OTHER HALF OF THIS ENTRY:** the trade cleared the three lists §TRADE EXPANSION names and
  failed on a FOURTH the book never mentioned — the site-root TOOLS registry in
  `HELIOS-BRIDGE/components/UIComponents.tsx`, without which a whole staged toolkit is linked
  from nothing at the root. **Second stand-up running whose story is a list the checklist
  omitted** (the first was the commons chip, scarred above), so §TRADE EXPANSION now names
  all four. Fixed, re-pushed, **deploy green**, and **LIVE-VERIFIED AT THE ARTIFACT**: all 11
  flooring URLs 200, the runtime and commons carrying the slug in the DEPLOYED bundles, the
  `data-f` fix and the four new VERDICTS greped out of the deployed `note.js` and
  `reconcile.js` rather than the source, then the letter driven end to end ON THE LIVE PAGE —
  14/14 elements present, 8/8 refusals absent, hub rendering all six tools with the pin first
  and the accent painted, zero page errors, and mobile-watertight re-run GREEN AGAINST
  PRODUCTION.
  https://mrdirno.github.io/nested-resonance-memory-archive/flooring/

- **[AXIS:WELL] C3628 (2026-08-17) — three wishes served at the root cause, and the WISH BOARD stands up.**
  Vibe well: GT "nothing happens" (0d71fdc9) root-caused to a `*/0` comment-terminator killing the
  whole wish IIFE — fixed; the silent `length<2` guard now SPEAKS on all 19 vibe-cards pages
  ("Escriba su deseo primero." / "Type your wish first."); stale "seven cards" (2a895681 + 598ae99c)
  fixed AND harnessed — counts sit in `data-count` spans a build gate re-derives from
  CARD_REGISTRY.md, and a second gate `node --check`s every inline script on every page so a dead
  handler can never deploy green again. All verified LIVE at 390px (handler alive, nudge visible,
  "nine" stated, no h-scroll), deploy green, wishes shipped with notes. BACKPORT RIDER FIRED both
  directions: vibe 19/19 pages patched; archive swept 125 pages / 117 inline blocks — clean (its
  toolkit.js already refuses visibly). OPERATOR DIRECTIVE (2026-08-17, mid-cycle): wish process
  standardized — new `/Volumes/dual/_vault/automation/scripts/wish_board.py` reads ALL THREE sinks
  (av_tool_requests + vibe_card_wishes + persona500 community_posts) oldest-first with ages and
  stale-claim flags, wired into the collage + persona500 directives and the wishitbetter
  {wish_queue} slot (live at next operator-app relaunch; render-proof green, template delta 0).
  First board read: 61 waiting, oldest 930h, 33 society wishes NO bump had ever seen — the rot the
  operator called, measured. persona500.com full-DD fleet (8 scouts) landed; revamp follows it.
  https://mrdirno.github.io/vibe-cards/gt/

- **[AXIS:WELL] C3629 (2026-08-18) — "Todo en Español para los Latinos": the toolkit's first bilingual tool.**
  Oldest wish across both wells (gc · improve · tm-tag.html) served end to end. EN/ES chips on the
  plate (first visit follows the phone's language, the pick is remembered), the whole UI en español
  de obra — vale, cuadrilla, MAYORDOMO for the foreman and never for the súper, tablaroca — and the
  assembled document BILINGUAL by design: the judge panel (3/3 BUILD-WITH-CHANGES — field lens ·
  receiver lens · strict skeptic) bound that a tag outlives its text thread (pay apps, CO backup,
  the AP clerk in March), so ES mode prints headings "ES / EN", picked options "ES (EN)", free text
  as typed, and EN mode's document is byte-identical to before. Vocabulary rides in gc/items.js
  `tag_es` with an en-twin on every entry (nothing paired by index); picks survive the flip both
  directions, remapped AT BOOT (see the new scar — the exit flush overwrote the first attempt).
  The note engine grew three additive, defaults-preserved params (copyFailLabel · rows rmLabel ·
  tick doc). Independent native-register review: 4 fixes, all applied ("Su PM"/"Su nombre" usted
  ambiguity, "verbal"-as-noun, "mano" calque). Gates: no-third-party PASS · note-live-fields 11/11
  on the page and 334 fields / 27 pages full sweep PASS (BACKPORT RIDER: the engine additions are
  proven no-ops for every sibling note page; no sibling carries a language layer yet — this is the
  FIRST instance) · mobile-watertight PASS 320/360/390/430 + bumped text · ES e2e ALL GREEN (locale
  default, bilingual doc, toggle round-trip, overflow at 4 widths, 44px chips, zero page errors).
  Stale-claim sweep: AV well 0 building; the 20 building in vibe-cards belong to a LIVE sibling
  lane (three commits the same evening) whose well is forward-only by design — nothing to release,
  and the board's "15 STALE" is that lane's WIP, recorded here so the flag has an answer on disk.
  ~~NEXT RUNG the wish itself names ("and other languages", five sibling tm-tags): the SECOND
  instance, where §THE THREE SHAPES says the language layer gets extracted into an engine.~~
  → **SHIPPED C3650 (2026-08-23):** the layer is `shared/lang.js` and every directed-work tag on
  all twelve trades speaks Spanish; gated by `tools/toolkit-gates/lang-layer.mjs`.
  https://mrdirno.github.io/nested-resonance-memory-archive/gc/tm-tag.html
- **[AXIS:WELL] C3630 (2026-08-18) — the stale claim WAS the oldest wish: the tap mark reaches
  the card faces.** The board flagged `e97de46a` (vibe-cards root, 2026-08-17: *"None of the
  cards here have the tap icon on the card face"*) sitting `building` >24h; the dead cycle's
  tap-mark commits touched Card Studio and the KELIBRO back design, never the surface the wish
  named, so finish-don't-release was the whole rung — and it was also the oldest wish on the
  board. PANEL 3/3 BUILD_WITH_CHANGES (7.5/7.5/7): honor the settled caption verdict (words on
  cards truncate — this is an icon, not a reopening), style it as chrome not ink, and audit the
  corner against every face. So the corner was MEASURED, not judged: the badge composited at
  worst case (320px viewport, 284px card) onto all 14 fronts — top-right clears all five hero
  faces but sits square on the QR finder pattern zaria prints there, so the wide deck anchors
  bottom-right (nearest call, aurea's spec lines, ends left of it). Build is pure CSS, zero
  markup: `.card::after` 30px plate + the printed decks' own contactless glyph as a data-URI
  SVG, `pointer-events:none` so the tap it advertises reaches the input, hidden while flipped
  via `:has()` (benign where unsupported), and the wide deck's pseudo is a frame at the faces'
  own declared 1100/694 because a figure's bottom belongs to the caption, not the face. Gate at
  320/360/390/430/1440, run LOCAL then LIVE post-deploy: no overflow at any width, badge
  geometry asserted, a click at the badge's own coordinate flips the card, badge hides while
  flipped. One scar filed (an animated property read the instant it changed — §SCARS
  2026-08-18). **BACKPORT rider FIRED, found the class nowhere else:** sub-pages' `figure.turn`
  is a drawing class, not the flip checkbox; gt's flip already carries "TAP TO FLIP"; all
  toolkit trades grepped — zero checkbox-flip cards anywhere. Shipped `037884c`, deploy green,
  wish `--ship`ed with the live URL; wisher anonymous, anonymity honored. Wells after this
  cycle: AV 2 new (both collage — oldest `02e8e493` aspect-lock toggle, then `9a1f6eb9` shuffle
  re-arrange + color match), vibe 2 new, 0 building anywhere — the stale-claim flag is clear.
  https://mrdirno.github.io/vibe-cards/

- `2026-08-19` — **[AXIS:INTERFACE] C3636 — THE BLOCK THAT SAT BESIDE THE BOXES IT WAS BUILT
  TO REPLACE, FOR FIVE DAYS, AND WHAT A DRIVER READS AT 5:50AM.** Wells read UNSCOPED first:
  AV 0 new / 0 building, vibe 0 / 0 (the 34 board items are all the society wall — P5's sink);
  no family owed; stalest axis INTERFACE (13 lane-cycles). The book's own ranked remainder —
  *"the single most concrete unbuilt thing on this whole file"* — was the order-page fulfilment
  axis, re-cut by the 2026-08-16 panel into a REPLACE. **before:** `shared/dropoff.js` v1 on
  ONE order page (plumbing, + sitework) while electrical/pull-list, low-voltage/consumables,
  framing/the-load and masonry/yard-call still printed a hand-rolled `fAccess` textarea +
  `fSigner` (+ `fMeet` on two) — a fork with a better header; the block's own document
  printed `When: morning, not before 07:00` under a gate placeholder that read "no trucks
  before 7" (two clocks for one fact); "Forklift on site / Boom or crane" offered to a box of
  J-hooks; no paperwork line at all, so a driver with the exact right code sat an hour for a
  COI; and `mobile-watertight` had never once sized the block (inside a closed drawer / behind
  a Delivery tap). **after:** **`dropoff.js` v2** — driver lines first (gate → *gate's wrong or
  nobody's there — call:* → *Before the gate:* → set it → who signs; off-the-truck and the
  window after) · the not-before control as the ONE clock, printed on the gate line, the
  placeholder no longer modelling a time · a multi-select PAPERWORK row whose every chip asks
  the supply house before it states anything (*"Tell me if our COI isn't on file with you
  yet"* · *"Tell me who's hauling — only approved carriers get in"* · sign-in · hard hat + vest
  · orientation; "tick any that apply" on the glass) · `load:"small"` — one CUSTODY axis
  (handed off · left at a drop point · with the super · security) in place of where-it-lands /
  how-it-lifts · `bare` + `seed` · the gate line a 2-row textarea. **THE REPLACE:** the four
  pages drop their boxes and mount the block per job behind the card — `shared/jobcard.js`
  grew `carry:` (kept, never painted) + `stash()`, the block seeds ONCE from the June answers
  and a seeded record persists even empty so a clear never resurrects them; shown off the
  page's own `fHow` (delivery → on; will-call / set-aside / restock → out of the document) or
  declared always-on where a truck is always coming (framing, masonry). **Six of eight order
  pages carry the block.** NOT taken, by decision: concrete/mix-order (ready-mix is chute /
  pump / washout — its own class) · hvac/truck-stock (a van is restocked at the shop, panel).
  THE PANEL (dispatcher 8 · two-class foreman 7 · skeptic 6 — 3/3 BUILD_WITH_CHANGES) and
  every BLOCKING demand landed before ship: "Left at a drop point" (the first wording
  contradicted the signer box in the same message) · the textarea · ask-first COI · "Before
  the gate", not "opens" · the two lead-time asks adjacent · paperwork printed right under
  the call line (two of three moved it up) · the fifth custody chip that replaced no typing
  cut · a HANDBACK assertion in the gate. The weight band stays OUT — operator's call. Gates,
  all green: `dropoff-block` 6 pages (order · one clock · ask-first · multi row · seed in BOTH
  storage shapes · cleared-stays-cleared; **4 injected mutants killed** — status-first COI,
  a clock on `When:`, a pick-one multi row, a seed that re-applies) · `jobcard-scope` 7 ·
  `order-live-header` 9 · `mobile-watertight` on all six pages at 320/360/390/430 × default
  and bumped, WITH a new revealed state (drawer open, block on, a multi chip lit — proved by
  an injected 600px chip failing at 320) · `no-third-party` 125 pages, 0 requests · eyes on the real page at
  390 on electrical, low-voltage and masonry (two 4-line labels trimmed from what the
  screenshot showed). **LIVE-VERIFIED against the deployed site:** all six files byte-
  identical to HEAD, `dropoff-block.mjs https://…` 6/6 incl. the seed, `mobile-watertight`
  LIVE 4/4, a yard call driven at 390 end to end, 0 page errors. Storefront: four notes in
  `persona500/src/data/fieldToolkits.ts` now name the block (P5 pushes). Roster rung struck
  with what was learned (not an engine rung; the placeholder was half the finding; the
  paperwork line belongs with the gate). **BACKPORT RIDER FIRED** — the sweep IS the ship:
  four siblings taken, two named not-taken. Five scars (§SCARS 2026-08-19).
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/pull-list.html

- `2026-08-22` — **[AXIS:DOCS]** **THE LAST TRADE IN THE BUILDING GOT THE WRITING IT DOES
  MOST** · **before:** flooring shipped as trade #13 with six tools and no write-up page; the
  DOCS axis had skipped it and sitework both, and flooring's own `tools.js` prune named the
  debt ("owed on two trades"). Two trades of thirteen carried no `docs.js` at all, so the DOCS
  capability — the axis the operator named by hand — was missing from the trade whose week is
  writing letters about a slab that isn't ready. · **after:** `flooring/docs.js` +
  `flooring/write-up.html` + one registry line (6→7 tools), **15 documents live.** FOUR are
  trade-specific, each a panel proposal the prune had moved off the hub INTO the library
  because a second docspec engine on one rack is the duplication the prune exists to catch:
  *What My Number Doesn't Cover* (the exclusions, and the ASSUMPTIONS everyone drops — the omit
  line), *The Prep Write-Up* (the PCO backup, written before the grind erases the evidence),
  the **shading call that routes the appearance determination TO the mill instead of making
  it**, and *You Told Me To Put It In Anyway* (the dated record of the directed override). All
  eleven shared documents kept — `drop:[]`, like every construction sibling, verified against
  disk (only non-construction creative ever dropped one) — and re-addressed to a floor.
  **NOTHING GRADES A FLOOR:** the reading prints beside the limit off his own bucket and the
  block never says which one wins — no moisture value, no flatness tolerance, no acclimation
  window, no pass/fail, no defect ruling. A **4-lens adversarial panel** ran against the actual
  emitted blocks and its **safety-leak lens came back EMPTY. IT CAUGHT TWO REAL DEFECTS,** both
  fixed and re-verified against the live blocks (§SCARS 2026-08-22): `directed-to-proceed` was
  a second front door onto the pinned `give-me-the-go.html` tool and now carries the steering
  note the kit's own convention requires; the `handover` override was inheriting the shared
  "keys, codes, manuals" facts and now declares flooring-native ones (attic stock, care info).
  **BACKPORT RIDER FIRED — the class was a US-dialect break in EMITTED text.** The engine
  itself shipped "authorised" and "characterisation" in the EXTRA WORK and incident spines of
  every block on all 13 trades, so fixing only flooring's reminder would have SPLIT flooring's
  own block. Swept `shared/docspec.js` (→ authorized / authorization / characterization /
  characterize) plus the trade-local instances in roofing, framing, av (`behaviour`→behavior)
  and masonry (one `colour` reminder-word); the intentional `colour -> color` dictation vocab
  pairs were left untouched — flipping them is the identity-pair defect the voice lens exists
  to catch. Gates, all re-run GREEN AGAINST PRODUCTION: **docspec-config 13 trades / 209 checks
  / 0 failing** (16/0 against the live site, flooring 15 docs) · **docspec-desk holds** (the
  engine edit goldened byte-for-byte in-run) · **mobile-watertight `flooring/write-up.html`
  LIVE at 320/360/390/430 × default and bumped** · no external refs · the live page driven end
  to end, each document picked and emitted (`directed-to-proceed` 12,484 chars). Storefront:
  entry made true in `persona500/src/data/fieldToolkits.ts` (P5 pushes that repo). **Sitework,
  the other owed trade, is a concurrent PEER session's this cycle — the split coordinated by
  message, no collision.**
  https://mrdirno.github.io/nested-resonance-memory-archive/flooring/write-up.html

- `2026-08-23` — **[AXIS:DOCS] C3643 — THE THIRTEENTH LIBRARY HAD BEEN FINISHED FOR ELEVEN
  HOURS AND WAS 404** · **before:** the well was dry (0 new, 0 building, both wells) and no
  family was owed, so the stalest axis governed. Step 0 of the ship loop found something else
  first: `sitework/docs.js` + `sitework/write-up.html` sat UNCOMMITTED on disk from a peer
  session that died at 13:07, and that session had already written *"SHIPPED 2026-08-22 … it
  closed the DOCS axis: thirteen trades, thirteen libraries, none left owed"* into
  `sitework/tools.js`. The previous cycle's own log entry says the same. **The live URL was
  404**, and the bump's LIVE STATE line — which counts `tools.js` off disk — read **98 tools
  while the artifact served 97** (§SCARS) · **after:** verified, gated and shipped: **15
  documents, 4 written for this trade** — what was in the ditch when it closed, what was found
  that is not on the plan, a line got hit, and the haul count in the unit it was counted in.
  Not re-derived work; the peer's build, read, driven and proved before it was trusted.
  **BACKPORT RIDER FIRED on the real class, which is not "docs" — it is a registry line making
  a claim about an artifact nobody checked.** New sweep, derived from disk: every trade's
  `tools.js`, every `href`, curled against the live site — **13 trades, 98 registry pages, 1
  unreachable, and it was this one.** Re-run after the deploy: **98/98**. (One 503 mid-sweep was
  GitHub Pages rate-limiting us, re-checked 3× at 200 — a transient is not a finding.) Gates,
  all re-run GREEN AGAINST PRODUCTION: **docspec 1 trade / 16 checks / 0 failing** on the live
  site, 13 trades / 213 checks locally · **mobile-watertight `sitework/write-up.html` live at
  320/360/390/430 × default and bumped** · **no-third-party 127/127** · the live page driven end
  to end at 390px as a foreman — searched *"a line got hit"*, picked it, copied **15,428 chars**,
  the clock-minute-by-minute omit line present, zero page errors, zero overflow. Storefront:
  entry made true in `persona500/src/data/fieldToolkits.ts` — sitework `tools[]` now 8, rack 98
  (P5 pushes that repo).
  https://mrdirno.github.io/nested-resonance-memory-archive/sitework/write-up.html

- `2026-08-23` — **[AXIS:COMMONS] C3643 — EIGHT DOCUMENTS LIVE ON ALL THIRTEEN TRADES AND EVERY
  TRADE RENAMED THEM** · **before:** COMMONS was the stalest axis (14 lane-cycles) and its next
  rung was already named on disk: *"`shared/docspec.js` is trade-siloed, so a man who knows
  'punch list reply' from framing gets nothing on any other trade's write-up."* **That prediction
  was wrong and the measurement is the finding** (§SCARS): driven through the real search box,
  733 unambiguous terms × 13 trades = **9,529 searches, ZERO dead ends** — `find.js` never
  returns nothing. The failure is the opposite: **1,083 searches returned a DIFFERENT document
  for one the reader's own library was holding**, and **512 of those carried no hedge at all**.
  On the AV page, *"somebody got hurt"* → **Damage / Pre-Existing Condition Note**, presented as
  an exact match. *"first aid"* → Turnover / Handover Summary. *"recordable"* → Daily Field
  Report. The cause is structural: `delay-notice` goes by **7 different names** across the rack,
  `daily-report` 6, `damage-found` 6, `handover` 6, `site-walk` 5 — and each trade's author wrote
  his own `aka`, so every page knew **one man's words for a document thirteen men named** ·
  **after:** `shared/docsindex.js`, the union of every name and `aka` anybody wrote, GENERATED
  from the thirteen libraries and added to the search index of every trade that **already
  carries that document id**. Live, on the real site: *"somebody got hurt"* → **Incident /
  Near-Miss Report**, *"first aid"* → Incident / Near-Miss Report, *"recordable"* → Incident /
  Near-Miss Report, *"we got held"* → Delay / We're Held Up Notice, each under a new heading —
  **"Another trade's name for it"**, the commons name table's own *WHO SAYS IT* rule one floor
  up, so a word that WORKS is never mistaken for the word to write down. Re-measured through the
  same 9,529: **his own document found 2,802 → 3,849; wrong 1,083 → 36; the unhedged half 512 →
  23.**
  **THE PANEL KILLED THE OTHER HALF 3–0, AND IT WAS THE HALF WITH THE BIGGER NUMBER.** A
  cross-trade HAND-OFF — route a man to the trade that owns the document he named — targeted
  5,644 misses and scored **5 / 1 / 2**. The field lens: *"it takes me off my page… what am I
  actually handed when I get there?"* The mechanism answers him and is why this is a refusal and
  not a deferral: **every block introduces the reader in the OWNING trade's words** — sitework's
  A Line Got Hit opens *"I am the foreman who was on the machine or in the hole; we do sitework
  and underground utility work."* Today he gets a wrong document in his own voice and rejects it
  in two seconds; routed, he gets a plausible document in the **wrong voice, that he asked for
  by name**. The safety lens named the residue nobody can mechanise: whether **this** man may
  author **this** document depends on his licence and his subcontract, and a client-side static
  page will never hold either. And the refute lens showed the routing row would sit **above** a
  correct local hit on exactly the 268 ambiguous terms. **Pooling survives precisely because it
  cannot cross that line:** a term is only added to trades that already hold its document, so the
  **57 single-trade documents can never push a word anywhere** and the entitlement question is
  already settled by the document being on his page.
  **THE COST, MEASURED AND NOT SMOOTHED AWAY:** cross-trade wrong answers presented as exact went
  **2,848 → 3,138 (+290)** — a wider index reaches full token coverage on more of the documents
  he does not carry. The refute lens predicted that direction and was right; the trade is 1,083
  of his own down to 36 against 290 more mislabelled among documents that were already wrong.
  **FOUR RAILS, ALL MECHANISMS:** (R1) a term is pooled only if it means ONE document across the
  whole rack, folded through **the engine's own normalizer** — 34 refused; (R2) a **near-name
  quarantine** drops any term within one edit of a term meaning a different document — 10 caught,
  and they are real: **"not us" / "notes"**, **"what we said" / "what we laid"**, **"blocked" /
  "locked"**, **"flash" / "clash"**. That rail costs honestly — *"what we said"* is one of the 36
  still missing, and it stays missing; (R3) two or more trades must carry a document before any
  word pools onto it; (R4) **the deploy regenerates the file from the staged libraries and
  refuses a diff**, so the header's claim cannot rot. To make R4 possible without a browser in
  CI, `shared/docspec.js` now **exports its verify surface BEFORE the mount and returns early
  with no `document`** — the merge rule is read, never re-implemented.
  **THE BLOCK IS UNTOUCHED, AND THAT IS ASSERTED, NOT ASSUMED:** `aka` also feeds the ROUTER line
  a man pastes into his AI, so `pooled()` returns COPIES and `byId()` keeps reading the real
  library — **docspec-desk holds byte-for-byte** and the live drive confirms no pooled word
  reaches the block. **GATE: `tools/toolkit-gates/docs-pool.mjs` is new — 13 trades, 80 checks,
  and PROVED RED BY FIVE MUTATIONS** before it was trusted (drop the `<script>` from one page ·
  let `pooled()` mutate instead of copy · smuggle a single-trade document into the pool ·
  un-quarantine `"notes"` · delete the heading). The deploy's two new asserts were each proved by
  NEGATIVE CONTROL, including the `commons/tips.html` scar's own shape: with the tag replaced by
  a comment mentioning the filename, **a plain grep still passes and the strip-then-grep fails.**
  All green against production: **docs-pool 80/80 LIVE** · docspec **213/0** · **desk gate holds**
  · mobile-watertight **13/13 write-up pages** at 320/360/390/430 default and bumped ·
  no-third-party **127/127** · menu-reachability **868 checks / 124 pages**. Storefront unchanged
  — no new tool, no new trade. **NAMED NEXT RUNG, with its mechanism:** `find.js` sets
  `mode = "exact"` when every LIVE query token was covered, **not when the match was strong** —
  so a query matching only the `why` prose at weight 2 is handed over unhedged. That is the
  single cause of all 3,161 remaining unhedged wrong answers, it lives in the engine all 16
  search surfaces share, and it is worth its own cycle.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html
- `2026-08-22` — **[AXIS:DEPTH] C3644 — THE READING THAT OUTLIVES THE SLAB.**
  `flooring/what-it-read.html` shipped — the moisture-reading log, a config on shape #3
  (`shared/rowlog.js`), no new engine. Flooring **7 tools → 8**. A floor hand tests the
  slab, writes the numbers on a scrap of drywall, the scrap goes in the dumpster — and once
  the adhesive is down that slab can never be tested again, so ninety days later this log is
  the only artefact left: the exhibit behind the pinned `give-me-the-go` letter, which
  carries the readings for ONE morning while this carries them for a month. Per row: Where
  (self-building) · What it read · Limit off the pail (sticky) · How/meter (sticky) · What
  it's for (sticky) · Note; grouped by area with a count per area; TSV round-trip verified
  **byte-identical** (rowlog-restore). THE REFUSAL, the longest in the kit and lifted
  straight from `flooring/trade.js`'s charter: the reading is HIS number, the limit is what
  HE read off HIS pail, the page prints them side by side and **does no math** — proven on a
  real over-limit case, `read 82% RH — limit 75% RH`, where the page says nothing. No
  threshold, no tolerance, no acclimation window, no pass/fail/ready/high/low in any wording.
  THE ONE STATE IS A FACT, NOT A VERDICT: the tap ladder has a single rung, **Covered** (the
  floor's down, the slab is sealed), because the engine ALWAYS renders the tap+chip and a
  truly status-less config ships a dead tap — **the next readings-log builder (roofing
  `what-we-found`, masonry `before-we-grout`) should adopt a factual rung, never omit
  status.** Chosen by ROTATION, not taste: 5+ straight DOCS cycles tripped the K≥4
  stalled-route rule, so the lane rotated to the stalest axis (DEPTH, cold 15 cycles) instead
  of the `find.js` next-rung C3643 named. **BACKPORT RIDER: swept — no sibling bug-class to
  carry** (a new DEPTH tool, not a fix); the reusable mechanisms (sticky meter/material,
  reading-beside-limit, factual-not-verdict rung) are named here for the next row-log to
  steal rather than re-derive. Gates green: mobile-watertight 4 widths default+bumped ·
  no-third-party · rowlog-restore · rowlog-commit-merge · menu-reachability sweep · hub card
  + nav link live. https://mrdirno.github.io/nested-resonance-memory-archive/flooring/what-it-read.html
- `2026-08-23` — **[AXIS:DEPTH] Order The Load** shipped (`roofing/order-the-load.html`, + the
  `load` block in `roofing/items.js`, + `roofing/tools.js`) — roofing's FIRST engine-A material
  order and the TENTH instance of checklist→request: the every-job first tool that plumbing,
  masonry, concrete, electrical, HVAC and AV all had and roofing lacked. Field by the square,
  membrane by the roll, edge metal by the stick; the unit welded to a bare number; the
  colour/lot MATCH (the roofing twin of the mason's run — a re-supply off a different lot
  stripes a finished slope); rooftop-vs-ground landing; the dry-in questions (field with no
  underlayment / starter / cap / edge, membrane with nothing to fasten or bond) on the GLASS,
  never in the sent order. Cast a 3-lens adversarial panel (safety / field-voice /
  document-logic) BEFORE ship — it killed a coverage figure ("3 bundles to the square") and a
  stock length ("10 ft most yards") that broke roofing's zero-spec edge, a brand-adjacent
  placeholder ("Weathered Wood" → generic), a silent wrong-unit guess on three "SAY WHICH"
  lines (dropped the default unit, matching the Tile line that was already right), and a
  stale-dry-in-pairs-after-Clear bug; all fixed, e2e re-verified 14/14. **BACKPORT RIDER
  fired: swept every trade — flooring is the one remaining material trade with no engine-A
  order (`give-me-the-go` / `what-it-read` are not it); named as the next DEPTH rung. No
  bug-class to carry (new tool).** Gates: mobile-watertight 4 widths default+bumped (caught a
  real bar-growth, see the 08-23 scar) · no-third-party · pickfilter (61 items / 10 sections) ·
  order-live-header · jobcard-scope · dropoff-block · headless e2e 14/14.
  https://mrdirno.github.io/nested-resonance-memory-archive/roofing/order-the-load.html
- **[AXIS:WELL] C3649 (2026-08-23) — the LEVIATHAN card carries card 010's address into the
  endless scroll.** Wish `e6f1af4d` (vibe-cards well, anonymous, cast from the deck's LEVIATHAN
  panel 24 min before RING 3 removed it): *"Needs a link to the endless scroll"*. 3-lens panel
  BUILD-WITH-CHANGES ×3 (8/6/3); shipped the unanimous core, cut the split JS doorway (§SCARS).
  **before:** the deck's rules-at-home LEVIATHAN card linked plain `persona500.com/leviathan` and
  dropped all six numbers; it was the one home card of three with no address grammar;
  `../leviathan/`'s "Fine-tune on the parametric deck" pointed at `#panel-fo`, an anchor deleted the
  same day, and the artifact gate cannot see a fragment. **after:** grammar line
  `fo|seed=N|h=N|n=N|crop=<name or 0-3>|vein=<name or 0-8>|cell=N` (both printed populations,
  never normalised — the panel's one hard rule); first link = card 010's printed address on the
  scroll, where the live engine grows that organism as band 0 in 3–4 s with no bad-address toast
  (asserted in a real browser, screenshot in the cycle scratch); card page button = the sibling pair
  `#rules-at-home` / "It is on the deck, and runs at home"; the well's page_url drops the page's own
  fragment before stamping (a `#panel-gesica` arrival used to file two hashes); credit on the card,
  no name because none was given. **BACKPORT RIDER FIRED:** swept every cross-page fragment on the
  site for the class — 5 links, 1 dead (the one fixed) — and wrote `tools/verify_fragments.mjs` into
  the Pages workflow so the class cannot pass green again; its first run PASSED the dead link (the
  deck's RING 2 comment says `id="panel-fo"` in prose) and reads markup only now — E1 caught it
  (§SCARS). Gates: fragments 62/62 · artifact gate complete (site + studio) · mobile gate watertight ·
  deck card at 320/360/390/430 default + bumped text, card-page button followed for real, live engine
  landing — 73/73 on the built site and 73/73 LIVE. Deploy run 32669527042 green; vibe-cards
  `4bcb378`. Named for P5 (persona500 repo, not pushed from here): the engine pages' modal button
  "Fine-tune on the parametric deck" (`cDeck` / `pDeck`) now opens a deck with no LEVIATHAN sliders —
  relabel to the sibling pair and point at `#rules-at-home`; and wishes `85542441` / `f94c82f2` /
  `a55f1234` ("doesn't open in Card Studio") sit inside P5's active handoff work (`45bcc6fc` +
  `ca2e03d`, both today) — serve or fold them there, not here. Not built, trigger named: the deck
  reading its own fragment (a live panel's `#gesica|…` setting its sliders) the day a deck URL with
  an address shows up in a wish or a referrer. https://mrdirno.github.io/vibe-cards/deck/#rules-at-home

- **[AXIS:BACKPORT] C3650 (2026-08-23) — THE TOOLKIT'S ONLY BILINGUAL TOOL WAS ONE PAGE OF ONE
  TRADE; THE LANGUAGE LAYER IS AN ENGINE NOW AND THE TAG SPEAKS SPANISH ON ALL TWELVE.**
  Wells: AV 0 new / 0 building; vibe-cards 3 building + 10 new — all thirteen are the operator's
  live feedback to the standalone orchestrator (PID 16035, its log written the second I read it)
  holding those claims on a dirty `vibe-cards` tree and staged `persona500` changes: nothing
  claimed, nothing released, recorded so the board's flag has an answer on disk. No family owed
  → stalest axis (BACKPORT, 17 cycles). **Before:** `gc/tm-tag.html` carried EN/ES inline
  (C3629) — 1 of 100 tools; the other eleven directed-work tags were English only. **After:**
  `shared/lang.js` (phone-follow default · one `toolkit.lang` key across trades, so a pick on the
  plumbing tag lands the roofing tag en español · `t()` · "ES (EN)" option composition ·
  boot-side draft remap PER KEY · toggle-by-reload · chrome swap), gc refactored onto it with its
  EN document byte-identical, and eleven siblings wired mechanically — every literal →
  `t(EN, ES)` with the EN half the ORIGINAL source literal; docName/docHead/docLabel compose
  "ES / EN"; closing and count bilingual; the engine defaults the pages leaned on (clock
  ph/nowLabel, rows rmLabel, copyFailLabel) named so ES carries them — plus `tag_es` twins in
  eleven `items.js` (30–45 entries per trade). **THE PANEL PROPOSED, AND IT DISPOSED:** per trade
  a bilingual foreman persona translated (11 agents), then two independent judges (native
  register · trade vocabulary) returned fixes — 85 applied, 0 unmatched, 21 conflicts resolved
  by rule (trade wins vocabulary, register wins prose). Eleven hub cards now say "En español
  también." **GATED, AND THE GATE IS PERMANENT:** `tools/toolkit-gates/lang-layer.mjs` — EN
  document identical to `git HEAD` under a frozen clock · an es-* phone opens en español and an
  en-* phone does not move · ES document bilingual on the name, every head and the last option
  of every vocabulary · the flip round-trips the draft EN→ES→EN through the twins · twins
  complete and verbatim · no overflow in Spanish at 320/360/390/430 · chips ≥ 44px · zero page
  errors — **PASS 12/12**; `note-live-fields` **334 fields / 27 pages PASS**; `mobile-watertight`
  **PASS on all 12**; `no-third-party` **129 pages, 0 requests**. **BACKPORT RIDER FIRED, TWICE:**
  (1) the trade judge translating sitework's examples found they were MASONRY's — four
  placeholders cloned with the page and never made sitework's; a sweep of long placeholders
  shared by two trades found exactly those four; fixed in both tongues (§SCARS). (2) The bar's
  count label is geometry, not language: 94px at 390 (80 on electrical), the panel's
  "1 hombre en el vale" needs 147px and gc's own "1 línea de cuadrilla en el vale" 239px —
  truncated since the day it shipped, invisible to every gate; all twelve now carry ≤ 12-char
  bar strings ("{n} hombres" · "Empezado" · "Nada aún") and read whole at 390 and 430 (§SCARS).
  **NAMED REMAINDER, MEASURED:** the ENGLISH empty label "Nothing on it yet" needs 131px in that
  119px box (97 on electrical) on a fresh note page at 390 — it has always read "NOTHING ON IT
  Y…"; a program-wide ≤ 11-char label across the 27 note pages is the next BACKPORT rung. CUT:
  `creative/thats-another-round` (a client-facing revision note, not jobsite Spanish — its own
  register, its own panel). Storefront: no new tool or trade; the fieldToolkits.ts tag entries
  stay true. Proof (tap ES on any of the twelve):
  https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/tm-tag.html ·
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/tm-tag.html ·
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/tm-ticket.html

- **[AXIS:BREADTH] C3653 (2026-08-24) — THE FOURTEENTH TRADE WAS FOUND BY THE QUESTION, NOT THE
  COUNT.** Flooring's own #14 instruction ran first: *whose gate is already written into other
  kits' vocabulary with no receiver behind it* — and "Before paint" is a literal gate VALUE in
  av's ladder, "Before it goes to paint" in framing's, with paint words in TEN of thirteen kits.
  The who[] count nominated doors (3+hm to the painter's 2); a four-lens Workflow panel
  (receiving · population · refusal · system-of-record, independent, scored) disposed UNANIMOUS
  for painting, 86–90 against doors' 67–76 — doors held as #15 front-runner in the private
  ladder, its #13 kill intact. Three blind in-trade voices (28 proposals) + an independent
  14-item refusal pass + the 20-year prune kept SEVEN and stand-up shipped SIX:
  `not-ready` (PINNED — the receiver behind ten countdowns; commencement is acceptance; the
  two-button close: FIX with a when, or PROCEED in writing) · `store-call` (unit-of-issue on the
  bare number, the batch as masonry's RUN with header passthrough AND the inverse case, sitework's
  buried list isomorphed to THE SHAKER LIST, ends-on-absence on the glass) · `coat-count`
  (flooring's factual-rung law — the one rung is RECOATED, and the visible-film filter IS the
  touch-up map: batch-per-area outlives the empties) · `ding-ledger` (observed-never-accused
  who-column with Unknown first-class; per-trade tallies feed the PM's back-charge as counts;
  the fix call is Touch-up vs Whole-wall-it'll-flash, craft not fault) · `color-lock` (answers
  THEIR numbered schedule, never re-authors it; CONFIRMED-or-keep-working, with the ASI absence
  question) · `write-up.html` + `docs.js` AT STAND-UP — fourteenth trade, fourteenth library,
  the DOCS axis never re-opened; own docs `coated-under-protest` / `walk-after-final` /
  `who-picked-the-color`. The prune's seventh (`wet-area-notice`, with Spray Notice and the
  Recoat Clock folded in) is the NAMED unbuilt rung in `painting/tools.js`, and the kit's ES debt
  is named there too. Accent MEASURED, not picked: #29FF29 — the tape line — nav 10.64:1 (bar 7),
  CIELAB dE 34.6 to its nearest neighbour, 1.8× the tightest shipped pair; lemon-white,
  magenta-white and blue killed with numbers in trade.js. Commons MEMBERSHIP same cycle: 12 gear
  + 12 tips + 10 names rows (three-agent fan-out, curated), chip live; all four CI lists joined;
  storefront `fieldToolkits.ts` entry TRUE with corpus-measured match tokens (all precision-1 by
  vacancy against 1,027 personas). **before:** 13 trades, the last trade through every room
  unaddressed by name in ten kits. **after:** 14 trades / 106 registered tools, every gate green
  — docspec 14 trades/228 checks · docs-pool 86 · commons 506 states · rowlogs 34/34 · menu 137
  pages · notes 364 fields · desk 14 · LIVE mobile sweep 8/8 pages at 320/360/390/430
  default+bumped, run twice (first live pass dropped two pages to CDN propagation; re-swept
  stable green). **BACKPORT RIDER FIRED as a sweep:** the required+sticky+chips class (§SCARS)
  searched across all thirteen siblings — zero instances; and C3650's named remainder was NOT
  re-shipped — the two new note pages carry "Nothing yet"/"Started"/short counts, while the 27
  legacy note pages still owe the program-wide ≤11-char label backport (unchanged, still the
  next BACKPORT rung). Deploy 32756016574 green + label follow-up. Named for P5: push the
  persona500 repo — `fieldToolkits.ts` now carries the painting entry (accent #29FF29, live:
  true, added 2026-08-24). https://mrdirno.github.io/nested-resonance-memory-archive/painting/

- **[AXIS:INTERFACE] C3654 (2026-08-24) — THE FOURTEENTH TRADE JOINS THE BOUNDARY IT WAS BUILT
  TO SERVE, AND THE SWEEP FINDS THE DONOR'S NAME IN EVERY LINE THE RUNTIME NEVER TOUCHES.**
  Wells read UNSCOPED first: AV 0 new / 0 building, vibe 0 / 0 (the 31 board items are all the
  society wall — P5's sink); no family owed; stalest axis INTERFACE. The roster's next rung is
  the forward leg — but step 0 found the sharper hole ON DISK: painting stood up at C3653 with
  none of the three boundary pages, unnamed — the only construction kit that could not send an
  ask, answer a list, or ask a building for a night, while ten kits write "before paint" into
  the very ladders it should stand behind. **before:** 14 trades / 106 tools, boundary on 13.
  **after:** 14 of 14 on the boundary, 109 tools. THE PANEL (repaint lens · new-construction
  lens · receiving desk → skeptic-disposer, 16 kills on the record): `rough-in-request.html`
  **Before Paint** — 11 asks × 3-5 specs, an 8-rung ladder that STARTS AT THE SHAKER because
  tint only turns one direction, and a lede that says the doorway refusal stays Not Ready's job;
  `answer-back.html` **Walk Back** — answers[] = We'll hit it · Done already · Not paint · Need
  the room, [2] and [3] split because they route differently on the receiving desk, and marks
  after final point at the ding ledger's dates; `getting-in.html` — the smell and spray-fog
  handbacks ("the panel on test, a head bagged and unbagged are your building's moves, not
  ours. Tell me who makes them"). **BACKPORT RIDER FIRED, AND IT WAS THE BIGGER FIND — the
  page-copy class, swept across all 14 kits:** sitework's rough-in wore MASONRY's `<title>`
  over CONCRETE's apple-title against its own config saying "Before We Dig"; sitework's answer
  page wore masonry's title too; THREE trades' home-screen names said concrete's "What I'll
  Set"; flooring's getting-in description was concrete's truck-and-pump under a page about
  twelve-foot rolls; and **flooring's Punch Back had promised four rungs its buttons never
  shipped for eleven days** — `answers[]` had exactly one taker (creative) since it was built,
  flooring's lede, registry desc, storefront note and items.js design comment all promised
  "not mine · damage needs a ticket" over default Will-do/Can't buttons, and reconcile's
  VERDICTS never knew the words, so such an answer pasted back read as "didn't say yes or no".
  All fixed in the same cycle; the ruling kept "Will do" verbatim at [0] so the engine's own
  no-date nag stays true. **TWO NEW GATES, EACH PROVED RED ON A SHIPPED DEFECT BEFORE BEING
  TRUSTED:** `boundary-titles.mjs` (41 pages — the tab says what the trade's own config says;
  red on sitework's real title, green after) · `answer-tapnote.mjs` (14 pages — the baked tap
  instructions say the words answers[] ships; red on the injected default note). And two
  existing gates earned their keep by refusing the first draft: `reconcile-join` rejected all
  six unclassified rungs (VERDICTS now carries them), `getting-in.mjs` demanded the
  grant-window ask painting's closing had dropped. GATES GREEN: getting-in 14/14 ·
  answer-tapnote 14 · boundary-titles 41 · reconcile-join 120 · reconcile-surface ·
  note-live-fields 376 fields/30 pages · menu-reachability 140 PASS · rowlog-restore 36/36 ·
  rowlog-commit-merge · no-third-party 140/0 · mobile-watertight on all 4 changed pages at
  320/360/390/430 × default+bumped locally AND the three new pages against the LIVE url.
  **LIVE-VERIFIED, deploy 32782876603 green:** 14 files byte-identical to HEAD, then Walk Back
  driven end to end on the real site at phone width — pasted the example walk, 8 lines lined
  up with the header skipped, all four rungs tapped (the list re-groups by status, which is
  why index-chasing fails and the job works), the promise dated through its chip + SAVE, the
  no-day nag appeared in painting's own words and CLEARED the moment the day landed, and the
  copied document carried the subject, the counts, both verbatim test lines, the date and the
  ding-ledger closing. §TRADE EXPANSION now names boundary membership (a deferral must be
  WRITTEN); §SCARS ×3. Storefront: painting 6→9 tools in `fieldToolkits.ts`, flooring's note
  now says the buttons' words — P5 pushes that repo. Roster: rung recorded with what was
  learned, painter edges + the PAINT gate ladder join the matrix; **the next INTERFACE rung
  stays the forward leg** (nothing reads an access ask back the way answer-back reads a
  rough-in ask), the owner's vendors behind it.
  https://mrdirno.github.io/nested-resonance-memory-archive/painting/rough-in-request.html

- **[AXIS:WELL] C3655 (2026-08-24) — THE LEAN-IN: pangea's zoom now resolves instead of
  stretching (wish c7e469a2, PANGEA-012, served 2h old).** The wisher asked for the nested
  thing by name — stems opening into twigs, smaller leaves, grass and water, "a programmatic
  way to do this elegantly." The elegance was already in the house: pangea's painter is
  resolution-independent by contract ("same seed, same plate, at any resolution") and every
  detail gate was px-relative from birth — hpx<30 blob→grown ontogeny, r1<1.3 stroke→modelled
  cylinder, lod>1 bark fracture glaze, ss<1.2 rect→stamped dab — so the WHOLE feature is a
  window (plan.view) handed to the existing painter: when a zoom gesture settles, the visible
  crop repaints on an overlay OUTSIDE the transformed stage at virtual W·k×H·k, base transform
  carrying the crop. Judge panel 9/8/8 build; their required changes all landed (bake cap
  2.25×/3.25× under the 4× pinch, sprite caps 6.5/12MP + 4090px sides against iOS canvas
  walls, two-way export exclusion, lod fenced to the leaned path, ~280ms crossfade).
  Determinism was the real craft: a THROWAWAY live score keeps the tuft stream's spend
  identical (live:null shears the foreground — §SCARS), blades + flock painted still from the
  score, years stays keyed to virtual H so no grown silhouette snaps, culled reflections still
  spend refCount so the cast never renumbers, weave+grain paint in VIEW space (surface tooth,
  not scene), paintRock's absolute setTransform became reset-to-base. PROOF, live at
  https://persona500.com/pangea#pg|world=88091 (deploy_commit c9c1879): e2e 10/10 on prod —
  crop-vs-view correlation 0.995, Laplacian variance 206.8 vs 76.6 (2.7× the fine detail of
  the stretched view), gesture hides instantly, dblclick returns, zero pageerrors; mobile
  sweep 12/12 at 320/360/390/430 incl. touch pinch-to-bake; pangea killtest 41/41 after the
  inherited red was dated and fixed (§SCARS); #chips wraps under 380px (leftmost buttons hung
  off the left edge at 320/360 — pre-existing, fixed same cycle). BACKPORT rider: FIRED —
  swept every sibling for zoom-without-resolve; class absent (bifurcata's own page already
  descends without limit per its v12, leviathan/gesica/9am have no zoom eye at all), so
  leviathan's eye+lean is a named DEPTH rung, not a broken sibling. Storefront: n/a — cards
  lane, no fieldToolkits entry. Wells after: AV 0/0, vibe 0/0. Next rungs named in the ship
  note: per-branch stream re-growth to lift the 4× cap (bifurcata-style endless descent),
  leaned fine-blades forked per clump, a zoom gate on the tap-modal.

- **[AXIS:WELL] C3656 (2026-08-25) — THE CARD STUDIO DOOR STOPPED FAILING IN SILENCE
  (wishes 64327a10 + 12183f06, both served, 12h old).** Two wishes three minutes apart from
  one thumb: "this one didn't go to card studio but others did", and "it didn't take at
  first, then I exited, clicked it again and it took — production grade fix so it will take
  any time, same for other generators." One root cause, and it was in the SENDER, not the
  studio the wishes named. "Open in Card Studio" on bifurcata/leviathan/pangea was one
  compound guard — `if (cell && !busy && !batch) { var w = window.open(...); if (w) {...} }`
  — whose own comment named the fall-through as "the fallback". But the anchor it falls
  through to carries `rel="noopener"`: that tab has no `window.opener`, so the sender can
  never postMessage into it. The fallback was a tab structurally incapable of the door's only
  job, and because the handler never reached `preventDefault` it was also mute. THREE legs
  land there; the everyday one is the SECOND TAP, because the door closes the modal the
  instant it is tapped — come back for another world, tap again while the first cut still
  holds `busySave`, get a second blank tab. Now every branch either hands the picture over or
  speaks: a cut in flight → "one moment, then tap Open in Card Studio again" with the modal
  LEFT OPEN so the retry is one tap; pop-up blocked → both recoveries named instead of a dead
  tab; pangea's `exportGuard`-false leg got a voice too. SECOND DEFECT, same handshake: the
  sender documented "the studio posts {vibeReady:1} … so we post on it instead of polling
  blind" and never did — `addEventListener('message', onMsg)` sat inside `rd.onload`, after
  the whole 2066×1319 cut, so both ready pings (parse ~0.5s, boot-end ~1–3s) were missed on
  every handoff that ever ran. `postFaceToStudio` is now `armStudioHandoff(w)` at the click +
  `handoffFace(h, blob)` when the cut lands, retry budget counting only ticks where a face
  exists. PROOF: NEW **KILL-TEST 4** (`card-studio-door`) drives both silent legs through the
  real UI on all three pages — **48/48 GREEN, 18/48 against pristine HEAD**, where the
  blocked pop-up and the second tap each open a real blank tab (`defaultPrevented=false`,
  `newTabs×1`, toast `""`). KILL-TEST 2 (real handoff) still 8/8; card-aspects OK on all
  seven card pages; `node --check` clean on every inline block. **NOT LIVE YET, and that is
  the honest state:** persona500 does not deploy from a push to main — Railway builds from
  the `persona500-deploy` staging tree via `automation/scripts/deploy_to_railway.sh` (proof:
  `98d2a7b` was authored 8.4h before its own `deploy_time`), so `9809dea` + `970a023` sit on
  main and prod still serves `98d2a7b`. That release is P5's; this lane pushed main, broadcast
  the hand-off (fleet #15642) and shipped `DOOR_BASE=https://persona500.com` so the same 48
  assertions can be re-run against what actually ships. The wishes stay **building**, not
  shipped — a live URL nobody can load is the claim this book keeps minting scars about.
  BACKPORT rider: **FIRED** — the
  door fix landed on all three generators in the same commit (the wish asked for it by name),
  and a second class was swept with it: every toast was capped at HALF the viewport
  (`left:50%` + shrink-to-fit means max-width never binds), so a 122-char message rendered
  160×161px at 320px on all three; `width:max-content` gives 292×82px with
  scrollWidth == clientWidth at 320/360/390/430. Storefront: n/a — cards lane, no
  fieldToolkits entry. FOUR SCARS minted (§SCARS), two of them against my own gate: a first
  draft poked `window.busySave` on pages whose JS is inside an IIFE and passed identically
  against both builds, and a second entered the busy state by reopening the modal — too slow,
  the cut resolves in 0.4s. Wells after: AV 0/0, vibe 2 new (iOS input-zoom on the wish field;
  cropper black edges). NOTE: this lane pushed persona500 for a card-page fix — exactly one
  unpushed commit, zero behind, deploy-safety confirming no other pane's WIP in the staged set.

- **[AXIS:WELL] C3657 (2026-08-25) — THE PICTURE ARRIVED, FILLED THE CARD, AND WAS
  INVISIBLE (vibe wish 2ce53d86, LEVIATHAN-010, the oldest of two stale `building`
  claims).** Both wells read 0 new, so claim order sent this cycle to the stale-claim
  sweep, and the older claim was real unfinished work: *"when card opens on card studio
  maybe refine the cropper or renderer so it re renders with no black edges? Or no edges
  with entire faces full black or below threshold — sometimes the sample is large enough
  to fill the card."* It was not the cropper. `placeFullCard()` unshifted the arriving
  picture to index 0 — the BOTTOM of the face's element stack — reasoning, in its own
  comment, that "a full-card image dropped on top would hide the text." True of text.
  Not true of the **47 shipped templates that ARE one opaque full-card image at exactly
  card size.** MEASURED through `drawFace`, the renderer that prints: blank face
  **99.31%** of the card is the picture; `leviathan-front` **0.00%**; `leviathan-back`
  **0.00%** with 24.95% of the card near-black; **all 47 art templates 0.00%**. What the
  eye got was the template's own ink — a dark border ("black edges", 23.05% near-black
  measured on the outer ring alone) and a baked QR plate ("entire faces full black").
  Their last clause was the proof the picture was fine: it filled the card, nobody could
  see it. THE RULE NOW, one function so it cannot drift (`placementFor`): *filled* —
  nothing covers the card, bottom of the stack, byte for byte the old unshift so a name
  still prints over a photo; *over-art* — a design's artwork is there, the picture goes
  ON TOP and the artwork is KEPT; *replaced* — a picture we placed earlier (a `data:`
  src, ours) is swapped in place. Over, not replacing, is deliberate: **this app has no
  undo and `leviathan-back` bakes its scannable code into the artwork pixels** — deleting
  that is unrecoverable, covering it is not. `coversCard()` reuses `bledElement`'s flush
  test (T = 0.01 mm) and its rot exclusion; hidden, rotated, see-through and contain-fit
  elements are not covers, an image with NO src IS one (the renderer paints an opaque
  placeholder), and the scan runs top-down like `hitElement`'s. JUDGE PANEL: three
  independent lenses, **6 / 6 / 5, unanimous BUILD WITH CHANGES** — every required change
  landed, and the user-intent judge is why the design changed from replace to cover (it
  found the baked QR and the no-undo trade), while the blast-radius judge found the
  sibling. PROOF, LIVE at https://mrdirno.github.io/vibe-cards/studio/ (vibe-cards
  `0d45310`, Pages deploy green): **16/16 driving the REAL door on live
  persona500.com/leviathan into the live studio** — a real world arrives over the real
  cross-origin handoff, lands on the card, and over `leviathan-back`'s plate the card
  goes **24.95% → 0.18% near-black with 0% on the outer ring**. NEW **KILL-TEST 5**
  (`card-studio-cover`, persona500 `c8c365018b`, beside kill-tests 1 and 4) measures
  RENDERED PIXELS across blank / front / back / a hand-laid opaque rect /
  text-must-stay-on-top / two handoffs running / **and every template carrying full-card
  art** — **26/26 green, 47/47 clear; 17/26 against pristine, naming all 47 at 0%.**
  KILL-TEST 1 still 8/8, `tools/verify.mjs` 16/16 with a new over-art/replace probe,
  mobile gate watertight at 320/360/390/430, `node --check` clean, the 3 NUL cache-key
  bytes intact. BACKPORT rider: **FIRED, twice.** `duplicateSel()` pushed its copy to the
  top of the WHOLE face, so duplicating a full-card background jumped it in front of every
  name, code and mark — the same "silently covering your work" shape inverted; now
  `splice(i + 1)`. And the studio's toast rendered **160×107 at 320px — half the viewport,
  six lines** — because `left:50%` puts the box's space at 50vw and shrink-to-fit means
  `max-width:70vw` never binds; `width:max-content` gives **224×72**. That is the
  IDENTICAL defect and the identical fix C3656 landed on persona500's generator toasts one
  day earlier, unswept in the sibling repo until now. Also shipped this cycle: wish
  **12183f06** (the Card Studio door) closed at last — held `building` by C3656 because
  prod had not deployed, now **48/48 against production** with `DOOR_BASE=https://persona500.com`.
  Credit: an anonymous Card Studio user, av/credits.json #23. Storefront: n/a — cards
  lane, no fieldToolkits entry. Wells after: AV 0/0, vibe 0/0, zero stale claims.
  **LEFT UNSERVED, named:** the wisher's *"below threshold"* is a separate persona500-side
  rung. Leviathan card faces measure 30.6–78.9 mean luminance against shipped deck art at
  59.7–76.9, so the darkest cuts really are darker than anything in the deck — this change
  cannot help a picture that is itself dark, only one that was fine and hidden. Named as
  its own rung, not folded in.

- `2026-08-25` — **[AXIS:DOCS] C3658 — THE LIST OF WHAT HE HAS TO SAY WAS ONLY EVER TOLD
  TO THE MACHINE** · **before:** the well was dry on both sinks (0 new, 0 building) and no
  family was owed, so the stalest axis governed. `facts` is authored on every document in the
  library — **214 documents, 661 distinct strings, 4 characters to 240** — and it reached
  exactly ONE reader: the model, inside VALIDATION, inside a 9,500-character block a man
  pastes into a Gem **once** and never opens again. The person whose whole job is to SUPPLY
  those facts was never shown them, and the engine's own instructions then bill him for it:
  every fact he did not say comes back `<MISSING>`, and the omitted line — the field this
  book calls the highest-value in the program — comes back `<MISSING>` **at the TOP of the
  open items by design**, because nobody told him to say it while he was talking. · **after:**
  **THE SAY-LIST**, on the picked card of all 14 write-up pages, from the same authored data
  and nothing new: the document's own facts, NUMBERED (a man rattling eleven off in a truck
  needs to know he is on 6 of 11), the family's continuity cue as the only addition — *"only
  what CHANGED since the last one"* for a report on a rhythm, *"say it whole; whoever reads
  this was not there"* for a record read years later, both compressions of the CONTINUITY
  block the engine already emits — and the omitted line directly beneath in the red frame it
  has always worn, NOT repeated, because it is the last thing to say. One control: **"Send
  this to your guys"**, which copies the list as plain text a foreman pastes into the group
  chat so three leads never open the page — **numbered there too, and the omitted lines keep
  their own heading and their place at the end**, because a flat dash-list in a text message
  throws away the red frame the card gives the highest-value field in the library.
  **PUTTING IT IN FRONT OF A HUMAN FOUND THREE LIVE DEFECTS IN MINUTES** (§SCARS): five
  framing documents author NO `facts`, so the block shipped **"check the input for: ."** — an
  empty check; `.join(", ")` turned `hvac/compressor-failure-report` into a **600-character
  run-on** where *"…amps at failure. Your numbers, nothing graded, What the oil…"* reads as an
  instruction, a fragment and a new list item in one line; and the halt bullet **said "stop
  and ask" twice** on **22 documents** across gc, hvac, low-voltage and plumbing, whose
  authors had already written the verb — a count that took THREE readings to settle: a source
  grep said 14 (it missed the shared library's per-trade overrides), the first gate said 21
  (its halt matcher identified the line by an alternation of opening words and went blind,
  silently, on the one author who opens *"Stop and ask on two things only:"*), and only a
  matcher anchored on POSITION — the halt is the second of three bullets, always — agreed with
  the merged libraries at **22**. All three fixed: framing's five authored from their
  own sections, the check emitted one bullet per fact, the generic tail standing down for an
  author who already used the verb — the mirror of the 2026-08-16 "Never halt" rule. Two
  further finds the card exposed: my own change made the fact bullets typographically
  identical to the three missing-input RULES beneath them, so those now carry their own stem
  (**WHEN SOMETHING ON THAT LIST IS NOT IN MY INPUT:**) rather than one blank line a model
  must infer a boundary from; and a mechanical addressee sweep of all 661 strings found
  **exactly one** written at the model rather than the man — `plumbing/service-writeup`
  item six carrying an OUTPUT RULE — split so the fact says what he supplies and the rule
  moved to that document's own `WHAT I DID` section. **One instance in 214 documents is the
  measurement:** the corpus is well-authored, and the rot was in the fields nothing read.
  **THE NEGATIVE CONTROL CAUGHT MY OWN GATE** (§SCARS): first pass, deleting framing's five
  `facts` back out — the state that had been live — left the gate **GREEN**, because
  `factsOf()`'s family fallback rescued it before any assertion could see it, while the gate's
  header claimed the belt was never load-bearing. Re-aimed UNDER the fallback, at `d.facts`
  rather than `factsOf()`. **FOUR NEGATIVE CONTROLS THEN PROVED RED ON THE SHIPPED DEFECTS
  BEFORE THE GATE WAS TRUSTED:** facts deleted → 5 failing · comma-join restored → 214 failing
  · halt tail always appended → **21 failing, which is how the true count was found — a source
  grep had said 14 and missed the shared library's overrides** · the cue crossed so a
  stand-alone record is told "only what changed" → 158 failing · the copy un-numbered → 14
  failing, because a list he reads numbered and sends un-numbered is two lists · the card
  rendered one character short of the block → 214 failing · the card's cue crossed against the
  block's CONTINUITY → 372 failing · the exclusivity dropped from `gc/impact-notice` → 1
  failing · the custom path's seed disclosure removed → 70 failing · the halt tail
  always appended → 22 failing, the reading that finally settled the count. **The two tautologies
  survived the FIRST four controls**, because a negative control asks "can this gate fail" and
  a tautology fails happily when you break the function BOTH sides read — the real test is
  whether the two sides of a compare come from different places.
  **BACKPORT RIDER FIRED — DERIVED MECHANICALLY, NOT ASSUMED.** The fix lives in the shared
  engine, so all 14 trades take it in one change. The CLASS — *a required-input list the
  runtime knows and the user never sees* — was then swept across every one of the 15 shared
  modules by extracting each engine's config keys and diffing its emit-only sites against its
  render sites: **`shared/docspec.js` is the only module in the program with emit-only keys at
  all**, and of those, `halt`, `trade` and `vocab` are machine rules, leaving `facts` as the
  single instance of the class. **Swept and NOT fixed, named so it is not lost:** `note` (62
  documents — *"no money words, ever"*, *"this is not an inspection"*) and `secondary` are
  also AI-only, but they are the ADJACENT class — rules about what the document must not
  claim, enforced where enforcement belongs — not required inputs; and a foreman lens flagged
  that nothing on the card distinguishes *"job name and number"* from *"circuit believed dead
  or known live"* by weight, which needs authored severity the library does not carry.
  **AN ADVERSARIAL FOREMAN LENS ON THE REAL SCREENSHOTS CHANGED THREE THINGS BEFORE SHIP:**
  the sub-line said *"comes back marked `<MISSING>`"* — angle brackets read as a broken page to
  someone who has never seen the token work, and **the screenshot path is real**, so the card's
  first ten seconds are not spent on notation; the list was bulleted, now numbered; and the
  control was *"Copy this list"* one screen above *"COPY INSTRUCTIONS"*, so a man on a ladder
  sends his lead the whole AI setup block — renamed to say what it is FOR. The same lens
  independently confirmed the plumbing item-six defect the addressee sweep had already found.
  **AN ADVERSARIAL CODE PASS THEN FOUND FOUR MORE, INCLUDING A FALSE CLAIM IN MY OWN GATE'S
  HEADER** (§SCARS ×2). **(i)** the halt suppression tested the author's WORDS, not what his
  sentence CLAIMS: 21 of the 22 matching halts also say *"only"*, but `gc/impact-notice` uses
  the verb with **two conditions and no exclusivity**, so dropping the tail there turned the
  one halt in the program with two conditions into a licence to interrogate about anything —
  the tail now stands down only where exclusivity is already stated, and is otherwise supplied
  in words that do not repeat him. **(ii)** the gate's headline assertion — *"both readers see
  the same list"* — compared `factsOf(d)` rendered against `factsOf(d)` called, **a tautology
  that could not fail**, while the only check touching the block compared bullet COUNT and
  never a string; it now compares the card's DOM against the COMPOSED BLOCK TEXT line by line,
  two artefacts built by different code paths. **(iii)** the copied message ended in a
  lowercase fragment — the cue's leading ellipsis was stripped for the copy, leaving *"and only
  what CHANGED since the last one…"* with no antecedent in a message forwarded to somebody who
  opens it cold; one source, two endings now. **(iv)** the CUSTOM path seeds its facts straight
  off the family, so five generic lines rendered under a confident heading with **no disclosure**
  — while the omission tick two controls over discloses exactly that class — and `library()`
  never returns the custom document, so the gate was blind to the whole path. Both fixed, and
  all five families are now asserted there.
  **GATES:** new `tools/toolkit-gates/docspec-say.mjs` — **14 trades / 214 documents / 2,978
  checks / 0 failing**, asserting card-DOM against composed-block text line by line, that no
  document authors zero facts, that one fact never shares a line, that the halt never repeats
  itself AND never loses its exclusivity, that the card's cue and the block's CONTINUITY agree
  about the same document, that the custom path's five families each produce a different list
  and each say they are a seed, and that the copy control ships what is on the card and not a
  second block (driven through a stubbed clipboard, on the string, not on the button's
  existence) — and **RE-RUN GREEN AGAINST PRODUCTION**, all 2,978 checks on the live site
  after the deploy, plus an independent live sweep of all 14 trades driving each one's
  WORST say-list end to end (card ≡ block line by line, numbered, the stem present, no empty
  check, zero overflow, zero page errors) · **docspec 14 trades / 228 checks / 0 failing** · **desk 14 trades / 0 failing**,
  after its facts extractor was re-anchored — it had gone red on all 14, which is how the
  format change was proved to reach the desk path · **mobile-watertight 140 pages ×
  320/360/390/430 × default and bumped, 0 failing**, with a NEW `REVEALS` entry for the
  say-list that derives each trade's worst document IN-PAGE (plumbing's eleven facts / 716
  characters, electrical's fifteen) rather than hardcoding a roster that could rot ·
  **no-third-party 140/140** · **menu-reachability green** · the custom path driven through
  **all five families**, each producing its own say-list and its own cue, and the zero-omit
  copy checked. Storefront unchanged — no new tool, no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/framing/write-up.html
- `2026-08-25` — **[AXIS:BACKPORT] C3659 — THE SEARCH SAID "THIS IS IT" 3,838 TIMES WHEN IT
  MEANT "THIS IS THE CLOSEST I HAVE"** · **TAGGED BACKPORT ON PURPOSE, THOUGH THE RUNG CAME
  OFF THE COMMONS LADDER:** the human layer — gear, tips, photos, guides — was not advanced by
  a line, so COMMONS stays owed and the next cycle should still see it as stalest. What
  happened instead is a single engine defect swept across **29 pages in one commit** ·
  **before:** COMMONS was the stalest axis and its book already named the rung, one floor
  down: *"`find.js` sets `mode = "exact"` when every LIVE query token was covered, not when
  the match was strong."* Re-measured on fourteen trades through the real boxes — 767
  unambiguous terms × 14 = **10,738 searches** — the class is bigger than the note said:
  **3,838 answers handed over with no hedge on them**, 3,615 of those a document the reader's
  trade **does not carry at all**. A plumber's *"gas shut off notice"* typed on the AV page
  returned the **Room Sign-Off (Commissioning Write-Up)** as an exact match; *"failed
  inspection"* returned the Meeting Failure / Outage Report. And it was 29 surfaces sharing
  the engine, not the 16 on record · **after:** a match now carries a **STRENGTH** beside its
  score, answering a narrower question than the score does — **did he NAME this thing?** Strong
  means the token is a word of what the item is CALLED (its title, or an alias somebody wrote)
  and he typed that word whole. Weak means the engine reached: it changed his characters
  (fuzzy), found his letters buried inside other words (infix), read past a word he had
  finished, or found the word only in a field the caller declared `about: true` — prose that
  says what a thing is FOR and names nothing. `mode` is now a claim about **the row he sees
  first**, and every caller already rendered the honest label, so the fix lands on all 29
  surfaces with **no page change**. **UNHEDGED WRONG 3,838 → 2,027. His own document first
  3,986 → 4,139. Zero answers right-before-and-wrong-after, zero correct answers hedged.**
  **THE ONE EXEMPTION IS THE WORD UNDER THE CURSOR:** a prefix counts as strong on the LAST
  token only, because half-typed is not the same as wrong. Measured both ways — strict
  everywhere scores better on complete queries (1,907) and turns **half of every keystroke into
  a "Closest to"** (113 of 214 four-character queries hedged); the exemption costs 99 of 10,738
  and returns mid-typing to silence at **214 of 214**. **THE +153 CAME FROM SOMEWHERE ELSE, AND COLLECTING IT COST TWO DEFECTS OF ITS OWN:**
  rule 4's phrase bonus had only ever looked at the PRIMARY field, so *"The Turnover Write-Up"*
  — a name an author wrote, in `aka` — lost to the Service Call Write-Up on the AV page. It now
  counts wherever a name is written, tested against **each alias on its own** and never against
  the aliases joined, because a query straddling two of them is not a name anybody wrote.
  **WHAT WAS CUT, and it is the finding:** letting strength also decide WHAT IS SHOWN (tier by
  strong coverage first) was written, working and elegant — **4,160 right with it and 4,160
  without**, and 56 more wrong answers made confident. Ablated out. Rule 2 is untouched.
  **BACKPORT RIDER FIRED, and it is the shape of the whole cycle:** every `Find.index(` call in
  the tree was swept in the same commit — `shared/docspec.js` (`why`), `commons/commons.js`
  (the object clause and the why line, on all three commons surfaces) declared `about`;
  `shared/pickfilter.js` has one field which IS the row's identity and correctly declares
  nothing. **GATES: `tools/toolkit-gates/find-honesty.mjs` is new — 17 surfaces, 6,492 checks,
  0 failing, every probe DERIVED from the surface's own strings so a row added next month is
  tested the day it lands (A verbatim name · B authored alias · C a query of words that name
  nothing on the surface · D one typo · E the spaces taken out · F the word under the cursor · G a word in THIS title and no other
  title LEADS this row, whatever answers to it as a nickname — added after an adversarial
  read found a lead flip A-F structurally cannot see, and verified red on that draft).
  PROVED RED BY NEGATIVE CONTROL against the engine as it shipped: `C 0/667 · D 0/593 ·
  E 0/668` — every prose, typo and joined-name query presented as exact — plus `B 1,852/1,933`,
  which is rule 4's blind spot showing up as 81 aliases leading with the wrong row. `A 693/693`
  and `F 539/539` are green on BOTH engines, which is what makes them a regression guard and
  not decoration.** Also green: docspec-say **2,978/0** · docs-pool **86/0** · commons-names
  **385** · commons-bag **506 states / 0** · pickfilter **12 pages / 156** · no-third-party
  **140/140** · mobile-watertight, plus a targeted long-query sweep — the new heading echoes the
  QUERY back, so a 62-character unbroken token was driven into all three box types at
  320/360/390/430: **24 states, 0 overflowing**. Storefront unchanged — no new tool, no new
  trade. **NAMED NEXT RUNG, with its falsifier already run:** rule 1 drops a token that matches
  nothing as noise the user added, which is right for *"template"* and silently wrong for a
  content word — **1,707 of the remaining ~2,027 (85%) carry dropped words**, and
  `commons/commons.js` already ships the answer (*Ignored "guard" — nothing here uses that
  word*) while the other 26 surfaces throw `noise` away.
  **RE-RUN AGAINST PRODUCTION AFTER THE DEPLOY, not only on disk: find-honesty 6,492/0 and
  docs-pool 86/0 on the live site, and the whole 10,738-search sweep re-driven through the
  DEPLOYED pages returns 4,139 / 2,027 — the same two numbers the working tree gave.**
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- **2026-08-26 (C3660) · [AXIS:WELL] · MINERALIA-016 "Needs to look real" — no ship, the
  engine is not mine to release.** Served the only `new` wish in either well (AV well empty,
  vibe-cards well one row, no stale claims anywhere). Cast a 3-lens JUDGE PANEL on the LIVE
  render before touching anything — a petrographer, an image-forensics eye, and a skeptic who
  went and pulled real crossed-polars photomicrographs first. They converged unprompted on the
  same three defects, and all three are one error: **something nature does by ACCIDENT was
  implemented as a LAW, or an absolute length was divided by grain size.** (1) `hdist` is a
  convex support function and `og.v` was constant, so every boundary in the frame was an exact
  straight segment — now ONE shared band-limited warp displaces the coordinates BOTH fronts are
  measured in, and `rock.sut` makes suturing DIAGNOSTIC (quartzite 1.45, granoblastic marble
  0.55). Scoped to the front only: migration moves where a grain ends, not the lattice inside
  it — carrying it into the interior gauge put boundary-scale wander onto 2-5px lamellae and
  every twinned grain came out as wood grain. (2) zoning was read off `sp.zone`, so EVERY grain
  of a zoned species wore the same concentric ring and `u` normalised per grain gave them all
  the same ring COUNT — **one gabbro plate carried the ring motif across 99.1% of its frame.**
  (3) `faces:0` fell through to `sqrt(X*X+Y*Y)`, an exact disc, and quartz is 78% of a
  quartzite. **MEASURED: zoned grains 56.6% → 15.4%, frame area carrying the ring motif
  61.1% → 17.5%; drag repaint 3.6ms → 2.5ms.** Kill-test **18/18 with 0 page errors, three
  times across the patch series** — the interference curve still matches published values to
  11/255 and 730nm is still turquoise, so none of it touched the physics. **BLIND A/B, new judges
  and a new randomisation: 5 of 6 pair-judgements called the fixed render better (one reader
  3/3 and named the OLD render as the one carrying the sphere; the second 2/3).** The one loss
  is honest and is the NAMED NEXT RUNG: the sphere's SHAPE is fixed, but a large
  low-birefringence grain still carries a smooth `tf` thickness ramp plus visible LUT contour
  banding, and that reader — who measured brightness profiles rather than eyeballing them —
  still called it a terminator. Both readers also still name flat polygon fills and repeated
  micro-texture stamps, so the ring was reduced and not solved. THREE realism metrics were built
  and CUT for measuring the wrong thing (§SCARS 3). **BACKPORT RIDER FIRED** on the `|0`-as-floor
  class — zero sites in the field toolkit, sibling card engines clean. **NO SHIP: the engine is
  `persona500/public/mineralia/index.html`, and persona500.com releases from the
  persona500-deploy staging tree, not from main (SCAR-C3655) — P5 owns that release.** The wish
  stays `building`, not shipped against a URL nobody can load. Change is in the worktree,
  patch saved at `_vault/outputs/handoff/C3660_mineralia_realism.patch`. **BINDING, and it must
  land as a pair:** the card faces at mrdirno.github.io/vibe-cards/mineralia/ are exports of
  THIS engine, so the deploy and a face regeneration have to ship together or the card's one
  claim — open the address and the same slice is cut again — stops being true.

- **2026-08-26 (C3661) · [AXIS:COMMONS]** · **THE SEARCH DELETED ONE OF HIS WORDS 3,631 TIMES
  AND ONLY ONE PAGE IN TWENTY-NINE EVER MENTIONED IT** · **before:** `shared/find.js` rule 1
  drops any query token that matches nothing and answers with what is left; `commons/commons.js`
  said so in four inline lines and **the other 26 surfaces said nothing at all**. Driven over
  **21,372 cross-surface searches through the real boxes: 3,631 came back labelled `exact`
  having quietly deleted a word**, and **3,409 of those (93.9%) kept HALF OR LESS of what was
  typed** — *"Inspection Note"* on the AV page deletes *inspection*, keeps *note*, and hands
  back the Damage / Pre-Existing Condition Note with no hedge on it · **after:** the sentence
  moved INTO the engine that causes it (`Find.dropped(res)`) and all three renderers call it —
  **3,631 → 3,360 now say so on the page (92.5%)**, `0 of 2,557` clean searches gained a
  sentence, and the move fixed three defects the single inline copy structurally could not
  see: plural over two words, a repeated word printed twice, and his own capitalisation.
  **THE PANEL VOTED TO DEMOTE THE LABEL TOO AND THE FALSIFIER KILLED ITS PREDICATE.** Two of
  three lenses said stop calling it `exact`; lens 2 gave `live <= half`. Measured: that costs
  **0 of 920** against own-page names — so lens 1's fear that *"Closest to becomes the app's
  normal voice"* is false — but **72 of 1,838** against a man's own item name plus *template ·
  form · sheet · pdf*, and all 72 are `1 word kept of 2` on a one-word item name. *"Washout
  template"* would be hedged: the cure becoming the disease. Not shipped; re-pitched in
  §THE COMMONS on a predicate the engine already computes (rule 4's `named()` — did the
  SURVIVORS spell a whole name, or a fragment?) with the 0/72 pair as its gate.
  **THE ADVERSARIAL LENS FOUND TWO THINGS 231 GREEN CHECKS COULD NOT.** (1) `norm()` keeps only
  `[a-z0-9]`, so *café* indexes as `caf` — and the recovery step then handed *"caf"* back
  **dressed up as the word he typed**, on a toolkit that ships a Spanish vocabulary block two
  trades wrote on purpose (`sitework/items.js`, `electrical/items.js` §TAG_ES). A recovered
  token now expands over anything that is not a separator until it is the whole word again:
  *café*, *résumé*, *compañía*. (2) A one-character token can only match EXACTLY, so the first
  letter of every word after the first is noise for one keystroke — the line appeared on
  *"1/4 drill b"* and vanished on *"1/4 drill bi"*, **text flickering under his thumb on the
  default interaction**. The word under his cursor is now held back until a separator says he
  finished it, which is the same exemption the scorer already makes, and **that fix exposed a
  second bug: every renderer `.trim()`s the query, so the "he finished" signal never reached
  the engine.** Both are now gate classes N8 and N9, red-verified on the exact draft the panel
  read. **BACKPORT RIDER FIRED — the class is "a surface quotes his raw query into the layout",
  and there are three.** Measuring the new sentence at 320px with a 54-character token pushed
  `hvac/truck-stock` **257px sideways**; the sweep then found the same class **pre-existing and
  live** in the `Closest to “…”` heading on **all 14 write-up pages** — 29px of horizontal
  scroll at 320, on a page that is clean with an empty search box. All three break long words
  now. Gates: **find-noise 318/318 over 29 surfaces (every class red-verified)**, find-honesty
  6,492/0, docspec-say 2,978/0, docs-pool 86/0, pickfilter 156/0, commons-bag 506/0,
  commons-names 385/0, mobile 20/20 at 320/360/390/430 on the longest sentence the data can
  make. **Storefront unchanged — no new tool, no new trade.**
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- **2026-08-26 (C3673) · [AXIS:DEPTH]** · **THE RUN IS NOT ONE RUN, AND THE PAGE SHIPPED
  SAYING IT WAS** · **before:** flooring was one of only three trades on a fourteen-trade
  rack with **no material list at all**, and by far the most order-heavy of the three;
  `flooring/tools.js` §2 had held the rung open since 2026-08-17 with the reason written
  on it — *"a vocabulary build the size of the supply-house order… half-building that is
  worse than not building it"* · **after: THE DEALER CALL is live**
  (`flooring/dealer-call.html`, flooring **8 → 9 tools**, rack **109 → 110**), the
  **eleventh** instance of shape #1 and the first whose SECOND READING is **derived**:
  `run` and `atticable` ride on the item in `items.js`, so the run block gathers itself
  and the attic-stock question raises itself against it — **nobody ticks anything.**
  **82 lines of trade vocabulary across seven categories, 31 of them run-bearing.**
  **THE PANEL BROKE THE THESIS, NOT THE CODE.** Three lenses read the shipped artifact.
  The field hand killed the sentence the mechanism was stolen with: a coil of **base** is
  Roppe or Burke, coordinated by colour, and on a carpet or tile job **guaranteed** to be
  another maker — so printing it under the plank's lot number sends a counter hunting for
  a number that is not in the base catalogue. **63 green assertions could not see it,
  because they proved the code matched the data and the data was wrong.** The run is now
  **one run per product FAMILY** — `field` (26 lines) and `base` (5) — two blocks, two
  sentences, one field. The same lens found **weld rod** missing (a welded seam in a
  hospital corridor is colour-matched rod off the sheet's own run, on a page that shipped
  sheet vinyl and sheet rubber) and **VCT** missing outright; both are in, with backer
  screws, a moisture-mitigation kit and a wet-saw blade. The safety lens found the file
  **breaking its own header rule six times** — `"BY THE BAG OR THE BUNDLE"` carrying
  `unit: "bag"`, so a bare 10 printed *"10 bag"* — now mechanical and asserted. The
  adversarial read found the on-glass hints classified by **regex on the item name**, and
  both interesting regexes were already wrong against their own data: `/tape/` caught
  masking tape (the *"nothing to hold them down"* nudge died silently in the exact case it
  exists for) and `/tile/` caught **carpet tile** (asked about grout). Plus one **latent**
  defect — `shared/checklist-request.js:312` gives a CLONED catalogue row the same `.rm`
  marker a write-in has, so a future *"+ another length"* on a stair nose would have
  dropped it out of the run block; keyed on catalogue membership now and **verified by
  injecting the engine's own clone button**. Gates: **68 end-to-end assertions driving the
  REAL page** (all 13 units rendered on a bare number, both run families, the write-in
  tick, the clone, the inverse case, clipboard === preview), **mobile-watertight 141/141**
  with the new page green at **320/360/390/430 on all 82 rows ticked plus an unbroken
  78-character token**, order-live-header **12/12 order pages**, no-third-party **141/141**,
  find-noise 329, find-honesty 6,492/0, commons-names 385, boundary-titles 41, dropoff-block
  9/9, jobcard-scope **10/10 green and red-verified at 10 defects**, menu-reachability 966,
  pickfilter 169/13. **RE-RUN GREEN AGAINST PRODUCTION — all 72 assertions re-driven
  through the DEPLOYED page** (base pointed at the Pages origin, not the working tree),
  because green on disk is not green on the artifact and this repo has a scar for exactly
  that.
  **BACKPORT RIDER FIRED, AND IT WAS THE BIGGEST THING IN THE CYCLE.** Chasing the
  double-sourced `fAttic` into `shared/jobcard.js` found `setVal()` unable to tell "no
  answer" from "an answer this list cannot hold" — it bailed on both, so **a new job kept
  the previous job's `<select>` on the glass and printed it as its own.** Swept off disk,
  not assumed: **9 of the 10 job-card pages carry the class** — `fCharge` on concrete ·
  electrical · framing · low-voltage · masonry · painting · roofing · sitework, plus
  `fAttic` here. **`tools/toolkit-gates/jobcard-scope.mjs` was green through all of it
  while its own summary read "a new job starts empty"**, for two reasons: `fillHeader()`
  skips selects on purpose, so they were never in `PER`; and the assertion is
  `if (afterNew[id])`, which a correctly RESET select fails anyway because "Job" is truthy.
  The gate grew the class it could not see — empty for a select is the option the markup
  marks SELECTED — and it is **RED-VERIFIED: reverting the one-line engine fix turns it
  red with 10 defects across 9 pages**, `#fCharge` reading *"T&M / extra"* on a brand-new
  job, a charge code from another job riding out on a material order. The page's other
  three defects did NOT backport and that was checked, not assumed: the ten older order
  pages carry the run as a TICK, so the clone marker costs them nothing, and the
  unit-of-issue rule was swept across all twelve `"X OR Y"` lines **in this file**, which
  is where that rule lives.
  **A NEAR-MISS WORTH MORE THAN THE FIX:** driven through a Playwright locator,
  *"+ Another job"* appeared to do **nothing** on this page AND on painting — which reads
  as a live engine defect on every card in the program, and was written up as one before
  it was checked. It is not. `collect()` calls `paint()`, which replaces `host.innerHTML`,
  so the click lands on a **detached node**. Dispatched in-page it works every time. **The
  test manufactured a product bug out of its own race, and reporting it would have sent a
  future cycle hunting something that is not there.** **Storefront: one line added to flooring's `tools[]` in
  `persona500/src/data/fieldToolkits.ts` — P5 pushes.**
  https://mrdirno.github.io/nested-resonance-memory-archive/flooring/dealer-call.html

- **[AXIS:BREADTH] C3674 (2026-08-27) — THE FIFTEENTH TRADE HAD ALREADY LOST TWICE, AND THE KILL
  WAS AIMED AT THE WRONG COMPANY.** Both wells dry (0 new, 0 building, 30 shipped) and no family
  owed, so the stalest axis governed: BREADTH, 11 lane-cycles cold. Ran the standing #15 method in
  order — gate-vocabulary query first, who[] count beside it, shortlist INCLUDING the
  count-invisible, panel disposes. The who[] re-tally: **doors 5 kits (flooring, framing,
  low-voltage, masonry, painting) · fire sprinkler 5 · steel 4 · ceilings/grid 4 · millwork 4 ·
  elevator 1** — and elevator, which the raw keyword scan had ranked FIRST at 16 mentions across 11
  kits, collapsed to one: eleven of those kits mean the elevator as a *building object* ("freight
  elevator's ours 7 to 9", "scuffs by the elevator, cart height"). **Mention count measures how
  much other trades trip over your work, not how much mail you send** — the count-first instrument
  was wrong again, the second cycle running. FOUR LENSES, and the first cast was MY error: I gave
  them a shortlist with doors, ceilings and steel missing, and had to send the correction mid-flight.
  **NOT UNANIMOUS, and the dissent is the record:** doors took #1 from the field-hand and the
  doctrine lens, #9 from population (identity), unranked→last from boundary. Sprinkler took #1 from
  boundary and #2 from the field hand — **both dissenting from the recorded #14 family-kill on the
  same argument** (it conflated the trade's certified documents with its field mail, the way HVAC
  ships an evac record and no charge chart) — and the doctrine lens, the only one that read the repo
  and re-tallied the rosters itself, held the kill: hydraulic calcs sealed by a NICET III or PE, the
  material-and-test certificate printed INSIDE the standard, ITM reports owned and numbered by
  third-party portals. **POISONED at the centre, not the edge.** Steel took #1 on population and
  died the same way (chapter 17 special-inspection record; the ban list names torque specs
  outright). Ceilings took #2 on population and lost its own premise to BOTH lenses that examined
  it — `concrete/trade.js` already wrote the sentence that settles it, *"a wall can be cut, A
  CEILING CAN BE PULLED"* — and its 118,600 headcount is the COMBINED BLS drywall+ceiling-tile
  code we already serve as framing. **Doors is the only candidate ranked #1 twice and vetoed by
  none, and the highest one surviving the safety rail.** THE KILL IT HAD TO SURVIVE, and the test
  that makes it checkable rather than a matter of taste: the schedule and the sets are the product
  for the DISTRIBUTOR; for the INSTALLER the schedule is an input he RECEIVES. **We cross the
  system of record only when our page becomes a second place the record lives** — (a) reproducing
  the owner's content, (b) issuing a rival identifier, (c) built to be filed instead of his form.
  Citing "Opening 101A" does none. **ADDRESS IS CLEAN. CONTENT IS DEAD.** The rack had already
  written the three-party distinction down without noticing: masonry names "Hollow metal / door
  supplier", framing "Doors & hardware", low-voltage "Door hardware". SHIPPED WHOLE — 8 tools:
  `before-they-ship` (PINNED, row-log — the openings walked with a tape before frames are welded;
  hand, wall, throat and what's in the way, none of it supplied, all of it his) · `rough-in-request`
  → **Set It For Me**, which is where the INTERFACE lands: `low-voltage/items.js` ships `doorprep`
  with `who: "doors"` — electric hinge, raceway in the leaf, frame prepped for the strike — an ask
  aimed at a man who until now had nowhere to answer it · `answer-back` → **Punch Back**, whose
  fourth rung is this trade's own: **"Not my call"**, because an installer frequently cannot say yes
  at an opening · `came-off-the-truck` (row-log — and *where you found it* is a first-class column,
  because a dent photographed on the trailer and one found on day nine are different conversations
  with different people paying) · `not-ready-to-hang` · `getting-in` · `write-up` (6 documents,
  17 total) · `total-package`. Commons joined on all THREE surfaces at 8 rows each (gear, tips,
  names — the name table is where this trade is richest: slab, core, strike, throat, hand and
  mullion all belong to somebody else on the same job). Accent **#B7BEDC**, primed hollow metal, and
  the first chip in the ONE structurally empty band on a 15-chip rack: the raw dE winner was a fifth
  pale pink (38.5) and repeating painting's recorded kill, so the sweep was re-run BAND-AWARE —
  nav 7.87 · ink 10.29 · white-on-deep 10.78 · dE 28.9, honestly below painting's 34.6, and the
  next stand-up should expect to argue for a new band rather than a better number. **GATES CAUGHT
  TWO OF MY OWN ERRORS BEFORE SHIP:** `docspec-config` failed 4 of 6 documents because I handed the
  writer a family vocabulary that does not exist (report/claim/log against the engine's five), and
  a hand audit of the RowLog surface caught `rl.refresh()` and `rl.clear()` — neither is on the
  engine — plus a missing `restore()`, the one §SCARS calls not optional. Also caught by sweep: a
  localStorage key still namespaced `toolkit.painting.notready.v1`, which would have made two trades
  share one saved note. **THE DEMERIT, WRITTEN AT STAND-UP so no later cycle rediscovers it: this
  trade survives BY DISCIPLINE, NOT STRUCTURALLY.** Flooring's numbers are warranty terms that
  disagree, so there is nothing to supply; here rated-assembly data sits at the centre and somebody
  will eventually propose a label field. Low-voltage proves discipline-survival is possible on this
  rack; it is just more expensive to hold. **AND THE RISK THAT IS NOT ABOUT DOCUMENTS:** two lenses
  independently found this trade may have no name its people call themselves — in union markets he
  is a carpenter out of a local, and framing already owns `carpenter`/`carpentry` in the storefront
  match, so doors binds NARROWLY on six measured precision-1 tokens rather than double-binding every
  framer. That is a measurement to take, not an argument won. BACKPORT RIDER FIRED — the
  module-adoption grep (creative's own recorded lesson: run it before ranking anything) found
  **painting at 10 of the 12 shared modules every sibling carries**, missing `package` and `lang`.
  `lang` is NOT a hole — it rides on tm-tag across twelve trades and painting deliberately ships no
  tag, already recorded. `package` was an UNNAMED absence, which §TRADE EXPANSION calls a hole, and
  painting was the ONLY construction kit on the rack without Total Package: shipped, +1 registry
  line, one per-trade sentence. THREE MORE GATES CAUGHT ME ON THE WAY OUT, all before push: `getting-in`
  floors the ask at 8 needs and 8 heads and this kit shipped 7 and 6; `reconcile-join`
  failed because **"Not my call" was a rung `shared/reconcile.js` could not classify** —
  the exact far-end check the C3654 entry describes, firing on the one new rung this
  trade added, and it is now VERDICTS position [3] (`ask`, because an answer that lives
  with whoever stamps the submittal is an ask pointed elsewhere, not a refusal); and
  `mobile-watertight` found `getting-in.html` throwing `undefined.concat()` at all four
  widths on a config missing three keys — a blank page, in the commit, invisible to every
  gate that reads content. Storefront: doors is one new entry (P5 pushes) and painting one
  new tool line. **AND THE DEPLOY WENT RED ANYWAY, on the one checklist item that is not a
  list you join:** `shared/docsindex.js` is GENERATED from every trade's `docs.js` and the
  deploy asserts it with `--check` — a fifteenth library makes it stale by existing.
  Regenerated (15 trades · 13 poolable ids · 302 terms) and §TRADE EXPANSION now carries it,
  with the reason it was the one that got missed: the other four memberships fail a grep,
  and this one only fails a rebuild. VERIFIED LIVE after green: 15/15 doors URLs 200 · the
  53-assertion drive re-run against the DEPLOYED pages, all green · mobile-watertight 10/10
  doors pages against production at 320/360/390/430 in both text sizes · the backport's
  `painting/total-package.html` 200 and watertight, so all fourteen construction kits carry
  it. https://mrdirno.github.io/nested-resonance-memory-archive/doors/

- **2026-08-28 (C3675) · [AXIS:INTERFACE]** · **THE ACCESS BOUNDARY WAS SERVED IN ONE
  DIRECTION FOR THIRTEEN DAYS, AND THE PANEL KILLED THE PAGE THE ROADMAP HAD RANKED.**
  Both wells dry (0 new, 0 building, no stale claims) and no trade owed, so the stalest
  axis governed. The private roster's one concrete INTERFACE rung was an answer page for
  whoever RECEIVES an access ask; a four-lens panel (building engineer · GC super · the
  foreman who sends these · a skeptic given the program's own rules as weapons) scored it
  2 / 6 / 6 / 2 and killed it twice — the receiver is not our user and never will be (every
  kit addresses this document to a building engineer, a chief engineer, a property manager,
  a director of security or an owner's rep, the GC kit included, so "the super will use it"
  is not an escape hatch), and an answer page exists to BE the grant that `getting-in.mjs`
  bans the ask from producing. All four then converged on the shape the foreman described
  before he was shown it. **before → after:** the ask sent, and whatever came back was a
  text nobody could work to → `shared/whatcameback.js` mounted as an INTAKE on all fifteen
  `getting-in.html` pages, two lines each, **zero new per-trade vocabulary** because the
  rows ARE that trade's own `need`/`heads` ticks. Two ladders and the flagged one has no
  affirmative rung ever; silence prints FIRST as `NOTHING SAID ABOUT THESE`; the window
  they actually gave printed against the one we asked for, with a name at the door and a
  cell; and the day-of check, because the page has no server and says so. New gate
  `what-came-back.mjs`, 751 checks, **re-driven against the DEPLOYED pages after green —
  15/15 clean on production**, every permitted line driven through its ENTIRE ladder, four
  widths and the 44px floor. **BACKPORT RIDER FIRED, and it found two SHIPPED gates broken
  — both silent rather than wrong:** `getting-in.mjs` printed "every permit hands back"
  while running ZERO handback assertions on flooring and sitework (they write theirs as
  "something powered down", "regulated material", "who owns the closure and the permit for
  it"), so it now prints what it asserted per trade and fails on a zero; and
  `mobile-watertight.mjs` — THE mobile ship gate — died three trades short of the end,
  reproducibly before and after this cycle, leaving plumbing, roofing and sitework
  unmeasured behind a wall of PASS lines. Both fixed here. Storefront made true in the same
  cycle: 15/15 `getting-in` entries in `fieldToolkits.ts` carry the return leg (P5 pushes).
  `mobile-watertight.mjs` now runs to the end — **152 pages at four widths in both text
  sizes, 0 failing**, including the 30 pages it had never reached. And the answer layer's
  own worst defect was caught before anyone met it: Clear wiped the ask and left the
  answers standing, so a different building inherited the last one's man at the door — the
  fix is asserted, and the assertion was proved to bite by removing the fix and watching it
  fail. 781 checks green on production.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/getting-in.html
- `2026-08-28` — **[AXIS:DOCS] C3676 — THE LINE THE WHOLE LIBRARY IS BUILT AROUND NEVER
  SAID WHAT WOULD SATISFY IT** · **before:** both wells dry (AV 0 new / 0 building, vibe
  0/0, no stale claims) and no family owed, so the stalest axis governed. `omit` is the
  field this book calls the highest-value in the program, and it HAS always reached both
  readers — the block and, since the say-list, the red frame on the card. What would
  SATISFY it never did. The five omission classes each carry an `artefact` string ("a
  date", "a name", "a before-value", "a location", "a named gap") and it rendered at
  **exactly one call site in the whole engine**: the tick list on the CUSTOM path, the path
  a man reaches only when his document is NOT in the library. All **231 library documents
  printed their line and named nothing**. · **THE FAILURE IS NOT A DROPPED HEADING, IT IS A
  FLUENT SENTENCE.** `hvac/red-tag-notice` asks for *"the time you shut it off and the name
  of the human you handed it to"*; what comes back is *"the unit was taken out of service
  and the property manager was notified"* — heading present, sentence present, **no
  `<MISSING>` anywhere**, and the only two facts that survive a dispute are not in it.
  Nothing in the engine ever told the model that a sentence is not the artefact. **A
  working foreman named this unprompted as the one failure he cannot catch by eye, and said
  why: he KNOWS he handed it to Denise at 2:40, so he reads her name into a sentence that
  does not contain it — every time.** · **after:** `needs` is authored beside `omit` on
  every document in the program, shape-mirrored (a string omit takes a flat list, a list
  omit takes one list per line, in order), and it reaches **both** readers from one
  resolver: the block gets *"This is not satisfied by a sentence about it. It has to carry
  a date or a clock time and a name — actual ones, out of my input"* with a **per-artefact
  `<MISSING: the name>` token** so a half-gap cannot come back as prose, the OUTPUT FORMAT
  placeholder carries the same demand into the finished document, and the red frame on the
  card carries it **before he opens his mouth** — which is where the GC lens independently
  put it and where the foreman lens said the only value is. The group-chat copy carries it
  too, because three leads get that message and never open the page.
  **A FOUR-LENS PANEL KILLED THREE QUARTERS OF THE BUILD I PROPOSED, AND THE PART THAT
  SURVIVED IS THE PART TWO OF THEM NAMED INDEPENDENTLY.** The proposal was a paste-back
  checker on the returned document — missing headings · omitted line present · `<MISSING>`
  harvest · forbidden-claim flags. **UNANIMOUS KILL on the heading check**: the block's own
  OUTPUT FORMAT says *"leave out any section that is empty, except the last two"*, so a
  checker flagging an absent spine heading punishes the AI for obeying us — and it is not an
  edge, **all 231 documents are false-positive candidates**. **THREE OF FOUR KILLED THE
  FORBIDDEN-CLAIM FLAGS AND THE ENGINE LENS MEASURED THEM DEAD: 151 of 231 documents
  (65.4%) author no `note` at all**, 35 section rules contain a verdict word the engine
  itself prints (`creative/sign-off-record` emits the heading *"WHAT'S IN THE VERSION THEY
  APPROVED"*), and a verdict lexicon fires on **15%** of compliant content — while a
  detector's silence is a clearance manufactured by an interface, on the one boundary the
  notes hand to the engineer of record and the AHJ. The skeptic found the locked rail that
  settles it: two toggles in this engine are `locked` and one of them is **"never call a
  reading good, bad, passing or to code"**. A page shipping that rail cannot return a
  verdict about verdicts. **Nothing built this cycle judges anything.**
  **THE CLASSIFICATION WAS RUN BLIND, TWICE, AND THE DISAGREEMENT IS ON RECORD RATHER THAN
  SMOOTHED AWAY: 142 distinct authored lines, exact agreement 96 (68%), overlapping 35
  (25%), disjoint 11 (8%).** Settled counts: `when` 63 · `who` 52 · `where` 44 · `notdone`
  41 · `count` 30 · `before` 16 · `change` 10 · `ref` 8 · `none` 11. **Most lines demand
  more than one artefact** — 50 one, 57 two, 29 three, 6 four — which is the finding, because
  the omitted line that costs the most is almost never one fact. **THE VOCABULARY IS EIGHT
  AND THE TICK LIST IS STILL FIVE.** The 2026-08-15 pass derived seven and refused the two
  extras because *"seven ticks is the ten generic ones the rung forbade"* — a constraint
  about a TICK LIST that had been silently governing a DATA vocabulary with no tick list.
  `count` is demanded by 30 of 142; it was never a rounding error, it was invisible. **The
  EIGHTH was forced by the corpus three separate times**: a document and its revision — the
  sheet, the bulletin, the packing list, the version a yes was given against. 2026-08-15
  filed it unreachable (4 of 26); of this cycle's two blind passes one pushed it into
  `none` and the other into `where`, both legibly wrong. `framing/wont-fit` is the argument:
  *"the sheet numbers and revisions, WITHOUT WHICH THE QUESTION CANNOT BE ANSWERED BY
  ANYONE."* `none` stays a real value at 11 of 142 — forcing an interpretation-shaped
  omission into a fact class puts a confident demand under a line that cannot satisfy one.
  **BACKPORT RIDER FIRED, and one half of it is a gate that had gone blind (§SCARS ×3).**
  The engine is shared, so all 15 trades take the demand in one change; the 142 insertions
  were driven off the settled classification rather than typed. Swept the gate directory for
  the same class and found it: **`docspec-say.mjs` had its trade roster HARDCODED at
  fourteen and had never once run on `doors`** — a typed roster does not fail when a trade
  lands, it goes silently blind and prints a green number that is the number of trades it
  was told about. Derived from disk; **14 → 15 trades, 214 → 231 documents, 2,978 → 3,213
  checks, still 0 failing**, which is precisely why nothing would have surfaced it.
  **THE NEW GATE'S FIRST ASSERTION WAS WRONG AND ITS FIRST RUN PROVED IT**: it compared the
  override's `omit`/`needs` by VALUE and went red on 14 correct documents, because two
  differently-worded lines demanding the same artefacts is the library working. Re-aimed at
  the KEY, under `library()`'s merge, on the raw overrides map. **AND READING THE REAL PAGE
  FOUND WHAT NO ASSERTION COULD**: the card's stem prepended a second article — *"Say the
  actual a date or a clock time"* — and the card-vs-block agreement check passed it, because
  an agreement assertion cannot see an error both sides share.
  **GATES:** new `tools/toolkit-gates/docspec-needs.mjs` — **15 trades / 231 documents / 241
  omit lines (24 declaring none) / 1,951 checks / 0 failing**, asserting that every document
  authors `needs` OF ITS OWN read *under* the resolver's degrade, that the shape mirrors
  `omit` line for line, that every id is in the SHIPPED vocabulary read off the engine, that
  `none` is exclusive and renders as *"in your own words"* rather than an empty red demand,
  that the card's DOM and the composed block name the same artefacts, that the per-artefact
  `<MISSING: …>` tokens are the shipped ones, that an override rewriting `omit` declares its
  own `needs`, and that the group-chat copy carries the demand — driven through a stubbed
  clipboard, on the string. **SIX NEGATIVE CONTROLS, ALL PROVED RED**: a deleted `needs` →
  1 failing · the card crossed against the block → 196 · `none` made non-exclusive → 1 · an
  override stripped of `needs` → 1 · the demand dropped from the copy → 15 · the
  per-artefact tokens collapsed back to a bare `<MISSING>` → 217. · **docspec-say 15 trades
  / 231 documents / 3,213 checks / 0 failing** · **docspec 15 trades / 246 checks / 0
  failing** · **desk 15 trades / 0 failing** · **no-third-party 152/152** ·
  **mobile-watertight** grew a NEW `REVEALS` entry deriving each trade's heaviest demand
  IN-PAGE off `needsOf`/`demandOf` — a different worst case from the say-list reveal, which
  picks the longest `facts` — and the real frame driven at 390px on the single and the
  three-line cases, 0 overflow. **NAMED NEXT RUNG, with the panel's narrowed form already on
  record:** `note` is the mirror field — 69 authored prohibitions, **65.4% of documents carry
  none**, and its only reader is a machine, which is the exact condition §SHAPE #4 HAS TWO
  READERS puts on the clock. Print it for a person and give it its own imperative heading in
  the block; do NOT grade against it. Storefront unchanged — no new tool, no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/hvac/write-up.html
- `2026-08-28` — **[AXIS:BACKPORT] C3677 — THE ONE ORDER PAGE THAT SHOWED HIM NOTHING, AND
  THE GATE THAT COUNTED TWELVE INSTEAD OF FAILING.** · **before:** both wells dry (AV 0 new
  / 0 building, vibe 0/0, no stale claims), no family owed, so the stalest axis governed and
  it was BACKPORT. The order shape — `checklist-request` + `pickfilter` + `jobcard` +
  `dropoff` — is the most-layered thing on the rack and runs on 13 pages across 13 trades.
  Two of the thirteen are the AV kit, the kit this book calls the shipped quality bar, and
  they are the two that never migrated. **`av/consumables.html` is the only order page in
  the program with no `#preview` at all**: he ticks twenty lines, hits Copy, and finds out
  what he sent when it is already in the group chat. And
  `tools/toolkit-gates/order-live-header.mjs` — the gate whose name is THE PREVIEW IS THE
  DOCUMENT — **printed `OK — 12 order page(s)` for that page's entire life**, because it
  finds its subjects by probing for `#list` + `#preview` + `#copy` + `#clear` and the page
  was missing the very thing being probed for (§SCARS ×4). ·
  **A FOUR-LENS PANEL SCORED MY PROPOSAL 7/6/4/3 AND KILLED MOST OF IT.** The build I put up
  was a JobCard mount on both AV pages. Unanimous kill on `device:["fReq"]` — **`fReq` is the
  Requested DATE, not "requested by"**, and the page's own comment is the tombstone: *"a
  saved copy would print Tuesday's date on Thursday's list — the one field where remembering
  is the bug."* Three of four killed `legacyKey:"toolkit.av.cableList.v1"`: that key is the
  engine's list record, `{v,cats,extra:{job,by,…}}`, renamed and nested, and `adopt()` reads
  only a flat id-bag or draft.js's `{v,s}` — **a migration line that reads like it works and
  adopts nothing.** And `jobcard-scope.mjs` fails a mount whose `perJob` is empty: **neither
  AV page has a single per-job answer** — no PO, no cost code, no gate code, no signer — so
  the chip would swap nothing, which is the ceremony §THE STRICT BAR forbids and the same
  reason `hvac/truck-stock` was left out of the 2026-08-16 migration. **No job card shipped.**
  The panel also found a defect in the MODULE that is not this page's to fix (§SCARS). ·
  **after:** what two lenses named independently, shipped. (1) **`av/consumables.html` puts
  the document on the glass** — the block is `asText()` itself, the same function the Copy
  button hands to the clipboard, so the block and the message **cannot** drift; the gate's
  first assertion is true by construction instead of by inspection. The sticky jobsite is
  line one of it, which is the whole point: that box survives Clear correctly, but it also
  survives a WEEK, and until now nothing said so. (2) **`av/cable-list.html` stops destroying
  his job and his name.** Swept every order page: eleven reset `fFor`/`fNotes`/`fDate` and
  ten additionally declare `device:["fBy"]` — **cable-list was the only one on the rack whose
  Clear wiped `fJob` and `fBy`**, so he retyped the jobsite and his own name on every single
  order, one-handed off a lift. They move to a record of their own, the mechanism its sibling
  page already ships, with a one-time carry done where the engine hands the decoded record
  over rather than through an adopter that cannot read it. ·
  **THE GATE LEARNED THREE THINGS AND EVERY ONE WAS PROVED TO BITE.** It had never once
  clicked Copy on a page with a line ticked — a header floating on its own — and one page
  (correctly) disables Copy at zero lines. Ticking first enrolled the thirteenth page **and
  strengthened the other twelve by ~40%**: fields proved in the document went concrete 7→11,
  electrical 7→13, low-voltage 7→13, hvac 7→10, masonry 10→13. New clause: **whatever Clear
  spares must survive a reload AND must not live in the record Clear just dropped** —
  measured, not argued, across all twelve (they keep it in a `jobcard`, a `dropoff`, or their
  own `header` key; never the list record). **The first version of that clause went GREEN
  against the exact cheap fix it was written to catch**, which is how the second one exists
  (§SCARS). New gate **`row-live-line.mjs`** for the row half `order-live-header` skips by
  design — and it caught a live one on the first run: with the block up, `av/consumables`
  bound nothing to `.qty` or `.note`, so the glass read `Wall Dogs x1` while the message said
  `x8`. **BACKPORT RIDER FIRED on three classes and honestly reports two populations of
  one:** Clear-destroys-a-device-field (cable-list alone), row-controls-never-repaint
  (consumables alone, the engine already does it), and no-preview (consumables alone).
  **GATES:** `order-live-header` **13 pages / 3 assertions / 0 failing** (was 12/2) ·
  `row-live-line` **13/13** · `mobile-watertight` **152 pages, four widths, both text sizes,
  0 failing**, both changed pages re-driven individually after the last edit ·
  `no-third-party` **152/152**. **FIVE NEGATIVE CONTROLS, ALL PROVED:** `#preview` removed →
  gate silently reports 12 · header repaint un-wired → 2 defects · the naive Clear fix →
  2 defects under clause 2 (0 under clause 1, which is the scar) · row repaint un-wired →
  block ≠ message · a fuller naive revert → 6. **NAMED NEXT RUNG:** per-legacy-key adoption
  in `shared/jobcard.js` — the store is keyed per TRADE and `adopt()` runs once per store,
  so the first trade to get a second carded page silently drops one page's saved answers.
  Nothing on the rack triggers it today; everything does the day it does. Storefront
  unchanged — no new tool, no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/consumables.html

- `2026-08-28` — **[AXIS:COMMONS] C3678 — THE PAGE DELETED THE WORD THAT DISCRIMINATES, THEN
  GRADED ITSELF ON WHAT WAS LEFT.** · **before:** both wells dry (AV 0 new / 0 building, vibe
  0/0, no stale claims) and no family owed, so WELL could not be served and the stalest axis
  with work governed: COMMONS, last worked C3661, holding its own named next rung. `find.js`
  rule 1 deletes a query token that matches nothing on a surface — right for *template* and
  *form* — and then rules 2 and 5 ask whether the lead covered THE SURVIVORS. **"Inspection
  Note" on the AV page keeps `note`, answers with the Damage / Pre-Existing Condition Note,
  and passes every check anyone would write, because `inspection` was never in the
  arithmetic.** Driven over **72,138 searches on all 31 surfaces that load the engine: 3,125
  handed back a row the query did not name with no hedge on it.** · **after: RULE 6 — coverage
  of what SURVIVED is not coverage of what he TYPED.** `honest = … && (!say.length ||
  wholeName(lead, liveQuery))`. **3,125 → 675**, diffed query by query rather than totalled:
  **2,450 newly hedged, every one over a lead the query had not named, ZERO right answers
  hedged**, and the lead row never moved — 41,194 correct leads before and after, 0
  right→wrong, 0 wrong→right, because rule 6 decides what the answer is CALLED and never what
  it is. Good cases unmoved: verbatim name or alias **7,417/7,417** exact, that name plus a
  search-box word **7,064/7,064**, mid-typing **14,762/21,017**. · **THE RUNG WAS RIGHT ABOUT
  THE MECHANISM AND WRONG TWICE, AND BOTH CORRECTIONS ARE NUMBERS.** (1) It said fire on
  `noise`; it fires on `say`. A one-character token can only match exactly, so the first
  letter of every word after the first is noise for one keystroke — firing on raw `noise`
  leaves **3,456 of 21,017** mid-typing queries unhedged against 14,762 with the hold-back,
  which is the heading flipping to "Closest to" and back under his thumb on the default way
  this box is used. The engine already declines to NAME that word out loud; a word we will not
  name is not a word we may hedge on. (2) The panel's counting predicate `live.length <=
  noise.length` was predicted to cost 72; on the full rack it costs **371 of 7,064** — the
  rung was measured on 14 trades and one class of surface, and the rack has one-word gear
  names where *"Washout template"* is the whole name plus chrome. · **RULE 6 IMMEDIATELY
  CAUGHT WHAT RULE 4 HAD BEEN HIDING.** Rule 4's phrase ladder was graded on the RAW query
  with the deleted word still in it, so *"Drywall lift template"* matched no name, drew NO
  bonus at all, and the row actually CALLED **Drywall lift** lost the lead to a longer row
  that beat it on weight — one dropped word MOVING the answer, the exact thing `find-noise`
  N7 forbids, sitting on rows N7 never probed. The honest label is what pointed at it: the
  heading went to "Closest to" and was RIGHT, because the row underneath was wrong. Rule 4 now
  reads the same live query under the same separator gate; **ungated it cost 149 mid-typing
  leads**, which is why the gate is there and not a symmetry argument. · **THE GATE, AND ITS
  TWO NEW CLASSES ARE ONE PAIR:** `find-honesty.mjs` **8,472 checks / 0 failing** (was 6,492).
  Same surface, same engine-proven-absent word, attached to a WHOLE name (**H** — stays exact)
  and to a FRAGMENT of one (**J** — hedges), so nothing about the chrome-ness of the deletion
  can explain the split and only wholeness can. Red-verified by restoring code, not argued:
  **J 0/108** against the pre-change engine, **H 1,402/1,468** against the counting predicate.
  · **BACKPORT RIDER FIRED — the same defect in the gate, not in a sibling trade.** Both
  find-gates capture "the index" by monkey-patching `Find.search` on one keystroke and taking
  whichever ran LAST. **A commons surface builds TWO** — its own rows and
  `commons/commons.js`'s cross-page `handoff.ix` — so on `commons/tips.html` the gate was
  proving words absent from the 135-row alias table while the page under test has 190 rows:
  believed-absent `template, pdf, printable, example, report`, actually absent `pdf, example,
  strap`. It was proving a probe word absent from a page it was not standing on. Both files
  now keep every index seen and take the one holding this surface's own first name — CONTAINS,
  not equals, because `shared/pickfilter.js` indexes a row's whole `<li>` text as its primary
  field, and equality silently skipped all thirteen tap-to-tick lists (caught by firing it).
  **GATES GREEN:** find-honesty **8,472/0** · find-noise **341, 31 surfaces, N0–N9 all ok**
  (was 340 — one more, on the right index) · docs-pool **92/0** · commons-names **395** ·
  commons-bag **530 states** · pickfilter **13 pages / 169** · docspec-needs **1,951** ·
  docspec-say **3,213** · docspec-desk **15 trades / 0** · lang-layer **12 pages** ·
  no-third-party **152/152** · mobile-watertight **152 pages, four widths, both text sizes**.
  **AND RE-DRIVEN AGAINST THE DEPLOYED PAGES, which is the run that counts (C3677's scar):**
  the live `shared/find.js` is byte-identical to HEAD, `find-honesty` **8,472/0** and
  `find-noise` **341** both green on the live base, and **the whole 72,138-search measurement
  returns the identical numbers off the artifact** — unhedged wrong 675, leads 41,194, own
  7,417/7,417, chrome 7,064/7,064, mid-typing 14,762/21,017. The heading QUOTES what he typed
  and rule 6 makes it appear more often, so a 55-character unbroken token was driven into it
  on three surfaces at 320/360/390/430 live: `scrollWidth === clientWidth` at every width.
  **THE PAIR IS VISIBLE ON ONE PAGE:** on live `av/write-up`, *"Damage / Pre-Existing
  Condition Note template "* stays EXACT and names the dropped word, while *"damage note
  template "* — same page, same dropped word, a PIECE of the name instead of the whole — now
  says **Closest to**. And *"punch list reply"* on `gc/write-up`, a document GC's library does
  not carry, went from a confident answer to a hedged one.
  **NAMED NEXT RUNG:** rule 6 only fires when rule 1 deleted something, and **322 of the 675
  remaining (47.7%) dropped nothing at all** — every word he typed is a word of some row's
  name here, at full strength, and no row is CALLED any of it (*"cut in"*, *"pipe wrenches"*
  on `av/write-up` → the Damage Note, exact, empty `noise`). Dropping the `!say.length` guard
  would hedge class F, the word under his cursor, so the rung is to find the condition that
  separates a lead he has HALF-TYPED from one he has NOT NAMED — 322 against 0 of class F.
  **SIGNAL DUTY — the bump pointed at an empty room and I had to re-derive the answer by
  hand.** `STALEST-AXIS SIGNAL = WELL … last worked 7 lane-cycle(s) ago` with both sinks at
  0 new / 0 building: WELL sits in the staleness table like any other axis, so once it is
  stalest it is named every bump until somebody wishes something. `due_axis()` now takes a
  `well_dry` flag, `_lane_well_dry()` reads the board that is ALREADY fetched for the block
  below it (one fenced subprocess, hard timeout, **any failure returns None and changes
  nothing** — an unread board may never be reported as an empty one), and `new`-or-`building`
  is what counts because a claim held by a dead cycle is work, not an empty well. Verified by
  firing it: `due_axis(None) = WELL`, `due_axis(True) = DEPTH`. Paid for under THE PARTITION
  — *"Breadth debt is paid, so the stalest-axis rule now governs"* was the template's own STEP
  0b said twice, and is deleted from the directive. **Template 0 words** (2,053 / 2,081
  ceiling, ALL TEMPLATES RENDER); directive 922 → **937**, +15 for a signal that was wrong
  this cycle.
  Storefront unchanged — no new tool, no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- `2026-08-29` — **[AXIS:DEPTH] C3679 — THE THINNEST KIT ON THE RACK GOT THE PAGE ITS OWN
  REGISTRY HAD BEEN NAMING FOR SIXTEEN DAYS, AND THE PANEL DISAGREED WITH THE ROSTER, WITH
  ITSELF, AND WITH ME.** Both wells dry (0 new, 0 building, 30 shipped, no stale claims) and
  no family owed, so the stalest axis governed — and the bump still printed `WELL` a cycle
  after `due_axis` learned to skip a dry one, so the axis was re-derived by hand off the log:
  DEPTH, 6 lane-cycles cold. **The rung picked itself twice over:** creative is the thinnest
  kit on a fifteen-trade rack (5 tools against a median of 8), `creative/tools.js` has
  carried *"Next off the panel's ranked list: Before I Export"* in its footer since
  2026-08-13, and §CREATIVE calls it *"now the top unbuilt rung on this trade."* **THREE
  LENSES RAN BEFORE A LINE WAS WRITTEN AND NOT ONE OF THEM LEFT THE DRAFT STANDING.** The
  field lens rebuilt the FRAME: a page that asks a client what shape he needs on the night of
  the render *"tells him you cut the whole thing without knowing — that's not diligence,
  that's a confession."* So block one is STATEMENTS and block two is the ask. It killed the
  roster's own sorter too (*"fifteen of twenty-two flagged means nothing is flagged"*) and
  replaced it with the one that costs money: **do I have to open the project again.** **THE
  PANEL SPLIT, AND THE SPLIT IS THE RECORD.** The field lens's favourite block — *free
  tonight, expensive next week*: a clean version, a no-music version, stills, a second shape
  — was killed outright by the boundary lens, because the kit would be handing a freelancer a
  warm, unpriced, WRITTEN offer of four extra renders to his own client, and the page next
  door (*That's Another Round*) exists to clean exactly that up. **It won on the field lens's
  own test**, which had killed *"do you need the project files?"* with *"that's a yes I never
  priced, and this page can't carry a price"* and then failed to apply it one paragraph
  later. What survives is `Everything I've got you down for` — the user stating what is
  ALREADY in his deal, downstream of his own scope document instead of an offer of anything
  new. The safety lens killed a closing line I had not noticed writing (*"anything that lands
  after I render means doing it again"* — a consequence clause in a friendly hat) and caught
  the deemed-acceptance defect this trade already stripped out once, **moved from prose into
  a DEFAULT**: a shape picker shipping `16:9` pre-selected puts a spec in a client's inbox
  that nobody chose. Every axis on the page now opens on an em-dash and every item carries a
  `sayNo` for the row ticked and never answered. **WHAT THE PAGE DOES THAT THE TEN SHAPE-#1
  PAGES BEFORE IT DO NOT: it argues with the user about the length of his own message.** Every
  sibling is trying to get MORE lines onto a list, because a supply house reads lists for a
  living; the receiver here is a marketing manager with forty seconds who has not seen a
  frame. Past five asks the glass says most people answer about five and go quiet on the
  rest; past eight it says this is a form, not a message. **The count never reaches the
  client** — printing it would be the page narrating the user to his own client. **BACKPORT
  RIDER FIRED, ON THE ENGINE AND ON AN INSTRUMENT, BOTH FOUND BY BUILDING:** `countLabel` was
  assembled a line BEFORE the document, so caller code in the CHROME could freeze the PRODUCT
  — the preview sat at *"(nothing on it yet)"* while the list filled up. One line moved in
  `shared/checklist-request.js`; **all 14 shape-#1 pages inherit it and `order-live-header`
  re-ran green on every one** (14 pages, everything in the document on the glass and surviving
  a reload). And `mobile-watertight` failed the new page on two menu rows: **not a new defect
  — that gate samples one tool page per trade ALPHABETICALLY, so a page beginning with "b"
  became the first `creative/` page ever measured with the menu open**, and getting-in has
  carried the same rows since 2026-08-13. **My first fix was a regression and the stacking
  order caught it** (nav z-40 paints OVER the z-30 bar; the panel was never covered) —
  reverted to a zero-line diff, and the real fix went into the GATE, which was probing a row's
  centre one pixel past a scrolling panel's clip edge and blaming the bar for it.
  Red-verified, not argued: a control planted under the bar with no scrolling ancestor still
  fails at four widths in both states. **The module sweep this cycle also RETIRED a standing
  hole rather than paying it:** `package` is not owed on creative — Total Package is a
  wages-and-fringes reckoning and this trade's rails ban rate cards, day rates, kill fees and
  deposit splits outright, which makes it the one absence with a reason. **GATES GREEN:**
  47/47 on a live drive of the real page (neutral axes never leak a placeholder, a
  note-shaped line with no note falls back instead of printing a stub, the flagged write-in
  routes into the ask and counts against it, the clipboard equals the block he proofread,
  everything survives a reload) · mobile-watertight **8/8 creative pages** at 320/360/390/430
  in both text sizes · order-live-header **14 order pages** · pickfilter **14 pages / 182** ·
  menu-reachability **1,050 checks / 150 pages** · no-third-party **153/153** · find-honesty
  **8,472 / 0 failing** · find-noise **352, N0–N9 all ok** (was 341 — the new tool's own rows).
  Storefront: one line added to `creative`'s `tools[]` in `fieldToolkits.ts`, parse-verified,
  P5 pushes it. **NAMED NEXT RUNG:** *What's in the drop*, as its OWN page rather than the
  "second output mode" §CREATIVE deferred it as — the other side of the render, addressed to
  a different moment: who signed, what is in the folder, and what is deliberately not in it.
  https://mrdirno.github.io/nested-resonance-memory-archive/creative/before-i-export.html

- **[AXIS:BREADTH] C3681 (2026-09-01) — THE RACK RAN OUT OF TRADES BELOW THE SAFETY RAIL, AND THE
  SIXTEENTH WAS THE FIRST ONE FOUND OFF IT — FIRST ON ALL FOUR LENSES, VETOED BY NONE.** Both wells
  dry (0 new, 0 building in the AV well and the cards well), no family owed, so the stalest axis
  governed: BREADTH, 6 lane-cycles cold. Ran the standing method in order and it came back EMPTY:
  the gate-vocabulary query over fifteen kits finds no unserved family owning a gate other kits count
  down to ("before tile goes in" is flooring, "before the ceiling closes" is framing, "before we
  insulate" is one mention and killed); the who[] re-tally reads steel 7 · ceilings 5 · hm 2 · survey
  2 · sprink 2 · mill 2 · owner 2 · singletons — every one killed, absorbed, or not a trade. **THE
  COUNT NOMINATED NOBODY, so the shortlist was written to INCLUDE THE COUNT-INVISIBLE** (the roster's
  own instruction since #14) and four independent lenses scored nine candidates: a field hand, a
  population count, the doctrine lens that reads the record, and the boundary lens that reads every
  shipped items.js. **LANDSCAPE & IRRIGATION took first on all four — 92 · 92 · 88 · 78 — vetoed by
  none.** That has not happened on this rack before. FIRE SPRINKLER took its THIRD kill, and this one
  is specific enough to stop a fourth hearing: the NFPA 13 material-and-test certificate's CONTENT is
  printed inside the standard and the NFPA 25 ITM report is numbered inside a municipally-mandated
  third-party portal — all three crossings in one document — and the residue after refusal is the
  boundary pages every trade already ships, "the glazing verdict verbatim." Steel was vetoed twice
  (its NAICS code is concrete's, rebar is served, ~10% micro-shop; the bolt-up log IS the ch.17
  dataset) and the boundary lens found the 7-count merges TWO receivers, the erector and the
  misc-metals welder. Survey vetoed (the product is a seal; "9 kits" collapsed to 3 under a targeted
  grep). Crane vetoed three times ("a date has no inbox"). Restoration vetoed twice (the S500 drying
  log is the standard's content, an Xactimate line and a claim-numbered platform record at once).
  **WHY LANDSCAPE, kept so #17 does not re-derive it:** the count that nominated nobody had measured
  him wrong — THREE shipped kits already built him a receiver chip with no ask behind it (concrete
  `irr` "Irrigation / landscape", sitework `land` + `irr` in what-is-in-the-ditch, gc `landscape`),
  and concrete/items.js carries HIS sleeve sentence — "driveway and flatwork sleeves — irrigation,
  gas, conduit — go in before I set forms" — inside an ask aimed at the PLUMBER, because the man whose
  sleeve that is had nowhere to answer from. Not an orphan ask; a MIS-ROUTED one: the doorprep gap one
  step earlier. The largest unserved population on the board by an order of magnitude (install half
  ~150-250k, nonemployer-dominant, no office — the painting profile), and the doctrine inverse:
  NOTHING upstream numbers what the crew sends. Structural on system-of-record, discipline on
  certified data — "strictly better ground than doors stood on, and doors shipped." SHIPPED WHOLE —
  10 tools: `where-i-cross` (PINNED, row-log — every place his pipe has to get under somebody else's
  concrete before it closes; the sleeve off HIS submittal as a learn axis, how far it sticks out,
  marked, the gate; the only irreversible gate this trade OWNS, because "before the pour" is concrete's
  word and "before backfill" is sitework's and a plant can be dug back out) · `rough-in-request`
  → **Before We Plant** (13 asks · 10 receivers · 9 milestones) · `answer-back` → **Walk Back**,
  whose fourth rung is this trade's own: **"It's the water"** — a dry plant is telling you about the
  clock, not the planting, and that answer lives with whoever holds the controller (reconcile VERDICTS
  position [3], `ask`) · `not-ready-to-plant` (12 stops, the two-button close) · `off-the-truck`
  (what the tag says · where you found it) · `sub-it-or-wait` (their schedule line as an ADDRESS, the
  yard's words, what he can get the way he'd order it — the Color Lock isomorph) · `waters-yours`
  (the handback: what HE set the clock to, copied off the face as free text ON PURPOSE — the moment it
  became fields it would be a watering schedule with our name on it; the code goes by phone, never on
  the note) · `getting-in` · `write-up` (7 own documents, 18 in the library) · `total-package`.
  Commons joined on all THREE surfaces at 8 rows each (five order names on the name table start with
  "Irrigation", and the block says why: head, main, lateral, sleeve, zone, box — not one is his).
  **THE NAME COLLISION IS A RULE:** twelve kits say "sprinkler" and mean fire; the brand word is
  LANDSCAPE, the pages say heads, valves, mainline, laterals, drip, zones and the clock, and the hub
  drive asserts the word is nowhere on the hub. Accent **#A1CB86**, a leaf in daylight — the sweep's
  best numbers across the ENTIRE solid were the muted sage greens (dE 32.6, nav 7.86:1), and the
  argument this time was CHROMA rather than a band: the first muted chip on a rack of fluorescent
  ones, and the eye reads a sage leaf and a neon highlighter as two colours whatever the hue wheel
  says. **THE HARD REFUSAL is 13 items** in trade.js, items.js and docs.js, and the most dangerous
  page anybody will propose is named at stand-up: the spray log (the licensed applicator's state
  record) — never. **GATES CAUGHT TWO OF MY OWN ERRORS BEFORE SHIP:** `getting-in` failed the landscape
  copy twice — the closing said "the hours you're actually giving us" where the gate reads "the
  window you're actually giving us" by regex, and not one heads-up classified as a permitted
  activity until the water shutdown named the backflow VALVE (§SCARS). **BACKPORT RIDER FIRED, TWO
  FINDS, BOTH FIVE DAYS OLD:** the hub-accent sweep (every hub's `:root --flag` against its trade.js
  accent, 16 trades) found `doors/index.html` wearing painting's #29FF29 on its well button and
  eyebrow since C3674 — fixed, and the deploy now asserts it per trade; and the docs writer, copying
  the doors shape, found `shared/docspec.js` reads reminders as STRINGS only, so doors' five
  `{when, say}` reminders had been reaching the pasted block as "- [object Object]" — the emitter now
  renders both forms and `docspec-config` fails on a stringified object (§SCARS, both). FOUR
  MEMBERSHIPS + THE REGENERATED INDEX: deploy TRADES + paths, `shared/toolkit.js` TRADES,
  COMMONS_TRADES, the site-root TOOLS entry (Sprout — the seedling is this trade's brick), and
  `shared/docsindex.js` regenerated to 16 trades · 302 terms. Storefront: one new entry in
  `fieldToolkits.ts`, staged in persona500, P5 pushes; the storefront match binds NARROWLY
  (`landscap`, `irrigation`, `irrigator`, `lawn_install`, `sod_install`, `hardscape`) and
  deliberately excludes `sprinkler`, `gardener` and `groundskeeper`. VERIFIED AT THE ARTIFACT before
  push: a 103-assertion drive that does each page's job (a crossing walked and read back off the
  document, a short line counted, a stop ticked, a substitution lined up, a handback with what he set,
  a pasted punch tapped four times to "It's the water"), mobile-watertight 12/12 pages at
  320/360/390/430 in both text sizes, getting-in, what-came-back (833 checks), note-live-fields,
  rowlog-restore, rowlog-commit-merge, reconcile-surface, reconcile-join (130), boundary-titles (47),
  answer-tapnote (16), commons-names, commons-bag, docspec-config/needs/say/desk, docs-pool,
  find-honesty, find-noise, menu- and overlay-reachability, no-third-party (165 pages, 0 requests).
  **NAMED UNBUILT, at stand-up:** THE YARD ORDER (shape #1, deferred for the window, not doctrine —
  it lights up four shared modules at once; painting/store-call is the page to isomorph) and THE ZONE
  WALK (folded into Water's Yours and the library because a page that logs coverage zone by zone is
  one wish from a coverage verdict — a judged call, not a gap). **THE DEMERITS, written down:** two
  trades in one hat and the kit serves the install half only · a TRUE zero of who[] asks (chips, no
  letters — the no-habit finding one size larger) · one engineered pressure point, and the first wish
  will be "can it work out my run times" (permanently no) · the gate ladder borrowed at both ends.
  Ten HALO-lane commits already on local main rode the push. VERIFIED LIVE after green (deploy
  33588052530, build + deploy success): 18/18 landscape URLs 200 · the 103-assertion drive re-run
  against the DEPLOYED pages, all green · mobile-watertight 12/12 pages against production ·
  doors/index.html `--flag` reads #B7BEDC live and the well button paints rgb(183,190,220) · both
  write-up libraries render their reminders with no "[object Object]" in the block · the commons
  shows 17 chips and "Carson box" typed on the gear list hands off to "He means Valve box" · the
  site-root Tools panel lists the kit (the bundle carries ./landscape/ once, same as ./doors/).
  https://mrdirno.github.io/nested-resonance-memory-archive/landscape/

- `2026-09-01` — **[AXIS:INTERFACE] C3692 — THE ROADMAP RANKED AN AXIS AND A LADDER; THE PANEL
  KEPT THE AXIS, KILLED THE LADDER, AND THE LADDER WAS THE HALF THAT WOULD HAVE SHIPPED A
  DEFECT** · **before:** both wells dry (AV 0 new / 0 building, vibe-cards 0/0, no stale
  claims in either sink this lane draws from) and no family owed, so the stalest axis
  governed — INTERFACE, 6 lane-cycles cold, with exactly one concrete rung left in the book's
  own named remainder: the long-lead **gear chase**, confirmed unbuilt on disk (no
  `gear|lead|chase|expedite|release|submit` page in any of the sixteen trades). The entry
  ranked a *what I'm asking for* axis — ship date · released · dimensions and weight ·
  approved schedules · freight — and a status ladder to carry it. · **A FOUR-LENS PANEL
  SCORED IT 8 / 7 / 8 / 2 AND CHANGED THE DESIGN, NOT THE WORDS.** The commercial EC project
  manager quoted his own sixth email verbatim, four months in, ending *"Please advise."* The
  **receiving desk** — the project-management desk at a distributor, answering from the other
  side with no idea we had the page open — gave the finding the whole build turns on: *"he
  asks the expensive question when he needed the cheap one. Say 'pouring 10/14, need pad dims
  and weight on MSB-1' and you get it this afternoon. Say 'any update' and you wait three
  days for a paragraph."* The sending lens had reached the same shape from the opposite end:
  *"email six braids five questions and the reader answers one — breaking the braid is the
  page's whole job."* **The skeptic scored it 2 and killed the ladder, correctly**: *released*
  and *in fabrication* are not facts the user holds, and rendering one in confident type with
  a settled edge is a clearance manufactured by an interface. · **after:**
  `<trade>/long-pole.html` on **electrical · HVAC · plumbing · doors** — one page file, four
  `TOOLKIT_LONGPOLE` configs, shape #3, **no new mechanism**. The ladder is `Asked → Nothing
  back → They told me something → It's here` and **every rung is his own act or his own
  eyes**; what the factory said lives in `told`, their words with a name on it, never a
  state. **The question is LINE ONE** — the subject line, the only line a lock-screen preview
  is guaranteed to show, which is where the receiving desk said he triages — and the ask list
  is ordered by how fast the answer comes back, cheapest first, which is the page's only real
  intelligence. **`asks[0]` on every kit is *anything you still need from us***, the half
  nobody writes, named independently by both field lenses. And **`told` holds one value and
  keeps no history**, which is the answer to the panel's sharpest kill: a dated repeatable
  "here is what you told me and when" with a TSV export is a delay-claim exhibit, and the
  receiving desk priced it — *"my answers get vaguer"* — so a field holding one sentence
  cannot become one. The word *promised* is banned outright; the field is what he was LAST
  TOLD. HVAC forced **"do not ship before"** (early is laydown storage, insurance and a second
  rig on six thousand pounds) and start-up as its own lead time; doors got the trade where
  *four people inside one house* is literal — detailer, hardware writer, wood plant, glass
  shop — so its fourth ask names the shop. **GC gets it never**, from both field lenses
  unprompted: he owns and numbers the procurement log. · **BACKPORT RIDER FIRED, AND IT FOUND
  A LIVE PAGE LYING TO A RECEIVER.** The defect the gate caught on the new page — a footer
  drawing from every row while the body is filtered — was swept across every filtered row
  log, and **`framing/whats-in-the-wall.html` had it in the worse direction**: scoped to *not
  covered yet* it printed one row, then demanded a size for a piece that was **Covered**, in
  the wall, and **not in the body at all**, so the AV contractor had no line above to argue
  with. A flag does not clear when a row goes in, so it had been asking since the day it was
  covered. `roofing/whats-open.html` was the same rule in the opposite direction — a hazard
  list must NOT narrow — so it took the disclosure branch instead. `creative/still-waiting-on`
  took the redundancy fix the new page taught. **6 filtered row logs, 2 were failing.** ·
  **GATES:** new `long-pole.mjs` **445 checks over 4 trades, 0 failing** — the ladder checked
  against factory verbs per trade, no real house named in any seed, every field found BY VALUE
  in what the real Copy button put on the clipboard, the question proved to print ONCE as a
  subject line and never per row, the excluded questions' lines proved ABSENT, `told`
  overwritten and the previous value proved gone from the message, the spreadsheet copy AND
  storage, Clear proved to take the header and the question with the list, and four widths
  with the 44px floor. New `foot-scope.mjs` **7 checks, 2 were red**. `no-third-party`
  **169/169**. `menu-reachability` **1,162 checks over 166 pages**, tightest clearance 15.5px.
  `row-live-line` **14 order pages**. · **STOREFRONT:** 4 rows added to `fieldToolkits.ts`,
  placement verified per-trade and the file re-parsed with esbuild — P5 pushes it.
  https://mrdirno.github.io/nested-resonance-memory-archive/electrical/long-pole.html

- **2026-09-02 (C3693) · [AXIS:WELL]** · **ONE DOT PER CARD RAN OUT OF PHONE.** The only
  waiting wish in either well was anonymous, four words, from the Vibe Cards landing page's
  own box after an Instagram bio-link tap: *"Fabel 5.1 just released revamp the space!"* A
  **3-judge panel** ran independently. All three agreed on the MEANING — "the space" is that
  landing page encountered cold — and all three scored their own *proposal* at CONFIDENCE 3,
  which is the panel saying nobody knows what was wanted specifically. The adversary's veto
  settled the tiebreak: **no restyle without a falsifiable pass/fail.** Neither of the other
  two proposals had one (a 3D card flip; reordering the h1 above the deck — both logged as
  next rungs with their falsifiers), so the build went to the defect I could measure. ·
  **WHAT WAS BROKEN:** the deck pager drew one 44px dot per card, and the deck had grown to
  15. Measured live at the four gate widths, as **rows the pager occupies**: 3 rows at 320,
  360 and 390px, 2 at 430 — 150px of page — and `.arrow` is `display:none` outside
  `(hover:hover)`, so **on a real phone those wrapped rows were the entire control**: 15
  identical 7px marks you cannot aim at. The page's own CSS had predicted this and named the
  trigger — *"card 008 will not reopen this"*. Card 016 did. · **THE FIX:** one row, forever
  — an `<input type="range">` rail you can drag plus an `03/15` readout. Same width at 5
  cards, at 15, at 60. It gives up sight-jumping (15 identical dots had already taken that)
  and gives back a scrub, a **number the page had never stated**, one labelled control
  instead of 15, arrow keys, and an `aria-valuetext` that names the card it rests on — so the
  deck reads out *better* to a screen reader, not worse. **Two bugs found by DRIVING it, not
  looking at it:** `scrollTo(behavior:'auto')` defers to CSS and `.deck` sets
  `scroll-behavior:smooth`, so released at card 11 the reel was still passing card 2;
  and painting on `change` read where the deck WAS, not where it was going, and dragged the
  readout backwards. One settle per rack, 90ms after the deck last moved, owns it now. A
  third, caught on the live page: the focus ring was drawn round the whole 44px × full-width
  control in the card's own accent — Build Lab's red framed the rail like a rejected field —
  so the halo moved to the thumb. · **THE ADVERSARY'S FIND, SHIPPED WITH IT:** `BUILD-LAB-001`
  was published, registered, given a page and both faces, and **linked from nowhere** —
  reachable only by already holding the printed card. `CARD_REGISTRY.md` step 5 calls `/lab/`
  "the live proof" that nothing checks this. The dot row was *why* nobody added it: a 6th dot
  was a 6th 44px target on a row already wrapping at 320px. It is now card 6 of 6 in the hero
  deck, and the registry step is rewritten to say what is and is not gated. Also fixed: the
  hero's first sentence printed at **x=0.0px** at every width while its neighbours sat at 18.0
  and 19.5 — `header.hero` has no padding and that line was the only child not in a `.wrap`. ·
  **GATES (E1 both ways):** `build_site.py` grows `data-count="deck"`, derived from the card
  figures in the reel above it, not from the registry — **proved to fail** naming the deck when
  the total is wrong. `verify_mobile.mjs` grows a pager check that bands controls by **vertical
  overlap** (a rounded `top` calls a 44px slider beside a 12px line a wrap; the first version
  did exactly that, and a child-level test could not see 15 buttons inside one `div` at all) —
  **8 failures on the live page before, watertight on it after**, all four widths, every page.
  · **BACKPORT RIDER FIRED, THREE CLASSES, ALL CLEAN:** wrapping control strip — no
  `.pager`/`.dots` exists anywhere in the 16 trades, the defect is structurally absent;
  orphaned page — **166 pages across 16 trades swept, 0 orphans** (the registry+hub pattern is
  what prevents it, and is exactly what a hand-written deck lacks); gutter escape — **48 live
  pages at 390px (every trade's hub plus two tools each), 0 flagged**. · **NOT DONE, NAMED:**
  the vibe-cards well has no credits surface, so an anonymous wish is credited only in the
  commit; `/gt/` is the remaining unlinked card and cannot take a slide until it has artwork.
  https://mrdirno.github.io/vibe-cards/

- `2026-09-02` — **[AXIS:DOCS] C3697 — ONE WORD MEANT TWO DOCUMENTS ON 12 SHELVES, AND THE
  MOST OBVIOUS WORD ON THE RACK MEANT THE WRONG ONE ON ALL 16** · **the well was verified
  EMPTY on disk in both sinks** (`av_wishing_well --list` and `--list --status building`, 0
  and 0; vibe-cards likewise) and no family was owed, so the stalest axis governed. ·
  **before:** `shared/docsindex.js` refuses to POOL a term meaning two documents — 35 of
  them, deploy-checked — and that rail sits at the LAST layer of the pipeline, so every layer
  above it looked covered. Measured on the merged shelves instead: **19 ambiguous whole
  terms across 16 trades**, `"damage"` on **12** of them (an alias on `incident-report` and
  on `damage-found`, whose name opens with the word), and — found by a second probe the
  first was structurally blind to — **21 of 1,707 authored aliases, typed whole at the real
  search box, handing back a document their author never wrote them on**, led by `"meeting"`
  on **16 of 16**, eaten every time by *"Toolbox Talk / Safety Meeting Note"* because a NAME
  outranks an alias. **THE MEASUREMENT OUTRANKED THE PLAN, TWICE.** The cycle opened on a
  different finding — doors and landscape are the only two trades with ZERO `overrides`
  — and **driving the real pages killed 8 of the first 10 collisions as non-defects**: on
  masonry, gc and concrete the ranking was already handing back the right document, and a
  fix would have been invented work. The one that survived the drive is the one that
  shipped. · **after: 19 → 0 and 21 → 0, verified at the artifact, and the two fixes with
  the widest reach are one line each.** `incident-report` gives up the bare `"damage"` to
  the document NAMED Damage (12 shelves); the safety note is renamed **"Toolbox Talk /
  Tailgate Note"** — the field's own word, §FIELD-COOL, and it stops the name eating an
  alias on 16 shelves. Then per-shelf: **roofing DROPS the shared `handover`** — the second
  drop in the program and the first where a shared document is displaced by a DOCUMENT
  rather than by a shipped tool (creative's was the first); it was not an opinion, the drive
  showed `"turnover"`, `"closeout"` and `"handover"` each returning BOTH, generic first, on
  the shelf where the roofer's own one was written for him — with the one demand the shared
  document made that `roof-turnover` did not carry (**what physically changed hands**:
  warranty paperwork, maintenance instructions, spare material, to whom, when) folded in as
  a new section rather than lost, and all four of its orphaned aliases carried over, because
  **dropping a document may not drop its words**. `framing` takes **masonry's** fix that
  nobody had carried across — renaming the inherited notice (**"We're Waiting On Somebody"**)
  so it stops opening on the same three words as *"We're Held Up (and the wall can't
  close)"*. Plus five aka trims where a name owned a word: gc `dig-in`, plumbing `call
  notes`, concrete `damage`/`cold`/`stopped`, electrical `write up`, sitework `plan`,
  roofing `pre-existing`/`trouble call`/`service call`. · **THE RATCHET:
  `tools/toolkit-gates/docs-shelf.mjs`**, all of it derived from the shipped engine and each
  shelf's own data so a document added next month is covered the day it lands: **A** no whole
  term resolves to two documents · **B** every authored alias, typed whole at the REAL box,
  LEADS its own document (the half A is structurally blind to — nothing is ambiguous when a
  name eats an alias outright) · **C** every `drop` names a real shared id, and the words a
  drop takes off the shelf are COUNTED and printed rather than failed, because only a person
  can tell roofing's drop (document displaced by document — **0 dark**) from creative's
  (displaced by a shipped TOOL — **18 dark, on purpose**). **PROVED BY NEGATIVE CONTROL:
  `--prove` re-authors the defect out of each shelf's own data and both detectors go RED on
  16/16.** · **THE BACKPORT RIDER FIRED AS THE FINDING ITSELF** — the sweep across all 16
  shelves is what produced the two rack-wide defects, and both were fixed in the SHARED
  library in one line each rather than 12 and 16 times. · **THE FIX PAID AT THE LAYER
  BELOW:** with the authoring ambiguity gone the pool stopped refusing — **302 → 304 pooled
  terms, 35 → 33 refusals**; `"damage"` is now lent to all 13 trades holding `damage-found`.
  · **GATES, all green:** shelf **16 trades / 1,701 checks / 0 failing** (negative control red
  16/16, both detectors) · docspec **16 / 264 / 0** · find-honesty **8,958 / 0** · docs-pool
  **98 / 0** · mobile-watertight on all four changed write-up pages at 320/360/390/430 ×
  default and bumped, **0 failing** · roofing driven end to end at 390px: shelf 14 documents
  with the shared handover gone, block **12,740 chars**, the folded section and every line of
  it in the pasted output, 0 overflow, 0 page errors · `shared/docsindex.js` regenerated so
  the deploy's `--check` cannot diff. **Storefront unchanged — no new tool, no new trade.**
  **THE RENAME BROKE A DOCUMENTED BEHAVIOUR AND THE SWEEP FOR STALE COMMENTS IS WHAT
  CAUGHT IT — no gate could have.** `shared/find.js`'s header cites this very document as
  rule 4's worked example (*"safety is the Toolbox Talk / Safety Meeting Note even though
  the Incident Report answers to that too"*), and taking *"Safety Meeting"* out of the name
  to stop it eating `"meeting"` also took **"safety" out of a TITLE**. Measured on five
  shelves: `"safety"` flipped to the Incident Report. The shelf gate is structurally blind
  to it — `"safety"` is nobody's authored alias, so there was nothing to probe. **An outcome
  that was reasoned about once does not get to change as a side effect of a different fix:**
  `"safety"` is now DECLARED on the document rather than bought with a word in the name we
  do not want, restored on all five re-measured shelves, `"meeting"` still reaching the
  minutes. Both of that comment's worked examples had also quietly stopped being true — the
  other one because this cycle retired the tie it described — and both are rewritten with
  the history intact. **A comment that names a behaviour is a claim, and it rots silently.**
  · **NAMED AND NOT DONE, so it is not lost:** `doors` and `landscape` are the only two trades
  on the rack with **zero `overrides`** — every other one of the 14 re-addresses between 1
  and 8 of the 11 shared documents, and those two inherit all 11 in the rack's generic voice.
  That is the next DOCS rung, and it is the 2026-08-15 roster lesson again: nobody asks a new
  trade what it was OWED. https://mrdirno.github.io/nested-resonance-memory-archive/roofing/write-up.html

- `2026-09-03` — **[AXIS:BACKPORT] C3699 — THE SHARE SHEET NOW SITS WITH COPY ON 117 PAGES OF
  16 TRADES, AND THE CYCLE THAT BUILT IT NEVER SHIPPED IT** · **the well was verified EMPTY on
  disk in BOTH sinks** (`av_wishing_well --list` and `--list --status building`, 0 and 0;
  vibe-cards the same), no family owed, so the stalest axis governed and it was BACKPORT. ·
  **before:** every page on this rack ends the same way — the document goes to the clipboard
  and the man leaves to find the thread, long-press, paste. C3698 built the one-tap version of
  that door and then stopped: the helper in `shared/toolkit.js`, one line in each of six
  engines, four hand-written pages, a 349-line parity gate, a deploy assertion and a change to
  the mobile ship gate — **all of it uncommitted**, under six hours old, invisible to every
  rail we own because every rail we own watches the ARTIFACT and the artifact is downstream of
  a commit (§SCARS 2026-09-03). Its source header cited `§THE PANEL, C3698` and `§SCARS
  C3698`; grepping this book for `C3698` returned **zero hits**. · **after:** VERIFIED, then
  shipped — the first act was to re-run the gate from zero rather than believe a header
  claiming it had passed. `tools/toolkit-gates/send-is-copy.mjs`: **117 pages mount Send · 17
  excluded by name (the 16 write-up shelves + `av/report-builder`, whose receiver is an AI chat
  box) · 0 pages with a Copy path and no decision · 297 parity pairs with the document actually
  MOVING on 148 · 5,199 checks · 0 failing.** 117 + 17 = **134**, which is exactly the tool
  count the registry claims. **NEGATIVE CONTROL run, not assumed:** `--prove` hands the sheet
  the copy text plus one character and goes RED on both placement classes and on the
  three-Send page (`getting-in`) — 2, 2, 1 and 6 failures where green had been. · `mobile-watertight` **169 pages at 320/360/390/430, default and bumped text — 0 failing**, with `navigator.share` stubbed PRESENT by default so the fixed bar is measured in the state a phone is actually in rather than the one headless Chromium is in (`TK_NO_SHARE=1` measures the desktop-Firefox state). The 6 soft field-height reports are all on `av/report-builder.html`, which mounts no Send — pre-existing and untouched ·
  `no-third-party` **169 pages, 0 third-party requests** — Send is `navigator.share`, so the
  document never leaves the phone. · **A NON-FINDING, measured rather than waved off:** the
  runtime styles Send from `var(--flag)` and `var(--cond)`, and an undefined custom property
  drops the whole declaration silently; a grep suggested ~100 pages never define `--cond`. The
  browser settled it instead — Send and Copy compute to the SAME `Arial Narrow` on every
  sampled page and Send carries each trade's own accent (roofing `#FF93C9`, plumbing
  `#C87137`, masonry `#B9EE1B`, painting `#29FF29`, sitework `#FFDDA3`, av `#F0BE1E`), 44px on
  all. The grep was scoped wrong; measuring cost two minutes. · **THE BACKPORT RIDER IS THE
  SHIP:** one refinement, landed once in the shared library, reaching all 16 trades at once —
  and the placement is a decision the runtime makes PER PAGE (fixed-ness read off computed
  style, never guessed from a class name), because C3698 measured the naive version killing
  the fixed bar on 25 of 50 pages at 320px. · **NOT SWEPT IN, and named so it is not lost:**
  `.github/workflows/toolkit-gates-and-e2e.yml` has sat untracked since 2026-08-25 — the same
  half-shipped state as the feature above, one layer up, and it is the very rail that would
  have caught it. It GLOBS `tools/toolkit-gates/*.mjs` (no hardcoded roster, so it ages well),
  but shipping it means turning every push in this repo red if any of the **34** gates on disk
  is currently failing, and that has not been measured. **Run all 34 green first, then commit
  it** — shipping an unverified rail is the exact mistake this cycle scarred. · **Storefront
  unchanged** — no new tool and no new trade; Send is a capability of 117 existing ones. ·
  **THE OPEN QUESTION THE PANEL LEFT, and it is countable:** one of three lenses scored this a
  **3**. Send and Copy are two doors to the same document — the CHOICE §THE EVO LOOP exists to
  instrument — and nothing counts which door gets used. That is the named next rung; until it
  is counted the dissent stands unanswered. · **VERIFIED ON THE LIVE ARTIFACT, not on the tree.** The deploy printed its own new assertion — `send: runtime helper present, 6 engines register it` — and the whole gate re-run against the deployed site returns the IDENTICAL line: **117 mount · 17 excluded · 297 parity pairs · 5,199 checks · 0 failing.** Before this cycle the live `shared/toolkit.js` matched `ToolkitSend` **zero** times. https://mrdirno.github.io/nested-resonance-memory-archive/plumbing/supply-house-order.html

- `2026-09-03` — **[AXIS:COMMONS] C3700 — THE WORD HE FINISHED TYPING WAS TREATED AS ONE HE
  WAS STILL ON, AND 453 WRONG ANSWERS RODE OUT THROUGH THE GAP.** The named COMMONS rung said
  the remaining lie lived where *nothing* was dropped, and cited *"pipe wrenches"* on
  `av/write-up` as its example. That query DROPS A WORD. `shared/find.js` would not name a
  trailing token until a separator arrived — right, while the word could still be in progress
  — but `say` empty ALSO makes rule 6's clause vacuous, so the answer went out labelled
  **exact** with no sentence at all. Rule 6 did not leave a hole beside itself; it left the
  door it stands in unlocked. · **MEASURED FIRST, RUNG WRITTEN SECOND: 41,516 searches on 33
  surfaces.** 3,181 answers were exact only because the hold-back had emptied `say`; the 623
  unhedged-wrong decompose **453 hold-back · 124 nothing-dropped · 46 past rule 6 on a real
  name**, not the 322/47.7% the book had written down. · **THE THRESHOLD IS EVIDENCE, NOT
  TASTE:** at one character `tokenScore()` has no prefix path (the real flicker window), at
  three both prefix and infix are live, so a three-character trailing token that matched
  NOTHING begins no word and sits inside no word anywhere in the library — a word this page
  does not have, not a word in progress. `var UNDER_THUMB = 3`, one clause, nothing else
  touched. · **BEFORE → AFTER: unhedged-wrong 623 → 172**, diffed query by query rather than
  totalled — **759 newly hedged, 0 newly UNhedged, lead row moved 0 times in 41,516
  searches**; verbatim 586/586, alias 864/864, mid-typing **12,813/12,813**, whole-name-plus
  -chrome 248/248 on the libraries and 60/60 on the commons. The 451 was PREDICTED from the
  baseline run through the engine's exported `wholeName` and then RETURNED by the patched
  engine's diff — **two paths, one number**. · **THE CANDIDATE THAT LOST IS ON THE RECORD:**
  RUN (a contiguous whole-word run inside one name) was written into the engine, measured at
  31 of the 124 nothing-dropped class for **24 mid-typing keystrokes**, and TAKEN BACK OUT
  against a pre-registered bar of zero; BAG (any order) sees 17. · **BACKPORT RIDER FIRED, and
  structurally — one engine, every surface that loads it.** Asserted rather than assumed: the
  451 distribute **198 document libraries · 217 tap-to-tick lists · 36 commons**, and all 33
  surfaces were driven. · **GATE:** `find-noise.mjs` N9 + N10 are ONE PAIR either side of the
  engine's own `Find.underThumb`, red-verified by restoring code — at 99 (old behaviour) N10
  fails on 33 surfaces, at 0 N9 fails on the same 33, at 3 **GREEN 396 checks** (was 363).
  `find-honesty.mjs` 8,973 checks 0 failing, unmoved. · **THE SCAR THIS CYCLE EARNED:** the
  first N10 read the constant to decide WHETHER to run, so reverting the engine made the class
  VANISH and the file printed GREEN — a probe may read a constant to choose what to TYPE, never
  whether to RUN. · **THE NAMED NEXT RUNG IS BIGGER THAN WHAT WAS LEFT:** rule 6 is
  structurally blind on the tap-to-tick surfaces, because `shared/pickfilter.js` indexes the
  whole `<li>` text as its one primary field and `wholeName()` can never be true there — class
  H is **8/280 exact on pick against 248/248 on the libraries**, so **272 false hedges** on the
  shape rule 6 was written to leave alone. It is a field spec, not a predicate, and it moves
  ranking on fourteen surfaces, so it ships with its own lead-movement diff or not at all. ·
  **ALL 34 GATES RUN THIS CYCLE: 33 green on `file://`, and the 34th
  (`rowlog-commit-merge`) green too once served — its red is `ERR_CONNECTION_REFUSED` on
  127.0.0.1:8777, an environment requirement, not a defect.** That answers C3699's open
  condition for shipping `.github/workflows/toolkit-gates-and-e2e.yml` and finds the reason it
  would STILL fail: the gates job globs every gate but starts no static server, so that one
  gate needs a server step (or a served default) before the rail goes on. Left untracked
  deliberately — shipping it unmeasured is the exact mistake C3699 scarred. · **Storefront
  unchanged** — no new tool, no new trade; this is a correctness fix inside the engine that
  134 registered tools already load. · **VERIFIED ON THE LIVE ARTIFACT, not on the tree:**
  `find-noise.mjs` re-run against the deployed site returns the identical **GREEN 396 checks**
  with N10 present, and the live page answers *"pipe wrenches"* with *Closest to "pipe
  wrenches"* + *Ignored "wrenches" — nothing here uses that word*, while *"damage n"* stays
  silent and *"daily field repo"* stays exact.
  https://mrdirno.github.io/nested-resonance-memory-archive/av/write-up.html

- `2026-09-03` — **[AXIS:DEPTH] C3702 — THE ROADMAP NAMED THREE PARTS FOR THE DELIVERY
  NOTE AND THE PANEL TOOK TWO OF THEM AWAY, INCLUDING THE ONE THAT WOULD HAVE PUT A
  CLIENT'S NAME ON AN APPROVAL RECORD.** · **before:** both wells dry (0 new, 0 building,
  toolkit and cards) and no family owed, so the stalest axis governed — DEPTH, 7
  lane-cycles cold, last worked C3679. The rung picked itself twice over, the way the last
  DEPTH cycle's did: creative is still the thinnest kit on a sixteen-trade rack (6 tools
  against a median of 8.5), and *What's in the drop* was named as the next rung in
  §CREATIVE item 4, in `creative/tools.js`'s footer, and in C3679's own closing line.
  · **after:** `creative/whats-in-the-drop.html` — 7 tools, the twelfth instance of shape
  #1, and **the first page on the rack that asks its receiver for nothing at all.**
  **THE PANEL SCORED IT 7 / 6 / 2 AND ONE LENS VOTED TO KILL IT.** What the dissent bought,
  in order of size: **"WHO SIGNED OFF" IS NOT A BLOCK** — the receiving lens ranked it
  above the deemed-acceptance clause as the riskiest thing in the proposal, because
  *"Approved by [name] on [date]" is a signature*: typed by one party, and the moment the
  client forwards it into a thread with a boss in it, the OTHER party's name is on an
  approval record that exists nowhere else. It survives as ONE header field in the
  sender's own first person, printed AFTER the lists rather than under the heading (read
  first it puts the receiver in auditor mode before he has opened a file), and never
  without the invitation to correct it. **The word "approved" appears nowhere on the page
  and the drive asserts it, along with "deliberately"** — *"nobody says deliberately about
  something they're volunteering; you say it when you're pre-empting a complaint"* — and
  *per scope*, *not included*, *exclusion*, *business days* and *as discussed*. **THE
  SIBLING'S ASK-COUNT BRAKE DID NOT COME ACROSS:** this page asks for nothing, so there was
  nothing to count, and the working editor named porting it as cargo-cult. What it brakes
  instead is **THE FENCE** — it counts absences against inclusions and says on the glass
  when the message has stopped being a delivery and started being a list of upsells, in
  three states (all-absence, parity, and past five). Never in the message. **AND THE
  DISSENT'S GROUND IS THE PAGE'S GROUND:** a transfer page already lists the FILES; nothing
  anywhere generates **ABSENCE**. The skeptic called that *"the one inch of real
  territory"* and the working editor called it *"drop that line and this is just a
  nicer-looking here-you-go"* — two lenses agreeing on what to build while disagreeing
  about whether to build it, which is the strongest signal this exercise produces.
  **BACKPORT RIDER FIRED, AND IT IS THE NEW PAGE'S OWN RAIL TURNED INTO AN INSTRUMENT:**
  `tools/toolkit-gates/no-clock.mjs` drives every page on disk carrying a `#preview` —
  every checkbox on, every field marked, every select moved off its default — and reads
  the DOCUMENT for a verb with legal weight attached to a timer or to silence. It reads
  the artefact and not the source on purpose: this toolkit's teaching prose is full of
  that vocabulary correctly (`cut-note` warns a man in as many words that silence reads as
  agreement), and a source-matching gate would fail the pages doing the right thing.
  **130 documents driven, 0 carrying a clock — and the CONTROL is the finding**, not the
  green: the first planted clause fired red on two patterns, the second landed by accident
  inside `plumbing/items.js`'s `tag_es` and **the gate stayed green on a page that was
  carrying it.** Twelve bilingual pages hold a second document behind `toolkit.lang` that
  it had never opened. Every one is now driven twice and the failure names the tongue;
  re-planted in a row the ES document renders, it goes red on `[es]` while the EN twin
  stays green. **THREE SCARS WRITTEN:** an append that matched an end-anchor it had already
  passed, duplicating 338 lines and assigning one key twice while `node --check` stayed
  green and the page served the older draft (found by reading item names off the DOM, and
  the fix is `grep -c`, not a new tool) · the book contradicting itself inside one section
  for five days, because A ROADMAP IS NOT A RECORD covers striking a rung that SHIPS and
  not a deferral that is REVERSED · and **a lens handing my own prompt back as a
  citation** — the kill verdict cited §THE SYSTEM OF RECORD as naming *"a delivery
  receipt"*, which it has never contained; one grep settles it, a panel cannot self-detect
  it, and the conclusion only survived because a second lens reached it independently.
  **RECONCILED RATHER THAN BUILT:** §CREATIVE's owed BACKPORT rung — the 153×16 tool link
  on `credits.html` — has been exempt in `mobile-watertight` since 2026-08-10 under the
  WCAG 2.5.8 inline-target rule, whose selector list names `.credit`. Page, gate and
  standard agree; only the book disagreed. Recorded as a decision, with the condition
  under which it would be built. **GATES:** the new page driven end to end at 390px,
  **32/32, and re-driven against the DEPLOYED artifact for the same 32** · order-live-header
  OK (5 header controls, 5 in the document) · pickfilter 13 assertions · mobile-watertight
  **local 169 pages and live on the new one**, 320/360/390/430 × both text sizes ·
  menu-reachability **1,169 checks / 167 pages** · find-honesty **8,973 / 0 failing** ·
  find-noise **408, N0–N10 all ok** · foot-scope 7/7 · no-clock **130 / 0**. Storefront:
  one line in `creative`'s `tools[]` in `fieldToolkits.ts`, parse-verified — P5 pushes it.
  **NAMED NEXT RUNG:** the PARTICIPANT half of Shoot Day Confirm — the short "how the day
  goes" note to talent or a client coming to set. Every one of this trade's seven tools
  points at a payer, a venue or the next editor; nothing points at the person who has to
  SHOW UP.
  https://mrdirno.github.io/nested-resonance-memory-archive/creative/whats-in-the-drop.html

- **[AXIS:BREADTH] C3706 (2026-09-04) — THE SEVENTEENTH TRADE WAS SITTING HALF-REGISTERED IN THE
  WORKING TREE WITH NO VERDICT ON DISK, AND THE PANEL THAT WAS NEVER CAST CONFIRMED IT — FIRST ON TWO
  LENSES, SECOND ON TWO, VETOED BY NONE.** Both wells dry (0 new, 0 building, AV well and cards
  well), no family owed, so the stalest axis governed: BREADTH, 7 lane-cycles cold. `git status`
  found what the RE-GROUND step is for: C3705 had died mid-cycle with `paving` already added to
  `shared/toolkit.js` TRADES, `commons/commons.js` COMMONS_TRADES and the deploy's TRADES list,
  plus a credits stub in `paving/` — no hub, no tools, no panel, no roster line, uncommitted. That is
  the §STEP 0 "claimed by a cycle that died" shape applied to a TRADE, and the fork was finish or
  release; neither was taken on the stub's word. **THE PANEL RAN FIRST** — four independent lenses
  (field hand · population/frequency · doctrine · boundary), nine count-invisible candidates, every
  factual claim cited path:line and grep-checked (§THE PANEL): **PAVING & STRIPING 70 · 70 · 62 ·
  78 — first on population and boundary, second on the other two, vetoed by none (sum 280)**, over
  EXTERIORS (siding · gutters) 74·57·58·52 (the field hand's first) and FINAL CLEAN 47·36·70·54
  (doctrine's first); plaster/stucco and solar each took one veto, tree service took two. NOT
  UNANIMOUS, AND THE TWO DISSENTS ARE THE DESIGN: doctrine's 62 named "the kill-in-waiting — the ADA
  stall count near the centre of his layout page", so the pinned page quotes the SHEET as an address
  and HIS TAPE and carries no count, dimension, slope or accessibility call of its own; the field
  hand's second place is the office on the paver half, so the kit speaks to the foreman and the
  owner-operator. **THE BOUNDARY EVIDENCE is the landscape finding one trade later:** the only
  candidate with a receiver chip AND a letter already written to it — landscape/items.js:329
  `Paving / striping` and :358 "Walk my sleeves before the base rolls" (who: paving, by: pave,
  "once it's paved it's a saw cut — and an argument") — plus sitework's ORPHAN chip `Paving /
  base` (:268, nine asks and none to him), low-voltage's "Pipe out to the gate before paving"
  aimed at the EC (:369), electrical's "Saw cut and patch the asphalt" (:492); "before you pave"
  (landscape/items.js:342) is the one irreversible gate word on the site rack that a shipped kit
  counts down to and no hub owned. **A LENS CORRECTED THE BRIEF:** my candidate notes said
  insulation was on seven kits and exteriors on four; the doctrine lens re-grepped and found three
  and ONE (hvac's hits are line-set insulation, framing's soffit is interior, concrete's gutter is
  curb-and-gutter). Recorded in the roster so #18's brief counts with a structured tally or says
  the number is a guess. **SHIPPED WHOLE — 9 tools:** `doesnt-fit` (PINNED, row-log — one row per
  place the striping sheet and the lot disagree: the spot in his words, what the sheet draws
  QUOTED, what his tape found, what's in the way, the decision he needs; Sent · Answered · Painted
  as answered; three of four lenses independently named this page as the one no other hub could
  write) · `under-the-mat` (row-log — the letter back to landscape, LV, the EC and sitework:
  everything somebody else has under his base before it rolls, who told him, whether he saw it in,
  the iron to grade, the gate) · `rough-in-request` → **Before I Roll** (12 asks · 10 receivers ·
  7 milestones, incl. "the lab on site the day I roll — the density number is theirs, not mine")
  · `answer-back` → **Walk Back**, whose fourth rung is this trade's own: **"It's the plan"** — a
  stall count, an arrow, an accessible pair the owner wants moved is a plan question that lives
  with the civil, not with the man holding the striper (reconcile VERDICTS position [3], `ask`) ·
  `not-ready-to-pave` (14 stops with the ask under each, the FIX / PAVE close) · `lot-closed-tonight`
  (the closure note: which section, which night, when cars come back in HIS words off HIS sheet,
  the tow list is theirs, the fire lane stays open — the process handed back on every line) ·
  `getting-in` (9 needs · 11 heads-ups · 4 permitted-activity handbacks asserted) · `write-up`
  (7 own documents, 18 in the library, 17 dictation corrections) · `total-package`. Commons joined on
  all three surfaces at 10/10/12 narrow rows (the one collision the commons gate found and the
  builder fixed: "risers" folded to plumbing's supply-line riser — the iron is "manholes" now).
  Accent **#FDF37A** — the first pale lemon on the rack (nav 12.60:1, dE 29.1 to av's gold, above
  doors' 28.9; the argument was BAND, the colour of a fresh stripe on new black). **THE NAME
  COLLISION IS A RULE:** "paver" on this rack is masonry's brick; the brand word is PAVING, the
  surface is THE MAT, and the hub drive asserts "pavers" is nowhere on the hub. **THE HARD REFUSAL
  is 12 items** in trade.js, items.js and docs.js; the most dangerous wish is named at stand-up:
  "just put the ADA number in" — permanently no. **VERIFIED AT THE ARTIFACT before push:** a
  103-assertion drive (`tools/toolkit-gates/_drive_paving.mjs`) that does each page's job — a run
  laid out and read back off the document with the sheet as its address, a crossing logged, a stop
  ticked, an ask ticked on the closure note, a pasted punch tapped four times to "It's the plan",
  the walk surviving a reload — and the first run's four FAILS were the drive's own: it banned the
  word "landscape" from the glass and the receiver chips legitimately say it, and it read
  "Before I Roll" case-sensitively against an uppercase h1 (fixed in the drive, not the page);
  mobile-watertight 13/13 pages at 320/360/390/430 in both text sizes; the full toolkit gate suite green (33 gates over the working tree, plus the mobile gate on the three commons surfaces; rowlog-commit-merge wants a local server on :8777 and passed against one); a deploy-assert
  simulation (registry hrefs, local deps, --flag = accent, panel-tools link, TRADES, chip, narrow
  rows) green; a two-lens ADVERSARIAL AUDIT — a refusal reader over every string (1 fix, 4 notes, all applied: donor "establishment period", a tenant named by habit in a privacy example, an acceptance claim in the foreman's mouth, "your own plant ticket" as his source, "rolls the base" on the card) and a field driver that did every page's job at 390px (267 of 292 steps passed; the real failures were the round trip and five copy/persistence defects, every one fixed — see BACKPORT). FIVE MEMBERSHIPS + THE REGENERATED INDEX: deploy TRADES + paths (the dead
  cycle's lines, kept), `shared/toolkit.js` TRADES (kept), COMMONS_TRADES (kept), the front-page
  Tools panel card AND the classic TOOLS entry (TrafficCone — a cone is gear), and
  `shared/docsindex.js` regenerated to 17 trades · 303 terms. Storefront: one entry in
  `fieldToolkits.ts`, staged in persona500, P5 pushes; the match binds NARROWLY (`paving`, `asphalt`,
  `sealcoat`, `striping`, `parking_lot`) and excludes `pavers`, `hardscape`, `highway`, `dot_`.
  **BACKPORT RIDER: FIRED, FOUR RACK-WIDE FINDS, none of them paving's alone (§SCARS ×2): (1) reconcile split the answer at the FIRST dash and every trade's own asks carry one — fixed in the engine, a real-vocabulary control added to reconcile-join (135 → 217 checks); (2) the request page's areaLabel/phArea override ran before the mount and had been dead on all sixteen kits since the engine shipped — the bar now reads the trade's words at mount, and paving's bar says "Section / area", "What exactly", "Where on the section"; (3) the row logs lost their job header on reload — persistExtra on paving's two and landscape's two; (4) the measured pair on the four not-ready pages printed his reading and the sheet's callout as two bare lines under one heading — docLabels on doors, landscape, painting and paving; and the pronoun rung "In — I saw it" is no longer lowercased on where-i-cross or under-the-mat.** **NAMED UNBUILT, at stand-up:** THE LOAD LOG (the plant ticket is
  the numbered record; a tally of tickets is one wish from a yield verdict — a judged call) · the
  DAY RATE / T&M ticket (electrical's engine; deferred for the window) · THE LANGUAGE LAYER (Not
  Ready to Pave is the first Lang.vocab candidate — the striping crew is heavily Spanish-speaking).
  **THE DEMERITS, written down:** two hats and often two companies in one chip · the layout page is
  one careless wish from a count table · the paver half has an office more often than the striper.
  Private roster: PAVING section written, #17's own "by the standing method" paragraph resolved,
  #18's shortlist recorded (exteriors, final clean, insulation). VERIFIED LIVE after green (deploy
  33946700134, build + deploy success, commit 27b6fc15): 16/16 paving URLs 200 · the 104-assertion
  drive re-run against the DEPLOYED pages, all green · mobile-watertight 11/11 pages against
  production · the front page carries the card · the commons shows 18 chips and the paving chip · the
  paving write-up shelf serves 18 documents with the pool defined · the hub's switcher lists 17 others
  and never itself · and the backport is on the glass: landscape/rough-in-request.html reads "Bed /
  area" in production for the first time since it shipped.
  https://mrdirno.github.io/nested-resonance-memory-archive/paving/

- `2026-09-05` — **[AXIS:INTERFACE] C3707 — THE CLOSE-IN LIST'S OWNER-VENDOR RECEIVER WAS ONE
  BUCKET FOR FIVE COMPANIES, SO THE GC KIT GOT THE PAGE THAT NAMES THE MAN** · **before:** both
  wells dry (AV well 0 new / 0 building, vibe-cards well 0 / 0), no family owed, so the stalest
  axis governed — INTERFACE, 7 lane-cycles cold, with exactly one unserved rung on the private
  matrix: the owner's vendors, "the most expensive miss on any close-in list" (kitchen, signage,
  EVSE, owner AV/FF&E showing up after the pour asking where their stub is). RE-GROUND found the
  rung was a STUB, not unserved: `gc/rough-in-request.html` already aims one ask ("Vendor rough
  points") at a receiver called *Owner vendor / rep*. That is the call a panel exists for. ·
  **A FOUR-LENS PANEL SCORED IT 7 / 7 / 7 / 5 AND THE 5 WAS NOT A KILL.** A GC super (build), the
  PM at a foodservice equipment contractor answering from the RECEIVING end (build), an owner's
  rep holding the OFCI matrix (build), and a skeptic armed with this book (EXTEND the Close-In
  List — *"I went to kill it and the page is mostly already built"*). All four named the same
  one thing first: *Owner vendor / rep* is one slug, and one list to the cooler guy, the hood guy
  and the sign guy is a list to nobody. The skeptic was right about every MECHANISM and wrong
  about the JOB — a piece keyed to a company outside the contract who has to TELL the super
  something, with a different ladder, closing, a named receiver, a cc'd rep and a per-send gate
  day the sub-facing page must never carry, is a second tool by §FIELD-COOL's own line. His cut
  decided two things anyway: the gates are `TOOLKIT_ROUGHIN.milestones` read at load, and the
  Close-In List's vendor ask stays exactly as it was. · **after:** `gc/by-others.html` — **By
  Others** (every lens's first name for it), a config on shape #3, **no new mechanism**. The
  typed vendor name is the receiver, learned, NEVER seeded (zero chips asserted); a message
  never goes to more than one of them (the other vendor's name and rows proved ABSENT by value).
  The owner's rep is cc'd — he has no contract with the kitchen guy, and the text has weight only
  with her on it — and is the To: for pieces with no name yet: the roll-up *what your vendors
  still owe me*, by vendor, the nameless under their own heading, one ask on those (*who's your
  person, and a day to walk it — the name is the whole ask*), which the super called the message
  that actually moves the date. **THE RECEIVING DESK CHANGED THE ASKS:** "tell me where it lands
  and what it needs" killed as the lead (*"my equipment schedule retyped into a text — I'll say
  it's on the drawings and stop answering"*); the ask that gets a PDF in an hour is *send me the
  rough-in sheet you already sent the architect — sheet and rev*; cheapest first by his own
  timings, the service list LAST for the piece with no sheet; pieces by their tag off the
  equipment schedule (K-4, OF-14) and the owner's room number — *"the first GC document that
  reads my numbering back to me."* **THE GATE'S DAY** is typed once at send time as a fact on
  line one (*slab pours 9/12*), on no row, never counted from — a deliberate exception to "a
  milestone, never a date" for a receiver outside the population, asked for by three lenses; and
  NO send date on line one (the super killed *"Sep 5 hanging off the subject with no noun"*).
  **KILLED, GATED:** "Nothing back" (a lateness label in a status, nobody's act) · "on the owner's
  schedule, not mine" (who-eats-it with the dollar sign filed off — all four) · the "moves the
  date" flag (the opening line of a delay exhibit, printed to a vendor) · "when you set it" (the
  owner tells him; no close-in gate — the long pole in a hat) · copier / vending (no gate) ·
  med-gas outlets / access control in the seed (pre-decides a furnish-vs-install fight) · "core
  drill" in the SENT document (*"forwarded as 'your GC is threatening me' — lands on the wrong
  man"*; it stays in the page's own copy to the super). Ladder `Asked → Got it → It's in`, blank
  is *not sent yet*; `told` one value, no history. · **BACKPORT RIDER FIRED — a sweep, not a
  fix:** every kit's `rough-in-request` receivers grepped for the owner class; 9 of 17 carry one,
  and all but GC's are the OWNER himself (property manager · homeowner · owner's rep — one party,
  correctly one bucket); sitework's *Owner / owner's vendor* is the only other mixed one and its
  asks to it are owner asks. The "one bucket, five companies" defect was GC's alone; no sibling
  changed, and the page stays GC-only because the sub's path to the owner's vendor runs through
  the GC. · **VERIFIED AT THE ARTIFACT, and the artifact bit twice before the gate was green:**
  new `tools/toolkit-gates/by-others.mjs` **198 checks, 0 failing** — static bans over the config
  (no factory verb, no "nothing back", one flag with no schedule word, the killed asks absent,
  the sheet asked before the paragraph, the closing carrying sheet-and-rev · whose-is-it · the
  half nobody writes, no gate list of its own, no no-gate seed, no real house incl. the kitchen /
  EVSE / signage / furniture houses, no claim word) and a 390 drive (two vendors + a nameless row
  + a row already in; Dave's message carries only Dave's open rows by tag with the rep cc'd and
  the set named; the day on line one and on no row; Lou's the mirror; the roll-up with all four
  open, by vendor, nameless under NOT SET; his own record with today; `told` overwritten in
  message · spreadsheet · storage; the ladder to the top and one past; reload; Clear taking the
  rep and the day; four widths, 44px). Its first run blew the stack (§SCARS: setFilter from
  onChange) and its first drive found the page dead at mount (§SCARS: the guard was in the
  comment); a drive with the placeholder's own words then found two more the gate's values hid
  (the cc tag printed twice; "asked" on every row to the vendor) — fixed and asserted. Sibling
  suite green over the working tree: mobile-watertight (1 page · 4 widths · both text sizes),
  no-third-party 182/182, menu-reachability 1,253 checks over 179 pages, foot-scope 7,
  long-pole 445, boundary-titles 50, row-live-line 15, send-is-copy 5,621, no-clock,
  overlay-reachability, rowlog-restore 52/53, reconcile-join 217, answer-tapnote 17,
  getting-in 17. · **SHIP:** commit `7eff753b` — and the first attempt at it took 81 of another
  lane's staged files off the shared index (§SCARS: "by pathspec" means `git commit -- <paths>`);
  undone soft, redone clean. **THE DEPLOY THEN DIED IN ANOTHER LANE'S NEW GATE:** run 33953336199
  failed in `halo-validation / instrument` (their `tests/halo` smoke.js, exit 2 after 351 s on a
  GPU-less runner) and SKIPPED build + deploy — the whole public site unpublished behind a physics
  instrument's browser test. Unblocked in `20b62dcc`: `build` no longer `needs:` that job; it
  still runs and reports on every push, it no longer decides whether seventeen trades ship. Fleet
  alerted (#17508). **LIVE-VERIFIED, run 33953911044 (build success · deploy success · HALO job
  still red on its own merits):** `gc/by-others.html` 200 and byte-identical to HEAD, `items.js`
  and `tools.js` the same, the hub registry carrying the entry; **the 198-check drive re-run
  against PRODUCTION, 0 failing**; mobile-watertight against production, 4 widths, both text
  sizes, 0 failing. · **STOREFRONT:** one row in `fieldToolkits.ts` under gc (8 tools), the file
  re-transformed with esbuild and the row found — P5 pushes that repo. **ROSTER:** the owner's
  vendors struck with the panel record; INTERFACE has, for the first time, nothing the matrix
  names — the next rung on this axis comes from a wish or the EVO loop. **SIGNAL DUTY:** 0 words
  cut from the template this cycle — every line changed what this cycle did (the panel, the
  rider, the gates, the pathspec rule).
  https://mrdirno.github.io/nested-resonance-memory-archive/gc/by-others.html

- `2026-09-05` — **[AXIS:DOCS] C3708 — THREE TRADES SPOKE IN A VOICE THAT BELONGED TO
  NOBODY, AND THE WORD THE FOURTH ONE TOOK BACK WAS RETURNED TO HIM BY SIXTEEN STRANGERS**
  · **the well was verified EMPTY on disk in both sinks** (`av_wishing_well --list` and
  `--list --status building`, 0 and 0; vibe-cards likewise), no family was owed, so the
  stalest axis governed and C3697 had already NAMED this rung: doors and landscape carry
  **zero `overrides`**, inheriting all eleven shared documents in the rack's generic voice.
  · **The census on disk said the rung had grown while nobody was looking: THREE trades, not
  two** — `paving` landed in C3706 with zero as well, which is the 2026-08-15 roster lesson
  for the third time: nobody asks a new trade what it was OWED. · **FIVE FRAMINGS WERE
  MEASURED AND FOUR DIED AT THE REAL PAGE, WHICH IS THE POINT.** A vocab-canon voice probe
  (170/183 "silent") was junk — 51 of its hits were on documents that ARE overridden. A
  short-word reach probe said 22 of 83 trade-authored documents were unreachable; driving
  the box killed it, because `seal`, `base`, `cones`, `frames`, `hang` and `ruts` all LEAD
  their own document at rank 1 and the engine substring-matches into a sentence-shaped
  alias perfectly well. A body-index probe found 4,454 words — and its own top examples were
  `"unlike"`, `"almost"`, `"audible"`, which is `shared/find.js` rule 5 explaining why prose
  is not identification. An id-subject probe found 27 and 25 of them were id grammar
  (`"writeup"`). **The shelf search survived every one of them, including the custom path:
  a mason typing `CMU` is told "Nothing matched that" and offered "not in the list", which
  is honest and is the designed graceful failure.** · **after: 3 trades at zero → 0, and
  nine documents now written in the trade's terms** — doors gets the callback on an opening
  (opening number, hand, the hardware set by function, and *whose it is* — warranty, abuse
  or building movement, with what you read at the frame), keys and cores (the control key
  and who signed for it, which is the line that gets a door man called back to every lock in
  a building), and doors damaged after hanging (the accept date and the found date against
  one opening number, because a door man hangs early and everybody works past his openings
  for months); landscape gets the day it becomes theirs (**the date the warranty starts and
  who is watering from it** — a plant warranty is void unwatered and the fight is always
  about which day), the warranty call read AT the plant, and the pre-plant look-ahead
  (nursery lead time and tag/hold status, and whether there is water at the point of
  connection); paving gets the renamed general notice, the final turnover (**cure and
  traffic in DATES, not durations** — power-steering scars on an August mat), and the
  pre-pave look-ahead (**who sends the closure notice to the tenants, and by when**).
  · **ONE OF THE NINE WAS A MEASUREMENT, NOT A JUDGEMENT, AND IT OPENED A RACK-WIDE HOLE.**
  Typing `"delay"` on the paving shelf returned the generic notice and NOTHING ELSE — "The
  Day We Couldn't Pave" never appeared — while doors and landscape both showed theirs second
  because their authors happened to write the word into a sentence. Moving it masonry's way
  **failed the shelf gate**: the word still led the generic. Removing `"delay notice"` too
  did not fix it. **The word was coming back from the POOL** — sixteen other shelves had
  voted `"delay"` onto `delay-notice`, and `shared/docsindex.js` is generated from the SHARED
  documents alone, so every trade-specific document is invisible to the thing lending words
  onto the page it lives on. **A trade's author was being overruled on his own shelf by
  trades he will never meet.** · **THE RATCHET: A CLAIM BEATS A LOAN.** `poolTerms()` reads
  what the whole merged shelf's own authors claim and refuses to lend a word another document
  there already owns (a term claimed twice is left alone — that is the shelf gate's
  assertion A). The pool gate gains assertion **9**, which catches the CAUSE rather than the
  symptom the shelf gate sees downstream. Measured before the fix: **1 case rack-wide**, the
  one this cycle created — so this was a latent trap, not a live defect, and it fired on the
  very first attempt to do what this rung asks. · **THE NEGATIVE CONTROL FOUND A HOLE IN MY
  OWN GATE** — assertion 9 was green on its first run AND green with the engine guard backed
  out, while the shelf gate went correctly red beside it, because it read the engine's own
  answer from a position where that object had not been filled yet. Written up in §SCARS.
  Corrected: guard off → red, guard on → green. · **GATES, all green:** shelf **17 / 1,893 /
  0** (negative control red 17/17, both detectors) · pool **17 / 121 / 0** · docspec **283 /
  0** · needs **2,240 / 0** · say **3,696 / 0** · desk **0** · find-honesty **9,607 / 0** ·
  find-noise **420 / 0** · mobile-watertight **0 failing** on all three changed write-up
  pages at 320/360/390/430 × default and bumped. Paving driven end to end at 390px over
  http: `"delay"` leads the paver's own document, block **18,752 chars**, the renamed general
  notice **13,219** carrying its seasonal-window line and "first asked", **0 page errors**,
  no overflow. Pooled vocabulary regenerated **303 → 340 terms** (ambiguous refused 35 → 37).
  **Storefront unchanged — no new tool, no new trade.** · **THE BACKPORT RIDER FIRED TWICE:**
  the zero-override sweep is what found paving (C3697 had named only two), and the pool fix
  landed in the SHARED engine once rather than on three shelves. **NAMED AND NOT DONE:**
  `hvac` is now the thinnest shelf on the rack at **1** override, and `refrigerant` — typed
  on the HVAC shelf, whose leak document's id literally opens with the word — still answers
  "Nothing matched that" and hands back Coordination Meeting Notes, because the word is in
  nobody's name or alias. That is the next DOCS rung.
  https://mrdirno.github.io/nested-resonance-memory-archive/paving/write-up.html
