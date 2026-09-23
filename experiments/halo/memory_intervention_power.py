#!/usr/bin/env python3
"""memory_intervention_power.py - how often can the Ring 30 frame rule decide at all? A design
input computed on the committed Ring 29 control before any intervention run existed
(analysis/2026-09-22_relic_intervention.md, "Decision rule").

The chamber is exactly symmetric under the point inversion, so a run with all 24 meshes
inverted is an equally probable realisation (memory_orientation_audit.py). A triple has four
orientation classes (as recorded; second, third, or second and third seed inverted; the first
inverted is the last up to one global inversion), and the frozen scorer's stranger null makes
each condition's outcome depend on its triple's class alone. Three conditions give 4^3 = 64
equally valid configurations of the same bytes. For each class this script scores the lab frame
and the inverted frame (memory_intervention_frames.py --op point) with the unchanged frozen
scorer, labels every condition with the registered rule (memory_intervention_decide.preference:
a signature is d = S(frame) - S(lab) past +/-0.04 for a run measurable in both frames), with the
draft's gate (a signature also needed a detection without the autocorrelation caveat or an F4
violation in the winning frame) and with a detection alone, and counts the configurations in
which each rule reaches a preference, and which. It also counts the configurations in which
every condition has three measurable runs in the lab frame while F1-F4 pass in every class
involved - the per-class basis of a "qualified" verdict (F5 counts measurable conditions; F3's
median and F4's violations aggregate across conditions, and pass in every class here).

Numbers only; nothing here is scored as a result.

    python3 experiments/halo/memory_intervention_power.py DIR --json OUT [--work TMPDIR]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, itertools, json, os, shutil, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import memory_intervention_decide as decide  # noqa: E402

SCORER = os.path.join(HERE, 'memory_estimator_qualify.py')
MANIFEST = os.path.join(HERE, 'memory_pilot_manifest.py')
FRAMES = os.path.join(HERE, 'memory_intervention_frames.py')
RECEIPT = os.path.join(REPO, 'data', 'results', 'halo', 'memory_estimator_qualification', 'synthetic.json')
CLASSES = {'as_recorded': (), 'second_inverted': (1,), 'third_inverted': (2,), 'second_and_third_inverted': (1, 2)}


def score(d):
    subprocess.run([sys.executable, MANIFEST, d, os.path.join(d, 'manifest.json')], check=True, capture_output=True)
    subprocess.run([sys.executable, SCORER, '--input-dir', d, '--manifest', os.path.join(d, 'manifest.json'),
                    '--synthetic-json', RECEIPT, '--output', os.path.join(d, 'qualification.json')],
                   check=True, capture_output=True)
    return os.path.join(d, 'qualification.json')


def gated(lab_runs, frame_runs, strict=True):
    """The draft's detection-gated signature (strict: also no caveat, no F4 violation), for comparison only."""
    ok = (lambda x: x['measurable'] and x['detected'] and not x['caveat'] and not x['f4_violation']) if strict \
        else (lambda x: x['measurable'] and x['detected'])
    cond = {}
    for sg in sorted({k[0] for k in lab_runs}):
        sigs = []
        for k in sorted(k for k in lab_runs if k[0] == sg):
            a, b = lab_runs[k], frame_runs.get(k)
            if b is None or not (a['measurable'] and b['measurable']):
                continue
            d = b['S'] - a['S']
            sigs.append('X' if (ok(b) and d >= decide.MARGIN) else ('L' if (ok(a) and d <= -decide.MARGIN) else '-'))
        x, l = 'X' in sigs, 'L' in sigs
        cond[sg] = 'mixed' if (x and l) else ('X' if x else ('L' if l else 'none'))
    return cond


def phi(labels):
    nx, nl, nm = labels.count('X'), labels.count('L'), labels.count('mixed')
    return 'X' if (nx >= 2 and nl == 0 and nm == 0) else ('L' if (nl >= 2 and nx == 0 and nm == 0) else 'none')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('--json', required=True)
    ap.add_argument('--work', default=None)
    a = ap.parse_args()
    runs = {}
    for fn in sorted(os.listdir(a.dir)):
        if not fn.endswith('.json'):
            continue
        try:
            r = json.load(open(os.path.join(a.dir, fn)))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(r, dict) and r.get('schema') == 'halo-memory-prereg/1':
            p = r['params']
            runs.setdefault(float(p['selfgrav']), []).append((p['seed'], fn, r))
    for k in runs:
        runs[k].sort()
    conds = sorted(runs)
    work = a.work or tempfile.mkdtemp(prefix='ring30_power_')
    src = os.path.abspath(a.dir)
    out = {'source': os.path.relpath(src, REPO) if src.startswith(REPO + os.sep) else os.path.basename(src),
           'margin': decide.MARGIN, 'classes': {}}
    reg, gat, det, meas, f4ok = {}, {}, {}, {}, {}
    for cname, inv in CLASSES.items():
        lab = os.path.join(work, cname, 'lab')
        shutil.rmtree(os.path.join(work, cname), ignore_errors=True)
        os.makedirs(lab)
        for sg, lst in runs.items():
            for idx, (seed, fn, r) in enumerate(lst):
                m = np.fromfile(os.path.join(a.dir, r['mesh_file']), dtype='<f4').reshape(r['mesh_count'], 32, 32, 32)
                if idx in inv:
                    m = np.ascontiguousarray(m[:, ::-1, ::-1, ::-1])
                m.astype('<f4').tofile(os.path.join(lab, r['mesh_file']))
                with open(os.path.join(lab, fn), 'w') as fh:
                    json.dump(r, fh)
        pi = os.path.join(work, cname, 'pi')
        subprocess.run([sys.executable, FRAMES, lab, '--op', 'point', '--out', pi], check=True, capture_output=True)
        qL, qP = score(lab), score(pi)
        L, vL = decide.load(qL)
        P, vP = decide.load(qP)
        per_run, cond, ph = decide.preference(L, P)
        g, g1 = gated(L, P), gated(L, P, strict=False)
        ql = json.load(open(qL))
        for sg in conds:
            reg[(cname, sg)] = cond[sg]
            gat[(cname, sg)] = g[sg]
            det[(cname, sg)] = g1[sg]
            meas[(cname, sg)] = all(L[k]['measurable'] for k in L if k[0] == sg)
        v = ql['verdict']
        f4ok[cname] = all(v[f]['pass'] for f in ('F1_identity', 'F2_false_positives', 'F4_robustness')) and \
            bool(v['F3_recovery'].get('evaluable')) and bool(v['F3_recovery'].get('pass'))
        out['classes'][cname] = {
            'inverted_positions_in_each_triple': list(inv), 'lab_verdict': vL['result'], 'pi_verdict': vP['result'],
            'registered_rule': {f'sg{sg:g}': ('Pi' if c == 'X' else c) for sg, c in cond.items()},
            'detection_gated_variant': {f'sg{sg:g}': ('Pi' if c == 'X' else c) for sg, c in g.items()},
            'detection_alone_variant': {f'sg{sg:g}': ('Pi' if c == 'X' else c) for sg, c in g1.items()},
            'lab_F1_F4': {f: v[f].get('pass') for f in ('F1_identity', 'F2_false_positives', 'F3_recovery', 'F4_robustness')},
            'runs': [{'run': L[k]['label'], 'measurable_lab': L[k]['measurable'], 'measurable_pi': P.get(k, {}).get('measurable'),
                      'S_lab': L[k]['S'], 'S_pi': P.get(k, {}).get('S'), 'detected_lab': L[k]['detected'],
                      'detected_pi': P.get(k, {}).get('detected'), 'd': per_run[k]['d'], 'signature': per_run[k]['signature']}
                     for k in sorted(L)]}
        print(f"{cname:27s} lab {vL['result']:20s} registered {[reg[(cname, sg)] for sg in conds]}  gated {[gat[(cname, sg)] for sg in conds]}")
    counts = {}
    for name, lab in (('registered_rule', reg), ('detection_gated_variant', gat), ('detection_alone_variant', det)):
        tally = {'L': 0, 'Pi': 0, 'none': 0}
        for combo in itertools.product(CLASSES, repeat=len(conds)):
            p = phi([lab[(c, sg)] for c, sg in zip(combo, conds)])
            tally['Pi' if p == 'X' else p] += 1
        counts[name] = tally
    qual = sum(all(meas[(c, sg)] for c, sg in zip(combo, conds)) and all(f4ok[c] for c in combo)
               for combo in itertools.product(CLASSES, repeat=len(conds)))
    out['configurations'] = len(CLASSES) ** len(conds)
    out['preference_counts'] = counts
    out['lab_every_condition_measurable_with_F1_F4_passing_in_every_class'] = qual
    with open(a.json, 'w') as fh:
        json.dump(out, fh, indent=1)
    if not a.work:
        shutil.rmtree(work, ignore_errors=True)
    print(f"over {out['configurations']} configurations: registered {counts['registered_rule']}, "
          f"draft gate {counts['detection_gated_variant']}, detection alone {counts['detection_alone_variant']}; "
          f"every condition measurable with F1-F4 passing {qual}")
    print(f'wrote {a.json}')


if __name__ == '__main__':
    main()
