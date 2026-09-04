# Improvisator ∞

An endless generative solo piano in one HTML file. No build step, no dependencies, no network.
Open `improvisator-infinite.html` in a browser and press the centre button.

Every passage is reproducible from its seed, which is in the URL hash. The same seed and settings
produce the same *performance* — the same notes, at the same moments, with the same touch — in the
browser, in the offline WAV bounce and in the MIDI export. That is checked, not asserted; see
**Proof** below.

The rendered audio is reproducible to about −83 dB rather than bit-for-bit, and the reason is worth
knowing: the sympathetic-string bank is twelve feedback delay lines, and Chromium does not render a
graph containing a feedback cycle bit-identically twice. Measured, two bounces of one seed differ by
−83 dB rms with a peak difference of −69 dBFS — a few bits of a sixteen-bit word, well under the
noise floor of the format. `browser-check.mjs` measures it on every run and fails if it ever rises above −60 dB, because
that would mean a per-note random value had stopped following the seed.

---

## What it does

Harmony, phrasing and timbre are computed from four incommensurable constants (φ, √2, e, π), so the
piece comes arbitrarily close to every state and returns to none of them. That is the "endless" —
not randomness, incommensurability.

- **Play / pause** — space, or the centre button
- **New passage** — `N`
- **Export MIDI** — `M` (format 1, real tempo map, parts on separate tracks, pedal on every lane)
- **Bounce to WAV** — `B` for a minute, `Shift+B` for four
- **Record what you hear** — `R`
- **Controls** — `C`

## The controls that matter

| Control | What it changes |
|---|---|
| **Pocket** | How far behind the beat the right hand sits. 0 is on top of the beat; 100 is about 30 ms behind a left hand that keeps time. |
| **Colour** | How far the harmony travels outside the key — applied dominants, tritone subs, passing diminished, borrowed chords. |
| **Swing** | How late the off-beat eighths land. Subtle at the default; a real ballad lilt at the top. Never triplet swing. |
| **Range** | Where the tune sits. The default keeps it in the tenor octave and saves the top for one moment a chorus. |
| **Melody / Motion / Texture** | Density of the line, of the rhythm and of the left hand. |
| **Sustain** | How slowly a finger comes off a key. The pedal-lift damper stays physical whatever this is set to. |
| **Resonance** | Depth of the sympathetic strings that ring under the pedal. |
| **Room size / Reverb / Warmth** | The room, and how much of it you hear. |
| **Journey** | How often the key moves. The mode underneath it shifts far more often than the key does. |

## Proof

Three scripts, in this directory. Run them from the repository root.

```bash
# The kernel, headless: statistics, plus four gates that must pass.
node tools/improvisator/analyze.mjs tools/improvisator/improvisator-infinite.html 256 session

# The real page in headless Chromium: script errors, the live transport,
# and a measurement of the audio the offline bounce actually produces.
IMPROV_SEED=grey-rain-0001 node tools/improvisator/browser-check.mjs \
  tools/improvisator/improvisator-infinite.html out.wav

# Level, band balance, stereo width, attack density and dynamic range of a bounce.
node tools/improvisator/audio-report.mjs before.wav after.wav
```

`analyze.mjs` fails loudly on any of:

- **DETERMINISM** — the same seed twice must give an identical event stream.
- **EXPORT PARITY** — a composer driven bar-by-bar (the MIDI export and the offline bounce) must
  produce the same piece as one driven through the realtime queue. Reading `barGlobal` or
  `sectionIndex` during composition breaks this, because those advance with playback.
- **RESET** — a reused composer must play a seed exactly as a fresh one does.
- **HARMONY** — every accompaniment attack must be a chord tone, the bass, an available tension, or
  a deliberate approach note. This is the check that caught a left-hand tenth built from an inverted
  bass, which put a natural eleventh against the third of a dominant.
- **SLASH NAMES** — the printed chord must always name the bass that is played.
- **FORM** — an authentic cadence must land on the tonic. A held turnaround spanning the last two
  blueprint slots used to take the first of them and end on the dominant instead.
- **PRESETS / EDGE SETTINGS** — every preset over 96 bars × 3 seeds, and both extremes of every
  slider across 12 keys and 8 modes, must produce only valid events.

It also reports, without failing on them: **GESTURE** (how many sections contain no interval wider
than a fifth, and how many are jumpy), **SEAMS** (how many section boundaries carry a pickup, and
the distribution of closure types), and **RAILS** (how often the velocity clamps bind, which is how
you find out that the clamp rather than the phrase shape is deciding what the top of a line sounds
like).

`browser-check.mjs` additionally parses the exported MIDI back from the bytes the button writes —
every note-on paired, the tempo map present, CC64 on all three lanes — and bounces the same seed
twice to confirm the two renders differ only at the level Web Audio itself is reproducible to.

It also reports the section search: quality distribution and how many of the eight candidate
sections it took. A median near 95 at three attempts means the gate is doing work without fighting
the generator; a median pinned at the floor with eight attempts every time means a rule is
miscalibrated, not that the music is bad.

## Where the musical decisions live

Everything is in the first `<script>` — a pure-JS kernel with no DOM and no Web Audio, exported as
`window.IMPROV`. The second `<script>` only makes it audible and visible.

| Concern | Look at |
|---|---|
| Chord identity, tensions, avoid notes | `QUALITY`, `makeChord`, `tensionOK`, `diatonicTensions` |
| Chromatic harmony | `chromaticize`, `cadenceChord`, `dominantColour` |
| Harmonic rhythm | `RHYTHM_PLANS`, `TURNAROUNDS`, `planChanges` |
| Long form | `formPosition`, `chooseBlueprint`, `maybeShade`, `maybeJourney`, `ARC_POOLS` |
| Two hands, register | `REG`, `minInterval`, `bassClearance`, `shapePool`, `chooseVoicing` |
| The bass line | `planBassLine` |
| The tune | `MOTIF_CELLS`, `developCell`, `planRests`, `APEX_PLAN`, `chooseMelodyPitch` |
| The left hand | `layHand`, `layAlone`, `voiceWeight`, `rollOffsets` |
| Time feel | `hammerDelay`, `handLead`, `layback`, `swingRatio`, `beatDurations`, `warpBeat` |
| The pedal | `pedalGesture`, and `scheduleBar` in the instrument layer |
| The instrument | `partialTable`, `ZoneRenderer`, `Engine.play`, `Engine.release`, `Engine.attach` |

## Three things worth knowing before you edit

**Every timing offset goes in `e.micro`, never in `e.beat`.** `e.beat` is what the bar clock measures
its own length from; putting lay-back, roll offsets or grace notes there makes the bar longer and the
tempo map wrong. `e.micro` is read identically by the realtime scheduler, the offline bounce and the
MIDI log, which is what keeps the three renderings the same performance.

**An offline render must stay a chunk ahead of itself.** `bounceWav` suspends the
`OfflineAudioContext` every eight seconds so finished voices can disconnect — without that the graph
only grows and the render is quadratic in the length of the take. But `Engine.play` clamps any note
scheduled behind `ctx.currentTime` to now + 2 ms, and once the render clock is running that clamp can
fire. Scheduling is therefore kept sixteen seconds ahead of the suspend point, not eight. Scheduling
only to the next suspend point moved one note by 33 ms and changed the take by 24 dB at the peak.

**On `lowpass` and `highpass` nodes, Web Audio reads `Q` in decibels.** Not as a quality factor.
`Q = 0.5` is half a decibel of resonance at the corner, so a filter that looks heavily damped is
actually boosting. A comb filter built with two such filters inside its feedback loop has a loop gain
above one and runs to full scale in about six seconds. Measure with `getFrequencyResponse` before
trusting any filter in this file.

---

**Author:** Aldrin Payopay · **License:** GPL-3.0
