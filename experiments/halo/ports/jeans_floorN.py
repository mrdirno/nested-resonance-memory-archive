#!/usr/bin/env python3
"""jeans_floorN.py - N-dependence of the helix=0 floor (fieldExp 2, mag 0,
aniso 0, H=1.2): shot-noise / mesh-scale fragmentation would move with N."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jeans_floor import RJob, run_jobs

if __name__ == '__main__':
    st = dict(helix=0.0, fieldExp=2.0, mag=0.0, aniso=0.0)
    jobs = [RJob('N2000_s12345', dict(H=1.2, seed=12345, N=2000, state=st), 'bisect'),
            RJob('N2000_s777', dict(H=1.2, seed=777, N=2000, state=st), 'bisect'),
            RJob('N8000_s12345', dict(H=1.2, seed=12345, N=8000, state=st), 'bisect'),
            RJob('N8000_s777', dict(H=1.2, seed=777, N=8000, state=st), 'bisect'),
            RJob('N16000_s12345', dict(H=1.2, seed=12345, N=16000, state=st), 'bisect')]
    run_jobs(jobs, 'jeans_floorN.json')
