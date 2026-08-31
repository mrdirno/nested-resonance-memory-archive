"""
Tests for the SoundHack x NRM bridge (nrm_core.soundhack_bridge).

Covers the four couplings: audio as a reality anchor (the
TranscendentalBridge adapter contract, i.e. Gate 2.6), audio-derived
entropy (SystemEntropy contract), Polansky mutation as an NRM composition
operator, and swarm sonification with a measurable reality round trip
(swarm -> audio -> re-analysis).
"""
import math
import os
import shutil
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.soundhack_bridge import (
    AudioRealityAdapter, AudioEntropy, mutate_series, resonance_omega,
    compose_trajectories, SwarmSonifier, write_wav, read_wav,
)
from nrm_core.soundhack_spectral import USIM, ISIM, LCM
from nrm_core.fractal import FractalAgent, Population


def _tone(freq_norm, length=16384, amp=0.5):
    return amp * np.sin(2 * np.pi * freq_norm * np.arange(length))


# --- AudioRealityAdapter: the bridge adapter contract ---------------------

def test_adapter_emits_bridge_contract_keys_in_range():
    sig = _tone(0.05) + 0.1 * np.random.default_rng(0).standard_normal(16384)
    adapter = AudioRealityAdapter(sig, sample_rate=44100)
    for metrics in adapter.frames():
        for key in ("cpu_percent", "memory_percent", "disk_percent"):
            assert key in metrics
            assert 0.0 <= metrics[key] <= 100.0
        assert "timestamp" in metrics


def test_adapter_centroid_tracks_frequency():
    low = AudioRealityAdapter(_tone(0.02), sample_rate=44100)
    high = AudioRealityAdapter(_tone(0.30), sample_rate=44100)
    mid = low.num_frames // 2
    assert (high.metrics_at(mid)["disk_percent"]
            > low.metrics_at(mid)["disk_percent"])


def test_adapter_silence_vs_signal_memory():
    silent = AudioRealityAdapter(np.zeros(8192))
    loud = AudioRealityAdapter(_tone(0.05, amp=0.9))
    assert silent.metrics_at(3)["memory_percent"] == 0.0
    assert loud.metrics_at(3)["memory_percent"] > 50.0


def test_adapter_feeds_legacy_transcendental_bridge(tmp_path):
    """Gate 2.6 in miniature: the audio substrate drives the legacy
    TranscendentalBridge with zero bridge changes."""
    src_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'src'))
    saved_path = list(sys.path)
    sys.path.insert(0, src_path)
    try:
        from bridge.transcendental_bridge import TranscendentalBridge
    finally:
        # Wholesale restore: the legacy module itself prepends src/ to
        # sys.path at import, which would otherwise leak a top-level
        # 'core' package into the rest of the pytest session.
        sys.path[:] = saved_path

    bridge = TranscendentalBridge(workspace_path=str(tmp_path))
    adapter = AudioRealityAdapter(_tone(0.05) * np.linspace(0, 1, 16384))
    states = [bridge.reality_to_phase(m) for m in adapter.frames()]
    assert len(states) == adapter.num_frames
    for s in states:
        assert 0.0 <= s.pi_phase < 2 * math.pi
        assert 0.0 <= s.e_phase < 2 * math.pi
        assert 0.0 <= s.phi_phase < 2 * math.pi
    # Round trip preserves the audio anchor verbatim (Reality Imperative).
    anchor = bridge.phase_to_reality(states[5])
    assert anchor["centroid_hz"] == adapter.metrics_at(5)["centroid_hz"]
    # Resonance detection operates on audio-anchored states unchanged.
    match = bridge.detect_resonance(states[5], states[6])
    assert 0.0 <= match.similarity <= 1.0


# --- AudioEntropy: the SystemEntropy contract -----------------------------

def test_audio_entropy_range_and_determinism():
    sig = _tone(0.07, length=4096)
    e1 = AudioEntropy(sig)
    e2 = AudioEntropy(sig)
    seq1 = [e1.get_float() for _ in range(50)]
    seq2 = [e2.get_float() for _ in range(50)]
    assert seq1 == seq2  # reproducible, unlike psutil+urandom
    assert all(0.0 <= x < 1.0 for x in seq1)
    assert len(set(seq1)) > 40  # and non-degenerate


def test_audio_entropy_differs_across_signals():
    a = AudioEntropy(_tone(0.07, length=4096))
    b = AudioEntropy(_tone(0.11, length=4096))
    assert [a.get_float() for _ in range(10)] != \
           [b.get_float() for _ in range(10)]


def test_audio_entropy_get_choice():
    e = AudioEntropy(_tone(0.05, length=2048))
    options = ["compose", "decompose", "hold"]
    picks = {e.get_choice(options) for _ in range(60)}
    assert picks <= set(options)
    assert len(picks) > 1


# --- Morphological mutation as composition operator -----------------------

def test_mutate_series_omega_extremes():
    rng = np.random.default_rng(3)
    src = np.cumsum(rng.standard_normal(200))
    tgt = np.cumsum(rng.standard_normal(200))
    assert np.allclose(mutate_series(src, tgt, USIM, omega=0.0), src)
    assert np.allclose(mutate_series(src, tgt, USIM, omega=1.0), tgt)


def test_mutate_series_huge_deltas_wrap_fast():
    # Unwrapped trajectories accumulate thousands of radians; the wrap
    # must be closed-form, not one period per iteration.
    a = np.linspace(0, 1e7, 50)
    b = np.linspace(1e7, 0, 50)
    out = mutate_series(a, b, USIM, omega=0.5, wrap_period=2 * np.pi)
    assert np.all(np.abs(out) <= np.pi + 1e-9)


def test_mutate_series_wrap_period_keeps_phases_bounded():
    rng = np.random.default_rng(4)
    a = np.mod(np.cumsum(0.3 * rng.standard_normal(300)), 2 * np.pi)
    b = np.mod(np.cumsum(0.3 * rng.standard_normal(300)), 2 * np.pi)
    out = mutate_series(a, b, USIM, omega=0.5, wrap_period=2 * np.pi)
    assert np.all(np.abs(out) <= np.pi + 1e-9)


def test_resonance_omega_matches_nrm_resonance():
    assert resonance_omega(1.0, 1.0) == pytest.approx(1.0)
    assert resonance_omega(0.0, np.pi / 2) == pytest.approx(0.0, abs=1e-12)
    # Same |cos| the rich FractalAgent caches in state.resonance.
    assert resonance_omega(0.3, 1.1) == pytest.approx(abs(math.cos(-0.8)))


def test_compose_trajectories_identical_agents_fuse():
    t = np.linspace(0, 8 * np.pi, 400) % (2 * np.pi)
    composed, omegas = compose_trajectories(t, t, USIM)
    assert np.allclose(omegas, 1.0)
    d = np.abs(np.exp(1j * composed) - np.exp(1j * t))
    assert np.max(d) < 1e-6


def test_compose_trajectories_orthogonal_agents_do_not_mutate():
    n = 300
    a = np.full(n, 0.5)
    b = np.full(n, 0.5 + np.pi / 2)  # resonance |cos(pi/2)| = 0 < 0.7
    composed, omegas = compose_trajectories(a, b, USIM)
    assert np.max(omegas) < 0.7
    d = np.abs(np.exp(1j * composed) - np.exp(1j * a))
    assert np.max(d) < 1e-9


def test_compose_nrm_core_agent_trajectories():
    """Composition operator applied to real nrm_core FractalAgent runs."""
    import random
    random.seed(20260831)  # FractalAgent phases draw from global random
    a1 = FractalAgent("sh_a", energy=1.0)
    a2 = FractalAgent("sh_b", energy=1.0)
    pop = Population()
    pop.add(a1)
    pop.add(a2)
    traj1, traj2 = [], []
    for _ in range(100):
        a1.coupled_evolve(0.1, [a2], coupling_strength=2.0)
        a2.coupled_evolve(0.1, [a1], coupling_strength=2.0)
        traj1.append(a1.phase_state.phases[0])
        traj2.append(a2.phase_state.phases[0])
    composed, omegas = compose_trajectories(traj1, traj2, mutation_type=LCM)
    assert len(composed) == 100
    assert np.all((composed >= 0) & (composed < 2 * np.pi))
    # Kuramoto coupling (K=2.0, dt=0.1, 100 steps) synchronizes the pair:
    # with this seed the run ends fully phase-locked.
    assert np.mean(omegas[-20:]) >= np.mean(omegas[:20])
    assert np.mean(omegas[-20:]) > 0.99


# --- SwarmSonifier: population -> audio -> re-analysis --------------------

def test_sonifier_output_shape_and_bounds():
    son = SwarmSonifier(num_agents=3, interpolation=128)
    ticks = 50
    energies = np.full((ticks, 3), 80.0)
    velocities = np.full((ticks, 3), 0.1)  # swarm base rate, rad/tick
    out = son.render_run(energies, velocities)
    assert len(out) == ticks * 128
    assert np.max(np.abs(out)) <= 0.9 + 1e-9
    assert np.max(np.abs(out)) > 0.1


def test_sonifier_dead_swarm_is_silent():
    son = SwarmSonifier(num_agents=2, interpolation=64)
    out = son.render_run(np.zeros((10, 2)), np.full((10, 2), 0.1))
    assert np.all(out == 0.0)


def test_sonifier_wav_round_trip_recovers_dynamics(tmp_path):
    """Reality loop: a two-phase population run is rendered to a real WAV,
    read back, and re-analyzed; the loud/quiet epochs must be recoverable
    from the audio alone."""
    son = SwarmSonifier(num_agents=4, interpolation=256, base_freq_hz=440.0)
    ticks = 80
    energies = np.zeros((ticks, 4))
    energies[:40] = 90.0   # epoch 1: energetic swarm
    energies[40:] = 5.0    # epoch 2: starving swarm
    velocities = np.full((ticks, 4), 0.1)
    velocities[:, 1] *= 2.0
    velocities[:, 2] *= 3.0
    velocities[:, 3] *= 4.0
    signal = son.render_run(energies, velocities)

    path = str(tmp_path / "swarm.wav")
    write_wav(path, signal, 44100)
    back, rate = read_wav(path)
    assert rate == 44100
    assert len(back) == len(signal)

    adapter = AudioRealityAdapter(back, sample_rate=44100)
    n = adapter.num_frames
    first = np.mean([adapter.metrics_at(k)["memory_percent"]
                     for k in range(2, n // 2 - 2)])
    second = np.mean([adapter.metrics_at(k)["memory_percent"]
                      for k in range(n // 2 + 2, n - 2)])
    assert first > second + 10.0  # energy epoch audible in the metrics
