#!/usr/bin/env python3
"""
Cycle 266: Population Stability Test (Helios Autonomous Mode)
Protocol: population_stability_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'population_stability_test' protocol.
    - Confirm baseline population survival under standard conditions.

Author: Gemini 3 Pro (MOG Pilot)
Date: 2025-11-20
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.helios.core.evolver import HeliosEvolver

def main():
    print("=" * 70)
    print("CYCLE 266: POPULATION STABILITY TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("population_stability_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Population Stability Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Population Stability Test Failed")
        print(f"Metrics: {result['metrics']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
