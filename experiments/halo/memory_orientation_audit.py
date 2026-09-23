#!/usr/bin/env python3
"""memory_orientation_audit.py - is a frozen-scorer detection a property of a run, or of the
orientation of its triple?

The chamber's equations of motion are exactly symmetric under the point inversion
(p, v) -> (-p, -v) about the centre (every force term is odd under it, the drive included; the
page's Lab re-seats its probe particles along fixed lab directions in two fallback branches,
about 1e-3 off the mirror image), and the uniform-ball initial ensemble is invariant under it.
So a run whose 24 meshes are all inverted through the mesh centre is an equally probable
realisation of the same condition. Inverting one run of a triple leaves that run's own relic
correlations unchanged, but it changes the stranger entries of its neighbours' matrices (and
with them the E3 and E5b inputs), so the frozen scorer's eligibility, measurability, S, p and
detection can move. This script scores a directory in each of the four orientation classes of
every triple (as recorded; second seed inverted; third seed inverted; second and third
inverted, which is the first inverted up to one global inversion) with the unchanged frozen
scorer, and prints what moves. A design input for Ring 30
(analysis/2026-09-22_relic_intervention.md); numbers only.

    python3 experiments/halo/memory_orientation_audit.py DIR --json OUT [--work TMPDIR]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SCORER = os.path.join(HERE, 'memory_estimator_qualify.py')
MANIFEST = os.path.join(HERE, 'memory_pilot_manifest.py')
RECEIPT = os.path.join(REPO, 'data', 'results', 'halo', 'memory_estimator_qualification', 'synthetic.json')
CLASSES = {'as_recorded': (), 'second_inverted': (1,), 'third_inverted': (2,), 'second_and_third_inverted': (1, 2)}


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
            runs.setdefault((p['preset'], p['selfgrav'], p['gainloss']), []).append((p['seed'], fn, r))
    for k in runs:
        runs[k].sort()
    work = a.work or tempfile.mkdtemp(prefix='orientation_audit_')
    src = os.path.abspath(a.dir)
    out = {'source': os.path.relpath(src, REPO) if src.startswith(REPO + os.sep) else os.path.basename(src), 'classes': {}}
    for cname, inv in CLASSES.items():
        d = os.path.join(work, cname)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        for key, lst in runs.items():
            for idx, (seed, fn, r) in enumerate(lst):
                m = np.fromfile(os.path.join(a.dir, r['mesh_file']), dtype='<f4').reshape(r['mesh_count'], 32, 32, 32)
                if idx in inv:
                    m = np.ascontiguousarray(m[:, ::-1, ::-1, ::-1])
                m.astype('<f4').tofile(os.path.join(d, r['mesh_file']))
                with open(os.path.join(d, fn), 'w') as fh:
                    json.dump(r, fh)
        subprocess.run([sys.executable, MANIFEST, d, os.path.join(d, 'manifest.json')], check=True, capture_output=True)
        subprocess.run([sys.executable, SCORER, '--input-dir', d, '--manifest', os.path.join(d, 'manifest.json'),
                        '--synthetic-json', RECEIPT, '--output', os.path.join(d, 'qualification.json')],
                       check=True, capture_output=True)
        q = json.load(open(os.path.join(d, 'qualification.json')))
        rows = []
        for r in q['runs']:
            l1 = r['lag1']
            rows.append({'condition': r['condition'], 'seed': r['seed'], 'measurable': l1['measurable'],
                         'eligible': l1['eligible_epochs'], 'S': l1.get('own', {}).get('S'),
                         'p': l1.get('own', {}).get('p'), 'detected': l1.get('detected'),
                         'e5_unbalanced': l1['e5_unbalanced'], 'e5_collapse': l1['e5_collapse']})
        det = [f"sg{x['condition']['selfgrav']:g}/{x['seed']}" for x in rows if x['detected']]
        out['classes'][cname] = {'inverted_positions_in_each_triple': list(inv), 'verdict': q['verdict']['result'],
                                 'detected': det, 'runs': rows}
        print(f"{cname:28s} verdict {q['verdict']['result']:22s} detected {len(det)}: {', '.join(det) or '-'}")
    with open(a.json, 'w') as fh:
        json.dump(out, fh, indent=1)
    if not a.work:
        shutil.rmtree(work, ignore_errors=True)
    print(f'wrote {a.json}')


if __name__ == '__main__':
    main()
