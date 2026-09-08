#!/usr/bin/env python3
"""memory_pilot_reproduction.py - can a recorded run be reproduced today?

The measurability pilot re-ran two conditions that the recorded 60-run grid also
contains, under byte-identical recorded parameters. They did not come back the
same. This script writes the receipt for the search that followed: each control
is one run of the SAME tag under one changed layer, and the question is which
layer, if any, reproduces the recorded bytes.

It computes nothing about memory and touches no pilot result. Per labelled mesh
it records the sha256, and against the recorded mesh the per-epoch Pearson
correlation of the full 32^3 density, so that "different" is a number and not an
impression.

Usage:
  python3 memory_pilot_reproduction.py OUT.json LABEL=PATH [LABEL=PATH ...] \
      --recorded PATH [--note TEXT]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import hashlib
import json
import os

import numpy as np

N = 32


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    m = np.fromfile(path, dtype='<f4')
    if m.size % (N ** 3):
        raise SystemExit(f'{path}: {m.size} floats is not a whole number of 32^3 meshes')
    return m.reshape(-1, N ** 3).astype(np.float64)


def pearson(a, b):
    if a.std() == 0 or b.std() == 0:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('output')
    ap.add_argument('controls', nargs='+', help='LABEL=PATH for each control mesh')
    ap.add_argument('--recorded', required=True, help='the recorded grid mesh of the same tag')
    ap.add_argument('--note', default='')
    args = ap.parse_args()

    rec = load(args.recorded)
    out = {'schema': 'halo-memory-pilot-reproduction/1', 'author': 'Aldrin Payopay',
           'note': args.note,
           'recorded': {'file': os.path.basename(args.recorded), 'path': args.recorded,
                        'sha256': sha256_file(args.recorded), 'epochs': int(rec.shape[0])},
           'controls': []}

    for spec in args.controls:
        if '=' not in spec:
            raise SystemExit(f'expected LABEL=PATH, got {spec!r}')
        label, path = spec.split('=', 1)
        m = load(path)
        n = min(m.shape[0], rec.shape[0])
        corr = [pearson(rec[k], m[k]) for k in range(n)]
        out['controls'].append({
            'label': label, 'file': os.path.basename(path),
            'sha256': sha256_file(path), 'epochs': int(m.shape[0]),
            'identical_to_recorded': bool(m.shape == rec.shape and np.array_equal(m, rec)),
            'per_epoch_pearson_vs_recorded': [round(c, 6) for c in corr],
            'min_pearson_vs_recorded': round(float(np.nanmin(corr)), 6),
            'last_epoch_pearson_vs_recorded': round(float(corr[-1]), 6),
        })

    shas = {c['sha256'] for c in out['controls']}
    out['controls_agree_with_each_other'] = len(shas) == 1
    out['any_control_reproduces_recorded'] = any(c['identical_to_recorded'] for c in out['controls'])

    with open(args.output, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"wrote {args.output}: {len(out['controls'])} controls, "
          f"{len(shas)} distinct output hash{'es' if len(shas) != 1 else ''}, "
          f"reproduces recorded: {out['any_control_reproduces_recorded']}")
    for c in out['controls']:
        print(f"  {c['label']:34s} {c['sha256'][:16]}  min r {c['min_pearson_vs_recorded']:8.4f}  "
              f"last r {c['last_epoch_pearson_vs_recorded']:8.4f}")


if __name__ == '__main__':
    main()
