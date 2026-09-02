#!/usr/bin/env python3
"""jeans_pm.py - numpy port of the resonance-chamber.html SELF-GRAVITY pass
(particle-mesh Poisson), layered on port2.Sim, which already carries the
current velocity shader (chladni field, smooth blend, aniso/helix hubble,
Lorentz, epoch rescale; validated against the GPU to 2e-3 by gt_check.py).

Ported from PM_GLSL / depositMat / poissonMat / pmSolve / velMat:
  PM_N = 32 cells per axis, PM_HALF = EXTENT*1.02 = 15.3, PM_CELL = 2*15.3/32
  cell(p) = floor((p/PM_HALF*0.5 + 0.5)*PM_N)   nearest-grid-point deposit,
      each particle adds 1/1024 to rho[cell] if all indices in [0,31]
  uPmMean  = N/PM_N^3/1024,  uPmScale = PM_N^3*1024/N
  src      = uPmScale*(rho - uPmMean)          (= rho/rho_mean - 1, the contrast)
  6 Jacobi sweeps per frame: phi_new = (sum6(phi_old) - src)/6, phi = 0 outside
      the mesh (Dirichlet), WARM-STARTED from the previous frame's phi
  force:  g_i = phi(c+e_i) - phi(c-e_i);  F += -selfgrav*SG_GAIN*g/(2*PM_CELL),
      SG_GAIN = 14, inside the velocity pass before the |F| <= 500 clamp
  pmSolve runs at the start of simStep on posA, i.e. on the same positions the
      velocity pass reads (self.p before raw_pass).
GPU precision (half=True, default): pmDens and pmPot are HalfFloat targets.
  The deposit literal is (1/1024).toFixed(8) = 0.00097656, which fp16 rounds
  back to exactly 2^-10, so rho = k/1024 exactly for k <= 2048; adding 2^-10
  to 2.0 rounds-to-even back to 2.0, so a cell stalls at 2048 particles.
  phi is rounded to fp16 after every sweep.  half=False keeps fp32.
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import port2
from port2 import PRESET, EXTENT

PM_N = 32
PM_HALF = float('%.4f' % (EXTENT * 1.02))               # 15.3000 (GLSL literal)
PM_CELL = float('%.6f' % (2 * EXTENT * 1.02 / PM_N))    # 0.956250 (GLSL literal)
PM_ITERS = 6
SG_GAIN = 14.0
CELLS = PM_N ** 3


def pm_cell_of(p):
    return np.floor((p / PM_HALF * 0.5 + 0.5) * PM_N).astype(np.int64)


def pm_deposit(p, half=True):
    """rho on the 32^3 mesh, indexed [ix, iy, iz]."""
    c = pm_cell_of(p)
    inside = np.all((c >= 0) & (c <= PM_N - 1), axis=1)
    ci = c[inside]
    flat = (ci[:, 0] * PM_N + ci[:, 1]) * PM_N + ci[:, 2]
    k = np.bincount(flat, minlength=CELLS).reshape(PM_N, PM_N, PM_N)
    if half:
        k = np.minimum(k, 2048)                 # fp16 additive-blend stall
    return (k / 1024.0).astype(np.float32)


def pm_source(rho, N):
    mean = np.float32(N / CELLS / 1024)
    scale = np.float32(CELLS * 1024 / max(1, N))
    return (scale * (rho - mean)).astype(np.float32)


def jacobi(phi, src, iters=PM_ITERS, half=True):
    P = np.zeros((PM_N + 2,) * 3, np.float32)          # Dirichlet halo
    for _ in range(iters):
        P[1:-1, 1:-1, 1:-1] = phi
        s = (P[2:, 1:-1, 1:-1] + P[:-2, 1:-1, 1:-1]
             + P[1:-1, 2:, 1:-1] + P[1:-1, :-2, 1:-1]
             + P[1:-1, 1:-1, 2:] + P[1:-1, 1:-1, :-2])
        phi = (s - src) / np.float32(6.0)
        if half:
            phi = phi.astype(np.float16).astype(np.float32)
    return phi


def pm_grad6(phi, p):
    """phi(c+e_i) - phi(c-e_i) at each particle's cell, zeros outside the mesh."""
    c = pm_cell_of(p)
    cc = np.clip(c, -2, PM_N + 1) + 3
    P = np.zeros((PM_N + 6,) * 3, np.float32)
    P[3:-3, 3:-3, 3:-3] = phi
    x, y, z = cc[:, 0], cc[:, 1], cc[:, 2]
    return np.stack([P[x + 1, y, z] - P[x - 1, y, z],
                     P[x, y + 1, z] - P[x, y - 1, z],
                     P[x, y, z + 1] - P[x, y, z - 1]], axis=1)


def pm_force(phi, p, selfgrav):
    return -selfgrav * SG_GAIN * pm_grad6(phi, p) / (2.0 * PM_CELL)


def laplacian_residual(phi, src):
    """RMS of (sum6(phi) - 6 phi - src) relative to RMS(src): 0 = solved."""
    P = np.zeros((PM_N + 2,) * 3, np.float64)
    P[1:-1, 1:-1, 1:-1] = phi
    s = (P[2:, 1:-1, 1:-1] + P[:-2, 1:-1, 1:-1] + P[1:-1, 2:, 1:-1]
         + P[1:-1, :-2, 1:-1] + P[1:-1, 1:-1, 2:] + P[1:-1, 1:-1, :-2])
    res = s - 6.0 * phi - src
    return float(np.sqrt((res ** 2).mean()) / max(1e-12, np.sqrt((src.astype(np.float64) ** 2).mean())))


class PMSim(port2.Sim):
    """port2.Sim + particle-mesh self-gravity, inserted where the shader has it."""

    def __init__(self, state):
        st = dict(state)
        self.selfgrav = float(st.pop('selfgrav', 0.0))
        self.half = bool(st.pop('half', True))
        self.pm_iters = int(st.pop('pm_iters', PM_ITERS))   # sweeps/frame (page: 6)
        super().__init__(st)
        self.phi = np.zeros((PM_N,) * 3, np.float32)   # fresh render target = 0
        self.rho = None
        self.N = int(self.st['particles'])
        self.Fsg = None

    def pm_solve(self):
        if not (self.selfgrav > 0.001):
            return                                      # pmSolve early-out
        self.rho = pm_deposit(self.p, self.half)
        src = pm_source(self.rho, self.N)
        self.phi = jacobi(self.phi, src, self.pm_iters, self.half)

    def raw_pass(self):
        self.pm_solve()                                 # simStep: pmSolve() first
        super().raw_pass()

    def force(self, p, v):
        F, SB = super().force(p, v)                     # field+flow+Lorentz (pre-clamp)
        if self.selfgrav > 0.001:
            self.Fsg = pm_force(self.phi, p, self.selfgrav)
            F = F + self.Fsg
        return F, SB


# ---------------------------------------------------------------- metrics
def contrast24(p):
    """selfgrav_test.js clumpiness: std/mean of counts over OCCUPIED 24^3 cells."""
    n, E = 24, 15.3
    c = np.floor((p / E * 0.5 + 0.5) * n).astype(np.int64)
    ok = np.all((c >= 0) & (c < n), axis=1)
    flat = (c[ok, 2] * n + c[ok, 1]) * n + c[ok, 0]
    g = np.bincount(flat, minlength=n ** 3).astype(float)
    occ = g[g > 0]
    mu = occ.mean()
    return float(np.sqrt(max(0.0, (occ ** 2).mean() - mu * mu)) / mu)


def run_case(cfg):
    """One 30 s run.  cfg keys: H, selfgrav, [seed, N, epoch, half, startStep,
    smooth, frames, t_win, state].  Returns the window-mean radius and friends."""
    st = dict(PRESET)
    st.update(dict(particles=int(cfg.get('N', 4000)), seed=int(cfg.get('seed', 12345)),
                   hubble=float(cfg['H']), epoch=bool(cfg.get('epoch', True)),
                   startStep=int(cfg.get('startStep', 9028)),
                   smooth=bool(cfg.get('smooth', True)), dt=1.0 / 20.0))
    st.update(cfg.get('state', {}))
    sim = PMSim(dict(st, selfgrav=float(cfg['selfgrav']), half=bool(cfg.get('half', True))))
    frames = int(cfg.get('frames', 600))
    t0w, t1w = cfg.get('t_win', (28.0, 30.0))
    rs = np.empty(frames); ts = np.empty(frames)
    con, clamp, fsg, sp = [], [], [], []
    for fi in range(frames):
        sim.frame(fi)
        r = np.linalg.norm(sim.p, axis=1)
        rs[fi] = r.mean(); ts[fi] = sim.simTime
        if t0w - 1e-9 <= sim.simTime < t1w - 1e-9:
            con.append(contrast24(sim.p))
            clamp.append(sim.clamp_frac)
            sp.append(float(np.linalg.norm(sim.v, axis=1).mean()))
            if sim.Fsg is not None:
                fsg.append(float(np.median(np.linalg.norm(sim.Fsg, axis=1))))
    win = (ts >= t0w - 1e-9) & (ts < t1w - 1e-9)
    out = {k: cfg[k] for k in cfg if k != 'state'}
    out.update(dict(
        R_win=float(rs[win].mean()), R_win_std=float(rs[win].std()),
        R_end=float(rs[-1]), R_min=float(rs.min()),
        r_series=[float(x) for x in rs[::10]],
        t_series=[float(x) for x in ts[::10]],
        contrast=float(np.mean(con)) if con else None,
        clamp_frac=float(np.mean(clamp)) if clamp else None,
        speed=float(np.mean(sp)) if sp else None,
        Fsg_med=float(np.mean(fsg)) if fsg else 0.0,
        finite=bool(np.isfinite(sim.p).all()),
        epochs=len(sim.epoch_frames)))
    return out


if __name__ == '__main__':
    import time
    sim = PMSim(dict(PRESET, particles=4000, selfgrav=0.5))
    t = time.time()
    for i in range(100):
        sim.frame(i)
    print('PMSim N=4000: %.2f ms/frame' % ((time.time() - t) * 10))
    print('phi range', float(sim.phi.min()), float(sim.phi.max()),
          'median |Fsg|', float(np.median(np.linalg.norm(sim.Fsg, axis=1))))
