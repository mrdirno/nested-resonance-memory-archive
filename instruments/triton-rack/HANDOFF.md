# TRITON-Rack × LuckyDreamer — build state

**As of:** 2026-09-02, rings 1–38 in `triton-rack.html`.
**Rule zero (unchanged):** both HTML files carry append-only ring/history blocks at
their very end. **Read the rings first.** Never edit or delete a ring; append one
per session. The donor keeps its own log format at its tail; both survive — that
is the merge law (Ring 5).

Round 1 (rings 1–19) executed the original brief: P0 mapping accuracy, the 4U
face, MIDI/WAV export, crate, Bank B, STRUM, a full BREAK pass. Round 2
(rings 20–25) executed the operator's simplification verdict (PLAY·DICE·SAVE,
theory bar, progression bank, hardware MIDI, second BREAK). Round 3
(rings 26–30) executed the third verdict with a THIRD DONOR (DreamDrummer,
committed beside LuckyDreamer): *"sounds like a typical arpeggiator… take
from sources with human timing… mixing and mastering is terrible… no way of
locking style or rhythm… the file has to reconfigure itself."* — the
drummer's correlated clock, the hook/bass cell engines, the mix rack + master
chain, locks on the dice, and KEEP (the file serializes a working copy of
itself carrying presets). Round 4 (ring 31) executed the fourth verdict:
*"the layering doesn't make sense… follow the process — drums first…
reinvent the dice roll for the AI age… build the song like an avatar, the
pieces are prebuilt, the engine seamlessly combines them… less clicks."* —
THE SONG AVATAR: five trait slots, three dealt candidates per trait, tap to
hear on the bar / tap the lit card to keep, the next trait deals itself; the
rail is the avatar and any filled slot remixes live; the whole TRITON rack
folds behind one "⚙ engine room" link. Round 5 (ring 32) executed the fifth
verdict: *"think like a producer… counterpoint instead of chords…
embellishments… a 2U rack space should populate under the player… dynamic
headroom… patching as dice/next/previous, never a list… an actual open
source library of human playing, quantized to any key any scale — the most
important part."* — THE PHRASE LIBRARY (mined from Groove MIDI CC-BY 4.0 and
OpenScore String Quartets CC0, judged by a 29-agent court, every phrase
re-verified against raw sources), THE COUNTER and THE EMBELLISH replacing
chords and lead, the groove field, the 2U rack shelf, and take-logged
dynamic headroom. Traits now: THE DRUMMER · THE LOW END · THE COUNTER ·
THE EMBELLISH · THE SHAPE. Round 6 (rings 33–34) executed the sixth verdict
by MEASUREMENT: the clipping was convicted at the tube waveshaper (raw bus
peaked 3.26; WebAudio hard-clamps past the curve domain) and fixed
structurally (MIX_BUS_TRIM 0.42; volume moved post-limiter), the SAVE
delivery hardened into persistent ⤓WAV/⤓MIDI chips, and VERB shipped — one
−/+ pill scaling every program's reverb send in 10% steps, default 50%.
Round 7 (rings 35, this round) absorbed a FOURTH DONOR (`dreamdrummer_22.html`):
*"load the sounds from dream drummer onto the Korg triton"* and *"could just
port the entire library over"* — the DD22 KIT ENGINE (all six drum voices +
the 11-kit bank, sliced verbatim-by-construction by `mine/dd22_port.js`, a
byte-compare fidelity gate in suite [8]), DD kits playable on every drummer
card via baked velocity layers through one `kitZone()` door with the TRITON
kit as per-hit fallback, the drums drawer one ring over TRITON + DD kits —
and the donor's SEVENTEEN DRUM LANGUAGES (KPAT cells + full style grammars,
verbatim) realized per-dream into dealable style drummers with MPC-math
swing, ghost floors, phrase-end fills, ensembles on this file's ported
percussion physics, and the 808 line ("the kick is the bassline") re-rooted
to any key and carrying the low end until a bass trait stands. Round 8
(ring 36) answered the eighth verdict — *"the offline render needs to stop
the track before it saves… dream drummer gives you three options wav the
midi or the entire project reloadable as a zip… investigate why it's
holding up, concurrency issues… you have distorting saws… make sure your
solutions are production grade"*: SAVE now STOPS the track and opens three
doors (**MIX** · **SCORE** · **SESSION**), the session zip **reloads** its
song through a ⤒ LOAD chip, the render's concurrency holes are closed, and
the saw distortion was convicted at the program insert (a hard clipper —
not feedback) and fixed structurally. Round 9 (ring 37) answered an open
verdict — *"leave no stone unturned"* — with the four things the rings had
been owing: THE FIVE-LENS BREAK COURT over the whole instrument (44
findings, 3 blockers: the envelope hold, a stored XSS from a bank file,
unvalidated fields into the conductor and the arp scheduler), THE BANK
COURT (all 128 programs measured; saturator headroom, the bell and formant
laws, three programs re-voiced), THE TAKE IN THE ZIP (a session reloads as
a re-renderable performance) and THE ADDRESS (a URL hash that regrows a
song, through the one validator) — plus the face at phone scale, a 4×
faster offline render and the kit bake off the main thread. Round 10
(ring 38) answered *"it's saving the search for sounds as well… it should
just save the song, structured, of the final selected choices"*: the doors
now bounce THE SONG — the final selections arranged from the top by the
same conductor, composed DRY and rendered — and a fifth door, JAM, keeps
the take exactly as played.

---

## 1. What is in this package

| file | what it is |
|---|---|
| `triton-rack.html` | The instrument (self-contained, no CDN/fetch/localStorage). The face is **THE SONG AVATAR** (round 4): a track is built like a game character — five trait slots (THE DRUMMER · THE LOW END · THE CHANGES · THE VOICE · THE SHAPE), the engine deals three prebuilt candidates per trait (curated dream identities + wildcard breeds; keys and bass voices; scale-matched named progressions; hook DNAs; loop/arc/song), tap a card to hear it swap in **on the bar** under everything kept, tap the lit card to keep it and the next trait deals itself; unfilled slots are muted, never faked; the rail is the avatar and tapping a filled slot remixes that trait live; a song stands in as few as five taps. Under the fold (one "⚙ engine room" link): the full Korg TRITON-Rack recreation — 128 programs + 16 user Bank B slots, 16 combis, Web MIDI in (hardware keyboards are first-class — the unit boots from a MIDI note, with a one-tap audio nudge for the autoplay law), DecentSampler export, EXB-LDR board with the donor's **ported percussion physics** (25 PERC_RECIPE voices) and 51 figures routed instrument-to-instrument, the **theory bar** (key, named progression, Roman numerals, the sounding chord — honest at every build stage), the 12-progression bank, the drummer's correlated clock + hook/bass cell engines, the mix rack + master chain. **THE TAKE** rolls from the moment anything plays and SAVE bounces it offline through the same engine into a normalized 24-bit WAV + SMF-1 with the player on a YOU track; ★ KEEP writes the standing song into a working copy of the file itself (the copy boots with the avatar rail rebuilt, remixable). Rings at tail. |
| `luckydreamer_3.html` | The first donor, byte-identical to the original upload. Reference and ground truth. **Do not modify it.** |
| `dreamdrummer_21.html` | The third donor (round 3), byte-identical to the upload. Source of the correlated human-timing science, the structural-consistency doctrine, the mix architecture, and the locks grammar (extraction: Ring 26). **Do not modify it.** |
| `dreamdrummer_22.html` | The fourth donor (round 7), byte-identical to the upload. Source of the DD22 kit engine (six drum voices, the 11-kit bank, Kit-as-a-bus) and the 17-style pattern library (KPAT cells + grammars + measured feel numbers), all sliced verbatim by `mine/dd22_port.js` (extraction: Ring 35). **Do not modify it.** |
| `mine/` | The phrase-library pipeline (round 5): SMF + MusicXML parsers (no deps), LDRP1 pack/unpack, extractors for Groove MIDI (CC-BY 4.0) and OpenScore String Quartets (CC0), structural pre-filter, the judges' decoder, the raw-source fidelity gate, the assembler and injector. See `mine/README.md` — the library is re-runnable and extensible. Round 7 adds `mine/dd22_port.js`: the DD22 verbatim slicer/injector (23 line-ranged donor slices → the `/*DD22-BEGIN*/…/*DD22-END*/` block; re-run it after donor-slice changes; suite [8] byte-compares). |
| `figure-instrument-map.json` | P0 provenance: all 51 figure→instrument assignments with evidence classes (A: donor voices the cell · B: donor voice tables · C: reasoned) and donor line anchors. The *playing* copy is `LDR_MAP` inside the artifact; this file is the argument for it. |
| `extracted-data.json` | Donor physics + figure catalog + samba style excerpt, eval'd out of the donor (not retyped). |
| `tests.js` | Node suite, no deps: `node tests.js`. Suites: [0] syntax · [1] bank schema · [2] figure graft · [3] conductor + theory engine + progression bank + human hand + **the song avatar** (40 seeds of card validity, composeP mute honesty, drummer-as-clock, shape→section laws) + audition improviser · [4] WAV writer · [5] mapping + **measured physics** (DFT fundamentals, T60s, pitch/damp bake, 13 pinned routes, zero-fallback sweep) · [6] take→SMF pipeline (held-note durations, tempo map, meter, GM preview, lead-in) · [7] Bank B validator/parser. · **[11] the take codec + the address** (nine roles round-trip, hostiles refused, the inflate cap stopping a bomb) · **[12] the bank court** (saturator headroom identity, the bandpass-on-sine law, bell/formant laws, lazy render + worker bake + tape laws by regex/sandbox); every round-9 gate mutation-tested · **[11] the take codec + the address** (round 9) · **[12] the bank court** (saturator headroom, bell/formant laws, the bandpass-on-sine data law) · **[13] the song bounce** (round 10: SONG_BARS follows sectFor, every hit path DRY, doors) |
| `browser-tests.js` | Headless-Chromium harness (`npm i playwright-core`; finds Chromium at `/opt/pw-browsers/...` or `CHROMIUM=` env): layout law, the avatar face (rail + hand + four buttons + engine-room fold), hardware-MIDI cold boot + nudge law + pedal/bend through `window._midiInject`, **the full build walkthrough** (deal → hear → keep across all five traits with the theory bar honest at each stage, the drummer's clock measured on the figure lane of the rolling tape, chords rolled by the hand, the hook breathing, remix + one-tap re-keep, trait-jump honesty probes), figure chip mid-dream handoff, Bank B write flow + hostile-name XSS, a full SAVE bounce read back from the downloads (WAV peak/RMS/crest + MThd + YOU track), duck survival after the bounce restore, KEEP copy booted and replayed with the rail rebuilt, power-off law, STRUM, improviser, voice-cap assertion, phone-scale, zero console errors. Screenshots `4u-face.png`.; **round 9:** the whole-bank loudness probe, the phone-scale touch law, take.json in the zip + LOAD-with-take + PLAY regrows, LINK/ADDRESS in a fresh page (content-exact regrow, hostile hashes, a VALID song wearing hostile strings), the lazy render counted at startRendering, the kit bake off the main thread |

## 2. What the accuracy fix settled (P0, rings 10–12; unchanged)

- The donor's FIG catalog is **data-only** (figHits has no callers); ground truth
  is its live engine: KPAT cells, the batucada style's perc rows, C12_ENS voice
  tables, TIMELINE_16 plan voices. All 51 figures route through `LDR_MAP`
  accordingly; stroke tokens reroute (martillo `hO`→bongoL, quinto `S`→djembeS,
  Big Four `C`→crash), tone rows split agogoL/agogoH, surdos land at the donor's
  own pitches (primeira = 46 Hz, terceira = the donor's congaL cutter).
- The physics is the donor's synthesis **ported number-for-number** (ModalBank,
  TunedDrum with Duffing sag, MetalVoice, ShakeVoice, Sat/Transient/AD/SVF…),
  rendered offline through the exact sample loop into cached velocity-layered
  buffers — sampler cost at play time, physical-model truth, measurable by test.
- Three gates hold it: `ldrMapCheck()` at load, suite [5] in CI, and the
  browser harness's zero-fallback assertion.

## 3. Round 2 in five cuts (rings 20–24)

1. **Ring 20 — SAVE replaces RECORD.** The ScriptProcessor recorder was the
   crappier variant of what the donor already solved. THE TAKE logs every
   engine event and every human note (durations patched on release); SAVE
   bounces the log offline through the same engine (globals swap, FX graph
   rebuilt, voice cap 1024, schedulers gated) → normalized 24-bit WAV + SMF-1
   with meter, GM preview programs, and the player's YOU track.
2. **Ring 21 — the face goes quiet.** Strip, crate, HALF-DICE, LEDs, preset
   select: gone. PLAY · DICE · SAVE and the theory bar (the strip's exact
   footprint). Figures live in the Rhythm tab where their 51 chips always were.
3. **Ring 22 — the progression bank.** A chord is a diatonic degree OR a spec
   `{r,iv,roman}` — how borrowed chords enter a key. Twelve named changes;
   DICE draws them scale-matched; Guaguancó cadences on a real V7; one
   realization function (`chordSpecFor`) feeds voices, bass, motif and MIDI.
4. **Ring 23 — the human hand.** Per-part feel at schedule time (bass ahead,
   chords in the pocket, lead loosest, pads roll like a hand), deterministic
   per seed, bounded, carried identically into live sound, take, bounce, .mid.
   The percussion figure stays machine-tight: it is the ensemble's clock.
5. **Ring 24 — the hardware wire.** A MIDI note boots the unit; the suspended-
   context trap gets a one-tap nudge (`ctxEnsure`); `window._midiInject`
   drives the exact controller wire, so the harness plays bytes, not stubs.

## 3b. Round 3 in five cuts (rings 26–30)

1. **Ring 26 — the third donor read.** DreamDrummer extracted by five lenses:
   correlated clock (wander fields, ensemble coupling, limb means), structure-
   not-search consistency, per-lane dice streams + locks, the full mix chain,
   persistence (none self-reconfiguring — that design is ours).
2. **Ring 27 — the arpeggiator dies.** The drummer's clock (keyed 1/f, every
   role coupled, per-dream humanity dial, figure at coupling 1.0), the HOOK
   engine (Q/A/B cells with rests, contour, color, voice-led cadences), the
   bass CELL (skeleton-gated onsets, chord-relative pool, intent windows).
3. **Ring 28 — the mix earns its console.** Role strips, the scheduled duck
   (kick-keyed gain dips — deterministic, offline-identical), the master
   chain (tilt/air EQ, parallel comp, glue, tube, cubic ceiling), mastered
   bounces (−17 dBFS RMS target, peak-capped).
4. **Ring 29 — locks + KEEP.** Tap the key card / the title to lock harmony /
   groove through DICE; ★ KEEP writes the current dream into the presets
   block and the file downloads a WORKING COPY OF ITSELF (rings included).
5. **Ring 30 — third BREAK.** Five lenses, 12 findings verified: 9 confirmed
   (worst: preset chip mid-dream wiped the take; KEEP's scrub blanked the tab
   panes), all fixed at the root; 3 refuted and recorded.

## 3c. Round 4 in five cuts (ring 31)

1. **The avatar core.** Pure functions first: candidate generators per trait
   (candDrums/candBass/candChords/candLead + FORMATS), `composeP()` wearing
   the kept traits together with honest mutes for unfilled slots, per-part
   seeds (the drummer's seed IS the world clock; bseed/lseed ride the
   preset), shape→section laws (`_building` holds a steady groove).
2. **The DEAL face.** Trait rail + three-card hand replace all browsing:
   tap to hear (bar-line swap), tap the lit card to keep, next trait deals
   itself and auditions card 0 unasked. Keep advances to the FIRST UNFILLED
   trait, so remixing a filled slot re-keeps in one tap.
3. **The fold.** The entire TRITON rack (tabs, programs, keys) hides behind
   one "⚙ engine room" link — a body-class CSS fold, no DOM surgery, so the
   KEEP serializer still round-trips.
4. **The figure lane.** A `ln` tag ("fig"/"comp") threads the main figure vs
   companions through the take log — same-recipe-name collisions had
   interleaved the kit-wave and perc-wave under one name and read the
   drummer's correlated clock as anti-correlated white.
5. **BREAK-lite + gates.** Un-kept auditions no longer outlive a trait jump
   (the rail is the avatar — the ear gets the kept song back on the bar);
   stage-4 hands (FORMATS verbatim) light the KEPT format, not card 0. Both
   gated in the harness alongside the full build walkthrough.

## 3d. Round 5 in five cuts (ring 32)

1. **The library** (`mine/` holds the whole pipeline + court verdicts).
   Open human-performance corpora fetched and license-verified, parsed by
   no-deps SMF/MusicXML readers, sliced to ~163k candidates, packed into
   LDRP1 (drums keep the player's per-event deviation; lines are
   semitones-from-tonic — any key, any scale), pre-filtered to 858, judged
   by a 26-judge + 3-auditor court (256 named picks; nine parser
   convictions fixed, picks re-bound to the corrected extraction), and
   every embedded phrase re-derived from its raw source at a rediscovered
   window offset: **222/222 pass** — 116 grooves · 20 fills · 25 bass ·
   41 counters · 20 licks, 66KB packed.
2. **The producer traits.** THE COUNTER replaces block chords: a sparse
   human counter-line leaves the middle open for a vocalist; the chord is
   one soft roll at section pivots. THE EMBELLISH replaces the lead: short
   gestures at phrase ends, voice-led into the coming change, silence
   otherwise.
3. **The groove field.** A library drummer's per-step median deviation
   becomes the timing field the melodic parts ride; the paired style-matched
   FILL takes the whole bar at phrase ends and wherever `sectFor` turns —
   the song moves on the finishes.
4. **The rack shelf.** Every kept trait materializes as a 2U unit under the
   conductor: name, voice, ‹ › walks the voice drawer, ◇ deals another take
   straight into the song on the bar, live meter per strip (analyser taps in
   `mkStrip`). Patching is never a list.
5. **Dynamic headroom.** `mixStageFor(n)` — deterministic trims from the
   active-part count (low end yields least, limiter drive eases) — applied
   at the bar a part lands and logged into the take as `mix` events, so the
   offline bounce replays the exact console moves.

## 3e. Round 6 in three cuts (rings 33–34)

1. **The clipping, measured.** Four analyser taps under a full band: the raw
   mix bus peaked 3.26 and drove the tube waveshaper past its curve domain,
   where WebAudio hard-clamps (flat-tops + oversampling ring). Fix:
   `MIX_BUS_TRIM` 0.42 seats the chain; the VOLUME knob moved post-limiter.
   Two standing harness gates: tube ≤0.25% samples ≥0.985; destination <0.95.
2. **SAVE delivery.** Persistent ⤓WAV/⤓MIDI chips on the face (a second
   programmatic download is blocked in real browsers; blob revoke now 300 s),
   with a render ticker.
3. **VERB.** One −/+ pill, 10% steps, default 50%, scaling every program's
   reverb send; carried by presets and KEEP; identical in the bounce.

## 3f. Round 7 in five cuts (ring 35)

1. **The DD22 kit engine, verbatim by construction.** `mine/dd22_port.js`
   slices 23 exact line ranges from `dreamdrummer_22.html` (atoms · studio
   bus · ModalBank+MODES · wavetables · KickVoice/SnareVoice/MetalVoice/
   TunedDrum/ShakeVoice/ClapVoice · Kit-as-a-bus · the 11-kit bank ·
   metricWeights · the whole k05 grammar) into the `DD22` IIFE between
   markers; the only transform is a 2-line rewrap. Suite [8] REBUILDS the
   block from the donor and byte-compares — the port cannot rot invisibly.
2. **DD kits on every drummer.** Velocity-layered stereo buffers baked off
   the hit path (`ddWarm`, core hits first), played through `ddHit` → the
   kit strip (meters/duck/headroom see them), hat choke kept at play time,
   `kitZone()` the single door with the TRITON kit as per-hit fallback.
   Cards carry `dkit`; the drums drawer is ONE ring over TRITON + DD kits;
   presets/KEEP validate and carry it; takes log role `dd`, GM-mapped in
   the MIDI, replayed in the bounce (kick keys the duck).
3. **The 17 languages.** KPAT/KPAT12 cells + full style grammars sliced
   verbatim; `kRealize()` (glue) walks them into one deterministic 2-bar
   plan — kit events on TRITON zones, ensembles on this file's LDR_RECIPE
   physics, the Bell cycle riding this file's own bembe figure, MPC-math
   swing baked into step values (swing:0 = machine, NOT MPC 0% — ring 35's
   conviction), ghost floors, phrase-end fills, BREAK dropout.
4. **The 808 line.** Style sub grammars stored as semitone offsets,
   re-rooted to the song's tonic at play time, played on the DD22 kick
   buffer retuned via playbackRate with drill slides gliding between
   different notes; carries the low end only while no bass trait stands;
   role `dd8` on the tape → bass channel in the MIDI → replayed offline.
5. **Gates.** Node suites [8]/[9] (fidelity, merge law, measured 808/choke/
   pan physics, dembow-verbatim, swing math, preset law, deal spread);
   harness: a forced knock/hyphyK dream lands dd hits with the limiter
   inside the round-6 ceiling, the drawer walks the shelf and wraps, the
   bounce renders the language, `DD_LVL` measured down to 1.0.

## 3g. Round 8 in five cuts (ring 36)

1. **SAVE stops the track, then offers three doors.** `transportStop()`
   (dream + figure engine + arp + all notes off + duck flush + tape close +
   PLAY UI) runs before anything renders — the donor can keep playing only
   because it renders on a second engine in a Worker; this file swaps the
   GLOBAL graph, so the stop IS the equivalent. Doors: **MIX** (one WAV) ·
   **SCORE** (MIDI, instant, no render) · **SESSION** (stems + mix + score +
   project.json, one zip). Percent progress from `OfflineAudioContext.suspend`
   checkpoints. The take survives the stop; a fresh PLAY clears the offer.
2. **The session zip reloads.** `project.json` carries the song in the
   preset law's shape; `zipReadStore` (store-only central-directory reader,
   hostile by default) + a ⤒ LOAD chip read it back through
   `presetParse`/`presetValidate` and stand it up via the preset chip-tap
   path. Imports never evict the user's own ★ rail. The donor has NO zip
   reader — this exceeds it.
3. **Concurrency closed.** `exporting` now gates applyFXP (force flag for
   the exporter), startWith, ldrToggle, powerOff, pulseAt, dreamPans, the
   mod wheel, pitch bend, the meter rAF loop, wall-clock kill timers and the
   volume knob; the render yields every 1024 events. Stems carry the mix's
   OWN duck automation and mastering gain (capped so a hot stem cannot clip
   the writer); VERB and the FX program are pinned for the whole export.
4. **The saws, convicted at the insert.** Not feedback (loop gain fb² ≤ .38;
   applyFXP never calls connect). `driveCurve`'s k=a·60+1 was a hard clipper
   at the common drive .2, fed by an untrimmed bus. Fixed: a headroom
   pre-trim (curve domain ±4 of bus), k=1+a·7, reference normalization at
   bus 0.5, the wet/dry pair normalized by its own sum, and per-voice
   osc-stack normalization (the amp LFO rides it too — it writes the same
   gain param additively). Measured: 0.00 dB drive-vs-clean at the
   reference, where the old law ran +4.8 dB at bus 0.3.
5. **Three gates that could not fail were rebuilt.** The "does the insert
   rail" check tapped a node the curve's own normalization bounds; the
   session-zip clip checks read bytes the 24-bit writer had already clamped;
   the drive-law check re-derived the math instead of reading `applyFXP`.
   All three now measure the mechanism at its cause, and every new gate was
   mutation-tested (revert the fix, confirm the gate fires).

## 3h. Round 9 in five cuts (ring 37)

1. **The five-lens BREAK court, finally sat.** Five independent lenses
   (producer · audio engineer · attacker · performance · correctness) over
   the WHOLE instrument, each with a headless-Chromium probe kit, ranked
   findings, adversarially verified, fixed down the ladder. The court's
   blockers: a written duration shorter than a program's attack left the
   note SILENT for its length then swelled and held (the dur path queued the
   release before the ramp — `holdEnv` now holds the envelope analytically
   at the release moment); Bank B `cat` reached the LCD innerHTML raw
   (stored XSS from a bank file); `leadOct`/`comps`/`tempo`/`arpDefault`
   were unvalidated on the way into the conductor and the arp scheduler
   (a tick storm, a dead PLAY, a tab freeze). Every fix carries a gate and
   every gate was mutation-tested.
2. **The bank court.** All 128 programs rendered offline and measured
   (single note through the insert, triads through the full chain, tube
   input with the limiter/tube bypassed). Convicted: 60 of 120 programs
   drove the master tube PAST its curve domain on a vel-1 triad from the
   keyboard (the round-6 trim staged the dream mix, not the player) — every
   saturator now wears the round-8 headroom law (`SAT_HEADROOM`, `mkSat`);
   bells summed their partials into the VCA and were the hottest peaks in
   the bank (the sqrt partial-sum law put the family's median on the bank's
   median); every VOX formant program sat 8–10 dB under the bank
   (`VOX_MAKEUP`); three programs were inaudible by construction (a Q 4–6
   bandpass on a sine: −31 to −36 dB) and were re-voiced. Standing gates:
   node suite [12] (headroom transfer identity, the bandpass-on-sine data
   law, the bell/vox laws) and a harness probe that renders the whole bank
   every run.
3. **The take rides in the zip.** `take.json` (the take codec: programs by
   bank index, foreign programs re-validated, every field ranged, 40k
   events / 600 s caps) joins the session zip; LOAD of a zip with a take
   comes back STOPPED under its song's console with the doors open — bounce
   it again at another VERB, pull a stem you did not pull — and PLAY regrows
   the song fresh. A bare project.json still stands the song up playing.
4. **The address.** The donor's `#address`, for a song: the preset-law JSON
   deflated and base64url'd into the URL hash, booting through the SAME
   hostile-file gate as the presets tag and project.json (one schema, one
   validator, one door — a hand-packed base36 codec would be a second
   format to keep honest). An address STAGES its song on the rail; PLAY
   starts it (the boot has no gesture). A LINK door writes it. Inflate bomb
   capped, hostile hashes refused aloud.
5. **The face at phone scale.** The court measured the ★ rail, ⤒ LOAD and
   the door chips at 7–8 px on a 390 px phone — the file's own touch law
   (≥45 px) broken by the controls that exist FOR phones. Below .62 scale
   they leave the scaled 4U and become a CSS-pixel strip beneath it; a
   probe holds the law every run.

## 3i. Round 10 in three cuts (ring 38)

1. **The doors bounce the song.** `songEvents(p)` runs the ONE conductor
   bar by bar against a scratch tape with `DRY` set — every hit path
   (`spawnVoice`, `ddHit`, `ddSub`, `drumHitP`) logs and returns before
   touching audio, UI pulse timers stay unarmed, the duck is muted — for a
   4-bar INTRO plus the shape's section list once through (`SONG_BARS`:
   arc/song 68, loop 36), then puts back everything it touched. MIX, SCORE
   and SESSION render that composition; the SESSION zip's take.json is the
   composed song, so LOAD restores a re-renderable song. The render awaits
   the kit's bake first (the worker), and a DRY `ddHit` logs whether or not
   the kit has baked, so the song never carries a fallback hit.
2. **JAM keeps the take.** A fifth door bounces the performance exactly as
   before (WAV + MIDI, `-jam`), with the player's own keys in it.
3. **Gates.** Node suite [13] (SONG_BARS follows `sectFor`'s own lists,
   every hit path proven to log-and-return DRY, the door wiring, the
   restore). Harness: the song composes DRY in-page (bar count, density,
   deterministic twice, no `you` role, the live take untouched), MIX renders
   it to the composed length plus tail, JAM keeps the YOU track, five doors,
   LOAD restores the composed song.
4. **The verify pass (round 10b).** Two skeptic lenses were cast over the
   diff. The DRY-composition lens ran and convicted four things, all fixed:
   the composition left `verbSet` on the live graph (now held and put
   back), armed per-bar readout timers (gated), sized a shape-less song as
   arc (defaults to loop), and could flush the live duck (gated). The
   doors+gates lens died on the session limit twice; it was walked by hand
   instead on 2026-09-02 — the export guard, the 40 ms bake poll under the
   `exporting` gate (PLAY/LOAD/power refuse while it holds), the dead-worker
   fallback (sync bake, 15 s cap), the empty-composition fallback (renamed
   `-jam`, honestly), session LOAD → `applyDream` sets `DREAM.p` so MIX
   recomposes the same song from the same seed, blob revocation across a
   JAM-after-MIX, `takeStart` clearing the doors. No defect found; the
   fleet pass over that lens is still the honest gate and remains owed.

## 4. Baseline bugs found and fixed along the way (rings 13, 18, 19; verified against the pristine upload)

1. **The dock never worked** — init IIFE died on a null before wiring; waits
   for DOMContentLoaded now (Ring 13).
2. **The tab row overflowed phones** (Ring 13).
3. **The 62-voice ledger leaked on steal** — `unreg` is exactly-once now (Ring 18).
4. **`esc()` was a no-op** — every "escaped" interpolation was raw (Ring 19).
5. **ENTER+POWER test mode was unreachable** (Ring 19).
6. **Live input during a DecentSampler export played into the offline render**;
   input gated, export boots the live graph first (Ring 19).
7. **Enabling the arp over held keys stranded their voices** (Ring 19).
8. **The recorder survived power-off** (Ring 19; the recorder itself is gone
   as of Ring 20 — power-off now pauses the take and keeps it saveable).

## 5. Constraints that must survive every session (unchanged)

Single self-contained HTML per artifact; no CDN, no fetches, no localStorage;
no Korg ROM data or firmware ever (all sound synthesized; honesty notes stay);
AudioContext only from a user gesture (quickBoot pattern — and the Ring 24
nudge for the hardware-MIDI edge); rings append-only, newest last, donor's
history stays in the donor; user-facing reports are one paragraph, process
lives in rings. Run `node tests.js` before AND after every change; run
`browser-tests.js` for anything touching UI, scheduling, or audio wiring. The
ear test remains the final gate on any mapping change — and A-class entries in
the map are the donor's hand: do not move them on taste.

## 6. Open edges (from the rings, for the next bench)

- FiloBass (48 pro jazz bass transcriptions) and GuitarSet (human comping +
  solos), both CC-BY 4.0, were blocked by the build bench's egress policy
  (zenodo.org). The `mine/` pipeline is ready for them (Ring 32).
- The groove field rides per-step medians; the full bar-by-bar deviation
  series is in the data — should the band follow the drummer bar-by-bar?
  (Ring 32)
- Dealer learning: phrases carry the court's tags; should kept choices
  weight future hands? (Rings 31/32)
- Promotion: the verdict asked for "promoting the tracks that sound the
  dopest, like playlisting" — KEEP holds 8; should kept songs rank, and
  should the dealer learn from what gets kept? (Ring 31)
- The 808 line yields to a kept bass — a dealable "THE 808" low-end card
  would let hyphy keep its bassline by choice (Ring 35).
- trapK/hyphyK kicks carry `tuned:1` — plain kick hits still land at patch
  pitch; per-key baked kicks would finish the donor's intent (Ring 35).
- The donor's k06 fill engine and the KSNARE_POOL/KHAT_POOL per-style
  alternate architectures stayed behind with the knock kit bank — liftable
  next bench (Ring 35).
- The SESSION door still renders one pass per lane; lazy instantiation made
  each pass 4× faster, but one pass with N recorders is the honest end state
  (Rings 36/37).
- The take's `you` role survives a zip round-trip as a re-renderable
  performance; replaying it LIVE over the regrown band (an overdub track) is
  a new transport mode — the regrow is content-exact, so it is buildable
  (Ring 37). The song bounce (Ring 38) leaves the player's keys to the JAM;
  carrying keys played over the FINAL world into the song bounce means
  choosing which section of a 68-bar arrangement a 12-bar overdub lands in.
- The loop bounce is 32 bars of groove by fiat; a loop's natural length is
  the phrase library's own cycle × a few — worth deriving. The conductor has
  an INTRO but no OUTRO: the song bounce stops on a bar line and rings out
  through the tail (Ring 38).
- The trait rail slots (12 px), VERB −/+ (10 px) and the rack ‹ › ◇ (18 px)
  still break the touch law at phone scale; the chips went first — the rest
  is a phone LAYOUT of the 4U, not a scale (Ring 37).
- The address is 342 chars for a full song; a dictionary-primed deflate
  would roughly halve it, but CompressionStream has no dictionary API and an
  inline inflater is the second implementation the round refused (Ring 37).
- The bank court judged C4 at vel 1; a court over the RANGE (C2–C6, vel
  .3–1) would find the key-tracking and velocity-law drifts the single note
  only half-showed (Ring 37).
- A listening pass on the mallets under the sqrt partial law (marimba −17,
  toy piano −16 dB momentary) against the keys (Ring 37).
- The insert is level-neutral at the reference bus but, like any saturator
  mixed with dry, still runs +0.9 dB at bus 0.1 and −1.7 dB at bus 2 for
  drive .2 — that IS drive's compression character, now centred rather than
  bolted on as makeup. Worth a listening pass to confirm it reads as
  character and not as a compressor (Ring 36).
- Hand size: is 3 cards right at phone scale? Long-press to re-deal one
  trait? (Ring 31)
- Enharmonic spelling: the theory bar spells sharps-only (A#maj7 where a flat
  key wants B♭maj7); a per-key table would read like the book (Ring 24).
- Swing, done honestly: the FIGURE must swing first and the band lean on it —
  figAnalysis would need a swing-aware grid (Rings 23/22).
- Secondary dominants (V7/x) as a bank "tension" option; prog-length-aware
  section phrasing for the 12-bar blues (Ring 22).
- MIDI clock in (0xF8) to sync the conductor to a DAW; a velocity remap
  option for hardware keyboards (Ring 24).
- Kit-lane figures (caixa, cavacha, pressRoll, marches) still speak TRITON —
  breed kick/snare/hat recipes from the donor's constructors (Rings 10/11).
- The export-vs-live globals swap is gated but the honest refactor threads
  ctx/bus as parameters (Ring 19).
- Reverse graft: the 128 programs riding back into LuckyDreamer (Ring 5).
