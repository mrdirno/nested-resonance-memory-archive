#!/usr/bin/env python3
"""
Count code vs. documentation lines for Paper 3 Pattern Archaeology.

Calculates docs/code ratio to test H2.1:
- Temporal-aware: expected ~2.0 (2 lines docs per line code)
- Non-aware baseline: expected ~0.5 (1 line docs per 2 lines code)

Author: Claude (DUALITY-ZERO-V2)
Date: 2025-11-04
Cycle: 972
"""

import os
from pathlib import Path
import csv

def count_lines(directory, extensions):
    """
    Count total lines in files with given extensions.

    Args:
        directory: Path to search
        extensions: List of file extensions to count (e.g., ['.py', '.md'])

    Returns:
        total_lines: Total line count
        file_count: Number of files counted
    """
    total_lines = 0
    file_count = 0

    for ext in extensions:
        for filepath in Path(directory).rglob(f'*{ext}'):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    file_count += 1
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")

    return total_lines, file_count

def main():
    """Calculate code/docs ratio for nested-resonance-memory-archive repository."""

    repo_root = Path.home() / "nested-resonance-memory-archive"

    print("=" * 60)
    print("CODE VS. DOCUMENTATION LINE COUNT")
    print("=" * 60)
    print()

    # Count Python code lines (excluding __pycache__, .pytest_cache)
    print("Counting Python code lines...")
    code_dirs = [
        repo_root / "code",
        repo_root / "tests"
    ]
    code_lines = 0
    code_files = 0
    for code_dir in code_dirs:
        if code_dir.exists():
            lines, files = count_lines(code_dir, ['.py'])
            code_lines += lines
            code_files += files
            print(f"  {code_dir.name}/: {lines:,} lines in {files} files")

    print(f"\nTotal Python code: {code_lines:,} lines in {code_files} files")
    print()

    # Count documentation lines
    print("Counting documentation lines...")
    docs_dirs = [
        (repo_root / "docs", ['.md', '.txt', '.rst']),
        (repo_root / "papers", ['.md']),
        (repo_root / "archive" / "summaries", ['.md']),
        (repo_root, ['.md'])  # Root-level READMEs, CLAUDE.md, etc.
    ]

    docs_lines = 0
    docs_files = 0
    for docs_dir, exts in docs_dirs:
        if docs_dir.exists():
            if docs_dir == repo_root:
                # For root, only count specific files, not subdirectories
                for ext in exts:
                    for filepath in docs_dir.glob(f'*{ext}'):
                        if filepath.is_file():
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines = len(f.readlines())
                                    docs_lines += lines
                                    docs_files += 1
                            except Exception as e:
                                print(f"Warning: Could not read {filepath}: {e}")
            else:
                lines, files = count_lines(docs_dir, exts)
                docs_lines += lines
                docs_files += files
                print(f"  {docs_dir.relative_to(repo_root)}: {lines:,} lines in {files} files")

    print(f"\nTotal documentation: {docs_lines:,} lines in {docs_files} files")
    print()

    # Calculate ratio
    if code_lines > 0:
        ratio = docs_lines / code_lines
        print("=" * 60)
        print(f"DOCS/CODE RATIO: {ratio:.2f}")
        print("=" * 60)
        print()
        print(f"Interpretation:")
        print(f"  - {ratio:.2f} lines of documentation per line of code")
        if ratio >= 2.0:
            print(f"  - ✅ EXCEEDS temporal-aware prediction (≥2.0)")
            print(f"  - Validates H2.1: Temporal awareness → high documentation density")
        elif ratio >= 1.0:
            print(f"  - ⚠️ ABOVE baseline (0.5) but below prediction (2.0)")
            print(f"  - Partial support for H2.1")
        else:
            print(f"  - ❌ BELOW temporal-aware prediction (<2.0)")
            if ratio > 0.5:
                print(f"  - Still above non-aware baseline (0.5)")
            else:
                print(f"  - At or below non-aware baseline (0.5)")
        print()

    # Save results to CSV
    output_file = Path("/Volumes/dual/DUALITY-ZERO-V2/data/code_docs_line_counts.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Lines', 'Files', 'Ratio'])
        writer.writerow(['Python Code', code_lines, code_files, ''])
        writer.writerow(['Documentation', docs_lines, docs_files, ''])
        writer.writerow(['Docs/Code Ratio', '', '', f'{ratio:.4f}' if code_lines > 0 else 'N/A'])

    print(f"Results saved to: {output_file}")
    print()

    # Additional metrics for pattern archaeology
    print("=" * 60)
    print("ADDITIONAL METRICS FOR PATTERN ARCHAEOLOGY")
    print("=" * 60)
    print()

    # Paper-specific documentation
    paper2_files = list((repo_root / "papers").glob("PAPER2*.md"))
    paper2_lines = sum(len(open(f, 'r', encoding='utf-8', errors='ignore').readlines())
                       for f in paper2_files if f.is_file())
    print(f"Paper 2 documentation: {paper2_lines:,} lines in {len(paper2_files)} files")

    # C176-related code
    c176_files = list((repo_root / "code" / "experiments").glob("*176*.py"))
    c176_lines = sum(len(open(f, 'r', encoding='utf-8', errors='ignore').readlines())
                     for f in c176_files if f.is_file())
    print(f"C176 experimental code: {c176_lines:,} lines in {len(c176_files)} files")

    # Cycle summaries (967-971, Paper 2 development)
    paper2_cycles = [967, 968, 969, 970, 971]
    paper2_summary_lines = 0
    for cycle in paper2_cycles:
        cycle_files = list((repo_root / "archive" / "summaries").glob(f"CYCLE{cycle}*.md"))
        for f in cycle_files:
            paper2_summary_lines += len(open(f, 'r', encoding='utf-8', errors='ignore').readlines())
    print(f"Paper 2 cycle summaries (967-971): {paper2_summary_lines:,} lines")

    print()

if __name__ == "__main__":
    main()
