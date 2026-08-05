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

Keep the boundary or the config rots: `trade.js` = IDENTITY + COPY · `tools.js` =
REGISTRY · `items.js` = that trade's VOCABULARY DATA (categories, size ladders, config
options, unit-of-issue sets). Size ladders and C×C/FIP/no-hub live in data — never in the
identity config and never inline in a tool page.

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

## SCARS — what went wrong, so it does not go wrong twice
Append here when a cycle finds one. Each is a rule, not a story.

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
