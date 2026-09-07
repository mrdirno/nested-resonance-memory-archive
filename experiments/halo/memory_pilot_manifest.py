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

    # Only files the scorer will actually load: a run JSON of the right schema, and
    # the mesh that JSON names. Hashing anything else is worse than useless. The
    # scorer verifies the manifest by matching it against the files it loaded, so a
    # stray mesh - one left by a crashed run, or by an arm that was re-run under a
    # different name - would appear in the manifest, never be loaded, and turn the
    # result into "inputs unverified". That verdict is then easy to miss, because
    # the script reports support before it reports inputs.
    entries, runs, extra = [], 0, []
    keep = {}
    for fn in sorted(os.listdir(args.input_dir)):
        path = os.path.join(args.input_dir, fn)
        if not os.path.isfile(path):
            continue
        if fn.endswith('.json'):
            try:
                with open(path) as fh:
                    head = json.load(fh)
            except (json.JSONDecodeError, UnicodeDecodeError):
                extra.append(fn)
                continue
            if not isinstance(head, dict) or head.get('schema') != 'halo-memory-prereg/1':
                extra.append(fn)
                continue
            mesh = head.get('mesh_file')
            if not mesh or not os.path.isfile(os.path.join(args.input_dir, mesh)):
                sys.exit(f'{fn} names mesh {mesh!r}, which is not in {args.input_dir}')
            runs += 1
            keep[fn] = None
            keep[mesh] = None
        elif not fn.endswith('.mesh.f32'):
            extra.append(fn)
    for fn in sorted(os.listdir(args.input_dir)):
        if fn.endswith('.mesh.f32') and fn not in keep:
            extra.append(fn)
    for fn in sorted(keep):
        path = os.path.join(args.input_dir, fn)
        entries.append({'file': fn, 'sha256': sha256_file(path),
                        'bytes': os.path.getsize(path)})
    if extra:
        print(f'not in the manifest ({len(extra)} file(s) the scorer will not load): '
              + ', '.join(extra), file=sys.stderr)

    if not runs:
        sys.exit(f'no halo-memory-prereg/1 runs in {args.input_dir}')

    doc = {'schema': 'halo-memory-pilot-manifest/1',
           'author': 'Aldrin Payopay',
           'input_dir': os.path.relpath(os.path.abspath(args.input_dir),
                                        os.path.dirname(os.path.abspath(__file__))),
           'runs': runs, 'note': args.note,
           'not_manifested': extra, 'files': entries}
    with open(args.output, 'w') as fh:
        json.dump(doc, fh, indent=1)
    print(f'{args.output}: {runs} runs, {len(entries)} files, '
          f'{sum(e["bytes"] for e in entries)} bytes')


if __name__ == '__main__':
    main()
