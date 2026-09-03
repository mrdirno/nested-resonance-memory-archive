#!/usr/bin/env python3
"""memory_prereg_artefact.py - is the pre-registered criterion a memory statistic at all?

Section 8 of the pre-registration decides a cell by

    Delta_k = Retained_k - TwoBack_k > 0.10 for three consecutive scored epochs

where Retained correlates the current inner 16^3 against the relic sampled at stride 2, and
TwoBack correlates the current inner 8^3 against the relic sampled at stride 4. The two arms
therefore differ in how densely they sample the relic, not only in epoch lag. This script asks
what that difference is worth on fields that cannot possibly remember anything.

Three checks, in increasing contact with the real data:

  STATIC      A closed-form spherically symmetric profile correlated with an IDENTICAL copy of
              itself. No time, no dynamics, no particles, no force clamp, nothing to remember.
              If Delta > 0.10 here, the criterion is not measuring memory.

  RADIAL      Every stored mesh replaced by its own spherical-shell average about the cavity
              centre. Every angular mode - the figure, the relic pattern, everything the claim
              is about - is deleted; only the radial profile survives. Section 8 is then re-run
              unchanged. Requires the meshes.

  ONECELL     In the conditions that fire, how much of TwoBack is one mesh cell? The whole x4
              relic block is replaced by a bare 0/1 indicator of its single dominant cell and
              the arm is recomputed. Requires the meshes.

The STATIC check needs no GPU, no meshes and no run data: it reproduces in about a second.

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


def blocks(f, q=None):
    """the same index map as memory_prereg_analyze._blocks and the page's labCorr."""
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


# ---------------------------------------------------------------- radius grid

_i = np.arange(N) - (N - 1) / 2.0
RADIUS = np.sqrt(_i[:, None, None] ** 2 + _i[None, :, None] ** 2 + _i[None, None, :] ** 2)


def static_profiles():
    r = RADIUS
    return [
        ('Plummer a=2', (1 + (r / 2.0) ** 2) ** -2.5),
        ('Plummer a=4', (1 + (r / 4.0) ** 2) ** -2.5),
        ('isothermal 1/(1+r^2)', 1.0 / (1.0 + r ** 2)),
        ('power law r^-2', 1.0 / np.maximum(r, 0.5) ** 2),
        ('Gaussian sigma=3', np.exp(-(r / 3.0) ** 2 / 2)),
        ('Gaussian sigma=6', np.exp(-(r / 6.0) ** 2 / 2)),
        ('exponential e^-r/3', np.exp(-r / 3.0)),
        ('uniform ball r<8', (r < 8).astype(float)),
    ]


def check_static():
    """A field correlated with itself. Delta here is pure index-map asymmetry."""
    print('STATIC - one field, correlated with an IDENTICAL copy of itself under the two maps.')
    print('         No time axis. Nothing to remember. Criterion is Delta > 0.10.\n')
    print(f"  {'profile':22s} {'Retained':>9s} {'Two-back':>9s} {'Delta':>8s}   fires?")
    fired = 0
    rows = []
    for name, f in static_profiles():
        ret = arm(f, f, 2)
        two = arm(f, f, 4)
        d = ret - two
        hit = (d == d) and d > THRESHOLD
        fired += bool(hit)
        rows.append({'profile': name, 'retained': ret, 'twoback': two, 'delta': d,
                     'fires': bool(hit)})
        ds = '     nan' if d != d else f'{d:8.4f}'
        print(f"  {name:22s} {ret:9.4f} {two:9.4f} {ds}   {'YES' if hit else 'no'}")
    print(f'\n  {fired} of {len(rows)} static profiles fire a criterion registered as a memory test.')
    return rows


def radialise(mesh, bin_width):
    idx = (RADIUS / bin_width).astype(np.int32)
    nb = int(idx.max()) + 1
    flat = idx.ravel()
    s = np.bincount(flat, weights=mesh.ravel().astype(np.float64), minlength=nb)
    c = np.bincount(flat, minlength=nb)
    return (s / np.maximum(c, 1))[idx].astype(np.float32)


def load_runs(indir):
    runs = {}
    for fn in sorted(os.listdir(indir)):
        if not fn.endswith('.json'):
            continue
        try:
            with open(os.path.join(indir, fn)) as fh:
                head = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # A derived product half-written by a crashed sibling is not a run, and
            # should not stop the analysis of 60 that are intact. This script's own
            # first version left exactly such a file here and then refused to start.
            print(f'  skipping {fn}: not valid JSON', file=sys.stderr)
            continue
        if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
            continue
        mp = os.path.join(indir, head['mesh_file'])
        if not os.path.exists(mp):
            print(f'  skipping {fn}: its mesh is missing', file=sys.stderr)
            continue
        p = head['params']
        runs.setdefault((p['preset'], p['selfgrav'], p['gainloss']), []).append((p['seed'], head, mp))
    for k in runs:
        runs[k].sort()
    return runs


def check_radial(runs, widths=(1.0, 0.5, 0.25)):
    """Delete every angular mode, then re-run section 8 unchanged."""
    print('\nRADIAL - every mesh replaced by its own spherical-shell average.')
    print('         All angular structure deleted; only the radial profile survives.\n')
    print(f"  {'radial bin (cells)':>19s} {'real fires':>11s} {'seed-null fires':>16s}   of cells")
    out = []
    for bw in widths:
        real = null = cells = 0
        for key in sorted(runs):
            group = runs[key]
            rad = []
            for _seed, head, mp in group:
                m = np.fromfile(mp, dtype=np.float32).reshape(head['mesh_count'], N, N, N)
                rad.append(np.stack([radialise(m[e], bw) for e in range(len(m))]))
            for i in range(len(group)):
                me, other = rad[i], rad[(i + 1) % len(group)]
                dr, dn = [], []
                for e in range(2, len(me)):
                    if not (FIRST_SCORED <= e + 1 <= LAST_SCORED):
                        continue
                    r = arm(me[e], me[e - 1], 2)
                    t = arm(me[e], me[e - 2], 4)
                    s = arm(me[e], other[e - 1], 2) if e - 1 < len(other) else float('nan')
                    dr.append(None if (r != r or t != t) else r - t)
                    dn.append(None if (s != s or t != t) else s - t)
                cells += 1
                real += fires(dr)
                null += fires(dn)
        print(f"  {bw:19} {real:11d} {null:16d}   of {cells}")
        out.append({'bin_width': bw, 'cells': cells, 'real_fires': real, 'null_fires': null})
    return out


def check_onecell(runs, conditions=None):
    """How much of the Two-back control arm is a single mesh cell?"""
    print('\nONECELL - the x4 relic block replaced by a 0/1 indicator of its dominant cell.\n')
    print(f"  {'condition':24s} {'seed':>6s} {'nnz/512':>8s} {'var in 1':>9s} {'Two-back':>9s} "
          f"{'TB 1-cell':>10s} {'Delta':>8s} {'Delta both 1-cell':>18s}")
    out = []
    keys = conditions or [k for k in sorted(runs) if k[0] == 'default' and k[1] >= 0.15 and k[2] == 0]
    # Every seed is reported. Taking runs[key][0] would silently pick the numerically
    # smallest seed (777) and hide that the collapse is not uniform across seeds - at
    # self-gravity 0.3 one seed keeps a Delta of 0.24 after both relics are reduced.
    c2, r2 = blocks(2)
    c4, r4 = blocks(4)
    med = lambda x: sorted(x)[len(x) // 2]
    for key in keys:
        if key not in runs:
            continue
        for seed, head, mp in runs[key]:
            m = np.fromfile(mp, dtype=np.float32).reshape(head['mesh_count'], N, N, N)
            tb, tbi, dd, ddi, nz, vr = [], [], [], [], [], []
            for k in range(2, len(m)):
                if not (FIRST_SCORED <= k + 1 <= LAST_SCORED):
                    continue
                cur4, rel4 = m[k][np.ix_(c4, c4, c4)], m[k - 2][np.ix_(r4, r4, r4)]
                cur2, rel2 = m[k][np.ix_(c2, c2, c2)], m[k - 1][np.ix_(r2, r2, r2)]
                ind4 = np.zeros_like(rel4); ind4.ravel()[np.argmax(rel4)] = 1.0
                ind2 = np.zeros_like(rel2); ind2.ravel()[np.argmax(rel2)] = 1.0
                a, b = pearson(cur4, rel4), pearson(cur4, ind4)
                c, d = pearson(cur2, rel2), pearson(cur2, ind2)
                if a == a and b == b and c == c and d == d:
                    tb.append(a); tbi.append(b); dd.append(c - a); ddi.append(d - b)
                nz.append(int((rel4 > 0).sum()))
                f = rel4.ravel().astype(np.float64) - rel4.mean()
                ss = float((f ** 2).sum())
                vr.append(float(f.max() ** 2 / ss) if ss > 0 else float('nan'))
            if not tb:
                continue
            row = {'condition': list(key), 'seed': seed, 'nonzero_relic_cells': med(nz),
                   'variance_in_one_cell': med(vr), 'twoback': med(tb),
                   'twoback_one_cell': med(tbi), 'delta': med(dd),
                   'delta_both_one_cell': med(ddi)}
            out.append(row)
            print(f"  {str(key):24s} {seed:6d} {med(nz):8d} {med(vr):9.4f} {med(tb):9.4f} "
                  f"{med(tbi):10.4f} {med(dd):8.4f} {med(ddi):18.4f}")
    return out


def jsonable(o):
    """an undefined value is written as null, so a strict parser in any language reads it."""
    if isinstance(o, float):
        return None if math.isnan(o) or math.isinf(o) else o
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


def main(indir):
    report = {'static': check_static()}
    if indir and os.path.isdir(indir):
        runs = load_runs(indir)
        if runs:
            report['radial'] = check_radial(runs)
            report['onecell'] = check_onecell(runs)
        else:
            print('\n(no meshes found; STATIC only)', file=sys.stderr)
    else:
        print('\n(no mesh directory; STATIC only)', file=sys.stderr)
    return report


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg')
    src = os.path.abspath(src)
    rep = main(src)
    dst = os.path.join(src, 'artefact.json') if os.path.isdir(src) else 'artefact.json'
    with open(dst, 'w') as fh:
        # NaN is not JSON (RFC 8259), and json.dump's `default=` never sees a float -
        # it is only consulted for types the encoder cannot handle at all, so the
        # first version of this raised on the uniform-ball row. Sanitise the tree.
        json.dump(jsonable(rep), fh, indent=1, allow_nan=False)
    print(f'\nwrote {dst}')
