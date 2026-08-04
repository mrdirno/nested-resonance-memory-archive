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
1. **Cable-types picker** — HDMI / Cat patch / fiber → a clean cable spec to the PM. (operator's example)
2. **Gear checklist by room type** — huddle / conference / boardroom / classroom → the kit to pull.
3. **Rack elevation / build note** — RU heights + gear → a rack elevation spec.
4. **Connector & adapter finder** — "source X → display Y, what adapter/dongle?"
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

## THE RATCHET
Each granted wish widens coverage of the real AV workflow. When a whole category is
covered, the toolkit trends toward the default field-AV utility layer, and the
open request/spec formats it standardizes become infrastructure others build on.

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
