#!/usr/bin/env python3
"""memory_prereg_analyze.py - the analysis for the pre-registered memory test.

Reads the runs written by tests/halo/memory_prereg_run.js (one JSON of the page's
own instrument values per run, plus the raw 32^3 density mesh at the end of every
epoch, float32) and computes every estimator and every null offline, so the whole
analysis is reproducible from the stored meshes without a GPU.

Estimators, all using the page's own correlation (labCorr, HELIOS-V501 line 5250)
with no rotation search and no normalisation beyond the Pearson:

  Retained_k      corr(rho_k, rho_{k-1}) under the x2 index map, inner 16^3 (n=4096)
  TwoBack_k       corr(rho_k, rho_{k-2}) under the x4 index map, inner  8^3 (n=512)
  RetainedM_k     Retained restricted to the SAME inner 8^3 block as TwoBack, so the
                  two arms differ only in epoch lag - the region-matched control the
                  page cannot display
  SeedNull_k      corr(rho_k, rho'_{k-1}) against an independent seed's relic at the
                  same epoch and the same settings: what the estimator reads when
                  there is, by construction, nothing to remember
  ShuffleNull_k   corr(rho_k, shuffled rho_{k-1}): the floor of the estimator itself

Honesty checks carried alongside every number:
  mass          sum(rho) must equal particles/1024; any shortfall is deposit
                saturation and invalidates the run
  ceiling       share of sampled particles pinned to the 500 force ceiling
  occupancy     mean and max particles per mesh cell

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import os
import sys
import numpy as np

N = 32
H = N // 2


def load_run(js_path):
    with open(js_path) as fh:
        d = json.load(fh)
    mesh_path = os.path.join(os.path.dirname(js_path), d['mesh_file'])
    m = np.fromfile(mesh_path, dtype=np.float32)
    k = d['mesh_count']
    if m.size != k * N ** 3:
        raise ValueError(f'{mesh_path}: {m.size} floats, expected {k * N ** 3}')
    d['mesh'] = m.reshape(k, N, N, N).astype(np.float64)
    return d


def _blocks(f, q=None):
    """cells of the current mesh, and the relic cells they read, for map factor f."""
    q = H // f if q is None else q
    cur = np.arange(H - q, H + q)
    rel = H + f * (cur - H)
    return cur, rel


def corr(rho, relic, f, q=None):
    cur, rel = _blocks(f, q)
    a = rho[np.ix_(cur, cur, cur)].ravel()
    b = relic[np.ix_(rel, rel, rel)].ravel()
    va, vb = a.var(), b.var()
    if va <= 0 or vb <= 0:
        return float('nan'), a.size
    return float(((a - a.mean()) * (b - b.mean())).mean() / np.sqrt(va * vb)), a.size


def series(mesh, other=None, rng=None):
    """per-epoch estimators; epoch index k is 1-based and matches the run's epochs."""
    out = []
    for k in range(len(mesh)):
        row = {'epoch': k + 1}
        if k >= 1:
            row['retained'], row['n_ret'] = corr(mesh[k], mesh[k - 1], 2)
            row['retained_matched'], row['n_retm'] = corr(mesh[k], mesh[k - 1], 2, q=H // 4)
            if rng is not None:
                sh = mesh[k - 1].ravel().copy()
                rng.shuffle(sh)
                row['shuffle_null'], _ = corr(mesh[k], sh.reshape(N, N, N), 2)
            if other is not None and k < len(other):
                row['seed_null'], _ = corr(mesh[k], other[k - 1], 2)
                row['seed_null_matched'], _ = corr(mesh[k], other[k - 1], 2, q=H // 4)
        if k >= 2:
            row['twoback'], row['n_two'] = corr(mesh[k], mesh[k - 2], 4)
            if other is not None and k < len(other):
                row['twoback_seed_null'], _ = corr(mesh[k], other[k - 2], 4)
        out.append(row)
    return out


def mass_check(d):
    expected = d['params']['particles'] / 1024.0
    sums = d['mesh'].sum(axis=(1, 2, 3))
    return {'expected_mass': expected,
            'measured_mass_min': float(sums.min()), 'measured_mass_max': float(sums.max()),
            'max_relative_loss': float(np.max(np.abs(sums - expected)) / expected),
            'saturated': bool(np.max(np.abs(sums - expected)) / expected > 1e-3),
            'max_cell_particles': float(d['mesh'].max() * 1024.0),
            'mean_cell_particles': float(d['mesh'].mean() * 1024.0)}


def main(indir):
    runs = {}
    for fn in sorted(os.listdir(indir)):
        if not fn.endswith('.json') or fn in ('analysis.json', 'verdict.json'):
            continue
        d = load_run(os.path.join(indir, fn))
        runs.setdefault((d['params']['preset'], d['params']['selfgrav'],
                         d['params']['gainloss']), []).append(d)

    rng = np.random.default_rng(20260902)
    report = []
    for key in sorted(runs):
        group = sorted(runs[key], key=lambda r: r['params']['seed'])
        for i, d in enumerate(group):
            partner = group[(i + 1) % len(group)] if len(group) > 1 else None
            d['series'] = series(d['mesh'], partner['mesh'] if partner is not None else None, rng)
            d['mass'] = mass_check(d)
            d['seed_null_partner'] = partner['params']['seed'] if partner is not None else None
            report.append({'preset': key[0], 'selfgrav': key[1], 'gainloss': key[2],
                           'seed': d['params']['seed'], 'particles': d['params']['particles'],
                           'pmDensType': d.get('caps_end', {}).get('pmDensType'),
                           'mass': d['mass'], 'series': d['series'],
                           'page': [{'epoch': e['epoch'], 'retained': e['retained'],
                                     'twoback': e['twoback'], 'ceiling': e['ceiling'],
                                     'lambda': e['lambda']} for e in d['epochs']]})
    return report


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg')
    rep = main(os.path.abspath(src))
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.abspath(src), 'analysis.json')
    with open(dst, 'w') as fh:
        json.dump(rep, fh, indent=1)
    print(f'{len(rep)} runs analysed -> {dst}')
