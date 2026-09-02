#!/usr/bin/env python3
"""memory_run45.py - the page's TRUE default (epochLen 45 s) as the control,
sg 0 vs 0.4, 2 seeds, 9 epochs (8 relic epochs). Same code paths as
memory_run.py / memory_analyze.py, separate output directory."""
import os, sys, time, json
import numpy as np
from multiprocessing import Pool
import memory_run as MR
import memory_analyze as MA

OUT45 = os.path.join(MR.HERE, 'memory_out45'); os.makedirs(OUT45, exist_ok=True)
MR.OUT = OUT45; MA.OUT = OUT45
MR.N_EPOCHS = 9
MR.SEEDS = [12345, 777]; MA.SEEDS = MR.SEEDS
MR.CFGS['default'] = dict(MR.DEFAULT, epochLen=45.0)
JOBS = [('default', sg, s) for sg in (0.0, 0.4) for s in MR.SEEDS]

if __name__ == '__main__':
    t0 = time.time()
    with Pool(4) as pool:
        for tag, msg in pool.imap_unordered(MR.run_one, JOBS):
            print(tag, msg, '(%.0fs)' % (time.time() - t0), flush=True)
    rows = []
    with Pool(4) as pool:
        for rr in pool.imap_unordered(MA.analyze_run, JOBS):
            rows.extend(rr)
    rows.sort(key=lambda r: (r['sg'], MR.SEEDS.index(r['seed']), r['epoch']))
    curves, diag = {}, {}
    for name, sg, seed in JOBS:
        S, C, dg, meta = MA.load(name, sg, seed)
        key = '%s_sg%.2f' % (name, sg)
        for t in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 9.9, 20.0, 30.0, 40.0, 44.9):
            sel = np.abs(C[:, 1] - t) <= 0.051
            if sel.any():
                curves.setdefault(key, {}).setdefault('%.2f' % t, []).extend(C[sel, 2].tolist())
                curves.setdefault(key, {}).setdefault('frac%.2f' % t, []).extend(C[sel, 3].tolist())
        diag.setdefault(key, []).append({'clamp': float(dg[:, 1].mean()), 'sgF_med': float(dg[:, 2].mean()),
                                         'speed_med': float(dg[:, 3].mean()), 'r_med': float(dg[:, 4].mean()),
                                         'Fchl_med': float(dg[:, 5].mean()), 'Fflow_med': float(dg[:, 6].mean()),
                                         'pm_resid': float(dg[:, 7].mean()), 'wall_s': meta['wall_s'],
                                         'frames': meta['nframes'], 'switches': meta['switches']})
    json.dump({'rows': rows, 'curves': curves, 'diag': diag}, open(os.path.join(OUT45, 'memory_results45.json'), 'w'))
    MA.report(rows, curves, diag)
    for key, c in curves.items():
        print('%s M(t) at t=20/30/40/44.9 s: %s' % (key, ' '.join('%.3f' % np.mean(c[t]) if t in c else 'nan' for t in ('20.00', '30.00', '40.00', '44.90'))),
              '| inner frac: %s' % ' '.join('%.2f' % np.mean(c['frac' + t]) if 'frac' + t in c else 'nan' for t in ('20.00', '30.00', '40.00', '44.90')))
    print('DONE45 %.0fs' % (time.time() - t0))
