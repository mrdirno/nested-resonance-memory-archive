"""Checks for experiments/halo/memory_estimator_qualify.py, the replacement memory estimator.

These pin the facts the qualification protocol rests on: the exact relic block each
current cell is the image of, mass conservation of the prediction, exact removal of any
cube-symmetric field by the orbit remover (and the radial-class remover's known leak on
block sums), the 48 cube symmetries, the null predictor's exactness for additive and
multiplicative nuisance from the six off-pairing entries only (so one run's effect cannot
leak into another's contrast), the block relabelling test, injection mass conservation,
the manifest check, and the decision layer's result states. No meshes needed.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import json
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
q = pytest.importorskip('memory_estimator_qualify')


def test_block_images_are_the_re_centred_map():
    for x in q.B2:
        assert np.isclose(np.mean((2 * x - 16, 2 * x - 15)), 2 * x - 15.5)
    for x in q.B4:
        assert np.isclose(np.mean(range(4 * x - 48, 4 * x - 44)), 4 * x - 46.5)
    assert q.B2[0] == 8 and q.B2[-1] == 23 and q.B4[0] == 12 and q.B4[-1] == 19


def test_prediction_is_the_exact_block_sum_and_conserves_mass():
    rng = np.random.default_rng(1)
    relic = rng.random((32, 32, 32))
    p2, p4 = q.predicted(relic, 2), q.predicted(relic, 4)
    assert p2.shape == (16, 16, 16) and p4.shape == (8, 8, 8)
    assert math.isclose(p2.sum(), relic.sum(), rel_tol=1e-12)
    assert math.isclose(p4.sum(), relic.sum(), rel_tol=1e-12)
    assert math.isclose(p2[3, 5, 7], relic[6:8, 10:12, 14:16].sum(), rel_tol=1e-12)
    assert math.isclose(p4[1, 2, 3], relic[4:8, 8:12, 12:16].sum(), rel_tol=1e-12)
    assert math.isclose(q.predicted_lag2_trilinear(relic)[1, 2, 3], relic[5:7, 9:11, 13:15].sum(), rel_tol=1e-12)


def test_orbit_remover_is_exact_where_radial_classes_leak():
    orbits, classes = q.Support(q.B2, 'orbits'), q.Support(q.B2, 'classes')
    assert orbits.nclass == 120 and classes.nclass == 66
    assert q.Support(q.B4, 'orbits').nclass == 20 and q.Support(q.B4, 'classes').nclass == 15
    u = q.B2 - 15.5
    r = np.sqrt(u[:, None, None] ** 2 + u[None, :, None] ** 2 + u[None, None, :] ** 2)
    centre_sampled = (1 + (r / 4) ** 2) ** -2.5
    for s in (orbits, classes):
        assert np.abs(s.residual(centre_sampled)).max() < 1e-12
    integrated = q.sub(q.plummer_cell_integrated(4.0, 3), q.B2)
    block_sum = q.predicted(q.plummer_cell_integrated(4.0, 3), 2)
    for field in (integrated, block_sum):
        assert q.relvar(orbits.residual(field), field) < 1e-24
    assert q.relvar(classes.residual(block_sum), block_sum) > 1e-9      # the leak the review found
    shells = q.Support(q.B2, 'shells1.0')
    assert np.abs(shells.residual(centre_sampled)).max() > 1e-3          # shells are not a remover


def test_cube_symmetries_are_48_radius_preserving_bijections():
    f = np.arange(16 ** 3, dtype=float).reshape(16, 16, 16)
    assert len({tuple(q.apply_op(f, op).ravel().astype(int)) for op in q.CUBE_OPS}) == 48
    u = np.arange(16) - 7.5
    r = np.sqrt(u[:, None, None] ** 2 + u[None, :, None] ** 2 + u[None, None, :] ** 2)
    for op in q.CUBE_OPS:
        assert np.allclose(q.apply_op(r, op), r)


def test_null_predictor_is_exact_and_does_not_read_other_runs_own_cells():
    rng = np.random.default_rng(2)
    a, b = rng.random(3), rng.random(3)
    M = [[a[i] + b[j] for j in range(3)] for i in range(3)]
    assert max(abs(q.contrast(M, i, c, 'additive')) for i in range(3) for c in range(3)) < 1e-12
    a, b = 0.3 + rng.random(3), 0.3 + rng.random(3)
    M = [[a[i] * b[j] for j in range(3)] for i in range(3)]
    assert max(abs(q.contrast(M, i, c, 'multiplicative')) for i in range(3) for c in range(3)) < 1e-12
    assert max(abs(q.contrast(M, i, i, 'hybrid', 0.05)) for i in range(3)) < 1e-3   # denominators >> den_min
    assert max(abs(q.contrast(M, i, i, 'additive')) for i in range(3)) > 1e-3       # additive alone leaks
    # an own-relic effect in run 1 only: run 1 sees it, runs 0 and 2 do not
    M[1][1] += 0.5
    assert q.contrast(M, 1, 1, 'hybrid') > 0.49
    assert abs(q.contrast(M, 0, 0, 'hybrid')) < 1e-3 and abs(q.contrast(M, 2, 2, 'hybrid')) < 1e-3
    # a common effect d in every diagonal is returned as d, not 1.5 d
    M = [[a[i] + b[j] + (0.1 if i == j else 0.0) for j in range(3)] for i in range(3)]
    assert all(math.isclose(q.contrast(M, i, i, 'additive'), 0.1, abs_tol=1e-12) for i in range(3))
    # near-zero correlations hand over smoothly to the additive form
    small = [[0.001 * v for v in row] for row in M]
    assert math.isclose(q.predict_cell(small, 0, 0, 'hybrid', 0.05), q.predict_cell(small, 0, 0, 'additive'), abs_tol=1e-6)
    # the pairing for c = i is the diagonal; for c != i it is a cyclic shift
    assert q.pairing(0, 0) == [(0, 0), (1, 1), (2, 2)] and q.pairing(0, 1) == [(0, 1), (1, 2), (2, 0)]


def test_block_relabelling_test_on_exchangeable_and_shifted_columns():
    rng = np.random.default_rng(3)
    small = 0
    for _ in range(60):
        Q = rng.standard_normal((22, 3)) * 0.05
        small += q.block_relabel_test(Q, np.random.default_rng(0))['own']['p'] < 0.05
    assert small <= 9
    Q = rng.standard_normal((22, 3)) * 0.05
    Q[:, 0] += 0.2
    r = q.block_relabel_test(Q, np.random.default_rng(0))
    assert r['own']['p'] < 0.01 and r['own']['S'] > q.S_MIN
    assert q.block_signflip_p(np.full(22, 0.3) + rng.standard_normal(22) * 0.05, np.random.default_rng(0)) < 0.01
    assert q.detection_rule(0.05, 0.01, 0.3, 0.0) and not q.detection_rule(0.05, 0.01, -0.3, 0.0)
    assert not q.detection_rule(0.01, 0.001, 0.3, 0.0)


def test_injection_preserves_block_mass_and_refuses_empty_blocks():
    rng = np.random.default_rng(4)
    cur, relic = rng.random((32, 32, 32)), rng.random((32, 32, 32))
    mixed = q.inject(cur, relic, 0.05)
    assert math.isclose(q.sub(mixed, q.B2).sum(), q.sub(cur, q.B2).sum(), rel_tol=1e-12)
    outside = np.ones((32, 32, 32), bool)
    outside[np.ix_(q.B2, q.B2, q.B2)] = False
    assert np.array_equal(mixed[outside], cur[outside])
    with pytest.raises(ValueError):
        q.inject(np.zeros((32, 32, 32)), relic, 0.1)


def test_manifest_check_reports_verified_mismatched_and_missing(tmp_path):
    f = tmp_path / 'a.json'
    f.write_bytes(b'{}')
    files = [{'file': 'a.json', 'sha256': q.sha256_file(str(f)), 'bytes': 2}]
    man = tmp_path / 'm.json'
    man.write_text(json.dumps({'files': [{'file': 'a.json', 'sha256': files[0]['sha256'], 'bytes': 2}]}))
    assert q.check_manifest(files, str(man))['verified']
    man.write_text(json.dumps({'files': [{'file': 'a.json', 'sha256': '0' * 64, 'bytes': 2},
                                         {'file': 'b.json', 'sha256': '0' * 64, 'bytes': 1}]}))
    res = q.check_manifest(files, str(man))
    assert not res['verified'] and res['mismatched'] == ['a.json'] and res['missing'] == ['b.json']


def _measure(kind, epochs=15, n_cond=1, seed=5):
    rng = np.random.default_rng(seed)
    runs = q.synth_grid(kind, rng, n_cond, epochs=epochs)
    return runs, q.measure_grid(runs, q.build_supports(), with_orientation=False, label='t')


def test_plummer_sphere_and_one_cell_are_not_measurable():
    for kind in ('plummer', 'one_cell'):
        _, measured = _measure(kind)
        for key, rec in measured.items():
            for i in range(3):
                s = q.summarise_run(rec['rows'], i, q.MAIN, np.random.default_rng(0))
                assert s['eligible_epochs'] == 0 and not s['measurable']


def test_perfect_relic_is_detected_and_shared_drive_is_not():
    _, measured = _measure('perfect_relic', epochs=16)
    for key, rec in measured.items():
        for i in range(3):
            s = q.summarise_run(rec['rows'], i, q.MAIN, np.random.default_rng(0))
            assert s['measurable'] and s['detected'] and s['own']['S'] > 0.5
    _, measured = _measure('shared_drive', epochs=16)
    for key, rec in measured.items():
        for i in range(3):
            s = q.summarise_run(rec['rows'], i, q.MAIN, np.random.default_rng(0))
            assert s['measurable'] and not s['detected'] and abs(s['own']['S']) < 0.05


def test_decision_layer_result_states():
    supports = q.build_supports()
    runs, measured = _measure('plummer')
    res = q.evaluate(runs, measured, supports, None, [], None, None)
    assert res['verdict']['result'] == 'insufficient support'
    runs, measured = _measure('perfect_relic', epochs=16, n_cond=3)
    res = q.evaluate(runs, measured, supports, None, [], None, None)
    assert res['verdict']['F5_support']['pass']
    assert res['verdict']['result'] == 'not evaluable'      # no synthetic receipt, so F1/F2 undecided
    assert len(res['detected_runs_main']) == 9
    assert res['verdict']['F3_recovery']['evaluable']        # increment-based alpha* is defined for detected runs too
    assert all(v['alpha_star'] is not None for v in res['verdict']['F3_recovery']['alpha_star_by_run'].values())


def test_main_refuses_a_grid_run_without_the_synthetic_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['x', '--input-dir', str(tmp_path), '--manifest', str(tmp_path / 'm.json')])
    with pytest.raises(SystemExit):
        q.main()
