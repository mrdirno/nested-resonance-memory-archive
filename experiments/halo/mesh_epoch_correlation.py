#!/usr/bin/env python3
"""mesh_epoch_correlation.py - per-epoch full-field Pearson correlation between two
runs' density meshes, read straight from the *.mesh.f32 files (24 epochs x 32^3
float32, epoch-major, as tests/halo/memory_prereg_run.js writes them).

The Ring 29 pre-registration (analysis/2026-09-21_sg032_third_condition.md) names
one reported, unscored diagnostic: for each seed shared between two conditions,
the per-epoch correlation between the two conditions' meshes at the same epoch
(median over the scored epochs), beside the cross-seed same-condition baseline.
This script computes exactly that, independently of the frozen scorer, and
reports numbers only. It decides nothing.

    python3 experiments/halo/mesh_epoch_correlation.py DIR --a spinchladni_sg0.3_gl0 \
        --b spinchladni_sg0.32_gl0 [--scored 3 24] [--json OUT]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, glob, json, os, re, statistics, sys
import numpy as np

MESH_N = 32
CELLS = MESH_N ** 3


def load_mesh(path):
    a = np.fromfile(path, dtype="<f4")
    if a.size % CELLS:
        raise SystemExit(f"{path}: {a.size} floats is not a multiple of {CELLS}")
    return a.reshape(-1, CELLS).astype(np.float64)


def pearson(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else float("nan")


def runs_of(dir_, cond):
    out = {}
    for p in sorted(glob.glob(os.path.join(dir_, f"{cond}_seed*_n*_e*.mesh.f32"))):
        m = re.search(r"_seed(\d+)_", os.path.basename(p))
        out[int(m.group(1))] = p
    return out


def per_epoch(pa, pb, e0, e1):
    A, B = load_mesh(pa), load_mesh(pb)
    n = min(A.shape[0], B.shape[0])
    rs = [pearson(A[i], B[i]) for i in range(n)]
    scored = [r for i, r in enumerate(rs, start=1) if e0 <= i <= e1]
    return {"epochs": n, "r_by_epoch": [round(r, 6) for r in rs],
            "median_all": round(statistics.median(rs), 6),
            "median_scored": round(statistics.median(scored), 6),
            "min_all": round(min(rs), 6), "max_all": round(max(rs), 6)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--scored", nargs=2, type=int, default=[3, 24], metavar=("FIRST", "LAST"),
                    help="1-based inclusive epoch window the scorer uses (its scored_epochs)")
    ap.add_argument("--json")
    a = ap.parse_args()
    RA, RB = runs_of(a.dir, a.a), runs_of(a.dir, a.b)
    shared = sorted(set(RA) & set(RB))
    e0, e1 = a.scored
    out = {"schema": "halo-mesh-epoch-correlation/1", "dir": a.dir, "condition_a": a.a, "condition_b": a.b,
           "scored_epochs": [e0, e1], "mesh_n": MESH_N, "shared_seeds": shared,
           "same_seed_cross_condition": {}, "cross_seed_within_b": {}, "cross_seed_within_a": {}}
    for s in shared:
        out["same_seed_cross_condition"][str(s)] = per_epoch(RA[s], RB[s], e0, e1)
    for name, R in (("cross_seed_within_b", RB), ("cross_seed_within_a", RA)):
        seeds = sorted(R)
        for i in range(len(seeds)):
            for j in range(i + 1, len(seeds)):
                out[name][f"{seeds[i]}/{seeds[j]}"] = per_epoch(R[seeds[i]], R[seeds[j]], e0, e1)
    def med(block, key):
        v = [x[key] for x in block.values()]
        return round(statistics.median(v), 6) if v else None
    out["summary"] = {
        "same_seed_cross_condition_median_of_medians_scored": med(out["same_seed_cross_condition"], "median_scored"),
        "cross_seed_within_b_median_of_medians_scored": med(out["cross_seed_within_b"], "median_scored"),
        "cross_seed_within_a_median_of_medians_scored": med(out["cross_seed_within_a"], "median_scored"),
    }
    print(f"{a.a} vs {a.b} in {a.dir}  (scored epochs {e0}-{e1})")
    print("  same seed, across conditions:")
    for s, x in out["same_seed_cross_condition"].items():
        print(f"    seed {s:>6}: median_scored {x['median_scored']:+.4f}  median_all {x['median_all']:+.4f}  range [{x['min_all']:+.4f}, {x['max_all']:+.4f}]")
    for name in ("cross_seed_within_b", "cross_seed_within_a"):
        print(f"  {name.replace('_', ' ')} ({a.b if name.endswith('b') else a.a}):")
        for k, x in out[name].items():
            print(f"    seeds {k:>13}: median_scored {x['median_scored']:+.4f}  median_all {x['median_all']:+.4f}  range [{x['min_all']:+.4f}, {x['max_all']:+.4f}]")
    print("  summary:", json.dumps(out["summary"]))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1)
        print("wrote", a.json)


if __name__ == "__main__":
    main()
