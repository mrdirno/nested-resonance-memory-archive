#!/usr/bin/env python3
"""memory_prereg_nullrate.py - what criterion (d) is worth, given that it estimates
its own null rate from the same 60 cells it then tests against.

THIS DOES NOT CHANGE THE DECISION RULE. Section 8 of the pre-registration decides,
and memory_prereg_verdict.py applies it literally. This script reads that script's
verdict.json and reports, alongside it, how much of the p-value survives when the
uncertainty in the estimated null rate is not thrown away.

The defect, stated plainly. Criterion (d) says the firing count must exceed the
count the same rule produces on the independent-seed series, "by a one-sided
binomial test at p < 0.05 over the 60 cells". The implementation estimates the
null probability as k_null / n and then treats that estimate as if it were known:

    p_null = k_null / n
    p      = P(Binomial(n, p_null) >= k_real)

When the null arm fires in zero cells - which is what a good null looks like -
p_null is exactly 0, and the probability of seeing even one firing cell under a
process that fires with probability 0 is 0. So a SINGLE firing cell clears
p < 0.05 automatically, and would have cleared it at any threshold. The test as
implemented cannot fail to reject once k_null is 0, which is the one case it was
written for. It is not a test at that point; it is an assertion.

Three numbers are printed instead of one:

  (1) AS REGISTERED - the plug-in p that section 8 specifies and verdict.py computes.
      This is the deciding number. It is reproduced here so the three sit together.

  (2) CONSERVATIVE - the same binomial tail, but with the null rate replaced by its
      one-sided 95% upper confidence bound rather than its point estimate. With
      k_null successes in n cells that bound is the largest p whose lower tail still
      leaves 5% at k_null, found by bisection (Clopper-Pearson). For 0 in 60 it is
      1 - 0.05^(1/60) = 0.0487, the exact form of the rule of three. This asks: if
      the null rate is as high as the data can barely exclude, is the real arm still
      ahead?

  (3) PAIRED (McNemar, exact) - the arms are not two independent samples. They are
      two measurements on the SAME cell: the same run's density scored against its
      own previous relic, and against another seed's relic at the same epoch and the
      same settings. The paired test throws away the cells where both fire or
      neither fires and asks whether the disagreements lean one way, under a fair
      coin. One discordant cell gives p = 0.5 whatever the grid size; five give
      0.031. This is the test the design actually earns.

Read them together. If the registered p is 0.0000 while the paired p is 0.5, the
grid has one firing cell and one arm's worth of evidence, and the registered number
is an artefact of estimating a rate as zero - not a discovery.

Usage:  python3 memory_prereg_nullrate.py [verdict.json]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import math
import os
import sys


def binom_tail(k, n, p):
    """P(X >= k) for X ~ Binomial(n, p). Same function verdict.py uses."""
    if p <= 0:
        return 0.0 if k > 0 else 1.0
    if p >= 1:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def upper_bound(k, n, alpha=0.05):
    """One-sided upper confidence bound on a binomial rate (Clopper-Pearson).

    The largest p for which P(X <= k) is still at least alpha; at k = 0 this is
    exactly 1 - alpha**(1/n), the rule of three. Found by bisection so the k > 0
    case needs no special maths.
    """
    if k >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X <= k) = 1 - P(X >= k+1)
        if (1.0 - binom_tail(k + 1, n, mid)) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mcnemar_exact(b, c):
    """One-sided exact McNemar: P(X >= b) for X ~ Binomial(b + c, 0.5).

    b = cells where the real arm fires and the null arm does not.
    c = cells where the null arm fires and the real arm does not.
    Concordant cells carry no information about which arm is ahead and drop out.
    """
    m = b + c
    if m == 0:
        return 1.0
    return sum(math.comb(m, i) for i in range(b, m + 1)) / 2 ** m


def main(path):
    v = json.load(open(path))
    cells = v['table']
    n = len(cells)
    k_real = sum(1 for c in cells if c['fires'])
    k_null = sum(1 for c in cells if c['fires_null'])
    b = sum(1 for c in cells if c['fires'] and not c['fires_null'])
    c_ = sum(1 for c in cells if c['fires_null'] and not c['fires'])
    both = sum(1 for c in cells if c['fires'] and c['fires_null'])

    p_plugin = binom_tail(k_real, n, k_null / n) if n else 1.0
    p_hi = upper_bound(k_null, n)
    p_cons = binom_tail(k_real, n, p_hi) if n else 1.0
    p_pair = mcnemar_exact(b, c_)

    print(f"criterion (d) on {n} cells:  real arm fired {k_real}, seed-null arm fired {k_null}")
    print(f"  paired breakdown: real only {b}, null only {c_}, both {both}, neither {n - b - c_ - both}")
    print(f"  (1) AS REGISTERED   p = {p_plugin:.4f}   (null rate taken as exactly {k_null / n:.4f})")
    print(f"  (2) CONSERVATIVE    p = {p_cons:.4f}   (null rate at its 95% upper bound {p_hi:.4f})")
    print(f"  (3) PAIRED McNEMAR  p = {p_pair:.4f}   (exact, on {b + c_} discordant cells)")
    if k_null == 0 and k_real > 0:
        print("  NOTE: the registered p is 0 by construction here - the null arm fired in no cell,")
        print("        so its estimated rate is exactly zero and any firing at all clears any")
        print("        threshold. Read (2) and (3), not (1).")
    return {'cells': n, 'fired': k_real, 'fired_under_null': k_null,
            'discordant_real_only': b, 'discordant_null_only': c_, 'both': both,
            'p_as_registered': p_plugin, 'null_rate_upper_95': p_hi,
            'p_conservative': p_cons, 'p_paired_mcnemar': p_pair}


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg', 'verdict.json')
    src = os.path.abspath(src)
    out = main(src)
    dst = os.path.join(os.path.dirname(src), 'nullrate.json')
    json.dump(out, open(dst, 'w'), indent=1)
    print('wrote', dst)
