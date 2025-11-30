#!/usr/bin/env python3
"""
Experiment: Cycle 2618 - The Review
Goal: Perform a final system audit before release.
"""

import os
import sys
from pathlib import Path

REQUIRED_FILES = [
    "experiments/cycle2606_api.py",
    "experiments/cycle2607_controller.py",
    "experiments/cycle2603_dashboard.py",
    "experiments/HELIOS_ONE_MANUAL.md",
    "experiments/Dockerfile",
    "experiments/docker-compose.yml",
    "helios_one/src/bridge/transcendental_bridge.py"
]

def check_files():
    print("Cycle 2618: The Review - File Integrity Check")
    missing = []
    for f in REQUIRED_FILES:
        path = Path(f)
        if path.exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            missing.append(f)
    
    if missing:
        print("FAILURE: Missing critical files.")
        sys.exit(1)
    print("SUCCESS: All critical files present.")

def check_bridge():
    print("\nCycle 2618: The Review - Bridge Diagnostics")
    try:
        # Add helios_one/src to path
        sys.path.insert(0, str(Path("helios_one/src").resolve()))
        from bridge.transcendental_bridge import TranscendentalBridge
        
        bridge = TranscendentalBridge()
        results = bridge.self_test()
        
        if results['success_rate'] == 1.0:
            print("  [OK] Bridge Self-Test Passed")
        else:
            print(f"  [FAIL] Bridge Self-Test Failed (Rate: {results['success_rate']})")
            sys.exit(1)
            
    except Exception as e:
        print(f"FAILURE: Bridge check crashed: {e}")
        sys.exit(1)

def main():
    print("--- HELIOS-ONE SYSTEM AUDIT ---")
    check_files()
    check_bridge()
    print("\n--- AUDIT COMPLETE: SYSTEM READY ---")

if __name__ == "__main__":
    main()
