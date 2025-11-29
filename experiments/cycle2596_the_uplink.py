"""
Cycle 2596: The Uplink (Gate 60.3)
Goal: Verify quantum synchronization in the new HELIOS-ONE environment.
"""

import sys
import os
import time
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from bridge.transcendental_bridge import TranscendentalBridge

def run_experiment():
    print("--- Cycle 2596: The Uplink (Quantum Verification) ---")
    
    try:
        bridge = TranscendentalBridge()
        print("Bridge Initialized.")
        
        print("Generating Oscillation...")
        states = bridge.generate_oscillation(frequency=0.5, duration=5.0)
        
        print(f"Received {len(states)} quantum states.")
        
        # Verification Logic: Check for non-zero phase values (Entropy injection)
        valid_entropy = False
        for i, state in enumerate(states[:5]): # Check first 5
            print(f"State {i}: pi={state.pi_phase:.4f}, e={state.e_phase:.4f}, phi={state.phi_phase:.4f}")
            if state.pi_phase != 0 or state.e_phase != 0:
                valid_entropy = True
                
        if valid_entropy:
            print("\nSUCCESS: Quantum Uplink Active. Entropy Injection Verified.")
        else:
            print("\nFAILURE: Bridge is static (No Entropy).")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: Uplink Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_experiment()
