#!/usr/bin/env python3
"""memory_prereg_figure.py - the pre-registered memory result in two panels.

LEFT - THE DECISION RULE ITSELF. Section 8 says a cell fires if three consecutive
scored epochs have Retained - TwoBack > 0.10. The decision statistic is therefore
the best any three-in-a-row window does:

    D = max over windows of ( min of Delta inside the window )

A cell fires exactly when D > 0.10. The vertical axis is D for the real arm; the
horizontal axis is D for the independent-seed arm, which is the same statistic on a
relic that cannot be remembered - the rule's own false-positive calibration. The
threshold is drawn on both axes, so the four quadrants are the four things a cell
can say, and the diagonal says whether a cell beats its own null.

RIGHT - IS THE INSTRUMENT BLIND? A null on the left panel means nothing if the
estimator cannot see a spatial correlation at all. Each run's mean correlation
against its own previous epoch (vertical) against its mean correlation with an
unrelated run's relic (horizontal), for the memory index and for the positive
control that applies no rescale map. The control sits far up the diagonal: strong,
and equally strong for a stranger's relic, because what it sees is the drive both
runs share, not memory.

GATES ARE DRAWN, NOT HIDDEN. Section 7 says a condition whose median force-ceiling
share reaches 0.5 is measuring the 500-unit clamp rather than the physics, and
cannot support a positive. Those cells are drawn hollow and grey wherever they land.
A void run is drawn with a cross. Nothing is dropped: a reader sees every cell and
sees which ones the protocol will not let speak.

Usage:  python3 memory_prereg_figure.py [results_dir] [out.png]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import math
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

THRESHOLD = 0.10
RUN = 3
CEILING_BOUND = 0.5
MASS_TOL = 1e-3
MAX_UNDEFINED = 4


def delta(series, arm, control='twoback'):
    """per-epoch contrast, None where either side is undefined."""
    out = []
    for e in series:
        a, b = e.get(arm), e.get(control)
        if a is None or b is None or (isinstance(a, float) and math.isnan(a)) \
                or (isinstance(b, float) and math.isnan(b)):
            out.append(None)
        else:
            out.append(a - b)
    return out


def best_run_of(vals, run=RUN):
    """the decision statistic: best over windows of the window's minimum.

    A window containing an undefined epoch cannot be scored, exactly as
    memory_prereg_verdict.py's `fires` breaks its streak on one. Returns NaN when
    no window is scorable, so such a cell is visibly absent rather than plotted
    at a made-up value.
    """
    best = float('-inf')
    for i in range(len(vals) - run + 1):
        w = vals[i:i + run]
        if any(v is None for v in w):
            continue
        best = max(best, min(w))
    return best if best > float('-inf') else float('nan')


def cell_state(r):
    """the §7 gates, per run, computed the way memory_prereg_verdict.py computes them."""
    s = r['series']
    undefined = sum(1 for e in s if e.get('epoch', 0) >= 3 and e.get('twoback') is None)
    void = (r['mass']['max_relative_loss'] > MASS_TOL) or (undefined > MAX_UNDEFINED)
    ceil = [e['ceiling'] for e in r['page'] if e['ceiling'] is not None]
    ceil.sort()
    med = ceil[len(ceil) // 2] if ceil else float('nan')
    return void, med


def mean_of(series, key):
    v = [e[key] for e in series
         if e.get(key) is not None and not (isinstance(e[key], float) and math.isnan(e[key]))]
    return float(np.mean(v)) if v else float('nan')


def main(src, dst):
    runs = json.load(open(os.path.join(src, 'analysis.json')))

    # a condition is ceiling-bound if the median of its seeds' medians reaches 0.5
    by_cond = {}
    for r in runs:
        by_cond.setdefault((r['preset'], r['selfgrav'], r['gainloss']), []).append(r)
    bound = {}
    for key, group in by_cond.items():
        meds = sorted(cell_state(g)[1] for g in group)
        bound[key] = meds[len(meds) // 2] >= CEILING_BOUND

    sgs = sorted({r['selfgrav'] for r in runs})
    cmap = plt.get_cmap('viridis')
    col = {sg: cmap(0.08 + 0.78 * (i / max(1, len(sgs) - 1))) for i, sg in enumerate(sgs)}
    mark = {'spinchladni': 'o', 'default': '^'}
    GREY = '#9aa0a6'

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.2, 6.3), dpi=160)
    fig.patch.set_facecolor('white')

    # ---------------- LEFT: the decision statistic -------------------------------
    fired = fired_null = drawn = greyed = voided = 0
    xs, ys = [], []
    for r in runs:
        key = (r['preset'], r['selfgrav'], r['gainloss'])
        void, _ = cell_state(r)
        cb = bound[key]
        x = best_run_of(delta(r['series'], 'seed_null'))
        y = best_run_of(delta(r['series'], 'retained'))
        if math.isnan(x) or math.isnan(y):
            continue
        drawn += 1
        xs.append(x); ys.append(y)
        if y > THRESHOLD:
            fired += 1
        if x > THRESHOLD:
            fired_null += 1
        if void:
            voided += 1
            axA.scatter(x, y, s=90, marker='x', color='#c0392b', linewidth=1.8, zorder=4)
        elif cb:
            greyed += 1
            axA.scatter(x, y, s=64, marker=mark.get(r['preset'], 'o'), facecolor='none',
                        edgecolor=GREY, linewidth=1.5, alpha=0.95, zorder=3)
        else:
            axA.scatter(x, y, s=64, marker=mark.get(r['preset'], 'o'),
                        facecolor=col[r['selfgrav']], edgecolor=col[r['selfgrav']],
                        linewidth=1.4, alpha=0.95, zorder=3)

    lo = min(min(xs), min(ys), -0.05) if xs else -0.3
    hi = max(max(xs), max(ys), 0.15) if xs else 0.5
    pad = 0.07 * max(1e-6, hi - lo)
    lim = (lo - pad, hi + pad)
    axA.plot(lim, lim, color='#444', linewidth=1.0, linestyle='--', zorder=1)
    axA.axhline(THRESHOLD, color='#c0392b', linewidth=1.2, zorder=2)
    axA.axvline(THRESHOLD, color='#c0392b', linewidth=1.0, linestyle=':', zorder=2)
    axA.annotate('fires (criterion: three epochs in a row above 0.10)',
                 xy=(lim[0] + 0.03 * (lim[1] - lim[0]), THRESHOLD), xytext=(0.04, 0.93),
                 textcoords='axes fraction', fontsize=9, color='#c0392b',
                 arrowprops=dict(arrowstyle='->', color='#c0392b', linewidth=1.0))
    axA.set_xlim(lim); axA.set_ylim(lim)
    axA.set_aspect('equal', adjustable='box')
    axA.set_xlabel('same statistic against an independent seed\'s relic', fontsize=10.5)
    axA.set_ylabel('best three-in-a-row of  Retained − Two-back', fontsize=10.5)
    axA.set_title('The pre-registered criterion, one point per run', fontsize=11.5, pad=10)
    axA.grid(True, linewidth=0.4, alpha=0.35)

    # ---------------- RIGHT: is the estimator blind? -----------------------------
    lo2, hi2 = 1.0, -1.0
    for r in runs:
        cb = bound[(r['preset'], r['selfgrav'], r['gainloss'])]
        s = r['series']
        for own_k, null_k, filled in (('retained', 'seed_null', True),
                                      ('recurrence', 'recurrence_null', False)):
            x, y = mean_of(s, null_k), mean_of(s, own_k)
            if math.isnan(x) or math.isnan(y):
                continue
            lo2, hi2 = min(lo2, x, y), max(hi2, x, y)
            edge = GREY if cb else col[r['selfgrav']]
            axB.scatter(x, y, s=64, marker=mark.get(r['preset'], 'o'),
                        facecolor=(edge if filled else 'none'), edgecolor=edge,
                        linewidth=1.5, alpha=0.95, zorder=3)
    pad2 = 0.06 * max(1e-6, hi2 - lo2)
    lim2 = (lo2 - pad2, hi2 + pad2)
    axB.plot(lim2, lim2, color='#444', linewidth=1.0, linestyle='--', zorder=1)
    axB.annotate('an unrelated run predicts this one\nexactly as well as its own past',
                 xy=(lim2[0] + 0.55 * (lim2[1] - lim2[0]), lim2[0] + 0.55 * (lim2[1] - lim2[0])),
                 xytext=(0.05, 0.82), textcoords='axes fraction', fontsize=9.5, color='#333',
                 arrowprops=dict(arrowstyle='->', color='#666', linewidth=1.0))
    axB.set_xlim(lim2); axB.set_ylim(lim2)
    axB.set_aspect('equal', adjustable='box')
    axB.set_xlabel("mean correlation with an independent seed's relic", fontsize=10.5)
    axB.set_ylabel("mean correlation with the run's own previous epoch", fontsize=10.5)
    axB.set_title('Can the estimator see anything at all?', fontsize=11.5, pad=10)
    axB.grid(True, linewidth=0.4, alpha=0.35)

    for ax in (axA, axB):
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)

    handles = [plt.Line2D([], [], marker='o', linestyle='', markerfacecolor=col[sg],
                          markeredgecolor=col[sg], markersize=8, label=f'self-gravity {sg}')
               for sg in sgs]
    handles += [
        plt.Line2D([], [], marker='o', linestyle='', markerfacecolor='#555',
                   markeredgecolor='#555', markersize=8, label='Spinning Chladni preset'),
        plt.Line2D([], [], marker='^', linestyle='', markerfacecolor='#555',
                   markeredgecolor='#555', markersize=8, label='shipped-defaults preset'),
        plt.Line2D([], [], marker='o', linestyle='', markerfacecolor='none',
                   markeredgecolor=GREY, markersize=8,
                   label=f'ceiling-bound: cannot support a positive (§7)'),
        plt.Line2D([], [], marker='x', linestyle='', color='#c0392b', markersize=8,
                   label='void run (§7)'),
        plt.Line2D([], [], marker='o', linestyle='', markerfacecolor='none',
                   markeredgecolor='#555', markersize=8,
                   label='right panel, hollow: positive control (no rescale)'),
    ]
    fig.suptitle('Cross-epoch memory in the HALO resonance chamber · 4,194,304 particles · '
                 f'24 epochs · {len(runs)} of 60 cells\n'
                 'pre-registered 2026-09-02 before any confirmatory run existed',
                 fontsize=12, y=1.02)
    # tight_layout does not know about a figure-level legend, so the band it sits in is
    # reserved BEFORE the legend is placed and the legend is anchored inside that band.
    # Placing the legend first and calling tight_layout afterwards laid four rows of
    # swatches directly over both x-axis labels.
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.legend(handles=handles, fontsize=8.5, loc='lower center', frameon=False,
               ncol=4, bbox_to_anchor=(0.5, 0.005))
    fig.savefig(dst, bbox_inches='tight')
    print(f'wrote {dst}   ({drawn} cells drawn, {fired} fired, {fired_null} fired under the '
          f'seed null, {greyed} ceiling-bound, {voided} void)')


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        here, '..', '..', 'data', 'results', 'halo', 'memory_prereg'))
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        here, '..', '..', 'data', 'figures', 'halo_memory_prereg_2026-09-03.png')
    main(src, os.path.abspath(dst))
