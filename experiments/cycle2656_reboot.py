#!/usr/bin/env python3
"""
Experiment: Cycle 2656 - The Reboot
Goal: Detect state corruption and restore from last snapshot.
"""

import sys
import math
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2646_rebirth import reboot_from_snapshot
except ImportError:
    sys.exit(1)

def watchdog_routine(current_val):
    print(f"Cycle 2656: The Reboot - Watchdog checking value: {current_val}")
    
    if math.isnan(current_val):
        print("  [ALERT] State Corruption Detected (NaN).")
        print("  [ACTION] Initiating Emergency Reboot...")
        
        try:
            reboot_from_snapshot()
            print("SUCCESS: System restored from archive.")
        except Exception as e:
            print(f"FAILURE: Reboot failed: {e}")
            sys.exit(1)
    else:
        print("  [OK] State nominal.")

if __name__ == "__main__":
    # 1. Test Normal
    watchdog_routine(50.0)
    
    # 2. Test Corrupt
    watchdog_routine(float('nan'))
