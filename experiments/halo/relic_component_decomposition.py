#!/usr/bin/env python3
"""relic_component_decomposition.py - where does the own-relic contrast live? A design
input for the Ring 30 intervention (analysis/2026-09-22_relic_intervention.md), computed
on the nine committed Ring 29 control runs before any intervention run existed.

Read-only on the data. Imports the frozen scorer (experiments/halo/memory_estimator_qualify.py,
sha256 7619ef6b...) as a module and never edits it; reuses predicted(), sub(), B2,
build_supports() (the orbit residual), pearson(), predict_cell(), contrast() and
block_relabel_test() with its seed.

The B2 (16^3) orbit residuals of the current field and of each x2 relic prediction are split
into six exactly orthogonal projections on the grid, array axes [z][y][x]:
  Y : the mirror y -> -y about 15.5 (y, mesh axis 1, is the chamber's spin axis)
  R : the quarter turn about y (np.rot90 on axes (0, 2)); R and Y commute
  C4 irreps about y: A (R-invariant), Bm (sign-alternating under R), E (the rest)
  components = {even, odd in y} x {A, Bm, E}; odd_A is also split into its pure y-profile
  (a function of y alone) and the rest. The point inversion P is the mirror composed with the
  half-turn about y, so the P-odd part is odd_A + odd_Bm + even_E; its share of each run's own
  correlation, O, is reported as P_parity.odd_own.
The orbit support is invariant under Y and R, so the projections commute with the monopole
removal. M_ab = sum over components of <rc_a^c, rp_b^c> / (|rc_a| |rp_b|) exactly; each
component (and each group of components) is also rescored "alone" with the scorer's own
hybrid null and block relabelling. The recomputed full matrices are checked against the
recorded qualification.json. Numbers only: a correlation on the control chooses which
component to intervene on; it decides nothing.

    python3 experiments/halo/relic_component_decomposition.py DIR --json OUT

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import json
import math
import os
import sys

import numpy as np

import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_estimator_qualify as mq  # noqa: E402


def Y(f):
    return np.flip(f, axis=1)


def R(f, k=1):
    return np.rot90(f, k, axes=(0, 2))


def components(f):
    f = f.reshape(16, 16, 16)
    ev = 0.5 * (f + Y(f))
    od = f - ev
    out = {}
    for pname, g in (('even', ev), ('odd', od)):
        r1, r2, r3 = R(g, 1), R(g, 2), R(g, 3)
        a = 0.25 * (g + r1 + r2 + r3)
        bm = 0.25 * (g - r1 + r2 - r3)
        e = 0.5 * (g - r2)
        if pname == 'odd':
            prof = a.mean(axis=(0, 2), keepdims=True) * np.ones_like(a)   # function of y only (odd)
            out['odd_A_yprof'] = prof
            out['odd_A_rest'] = a - prof
        else:
            out[f'{pname}_A'] = a
        out[f'{pname}_Bm'] = bm
        out[f'{pname}_E'] = e
    return out


COMP = ['even_A', 'even_Bm', 'even_E', 'odd_A_yprof', 'odd_A_rest', 'odd_Bm', 'odd_E']
GROUPS = {'even': ['even_A', 'even_Bm', 'even_E'], 'odd': ['odd_A_yprof', 'odd_A_rest', 'odd_Bm', 'odd_E'],
          'Rinv': ['even_A', 'odd_A_yprof', 'odd_A_rest'], 'odd_A': ['odd_A_yprof', 'odd_A_rest'],
          'all_but_odd_yprof': ['even_A', 'even_Bm', 'even_E', 'odd_A_rest', 'odd_Bm', 'odd_E'], 'Rrem': ['even_Bm', 'even_E', 'odd_Bm', 'odd_E'],
          'even_Rinv': ['even_A'], 'even_Rrem': ['even_Bm', 'even_E'],
          'P_odd': ['odd_A_yprof', 'odd_A_rest', 'odd_Bm', 'even_E'], 'P_even': ['even_A', 'even_Bm', 'odd_E'],
          'odd_Rinv': ['odd_A_yprof', 'odd_A_rest'], 'odd_Rrem': ['odd_Bm', 'odd_E']}


def add_null(M, i):
    return mq.predict_cell(M, i, i, 'additive')


def mean(x):
    # None is the frozen scorer's JSON null for a value it could not form (its NaN/inf -> None),
    # dropped here exactly as NaN always was. Added with Ring 30's results: the recorded lag-two
    # row is null in one lag-one-eligible epoch of two intervened runs, which crashed this
    # report; on every input without a null the output is byte-identical.
    x = [v for v in x if v is not None and v == v]
    return float(np.mean(x)) if x else float('nan')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir', help='a scored directory: nine run JSONs + meshes + qualification.json')
    ap.add_argument('--json', required=True)
    a = ap.parse_args()
    INDIR, OUT = a.dir, a.json
    q = json.load(open(os.path.join(INDIR, 'qualification.json')))
    DETECTED = {(r['condition']['selfgrav'], r['seed']) for r in q['runs'] if r['lag1'].get('detected')}
    runs, _ = mq.load_grid(INDIR)
    s2 = mq.build_supports()['orbits'][0]
    rec_by = {(r['condition']['selfgrav'], r['seed']): r for r in q['runs']}
    check = {'max_abs_M_diff': 0.0, 'max_abs_Q_diff': 0.0, 'n_epochs_checked': 0}
    out_runs = []
    for key in sorted(runs):
        group = runs[key]
        seeds = [g['seed'] for g in group]
        meshes = [g['mesh'] for g in group]
        per_epoch = []  # per k: dict of matrices
        for k in range(mq.FIRST_SCORED, mq.LAST_SCORED + 1):
            cur2 = [mq.sub(m[k - 1], mq.B2) for m in meshes]
            rc = [s2.residual(c) for c in cur2]
            rc = [r - r.mean() for r in rc]
            preds = {}
            for L in range(0, 5):
                idx = k - 1 - L
                if idx < 0:
                    continue
                rp = [s2.residual(mq.predicted(m[idx], 2)) for m in meshes]
                preds[L] = [r - r.mean() for r in rp]
            rp = preds[1]
            M = [[mq.pearson(rc[a], rp[b]) for b in range(3)] for a in range(3)]
            cc = [components(r) for r in rc]
            cp = [components(r) for r in rp]
            nc = [float(np.sqrt((r * r).sum())) for r in rc]
            npp = [float(np.sqrt((r * r).sum())) for r in rp]
            Mc = {c: [[float((cc[a][c] * cp[b][c]).sum() / (nc[a] * npp[b])) for b in range(3)]
                      for a in range(3)] for c in COMP}
            Malone = {c: [[mq.pearson(cc[a][c], cp[b][c]) for b in range(3)] for a in range(3)]
                      for c in COMP}
            varc = {c: [float((cc[a][c] ** 2).sum()) / nc[a] ** 2 for a in range(3)] for c in COMP}
            varp = {c: [float((cp[a][c] ** 2).sum()) / npp[a] ** 2 for a in range(3)] for c in COMP}
            lagc = {L: [[mq.pearson(rc[a], preds[L][b]) for b in range(3)] for a in range(3)] for L in preds}
            # symmetry-op scores of the own prediction (and the identity) for each row
            ops = {}
            for a in range(3):
                p = rp[a].reshape(16, 16, 16)
                ops[a] = {'id': M[a][a], 'Y': mq.pearson(rc[a], Y(p)),
                          'R1': mq.pearson(rc[a], R(p, 1)), 'R2': mq.pearson(rc[a], R(p, 2)),
                          'R3': mq.pearson(rc[a], R(p, 3)),
                          'YR2': mq.pearson(rc[a], Y(R(p, 2)))}
                allo = [(mq.pearson(rc[a], s2.residual(mq.apply_op(mq.predicted(meshes[a][k - 2], 2), op))), op)
                        for op in mq.CUBE_OPS[1:]]
                best = max(allo, key=lambda t: t[0] if t[0] == t[0] else -9)
                ops[a]['best_nonid'] = best[0]
                ops[a]['best_nonid_op'] = {'perm_zyx': list(best[1][0]), 'flips_zyx': list(best[1][1])}
                ops[a]['ties_1e-3'] = [{'perm_zyx': list(op[0]), 'flips_zyx': list(op[1])}
                                       for v, op in allo if v == v and abs(v - M[a][a]) < 1e-3]
            per_epoch.append({'k': k, 'M': M, 'Mc': Mc, 'Malone': Malone, 'varc': varc, 'varp': varp,
                              'lag': lagc, 'ops': ops})
        for i, seed in enumerate(seeds):
            rec = rec_by[(key[1], seed)]
            strangers = [j for j in range(3) if j != i]
            elig = [e['eligible'] for e in rec['epochs']]
            assert len(elig) == len(per_epoch)
            rows = [pe for pe, ok in zip(per_epoch, elig) if ok]
            # identity check vs the recorded numbers
            for pe, e in zip(per_epoch, rec['epochs']):
                d = max(abs(pe['M'][i][c] - e['M_row'][c]) for c in range(3))
                check['max_abs_M_diff'] = max(check['max_abs_M_diff'], d)
                if e['eligible']:
                    dq = abs(mq.contrast(pe['M'], i, i) - e['Q_own'])
                    check['max_abs_Q_diff'] = max(check['max_abs_Q_diff'], dq)
                check['n_epochs_checked'] += 1
            n = len(rows)
            Q = np.array([[mq.contrast(pe['M'], i, i)] + [mq.contrast(pe['M'], i, c) for c in strangers]
                          for pe in rows])
            test = mq.block_relabel_test(Q, np.random.default_rng(mq.PERM_SEED))
            res = {'condition_sg': key[1], 'seed': seed, 'detected_main': (key[1], seed) in DETECTED,
                   'eligible_epochs': n, 'S_hybrid': test['own']['S'], 'p_hybrid': test['own']['p'],
                   # a run the frozen scorer left unmeasurable (below its eligible-epoch floor) has
                   # no recorded 'own': None here; its decomposition is still reported, never scored
                   'recorded_S': rec['lag1'].get('own', {}).get('S'), 'recorded_p': rec['lag1'].get('own', {}).get('p'),
                   'mean_M_own': mean([pe['M'][i][i] for pe in rows]),
                   'mean_M_strangers': mean([np.mean([pe['M'][i][j] for j in strangers]) for pe in rows]),
                   'mean_P_hybrid': mean([mq.predict_cell(pe['M'], i, i) for pe in rows]),
                   'mean_P_additive': mean([add_null(pe['M'], i) for pe in rows]),
                   'S_additive_total': mean([pe['M'][i][i] - add_null(pe['M'], i) for pe in rows])}
            comp = {}
            for c in COMP:
                comp[c] = {
                    'var_share_cur': mean([pe['varc'][c][i] for pe in rows]),
                    'var_share_ownpred': mean([pe['varp'][c][i] for pe in rows]),
                    'M_own_contrib': mean([pe['Mc'][c][i][i] for pe in rows]),
                    'M_strangers_contrib': mean([np.mean([pe['Mc'][c][i][j] for j in strangers]) for pe in rows]),
                    'Q_additive_contrib': mean([pe['Mc'][c][i][i] - add_null(pe['Mc'][c], i) for pe in rows]),
                    'alone_M_own': mean([pe['Malone'][c][i][i] for pe in rows]),
                    'alone_M_strangers': mean([np.mean([pe['Malone'][c][i][j] for j in strangers]) for pe in rows]),
                }
                Qa = np.array([[mq.contrast(pe['Malone'][c], i, i)] + [mq.contrast(pe['Malone'][c], i, cc)
                                                                          for cc in strangers] for pe in rows])
                if np.all(np.isfinite(Qa)):
                    ta = mq.block_relabel_test(Qa, np.random.default_rng(mq.PERM_SEED))
                    comp[c]['alone_S_hybrid'] = ta['own']['S']
                    comp[c]['alone_p'] = ta['own']['p']
            grp = {}
            for gname, cs in GROUPS.items():
                grp[gname] = {f: float(sum(comp[c][f] for c in cs))
                              for f in ('var_share_cur', 'var_share_ownpred', 'M_own_contrib',
                                        'M_strangers_contrib', 'Q_additive_contrib')}
                # the group taken alone: sum the component matrices then renormalise by group norms
                Qg, Mown_g, Mstr_g = [], [], []
                for pe in rows:
                    Mg = [[sum(pe['Mc'][c][a][b] for c in cs) /
                           math.sqrt(max(sum(pe['varc'][c][a] for c in cs), 1e-300) *
                                     max(sum(pe['varp'][c][b] for c in cs), 1e-300))
                           for b in range(3)] for a in range(3)]
                    Qg.append([mq.contrast(Mg, i, i)] + [mq.contrast(Mg, i, cc) for cc in strangers])
                    Mown_g.append(Mg[i][i])
                    Mstr_g.append(np.mean([Mg[i][j] for j in strangers]))
                tg = mq.block_relabel_test(np.array(Qg), np.random.default_rng(mq.PERM_SEED))
                grp[gname].update({'alone_M_own': mean(Mown_g), 'alone_M_strangers': mean(Mstr_g),
                                   'alone_S_hybrid': tg['own']['S'], 'alone_p': tg['own']['p']})
            res['components'] = comp
            # point inversion P = mirror o half-turn about y: P-odd = odd_A + odd_Bm + even_E. P is an
            # exact symmetry of the chamber, so the P-odd part of the own correlation (O) does not
            # depend on which way any stranger was realised; the scorer's null does.
            podd, peven = ['odd_A_yprof', 'odd_A_rest', 'odd_Bm', 'even_E'], ['even_A', 'even_Bm', 'odd_E']
            res['P_parity'] = {f'{par}_{f}': float(sum(comp[c][fk] for c in cs))
                               for par, cs in (('odd', podd), ('even', peven))
                               for f, fk in (('own', 'M_own_contrib'), ('strangers', 'M_strangers_contrib'),
                                             ('Qadd', 'Q_additive_contrib'))}
            res['groups'] = grp
            # per-epoch own contributions for the four aggregate groups
            res['by_epoch'] = [{'k': pe['k'], 'M_own': pe['M'][i][i],
                                'Q_hybrid': mq.contrast(pe['M'], i, i),
                                'Q_additive': pe['M'][i][i] - add_null(pe['M'], i),
                                **{f'Mown_{g}': float(sum(pe['Mc'][c][i][i] for c in GROUPS[g]))
                                   for g in ('even', 'odd', 'Rinv', 'Rrem')},
                                **{f'Qadd_{g}': float(sum(pe['Mc'][c][i][i] - add_null(pe['Mc'][c], i)
                                                          for c in GROUPS[g]))
                                                   for g in ('even', 'odd', 'Rinv', 'Rrem')},
                                **{'Mown_odd_yprof': pe['Mc']['odd_A_yprof'][i][i],
                                   'Qadd_odd_yprof': pe['Mc']['odd_A_yprof'][i][i] - add_null(pe['Mc']['odd_A_yprof'], i)}}
                               for pe in rows]
            # orientation diagnostic, recorded + recomputed symmetry-op scores
            orr = [e['orientation'] for e, ok in zip(rec['epochs'], elig) if ok]
            res['orientation_recorded'] = {
                'mean_share_own': mean([o['share_own'] for o in orr]),
                'epochs_identity_unique_top': int(sum(1 for o in orr if o['share_own'] == 0)),
                'mean_max_own_minus_M_own': mean([o['max_own'] - pe['M'][i][i] for o, pe in zip(orr, rows)]),
                'epochs_max_nonid_above_identity': int(sum(1 for o, pe in zip(orr, rows)
                                                          if o['max_own'] > pe['M'][i][i])),
                'mean_degenerate_own': mean([o['degenerate_own'] for o in orr]),
                'mean_share_stranger': mean([o['share_stranger'] for o in orr])}
            opn = ['Y', 'R1', 'R2', 'R3', 'YR2']
            res['symmetry_ops_own_pred'] = {
                **{f'mean_{o}': mean([pe['ops'][i][o] for pe in rows]) for o in opn},
                'mean_identity': mean([pe['ops'][i]['id'] for pe in rows]),
                'mean_best_nonid': mean([pe['ops'][i]['best_nonid'] for pe in rows]),
                'best_nonid_op_counts': {},
                'mean_ties_1e-3': mean([len(pe['ops'][i]['ties_1e-3']) for pe in rows])}
            cnt = {}
            for pe in rows:
                b = pe['ops'][i]['best_nonid_op']
                s = f"perm{''.join(map(str, b['perm_zyx']))}_flip{''.join('1' if f else '0' for f in b['flips_zyx'])}"
                cnt[s] = cnt.get(s, 0) + 1
            res['symmetry_ops_own_pred']['best_nonid_op_counts'] = dict(sorted(cnt.items(), key=lambda t: -t[1]))
            # unmapped and lag-two arms: recorded summaries + per-epoch rows over eligible epochs
            def arm_summary(name):
                a = rec.get(name, {})
                keep = ('eligible_epochs', 'measurable', 'e5_collapse', 'e5_unbalanced', 'detected',
                        'mean_c_own', 'mean_c_stranger', 'lag1_autocorr_Q', 'S_ci95_block_bootstrap')
                o = {kk: a.get(kk) for kk in keep if kk in a}
                if 'own' in a:
                    o['S'] = a['own']['S']
                    o['p'] = a['own']['p']
                return o
            ee = [e for e in rec['epochs'] if e['eligible']]
            res['unmapped'] = {'recorded': arm_summary('unmapped'),
                               'mean_U_own_lag1elig': mean([e['U_row'][i] for e in ee]),
                               'mean_U_strangers_lag1elig': mean([mean([e['U_row'][j] for j in strangers]) for e in ee])}
            res['lag2'] = {'recorded': arm_summary('lag2'), 'recorded_trilinear': arm_summary('lag2_tri'),
                           'mean_M2_own_lag1elig': mean([e['M2_row'][i] for e in ee]),
                           'mean_M2_strangers_lag1elig': mean([mean([e['M2_row'][j] for j in strangers]) for e in ee])}
            # lag decorrelation: current B2 vs x2 prediction of mesh k-1-L (L=1 is the scored relic)
            lagd = {}
            for L in range(0, 5):
                rr = [pe for pe in rows if L in pe['lag']]
                lagd[f'L{L}'] = {'n': len(rr), 'own': mean([pe['lag'][L][i][i] for pe in rr]),
                                 'strangers': mean([np.mean([pe['lag'][L][i][j] for j in strangers]) for pe in rr]),
                                 'own_minus_strangers': mean([pe['lag'][L][i][i] - np.mean([pe['lag'][L][i][j] for j in strangers])
                                                              for pe in rr]),
                                 'Q_hybrid_mean': mean([mq.contrast(pe['lag'][L], i, i) for pe in rr])}
            res['lag_decorrelation_x2'] = lagd
            # centre of mass and y asymmetry per mesh (all 24)
            m = meshes[i].astype(np.float64)
            idx = np.arange(32) - mq.CENTRE
            tot = m.sum(axis=(1, 2, 3))
            comz = (m.sum(axis=(2, 3)) * idx).sum(axis=1) / tot
            comy = (m.sum(axis=(1, 3)) * idx).sum(axis=1) / tot
            comx = (m.sum(axis=(1, 2)) * idx).sum(axis=1) / tot
            north = m[:, :, 16:, :].sum(axis=(1, 2, 3))
            south = m[:, :, :16, :].sum(axis=(1, 2, 3))
            yasym = (north - south) / tot
            b2 = m[:, 8:24, 8:24, 8:24]
            b2n = b2[:, :, 8:, :].sum(axis=(1, 2, 3))
            b2s = b2[:, :, :8, :].sum(axis=(1, 2, 3))
            steps = np.sqrt(np.diff(comz) ** 2 + np.diff(comy) ** 2 + np.diff(comx) ** 2)
            res['com'] = {'z': comz.tolist(), 'y': comy.tolist(), 'x': comx.tolist(),
                          'radius': np.sqrt(comz ** 2 + comy ** 2 + comx ** 2).tolist(),
                          'step': steps.tolist(), 'mean_step': float(steps.mean()),
                          'max_radius': float(np.sqrt(comz ** 2 + comy ** 2 + comx ** 2).max()),
                          'y_asym_total': yasym.tolist(),
                          'y_asym_b2': ((b2n - b2s) / b2.sum(axis=(1, 2, 3))).tolist(),
                          'mean_abs_y_asym_total': float(np.abs(yasym).mean()),
                          'mean_abs_y_asym_b2': float(np.abs((b2n - b2s) / b2.sum(axis=(1, 2, 3))).mean()),
                          'y_asym_total_lag1_autocorr': float(np.corrcoef(yasym[:-1], yasym[1:])[0, 1]),
                          'units': 'mesh cells from the centre 15.5; y_asym = (N - S)/total, N = y index 16..31'}
            ya_b2 = (b2n - b2s) / b2.sum(axis=(1, 2, 3))
            ks = [pe['k'] for pe in rows]
            cur_a = np.array([ya_b2[k - 1] for k in ks])
            rel_a = np.array([yasym[k - 2] for k in ks])
            res['y_asym_persistence_elig'] = {
                'n': len(ks), 'same_sign_epochs': int((np.sign(cur_a) == np.sign(rel_a)).sum()),
                'corr_cur_b2_vs_relic_total': float(np.corrcoef(cur_a, rel_a)[0, 1]),
                'mean_cur_b2': float(cur_a.mean()), 'mean_relic_total': float(rel_a.mean()),
                'strangers_same_sign_epochs': {str(seeds[j]): int(sum(
                    np.sign(ya_b2[k - 1]) == np.sign(
                        (meshes[j][k - 2][:, 16:, :].astype(np.float64).sum() - meshes[j][k - 2][:, :16, :].astype(np.float64).sum()))
                    for k in ks)) for j in strangers}}
            out_runs.append(res)
            rs = 'unmeasurable' if res['recorded_S'] is None else f"{res['recorded_S']:.4f}"
            print(f"{key[1]} {seed} n={n} S={res['S_hybrid']:.4f} (rec {rs}) "
                  f"Mown={res['mean_M_own']:.4f}", file=sys.stderr)
    # hemisphere-sign agreement between seeds of a condition (all 24 meshes, |asym| > 0.1 in both)
    hemi = {}
    by = {}
    for r in out_runs:
        by.setdefault(r['condition_sg'], {})[r['seed']] = np.array(r['com']['y_asym_total'])
    for c, rr in by.items():
        ss = list(rr)
        hemi[str(c)] = {'mean_y_asym_total': {str(k): float(v.mean()) for k, v in rr.items()}, 'pairs': {}}
        for a in range(3):
            for b in range(a + 1, 3):
                x, y = rr[ss[a]], rr[ss[b]]
                m = (np.abs(x) > 0.1) & (np.abs(y) > 0.1)
                hemi[str(c)]['pairs'][f'{ss[a]}-{ss[b]}'] = [int((np.sign(x[m]) == np.sign(y[m])).sum()), int(m.sum())]
    allabs = np.array([np.abs(r['com']['y_asym_total']) for r in out_runs])
    hemi['mesh_idx_abs_asym_gt_0.9_all_runs'] = [int(i) for i in range(allabs.shape[1]) if (allabs[:, i] > 0.9).all()]
    hemi['median_abs_asym_by_mesh_idx'] = np.median(allabs, axis=0).tolist()
    for r in out_runs:
        qv = np.array([e['Q_hybrid'] for e in r['by_epoch']])
        srt = np.sort(qv)[::-1]
        r['Q_concentration'] = {'top3_sum_over_n': float(srt[:3].sum() / len(qv)),
                                'S_without_top3': float(srt[3:].mean())}
    out = {'hemisphere': hemi, 'check_vs_recorded': check, 'components': COMP, 'groups': GROUPS, 'runs': out_runs,
           'notes': {'decomposition': 'orbit residual of B2 (16^3), projections exact on the grid; '
                                      'M_own_contrib and Q_additive_contrib sum exactly over components to M_own and to the additive-null Q; '
                                      'the scored Q is hybrid (nonlinear in the off-diagonals) and is reported whole, plus per-component-alone rescoring (alone_*)',
                     'lag': 'L = mesh age: current is mesh k-1, the scored relic is mesh k-2 (L=1); L=2 is mesh k-3 mapped with ONE x2 compression'}}
    with open(OUT, 'w') as fh:
        json.dump(mq.jsonable(out), fh, indent=1)
    print(json.dumps(check), file=sys.stderr)


if __name__ == '__main__':
    main()
