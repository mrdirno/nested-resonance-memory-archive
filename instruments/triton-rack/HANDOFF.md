# TRITON-Rack × LuckyDreamer — build state

**As of:** 2026-08-30, rings 1–18 (+19 pending in `triton-rack.html`).
**Rule zero (unchanged):** both HTML files carry append-only ring/history blocks at
their very end. **Read the rings first.** Never edit or delete a ring; append one
per session. The donor keeps its own log format at its tail; both survive — that
is the merge law (Ring 5).

The original handoff brief (P0 mapping accuracy → P1 4U face → P2/P3 backlog) is
**fully executed**; this file now describes what stands and where the open edges
are. The prior brief's text lives in git history and in Rings 8–9.

---

## 1. What is in this package

| file | what it is |
|---|---|
| `triton-rack.html` | The instrument (~305 KB, self-contained, no CDN/fetch/localStorage). Korg TRITON-Rack recreation: 128 programs + 16 user Bank B slots, 16 combis, Web MIDI in, DecentSampler export, EXB-LDR board with the donor's **ported percussion physics** (25 PERC_RECIPE voices) and 51 figures routed instrument-to-instrument, Dream Conductor v2 with a **4U face** (scope, part LEDs, RECORD/DICE/PLAY/HALF pads, dream+figure+crate tile strip), WAV **and MIDI** take export, seed crate, STRUM arp, audition improviser. Rings at tail. |
| `luckydreamer_3.html` | The donor, byte-identical to the original upload. Reference and ground truth. **Do not modify it.** |
| `figure-instrument-map.json` | P0 provenance: all 51 figure→instrument assignments with evidence classes (A: donor voices the cell · B: donor voice tables · C: reasoned) and donor line anchors. The *playing* copy is `LDR_MAP` inside the artifact; this file is the argument for it. |
| `extracted-data.json` | Donor physics + figure catalog + samba style excerpt, eval'd out of the donor (not retyped). |
| `tests.js` | Node suite, no deps: `node tests.js`. Suites: [0] syntax · [1] bank schema · [2] figure graft · [3] conductor + HALF-DICE + crate + audition improviser · [4] WAV writer · [5] mapping + **measured physics** (DFT fundamentals, T60s, pitch/damp bake, 13 pinned definition-of-done routes, zero-fallback sweep) · [6] SMF MIDI writer · [7] Bank B validator/parser. |
| `browser-tests.js` | Headless-Chromium harness (`npm i playwright-core`; finds Chromium at `/opt/pw-browsers/...` or `CHROMIUM=` env): touch-law geometry, live conduction with zero mapping fallbacks, dice + HALF-DICE mid-flight, crate pin/replay by seed, Bank B write flow, record UI mirroring, STRUM, improviser, voice-cap assertion, phone-scale checks, zero console errors. Screenshots `4u-face.png`. |

## 2. What the accuracy fix settled (P0, rings 10–12)

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

## 3. Baseline bugs found and fixed along the way (verified against the pristine upload)

1. **The dock never worked** — `#fab` renders below the scripts; the init IIFE
   died on a null before wiring fabPlay/fabDice/fabRec or the preset-change
   listener. Init now waits for DOMContentLoaded (Ring 13).
2. **The tab row overflowed phones** — 413 px scrollWidth at 380 px; tabs wrap
   3+3 under 520 px (Ring 13).
3. **The 62-voice ledger leaked on steal** — shift-before-kill made `unreg`'s
   indexOf skip the decrement; under load activeVoices inflated (measured 291)
   until every voice was stolen on arrival. `unreg` is exactly-once now
   (Ring 18).
4. **`esc()` was a no-op** — every "escaped" LCD/pane interpolation was raw
   (weaponizable once Bank B/crate imports landed); it escapes for real now
   (Ring 19).
5. **ENTER+POWER test mode was unreachable** — window pointerup cleared
   `entHeld` before the power button's click; the combo arms at the power
   button's pointerdown now (Ring 19).
6. **Live input during a DecentSampler export played into the offline render**
   (globals swap), and exporting before first power-on wedged the boot path;
   input is gated and export boots the live graph first (Ring 19).
7. **Enabling the arp over held keys stranded their voices forever** (noteOff's
   arp early-return); the arp toggle now releases held stacks (Ring 19).
8. **The recorder survived power-off** with a frozen timer and takes spliced
   across power sessions; power-off now stops the tape (Ring 19).

## 4. Constraints that must survive every session (unchanged)

Single self-contained HTML per artifact; no CDN, no fetches, no localStorage;
no Korg ROM data or firmware ever (all sound synthesized; honesty notes stay);
AudioContext only from a user gesture (quickBoot pattern); rings append-only,
newest last, donor's history stays in the donor; user-facing reports are one
paragraph, process lives in rings. Run `node tests.js` before AND after every
change; run `browser-tests.js` for anything touching UI, scheduling, or audio
wiring. The ear test remains the final gate on any mapping change — and A-class
entries in the map are the donor's hand: do not move them on taste.

## 5. Open edges (from the rings, for the next bench)

- Kit-lane figures (caixa, cavacha, pressRoll, marches) still speak TRITON —
  breed kick/snare/hat recipes from the donor's kit()/snare() constructors so
  physics mode covers all 51? (Rings 10/11)
- A scheduler transcript test — assert a bar of bembé lands its 7 hits at the
  written pulses (Ring 12).
- MIDI: rolling pre-roll capture; GM program guesses per channel (Ring 14).
- The second half-dice (keep harmony, re-roll the figure); LED pulse on cut;
  cut-depth in the readout (Ring 15).
- Crate entries could carry the ring number they were pinned under; a bundle
  export (crate + Bank B + takes) (Rings 16/17).
- STRUM direction by strum-count; audVary echo interval by patch category;
  voice-count trace on the scope (Ring 18).
- Reverse graft: the 128 programs riding back into LuckyDreamer (Ring 5).
