# Art and intelligence roadmap

**Evidence checked: 2026-09-05. C3711 native Art Rack shipped and verified live:** [code efdc4b9f](https://github.com/mrdirno/nested-resonance-memory-archive/commit/efdc4b9fcb62bbf7262549f65732e1f4a491863d), [successful Pages deployment](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33991651937), 58/58 public-site browser cases and complete decoded-video inspection. Art Room and lyric help previously shipped in C3710. [Code 3f3ede40](https://github.com/mrdirno/nested-resonance-memory-archive/commit/3f3ede40a00d008bdc1d6a40dcbb50de0385ed59) passed [Pages deployment](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33989801143) and 40/40 public-site browser cases. The JS, CSS, render worker and service worker match the tested build byte for byte. Browser transcription and the native helper below are proposed, with no installation, model download, or performance benchmark completed during this research.

## The product we are building

An artist should bring their recording, pictures, and visual instruments; shape a sequence around the song; correct its words; and export a finished film with an editable project they own. The useful CapCut alternative is that complete workflow, with original generative art and portable source material. Adding model buttons without trustworthy editing, recovery, and export does not complete it.

Keep the small browser editor useful everywhere. Offer heavier intelligence through explicit downloaded packages or an optional local-machine helper. Free at the point of use can mean no transcription API bill; it still requires bandwidth, storage, memory, electricity, and maintenance. Neither unlimited free compute nor universal GPU support is a product assumption.

## Current and proposed

| State | Capability and boundary |
|---|---|
| Existing implementation | Collage composition, motion, soundtrack/video controls, titles, preview and MP4 export. Manual lyrics, evenly spaced paste drafts, plain SRT/VTT import/export, timed caption rendering, project/recovery integration, and an original procedural-art starter. |
| Existing limitation | Projects preserve photographs and captions; original soundtrack/video files are not yet fully packaged. A saved project is not a complete portable film source. |
| Shipped C3710 | In-studio help for external lyric extraction; local HTML art instruments in an isolated player, capturing real still pixels for normal collage intake. Loading an instrument does not establish deterministic animation or compatibility with every HTML app. |
| Shipped C3711 | Eight native art families, editable layered recipes, visibility/solo/blending, dice locks, parameter automation and exact-loop video duration. |
| Proposed | Downloaded browser transcription, native Mac handoff package, third-party deterministic renderer adapters, global overlay/shot timelines, portable audiovisual projects, and authored sequences. |

The implementation boundary is visible in the [caption module](src/lib/captions.ts), [project serialization](src/lib/project.ts), and [stage renderer](src/lib/stage.ts). Release status must come from deployment and real-page verification, not this roadmap.

## 1. Downloadable browser lyric drafts

First scope: **Draft lyrics from a selected 5–30 second take**. Explicitly download one model package, process locally in one worker, review proposed words/timings, then Apply with undo. Preserve the existing track throughout downloading, cancellation, errors, and editing. Keep manual paste/import available on unsupported devices.

Current npm `latest` and the upstream release identify Transformers.js **4.2.0**. The documentation banner still points to 3.8.1, so implementation should pin 4.2.0 and use its tagged source. Its ASR pipeline accepts model revision, device, precision, download progress, and segment/word timestamp options. These primitives still require application-level lifecycle and quality controls. [Release](https://github.com/huggingface/transformers.js/releases/tag/4.2.0), [tagged pipeline factory](https://github.com/huggingface/transformers.js/blob/4.2.0/packages/transformers/src/pipelines.js), [ASR contract](https://github.com/huggingface/transformers.js/blob/4.2.0/packages/transformers/src/pipelines/automatic-speech-recognition.js).

Quantized multilingual Whisper tiny has **40.85 MB** of encoder plus merged-decoder weights; base has **76.91 MB**. These exclude runtime, tokenizer/configuration, and inference memory. Freeze exact model revision, file sizes, hashes, and notices in the package manifest; show the actual total before downloading. Tiny is a feasibility candidate, not a singing-quality promise. [Tiny files](https://huggingface.co/Xenova/whisper-tiny/tree/main/onnx), [base files](https://huggingface.co/Xenova/whisper-base/tree/main/onnx).

Certify q8 WASM CPU first; add a measured WebGPU path. ONNX Runtime's WASM proxy cannot host WebGPU, and multithreading requires browser support plus cross-origin isolation. Run the runtime inside an owned worker; do not assume turning on a proxy or changing site headers solves every device. [Runtime constraints](https://onnxruntime.ai/docs/tutorials/web/env-flags-and-session-options.html).

“Available offline” requires the shell, worker, matching JS/WASM, tokenizer/configuration, and weights to survive a fresh offline reload. Browser caches can be evicted. Missing assets should explain the problem and preserve editing, with no silent cloud fallback. Model removal must leave projects intact. [Transformers.js cache configuration](https://github.com/huggingface/transformers.js/blob/4.2.0/packages/transformers/src/env.js), [browser storage rules](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria).

Release gates:

- No audio/transcript network transfer; successful fresh offline extraction after installation.
- Download interruption, denied storage, corrupt/missing assets, GPU failure, and single-thread CPU paths produce recoverable outcomes.
- Cancel acknowledges within one second; stale jobs never modify captions. Record peak memory and cold/warm duration on named physical devices.
- Proposed usefulness threshold: a 30-second passage finishes within 120 seconds on advertised devices, and median correction time beats manual entry by 25% across at least ten owned song excerpts. Narrow or drop the feature if it fails.
- Review repeated hooks, instrumentals, quiet vocals, dense mixes, and advertised languages; validate take offsets and caption bounds before Apply.

Whisper can hallucinate or repeat words. Lyrics research identifies accompaniment as a distinct difficulty. Estimated word timestamps do not equal verified karaoke alignment; forced alignment of a corrected transcript is a separate future stage. [Whisper limitations](https://github.com/openai/whisper/blob/main/model-card.md), [lyrics-transcription research](https://arxiv.org/abs/2506.15514), [WhisperX alignment](https://github.com/m-bain/whisperX).

## 2. Optional Apple Silicon handoff

The immediate route is external local transcription, then paste TXT or import plain SRT. Apple's MLX Whisper example provides this workflow; current MLX requires native Python 3.10+, Apple Silicon, and macOS 14+. This is upstream setup, not a Studio installer. [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper), [MLX requirements](https://ml-explore.github.io/mlx/build/html/install.html).

A later compact arm64 package should use a pinned whisper.cpp worker with Metal, a native file picker, explicit model download, progress/cancel, and TXT/SRT output to a chosen folder. Core ML encoder acceleration is optional and separately packaged; it is not evidence the entire model runs on the Neural Engine. [whisper.cpp capabilities](https://github.com/ggml-org/whisper.cpp).

Acceptance requires a clean supported Mac installation, distribution/signing checks, decoder/model notices, a fresh offline process, cancellation/memory-pressure tests, and reviewed lyric/timing results. Imported SRT must survive Studio preview and exported-video inspection. Start with file handoff; a browser extension or localhost service adds no necessary value to that first release.

## 3. Art Room: native layers and imported instruments

C3711 implements a template-first native rack with eight original families: Contour Atlas, Petal Engine, Orbit Press, Ribbon Choir, Branch Fans, Prism Garden, Woven Circuit and Satellite Dust. A rack holds up to eight ordered layers, each with its own seed, palette, visibility, dice lock, opacity, blend, geometry and automation. Solo preserves the other visibility flags. Global dice leaves locked and disabled layers unchanged. Layer edits have a bounded undo history; closing the room retains the draft for this session. Apply keeps an editable source in the composition; Save recipe downloads the working draft separately.

Native recipes travel in `.collage`, SVG metadata and recovery with a matching opening-frame PNG. Updating an applied rack creates a new immutable asset ID and remaps its pins and crop, so recovery stores current pixels. The source selector reopens saved racks for editing. A rack is one procedural source with internal overlays; it is not yet a global overlay timeline above every collage fragment.

One bounded Canvas renderer samples explicit output seconds in the room, the live Stage and offline video. Automation can change form, scale, rotation, opacity or drift, with amount, one to four cycles and phase across a 2–24 second loop. The export sheet offers the exact shared loop length. Static exports use time zero. Native source rasters sharpen on demand up to 4096 pixels per side and 16 MP; larger final artifacts scale that source. Identical pixels are checked within a fixed browser/rendering path; cross-device rasterization and encoded video are not promised byte-identical.

The Vibe card source is 2066×1319 pixels, the current bleed canvas. Square, portrait and wide canvases are also available. These are source dimensions, not a guarantee that a downstream composition/export keeps the print trim or includes production bleed marks. The implementation ships original math and no third-party instrument engine or new runtime dependency. Recipe version 1 must retain its semantics; incompatible renderer changes require a new version or an explicit migration.

HTML loading is secondary to the template gallery. Its current contract remains a still capture:

The shipped player accepts user-selected self-contained HTML and supplies a real **Use this artwork** capture. **Show artwork** reveals a deferred canvas or Bifurcata grove so visibility-triggered rendering can start. Accept bounded PNG pixels through an isolated frame and authenticated private session, then use the normal image intake. Reject wrong-session, malformed, oversized, and stale captures; closing/replacing an instrument must retire its pending work. Demonstrate nonempty art, mobile controls, project reload, and blocked parent access/external resource requests as release gates. All passed for this release. The sandbox is for HTML the user owns or trusts; it does not promise universal containment of arbitrary code or every self-navigation.

Local source audits found reusable hosting principles in MIDI Room and HTML Gauntlet, but neither constitutes an existing universal video adapter. Bifurcata's seed-addressed engine has real PNG export seams; its crop depends on device geometry, and it has no declared Studio `renderAtTime` contract. Its current declaration is `LicenseRef-Persona500-Proprietary`. Public access is not permission to rebundle it as GPL. Keep the [public Bifurcata workflow](https://persona500.com/bifurcata) separate from distribution rights and adapter compatibility.

Define these **proposed semantic contracts**, rather than calling every message-compatible instrument interchangeable:

| Contract | Required meaning |
|---|---|
| `art.image.v1` | A validated PNG Blob, dimensions, source ID/version or hash, seed/recipe when available, and capture time. Pixels are frozen; provenance cannot promise regeneration unless it is complete and persisted. |
| `art.renderer.v1` | Describe capabilities; validate recipe; prepare fixed seed/parameters/size; render a requested timeline time; cancel; dispose. Arbitrary seek order must work. Source version/hash and dependencies are frozen with the project. |

Moving adapters must follow Studio's requested time rather than wall-clock animation. The stage awaits their frames alongside video seeks, with timeouts, cancellation, bounded dimensions, and bitmap disposal. Test repeated timestamps and out-of-order seeks against a reference render. Specify the supported determinism level: exact pixels on a pinned environment, or a documented cross-device tolerance. If the source cannot be preserved or re-executed, offer an explicit frozen image/video artifact and record the loss of procedural editability. Compare actual encoded frames before claiming reproducible export.

## 4. Remove the remaining CapCut dependencies in order

**Portable originals first.** Bundle or explicitly relink soundtrack/video originals, content hashes, trim/speed/volume settings, and rights/provenance metadata. Refuse incomplete “fully portable” saves. Acceptance: reopen on a clean offline device, recover every source, and reproduce the take. A thumbnail, proxy, or temporary object URL is insufficient.

**Authored shots next.** Add a bounded sequence of art states with duration, beat-aware cuts, per-shot motion, captions, and audio continuity. Start with three shots and reversible reorder/trim operations. Acceptance: preview and export agree at every boundary; reopening preserves the sequence without manual reconstruction.

**Generation and reproducible export follow.** Allow original procedural instruments and optional local model outputs through the same source contract. Record engine/model version, seed, parameters, dependencies, and accepted frozen outputs. A changed generator must never silently rewrite an old project. Publish export receipts containing source hashes, renderer version, frame rate, duration, and audio settings.

Preserve Studio's GPL-3.0-only licensing, dependency notices, and source-distribution procedures. Transformers.js is Apache-2.0; original Whisper, whisper.cpp, and MLX examples use MIT, while converted models and imported instruments require their own provenance checks. Local execution removes a recurring API dependency, not those responsibilities or hardware costs. [Transformers.js license](https://github.com/huggingface/transformers.js/blob/4.2.0/packages/transformers/package.json), [Whisper license](https://github.com/openai/whisper#license), [whisper.cpp license](https://github.com/ggml-org/whisper.cpp/blob/master/LICENSE), [MLX examples license](https://github.com/ml-explore/mlx-examples/blob/main/LICENSE).
