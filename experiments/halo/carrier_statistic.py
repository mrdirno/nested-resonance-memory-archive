#!/usr/bin/env python3
"""carrier_statistic.py - a within-run carrier statistic for the HALO chamber, its own synthetic
receipt, and the scoring and decision rule of the fresh runs registered with it.

Ring 32 (analysis/2026-09-24_within_run_carrier_statistic.md). Ring 30's registered
intervention read the frozen scorer (experiments/halo/memory_estimator_qualify.py, 7619ef6b)
in two frames of each run and returned NOT DECIDABLE with a silent positive control. The frozen
contrast compares a run's own relic with a null predicted from its two strangers, so its frame
difference depends on how a triple's hemispheres line up (Ring 30 pre-registration, control item
6). This statistic is read inside one run and takes no other run as input.

  pair k        1-based current epoch k = 3..24 (the frozen scorer's 22 lag-one pairs, kept for
                comparability): current C = mesh k-1, relic R = mesh k-2 (0-based mesh indices).
  fields        c = the current's inner 16^3 block B2 (cells 8..23); p = the x2 relic
                prediction (2x2x2 block sum), both from the frozen scorer, then its orbit
                residual (the frozen main support).
  odd part      odd(f) = (f - Pf) / 2, P the point inversion of the 16^3 block
                (f[::-1, ::-1, ::-1]); P maps every support the scorer has to itself, so the
                residual changes only the even part and odd(residual(f)) = odd(f).
  rho_k         <odd(c), odd(p)> / (|odd(c)| |odd(p)|).
  eligible      the frozen scorer's own-field gates only: E1 (current mass in B2 >= 1%), E2 for
                the current and the OWN prediction (participation >= 8, residual variance >= 1e-9
                of the block's), E2 on the two odd parts (participation >= 8), and rho_k finite.
                No stranger enters: E3, E5 and E5b are gates on the triple and are not used.
  T             mean of rho_k over the eligible pairs; n their number; unscored if n < 12.
  p             the exact two-sided sign-flip p over all 2^n sign vectors.
  call          L if T > 0 and p < 0.05; Pi if T < 0 and p < 0.05; none otherwise.

Ring 30's inverted frame (memory_intervention_frames.py: D_j = P^j C_j) inverts exactly one
member of every lag-one pair, so rho_k and T change sign and nothing else changes: the
within-run frame preference IS the call on the lab frame.

The null is the random-frame model: each mesh inverted or not by jointly independent fair coins,
independent of the run. Under it the pair signs are independent fair coins and the per-pair
sign-flip test is exact given the |rho_k|. A call reads "the lab-frame lag-one orientation
products are not fair coins", with its direction from the sign of T. The null does not test a
point-odd structure pinned to the lab; the positive control and the between-run pinning
diagnostic do.

Modes
  receipt --design-commit C --control DIR [--control DIR] --json OUT   the receipt (G1-G5)
  score ARM_DIR --arm NAME --receipt RECEIPT --json OUT                T for the nine runs
  decide --prereg-commit R --arm NAME SCORE [--arm ...] --json OUT     V1 and the branch

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse
import itertools
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import memory_estimator_qualify as mq          # noqa: E402  frozen, imported, never edited
import memory_intervention_frames as mf        # noqa: E402  Ring 30's inverted frame

SCHEMA_RECEIPT = 'halo-carrier-receipt/1'
SCHEMA_SCORE = 'halo-carrier-score/1'
SCHEMA_DECISION = 'halo-carrier-decision/1'
SCRIPT_REL = 'experiments/halo/carrier_statistic.py'
PREREG_REL = 'analysis/2026-09-24_within_run_carrier_statistic.md'

MIN_PAIRS = mq.MAIN['min_epochs']              # 12
P_CALL = mq.P_DETECT                           # 0.05
TIE_ABS = 1e-12                                # ties: |sum s rho| >= |sum rho| - 1e-12 * sum |rho|
EXACT_TOL = 1e-12                              # G1
RECEIPT_SEED = 20260924
N_NULL_DRAWS = 200                             # G2 draws per control run
N_INJ_DRAWS = 20                               # G4 draws per control run
N_SHUFFLE_DRAWS = 50                           # reported lag-specificity draws per control run
ALPHAS = list(mq.ALPHAS)                       # 0 .. 0.2, the frozen F3 grid
ALPHA_FAIL = mq.ALPHA_FAIL                     # 0.10
RECOVER_AT_MAX = 0.95                          # G4: share of a run's kept draws recovered at 0.2
LICENSE_MIN_PI = 4                             # CONFIRMED needs at least this many Pi calls
STATIC_A3 = 0.999                              # a run whose median lag-one full-field Pearson reaches this is static
RECEIPT_REL = 'data/results/halo/carrier_statistic/receipt.json'
LEDGER_REL = 'data/results/halo/memory_carrier_launches.tsv'

S2 = mq.Support(mq.B2, mq.MAIN['support'])     # the frozen main support (cube orbits)

# the fresh runs: nine seeds, three per condition, the first five significant digits of sqrt(n)
# for the first nine non-square n >= 2; the decided arm a CONFIRMED would license takes the next nine
REGISTERED = {0.3: (14142, 17320, 22360), 0.32: (24494, 26457, 28284), 0.35: (31622, 33166, 34641)}
DECIDED_ARM_SEEDS = {0.3: (36055, 37416, 38729), 0.32: (41231, 42426, 43588), 0.35: (44721, 45825, 46904)}
CANARY = (0.32, 777, 'ce15f08155e34fff22c234a802ef1784549c8bf3e6af1e282d72beb946e34177')  # Ring 29's mesh
CLOSING = (0.3, 14142)
HARNESS_SHA = 'f2f30d79854bb0161b14ed84b6c919b2b763727ebcbd9b2c865572c91ce79652'
RUNTIME_PINS = {'browser': '151.0.7922.34', 'playwright': '1.62.1', 'node': 'v24.4.1'}
RENDERER = 'ANGLE (Apple, ANGLE Metal Renderer: Apple M4 Pro, Unspecified Version)'
MESH0_BYTES = 32 ** 3 * 4
DIRS = {'identity': 'memory_carrier_identity', 'invert_all': 'memory_carrier_invert_all',
        'canary': 'memory_carrier_canary', 'close': 'memory_carrier_identity_close'}


# ------------------------------------------------------------------ the statistic

def odd16(f):
    f = np.asarray(f, dtype=np.float64).reshape(16, 16, 16)
    return 0.5 * (f - f[::-1, ::-1, ::-1])


def pair_value(cur, relic):
    """one lag-one pair: eligibility inputs (own fields only) and rho."""
    cur = np.asarray(cur)
    total = float(cur.astype(np.float64).sum())
    c = mq.sub(cur, mq.B2)
    p = mq.predicted(relic, 2)
    rc, rp = S2.residual(c), S2.residual(p)
    e1 = (float(c.sum()) / total if total > 0 else 0.0) >= mq.MAIN['e1_mass']
    e2 = (mq.participation(rc) >= mq.MAIN['e2_pr'] and mq.relvar(rc, c) >= mq.MAIN['e2_relvar']
          and mq.participation(rp) >= mq.MAIN['e2_pr'] and mq.relvar(rp, p) >= mq.MAIN['e2_relvar'])
    oc, op = odd16(rc), odd16(rp)
    e2odd = mq.participation(oc) >= mq.MAIN['e2_pr'] and mq.participation(op) >= mq.MAIN['e2_pr']
    nc, npr = float(np.sqrt((oc * oc).sum())), float(np.sqrt((op * op).sum()))
    rho = float((oc * op).sum() / (nc * npr)) if nc > 0 and npr > 0 else float('nan')
    e4 = math.isfinite(rho)
    vc, vp = float((rc * rc).sum()), float((rp * rp).sum())
    return {'e1': bool(e1), 'e2': bool(e2), 'e2odd': bool(e2odd), 'e4': bool(e4),
            'eligible': bool(e1 and e2 and e2odd and e4), 'rho': rho,
            'odd_share_cur': nc * nc / vc if vc > 0 else float('nan'),
            'odd_share_pred': npr * npr / vp if vp > 0 else float('nan')}


def run_pairs(mesh, cur_override=None):
    """the 22 lag-one pairs of one run. cur_override: {k: 32^3 current} replacing mesh k-1."""
    out = []
    for k in range(mq.FIRST_SCORED, mq.LAST_SCORED + 1):
        cur = mesh[k - 1] if cur_override is None or k not in cur_override else cur_override[k]
        v = pair_value(cur, mesh[k - 2])
        v['k'] = k
        out.append(v)
    return out


def _all_sums(v):
    s = np.zeros(1)
    for a in v:
        s = np.concatenate([s + a, s - a])
    return s


def signflip_p(x):
    """exact two-sided sign-flip p of mean(x) = 0 over all 2^n sign vectors (n <= 24), by
    meet-in-the-middle; p = 1 when the sum is zero."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n == 0:
        return float('nan')
    if n > 24:
        raise ValueError(f'{n} pairs: the exact enumeration is written for n <= 24')
    thr = abs(float(x.sum())) - TIE_ABS * float(np.abs(x).sum())
    if not thr > 0:
        return 1.0
    h = n // 2
    A = _all_sums(x[:h])
    B = np.sort(_all_sums(x[h:]))
    hi = B.size - np.searchsorted(B, thr - A, side='left')      # A_i + B_j >= thr
    lo = np.searchsorted(B, -thr - A, side='right')             # A_i + B_j <= -thr
    return float(int(hi.sum()) + int(lo.sum())) / float(2 ** n)


def direct_p(x):
    """the same p by direct enumeration of every sign vector (the G2b cross-check)."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    thr = abs(float(x.sum())) - TIE_ABS * float(np.abs(x).sum())
    if not thr > 0:
        return 1.0
    hits = 0
    blk = min(n, 12)
    head = np.array(list(itertools.product((1.0, -1.0), repeat=blk)))       # 2^blk x blk
    tail_sums = _all_sums(x[blk:]) if n > blk else np.zeros(1)
    hs = head @ x[:blk]
    for t in tail_sums:
        hits += int((np.abs(hs + t) >= thr).sum())
    return hits / float(2 ** n)


def call_of(T, p, n):
    if n < MIN_PAIRS:
        return 'unscored'
    if p < P_CALL and T > 0:
        return 'L'
    if p < P_CALL and T < 0:
        return 'Pi'
    return 'none'


def statistic(pairs, mask=None):
    """T, n, p and the call from a run's pairs; mask fixes the eligible set (G4)."""
    el = [pr['eligible'] for pr in pairs] if mask is None else list(mask)
    if len(el) != len(pairs):
        raise ValueError(f'mask of {len(el)} for {len(pairs)} pairs')
    x = [pr['rho'] for pr, ok in zip(pairs, el) if ok]
    n = len(x)
    T = float(np.mean(x)) if n else float('nan')
    p = signflip_p(x) if n >= MIN_PAIRS else None
    ax = np.abs(np.asarray(x)) if n else np.zeros(0)
    neff = float(ax.sum() ** 2 / (ax ** 2).sum()) if n and (ax ** 2).sum() > 0 else float('nan')
    top3 = float(np.sort(ax)[::-1][:3].sum() / ax.sum()) if n and ax.sum() > 0 else float('nan')
    return {'T': T, 'n': n, 'p': p, 'call': call_of(T, 1.0 if p is None else p, n),
            'n_eff': neff, 'top3_share': top3, 'eligible_mask': [bool(e) for e in el]}


def a3_static(mesh):
    """median over the 22 lag-one pairs of the full-field Pearson of mesh k-1 with mesh k-2, in the
    lab frame and in the inverted frame; the larger one. A static field reaches about 1 in the
    frame that undoes the interventions (Ring 22: 0.99995-0.99999); this support's runs sit near 0.1."""
    out = []
    for m in (mesh, mf.derive(mesh, 'point')):
        out.append(float(np.median([mq.pearson(m[k - 1], m[k - 2]) for k in range(mq.FIRST_SCORED, mq.LAST_SCORED + 1)])))
    return max(out)


def binom_band(n, p=P_CALL):
    """the 2.5% and 97.5% quantiles of Binomial(n, p), computed as the frozen binom_interval
    computes them but in log space: the frozen one overflows a float above n = 1,029."""
    i = np.arange(n + 1)
    lp = (math.lgamma(n + 1) - np.array([math.lgamma(k + 1) + math.lgamma(n - k + 1) for k in i])
          + i * math.log(p) + (n - i) * math.log1p(-p))
    cum = np.cumsum(np.exp(lp))
    return [int(np.searchsorted(cum, 0.025)), int(np.searchsorted(cum, 0.975))]


def invert_mesh(m):
    return np.ascontiguousarray(np.asarray(m)[::-1, ::-1, ::-1])


def random_frame(mesh, rng):
    """each mesh inverted or not by an independent fair coin: a draw of the null."""
    coins = rng.integers(0, 2, size=mesh.shape[0])
    out = np.stack([invert_mesh(m) if c else np.asarray(m) for m, c in zip(mesh, coins)])
    return out, coins


def lower_median(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2] if s else math.inf


def pinning(meshes):
    """report only: a point-odd structure pinned to the lab would align DIFFERENT runs at the
    same mesh index. G = mean over run pairs and meshes 1..23 of the cosine of the inner
    blocks' odd parts; exact one-sided p over every run-level inversion (2^R sign patterns,
    each run's whole mesh set inverted or not; s and -s give the same G, so p >= 2 / 2^R)."""
    R = len(meshes)
    odds = [np.stack([odd16(mq.sub(m[j], mq.B2)).ravel() for j in range(1, m.shape[0])]) for m in meshes]
    odds = [o / np.maximum(np.linalg.norm(o, axis=1, keepdims=True), 1e-300) for o in odds]
    C = np.zeros((R, R))
    for a in range(R):
        for b in range(a + 1, R):
            C[a, b] = float((odds[a] * odds[b]).sum(axis=1).mean())
    pairs = [(a, b) for a in range(R) for b in range(a + 1, R)]
    G = float(np.mean([C[a, b] for a, b in pairs])) if pairs else float('nan')
    ge = 0
    for s in itertools.product((1, -1), repeat=R):
        g = np.mean([s[a] * s[b] * C[a, b] for a, b in pairs])
        ge += g >= G - 1e-15
    return {'runs': R, 'G_mean_cosine': G, 'pairs_positive': int(sum(C[a, b] > 0 for a, b in pairs)),
            'pairs': len(pairs), 'p_one_sided_exact': ge / 2 ** R, 'patterns': 2 ** R}


def planning(q_from, w_values=(0.0, 0.01, 0.025), runs_per_condition=3):
    """report only: under per-run call rates (target q, contrary w, none otherwise), the chance
    of each branch outcome of one nine-run arm under the fixed aggregation."""
    out = []
    for q in q_from:
        for w in w_values:
            probs = {'target': q, 'contrary': w, 'none': max(0.0, 1.0 - q - w)}
            dist = {'pref_target': 0.0, 'target_calls_ge_license': 0.0, 'license': 0.0, 'contrary_any': 0.0}
            for calls in itertools.product(('target', 'contrary', 'none'), repeat=3 * runs_per_condition):
                pr = 1.0
                for c in calls:
                    pr *= probs[c]
                if pr == 0:
                    continue
                conds = {}
                for ci in range(3):
                    cc = calls[ci * runs_per_condition:(ci + 1) * runs_per_condition]
                    conds[ci] = condition_label(['Pi' if c == 'target' else 'L' if c == 'contrary' else 'none' for c in cc])
                pref = preference(conds) == 'Pi'
                k = sum(c == 'target' for c in calls)
                dist['pref_target'] += pr * pref
                dist['target_calls_ge_license'] += pr * (k >= LICENSE_MIN_PI)
                dist['license'] += pr * (pref and k >= LICENSE_MIN_PI and 'contrary' not in calls)
                dist['contrary_any'] += pr * ('contrary' in calls)
            out.append({'q': q, 'w': w, **{k: round(v, 4) for k, v in dist.items()}})
    return out


# ------------------------------------------------------------------ io

def sha256_file(path):
    return mq.sha256_file(path)


def rel(path):
    root = mq.repo_root()
    ap = os.path.abspath(path)
    return os.path.relpath(ap, root) if ap.startswith(root + os.sep) else ap


def git(*args):
    return subprocess.run(['git', '-C', mq.repo_root(), *args], capture_output=True, text=True)


def committed_same(commit, relpath):
    """True when `commit` holds relpath with exactly the bytes on disk."""
    a = git('rev-parse', f'{commit}:{relpath}')
    b = git('hash-object', os.path.join(mq.repo_root(), relpath))
    return a.returncode == 0 and b.returncode == 0 and a.stdout.strip() == b.stdout.strip()


def load_runs(indir):
    """every halo-memory-prereg/1 record in indir with its mesh (void records are skipped)."""
    grid, _ = mq.load_grid(indir)
    heads = {}
    for fn in sorted(os.listdir(indir)):
        if fn.endswith('.json'):
            try:
                h = json.load(open(os.path.join(indir, fn)))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(h, dict) and h.get('schema') == mq.SCHEMA_IN:
                heads[h['tag']] = (os.path.join(indir, fn), h)
    out = []
    for key in sorted(grid):
        for r in grid[key]:
            jp, h = heads[r['tag']]
            mp = os.path.join(indir, h['mesh_file'])
            out.append({'key': key, 'seed': r['seed'], 'tag': r['tag'], 'mesh': r['mesh'],
                        'label': mq.run_label(key, r['seed']), 'json': jp, 'mesh_path': mp,
                        'json_sha256': sha256_file(jp), 'mesh_sha256': sha256_file(mp)})
    return out


def runtime():
    return {'python': platform.python_version(), 'numpy': np.__version__, 'platform': platform.platform()}


def script_sha256():
    return sha256_file(os.path.abspath(__file__))


def write_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(mq.jsonable(obj), fh, indent=1, sort_keys=True)
        fh.write('\n')


# ------------------------------------------------------------------ receipt

def receipt(control_dirs, design_commit, out_path):
    full = git('rev-parse', design_commit).stdout.strip()
    for relpath in (SCRIPT_REL, PREREG_REL):
        if not committed_same(full or design_commit, relpath):
            raise SystemExit(f'refusing: {relpath} on disk is not the file committed at {design_commit}')
    runs, seen = [], {}
    for d in control_dirs:
        for r in load_runs(d):
            if r['mesh_sha256'] in seen:          # the second Ring 29 directory reuses six meshes
                seen[r['mesh_sha256']]['also_in'].append(rel(d))
                continue
            r['dir'] = rel(d)
            r['also_in'] = []
            seen[r['mesh_sha256']] = r
            runs.append(r)
    print(f'{len(runs)} distinct control runs', file=sys.stderr)
    base = {r['label']: run_pairs(r['mesh']) for r in runs}
    stats = {lab: statistic(pp) for lab, pp in base.items()}

    # G1 exactness (a construction check: fails only on a bug)
    supports = mq.build_supports()
    dev_anti = dev_inv = dev_odd_rel = dev_frame = 0.0
    frame_mask_same, nonfinite = True, 0
    for r in runs:
        m = r['mesh']
        for k in range(mq.FIRST_SCORED, mq.LAST_SCORED + 1):
            C, R = m[k - 1], m[k - 2]
            a = pair_value(C, R)['rho']
            b = pair_value(invert_mesh(C), R)['rho']
            c = pair_value(invert_mesh(C), invert_mesh(R))['rho']
            if a == a or b == b or c == c:
                if not (math.isfinite(a) and math.isfinite(b) and math.isfinite(c)):
                    nonfinite += 1
                    continue
                dev_anti = max(dev_anti, abs(a + b))
                dev_inv = max(dev_inv, abs(c - a))
            for fld in (mq.sub(C, mq.B2), mq.predicted(R, 2)):
                raw = odd16(fld)
                scale = float(np.abs(fld).max()) or 1.0
                for mode, (s2, _) in supports.items():
                    d = float(np.abs(odd16(s2.residual(fld)) - raw).max()) / scale
                    nonfinite += not math.isfinite(d)
                    dev_odd_rel = max(dev_odd_rel, d if math.isfinite(d) else 0.0)
        sp = statistic(run_pairs(mf.derive(m, 'point')))
        sl = stats[r['label']]
        if sl['n'] and sp['n']:
            d = abs(sp['T'] + sl['T'])
            nonfinite += not math.isfinite(d)
            dev_frame = max(dev_frame, d if math.isfinite(d) else 0.0)
        frame_mask_same = frame_mask_same and sp['eligible_mask'] == sl['eligible_mask']
    g1 = {'max_abs_rho_PC_R_plus_rho_C_R': dev_anti, 'max_abs_rho_PC_PR_minus_rho_C_R': dev_inv,
          'max_odd_residual_minus_odd_raw_over_max_field_all_supports': dev_odd_rel,
          'supports_checked': sorted(supports), 'max_abs_T_Pi_plus_T_L': dev_frame,
          'eligible_sets_identical_in_both_frames': bool(frame_mask_same), 'tolerance': EXACT_TOL,
          'nonfinite_deviations': nonfinite, 'kind': 'construction check: fails only on a bug'}
    g1['pass'] = bool(max(dev_anti, dev_inv, dev_odd_rel, dev_frame) <= EXACT_TOL and frame_mask_same
                      and nonfinite == 0)
    print(f"G1 {'PASS' if g1['pass'] else 'FAIL'}", file=sys.stderr)

    # G2 the null end to end, and G2b the exact p by two enumerations (construction checks)
    calls = {'L': 0, 'Pi': 0, 'none': 0, 'unscored': 0}
    per_run_null, p_mismatch, p_checked = {}, 0, 0
    for ri, r in enumerate(runs):
        cr = {'L': 0, 'Pi': 0, 'none': 0, 'unscored': 0}
        for dr in range(N_NULL_DRAWS):
            rng = np.random.default_rng([RECEIPT_SEED, 2, ri, dr])
            fm, _ = random_frame(r['mesh'], rng)
            pp = run_pairs(fm)
            s = statistic(pp)
            cr[s['call']] += 1
            if dr < 5 and s['n'] >= MIN_PAIRS:
                x = [pr['rho'] for pr in pp if pr['eligible']]
                p_checked += 1
                p_mismatch += direct_p(x) != s['p']
        per_run_null[r['label']] = cr
        for kk in calls:
            calls[kk] += cr[kk]
        s = stats[r['label']]
        if s['n'] >= MIN_PAIRS:
            p_checked += 1
            p_mismatch += direct_p([pr['rho'] for pr in base[r['label']] if pr['eligible']]) != s['p']
        print(f"  G2 {r['label']}: {cr}", file=sys.stderr)
    n_scored = calls['L'] + calls['Pi'] + calls['none']
    band = binom_band(n_scored, P_CALL) if n_scored else [0, 0]
    g2 = {'draws_per_run': N_NULL_DRAWS, 'runs': len(runs), 'scored': n_scored, 'calls': calls,
          'rejections': calls['L'] + calls['Pi'], 'band95_for_0.05': band, 'per_run': per_run_null,
          'kind': 'construction check: the test is exact under this null by construction, so the '
                  'count checks the code end to end and says nothing about the chamber; with correct '
                  'code it exceeds the band about 2.4% of the time'}
    g2['pass'] = bool(n_scored > 0 and g2['rejections'] <= band[1])
    g2b = {'p_values_checked': p_checked, 'mismatches': p_mismatch,
           'kind': 'construction check: meet-in-the-middle p equals direct enumeration, exactly'}
    g2b['pass'] = bool(p_checked > 0 and p_mismatch == 0)
    print(f"G2 {'PASS' if g2['pass'] else 'FAIL'} {g2['rejections']} of {n_scored} band {band}; "
          f"G2b {p_mismatch} mismatches of {p_checked}", file=sys.stderr)

    # G3 one run in (a construction check)
    g3_same = True
    for r in runs:
        alone = statistic(run_pairs(np.fromfile(r['mesh_path'], dtype='<f4').reshape(-1, mq.N, mq.N, mq.N)))
        s = stats[r['label']]
        g3_same = g3_same and alone['T'] == s['T'] and alone['n'] == s['n'] and alone['p'] == s['p']
    g3 = {'runs': len(runs), 'identical_from_the_run_alone': bool(g3_same),
          'kind': 'construction check: the function takes one run; no other run enters'}
    g3['pass'] = bool(g3_same)

    # G4 the falsifier: recovery of an injected carried relic after a null draw
    per_run, contrary_at_alpha = {}, 0
    for ri, r in enumerate(runs):
        stars, rec02, excl = [], [], 0
        for dr in range(N_INJ_DRAWS):
            rng = np.random.default_rng([RECEIPT_SEED, 4, ri, dr])
            fm, _ = random_frame(r['mesh'], rng)
            p0 = run_pairs(fm)
            s0 = statistic(p0)
            if s0['n'] < MIN_PAIRS or s0['call'] != 'none':
                excl += 1
                continue
            mask = s0['eligible_mask']
            star, got02 = None, False
            for alpha in ALPHAS[1:]:
                over = {pr['k']: mq.inject(fm[pr['k'] - 1], fm[pr['k'] - 2], alpha)
                        for pr, ok in zip(p0, mask) if ok}
                s = statistic(run_pairs(fm, cur_override=over), mask=mask)
                contrary_at_alpha += s['call'] == 'Pi'
                if s['call'] == 'L' and star is None:
                    star = alpha
                if alpha == ALPHAS[-1]:
                    got02 = s['call'] == 'L'
            stars.append(ALPHAS[-1] if star is None else star)   # unrecovered counts as 0.2 (frozen F3)
            rec02.append(got02)
        kept = len(stars)
        per_run[r['label']] = {'alpha_star': stars, 'median_alpha_star': lower_median(stars),
                               'kept_draws': kept, 'excluded_draws': excl,
                               'recovered_at_0.2': int(sum(rec02)),
                               'required_at_0.2': int(math.ceil(RECOVER_AT_MAX * kept))}
        print(f"  G4 {r['label']}: median alpha* {per_run[r['label']]['median_alpha_star']}, "
              f"at 0.2 {sum(rec02)}/{kept}, excluded {excl}", file=sys.stderr)
    meds = [v['median_alpha_star'] for v in per_run.values()]
    overall = lower_median(meds)
    all_recovered = all(v['kept_draws'] > 0 and v['recovered_at_0.2'] >= v['required_at_0.2'] for v in per_run.values())
    g4 = {'draws_per_run': N_INJ_DRAWS, 'alphas': ALPHAS, 'injection': 'the frozen F3 mix (memory_estimator_qualify.inject)',
          'per_run': per_run, 'lower_median_over_runs_of_lower_median_alpha_star': overall,
          'threshold_median': ALPHA_FAIL, 'threshold_share_at_0.2': RECOVER_AT_MAX,
          'Pi_calls_at_any_alpha_above_0': contrary_at_alpha,
          'kind': 'the falsifier: sensitivity to a carried relic mixed into every pair, not power on the chamber'}
    g4['pass'] = bool(overall <= ALPHA_FAIL and all_recovered and contrary_at_alpha == 0)
    print(f"G4 {'PASS' if g4['pass'] else 'FAIL'} median alpha* {overall}; Pi at alpha>0 {contrary_at_alpha}",
          file=sys.stderr)

    # G5 reported: the unperturbed control in the lab frame (decides nothing)
    ctl = {lab: {k: v for k, v in s.items() if k != 'eligible_mask'} for lab, s in stats.items()}
    ncall = {c: sum(1 for s in stats.values() if s['call'] == c) for c in ('L', 'Pi', 'none', 'unscored')}
    g5 = {'runs': len(runs), 'calls': ncall, 'per_run': ctl, 'kind': 'reported baseline; decides nothing'}

    # reported: lag specificity, lab pinning, and the planning table
    lagspec = {}
    for ri, r in enumerate(runs):
        m = r['mesh']
        Ts, cs = [], {'L': 0, 'Pi': 0, 'none': 0, 'unscored': 0}
        for dr in range(N_SHUFFLE_DRAWS):
            rng = np.random.default_rng([RECEIPT_SEED, 6, ri, dr])
            pairs = []
            for k in range(mq.FIRST_SCORED, mq.LAST_SCORED + 1):
                choices = [j for j in range(m.shape[0]) if j not in (k - 2, k - 1, k)]
                pairs.append(pair_value(m[k - 1], m[int(rng.choice(choices))]))
            s = statistic(pairs)
            Ts.append(s['T'])
            cs[s['call']] += 1
        lagspec[r['label']] = {'mean_T': float(np.nanmean(Ts)), 'calls': cs}
    q_ctl = ncall['L'] / len(runs) if runs else 0.0
    out = {'schema': SCHEMA_RECEIPT, 'script': SCRIPT_REL, 'script_sha256': script_sha256(),
           'design_commit': full, 'prereg': PREREG_REL,
           'frozen_scorer_sha256': sha256_file(os.path.join(HERE, 'memory_estimator_qualify.py')),
           'frames_script_sha256': sha256_file(os.path.join(HERE, 'memory_intervention_frames.py')),
           'gates_script_sha256': sha256_file(os.path.join(HERE, 'memory_intervention_gates.py')),
           'computed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'runtime': runtime(),
           'constants': {'min_pairs': MIN_PAIRS, 'p_call': P_CALL, 'tie_abs': TIE_ABS, 'exact_tol': EXACT_TOL,
                         'seed': RECEIPT_SEED, 'null_draws': N_NULL_DRAWS, 'injection_draws': N_INJ_DRAWS,
                         'shuffle_draws': N_SHUFFLE_DRAWS, 'alphas': ALPHAS, 'alpha_fail': ALPHA_FAIL,
                         'recover_at_max': RECOVER_AT_MAX, 'license_min_pi': LICENSE_MIN_PI,
                         'support': mq.MAIN['support']},
           'inputs': [{'dir': r['dir'], 'also_in': r['also_in'], 'label': r['label'], 'json': os.path.basename(r['json']),
                       'json_sha256': r['json_sha256'], 'mesh': os.path.basename(r['mesh_path']),
                       'mesh_sha256': r['mesh_sha256']} for r in runs],
           'G1_exactness': g1, 'G2_null_end_to_end': g2, 'G2b_exact_p': g2b, 'G3_one_run_in': g3,
           'G4_recovery': g4, 'G5_control_baseline_reported': g5,
           'reported_lag_specificity': lagspec,
           'reported_lab_pinning_control': pinning([r['mesh'] for r in runs]),
           'reported_planning': {'q_from_control_L_calls': q_ctl,
                                 'table': planning([q_ctl, q_ctl / 2, 2 / 9]),
                                 'note': 'planning numbers from the control bytes, not thresholds'},
           'control_pairs': {lab: [{'k': pr['k'], 'eligible': pr['eligible'], 'rho': pr['rho'],
                                    'odd_share_cur': pr['odd_share_cur'], 'odd_share_pred': pr['odd_share_pred']}
                                   for pr in pp] for lab, pp in base.items()}}
    out['receipt_passed'] = bool(g1['pass'] and g2['pass'] and g2b['pass'] and g3['pass'] and g4['pass'])
    write_json(out, out_path)
    print(f"receipt passed = {out['receipt_passed']} -> {out_path}", file=sys.stderr)
    return out


# ------------------------------------------------------------------ score

def receipt_gates_pass(rc):
    return all(rc.get(g, {}).get('pass') is True for g in
               ('G1_exactness', 'G2_null_end_to_end', 'G2b_exact_p', 'G3_one_run_in', 'G4_recovery'))


def check_receipt(receipt_path):
    rc = json.load(open(receipt_path))
    if rc.get('schema') != SCHEMA_RECEIPT or not rc.get('receipt_passed') or not receipt_gates_pass(rc):
        raise SystemExit(f'{receipt_path}: not a passing receipt')
    for key, fn in (('frozen_scorer_sha256', 'memory_estimator_qualify.py'),
                    ('frames_script_sha256', 'memory_intervention_frames.py'),
                    ('gates_script_sha256', 'memory_intervention_gates.py')):
        if rc.get(key) != sha256_file(os.path.join(HERE, fn)):
            raise SystemExit(f'refusing: {fn} differs from the bytes the receipt recorded')
    rt = rc.get('runtime', {})
    if (rt.get('python'), rt.get('numpy')) != (platform.python_version(), np.__version__):
        raise SystemExit('refusing: not the Python and numpy the receipt was computed with')
    if rc.get('script_sha256') != script_sha256():
        raise SystemExit('the receipt was produced by different script bytes; refusing')
    if not committed_same(rc.get('design_commit', 'x'), SCRIPT_REL):
        raise SystemExit('this script is not the one committed at the receipt\'s design commit; refusing')
    return rc


def checks_exist(root):
    """nothing is scored before the canary and the closing repeat have records."""
    missing = []
    for name, (sg, seed) in (('canary', CANARY[:2]), ('close', CLOSING)):
        tag = f'spinchladni_sg{sg:g}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_ividentity'
        if not os.path.exists(os.path.join(root, DIRS[name], tag + '.json')):
            missing.append(DIRS[name])
    return missing


def score(indir, arm, receipt_path, out_path):
    check_receipt(receipt_path)
    miss = checks_exist(os.path.dirname(os.path.abspath(indir)))
    if miss:
        raise SystemExit(f'refusing: no record yet in {miss}; nothing is scored before the twentieth record')
    runs = load_runs(indir)
    got = sorted((r['key'][1], r['seed']) for r in runs)
    want = sorted((sg, s) for sg, seeds in REGISTERED.items() for s in seeds)
    if got != want:
        raise SystemExit(f'refusing: {indir} holds {got}, not the nine registered runs')
    res, pins = [], pinning([r['mesh'] for r in sorted(runs, key=lambda r: (r['key'][1], r['seed']))])
    for r in runs:
        pairs = run_pairs(r['mesh'])
        s = statistic(pairs)
        sp = statistic(run_pairs(mf.derive(r['mesh'], 'point')))
        frame_ok = sp['eligible_mask'] == s['eligible_mask'] and (not s['n'] or abs(sp['T'] + s['T']) <= EXACT_TOL)
        res.append({'label': r['label'], 'selfgrav': r['key'][1], 'seed': r['seed'], 'tag': r['tag'],
                    'json': os.path.basename(r['json']), 'json_sha256': r['json_sha256'],
                    'mesh_sha256': r['mesh_sha256'], 'T': s['T'], 'n': s['n'], 'p': s['p'], 'call': s['call'],
                    'n_eff': s['n_eff'], 'top3_share': s['top3_share'], 'T_Pi_frame': sp['T'],
                    'a3_static': a3_static(r['mesh']),
                    'frame_identity_holds': bool(frame_ok), 'eligible_mask': s['eligible_mask'],
                    'rho': [pr['rho'] for pr in pairs]})
        print(f"{r['label']}: T {s['T']:+.4f} n {s['n']} p {s['p']} call {s['call']}", file=sys.stderr)
    out = {'schema': SCHEMA_SCORE, 'arm': arm, 'dir': rel(indir), 'script_sha256': script_sha256(),
           'receipt': rel(receipt_path), 'receipt_sha256': sha256_file(receipt_path),
           'computed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'runtime': runtime(),
           'reported_lab_pinning': pins, 'runs': res}
    write_json(out, out_path)
    return out


# ------------------------------------------------------------------ decide

def condition_label(calls):
    has_pi, has_l = 'Pi' in calls, 'L' in calls
    return 'mixed' if has_pi and has_l else 'Pi' if has_pi else 'L' if has_l else 'none'


def preference(conds):
    labs = list(conds.values())
    if sum(c == 'Pi' for c in labs) >= 2 and not any(c in ('L', 'mixed') for c in labs):
        return 'Pi'
    if sum(c == 'L' for c in labs) >= 2 and not any(c in ('Pi', 'mixed') for c in labs):
        return 'L'
    return 'none'


def arm_summary(runs):
    conds, scored = {}, {}
    for sg in REGISTERED:
        cc = [r['call'] for r in runs if abs(r['selfgrav'] - sg) < 1e-9]
        conds[f'sg{sg:g}'] = condition_label(cc)
        scored[f'sg{sg:g}'] = sum(c != 'unscored' for c in cc)
    counts = {c: sum(1 for r in runs if r['call'] == c) for c in ('L', 'Pi', 'none', 'unscored')}
    return {'conditions': conds, 'scored_per_condition': scored, 'preference': preference(conds),
            'call_counts': counts}


def classify(ident, pos, static_runs=0):
    """the branch from the two arm summaries, in the registered order (after V1)."""
    if static_runs:
        return 'STATIC', f'{static_runs} run(s) with a median lag-one full-field Pearson of at least {STATIC_A3}'
    if any(v < 2 for v in list(ident['scored_per_condition'].values()) + list(pos['scored_per_condition'].values())):
        return 'UNMEASURED', 'a condition with fewer than 2 scored runs'
    if ident['preference'] == 'Pi' or pos['preference'] == 'L' or ident['call_counts']['Pi'] >= 2 \
            or pos['call_counts']['L'] >= 2:
        return 'BROKEN', (f"identity {ident['preference']} with {ident['call_counts']['Pi']} Pi calls; "
                          f"invert_all {pos['preference']} with {pos['call_counts']['L']} L calls")
    if ident['preference'] != 'L':
        return 'BASELINE SILENT', f"identity prefers {ident['preference']}"
    k = pos['call_counts']['Pi']
    if pos['preference'] == 'Pi':      # an L call makes its condition L or mixed, so none is present here
        if k >= LICENSE_MIN_PI:
            return 'CONFIRMED', f'invert_all prefers Pi with {k} Pi calls'
        return 'LOW POWER', f'invert_all prefers Pi with only {k} Pi calls'
    if pos['call_counts']['L']:
        return 'CONTRARY', f"invert_all has {pos['call_counts']['L']} L call and prefers none"
    return 'SILENT', 'invert_all prefers none'


def v1_voids(d):
    """Ring 30's re-issue rule: a 'refused' void is not a run and is skipped; every other void is
    a crash with no page error, at most one per run, and the run it voided exists."""
    bad, per_tag, n = [], {}, 0
    if not os.path.isdir(d):
        return [f'{rel(d)} missing'], 0
    for fn in sorted(os.listdir(d)):
        if '.void-' not in fn or not fn.endswith('.json'):
            continue
        try:
            v = json.load(open(os.path.join(d, fn)))
        except (OSError, json.JSONDecodeError) as e:
            bad.append(f'{fn}: unreadable void record ({type(e).__name__})')
            continue
        if v.get('kind') == 'refused':
            continue
        n += 1
        tag = fn.split('.void-')[0]
        per_tag[tag] = per_tag.get(tag, 0) + 1
        if v.get('kind') != 'crash' or v.get('pageerrors'):
            bad.append(f"{fn}: kind {v.get('kind')} with page errors {v.get('pageerrors')} is not re-issuable")
        if not os.path.exists(os.path.join(d, tag + '.json')):
            bad.append(f'{fn}: the voided run was not re-issued to a record')
    bad += [f'{t}: {c} voids (the rule allows one re-issue)' for t, c in per_tag.items() if c > 1]
    return bad, n


def runtime_faults(r):
    ins, caps = r.get('instrument', {}), (r.get('applied') or {}).get('caps') or {}
    bad = [f'{k} {ins.get(k)} is not {v}' for k, v in RUNTIME_PINS.items() if ins.get(k) != v]
    if caps.get('renderer') != RENDERER:
        bad.append(f"renderer {caps.get('renderer')}")
    return bad


def ledger_faults(root):
    """at most two counted launches per run (a launch that ended in a 'refused' void is not a run),
    and a second launch only after a crash void or a kept-aside first attempt."""
    path = os.path.join(mq.repo_root(), LEDGER_REL)
    if not os.path.exists(path):
        return ['no launch ledger']
    rows = [l.rstrip('\n').split('\t') for l in open(path) if l.strip()]
    bad, per = [], {}
    for r in rows:
        per.setdefault((r[1], r[2]), []).append(r)
    for (d, tag), rr in per.items():
        dd = os.path.join(mq.repo_root(), d)
        voids = []
        for fn in sorted(os.listdir(dd)) if os.path.isdir(dd) else []:
            if fn.startswith(tag + '.void-') and fn.endswith('.json'):
                voids.append(json.load(open(os.path.join(dd, fn))).get('kind'))
        counted = len(rr) - voids.count('refused')
        if counted > 2:
            bad.append(f'{tag}: {counted} counted launches')
        if counted == 2 and not ('crash' in voids or os.path.exists(os.path.join(dd, tag + '.attempt1.mesh.f32.partial'))):
            bad.append(f'{tag}: a second launch with neither a crash void nor a kept-aside first attempt')
    return bad


def decide(arms, prereg, out_path, root=None):
    import memory_intervention_gates as mig   # Ring 30's per-record and per-hook checks, reused
    root = root or os.path.join(mq.repo_root(), 'data', 'results', 'halo')
    prereg = git('rev-parse', prereg).stdout.strip() or prereg
    v1, n_voids, sums, mesh0, n_static = [], 0, {}, {}, 0
    # the receipt must be the one committed at R, written from a design commit that is R's ancestor
    rpath = os.path.join(mq.repo_root(), RECEIPT_REL)
    rc = check_receipt(rpath)
    if not committed_same(prereg, RECEIPT_REL):
        v1.append('the receipt on disk is not the one committed at R')
    dc = rc.get('design_commit', '')
    if dc == prereg or git('merge-base', '--is-ancestor', dc or 'x', prereg).returncode != 0:
        v1.append('the receipt\'s design commit is not a strict ancestor of R')
    v1 += ledger_faults(root)
    for name, path in arms:
        sc = json.load(open(path))
        if sc.get('schema') != SCHEMA_SCORE or sc.get('arm') != name:
            raise SystemExit(f'{path}: not the carrier score of arm {name}')
        if sc.get('script_sha256') != script_sha256() or sc.get('receipt_sha256') != sha256_file(rpath):
            v1.append(f'{name}: the score was not written by these bytes from this receipt')
        d = os.path.join(root, DIRS[name])
        # re-derive every call from the meshes; the score file is not trusted
        fresh = {(r['key'][1], r['seed']): r for r in load_runs(d)}
        want = sorted((sg, s_) for sg, seeds in REGISTERED.items() for s_ in seeds)
        if sorted(fresh) != want or sorted((r['selfgrav'], r['seed']) for r in sc['runs']) != want:
            v1.append(f'{name}: not exactly the nine registered runs')
        for r in sc['runs']:
            fr = fresh.get((r['selfgrav'], r['seed']))
            if fr is None:
                continue
            s_ = statistic(run_pairs(fr['mesh']))
            if (s_['T'], s_['n'], s_['p'], s_['call']) != (r['T'], r['n'], r['p'], r['call']):
                v1.append(f"{name} {r['label']}: the score's T, n, p or call is not what the mesh gives")
            if a3_static(fr['mesh']) >= STATIC_A3:
                n_static += 1
        vb, nv = v1_voids(d)
        v1 += [f'{name} {b}' for b in vb]
        n_voids += nv
        for r in sc['runs']:
            rec = json.load(open(os.path.join(d, r['json'])))
            v1 += [f"{name} {r['label']}: {b}" for b in
                   mig.run_faults(d, r['json'], rec, name, prereg, HARNESS_SHA) + runtime_faults(rec)]
            if sha256_file(os.path.join(d, rec['mesh_file'])) != r['mesh_sha256']:
                v1.append(f"{name} {r['label']}: mesh bytes differ from the score")
            with open(os.path.join(d, rec['mesh_file']), 'rb') as fh:
                mesh0.setdefault((r['selfgrav'], r['seed']), {})[name] = fh.read(MESH0_BYTES)
        sums[name] = arm_summary(sc['runs'])
    # the same-seed gate: an arm's first mesh is written before its first hook
    m0 = {k: v for k, v in mesh0.items()}
    for k, v in m0.items():
        if len(set(v.values())) != 1:
            v1.append(f'sg{k[0]:g} seed {k[1]}: the first mesh differs between arms')
    if len({next(iter(v.values())) for v in m0.values()}) != len(m0):
        v1.append('two registered runs share a first mesh')
    # the canary (Ring 29's bytes) and the closing repeat
    for name, (sg, seed), want in (('canary', CANARY[:2], CANARY[2]), ('close', CLOSING, None)):
        d = os.path.join(root, DIRS[name])
        tag = f'spinchladni_sg{sg:g}_gl0_seed{seed}_n4194304_e24_fieldExp1.7_ividentity'
        try:
            rec = json.load(open(os.path.join(d, tag + '.json')))
            v1 += [f'{name}: {b}' for b in mig.run_faults(d, tag + '.json', rec, 'identity', prereg, HARNESS_SHA)
                   + runtime_faults(rec)]
            got = sha256_file(os.path.join(d, rec['mesh_file']))
            if want is None:
                want = sha256_file(os.path.join(root, DIRS['identity'], tag + '.mesh.f32'))
            if got != want:
                v1.append(f'{name}: mesh {got[:8]} is not {want[:8]}')
        except (OSError, json.JSONDecodeError) as e:
            v1.append(f'{name}: {type(e).__name__} {e}')
        vb, nv = v1_voids(d)
        v1 += [f'{name} {b}' for b in vb]
        n_voids += nv
    if v1:
        branch, cause = 'VOID', f'V1: {len(v1)} failure(s)'
    else:
        branch, cause = classify(sums['identity'], sums['invert_all'], n_static)
    out = {'schema': SCHEMA_DECISION, 'prereg_commit': prereg, 'script_sha256': script_sha256(),
           'V1_instrument': {'pass': not v1, 'failures': v1, 'void_records': n_voids},
           'static_runs': n_static,
           'arms': sums, 'branch': branch, 'proximate_cause': cause,
           'identity_L_calls': sums['identity']['call_counts']['L'],
           'invert_all_Pi_calls': sums['invert_all']['call_counts']['Pi'],
           'computed_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    write_json(out, out_path)
    print(f'branch {branch} ({cause})', file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='mode', required=True)
    a1 = sub.add_parser('receipt')
    a1.add_argument('--design-commit', required=True)
    a1.add_argument('--control', action='append', required=True)
    a1.add_argument('--json', required=True)
    a2 = sub.add_parser('score')
    a2.add_argument('dir')
    a2.add_argument('--arm', required=True, choices=('identity', 'invert_all'))
    a2.add_argument('--receipt', required=True)
    a2.add_argument('--json', required=True)
    a3 = sub.add_parser('decide')
    a3.add_argument('--prereg-commit', required=True)
    a3.add_argument('--arm', nargs=2, action='append', metavar=('NAME', 'SCORE_JSON'), required=True)
    a3.add_argument('--json', required=True)
    a = ap.parse_args()
    if a.mode == 'receipt':
        receipt(a.control, a.design_commit, a.json)
    elif a.mode == 'score':
        score(a.dir, a.arm, a.receipt, a.json)
    else:
        decide(a.arm, a.prereg_commit, a.json)


if __name__ == '__main__':
    main()
