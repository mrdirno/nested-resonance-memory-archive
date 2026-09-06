#!/usr/bin/env python3
"""Centered radial-residual recurrence qualification; no physical simulation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only

Analytical fixtures qualify this statistic only. Recorded rotation ranks are
descriptive because the physical fields need not be rotation-exchangeable.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
from scipy.ndimage import gaussian_filter
from scipy.stats import binomtest

from halo_memory_input_integrity import audit_inputs


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Geometry:
    """Fixed spherical support and exact discrete radial shells, in z/y/x order."""

    def __init__(self, design, radius=None):
        self.design = design
        self.n = design["mesh_n"]
        self.radius = design["radius_cells"] if radius is None else radius
        z, y, x = np.indices((self.n,) * 3)
        self.q = sum((2 * axis - (self.n - 1)) ** 2 for axis in (z, y, x))
        self.mask = (self.q <= (2 * self.radius) ** 2).ravel()
        _, self.shell = np.unique(self.q.ravel()[self.mask], return_inverse=True)
        self.counts = np.bincount(self.shell)
        _, self.full_shell = np.unique(self.q.ravel(), return_inverse=True)
        self.full_counts = np.bincount(self.full_shell)
        cube = np.arange(self.n ** 3).reshape((self.n,) * 3)
        inverse = np.full(self.n ** 3, -1, dtype=np.int32)
        inverse[self.mask] = np.arange(np.count_nonzero(self.mask))
        transforms = []
        for perm in itertools.permutations(range(3)):
            parity = (-1) ** sum(perm[i] > perm[j] for i in range(3) for j in range(i + 1, 3))
            for signs in itertools.product((1, -1), repeat=3):
                if parity * np.prod(signs) != 1:
                    continue
                a = cube.transpose(perm)
                a = a[tuple(slice(None, None, sign) for sign in signs)]
                transforms.append((perm, signs, inverse[a.ravel()[self.mask]]))
        transforms.sort(key=lambda t: (t[0] != (0, 1, 2) or t[1] != (1, 1, 1), t[0], t[1]))
        self.rotations = np.stack([t[2] for t in transforms])
        assert self.rotations.shape[0] == 24 and np.all(self.rotations >= 0)

    def shell_means(self, values):
        return np.bincount(self.shell, weights=values, minlength=len(self.counts)) / self.counts

    def remove_radial(self, values):
        values = np.asarray(values, dtype=np.float64)
        return values - self.shell_means(values)[self.shell]

    def radial_envelope(self, mesh):
        values = np.asarray(mesh, dtype=np.float64).ravel()
        means = np.bincount(self.full_shell, weights=values) / self.full_counts
        return means[self.full_shell].reshape((self.n,) * 3)

    def field(self, mesh):
        mesh = np.asarray(mesh, dtype=np.float64)
        if mesh.shape != (self.n,) * 3 or not np.all(np.isfinite(mesh)) or np.any(mesh < 0):
            raise ValueError("Density must have the declared shape and finite nonnegative values")
        values = mesh.ravel()[self.mask]
        residual = self.remove_radial(values)
        norm2 = float(np.dot(residual, residual))
        total, mass = float(mesh.sum()), float(values.sum())
        mean = float(values.mean())
        fraction = mass / total if total > 0 else 0.0
        relative_rms = float(np.sqrt(norm2 / values.size) / mean) if mean > 0 else 0.0
        fourth = float(np.sum(residual ** 4))
        effective = norm2 ** 2 / fourth if fourth > 0 else 0.0
        reasons = []
        for failed, name in (
            (fraction < self.design["minimum_mass_fraction"], "insufficient_mask_mass"),
            (relative_rms < self.design["minimum_relative_residual_rms"], "insufficient_angular_variance"),
            (effective < self.design["minimum_residual_effective_cells"], "insufficient_residual_support"),
        ):
            if failed:
                reasons.append(name)
        return {"residual": residual, "eligible": not reasons, "reasons": reasons,
                "mass_fraction": fraction, "relative_residual_rms": relative_rms,
                "residual_effective_cells": effective}

    def comparison(self, a, b):
        if not a["eligible"] or not b["eligible"]:
            return {"eligible": False, "correlation": None, "orientation_rank": None,
                    "alarm": None, "reasons": sorted(set(a["reasons"] + b["reasons"]))}
        ar, br = a["residual"], b["residual"]
        scores = (br[self.rotations] @ ar) / (np.linalg.norm(ar) * np.linalg.norm(br))
        scores = np.clip(scores, -1.0, 1.0)
        score = float(scores[0])
        rank = float(np.mean(scores >= score - self.design["tie_tolerance"]))
        return {"eligible": True, "correlation": score, "orientation_rank": rank,
                "alarm": bool(rank <= self.design["alpha"] and score >= self.design["alarm_min_correlation"]),
                "rotation_score_range": [float(scores.min()), float(scores.max())], "reasons": []}


def exact_interval(successes, trials):
    if not trials:
        return [0.0, 1.0]
    ci = binomtest(successes, trials).proportion_ci(confidence_level=0.95, method="exact")
    return [float(ci.low), float(ci.high)]


def analytical_pair(geometry, envelope, rng, family, correlation=None):
    """Nonnegative shell-mass-preserving analytical fixtures, never observations."""
    mean = envelope.ravel()[geometry.mask]
    vectors = []
    for _ in range(2):
        noise = rng.normal(size=envelope.shape)
        if family == "smooth_sigma2":
            noise = gaussian_filter(noise, sigma=2.0, mode="reflect")
        elif family != "iid":
            raise ValueError("Unknown analytical fixture family")
        vector = mean * geometry.remove_radial(noise.ravel()[geometry.mask])
        norm = np.linalg.norm(vector)
        if not norm > 0:
            raise ValueError("Envelope has no angular support for a fixture")
        vectors.append(vector / norm)
    u, v = vectors
    if correlation is not None:
        v = v - np.dot(v, u) * u
        norm = np.linalg.norm(v)
        if not norm > 1e-12:
            raise ValueError("Analytical basis is degenerate")
        v /= norm
        v = correlation * u + np.sqrt(1 - correlation ** 2) * v
    outputs = []
    for vector in (u, v):
        valid = mean > 0
        peak = float(np.max(np.abs(vector[valid]) / mean[valid]))
        amplitude = geometry.design["fixture_max_relative_deviation"] / peak
        out = envelope.copy().ravel()
        out[geometry.mask] = mean + amplitude * vector
        outputs.append(out.reshape(envelope.shape))
    return outputs


def compact_field(field):
    return {key: value for key, value in field.items() if key != "residual"}


def characterize_recorded(runs, geometry, sensitivity):
    reports = []
    radial_failures, equivariance_failures = 0, 0
    for name, metadata, mesh in runs:
        fields = [geometry.field(frame) for frame in mesh]
        secondary = [sensitivity.field(frame) for frame in mesh]
        for frame in mesh:
            radial = geometry.radial_envelope(frame)
            projected = geometry.field(radial)
            scale = np.linalg.norm(radial.ravel()[geometry.mask])
            fraction = np.linalg.norm(projected["residual"]) / scale if scale else 0.0
            radial_failures += int(projected["eligible"] or fraction > geometry.design["radial_relative_tolerance"])
        pairs = []
        for k in range(1, len(mesh)):
            measured = geometry.comparison(fields[k], fields[k - 1])
            alternate = sensitivity.comparison(secondary[k], secondary[k - 1])
            row = {"current_epoch": k + 1, "previous_epoch": k, **measured,
                   "sensitivity": alternate}
            if measured["eligible"]:
                rotation = geometry.rotations[7]
                a = {**fields[k], "residual": fields[k]["residual"][rotation]}
                b = {**fields[k - 1], "residual": fields[k - 1]["residual"][rotation]}
                rotated = geometry.comparison(a, b)
                error = abs(rotated["correlation"] - measured["correlation"])
                equivariance_failures += int(error > geometry.design["rotation_equivariance_absolute_tolerance"])
            if measured["eligible"] and alternate["eligible"]:
                row["sensitivity_absolute_difference"] = abs(measured["correlation"] - alternate["correlation"])
            pairs.append(row)
        eligible = [p for p in pairs if p["eligible"]]
        shared = [p for p in eligible if p["sensitivity"]["eligible"]]
        minimum = geometry.design["recorded_pairs_minimum_per_run"]
        shared_fraction = len(shared) / len(eligible) if eligible else 0.0
        max_difference = max((p["sensitivity_absolute_difference"] for p in shared), default=None)
        reports.append({"run": name, "params": metadata["params"],
                        "epochs": [compact_field(f) for f in fields], "pairs": pairs,
                        "eligible_pair_count": len(eligible), "total_pair_count": len(pairs),
                        "enough_pairs_for_summary": len(eligible) >= minimum,
                        "median_correlation": float(np.median([p["correlation"] for p in eligible])) if len(eligible) >= minimum else None,
                        "diagnostic_alarm_count": sum(p["alarm"] for p in eligible),
                        "support_shared_eligible_fraction": shared_fraction,
                        "support_maximum_score_difference": max_difference,
                        "support_robustness_passed": bool(len(eligible) >= minimum
                            and shared_fraction >= geometry.design["sensitivity_minimum_shared_eligible_fraction"]
                            and max_difference is not None
                            and max_difference <= geometry.design["sensitivity_maximum_pair_score_difference"]),
                        "interpretation": "Exploratory angular recurrence only; adjacent epochs are dependent and ranks are not physical p-values."})
    return reports, {"radialized_epoch_count": sum(len(r[2]) for r in runs),
                     "radial_control_failures": radial_failures,
                     "simultaneous_rotation_failures": equivariance_failures}


def characterize_fixtures(runs, geometry, design):
    anchors = [run for run in runs if run[1]["params"]["seed"] == design["fixture_anchor_seed"]]
    if len(anchors) != 3:
        raise ValueError("The frozen design requires three anchor parameter groups")
    streams = np.random.SeedSequence(design["fixture_seed"]).spawn(len(anchors) * len(design["fixture_families"]))
    reports, stream_index = [], 0
    for name, _, mesh in anchors:
        envelope = geometry.radial_envelope(mesh[design["fixture_anchor_epoch_index"]])
        shell_mass = np.bincount(geometry.full_shell, weights=envelope.ravel())
        for family in design["fixture_families"]:
            rng = np.random.default_rng(streams[stream_index])
            stream_index += 1
            row = {"anchor_run": name, "anchor_epoch": design["fixture_anchor_epoch_index"] + 1,
                   "family": family, "kind": "analytical qualification fixtures, not physical data",
                   "null": None, "power": [], "numerical_failures": 0}
            cases = [(None, design["null_replicates_per_stratum"])] + [(effect, design["power_replicates_per_stratum_per_effect"]) for effect in design["injected_correlations"]]
            for effect, trials in cases:
                eligible = alarms = rank_exceedances = numerical_failures = 0
                max_correlation_error = 0.0
                for _ in range(trials):
                    a, b = analytical_pair(geometry, envelope, rng, family, effect)
                    for density in (a, b):
                        actual_mass = np.bincount(geometry.full_shell, weights=density.ravel())
                        if np.any(density < 0) or not np.allclose(actual_mass, shell_mass, rtol=design["mass_preservation_relative_tolerance"], atol=0):
                            numerical_failures += 1
                    af, bf = geometry.field(a), geometry.field(b)
                    measured = geometry.comparison(af, bf)
                    if effect is not None:
                        ar, br = af["residual"], bf["residual"]
                        actual = float(np.dot(ar, br) / (np.linalg.norm(ar) * np.linalg.norm(br)))
                        error = abs(actual - effect)
                        max_correlation_error = max(max_correlation_error, error)
                        numerical_failures += int(error > design["correlation_recovery_absolute_tolerance"])
                    if measured["eligible"]:
                        eligible += 1
                        alarms += measured["alarm"]
                        rank_exceedances += measured["orientation_rank"] <= design["alpha"]
                    if effect is not None and "static_anisotropic_control" not in row:
                        row["static_anisotropic_control"] = geometry.comparison(af, af)
                result = {"assigned_residual_correlation": effect, "trials": trials, "eligible": eligible,
                          "eligible_fraction": eligible / trials, "alarm_count": int(alarms),
                          "alarm_rate": alarms / eligible if eligible else None,
                          "alarm_interval_95_exact": exact_interval(alarms, eligible),
                          "rank_only_count": int(rank_exceedances),
                          "rank_only_interval_95_exact": exact_interval(rank_exceedances, eligible),
                          "maximum_correlation_recovery_error": max_correlation_error if effect is not None else None,
                          "numerical_failures": numerical_failures}
                result["eligibility_passed"] = result["eligible_fraction"] >= design["fixture_min_eligible_fraction"]
                if effect is None:
                    result["null_passed"] = bool(result["eligibility_passed"]
                        and result["alarm_interval_95_exact"][1] <= design["null_upper_95_limit"]
                        and result["rank_only_interval_95_exact"][1] <= design["null_upper_95_limit"])
                    row["null"] = result
                else:
                    row["power"].append(result)
                row["numerical_failures"] += numerical_failures
            target = next(p for p in row["power"] if p["assigned_residual_correlation"] == design["target_power_correlation"])
            row["target_power_passed"] = bool(target["eligibility_passed"] and target["alarm_interval_95_exact"][0] >= design["power_lower_95_limit"])
            row["passed"] = bool(row["null"]["null_passed"] and row["target_power_passed"] and row["numerical_failures"] == 0
                                 and all(p["eligibility_passed"] for p in row["power"]))
            reports.append(row)
            print(json.dumps({"fixture_stratum": [name, family], "passed": row["passed"],
                              "null_eligible": row["null"]["eligible"], "null_rank_ci": row["null"]["rank_only_interval_95_exact"],
                              "target_power_ci": target["alarm_interval_95_exact"]}), flush=True)
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    design_bytes = args.design.read_bytes()
    design = json.loads(design_bytes)
    source_hash = digest(__file__)
    input_dir = workspace / design["input_directory"]
    manifest = workspace / design["manifest"]
    output = args.output.resolve()
    if input_dir.resolve() in output.parents or output == manifest.resolve() or output == args.design.resolve():
        raise ValueError("Output must not overwrite inputs or frozen design")
    before = audit_inputs(input_dir, manifest)
    if not before["passed"]:
        raise ValueError("Input integrity failed before qualification")
    runs = []
    for entry in before["files"]:
        name = entry["file"]
        if not name.endswith(".json"):
            continue
        metadata = json.loads((input_dir / name).read_text())
        mesh = np.fromfile(input_dir / metadata["mesh_file"], dtype="<f4").reshape((design["epochs"],) + (design["mesh_n"],) * 3)
        mesh.setflags(write=False)
        runs.append((name, metadata, mesh))
    runs.sort(key=lambda r: r[0])
    geometry = Geometry(design)
    sensitivity = Geometry(design, radius=design["sensitivity_radius_cells"])
    recorded, numerical = characterize_recorded(runs, geometry, sensitivity)
    print("Recorded descriptive comparisons calculated; proceeding to frozen analytical fixtures.", flush=True)
    fixtures = characterize_fixtures(runs, geometry, design)
    after = audit_inputs(input_dir, manifest)
    unchanged = (after["passed"] and before["manifest_sha256"] == after["manifest_sha256"]
                 and [f["sha256"] for f in before["files"]] == [f["sha256"] for f in after["files"]]
                 and args.design.read_bytes() == design_bytes and digest(__file__) == source_hash)
    gates = {"input_and_design_unchanged": bool(unchanged),
             "numerical_invariants": bool(not numerical["radial_control_failures"] and not numerical["simultaneous_rotation_failures"] and all(f["numerical_failures"] == 0 for f in fixtures)),
             "analytical_null_and_power": all(f["passed"] for f in fixtures),
             "recorded_pair_eligibility": all(r["enough_pairs_for_summary"] for r in recorded),
             "recorded_support_robustness": all(r["support_robustness_passed"] for r in recorded)}
    report = {"schema": "halo-angular-recurrence-qualification/1", "author": "Aldrin Payopay",
              "measured_at": datetime.now(timezone.utc).isoformat(), "execution_ok": bool(unchanged),
              "qualification_passed": all(gates.values()), "gates": gates,
              "design": design, "design_sha256": hashlib.sha256(design_bytes).hexdigest(),
              "script_sha256": source_hash, "integrity_script_sha256": before["script_sha256"],
              "input_manifest_sha256": before["manifest_sha256"],
              "input_file_hashes": [{"file": f["file"], "sha256": f["sha256"]} for f in before["files"]],
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()},
              "geometry": {"shape": [design["mesh_n"]] * 3, "center": (design["mesh_n"] - 1) / 2,
                           "mask_cells": int(geometry.mask.sum()), "exact_radius_shells": len(geometry.counts),
                           "sensitivity_mask_cells": int(sensitivity.mask.sum()), "proper_rotations": len(geometry.rotations)},
              "numerical_controls": numerical, "recorded_runs": recorded, "analytical_fixtures": fixtures,
              "interpretation": "Qualification of descriptive angular recurrence only. No result establishes passive relic retention or causal NRM memory. All analytical fixtures are labeled measurement tests, not physical observations.",
              "limits": design["limits"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"execution_ok": report["execution_ok"], "qualification_passed": report["qualification_passed"], "gates": gates}), flush=True)
    print("Receipt: " + str(output), flush=True)
    return 0 if unchanged else 1


if __name__ == "__main__":
    raise SystemExit(main())
