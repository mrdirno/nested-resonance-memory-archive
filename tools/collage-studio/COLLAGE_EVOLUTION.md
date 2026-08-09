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
  scaled, instead of four partitions generated independently;
  TRIM — per-clip in/out points with a filmstrip sheet, held by ONE
  output-time-to-source-time function (`lib/clipWindow.ts`) that the live
  element, the offline frame seek and the offline audio mix all ask, and coupled
  to video-length sync through the WINDOW length rather than the file's;
  THE LAP SCHEDULE — when a clip's audio track ENDS INSIDE the trim window, the
  export stops asking one looping node to express a signal that is not periodic
  at its own loop length and schedules one non-looping node PER PICTURE LAP
  (`clipWindow.audioSchedule`), so the sound laps with the picture instead of
  with the audio track;
  THE COMPOSITION CODE — every composition has a short code, shown under the
  dice, tap to copy, paste one back to open it, and carried in the address bar
  so a LINK is a collage. `lib/rollCode.ts` owns the one seam between app state
  and a `Roll` in both directions; the sources are deliberately not in it;
  THE TITLE — a caption typed into the dock and drawn over the finished collage
  by all four surfaces that produce pixels (still preview, live Stage and so
  both video recorders, the export WORKER's OffscreenCanvas, and the SVG as real
  `<text>`), from ONE plan wrapped once on the main thread at the 1200 basis
  (`lib/title.ts`) and scaled per surface.;
  THE LOOK — a colour grade on the photographs, eight named looks on one row of
  chips, reaching all four surfaces that produce pixels from ONE ordered
  pipeline (`lib/grade.ts`): the three canvas paths set `ctx.filter` from
  `cssFilterFor`, and the SVG emits the spec-equivalent `<filter>` primitives in
  the same order through the same formatter, pinned to `sRGB`. It rides the dice
  AND the composition code — unlike the title, because a grade IS part of a
  recipe.;
  THE FULL WALL — the offline export admits EVERY clip, not just the realtime
  decoder budget. The count/pixel caps (`lib/stage.ts`, mobile 3 / desktop 4-8)
  exist so LIVE compositing keeps a clock; an offline render has no clock — it
  seeks one frame at a time — so `beginOfflineRender` lifts them and re-admits
  the deferred clips, restoring both on exit. Before, a clip past the cap
  exported as a FROZEN STILL while `describeAudioSources` mixed its sound in
  regardless, so the file played audio over a picture that never moved; now the
  video matches the audio it was already carrying;
  THE POST — the exported SVG IS the project file. A composition code is a
  RECIPE and carries no pictures; the SVG already held both and could not be
  opened. `lib/svgProject.ts` is the one pure seam between the writer
  (`vectorExport`) and the reader (`project.ts:loadFromSVG`): the manifest lives
  in `<metadata id="collage-project">` instead of an XML comment that a caption
  containing `--` could make ill-formed, each `<image>` carries `data-src-id`,
  and the pool's UNDRAWN members ride in `<defs id="collage-sources">` because
  `arrangeBag` deals from the pool's length as well as its order. It fails
  CLOSED — a pool that comes back short is refused, visibly, rather than opened
  into a plausible collage that is not yours. `density` and `countOwned` are now
  persisted too, because a project that saved neither described neither the
  number of fragments nor the crop it was looking at;
  THE MOVE — the collage has a TIME AXIS. Five per-fragment drifts (Push /
  Drift / Sway / Pulse / Wander) on one chip row, on the dice and in the share
  code, held by ONE pure module (`lib/motion.ts`) that every render path already
  reaches through `calculateSmartCrop`. The static half of a move (which one,
  and this fragment's own phase in it) rides the per-slot `analysis` — the seam
  `withFocus` and `withTwist` share — and the TIME is a fourth argument
  defaulted to 0, because one analysis is drawn at many instants. Zero at t=0
  BY REFERENCE (`NO_MOVE`), so the three surfaces that produce a single frame
  (still preview, raster export, SVG) pass no time and are bit-identical to a
  build without it, and the video opens on the picture the preview is showing.
  Periodic on a fixed 12 s raised cosine rather than on the export's duration:
  the live preview has no end to ramp towards, and a duration-keyed ramp would
  make the same collage move differently at 10 s and at 30 s — and differently
  again when the device cap clips the take. The stagger that makes a collage
  feel alive lives in the HARMONIC and the BEARING, never in a phase offset,
  because a phase offset is exactly what would break rest-at-zero. And it
  WIDENED `liveMode`: the video export was gated on `clips.length > 0`, so a
  collage of photographs could not be recorded at all — the one thing a photo
  collage could never be was a video, and a move is precisely what makes it one;
  THE SOUNDTRACK — music under the collage, held as A CLIP WITH NO PICTURE.
  It plugs into the five audio seams the Stage already had (element →
  `MediaElementSource` → gain → `masterGain`, an intent flag, and one
  `describeAudioSources` row), so `offlineAudio.mixSources` changed by not one
  line and the realtime recorder gets it free from `captureStream`'s tap on
  `masterGain`. `lib/soundtrack.ts` carries only what is particular to music:
  `span: 0` for every duration (a container's length is not the decoded
  buffer's, and that hop would flip `audioSchedule` into its LAPPED branch and
  cut a sliver of silence into every repeat), intent kept structurally free of
  the monitor, and a file classifier disjoint from `isVideoFile` so every
  picked file lands in exactly one bucket. Music arrives UNMUTED because adding
  it is an explicit act whose whole purpose is the sound, and the take resets it
  to the top beside `moveOriginMs` so both recorders open on the same bar.

## THE CAPABILITY LADDER (→ CapCut — GROW this list as you learn)
Each cycle pick ONE rung by **leverage × feasibility** (what a real editor reaches
for most, vs build cost). Mark shipped ones `[x]`; add rungs as you find gaps.
- [~] **Timeline & trim** — the single biggest CapCut gap, now part-shipped.
      **TRIM (in/out) is done**: `lib/clipWindow.ts` owns the one function that
      maps OUTPUT time to SOURCE time (`sourceTimeAt`), and the three timelines
      that used to each carry a copy of that formula — the live `<video>`
      watchdog, the offline frame seek, the offline audio mix — now ask it. Trim
      composes with video-length sync, because sync is fed the WINDOW length
      rather than the file's duration. Still owed on this rung: **drag-reorder**,
      **playhead scrub** and **split/cut**, which are a timeline WIDGET rather
      than a timing contract and are their own increment.
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
- [x] **THE LAP SCHEDULE** — a trim that straddles the end of a short audio
      track now laps with the PICTURE instead of with the audio track.
      `audioPlan` clamps `loopEnd` into the decoded buffer, which is the only
      safe thing to hand a node — but a clamped loop region is also a clamped
      PERIOD, and the period is the one thing the picture and the sound must
      share. `shortaudio.mp4` (6.000 s picture, 2.99998 s sound) trimmed to 2→5:
      the picture lapped every 3 s and the node every 1 s, so from one second in
      they walked apart and never met again — an unbroken 440 Hz drone under a
      picture the file is silent for. The fix is not a better clamp: ONE node
      cannot express a signal that is not periodic at its own loop length. So
      `audioSchedule` (lib/clipWindow.ts) emits one NON-LOOPING node PER PICTURE
      LAP for that case — each lap plays what the file has and then stops, which
      is exactly what the live `<video>` already did, so the export finally
      reproduces the preview instead of inventing a drone the preview never had.
      **The scope is the branch condition**: a schedule differs from the plan iff
      the plan wanted to loop over LESS than the picture window, so every other
      export is bit-identical (I16, 8,298 setups, `Object.is`). Proof:
      envelope of the exported MP4 at 0.25 s resolution reads
      `####........####....` — 40% duty, silence exactly where the file has none,
      against ~100% before.
- [ ] **`offlineAudio.mixSources` HAS NO UNIT COVERAGE, and it is where a
      scheduling fix actually lands.** Raised by the adversarial audit of the lap
      schedule and only half-closed. The sweep loads `clipWindow.ts` and
      `videoSync.ts` only, so the translation from an `AudioStart` to a real
      `node.start(when, offset, duration)` — the per-lap wiring loop — is
      asserted by exactly ONE test in the whole tree (trim.spec.ts T7). The
      audit's mutations of that loop (`start(0, …)` instead of `start(s.when, …)`,
      wiring only the first entry) were green before T7 gained its phase anchor
      and are red now, so the hole is narrowed rather than closed: a single e2e
      is still the only guard on the loop, and it costs eight minutes to run.
      The fix is a fake `OfflineAudioContext` (record `createBufferSource` /
      `connect` / `start` calls) driven against a real schedule — cheap, since
      the mixer only ever calls five methods — which would let mutation testing
      reach the wiring in milliseconds instead of minutes.
      **AND THE STAKES WENT UP WITH THE SOUNDTRACK.** That loop now wires a
      source the user CHOSE for its sound rather than one that came along with a
      picture, and it is the only source in a photo collage — so a mutation
      there is no longer "one clip is quiet", it is "the export is silent".
      `tests/unit/soundtrack.invariants.mjs` covers the row handed IN; nothing
      still covers what the mixer does with it.
- [ ] **THE TITLE CANNOT TRAVEL IN A COMPOSITION CODE, and that is a decision,
      not an oversight.** A code is a RECIPE anyone can open with their own
      photographs; somebody else's caption over your pictures is not the same
      collage, so the title rides in the project file and in the SVG's
      JSON_MANIFEST (both carry the whole `AppState`) and not in `?c=`. It is
      the second thing on the "in the app but not in the code" list, after
      pinned fragments — and unlike pins it is not even disclosed in the strip,
      which is the honest gap here.
- [ ] **The title is one caption, not a text LAYER.** Two captions, a
      lower-third with a name and a role, a credit block in one corner and a
      date in another — all of these are the same plan repeated, and `TitlePlan`
      is already an array of positioned lines. The generalisation is a LIST of
      plans, and the moment a second caption exists the placement roster stops
      being four chips and becomes a real position control.
- [ ] **Drag-reorder, playhead scrub and split/cut** — the timeline WIDGET, the
      remaining half of the timeline rung. Trim is a timing CONTRACT and is done;
      these are direct manipulation and are their own increment.
- [ ] **Transitions** — cross-dissolve / fade / wipe / slide between clips/scenes.
- [~] **Text & titles** — part-shipped as **THE TITLE**. One caption, four
      placements, three sizes, drawn on a scrim so it stays readable over any
      photograph, and it reaches every surface that produces pixels. The seam is
      that the WRAP IS DECIDED ONCE: `planTitle` (lib/title.ts) resolves the
      whole caption to geometry in the canonical 1200 basis against the context
      the PREVIEW measures with, and `titlePlanFor(plan, width)` takes that
      finished plan to whatever size each caller draws at. Letting the four
      paths each wrap the text would have decided the break four times against
      four font environments — and one of them is a WORKER THREAD, where the
      same font stack is free to resolve to something else, which is the
      preview-is-not-the-file divergence ONE LAYOUT exists to prevent. The text
      box is the margin box less the plate's own padding, because the thing that
      has to respect the margin is the SCRIM, not the glyphs (the naive rule
      pushes the scrim off the canvas on 326/756 swept plans, by up to 2*padX).
      Still owed on this rung: a colour/weight choice, per-line styling, MOTION
      (animated titles and lower-thirds — the first thing here that needs a time
      axis), and auto-captions from the audio track.
- [x] **A code's middle group is read by LENGTH, and nothing rejects a LONGER
      one.** CLOSED — and THE MOVE is what made it load-bearing.
      **AND IT WAS WORSE THAN WRITTEN.** Adding the move gave the group a THIRD
      checksummed length, and the sweep written for it turned up the other half:
      `hasLook`/`hasMove` enter the checksummed band BY LENGTH, so lopping two
      or three characters off a real code drops it BELOW the band — 16 or 17 —
      where the guard did not run at all and the code opened, cleanly, as
      somebody else's collage. Truncation in a chat client is the exact hazard
      the checksum exists for, arriving through the door that decides whether to
      look. Both ends are closed by one comparison against
      `MINTED_GROUP_LENGTHS` = {18, 19, 20}, and those three are safe to name
      exactly because git says so: this codec was wired to nothing until
      a1797423 (2026-08-07, "the code that was written, documented and never
      called"), so no other length has ever existed in the wild. The old
      assertion in rollCode's own sweep listed 16 on the TRUST side while the
      comment beside it said 15 — over-inclusion, now narrowed. Original text: Found while adding the look. `decodeRoll` picks the layout of that
      group from its length (15 pre-flag, 16 flag-no-checksum, 18 pre-look, 19
      with a look) and then slices the checksum at a fixed offset — so trailing
      characters BEYOND 19 are simply ignored and a code with junk appended
      still validates. Entirely pre-existing (an over-long group sailed through
      the 18-character form the same way) and not reachable from the app, but
      "no error case" is the error case for a string whose job is to survive
      chat clients. The fix is an exact-length check per generation, which is
      one line and a sweep arm.
- [ ] **THE LOOK is a preset roster, not a grading desk.** Eight fixed grades is
      the right first cut — a picker you have to scroll is a settings screen —
      but `Grade` is already five continuous numbers, so exposing them as
      sliders is a UI change rather than an engine change. The moment that
      happens the two-decimal `GRADE_GRID` stops being a property of a
      hand-written roster and has to be enforced on the way in, exactly as
      `snapRoll` does for the composition sliders.
- [~] **Keyframes** — part-shipped as **THE MOVE**: POSITION and SCALE over
      time, per fragment, as a named roster rather than as hand-set keyframes.
      `lib/motion.ts` owns both halves — `movePhase` (a fragment's bearing, from
      WHERE IT IS and never from its slot index, quantised to the same 1e-6 grid
      `twistAngle` records the reason for) and `sampleMove` (that phase plus a
      time, to a zoom multiplier and an anchor nudge). The load-bearing
      decisions, in order of what they cost to get wrong:
      **REST IS A SHARED OBJECT.** `sampleMove` returns `NO_MOVE` by reference
      at t=0 and at every cycle boundary, and `calculateSmartCrop` branches on
      that identity rather than on arithmetic that happens to be a no-op — no
      multiply by 1.0, no add of 0. That is what makes the still preview, the
      raster export and the SVG provably untouched: 27,000 swept setups where a
      move at t=0 is `Object.is`-identical, field by field, to no move at all.
      The mutation that returns a fresh `{zoom:1,ax:0,ay:0}` instead PASSES that
      check today and fails the reference one — which is why both are asserted.
      **A PAN IS A FRACTION OF THE ROOM ITS OWN ZOOM LEAVES.** The crop is
      clamped inside the image, so a pan bigger than the slack does not pan, it
      CLAMPS — and a clamped fragment sits still while its neighbours move,
      which reads as a bug in the one place the eye is already looking. Defining
      the reach as `(1 - 1/zoom)/2 * pan` makes "pan without room"
      unrepresentable rather than merely tested: 69,000 crops, 0 clamped,
      against a naive flat 0.25 pan that clamps 13,764 of 22,700 with a worst
      overshoot of 1,495 source pixels.
      **THE STAGGER IS IN THE HARMONIC, NOT THE PHASE.** The obvious way to make
      a collage feel alive is to phase-shift each fragment, and a phase shift
      inside the wave puts every shifted fragment somewhere other than rest at
      t=0 — which would have cost the identity guarantee above. So a fragment
      breathes once or twice per cycle (both exactly zero at both ends) and
      drifts along its own bearing. Same liveliness, no discontinuity anywhere.
      **THE RE-CROP IS NOT IN `drawFrame`.** That loop's written contract is
      "fully synchronous, zero allocation", and `calculateSmartCrop` returns an
      object literal. `refreshMoveCrops` runs off the draw — from the tick and
      from `renderAtTime` — so the draw loop is byte-for-byte the loop it was
      and the allocation is paid only by compositions that actually move.
      Still owed on this rung: OPACITY and ROTATION over time, a user-set speed
      (the 12 s cycle is fixed), per-fragment choice rather than one roster pick
      for the whole collage, and real hand-set keyframes with a curve editor —
      which is a timeline WIDGET and belongs with drag-reorder and scrub.
- [~] **Adjustments & filters** — part-shipped as **THE LOOK**. Eight named
      grades (None / Punch / Faded / Mono / Noir / Warm / Cool / Bleach) on one
      wrapping chip row, on the dice and in the share code. The seam is that a
      grade is not a STRING, it is an ORDERED LIST OF STEPS
      (`brightness -> contrast -> saturate -> sepia -> hue-rotate`), and the two
      emitters are both pure functions of that one list: `cssFilterFor` joins it
      for the three canvas paths, `svgFilterFor` maps each step to the primitive
      CSS Filter Effects defines as its exact equivalent, in the same order,
      through the SAME number formatter. Colour operations do not commute, so
      the order is part of the grade and lives in one place.
      **The load-bearing decision is `color-interpolation-filters="sRGB"`**:
      canvas evaluates CSS filter functions in sRGB and SVG filters default to
      LINEAR light, so the identical primitives with the identical numbers make
      the exported SVG a different picture from the exported JPEG. Measured:
      dropping that one attribute moves them up to **105.2/255** apart (mean
      28.1/255). Still owed on this rung: user-set sliders rather than only
      presets, per-fragment grades, LUT import, and a grade on the BACKGROUND
      (deliberately excluded today — the frame colour comes out the colour you
      picked).
- [~] **Audio** — part-shipped as **THE SOUNDTRACK**: music under the collage.
      THE MOVE gave a collage of photographs a time axis, so a photo collage
      could finally be exported as a video — and that video was NECESSARILY
      SILENT, because every sample this app had ever mixed came out of a video
      clip's own audio track and a collage of photographs has no clips. The file
      picker took `image/*,video/*` and `ingestFiles` rejected everything else
      with "images and video only", so there was no door at all.
      **THE WHOLE DESIGN IS ONE SENTENCE: A SOUNDTRACK IS A CLIP WITH NO
      PICTURE.** The Stage's audio architecture was already per-source and
      complete — an element, a `MediaElementSource`, a gain into `masterGain`
      (which is what `captureStream` taps, so the REALTIME recorder gets music
      for free), an INTENT flag, and one row out of `describeAudioSources()` for
      the offline mixer. Music plugs into all five, and
      `offlineAudio.mixSources` changed by NOT ONE LINE: it decodes a url,
      resolves a window through `clipWindow`, and sums under the true-peak
      limiter, none of which cares whether the container also had pictures in
      it. `lib/soundtrack.ts` holds only what is particular to music:
      **SPAN 0, FOR EVERY DURATION.** `OfflineAudioSource.span` exists so a
      clip's sound lands in the same window as its PICTURE. Music has no
      picture, and its container duration is not its decoded duration (mp3
      carries encoder delay and padding). Passing that hop as `span` does not
      merely round differently — it changes BRANCH: `audioSchedule` reads "the
      sound ends inside the window" as the LAPPED case and answers with one
      non-looping node per lap, cutting a sliver of silence into every repeat
      forever. `span: 0` is the documented "unknown" and the mixer then uses
      `buf.duration`, which for music is the only length there is. The sweep
      asserts 0 for SANE durations too, so the helpful edit fails instead of
      shipping the sliver.
      **INTENT IS NOT AUDIBILITY, and this time they live three lines apart.**
      Same split that made every export silent once already: `gain` for the FILE
      is `!muted`; `audible` also carries the monitor (which starts OFF, because
      browsers only autoplay muted media). `soundtrackSource` takes no monitor
      argument at all and the sweep is what keeps it that way.
      **A CLIP IS A PICTURE THAT HAPPENS TO HAVE SOUND; A SOUNDTRACK IS NOTHING
      BUT SOUND**, so music arrives UNMUTED where a clip arrives muted — which
      is why the e2e's headline path presses record and touches nothing else.
      **THE MUSIC RESTARTS WHEN THE TAKE DOES**, beside `moveOriginMs = -1` in
      `setCaptureActive`, or the realtime recorder captures whatever bar the
      preview happened to be on while the offline render starts at the top.
      Proof: `5.0s · 999 KB · 30fps · 150 frames · sound`, decoded back to
      samples — 1500 Hz at **3114x** the 5 kHz control, in the MIDDLE of a 5 s
      take from a 2 s file, so it lapped; muting the chip gives
      `150 frames · silent` and no decodable audio track at all.
      Still owed on this rung: **a fade in/out** (the mix currently hard-cuts at
      the end of the take — the honest place for it is the sample domain, right
      where the peak limiter already walks the whole rendered buffer), volume
      per source, ducking, and beat-sync.
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
- [x] **Reopening an exported .svg is a silent no-op → THE POST.** `loadFromSVG`
      (`lib/project.ts`) parsed the embedded JSON_MANIFEST and then returned
      `null` unconditionally, so the file input advertised `.svg` and did
      nothing with it. The TODO said it was waiting on "vectorExport MUST convert
      images to Base64" — that fix had shipped long before and nobody came back
      to tell it. `lib/svgProject.ts` is now the one seam in both directions;
      the manifest moved out of the XML comment (a caption with `--` in it made
      the file ill-formed XML — MEASURED at 4/14 captions) into `<metadata
      id="collage-project">`, sources are matched by `data-src-id`, and the
      undrawn pool rides in `<defs id="collage-sources">` because `arrangeBag`
      deals from the pool's LENGTH as well as its order.
- [ ] **The writer can emit a file the reader will always refuse.** If
      `blobToBase64` fails for a pool source, `vectorExport` writes
      `xlink:href=""` AND still lists that id in the manifest, so `loadFromSVG`
      throws on it and refuses the whole file — at open time, with nothing said
      at export time. NOT reachable in ordinary use (a pool asset's object URL
      is never revoked while it is in `images`: App.tsx:973 only revokes a
      source it is discarding, and `revokeFrames` disposes the extraction
      batch's URLs, not the ones `handleUpload` minted), and not a regression —
      that path already wrote an empty href. Repro: revoke an asset's `src`
      before exporting. The honest fix is for the export to SAY the file is not
      re-openable, not to quietly ship a shorter pool.
- [ ] **`PROJECT_FORMAT` is written and never read.** `readProject` ignores the
      `format` field, so a future v2 file would be parsed by a v1 reader as
      though it understood it. Costs one comparison; unreachable until the
      shape actually changes, which is exactly when it stops being free.
- [ ] **Opening a project never releases the pool it replaced.** `loadFromSVG`
      mints one object URL per pool image and `setImages` replaces the pool
      wholesale; nothing revokes the old one, so every Open retains another full
      copy of every photograph for the life of the tab (MEASURED: 8 photos =
      15.64 MB, one Open = 30.58 MB, 17 of the original 18 URLs still
      resolvable). NOT a one-liner, and that is the point: `addToHistory(state,
      images, …)` retains the pool array, so blind revocation would blank a
      restored history snapshot — a silent wrong picture, which is strictly
      worse than the leak. `handleClear` has the same shape and the same reason.
      The honest fix is refcounting the pool against history, as its own
      increment.
- [x] **A seed the user can pin → THE COMPOSITION CODE.** `encodeRoll` /
      `decodeRoll` existed and were wired to NOTHING, and `diceRoll.ts`'s own
      header had promised "same code, same collage, on any device" the whole
      time. The missing piece was never the codec: the roll flowed ONE WAY, into
      fifteen `setState` calls with no route back, so there was no code to show.
      `lib/rollCode.ts` is that route in both directions (`CompositionState` ↔
      `Roll` ↔ string), pure, plus `codeFromUrl`. The UI is a strip under the
      dice — tap the code to copy, paste one and press Open — and `?c=` is read
      at mount and kept current with `replaceState`, so the address bar is the
      share button. Wiring it up is what exposed that the codec could not
      actually carry a composition: see the four scars below.
- [ ] **The code is a recipe, so the next rung is a POST — a code plus the
      pictures.** "Send someone your collage" currently means sending a code and
      the photographs separately. The obvious extension is a single artifact
      (the exported image with the code in its metadata, or a project file that
      opens by drop), and it is a different problem — bytes, not parameters.
- [ ] **PINNED FRAGMENTS cannot travel in a code, and are only DISCLOSED.** A
      lock is a cell→imageId pin, and it does not just hold one picture in place:
      it claims that image, which re-deals every slot after it. So a code minted
      with pins does not describe what is on screen. The ids are per-session
      (`${prefix}-${Date.now()}-${seq}`), so they genuinely cannot ride in a
      source-independent code — the strip says so instead, which is honest but is
      not the same as solved. A real fix needs a source-independent way to name
      "the third picture you gave me", which is its own increment.
- [ ] **THE CROP ANCHOR DEPENDS ON A CDN RACE, so one code plus one set of
      photographs still has two possible pictures.** `analyzeImage` uses
      tfjs/blazeface loaded at runtime from jsdelivr; whether it arrives before
      the analysis runs changes the energy centroid every fragment crops around.
      Entirely pre-existing and orthogonal to the code, but it is the one
      remaining hole in "same code, same collage" and it belongs on this list
      until the analysis is either deterministic or recorded.
- [ ] **The share code cannot express an off-roster FRAME SHAPE.** Aspect
      travels as an index into the seven-value roster, so a project saved with a
      hand-set aspect (1.33, say) encodes to the NEAREST roster value. That is a
      bounded, documented loss and it beats what it replaced (`findIndex` = -1
      → index 0 → SQUARE, silently), but a code minted from a loaded legacy
      project is not exact. Fix, if a real one is ever hit: an exact 4-char
      aspect appended to the middle group, read by length like the others.

- [ ] **A MOVE IS ONE ROSTER PICK FOR THE WHOLE COLLAGE, and the speed is not a
      control.** Same shape as the look's own open rung, and the same fix: the
      cycle length is a constant (`MOVE_CYCLE_SEC = 12`) and every fragment
      takes the same move. Per-fragment moves and a speed slider are both UI
      changes rather than engine changes — `sampleMove` already takes the spec
      per slot — but the moment a speed is user-set it has to be SNAPPED to a
      grid on the way in and given a field in the code, exactly as `snapRoll`
      does for the sliders, or the round trip stops being an equality.
- [ ] **THE STILL PREVIEW OF A MOVING COLLAGE IS ITS FIRST FRAME, so at rest it
      looks identical to a still one.** A deliberate consequence of rest-at-zero
      and the right default (the preview agrees with the export's opening
      frame), but it means the chip row is the only thing telling you a move is
      on until the Stage mounts and starts. The honest next cut is a scrub or a
      "show me" that runs one cycle, which is the same widget the timeline rung
      wants anyway.
- [ ] **THE MOVE IS NOT IN THE SVG, and that is a format limit rather than a
      decision.** The vector export draws one instant, and a still is what an
      SVG is for — but SMIL/CSS animation inside an SVG is real and Inkscape
      opens it, so "the exported SVG is the project" (THE POST) currently loses
      the move on the way out even though the manifest carries it. The manifest
      is the reason this is only a display gap: reopening the file restores it.
- [ ] **THE REALTIME RECORDER ONLY CAPTURES WHAT THE SPEAKERS ARE PLAYING, and
      the label promises intent.** `applyMutes` sets every source's graph gain
      from `audible` (monitor AND intent), and `captureStream` taps `masterGain`
      — so a REALTIME take made with the monitor off is silent, for clips and
      now for music alike, while the Record tooltip says "sound from the music".
      Entirely pre-existing and invisible on any device that takes the OFFLINE
      path (which is the default, and which honours intent — that is what
      `describeAudioSources` exists for), so this bites only where WebCodecs is
      missing. It is not a one-line fix and that is the point: the element's own
      `muted` is what gates signal INTO the graph, so honouring intent without
      the monitor means UNMUTING THE SPEAKERS for the duration of the take. The
      honest cut is either to say so on the button when the realtime path is the
      one that will run, or to raise the monitor for the take and put it back.
- [ ] **A SOUNDTRACK IS DECODED IN FULL, however long it is.** `prepareOfflineAudio`
      bounds the TAKE (`MAX_PCM_BYTES` against `seconds`), not the DECODE: the
      whole file goes through `decodeAudioData` before anything is windowed. For
      clips that was fine — an imported clip is a clip. Music is different in
      kind: dropping a 45-minute DJ set under a 10 s collage is an ordinary
      thing to want, and it decodes 45 minutes of PCM (~500 MB at 48 kHz stereo
      float) to use 10 seconds of it. Raised by the adversarial audit; not a
      correctness bug and not reachable from the fixtures, which is exactly why
      it needs writing down rather than fixing in a hurry.
- [ ] **THE MIX HARD-CUTS AT THE END OF THE TAKE.** Ten seconds of music under a
      collage stops dead on the last sample, mid-phrase, which is the single
      most amateur-sounding thing a video editor can do and the reason CapCut
      auto-fades. It is not new (a clip's audio has always ended this way) but
      music is what makes it audible, because music is the thing that is still
      playing at t = duration. The honest fix is NOT another node or another
      envelope: `mixSources` already walks the whole rendered buffer sample by
      sample for the true-peak limiter, so a fade is a few lines in the SAMPLE
      DOMAIN at a place the code already visits, and it would cover clips and
      music together rather than only the source that happens to be new.
      Deliberately not taken this cycle: it changes the last ~0.6 s of EVERY
      export the app has ever produced, which is a decision to make on its own
      and not a rider on a feature.
- [ ] **THE MUSIC DOES NOT TRAVEL, in a code OR in a project file.** A
      composition code is a source-independent RECIPE, so a track cannot ride it
      for the same reason photographs cannot — third on the "in the app but not
      in the code" list after pinned fragments and the title. The project file
      and the SVG are different: they DO carry bytes (every photograph, base64),
      so a soundtrack could ride there and does not. `svgProject` embeds
      `<image>` elements the format defines; audio would need a private
      `<metadata>` blob, and a three-minute mp3 is 3 MB of base64 inside a file
      Inkscape has to parse. Reopening a project therefore restores the collage
      and silently loses its music, which is exactly the "absent means keep
      whatever is on screen" shape already scarred here — the honest first cut
      is for the loader to SAY the file had music rather than to grow the
      format.
- [ ] **A SOUNDTRACK IS ONE TRACK, AND THE LAST ONE PICKED WINS.** Two music
      files dropped together take the last and flash a notice. Fine for "music
      under this collage", wrong the moment anyone wants a voiceover UNDER a
      music bed — which is two sources at two levels, i.e. the volume rung
      above, not this one. The Stage holds `track` as a single field; making it
      a list is mechanical (every seam already loops over clips) but the UI
      question — per-source level — is the actual work.
- [ ] **`refreshMoveCrops` re-crops EVERY fragment every frame while anything
      moves, including fragments whose picture is not visible.** The whole draw
      list, unconditionally, at 60 Hz. It is the honest first cut — a few dozen
      small objects of young-generation garbage, paid only when moving — but the
      obvious economy is to skip items whose source has not been decoded yet,
      and the real one is to write the eight numbers in place instead of
      allocating a `CropGeometry` per item per frame. Measure before doing
      either: on a phone with the realtime budget already capping decoders, this
      may not be what costs the frame.

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
- **WEBKIT REFUSES A BLOB INTO INDEXEDDB, SO CRASH RECOVERY WAS A NO-OP ON EVERY
  iOS BROWSER FROM THE DAY IT SHIPPED.** Measured, same page, same code:
  plain object OK / ArrayBuffer OK / Uint8Array OK / **Blob → transaction error
  with an EMPTY name and an EMPTY message, then abort**. Chromium stores Blobs
  happily, which is exactly why nobody saw it: the whole suite was chromium-only
  (`--project=chromium`), and the two WebKit projects in `playwright.config.ts`
  — the only iOS-shaped coverage this repo has — were never pointed at this
  feature. Because both stores are written in ONE transaction, one Blob took the
  manifest down with it: nothing persisted, no banner ever appeared, and the
  failure was *silent by design* (the store fails soft on purpose). A feature
  whose premise is "a phone browser runs out of memory" did nothing on the
  phone. Fixed by storing `ArrayBuffer` + a mime string and rebuilding the Blob
  on the way out. **Three general shapes: (1) a capability that is universal on
  your dev engine is not a capability, it is a coincidence; (2) fail-soft
  insurance hides its own total absence — if it can silently do nothing, some
  engine is silently doing nothing; (3) a config that HAS the other engines and
  a habit that never invokes them is worse than not having them, because the
  coverage looks present.** Standing rule: anything touching storage, codecs or
  media runs `--project=webkit-desktop --project="Mobile Safari"` before ship.
- **THE STORAGE FORMAT WAS COPIED FROM THE DOWNLOAD FORMAT, AND THE BYTES CAME
  WITH IT.** Crash-safe autosave stored the session as the same `.collage` ZIP a
  manual Save produces, argued for as "one format, no drift" — which reads as
  discipline and cost everything, because the archive carries the image BYTES.
  Every debounce therefore re-fetched and re-zipped the whole pool: nudge a
  slider on a twenty-photo project and 1.5s later ~80MB moved on the main
  thread, to persist a manifest change of a few dozen characters. IndexedDB
  stores Blobs natively; the zip only ever existed to make a FILE, and a stored
  session is not a file. **The general shape: a serialization format encodes the
  cost of its DESTINATION. Reusing one across destinations inherits a cost that
  had a reason somewhere else.** The drift argument was real and survives — the
  manifest and the hydration path are still shared; only the container split.
- **THE PATH THAT FORGOT `onerror`, AGAIN, IN THE SAME FILE.** `loadProject`'s
  archive branch awaited `imgElem.onload` with no `onerror` and no timeout;
  `loadFromSVG`, twenty lines below in the same module, always handled it. One
  asset the browser refuses to decode — a blob truncated by a quota failure, a
  4K frame on a phone at its memory line — fires `error`, never `load`, and that
  promise never settles. Open, or Restore, then hangs FOREVER: no picture, no
  message, no failure to report. The user's words were "endless loop of restore",
  and they were describing a HUMAN loop: tap, nothing, reload, the offer is back,
  tap, nothing. **A promise awaited on a success event with no failure event is
  not slow, it is stopped — and a stopped path looks exactly like a broken
  button.** Pair rule shipped with it: a restore that cannot succeed CLEARS the
  session, or the offer returns forever.
- **THE THUMBNAIL TIER WAS DROPPED ON THE WAY BACK IN, SO RECOVERING MADE THE APP
  SLOWER THAN THE CRASH DID.** Upload builds `previewSrc` as a ≤1024px JPEG and
  the app draws `previewSrc` EVERYWHERE (`stage.ts` states the contract in its
  own comment). Both restore paths set `previewSrc` to the full-resolution
  original — one line, no error, no warning — so every restored project silently
  promoted its whole pool to full-res previews: a 4032×3024 photo is 15.5× the
  pixels of its thumbnail, re-decoded on every drag, ~48MB resident each. The
  editor was permanently worse AFTER recovering than before, which pushes the
  phone back toward the same OOM that started it. Missed by the e2e because the
  fixtures are 1400×1000 — a 1.87× delta where a real photo is 15.5×. Found by an
  adversarial subagent reading the consumers, not the feature. **Two general
  shapes: (1) a derived tier that is REBUILT on one path and ALIASED on another
  will diverge silently, because aliasing is always type-correct; (2) fixtures
  chosen for speed can sit entirely inside the regime where the bug does not
  exist.**
- **:5173 WAS STILL THE PLAYWRIGHT DEFAULT.** Every spec's header documented
  `COLLAGE_BASE_URL=http://localhost:5199/` as the way to avoid attaching to
  Persona 500's dev server — while `playwright.config.ts` kept `baseURL:
  'http://localhost:5173'` with `reuseExistingServer`, so the documented hazard
  WAS the default and the safe path was a thing everyone had to remember. Now
  5199 with `--strictPort`. **A convention that lives only in comments while the
  config contradicts it is not a convention, it is a trap with a warning label.**
- **A PAUSE THAT COVERS EVERYTHING AND A REPLAY THAT COVERS ONE KIND.**
  `beginOfflineRender` calls `pauseAll()`; `endOfflineRender` replays from
  `offlineWantPlay`, a list only CLIPS are ever put on. Adding the soundtrack to
  `pauseAll` — obviously correct on its own — therefore made every export stop
  the live music FOR GOOD, with no control that revives it: the chip toggles
  INTENT, and the intent never changed, so the one button that looks like the
  answer does nothing. Nothing saw it. The unit sweep is about the mixer row;
  all five e2e assertions were about the exported FILE, which was perfect; the
  preview is simply silent from the first take onward. Found by an adversarial
  audit that drove a real browser and probed `document.querySelector('audio')`
  before and after a take (paused=false → paused=true, currentTime 0.00).
  **The general shape: a stop-everything and a start-the-ones-I-know-about are
  not inverses, and the asymmetry is invisible until something new is stopped.**
  Now covered by soundtrack.spec T4, which is red on the pre-fix code.
- **`liveMode` PROMISED A SURFACE THAT WAS NOT RENDERED.** It gates the dock's
  portal bar and the Export sheet's video offer, but the Stage itself only
  exists inside the `images.length > 0` branch. Both older terms hid this by
  accident — `moving` already requires images and a clip cannot exist without
  the frames it landed — and MUSIC is the one source that can arrive before any
  photograph. Result, measured in a real browser: drop an mp3 on an empty app
  and you get 13px of empty chrome and an Export sheet offering a video whose
  recorder handle is null. The precondition now lives in `liveMode` itself
  rather than being re-derived at each use, which is also what makes the dock
  bar's condition sayable in one word: "is the Stage mounted".
- **A THREE-STATE BUTTON WITH A TWO-STATE NAME, and the e2e is what found it.**
  The music chip's speaker has three states, not two, because music arrives IN
  the piece (adding it is an explicit act about sound) while the MONITOR starts
  off (browsers only autoplay muted media). So the first press means "let me
  hear it", the second means "take it out of the file" — deliberate, and the
  right behaviour. The `title` said so. The **accessible name did not**: it read
  `Mute the music` in a state where pressing it unmutes the monitor and mutes
  nothing. Caught because the e2e drives by ROLE AND NAME, clicked the thing
  called "Mute the music", and then could not find the muted state it had just
  asked for — a test written against the visible label would have sailed past,
  and a screen-reader user would have been told the opposite of what the button
  does. The fix is one string (`trackAction`) that the title, the accessible
  name and the handler's branch all read, so the button cannot say one thing and
  do another. `aria-pressed` still tracks INTENT (what the file will carry),
  because with three states the name and the pressed-ness are genuinely two
  different facts.
- **A GATE NAMED AFTER ITS OLD REASON: `liveCount > 0` MEANT "IS THERE ANYTHING
  TO RECORD", AND STOPPED MEANING IT TWICE.** Three dock controls — the monitor,
  the Record button, and `recorderRef.canRecord` — were gated on the number of
  live VIDEO DECODERS, which was the same question as "can this Stage produce a
  take" right up until THE MOVE made a photographs-only collage recordable, and
  then again when music did. With music and no video the monitor button rendered
  DISABLED, so the one thing the user had just added was the one thing they
  could not hear. Renamed to `takeable` and widened. The general shape: a
  boolean named after the mechanism it currently reads survives every change to
  what it is actually asking.
- **A REALTIME BUDGET LEAKED INTO THE FILE, so the export FROZE every clip the
  device could not PLAY AT ONCE — while mixing that clip's SOUND in anyway.** The
  decoder caps (`detectStageCaps`: mobile 3, desktop 4-8) are a REALTIME limit —
  they exist so live compositing keeps up with a clock. But the offline export
  (`renderOffline` → `stage.renderAtTime`) draws only `c.live` clips, so a clip
  the realtime budget deferred rendered its extracted STILL into the FILE, frozen
  for the whole take. The tell that it was a leak and not a limit: the offline
  AUDIO mixer (`describeAudioSources`) had ALREADY been fixed to ignore the cap —
  its own scar, three entries down about `live` — so the export played the
  deferred clip's sound over a picture that never moved. Two readers of one
  resource, and only ONE of them had been told the resource was realtime-only.
  The fix is the same shape as that audio one: `beginOfflineRender` lifts the
  caps and re-admits every clip, `endOfflineRender` restores them and evicts back
  to the realtime budget. Two general lessons. **A cap justified by one cost
  (keeping a clock) must be re-examined at every reader that does not pay that
  cost** — the offline path pays no clock, and already overrode the realtime
  BACKING-WIDTH cap for exactly that reason, so the decoder cap was the one
  realtime budget nobody had followed through. And **when you fix "a realtime
  limit silently decided what the file contains" for one track, grep for every
  other track reading the same limit** — the audio fix and this video fix are the
  same bug in two media, filed a cycle apart. Also filed: the OVER-BUDGET seat is
  safe because nothing offline PLAYS the clips — a seek on a throttled decoder
  degrades to its last frame via the 400 ms `seekClipTo` timeout, never a crash —
  and a just-admitted clip needs `ensureClipReady` before its first seek or that
  frame is a still (its `videoWidth` is 0 until metadata lands; `spanOf` alone is
  not enough — it can be non-zero from `hintDur` with no dimensions yet).
- **A MEASUREMENT THAT LOOKS LIKE A PROOF AND IS ACTUALLY MEASURING THE
  BACKGROUND.** The title's first e2e counted DARK PIXELS in a band, on solid
  near-white tiles, reasoning that the only dark thing in the frame could be the
  caption's scrim. It could not: the layout's own GUTTERS are dark, and on a
  `Balanced` grid they put a dark line in essentially every row. Measured, the
  bottom band of an UNTITLED export already read 5.1% dark, and the titled one
  6.1% — so the assertion that the caption reached the file was resting on a
  1-point difference inside a signal that was 84% gutter, and the "how tall is
  the caption" metric returned 100% of the frame. The fix is not a better
  threshold: every check now DIFFERENCES the render against the same
  composition rendered untitled, which cancels the gutters exactly and leaves
  the caption and nothing else. Generalised: when a proof rests on "only X can
  produce this signal", enumerate what else produces it before trusting the
  number — and prefer a differential against a baseline you control over an
  absolute threshold against a scene you do not.
- **A FEATURE THAT IS NEVER CALLED IS NEVER WRONG, AND THAT IS NOT THE SAME AS
  BEING RIGHT.** `encodeRoll`/`decodeRoll` were written, documented with a
  promise in the module header, covered by two unit sweeps, and imported by
  nothing but those sweeps. Wiring them to the UI took an afternoon; making them
  TRUE took the rest of the cycle, because the moment a real composition was fed
  through them four separate fields could not survive the trip — and every one
  of those defects had been sitting in a green test suite for months. The sweeps
  were not weak: they asserted round-trips over ROLLED rolls, which is the one
  region of the space where the codec happened to be exact. **Coverage measured
  over the inputs a function currently receives says nothing about the inputs it
  is about to receive.** When you connect a dormant module, audit it as new code.
- **`Math.max(0, indexOf(x))` IS A SILENT WRONG ANSWER WEARING A DEFAULT'S
  CLOTHES.** Four fields used it. `LAYOUT_ORDER` held only the 23 generators, so
  every one of the five legacy modes — including `minimal`, **which the app boots
  on** — returned -1 and encoded as index 0, a completely different construction.
  The background index did the same for any colour off the eight-value roster,
  and the "Average" swatch derives one from your photographs, so a paper-white
  collage encoded as near-black. `-1` means NOT REPRESENTABLE and is information;
  clamping it to 0 destroys that information and substitutes a plausible-looking
  neighbour. Either widen the space (the legacy modes are now appended, so every
  index already minted is stable), carry the value exactly (the background now
  travels as 24 bits and the index only survives to degrade a truncated code), or
  return null — but never quietly pick element zero.
- **QUANTISING ONLY REPRODUCES EXACTLY IF THE STATE IS ON THE GRID, AND NOBODY
  HAD PUT IT THERE.** The codec's docstring argued — correctly — that quantising
  keeps a code short AND makes a shared roll reproduce exactly rather than
  approximately. The argument holds only for states that are already on the
  quantisation grid, and `rollDice` drew entropy, gutter and zoom from CONTINUOUS
  ranges. So the very first encode of a fresh roll already lost something, and
  the chaos grid (1/63) did not even contain the chaos slider's own step (0.01),
  so a hand-tuned composition was off-grid too. The fix is one line in the right
  place — `rollDice` returns `snapRoll(...)` — plus choosing the grid to CONTAIN
  the UI's steps rather than the other way round. A rounding argument in a
  comment is a claim about a value's provenance, and provenance is exactly what
  a comment cannot enforce.
- **AND I DID IT A SECOND TIME, IN THE SWEEP, IN A COMMENT.** The unit sweep
  sampled `count: 2 + Math.floor(rnd() * 400)` under the comment "the count
  slider bottoms out at 1 and the codec floors at 2; the app's own
  one-fragment-per-source rule never goes below 2 in practice" — an EXCUSE for
  excluding the failing value, written directly above the line that excluded it,
  and it was wrong on the facts: the stepper floors at `Math.max(1, …)` and
  disables only once you have landed ON 1, so one fragment is a resting state.
  Both codec floors read `Math.max(2, …)`, so counts 0, 1 and 2 all minted the
  SAME string — the codec was not injective over states the UI can rest in — and
  a one-fragment collage opened as two, silently, with a visibly different
  canvas. The e2e missed it too, because its stepper loop stopped at 3. Fixed on
  three sides: the floors are 1, the sweep pins 1/2/3 BY NAME plus injectivity
  rather than trusting a sampler, and T7 now drives the stepper all the way down.
  **The same avoidance appeared twice in one cycle in two different files, both
  times as prose justifying a bound.** A comment explaining why a value is out of
  scope is the highest-yield place to go looking.
- **I WROTE A TEST HELPER THAT FILTERED OUT THE FAILING HALF OF THE SPACE, AND
  DOCUMENTED WHY.** `rollUsable()` re-rolled until the composition asked for at
  least as many fragments as there were sources, with a docstring explaining that
  below that line "the app grows the count to cover the sources … it would make a
  code applied BEFORE the upload land on a different count than one applied
  after." That is not a precondition. That is the bug, written down, in the
  helper that stopped anything from seeing it — and all five tests called it, so
  the suite was green over exactly the half where the feature worked. An
  adversarial lens measured the other half in minutes: a 3-fragment code opened
  with 6 photographs produced 6, and then the address-bar rewrite replaced the
  sender's code with the wrong one 400ms later, so what they were sent could not
  even be recovered. **If a helper's docstring explains why a case is excluded,
  the case is the finding.** Read your own comments as evidence.
- **THE FIRST FIX RACED REACT, AND "IT WORKS" WAS THE ONLY THING TESTING IT.**
  Honouring the code's count needed the auto-follow effect to stand down for the
  drop the code was waiting for, so the first cut set a ref and cleared it in the
  ingest's `finally`. It never once worked: the upload loop yields with
  `requestAnimationFrame`, which resolves BEFORE React flushes passive effects,
  so the flag was already cleared by the time the effect read it. Rewritten as a
  drop marker in STATE, the ordering is React's own and there is no window at
  all. **A cleanup whose correctness depends on when a frame lands is a race
  wearing a tidy-up's clothes** — put the marker in the same queue as the data.
- **A COUNT AND A COUNT ARE NOT THE SAME COUNT.** The first fix then pinned the
  code's count onto the next import unconditionally — right for a number the user
  CHOSE, wrong for one the app DERIVED from "you happened to have six
  photographs". The two are indistinguishable once serialised, and the address
  bar now carries this page's own code, so a plain REFRESH replays it: a derived
  6 would have been pinned onto every later pool forever. The app already knew
  the difference (`countTouchedRef`) and the code did not, so the code learned to
  carry it. **When a value can be a decision or a default, the serialisation has
  to say which** — a number alone is not enough information to apply it correctly.
- **A NEW BUTTON RENAMES EVERY OLD ONE THAT SHARED ITS WORD.** The strip's
  "Open" is the second control on the page called that — the Header's has opened
  a saved project since the beginning. Nothing about the Header changed, and yet
  `project-roundtrip.spec.ts` started failing on a click that had worked for
  months, because `getByRole('button', { name: 'Open' })` matches on a substring
  and now found two. The test was right to fail: an accessible name is how
  somebody navigating by voice or by a screen-reader's element list ADDRESSES a
  control, so two controls answering to "Open" is an ambiguity for them before it
  is one for Playwright. Fixed on both sides — the new button carries
  `aria-label="Open the pasted composition code"` (which still CONTAINS its
  visible label, so label-in-name holds) and the old test asks for
  `{ name: 'Open', exact: true }`. **Adding a control edits the namespace every
  existing by-name selector reads from; run the whole suite, not the new spec.**
- **ALMOST EVERY MANGLING OF A VALID CODE WAS ANOTHER VALID CODE.** The seed is
  the last field of the last group and the only one free to vary in length, so
  lopping four characters off the end read as a smaller number and the code
  opened — cleanly, silently — as somebody else's collage. For a string whose
  entire job is to survive chat clients that wrap, truncate and autocorrect, "no
  error case" is the error case. A checksum was the answer, but the FIRST one was
  a position-weighted sum mod 36 and it only caught 88.9%, because 36 is not
  prime: at every position whose weight shares a factor with it, whole families
  of single-character changes multiply to zero and vanish. A multiply-and-mix
  chain over two characters caught 99.9% (17,952 of 17,964 manglings), and the
  remaining 12 are the 1-in-1296 floor. Two lessons, and the second is the one
  that generalises: **a serialisation with no redundancy cannot distinguish
  damage from a different message**, and **a checksum's modulus and its weights
  must be coprime or half its positions are blind.** Measure the catch rate; do
  not reason about it.
- **A GUARD THAT COVERS THREE OF THE FOUR GROUPS IS A GUARD WITH A HOLE.** The
  checksum lived in `encodeRoll` and covered the three groups that function
  emits. `encodeState`, one layer up, appends a fourth for the shuffle — and
  every single mangling that survived the sweep had landed in it. The fix was to
  fold the upper layer's bytes into the lower layer's checksum rather than to add
  a second one. **Ask what your integrity check does NOT cover, then go and look
  at whether anything lives there.**
- **`padStart` SETS A MINIMUM, AND EVERY READER TREATED IT AS A MAXIMUM.** The
  code is read back by slicing at fixed offsets, so a field that needs one more
  character than it was given does not clip — it lengthens its group and shifts
  every later slice along by one. The result is not a rejected code, which would
  be fine; it is a code that decodes CLEANLY into a different composition. Found
  by probing the field ceilings by hand rather than by any test: `count` at
  36³ = 46,656 made the reader see 1,296 fragments and take the chaos value out
  of the seed's digits. Unreachable with the stepper (twenty minutes of holding
  it down), one keystroke away in a saved project file. Two fixes, and the second
  is the one that lasts: a single `fw()` helper clamps EVERY fixed-width field to
  its own capacity instead of fixing them one at a time, and the sweep now
  asserts each roster against the width that carries it, so a twelfth twist mode
  or a 1,300th layout fails a test rather than silently corrupting codes. **Ask
  what a serialiser does when a value is one larger than you imagined — if the
  answer is "the next field moves", the format has no error case at all.**
- **TWO LISTS OF THE SAME THING DRIFT, AND THE DRIFT HIDES INSIDE THE TOLERANCE
  THAT WAS SUPPOSED TO ABSORB IT.** The frame-shape chips were typed by hand as
  0.666 / 1 / 1.77 / 0.5625; the dice rolled from `ASPECTS` = …0.6667…1.7778….
  Two of the four chips sat a rounding error off the roster, and NOTHING could
  see it: the chip's own active test is `|aspect - v| < 0.01`, the canvas
  difference is 2px of height at 1200 wide, and the encoder's `findIndex` used
  the same 0.01 tolerance, so it matched. It only became visible when the code
  had to round-trip: encode found the roster value, decode returned it, and the
  collage moved. The chips now read the roster. **A tolerance that makes two
  values interchangeable for a comparison does not make them interchangeable for
  a round trip** — and a test built from the same tolerance is a mirror.
- **A CLAMP THAT KEEPS A LOOP REGION SAFE ALSO CHANGES ITS PERIOD, and the period
  is the shared quantity.** `audioPlan` clamped `loopEnd` into the decoded buffer
  — correct, a loop region past the buffer is undefined behaviour — and by doing
  so silently made the sound's lap length the AUDIO's instead of the WINDOW's.
  Everything local was right: the region was inside the buffer, the IN point had
  not moved, the offset was the picture's position, and the first lap was
  perfect. Only the SECOND lap was wrong, and then every lap after it. The
  general shape: when two timelines must agree, a bound applied to one of them is
  not a safety measure, it is a change to the contract. Ask what the clamp does
  to the PERIOD, not just to the range.
- **ONE NODE CANNOT EXPRESS A SIGNAL THAT IS NOT PERIODIC AT ITS OWN LOOP
  LENGTH.** The instinct on finding the above was to compute a better `loopEnd`.
  There isn't one: the clip's sound is "1 s of tone then 2 s of nothing, every
  3 s", and an `AudioBufferSourceNode` loop plays a contiguous region forever. No
  choice of loopStart/loopEnd produces silence in the middle. The fix had to
  change the SHAPE of the answer — a schedule of N starts, not a plan of one —
  and the API changed from `audioPlan` returning a config to `audioSchedule`
  returning a list. When no parameter value is right, the parameter is the wrong
  question.
- **THE LIVE PREVIEW WAS ALREADY CORRECT, AND THAT IS THE SPEC.** A `<video>`
  element's audio track simply runs out while its picture keeps going, then both
  restart on the wrap — which is precisely the lap schedule. Every earlier scar
  in this file is the export drifting from the preview; this one is the export
  drifting from the preview in the one place nobody had thought to look, because
  the preview reached the behaviour for free and the export had to construct it.
  When the export needs code to reproduce something the preview gets from the
  platform, that is where to look for the next one.
- **A DUTY CYCLE AND A LONGEST-RUN ARE BOTH INVARIANT UNDER TRANSLATION, so a
  test built from them says HOW MUCH and HOW LONG and never WHERE.** T7's first
  cut measured the exported audio's envelope in 0.25 s slices and asserted the
  fraction that were loud plus the longest silence — which does separate the
  drone (100% duty, no silence) from the fix (40%, 2.00 s), and separates nothing
  else. An adversarial audit rebuilt the measurement over the real fixture and
  showed that a render whose every lap is ONE SECOND LATE — a full second of
  audible desync — scores duty 40%, longest silence 2.00 s, peak 0.1247: digit
  for digit the correct render's numbers. So did "sound in the gap instead of on
  the beat". The repair is to put the PICTURE in the assertion: the file has
  sound at output `t` exactly when `t % LAP < SOUND`, asserted slice by slice.
  Measured across seven candidate renders, the two statistics pass 4/7 and the
  phase anchor passes 1/7. If an assertion would hold for a translated copy of
  the signal, it is not testing a timing fix.
- **A MODEL THAT RETURNS THE FIRST MATCH CANNOT SEE AN OVERLAP.**
  `schedulePositionAt` walks the starts and returns the first one covering an
  instant, so two laps sounding at once look identical to one lap sounding — and
  in the real graph they SUM and that stretch plays at double level. The A/V
  agreement audit would have passed a schedule with overlapping laps. Non-overlap
  needed its own assertion, checked on the STARTS rather than through the model.
  A model can only be trusted where the thing it models is known not to do
  something else.
- **A GUARD INHERITED INTO A PATH ITS REASON DOES NOT COVER LEAVES A HOLE ONE
  SLIDER DETENT WIDE.** `audioPlan` refuses a loop region under 10 ms because a
  node's WRAP is unstable below that across engines. The first cut of
  `audioSchedule` decided "is this a straddle" by reading `plan.loop` — and so
  inherited that refusal into the LAP path, WHICH NEVER WRAPS. A window
  overlapping its audio by 9 ms therefore took the single-node path and played
  one blip for the whole take where the picture asks for one per lap: measured,
  15 blips collapsed to 1 on a 30 s take, and the trim slider's step is 0.01 s,
  so it sat exactly one detent from correct. Found by two independent audit
  lenses, neither of which was looking for it. Ask what a guard is FOR before
  reusing the flag that carries it; the 10 ms floor belongs to the period being
  scheduled (`L`), not to the one that happens to be nearby.
- **A TEST THAT DEFINES THE BOUNDARY THE WAY THE CODE DEFINES IT CANNOT SEE THE
  BOUNDARY BEING WRONG.** I16's first cut read the straddle off `plan.loop`,
  exactly as the code did, so the sliver above was invisible to 5.4M checks: the
  test and the defect agreed. Rewritten to derive the straddle from the WINDOW
  independently, coverage went 738 → 1,440 straddles and reverting the fix now
  fails 1,284 assertions. An invariant must state the property in its OWN terms
  or it is a mirror.
- **A DOCSTRING THAT ARGUES SOMETHING IS UNREACHABLE IS A CLAIM, AND A CORRECTION
  IS ANOTHER CLAIM.** `MAX_AUDIO_LAPS` was documented unreachable because "a lap
  is at least `MIN_WINDOW_SEC` of output time whatever the rate — sync sets
  `rate = length / target`, so `length / rate` IS the target". An auditor
  falsified it by reading the reasoning rather than the code, and the correction
  written in response BLAMED THE RATE CLAMP — which a second auditor then
  falsified by measurement: where `RATE_MAX` engages it LENGTHENS the lap
  (9.000 ms unclamped → 9.375 ms clamped), so it strictly REDUCES the node
  count. Swept over 23,040 clip-cases the rate clamped in 2,940 and the shortest
  lap was exactly 0.150000 s. The real mechanism is `normaliseWindow`'s own floor
  clause — a span at or under `MIN_WINDOW_SEC` comes back WHOLE, so a source FILE
  under 150 ms yields a sub-150 ms window that becomes the sync reference.
  Two wrong explanations for one true fact, the second written while fixing the
  first. A comment that explains WHY is load-bearing and must be measured like
  code; if it cannot be measured, state the fact and not the mechanism.
- **A ZERO-LENGTH REQUEST WENT DOWN THE UNBOUNDED BRANCH, so the one case asking
  for NOTHING got EVERYTHING.** The mixer tested `duration > 0` before passing a
  stop length to `node.start`, and fell through to the two-argument form
  otherwise — where a `BufferSource` plays from `offset` to the end of the
  BUFFER, i.e. straight through all the material the user trimmed away. Both
  models read `local >= duration` as "already over", so the mixer was the only
  reader of that number that disagreed, and it disagreed maximally. Latent, not
  live (it needs `startAt > 0`, which nothing sets today) and inherited from the
  single-plan code. Guard on `!== null` and skip the entry, never `> 0`: a
  falsy-guard on a quantity whose zero is MEANINGFUL is the same bug as
  "absent means keep whatever is on screen", one scar further up this list.
- **EVERY CLIP MUST LAND IN EXACTLY ONE BUCKET, and this one block produced the
  same "lands in none" defect TWICE in a single cycle.** `mixSources` sorts each
  clip into wired / silent / failed, and the reason ladder reads those counters
  to tell the user what happened. First instance: an empty-but-not-silent
  schedule fell through both, so `wired === 0 && silent === 0` reported "Mixing
  the sound failed." for a correct render. Second instance, introduced BY THE FIX
  FOR THE FIRST — the new zero-duration skip can skip EVERY entry of a non-empty
  schedule, and `if (started) wired++` then fires for neither. Same wrong message,
  new route, one edit later. Caught by an auditor who bundled the real module and
  ran the real `prepareOfflineAudio` against stubbed Web Audio rather than
  reading it. The lesson is structural, not local: when a function classifies
  into N buckets and something downstream reads the counts, every `continue` is a
  classification decision and must say which bucket. `started === 0` with
  `skipped` SHORT of the list is the genuine third case — those entries threw —
  and correctly stays uncounted.
- **"ONE CLIP'S FAILURE IS THAT CLIP'S SILENCE" STOPS BEING TRUE WHEN A CLIP IS N
  NODES.** The per-clip `try` was written when a clip was exactly one
  `start()` call, so a throw cost that clip and nothing more. With a schedule it
  would abandon every remaining lap AND leave the already-connected ones sounding
  while `wired` recorded the clip as contributing nothing — which feeds the
  "there was nothing to mix" message and can discard a mix that has audio in it.
  Each lap now has its own catch and `wired` counts what actually started.
- **THE TRIM SHEET AND THE STAGE RESOLVE THE WINDOW AGAINST DIFFERENT SPANS, and
  it is safe for a reason worth writing down rather than for luck.** The sheet
  only has `LiveClip.durationSec`; the Stage has `max(EPS, el.duration - EPS)`,
  4 ms shorter. So `normaliseWindow(...).full` can disagree between them, and
  `full` is what decides whether the element keeps its NATIVE loop. Swept 60
  duration/window pairs: 18 disagree, **all in the same direction** — the sheet
  says "trimmed" while the Stage says "whole clip". The dangerous direction
  (`ui.full === true` while the Stage silently turns the native loop off for a
  clip nobody trimmed) **cannot occur**: `ui.full` requires `out === durationSec`
  exactly, and the Stage then clamps that same `out` to its own span, which makes
  it full there too. The disagreement band is also unreachable through the
  control: it is 4 ms wide and the slider's step is 10 ms (100 ms past 60 s). Do
  not "fix" this by inventing a tolerance — record it, and re-check the direction
  if either span definition ever moves.
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
- **A FILMSTRIP LAID OUT BY FRAME INDEX IS A LIE ABOUT TIME.** Frame extraction
  is `strategy: 'smart'`, so the stills a clip hands back cluster wherever it was
  interesting — measured on a six-second fixture: 10 of 12 frames inside the
  first 31%. Rendered `flex-1` (equal widths) those ten fill 83% of the strip
  while the IN/OUT bracket, which is positioned by TIME, sits at 38–60% —
  pointing at pictures that are not the ones about to be cut. Fixed by giving
  each frame the stretch of the clip it is the NEAREST frame to (boundaries at
  the midpoints between adjacent `sourceTime`s). NEITHER this nor the dead
  dimming below was visible to any assertion in the suite; both were caught by
  screenshotting the real sheet and looking at it.
- **A NON-STANDARD TAILWIND OPACITY STEP GENERATES NO RULE AND FAILS SILENTLY.**
  `bg-black/72` is not one of the generated steps, so the overlay that dims
  everything outside the trim window simply did not exist — the class was in the
  markup, the element was in the DOM, and nothing was dimmed. `/70` works. Any
  arbitrary opacity needs the bracket form or a standard step.
- **A MEASUREMENT CAN AGREE WITH THE RIGHT ANSWER FOR THE WRONG REASON.** The
  trim export test measured tones in ONE window from the middle of the take —
  the instrument `video-audio-export.spec.ts` established, and correct for its
  question. Here it PASSED with the audio mixer deliberately ignoring the trim,
  because an untrimmed five-second take is red→green→blue and its midpoint lands
  in the green third, which is exactly the third the trim was isolating. Caught
  only by the red gauntlet, never by reading. A trim test must ask "is a WRONG
  value ANYWHERE", not "is the right value here": five probes across the file,
  loudest reading kept per frequency.
- **A TALLY CANNOT EXPRESS "IT LOOPED".** Forcing every clip onto the trimmed
  code path (native loop off for untrimmed clips too) left the set of thirds
  seen unchanged — the clip simply played once through and froze on blue — so a
  set-based assertion stayed green while the compatibility clause was broken.
  The SEQUENCE is the assertion: a clip that loops returns to an earlier third.
- **A WATCHDOG ON THE COMPOSITOR'S CLOCK IS ONLY AS PROMPT AS THE COMPOSITOR.**
  Holding the trim window from `tick` alone let a clip run ~0.4s past its OUT
  point when the main thread was busy (measured under a harness pulling the
  canvas back 11×/s). Fixed by ALSO enforcing in the `requestVideoFrameCallback`
  hook — the per-presented-frame signal, i.e. the exact moment a clip can newly
  be outside its window. The residual bound is real and stated rather than
  papered over: the live preview holds the window to within one frame; the
  EXPORT is exact, because it seeks by arithmetic instead of racing a clock.
  Assert it structurally ("never two consecutive samples outside") rather than
  with a tolerance — a broken window parks outside for 77 samples, a wrap blip
  is 1, and that is two orders of magnitude of daylight with no threshold to
  argue about.
- **A PROOF WITH NO RUNNER IS A PROOF THAT ROTS.** `video-audio-export.spec.ts`
  had no config of its own, so the only way to run the suite guarding
  `offlineAudio.ts` was the repo default — which points at :5173, Persona 500.
  It now has `playwright.video-audio.config.ts` like every other suite.
- **A GATE THAT IMPORTS NO VIDEO CANNOT SEE THE VIDEO CONTROLS, AND THE VIDEO
  CONTROLS WERE THE PART THAT FAILED.** `mobile-watertight.spec.ts` imported six
  PNGs, so the whole live-stage transport — clip chips, trim, per-clip sound,
  play/pause, monitor, take length, Record — did not exist while it ran, and the
  suite reported the app watertight for months on the strength of the photo-only
  page. Measured at 390px with one video loaded: **ELEVEN controls under the 44px
  law**, from `Stop playing` at 24x28 to `Record video` — the button that starts
  an export — at 32x32. Same class as twist's T4 and one-layout's `complex`, one
  layer up: green for a reason that has nothing to do with the assertion. The
  gate now imports a real video; whatever a test cannot reach, it is silently
  approving.
- **A DECLARED WIDTH IS NOT A WIDTH INSIDE A SHRINKING FLEX ROW.**
  `.ui-stepper__btn { width: 52px }` with the default `flex-shrink: 1` collapsed
  both fragment steppers to **18px at 320px**. Found by the new video-dock gate
  within minutes of it existing, and invisible to the old one for a second
  reason worth separating: those tests read tap targets on the SETTINGS tab,
  where the stepper is not rendered at all. `flex: 0 0 52px` + `min-width: 44px`.
- **AN EFFECT KEYED ON AN INLINE CALLBACK RE-RUNS ON EVERY RENDER, AND A FOCUS
  CALL INSIDE IT IS THEN A FOCUS THIEF.** The trim sheet's modal effect depended
  on `[onClose]` — `onClose={() => setTrimming(null)}`, rebuilt every render — so
  every slider change re-ran it and re-focused the Close button. Measured on the
  real page, keyboard only, and again in a PRODUCTION build: ArrowRight moved IN
  from 0 to 0.01, focus jumped to Close, and presses 2..20 did nothing; Enter —
  the natural "is this thing on?" — dismissed the sheet. Reaching the spec's own
  2.3 s window would have cost 230 Tab+Arrow pairs. Both things that would have
  caught it do not: a DRAG is unaffected (a range keeps pointer capture straight
  through the steal) and so is Playwright's `fill()`, which writes the value in
  one shot. Hold the callback in a ref and give the effect an EMPTY dep list.
  Found by three of the four audit lenses independently.
- **A CSS VARIABLE WITH A FALLBACK FAILS SILENTLY AND LOOKS DELIBERATE.** The
  app's global range track is a gradient stopped at `var(--fill, 50%)`, and the
  two trim sliders never set `--fill` — so both bars painted half green forever,
  with the OUT handle sitting at the far right above a half-full track. Nothing
  errored, nothing was missing from the DOM, and the wrong picture reads as a
  design choice. Sibling of the `bg-black/72` scar: the failure mode of a style
  that does not exist is not blankness, it is a plausible wrong answer.
- **`LayoutItem.id` is a module-level counter, not a function of the layout.**
  `shards` returns `shd-0…` on one call and `shd-24…` on the next for identical
  geometry. Inert today — every consumer and the React key use the ARRAY INDEX —
  and asserted in the sweep (I2b) so the day something keys off it, the record is
  already there instead of the bug being rediscovered.
- **`git checkout --` IS NOT AN UNDO FOR A MUTATION TEST, IT IS A REVERT TO
  HEAD.** Three mutations were planted to prove the new tests go red, each
  followed by `git checkout -- <file>` to put it back. All three went red, which
  was the point — and the cleanup then silently destroyed the cycle's work in
  two of the three files, because `checkout` restores the file as HEAD has it
  and HEAD did not have the feature yet. The third file was worse: it was
  UNTRACKED, so `checkout` errored, the error scrolled past inside a longer
  script, and the mutation stayed in the tree. Fifteen minutes later the sweep
  and the e2e were both still green — on code that had lost the worker's grade,
  lost the codec's look field, and still carried the deliberately broken
  `<filter>`. **A mutation test edits code you have not committed, so the undo
  must be a byte copy you took yourself**, not a VCS operation whose reference
  point is a commit that predates the work. Copy the file aside, mutate, restore
  from the copy, and diff to confirm the restore.

## THE RATCHET (perpetual by construction)
When a capability tier reaches broad parity with CapCut, the north star raises:
the next tier (pro effects, AI-assisted editing, collaboration) becomes the
frontier. Today's ceiling is tomorrow's floor.

## CYCLE LOG (append one line per collage cycle — capability · before→after · proof)
- 2026-08-08 · **[AXIS:COLLAGE] THE SOUNDTRACK — music under the collage**
  (well empty — 0 new, 0 stranded in `building`, read UNSCOPED across all trades
  first; breadth debt 0, so LIVE STATE's stalest-axis rule governed and it named
  COLLAGE.) before→after: **a collage of photographs could be a video and that
  video was NECESSARILY SILENT → you can drop a song under it, hear it while you
  work, and it is in the file.** THE MOVE shipped the time axis last cycle and
  handed this one its own gap: every sample this app had ever mixed came out of
  a video clip's audio track, the picker took `image/*,video/*`, and
  `ingestFiles` rejected an mp3 with "images and video only" — there was no door.
  THE WHOLE DESIGN IS ONE SENTENCE: **a soundtrack is A CLIP WITH NO PICTURE**,
  so it plugs into the five audio seams the Stage already had (element →
  `MediaElementSource` → gain → `masterGain`, an intent flag, one
  `describeAudioSources` row) and **`offlineAudio.mixSources` changed by NOT ONE
  LINE** — the realtime recorder gets it free from `captureStream`'s tap on
  `masterGain`. `lib/soundtrack.ts` (~180 lines) holds only what is particular
  to music: **`span: 0` for EVERY duration** (a container's length is not the
  decoded buffer's — mp3 carries encoder delay and padding — and that hop does
  not round differently, it flips `audioSchedule` into its LAPPED branch and
  cuts a sliver of silence into every repeat forever); intent kept structurally
  free of the monitor (`soundtrackSource` takes no `soundOn` argument, and the
  sweep is what keeps it that way — the recorded bug that made every export
  silent); and a file classifier DISJOINT from `isVideoFile`, so the ambiguous
  containers (.mp4/.webm/.ogg) stay video and every picked file lands in exactly
  one bucket. Music arrives UNMUTED where a clip arrives muted — a clip is a
  picture that happens to have sound, a soundtrack is nothing but sound — and
  **the music restarts when the take does**, beside `moveOriginMs = -1` in
  `setCaptureActive`, or the two recorders open on two different bars.
  PROOF, at the artifact: `5.0s · 30fps · 150 frames · sound`, the MP4 decoded
  back to samples — **1500 Hz at 3114x the 5 kHz control**, measured at the
  MIDDLE of a 5 s take from a 2.0 s file, so it LAPPED; muting the chip gives
  `150 frames · silent` and no decodable audio track at all. Sweep: 4,920
  assertions over 1,080 file shapes and 108 specs, and it BITES — three
  mutations (span carrying the duration, an untyped .mp4 claimed as music, gain
  reading a monitor) each fail it. Regressions green: video-audio-export 4/4
  (its tone instrument was EXTRACTED to `tests/e2e/tone-measure.ts` and is now
  read by both suites rather than copied), motion 5/5, mobile-watertight 6/6,
  `tsc --noEmit` clean, `vite build` clean.
  THREE DEFECTS THE VERIFICATION FOUND, all fixed here: (1) the chip's
  ACCESSIBLE NAME said "Mute the music" in the state where pressing it unmutes
  the MONITOR — found only because the e2e drives by role and name; (2) the
  duration probe was AWAITED before adopting the track, so two quick picks meant
  the FASTEST PROBE won and the other's url was revoked out from under it;
  (3) **the fifth rail button pushed "Clear all" off the bottom of the band on
  every phone with the dock open** — invisible to every existing gate, because
  the rail is absolutely positioned inside an `overflow-hidden` parent and a
  clipped child costs the document no scrollWidth. The threshold was the literal
  `200`, already 16px short of the FOUR-button column it was written for; it is
  now DERIVED from the button count, and the e2e walks each rail button's
  clipping ancestors so the next button cannot reintroduce it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
  **AND THE AUDIT EARNED ITS KEEP AGAIN — a THIRD time on this project.** A
  three-lens adversarial fan-out (lifecycle/ownership · the WebAudio graph and
  the offline mixer · preview-file parity) ran against the shipped diff and drove
  REAL BROWSERS, writing its own probe specs rather than only reading. It found
  what five green e2e assertions could not, because all five were about the
  exported FILE: **`beginOfflineRender` pauses everything and `endOfflineRender`
  replays only CLIPS, so the first export stopped the live music for good** —
  and the chip that looks like the answer toggles intent, which never changed.
  Also confirmed, reproduced in a browser with `createObjectURL` instrumented:
  music dropped before any photograph left 13px of empty dock chrome and an
  Export sheet offering a video whose recorder handle is null, because
  `liveMode` claimed a Stage the `images.length > 0` branch had not rendered.
  Both fixed here, both now covered (T4, T5), and T4 is RED on the pre-fix code
  (`paused=true, t=0.00`). Two further findings are written up on the ladder
  rather than fixed: the realtime recorder captures only what the monitor is
  playing, and a soundtrack is decoded in full however long it is.
- 2026-08-08 · **[AXIS:COLLAGE] THE MOVE — the collage has a TIME AXIS**
  (well empty, breadth debt 0, LIVE STATE named COLLAGE the stalest axis; working
  tree read FIRST, per the scar directly below — nothing was stranded this time.)
  before→after: **a collage was a picture that could contain moving video → the
  PHOTOGRAPHS move too, and a collage of nothing but photographs is now a video
  you can record.** Five drifts on one chip row (Push / Drift / Sway / Pulse /
  Wander), on the dice and in the share code, from ONE pure module —
  `lib/motion.ts`, ~330 lines, `movePhase` (a fragment's bearing, from WHERE IT
  IS) + `sampleMove` (that phase plus a time → a zoom multiplier and an anchor
  nudge) — reaching every render path through the seam they already share:
  `withFocus` re-points `analysis.face`, `withTwist` writes `analysis.twist`,
  `withMove` writes `analysis.move`, and `calculateSmartCrop` reads all three.
  The one thing a move needs that a twist does not is a CLOCK, and an analysis
  has no clock, so the TIME is a fourth argument **defaulted to 0** — and 0 is
  the identity BY REFERENCE (`NO_MOVE`), not by arithmetic. That is the whole
  safety argument and it is measured, not asserted: **27,000 swept setups where
  a move at t=0 is `Object.is`-identical, field by field, to no move at all**, so
  the three surfaces that produce a single frame (still preview, raster export,
  SVG) are provably the build they were, and only the Stage — which both video
  recorders capture and which the offline render seeks — ever passes a real time.
  **THE PREMISE I STARTED FROM WAS WRONG, AND CHECKING IT IS WHAT MADE THIS
  REACHABLE.** I set out to fix "a photos-only collage exports as a video of a
  still", then read the gate: `canExportVideo={liveMode}`, `liveMode =
  clips.length > 0`. A photo collage could not export a video AT ALL. Correct
  while nothing moves and exactly wrong the moment something does — so the gate
  widened to `(clips.length > 0 || moving)`, which costs nothing when nothing
  moves (`syncClips([])` is a no-op, the transport renders per clip and renders
  none, the demand-driven tick idles at zero rAF) and is the difference between
  a feature and a feature nobody without a video could see.
  **PERIODIC ON A FIXED 12 s, NOT ON THE EXPORT'S DURATION**, for two reasons
  about this app rather than about taste: the live preview loops forever and has
  no end to ramp towards (a duration-keyed ramp would need a SECOND time
  contract beside `clipWindow`'s, and the thing this codebase has learned twice
  is that a formula in two places diverges), and the export duration is user-set
  AND silently clipped by the device cap — so the same collage would move
  differently at 10 s and at 30 s, and a capped take would be a different
  picture from the one asked for. Raised cosine, so the turnaround and the loop
  point are both smooth. **The stagger lives in the HARMONIC and the BEARING,
  never in a phase offset** — a phase offset is precisely what would put a
  fragment somewhere other than rest at t=0 and cost the guarantee above.
  **A PAN IS A FRACTION OF THE ROOM ITS OWN ZOOM LEAVES**, so "pan without room"
  is unrepresentable rather than merely tested: the crop is clamped inside the
  image, and a clamped fragment sits still while its neighbours move. 69,000
  crops, 0 clamped; the naive flat 0.25 pan clamps 13,764 of 22,700, worst
  overshoot 1,495 source pixels. **The re-crop is NOT in `drawFrame`** — that
  loop's written contract is "zero allocation" and `calculateSmartCrop` returns
  an object literal, so `refreshMoveCrops` runs off the draw, from the tick and
  from `renderAtTime`, and the draw loop is byte-for-byte the loop it was.
  **THE SWEEP FOUND A SECOND, WORSE HALF OF AN OPEN SCAR.** The ladder carried
  "a code's middle group is read by LENGTH and nothing rejects a LONGER one" as
  untidy-but-unreachable. Adding the move gave the group a THIRD checksummed
  length (18 flag → 19 look → 20 move) and the new sweep turned up the other
  end: `hasLook`/`hasMove` ENTER the checksummed band by length, so lopping two
  or three characters off a real code drops it BELOW the band — 16 or 17 — where
  the guard never ran and the code opened, cleanly, as somebody else's collage.
  Truncation in a chat client is the exact hazard the checksum exists for,
  arriving through the door that decides whether to look. Both ends closed by
  one comparison against `MINTED_GROUP_LENGTHS` = {18,19,20}, and those three
  are safe to name EXACTLY because git says so: the codec was wired to nothing
  until a1797423 (2026-08-07, "the code that was written, documented and never
  called"), so no other length has ever existed in the wild. `rollCode`'s own
  sweep had 16 on the TRUST side while the comment beside it said 15 —
  over-inclusion, now narrowed, with the truncation and the append both asserted.
  **WATCHED GOING RED, all four.** Rest returning a fresh `{zoom:1,ax:0,ay:0}`
  instead of the shared object → I1b red (and I1 still GREEN, which is exactly
  why both exist); pan as a flat 0.25 → I3 and I4 red; the length check deleted
  → I8d red; the harmonic flattened → I6b red. Restored, 19/19.
  Proof: unit **19/19** (`motion.invariants.mjs`) and all 11 sweeps green
  (`grade` and `rollCode` updated for the new group length, not loosened);
  e2e **motion 5/5** on the real UI — the picture measurably moves for every one
  of the five (drift 19.4% of samples / worst 175, sway 15.4/167, push 10.0/159,
  wander 7.9/158, pulse 5.9/139; bars set from the floor of three measured runs
  rather than by taste, after a taste-picked 5% flaked on pulse), STILL restores
  the opening frame, the exported PICTURE is untouched to within one channel,
  the code round-trips, and the row is watertight at 320/360/390/430 with
  scrollW 393 = clientW 393 and every chip 44px. Regression: title 10/10, trim
  9/9, svg-project 16/16, look 12/12, twist 8/8, one-layout 4/4, mobile 6/6,
  roll-code 20/20, composition 10/10, video-audio 4/4, project-roundtrip 1/1,
  `tsc` + `vite build` clean.
  **PRE-EXISTING, NOT FIXED:** `stage-room` R1b and R11, which the entry below
  already records as failing on live's old code. **AND A FALSE RED THAT COST
  REAL TIME:** `playwright.composition.config.ts` had no `workers: 1` where its
  sibling roll-code config does, so its two projects each ran a
  full-resolution worker export at once and timed each other out — chromium
  alone 5/5, Mobile Chrome alone 2/2, both parallel 2 failed, both serial 10/10.
  Pinned serial, with the measurement in the comment, so the next cycle does not
  re-diagnose it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-08 · **[AXIS:COLLAGE] THE POST — the exported SVG IS the project file**
  (and, again, the increment had been BUILT AND STAGED BY A CYCLE THAT DIED BEFORE
  COMMITTING — nothing in any commit, nothing live, a dirty tree with 196 insertions
  in it. That is the SECOND time this exact thing has happened here, after TRIM on
  2026-08-06, so it is no longer an accident: **the well was empty and breadth debt
  was 0, and this cycle's first act was to read the working tree instead of starting
  something new.** A stranded build looks exactly like an idle repo unless you look.)
  before→after: **a collage you could send as a picture or as a recipe, never as
  both → the file you send IS the project.** `loadFromSVG` had been `return null`
  under thirty lines of deliberation about whether the pictures would be
  recoverable, ending on "vectorExport MUST convert images to Base64 — I need to fix
  vectorExport"; that fix shipped long ago and the TODO never heard, so the file
  input advertised `.svg` and the Open button promised "or an exported SVG layout"
  for as long as neither could work. `lib/svgProject.ts` is the one PURE seam
  (string in, string out — no DOM, no fetch) that the writer and the reader both
  ask, which is why the codec is swept under plain node instead of only inside an
  eight-minute browser run.
  **The manifest had to leave the XML comment, and that is a bug the title shipped.**
  XML forbids `--` anywhere inside a comment and `-->` closes one early, and the
  caption is free text that `JSON.stringify` passes through untouched — so
  "DAY 3 -- the rough-in" produced an SVG that is not a degraded picture but a PARSE
  ERROR. The sweep MEASURES that rather than asserting it: **4 of 14 ordinary
  captions produced an ill-formed comment under the old construction**, all 14 clean
  under `<metadata id="collage-project">`.
  **Proof:** `svgProject.invariants.mjs` **2,070 checks, 0 failures** ·
  `svg-project.spec.ts` **16/16 AGAINST LIVE PRODUCTION, desktop AND Pixel 5**, the load-
  bearing one being S1: export an SVG, RELOAD the page so nothing is in memory, open
  the file, export again, and require the two downloads BYTE-IDENTICAL — one
  equality that covers the settings, the caption, the look, each picture's analysis
  floats, each picture's bytes, and the pool's ORDER and LENGTH, which is what
  matters because `arrangeBag` deals from both and one missing source re-deals every
  fragment after it. Regression: title 10/10, look 12/12, one-layout 4/4,
  export-integrity 3/3, roundtrip 1/1, mobile 6/6, source-count 7/7, `tsc` clean,
  `vite build` clean. Composition 9/10 — the documented seed flake, now PINNED
  rather than waved at: the failing assertion is the fixture's own precondition
  (`|previewGap| > 8`, got 6.14 on an unlucky roll of `blobs()`), not the assertion
  under test, and it passed 2 of 3 reruns; this change touches the SVG writer and
  that test reads a raster export.
  **I FOUND TWO OF MY OWN, and both were the gate lying rather than the code.**
  (1) THE MOBILE GATE HAD NEVER SEEN THE THING IT WAS GRADING — again, exactly as
  in trim. S5 measured a header in its RESTING state, while the increment put a NEW
  state in it: on a refused file the Open button stops saying "Open" (4 characters)
  and says "COULDN'T OPEN THAT FILE" (23) in a `ui-btn--compact` sharing a row with
  Export and Save. S6 now FORCES the refusal at 320/360/390/430 and measures the row
  on its own (an overflowing header inside a scroll container never moves
  `documentElement.scrollWidth`). It passes — and was **watched going RED** on a
  bar raised to 999 to prove the numbers are live: the button measures **exactly
  44px** at 320px, clearing the tap-target law with zero margin.
  (2) THE COPY OVERPROMISED. The new Export caption said the SVG "drops back into
  Open exactly as you left it" — untrue for a video project, because `metaForAsset`
  keeps id/name/analysis and drops `clipId`/`sourceKind`, and the option is not
  gated on the video tab. A clip comes back as the frame it drew. The caption now
  says so, because the alternative is a man finding out after he sends the file.
  Named and NOT fixed, both on the ladder with repros: `vectorExport` can emit a
  file `loadFromSVG` will always refuse (a failed `blobToBase64` writes an empty
  href AND still lists the id) — unreachable in ordinary use, since a pool asset's
  object URL is never revoked while it is in `images`, and not a regression;
  and `PROJECT_FORMAT` is written and never read.
  **THE ADVERSARIAL AUDIT EARNED ITS KEEP FOR THE FIFTH TIME IN SIX — 12 agents,
  four lenses, EIGHT CONFIRMED and one refuted**, and it ran against the commit
  rather than the plan: the increment shipped as `bd2f2f61` while the audit was
  still probing, so one verifier materialised HEAD on its OWN port (:5411) to
  keep "as delivered" separate from the fix landing under it mid-run, and then
  reported the discriminator both ways — fails on delivered, passes on the patch.
  That is the standard. Everything below was fixed in the SAME cycle, in
  `1af9a714`.
  (1) **HIGH — SHUFFLE WAS IN NEITHER DIRECTION.** Found independently by two
  lenses. `shuffleTrigger` seeds the deal twice (`createRng(seed + shuffle)` into
  `assignSources`, and again as `arrangeBag({ shuffle })`), the composition CODE
  has always carried it, and the project file carried neither half — so one press
  of Shuffle before an export produced a file that reopened as a **different
  pairing of the same photographs, silently**. Exactly the failure class
  `svgProject.ts`'s own header says it fails closed to prevent, arriving through
  the one door nothing was watching. S1 could not see it because S1's equality is
  only as wide as the state it varies, and it varies none.
  (2) **MEDIUM — `mode` WAS WRITTEN AND READ BY NOTHING.** An export taken with
  Settings open reopened on Layout and re-exported a different manifest, so the
  headline byte-identical guarantee was false for that path.
  `handleRestoreHistory` had always restored it; this path forgot.
  (3) **MEDIUM — THE COUNT LATCH OUTLIVED THE OPEN.** Nothing bumped `dropId`, so
  the NEXT import took the `drop !== dropId` branch, cleared the latch and
  returned WITHOUT reaching grow-to-cover: the first photos added after opening a
  project got no fragment, once, silently — breaking the "nothing uploaded is
  stranded" guarantee the effect's own comment states in full.
  (4) **HIGH — MY OWN FIX FOR THE REFUSAL BROKE THE HEADER.** Swapping "Open" (4
  chars) for "COULDN'T OPEN THAT FILE" (23) took `.ui-topbar__actions` from 317px
  to 390px min-content and shoved EXPORT off the right edge: 94px gone at 320,
  54px at 360, 24px at 390, leaving the primary action a 6.6px sliver. **Every
  gate read clean** — the app sits in a `fixed inset-0` with `overflow: hidden`,
  so those pixels are DESTROYED rather than scrolled and `scrollWidth` never
  moves, and `getBoundingClientRect().width` cheerfully reports 100.6px for a
  button 94px off-screen. And S6, which I had added THIS cycle specifically to
  close the mobile blind spot, measured only the button it had just changed —
  the same mistake one element over. S6 now measures every control on the row by
  its INTERSECTION with the viewport, which immediately found a **pre-existing**
  21px clip of Export at 320px *at rest*, fixed by letting the row wrap when it
  genuinely does not fit (no breakpoint: wider widths are untouched).
  (5) **MEDIUM — THE MESSAGE WAS UNREADABLE ANYWAY.** `.ui-btn__msg` caps at
  108px and the string measures 174px, so it rendered "COULDN'T OPEN…" at EVERY
  width including desktop, with the remainder reachable only via a `title`
  attribute no touch device can surface; and `.ui-btn:hover` (0-2-0) beat
  `.ui-btn--bad` (0-1-0) on background but not colour, painting #1a0505 on
  --surface-3 at **1.25:1** — in precisely the state an error is born in, with
  the pointer still on the button that just failed. `--primary` and `--warn` each
  carry a hover rule and `--bad` simply did not. The sentence now goes to the
  notice toast (this app's own idiom for a failure, and the only surface with
  room), the button changes COLOUR and ICON only at zero pixel cost, and S6
  asserts the settled contrast at ≥4.5:1 — an assertion that first failed at
  3.77:1 by sampling mid-CSS-transition, which is a fact about the ruler, not the
  wall.
  (6) **LOW, now answered by (5):** every SVG exported before this is permanently
  unopenable and nothing said so. The toast says so.
  Named and NOT fixed, on the ladder with its measurement: **opening a project
  never releases the pool it replaced** (8 photos = 15.64 MB → 30.58 MB after one
  Open, 17 of 18 URLs still live). Deliberately not a one-liner —
  `addToHistory(state, images, …)` retains the pool, so blind revocation blanks a
  restored snapshot, and a silently wrong picture is worse than a leak.
  **BACKPORT rider fired, and came back clean on all three classes.** The classes
  fixed here are "a refusal that shows nothing", "`||` swallows a legal zero", and
  "a surface advertises a capability it does not have". Swept all 6 trades / 26
  tools: all **9 clipboard sites** (`shared/checklist-request.js`, `docspec.js`,
  `note.js`, `rowlog.js`, `av/consumables`, `av/report-builder`, `gc/weather-day`,
  `hvac/repair-recommendation`, `plumbing/supply-house-order`) carry BOTH a
  rejection handler and an `execCommand` fallback, and every path ends in a visible
  `flash()`/`done()` — structurally immune, not merely currently-correct; zero hits
  for `||`-on-a-number (the only two matches are `(x || 0) + 1` counters, where
  absent and zero ARE the same thing); and no trade tool has a file input or an
  import to over-promise. Recorded so the next cycle does not re-sweep it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-08 · **[AXIS:WELL] THE ARTWORK GETS THE ROOM** — wishing-well IMPROVE (id
  `51c65a1c`, trade=collage, anonymous: *"it's hard to see the layouts when it's
  minimized and there's so many features stacking — you need a way to maximize the
  shot, and controls at most half the height"*). Measured on LIVE before touching
  anything: the collage was **6.2% of a 1280x900 window, 10% of a 390px phone, and
  at 320x568 it rendered at THREE BY FOUR PIXELS** — the thing the app exists to
  show, gone. **TWO causes, one symptom. (1) The dock had no ceiling:** `shrink-0`
  with no `max-h`, so every panel ever added took its space out of the picture —
  measured at **60.8% of the screen**, leaving a 52px stage band that `p-6` then ate
  48px of. **(2) The art frame was CONTENT-SIZED against a canvas that sizes itself
  from the frame:** `{aspectRatio, maxHeight:'100%', maxWidth:'100%'}` with no width
  or height, while `Stage.resize` reads `cv.clientWidth` and floors it at 240. A
  circular definition resolves at its floor and stays — **the artwork was ~240-300
  CSS px wide on ANY screen** (300x450 inside a 1900x776 band), and `maxHeight`
  could only ever shrink it further. **after →** the cap moved onto `--dock-max`,
  the panel's OWN existing scroller (its comment claimed "never more than ~44% of
  the viewport" while measuring the wrong box — the clip/transport row and tab bar
  above it, 156px at 390 and 204px at 320, were never charged against it); the band
  is measured by a ResizeObserver and the frame is given **explicit pixels**
  (`artFit` = largest box of `aspect` fitting the band), cutting the loop; padding
  went responsive; and **full bleed** (button, `F`, `Esc`) hides header and dock
  with `display:none` — *not* an unmount, so the Stage keeps its decoder, its
  AudioContext and its playhead — over a translucent pill carrying Roll · Shuffle ·
  Remix · Exit, because you maximize in order to COMPARE LAYOUTS.
  **Result (normal → full bleed): 320x568 3x4 → 16x24 → 312x467 (80% of screen);
  390x844 148x222 → 215x323 → 382x572 (66%); 430x932 → 265x398 → 422x632;
  1280x900 219x328 → 266x400 → 589x884 (45%); 1900x1300 300x450 → 533x800.**
  **Said plainly: 320x568 and landscape phones are CHROME-bound, not layout-bound**
  — header plus a wrapping transport row plus the tab bar is 265px of things the app
  needs before any panel opens, so the normal view there stays small and FULL BLEED
  is the real answer. The gate says so out loud rather than carrying a floor it
  cannot meet.
  **THE GATES NEVER SAW IT, AND THAT IS THE SCAR:** `mobile-watertight` asserts the
  canvas is *visible*, never that it is **big enough to look at**, so a stage
  collapsing toward zero was green every single run. New `stage-room.spec.ts`
  asserts SIZE — and was **watched going RED against LIVE production on all 8
  original checks**, reporting the real numbers back ("artwork only 3px wide at
  320px", "controls take 60.8% of the screen", "artwork only 450px tall in a 1300px
  window"). Measuring rather than looking then found more, all now gated:
  **(R6)** a phone held LANDSCAPE leaves a ~118px band and the 200px button rail
  **clipped `Clear all` off the bottom** with nothing to scroll (measured 82px past
  the edge) — the rail now lays across when the band is short; **(R7)** the new `F`
  shortcut listens on `window`, so a title containing the letter f maximized the
  app — the target guard is gated and was **watched going red without it**.
  **THE ADVERSARIAL AUDIT EARNED ITS KEEP AGAIN, AND HARDER THAN USUAL — four
  lenses, 21 distinct claims, and TWO of them changed the shape of the fix.**
  **(1) THE FIRST CAP WAS A REGRESSION.** The dock was wrapped in
  `max-h-[50vh] overflow-y-auto` — but `.ui-dock` is ALREADY a capped scroller
  whose primary action bar (fragment count · Shuffle · Remix) is `position:
  sticky` against ITS bottom. Nesting a second scroller pinned that bar to the
  bottom of an inner box pushed below the outer scrollport, and the most-used
  controls in the app went off screen: **measured 778..832 in an 844px viewport,
  to 869..923.** Every gate was green; nothing in the suite asked whether the
  primary actions were still visible. The cap moved to `--dock-max` (one
  scroller, sticky bar in it), and R11 now asserts `scrollers <= 1` plus
  `stickyInView` at three viewports. That single find also retired four other
  claims with it — `pb-safe` inside a scroll container, `50vh` measuring iOS's
  large viewport, the cap being a no-op, and the transport becoming
  scroll-dependent were all consequences of the scroller that no longer exists.
  **(2) A RUNNING TAKE BECAME INVISIBLE AND UNSTOPPABLE.** Stop lives in the
  transport row inside the dock; full bleed hides the dock; and Cmd-E still
  reaches Export while maximized because the Header stays MOUNTED under
  `display:none`. So: maximize → Cmd-E → Record, and the pill keeps offering
  Roll/Shuffle/Remix, changing the composition mid-take. Entering full bleed is
  now refused while `recorder.isRecording`, and starting a take drops out of it
  first. **(3) AND THE VERIFIER THAT WENT FURTHEST BUILT ITS OWN INSTRUMENT.**
  Told to refute a claim that the measured-pixel style had lost the synchronous
  `maxWidth/maxHeight: 100%` clamp, it first showed the ORIGINAL evidence was
  worthless — a rAF sampler reads BEFORE that frame's style/layout step, so a
  stale reading proves the DOM was stale, not that anything was painted — then
  captured real composited frames over CDP `Page.startScreencast` with a 12-bit
  barcode stamped into each frame to map it back to its layout. **Leaving full
  bleed at 1280x900 painted the collage at 589x884 inside a 1248x459 band, header
  and dock already restored, top and bottom sliced off by `overflow-hidden` — 8
  of 8 exits, 5 caught on screen, 0 with the clamp restored.** Both remedies are
  in: the CSS clamp (synchronous, and it covers the changes we do NOT drive —
  rotation, URL-bar collapse) and a layout effect on `maximized` that measures our
  own toggle before paint. R12 asserts the outcome and was red-checked properly:
  **it goes green if EITHER remedy is present, so it was watched going RED with
  BOTH removed**, reporting the verifier's own numbers back. Three smaller ones
  taken as well: the first-paint measurement sat BEHIND the `ResizeObserver ===
  undefined` guard even though it needs no observer, so an engine without one
  reverted to the content-sized model permanently — on the oldest devices, where
  it is worst; the `lg:p-6` padding step made the artwork ~9% SMALLER when the
  window got one pixel wider; and the full-bleed pill had no safe-area inset
  while being the only way out on a touch device, putting Exit under the iOS
  home indicator. And the sharpest single find:
  its sheet once and closes with `classList.remove("on")` against
  `.fb-wrap{display:none}` — so **one Feedback click killed F and Escape for the
  rest of the session**. Reproduced deterministically before fixing; the guard now
  asks whether a dialog is RENDERED (`getClientRects().length`). **And the gate for
  it had to be built to SEE the thing it grades** — in local dev `shared/feedback.js`
  404s by design, so every other test in this file runs in an app with no feedback
  modal at all, which is precisely how a production-only break could ship green;
  R8 loads the real shared script into the page and drives `Feedback.open/close`.
  Three more from the same lens, fixed whatever the verifiers ruled: the recorded-take
  preview was **the one full-screen sheet in the app never declared `role="dialog"`**
  (R9 now asserts generically that no fixed, screen-covering, z≥100 element lacks it);
  `F` with an EMPTY pool hid the entire UI and the strand-guard could not fire because
  `images.length` never changed (entry now refused at the door); and every toggle
  dropped focus to `<body>` because `display:none` blurs and the two buttons unmount
  each other (R10 asserts focus lands on the control that replaced the one removed).
  Two tests were themselves corrected: the first playhead assertion failed on a
  WORKING build because the clip loops and `currentTime` legitimately wraps — it now
  stamps the live `<video>` and `<canvas>` and checks the stamps survive, which is
  the real question (was the Stage remounted?); and an earlier R7 draft was DELETED
  for **passing with the code it claimed to test removed** — the empty-pool backstop
  is documented as defensive rather than covered, because a receipt for an
  unreachable state is worth nothing. **Proof:** 133 tests —
  stage-room 16/16, mobile 6/6, source-count 7/7, video-audio 4/4, one-layout 4/4,
  export-integrity 3/3, look 12/12, title 10/10, twist 8/8, composition 9/9,
  roll-code 20/20, trim 9/9, commons 10/10, well-mobile 15/15 — plus a stress pass
  showing zero oscillation over 3s idle, exact ratios across four aspect changes
  (2:3 · 1:1 · 16:9 · 9:16, all fitting the band) and a single settled size after
  rapid resizing; `tsc` + `vite build` clean. **Then re-run against PRODUCTION
  after deploy — the same 16 checks that were red there before: 16/16 green**, and
  a live phone capture at 390px shows full bleed at 382x572 (66.4% of the screen)
  with the clip still playing.
  **BACKPORT rider: swept, and it does not apply.** The class is "a flex child with
  no ceiling starves its sibling, and a replaced element's intrinsic size becomes
  the layout's fixed point". Checked all six trade toolkits: they are document
  GENERATORS — no canvas, no stage, no `flex-1`/`shrink-0` split, and the pages
  scroll the document rather than pinning to `fixed inset-0`, so nothing there can
  starve. Nothing to carry over.
  Also closed this cycle: BUG `b25242e0` (*"Why are we pulling frames?"*), filed 22
  minutes BEFORE `480ba233` deployed the fix for it. Verified at the artifact rather
  than assumed — on LIVE, one dropped video is one looping cell, and nine fragments
  run off ONE decoder with no sheet and no picker. Credited, not rebuilt.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-08 · **[AXIS:WELL] THE FULL WALL** — wishing-well BUG (id `0fd3a59f`,
  "The videos aren't all playing", trade=collage, anonymous): a multi-video
  collage EXPORTED every clip past the realtime decoder budget as a FROZEN STILL
  while still playing that clip's sound. **before → `renderOffline` →
  `stage.renderAtTime` drew only `c.live` clips, and admission caps them at
  mobile 3 / desktop 4-8, so a deferred clip's extracted still was baked into the
  FILE while `describeAudioSources` (already cap-blind, its own scar) mixed the
  audio in — sound over a picture that never moved. after → `beginOfflineRender`
  lifts the count/pixel caps and re-admits EVERY clip; `endOfflineRender` restores
  them and evicts back to the realtime budget; `renderAtTime` gained
  `ensureClipReady` so a just-admitted clip's first frame is not a still.** The
  caps are a REALTIME limit (keep up with a clock); an offline render has no clock
  and already lifts the realtime backing-WIDTH cap here for the same reason, so
  the decoder cap was the last realtime budget leaking into the file. **Proof
  (chromium, dev :5199 + LIVE):** a new e2e imports FIVE clips on an iPhone UA
  (cap 3), asserts the preview really is capped (<5 decoders), then asserts the
  offline take seats ALL 5 and a real MP4 comes back, then that the realtime cap
  is restored afterward (extra decoders evicted). Regression: video-collage 17/17
  (incl. the exact-duration render invariant and "two HD clips BOTH play" live),
  trim + video-audio-export 13/13; `tsc` + `vite build` clean. **BACKPORT rider:
  swept, N/A** — the class ("a realtime cap leaked into an offline artifact") lives
  in the collage engine (`lib/stage.ts`); no trade toolkit ships a video
  compositor or an offline export, so there is no sibling to carry it to.
- 2026-08-07 · **[AXIS:COLLAGE] THE LOOK** — the collage can be graded. Eight named
  looks (None · Punch · Faded · Mono · Noir · Warm · Cool · Bleach) on one wrapping
  chip row, on the dice, and **in the composition code** — unlike the caption, because
  a grade IS part of a recipe. **before → nothing in the tree ever assigned
  `ctx.filter`; the `Adjustments & filters` rung was untouched. after → `lib/grade.ts`
  is ONE ordered pipeline and all four surfaces that produce pixels apply it**: the
  still preview, the live Stage (so both video recorders), the export WORKER's
  OffscreenCanvas on another thread, and the SVG as real `<filter>` primitives.
  **The seam is that a grade is not a STRING, it is an ORDERED LIST OF STEPS**
  (`brightness → contrast → saturate → sepia → hue-rotate`) and the two emitters are
  both pure functions of that one list, through the same number formatter. Colour
  operations do not commute — saturate-then-sepia is a toned photograph, sepia-then-
  saturate is a loud brown one — so the order is part of the grade and is fixed in one
  place rather than implied twice.
  **The load-bearing decision is `color-interpolation-filters="sRGB"`.** Canvas
  evaluates CSS filter functions in sRGB; SVG filters default to LINEAR light. The
  identical primitives with the identical numbers therefore make the exported SVG a
  different picture from the exported JPEG of the same collage — **RED PROOF: up to
  105.2/255 apart, mean 28.1/255**, per-look table in the sweep output.
  **The sweep found a real defect before the browser did**: the CSS path prints the
  grade's PARAMETERS and lets the browser derive the matrix, while the SVG path prints
  DERIVED MATRIX TERMS — at four decimals `0.769 - 0.769·0.94 = 0.04614` printed as
  `0.0461` and the two exports landed 5.4e-6 apart. Invisible, and still two pictures.
  Fixed at six decimals with a stated reason (every sepia term is a 3-decimal constant
  times the amount, so a 2-decimal grade is exact) plus `GRADE_GRID`, which holds the
  ROSTER to that grid instead of hoping — the same argument `snapRoll` makes for the
  composition sliders. Now 6.66e-16.
  Proof: unit sweep **46,987 checks / 0 failures** over 5,832 swatches × 8 looks,
  including a numeric equivalence between the two emitters (not a string comparison),
  every look asserted in the DIRECTION its own name claims, and 56/56 single-character
  look manglings refused by the checksum. e2e **12/12 on chromium + Pixel 5**: T1 proves
  the NO-OP end to end (back to NONE returns the byte-identical picture, **0/255**
  residue), T3 renders two real 2K exports and measures the worker's warmth shift at
  **13.6/255 against the preview's 13.6/255**, T4 downloads the real SVG, rasterises it
  and lands **13.4 vs the canvas's 13.2** — the sRGB pin, proved at the artifact. **All
  three mutations go red**: deleting the worker's filter fails T3, dropping the sRGB
  attribute fails T4 *and* 7 sweep arms, dropping the look from the codec fails T5.
  Watertight asserted on the REAL page at 320/360/390/430 — eight 44px chips cannot fit
  one 320px line, so the row WRAPS and every chip is measured inside its dock.
  Regression: all 9 unit sweeps plus roll-code, one-layout, composition, twist, title,
  export-integrity, mobile-watertight, project-roundtrip and source-count green; `tsc`
  and `vite build` clean.
  **A process scar, filed:** `git checkout --` cleaned up the mutations by reverting to
  HEAD, which discarded this cycle's uncommitted work in two files and left the
  mutation in place in the third (untracked, so the error scrolled past). Everything
  was still green, on broken code. Mutation cleanup is a byte copy you took yourself.
  **BACKPORT rider fired, and came back CLEAN — with a structural reason.** The class
  fixed here is "one quantity DERIVED independently in two places at two precisions, so
  the two descriptions of it drift". Swept all 68 pages across the six trades plus
  `shared/`: **0 hits, and not by luck — no trade page derives a number for display at
  all** (0 `toFixed`, 0 `Math.round`, 0 `toLocaleString`). That is the SAFETY rail doing
  a second job: because a tool may never ship authoritative computed data and is scoped
  to structuring what the user ENTERS, there is no derived quantity for a precision to
  disagree about. Also swept the sibling class this cycle avoided by construction —
  "a load-bearing roster typed out twice" (`LOOK_IDS` is derived from `LOOKS`, never
  re-listed): **0 literal rosters appear in more than one file** across the same 68.
  Storefront: no manifest change owed — `fieldToolkits.ts` carries the six TRADES, and
  a Collage capability is neither a new tool in a trade nor a new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-07 · **[AXIS:COLLAGE] THE TITLE** — you can say what it is. A caption typed
  into the dock, four placements, three sizes, white on a scrim so it reads over any
  photograph. **before → nothing in the tree called `fillText`; a collage could not
  carry a word. after → `lib/title.ts` plans it ONCE and all four surfaces that produce
  pixels draw that one plan**: the still preview, the live Stage (so both video
  recorders), the export WORKER's OffscreenCanvas on another thread, and the SVG as real
  selectable `<text>`. **The seam is that the WRAP IS DECIDED ONCE.** `planTitle`
  resolves the caption to geometry at the canonical 1200 basis against the context the
  PREVIEW measures with, and `titlePlanFor(plan, width)` scales that finished plan for
  each caller — because letting four paths wrap the same string would decide the break
  four times against four font environments, and one of them is a worker THREAD where
  the font stack is free to resolve differently. That is the preview-is-not-the-file
  divergence ONE LAYOUT exists to prevent, arriving by a new door.
  **The load-bearing decision is which box the wrap respects:** the thing that must stay
  inside the margin is the SCRIM, not the glyphs, so the text box is the margin box less
  the plate's own padding. Sweep **82,871 checks / 0 failures** with a RED PROOF — the
  naive "wrap to the margin" rule, run as an oracle on the identical inputs, pushes the
  scrim off the canvas on **326/756** plans, worst overflow **95.0px at basis 1200**,
  which is exactly 2·padX at the `lg` size (mechanism matches to the digit).
  e2e **10/10 on chromium + Pixel 5**: T1 proves the NO-OP end to end (clearing the title
  returns the byte-identical picture, 0.00/255 residue), T3 renders two real 2K exports
  and differences them, T4 downloads the real SVG and checks its declared scrim against
  the rows the raster actually changed — a one-line re-wrap would move them apart by a
  whole line height. **Both mutations go red**: deleting the worker's `drawTitlePlan`
  fails T3, deleting the SVG emit fails T4. Watertight asserted on the REAL page at
  320/360/390/430 with a long caption in the box, zero horizontal overflow, every
  control ≥44px. Regression: all 8 unit sweeps, one-layout, export-integrity,
  composition, roll-code and mobile-watertight green; `tsc` and `vite build` clean.
  **A metric scar, filed:** the first version of this proof counted dark pixels and was
  really measuring the gutters (5.1% dark in an UNTITLED export) — every check now
  differences against the same collage rendered without a caption.
  **BACKPORT rider fired, and came back CLEAN.** The class fixed here is "one artifact
  computed independently by more than one path, so the paths can disagree". Swept all 25
  tool pages across the six trades: every page that has both an on-screen preview and a
  copy button reads the SAME builder for both — `asText()` (av/consumables,
  plumbing/supply-house-order), `text()` (gc/weather-day), `buildInstructions()`
  (av/report-builder), `buildDoc()` (hvac/repair-recommendation). **0 hits.**
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-07 · **[AXIS:COLLAGE] THE COMPOSITION CODE** — a good roll is no longer lost.
  Every composition now has a short code, shown under the dice (tap to copy), a box to
  paste somebody else's into, and the same code in the ADDRESS BAR, so a link is a collage.
  **before → `encodeRoll`/`decodeRoll` had existed since the roster landed, promised "same
  code, same collage, on any device" in their own module header, and were imported by
  nothing but two unit sweeps; after → `lib/rollCode.ts` is the missing direction**
  (`CompositionState` ↔ `Roll` ↔ string, pure) plus `codeFromUrl`, wired to a strip in
  SimpleControls and to `?c=` at mount + `replaceState`.
  **Wiring it up is what proved the codec could not carry a composition.** Five defects,
  all inside a green suite: `LAYOUT_ORDER` held only the 23 generators, so `minimal` — what
  the app BOOTS on — encoded as index 0, a different construction; the background was an
  index into 8 roster colours, so the "Average" swatch (derived from your photographs)
  encoded a paper-white collage as near-black; `rollDice` drew entropy/gutter/zoom from
  CONTINUOUS ranges while the code quantised them, so the first encode of a fresh roll was
  already lossy and the chaos grid (1/63) did not even contain the chaos slider's step
  (0.01); four frame chips were typed by hand (0.666, 1.77) against a roster of 0.6667 /
  1.7778, invisible to the chip's own `< 0.01` test and to 2px of canvas but not to a round
  trip; and `padStart` sets a MINIMUM, so a count at 36³ lengthened its group and shifted
  every later slice — the code then decoded CLEANLY into a different composition.
  Proof: unit sweep **206,120 checks / 0 failures** with a RED PROOF (the previous encoder
  mis-carries **59,961 of the same 60,000 compositions**; per-field breakdown matches the
  mechanism exactly); e2e **10/10 on chromium + Pixel 5**, asserting a PIXEL HASH of the
  canvas rather than the controls, and deliberately dropping `setSeed` turns T1 and T2 red.
  Regression: source-count, one-layout, composition, twist, export-integrity,
  mobile-watertight, project-roundtrip and all six sibling sweeps green; `tsc` and
  `vite build` clean; zero horizontal overflow at 320/360/390/430 with the strip's children
  measured for spill.
  **The four-lens adversarial audit earned its keep and changed the ship six times.**
  **(1)** A SHIP-BLOCKER: grow-to-cover overrode the code's fragment count whenever the
  recipient's pool was larger, and the address-bar rewrite then replaced the sender's code
  with the wrong one — measured, a 3-fragment code opened with 6 photographs gave 6, and
  21% of rolls ask for fewer fragments than a 40-photograph pool. **(2)** The same lens
  showed my own e2e helper `rollUsable()` re-rolled until the count cleared the pool size,
  with a docstring explaining why — so every test ran on the half of the space where the
  feature worked. The helper is gone and T7 drives the excluded case on purpose.
  **(3)** The first fix RACED: it cleared its flag in the ingest's `finally`, and the upload
  loop yields with `requestAnimationFrame`, which resolves before React flushes passive
  effects — so it never once worked. Rewritten as a drop marker in state. **(4)** The second
  fix then pinned a DERIVED count onto every later pool, which matters now that a plain
  refresh replays the address bar's own code; the code learned to carry whether its count is
  a decision or a default, and T10 proves both branches. **(5)** A truncated code used to
  open as somebody else's collage, because the seed is the only variable-length field — so
  codes are now checksummed, and the first checksum (weighted sum mod 36) caught only 88.9%
  because 36 is not prime and half its positions are blind; a multiply-and-mix pair catches
  **99.9% (17,952/17,964)**. **(6)** And that checksum had a hole: it covered the three
  groups `encodeRoll` emits, not the shuffle group the layer above appends — where every
  surviving mangling had landed. Also disclosed rather than fixed: pinned fragments cannot
  ride in a source-independent code, so the strip says so (T9).
  **BACKPORT rider fired, and came back CLEAN.** The class fixed here is "a silent index
  fallback that substitutes a plausible neighbour for an unrepresentable value"
  (`Math.max(0, indexOf(…))`). Swept all six trade toolkits plus `shared/`: **0 hits**. Also
  swept the sibling class "two lists of the same thing drift" — 225 array literals across the
  six trades, **0 appearing in more than one file**.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-07 · **[AXIS:COLLAGE] THE LAP SCHEDULE** — a trim that straddles the end of a
  short audio track now laps with the PICTURE, not with the audio track. `audioPlan`
  clamped `loopEnd` into the decoded buffer — the only safe thing to hand a node, and by
  doing so it clamped the PERIOD, which is the one quantity the two timelines must share.
  Measured on the repo's `shortaudio.mp4` (6.000 s picture / 2.99998 s sound) trimmed 2→5,
  5 s take: **before → sound present 100% of the take, WRONG on 80% of sampled instants**
  (an unbroken 440 Hz drone under a picture the file is silent for); **after → 40% and 0%**.
  The fix is not a better clamp — ONE node cannot express a signal that is not periodic at
  its own loop length — so `clipWindow.audioSchedule` emits one NON-LOOPING node per PICTURE
  LAP, which is what the live `<video>` always did, so the export finally reproduces the
  preview. Scope is the branch condition: differs from the plan iff the plan would loop over
  LESS than the picture window, so everything else is bit-identical (I16, 8,298 setups,
  `Object.is`). Proof: exported MP4 envelope at 0.25 s reads `####........####....`;
  unit sweep 5,445,981 checks / 0 failures with a RED PROOF (the old plan fails 725 of 738
  straddles); trim 9/9 + video-audio 4/4 e2e; `tsc` and `vite build` clean.
  **The adversarial audit (4 lenses) earned its keep and changed the ship six times.**
  It independently verified the schedule through REAL Web Audio in two engines (Chromium +
  WebKit): 0 drift / 0 missing / 0 invented on 800 instants where the old plan scores 506
  wrong, `duration` confirmed empirically as BUFFER seconds in both, no overlap; and
  2,280,960 hostile inputs with no hang, throw or unbounded allocation. What it CHANGED:
  **(1)** T7's duty-cycle + longest-silence pair is invariant under TRANSLATION — a render
  whose laps are 1 s late scored digit-for-digit identical to the correct one — so T7 gained
  a PHASE ANCHOR asserting slice-by-slice that sound is present exactly where
  `t % LAP < SOUND` (the old pair passes 4 of 7 candidate renders, the anchor 1 of 7).
  **(2)** THE SLIVER, raised by two lenses independently: the straddle was read off
  `plan.loop`, which inherited `audioPlan`'s 10 ms loop-WRAP floor into a path that never
  wraps — a 9 ms overlap played 1 blip where the picture asks for 15, one trim-slider detent
  from correct. Now decided on the WINDOW; I16 rewritten to define the boundary
  independently rather than mirror the code, coverage 738 → 1,440 straddles, and reverting
  the fix fails 1,284 assertions. **(3)** a latent `duration > 0` guard sent a ZERO-length
  request down the unbounded branch, so the one case asking for nothing got the whole buffer.
  **(4)** an empty-but-not-silent schedule fell through both counters and reported "Mixing
  the sound failed." for a mix that did exactly what was asked. **(5)** the cap was asserted
  only in the direction a MISSING cap satisfies — now pinned from both sides. **(6)** the
  `MAX_AUDIO_LAPS` docstring's "unreachable" proof was false in both halves (the rate clamp
  at 16 shrinks the output lap without bound); comment corrected and `truncated` wired
  through to a real user warning. **(7)** and the one that says most about the method: the
  fix for (4) INTRODUCED A SECOND ROUTE TO THE SAME DEFECT — the new zero-duration skip can
  skip every entry of a non-empty schedule, so the clip again landed in neither counter and
  again reported "Mixing the sound failed." for a correct silent render. An auditor found it
  by BUNDLING the real `offlineAudio.ts` and running the real `prepareOfflineAudio` against
  stubbed Web Audio — the very harness this file's ladder now names as the missing coverage.
  The audit's remaining half — `mixSources` has no unit coverage, so one 8-minute e2e is the
  only guard on the wiring loop — is now a ladder rung rather than a silence, and (7) is the
  argument for building it.
  **Same-class sweep (the BACKPORT rider, applied within collage): CLEAN.** `videoSync` also
  clamps — the browser's playbackRate range — but `describeAudioSources` and `seekClipTo`
  both read the SAME `clip.playbackRate`, so that clamp moves both timelines together. The
  audio-buffer clamp was the only bound applied to one side alone.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
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
  **BACKPORT rider fired, and came back clean.** The class fixed here is "the preview and the
  output are derived independently", and the trade toolkits have exactly that shape — a
  rendered preview and a copied document. Swept all 6 trades / 26 tools: the five tools that
  write to the clipboard (`av/consumables`, `av/report-builder`, `gc/weather-day`,
  `hvac/repair-recommendation`, `plumbing/supply-house-order`) all pass BOTH the on-screen
  preview and the clipboard through ONE producer — `text()`, `buildDoc()`, `asText()` — so
  they are structurally immune, not merely currently-correct. Nothing to carry over; recorded
  so the next cycle does not re-sweep it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-06 · **[AXIS:COLLAGE] TRIM — one formula decides where a clip is, and all three
  timelines ask it** (the biggest CapCut gap, and the increment that had been BUILT AND
  STAGED BY A CYCLE THAT DIED BEFORE COMMITTING — the book's body described it as shipped
  while nothing was in any commit and nothing was live). before→after: **a clip is all of
  itself → a clip is the part you chose.** Per-clip in/out with a filmstrip sheet. The
  reason it touches so little is that it did not add a window in three places:
  `Stage.seekClipTo`, `offlineAudio.mixSources` and the live `<video>` each carried their
  own copy of the same two lines, so the window went into ONE module (`lib/clipWindow.ts`,
  `sourceTimeAt`) and the three consumers now ASK instead of remembering. Compatibility is
  asserted, not hoped for: an untrimmed clip is `in=0, out=span` and adding exactly zero is
  the IEEE-754 identity, so every existing project renders bit-identically. Trim composes
  with video-length sync because sync is fed the WINDOW length rather than the file's.
  **Proof:** `clipWindow.invariants.mjs` **5,312,343 checks, 0 failures** · `trim.spec.ts`
  **8/8 on the real UI and 8/8 against LIVE**, reading exported PIXELS and decoded AUDIO —
  the trimmed-to third's 1200 Hz at 0.084 against the trimmed-away 440 Hz at 0.00007, 961
  rAF frames with `playheadOutside=0`, a container with `duration = Infinity` trimmed
  anyway, and a window past the end of a short audio track exporting silence rather than a
  looped fragment. Regression: mobile 6/6, source-count 7/7, one-layout 4/4, twist 8/8,
  export-integrity 3/3, video-audio 4/4, composition 9/10 (the documented seed flake), every
  sweep clean, `tsc` + `vite build` clean.
  **THE MOBILE GATE HAD NEVER SEEN THE THING IT WAS GRADING.** `mobile-watertight.spec.ts`
  imports PNGs, so the entire video transport does not exist while it runs — measured at
  390px with one video loaded, **ELEVEN controls under the 44px law**, including `Record
  video`, the button that starts an export, at 32x32. The bar now WRAPS below `sm` (44×7
  plus a clip chip does not fit on one 320px line) and the gate imports a real video, which
  within minutes found a second one older than trim: `.ui-stepper__btn` declares `width:
  52px` with default `flex-shrink`, collapsing both fragment steppers to **18px at 320px**.
  **The adversarial audit earned its keep for the fourth time in five — 9 agents, four
  lenses, three CONFIRMED defects and one refuted**, and the refutation is worth as much as
  the finds: that verifier noticed the worktree had moved under it mid-audit, materialised
  the STAGED blob into a scratch tree, served it on its own port and A/B'd one line.
  (1) THE TRIM HANDLES ACCEPTED EXACTLY ONE KEYSTROKE — the modal effect keyed on
  `[onClose]`, an inline arrow rebuilt every render, re-focused the Close button on every
  value change; ArrowRight moved IN 0→0.01 and presses 2..20 did nothing, and Enter, the
  natural "is this thing on?", dismissed the sheet. Reproduced in a PRODUCTION build, so not
  a StrictMode artifact. Neither a drag (pointer capture survives the steal) nor `fill()`
  can see it, which is why the suite was green. Fixed with a ref + empty dep list, and
  `trim.spec.ts` T3b presses a REAL arrow five times and **was watched going RED** on the
  reintroduced dep array. (2) THE SLIDER TRACKS LIED — the global range track is
  `var(--fill, 50%)` and neither trim slider set it, so both bars painted half green with
  the OUT handle at the far right. (3) NOT FIXED, ON THE LADDER WITH ITS REPRO: a trim
  window that STRADDLES the end of a short audio track loops the surviving fragment at the
  AUDIO's period instead of the picture's — `shortaudio.mp4` trimmed 2→5 gives a 3 s picture
  lap against a 1 s sound lap, and 16 of 24 sampled instants play a tone under a picture the
  file is silent for. Pre-existing in class; the honest fix is per-lap scheduling, not a
  clamp, so it is its own increment.
  **BACKPORT rider fired, and did NOT come back clean.** The class fixed here is "a modal
  that traps nothing", and the trade toolkits have exactly that shape — the wishing well is
  injected into every page of every trade. Measured on LIVE production before the fix:
  **12 of 16 Tab stops landed OUTSIDE the open dialog**, on the nav, on the trigger, and on
  a tool page on the user's own INPUT. `aria-modal="true"` was already there and is a
  promise to assistive tech, not a behaviour. One handler in `shared/toolkit.js` covers all
  six trades because the runtime is shared; `shared/feedback.js` repeats it locally because
  it is a standalone drop-in that may not assume the toolkit is present. Verified LIVE on
  all six trades plus a tool page: **0 of 26 stops outside, forwards and backwards.**
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-08 · **[AXIS:WELL] THE THIRD TIME HE ASKED, THE APP WAS STILL ASKING BACK**
  (wish 8c2fc142, the owner: "You're still asking for how many frames to pull instead of
  just loading the video. Stop asking for frames period.") — the THIRD filing of one
  complaint in thirteen hours, after "stop pulling single frames" (0fd3a59f) and "why are
  we pulling frames?" (b25242e0). **b25242e0 was closed as ALREADY SERVED, "verified on
  LIVE this cycle rather than assumed", with no code changed — and it was not served.**
  That live verification drove the default code PATH and never read what the page SAID.
  Two surfaces were still asking, measured on production before the fix: the button that
  takes a video was labelled, in title AND aria-label, **"Extract frames from a video"** —
  a promise it had already stopped keeping — and Settings > Video carried a switch,
  **"Choose frames on import"**, whose ON state routed every clip into a sheet whose
  primary control is a 1..N **"Frames"** slider and whose commit button reads "ADD N
  FRAMES". **Default-off was the wrong fix for "stop asking": an opt-in ask is still an
  ask**, and a `genart.framePicker` of `'1'` persisted from an earlier visit pinned a
  returning user to the exact behaviour we had removed for everyone else. So the route is
  DELETED, not defaulted off — no sheet, no queue, no preference, no switch,
  `VideoImport.tsx` (600 lines) gone. Frames survive only as an internal detail nothing
  mentions: one poster raster, which is what the static exports draw and what a device with
  no decoder to spare falls back to.
  **AND THE OTHER HALF OF "INSTEAD OF JUST LOADING THE VIDEO" WAS REAL AND MEASURABLE.**
  Intake was `probeVideo` + `extractFrames`: one decoder opened for metadata and thrown
  away, a second opened, primed and seeked THREE times (smart@1 oversamples by 3), before
  the stage opened the third one it would actually play. On LIVE, WebKit, a 25 s 1080p
  H.264 clip: **the decoder was ADVANCING at 256 ms and the clip did not reach the collage
  until 3,517 ms** — thirteen fourteenths of the wait was the app pulling a frame out of a
  video it had already decoded. `openClip()` does it in one session and one seek.
  **LIVE, same URL, same clip, after: 915 ms** (local dev 3,517 → 490).
  Dropping the oversample is the one real risk — oversampling is what dodged black leader —
  so it gets a GATE, not an assurance: `clip-intake.spec.ts` drives the REAL module against
  a fixture that is black for its first 1.5 s of 5 s and asserts the poster is not, and it
  **was watched going RED** (luma 0, t=0.1 s) on a deliberately reintroduced head-sample.
  The two tests that asserted the OPPOSITE — that the picker was merely off by default, and
  that its route "still works when enabled" — are now the negative, including a stale `'1'`
  in localStorage that must not resurrect it. Regression: chromium video 17/17,
  clip-intake 3/3, mobile-watertight + source-count + video-length-sync + video-audio-export
  + trim 26/26, unit sweeps 10/10, `tsc` + `vite build` clean, LIVE mobile gate 6/6 and
  4/4 at 320/360/390/430 with zero horizontal overflow.
  **NOT FIXED, ON THE LADDER WITH ITS REPRO:** WebKit 19/20 — "the offline render seats
  EVERY clip" times out waiting for the fifth of five clips (`tone_e.webm`) to register.
  **Pre-existing: it fails IDENTICALLY against live's old code**, so it is not this
  change, and it is in class with wish 0fd3a59f ("the videos aren't all playing"), on the
  owner's own engine. Its own increment. Same for `stage-room` R1@320 / R1b / R11, which
  fail on live's old code too in a gate the book above records as green.
  **BACKPORT rider fired, and came back CLEAN.** The class is "a label or a persisted
  preference that outlived the behaviour it described", and the trades share one runtime,
  so it would land on all six at once. Swept: the only `localStorage` key in
  `shared/toolkit.js` is `av.favorites.v1`, read solely as a deliberate legacy migration
  into the namespaced key — the opposite of an orphan; and **0 inert labelled controls
  across all six live trade hubs** (av, plumbing, electrical, hvac, gc, low-voltage).
  Wisher credited anonymously in `tools/collage-studio/credits.json`, `av/credits.json`,
  and ON THE PAGE — in Settings, on the line where the switch used to be, so anyone hunting
  for it reads where it went.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
  **POSTSCRIPT, and the reason this entry names its own verification method:** a FOURTH
  filing (929ccef8) landed at 16:36:14Z — "I'm presented with select frames why? … nobody
  will want to sit there and press and move the dial to 1 frame" — 14 minutes BEFORE this
  fix's deploy finished (16:50:50Z). It describes the pre-fix build. It was NOT closed on
  that timing, because closing by inference is exactly what went wrong with b25242e0.
  Verified instead on the REAL returning-user path: LIVE, WebKit, service worker installed
  and CONTROLLING (never unregistered — the fix has to reach a user who does not clear
  their cache), `genart.framePicker` forced to `'1'`. The SW is network-first on
  navigations and a new content hash misses the cache, so one reload carries the new
  bundle; asserted, not assumed. 0 controls asking about frames.


- 2026-08-09 · **[AXIS:WELL] THE BIGGER FILE WOULD HAVE BEEN THE SAME PHOTOGRAPH, ONLY SOFTER**
  (wish `608a5aab`, anonymous: "same hi res output feature like the photo **or** a simple way to
  do full screen **and** capture data to a zip that can be preserved and loaded later… makes the
  creation tool a utility and has presentation function all in one go") — three clauses, and only
  ONE of them was unserved. **Full screen already exists** (F / the Maximize button → full bleed:
  header and dock `display:none`, Esc out, safe-area action bar; and on iPhone Safari
  `Element.requestFullscreen` does not exist at all, so full bleed IS as full-screen as the
  platform permits). **The `.collage` zip already exists** and round-trips the sources and every
  setting. Both verified on the RUNNING APP, not inferred — the b25242e0 scar is that "already
  served" was once concluded from a code path and was wrong.
  **THE UNSERVED CLAUSE WAS TWO CEILINGS STACKED, and only one was visible.** SIZE: `maxBackingW
  = opts.maxBackingWidth ?? logicalW`, and VideoStage built the Stage as `createStage(cv, {
  onStatus })` — passing neither, so every exported MP4 was **1200px wide on every device from
  any source**, beside a still export offering 16384. SOURCE: `stillKey = asset.previewSrc ||
  asset.src` — the Stage draws the **≤1024px THUMBNAIL**, while the still exporter draws the
  ORIGINAL and names that exact asymmetry as a bug it already fixed (`render.worker.ts`: "TWO
  SOURCES, IN ORDER OF QUALITY"). The video path never got that fix.
  **THAT IS WHY IT IS ONE CHANGE.** Lifting the size alone passes every assertion — bigger file,
  larger dimensions — and ships a 4K container of upscaled thumbnails, which no frame-size check
  can detect. So the PICTURE is measured: one scene, one canvas size, rendered twice with only
  the source swapped, scored on gradient energy along a scanline against a stripe fixture whose
  period dies at 1024px and survives at 3000. **33.0 → 124.4 (3.8×)**, and the test **was watched
  going RED** with the swap disabled (33.0 vs 33.0). End to end, driving the real UI:
  **1200×1802 → 2488×3732**, with the sheet's label matching the delivered file.
  **THE LADDER IS PROBED, PER DEVICE AND PER SHAPE.** H.264 caps the frame in MACROBLOCKS, so the
  ceiling depends on the aspect (4096 on a 16:9 long edge, ~3760 on the default 2:3 portrait) — a
  fixed list would carry rungs that fail only after a render has been waited out. Refused rungs
  render unavailable with the real reason; MAX is probed DOWN from the ceiling so the top is the
  true top. It deliberately does NOT mirror the still's 8K/16K/MAX and says so in the sheet: that
  ceiling is the FORMAT's, not the device's.
  **BUDGETED BY GEOMETRY, which is what makes it safe on the phone the wish came from.** A
  fragment covering 400×600 device pixels cannot show more than that much of its source, so each
  original is rasterised only to the scale its own fragments consume and released immediately,
  sequentially. Pointing the key at the originals and letting `ensureStills` fetch them would
  hold N full-res decodes at once — twenty 12MP photos ≈ 975MB, on the call stack that has just
  admitted every clip decoder and is about to reallocate the canvas 4× larger. Both levers are
  restored in `endOfflineRender`, including an EXPLICIT eviction of the take's rasters: the cache
  prunes only above `wanted.size + 32`, so 40 entries against a threshold of 52 would have leaked
  every raster for the rest of the session.
  **THE PANEL WAS RUN TWICE, AND THE FIRST RUN WAS THE LESSON.** Round 1 voted 2–1 for a
  fullscreen mode — on a fact sheet that said full screen was "absent entirely", which was MY
  error, not theirs. Corrected and re-cast, the same three lenses went **3/3 for this increment**,
  and the round-1 skeptic's own fail-mode prediction ("an immersive layer upscaling a 1200px stage
  onto a 2560px display looks WORSE than the windowed app") turned out to name this very ceiling.
  A panel agreeing on a false premise is not agreement; it is a broken instrument.
  **FOUND BY THE NEW MOBILE GATE, PRE-EXISTING, BOTH FIXED:** the video length buttons were 43×30
  — under a thumb, beside the take button, in a sheet only ever opened on a phone; and
  `.ui-btn--icon` DECLARED the 44px tap size and RENDERED at 37px, because a flex ITEM shrinks
  past its own width down to its content (an 18px icon). `flex: none` fixes every icon button in
  the app at once — the rule was never wrong, it was being overruled by the box it sat in.
  Gates: unit sweeps 13/13 (`videoSize` watched RED on two deliberate breaks — a MAX that stops
  early, and a ladder that offers what the encoder refused); chromium e2e 115/115;
  mobile-watertight at 320/360/390/430 with the new row, zero horizontal overflow, every rung
  ≥44px. WebKit 37/39 on the touched paths — the two failures (`trim` "no duration in its
  container", `video-collage` "seats EVERY clip") **verified failing IDENTICALLY on a clean HEAD
  worktree**, so pre-existing and on the ladder with their repro. `tsc` + `vite build` clean.
  Wisher credited in `credits.json` and ON the size row.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
  **BACKPORT RIDER FIRED. CLEAN ON THE CLASS FIXED — AND IT FOUND A DIFFERENT ONE.** The class
  is "a control that DECLARES the 44px tap size and RENDERS under it", swept on all six LIVE trade
  hubs at 390px: **0 of 0 declared-but-shrunk** on av · plumbing · electrical · hvac · gc ·
  low-voltage, and zero horizontal overflow on all six. But the same sweep measured something the
  existing gates do not look at: the **cross-trade footer links** ("AV Field Toolkit →",
  "Plumbing Field Toolkit →", …) are **17px tall on every one of the six hubs** — 7–8 controls per
  page, under a thumb, on the one control whose entire job is moving a tradesperson between kits.
  `well-mobile.spec.ts` passes because it is scoped to the wishing well and never sees them. NOT
  fixed here: it is a layout change to six live footers needing its own 4-width × 6-trade
  verification, which is an increment, not a rider — filed with its numbers rather than
  half-landed at the end of a cycle. **NEXT RUNG, and it is a real one.**

- 2026-08-09 · **[AXIS:WELL] "THE APP CRASHED AND I LOST WHAT I WAS DOING" — NOW THE NEXT
  LAUNCH HANDS IT BACK** — wishing-well BUG (id `479a6da8`, collage, `about_tool=export`,
  anonymous): a 4K video capture pushed the phone's browser over its memory line, the tab
  reloaded, and the whole collage was gone. THE CAUSE WAS TOTAL — every bit of project state
  lived in React `useState` and NOTHING was ever persisted; the only durable save was the user
  manually downloading a `.collage`, which nobody does mid-capture. before→after: **no autosave
  anywhere → the working project is written to IndexedDB continuously**, and the next launch
  OFFERS "pick up where you left off".
  **BUILT ON THE PROVEN ROUND-TRIP, NOT A SECOND FORMAT.** `buildProjectBlob` is extracted from
  `saveProject`; autosave stores those exact bytes; restore is `loadProject` on the stored blob
  fed through the SAME `applyLoadedProject` hydration Open uses — one serialization, one apply
  path, no drift (the "path that forgot it" class this book already carries is exactly what a
  hand-copied second apply path would reintroduce). The archive **never zips video**, so autosave
  cost scales with still count, not clip size — cheap even beside a heavy capture.
  **THE GATES ARE THE FEATURE.** New pure core `lib/session.ts` — `canAutosave` refuses to write
  into an EMPTY pool (would clobber the session a tap from restoring), DURING an export/capture
  (the memory cliff itself), or OVER a pending restore. Unit-swept **6376/0**, and WATCHED RED
  with the export guard dropped (5 failures incl. "never autosave mid-export — the crash moment").
  New `lib/sessionStore.ts` IDB shell **fails soft everywhere** (private-mode Safari denying
  IndexedDB can never break the editor). An **immediate checkpoint** fires the instant
  runExport/capture starts, so the one moment that actually crashes is saved at zero staleness; a
  `beforeunload` guard covers the soft refresh the browser lets us warn about.
  **VERIFIED AT THE ARTIFACT, DRIVING THE REAL UI.** chromium e2e **3/3**: cold start shows NO
  banner (no false-fire on a first visit) → import two photos → autosave → `page.reload()` (the
  crash) → banner appears and its subtitle names **"2 images"** (metadata round-tripped, not just
  a box) → Restore puts the collage back on the stage → Dismiss clears it for good and a further
  reload does not re-offer it. Mobile-watertight **320/360/390/430**: zero horizontal overflow,
  Restore + Dismiss both ≥44px. `tsc` clean, all **14 unit sweeps** green, `vite build` clean.
  **BACKPORT RIDER — SWEPT, NOTHING TO CARRY (yet).** Crash-safe autosave is a property of a
  STATEFUL editor; the six trade toolkits are static single-tool pages whose output is copied out
  immediately and hold no multi-field working session to lose, so there is no sibling surface with
  this class today. Filed, not forced — the nearest future carry is the report-builder shape if it
  ever grows persistent drafts.
  **NEXT RUNG:** incremental blob cache (store each image once in IDB, autosave only the small
  manifest) so a 30-photo project stops re-zipping on every idle; and persist the soundtrack + live
  clips so a restored VIDEO project comes back whole, not just its stills. Plus the improve wish
  (id `4124be76`) — show the wisher credit inside the well modal — and last cycle's 17px
  cross-trade footer links.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-09 · **[AXIS:WELL] THE WISHERS WERE CREDITED IN A LEDGER NOBODY COULD SEE ·
  now the well shows them, in the modal, on every surface it touches.** Wished straight into the
  Collage well (anonymous): "display who wished it better somewhere in this modal … stay consistent
  cross apps." The trade toolkits already showed this at `<trade>/credits.html` from their nav;
  Collage is a React app with no such nav, so the five capabilities its users had wished into it
  lived in a `credits.json` nothing rendered.
  **THE FIX IS IN THE ONE SHARED WELL, NOT THIS APP.** An in-modal **Wall of Wishes** landed in
  `shared/feedback.js`, so Collage, the commons, and every future non-trade surface got it in a
  SINGLE edit while the trades keep their `credits.html` — every surface the program ships now
  shows who wished it. A "★ Wall of Wishes" link appears under the form ONLY when the surface's
  ledger loads with ≥1 credit; it fetches that surface's own `credits.json` (relative, so
  `/collage/` loads `/collage/credits.json`), unifies the two ledger dialects in one renderer
  (trade `tool_name`/`wisher`, collage `capability`/`wisher_display`), and only ever prints the
  already-anonymised name — nothing can leak a requester.
  **DEPLOY:** the Collage ledger moved to `public/credits.json` so vite ships it to
  `/collage/credits.json`, now asserted in `deploy_bridge.yml` (fail-closed vs a silent 404).
  **VERIFIED AT THE LIVE ARTIFACT.** Playwright against the DEPLOYED site at **320/360/390/430**:
  zero horizontal overflow in BOTH the form and the wall, every new control ≥44px, six rows
  newest-first, head swaps to "Wall of Wishes" and Back restores the form, "wished by an anonymous
  Collage user", no PII. `tsc` clean, `vite build` clean, `node --check` on the runtime clean.
  Closes the NEXT RUNG the autosave cycle named (wish `4124be76`).
  **BACKPORT RIDER — SWEPT, ALL GREEN.** All 7 trades' `credits.html` re-fetched live → 200; the
  wall they already had is intact. Extraction ran the OTHER way this cycle — the trades' proven
  credits pattern carried INTO the shared well for the surfaces that lacked it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C78 · 2026-08-09 · [AXIS:WELL] RESTORE IS INSTANT, AND IT CANNOT HANG** —
  wishing-well **BUG** `b79c2df6` (collage, `about_tool=project`, anonymous):
  *"Restoring images is slow and is glitching. Endless loop of restore also does
  not restore quickly need to optimize do research perpetual improvements."*
  Filed hours after the autosave shipped, and it named **three** defects, not one.
  **1 · THE HANG (the "endless loop").** `loadProject`'s archive branch awaited
  `onload` with no `onerror`, no timeout — an undecodable asset never settled the
  promise, so Restore vanished the card and did nothing, forever; reload and the
  offer was back. `measureSource` now resolves on load, error AND a 15s timer, and
  a restore that cannot succeed **clears** the session instead of re-offering one
  that can never load. **2 · THE GLITCH.** The session was the whole `.collage`
  ZIP in one row, so every 1.5s debounce re-fetched and re-zipped the entire pool
  for a settings change. Bytes now live one row per asset behind a pure diff
  (`planAssetWrites`): before→after on a settings change = **4 image writes → 0**,
  manifest still re-saved (both asserted; the 4 is the measured red).
  **3 · THE SLOWNESS, twice.** The manifest now carries `width`/`height`, so
  restore stops decoding every photo in sequence to relearn numbers it wrote down;
  and the **≤1024px thumbnail is stored beside the original** — restoring only the
  originals had silently promoted the pool to full-res previews (the app draws
  `previewSrc` everywhere), leaving the editor slower AFTER recovering than before
  the crash. Missed originally because the fixtures are 1400×1000; found by an
  adversarial subagent reading the CONSUMERS. Same fix carried into the archive
  itself (`previews/`, additive — older `.collage` files open unchanged).
  **PROOF.** Restore **140ms** at 390px, zero horizontal overflow at 320/360/390/430,
  stored tiers 74054→43413 and 186955→69411 bytes. Unit sweep **8028 checks / 0
  failures** (+3 new invariant families), watched RED three ways: 783 failures with
  the diff removed, 3 with `previewSrc` re-aliased, e2e red with the `onerror`
  removed. **122/122 chromium e2e**, `tsc` clean, `vite build` clean. New e2e:
  settings-change-writes-no-bytes, restore-is-quick, cannot-hang, and a **v1
  legacy session still restores** (the old rows are somebody's unfinished work, so
  they are read, not discarded). Also fixed the harness scar: `playwright.config.ts`
  pointed at **:5173** — Persona 500's port — with `reuseExistingServer`, so the
  documented hazard was the default. Now :5199 `--strictPort`.
  **BACKPORT RIDER — SWEPT.** The class here is *within* this app rather than
  across trades: both restore doors (`loadSession` and `loadProject`) got the
  thumbnail tier and the decode fix, and `loadFromSVG` is noted as the remaining
  aliaser (an SVG carries only full-res base64; regenerating there is its own
  rung). All 7 trades re-checked for the `.collage`/IndexedDB class — none of them
  persist binary sessions, so there is nothing of this shape to carry over.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C78b · 2026-08-09 · [AXIS:WELL] THE SAME FEATURE, NOW ACTUALLY ON THE PHONE** —
  ran the two WebKit projects at this feature for the first time and got **0/14**.
  Checked it against the pre-fix commit in a worktree: **0/14 there too** — not a
  regression, a feature that had *never once worked on iOS*. Narrowed by probe to
  a single fact: **WebKit refuses a Blob into IndexedDB** (plain object OK,
  ArrayBuffer OK, Uint8Array OK, Blob → empty-named transaction error, abort), and
  since manifest and bytes share one transaction, one Blob silently killed the
  whole snapshot. Session assets are now `ArrayBuffer` + mime, rebuilt into a Blob
  on read; rows written by the Blob deploy are still read. before→after on WebKit
  + Mobile Safari: **0/14 → 24 passed / 4 skipped** across all four engines (the 4
  are the v1-legacy tests, skipped on WebKit *because a v1 row was a Blob row and
  WebKit could never have written one* — an honest statement of a state that
  cannot exist, not a green-washed skip). Also hardened in the same pass: a flush
  that cannot capture an asset's bytes now writes NOTHING rather than a manifest
  naming bytes the store lacks — restore fails closed and then clears, so a
  poisoned snapshot would have destroyed the good one under it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
