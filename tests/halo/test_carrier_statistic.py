"""Checks for experiments/halo/carrier_statistic.py, the within-run carrier statistic of Ring 32
(analysis/2026-09-24_within_run_carrier_statistic.md). Synthetic arrays only: the run meshes
are not in git, so the receipt on the control bytes is committed as a result, not recomputed here.

Pinned: the exact sign-flip p on vectors whose answer is known by counting; the frame identity
(inverting one member of a lag-one pair flips rho and nothing else; inverting both leaves it);
that the statistic of a run reads that run only; the call rule; and the decision's aggregation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import itertools
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
cs = pytest.importorskip('carrier_statistic')


def brute_p(x):
    x = np.asarray(x, dtype=float)
    obs = abs(x.sum())
    thr = obs - 1e-12 * np.abs(x).sum()
    hits = sum(abs(np.dot(s, x)) >= thr for s in itertools.product((1, -1), repeat=x.size))
    return hits / 2 ** x.size


@pytest.mark.parametrize('x', [[1, 1, 1], [0.3, -0.1, 0.2, 0.05, -0.4, 0.7, 0.01],
                               [0.2] * 12, list(np.linspace(-0.3, 0.5, 13))])
def test_signflip_p_matches_brute_force(x):
    assert cs.signflip_p(x) == brute_p(x)


def test_signflip_p_edge_cases():
    assert cs.signflip_p([1.0, -1.0]) == 1.0           # the sum is zero
    assert cs.signflip_p([0.5]) == 1.0                 # one pair: both signs reach |x|
    assert cs.signflip_p([0.2] * 12) == 2 / 4096       # the floor at the minimum 12 pairs
    assert math.isnan(cs.signflip_p([]))


@pytest.mark.parametrize('n', [9, 12, 50, 200, 900])
def test_binom_band_equals_the_frozen_band_where_that_one_works(n):
    assert cs.binom_band(n, 0.05) == cs.mq.binom_interval(n, 0.05)


def test_binom_band_does_not_overflow():
    lo, hi = cs.binom_band(2400, 0.05)
    assert 0 < lo < 120 < hi < 2400


def fake_run(seed, epochs=24):
    rng = np.random.default_rng(seed)
    base = rng.gamma(2.0, 1.0, size=(epochs, 32, 32, 32))
    # a lopsided blob that persists: gives every pair a point-odd part to correlate
    z, y, x = np.meshgrid(*(np.arange(32) - 15.5,) * 3, indexing='ij')
    blob = np.exp(-((y - 4) ** 2 + z ** 2 + x ** 2) / 20.0)
    return (base + 40 * blob[None]).astype('<f4')


def test_frame_identity_on_a_pair():
    m = fake_run(1)
    C, R = m[9], m[8]
    a = cs.pair_value(C, R)['rho']
    b = cs.pair_value(cs.invert_mesh(C), R)['rho']
    c = cs.pair_value(cs.invert_mesh(C), cs.invert_mesh(R))['rho']
    assert a > 0.1
    assert abs(a + b) < 1e-12 and abs(c - a) < 1e-12


def test_odd_part_ignores_the_support():
    m = fake_run(2)
    f = cs.mq.sub(m[5], cs.mq.B2)
    for mode, (s2, _) in cs.mq.build_supports().items():
        assert np.abs(cs.odd16(s2.residual(f)) - cs.odd16(f)).max() <= 1e-12 * np.abs(cs.odd16(f)).max()


def test_inverted_frame_flips_T_only():
    m = fake_run(3)
    s = cs.statistic(cs.run_pairs(m))
    sp = cs.statistic(cs.run_pairs(cs.mf.derive(m, 'point')))
    assert s['n'] == sp['n'] >= cs.MIN_PAIRS
    assert abs(s['T'] + sp['T']) < 1e-12 and abs(s['p'] - sp['p']) < 1e-12
    assert s['call'] == 'L' and sp['call'] == 'Pi'


def test_a_run_reads_itself_only():
    a, b = fake_run(4), fake_run(5)
    s1 = cs.statistic(cs.run_pairs(a))
    _ = cs.statistic(cs.run_pairs(b))
    s2 = cs.statistic(cs.run_pairs(a.copy()))
    assert s1['T'] == s2['T'] and s1['p'] == s2['p'] and s1['n'] == s2['n']


def test_call_rule():
    assert cs.call_of(0.1, 0.01, 12) == 'L'
    assert cs.call_of(-0.1, 0.01, 12) == 'Pi'
    assert cs.call_of(0.1, 0.05, 12) == 'none'
    assert cs.call_of(0.1, 0.01, 11) == 'unscored'


def test_aggregation():
    assert cs.condition_label(['Pi', 'none', 'unscored']) == 'Pi'
    assert cs.condition_label(['Pi', 'L', 'none']) == 'mixed'
    assert cs.condition_label(['none', 'none', 'none']) == 'none'
    assert cs.preference({'a': 'Pi', 'b': 'Pi', 'c': 'none'}) == 'Pi'
    assert cs.preference({'a': 'Pi', 'b': 'Pi', 'c': 'L'}) == 'none'
    assert cs.preference({'a': 'L', 'b': 'L', 'c': 'L'}) == 'L'
    assert cs.preference({'a': 'Pi', 'b': 'none', 'c': 'none'}) == 'none'



@pytest.mark.parametrize('seed', range(6))
def test_two_enumerations_agree(seed):
    x = np.random.default_rng(seed).normal(0.02, 0.1, size=12 + 2 * seed)
    assert cs.direct_p(x) == cs.signflip_p(x)


def _arm(calls):
    runs = [{'selfgrav': sg, 'call': c} for sg, c in zip([0.3] * 3 + [0.32] * 3 + [0.35] * 3, calls)]
    return cs.arm_summary(runs)


@pytest.mark.parametrize('ident, pos, branch', [
    (['L'] * 9, ['Pi'] * 9, 'CONFIRMED'),
    (['L'] * 9, ['Pi', 'none', 'none', 'Pi', 'none', 'none', 'Pi', 'Pi', 'none'], 'CONFIRMED'),
    (['L'] * 9, ['Pi', 'none', 'none', 'Pi', 'none', 'none', 'none', 'none', 'none'], 'LOW POWER'),
    (['L'] * 9, ['none'] * 9, 'SILENT'),
    (['L'] * 9, ['Pi'] * 8 + ['L'], 'CONTRARY'),
    (['L'] * 9, ['none'] * 8 + ['L'], 'CONTRARY'),
    (['none'] * 9, ['Pi'] * 9, 'BASELINE SILENT'),
    (['L'] * 9, ['L'] * 9, 'BROKEN'),
    (['L'] * 9, ['Pi'] * 7 + ['L', 'L'], 'BROKEN'),
    (['Pi'] * 9, ['Pi'] * 9, 'BROKEN'),
    (['L'] * 7 + ['Pi', 'Pi'], ['Pi'] * 9, 'BROKEN'),
    (['L'] * 9, ['Pi'] * 6 + ['unscored'] * 2 + ['Pi'], 'UNMEASURED'),
])
def test_branches(ident, pos, branch):
    assert cs.classify(_arm(ident), _arm(pos))[0] == branch


def test_void_rule(tmp_path):
    import json
    d = tmp_path / 'arm'
    d.mkdir()
    (d / 'a.json').write_text('{}')
    (d / 'a.void-1.json').write_text(json.dumps({'kind': 'crash', 'pageerrors': []}))
    (d / 'b.void-1.json').write_text(json.dumps({'kind': 'refused', 'pageerrors': []}))
    assert cs.v1_voids(str(d)) == ([], 1)
    (d / 'c.void-1.json').write_text(json.dumps({'kind': 'receipt', 'pageerrors': []}))
    bad, n = cs.v1_voids(str(d))
    assert n == 2 and len(bad) == 2       # a receipt void is not re-issuable, and c was never re-issued


def test_pinning_sees_a_lab_template_and_not_random_runs():
    runs = [fake_run(10 + i) for i in range(5)]
    free = cs.pinning([r if i % 2 else np.stack([cs.invert_mesh(m) for m in r]) for i, r in enumerate(runs)])
    assert free['patterns'] == 32
    z, y, x = np.meshgrid(*(np.arange(32) - 15.5,) * 3, indexing='ij')
    tmpl = np.exp(-((x - 5) ** 2 + (y - 3) ** 2 + z ** 2) / 10.0)
    pinned = cs.pinning([np.stack([cs.invert_mesh(m) if i % 2 else m for m in r]) + 200 * tmpl[None] for i, r in enumerate(runs)])
    assert pinned['G_mean_cosine'] > 0.5 and pinned['p_one_sided_exact'] == 2 / 32   # s and -s give the same G


def test_registered_seeds_are_nine_distinct_square_root_digits():
    seeds = [s for v in cs.REGISTERED.values() for s in v]
    later = [s for v in cs.DECIDED_ARM_SEEDS.values() for s in v]
    assert len(set(seeds + later)) == 18
    nonsq = [n for n in range(2, 30) if int(math.isqrt(n)) ** 2 != n][:18]
    digits = [int(f'{math.sqrt(n):.10f}'.replace('.', '')[:5]) for n in nonsq]
    assert seeds + later == digits


# ---- enforcement code (added after the kill-test's mutants survived the first suite)

def test_crash_void_with_page_errors_is_flagged(tmp_path):
    import json
    (tmp_path / 'a.json').write_text('{}')
    (tmp_path / 'a.void-1.json').write_text(json.dumps({'kind': 'crash', 'pageerrors': ['boom']}))
    bad, n = cs.v1_voids(str(tmp_path))
    assert n == 1 and bad


@pytest.mark.parametrize('k, branch', [(3, 'LOW POWER'), (4, 'CONFIRMED'), (2, 'LOW POWER')])
def test_licence_boundary(k, branch):
    # k Pi calls spread over the three conditions, the rest none
    pos = ['none'] * 9
    for i in range(k):
        pos[(i % 3) * 3 + i // 3] = 'Pi'
    assert cs.classify(_arm(['L'] * 9), _arm(pos))[0] == branch


def test_static_run_is_its_own_branch():
    assert cs.classify(_arm(['L'] * 9), _arm(['Pi'] * 9), static_runs=1)[0] == 'STATIC'


def test_mask_excludes_and_must_match():
    pairs = cs.run_pairs(fake_run(6))
    full = cs.statistic(pairs)
    mask = list(full['eligible_mask'])
    first = mask.index(True)
    mask[first] = False
    part = cs.statistic(pairs, mask=mask)
    assert part['n'] == full['n'] - 1
    with pytest.raises(ValueError):
        cs.statistic(pairs, mask=mask[:5])


def test_own_field_gates():
    m = fake_run(7).astype(np.float64)
    cur = np.zeros_like(m[5])
    cur[0, 0, 0] = 1e6                              # all the mass outside the inner block
    cur[10, 10, 10] = 1.0
    assert cs.pair_value(cur, m[4])['e1'] is False
    cur2 = np.array(m[5])
    cur2[8:24, 8:24, 8:24] = 1.0                   # a flat inner block: its point-odd part is empty
    cur2[20, 20, 20] = 50.0                        # except one cell and its mirror
    v = cs.pair_value(cur2, m[4])
    assert v['e2odd'] is False and v['eligible'] is False


def _receipt(tmp_path, **over):
    import json
    import platform as pf
    r = {'schema': cs.SCHEMA_RECEIPT, 'receipt_passed': True, 'script_sha256': cs.script_sha256(),
         'design_commit': 'x', 'runtime': {'python': pf.python_version(), 'numpy': np.__version__},
         'frozen_scorer_sha256': cs.sha256_file(os.path.join(cs.HERE, 'memory_estimator_qualify.py')),
         'frames_script_sha256': cs.sha256_file(os.path.join(cs.HERE, 'memory_intervention_frames.py')),
         'gates_script_sha256': cs.sha256_file(os.path.join(cs.HERE, 'memory_intervention_gates.py'))}
    for g in ('G1_exactness', 'G2_null_end_to_end', 'G2b_exact_p', 'G3_one_run_in', 'G4_recovery'):
        r[g] = {'pass': True}
    r.update(over)
    p = tmp_path / 'receipt.json'
    p.write_text(json.dumps(r))
    return str(p)


def test_check_receipt_refusals(tmp_path, monkeypatch):
    monkeypatch.setattr(cs, 'committed_same', lambda c, rel: True)
    cs.check_receipt(_receipt(tmp_path))                                   # the good one passes
    for over in ({'G4_recovery': {'pass': False}}, {'script_sha256': '0' * 64},
                 {'frozen_scorer_sha256': '0' * 64}, {'gates_script_sha256': '0' * 64},
                 {'runtime': {'python': '0', 'numpy': '0'}}, {'receipt_passed': False}):
        with pytest.raises(SystemExit):
            cs.check_receipt(_receipt(tmp_path, **over))
    monkeypatch.setattr(cs, 'committed_same', lambda c, rel: False)
    with pytest.raises(SystemExit):
        cs.check_receipt(_receipt(tmp_path))


def test_runtime_pins():
    good = {'instrument': dict(cs.RUNTIME_PINS), 'applied': {'caps': {'renderer': cs.RENDERER}}}
    assert cs.runtime_faults(good) == []
    bad = {'instrument': dict(cs.RUNTIME_PINS, browser='150'), 'applied': {'caps': {'renderer': 'SwiftShader'}}}
    assert len(cs.runtime_faults(bad)) == 2


def _fake_dir(root, name, pairs):
    import json
    d = root / cs.DIRS[name]
    d.mkdir(parents=True)
    for sg, seed in pairs:
        tag = f'spinchladni_sg{sg:g}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_iv{name if name in ("identity", "invert_all") else "identity"}'
        fake_run(seed % 1000).tofile(d / f'{tag}.mesh.f32')
        (d / f'{tag}.json').write_text(json.dumps({
            'schema': 'halo-memory-prereg/1', 'tag': tag, 'mesh_file': f'{tag}.mesh.f32', 'mesh_count': 24,
            'params': {'preset': 'spinchladni', 'selfgrav': sg, 'gainloss': 0, 'seed': seed, 'particles': 4194304}}))
    return d


def test_score_refuses_before_the_checks_and_on_the_wrong_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(cs, 'committed_same', lambda c, rel: True)
    rp = _receipt(tmp_path)
    nine = [(sg, s) for sg, seeds in cs.REGISTERED.items() for s in seeds]
    root = tmp_path / 'halo'
    d = _fake_dir(root, 'identity', nine)
    with pytest.raises(SystemExit):                  # no canary and no closing repeat yet
        cs.score(str(d), 'identity', rp, str(tmp_path / 's.json'))
    _fake_dir(root, 'canary', [cs.CANARY[:2]])
    _fake_dir(root, 'close', [cs.CLOSING])
    out = cs.score(str(d), 'identity', rp, str(tmp_path / 's.json'))
    assert len(out['runs']) == 9 and all(r['frame_identity_holds'] for r in out['runs'])
    d2 = _fake_dir(tmp_path / 'other', 'identity', nine[:8] + [(0.35, 99999)])
    _fake_dir(tmp_path / 'other', 'canary', [cs.CANARY[:2]])
    _fake_dir(tmp_path / 'other', 'close', [cs.CLOSING])
    with pytest.raises(SystemExit):                  # a seed that is not registered
        cs.score(str(d2), 'identity', rp, str(tmp_path / 's2.json'))


def test_ledger_counts_refused_launches_as_no_run(tmp_path, monkeypatch):
    import json
    d = tmp_path / 'arm'
    d.mkdir()
    led = tmp_path / 'ledger.tsv'
    monkeypatch.setattr(cs, 'LEDGER_REL', str(led))
    row = lambda i: f'2026-09-24T00:00:0{i}+00:00\t{d}\ttagA\t{i}\tabc\n'
    led.write_text(row(1) + row(2) + row(3))
    (d / 'tagA.void-1.json').write_text(json.dumps({'kind': 'refused'}))
    (d / 'tagA.void-2.json').write_text(json.dumps({'kind': 'crash', 'pageerrors': []}))
    assert cs.ledger_faults(str(tmp_path)) == []     # 3 launches, 1 refused: 2 counted, after a crash
    led.write_text(row(1) + row(2) + row(3) + row(4))
    assert cs.ledger_faults(str(tmp_path))           # 3 counted launches
