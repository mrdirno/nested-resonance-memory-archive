#!/usr/bin/env python3
"""jeans_sweep.py - self-gravity collapse threshold vs hubble, staged over a
process pool.  Criterion: window-mean radius over simTime in [28,30) (just
before the epoch at t=30) below HALF the selfgrav=0 value of the same job.

  main      H in {0.3,0.6,0.9,1.2,1.8,2.4} x 3 seeds, preset otherwise:
            full selfgrav curve 0..2 step 0.1, then bisection to 0.025
  noepoch   same H, epoch off (bisection only)
  controls  at H=1.2: N=2000/8000/16000, fp32 mesh, hard mode jumps,
            page protocol (startStep 4, 25-27 s window), isotropic
            (aniso=0, helix=0)
"""
import json, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_pm import run_case

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = [round(0.1 * i, 3) for i in range(16)]   # 0..1.5 for the one curve job
RES = 0.025
HS = [0.3, 0.6, 0.9, 1.2, 1.8, 2.4]


def collapsed(r, R0):
    return r['R_win'] < 0.5 * R0


class Job:
    def __init__(self, name, base, mode):
        self.name, self.base, self.mode = name, base, mode
        self.results = {}
        self.done = False
        self.censored = False
        self.lo = self.hi = None

    def cfg(self, sg):
        return dict(self.base, selfgrav=float(sg), job=self.name)

    def feed(self, r):
        self.results[round(r['selfgrav'], 5)] = r

    def pending(self):
        if self.done:
            return []
        if self.mode == 'curve' and not self.results:
            return [self.cfg(s) for s in GRID]
        if self.mode == 'bisect':
            if 0.0 not in self.results:
                return [self.cfg(0.0)]
            if 2.0 not in self.results:
                return [self.cfg(2.0)]
        R0 = self.results[0.0]['R_win']
        sgs = sorted(self.results)
        col = [s for s in sgs if s > 0 and collapsed(self.results[s], R0)]
        if not col:
            self.censored = True
            self.done = True
            self.lo, self.hi = 2.0, None
            return []
        first = col[0]
        self.hi = first
        self.lo = max(s for s in sgs if s < first)
        if self.hi - self.lo <= RES + 1e-9:
            self.done = True
            return []
        return [self.cfg(round(0.5 * (self.lo + self.hi), 5))]

    def summary(self):
        R0 = self.results[0.0]['R_win'] if 0.0 in self.results else None
        curve = {str(s): dict(R=self.results[s]['R_win'], contrast=self.results[s]['contrast'],
                              clamp=self.results[s]['clamp_frac'], Fsg=self.results[s]['Fsg_med'],
                              R_min=self.results[s]['R_min'], finite=self.results[s]['finite'])
                 for s in sorted(self.results)}
        thr = None if (self.censored or self.hi is None) else 0.5 * (self.lo + self.hi)
        err = None if thr is None else 0.5 * (self.hi - self.lo)
        return dict(name=self.name, mode=self.mode, base=self.base, R0=R0,
                    lo=self.lo, hi=self.hi, thr=thr, err=err,
                    censored=self.censored, curve=curve)


def main():
    # LEAN PLAN (the box is shared; ~290 runs): bisection-only jobs, one full
    # response curve at H=1.2, N=4000 unless stated.
    jobs = []
    for H in HS:
        for seed in (12345, 777, 31415):
            jobs.append(Job('main_H%g_s%d' % (H, seed), dict(H=H, seed=seed), 'bisect'))
    jobs.append(Job('curve_H1.2_s12345', dict(H=1.2, seed=12345), 'curve'))
    for H in HS:
        jobs.append(Job('noepoch_H%g' % H, dict(H=H, seed=12345, epoch=False), 'bisect'))
    ex = dict(H=1.2, seed=12345)
    jobs += [Job('N2000', dict(ex, N=2000), 'bisect'),
             Job('N8000', dict(ex, N=8000), 'bisect'),
             Job('fp32mesh', dict(ex, half=False), 'bisect'),
             Job('hardjumps', dict(ex, smooth=False), 'bisect'),
             Job('pageproto_step4_26s', dict(ex, startStep=4, frames=540, t_win=(25.0, 27.0)), 'bisect'),
             Job('isotropic', dict(ex, state=dict(aniso=0.0, helix=0.0)), 'bisect')]
    by = {j.name: j for j in jobs}
    rows = []
    t_all = time.time()
    with Pool(4) as pool:
        stage = 0
        while True:
            batch = []
            for j in jobs:
                batch += [(j.name, c) for c in j.pending()]
            if not batch:
                break
            stage += 1
            t = time.time()
            res = pool.map(run_case, [c for _, c in batch], chunksize=1)
            for (name, c), r in zip(batch, res):
                by[name].feed(r)
                rows.append(r)
            json.dump(rows, open(os.path.join(HERE, 'jeans_rows.json'), 'w'))
            json.dump([j.summary() for j in jobs],
                      open(os.path.join(HERE, 'jeans_thresholds.json'), 'w'), indent=1)
            print('stage %d: %d runs in %.0f s (total %.0f s); open jobs: %s'
                  % (stage, len(batch), time.time() - t, time.time() - t_all,
                     ', '.join('%s[%s,%s]' % (j.name, j.lo, j.hi) for j in jobs if not j.done)),
                  flush=True)
    for j in jobs:
        s = j.summary()
        print('%-28s R0=%6.2f  thr=%s  bracket=[%s, %s]%s' % (
            s['name'], s['R0'] or -1, '%.4f' % s['thr'] if s['thr'] is not None else '  >2 ',
            s['lo'], s['hi'], '  CENSORED' if s['censored'] else ''), flush=True)


if __name__ == '__main__':
    main()
