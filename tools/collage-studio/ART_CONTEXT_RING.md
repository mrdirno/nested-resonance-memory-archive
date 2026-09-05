# Ring C3713 — Template intent and art context

Author: Aldrin Payopay · GPL-3.0-only

## Observation

After C3712, choosing a template still appended a layer. The large gallery tile called the same `add` operation as the layer-building path. A starter with three layers became four after choosing A and five after choosing B. The interface presented template browsing but executed accumulation.

## Intended semantics

`Use template` replaces the selected native artwork's draft stack in one undoable transaction. It preserves the art canvas, background and loop duration; its new layer receives a fresh identity; solo resets. The saved source library and outer collage pool are untouched until the separate Add artwork / Update artwork action.

`Add layer` is an explicit second action. It appends one layer and preserves the IDs, values, enabled flags and dice locks of every sibling. Loading an old stacked project preserves it exactly; loading is never a migration to one layer. Dice locks protect against randomization only. Explicit Use replaces even locked layers; Undo restores their former lock states. Direct property edits remain available on locked layers.

Undo and redo restore the stack, its selected layer, and the selected dice scope. Changing the applied-source selector clears draft history rather than replaying a change against a different source. Apply's source ID belongs to the parent pool, not a historical draft snapshot. This is draft undo while Art Room stays open: closing the room discards its local history. Outer Collage undo does not roll back an already applied native-art revision.

## Context and supported actions

| Context | Mutations allowed now | Boundary |
|---|---|---|
| Native art composition | Use template, explicitly add layer, order layers, canvas/background/duration, dice enabled unlocked layers | One native art source, not every imported photo/video in the outer collage |
| Selected layer | Shared renderer controls, type-specific density description, enable/solo/dice lock, dice this one layer | Untargeted, locked and disabled layers retain identity and values |
| Selected property | Direct control edits through typed whitelisted fields | No property dice or arbitrary metadata code |
| Region / external AI | Not implemented | No inferred geometry, cross-app execution or model-backed capability claim |

Context metadata describes renderer-backed controls in the UI. It does not extend strict recipe version 1, change rendering, or execute code supplied by a project or template.

## Counterexample and regression

`tests/e2e/art-intent-ring.spec.ts` drives the public UI and downloaded recipes/projects:

- Primary A then B must contain B alone; one Undo restores A, one Redo restores B.
- Explicit Add B after A yields A+B, preserving A's complete settings and ID. Add refuses a ninth layer; Use can replace a full eight-layer stack.
- Replacement Undo restores selected layer, held/disabled states and solo.
- Selected-layer dice changes its target only; composition dice preserves locked/disabled layers.
- Opening a saved three-layer source leaves its recipe unchanged. Browsing A/B does not update its saved source until Apply; imported original bytes survive Apply.
- Primary Use and secondary Add remain separate, hittable 44px targets on narrow phone and landscape layouts, alongside an explicit dice scope.

The existing Art Rack, Art Room layout and encoded-loop cases remain regression evidence. A test expecting accumulation is valid only when it drives the explicit Add action.

## Release evidence

Code [`0b29eb28`](https://github.com/mrdirno/nested-resonance-memory-archive/commit/0b29eb2832e6bfa1580b8454ee2958cd89718ce1) is [deployed](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33996665537) at [Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/). The old public page was exercised in a fresh muted browser: saved recipe layer counts were 3→4→5; the expected last-template-only count was 1. The new public UI passed 45/45 browser cases: 18 intent/context cases, 24 existing Art Rack/Art Room cases and 3 actual moving-loop exports, across Chromium, Mobile Chrome and Mobile Safari. Typecheck, production build and three unit suites passed. Public JS/CSS/worker/service-worker bytes match the tested build.

The intent cases compare downloaded recipes and actual ZIP project bytes. They verify old stacked-project preservation, Apply's fresh native-source identity and byte-identical imported originals. Separate narrow checks exercise 320×664, 390×844 and 844×390 layouts with 44px controls. Existing native export cases decode sampled frames at 0.1, 2, 5 and 7.9 seconds and verify moving, nonempty output and an eight-second duration. These are automated browser profiles, not a claim of physical-device certification. See [release](C3713_RELEASE.md) for boundaries and the shared fleet thread.
