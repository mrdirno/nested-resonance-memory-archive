#!/usr/bin/env python3
"""
Experiments Directory Quality Analysis Script
Analyzes experiments/ directory (249 files) for docstring coverage and quality metrics.

Author: Aldrin Payopay + Claude (DUALITY-ZERO-V2)
Date: 2025-10-31
Cycle: 715
"""

import os
from pathlib import Path
import re
from collections import defaultdict

def analyze_docstrings(file_path):
    """Analyze docstring presence in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for module docstring (first non-comment line after imports)
        lines = content.split('\n')
        has_module_docstring = False
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                has_module_docstring = True
                break
            else:
                break

        # Count functions and classes
        func_pattern = re.compile(r'^\s*def\s+\w+\s*\(', re.MULTILINE)
        class_pattern = re.compile(r'^\s*class\s+\w+', re.MULTILINE)

        functions = len(func_pattern.findall(content))
        classes = len(class_pattern.findall(content))

        return {
            'has_module_docstring': has_module_docstring,
            'functions': functions,
            'classes': classes,
            'lines': len(lines)
        }
    except Exception as e:
        return None

def extract_cycle_number(filename):
    """Extract cycle number from filename (e.g., 'cycle177_...' -> 177)."""
    match = re.search(r'cycle(\d+)', filename.lower())
    if match:
        return int(match.group(1))
    return None

def main():
    """Run experiments directory quality analysis."""
    experiments_dir = Path(__file__).parent.parent / 'experiments'

    if not experiments_dir.exists():
        print(f"Error: {experiments_dir} does not exist")
        return

    print("=" * 80)
    print("Experiments Directory Quality Analysis - Cycle 715")
    print("=" * 80)
    print()

    # Collect all Python files
    py_files = [f for f in experiments_dir.rglob('*.py') if '__pycache__' not in str(f)]
    total_files = len(py_files)

    print(f"Total Python files in experiments/: {total_files}")
    print()

    # Analyze all files
    files_with_docstrings = []
    files_without_docstrings = []
    total_functions = 0
    total_classes = 0
    total_lines = 0

    # Track by cycle number for patterns
    by_cycle = defaultdict(list)

    for py_file in py_files:
        metrics = analyze_docstrings(py_file)
        if metrics:
            total_functions += metrics['functions']
            total_classes += metrics['classes']
            total_lines += metrics['lines']

            cycle_num = extract_cycle_number(py_file.name)

            if metrics['has_module_docstring']:
                files_with_docstrings.append(py_file)
                if cycle_num:
                    by_cycle[cycle_num].append((py_file.name, True))
            else:
                files_without_docstrings.append(py_file)
                if cycle_num:
                    by_cycle[cycle_num].append((py_file.name, False))

    # Calculate statistics
    coverage = len(files_with_docstrings) / total_files * 100 if total_files > 0 else 0
    avg_lines = total_lines / total_files if total_files > 0 else 0
    avg_functions = total_functions / total_files if total_files > 0 else 0
    avg_classes = total_classes / total_files if total_files > 0 else 0

    # Overall metrics
    print("OVERALL QUALITY METRICS:")
    print("-" * 80)
    print(f"  Total Files:           {total_files}")
    print(f"  With Docstrings:       {len(files_with_docstrings)} ({len(files_with_docstrings)/total_files*100:.1f}%)")
    print(f"  Without Docstrings:    {len(files_without_docstrings)} ({len(files_without_docstrings)/total_files*100:.1f}%)")
    print(f"  Total Functions:       {total_functions}")
    print(f"  Total Classes:         {total_classes}")
    print(f"  Total Lines:           {total_lines:,}")
    print(f"  Avg Lines/File:        {avg_lines:.0f}")
    print(f"  Avg Functions/File:    {avg_functions:.1f}")
    print(f"  Avg Classes/File:      {avg_classes:.1f}")
    print()

    # Docstring coverage by cycle range
    if by_cycle:
        print("DOCSTRING COVERAGE BY CYCLE:")
        print("-" * 80)
        cycle_ranges = [
            (0, 99, "C0-C99"),
            (100, 199, "C100-C199"),
            (200, 299, "C200-C299"),
            (300, 399, "C300-C399"),
            (400, 499, "C400-C499"),
        ]

        for min_c, max_c, label in cycle_ranges:
            cycles_in_range = {c: files for c, files in by_cycle.items() if min_c <= c <= max_c}
            if cycles_in_range:
                total_in_range = sum(len(files) for files in cycles_in_range.values())
                with_docs = sum(1 for files in cycles_in_range.values() for _, has_doc in files if has_doc)
                coverage_pct = with_docs / total_in_range * 100 if total_in_range > 0 else 0
                print(f"  {label:12s}: {with_docs:3d}/{total_in_range:3d} files ({coverage_pct:5.1f}%)")
        print()

    # Show sample of files without docstrings (up to 30)
    if files_without_docstrings:
        print(f"FILES WITHOUT MODULE DOCSTRINGS ({len(files_without_docstrings)} total):")
        print("-" * 80)
        display_count = min(30, len(files_without_docstrings))

        # Sort by cycle number for clarity
        sorted_missing = sorted(files_without_docstrings,
                               key=lambda f: extract_cycle_number(f.name) or 999999)

        for i, py_file in enumerate(sorted_missing[:display_count]):
            rel_path = py_file.relative_to(experiments_dir)
            cycle_num = extract_cycle_number(py_file.name)
            cycle_label = f"C{cycle_num}" if cycle_num else "Unknown"
            print(f"  [{cycle_label:8s}] {rel_path}")

        if len(files_without_docstrings) > display_count:
            print(f"  ... and {len(files_without_docstrings) - display_count} more files")
        print()

    # Assessment
    print("ASSESSMENT:")
    print("-" * 80)
    if coverage >= 90:
        status = "✅ EXCELLENT"
    elif coverage >= 75:
        status = "✓ GOOD"
    elif coverage >= 50:
        status = "⚠ FAIR"
    else:
        status = "❌ NEEDS IMPROVEMENT"

    print(f"  Docstring Coverage: {coverage:.1f}% - {status}")
    print(f"  Code Complexity:    {avg_functions:.1f} functions/file, {avg_lines:.0f} lines/file")

    if coverage < 100:
        print(f"\n  Recommendation: Add module docstrings to {len(files_without_docstrings)} files")
        print(f"  Priority: {'HIGH' if coverage < 75 else 'MEDIUM' if coverage < 90 else 'LOW'}")
    else:
        print(f"\n  Status: All experiment files properly documented! 🎉")

    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
