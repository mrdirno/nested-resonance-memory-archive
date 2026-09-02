#!/usr/bin/env python3
"""disc_q1.py - Razor Disc vs integrator step (Question 1).

Runs the shipped 'Razor Disc' preset on the validated numpy port (port2.Sim,
UNTOUCHED) over a dt ladder and reports disc metrics at each dt.  In the port
damping is a rate (v *= exp(-damping*dt)) so it is dt-consistent by
construction; the digit sequencer advances on sim time, so the mode order is
identical at every dt.  Fresh seed per run, 30 s of sim time, 3000 particles.

Metrics (page conventions, see disc_mech.js):
  mean|y|, p90|y|            y = coordinate along B (disc normal)
  coh                        majority fraction of sign(z*vx - x*vz)  (L_y sign)
  dense_annulus_r            peak of cylindrical-radius density per unit area
  wrap diagnostics           reconstructed from the position pass over the last
                             2 s: wrap rate, mean overshoot e, fraction capped
                             at the shader's e <= EXTENT/2 (re-entry at r=7.5)

--variant additionally runs an ATTRIBUTION variant (SimExactB): identical to
the port except the Lorentz kick uses the exact rotation of v about B over dt
instead of the explicit v_old x B force.  Not the page; used only to say which
integrator feature the disc rides on.
"""
import sys, os, json, math, time, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import port2
EXTENT = port2.EXTENT
RESTITUTION = port2.RESTITUTION


def disc_state(mag, dt, seed, particles=3000):
    return dict(particles=particles, dt=dt, seed=seed,
                fieldForm='chladni', fieldExp=0.0, damping=0.8, stepsPerSec=2.0,
                smooth=True, base=10, constants={'a': 'phi', 'b': 'phi', 'c': 'pi'},
                strideIndex=51, boundary='wrap', hubble=3.0, epoch=False, mag=mag,
                twist=False, aniso=0.0, helix=0.0, cascade='out', startStep=0)


class SimExactB(port2.Sim):
    """ATTRIBUTION VARIANT ONLY.  Same pass ordering as port2.Sim.raw_pass, but the
    Lorentz term is the exact rotation of v about yhat by Omega*dt,
    Omega = mag*30*|B|, |B| = 0.35, instead of the explicit v_old x B kick."""
    def raw_pass(self):
        st, dt = self.st, self.dt
        F, SB = self.force(self.p, np.zeros_like(self.v))   # Lorentz term is 0 at v=0
        self.lastS = SB
        fmag = np.linalg.norm(F, axis=1)
        over = fmag > 500.0
        self.clamp_frac = float(over.mean())
        if over.any():
            F[over] *= (500.0 / fmag[over])[:, None]
        v = self.v + F * dt
        th = st['mag'] * 30.0 * 0.35 * dt
        c, s = math.cos(th), math.sin(th)
        vx = v[:, 0].copy(); vz = v[:, 2].copy()
        v[:, 0] = c * vx - s * vz      # dv/dt = Omega (v x yhat), (vx,0,vz) x yhat = (-vz,0,vx)
        v[:, 2] = c * vz + s * vx
        self.v = v * math.exp(-st['damping'] * dt)
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


def metrics(sim):
    p, v = sim.p, sim.v
    y = np.abs(p[:, 1])
    Ly = p[:, 2] * v[:, 0] - p[:, 0] * v[:, 2]
    pos = float((Ly > 0).mean())
    rho = np.hypot(p[:, 0], p[:, 2])
    edges = np.arange(0.0, EXTENT + 0.25, 0.25)
    cnt, _ = np.histogram(rho, bins=edges)
    mid = 0.5 * (edges[1:] + edges[:-1])
    area = np.pi * (edges[1:] ** 2 - edges[:-1] ** 2)
    dens = cnt / area
    k = int(np.argmax(dens))
    peaks = [i for i in range(1, len(dens) - 1)
             if dens[i] > dens[i - 1] and dens[i] >= dens[i + 1] and cnt[i] >= 30]
    peaks = sorted(peaks, key=lambda i: -dens[i])[:4]
    speed = np.linalg.norm(v, axis=1)
    return dict(mean_abs_y=float(y.mean()), p90_abs_y=float(np.percentile(y, 90)),
                median_abs_y=float(np.median(y)), frac_y_lt_0p01=float((y < 0.01).mean()),
                coh=max(pos, 1 - pos),
                dense_annulus_r=float(mid[k]),
                dense_annulus_contrast=float(dens[k] / max(dens.mean(), 1e-12)),
                ring_peaks_r=[float(mid[i]) for i in peaks],
                speed_mean=float(speed.mean()), speed_median=float(np.median(speed)),
                vy_rms=float(np.sqrt((v[:, 1] ** 2).mean())),
                r_mean=float(np.linalg.norm(p, axis=1).mean()),
                rho_mean=float(rho.mean()),
                clamp_frac=float(sim.clamp_frac))


def run(mag, dt, seed, T=30.0, particles=3000, variant=False, checkpoints=(5, 10, 20, 30)):
    st = disc_state(mag, dt, seed, particles)
    sim = (SimExactB if variant else port2.Sim)(st)
    nfr = int(round(T / dt))
    cp_frames = {int(round(c / dt)): c for c in checkpoints if c <= T + 1e-9}
    out = dict(mag=mag, dt_inv=int(round(1 / dt)), dt=dt, seed=seed,
               variant='exactB' if variant else 'port', T=T, particles=particles,
               checkpoints={})
    wa = dict(n=0, wrapped=0, e_sum=0.0, capped=0)
    t0 = time.time()
    for fi in range(nfr):
        p_prev = sim.p.copy()
        sim.frame(fi)
        t = (fi + 1) * dt
        if t > T - 2.0:
            p_pre = p_prev + sim.v * dt          # position pass before the wrap (rescale=1)
            r_pre = np.linalg.norm(p_pre, axis=1)
            w = r_pre > EXTENT
            wa['n'] += len(w); wa['wrapped'] += int(w.sum())
            if w.any():
                e = r_pre[w] - EXTENT
                wa['e_sum'] += float(np.minimum(e, EXTENT * 0.5).sum())
                wa['capped'] += int((e >= EXTENT * 0.5).sum())
        if (fi + 1) in cp_frames:
            out['checkpoints'][str(cp_frames[fi + 1])] = metrics(sim)
    out['final'] = metrics(sim)
    out['wrap'] = dict(frac_per_frame=wa['wrapped'] / max(1, wa['n']),
                       rate_per_sec=wa['wrapped'] / max(1, wa['n']) / dt,
                       e_mean=wa['e_sum'] / max(1, wa['wrapped']),
                       capped_frac=wa['capped'] / max(1, wa['wrapped']))
    out['elapsed_s'] = time.time() - t0
    out['frames'] = nfr
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mag', type=float, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--dts', default='20,40,80,160,320,640,1280')
    ap.add_argument('--reps', type=int, default=2, help='seeds per rung for dt_inv<=320')
    ap.add_argument('--T', type=float, default=30.0)
    ap.add_argument('--particles', type=int, default=3000)
    ap.add_argument('--variant', action='store_true')
    ap.add_argument('--checkpoints', default='5,10,20,30')
    ap.add_argument('--seedbase', type=int, default=0)
    a = ap.parse_args()
    cps = tuple(int(x) for x in a.checkpoints.split(','))
    rows = []
    dts = [int(x) for x in a.dts.split(',')]
    for i, di in enumerate(dts):
        reps = a.reps if di <= 320 else 1
        for rep in range(reps):
            seed = 1000 * (i + 1) + 10 * rep + int(round(a.mag * 10)) + 3 + a.seedbase
            r = run(a.mag, 1.0 / di, seed, T=a.T, particles=a.particles, checkpoints=cps)
            rows.append(r)
            f = r['final']
            print(f"mag {a.mag} dt 1/{di:<5d} seed {seed:<6d} mean|y| {f['mean_abs_y']:.5f} "
                  f"p90|y| {f['p90_abs_y']:.5f} coh {f['coh']:.3f} annulus_r {f['dense_annulus_r']:.2f} "
                  f"(x{f['dense_annulus_contrast']:.1f}) speed {f['speed_mean']:.1f} clamp {f['clamp_frac']:.2f} "
                  f"wrap/s {r['wrap']['rate_per_sec']:.3f} e {r['wrap']['e_mean']:.2f} "
                  f"capped {r['wrap']['capped_frac']:.2f}  [{r['elapsed_s']:.0f}s]", flush=True)
            json.dump(rows, open(a.out, 'w'), indent=1)
    if a.variant:
        for di in (20, 80, 320):
            seed = 77 + di
            r = run(a.mag, 1.0 / di, seed, T=a.T, particles=a.particles, variant=True, checkpoints=cps)
            rows.append(r)
            f = r['final']
            print(f"VARIANT exactB mag {a.mag} dt 1/{di:<5d} mean|y| {f['mean_abs_y']:.5f} "
                  f"p90|y| {f['p90_abs_y']:.5f} coh {f['coh']:.3f} annulus_r {f['dense_annulus_r']:.2f} "
                  f"speed {f['speed_mean']:.1f} clamp {f['clamp_frac']:.2f} "
                  f"wrap/s {r['wrap']['rate_per_sec']:.3f} e {r['wrap']['e_mean']:.2f} "
                  f"capped {r['wrap']['capped_frac']:.2f}  [{r['elapsed_s']:.0f}s]", flush=True)
            json.dump(rows, open(a.out, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
