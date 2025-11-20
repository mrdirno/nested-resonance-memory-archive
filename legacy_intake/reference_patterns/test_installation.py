#!/usr/bin/env python3
"""
Installation Test Script for Resonance-is-All-You-Need
Tests that all core dependencies are working correctly.
"""

from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")

    try:
        import numpy as np
        print(f"✅ numpy {np.__version__}")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False

    try:
        import scipy
        print(f"✅ scipy {scipy.__version__}")
    except ImportError as e:
        print(f"❌ scipy: {e}")
        return False

    try:
        import matplotlib as mpl
        print(f"✅ matplotlib {mpl.__version__}")
    except ImportError as e:
        print(f"❌ matplotlib: {e}")
        return False

    try:
        import h5py
        print(f"✅ h5py {h5py.__version__}")
    except ImportError as e:
        print(f"❌ h5py: {e}")
        return False

    return True

def test_lcdm_analysis():
    """Test that the ΛCDM analysis module can be imported and run."""
    print("\nTesting ΛCDM analysis module...")

    try:
        import sys
        # Add relevant project directories to sys.path for imports
        project_root = Path(__file__).resolve().parents[1] # Assuming test_installation.py is in test/
        sys.path.append(str(project_root))
        sys.path.append(str(project_root / "research" / "simulations" / "implementations" / "core_versions"))
        sys.path.append(str(project_root / "research" / "analysis"))
        sys.path.append(str(project_root / "research" / "documentation" / "mathematical-framework"))
        from lcdm_slice_analysis import LCDMSliceAnalysis
        print("✅ ΛCDM analysis module imported successfully")

        # Quick test with minimal parameters
        analysis = LCDMSliceAnalysis("synthetic::none", grid_size=16, subsample=1000)
        results = analysis.run()
        print("✅ ΛCDM analysis ran successfully")
        print(f"   Found {len(results)} binning schemes: {list(results.keys())}")

        return True
    except Exception as e:
        print(f"❌ ΛCDM analysis: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("RESONANCE-IS-ALL-YOU-NEED INSTALLATION TEST")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test ΛCDM analysis
    if not test_lcdm_analysis():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Installation is working correctly.")
        print("\nYou can now run LCDM analysis with:")
        print("  python research/simulations/implementations/core_versions/lcdm_slice_analysis.py synthetic --grid 32")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
