#!/usr/bin/env python3
"""jeans_lag.py - is the helix=0 floor the warm-start Jacobi lag after the
epoch halving?  Same jobs as two floor cases but 60 sweeps/frame (page: 6)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_floor import RJob, run_jobs, SEEDS

if __name__ == '__main__':
    jobs = []
    for s in SEEDS:
        jobs.append(RJob('lag60_fe2_mag0_aniso0_s%d' % s, dict(H=1.2, seed=s, state=dict(helix=0.0, fieldExp=2.0, mag=0.0, aniso=0.0, pm_iters=60)), 'bisect'))
        jobs.append(RJob('lag60_fe2_s%d' % s, dict(H=1.2, seed=s, state=dict(helix=0.0, fieldExp=2.0, pm_iters=60)), 'bisect'))
    run_jobs(jobs, 'jeans_lag.json')
