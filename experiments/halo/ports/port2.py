#!/usr/bin/env python3
"""Extension of particle_port.py to the CURRENT resonance-chamber.html velocity
shader.  Adds, relative to particle_port.py:

  * uAniso        F += uHubble * p * uAniso,
                  uAniso = (1-0.65*aniso, 1+1.3*aniso, 1-0.65*aniso)
  * uHelix        F += uHelix * 6.0 * vec3(-p.z, 0, p.x)      (when helix>0.001)
  * epoch/cascade every epochLen s of simTime, pendingRescale = 0.5 ('out') or
                  2.0 ('in') for EXACTLY one simStep; velocity pass ends with
                  v *= uRescale, position pass ends with p *= uRescale
                  (and the position pass consumes the ALREADY-rescaled v).
  * smooth blend  two live modes A=cavityModeAt(step-1), B=cavityModeAt(step);
                  F = amp*fscale*mix(FA,FB, blend), blend = min(1, stepAccum*4)
                  when smooth, else 1.  Separate twist phases omegaA*t, omegaB*t.
  * dt            configurable (page uses dtSim = min(dtWall, 1/20)).
  * startStep     the sequencer can start at an arbitrary digit index.

Frame ordering copies frame() in the html exactly:
  stepAccum += dt*stepsPerSec -> maybe advance step & pushModes
  blend = smooth ? min(1, stepAccum*4) : 1
  simTime += dt
  updateCosmos()   (epoch test on the NEW simTime; twist = omega*simTime)
  simStep(dt)
  pendingRescale = 1
"""
import math
import numpy as np

import particle_port as PP
from particle_port import (EXTENT, FORCE_SCALE, CHLADNI_SCALE, RESTITUTION,
                           L_MAX, N_MAX, PRIMES, digitsFor, schmidt,
                           radial_profile, radial_at, legendreP, jsround,
                           cavity_force)

# ----------------------------------------------------------------------------
# the user's preset ("Spinning chladni") as the BASELINE for every measurement
# ----------------------------------------------------------------------------
PRESET = dict(
    particles=4000,
    stepsPerSec=0.5,
    smooth=True,
    fieldForm='chladni',
    fieldExp=2.0,
    damping=1.0,
    base=10,
    constants={'a': 'phi', 'b': 'phi', 'c': 'phi'},
    offsetMode='auto',
    strideIndex=0,
    boundary='reflect',
    hubble=1.2,
    epoch=True,
    epochLen=10.0,
    mag=0.4,
    twist=True,
    aniso=0.55,
    helix=0.8,
    cascade='out',
    startStep=9028,
    seed=12345,
    dt=1.0 / 20.0,
    fixedMode=None,
)


def offset_for(st, axis):
    stride = PRIMES[st['strideIndex']]
    return 0 if axis == 'a' else stride if axis == 'b' else stride * 2


def digit_at(st, axis, s):
    seq = digitsFor(st['constants'][axis], st['base'])
    idx = ((s + offset_for(st, axis)) % len(seq) + len(seq)) % len(seq)
    return seq[idx]


def cavity_mode_at(st, s):
    if st.get('fixedMode') is not None:
        n, l, m = st['fixedMode']
        m2 = l - m
        if m2 == m and m > 0:
            m2 = m - 1
    else:
        u = lambda ax: digit_at(st, ax, s) / (st['base'] - 1)
        n = 1 + math.floor(u('a') * (N_MAX - 0.001))
        l = math.floor(u('b') * (L_MAX + 0.999))
        m = jsround(u('c') * l)
        m2 = l - m
        if m2 == m and m > 0:
            m2 = m - 1
    omega = (0.10 + 0.06 * m) * (1 if n % 2 else -1) if st['twist'] else 0.0
    return {'n': n, 'l': l, 'm': m, 'm2': m2, 'omega': omega}


def aniso_vec(a):
    return np.array([1.0 - 0.65 * a, 1.0 + 1.3 * a, 1.0 - 0.65 * a])


# ----------------------------------------------------------------------------
def field_S_and_grad(pos, mode, tab, twist):
    """S and grad(S) of the chladni superposition (no amp/fscale)."""
    rr = np.linalg.norm(pos, axis=1)
    jr, djr = radial_at(rr, tab[0], tab[1])
    r = np.maximum(rr, 0.35)
    ct = np.clip(pos[:, 1] / r, -1.0, 1.0)
    st_ = np.maximum(np.sqrt(1.0 - ct * ct), 1e-3)
    phi = np.arctan2(pos[:, 2], pos[:, 0])
    n1 = schmidt(mode['l'], mode['m'])
    v1, g1 = PP.sh_term(pos, r, ct, st_, phi, mode['l'], mode['m'], n1, jr, djr, twist)
    n2 = schmidt(mode['l'], mode['m2'])
    v2, g2 = PP.sh_term(pos, r, ct, st_, phi, mode['l'], mode['m2'], n2, jr, djr,
                        twist + 1.5707963)
    return v1 - v2, g1 - g2


class Sim:
    def __init__(self, state):
        st = dict(PRESET)
        st.update(state)
        self.st = st
        self.dt = st['dt']
        rng = np.random.default_rng(st['seed'])
        N = st['particles']
        r = EXTENT * 0.94 * np.cbrt(rng.random(N))
        ct = 2 * rng.random(N) - 1
        stt = np.sqrt(1 - ct * ct)
        ph = rng.random(N) * 2 * np.pi
        self.p = np.stack([r * stt * np.cos(ph), r * ct, r * stt * np.sin(ph)], axis=1)
        self.v = np.zeros_like(self.p)

        self.step = int(st['startStep'])
        self.stepAccum = 0.0
        self.simTime = 0.0
        self.lastEpochT = 0.0
        self.epochN = 0
        self.amp = 10.0 ** st['fieldExp']
        self.chladni = st['fieldForm'] == 'chladni'
        self.fscale = CHLADNI_SCALE if self.chladni else FORCE_SCALE
        self.anis = aniso_vec(st['aniso'])
        self.blend = 1.0
        self.rescale = 1.0
        self.switch_frames = []
        self.epoch_frames = []
        self._push_modes()

    def _push_modes(self):
        self.modeA = cavity_mode_at(self.st, self.step - 1)
        self.modeB = cavity_mode_at(self.st, self.step)
        self.tabA = radial_profile(self.modeA['l'], self.modeA['n'])
        self.tabB = radial_profile(self.modeB['l'], self.modeB['n'])

    def force(self, p, v):
        """Full velocity-pass force, pre-clamp (returns F, and S_B for metrics).
        For chladni it also caches S_B and grad(S_B) so the sheet metrics are
        free: F_chladni = -(S * grad S), so the same two evaluations serve both."""
        st = self.st
        twA = self.modeA['omega'] * self.simTime
        twB = self.modeB['omega'] * self.simTime
        if self.chladni:
            SB, GB = field_S_and_grad(p, self.modeB, self.tabB, twB)
            SA, GA = field_S_and_grad(p, self.modeA, self.tabA, twA)
            FB = -(SB[:, None] * GB)
            FA = -(SA[:, None] * GA)
            self.SB, self.GB = SB, GB
        else:
            FA, _ = cavity_force(p, self.modeA, self.tabA[0], self.tabA[1], twA, False)
            FB, SB = cavity_force(p, self.modeB, self.tabB[0], self.tabB[1], twB, False)
            self.SB, self.GB = SB, None
        b = self.blend
        Fchl = self.amp * self.fscale * ((1.0 - b) * FA + b * FB)
        Fflow = st['hubble'] * p * self.anis[None, :]
        if st['helix'] > 0.001:
            Fflow = Fflow.copy()
            Fflow[:, 0] += st['helix'] * 6.0 * (-p[:, 2])
            Fflow[:, 2] += st['helix'] * 6.0 * (p[:, 0])
        self.Fchl_mag = float(np.median(np.linalg.norm(Fchl, axis=1)))
        self.Fflow_mag = float(np.median(np.linalg.norm(Fflow, axis=1)))
        F = Fchl + Fflow
        if st['mag'] > 0.001:
            B = np.array([0.0, 0.35, 0.0])
            F = F + st['mag'] * 30.0 * np.cross(v, B)
        return F, SB

    def frame(self, fi=0):
        st, dt = self.st, self.dt
        # ---- sequencer ----
        self.stepAccum += dt * st['stepsPerSec']
        if self.stepAccum >= 1:
            jump = math.floor(self.stepAccum)
            self.stepAccum -= jump
            prev = (self.modeB['n'], self.modeB['l'], self.modeB['m'], self.modeB['m2'])
            self.step += jump
            self._push_modes()
            now = (self.modeB['n'], self.modeB['l'], self.modeB['m'], self.modeB['m2'])
            self.switch_frames.append((fi, prev != now))
        self.blend = min(1.0, self.stepAccum * 4.0) if st['smooth'] else 1.0

        self.simTime += dt
        # ---- updateCosmos: epoch rescale ----
        self.rescale = 1.0
        if st['epoch'] and self.simTime - self.lastEpochT >= st['epochLen']:
            self.lastEpochT = self.simTime
            self.epochN += 1
            self.rescale = 2.0 if st['cascade'] == 'in' else 0.5
            self.epoch_frames.append(fi)

        self.raw_pass()

    def raw_pass(self):
        """velocity pass + position pass with the CURRENT blend/rescale/simTime.
        Split out so the GPU ground-truth test can drive one pass directly."""
        st, dt = self.st, self.dt
        # ---- velocity pass ----
        F, SB = self.force(self.p, self.v)
        self.lastS = SB
        fmag = np.linalg.norm(F, axis=1)
        over = fmag > 500.0
        self.clamp_frac = float(over.mean())
        if over.any():
            F[over] *= (500.0 / fmag[over])[:, None]
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

        # ---- position pass (uses the already-rescaled v, as the shader does) ----
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

    # ---------------- measurement helpers ----------------
    def signed_sheet_distance(self, pos=None):
        """u = S/|grad S| for mode B: first-order signed distance to the nodal
        surface, in world units (cavity radius = 15)."""
        p = self.p if pos is None else pos
        tw = self.modeB['omega'] * self.simTime
        S, G = field_S_and_grad(p, self.modeB, self.tabB, tw)
        g = np.linalg.norm(G, axis=1)
        return S / np.maximum(g, 1e-9), S, g

    def uniform_absS(self, rng, n=4000):
        """<|S|> for a UNIFORM gas in the current mode: the 'unconverged'
        reference that makes <|S|> comparable across modes."""
        r = EXTENT * 0.94 * np.cbrt(rng.random(n))
        ct = 2 * rng.random(n) - 1
        stt = np.sqrt(1 - ct * ct)
        ph = rng.random(n) * 2 * np.pi
        q = np.stack([r * stt * np.cos(ph), r * ct, r * stt * np.sin(ph)], axis=1)
        tw = self.modeB['omega'] * self.simTime
        S, G = field_S_and_grad(q, self.modeB, self.tabB, tw)
        g = np.linalg.norm(G, axis=1)
        return float(np.abs(S).mean()), float(np.abs(S / np.maximum(g, 1e-9)).mean())
