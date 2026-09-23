#!/usr/bin/env python3
"""hemisphere_persistence.py - does a run's north/south mass split survive each scored
epoch boundary? Read straight from the *.mesh.f32 files (24 epochs x 32^3 float32,
epoch-major, [z][y][x], as tests/halo/memory_prereg_run.js and
tests/halo/memory_intervention_run.js write them). y is the chamber's spin axis and
mesh axis 1; "north" is y index 16..31, "south" 0..15.

The Ring 30 pre-registration (analysis/2026-09-22_relic_intervention.md) reports this,
beside the component decomposition's O, as an unscored mechanism diagnostic. The Ring 29
control's own-relic contrast sits mostly in the point-odd part of the field, and in 7 of the
8 detections over the four orientation classes the detected run is the hemisphere-sign odd
one out of its condition, so the diagnostic
counts, for every lag-one pair the frozen scorer reads (relic mesh e-1 -> current mesh
e, e = 3..24, 1-based), whether the current's inner-block (B2, cells 8..23) north/south
sign equals the relic's whole-mesh sign: after the x1/2 zoom-out the whole relic lands
in B2. It also reports the lag-one autocorrelation of the whole-mesh split and, inside
each condition, how often two seeds sit in the same hemisphere. Numbers only; it
decides nothing and is not the frozen scorer.

    python3 experiments/halo/hemisphere_persistence.py DIR [--qualification Q.json] [--json OUT]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>  License: GPL-3.0-only
"""
import argparse, glob, json, os, re, sys
import numpy as np

MESH_N = 32
CELLS = MESH_N ** 3
B2 = slice(8, 24)
SCORED = (3, 24)          # the frozen scorer's lag-one epochs, 1-based current index


def load_mesh(path):
    a = np.fromfile(path, dtype="<f4")
    if a.size % CELLS:
        raise SystemExit(f"{path}: {a.size} floats is not a multiple of {CELLS}")
    return a.reshape(-1, MESH_N, MESH_N, MESH_N).astype(np.float64)


def split(m):
    """(north - south) / (north + south) over a [z][y][x] block; nan if empty."""
    h = m.shape[1] // 2
    s, n = float(m[:, :h, :].sum()), float(m[:, h:, :].sum())
    return (n - s) / (n + s) if (n + s) > 0 else float("nan")


def sign(v):
    return 0 if not np.isfinite(v) or v == 0 else (1 if v > 0 else -1)


def lag1_autocorr(x):
    x = np.asarray([v for v in x if np.isfinite(v)], dtype=float)
    if x.size < 3:
        return float("nan")
    x = x - x.mean()
    d = float((x * x).sum())
    return float((x[:-1] * x[1:]).sum() / d) if d > 0 else float("nan")


def run_numbers(mesh, eligible=None):
    """mesh: (epochs, 32, 32, 32). eligible: optional {e: bool} keyed by 1-based current epoch."""
    E = mesh.shape[0]
    whole = [split(mesh[i]) for i in range(E)]
    inner = [split(mesh[i][B2, B2, B2]) for i in range(E)]
    pairs = []
    for e in range(SCORED[0], min(SCORED[1], E) + 1):
        rel, cur = whole[e - 2], inner[e - 1]
        pairs.append({"e": e, "relic_whole": round(rel, 6), "current_b2": round(cur, 6),
                      "same_sign": sign(rel) != 0 and sign(rel) == sign(cur),
                      "eligible": None if eligible is None else bool(eligible.get(e, False))})
    same_all = sum(p["same_sign"] for p in pairs)
    el = [p for p in pairs if p["eligible"]]
    rc = np.array([[p["relic_whole"], p["current_b2"]] for p in pairs])
    corr = float(np.corrcoef(rc[:, 0], rc[:, 1])[0, 1]) if len(pairs) > 2 and rc.std(axis=0).min() > 0 else float("nan")
    return {"pairs_scored": len(pairs), "same_sign_scored": same_all,
            "pairs_eligible": len(el) if eligible is not None else None,
            "same_sign_eligible": sum(p["same_sign"] for p in el) if eligible is not None else None,
            "corr_relic_whole_vs_current_b2": round(corr, 6),
            "lag1_autocorr_whole_split": round(lag1_autocorr(whole), 6),
            "whole_split_by_mesh": [round(v, 6) for v in whole],
            "b2_split_by_mesh": [round(v, 6) for v in inner],
            "pairs": pairs}


def discover(dir_):
    """{condition: {seed: (json_path, mesh_path)}} from the run JSONs in dir_."""
    out = {}
    for jp in sorted(glob.glob(os.path.join(dir_, "*.json"))):
        try:
            head = json.load(open(jp))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(head, dict) or "mesh_file" not in head or "params" not in head:
            continue
        p = head["params"]
        cond = f"{p['preset']}_sg{p['selfgrav']:g}_gl{p['gainloss']:g}"
        out.setdefault(cond, {})[int(p["seed"])] = (jp, os.path.join(dir_, head["mesh_file"]))
    return out


def eligible_from(qpath):
    """{(condition, seed): {e: eligible}} from a frozen-scorer qualification.json."""
    q = json.load(open(qpath))
    out = {}
    for r in q.get("runs", []):
        c = r["condition"]
        cond = f"{c['preset']}_sg{c['selfgrav']:g}_gl{c['gainloss']:g}"
        out[(cond, int(r["seed"]))] = {int(ep["epoch"]): bool(ep["eligible"]) for ep in r["epochs"]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--qualification", default=None, help="frozen-scorer output for this dir (for eligible epochs)")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    runs = discover(a.dir)
    if not runs:
        raise SystemExit(f"no run JSON with a mesh_file in {a.dir}")
    elig = eligible_from(a.qualification) if a.qualification else {}
    here = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    src = os.path.abspath(a.dir)
    shown = os.path.relpath(src, here) if src.startswith(here + os.sep) else os.path.basename(src)
    res = {"dir": shown, "scored": list(SCORED), "b2": [8, 23], "north": "y index 16..31",
           "runs": {}, "conditions": {}}
    for cond in sorted(runs):
        meshes = {}
        for seed in sorted(runs[cond]):
            m = load_mesh(runs[cond][seed][1])
            meshes[seed] = m
            e = elig.get((cond, seed)) if a.qualification else None
            res["runs"][f"{cond}_seed{seed}"] = run_numbers(m, e)
        seeds = sorted(meshes)
        agree = {}
        for i in range(len(seeds)):
            for j in range(i + 1, len(seeds)):
                A, B = meshes[seeds[i]], meshes[seeds[j]]
                n = min(A.shape[0], B.shape[0])
                cur = range(SCORED[0], min(SCORED[1], n) + 1)
                agree[f"{seeds[i]}-{seeds[j]}"] = sum(
                    sign(split(A[e - 1][B2, B2, B2])) == sign(split(B[e - 1][B2, B2, B2])) != 0 for e in cur)
        res["conditions"][cond] = {"seeds": seeds, "b2_same_hemisphere_scored": agree}
        for seed in seeds:
            r = res["runs"][f"{cond}_seed{seed}"]
            print(f"{cond} seed {seed}: same sign {r['same_sign_scored']}/{r['pairs_scored']} scored"
                  + (f", {r['same_sign_eligible']}/{r['pairs_eligible']} eligible" if r['pairs_eligible'] is not None else "")
                  + f"; corr {r['corr_relic_whole_vs_current_b2']:+.3f}; lag-1 autocorr {r['lag1_autocorr_whole_split']:+.3f}")
        print(f"  {cond} seeds in the same B2 hemisphere (scored meshes): {agree}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"wrote {a.json}")


if __name__ == "__main__":
    main()
