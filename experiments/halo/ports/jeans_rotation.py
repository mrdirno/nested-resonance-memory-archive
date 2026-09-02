#!/usr/bin/env python3
"""jeans_rotation.py - what actually opposes self-gravity in the preset?
For the frozen selfgrav=0 swarm (settled t=29.5 and just after the t=20 epoch
halving) compare, per particle and averaged, the in-plane (x-z) accelerations:
  centrifugal  a_c = v_phi^2 / rho          (helix + Lorentz driven spin about y)
  hubble       a_H = H * 0.6425 * rho
  self-gravity g_rho = -(F_sg(sg=1) . rho_hat)   from the port's PM solve
and along y: a_Hy = H*1.715*|y| vs g_y.  sg_X = a_X / g is the coupling at
which gravity balances X."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import PMSim, PRESET, PM_N, pm_deposit, pm_source, jacobi, pm_force
from port2 import aniso_vec

HERE = os.path.dirname(os.path.abspath(__file__))
an = aniso_vec(PRESET['aniso'])
out = {}
print('   H   snapshot           R     Omega_y  <a_c>   <a_Hxz>  <g_rho>  sg_rot  sg_Hxz | <a_Hy>  <g_y>  sg_Hy')
for H in (0.3, 1.2, 2.4):
    sim = PMSim(dict(PRESET, particles=4000, hubble=H, selfgrav=0.0, dt=1 / 20))
    snaps = {}
    for fi in range(590):
        sim.frame(fi)
        if fi == 399:
            snaps['post-epoch t=20.0'] = (sim.p.copy(), sim.v.copy())
        if fi == 409:
            snaps['t=20.5'] = (sim.p.copy(), sim.v.copy())
    snaps['settled t=29.5'] = (sim.p.copy(), sim.v.copy())
    out[str(H)] = {}
    for name, (p, v) in snaps.items():
        rho = np.maximum(np.hypot(p[:, 0], p[:, 2]), 1e-6)
        rhat = np.stack([p[:, 0] / rho, np.zeros(len(p)), p[:, 2] / rho], 1)
        vphi = (p[:, 0] * v[:, 2] - p[:, 2] * v[:, 0]) / rho
        Omega = float((rho * vphi).sum() / (rho ** 2).sum())
        a_c = vphi ** 2 / rho
        a_H = H * an[0] * rho
        dens = pm_deposit(p, True); src = pm_source(dens, 4000)
        phi = jacobi(np.zeros((PM_N,) * 3, np.float32), src, 4000, True)
        F1 = pm_force(phi, p, 1.0)
        g_rho = -(F1 * rhat).sum(1)
        g_y = -F1[:, 1] * np.sign(p[:, 1])
        a_Hy = H * an[1] * np.abs(p[:, 1])
        row = dict(R=float(np.linalg.norm(p, axis=1).mean()), Omega=Omega,
                   a_c=float(a_c.mean()), a_H=float(a_H.mean()), g_rho=float(g_rho.mean()),
                   sg_rot=float(a_c.mean() / g_rho.mean()), sg_H=float(a_H.mean() / g_rho.mean()),
                   a_Hy=float(a_Hy.mean()), g_y=float(g_y.mean()), sg_Hy=float(a_Hy.mean() / g_y.mean()),
                   speed=float(np.linalg.norm(v, axis=1).mean()))
        out[str(H)][name] = row
        print('  %3.1f  %-18s %5.2f  %7.3f  %6.2f  %6.2f  %7.2f  %6.3f  %6.3f | %6.2f  %6.2f  %6.3f'
              % (H, name, row['R'], Omega, row['a_c'], row['a_H'], row['g_rho'], row['sg_rot'],
                 row['sg_H'], row['a_Hy'], row['g_y'], row['sg_Hy']))
json.dump(out, open(os.path.join(HERE, 'jeans_rotation.json'), 'w'), indent=1)
