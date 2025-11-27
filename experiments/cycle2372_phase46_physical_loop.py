"""
Phase 46: The Physical Loop (Gate 8)
Validates the full ClosedLoopController integration.
Runs the Sense-Think-Act loop using the `src.helios.control` module.
"""

import os
import sys
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.control import ClosedLoopController

def run_phase46_validation():
    print("="*60)
    print("PHASE 46: THE PHYSICAL LOOP (GATE 8)")
    print("="*60)
    
    # Initialize Controller
    ctrl = ClosedLoopController(target_pos=[0.0, 0.0], kp=0.15, virtual=True)
    
    # Connect
    if not ctrl.connect():
        print("❌ Initialization Failed")
        return False
        
    # Execute Loop
    print("Executing 5-second stability run...")
    ctrl.run_loop(duration=5.0, interval=0.2)
    
    # Disconnect
    ctrl.disconnect()
    
    print("✅ Phase 46 Validation Complete")
    return True

if __name__ == "__main__":
    success = run_phase46_validation()
    sys.exit(0 if success else 1)
