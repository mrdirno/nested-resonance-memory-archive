"""
Fidelity tests for the SoundHack spectral core port (nrm_core.soundhack_spectral).

Each test pins a numeric property quoted from the original C source
(Math/FFT.c, Math/Windows.c, Math/PhaseVocoderRoutines.c,
Processing/PhaseVocoder.c, Processing/Mutate.c in
https://github.com/mrdirno/soundhack-x-NRM-Archive-).
"""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.soundhack_spectral import (
    HAMMING, VONHANN, KAISER, RECTANGLE, RAMP, TRIANGLE, SINC,
    USIM, ISIM, IUIM, UUIM, LCM, LCMIUIM, LCMUUIM,
    get_window, scale_windows, wrap_pm_pi, window_fold, analyze_frame,
    stft_analyze, stft_resynthesize, find_best_ratio, phase_vocoder,
    usim_mutate, isim_mutate, iuim_mutate, uuim_mutate, lcm_mutate,
    pick_mutate_table, MutationSpec, MutationEngine, spectral_mutate,
    OscillatorBank, SINE_TABLE_SIZE,
)

import random


def _test_signal(length, seed=7):
    rng = np.random.default_rng(seed)
    t = np.arange(length)
    sig = (0.5 * np.sin(2 * np.pi * 0.01 * t)
           + 0.3 * np.sin(2 * np.pi * 0.037 * t + 1.0)
           + 0.05 * rng.standard_normal(length))
    return sig.astype(float)


# --- Windows (Math/Windows.c) ---------------------------------------------

def test_hamming_window_formula():
    w = get_window(64, HAMMING)
    i = np.arange(64)
    expected = 0.54 - 0.46 * np.cos(2 * np.pi * i / 63)
    assert np.allclose(w, expected)


def test_vonhann_uses_nonstandard_040_coefficient():
    # SoundHack's "von Hann" is 0.50 - 0.40*cos, endpoints 0.1 (not 0.0).
    w = get_window(128, VONHANN)
    assert w[0] == pytest.approx(0.1)
    assert w[-1] == pytest.approx(0.1)
    assert w.max() == pytest.approx(0.9, abs=1e-3)


def test_kaiser_endpoints_forced_zero():
    w = get_window(64, KAISER)
    assert w[0] == 0.0
    assert w[-1] == 0.0
    assert w[32] == pytest.approx(1.0)  # ino(6.8)/ino(6.8) at center


def test_ramp_divides_by_size_not_size_minus_one():
    w = get_window(8, RAMP)
    assert w[0] == 1.0
    assert w[-1] == pytest.approx(1.0 / 8.0)


def test_triangle_shape():
    w = get_window(64, TRIANGLE)
    assert w[0] == 0.0
    assert w.max() == pytest.approx(1.0, abs=2.0 / 64)


# --- Phase wrap (the C while-loops) ---------------------------------------

def test_wrap_pm_pi_keeps_boundaries():
    # Strict inequalities: exactly +pi and -pi are NOT moved.
    x = np.array([math.pi, -math.pi, 3 * math.pi, -3 * math.pi, 0.5])
    out = wrap_pm_pi(x)
    assert out[0] == pytest.approx(math.pi)
    assert out[1] == pytest.approx(-math.pi)
    assert out[2] == pytest.approx(math.pi)
    assert out[3] == pytest.approx(-math.pi)
    assert out[4] == 0.5


# --- Fold-and-rotate phase reference (WindowFold) -------------------------

def test_window_fold_absolute_time_phase_reference():
    """For a sinusoid at exact bin center, the fold/rotate convention makes
    the measured phase CONSTANT across frames (per-hop deviation ~ 0)."""
    points = 256
    window_size = 256
    decimation = 32
    bin_k = 8
    n = np.arange(4096)
    sig = np.cos(2 * np.pi * bin_k * n / points)
    amps, phases, info = stft_analyze(sig, points, window_size, decimation)
    # Skip priming frames (first window_size/decimation hops) and EOF drain.
    steady = slice(10, len(phases) - 10)
    ph = phases[steady, bin_k]
    dev = wrap_pm_pi(np.diff(ph))
    assert np.max(np.abs(dev)) < 1e-6


# --- STFT round trip (ScaleWindows + WindowFold + OverlapAdd) -------------

def test_stft_round_trip_identity():
    sig = _test_signal(5000)
    points = 256
    amps, phases, info = stft_analyze(sig, points)
    out = stft_resynthesize(amps, phases, info)
    # The emitted stream begins one hop BEFORE input time zero (ShiftOut
    # fires at gOutPointer == -interpolation in the C) -- drop the pre-roll.
    out = out[info["decimation"]:]
    n = min(len(out), len(sig))
    assert n >= len(sig) - points
    # Compare away from the very edges (priming/drain).
    a, b = sig[256:n - 256], out[256:n - 256]
    err = np.max(np.abs(a - b)) / np.max(np.abs(a))
    assert err < 0.02
    corr = np.corrcoef(a, b)[0, 1]
    assert corr > 0.9999


# --- FindBestRatio (Processing/PhaseVocoder.c) ----------------------------

def test_find_best_ratio_unity_and_bounds():
    d, i, r = find_best_ratio(1.0, 1024)
    assert d == i == 128
    assert r == 1.0
    d, i, r = find_best_ratio(2.0, 1024)
    assert i <= 128 and d <= 128
    assert max(r, 2.0) / min(r, 2.0) < 1.004


def test_phase_vocoder_unity_identity():
    sig = _test_signal(4000)
    out = phase_vocoder(sig, 1.0, points=256)
    out = out[32:]  # one-hop pre-roll (interpolation = 256 // 8)
    n = min(len(out), len(sig))
    a, b = sig[256:n - 256], out[256:n - 256]
    assert np.corrcoef(a, b)[0, 1] > 0.999


def test_phase_vocoder_stretch_length():
    sig = _test_signal(4000)
    out = phase_vocoder(sig, 2.0, points=256)
    assert len(out) > 1.7 * len(sig)


# --- Mutation kernels (verbatim per-bin math from Mutate.c) ---------------

def test_usim_is_linear_interpolation_of_deltas():
    assert usim_mutate(2.0, -4.0, 0.0) == 2.0
    assert usim_mutate(2.0, -4.0, 1.0) == -4.0
    assert usim_mutate(2.0, -4.0, 0.5) == -1.0


def test_isim_replaces_with_target_delta():
    assert isim_mutate(-3.5) == -3.5


def test_iuim_target_magnitude_source_sign():
    assert iuim_mutate(-2.0, 5.0) == -5.0
    assert iuim_mutate(2.0, -5.0) == 5.0
    assert iuim_mutate(0.0, -5.0) == 5.0  # C: sourceDelta >= 0 branch


def test_uuim_lerp_magnitude_source_sign():
    # lerp(2, -4, 0.5) = -1; |.| with sign of source (+) -> +1
    assert uuim_mutate(2.0, -4.0, 0.5) == 1.0
    assert uuim_mutate(-2.0, 4.0, 0.5) == -1.0


def test_lcm_source_magnitude_target_sign():
    assert lcm_mutate(3.0, -1.0) == -3.0
    assert lcm_mutate(-3.0, 1.0) == 3.0
    assert lcm_mutate(-3.0, 0.0) == 3.0  # C: targetDelta >= 0 branch


# --- PickMutateTable ------------------------------------------------------

def test_pick_mutate_table_count_and_size():
    bands = 512
    num_steps = int(math.log2(bands)) * 3  # 27
    small = np.zeros(num_steps, dtype=bool)
    rng = random.Random(42)
    decision = pick_mutate_table(0.5, 1.0, bands, small, rng)
    assert len(decision) == bands + 1
    assert int(np.count_nonzero(small)) == int(0.5 * num_steps)


def test_pick_mutate_table_persistence_one_keeps_selection():
    bands = 512
    num_steps = int(math.log2(bands)) * 3
    small = np.zeros(num_steps, dtype=bool)
    rng = random.Random(1)
    d1 = pick_mutate_table(0.5, 1.0, bands, small, rng)
    snapshot = small.copy()
    d2 = pick_mutate_table(0.5, 1.0, bands, small, rng)
    # persist=1.0: no slot ever decays, count already correct -> unchanged.
    assert np.array_equal(small, snapshot)
    assert np.array_equal(d1, d2)


def test_pick_mutate_table_extremes():
    bands = 512
    num_steps = int(math.log2(bands)) * 3
    small = np.zeros(num_steps, dtype=bool)
    rng = random.Random(3)
    d = pick_mutate_table(0.0, 1.0, bands, small, rng)
    assert not d.any()
    d = pick_mutate_table(1.0, 1.0, bands, small, rng)
    assert d.all()


# --- MutationEngine end-to-end identities ---------------------------------

def test_mutation_engine_usim_omega0_tracks_source():
    engine = MutationEngine(128, MutationSpec(mutation_type=USIM, omega=0.0))
    rng = np.random.default_rng(0)
    for _ in range(5):
        s_amp = rng.uniform(0, 2, 129)
        s_ph = rng.uniform(-np.pi, np.pi, 129)
        t_amp = rng.uniform(0, 2, 129)
        t_ph = rng.uniform(-np.pi, np.pi, 129)
        m_amp, m_ph = engine.mutate_frame(s_amp, s_ph, t_amp, t_ph, 0.0)
    assert np.allclose(m_amp, s_amp)
    assert np.allclose(wrap_pm_pi(m_ph - s_ph), 0.0, atol=1e-9)


def test_mutation_engine_usim_omega1_tracks_target():
    engine = MutationEngine(128, MutationSpec(mutation_type=USIM, omega=1.0))
    rng = np.random.default_rng(1)
    for _ in range(5):
        s_amp = rng.uniform(0, 2, 129)
        s_ph = rng.uniform(-np.pi, np.pi, 129)
        t_amp = rng.uniform(0, 2, 129)
        t_ph = rng.uniform(-np.pi, np.pi, 129)
        m_amp, m_ph = engine.mutate_frame(s_amp, s_ph, t_amp, t_ph, 1.0)
    assert np.allclose(m_amp, t_amp)
    assert np.allclose(wrap_pm_pi(m_ph - t_ph), 0.0, atol=1e-9)


def test_spectral_mutate_omega0_reproduces_source():
    src = _test_signal(4000, seed=2)
    tgt = _test_signal(4000, seed=3)
    out = spectral_mutate(src, tgt,
                          MutationSpec(mutation_type=USIM, omega=0.0),
                          points=256)
    out = out[32:]  # one-hop pre-roll
    n = min(len(out), len(src))
    a, b = src[256:n - 256], out[256:n - 256]
    assert np.corrcoef(a, b)[0, 1] > 0.999


def test_spectral_mutate_omega1_reproduces_target():
    src = _test_signal(4000, seed=2)
    tgt = _test_signal(4000, seed=3)
    out = spectral_mutate(src, tgt,
                          MutationSpec(mutation_type=USIM, omega=1.0),
                          points=256)
    out = out[32:]  # one-hop pre-roll
    n = min(len(out), len(tgt))
    a, b = tgt[256:n - 256], out[256:n - 256]
    assert np.corrcoef(a, b)[0, 1] > 0.999


def test_spectral_mutate_irregular_omega0_reproduces_source():
    src = _test_signal(4000, seed=4)
    tgt = _test_signal(4000, seed=5)
    out = spectral_mutate(src, tgt,
                          MutationSpec(mutation_type=ISIM, omega=0.0, seed=9),
                          points=256)
    out = out[32:]  # one-hop pre-roll
    n = min(len(out), len(src))
    a, b = src[256:n - 256], out[256:n - 256]
    assert np.corrcoef(a, b)[0, 1] > 0.999


def test_spectral_mutate_intermediate_omega_is_neither():
    src = _test_signal(4000, seed=2)
    tgt = _test_signal(4000, seed=3)
    out = spectral_mutate(src, tgt,
                          MutationSpec(mutation_type=USIM, omega=0.5),
                          points=256)
    n = min(len(out), len(src))
    c_src = np.corrcoef(src[256:n - 256], out[256:n - 256])[0, 1]
    c_tgt = np.corrcoef(tgt[256:n - 256], out[256:n - 256])[0, 1]
    assert c_src < 0.99 and c_tgt < 0.99
    assert np.max(np.abs(out)) > 0.01  # not silence


def test_spectral_mutate_seeded_runs_reproduce():
    src = _test_signal(3000, seed=6)
    tgt = _test_signal(3000, seed=7)
    spec = MutationSpec(mutation_type=IUIM, omega=0.7,
                        band_persistence=0.5, seed=123)
    out1 = spectral_mutate(src, tgt, spec, points=256)
    spec2 = MutationSpec(mutation_type=IUIM, omega=0.7,
                         band_persistence=0.5, seed=123)
    out2 = spectral_mutate(src, tgt, spec2, points=256)
    assert np.array_equal(out1, out2)


# --- OscillatorBank (AddSynth) --------------------------------------------

def test_oscillator_bank_frequency_and_amplitude():
    interp = 128
    bank = OscillatorBank(num_partials=1, interpolation=interp)
    freq = 0.05  # cycles/sample
    frames = [bank.synthesize_frame(np.array([1.0]), np.array([freq]))
              for _ in range(40)]
    out = np.concatenate(frames[2:])  # skip the amp ramp-in
    # Table is 0.5*cos: amplitude 1.0 partial peaks at ~0.5.
    assert np.max(np.abs(out)) == pytest.approx(0.5, rel=0.02)
    spectrum = np.abs(np.fft.rfft(out * np.hanning(len(out))))
    peak_bin = int(np.argmax(spectrum))
    assert peak_bin / len(out) == pytest.approx(freq, rel=0.02)


def test_oscillator_bank_zero_amp_partial_is_silent():
    bank = OscillatorBank(num_partials=2, interpolation=64)
    out = bank.synthesize_frame(np.array([0.0, 0.0]), np.array([0.05, 0.1]))
    assert np.all(out == 0.0)
