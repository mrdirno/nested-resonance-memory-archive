#!/usr/bin/env python3
"""memory_pm.py - numpy port of the chamber's particle-mesh SELF-GRAVITY,
layered on the validated port2.Sim (which itself layers on particle_port).

Ported from resonance-chamber.html (PM_GLSL, depositMat, poissonMat, pmSolve,
simStep, and the uSelfGrav block of the velMat fragment shader):

  mesh      PM_N = 32 cells per axis over [-PM_HALF, PM_HALF]^3,
            PM_HALF = EXTENT*1.02 = 15.3, PM_CELL = 30.6/32 = 0.95625
  cell      c = floor((p / PM_HALF * 0.5 + 0.5) * PM_N)          (NGP)
  deposit   rho(c) += 1/1024 per particle whose cell is inside the mesh
  source    src = uPmScale * (rho - uPmMean),
            uPmMean = N / 32^3 / 1024,  uPmScale = 32^3 * 1024 / N
            (= count/mean_count - 1: the density contrast, Jeans swindle)
  solve     PM_ITERS = 6 Jacobi sweeps per frame, WARM-STARTED from the
            previous frame's potential:  phi = (sum of 6 neighbours - src)/6,
            phi == 0 outside the mesh (Dirichlet)
  order     pmSolve() runs at the top of simStep, i.e. the deposit reads the
            positions at the START of the frame and the velocity pass of the
            same frame reads the freshly swept potential
  force     g_i = phi(c+e_i) - phi(c-e_i)  (0 outside the mesh)
            F += -uSelfGrav * SG_GAIN * g / (2*PM_CELL),  SG_GAIN = 14,
            added with the other forces BEFORE the |F| <= 500 clamp

Half-float caveat: the GPU keeps rho and phi in 16-bit floats; this port uses
float64.  Deposits of k/1024 are exact in half float for k <= 2048, so the
density is identical; phi differs at the ~5e-4 relative level.
"""
import math
import numpy as np

import port2
from port2 import EXTENT

PM_N = 32
PM_HALF = EXTENT * 1.02            # 15.3
PM_CELL = 2 * PM_HALF / PM_N       # 0.95625
PM_ITERS = 6
SG_GAIN = 14.0


def pm_cell_of(p):
    """pmCellOf(): integer NGP cell per particle, shape (N,3)."""
    return np.floor((p / PM_HALF * 0.5 + 0.5) * PM_N).astype(np.int64)


def deposit(p):
    """depositMat: rho = count/1024 on the 32^3 mesh (index order x,y,z)."""
    c = pm_cell_of(p)
    inside = np.all((c >= 0) & (c <= PM_N - 1), axis=1)
    c = c[inside]
    flat = (c[:, 0] * PM_N + c[:, 1]) * PM_N + c[:, 2]
    counts = np.bincount(flat, minlength=PM_N ** 3).reshape(PM_N, PM_N, PM_N)
    return counts / 1024.0


def source(rho, total):
    cells = PM_N ** 3
    mean = total / cells / 1024.0
    scale = cells * 1024.0 / max(1, total)
    return scale * (rho - mean)


def jacobi(phi, src, iters):
    """poissonMat sweeps: phi_new = (sum of 6 neighbours - src)/6, phi=0 outside."""
    for _ in range(iters):
        pp = np.pad(phi, 1)
        s = (pp[2:, 1:-1, 1:-1] + pp[:-2, 1:-1, 1:-1]
             + pp[1:-1, 2:, 1:-1] + pp[1:-1, :-2, 1:-1]
             + pp[1:-1, 1:-1, 2:] + pp[1:-1, 1:-1, :-2])
        phi = (s - src) / 6.0
    return phi


def laplacian_residual(phi, src):
    """|sum_nb phi - 6 phi - src|_max : zero when the sweeps have converged."""
    pp = np.pad(phi, 1)
    s = (pp[2:, 1:-1, 1:-1] + pp[:-2, 1:-1, 1:-1]
         + pp[1:-1, 2:, 1:-1] + pp[1:-1, :-2, 1:-1]
         + pp[1:-1, 1:-1, 2:] + pp[1:-1, 1:-1, :-2])
    return float(np.abs(s - 6.0 * phi - src).max())


def pm_force(phi, p, selfgrav):
    """velMat uSelfGrav block: central differences of phi at the particle's
    NGP cell, potential pinned to 0 outside the mesh."""
    c = pm_cell_of(p)
    c = np.clip(c, -1, PM_N)           # keeps every c+-1 lookup inside the pad
    pp = np.pad(phi, 2)                # pad 2: index c -> c+2
    cx, cy, cz = c[:, 0] + 2, c[:, 1] + 2, c[:, 2] + 2
    g = np.stack([pp[cx + 1, cy, cz] - pp[cx - 1, cy, cz],
                  pp[cx, cy + 1, cz] - pp[cx, cy - 1, cz],
                  pp[cx, cy, cz + 1] - pp[cx, cy, cz - 1]], axis=1)
    return -selfgrav * SG_GAIN * g / (2.0 * PM_CELL)


class MemSim(port2.Sim):
    """port2.Sim + the chamber's self-gravity. cfg['selfgrav'] in [0,2]."""

    def __init__(self, cfg):
        super().__init__(cfg)
        self.selfgrav = float(self.st.get('selfgrav', 0.0))
        self.phi = np.zeros((PM_N, PM_N, PM_N))
        self.sgF_med = 0.0
        self.pm_resid = 0.0

    def raw_pass(self):
        if self.selfgrav > 0.001:
            # pmSolve(): deposit the START-of-frame positions, 6 warm sweeps
            src = source(deposit(self.p), len(self.p))
            self.phi = jacobi(self.phi, src, PM_ITERS)
            self._src = src
        super().raw_pass()

    def force(self, p, v):
        F, SB = super().force(p, v)
        if self.selfgrav > 0.001:
            Fsg = pm_force(self.phi, p, self.selfgrav)
            self.sgF_med = float(np.median(np.linalg.norm(Fsg, axis=1)))
            F = F + Fsg
        return F, SB


# ----------------------------------------------------------------------------
def validate():
    rng = np.random.default_rng(3)
    # (1) cell mapping, hand-evaluated against pmCellOf():
    #     p = 15.3 -> 32 (outside); p = -15.3 -> 0; p = 0 -> 16; p = 7.65 -> 24
    #     p = 7.0 -> floor((7/15.3*0.5+0.5)*32) = floor(23.32) = 23
    c = pm_cell_of(np.array([[15.3, -15.3, 0.0], [7.65, 7.0, -0.001]]))
    assert c.tolist() == [[32, 0, 16], [24, 23, 15]], c.tolist()

    # (2) the sweep solves sum_nb(phi) - 6 phi = src (sign and scale)
    N = 5000
    p = (rng.random((N, 3)) - 0.5) * 2 * 14.0
    src = source(deposit(p), N)
    assert abs(src.sum()) < 1e-6 * N, src.sum()         # swindle: zero net source
    phi = jacobi(np.zeros((PM_N,) * 3), src, 4000)
    res = laplacian_residual(phi, src)
    assert res < 1e-6, res

    # (3) hand-evaluated force at one cell: put phi = 0 everywhere except
    #     phi[17,16,16] = -3.0 ; a particle in cell (16,16,16) sees
    #     g = (phi[17]-phi[15], 0, 0) = (-3, 0, 0)
    #     F = -sg*14*g/(2*0.95625) = sg*14*3/1.9125 = sg*21.9607843...
    ph = np.zeros((PM_N,) * 3); ph[17, 16, 16] = -3.0
    q = np.array([[0.1, 0.2, -0.3]])           # cell (16,16,15)? check: -0.3 -> floor(15.69)=15
    q = np.array([[0.1, 0.2, 0.3]])            # cell (16,16,16)
    assert pm_cell_of(q).tolist() == [[16, 16, 16]]
    Fh = pm_force(ph, q, 0.5)[0]
    assert abs(Fh[0] - 0.5 * 14.0 * 3.0 / (2 * PM_CELL)) < 1e-12 and Fh[1] == 0 and Fh[2] == 0, Fh
    assert abs(Fh[0] - 10.98039215686) < 1e-8, Fh[0]
    # and the pull is TOWARD the well (well at +x, force +x): attractive
    assert Fh[0] > 0

    # (4) THIN SHELL: potential minimum within one cell of the shell radius.
    a = 7.5
    M = 40000
    ct = 2 * rng.random(M) - 1; st = np.sqrt(1 - ct * ct); ph_ = rng.random(M) * 2 * np.pi
    shell = a * np.stack([st * np.cos(ph_), ct, st * np.sin(ph_)], axis=1)
    src = source(deposit(shell), M)
    phi = jacobi(np.zeros((PM_N,) * 3), src, 4000)
    idx = np.indices((PM_N,) * 3).reshape(3, -1).T
    xyz = (idx + 0.5) * PM_CELL - PM_HALF
    r = np.linalg.norm(xyz, axis=1)
    rb = np.floor(r / PM_CELL).astype(int)
    prof = np.array([phi.ravel()[rb == b].mean() for b in range(16)])
    rmid = (np.arange(16) + 0.5) * PM_CELL
    kmin = int(np.argmin(prof))
    r_min = rmid[kmin]
    # sub-cell refinement: parabola through the three bins around the minimum
    if 0 < kmin < 15:
        y0, y1, y2 = prof[kmin - 1:kmin + 2]
        den = (y0 - 2 * y1 + y2)
        r_min_ref = rmid[kmin] + (0.5 * (y0 - y2) / den) * PM_CELL if den != 0 else r_min
    else:
        r_min_ref = r_min
    ok = abs(r_min - a) <= PM_CELL
    # same test with the chamber's own cadence: 6 warm-started sweeps/frame, 200 frames
    phi6 = np.zeros((PM_N,) * 3)
    for _ in range(200):
        phi6 = jacobi(phi6, src, PM_ITERS)
    prof6 = np.array([phi6.ravel()[rb == b].mean() for b in range(16)])
    r_min6 = rmid[int(np.argmin(prof6))]
    print("PM VALIDATION")
    print("  cell map, Laplacian residual after 4000 sweeps = %.2e, hand-evaluated force OK" % res)
    print("  thin shell a = %.3f : angle-averaged phi(r) minimum at r = %.3f "
          "(bin-refined %.3f), |dr| = %.3f cell  -> %s" %
          (a, r_min, r_min_ref, abs(r_min - a) / PM_CELL, "PASS" if ok else "FAIL"))
    print("  same shell with the chamber cadence (6 sweeps/frame x 200 frames): "
          "minimum at r = %.3f, residual %.3e" % (r_min6, laplacian_residual(phi6, src)))
    print("  phi(r) profile (cell-bin means):")
    for rr, pv, p6 in zip(rmid, prof, prof6):
        print("     r=%6.2f  phi=%9.3f  phi_6/frame=%9.3f %s" %
              (rr, pv, p6, "<- shell" if abs(rr - a) < PM_CELL / 2 else ""))
    assert ok
    return r_min


if __name__ == '__main__':
    port2.PP.validate_math()
    port2.validate_added() if hasattr(port2, 'validate_added') else None
    validate()
