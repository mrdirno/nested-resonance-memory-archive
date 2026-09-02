#!/usr/bin/env python3
"""jeans_clamp.py - does the |F|<=500 clamp set the collapsed blob's size?
sg=1.0, H=1.2, preset, 3 seeds:  (a) clamp 500, dt 1/20  (b) clamp 2000, dt 1/80
(dv per step held at 25)  (c) clamp 500, dt 1/80.  Blob metrics in mesh cells."""
import json, math, os, sys
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import PMSim, PRESET, PM_N, PM_CELL, contrast24, pm_cell_of
from port2 import EXTENT, RESTITUTION
HERE = os.path.dirname(os.path.abspath(__file__))


class ClampSim(PMSim):
    """PMSim with the velocity-pass clamp as a parameter (port2 hard-codes 500)."""
    def __init__(self, state):
        st = dict(state)
        self.clamp = float(st.pop('clamp', 500.0))
        super().__init__(st)

    def raw_pass(self):
        self.pm_solve()
        st, dt = self.st, self.dt
        F, SB = self.force(self.p, self.v)
        self.lastS = SB
        fmag = np.linalg.norm(F, axis=1)
        over = fmag > self.clamp
        self.clamp_frac = float(over.mean())
        self.fsg_over = float((np.linalg.norm(self.Fsg, axis=1) > self.clamp).mean()) if self.Fsg is not None else 0.0
        if over.any():
            F[over] *= (self.clamp / fmag[over])[:, None]
        self.lastF = F
        self.v = (self.v + F * dt) * math.exp(-st['damping'] * dt)
        if st['boundary'] == 'reflect':
            pn = self.p + self.v * dt
            rn = np.linalg.norm(pn, axis=1)
            out = rn > EXTENT
            if out.any():
                nrm = pn[out] / rn[out][:, None]
                vr = np.einsum('ij,ij->i', self.v[out], nrm)
                hit = vr > 0
                if hit.any():
                    idx = np.where(out)[0][hit]
                    self.v[idx] -= (1.0 + RESTITUTION) * vr[hit][:, None] * nrm[hit]
        self.v *= self.rescale
        self.p = self.p + self.v * dt
        rr = np.linalg.norm(self.p, axis=1)
        out = rr > EXTENT
        if out.any():
            if st['boundary'] == 'reflect':
                self.p[out] *= (EXTENT / rr[out])[:, None]
            else:
                e = np.minimum(rr[out] - EXTENT, EXTENT * 0.5)
                self.p[out] = -self.p[out] * ((EXTENT - e) / rr[out])[:, None]
        self.p *= self.rescale


def blob_metrics(p):
    c = pm_cell_of(p)
    flat = (c[:, 0] * PM_N + c[:, 1]) * PM_N + c[:, 2]
    k = np.bincount(flat, minlength=PM_N ** 3)
    order = np.argsort(k)[::-1]
    cum = np.cumsum(k[order]) / len(p)
    cells50 = int(np.searchsorted(cum, 0.5) + 1)
    cells90 = int(np.searchsorted(cum, 0.9) + 1)
    top = order[0]
    tc = np.array([top // (PM_N * PM_N), (top // PM_N) % PM_N, top % PM_N])
    inblock = np.all(np.abs(c - tc) <= 1, axis=1)          # densest cell + 26 neighbours
    q = p[inblock]
    rms_block = float(np.sqrt(((q - q.mean(0)) ** 2).sum(1).mean())) if len(q) > 1 else 0.0
    cm = p.mean(0)
    return dict(occupied=int((k > 0).sum()), cells50=cells50, cells90=cells90,
                max_cell_frac=float(k[top] / len(p)), block_frac=float(inblock.mean()),
                rms_block_cells=rms_block / PM_CELL,
                rms_cm=float(np.sqrt(((p - cm) ** 2).sum(1).mean())))


def run(cfg):
    dt = cfg['dt']
    sim = ClampSim(dict(PRESET, particles=4000, seed=cfg['seed'], hubble=1.2, dt=dt,
                        selfgrav=1.0, clamp=cfg['clamp']))
    frames = int(round(30.0 / dt))
    rs, con, cl, fo, sp = [], [], [], [], []
    last = None
    for fi in range(frames):
        sim.frame(fi)
        if 28.0 - 1e-9 <= sim.simTime < 30.0 - 1e-9:
            rs.append(float(np.linalg.norm(sim.p, axis=1).mean()))
            con.append(contrast24(sim.p)); cl.append(sim.clamp_frac); fo.append(sim.fsg_over)
            sp.append(float(np.linalg.norm(sim.v, axis=1).mean()))
            last = sim.p.copy()
    out = dict(cfg, R_win=float(np.mean(rs)), contrast=float(np.mean(con)), clamp_frac=float(np.mean(cl)),
               fsg_over_clamp=float(np.mean(fo)), speed=float(np.mean(sp)), epochs=len(sim.epoch_frames),
               finite=bool(np.isfinite(sim.p).all()))
    out.update(blob_metrics(last))
    return out


if __name__ == '__main__':
    cfgs = [dict(seed=s, dt=dt, clamp=cl, label=lab)
            for lab, cl, dt in (('clamp500_dt1/20', 500.0, 1 / 20), ('clamp2000_dt1/80', 2000.0, 1 / 80), ('clamp500_dt1/80', 500.0, 1 / 80))
            for s in (12345, 777, 31415)]
    with Pool(4) as pool:
        res = pool.map(run, cfgs, chunksize=1)
    json.dump(res, open(os.path.join(HERE, 'jeans_clamp.json'), 'w'), indent=1)
    print('%-18s seed   R_win  contrast  clampfrac  |Fsg|>clamp  speed  occ  cells50 cells90 maxcell  block  rms_block(cells)  rms_cm' % 'case')
    for r in res:
        print('%-18s %5d  %6.2f   %5.2f     %.3f      %.3f     %6.1f  %4d   %4d    %4d   %.3f   %.3f      %.2f          %6.2f'
              % (r['label'], r['seed'], r['R_win'], r['contrast'], r['clamp_frac'], r['fsg_over_clamp'], r['speed'],
                 r['occupied'], r['cells50'], r['cells90'], r['max_cell_frac'], r['block_frac'], r['rms_block_cells'], r['rms_cm']))
