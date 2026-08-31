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
    PhaseInterpolator,
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


def test_wrap_pm_pi_large_values_wrap_fast():
    # The closed-form reduction handles arbitrarily large inputs in O(1)
    # (the naive one-period-per-iteration loop would spin ~1e15 times).
    x = np.array([1e16, -1e16, 12345.678, -98765.4321])
    out = wrap_pm_pi(x)
    assert np.all(out <= math.pi) and np.all(out >= -math.pi)
    assert out[2] == pytest.approx(
        math.atan2(math.sin(12345.678), math.cos(12345.678)), abs=1e-6)


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

def test_find_best_ratio_matches_compiled_c():
    """Pins against FindBestRatio extracted verbatim from PhaseVocoder.c,
    compiled with gcc, over (window_size, scale_factor) cases — including
    the quirky exits: the loop-condition exit at percentError <= 1.01
    returns a MISMATCHED pair (hop decremented once past the accepted
    pair), and the hop==1 fallback lands on max_hop - 1."""
    c_truth = [
        # (window_size, scale_factor, decimation, interpolation)
        (1024, 0.25, 128, 32),
        (1024, 0.503, 127, 64),      # 1.004..1.01 exit: mismatched pair
        (1024, 0.77, 127, 98),
        (1024, 1.0, 128, 128),
        (1024, 1.001, 127, 127),
        (1024, 1.01, 126, 127),
        (1024, 1.05, 121, 127),
        (1024, 1.3, 98, 127),
        (1024, 2.0, 64, 128),
        (1024, 3.0, 42, 126),
        (1024, 7.9, 16, 126),
        (256, 0.4, 30, 12),
        (256, 0.503, 31, 16),
    ]
    for ws, sf, dec, interp in c_truth:
        d, i, _ = find_best_ratio(sf, ws)
        assert (d, i) == (dec, interp), (
            f"ws={ws} sf={sf}: got ({d},{i}), C gives ({dec},{interp})")


def test_find_best_ratio_rejects_nonpositive_scale():
    with pytest.raises(ValueError):
        find_best_ratio(0.0, 1024)
    with pytest.raises(ValueError):
        find_best_ratio(-1.0, 1024)


def test_shift_in_frame_count_matches_c_countdown():
    """The C decrements validSamples on the short-read block itself, so
    for L=5000, W=256, d=32 the countdown runs 200,168,...,8,-24 and the
    analysis performs exactly 164 blocks."""
    rng = np.random.default_rng(7)
    sig = rng.standard_normal(5000)
    amps, phases, info = stft_analyze(sig, 256, 256, 32)
    assert len(amps) == 164


def test_phase_vocoder_unity_identity():
    sig = _test_signal(4000)
    out = phase_vocoder(sig, 1.0, points=256)
    out = out[32:]  # one-hop pre-roll (interpolation = 256 // 8)
    n = min(len(out), len(sig))
    a, b = sig[256:n - 256], out[256:n - 256]
    assert np.corrcoef(a, b)[0, 1] > 0.999


def test_phase_interpolate_locking_matches_compiled_c():
    """Differential pin: PhaseInterpolate extracted verbatim from
    PhaseVocoder.c, compiled with gcc (points=32, halfPoints=16,
    decimation=4, scaleFactor=1.5, phaseLocking=TRUE), run over 6 random
    frames with zero-amp bins. The port must match the C's output phases
    (float32 precision), including the in-place low-neighbor read."""
    frames_in = [
    ([0.35047096, 0, 0, 0.841929853, 0, 0.38106364, 0.574094296, 0.210155055, 0, 0, 0.886479139, 0.370990783, 0.995649993, 0.673540235, 0.736772001, 0.917374492, 0.53433466],
     [1.3937459, 0, 0, 2.7457366, 0, -1.10795057, -0.0853228122, 1.80313826, 0, 0, -1.32937205, 0.120111898, 2.66168475, 1.68578649, -1.9846971, -2.89663386, 0.679175258]),
    ([0.435365379, 0.669722974, 0.780500531, 0.37631005, 0.648124337, 0, 0.460288733, 0.354961663, 0.705963075, 0.760329783, 0.630853355, 0, 0.37058121, 0.340371817, 0, 0.644580424, 0.439200997],
     [2.90966463, 0.776380062, -0.410553515, 1.42046404, -0.33499822, 0, -2.52715349, 0.990173757, 3.0639317, 2.82005119, 1.38057792, 0, 1.44740832, -2.62781644, 0, 1.36396658, -3.11831999]),
    ([0.746281862, 0.269552976, 0.433719873, 0.787535727, 0.551008344, 0.65610683, 0.33931762, 0.787758648, 0.893295646, 0.206212386, 0, 0, 0.739402771, 0.671986818, 0.584284365, 0.847674906, 0.519822121],
     [-1.99561989, -1.85138571, -2.44813013, -3.11293554, 2.11632729, -2.10508871, -0.612589777, -0.901861429, -2.41600752, -0.675721943, 0, 0, -2.51105213, 0.904627383, -2.45617223, -1.77640152, -1.33592522]),
    ([0.487554014, 0.850067914, 0, 0, 0.999513686, 0, 0, 0.37204662, 0, 0.416217148, 0.759522855, 0.606472313, 0, 0.600272775, 0.452535123, 0.998888791, 0.206720471],
     [-1.08741975, -2.21640563, 0, 0, 0.760691583, 0, 0, 2.2645328, 0, -1.07805371, -1.86868715, -2.01636505, 0, -1.17391944, 0.184370562, -0.0317786075, 0.603537917]),
    ([0.583117783, 0.162902713, 0.976736724, 0.286163539, 0, 0.281353652, 0, 0.798536956, 0.680451274, 0.33179459, 0.457937807, 0.405137599, 0.283121765, 0, 0, 0.793019116, 0.934383273],
     [2.24909425, -1.95068169, -2.92936254, 1.99440014, 0, -1.07336187, 0, 0.76685822, 1.56602967, 2.65907311, -1.72206616, -0.837582529, -1.08626628, 0, 0, 0.17653513, 1.46069765]),
    ([0.372979462, 0.996456146, 0.905460715, 0, 0.464149088, 0.932333708, 0.547436118, 0.842563987, 0.899097681, 0.653906703, 0.366081953, 0.567157507, 0.887156785, 0.326530844, 0.206166714, 0.549127996, 0.403649062],
     [-1.5969373, -1.63903677, 2.03628922, 0, -1.74908948, -1.77853918, -1.82416606, -2.32695842, -2.27218413, -2.40281606, 1.55920088, 0.738224924, -1.60311878, -1.33766532, -0.897339821, 1.44234717, 0.599393249]),
    ]
    expected = [
    [2.09061885, 0, 0, -2.16458082, 0, 1.05011308, -0.127984226, -1.24208939, 0, 0, -1.99405813, -1.11256075, -2.29065847, -2.32342577, 3.11633205, 1.93823481, -0.208980083],
    [-1.84989882, 0.562267005, -0.615830302, 2.6325922, -0.502497315, 1.05011308, 2.49245524, -1.75127983, -0.875011444, -2.05310869, 2.08447552, -1.11256075, 2.17111254, -2.41596675, 3.11633205, 2.04595041, -0.364101619],
    [-2.92463923, -1.3160007, 0.0453529358, 2.11567831, -0.120859146, -0.445594192, 0.832499743, -2.50990629, -2.81173563, 2.45838737, 2.08447552, -1.11256075, 2.51660728, -2.33576035, -0.416122437, -2.6646018, -2.87449956],
    [-2.29407167, -1.86353064, 0.0453529358, 2.11567831, -2.15431261, -0.445594192, 0.832499743, 2.23968506, -2.81173563, -1.23741293, -2.78942204, 2.61142492, 2.51660728, 0.829604626, -2.90427613, -0.0476675034, 2.20675516],
    [2.71069956, -1.40728199, -0.676495671, -1.9663043, -2.15431261, 1.10199606, 0.832499743, -0.00682687759, 1.1328249, -3.06531715, -2.56949043, 0.162191153, 2.83817053, 0.829604626, -2.90427613, 2.41616917, -2.79069066],
    [-1.92692137, -0.939814627, -0.805759728, -1.9663043, -2.03398132, 0.0442301035, 2.38855648, 1.69713497, 1.6586895, 1.65289593, 2.33597994, 0.565009713, 2.06289172, -1.13266277, 0.172538996, -1.96829844, -2.80157042],
    ]
    interp = PhaseInterpolator(16, 1.5, 4, 32, phase_locking=True)
    for (amps, phases), exp in zip(frames_in, expected):
        out = interp.process(np.array(amps), np.array(phases))
        assert np.max(np.abs(out - np.array(exp))) < 1e-4


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


def test_oscillator_bank_zero_amp_is_hard_cut():
    """C: a silent target amplitude skips the sample loop entirely (no
    ramp-down) and freezes the oscillator's table address."""
    bank = OscillatorBank(num_partials=1, interpolation=64)
    bank.synthesize_frame(np.array([1.0]), np.array([0.05]))
    addr_before = bank.address[0]
    out = bank.synthesize_frame(np.array([0.0]), np.array([0.05]))
    assert np.all(out == 0.0)          # hard cut, not a ramp to zero
    assert bank.address[0] == addr_before  # phase frozen
    assert bank.last_amp[0] == 0.0


def test_validation_errors():
    with pytest.raises(ValueError):
        stft_analyze(np.zeros(100), points=4)
    with pytest.raises(ValueError):
        spectral_mutate(np.zeros(100), np.zeros(100),
                        MutationSpec(omega=[]), points=256)
    with pytest.raises(ValueError):
        phase_vocoder(np.zeros(100), -1.0, points=256)
    with pytest.raises(ValueError):
        stft_analyze(np.zeros(100), points=256, window_size=256,
                     decimation=512)
