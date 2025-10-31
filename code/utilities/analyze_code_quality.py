#!/usr/bin/env python3
"""
Code Quality Analysis Script
Analyzes Python codebase for quality metrics without external tools.

Author: Aldrin Payopay + Claude (DUALITY-ZERO-V2)
Date: 2025-10-31
Cycle: 714
"""

import os
from pathlib import Path
from collections import defaultdict
import re

def count_files_by_module(code_dir):
    """Count Python files per module."""
    module_counts = defaultdict(int)

    for root, dirs, files in os.walk(code_dir):
        # Skip __pycache__ directories
        if '__pycache__' in root:
            continue

        # Get module name (first directory after code/)
        rel_path = os.path.relpath(root, code_dir)
        if rel_path == '.':
            module = 'root'
        else:
            module = rel_path.split(os.sep)[0]

        # Count .py files
        py_files = [f for f in files if f.endswith('.py')]
        module_counts[module] += len(py_files)

    return dict(sorted(module_counts.items(), key=lambda x: x[1], reverse=True))

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

def analyze_module_quality(module_dir):
    """Analyze quality metrics for a module."""
    py_files = list(Path(module_dir).rglob('*.py'))

    total_files = len(py_files)
    if total_files == 0:
        return None

    files_with_docstrings = 0
    total_functions = 0
    total_classes = 0
    total_lines = 0

    for py_file in py_files:
        if '__pycache__' in str(py_file):
            continue

        metrics = analyze_docstrings(py_file)
        if metrics:
            if metrics['has_module_docstring']:
                files_with_docstrings += 1
            total_functions += metrics['functions']
            total_classes += metrics['classes']
            total_lines += metrics['lines']

    return {
        'total_files': total_files,
        'files_with_docstrings': files_with_docstrings,
        'docstring_coverage': files_with_docstrings / total_files if total_files > 0 else 0,
        'total_functions': total_functions,
        'total_classes': total_classes,
        'total_lines': total_lines,
        'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0
    }

def main():
    """Run code quality analysis."""
    code_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("Code Quality Analysis - Cycle 714")
    print("=" * 80)
    print()

    # Module file counts
    print("MODULE FILE COUNTS:")
    print("-" * 80)
    module_counts = count_files_by_module(code_dir)
    for module, count in module_counts.items():
        print(f"  {module:20s}: {count:3d} files")
    print()

    # Analyze core infrastructure modules
    core_modules = ['core', 'reality', 'bridge', 'fractal', 'orchestration', 'validation']

    print("CORE MODULE QUALITY METRICS:")
    print("-" * 80)
    print(f"{'Module':<15} {'Files':<6} {'Docstrings':<12} {'Coverage':<10} {'Functions':<10} {'Classes':<8} {'Avg Lines':<10}")
    print("-" * 80)

    for module in core_modules:
        module_path = code_dir / module
        if not module_path.exists():
            continue

        metrics = analyze_module_quality(module_path)
        if metrics:
            coverage_pct = metrics['docstring_coverage'] * 100
            print(f"{module:<15} {metrics['total_files']:<6} "
                  f"{metrics['files_with_docstrings']:<12} "
                  f"{coverage_pct:>6.1f}%    "
                  f"{metrics['total_functions']:<10} "
                  f"{metrics['total_classes']:<8} "
                  f"{metrics['avg_lines_per_file']:>7.0f}")

    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
