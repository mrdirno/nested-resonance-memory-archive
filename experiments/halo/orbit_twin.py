#!/usr/bin/env python3
"""numpy twin of the page's "Two clumps in orbit" experiment.

The page's operator, rebuilt here: nearest-cell deposit on a 32^3 mesh
(cell = floor((p / PM_HALF) / 2 + 1/2) * 32, the shader's pmCellOf), contrast
count / mean - 1, the 7-point Laplacian in cell units with the potential zero
one cell outside the mesh, solved exactly by a sine transform (DST-I) or by six
warm-started Jacobi sweeps a tick, the pull -SG_GAIN * s * (phi[c+1] - phi[c-1])
/ (2 PM_CELL) at the particle's cell, the 500 ceiling, semi-implicit Euler at
tick 1/20. Two rigid clumps of n particles at the centres of cells (12,16,16)
and (20,16,16), i.e. d = 4 cells either side of the centre of the middle cell,
the clump cell reads contrast 16383 over a -1 background; velocities +-v_circ
along z from the exact pull on the +x clump (F = 14.58 at s = 0.05, v = 7.47,
T = 3.218 s, 0.39 cells per tick). Measured every 0.25 s: the unwrapped angle
of the separation against time (period), the separation's slope (drift per
orbit), the first sample under one cell (merge), the cells crossed per tick,
the wander of the pair's midpoint. Also the cell-jump band: the exact radial
pull sampled around the starting circle, the pair placed cell by cell.

Usage: python3 experiments/halo/orbit_twin.py [--json] [--seconds 10] [--s 0.05] [--d 4]
Requires numpy only; about 3 s.
"""
import argparse
import json

import numpy as np

N = 32; EXTENT = 15.0; PM_HALF = EXTENT * 1.02; PM_CELL = 2 * PM_HALF / N; SG = 14.0; TICK = 0.05
_i = np.arange(N)
_S = np.sin(np.pi * np.outer(_i + 1, _i + 1) / (N + 1))
_lam = 2 * np.cos(np.pi * (_i + 1) / (N + 1)) - 2
_L = _lam[:, None, None] + _lam[None, :, None] + _lam[None, None, :]


def dst3(a):
    a = np.tensordot(_S, a, axes=([1], [0]))
    a = np.tensordot(_S, a, axes=([1], [1])).transpose(1, 0, 2)
    a = np.tensordot(_S, a, axes=([1], [2])).transpose(1, 2, 0)
    return a


def solve_exact(delta):
    return dst3(dst3(delta) * (2 / (N + 1)) ** 3 / _L)


def jacobi(delta, phi, sweeps=6):
    for _ in range(sweeps):
        p = np.pad(phi, 1)
        s = (p[2:, 1:-1, 1:-1] + p[:-2, 1:-1, 1:-1] + p[1:-1, 2:, 1:-1] + p[1:-1, :-2, 1:-1] + p[1:-1, 1:-1, 2:] + p[1:-1, 1:-1, :-2])
        phi = (s - delta) / 6
    return phi


def cell(p):
    return np.floor((p / PM_HALF * 0.5 + 0.5) * N).astype(int)


def cc(u):
    """chamber coordinate of continuous cell coordinate u (cell i spans [i, i+1))"""
    return (u / N - 0.5) * 2 * PM_HALF


def source(cells, weight):
    d = -np.ones((N, N, N))
    for c in cells:
        if np.all(c >= 0) and np.all(c < N):
            d[tuple(c)] += weight
    return d


def gather(phi, c):
    def at(q):
        if np.any(q < 0) or np.any(q > N - 1):
            return 0.0
        return phi[tuple(q)]
    g = np.zeros(3)
    for ax in range(3):
        e = np.zeros(3, int); e[ax] = 1
        g[ax] = at(c + e) - at(c - e)
    return -g / (2 * PM_CELL)


def ceiling(F):
    m = np.linalg.norm(F)
    return F * (500 / m) if m > 500 else F


def setup(s, d, n):
    weight = n * N ** 3 / (2 * n)
    cA = np.array([N // 2 - d, N // 2, N // 2]); cB = np.array([N // 2 + d, N // 2, N // 2])
    O = np.array([cc(N // 2 + 0.5)] * 3)
    pA = np.array([cc(cA[0] + 0.5), O[1], O[2]]); pB = np.array([cc(cB[0] + 0.5), O[1], O[2]])
    phi = solve_exact(source([cA, cB], weight))
    FA = SG * s * gather(phi, cA); FB = SG * s * gather(phi, cB)
    r = d * PM_CELL; Fr = -FB[0]; vcirc = np.sqrt(Fr * r); Tpred = 2 * np.pi * r / vcirc
    # the cell-jump band: the exact radial pull around the starting circle, the pair as mirror images through O
    frs = []
    for th in np.linspace(0, 2 * np.pi, 72, endpoint=False):
        q = O + r * np.array([np.cos(th), 0, np.sin(th)]); q2 = 2 * O - q
        c1, c2 = cell(q), cell(q2)
        F = SG * s * gather(solve_exact(source([c1, c2], weight)), c1)
        frs.append(-F @ ((q - O) / r))
    frs = np.array(frs)
    band = [float(np.sqrt(Fr / frs.max())), float(np.sqrt(Fr / frs.min()))]
    return dict(weight=weight, cA=cA, cB=cB, O=O, pA=pA, pB=pB, FA=FA, FB=FB, r=r, Fr=Fr, vcirc=vcirc, Tpred=Tpred, band=band,
                jumps_pred=2 * vcirc * TICK / PM_CELL, force_min=float(frs.min()), force_max=float(frs.max()))


def run(cfg, s, solver, seconds=10.0, sample=0.25, warm_solves=400):
    weight, O = cfg['weight'], cfg['O']
    p = np.array([cfg['pA'], cfg['pB']]); v = np.array([[0, 0, -cfg['vcirc']], [0, 0, cfg['vcirc']]], dtype=float)
    phi_j = None
    if solver != 'exact':
        phi_j = np.zeros((N, N, N))
        for _ in range(warm_solves):
            phi_j = jacobi(source([cfg['cA'], cfg['cB']], weight), phi_j, 6)
    t = 0.0; rows = []; crossings = 0; ticks = 0; prev = [cell(p[0]), cell(p[1])]
    nsteps = int(round(seconds / TICK)); every = int(round(sample / TICK))
    for k in range(nsteps + 1):
        if k % every == 0:
            rows.append((t, p.copy()))
        if k == nsteps:
            break
        cA_, cB_ = cell(p[0]), cell(p[1])
        dlt = source([cA_, cB_], weight)
        if solver == 'exact':
            ph = solve_exact(dlt)
        else:
            phi_j = jacobi(dlt, phi_j, 6); ph = phi_j
        F = np.array([ceiling(SG * s * gather(ph, cA_)), ceiling(SG * s * gather(ph, cB_))])
        v = v + F * TICK; p = p + v * TICK; t += TICK; ticks += 1
        for j in range(2):
            rr = np.linalg.norm(p[j])
            if rr > EXTENT:
                p[j] *= EXTENT / rr
        nc = [cell(p[0]), cell(p[1])]
        crossings += int(np.any(nc[0] != prev[0])) + int(np.any(nc[1] != prev[1])); prev = nc
    ts = np.array([r_[0] for r_ in rows]); P = np.array([r_[1] for r_ in rows])
    sep = P[:, 1] - P[:, 0]; dist = np.linalg.norm(sep, axis=1); mid = np.linalg.norm((P[:, 1] + P[:, 0]) / 2 - O, axis=1)
    th = np.unwrap(np.arctan2(sep[:, 2], sep[:, 0]))
    ok = dist > 0.5 * dist[0]
    m = int(np.argmin(ok)) if (~ok).any() else len(ok)
    under = np.where(dist < PM_CELL)[0]
    merge = float(ts[under[0]]) if len(under) else None
    orbits = abs(th[max(0, m - 1)]) / (2 * np.pi)
    if m < 3 or orbits < 0.25:
        Tm = drift = float('nan')
    else:
        A = np.vstack([ts[:m], np.ones(m)]).T
        slope = np.linalg.lstsq(A, th[:m], rcond=None)[0][0]; Tm = 2 * np.pi / abs(slope)
        drift = np.linalg.lstsq(A, dist[:m], rcond=None)[0][0] * Tm
    return dict(solver=solver, T=Tm, ratio=Tm / cfg['Tpred'], drift=drift, merge=merge, orbits=float(orbits),
                jumps=crossings / ticks, ticks=ticks, centre=float(mid.max()), sep0=float(dist[0]), sep=float(dist[-1]),
                sep_min=float(dist.min()), sep_max=float(dist.max()), t=float(ts[-1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='print one JSON line last')
    ap.add_argument('--seconds', type=float, default=10.0)
    ap.add_argument('--s', type=float, default=0.05)
    ap.add_argument('--d', type=int, default=4)
    ap.add_argument('--n', type=int, default=512)
    a = ap.parse_args()
    cfg = setup(a.s, a.d, a.n)
    print(f'cells ({16 - a.d},16,16) and ({16 + a.d},16,16), {a.n} particles each, s = {a.s}: pull on the +x clump {cfg["Fr"]:.3f} '
          f'(on its partner {abs(cfg["FA"][0]):.3f}), orbit speed {cfg["vcirc"]:.3f}, radius {cfg["r"]:.3f}, predicted period {cfg["Tpred"]:.3f} s, '
          f'{cfg["vcirc"] * TICK / PM_CELL:.2f} cells per tick; pull around the circle {cfg["force_min"]:.2f}..{cfg["force_max"]:.2f} '
          f'so the cell jumps allow a ratio in [{cfg["band"][0]:.3f}, {cfg["band"][1]:.3f}]')
    out = dict(Tpred=float(cfg['Tpred']), vcirc=float(cfg['vcirc']), Fr=float(cfg['Fr']), FA=cfg['FA'].tolist(), FB=cfg['FB'].tolist(),
               r=float(cfg['r']), band=cfg['band'], jumps_pred=float(cfg['jumps_pred']), phases={})
    for solver in ('jacobi', 'exact'):
        r = run(cfg, a.s, solver, a.seconds)
        out['phases'][solver] = r
        print(f'{solver:7s}: period {r["T"]:.3f} s (ratio {r["ratio"]:.3f}), drift {r["drift"]:+.3f} per orbit, merge {r["merge"]}, '
              f'{r["orbits"]:.2f} orbits, {r["jumps"]:.2f} cell jumps per tick, centre moved {r["centre"]:.3f}, separation {r["sep_min"]:.2f}..{r["sep_max"]:.2f}')
    if a.json:
        def clean(o):   # NaN is not JSON: a missing period is null
            if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
            if isinstance(o, list): return [clean(v) for v in o]
            if isinstance(o, float) and o != o: return None
            return o
        print(json.dumps(clean(out)))


if __name__ == '__main__':
    main()
