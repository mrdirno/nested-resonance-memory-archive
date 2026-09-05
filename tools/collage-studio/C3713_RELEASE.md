# C3713 — Template intent and scoped dice

Author: Aldrin Payopay · September 5, 2026 · GPL-3.0-only

[Open Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/) · [Code 0b29eb28](https://github.com/mrdirno/nested-resonance-memory-archive/commit/0b29eb2832e6bfa1580b8454ee2958cd89718ce1) · [Successful deployment](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33996665537)

Choosing a template now replaces the native artwork's layer stack. **Add layer** is the separate action for combining looks. The preview-first layout remains in place.

1. Choose a template thumbnail to use that look alone. Canvas size, background and loop duration stay as set.
2. Choose **Add layer** to build a stack. Select a layer under Layers to edit its look or motion; Density explains what it controls for that family.
3. The dropdown beside **Dice** names the target: the native art composition or the selected layer. Dice preserves locked and disabled layers. Locks do not prevent deliberate property edits or template replacement.
4. **Canvas & recipe → Undo/Redo**, or the existing shortcuts, restores the draft stack, selected layer and dice scope. Use can replace a full eight-layer stack; Add refuses a ninth.
5. **Add artwork / Update artwork** applies the draft to the Collage source pool. Browsing templates alone does not rewrite the saved source. Existing stacked projects remain stacked when opened, and imported original bytes are preserved.

## Verification and boundaries

**45/45 local and 45/45 public browser cases**: 18 intent/context cases, 24 existing Art Rack/Art Room regressions, 3 actual moving-loop exports. All run on desktop Chromium, Mobile Chrome and Mobile Safari. Three relevant unit suites, typecheck and production build passed. The public JavaScript, CSS, render worker and service worker match the tested build. Native videos decode to complete eight-second loops; an independent full-frame scan finds 240 desktop frames and 192 per mobile profile, with no blank frames.

Draft undo is local to an open Art Room. Closing it clears that history; outer Collage undo does not roll back an already applied art revision. This release adds no property/region dice, arbitrary metadata execution, model inference or saved recipe fields. Existing build-tool warnings remain non-failing.

The [Art context Ring](ART_CONTEXT_RING.md) links the observed 3→4→5 defect to precise semantics, regression cases and release evidence. The shared publication thread is `persona500-collage-C3713-release`; fleet storage and a peer reading it are separate observations.
