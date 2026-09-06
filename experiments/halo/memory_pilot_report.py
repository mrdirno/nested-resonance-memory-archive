#!/usr/bin/env python3
"""memory_pilot_report.py - the measurability diagnostic for a pilot arm.

Reads one or more qualification JSON documents written by the FROZEN script
(memory_estimator_qualify.py, schema halo-memory-estimator-qualification/2) and
reports, per condition and per run, the numbers that decide whether the frozen
estimator can measure that condition at all. It computes nothing new: every
number here is read out of the frozen script's own result, so the report cannot
change a verdict. Its only job is to make the verdict readable and to count the
pilot's metric.

The metric: a condition is measurable when all three of its runs are measurable
(at least 12 eligible epochs of the 22 scored, and passing E5 and E5b). The
count of measurable conditions across every arm is the pilot's headline number.

Usage:
  python3 memory_pilot_report.py ARM.json [ARM2.json ...] [--json OUT.json]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import json
import statistics as st


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return st.median(xs) if xs else float('nan')


def flat(v):
    if isinstance(v, list):
        return [x for x in v if isinstance(x, (int, float))]
    return [v] if isinstance(v, (int, float)) else []


def arm_rows(doc, arm_name):
    rows = []
    for r in doc['runs']:
        c = r['condition']
        key = f"{c['preset']}_sg{c['selfgrav']:g}_gl{c['gainloss']:g}"
        lag1 = r['lag1']
        tx, pr_pred, pr_cur, mass = [], [], [], []
        for e in r['epochs']:
            tx += [abs(x) for x in flat(e.get('tmpl_xcorr'))]
            pr_pred += flat(e.get('pr_pred'))
            pr_cur += flat(e.get('pr_cur'))
            mass += flat(e.get('mass_b2'))
        rows.append({
            'arm': arm_name, 'condition': key, 'seed': r['seed'], 'tag': r.get('tag'),
            'eligible_epochs': lag1['eligible_epochs'],
            'fail_e1': lag1['gate_fail_counts']['e1'], 'fail_e2': lag1['gate_fail_counts']['e2'],
            'fail_e3': lag1['gate_fail_counts']['e3'], 'fail_e4': lag1['gate_fail_counts']['e4'],
            'e5_collapse': lag1['e5_collapse'], 'e5_unbalanced': lag1['e5_unbalanced'],
            'seed_null_values': lag1['seed_null_values'],
            'measurable': lag1['measurable'],
            'median_template_xcorr': med(tx), 'median_pr_predicted': med(pr_pred),
            'median_pr_current': med(pr_cur), 'median_mass_b2': med(mass),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arms', nargs='+', help='qualification JSON per arm; the file name is the arm label')
    ap.add_argument('--json', help='write the whole report as JSON here')
    args = ap.parse_args()

    all_rows, arms = [], []
    for path in args.arms:
        with open(path) as fh:
            doc = json.load(fh)
        name = path.split('/')[-1].replace('.json', '')
        v = doc['verdict']
        arms.append({'arm': name, 'file': path, 'result': v['result'],
                     'measurable_runs': v['F5_support']['measurable_runs'],
                     'runs': len(doc['runs']),
                     'measurable_conditions': v['F5_support']['measurable_conditions'],
                     'detected_runs': doc.get('detected_runs_main', []),
                     'below_floor_runs': doc.get('below_floor_runs_main', []),
                     'scored_epochs': doc.get('scored_epochs')})
        all_rows += arm_rows(doc, name)

    hdr = (f"{'arm':22s} {'condition':24s} {'seed':>6s} {'elig':>4s} {'E1':>3s} {'E2':>3s} {'E3':>3s} "
           f"{'E5c':>5s} {'E5b':>5s} {'meas':>5s} {'tmplX':>7s} {'PRpred':>7s} {'massB2':>7s}")
    print(hdr)
    print('-' * len(hdr))
    for r in all_rows:
        print(f"{r['arm'][:22]:22s} {r['condition']:24s} {r['seed']:6d} {r['eligible_epochs']:4d} "
              f"{r['fail_e1']:3d} {r['fail_e2']:3d} {r['fail_e3']:3d} "
              f"{str(r['e5_collapse']):>5s} {str(r['e5_unbalanced']):>5s} {str(r['measurable']):>5s} "
              f"{r['median_template_xcorr']:7.4f} {r['median_pr_predicted']:7.2f} {r['median_mass_b2']:7.4f}")

    n_cond = sum(len(a['measurable_conditions']) for a in arms)
    n_runs = sum(a['measurable_runs'] for a in arms)
    total_runs = sum(a['runs'] for a in arms)
    print()
    for a in arms:
        print(f"{a['arm']}: {a['result']} | measurable runs {a['measurable_runs']}/{a['runs']} | "
              f"measurable conditions {len(a['measurable_conditions'])} | detected {len(a['detected_runs'])}")
    print(f"\nPILOT METRIC: {n_cond} measurable conditions across {len(arms)} arms "
          f"({n_runs}/{total_runs} measurable runs). F5 needs 3 conditions; F3 needs 6 runs.")

    if args.json:
        with open(args.json, 'w') as fh:
            json.dump({'schema': 'halo-memory-pilot-report/1', 'author': 'Aldrin Payopay',
                       'arms': arms, 'rows': all_rows,
                       'measurable_conditions_total': n_cond,
                       'measurable_runs_total': n_runs, 'runs_total': total_runs}, fh, indent=1)
        print(f'wrote {args.json}')


if __name__ == '__main__':
    main()
