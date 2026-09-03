#!/usr/bin/env python3
"""memory_prereg_rotation.py - EXPLORATORY, not part of the registered decision rule.

The registered estimator does not de-rotate. Under Spinning Chladni the swarm turns
about 4.8 rad/s, so a relic that re-forms in a rotated orientation would score zero
in the fixed lab frame, and a null there licenses only "no lab-frame memory".

This asks the rotation-marginalised question: maximise the same correlation over
rotations of the relic about the y axis, and - this is the part that makes it a
test rather than a number - give the independent-seed null the SAME search. A
max-over-angles estimator has a positive bias floor (the port measured 0.045 to
0.088 at 5,000 particles); applying the search to both arms cancels it.

Reads the same run JSONs and meshes as memory_prereg_analyze.py. Writes
rotation.json beside them. It cannot change the verdict; it bounds what the
verdict is allowed to claim.

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import os
import sys
import numpy as np
from scipy.ndimage import rotate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_prereg_analyze import load_run, corr, N, H   # noqa: E402

N_ANGLES = 36            # 10 degree steps; the port used 72 at 5,000 particles


def rot_y(mesh, deg):
    """rotate about the y axis. mesh is indexed [z][y][x], so y is axis 1."""
    if deg == 0:
        return mesh
    return rotate(mesh, deg, axes=(0, 2), reshape=False, order=1, mode='constant', cval=0.0)


def best_over_rotation(rho, relic, f):
    best, best_deg = -2.0, None
    for i in range(N_ANGLES):
        deg = 360.0 * i / N_ANGLES
        v, _ = corr(rho, rot_y(relic, deg), f)
        if v == v and v > best:
            best, best_deg = v, deg
    return (None, None) if best_deg is None else (float(best), best_deg)


def main(indir):
    runs = {}
    for fn in sorted(os.listdir(indir)):
        if not fn.endswith('.json'):
            continue
        # A denylist of derived products rots: nullrate.json and robustness.json were
        # written by scripts that did not exist when this list did, and each one landed
        # here as a KeyError on 'mesh_file'. A run is what declares the run schema.
        with open(os.path.join(indir, fn)) as fh:
            head = json.load(fh)
        if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
            continue
        d = load_run(os.path.join(indir, fn))
        runs.setdefault((d['params']['preset'], d['params']['selfgrav'],
                         d['params']['gainloss']), []).append(d)

    out = []
    for key in sorted(runs):
        group = sorted(runs[key], key=lambda r: r['params']['seed'])
        for i, d in enumerate(group):
            partner = group[(i + 1) % len(group)] if len(group) > 1 else None
            rows = []
            for k in range(1, len(d['mesh'])):
                own, own_deg = best_over_rotation(d['mesh'][k], d['mesh'][k - 1], 2)
                row = {'epoch': k + 1, 'retained_rot': own, 'best_deg': own_deg}
                if partner is not None and k < len(partner['mesh']):
                    nul, nul_deg = best_over_rotation(d['mesh'][k], partner['mesh'][k - 1], 2)
                    row['seed_null_rot'] = nul
                    row['null_best_deg'] = nul_deg
                    if own is not None and nul is not None:
                        row['excess'] = own - nul
                rows.append(row)
            ex = [r['excess'] for r in rows if r.get('excess') is not None]
            out.append({'preset': key[0], 'selfgrav': key[1], 'gainloss': key[2],
                        'seed': d['params']['seed'], 'series': rows,
                        'mean_excess': float(np.mean(ex)) if ex else None,
                        'max_excess': float(np.max(ex)) if ex else None,
                        'n_excess': len(ex)})
            print(f"  {key[0]:12s} sg={key[1]:<5} gl={key[2]:<4} seed={d['params']['seed']:<6} "
                  f"mean excess {out[-1]['mean_excess']:+.4f}  max {out[-1]['max_excess']:+.4f}"
                  if ex else f"  {key} seed={d['params']['seed']} no excess computed")
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg')
    src = os.path.abspath(src)
    rows = main(src)
    allex = [r['mean_excess'] for r in rows if r['mean_excess'] is not None]
    summary = {'n_angles': N_ANGLES, 'runs': len(rows),
               'grand_mean_excess': float(np.mean(allex)) if allex else None,
               'max_run_mean_excess': float(np.max(allex)) if allex else None, 'runs_detail': rows}
    json.dump(summary, open(os.path.join(src, 'rotation.json'), 'w'), indent=1)
    print(f"\nrotation-marginalised excess over the independent-seed null, same search on both arms:")
    print(f"  grand mean {summary['grand_mean_excess']:+.4f}   worst run mean {summary['max_run_mean_excess']:+.4f}")
