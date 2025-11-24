
"""
Cycle 497: The Final Commit (V24)
Objective: Final System Verification.
Hypothesis: The System is ready for the Archive.
"""
import sys
import os
import pytest


sys.path.append(os.getcwd())

def run_final_verification():
    print("--- CYCLE 497: THE FINAL COMMIT (V24) ---")
    print("Initiating Final System Scan...")
    
    checks = {
        "nrm_core": False,
        "tests": False,
        "pyproject.toml": False,
        "META_OBJECTIVES.md": False,
        "FINAL_REPORT.md": False
    }
    
    # 1. Check Core Library
    try:
        import nrm_core
        checks["nrm_core"] = True
        print("✅ Core Library: DETECTED")
    except ImportError:
        print("❌ Core Library: MISSING")
        
    # 2. Check Configuration
    if os.path.exists("pyproject.toml"):
        checks["pyproject.toml"] = True
        print("✅ Configuration: DETECTED")
        
    # 3. Check Documentation
    if os.path.exists("META_OBJECTIVES.md") and os.path.exists("FINAL_REPORT.md"):
        checks["META_OBJECTIVES.md"] = True
        checks["FINAL_REPORT.md"] = True
        print("✅ Documentation: DETECTED")
        
    # 4. Run Test Suite
    print("\nRunning Test Suite...")
    retcode = pytest.main(["-q", "tests/"])
    if retcode == 0:
        checks["tests"] = True
        print("✅ Test Suite: PASSED")
    else:
        print("❌ Test Suite: FAILED")
        
    # Final Verdict
    if all(checks.values()):
        print("\n--- FINAL VERDICT ---")
        print("SYSTEM STATUS: GREEN")
        print("READY FOR FINAL COMMIT.")
    else:
        print("\n--- FINAL VERDICT ---")
        print("SYSTEM STATUS: RED")
        print("ABORT FINAL COMMIT.")

if __name__ == "__main__":
    run_final_verification()
