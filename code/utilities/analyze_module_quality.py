#!/usr/bin/env python3
"""
Module Quality Analysis Script
Analyzes any code module for docstring coverage and quality metrics.

Author: Aldrin Payopay + Claude (DUALITY-ZERO-V2)
Date: 2025-10-31
Cycle: 715
"""

import os
import sys
from pathlib import Path
import re
from collections import defaultdict

def analyze_docstrings(file_path):
    """Analyze docstring presence in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for module docstring
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

def main():
    """Run module quality analysis."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_module_quality.py <module_name>")
        print("Example: python analyze_module_quality.py analysis")
        sys.exit(1)

    module_name = sys.argv[1]
    module_dir = Path(__file__).parent.parent / module_name

    if not module_dir.exists():
        print(f"Error: {module_dir} does not exist")
        sys.exit(1)

    print("=" * 80)
    print(f"{module_name.capitalize()}/ Directory Quality Analysis - Cycle 715")
    print("=" * 80)
    print()

    # Collect all Python files
    py_files = [f for f in module_dir.rglob('*.py') if '__pycache__' not in str(f)]
    total_files = len(py_files)

    print(f"Total Python files in {module_name}/: {total_files}")
    print()

    # Analyze all files
    files_with_docstrings = []
    files_without_docstrings = []
    total_functions = 0
    total_classes = 0
    total_lines = 0

    for py_file in py_files:
        metrics = analyze_docstrings(py_file)
        if metrics:
            total_functions += metrics['functions']
            total_classes += metrics['classes']
            total_lines += metrics['lines']

            if metrics['has_module_docstring']:
                files_with_docstrings.append(py_file)
            else:
                files_without_docstrings.append(py_file)

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

    # Show files without docstrings (if any)
    if files_without_docstrings:
        print(f"FILES WITHOUT MODULE DOCSTRINGS ({len(files_without_docstrings)} total):")
        print("-" * 80)
        for py_file in sorted(files_without_docstrings):
            rel_path = py_file.relative_to(module_dir)
            print(f"  {rel_path}")
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
        print(f"\n  Status: All {module_name}/ files properly documented! 🎉")

    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
