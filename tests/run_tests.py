#!/usr/bin/env python3
"""
DUALITY-ZERO Test Runner
Executes all reality-grounded tests and reports results

Test Categories:
- reality_grounding: Tests verifying reality anchoring (psutil, SQLite, file I/O)
- integration: Tests verifying component interactions
- unit: Tests verifying individual module functionality

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

def run_test_file(test_path: Path) -> Tuple[bool, str]:
    """
    Run a single test file and return (success, output).

    Args:
        test_path: Path to test file

    Returns:
        Tuple of (success_bool, output_string)
    """
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: Test exceeded 5 minute limit"
    except Exception as e:
        return False, f"ERROR: {str(e)}"


def run_test_suite(test_dir: Path, category: str) -> Tuple[int, int, List[str]]:
    """
    Run all tests in a directory.

    Args:
        test_dir: Directory containing test files
        category: Test category name (for reporting)

    Returns:
        Tuple of (passed_count, total_count, failed_test_names)
    """
    test_files = sorted(test_dir.glob("test_*.py"))

    if not test_files:
        print(f"  No tests found in {category}/")
        return 0, 0, []

    passed = 0
    failed_tests = []

    for test_file in test_files:
        print(f"  Running {test_file.name}...", end=" ")
        success, output = run_test_file(test_file)

        if success:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            failed_tests.append(test_file.name)
            print(f"    Error output:")
            for line in output.split('\n')[:10]:  # Show first 10 lines
                print(f"      {line}")
            if len(output.split('\n')) > 10:
                print(f"      ... ({len(output.split('\n')) - 10} more lines)")

    return passed, len(test_files), failed_tests


def main():
    """Execute all test suites and report results."""
    print("="*80)
    print("DUALITY-ZERO TEST SUITE")
    print("="*80)
    print()

    tests_root = Path(__file__).parent

    # Run reality grounding tests
    print("REALITY GROUNDING TESTS")
    print("-"*80)
    rg_passed, rg_total, rg_failed = run_test_suite(
        tests_root / "reality_grounding",
        "reality_grounding"
    )
    print()

    # Run integration tests
    print("INTEGRATION TESTS")
    print("-"*80)
    int_passed, int_total, int_failed = run_test_suite(
        tests_root / "integration",
        "integration"
    )
    print()

    # Run unit tests
    print("UNIT TESTS")
    print("-"*80)
    unit_passed, unit_total, unit_failed = run_test_suite(
        tests_root / "unit",
        "unit"
    )
    print()

    # Summary
    total_passed = rg_passed + int_passed + unit_passed
    total_tests = rg_total + int_total + unit_total

    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Reality Grounding: {rg_passed}/{rg_total} passed")
    print(f"Integration:       {int_passed}/{int_total} passed")
    print(f"Unit:              {unit_passed}/{unit_total} passed")
    print(f"Total:             {total_passed}/{total_tests} passed")
    print()

    if total_passed == total_tests:
        print("✅ ALL TESTS PASSED")
        print("="*80)
        return 0
    else:
        print(f"❌ {total_tests - total_passed} TEST(S) FAILED")
        print()
        print("Failed tests:")
        for test in rg_failed + int_failed + unit_failed:
            print(f"  - {test}")
        print("="*80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
