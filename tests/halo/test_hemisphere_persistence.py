"""Checks for experiments/halo/hemisphere_persistence.py, the Ring 30 unscored mechanism
diagnostic.

These pin what the script reports: the north/south split on mesh axis 1 (y, the spin
axis; north = index 16..31), the scorer's lag-one pairs (relic mesh e-1 -> current mesh
e for e = 3..24, 22 pairs), a same-sign count of the current's inner block B2 against
the relic's whole mesh, the eligible-epoch count when a qualification.json names the
eligible epochs, and the per-condition count of scored meshes in which two seeds share a
hemisphere. Numbers only; the script decides nothing.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import json
import os
import subprocess
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
hp = pytest.importorskip('hemisphere_persistence')
SCRIPT = os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo', 'hemisphere_persistence.py')
N = hp.MESH_N


def _blob(north, rng=None, epochs=24, signs=None):
    """A run whose mass sits in one hemisphere of B2 each epoch (sign +1 north, -1 south)."""
    m = np.full((epochs, N, N, N), 1e-3)
    for e in range(epochs):
        s = signs[e] if signs is not None else (1 if north else -1)
        y0 = 18 if s > 0 else 10
        m[e, 14:18, y0:y0 + 3, 14:18] += 5.0
        if rng is not None:
            m[e] += rng.random((N, N, N)) * 1e-2
    return m


def _write_run(dir_, seed, mesh, sg=0.3):
    tag = f'spinchladni_sg{sg}_gl0_seed{seed}_n4194304_e24_fieldExp1.7'
    mesh.astype('<f4').tofile(os.path.join(dir_, tag + '.mesh.f32'))
    with open(os.path.join(dir_, tag + '.json'), 'w') as fh:
        json.dump({'tag': tag, 'schema': 'halo-memory-prereg/1', 'mesh_file': tag + '.mesh.f32',
                   'mesh_count': mesh.shape[0],
                   'params': {'preset': 'spinchladni', 'selfgrav': sg, 'gainloss': 0, 'seed': seed,
                              'particles': 4194304}}, fh)


def test_split_is_north_minus_south_over_total_on_axis_one():
    m = np.zeros((N, N, N))
    m[:, 20, :] = 3.0      # north (y index 20)
    m[:, 5, :] = 1.0       # south
    assert abs(hp.split(m) - 0.5) < 1e-12
    assert np.isnan(hp.split(np.zeros((N, N, N))))
    assert hp.sign(0.2) == 1 and hp.sign(-1e-9) == -1 and hp.sign(float('nan')) == 0


def test_a_run_that_keeps_its_hemisphere_scores_every_scored_pair():
    r = hp.run_numbers(_blob(True))
    assert r['pairs_scored'] == 22 and [p['e'] for p in r['pairs']] == list(range(3, 25))
    assert r['same_sign_scored'] == 22
    assert r['pairs_eligible'] is None


def test_a_run_that_alternates_hemisphere_scores_no_scored_pair():
    signs = [1 if e % 2 == 0 else -1 for e in range(24)]
    r = hp.run_numbers(_blob(True, signs=signs))
    assert r['same_sign_scored'] == 0
    assert r['lag1_autocorr_whole_split'] < -0.9


def test_eligible_mask_restricts_the_count_to_the_named_epochs():
    signs = [1] * 12 + [-1] * 12
    elig = {e: (e >= 14) for e in range(3, 25)}
    r = hp.run_numbers(_blob(True, signs=signs), elig)
    # pairs e = 3..24; the one sign change sits between meshes 12 and 13 (pair e = 13)
    assert r['same_sign_scored'] == 21
    assert r['pairs_eligible'] == 11 and r['same_sign_eligible'] == 11


def test_cli_discovers_runs_by_json_and_counts_shared_hemispheres(tmp_path):
    rng = np.random.default_rng(3)
    _write_run(tmp_path, 1, _blob(True, rng))
    _write_run(tmp_path, 2, _blob(True, rng))
    _write_run(tmp_path, 3, _blob(False, rng))
    out = tmp_path / 'hp.json'
    subprocess.run([sys.executable, SCRIPT, str(tmp_path), '--json', str(out)], check=True,
                   capture_output=True, text=True)
    res = json.load(open(out))
    agree = res['conditions']['spinchladni_sg0.3_gl0']['b2_same_hemisphere_scored']
    assert agree == {'1-2': 22, '1-3': 0, '2-3': 0}
    assert all(res['runs'][k]['same_sign_scored'] == 22 for k in res['runs'])
