#!/usr/bin/env python3
"""jeans_floor.py - the helix=0 floor: does it track the eigenmode field?
helix 0, fieldExp in {0,1,2,3} (amp = 10^fieldExp), H=1.2, preset otherwise,
3 seeds, bisection with a RELATIVE stopping rule (width <= max(0.004, 6% of hi)).
Controls: helix 0, fieldExp 2, mag 0 ; helix 0, fieldExp 2, mag 0, aniso 0.
(Results: jeans_floor.json / jeans_floor.log.)"""
import json, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_sweep import Job
from jeans_pm import run_case
HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = (12345, 777, 31415)


class RJob(Job):
    """Job with a relative stopping rule for small thresholds."""
    def pending(self):
        if self.done:
            return []
        out = super().pending()
        if self.done and not self.censored and self.hi is not None and (self.hi - self.lo) > max(0.004, 0.06 * self.hi):
            self.done = False
            return [self.cfg(round(0.5 * (self.lo + self.hi), 6))]
        return out


def run_jobs(jobs, out_name):
    by = {j.name: j for j in jobs}
    rows = []
    t0 = time.time()
    with Pool(4) as pool:
        while True:
            batch = [(j.name, c) for j in jobs for c in j.pending()]
            if not batch:
                break
            for (name, c), r in zip(batch, pool.map(run_case, [c for _, c in batch], chunksize=1)):
                by[name].feed(r); rows.append(r)
            print('stage done: %d runs, %.0f s, open %d' % (len(batch), time.time() - t0, sum(not j.done for j in jobs)), flush=True)
    json.dump(dict(jobs=[j.summary() for j in jobs], rows=rows), open(os.path.join(HERE, out_name), 'w'), indent=1)
    for j in jobs:
        s = j.summary()
        print('%-28s R0=%6.2f  thr=%s  [%s, %s]%s' % (s['name'], s['R0'], ('%.4f' % s['thr']) if s['thr'] is not None else '>2',
                                                     s['lo'], s['hi'], '  CENSORED' if s['censored'] else ''), flush=True)


def main():
    jobs = []
    for fe in (0.0, 1.0, 2.0, 3.0):
        for s in SEEDS:
            jobs.append(RJob('fe%g_s%d' % (fe, s), dict(H=1.2, seed=s, state=dict(helix=0.0, fieldExp=fe)), 'bisect'))
    for s in SEEDS:
        jobs.append(RJob('fe2_mag0_s%d' % s, dict(H=1.2, seed=s, state=dict(helix=0.0, fieldExp=2.0, mag=0.0)), 'bisect'))
        jobs.append(RJob('fe2_mag0_aniso0_s%d' % s, dict(H=1.2, seed=s, state=dict(helix=0.0, fieldExp=2.0, mag=0.0, aniso=0.0)), 'bisect'))
    run_jobs(jobs, 'jeans_floor.json')


if __name__ == '__main__':
    main()
