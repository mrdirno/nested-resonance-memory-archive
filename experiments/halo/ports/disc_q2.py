#!/usr/bin/env python3
"""disc_q2.py - Benettin twin-method Lyapunov exponent on the validated port
(port2.Sim, untouched).  Question 2.

Method (as specified): N originals settle for `settle` s; then each gets a twin
at phase-space distance d0 (position offset along a random direction, same
velocity).  All 2N particles run the FULL dynamics in one Sim (particles are
independent; the digit sequence, twist phase and epoch clock are global).
Every tau s: d = |(dp, dv)| (norm='6d', default) or |dp| (norm='pos');
log(d/d0) is accumulated per pair, then the twin is renormalised to d0 along
the current separation with position and velocity separation scaled by the
same factor.  Intervals in which d > 3 (wall event / wrap teleport) or in
which an epoch rescale fired are excluded for that pair (all pairs, for an
epoch) and the pair is re-paired (fresh random offset at d0, same velocity).
lambda_i = sum log(d/d0) / (n_included_i * tau); lambda = mean_i, SE = std_i/sqrt(n).
"""
import sys, os, json, math, time, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import port2


def base_default():
    return dict(fieldForm='chladni', fieldExp=0.0, damping=2.5, stepsPerSec=2.0,
                smooth=True, base=10, constants={'a': 'phi', 'b': 'phi', 'c': 'pi'},
                strideIndex=51, boundary='reflect', hubble=0.3, epoch=False,
                epochLen=10.0, mag=0.6, twist=True, aniso=0.0, helix=0.0,
                cascade='out', startStep=0, dt=1.0 / 20.0)


DISC = dict(fieldForm='chladni', fieldExp=0.0, damping=0.8, stepsPerSec=2.0,
            smooth=True, base=10, constants={'a': 'phi', 'b': 'phi', 'c': 'pi'},
            strideIndex=51, boundary='wrap', hubble=3.0, epoch=False, epochLen=10.0,
            mag=3.0, twist=False, aniso=0.0, helix=0.0, cascade='out', startStep=0,
            dt=1.0 / 20.0)

SPIN = dict(fieldForm='chladni', fieldExp=2.0, damping=1.0, stepsPerSec=0.5,
            smooth=True, base=10, constants={'a': 'phi', 'b': 'phi', 'c': 'phi'},
            strideIndex=0, boundary='reflect', hubble=1.2, epoch=True, epochLen=10.0,
            mag=0.4, twist=True, aniso=0.55, helix=0.8, cascade='out', startStep=0,
            dt=1.0 / 20.0)


def regimes():
    a = base_default()
    return {
        'a_default': dict(a),
        'b_frozen': {**a, 'stepsPerSec': 0.02},
        'c_disc_dt20': {**DISC, 'dt': 1.0 / 20.0},
        'c_disc_dt80': {**DISC, 'dt': 1.0 / 80.0},
        'd_spin': dict(SPIN),
        'e_free': {**a, 'damping': 0.3, 'hubble': 0.0, 'mag': 0.0},
    }


def benettin(state, npairs=500, d0=1e-3, tau=0.5, settle=10.0, T=40.0, seed=1, norm='6d',
             wall_r=14.5, overrides=None):
    st = dict(state); st['particles'] = npairs; st['seed'] = seed
    if overrides:
        st.update(overrides)
    sim = port2.Sim(st)
    dt = sim.dt
    fi = 0
    for _ in range(int(round(settle / dt))):
        sim.frame(fi); fi += 1
    settle_info = dict(speed_mean=float(np.linalg.norm(sim.v, axis=1).mean()),
                       absS_mean=float(np.abs(sim.lastS).mean()),
                       r_mean=float(np.linalg.norm(sim.p, axis=1).mean()),
                       mode={k: sim.modeB[k] for k in ('n', 'l', 'm', 'm2')},
                       clamp_frac=float(sim.clamp_frac))
    rng = np.random.default_rng(seed + 977)

    def dirs(n):
        g = rng.normal(size=(n, 3))
        return g / np.linalg.norm(g, axis=1)[:, None]

    P, V = sim.p.copy(), sim.v.copy()
    sim.p = np.concatenate([P, P + d0 * dirs(npairs)])
    sim.v = np.concatenate([V, V.copy()])
    fpi = int(round(tau / dt))
    assert abs(fpi * dt - tau) < 1e-9, (tau, dt)
    nint = int(round(T / tau))
    logsum = np.zeros(npairs); cnt = np.zeros(npairs, int)
    logsum_free = np.zeros(npairs); cnt_free = np.zeros(npairs, int)
    logsum_wall = np.zeros(npairs); cnt_wall = np.zeros(npairs, int)
    n_touch = 0
    n_excl_big = 0; n_excl_epoch = 0; n_int_pairs = 0
    series = []            # per-interval mean of log(d/d0)/tau over included pairs
    dpos_frac = []         # share of the 6d separation carried by position
    t0 = time.time()
    for k in range(nint):
        ep0 = sim.epochN
        rmax = np.zeros(2 * npairs)
        for _ in range(fpi):
            sim.frame(fi); fi += 1
            rmax = np.maximum(rmax, np.linalg.norm(sim.p, axis=1))
        touched = (rmax[:npairs] > wall_r) | (rmax[npairs:] > wall_r)
        dp = sim.p[npairs:] - sim.p[:npairs]
        dv = sim.v[npairs:] - sim.v[:npairs]
        dp2 = (dp * dp).sum(1); dv2 = (dv * dv).sum(1)
        d = np.sqrt(dp2 + (dv2 if norm == '6d' else 0.0))
        bad = ~np.isfinite(d) | (d > 3.0) | (d <= 0.0)
        n_excl_big += int(bad.sum())
        if sim.epochN != ep0:
            bad[:] = True; n_excl_epoch += 1
        good = ~bad
        n_int_pairs += npairs
        if good.any():
            lg = np.log(d[good] / d0)
            logsum[good] += lg; cnt[good] += 1
            gf = good & ~touched; gw = good & touched
            logsum_free[gf] += np.log(d[gf] / d0); cnt_free[gf] += 1
            logsum_wall[gw] += np.log(d[gw] / d0); cnt_wall[gw] += 1
            n_touch += int(touched.sum())
            series.append(float(lg.mean() / tau))
            dpos_frac.append(float(np.sqrt(dp2[good]).mean() / max(d[good].mean(), 1e-300)))
        else:
            series.append(float('nan'))
        f = d0 / np.maximum(d, 1e-300)
        twp = sim.p[npairs:]; twv = sim.v[npairs:]
        twp[good] = sim.p[:npairs][good] + dp[good] * f[good, None]
        twv[good] = sim.v[:npairs][good] + dv[good] * f[good, None]
        nb = int(bad.sum())
        if nb:
            twp[bad] = sim.p[:npairs][bad] + d0 * dirs(nb)
            twv[bad] = sim.v[:npairs][bad]
    ok = cnt > 0
    lam = logsum[ok] / (cnt[ok] * tau)
    okf = cnt_free > 0; okw = cnt_wall > 0
    lam_free = logsum_free[okf] / (cnt_free[okf] * tau)
    lam_wall = logsum_wall[okw] / (cnt_wall[okw] * tau)
    r_end = np.linalg.norm(sim.p[:npairs], axis=1)
    res = dict(lambda_mean=float(lam.mean()),
               se=float(lam.std(ddof=1) / math.sqrt(len(lam))) if len(lam) > 1 else float('nan'),
               n_pairs_used=int(ok.sum()), n_pairs=npairs,
               frac_pairs_positive=float((lam > 0).mean()),
               lam_p10=float(np.percentile(lam, 10)), lam_p50=float(np.percentile(lam, 50)),
               lam_p90=float(np.percentile(lam, 90)),
               excl_frac_big=n_excl_big / n_int_pairs, n_excl_epoch=n_excl_epoch,
               n_intervals=nint, tau=tau, dt=dt, d0=d0, norm=norm, seed=seed,
               settle=settle_info,
               lam_free=float(lam_free.mean()) if len(lam_free) else float('nan'),
               se_free=float(lam_free.std(ddof=1) / math.sqrt(len(lam_free))) if len(lam_free) > 1 else float('nan'),
               n_free=int(len(lam_free)),
               lam_wall=float(lam_wall.mean()) if len(lam_wall) else float('nan'),
               n_wall=int(len(lam_wall)),
               touch_frac=n_touch / n_int_pairs,
               end_wall_frac=float((r_end > wall_r).mean()),
               end_r_mean=float(r_end.mean()),
               overrides=overrides or {},
               series_first_last=[series[:4], series[-4:]],
               series_mean_first_half=float(np.nanmean(series[:nint // 2])),
               series_mean_second_half=float(np.nanmean(series[nint // 2:])),
               dpos_frac_mean=float(np.mean(dpos_frac)) if dpos_frac else float('nan'),
               end_speed_mean=float(np.linalg.norm(sim.v[:npairs], axis=1).mean()),
               elapsed_s=time.time() - t0)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--regimes', default='a_default,b_frozen,c_disc_dt20,c_disc_dt80,d_spin,e_free')
    ap.add_argument('--npairs', type=int, default=500)
    ap.add_argument('--T', type=float, default=40.0)
    ap.add_argument('--settle', type=float, default=10.0)
    ap.add_argument('--taus', default='0.5')
    ap.add_argument('--norms', default='6d,pos')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', default='disc_q2.json')
    ap.add_argument('--d0s', default='1e-3')
    ap.add_argument('--set', action='append', default=[], help='override key=value (json)')
    a = ap.parse_args()
    overrides = {}
    for kv in a.set:
        k, v = kv.split('=', 1)
        try:
            overrides[k] = json.loads(v)
        except Exception:
            overrides[k] = v
    R = regimes()
    rows = []
    for name in a.regimes.split(','):
        for norm in a.norms.split(','):
            for tau in [float(x) for x in a.taus.split(',')]:
              for d0 in [float(x) for x in a.d0s.split(',')]:
                r = benettin(R[name], npairs=a.npairs, d0=d0, tau=tau, settle=a.settle, T=a.T,
                             seed=a.seed, norm=norm, overrides=overrides)
                r['regime'] = name
                rows.append(r)
                print(f"{name:<13s} {str(overrides) if overrides else ''} norm {norm:<3s} tau {tau:<5g} d0 {d0:g} lambda {r['lambda_mean']:+.4f} "
                      f"+/- {r['se']:.4f}  pairs {r['n_pairs_used']}  frac>0 {r['frac_pairs_positive']:.2f} "
                      f"| wall-free {r['lam_free']:+.4f}+/-{r['se_free']:.4f} (n={r['n_free']}) wall {r['lam_wall']:+.4f} (n={r['n_wall']}) touch {r['touch_frac']:.2f} end_wall {r['end_wall_frac']:.2f} r_end {r['end_r_mean']:.1f} "
                      f"p10/50/90 {r['lam_p10']:+.3f}/{r['lam_p50']:+.3f}/{r['lam_p90']:+.3f}  "
                      f"excl_big {r['excl_frac_big']:.3f} excl_epoch {r['n_excl_epoch']}  "
                      f"1st/2nd half {r['series_mean_first_half']:+.3f}/{r['series_mean_second_half']:+.3f}  "
                      f"settle: speed {r['settle']['speed_mean']:.2f} |S| {r['settle']['absS_mean']:.4f} "
                      f"mode {r['settle']['mode']}  [{r['elapsed_s']:.0f}s]", flush=True)
                json.dump(rows, open(a.out, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
