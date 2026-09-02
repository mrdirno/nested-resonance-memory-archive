# SoundHack × NRM Bridge

**Modules:** `nrm_core/soundhack_spectral.py`, `nrm_core/soundhack_bridge.py`
**Tests:** `tests/test_soundhack_spectral.py`, `tests/test_soundhack_bridge.py` (51 tests)
**Companion archive:** [soundhack-x-NRM-Archive-](https://github.com/mrdirno/soundhack-x-NRM-Archive-)
(Tom Erbe's SoundHack C source, MIT; the crossover map lives there as
`python/CROSSOVER_MAP.md`)

## Why this exists

The Universal Adapter doctrine says the control layer must never know
where its entropy comes from, and Gate 2.6 (Multi-Modal Anchor
Validation) asks for NRM dynamics driven by a substrate other than CPU
metrics. SoundHack — a 1990s spectral processor built entirely out of
phase-oscillator banks — supplies both the substrate and, unexpectedly, a
composition operator NRM was missing.

## The four couplings

### 1. Audio as a reality anchor (toward Gate 2.6)

`TranscendentalBridge.reality_to_phase` reads exactly three keys:
`cpu_percent`, `memory_percent`, `disk_percent`, each in [0, 100]. That
dict is the *entire* adapter contract. `AudioRealityAdapter` derives it
from measurable spectral properties of a real signal:

| Bridge key | Audio measurement | Reading |
|---|---|---|
| `cpu_percent` | spectral flux (positive magnitude change / total magnitude) | activity |
| `memory_percent` | RMS level on a 60 dB window below full scale | occupancy |
| `disk_percent` | spectral centroid / Nyquist | where the mass sits |

The raw measurements (`spectral_flux`, `rms_db`, `centroid_hz`) ride
along in the dict and survive the phase round trip verbatim in
`TranscendentalState.reality_anchor` — the Reality Imperative holds on
the new substrate. `test_adapter_feeds_legacy_transcendental_bridge`
drives the *legacy* `src/bridge/transcendental_bridge.py` with audio
metrics, unmodified.

```python
from nrm_core.soundhack_bridge import AudioRealityAdapter
adapter = AudioRealityAdapter(signal, sample_rate=44100)
for metrics in adapter.frames():
    state = bridge.reality_to_phase(metrics)   # zero bridge changes
```

`AudioEntropy` additionally implements `SystemEntropy`'s two-method
contract (`get_float() -> [0,1)`, `get_choice(list)`) by SHA-256-hashing
signal frames with a call counter. Unlike the psutil+urandom stream it
can replace, it is **reproducible**: the same recording replays the same
experiment bit-for-bit.

### 2. Polansky mutation as a composition operator

SoundHack's Spectral Mutation (Larry Polansky's morphological mutation
functions) combines the frame-to-frame *deltas* of two evolving states
with one of five kernels, under a mutation index Ω ∈ [0, 1]. NRM's
`CompositionEngine` merges agents with an arithmetic phase mean — an
operator with no interior structure. The bridge lifts the mutation
recurrence out of the spectral frame and applies it along time:

```python
from nrm_core.soundhack_bridge import compose_trajectories
composed, omegas = compose_trajectories(traj_a, traj_b, mutation_type=LCM)
```

Ω is supplied per step by NRM's own resonance, `|cos(φ_a − φ_b)|` — the
exact quantity `FractalAgent.calculate_resonance` caches — and steps
below the CompositionEngine threshold (0.7) do not mutate, mirroring
`can_compose`. Fully resonant agents fuse; orthogonal agents stay
distinct. The kernels are Polansky's, verbatim (see the fidelity tests).

### 3. Swarm sonification through AddSynth

`FractalSwarm` *is* an oscillator bank: Kuramoto phase oscillators
carrying energy. `SwarmSonifier` renders a run through a faithful port of
SoundHack's `AddSynth` (8192-entry 0.5·cos table, truncating lookup,
per-frame linear amp/freq interpolation): one agent per partial,
amplitude ← energy, frequency ← phase velocity, one NRM tick per
synthesis frame.

```python
from nrm_core.soundhack_bridge import SwarmSonifier, write_wav
son = SwarmSonifier(num_agents=4)
signal = son.render_run(energy_series, velocity_series)  # (ticks, agents)
write_wav("swarm.wav", signal)
```

The output is a measurable artifact, not decoration:
`test_sonifier_wav_round_trip_recovers_dynamics` renders a run with two
energy epochs to a real WAV, reads it back, re-analyzes it with
`AudioRealityAdapter`, and recovers the epochs from the audio alone —
swarm → audio → reality metrics, the loop closed.

### 4. The spectral core itself

`nrm_core/soundhack_spectral.py` is the full port: seven windows
(including the nonstandard 0.50/0.40 von Hann), the fold-and-rotate STFT
engine, phase-vocoder time-stretch, the complete mutation engine
(7 types, stochastic third-octave band selection, delta emphasis,
absolute mode), and the AddSynth bank. It is self-contained (numpy +
stdlib) and mirrored byte-identically in the SoundHack archive as
`python/soundhack_spectral.py`, where a CLI (`python/mutate_cli.py
--selftest`) renders every mutation type to audio with zero assets.

## Verification

- 51 tests in the maintained suite (run them with
  `pytest tests/test_soundhack_spectral.py tests/test_soundhack_bridge.py`,
  or run everything with `pytest tests/`; the two Helios test files skip
  themselves when the libraries they need, such as OpenCV and Flask, are
  not installed), pinning window coefficients, kernel math, round-trip
  identity, the one-hop `ShiftOut` pre-roll and the `ShiftIn` validSamples
  countdown, contract ranges, determinism under seeds, and the two
  integration loops above.
- Differential tests against the original C, compiled with gcc from the
  SoundHack archive: `RealFFT` matches `conj(np.fft.rfft())` in the
  packed layout at float32 precision (~1.6e-7 relative) with round-trip
  identity (~4.8e-7); all seven windows match (~4e-7); `FindBestRatio`
  matches on 78 (window, scale) cases including its mismatched-pair and
  fallback exits; `PhaseInterpolate` with phase locking matches over
  multi-frame random input (~7e-6 rad).

## Provenance

Original C: SoundHack, © Tom Erbe (MIT License). Mutation algorithms:
Larry Polansky — morphological mutation functions (Polansky & McKinney,
Proc. ICMC 1991); L. Polansky & T. Erbe, "Spectral Mutation in
SoundHack," Computer Music Journal 20(1): 92–101, 1996. Port and
bridge: Aldrin Payopay. The port file is MIT (matching its source
material); the bridge module is GPL-3.0 with the rest of this repository.

<!-- ═══ RINGS · agent context, newest last · read before changing this file ═══
RING 1 · 2026-08-31 · cross-pollination session 1
WHAT CHANGED: first bridge between this repo and soundhack-x-NRM-Archive-.
Port (soundhack_spectral) + adapters (soundhack_bridge) + 51 tests + this
doc; mirror + CLI + CROSSOVER_MAP.md + README on the SoundHack side.
BANNED: doc-only cross-links; generic modernization port; generic
sonification; ctypes bindings; audio-as-RNG-seed.
DEAD BRANCHES: shared pip package (premature per Library Release
Doctrine); porting Convolve first (metaphor, not isomorphism); wiring
into legacy src/fractal CompositionEngine (unused by the swarm loop;
nrm_core is the tested surface).
KILL-TEST: "the port agrees with notes, not with the C" — killed by
compiling the archive's actual FFT.c/Windows.c/FindBestRatio/
PhaseInterpolate and matching at float32 precision; a 4-lens adversarial
review then found and fixed 5 real fidelity divergences (ShiftIn same-
block countdown, FindBestRatio loop exits, locking's in-place neighbor
read, AddSynth hard cut, table-B parity). Residual: Mutate.c's frame
loop verified behaviorally (omega extremes reproduce source/target
through the full chain), not compiled.
THE NON-OBVIOUS CHOICE: Polansky mutation as NRM's missing composition
operator (omega = resonance), not NRM as a modulation source for effects.
OPEN QUESTIONS: drive FractalSwarm coupling_strength from audio flux and
compare composition cascades vs CPU-driven runs (full Gate 2.6)? port
Extract's frequency-deviation statistic as the swarm burst detector? map
deltaEmphasis to NRM energy decay so both share one constant?
═══ end rings ═══ -->
