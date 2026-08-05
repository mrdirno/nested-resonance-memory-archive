# COLLAGE STUDIO — EVOLUTION DOCTRINE (→ CapCut, iteratively)

The evolvable "book" for the P0 **🎬 COLLAGE** lane (added to the operator app
2026-08-03). Read it FIRST every collage cycle; UPDATE it every collage cycle.

## NORTH STAR
Collage Studio becomes a **CapCut-level photo/video editor**, reached by an
EVOLUTIONARY LOOP — **one shipped, verified capability increment per cycle**,
compounding. Not a rewrite; a ratchet. Operator directive 2026-08-03: *"get to
CapCut level eventually iteratively… an evolutionary loop like society world and
the trading desk."*

## THE LAW (anti-theatre — mirrors vault CLAUDE.md §1.6.6)
A cycle PASSES only on a capability that is **SHIPPED AND VERIFIED LIVE** — not a
plan, not a refactor, not a doc. Name the capability, its before→after, and the
proof (a passing e2e against production + a visual/functional check). Re-deriving
or re-documenting an existing capability is DD, not delivery.

## CURRENT STATE (update every cycle)
- **Stack**: React 18 + TS + Vite; a framework-free Stage canvas compositor
  (Carmack frame-budget, one `<video>` per clip, decoder-economy admission);
  offline WebCodecs export + audio mix; PWA.
- **Repo**: github.com/mrdirno/nested-resonance-memory-archive · tool at
  `tools/collage-studio` · **Live**:
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/ ·
  **Deploy**: GitHub Actions `deploy_bridge.yml` → Pages artifact.
- **Shipped**: 23-generator generative layout roster; source-first duplicate-free
  fill (fragment count = # uploaded photos/videos, a video = ONE source); live
  video compositing; offline export WITH sound; video-length sync
  (loop / stretch-to-longest / speed-to-shortest), live and in export;
  COMPOSITION — 11 arrangements (photo metric x fragment spatial key, zipped)
  and 5 crop-focus modes, both rolled by the dice and carried in the share code.

## THE CAPABILITY LADDER (→ CapCut — GROW this list as you learn)
Each cycle pick ONE rung by **leverage × feasibility** (what a real editor reaches
for most, vs build cost). Mark shipped ones `[x]`; add rungs as you find gaps.
- [ ] **Timeline & trim** — a real timeline UI: per-clip in/out trim, drag-reorder,
      playhead scrub, split/cut. (The single biggest CapCut gap.)
- [ ] **Transitions** — cross-dissolve / fade / wipe / slide between clips/scenes.
- [ ] **Text & titles** — text overlays, fonts, animated titles / lower-thirds;
      later, auto-captions from the audio track.
- [ ] **Keyframes** — animate position/scale/opacity/rotation over time (Ken Burns).
- [ ] **Adjustments & filters** — brightness/contrast/saturation/temp, LUT filters.
- [ ] **Audio** — multi-track mix (partly done), volume envelopes / ducking, fade
      in/out, a music track, beat-sync.
- [ ] **Speed** — per-clip speed ramps / freeze frames (video-length sync is step 1).
- [ ] **Overlays** — stickers, shapes, picture-in-picture, masks, chroma-key.
- [x] **Composition** — WHICH photo lands in WHICH fragment (11 arrangements) and
      WHAT each fragment centres on (5 crop-focus modes). `lib/composition.ts`.
- [ ] **Twist** — per-fragment ROTATION of the image inside its cell. Asked for in
      the same wish as Composition and deliberately NOT bundled with it: rotation
      is the first change that has to reach the hot draw loop (`stage.ts`) AND
      `renderer.ts` AND `render.worker.ts` AND `vectorExport.ts`, so it is its own
      increment with its own pixel proof. Cells TILE the canvas, so rotating the
      cell is wrong — rotate the SAMPLING inside the clip path and expand the dest
      rect by |cos|+|sin| or the corners open up.
- [ ] **Composition presets** — an arrangement is currently one chip; the pairings
      that read best (metric x key) are a bigger space than the 11 named ones.
- [ ] **Templates & export presets** — one-tap templates; aspect presets 9:16 / 1:1
      / 16:9; platform sizes; resolution/bitrate choice.
- [ ] **UX** — deeper undo/redo, robust project save/load, mobile-first touch editing.

## THE PER-CYCLE LOOP (burn → build → verify → ship → ratchet)
0. **PICK ONE RUNG** (entry condition, first). One line naming the capability. Or
   the honest one-line `no ship — <reason>`.
1. **RE-GROUND** — read this file + `git log --oneline -8` + the SCARS below.
   Confirm the rung is not already shipped (if a *reported bug*, diff the DEPLOYED
   bundle before re-reasoning — the fix has repeatedly been written and not shipped).
2. **BUILD watertight** — pure logic in its own module with a unit sweep (seeds ×
   inputs — transpile the REAL module via esbuild and assert invariants, never a
   copy; see `fill.ts` / `videoSync.ts` + their `tests/unit/*.invariants.mjs`).
   UI wired minimally. `npx tsc --noEmit` clean.
3. **VERIFY AT THE ARTIFACT** — a Playwright e2e that drives the REAL UI and
   asserts the capability, run against the collage dev server on **:5199**
   (NEVER :5173 — that is Persona 500). Then `npx vite build`.
4. **SHIP** — commit BY PATHSPEC (shared index — never `git add -A`),
   `git push origin main`; the Actions deploy runs — watch it green.
5. **VERIFY LIVE** — re-run the e2e with
   `COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/`.
   A 200 is not a render. For anything subtle, an adversarial Workflow audit
   before ship (it has caught real bugs — twice, on 2026-08).
6. **RATCHET** — update this file: mark the rung `[x]`, add newly-found gaps, and
   append a cycle-log line at the bottom.

## QC GATES (fab-lab watertight — non-negotiable)
`tsc --noEmit` clean · a unit sweep for any pure algorithm · e2e on :5199 for dev
and `COLLAGE_BASE_URL`=production for the live proof · commit by pathspec (the
deploy artifact IS the whole site; staging order matters) · an adversarial
multi-agent audit for non-trivial changes.

## SCARS (carried from the 2026-08 build — add to this)
- Fill/count reckon in **SOURCES**, not assets (a video = 1 source, however many frames).
- Playwright's default `baseURL` is **:5173 = Persona 500** — always pin :5199 /
  `COLLAGE_BASE_URL`, and `curl` a dev server's identity before trusting it.
- The deploy is an Actions **artifact** (`upload-pages-artifact`); anything outside
  it 404s silently — assert the entry points exist.
- WebCodecs `description` differs per engine (WebKit vs Chrome); `decodeAudioData`
  refuses `.mov`.
- **Realtime capture BAKES IN the stall** — render offline, timestamp from frame INDEX.
- `exportLimits.ts` (1,490 lines) is committed but **UNWIRED** — MAX still-export
  hangs on the owner's phone. A live defect, not dead code.
- **Key one list off the OTHER list's length and you silently lose data.** The
  first `arrangeBag` keyed its fragment ranks off `cells.length`, but the fill
  allocates `max(count, layout.length)` slots, so the tail has no geometry: the
  rank list came back short, `out[slotOrder[i]]` wrote to `out[undefined]` — which
  does not throw — and a photo vanished from the collage while another appeared
  twice. Caught by the permutation invariant, not by looking. Any zip of two
  rankings must take its length from the SLOTS, never from either input.
- **A picker whose entries render the same picture is a lie in the UI.** The
  sweep asserts every arrangement (a) moves the order and (b) differs from every
  other one. Two chips with one behaviour is a defect, not a duplicate label.
- **Family-gating starves the roster.** Conditioning the dice's arrangement HARD
  on the layout family sent 9/24 generators to one group and 4/24 to the other,
  so half the roster came up ~1% of the time. Bias, don't gate: 0.8/0.2, and
  assert the spread in the sweep.
- **The tabs are labelled `Layout` / `Settings`, not Simple / Advanced** — an e2e
  written against the internal state names finds no button and times out.
- `shuffleTrigger` co-seeds the fill RNG but isn't persisted — Restore reproduces
  a layout's geometry, not its exact shuffled arrangement (fix = persist it in the
  save schema; do NOT fold into `seed`, that breaks shuffle's "shapes stay put").

## THE RATCHET (perpetual by construction)
When a capability tier reaches broad parity with CapCut, the north star raises:
the next tier (pro effects, AI-assisted editing, collaboration) becomes the
frontier. Today's ceiling is tomorrow's floor.

## CYCLE LOG (append one line per collage cycle — capability · before→after · proof)
- 2026-08-03 · lane created · source-first fill + video-length sync already live · next rung: **timeline & trim**
- 2026-08-04 · **[AXIS:WELL] export stopped lying** (wish d88093af, reported by the owner:
  *"when I hit export sometimes it will show a black screen… partial elements of the collage
  appeared but it failed to export full image"*). Root cause was not missing logic — it was
  logic that existed and was never called. `lib/exportLimits.ts` (1,490 lines, 57 passing
  self-tests, a comment predicting this exact black-JPEG bug) was imported by nothing.
  THREE real defects, all now closed: **(1) BLACK** — over a platform's canvas ceiling
  `new OffscreenCanvas()` does not throw; it returns a valid, correctly-sized, entirely black
  JPEG. The worker now writes a sentinel to the far corner and reads it back before drawing
  AND after (WebKit can discard a live surface mid-render), reports `surfaceLive:false`, and
  the ladder steps down instead of handing over the black file. **(2) PARTIAL** — the preview
  draws `previewSrc`, the export drew `src`, so a source whose original object URL was dead
  rendered perfectly in the preview and vanished from the export; the worker now falls back
  to the preview source and only counts a fragment failed when BOTH are gone. **(3) THE
  OUT-OF-BOUNDS the report guessed at** — `orderedImages.map(img => ({src: img.src…}))` had no
  null guard, so a short fill bag threw *while building the worker message*, was caught as
  "worker unavailable", and silently re-rendered on the main thread where holes are skipped.
  Export now walks a ladder derived from a MEASURED device ceiling, validates every blob
  before accepting it, and a failure says which tier and why instead of showing the word
  "error". before→after: 0 → 68 unit cases (`composeTiers` extracted + swept, 11 new) and
  3/3 artifact-level e2e reading the exported PIXELS (`tests/e2e/export-integrity.spec.ts`),
  because every failure in this report produces a file that looks fine to a check that only
  asks "did an image appear?". https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-05 · **[AXIS:COLLAGE] composition — which photo goes where, and what it centres on**
  (wish 253b1ba7, anonymous: *"More unique algorithms and sorting capabilities like the color
  match… cropping algorithms for what to center on. Anything arrangement and composition wise
  to create more variation in the dice"*). before→after: **1 ordering → 11 arrangements**, and
  **1 fixed crop rule → 5 crop-focus modes**, both rolled by the dice and carried in the share
  code. The idea that made it more than a longer menu: an arrangement is **not a sort of the
  bag**. It ranks the PHOTOS by a metric and the FRAGMENTS by a spatial key and zips the two,
  which is what turns "by hue" into *the colour wheel wrapped around the canvas* (`wheel`), and
  what makes `hero` — the strongest photo in the biggest fragment — expressible at all. Hue is
  ranked CIRCULARLY, starting the run at the widest empty stretch of the wheel, so the seam
  falls where this set of photos has no colour instead of at red. Focus is per-SLOT, not per
  photo, so one photo in three fragments can show three different parts of itself (`wander`);
  it re-points `analysis.face` on a per-slot copy, which every one of the four crop paths (live
  Stage, static renderer, export worker, vector export) already reads — one seam, four
  consumers, zero changes to any of them, and `auto` returns the original object by reference
  so the default path allocates and recomputes nothing. The share code grew two base-36
  characters INSIDE its middle group and `decodeRoll` reads them only when present, so every
  code already sitting in a chat log still opens. `Colour resonance` — a binary wearing a
  percentage, where only the 10% threshold did anything — is gone; a project saved with it
  above threshold loads as `flow`. **Proof:** unit sweep `tests/unit/composition.invariants.mjs`
  (8 invariant families over 11 arrangements × 5 focus modes × 7 pool shapes × 40 seeds, plus
  4,000 dice rolls for roster spread — it caught the `out[undefined]` photo-loss and a legacy
  share code that would not decode) · `tests/e2e/composition.spec.ts` 4/4 on the real UI,
  asserting PIXELS: Spotlight pulls the bright end of a luminance ramp to the centre, Eclipse
  turns it inside out · regression 7/7 source-count + 3/3 export-integrity + `tsc` clean.
  **Mobile ship gate, now a test rather than a habit:** `tests/e2e/mobile-watertight.spec.ts`
  drives 320/360/390/430px and three zoom-outs, asserting `scrollWidth <= clientWidth` and a
  44px floor on every control — it found SIX pre-existing sub-44px targets (three canvas
  buttons at 40×40, both bottom tabs at 42, the frame-picker switch at 29) and all six are
  fixed. Credit ledger isomorphed from `av/credits.json` → `tools/collage-studio/credits.json`,
  and the credit is ON the page. NOT shipped from this wish and named on the ladder with its
  reason: **twist** (per-fragment rotation) — it is the first change that must reach the hot
  draw loop and all three export paths, so it gets its own increment and its own pixel proof.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
