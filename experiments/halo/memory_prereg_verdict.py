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
FIRST_SCORED = 3      # section 8: "Scored epochs are k = 3 ... 24."
LAST_SCORED = 24
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
    """the per-epoch contrast over the SCORED epochs only.

    Section 8: "Scored epochs are k = 3 ... 24." This filter used to be absent, and
    `fires` streaks over list position, so epochs 1 and 2 could complete a triple.
    Unreachable with real data - `retained` is undefined at epoch 1 and `twoback` at
    epoch 2, so both entries are always None - but the rule says k >= 3 and the code
    now says it too, rather than relying on the estimator to say it by accident.
    """
    out = []
    for e in series:
        if e.get('epoch', 0) < FIRST_SCORED or e.get('epoch', 0) > LAST_SCORED:
            continue
        a, b = e.get(arm), e.get(control)
        if a is None or b is None or math.isnan(a) or math.isnan(b):
            out.append(None)
        else:
            out.append(a - b)
    return out


def median(xs):
    """the median proper: on an even-length list, the mean of the two middle values.

    The previous code took the upper-middle element, which differs from the median
    whenever a run has an even number of scored epochs - which is every run here, at
    22. It never mattered on this data, because the ceiling shares are bimodal and
    nothing lands near the 0.5 gate, but the gate is stated as a median.
    """
    s = sorted(xs)
    n = len(s)
    if not n:
        return float('nan')
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def binom_tail(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p)."""
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


EXPECTED_CELLS = 60      # section 5: 2 presets x 5 self-gravity x 2 gain/loss x 3 seeds
EXPECTED_SEEDS = 3


def completeness(runs):
    """what section 9 forbids: a look at a grid that is not finished.

    Returns (ok, message). The grid is complete when it holds EXPECTED_CELLS runs and
    every condition holds EXPECTED_SEEDS of them. On a short grid the quorum of
    section 8(a) cannot be assessed for a condition that is missing a seed, and the
    binomial of 8(d) is taken over the wrong n - so the answer is not merely noisier,
    it is a different rule. The script refuses rather than printing a verdict nobody
    should read.
    """
    conds = {}
    for r in runs:
        conds.setdefault((r.get('preset', 'spinchladni'), r['selfgrav'], r['gainloss']), 0)
        conds[(r.get('preset', 'spinchladni'), r['selfgrav'], r['gainloss'])] += 1
    short = sorted(k for k, v in conds.items() if v != EXPECTED_SEEDS)
    if len(runs) == EXPECTED_CELLS and not short and len(conds) == EXPECTED_CELLS // EXPECTED_SEEDS:
        return True, f'complete: {len(runs)} cells, {len(conds)} conditions, {EXPECTED_SEEDS} seeds each'
    bits = [f'{len(runs)} of {EXPECTED_CELLS} cells', f'{len(conds)} of {EXPECTED_CELLS // EXPECTED_SEEDS} conditions']
    if short:
        bits.append(f'{len(short)} condition(s) without {EXPECTED_SEEDS} seeds: ' +
                    ', '.join(f'{k[0]} sg{k[1]} gl{k[2]}={conds[k]}' for k in short[:6]))
    return False, 'INCOMPLETE - ' + '; '.join(bits)


def main(path):
    runs = json.load(open(path))
    cells, conditions = [], {}
    for r in runs:
        s = r['series']
        undefined = sum(1 for e in s if e.get('epoch', 0) >= 3
                        and (e.get('twoback') is None or (isinstance(e.get('twoback'), float)
                                                          and math.isnan(e['twoback']))))
        loss = r.get('mass', {}).get('max_relative_loss')
        # A half-written run has no mass evidence, so it cannot pass gate 1; it is void,
        # not a crash. Section 9 anticipates a machine failing mid-grid.
        void = (loss is None) or (loss > MASS_TOL) or (undefined > MAX_UNDEFINED)
        # section 7 gate 2 says "median ceiling share OVER SCORED EPOCHS". The epoch
        # filter was missing, so the two unscored epochs entered the median.
        ceil = [e['ceiling'] for e in r['page']
                if e['ceiling'] is not None and FIRST_SCORED <= e.get('epoch', 0) <= LAST_SCORED]
        med = median(ceil)
        cell = {
            'preset': r.get('preset', 'spinchladni'),
            'selfgrav': r['selfgrav'], 'gainloss': r['gainloss'], 'seed': r['seed'],
            'void': void, 'undefined': undefined,
            'mass_loss': loss,
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
        med = median([c['median_ceiling'] for c in group])
        bound = med >= CEILING_BOUND
        anyvoid = any(c['void'] for c in group)
        nf = sum(1 for c in group if c['fires'])
        nm = sum(1 for c in group if c['fires_matched'])
        # Section 8(a) says ">= 2 of its 3 seeds", literally. The old fallback
        # `2 if len(group) >= 3 else len(group)` let a condition holding ONE run pass
        # (a) and (b) on that single run, which is only reachable on a partial grid -
        # exactly the interim look section 9 forbids. A short condition now cannot pass.
        need = 2
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
        med = median([x['median_ceiling'] for x in group])
        if med >= CEILING_BOUND:
            continue
        need = 2
        if sum(1 for x in group if x['fires']) >= need and \
           sum(1 for x in group if x['fires_matched']) >= need:
            adm_pass.append(key)
    adm_cells = [c for c in adm if median(
        [x['median_ceiling'] for x in adm_conditions[(c['preset'], c['selfgrav'], c['gainloss'])]]
    ) < CEILING_BOUND]
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
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    partial = '--partial' in sys.argv
    src = args[0] if args else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg', 'analysis.json')
    src = os.path.abspath(src)
    ok, why = completeness(json.load(open(src)))
    print(f'grid: {why}')
    if not ok and not partial:
        print('REFUSING to score an unfinished grid. Section 9 of the pre-registration allows no')
        print('interim look; a short condition also changes the rule, not just its noise. Pass')
        print('--partial to score it anyway, and label the output as deciding nothing.')
        sys.exit(3)
    if not ok:
        print('*** PARTIAL GRID - THIS DECIDES NOTHING (section 9) ***')
    v = main(src)
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
    v['grid_complete'] = ok
    v['grid_note'] = why
    out = os.path.join(os.path.dirname(src), 'verdict.json' if ok else 'verdict_partial.json')
    json.dump(v, open(out, 'w'), indent=1)
    print('wrote', out)
