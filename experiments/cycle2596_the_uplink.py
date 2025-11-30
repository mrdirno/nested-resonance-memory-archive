#!/usr/bin/env python3
"""
Experiment: Cycle 2596 - The Uplink
Goal: Verify Transcendental Bridge operation in HELIOS-ONE environment.
"""

import sys
import os
import json
from pathlib import Path
import math

# Add HELIOS-ONE src to path
HELIOS_SRC = Path("helios_one/src").resolve()
sys.path.insert(0, str(HELIOS_SRC))

# Try importing the bridge
try:
    from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import TranscendentalBridge. Path: {sys.path}")
    print(f"Error: {e}")
    sys.exit(1)

def validate_oscillation(sequence):
    """
    Validate that the oscillation sequence has expected properties.
    """
    print(f"Validating sequence of length {len(sequence)}...")
    
    if not sequence:
        return False, "Sequence is empty"

    # Check 1: Magnitude consistency (should not be 0 unless phases are 0)
    for i, state in enumerate(sequence):
        if state.magnitude == 0 and (state.pi_phase != 0 or state.e_phase != 0):
            return False, f"State {i} has zero magnitude but non-zero phases."
        
        # Check 2: Phase bounds
        if not (0 <= state.pi_phase <= 2 * math.pi):
            return False, f"State {i} pi_phase out of bounds: {state.pi_phase}"

    # Check 3: Evolution (phases should change)
    if len(sequence) > 1:
        s0 = sequence[0]
        s1 = sequence[1]
        if s0.pi_phase == s1.pi_phase and s0.e_phase == s1.e_phase:
            return False, "Phases did not evolve between steps."

    return True, "Oscillation sequence is valid."

def main():
    print("Cycle 2596: The Uplink - Initialization")
    
    # use a test workspace to avoid polluting main DB during test if needed
    # but the prompt implies verification in the environment.
    # using default path is fine as it persists to bridge.db
    
    try:
        bridge = TranscendentalBridge()
        print("TranscendentalBridge initialized.")
    except Exception as e:
        print(f"Failed to initialize bridge: {e}")
        sys.exit(1)

    # Generate Oscillation
    print("Generating oscillation...")
    frequency = 0.1
    duration = 50
    
    try:
        sequence = bridge.generate_oscillation(frequency, duration)
    except Exception as e:
        print(f"Error generating oscillation: {e}")
        sys.exit(1)

    # Validate
    is_valid, message = validate_oscillation(sequence)
    
    if is_valid:
        print(f"SUCCESS: {message}")
        
        # Log some details
        print("\nFirst 3 states:")
        for i, s in enumerate(sequence[:3]):
            print(f"  [{i}] pi={s.pi_phase:.4f}, e={s.e_phase:.4f}, phi={s.phi_phase:.4f}")
            
        # Check resonance self-test
        print("\nRunning internal self-test...")
        results = bridge.self_test()
        if results['success_rate'] == 1.0:
             print("Bridge Self-Test: PASSED")
        else:
             print(f"Bridge Self-Test: FAILED ({results['success_rate']})")
             sys.exit(1)
             
    else:
        print(f"FAILURE: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()