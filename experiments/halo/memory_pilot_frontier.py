#!/usr/bin/env python3
"""memory_pilot_frontier.py - where a pilot arm's conditions sit against the two
gates that decide measurability.

Every number is read from two committed documents and nothing is recomputed
except one aggregation the frozen result does not print:

  scn_qualification.json  the frozen scorer's own result. Eligible epochs come
                          straight out of it. The x axis is the pre-registration's
                          D3 statistic - the median over epochs of the MINIMUM over
                          the three seeds of the predicted field's participation
                          ratio - which is what E2 tests. The result file's
                          per-run `pr_pred` is that run's OWN predicted field, which
                          is always the larger number; it is printed in the label so
                          the two readings can be told apart.
  scn_screens.json        the pilot's five screens. The y axis is A2, the
                          cross-seed template correlation with the deposit's Poisson
                          shot noise divided out, so that an E3 number bought by
                          degrading the estimate does not read as separation.

Only the lower-right box can hold a measurable condition: E2 needs at least 8
effective cells, and seeds count as separated only below A2 = 0.9. A2 above 1 is
not a possible correlation - it is the correction dividing by a residual that is
mostly noise - and those points are drawn hollow-hatched above the 1.0 rule.

Usage: python3 memory_pilot_frontier.py QUALIFICATION.json SCREENS.json OUT.png

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import json
import statistics as st
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

E2_CELLS = 8.0     # the frozen gate: effective cells in the compressed relic
A2_STRUCT = 0.9    # the pilot's screen: structural cross-seed template correlation


def series(run, field):
    out = []
    for e in run['epochs']:
        v = e.get(field)
        out.append(v if isinstance(v, (int, float)) else (v[0] if isinstance(v, list) and v else None))
    return out


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    qual = json.load(open(sys.argv[1]))
    screens = json.load(open(sys.argv[2]))
    out = sys.argv[3]

    by = {}
    for r in qual['runs']:
        c = r['condition']
        key = f"{c['preset']}_sg{c['selfgrav']:g}_gl{c['gainloss']:g}"
        by.setdefault(key, []).append(r)
    sc = {s['condition']: s for s in screens['screens']}

    fig, ax = plt.subplots(figsize=(9.6, 6.4))
    ax.fill_between([E2_CELLS, 400], -0.14, A2_STRUCT, color='#e8f5e9', zorder=0)
    ax.text(170, -0.05, 'the only box a measurable\ncondition can occupy', color='#2e7d32',
            fontsize=9, ha='center', va='bottom', zorder=2)
    ax.axhline(A2_STRUCT, color='#c62828', lw=1.2, ls='--', zorder=1)
    ax.axvline(E2_CELLS, color='#c62828', lw=1.2, ls='--', zorder=1)
    ax.axhline(1.0, color='#616161', lw=0.9, ls=':', zorder=1)
    ax.text(1.35, 0.74, 'A2: seeds count as separated\nonly below 0.9', color='#c62828', fontsize=8)
    ax.text(1.32, 0.52, 'above this line A2 is not a possible correlation:\n'
                         'the shot-noise correction is dividing by noise',
            color='#616161', fontsize=7.5)
    ax.text(8.55, -0.11, 'E2: the compressed relic needs 8 effective cells',
            color='#c62828', fontsize=8, rotation=90, va='bottom')

    # Two pairs of conditions land almost on top of each other and two sit against a
    # gate line; nudge and align their labels by hand rather than let the picture lie
    # about how many points there are or which side of a gate they fall on.
    NUDGE = {'goldstair_sg0.15_gl0': (11, 14), 'goldstair_sg0.3_gl0': (11, -40),
             'hardprint_sg0.15_gl0': (-12, 16), 'hardprint_sg0.3_gl0': (-12, -34),
             'stillspindle_sg0.15_gl0': (11, 6), 'spinchladni_sg0.15_gl0': (-16, -38),
             'spinchladni_sg0.3_gl0': (11, 6)}
    ALIGN = {'hardprint_sg0.15_gl0': 'right', 'hardprint_sg0.3_gl0': 'right',
             'spinchladni_sg0.15_gl0': 'right'}

    for cond, runs in sorted(by.items()):
        s = sc.get(cond, {})
        pr = [series(r, 'pr_pred') for r in runs]
        n = min(len(p) for p in pr)
        mins = [min(p[i] for p in pr) for i in range(n)
                if all(isinstance(p[i], (int, float)) for p in pr)]
        x = st.median(mins)
        own = st.median([st.median([v for v in p if isinstance(v, (int, float))]) for p in pr])
        y = s.get('A2_tstruct_median', float('nan'))
        elig = [r['lag1']['eligible_epochs'] for r in runs]
        anchor = cond.startswith('spinchladni')
        struck = bool(s.get('struck_by'))
        colour = '#1565c0' if anchor else ('#ef6c00' if struck else '#2e7d32')
        ax.scatter([x], [y], s=210, marker='D' if anchor else 'o',
                   facecolor='none' if struck else colour, edgecolor=colour,
                   linewidths=2.0, hatch='///' if y > 1.0 else None, zorder=4)
        ax.annotate(f"{cond.replace('_gl0', '').replace('_sg', ' sg')}\n"
                    f"elig {'/'.join(map(str, elig))} of 22 · own {own:.1f}",
                    (x, y), textcoords='offset points', xytext=NUDGE.get(cond, (10, 8)),
                    fontsize=8, color=colour, zorder=5, ha=ALIGN.get(cond, 'left'))

    ax.set_xscale('log')
    ax.set_xlim(1.2, 400)
    ax.set_ylim(-0.14, 1.22)
    ax.set_xlabel('effective cells in the compressed relic — D3, the median of the per-epoch minimum '
                  'over the three seeds\n("own" in each label is that condition\'s median own-field value, '
                  'the number the diagnostic prints)')
    ax.set_ylabel('A2: cross-seed template correlation, shot noise removed')
    ax.set_title('HALO measurability pilot, 21 runs at 4,194,304 particles: no condition is measurable\n'
                 'diamonds are the two anchors, hollow markers were struck by a screen, hatched markers '
                 'have an A2 above 1',
                 fontsize=10)
    ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print('wrote', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
