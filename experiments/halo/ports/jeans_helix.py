#!/usr/bin/env python3
"""jeans_helix.py - falsification test of the rotational-support reading:
at fixed H=1.2, vary the helix slider (which sets the spin Omega about y).
Prediction from the frozen no-gravity swarm right after the t=20 epoch:
    sg_pred = <v_phi^2/rho> / <-F_sg(1).rho_hat>
Measurement: bisection threshold (R_win < R0/2) as in jeans_sweep."""
import json, os, sys
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_sweep import Job
from jeans_pm import PMSim, PRESET, PM_N, pm_deposit, pm_source, jacobi, pm_force, run_case
HERE = os.path.dirname(os.path.abspath(__file__))
HELIX = [0.0, 0.4, 0.8, 1.2]


def predict(helix):
    sim = PMSim(dict(PRESET, particles=4000, hubble=1.2, helix=helix, selfgrav=0.0, dt=1 / 20))
    for fi in range(400):
        sim.frame(fi)
    p, v = sim.p, sim.v                      # just after the t=20 epoch halving
    rho = np.maximum(np.hypot(p[:, 0], p[:, 2]), 1e-6)
    rhat = np.stack([p[:, 0] / rho, np.zeros(len(p)), p[:, 2] / rho], 1)
    vphi = (p[:, 0] * v[:, 2] - p[:, 2] * v[:, 0]) / rho
    Omega = float((rho * vphi).sum() / (rho ** 2).sum())
    dens = pm_deposit(p, True); src = pm_source(dens, 4000)
    phi = jacobi(np.zeros((PM_N,) * 3, np.float32), src, 4000, True)
    F1 = pm_force(phi, p, 1.0)
    g = -(F1 * rhat).sum(1).mean()
    a_c = (vphi ** 2 / rho).mean()
    a_H = (1.2 * 0.6425 * rho).mean()
    return dict(helix=helix, Omega=Omega, a_c=float(a_c), g_rho=float(g), a_H=float(a_H),
                sg_rot=float(a_c / g), sg_H=float(a_H / g), sg_rot_plus_H=float((a_c + a_H) / g))


if __name__ == '__main__':
    with Pool(4) as pool:
        preds = pool.map(predict, HELIX)
        jobs = [Job('helix%g' % h, dict(H=1.2, seed=12345, state=dict(helix=h)), 'bisect') for h in HELIX if h != 0.8]
        by = {j.name: j for j in jobs}
        while True:
            batch = [(j.name, c) for j in jobs for c in j.pending()]
            if not batch:
                break
            for (name, c), r in zip(batch, pool.map(run_case, [c for _, c in batch], chunksize=1)):
                by[name].feed(r)
    print(' helix  Omega_y  <a_c>  <a_Hxz>  <g_rho>  sg_rot(pred)  sg_rot+H   measured thr')
    out = []
    for pr in preds:
        j = by.get('helix%g' % pr['helix'])
        s = j.summary() if j else None
        thr = s['thr'] if s else 0.5156
        err = s['err'] if s else 0.0156
        print(' %4.1f   %6.3f  %6.1f  %6.2f   %6.1f   %8.3f      %6.3f     %.4f +/- %.4f%s'
              % (pr['helix'], pr['Omega'], pr['a_c'], pr['a_H'], pr['g_rho'], pr['sg_rot'],
                 pr['sg_rot_plus_H'], thr, err, '' if j else '  (from main sweep)'))
        out.append(dict(pr, thr=thr, err=err, R0=(s['R0'] if s else 12.29)))
    json.dump(out, open(os.path.join(HERE, 'jeans_helix.json'), 'w'), indent=1)
