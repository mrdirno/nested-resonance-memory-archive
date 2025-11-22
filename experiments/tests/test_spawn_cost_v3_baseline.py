#!/usr/bin/env python3
"""
Quick test of c186_spawn_cost_scaling_v3.py baseline experiment
Tests that JSON fixes resolved NameError and basic execution works.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (Anthropic)
Date: November 18, 2025
License: GPL-3.0
"""

import sys
import os

# Add experiments directory to path
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

# Import the script module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "spawn_cost_v3",
    "/Volumes/dual/DUALITY-ZERO-V2/experiments/c186_spawn_cost_scaling_v3.py"
)
spawn_cost_v3 = importlib.util.module_from_spec(spec)

# Temporarily reduce CYCLES for quick test
original_cycles = None

try:
    spec.loader.exec_module(spawn_cost_v3)

    # Save original cycles and replace with test value
    original_cycles = spawn_cost_v3.CYCLES
    spawn_cost_v3.CYCLES = 5000  # Short test run

    print("="*80)
    print("TESTING c186_spawn_cost_scaling_v3.py (5,000 cycles)")
    print("="*80)
    print(f"Testing spawn_cost=5.0, seed=42")
    print(f"Reduced cycles: {spawn_cost_v3.CYCLES:,} (original: {original_cycles:,})")
    print()

    # Run single baseline experiment
    success = spawn_cost_v3.run_experiment(
        spawn_cost=5.0,
        spawn_label="5.0",
        seed=42
    )

    print()
    print("="*80)
    print("TEST RESULT")
    print("="*80)
    if success:
        print("✓ PASS: Baseline experiment completed successfully")
        print("  - No NameError (f_spawn references fixed)")
        print("  - JSON sections working")
        print("  - Database writes successful")
    else:
        print("✗ FAIL: Experiment returned False")
    print("="*80)

    sys.exit(0 if success else 1)

except Exception as e:
    print()
    print("="*80)
    print("ERROR IN TEST")
    print("="*80)
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Restore original cycles if module was loaded
    if original_cycles is not None and hasattr(spawn_cost_v3, 'CYCLES'):
        spawn_cost_v3.CYCLES = original_cycles
