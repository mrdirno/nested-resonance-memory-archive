# Improvisator ∞

An endless generative solo piano in one HTML file. No build step, no dependencies, no network.
Open `improvisator-infinite.html` in a browser and press the centre button.

**Nothing here sounds that a hand did not strike.** There is no echo voice, no delay line, no
pre-delay, no discrete early reflection, and no note inherited across a bar line from the one
before it. If you can hear it, it is in the score, and it is in the MIDI export. That is a
property the harness checks on every run, not a claim in a comment — see **NO REPEAT** below.

Every passage is reproducible from its seed, which is in the URL hash. The same seed and settings
produce the same *performance* — the same notes, at the same moments, with the same touch —
through the transport, through the offline bounce, and into the MIDI file.

---

## What it does

Harmony, phrasing and timbre are computed from four incommensurable constants (φ, √2, e, π), so
the piece comes arbitrarily close to every state and returns to none of them. That is the
"endless" — not randomness, incommensurability.

Forty-two performance rudiments — melodic shapes, hand patterns, bass figures, timing characters
and pedal characters — are selected by context and coordinated by a persistent player state. The
composer reasons at movement → phrase → gesture → hand → finger.

- **Play / pause** — space, or the centre button
- **New passage** — `N`
- **Export MIDI** — `M` (format 1, real tempo map, parts on separate tracks, pedal on every lane)
- **Bounce to WAV** — `B` for a minute, `Shift+B` for four
- **Record what you hear** — `R`
- **Controls** — `C`

## The characters

The eight buttons choose a key, a mode, and a compositional posture: how busy the gait is, how
much lead the right hand carries, how thick the voicings are, how far the key travels, and where
the tune sits. They do **not** change the tempo, how the keys are struck, or the mix — those are
one approved posture (`LOCKED_PERFORMANCE`), and `reference` is that posture by name. Which
settings a character may move is the list `CHARACTER_KEYS`; the engine reads only `warmth`,
`resonance`, `reverb` and `space`, and none of those are in it.

Over 48 bars from one seed the characters run from 272 to 454 notes; Ascent carries twice the
tune of Vigil.

---

## Proof

Two harnesses. Both exit non-zero on failure, so they work in CI.

```sh
node tools/improvisator/analyze.mjs                      # the composer, headless
PLAYWRIGHT_CORE=node_modules/playwright-core \
  node tools/improvisator/browser-check.mjs              # the page, in a real Chromium
node tools/improvisator/audio-report.mjs some.wav        # level, balance, width, dynamics
```

`analyze.mjs` loads the two logic `<script>` blocks into a bare V8 context — the third needs a
DOM and is deliberately not evaluated — and runs the composer for as many bars as you ask.

| Gate | What it means |
|---|---|
| **NO REPEAT** | No event carries the `echo` role, no voice is inherited across a bar line, and no bass answer re-strikes the note already sounding under it. Every sounding note was struck by a hand that decided to strike it — never inherited, and never by a fallback. |
| **HARMONY** | An accompaniment attack is a chord tone, the bass, or an available tension. A short bass approach note leaning into the next root is allowed; anything held is not. Measured across every character, because the bass rudiments that write approach tones do not fire at all settings. |
| **TEXTURE** | Three things a listener notices first: whether the bottom of the piano is muddy, whether the tune is on top, and whether it sounds a minor ninth against a note the hand is holding. All measured at simultaneity — notes actually sounding together, not notes written near each other. |
| **FORM** | A section can end in more than one way, and the chord that resolves has a third in it to resolve with. |
| **RHYTHM** | The melody is written in note values, not floats, and the tempo has somewhere to go — a nominal tempo sitting on its own clamp throws away half the rubato. |
| **DETERMINISM** | One seed, one performance. |
| **RESET** | A composer told to play a seed again plays it again. |
| **ONE PIECE** | A seed played straight and the same seed played from a filled queue are the same music, bar for bar — and filling the queue then dropping it, which is what a character click does, leaves the composer exactly where it was. The page composes ahead of playback in idle time; how far ahead it has got must not change a note. |
| **PRESETS** | Every character survives 96 bars at three seeds. |
| **EDGE SETTINGS** | Both extremes of every continuous control, in twelve keys and eight modes. |
| **PRESET IDENTITY** | Each character has settings of its own, applied the way the page applies them, and the busiest carries at least 1.4× the melody of the sparsest. |
| **VOCABULARY** | Every rudiment is reachable at some character and seed, and no more than two families are selected essentially uniformly — a vocabulary picked at random is a shuffle, not a choice. |

`browser-check.mjs` drives the real page:

| Gate | What it means |
|---|---|
| **ONE RENDERER** | Exactly one function turns a bar into engine calls. The transport and the offline bounce used to carry separate copies, and the copies had drifted. |
| **SAMPLE RATE** | No buffer is declared at a literal rate. The bank renders at the rate fixed on page load and the playback context is created later; 44.1 kHz read as 48 is 1.47 semitones sharp. |
| **CHARACTERS** | Every character button applies, becomes the active one, produces a distinct key and posture, and throws nothing. |
| **PLAYS / BOUNCE** | It plays; the bounce has audio and no clipping. |
| **MIDI** | The export parses back with every note paired, a tempo map, a time signature (the composer writes 3/4 to 5/4), the pedal on every channel that carries notes, no note retriggering a pitch already sounding on its channel, no character lost to ASCII flattening, and no silent lead-in. |
| **LAYOUT** | Every control is reachable and big enough at ten viewport sizes, portrait and landscape, panel open and shut — scrolled into view the way a browser does. |
| **KEYBOARD** | Space activates the focused control and reaches the transport only when nothing is focused; `r` respects a record button hidden by a stylesheet. |
| **LONG BOUNCE** | Four minutes renders in linear time. Scheduling a whole take before `startRendering` never lets a finished voice leave the graph, so the cost grows with the length — 255 s for four minutes that way, against 31 with the render suspended every eight seconds. |
| **REPEATABLE** | Two bounces of one seed differ by less than −60 dB. |
| **NO ERRORS** | No console or page errors across the whole run. |

---

## Where each concern lives

| Concern | Look at |
|---|---|
| The rule against inherited notes | `generateAttempt` (the displaced inner answer), `buildImpulse` |
| Chords and their qualities | `buildSoulChord`, `buildDegreePath`, `QUALITY` naming in `qualityName` |
| Two hands, register, mud | `lowIntervalFloor`, `voicingCandidates`, `voicingCost`, `chooseSoulVoicing`, `chooseSoulBass` |
| The bass line | `chooseSoulBass` and the `BASS_RUDIMENTS` table |
| The tune | `MELODY_RUDIMENTS`, `transformMotif`, `generateSoulMelody`, `chooseMelodyPitch` |
| The left hand | `laySoulHand`, `ACCOMP_RUDIMENTS`, and the lay-out decision in `generateAttempt` |
| Time feel | `hammerTravel`, `TOUCH_COMPENSATION`, `LAY_BACK`, `flexibleBeatDurations`, `warpFlexible` |
| Cadences and the long form | `CADENCES`, `chooseCadence`, `buildDegreePath`, `buildSoulChord` |
| The pedal | `PEDAL_RUDIMENTS`, `makePedalPlan`, `renderBar` |
| Which rudiment fires when | `pickRudiment` |
| What counts as a good section | `validateSection`, `SEARCH_BUDGET` |
| The instrument | `partialTable`, `ZoneRenderer`, `Engine.play`, `Engine.release`, `Engine.attach` |

## Five things worth knowing before you edit

**Nothing may be inherited.** If a note is not in the event stream, it must not be audible. The
composer may decide the hand plays fewer notes — that is a musical decision and it is written
down — but it may never delete a note on the assumption that the pedal is still holding one. That
is what makes the score, the MIDI and the audio the same performance.

**Every timing offset goes in `e.micro`, never in `e.beat`.** `e.beat` is what the bar clock
measures its own length from; putting lay-back, roll offsets or grace notes there makes the bar
longer and the tempo map wrong.

**A penalty in `validateSection` only does something if it can push a candidate below 88.** The
search stops at the first candidate scoring 88 or more, so a penalty smaller than the gap between
a typical score and that threshold is a constant subtracted from everything, and ranks nothing.
The "no gesture" penalty at 6 left 59% of sections with no interval wider than a fourth; at 14,
12%, at a cost of three search attempts instead of one.

**Composition and performance draw from separate random streams,** and the section search draws
from a third derived from the section's own index. Otherwise how good the first candidate happened
to be shifts every note that follows it, and composing ahead of playback changes the music.
Composing ahead must also be reversible: `pump` records the composer's whole position and
`dropQueue` restores it, or a character click skips a section and can move the key.

**The eight character buttons move only the settings in `CHARACTER_KEYS`.** The engine reads
`warmth`, `resonance`, `reverb` and `space` — those four are the mix; `sustain` and `humanize` are
how the hands behave; `bpm` is the tempo. None of them are a character's business, and `reference`
is that posture by name.

---

**Author:** Aldrin Payopay · **License:** GPL-3.0
