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
  reaching all four render paths through the one geometry function they share;
  ONE LAYOUT — every render path (preview, Stage, video, raster export, SVG)
  draws ONE partition at four sizes, generated once at a 1200-space basis and
  scaled, instead of four partitions generated independently.

## THE CAPABILITY LADDER (→ CapCut — GROW this list as you learn)
Each cycle pick ONE rung by **leverage × feasibility** (what a real editor reaches
for most, vs build cost). Mark shipped ones `[x]`; add rungs as you find gaps.
- [ ] **Timeline & trim** — a real timeline UI: per-clip in/out trim, drag-reorder,
      playhead scrub, split/cut. (The single biggest CapCut gap.)
- [x] **ONE LAYOUT** — the preview's partition IS the export's. `computeLayout`
      now runs the generators once at a canonical basis (1200-space = `PREVIEW_W`
      = the Stage's `DEFAULT_LOGICAL_W`) and SCALES the result to whatever size
      the caller draws at. `lib/layoutScale.ts` (`basisFor` / `scaleLayout`); the
      old body is kept, unchanged and exported, as `computeAtBasis` — the oracle
      the sweep measures the historical divergence against. The compatibility
      decision: at the preview both scale factors are exactly 1 and `scaleLayout`
      returns the input array untouched, so every existing seed, project and
      share code renders BIT-IDENTICALLY and only the exports move — onto the
      picture the user was already looking at.
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
- [ ] **Reopening an exported .svg is a silent no-op** — `loadFromSVG`
      (`lib/project.ts`) parses the embedded JSON_MANIFEST and then returns
      `null` unconditionally, so the file input advertises `.svg` and does
      nothing with it. Entirely pre-existing; small, self-contained, and it is a
      promise the UI already makes.
- [ ] **A seed the user can pin** — nothing in the UI sets `seed` (it is
      `Date.now()`), so no test and no user can reproduce a specific composition
      on demand, and the known-flaky composition precondition has no way to stop
      being seed-dependent. `encodeRoll`/`decodeRoll` already exist in
      `diceRoll.ts` and are wired to NOTHING; a paste-a-code field would make
      share codes real and pin the flake at the same time.

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
- **A normalised coordinate is the same NUMBER at every width and not the same
  FLOAT.** `1200/0.666` gives cy = 0.49999999999999994 where 4094 gives exactly
  0.5 — geometrically identical cells, one ULP apart. Any step or singularity
  keyed on those coordinates then answers differently per render width. Twist hit
  it twice: `tilt`'s `floor(cy*4)` parity flipped on 480/480 slit-scan cells
  across 40/40 seeds (preview leaning left-right-left, downloaded file
  right-left-right), and `pinwheel`'s `atan2` at r~1e-16 swung the dead-centre
  fragment of every radial layout across its full ±16°. Fix: QUANTISE to a 1e-6
  grid before any discontinuous use — the layouts agree to ~1e-16, so it is ten
  orders of magnitude of slack — and write `sin(atan2(dy,dx))` as `dy/r` so the
  singularity is impossible to miss and can be guarded.
- **Asserting determinism by calling a pure function twice with the SAME argument
  proves nothing.** That is what the first version of the twist sweep did, and it
  is why neither ULP defect above was caught by it. The real question is never
  "same input, same output" — it is "does an input that SHOULD be the same but
  arrives a hair different produce the same answer". Invariant 11 nudges the
  coordinate instead of reusing it.
- **`composition.spec.ts` "the exported file carries the crop focus" is FLAKY,
  and it predates this cycle.** Its precondition (`|detail - centre| > 8` luma)
  depends on the app's `Date.now()` seed, so an unlucky layout does not separate
  the two focus modes far enough. MEASURED at 1 failure in 12 runs on
  pre-cycle source `e2ceb1c9` and 2 in 9 on the twist branch — no significant
  difference, and mechanically it cannot be twist (with `twist: 'none'` both
  `withTwist` and `retwistFor` are identity). Against LIVE it fails more often
  (1 pass in 4), which points at the second cause: the test allows 1200ms for the
  preview to settle after a chip click, which is generous on localhost and tight
  over the network, so the measurement can land on a half-rendered preview and
  the two focus modes read closer together than they are. The other four
  composition tests — including "crop focus re-frames the pictures without losing
  any" — pass live every time, and the failing line is a PRECONDITION about the
  preview, before any export, so the feature is fine and the test is not. Fix =
  pin the seed AND wait on the rendered blob rather than on a clock. Do not chase
  it as a regression; do fix it.
- **The preview's layout and the export's layout are not the same layout.** Every
  export recomputes `computeLayout` at its own width, and the generator is not
  scale-invariant: 11.3% of seeds at count=24 (27.7% at count=40) return a
  DIFFERENT partition, not a scaled one. Anything baked against the preview's
  cells and consumed positionally by an export is then reading the wrong cell.
  Twist's fix was to re-derive the angle from the geometry being drawn
  (`retwistFor`) so each output is at least internally honest; the ROOT cause is
  on the ladder as its own rung, because the same coupling has silently applied
  to arrangement since the day arrangement shipped.
- **A test that only exercises the geometry-INDEPENDENT variant cannot see a
  geometry-keyed bug.** The first export proof drove `scatter`, whose angle is a
  hash of the slot seed — the one mode that does not care where its fragment
  sits. It passed while the position-keyed modes went through a different code
  path entirely. Any roster with a "doesn't depend on X" member needs a case that
  DOES depend on X (T4), or the suite is green on the easy half.
- **A `save()` inside a `try` whose `catch` only counts the failure leaks canvas
  state.** The export worker had this before twist: a decoder dying mid-drawImage
  left the clip on the stack and every LATER fragment in that export inherited
  the dead fragment's clip region. Adding a second save for the rotation would
  have leaked the transform too, turning one bad decode into a sheared file.
  Every push now pops in a `finally`.
- **"Absent means keep whatever is on screen" is not a restore.** Two of the three
  composition controls were truthiness-guarded on load (`if (l.focus) setFocus(...)`),
  and every id in those rosters is a non-empty string, so the guard only ever
  fires on ABSENT — i.e. exactly the legacy projects it was meant to help. Open a
  pre-focus project while Wander is selected and you get that project's fragments
  with today's crop: a composition nobody ever saved. Absent means the DEFAULT.
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
- **THE FIX FOR A SCALE BUG HAD THE SCALE BUG.** The first cut of ONE LAYOUT
  recovered the basis height as `H / (W / 1200)`. At W=1364 that gives
  1801.8018018018015 where the preview holds ...017 — two doubles apart, the same
  number to any eye — and `metatron` returned **45 cells at one and 39 at the
  other**. Caught on the sweep's first run, not by reading. A basis that is
  DERIVED per call is not a basis; take the aspect the caller already has and
  compute `1200 / aspect` from it, so every render path lands on ONE float.
- **A WHOLE-PIXEL EXPORT DOES NOT RENDER AT THE PREVIEW'S ASPECT.**
  `dimsForTier(4096, 0.666)` is 2727x4094 — aspect 0.66610, not 0.666. So no
  quantisation of `W/H` can bucket the export together with the preview without
  also bucketing genuinely different aspects together. That 1.5-parts-in-10,000
  residue is absorbed by scaling x and y INDEPENDENTLY: the partition stays
  identical everywhere and each canvas is still filled exactly to its own edges.
  Any invariant asserting "normalised coverage is preserved EXACTLY" is therefore
  a lie about what the code does — assert it to the canvas's pixel rounding.
- **A GENERATOR THAT IS ALREADY SCALE-INVARIANT IS A FALSE-GREEN TEST SUBJECT.**
  `complex` (voronoi) was measured stable at 2e-16 across widths, so an artifact
  test driving it would have passed against the BROKEN build. The rect family
  (`minimal`, `balanced`) drifts 4.5e-4 on its *best* seed of sixty. Same lesson
  as twist's T4, one layer down: pick the case that depends on the thing.
- **`LayoutItem.id` is a module-level counter, not a function of the layout.**
  `shards` returns `shd-0…` on one call and `shd-24…` on the next for identical
  geometry. Inert today — every consumer and the React key use the ARRAY INDEX —
  and asserted in the sweep (I2b) so the day something keys off it, the record is
  already there instead of the bug being rediscovered.

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
  **The adversarial audit earned its keep for the third time**, and what it found was
  bigger than the increment: the preview's layout and the export's layout are NOT the same
  layout. Every export recomputes `computeLayout` at its own width, and the generator is not
  scale-invariant — I measured the shipped code at **11.3% of seeds (count=24) and 27.7%
  (count=40) returning a different partition**, worst drift 0.87 of the canvas. That coupling
  is older than twist (`arrangeBag` has paired photos against preview cells since the day
  arrangement shipped) and it is now the NAMED NEXT RUNG, **ONE LAYOUT**, because both fixes
  change what existing seeds render and that is a compatibility decision, not a hotfix. What
  landed this cycle is twist's share of it: `retwistFor` re-derives the angle from the
  geometry actually being drawn, at both export sites, so each output is internally honest.
  The audit also named a blind spot in my own proof — T3 drove `scatter`, the ONE mode
  independent of cell geometry — which became T4 (position-keyed, and watched going RED).
  Two more real defects closed on the way: the export worker leaked canvas state when a
  decode threw (pre-existing; adding a second save for the rotation would have leaked the
  transform too, shearing the rest of the file), and two of the three composition controls
  were truthiness-guarded on load, so a legacy project reopened with today's crop instead of
  its own. NOT fixed and deliberately named: `loadFromSVG` (project.ts) parses the embedded
  JSON_MANIFEST and then returns null unconditionally, so reopening an exported .svg is a
  silent no-op — entirely pre-existing, unrelated to twist, and its own small increment.
  **Then the audit's second round found two defects the re-bake itself had introduced**, both
  the same class and both invisible to the sweep as written: a normalised coordinate is the
  same NUMBER at every render width and not the same FLOAT, so `tilt`'s `floor(cy*4)` parity
  flipped on 480/480 slit-scan cells across 40/40 seeds (Slit Scan + Tilt previewed
  left-right-left and downloaded right-left-right) and `pinwheel`'s `atan2` at r~1e-16 swung
  the dead-centre fragment of every radial construction across its full ±16°. Fixed by
  quantising to a 1e-6 grid before any discontinuous use — ten orders of magnitude of slack
  over the ~1e-16 the layouts actually agree to — plus an explicit zero-radius guard so
  pinwheel's singularity is impossible by construction rather than incidentally absent.
  Invariant 11 now nudges the coordinate instead of reusing the same object, and was watched
  going RED (17.90° swing on the exact reported pair) with the quantiser removed. The honest
  note: the quantiser is the load-bearing fix for BOTH — with it in place the radius guard is
  belt-and-braces, so the dead-centre behaviour is pinned as an assertion rather than claimed
  as an independently-proven fix. Also measured and recorded, not chased:
  `composition.spec.ts` "the exported file carries the crop focus" is flaky at 1/12 runs on
  PRE-CYCLE source and 2/9 here — a seed-dependent precondition, not a regression.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-06 · **[AXIS:COLLAGE] ONE LAYOUT — the preview's partition IS the exported
  partition** (the rung the last cycle's audit named, not a wish; a correctness debt older
  than every feature paired against it). before→after: **four render paths generating four
  partitions → one partition drawn at four sizes.** `computeLayout` now runs the generators
  once at a canonical 1200-space basis — which is `PREVIEW_W` and the Stage's
  `DEFAULT_LOGICAL_W`, so three of the four paths were already there — and SCALES the result
  to whatever size the caller draws at (`lib/layoutScale.ts`). The old body is kept verbatim
  and exported as `computeAtBasis`, which is what lets the sweep measure the bug instead of
  describing it: **10.5% of seeds at count=24 and 24.5% at count=40 came back as a genuinely
  different partition, worst normalised centroid drift 1.18 of the canvas** — and 0.0% /
  3.1e-16 through the wrapper, same 200 seeds. The RED run named damage bigger than the
  drift: `metatron` at count=24 drew **45 fragments on screen and 22 in the 12000-tier file**,
  `voronoi` silently lost one, and normalised coverage moved 16.6%.
  **The compatibility decision, which is why this was a rung and not a hotfix:** pin the basis
  at 1200 and the preview's scale factors are exactly 1, `scaleLayout` returns the input array
  untouched, and every existing seed, saved project and share code renders BIT-IDENTICALLY —
  only the exports move, onto the picture the user was already looking at. Asserted (I2), not
  hoped for.
  **The fix had the bug it was fixing, and the sweep caught it on the first run.** Recovering
  the basis height as `H/(W/1200)` gives 1801.8018018018015 at W=1364 where the preview holds
  ...017 — two doubles apart — and `metatron` answered 45 cells at one and 39 at the other. Nor
  can it be quantised away: `dimsForTier(4096, 0.666)` is **2727x4094**, an aspect of 0.66610,
  so the export does not render at the preview's aspect at all. The answer is to take the
  `aspect` the caller already holds (11th arg, all four call sites) and absorb the whole-pixel
  residue by scaling x and y INDEPENDENTLY: identical partition everywhere, each canvas still
  filled to its own edges, cells distorted by exactly the amount the canvas was.
  **Proof:** `tests/unit/oneLayout.invariants.mjs` — 36 invariants over the whole 23-generator
  roster plus the 7 legacy modes × 4 aspects × 3 counts × 5 seeds **at the sizes the app really
  renders** (`dimsForTier`, not round numbers), 9,900 comparisons, **watched going RED with the
  wrapper bypassed** (I1 Infinity, I3d/e, I4, I5d) · `tests/e2e/one-layout.spec.ts` 4/4 desktop
  AND 393px, comparing the PREVIEW's own lock-overlay polygons against the polygons parsed out
  of the **downloaded SVG file**, also watched going RED (1.05e-3 and 1.48e-3 against a 2e-5
  tolerance). That test is a 100% discriminator rather than a seed lottery because it is
  geometric, not pixel-similarity: the SVG's `toFixed(2)` noise floor is 5e-6 normalised and the
  pre-fix code's BEST seed of sixty was 4.5e-4. Deliberately driven on the rect family —
  `complex`/voronoi measured already scale-invariant at 2e-16 and would have been green against
  the broken build, the same trap as twist's T4. Regression: composition 10/10, twist 8/8,
  source-count 7/7, export-integrity 3/3, mobile-watertight 5/5, fill 368,962 checks, videoSync
  + composition + twist sweeps clean, `tsc` clean, `vite build` clean.
  **The adversarial audit found NOTHING this time — 15 agents, four lenses, every candidate
  refuted by running code**, and that is worth recording precisely because the previous three
  audits each found HIGH defects. What it did land was two of my own COMMENTS asserting things
  the code does not do (a divergence rate quoted from the book rather than from the sweep in
  the same repo, and a fallback advertised as "consistent across widths" that is not, at
  aspect 1.7778, once `dimsForTier` floors) — both corrected, because a comment describing
  code that behaves differently is already a scar in this book. Named and NOT fixed:
  `loadFromSVG` still returns null unconditionally, and nothing in the UI can pin a seed —
  both now on the ladder.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
