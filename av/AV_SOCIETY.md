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

Keep the boundary or the config rots: `trade.js` = IDENTITY + COPY · `tools.js` =
REGISTRY · `items.js` = that trade's VOCABULARY DATA (categories, size ladders, config
options, unit-of-issue sets). Size ladders and C×C/FIP/no-hub live in data — never in the
identity config and never inline in a tool page.

## SCARS — what went wrong, so it does not go wrong twice
Append here when a cycle finds one. Each is a rule, not a story.

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
