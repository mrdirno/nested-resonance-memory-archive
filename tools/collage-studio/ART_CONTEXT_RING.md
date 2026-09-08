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


# Ring C3721 — The original behind the sound

## Intent and observation

An editable music-backed artwork must carry the original sound and its authored source settings when downloaded. The previous public `.collage` writer omitted music entirely. A real save after importing `music_thirds.m4a` and setting IN 2, OUT 4, level 25%, fade 0.5 produced no soundtrack member or descriptor; the new round-trip assertion failed there as expected.

## Mechanism and repair

The shared `AppState` is also consumed by SVG, history and incremental recovery. Adding ephemeral audio URLs there would spread a false portability claim. The manual archive instead takes a separate optional soundtrack input and writes one original, with strict versioned metadata and content integrity. Full candidate validation precedes adoption. Open uses direct hydration rather than the music-import gesture, which chooses motion defaults and starts preview sound. A project-open epoch discards stale files and frees their candidate URLs; source/take ownership is checked again after the read.

Independent review found three additional failure modes: an earlier intake or a newer take could race adoption; saved duration zero disabled Trim forever; restored Still was not marked owned and drifted on music replacement. Those paths now preserve current work, measure unknown duration locally, and honor the restored motion. Beat/probe completions remain tied to their soundtrack URL. A metadata descriptor with just one trim endpoint is refused rather than letting playback and the inspector disagree.

## Executable checks and evidence boundary

`tests/unit/projectSoundtrack.invariants.mjs` checks exact archive bytes/MIME/hash, strict fields, bounded expansion, missing originals and URL cleanup. `tests/e2e/project-music.spec.ts` drives original audio/video-container saves, offline file reopening in an already-loaded app, actual encoded middle-tone/gain/fades, failed save retry, atomic refusal with continuing sound, legacy clear, Open A/B, Clear/replacement races, duration recovery and owned motion. A single `audio.paused` sample is insufficient playback evidence during asynchronous seeks: the test now also requires unchanged controls and real forward clock movement without another Play gesture.

Release evidence and exact production status are maintained in [C3721_RELEASE.md](C3721_RELEASE.md). Manual music-source portability does not establish portable video originals, persisted master take settings, music in crash recovery, or cold offline installation.

**C3721 live close:** [code 1e89d3d9](https://github.com/mrdirno/nested-resonance-memory-archive/commit/1e89d3d92543e9749d96beae9abae52ec873c59e) reached [Pages 34184898401](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/34184898401); 58 public cases passed on muted Chromium/Mobile Chrome. All four shipped runtime artifacts match the final tested build. Reopened MP4s decode fully and preserve the selected tone, quarter gain and lap fades. The failing old public archive and current exported artifacts remain with the source-task release receipt.
