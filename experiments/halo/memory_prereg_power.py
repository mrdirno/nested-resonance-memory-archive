#!/usr/bin/env python3
"""memory_prereg_power.py - how much real memory would this design have caught?

The pre-registration fixed a criterion (Delta > 0.10 for three consecutive scored epochs)
and a grid, and never asked what effect size that combination can detect. Without that
number neither INCONCLUSIVE nor a null is interpretable: "we found nothing" means one thing
if the design could see a 2% relic and another if it could only see a 50% one.

INJECTION-RECOVERY. At every scored epoch of every run, a fraction alpha of the scored
block's mass is replaced by a verbatim copy of exactly what the strong passive-relic reading
predicts: the previous epoch's relic, read through labCorr's own x2 index map so it lands
where the map says it should reappear, rescaled to leave the block's total mass unchanged.

    block'  =  (1 - alpha) * block  +  alpha * relic * (mass(block) / mass(relic))

Nothing else changes - same meshes, same estimators, same section 7 gates, same section 8
rule. alpha = 0 is the archive's own dataset and must reproduce 32 fires.

Two readings of the null arm are reported, because the choice is not obvious and it moves
the answer:

  null held    the SeedNull arm keeps its measured value. Defensible because the injected
               signal is this run's own relic, which an unrelated seed's relic does not
               contain - but in the `default` family the two seeds' fields are near
               duplicates, so injecting into the current field does leak into SeedNull.
  null injected the SeedNull arm is recomputed on the injected current field. Strictly
               conservative: whatever the injection does to the real arm, it is allowed to
               do to the null as well.

The injection is not propagated into the next epoch's relic, which makes every threshold
below an upper bound on what a real memory of that strength would have produced.

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import math
import os
import sys

import numpy as np

N = 32
H = N // 2
THRESHOLD = 0.10
RUN = 3
FIRST_SCORED, LAST_SCORED = 3, 24
CEILING_BOUND = 0.5
ALPHAS = (0.0, 0.010, 0.015, 0.019, 0.020, 0.030, 0.050, 0.100, 0.200)


def blocks(f, q=None):
    q = H // f if q is None else q
    cur = np.arange(H - q, H + q)
    return cur, H + f * (cur - H)


def pearson(a, b):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    va, vb = a.var(), b.var()
    if va <= 0 or vb <= 0:
        return float('nan')
    return float(((a - a.mean()) * (b - b.mean())).mean() / math.sqrt(va * vb))


def arm(cur_field, relic_field, f, q=None):
    cur, rel = blocks(f, q)
    return pearson(cur_field[np.ix_(cur, cur, cur)], relic_field[np.ix_(rel, rel, rel)])


def fires(vals):
    streak = 0
    for v in vals:
        if v is not None and v == v and v > THRESHOLD:
            streak += 1
            if streak >= RUN:
                return True
        else:
            streak = 0
    return False


def median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return float('nan')
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def binom_tail(k, n, p):
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def inject(cur_mesh, relic_mesh, alpha):
    """replace alpha of the scored block's mass with the relic the x2 map predicts."""
    if alpha <= 0:
        return cur_mesh
    cur, rel = blocks(2)
    out = cur_mesh.copy()
    block = out[np.ix_(cur, cur, cur)].astype(np.float64)
    relic = relic_mesh[np.ix_(rel, rel, rel)].astype(np.float64)
    bm, rm = block.sum(), relic.sum()
    if rm <= 0 or bm <= 0:
        return cur_mesh
    out[np.ix_(cur, cur, cur)] = ((1 - alpha) * block + alpha * relic * (bm / rm)).astype(np.float32)
    return out


def load(indir):
    runs = {}
    for fn in sorted(os.listdir(indir)):
        if not fn.endswith('.json'):
            continue
        try:
            with open(os.path.join(indir, fn)) as fh:
                head = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
            continue
        mp = os.path.join(indir, head['mesh_file'])
        if not os.path.exists(mp):
            continue
        p = head['params']
        ceil = [e['ceiling'] for e in head['epochs']
                if e.get('ceiling') is not None and FIRST_SCORED <= e.get('epoch', 0) <= LAST_SCORED]
        runs.setdefault((p['preset'], p['selfgrav'], p['gainloss']), []).append({
            'seed': p['seed'],
            'mesh': np.fromfile(mp, dtype=np.float32).reshape(head['mesh_count'], N, N, N),
            'ceiling': median(ceil) if ceil else float('nan'),
        })
    for k in runs:
        runs[k].sort(key=lambda r: r['seed'])
    return runs


def score(runs, alpha, null_injected):
    cells = []
    for key, group in sorted(runs.items()):
        for i, r in enumerate(group):
            partner = group[(i + 1) % len(group)]
            m, om = r['mesh'], partner['mesh']
            dr, dn, dm = [], [], []
            for k in range(2, len(m)):
                if not (FIRST_SCORED <= k + 1 <= LAST_SCORED):
                    continue
                cur = inject(m[k], m[k - 1], alpha)
                ret = arm(cur, m[k - 1], 2)
                two = arm(cur, m[k - 2], 4)
                retm = arm(cur, m[k - 1], 2, q=H // 4)
                nul_src = cur if null_injected else m[k]
                sn = arm(nul_src, om[k - 1], 2) if k - 1 < len(om) else float('nan')
                snm = arm(nul_src, om[k - 1], 2, q=H // 4) if k - 1 < len(om) else float('nan')
                two_n = arm(nul_src, m[k - 2], 4)
                dr.append(None if (ret != ret or two != two) else ret - two)
                dm.append(None if (retm != retm or two != two) else retm - two)
                dn.append(None if (sn != sn or two_n != two_n) else sn - two_n)
                del snm
            cells.append({'condition': key, 'seed': r['seed'], 'ceiling': r['ceiling'],
                          'fires': fires(dr), 'fires_matched': fires(dm), 'fires_null': fires(dn)})
    n = len(cells)
    k_real = sum(c['fires'] for c in cells)
    k_null = sum(c['fires_null'] for c in cells)
    p_null = k_null / n if n else 0.0
    p_value = binom_tail(k_real, n, p_null) if n else 1.0
    passing, blocked = [], []
    conds = {}
    for c in cells:
        conds.setdefault(c['condition'], []).append(c)
    for key, g in sorted(conds.items()):
        bound = median([x['ceiling'] for x in g]) >= CEILING_BOUND
        if sum(x['fires'] for x in g) >= 2 and sum(x['fires_matched'] for x in g) >= 2:
            (blocked if bound else passing).append(key)
    if passing and p_value < 0.05:
        verdict = 'POSITIVE'
    elif passing or blocked:
        verdict = 'INCONCLUSIVE'
    else:
        verdict = 'NULL'
    return {'alpha': alpha, 'null_injected': null_injected, 'cells': n, 'fired': k_real,
            'fired_null': k_null, 'p_value': p_value, 'verdict': verdict,
            'passing': [list(k) for k in passing], 'blocked': len(blocked)}


def main(indir):
    runs = load(indir)
    total = sum(len(v) for v in runs.values())
    print(f'{total} runs, {len(runs)} conditions\n')
    out = []
    for null_injected in (False, True):
        tag = 'null recomputed on the injected field' if null_injected else 'null held at its measured value'
        print(f'--- {tag}')
        print(f"  {'alpha':>7s} {'fired':>6s} {'null':>5s} {'p (8d)':>9s} {'pass':>5s} {'blocked':>8s}  verdict")
        for a in ALPHAS:
            r = score(runs, a, null_injected)
            out.append(r)
            print(f"  {a:7.3f} {r['fired']:6d} {r['fired_null']:5d} {r['p_value']:9.5f} "
                  f"{len(r['passing']):5d} {r['blocked']:8d}  {r['verdict']}")
        print()
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg'))
    rep = main(src)
    dst = os.path.join(src, 'power.json')
    with open(dst, 'w') as fh:
        json.dump(rep, fh, indent=1, allow_nan=False)
    print(f'wrote {dst}')
