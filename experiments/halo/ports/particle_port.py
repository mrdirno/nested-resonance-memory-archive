#!/usr/bin/env python3
"""Numpy port of the Resonance Chamber PARTICLE DYNAMICS (velMat/posMat shaders).

Faithful to resonance-chamber.html:
  velocity pass : F = amp*fscale*cavityForce(modeB)  (blend=1, hard mode jumps)
                  + hubble*p + mag*30*cross(v, B),  B=(0,0.35,0)  (no centers)
                  |F| clamped to 500
                  v = (v + F*dt)*exp(-damping*dt)
                  reflect-boundary: predictive wall reflection, restitution 0.5
  position pass : p += v*dt; reflect -> p*=R/r ; wrap -> antipodal re-entry
  field         : wells  F = -grad(Psi), Psi = j_l(z r/R) P_l^m(ct) cos(m phi - tw)
                  chladni S = term(m, tw) - term(m2, tw+pi/2), F = -S grad(S)
                  radial j_l lookup table (1024 samples, lerped) normalized to peak 1
                  Schmidt-normalized Legendre, Condon-Shortley dropped
  modes         : digit-driven cavityModeAt(step), step advances every 1/stepsPerSec
                  of sim time; twist phase = omega*simTime,
                  omega = (0.10+0.06m)*(+1 if n odd else -1) when cosmos.twist
"""
import math, json, re, sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "resonance-chamber.html")

EXTENT = 15.0
FORCE_SCALE = 130.0
CHLADNI_SCALE = 100.0
RESTITUTION = 0.5
RAD_N = 1024
L_MAX, N_MAX = 9, 6
DT = 1.0 / 30.0

# ---------------- digits (validated in replica_sweep.py) ----------------
src = open(HTML).read()
DEC = {}
for key in ("pi", "e", "sqrt2", "phi"):
    m = re.search(key + r":\s*'([0-9]+)'", src)
    DEC[key] = m.group(1)
for k, v in DEC.items():
    assert len(v) == 2500, (k, len(v))

PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
          73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,
          151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,
          233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,
          317,331,337,347,349,353,359,367,373,379,383,389,397,401,409,
          421,431,433,439,443,449,457,461,463,467,479,487,491,499]

_digit_cache = {}
def digitsFor(constKey, base):
    ck = (constKey, base)
    if ck in _digit_cache:
        return _digit_cache[ck]
    dec = DEC[constKey]
    if base == 10:
        out = [ord(c) - 48 for c in dec]
    else:
        count = math.floor(len(dec) * math.log(10.0) / math.log(base)) - 4
        denom = 10 ** len(dec)
        frac = int(dec)
        out = []
        for _ in range(count):
            frac *= base
            out.append(frac // denom)
            frac %= denom
    _digit_cache[ck] = out
    return out

def jsround(x):
    return math.floor(x + 0.5)

# ---------------- Bessel machinery (port of sphj/besselZeros) ----------------
def sphj(l, x):
    if x < 1e-9:
        return 1.0 if l == 0 else 0.0
    lmax = l + 16 + math.ceil(x)
    jp1 = 0.0; j = 1e-30; target = 0.0
    for i in range(lmax, 0, -1):
        jm1 = ((2 * i + 1) / x) * j - jp1
        jp1 = j; j = jm1
        if i - 1 == l:
            target = j
        if abs(j) > 1e20:
            j *= 1e-20; jp1 *= 1e-20; target *= 1e-20
    if j == 0.0:                # JS would give Infinity; emulate with a tiny denom
        j = 1e-300
    return target * ((math.sin(x) / x) / j)

def sphjDeriv(l, x):
    if x < 1e-9:
        return 1.0/3.0 if l == 1 else 0.0
    if l == 0:
        return -sphj(1, x)
    return sphj(l - 1, x) - ((l + 1) / x) * sphj(l, x)

def besselZeros(l, count):
    zeros = []
    x0, f0 = 0.1, sphj(l, 0.1)
    x = 0.15
    while x < 120 and len(zeros) < count:
        f = sphj(l, x)
        if f0 != 0 and math.copysign(1, f) != math.copysign(1, f0):
            a, b = x0, x
            for _ in range(60):
                mid = (a + b) / 2
                if math.copysign(1, sphj(l, mid)) == math.copysign(1, sphj(l, a)):
                    a = mid
                else:
                    b = mid
            zeros.append((a + b) / 2)
        x0, f0 = x, f
        x += 0.05
    return zeros

BESSEL_ZEROS = [besselZeros(l, N_MAX) for l in range(L_MAX + 1)]

def schmidt(l, m):
    if m == 0:
        return 1.0
    f = 1.0
    for k in range(l - m + 1, l + m + 1):
        f *= k
    return math.sqrt(2.0 / f)

_rad_cache = {}
def radial_profile(l, n):
    key = (l, n)
    hit = _rad_cache.get(key)
    if hit is not None:
        return hit
    z = BESSEL_ZEROS[l][n - 1]
    j = np.empty(RAD_N); dj = np.empty(RAD_N)
    peak = 1e-9
    for i in range(RAD_N):
        r = ((i + 0.5) / RAD_N) * EXTENT
        x = z * r / EXTENT
        jj = sphj(l, x)
        j[i] = jj
        dj[i] = (z / EXTENT) * sphjDeriv(l, x)
        peak = max(peak, abs(jj))
    j /= peak; dj /= peak
    _rad_cache[key] = (j, dj)
    return j, dj

def radial_at(r, tab_j, tab_dj):
    u = np.clip(r / EXTENT, 0.0, 1.0) * (RAD_N - 1.0)
    i0 = np.floor(u).astype(np.int64)
    f = u - i0
    i1 = np.minimum(i0 + 1, RAD_N - 1)
    jr = tab_j[i0] * (1.0 - f) + tab_j[i1] * f
    djr = tab_dj[i0] * (1.0 - f) + tab_dj[i1] * f
    return jr, djr

# ---------------- Legendre (port of GLSL legendreP, vectorized) ----------------
def legendreP(l, m, ct, st):
    pmm = np.ones_like(ct)
    for i in range(1, m + 1):
        pmm = pmm * (float(2 * i - 1) * st)
    plm = pmm
    plm1 = np.zeros_like(ct)
    if l > m:
        prev = pmm
        cur = ct * float(2 * m + 1) * pmm
        for k in range(2, 10):
            LL = m + k
            if LL > l:
                break
            nxt = (ct * float(2 * LL - 1) * cur - float(LL + m - 1) * prev) / float(LL - m)
            prev, cur = cur, nxt
        plm, plm1 = cur, prev
    P = plm
    dP = (float(l) * ct * plm - float(l + m) * plm1) / st
    return P, dP

def sh_term(pos, r, ct, st, phi, l, m, nrm, jr, djr, phase):
    P, dP = legendreP(l, m, ct, st)
    P = P * nrm; dP = dP * nrm
    a = float(m) * phi - phase
    ca = np.cos(a); sa = np.sin(a)
    val = jr * P * ca
    Fr = djr * P * ca
    Ft = (jr / r) * dP * ca
    Fp = -(jr / (r * st)) * P * float(m) * sa
    cp = np.cos(phi); sp = np.sin(phi)
    er = pos / r[:, None]
    et = np.stack([ct * cp, -st, ct * sp], axis=1)
    ep = np.stack([-sp, np.zeros_like(sp), cp], axis=1)
    grad = Fr[:, None] * er + Ft[:, None] * et + Fp[:, None] * ep
    return val, grad

def cavity_force(pos, mode, tab_j, tab_dj, twist, chladni):
    """Returns (force, S) where S is the field value particles feel."""
    rr = np.linalg.norm(pos, axis=1)
    jr, djr = radial_at(rr, tab_j, tab_dj)
    r = np.maximum(rr, 0.35)
    ct = np.clip(pos[:, 1] / r, -1.0, 1.0)
    st = np.maximum(np.sqrt(1.0 - ct * ct), 1e-3)
    phi = np.arctan2(pos[:, 2], pos[:, 0])
    n1 = schmidt(mode['l'], mode['m'])
    v1, g1 = sh_term(pos, r, ct, st, phi, mode['l'], mode['m'], n1, jr, djr, twist)
    if not chladni:
        return -g1, v1
    n2 = schmidt(mode['l'], mode['m2'])
    v2, g2 = sh_term(pos, r, ct, st, phi, mode['l'], mode['m2'], n2, jr, djr,
                     twist + 1.5707963)
    S = v1 - v2
    return -(S[:, None] * (g1 - g2)), S

# ---------------- state / mode sequencing ----------------
DEFAULT_STATE = {
    'fieldForm': 'chladni',
    'fieldExp': 0.0,
    'damping': 2.5,
    'stepsPerSec': 2.0,
    'base': 10,
    'constants': {'a': 'phi', 'b': 'phi', 'c': 'pi'},
    'strideIndex': 51,
    'hubble': 0.3,
    'mag': 0.6,
    'twist': True,
    'boundary': 'reflect',
    'particles': 4000,
    'seed': 12345,
    'fixedMode': None,   # (n,l,m) to freeze the sequencer (validation runs)
}

def offset_for(state, axis):
    stride = PRIMES[state['strideIndex']]
    return 0 if axis == 'a' else stride if axis == 'b' else stride * 2

def digit_at(state, axis, s):
    seq = digitsFor(state['constants'][axis], state['base'])
    idx = ((s + offset_for(state, axis)) % len(seq) + len(seq)) % len(seq)
    return seq[idx]

def cavity_mode_at(state, s):
    if state['fixedMode'] is not None:
        n, l, m = state['fixedMode']
        m2 = l - m
        if m2 == m and m > 0:
            m2 = m - 1
    else:
        u = lambda ax: digit_at(state, ax, s) / (state['base'] - 1)
        n = 1 + math.floor(u('a') * (N_MAX - 0.001))
        l = math.floor(u('b') * (L_MAX + 0.999))
        m = jsround(u('c') * l)
        m2 = l - m
        if m2 == m and m > 0:
            m2 = m - 1
    omega = (0.10 + 0.06 * m) * (1 if n % 2 else -1) if state['twist'] else 0.0
    return {'n': n, 'l': l, 'm': m, 'm2': m2, 'omega': omega}

# ---------------- the simulator ----------------
class Sim:
    def __init__(self, state):
        self.state = dict(DEFAULT_STATE)
        self.state.update(state)
        st = self.state
        rng = np.random.default_rng(st['seed'])
        N = st['particles']
        u = rng.random(N)
        r = EXTENT * 0.94 * np.cbrt(u)
        ct = 2 * rng.random(N) - 1
        stt = np.sqrt(1 - ct * ct)
        ph = rng.random(N) * 2 * np.pi
        self.p = np.stack([r * stt * np.cos(ph), r * ct, r * stt * np.sin(ph)], axis=1)
        self.v = np.zeros_like(self.p)
        self.step = 0
        self.stepAccum = 0.0
        self.simTime = 0.0
        self.amp = 10.0 ** st['fieldExp']
        self.chladni = st['fieldForm'] == 'chladni'
        self.fscale = CHLADNI_SCALE if self.chladni else FORCE_SCALE
        self.modeB = cavity_mode_at(st, 0)
        self.tab = radial_profile(self.modeB['l'], self.modeB['n'])
        self.switch_frames = []   # frame indices where the mode jumped
        self.lastS = None

    def frame(self, fi):
        st = self.state
        # sequencer (blend ramp ignored: hard jumps)
        self.stepAccum += DT * st['stepsPerSec']
        if self.stepAccum >= 1:
            jump = math.floor(self.stepAccum)
            self.stepAccum -= jump
            self.step += jump
            nm = cavity_mode_at(st, self.step)
            if (nm['n'], nm['l'], nm['m'], nm['m2']) != (
                    self.modeB['n'], self.modeB['l'], self.modeB['m'], self.modeB['m2']):
                self.switch_frames.append(fi)
            self.modeB = nm
            self.tab = radial_profile(nm['l'], nm['n'])
        self.simTime += DT
        twist = self.modeB['omega'] * self.simTime

        # ---- velocity pass ----
        F, S = cavity_force(self.p, self.modeB, self.tab[0], self.tab[1],
                            twist, self.chladni)
        self.lastS = S
        F = self.amp * self.fscale * F
        F += st['hubble'] * self.p
        if st['mag'] > 0.001:
            B = np.array([0.0, 0.35, 0.0])
            F += st['mag'] * 30.0 * np.cross(self.v, B)
        fmag = np.linalg.norm(F, axis=1)
        over = fmag > 500.0
        if over.any():
            F[over] *= (500.0 / fmag[over])[:, None]
        self.v = (self.v + F * DT) * math.exp(-st['damping'] * DT)
        if st['boundary'] == 'reflect':
            pn = self.p + self.v * DT
            rn = np.linalg.norm(pn, axis=1)
            out = rn > EXTENT
            if out.any():
                nrm = pn[out] / rn[out][:, None]
                vr = np.einsum('ij,ij->i', self.v[out], nrm)
                hit = vr > 0
                if hit.any():
                    idx = np.where(out)[0][hit]
                    self.v[idx] -= (1.0 + RESTITUTION) * vr[hit][:, None] * nrm[hit]

        # ---- position pass ----
        self.p = self.p + self.v * DT
        r = np.linalg.norm(self.p, axis=1)
        out = r > EXTENT
        if out.any():
            if st['boundary'] == 'reflect':
                self.p[out] *= (EXTENT / r[out])[:, None]
            else:
                e = np.minimum(r[out] - EXTENT, EXTENT * 0.5)
                self.p[out] = -self.p[out] * ((EXTENT - e) / r[out])[:, None]

    def probe_field(self, dirs, radii):
        """Inward radial field force (amp*fscale included) sampled on probe
        directions x radii for the CURRENT mode/twist. Returns f_in[r] =
        mean over dirs of max(0, -F.rhat)."""
        twist = self.modeB['omega'] * self.simTime
        out = np.empty(len(radii))
        for i, rr in enumerate(radii):
            pos = dirs * rr
            F, _ = cavity_force(pos, self.modeB, self.tab[0], self.tab[1],
                                twist, self.chladni)
            F = self.amp * self.fscale * F
            fm = np.linalg.norm(F, axis=1)
            ov = fm > 500.0
            if ov.any():
                F[ov] *= (500.0 / fm[ov])[:, None]
            rad = np.einsum('ij,ij->i', F, dirs)
            out[i] = np.mean(np.maximum(0.0, -rad))
        return out

# ---------------- metrics ----------------
def pearson(a, b):
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    a = a - a.mean(); b = b - b.mean()
    d = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0

def radial_metrics(r, nbins=48):
    cnt, edges = np.histogram(r, bins=nbins, range=(0, EXTENT))
    p = cnt / max(1, cnt.sum())
    nz = p[p > 0]
    ent = float(-(nz * np.log(nz)).sum() / math.log(nbins))
    mid = 0.5 * (edges[1:] + edges[:-1])
    shell = cnt / (mid ** 2)          # ~ density per volume
    pk = int(np.argmax(shell))
    return {'r_entropy': ent, 'r_mean': float(r.mean()), 'r_std': float(r.std()),
            'shell_peak_r': float(mid[pk]),
            'shell_peak_ratio': float(shell[pk] / max(1e-9, shell.mean())),
            'wall_frac': float((r > 0.98 * EXTENT).mean())}

def quadrupole(pos):
    r = np.linalg.norm(pos, axis=1)
    n = pos / np.maximum(r, 1e-9)[:, None]
    Q = 3.0 * (n[:, :, None] * n[:, None, :]).mean(axis=0) - np.eye(3)
    return float(np.sqrt((Q * Q).sum()))

def grid_hist(pos, ngrid=12):
    H, _ = np.histogramdd(pos, bins=(ngrid,) * 3,
                          range=[(-EXTENT, EXTENT)] * 3)
    return H

def parity_metrics(pos, ngrid=12):
    H = grid_hist(pos, ngrid)
    Hf = H[::-1, ::-1, ::-1]
    ac = pearson(H, Hf)
    He = 0.5 * (H + Hf); Ho = 0.5 * (H - Hf)
    He = He - He.mean()
    tot = (He * He).sum() + (Ho * Ho).sum()
    return {'antip_corr': ac,
            'odd_frac': float((Ho * Ho).sum() / max(1e-9, tot))}

def pair_g(pos, rng, nsub=1200, nbins=60):
    """g-ratio(r): pair-distance histogram / same-radii-random-angle surrogate."""
    N = len(pos)
    idx = rng.choice(N, size=min(nsub, N), replace=False)
    P = pos[idx]
    r = np.linalg.norm(P, axis=1)
    ct = 2 * rng.random(len(P)) - 1
    stt = np.sqrt(1 - ct * ct)
    ph = rng.random(len(P)) * 2 * np.pi
    Q = np.stack([r * stt * np.cos(ph), r * ct, r * stt * np.sin(ph)], axis=1)
    def pd(X):
        d = X[:, None, :] - X[None, :, :]
        dd = np.sqrt((d * d).sum(-1))
        iu = np.triu_indices(len(X), 1)
        return dd[iu]
    hd, edges = np.histogram(pd(P), bins=nbins, range=(0, 2 * EXTENT))
    hs, _ = np.histogram(pd(Q), bins=nbins, range=(0, 2 * EXTENT))
    ratio = hd / np.maximum(1.0, hs)
    mid = 0.5 * (edges[1:] + edges[:-1])
    ok = hs > 50
    if not ok.any():
        return {'g_peak': 1.0, 'g_peak_r': 0.0}
    j = int(np.argmax(np.where(ok, ratio, 0)))
    return {'g_peak': float(ratio[j]), 'g_peak_r': float(mid[j])}

def run_and_measure(state, frames=600, warm=150, tag='', probe=True):
    sim = Sim(state)
    rng = np.random.default_rng(999)
    Hs_pre_switch = []           # grid hist just before each mode switch
    Hs_mid = []                  # mid-dwell hists (stationarity)
    fin_acc = None; fin_n = 0
    radii = np.linspace(0.5, EXTENT - 0.05, 40)
    dirs = fib_sphere(192)
    absS = []
    next_probe = warm
    fps = None
    if state.get('stepsPerSec', DEFAULT_STATE['stepsPerSec']) > 0:
        fps = max(1, round(1.0 / (DT * (state.get('stepsPerSec') or 2.0))))
    for fi in range(frames):
        # capture pre-switch structure: mode advances when stepAccum>=1
        will_switch = (sim.stepAccum + DT * sim.state['stepsPerSec']) >= 1
        if will_switch and fi >= warm:
            Hs_pre_switch.append(grid_hist(sim.p))
        sim.frame(fi)
        if fi >= warm and fps and (fi % fps) == fps // 2:
            Hs_mid.append(grid_hist(sim.p))
        if probe and fi >= next_probe:
            f = sim.probe_field(dirs, radii)
            fin_acc = f if fin_acc is None else fin_acc + f
            fin_n += 1
            next_probe += 30
        if fi >= warm and sim.lastS is not None:
            absS.append(float(np.abs(sim.lastS).mean()))
    r = np.linalg.norm(sim.p, axis=1)
    met = radial_metrics(r)
    met.update(parity_metrics(sim.p))
    met['quad'] = quadrupole(sim.p)
    met.update(pair_g(sim.p, rng))
    met['speed_mean'] = float(np.linalg.norm(sim.v, axis=1).mean())
    met['absS_end'] = absS[-1] if absS else None
    # persistence across mode switches / stationarity
    pc = [pearson(Hs_pre_switch[i], Hs_pre_switch[i + 1])
          for i in range(len(Hs_pre_switch) - 1)]
    met['persist'] = float(np.mean(pc)) if pc else None
    sc = [pearson(Hs_mid[i], Hs_mid[i + 1]) for i in range(len(Hs_mid) - 1)]
    met['stationarity'] = float(np.mean(sc)) if sc else None
    # terminal-radius prediction: largest r where mean inward field force
    # >= hubble*r  (both measured from the ported dynamics)
    if probe and fin_n:
        fin = fin_acc / fin_n
        hub = sim.state['hubble'] * radii
        cross = np.where(fin >= hub)[0]
        met['r_balance'] = float(radii[cross[-1]]) if len(cross) else 0.0
        met['fin_at_peak'] = float(np.interp(met['shell_peak_r'], radii, fin))
        met['hub_at_peak'] = float(sim.state['hubble'] * met['shell_peak_r'])
    met['tag'] = tag
    return met, sim

def fib_sphere(n):
    i = np.arange(n) + 0.5
    ph = math.pi * (3 - math.sqrt(5)) * i
    ct = 1 - 2 * i / n
    stt = np.sqrt(1 - ct * ct)
    return np.stack([stt * np.cos(ph), ct, stt * np.sin(ph)], axis=1)

# ---------------- math validation ----------------
def validate_math():
    # digits: pi in hex
    frac = int(DEC['pi']); denom = 10 ** 2500
    ref = (frac * 16 ** 8) // denom
    got = 0
    for h in digitsFor('pi', 16)[:8]:
        got = got * 16 + h
    assert got == ref and hex(got) == '0x243f6a88', hex(got)
    # sphj vs exact closed forms
    for x in (0.3, 1.7, 6.1, 20.5):
        assert abs(sphj(0, x) - math.sin(x) / x) < 1e-12
        j1 = math.sin(x) / x**2 - math.cos(x) / x
        assert abs(sphj(1, x) - j1) < 1e-12
    assert abs(BESSEL_ZEROS[0][0] - math.pi) < 1e-9
    assert abs(BESSEL_ZEROS[0][1] - 2 * math.pi) < 1e-9
    # legendre vs exact (CS dropped): P_2^1 = 3 ct st ; P_3^1 = 1.5(5ct^2-1) st
    ct = np.array([0.3, -0.7, 0.9]); stt = np.sqrt(1 - ct * ct)
    P, dP = legendreP(2, 1, ct, stt)
    assert np.allclose(P, 3 * ct * stt, atol=1e-12)
    P, _ = legendreP(3, 1, ct, stt)
    assert np.allclose(P, 1.5 * (5 * ct**2 - 1) * stt, atol=1e-12)
    # gradient of sh_term vs finite differences (chladni S too)
    rng = np.random.default_rng(7)
    pos = (rng.random((6, 3)) - 0.5) * 18
    mode = {'n': 2, 'l': 3, 'm': 1, 'm2': 2, 'omega': 0.0}
    tj, tdj = radial_profile(3, 2)
    eps = 1e-4
    F0, S0 = cavity_force(pos, mode, tj, tdj, 0.37, True)
    for k in range(3):
        pp = pos.copy(); pp[:, k] += eps
        pm = pos.copy(); pm[:, k] -= eps
        _, Sp = cavity_force(pp, mode, tj, tdj, 0.37, True)
        _, Sm = cavity_force(pm, mode, tj, tdj, 0.37, True)
        # F = -S grad S = -grad(S^2/2)
        num = -(Sp**2 - Sm**2) / (4 * eps)
        ok = np.abs(num - F0[:, k]) < 2e-3 * (1 + np.abs(num))
        assert ok.all(), (k, num, F0[:, k])
    print("math validation OK (digits, sphj, zeros, legendre, grad-vs-FD)")

if __name__ == '__main__':
    validate_math()
