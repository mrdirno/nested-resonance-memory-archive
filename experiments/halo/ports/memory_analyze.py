#!/usr/bin/env python3
"""memory_analyze.py - post-processing of memory_run.py snapshots (parallel).

Per run, per epoch k >= 1 (rho_k = NGP counts of the end-of-epoch-k positions
on the chamber's 32^3 mesh; S[j] = positions at the end of epoch j):

  PRESCRIBED  M_raw   Pearson over inner 16^3 cells of rho_k vs counts(S[k-1]/2)
              M_max   same, maximised over rigid rotation of S[k-1] about y
              M_single relic read from the single old cell c_old = 2c - N/2
  NULLS       sh_*    spatially shuffled relic (mean, sd over 200; max-of-72)
              M2_*    relic from S[k-2] with the same x0.5 map;  M4_* with x0.25
              X_*     relic from an independent seed's S[k-1] (same digit script)
              A_raw   relic with the azimuth (about y) of every particle
                      randomised: keeps the axisymmetric envelope only
  SMOOTHED    Ms_*, Ms2_*, Xs_*, shs_mean : 3^3 boxcar on both fields
  SCALE SCAN  Mf[f], M2f[f], Xf[f]  (f = 0.5 .. 1.0): full-mesh Pearson of
              rho_k vs counts(f * R_theta S[..]), maximised over theta.
              f = 1.0 is the 'figure recurrence' R (does the end-of-epoch
              pattern re-form where it was?); RA = its azimuth-randomised null.
"""
import json, math, os, sys, time
import numpy as np
from multiprocessing import Pool

import memory_run as MR
from memory_run import counts, inner, pear, rot_y, box3, jobs, SEEDS, OUT, LO, HI, PM_N

THETAS = np.arange(72) * 2 * np.pi / 72
FS = [0.5, 0.625, 0.75, 0.875, 1.0]


def scan(target, p_old, f, region, smooth=False):
    vals = []
    for th in THETAS:
        r = counts(rot_y(p_old, th) * f)
        if smooth:
            r = box3(r)
        vals.append(pear(target, region(r)))
    k = int(np.argmax(vals))
    return vals[0], vals[k], float(np.degrees(THETAS[k]))


def azi_random(p, rng):
    """same radial/polar distribution, azimuth about y randomised"""
    rho = np.hypot(p[:, 0], p[:, 2])
    ph = rng.random(len(p)) * 2 * np.pi
    return np.stack([rho * np.cos(ph), p[:, 1], rho * np.sin(ph)], axis=1)


def load(name, sg, seed):
    d = np.load(os.path.join(OUT, '%s_sg%.2f_s%d.npz' % (name, sg, seed)))
    return d['snaps'], d['curve'], d['diag'], json.loads(str(d['meta']))


def analyze_run(job):
    name, sg, seed = job
    S, curve, diag, meta = load(name, sg, seed)
    other = SEEDS[(SEEDS.index(seed) + 1) % len(SEEDS)]
    SO = load(name, sg, other)[0]
    rng = np.random.default_rng(1000 + seed)
    N = S.shape[1]
    full = lambda r: r
    rows = []
    for k in range(1, len(S)):
        rho = counts(S[k]); inn = inner(rho)
        rho_s = box3(rho); inn_s = inner(rho_s)
        row = {'name': name, 'sg': sg, 'seed': seed, 'epoch': k, 'inner_frac': float(inn.sum() / N)}
        row['M_raw'], row['M_max'], row['M_th'] = scan(inn, S[k - 1], 0.5, inner)
        r_old = counts(S[k - 1])
        ix = 2 * np.arange(LO, HI) - PM_N // 2
        row['M_single'] = pear(inn, r_old[np.ix_(ix, ix, ix)])
        row['Ms_raw'], row['Ms_max'], _ = scan(inn_s, S[k - 1], 0.5, inner, smooth=True)
        rel0 = inner(counts(S[k - 1] * 0.5)).ravel()
        sh = np.array([pear(inn, rng.permutation(rel0)) for _ in range(200)])
        row['sh_mean'], row['sh_sd'] = float(sh.mean()), float(sh.std())
        row['sh_max72'] = float(np.mean([np.max([pear(inn, rng.permutation(rel0)) for _ in range(72)])
                                         for _ in range(10)]))
        rel0s = inner(box3(counts(S[k - 1] * 0.5))).ravel()
        row['shs_mean'] = float(np.mean([pear(inn_s, rng.permutation(rel0s)) for _ in range(100)]))
        row['A_raw'] = float(np.mean([pear(inn, inner(counts(azi_random(S[k - 1], rng) * 0.5))) for _ in range(8)]))
        if k >= 2:
            row['M2_raw'], row['M2_max'], _ = scan(inn, S[k - 2], 0.5, inner)
            row['M4_raw'], row['M4_max'], _ = scan(inn, S[k - 2], 0.25, inner)
            row['Ms2_raw'], row['Ms2_max'], _ = scan(inn_s, S[k - 2], 0.5, inner, smooth=True)
        row['X_raw'], row['X_max'], _ = scan(inn, SO[k - 1], 0.5, inner)
        row['Xs_raw'], row['Xs_max'], _ = scan(inn_s, SO[k - 1], 0.5, inner, smooth=True)
        # scale scan on the full mesh
        for f in FS:
            r0, rm, th = scan(rho, S[k - 1], f, full)
            row['Mf_raw_%.3f' % f] = r0; row['Mf_max_%.3f' % f] = rm
            _, xm, _ = scan(rho, SO[k - 1], f, full)
            row['Xf_max_%.3f' % f] = xm
            if k >= 2:
                _, m2, _ = scan(rho, S[k - 2], f, full)
                row['M2f_max_%.3f' % f] = m2
        row['R_raw'], row['R_max'], row['R_th'] = row['Mf_raw_1.000'], row['Mf_max_1.000'], th
        row['RA'] = float(np.mean([pear(rho, counts(azi_random(S[k - 1], rng))) for _ in range(8)]))
        rows.append(row)
    return rows


def stat(v):
    v = np.array([x for x in v if x is not None], float)
    if not len(v):
        return float('nan'), float('nan'), 0
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0, len(v)


def report(rows, curves, diag):
    keys = sorted(set((r['name'], r['sg']) for r in rows), key=lambda k: (k[0] != 'spin', k[1]))
    def line(name, sg, cols):
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        return '%-16s ' % ('%s sg=%.2f' % (name, sg)) + ' '.join(
            '%+.3f+/-%.3f' % stat([r.get(c) for r in R])[:2] if c else '' for c in cols)
    def head(cols):
        return '%-16s ' % 'setting' + ' '.join('%-13s' % c for c in cols)
    print('\n' + '=' * 110)
    print('PRESCRIBED MEMORY INDEX M_retained (inner 16^3 cells, end of epoch k vs x0.5 relic of end of epoch k-1)')
    print('mean +/- sd over epochs x seeds; n = %d values per setting (2-back: %d)' % (len([r for r in rows if r['name']==keys[0][0] and r['sg']==keys[0][1]]), len([r for r in rows if r['name']==keys[0][0] and r['sg']==keys[0][1] and 'M2_raw' in r])))
    print('=' * 110)
    cols = ['M_raw', 'M_max', 'M_single', 'sh_mean', 'sh_max72', 'M2_raw', 'M2_max', 'X_raw', 'X_max', 'A_raw']
    print(head(cols))
    for name, sg in keys:
        print(line(name, sg, cols))
    print('\nPAIRED EXCESS over same-epoch nulls: own relic minus null relic; cell = mean+/-sd (t = mean/(sd/sqrt n)); n in brackets')
    pairs = [('M_max', 'X_max', 'M-X(seed)'), ('M_max', 'M2_max', 'M-M2(2back)'), ('M_raw', 'A_raw', 'M-A(azi)'),
             ('Ms_max', 'Xs_max', 'Ms-Xs'), ('R_max', 'Xf_max_1.000', 'R-RX(seed)'), ('R_max', 'M2f_max_1.000', 'R-R2(2back)'),
             ('R_raw', 'RA', 'R-RA(azi)'), ('Mf_max_0.750', 'Xf_max_0.750', 'f.75 own-seed'), ('Mf_max_0.875', 'Xf_max_0.875', 'f.875 own-seed')]
    print('%-16s ' % 'setting' + ' '.join('%-22s' % lab for _, _, lab in pairs))
    for name, sg in keys:
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        cells = []
        for a, b, lab in pairs:
            d = [r[a] - r[b] for r in R if a in r and b in r]
            m, sd, n = stat(d)
            t = m / (sd / math.sqrt(n)) if n > 1 and sd > 0 else float('nan')
            cells.append('%+.3f+/-%.3f(t%+.1f)[%d]' % (m, sd, t, n))
        print('%-16s ' % ('%s sg=%.2f' % (name, sg)) + ' '.join('%-22s' % c for c in cells))
    print('\nSMOOTHED (3^3 boxcar):')
    cols = ['Ms_raw', 'Ms_max', 'shs_mean', 'Ms2_raw', 'Ms2_max', 'Xs_raw', 'Xs_max']
    print(head(cols))
    for name, sg in keys:
        print(line(name, sg, cols))
    print('\nSCALE SCAN, full mesh, theta-maximised: relic of S[k-1] scaled by f (0.5 = the rescale image, 1.0 = absolute coords)')
    cols = ['Mf_max_%.3f' % f for f in FS] + ['Mf_raw_1.000', 'RA']
    print(head(['f=%.3f' % f for f in FS] + ['R_raw(f=1)', 'R_azirand']))
    for name, sg in keys:
        print(line(name, sg, cols))
    print('  cross-seed null (Xf_max):')
    cols = ['Xf_max_%.3f' % f for f in FS]
    for name, sg in keys:
        print(line(name, sg, cols))
    print('  two-back null (M2f_max):')
    cols = ['M2f_max_%.3f' % f for f in FS]
    for name, sg in keys:
        print(line(name, sg, cols))
    print('\nx4 two-back (M4), inner fraction, best rotation angle stats:')
    for name, sg in keys:
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        print('%-16s M4_raw %+.3f+/-%.3f  M4_max %+.3f+/-%.3f  inner_frac %.3f  M_th(deg) median %.0f  R_th median %.0f' % (
            '%s sg=%.2f' % (name, sg), *stat([r.get('M4_raw') for r in R])[:2], *stat([r.get('M4_max') for r in R])[:2],
            stat([r['inner_frac'] for r in R])[0], np.median([r['M_th'] for r in R]), np.median([r['R_th'] for r in R])))
    print('\nPER-EPOCH M_raw (prescribed) by seed  [epochs 1..n]:')
    for name, sg in keys:
        for seed in SEEDS:
            R = [r for r in rows if r['name'] == name and r['sg'] == sg and r['seed'] == seed]
            if R:
                m, s, n = stat([r['M_raw'] for r in R])
                print('  %-16s seed %-6d %s | mean %+.3f sd %.3f' % ('%s sg=%.2f' % (name, sg), seed,
                      ' '.join('%+.3f' % r['M_raw'] for r in R), m, s))
    print('\nPER-EPOCH M_max (rotation-maximised) by seed:')
    for name, sg in keys:
        for seed in SEEDS:
            R = [r for r in rows if r['name'] == name and r['sg'] == sg and r['seed'] == seed]
            if R:
                m, s, n = stat([r['M_max'] for r in R])
                print('  %-16s seed %-6d %s | mean %+.3f sd %.3f' % ('%s sg=%.2f' % (name, sg), seed,
                      ' '.join('%+.3f' % r['M_max'] for r in R), m, s))
    print('\nPER-EPOCH R_max (figure recurrence, f=1, rotation-maximised) by seed:')
    for name, sg in keys:
        for seed in SEEDS:
            R = [r for r in rows if r['name'] == name and r['sg'] == sg and r['seed'] == seed]
            if R:
                m, s, n = stat([r['R_max'] for r in R])
                print('  %-16s seed %-6d %s | mean %+.3f sd %.3f' % ('%s sg=%.2f' % (name, sg), seed,
                      ' '.join('%+.3f' % r['R_max'] for r in R), m, s))
    ts = ['0.00', '0.25', '0.50', '1.00', '2.00', '3.00', '5.00', '7.00', '9.00', '9.90']
    print('\nM(t) DECAY (theta = 0, prescribed inner index), mean over epochs x seeds; t = s since rescale')
    print('%-16s ' % 'setting' + ' '.join('%7s' % t for t in ts) + '   | inner frac at t=0 / 9.9')
    for name, sg in keys:
        c = curves.get('%s_sg%.2f' % (name, sg), {})
        print('%-16s ' % ('%s sg=%.2f' % (name, sg)) + ' '.join('%7.3f' % np.mean(c[t]) if t in c else '    nan' for t in ts)
              + '   | %.2f / %.2f' % (np.mean(c.get('frac0.00', [np.nan])), np.mean(c.get('frac9.90', [np.nan]))))
    print('\nDIAGNOSTICS (run means): clamp fraction, median |F_selfgrav|, |F_chladni|, |F_flow|, speed, r, PM residual')
    for name, sg in keys:
        for d in diag.get('%s_sg%.2f' % (name, sg), []):
            print('  %-16s clamp %.3f  |Fsg| %7.2f  |Fchl| %7.2f  |Fflow| %6.2f  speed %6.2f  r_med %5.2f  resid %.2e  wall %.0fs frames %d switches %d' % (
                '%s sg=%.2f' % (name, sg), d['clamp'], d['sgF_med'], d['Fchl_med'], d['Fflow_med'], d['speed_med'],
                d['r_med'], d['pm_resid'], d['wall_s'], d['frames'], d['switches']))


if __name__ == '__main__':
    t0 = time.time()
    J = jobs()
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        d = json.load(open(os.path.join(OUT, 'memory_results2.json')))
        report(d['rows'], d['curves'], d['diag']); sys.exit()
    rows = []
    with Pool(4) as pool:
        for rr in pool.imap_unordered(analyze_run, J):
            rows.extend(rr)
            print('analyzed', rr[0]['name'], rr[0]['sg'], rr[0]['seed'], '(%.0fs)' % (time.time() - t0), flush=True)
    rows.sort(key=lambda r: (r['name'] != 'spin', r['sg'], SEEDS.index(r['seed']), r['epoch']))
    curves, diag = {}, {}
    for name, sg, seed in J:
        S, C, dg, meta = load(name, sg, seed)
        key = '%s_sg%.2f' % (name, sg)
        for t in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 9.9):
            sel = np.abs(C[:, 1] - t) <= 0.051
            if sel.any():
                curves.setdefault(key, {}).setdefault('%.2f' % t, []).extend(C[sel, 2].tolist())
                curves.setdefault(key, {}).setdefault('frac%.2f' % t, []).extend(C[sel, 3].tolist())
        diag.setdefault(key, []).append({'clamp': float(dg[:, 1].mean()), 'sgF_med': float(dg[:, 2].mean()),
                                         'speed_med': float(dg[:, 3].mean()), 'r_med': float(dg[:, 4].mean()),
                                         'Fchl_med': float(dg[:, 5].mean()), 'Fflow_med': float(dg[:, 6].mean()),
                                         'pm_resid': float(dg[:, 7].mean()), 'wall_s': meta['wall_s'],
                                         'frames': meta['nframes'], 'switches': meta['switches']})
    json.dump({'rows': rows, 'curves': curves, 'diag': diag}, open(os.path.join(OUT, 'memory_results2.json'), 'w'))
    report(rows, curves, diag)
    print('\nANALYSIS WALL %.0fs' % (time.time() - t0))
