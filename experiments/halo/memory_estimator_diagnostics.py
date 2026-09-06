#!/usr/bin/env python3
"""memory_estimator_diagnostics.py - the reported-only numbers beside a qualification result.

Companion to memory_estimator_qualify.py (imported as a library and never modified). It
writes one JSON with three groups of numbers the qualification result does not store:

  variants     per-run statistics (S, p, intervals, own and stranger correlations, seed
               null values) under the two robustness variants that admit runs on the
               recorded grid; the protocol calls these reported, never scored.
  static_runs  per-run measurements from the raw meshes: epoch-to-epoch correlation of
               the full density, cells holding 99 % of the mass, mass centroid, the
               orbit-residual's epoch-to-epoch correlation on the inner block, and the
               best single-cell shift aligning each pair of seeds.
  resampling   the frozen gates re-run on the recorded meshes Poisson-resampled to fewer
               particles (same fields, more shot noise): eligible epochs, measurable runs
               and detections per condition and count. Exploratory; it assumes the fields
               themselves do not change with particle count.

Usage
  python3 experiments/halo/memory_estimator_diagnostics.py --input-dir DIR --result Q.json \
      --output diagnostics.json [--counts 3000000 1048576 ...]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import hashlib
import itertools
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_estimator_qualify as Q  # noqa: E402

SEEDS = (777, 12345, 31337)
DEFAULT_COUNTS = (3000000, 1048576, 400000, 262144, 65536, 16384)
RESAMPLE_SEED = 7
UNITS_TOTAL = 4096.0            # meshes are in particles/1024 per cell: 4,194,304/1024


def label(key, seed):
    return Q.run_label(key, seed)


def pearson(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    a = a - a.mean(); b = b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else float('nan')


def cells_for_mass(mesh, share=0.99):
    s = np.sort(mesh.ravel().astype(np.float64))[::-1]
    c = np.cumsum(s) / s.sum()
    return int(np.searchsorted(c, share) + 1)


def centroid(mesh):
    m = mesh.astype(np.float64); tot = m.sum()
    z, y, x = np.meshgrid(np.arange(32), np.arange(32), np.arange(32), indexing='ij')
    return [float((m * x).sum() / tot), float((m * y).sum() / tot), float((m * z).sum() / tot)]


def best_shift(a, b):
    """largest Pearson between a and b over single-cell shifts of b along each axis."""
    best = (float('-inf'), (0, 0, 0))
    for dz, dy, dx in itertools.product((-1, 0, 1), repeat=3):
        r = pearson(a, np.roll(b, (dz, dy, dx), axis=(0, 1, 2)))
        if r > best[0]:
            best = (r, (dx, dy, dz))
    return {'pearson': best[0], 'shift_xyz': list(best[1])}


def variant_block(measured, name, cfg):
    res = Q.summarise_all(measured, cfg, 'lag1')
    unm = Q.summarise_all(measured, cfg, 'unmapped')
    out = {'config': cfg, 'runs': {}}
    for (key, seed), r in res.items():
        if r['eligible_epochs'] < cfg['min_epochs'] and not r['measurable']:
            continue
        row = {k: r.get(k) for k in ('eligible_epochs', 'measurable', 'e5_collapse', 'e5_unbalanced',
                                     'seed_null_values', 'mean_mutual_coupling', 'mean_own_coupling', 'p_min')}
        if r['measurable']:
            row.update({'S': r['own']['S'], 'p': r['own']['p'], 'detected': r['detected'],
                        'below_floor': r['below_floor'], 'S_ci95_block_bootstrap': r['S_ci95_block_bootstrap'],
                        'mean_c_own': r['mean_c_own'], 'mean_c_stranger': r['mean_c_stranger'],
                        'mean_c_shuffle': r['mean_c_shuffle'], 'template_rho_mean': r['template_rho_mean'],
                        'lag1_autocorr_Q': r['lag1_autocorr_Q'],
                        'multiplicative_weight_mean': r['multiplicative_weight_mean'],
                        'unmapped_S': unm[(key, seed)]['own']['S'] if unm[(key, seed)].get('measurable') else None,
                        'eligible_epoch_numbers': [k for k, ok in zip(range(Q.FIRST_SCORED, Q.LAST_SCORED + 1), r['eligible_mask']) if ok]})
        out['runs'][label(key, seed)] = row
    out['measurable_runs'] = sorted(k for k, v in out['runs'].items() if v.get('measurable'))
    out['detected_runs'] = sorted(k for k, v in out['runs'].items() if v.get('detected'))
    return out


def static_block(runs, result):
    relvar = {}
    for r in result['runs']:
        relvar[r['tag']] = [e['relvar_cur'] for e in r['epochs']]
    s2 = Q.build_supports()['orbits'][0]
    out = {}
    for key in sorted(runs):
        group = runs[key]
        for g in group:
            m = g['mesh']
            cons = [pearson(m[k], m[k - 1]) for k in range(1, m.shape[0])]
            res = [s2.residual(Q.sub(m[k], Q.B2)) for k in range(m.shape[0])]
            rcons = [pearson(res[k], res[k - 1]) for k in range(1, len(res))]
            out[g['tag']] = {
                'consecutive_epoch_correlation_median': float(np.median(cons)),
                'consecutive_epoch_correlation_min': float(min(cons)),
                'residual_consecutive_correlation_median': float(np.nanmedian(rcons)),
                'cells_for_99pct_mass_median': float(np.median([cells_for_mass(mk) for mk in m])),
                'centroid_xyz_median': [float(v) for v in np.median([centroid(mk) for mk in m], axis=0)],
                'top_cell_mass_share_median': float(np.median([mk.max() / mk.sum() for mk in m])),
                'relvar_cur_min_max': [float(np.nanmin(relvar[g['tag']])), float(np.nanmax(relvar[g['tag']]))],
            }
        # pairwise best single-cell shift at mesh index 20 (epoch 21)
        for a, b in itertools.combinations(group, 2):
            out[f"{a['tag']}|{b['tag']}"] = dict(best_shift(a['mesh'][20], b['mesh'][20]), epoch=21)
    return out


def resampling_block(runs, supports, counts):
    out = {}
    for n in counts:
        rng = np.random.default_rng(RESAMPLE_SEED)
        block = {'conditions': {}, 'measurable_runs': 0, 'measurable_conditions': [], 'detected_runs': []}
        for key in sorted(runs):
            group = runs[key]
            meshes = [(rng.poisson(g['mesh'].astype(np.float64) / UNITS_TOTAL * n) * (UNITS_TOTAL / n)).astype(np.float32)
                      for g in group]
            rows = Q.condition_measure(meshes, [g['seed'] for g in group], key, supports, with_orientation=False)
            res = [Q.summarise_run(rows, i, Q.MAIN, np.random.default_rng(Q.PERM_SEED), 'lag1') for i in range(3)]
            cond = label(key, 0)[:-6]
            block['conditions'][cond] = {
                'eligible_epochs': [r['eligible_epochs'] for r in res],
                'measurable': [bool(r['measurable']) for r in res],
                'e5b_unbalanced': [bool(r['e5_unbalanced']) for r in res],
                'S': [r['own']['S'] if r['measurable'] else None for r in res],
                'p': [r['own']['p'] if r['measurable'] else None for r in res],
                'detected': [bool(r.get('detected', False)) for r in res]}
            block['measurable_runs'] += sum(r['measurable'] for r in res)
            if all(r['measurable'] for r in res):
                block['measurable_conditions'].append(cond)
            block['detected_runs'] += [label(key, g['seed']) for g, r in zip(group, res) if r.get('detected')]
        out[str(n)] = block
        print(f'  resampled {n}: measurable runs {block["measurable_runs"]}, conditions {block["measurable_conditions"]}, '
              f'detected {block["detected_runs"]}', file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--result', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--counts', nargs='*', type=int, default=list(DEFAULT_COUNTS))
    args = ap.parse_args()
    t0 = time.time()
    with open(args.result) as fh:
        result = json.load(fh)
    runs, files = Q.load_grid(args.input_dir)
    supports = Q.build_supports()
    measured = Q.measure_grid(runs, supports, with_orientation=False, label='diag')
    out = {'schema': 'halo-memory-estimator-diagnostics/1', 'author': 'Aldrin Payopay',
           'measured_at': datetime.now(timezone.utc).isoformat(),
           'qualification_result_sha256': Q.sha256_file(args.result),
           'qualify_script_sha256': Q.sha256_file(Q.__file__),
           'this_script_sha256': Q.sha256_file(os.path.abspath(__file__)),
           'note': 'reported-only diagnostics; nothing here is scored by the protocol',
           'variants': {name: variant_block(measured, name, Q.VARIANTS[name]) for name in ('e2_pr4', 'den_0.10')},
           'static_runs': static_block(runs, result),
           'resampling': {'seed': RESAMPLE_SEED, 'assumption': 'the recorded fields are unchanged; only shot noise is added',
                          'counts': resampling_block(runs, supports, args.counts)},
           'seconds': None}
    out['seconds'] = time.time() - t0
    with open(args.output, 'w') as fh:
        json.dump(Q.jsonable(out), fh, indent=1, allow_nan=False)
    print(f'wrote {args.output} in {out["seconds"]:.0f}s')


if __name__ == '__main__':
    main()
