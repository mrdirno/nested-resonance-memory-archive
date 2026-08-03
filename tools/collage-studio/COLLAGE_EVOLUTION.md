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
  (loop / stretch-to-longest / speed-to-shortest), live and in export.

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
- `shuffleTrigger` co-seeds the fill RNG but isn't persisted — Restore reproduces
  a layout's geometry, not its exact shuffled arrangement (fix = persist it in the
  save schema; do NOT fold into `seed`, that breaks shuffle's "shapes stay put").

## THE RATCHET (perpetual by construction)
When a capability tier reaches broad parity with CapCut, the north star raises:
the next tier (pro effects, AI-assisted editing, collaboration) becomes the
frontier. Today's ceiling is tomorrow's floor.

## CYCLE LOG (append one line per collage cycle — capability · before→after · proof)
- 2026-08-03 · lane created · source-first fill + video-length sync already live · next rung: **timeline & trim**
