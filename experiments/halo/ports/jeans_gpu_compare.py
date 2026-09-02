#!/usr/bin/env python3
"""jeans_gpu_compare.py - the page's OWN potential mesh (read back by
jeans_gpu_phi.js after 20 s of the shell setup) against the numpy port solving
from the SAME read-back positions.  Also inverts the GPU potential through the
discrete Laplacian to recover the GPU's source and compares it with the port's
deposit -> checks cell mapping and axis order, not just the smooth answer."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import PM_N, PM_HALF, PM_CELL, pm_deposit, pm_source, jacobi, pm_force

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'jeans_gpu_phi.json')))
N = int(d['total'])
pos = np.array(d['pos'], dtype=np.float64).reshape(N, 3)
phi_gpu = np.array(d['phi'], dtype=np.float32).reshape(PM_N, PM_N, PM_N)
r = np.linalg.norm(pos, axis=1)
print('GPU: N=%d simTime=%.2f  |p| mean %.3f std %.3f (shell target 7.5)  finite %s'
      % (N, d['simTime'], r.mean(), r.std(), np.isfinite(pos).all()))
print('GPU phi: min %.4f max %.4f' % (phi_gpu.min(), phi_gpu.max()))

rho = pm_deposit(pos, half=True)
src = pm_source(rho, N)
# GPU-implied source from the discrete Laplacian of the GPU potential
P = np.zeros((PM_N + 2,) * 3, np.float64); P[1:-1, 1:-1, 1:-1] = phi_gpu
s6 = (P[2:, 1:-1, 1:-1] + P[:-2, 1:-1, 1:-1] + P[1:-1, 2:, 1:-1]
      + P[1:-1, :-2, 1:-1] + P[1:-1, 1:-1, 2:] + P[1:-1, 1:-1, :-2])
src_gpu = s6 - 6.0 * phi_gpu


def corr(a, b):
    a = a.ravel() - a.mean(); b = b.ravel() - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


print('source check (deposit indexing): corr(src_port, Laplacian(phi_gpu)) = %.4f'
      % corr(src, src_gpu))
for name, perm in (('xyz', (0, 1, 2)), ('yxz', (1, 0, 2)), ('zyx', (2, 1, 0)), ('xzy', (0, 2, 1))):
    print('   axis order %s: corr = %.4f' % (name, corr(np.transpose(src, perm), src_gpu)))
occ = src > 0
print('   occupied cells: port %d ; GPU-implied src>1 cells %d ; mean src in port-occupied cells: port %.2f gpu %.2f'
      % (occ.sum(), (src_gpu > 1).sum(), src[occ].mean(), src_gpu[occ].mean()))

zero = np.zeros((PM_N,) * 3, np.float32)
phi_page = jacobi(zero, src, 6 * 400, True)       # the page's 400 frames x 6 sweeps
phi_conv = jacobi(zero, src, 20000, False)


def rprof(phi, nb=16):
    idx = np.indices((PM_N,) * 3).reshape(3, -1).T
    rr = np.linalg.norm((idx + 0.5 - PM_N / 2) * PM_CELL, axis=1)
    b = np.floor(rr / PM_HALF * nb).astype(int); ok = b < nb
    prof = np.bincount(b[ok], weights=phi.ravel()[ok], minlength=nb) / np.maximum(1, np.bincount(b[ok], minlength=nb))
    return (np.arange(nb) + 0.5) / nb * PM_HALF, prof


for name, phi in (('port 2400 sweeps fp16', phi_page), ('port converged fp32', phi_conv)):
    diff = phi - phi_gpu
    print('%-24s corr %.5f | rms diff / rms gpu = %.4f | max|diff| %.3f (gpu range %.2f) | min at r=%.2f (gpu %.2f)'
          % (name, corr(phi, phi_gpu), np.sqrt((diff ** 2).mean()) / np.sqrt((phi_gpu ** 2).mean()),
             np.abs(diff).max(), phi_gpu.max() - phi_gpu.min(),
             rprof(phi)[0][np.argmin(rprof(phi)[1])], rprof(phi_gpu)[0][np.argmin(rprof(phi_gpu)[1])]))
# force felt by the particles themselves: GPU potential vs port potential
Fg = pm_force(phi_gpu, pos, 1.0); Fp = pm_force(phi_page, pos, 1.0)
print('per-particle force (selfgrav=1): corr %.5f, rms rel diff %.4f, median |F| gpu %.3f port %.3f'
      % (corr(Fg, Fp), np.sqrt(((Fg - Fp) ** 2).sum(1).mean()) / np.sqrt((Fg ** 2).sum(1).mean()),
         np.median(np.linalg.norm(Fg, axis=1)), np.median(np.linalg.norm(Fp, axis=1))))
rm, pg = rprof(phi_gpu); _, pp = rprof(phi_page)
print('\n   r     phi_gpu   phi_port')
for a, b, c in zip(rm, pg, pp):
    print('%6.2f  %9.4f  %9.4f' % (a, b, c))
