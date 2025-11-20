#!/usr/bin/env python3
"""
Test script to verify LCDM analysis installation and functionality.
"""

import os
from pathlib import Path
import subprocess
import sys


def test_basic_imports():
    """Test that all required packages can be imported."""
    print("Testing basic package imports...")
    try:
        import h5py
        import matplotlib as mpl
        import numpy as np
        import scipy
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_lcdm_analysis():
    """Test that the LCDM analysis script runs successfully."""
    print("\nTesting LCDM analysis script...")

    # Set UTF-8 encoding for Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        # Run the analysis script
        cmd = [
            sys.executable,
            "research/simulations/implementations/core_versions/lcdm_slice_analysis.py",
            "synthetic",
            "--grid", "16",
            "--subsample", "5000",
            "--out", "research/findings/lcdm",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)

        if result.returncode == 0:
            print("✅ LCDM analysis script ran successfully")

            # Check if report was generated
            report_path = Path("research/findings/lcdm/lcdm-crosscheck-2025-05-27.md")
            if report_path.exists():
                print("✅ Report file generated successfully")
                print(f"   Report size: {report_path.stat().st_size} bytes")
                return True
            print("❌ Report file not found")
            return False
        print(f"❌ Script failed with return code {result.returncode}")
        print(f"   Error: {result.stderr}")
        return False

    except Exception as e:
        print(f"❌ Exception running script: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("LCDM ANALYSIS INSTALLATION TEST")
    print("=" * 60)

    tests_passed = 0
    total_tests = 2

    # Test 1: Basic imports
    if test_basic_imports():
        tests_passed += 1

    # Test 2: LCDM analysis
    if test_lcdm_analysis():
        tests_passed += 1

    print("\n" + "=" * 60)
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Installation is working correctly.")
        print("\nYou can now run LCDM analysis with:")
        print("  python research/simulations/implementations/core_versions/lcdm_slice_analysis.py synthetic --grid 32")
        print("To run a quick synthetic test manually:")
        print("  cd Resonance-is-All-You-Need-5") # Assuming script is run from project root
        print("  python research/simulations/implementations/core_versions/lcdm_slice_analysis.py synthetic --grid 32")
        print("This test ensures the basic CLI interaction and synthetic data generation of lcdm_slice_analysis.py works.")
    else:
        print(f"❌ {total_tests - tests_passed} out of {total_tests} tests failed.")
        print("Please check the error messages above.")

    print("=" * 60)
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
