"""
Cycle 2480: The Final Audit (Gate 108)
Experiment: System Integrity Check
Goal: Verify that the system is healthy after colonization.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.maintenance.keeper import Keeper

def run_audit():
    print("--- CYCLE 2480: THE FINAL AUDIT ---")
    
    # 1. Run Keeper
    print("\n[PHASE 1] KEEPER CHECK")
    k = Keeper()
    k.run()
    
    # 2. Run Unit Tests (src/life)
    print("\n[PHASE 2] UNIT TEST VERIFICATION")
    loader = unittest.TestLoader()
    start_dir = 'src/life'
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    print("\n--- AUDIT RESULTS ---")
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED.")
        print("SYSTEM INTEGRITY: 100%")
    else:
        print("❌ TESTS FAILED.")
        print(f"Errors: {len(result.errors)}")
        print(f"Failures: {len(result.failures)}")
        print("SYSTEM INTEGRITY: COMPROMISED")

if __name__ == "__main__":
    run_audit()
