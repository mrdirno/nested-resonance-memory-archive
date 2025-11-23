#!/usr/bin/env python3
"""
Cycle 270: Injection Test (Helios Autonomous Mode)
Protocol: injection_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'injection_test' protocol.
    - Confirm Reality Injection (External Sensing) dynamics.
    - Success Criteria: active_agents > 0 (System survives high load/stress).

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
    print("CYCLE 270: INJECTION TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("injection_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Injection Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Injection Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Active agents must be > 0 under high stress")
    print("=" * 70)

if __name__ == "__main__":
    main()
