#!/usr/bin/env python3
"""
Cycle 272: Energy Pooling Test (Helios Autonomous Mode)
Protocol: energy_pooling_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'energy_pooling_test' protocol.
    - Confirm Cooperative Energy Pooling dynamics.
    - Success Criteria: active_clusters > 0 AND active_agents > 5.

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
    print("CYCLE 272: ENERGY POOLING TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("energy_pooling_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Energy Pooling Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Energy Pooling Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Active clusters must be > 0 AND active agents > 5")
    print("=" * 70)

if __name__ == "__main__":
    main()
