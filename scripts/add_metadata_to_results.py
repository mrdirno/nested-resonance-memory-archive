#!/usr/bin/env python3
"""
Add metadata sections to result JSON files that lack them.

This script:
1. Finds all JSON files in data/results/ without 'metadata' key
2. Infers git SHA from file modification time
3. Extracts existing date/timestamp information
4. Adds proper metadata section
5. Preserves all existing data

Usage:
    python scripts/add_metadata_to_results.py --dry-run  # Preview changes
    python scripts/add_metadata_to_results.py            # Apply changes
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


def get_git_sha_for_timestamp(timestamp: datetime, repo_path: Path) -> Optional[str]:
    """Get the git SHA for the commit closest to (before) the given timestamp."""
    try:
        # Format timestamp for git log
        until_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Get the most recent commit before this timestamp
        result = subprocess.run(
            ["git", "log", f"--until={until_time}", "--format=%H", "-n", "1"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        sha = result.stdout.strip()
        return sha if sha else None
    except Exception as e:
        print(f"  Warning: Could not determine git SHA: {e}")
        return None


def extract_date_from_data(data: Any) -> Optional[str]:
    """Extract date/timestamp from existing data structure."""
    if isinstance(data, dict):
        # Look for common date fields
        for key in ['date', 'generated_at', 'timestamp', 'analysis_date']:
            if key in data:
                return str(data[key])

        # Check meta_info section
        if 'meta_info' in data and isinstance(data['meta_info'], dict):
            for key in ['analysis_date', 'date', 'timestamp']:
                if key in data['meta_info']:
                    return str(data['meta_info'][key])

    return None


def extract_experiment_info(data: Any, filename: str) -> Dict[str, Any]:
    """Extract experiment/cycle information from data."""
    info = {}

    if isinstance(data, dict):
        # Cycle ID from filename or data
        if 'cycle_id' in data:
            info['cycle'] = data['cycle_id']
        elif 'cycle' in data:
            info['cycle'] = data['cycle']
        elif filename.startswith('cycle'):
            # Extract from filename like "cycle151_anti_harmonic_scan.json"
            try:
                cycle_num = int(filename.split('_')[0].replace('cycle', ''))
                info['cycle'] = cycle_num
            except:
                pass

        # Experiment name
        if 'experiment' in data:
            info['experiment'] = str(data['experiment'])
        elif 'description' in data:
            info['description'] = str(data['description'])

    return info


def create_metadata(
    filename: str,
    file_path: Path,
    data: Any,
    repo_path: Path
) -> Dict[str, Any]:
    """Create metadata section for a result file."""
    metadata = {}

    # 1. Determine timestamp
    existing_date = extract_date_from_data(data)
    if existing_date:
        # Parse existing date
        generated_at = existing_date
    else:
        # Use file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        generated_at = mtime.isoformat()

    # 2. Get git SHA
    if existing_date:
        try:
            # Parse date for git lookup
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    ts = datetime.strptime(existing_date.split('.')[0].replace('Z', ''), fmt)
                    break
                except:
                    continue
            else:
                ts = datetime.fromtimestamp(file_path.stat().st_mtime)
        except:
            ts = datetime.fromtimestamp(file_path.stat().st_mtime)
    else:
        ts = datetime.fromtimestamp(file_path.stat().st_mtime)

    git_sha = get_git_sha_for_timestamp(ts, repo_path)
    if git_sha:
        metadata['git_sha'] = git_sha

    metadata['generated_at'] = generated_at

    # 3. Infer script from filename pattern
    if filename.startswith('cycle'):
        # Extract cycle number
        try:
            cycle_num = int(filename.split('_')[0].replace('cycle', ''))
            metadata['script'] = f"cycle{cycle_num}_*.py"
        except:
            metadata['script'] = "unknown"
    elif 'analysis' in filename or 'meta' in filename:
        metadata['script'] = "analysis_script.py"
        metadata['analysis_type'] = filename.replace('.json', '')
    else:
        metadata['script'] = f"{filename.replace('.json', '')}.py"

    # 4. Add experiment info
    exp_info = extract_experiment_info(data, filename)
    metadata.update(exp_info)

    # 5. Add NRM version
    metadata['nrm_version'] = '6.7'

    # 6. Add note about retrospective metadata
    metadata['metadata_added_retrospectively'] = True

    return metadata


def add_metadata_to_file(
    file_path: Path,
    repo_path: Path,
    dry_run: bool = False
) -> bool:
    """Add metadata section to a single file."""
    filename = file_path.name
    print(f"\nProcessing: {filename}")

    try:
        # Read existing data
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Check if already has metadata
        if isinstance(data, dict) and 'metadata' in data:
            print(f"  ✓ Already has metadata, skipping")
            return False

        # Skip empty arrays
        if isinstance(data, list) and len(data) == 0:
            print(f"  ⚠ Empty array, skipping")
            return False

        # Create metadata
        metadata = create_metadata(filename, file_path, data, repo_path)
        print(f"  Generated metadata:")
        for key, value in metadata.items():
            print(f"    - {key}: {value}")

        # Add metadata to data
        if isinstance(data, dict):
            # Insert metadata at beginning
            new_data = {'metadata': metadata}
            new_data.update(data)
        else:
            # Wrap list in dict with metadata
            new_data = {
                'metadata': metadata,
                'data': data
            }

        # Save if not dry run
        if not dry_run:
            with open(file_path, 'w') as f:
                json.dump(new_data, f, indent=2)
            print(f"  ✅ Updated")
        else:
            print(f"  [DRY RUN] Would update")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add metadata to result JSON files")
    parser.add_argument('--dry-run', action='store_true', help="Preview changes without modifying files")
    args = parser.parse_args()

    repo_path = Path('/Users/aldrinpayopay/nested-resonance-memory-archive')
    results_dir = repo_path / 'data' / 'results'

    print(f"Repository: {repo_path}")
    print(f"Results directory: {results_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY CHANGES'}")
    print("=" * 80)

    # Find files without metadata
    files_without_metadata = []
    for fname in sorted(os.listdir(results_dir)):
        if not fname.endswith('.json'):
            continue

        fpath = results_dir / fname
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'metadata' not in data:
                    files_without_metadata.append(fpath)
                elif isinstance(data, list):
                    files_without_metadata.append(fpath)
        except Exception as e:
            print(f"Warning: Could not read {fname}: {e}")

    print(f"\nFound {len(files_without_metadata)} files without metadata\n")

    # Process each file
    updated = 0
    skipped = 0
    errors = 0

    for file_path in files_without_metadata:
        try:
            if add_metadata_to_file(file_path, repo_path, args.dry_run):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Fatal error: {e}")
            errors += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total processed: {len(files_without_metadata)}")

    if args.dry_run:
        print("\nDRY RUN complete. Run without --dry-run to apply changes.")
    else:
        print("\nChanges applied successfully!")


if __name__ == '__main__':
    main()
