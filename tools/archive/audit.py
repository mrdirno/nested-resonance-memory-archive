#!/usr/bin/env python3
"""Read-only archive inventory and publication-boundary checks.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import xml.etree.ElementTree as ET


STATUSES = {"active", "maintained", "experimental", "archived", "dormant"}
PRIVATE_SUFFIXES = {".stl", ".obj", ".gcode", ".3mf", ".step", ".stp",
                    ".iges", ".igs", ".f3d", ".f3z"}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def tracked_files(root):
    return sorted(set(git(root, "ls-files", "-z").decode("utf-8").rstrip("\0").split("\0")) - {""})


def signaltap_session(root, path):
    """.stp also names Quartus SignalTap sessions; accept only actual session XML."""
    if not path.startswith("fpga/"):
        return False
    try:
        source = local_path(root, path)
        if not source.is_file() or source.stat().st_size > 1_000_000:
            return False
        document = ET.fromstring(source.read_bytes())
        return document.tag == "session" and any(
            instance.get("source_file") == "sld_signaltap.vhd"
            and instance.find("node_ip_info") is not None
            for instance in document.findall("instance")
        )
    except (OSError, ValueError, ET.ParseError):
        return False


def private_artifact(path, root=None):
    p = PurePosixPath(path)
    parts = {part.lower() for part in p.parts}
    private_suffix = p.suffix.lower() in PRIVATE_SUFFIXES
    if private_suffix and p.suffix.lower() == ".stp" and root is not None:
        private_suffix = not signaltap_session(root, path)
    return (bool(parts & {"fabrication", "slicer_profiles", "printer_configs"})
            or private_suffix
            or "workspace/cache/" in path or "npm_cache" in parts)


def local_path(root, value):
    """Reject absolute paths and symlink/path traversal beyond the checkout."""
    if not isinstance(value, str) or not value or PurePosixPath(value).is_absolute():
        raise ValueError(f"Expected a non-empty repository-relative path: {value!r}")
    if ".." in PurePosixPath(value).parts or "\\" in value:
        raise ValueError(f"Unsafe repository path: {value!r}")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes checkout: {value!r}")
    return target


def validate_registry(root, registry):
    errors = []
    seen = set()
    if registry.get("schema_version") != 1:
        errors.append("Registry schema_version must be 1")
    if not isinstance(registry.get("components"), list) or not registry["components"]:
        return errors + ["Registry components must be a non-empty list"]
    for component in registry["components"]:
        if not isinstance(component, dict):
            errors.append("Every component must be an object")
            continue
        name = component.get("id")
        if not isinstance(name, str) or not name or name in seen:
            errors.append(f"Missing or duplicate component id: {name!r}")
        seen.add(str(name))
        if component.get("status") not in STATUSES:
            errors.append(f"{name}: unknown lifecycle status")
        for field in ("summary", "next_action"):
            if not isinstance(component.get(field), str) or not component[field].strip():
                errors.append(f"{name}: missing {field}")
        for field in ("paths", "entry_points", "evidence"):
            values = component.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"{name}: {field} must be a non-empty list")
                continue
            for value in values:
                try:
                    if not local_path(root, value).exists():
                        errors.append(f"{name}: missing {field}: {value}")
                except ValueError as exc:
                    errors.append(f"{name}: {exc}")
    return errors


def inventory(root, registry, files):
    components = []
    classified = set()
    for component in registry["components"]:
        selected = {p for p in files for prefix in component["paths"]
                    if p == prefix.rstrip("/") or p.startswith(prefix.rstrip("/") + "/")}
        classified.update(selected)
        components.append({**component, "tracked_file_count": len(selected)})
    return {
        "schema_version": 1,
        "author": "Aldrin Payopay",
        "source_commit": git(root, "rev-parse", "HEAD").decode().strip(),
        "scope": "Git index paths; working-tree files validate entry points. Untracked files are excluded. Lifecycle labels are stewardship decisions, not test results.",
        "tracked_path_digest_sha256": hashlib.sha256("\n".join(files).encode()).hexdigest(),
        "tracked_file_count": len(files),
        "classified_file_count": len(classified),
        "unclassified_file_count": len(set(files) - classified),
        "top_level": dict(sorted(Counter(p.split("/")[0] for p in files).items())),
        "private_artifact_violation_count": sum(private_artifact(p, root) for p in files),
        "components": components,
        "limits": ["Does not establish scientific validity, dependency safety, execution health, deployment status, or release readiness.",
                   "Archived content stays in place to preserve citations and historical imports.",
                   "Unclassified content needs review; age alone never triggers archival or deletion."],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--registry", default="docs/archive/components.json")
    parser.add_argument("--output", type=Path, help="Write measured JSON inventory to this explicit path")
    parser.add_argument("--check", action="store_true", help="Fail on broken registry paths or private tracked artifacts")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        registry = json.loads(local_path(root, args.registry).read_text())
        if not isinstance(registry, dict):
            raise ValueError("Registry must be a JSON object")
        errors = validate_registry(root, registry)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        report = inventory(root, registry, tracked_files(root))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(f"{report['tracked_file_count']} tracked files; {len(report['components'])} lifecycle entries; "
              f"{report['unclassified_file_count']} files await classification")
        if report["private_artifact_violation_count"]:
            print(f"{report['private_artifact_violation_count']} private artifact paths are tracked; inspect locally before publication.", file=sys.stderr)
        if args.check and report["private_artifact_violation_count"]:
            return 1
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Archive audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
