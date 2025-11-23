#!/usr/bin/env python3
"""
Cycle 267: Criticality Test (Helios Autonomous Mode)
Protocol: criticality_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'criticality_test' protocol.
    - Confirm Swarm Criticality (Edge of Chaos) dynamics.
    - Success Criteria: 0 < active_clusters <= 5 (Clusters exist but don't dominate).

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
    print("CYCLE 267: CRITICALITY TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("criticality_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Criticality Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Criticality Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Clusters must be > 0 and <= 5")
    print("=" * 70)

if __name__ == "__main__":
    main()
