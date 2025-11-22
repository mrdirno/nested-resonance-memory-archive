#!/usr/bin/env python3
"""
Cycle 271: Kuramoto Coupling Test (Helios Autonomous Mode)
Protocol: kuramoto_coupling_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'kuramoto_coupling_test' protocol.
    - Confirm Kuramoto Coupling (Resonance) dynamics.
    - Success Criteria: active_clusters > 0 (Resonance clusters formed).

Author: Gemini 3 Pro (MOG Pilot)
Date: 2025-11-20
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from code.helios.core.evolver import HeliosEvolver

def main():
    print("=" * 70)
    print("CYCLE 271: KURAMOTO COUPLING TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("kuramoto_coupling_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Kuramoto Coupling Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Kuramoto Coupling Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Active clusters must be > 0")
    print("=" * 70)

if __name__ == "__main__":
    main()
