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
  and 5 crop-focus modes, both rolled by the dice and carried in the share code;
  TWIST — 5 per-fragment rotation modes (the picture leans, the tiling does not),
  reaching all four render paths through the one geometry function they share.

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
- [x] **Twist** — per-fragment ROTATION of the image inside its cell. 5 modes
      (Straight / Tilt / Scatter / Pinwheel / Cascade), on the dice and in the
      share code. `composition.twistAngle` + `renderer.twistedDest`. The advance
      note left here was right on both counts: the cell is never rotated (only the
      SAMPLING inside an untouched clip path), and the dest grows by |cos|+|sin| or
      the corners open up. What turned four changes into ONE seam was carrying the
      angle on the per-slot `analysis` — the channel crop focus already rides.
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
- **An export that rebuilds its own asset list will silently drop whatever the
  preview added.** `renderAtSize` and `handleExportSVG` each re-derived
  `shuffledIndices.map(idx => images[idx])` instead of reading `orderedAssets`,
  so the per-slot crop focus never reached the worker or the SVG: the preview
  re-framed and the downloaded file came out at the old anchor. The VIDEO export
  was fine, because it samples the Stage — so one composition exported two
  different ways. Second occurrence of this exact class (the first was
  previewSrc-vs-src). RULE: there is ONE draw order, `orderedAssets`; an export
  that builds its own is a bug waiting for a release.
- **A deterministic pairing makes Shuffle a dead button, silently.** An
  arrangement's output is a function of the SET of photos plus the geometry, so
  re-ordering the bag — which is all Shuffle does — changed nothing at the
  default count (one slot per upload). Since the dice sets an arrangement on
  ~80% of rolls, a user could press Shuffle forever with no feedback and no
  visible control explaining why. Fixed with a bounded re-deal INSIDE the
  ranking (`reDeal`, composition.ts).
- **A "windowed" Fisher-Yates is not windowed.** `for i = n-1 down to 1, swap
  with something in [i-w, i]` compounds: an element swapped down gets picked up
  again when the cursor reaches its new home. Measured 36/40 slots of drift for
  a window meant to be 6. Jitter-and-resort (add <= w/2 to each rank, re-sort)
  caps displacement at w by construction.
- **Measure a re-deal where it is VISIBLE, not in array indices.** Adjacent
  RANKS map to spatially adjacent CELLS whose bag positions can be at opposite
  ends of the array, so a one-rank nudge reads as a 34-slot "move" while
  changing almost nothing on screen. The honest invariant is slot-by-slot metric
  correlation against the exact ranking.
- **Preview-only e2e cannot see an export defect** — the crop-focus split passed
  4/4 pixel-level preview tests. Any capability that must survive to a FILE needs
  a test that drives the export and compares the two. Prove the test fails on the
  reintroduced bug before believing it.
- **Rotating the CELL is the obvious move and it is wrong.** The fragments TILE
  the canvas; rotate a cell and you open wedges of background between it and its
  neighbours. The rotation belongs to the SAMPLING inside an untouched clip path
  — the hole stays put, the picture leans. And the moment you do that you owe the
  cover: a w x h rect rotated by t no longer contains the axis-aligned w x h cell,
  so the destination must grow to w|cos t|+h|sin t| by w|sin t|+h|cos t|. Skip the
  growth and the identical gap reappears four pixels inward, where it is harder to
  see and easier to ship. Proved by geometry (79,200 corner containments) rather
  than by looking, and the sweep was watched going RED with the growth removed.
- **A grown destination changes the ASPECT, so the cover fit has to be recomputed
  against the grown box.** Fitting the crop to the CELL aspect and drawing it into
  the grown rect squashes every twisted fragment — a defect that reads as bad
  photography rather than as a bug, which is exactly why it needs an invariant
  (`sw/sh === dw/dh`) instead of an eyeball.
- **`deg` is a promise, so jitter may only go DOWN.** `tilt` jittered its magnitude
  symmetrically about its declared peak, which put 20% of fragments past it. The
  spec field is what the crop-in is computed from, so exceeding it is not a
  cosmetic overshoot. Caught by the budget invariant on the first run, not by
  looking at the picture — at 10.8 degrees instead of 9 it looks completely fine.
- **A save() pushed inside a `try` must be popped OUTSIDE the `catch`.** The Stage's
  live-video branch wraps `drawImage` in a try/catch because a dying decoder must
  not kill the frame. Put the twist's `ctx.save()` and `ctx.restore()` inside that
  block and a thrown decode leaks one save per frame: the transform accumulates
  and the whole surface shears a little more every frame, forever. The push goes
  before the try, the pop after the catch, so every path is balanced.
- **An angle keyed off the SLOT INDEX silently re-rolls when the arrangement
  changes.** Slot order is draw order, which `arrangeBag` re-pairs — so an
  index-keyed tilt pattern is a different pattern under every arrangement, for no
  reason a user could see. Key the field off WHERE the fragment is instead, and it
  survives re-pairing (`scatter` is the deliberate exception).
- **A field mode built on a raw angle has a seam at ±π.** `pinwheel` from a plain
  theta ramp tears across the 9 o'clock line: two touching fragments differ by
  2·max. `sin(theta)` closes the field on itself, and the sweep asserts the largest
  step around a full ring stays under a quarter of the peak.
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

- 2026-08-05 · **[AXIS:COLLAGE] the adversarial audit earned its keep — two HIGH defects at the
  seams, both live, both closed.** The pure module was sound (`tsc` clean, every invariant
  holding, 4/4 pixel e2e) and *the defects were still there*, because both lived where the new
  module met old code. **(1) THE EXPORT LIED.** `renderAtSize` and `handleExportSVG` each
  rebuilt their own asset list from the raw pool instead of reading `orderedAssets`, so the
  per-slot crop focus never reached the worker or the SVG: pick Wander, watch every fragment
  re-frame, download a PNG cropped the old way. The MP4 export was correct the whole time
  (it samples the Stage), so one composition exported two different ways — second occurrence
  of the previewSrc-vs-src class. **(2) SHUFFLE WENT DEAD.** An arrangement's output is a
  function of the SET of photos plus the geometry, so re-ordering the bag — all Shuffle does —
  changed nothing at the default count, and the dice sets an arrangement on ~80% of rolls. The
  fix is not to weaken the ranking but to draw a different sample from it: a bounded re-deal
  seeded by `shuffleTrigger`, same idea that makes two rolls of one recipe siblings. Writing
  it exposed a third bug of my own — a "windowed" Fisher-Yates is not windowed (an element
  swapped down gets picked up again when the cursor reaches it; measured 36/40 slots of drift
  for a window meant to be 6), replaced with jitter-and-resort which caps displacement at `w`
  by construction. Also fixed: unclamped `cy` degrading every radial arrangement to a y-sort
  for one frame during an aspect change, and row bucketing derived from the FILL count rather
  than the grid, which mis-banded the ramp when cells were locked. before→after: **20 → 24
  invariant/e2e assertions** — 2 new invariant families (`3b` re-deal, `3c` locked-cell
  banding) and a preview-vs-export test proved to go RED on the reintroduced defect before
  being believed. The lesson worth keeping: a preview-only test suite cannot see an export
  defect, and a green pure module says nothing about its seams.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-05 · **[AXIS:COLLAGE] twist — the picture leans, the tiling does not** (the
  half of wish 253b1ba7 that last cycle deliberately did not ship: *"Also maybe twisting
  capabilities…"*). before→after: **every fragment square → 5 twist modes** (Straight, Tilt,
  Scatter, Pinwheel, Cascade), rolled by the dice, carried in the share code, live in all four
  render paths. The rung was deferred because rotation "has to reach the hot draw loop AND
  renderer AND render.worker AND vectorExport" — and the thing that made it ONE change instead
  of four was noticing the seam crop focus had already found: every path reads its geometry
  from `calculateSmartCrop`, and `calculateSmartCrop` reads `analysis`. So `withTwist` writes
  the angle onto a per-slot COPY of the analysis and all four paths steer with no new parameter
  threaded through any of them; the only per-path edit is the four lines that actually rotate.
  The geometry is the load-bearing part: the cells TILE, so nothing rotates a cell — the clip
  path stays exactly where it was and the SAMPLING inside it leans, with the destination grown
  by |cos|+|sin| so the corners cannot open up (`renderer.twistedDest`, one definition, two
  callers). Modes are FIELDS over the canvas, not per-photo attributes, keyed off where the
  fragment SITS rather than its slot index — so choosing a different arrangement does not
  silently re-roll the tilt pattern, and `pinwheel` uses sin(theta) so the swirl has no tear at
  the ±π seam. **Proof:** `tests/unit/twist.invariants.mjs` — 10 invariant families, **79,200
  corner containments**, plus minimality (a 0.5% smaller rect must FAIL to cover), no-stretch,
  hostile-angle clamping, and a bit-identical untwisted path; it caught `tilt` jittering 20%
  past its own declared peak on the first run. `tests/e2e/twist.spec.ts` 3/3 desktop AND 3/3 at
  393px, reading PIXELS: every chip moves the picture, no two chips are the same picture, solid
  white tiles show no background leak, and the exported FILE matches the twisted preview rather
  than the straight one. **Both artifact tests were watched going RED on the reintroduced
  defect before being believed** — T2 with the expansion removed, T3 with the export ignoring
  the angle (it reported "matches the STRAIGHT preview (32.6) better than the twisted one
  (54.5)"). Regression: composition 5/5, source-count 7/7, export-integrity 3/3,
  mobile-watertight 5/5, fill + videoSync + composition sweeps clean, `tsc` clean, `vite build`
  clean. Credit appended to `credits.json` and on the page.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
