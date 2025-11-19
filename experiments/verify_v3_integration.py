#!/usr/bin/env python3
"""
V3 Integration Verification Script
Purpose: Verify that V3 components (Homeostasis, Autopoiesis) are correctly integrated into core classes.
"""

import sys
import time
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import FractalSwarm
from fractal.memetics import Pattern

def test_synaptic_homeostasis():
    print("\nTEST 1: Synaptic Homeostasis Integration")
    print("-" * 40)
    
    # Mock dependencies
    from bridge.transcendental_bridge import TranscendentalBridge
    bridge = TranscendentalBridge()
    reality = {'cpu_percent': 10.0, 'memory_percent': 10.0}
    
    agent = FractalAgent(agent_id="test_agent", bridge=bridge, initial_reality=reality)
    
    # Initialize with unbalanced weights
    agent.patterns = [
        Pattern(pattern_id=0.1, weight=10.0),
        Pattern(pattern_id=0.2, weight=20.0),
        Pattern(pattern_id=0.3, weight=30.0)
    ]
    
    initial_sum = sum(p.weight for p in agent.patterns)
    print(f"Initial Weight Sum: {initial_sum}")
    
    # Apply homeostasis
    target = 10.0
    print(f"Applying homeostasis (Target={target})...")
    agent.apply_homeostatic_scaling(target_sum=target)
    
    final_sum = sum(p.weight for p in agent.patterns)
    print(f"Final Weight Sum: {final_sum}")
    
    if abs(final_sum - target) < 1e-6:
        print("✅ PASS: Weights normalized to target.")
        return True
    else:
        print("❌ FAIL: Weight normalization failed.")
        return False

def test_autopoietic_boundary():
    print("\nTEST 2: Autopoietic Boundary Metric")
    print("-" * 40)
    
    swarm = FractalSwarm(clear_on_init=True)
    
    # Create a simple cluster manually in the graph
    print("Creating mock cluster topology...")
    swarm.composition_graph.add_edge("A", "B")
    swarm.composition_graph.add_edge("B", "C")
    swarm.composition_graph.add_edge("C", "A") # Triangle (Strong cluster)
    
    # Add an external edge
    swarm.composition_graph.add_edge("C", "D") # Bridge to D
    
    # Manually define the cluster (A, B, C)
    swarm.composition.clusters["cluster_1"] = {"A", "B", "C"}
    # D is free-floating or in another cluster
    
    # Total edges = 4
    # Intra-cluster edges (A-B-C) = 3
    # Expected boundary strength = 3/4 = 0.75
    
    strength = swarm.compute_boundary_strength()
    print(f"Computed Boundary Strength: {strength}")
    
    if abs(strength - 0.75) < 1e-6:
        print("✅ PASS: Boundary strength metric correct.")
        return True
    else:
        print(f"❌ FAIL: Expected 0.75, got {strength}")
        return False

def main():
    print("STARTING V3 INTEGRATION VERIFICATION")
    print("=" * 60)
    
    results = []
    results.append(test_synaptic_homeostasis())
    results.append(test_autopoietic_boundary())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED: V3 Integration Successful")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
