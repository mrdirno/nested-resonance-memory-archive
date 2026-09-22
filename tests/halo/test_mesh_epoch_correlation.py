"""Checks for experiments/halo/mesh_epoch_correlation.py, the Ring 29 unscored diagnostic.

These pin what the script reports: Pearson per epoch straight from the *.mesh.f32 bytes
(24 x 32^3 float32, epoch-major), 1.0 for a run against itself, near 0 for independent
noise, the median over the scorer's 1-based scored window (3-24) distinct from the
all-epoch median, shared seeds discovered from the run filenames, and a JSON output whose
summary is the median of the per-pair medians. Numbers only; the script decides nothing.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import json
import os
import subprocess
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
mec = pytest.importorskip('mesh_epoch_correlation')
SCRIPT = os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo', 'mesh_epoch_correlation.py')


def _write(dir_, cond, seed, mesh):
    p = os.path.join(dir_, f'{cond}_seed{seed}_n4194304_e24_fieldExp1.7.mesh.f32')
    mesh.astype('<f4').tofile(p)
    return p


def test_pearson_is_one_on_self_and_near_zero_on_independent_noise():
    rng = np.random.default_rng(7)
    a, b = rng.random(mec.CELLS), rng.random(mec.CELLS)
    assert abs(mec.pearson(a, a) - 1.0) < 1e-12
    assert abs(mec.pearson(a, b)) < 0.02
    assert np.isnan(mec.pearson(np.ones(mec.CELLS), a))  # a constant field has no correlation


def test_load_mesh_reshapes_epoch_major_and_refuses_a_partial_file(tmp_path):
    rng = np.random.default_rng(1)
    m = rng.random((24, mec.CELLS))
    p = _write(tmp_path, 'c', 1, m)
    back = mec.load_mesh(p)
    assert back.shape == (24, mec.CELLS)
    assert np.allclose(back[5], m[5].astype('<f4'))
    bad = tmp_path / 'short.mesh.f32'
    bad.write_bytes(b'\x00' * (mec.CELLS * 4 + 8))
    with pytest.raises(SystemExit):
        mec.load_mesh(str(bad))


def test_scored_window_median_differs_from_all_epoch_median(tmp_path):
    rng = np.random.default_rng(3)
    base = rng.random((24, mec.CELLS))
    other = rng.random((24, mec.CELLS))
    # epochs 1-2 identical (r = 1), epochs 3-24 independent (r ~ 0)
    other[:2] = base[:2]
    pa, pb = _write(tmp_path, 'a', 5, base), _write(tmp_path, 'b', 5, other)
    r = mec.per_epoch(pa, pb, 3, 24)
    assert r['epochs'] == 24
    assert r['r_by_epoch'][0] == 1.0 and r['r_by_epoch'][1] == 1.0
    assert abs(r['median_scored']) < 0.02
    assert r['max_all'] == 1.0
    assert r['median_all'] < 0.5  # 2 of 24 at 1.0 cannot carry the median


def test_runs_of_finds_seeds_and_the_cli_writes_the_summary(tmp_path):
    rng = np.random.default_rng(11)
    for cond in ('spinchladni_sg0.3_gl0', 'spinchladni_sg0.32_gl0'):
        for seed in (777, 12345, 31337):
            _write(tmp_path, cond, seed, rng.random((24, mec.CELLS)))
    _write(tmp_path, 'spinchladni_sg0.32_gl0', 2718, rng.random((24, mec.CELLS)))  # unshared seed
    assert sorted(mec.runs_of(str(tmp_path), 'spinchladni_sg0.32_gl0')) == [777, 2718, 12345, 31337]
    out = tmp_path / 'x.json'
    res = subprocess.run([sys.executable, SCRIPT, str(tmp_path), '--a', 'spinchladni_sg0.3_gl0',
                          '--b', 'spinchladni_sg0.32_gl0', '--json', str(out)],
                         capture_output=True, text=True, check=True)
    assert 'seed    777' in res.stdout
    j = json.loads(out.read_text())
    assert j['shared_seeds'] == [777, 12345, 31337]
    assert j['scored_epochs'] == [3, 24]
    assert len(j['same_seed_cross_condition']) == 3
    assert len(j['cross_seed_within_b']) == 6  # 4 seeds in b -> 6 pairs
    assert len(j['cross_seed_within_a']) == 3
    for block in ('same_seed_cross_condition', 'cross_seed_within_b', 'cross_seed_within_a'):
        assert all(abs(x['median_scored']) < 0.03 for x in j[block].values())
    assert abs(j['summary']['same_seed_cross_condition_median_of_medians_scored']) < 0.03
