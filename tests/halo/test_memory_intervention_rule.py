"""Checks for the Ring 30 analysis scripts: experiments/halo/memory_intervention_frames.py (the
carried frame D_j = T^j C_j) and experiments/halo/memory_intervention_decide.py (the
frame-preference rule on frozen-scorer output).

The frame builder must reverse the named mesh axes on the odd-indexed meshes only, leave the
even ones byte-for-byte alone, be its own inverse, write byte-identical output when run twice,
and keep schema, params and tag so the frozen loader keys a derived run exactly as its source.
The rule must sign a run only past the 0.04 margin on d = S(frame) - S(lab), whether or not
the frozen scorer detected it, never sign a run that is unmeasured in either frame, and give an
arm a preference only when two of three conditions agree and none dissents.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import json
import os
import subprocess
import sys

import numpy as np
import pytest

HALO = os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo')
sys.path.insert(0, HALO)
frames = pytest.importorskip('memory_intervention_frames')
decide = pytest.importorskip('memory_intervention_decide')


def _run(tmp, seed, meshes):
    tag = f'spinchladni_sg0.3_gl0_seed{seed}_n4194304_e24_fieldExp1.7_ivmatter'
    meshes.astype('<f4').tofile(os.path.join(tmp, tag + '.mesh.f32'))
    rec = {'tag': tag, 'schema': 'halo-memory-prereg/1', 'mesh_file': tag + '.mesh.f32', 'mesh_count': meshes.shape[0],
           'params': {'preset': 'spinchladni', 'selfgrav': 0.3, 'gainloss': 0, 'seed': seed, 'particles': 4194304}}
    with open(os.path.join(tmp, tag + '.json'), 'w') as fh:
        json.dump(rec, fh)
    return rec


def test_derive_reverses_named_axes_on_odd_meshes_only_and_is_an_involution():
    rng = np.random.default_rng(1)
    m = rng.random((4, 32, 32, 32)).astype('<f4')
    d = frames.derive(m, 'point')
    assert np.array_equal(d[0], m[0]) and np.array_equal(d[2], m[2])
    assert np.array_equal(d[1], m[1][::-1, ::-1, ::-1]) and np.array_equal(d[3], m[3][::-1, ::-1, ::-1])
    y = frames.derive(m, 'mirror')
    assert np.array_equal(y[1], m[1][:, ::-1, :]) and np.array_equal(y[0], m[0])
    assert np.array_equal(frames.derive(frames.derive(m, 'mirror'), 'mirror'), m)


def test_cli_writes_a_loadable_record_and_is_byte_deterministic(tmp_path):
    src, a, b = tmp_path / 'src', tmp_path / 'a', tmp_path / 'b'
    src.mkdir()
    rng = np.random.default_rng(2)
    rec = _run(str(src), 777, rng.random((24, 32, 32, 32)))
    script = os.path.join(HALO, 'memory_intervention_frames.py')
    for out in (a, b):
        subprocess.run([sys.executable, script, str(src), '--op', 'point', '--out', str(out)], check=True, capture_output=True)
    names = sorted(os.listdir(a))
    assert names == sorted(os.listdir(b))
    for n in names:
        assert open(a / n, 'rb').read() == open(b / n, 'rb').read()
    got = json.load(open(a / (rec['tag'] + '.json')))
    assert got['schema'] == rec['schema'] and got['params'] == rec['params'] and got['tag'] == rec['tag']
    assert got['mesh_file'].endswith('.frame-point.mesh.f32') and got['derivation']['op'] == 'point'


def _r(S, det=False, cav=False, f4=False, meas=True):
    return {'label': 'x', 'measurable': meas, 'eligible': 16, 'S': S, 'p': 0.01 if det else 0.5, 'detected': det,
            'caveat': cav, 'ci95': None, 'lag1_autocorr_Q': 0.0, 'f4_violation': f4}


def test_signature_is_the_margin_on_d_and_does_not_need_a_detection():
    L = {(0.3, 1): _r(0.06, det=True), (0.3, 2): _r(0.03), (0.3, 3): _r(0.05, det=True), (0.3, 4): _r(0.01, cav=True, f4=True)}
    F = {(0.3, 1): _r(0.00), (0.3, 2): _r(-0.01), (0.3, 3): _r(0.02), (0.3, 4): _r(0.05)}
    per_run, cond, _ = decide.preference(L, F)
    assert per_run[(0.3, 1)]['signature'] == 'L'      # d = -0.06
    assert per_run[(0.3, 2)]['signature'] == 'L'      # d = -0.04, detected in neither frame: still signed
    assert per_run[(0.3, 3)]['signature'] == '-'      # d = -0.03: inside the margin
    assert per_run[(0.3, 4)]['signature'] == 'X'      # d = +0.04: caveat and F4 flags do not gate the frame test
    assert cond[0.3] == 'mixed'


def test_preference_needs_two_agreeing_conditions_and_no_dissent():
    def arm(signs):
        L, F = {}, {}
        for i, (sg, s) in enumerate(signs):
            if s == 'X':
                L[(sg, i)], F[(sg, i)] = _r(0.0), _r(0.06, det=True)
            elif s == 'L':
                L[(sg, i)], F[(sg, i)] = _r(0.06, det=True), _r(0.0)
            else:
                L[(sg, i)], F[(sg, i)] = _r(0.01), _r(0.01)
        return decide.preference(L, F)[2]
    assert arm([(0.3, 'X'), (0.32, 'X'), (0.35, '-')]) == 'X'
    assert arm([(0.3, 'X'), (0.32, 'X'), (0.35, 'L')]) == 'none'     # dissent
    assert arm([(0.3, 'L'), (0.32, 'L'), (0.35, 'L')]) == 'L'
    assert arm([(0.3, 'X'), (0.32, '-'), (0.35, '-')]) == 'none'     # one condition is not enough
    assert arm([(0.3, 'X'), (0.3, 'L'), (0.32, 'X'), (0.35, 'X')]) == 'none'   # a mixed condition


def test_an_unmeasured_run_is_never_read_as_a_signature():
    L = {(0.3, 1): _r(0.06, det=True), (0.32, 1): _r(0.06, det=True)}
    F = {(0.3, 1): _r(None, meas=False), (0.32, 1): _r(0.0)}
    per_run, cond, _ = decide.preference(L, F)
    assert per_run[(0.3, 1)]['signature'] == 'unmeasured' and cond[0.3] == 'none' and cond[0.32] == 'L'
