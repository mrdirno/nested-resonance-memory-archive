#!/usr/bin/env python3
"""jeans_predict.py - linear force-balance prediction of the collapse coupling,
from the port itself: freeze the selfgrav=0 preset swarm at each H (settled,
t=29.5 s, and just after the t=20 epoch halving), solve its PM potential, and
find the selfgrav at which the self-force balances the anisotropic hubble push:
    sg_i = H * aniso_i * <p_i^2> / <-F_sg(1)_i * p_i>      per axis i
    sg_r = sum_i H aniso_i <p_i^2> / <-F_sg(1) . p>         radial (virial-like)
Under this null the threshold scales as H^1 times the H-dependence of 1/k(H),
k = SG_GAIN*delta/(3h^2) being the swarm's own contrast-driven spring constant."""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import PMSim, PRESET, PM_N, PM_CELL, SG_GAIN, pm_deposit, pm_source, jacobi, pm_force
from port2 import aniso_vec

HERE = os.path.dirname(os.path.abspath(__file__))
HS = [0.3, 0.6, 0.9, 1.2, 1.8, 2.4]
an = aniso_vec(PRESET['aniso'])
out = {}
print('aniso vector', an)
print('   H   snapshot      R_mean  delta_rms  k_eff   sg_x    sg_y    sg_z    sg_r')
for H in HS:
    sim = PMSim(dict(PRESET, particles=4000, hubble=H, selfgrav=0.0, dt=1 / 20))
    snaps = {}
    for fi in range(590):
        sim.frame(fi)
        if fi == 399:                       # t = 20.0: epoch halving applied this frame
            snaps['post-epoch t=20.0'] = sim.p.copy()
        if fi == 419:
            snaps['t=21.0'] = sim.p.copy()
    snaps['settled t=29.5'] = sim.p.copy()
    out[str(H)] = {}
    for name, p in snaps.items():
        rho = pm_deposit(p, True); src = pm_source(rho, 4000)
        phi = jacobi(np.zeros((PM_N,) * 3, np.float32), src, 4000, True)
        F1 = pm_force(phi, p, 1.0)
        num = H * an * (p ** 2).mean(axis=0)              # per-axis hubble work
        den = (-F1 * p).mean(axis=0)                      # per-axis self-gravity work at sg=1
        sg_axis = num / np.where(np.abs(den) > 1e-9, den, np.nan)
        sg_r = num.sum() / max(1e-9, den.sum())
        k_eff = den.sum() / (p ** 2).sum(axis=0).sum() * 4000  # <-F.p>/<p.p>
        d_rms = float(np.sqrt((src.astype(np.float64) ** 2).mean()))
        out[str(H)][name] = dict(R=float(np.linalg.norm(p, axis=1).mean()), delta_rms=d_rms,
                                 k_eff=float(k_eff), sg_axis=[float(v) for v in sg_axis], sg_r=float(sg_r))
        print('  %3.1f  %-18s %6.2f   %6.2f   %6.3f  %6.3f  %6.3f  %6.3f  %6.3f'
              % (H, name, out[str(H)][name]['R'], d_rms, k_eff, *sg_axis, sg_r))
json.dump(out, open(os.path.join(HERE, 'jeans_predict.json'), 'w'), indent=1)
# slope of the radial prediction (settled) vs H
hs = np.array(HS); ys = np.array([out[str(h)]['settled t=29.5']['sg_r'] for h in HS])
yy = np.array([out[str(h)]['settled t=29.5']['sg_axis'][1] for h in HS])
ye = np.array([out[str(h)]['post-epoch t=20.0']['sg_r'] for h in HS])
for lab, y in (('radial settled', ys), ('y-axis settled', yy), ('radial post-epoch', ye)):
    ok = np.isfinite(y) & (y > 0)
    sl = np.polyfit(np.log(hs[ok]), np.log(y[ok]), 1)[0]
    print('linear-balance prediction, %-18s: log-log slope %.2f, value at H=1.2: %.3f' % (lab, sl, y[HS.index(1.2)]))
