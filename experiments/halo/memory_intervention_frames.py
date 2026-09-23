#!/usr/bin/env python3
"""memory_intervention_frames.py - the carried frame of an intervened run, for the frozen
scorer to read.

Ring 30 (analysis/2026-09-22_relic_intervention.md) applies an exact cube operation T to
the carried state at every boundary k = 1..23, right after mesh k is exported. Mesh j
(0-based, j = 0..23) has therefore had j interventions before it was written. The carried
frame undoes them: D_j = T^j C_j, and because every T used here is an involution (T^2 = 1)
that is T applied to the odd-indexed meshes. The frozen scorer, run unchanged on a
directory of D-files, then correlates each current mesh with the T-image of the relic it
compares against, for own and stranger entries alike: the cube operations about the mesh
centre 15.5 commute exactly with the scorer's x2 block sum, its B2 cut and its orbit
residual, so the per-epoch eligibility inputs (E1-E4) are unchanged and only the frame of the
relic moves. Every lag-one entry is recomputed, and with it the run-level gates E5 and E5b and
the shuffled-relic floor, so a run can be measurable in one frame only.

    point   (x, y, z) -> (31-x, 31-y, 31-z)   all three mesh axes reversed
    mirror  (x, y, z) -> (x, 31-y, z)         mesh axis 1 (y, the spin axis) reversed

Each output JSON is the source record with `mesh_file` pointing at the derived mesh and one
added key, `derivation`; schema, params and tag are unchanged, so the frozen loader keys it
exactly as the source. A derived directory is a frame-mapped reading of the source runs,
not a new run and not a qualification.

    python3 experiments/halo/memory_intervention_frames.py SRC_DIR --op point|mirror --out OUT_DIR

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, hashlib, json, os, sys
import numpy as np

N = 32
OPS = {'point': (0, 1, 2), 'mirror': (1,)}     # axes of the [z][y][x] mesh to reverse
SCHEMA = 'halo-memory-prereg/1'
RULE = 'D_j = T^j C_j for 0-based mesh index j; T is an involution, so T is applied to odd j'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def apply(mesh, axes):
    out = mesh
    for ax in axes:
        out = np.flip(out, axis=ax)
    return np.ascontiguousarray(out)


def derive(meshes, op):
    axes = OPS[op]
    return np.stack([apply(m, axes) if j % 2 == 1 else m for j, m in enumerate(meshes)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--op', required=True, choices=sorted(OPS))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    script_sha = sha256(os.path.abspath(__file__))
    n = 0
    for fn in sorted(os.listdir(a.src)):
        if not fn.endswith('.json'):
            continue
        path = os.path.join(a.src, fn)
        try:
            rec = json.load(open(path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(rec, dict) or rec.get('schema') != SCHEMA:
            continue
        src_mesh = os.path.join(a.src, rec['mesh_file'])
        k = rec['mesh_count']
        raw = np.fromfile(src_mesh, dtype='<f4')
        if raw.size != k * N ** 3:
            raise SystemExit(f'{src_mesh}: {raw.size} floats, expected {k * N ** 3}')
        d = derive(raw.reshape(k, N, N, N), a.op).astype('<f4')
        new_mesh = rec['mesh_file'][:-len('.mesh.f32')] + f'.frame-{a.op}.mesh.f32'
        d.tofile(os.path.join(a.out, new_mesh))
        rec['mesh_file'] = new_mesh
        rec['derivation'] = {'source_json': fn, 'source_json_sha256': sha256(path),
                             'source_mesh': os.path.basename(src_mesh), 'source_mesh_sha256': sha256(src_mesh),
                             'op': a.op, 'mesh_axes_reversed_zyx': list(OPS[a.op]), 'rule': RULE,
                             'script': 'experiments/halo/memory_intervention_frames.py', 'script_sha256': script_sha}
        with open(os.path.join(a.out, fn), 'w') as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        n += 1
    if not n:
        raise SystemExit(f'no {SCHEMA} records in {a.src}')
    print(f'{n} runs -> {a.out} ({a.op} frame)')


if __name__ == '__main__':
    main()
