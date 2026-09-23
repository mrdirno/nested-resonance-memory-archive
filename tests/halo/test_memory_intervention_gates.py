"""Checks for experiments/halo/memory_intervention_gates.py, the Ring 30 gates V1-V5 and branch.

The per-boundary receipts must fail on a lost write, a potential moved in the wrong arm, a
wrong flip count, a density receipt past its bound and a tick that consumed something else;
the per-run comparison must see numbers and ignore names; and the branch must follow the
pre-registered order: a failed gate ends the ring, MOVED needs only Phi(invert_matter) = Pi,
NULL also needs Phi(invert_all) = Pi and F1 plus an evaluable, passing F3 in both
invert_matter directories, and everything else is NOT DECIDABLE.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
gates = pytest.importorskip('memory_intervention_gates')
N = gates.N_PART


def hook(k, mode):
    inv, pot = mode != 'identity', mode == 'invert_all'
    return {'k': k, 'epochN': k, 'zoom_ticks_stepped': gates.ZOOM_D[k],
            'posA': {'pre': 1, 'post': 2 if inv else 1, 'words_changed': 3 * N if inv else 0, 'mismatched_words': 0},
            'velA': {'pre': 3, 'post': 4 if inv else 3, 'words_changed': 3 * N if inv else 0, 'mismatched_words': 0},
            'pmPot': {'pre': 5, 'post': 6 if pot else 5, 'mismatched_words': 0},
            'moments': {'ok': True},
            'density': {'cells_differing': 7 if inv else 0, 'particles_moved_est': 3 if inv else 0},
            'consumed': {'posB': 2 if inv else 1, 'velB': 4 if inv else 3, 'epochN': k,
                         'posB_mismatched_words': 0, 'velB_mismatched_words': 0}}


@pytest.mark.parametrize('mode', ['identity', 'invert_all', 'invert_matter'])
def test_clean_hooks_pass_in_every_arm(mode):
    assert all(gates.hook_faults(hook(k, mode), k, mode) == [] for k in range(1, 24))


def test_each_receipt_fails_on_its_own_defect():
    h = hook(5, 'invert_all'); h['pmPot']['post'] = h['pmPot']['pre']
    assert gates.hook_faults(h, 5, 'invert_all')                 # potential not moved with the particles
    h = hook(5, 'invert_matter'); h['pmPot']['post'] = 99
    assert gates.hook_faults(h, 5, 'invert_matter')              # potential moved in the matter-only arm
    h = hook(5, 'invert_matter'); h['velA']['words_changed'] = 3 * N - 1
    assert gates.hook_faults(h, 5, 'invert_matter')
    h = hook(5, 'invert_matter'); h['density']['particles_moved_est'] = N // 256 + 1
    assert gates.hook_faults(h, 5, 'invert_matter')
    h = hook(5, 'identity'); h['density']['cells_differing'] = 1
    assert gates.hook_faults(h, 5, 'identity')
    h = hook(5, 'invert_all'); h['consumed']['posB'] = 12345
    assert gates.hook_faults(h, 5, 'invert_all')                 # the next tick read something else
    h = hook(5, 'invert_all'); h['zoom_ticks_stepped'] = 1
    assert gates.hook_faults(h, 5, 'invert_all')                 # d_5 is 2
    h = hook(5, 'identity'); h['posA']['mismatched_words'] = 1
    assert gates.hook_faults(h, 5, 'identity')
    h = hook(5, 'invert_matter'); h['consumed']['velB_mismatched_words'] = 3
    assert gates.hook_faults(h, 5, 'invert_matter')              # hashes agree but the words do not
    h = hook(5, 'invert_all'); h['posA']['post'] = h['posA']['pre']
    assert gates.hook_faults(h, 5, 'invert_all')                 # an inversion that left the hash unchanged


def test_numbers_compare_values_not_names():
    a = {'tag': 'x_ividentity', 'lag1': {'S': 0.1, 'p': 0.02, 'detected': True, 'ci': [0.01, 0.2]}}
    b = copy.deepcopy(a); b['tag'] = 'x'
    assert dict(gates.numbers(a)) == dict(gates.numbers(b))
    b['lag1']['ci'][1] = 0.2000001
    assert dict(gates.numbers(a)) != dict(gates.numbers(b))


def qual(f1=True, f3_eval=True, f3_pass=True):
    return {'verdict': {'F1_identity': {'pass': f1}, 'F3_recovery': {'evaluable': f3_eval, 'pass': f3_pass}}}


CLEAN = {g: [] for g in gates.GATES}
QUALS = {('invert_matter', 'L'): qual(), ('invert_matter', 'Pi'): qual()}


def test_branch_order():
    phi = {'identity': 'L', 'invert_all': 'Pi', 'invert_matter': 'Pi'}
    assert gates.decide_branch(CLEAN, phi, QUALS)[0] == 'MOVED'
    assert gates.decide_branch(CLEAN, dict(phi, invert_all='none'), QUALS)[0] == 'MOVED'   # a silent positive control
    assert gates.decide_branch(CLEAN, dict(phi, invert_matter='L'), QUALS)[0] == 'NULL'
    b, cause, _ = gates.decide_branch(CLEAN, dict(phi, invert_matter='L', invert_all='none'), QUALS)
    assert b == 'NOT DECIDABLE' and 'invert_all' in cause
    q = dict(QUALS); q[('invert_matter', 'Pi')] = qual(f3_eval=False)
    assert gates.decide_branch(CLEAN, dict(phi, invert_matter='L'), q)[0] == 'NOT DECIDABLE'
    q = dict(QUALS); q[('invert_matter', 'L')] = qual(f1=False)
    assert gates.decide_branch(CLEAN, dict(phi, invert_matter='L'), q)[0] == 'NOT DECIDABLE'
    assert gates.decide_branch(CLEAN, dict(phi, invert_matter='none'), QUALS)[0] == 'NOT DECIDABLE'
    for g in gates.GATES:
        b, cause, _ = gates.decide_branch(dict(CLEAN, **{g: ['x']}), phi, QUALS)
        assert b == 'NOT DECIDABLE' and g in cause
