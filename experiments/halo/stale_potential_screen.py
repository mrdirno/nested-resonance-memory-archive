#!/usr/bin/env python3
"""stale_potential_screen.py - how hard does the relic's own potential pull on the zoomed matter?

At every epoch boundary the page rescales the particles by 1/2 about the centre, but its
self-gravity solver (32^3 particle mesh, six Jacobi sweeps per tick, warm-started from the
previous potential) is solved on the pre-zoom positions on the zoom tick and never rescaled.
For the first second or so of every epoch the zoomed matter therefore moves in the potential
of the UNZOOMED relic. This screen asks, on the recorded meshes, how large that pull is.

For every boundary of every run it solves the page's Poisson equation exactly (unit-spacing
7-point Laplacian, Dirichlet zero outside the mesh, source = density contrast rho/mean - 1,
the page's own normalisation) for two fields: the relic (mesh k-1, the stale warm start) and
its x2 zoomed image placed in the inner block (the matter just after the zoom-out). It
reports, weighted by the zoomed matter, the net force along the spin axis y of each potential
(force = -sg * 14 * central difference / (2 * cell), the page's force law), the page's Hubble
push along y on the zoomed centre of mass, and the relic's north/south split. It is STATIC:
the matter is not moved, the Jacobi lag is not replayed, and nothing here is a measurement of
what carries the hemisphere — it is the reason the Ring 30 pre-registration
(analysis/2026-09-22_relic_intervention.md) asks the question. Numbers only.

    python3 experiments/halo/stale_potential_screen.py DIR --json OUT

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, json, os, sys
import numpy as np
from scipy.fft import dstn, idstn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_estimator_qualify as mq  # noqa: E402  (frozen; read only)

N = 32
EXTENT = 15.0
PM_CELL = 2 * EXTENT * 1.02 / N
SG_GAIN = 14.0
HUBBLE, ANISO = 1.2, 0.55                      # the spinchladni preset: Hubble stretched along y
LAM1 = 2 * np.cos(np.pi * (np.arange(N) + 1) / (N + 1)) - 2
LAM = LAM1[:, None, None] + LAM1[None, :, None] + LAM1[None, None, :]


def solve(rho):
    """Exact solution of lap(phi) = rho/mean - 1, phi = 0 outside the mesh."""
    return idstn(dstn(rho / rho.mean() - 1.0, type=1) / LAM, type=1)


def grad_y(phi):
    """Central difference along mesh axis 1 (y) with zero outside, arrays [z][y][x]."""
    p = np.pad(phi, 1)
    return p[1:-1, 2:, 1:-1] - p[1:-1, :-2, 1:-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('--json', required=True)
    a = ap.parse_args()
    runs, _ = mq.load_grid(a.dir)
    ycell = (np.arange(N) - 15.5)[None, :, None]
    out = []
    for key in sorted(runs):
        sg = key[1]
        for g in runs[key]:
            m = g['mesh'].astype(np.float64)
            rows = []
            for k in range(1, m.shape[0]):          # the boundary between mesh k-1 (relic) and mesh k
                rel = m[k - 1]
                zoomed = np.zeros_like(rel)
                zoomed[8:24, 8:24, 8:24] = mq.predicted(rel, 2)
                f_stale = -sg * SG_GAIN * grad_y(solve(rel)) / (2 * PM_CELL)
                f_fresh = -sg * SG_GAIN * grad_y(solve(zoomed)) / (2 * PM_CELL)
                w = zoomed / zoomed.sum()
                y_com = float((w * ycell).sum()) * PM_CELL
                rows.append({'boundary': k,
                             'relic_split': float((rel[:, 16:, :].sum() - rel[:, :16, :].sum()) / rel.sum()),
                             'net_Fy_stale': float((w * f_stale).sum()), 'net_Fy_fresh': float((w * f_fresh).sum()),
                             'hubble_Fy_on_com': HUBBLE * (1 + 1.3 * ANISO) * y_com, 'y_com_zoomed': y_com})
            arr = np.array([[r['relic_split'], r['net_Fy_stale'], r['net_Fy_fresh'], r['hubble_Fy_on_com']] for r in rows])
            summary = {'boundaries': len(rows),
                       'stale_pull_toward_relic_hemisphere': int((np.sign(arr[:, 1]) == np.sign(arr[:, 0])).sum()),
                       'median_abs_net_Fy_stale': float(np.median(np.abs(arr[:, 1]))),
                       'median_abs_net_Fy_fresh': float(np.median(np.abs(arr[:, 2]))),
                       'median_abs_hubble_Fy_on_com': float(np.median(np.abs(arr[:, 3])))}
            print(f"sg{sg:g} seed {g['seed']}: stale pull toward the relic's hemisphere at "
                  f"{summary['stale_pull_toward_relic_hemisphere']}/{len(rows)} boundaries; median |net Fy| stale "
                  f"{summary['median_abs_net_Fy_stale']:.1f}, fresh {summary['median_abs_net_Fy_fresh']:.2f}, "
                  f"Hubble on the centre of mass {summary['median_abs_hubble_Fy_on_com']:.2f}")
            out.append({'condition': {'preset': key[0], 'selfgrav': sg, 'gainloss': key[2]}, 'seed': g['seed'],
                        'summary': summary, 'rows': rows})
    with open(a.json, 'w') as fh:
        src = os.path.abspath(a.dir)
        repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
        json.dump({'source': os.path.relpath(src, repo) if src.startswith(repo + os.sep) else os.path.basename(src),
                   'static': True, 'runs': out}, fh, indent=1)
    print(f'wrote {a.json}')


if __name__ == '__main__':
    main()
