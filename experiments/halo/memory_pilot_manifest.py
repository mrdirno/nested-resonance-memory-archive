#!/usr/bin/env python3
"""memory_pilot_manifest.py - write the input manifest the frozen qualification
script checks with --manifest.

The frozen script (memory_estimator_qualify.py, check_manifest) reads a JSON
document with a "files" list of {"file", "sha256", "bytes"} and reports
"inputs unverified" unless every entry matches a file it actually loaded.

What this manifest is and is not: it is written from the recorded files
immediately after a pilot arm finishes and before that arm is scored, so it
detects a file that changed, was truncated or was swapped BETWEEN recording and
scoring. It is a self-attestation of one sitting, not an independent
preservation step like the recorded grid's input-provenance audit, and it
cannot detect an error made while recording.

Usage:
  python3 memory_pilot_manifest.py INPUT_DIR OUT.json [--note "text"]

Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0
"""
import argparse
import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input_dir')
    ap.add_argument('output')
    ap.add_argument('--note', default='')
    args = ap.parse_args()

    entries, runs = [], 0
    for fn in sorted(os.listdir(args.input_dir)):
        if not (fn.endswith('.json') or fn.endswith('.mesh.f32')):
            continue
        path = os.path.join(args.input_dir, fn)
        if not os.path.isfile(path):
            continue
        if fn.endswith('.json'):
            try:
                with open(path) as fh:
                    head = json.load(fh)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
                continue
            runs += 1
        entries.append({'file': fn, 'sha256': sha256_file(path),
                        'bytes': os.path.getsize(path)})

    if not runs:
        sys.exit(f'no halo-memory-prereg/1 runs in {args.input_dir}')

    doc = {'schema': 'halo-memory-pilot-manifest/1',
           'author': 'Aldrin Payopay',
           'input_dir': os.path.relpath(os.path.abspath(args.input_dir),
                                        os.path.dirname(os.path.abspath(__file__))),
           'runs': runs, 'note': args.note, 'files': entries}
    with open(args.output, 'w') as fh:
        json.dump(doc, fh, indent=1)
    print(f'{args.output}: {runs} runs, {len(entries)} files, '
          f'{sum(e["bytes"] for e in entries)} bytes')


if __name__ == '__main__':
    main()
