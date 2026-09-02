#!/usr/bin/env python3
"""disc_boris.py - Spinning Chladni (port2.PRESET, startStep 9028) under the page's
explicit-Euler Lorentz kick (port2.Sim, UNTOUCHED) vs the page's new Boris step.
SimBoris = page ordering: non-Lorentz F clamped at 500, half kick, rotate about +y by
th = mag*30*0.35*dt (vx' = vx cos - vz sin, vz' = vx sin + vz cos), half kick, damping,
then the untouched reflect / rescale / position pass.  Also a force + energy
decomposition: radial/azimuthal/y components of each term and the kinetic energy the
Lorentz term injects per step (zero in exact physics)."""
import sys, os, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import port2
from port2 import EXTENT, RESTITUTION, aniso_vec
B = np.array([0.0, 0.35, 0.0])


class SimBoris(port2.Sim):
    def raw_pass(self):
        st, dt = self.st, self.dt
        F, SB = self.force(self.p, np.zeros_like(self.v))
        self.lastS = SB
        fmag = np.linalg.norm(F, axis=1); over = fmag > 500.0
        self.clamp_frac = float(over.mean())
        if over.any():
            F[over] *= (500.0 / fmag[over])[:, None]
        self.lastF = F
        v = self.v + 0.5 * F * dt
        th = st['mag'] * 30.0 * 0.35 * dt; c, s = math.cos(th), math.sin(th)
        vx = v[:, 0].copy(); vz = v[:, 2].copy()
        v[:, 0] = vx * c - vz * s
        v[:, 2] = vx * s + vz * c
        v = v + 0.5 * F * dt
        self.v = v * math.exp(-st['damping'] * dt)
        if st['boundary'] == 'reflect':
            pn = self.p + self.v * dt
            rn = np.linalg.norm(pn, axis=1); out = rn > EXTENT
            if out.any():
                nrm = pn[out] / rn[out][:, None]
                vr = np.einsum('ij,ij->i', self.v[out], nrm); hit = vr > 0
                if hit.any():
                    idx = np.where(out)[0][hit]
                    self.v[idx] -= (1.0 + RESTITUTION) * vr[hit][:, None] * nrm[hit]
        self.v *= self.rescale
        self.p = self.p + self.v * dt
        rr = np.linalg.norm(self.p, axis=1); out = rr > EXTENT
        if out.any():
            if st['boundary'] == 'reflect':
                self.p[out] *= (EXTENT / rr[out])[:, None]
            else:
                e = np.minimum(rr[out] - EXTENT, EXTENT * 0.5)
                self.p[out] = -self.p[out] * ((EXTENT - e) / rr[out])[:, None]
        self.p *= self.rescale


def decompose(sim, boris):
    """Swarm-mean radial (rho-hat), azimuthal (phi-hat), y components of each force
    term as applied (clamp included), work rates, and the per-step KE change caused by
    the Lorentz term (numerical; exact physics gives 0)."""
    st, dt, p, v = sim.st, sim.dt, sim.p, sim.v
    F0, _ = sim.force(p, np.zeros_like(v))
    hub = st['hubble'] * p * aniso_vec(st['aniso'])[None, :]
    hel = np.zeros_like(p); hel[:, 0] = st['helix'] * 6.0 * (-p[:, 2]); hel[:, 2] = st['helix'] * 6.0 * p[:, 0]
    fld = F0 - hub - hel
    FL = st['mag'] * 30.0 * np.cross(v, B)
    if boris:
        s = np.minimum(1.0, 500.0 / np.maximum(np.linalg.norm(F0, axis=1), 1e-9))
    else:
        s = np.minimum(1.0, 500.0 / np.maximum(np.linalg.norm(F0 + FL, axis=1), 1e-9))
    rho = np.hypot(p[:, 0], p[:, 2]); ok = rho > 0.5
    rh = np.zeros_like(p); rh[:, 0] = p[:, 0] / np.maximum(rho, 1e-9); rh[:, 2] = p[:, 2] / np.maximum(rho, 1e-9)
    ph = np.zeros_like(p); ph[:, 0] = -rh[:, 2]; ph[:, 2] = rh[:, 0]
    out = {}
    for name, F in (('field', fld * s[:, None]), ('hubble', hub * s[:, None]), ('helix', hel * s[:, None]),
                    ('lorentz', FL * (s[:, None] if not boris else 1.0)), ('damping', -st['damping'] * v)):
        out[name] = dict(r=float(np.einsum('ij,ij->i', F, rh)[ok].mean()),
                         phi=float(np.einsum('ij,ij->i', F, ph)[ok].mean()),
                         y=float(F[ok, 1].mean()),
                         work=float(np.einsum('ij,ij->i', F, v).mean()))
    dmp = math.exp(-2.0 * st['damping'] * dt)
    if boris:
        Fc = F0 * s[:, None]
        vh = v + 0.5 * Fc * dt
        th = st['mag'] * 30.0 * 0.35 * dt; c, sn = math.cos(th), math.sin(th)
        vr = vh.copy(); vr[:, 0] = vh[:, 0] * c - vh[:, 2] * sn; vr[:, 2] = vh[:, 0] * sn + vh[:, 2] * c
        ke_with = 0.5 * ((vr + 0.5 * Fc * dt) ** 2).sum(1); ke_without = 0.5 * ((v + Fc * dt) ** 2).sum(1)
    else:
        ke_with = 0.5 * ((v + (F0 + FL) * s[:, None] * dt) ** 2).sum(1)
        ke_without = 0.5 * ((v + F0 * s[:, None] * dt) ** 2).sum(1)
    out['lorentz_KE_inject_per_s'] = float(((ke_with - ke_without) * dmp).mean() / dt)
    out['KE'] = float(0.5 * (v * v).sum(1).mean())
    om = (np.einsum('ij,ij->i', v, ph) / np.maximum(rho, 1e-9))[ok]
    out['omega_rot_mean'] = float(om.mean()); out['omega_rot_median'] = float(np.median(om))
    out['frac_stream_3to7'] = float(((om > 3) & (om < 7)).mean())
    out['clamp_frac'] = float((s < 1).mean())
    return out


def stats(sim):
    p, v = sim.p, sim.v
    r = np.linalg.norm(p, axis=1); sp = np.linalg.norm(v, axis=1)
    return dict(mean_abs_y=float(np.abs(p[:, 1]).mean()), r=float(r.mean()), rho=float(np.hypot(p[:, 0], p[:, 2]).mean()),
                speed=float(sp.mean()), wall=float((r > 14.5).mean()), clamp=float(sim.clamp_frac),
                absS=float(np.abs(sim.lastS).mean()) if sim.lastS is not None else float('nan'))


def run(boris, mag, dt=1 / 20, T=30.0, seed=1, particles=4000, snaps=(10, 20, 30), series_every=2.0, **kw):
    st = dict(particles=particles, seed=seed, mag=mag, dt=dt); st.update(kw)
    sim = (SimBoris if boris else port2.Sim)(st)
    n = int(round(T / dt)); series = []; dec = {}
    for fi in range(n):
        t = (fi + 1) * dt
        if any(abs(t - s_) < 0.5 * dt for s_ in snaps):
            dec[str(int(round(t)))] = decompose(sim, boris)   # state entering this frame
        sim.frame(fi)
        if abs(t / series_every - round(t / series_every)) < 0.5 * dt / series_every:
            series.append((round(t, 2), stats(sim)))
    return dict(boris=boris, mag=mag, dt=dt, seed=seed, final=stats(sim), series=series, decomp=dec,
                epochs=len(sim.epoch_frames))


def show(r, label):
    f = r['final']
    print(f"{label:<34s} mean|y| {f['mean_abs_y']:6.2f}  r {f['r']:5.2f}  rho {f['rho']:5.2f}  speed {f['speed']:5.1f}  "
          f"wall {f['wall']:.2f}  clamp {f['clamp']:.3f}  |S| {f['absS']:.3f}  epochs {r['epochs']}")


if __name__ == '__main__':
    out = {}
    print("=== (1) Spinning Chladni preset, 30 s, dt 1/20, 4000 particles ===")
    E = run(False, 0.4); Bz = run(True, 0.4)
    E2 = run(False, 0.4, seed=2); B2 = run(True, 0.4, seed=2)
    show(E, 'Euler   mag 0.4 seed 1'); show(E2, 'Euler   mag 0.4 seed 2')
    show(Bz, 'Boris   mag 0.4 seed 1'); show(B2, 'Boris   mag 0.4 seed 2')
    out['euler'] = E; out['boris'] = Bz; out['euler2'] = E2; out['boris2'] = B2
    print("\n--- time series (t: mean|y| / r / speed / clamp) ---")
    for (tE, sE), (tB, sB) in zip(E['series'], Bz['series']):
        print(f"t {tE:5.1f}  Euler |y| {sE['mean_abs_y']:6.2f} r {sE['r']:5.2f} v {sE['speed']:5.1f} clamp {sE['clamp']:.3f} wall {sE['wall']:.2f}"
              f"   | Boris |y| {sB['mean_abs_y']:6.2f} r {sB['r']:5.2f} v {sB['speed']:5.1f} clamp {sB['clamp']:.3f} wall {sB['wall']:.2f}")
    print("\n--- force decomposition (swarm means, particles with rho>0.5; components: radial, azimuthal, y; work = F.v) ---")
    for label, R in (('Euler', E), ('Boris', Bz)):
        for t, d in R['decomp'].items():
            print(f"{label} t={t}s  KE {d['KE']:8.1f}  omega_rot mean/median {d['omega_rot_mean']:+.2f}/{d['omega_rot_median']:+.2f} rad/s  "
                  f"frac 3<omega<7 {d['frac_stream_3to7']:.2f}  clamp {d['clamp_frac']:.3f}  Lorentz-KE-inject {d['lorentz_KE_inject_per_s']:+9.1f} /s")
            for k in ('field', 'hubble', 'helix', 'lorentz', 'damping'):
                c = d[k]
                print(f"      {k:<8s} r {c['r']:+8.2f}  phi {c['phi']:+8.2f}  y {c['y']:+8.2f}   work {c['work']:+9.1f}")
    print("\n=== Euler at smaller dt (does the figure survive substeps?) ===")
    for di in (40, 80, 160):
        R = run(False, 0.4, dt=1.0 / di); out[f'euler_dt{di}'] = R
        show(R, f'Euler   mag 0.4 dt 1/{di}')
    R = run(True, 0.4, dt=1.0 / 80); out['boris_dt80'] = R; show(R, 'Boris   mag 0.4 dt 1/80')
    print("\n=== (3) mag 0.05: Euler vs Boris must agree (pumping 0.007/s) ===")
    for lab, b, sd in (('Euler mag 0.05 seed 1', False, 1), ('Euler mag 0.05 seed 2', False, 2),
                       ('Boris mag 0.05 seed 1', True, 1), ('Boris mag 0.05 seed 2', True, 2)):
        R = run(b, 0.05, seed=sd); out[lab] = R; show(R, lab)
    d = out['Euler mag 0.05 seed 1']['decomp']['30']; d2 = out['Boris mag 0.05 seed 1']['decomp']['30']
    print(f"   Lorentz-KE-inject at 30 s: Euler {d['lorentz_KE_inject_per_s']:+.2f}/s  Boris {d2['lorentz_KE_inject_per_s']:+.2f}/s ; KE {d['KE']:.1f} vs {d2['KE']:.1f}")
    print("\n=== mag 0 reference (both integrators identical by construction) ===")
    show(run(False, 0.0), 'Euler   mag 0'); show(run(True, 0.0), 'Boris   mag 0')
    json.dump(out, open('disc_boris.json', 'w'))
