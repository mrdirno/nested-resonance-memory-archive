#!/usr/bin/env python3
"""
Metadata Enrichment Script for Result Files

Purpose: Retroactively add standardized provenance metadata to result JSON files
         that are missing git_sha and other key provenance fields.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Created: 2025-10-30
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Usage:
    python enrich_result_metadata.py --dry-run  # Preview changes
    python enrich_result_metadata.py            # Apply changes

Metadata Added:
    - git_sha: Current repository commit hash
    - generated_at: File modification timestamp (preserved from filesystem)
    - script: Inferred from filename or existing metadata
    - nrm_version: "6.17" (current version)
    - metadata_added_retrospectively: true (transparency flag)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import argparse


def get_git_sha():
    """Get current git commit SHA"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def infer_script_name(filepath):
    """Infer script name from filename patterns"""
    filename = filepath.stem

    # Pattern: cycle###_description.json → cycle###_description.py
    if filename.startswith("cycle"):
        return f"{filename}.py"

    # Pattern: paper#_description.json → paper#_description.py
    if filename.startswith("paper"):
        return f"{filename}.py"

    # Pattern: exp_timestamp_results.json → experiment_script.py
    if filename.startswith("exp_"):
        return "experiment_script.py"

    # Default
    return "analysis_script.py"


def get_file_timestamp(filepath):
    """Get file modification time as ISO timestamp"""
    mtime = filepath.stat().st_mtime
    return datetime.fromtimestamp(mtime).isoformat()


def needs_enrichment(data):
    """Check if file needs metadata enrichment"""
    if "metadata" not in data:
        return True

    metadata = data["metadata"]

    # Missing git_sha is primary indicator
    if "git_sha" not in metadata:
        return True

    return False


def enrich_metadata(filepath, dry_run=False):
    """
    Add standardized metadata to a result file

    Args:
        filepath: Path to JSON result file
        dry_run: If True, only print what would be changed

    Returns:
        bool: True if enriched, False if skipped
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Error reading {filepath.name}: {e}")
        return False

    # Skip if data is not a dict (e.g., empty list, array, etc.)
    if not isinstance(data, dict):
        print(f"⚠️  Skipping {filepath.name}: Not a dict (type: {type(data).__name__})")
        return False

    if not needs_enrichment(data):
        return False

    # Ensure metadata dict exists
    if "metadata" not in data:
        data["metadata"] = {}

    metadata = data["metadata"]

    # Add missing fields
    if "git_sha" not in metadata:
        metadata["git_sha"] = get_git_sha()

    if "generated_at" not in metadata:
        metadata["generated_at"] = get_file_timestamp(filepath)

    if "script" not in metadata:
        metadata["script"] = infer_script_name(filepath)

    if "nrm_version" not in metadata:
        metadata["nrm_version"] = "6.17"

    # Add transparency flag
    metadata["metadata_added_retrospectively"] = True

    if dry_run:
        print(f"✓ Would enrich: {filepath.name}")
        print(f"  - git_sha: {metadata['git_sha'][:8]}...")
        print(f"  - script: {metadata['script']}")
        print(f"  - nrm_version: {metadata['nrm_version']}")
        return True

    # Write back with enriched metadata
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Enriched: {filepath.name}")
        return True
    except IOError as e:
        print(f"❌ Error writing {filepath.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Enrich result files with standardized provenance metadata"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "data" / "results",
        help="Path to results directory (default: ../data/results)"
    )

    args = parser.parse_args()

    results_dir = args.results_dir

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        sys.exit(1)

    print(f"{'DRY RUN - ' if args.dry_run else ''}Metadata Enrichment")
    print("=" * 60)
    print(f"Results directory: {results_dir}")
    print(f"Git SHA: {get_git_sha()[:8]}...")
    print(f"NRM Version: 6.17")
    print()

    # Find all JSON files
    json_files = list(results_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON result files")
    print()

    # Process each file
    enriched_count = 0
    skipped_count = 0
    error_count = 0

    for filepath in sorted(json_files):
        try:
            if enrich_metadata(filepath, dry_run=args.dry_run):
                enriched_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"❌ Unexpected error with {filepath.name}: {e}")
            error_count += 1

    # Summary
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  {'Would enrich' if args.dry_run else 'Enriched'}: {enriched_count}")
    print(f"  Skipped (already complete): {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(json_files)}")

    if enriched_count > 0:
        new_coverage = (skipped_count + enriched_count) / len(json_files) * 100
        print()
        print(f"  New metadata coverage: {new_coverage:.1f}%")

    if args.dry_run and enriched_count > 0:
        print()
        print("Run without --dry-run to apply changes")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
