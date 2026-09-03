#!/usr/bin/env python3
"""Load a snapshot saved by the Resonance Chamber's "Save NPZ" button.

Usage: python3 experiments/halo/load_chamber_npz.py resonance-chamber-snapshot.npz

Prints the shapes, checks that every number is finite, recomputes the density
by a histogram on the page's own grid (32 cells of PM_CELL across the mesh,
cell c = floor(p / PM_CELL + 16)) and reports its correlation with the exported
density (nearest-cell deposit: above 0.99, the only differences being particles
that sit within float rounding of a cell edge; cloud-in-cell shares each
particle among eight cells, so the correlation is lower there), then applies
the page's Poisson operator to the exported potential and reports the residual
against the contrast (six sweeps a tick leave some; the exact solver leaves
float rounding). The last line is a JSON summary. Requires numpy only.
"""
import json
import sys
import zipfile

import numpy as np

META_KEYS = ('step', 'simTime', 'EXTENT', 'PM_HALF', 'PM_CELL', 'SG_GAIN', 'tick', 'ceiling', 'force', 'state')


def main(path):
    z = np.load(path)
    pos, vel, dens, pot = z['positions'], z['velocities'], z['density'], z['potential']
    with zipfile.ZipFile(path) as zf:
        meta = json.loads(zf.read('meta.json'))
    finite = all(np.isfinite(a).all() for a in (pos, vel, dens, pot))
    N = int(meta['PM_N'])
    shapes_ok = (pos.ndim == 2 and pos.shape[1] == 3 and vel.shape == pos.shape and dens.shape == (N, N, N) and pot.shape == (N, N, N)
                 and pos.dtype == np.float32 and vel.dtype == np.float32 and dens.dtype == np.float32 and pot.dtype == np.float32)
    meta_ok = all(k in meta for k in META_KEYS) and meta['ceiling'] == 500
    print(f'positions {pos.shape} {pos.dtype}, velocities {vel.shape} {vel.dtype}, density {dens.shape} {dens.dtype}, potential {pot.shape} {pot.dtype}')
    print(f'all finite: {finite}; step {meta["step"]}, sim time {meta["simTime"]} s, self-gravity {meta["selfgrav"]}, '
          f'solver {meta.get("solver", "?")}, mesh {meta.get("assign", "?")}, {meta["particles"]} particles')
    print(f'radius: max {np.linalg.norm(pos, axis=1).max():.3f} (wall at {meta["EXTENT"]}); speed: max {np.linalg.norm(vel, axis=1).max():.3f}')
    cell = float(meta['PM_CELL'])
    edges = (np.arange(N + 1) - N / 2) * cell
    H, _ = np.histogramdd(pos.astype(np.float64), bins=(edges, edges, edges))
    out = dict(particles=int(pos.shape[0]), finite=bool(finite), shapes_ok=bool(shapes_ok), meta_ok=bool(meta_ok),
               meta_keys=[k for k in META_KEYS if k in meta], step=meta['step'], simTime=meta['simTime'],
               density_total=float(dens.sum()), histogram_total=float(H.sum()))
    if dens.any():
        corr = float(np.corrcoef(H.ravel(), dens.astype(np.float64).ravel())[0, 1])
        diff = int(round(np.abs(H - dens).sum() / 2))
        print(f'density: {dens.sum():.0f} particles on the mesh, histogram {H.sum():.0f}; correlation {corr:.6f}; '
              f'{diff} particles land in a different cell (float rounding at cell edges, or cloud-in-cell sharing)')
        out['correlation'] = corr; out['cells_differing_particles'] = diff
    else:
        print('density is all zeros: self-gravity was off when the snapshot was saved')
    if pot.any():
        mean = pos.shape[0] / N ** 3
        delta = dens.astype(np.float64) / mean - 1.0
        p = np.pad(pot.astype(np.float64), 1)
        lap = (p[2:, 1:-1, 1:-1] + p[:-2, 1:-1, 1:-1] + p[1:-1, 2:, 1:-1] + p[1:-1, :-2, 1:-1]
               + p[1:-1, 1:-1, 2:] + p[1:-1, 1:-1, :-2] - 6 * pot)
        resid = float(np.sqrt(np.mean((lap - delta) ** 2)) / np.sqrt(np.mean(delta ** 2)))
        print(f'potential: range {pot.min():.3f} to {pot.max():.3f}; Poisson residual rms(L phi - contrast) / rms(contrast) = {resid:.4f}')
        out['poisson_residual'] = resid
    print(json.dumps(out))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1])
