"""
SoundHack x NRM Bridge
======================

Cross-pollination layer between SoundHack's spectral engine (ported in
nrm_core.soundhack_spectral) and the Nested Resonance Memory framework.

Four couplings, each grounded in math the two systems already share:

1. AudioRealityAdapter -- audio as a reality anchor (Gate 2.6).
   The TranscendentalBridge's entire adapter contract is a dict with
   'cpu_percent', 'memory_percent', 'disk_percent' in [0, 100]. This class
   derives those three numbers from measurable spectral properties of a
   real signal (spectral flux, RMS level, spectral centroid), making audio
   a drop-in substrate for the bridge layer with zero bridge changes --
   the Multi-Modal Anchor Validation the Universal Adapter doctrine calls
   for.

2. AudioEntropy -- a SystemEntropy-compatible entropy stream
   (get_float / get_choice) hashed deterministically from signal frames.
   Unlike the psutil+urandom stream it replaces, it is reproducible:
   the same audio yields the same entropy sequence, so experiments
   driven by it can be replayed and audited.

3. mutate_series / compose_trajectories -- Larry Polansky's morphological
   mutation functions (SoundHack's Mutate.c) generalized back to their
   original setting: arbitrary parameter streams. NRM composition merges
   two agents' states; mutation gives that merge a principled,
   literature-grounded operator that works on the DELTAS of two
   trajectories, with the mutation index omega supplied by NRM resonance
   (omega = |cos(phase_a - phase_b)|).

4. SwarmSonifier -- NRM population dynamics rendered to audio through
   SoundHack's AddSynth oscillator bank: each agent is a partial,
   amplitude follows energy, frequency follows phase velocity. The output
   is a real, measurable artifact: re-analyzing the rendered audio
   recovers the population's spectral footprint.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0 (SoundHack-derived DSP core is MIT; see
nrm_core/soundhack_spectral.py for provenance)
"""

import hashlib
import math
import struct
import wave
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import numpy as np

from .soundhack_spectral import (
    HAMMING, USIM, ISIM, IUIM, UUIM, LCM,
    get_window, wrap_pm_pi, OscillatorBank,
    usim_mutate, isim_mutate, iuim_mutate, uuim_mutate, lcm_mutate,
)

TWO_PI = 2.0 * math.pi


# ---------------------------------------------------------------------------
# 1. Audio as a reality anchor (Gate 2.6 substrate)
# ---------------------------------------------------------------------------

class AudioRealityAdapter:
    """Derive the TranscendentalBridge reality-metrics contract from audio.

    Frame-by-frame spectral measurements of a real signal, mapped onto the
    three keys the bridge reads (all in [0, 100]):

    - cpu_percent    <- spectral flux: positive per-frame change in the
                        magnitude spectrum, normalized by the frame's total
                        magnitude (activity / load).
    - memory_percent <- RMS level on a 60 dB window below full scale
                        (occupancy).
    - disk_percent   <- spectral centroid as a fraction of Nyquist
                        (where the mass sits).

    Every metrics dict also carries the raw measurements
    (spectral_flux, rms_db, centroid_hz) and a frame timestamp in seconds,
    which the bridge preserves verbatim in TranscendentalState.reality_anchor.
    """

    def __init__(self, signal: np.ndarray, sample_rate: int = 44100,
                 points: int = 1024, decimation: Optional[int] = None):
        self.signal = np.asarray(signal, dtype=float)
        self.sample_rate = sample_rate
        self.points = points
        self.decimation = decimation if decimation is not None else points // 2
        self._window = get_window(points, HAMMING)
        self._analyze()

    def _analyze(self) -> None:
        sig, points, hop = self.signal, self.points, self.decimation
        num_frames = max(1, 1 + (len(sig) - points) // hop) \
            if len(sig) >= points else 1
        flux = np.zeros(num_frames)
        rms = np.zeros(num_frames)
        centroid = np.zeros(num_frames)
        prev_amp = None
        freqs = np.fft.rfftfreq(points, d=1.0 / self.sample_rate)
        for k in range(num_frames):
            frame = np.zeros(points)
            chunk = sig[k * hop:k * hop + points]
            frame[:len(chunk)] = chunk
            amp = np.abs(np.fft.rfft(frame * self._window))
            total = amp.sum()
            if prev_amp is not None and total > 0:
                flux[k] = np.maximum(amp - prev_amp, 0.0).sum() / total
            rms[k] = math.sqrt(float(np.mean(frame * frame)))
            centroid[k] = float((freqs * amp).sum() / total) if total > 0 \
                else 0.0
            prev_amp = amp
        self.spectral_flux = flux
        self.rms = rms
        self.centroid_hz = centroid
        self.num_frames = num_frames

    def metrics_at(self, frame_index: int) -> Dict[str, float]:
        """One reality-metrics dict, satisfying the bridge adapter contract."""
        k = min(max(frame_index, 0), self.num_frames - 1)
        cpu = min(100.0, 100.0 * self.spectral_flux[k])
        rms_db = 20.0 * math.log10(self.rms[k]) if self.rms[k] > 0 else -120.0
        memory = min(100.0, max(0.0, 100.0 * (rms_db + 60.0) / 60.0))
        disk = min(100.0, 100.0 * self.centroid_hz[k]
                   / (self.sample_rate / 2.0))
        return {
            "cpu_percent": float(cpu),
            "memory_percent": float(memory),
            "disk_percent": float(disk),
            "spectral_flux": float(self.spectral_flux[k]),
            "rms_db": float(rms_db),
            "centroid_hz": float(self.centroid_hz[k]),
            "timestamp": float(k * self.decimation / self.sample_rate),
        }

    def frames(self) -> Iterator[Dict[str, float]]:
        for k in range(self.num_frames):
            yield self.metrics_at(k)


class AudioEntropy:
    """SystemEntropy-compatible entropy stream derived from audio frames.

    Implements the exact two-method contract of
    src/core/system_entropy.SystemEntropy -- get_float() -> [0, 1) and
    get_choice(options) -- but is DETERMINISTIC for a given signal:
    each call hashes (frame bytes, call counter) with SHA-256 and takes
    the first 8 digest bytes / 2**64, so experiment runs driven by audio
    entropy can be replayed bit-for-bit.
    """

    def __init__(self, signal: np.ndarray, frame_size: int = 1024):
        sig = np.asarray(signal, dtype=np.float64)
        self._frames = [sig[i:i + frame_size].tobytes()
                        for i in range(0, max(len(sig), 1), frame_size)]
        self._counter = 0

    def get_float(self) -> float:
        frame = self._frames[self._counter % len(self._frames)]
        data = frame + struct.pack(">Q", self._counter)
        self._counter += 1
        digest = hashlib.sha256(data).digest()
        return int.from_bytes(digest[:8], "big") / 2 ** 64

    def get_choice(self, options: list):
        return options[int(self.get_float() * len(options))]


# ---------------------------------------------------------------------------
# 2. Morphological mutation as an NRM composition operator
# ---------------------------------------------------------------------------

def mutate_series(source: Sequence[float], target: Sequence[float],
                  mutation_type: int = USIM, omega=0.5,
                  wrap_period: Optional[float] = None,
                  decision: Optional[np.ndarray] = None) -> np.ndarray:
    """Polansky morphological mutation on two arbitrary 1-D series.

    This is Mutate.c's per-bin recurrence lifted out of the spectral frame
    and applied along time: deltas of source and target are combined by
    the chosen kernel and accumulated from zero, exactly as the mutant
    spectrum accumulates frame-to-frame (first delta measured against 0,
    matching the zeroed j-buffers of the original).

    omega may be a scalar or a per-step array. wrap_period (e.g. 2*pi for
    phase trajectories) applies circular wrapping to deltas and output,
    mirroring the phase path of MutateSpectrum. `decision` (bool array,
    one per step) gates the irregular types along TIME the way
    PickMutateTable gates them along frequency; unset means all steps
    mutate.
    """
    src = np.asarray(source, dtype=float)
    tgt = np.asarray(target, dtype=float)
    if len(src) != len(tgt):
        raise ValueError("source and target series must have equal length")
    n = len(src)
    omega_arr = np.broadcast_to(np.asarray(omega, dtype=float), (n,))
    if decision is None:
        decision = np.ones(n, dtype=bool)

    def _wrap(x):
        if wrap_period is None:
            return x
        half = wrap_period / 2.0
        out = np.array(x, dtype=float)
        while np.any(out > half):
            out = np.where(out > half, out - wrap_period, out)
        while np.any(out < -half):
            out = np.where(out < -half, out + wrap_period, out)
        return out

    s_prev = 0.0
    t_prev = 0.0
    m_prev = 0.0
    out = np.empty(n)
    for k in range(n):
        s_d = _wrap(src[k] - s_prev)
        t_d = _wrap(tgt[k] - t_prev)
        w = omega_arr[k]
        if mutation_type == USIM:
            m_d = usim_mutate(s_d, t_d, w)
        elif mutation_type == UUIM:
            m_d = uuim_mutate(s_d, t_d, w)
        elif mutation_type == ISIM:
            m_d = isim_mutate(t_d) if decision[k] else s_d
        elif mutation_type == IUIM:
            m_d = iuim_mutate(s_d, t_d) if decision[k] else s_d
        elif mutation_type == LCM:
            m_d = lcm_mutate(s_d, t_d) if decision[k] else s_d
        else:
            m_d = s_d
        m = _wrap(m_prev + float(m_d))
        out[k] = m
        s_prev, t_prev, m_prev = src[k], tgt[k], float(m)
    return out


def resonance_omega(phase_a: float, phase_b: float) -> float:
    """NRM pairwise resonance as a mutation index: |cos(dphi)| in [0, 1].

    The same quantity FractalAgent.calculate_resonance caches (absolute
    value), reused as Polansky's omega: fully aligned agents (resonance 1)
    mutate all the way toward each other; orthogonal agents (resonance 0)
    leave the source untouched.
    """
    return abs(math.cos(phase_a - phase_b))


def compose_trajectories(traj_a: Sequence[float], traj_b: Sequence[float],
                         mutation_type: int = USIM,
                         resonance_threshold: float = 0.7
                         ) -> Tuple[np.ndarray, np.ndarray]:
    """Compose two agent phase trajectories via resonance-gated mutation.

    Per step, omega = |cos(a_k - b_k)| (NRM resonance); steps below
    `resonance_threshold` (the CompositionEngine default 0.7) do not
    mutate, mirroring can_compose's gate. Returns (composed_trajectory,
    omega_series). Phases wrap on 2*pi.
    """
    a = np.asarray(traj_a, dtype=float)
    b = np.asarray(traj_b, dtype=float)
    omegas = np.abs(np.cos(a - b))
    decision = omegas >= resonance_threshold
    composed = mutate_series(a, b, mutation_type=mutation_type,
                             omega=omegas * decision,
                             wrap_period=TWO_PI,
                             decision=decision)
    return np.mod(composed, TWO_PI), omegas


# ---------------------------------------------------------------------------
# 3. Swarm sonification (AddSynth oscillator bank)
# ---------------------------------------------------------------------------

class SwarmSonifier:
    """Render NRM population dynamics to audio via the AddSynth bank.

    Each agent is one partial of a SoundHack oscillator bank:
    - amplitude follows the agent's energy (normalized by `energy_scale`);
    - frequency follows the agent's phase velocity, mapped so that one
      full phase cycle per NRM tick lands at `base_freq_hz`.

    One NRM tick = one AddSynth frame of `interpolation` output samples,
    with the bank's own linear amp/freq interpolation smoothing between
    ticks -- the same mechanism that smooths phase-vocoder frames.
    """

    def __init__(self, num_agents: int, sample_rate: int = 44100,
                 interpolation: int = 256, base_freq_hz: float = 220.0,
                 energy_scale: float = 100.0):
        self.sample_rate = sample_rate
        self.base_freq_hz = base_freq_hz
        self.energy_scale = energy_scale
        self.bank = OscillatorBank(num_agents, interpolation)

    def render_tick(self, energies: Sequence[float],
                    phase_velocities: Sequence[float]) -> np.ndarray:
        """One NRM tick -> `interpolation` audio samples.

        phase_velocities are in radians per tick (as FractalAgent stores
        velocity); energy is clipped at energy_scale for unit amplitude.
        """
        amps = np.clip(np.asarray(energies, dtype=float)
                       / self.energy_scale, 0.0, 1.0)
        cycles_per_tick = np.asarray(phase_velocities, dtype=float) / TWO_PI
        freqs_hz = np.abs(cycles_per_tick) * self.base_freq_hz * TWO_PI
        freqs_cycles = np.clip(freqs_hz / self.sample_rate, 0.0, 0.5)
        return self.bank.synthesize_frame(amps, freqs_cycles)

    def render_run(self, energy_series: np.ndarray,
                   velocity_series: np.ndarray) -> np.ndarray:
        """Render a full run: arrays shaped (ticks, agents) -> signal."""
        ticks = [self.render_tick(e, v)
                 for e, v in zip(energy_series, velocity_series)]
        out = np.concatenate(ticks) if ticks else np.zeros(0)
        peak = np.max(np.abs(out)) if len(out) else 0.0
        return out / peak * 0.9 if peak > 0 else out


def write_wav(path: str, signal: np.ndarray, sample_rate: int = 44100) -> None:
    """Write a mono float signal in [-1, 1] as 16-bit PCM."""
    pcm = np.clip(np.asarray(signal, dtype=float), -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm.tobytes())


def read_wav(path: str) -> Tuple[np.ndarray, int]:
    """Read a WAV written by write_wav back to float in [-1, 1]."""
    with wave.open(path, "rb") as f:
        rate = f.getframerate()
        n = f.getnframes()
        data = np.frombuffer(f.readframes(n), dtype="<i2")
        if f.getnchannels() > 1:
            data = data.reshape(-1, f.getnchannels())[:, 0]
    return data.astype(float) / 32767.0, rate


# [SPORE] ID: The Colony
