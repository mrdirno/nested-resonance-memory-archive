#!/usr/bin/env python3
"""memory_prereg_robustness.py - does the verdict depend on how the rule is read?

Section 8 of the pre-registration decides, and memory_prereg_verdict.py applies it.
But three clauses of §7-§8 do not determine a single answer, and three independent
readers of the frozen prose split on all three. A result that changes with the
reading is not a result; a result that survives every reading is worth more than one
that was never checked. This script scores the same data under every reading and
prints them together.

THE THREE READINGS, and what the prose says about each:

  ADJACENCY - §8 says "three consecutive scored epochs"; §7.3 says an undefined epoch
  "is excluded and counted". If it is excluded, do its neighbours become adjacent, or
  does the sequence break? The prose says both things and settles neither.
      break   - an undefined epoch resets the streak (what verdict.py does)
      close   - undefined epochs are dropped and the survivors are consecutive

  VOID ACCOUNTING - §7 says a gated run "cannot support a positive"; §8(a) says a
  condition must fire "in >= 2 of its 3 seeds". Does a void run still occupy a seed
  slot in the quorum, and does it still count in the grid totals of (d)?
      keep    - void cells stay in the counts (what verdict.py does)
      drop    - void cells leave both the quorum and the grid totals

  CEILING POOLING - §7.2 attaches a median to a CONDITION, but the ceiling share is
  measured per epoch per run, and no combining rule is given.
      medmed  - median per run, then median across the three seeds (what verdict.py does)
      pooled  - one median over every scored epoch of every seed

That is 2 x 2 x 2 = 8 readings. If all eight agree, the verdict does not rest on an
ambiguity. If they split, this script says exactly which clause splits them, and the
write-up must report the split rather than pick a favourite.

Usage:  python3 memory_prereg_robustness.py [analysis.json]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import itertools
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_prereg_verdict import (THRESHOLD, RUN, CEILING_BOUND, MASS_TOL,
                                   MAX_UNDEFINED, FIRST_SCORED, LAST_SCORED,
                                   binom_tail, median, completeness)


def scored(series):
    return [e for e in series
            if FIRST_SCORED <= e.get('epoch', 0) <= LAST_SCORED]


def contrast(series, arm, control='twoback'):
    out = []
    for e in scored(series):
        a, b = e.get(arm), e.get(control)
        bad = (a is None or b is None
               or (isinstance(a, float) and math.isnan(a))
               or (isinstance(b, float) and math.isnan(b)))
        out.append(None if bad else a - b)
    return out


def fires(vals, adjacency):
    if adjacency == 'close':
        vals = [v for v in vals if v is not None]
    streak = 0
    for v in vals:
        if v is not None and v > THRESHOLD:
            streak += 1
            if streak >= RUN:
                return True
        else:
            streak = 0
    return False


def score(runs, adjacency, voidacct, pooling):
    cells = []
    for r in runs:
        s = r['series']
        undef = sum(1 for e in scored(s) if e.get('twoback') is None)
        loss = r.get('mass', {}).get('max_relative_loss')
        void = (loss is None) or (loss > MASS_TOL) or (undef > MAX_UNDEFINED)
        cs = [e['ceiling'] for e in r['page']
              if e['ceiling'] is not None and FIRST_SCORED <= e.get('epoch', 0) <= LAST_SCORED]
        cells.append({
            'key': (r.get('preset', 'spinchladni'), r['selfgrav'], r['gainloss']),
            'seed': r['seed'], 'void': void, 'ceil': cs,
            'f': fires(contrast(s, 'retained'), adjacency),
            'fm': fires(contrast(s, 'retained_matched'), adjacency),
            'fn': fires(contrast(s, 'seed_null'), adjacency),
        })

    used = [c for c in cells if not (voidacct == 'drop' and c['void'])]
    conds = {}
    for c in used:
        conds.setdefault(c['key'], []).append(c)

    n = len(used)
    k_real = sum(1 for c in used if c['f'])
    k_null = sum(1 for c in used if c['fn'])
    p_val = binom_tail(k_real, n, k_null / n) if n else 1.0

    passing, blocked = [], []
    for key, group in sorted(conds.items()):
        if pooling == 'pooled':
            med = median([v for c in group for v in c['ceil']])
        else:
            med = median([median(c['ceil']) for c in group])
        bound = med >= CEILING_BOUND
        anyvoid = any(c['void'] for c in group)
        if sum(1 for c in group if c['f']) >= 2 and sum(1 for c in group if c['fm']) >= 2:
            (blocked if (bound or anyvoid) else passing).append((key, round(med, 3)))

    if passing and p_val < 0.05:
        v = 'POSITIVE'
    elif passing or blocked:
        v = 'INCONCLUSIVE'
    else:
        v = 'NULL'
    return {'verdict': v, 'cells': n, 'fired': k_real, 'fired_null': k_null,
            'p': p_val, 'passing': passing, 'blocked': blocked,
            'void_cells': sum(1 for c in cells if c['void'])}


def main(path):
    runs = json.load(open(path))
    ok, why = completeness(runs)
    print(f'grid: {why}')
    if not ok:
        print('*** PARTIAL GRID - THIS DECIDES NOTHING (section 9) ***')

    rows = []
    for adj, va, pool in itertools.product(('break', 'close'), ('keep', 'drop'),
                                           ('medmed', 'pooled')):
        r = score(runs, adj, va, pool)
        r['reading'] = (adj, va, pool)
        rows.append(r)

    print(f"\n{'adjacency':10s} {'void':6s} {'ceiling':8s} | {'verdict':13s} "
          f"{'cells':>5s} {'fired':>5s} {'null':>5s} {'p':>8s}  passing / blocked")
    print('-' * 96)
    for r in rows:
        a, v, p = r['reading']
        print(f"{a:10s} {v:6s} {p:8s} | {r['verdict']:13s} {r['cells']:5d} "
              f"{r['fired']:5d} {r['fired_null']:5d} {r['p']:8.4f}  "
              f"{len(r['passing'])} / {len(r['blocked'])}")

    verdicts = {r['verdict'] for r in rows}
    print()
    if len(verdicts) == 1:
        print(f"ALL EIGHT READINGS AGREE: {verdicts.pop()}. The verdict does not rest on any "
              f"clause the pre-registration left open.")
    else:
        print(f"THE READINGS SPLIT: {sorted(verdicts)}. The pre-registration under-determines "
              f"the outcome, and the split must be published, not resolved by preference.")
        for axis, i in (('adjacency', 0), ('void accounting', 1), ('ceiling pooling', 2)):
            groups = {}
            for r in rows:
                groups.setdefault(r['reading'][i], set()).add(r['verdict'])
            if any(len(v) > 1 for v in groups.values()) or len({frozenset(v) for v in groups.values()}) > 1:
                print(f"  - {axis}: " + '; '.join(f"{k} -> {sorted(v)}" for k, v in groups.items()))

    out = os.path.join(os.path.dirname(path), 'robustness.json')
    json.dump({'grid_complete': ok, 'grid_note': why,
               'readings': [{**r, 'reading': list(r['reading'])} for r in rows]},
              open(out, 'w'), indent=1)
    print('wrote', out)
    return rows


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg', 'analysis.json')
    main(os.path.abspath(src))
