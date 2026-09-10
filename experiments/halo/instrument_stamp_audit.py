#!/usr/bin/env python3
"""instrument_stamp_audit.py - what the 81 recorded HALO memory runs can say about
the instrument that made them, and what they cannot.

Ring 17 asked what a run record must carry to be regenerable, having spent seven
controlled re-runs recovering one build. This audit answers it from the records
themselves. It reports three things and decides none of them:

  1. THE DESIGNED PIN. instrument_identity.sim_digest over the four page revisions
     of ring 17's labelled set, scored against the partition that set established.
  2. THE ACCIDENTAL PIN. tests/halo/memory_prereg_run.js:170 hardcodes a 22-name
     csv_head while csv_rows is read live from the page. Ring 13 widened the page's
     lab-log row from 22 to 28 fields and the literal did not move, so every record
     carries the width of the instrument that wrote it - a two-class fingerprint
     nobody designed, and a header that mislabels six columns in the newer arm.
  3. WHAT THE RECORD CANNOT DO. Tags that appear in both arms with byte-identical
     recorded parameters and different mesh hashes: the record is not a sufficient
     key for its own output.

Stdlib only, no GPU, no browser. Author: Aldrin Payopay. GPL-3.0-only.
"""
import collections
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))   # experiments/halo -> experiments -> repo root
sys.path.insert(0, HERE)
import instrument_identity as ii  # noqa: E402

ARMS = {
    'recorded_grid': 'data/results/halo/memory_prereg',
    'measurability_pilot': 'data/results/halo/memory_pilot/scn',
}
# Files in memory_prereg/ that are analysis outputs, not runs.
NOT_RUNS = {'analysis.json', 'artefact.json', 'nullrate.json', 'power.json',
            'robustness.json', 'rotation.json', 'verdict.json'}


def load_runs(rel):
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, rel, '*.json'))):
        if os.path.basename(p) in NOT_RUNS:
            continue
        d = json.load(open(p))
        if d.get('schema') != 'halo-memory-prereg/1':
            continue
        out.append((os.path.basename(p), d))
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    repo = REPO
    # --- 1. the designed pin, scored on ring 17's labelled set -------------
    labelled = {}
    for rev, cls in ii.LABELLED.items():
        html = ii.from_git(rev, repo)
        d = ii.digests(html)
        labelled[rev] = {'true_class': cls, 'sim_digest': d['sim_digest'],
                         'whole_file_sha256': d['whole_file_sha256'],
                         'glsl_chunks': d['glsl_chunks'], 'glsl_bytes': d['glsl_bytes']}
    by_sim = collections.defaultdict(list)
    by_sha = collections.defaultdict(list)
    for rev, v in labelled.items():
        by_sim[v['sim_digest']].append(rev)
        by_sha[v['whole_file_sha256']].append(rev)
    true_partition = collections.defaultdict(list)
    for rev, v in labelled.items():
        true_partition[v['true_class']].append(rev)
    sim_ok = sorted(map(sorted, by_sim.values())) == sorted(map(sorted, true_partition.values()))

    # --- 2. the accidental pin, over every record --------------------------
    arms = {}
    tag_index = collections.defaultdict(list)
    for arm, rel in ARMS.items():
        runs = load_runs(rel)
        widths = collections.Counter()
        heads = collections.Counter()
        rows_total = 0
        for name, d in runs:
            heads[d.get('csv_head', '')] += 1
            for r in d.get('csv_rows', []):
                widths[len(r.split(',')) if isinstance(r, str) else len(r)] += 1
                rows_total += 1
            mesh = os.path.join(repo, rel, d['mesh_file'])
            tag_index[d['tag']].append({
                'arm': arm,
                'mesh_sha256': sha256_file(mesh) if os.path.exists(mesh) else None,
                'params': d['params'],
                'applied_cosmos': d['applied']['cosmos'],
            })
        head_names = max(heads, key=heads.get).split(',')
        arms[arm] = {
            'runs': len(runs),
            'csv_head_names': len(head_names),
            'distinct_csv_head': len(heads),
            'csv_row_widths': dict(widths),
            'csv_rows_total': rows_total,
            'header_describes_rows': set(widths) == {len(head_names)},
            'unnamed_columns': (max(widths) - len(head_names)) if widths else None,
        }

    # --- 3. what the record cannot do --------------------------------------
    collisions = []
    for tag, entries in sorted(tag_index.items()):
        if len(entries) < 2:
            continue
        meshes = {e['mesh_sha256'] for e in entries}
        params_same = all(e['params'] == entries[0]['params'] for e in entries)
        cosmos_same = all(e['applied_cosmos'] == entries[0]['applied_cosmos'] for e in entries)
        collisions.append({
            'tag': tag,
            'arms': [e['arm'] for e in entries],
            'recorded_params_identical': params_same and cosmos_same,
            'mesh_sha256': sorted(m[:16] for m in meshes if m),
            'outputs_differ': len(meshes) > 1,
        })

    receipt = {
        'schema': 'halo-instrument-identity/1',
        'author': 'Aldrin Payopay',
        'licence': 'GPL-3.0-only',
        'question': ("Ring 17: what must a run record carry - starting with the sha256 of the "
                     "instrument that drove it - for a grid to be regenerable at all?"),
        'script_sha256': sha256_file(os.path.join(HERE, 'instrument_identity.py')),
        'audit_sha256': sha256_file(os.path.abspath(__file__)),
        'page': ii.PAGE_REL,
        'designed_pin': {
            'labelled_set': 'data/results/halo/memory_pilot/reproduction_probe.json',
            'revisions': labelled,
            'sim_digest_classes': {k: sorted(v) for k, v in by_sim.items()},
            'whole_file_sha256_classes': {k[:16]: sorted(v) for k, v in by_sha.items()},
            'sim_digest_classes_n': len(by_sim),
            'whole_file_classes_n': len(by_sha),
            'true_classes_n': len(true_partition),
            'sim_digest_reproduces_partition': sim_ok,
            'whole_file_reproduces_partition': len(by_sha) == len(true_partition),
        },
        'accidental_pin': {
            'cause': ('tests/halo/memory_prereg_run.js:170 hardcodes csv_head as a 22-name '
                      'string literal; csv_rows is read live from window.__probe.lab.log. '
                      'Ring 13 (122d0a57) widened the page row from 22 to 28 fields.'),
            'arms': arms,
        },
        'record_is_not_a_key': {
            'tags_in_both_arms': len(collisions),
            'all_have_identical_recorded_params': all(c['recorded_params_identical'] for c in collisions),
            'all_have_different_outputs': all(c['outputs_differ'] for c in collisions),
            'collisions': collisions,
        },
        'what_this_does_not_license': [
            'It does not say the two classes differ by any particular amount, only that they differ.',
            'The class-B stamp rests on ONE tag reproducing byte for byte in ring 17 s receipt; '
            'the other 59 recorded runs are stamped by shared provenance, not by re-running them.',
            'sim_digest covers the GPU program, the named physics constants, the driven presets '
            'and DEFAULTS. A JavaScript-only change to the tick loop does not move it.',
            'Nothing here measures memory, and nothing here changes any scored number.',
        ],
    }
    out = os.path.join(repo, 'data/results/halo/instrument_identity.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(receipt, f, indent=1, sort_keys=False)
        f.write('\n')
    print(f'wrote {out}')
    print(f"  designed pin: sim_digest {len(by_sim)} classes (want {len(true_partition)}) "
          f"-> {'PASS' if sim_ok else 'FAIL'}; whole-file sha256 {len(by_sha)} classes")
    for arm, a in arms.items():
        print(f"  {arm}: {a['runs']} runs, head names {a['csv_head_names']}, "
              f"row widths {a['csv_row_widths']}, unnamed columns {a['unnamed_columns']}")
    print(f"  tags in both arms: {len(collisions)}; identical recorded params: "
          f"{all(c['recorded_params_identical'] for c in collisions)}; "
          f"outputs differ: {all(c['outputs_differ'] for c in collisions)}")


if __name__ == '__main__':
    main()
