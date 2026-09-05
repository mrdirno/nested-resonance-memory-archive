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
- **C3712 — PREVIEW-FIRST STUDIO (2026-09-05), shipped and verified:** whole-artwork playback with one optional editor at a time, compact persistent transport, and a simplified template-first Art Room. The same lyric sample grew from 164×292 to 338×602 on a 390×844 viewport, and 111×199 to 273×487 on 1280×720; visible buttons fell from 19 to 11. Add / Layout / Look / Motion / Text replace the always-open control wall. Code `496a17ba`, [Pages success](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33995354619), **173/173 public-site browser cases**, 40/40 unit suites, complete decoded native-video inspection, and matching public JS/CSS/worker/service-worker bytes. [Release and navigation guide](C3712_RELEASE.md).
- **C3711 — NATIVE ART RACK (2026-09-05), shipped and verified:** eight original templates with real thumbnails; up to eight enabled, soloed, ordered, blended layers; seeds and dice locks; parameter automation; persistent editable recipes plus canonical PNG; native Stage/video rendering at requested time. Template gallery is primary; HTML player is secondary. Code `efdc4b9f`, [Pages success](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33991651937), **58/58 public-site browser cases**, 40/40 unit suites, and real encoded-frame inspection. Native animation reaches video; imported HTML remains a still capture.
- **C3710 — ART ROOM + LYRIC HANDOFFS (2026-09-05):** the Art Room dock opens an original seeded Tidal Paper instrument or local self-contained HTML. An opaque sandbox and private session return validated still PNG pixels into the existing collage/project workflow. Show artwork reveals deferred Bifurcata worlds; local Bifurcata capture and saved originals passed on Chromium, Mobile Chrome and Mobile Safari. Lyrics now includes a copyable audio-transcription prompt, verified free/browser options and an Apple Silicon setup link. The [art and intelligence roadmap](ART_AND_INTELLIGENCE_ROADMAP.md) defines downloaded browser drafts, a native Mac handoff, deterministic animation adapters and portable audiovisual projects. These future capabilities are not shipped by this release. Code `3f3ede40`, [Pages success](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33989801143), **40/40 live browser cases** and actual live capture/guide review. Only captured pixels persist; editable HTML, seed recipes and live instrument motion do not.
- **C3709 — TIMED LYRICS (2026-09-05):** editable cue text and in/out timing,
  playhead stamping, preview, plain SRT/WebVTT interchange, and one-step track
  undo. The same planned text reaches the live canvas and recorded video;
  still/PNG/SVG show time zero and SVG metadata carries the whole track.
  `.collage` and crash recovery retain captions and manual pins. Saving refuses
  unreadable required image originals; opening a picture project clears the
  previous session's soundtrack. "Try a lyric film" supplies four original
  procedural images and three timed cues, ready to edit and record. This does
  not add transcription, word karaoke, a multi-shot timeline, or original
  audio/video packaging. Live release receipt: code `9f535486`, [successful Pages run](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33988232971), 37/37 production browser cases and manual live sample/export review.
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
  THE COLOUR DICE — a second roll (`lib/dealRoll.ts`) over the arrangement, the
  focus and the twist ONLY, so a colour sort can be re-rolled without losing the
  layout you just found; now under Layout → Composition. Expanded preview
  keeps Dice, Undo and Back to editing outside the artwork;
  INTENT-AWARE INTAKE — the MUSIC button takes a video for its SOUND and leaves
  its pictures out (`lib/intake.ts`, swept over extension x MIME x intent);
  EVICTION — in full bleed a tap arms a fragment and offers pin or REMOVE, and
  removing takes the whole SOURCE (a clip leaves with all its frames,
  `lib/evict.ts`);
  TWIST — 5 per-fragment rotation modes (the picture leans, the tiling does not),
  reaching all four render paths through the one geometry function they share;
  ONE LAYOUT — every render path (preview, Stage, video, raster export, SVG)
  draws ONE partition at four sizes, generated once at a 1200-space basis and
  scaled, instead of four partitions generated independently;
  MUSIC RANGE — the soundtrack gets the same in/out window every clip has,
  through the SAME sheet (`TrimSheet` now takes a name and a span, not a clip),
  a ruler instead of a filmstrip where there is no picture, and the same
  `clipWindow` formula on all three timelines; music also starts the collage
  DRIFTING when nobody has chosen a move;
  CUT AUDITION — holding a trim handle plays that cut like a DAW wheel: the IN
  handle loops the monitor ON the cut, the OUT handle plays the approach up to
  it, looping until the handle is left (`lib/audition.ts` owns the sub-window;
  `stage.setAudition` retargets the track's OWN element — no second decoder, no
  double — solo and at unity through `applyMutes`' audibility terms, with the
  range fade armed on the REAL window so the landing previews as it will ship);
  THE SWAP — the collage's drag-reorder: the armed fragment's third verb parks
  it, the next tap on the canvas names its partner, and the two pictures trade
  fragments (`lib/swap.ts`). It reaches every render path through the one seam
  they share (`shuffledIndices` -> `orderedAssets`), the partition does not move
  (focus, twist and lean are properties of the FRAGMENT), and it re-pins both
  cells — which is the half that makes it survive a re-deal instead of being
  undone by the next gutter nudge;
  TRIM — per-clip in/out points with a filmstrip sheet, held by ONE
  output-time-to-source-time function (`lib/clipWindow.ts`) that the live
  element, the offline frame seek and the offline audio mix all ask, and coupled
  to video-length sync through the WINDOW length rather than the file's;
  THE LAP SCHEDULE — when a clip's audio track ENDS INSIDE the trim window, the
  export stops asking one looping node to express a signal that is not periodic
  at its own loop length and schedules one non-looping node PER PICTURE LAP
  (`clipWindow.audioSchedule`), so the sound laps with the picture instead of
  with the audio track;
  UNDO — the roll you liked comes back: undo+redo over the destructive
  composition events (roll, shuffle, remix, applied code), under Layout and
  on Cmd-Z / Shift-Cmd-Z / Ctrl-Y; expanded preview keeps Undo visible;
  THE COMPOSITION CODE — every composition has a short code, shown under the
  dice, tap to copy, paste one back to open it, and carried in the address bar
  so a LINK is a collage. `lib/rollCode.ts` owns the one seam between app state
  and a `Roll` in both directions; the sources are deliberately not in it;
  THE TITLE — a caption typed under Text → Title and drawn over the finished collage
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
  THE CONCURRENCY — every video you drop plays at once, on a phone too.
  `lib/admission.ts` (pure, swept) owns WHO gets a decoder: the COUNT cap is
  unchanged (phone 3 / Android flagship 4 / desktop 4-6-8), the PIXEL guard is
  the count cap FILLED — two DCI-4K seats plus 1080p seats on a phone, 2-4 4K
  seats on a desktop by reported memory — and behind it a MEASURED ceiling: the
  lowest summed load at which a decoder was SEEN to stall this session. The
  probe (`stage.armPlayProbe`) reads EVERY live clip's presented-frame count
  over the same window and `judgeStall` says which failure it is — `blocked`
  (paused, or nobody advancing: gesture / Low Power → "Tap to play"), `stalled`
  (un-paused and frozen while a sibling moves → two strikes → `settleStall`
  lowers the ceiling, re-plan, nudge, bounded at 4 rounds per episode with a
  1.2 s cooldown and a floor of one decoder), or `fine`. Before: the pixel cap
  was `count × 1080p` (phone 6.2 Mpx), so any 4K clip (8.3 Mpx) pinned a phone
  to ONE playing clip with a notice that read like a hardware fact;
  THE FRAME TRAVELS — a hand-set crop is now IN the file. THE REFRAME lived in
  one place, a `Map<assetId, Frame>` in App state, and every surface that DRAWS
  read it while every surface that WRITES read the pool: the `.collage` archive,
  the crash-safe snapshot and the exported SVG all serialise `img.analysis`, and
  the correction was never in it. So the SVG drew a reframed collage and REOPENED
  as the un-reframed one, and the autosave that exists to survive an OOM dropped
  the correction silently. `lib/reframe.ts` now owns the ONE seam between the two
  representations — `poolWithFrames` on the way out, `framesFromPool` +
  `poolWithoutFrames` on the way in — and App holds a single `poolForSave` memo
  that the three writers take instead of `images`. Both directions are identity-
  preserving when nobody has dragged a picture, so every file this app writes for
  everybody else is byte-for-byte what it was;
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
  to the top beside `moveOriginMs` so both recorders open on the same bar;
  THE FADE — the take stops sounding like somebody pulled the cable out. One
  linear envelope in `lib/fade.ts`, read by BOTH surfaces that can carry sound:
  the offline render multiplies through the mixed buffer (`applyFade`, after the
  true-peak limiter) and the realtime MediaRecorder fallback schedules the same
  shape as automation on `masterGain` (`Stage.applyTakeFade`). LINEAR is not a
  compromise, it is the reason there can be two emitters: it is the only shape
  an `AudioParam` and a sample walk express identically, and the sweep reads the
  ramp schedule back through `rampGainAt` and compares it to `fadeGainAt`
  pointwise. It runs AFTER the limiter in both directions of the argument — the
  envelope is ≤1 so it can never breach the ceiling, and limiting first stops
  the take's ENDS from setting the level of its middle. It lives beside the take
  LENGTH (same state, same bar, same lifetime) and therefore rides in no dice
  roll, no composition code and no project file, because a fade is a fact about
  a render and a code is a recipe somebody else opens with their own music;
  THE RANGE FADE — the cut you chose stops arriving as a click. THE FADE above
  fades the SUMMED MIX at the take's two ends and is structurally incapable of
  reaching a splice in the middle: a music range shorter than the take LAPS, so a
  10 s chorus under a 30 s take spliced hard at 10 s and 20 s with no control
  anywhere in the app. `lib/windowFade.ts` is ONE envelope per SOURCE, in SOURCE
  time — silence at the window's IN point, full level through the middle, silence
  again where the sound runs out — and because it is a fact about the WINDOW it
  repeats every lap, which is the point, because the splice does too. It is
  `fade.ts`'s envelope, not a new one (`windowFadeGainAt` is `fadeGainAt` with the
  LAP as its take), so there is one curve in the app and the sweep can hold both
  emitters to it: the mixer schedules `mixWindowRamps` on a gain node it puts in
  series with the source's level, the monitor schedules `liveWindowRamps` from the
  element's own clock, and 3.19 M sampled instants assert both read back through
  `rampGainAt` as the envelope of the position `schedulePositionAt` models. THE
  CLAMP IS A QUARTER where the take fade's is a half, and that is the decision the
  judge panel turned on: a take plays ONCE so a triangle is a worst case, while a
  WINDOW laps, so the same clamp makes a short loop a tremolo. A quarter keeps at
  least half of every lap at full level. THE ROSTER'S SHORT END (0.1 s) is the
  feature: a splice click is a sub-10 ms discontinuity and a "fade the range"
  gesture is 0.5–2 s, so offering only the long end cures a click by cutting a hole
  in the music at every wrap. The OUT edge is `audibleEnd`, never `outSec`, or the
  control would do nothing on exactly the clips whose splice is harshest. It is
  offered for the music AND for a clip's own sound — the LEVEL's precedent, not the
  SPEED's — on the sheet where the range is chosen, which is where it was wished
  for. Unlike the take fade it is PRE-LIMITER by construction and says so;
  THE PLAYHEAD — the take has a clock you can SEE and DRAG. Six cycles of
  time-domain work (the move, the trim window, the music range, the lap
  schedule, the fade) had shipped without one of them being observable without
  exporting a file, and two separate rungs of the ladder below asked for the
  same widget in the same words. `lib/playhead.ts` owns the arithmetic — the
  ruler, the lap, the seek grid, the fade's place on it, and the seek PUMP —
  while the Stage owns the seek, which it already had: `renderAtTime` is what
  the offline exporter walks the take with and it reads `this.offline` exactly
  zero times, so a scrub borrows it whole without entering the render mode and
  inheriting its lifted decoder caps, its frozen backing size and its
  full-resolution rasters.
  THE CLOCK LAPS THE TAKE AND A SCRUB SEEKS. Wrapping the readout over an
  unwrapped clock would have the bar claim 7s while the move sat at phase 37
  (the move is periodic on a FIXED 12s, deliberately not on the take), so the
  CLOCK wraps and the origin moves with it — but the lap re-seeks NOTHING,
  because restarting every clip and the music at a boundary changes what every
  preview this app has ever shown, which is a decision to make on its own and
  not a rider on a ruler. A SCRUB is the opposite case and seeks everything,
  clips and music alike, because parking on 7s is a deliberate act by someone
  who asked for that instant — and the music is seeked through the same
  `sourceTimeAt` the offline mixer and the live watchdog already ask, so three
  callers share one formula.
  The bar is a native `<input type="range">`, which buys pointer capture
  through a drag that leaves the element, the keyboard, the accessible name and
  the app's own 44px range styling for free; `PLAYHEAD_STEP_SEC` is an exact
  multiple of the seek grid so an arrow press and a thumb land on the same
  instant and the pump can refuse a duplicate from either. The position is
  written to the DOM from the component's own rAF and never to React state (a
  `setState` per frame re-renders the whole transport sixty times a second),
  and that loop BACKS OFF to a 250ms timer after forty motionless frames, so a
  parked preview costs four wake-ups a second rather than sixty.
  And it made the transport honest on the way past: `anyPlaying` asked
  `clips.some(playing)`, which answered NO for a collage of photographs
  drifting under a soundtrack — the exact thing THE MOVE and THE SOUNDTRACK
  added — so the button showed Play while the picture moved, pressing it did
  nothing, and on a photo collage it was disabled outright. `StageStatus.rolling`
  answers from the Stage, which is the only place that can see the move, the
  music, the clips AND the park at once.
  THE BEAT — the collage cuts ON THE MUSIC. Four cycles built a time axis and
  a sound (THE SOUNDTRACK, THE TURN, THE FADE, THE PACE) and every clock among
  them was INDEPENDENT of the track: a collage over a 128 BPM song cut every
  5.000 s because `march` says 5.000 s, so the wall and the music walked past
  each other and met by accident. Now the turn's hold is SNAPPED to the beat.
  A BEAT SYNC IS NOT A NEW RATE DIAL, IT IS A QUANTISER ON THE RATE ALREADY
  ASKED FOR — the obvious division roster (every beat / half bar / bar / two
  bars) would have put a fifth chip row on a phone AND made the two controls
  that already answer "how often" into dead weight, which is the exact defect
  the ladder files against the pace. So the mode still says how often it wants
  to cut, the pace still scales that want, and `lib/beat.ts` rounds the result
  to the nearest musical multiple {1,2,4,8,16} of the detected beat — in RATIO,
  not in seconds, because with a 0.5 s beat and a 3 s target the 2 s and 4 s
  holds are a dead tie on the difference and 1.50x against 1.33x on the tempo.
  THE FADE BECOMES A FRACTION OF THE HOLD, which is `lib/pace.ts`'s own
  argument arriving from the other side: a pace can leave `TURN_FADE_SEC` a
  constant because it scales the CLOCK, so `fade/hold` is invariant by
  construction; a beat sync sets an ABSOLUTE hold from outside the roster, and
  174 BPM at 2x is a 1.379 s hold that a constant 0.7 s dissolve would leave
  50.7% soft. `turnFadeFor` caps it at the roster's own worst ratio (ripple,
  20%) and the sweep holds every mode at exactly 20.0% at every tempo.
  DETECTION IS A COMB, NOT A BEAT TRACKER — one period and one phase is all a
  `first + k*hold` schedule can use. An onset envelope (rectified RMS
  difference), autocorrelation for a coarse period, then eleven musical
  RATIOS of it scored by comb and resolved by "the SHORTEST period that
  explains every hit", then a fine (period, phase) search. Three separate
  measurement bugs had to be fixed before that rule meant anything, and each
  was found by a sweep rather than reasoned out: an interpolated tooth, then a
  max-of-pair tooth, both let a comb whose period is a WHOLE NUMBER OF HOPS
  sample only well-aligned onsets and beat the truth (a 180 BPM click track
  measured 60); the real cause is that RMS is a square ROOT of a mean, so an
  onset SPLIT between two windows measures genuinely SMALLER, not merely
  divided — and the fix is a window twice the hop, stepped by the hop, which
  took the alignment bias from 10.3% to 0.8%. Twelve tempi from 60 to 180 BPM
  are now detected EXACTLY, backbeats included. It REFUSES rather than guesses:
  white noise, silence and junk return null, because a collage cutting
  confidently on a beat that is not there is worse than one that never synced.
  It rides the composition code (a 23-character group; all six earlier
  generations still decode byte-identically) and DELIBERATELY NOT THE DICE —
  every other roll re-deals what the collage LOOKS like, and `sync` is a
  relationship to a FILE the dice cannot see.
  THE TURN — the collage CUTS. Every time-axis feature before this one moved
  the CROP (the move), the SOUND (music, trim, the lap schedule, the fade) or
  the CLOCK (the playhead); not one of them changed WHICH PICTURE IS WHERE, so
  a twenty-second export was one deal of photographs held for twenty seconds,
  breathing. Now, every few seconds, the pictures land in different fragments
  and cross-dissolve on the way — the cut, the dissolve and the wipe at once,
  because in a mosaic those three are one event at three granularities.
  EVERY STATE IS A PERMUTATION OF THE DEAL, and that is what the whole design
  is for: source-first duplicate-free filling is this app's oldest promise
  about what a collage IS, and a time axis is exactly the sort of feature that
  voids a static guarantee quietly. `lib/turn.ts` composes STEP permutations,
  so by induction no two fragments can ever hold the same photograph — not at
  rest, not mid-dissolve, not after a thousand cuts.
  That constraint also kills the obvious first design. "Stagger the turns so
  the wall does not blink at once" reads as free until the injectivity
  condition is written down: with slot j showing `base[(j + k_j) mod n]` and
  k_j in {k, k+1}, the map is injective iff the turned set is closed under +1,
  which cyclically forces ALL or NONE — a stagger over a global rotation is
  duplicate-free only in the two cases where it is not a stagger. `ripple` gets
  its stagger the way that survives the proof: it rotates one parity HALF among
  itself, which is a permutation on the nose, and measured at the artifact it
  moves 41.1% of the frame in one cut where `march` moves 93.2%.
  A TURN CHANGES WHICH PICTURE, NEVER WHERE. The cell, its clip path, its
  twist angle and its grown destination box are properties of the FRAGMENT and
  are resolved once per scene; only the source, its crop and its analysis are
  re-pointed. That is what keeps the feature off `computeLayout`, out of the
  SVG geometry and — the one that would have cost the most — out of
  `refreshAdmission`: a fragment holding a live clip is a FIXED POINT of every
  permutation, so decoder ranking stays a scene-time decision instead of
  something a cut could invalidate sixty times a second.
  The seam is a CALLBACK, `resolve(slot, fromSlot)`, not a table: the number of
  cuts in a preview is unbounded while the number of distinct bindings ever
  asked for is one per participating fragment per cut. It answers "the
  photograph that BELONGS to `fromSlot`, decorated for `slot`'s fragment",
  because the FACE and the COLOUR travel with the picture while the FOCUS, the
  TWIST and the MOVE stay with the cell — and only the App knows how to compose
  those two halves. Rest is `NO_TURN` by reference at t=0 and for the whole
  first hold, so the still preview, the raster export and the SVG are
  bit-identical to a build without this file (proved at the artifact: the
  exported JPG differs by <= 1 level with `scatter` running).
  It rides the dice and the composition code — a turn is a RECIPE ("these
  fragments, dealt this way, re-cutting like this"), unlike the title and the
  fade, which are facts about your own render. The group grew to 21 characters
  and the back-compatibility rule came out free: `hasTurn` enters the
  checksummed band by `>=`, so every 18/19/20-length code ever minted decodes
  byte-identically, which the sweep proves by rebuilding forty legacy codes and
  re-deriving their checksums.
  THE PACE — the collage has a TEMPO, and it is the second axis two rungs of
  the ladder below asked for in the same words. Every rhythm this app had
  conflated the SHAPE of a motion with its RATE: `march` holds 5 s and `ripple`
  3.5 s, so "cut faster" was a request for a different PERMUTATION, and the
  move's 12 s cycle was a constant with no control at all. Five chips
  (0.5× / 0.75× / 1× / 1.5× / 2×) now scale the clock the move and the turn are
  read against, on the dice and in the composition code, so the shape rosters
  finally answer only the question they are good at.
  SCALE THE CLOCK, NOT THE PERIODS, and that decision is the whole file.
  Dividing each mode's hold by the rate is the obvious implementation and it
  degenerates: `TURN_FADE_SEC` is a CONSTANT that does not divide with the hold,
  so `ripple` at 2× would hold 1.75 s while still dissolving for 0.7 s of it —
  40% of the take soft instead of 20%, and 80% at 4×. Scaling the TIME leaves
  `fade / hold` invariant by construction, which is why the control needs no
  clamp and no per-mode exception. Measured both ways in the sweep: the shipped
  design holds march/scatter/ripple/swap at 13.6/10.5/19.5/17.0% soft at EVERY
  rate; the rejected one takes ripple from 20.0% to 39.0% at 2×.
  ONE MULTIPLICATION AT TWO SEAMS. `lib/pace.ts` is 30 lines of logic and the
  Stage applies it in exactly two places — `refreshTurn` and `crop` — never to
  `outTime` itself, because the take's own clock is what the ruler shows, what
  the exporter walks and what every audio schedule is written against. Rest at
  zero survives for free (`0 * r` is 0), so the three surfaces that pass no time
  are bit-identical to a build without the file, and the two that do (the live
  Stage and the offline walk it shares with the exporter) get it from one place.
  PROVED WITHOUT A CLOCK. `renderAtTime` is a pure function of the instant —
  which is why the offline exporter can walk it — so the e2e SCRUBS instead of
  waiting: march holds 5 s, so at 1× the wall at t=3.0 is still its opening
  deal, at 2× it has cut, and at 0.5× t=6.0 is STILL the opening deal where 1×
  has already cut. Measured on the canvas: 1× at 3.0 s is **0.0% moved, worst
  channel 0/255** against the opening frame — bit-identical, the hold is a hold
  — while 2× at the same instant moves **94.5% of the frame, worst 202/255**;
  and at 6.0 s the two swap places, 0.5× reading **0.5% / worst 29** where 1×
  reads **94.5% / worst 202**. (Those are the numbers off PRODUCTION, not off
  the dev server.) Three rates,
  same pixels, no timer anywhere — and because a scrub is the export's own path,
  green here is evidence about the file.
  THE SPEED — a CLIP has its own clock now, and it is the first control in this
  app that belongs to a SOURCE rather than to the composition. Five chips
  (0.25× / 0.5× / 1× / 2× / 4×) on the clip's own sheet, beside the trim,
  because both questions there are about the file — which part of it, and how
  fast — while every control outside is about the collage.
  IT ENTERS THROUGH THE ONE RATE THIS APP ALREADY HAD, which is the whole
  implementation: `clipWindow.sourceTimeAt` is the single place output time
  becomes source time and it already took a `rate`, so the live `<video>`, the
  offline picture seek and the offline audio mix picked the speed up with no
  new seam, no new argument threaded through four render paths, and no fourth
  copy of a formula this project has been burned by three times.
  SO THE ONLY REAL DECISION WAS HOW IT COMPOSES WITH VIDEO-LENGTH SYNC, and the
  answer is one people find surprising: under a stretch mode a per-clip speed
  MOVES THE REFERENCE and cannot make one clip outrun another. "Every clip lands
  on ONE on-screen length" is a constraint on the result, so a speed cannot
  break it — what it changes is which length the reference IS, because the
  reference is taken over `window / speed` rather than over the files. Under
  'loop' (the default) there is no reference and the rate simply IS the speed,
  which is the case a user has in mind. The sheet SAYS which of the two is in
  force rather than leaving it to be discovered. The rejected design — sync
  first, multiply the speed on afterwards — is refuted in the sweep by up to
  **61.4×** of on-screen spread between clips that asked to be the same length.
  THE ROSTER IS POWERS OF TWO, and here that is a guarantee rather than a
  legibility choice (the opposite of `lib/pace.ts`, which deliberately carries
  0.75 and documents that reversibility is a property nothing needs): a speed
  DIVIDES a window to pick the reference and then MULTIPLIES a source time a
  decoder is asked to seek to, so the same quantity makes a round trip through
  both. 4000/4000 windows round-trip bitwise at {0.25, 0.5, 1, 2, 4}×, against
  3075/4000 at 0.75×.
  PROVED AS A RE-PARAMETERISATION, ON PRODUCTION PIXELS. A speed is not "a
  different picture", it is the clip's own clock read at a different rate — so
  the frame at output 1.5 s under 2× must be THE SAME FRAME as the frame at
  output 3.0 s under 1×. Measured: **0.0% of the frame differs, worst channel
  0/255** — bit-identical — while two genuinely different instants on the same
  clip differ by **99.2%, worst 208/255**, so the equality is not vacuous. Both
  directions are measured (2× reads r,g,b and then LAPS a 6 s clip back to r
  inside a 5 s take, which 1× cannot do at all; 0.5× is still on the first third
  at 3.0 s where 1× has moved to the second), and every instant is on the
  playhead's 0.1 s grid because a range `fill` off the grid is rejected as
  "Malformed value" and reads like a broken selector.
  THE STRIP — the ruler stops measuring an empty ten seconds. Under the
  playhead's bar, on the playhead's own axis: a row of CUT MARKS where the
  collage re-deals, and one LANE per timed source (each clip, then the music)
  drawn as the passes it makes through the take, the last one short when the
  take ends mid-lap. `lib/takeMap.ts` is the arithmetic, in fractions, exactly
  as `fadeMarks` already was.
  IT IS DERIVED FROM THE COMPOSITOR'S SCHEDULE, NOT FROM A SECOND BELIEF ABOUT
  IT. `cutPlan` collapses `turnAt`'s two branches into one output-time
  `{hold, first, fade}` — the roster's hold divided by the pace rate (because
  `paceTime` scales the CLOCK, so a boundary at scaled `k*hold` is at real
  `k*hold/rate`, and the fade divides with it), or the beat grid verbatim and
  UNPACED, which is the one decision the sync feature turns on at the Stage. The
  sweep does not restate that algebra; it imports `turnAt` and interrogates it:
  4,511 marks, each asserted to be a boundary the compositor agrees with, plus a
  240 Hz walk of 180 schedules proving no cut is MISSING. A lane's period is
  `clipWindow.effectiveLength` — the same function the live element, the offline
  seek and the offline mixer read — so THE SPEED and the sync mode reach the
  drawing for free, and the seam is asserted against `sourceTimeAt` wrapping the
  window rather than against `length / rate` written out a second time.
  AND IT FOUND AN ERROR IN WHAT WAS ALREADY THERE. A range thumb's centre
  travels from `thumb/2` to `width - thumb/2`, but everything drawn beneath the
  bar was positioned against the TRACK's full width — so the fade wedges have
  always been out by up to half a thumb (13 px of a 227 px bar is 6% of the
  take, most of a second on a 15 s one). Invisible while the wedges were the
  only thing there, and fatal to a mark whose entire claim is "the playhead
  crosses this when the collage cuts". `--range-thumb` is now one token, used by
  BOTH engines' thumbs (WebKit 26 px and Firefox 22 px, for no reason) and by
  the one inset that wraps the wedges and the strip together. Measured at the
  artifact: at the 5 s cut of a 15 s take the thumb's computed centre is 408.0
  and the mark is drawn at 408.0.
  WHAT IT MAKES VISIBLE FOR THE FIRST TIME is a RELATIONSHIP, which is why it is
  worth pixels: THE BEAT shipped two cycles ago and the exported file was the
  only witness that a sync had taken. Now `march` over a 15 s take draws two
  marks at 1/3 and 2/3, and one tap of `sync` moves them to three at 4/15, 8/15
  and 12/15 — the same mode, the same take, the music deciding.
  THE STILL TAKE — the ruler and the strip finally describe a collage of
  PHOTOGRAPHS, which is the commonest thing this app makes and was the one
  composition both of them said nothing about. Two halves, both about the same
  hole: what is in a take when nothing in it is a source.
  THE DRIFT ROW. The move is periodic on `MOVE_CYCLE_SEC / paceRate` and
  appeared nowhere on the strip, so photographs + a move + HOLD + no music drew
  NO STRIP AT ALL (`empty`) — a bare ruler over ten seconds the collage was busy
  for. It is a ROW, not a lane (`takeMap.ts` DECISION 5): `TakeStrip` DECISION B
  reads a lane's identity off its POSITION against the chip row below, and
  `MAX_LANES` is a budget for SOURCES, so a row with no chip and no place in
  that budget belongs with the CUTS above the lanes — both are facts about the
  whole wall rather than about one picture. Amber, the fourth colour in the
  code, and the row is drawn by the same `Passes` component the source lanes
  are, extracted the moment there was a second kind of row. A seam is an instant
  the collage is back at REST, which is the one thing `sampleMove` guarantees
  BY REFERENCE, so the sweep asserts every seam against the compositor's own
  function (3,725 instants, identity) exactly as the cut marks are asserted
  against `turnAt`. At the artifact: seams at 0.0000 and 0.8000 of a 15 s take,
  measured as the pass's own box against the row's; 2× makes it three passes.
  THE DERIVED CLOCK. The tick is demand-driven, so a still collage under music
  drew once and idled — and the playhead sat at 0 for the length of the song
  while the take was genuinely running. `outTime` was already `(now - anchor)`,
  i.e. a pure function, so `takePosition` now COMPUTES the position when asked
  instead of reading whatever the last drawn frame left behind: the Stage
  schedules nothing at all, and the Playhead's pump — already a loop — reads a
  getter. The tick's last branch keeps `clockRunning` true while the soundtrack
  ELEMENT is rolling, which is what holds the anchor valid across the idle, and
  `pulseClock` wakes the loop for exactly one frame on that element's `play` /
  `pause` / `ended` because the tick already contains both edges. The cost of
  the derivation is `freezeClock()`: `outTime` can now be far behind the real
  position, so every caller that means "hold HERE" has to write it back —
  `stop()`, `applyPowerState`, and `setTake`'s shorter-ruler wrap. Measured:
  1.900s -> 4.900s over 3 s of wall clock with the canvas hash IDENTICAL at both
  ends (the control — if anything were drawing, the clock would have run for the
  old reason), and 0.000s -> 0.000s with the one line reverted.
  THE DESK — the eight looks are now four axes anybody can move. `Grade` was
  already five continuous numbers, so the engine did not move: the four
  surfaces that paint still read ONE ordered pipeline out of `lib/grade.ts`.
  What changed is what they are HANDED — a roster id OR the five numbers
  themselves (`LookRef`), both structured-cloneable, so the second kind crosses
  to the export worker's thread the way the title plan already did.
  WARMTH IS BIPOLAR BECAUSE THE ROSTER ALREADY WAS. `sepia` and `hue` are not
  two quantities a person has an opinion about; they are two halves of one
  tonal decision, and the roster proves it — `warm` is sepia 0.30 unrotated,
  `cool` is sepia 0.70 at 190deg, two points on one axis running through
  untoned. So the desk is EXPOSURE / CONTRAST / COLOUR / WARMTH: four sliders
  rather than five, and the fifth was never a control, it was a coordinate.
  EVERY ONE OF THE EIGHT IS A POINT IN THIS SPACE, exactly. That is the
  invariant the whole feature rests on — a person opens ADJUST to drag ONE
  axis, so the other three must leave the picture where the preset put it.
  `gradeFromDesk(deskFromGrade(g))` returns g field-for-field (`Object.is`) for
  all eight, and at the artifact opening the desk on a graded collage moves the
  worst channel by 0/255.
  THE GRID IS ENFORCED ON THE WAY IN, and that is correctness rather than
  tidiness. `num` is exact at six decimals BECAUSE a sepia term is a
  three-decimal constant times an amount on the two-decimal `GRADE_GRID` — a
  property of a roster written by hand. A desk COMPUTES its amounts (warmth
  0.1 x 0.6 is 0.06000000000000001 in binary floating point), so unsnapped it
  lands as a difference between the exported SVG and the exported JPEG of the
  same collage. `snapDesk` is `snapRoll`'s argument one roster out: quantising
  is only lossless if the state is already on the grid.
  IT RIDES THE CODE AS THE FIRST OPTIONAL GROUP. Four axes, two base-36
  characters each, present ONLY when an axis is off its preset — so a collage
  on one of the eight still mints the exact 21-character group this codec has
  minted since THE BEAT, and 22..28 belongs to no generation at all. That gap
  is the feature: a desk code that lost characters in transit is refused by
  `MINTED_GROUP_LENGTHS` rather than sliced into a shorter body that opens,
  cleanly, as somebody else's collage.
  THE DICE STILL DEAL A ROSTER, and therefore drop a custom grade — a roll is a
  destructive composition event and is already on the undo stack, so the axes
  come back with one press. Defending them there would leave the dice unable to
  change the look at all, which is the one thing a die is for.
  THE LEVEL — how loud each source sits in the mix. Every gain in this app was a
  BOOLEAN WEARING A NUMBER'S CLOTHES (`describeAudioSources` emitted
  `wanted ? 1 : 0`, `soundtrackSource` emitted `t.muted ? 0 : 1`, `applyMutes`
  wrote `audible ? 1 : 0`), so "how loud is the music under the clips" had two
  answers: ALL and NOTHING. `lib/level.ts` is one roster of five (-6 dB a step,
  exact halvings, 100% down to a 6% bed), one `mixGain(wanted, level)` that BOTH
  row emitters now call so a clip and the music cannot hold two opinions about
  what a level means, and one `livePath` for the room. Mute is untouched and
  still owns 0: a level is what the sound does when it is NOT muted, so the
  speaker button stays one control for one fact. The roster rides the sheet the
  trim and the speed already share, which is where a per-SOURCE question belongs
  and which is why the dock's one-line scroll row gained nothing but a badge.
  `mixSources` changed by NOT ONE LINE — it already multiplied by `src.gain` —
  which is the same sentence THE SOUNDTRACK earned for the same reason.
  Measured at the artifact by DIVIDING ONE TONE BY ANOTHER IN THE SAME FILE (the
  true-peak limiter scales every sample by one scalar, so it cancels out of a
  ratio and out of nothing else): music/clip 1.2912 -> 0.3227 = **0.2499x, 12.0
  dB down** against a nominal 12.04, with the clip's own 440 Hz bin reading
  0.08502 in BOTH exports — the control moved the source it names and nothing
  else. The clip path travels a different route (Stage-only lifetime,
  `describeAudioSources` instead of `soundtrackSource`) so it is measured
  separately: A/B 0.7183 -> 0.1782 = 0.2481x.
  THE REFRAME — the picture moves inside its fragment, by hand. Every crop this
  app had ever drawn was decided FOR the user: `analysis.face` is a detector's
  guess, `energy` is its fallback, THE FOCUS is five automatic rules and THE
  MOVE nudges the anchor on a clock — and not one of them is a way of saying
  *no, THAT part of THAT photograph*. So the most ordinary complaint anyone has
  about a collage, **this one is cropped through his head**, had exactly two
  answers here: re-roll the whole wall and hope, or throw the picture away.
  `lib/reframe.ts` is pure and its contact with the geometry is ONE TERM at the
  front of `calculateSmartCrop`'s anchor chain (`an.frame || an.face ||
  an.energy || CENTRE`), so all four surfaces that produce pixels inherit it
  without knowing it exists. **IT IS KEYED BY ASSET ID, NOT BY SLOT** — a frame
  is a corrected FACE, so it belongs on the side of `turnResolve`'s own line
  where the face and the colour already sit, and it therefore survives a
  shuffle, a re-deal, a swap and a turn. Keyed by slot it would have been undone
  by the next roll, and rolling is what this app is for. **THE STATE IS THE
  CROP, so there is no state to carry**: `dragToFrame` reads the position off
  the CLAMPED source rect the shipped crop function just returned rather than
  off the previous anchor, which is what makes an edge release on the very next
  pixel back instead of banking invisible travel. A LEAN ROTATES THE FINGER, not
  the picture (the drag is rotated by -twist into the photograph's own axes; the
  naive version sends it 37.5% off the finger's line at the roster's 22deg
  ceiling). The way IN is the drag on the ARMED fragment — no mode, no fourth
  verb — and the only button is RECENTRE, which appears solely on a picture
  somebody actually moved.

## THE CAPABILITY LADDER (→ CapCut — GROW this list as you learn)
Each cycle pick ONE rung by **leverage × feasibility** (what a real editor reaches
for most, vs build cost). Mark shipped ones `[x]`; add rungs as you find gaps.
- [x] **PREVIEW FIRST, ONE EDITING TASK AT A TIME (C3712)** — native art templates, a media import or the original lyric sample start a project. Main editing opens Add, Layout, Look, Motion or Text in one bounded inspector; media Details uses the same screen-space budget. The whole artwork fits the measured remaining band and expanded preview retains playback. Art Room exposes the selected layer's controls and keeps secondary recipe/HTML actions collapsed. Browser geometry, input/keyboard focus, retained Stage/decoder/playhead, save/reopen and encoded video prove the route.
- [x] **TIMED LYRICS** — a single non-overlapping track of editable cues on the
      output clock, with SRT/WebVTT import/export and project/recovery persistence.
      A cue replaces the static title on [start,end); the title returns in gaps.
      Caption geometry is planned once, including long-cue shrink-to-fit, then
      reused by Stage and export. Cues do not ride a public composition URL.
      Limits: 200 cues, 240 characters each, 50 ms minimum and one-hour range;
      unsupported subtitle styling is visibly refused, never silently stripped.
- [ ] **ORIGINAL AUDIO AND VIDEO MUST TRAVEL IN THE PROJECT** — highest-priority
      independence gap. Current files preserve images, settings, pins and lyrics;
      moving sources and soundtrack remain session media. Package the originals
      with a versioned manifest/checksums and deliberate relinking. Acceptance:
      fresh profile, network off, saved project reopened with the same sources,
      audible music, pins and lyrics, then a verified second video export.
- [ ] **AUTHOR A MUSICAL SEQUENCE** — split/reorder/trim several shots with a
      global soundtrack and lyric clock. Start with cuts and one transition.
      Every boundary must agree in preview, scrubbing, save/reopen and the file.
- [ ] **OPTIONAL LOCAL GENERATION AS AN ASSET JOB** — one pinned workflow with
      inputs, seed, provenance, progress, cancel/retry and rollback. Its output
      becomes ordinary editable media. An unavailable model/worker must not stop
      a saved project from opening or rendering previously generated assets.
- [~] **Timeline & trim** — the single biggest CapCut gap, now part-shipped.
      **TRIM (in/out) is done**: `lib/clipWindow.ts` owns the one function that
      maps OUTPUT time to SOURCE time (`sourceTimeAt`), and the three timelines
      that used to each carry a copy of that formula — the live `<video>`
      watchdog, the offline frame seek, the offline audio mix — now ask it. Trim
      composes with video-length sync, because sync is fed the WINDOW length
      rather than the file's duration.
      **PLAYHEAD SCRUB IS NOW DONE TOO** — see THE PLAYHEAD in CURRENT STATE.
      It is the first timeline WIDGET in this app: a ruler over the take, a
      position that tracks the clock, and a drag that parks the whole
      composition on any instant of it.
      **AND DRAG-REORDER IS DONE, IN THE GRAMMAR A COLLAGE HAS → THE SWAP.**
      There is no timeline to drag along: the sources sit in FRAGMENTS, so
      reordering them is trading two fragments' pictures. `lib/swap.ts` owns the
      rule; the armed puck's third verb parks one fragment and the next tap on
      the canvas names its partner. The entry was right that this is direct
      manipulation of the SOURCES and right that it is its own increment; what
      it did not predict is that HALF the work is not the transposition at all
      (see THE SWAP'S SECOND HALF below). Still owed on this rung: **split/cut**.
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
      **AND THE FADE NARROWED IT AGAIN WITHOUT CLOSING IT.** `applyFade` is now
      swept directly on real `Float32Array`s (`tests/unit/fade.invariants.mjs`,
      including 2.16 M samples proven `Object.is`-identical with the fade off),
      so the ENVELOPE is unit-covered end to end — but the two lines in
      `mixSources` that hand it `mixed.getChannelData(c)`, `mixed.sampleRate`
      and `seconds` are not, and they are exactly the kind of wiring the fake
      `OfflineAudioContext` above exists to reach. Today the only guard on them
      is `tests/e2e/fade.spec.ts`, which is a real artifact measurement and
      still a whole browser render per assertion.
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
- [x] **Drag-reorder, playhead scrub and split/cut** — the timeline WIDGET, the
      remaining half of the timeline rung. Trim is a timing CONTRACT and is done;
      these are direct manipulation and are their own increment. **TWO OF THE
      THREE ARE NOW SHIPPED** (playhead scrub, then THE SWAP); split/cut is
      carried forward on the timeline rung above.
- [ ] **THE SWAP'S SECOND HALF IS THE PIN REWRITE, AND THAT IS THE GENERAL
      LESSON, not a detail of this feature.** `shuffledIndices` is DERIVED — an
      effect recomputes it from nine inputs, and `layoutItems` alone re-runs on a
      gutter nudge, an entropy nudge, a mode change. So ANY direct manipulation
      written only into the assignment has a shelf life measured in slider
      touches, and the failure is not "it reverted": a pin already on one of the
      two cells drags its old picture back and leaves HALF a trade, which is a
      DUPLICATE on screen. The one state a re-deal honours is `lockedCells`, so
      the swap re-pins both cells. Measured, not argued: the mutant that skips
      the rewrite fails **162,521** of the sweep's assertions.
      **THE OPEN QUESTION THIS LEAVES** is that pinning is now something a
      gesture does to you rather than something you ask for. It is disclosed
      (both fragments come back wearing the badge, and the notice says so the
      first time) and it is undoable (a pin is one tap), but the honest next cut
      is a WEAKER pin — "hold this until I re-roll" versus "hold this forever" —
      which is a second kind of lock and therefore a real design decision, not a
      flag.
- [ ] **A SWAP CANNOT TRAVEL IN A COMPOSITION CODE.** It joins pinned fragments
      and the title on the "in the app but not in the code" list, and for the
      same structural reason the pins are on it: an arbitrary permutation of n
      fragments is n! of information and a code is a fixed-length recipe. It
      does travel in the PROJECT file and in the SVG's JSON_MANIFEST (both carry
      the whole `AppState`, pins included), and — unlike an eviction — it is
      recoverable through the rail's Undo — though only after `assignNonce`, and
      the first version of this entry asserted it wrongly (see the scar: the
      pins reverted and the pictures stayed traded, 285 RGB from the picture
      Undo claimed to restore). Undisclosed in the strip, which is the honest
      gap, exactly as it is for pins.
- [ ] **THE PENDING PILL SITS ON THE FRAGMENT IT PARKED, so on a small fragment
      it covers the tap that would cancel.** Found by the WebKit and Mobile
      Chrome runs of swap.spec T4 — a centre-of-fragment tap landed on the pill.
      The guaranteed outs (the pill's own 44 px X, and Escape) are both there and
      both tested, so this is a convenience that degrades rather than a trap; but
      "the gesture the affordance covers" is a shape worth naming, because the
      armed puck has the same geometry and will meet it again.
- [~] **Transitions** — part-shipped as **THE TURN**: the cross-dissolve, the
      cut and (in `ripple`) the wipe, expressed in the grammar a collage has —
      between DEALS rather than between clips, because a mosaic shows every
      source at once and has no shot to cut away from. Five modes on one chip
      row (`hold` / `march` / `scatter` / `ripple` / `swap`), on the dice and in
      the share code, held by one pure module (`lib/turn.ts`) that the only
      moving surface (`stage.ts`, which is also what the offline exporter walks)
      reaches through `refreshTurn` — sited beside `refreshMoveCrops` and called
      from the same two places for the same reason: `drawFrame`'s contract is
      zero allocation and resolving an asset allocates.
      Still owed on this rung: a transition between LAYOUTS (the partition
      itself changing, which needs a second `computeLayout` and a second draw
      pass, and is its own increment), a per-mode SPEED (the hold is a property
      of the mode today, exactly as the move's 12 s cycle is), and a transition
      the SVG can express — it cannot, for the same reason it cannot express the
      move.
- [x] **THE TURN'S HOLD IS A PROPERTY OF THE MODE, so "cut faster" is not
      askable → THE PACE.** CLOSED, together with the move's own speed rung
      below, by the one control both entries predicted in the same words. The
      generalisation turned out to be even smaller than "a rate control that
      snaps to a grid": a rate is a ROSTER, so it needed no `snapRoll` arm at
      all — a quantised index is quantised by construction, and it rides the
      code through the machinery `look`/`move`/`turn` already built. What the
      two entries did NOT predict is the implementation trap, and it is the
      whole of `lib/pace.ts`: dividing the hold is wrong because
      `TURN_FADE_SEC` does not divide with it. Original text: `march` is 5 s,
      `ripple` 3.5 s, and the only way to change that is to pick a different
      mode — which also changes the permutation. The two are independent and
      the roster pretends they are not.
- [ ] **THE PACE IS ONE DIAL OVER TWO INDEPENDENT RHYTHMS.** A slow ambient
      drift under fast cuts is a real look and it is unaskable: one rate scales
      the move and the turn together. Shipping one dial was the deliberate first
      cut — the point of the rung was to make the SHAPE rosters honest, not to
      double the roster count — but the two clocks genuinely are independent,
      and the honest generalisation is `moveRate` and `turnRate` as two fields.
      The cost is two more code characters and a second chip row on a phone,
      which is exactly the NON-CLUTTERY question that should decide it.
- [ ] **THE BEAT SNAPS THE CUT AND NOTHING ELSE.** The move's 12 s cycle, the
      trim windows and the fade are all still on their own clocks, so a collage
      cutting on the bar can be drifting on a period that has nothing to do with
      the music. The turn was the right first cut — it is the only one of the
      four whose events a listener can HEAR land — but a drift whose cycle is a
      whole number of bars is the obvious next one, and it is the same
      `snapHold` call.
- [ ] **A DOWNBEAT IS NOT DETECTED, ONLY A BEAT.** The grid says where the
      pulses are and says nothing about which of them is beat one, so a
      four-beat hold lands on SOME beat of the bar rather than on the ONE. The
      phase is snapped to the nearest beat in both directions, so the choice is
      arbitrary rather than late — but "cut on the downbeat" is a different and
      harder question (it needs harmonic change or a bar-level pattern, not a
      comb), and it is what stands between this and sounding deliberate on
      material with a strong bar structure.
- [ ] **A LAP RE-PHASES THE MUSIC AND NOT THE GRID.** The soundtrack loops when
      the take outruns its window; unless that window is a whole number of
      beats, the song's downbeat moves on the second pass while the cut grid
      does not, so a long take drifts off the music it started on. Same family
      as "a cut at a lap is a hard cut" below, and the honest fix is the same
      one: snap the WINDOW to the grid.
- [ ] **A PACE DOES NOTHING TO A COLLAGE THAT IS MOSTLY VIDEO, AND NOTHING SAYS
      SO.** The same shape as the turn's own gap: a live clip is excluded from
      the turn ring, and a clip's playback rate is untouched by the pace, so a
      wall of video has almost nothing for either control to move. The caption
      teaches the still case ("pick a MOVE or a TURN and this sets the tempo")
      and says nothing about the video one.
- [ ] **A CUT AT A LAP IS A HARD CUT.** The turn is periodic on a FIXED hold
      and deliberately not on the take, for the reason THE MOVE settled — a
      duration-keyed schedule would make the same collage cut differently at
      10 s and at 30 s, and differently again when the device cap clips the
      take. The consequence is that the live preview's clock WRAPS at the take
      length and the wall snaps back to its base deal with no dissolve. The
      EXPORTED file never sees it (the offline walk is monotone from 0 to L), so
      this is a preview artefact of the existing lap decision rather than a new
      defect — it is filed here because it is the first feature where a lap is
      plainly VISIBLE rather than subtle, and that raises the price of
      `THE LAP RE-SEEKS NOTHING` below.
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
      Timed cue text now ships separately as TIMED LYRICS (C3709).
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
- [x] **THE LOOK is a preset roster, not a grading desk → THE DESK.** CLOSED.
      The entry was right about the engine (five numbers were already there; the
      four surfaces did not change) and right about the trap — and the trap
      turned out to be the load-bearing half, because the grid is WHY the SVG
      and the JPEG are the same picture, not housekeeping. What it did not
      predict is the shape of the control. Five numbers do not make five
      sliders: `sepia` and `hue` are two halves of one tonal decision and the
      roster was already using them that way (`warm` = sepia 0.30, `cool` =
      sepia 0.70 at 190deg), so the desk is FOUR axes and warmth is bipolar.
      Every one of the eight is a point in that space, bit for bit, which is
      what makes opening the panel a no-op instead of a restatement. It also
      turned the codec's first OPTIONAL group: 21 characters for a roster look,
      29 with a desk, nothing minted between — and that gap refuses a truncated
      desk code instead of reading a shorter generation out of it.
      Original text: *"Eight fixed grades is the right first cut — a picker you
      have to scroll is a settings screen — but `Grade` is already five
      continuous numbers, so exposing them as sliders is a UI change rather
      than an engine change. The moment that happens the two-decimal
      `GRADE_GRID` stops being a property of a hand-written roster and has to be
      enforced on the way in, exactly as `snapRoll` does for the composition
      sliders."*
- [ ] **THE DESK IS ONE GRADE FOR THE WHOLE COLLAGE, and the roster row above it
      is now a SEED rather than a state.** Tapping a preset with a custom grade
      in force replaces it outright, which is right — but it means the eight
      chips answer "where did you start" and nothing shows you the way back to a
      grade you liked except undo. The honest next cut is not more chips: it is
      that a custom grade is a NAMEABLE thing, i.e. the same problem THE
      COMPOSITION CODE already solved one level up, and the code already carries
      the four axes. A "keep this grade" slot is a UI question, not an engine one.
- [ ] **A DESK CANNOT REACH THE GRADES THE FIVE NUMBERS CAN EXPRESS.** `warmth`
      collapses (`sepia`, `hue`) onto ONE axis through two roster points, so a
      tone at 45deg — legal in `Grade`, reachable by a hand-edited project file
      — has no desk that produces it. `deskFromGrade` answers `null` for those
      rather than clamping to a plausible neighbour, and `deskForLook` falls
      back to NO_DESK, so nothing in the app can currently arrive there. It
      becomes real the day a template, an import or a LUT wants a tone this axis
      does not pass through, and the answer then is a second axis (a TINT), not
      a wider warmth.
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
      28.1/255). **USER-SET SLIDERS ARE NOW SHIPPED — see THE DESK in CURRENT
      STATE, and the rung it closed above.** Still owed on this rung:
      per-fragment grades, LUT import, and a grade on the BACKGROUND
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
      **THE FADE IS NOW SHIPPED**, and the note that used to sit here — "the
      honest place for it is the sample domain, right where the peak limiter
      already walks the whole rendered buffer" — was right about the offline
      path and BLIND to the other one. The realtime `record()` fallback encodes
      a LIVE graph and has no buffer to walk, so the same envelope has to exist
      twice: once as samples, once as `AudioParam` automation. That is what
      forced the shape to be LINEAR (DECISION 1 in `lib/fade.ts`) — an
      equal-power curve needs `setValueCurveAtTime` with a sampled table on one
      side and a closed form on the other, i.e. a fade that is measurably not
      the same fade depending on which recorder your browser gave you. The
      general shape, and it is the third time this project has met it: **an
      "obvious" implementation note names the path you were already looking at.
      Count the surfaces BEFORE choosing the representation** — ONE LAYOUT
      counted four, THE TITLE counted four, this counted two and the count is
      what picked the curve.
      **BEAT-SYNC IS NOW SHIPPED** — see THE BEAT in CURRENT STATE. It is the
      first feature in this app where the SOUND drives the PICTURE rather than
      riding under it, and it needed nothing new from this rung: the decode it
      analyses is the same `decodeAudioData` the mixer does, at 8 kHz mono
      because tempo survives losing every frequency detail.
      **VOLUME PER SOURCE IS NOW SHIPPED** — see THE LEVEL in CURRENT STATE. The
      thing this list asked for by name, and the shape of the answer was decided
      by a fact the entry did not contain: every gain in the app was already a
      `number`, so the feature was not "add a level", it was "stop writing 1 into
      the number you have". Three call sites, one of them (`mixSources`) needing
      no edit at all.
      **A FADE AT THE RANGE EDGES IS NOW SHIPPED** — see THE RANGE FADE in
      CURRENT STATE. Named as NOT SHIPPED in the same cycle that shipped the audio
      range, and then wished for verbatim from the field ("Need to be able to add
      fade even when selecting clip range for audio"), which is the second time
      this book's own owed-list has been read back to it by a user. The shape was
      decided by a 3-lens judge panel that split on the one question that mattered
      — every lap, or once — and the split RESOLVED rather than being voted
      through: the two lenses arguing every-lap were right that a once-only fade
      duplicates the take chip and leaves every intermediate splice clicking, and
      the lens arguing against was right that 0.25–1 s dips at every wrap sound
      broken. What survives both is every-lap WITH a 0.1 s roster entry and a
      quarter-lap clamp. A panel is worth casting when its disagreement is
      load-bearing; here it moved the roster and the clamp, not the decision.
      Still owed on this rung: an ASYMMETRIC fade (in and out are one control
      today, which is one job and the right first cut, but a long tail under a
      short head is what people actually reach for), a CROSSFADE at the lap join
      (a fade to silence is the honest first cut and an overlap is the better
      one — it needs two nodes and a period the picture also has to agree with),
      DUCKING, and — now that a grid exists — snapping the TRIM to it.
- [ ] **A LEVEL IS SET BY HAND; DUCKING IS THE ONE PEOPLE ACTUALLY WANT.** "Turn
      the music down" is what somebody asks for, and what they MEAN is "turn it
      down while the clips are talking". THE LEVEL makes the ask expressible for
      the first time and answers the static half of it; the moving half needs the
      clip's ENVELOPE, which means analysing a decode the live path does not have
      — the same `decodeAudioData` THE BEAT already does at 8 kHz mono, which is
      the seam to build it on rather than a new one. The honest first cut is
      probably not a compressor at all: it is a per-lap gain the offline mixer
      already knows how to schedule, because `audioSchedule` emits one node per
      lap and a node takes an `AudioParam`.
- [ ] **A LEVEL DOES NOT TRAVEL, in a code OR in a project file** — the same
      sentence, word for word, that the trim, the speed and the music itself
      already carry, and it is now the FOURTH per-source fact in that state. The
      code's boundary is right and does not move (a code is a recipe somebody
      else opens with their own sources). The PROJECT FILE's is not: a project is
      reopened with the same files by the same person, and it silently drops four
      things they set. Four instances of one gap is the point at which the fix is
      one `SourceState` the project writes and reads, not a fifth entry here.
- [ ] **THE LEVEL IS BEHIND A BUTTON THE TRIM DISABLES.** The roster lives on the
      sheet the trim button opens, and that button is `disabled` until the source
      is longer than `MIN_WINDOW_SEC` and while the app is `busy`. So a clip too
      short to cut cannot be quietened either, and neither can anything during a
      render. Correct for a TRIM (a sheet opened against a zero-width axis is two
      handles that do nothing) and wrong for a LEVEL, which has no length
      precondition at all. It is the cost of putting a second question behind one
      door and it is small today — 0.15 s of video is not a real clip — but the
      door's condition should be the union of what is behind it, not the first
      thing that was.
- [~] **Speed** — part-shipped as **THE SPEED**: one multiplier per clip, five
      chips (0.25× / 0.5× / 1× / 2× / 4×) on the clip's own sheet beside the
      trim, `lib/speed.ts`. The rung's own note was right on both counts — it IS
      a property of the SOURCE, not of the composition's clock, and it composes
      with THE PACE — and the pitch question it flagged turned out to be the
      interesting half (see the scar below: the preview was time-stretching
      where the export resamples, and the fix was to stop the PREVIEW
      flattering the file). It enters through the ONE `rate` in
      `clipWindow.sourceTimeAt`, so the live element, the offline picture seek
      and the offline audio mix all got it without a new seam.
      RAMPS AND FREEZE FRAMES ARE NOT SHIPPED — see the two rungs below.
- [ ] **A SPEED IS A SCALAR, NOT A CURVE — a RAMP is the next cut.** CapCut's
      speed curve (slow into a beat, snap out of it) needs a per-clip envelope
      over output time, which is the keyframe machinery `lib/motion.ts` has for
      position and scale and nothing has for TIME. The seam is already the right
      shape: `sourceTimeAt` takes a rate as a NUMBER, and a ramp is that number
      becoming a function of `t` — i.e. the source time becomes an INTEGRAL of
      the rate rather than a product, which is the whole build cost. Note the
      audio consequence before starting: an `AudioBufferSourceNode` can be
      automated on `playbackRate`, so the offline mixer CAN follow a curve, but
      `audioSchedule`'s lap arithmetic is written in terms of a constant rate
      (`L / r`) and would need the same integral.
- [ ] **A FREEZE (speed 0) IS NOT THE BOTTOM OF THE ROSTER.** `sourceTimeAt`
      would hold at the IN point for free (`t * 0` is 0), which makes it look
      like a one-line addition. It is not: `AudioBufferSourceNode.playbackRate`
      of 0 is not a still frame, it is an undefined-to-stalled node, so a frozen
      picture would run under sound that keeps going — the preview/export
      divergence class this project files scars about. A freeze needs its own
      answer for the sound (mute the clip for the frozen span, most likely) and
      is therefore its own rung, not a sixth chip.
- [ ] **A SPEED DOES NOT TRAVEL, in a code OR in a project file** — the same
      hole THE TRIM and THE MUSIC have, and the same reason: a composition code
      is a RECIPE somebody else opens with their own sources, and a speed is a
      fact about a FILE the code cannot see. Consistent, and still a real gap
      the moment `.collage` projects carry clips rather than re-importing them.
      Fix all three together or not at all.
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

- [~] **A MOVE IS ONE ROSTER PICK FOR THE WHOLE COLLAGE, and the speed is not a
      control.** THE SPEED HALF IS CLOSED by THE PACE: `MOVE_CYCLE_SEC` is
      still 12, but the clock it is read against is not, so the drift breathes
      every 6 s at 2× and every 24 s at 0.5× — and the roster's periods stay
      relative to each other, which is what keeps a rate from turning into
      five more moves. The prediction that a user-set speed "has to be SNAPPED
      to a grid on the way in" was right about the requirement and wrong about
      the mechanism: a roster IS the grid.
      Still owed: ONE MOVE FOR THE WHOLE COLLAGE. `sampleMove` already takes
      the spec per slot, so per-fragment moves remain a UI change rather than
      an engine change.
- [x] **THE STILL PREVIEW OF A MOVING COLLAGE IS ITS FIRST FRAME → THE
      PLAYHEAD.** CLOSED, by exactly the widget this entry predicted: "the
      honest next cut is a scrub or a 'show me' that runs one cycle, which is
      the same widget the timeline rung wants anyway." Right on both counts —
      one bar closed this rung and half the timeline rung, which is the whole
      argument for reading the ladder before picking off it. The underlying
      property is unchanged and still correct: rest-at-zero means the still
      preview IS the export's opening frame. What changed is that you can now
      move off zero without spending a render to see what is there.
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
- [x] **THE MIX HARD-CUTS AT THE END OF THE TAKE → THE FADE.** Shipped the very
      next cycle and this entry was never marked — found by THIS cycle while
      reading the ladder in order to pick from it, which is exactly the harm an
      unmarked rung does: the next cycle can spend itself re-shipping something
      that is already live. Original text follows.
      **THE MIX HARD-CUTS AT THE END OF THE TAKE.** Ten seconds of music under a
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

- [ ] **THE LAP RE-SEEKS NOTHING, so the preview and the export still walk apart
      inside a take.** Deliberate, and named here so the next cycle can take it
      as its own decision rather than as a rider: the clock wraps at the take
      but the clips and the music are left running, because restarting every
      source at a boundary changes what EVERY preview this app has ever shown.
      The divergence it leaves is pre-existing and orthogonal — a clip's live
      position is governed by its element (native loop, or the `enforceWindow`
      watchdog) while the export computes `sourceTimeAt`, so the two free-run
      against each other from the first frame — but a playhead is the first
      thing in this app that makes it VISIBLE, which is exactly what raises it.
      The honest next cut is `restartTake()`: one method that seeks every clip
      to its window start, the music to its own, and the move to zero, called
      from the lap AND from `setCaptureActive` (see the rung below), so the two
      cannot drift apart.

- [ ] **`setCaptureActive` RESTARTS THE MOVE AND THE MUSIC AND NOT THE CLIPS, so
      a REALTIME take opens on whatever frame each clip happened to be showing.**
      Found while mapping the Stage for the playhead. The comment there is
      explicit that the move and the music are reset "so the two recorders
      agree" — and clips, the one source that was already there when that was
      written, are not. It bites only on the realtime path (the offline renderer
      seeks every clip per frame through `renderAtTime`, so the reset would be
      overwritten anyway), which is why nothing has caught it: every engine in
      this suite has WebCodecs. Same fix as the rung above, and they should ship
      together — one `restartTake()`, two callers.

- [x] **A STILL COLLAGE UNDER MUSIC HAS NO CLOCK → THE DERIVED CLOCK.** CLOSED,
      and the entry was right that the fix is "a cheaper clock for that one
      case, not a livelier loop" — and wrong about which clock. It is not the
      element's `currentTime`: the song laps inside the take on its own window,
      so its position is not the take's. The cheaper clock is the one that was
      already there. `outTime` is `(now - moveOriginMs) / 1000` — a PURE
      FUNCTION of an anchor — so the position at any instant can simply be
      COMPUTED when someone asks. `takePosition` now derives it, the tick's last
      branch holds `clockRunning` true while the soundtrack element is rolling
      (which is what keeps the anchor valid across the idle), and the Stage
      schedules NOTHING: zero rAFs, zero timers, and the Playhead's own pump —
      already a loop — reads a getter instead of a field.
      **THE TRAP THE DERIVATION CREATES IS THE REAL WORK.** `outTime` can now be
      minutes behind `takePosition`, so every place that stopped the clock by
      clearing the flag was silently freezing it at the last frame that happened
      to be DRAWN — under a still collage that frame is the first one, so the
      bar would spring back to 0 on every hide, scroll-away and `stop()`.
      `freezeClock()` is the one method that means "hold HERE"; `setTake`'s
      shorter-ruler wrap reads the derived position for the same reason; and the
      callers that mean "go to zero" or "go to t" still write `outTime`
      themselves and deliberately do not use it.
      **AND THE TWO EDGES, ON THE ELEMENT.** `pulseClock` wakes the loop for
      exactly ONE frame on the soundtrack's own `play` / `pause` / `ended`,
      because the tick already contains both halves — re-anchor at the parked
      position, and write the derived position back before the anchor is
      dropped. `disposeSoundtrack` pulses too: it nulls `this.track` before
      pausing, so the listener's identity guard (correctly) refuses that event.
      PROOF: photographs + music, move STILL, turn HOLD — 1.900s -> 4.900s over
      3 s of wall clock with the canvas hash IDENTICAL at both ends, which is
      the control that makes it a measurement (if anything were drawing, the
      clock would have run for the old reason). The same test against the one
      reverted line reads 0.000s -> 0.000s.

- [x] **THE RULER SHOWS THE TAKE AND NOT WHAT IS IN IT → THE STRIP.** CLOSED,
      and it closed a second thing the entry did not predict: the marks and the
      fade wedges were drawn on the TRACK's width while the playhead travels the
      THUMB's, so everything under the bar was out by up to half a thumb (13px
      of a 227px bar = 6% of the take). `--range-thumb` is now one token, used
      by both engines' thumbs and by the one inset under the bar, and the e2e
      measures the thumb's computed centre against the drawn mark: 408.0 against
      408.0. Original text: The bar knows the take's length and the fade's shape
      and nothing else. A real timeline draws each clip's extent on it, so you
      can see that the 3s clip laps three times inside a 10s take and that the
      trimmed one covers only its window. That is the same widget `drag-reorder`
      and `split/cut` want, and it is the natural next rung now that a ruler
      exists to draw them on.

- [ ] **THE STRIP DRAWS THE TAKE AND IS NOT A CONTROL.** It shows where the
      collage cuts and where each source laps, and you cannot touch any of it.
      The obvious next cut is that a lane is a HANDLE: tap one to open that
      clip's trim sheet (the sheet already exists and is already reached by a
      button elsewhere), and drag a seam to set the OUT point. That is
      `drag-reorder` and `split/cut` arriving as direct manipulation of the
      thing the ruler now draws, which is the argument this rung's parent made
      for building the picture first.
      **AND IT IS BLOCKED BY THE MOBILE LAW, WHICH IS WHY IT WAS NOT TAKEN THIS
      CYCLE.** A lane is 6 px on a 2 px pitch and the ship gate is a 44 px tap
      target. Eight source lanes at 44 px is 352 px of vertical space — the
      whole transport — and overlapping hit areas on an 8 px pitch make "which
      lane did you mean" unanswerable, which is worse than no control. The two
      designs that actually satisfy the law are (a) PROGRESSIVE DISCLOSURE: the
      strip stays a picture and tapping it opens the take's contents as a real
      44 px list with a Trim button per row — CapCut-shaped, and a new sheet to
      justify against ONE JOB PER TOOL; or (b) a control that is not per-lane at
      all, e.g. drag anywhere on the strip to set the OUT point of whatever the
      playhead is over. Measured this cycle, not guessed: the strip renders
      22 px tall with three rows at 320/360/390/430.

- [x] **THE MOVE HAS NO LANE, AND IT IS THE ONE THING EVERY COLLAGE HAS → THE
      DRIFT ROW.** CLOSED, and the entry's own prescription — "one more lane,
      the same `lapSegments` call on `MOVE_CYCLE_SEC / paceRate`" — was right
      about the arithmetic and wrong about the word LANE, which is the whole of
      `takeMap.ts` DECISION 5. A lane is a SOURCE: `TakeStrip` DECISION B reads
      a lane's identity off its POSITION ("the lanes are in the same order as
      the clip chips one row below"), so inserting a row with no chip under it
      would have shifted every clip lane off the chip that names it; and
      `MAX_LANES` is a budget for sources, so the one thing that is true of
      every collage would have been the row a ninth clip evicts. It is a
      SEPARATE FIELD (`TakeMap.drift`), drawn with the CUTS above the lanes,
      because both of those are facts about the whole wall.
      **The oracle is what makes it a measurement.** A drift seam is an instant
      the collage is back at REST, and `sampleMove` guarantees exactly that by
      REFERENCE (`NO_MOVE` at t=0 and at every cycle boundary) — so I13 asserts
      every seam against the compositor's own function, sampled through
      `paceTime` because that is the clock the Stage reads the move against.
      3,725 instants, identity not arithmetic. The interior probe is at a
      QUARTER of the cycle and never the half: `envelope` is exactly 0 at
      mid-cycle for a `stagger` fragment with `ph >= 0.5`, so a midpoint probe
      would have asserted that a legitimately-resting fragment is moving.
      Original text: The strip draws clips and music; the drift is periodic on
      a fixed 12 s cycle (scaled by the pace) and appears nowhere on it, so a
      collage of photographs with the turn on HOLD and no music draws no strip
      at all — correct today (`empty`), and plainly incomplete once you notice
      that the drift IS what is in that take.
- [ ] **THE DRIFT ROW SAYS WHEN, AND NEVER HOW MUCH.** Every moving mode shares
      `MOVE_CYCLE_SEC`, so PUSH and WANDER draw the identical row — the period
      is a property of the ROSTER, not of the pick. That is honest today (the
      row's job is "where does it come back to rest") and it stops being honest
      the moment per-fragment moves or a user-set amplitude exist, because then
      two collages with the same row would be visibly different takes. The row
      would need an amplitude, and the only amplitude the compositor knows is
      `sampleMove`'s peak — which is per fragment.

- [x] **THE CROP IS DECIDED FOR YOU AND THERE IS NO WAY TO SAY OTHERWISE ->
      THE REFRAME.** CLOSED. Five automatic rules and a detector, and no hand.
      See THE REFRAME in CURRENT STATE. It is also this app's FIRST free-form
      drag: every other continuous control is a native `<input type="range">`,
      which is why nothing else in the tree carries the defect below.
- [ ] **A DRAG THAT READS ITS OWN STATE BACK IS LOSSY, and this is the general
      lesson rather than a detail of the gesture.** The first version asked
      `calculateSmartCrop` for the CURRENT crop on every `pointermove` and
      applied the delta since the previous one. Pointer events fire faster than
      React re-renders and `setFrames` is asynchronous, so runs of consecutive
      moves read the SAME stale crop and each overwrote the last: a 600px drag
      arrived as whatever its final 8px event asked for. Fixed by sampling the
      crop ONCE at `pointerdown` and mapping the TOTAL displacement onto it —
      legal precisely because `sw`/`sh`/`dw`/`dh`/`twist` are invariant under a
      reframe, which is unit invariant I7. Any future free-form drag in this app
      inherits the same trap and the same fix.
- [x] **A REFRAME DOES NOT TRAVEL — not in a code, not in a project file, not in
      the SVG.** CLOSED for the FILE, still true for the code (a per-picture
      anchor is unbounded information and a code is a fixed-length recipe, which
      is the same structural reason pinned fragments and the swap are on that
      list). See THE FRAME TRAVELS in CURRENT STATE.
      **THE OPEN QUESTION THIS ENTRY LEFT WAS ANSWERED, AND THE ANSWER WAS NO —
      AND THE NAMED FIX WAS STILL WRONG.** The fear was a re-deal: `images` is a
      dependency of the layout effect and of the assignment effect. It does not
      re-deal — the deal reads `analysis.color` (`arrangeBag`'s `metricOf`) and
      the layout reads pixels and `images.length`, and a frame write moves none
      of them, swept over 440 deals as I6 of
      `tests/unit/reframe-travel.invariants.mjs`. What the entry did NOT name is
      the dependency that actually bites: `layoutItems` is a dependency of the
      DISARM effect (`setArmedCell(null) ... [layoutItems, maximized,
      shuffledIndices]`), so committing on `pointerup` took the puck away from
      under the finger that had just let go and a second drag on the same picture
      became impossible. reframe.spec T1 went from green to "fragment 2: no point
      in it takes a drag" on both engines. So the pool is the FILE FORMAT and the
      Map stays the LIVE STATE, and the merge happens at the writers.
      **THE GENERAL LESSON**, which is bigger than this feature: in this app
      `images` is not "the pictures", it is an INPUT TO THE DEAL, and anything
      written into it is a composition event whether or not it changes the
      composition. A fact about a photograph that the user set by hand belongs in
      the file, not in the pool the effects watch.
- [ ] **A FRAME STILL CANNOT TRAVEL IN A COMPOSITION CODE, and now it is the
      only one of the four that has a FILE.** Pinned fragments, the swap, the
      title and the reframe are the "in the app but not in the code" list; the
      reframe has just moved onto the "in the FILE" side of it, along with the
      title and (through the whole `AppState`) the pins and the swap. What is
      left is honest and small: the strip does not DISCLOSE that a code you are
      about to send carries none of them. One sentence under the code would close
      it, and the roster of what a code drops is now long enough to deserve one.
- [ ] **THE RESTORE BANNER IS THE FOURTH THING TO COVER A CONTROL, and the
      pattern is now a rule this app needs rather than a run of coincidences.**
      Fixed this cycle (`top-28 md:top-3`), but the shape has recurred often
      enough — the pending pill, the verbs puck, the full-bleed rail, now a
      fixed-position card over the header — that the honest next cut is a single
      overlay LAYER with a declared safe area, instead of four components each
      choosing a `top`/`bottom` and being measured after the fact.
- [ ] **A REFRAME AT THE EDGE MAKES THE MOVE CLAMP.** `sampleMove` sizes its pan
      from the room the ZOOM leaves and assumes the anchor is central enough for
      the crop clamp to have nothing to do — which was true of every anchor the
      app could produce before this. Drag a picture to the end of itself and the
      drift now has nowhere to go on that axis, so a moving collage has one
      fragment that stutters against its edge. Not measured this cycle; the
      honest fix is to narrow the reframe band by the move's own reach when a
      move is on, which couples two modules that are currently independent.
- [ ] **THE RAIL COVERS THE BOTTOM OF THE ARTWORK, so a drag cannot START
      there.** Found by the spec, not reasoned about: in full bleed the control
      pill owns roughly the bottom 90px of the screen and takes the pointerdown,
      so a fragment reaching the floor cannot be grabbed down there. Every
      editor has a toolbar and this is the ordinary cost of one — filed because
      it is the THIRD instance of "the affordance covers the gesture it
      documents" (the pending pill, the verbs puck, now the rail), which makes
      it a shape this app meets whenever it puts something over the canvas.
- [ ] **THE REFRAME IS FULL-BLEED ONLY**, because arming is. Outside full bleed
      a tap PINS, so a drag beginning as a tap would pin whatever it crossed;
      scoping the gesture to the ARMED fragment is what keeps every shipped
      gesture byte for byte and what lets `touch-action: none` be scoped to a
      state with nothing to scroll. The cost is discoverability: the correction
      is one tap further away than the complaint is.
- [ ] **A CONTINUOUS COMPOSITION CONTROL RESTARTS THE TAKE.** `turnScene` is a
      dependency of the Stage's scene effect and `setScene` resets
      `moveOriginMs`, so anything that re-derives `orderedAssets` per event —
      the gutter slider, the entropy slider, and now a reframe drag — restarts
      the clock under the user's finger. Pre-existing and shipped, but a drag on
      the ARTWORK is the first one where you are looking straight at it. The fix
      is a re-pointable scene (`stage.setAssets`) rather than a rebuild, which
      is the same shape as `setAudition`'s retarget.

- [ ] **A DENSE LANE IS A HATCH AND SAYS NOTHING ABOUT HOW DENSE.** Past 48
      seams the lane draws one hatched bar; the exact count rides in the `title`
      and the `sr-only` sentence and nowhere a thumb can reach. Fine while it
      only happens to a 0.3 s window, worth revisiting the moment a lane is a
      control.

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
7. **COORDINATE AFTER PUBLICATION** — send one factual release receipt to the existing fleet channel so Codex and Claude read the same shipped state at their next bump. Include commit, deployment, live evidence, limits, next owner and this book. Deduplicate by release thread; retain the read-back message ID. Posting is not peer acknowledgement. C3712 uses `persona500-collage-C3712-release`.

## QC GATES (fab-lab watertight — non-negotiable)
`tsc --noEmit` clean · a unit sweep for any pure algorithm · e2e on :5199 for dev
and `COLLAGE_BASE_URL`=production for the live proof · commit by pathspec (the
deploy artifact IS the whole site; staging order matters) · an adversarial
multi-agent audit for non-trivial changes.

## SCARS (carried from the 2026-08 build — add to this)

### 2026-09-05 (C3712) — OPTIONAL PANELS MUST SHARE ONE SPACE BUDGET

Making the old controls collapsible was insufficient while playback Details could open beside another editor and status toasts covered the scrubber. App and VideoStage now coordinate one disclosure; notices occupy their own row. The portal host and Stage remain mounted through task/focus changes. Tests park the playhead, retain the actual canvas and decoder, open competing panels and inspect controls against artwork bounds. Stop stays visible while recording, including in expanded preview.

### 2026-09-05 (C3712) — FOCUS RETURNS AFTER THE LAYOUT EXISTS

On a 360×448 screen the taskbar hides while editing. Focusing its trigger in the close event did nothing because CSS still hid the target until React committed the next view. A layout effect restores focus after the change and moves focus into a short-screen inspector on open. Returning from expanded preview chooses the visible header control or the inspector's Done button. Escape closes the innermost disclosure without also leaving expanded playback. Desktop and WebKit cases exercise opening, Done, focused inputs, F, Escape and the return path.

### 2026-09-05 (C3712) — A THUMBNAIL IS NOT THE LOADED STAGE

The new start tile has a canvas, so a generic first-canvas readiness check can pass before import. New and migrated gates identify the actual artwork container. A static title can render through the still path, so bounds tests measure the shared artwork wrapper rather than requiring a canvas. Pixel-repeat checks wait for the four-second inline status to retire and assert the same backing dimensions; comparing two preview raster sizes is not a determinism test. Focus geometry is checked against the maximum complete fit inside the measured band, with padding subtracted, rather than an arbitrary fraction of the entire screen.

### 2026-09-05 (C3711) — A RECIPE REVISION NEEDS CURRENT PIXELS

Recovery treats asset IDs as immutable. Reusing an ID after changing its recipe would save new metadata beside an old PNG. Apply now mints a new ID, atomically replaces the source slot and remaps pins, crop and history references. Archive, SVG and recovery preflight native recipes before adoption. Actual IndexedDB inspection and reopening compare the revised recipe and exact PNG bytes.

### 2026-09-05 (C3711) — MOTION HAS MORE THAN ONE GATE

Adding native animation to App and Stage was not enough: the dock's takeability test still recognized only video, music and captions. The dock now admits native animation, drift and turning, and the real encoded-video test requires Record to be enabled. Export supports the native loop duration and clears that extra duration when the pool becomes mixed. Source switching also retires the previous slider coalescing key, so the next edit always has an Undo entry.

### 2026-09-05 (C3711) — CANVAS STATE AND READBACK ARE PART OF THE PROOF

WebKit did not restore a filter property through save/restore in the tested context; the shared renderer now explicitly preserves that property. Repeated pixel readbacks can switch Chromium's raster backend. Repeat-seek tests warm that path before measurement; direct renderer and Stage seams remain exact. The scaled preview comparison allows at most two color levels on fewer than 150 of 144000 channels, after observed GPU readback differences were measured at 26 channels. Video tests await the presented frame after WebKit seek events and inspect actual decoded frames; a separate decoder scans the entire movie. Sliders carry the actual percentage into the shared CSS fill contract instead of displaying its default 50 percent.

### 2026-09-05 (C3710) — A LOADED INSTRUMENT MAY NEVER START DRAWING

Bifurcata starts a world when it approaches the visible viewport. In the nested
player at a 720px desktop height, the first grove sat below the visible frame
and no canvas appeared. The same file at 900px drew correctly, so source loading
and a single viewport were insufficient evidence. Show artwork scrolls the
selected canvas or first band into view. The actual button now leads through
Bifurcata rendering, PNG capture, source intake and a saved archive on desktop,
Android-shaped Chrome and iPhone-shaped Safari. Public Bifurcata is not embedded
or rebundled; its separate native PNG export remains an available handoff.

### 2026-09-05 (C3710) — INERT DOES NOT CANCEL SAFARI'S EDIT HISTORY

Stopping key propagation inside a native dialog prevented app shortcuts but
Safari's default undo still edited a textarea behind it. Both the lyric guide
and Art Room host now cancel native editor chords while preserving copy/select
all. Explicit close focus returns to each trigger. Tests retain actual unsaved
cue/lyric values, exercise both engines, and distinguish browser-chrome Tab focus
from focus escaping into the app. Only mounting Art Room when open also keeps
the existing upload input ordering intact.

### 2026-09-05 (C3710) — RETIRE THE PIXELS AFTER THE LAST AWAIT

An owned port and generation check at capture receipt are not enough: a user can
close the room during the parent's image decode. The shared upload path now
checks the capture generation after decoding, revokes the discarded original
and thumbnail URLs, and drains the intake counter before returning. A delayed
real browser decode proves that canceled pixels never land. PNG dimensions and
byte limits are checked before decode; actual decoded dimensions must agree.
The HTML policy and bridge precede every imported byte, without parsing the
instrument in the host document. This is an isolated player for owned/trusted
HTML, not a claim of universal containment of arbitrary script or self-navigation.

### 2026-09-05 (C3709) — A PLAUSIBLE SAVE WAS NOT THE EDIT

The earlier book claimed pins travelled in files, but no writer serialized the
live lock Map. Project, SVG and crash recovery now share one state builder and
canonical lock normalization. The archive writer also swallowed failed original
reads and downloaded a broken archive. Required originals now fail the whole
save visibly; an optional thumbnail may fall back to its original. The tests
force a missing source, require no download, retry successfully, and compare
saved/restored pins and exported geometry. They inspect actual archives and
IndexedDB rows instead of calling the writer and treating its output as proof.

### 2026-09-05 (C3709) — A NEGATIVE CLOCK ORIGIN IS VALID

Seeking later than page uptime makes an output-clock origin negative. The old
`-1`/`<0` sentinel treated that legitimate anchor as unset and restarted playback
at zero. Stage now uses NaN/Number.isFinite for the unset state. The direct Stage
browser check proves playback resumes from a late seek and a caption-only still
composition keeps advancing. Cue edits use a dedicated plan setter so they do
not reset the media scene or playhead. Caption timing uses output time directly,
not the visual motion pace, and the export test decodes cue/gap pixels and audio.

### 2026-09-05 (C3709) — VISIBLE IS NOT BIG ENOUGH TO EDIT

The iPhone12 browser profile has a 390x664 usable viewport. A lyrics details panel
capped alone at 34vh still left only 70px of artwork after transport, tabs and the
stage rail. The whole lyrics dock now shares a bounded flex layout, reserving
space for art and letting the editor scroll. The original >80px artwork test was
kept: 390x664 now has 134px. Narrow-width gates also measure 44px targets; WebKit
native selects needed explicit height/appearance rather than only min-height.
Full-bleed visual inspection also caught bottom lyrics under the floating rail.
The artwork band now reserves the measured rail height (including wrapped rows
and safe-area padding) for bottom captions and static titles; export geometry
is unchanged. The starter's asynchronous encoding/import is guarded against simultaneous
project replacement, source intake and save, so it cannot overwrite real work.

### 2026-09-03 (C3704) — THE FIX THE LADDER NAMED WAS THE ONE THAT BROKE THE GESTURE

**What I did.** The ladder said: commit the frame into the pool on `pointerup`,
and it named the risk itself — `images` is a dependency of the layout effect, so
"mutating the pool per drag frame would RE-DEAL THE WHOLE WALL". I built exactly
that, proved the re-deal fear was unfounded (I6: 440 deals, `arrangeBag` places
identically), and shipped it into the spec.

**What actually happened.** reframe.spec T1 — which had been green for a week —
failed on both engines with `fragment 2: no point in it takes a drag`. The commit
sets `images`, the layout effect re-runs and sets `layoutItems`, and
`layoutItems` is a dependency of `useEffect(() => { setArmedCell(null); ... })`.
So letting go of the picture DISARMED the fragment. Not a re-deal, not a wrong
picture — the puck vanished from under the finger, and a second drag on the same
photograph was impossible without re-tapping it.

**The lesson, and it generalises past this feature.** The entry was right that
`images` is dangerous and wrong about WHY, and being right about the risk while
wrong about the mechanism is worse than not having named it: I proved the named
risk absent and took that as clearance. `images` in this app is an INPUT TO THE
DEAL, and the deal's outputs are dependencies of things that have nothing to do
with dealing. A fact about a photograph that a person set by hand belongs in the
FILE FORMAT, not in the array the effects watch — so `poolWithFrames` merges at
the writers and the live app never sees it.

**And the mutant that proved the point was wrong twice.** The first "before"
mutant removed the commit and LEFT the Map delete, which reverted the whole
gesture at pointerup and failed the drag rather than the claim. A mutation that
breaks something OTHER than the thing under test is not evidence about the thing
under test; the honest before-state removed both, and then T4 failed on exactly
the sentence it exists to assert (no `"frame":{"x"` anywhere in the file) and T5
on `found = -1`.

### 2026-09-03 (C3704) — THE OFFER TO COME BACK COVERED THE DOOR OUT

The restore banner is `fixed top-3 left-1/2 -translate-x-1/2 w-[min(28rem,94vw)]`.
On a 390px phone that is x 12..381, y 12..78; the header's OPEN button is at
x 294..378, y 8..52. The card covered it completely, so a centre-tap on Open hit
the card and no file chooser ever opened — the offer to bring back the last
session physically blocked the one control that opens a DIFFERENT one. At 320 and
360 the header wraps to y 61..105 and the same card clipped its top third. On a
1280px desktop the card is 448px centred and the button is at the far right, so
it never touched it: the defect existed only where the app is actually used.

Found because reframe.spec T4 could not reach Open on Mobile Chrome and passed on
chromium. **A Playwright "waiting for event filechooser" timeout is what an
element covering a button looks like from the test side** — it reads as flake and
it is a product bug, so T4/T5 now assert `document.elementFromPoint` at the
centre of Open resolves INSIDE Open, which fails with the name of whatever is on
top instead of with a timeout.

FOURTH instance of "the affordance covers the gesture it documents" — the pending
pill, the verbs puck, the full-bleed rail, now this. Filed as a rung: four
components each choosing their own `top` is not a coincidence any more.

### 2026-09-03 (C3704) — A SEARCH LOOP THAT NEVER SEARCHED

T5's first draft hunted for the reopened correction by arming every fragment in
turn: `for (i…) { await armCell(page, i); if (recentre) found = i; }`. `armCell`
returns as soon as ANY puck is up — so after the first iteration it never clicked
again, and the loop asserted one cell ten times. It went green on chromium by
luck (the corrected picture was in cell 0) and red on a phone, which is the
signature of a vacuous test rather than a real one. Replaced with the claim T4
had already earned: the reopened project re-exports byte for byte, so the picture
is in the slot it was corrected in and there is nothing to hunt for.

### 2026-08-29 (C3680) — THE DRAG THAT READ ITS OWN STATE BACK, AND THE TEST THAT COULD NOT SEE IT
Two bugs, one root, and the test found both because it measured PIXELS rather
than asserting the handler ran.

**THE APP BUG.** `moveReframe` computed the current crop from `orderedAssets` on
every `pointermove` and applied the delta since the previous event. Pointer
events fire faster than React commits and `setFrames` is asynchronous, so a run
of consecutive moves all read the SAME crop and each overwrote the last: the
drag delivered only its final event. `reframe.spec` T1 dragged the length of a
photograph twice, both ways, and landed where it started. Fixed by sampling the
crop ONCE at `pointerdown` and mapping the TOTAL displacement onto it — legal
because a reframe leaves `sw`/`sh`/`dw`/`dh`/`twist` untouched, which is
invariant I7 rather than an assumption.

**THE INSTRUMENT BUG, and it hid the app bug for two runs.** The first tiles
were BANDED (three flat colours). "Drag until the colour stops changing" is the
only pass count that holds on a Pixel as well as on a desktop — and with bands
the colour is constant while the crop moves INSIDE one, so the helper settled in
the middle of a band and called it the end of the photograph. Gradients made
every pixel of travel measurable and the settle became the clamp.

**AND A THIRD, WHICH IS A REAL OVERLAP AND NOT A TEST ARTEFACT.** T1 failed on
chromium and WebKit but passed on both phones, which is backwards for a touch
gesture. The drag was starting at the bottom of a fragment that reached the
floor of the screen — where the full-bleed RAIL owns the pointer and its pill
takes the `pointerdown`. Third instance of "the affordance covers the gesture it
documents" after the pending pill and the verbs puck; the puck and the pill both
got the one-line class fix (`pointer-events-none` on the container, `auto` on the
buttons, swap.spec 24/24 unchanged), the rail is filed on the ladder because a
toolbar is allowed to take taps.

**AND THE SPEC'S OWN FIX FOR IT WAS STILL GUESSING.** Clamping the start point
above the rail was not enough: the seed is random per boot, so the partition
differs every run, and a NARROW fragment has no point at its own half-width that
clears a 98px puck arm — so some runs still grabbed a button. `dragPicture` now
TRIES a ranked list of points (furthest from the centroid first) and advances to
the next when a pass moved nothing on a picture that has not moved at all, which
is also the honest model of the gesture: a user whose thumb lands on a button
tries somewhere else. And the IDENTIFICATION stopped comparing to endpoint
colours — a weak discriminator, because a crop parked at the top of a photograph
is centred half a crop HEIGHT into it — in favour of projecting each reading onto
its source's own gradient: the perpendicular residual says WHICH photograph (~1
for the right one, >50 for any other) and the parameter says WHERE ON IT, so
both questions get a tight bar instead of one loose one. Green 12/12 twice in a
row against the DEPLOYED page with all four engines in parallel, which is the
run that had been flaking.

**AND A FOURTH: EVERY READ WAS RACING THE PREVIEW.** The still preview is
`renderCanvas` -> `toBlob` -> an object URL an `<img>` must load, so a colour read
taken straight after a gesture is racing it. Serial runs hid it completely;
under three parallel workers a drag looked like it did nothing twice in a row,
which the settle test read as the end of the photograph. Every measurement in
the spec now goes through `stableColour`, which polls until two reads 220ms
apart agree. **The lesson is the general one: a spec that reads an async render
must settle it, and a serial run is not evidence that it does.**


### 2026-08-26 (C3675) — `--strictPort` PROTECTED THE WRONG RUN, AND THE SUITE WOULD HAVE GONE GREEN AGAINST A STRANGER

`playwright.config.ts` already carried a long, correct comment: :5173 belongs to
Persona 500, `reuseExistingServer` will happily attach to whatever is listening,
so the port was moved to **:5199** and `--strictPort` was added. The hole was
declared closed. It was not.

`--strictPort` only protects the run that starts the server **first**. When
something else is already on the port, Playwright does not start vite at all —
it attaches. Measured this cycle: `/Volumes/dual/persona500` had vite on
**:5199 --host**, and a run of the new swap spec spent four minutes per test
waiting for a file input that does not exist. `curl` on the port answered
`<title>Persona 500 | 1,022 AI Mentors & 1,070+ Tools</title>`.

**A TIMEOUT IS THE LUCKY VERSION.** The dangerous version is a spec whose
assertions are trivially true on a page that has none of this app's furniture —
every `toHaveCount(0)`, every `not.toBeVisible()` — which is a whole suite
reporting green about software it never loaded. The same class as
SCAR-VERIFICATION-THEATRE, arriving through the door that decides WHICH APP the
theatre is about.

**THE FIX IS THE CLASS FIX, NOT A PER-SPEC GUARD.** `tests/globalSetup.ts` does
one fetch before any browser starts and throws with the name of whatever
answered; it is wired into **all 34** playwright configs, so it covers every
spec at once instead of asking 39 files to remember. It also catches a
`COLLAGE_BASE_URL` pointed at a Pages URL that 404s. Proven by firing it: the
:5199 run now fails in seconds with `E2E TARGET IS NOT COLLAGE STUDIO … got:
"Persona 500 | 1,022 AI Mentors & 1,070+ Tools"`.

**AND THE PORT IS NOT THE LESSON.** Moving to :5202 would have reproduced this
in a month. Asserting the identity of the thing on the other end of the URL is
the lesson.

### 2026-08-26 (C3675) — AN UNDO THAT VISIBLY DID NOTHING, AND THE CLAIM WAS ALREADY WRITTEN DOWN

The swap's first draft pushed a history step and the code comment said "IT IS
RECOVERABLE through the rail's Undo, and that is not luck: a step records the
composition code AND the pins, and the pins are where a swap lives." Every
clause of that is true and the conclusion was false.

`restoreSnapshot` calls `applyCompositionCode`, which writes `setCount`,
`setSeed`, `setArrangement`, `setShuffleTrigger` — and a swap changes NONE of
those. Identical values, so React bails out of the re-render, so the assignment
effect never runs. The pins reverted; the PICTURES stayed traded. Measured
before the fix, by writing the assertion first: **285 RGB** away from the
picture Undo claimed to restore (swap.spec T6).

**THE CLASS, and it is bigger than Undo.** The pin table is half of what decides
the deal and is deliberately NOT a dependency of the assignment effect, because
toggling a pin must not disturb the deal on screen. Any code path that changes
pins and expects the picture to follow has this bug waiting for it.

The fix is one nonce (`assignNonce`) bumped by `restoreSnapshot` and added to
the effect's deps — NOT a special case for swaps, because it is safe to fire on
every restore: the bag is seed-deterministic, so re-deriving with the same
inputs reproduces the same deal exactly, and re-deriving with different pins
reproduces the deal those pins imply, which is the thing being restored.
undo.spec 21/21 unchanged, and source-count 7/7, dice-count 6/6, one-layout 4/4,
roll-code 20/20, frame-hold 5/5 confirm the extra dep re-deals nothing.

**THE LESSON IS THE ORDER.** The claim was in the commit, in the code and in
the book before it was measured. Writing T6 as a FAILING test first is what
turned a confident sentence into a defect.

### 2026-08-26 (C3675) — THE AFFORDANCE COVERED THE GESTURE IT DOCUMENTED

The swap's pending pill is positioned on the centroid of the fragment it parked,
and the code comment claimed "tapping the parked fragment again is CANCEL — the
way out of a mis-tap". On WebKit and Mobile Chrome that tap lands on the PILL.
Chromium desktop passed, because the fragment happened to be large enough for
the element's centre to clear the pill — so a single-engine run would have
shipped a documented gesture that does not exist on a phone.

Not fixed by moving the pill (it belongs on the thing it is about) but by
un-over-claiming: the guaranteed outs are the pill's own 44 px X and Escape,
both now asserted, and the fragment tap is the convenience for a fragment with
an edge showing. The TEST now finds a genuinely uncovered point and falls back
to the X when there is none — so "the mode has a reachable exit" is measured,
not assumed. **The armed puck has the same geometry and will meet this again.**


### 2026-08-23 (C3647) — A THRESHOLD MEASURED OFF A RANDOM DEAL
`desk.spec` T2 asserted "the cool end must be cooler than the ungraded frame by
5" and passed six times, then failed on the seventh: the base R-B of this
fixture's own deal has been measured from **-16.8 to +9.7** across runs, because
which of the ten tiles land where is the point of the app. The assertion was
arithmetic about the DEAL wearing a claim about the GRADE.

The mechanism is worth keeping, because it is not a test bug, it is a fact about
colour: every other claim in that test is MULTIPLICATIVE on whatever the deal
contains (saturate scales the chroma that is there, contrast scales the spread
that is there), so a base offset cannot flip it. **A TONE is not.** A sepia
washes the picture's own hues out before the rotation turns what is left, so
`cool` lands near a fixed R-B whatever it started from — and on a deal that
dealt itself blue, the cool end is LESS blue than the ungraded frame.

The fix is to compare the two ENDS of the axis (invariant to the deal) plus the
one absolute each direction can actually claim: warm is a SHIFT (a tone can only
raise R-B), cool is an ABSOLUTE (its saturate runs first, so 9% of the picture's
own cast survives to argue with the tone). And what is deliberately NOT asserted
is written down beside them — at the roster's 30% tone, `warm`'s OUTPUT is not
positive on a blue deal (measured -2.6 against a base of -16.8); the roster's
warm is a lean, not a wash.

**BACKPORT: `look.spec` T2 carried the identical pair and had been flaking on it
since it was written.** Swept every e2e for the shape (`grep 'base[A-Za-z]* [-+]
[0-9]'`); `twist.spec`'s base-relative bar is the same SHAPE and not the same
class — darkness under twist is monotone in the deal — and is left alone.

### 2026-08-23 (C3647) — A CONSTANT THAT SEVEN SWEEPS READ AS SOMETHING ELSE
`MINTED_GROUP_MAX` was documented as "THE LENGTH THIS BUILD MINTS", and five
sibling sweeps asserted their freshly-minted code against it. True for six
generations, because every one of them added a field EVERY roll carries. THE
DESK is the first OPTIONAL group, so "the newest generation" and "what this
build mints for this roll" became two different numbers and all five sweeps went
red at once with the same message.

The temptation is to relax the assertions to `MINTED_GROUP_LENGTHS.has(len)`.
That is a weaker claim about a real property and it would have hidden the next
generation's mistake. The fix is to name the second fact in the CODEC —
`MINTED_GROUP_PLAIN`, derived as the max minus the desk's own width — so the
sweeps keep asserting exactly what they meant and adding a ninth generation
still moves both together.

- **SCAR-C166-A-BUDGET-CONSTANT-THAT-READS-LIKE-A-HARDWARE-FACT.** The realtime
  pixel cap was `maxLiveClips × 1080p` — a guess dressed as a measurement — and
  on a phone it was 6.2 Mpx. A phone-shot 4K clip is 8.3 Mpx, so with ANY 4K
  clip in the set the first was admitted (the first is always let in) and every
  later clip refused — a 1080p one too, since 8.3 + 2.1 is also over — with the
  notice "these clips are too high-resolution to decode together". Two videos
  from the same phone the page was open on, and the app played one. This was
  the SECOND time the same constant pinned the budget to one (the first: a flat
  2,500,000 vs 1080p); re-denominating it in 1080p streams moved the cliff to 4K
  and called it fixed. The law: a cap that refuses work must either be
  denominated in the thing it rations WITH HEADROOM (DCI 4K, the largest frame
  a camera labels 4K — `2 × UHD` let two UHD clips through on the boundary and
  refused two 4096-wide ones with the wish's exact sentence), or be MEASURED on
  the device (`settleStall`); and its notice must name the user's lever — fewer
  clips, smaller clips, or "this device can't run them all" — never a rule
  wearing a hardware costume. Sweep I9 now pins the pair that failed.
- **SCAR-C167-A-PROBE-THAT-READS-ONE-CLIP-CANNOT-TELL-A-GESTURE-FROM-A-BUDGET.**
  `armPlayProbe` read its own clip's clock and flagged "Tap to start playback"
  on any stall — the wrong sentence for a decoder the OS starved, and a tap that
  replays everything makes that one worse. The verdict is COMPARATIVE (every
  live clip over the SAME window) and its vocabulary matters: a starved decoder
  is UN-PAUSED and presents no frames; a PAUSED non-advancer is permission,
  power or end-of-media (iOS Low Power on an incrementally admitted clip while
  the tapped ones keep rolling — the panel's lens found the sequence). The
  signal is PRESENTED FRAMES (requestVideoFrameCallback), not `currentTime`: a
  clock advances over a frozen picture when a decoder is reclaimed under it,
  and a short trim window wraps the clock back onto its baseline. Guards before
  a verdict may EVICT: seated at the baseline (readyState ≥ 3 or 3 s live), not
  ended, still wanted, visible + on-screen + not parked + not offline, two
  consecutive strikes, a plan that did not change under the probe (epoch), a
  cooldown after a settle, an episode bound on rounds, a floor of one decoder
  on the ceiling, and MEDIA_ERR_DECODE with siblings live is one retry as a
  stall before it is "broken". I12's Stage-vocabulary table pins each.
- **SCAR-C168-A-MOTION-FIXTURE-WHOSE-MOTION-CAN-MISS-THE-CROP.** The first cut
  of the concurrency e2e keyed each clip by hue and asserted its canvas region
  CHANGED over 400 ms — with a single white bar sweeping the frame. A fragment
  shows a CROP; when the bar was outside the crop for the whole window the clip
  read "frozen for the person" while its decoder ran (0 of 6 changed, one run
  in three). The fixtures are now white STRIPES at 50 % duty moving half a
  period per 400 ms, so ANY crop flips field↔white between two samples; 6/6
  consecutive runs green. The law: a pixel witness must move everywhere the
  composition can look, or it measures the layout's luck, not playback.
- **SCAR-C169-TWO-CYCLES-DIED-ON-ONE-CLAIM-WITH-NOTHING-COMMITTED.** C3633 claimed
  the concurrency wish, wrote `lib/admission.ts`, an 81k-check sweep, the e2e,
  six fixtures and three probes; C3634 refined the module and the sweep; neither
  committed a byte or wrote a book line, so the well showed `building` for 20 h
  and the third cycle re-derived the plan from a working tree. The law: a seam
  that holds on its own (a pure module + its sweep) is COMMITTED the moment it
  holds, before the wiring starts — a cycle that dies then leaves a foothold,
  not a puzzle — and the `--status building` sweep is read FIRST every cycle.
- **SCAR-C165-A-SPEC-THAT-ASSERTS-THE-GATE-BUT-NOT-THE-CLAIM.** The frame-hold
  rail change widened the wrap cap (4 targets below 390 → 5 below 430) and its
  F3b asserted everything the SHIP GATE demands — 44px law, viewport
  containment, no sideways scroll — and nothing the CHANGE claims: the 5-makers
  /3-navigators split rests on an exact-fit equality, so a silent regression to
  a 4/4 split (a gap tweak, a rounding tie) would have passed every assertion.
  The panel's mobile lens caught it pre-ship; F3b now asserts row membership by
  y-coordinate (hold beside the dice, navigators wrapped below 430, one row at
  430). Same lens found the wrap comment's one-row derivation 9px optimistic
  (counted 7 gaps, dropped the separator) — the number the NINTH button will
  re-derive from. The law: a geometry change carries a witness for its own
  geometry, not only for the standing gate — the gate proves you broke nothing,
  never that you built the thing; and a load-bearing derivation in a comment
  gets re-added, not trusted, when the roster it counts changes.
- **SCAR-C163-A-SWEEP-THAT-AVOIDS-THE-SIZES-PEOPLE-UPLOAD-PROVES-THE-WRONG-POOL.**
  The first Shuffle revival (e90d8a55) swept its re-deal at n=40 only, and the
  re-deal was the IDENTITY at n ≤ 6 for every seed — the jitter window's floor
  of 1 rank is an amplitude of ±0.5, which can never carry one rank past
  another. Its own test was green while the button stayed dead at the sizes a
  phone actually uploads, and the wish came back in exactly those words. The
  law: when a control's behaviour depends on n, the sweep runs at the n the
  USERS produce (2..13 for uploads), not the n that makes statistics easy.
  §3b-small and §3b-small-exhaustive (2000 consecutive triggers, sizes 2..16)
  now hold it; the old code dies on them with 41,632 assertion failures.
- **SCAR-C164-A-GREEN-BATTERY-CAN-HIDE-AN-UNCAUGHT-ASSERT.** The soundtrack
  sweep sat RED on HEAD since f1d25ab4 — the range-fade commit added `fadeSec`
  to the mixer row and left the sweep's pinned field list stale — while that
  cycle's log claimed 30/30 green. It stayed invisible because the failure was
  an uncaught `assert.deepStrictEqual`, which prints no per-check ✗ line: any
  detector that greps output patterns reads it as "no failures". The law:
  a sweep's verdict is its EXIT CODE, never its output shape — and "run all
  sweeps" belongs to every cycle's gate, not only to cycles that touched the
  module.
- **SCAR-C161-A-BOTTOM-PINNED-SHEET-LOSES-ITS-HEAD-NOT-ITS-FOOT.** The mobile
  law says nothing is clipped and the confirm button is reachable, so the first
  version of the range-fade e2e asserted exactly that: `Done` has a box, is 44px,
  and sits inside the viewport. It passed **with the height bound deliberately
  removed**. `TrimSheet`'s panel lives in a `fixed inset-0` host with
  `items-end`, so an over-tall sheet does not push its footer off the bottom —
  it pushes its HEADER off the top, at a negative `y` the page cannot scroll back
  to because the host is fixed. The assertion was aimed at the one end that
  cannot go missing. Fixed by asserting BOTH ends (`Close trim` and `Done`) after
  `scrollIntoViewIfNeeded`, and by adding a LANDSCAPE probe (568×320): at 430×932
  a fourth roster row fits with room to spare, so a portrait-only sweep cannot
  see the defect it exists to prevent. The mutant then died at
  `y=-166.6`. **General shape: when a container pins one edge, the overflow
  assertion belongs on the OTHER edge — and a viewport sweep that only varies
  WIDTH cannot see a height defect at all.**
- **SCAR-C162-A-PHASE-THAT-WRAPS-FOR-A-SOURCE-THAT-DOES-NOT.** `lapEdges` was
  extracted out of `audioSchedule`'s straddle branch so the fade and the lap
  schedule could not disagree about where a lap begins. The extracted line was
  `(at * r) % L` verbatim — correct in the branch it came from, which only runs
  when `p.loop`, and wrong the moment a second caller asked it about a
  NON-looping source, which holds at its OUT point instead of coming round. It
  would have put a fade-in in the middle of a clip parked at its end, for any
  `startAt > 0`. Latent today (nothing sets `startAt`), found by writing the
  invariant `phase === sourceTimeAt(p, at) - inSec` rather than by running
  anything. **General shape: extracting a formula out of a branch inherits the
  branch's precondition silently. Tie the extracted function to the older
  formula it must agree with, not to the caller it came from.**
- **SCAR-C160-A-CHANGE-DETECTOR-THAT-ENUMERATES-FIELDS-SWALLOWS-EVERY-FIELD-
  ADDED-AFTER-IT.** `Stage.emitStatus` skips the React push when a hand-built
  signature string is unchanged — the right idea (the loop calls it every frame),
  with a list of fields spelled out by hand. `level` was not in the list, so the
  Stage held the new value, the export rendered it, the room played it, and the
  chip row read back the OLD one: press a level, nothing moves. It fails
  SILENTLY, in ONE DIRECTION (write-through works, read-back is frozen), which is
  precisely the shape that reads as "the button is broken" rather than as "the
  status is stale". Caught by `level.spec.ts` L2 — an `aria-pressed` assertion,
  not a render check, because the render was fine.
  **AND IT HAD ALREADY EATEN A FIELD.** `moving` — THE DRIFT ROW's own gate,
  shipped ONE CYCLE EARLIER — was missing from the same list, so a status where
  only the drift changed could not reach the strip. Two for two: every field
  added to `StageStatus` since the signature was written had fallen through it.
  Both are in the list now, which is the cheap fix; the real one is a structural
  digest over the object, and it is its own rung.
  The general shape: **a manually-maintained mirror of a growing type is a defect
  with a delay fuse.** This project has three of them — this signature, the
  duplicated `SoundtrackSpec` shape in `VideoStage`'s props (also fixed this
  cycle, also one field behind), and `SoundtrackSource` vs `OfflineAudioSource`
  (which is the one that is DELIBERATE and has a sweep asserting the two agree —
  the difference being that it is checked).
- **SCAR-C160-THE-NOISE-FLOOR-IS-A-PROPERTY-OF-THE-FILE-NOT-OF-THE-HARNESS.**
  L3's first bound copied `soundtrack.spec` T2's "a muted tone must be under
  `control * 4`", and failed at 3.6x — on a take where the music was 732x down
  from unmuted and 567x below the clip it sat under. T2's bound is right THERE:
  its collage is photographs, so muting the only source means the mixer writes no
  audio track at all and the control is measured over digital silence. L3 keeps a
  440 Hz clip sounding, so the file is a real AAC encode and EVERY empty bin
  carries that encode's quantisation noise, the 5000 Hz control included. The
  yardstick moved and the tone did not. **A control bin is only a floor for the
  file it was measured in** — bound against the SOURCE the quiet one is supposed
  to be under, which is the same ratio-not-absolute rule the rest of the suite is
  built on, and which the limiter makes mandatory anyway.
- **SCAR-C159-A-MUTATION-HARNESS-THAT-RESTORES-FROM-GIT-DELETES-THE-WORK-IT-IS-
  TESTING.** The battery for the drift row applied one edit to `takeMap.ts`, ran
  the sweep, and restored with `git checkout -- src/lib/takeMap.ts`. That
  restores HEAD. The module was UNCOMMITTED — the mutation harness exists
  precisely to grade work that is not committed yet — so the first mutation
  reported KILL correctly and then wiped every edit in the file, and the
  remaining eight ran against a module with no drift in it and printed
  "anchor not found" eight times. The output does not look like a catastrophe;
  it looks like a harness with stale anchors, which is exactly how it nearly
  went unnoticed. Restore from a copy read into memory BEFORE the first
  mutation. The general shape, and it is the third time this project has met a
  version of it: **a tool that reverts must be told what to revert TO, and
  `HEAD` is not the same thing as "how I found it".** Nothing else was lost —
  the other five files were untouched, `tsc` caught nothing because the file
  merely reverted to a coherent older state, and the sweep passing again after
  re-applying is what confirmed the recovery was complete rather than close.
- **SCAR-C157-THE-CAP-WAS-WRITTEN-ON-THE-KNOB-AND-THE-PICTURE-NEVER-READ-IT.**
  A wish said the dice deals over a hundred fragments from twelve photographs.
  It does, and the wiring defect was one line: `rollDice({ hasVideo })` — the
  roll had no idea how big the pool was, so a recipe sampled its absolute band
  and twelve photographs became two hundred repeats. The obvious fix — cap the
  rolled `count` — is a cap on a number nobody is looking at, and the panel made
  that its decisive objection before a line shipped. **`count` is a REQUEST.**
  App.tsx says so in its own words ("the count is documented as a target, not a
  guarantee") and the generators miss it in both directions: measured on the real
  module across 7 aspects x 4 seeds x 3 entropies, a Flower of Life asked for 4
  returns 39 cells and cannot go below that at ANY request; truchet asked for 12
  returns 39; kaleidoscope overshoots 2.2x in the low band; apollonian and
  penrose UNDER-deliver by half. So capping the request at 36 still put 87 cells
  on the canvas. **The general shape: a ceiling imposed on an input is a promise
  about an output, and the two are only the same number when nothing in between
  is allowed to disagree.** Fixed with two measured facts per generator —
  `deliveredFloor` (the fewest cells it can produce at any request) and
  `overshoot` (delivered/requested, p75 over the low band) — used to aim the
  request BELOW the budget and to refuse a figure that physically cannot be drawn
  under it. **AND THE SECOND HALF OF THE SCAR IS THE DATA ITSELF:** two of those
  numbers are measurements living in a source file, which is the same thing as a
  comment, and this file already carries "a docstring is not a test". So the
  sweep RE-MEASURES both against the real generators on every run and fails on
  drift — which caught it immediately when the shipped p75 was compared against a
  re-measured median, a units mismatch that would otherwise have shipped as a
  gate that could never fire. **`countRange[0]` was the original lie:** written
  as "cells this construction looks best at", read ever since as "cells it can
  do", and false for seven of twenty-three.
- **SCAR-C157b-THE-FLOOR-ROUNDED-UP-THROUGH-THE-CEILING.** The band the pool
  produces is fractional (a budget divided by a density and an overshoot), and
  the integer clamp read `hi = max(lo, floor(hi))` — so a band of [7.5, 7.5]
  rounded the low end UP to 8 and at density 2 put 16 fragments on screen against
  a budget of 15. Caught by the sweep in its first run, four lines after the
  invariant that describes it. A floor is a preference and a ceiling is a
  promise: when a fractional band cannot hold both, the promise survives.
- **SCAR-C156b-THREE PLACES ANSWERED "IS THE WALL TURNING" AND THE NEW FEATURE
  ASKED THE WRONG ONE.** `Stage.setScene` builds the turn RING out of the
  fragments that are NOT holding a live clip and switches the feature off below
  two of them; App's own `turning` is `isTurning(turn) && images.length > 1`,
  which counts the POOL. Those are different sets, and the difference is total
  for the app's headline case: every frame extracted from a video carries a
  `clipId` and binds to that clip, so a collage made of videos has an EMPTY ring
  and **never cuts — in the preview and in the exported file — however loudly
  MARCH is selected**. THE STRIP drew App's answer, so it put two white ticks
  under a wall that never re-deals. In mixed pools it is worse than wrong, it is
  SHUFFLE-DEPENDENT: 1 video + 2 photos over 3 fragments actually cuts in 195 of
  400 deals while the strip drew the same two marks in all 400, so a remix
  flipped the truth and not the picture. **The general shape: a feature that
  DRAWS another feature inherits every predicate that other feature uses, and a
  predicate that exists in three places has three values.** Fixed by publishing
  the Stage's own answer (`StageStatus.turning`, in the `emitStatus` dedupe
  signature) and gating the strip on it — never by re-deriving the ring in the
  component, which is the second-place-that-decides defect `takeMap.ts` DECISION
  1 exists to refuse. **AND NO TEST IN THE TREE COULD HAVE SEEN IT**: the unit
  sweep interrogates `turnAt` given a mode id, which is the right oracle for
  WHERE the cuts are and structurally blind to the Stage having switched the
  feature off; the e2e suite closed the same door from the other side by never
  once putting a clip and a turn mode in the same scene. `take-strip.spec.ts` S6
  is that scene, and it pins the ground truth rather than the behaviour — two
  videos, MARCH, parked past the would-be cut AND its dissolve, measured against
  the same instant with the turn off: 0.0% of the frame moved, worst 0/255.
- **SCAR-C156c-THE LABEL ROUNDED AWAY THE ONE FACT ITS OWN DOCSTRING SAID IT
  EXISTED TO STATE.** `laneLabel`'s comment reads "`x2.5` rather than `x3`: the
  fractional part IS the information — it says the take ends mid-pass", and the
  code under it was `Math.round(times * 10) / 10`, which snaps anything within
  0.05 of an integer onto it. A 10.4 s source in a 10 s take printed `x1` — it
  plays through once — directly beside a bar drawn as a single DIMMED partial
  pass. On a 10 s take every period from 9.524 to 10.000 s read `x1`, and
  4.878–5.000 s read `x2` while three segments were drawn. The sweep's three
  cases (5/10, 3/10, 30/10) all sit outside those bands, which is exactly why
  they held. **The general shape: a docstring is not a test, and a value derived
  a SECOND way from the same inputs will disagree with the picture at the
  boundaries nobody sampled.** Fixed by reading the claim off the SEGMENTS the
  component draws (`segments.at(-1).whole`) rather than off a re-rounding, so
  the label and the bar agree by construction; I10 now sweeps 3,457 periods
  continuously instead of three round ones.
- **SCAR-C156-EVERYTHING DRAWN UNDER A SLIDER WAS DRAWN ON THE WRONG AXIS.**
  A range thumb's CENTRE travels from `thumb/2` to `width - thumb/2`, not from 0
  to `width` — so an overlay positioned at `left: f%` of the element is not
  under the thumb at value `f`. The fade wedges shipped with that error two
  cycles ago and nobody could see it, because a wedge is a soft triangle and
  nothing was aligned to it. THE STRIP made it fatal: a cut mark's entire claim
  is "the playhead crosses this when the collage cuts", and 13 px of a 227 px
  bar is 6% of the take — most of a second on a 15 s one. **The general shape: a
  control and a drawing of that control share an axis only if they were built
  from the same number.** `--range-thumb` is now that number, in tokens.css,
  used by both engines' thumbs and by the one inset that wraps everything drawn
  beneath the bar; the two engines had been 26 px and 22 px for no reason, which
  would have made the ruler right on one of them at best. Asserted at the
  artifact by computing the thumb's centre the way the engine lays it out and
  comparing it to the mark's own `getBoundingClientRect` — 408.0 against 408.0,
  with the thumb width READ FROM THE PAGE so a test cannot pass against a build
  that changed it.
  **BACKPORT RIDER FIRED — the class was swept everywhere it could live, and it
  lives in exactly two more places, both benign for a stated reason.** No trade
  toolkit page has a slider at all (`grep -rl 'type="range"' av/ electrical/
  framing/ gc/ hvac/ low-voltage/ plumbing/ roofing/ shared/` is empty), so the
  class cannot exist there. Inside collage there are seven ranges; the only ones
  with anything drawn beneath them are the playhead's, both fixed by the one
  inset. The other five use `--fill`, a gradient stop INSIDE the track, whose
  end disagrees with the thumb's centre by the same up-to-half-a-thumb — and is
  invisible by construction, because that error is bounded by `thumb/2` and the
  thumb is a 26 px disc centred on the very point it is measured against, so the
  gradient's end is always underneath it. Not fixed, and not an oversight: the
  cheap fix (a unitless `--fill` and a `calc` against `--range-thumb`) would
  touch five call sites to move a pixel nobody can see.
- **SCAR-C150-THE-PREVIEW-WAS-TIME-STRETCHING-WHERE-THE-EXPORT-RESAMPLES.**
  `HTMLMediaElement.preservesPitch` defaults to **true**, so a live `<video>` at
  2× plays faster at the SAME PITCH. The offline mixer has no such switch —
  `AudioBufferSourceNode.playbackRate` is a resampling and always carries the
  pitch with it — so the preview and the file it claims to be previewing
  disagreed about what a rate SOUNDS like. It was latent rather than harmless:
  the only thing that ever set a rate was video-length sync, whose DEFAULT mode
  ('loop') leaves every rate at 1, so the divergence sat behind a control most
  people never touch. A per-clip SPEED puts it one tap away in the default mode.
  Fixed by correcting the PREVIEW (`preservesPitch = false`, plus the WebKit
  alias, in the one `applyRate` all three assignment sites now go through) —
  not by teaching the offline mixer to time-stretch. **The general shape: when a
  preview and an export disagree, the export is the artifact and the preview is
  the defect — a preview that flatters the file is worse than one that is
  merely ugly.** Asserted at the artifact on the real element (`rate=0.5`,
  `preservesPitch=false`), because a flag nobody reads back is a comment.
- **SCAR-C150-A UNIT SWEEP THAT `transform`s ONE FILE DIES THE DAY ITS MODULE
  GROWS AN IMPORT.** `videoSync.ts` gained `import { safeSpeed } from './speed'`
  and TWO sweeps went red instantly with `ERR_MODULE_NOT_FOUND … /speed` —
  `esbuild.transform` compiles a single file and leaves its relative imports
  pointing at paths that do not exist in the temp directory. The failure reads
  like a broken test, not like a missing flag, and it lands on sweeps that were
  green for weeks and had nothing to do with the change. The majority of this
  directory already used `esbuild.build({ bundle: true })`; six files were
  stragglers. **The general shape: a harness that only works while the module
  under test has no dependencies is a harness with an undeclared precondition.**
  BACKPORT RIDER FIRED: all six converted in the same cycle (clipWindow,
  videoSync, fill, rasterBudget, session, exportLimits — the last builds once
  and copies the bundled text N times, because it deliberately re-imports fresh
  module instances), and the whole tree re-run: 24/24 sweeps green.
- **SCAR-C147-THE-DEV-SERVER-WAS-FOUR-DAYS-OLD AND SERVING CODE THAT NO LONGER
  EXISTED.** An e2e run failed on an assertion the module provably satisfied —
  the same fixture through the same functions in node returned `first 4.004`
  while the browser was acting on `first 4.496`. The cause was not the code:
  `lsof -ti:5199` named a vite dev server **started on Aug 8, four days
  earlier**, holding the port this project's playwright config attaches to. A
  file CREATED during the session was transformed fresh on its first request and
  then EDITED five times, and the watcher — on `/Volumes/dual`, an external
  volume where fs events are not reliable — missed every edit after the first.
  So the run was green-or-red about a version of `beat.ts` that had been
  overwritten an hour before. **The general shape: a long-lived dev server is a
  CACHE, and a cache on a volume whose change notifications are unreliable is a
  cache with no invalidation.** The sibling scar to "a run silently reused
  another project's server on :5173" — same failure (measuring something other
  than what you wrote), different mechanism. The check is one command and it
  belongs before believing any surprising e2e result:
  `lsof -ti:5199 | xargs ps -o lstart,command` — if the start time predates the
  edit you are testing, kill it and let playwright start its own.
- **SCAR-C147-THE-SWEEP-COULD-NOT-SEE-EITHER-PHASE-BUG, AND THE BROWSER SAW
  BOTH.** `beatSchedule` reduced its phase modulo the HOLD. Every arithmetic
  invariant passed — the cuts really did land on beats, which is what I3 and I4
  assert — because shifting a grid by whole beats leaves it on the same beats.
  What it also does is put the FIRST cut up to a whole hold late: measured at
  the artifact, a 120 BPM track under `march` snapped to 4 s cut first at
  4.496 s where the unsynced build cuts at 4.000. Fixed to reduce modulo the
  BEAT — and the browser immediately produced the SECOND bug hiding behind it:
  a detector's phase is quantised to a hop, so the beat at 0.500 comes back as
  0.496, and reduced into `[0, period)` that reads as almost a whole beat of
  delay rather than as 4 ms early. **The snap has to go to the NEAREST beat, in
  both directions** — a phase over half a beat becomes a small negative one,
  which lands on exactly the same beats and puts the first cut within half a
  beat of where the roster would have put it. **The general shape: an invariant
  that quantifies over a SYMMETRY of the thing it is testing cannot see a defect
  that lives in the choice of representative.** Both are now pinned by I4b,
  which asserts the departure from the roster's own first cut rather than
  membership of the grid.
- **SCAR-C147-TWO SIBLING SPECS HAD NO WALL-CLOCK BUDGET, AND FAILED IDENTICALLY
  AGAINST PRODUCTION.** `turn.spec.ts` T1/T2 and `motion.spec.ts` T1/T2 came
  back red during this cycle's regression, on `Test timeout of 30000ms
  exceeded` rather than on any assertion. They WAIT rather than scrub — which is
  the point of those two tests, since something has to prove the schedule runs
  under a real rAF clock and not only when a ruler asks it a question — and they
  wait 5.2 s at rest before bracketing four turn boundaries, i.e. past the
  config's 30 s default before reading a pixel. **They were not a regression and
  the check that proved it took one command**: run the same spec with
  `COLLAGE_BASE_URL=<production>`, which is by definition the code from before
  the change. Identical failure. Fixed for both — the same explicit
  `describe.configure({ timeout: 300_000 })` the scrub-based specs already
  carry — because the previous cycle's own scar says the flake is never one
  spec, it is one habit, and the habit here is a spec that waits without saying
  how long it may.
- **SCAR-C144-HOVER-BEAT-CHOSEN, ON THE ONE DEVICE THAT CANNOT UN-HOVER.**
  Found by SCREENSHOTTING THE LIVE PAGE after shipping THE PACE, not by any
  test: the `2×` chip was active and was not green. `.ui-chip:hover:not(:disabled)`
  is specificity (0,3,0); `.ui-chip[data-active='true']` is (0,2,0). Hover won,
  so a chosen chip under the pointer rendered `--surface-3`. Measured on
  production: **rgb(31,36,39) chosen-and-hovered against rgb(22,25,27) genuinely
  unchosen — nine units per channel — where the right answer is rgb(61,220,151)**.
  On a desktop that is a flicker. On iOS Safari a tap leaves a STICKY hover
  until you touch something else, so **the chip you just tapped sits there
  looking untapped**, on the exact device the MOBILE-WATERTIGHT law is written
  for. It was never about the pace: FIVE of the six hover/active families in
  `controls.css` had it — `ui-chip` (the look, the move, the turn, the pace),
  `ui-gchip`, `ui-option`, `ui-swatch`, `ui-tile` — which is every roster row in
  the app. `.ui-ratio` was correct BY SOURCE ORDER ALONE (equal specificity,
  active declared thirteen lines later), which is not a property anyone should
  have to preserve while editing a stylesheet, so it got the guard too.
  **The general shape, twice over.** First: a screenshot is not decoration —
  four e2e suites, thirteen invariants and a green production run all passed
  over a control that looked unpressed, because every one of them asked the DOM
  what state it was in and none of them asked what COLOUR it came out. Second:
  the fix is to make hover NOT MATCH a chosen control (`:not([data-active='true'])`)
  rather than to out-specify it — the two states are mutually exclusive by
  intent, and saying so in the selector means no future reordering can put them
  back in competition. `pace.spec.ts` P5 is the guard, and it sweeps the sibling
  rows rather than only the row this cycle added; the mutation that removes the
  guard fails it with exactly the two colours above.
- **SCAR-C144-DYADIC-IS-NOT-EXACT, AND I WROTE THE CLAIM INTO THE MODULE HEADER
  BEFORE THE SWEEP READ IT BACK.** `lib/pace.ts` shipped its first draft
  claiming all five rates are dyadic rationals and therefore "EXACT in binary
  floating point and exactly reversible", with a paragraph explaining that this
  is what stops the preview and the exporter drifting apart. Half of it is
  true. 1/2, 1 and 2 are powers of two and exact both ways; 3/4 and 3/2 carry a
  factor of THREE, and multiplying by three can need one more mantissa bit than
  there is — `0.1 * 0.75 / 0.75` is 0.10000000000000002. I3 failed on the first
  run of the sweep written to confirm the claim, which is the entire argument
  for writing the sweep in the same cycle as the module: a header comment is
  the one place a wrong idea can sit unexecuted for years, looking authoritative
  to the next reader. **The general shape: a property you assert in prose is a
  property nothing is testing.** Both were corrected — the header now says what
  is actually guaranteed (one correctly-rounded multiplication, deterministic,
  applied identically by the preview and the offline walk), and the arm asserts
  exactness only for the powers of two, order-preservation for all of them, and
  determinism, which is the property callers actually rely on. Reversibility
  turned out to be needed by nobody: no caller ever divides by the rate.
- **SCAR-C144-THREE-SIBLING-SWEEPS-PINNED-THE-CODEC'S-LENGTH-AS-A-LITERAL, AND
  ONE FIELD BROKE ALL THREE.** grade I8c, motion I8c and turn I8b each carried
  their own hand-written `21` for "the middle group this build mints", and THE
  PACE made it 22 — three red arms, three identical messages, in files that have
  nothing else to do with each other. Each was asserting the right property
  through the wrong constant: what they mean is "one character longer than the
  generation I am about to rebuild", and that is a fact the CODEC owns. Fixed
  once, at the source: `diceRoll.ts` now exports `MINTED_GROUP_MAX` (derived
  from `MINTED_GROUP_LENGTHS`, the registry the codec already had to maintain)
  and all three read it. **The general shape, and it is this lane's BACKPORT
  rider applied inside one repo: when the same literal appears in three
  unrelated files, the next change breaks all three at once — and a test that
  fails for a legitimate reason in three places is a test that will be edited
  three times, which is three chances to edit it wrong.** The codec's own
  comment already told the next author to add the length to the set; now that
  set is the single source and the sweeps follow it.
- **A FADE THAT COULD NOT END, BECAUSE THE FLAG WAS A COMPARISON OF TWO NUMBERS
  ONE OF WHICH HAD JUST MOVED.** Shipped in THE TURN's first cut and caught by
  the adversarial audit before anyone used it — three independent lenses
  (canvas-state, schedule, wiring) reached it separately, which is what a lens
  panel is for. `refreshTurn` ended a dissolve with
  `if (this.turnBoundB !== this.turnBoundA)`, and the branch fifteen lines above
  advances `turnBoundA` to exactly that index IN THE SAME CALL — so the guard
  was already false and the cleanup never ran once. Replaying the real schedule
  at 30fps: `mix` sticks at 0.9944 forever, cleanup runs 0 times where it should
  run once per cut.
  WHAT IT LOOKED LIKE IS WHY NOTHING CAUGHT IT. After a cut, the incoming
  picture and the outgoing picture are the SAME photograph, so a stale 99.4%
  alpha over an identical image is invisible — six e2e tests, a 65,600-case
  permutation sweep and a live deploy all passed with it in. The symptom is one
  step removed: the incoming crop is only refreshed inside the fading branch, so
  under a MOVE a FROZEN copy sat over the drifting one and the drift stopped
  dead. Every frame also paid a second `drawImage` per fragment for the rest of
  the take.
  THE FIX IS THE SHAPE, NOT THE COMPARISON: a boolean `turnFading` that a
  sibling assignment cannot make false, and `turnBoundB = -1` as "nothing is
  bound" rather than an index that also happens to be a valid cache key (which
  was a second bug — a scrub back into a fade already passed would have found
  the key present and `still2` null, and dissolved into nothing). Now guarded
  BOTH ways: `turn.invariants.mjs` I10 replays the consumer state machine at
  24/30/60fps against the real `turnAt` AND carries a RED PROOF that the
  index-comparison shape fails it, and `turn.spec.ts` T7 measures on pixels that
  a drift survives a cut (10.46% of the frame moving, worst 99).
- **A SCENE PROP BUILT INLINE IN JSX RESTARTS THE TAKE ON EVERY UNRELATED
  RENDER.** Also from the audit, also found by three lenses. `turn={turning ? {
  id: turn, seed, resolve: turnResolve } : null}` allocated a fresh object every
  App render, and that object is a dependency of VideoStage's `setScene` effect
  — which ends by resetting `moveOriginMs` to -1, the take's clock origin. So
  any unrelated state change (a notice, a hover, the autosave tick) rebuilt the
  scene and restarted the clock, and a schedule keyed on ELAPSED TIME is then
  permanently inside its first hold: the feature would simply never fire in a
  session where anything else moves. Every other entry in that dep array is a
  primitive or a `useMemo` for precisely this reason — VideoStage's own comment
  says so about the soundtrack, twenty lines below the line that broke it.
  Memoised now. The general rule this earns: ANY object handed to `setScene` is
  a clock reset in disguise, and belongs in a `useMemo` keyed on primitives.
- **A "LEGACY" FIXTURE THAT LEARNS THE NEW FIELD STOPS BEING A LEGACY FIXTURE.**
  Third audit finding, minor and the most embarrassing: `session-recovery.spec.ts`'s
  `legacyArchive()` is documented one line above itself as "a `.collage` archive
  exactly as the PREVIOUS build wrote it", and THE TURN's first cut helpfully
  added `turn: 'hold'` to it — deleting the repo's only coverage of a manifest
  that LACKS the newest field, in the same commit that made the field exist.
  Reverted. Adding a field to a legacy fixture is not maintenance; it is
  removing the test.
- **A GUARD THAT FAILS THREE RUNS IN FOUR IS NOT A GUARD — `composition.spec.ts`
  line 225.** Found while attributing a red run during THE TURN, and it is NOT a
  turn regression: measured on BOTH trees, 4 runs each. The assertion is the
  fixture-sensitivity check that Detail and Centre crop differently at all
  (`|previewGap| > 8`), but the app boots on a `Date.now()` seed, so the layout
  and the deal are different every run and the gap is a random variable.
  Measured gaps — THE TURN's tree: 7.5 / 5.4 / 7.4 / 6.7 (1 pass in 4). Clean
  HEAD (`git archive HEAD` into a scratch dir, its own vite on :5198, so the
  working tree was never disturbed): 5.2 / 5.0 / 7.4 (1 pass in 4). Identical
  distributions, straddling a bar of 8.
  THE COST IS NOT THE RED, IT IS WHAT THE RED TEACHES. A suite where one spec
  cries wolf 75% of the time trains the next cycle to wave a failure through,
  which is the exact failure mode `THE COLOUR PROOF WAS A RANDOM VARIABLE`
  (d05f5b44) was filed for one cycle earlier — same root cause, different spec,
  and this one was not swept then. The fix is the one that scar names: PIN THE
  SEED. The app already accepts a whole composition (seed included) through the
  `?c=` code param, so the test can boot on a fixed code and the bar can be
  re-derived from the floor of several runs on THAT composition, instead of
  being a taste-picked number held against a distribution nobody measured.
  THE SWEEP FOR THE SAME CLASS (the rider: a fix that lands on one place and
  leaves its siblings is half a fix). Static pass over all 28 e2e specs asking
  "does this file's numeric bar document where it came from, and does it pin a
  composition?" — exactly ONE spec documents measured provenance for its pixel
  bars (`motion.spec.ts`, five citations and a per-move table of three runs),
  and NOT ONE spec pins the seed before taking a pixel measurement. The
  shortlist that measures PIXELS over an unseeded boot, and is therefore in the
  same class as the defect above rather than merely adjacent to it:
  `composition`, `look`, `twist`, `title`, `colour-dice`. This is a STATIC
  heuristic, not a flake measurement — only `composition` has actually been run
  enough times to show a distribution (4 runs per tree). Naming the shortlist is
  the sweep; measuring it is the next cycle's, and cheap: run each five times
  and read the spread.
- **A FRAGMENT REBOUND BEFORE ITS DECODE LANDS KEEPS THE OLD PICTURE AND THE NEW
  ANALYSIS, for a few frames.** `bindTurnSource` re-points `stillKey`,
  `previewKey`, `fullKey` and `analysis` together, but only swaps `it.still` and
  recomputes the crop if the decode is already resident — the "a softer fragment
  beats a hole" rule `applyStillKeys` relies on, and `adoptStill` patches the
  pointer the instant the decode resolves. In the window between, a `move` would
  crop the OUTGOING image against the INCOMING one's analysis: a valid, clamped,
  slightly-wrong crop for at most a few frames. Not reachable in practice —
  `setScene` puts every participating key in `wanted` and the first cut is at
  least 3.5 s later — which is exactly why it is written down rather than
  guarded: the guard would cost a per-frame branch on the one path where the
  frame budget is the product, and the real fix is a deferred rebind that
  retries, not a check.
- **THE TURN IS SCOPED TO PHOTOGRAPH FRAGMENTS, and that is a decision.** A
  fragment holding a live clip is a fixed point of every permutation. Moving a
  clip between cells would change `clip.fragments` and `clip.area`, which are
  what `refreshAdmission` ranks decoders by — so a cut would have to re-rank
  decoder admission mid-take, and during a dissolve BOTH the outgoing and the
  incoming clip would have to be `live` simultaneously or one side of the fade
  degrades to a poster. Defensible on its own terms (a clip is already a moving
  picture; you do not dissolve it away mid-play) and it keeps admission a
  scene-time decision. The honest gap: in a collage that is mostly video, THE
  TURN has little to move, and nothing in the UI says so.
- **THE TAKE'S CLOCK AND THE RECORDER'S PROMISE ARE TWO DIFFERENT CLOCKS, and
  THE FADE was wired to the wrong one at BOTH ends.** Found by the adversarial
  audit, three independent lenses, all three confirmed under refutation — and
  nothing in this repo's suite could have caught either half, because every
  engine here has WebCodecs and therefore never takes the realtime branch.
  **THE HEAD.** `stage.applyTakeFade` anchors the whole envelope to
  `ctx.currentTime` at the instant it is called, and it was called at the call
  site that invokes `record()` — which is not when recording starts.
  `record()`'s first act is `await probeVideoExportSupport()`, a one-time dry
  run worth up to `PROBE_RECORD_MS + PROBE_STOP_MS` ≈ 1.9 s, and `rec.start()`
  is ~200 lines later. So the ramp DOWN to zero landed ~1.9 s before the encoder
  stopped: the file's head opened part-way up the fade-in and its whole tail
  recorded at gain 0. Reachable on any engine without a usable WebCodecs H.264
  encoder — and, more sharply, on EVERY engine in the window before
  `probeFrameExportSupport` resolves, because `useRender = !!frameSupport?.supported`
  is false while the probe is still null and `canRecord` is optimistically true.
  The fix is not a guess at the latency: `RecordOptions.onStart` now fires the
  instant `rec.start()` returns, and the envelope is armed from there.
  **THE TAIL.** `clearTakeFade` was called from the recorder's `.finally()`,
  i.e. when the PROMISE settled — which is after `MediaRecorder.stop()`, after
  finalize, and after the result is decoded back to validate it. An `AudioParam`
  holds its last event value indefinitely and `masterGain` is not a record-only
  tap (`ensureAudio` wires it straight to `ctx.destination`; `captureStream`
  adds a SECOND leg), so the live preview sat at silence for those seconds and
  then STEPPED back to full level. The fix puts the monitor's recovery into the
  same atomic schedule, a beat after the take and as a ramp rather than a step;
  `clearTakeFade` stays for the take that ends early.
  **The general shape, and it is the one to carry forward: a promise settling is
  not the event happening, and the call site of an async function is not the
  moment it starts. Anything scheduled on a clock for an operation that begins
  later must be armed BY that operation, not by the code that asked for it.**
  Third finding from the same audit, same family and cheaper — and the one
  place the refutation pass earned its own keep, by narrowing WHICH trigger is
  reachable: an encoder error mid-loop (never, in practice, the memory cap,
  which needs ~3x the configured bitrate for a whole take) leaves
  `frames < totalFrames`, so `truncateAudio` cuts the audio where the envelope
  is still 1.0 and the delivered file ends at full level — the exact hard cut
  the feature removes — while the take bar still reads "fading in and out over
  1s". Unfixable after the fact (the samples are AAC by then, and the mix ran
  before the frame loop knew the length), so it is REPORTED, which is the rule
  `mixSources`' `onTruncated` already follows one layer down.
- **A DESIGN NOTE WRITTEN FROM INSIDE ONE CODE PATH PRESCRIBED AN IMPLEMENTATION
  THE OTHER PATH CANNOT EXECUTE.** The Audio rung had carried this sentence
  since THE SOUNDTRACK shipped: a fade's "honest place is the sample domain,
  right where the peak limiter already walks the whole rendered buffer." It is
  correct, it is specific, it names a real line — and it is only true of
  `renderOffline`. The realtime `record()` fallback encodes a LIVE graph through
  `captureStream`'s tap on `masterGain` and has no buffer to walk at all, so a
  fade built to that note would simply not exist on any browser without
  WebCodecs, silently, with every gate green (the whole suite is chromium-only,
  and chromium always takes the offline path). Counting the surfaces FIRST is
  what changed the design: two emitters means the envelope has to be a shape
  both can express exactly, which is why it is linear rather than equal-power.
  **The general shape: a "still owed" note is written by whoever was last
  standing in one path, and it inherits that path's assumptions without saying
  so. Before implementing one, count the surfaces the capability has to reach
  and check the note is true of all of them.** ONE LAYOUT counted four, THE
  TITLE counted four, THE LOOK counted four; this one had counted one.
- **THE INSTRUMENT THAT MEASURES THE ARTIFACT LIVED INSIDE A SPEC FILE.**
  `toneEnvelope` — decode the exported MP4 and read energy at one tone slice by
  slice — was written in `trim.spec.ts` for the lap schedule and left there. It
  is not a trim thing: it is the ONLY measurement in this repo with a time axis,
  and a time axis is what every future audio capability (a fade, ducking,
  beat-sync, an asymmetric tail) needs to prove itself. The next suite to want
  it would have pasted a third Goertzel next to the two already in the tree, and
  then two suites would be free to disagree about what one MP4 contains — the
  exact reason `tone-measure.ts` exists at all. Moved on its SECOND caller, as
  the extract-the-engine rule says, and the trim straddle test re-run to prove
  the move changed nothing (`####........####....`, digit for digit).
  **`measureTones` still has a private copy in `trim.spec.ts` and that is the
  next one to collapse** — named here rather than swept in this cycle, because a
  pure move deserves the regression run that proves it and this cycle spent that
  budget on the envelope.
- **A TEST ASSERTED THE LAYOUT THAT PROVIDED THE GUARANTEE, NOT THE GUARANTEE.**
  `undo.spec.ts` U4b checked that every full-bleed rail control started to the
  RIGHT of the one before it. That was true, and it was really protecting
  "controls never sit on top of each other" — but it encoded the single ROW as
  if the row were the point. Adding the seventh 44px target (the colour dice)
  made a single row impossible at 320px at any legal tap size, so the rail wraps
  4/3 and three engines went red **against correct code**. The fix is not to
  delete the assertion: it is to assert the invariant it was standing in for —
  pairwise non-overlap, which holds along a row and across a wrap. **The general
  shape: when a passing test fails on a deliberate design change, ask whether it
  was asserting the promise or the current implementation of the promise.** One
  of those is worth keeping.
- **A FLAT FIXTURE CANNOT WITNESS A CROP.** The colour-dice spec built its
  sources as solid-colour PNGs, then asserted that every roll repaints. A roll
  that changes only `focus` moves WHERE IN THE PHOTO each fragment is centred —
  and every part of a flat tile is the same pixel, so the correct button
  repainted nothing and the spec reported "the picture did not repaint" on two
  engines. The fixture could not express the property under test. **Before
  believing a red, check that the fixture is capable of showing the thing being
  asserted** — and note the sibling fact this turned up: `auto` falls back to the
  busiest region on a photo with no face in it, which is exactly what `energy`
  already is, so that pair genuinely paints the same picture on any content. The
  per-press claim now rides on the arrangement (always visible across distinct
  sources); the crop rides on a count across presses.
- **A CHECKSUM IS NOT A PARAMETER.** "Every field of the composition code except
  the three this button owns must come back byte-identical" reads airtight and
  is wrong: the code ends in a checksum OVER ALL FIELDS, including the three
  that legitimately changed. As written, the assertion could only pass against a
  dead control — and its failure message said "the colour dice moved something
  it does not own", which is exactly what a real bug would say. **A witness
  derived from the thing under test is not an independent field.**
- **A COMMENT CLAIMED A BOUND, THE CODE NEVER HAD ONE, AND THE COMMENT IS WHY
  NOBODY LOOKED.** `prepareOfflineStills` rasterised each source to the scale
  its own fragments consume — correct — under a doc sentence reading "and the
  rasters together are bounded by the canvas area" — false. It is true only for
  a fragment showing its WHOLE source. A fragment shows a CROP, so asking for
  `dwPx / isw` of a source that is `k` crops wide rasterises `k * dwPx`: the
  raster is **k² times the destination area**, and k = 2 is an ordinary
  cover-fit. Nothing bounded the total; the loop walked every source and
  allocated whatever geometry asked. Its only limit was a 20-second wall clock,
  **which on a faster machine lets it allocate MORE, not less** — so the bug got
  worse the better the device and the more photos were in the collage. 30 photos
  at k=2 was 415 MB of resident RGBA; 120 at k=3.5 was 5,089 MB. **The general
  shape: a load-bearing claim written as prose is never checked again. If a
  comment states a bound, either a test asserts that exact sentence or the
  sentence is a liability** — this one survived every review precisely because
  it sounded like the reasoning had already been done.
- **A BOUND PROVEN IN CONTINUOUS MATH IS NOT A BOUND ONCE `Math.round` RUNS.**
  The fix's allocator returned the scale where `srcPx * s² == capPx` exactly,
  and the caller then rounded a width and a height to integers — **rounding up
  from an exact fit lands above it, every time**. A few hundred pixels per
  source, 135 breaches across the sweep, and each one individually invisible.
  The rule that came out of it: **the function that produces the INTEGERS must
  own the ceiling**, not inherit it through a real-valued scale. Flooring all
  three ceilings (`source`, `wanted scale`, `sqrt(cap · srcW / srcH)`) makes
  `w·h ≤ cap` an identity instead of a rounding accident. Two sibling defects
  in the same module, same family: **the ceiling was applied AFTER the charge it
  was meant to cover** (`min(ceiling, pool − canvas)` lets the ceiling swallow
  the canvas charge whenever the device pool sits above it — i.e. exactly at the
  top end, so the rung rendering the biggest canvases was the one rung not
  paying for them); and **`navigator.deviceMemory` SATURATES AT 8**, so a 64 GB
  Mac Studio and an 8 GB Air report the same number and the top rung must be
  sized for the smallest machine in it, not the largest. That one had a tell
  worth remembering: the Chromium path handed a laptop 512 MB while the GPU path
  handed the SAME laptop 256 MB — **one machine, two budgets, decided by which
  browser it was opened in. Two code paths disagreeing about one device is a
  defect even when neither number looks wrong.**
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

- **SCAR-C90-THE-RULER-MOVED-BEFORE-THE-APP-DID (an exact pixel hash is not a
  witness for a picture that is supposed to move).** The first run of the new
  undo e2e reported "undo did not restore the picture": same size, same luma to
  two decimal places, different FNV hash. That reads exactly like a real defect
  — same composition, pixels in different places, i.e. the deal moved. It was
  the TEST. A composition carrying a MOVE mounts the live Stage canvas instead
  of the static JPEG, and a drifting canvas renders different pixels every
  frame; sampling one twice 700ms apart **with no interaction at all** produced
  two different hashes at identical luma. Measured rather than argued: 20
  readbacks of an untouched preview give **1 distinct hash on a still preview
  and 6 on a drifting one**, while a 256-block signature (16x16, each block
  reduced to its dominant channel or a luma bucket) gives **1 in every case and
  still separates 10 of 10 distinct rolls** — stable under the drift and still
  able to fail, which is the whole test for a witness. THE RULE: when a
  comparison fails, ask whether the thing you are measuring with is allowed to
  change on its own before you go looking in the code. The same defect was
  sitting in `tests/e2e/roll-code.spec.ts`, which had been failing about one run
  in five for this exact reason; fixed there in the same cycle (BACKPORT rider).

- **SCAR-C90-NOT-YET-MOVED-IS-NOT-SETTLED.** The replacement wait sampled until
  two consecutive readings agreed and returned that shot — which is satisfied
  perfectly by the picture that has not started changing yet. Click undo, sample
  twice before the repaint lands, get two identical readings **of the
  composition undo is leaving**, and report "undo did not restore" against a
  shot of the thing being replaced. It only ever fired on WebKit, where the
  repaint is slower, so it looked like a WebKit product bug. A wait that can
  return the PREVIOUS state is not a wait: it must be told what it is leaving
  (`settled(page, changedFrom)`) and refuse to settle until the picture has
  actually moved.

- **SCAR-C90-EVERY-`<input>`-IS-NOT-A-TEXT-BOX.** The Cmd-Z handler guarded
  itself with `/^(INPUT|TEXTAREA|SELECT)$/` so the caption box would keep its
  own undo. A range slider, a colour swatch, a checkbox and the file input are
  all `<input>` and none of them owns Cmd-Z — so undo would have been DEAD for
  the rest of the session after any slider drag, silently, because a dead
  shortcut is indistinguishable from a shortcut you imagined. Only a control
  with TEXT in it has an undo to defend. Found by the WebKit run (Mobile Safari
  leaves focus on the file input after an upload), not by reading the code.

- **SCAR-C90-THE-WITNESS-CAN-BE-THE-FEATURE-WORKING.** The test asserting "Cmd-Z
  inside the caption box must not step the collage back" compared PIXELS, and
  went red on every engine. The caption is DRAWN ON THE COLLAGE, so the
  browser's own field-undo removing the typed text changes the picture — the red
  was the guard succeeding. The caption is deliberately not in the composition
  code, which makes the code the only correct witness for "the composition did
  not move".

- **SCAR-C126-A-BOUNDARY-MUST-BE-REACHED-THE-WAY-PRODUCTION-REACHES-IT.**
  `lapAdjust` subtracts the laps rather than taking a modulo, and the module
  said why: the two "disagree exactly at the boundary the caller is about to
  test." The sweep asserted everything around that claim and never it, because
  the sweep built its boundaries by MULTIPLYING (`k * take`, exact) while a
  clock reaches them by ADDING. Mutation testing is what exposed the gap — `%`
  for the subtraction SURVIVED the first pass — and the arm written to kill it
  then went red against the REAL module and found a defect neither the code nor
  the mutant had: ten laps of a 4.3s take arrive at 42.99999999999999, `floor`
  reports NINE, and the playhead sits at the far RIGHT of the bar for one frame
  at the exact instant it should be returning to the left. Measured once the arm
  existed: `%` and the subtraction differ on 330,567 pairs with a worst delta of
  a WHOLE TAKE. **The general shape: a claim about a boundary is only tested by
  a boundary reached the way the shipped code reaches it. Accumulate if
  production accumulates.** `LAP_EPSILON` is the fix; M14/M15 guard it.

- **SCAR-C126-A-DERIVED-CLOCK-NEEDS-A-STOP-AT-EVERY-PLACE-THE-DRIVER-STOPS.**
  The playhead's position is `(now - origin)`, so the origin must be re-anchored
  whenever the loop was not running — and THREE different things end this app's
  rAF, of which only one runs any code: the tick's own idle branch (which can be
  told), `stop()` (which cancels the handle outright) and `applyPowerState`
  (which cancels it when the Stage scrolls off screen or the tab hides). A clock
  still marked "running" across one of those gaps counts the entire gap into the
  playhead the moment something plays — scroll the Stage away for a minute and
  the bar jumps a minute. Found by MAPPING the driver before writing the
  consumer rather than by shipping it, which is the only reason it is a note and
  not an incident. **The general shape: when you derive a value from elapsed
  wall-clock, enumerate every place the driver stops — cancelling a timer is
  silent, and silence is the failure mode.**

- **SCAR-C126-A-CONTROL-THAT-ASKS-WHICH-SOURCES-EXIST-DISABLES-ITSELF, AND THE
  ANSWER WAS ALREADY WRITTEN ONE BUTTON TO THE RIGHT.** The Play button was
  `disabled={liveCount === 0}` and its icon read `clips.some(playing)` — so a
  collage of photographs drifting under a soundtrack showed Play while the
  picture moved, and could not be started or stopped at all. This is the SAME
  bug, in the same bar, that `takeable` was invented to fix for the SOUND
  button, with the fix's own comment sitting three lines above the broken
  control: *"it stopped being the same question the moment the Stage could
  record something that is not a clip."* One control was swept and its
  neighbour was not. **The general shape, and it is this lane's BACKPORT rider
  applied INSIDE a component: when you fix a "which sources exist" question on
  one control, sweep the whole bar for the same question before you leave.**
  `StageStatus.rolling` now answers from the Stage, which is the only place that
  can see the move, the music, the clips AND the park at once.

- **SCAR-C126-A-COLOUR-PROOF-NEEDS-A-CANVAS-THAT-IS-ONLY-THE-THING-BEING-GRADED.**
  The scrub proof grades the LIVE canvas by dominant channel, an instrument
  trim.spec.ts built and which averages the WHOLE surface. This spec uploaded
  the ramp fixture AND a photograph, for realism — so a second picture entered
  the average, and whether the ramp still won by the classifier's 1.6x margin
  came down to the DICE: which fragment got which source and how big it came
  out. It passed locally and the SAME assertion read `?` on the very first run
  against production, because the two runs rolled different layouts. trim.spec
  uploads exactly one file and now so does this. **The general shape: a
  generative layout makes any whole-canvas measurement a random variable, so a
  spec that grades pixels must control the composition, not just the moment.**
  Caught by running the suite against PRODUCTION rather than treating a green
  localhost run as the ship gate.

- **SCAR-C127-A-ROUTER-THAT-ASKS-THE-OBJECT-CANNOT-HEAR-THE-VERB.**
  Three file buttons — add anything, add video, add MUSIC — all fired one
  `onChange` that called `ingestFiles(list)`, so routing was a total function of
  the FILE and the app could not know which button was pressed. Press "Add
  music", hand it a `.mov`, and `isVideoFile` answered *video* — correctly, for
  a question nobody asked — and the clip landed in the collage as a rectangle.
  Nothing in the ladder was wrong; the ladder was answering the wrong question.
  **The general shape: when the same input can mean two things depending on WHICH
  CONTROL the person reached for, the control's intent is part of the input.
  Adding a fourth predicate is the wrong fix — "what kind of file is this" has
  one answer and "what did this person ask for" has another, and only the second
  one can be wrong.** The second half of the same defect was in the picker
  itself: `accept="audio/*,…"` greyed the video out before any routing ran, so
  even a perfect ladder was unreachable from a desktop. A rule that lives in two
  places (the router AND the `accept` list) is only fixed when both agree.

- **SCAR-C128-AN-UNDO-THAT-CANNOT-RESTORE-THE-THING-IS-WORSE-THAN-NO-UNDO.**
  Eviction removes assets, and the full-bleed rail has an Undo two buttons away
  from where it happens — so wiring the removal to `pushHistory` was the obvious
  move and would have been a lie: `compositionHistory` holds a share code and
  the pins, never the pool, so the "undone" state would come back with the
  photograph still gone. A control that appears to reverse an action and does
  not is strictly worse than one that never offered, because the person stops
  looking for the real way back. It writes to the SESSION history `handleClear`
  already uses — the one that carries `images` — and the rail's Undo was left
  alone. **The general shape: before wiring a destructive action to an existing
  undo, check what that undo actually stores. Two histories in one app is not a
  bug; assuming they are the same one is.**

## THE RATCHET (perpetual by construction)
When a capability tier reaches broad parity with CapCut, the north star raises:
the next tier (pro effects, AI-assisted editing, collaboration) becomes the
frontier. Today's ceiling is tomorrow's floor.

## CYCLE LOG (append one line per collage cycle — capability · before→after · proof)
- 2026-08-14 · **[AXIS:WELL] THE DICE NOW SEES HOW MANY PHOTOS YOU SENT** — from
  wish `d27650c7` (kind=bug, the well read UNSCOPED first; 1 new, 0 stranded in
  `building`): *"You should make randomize the same count as the images uploaded
  — why everytime I hit random it does over 100 it should be within range of the
  number of images sent."* **before → after**, measured end to end on the real
  generators at the wisher's own pool of twelve photographs, on cells actually
  DRAWN and not on the number requested: **median 69 fragments → 23 · p90 180 →
  32 · worst-in-600 434 → 62 · share of rolls that break the ceiling 79.3% →
  2.8%.** Big pools untouched: at eighty photographs the roll is what it always
  was (median 77 → 76). Confirmed in the DEPLOYED bundle before a line was
  written — `count:[90,220]`, `count:[80,260]` — never re-reasoned from source.
  **THE DEFECT WAS ONE LINE OF WIRING:** `rollDice({ hasVideo })`. The app snaps
  the fragment count to the number of distinct sources on import and has an e2e
  proving it; the most prominent button then threw that away, because the roll
  was never told the pool existed, and `countOwned` latched so every later press
  did it again. **THE PANEL RETURNED BUILD_DIFFERENT_SHAPE, UNANIMOUS, AND ITS
  DECISIVE OBJECTION KILLED THE OBVIOUS FIX:** `count` is a REQUEST, not the
  number of fragments — capping it at 36 still puts 87 cells on the canvas,
  because a Flower of Life emits 39 at its smallest lattice whatever you ask for.
  Two measured facts per generator now carry that (`deliveredFloor`,
  `overshoot`), and the sweep RE-MEASURES both every run so neither can rot into
  a comment. **THE PANEL'S FIRST DRAFT WAS ALSO OVERRULED, WITH ITS OWN
  MEASUREMENT:** forcing the count UP to the source total (so "nothing is
  stranded") moves the median at eighty photographs from 80 to 115 — it makes the
  tool do MORE of the thing the wish is about, to enforce a guarantee the app
  does not make (`source-count.spec.ts` R3 pins a user holding three photos at
  two fragments as CORRECT). So the pool may only ever LOWER a roll, never raise
  one, and that is invariant I1. **NOTHING WAS FILTERED BY TASTE** — the loudest
  attack was that a band-filter deletes nineteen of twenty-four recipes at a
  small pool, and this file already records that scar twice in its own words ("A
  LEAN, not a rule"). Admission is by PHYSICS: a figure is dropped only when it
  cannot be drawn under the ceiling at any request, which costs exactly one
  figure and one recipe below thirteen sources and nothing above it — asserted,
  not asserted-to, as I6. **BACKPORT RIDER FIRED — the class is "a control that
  ignores the size of the user's own input", swept across every other count-
  setting path in the app:** `rollDeal` (the colour dice) rolls no count and
  needed nothing; `applyCompositionCode` carries a literal count and is correctly
  EXEMPT (a code must reproduce the sender's picture, not the recipient's pool);
  `templates.ts` carries fixed counts and the import grow-to-cover already lifts
  them; and `density` was the one that bit — the readout prints `count x density`
  and the chips go to 4x, so a ceiling on the count alone let twelve photographs
  become 144 fragments WITH the fix installed, which is the wisher's literal
  complaint reproducing through its own fix. Density is inside the ceiling now
  (D6). No trade toolkit page has a generative control, so the class cannot exist
  there. **GATES: 12 invariants over 16 pool sizes x 900 seeds x every recipe and
  generator, all green** — including I11, which re-measures the shipped delivery
  data against the real module, and I12, which BANDS the accepted residue (the
  quantised figures landing on their next admissible rung) so re-widening it
  fails loudly. Plus a new 6-assertion e2e driving the real button on the real
  page — **3 of 5 RED against the shipped build, 6 of 6 green against the fix** —
  and green again against PRODUCTION after deploy. Regression: all 26 unit
  sweeps, `source-count` 7/7, `roll-code` 20/20, `colour-dice` 9/9, `tsc` and
  `vite build` clean. **NOT SHIPPED, AND NAMED SO IT IS NOT RE-DERIVED:**
  `slotCount = max(effectiveCount, layoutItems.length)` sizes the photo
  assignment to the REQUEST while the renderer paints only delivered cells, so an
  under-delivering figure leaves a source assigned to a cell nobody draws (~8% of
  rolls at twelve). It is a separate defect in a different module, it bites the
  manual stepper identically, and it reads at five call sites plus the export
  path — it is the next rung, with its own gate. Wisher credited on the Wall of
  Wishes, anonymity honoured.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
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

- **C78c · 2026-08-09 · [AXIS:WELL] WHAT THE ADVERSARIAL AUDIT FOUND, INCLUDING MY
  OWN HOUR-OLD BUG** — cast a subagent at the shipped commit asking only "how does
  a user LOSE WORK here". Five real findings, all fixed in this pass:
  **(1) The guard I added an hour earlier was itself a data-loss bug.** "If a flush
  cannot capture every asset, write nothing" sounds safe and freezes autosave
  FOREVER — `plan.write` holds exactly the ids the store lacks, so one unreadable
  asset is in every subsequent plan, fails every time, and silently stops saving
  for the rest of the session while the user believes they are protected. Now the
  snapshot EXCLUDES what it could not capture instead of refusing to exist: a
  recovery one photograph short is a real recovery; an autosave that quietly
  stopped an hour ago is not. **(2) Two tabs could destroy each other's session.**
  The plan is computed on one connection and committed on another, so a second
  tab's flush can drop this tab's assets as orphans in between — leaving a
  manifest naming bytes that no longer exist, which the next restore fails closed
  on and then CLEARS. `putSession` now re-derives the key set INSIDE the write
  transaction and aborts on a stale plan, so the previous good snapshot stands.
  **(3) A failed READ was treated as a dead session and deleted.** `loadSession`
  now returns `unreadable` distinctly from "gone", and only a structurally-bad row
  is forgotten — pulling a whole pool back out is exactly what fails on the device
  that just died of memory pressure. **(4) The v1 archive branch accepted a SHORT
  or EMPTY pool**, silently, while the SVG branch and the session path both
  document why that is forbidden; an empty one never dismissed the banner, so the
  endless loop was still live on that branch. Fails closed now. **(5) A
  zero-dimension asset entered the pool** (the hang fix turned a hang into a
  silently broken asset) and then got copied forward into the v2 manifest, so it
  restored blank forever. Rejected on both doors now, the same rule `handleUpload`
  already enforced. Plus the archive branch's `catch` leaked every object URL it
  had minted. **24 passed / 4 skipped** across all four engines, **123/123**
  chromium. The audit's clean negatives are on the record too — `putSession`
  atomicity, `write ∩ drop = ∅`, restore ordering and settings fidelity, and the
  URL bookkeeping in `handleRestoreSession` — all verified correct.
  **NOTE FOR A LATER CYCLE (found, not fixed, not mine):** `svg-project` S1/S3/S8
  fail on Mobile Chrome and Mobile Safari, and fail identically on the pre-fix
  commit — a pre-existing mobile gap in the SVG round-trip, unrelated to this wish.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C87 · 2026-08-10 · [AXIS:WELL] THE RENDER ASKED FOR EVERY PHOTO AT FULL
  RESOLUTION AT ONCE, AND THE TAB DIED** — wish `66ba8852` (bug, collage/export,
  anonymous): *"The video export crashes when rendering higher than 2k. Please
  audit the code and look for sota way to render higher photos."* Found it
  **STRANDED in `status=building`** by a cycle that died mid-build, with
  `rasterBudget.ts` and its 2,506-check sweep sitting uncommitted in the working
  tree — **and the sweep was RED: 135 breaches of the very bound it was written
  to prove.** Finishing it was the claim; a wish that looks served and is not is
  worse than an unclaimed one.
  **THE BUG:** `prepareOfflineStills` allocated `k²` × the destination area per
  source with no global ceiling anywhere (see the scar above), so cost grew with
  photo count AND with crop tightness, and its only limit was a wall clock that
  a fast machine beats. **THE FIX:** a device-derived pool divided **fair-share
  with roll-forward** — a greedy source is capped instead of eating the budget
  and abandoning the tail at preview quality — floored at the thumbnail already
  bound, so an over-tight budget means *"no upgrade happened"*, never a softer
  frame and never a hole. **THE THREE DEFECTS THE SWEEP CAUGHT AND READING DID
  NOT:** the continuous proof did not survive `Math.round`; the ceiling was
  applied after the canvas charge; `deviceMemory` saturates at 8. All three in
  the scar above.
  **NUMBERS.** 30 photos @ k=2: **415 MB → 136 MB**. 30 @ k=3: 935 → 136.
  60 @ k=3: 1,869 → 136. 120 @ k=3.5: **5,089 MB → 136 MB.** Flat — the pool
  decides, the content no longer does.
  **VERIFIED WHERE IT COULD HAVE SHIPPED AS A QUIETER VERSION OF ITSELF.**
  Bounding memory by softening every photo passes a memory test perfectly, so
  the picture was measured, not assumed: `video-resolution` scores gradient
  energy along a scanline and the originals still read **124.4 against the
  thumbnails' 33.0**. Added `tests/e2e/raster-budget.spec.ts` because the unit
  sweep grades ARITHMETIC and cannot see WIRING — one missed `ledger.commit()`
  on a refusal path leaves the arithmetic perfect while the pool runs over. On
  the real Stage with real decodes: n=8 used 13,665,992 / budget 13,668,352;
  n=12 used 13,668,273; **n=32 used 13,666,329 — four times the photos, the same
  13.67 MP**; and starved to a 1-pixel pool, `full=0 fellBack=12` with the frame
  still measurably whole.
  **4,673 invariant checks · 26 export e2e · 3 new wiring e2e · tsc + vite build
  clean · live bundle SHA-256 byte-identical to the local build.**
  **RESIDUAL, MEASURED NOT GUESSED (next rung):** when the pool cannot lift
  every source, WHICH sources get lifted is decided by iteration order — the
  ledger's roll-forward grows the share as early sources refuse, so the ones
  lifted are at the back. At n=32 the split is 19 photos at a 1024px thumbnail
  against 13 at 1025px, i.e. **imperceptible by construction**, because the
  floor rule forces the fallback to sit at most a pixel below the smallest
  raster that beats it. It is still 13 full decodes and allocations bought for
  one pixel each. Fixing it properly is a two-pass allocator that knows source
  dimensions BEFORE deciding shares — which `prepareOfflineStills` cannot, since
  it learns them from the decode. Tempting one-line thresholds make it WORSE:
  requiring a 1.25× margin to be "worth the allocation" turns 19@1024/13@1025
  into 24@1024/8@1307, trading an invisible split for a visible one. Design
  change, not a tweak.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C87b · 2026-08-10 · [AXIS:WELL] THE BUDGET WAS DOING CAREFUL ARITHMETIC
  DOWNSTREAM OF THE CRASH — A CORRECTION TO C87 ABOVE** — cast an adversarial
  audit at the commit I had just shipped, asking only "can this still exhaust
  memory". It could, and the entry above **overclaims**: the pool is correct
  about what it bounds, and what it bounds was **not the dominant term**.
  **THE REAL CRASH.** `beginOfflineRender` sets `offlineFullRes = true` and
  calls `applyStillKeys()`, which repoints every fragment's `stillKey` at its
  ORIGINAL and hands that set to `ensureStills` — which starts every missing key
  **AT ONCE**, one `new Image()` per source, each decode retained in
  `this.stills` for the whole take. N full-resolution decodes went resident, in
  parallel, **before `prepareOfflineStills` had ranked, budgeted or even counted
  anything.** Thirty 12 MP photos is ~1.4 GB of RGBA; the pool was managing
  136 MB of rasters downstream of it.
  **THE PART THAT SHOULD HAVE CAUGHT ME.** `applyStillKeys`'s own doc comment,
  twenty lines above the call, says it exactly: *"Pointing `stillKey` at the
  originals and letting `ensureStills` fetch them would therefore hold N
  full-resolution decodes at once … That is not a slow export, it is a dead
  tab."* I read that comment while writing C87 — I quoted its neighbour in the
  scar above — and read it as the rationale for the geometry budget rather than
  as a live description of what the caller was doing. **A comment can be
  simultaneously the best explanation in the file and a report of a bug nobody
  noticed it was reporting.**
  **FIX:** separate repointing from fetching. The offline path still repoints
  (that is what makes `adoptStill` land a budgeted raster on the right
  fragments) and leaves the FETCHING to `prepareOfflineStills`, which does it
  sequentially, inside the pool, releasing each decode before the next.
  **MEASURED BOTH DIRECTIONS**, because a guard that passes before AND after a
  fix is not a guard — B4 counts full-res `<img>` decodes the offline pass
  starts: **old line n=8→8, n=32→32** (linear, parallel, retained); **new line
  n=8→0, n=32→0**. And the picture did not pay for it: `video-resolution` still
  scores originals **124.4 vs thumbnails 33.0**.
  **WHAT THIS SAYS ABOUT C87's METHOD.** 4,673 invariant checks and three
  wiring e2e all passed against a fix that left the dominant allocation
  untouched, because every one of them was scoped to the thing I had decided
  was the bug. **A test suite inherits its author's hypothesis; only an
  adversary re-derives it.** The cheap general rule: when you bound a resource,
  measure the resource — not your model of it. B4 measures decodes; C87
  measured only the pool.
  **STILL OPEN FROM THE SAME AUDIT** (verified real, not fixed here): the
  "never softer than the preview" floor reads `it.still`, so exporting BEFORE
  thumbnails have decoded gives floor 0 and can render a take from 258px
  rasters while reporting `fellBack: 0`; and `signalsOnce` caches a failed
  WebGL probe for the page lifetime, pinning the pool to `FLOOR_POOL_PX` for
  the rest of the session. Both are visible-quality, neither is a crash.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C90 · 2026-08-10 · [AXIS:WELL] THE ROLL YOU LIKED, BROUGHT BACK** — wish
  `83c15771` (bug, collage/layout, anonymous): *"Need an undo button for quick
  recall on quickly — rolling the dice in full view."* Full bleed puts the dice
  under your thumb precisely so you can roll it again and again to compare
  layouts, and **every press destroyed the one before it**: fifteen setState
  calls land at once and the composition you were looking at three seconds ago
  did not exist anywhere.
  **WHAT A STEP IS.** A destructive COMPOSITION EVENT — the roll, the shuffle,
  the remix, an applied code — not every setState, or one drag of the chaos
  slider would put fifty entries in the stack and undo would walk you back
  through a slider instead of back to a picture. The snapshot is taken at the
  MOMENT of the action off the LIVE state, so a nudge between two rolls rides
  along inside it: roll, tweak the gutter, roll, undo -> your tweaked version.
  **WHAT IT COST.** Almost nothing, because `rollCode.ts` already made the
  composition a round-trip-exact string: a step is that string plus the two
  things a code deliberately omits (the fragments pinned by hand, the recipe
  name). Undo restores a COMPOSITION, never a pool — clearing your images is not
  an undoable step and this does not pretend it is. Undo+redo in the full-bleed
  rail (where it was wished from), the same pair under the dice in the dock (the
  dock's dice had the identical problem — the sibling sweep), Cmd-Z / Shift-Cmd-Z
  / Ctrl-Y everywhere else.
  **WHAT THE PHONE ENGINE CAUGHT THAT READING DID NOT.** The keyboard guard
  bailed on any focused `INPUT` — and a range slider, a colour swatch and the
  file input are all `INPUT`. Undo would have been DEAD for the rest of the
  session after any slider drag, silently. Only a control with TEXT in it has an
  undo to defend (SCAR above).
  **PROOF. 569,253 invariant checks · 0 failures**, centred on an ORACLE: a
  reference model of the obvious shape (one tape plus a cursor) driven through
  **160,000 random operations** alongside the shipped past/future pair, both
  asked after EVERY operation what is on screen and which buttons are live — two
  different data structures reaching the same answer, which is the only reason
  the comparison proves anything. Then **6 e2e driving the real UI, 72/72 green
  across Chrome, Android Chrome and iOS Safari at four repeats each**, because a
  unit sweep grades arithmetic and cannot see wiring (C87b). The rail went from
  five children to seven, so the mobile law is asserted where it bites:
  **320/360/390/430 and zoomed out — zero horizontal overflow, seven 44px
  targets, none overlapping, none past the edge** (seven targets is 295 of the
  304 usable pixels at 320, which is why the GAP tightens below 360 and the
  buttons never do). Re-run against the LIVE deploy: **21/21 green.**
  **AND THE RULER WAS WRONG BEFORE THE APP WAS.** The first red — "same size,
  same luma, different hash" — was the witness, not the feature: a composition
  carrying a MOVE mounts the live Stage canvas and a drifting canvas renders
  different pixels every frame. Measured: 20 readbacks of an untouched preview ->
  **1 distinct hash still, 6 drifting**, while a 256-block signature -> **1 in
  every case and still 10 distinct signatures from 10 rolls**. Three scars
  above. **BACKPORT RIDER FIRED:** the identical defect was live in
  `tests/e2e/roll-code.spec.ts` (the only sibling sharing the pattern — grepped,
  not assumed), where it had been failing about one run in five for this exact
  reason; fixed there in the same cycle, 20/20 green.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C93 · 2026-08-10 · [AXIS:WELL] THE EXPORT SAID TWELVE PHOTOS CAME BACK FULL
  AND RENDERED THEM AT 200px** — wish `c39685fa` (bug, collage/export,
  anonymous): *"once it reaches a recursive threshold you shouldn't be trying to
  load the high resolution in each frame ... so that higher resolutions don't
  crash but allow really powerful machines to do it."* The CRASH half shipped in
  C87–C89. This is the QUALITY half, and it is the two defects C89 wrote down as
  **verified real, not fixed here** — which is the whole reason that habit
  exists.
  **AN UN-DECODED PREVIEW IS NOT A FLOOR OF ZERO.** `beginOfflineRender`
  repoints every fragment's still key from its preview to its ORIGINAL before
  the budget runs, so a preview decode still in flight lands on a key nothing is
  listening to. The floor a budgeted raster may not go under is read off the
  still currently bound — none — so it came out 0, which reads as "this fragment
  draws nothing, anything is an upgrade". Under a starved pool that adopted a
  postage stamp, pinned the fragment to it for the whole take (its preview can
  never arrive now, the key is orphaned) and reported the source as FULL. Drop
  photos in and hit Export and that is the ORDINARY path, not a corner. Unknown
  is now its own value and admits ONE size: the raster the budget did NOT
  choose. An unclamped raster is bounded by the source or by the sampling the
  destination can show, so it cannot be softer than any preview of that source —
  and refusing sends the fragment back to the preview that was always on its way
  instead of pinning a stamp. Two of the three cases still yield a real number,
  and the second is free: the decode may have LANDED after the repoint.
  **MEASURE THE ANSWER, NOT THE FAILURE.** `deviceSignals ??= readDeviceSignals()`
  cached a blank WebGL probe as a permanent verdict. `getContext('webgl')`
  returns null transiently for reasons that say nothing about the device —
  Chromium evicts the oldest context past its per-page cap, a GPU-process crash
  blanks every one until it restarts — and a blank verdict is `FLOOR_POOL_PX`,
  the smallest pool there is, for the REST OF THE SESSION. Measured: **9.8x the
  pool**, 15 MB instead of 149 MB. Cached only once it carries something, with a
  bounded retry: without the retry a blip is permanent, without the settle a
  WebGL-less realm probes forever.
  **BACKPORT RIDER FIRED, AND IT FOUND THE WORSE ONE.** Swept the codebase for
  the same class: `??=` now appears nowhere in `src`, but the SAME WebGL probe
  lives spelled longhand in `exportLimits.ts`, and its copy is worse. The retry
  alone would have fixed nothing there — `probeBudgetAreaPx` only consults the
  GPU where `deviceMemory` is absent (Safari, iOS, Firefox), a blank falls
  through to `SAFE_FLOOR_AREA*4`, and THAT is the ceiling `probeMaxArea`
  searches up to, so the measurement is a fact about the guess. `probeMaxCanvas`
  then wrote it to **sessionStorage as `source:'probe'`**, indistinguishable
  from a real measurement, where `readCache` accepts anything clearing the
  floor — and it runs once per session, so the retry never got a second chance.
  One blank probe as the export sheet opened deleted the top of the size ladder
  for the whole browser session AND SURVIVED THE RELOAD that would have cured
  it. A measurement taken while the class is merely UNKNOWN is now provisional:
  neither persisted nor memoised, bounded by the same settle. Reproduced on HEAD
  (persists 4.2MP as `source:'probe'`, 1 write) vs fixed (0 writes).
  **PROOF. 5,660 invariant checks · 0 failures** against the REAL transpiled
  modules. The unknown-floor rule is swept as one TOTAL specification rather
  than case by case — `rasterDims(…,null,…) === rasterDims(…,0,…)` when that
  result is unclamped and `null` otherwise — over 80 seeds × 6 source shapes ×
  starved and generous caps: 192 adopted, 208 refused, and **the narrowest
  raster a floor of 0 would have adopted and reported as FULL was 59px.** The
  probe-cache sweep runs under node precisely because there is no WebGL there —
  the failure mode under test, permanently and for free — on a fresh module
  instance per scenario, because the thing under test IS module-level mutable
  state.
  **AND THEN THE WIRING, BECAUSE A SWEEP CANNOT SEE WIRING (C87b).** Every
  existing case waits 1200ms for thumbnails to bind, which is exactly why all
  four passed and none could see this. B5 HOLDS the preview decodes instead —
  deterministic, not a race — and asserts `heldPreviews === 12` FIRST so the
  case cannot quietly degrade into B1. On HEAD it reproduces the defect verbatim:
  `full 12, fellBack 0, clamped 12` at ~200px per photo. B6 is the half a
  too-simple "refuse when unknown" fix would fail: a generous pool must still
  upgrade, `clamped 0`. **24/24 across Chromium, Mobile Chrome, Mobile Safari
  and WebKit-desktop**; every other unit sweep re-run unchanged. Live:
  **28/28 mobile-watertight against the deploy** at 320/360/390/430 and zoomed
  out, and **4/4 export tests driving the deployed UI**, one of them end to end
  to a 2488×3732 file. The live bundle hash matched the local build both times.
  **STILL OPEN, VERIFIED REAL BUT LATENT** (the same habit, paying forward):
  `hydrateSessionAssets` (session.ts) manufactures `width: 0` for a manifest
  entry with no usable intrinsic size, where every other pool door fails closed
  — reachable only from a session persisted by a build older than the
  `project.ts` door fix, and it would render a hole that `render.worker` counts
  as drawn. And `span: 0` carries two meanings into the offline mixer ("unknown
  duration" and soundtrack's deliberate "no picture to agree with"), which for a
  TRIMMED clip routes around `audibleEnd`/`spanLimit` into the re-normalisation
  `clipWindow.ts` documents as catastrophic — unreachable through the app today,
  but `durationSec` is optional in the public `StageClipInput` type while
  `inSec`/`outSec` are too. Neither is this cycle's fix; both are written down
  so they get one.
  **NOT SHIPPED FROM THIS WISH, AND SAID PLAINLY:** the stencil half — upload a
  photo of a grid, detect the shapes, emit SVG slots to drop photos and video
  into. That is its own tool, not an export fix.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C96 · 2026-08-10 · [AXIS:WELL] THE ONLY CUT OF A SONG THIS APP COULD PLAY
  WAS THE FIRST N SECONDS OF IT** — wish `f6cbf511` (bug, collage/audio), the
  oldest unserved row in the well: *"The audio import is cool. Need a way to
  click it and select the range and also looping image movement is the
  default."* Both halves shipped.
  **THE RANGE IS THE SHEET THAT ALREADY EXISTED.** A soundtrack is a clip with
  no picture — the file has said so since the day it was written — and the
  second instance of a shape is where this project extracts the engine instead
  of forking a page. So `TrimSheet` stopped taking a `LiveClip` and started
  taking a NAME and a SPAN, and the music chip got the same Scissors button, the
  same two native handles, the same focus trap, the same
  both-handles-stop-at-each-other rule a ratcheting OUT point taught it, and the
  same "All" reset. Zero new UI vocabulary; `SOUNDTRACK_ID` is minted so it can
  never collide with a clip id, which is what lets ONE `trimming` slot hold
  either and keeps the only-one-sheet-open invariant free.
  **AND THE STRIP STAYED HONEST.** The tempting move for audio is a waveform,
  which means decoding the whole file to draw a control — precisely the second
  decoder the sheet's own comment refuses ("the difference between a trim UI
  that works on a phone with three clips open and one that evicts a live decoder
  to draw itself"), on the one import most likely to be a 5 MB song on a phone.
  A track with no frames gets a RULER instead: minute marks on the same time
  axis, which is the actual question you ask a song.
  **THE BURIED PART IS THAT `span: 0` IS WHAT MAKES A RANGE ON MUSIC CORRECT.**
  C93 wrote this down as latent and named the trim as the case that would reach
  it. The user authors the range against the CONTAINER duration — the number the
  probe reported and the max of the OUT slider — while the mixer resolves it
  against the DECODED buffer, and an mp3's two lengths differ by the encoder's
  delay and padding in either direction. Handing `durationSec` over as the span
  to "help" the window sets OUT a hop PAST `buf.duration`, and `audioSchedule`
  reads a window ending past the sound as the audio ENDING INSIDE the picture's
  window: the LAPPED plan, one non-looping node per lap, a sliver of silence cut
  into every repeat forever. With `span: 0` the mixer falls back to
  `buf.duration` itself, OUT is clamped to real sound, `audibleEnd` equals OUT by
  construction, and the straddle branch is UNREACHABLE for music. The hazard is
  closed at the source rather than downstream. **`outSec === durationSec` is not
  a corner case — it is what "from the drop to the end" produces on the first
  drag.**
  **PROOF, THREE WAYS.** (1) 45,719 unit assertions against the REAL transpiled
  modules, over 30 ranges × 5 container lengths × 5 decode hops (0, ±26 ms, ±104
  ms) × 3 take lengths, modelling the mixer with the real `normaliseWindow` +
  `audioSchedule` rather than a paraphrase: never `silent`, never `lapped`, never
  `truncated`, one node, `loopEnd` inside the buffer, and `schedulePositionAt`
  inside the chosen window at 41 instants per case. **The contrast case is
  asserted to REPRODUCE the defect** (`lappedWhenHelpful > 0`) — pass the
  container duration as the span and the same user range laps — so I5 proves
  something rather than describing it. (2) T6 at the artifact: a new
  `music_thirds.m4a` fixture, 6 s in three 2 s thirds at 900/1500/2300 Hz (a
  single-tone fixture measures identically whether the range was honoured or
  ignored), trimmed to the middle third, exported, decoded: **1500 Hz = 0.10969,
  900 Hz = 0.00011, 2300 Hz = 0.00012, control 0.00004** — the parts you cut are
  ~1000× down and the take ran 5.01 s, so the 2 s window LAPPED. (3) The LIVE
  timeline, because a range you can see in the file but cannot hear in the
  monitor is the preview/export split this repo is scarred by wearing a new hat:
  30 samples of the real `<audio>` element must all sit inside 2→4. **Negative
  control run:** with the watchdog stubbed out it plays 0.47 → 3.40, straight
  through the third the user cut, and the assertion fails.
  **THE WATCHDOG DIVERGES FROM THE CLIP PATH, DELIBERATELY.** A trimmed clip is
  held from `tick`, on frames the compositor is already drawing. Music is the one
  source that can be playing while nothing is drawn at all — a still collage with
  a soundtrack and no clips is an ordinary state — so it is held from the
  element's own `timeupdate` as well, and native `loop` STAYS ON where a clip
  turns it off: a paused element in a background tab needs a `play()` inside a
  gesture that ended long ago, and a fraction of a second of intro once is a
  better failure than silence that needs a tap to fix.
  **THE SECOND HALF OF THE WISH.** Adding music is the one import that can only
  mean "this is a video now", so the collage starts DRIFTING — but only when
  nobody has chosen a move, because `'still'` is both the default and a real
  answer, which is what `moveOwnedRef` is for; the move control and the dice both
  claim it, a restored session does not (sessions never carry the soundtrack). The
  notice says what changed, because a control that moves on its own without
  saying so is the same defect as one that reads back the wrong state.
  **SWEPT:** the same-url door in `setSoundtrack` updated only `muted`, so every
  drag of the IN handle would have reached the export and not the monitor — the
  one door built to prevent a preview/export split, reintroducing it. Fixed in
  the same edit. Full soundtrack suite 6/6, clip trim suite 9/9 (the `TrimSheet`
  refactor), mobile-watertight 7/7, video-audio-export 4/4, all 17 unit sweeps
  green, `tsc --noEmit` clean.
  **NOT SHIPPED, AND SAID PLAINLY:** no waveform (see above), no fade in/out at
  the range edges, and the range is not carried in a saved project or share code
  — the soundtrack has never been, and adding it is a format change that deserves
  its own cycle rather than a rider on this one.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-10 · **[AXIS:WELL] THE COLOUR DICE — roll the colour sort and the crop,
  keep the layout** (well read UNSCOPED across all trades first: 2 new, 0
  stranded in `building`; one `bug`-kind row on collage/layout, and bugs
  outrank every roadmap — so the stalest-axis signal, DEPTH, yielded to it.)
  before→after: **the only way to try a different colour sorting was to roll the
  shape away with it → one press re-sorts and re-crops and the layout does not
  move.** Wished for verbatim: *"Add another dice for color sorting and cropping
  style. For full view for better ui/ux."* The dice this app already had
  replaces the WHOLE composition — which is what makes it worth pressing and
  exactly why it is useless the moment you like what is on screen; the
  arrangement, focus and twist rosters (wished into being by the same person,
  first entry in the collage ledger) lived only as thirty-two chips in the
  Advanced panel, which on a phone in full bleed is not a control that exists.
  `lib/dealRoll.ts` rolls those three and NOTHING else: layout, count, chaos,
  aspect, gutter, background, zoom, grade, motion and above all the SEED — the
  seed drives the subdivision, so rolling it would move every fragment edge and
  the button would quietly be the first dice again. It never returns `natural`
  (the unsorted order is not a colour sort) and never the deal already on
  screen, guaranteed by a single deterministic step rather than a redraw loop
  that could take unbounded draws off the stream. One family table, two dice:
  `arrangementFor`/`twistFor` gained weight parameters instead of a second copy
  of the lean, and the main dice's own spread is unchanged (`natural` 18%).
  PROOF: `tests/unit/dealRoll.invariants.mjs` — 1,104,000 CHAINED rolls (every
  generator x 400 seeds x 120 presses, each result fed back as the next
  `previous`, because that is how the field presses it), 1,800 forced
  collisions, 920 replays, 0 failures. `tests/e2e/colour-dice.spec.ts` — 9/9 on
  Chrome, Android Chrome and iOS Safari, asserting "the layout did not move"
  against the COMPOSITION CODE rather than by reading the controls back (which
  would agree with the wiring by construction), and asserting the roll reaches
  the pixels via a block fingerprint. MOBILE: this is the rail's seventh 44px
  target and six were already 295 of the 304 pixels a 320px phone has, so the
  pill now wraps below 390 — the four buttons that MAKE a picture on one row,
  the three that navigate between pictures on the next — asserted at 320 / 360 /
  390 / 430 with zero horizontal overflow, every target ≥44px, nothing off an
  edge and no two controls overlapping. Regression: undo 21/21, mobile
  watertight 7/7, rollCode + composition + twist sweeps green, `tsc --noEmit`
  clean, `vite build` clean. Credited on the page under the button itself and in
  BOTH ledgers. **BACKPORT RIDER FIRED:** the class this exposed is *a control
  row with a fixed number of 44px targets and no room for the next one*, so all
  7 trades were swept for it on the LIVE site — 56 measurements (7 trades x 4
  pages x {320, 390}) — and came back CLEAN: zero horizontal overflow anywhere,
  smallest visible sticky-bar control exactly 44px. `shared/toolkit.js` already
  answers the class by degrading the brand instead of wrapping; that was written
  down but had not been re-measured since the trade count reached 7. **NOT SHIPPED, AND SAID PLAINLY:** the colour dice is not in the
  keyboard map (the main dice is not either), and it does not appear in the
  share code as a distinguishable act — a code records the deal, not which
  button produced it, which is correct and worth stating.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-11 · **[AXIS:COLLAGE] THE FADE — the take stops sounding like somebody
  pulled the cable out**
  (well empty — 0 new, 0 stranded in `building`, read UNSCOPED across all trades
  first; breadth debt 0, so LIVE STATE's stalest-axis rule governed and it named
  COLLAGE.) before→after: **every export began at full level on sample zero and
  ENDED MID-BAR → the sound rises out of silence and settles back into it, over
  0.5s, 1s or 2s, on one tap.** `mixSources` renders exactly
  `ceil(seconds * 48000)` samples and hands every one to the encoder, so the last
  sample of a 5 s take was whatever the song happened to be doing at 5.000 s —
  which is what a hard cut IS, and the Audio rung has named a fade as the first
  thing owed since THE SOUNDTRACK shipped. `lib/fade.ts` is one linear envelope
  with TWO emitters, and the count is what set the design: the offline renderer
  holds the whole mixed buffer and multiplies through it (`applyFade`), while the
  realtime MediaRecorder fallback encodes a LIVE graph through `captureStream`'s
  tap on `masterGain` and has no buffer to walk at all, so the same shape has to
  exist as `AudioParam` automation (`Stage.applyTakeFade`). LINEAR is therefore
  not a compromise but the enabling decision — it is the only shape both sides
  express exactly, where an equal-power curve would need `setValueCurveAtTime`
  with a sampled table on one side and a closed form on the other, i.e. a fade
  that is measurably not the same fade depending on which recorder your browser
  gave you. **The load-bearing decisions, in order of what they cost to get
  wrong:** the fade runs AFTER the true-peak limiter, and the order is safe in
  both directions of the argument only that way round — the envelope is ≤1 so it
  can never breach the ceiling, and limiting first stops the take's ENDS from
  setting the level of its middle (fading first would let a peak inside a ramp
  lower the measured peak, the limiter would scale by less, and switching a fade
  on would make the untouched middle LOUDER); `fadeSpan` clamps the request to
  `take/2`, which makes "a fade longer than the take" unrepresentable rather than
  merely tested; `applyFade` walks only the two ramp REGIONS, so the bound is a
  value the sweep asserts rather than a property implied by arithmetic; and OFF
  is the default, so every export made before this exists is still reproducible.
  It lives beside the take LENGTH — same state, same bar, same lifetime — and
  therefore rides in **no** dice roll, **no** composition code and **no** project
  file, because a fade is a fact about a render and a `?c=` code is a recipe
  somebody else opens with their own music. UI is ONE 44px chip that cycles
  OFF→0.5s→1s→2s, in the scroll row rather than the fixed one: the take bar is
  already eleven controls and a second four-chip group there is exactly the scar
  the colour dice left in the trades' rails. It is offered only when the take
  will carry sound at all (`willCarrySound`), because a control that provably
  cannot change the file is the inert-control defect this component has been
  filed against four times.
  PROOF: `tests/unit/fade.invariants.mjs` — **708,601 assertions**: 176,088
  envelope points across 88 (take, fade) pairs where the sample-domain envelope
  and the ramp schedule read back through `rampGainAt` must agree pointwise,
  99 clamps, 264 region tilings, **2,160,000 samples proven `Object.is`-identical
  with the fade off**, 9 faded buffers checked sample-by-sample for an untouched
  middle and for never-louder, 25 garbage inputs. MUTATION-TESTED, which is the
  part worth keeping: 8 deliberate defects injected into the shipped module,
  **7 killed** each on the assertion written for it — and the 8th (`up * down`
  for `min(up, down)`) SURVIVED as an EQUIVALENT mutant, which is the clamp's
  payoff stated as evidence rather than as prose: under `f ≤ take/2` one factor
  is always exactly 1, so the two spellings are the same function, and removing
  the clamp is what makes them differ. `tests/e2e/fade.spec.ts` at the ARTIFACT,
  by DECODING the exported MP4 and reading its envelope 20 slices deep — fade
  OFF `79999999999999999999` (flat), fade ON `01345678999997654321` (the 2 s
  trapezoid), **worst point-by-point deviation from a hand-written `min(t/2,
  (5-t)/2, 1)` = 0.024** against a 0.12 tolerance, and **plateau ratio
  faded/flat = 1.000**, which is the limiter-order claim measured rather than
  argued. That point-by-point assertion is the one that carries the test: quiet
  ends and monotone ramps are both invariant under the ramp LENGTH — a 1 s fade
  passes every other assertion in the file — the same lesson `trim.spec.ts` wrote
  down when duty cycle and longest-silence both scored a one-second-late render
  as perfect. MOBILE: F3 drives the real chip at 320/360/390/430, asserting zero
  horizontal overflow, ≥44px in both axes, no ancestor clipping, AND that a tap
  actually changes the value at every width. REGRESSION: soundtrack 6/6, trim
  9/9 (straddle still reads `####........####....` digit for digit, so the
  `toneEnvelope` move is behaviour-preserving), video-audio-export 4/4, fade 2/2,
  `tsc --noEmit` clean, `vite build` clean. **EXTRACTION RIDER:** `toneEnvelope`
  — the only measurement in this repo with a TIME AXIS — lived inside
  `trim.spec.ts`, so this cycle's suite would have been the third Goertzel in the
  tree; moved into `tone-measure.ts` beside `measureTones` on its second caller,
  per the extract-the-engine rule. **NOT SHIPPED, AND SAID PLAINLY:** the fade is
  SYMMETRIC (one control sets in and out together — a long tail under a short
  head is the next rung); the realtime `record()` path's fade is proven
  STRUCTURALLY (same pure function, ramp schedule asserted against the envelope)
  and NOT at the artifact, because every engine in this suite has WebCodecs and
  therefore never takes that path; and `mixSources`' two lines that hand the
  buffer to `applyFade` are still guarded only by a whole browser render, which
  is the fake-`OfflineAudioContext` rung the ladder has been carrying since the
  lap schedule.
  **THE ADVERSARIAL AUDIT EARNED ITS KEEP AGAIN — three lenses, THREE CONFIRMED
  DEFECTS, every one of them in the half of the feature this suite cannot
  reach.** All three lived in the REALTIME path or in a short-stopped render,
  i.e. exactly where "chromium has WebCodecs so it always takes the offline
  branch" made the gates blind: (1) the envelope was anchored at the CALL SITE
  of `record()`, which awaits a ~1.9 s dry run before `rec.start()`, so the
  file's tail recorded at gain 0 — fixed with a new `RecordOptions.onStart` hook
  that fires the instant the recorder really starts; (2) `clearTakeFade` was
  bound to the recorder's PROMISE (which settles only after stop + finalize +
  validate) rather than to the end of the take, and `masterGain` is the MONITOR
  bus as well as the capture tap, so the live preview sat in silence for seconds
  and then stepped back to full level — fixed by scheduling the monitor's
  recovery into the same atomic automation, a beat after the take and as a ramp
  rather than a step; (3) a render that stops early has `truncateAudio` cut the
  audio where the envelope is still 1.0, so the file ends at full level while
  the bar still promises a fade — unfixable after the fact and therefore
  REPORTED, the rule `mixSources`' `onTruncated` already follows one layer down.
  Filed as ONE scar, because (1) and (2) are the same mistake twice: **a promise
  settling is not the event happening, and the call site of an async function is
  not the moment it starts.** Live-verified on production BEFORE the fixes
  (fade off `79999999999999999999`, fade on `01345678999997654321`, worst delta
  0.024, plateau ratio 1.000) and again after them.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C126 — [AXIS:COLLAGE] THE PLAYHEAD — the take gets a clock you can see and
  drag.** BEFORE: six cycles of time-domain work — THE MOVE, the trim window,
  the music range, the lap schedule, THE FADE — and not one of them observable
  without spending an export; the live preview had no beginning, no end and no
  position, so "does the fade-out land where I think it does" cost a render and
  "what does this look like at seven seconds" was unanswerable. AFTER: a ruler
  over the take in the transport bar, a position that tracks the clock, a drag
  (or an arrow key) that parks the WHOLE composition on any instant of it, a
  `m:ss.d / m:ss.d` readout, and the fade drawn under it as its own two
  triangles from `fadeSpan` rather than from the number on the chip.
  THE RUNG PICKED ITSELF: two separate ladder entries asked for the same widget
  in the same words — the timeline rung owed `playhead scrub`, and THE MOVE's
  own rung said "the honest next cut is a scrub or a 'show me' that runs one
  cycle, which is the same widget the timeline rung wants anyway." One bar
  closed the second outright and half of the first.
  THE SEAM: `lib/playhead.ts` owns the arithmetic (ruler, lap, seek grid, fade
  marks, the seek PUMP) and the Stage owns the seek, which it already had —
  `renderAtTime` is what the offline exporter walks the take with and it reads
  `this.offline` exactly ZERO times, so a scrub borrows it whole without
  entering the render mode and inheriting its lifted decoder caps, frozen
  backing size and full-resolution rasters. **THE CLOCK LAPS, A SCRUB SEEKS:**
  wrapping the readout over an unwrapped clock would have the bar claim 7s while
  the move sat at phase 37 (the move is periodic on a fixed 12s, deliberately
  not on the take), so the clock itself wraps — but the lap re-seeks NOTHING,
  because restarting every source at a boundary changes what every preview this
  app has ever shown, and this book's own precedent (the end-of-take hard cut,
  deferred for exactly that reason) says that is a decision to make on its own
  and not a rider on a feature. Filed as two open rungs instead.
  PROOF, at the artifact and by pixel: `ramp_rgb.mp4` is 6s in three flat
  thirds, so a seek can be GRADED — scrubbing to 1.0/3.0/4.5s shows r/g/b in
  that order, the parked canvas hashes IDENTICAL across 1.1s of wall clock (a
  park that holds), and Play resumes at >2.9s after a park at 3.0s rather than
  from the top. Repeated at 390px with the same three colours, because a tap
  target that is big enough and changes nothing is not a control.
  SWEEP: `tests/unit/playhead.invariants.mjs`, 54,337 assertions — 400 seeded
  pump interleavings, 2,880 lap adjustments, 252 origin round trips through the
  tick's own expression spelled verbatim, 1,216 range-input readings, 3,600
  snaps, 84 fade rulers, 64 garbage pairs. **MUTATION TESTING EARNED ITS KEEP
  AGAIN: 15 injected defects, 13 died on the first pass and the two that
  survived were both comments the sweep was asserting AROUND rather than
  THROUGH** — and the arm written to kill the first of them then went red
  against the REAL module and found a defect neither mutant had (see
  SCAR-C126-A-BOUNDARY-MUST-BE-REACHED-THE-WAY-PRODUCTION-REACHES-IT).
  RIDER FOUND ON THE WAY PAST: the Play button was `disabled={liveCount === 0}`
  and its icon read `clips.some(playing)`, so a photo collage drifting under a
  soundtrack showed Play while the picture moved and could not be started or
  stopped at all — the SAME question `takeable` was invented to fix for the
  sound button three lines above it. `StageStatus.rolling` answers from the
  Stage now. Filed as SCAR-C126-A-CONTROL-THAT-ASKS-WHICH-SOURCES-EXIST.
  REGRESSION (the changed tick, the parking Pause and the rewired transport are
  what put these at risk): motion 5/5, trim 9/9 (including the 11s live watch
  that the lap would have disturbed had it re-seeked), soundtrack 6/6,
  source-count 7/7, video-audio-export 4/4, playhead 2/2, `tsc --noEmit` clean,
  `vite build` clean.
  NOT SHIPPED, AND SAID PLAINLY: the ruler shows the take and nothing IN it (no
  clip extents, no trim windows); a still collage under music has no clock at
  all, because the tick it rides is demand-driven and photographs do not demand
  frames; and scrubbing is silent — a park stops the audio rather than scrubbing
  it, which is the one thing a real NLE does here that this does not.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C141 — [AXIS:COLLAGE] THE TURN — the collage CUTS, and every cut is a
  permutation** — before: six cycles of time-axis work (the move, the trim, the
  music range, the lap schedule, the fade, the playhead) and the pictures had
  never once changed fragment; a twenty-second export was ONE deal held for
  twenty seconds, breathing. The fundamental verb of an editor — the cut, one
  shot becoming another — did not exist in this app at all. After: five modes on
  one chip row (`hold` / `march` / `scatter` / `ripple` / `swap`), and every few
  seconds the photographs land in different fragments and cross-dissolve on the
  way, in the live preview and in the exported video.
  THE DESIGN IS THE INVARIANT. `lib/turn.ts` composes STEP permutations, so by
  induction every reachable state is a permutation of the deal and two fragments
  can never hold the same photograph — which is how a time axis was added
  without voiding the source-first duplicate-free promise `lib/fill.ts` has made
  since the beginning. That constraint is also what ruled out the obvious first
  design: a stagger over a global rotation is injective only if the turned set
  is closed under +1, which cyclically forces ALL or NONE, so `ripple` takes its
  stagger by rotating one parity HALF among itself instead. Measured at the
  artifact across exactly one cut: ripple moves 41.1% of the frame, march 93.2%
  — the roster is structurally different, not four chips wired to one behaviour.
  A TURN CHANGES WHICH PICTURE, NEVER WHERE, which is what kept it off
  `computeLayout`, out of the SVG geometry and out of `refreshAdmission` (a
  fragment holding a live clip is a fixed point of every permutation, so decoder
  ranking stays a scene-time decision). The seam is one callback,
  `resolve(slot, fromSlot)` — the face and the colour travel with the
  photograph, the focus, twist and move stay with the cell.
  PROOF, unit: 13/13 invariants including 65,600 assignments proved to be
  permutations across 5 modes x n=1..64 x 5 seeds x k=0..40, rest returned by
  reference, and forty rebuilt pre-turn codes still opening as `hold` with every
  other field unmoved. PROOF, artifact: 6/6 Playwright tests on the real page —
  and T3 is the one to read, because the hue census literally rotated
  (10.7/16.8/11.5/20.2/25.6/15.1 -> 11.4/20.2/14.9/10.9/17.0/25.7): the same six
  photographs, the same six shares, in a different order. That is the
  permutation, observed in pixels. The exported JPG differs by <= 1 level with
  `scatter` running, so the three single-frame surfaces never saw it.
  THE AUDIT IS WHAT MADE IT TRUE, and this is the cycle to point at when
  somebody asks whether the adversarial pass earns its cost. Four independent
  lenses over the diff, each finding refuted by a separate skeptic. It returned
  THREE real defects that six green e2e tests, a 65,600-case permutation sweep
  and a LIVE DEPLOY had all passed with in: a dissolve that could never end
  (`mix` stuck at 0.9944 forever, which froze the MOVE — invisible because the
  two pictures either side of a completed cut are the same photograph), a scene
  prop built inline in JSX that restarted the take clock on every unrelated
  render (the feature would never have fired in a real session), and a "legacy"
  fixture that had been taught the new field and so stopped being legacy. All
  three are filed as scars above, all three are fixed, and both of the serious
  ones now have a guard that would have caught them — `turn.invariants.mjs` I10
  (the consumer state machine replayed at three frame rates, WITH a red proof
  that the broken shape fails it) and `turn.spec.ts` T7 (a drift measured
  surviving a cut on real pixels). T7 also cost the fixture a redesign: the hue
  census wants flat tiles and a move needs structure, and the two are reconciled
  by putting every variation in BRIGHTNESS, which the direction-based classifier
  is invariant to by construction.
  REGRESSION (the draw loop, the tick gate and `renderAtTime` are what put these
  at risk): motion 5/5, playhead, source-count, one-layout, session-recovery
  24/24, plus
  every unit sweep in the tree green — rollCode 207,028 checks (it now covers
  `turn` in sections 1/2/3, which is more than `look` or `move` ever got there),
  grade 46,987, clipWindow 5,450,896, fade 708,601, fill 368,962. `tsc --noEmit`
  clean, `vite build` clean.
  NOT SHIPPED, AND SAID PLAINLY: the LAYOUT does not change at a cut, only the
  deal; the hold is a property of the mode so "cut faster" is not askable; a
  collage that is mostly video has little for a turn to move and nothing says
  so; and a lap in the live preview snaps the wall back to its base deal with no
  dissolve, because the schedule is deliberately periodic on a fixed hold rather
  than on the take — the exported file, which walks 0 to L monotonically, never
  sees it.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C144 — [AXIS:COLLAGE] THE PACE — the roster said what SHAPE, it never said
  how fast** (well read UNSCOPED first: 0 new, 0 stranded in `building`, across
  all trades; breadth debt 0, so LIVE STATE's stalest-axis rule governed and it
  named COLLAGE.) before→after: **"cut faster" was a request for a different
  PERMUTATION → it is a request for a different tempo.** Two rungs of the ladder
  had filed the same gap in the same words — the turn's hold is a property of
  the mode (`march` 5s, `ripple` 3.5s, change one and you change the other) and
  the move's 12s cycle is a constant with no control at all — so both rosters
  were answering two questions with one chip. Five chips
  (**0.5× · 0.75× · 1× · 1.5× · 2×**) now scale the clock the move and the turn
  are read against, on the dice and in the composition code, and the shape
  rosters finally answer only the question they are good at.
  THE DESIGN IS ONE SENTENCE AND ONE REFUTATION: **scale the CLOCK, not the
  PERIODS.** Dividing each mode's hold by the rate is the obvious build and it
  degenerates, because `TURN_FADE_SEC` is a constant that does not divide with
  it — `ripple` at 2× would hold 1.75s and still dissolve for 0.7s of it. The
  sweep implements the rejected design ONLY to measure it failing: the shipped
  one holds march/scatter/ripple/swap at **13.6 / 10.5 / 19.5 / 17.0% soft at
  EVERY rate**, the rejected one takes ripple from **20.0% → 39.0% at 2×**. That
  invariance is also why the control needs no clamp: there is no rate at which
  the schedule degenerates. `lib/pace.ts` is ~30 lines of logic; the Stage
  applies it at exactly two seams (`refreshTurn`, `crop`) and NEVER to `outTime`
  itself, because the take's own clock is what the ruler shows, what the
  exporter walks and what every audio schedule is written against. Rest at zero
  survives for free (`0 * r` is 0), so the still preview, the raster export and
  the SVG are bit-identical to a build without the file.
  PROVED WITHOUT A CLOCK, which is the other half of the method: `renderAtTime`
  is a pure function of the instant — that is why the offline exporter can walk
  it — so the e2e SCRUBS instead of waiting. march holds 5s, so at 1× the wall
  at t=3.0 is **0.0% moved, worst channel 0/255** from its opening frame; at 2×
  the same instant reads 6.0s and moves **94.5%, worst 202/255**; at 6.0s the
  two swap places, 0.5× reading **0.5% / worst 29** where 1× reads **94.5% /
  worst 202**. Three rates, same pixels, no timer anywhere — measured against
  PRODUCTION, and a scrub is the export's own path, so it is evidence about the
  file. (The CUT magnitude is a random variable and re-runs read 94-96% / worst
  ~200, because the layout is generative and each boot deals differently — the
  scar about whole-canvas measurements applies. The HOLD is not a random
  variable: 1× at 3.0 s reads 0.0% / worst 0 every time, because rest at zero is
  an identity rather than a tolerance.) Both mutations red: neutering `paceTime` and cutting the Stage seam each
  fail P1 (the seam mutation with `worst 0` — the picture literally identical).
  AND THE SCREENSHOT CAUGHT WHAT NONE OF THAT DID. Looking at the live page at
  390px afterwards, the chosen `2×` chip was not green: `:hover` out-specifies
  `[data-active='true']` by one pseudo-class, so **the chip you just tapped
  renders as unchosen** — rgb(31,36,39) against rgb(22,25,27) for one that
  really is unchosen, and on iOS the hover STICKS after a tap. Five of the six
  hover/active families in `controls.css` had it, which is every roster row in
  the app; `.ui-ratio` was right by source order alone. Fixed as a class
  (`:not([data-active='true'])` on all six) with P5 as the guard, and P5 sweeps
  the SIBLING rows — look, move, turn — not only the row this cycle added.
  Filed as three scars: the hover one, the module header that claimed dyadic
  rates are exactly reversible (they are not — 3/4 and 3/2 carry a factor of
  three; the sweep failed on its first run and the claim was corrected to what
  is actually guaranteed), and three sibling sweeps that each pinned the codec's
  group length as a literal `21` and all broke at once — now one exported
  `MINTED_GROUP_MAX`.
  PROOF: 13 invariants (one of them a red proof), 4 e2e green against
  production. Regression: turn 7/7, motion 5/5, playhead 2/2, one-layout 4/4,
  roll-code 20/20 (one T4 flake under parallelism on the first run, green in
  isolation and on a full re-run — not this change), every unit sweep in the
  tree green including rollCode's 207,028 checks, clipWindow 5,450,896, fade
  708,601, grade 46,987, fill 368,962. `tsc --noEmit` and `vite build` clean.
  NOT SHIPPED, AND SAID PLAINLY: it is ONE dial over two independent rhythms, so
  a slow drift under fast cuts is still unaskable; a collage that is mostly
  video has almost nothing for a pace to move and nothing says so; and a clip's
  own playback rate is untouched, which is the `Speed` rung and stays open.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C147 — [AXIS:COLLAGE] THE BEAT — the collage cuts ON THE MUSIC** (well read
  UNSCOPED across all trades first: 0 new, 0 stranded in `building`; breadth
  debt 0, so LIVE STATE's stalest-axis rule governed and it named COLLAGE.)
  before→after: **a collage over a 128 BPM track cut every 5.000 s because
  `march` says 5.000 s → the hold snaps to the music and the wall lands where
  the drums are.** Four cycles had built a time axis and a sound — THE
  SOUNDTRACK, THE TURN, THE FADE, THE PACE — and every clock among them was
  independent of the track, so the picture and the song met by accident.
  **A BEAT SYNC IS NOT A NEW RATE DIAL, IT IS A QUANTISER ON THE RATE ALREADY
  ASKED FOR.** The obvious design is a division roster (every beat / half bar /
  bar / two bars) and it is wrong twice: a fifth chip row on a phone, and the
  two controls that already answer "how often" (the turn's mode, THE PACE)
  become dead weight the moment it is on — the exact defect the ladder files
  against the pace itself. So the mode still says how often it wants to cut, the
  pace still scales that want, and `lib/beat.ts` rounds the result to the
  nearest musical multiple {1,2,4,8,16} of the detected beat. ONE toggle, no new
  vocabulary, every existing control keeps its meaning.
  **NEAREST IN RATIO, NOT IN SECONDS**: with a 0.5 s beat and a 3 s target, 2 s
  and 4 s sit exactly 1 s away on either side — a dead tie on the difference,
  and 1.50x against 1.33x on the tempo, which is the comparison a listener
  actually makes.
  **THE FADE BECOMES A FRACTION OF THE HOLD**, and that is `lib/pace.ts`'s own
  argument arriving from the other side: a pace scales the CLOCK so `fade/hold`
  is invariant by construction and `TURN_FADE_SEC` can stay a constant; a beat
  sync sets an ABSOLUTE hold from outside the roster, and 174 BPM at 2x is a
  1.379 s hold that a constant 0.7 s dissolve leaves **50.7% soft**.
  `turnFadeFor` caps at the roster's own worst ratio and the sweep holds every
  mode at exactly **20.0%** at every tempo (I6, with I6b as the red proof).
  **AND A SYNCED TURN IS NOT PACED** — the pace already went into choosing the
  schedule, and applying it again would scale the clock underneath a grid whose
  whole purpose is to sit at absolute instants the music decides.
  **DETECTION IS A COMB, NOT A BEAT TRACKER**: rectified-RMS onset envelope,
  autocorrelation for a coarse period, eleven musical ratios of it scored by
  comb and resolved by "the SHORTEST period that explains every hit", then a
  fine (period, phase) search. THREE measurement bugs had to be fixed before
  that rule meant anything, all found by the sweep: an interpolated tooth and
  then a max-of-pair tooth both let a comb whose period is a WHOLE NUMBER OF
  HOPS sample only well-aligned onsets and beat the truth (a 180 BPM click track
  measured **60**). The cause is that RMS is a square ROOT of a mean, so an
  onset split between two windows measures genuinely SMALLER rather than merely
  divided; a window twice the hop, stepped by the hop, took the alignment bias
  from **10.3% to 0.8%**. Twelve tempi 60→180 BPM now detect EXACTLY, backbeats
  included, and white noise / silence / junk are REFUSED (a confident wrong grid
  is worse than no sync). One gate was BUILT AND REMOVED after measuring it: the
  "is this phase special" test reads 2.25 where the energy test reads 2.23, on
  every signal tried — it was the same statistic at twice the cost.
  It rides the composition code (23-character group; all six earlier generations
  still decode byte-identically, 240 rebuilt legacy codes) and **deliberately
  NOT the dice** — every other roll re-deals what the collage LOOKS like, and
  `sync` is a relationship to a FILE the dice cannot see.
  PROOF: 19 unit invariants including the ORACLE arm (31,717 checks proving the
  unsynced path is `Object.is`-identical to the build with no beat in it, 12,332
  of them `NO_TURN` by reference) and 20,000-schedule sweeps; **4 e2e assertions
  on production pixels** — 120 BPM found by the real browser from a WAV the test
  built, `march` snapped to 8 beats, and at t=4.8 s the synced wall has cut
  (**93.6% of the frame moved, worst channel 196/255**) where the unsynced one
  is still on its opening deal (**0.2% moved, worst 22**), with all six
  photographs present exactly once; watertight at 320 px.
  Regression: every unit sweep in the tree green, turn 7/7, motion 5/5, pace
  4/4, playhead 2/2, roll-code 20/20 — and `pace.spec` P5, the colour guard the
  C144 hover scar left behind, was extended to the new row IN THIS CYCLE rather
  than in the one that would have broken it (green on production: the chosen
  chip reads `--signal`). `tsc --noEmit` and `vite build` clean.
  THREE SCARS, and two of them are about the PROOF rather than the code: the
  dev server on :5199 had been running since **Aug 8** and its watcher, on an
  external volume, had missed every edit to a file it cached on first request —
  so a red run was measuring code that no longer existed; the arithmetic sweep
  could not see EITHER phase bug because both live in the choice of
  representative inside a symmetry it quantifies over, and the browser found
  both; and two sibling specs that WAIT rather than scrub had no wall-clock
  budget and failed identically against production, i.e. were never this
  cycle's regression. BACKPORT RIDER FIRED: `pace.invariants.mjs` still pinned
  the codec's group length as a literal `22` — the same class C144 filed after
  grade/motion/turn all pinned `21` — so it now reads `MINTED_GROUP_MAX`, and
  the sibling sweeps were swept for the same literal (15 uses, all derived).
  NOT SHIPPED, AND SAID PLAINLY: only the CUT is snapped — the move's 12 s
  cycle, the trim windows and the fade are still on their own clocks; a DOWNBEAT
  is not detected, only a beat, so a four-beat hold lands on some beat of the
  bar rather than on the one; a lap re-phases the music and not the grid; and a
  tonal source with no percussion is accepted at 0.53 confidence because its RMS
  really does rise and fall periodically — the BPM on the chip and the switch
  nobody is holding down are the mitigations, not a cleverer number.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-12 · **[AXIS:COLLAGE] THE SPEED — a clip gets its own clock**
  (well read UNSCOPED first across all trades: 0 new, 0 stranded in `building`;
  breadth debt 0, so LIVE STATE's stalest-axis rule governed and it named
  COLLAGE. Of the ladder's top-level rungs exactly two had never been started —
  Speed and Overlays — and Speed was taken because its seam already existed.)
  before→after: **every clip in a collage ran at exactly the rate the file was
  shot at, and the only thing that could change that was a sync mode that
  rescales ALL of them together → five chips on the clip's own sheet run THAT
  clip at 0.25× / 0.5× / 1× / 2× / 4×, live and in the exported file.**
  `lib/speed.ts` is the roster and the rules; the rate itself enters through the
  ONE `rate` in `clipWindow.sourceTimeAt`, so the live `<video>`, the offline
  frame seek and the offline audio mix all got it without a new seam. The only
  real design decision was the composition with video-length sync, and it went
  INSIDE `computeClipPlayback` rather than being multiplied on by the caller —
  a sync rate and a user speed are the same physical quantity, so two places
  deciding a clip's rate would have left the element clamp guarding the wrong
  number. Consequence, stated in the UI rather than left to be discovered:
  under a stretch mode a speed moves the REFERENCE (the reference is taken over
  `window / speed`), so it cannot make one clip outrun another; under 'loop'
  the rate simply is the speed.
  PROOF, on PRODUCTION pixels, no wall-clock anywhere: a speed is a
  RE-PARAMETERISATION of the clip's own time, so 2× at 1.5 s must be the same
  frame as 1× at 3.0 s — **0.0% of the frame differs, worst channel 0/255**,
  against **99.2% / worst 208** for two genuinely different instants. Both
  directions measured (2× reads r,g,b then LAPS the 6 s clip back to r inside a
  5 s take; 0.5× is still on the first third at 3.0 s where 1× has moved on),
  and the live element reads back `rate=0.5, preservesPitch=false`. Watertight
  at 320/360/390/430 with the sheet OPEN — five 54.4px chips, zero horizontal
  overflow, Done still on screen.
  Regression: 24/24 unit sweeps green (13 new in `speed.invariants.mjs`,
  including the identity clause measured BITWISE against a verbatim copy of the
  pre-feature function, and the rejected "multiply afterwards" design refuted at
  61.4× of on-screen spread); e2e trim 9/9, playhead 2/2, mobile 7/7,
  video-length-sync + source-count 7/7, pace 4/4. `tsc --noEmit` and
  `vite build` clean.
  TWO SCARS. `preservesPitch` defaults TRUE, so the live element was
  time-stretching where the offline mixer resamples — the preview and the export
  disagreeing about what a rate SOUNDS like, latent only because sync's default
  mode leaves every rate at 1. Fixed in the PREVIEW, through one `applyRate` all
  three assignment sites now share. And a sweep that `transform`s a single file
  dies the day its module grows an import: two sweeps went red the moment
  `videoSync.ts` imported `speed.ts`. BACKPORT RIDER FIRED — all six
  non-bundling sweeps in the tree converted to `bundle: true` in the SAME cycle
  (clipWindow, videoSync, fill, rasterBudget, session, exportLimits), not just
  the two that were failing, because the other four carried the identical
  undeclared precondition.
  NOT SHIPPED, AND SAID PLAINLY: a speed is a SCALAR, not a curve — no ramps, so
  "slow into the beat and snap out" is still unaskable; a FREEZE (0×) is not the
  bottom of the roster because a stalled audio node is not a still frame, and it
  needs its own answer for the sound; and a speed does not travel in a
  composition code or a project file, exactly like the trim and the music.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C156 — 2026-08-12 · [AXIS:COLLAGE] THE STRIP — the ruler stops measuring an
  empty ten seconds** (well read UNSCOPED first and empty — 0 new, 0 stranded in
  `building`, 19 shipped; breadth debt 0; COLLAGE named stalest, and the ladder
  named this rung "the natural next one now that a ruler exists to draw them
  on"). BEFORE: the playhead knew the take's length and the fade's shape and
  nothing else — six cycles of time-domain work (THE MOVE, the trim window, the
  music range, the lap schedule, THE FADE, THE PACE, THE BEAT) and not one of
  them observable without exporting a file. AFTER: under the bar, on the bar's
  own axis, a row of CUT MARKS where the collage re-deals — each a hairline plus
  its dissolve's real width — and one LANE per timed source drawn as the passes
  it makes, the last one short when the take ends mid-lap.
  THE DESIGN IS ONE SENTENCE: draw the compositor's schedule, never a second
  belief about it. `lib/takeMap.ts:cutPlan` collapses `turnAt`'s two branches
  into one output-time `{hold, first, fade}` — the roster's hold over the pace
  rate (`paceTime` scales the CLOCK, so a boundary at scaled `k*hold` is at real
  `k*hold/rate`, and the FADE divides with it, which is why `fade/hold` is
  invariant), or the beat grid verbatim and UNPACED. A lane's period is
  `clipWindow.effectiveLength`, so the sync mode and THE SPEED reached the
  drawing with no new seam and no fourth copy of a formula.
  AND IT FOUND AN ERROR IN WHAT WAS ALREADY LIVE: everything drawn under the bar
  was positioned on the TRACK's width while the thumb travels `thumb/2` to
  `width - thumb/2`, so the fade wedges have been out by up to half a thumb
  since they shipped — 6% of the take. `--range-thumb` is one token now, both
  engines' thumbs and the one inset. SCAR-C156 filed; BACKPORT RIDER FIRED and
  the sweep is named in it: no trade toolkit page has a slider at all, and the
  five other collage ranges carry the same error inside `--fill` where it is
  bounded by `thumb/2` and therefore always hidden under the 26px thumb itself.
  PROOF. Unit: 11 invariants, 14/14 mutations killed — 4,511 marks each asserted
  to be a boundary `turnAt` agrees with, a 240Hz walk of 180 schedules proving
  none is MISSING, seams asserted against `sourceTimeAt` wrapping the window.
  The one mutation that SURVIVED the first pass was deleting the lap epsilon,
  which only bites on an exact division — measure-zero under 4,000 random pairs,
  12 real cases among the 400 exact ones now swept (SCAR-C147's shape again).
  Artifact: marks measured in the DOM at 0.3333/0.6667, one tap of `sync` moving
  them to 0.2664/0.5331/0.7997 on a 120 BPM grid; the thumb's computed centre at
  the 5s cut is 408.0 and the mark is drawn at 408.0; clip lane 3 laps at 1x and
  5 at 2x; zero horizontal overflow at 320/360/390/430 — green on chromium AND
  on both WebKit projects, then re-run GREEN AGAINST PRODUCTION. Regression
  40/40 (playhead, mobile-watertight, pace, beat, turn, speed, soundtrack, trim,
  video-length-sync, visual-regression); `tsc --noEmit` and `vite build` clean.
  NOT SHIPPED, AND SAID PLAINLY: the strip is a DRAWING, not a control — a lane
  is not yet a handle onto its clip's trim sheet, and a seam is not draggable,
  which is where `drag-reorder` and `split/cut` now obviously live. THE MOVE has
  no lane, so a still collage with the turn on HOLD and no music still draws
  nothing at all. And a lane past 48 seams goes to a hatch that says "too fast
  to draw" only in its title.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C156b — 2026-08-12 · [AXIS:COLLAGE] THE ADVERSARIAL AUDIT EARNED ITS KEEP
  AGAIN — the strip was drawing cuts on a wall that cannot cut** (same cycle,
  post-ship, pre-close; the audit ran against the shipped tree while the live
  verification was in flight). ONE HIGH, TWO MEDIUM, FOUR LOW; the HIGH and both
  MEDIUMs fixed, three LOWs fixed, one LOW measured and deliberately left.
  THE HIGH IS SCAR-C156b: three predicates answer "is the wall turning" and the
  strip read App's (`images.length > 1`, the POOL) instead of the Stage's (the
  turn RING, which excludes every fragment holding a live clip). A collage of
  videos never cuts and the strip drew two ticks saying it does — in mixed pools
  shuffle-dependently, 195 of 400 deals. `StageStatus.turning` is published now
  and the strip is gated on it.
  THE MEDIUMS: `laneLabel` rounded away the partial pass it exists to state
  (SCAR-C156c), and a MUTED soundtrack — which contributes neither picture nor
  sound to the file — still got a lane. THE LOWS: `cutPlan` mirrored
  `scheduledTurnAt`'s fade test when the PIPELINE repairs that field before the
  compositor sees it, so a `fade: 0` grid drew nothing while the wall cut; with
  nine sources the MUSIC lane was the one dropped, and it is the only lane whose
  identity is unambiguous; an unmeasured source with nothing beside it came back
  `empty` and took its own "1 source of unknown length" admission with it.
  LEFT, WITH THE MEASUREMENT: `--fill` is a gradient stop inside the TRACK while
  the strip is on the thumb's travel, so on WebKit they differ by
  `thumb*|f-0.5|` — 7.8px at 20% of a 294px bar. Bounded by `thumb/2` and
  therefore always underneath the 26px thumb itself, which is why five call
  sites are not being touched to move a pixel nobody can see.
  WHAT THE TESTS COULD NOT HAVE SEEN, AND NOW CAN: no spec in this tree had ever
  put a clip and a turn mode in the SAME SCENE, and the unit sweep's oracle
  (`turnAt` given a mode id) is structurally blind to the Stage switching the
  feature off. S6 is that scene: two videos, MARCH, parked at 5.8s — past the
  cut and past its dissolve — against the same instant with the turn off. 0.0%
  of the frame moved, worst channel 0/255, and the strip draws 0 marks.
  PROOF: 13 invariants, 19/19 mutations killed (one per finding); take-strip
  4/4, turn + beat + playhead 15/15; the full chromium suite 149/149 on the
  build this corrects; `tsc` and `vite build` clean.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C159 — 2026-08-14 · [AXIS:COLLAGE] THE STILL TAKE — the ruler and the strip
  finally describe a collage of PHOTOGRAPHS** (well read UNSCOPED first: 0 new,
  0 building, 23 shipped, 2 declined — no wish to claim; LIVE STATE: no trades
  owed; stalest axis COLLAGE, 9 lane-cycles). Two rungs, one hole: what is in a
  take when nothing in it is a source. BEFORE → AFTER, both measured at the
  artifact. (1) THE DRIFT ROW — photographs + a move + HOLD + no music drew NO
  STRIP AT ALL (`empty`); it now draws an amber row above the source lanes,
  seams at 0.0000 and 0.8000 of a 15 s take, three passes at 2×. It is a ROW and
  not a lane on purpose (`takeMap.ts` DECISION 5): DECISION B reads a lane's
  identity off its POSITION against the chip row, and `MAX_LANES` is a budget
  for SOURCES, so the one thing true of every collage must not be the row a
  ninth clip evicts. Gated on `StageStatus.moving` — published this cycle beside
  `turning` — because `setScene` builds that flag from the per-fragment analysis
  and the chip row only knows what was picked. (2) THE DERIVED CLOCK — a still
  collage under music sat at 0 for the length of the song; `takePosition` now
  COMPUTES the position from the anchor the tick holds open while the soundtrack
  element rolls, so the Stage schedules nothing at all: 1.900s → 4.900s over 3 s
  of wall clock with the canvas hash IDENTICAL at both ends, and 0.000s →
  0.000s with the one line reverted. Its price is `freezeClock()` — `outTime`
  can now be far behind the truth, so `stop()`, `applyPowerState` and `setTake`
  had to be taught to hold HERE rather than at the last frame drawn.
  BACKPORT RIDER: no trade page touched, so no cross-trade sweep applied; the
  in-tree sweep for the same class found the sibling — `TakeStrip` had TWO
  copies of the pass-drawing rules the moment a second kind of row existed, and
  `laneLabel` two copies of the lap arithmetic, both extracted (`Passes`,
  `passesLabel`) rather than forked. Mutation M8 proves the label extraction is
  load-bearing: breaking it fails I10, an invariant written two cycles before
  the drift existed.
  PROOF: 3 new invariants (I13–I15, 3,725 instants swept against `sampleMove`'s
  own `NO_MOVE` identity), 8/9 mutations killed and the ninth demonstrated
  EQUIVALENT rather than waved past; 25/25 unit sweeps; e2e 50/50 across
  take-strip 5/5 (incl. the 320/360/390/430 mobile law at 22 px of strip, zero
  overflow), playhead 3/3, motion+turn+pace+beat+soundtrack 24/24, and
  trim+speed+video-audio-export+export-integrity+visual-regression 18/18;
  `tsc` and `vite build` clean. Scar filed: a mutation harness that restores
  with `git checkout --` deletes the uncommitted work it exists to grade.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **C160 — 2026-08-15 · [AXIS:COLLAGE] THE LEVEL — every gain in this app was a
  boolean wearing a number's clothes** (well read UNSCOPED first: 0 new, 0
  building, 23 shipped, 2 declined — no wish to claim; LIVE STATE: no trades
  owed; `av/AV_SOCIETY.md`'s last COLLAGE tag is 2026-08-12, one line older than
  the WELL tag the bump flagged, so COLLAGE is the true stalest axis and WELL is
  unclaimable). The Audio rung has asked for `volume per source` by name since
  THE SOUNDTRACK shipped. BEFORE → AFTER, measured by DECODING THE EXPORTED MP4.
  **THE SHAPE WAS DECIDED BY A FACT THE RUNG DID NOT CONTAIN**: every gain was
  already a `number`, so the work was not "add a level", it was "stop writing 1
  into the number you have" — `mixSources` changed by NOT ONE LINE, exactly as
  THE SOUNDTRACK did and for the same reason.
  `lib/level.ts`: one roster of five (-6 dB a step, exact halvings, 100% to a 6%
  bed), one `mixGain(wanted, level)` that BOTH row emitters call — they had been
  spelling one boolean rule two ways (`wanted ? 1 : 0` and `t.muted ? 0 : 1`),
  which is fine while it is a boolean and is how two emitters of one row drift
  the moment it is not — and one `livePath`, whose whole job is that the level be
  applied EXACTLY ONCE: an element's `volume` and the gain node it feeds are in
  SERIES, so writing it to both renders 25% as 6%. I2 pins `node * element ===
  effective` in both branches, which makes that bug unrepresentable rather than
  fixed. MUTE IS UNTOUCHED and still owns 0.
  PROOF AT THE ARTIFACT, and the design of the measurement is the point: the
  true-peak limiter scales every sample by ONE scalar, so absolute energy is
  partly its answer and the RATIO between two tones in one file is the user's
  alone. **music/clip 1.2912 → 0.3227 = 0.2499x, 12.0 dB down** against a nominal
  12.04 — with the clip's own 440 Hz bin reading 0.08502 in BOTH exports, so the
  control moved the source it names and nothing else. The clip path is a
  different route (Stage-only lifetime, `describeAudioSources`) and is measured
  separately rather than argued from the music: **A/B 0.7183 → 0.1782 =
  0.2481x**. A muted track at 6% sits 568x under the clip.
  BACKPORT RIDER: fired IN-TREE, and it found a live defect one cycle old.
  `emitStatus` de-dupes on a hand-enumerated signature; `level` was missing from
  it (the level wrote through to the file and the room while the chip read back
  the old value), and so was `moving` — THE DRIFT ROW's own gate from C159. Two
  for two: every field added to `StageStatus` since that line was written had
  fallen through it. Both in now, scar filed. Same class, same cycle: the
  duplicated `SoundtrackSpec` shape in `VideoStage`'s props was also one field
  behind and is now the type itself. No trade page touched, so no cross-trade
  sweep applied.
  PROOF: 10 new invariants (I1–I8 incl. the pre-level oracle, 4,019 coercion
  probes and 2,448 live-path settings); 26/26 unit sweeps; e2e 5/5 on the new
  suite (two full offline renders and a division, plus the 320/360/390/430
  mobile law with five 44 px chips inside a sheet that already holds a trim
  strip, two range handles and a speed roster — zero overflow at every width),
  and 27/27 regression across soundtrack 6/6, take-strip+playhead 8/8,
  video-audio-export+mobile-watertight 11/11, speed 2/2, fade 2/2; `tsc` and
  `vite build` clean. Second scar filed: a control bin is a floor only for the
  file it was measured in — L3's first bound copied a threshold from a suite
  whose file was digital silence and failed at 3.6x on a tone that was 732x down.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-16 · **[AXIS:WELL] THE MUSIC BUTTON TAKES A VIDEO'S SOUND AND LEAVES
  ITS PICTURES · AND A FRAGMENT CAN BE THROWN OUT FROM FULL BLEED** — from wish
  `86c34aa3` (kind=improve, about_tool=upload), read UNSCOPED first and found in
  `--status building`: a previous cycle claimed it, wrote `lib/intake.ts` and
  widened `isVideoFile`, then died before wiring, sweeping or shipping. Finished
  rather than re-claimed, which is what the stranded-`building` sweep is for.
  *"Be able to add music or sound without the video. Right now if you use a video
  for the sound or import audio from video it just imports video… if you're
  importing audio it should not display the video. Also when full mode is active
  if I click a box or segment there should be ability to remove that from the
  group of images displayed or videos."* **before → after**: (1) all three file
  buttons fired one `onChange`, so routing read the FILE and never the BUTTON —
  a `.mov` picked with MUSIC became a rectangle in the collage; now `lib/intake.ts`
  owns the ladder and takes the button's INTENT, the music input's `accept`
  carries the video containers (without them the desktop picker greys the clip
  out and the fix is unreachable), and a picture handed to that button is refused
  ALOUD instead of quietly added. `'any'` is byte-identical to what shipped, and
  that is a measurement over the whole extension × MIME cross product, not a
  hope. (2) full bleed had a button for throwing away EVERYTHING and none for
  throwing away ONE; now a tap ARMS a fragment and a 2×44px puck offers pin or
  remove, with `lib/evict.ts` deciding what leaves — a photograph alone, a frame
  of a clip taking the whole clip and its other frames, because `assignSources`
  already defines a video as ONE source. Outside full bleed the tap still pins,
  byte for byte. **BACKPORT rider FIRED, and found nothing to carry:** 0 of 105
  trade pages have a file intake, so the intent-blind routing class cannot occur
  there; the per-item-removal class is already carried by the trade list tools
  that need it (`.rm`, itself the product of an earlier backport). The remaining
  ~96 fixed-roster pages were NOT audited one by one for an extensible list
  lacking a removal — that is the named next rung, not a swept-clean claim.
  PROOF: 2 new sweeps (intake 17,527 assertions over 2,160 file × intent rows and
  400 splits; evict 64,258 over 400 pools and 3,070 targets) and 29/29 unit
  sweeps; a new e2e suite 10/10 **against the LIVE deploy**, including a Goertzel
  read of the decoded export — 440 Hz at 2,032× the control out of a collage of
  two photographs, which have no other way to make a sound — and the
  320/360/390/430 mobile law with both 44px targets whole over the artwork;
  75/75 regression across roll-code 20, undo 21, soundtrack 6, level 5,
  source-count 7, take-strip 5, video-audio 4, playhead 3, speed 2, fade 2;
  `tsc` and `vite build` clean. Two scars filed (C127 a router that asks the
  object cannot hear the verb; C128 an undo that cannot restore the thing).
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-16 · **[AXIS:WELL] THE RANGE FADE — the cut you chose stops arriving
  as a click** (well read UNSCOPED across all trades first: 1 new, 0 stranded in
  `building`; it was the only wish, so the stalest-axis signal INTERFACE yielded
  to it — a wish outranks every roadmap). before→after: **a music range shorter
  than the take spliced hard at every wrap, with no control anywhere in the app →
  one roster row on the sheet where the range is chosen eases that source in at
  its IN point and out where its sound stops, every time it comes round.** Wished
  for verbatim: *"Need to be able to add fade even when selecting clip range for
  audio"* — which is, word for word, the hole this book named as NOT SHIPPED in
  the cycle that shipped the audio range. THE PANEL (3 lenses: a working editor,
  an audio engineer, a product skeptic) came back 3/3 BUILD_WITH_CHANGES (6/6/7)
  and split 2:1 on the only question that mattered — every lap, or once. It
  RESOLVED rather than being voted through: the majority were right that a
  once-only fade duplicates the take chip and leaves every intermediate splice
  clicking, and the dissenter was right that 0.25–1s dips at every wrap sound
  broken rather than edited. What survives both is every-lap WITH a 0.1s roster
  entry (a de-click, inaudible as a dip) and a QUARTER-lap clamp where the take
  fade's is a half — a take plays once so a triangle is a worst case, a window
  laps so the same clamp is tremolo. `lib/windowFade.ts` is `fade.ts`'s envelope
  with the LAP as its take, so there is still exactly one curve in this app; the
  mixer schedules it on a gain node in SERIES with the source's level and the
  monitor schedules it from the element's own clock, because the frame loop is
  demand-driven (a still collage with a soundtrack draws nothing at all) and a
  per-frame write would park mid-ramp. The OUT edge is `audibleEnd`, never
  `outSec`. **PROOF:** a new unit sweep — 3.85M assertions over 480 clip cases,
  3.19M sampled instants asserting BOTH emitters read back through `rampGainAt`
  as the envelope of the position `schedulePositionAt` models — with 6/6 injected
  mutants dying on the assertion written for them; a new e2e 3/3 reading the
  DECODED EXPORT, whose measured envelope is
  `01357899999999998642113578999999999986421135789999999999864211357999999999998642113`
  against a control take that reads `2999...9` — four joins at 0.06–0.25 of peak
  where the control reads 0.99, and every lap MIDDLE still at full level (the
  assertion that fails if anyone widens the clamp). Plateau ratio faded/flat
  0.997, so the limiter did not rescale the export. 30/30 unit sweeps, 40 e2e
  green across soundtrack 6, trim 9, level 5, fade 4, video-audio 4, playhead 3,
  speed 2, mobile-watertight 7; `tsc` and `vite build` clean. Two scars filed
  (C161 a bottom-pinned sheet loses its head not its foot — the mobile assertion
  passed with the height bound removed; C162 a phase that wraps for a source that
  does not). **BACKPORT rider FIRED, and found nothing to carry:** the class was
  "an overlay with no height bound whose controls can go off-screen"; swept all
  105 trade pages across 11 trades — every modal goes through
  `shared/toolkit.js`'s `.av-modal` (`align-items:flex-start` + `overflow-y:auto`
  on the OVERLAY, which is the correct pattern) or `shared/feedback.js`'s sheet
  (`max-height:min(92vh,100%);overflow:auto`), and the one page the grep flagged
  (`av/consumables.html`) is a bottom dock and a clipboard-fallback textarea, not
  a sheet. 0 of 105 carry the class.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-18 · **[AXIS:WELL] THE SECOND REVIVAL — Shuffle switches the photos
  up at the sizes a phone uploads** (wells read UNSCOPED first: AV 2 new, vibe
  4 new, 0 stranded in `building` in either; oldest lived in the AV well and
  rank took the improve over the new_tool — the sibling aspect-lock wish stays
  queued, ONE wish per cycle). Wished verbatim: *"When you upload multiple
  images and you have a shuffle going for arrangement shuffle should switch the
  photos up. But make sure your you're doing color matching too though."*
  before→after: **under every colour arrangement, 0/200 presses changed
  anything at 3–6 photos and 6% at 8 (measured on the shipped module — the
  first revival's window floor of 1 rank is a ±0.5 amplitude that can never
  cross two ranks) → every press re-deals at every n: jitter keeps its overtake
  bound (floor 2), a seeded rotation of ≤3-rank blocks guarantees the movement,
  n=2 alternates its only two deals, and a proof hatch makes "never the exact
  ranking" hard for n ≥ 3 — displacement stays capped so the colour matching is
  structural, not preserved by luck.** THE PANEL (3 lenses: visual artist,
  determinism engineer, product skeptic) came back 3/3 BUILD_WITH_CHANGES
  (6/6/7) and every demand landed or was RESOLVED with data: the skeptic's
  small-n sweep and the artist's exhaustive-trigger sweep are §3b-small +
  §3b-small-exhaustive; the artist's "scale the block down at small n" was
  measured and REJECTED (b=2 tightens worst move 3→2 ranks and quarters the
  deal space at n=6, 83→24 distinct — the dead feel back by another door); the
  engineer's n=2 "always swap" fix would kill the button permanently after one
  press (two deals: always-swap never changes again), so alternation stands —
  the UX criterion is "the press changes the picture", not "≠ ranking".
  **PROOF:** composition sweep green with the new sections (M-OLD, the shipped
  code, dies with 41,632 failures; M2, a rotation-stripped floor-bump, with
  9,807); 30/30 unit sweeps; 14/14 composition e2e incl. two new pixel tests —
  the six-photo re-deal test FAILS on the old code (kill-proof run) — and 7/7
  mobile-watertight; tsc + vite build clean; live-verified: bundle c9235da4 →
  159737d2 and 4/4 shuffle e2e against the DEPLOYED site, desktop + Mobile
  Chrome. Wisher credited in av/credits.json (anchor 3f76ee8b) and on the
  Settings panel, anonymous as filed. Two scars filed (C163 a sweep that
  avoids the sizes people upload; C164 a green battery hiding an uncaught
  assert — the soundtrack sweep sat red on HEAD since f1d25ab4 and is fixed in
  the same ship, with tone_b.mp4, referenced by three committed specs but
  never committed, landed too). **BACKPORT rider FIRED, found nothing to
  carry:** the class is "a variance/shuffle control that silently no-ops at
  small input sizes"; swept all 13 trades' pages + shared/*.js for shuffle /
  randomize / re-roll / dice controls — zero exist outside Collage Studio
  (reconcile.js's "Dice" is the Sørensen–Dice coefficient). 0 of 13 trades
  carry the class.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-18 · **[AXIS:WELL] THE FRAME HOLD — the dice keeps the shape you
  found** (wells read UNSCOPED first: vibe 0 + 0 building, AV 1 new + 1
  STRANDED in `building` — C3631 claimed the aspect-lock wish, built most of
  it, and died with no commit and no book line; the building sweep is what
  surfaced it, and this cycle finished that claim instead of claiming the new
  concurrent-video wish — ONE wish per cycle, the concurrency wish is next).
  Wished verbatim: *"Tide pool is sick I like them. Maybe good idea to lock
  aspect ratio too as a toggle."* before→after: **every dice press re-dealt
  the canvas shape (roster of seven — 12-for-12 measured pre-fix) with no way
  to pin it → a "Keep frame shape" toggle, OFF by default, on both surfaces
  the chase happens (dock chip under the dice, rail button beside it); held,
  the dice re-rolls everything else and pins what is ON SCREEN — a hand-set
  Canvas chip becomes the held value (F4) — and OFF stays byte-identical to
  the old dice: `if (!holdFrame) setAspect(roll.aspect)`, NOT
  `locks:['aspect']`, because RollLock copies the last ROLL and would snap
  back over a hand-set frame, and skipping the setter leaves the rnd stream
  untouched.** THE PANEL (3 lenses: wisher's advocate, state engineer, mobile
  rail auditor) came back 3/3 SHIP_AS_IS (9/9/8) — zero blocking demands —
  and all five advisories landed pre-ship: the wisher's own words "(aspect
  ratio)" in both un-held tooltips; a constant rail aria-label (aria-pressed
  carries the state — the flipping-label draft never deployed); the rail
  comment's one-row arithmetic corrected (claimed 394+24, is 403+24=427 — 9
  flex items, 8 gaps, the separator counts); rail-shuffle/rail-remix testids
  into F3b's containment loop; two new witnesses (undo-under-hold in F1, and
  the row-split geometry itself in F3b). **PROOF:** 30/30 unit sweeps (exit
  codes, per C164); frame-hold e2e 5/5 + rail siblings colour-dice 9/9, undo
  21/21, mobile-watertight 7/7; tsc + vite build clean; live-verified: bundle
  159737d2 → 048c7ff3 and 5/5 frame-hold e2e against the DEPLOYED site.
  Wisher credited in av/credits.json (anchor 32d19212) and on the dock chip,
  anonymous as filed. Scar filed (C165 — a spec that asserts the gate but not
  the claim). **BACKPORT rider FIRED, found nothing to carry:** class = "an
  aria-pressed toggle whose accessible name flips with state"; swept all 13
  trades + shared/*.js — every toggle carries a constant text name (EN/ES,
  With-my-name/Anonymous, basis chips, favorite stars); the only flipping
  aria-label was this cycle's own rail draft, fixed before it deployed. 0 of
  13 trades carry the class.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/
- 2026-08-19 · **[AXIS:WELL] THE CONCURRENCY — every video you drop plays at
  once, on a phone too** (wells read UNSCOPED first: AV 0 new + 1 STRANDED in
  `building`, vibe 0 + 0; the stranded claim was the concurrency wish C3633 took
  and C3634 kept — `lib/admission.ts`, an 81k-check sweep, the e2e and six
  fixtures sat on disk with NOTHING committed and the Stage half-wired; this
  cycle finished that claim — ONE wish per cycle, and a claim left in the well
  outranks a new one). Wished verbatim: *"Multiple videos should play back at
  the same time ando. Concurrency not just one."* before→after: **the realtime
  pixel cap was `count × 1080p` (phone 6.2 Mpx), so any 4K clip (8.3 Mpx) let
  ONE clip play on a phone — the first always admitted, every later one refused
  with "too high-resolution to decode together", a rule in a hardware costume;
  measured on the LIVE deploy: two 4K clips on an iPhone UA → 1 decoder → now
  the budget is the count cap FILLED (two DCI-4K seats + 1080p seats on a phone,
  2-4 4K seats on a desktop by REPORTED memory — unreported = middle tier, an
  iPhone is never a flagship by construction) behind a MEASURED ceiling: the
  probe reads every live clip's presented frames over one window and
  `judgeStall` names the failure — paused or nobody moving = `blocked` (Tap to
  play, as before); un-paused + frozen while a sibling moves = `stalled`, two
  strikes, `settleStall` lowers the ceiling to the load that failed (floor: one
  decoder), re-plan, nudge, 4 rounds per episode, 1.2 s cooldown, a
  MEDIA_ERR_DECODE with siblings live gets one retry as a stall before it is
  "broken"; the notice says the lever — "plays 3 at a time" / "too big — smaller
  clips would run" / "this device can't run them all" — in ≤ 90 chars so it
  survives the 9px truncating span.** THE PANEL (3 lenses: iOS media engineer,
  state/invariants engineer, wisher's advocate) came back 3/3
  BUILD_WITH_CHANGES (7/7/7) on the stranded design and every BLOCKING demand
  landed: frames not clock as the signal (a clock advances over a frozen
  picture), `paused` in the vocabulary (a starved decoder is un-paused; iOS
  Low Power on an incremental admit is paused), arm-time load + plan epoch
  (a probe that raced a re-plan recorded a stall at a load never live), seated
  guard + grace + strikes + cooldown + episode reset + floor, DCI headroom
  (`2 × UHD` refused two 4096-wide clips with the wish's sentence), the measured
  verdict named in the status, `livePixels` from what is ACTUALLY live, I2
  unconditional (a count cap of 0 seated nothing), junk pixels charged the
  UNKNOWN rate, I7b verdict-justification, and the `* 0` vacuous I15 line
  fixed. Resolved against the panel with data: the stalled clip is NOT
  penalised in rank (the rank re-plan + nudge reaches the same seat count and
  keeps the biggest picture moving); `paused ⇒ blocked` chosen over lens 1's
  "OS-pause is a budget signature" because a muted inline video is never
  session-interrupted on iOS and the LPM-incremental sequence is the one that
  regresses the wisher's own phone. NOT built, named: frame-rate in
  `pixelCost` (4K60 costs 2×), a ceiling reset on visibility return, a Stage
  hook to force a stall (no headless engine starves a decoder, so the
  `stalled → sentence (c)` path is pinned only at the pure seam). **PROOF:**
  admission sweep 101,133 checks over I1–I15 + I7b + I13b, 8/8 injected
  mutants dying on the assertion written for each (paused rule → I12; 2×UHD
  phone ceiling → I9 DCI pair; floor → I13b; bound → I13; clamp → I2; junk → I14;
  guard order → I7b; stalled-list → I12); 31/31 unit sweeps (exit codes);
  concurrency e2e 3/3 on :5199 — three hue-keyed clips: 3 decoders unpaused,
  3 clocks advancing, 3 canvas regions moving, and after 2.5 s of probes still 3
  with no stall sentence; THE WISH test: two REAL 3840×2160 VP9 clips on an
  iPhone UA both decode, both move, no "1 of 2" — which FAILS on the live
  deploy ("Received: 1", the kill-proof) and passes here; 6/6 consecutive
  green after the fixtures became stripes; regression video-collage 17/17,
  video-audio 4/4, mobile-watertight 7/7, frame-hold 5/5, trim 9/9; tsc + vite
  build clean; live-verified: bundle 048c7ff3 → 3092dc0f and 3/3 concurrency
  e2e against the DEPLOYED site incl. the 4K pair. Wisher credited in
  av/credits.json (anchor 0080f006) and on the Advanced panel, anonymous as
  filed. Four scars filed (C166 a budget constant in a hardware costume; C167 a
  one-clip probe cannot tell a gesture from a budget; C168 a motion fixture
  whose motion can miss the crop; C169 two cycles died on one claim with
  nothing committed). **BACKPORT rider FIRED, found nothing to carry:** class =
  "a device/resource budget expressed as an unmeasured constant that refuses
  work the device could do"; swept all 13 trades' pages + shared/*.js for
  count/size/resource caps — none exist (no file counts, no size refusals, no
  decoders; toolkit.js's maxima are CSS bounds measured per viewport, the
  opposite pattern). 0 of 13 trades carry the class.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-23 · **[AXIS:COLLAGE] C3647 — THE DESK: eight looks were a picker, and
  under them was a control nobody could reach.** **before:** the grade was a
  roster of eight chips. "Make it a bit brighter" was unaskable — the nearest
  answers were `punch` (which also adds 30% colour) or nothing — and `Grade` had
  been five continuous numbers the whole time, reaching four render surfaces
  through one ordered pipeline, with a UI that could only name eight points in
  that space. **after:** an ADJUST door at the end of the row opens
  **EXPOSURE / CONTRAST / COLOUR / WARMTH**, live on the preview, in the export
  worker's own file, in the SVG's real `<filter>` primitives, and in the
  composition code. **THE ENGINE DID NOT MOVE** — the four surfaces are handed a
  roster id OR the five numbers (`LookRef`, structured-cloneable, so it crosses
  to the worker thread like the title plan does), and there is still exactly one
  pipeline in one file. **WARMTH IS BIPOLAR BECAUSE THE ROSTER ALREADY WAS:**
  `sepia` and `hue` are two halves of one tonal decision, and `warm` (sepia 0.30,
  unrotated) and `cool` (sepia 0.70 at 190deg) are two points on one axis through
  untoned — so four sliders, not five, and the fifth was never a control, it was
  a coordinate. **EVERY ONE OF THE EIGHT IS A POINT IN THIS SPACE, BIT FOR BIT**,
  which is the invariant the feature rests on: a person opens the panel to drag
  ONE axis, so opening it must not restate the other three. Measured at the
  artifact — **worst channel delta 0/255** — and swept as `Object.is` equality
  field by field. **THE GRID IS ENFORCED ON THE WAY IN AND THAT IS CORRECTNESS:**
  `num`'s six-decimal exactness rests on amounts sitting on the two-decimal
  `GRADE_GRID`, a property of a roster written by hand; a desk COMPUTES its
  amounts (0.1 x 0.6 = 0.06000000000000001), and unsnapped that lands as a
  difference between the exported SVG and the exported JPEG of the same collage.
  **THE CODEC GREW ITS FIRST OPTIONAL GROUP:** eight characters present only when
  an axis is off its preset, so a collage on one of the eight still mints the
  exact 21-character group minted since THE BEAT — and 22..28 belongs to no
  generation, so a desk code that lost characters is REFUSED rather than sliced
  into a shorter body that opens cleanly as somebody else's collage.
  **PROOF:** grade.invariants **71,095 checks / 0 failures** (1,812 reachable
  desks on the grid AND inside the range CSS Filter Effects defines; the two
  emitters denoting one transform to **2.2e-16** on grades that are on no roster;
  the optional group; truncated desk codes refused) with **6 of 7 mutants dying
  on the assertion written for each** — unsnapped sepia, a warmth constant out of
  sepia's legal range, the roster no longer fitting the axis, COOL_HUE moved, the
  group minted unconditionally, an absent desk materialised as a neutral one —
  and the seventh SURVIVING is written down rather than papered over (scaling
  WARM_SEPIA rescales the axis and changes no pixel: what is pinned is that the
  roster FITS inside it, not the number). **31/31 unit sweeps, tsc clean, vite
  build clean. desk.spec 12/12 AGAINST PRODUCTION** — opening the desk 0/255,
  each axis moving its own statistic and no other (exposure luma 120->80 and
  ->144, contrast spread 53->71, colour chroma 98->0.0, warmth R-B +26.6 vs
  -22.9), the export WORKER's own file monochrome at chroma 0.0 against an
  ungraded 93.1, the SVG and the canvas at **R-B -24.7 vs -24.7**, the code
  round-tripping the axes and the pixels, and the panel watertight at
  320/360/390/430 with nine chips and four 44px ranges. look.spec **12/12 against
  production** too. **BACKPORT RIDER FIRED:** the class is *a threshold measured
  off a RANDOM DEAL* — the desk's own axis test failed one run in eight on
  `cool < base - 5`, because a TONE replaces a picture's cast rather than scaling
  it. Swept every e2e for the shape: `look.spec` T2 carried the identical pair and
  had been flaking on it since it was written; both now measure the two ENDS
  against each other plus the one absolute each direction can claim, with what is
  deliberately not asserted written beside them. `twist.spec`'s base-relative bar
  is the same shape and NOT the same class (darkness under twist is monotone in
  the deal) — swept, named, left alone. **SWEPT AND NOT FIXED:** svg-project
  S1/S3/S8 time out on `filechooser` under Mobile Chrome — confirmed pre-existing
  by stashing this work and reproducing it, so it is a harness defect on the
  Open-a-project path and owed its own cycle. **THE CYCLE'S OTHER FINDING IS WHY
  IT WAS A COLLAGE CYCLE AT ALL:** the bump named DEPTH as the stalest axis, "last
  worked 14 lane-cycles ago", while DEPTH had shipped in each of the previous two
  — `field_toolkit_directive.py` read `.read(400000)` of books that are
  append-only and 472,507 chars long, so the newest ~15 cycle-log lines were
  invisible. Fixed with one `read_book()` helper (the private roster's reader had
  the identical cap) and a NEGATIVE CONTROL asserting the last tagged line on disk
  reaches the parser; the corrected staleness is COLLAGE 22 / BACKPORT 15 /
  BREADTH 12 / INTERFACE 6 / WELL 5 / DOCS 2 / COMMONS 1 / DEPTH 0. Scar in
  av/AV_SOCIETY.md §SCARS — second failure of the same mechanism, second
  mechanism, same reason: a blind reader's output looks exactly like a truthful
  one. Storefront unchanged — no new tool and no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-24 · **[AXIS:WELL] C3652 — THE CUT YOU CAN HEAR: the trim handles now
  play like a DAW wheel.** From the well (oldest and only NEW wish across both
  wells, anonymous, trade `collage`): "the audio ripping doesn't have a
  playback… if you're at the front you play on the cut, if you're dragging the
  back you play a few seconds before up to the cut, then loop again."
  **before:** the TrimSheet dialed the soundtrack DEAF — video got a filmstrip,
  audio got ruler marks, and the only way to hear a cut was to close the sheet
  and play the piece. **after:** grabbing the IN handle loops the monitor ON
  the cut (`[in, in+2.5s]` — one bar at 96 BPM, the tail's written rationale);
  the OUT handle plays the approach (`[out-2.5s, out]`), the loop landing
  exactly on the cut; release keeps it cycling, blur/Escape gives the room
  back; a white playhead rides the strip at rAF rate through a ref, never a
  render. **THE PANEL CHANGED THE BUILD, WHICH IS WHAT IT IS FOR:** three
  judges (DAW-UX 7, engineering 6, adversarial 5 — unanimous AMEND) converged
  independently on the same hole — a second `<audio>` on the same blob doubles
  the exact source being judged, invisibly to Stage's decoder accounting — so
  the shipped design RETARGETS THE TRACK'S OWN ELEMENT (`stage.setAudition`
  swaps only which window `enforceTrackWindow` holds), which dissolved the
  double, the second decoder, the blob-replace-while-open death (B's find;
  `key={url}` remounts the sheet, the rebuilt track starts audition-null), AND
  Judge A's fade demand for free: the envelope stays armed on the REAL window,
  so the OUT audition hears the configured landing while the artificial edge
  wraps hard, as DAW loops do. Audibility never touches intent: `applyMutes`
  gains an audition term and a solo term (`soundOn`/`muted` unwritten — the
  DECISION 2 split), gated on metadata so a probing track cannot blip its head,
  and on `broken` so a dead blob degrades to a hidden playhead, not a lie.
  **PROOF:** `audition.invariants` **16,654 checks / 0 failures** (edge pinned
  `Object.is`-exact; containment; tail = min(2.5, range); the overlap band
  `range < 2·tail` on purpose; wrap ≡ `liveWrapTarget` over the sub-window
  INCLUDING a full trim window — the trap `full:false` steers around) with
  **both mutants dying** (OUT-edge tail cut → 38 fails; `full` propagated →
  1,544). **32/32 unit sweeps, tsc clean, vite build clean. audition.spec 22
  green / 2 documented skips across all four engines** — the grab speaks, the
  lap comes round on the cut, the approach ends AT it, Escape restores the
  room muted, the replaced song recovers, watertight at 390 with the audition
  rolling, and the keyboard path (Tab parks silent, first arrow speaks, blur
  stops) proven on the Chromiums and SKIPPED on WebKit with the reason in the
  skip: Tab reaches a range input there only under Full Keyboard Access, and
  the pointer path drives the same arming code. Regressions: soundtrack 6/6,
  trim 9/9 (sheet watertight 320/360/390/430). **SWEPT AND NOT FIXED:**
  level.spec L5's decoded-file bound (0.4356 vs <0.42) fails IDENTICALLY on
  the stashed pre-diff tree — pre-existing threshold drift in the family
  look.spec T2 is already scarred for, owed its own cycle, not this one's
  blame. **SCOPE HELD:** the clip sheet's audition is NAMED, not shipped — the
  retarget mechanism would scrub the clip's PICTURE through the live collage,
  which is a design decision owed its own panel, not a side effect of a prop
  in scope (the speed's exact sentence). BACKPORT rider fired inside the app:
  swept the trim surfaces for the deaf-dial class — the clip sheet carries it
  (named above, next rung), the take-fade and level rows do not (they preview
  through the live mix they configure). Storefront unchanged — capability
  inside Collage Studio, no new tool, no new trade. Wish ccf452b3 claimed →
  shipped; credit in av/credits.json AND in the sheet's own credit line,
  anonymity honoured. Operator mid-cycle constraint (open-in-card-studio must
  survive IG/LinkedIn in-app WebViews) relayed to P5 as fleet #15463 with the
  URL-fragment-carrier shape spelled out — that class belongs to the live
  card-studio session whose claims commits dee4922/8c9303d prove alive; the 16
  cards `building` wishes were verified live and released NOTHING.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-26 · **[AXIS:COLLAGE] C3675 — THE SWAP: every composition control in
  this app was GENERATIVE, and now one is not.** Wells read UNSCOPED first, both
  dry (0 new, 0 `building`, no stale claim to release); breadth debt paid; the
  stalest axis was COLLAGE at 11 lane-cycles, so the rung was chosen off the
  ladder — **drag-reorder**, open since the timeline rung was written, and the
  named "single biggest CapCut gap". **before → after:** after twenty rolls the
  wall is right except for two fragments and there was no way to say *"that one
  goes THERE"* — only PIN ("keep this one") and REMOVE ("lose this one"). Now the
  armed puck has the missing third verb: park a fragment, tap its partner, they
  trade. **A collage has no timeline to drag along, so the gesture is the one a
  collage HAS**: the sources sit in fragments, so reordering them is trading two
  fragments' pictures — the same move THE TURN made when it expressed transitions
  between DEALS rather than between clips. **THE HALF THAT IS NOT OBVIOUS, and
  it is most of the work:** `shuffledIndices` is DERIVED — an effect recomputes
  it from nine inputs and `layoutItems` alone re-runs on a gutter nudge — so a
  swap written only into the assignment has a shelf life measured in slider
  touches, and the failure is not "it reverted": a pin already sitting on one of
  the two cells drags its old picture back and leaves HALF a trade, which is a
  DUPLICATE on screen. The only state a re-deal honours is `lockedCells`, so the
  plan re-pins BOTH cells to what they now hold — disclosed by the badge that
  already exists and by the notice, undoable in one tap. **PROOF:**
  `swap.invariants` **676,701 assertions over 49,336 slot pairs / 0 failures**
  (multiset preserved; exactly two positions move; order-independent; self-
  inverse; every refusal inert AND said-or-silent by design; and I9, the REDEAL
  invariant, which re-runs App.tsx's own lock step against the post-swap pins)
  with **four mutants dead — the indices-only implementation fails 162,521**,
  half-a-transposition 154,659, one-sided re-pin 110,494, pins-name-the-old-
  picture 110,472. **AT THE ARTIFACT:** `swap.spec` **24/24 across chromium,
  Mobile Chrome, Mobile Safari and webkit-desktop**, measured on PIXELS with
  six solid tiles — the two colours change places with each other, every other
  fragment is `<45` RGB from where it was, and T2 presses SHUFFLE (a full
  re-deal of everything unpinned) and asserts the trade HOLDS while proving the
  shuffle really re-dealt, so the assertion cannot be vacuous; T6 does the
  same for Undo and Redo. 33/33 unit
  sweeps, tsc clean, vite build clean; regressions intake-intent 10/10 (the
  puck's own spec), undo 21/21, one-layout 4/4. **THREE SCARS, none from reasoning
  — two from engines, one from writing the assertion first.** (1) `--strictPort` protected the wrong run:
  persona500's vite held **:5199**, `reuseExistingServer` attached to it, and
  the suite would have gone green against a page with none of this app's
  furniture — fixed as a CLASS in `tests/globalSetup.ts`, wired into **all 34**
  playwright configs, and proven by firing it. (2) The pending pill sits on the
  fragment it parked, so on WebKit and Mobile Chrome the "tap it again to
  cancel" tap landed on the pill; chromium passed because the fragment was big
  enough. Un-over-claimed rather than papered over — the X and Escape are the
  guaranteed outs and are now asserted. **(3) AND A THIRD, THE WORST, CAUGHT BY
  WRITING THE ASSERTION BEFORE BELIEVING THE SENTENCE:** the commit, the code
  comment and this book all said the swap was recoverable through Undo "and that
  is not luck". `restoreSnapshot` writes back identical seed/count/arrangement/
  shuffle after a swap, React bails out, the assignment never re-derives — Undo
  reverted the PINS and left the PICTURES traded, **285 RGB** from what it
  claimed to restore. Closed by `assignNonce`, a nonce on the assignment effect
  bumped by every restore (safe on every path because the bag is seed-
  deterministic), with swap.spec T6 as the guard; undo 21/21 unchanged, and
  source-count 7/7, dice-count 6/6, one-layout 4/4, roll-code 20/20, frame-hold
  5/5 confirm the extra dep re-deals nothing. **SWEPT AND NOT FIXED:**
  composition.spec's crop-focus export test failed ONCE under 5-worker parallel
  load (preview gap 3.7 vs a bar of 8) and passes 3/3 serially WITH this diff
  present — pre-existing load sensitivity in that test, owed its own cycle, not
  this one's blame. **BACKPORT rider FIRED** — the wrong-app hole was not
  patched in the one spec that hit it but swept across every playwright config
  in the tool (34 of 34), which is the same class the :5173 comment had already
  half-seen. Storefront unchanged: a capability inside Collage Studio, no new
  tool, no new trade.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- 2026-08-29 · **[AXIS:COLLAGE] C3680 — THE REFRAME: the picture moves inside its
  fragment, by hand.** Rung taken because both wells were EMPTY (toolkit 0 new /
  0 building, vibe-cards 0 / 0) and no trade was owed, which left COLLAGE the
  stalest actionable axis — starved since 2026-08-26 while seven toolkit cycles
  ran. **before → after:** every crop this app had ever drawn was decided FOR
  you — a face detector's guess, an energy fallback, five automatic focus rules,
  a drift on a clock — so *"this one is cropped through his head"* had two
  answers, re-roll the whole wall and hope, or throw the picture away. Now you
  drag it. **THE WHOLE CONTACT WITH THE GEOMETRY IS ONE TERM** at the front of
  `calculateSmartCrop`'s anchor chain, so the still preview, the live Stage
  (which both video recorders capture and the offline render seeks), the export
  worker and the SVG all inherit it without knowing it exists. **KEYED BY ASSET
  ID, NOT BY SLOT** — a frame is a corrected FACE, so it sits on the side of
  `turnResolve`'s own line where the face and the colour already are, and it
  survives a shuffle, a re-deal, a swap and a turn; keyed by slot the next roll
  would have undone it, and rolling is what this app is for. **THE STATE IS THE
  CROP**: `dragToFrame` reads the position off the CLAMPED rect the shipped crop
  function just returned rather than off the previous anchor, so an edge
  releases on the very next pixel back instead of banking invisible travel.
  **PROOF, unit:** `reframe.invariants` **12/12** — the picture follows the
  finger to **1.01e-12 canvas units** over 5,557 unclamped drags across 5 cell
  shapes x 5 image shapes x 4 zooms x 4 leans x 4 anchors x 9 drags; 14,400
  crops never leave the photograph; 14,400 reframes leave the FRAGMENT
  `Object.is`-identical; 4,162 round trips return to the start; 3,780 zero-slack
  axes do not travel; 8,843 clamped drags bank nothing; and the rejected design
  (no `-twist` rotation) is measured **37.5% off the finger's line**, not argued
  about. **AT THE ARTIFACT:** `reframe.spec` **12/12 across chromium, Mobile
  Chrome, Mobile Safari and webkit-desktop — and 12/12 twice against the DEPLOYED
  page**, on PIXELS with gradient tiles — a drag down reveals the TOP of the
  photograph and a drag up the BOTTOM, and the spec IDENTIFIES ITS OWN SOURCE by
  projecting each reading onto that source's own gradient (the residual says
  WHICH photograph, the parameter says WHERE ON IT) rather than being told the
  answer; every other fragment within 18 RGB; every fragment's box within
  1.5px; Recentre appears only on a moved picture and restores to 22 RGB; and
  the correction survives a SHUFFLE that is proven non-vacuous first.
  **FIVE SCARS, all found by measuring rather than reasoning** — a drag that
  read its own state back delivered only its last event; banded tiles let
  "drag until it stops changing" stop mid-band; the full-bleed RAIL takes the
  pointerdown at the floor of the screen (third instance of "the affordance
  covers the gesture it documents"); and every colour read was racing an async
  preview, which a serial run hid completely. **BACKPORT RIDER FIRED** — the
  class fixed was the affordance/gesture overlap, and it was applied to BOTH
  overlays that carry it, including the pending pill the scar was originally
  filed against (`pointer-events-none` container, `pointer-events-auto` buttons);
  the accumulate-from-origin fix has no sibling to reach because this is the
  app's FIRST free-form drag — every other continuous control is a native
  `<input type="range">`, which was checked rather than assumed. **GATES:** 34/34
  unit sweeps · 40/40 e2e regression (swap 24, undo, intake-intent, one-layout,
  look, project-roundtrip, svg-project) · 18/18 composition/desk/take-strip
  serially · mobile-watertight 14/14 on both phone engines · tsc clean · vite
  build clean. Storefront unchanged: a capability inside Collage Studio, no new
  tool, no new trade. **NAMED NEXT RUNG:** commit the frame into the pool asset
  on `pointerup` so a reframe travels in the project file and the SVG — the
  manifest already persists `analysis`, and the only thing in the way is that
  `computeLayout` depends on `images`, so the write has to happen once at the
  end of the gesture rather than per frame.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **[AXIS:COLLAGE] 2026-09-03 (C3704) — THE FRAME TRAVELS.** A hand-set crop is
  now in the file. BEFORE: THE REFRAME lived only in App's `frames` Map; every
  surface that DREW it read the Map and every surface that WROTE read the pool,
  so the exported SVG rendered a reframed collage and REOPENED as the un-reframed
  one (measured: no `"frame":{"x"` anywhere in the manifest), the `.collage`
  archive lost it, the crash-safe autosave dropped it without a word, and a
  correction reopened from a file had no Recentre verb because the verb was gated
  on memory (`found = -1`). AFTER: `lib/reframe.ts` owns the one seam between the
  two representations — `poolWithFrames` out, `framesFromPool` + `poolWithoutFrames`
  in — and a single `poolForSave` memo feeds all three writers, so the Map stays
  the live state and the pool is the file format. **THE LADDER'S NAMED FIX WAS
  WRONG AND THE MEASUREMENT IS WHY:** committing into the pool on `pointerup`
  does NOT re-deal the wall (I6, 440 deals, `arrangeBag` identical) — it DISARMS
  the fragment, because `layoutItems` is a dependency of the disarm effect, and
  T1 went red with "no point in it takes a drag" on both engines. **BACKPORT
  RIDER FIRED** — the class swept was "an overlay covering the control under it":
  the restore banner (`top-3`, 94vw, centred) covered the header's Open button at
  390 and 430px, so on a phone the offer to restore the last session blocked the
  door to a different one; fixed (`top-28 md:top-3`) and now ASSERTED with
  `elementFromPoint` rather than inferred from a filechooser timeout. It is the
  fourth instance of that shape, so a single overlay layer with a declared safe
  area is filed as a rung. Also swept: the two seed-dependent RGB thresholds in
  this spec (60 -> 30, measured 49.5 on an unlucky deal), and one vacuous search
  loop of my own making. **GATES:** 36/36 unit sweeps (the new one is 9
  invariants, mutation-checked three ways: wrong index, null-instead-of-drop, and
  a deal that reads the frame — each lights a different set) · reframe 12/12 on
  chromium AND Mobile Chrome, including T6, which reads the crash-safe snapshot
  straight out of IndexedDB and goes red on the third writer alone (`images`
  instead of `poolForSave`: "4 images and not one correction") · svg-project
  16/16 (byte-identity round trips, both engines) · session-recovery 7/7 · project-roundtrip 1/1 · mobile-watertight 7/7
  · swap/undo/intake/one-layout 25/25 · tsc clean · vite build clean. Storefront
  unchanged: a capability inside Collage Studio, no new tool, no new trade.
  **NAMED NEXT RUNG:** disclose under the composition code what a code does NOT
  carry — pins, the swap, the title and now the frame all travel in the FILE and
  none of them travel in a link, and the strip says nothing.
  https://mrdirno.github.io/nested-resonance-memory-archive/collage/

- **2026-09-05 · [AXIS:COLLAGE] C3709 — TIMED LYRICS.** Before: a single static
  title and no editable lyric timing. After: plain SRT/WebVTT or pasted/manual
  cues, precise preview and in/out edits, captioned video, and complete lyric
  persistence through project/SVG/recovery. A locally generated original-art
  starter makes the workflow immediately usable. Supporting integrity fixes:
  pins travel; missing originals refuse save; a reopened picture project cannot
  inherit unrelated music; late seeks retain a valid clock. Independent audits
  found and checked the clock sentinel, Safari layout and starter race. Wells:
  collage 0 new / 0 building. New source dependencies: none. Local validation:
  37/37 pure module suites; 38/38 browser cases (30 caption/project cases across Chromium, Mobile Chrome and Mobile Safari; mobile-watertight 7/7; direct Stage 1/1), typecheck and production build passed. Production evidence:
  30/30 caption/project cases on Chromium, Mobile Chrome and Mobile Safari plus mobile-watertight 7/7 against the deployed URL; the JS, CSS, render worker and service worker are byte-identical to the tested build. Code `9f535486`; Pages run `33988232971` succeeded. Manual live starter, cue preview, full-bleed text and ten-second MP4 result visually checked. Build warnings retained: existing >500kB chunk
  and stale Browserslist database. Remaining independence gap: original video
  and soundtrack bytes are not packaged in saved projects. Next rung: portable
  original media, then authored shot sequencing. Storefront unchanged; this is
  a capability in the existing studio.

- **2026-09-05 · [AXIS:COLLAGE] C3710 — ART ROOM + LYRIC HANDOFFS.** Before: visual HTML instruments lived outside the editor and lyric extraction had no in-app handoff. After: original Tidal Paper and user-selected local HTML produce validated still PNG sources inside GenArt; completed local Bifurcata worlds feed normal collage and saved-project paths. A copyable prompt and verified Gemini, Whisper Web and MLX links make the current lyric workflow actionable. The sourced roadmap separates shipped handoffs from optional downloaded transcription, native workers, deterministic moving adapters and portable originals. Local gates: actual-module Art Room invariant suite, typecheck/build, 21 Art Room cases (18 plus three focused passes after a label-selector correction), nine lyric-help cases, three caption/project regressions and seven mobile cases. **Live: 40/40** (21 Art Room, nine guide, three regression, seven mobile), including all three local-Bifurcata integration profiles; public JS/CSS/worker/SW bytes match the tested build. Code `3f3ede40`; Pages run `33989801143` green. Actual live Tidal Paper capture saved a 1200×900 image and project; fixture round trips preserved original bytes. Guide prompt-copy was visually exercised. Independent boundary/lifecycle audit passed. Cleanup: zero candidates. No new dependency or storefront entry; existing large-chunk/Browserslist and Actions runtime-deprecation warnings remain. Next capability: portable audio/video originals with session edits, alongside the bounded downloaded lyric-draft experiment described in the new roadmap. Moving HTML generators still require a deterministic time/recipe interface.


- **2026-09-05 · [AXIS:COLLAGE] C3711 — EDITABLE NATIVE ART RACK.** Before: one HTML starter and a flattened captured PNG. After: eight original art families, a template-first visual browser, up to eight composited layers with visibility/solo/order/blend, protected dice, geometry controls and looped parameter automation. Apply persists the recipe with its opening-frame PNG; selecting saved artwork reopens its layers. A revised source gets a new immutable ID with pins/crops/history remapped, and recovery retains its current bytes. Native art ticks without music, captions or video and is sampled once per unique source at requested output time; turn/dissolve, still, SVG, worker and offline video paths share its renderer. The export sheet offers an exact shared loop duration. **Gates:** typecheck and production build passed; 40/40 actual-module unit suites; two native-engine pixel profiles, two Stage integration profiles and one prior caption Stage regression; **58/58 production cases** (15 rack, 3 real video, 21 HTML/Bifurcata, 9 lyric-help, 3 caption/project and 7 mobile). These repeat the same 58 distinct local cases; development test corrections and targeted reruns are retained as evidence, not hidden. Independent division covered recipe/geometry, serialization and compositor integration; review-found undo/duration state bugs and a root-found dock recording gate were fixed and tested. Code `efdc4b9f`; Pages `33991651937` succeeded; deployed JS/CSS/worker/SW are byte-identical to the tested build. Manual public template, dice and hold controls inspected. Public exports decoded into 240 desktop frames at 30 fps and 192 frames at 24 fps for each mobile profile; all contain artwork. A real live `.collage`, 2066×1319 PNG, recipe JSON and 8-second MP4 were saved as examples. Wells: 0 new / 0 building; cleanup: 0 candidates; no new runtime dependency or storefront entry. Limits: native source rasters cap at 4096 pixels per side / 16 MP, browser video color/raster results differ, HTML still captures do not gain motion, and original imported audio/video packaging plus global overlay/shot sequencing remain future work.

- **2026-09-05 · [AXIS:COLLAGE] C3712 — PREVIEW-FIRST WORKFLOW.** User reported an unintuitive control wall and a playback viewport too small to see. The default project now opens with the full composition and a compact transport; one focused Add/Layout/Look/Motion/Text inspector or media Details takes space at a time. Templates lead the Art Room; layer actions and automation are disclosed on selection, with whole-art preview and an explicit return. Same-sample public measurements: desktop 111×199 → 273×487; phone 164×292 → 338×602; short landscape 19×34 → 88×157. Visible default buttons 19 → 11. **Gates:** 173 distinct local cases and **173/173 public browser cases** across Chromium, Mobile Chrome and Mobile Safari (legacy Stage tests cover Chromium/Safari), 40/40 unit suites, typecheck/build. Independent review found and fixed competing disclosures and short-screen focus loss. Migrated old selectors and fixed test assumptions are recorded in scars; no failed production gate is hidden. Native exports decoded to 240 desktop frames and 192 frames per mobile profile, all nonempty. Lyric/video exports retain timed text and their soundtrack; project/SVG/recovery and actual local Bifurcata capture passed. Code `496a17ba`; Pages `33995354619` green; public JS/CSS/worker/SW match the tested build. Wells: 0 new; cleanup: 0 candidates. Existing bundle-size/Browserslist and Actions deprecation warnings remain. Next owner reads this book and fleet release `persona500-collage-C3712-release`; continue portable audiovisual originals and authored sequencing without restoring an always-open control wall. Built-in transcription and moving HTML adapters remain roadmap work.
