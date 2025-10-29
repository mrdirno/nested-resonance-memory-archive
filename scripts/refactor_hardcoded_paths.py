#!/usr/bin/env python3
"""
Refactor hard-coded workspace paths to use workspace_utils.

This script:
1. Finds all Python files with hard-coded /Volumes/dual/DUALITY-ZERO paths
2. Adds workspace_utils import if needed
3. Replaces hard-coded paths with get_workspace_path() or get_results_path()
4. Preserves code formatting and structure

Usage:
    python scripts/refactor_hardcoded_paths.py --dry-run  # Preview changes
    python scripts/refactor_hardcoded_paths.py            # Apply changes
"""

import re
import os
import subprocess
from pathlib import Path
from typing import List, Tuple


def find_files_with_hardcoded_paths(repo_path: Path) -> List[Path]:
    """Find all Python files with hard-coded paths."""
    result = subprocess.run(
        [
            "grep",
            "-r",
            "/Volumes/dual/DUALITY-ZERO",
            "--include=*.py",
            "code/",
            "papers/",
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    files = set()
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        filepath = line.split(":")[0]
        files.add(repo_path / filepath)

    return sorted(files)


def has_workspace_utils_import(content: str) -> bool:
    """Check if file already imports workspace_utils."""
    patterns = [
        r"from workspace_utils import",
        r"from \.\.experiments\.workspace_utils import",
        r"import workspace_utils",
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False


def add_workspace_utils_import(content: str) -> str:
    """Add workspace_utils import to file."""
    # Find first import block
    lines = content.split("\n")
    import_index = None
    last_import_index = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            if import_index is None:
                import_index = i
            last_import_index = i

    if last_import_index is not None:
        # Add after last import
        insert_index = last_import_index + 1
        lines.insert(
            insert_index, "from workspace_utils import get_workspace_path, get_results_path"
        )
    else:
        # No imports found, add after docstring/comments
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith("#") and '"""' not in line:
                insert_index = i
                break
        lines.insert(insert_index, "from workspace_utils import get_workspace_path, get_results_path")
        lines.insert(insert_index + 1, "")

    return "\n".join(lines)


def refactor_workspace_paths(content: str) -> Tuple[str, int]:
    """Replace hard-coded workspace paths with get_workspace_path()."""
    changes = 0

    # Pattern 1: workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    pattern1 = r'(\w+)\s*=\s*Path\s*\(\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*\/workspace["\']\s*\)'
    matches1 = list(re.finditer(pattern1, content))
    for match in matches1:
        var_name = match.group(1)
        old = match.group(0)
        new = f"{var_name} = get_workspace_path()"
        content = content.replace(old, new, 1)
        changes += 1

    # Pattern 2: workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2"
    pattern2 = r'workspace_path:\s*str\s*=\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*["\']'
    if re.search(pattern2, content):
        content = re.sub(
            pattern2,
            'workspace_path: Path = get_workspace_path()',
            content,
        )
        changes += 1

    # Pattern 3: def __init__(self, workspace_path: str = "/Volumes/...")
    pattern3 = r'workspace_path:\s*str\s*=\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*["\']'
    matches = list(re.finditer(pattern3, content))
    for match in matches:
        old = match.group(0)
        # Check if it's in a function signature
        start = max(0, match.start() - 50)
        before = content[start : match.start()]
        if "def " in before or "class " in before:
            # Replace with None default and add docs
            new = 'workspace_path: str = None'
            content = content.replace(old, new, 1)
            changes += 1

    # Pattern 4: results_path = Path("/Volumes/dual/DUALITY-ZERO-V2/...")
    pattern4 = r'results_path\s*=\s*Path\s*\(\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*["\']\s*\)'
    if re.search(pattern4, content):
        content = re.sub(pattern4, "results_path = get_results_path()", content)
        changes += 1

    # Pattern 5: output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/results")
    pattern5 = r'output_dir\s*=\s*Path\s*\(\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*\/data\/results["\']\s*\)'
    if re.search(pattern5, content):
        content = re.sub(pattern5, "output_dir = get_results_path()", content)
        changes += 1

    # Pattern 6: db_path = "/Volumes/dual/DUALITY-ZERO-V2/workspace/bridge.db"
    pattern6 = r'db_path\s*=\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*\/workspace\/([^"\']+)["\']'
    matches = list(re.finditer(pattern6, content))
    for match in matches:
        filename = match.group(1)
        old = match.group(0)
        new = f'db_path = get_workspace_path() / "{filename}"'
        content = content.replace(old, new, 1)
        changes += 1

    # Pattern 7: CONST_NAME = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/...")
    pattern7 = r'([A-Z_]+)\s*=\s*Path\s*\(\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*\/experiments\/results\/([^"\']+)["\']\s*\)'
    matches7 = list(re.finditer(pattern7, content))
    for match in matches7:
        const_name = match.group(1)
        filename = match.group(2)
        old = match.group(0)
        new = f'{const_name} = get_results_path() / "{filename}"'
        content = content.replace(old, new, 1)
        changes += 1

    # Pattern 8: Generic results file path
    pattern8 = r'(\w+)\s*=\s*Path\s*\(\s*["\']\/Volumes\/dual\/DUALITY-ZERO[^"\']*\/experiments\/results\/([^"\']+)["\']\s*\)'
    matches8 = list(re.finditer(pattern8, content))
    for match in matches8:
        var_name = match.group(1)
        filename = match.group(2)
        old = match.group(0)
        # Skip if already handled by pattern 7 (constants)
        if var_name.isupper():
            continue
        new = f'{var_name} = get_results_path() / "{filename}"'
        content = content.replace(old, new, 1)
        changes += 1

    return content, changes


def refactor_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """Refactor a single file."""
    print(f"\nProcessing: {file_path.relative_to(file_path.parents[2])}")

    try:
        with open(file_path, "r") as f:
            original_content = f.read()

        # Check if file has hard-coded paths
        if "/Volumes/dual/DUALITY-ZERO" not in original_content:
            print(f"  ✓ No hard-coded paths found, skipping")
            return False, 0

        content = original_content

        # Add import if needed
        if not has_workspace_utils_import(content):
            print(f"  + Adding workspace_utils import")
            content = add_workspace_utils_import(content)

        # Refactor paths
        content, changes = refactor_workspace_paths(content)

        if changes == 0:
            print(f"  ⚠ Has hard-coded paths but no patterns matched (manual review needed)")
            return False, 0

        print(f"  ✏️  Refactored {changes} path(s)")

        # Save if not dry run
        if not dry_run:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"  ✅ Saved")
        else:
            print(f"  [DRY RUN] Would save")

        return True, changes

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Refactor hard-coded workspace paths")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of files to process"
    )
    args = parser.parse_args()

    repo_path = Path("/Users/aldrinpayopay/nested-resonance-memory-archive")

    print(f"Repository: {repo_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY CHANGES'}")
    print("=" * 80)

    # Find files
    files = find_files_with_hardcoded_paths(repo_path)
    print(f"\nFound {len(files)} files with hard-coded paths")

    if args.limit:
        files = files[: args.limit]
        print(f"Processing first {args.limit} files")

    # Process files
    updated = 0
    total_changes = 0
    manual_review = []

    for file_path in files:
        success, changes = refactor_file(file_path, args.dry_run)
        if success:
            updated += 1
            total_changes += changes
        elif "/Volumes/dual/DUALITY-ZERO" in open(file_path).read():
            # Has hard-coded paths but couldn't refactor automatically
            manual_review.append(file_path)

    # Summary
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Files updated: {updated}/{len(files)}")
    print(f"  Total changes: {total_changes}")
    print(f"  Manual review needed: {len(manual_review)}")

    if manual_review:
        print(f"\n  Files needing manual review:")
        for f in manual_review[:10]:
            print(f"    - {f.relative_to(repo_path)}")
        if len(manual_review) > 10:
            print(f"    ... and {len(manual_review) - 10} more")

    if args.dry_run:
        print("\nDRY RUN complete. Run without --dry-run to apply changes.")
    else:
        print("\nChanges applied successfully!")


if __name__ == "__main__":
    main()
