#!/usr/bin/env python3
"""memory_run.py - MEMORY ACROSS EPOCHS with and without self-gravity.

Simulator: memory_pm.MemSim = port2.Sim (validated vs the GPU shaders) + the
chamber's particle-mesh self-gravity (memory_pm, validated separately).

Memory index (prescribed):
  M(t) = Pearson over the inner 16^3 cells (c in [8,23] per axis: the cells
  whose 2x2x2 parent block lies inside the old mesh) of
      rho(c, t)          NGP counts on the chamber's own 32^3 mesh
  vs  rho_relic(c)       counts of {x_old / 2}, x_old = positions at the end of
                         the previous epoch (= the 2x2x2 block sum of the old
                         mesh; the exact image of the x0.5 rescale)
  M_retained = M just before the next rescale.
Because the helix spins the swarm about y (~4.8 rad/s), M is also maximised
over a rigid rotation of the relic about y (72 angles).  Every null baseline
gets the same treatment.

Nulls: (a) spatially shuffled relic, (b) relic from TWO epochs back (same x2
map, and the x4 map), (c) relic from an independent seed at the same epoch
(same digit script, different matter), plus the 'figure recurrence' R =
full-mesh Pearson of the end-of-epoch density vs the previous end-of-epoch
density in ABSOLUTE coordinates (does the pattern re-form where it was?).

modes:  python3 memory_run.py smoke
        python3 memory_run.py run      (batch, multiprocessing, writes npz)
        python3 memory_run.py analyze  (post-process -> memory_results.json)
"""
import json, math, os, sys, time
import numpy as np
from multiprocessing import Pool

import port2
from port2 import PRESET, EXTENT
import memory_pm as MP
from memory_pm import PM_N

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'memory_out')
os.makedirs(OUT, exist_ok=True)

NPART = 5000
DT = 1.0 / 20.0
N_EPOCHS = 13                      # -> 12 epochs with a relic, 11 with a 2-back relic
SEEDS = [12345, 777, 31337, 2026]
SPIN_SG = [0.0, 0.15, 0.3, 0.5, 1.0]
DEF_SG = [0.0, 0.4, 1.0]

SPIN = dict(PRESET)
SPIN.update(particles=NPART, smooth=False, dt=DT)            # hard mode jumps
DEFAULT = dict(PRESET)
DEFAULT.update(particles=NPART, smooth=False, dt=DT,
               fieldExp=0.0, damping=2.5, stepsPerSec=2.0,
               constants={'a': 'phi', 'b': 'phi', 'c': 'pi'}, strideIndex=51,
               hubble=0.3, mag=0.6, twist=True, aniso=0.0, helix=0.0,
               epoch=True, epochLen=10.0, cascade='out', boundary='reflect',
               startStep=0)
CFGS = {'spin': SPIN, 'default': DEFAULT}

LO, HI = PM_N // 4, 3 * PM_N // 4          # inner block: cells 8..23


def counts(p):
    return MP.deposit(p) * 1024.0


def inner(rho):
    return rho[LO:HI, LO:HI, LO:HI]


def pear(a, b):
    a = a.ravel().astype(np.float64); b = b.ravel().astype(np.float64)
    a = a - a.mean(); b = b - b.mean()
    d = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


def rot_y(p, th):
    c, s = math.cos(th), math.sin(th)
    return np.stack([p[:, 0] * c - p[:, 2] * s, p[:, 1], p[:, 0] * s + p[:, 2] * c], axis=1)


def box3(rho):
    """3x3x3 boxcar mean (zero padded) - the smoothed variant."""
    pp = np.pad(rho, 1)
    out = np.zeros_like(rho)
    for dx in (0, 1, 2):
        for dy in (0, 1, 2):
            for dz in (0, 1, 2):
                out += pp[dx:dx + PM_N, dy:dy + PM_N, dz:dz + PM_N]
    return out / 27.0


# ----------------------------------------------------------------------------
def run_one(args):
    name, sg, seed = args
    tag = '%s_sg%.2f_s%d' % (name, sg, seed)
    path = os.path.join(OUT, tag + '.npz')
    if os.path.exists(path):
        return tag, 'cached'
    cfg = dict(CFGS[name]); cfg['seed'] = seed; cfg['selfgrav'] = sg
    sim = MP.MemSim(cfg)
    dt, L = sim.dt, cfg['epochLen']
    nframes = int(round(N_EPOCHS * L / dt)) + 2
    snaps, curve, diag, ep_frames = [], [], [], []
    relic0 = None
    t0 = time.time()
    for fi in range(nframes):
        if len(snaps) >= N_EPOCHS:
            break
        will = bool(cfg['epoch'] and ((sim.simTime + dt) - sim.lastEpochT >= L))
        if will:
            snaps.append(sim.p.astype(np.float32).copy())
            ep_frames.append(fi)
        if relic0 is not None and (fi % 2 == 0 or will):
            rho = counts(sim.p)
            inn = inner(rho)
            curve.append([sim.epochN, sim.simTime - sim.lastEpochT,
                          pear(inn, relic0), inn.sum() / len(sim.p)])
        sim.frame(fi)
        if will:
            assert sim.epoch_frames and sim.epoch_frames[-1] == fi, (fi, sim.epoch_frames[-3:])
            relic0 = inner(counts(snaps[-1] * 0.5))
        if fi % 10 == 0:
            sp = np.linalg.norm(sim.v, axis=1); rr = np.linalg.norm(sim.p, axis=1)
            diag.append([fi, sim.clamp_frac, sim.sgF_med, float(np.median(sp)),
                         float(np.median(rr)), sim.Fchl_mag, sim.Fflow_mag,
                         MP.laplacian_residual(sim.phi, sim._src) if sg > 0.001 else 0.0])
    np.savez_compressed(path, snaps=np.array(snaps), curve=np.array(curve),
                        diag=np.array(diag), ep_frames=np.array(ep_frames),
                        meta=json.dumps({'name': name, 'sg': sg, 'seed': seed,
                                         'nframes': fi + 1, 'wall_s': time.time() - t0,
                                         'switches': len(sim.switch_frames)}))
    return tag, '%.1fs frames=%d epochs=%d' % (time.time() - t0, fi + 1, len(snaps))


def jobs():
    J = []
    for sg in SPIN_SG:
        for seed in SEEDS:
            J.append(('spin', sg, seed))
    for sg in DEF_SG:
        for seed in SEEDS:
            J.append(('default', sg, seed))
    return J


# ----------------------------------------------------------------------------
THETAS = np.arange(72) * 2 * np.pi / 72


def scan(target, p_old, f, region, smooth=False):
    """max over rigid y-rotation of the relic; returns (raw, max, argmax_deg)."""
    vals = []
    for th in THETAS:
        r = counts(rot_y(p_old, th) * f)
        if smooth:
            r = box3(r)
        vals.append(pear(target, region(r)))
    k = int(np.argmax(vals))
    return vals[0], vals[k], float(np.degrees(THETAS[k]))


def analyze():
    J = jobs()
    data = {}
    for name, sg, seed in J:
        tag = '%s_sg%.2f_s%d' % (name, sg, seed)
        d = np.load(os.path.join(OUT, tag + '.npz'))
        data[(name, sg, seed)] = {'snaps': d['snaps'], 'curve': d['curve'],
                                  'diag': d['diag'], 'meta': json.loads(str(d['meta']))}
    rng = np.random.default_rng(11)
    rows = []
    for (name, sg, seed), D in data.items():
        S = D['snaps']; n = len(S); N = S.shape[1]
        other_seed = SEEDS[(SEEDS.index(seed) + 1) % len(SEEDS)]
        SO = data[(name, sg, other_seed)]['snaps']
        full = lambda r: r
        for k in range(1, n):
            rho = counts(S[k]); inn = inner(rho)
            rho_s = box3(rho); inn_s = inner(rho_s)
            row = {'name': name, 'sg': sg, 'seed': seed, 'epoch': k,
                   'inner_frac': float(inn.sum() / N)}
            # main memory index (prescribed) + rotation-maximised
            row['M_raw'], row['M_max'], row['M_th'] = scan(inn, S[k - 1], 0.5, inner)
            # single-cell variant of the relic map (c_old = 2c - N/2, no block sum)
            r_old = counts(S[k - 1])
            sc = r_old[2 * np.arange(LO, HI) - PM_N // 2][:, 2 * np.arange(LO, HI) - PM_N // 2][:, :, 2 * np.arange(LO, HI) - PM_N // 2]
            row['M_single'] = pear(inn, sc)
            # smoothed
            row['Ms_raw'], row['Ms_max'], _ = scan(inn_s, S[k - 1], 0.5, inner, smooth=True)
            # (a) shuffled relic
            rel0 = inner(counts(S[k - 1] * 0.5)).ravel()
            sh = np.array([pear(inn, rng.permutation(rel0)) for _ in range(200)])
            row['sh_mean'], row['sh_sd'] = float(sh.mean()), float(sh.std())
            row['sh_max72'] = float(np.mean([np.max([pear(inn, rng.permutation(rel0)) for _ in range(72)])
                                             for _ in range(10)]))
            rel0s = inner(box3(counts(S[k - 1] * 0.5))).ravel()
            row['shs_mean'] = float(np.mean([pear(inn_s, rng.permutation(rel0s)) for _ in range(100)]))
            # (b) two epochs back: same x2 map, and the x4 map
            if k >= 2:
                row['M2_raw'], row['M2_max'], _ = scan(inn, S[k - 2], 0.5, inner)
                row['M4_raw'], row['M4_max'], _ = scan(inn, S[k - 2], 0.25, inner)
                row['Ms2_raw'], row['Ms2_max'], _ = scan(inn_s, S[k - 2], 0.5, inner, smooth=True)
            # (c) cross-seed relic (same script, independent matter)
            row['X_raw'], row['X_max'], _ = scan(inn, SO[k - 1], 0.5, inner)
            row['Xs_raw'], row['Xs_max'], _ = scan(inn_s, SO[k - 1], 0.5, inner, smooth=True)
            # figure recurrence in absolute coordinates (full mesh, no rescale)
            row['R_raw'], row['R_max'], row['R_th'] = scan(rho, S[k - 1], 1.0, full)
            row['RX_raw'], row['RX_max'], _ = scan(rho, SO[k - 1], 1.0, full)
            if k >= 2:
                row['R2_raw'], row['R2_max'], _ = scan(rho, S[k - 2], 1.0, full)
            rows.append(row)
        print('analyzed', name, sg, seed, 'epochs', n - 1, flush=True)
    # decay curves: M(theta=0, t) averaged over epochs, per setting
    curves = {}
    for (name, sg, seed), D in data.items():
        C = D['curve']
        key = '%s_sg%.2f' % (name, sg)
        for t in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 9.9):
            sel = np.abs(C[:, 1] - t) <= 0.051
            if sel.any():
                curves.setdefault(key, {}).setdefault('%.2f' % t, []).extend(C[sel, 2].tolist())
                curves.setdefault(key, {}).setdefault('frac%.2f' % t, []).extend(C[sel, 3].tolist())
    diag = {}
    for (name, sg, seed), D in data.items():
        key = '%s_sg%.2f' % (name, sg)
        dg = D['diag']
        diag.setdefault(key, []).append({'clamp': float(dg[:, 1].mean()), 'sgF_med': float(dg[:, 2].mean()),
                                         'speed_med': float(dg[:, 3].mean()), 'r_med': float(dg[:, 4].mean()),
                                         'Fchl_med': float(dg[:, 5].mean()), 'Fflow_med': float(dg[:, 6].mean()),
                                         'pm_resid': float(dg[:, 7].mean()), 'wall_s': D['meta']['wall_s'],
                                         'frames': D['meta']['nframes'], 'switches': D['meta']['switches']})
    json.dump({'rows': rows, 'curves': curves, 'diag': diag},
              open(os.path.join(OUT, 'memory_results.json'), 'w'))
    report(rows, curves, diag)


def report(rows, curves, diag):
    import collections
    def stat(v):
        v = np.array([x for x in v if x is not None], float)
        return (v.mean(), v.std(ddof=1) if len(v) > 1 else 0.0, len(v)) if len(v) else (float('nan'), float('nan'), 0)
    keys = sorted(set((r['name'], r['sg']) for r in rows), key=lambda k: (k[0] != 'spin', k[1]))
    print('\n' + '=' * 100)
    print('M_retained = Pearson(inner 16^3 cells) of end-of-epoch density vs x0.5-rescaled previous end-of-epoch density')
    print('raw = fixed frame; max = best rigid rotation about y (72 angles). mean +/- sd over (epochs x seeds); n')
    print('=' * 100)
    hdr = '%-16s %-14s %-14s %-14s %-14s %-14s %-14s %-14s' % (
        'setting', 'M_raw', 'M_max', 'shuffle', 'shuf_max72', '2back_raw', '2back_max', 'xseed_max')
    print(hdr)
    for name, sg in keys:
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        f = lambda key: '%+.3f+/-%.3f' % stat([r.get(key) for r in R])[:2]
        print('%-16s %-14s %-14s %-14s %-14s %-14s %-14s %-14s' % (
            '%s sg=%.2f' % (name, sg), f('M_raw'), f('M_max'), f('sh_mean'), f('sh_max72'),
            f('M2_raw'), f('M2_max'), f('X_max')))
    print('\nsmoothed (3^3 boxcar) variant:')
    print('%-16s %-14s %-14s %-14s %-14s %-14s' % ('setting', 'Ms_raw', 'Ms_max', 'shuffle_s', '2back_s_max', 'xseed_s_max'))
    for name, sg in keys:
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        f = lambda key: '%+.3f+/-%.3f' % stat([r.get(key) for r in R])[:2]
        print('%-16s %-14s %-14s %-14s %-14s %-14s' % (
            '%s sg=%.2f' % (name, sg), f('Ms_raw'), f('Ms_max'), f('shs_mean'), f('Ms2_max'), f('Xs_max')))
    print('\nfigure recurrence R (full mesh, absolute coords, end-of-epoch k vs k-1); x4 map two-back; single-cell relic map; inner fraction:')
    print('%-16s %-14s %-14s %-14s %-14s %-14s %-14s %-10s' % ('setting', 'R_raw', 'R_max', 'R_2back_max', 'R_xseed_max', 'M4_max', 'M_single', 'inner_frac'))
    for name, sg in keys:
        R = [r for r in rows if r['name'] == name and r['sg'] == sg]
        f = lambda key: '%+.3f+/-%.3f' % stat([r.get(key) for r in R])[:2]
        print('%-16s %-14s %-14s %-14s %-14s %-14s %-14s %-10s' % (
            '%s sg=%.2f' % (name, sg), f('R_raw'), f('R_max'), f('R2_max'), f('RX_max'), f('M4_max'), f('M_single'),
            '%.3f' % stat([r['inner_frac'] for r in R])[0]))
    print('\nper-epoch M_raw / M_max by seed:')
    for name, sg in keys:
        for seed in SEEDS:
            R = [r for r in rows if r['name'] == name and r['sg'] == sg and r['seed'] == seed]
            if not R:
                continue
            m, s, n = stat([r['M_raw'] for r in R]); mm, ss, _ = stat([r['M_max'] for r in R])
            print('  %s sg=%.2f seed=%-6d raw: %s  mean %.3f sd %.3f | max: %s mean %.3f sd %.3f' % (
                name, sg, seed, ' '.join('%+.2f' % r['M_raw'] for r in R), m, s,
                ' '.join('%+.2f' % r['M_max'] for r in R), mm, ss))
    print('\nM(t) decay (theta=0), mean over epochs x seeds; t = seconds since the rescale:')
    ts = ['0.00', '0.25', '0.50', '1.00', '2.00', '3.00', '5.00', '7.00', '9.00', '9.90']
    print('%-16s ' % 'setting' + ' '.join('%7s' % t for t in ts) + '   | inner frac at 0 / 9.9')
    for name, sg in keys:
        key = '%s_sg%.2f' % (name, sg)
        c = curves.get(key, {})
        print('%-16s ' % ('%s sg=%.2f' % (name, sg)) + ' '.join('%7.3f' % np.mean(c[t]) if t in c else '    nan' for t in ts)
              + '   | %.2f / %.2f' % (np.mean(c.get('frac0.00', [np.nan])), np.mean(c.get('frac9.90', [np.nan]))))
    print('\ndiagnostics (means over the run): clamp fraction, median |F_selfgrav|, median |F_chladni|, median |F_flow|, median speed, median r, PM residual, wall s')
    for name, sg in keys:
        key = '%s_sg%.2f' % (name, sg)
        for d in diag.get(key, []):
            print('  %-16s clamp %.3f  |Fsg| %7.2f  |Fchl| %7.2f  |Fflow| %6.2f  speed %6.2f  r %5.2f  resid %.2e  wall %.0fs frames %d switches %d' % (
                '%s sg=%.2f' % (name, sg), d['clamp'], d['sgF_med'], d['Fchl_med'], d['Fflow_med'], d['speed_med'],
                d['r_med'], d['pm_resid'], d['wall_s'], d['frames'], d['switches']))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if mode == 'smoke':
        N_EPOCHS = 2
        OUT = os.path.join(HERE, 'memory_out', 'smoke'); os.makedirs(OUT, exist_ok=True)
        t = time.time()
        print(run_one(('spin', 0.5, 12345)))
        d = np.load(os.path.join(OUT, 'spin_sg0.50_s12345.npz'))
        C = d['curve']; S = d['snaps']
        print('snaps', S.shape, 'epoch frames', d['ep_frames'], 'meta', str(d['meta']))
        print('M(theta=0) first rows after rescale:', np.round(C[:4], 3).tolist())
        print('M(theta=0) last rows before next rescale:', np.round(C[-3:], 3).tolist())
        inn = inner(counts(S[1]))
        print('M_raw/M_max/theta:', scan(inn, S[0], 0.5, inner))
        print('diag last:', d['diag'][-1])
        print('smoke wall %.1fs' % (time.time() - t))
    elif mode == 'run':
        J = jobs()
        print('jobs:', len(J), flush=True)
        t = time.time()
        with Pool(4) as pool:
            for tag, msg in pool.imap_unordered(run_one, J):
                print(tag, msg, '(elapsed %.0fs)' % (time.time() - t), flush=True)
        print('ALL RUNS DONE %.0fs' % (time.time() - t), flush=True)
        analyze()
        print('ANALYSIS DONE %.0fs' % (time.time() - t), flush=True)
    elif mode == 'analyze':
        analyze()
    elif mode == 'report':
        d = json.load(open(os.path.join(OUT, 'memory_results.json')))
        report(d['rows'], d['curves'], d['diag'])
