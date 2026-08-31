# TRITON-Rack × LuckyDreamer — build state

**As of:** 2026-08-31, rings 1–31 in `triton-rack.html`.
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
THE SONG AVATAR: five trait slots (THE DRUMMER · THE LOW END · THE CHANGES ·
THE VOICE · THE SHAPE), three dealt candidates per trait, tap to hear on the
bar / tap the lit card to keep, the next trait deals itself; the rail is the
avatar and any filled slot remixes live; the whole TRITON rack folds behind
one "⚙ engine room" link.

---

## 1. What is in this package

| file | what it is |
|---|---|
| `triton-rack.html` | The instrument (self-contained, no CDN/fetch/localStorage). The face is **THE SONG AVATAR** (round 4): a track is built like a game character — five trait slots (THE DRUMMER · THE LOW END · THE CHANGES · THE VOICE · THE SHAPE), the engine deals three prebuilt candidates per trait (curated dream identities + wildcard breeds; keys and bass voices; scale-matched named progressions; hook DNAs; loop/arc/song), tap a card to hear it swap in **on the bar** under everything kept, tap the lit card to keep it and the next trait deals itself; unfilled slots are muted, never faked; the rail is the avatar and tapping a filled slot remixes that trait live; a song stands in as few as five taps. Under the fold (one "⚙ engine room" link): the full Korg TRITON-Rack recreation — 128 programs + 16 user Bank B slots, 16 combis, Web MIDI in (hardware keyboards are first-class — the unit boots from a MIDI note, with a one-tap audio nudge for the autoplay law), DecentSampler export, EXB-LDR board with the donor's **ported percussion physics** (25 PERC_RECIPE voices) and 51 figures routed instrument-to-instrument, the **theory bar** (key, named progression, Roman numerals, the sounding chord — honest at every build stage), the 12-progression bank, the drummer's correlated clock + hook/bass cell engines, the mix rack + master chain. **THE TAKE** rolls from the moment anything plays and SAVE bounces it offline through the same engine into a normalized 24-bit WAV + SMF-1 with the player on a YOU track; ★ KEEP writes the standing song into a working copy of the file itself (the copy boots with the avatar rail rebuilt, remixable). Rings at tail. |
| `luckydreamer_3.html` | The first donor, byte-identical to the original upload. Reference and ground truth. **Do not modify it.** |
| `dreamdrummer_21.html` | The third donor (round 3), byte-identical to the upload. Source of the correlated human-timing science, the structural-consistency doctrine, the mix architecture, and the locks grammar (extraction: Ring 26). **Do not modify it.** |
| `figure-instrument-map.json` | P0 provenance: all 51 figure→instrument assignments with evidence classes (A: donor voices the cell · B: donor voice tables · C: reasoned) and donor line anchors. The *playing* copy is `LDR_MAP` inside the artifact; this file is the argument for it. |
| `extracted-data.json` | Donor physics + figure catalog + samba style excerpt, eval'd out of the donor (not retyped). |
| `tests.js` | Node suite, no deps: `node tests.js`. Suites: [0] syntax · [1] bank schema · [2] figure graft · [3] conductor + theory engine + progression bank + human hand + **the song avatar** (40 seeds of card validity, composeP mute honesty, drummer-as-clock, shape→section laws) + audition improviser · [4] WAV writer · [5] mapping + **measured physics** (DFT fundamentals, T60s, pitch/damp bake, 13 pinned routes, zero-fallback sweep) · [6] take→SMF pipeline (held-note durations, tempo map, meter, GM preview, lead-in) · [7] Bank B validator/parser. |
| `browser-tests.js` | Headless-Chromium harness (`npm i playwright-core`; finds Chromium at `/opt/pw-browsers/...` or `CHROMIUM=` env): layout law, the avatar face (rail + hand + four buttons + engine-room fold), hardware-MIDI cold boot + nudge law + pedal/bend through `window._midiInject`, **the full build walkthrough** (deal → hear → keep across all five traits with the theory bar honest at each stage, the drummer's clock measured on the figure lane of the rolling tape, chords rolled by the hand, the hook breathing, remix + one-tap re-keep, trait-jump honesty probes), figure chip mid-dream handoff, Bank B write flow + hostile-name XSS, a full SAVE bounce read back from the downloads (WAV peak/RMS/crest + MThd + YOU track), duck survival after the bounce restore, KEEP copy booted and replayed with the rail rebuilt, power-off law, STRUM, improviser, voice-cap assertion, phone-scale, zero console errors. Screenshots `4u-face.png`. |

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

- Promotion: the verdict asked for "promoting the tracks that sound the
  dopest, like playlisting" — KEEP holds 8; should kept songs rank, and
  should the dealer learn from what gets kept? (Ring 31)
- A full five-lens BREAK court on the builder (like rings 19/25/30) is owed
  next round; ring 31 shipped with a BREAK-lite only (Ring 31).
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
