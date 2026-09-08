# C3722 — Browse, audition, keep

Author: Aldrin Payopay · September 7, 2026 · GPL-3.0-only

**Shipped and verified live:** [code 506b6c62](https://github.com/mrdirno/nested-resonance-memory-archive/commit/506b6c625592d247152ea7a86b4f6a60f4a1260a) · [Pages 34190005150](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/34190005150) · [Open Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/).

The artist asked to try more cinematic visual instruments against an existing layered artwork, keep a variation deliberately, and move quickly among numbered layers. C3713 made a template tile replace the whole native stack. C3722 changes that browsing gesture into a temporary audition; existing kept layers remain intact until an explicit Keep, Replace or starting-template action.

## Workflow

1. Browse the horizontal library of twelve original instruments. Family filtering and previous/next controls help expose the full roster without a tall wall of buttons.
2. Select a template to preview it over the kept artwork. Selecting another template changes this one candidate, rather than accumulating layers. Dice preview, preview opacity/blend and Preview alone affect the candidate or its monitor view.
3. Keep the candidate as the next layer, or choose Replace for the selected kept layer. Use as starting template is a separate disclosed action that replaces the kept stack. These decisions enter draft undo history; browsing does not.
4. Use the numbered layer strip to return to a kept layer. Five slots are visible by default; existing layers six through eight remain available by horizontal scrolling and in the full Layers panel. The saved recipe limit remains eight.
5. Use in Studio / Update in Studio applies the kept artwork as one editable source. An unkept preview must first be kept or dismissed. Saving a recipe preserves kept layers and says when the preview is excluded.

The preview can audition one extra candidate at capacity, but Keep cannot save a ninth layer. Replacement remains available. Preview alone does not overwrite enabled flags; audition can temporarily suspend solo for comparison. Source changes and closing discard the candidate. Draft history restores the kept recipe, selected layer and dice scope.

## Four dimensional instruments

| Instrument | Original geometry and visual behavior |
|---|---|
| Knot Foundry (`torus-knot`) | A tube swept around a seeded three-dimensional knot. Perspective, surface normals, directional light, highlights and depth sorting expose its interwoven solid form. |
| Crystal Vault (`crystal-vault`) | A cluster of tapered polygonal mineral spires with distinct tips, planar faces and a turning light/view relationship. |
| Stellar Passage (`star-tunnel`) | Stars, trails and luminous hoops occupy different depths. Perspective changes their apparent scale; distance/edge fades conceal the bounded passage's wrap. |
| Tidal Surface (`wave-surface`) | An interference heightfield forms a shaded reflective sheet; sampled form changes its actual height and surface normals. |

These are original deterministic CPU-rendered 3D geometry, projected into the existing Canvas2D/OffscreenCanvas path. They add no runtime dependency, model download, imported instrument engine or copied third-party artwork. New starting palettes/opacity apply only to the four new kinds. The existing eight families, palette definitions and default composition retain their prior outputs.

Recipe version 1 gains four permitted kind values; it gains no new serialized fields. Sampling still uses the requested output time and the existing form/scale/rotation/opacity/drift automation. Geometry never advances an internal random stream across frames. Maximum measured geometry in the unit sweep: 1,120 faces for a single mesh, or 320 stars and 21 hoops for the tunnel. Density is bounded rather than a multiplier over an unrestricted mesh.

Faces use average-depth painter sorting with directional/specular/rim shading. This is a compact visual renderer, not physical materials, ray tracing or a guarantee of globally correct occlusion for every intersecting surface. The native render limit remains 4096 pixels per side and 16 megapixels. Cross-device rasterization and encoded video are not promised byte-identical.

## Design due diligence

The implementation keeps the established explicit-time Canvas contract. Three.js documents parametric geometry as a function from surface coordinates to 3D points with explicit subdivision counts; that supports bounded analytic geometry as a design direction, without adopting its runtime. Its shader guide also explains why whole-scene per-pixel demonstrations can carry a different performance cost. [ParametricGeometry](https://threejs.org/docs/pages/ParametricGeometry.html), [shader guide](https://threejs.org/manual/en/shadertoy.html).

Blender's asset-thumbnail guidance favors recognizable shape, framing and selective contrast in small library images, while its interface guidance supports stable controls and clear actions. The product inference here is a compact shelf with different silhouettes and a visible preview → keep decision. Hydra documents distinct layer/blend/add/multiply operations; our native layer controls keep those distinctions instead of making browsing silently commit them. These references informed the design; none is bundled as an engine. [Asset thumbnails](https://developer.blender.org/docs/features/interface/asset_thumbnails/), [interface guidance](https://developer.blender.org/docs/features/interface/human_interface_guidelines/best_practices/), [source combination](https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/combine/).

## Validation and production receipt

| Gate | Evidence/status |
|---|---|
| Dimensional model and Canvas invariants | **Passed: 9 groups** in `tests/unit/artDimension.invariants.mjs`. Genuine depth, finite projected coordinates/normals, whole-model bounds, work ceilings, exact loop endpoints, random-access seeks, all palettes/automation targets, disabled/solo behavior and caller-state restoration. |
| Existing renderer parity | **Passed:** frozen Canvas-command hashes from actual `e4e19604` match all eight old painters and the default composition. A separate real-browser comparison matches all eight previous-live PNG SHA-256 hashes at seed 500 / time 2.37 / 880×880. |
| Audition/keep/history/capacity invariants | **Passed:** pure candidate isolation, exact preview/keep recipe identity, sibling preservation, solo comparison, replacement, capacity refusal, starting-template preservation and immutable snapshots. Existing Art Intent, Art Rack, archive/recipe and HTML invariants also passed; SVG has 2,070 passing checks. |
| Typecheck and final production build | **Passed.** Final frozen runtime: `index-643e1f04.js`, `index-475ab2bf.css`, `render.worker-e06f7083.js`, service-worker cache `genart-v3-9906a848f276`. Retained typecheck/build logs. Existing stale Browserslist and large-chunk warnings remain; neither is a build error. |
| Browser workflow and mobile/short-landscape layout | **Passed: 96/96 final built-app cases, 3.4 minutes, exit 0**, serial muted Chromium and Mobile Chrome. Includes 320×448, 320×664, 360×780, 390×844 and 844×390; keyboard focus, exact audition/Keep pixels, capacity/replace/solo/Undo, delayed Apply and source/project boundaries. Two source-import engine cases passed separately and are not counted as built/public coverage. |
| Visual quality and saved/exported artwork | **Passed:** four distinct dimensional families inspected in a muted real browser, with changing pixels at separate requested times. Four final native MP4 exports cover the original starter stack and kept dimensional stack in both profiles, with distinct decoded frames and complete eight-second loops. Recipes/projects reopen with unchanged original bytes and layers. |
| Existing music/lyrics/project regressions | **Passed within the 96 cases:** captions, music originals/authored mix, project integrity, Solo and forced early music arrival. QA output was muted; test media is owned/synthetic. No WebKit audio or physical-device certification is claimed. |
| Production source commit | [506b6c62](https://github.com/mrdirno/nested-resonance-memory-archive/commit/506b6c625592d247152ea7a86b4f6a60f4a1260a). |
| Pages deployment and archive health | **Succeeded:** [Pages 34190005150](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/34190005150), [Archive health 34190005148](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/34190005148). |
| Public JS/CSS/render-worker/service-worker byte comparison | **Passed:** all five public files, including the HTML entry, match the final tested bytes. JS SHA-256 `0506a986c3d14e02bc079dd241f8ebde2070d04137d688c17659bdbcf52ee2a1`. Names/cache are listed above; complete digests are retained in `source-artifact-match.json`. |
| Public behavioral/visual verification | **Passed: 96/96 cases on the public URL, 3.6 minutes, exit 0**, muted Chromium/Mobile Chrome, one worker. Live fixed-time PNGs for all eight old families match the previous release; all four new families animate. Four live eight-second 1080×690 art MP4s fully decode without errors. |
| Fleet delivery and peer awareness | **Posted and read back:** broadcast `17937`, thread `persona500-collage-C3722-release`, from `codex-collage-studio`. Exact body and metadata match. `read_by` was empty at close; peer reading is not yet confirmed. |

The source task retains this cycle's working artifacts under `work/c3722` and earlier `work/c3722-*` runs. The demonstrated old public baseline has zero Preview actions where the new flow requires one. All four dimensional families show distinct moving pixels; original-family parity is measured separately.

Independent review found and repaired a pending Apply cancellation caused by navigating to Layers, replacement accessible naming, focus after Keep/Dismiss in expanded or filtered views, keyboard Undo focus, and cramped short-screen preview controls. The integrated regression checks use real delayed canvas serialization, exact downloaded recipe/archive bytes and actual encoded frames. An intermediate development run was 47/48; its unchanged isolated mobile export rerun passed. Hot refresh canceling a notice timer is a possible cause, not an established diagnosis. That failed run is retained. The first final-build layout pass also caught a 124px canvas on the smallest normal phone after a layout adjustment; the minimum stage height was restored before rebuilding. A later full frozen-build run passed 92/94, with two music-start failures. Controlled decoding proved the existing early-arrival defect, and the startup artwork canvas also made the ordinary Solo fixture declare readiness too early. The parent now queues the music arrival before photographs finish, and suppresses obsolete arrival delivery after the track is removed. Ordinary fixture readiness and a separate forced-order regression cover both cases; no failed assertion was simply removed. The Solo fixture also now targets the actual image/video input: after artwork mounts, its previous first-input selector could send a clip to the hidden caption importer. The gated test passes both profiles, including music removal and a subsequent explicit music import. Final frozen-build and public-site runs below determine release status.

## Boundaries and next work

The overlays are internal layers of one native Art Room source. They do not yet sit above every Studio photograph/video as global tracks, and C3722 is not a full CapCut replacement. C3721's manual soundtrack-original portability remains in place; original moving-video packaging, master take settings, authored shots, global overlay timelines and local lyric models remain separate roadmap work. No old project is rewritten merely by opening it.

The existing Monday 10 a.m. Pacific weekly evolution remains active. Publication close updates the shared fleet with this release, evidence, limitations and next direction so Codex and Claude can discover it at their next bump; no duplicate scheduler is added.

Repeat the built/public behavioral gate with the actual target URL; the source-only engine spec is deliberately separate:

```sh
COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ npx playwright test tests/e2e/art-audition.spec.ts tests/e2e/art-intent-ring.spec.ts tests/e2e/art-rack.spec.ts tests/e2e/art-rack-export.spec.ts tests/e2e/art-room-ux.spec.ts tests/e2e/project-music.spec.ts tests/e2e/project-integrity.spec.ts tests/e2e/solo.spec.ts tests/e2e/captions.spec.ts --project=chromium --project='Mobile Chrome' --workers=1
```

The final local log is `work/c3722/final-built-r3.log`. Earlier development failures, controlled negative music baseline, exact old-family pixels, final artifact hashes, layouts and downloaded media remain in the same source task. This is browser-profile coverage on this Mac, not a guarantee of equivalent frame rate or autoplay on another device.

Final evidence: `work/c3722/live-browser.log`, `live-browser-receipt.json`, `live-visual-proof.json`, `live-full-decode.json`, and `source-artifact-match.json`. The task outputs include a ready-to-open `.collage` demo, editable recipe, phone screenshot and a silent moving dimensional video. The live demo pacing measured on this Mac is not a mobile hardware performance promise.
