"""
Cycle 2445: Continuous Integration (Gate 73)
Role: The Tester
Responsibility: Run all critical experiments and verify system stability.
Logic:
1. Define test list (Unit tests, Integration tests, Simulations).
2. Execute each test.
3. Report Pass/Fail metrics.
"""

import os
import sys
import subprocess
import time

TEST_LIST = [
    "scripts/system_health_check.py",
    "automation/guardian/guardian.py",
    "experiments/cycle2420_revival_dry_run.py",
    "experiments/cycle2400_compiler_integration.py"
    # Add more critical paths here
]

def run_tests():
    print("Cycle 2445: Continuous Integration Suite")
    print("========================================")
    
    passed = 0
    failed = 0
    total = len(TEST_LIST)
    
    for test_script in TEST_LIST:
        print(f"\n[TEST] Running {test_script}...")
        
        if not os.path.exists(test_script):
            print(f"[FAIL] Script missing: {test_script}")
            failed += 1
            continue
            
        start_time = time.time()
        try:
            result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"[PASS] {test_script} ({duration:.2f}s)")
                passed += 1
            else:
                print(f"[FAIL] {test_script} (Return Code: {result.returncode})")
                print("--- STDERR ---")
                print(result.stderr)
                failed += 1
                
        except Exception as e:
            print(f"[ERROR] Execution failed: {e}")
            failed += 1
            
    print("\n========================================")
    print(f"SUMMARY: {passed}/{total} Passed. {failed} Failed.")
    
    if failed == 0:
        print("SYSTEM GREEN.")
        return True
    else:
        print("SYSTEM RED.")
        return False

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
