"""
SoundHack Spectral Core (Python port)
=====================================

A faithful NumPy port of the spectral-processing engine of SoundHack,
Tom Erbe's classic Macintosh sound-processing program (1991-):

- Window generators           (Math/Windows.c   -- incl. the nonstandard
                               0.50/0.40 "von Hann" coefficients)
- Window normalization        (Math/PhaseVocoderRoutines.c ScaleWindows)
- Fold-and-rotate STFT engine (WindowFold / OverlapAdd / ShiftIn / ShiftOut)
- Phase-vocoder time-stretch  (Processing/PhaseVocoder.c PhaseInterpolate)
- Spectral Mutation           (Processing/Mutate.c -- Larry Polansky's
                               morphological mutation functions: USIM, ISIM,
                               IUIM, UUIM, LCM, LCMIUIM, LCMUUIM)

FFT convention note: SoundHack's RealFFT (Math/FFT.c) uses an e^{+i} forward
kernel, producing the CONJUGATE of numpy's rfft in a packed layout
[Re0, ReNyq, Re1, Im1, ...]; its CartToPolar then negates atan2. The two
sign flips cancel, so in this port:

    amp   == np.abs(np.fft.rfft(frame))
    phase == np.angle(np.fft.rfft(frame))

and the inverse chain (PolarToCart + RealFFT FREQ2TIME, which embeds a 2/N
scale) equals np.fft.irfft(amp * np.exp(1j * phase), n=points) exactly.
numpy's rfft/irfft therefore replace Math/FFT.c wholesale with no scaling
corrections; every other numeric detail below reproduces the C.

This file is deliberately self-contained (numpy + stdlib only) and is
mirrored byte-identically in two repositories:

- https://github.com/mrdirno/soundhack-x-NRM-Archive-   (python/)
- https://github.com/mrdirno/nested-resonance-memory-archive (nrm_core/)

Original C source: SoundHack, Copyright (c) Tom Erbe (MIT License,
https://github.com/tomerbe -- archived at soundhack-x-NRM-Archive-).
Mutation algorithms: Larry Polansky, "Morphological Metrics" /
mutation functions (Leonardo Music Journal, CMJ 16(4) 1992).

This port: MIT License (matching the source material).
Port author: Aldrin Payopay <aldrin.gdf@gmail.com>
"""

import math
import random as _random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

TWO_PI = 2.0 * math.pi

# Window types -- enum values from ToolBox/SoundHack.h
HAMMING = 1
KAISER = 2
RAMP = 3
RECTANGLE = 4
SINC = 5
TRIANGLE = 6
VONHANN = 7

# Mutation types -- #defines from Processing/Mutate.h
USIM = 1      # uniform signed interval mutation
ISIM = 2      # irregular signed interval mutation
IUIM = 3      # irregular unsigned interval mutation
UUIM = 4      # uniform unsigned interval mutation
LCM = 5       # linear contour mutation
LCMIUIM = 6   # LCM then IUIM (second stage gated by table B)
LCMUUIM = 7   # LCM then UUIM (second stage unconditional)

MUTATION_NAMES = {
    USIM: "USIM", ISIM: "ISIM", IUIM: "IUIM", UUIM: "UUIM",
    LCM: "LCM", LCMIUIM: "LCIUIM", LCMUUIM: "LCUUIM",
}


# ---------------------------------------------------------------------------
# Windows (Math/Windows.c)
# ---------------------------------------------------------------------------

def _ino(x: float) -> float:
    """Modified Bessel I0 series, exactly as in Math/Windows.c ino()."""
    y = x / 2.0
    t = 1.0e-08
    e = 1.0
    de = 1.0
    for i in range(1, 26):
        de = de * y / i
        sde = de * de
        e += sde
        if e * t > sde:
            break
    return e


def get_window(size: int, window_type: int) -> np.ndarray:
    """GetWindow(): one of SoundHack's 7 window shapes, length `size`.

    Quirks preserved from the C source:
    - VONHANN uses coefficients 0.50/0.40 (endpoints 0.1), not the
      textbook 0.5/0.5.
    - KAISER is fixed at beta = 6.8 with endpoints forced to zero.
    - RAMP divides by size (not size-1), descending from 1.0.
    """
    i = np.arange(size, dtype=float)
    if window_type == HAMMING:
        return 0.54 - 0.46 * np.cos(TWO_PI * i / (size - 1))
    if window_type == VONHANN:
        return 0.50 - 0.40 * np.cos(TWO_PI * i / (size - 1))
    if window_type == RECTANGLE:
        return np.ones(size)
    if window_type == RAMP:
        return 1.0 - i / size
    if window_type == SINC:
        half = size / 2.0
        w = np.empty(size)
        for n in range(size):
            if float(n) == half:
                w[n] = 1.0
            else:
                w[n] = (size * math.sin(math.pi * (n - half) / half)
                        / (2.0 * math.pi * (n - half)))
        return w
    if window_type == TRIANGLE:
        w = np.empty(size)
        up = True
        tmp = 0.0
        for n in range(size):
            w[n] = 2.0 * tmp
            if up:
                tmp += 1.0 / size
                if tmp > 0.5:
                    tmp = 1.0 - tmp
                    up = False
            else:
                tmp -= 1.0 / size
        return w
    if window_type == KAISER:
        half = size // 2
        bes = _ino(6.8)
        xind = float(size - 1) * float(size - 1)
        w = np.zeros(size)
        for n in range(half):
            r = math.sqrt(1.0 - 4.0 * n * n / xind)
            v = _ino(6.8 * r) / bes
            w[half + n] = v
            w[half - n] = v
        w[0] = 0.0
        w[size - 1] = 0.0
        return w
    raise ValueError(f"unknown window type {window_type}")


def scale_windows(analysis_window: np.ndarray,
                  synthesis_window: np.ndarray,
                  points: int,
                  interpolation: int) -> Tuple[np.ndarray, np.ndarray]:
    """ScaleWindows(): normalize windows for unity analysis/OLA gain.

    Reproduces Math/PhaseVocoderRoutines.c (the phase-vocoder path;
    the dormant CSOUND_ANALYSIS branch is intentionally omitted):
    - if window_size > points, both windows get a sinc taper;
    - analysis factor = 2 / sum(analysis_window);
    - if window_size <= points, the synthesis window is additionally
      normalized by the hop-lattice sum of its squares (COLA).
    """
    analysis_window = np.array(analysis_window, dtype=float)
    synthesis_window = np.array(synthesis_window, dtype=float)
    window_size = len(analysis_window)

    if window_size > points:
        half = -((window_size - 1.0) / 2.0)
        for n in range(window_size):
            h = half + n
            if h != 0.0:
                analysis_window[n] *= (points * math.sin(math.pi * h / points)
                                       / (math.pi * h))
                if interpolation != 0:
                    synthesis_window[n] *= (
                        interpolation * math.sin(math.pi * h / interpolation)
                        / (math.pi * h))

    anal_factor = 2.0 / analysis_window.sum()
    synth_factor = (1.0 / anal_factor) if window_size > points else anal_factor
    analysis_window *= anal_factor
    synthesis_window *= synth_factor

    if window_size <= points:
        lattice = synthesis_window[0:window_size:interpolation]
        synthesis_window *= 1.0 / np.sum(lattice * lattice)

    return analysis_window, synthesis_window


# ---------------------------------------------------------------------------
# STFT engine (WindowFold / OverlapAdd, fold-and-rotate convention)
# ---------------------------------------------------------------------------

def wrap_pm_pi(x: np.ndarray) -> np.ndarray:
    """C-faithful phase wrap: while (x > pi) x -= 2pi; while (x < -pi) x += 2pi.

    Keeps values already in [-pi, pi] untouched (both endpoints included),
    matching the strict inequalities of the original while-loops.
    """
    x = np.array(x, dtype=float)
    while np.any(x > math.pi):
        x = np.where(x > math.pi, x - TWO_PI, x)
    while np.any(x < -math.pi):
        x = np.where(x < -math.pi, x + TWO_PI, x)
    return x


def window_fold(input_buf: np.ndarray, window: np.ndarray,
                points: int, current_time: int) -> np.ndarray:
    """WindowFold(): window, fold to FFT size, rotate by the sample clock.

    The rotation by (current_time mod points) references all phases to
    absolute input time zero, which is what lets the phase vocoder measure
    only the deviation from bin center.
    """
    window_size = len(input_buf)
    frame = np.zeros(points)
    ct = current_time % points  # Python % is already non-negative
    idx = (ct + np.arange(window_size)) % points
    np.add.at(frame, idx, input_buf * window)
    return frame


def overlap_add(frame: np.ndarray, window: np.ndarray,
                output_buf: np.ndarray, current_time: int) -> None:
    """OverlapAdd(): unrotate, window, accumulate into the output buffer."""
    window_size = len(output_buf)
    points = len(frame)
    ct = current_time % points
    idx = (ct + np.arange(window_size)) % points
    output_buf += frame[idx] * window


def analyze_frame(frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """RealFFT(TIME2FREQ) + CartToPolar for one folded frame.

    Returns (amp, phase), each of length points//2 + 1.
    Zero-amplitude bins get phase 0 (as in CartToPolar).
    """
    spectrum = np.fft.rfft(frame)
    amp = np.abs(spectrum)
    phase = np.where(amp == 0.0, 0.0, np.angle(spectrum))
    return amp, phase


def synthesize_frame(amp: np.ndarray, phase: np.ndarray,
                     points: int) -> np.ndarray:
    """PolarToCart + RealFFT(FREQ2TIME): polar half-spectrum -> time frame."""
    return np.fft.irfft(amp * np.exp(1j * phase), n=points)


def simple_spectral_gate(amp: np.ndarray, mask_ratio: float = 0.0,
                         min_amplitude: float = 0.0) -> np.ndarray:
    """SimpleSpectralGate(): zero bins under the relative/absolute floors."""
    if mask_ratio == 0.0 and min_amplitude == 0.0:
        return amp
    mask_amplitude = mask_ratio * amp.max() if len(amp) else 0.0
    out = np.array(amp)
    out[out < mask_amplitude] = 0.0
    out[out < min_amplitude] = 0.0
    return out


class _SlidingInput:
    """ShiftIn(): windowSize sliding buffer over a signal, hop = decimation.

    Zero-pads past EOF and counts validSamples down exactly as the C static
    does; `exhausted` mirrors the -2 return (the driver still processes the
    block on which it fires, then stops).
    """

    def __init__(self, signal: np.ndarray, window_size: int, decimation: int):
        self.signal = np.asarray(signal, dtype=float)
        self.window_size = window_size
        self.decimation = decimation
        self.buf = np.zeros(window_size)
        self.pos = 0
        self.valid = window_size
        self._eof = False

    def shift_in(self) -> bool:
        """Advance one hop; returns True while the stream is still valid."""
        d = self.decimation
        self.buf[:-d] = self.buf[d:]
        chunk = self.signal[self.pos:self.pos + d]
        self.pos += d
        n = len(chunk)
        tail = self.buf[self.window_size - d:]
        tail[:n] = chunk
        tail[n:] = 0.0
        if not self._eof:
            if n < d:
                self._eof = True
                self.valid = self.window_size - d + n
        else:
            self.valid -= d
        return self.valid > 0


def stft_analyze(signal: np.ndarray, points: int = 1024,
                 window_size: Optional[int] = None,
                 decimation: Optional[int] = None,
                 window_type: int = HAMMING
                 ) -> Tuple[np.ndarray, np.ndarray, dict]:
    """Full SoundHack analysis pass: signal -> (amps, phases) frame stacks.

    Defaults mirror the Mutate/pitch path: window_size = points,
    decimation = points // 8 (87.5% overlap). Returns (amps, phases, info)
    where amps/phases have shape (num_frames, points//2 + 1) and info holds
    the windows and pointers needed for an exact resynthesis.
    """
    if window_size is None:
        window_size = points
    if decimation is None:
        decimation = points // 8
    raw = get_window(window_size, window_type)
    anal_win, synth_win = scale_windows(raw, raw.copy(), points, decimation)

    stream = _SlidingInput(signal, window_size, decimation)
    in_pointer = -window_size
    amps: List[np.ndarray] = []
    phases: List[np.ndarray] = []
    while True:
        in_pointer += decimation
        alive = stream.shift_in()
        frame = window_fold(stream.buf, anal_win, points, in_pointer)
        amp, phase = analyze_frame(frame)
        amps.append(amp)
        phases.append(phase)
        if not alive:
            break
    info = {
        "points": points, "window_size": window_size,
        "decimation": decimation, "window_type": window_type,
        "analysis_window": anal_win, "synthesis_window": synth_win,
        "first_in_pointer": -window_size + decimation,
    }
    return np.array(amps), np.array(phases), info


def stft_resynthesize(amps: np.ndarray, phases: np.ndarray,
                      info: dict, interpolation: Optional[int] = None
                      ) -> np.ndarray:
    """Full SoundHack resynthesis pass: frame stacks -> signal.

    Mirrors the PvocBlock output chain: inverse FFT, rotated overlap-add,
    ShiftOut gating (no samples emitted until the priming ramp has passed).
    Faithful quirk: the C fires its first write at gOutPointer ==
    -interpolation, so the emitted stream begins exactly one hop BEFORE
    input time zero; drop the first `interpolation` samples to align
    output with input.
    """
    points = info["points"]
    window_size = info["window_size"]
    decimation = info["decimation"]
    if interpolation is None:
        interpolation = decimation
    synth_win = info["synthesis_window"]

    in_pointer = -window_size
    # C: gOutPointer = (gInPointer * interpolation) / decimation, truncating.
    out_pointer = int(in_pointer * interpolation / decimation)
    out_buf = np.zeros(window_size)
    emitted: List[np.ndarray] = []
    for amp, phase in zip(amps, phases):
        in_pointer += decimation
        out_pointer += interpolation
        frame = synthesize_frame(amp, phase, points)
        overlap_add(frame, synth_win, out_buf, out_pointer)
        if out_pointer + interpolation >= 0:
            emitted.append(out_buf[:interpolation].copy())
        out_buf[:-interpolation] = out_buf[interpolation:]
        out_buf[-interpolation:] = 0.0
    return np.concatenate(emitted) if emitted else np.zeros(0)


# ---------------------------------------------------------------------------
# Phase vocoder time-stretch (Processing/PhaseVocoder.c)
# ---------------------------------------------------------------------------

def find_best_ratio(scale_factor: float, window_size: int
                    ) -> Tuple[int, int, float]:
    """FindBestRatio(): integer hop pair within 0.4% of scale_factor.

    Returns (decimation, interpolation, achieved_ratio); both hops capped
    at window_size // 8.
    """
    max_hop = window_size // 8
    decimation = interpolation = max_hop
    if scale_factor > 1.0:
        interpolation = max_hop
        while interpolation > 1:
            decimation = int(interpolation / scale_factor)
            if decimation == 0:
                interpolation -= 1
                continue
            test = float(interpolation) / decimation
            err = max(test, scale_factor) / min(test, scale_factor)
            if err < 1.004:
                break
            interpolation -= 1
        if interpolation <= 1:
            interpolation = max_hop
            decimation = int(max_hop / scale_factor)
    elif scale_factor < 1.0:
        decimation = max_hop
        while decimation > 1:
            interpolation = int(decimation * scale_factor)
            if interpolation == 0:
                decimation -= 1
                continue
            test = float(interpolation) / decimation
            err = max(test, scale_factor) / min(test, scale_factor)
            if err < 1.004:
                break
            decimation -= 1
        if decimation <= 1:
            decimation = max_hop
            interpolation = int(max_hop * scale_factor)
    return decimation, interpolation, float(interpolation) / decimation


class PhaseInterpolator:
    """PhaseInterpolate(): per-band phase rescaling for time-stretching.

    Faithful to Processing/PhaseVocoder.c including its quirks:
    - the input phase-difference unwrap is COMMENTED OUT in this source
      version, so none is applied here;
    - zero-amplitude bins hold the last output phase and do not update
      the input-phase memory;
    - phase locking (off by default) checks the low neighbor only for
      b > 1 and does not update max amplitude for the high neighbor.
    """

    def __init__(self, half_points: int, scale_factor: float,
                 decimation: int, points: int, phase_locking: bool = False):
        self.last_phase_in = np.zeros(half_points + 1)
        self.last_phase_out = np.zeros(half_points + 1)
        self.scale_factor = scale_factor
        self.phase_per_band = decimation * TWO_PI / points
        self.phase_locking = phase_locking

    def process(self, amp: np.ndarray, phase: np.ndarray) -> np.ndarray:
        n = len(amp)
        new_phase = np.empty(n)
        for b in range(n):
            if amp[b] == 0.0:
                new_phase[b] = self.last_phase_out[b]
                continue
            if self.phase_locking:
                max_amplitude = 0.0
                pd = 0.0
                if b > 1:
                    max_amplitude = amp[b - 1]
                    pd = ((phase[b - 1] - self.last_phase_in[b - 1])
                          - self.phase_per_band)
                if amp[b] > max_amplitude:
                    max_amplitude = amp[b]
                    pd = phase[b] - self.last_phase_in[b]
                if b != n - 1 and amp[b + 1] > max_amplitude:
                    pd = ((phase[b + 1] - self.last_phase_in[b + 1])
                          + self.phase_per_band)
            else:
                pd = phase[b] - self.last_phase_in[b]
            self.last_phase_in[b] = phase[b]
            pd *= self.scale_factor
            out = self.last_phase_out[b] + pd
            while out > math.pi:
                out -= TWO_PI
            while out < -math.pi:
                out += TWO_PI
            new_phase[b] = out
            self.last_phase_out[b] = out
        return new_phase


def phase_vocoder(signal: np.ndarray, scale_factor: float,
                  points: int = 1024, window_size: Optional[int] = None,
                  window_type: int = HAMMING,
                  phase_locking: bool = False) -> np.ndarray:
    """Time-stretch a mono signal by scale_factor (output/input duration).

    The complete PvocBlock time-mode chain: ShiftIn -> WindowFold -> FFT ->
    CartToPolar -> PhaseInterpolate -> PolarToCart -> IFFT -> OverlapAdd ->
    ShiftOut, with FindBestRatio picking the integer hop pair. The output
    begins one hop before input time zero (see stft_resynthesize).
    """
    if window_size is None:
        window_size = points
    decimation, interpolation, achieved = find_best_ratio(
        scale_factor, window_size)
    raw = get_window(window_size, window_type)
    anal_win, synth_win = scale_windows(raw, raw.copy(), points, interpolation)

    stream = _SlidingInput(signal, window_size, decimation)
    interp = PhaseInterpolator(points // 2, achieved, decimation, points,
                               phase_locking)
    in_pointer = -window_size
    out_pointer = int(in_pointer * interpolation / decimation)
    out_buf = np.zeros(window_size)
    emitted: List[np.ndarray] = []
    while True:
        in_pointer += decimation
        out_pointer += interpolation
        alive = stream.shift_in()
        frame = window_fold(stream.buf, anal_win, points, in_pointer)
        amp, phase = analyze_frame(frame)
        new_phase = interp.process(amp, phase)
        out_frame = synthesize_frame(amp, new_phase, points)
        overlap_add(out_frame, synth_win, out_buf, out_pointer)
        if out_pointer + interpolation >= 0:
            emitted.append(out_buf[:interpolation].copy())
        out_buf[:-interpolation] = out_buf[interpolation:]
        out_buf[-interpolation:] = 0.0
        if not alive:
            break
    return np.concatenate(emitted) if emitted else np.zeros(0)


# ---------------------------------------------------------------------------
# Spectral Mutation (Processing/Mutate.c -- Polansky mutation functions)
# ---------------------------------------------------------------------------

def usim_mutate(source_delta, target_delta, omega):
    """Uniform signed interval mutation: lerp between the deltas."""
    return source_delta + omega * (target_delta - source_delta)


def isim_mutate(target_delta):
    """Irregular signed interval mutation: target delta replaces source."""
    return target_delta


def iuim_mutate(source_delta, target_delta):
    """Irregular unsigned: |target delta| carrying the source delta's sign."""
    return np.where(np.asarray(source_delta) < 0.0,
                    -np.abs(target_delta), np.abs(target_delta))


def uuim_mutate(source_delta, target_delta, omega):
    """Uniform unsigned: |lerp of deltas| carrying the source delta's sign."""
    v = np.asarray(source_delta) + omega * (
        np.asarray(target_delta) - np.asarray(source_delta))
    return np.where(np.asarray(source_delta) < 0.0, -np.abs(v), np.abs(v))


def lcm_mutate(source_delta, target_delta):
    """Linear contour mutation: |source delta| with the target delta's sign."""
    return np.where(np.asarray(target_delta) < 0.0,
                    -np.abs(source_delta), np.abs(source_delta))


def pick_mutate_table(omega: float, persist: float, bands: int,
                      small_decision: np.ndarray,
                      rng: _random.Random) -> np.ndarray:
    """PickMutateTable(): stochastic third-octave band selection.

    `small_decision` (bool array of 3*floor(log2(bands)) slots) persists
    across frames and is mutated in place; the returned array has bands+1
    per-bin booleans. Faithful to the C including:
    - ON slots survive phase A with probability `persist`;
    - target count = floor(omega * num_steps);
    - the toggle index floor(u * (num_steps-1)) practically never reaches
      the top slot (the C could spin waiting for rand()==RAND_MAX; this
      port breaks the stall deterministically after a bounded number of
      draws, the one deliberate deviation).
    """
    num_steps = len(small_decision)

    for step in range(num_steps):
        if persist < rng.random() and small_decision[step]:
            small_decision[step] = False

    count = int(omega * num_steps)
    old_count = int(np.count_nonzero(small_decision))
    max_draws = 1000 * max(num_steps, 1)
    draws = 0
    if old_count < count:
        n = old_count
        while n < count and draws < max_draws:
            step = int(rng.random() * (num_steps - 1))
            draws += 1
            if not small_decision[step]:
                small_decision[step] = True
                n += 1
        # bounded stall-break: fill lowest-index OFF slots deterministically
        for step in range(num_steps):
            if n >= count:
                break
            if not small_decision[step]:
                small_decision[step] = True
                n += 1
    elif old_count > count:
        n = old_count
        while n > count and draws < max_draws:
            step = int(rng.random() * (num_steps - 1))
            draws += 1
            if small_decision[step]:
                small_decision[step] = False
                n -= 1
        for step in range(num_steps):
            if n <= count:
                break
            if small_decision[step]:
                small_decision[step] = False
                n -= 1

    decision = np.zeros(bands + 1, dtype=bool)
    next_octave = -0.3333333333333
    next_division = int(2.0 ** next_octave * bands)
    step = num_steps - 1
    for band in range(bands, -1, -1):
        if band <= next_division:
            step -= 1
            next_octave -= 0.3333333333333
            next_division = int(2.0 ** next_octave * bands)
        decision[band] = small_decision[max(step, 0)]
    return decision


@dataclass
class MutationSpec:
    """MutateInfo: parameters of one spectral mutation (defaults per dialog).

    omega            mutation index in [0,1]; interpolation weight for the
                     uniform types, fraction of third-octave slots mutated
                     for the irregular types. May also be an array of
                     per-frame values (the drawn-function mode).
    band_persistence P(selected band stays selected next frame), irregular
                     types only.
    delta_emphasis   [-1,1], amplitude only: >= 0 attenuates the delta,
                     < 0 attenuates the accumulated mutant.
    absolute         measure amplitude deltas against fixed references
                     (source_reference/target_reference) instead of the
                     previous frame, and rebuild the mutant amplitude base
                     from their omega-crossfade each frame.
    """
    mutation_type: int = USIM
    omega: object = 0.5
    band_persistence: float = 1.0
    delta_emphasis: float = 0.0
    absolute: bool = False
    source_reference: float = 0.0
    target_reference: float = 0.0
    seed: Optional[int] = None


class MutationEngine:
    """MutateSpectrum(): frame-by-frame morphological spectral mutation.

    Holds the previous source/target frames and the mutant accumulator
    (which is simultaneously the previous-mutant memory and the output
    frame, exactly as mutantjSpectrum is in the C). Mono chain.
    """

    def __init__(self, half_points: int, spec: MutationSpec):
        self.half_points = half_points
        self.spec = spec
        self.rng = _random.Random(spec.seed)
        n = half_points + 1
        self.source_prev_amp = np.zeros(n)
        self.source_prev_phase = np.zeros(n)
        self.target_prev_amp = np.zeros(n)
        self.target_prev_phase = np.zeros(n)
        self.mutant_amp = np.zeros(n)
        self.mutant_phase = np.zeros(n)
        num_steps = int(math.log2(half_points)) * 3 if half_points > 1 else 3
        self.small_decision_a = np.zeros(num_steps, dtype=bool)
        self.small_decision_b = np.zeros(num_steps, dtype=bool)

    def _mutate_deltas(self, s_amp_d, t_amp_d, s_ph_d, t_ph_d, omega):
        """The type switch of MutateSpectrum, on full delta vectors."""
        spec = self.spec
        mt = spec.mutation_type
        if mt in (ISIM, IUIM, LCM, LCMIUIM, LCMUUIM):
            dec_a = pick_mutate_table(omega, spec.band_persistence,
                                      self.half_points,
                                      self.small_decision_a, self.rng)
        if mt == LCMIUIM:
            dec_b = pick_mutate_table(omega, spec.band_persistence,
                                      self.half_points,
                                      self.small_decision_b, self.rng)

        if mt == USIM:
            return (usim_mutate(s_amp_d, t_amp_d, omega),
                    usim_mutate(s_ph_d, t_ph_d, omega))
        if mt == UUIM:
            return (uuim_mutate(s_amp_d, t_amp_d, omega),
                    uuim_mutate(s_ph_d, t_ph_d, omega))
        if mt == ISIM:
            return (np.where(dec_a, isim_mutate(t_amp_d), s_amp_d),
                    np.where(dec_a, isim_mutate(t_ph_d), s_ph_d))
        if mt == IUIM:
            return (np.where(dec_a, iuim_mutate(s_amp_d, t_amp_d), s_amp_d),
                    np.where(dec_a, iuim_mutate(s_ph_d, t_ph_d), s_ph_d))
        if mt == LCM:
            return (np.where(dec_a, lcm_mutate(s_amp_d, t_amp_d), s_amp_d),
                    np.where(dec_a, lcm_mutate(s_ph_d, t_ph_d), s_ph_d))
        if mt == LCMIUIM:
            m_amp = np.where(dec_a, lcm_mutate(s_amp_d, t_amp_d), s_amp_d)
            m_ph = np.where(dec_a, lcm_mutate(s_ph_d, t_ph_d), s_ph_d)
            m_amp = np.where(dec_b, iuim_mutate(m_amp, t_amp_d), m_amp)
            m_ph = np.where(dec_b, iuim_mutate(m_ph, t_ph_d), m_ph)
            return m_amp, m_ph
        if mt == LCMUUIM:
            m_amp = np.where(dec_a, lcm_mutate(s_amp_d, t_amp_d), s_amp_d)
            m_ph = np.where(dec_a, lcm_mutate(s_ph_d, t_ph_d), s_ph_d)
            return (uuim_mutate(m_amp, t_amp_d, omega),
                    uuim_mutate(m_ph, t_ph_d, omega))
        return s_amp_d, s_ph_d  # C default: pass source deltas through

    def mutate_frame(self, source_amp: np.ndarray, source_phase: np.ndarray,
                     target_amp: np.ndarray, target_phase: np.ndarray,
                     omega: float) -> Tuple[np.ndarray, np.ndarray]:
        """One frame of mutation; returns (mutant_amp, mutant_phase)."""
        spec = self.spec

        # Step 1: amplitude deltas (absolute mode overwrites the mutant
        # amplitude base BEFORE accumulation, destroying amplitude memory).
        if spec.absolute:
            s_amp_d = source_amp - spec.source_reference
            t_amp_d = target_amp - spec.target_reference
            self.mutant_amp = np.full(
                self.half_points + 1,
                (1.0 - omega) * spec.source_reference
                + omega * spec.target_reference)
        else:
            s_amp_d = source_amp - self.source_prev_amp
            t_amp_d = target_amp - self.target_prev_amp

        # Step 2: phase deltas, always frame-relative, wrapped.
        s_ph_d = wrap_pm_pi(source_phase - self.source_prev_phase)
        t_ph_d = wrap_pm_pi(target_phase - self.target_prev_phase)

        # Step 3: the mutation function (same kernel for amp and phase).
        m_amp_d, m_ph_d = self._mutate_deltas(
            s_amp_d, t_amp_d, s_ph_d, t_ph_d, omega)

        # Step 4: accumulate. deltaEmphasis applies to amplitude only.
        e = spec.delta_emphasis
        if e >= 0.0:
            amp_result = self.mutant_amp + (1.0 - e) * m_amp_d
        else:
            amp_result = (1.0 + e) * self.mutant_amp + m_amp_d
        amp_result = np.maximum(amp_result, 0.0)
        phase_result = wrap_pm_pi(self.mutant_phase + m_ph_d)
        self.mutant_amp = amp_result
        self.mutant_phase = phase_result

        # Step 5: history update.
        self.source_prev_amp = np.array(source_amp)
        self.source_prev_phase = np.array(source_phase)
        self.target_prev_amp = np.array(target_amp)
        self.target_prev_phase = np.array(target_phase)
        return amp_result, phase_result


def spectral_mutate(source: np.ndarray, target: np.ndarray,
                    spec: MutationSpec, points: int = 1024,
                    scale_to_source: bool = False) -> np.ndarray:
    """MutateBlock(): the full mutation chain, mono signal in/out.

    Both signals are analyzed with identical Hamming phase-vocoder chains
    (window_size = points, hop = points // 8); when scale_to_source is set
    the target is hopped at a proportional rate so it spans the source's
    duration (the dialog's "scale" checkbox).

    spec.omega may be a scalar or a per-frame sequence (the drawn-function
    mode); sequences are sampled by frame index, clamped at the last value.
    The output begins one hop before input time zero (see
    stft_resynthesize).
    """
    window_size = points
    half_points = points // 2
    interpolation = decimation = window_size // 8

    f_decimation = decimation
    if scale_to_source and len(source) > 0:
        ratio = float(len(target)) / float(len(source))
        if ratio <= 1.0:
            f_decimation = max(1, int(interpolation * ratio))
        else:
            f_decimation = window_size // 8
            decimation = interpolation = max(1, int(f_decimation / ratio))

    raw = get_window(window_size, HAMMING)
    anal_win, synth_win = scale_windows(raw, raw.copy(), points, interpolation)

    src_stream = _SlidingInput(source, window_size, decimation)
    tgt_stream = _SlidingInput(target, window_size, f_decimation)
    engine = MutationEngine(half_points, spec)

    omega_seq = None
    if not np.isscalar(spec.omega):
        omega_seq = np.asarray(spec.omega, dtype=float)

    in_pointer = -window_size
    f_in_pointer = -window_size
    out_pointer = -window_size
    out_buf = np.zeros(window_size)
    emitted: List[np.ndarray] = []
    block = 0
    while True:
        in_pointer += decimation
        f_in_pointer += f_decimation
        out_pointer += interpolation

        src_alive = src_stream.shift_in()
        tgt_alive = tgt_stream.shift_in()

        src_frame = window_fold(src_stream.buf, anal_win, points, in_pointer)
        s_amp, s_ph = analyze_frame(src_frame)
        tgt_frame = window_fold(tgt_stream.buf, anal_win, points, f_in_pointer)
        t_amp, t_ph = analyze_frame(tgt_frame)

        if omega_seq is not None:
            omega = float(omega_seq[min(block, len(omega_seq) - 1)])
        else:
            omega = float(spec.omega)
        m_amp, m_ph = engine.mutate_frame(s_amp, s_ph, t_amp, t_ph, omega)

        out_frame = synthesize_frame(m_amp, m_ph, points)
        overlap_add(out_frame, synth_win, out_buf, out_pointer)
        if out_pointer + interpolation >= 0:
            emitted.append(out_buf[:interpolation].copy())
        out_buf[:-interpolation] = out_buf[interpolation:]
        out_buf[-interpolation:] = 0.0

        block += 1
        if not (src_alive and tgt_alive):
            break
    return np.concatenate(emitted) if emitted else np.zeros(0)


# ---------------------------------------------------------------------------
# Oscillator bank (AddSynth, Processing/PhaseVocoder.c pitch mode)
# ---------------------------------------------------------------------------

SINE_TABLE_SIZE = 8192
_SINE_TABLE = 0.5 * np.cos(TWO_PI * np.arange(SINE_TABLE_SIZE)
                           / SINE_TABLE_SIZE)


class OscillatorBank:
    """AddSynth(): table-lookup additive resynthesis, one call per frame.

    Faithful mechanics: an 8192-entry 0.5*cos table, truncating (non-
    interpolated) lookup, per-frame linear interpolation of amplitude and
    frequency across `interpolation` output samples, oscillator phase held
    in the running table address. Frequencies are given in cycles/sample;
    table increments are cycles * 8192.

    Where the C's zero-amplitude branch snaps the stored frequency to the
    partial's nominal FFT-bin frequency, this generalized bank (partials
    need not be FFT bins) snaps to the incoming target frequency instead.
    """

    def __init__(self, num_partials: int, interpolation: int):
        self.num_partials = num_partials
        self.interpolation = interpolation
        self.last_amp = np.zeros(num_partials)
        self.last_freq = np.zeros(num_partials)
        self.address = np.zeros(num_partials)

    def synthesize_frame(self, amps: np.ndarray,
                         freqs_cycles: np.ndarray) -> np.ndarray:
        interp = self.interpolation
        output = np.zeros(interp)
        increments = np.asarray(freqs_cycles, dtype=float) * SINE_TABLE_SIZE
        s = np.arange(interp)
        for b in range(self.num_partials):
            if amps[b] == 0.0 and self.last_amp[b] == 0.0:
                self.last_freq[b] = increments[b]
                continue
            amp_inc = (amps[b] - self.last_amp[b]) / interp
            freq_inc = (increments[b] - self.last_freq[b]) / interp
            freq_ramp = self.last_freq[b] + freq_inc * s
            addr = self.address[b] + np.concatenate(
                ([0.0], np.cumsum(freq_ramp[:-1])))
            addr_wrapped = np.mod(addr, SINE_TABLE_SIZE)
            amp_ramp = self.last_amp[b] + amp_inc * s
            output += amp_ramp * _SINE_TABLE[addr_wrapped.astype(int)]
            self.address[b] = math.fmod(
                self.address[b] + freq_ramp.sum(), SINE_TABLE_SIZE)
            self.last_amp[b] = amps[b]
            self.last_freq[b] = increments[b]
        return output


# [SPORE] ID: The Colony
