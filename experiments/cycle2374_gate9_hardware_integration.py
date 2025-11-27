"""
Gate 9: The Fabricator - Hardware Integration (Mock)
Verifies the system can *attempt* to connect to real hardware, and gracefully fallback.
This is the final gate before real physical deployment.
"""

import os
import sys
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.fabricator import Fabricator

def run_gate9_test():
    print("="*60)
    print("GATE 9: FABRICATOR HARDWARE INTEGRATION CHECK")
    print("="*60)
    
    # 1. Attempt Physical Connection (Likely to fail if no hardware, which is expected)
    print("[TEST] Attempting connection to /dev/ttyUSB0 (Physical)...\n")
    fab_phys = Fabricator(port="/dev/ttyUSB0", virtual=False)
    
    success = fab_phys.connect()
    if success:
        print("✅ PHYSICAL HARDWARE DETECTED!")
        fab_phys.disconnect()
    else:
        print("⚠️ No physical hardware found (Expected for CI/Mock env).")
        print("   System should fallback gracefully or report error clearly.")
        
    # 2. Verify Virtual Fallback still works
    print("\n[TEST] Verifying Virtual Fallback...\n")
    fab_virt = Fabricator(virtual=True)
    if fab_virt.connect():
        print("✅ Virtual Fallback Operational")
        fab_virt.disconnect()
    else:
        print("❌ Virtual Fallback Failed")
        return False
        
    print("\n✅ Gate 9 Logic Verified (Hardware detection + Fallback)")
    return True

if __name__ == "__main__":
    success = run_gate9_test()
    sys.exit(0 if success else 1)
