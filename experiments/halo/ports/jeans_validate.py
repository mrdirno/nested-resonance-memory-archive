#!/usr/bin/env python3
"""jeans_validate.py - static validation of the PM port (no dynamics).
1. thin shell at r = 7.5: potential minimum must sit within one cell of 7.5
2. force points toward the shell from both sides
3. discrete Laplacian residual of the converged phi vs the source
4. uniform ball: effective spring constant of the self-force vs the analytic
   k = SG_GAIN * delta / (3 h^2)  (from grad^2 phi = delta/h^2)
"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import (PM_N, PM_HALF, PM_CELL, SG_GAIN, pm_deposit, pm_source,
                      jacobi, pm_force, laplacian_residual)


def sphere_dirs(N, rng):
    u = rng.random(N) * 2 - 1
    ph = rng.random(N) * 2 * np.pi
    s = np.sqrt(1 - u * u)
    return np.stack([s * np.cos(ph), u, s * np.sin(ph)], axis=1)


def radial_profile(phi, nb):
    idx = np.indices((PM_N,) * 3).reshape(3, -1).T
    x = (idx + 0.5 - PM_N / 2) * PM_CELL
    r = np.linalg.norm(x, axis=1)
    b = np.floor(r / PM_HALF * nb).astype(int)
    ok = b < nb
    sums = np.bincount(b[ok], weights=phi.ravel()[ok], minlength=nb)
    cnt = np.bincount(b[ok], minlength=nb)
    prof = sums / np.maximum(cnt, 1)
    rmid = (np.arange(nb) + 0.5) / nb * PM_HALF
    return rmid, prof, cnt, r.reshape(phi.shape)


out = {}
rng = np.random.default_rng(1)
print('cell size h = %.5f, mesh half-width %.4f' % (PM_CELL, PM_HALF))
for N in (4000, 65536):
    p = 7.5 * sphere_dirs(N, rng)
    rho = pm_deposit(p, half=True)
    src = pm_source(rho, N)
    for label, iters, half in (('page-protocol 400x6 sweeps fp16', 2400, True),
                               ('converged 20000 sweeps fp16', 20000, True),
                               ('converged 20000 sweeps fp32', 20000, False)):
        t = time.time()
        phi = jacobi(np.zeros((PM_N,) * 3, np.float32), src, iters, half)
        dt = time.time() - t
        rmid, prof, cnt, rcell = radial_profile(phi, 16)     # 16 bins = one cell wide
        rmin16 = float(rmid[np.argmin(prof)])
        rargmin = float(rcell.ravel()[np.argmin(phi.ravel())])
        resid = laplacian_residual(phi, src)
        # force direction on either side of the shell
        d = sphere_dirs(2000, rng)
        fin = pm_force(phi, 6.0 * d, 1.0); fout = pm_force(phi, 9.0 * d, 1.0)
        fr_in = float(np.einsum('ij,ij->i', fin, d).mean())
        fr_out = float(np.einsum('ij,ij->i', fout, d).mean())
        key = 'shell N=%d %s' % (N, label)
        out[key] = dict(rmin_binned=rmin16, r_argmin_cell=rargmin,
                        off_cells=abs(rmin16 - 7.5) / PM_CELL,
                        resid=resid, Fr_at_6=fr_in, Fr_at_9=fr_out,
                        phi_min=float(phi.min()), phi_max=float(phi.max()),
                        profile=[[float(a), float(b)] for a, b in zip(rmid, prof)])
        print('%-48s phi-min at r=%.2f (argmin cell r=%.2f) -> %.2f cells from 7.5 | '
              'resid %.1e | F.r at r=6: %+.3f, at r=9: %+.3f | %.1fs'
              % (key, rmin16, rargmin, abs(rmin16 - 7.5) / PM_CELL, resid, fr_in, fr_out, dt))

# uniform ball: measured spring constant vs analytic
N = 65536
Rb = 12.0
d = sphere_dirs(N, rng)
p = d * (Rb * np.cbrt(rng.random(N)))[:, None]
rho = pm_deposit(p, True); src = pm_source(rho, N)
phi = jacobi(np.zeros((PM_N,) * 3, np.float32), src, 20000, True)
Vbox = (2 * PM_HALF) ** 3
delta = Vbox / (4 / 3 * math.pi * Rb ** 3) - 1
k_analytic = SG_GAIN * delta / (3 * PM_CELL ** 2)
rows = []
for rr in (2.0, 4.0, 6.0, 8.0, 10.0):
    q = rr * sphere_dirs(3000, rng)
    F = pm_force(phi, q, 1.0)
    fr = float(np.einsum('ij,ij->i', F, q / rr).mean())
    rows.append((rr, fr, -fr / rr))
    print('uniform ball R=12: r=%4.1f  F_r=%+8.3f  k_eff=%.3f  (analytic k=%.3f, delta=%.3f)'
          % (rr, fr, -fr / rr, k_analytic, delta))
out['uniform_ball'] = dict(delta=delta, k_analytic=k_analytic,
                           rows=[[float(a), float(b), float(c)] for a, b, c in rows])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'jeans_validate.json'), 'w'), indent=1)
