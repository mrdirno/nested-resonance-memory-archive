#!/usr/bin/env python3
"""
Dependency Usage Analysis Script
Analyzes which packages from requirements.txt are actually used in the codebase.

Author: Aldrin Payopay + Claude (DUALITY-ZERO-V2)
Date: 2025-10-31
Cycle: 716
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_imports_from_file(file_path):
    """Extract all import statements from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Match "import package" or "from package import ..."
                if line.startswith('import ') or line.startswith('from '):
                    # Extract package name
                    if line.startswith('import '):
                        pkg = line[7:].split()[0].split('.')[0]
                    else:  # from X import Y
                        pkg = line[5:].split()[0].split('.')[0]
                    imports.add(pkg)
    except Exception:
        pass
    return imports

def main():
    """Run dependency usage analysis."""
    code_dir = Path(__file__).parent.parent

    # Packages in requirements.txt (excluding dev tools like pytest, black, etc.)
    core_packages = ['numpy', 'psutil', 'matplotlib', 'seaborn', 'pandas', 'scipy']
    dev_packages = ['pytest', 'black', 'pylint', 'sphinx']
    all_packages = core_packages + dev_packages

    print("=" * 80)
    print("Dependency Usage Analysis - Cycle 716")
    print("=" * 80)
    print()

    # Find all Python files
    py_files = list(code_dir.rglob('*.py'))
    py_files = [f for f in py_files if '__pycache__' not in str(f)]

    # Collect all imports
    package_usage = defaultdict(set)

    for py_file in py_files:
        imports = extract_imports_from_file(py_file)
        for pkg in imports:
            if pkg in all_packages:
                rel_path = py_file.relative_to(code_dir)
                package_usage[pkg].add(str(rel_path))

    # Report results
    print("CORE DEPENDENCIES:")
    print("-" * 80)
    for pkg in core_packages:
        count = len(package_usage[pkg])
        status = "✅ USED" if count > 0 else "⚠ UNUSED"
        print(f"  {pkg:15s}: {count:3d} files - {status}")
    print()

    print("DEVELOPMENT DEPENDENCIES:")
    print("-" * 80)
    for pkg in dev_packages:
        count = len(package_usage[pkg])
        status = "✅ USED" if count > 0 else "ℹ️  OK (dev tool)"
        print(f"  {pkg:15s}: {count:3d} files - {status}")
    print()

    # Show detailed usage for core packages
    print("DETAILED USAGE (Core Packages):")
    print("-" * 80)
    for pkg in core_packages:
        if package_usage[pkg]:
            print(f"\n{pkg} ({len(package_usage[pkg])} files):")
            for file_path in sorted(list(package_usage[pkg]))[:10]:  # Show first 10
                print(f"  - {file_path}")
            if len(package_usage[pkg]) > 10:
                print(f"  ... and {len(package_usage[pkg]) - 10} more files")

    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
