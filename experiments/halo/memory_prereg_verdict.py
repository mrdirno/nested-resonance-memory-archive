#!/usr/bin/env python3
"""memory_prereg_verdict.py - applies section 8 of the pre-registration, literally.

Input:  the analysis.json written by memory_prereg_analyze.py
Output: the verdict, the table behind it, and the rule's own false-positive rate,
        measured on this dataset rather than assumed.

The rule (docs/preregistrations/2026-09-02_halo_cross_epoch_memory.md section 8):
  a cell fires if three consecutive scored epochs have Retained - TwoBack > 0.10;
  POSITIVE needs a condition firing in >=2 of 3 seeds, firing the same way on the
  region-matched arm, not ceiling-bound, not void, and a firing count above what
  the same rule produces on the independent-seed null.

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import math
import os
import sys

THRESHOLD = 0.10
RUN = 3
CEILING_BOUND = 0.5
MASS_TOL = 1e-3
MAX_UNDEFINED = 4


def fires(vals):
    """three consecutive scored epochs above threshold; None breaks the run."""
    streak = 0
    for v in vals:
        if v is not None and not math.isnan(v) and v > THRESHOLD:
            streak += 1
            if streak >= RUN:
                return True
        else:
            streak = 0
    return False


def contrast(series, arm, control='twoback'):
    out = []
    for e in series:
        a, b = e.get(arm), e.get(control)
        if a is None or b is None or math.isnan(a) or math.isnan(b):
            out.append(None)
        else:
            out.append(a - b)
    return out


def binom_tail(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p)."""
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def main(path):
    runs = json.load(open(path))
    cells, conditions = [], {}
    for r in runs:
        s = r['series']
        undefined = sum(1 for e in s if e.get('epoch', 0) >= 3
                        and (e.get('twoback') is None or (isinstance(e.get('twoback'), float)
                                                          and math.isnan(e['twoback']))))
        void = (r['mass']['max_relative_loss'] > MASS_TOL) or (undefined > MAX_UNDEFINED)
        ceil = [e['ceiling'] for e in r['page'] if e['ceiling'] is not None]
        ceil.sort()
        med = ceil[len(ceil) // 2] if ceil else float('nan')
        cell = {
            'preset': r.get('preset', 'spinchladni'),
            'selfgrav': r['selfgrav'], 'gainloss': r['gainloss'], 'seed': r['seed'],
            'void': void, 'undefined': undefined,
            'mass_loss': r['mass']['max_relative_loss'],
            'max_cell_particles': r['mass']['max_cell_particles'],
            'pmDensType': r.get('pmDensType'),
            'median_ceiling': med,
            'fires': fires(contrast(s, 'retained')),
            'fires_matched': fires(contrast(s, 'retained_matched')),
            'fires_null': fires(contrast(s, 'seed_null')),
            'fires_null_matched': fires(contrast(s, 'seed_null_matched')),
            'max_delta': max([d for d in contrast(s, 'retained') if d is not None] or [float('nan')]),
        }
        cells.append(cell)
        conditions.setdefault((cell['preset'], cell['selfgrav'], cell['gainloss']), []).append(cell)

    n = len(cells)
    k_real = sum(1 for c in cells if c['fires'])
    k_null = sum(1 for c in cells if c['fires_null'])
    p_null = k_null / n if n else 0.0
    p_value = binom_tail(k_real, n, p_null) if n else 1.0

    passing, blocked = [], []
    for key, group in sorted(conditions.items()):
        med = sorted(c['median_ceiling'] for c in group)[len(group) // 2]
        bound = med >= CEILING_BOUND
        anyvoid = any(c['void'] for c in group)
        nf = sum(1 for c in group if c['fires'])
        nm = sum(1 for c in group if c['fires_matched'])
        need = 2 if len(group) >= 3 else len(group)
        rec = {'condition': key, 'seeds': len(group), 'fires': nf, 'fires_matched': nm,
               'median_ceiling': med, 'ceiling_bound': bound, 'any_void': anyvoid}
        if nf >= need and nm >= need:
            (blocked if (bound or anyvoid) else passing).append(rec)

    if passing and p_value < 0.05:
        verdict = 'POSITIVE'
    elif passing and p_value >= 0.05:
        verdict = 'INCONCLUSIVE'
        # fires, but no more often than the rule fires on a relic that cannot be remembered
    elif blocked and not passing:
        verdict = 'INCONCLUSIVE'
    else:
        verdict = 'NULL'

    # REPORTED ALONGSIDE, NOT A CHANGE TO THE RULE. Section 7 says a ceiling-bound or
    # void condition "cannot support a positive"; the rule above lets such a condition
    # push the WHOLE grid to INCONCLUSIVE even when every admissible condition is a
    # clean null. Both readings are printed so a reader can see which is which.
    adm = [c for c in cells if not c['void']]
    adm_conditions = {}
    for c in adm:
        adm_conditions.setdefault((c['preset'], c['selfgrav'], c['gainloss']), []).append(c)
    adm_pass = []
    for key, group in sorted(adm_conditions.items()):
        med = sorted(x['median_ceiling'] for x in group)[len(group) // 2]
        if med >= CEILING_BOUND:
            continue
        need = 2 if len(group) >= 3 else len(group)
        if sum(1 for x in group if x['fires']) >= need and \
           sum(1 for x in group if x['fires_matched']) >= need:
            adm_pass.append(key)
    adm_cells = [c for c in adm if sorted(
        x['median_ceiling'] for x in adm_conditions[(c['preset'], c['selfgrav'], c['gainloss'])]
    )[len(adm_conditions[(c['preset'], c['selfgrav'], c['gainloss'])]) // 2] < CEILING_BOUND]
    admissible = {
        'conditions': len({(c['preset'], c['selfgrav'], c['gainloss']) for c in adm_cells}),
        'cells': len(adm_cells),
        'fired': sum(1 for c in adm_cells if c['fires']),
        'fired_under_null': sum(1 for c in adm_cells if c['fires_null']),
        'fired_matched': sum(1 for c in adm_cells if c['fires_matched']),
        'fired_matched_under_null': sum(1 for c in adm_cells if c['fires_null_matched']),
        'passing_conditions': adm_pass,
        'verdict': 'NULL' if not adm_pass else 'POSITIVE-CANDIDATE',
    }

    return {'verdict': verdict, 'cells': n, 'fired': k_real, 'fired_under_null': k_null,
            'null_firing_rate': p_null, 'p_value': p_value,
            'passing_conditions': passing, 'blocked_conditions': blocked,
            'admissible_subset': admissible, 'table': cells}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg', 'analysis.json')
    v = main(os.path.abspath(src))
    print(f"VERDICT: {v['verdict']}")
    print(f"  cells {v['cells']}   fired {v['fired']}   fired under the seed null {v['fired_under_null']}"
          f"   null rate {v['null_firing_rate']:.3f}   p {v['p_value']:.4f}")
    for r in v['passing_conditions']:
        print(f"  PASS   {r['condition']}  {r['fires']}/{r['seeds']} seeds, matched {r['fires_matched']}, "
              f"ceiling {r['median_ceiling']:.2f}")
    for r in v['blocked_conditions']:
        print(f"  BLOCKED{r['condition']}  {r['fires']}/{r['seeds']} seeds  "
              f"({'ceiling-bound' if r['ceiling_bound'] else ''}{' void' if r['any_void'] else ''})")
    a = v['admissible_subset']
    print(f"  ADMISSIBLE SUBSET (not ceiling-bound, not void): {a['conditions']} conditions, "
          f"{a['cells']} cells -> {a['verdict']}")
    print(f"    as-displayed arm fired {a['fired']}, its null fired {a['fired_under_null']};  "
          f"matched arm fired {a['fired_matched']}, its matched null fired {a['fired_matched_under_null']}")
    out = os.path.join(os.path.dirname(os.path.abspath(src)), 'verdict.json')
    json.dump(v, open(out, 'w'), indent=1)
    print('wrote', out)
