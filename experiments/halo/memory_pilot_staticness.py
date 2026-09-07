#!/usr/bin/env python3
"""memory_pilot_staticness.py - the measurability pilot's own screens.

Screens A1 to A5 of docs/halo/2026-09-06_measurability_pilot_preregistration.md.
They change no gate, no threshold and no verdict the frozen scorer produces; they
decide only whether a condition counts toward the pilot's headline number, and they
are published for every condition whatever the outcome.

  A1 seed degeneracy       raw cross-seed Pearson of the full density, worst pair
  A2 structural template   cross-seed template correlation with the deposit's Poisson
                           shot-noise power removed
  A3 staticness            lag-one Pearson of the full field and of the angular residual
  A4 clamp share           median recorded force-clamp share
  A5 particle-identity     shot-noise share of the predicted residual's power

The original question this file answered, and still answers, is A3:

The frozen qualification protocol has no gate that names a static field. On the
recorded grid the twelve static runs were removed only as a side effect, and the
two conditions that did reach twelve eligible epochs were refused by the
seed-balance gate E5b -- a rule whose stated reason is unbalanced seed quality,
not "this field does not move". One condition on that grid, default sg0.8 gl0,
is a three-way duplicate whose seeds share a centroid and correlate pairwise at
0.99999, already passes E5 and E5b with balanced null values, and sits six
eligible epochs short of being called measurable. A pilot that counts measurable
conditions can therefore be satisfied by a field carrying no information.

This script measures staticness beside the frozen scorer, and changes nothing it
does. Per run it reports:

  self_full     median Pearson of each epoch's full 32^3 density against its own
                previous epoch
  self_resid    the same for the monopole-removed angular residual on B2 (the
                inner 16^3, cells 8..23), which is the quantity the estimator's
                correlations actually see
  centroid      the mass centroid of the last epoch, and how far it moves across
                the run

Per condition it reports the pairwise cross-seed correlation of the last epoch's
full density at zero shift and at the best shift of one cell along each axis: a
pair that only differs by a one-cell translation is one run, not two.

Monopole removal here is written from the protocol's prose, independently of the
frozen script: cells related by a symmetry of the cube about the centre 15.5 form
an orbit (the cells sharing one sorted triple of axis distances), and each field
is replaced by its deviation from its own orbit mean inside the block.

Usage: python3 memory_pilot_staticness.py INPUT_DIR [--json OUT.json]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import json
import math
import os

import numpy as np

N = 32
CENTRE = (N - 1) / 2.0
B2 = slice(8, 24)
STATIC_AT = 0.99          # A3, full field
RESID_STATIC_AT = 0.70    # A3, angular residual
DEGENERATE_AT = 0.99      # A1
TSTRUCT_AT = 0.9          # A2
CLAMP_AT = 0.5            # A4
IDENTITY_AT = 0.01        # A5
DEPOSIT_UNIT = 1024.0     # a mesh cell holds value*1024 particles


def orbit_labels():
    """One integer per B2 cell; cells sharing a sorted triple of |axis distance| match."""
    u = np.abs(np.arange(8, 24) - CENTRE)
    key = {}
    lab = np.zeros((16, 16, 16), dtype=np.int32)
    for i in range(16):
        for j in range(16):
            for k in range(16):
                t = tuple(sorted((u[i], u[j], u[k])))
                lab[i, j, k] = key.setdefault(t, len(key))
    return lab, len(key)


def residual(block, lab, n_orb):
    flat = block.reshape(-1).astype(np.float64)
    l = lab.reshape(-1)
    means = np.bincount(l, weights=flat, minlength=n_orb) / np.bincount(l, minlength=n_orb)
    return flat - means[l]


def pearson(a, b):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if a.std() == 0 or b.std() == 0:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def predicted(relic):
    """The passive-relic prediction on B2: current cell x in 8..23 is the SUM of the
    relic cells {2x-16, 2x-15} on each axis, which is the exact image of a shrink by
    two under a nearest-cell deposit."""
    lo = 2 * np.arange(8, 24) - 16
    out = np.zeros((16, 16, 16), dtype=np.float64)
    for dz in (0, 1):
        for dy in (0, 1):
            for dx in (0, 1):
                out += relic[np.ix_(lo + dz, lo + dy, lo + dx)].astype(np.float64)
    return out


def noise_share(pred, resid):
    """Fraction of the predicted residual's power that is the deposit's Poisson noise.

    A cell holding value c in units of particles/1024 holds 1024*c particles, whose
    Poisson variance is 1024*c particles, i.e. c/1024 in mesh units squared. Summed
    over the block that is the shot-noise power; divide by the residual's own power."""
    power = float(np.sum(resid ** 2))
    if power <= 0:
        return float('nan')
    return float(np.sum(pred) / DEPOSIT_UNIT / power)


def centroid(mesh):
    tot = mesh.sum()
    if tot <= 0:
        return [float('nan')] * 3
    g = np.arange(N, dtype=np.float64)
    return [float((mesh.sum(axis=(1, 2)) * g).sum() / tot),   # z
            float((mesh.sum(axis=(0, 2)) * g).sum() / tot),   # y
            float((mesh.sum(axis=(0, 1)) * g).sum() / tot)]   # x


def best_shift_corr(a, b):
    """Best Pearson over shifts of at most one cell on each axis, and the shift."""
    best, at = -2.0, (0, 0, 0)
    for dz in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                r = pearson(a, np.roll(b, (dz, dy, dx), axis=(0, 1, 2)))
                if np.isfinite(r) and r > best:
                    best, at = r, (dz, dy, dx)
    return best, at


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input_dir')
    ap.add_argument('--json')
    args = ap.parse_args()

    lab, n_orb = orbit_labels()
    runs, conds = [], {}
    for fn in sorted(os.listdir(args.input_dir)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(args.input_dir, fn)) as fh:
            head = json.load(fh)
        if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
            continue
        mesh = np.fromfile(os.path.join(args.input_dir, head['mesh_file']),
                           dtype='<f4').reshape(head['mesh_count'], N, N, N)
        p = head['params']
        key = f"{p['preset']}_sg{float(p['selfgrav']):g}_gl{float(p['gainloss']):g}"
        full = [pearson(mesh[k], mesh[k - 1]) for k in range(1, len(mesh))]
        res = [residual(m[B2, B2, B2], lab, n_orb) for m in mesh]
        resid = [pearson(res[k], res[k - 1]) for k in range(1, len(res))]
        c0, c1 = centroid(mesh[0]), centroid(mesh[-1])
        row = {'tag': head['tag'], 'condition': key, 'seed': int(p['seed']),
               'particles': int(p['particles']), 'epoch_len': float(p['epoch_len']),
               'epochs': int(head['mesh_count']),
               'self_full_median': float(np.nanmedian(full)),
               'self_full_min': float(np.nanmin(full)),
               'self_resid_median': float(np.nanmedian(resid)),
               'self_resid_min': float(np.nanmin(resid)),
               'centroid_first': c0, 'centroid_last': c1,
               'centroid_travel': float(np.linalg.norm(np.array(c1) - np.array(c0))),
               'static': bool(np.nanmedian(full) >= STATIC_AT)}
        row['clamp_share_median'] = float(np.nanmedian(
            [e['ceiling'] for e in head.get('epochs', []) if isinstance(e.get('ceiling'), (int, float))]
            or [float('nan')]))
        runs.append(row)
        # A2 and A5 need the predicted fields of every seed at the same epoch, so keep
        # the monopole-removed prediction per scored epoch (k = 3..24: current index
        # k-1, relic index k-2, so the relics are mesh indices 1..22).
        preds, shares = [], []
        for j in range(1, min(23, len(mesh) - 1) + 1):
            pr = predicted(mesh[j])
            rp = residual(pr, lab, n_orb)
            preds.append(rp)
            shares.append(noise_share(pr, rp))
        conds.setdefault(key, []).append((int(p['seed']), mesh[-1], preds, shares))

    pairs, screens = [], []
    for key, group in sorted(conds.items()):
        group.sort(key=lambda g: g[0])
        worst_raw, tmpl, tstruct = -2.0, [], []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                r0 = pearson(group[i][1], group[j][1])
                rb, at = best_shift_corr(group[i][1], group[j][1])
                pairs.append({'condition': key, 'seeds': [group[i][0], group[j][0]],
                              'corr_shift0': r0, 'corr_best': rb, 'best_shift': list(at)})
                if np.isfinite(r0):
                    worst_raw = max(worst_raw, abs(r0))
                # A2, per scored epoch: the two seeds' predicted residuals, and the
                # same correlation with each field's shot-noise power divided out.
                for e in range(min(len(group[i][2]), len(group[j][2]))):
                    c = pearson(group[i][2][e], group[j][2][e])
                    fi, fj = group[i][3][e], group[j][3][e]
                    tmpl.append(abs(c))
                    d = math.sqrt(max(0.0, (1 - fi)) * max(0.0, (1 - fj))) if np.isfinite(fi) and np.isfinite(fj) else float('nan')
                    tstruct.append(abs(c) / d if d and np.isfinite(d) and d > 0 else float('nan'))
        allshares = [x for g in group for x in g[3] if np.isfinite(x)]
        clamps = [r['clamp_share_median'] for r in runs if r['condition'] == key]
        statics = [r for r in runs if r['condition'] == key]
        sc = {'condition': key,
              'A1_worst_raw_cross_seed': worst_raw if worst_raw > -2 else float('nan'),
              'A2_tmpl_median': float(np.nanmedian(tmpl)) if tmpl else float('nan'),
              'A2_tstruct_median': float(np.nanmedian(tstruct)) if tstruct else float('nan'),
              'A3_self_full_max': float(np.nanmax([r['self_full_median'] for r in statics])),
              'A3_self_resid_max': float(np.nanmax([r['self_resid_median'] for r in statics])),
              'A4_clamp_share_median': float(np.nanmedian(clamps)) if clamps else float('nan'),
              'A5_noise_share_median': float(np.nanmedian(allshares)) if allshares else float('nan')}
        struck = []
        if sc['A1_worst_raw_cross_seed'] >= DEGENERATE_AT: struck.append('A1 seed degeneracy')
        if sc['A2_tstruct_median'] >= TSTRUCT_AT: struck.append('A2 structural template')
        if sc['A3_self_full_max'] >= STATIC_AT or sc['A3_self_resid_max'] >= RESID_STATIC_AT:
            struck.append('A3 staticness')
        if sc['A4_clamp_share_median'] > CLAMP_AT: struck.append('A4 clamp share')
        if sc['A5_noise_share_median'] > IDENTITY_AT: struck.append('A5 particle identity')
        sc['struck_by'] = struck
        sc['passes_screens'] = not struck
        screens.append(sc)

    hdr = (f"{'tag':56s} {'selfFull':>9s} {'selfResid':>9s} {'travel':>7s} {'static':>7s}")
    print(hdr); print('-' * len(hdr))
    for r in sorted(runs, key=lambda r: (r['condition'], r['seed'])):
        print(f"{r['tag'][:56]:56s} {r['self_full_median']:9.5f} {r['self_resid_median']:9.5f} "
              f"{r['centroid_travel']:7.3f} {str(r['static']):>7s}")
    print()
    for p in pairs:
        print(f"{p['condition']:26s} seeds {p['seeds'][0]:6d}/{p['seeds'][1]:<6d} "
              f"r(shift 0) {p['corr_shift0']:8.5f}  best {p['corr_best']:8.5f} at {p['best_shift']}")
    print()
    h = (f"{'condition':26s} {'A1 raw':>8s} {'A2 tmpl':>8s} {'A2 tstr':>8s} {'A3 full':>8s} "
         f"{'A3 res':>7s} {'A4 clmp':>8s} {'A5 noise':>9s}  screens")
    print(h); print('-' * len(h))
    for sc in screens:
        print(f"{sc['condition']:26s} {sc['A1_worst_raw_cross_seed']:8.4f} {sc['A2_tmpl_median']:8.4f} "
              f"{sc['A2_tstruct_median']:8.4f} {sc['A3_self_full_max']:8.4f} {sc['A3_self_resid_max']:7.4f} "
              f"{sc['A4_clamp_share_median']:8.4f} {sc['A5_noise_share_median']:9.2e}  "
              f"{'PASS' if sc['passes_screens'] else 'STRUCK by ' + '; '.join(sc['struck_by'])}")
    static_conds = sorted({r['condition'] for r in runs if r['static']})
    print(f"\nstatic conditions (median epoch-to-epoch density correlation >= {STATIC_AT}): "
          f"{static_conds if static_conds else 'none'}")

    if args.json:
        with open(args.json, 'w') as fh:
            json.dump({'schema': 'halo-memory-pilot-staticness/1', 'author': 'Aldrin Payopay',
                       'thresholds': {'A1': DEGENERATE_AT, 'A2': TSTRUCT_AT, 'A3_full': STATIC_AT,
                                      'A3_resid': RESID_STATIC_AT, 'A4': CLAMP_AT, 'A5': IDENTITY_AT},
                       'runs': runs, 'cross_seed_pairs': pairs, 'screens': screens,
                       'static_conditions': static_conds}, fh, indent=1)
        print(f'wrote {args.json}')


if __name__ == '__main__':
    main()
