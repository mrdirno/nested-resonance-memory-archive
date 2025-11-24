#!/usr/bin/env python3
"""
Cycle 275: Meta-Controller Integration Test (Helios Autonomous Mode)
Protocol: meta_controller_integration_test

Purpose:
    - Validate HeliosEvolver's ability to execute the 'meta_controller_integration_test' protocol.
    - Confirm Meta-Controller Integration dynamics (C275).
    - Success Criteria: adaptation_score > 0.0.

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
    print("CYCLE 275: META-CONTROLLER INTEGRATION TEST (HELIOS AUTONOMOUS)")
    print("=" * 70)
    
    # Initialize Evolver
    evolver = HeliosEvolver(daemon_mode=False)
    
    # Manually trigger the specific protocol for this cycle
    result = evolver.execute_protocol("meta_controller_integration_test")
    
    print("-" * 70)
    if result['success']:
        print("SUCCESS: Meta-Controller Integration Test Passed")
        print(f"Metrics: {result['metrics']}")
    else:
        print("FAILURE: Meta-Controller Integration Test Failed")
        print(f"Metrics: {result['metrics']}")
        print("Reason: Adaptation score must be > 0.0")
    print("=" * 70)

if __name__ == "__main__":
    main()
