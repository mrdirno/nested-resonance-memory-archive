#!/usr/bin/env python3
"""Read-only integrity audit of preserved HALO density/metadata pairs.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only

This checks files and numeric validity, not an estimator or physical claim.
Requires NumPy. Raw meshes are interpreted explicitly as little-endian float32;
the historical native-endian writer did not embed an endian marker.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def audit_inputs(input_dir, manifest_path, expected_runs=9, epochs=24, mesh_n=32):
    """Read each manifest-listed file; return evidence without modifying inputs."""
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a JSON object")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("Manifest files must be a list")
    failures, records, payloads, names = [], [], {}, set()
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("Manifest entry is not an object")
            continue
        name = entry.get("file")
        if (not isinstance(name, str) or not name or Path(name).name != name
                or "\\" in name or name in {".", ".."}):
            failures.append("Manifest contains an unsafe filename")
            continue
        if name in names:
            failures.append("Duplicate manifest entry: " + name)
            continue
        names.add(name)
        path = input_dir / name
        record = {"file": name, "expected_bytes": entry.get("bytes"),
                  "expected_sha256": entry.get("sha256")}
        records.append(record)
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError("Expected a regular, non-symlink input file")
            data = path.read_bytes()
            record.update(bytes=len(data), sha256=sha256(data))
            record["manifest_match"] = (record["bytes"] == entry.get("bytes")
                                        and record["sha256"] == entry.get("sha256"))
            if not record["manifest_match"]:
                failures.append("Manifest mismatch: " + name)
            payloads[name] = data
        except (OSError, ValueError) as exc:
            record["error"] = str(exc)
            failures.append("Unreadable input: " + name)

    actual_names = {path.name for path in input_dir.iterdir()}
    if actual_names != names:
        failures.append("Input directory members differ from the manifest")
    json_names = sorted(name for name in names if name.endswith(".json"))
    mesh_names = {name for name in names if name.endswith(".mesh.f32")}
    if len(json_names) != expected_runs or len(mesh_names) != expected_runs:
        failures.append("Expected run-pair count differs from the manifest")
    if len(names) != 2 * expected_runs:
        failures.append("Unexpected file count or file type in manifest")
    if mesh_names != {name[:-5] + ".mesh.f32" for name in json_names}:
        failures.append("Density and JSON basenames are not paired")

    shape = (epochs, mesh_n, mesh_n, mesh_n)
    expected_bytes = epochs * mesh_n ** 3 * np.dtype("<f4").itemsize
    runs = []
    for json_name in json_names:
        mesh_name = json_name[:-5] + ".mesh.f32"
        run = {"metadata_file": json_name, "mesh_file": mesh_name, "failures": []}
        runs.append(run)
        try:
            metadata = json.loads(payloads[json_name])
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be an object")
            params = metadata.get("params", {})
            metadata_valid = (metadata.get("schema") == "halo-memory-prereg/1"
                              and metadata.get("tag") == json_name[:-5]
                              and metadata.get("mesh_file") == mesh_name
                              and metadata.get("mesh_n") == mesh_n
                              and metadata.get("mesh_count") == epochs
                              and isinstance(params, dict)
                              and params.get("epochs") == epochs
                              and isinstance(metadata.get("epochs"), list)
                              and len(metadata["epochs"]) == epochs)
            run["metadata_shape_matches"] = metadata_valid
            run["recorded_page_error_count"] = len(metadata.get("pageerrors", []))
            if not metadata_valid:
                run["failures"].append("Metadata shape, schema or pair identity mismatch")
            data = payloads[mesh_name]
            run["exact_byte_count"] = len(data) == expected_bytes
            if not run["exact_byte_count"]:
                raise ValueError("Mesh byte count does not match the required shape")
            mesh = np.frombuffer(data, dtype="<f4").reshape(shape)
            finite = np.isfinite(mesh)
            totals = mesh.sum(axis=(1, 2, 3), dtype=np.float64)
            run.update(shape=list(mesh.shape), dtype="<f4", cells=int(mesh.size),
                       nonfinite_cells=int(np.count_nonzero(~finite)),
                       negative_cells=int(np.count_nonzero(mesh < 0)),
                       positive_finite_epoch_totals=int(np.count_nonzero(np.isfinite(totals) & (totals > 0))),
                       epoch_totals=[float(value) if np.isfinite(value) else None for value in totals])
            if run["nonfinite_cells"]:
                run["failures"].append("Mesh contains nonfinite cells")
            if run["negative_cells"]:
                run["failures"].append("Mesh contains negative cells")
            if run["positive_finite_epoch_totals"] != epochs:
                run["failures"].append("An epoch has nonfinite or nonpositive total density")
        except (KeyError, OSError, TypeError, ValueError) as exc:
            run["failures"].append(str(exc))
        run["passed"] = not run["failures"]
        if not run["passed"]:
            failures.append("Run failed: " + json_name)

    # Detect concurrent changes during the audit, including to the manifest.
    for record in records:
        try:
            record["unchanged_during_audit"] = sha256((input_dir / record["file"]).read_bytes()) == record.get("sha256")
        except OSError:
            record["unchanged_during_audit"] = False
        if not record["unchanged_during_audit"]:
            failures.append("Input changed during audit: " + record["file"])
    manifest_unchanged = manifest_path.read_bytes() == manifest_bytes
    if not manifest_unchanged:
        failures.append("Manifest changed during audit")
    return {
        "schema": "halo-memory-input-integrity/1", "author": "Aldrin Payopay",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "input_directory": str(input_dir), "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_bytes), "manifest_unchanged": manifest_unchanged,
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "platform": platform.platform(), "host_byteorder": sys.byteorder},
        "expected_shape": list(shape), "interpreted_dtype": "<f4",
        "files": records, "runs": runs,
        "summary": {"file_count": len(records), "run_count": len(runs),
                    "manifest_matches": sum(r.get("manifest_match", False) for r in records),
                    "bytes_read": sum(r.get("bytes", 0) for r in records),
                    "cells_checked": sum(r.get("cells", 0) for r in runs),
                    "nonfinite_cells": sum(r.get("nonfinite_cells", 0) for r in runs),
                    "negative_cells": sum(r.get("negative_cells", 0) for r in runs),
                    "positive_finite_epoch_totals": sum(r.get("positive_finite_epoch_totals", 0) for r in runs)},
        "passed": not failures, "failures": failures,
        "limits": ["Raw inputs and preservation manifest are local-only, not distributed in the public repository.",
                   "Nine runs were selected exploratorily after the prior audit; they are not a confirmatory holdout.",
                   "The raw format has no embedded endian marker. This audit explicitly uses little-endian float32, consistent with the recorded Apple M4 Pro capture and historical native-endian writer.",
                   "Positive density sums are numeric validity checks in stored units, not mass conservation or a physical interpretation.",
                   "No memory estimator, spatial-support diagnostic, surrogate data or scientific inference is computed.",
                   "Matching a preservation manifest does not independently authenticate the original experiment or instrument."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-runs", type=int, default=9)
    parser.add_argument("--epochs", type=int, default=24)
    parser.add_argument("--mesh-n", type=int, default=32)
    args = parser.parse_args()
    input_dir, manifest_path, output = (p.resolve() for p in (args.input_dir, args.manifest, args.output))
    if min(args.expected_runs, args.epochs, args.mesh_n) < 1:
        parser.error("Expected dimensions and run count must be positive")
    if output == manifest_path or output == input_dir or input_dir in output.parents:
        parser.error("Output must be outside the input directory and must not overwrite the manifest")
    try:
        report = audit_inputs(input_dir, manifest_path, args.expected_runs, args.epochs, args.mesh_n)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    except (OSError, TypeError, ValueError) as exc:
        print("Input audit failed: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"passed": report["passed"], **report["summary"], "failures": report["failures"]}))
    print("Receipt: " + str(output))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
