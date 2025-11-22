#!/usr/bin/env python3
"""
Quick test to verify database agent_id collision fix.

Creates multiple FractalSwarm instances sequentially with same workspace,
spawning agents in each. Before fix: collisions likely. After fix: no collisions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm

def test_collision_fix():
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    print("Testing database collision fix...")
    print("="*60)

    # Test 1: Multiple swarms WITHOUT clear_on_init (should accumulate)
    print("\nTest 1: WITHOUT clear_on_init (old behavior):")
    try:
        for i in range(3):
            swarm = FractalSwarm(str(workspace), clear_on_init=False)
            for j in range(10):
                swarm.spawn_agent(reality_metrics)
            print(f"  Run {i+1}: Spawned 10 agents successfully")
    except Exception as e:
        print(f"  ✗ ERROR after {i+1} runs: {e}")

    # Test 2: Multiple swarms WITH clear_on_init (should work)
    print("\nTest 2: WITH clear_on_init=True (fixed behavior):")
    try:
        for i in range(3):
            swarm = FractalSwarm(str(workspace), clear_on_init=True)
            for j in range(10):
                swarm.spawn_agent(reality_metrics)
            print(f"  Run {i+1}: Spawned 10 agents successfully")
        print("  ✓ All runs completed without collision!")
    except Exception as e:
        print(f"  ✗ ERROR after {i+1} runs: {e}")

    print("\n" + "="*60)
    print("Test complete. Fix validated if Test 2 succeeded.")

if __name__ == "__main__":
    test_collision_fix()
