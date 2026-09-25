"""Tests for experiments/halo/carrier_decided_arm.py (Ring 34: the decided arm, invert_matter, under
Ring 32's within-run carrier statistic and rule).

The end-to-end tests build a complete registered tree of synthetic runs (records from committed
templates, synthetic meshes) and plant one fault at a time; each must turn V1 to a failure. The
replay tests (skipped where the gitignored Ring 32 meshes are absent) run this module's decide on
a copy of Ring 32's recorded tree: untouched it must return Ring 33's counts, and every fault that
Ring 33's breaker named, planted in the copy, must be caught here and is missed by Ring 32's decide.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import glob
import itertools
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'experiments', 'halo'))
import carrier_decided_arm as da      # noqa: E402
import carrier_statistic as cs        # noqa: E402

HALO = os.path.join(REPO, 'data', 'results', 'halo')
R_FULL = da.RECEIPT_COMMIT
DESIGN_1E28 = subprocess.run(['git', '-C', REPO, 'rev-parse', '1e2810a5'], capture_output=True, text=True).stdout.strip()


def head():
    return subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()


def fake_run(seed, epochs=24):
    rng = np.random.default_rng(seed)
    base = rng.gamma(2.0, 1.0, size=(epochs, 32, 32, 32))
    z, y, x = np.meshgrid(*(np.arange(32) - 15.5,) * 3, indexing='ij')
    blob = np.exp(-((y - 4) ** 2 + z ** 2 + x ** 2) / 20.0)
    return (base + 40 * blob[None]).astype('<f4')


def template(mode):
    pat = {'identity': 'memory_carrier_identity/*ividentity.json',
           'invert_matter': 'memory_intervention_invert_matter/*ivinvert_matter.json'}[mode]
    with open(sorted(glob.glob(os.path.join(HALO, pat)))[0]) as fh:
        return json.load(fh)


# ------------------------------------------------------------------ registry and table

def test_registered_runs_order_and_seeds():
    reg = da.registered()
    assert len(reg) == 20
    assert reg[0][:3] == ('canary', 'memory_decided_canary', 'identity') and reg[0][3:] == (0.32, 777)
    assert reg[-1] == ('close', 'memory_decided_close', 'invert_matter', 0.3, 36055)
    body = reg[1:-1]
    assert [r[0] for r in body] == ['identity', 'invert_matter'] * 9
    assert [(r[3], r[4]) for r in body[::2]] == [(r[3], r[4]) for r in body[1::2]] == da.pairs()
    assert da.pairs() == [(0.3, 36055), (0.3, 37416), (0.3, 38729), (0.32, 41231), (0.32, 42426),
                          (0.32, 43588), (0.35, 44721), (0.35, 45825), (0.35, 46904)]
    fresh = {s for _, s in da.pairs()}
    assert len(fresh) == 9 and not fresh & {s for seeds in cs.REGISTERED.values() for s in seeds}
    assert (da.CLOSING[1], da.CLOSING[2]) == da.pairs()[0] and da.CLOSING[0] == da.DECIDED
    assert da.CANARY[3] == 'ce15f08155e34fff22c234a802ef1784549c8bf3e6af1e282d72beb946e34177'
    assert da.LICENSE_MIN == 4 and len(set(da.DIRS.values())) == 4


def _arm(calls):
    conds = {f'sg{sg:g}': cs.condition_label(calls[3 * i:3 * i + 3]) for i, sg in enumerate(da.SEEDS)}
    return {'conditions': conds,
            'scored_per_condition': {f'sg{sg:g}': sum(c != 'unscored' for c in calls[3 * i:3 * i + 3])
                                     for i, sg in enumerate(da.SEEDS)},
            'preference': cs.preference(conds),
            'call_counts': {c: calls.count(c) for c in ('L', 'Pi', 'none', 'unscored')}}


IDENT_OK = ['L', 'none', 'none', 'L', 'none', 'none', 'none', 'none', 'none']


@pytest.mark.parametrize('ident,dec,branch', [
    (IDENT_OK, ['Pi'] * 4 + ['none'] * 5, 'FOLLOWS THE MATTER'),
    (IDENT_OK, ['Pi', 'none', 'none', 'Pi', 'none', 'none', 'none'] + ['none'] * 2, 'FEW CALLS'),
    (IDENT_OK, ['L', 'L', 'none', 'L', 'none', 'none', 'L', 'none', 'none'], 'STAYS IN THE LAB FRAME'),
    (IDENT_OK, ['L', 'none', 'none', 'L', 'none', 'none', 'none', 'none', 'none'], 'FEW CALLS'),
    (IDENT_OK, ['L', 'Pi', 'none', 'none', 'none', 'none', 'none', 'none', 'none'], 'SPLIT'),
    (IDENT_OK, ['Pi', 'Pi', 'Pi', 'Pi', 'none', 'none', 'L', 'none', 'none'], 'SPLIT'),
    (IDENT_OK, ['Pi', 'Pi', 'Pi', 'none', 'none', 'none', 'none', 'none', 'none'], 'NO PREFERENCE'),
    (IDENT_OK, ['none'] * 9, 'NO PREFERENCE'),
    (['Pi', 'none', 'none', 'L', 'none', 'none', 'L', 'none', 'none'], ['Pi'] * 9, 'BASELINE SILENT'),
    (['Pi', 'Pi', 'none', 'L', 'L', 'none', 'L', 'none', 'none'], ['Pi'] * 9, 'BROKEN'),
    (['none'] * 9, ['Pi'] * 9, 'BASELINE SILENT'),
    (['unscored', 'unscored', 'L'] + ['L'] * 6, ['Pi'] * 9, 'UNMEASURED'),
    (IDENT_OK, ['unscored', 'unscored', 'Pi'] + ['Pi'] * 6, 'UNMEASURED'),
])
def test_branch_table(ident, dec, branch):
    assert da.classify(_arm(ident), _arm(dec))[0] == branch


def test_static_comes_first():
    assert da.classify(_arm(IDENT_OK), _arm(['Pi'] * 9), static_runs=1)[0] == 'STATIC'


def test_decided_table_is_a_partition_and_agrees_with_classify():
    seen = {}
    for calls in itertools.product(('Pi', 'L', 'none'), repeat=9):
        calls = list(calls)
        b = da.decided_outcome(calls)
        assert b == da.classify(_arm(IDENT_OK), _arm(calls))[0]
        seen[b] = seen.get(b, 0) + 1
    assert sum(seen.values()) == 3 ** 9
    assert set(seen) == {'FOLLOWS THE MATTER', 'STAYS IN THE LAB FRAME', 'FEW CALLS', 'SPLIT', 'NO PREFERENCE'}
    assert seen['FOLLOWS THE MATTER'] == seen['STAYS IN THE LAB FRAME']      # the table is symmetric


def test_plan_rows_sum_to_one():
    for row in da.plan():
        tot = sum(v for k, v in row.items() if k not in ('q', 'w'))
        assert abs(tot - 1.0) < 1e-3
    row = da.plan(rates=((5, 9),), contrary=(0.0,))[0]
    assert row['toward (q direction, >= 4 calls)'] == 0.8426 and row['NO PREFERENCE'] == 0.0218


def test_bound_to_refuses_other_bytes(monkeypatch):
    monkeypatch.setattr(cs, 'committed_same', lambda c, rel: False)
    with pytest.raises(SystemExit):
        da.bound_to('HEAD')
    with pytest.raises(SystemExit):
        da.bound_to('not-a-commit')


def test_bound_to_refuses_a_commit_before_R(monkeypatch):
    monkeypatch.setattr(cs, 'committed_same', lambda c, rel: True)
    with pytest.raises(SystemExit):
        da.bound_to(DESIGN_1E28)
    assert da.bound_to('HEAD') == head()


# ------------------------------------------------------------------ synthetic end to end

TEMPLATES = {}


def write_run(d, iv, sg, seed, mesh, rev):
    tag = da.tag_of(iv, sg, seed)
    if iv not in TEMPLATES:
        TEMPLATES[iv] = template(iv)
    rec = json.loads(json.dumps(TEMPLATES[iv]))
    rec['tag'], rec['mesh_file'] = tag, tag + '.mesh.f32'
    rec['params']['seed'], rec['params']['selfgrav'] = seed, sg
    rec['applied']['cosmos']['selfgrav'] = sg
    rec['instrument']['git_rev'] = rev
    os.makedirs(d, exist_ok=True)
    np.ascontiguousarray(mesh, dtype='<f4').tofile(os.path.join(d, tag + '.mesh.f32'))
    with open(os.path.join(d, tag + '.json'), 'w') as fh:
        json.dump(rec, fh)
    return tag


def build_tree(base, monkeypatch):
    """a complete registered tree of synthetic runs, its ledger and both score files."""
    rev = head()
    root = os.path.join(base, 'halo')
    firsts = {}
    for name, d, iv, sg, s in da.registered():
        if name == 'close':
            src = os.path.join(root, da.DIRS[iv], da.tag_of(iv, sg, s) + '.mesh.f32')
            mesh = np.fromfile(src, dtype='<f4').reshape(24, 32, 32, 32)
        elif name == 'canary':
            mesh = fake_run(777)
        else:
            mesh = fake_run(s * 3 + (name == da.DECIDED))
            mesh[0] = firsts.setdefault((sg, s), fake_run(s)[0])
        write_run(os.path.join(root, d), iv, sg, s, mesh, rev)
    canary = os.path.join(root, da.DIRS['canary'], da.tag_of('identity', 0.32, 777) + '.mesh.f32')
    ledger = os.path.join(base, 'launches.tsv')
    with open(ledger, 'w') as fh:
        for j, (name, d, iv, sg, s) in enumerate(da.registered()):
            fh.write(f'2026-09-24T00:{j:02d}:00+00:00\t{os.path.join(root, d)}\t{da.tag_of(iv, sg, s)}\t1\t{rev}\n')
    patch(monkeypatch, ledger, cs.sha256_file(canary))
    scores = {}
    for arm in da.ARMS:
        scores[arm] = os.path.join(base, f'score_{arm}.json')
        da.score(os.path.join(root, da.DIRS[arm]), arm, 'HEAD', scores[arm])
    return root, ledger, scores


def patch(monkeypatch, ledger, canary_sha):
    monkeypatch.setattr(da, 'LEDGER_REL', ledger)
    monkeypatch.setattr(da, 'bound_to', lambda p: head())
    monkeypatch.setattr(da, 'CANARY', ('identity', 0.32, 777, canary_sha))
    monkeypatch.setattr(cs, 'check_receipt', lambda p: {})


def decide(root, scores, out):
    return da.decide([(a, scores[a]) for a in da.ARMS], 'HEAD', out, root=root)


@pytest.fixture(scope='module')
def clean_tree(tmp_path_factory):
    base = str(tmp_path_factory.mktemp('decided'))
    mp = pytest.MonkeyPatch()
    try:
        root, ledger, scores = build_tree(base, mp)
        canary_sha = da.CANARY[3]
    finally:
        mp.undo()
    return base, root, ledger, scores, canary_sha


def fresh_copy(clean_tree, tmp_path, monkeypatch):
    base, root, ledger, scores, canary_sha = clean_tree
    nb = str(tmp_path / 'copy')
    shutil.copytree(base, nb)
    nroot = os.path.join(nb, 'halo')
    nledger = os.path.join(nb, 'launches.tsv')
    with open(nledger) as fh:
        txt = fh.read().replace(root, nroot)
    with open(nledger, 'w') as fh:
        fh.write(txt)
    patch(monkeypatch, nledger, canary_sha)
    return nroot, nledger, {a: os.path.join(nb, os.path.basename(p)) for a, p in scores.items()}


def test_clean_synthetic_tree_passes_V1(clean_tree, tmp_path, monkeypatch):
    root, ledger, scores = fresh_copy(clean_tree, tmp_path, monkeypatch)
    out = decide(root, scores, str(tmp_path / 'd.json'))
    assert out['V1_instrument']['failures'] == [] and out['branch'] in da.BRANCHES and out['branch'] != 'VOID'


def _rows(ledger):
    with open(ledger) as fh:
        return [l for l in fh if l.strip()]


def _put(ledger, rows):
    with open(ledger, 'w') as fh:
        fh.writelines(rows)


def _first(root, arm='identity'):
    sg, s = da.pairs()[0]
    return os.path.join(root, da.DIRS[arm]), da.tag_of(arm, sg, s)


def plant(fault, root, ledger, scores):
    d, tag = _first(root)
    if fault == 'duplicate seed under another tag':
        other = tag.replace('fieldExp1.7', 'fieldExp2')
        rec = json.load(open(os.path.join(d, tag + '.json')))
        rec['tag'], rec['mesh_file'] = other, other + '.mesh.f32'
        json.dump(rec, open(os.path.join(d, other + '.json'), 'w'))
        shutil.copy(os.path.join(d, tag + '.mesh.f32'), os.path.join(d, other + '.mesh.f32'))
    elif fault == 'second copy of a record':
        shutil.copy(os.path.join(d, tag + '.json'), os.path.join(d, tag + '.copy.json'))
    elif fault == 'kept-aside attempt with one launch':
        shutil.copy(os.path.join(d, tag + '.mesh.f32'), os.path.join(d, tag + '.attempt1.mesh.f32.partial'))
    elif fault == 'partial beside a record':
        shutil.copy(os.path.join(d, tag + '.mesh.f32'), os.path.join(d, tag + '.mesh.f32.partial'))
    elif fault == 'ledger commit not after P':
        rows = _rows(ledger)
        rows[3] = rows[3].rsplit('\t', 1)[0] + '\t' + DESIGN_1E28 + '\n'
        _put(ledger, rows)
    elif fault == 'run with no ledger row':
        _put(ledger, _rows(ledger)[:5] + _rows(ledger)[6:])
    elif fault == 'ledger row for an unregistered run':
        rows = _rows(ledger)
        _put(ledger, rows + [rows[1].replace('seed36055', 'seed99999')])
    elif fault == 'attempt numbered 2 without 1':
        rows = _rows(ledger)
        f = rows[4].split('\t')
        f[3] = '2'
        rows[4] = '\t'.join(f)
        _put(ledger, rows)
    elif fault == 'first launches out of order':
        rows = _rows(ledger)
        rows[2], rows[3] = rows[3], rows[2]
        _put(ledger, rows)
    elif fault == 'record seed not its tag':
        rec = json.load(open(os.path.join(d, tag + '.json')))
        rec['params']['seed'] = 36056
        json.dump(rec, open(os.path.join(d, tag + '.json'), 'w'))
    elif fault == 'score missing a run':
        sc = json.load(open(scores['identity']))
        sc['runs'] = sc['runs'][1:]
        json.dump(sc, open(scores['identity'], 'w'))
    elif fault == 'score call edited':
        sc = json.load(open(scores[da.DECIDED]))
        sc['runs'][0]['call'] = 'Pi' if sc['runs'][0]['call'] != 'Pi' else 'L'
        json.dump(sc, open(scores[da.DECIDED], 'w'))
    elif fault == 'closing repeat differs':
        iv, sg, s = da.CLOSING
        p = os.path.join(root, da.DIRS['close'], da.tag_of(iv, sg, s) + '.mesh.f32')
        m = np.fromfile(p, dtype='<f4')
        m[-1] += 1.0
        m.tofile(p)
    elif fault == 'canary differs':
        p = os.path.join(root, da.DIRS['canary'], da.tag_of('identity', 0.32, 777) + '.mesh.f32')
        m = np.fromfile(p, dtype='<f4')
        m[-1] += 1.0
        m.tofile(p)
    elif fault == 'first mesh differs between arms':
        dd, t2 = _first(root, da.DECIDED)
        p = os.path.join(dd, t2 + '.mesh.f32')
        m = np.fromfile(p, dtype='<f4')
        m[0] += 1.0
        m.tofile(p)
        sc = json.load(open(scores[da.DECIDED]))
        for r in sc['runs']:
            if r['tag'] == t2:
                r['mesh_sha256'] = cs.sha256_file(p)
        json.dump(sc, open(scores[da.DECIDED], 'w'))
    elif fault == 'crash void with no launch row of its own':
        json.dump({'kind': 'crash', 'pageerrors': []}, open(os.path.join(d, tag + '.void-1.json'), 'w'))
    elif fault == 'void of an unregistered run':
        other = tag.replace('seed36055', 'seed99999')
        json.dump({'kind': 'refused', 'pageerrors': []}, open(os.path.join(d, other + '.void-1.json'), 'w'))
    elif fault == 'record git_rev symbolic':
        rec = json.load(open(os.path.join(d, tag + '.json')))
        rec['instrument']['git_rev'] = 'HEAD'
        json.dump(rec, open(os.path.join(d, tag + '.json'), 'w'))
    elif fault == 'ledger commit symbolic':
        rows = _rows(ledger)
        rows[3] = rows[3].rsplit('\t', 1)[0] + '\tHEAD\n'
        _put(ledger, rows)
    elif fault == 'void of kind receipt':
        json.dump({'kind': 'receipt', 'pageerrors': []}, open(os.path.join(d, tag + '.void-1.json'), 'w'))
    else:
        raise KeyError(fault)


FAULTS = ['duplicate seed under another tag', 'second copy of a record', 'kept-aside attempt with one launch',
          'partial beside a record', 'ledger commit not after P', 'run with no ledger row',
          'ledger row for an unregistered run', 'attempt numbered 2 without 1', 'first launches out of order',
          'record seed not its tag', 'score missing a run', 'score call edited', 'closing repeat differs',
          'canary differs', 'first mesh differs between arms', 'void of kind receipt',
          'crash void with no launch row of its own', 'void of an unregistered run',
          'record git_rev symbolic', 'ledger commit symbolic']


@pytest.mark.parametrize('fault', FAULTS)
def test_every_planted_fault_fails_V1(fault, clean_tree, tmp_path, monkeypatch):
    root, ledger, scores = fresh_copy(clean_tree, tmp_path, monkeypatch)
    plant(fault, root, ledger, scores)
    out = decide(root, scores, str(tmp_path / 'd.json'))
    assert out['branch'] == 'VOID' and out['V1_instrument']['failures'], fault


def test_score_refuses_a_duplicate_and_a_missing_check(clean_tree, tmp_path, monkeypatch):
    root, ledger, scores = fresh_copy(clean_tree, tmp_path, monkeypatch)
    plant('duplicate seed under another tag', root, ledger, scores)
    with pytest.raises(SystemExit):
        da.score(os.path.join(root, da.DIRS['identity']), 'identity', 'HEAD', str(tmp_path / 's.json'))
    root2, _, _ = fresh_copy(clean_tree, tmp_path / 'b', monkeypatch)
    iv, sg, s = da.CLOSING
    os.remove(os.path.join(root2, da.DIRS['close'], da.tag_of(iv, sg, s) + '.json'))
    with pytest.raises(SystemExit):
        da.score(os.path.join(root2, da.DIRS[da.DECIDED]), da.DECIDED, 'HEAD', str(tmp_path / 's2.json'))


def test_a_run_with_no_eligible_pair_is_unscored_not_void(clean_tree, tmp_path, monkeypatch):
    """a run whose meshes after the first are empty has no eligible pair: its T is NaN, which the
    score file writes as null, and V1 must still pass (an exact comparison would VOID the batch)."""
    root, ledger, scores = fresh_copy(clean_tree, tmp_path, monkeypatch)
    sg, s = da.pairs()[1]
    p = os.path.join(root, da.DIRS[da.DECIDED], da.tag_of(da.DECIDED, sg, s) + '.mesh.f32')
    m = np.fromfile(p, dtype='<f4').reshape(24, 32, 32, 32)
    m[1:] = 0.0
    m.tofile(p)
    da.score(os.path.join(root, da.DIRS[da.DECIDED]), da.DECIDED, 'HEAD', scores[da.DECIDED])
    row = [r for r in json.load(open(scores[da.DECIDED]))['runs'] if r['seed'] == s][0]
    assert row['n'] == 0 and row['T'] is None and row['call'] == 'unscored'
    out = decide(root, scores, str(tmp_path / 'd.json'))
    assert out['V1_instrument']['failures'] == [] and out['arms'][da.DECIDED]['call_counts']['unscored'] == 1


def test_a_reissued_run_passes(clean_tree, tmp_path, monkeypatch):
    """a crash void re-issued once, and a kept-aside first attempt with its second launch, both pass."""
    root, ledger, scores = fresh_copy(clean_tree, tmp_path, monkeypatch)
    rows = _rows(ledger)
    d, tag = _first(root)
    json.dump({'kind': 'crash', 'pageerrors': []}, open(os.path.join(d, tag + '.void-1.json'), 'w'))
    r2 = rows[1].split('\t')
    r2[3] = '2'
    rows.insert(2, '\t'.join(r2))
    dd, t2 = _first(root, da.DECIDED)
    shutil.copy(os.path.join(dd, t2 + '.mesh.f32'), os.path.join(dd, t2 + '.attempt1.mesh.f32.partial'))
    r3 = rows[3].split('\t')
    r3[3] = '2'
    rows.insert(4, '\t'.join(r3))
    _put(ledger, rows)
    out = decide(root, scores, str(tmp_path / 'd.json'))
    assert out['V1_instrument']['failures'] == []


# ------------------------------------------------------------------ replay on Ring 32's recorded tree

RING32 = [os.path.join(HALO, v) for v in cs.DIRS.values()]
HAVE_MESHES = all(os.path.isdir(d) and len(glob.glob(os.path.join(d, '*.mesh.f32'))) >= 1 for d in RING32) and \
    len(glob.glob(os.path.join(HALO, 'memory_carrier_identity', '*.mesh.f32'))) == 9
needs_ring32 = pytest.mark.skipif(not HAVE_MESHES, reason='the gitignored Ring 32 meshes are not on this machine')

REPLAY_FAULTS = ['duplicate seed under another tag', 'kept-aside attempt with one launch', 'ledger commit not after P',
                 'run with no ledger row', 'ledger row for an unregistered run', 'attempt numbered 2 without 1',
                 'first launches out of order']


def ring32_copy(base, monkeypatch):
    root = os.path.join(base, 'halo')
    for name, sub in cs.DIRS.items():
        src, dst = os.path.join(HALO, sub), os.path.join(root, sub)
        os.makedirs(dst)
        for fn in os.listdir(src):
            if fn.startswith('spinchladni_') and fn.endswith('.json'):
                shutil.copy(os.path.join(src, fn), dst)
            elif fn.endswith('.mesh.f32'):
                os.symlink(os.path.join(src, fn), os.path.join(dst, fn))
    ledger = os.path.join(base, 'launches.tsv')
    with open(os.path.join(REPO, cs.LEDGER_REL)) as fh:
        txt = fh.read().replace('data/results/halo/', root + '/')
    with open(ledger, 'w') as fh:
        fh.write(txt)
    monkeypatch.setattr(da, 'SEEDS', dict(cs.REGISTERED))
    monkeypatch.setattr(da, 'DECIDED', 'invert_all')
    monkeypatch.setattr(da, 'ARMS', ('identity', 'invert_all'))
    monkeypatch.setattr(da, 'DIRS', dict(cs.DIRS))
    monkeypatch.setattr(da, 'CLOSING', ('identity', 0.3, 14142))
    monkeypatch.setattr(da, 'LEDGER_REL', ledger)
    monkeypatch.setattr(da, 'bound_to', lambda p: R_FULL)
    monkeypatch.setattr(cs, 'LEDGER_REL', ledger)
    old = {a: os.path.join(HALO, 'memory_carrier_scores', f'{a}.json') for a in ('identity', 'invert_all')}
    new = {}
    for a in ('identity', 'invert_all'):
        new[a] = os.path.join(base, f'new_{a}.json')
        da.score(os.path.join(root, cs.DIRS[a]), a, R_FULL, new[a])
    return root, ledger, old, new


def old_decide(root, old, out):
    return cs.decide([(a, old[a]) for a in ('identity', 'invert_all')], R_FULL, out, root=root)


def new_decide(root, new, out):
    return da.decide([(a, new[a]) for a in ('identity', 'invert_all')], R_FULL, out, root=root)


@needs_ring32
def test_replay_returns_ring33s_counts(tmp_path, monkeypatch):
    root, ledger, old, new = ring32_copy(str(tmp_path), monkeypatch)
    o = old_decide(root, old, str(tmp_path / 'old.json'))
    n = new_decide(root, new, str(tmp_path / 'new.json'))
    assert o['branch'] == 'CONFIRMED' and o['V1_instrument']['pass']
    assert n['V1_instrument']['failures'] == []
    assert (n['identity_L_calls'], n['identity_Pi_calls'], n['decided_Pi_calls'], n['decided_L_calls']) == (6, 0, 5, 0)
    assert n['arms']['invert_all']['preference'] == 'Pi' and n['branch'] == 'FOLLOWS THE MATTER'


@needs_ring32
@pytest.mark.parametrize('fault', REPLAY_FAULTS)
def test_replay_faults_ring32_decide_misses_and_this_one_catches(fault, tmp_path, monkeypatch):
    root, ledger, old, new = ring32_copy(str(tmp_path), monkeypatch)
    if fault == 'duplicate seed under another tag':
        d = os.path.join(root, cs.DIRS['identity'])
        tag = 'spinchladni_sg0.3_gl0_seed14142_n4194304_e24_fieldExp1.7_ividentity'
        other = tag.replace('fieldExp1.7', 'fieldExp2')
        rec = json.load(open(os.path.join(d, tag + '.json')))
        rec['tag'], rec['mesh_file'] = other, other + '.mesh.f32'
        json.dump(rec, open(os.path.join(d, other + '.json'), 'w'))
        os.symlink(os.path.realpath(os.path.join(d, tag + '.mesh.f32')), os.path.join(d, other + '.mesh.f32'))
    elif fault == 'kept-aside attempt with one launch':
        d = os.path.join(root, cs.DIRS['identity'])
        tag = 'spinchladni_sg0.3_gl0_seed14142_n4194304_e24_fieldExp1.7_ividentity'
        os.symlink(os.path.realpath(os.path.join(d, tag + '.mesh.f32')),
                   os.path.join(d, tag + '.attempt1.mesh.f32.partial'))
    else:
        rows = _rows(ledger)
        if fault == 'ledger commit not after P':
            rows[3] = rows[3].rsplit('\t', 1)[0] + '\t' + DESIGN_1E28 + '\n'
        elif fault == 'run with no ledger row':
            rows = rows[:5] + rows[6:]
        elif fault == 'ledger row for an unregistered run':
            rows = rows + [rows[1].replace('seed14142', 'seed99999')]
        elif fault == 'attempt numbered 2 without 1':
            f = rows[4].split('\t')
            f[3] = '2'
            rows[4] = '\t'.join(f)
        elif fault == 'first launches out of order':
            rows[2], rows[3] = rows[3], rows[2]
        _put(ledger, rows)
    o = old_decide(root, old, str(tmp_path / 'old.json'))
    n = new_decide(root, new, str(tmp_path / 'new.json'))
    assert o['V1_instrument']['pass'] and o['branch'] == 'CONFIRMED', f'Ring 32 decide caught {fault}'
    assert n['branch'] == 'VOID' and n['V1_instrument']['failures'], f'this decide missed {fault}'
