#!/usr/bin/env python3
"""
Cycle 273: Factorial Optimization Test (Helios Autonomous Mode)
Protocol: optimization_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'optimization_test' protocol.
    - Confirm Factorial Optimization dynamics (C256).
    - Success Criteria: performance_score > 50 AND validation_error < 0.05.

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
    print("CYCLE 273: FACTORIAL OPTIMIZATION TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("optimization_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Factorial Optimization Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Factorial Optimization Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Performance score > 50 and Validation error < 0.05")
    print("=" * 70)

if __name__ == "__main__":
    main()
