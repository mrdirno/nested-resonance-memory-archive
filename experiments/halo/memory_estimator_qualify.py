#!/usr/bin/env python3
"""memory_estimator_qualify.py - qualify a replacement cross-epoch memory estimator.

Implements docs/halo/2026-09-05_memory_estimator_qualification_protocol.md section by
section. It qualifies an instrument; it makes no claim about memory.

  Geometry    a shrink by f about the cavity centre 15.5 sends relic cell r to current
              cell x with r = f*x - 15.5(f-1). Current cell x in the inner (32/f)^3 block
              is the exact image of the relic block {f*x - 16(f-1) ... + f-1} per axis
              (nearest-cell deposit), so the predicted density is the block SUM.
  Monopole    cube orbits: cells related by a symmetry of the cube about the centre
              (same sorted |u| triple; 120 orbits on B2, 20 on B4). Subtract the orbit
              mean inside the block. Exact for any field the grid sees as spherically
              symmetric, including every nearest-cell deposit of a spherical density
              and every block sum of one. Radial classes (66/15) are a variant.
  Matrix      per condition and epoch, M[i][j] = Pearson(residual current field of run i,
              residual predicted field from run j's relic). Diagonal = own relic.
  Statistic   Q_i = M_ii minus its null prediction from the other eight entries: the
              log-additive (multiplicative) fit when every entry exceeds 0.05, which is
              exact for M_ij = a_i * b_j (a shared template with seed-dependent noise or
              amplitude), else the additive fit, exact for M_ij = a_i + b_j.
  Eligible    E1 mass in B2 >= 1%; E2 participation >= 8 and residual variance >= 1e-9
              of block variance for the current field and all three predicted fields;
              E3 |template cross-correlation| < 0.9 for both strangers; E4 all nine
              entries finite.
  Detection   S = mean Q over eligible epochs; column relabelling in blocks of 3
              consecutive eligible epochs, 4,000 draws; detected if S >= 0.02, p < 0.05,
              mean M_ii > 0 and > the shuffled-relic floor.
  Falsifiers  F1 identity checks, F2 false positives on exchangeable controls,
              F3 recovery, F4 robustness, F5 support - rules fixed in the protocol.

Usage
  --synthetic --output S.json                 controls that need no meshes (section 9)
  --input-dir DIR --manifest M --synthetic-json S.json --output Q.json   the recorded grid
  --figure Q.json OUT.png                     the figure

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone

import numpy as np

N = 32
CENTRE = (N - 1) / 2.0            # 15.5
FIRST_SCORED, LAST_SCORED = 3, 24
SCHEMA_IN = 'halo-memory-prereg/1'
SCHEMA_OUT = 'halo-memory-estimator-qualification/2'

QUALITY_RATIO_MAX = 3.0     # E5b: the strongest seed's coupling may not exceed three times the weakest's
MAIN = {'e1_mass': 0.01, 'e2_pr': 8.0, 'e2_relvar': 1e-9, 'e3_xseed': 0.9,
        'min_epochs': 12, 'support': 'orbits', 'lag2': 'box', 'model': 'hybrid', 'den_min': 0.05,
        'quality_ratio': QUALITY_RATIO_MAX}
AR1_SIZE_MAX = 0.10         # declared ceiling for the test's size at lag-one autocorrelation 0.5
AUTOCORR_CAVEAT = 0.3       # a detection with p >= P_STRONG and lag-one autocorrelation above this is flagged
F4_TOLERANCE = 0.05         # band violations allowed per variant: max(1, ceil(0.05 * runs measurable under both))
RHO_ALLOWANCE_MAX = 0.5     # a run whose templates correlate above this need not recover at alpha = 0.2
VARIANTS = {
    'e1_0.005': dict(MAIN, e1_mass=0.005), 'e1_0.02': dict(MAIN, e1_mass=0.02),
    'e2_pr4': dict(MAIN, e2_pr=4.0), 'e2_pr16': dict(MAIN, e2_pr=16.0),
    'e3_0.8': dict(MAIN, e3_xseed=0.8), 'e3_0.95': dict(MAIN, e3_xseed=0.95),
    'classes': dict(MAIN, support='classes'),
    'den_0.03': dict(MAIN, den_min=0.03), 'den_0.10': dict(MAIN, den_min=0.10),
    'ratio_2.5': dict(MAIN, quality_ratio=2.5), 'ratio_4': dict(MAIN, quality_ratio=4.0),
}
# reported contrasts, never scored: the protocol itself calls these wrong models
CONTRASTS = {'no_removal': dict(MAIN, support='none'), 'additive_only': dict(MAIN, model='additive'),
             'shells_1.0': dict(MAIN, support='shells1.0'), 'shells_0.5': dict(MAIN, support='shells0.5')}
SUPPORT_MODES = ('orbits', 'classes', 'shells1.0', 'shells0.5', 'none')

N_PERM = 4000
N_BOOT = 2000
BLOCK = 3                   # relabelling and bootstrap block, in eligible epochs
BOOT_MIN_EPOCHS = 12
ALPHAS = [0.0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
ALPHA_FAIL = 0.10
S_MIN = 0.02
P_DETECT = 0.05
P_STRONG = 0.02             # F4 bands: p < 0.02 must stay detected, p > 0.10 must stay undetected
P_WEAK = 0.10
SHUFFLE_SEED = 20260905
PERM_SEED = 20260905
PARTICLES = 4194304


# ------------------------------------------------------------------ geometry

def block_cells(f):
    q = (N // 2) // f
    return np.arange(N // 2 - q, N // 2 + q)


B2 = block_cells(2)      # 8..23
B4 = block_cells(4)      # 12..19
assert B2[0] == 8 and B2[-1] == 23 and B4[0] == 12 and B4[-1] == 19


def predicted(relic, f):
    """block SUM of the relic over each current cell's exact image: mass-conserving."""
    m = N // f
    return relic.reshape(m, f, m, f, m, f).astype(np.float64).sum(axis=(1, 3, 5))


def predicted_lag2_trilinear(relic):
    """reported variant of the secondary lag-two arm: the inner 2^3 of every 4^3 block."""
    r = relic.reshape(8, 4, 8, 4, 8, 4).astype(np.float64)
    return r[:, 1:3, :, 1:3, :, 1:3].sum(axis=(1, 3, 5))


def sub(field, cells):
    return field[np.ix_(cells, cells, cells)].astype(np.float64)


class Support:
    """monopole removal on a cubic block: exact radial classes, cube orbits, shells, none."""

    def __init__(self, cells, mode='classes'):
        u = cells - CENTRE
        q = (2 * u) ** 2                       # integer valued: (2u)^2
        r2x4 = q[:, None, None] + q[None, :, None] + q[None, None, :]
        if mode == 'classes':
            key = np.rint(r2x4).astype(np.int64)
        elif mode == 'orbits':
            # cells related by a cube symmetry: the sorted triple of |2u| per axis
            a = np.abs(2 * u).astype(np.int64)
            t = np.stack(np.meshgrid(a, a, a, indexing='ij'), axis=-1)
            t = np.sort(t, axis=-1)
            key = t[..., 0] * 10000 + t[..., 1] * 100 + t[..., 2]
        elif mode.startswith('shells'):
            width = float(mode[len('shells'):])
            key = np.floor(np.sqrt(r2x4) / 2.0 / width).astype(np.int64)
        elif mode == 'none':
            key = np.zeros(r2x4.shape, dtype=np.int64)
        else:
            raise ValueError(mode)
        _, self.inv = np.unique(key.ravel(), return_inverse=True)
        self.inv = self.inv.ravel()
        self.nclass = int(self.inv.max()) + 1
        self.counts = np.bincount(self.inv, minlength=self.nclass)
        self.n = int(cells.size ** 3)

    def class_means(self, field):
        f = np.asarray(field, dtype=np.float64).ravel()
        s = np.bincount(self.inv, weights=f, minlength=self.nclass)
        return s / np.maximum(self.counts, 1)

    def residual(self, field):
        f = np.asarray(field, dtype=np.float64).ravel()
        return f - self.class_means(f)[self.inv]

    def radialised(self, field):
        f = np.asarray(field, dtype=np.float64).ravel()
        return f - self.residual(f)


FULL = Support(np.arange(N), 'orbits')


def radialise_full(mesh):
    return FULL.radialised(mesh).reshape(N, N, N)


def pearson(a, b):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    a = a - a.mean()
    b = b - b.mean()
    va, vb = (a * a).mean(), (b * b).mean()
    if not (va > 0 and vb > 0):
        return float('nan')
    return float((a * b).mean() / math.sqrt(va * vb))


def participation(res):
    s2 = float((res * res).sum())
    s4 = float((res ** 4).sum())
    return s2 * s2 / s4 if s4 > 0 else 0.0


def relvar(res, field):
    v = float(np.var(np.asarray(field, dtype=np.float64)))
    return float(np.var(res)) / v if v > 0 else 0.0


CUBE_OPS = [(perm, flips) for perm in itertools.permutations(range(3))
            for flips in itertools.product((False, True), repeat=3)]
assert len(CUBE_OPS) == 48 and CUBE_OPS[0] == ((0, 1, 2), (False, False, False))


def apply_op(field, op):
    perm, flips = op
    out = np.transpose(field, perm)
    for ax, fl in enumerate(flips):
        if fl:
            out = np.flip(out, axis=ax)
    return out


def pairing(i, c):
    """the cyclic shift of relic columns that sends row i to column c: rows (i, i+1, i+2)
    pair with columns (c, c+1, c+2) mod 3. For c = i it is the diagonal."""
    return [((i + s) % 3, (c + s) % 3) for s in range(3)]


def off_pairing(M, i, c):
    """the six entries off the pairing, named relative to row r0 = i and column k0 = c."""
    r0, r1, r2 = i, (i + 1) % 3, (i + 2) % 3
    k0, k1, k2 = c, (c + 1) % 3, (c + 2) % 3
    return {'r0k1': M[r0][k1], 'r0k2': M[r0][k2], 'r1k0': M[r1][k0], 'r2k0': M[r2][k0],
            'r1k2': M[r1][k2], 'r2k1': M[r2][k1]}


def predict_cell(M, i, c, model='hybrid', den_min=0.05):
    """null prediction for the paired cell (i, c) from the six entries off its pairing only,
    so a genuine effect in another run's own cell cannot enter.

    additive:        (r0k1 + r0k2 + r1k0 + r2k0 - r1k2 - r2k1) / 2; exact for M = a_r + b_k.
    multiplicative:  two exact cross-ratio estimates for M = a_r * b_k, r0k1*r2k0/r2k1 and
                     r0k2*r1k0/r1k2, weighted by the squares of their denominators.
    hybrid:          w * multiplicative + (1 - w) * additive with w = D^2 / (D^2 + den_min^2),
                     D^2 = r2k1^2 + r1k2^2 the two denominators: a smooth hand-over, not a
                     switch. With no shared template every entry is near zero, D is small and
                     the additive form is used; there is then no multiplicative nuisance."""
    e = off_pairing(M, i, c)
    add = 0.5 * (e['r0k1'] + e['r0k2'] + e['r1k0'] + e['r2k0'] - e['r1k2'] - e['r2k1'])
    if model == 'additive':
        return float(add)
    d2 = e['r2k1'] ** 2 + e['r1k2'] ** 2
    if d2 <= 0:
        return float(add)
    mult = (e['r0k1'] * e['r2k0'] * e['r2k1'] + e['r0k2'] * e['r1k0'] * e['r1k2']) / d2
    mult = max(-1.0, min(1.0, mult))
    if model == 'multiplicative':
        return float(mult)
    w = d2 / (d2 + den_min ** 2)
    return float(w * mult + (1.0 - w) * add)


def contrast(M, i, c, model='hybrid', den_min=0.05):
    """M[i][c] minus its null prediction from the six entries off the pairing."""
    return float(M[i][c] - predict_cell(M, i, c, model, den_min))


def collapse_2x2(Ms, i, den_min):
    """E5 at run level. Ms: the eligible epochs' matrices. The strangers' mutual coupling
    (M_BC + M_CB)/2 and run i's coupling to the strangers (M_iB + M_iC + M_Bi + M_Ci)/4 are
    averaged over epochs. If the mutual coupling is consistent with zero (|mean| below twice
    its standard error) while run i's coupling is not and exceeds den_min, the matrix has
    collapsed to a 2x2 in which a seed-quality nuisance and an own-relic effect cannot be told
    apart. Returns (collapsed, mean mutual coupling, mean own coupling)."""
    B, C = [j for j in range(3) if j != i]
    mutual = np.array([(M[B][C] + M[C][B]) / 2.0 for M in Ms], dtype=np.float64)
    own = np.array([(M[i][B] + M[i][C] + M[B][i] + M[C][i]) / 4.0 for M in Ms], dtype=np.float64)
    n = mutual.size
    if n < 2:
        return False, float('nan'), float('nan')
    se_m = float(mutual.std(ddof=1) / math.sqrt(n))
    se_o = float(own.std(ddof=1) / math.sqrt(n))
    m_m, m_o = float(mutual.mean()), float(own.mean())
    collapsed = abs(m_m) < 2 * se_m and abs(m_o) >= 2 * se_o and abs(m_o) >= den_min
    return bool(collapsed), m_m, m_o


def quality_balance(Ms, den_min, ratio_max, model='hybrid'):
    """E5b at run level. Each seed's null value is its diagonal as predicted from the six
    off-diagonal entries (so a genuine own effect does not enter), averaged over the eligible
    epochs. When all three are positive, the largest is at least den_min and exceeds ratio_max
    times the smallest, one seed sits near the noise floor relative to
    the others and the rank-one correction rests on entries it cannot estimate; the run is not
    measurable for unbalanced seed quality. With every null value below den_min there is no
    shared template and no correction to make. Returns (unbalanced, null values)."""
    if not Ms:
        return False, [float('nan')] * 3
    nulls = [float(np.mean([predict_cell(M, j, j, model, den_min) for M in Ms])) for j in range(3)]
    hi, lo = max(nulls), min(nulls)
    # only a positive rank-one set of null values is a quality ladder; mixed signs mean the
    # off-diagonals are not a shared template at all (seed-specific patterns partly aligned),
    # which the gate does not judge
    unbalanced = lo > 0 and hi >= den_min and hi / lo > ratio_max
    return bool(unbalanced), nulls


def shuffle_rng(cond_key, seed, k):
    h = zlib.crc32(f'{cond_key[0]}|{cond_key[1]}|{cond_key[2]}'.encode())
    return np.random.default_rng([SHUFFLE_SEED, int(h), int(seed), int(k)])


# ------------------------------------------------------------------ per condition

def condition_measure(meshes, seeds, cond_key, supports, with_orientation=True, last=None):
    """per epoch: the 3x3 matrices of every arm, eligibility inputs and diagnostics.

    meshes: three arrays (epochs, 32, 32, 32) in seed-sorted order."""
    assert len(meshes) == 3 and len(seeds) == 3
    last = min(LAST_SCORED, min(len(m) for m in meshes)) if last is None else last
    rows = []
    for k in range(FIRST_SCORED, last + 1):
        cur = [m[k - 1] for m in meshes]
        rel = [m[k - 2] for m in meshes]
        rel2 = [m[k - 3] for m in meshes]
        cur2 = [sub(c, B2) for c in cur]
        cur4 = [sub(c, B4) for c in cur]
        total = [float(c.astype(np.float64).sum()) for c in cur]
        pred = [predicted(r, 2) for r in rel]
        pred4 = [predicted(r, 4) for r in rel2]
        pred4t = [predicted_lag2_trilinear(r) for r in rel2]
        relb2 = [sub(r, B2) for r in rel]
        shuf = []
        for i in range(3):
            rng = shuffle_rng(cond_key, seeds[i], k)
            shuf.append(predicted(rel[i].ravel()[rng.permutation(N ** 3)].reshape(N, N, N), 2))
        ep = {'epoch': k,
              'mass_b2': [float(cur2[i].sum()) / total[i] if total[i] > 0 else 0.0 for i in range(3)],
              'mass_b4': [float(cur4[i].sum()) / total[i] if total[i] > 0 else 0.0 for i in range(3)],
              'xseed_raw': [[pearson(cur[i], cur[j]) for j in range(3)] for i in range(3)],
              'modes': {}}
        for mode in SUPPORT_MODES:
            s2, s4 = supports[mode]
            rc = [s2.residual(c) for c in cur2]
            rp = [s2.residual(p) for p in pred]
            rc4 = [s4.residual(c) for c in cur4]
            row = {
                'M': [[pearson(rc[i], rp[j]) for j in range(3)] for i in range(3)],
                'U': [[pearson(rc[i], s2.residual(relb2[j])) for j in range(3)] for i in range(3)],
                'M2': [[pearson(rc4[i], s4.residual(pred4[j])) for j in range(3)] for i in range(3)],
                'M2t': [[pearson(rc4[i], s4.residual(pred4t[j])) for j in range(3)] for i in range(3)],
                'MR': [[pearson(rc4[i], s4.residual(pred[j][4:12, 4:12, 4:12])) for j in range(3)]
                       for i in range(3)],
                'pr_cur': [participation(r) for r in rc], 'pr_pred': [participation(r) for r in rp],
                'relvar_cur': [relvar(rc[i], cur2[i]) for i in range(3)],
                'relvar_pred': [relvar(rp[i], pred[i]) for i in range(3)],
                'tmpl_xcorr': [[pearson(rp[i], rp[j]) for j in range(3)] for i in range(3)],
                'xseed_now': [[pearson(rc[i], rc[j]) for j in range(3)] for i in range(3)],
                'c_shuf': [pearson(rc[i], s2.residual(shuf[i])) for i in range(3)],
                'radial_overlap': [pearson(s2.class_means(cur2[i]), s2.class_means(pred[i]))
                                   for i in range(3)],
            }
            if with_orientation and mode == MAIN['support']:
                orient = []
                for i in range(3):
                    c_own = row['M'][i][i]
                    j = [x for x in range(3) if x != i][0]
                    c_str = row['M'][i][j]
                    ors = [pearson(rc[i], s2.residual(apply_op(pred[i], op))) for op in CUBE_OPS[1:]]
                    ors_s = [pearson(rc[i], s2.residual(apply_op(pred[j], op))) for op in CUBE_OPS[1:]]
                    fin = [o for o in ors if o == o]
                    fin_s = [o for o in ors_s if o == o]
                    orient.append({
                        'share_own': float(np.mean([o >= c_own for o in fin])) if fin and c_own == c_own else float('nan'),
                        'max_own': float(max(fin)) if fin else float('nan'),
                        'degenerate_own': int(sum(abs(o - c_own) < 1e-3 for o in fin)) if c_own == c_own else 0,
                        'share_stranger': float(np.mean([o >= c_str for o in fin_s])) if fin_s and c_str == c_str else float('nan'),
                    })
                row['orientation'] = orient
            ep['modes'][mode] = row
        rows.append(ep)
    return rows


def inject(cur, own_relic, alpha):
    """protocol F3: block-mass-preserving mix of the current B2 block with the exact
    passive-relic prediction. Returns a full 32^3 float64 mesh."""
    out = cur.astype(np.float64).copy()
    if alpha == 0:
        return out
    p = predicted(own_relic, 2)
    cur2 = sub(cur, B2)
    m_c, m_p = cur2.sum(), p.sum()
    if not (m_c > 0 and m_p > 0):
        raise ValueError('injection needs positive block mass and relic mass')
    out[np.ix_(B2, B2, B2)] = (1.0 - alpha) * cur2 + alpha * p * (m_c / m_p)
    return out


# ------------------------------------------------------------------ run level

ARM_KEY = {'lag1': 'M', 'unmapped': 'U', 'lag2': 'M2', 'lag2_tri': 'M2t', 'matched': 'MR'}


def eligible(ep, mode_row, i, cfg):
    r = mode_row
    ok_e1 = ep['mass_b2'][i] >= cfg['e1_mass']
    ok_e2 = (r['pr_cur'][i] >= cfg['e2_pr'] and r['relvar_cur'][i] >= cfg['e2_relvar']
             and all(r['pr_pred'][j] >= cfg['e2_pr'] and r['relvar_pred'][j] >= cfg['e2_relvar']
                     for j in range(3)))
    xs = [r['tmpl_xcorr'][i][j] for j in range(3) if j != i]
    ok_e3 = all(x == x and abs(x) < cfg['e3_xseed'] for x in xs)
    finite = all(v == v for rowv in r['M'] for v in rowv)
    return bool(ok_e1 and ok_e2 and ok_e3 and finite), {'e1': bool(ok_e1), 'e2': bool(ok_e2),
                                                        'e3': bool(ok_e3), 'e4': bool(finite)}


def block_relabel_test(Q, rng, n_perm=N_PERM):
    """Q: (n, 3) contrasts at cells (i, c) for c = 0,1,2 with the own column at index 0.
    The own label is moved uniformly among the three columns, one draw per block of
    BLOCK consecutive eligible epochs. Returns S, p for each column taken as own."""
    n = Q.shape[0]
    nb = int(math.ceil(n / BLOCK))
    pick_blocks = rng.integers(0, 3, size=(n_perm, nb))
    pick = np.repeat(pick_blocks, BLOCK, axis=1)[:, :n]
    vals = Q[np.arange(n)[None, :], pick]
    s_perm = vals.mean(axis=1)
    out = {}
    for name, col in (('own', 0), ('B', 1), ('C', 2)):
        s = float(Q[:, col].mean())
        p = (1 + int((s_perm >= s).sum())) / (n_perm + 1)
        out[name] = {'S': s, 'p': p}
    return out


def block_signflip_p(x, rng, n_perm=N_PERM):
    """two-sided sign-flip test of mean(x) = 0 with flips shared inside blocks."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n == 0:
        return float('nan')
    nb = int(math.ceil(n / BLOCK))
    signs = np.repeat(rng.choice([-1.0, 1.0], size=(n_perm, nb)), BLOCK, axis=1)[:, :n]
    m = abs(float(x.mean()))
    perm = np.abs((signs * x[None, :]).mean(axis=1))
    return (1 + int((perm >= m).sum())) / (n_perm + 1)


def detection_rule(S, p, mean_own, mean_shuf):
    """protocol section 7: S >= S_MIN, p < P_DETECT, mean own correlation positive and above
    the shuffled-relic floor (the floor condition is waived when the floor is undefined)."""
    return bool(S >= S_MIN and p < P_DETECT and mean_own > 0
                and (mean_shuf != mean_shuf or mean_own > mean_shuf))


def block_bootstrap(e, rng):
    n = e.size
    if n < BOOT_MIN_EPOCHS:
        return None
    nb = int(math.ceil(n / BLOCK))
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, nb))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(N_BOOT, -1)[:, :n]
    means = e[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def lag1_autocorr(x):
    x = np.asarray(x, dtype=np.float64)
    if x.size < 3 or np.var(x) <= 0:
        return float('nan')
    x = x - x.mean()
    return float((x[:-1] * x[1:]).sum() / (x * x).sum())


def summarise_run(rows, i, cfg, rng, arm='lag1', mask_override=None):
    """apply eligibility and the detection rule to run i of a condition under cfg."""
    mode = cfg['support']
    key = ARM_KEY['lag2_tri' if (arm == 'lag2' and cfg['lag2'] == 'trilinear') else arm]
    elig, gates, Q, e_unc, D, shuf, own, stran, branch, rho, Ms = [], [], [], [], [], [], [], [], [], [], []
    strangers = [j for j in range(3) if j != i]
    for idx, ep in enumerate(rows):
        r = ep['modes'][mode]
        if mask_override is not None:
            ok, g = bool(mask_override[idx]), {'e1': True, 'e2': True, 'e3': True, 'e4': True}
        else:
            ok, g = eligible(ep, r, i, cfg)
        M = r[key]
        fin = all(v == v for rowv in M for v in rowv)
        ok = ok and fin
        gates.append(g)
        elig.append(bool(ok))
        if ok:
            model, dm = cfg.get('model', 'hybrid'), cfg.get('den_min', 0.05)
            Q.append([contrast(M, i, i, model, dm)] + [contrast(M, i, c, model, dm) for c in strangers])
            e = off_pairing(M, i, i)
            d2 = e['r2k1'] ** 2 + e['r1k2'] ** 2
            branch.append(float(d2 / (d2 + dm ** 2)) if model == 'hybrid' else (1.0 if model == 'multiplicative' else 0.0))
            rho.append(float(np.mean([abs(r['tmpl_xcorr'][i][j]) for j in strangers])))
            Ms.append(M)
            e_unc.append(M[i][i] - np.mean([M[i][j] for j in strangers]))
            D.append(M[i][strangers[0]] - M[i][strangers[1]])
            shuf.append(r['c_shuf'][i])
            own.append(M[i][i])
            stran.append(float(np.mean([M[i][j] for j in strangers])))
    n_el = sum(elig)
    if mask_override is None:
        collapsed, m_mutual, m_own = collapse_2x2(Ms, i, cfg.get('den_min', 0.05))
        unbalanced, coup = quality_balance(Ms, cfg.get('den_min', 0.05), cfg.get('quality_ratio', QUALITY_RATIO_MAX),
                                           cfg.get('model', 'hybrid'))
    else:
        collapsed, m_mutual, m_own, unbalanced, coup = False, float('nan'), float('nan'), False, [float('nan')] * 3
    out = {'eligible_epochs': n_el, 'eligible_mask': elig,
           'gate_fail_counts': {g2: sum(1 for g in gates if not g[g2]) for g2 in ('e1', 'e2', 'e3', 'e4')},
           'e5_collapse': bool(collapsed), 'mean_mutual_coupling': m_mutual, 'mean_own_coupling': m_own,
           'e5_unbalanced': bool(unbalanced), 'seed_null_values': coup,
           'measurable': n_el >= cfg['min_epochs'] and not collapsed and not unbalanced,
           'p_min': 3.0 ** -int(math.ceil(n_el / BLOCK)) if n_el else None}
    if out['measurable']:
        Qm = np.array(Q, dtype=np.float64)
        test = block_relabel_test(Qm, rng)
        mean_own = float(np.mean(own))
        mean_shuf = float(np.nanmean(shuf)) if any(s == s for s in shuf) else float('nan')
        out.update(test)
        out['detected'] = detection_rule(test['own']['S'], test['own']['p'], mean_own, mean_shuf)
        out['below_floor'] = bool(test['own']['S'] > 0 and test['own']['p'] < P_DETECT
                                  and test['own']['S'] < S_MIN)
        out['S_ci95_block_bootstrap'] = block_bootstrap(Qm[:, 0], rng)
        out['lag1_autocorr_Q'] = lag1_autocorr(Qm[:, 0])
        out['multiplicative_weight_mean'] = float(np.mean(branch))
        out['template_rho_mean'] = float(np.mean(rho))
        out['autocorrelation_caveat'] = bool(out['detected'] and test['own']['p'] >= P_STRONG
                                             and out['lag1_autocorr_Q'] == out['lag1_autocorr_Q']
                                             and out['lag1_autocorr_Q'] > AUTOCORR_CAVEAT)
        out['mean_c_own'] = mean_own
        out['mean_c_stranger'] = float(np.mean(stran))
        out['mean_c_shuffle'] = mean_shuf
        out['uncentred_excess'] = float(np.mean(e_unc))
        out['mean_D'] = float(np.mean(D))
        out['D_signflip_p'] = block_signflip_p(D, rng)
        out['Q_by_epoch'] = [float(x) for x in Qm[:, 0]]
    return out


# ------------------------------------------------------------------ loading

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_grid(indir):
    runs, files = {}, []
    for fn in sorted(os.listdir(indir)):
        if not fn.endswith('.json'):
            continue
        path = os.path.join(indir, fn)
        try:
            with open(path) as fh:
                head = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(head, dict) or head.get('schema') != SCHEMA_IN:
            continue
        mesh_path = os.path.join(indir, head['mesh_file'])
        if not os.path.exists(mesh_path):
            print(f'  skipping {fn}: mesh missing', file=sys.stderr)
            continue
        raw = np.fromfile(mesh_path, dtype='<f4')
        k = head['mesh_count']
        if raw.size != k * N ** 3:
            raise ValueError(f'{mesh_path}: {raw.size} floats, expected {k * N ** 3}')
        p = head['params']
        key = (p['preset'], float(p['selfgrav']), float(p['gainloss']))
        runs.setdefault(key, []).append({'seed': int(p['seed']), 'tag': head['tag'],
                                         'mesh': raw.reshape(k, N, N, N),
                                         'particles': int(p['particles'])})
        files.append({'file': fn, 'sha256': sha256_file(path), 'bytes': os.path.getsize(path)})
        files.append({'file': head['mesh_file'], 'sha256': sha256_file(mesh_path),
                      'bytes': os.path.getsize(mesh_path)})
    for key in runs:
        runs[key].sort(key=lambda r: r['seed'])
    return runs, files


def check_manifest(files, manifest_path):
    with open(manifest_path) as fh:
        man = json.load(fh)
    by_name = {f['file']: f for f in files}
    matched, mismatched, missing = [], [], []
    for entry in man.get('files', []):
        name = entry.get('file')
        got = by_name.get(name)
        if got is None:
            missing.append(name)
        elif got['sha256'] == entry.get('sha256') and got['bytes'] == entry.get('bytes'):
            matched.append(name)
        else:
            mismatched.append(name)
    return {'manifest': manifest_path, 'manifest_sha256': sha256_file(manifest_path),
            'matched': len(matched), 'mismatched': mismatched, 'missing': missing,
            'verified': bool(matched) and not mismatched and not missing}


# ------------------------------------------------------------------ the grid

def measure_grid(runs, supports, with_orientation=True, radialised=False, label=''):
    """{condition: rows} for a grid {condition: [run, run, run]} in seed-sorted order."""
    t0 = time.time()
    out = {}
    for ci, key in enumerate(sorted(runs)):
        group = runs[key]
        if len(group) != 3:
            print(f'  {key}: {len(group)} seeds, the protocol needs exactly 3; skipped', file=sys.stderr)
            continue
        meshes = [g['mesh'] for g in group]
        if radialised:
            meshes = [np.stack([radialise_full(m) for m in run]) for run in meshes]
        out[key] = {'rows': condition_measure(meshes, [g['seed'] for g in group], key, supports,
                                              with_orientation),
                    'seeds': [g['seed'] for g in group], 'tags': [g.get('tag') for g in group]}
        print(f'  [{label}] {ci + 1}/{len(runs)} {key}  {time.time() - t0:.0f}s', file=sys.stderr)
    return out


def run_label(key, seed):
    return f'{key[0]}_sg{key[1]:g}_gl{key[2]:g}_seed{seed}'


def summarise_all(measured, cfg, arm='lag1'):
    res = {}
    for key in sorted(measured):
        rows = measured[key]['rows']
        for i, seed in enumerate(measured[key]['seeds']):
            res[(key, seed)] = summarise_run(rows, i, cfg, np.random.default_rng(PERM_SEED), arm)
    return res


def injection_sweep(runs, measured, cfg, supports, keys=None):
    """F3: S(alpha), p(alpha), alpha* on the measurable runs under cfg. Eligibility is fixed
    at alpha = 0; only the injected run's current field changes, so only the three entries
    of its row are recomputed and the other six are unchanged. The shuffled floor is held
    at its baseline value. alpha* is the smallest alpha at which the full detection rule
    holds AND S(alpha) - S(0) >= S_MIN, so a run's baseline signal does not count as
    sensitivity. alpha*_eff = alpha* * (1 - rho), rho the run's mean template correlation:
    the contrast can respond only to the seed-specific part of the injected template."""
    mode = cfg['support']
    s2 = supports[mode][0]
    base = summarise_all(measured, cfg)
    out = {}
    for (key, seed), summ in base.items():
        if not summ['measurable'] or (keys is not None and (key, seed) not in keys):
            continue
        group = runs[key]
        i = [g['seed'] for g in group].index(seed)
        meshes = [g['mesh'] for g in group]
        rows = measured[key]['rows']
        mask = summ['eligible_mask']
        model, dm = cfg.get('model', 'hybrid'), cfg.get('den_min', 0.05)
        strangers = [j for j in range(3) if j != i]
        curve, alpha_star, s0 = [], None, None
        for alpha in ALPHAS:
            Q, own = [], []
            for idx, ep in enumerate(rows):
                if not mask[idx]:
                    continue
                k = ep['epoch']
                cur = inject(meshes[i][k - 1], meshes[i][k - 2], alpha)
                rc = s2.residual(sub(cur, B2))
                M = [list(r) for r in ep['modes'][mode]['M']]
                M[i] = [pearson(rc, s2.residual(predicted(meshes[j][k - 2], 2))) for j in range(3)]
                Q.append([contrast(M, i, i, model, dm)] + [contrast(M, i, c, model, dm) for c in strangers])
                own.append(M[i][i])
            Qm = np.array(Q)
            test = block_relabel_test(Qm, np.random.default_rng(PERM_SEED))['own']
            if s0 is None:
                s0 = test['S']
            det = detection_rule(test['S'], test['p'], float(np.mean(own)), summ.get('mean_c_shuffle', float('nan')))
            inc = test['S'] - s0 >= S_MIN
            curve.append({'alpha': alpha, 'S': test['S'], 'p': test['p'], 'detected': det,
                          'increment_reached': bool(inc)})
            if alpha_star is None and det and inc:
                alpha_star = alpha
        rho = summ.get('template_rho_mean', 0.0)
        out[(key, seed)] = {'curve': curve, 'alpha_star': alpha_star,
                            'alpha_star_eff': None if alpha_star is None else alpha_star * (1.0 - rho),
                            'template_rho_mean': rho,
                            'baseline_detected': bool(summ['detected']),
                            'recovered_at_0.2': bool(curve[-1]['detected'] and curve[-1]['increment_reached'])}
    return out


def binom_sf(k, n, p):
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def binom_interval(n, p=0.05):
    pm = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    cum = np.cumsum(pm)
    return [int(np.searchsorted(cum, 0.025)), int(np.searchsorted(cum, 0.975))]


F3_MIN_RUNS = 6


def f3_summary(inj):
    """F3: the median effective threshold over measurable runs, at least F3_MIN_RUNS of them,
    must not exceed ALPHA_FAIL, and every run whose templates correlate below
    RHO_ALLOWANCE_MAX must recover at alpha = 0.2."""
    if not inj:
        return {'pass': None, 'evaluable': False, 'reason': 'no measurable run'}
    if len(inj) < F3_MIN_RUNS:
        return {'pass': None, 'evaluable': False, 'reason': f'fewer than {F3_MIN_RUNS} measurable runs',
                'runs': len(inj)}
    eff = [v['alpha_star_eff'] for v in inj.values()]
    unrec = [k for k, v in inj.items() if v['alpha_star'] is None]
    must_recover = [k for k, v in inj.items() if v['template_rho_mean'] < RHO_ALLOWANCE_MAX]
    unrec_low_rho = [k for k in unrec if k in must_recover]
    med = float(np.median([e if e is not None else 0.2 for e in eff]))   # unrecovered counts as 0.2
    return {'pass': bool(not unrec_low_rho and med <= ALPHA_FAIL), 'evaluable': True,
            'median_alpha_star_eff': med, 'runs': len(inj), 'unrecovered_at_0.2': len(unrec),
            'unrecovered_with_low_template_rho': [run_label(*k) for k in unrec_low_rho],
            'median_alpha_star_raw': float(np.median([v['alpha_star'] if v['alpha_star'] is not None else 0.2
                                                      for v in inj.values()]))}


def evaluate(runs, measured, supports, manifest_path, files, radial_measured, synthetic,
             protocol_commit=None):
    keys = sorted((key, seed) for key in measured for seed in measured[key]['seeds'])
    configs = [('main', MAIN)] + list(VARIANTS.items()) + list(CONTRASTS.items())
    per_config = {name: {arm: summarise_all(measured, cfg, arm) for arm in ('lag1', 'unmapped', 'lag2', 'matched')}
                  for name, cfg in configs}
    per_config['main']['lag2_tri'] = summarise_all(measured, dict(MAIN, lag2='trilinear'), 'lag2')
    main = per_config['main']['lag1']

    def detected_set(res):
        return {k for k, r in res.items() if r['measurable'] and r['detected']}

    def measurable_set(res):
        return {k for k, r in res.items() if r['measurable']}

    meas = measurable_set(main)
    cond_meas = {key for key in measured if all((key, s) in meas for s in measured[key]['seeds'])}
    frac_by_cond = {run_label(key, 0)[:-6]: sum((key, s) in meas for s in measured[key]['seeds']) / 3.0
                    for key in measured}

    # F1 identity checks
    f1 = {'radialised_eligible_epochs': None, 'plummer_eligible_epochs': None, 'pass': None}
    if radial_measured is not None:
        rr = summarise_all(radial_measured, MAIN)
        f1['radialised_eligible_epochs'] = int(sum(v['eligible_epochs'] for v in rr.values()))
        f1['radialised_detections'] = int(sum(1 for v in rr.values() if v['measurable'] and v['detected']))
    if synthetic is not None:
        f1['plummer_eligible_epochs'] = synthetic['plummer']['eligible_epochs_total']
        f1['one_cell_eligible_epochs'] = synthetic['one_cell']['eligible_epochs_total']
    if f1['radialised_eligible_epochs'] is not None and f1['plummer_eligible_epochs'] is not None:
        f1['pass'] = bool(f1['radialised_eligible_epochs'] == 0 and f1['plummer_eligible_epochs'] == 0)

    # F2: exchangeable-by-construction controls (synthetic); recorded diagnostics reported only
    f2 = {'pass': None, 'controls': {},
          'rule': 'detections at or below the upper 95% binomial bound for a 5% rate on every '
                  'field control and the iid statistic control; size at most 0.10 on the AR(1) control'}
    if synthetic is not None:
        ok = True
        for name in ('white_noise', 'deposited_sphere', 'shared_drive_hetero_noise',
                     'shared_drive_hetero_amplitude', 'shared_drive_hetero_noise_mid',
                     'shared_drive_hetero_noise_low', 'single_seed_dipole_innocents',
                     'iid_columns_0.3', 'iid_columns_0.05', 'ar1_columns_0.3', 'ar1_columns_0.05'):
            c = synthetic.get(name)
            if c is None:
                ok = False
                f2['controls'][name] = 'missing'
                continue
            if name.startswith('ar1'):
                size = c['detections'] / c['runs']
                good = bool(size <= AR1_SIZE_MAX)
                f2['controls'][name] = {'detections': c['detections'], 'runs': c['runs'], 'size': size,
                                        'ceiling': AR1_SIZE_MAX, 'pass': good}
            else:
                n_pool = c.get('measurable', c['runs'])
                upper = binom_interval(n_pool, P_DETECT)[1] if n_pool else 0
                good = bool(c['detections'] <= upper)
                f2['controls'][name] = {'detections': c['detections'], 'runs': c['runs'], 'measurable': n_pool,
                                        'upper95': upper, 'pass': good}
            ok = ok and good
        f2['pass'] = bool(ok)
        f2['reported_sizes'] = {n: synthetic[n] for n in synthetic if n.startswith('ar1_columns_0.7')}
    fp = [(main[k]['B']['p'] < P_DETECT and main[k]['B']['S'] >= S_MIN,
           main[k]['C']['p'] < P_DETECT and main[k]['C']['S'] >= S_MIN) for k in meas]
    f2['recorded_stranger_as_own'] = {'fires': int(sum(a + b for a, b in fp)), 'tests': 2 * len(fp),
                                      'note': 'diagnostic only: the three column statistics share one matrix'}
    f2['recorded_strangers_not_exchangeable'] = int(sum(1 for k in meas if main[k]['D_signflip_p'] < 0.05))

    # F3 recovery
    inj = injection_sweep(runs, measured, MAIN, supports)
    f3 = f3_summary(inj)
    f3['alpha_star_by_run'] = {run_label(*k): {'alpha_star': v['alpha_star'], 'alpha_star_eff': v['alpha_star_eff'],
                                               'template_rho_mean': v['template_rho_mean'],
                                               'baseline_detected': v['baseline_detected']} for k, v in inj.items()}
    f3['fail_above'] = ALPHA_FAIL
    f3['rho_allowance_max'] = RHO_ALLOWANCE_MAX
    if synthetic is not None:
        f3['synthetic_ladders'] = {n: synthetic[n].get('injection_alpha_star') for n in
                                   ('white_noise', 'deposited_sphere', 'shared_drive') if n in synthetic}

    # F4 robustness: banded stability among runs measurable under both, with a tolerance of
    # max(1, ceil(F4_TOLERANCE * n_both)) violations, plus the F3 verdict recomputed on the
    # same run set under main and under the variant
    main_det = detected_set(main)
    f4 = {'rows': {}, 'pass': True, 'tolerance_rule': 'violations <= max(1, ceil(0.05 * runs measurable under both))'}
    for name in VARIANTS:
        res = per_config[name]['lag1']
        both = meas & measurable_set(res)
        broke_strong = sorted(run_label(*k) for k in both if k in main_det and main[k]['own']['p'] < P_STRONG
                              and not res[k]['detected'])
        broke_weak = sorted(run_label(*k) for k in both if k not in main_det and main[k]['own']['p'] > P_WEAK
                            and res[k]['detected'])
        allowed = max(1, int(math.ceil(F4_TOLERANCE * len(both))))
        inj_v = injection_sweep(runs, measured, VARIANTS[name], supports, keys=both)
        f3_v = f3_summary(inj_v)
        f3_m = f3_summary({k: v for k, v in inj.items() if k in both})
        row = {'measurable_runs': len(measurable_set(res)), 'measurable_both': len(both),
               'detected': sorted(run_label(*k) for k in detected_set(res)),
               'newly_undetected_strong': broke_strong, 'newly_detected_weak': broke_weak,
               'violations_allowed': allowed,
               'symmetric_difference_among_both': len({k for k in both if (k in main_det) != res[k]['detected']}),
               'f3_variant': {k2: v for k2, v in f3_v.items() if k2 in ('pass', 'evaluable', 'median_alpha_star_eff')},
               'f3_main_same_runs': {k2: v for k2, v in f3_m.items() if k2 in ('pass', 'evaluable', 'median_alpha_star_eff')}}
        stable = (len(broke_strong) + len(broke_weak)) <= allowed
        if f3_m['pass'] is not None and f3_v['pass'] is not None and f3_v['pass'] != f3_m['pass']:
            stable = False
        row['stable'] = bool(stable)
        f4['rows'][name] = row
        f4['pass'] = bool(f4['pass'] and stable)

    f5 = {'measurable_runs': len(meas), 'measurable_conditions': sorted(run_label(k, 0)[:-6] for k in cond_meas),
          'measurable_fraction_by_condition': frac_by_cond,
          'eligible_cell_epochs': int(sum(r['eligible_epochs'] for r in main.values())),
          'of_cell_epochs': len(keys) * (LAST_SCORED - FIRST_SCORED + 1),
          'pass': len(cond_meas) >= 3}

    manifest = check_manifest(files, manifest_path) if manifest_path else None
    inputs_ok = manifest is None or manifest['verified']
    verdict = {'F1_identity': f1, 'F2_false_positives': f2, 'F3_recovery': f3, 'F4_robustness': f4,
               'F5_support': f5, 'inputs_verified': bool(inputs_ok)}
    if not f5['pass']:
        verdict['result'] = 'insufficient support'
    elif not inputs_ok:
        verdict['result'] = 'inputs unverified'
    elif any(verdict[k]['pass'] is None for k in ('F1_identity', 'F2_false_positives', 'F3_recovery')):
        verdict['result'] = 'not evaluable'
    elif all(verdict[k]['pass'] for k in ('F1_identity', 'F2_false_positives', 'F3_recovery', 'F4_robustness')):
        verdict['result'] = 'qualified'
    else:
        verdict['result'] = 'not qualified'

    def run_out(k):
        key, seed = k
        i = measured[key]['seeds'].index(seed)
        rows = measured[key]['rows']
        strangers = [j for j in range(3) if j != i]
        o = {'condition': {'preset': key[0], 'selfgrav': key[1], 'gainloss': key[2]}, 'seed': seed,
             'tag': measured[key]['tags'][i], 'strangers': [measured[key]['seeds'][j] for j in strangers],
             'epochs': []}
        for idx, ep in enumerate(rows):
            c = ep['modes'][MAIN['support']]
            o['epochs'].append({
                'epoch': ep['epoch'], 'mass_b2': ep['mass_b2'][i], 'mass_b4': ep['mass_b4'][i],
                'eligible': main[k]['eligible_mask'][idx],
                'M_row': c['M'][i], 'M_col': [c['M'][l][i] for l in range(3)],
                'Q_own': (contrast(c['M'], i, i, MAIN['model'], MAIN['den_min'])
                          if all(v == v for r_ in c['M'] for v in r_) else float('nan')),
                'U_row': c['U'][i], 'M2_row': c['M2'][i], 'M2t_row': c['M2t'][i], 'MR_row': c['MR'][i],
                'c_shuf': c['c_shuf'][i], 'pr_cur': c['pr_cur'][i], 'pr_pred': c['pr_pred'][i],
                'relvar_cur': c['relvar_cur'][i], 'relvar_pred': c['relvar_pred'][i],
                'tmpl_xcorr': [c['tmpl_xcorr'][i][j] for j in strangers],
                'xseed_now': [c['xseed_now'][i][j] for j in strangers],
                'xseed_raw': [ep['xseed_raw'][i][j] for j in strangers],
                'radial_overlap': c['radial_overlap'][i],
                'orientation': c.get('orientation', [None] * 3)[i],
                'M_row_no_removal': ep['modes']['none']['M'][i]})
        for arm in ('lag1', 'unmapped', 'lag2', 'lag2_tri', 'matched'):
            o[arm] = {k2: v for k2, v in per_config['main'][arm][k].items() if k2 != 'eligible_mask'}
        o['contrasts'] = {name: {k2: v for k2, v in per_config[name]['lag1'][k].items()
                                 if k2 in ('measurable', 'eligible_epochs', 'own', 'detected', 'mean_c_own',
                                           'mean_c_stranger')} for name in CONTRASTS}
        if k in inj:
            o['injection'] = inj[k]
        return o

    return {
        'schema': SCHEMA_OUT, 'author': 'Aldrin Payopay',
        'protocol': 'docs/halo/2026-09-05_memory_estimator_qualification_protocol.md',
        'protocol_commit': protocol_commit,
        'measured_at': datetime.now(timezone.utc).isoformat(),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__,
                    'platform': platform.platform(), 'host_byteorder': sys.byteorder},
        'script_sha256': sha256_file(os.path.abspath(__file__)),
        'config_main': MAIN, 'variants': VARIANTS, 'alphas': ALPHAS, 'alpha_fail': ALPHA_FAIL,
        's_min': S_MIN, 'p_detect': P_DETECT, 'p_strong': P_STRONG, 'p_weak': P_WEAK,
        'ar1_size_max': AR1_SIZE_MAX, 'autocorr_caveat': AUTOCORR_CAVEAT, 'f4_tolerance': F4_TOLERANCE,
        'rho_allowance_max': RHO_ALLOWANCE_MAX, 'f3_min_runs': F3_MIN_RUNS, 'contrasts_reported': list(CONTRASTS),
        'protocol_sha256': protocol_sha256(),
        'n_perm': N_PERM, 'n_boot': N_BOOT, 'block': BLOCK, 'boot_min_epochs': BOOT_MIN_EPOCHS,
        'perm_seed': PERM_SEED, 'shuffle_seed': SHUFFLE_SEED,
        'scored_epochs': [FIRST_SCORED, LAST_SCORED],
        'null_means': 'undefined correlation (zero residual variance) or diagnostic not computed',
        'inputs': {'runs': len(keys), 'conditions': len(measured), 'files': files, 'manifest_check': manifest},
        'verdict': verdict,
        'detected_runs_main': sorted(run_label(*k) for k in main_det),
        'below_floor_runs_main': sorted(run_label(*k) for k in meas if main[k].get('below_floor')),
        'measurable_runs_main': sorted(run_label(*k) for k in meas),
        'runs': [run_out(k) for k in keys],
        'condition_detected_counts': {run_label(key, 0)[:-6]: sum((key, s) in main_det for s in measured[key]['seeds'])
                                      for key in measured},
        'synthetic': synthetic,
    }


# ------------------------------------------------------------------ synthetic

_IDX = np.arange(N) - CENTRE
_R = np.sqrt(_IDX[:, None, None] ** 2 + _IDX[None, :, None] ** 2 + _IDX[None, None, :] ** 2)
_Z, _Y, _X = np.meshgrid(_IDX, _IDX, _IDX, indexing='ij')


def plummer_centre(a=4.0):
    return (1 + (_R / a) ** 2) ** -2.5


_PCI_CACHE = {}


def plummer_cell_integrated(a=4.0, sub_n=4):
    """mean of the Plummer density over each cell, sub_n^3 midpoint samples (cached)."""
    if (a, sub_n) in _PCI_CACHE:
        return _PCI_CACHE[(a, sub_n)]
    off = (np.arange(sub_n) + 0.5) / sub_n - 0.5
    acc = np.zeros((N, N, N))
    for dz in off:
        for dy in off:
            for dx in off:
                r = np.sqrt((_Z + dz) ** 2 + (_Y + dy) ** 2 + (_X + dx) ** 2)
                acc += (1 + (r / a) ** 2) ** -2.5
    _PCI_CACHE[(a, sub_n)] = acc / sub_n ** 3
    return _PCI_CACHE[(a, sub_n)]


def deposited_sphere(rng, a=4.0, particles=PARTICLES, angular=None):
    """a static sphere seen through a nearest-cell deposit of `particles` particles:
    independent Poisson counts per cell around the cell-integrated density, in the
    recorded units of particles/1024. `angular` multiplies the expected density."""
    lam = plummer_cell_integrated(a)
    if angular is not None:
        lam = lam * angular
    lam = lam / lam.sum() * particles
    return rng.poisson(lam).astype(np.float64) / 1024.0


DRIVE_NOISE = 0.9   # shared-drive family: keeps the coarse templates' cross-correlation near 0.8, inside E3


def quadrupole():
    return (_X * _Y) / np.maximum(_R, 1.0) ** 2 * 3.0


def synth_grid(kind, rng, n_conditions=1, epochs=LAST_SCORED):
    """three seeds x epochs of 32^3 positive fields, no particles, no GPU."""
    plum = plummer_centre(4.0)
    runs = {}
    for c in range(n_conditions):
        key = (kind, float(c), 0.0)
        seeds = []
        common = plum * (1.0 + 0.5 * quadrupole())
        dipoles = []
        for s in range(3):
            fields = []
            if kind == 'plummer':
                fields = [plum.copy() for _ in range(epochs)]
            elif kind == 'one_cell':
                f0 = np.zeros((N, N, N)); f0[15, 15, 15] = 1.0
                fields = [f0.copy() for _ in range(epochs)]
            elif kind == 'white_noise':
                fields = [np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'perfect_relic':
                f = np.abs(rng.standard_normal((N, N, N)))
                fields.append(f)
                for _ in range(epochs - 1):
                    nxt = np.abs(rng.standard_normal((N, N, N)))
                    p = predicted(fields[-1], 2)
                    nxt[np.ix_(B2, B2, B2)] = p / p.mean() + 0.3 * np.abs(rng.standard_normal((16, 16, 16)))
                    fields.append(nxt)
            elif kind == 'shared_drive':
                fields = [common + DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'shared_drive_hetero_noise':
                mult = (0.7, 1.0, 1.4)[s]
                fields = [common + mult * DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'shared_drive_hetero_noise_low':
                # the straddle regime the second review found: a four-fold noise spread at a
                # drive level that puts the noisiest seed's own correlation near 0.07
                mult = (0.5, 1.0, 2.0)[s]
                fields = [common + mult * 1.6 * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'shared_drive_hetero_noise_mid':
                # a three-fold noise spread at the same drive level: the boundary the quality
                # gate is set at
                mult = (0.577, 1.0, 1.732)[s]
                fields = [common + mult * 1.2 * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'single_seed_dipole':
                # one guilty seed carries a persistent dipole on the shared drive; the two
                # innocent seeds must not be detected through the matrix
                if s == 1:
                    d = np.array([0.6, 0.8, 0.0])
                    cosang = (d[0] * _X + d[1] * _Y + d[2] * _Z) / np.maximum(_R, 1.0)
                    base = common * (1.0 + 0.6 * cosang)
                else:
                    base = common
                fields = [base + DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'shared_drive_breathing_phase':
                # a shared amplitude that breathes in time with a seed-specific phase: nothing
                # persists in the lab frame, yet the seed-specific parameter is remembered
                phase = (0.0, 2 * math.pi / 3, 4 * math.pi / 3)[s]
                fields = [plum * (1.0 + 0.5 * (1.0 + 0.8 * math.sin(2 * math.pi * k / 16.0 + phase)) * quadrupole())
                          + DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N))) for k in range(epochs)]
            elif kind == 'shared_drive_rotating_offset':
                # a shared pattern co-rotating about z at 5 degrees per epoch with a seed-specific
                # phase offset of 0, 30, 60 degrees
                off = (0.0, 30.0, 60.0)[s]
                fields = []
                for k in range(epochs):
                    ang = math.radians(5.0 * k + off)
                    xr = _X * math.cos(ang) - _Y * math.sin(ang)
                    yr = _X * math.sin(ang) + _Y * math.cos(ang)
                    quad = (xr * yr) / np.maximum(_R, 1.0) ** 2 * 3.0
                    fields.append(plum * (1.0 + 0.5 * quad) + DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N))))
            elif kind == 'shared_drive_hetero_amplitude':
                mult = (0.7, 1.0, 1.4)[s]
                fields = [plum * (1.0 + mult * 0.5 * quadrupole()) + DRIVE_NOISE * plum * np.abs(rng.standard_normal((N, N, N)))
                          for _ in range(epochs)]
            elif kind == 'shared_drive_hetero_scale':
                a = (3.0, 4.0, 5.0)[s]
                env = plummer_centre(a)
                fields = [env * (1.0 + 0.5 * quadrupole()) + DRIVE_NOISE * env * np.abs(rng.standard_normal((N, N, N)))
                          for _ in range(epochs)]
            elif kind == 'persistent_dipole':
                # one fixed direction per seed, kept at least 60 degrees from the others so the
                # E3 template gate is not tripped by a chance alignment
                while True:
                    d = rng.standard_normal(3); d /= np.linalg.norm(d)
                    if all(abs(float(d @ prev)) <= 0.5 for prev in dipoles):
                        break
                dipoles.append(d)
                cosang = (d[0] * _X + d[1] * _Y + d[2] * _Z) / np.maximum(_R, 1.0)
                base = plum * (1.0 + 0.6 * cosang)
                fields = [base + 0.3 * plum * np.abs(rng.standard_normal((N, N, N))) for _ in range(epochs)]
            elif kind == 'deposited_sphere':
                fields = [deposited_sphere(rng, 4.0) for _ in range(epochs)]
            else:
                raise ValueError(kind)
            seeds.append({'seed': s, 'tag': f'{kind}_c{c}_s{s}', 'mesh': np.stack(fields).astype(np.float32),
                          'particles': 0})
        runs[key] = seeds
    return runs


def ar1_columns_control(rng, n_runs=1000, phi=0.5, sigma=0.07, n_epochs=22, mu=0.3):
    """statistic-level control: 3x3 matrices whose nine entries are independent AR(1)
    series in time with exchangeable columns and no diagonal effect. Measures the size
    of the block-relabelling test with the full detection rule and with p alone."""
    det_full = det_p = 0
    for _ in range(n_runs):
        eps = rng.standard_normal((n_epochs, 3, 3)) * sigma * math.sqrt(1 - phi ** 2)
        M = np.zeros((n_epochs, 3, 3))
        M[0] = rng.standard_normal((3, 3)) * sigma
        for t in range(1, n_epochs):
            M[t] = phi * M[t - 1] + eps[t]
        M += mu
        Q = np.array([[contrast(M[t].tolist(), 0, c, MAIN['model'], MAIN['den_min']) for c in (0, 1, 2)]
                      for t in range(n_epochs)])
        test = block_relabel_test(Q, np.random.default_rng(PERM_SEED))['own']
        det_p += test['p'] < P_DETECT
        det_full += test['p'] < P_DETECT and test['S'] >= S_MIN
    return {'runs': n_runs, 'phi': phi, 'sigma': sigma, 'mu': mu, 'detections': int(det_full),
            'detections_p_only': int(det_p), 'interval95': binom_interval(n_runs, P_DETECT)}


def run_synthetic(supports):
    rng = np.random.default_rng(20260905)
    out = {}
    plan = [('plummer', 1), ('one_cell', 1), ('white_noise', 40), ('perfect_relic', 3),
            ('shared_drive', 3), ('persistent_dipole', 3), ('deposited_sphere', 10),
            ('shared_drive_hetero_noise', 30), ('shared_drive_hetero_amplitude', 30),
            ('shared_drive_hetero_noise_low', 30), ('shared_drive_hetero_noise_mid', 30), ('single_seed_dipole', 12),
            ('shared_drive_hetero_scale', 3), ('shared_drive_breathing_phase', 3),
            ('shared_drive_rotating_offset', 3)]
    for kind, n_cond in plan:
        runs = synth_grid(kind, rng, n_cond)
        measured = measure_grid(runs, supports, with_orientation=False, label=kind)
        summ = summarise_all(measured, MAIN)
        summ_u = summarise_all(measured, MAIN, 'unmapped')
        n_runs = len(summ)
        meas = [v for v in summ.values() if v['measurable']]
        det = int(sum(1 for v in meas if v['detected']))
        rec = {'runs': n_runs, 'measurable': len(meas), 'eligible_epochs_total': int(sum(v['eligible_epochs'] for v in summ.values())),
               'detections': det, 'interval95': binom_interval(len(meas), P_DETECT) if meas else [0, 0],
               'mean_S': float(np.mean([v['own']['S'] for v in meas])) if meas else None,
               'mean_uncentred_excess': float(np.mean([v['uncentred_excess'] for v in meas])) if meas else None,
               'mean_c_own': float(np.mean([v['mean_c_own'] for v in meas])) if meas else None,
               'mean_c_stranger': float(np.mean([v['mean_c_stranger'] for v in meas])) if meas else None,
               'strangers_not_exchangeable': int(sum(1 for v in meas if v['D_signflip_p'] < 0.05)),
               'stranger_as_own_fires': int(sum((v['B']['p'] < P_DETECT and v['B']['S'] >= S_MIN)
                                               + (v['C']['p'] < P_DETECT and v['C']['S'] >= S_MIN) for v in meas)),
               'gate_fail_counts': {g: int(sum(v['gate_fail_counts'][g] for v in summ.values())) for g in ('e1', 'e2', 'e3', 'e4')},
               'e5_collapsed_runs': int(sum(1 for v in summ.values() if v['e5_collapse'])),
               'e5_unbalanced_runs': int(sum(1 for v in summ.values() if v['e5_unbalanced'])),
               'multiplicative_weight_mean': float(np.mean([v['multiplicative_weight_mean'] for v in meas])) if meas else None,
               'unmapped_detections': int(sum(1 for v in summ_u.values() if v['measurable'] and v['detected'])),
               'unmapped_mean_S': float(np.mean([v['own']['S'] for v in summ_u.values() if v['measurable']]))
               if any(v['measurable'] for v in summ_u.values()) else None}
        if kind in ('white_noise', 'deposited_sphere', 'shared_drive'):
            sub_keys = {k for k in summ if k[0] in sorted(runs)[:3]}
            inj = injection_sweep(runs, measured, MAIN, supports, keys=sub_keys)
            rec['injection_alpha_star'] = [v['alpha_star'] for v in inj.values()]
            rec['injection_alpha_star_eff'] = [v['alpha_star_eff'] for v in inj.values()]
            rec['injection_template_rho'] = [v['template_rho_mean'] for v in inj.values()]
        if kind == 'single_seed_dipole':
            guilty = [v for (key, seed), v in summ.items() if seed == 1]
            innocent = [v for (key, seed), v in summ.items() if seed != 1]
            out['single_seed_dipole_guilty'] = {'runs': len(guilty), 'measurable': sum(v['measurable'] for v in guilty),
                                                'detections': sum(1 for v in guilty if v['measurable'] and v['detected'])}
            n_inn = sum(v['measurable'] for v in innocent)
            out['single_seed_dipole_innocents'] = {'runs': len(innocent), 'measurable': n_inn,
                                                   'detections': sum(1 for v in innocent if v['measurable'] and v['detected']),
                                                   'interval95': binom_interval(n_inn, P_DETECT) if n_inn else [0, 0],
                                                   'mean_S': float(np.mean([v['own']['S'] for v in innocent if v['measurable']]))
                                                   if any(v['measurable'] for v in innocent) else None}
        out[kind] = rec
        print(f'  {kind:30s} runs={n_runs:3d} measurable={len(meas):3d} detected={det:3d} band={rec["interval95"]} '
              f'S={rec["mean_S"]} unc={rec["mean_uncentred_excess"]}', file=sys.stderr)
    for phi in (0.0, 0.5, 0.7):
        for mu in (0.3, 0.05):
            rec = ar1_columns_control(rng, phi=phi, mu=mu)
            name = ('iid_columns' if phi == 0.0 else f'ar1_columns') + (f'_{phi}' if phi == 0.7 else '') + f'_{mu}'
            if phi == 0.7:
                name = f'ar1_columns_0.7_{mu}'
            out[name] = rec
            print(f'  {name}: detections {rec["detections"]} (p-only {rec["detections_p_only"]}) of {rec["runs"]} '
                  f'band {rec["interval95"]}', file=sys.stderr)
    return out


# ------------------------------------------------------------------ figure

def make_figure(res, out_png):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    runs = res['runs']
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    conds = sorted({(r['condition']['preset'], r['condition']['selfgrav'], r['condition']['gainloss']) for r in runs})
    labels = [f"{c[0][:4]} sg{c[1]:g} gl{c[2]:g}" for c in conds]
    elig = [sum(r['lag1']['eligible_epochs'] for r in runs
                if (r['condition']['preset'], r['condition']['selfgrav'], r['condition']['gainloss']) == c) for c in conds]
    ax = axes[0]
    ax.barh(range(len(conds)), elig, color=['#2a7' if e >= 27 else '#bbb' for e in elig])
    ax.set_yticks(range(len(conds))); ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel('eligible cell-epochs of 66 (3 seeds x 22)')
    ax.set_title('(a) where the estimator can measure', fontsize=10)
    ax = axes[1]
    meas = [r for r in runs if r['lag1']['measurable']]
    for i, r in enumerate(meas):
        s = r['lag1']['own']['S']; ci = r['lag1'].get('S_ci95_block_bootstrap')
        col = '#c33' if r['lag1']['detected'] else ('#e9a' if r['lag1'].get('below_floor') else '#468')
        if ci:
            ax.errorbar(s, i, xerr=[[s - ci[0]], [ci[1] - s]], fmt='o', color=col, ms=4, capsize=2)
        else:
            ax.plot(s, i, 'o', color=col, ms=4)
    ax.axvline(0, color='k', lw=0.6); ax.axvline(res.get('s_min', 0.02), color='#c33', lw=0.6, ls=':')
    ax.set_yticks(range(len(meas)))
    ax.set_yticklabels([f"{r['condition']['preset'][:4]} sg{r['condition']['selfgrav']:g} gl{r['condition']['gainloss']:g} s{r['seed']}"
                        for r in meas], fontsize=7)
    ax.set_xlabel('S: own-relic contrast, doubly centred (block bootstrap where n >= 12)')
    ax.set_title('(b) own relic against strangers; red = detected, pink = below floor', fontsize=10)
    ax = axes[2]
    for r in meas:
        if 'injection' not in r:
            continue
        a = [c['alpha'] for c in r['injection']['curve']]; s = [c['S'] for c in r['injection']['curve']]
        ax.plot([max(x, 1e-3) for x in a], s, '-o', ms=3, lw=1, alpha=0.8)
    ax.axhline(res.get('s_min', 0.02), color='#c33', lw=0.6, ls=':')
    ax.set_xscale('log'); ax.set_xlabel('injected fraction of block mass (0 drawn at 1e-3)')
    ax.set_ylabel('S'); ax.set_title('(c) recovery of an injected passive relic', fontsize=10)
    fig.suptitle('Replacement memory estimator: eligibility, own-relic contrast, injection recovery', fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    print(f'wrote {out_png}')


# ------------------------------------------------------------------ main

def jsonable(o):
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, np.floating):
        return jsonable(float(o))
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    return o


def build_supports():
    return {mode: (Support(B2, mode), Support(B4, mode)) for mode in SUPPORT_MODES}


PROTOCOL_PATH = 'docs/halo/2026-09-05_memory_estimator_qualification_protocol.md'


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def protocol_sha256():
    path = os.path.join(repo_root(), PROTOCOL_PATH)
    return sha256_file(path) if os.path.exists(path) else None


def commit_holds_protocol(commit):
    """True when `commit` contains the protocol file with the same content as on disk and
    the script with the same content as the running one."""
    try:
        for rel, local in ((PROTOCOL_PATH, os.path.join(repo_root(), PROTOCOL_PATH)),
                           (os.path.relpath(os.path.abspath(__file__), repo_root()), os.path.abspath(__file__))):
            blob = subprocess.run(['git', '-C', repo_root(), 'rev-parse', f'{commit}:{rel}'],
                                  capture_output=True, text=True, check=True).stdout.strip()
            here = subprocess.run(['git', '-C', repo_root(), 'hash-object', local],
                                  capture_output=True, text=True, check=True).stdout.strip()
            if blob != here:
                return False
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def git_head(path):
    try:
        return subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(path)), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--synthetic', action='store_true')
    ap.add_argument('--input-dir')
    ap.add_argument('--manifest')
    ap.add_argument('--output')
    ap.add_argument('--synthetic-json', help='the synthetic receipt written by --synthetic; required with --input-dir')
    ap.add_argument('--protocol-commit', help='commit that froze the protocol (default: git HEAD of this script)')
    ap.add_argument('--figure', nargs=2, metavar=('IN_JSON', 'OUT_PNG'))
    args = ap.parse_args()
    t0 = time.time()
    if args.figure:
        with open(args.figure[0]) as fh:
            make_figure(json.load(fh), args.figure[1])
        return
    supports = build_supports()
    script_sha = sha256_file(os.path.abspath(__file__))
    if args.synthetic and not args.input_dir:
        syn = run_synthetic(supports)
        out = {'schema': SCHEMA_OUT + '/synthetic', 'author': 'Aldrin Payopay',
               'measured_at': datetime.now(timezone.utc).isoformat(), 'script_sha256': script_sha,
               'protocol_sha256': protocol_sha256(),
               'config_main': MAIN, 's_min': S_MIN, 'p_detect': P_DETECT, 'block': BLOCK,
               'synthetic': syn, 'seconds': time.time() - t0}
        dst = args.output or 'synthetic.json'
        with open(dst, 'w') as fh:
            json.dump(jsonable(out), fh, indent=1, allow_nan=False)
        print(f'wrote {dst} in {time.time() - t0:.0f}s')
        return
    if not args.input_dir:
        ap.error('--input-dir, --synthetic or --figure required')
    if not args.synthetic_json:
        ap.error('--synthetic-json is required with --input-dir (protocol section 10)')
    if not args.manifest:
        ap.error('--manifest is required with --input-dir (protocol section 2)')
    with open(args.synthetic_json) as fh:
        syn_doc = json.load(fh)
    if syn_doc.get('script_sha256') != script_sha:
        sys.exit(f'refusing: the synthetic receipt was written by script sha {syn_doc.get("script_sha256")}, '
                 f'this script is {script_sha}')
    if syn_doc.get('protocol_sha256') != protocol_sha256():
        sys.exit('refusing: the protocol text differs from the one the synthetic receipt was written under')
    commit = args.protocol_commit or git_head(__file__)
    if not commit or not commit_holds_protocol(commit):
        sys.exit(f'refusing: commit {commit} does not hold this protocol and script; freeze first '
                 f'(protocol section 10)')
    syn = syn_doc['synthetic']
    runs, files = load_grid(args.input_dir)
    print(f'loaded {sum(len(v) for v in runs.values())} runs in {len(runs)} conditions ({time.time() - t0:.0f}s)',
          file=sys.stderr)
    measured = measure_grid(runs, supports, with_orientation=True, label='grid')
    radial = measure_grid(runs, supports, with_orientation=False, radialised=True, label='radialised')
    result = evaluate(runs, measured, supports, args.manifest, files, radial, syn, commit)
    result['seconds'] = time.time() - t0
    dst = args.output or 'qualification.json'
    with open(dst, 'w') as fh:
        json.dump(jsonable(result), fh, indent=1, allow_nan=False)
    v = result['verdict']
    print(f'wrote {dst} in {time.time() - t0:.0f}s')
    print(f"result: {v['result']} | measurable runs {v['F5_support']['measurable_runs']}/{len(result['runs'])} | "
          f"conditions {len(v['F5_support']['measurable_conditions'])} | detected {len(result['detected_runs_main'])} | "
          f"below floor {len(result['below_floor_runs_main'])}")
    print('F1', v['F1_identity']['pass'], 'F2', v['F2_false_positives']['pass'], 'F3', v['F3_recovery'].get('pass'),
          v['F3_recovery'].get('median_alpha_star'), 'F4', v['F4_robustness']['pass'], 'F5', v['F5_support']['pass'])


if __name__ == '__main__':
    main()
