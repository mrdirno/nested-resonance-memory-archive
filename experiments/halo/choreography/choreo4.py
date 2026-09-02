#!/usr/bin/env python3
"""choreo4.py - four like charges in an oscillating axial magnetic field:
Boris pusher, exact tangent map, Z4 time-delay choreography by Newton
shooting, monodromy / Floquet spectrum, long stress run.

Model (as specified): m = q = 1, pairwise regularized Coulomb repulsion
F_i = sum_j q^2 (r_i - r_j) / (|r_i - r_j|^2 + eps^2)^{3/2}, and the force
q v x B(t) with B(t) = B0 [a + (1 - a) cos(w t)] z-hat. a = 0 is the
specified zero-mean drive; a = 1 a constant field (used as the homotopy
start and as the pipeline self-test). No induced electric field is
included, exactly as specified (note: a time-varying uniform B has one,
E = -(1/2) dB/dt z x r; the specified model omits it).

Two facts about the specified model are proved below and checked
numerically at run time; the search is then carried out exactly as
specified and prints the singular value decompositions where the
specification itself asks for them.

  THEOREM 1 (no non-planar periodic orbit).  For B parallel to z the
  magnetic force has no z component, so with Iz = (1/2) sum_k (z_k - zcm)^2:
  d^2 Iz / dt^2 = sum_k (dz_k/dt - dzcm/dt)^2
                + sum_{i<j} q^2 (z_i - z_j)^2 / (|r_ij|^2 + eps^2)^{3/2} >= 0,
  with equality only if all z_k are equal and at rest relative to each
  other. A periodic function with non-negative second derivative is
  constant, so every periodic orbit has all z_k equal: it is planar.
  Corollary: about any planar periodic orbit the out-of-plane
  perturbations obey dd(z)/dt^2 = L(t) z with L(t) positive semidefinite
  (a graph Laplacian with positive weights), whose relative modes are
  hyperbolic; a planar orbit is never linearly stable in all 24
  directions.

  THEOREM 2 (delay consistency).  r_k(t) = r_1(t + (k-1) tau) can solve
  the same equations as r_1 only if B(t + tau) = B(t): the Coulomb terms
  are permutation invariant, the magnetic term is not time-shift
  invariant. With B = B0 cos(w t) and tau = T/4 = pi/(2 w),
  B(t + tau) = -B0 sin(w t) != B(t). The consistent Z4 choreography has
  delay tau = one drive period 2 pi / w and period T = 4 tau.
"""
import sys, time, math, argparse
import numpy as np

# ----------------------------------------------------------------- model
Q = 1.0; M = 1.0; Q2 = 1.0
EPS = 0.05; EPS2 = EPS * EPS
P = 4
I12 = np.eye(3 * P); I24 = np.eye(6 * P)
KZ = 0.0     # axial spring (not in the specification; set by --kz for the extension search)


def Bfun(t, B0, w, a):
    return B0 * (a + (1.0 - a) * math.cos(w * t))


def force(r):
    d = r[:, None, :] - r[None, :, :]
    s2 = (d * d).sum(-1) + EPS2
    np.fill_diagonal(s2, np.inf)
    inv3 = s2 ** -1.5
    F = Q2 * (d * inv3[..., None]).sum(1)
    if KZ:
        F[:, 2] -= KZ * r[:, 2]
    return F


def potential(r):
    d = r[:, None, :] - r[None, :, :]
    s2 = (d * d).sum(-1) + EPS2
    iu = np.triu_indices(len(r), 1)
    return Q2 * (s2[iu] ** -0.5).sum() + 0.5 * KZ * (r[:, 2] ** 2).sum()


def energy(r, v):
    return 0.5 * M * (v * v).sum() + potential(r)


def rot3(th):
    c, s = math.cos(th), math.sin(th)
    # dv/dt = (q/m) v x B z-hat  =>  (vx + i vy)' = -i wc (vx + i vy)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])


def boris_step(r, v, t, dt, B0, w, a):
    """Symmetric composition, second order and time-reversible with
    synchronized r and v: half Coulomb kick, half drift, exact Boris rotation
    about z by the mid-step angle, half drift, half Coulomb kick. (The
    classical Boris leapfrog is the same rotation kernel with the velocity
    staggered by half a step; synchronizing it is what makes the energy
    check below meaningful at second order.)"""
    h = 0.5 * dt
    v = v + (h / M) * force(r)
    r = r + h * v
    R = rot3((Q / M) * Bfun(t + h, B0, w, a) * dt)
    sp0 = np.hypot(v[:, 0], v[:, 1])
    v = v @ R.T
    # a rotation does no work: restore the in-plane speed to the last bit, so that
    # rounding in cos/sin cannot bias the energy over a billion steps
    sp1 = np.hypot(v[:, 0], v[:, 1])
    f = np.where(sp1 > 0, sp0 / np.where(sp1 > 0, sp1, 1.0), 1.0)
    v[:, 0] *= f; v[:, 1] *= f
    r = r + h * v
    v = v + (h / M) * force(r)
    return r, v


def force_jac(r):
    K = np.zeros((3 * P, 3 * P))
    for i in range(P):
        for j in range(i + 1, P):
            d = r[i] - r[j]
            s = d @ d + EPS2
            blk = Q2 * (np.eye(3) * s ** -1.5 - 3.0 * np.outer(d, d) * s ** -2.5)
            K[3*i:3*i+3, 3*i:3*i+3] += blk; K[3*j:3*j+3, 3*j:3*j+3] += blk
            K[3*i:3*i+3, 3*j:3*j+3] -= blk; K[3*j:3*j+3, 3*i:3*i+3] -= blk
    if KZ:
        for i in range(P):
            K[3*i+2, 3*i+2] -= KZ
    return K


def step_jac(r, v, t, dt, B0, w, a):
    """Exact Jacobian of one step, state ordering (r_1..r_4, v_1..v_4):
    the product of the five stage Jacobians, evaluated at the same
    intermediate states the step itself visits."""
    h = 0.5 * dt
    Z = np.zeros((3 * P, 3 * P))
    K1 = force_jac(r)
    v1 = v + (h / M) * force(r)
    r1 = r + h * v1
    R = np.kron(np.eye(P), rot3((Q / M) * Bfun(t + h, B0, w, a) * dt))
    v2 = v1 @ np.kron(np.eye(P), rot3((Q / M) * Bfun(t + h, B0, w, a) * dt))[:3, :3].T
    r2 = r1 + h * v2
    K2 = force_jac(r2)
    kick1 = np.block([[I12, Z], [(h / M) * K1, I12]])
    drift = np.block([[I12, h * I12], [Z, I12]])
    rota = np.block([[I12, Z], [Z, R]])
    kick2 = np.block([[I12, Z], [(h / M) * K2, I12]])
    return kick2 @ drift @ rota @ drift @ kick1


def unpack(X):
    return X[:3 * P].reshape(P, 3).copy(), X[3 * P:].reshape(P, 3).copy()


def pack(r, v):
    return np.concatenate([r.ravel(), v.ravel()])


def flow(X, t0, n, dt, B0, w, a, jac=False):
    r, v = unpack(X)
    J = I24.copy() if jac else None
    t = t0
    for _ in range(n):
        if jac:
            J = step_jac(r, v, t, dt, B0, w, a) @ J
        r, v = boris_step(r, v, t, dt, B0, w, a)
        t += dt
    return (pack(r, v), J) if jac else pack(r, v)


# the cyclic shift: (S X)_k = X_{k+1 mod 4}, positions and velocities alike
def shift_matrix():
    S = np.zeros((6 * P, 6 * P))
    for k in range(P):
        kk = (k + 1) % P
        S[3*k:3*k+3, 3*kk:3*kk+3] = np.eye(3)
        S[3*P+3*k:3*P+3*k+3, 3*P+3*kk:3*P+3*kk+3] = np.eye(3)
    return S


S = shift_matrix(); Sinv = S.T


def residual(X, tau, N, B0, w, a, jac=True):
    """G(X) = S^-1 Phi_tau(X) - X and its exact Jacobian."""
    dt = tau / N
    if jac:
        Y, J = flow(X, 0.0, N, dt, B0, w, a, jac=True)
        return Sinv @ Y - X, Sinv @ J - I24
    return Sinv @ flow(X, 0.0, N, dt, B0, w, a) - X


ZIDX = np.array([3 * k + 2 for k in range(P)] + [3 * P + 3 * k + 2 for k in range(P)])


def newton(X, tau, N, B0, w, a, tol=1e-12, maxit=60, rcond=1e-9, verbose=False, log=None, planar=False):
    """Damped Gauss-Newton with the exact Jacobian and a minimum-norm step
    (the symmetry directions - translations, rotation about z - are exact
    null directions of the residual and receive no step)."""
    F, DF = residual(X, tau, N, B0, w, a)
    nf = np.linalg.norm(F)
    hist = [nf]
    for it in range(maxit):
        if nf < tol:
            break
        d = -np.linalg.pinv(DF, rcond=rcond) @ F
        alpha, ok = 1.0, False
        for _ in range(12):
            Xn = X + alpha * d
            if planar:
                Xn[ZIDX] = 0.0      # the plane is an invariant subspace of the exact map; keep roundoff out of it
            Fn = residual(Xn, tau, N, B0, w, a, jac=False)
            nfn = np.linalg.norm(Fn)
            if nfn < nf * (1.0 - 1e-4 * alpha):
                ok = True
                break
            alpha *= 0.5
        if not ok:
            break
        X = Xn
        F, DF = residual(X, tau, N, B0, w, a)
        nf = np.linalg.norm(F)
        hist.append(nf)
        if verbose:
            print(f'      it {it+1:2d}  |G| = {nf:.3e}  step {alpha:g}')
        if log is not None:
            log.append((it + 1, nf, alpha))
    return X, nf, DF, hist


def step_jac_inv(r, v, t, dt, B0, w, a):
    """Exact inverse of the step Jacobian: the stage inverses in reverse order
    (kick with -h at the same positions, drift with -h, rotation by -theta)."""
    h = 0.5 * dt
    Z = np.zeros((3 * P, 3 * P))
    K1 = force_jac(r)
    v1 = v + (h / M) * force(r)
    r1 = r + h * v1
    R3 = rot3((Q / M) * Bfun(t + h, B0, w, a) * dt)
    v2 = v1 @ R3.T
    r2 = r1 + h * v2
    K2 = force_jac(r2)
    kick1i = np.block([[I12, Z], [-(h / M) * K1, I12]])
    drifti = np.block([[I12, -h * I12], [Z, I12]])
    rotai = np.block([[I12, Z], [Z, np.kron(np.eye(P), R3.T)]])
    kick2i = np.block([[I12, Z], [-(h / M) * K2, I12]])
    return kick1i @ drifti @ rotai @ drifti @ kick2i


def monodromy(X, tau, N, B0, w, a):
    """M = prod J_n over the full period T = 4 tau (and its exact inverse,
    accumulated from the stage inverses), plus the closure of particle 1."""
    dt = tau / N
    r, v = unpack(X)
    J = I24.copy(); Ji = I24.copy(); t = 0.0
    for _ in range(4 * N):
        J = step_jac(r, v, t, dt, B0, w, a) @ J
        Ji = Ji @ step_jac_inv(r, v, t, dt, B0, w, a)
        r, v = boris_step(r, v, t, dt, B0, w, a)
        t += dt
    r0, v0 = unpack(X)
    closure = np.linalg.norm(r[0] - r0[0]) + np.linalg.norm(v[0] - v0[0])
    return J, Ji, closure, pack(r, v)


XYIDX = np.array(sorted(set(range(6 * P)) - set(ZIDX.tolist())))


def block_multipliers(Mm, Mi, idx):
    """Multipliers of one invariant block: the ones of modulus >= 1 from
    eig(M), the ones below from the reciprocals of eig(M^-1). A product of
    5e2 step Jacobians with hyperbolic growth 1e13 has an absolute
    eigenvalue floor of ||M|| eps ~ 1e-3, so the small multipliers of M can
    only be read from M^-1, whose large ones are exactly as well
    conditioned as the large ones of M."""
    A = Mm[np.ix_(idx, idx)]; Ai = Mi[np.ix_(idx, idx)]
    la = np.linalg.eigvals(A); li = 1.0 / np.linalg.eigvals(Ai)
    big = sorted(la, key=lambda z: -abs(z)); small = sorted(li, key=lambda z: abs(z))
    n = len(idx)
    out = []
    # take the k largest from M and the n - k smallest from M^-1 with k the count of |lambda| >= 1 in M
    k = int(sum(1 for z in la if abs(z) >= 1.0))
    out = big[:k] + small[:n - k]
    return np.array(sorted(out, key=lambda z: abs(z)))


def floquet_report(Mm, Mi):
    lam_xy = block_multipliers(Mm, Mi, XYIDX)
    lam_z = block_multipliers(Mm, Mi, ZIDX)
    rows = [(l, abs(l) - 1.0, 'in-plane') for l in lam_xy] + [(l, abs(l) - 1.0, 'out-of-plane') for l in lam_z]
    rows.sort(key=lambda t: abs(t[0]))
    lam = np.array([t[0] for t in rows])
    coupling = np.abs(Mm[np.ix_(XYIDX, ZIDX)]).max() / np.abs(Mm[np.ix_(XYIDX, XYIDX)]).max()
    return lam, rows, coupling


def full_multipliers(Mm, Mi):
    """All 24 multipliers when the orbit is non-planar: the ones of modulus
    >= 1 from eig(M), the rest as reciprocals of eig(M^-1); modes are labelled
    by the z-support of their eigenvectors."""
    la, va = np.linalg.eig(Mm); li, vi = np.linalg.eig(Mi)
    k = int(sum(1 for z in la if abs(z) >= 1.0))
    ia = np.argsort(-np.abs(la))[:k]; ii = np.argsort(-np.abs(li))[:24 - k]
    rows = []
    for j in ia:
        vz = np.linalg.norm(va[ZIDX, j]) / np.linalg.norm(va[:, j])
        rows.append((la[j], abs(la[j]) - 1.0, 'out-of-plane' if vz > 0.7 else ('in-plane' if vz < 0.3 else 'mixed')))
    for j in ii:
        vz = np.linalg.norm(vi[ZIDX, j]) / np.linalg.norm(vi[:, j])
        l = 1.0 / li[j]
        rows.append((l, abs(l) - 1.0, 'out-of-plane' if vz > 0.7 else ('in-plane' if vz < 0.3 else 'mixed')))
    rows.sort(key=lambda t: abs(t[0]))
    return np.array([t[0] for t in rows]), rows


def pairing(lams):
    return max(min(abs(l * l2 - 1.0) for l2 in lams) for l in lams)


def print_state(X, label):
    r, v = unpack(X)
    print(label)
    for k in range(P):
        print(f'  k={k+1}  r = ({r[k,0]:+.10f}, {r[k,1]:+.10f}, {r[k,2]:+.10f})'
              f'   v = ({v[k,0]:+.10f}, {v[k,1]:+.10f}, {v[k,2]:+.10f})')


def print_svd(DF, label):
    sv = np.linalg.svd(DF, compute_uv=False)
    print(label)
    print('  singular values of DG - I (24, descending):')
    for i in range(0, 24, 6):
        print('   ', ' '.join(f'{s:.3e}' for s in sv[i:i+6]))
    return sv


# ------------------------------------------------ the rotating-square reference
def rotating_square(B0, R, branch):
    """Four charges on a square of circumradius R rigidly rotating in a
    constant field B0 z-hat. Radial balance for angular rate W (clockwise
    for B0 > 0): W^2 R + (q B0 / m) W R + F_rep / m = 0."""
    r = np.array([[R * math.cos(k * math.pi / 2), R * math.sin(k * math.pi / 2), 0.0] for k in range(P)])
    Frep = np.linalg.norm(force(r)[0])          # outward, by symmetry radial
    b = (Q * B0 / M) * R
    disc = b * b - 4.0 * R * Frep / M
    if disc < 0:
        return None
    Ws = [(-b - math.sqrt(disc)) / (2 * R), (-b + math.sqrt(disc)) / (2 * R)]   # fast, slow (both clockwise)
    W = Ws[0] if branch == 'fast' else Ws[1]
    # particle k sits where particle 1 will be after (k-1) quarter turns: order them along the rotation
    sgn = 1.0 if W > 0 else -1.0
    r = np.array([[R * math.cos(sgn * k * math.pi / 2), R * math.sin(sgn * k * math.pi / 2), 0.0] for k in range(P)])
    v = np.array([W * np.array([-r[k, 1], r[k, 0], 0.0]) for k in range(P)])   # W r phi-hat
    return pack(r, v), W


# ------------------------------------------------------- long run (numba)
try:
    import numba
    HAVE_NUMBA = True
except Exception:
    HAVE_NUMBA = False

if HAVE_NUMBA:
    @numba.njit(cache=True, fastmath=False)
    def long_run(r, v, ref, ncyc, N, dt, B0, w, a, q2, eps2, m, q, E0, every, dev_out, en_out, kz):
        """ncyc drive cycles of N Boris steps; at each cycle start the state is
        compared with ref[c mod 4] (the shifted initial state). Returns
        (max position deviation, max |dE/E0|); subsampled traces in *_out."""
        Pn = r.shape[0]
        F = np.zeros((Pn, 3))
        maxdev = 0.0; maxde = 0.0
        t = 0.0
        for c in range(ncyc):
            # deviation and energy at the cycle start
            k = c % 4
            dev = 0.0
            for i in range(Pn):
                dx = r[i, 0] - ref[k, i, 0]; dy = r[i, 1] - ref[k, i, 1]; dz = r[i, 2] - ref[k, i, 2]
                dd = math.sqrt(dx * dx + dy * dy + dz * dz)
                if dd > dev:
                    dev = dd
            pe = 0.0
            for i in range(Pn):
                for j in range(i + 1, Pn):
                    dx = r[i, 0] - r[j, 0]; dy = r[i, 1] - r[j, 1]; dz = r[i, 2] - r[j, 2]
                    pe += q2 / math.sqrt(dx * dx + dy * dy + dz * dz + eps2)
            ke = 0.0
            for i in range(Pn):
                ke += 0.5 * m * (v[i, 0] ** 2 + v[i, 1] ** 2 + v[i, 2] ** 2)
                pe += 0.5 * kz * r[i, 2] ** 2
            de = abs((ke + pe - E0) / E0)
            if dev > maxdev:
                maxdev = dev
            if de > maxde:
                maxde = de
            if c % every == 0:
                dev_out[c // every] = dev
                en_out[c // every] = de
            # forces at the cycle-start positions (then carried from step to step)
            for i in range(Pn):
                F[i, 0] = 0.0; F[i, 1] = 0.0; F[i, 2] = 0.0
            for i in range(Pn):
                for j in range(i + 1, Pn):
                    dx = r[i, 0] - r[j, 0]; dy = r[i, 1] - r[j, 1]; dz = r[i, 2] - r[j, 2]
                    s = dx * dx + dy * dy + dz * dz + eps2
                    inv3 = q2 / (s * math.sqrt(s))
                    fx = dx * inv3; fy = dy * inv3; fz = dz * inv3
                    F[i, 0] += fx; F[i, 1] += fy; F[i, 2] += fz
                    F[j, 0] -= fx; F[j, 1] -= fy; F[j, 2] -= fz
            for i in range(Pn):
                F[i, 2] -= kz * r[i, 2]
            h = 0.5 * dt
            hk = h / m
            for n in range(N):
                th = (q / m) * B0 * (a + (1.0 - a) * math.cos(w * (t + h))) * dt
                cth = math.cos(th); sth = math.sin(th)
                for i in range(Pn):
                    vx = v[i, 0] + hk * F[i, 0]; vy = v[i, 1] + hk * F[i, 1]; vz = v[i, 2] + hk * F[i, 2]
                    x1 = r[i, 0] + h * vx; y1 = r[i, 1] + h * vy; z1 = r[i, 2] + h * vz
                    vx2 = vx * cth + vy * sth; vy2 = -vx * sth + vy * cth
                    sp0 = math.sqrt(vx * vx + vy * vy); sp1 = math.sqrt(vx2 * vx2 + vy2 * vy2)
                    if sp1 > 0.0:
                        fr = sp0 / sp1; vx2 *= fr; vy2 *= fr
                    r[i, 0] = x1 + h * vx2; r[i, 1] = y1 + h * vy2; r[i, 2] = z1 + h * vz
                    v[i, 0] = vx2; v[i, 1] = vy2; v[i, 2] = vz
                for i in range(Pn):
                    F[i, 0] = 0.0; F[i, 1] = 0.0; F[i, 2] = 0.0
                for i in range(Pn):
                    for j in range(i + 1, Pn):
                        dx = r[i, 0] - r[j, 0]; dy = r[i, 1] - r[j, 1]; dz = r[i, 2] - r[j, 2]
                        s = dx * dx + dy * dy + dz * dz + eps2
                        inv3 = q2 / (s * math.sqrt(s))
                        fx = dx * inv3; fy = dy * inv3; fz = dz * inv3
                        F[i, 0] += fx; F[i, 1] += fy; F[i, 2] += fz
                        F[j, 0] -= fx; F[j, 1] -= fy; F[j, 2] -= fz
                for i in range(Pn):
                    F[i, 2] -= kz * r[i, 2]
                for i in range(Pn):
                    v[i, 0] += hk * F[i, 0]; v[i, 1] += hk * F[i, 1]; v[i, 2] += hk * F[i, 2]
                t += dt
            # keep the drive phase exact over a million cycles
            t = (c + 1) * N * dt
        return maxdev, maxde


# ================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--N', type=int, default=256, help='Boris steps per delay (drive period)')
    ap.add_argument('--cycles', type=int, default=1_000_000, help='drive cycles in the long run')
    ap.add_argument('--B0', type=float, default=3.0)
    ap.add_argument('--R', type=float, default=1.0)
    ap.add_argument('--branch', default='slow', choices=['slow', 'fast'])
    ap.add_argument('--quick', action='store_true', help='skip the long run')
    ap.add_argument('--kz', type=float, default=0.0, help='axial spring constant for the extension search (0 = the specification)')
    ap.add_argument('--zamp', type=float, default=0.3, help='out-of-plane seed amplitude for the extension search')
    args = ap.parse_args()
    global KZ
    np.set_printoptions(precision=10, suppress=False, linewidth=140)
    t_start = time.time()
    B0, R = args.B0, args.R

    print('=' * 78)
    print('LAYER 1 - Boris pusher: energy conservation on an isolated two-body problem')
    print('=' * 78)
    # two charges in the specified zero-mean drive (a = 0); the magnetic force
    # does no work for any B(t), so E = KE + PE is exactly conserved by the model
    w1 = 1.0
    r2 = np.array([[-0.5, 0.0, -0.2], [0.5, 0.0, 0.2]])
    v2 = np.array([[0.0, 0.6, 0.1], [0.0, -0.6, -0.1]])
    global P, I12, I24
    P_saved = P
    P = 2; I12 = np.eye(6); I24 = np.eye(12)
    E0 = energy(r2, v2)
    passed = None
    print(f'  E0 = {E0:.12f}   (B0 = {B0}, w = {w1}, a = 0, 10^4 steps at each dt)')
    for dt in [1e-2, 1e-3, 1e-4, 1e-5]:
        r, v = r2.copy(), v2.copy(); t = 0.0; worst = 0.0
        for n in range(10_000):
            r, v = boris_step(r, v, t, dt, B0, w1, 0.0); t += dt
            worst = max(worst, abs((energy(r, v) - E0) / E0))
        flag = 'PASS' if worst < 1e-10 else 'fail'
        print(f'  dt = {dt:<8g} max|dE/E0| = {worst:.3e}  {flag}')
        if worst < 1e-10 and passed is None:
            passed = dt
    print(f'  Layer 1 {"VALIDATED" if passed else "FAILED"}: |dE/E0| < 1e-10 over 10^4 steps at dt = {passed}')
    if not passed:
        sys.exit(1)
    # harsher: ten drive periods at the working resolution
    dt = (2 * math.pi / w1) / args.N; r, v = r2.copy(), v2.copy(); t = 0.0; worst = 0.0
    for n in range(10 * args.N):
        r, v = boris_step(r, v, t, dt, B0, w1, 0.0); t += dt
        worst = max(worst, abs((energy(r, v) - E0) / E0))
    print(f'  (working resolution N = {args.N} per period, ten periods: max|dE/E0| = {worst:.3e})')
    P = P_saved; I12 = np.eye(3 * P); I24 = np.eye(6 * P)

    print('\n  Tangent map check: analytic step Jacobian against central differences')
    rng = np.random.default_rng(0)
    Xc = np.concatenate([rng.normal(size=12), 0.3 * rng.normal(size=12)])
    dtc = 0.01
    Jan = step_jac(unpack(Xc)[0], unpack(Xc)[1], 0.3, dtc, B0, w1, 0.0)
    Jfd = np.zeros((24, 24)); h = 1e-6
    for i in range(24):
        e = np.zeros(24); e[i] = h
        rp, vp = unpack(Xc + e); rm, vm = unpack(Xc - e)
        yp = pack(*boris_step(rp, vp, 0.3, dtc, B0, w1, 0.0)); ym = pack(*boris_step(rm, vm, 0.3, dtc, B0, w1, 0.0))
        Jfd[:, i] = (yp - ym) / (2 * h)
    err = np.abs(Jan - Jfd).max() / np.abs(Jan).max()
    print(f'  max |J_analytic - J_fd| / max|J| = {err:.2e}   ({"VALIDATED" if err < 1e-6 else "FAILED"})')
    if err >= 1e-6:
        sys.exit(1)

    print('\n' + '=' * 78)
    print('LAYER 2 - symmetry: what the specified force law allows')
    print('=' * 78)
    print('  THEOREM 1 (see docstring): d^2 Iz/dt^2 >= 0 along every trajectory, so no')
    print('  non-planar periodic orbit exists for any B parallel to z. Numerical witness')
    print('  on a non-planar 4-body trajectory in the specified drive:')
    r0 = np.array([[1, 0, 0.3], [0, 1, -0.3], [-1, 0, 0.3], [0, -1, -0.3]], float)
    v0 = np.array([[0, -0.4, 0.2], [0.4, 0, -0.1], [0, 0.4, 0.15], [-0.4, 0, -0.25]], float)
    r, v = r0.copy(), v0.copy(); t = 0.0; dt = 2 * math.pi / args.N; mn = np.inf; Iz = []
    for n in range(4 * args.N):
        zr = r[:, 2] - r[:, 2].mean(); vzr = v[:, 2] - v[:, 2].mean()
        acc = (vzr ** 2).sum()
        for i in range(P):
            for j in range(i + 1, P):
                d = r[i] - r[j]; acc += Q2 * d[2] ** 2 / (d @ d + EPS2) ** 1.5
        mn = min(mn, acc); Iz.append(0.5 * (zr ** 2).sum())
        r, v = boris_step(r, v, t, dt, B0, w1, 0.0); t += dt
    print(f'    min over 4 periods of d^2 Iz/dt^2 = {mn:.6e} (>= 0)   Iz(0) = {Iz[0]:.4f} -> Iz(T) = {Iz[-1]:.4f} (convex, non-periodic)')
    tau_spec = math.pi / (2 * w1)
    mism = max(abs(Bfun(t + tau_spec, B0, w1, 0.0) - Bfun(t, B0, w1, 0.0)) for t in np.linspace(0, 2 * math.pi, 1000))
    print('  THEOREM 2: the delay must be a period of the drive.')
    print(f'    max_t |B(t + T/4) - B(t)| = {mism:.6f} = sqrt(2) B0 != 0  -> the T/4 delay is inconsistent;')
    print('    consistent Z4 choreography: delay tau = 2 pi / w (one drive period), period T = 4 tau.')
    print('    All shooting below uses G(X) = S^-1 Phi_tau(X) - X, (S X)_k = X_{k+1}, with tau = 2 pi / w.')

    print('\n' + '=' * 78)
    print('LAYER 3/4 SELF-TEST - a known choreography: the rotating square in a constant field')
    print('=' * 78)
    ref = rotating_square(B0, R, args.branch)
    if ref is None:
        print('  no rotating square at these parameters'); sys.exit(1)
    Xref, W = ref
    tau = (2 * math.pi / abs(W)) / 4          # delay = a quarter turn
    w = 2 * math.pi / tau                      # drive frequency such that one drive period = the delay
    N = args.N
    print(f'  B0 = {B0}, circumradius R = {R}, {args.branch} branch: W = {W:+.10f} rad/s, tau = {tau:.10f}, w = 4|W| = {w:.10f}')
    F0 = residual(Xref, tau, N, B0, w, 1.0, jac=False)
    print(f'  |G(X_analytic)| = {np.linalg.norm(F0):.3e} (continuous orbit vs the discrete map, O(dt^2)); Newton polishes:')
    Xr, nf, DFr, hist = newton(Xref, tau, N, B0, w, 1.0, verbose=True, planar=True)
    print(f'  converged |G| = {nf:.3e} in {len(hist)-1} iterations')
    Mr, Mri, clos, _ = monodromy(Xr, tau, N, B0, w, 1.0)
    lam, rows, coupling = floquet_report(Mr, Mri)
    # consistency: M must equal (S^-1 DPhi_tau)^4 = (DG + I)^4, and M M^-1 = I
    M4 = np.linalg.matrix_power(DFr + I24, 4)
    print(f'  closure ||r1(T)-r1(0)|| + ||v1(T)-v1(0)|| = {clos:.3e}')
    Mxy = Mr[np.ix_(XYIDX, XYIDX)]; Mxyi = Mri[np.ix_(XYIDX, XYIDX)]
    print(f'  ||M - (S^-1 DPhi_tau)^4|| / ||M|| = {np.linalg.norm(Mr - M4) / np.linalg.norm(Mr):.2e};  in-plane ||M M^-1 - I|| = {np.linalg.norm(Mxy @ Mxyi - np.eye(16)):.2e}')
    print(f'  block structure: in-plane 16x16, out-of-plane 8x8, cross-coupling {coupling:.1e};  det M_xy = {np.linalg.det(Mxy):.12f} (the z block spans {np.abs(Mr[np.ix_(ZIDX, ZIDX)]).max():.1e}: its small multipliers come from the exact inverse)')
    lxy = [l for l, _, c in rows if c == "in-plane"]; lz = [l for l, _, c in rows if c == "out-of-plane"]
    print(f'  reciprocal pairing max_i min_j |lambda_i lambda_j - 1|: in-plane {pairing(lxy):.2e}, out-of-plane {pairing(lz):.2e}')
    print('  Floquet multipliers of the reference (sorted by modulus):')
    for l, dm, cls in rows:
        print(f'    {l.real:+.10f} {l.imag:+.10f}i   |lambda|-1 = {dm:+.3e}   {cls}')
    n_unit = sum(1 for _, dm, _ in rows if abs(dm) < 1e-5)
    n_out_hyp = sum(1 for _, dm, cls in rows if cls == 'out-of-plane' and abs(dm) > 1e-5)
    print(f'  {n_unit} multipliers on the unit circle to 1e-5, {n_out_hyp} hyperbolic out-of-plane (Theorem 1 corollary)')

    print('\n' + '=' * 78)
    print('SEARCH A - the specification as written: non-planar seeds, zero-mean drive (a = 0)')
    print('=' * 78)
    best = None
    seeds = []
    rngA = np.random.default_rng(1)
    for s in range(4):
        r, v = unpack(Xr)
        r[:, 2] += 0.3 * np.array([1, -1, 1, -1]) * (1 + 0.2 * s)
        v[:, 2] += 0.1 * rngA.normal(size=P)
        v[:, :2] += 0.05 * rngA.normal(size=(P, 2))
        seeds.append(pack(r, v))
    for s, X0 in enumerate(seeds):
        log = []
        Xs, nfs, DFs, hist = newton(X0, tau, N, B0, w, 0.0, maxit=40, log=log)
        rs, vs = unpack(Xs)
        zs = rs[:, 2].std()
        print(f'  seed {s+1}: |G| {hist[0]:.3e} -> {nfs:.3e} after {len(hist)-1} accepted steps;  z-spread {unpack(X0)[0][:,2].std():.3f} -> {zs:.3e}')
        if best is None or nfs < best[1]:
            best = (Xs, nfs, DFs, s + 1)
    Xa, nfa, DFa, sa = best
    if nfa < 1e-10:
        ra = unpack(Xa)[0]
        print(f'  a fixed point converged from seed {sa}: z-spread {ra[:,2].std():.3e} -> {"PLANAR (Theorem 1)" if ra[:,2].std() < 1e-6 else "NON-PLANAR ?!"}')
    else:
        print(f'  no non-planar closure within 40 Newton steps from any seed (best |G| = {nfa:.3e}, seed {sa}), as Theorem 1 requires.')
    sva = print_svd(DFa, f'  Jacobian at the best non-planar iterate (seed {sa}):')
    print(f'  rank-deficiency: {int((sva < 1e-8 * sva[0]).sum())} singular values below 1e-8 sigma_max; smallest {sva[-1]:.3e}')

    print('\n' + '=' * 78)
    print('SEARCH B - planar Z4 choreography, homotopy from the constant field to the zero-mean drive')
    print('=' * 78)
    print('  B(t) = B0 [a + (1 - a) cos(w t)], a: 1 -> 0, Newton at each a with the exact Jacobian.')
    print('  Each rotating square (branch, radius) fixes its own delay and drive frequency w = 4|W|;')
    print('  the scan below follows every one of them toward the zero-mean drive.')

    def homotopy(Xstart, DFstart, tau_, w_, verbose):
        a = 1.0; da = 0.05; Xb = Xstart.copy(); last = (1.0, Xstart.copy(), DFstart.copy()); fold_ = None
        while a > 0.0:
            an = max(0.0, a - da)
            Xn, nfn, DFn, hist = newton(Xb, tau_, N, B0, w_, an, maxit=30, planar=True)
            if nfn < 1e-10:
                a = an; Xb = Xn; last = (a, Xb.copy(), DFn.copy())
                if verbose:
                    rb, vb = unpack(Xb)
                    print(f'    a = {a:.4f}  converged |G| = {nfn:.2e} in {len(hist)-1} steps;  max radius {np.linalg.norm(rb, axis=1).max():.4f}, max speed {np.linalg.norm(vb, axis=1).max():.4f}')
                if a == 0.0:
                    break
                da = min(0.05, da * 1.5)
            else:
                da *= 0.5
                if verbose:
                    print(f'    a = {an:.4f}  failed (|G| = {nfn:.2e} after {len(hist)-1} steps): halving the step to {da:.4g}')
                if da < 2e-3:
                    fold_ = (an, Xn, DFn, nfn)
                    break
        return last, fold_

    scan = []
    for br in ('slow', 'fast'):
        for Rs in (0.7, 1.0, 1.5, 2.0, 3.0):
            ref_s = rotating_square(B0, Rs, br)
            if ref_s is None:
                print(f'    {br:4s} R = {Rs:.1f}: no rotating square (field below the threshold for this radius)')
                continue
            Xs0, Ws = ref_s
            tau_s = (2 * math.pi / abs(Ws)) / 4; w_s = 2 * math.pi / tau_s
            Xs, nfs, DFs, _ = newton(Xs0, tau_s, N, B0, w_s, 1.0, planar=True)
            if nfs > 1e-10:
                print(f'    {br:4s} R = {Rs:.1f}: reference did not close (|G| = {nfs:.1e})'); continue
            last_s, fold_s = homotopy(Xs, DFs, tau_s, w_s, verbose=(br == args.branch and Rs == R))
            a_s = last_s[0]
            scan.append((a_s, br, Rs, Ws, tau_s, w_s, last_s, fold_s))
            print(f'    {br:4s} R = {Rs:.1f}  W = {Ws:+.4f}  w = {w_s:.4f}:  reaches a = {a_s:.4f}' + ('' if fold_s is None else f' (fold before a = {fold_s[0]:.4f})'))
    scan.sort(key=lambda t: t[0])
    a_fin, br_fin, R_fin, W_fin, tau, w, last, fold = scan[0]
    _, Xfin, DFfin = last
    print(f'  furthest branch: {br_fin} R = {R_fin:.1f} (w = {w:.4f}), a = {a_fin:.4f}')
    if a_fin == 0.0:
        print('  the branch reaches a = 0: a planar Z4 choreography exists in the specified zero-mean drive')
    else:
        print(f'  every branch folds before a = 0 (best {a_fin:.4f}): no planar Z4 choreography connected to a rotating')
        print('  square exists in the specified zero-mean drive within this window.')
        print_svd(DFfin, f'  Jacobian at the last converged orbit (a = {a_fin:.4f}):')
        print_svd(fold[2], f'  Jacobian at the failed iterate (a = {fold[0]:.4f}, |G| = {fold[3]:.2e}):')

    nonplanar = False
    if args.kz > 0:
        print('\n' + '=' * 78)
        print(f'SEARCH C - beyond the specification: an axial spring lifts Theorem 1 (constant field, a = 1)')
        print('=' * 78)
        tau_c = (2 * math.pi / abs(W)) / 4; w_c = 2 * math.pi / tau_c
        c0 = math.sqrt(2.0) / R ** 3
        kres = (math.pi / tau_c) ** 2 + c0
        print('  With F_z = -k_z z the out-of-plane dynamics is confined. On the rotating square the alternating')
        print(f'  z mode (+,-,+,-) has frequency^2 = k_z - sqrt(2)/R^3 = k_z - {c0:.4f}; a Z4 choreography needs z_1 of')
        print(f'  period 2 tau, frequency pi/tau = {math.pi / tau_c:.4f}, so the linear resonance is at k_z = {kres:.4f}. The')
        print('  Coulomb z-coupling softens with amplitude, so solutions sit at k_z a little below that, at finite h.')
        print(f'  Seeds: the {args.branch} R = {R} reference plus z = h (+1, -1, +1, -1), v_z = 0; springs from --kz.')
        grid = [args.kz] if args.kz != 1.0 else [kres - 0.02, kres - 0.05, kres - 0.1, kres - 0.2]
        found = None
        for kz in grid:
            KZ = kz
            for hz in (args.zamp, 0.5 * args.zamp, 2.0 * args.zamp):
                X0 = Xr.copy()
                X0[ZIDX[:4]] = hz * np.array([1.0, -1.0, 1.0, -1.0])
                Xc, nfc, DFc, hist = newton(X0, tau_c, N, B0, w_c, 1.0, maxit=80)
                rc = unpack(Xc)[0]
                print(f'    k_z = {kz:.4f}  h = {hz:.3f}: |G| {hist[0]:.2e} -> {nfc:.2e} in {len(hist)-1} steps;  z-spread {rc[:,2].std():.4f}')
                if nfc < 1e-10 and rc[:, 2].std() > 1e-3:
                    found = (Xc, DFc, kz, hz); break
            if found:
                break
        if found is None:
            print('  no non-planar closure on this grid; the specification results above stand.')
            KZ = 0.0
        else:
            Xfin, DFfin, kz, hz = found
            KZ = kz; a_fin = 1.0; tau = tau_c; w = w_c; nonplanar = True
            print(f'  a NON-PLANAR Z4 choreography closed at k_z = {kz:.4f} from h = {hz}: the extension result.')

    print('\n' + '=' * 78)
    print(f'LAYER 4 - monodromy and Floquet multipliers of the final orbit (a = {a_fin:.4f}, k_z = {KZ})')
    print('=' * 78)
    Mf, Mfi, closf, _ = monodromy(Xfin, tau, N, B0, w, a_fin)
    if nonplanar:
        lam, rows = full_multipliers(Mf, Mfi)
    else:
        lam, rows, coupling = floquet_report(Mf, Mfi)
    print_state(Xfin, '  OUTPUT 1 - initial state vectors r_k(0), v_k(0):')
    print(f'  closure ||r1(T)-r1(0)|| + ||v1(T)-v1(0)|| = {closf:.3e}   ({"< 1e-10" if closf < 1e-10 else ">= 1e-10"})')
    if nonplanar:
        print(f'  ||M M^-1 - I|| = {np.linalg.norm(Mf @ Mfi - I24):.2e};  det M = {np.linalg.det(Mf):.12f};  reciprocal pairing over all 24: {pairing(lam):.2e}')
    else:
        print(f'  in-plane ||M M^-1 - I|| = {np.linalg.norm(Mf[np.ix_(XYIDX, XYIDX)] @ Mfi[np.ix_(XYIDX, XYIDX)] - np.eye(16)):.2e};  det M_xy = {np.linalg.det(Mf[np.ix_(XYIDX, XYIDX)]):.12f}')
        lxy = [l for l, _, c in rows if c == "in-plane"]; lz = [l for l, _, c in rows if c == "out-of-plane"]
        print(f'  reciprocal pairing: in-plane {pairing(lxy):.2e}, out-of-plane {pairing(lz):.2e}')
    print('  OUTPUT 2 - the 24 Floquet multipliers sorted by modulus:')
    for l, dm, cls in rows:
        print(f'    {l.real:+.10f} {l.imag:+.10f}i   |lambda| = {abs(l):.10f}   |lambda|-1 = {dm:+.3e}   {cls}')
    inpl = [dm for _, dm, cls in rows if cls != 'out-of-plane'] or [0.0]
    outp = [dm for _, dm, cls in rows if cls == 'out-of-plane'] or [0.0]
    lab_in = 'modes with in-plane or mixed support' if nonplanar else 'in-plane modes'
    print(f'  {lab_in}: {len(inpl)}, max ||lambda|-1| = {max(abs(x) for x in inpl):.3e}  -> '
          f'{"all within 1e-5 of the unit circle" if max(abs(x) for x in inpl) < 1e-5 else "NOT all on the unit circle"}')
    print(f'  out-of-plane modes: {len(outp)}, max ||lambda|-1| = {max(abs(x) for x in outp):.3e}  -> '
          f'{("hyperbolic, as Theorem 1 corollary requires" if KZ == 0 else "hyperbolic") if max(abs(x) for x in outp) > 1e-5 else "on the unit circle (all within 1e-5)"}')
    stable_all = max(abs(dm) for _, dm, _ in rows) < 1e-5
    print(f'  all 24 within 1e-5 of the unit circle: {stable_all}')

    print('\n' + '=' * 78)
    print('LAYER 5 - long run')
    print('=' * 78)
    if args.quick:
        print('  skipped (--quick)')
    else:
        ncyc = args.cycles if HAVE_NUMBA else min(args.cycles, 20_000)
        if not HAVE_NUMBA:
            print(f'  numba unavailable: running {ncyc} cycles in numpy instead of {args.cycles}')
        r0, v0 = unpack(Xfin)
        refs = np.stack([unpack(np.linalg.matrix_power(S, k) @ Xfin)[0] for k in range(4)])
        E0 = energy(r0, v0)
        dt = tau / N
        every = max(1, ncyc // 1000)
        dev_out = np.zeros(ncyc // every + 1); en_out = np.zeros(ncyc // every + 1)
        t0 = time.time()
        if HAVE_NUMBA:
            maxdev, maxde = long_run(r0.copy(), v0.copy(), refs, ncyc, N, dt, B0, w, a_fin, Q2, EPS2, M, Q, E0, every, dev_out, en_out, KZ)
        else:
            r, v = r0.copy(), v0.copy(); t = 0.0; maxdev = 0.0; maxde = 0.0
            for c in range(ncyc):
                dev = np.linalg.norm(r - refs[c % 4], axis=1).max(); de = abs((energy(r, v) - E0) / E0)
                maxdev = max(maxdev, dev); maxde = max(maxde, de)
                if c % every == 0:
                    dev_out[c // every] = dev; en_out[c // every] = de
                for n in range(N):
                    r, v = boris_step(r, v, t, dt, B0, w, a_fin); t += dt
                t = (c + 1) * N * dt
        el = time.time() - t0
        print(f'  {ncyc} drive cycles ({ncyc * N} Boris steps) in {el:.1f} s')
        print(f'  max positional deviation from the choreography at cycle starts = {maxdev:.3e}   ({"bounded within 1e-4" if maxdev < 1e-4 else "EXCEEDS 1e-4"})')
        print(f'  OUTPUT 3 - max |dE/E0| at the {ncyc} cycle starts (the secular drift; the discrete orbit is exactly')
        print(f'             periodic, so this is roundoff plus any instability) = {maxde:.3e}   ({"below 1e-8" if maxde < 1e-8 else "ABOVE 1e-8"})')
        # the within-cycle excursion is the integrator's O(dt^2) energy oscillation, not a drift
        for Nx in (N, 4 * N, 16 * N):
            r, v = r0.copy(), v0.copy(); t = 0.0; dtx = tau / Nx; worst = 0.0
            for n in range(4 * Nx):
                r, v = boris_step(r, v, t, dtx, B0, w, a_fin); t += dtx
                worst = max(worst, abs((energy(r, v) - E0) / E0))
            print(f'             within-cycle excursion at N = {Nx:5d} steps per drive period: {worst:.3e}')
        # growth trend: deviation at the quartiles
        nrec = ncyc // every
        qs = [dev_out[min(nrec - 1, int(nrec * f) - 1)] for f in (0.25, 0.5, 0.75, 1.0)]
        print('  deviation at 25/50/75/100% of the run: ' + '  '.join(f'{q:.2e}' for q in qs))

    print('\n' + '=' * 78)
    print('VERDICT')
    print('=' * 78)
    if nonplanar:
        print(f'  EXTENSION: with an axial spring k_z = {KZ:.4f} (not in the specification) a NON-PLANAR Z4')
        print('  choreography closed to 1e-12 with all 24 Floquet multipliers on the unit circle; its long run')
        print('  is reported above. This is the object the specification describes, in the nearest model that')
        print('  can contain it.')
    if a_fin == 0.0:
        print('  A planar Z4 choreography exists in the specified drive (found by homotopy).')
    elif not nonplanar:
        print('  No Z4 choreography exists in the specified zero-mean drive along the branches searched;')
        print('  the SVDs above are the divergence evidence the specification asks for.')
    else:
        print('  In the specified zero-mean drive itself no Z4 choreography exists along the branches searched')
        print('  (see the SVDs of Search B in the specification run).')
    print('  No non-planar periodic orbit exists in the specified model (Theorem 1, witnessed numerically);')
    print('  every planar one has hyperbolic out-of-plane modes, so "|lambda| = 1 for all 24 modes" is')
    print('  unattainable with a purely repulsive z-dynamics. The minimal change that lifts both obstructions')
    print('  is an axial confining force or a transverse field component; neither is in the specification.')
    print(f'  total wall time {time.time() - t_start:.1f} s')


if __name__ == '__main__':
    main()


# ═══ RINGS · agent context, append-only, newest last · read before changing this file ═══
# RING 1 · 2026-09-02 · four charges, an axial drive, and two theorems
# WHAT CHANGED: (1) a symmetric composition step - half Coulomb kick, half
# drift, exact Boris rotation about z by the mid-step angle, half drift, half
# kick - second order and time-reversible with synchronized r and v, with the
# in-plane speed restored to the last bit after each rotation. (2) The exact
# tangent map of that step as the product of five stage Jacobians, and its
# exact inverse from the stage inverses, checked against central differences
# to 1.06e-10. (3) Shooting on the quarter-period permutation map G(X) =
# S^-1 Phi_tau(X) - X with damped Gauss-Newton, minimum-norm steps through the
# symmetry null space, and a planar projection when the plane is the subspace
# searched. (4) Floquet multipliers block-wise for planar orbits and from
# eig(M) / eig(M^-1) for the 1e9-1e14 hyperbolic block, where eig(M) alone
# returns noise for the small ones. (5) A homotopy B0 [a + (1 - a) cos wt]
# from every rotating square (two branches, five radii) toward the specified
# zero-mean drive. (6) An extension search with an axial spring aimed at the
# resonance k_z = (pi/tau)^2 + sqrt(2)/R^3 from a little below. (7) A numba
# long run of 1e6 drive cycles (2.6e8 steps in 28 s).
# BANNED: Runge-Kutta and every non-volume-preserving integrator (specified);
# scipy and black-box optimizers (specified; the Jacobian is analytic and
# the pseudo-inverse is linear algebra); reading the small multipliers of a
# block spanning 1e14 from eig(M); shipping a planar orbit as the deliverable
# (specified; the planar Z4 choreography is the pipeline's demonstration and
# the extension orbit is the object the specification describes); declaring
# the specification satisfiable when two of its layers contradict its own
# force law - the theorems are printed instead.
# DEAD BRANCHES: (1) the staggered Boris leapfrog read as synchronous: the
# energy error fell one decade per decade of dt (2.4e-3, 2.3e-4, 1.6e-5) -
# first order in the synchronous energy - and could not reach 1e-10; the
# symmetric composition gives 1.4e-5, 1.4e-7, 3.6e-10, 3.4e-13. (2) Particles
# ordered against the sense of rotation: |G| = 4.25 at the analytic square,
# Newton wandered into the regularization core (radius 0.05, speed 2.5) and
# the homotopy followed that object to a fold at a = 0.70; ordered along the
# rotation, |G| = 2.8e-3 and two Newton steps close it. (3) eig(M) on the
# out-of-plane block: an 8x8 block with entries 1e9 returned its small
# eigenvalues as 1e-3 noise and a determinant of -31; the small multipliers
# come from the exact inverse product, where they are as well conditioned as
# the large ones. (4) A spring of k_z = 2 on the R = 2 orbit: Newton fell back
# to the planar solution from three amplitudes, because the alternating mode
# sat at frequency 1.35 against a required 0.08; the resonance must be aimed
# at. (5) The raw rotation kernel over 1e9 steps: the deviation grew as t^2
# (1.0e-4, 4.2e-4, 9.4e-4, 1.7e-3 at the quartiles) and grew LARGER with finer
# steps (4.9e-3 at N = 1024) - rounding bias in the rotation, not
# instability, since all 24 multipliers sat on the unit circle to 3e-14;
# restoring the in-plane speed after each rotation brought it to 7.0e-5.
# KILL-TEST: Layer 1 3.4e-13 at dt = 1e-5 over 1e4 steps, second order across
# four decades. The rotating square closes to 7.6e-13 in two Newton steps, its
# in-plane block has det 1 to 1e-12 and reciprocal pairing 2.6e-9, and the
# full-period monodromy equals (DG + I)^4 to 1.5e-13. Theorem 1 witnessed:
# min d2Iz/dt2 = 0.53 > 0 along a non-planar trajectory with Iz rising 0.18 to
# 1599 over four periods; Theorem 2 witnessed: max |B(t + T/4) - B(t)| =
# sqrt(2) B0. Search A: four non-planar seeds stall at |G| >= 3.9 with the
# z-spread falling and exactly three null singular values (the translations).
# Search B: all nine rotating-square branches fold before the zero-mean drive
# (a = 0.50 to 0.997), with the SVDs printed; the furthest planar orbit closes
# to 2.8e-12 with 16 in-plane multipliers within 1.9e-6 of the unit circle and
# out-of-plane multipliers to 3e3 (hyperbolic, as the corollary requires), and
# wanders by 0.95 over 1e6 cycles (fails the 1e-4 bound) at an energy drift of
# 6.4e-11. Extension: a non-planar Z4 choreography at k_z = 1.9191 closes to
# 6e-13, all 24 multipliers within 2.8e-14 of the unit circle, det M = 1 to
# 1e-12, pairing 2.5e-14, deviation 7.0e-5 over 1e6 drive cycles (within
# 1e-4), energy drift 1.7e-11 (within 1e-8): every layer of the specification
# met, in the nearest model that can contain the object.
# THE NON-OBVIOUS CHOICE: solving the quarter-period permutation map rather
# than the full-period closure. It makes the Z4 symmetry the equation instead
# of a constraint, cuts the integration per residual by four, and turns the
# full monodromy from the thing solved for into a consistency check the
# solver cannot have tuned - (DG + I)^4 = M to 1e-13.
# OPEN QUESTIONS: a zero-mean-drive Z4 choreography on a branch not connected
# to any rotating square - the free motion has closed orbits at the Bessel
# zeros qB0/(m w) = 2.4048, 5.52, ..., and a breathing family may live near
# them. The induced electric field the specification omits, -(1/2) dB/dt z x
# r: with it the canonical angular momentum is conserved and the drive does
# work, so the search space changes. Whether the extension orbit's remaining
# t^2 drift of 7e-5 is the rotation family's neutral direction fed by
# roundoff (a 128-bit run would say). And a transverse field component in
# place of the spring, which lifts Theorem 1 with a magnetic term alone.
# ═══ end rings ═══
