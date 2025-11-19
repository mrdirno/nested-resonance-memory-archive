#!/usr/bin/env python3
"""
URGENT TEST: Does agent_cap affect basin outcomes?

User hypothesis: "More particles looks like less energy because computer 
renders what it can handle - processing power tied to perceived render"

Test: Run SAME parameters (threshold=400) with DIFFERENT agent_caps
Expected if hypothesis TRUE: Different basins depending on agent_cap
Expected if hypothesis FALSE: Same basin regardless of agent_cap
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge

def pattern_to_key(pattern):
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def get_dominant_pattern(memory):
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction

def run_with_agent_cap(agent_cap, cycles=1000):
    """Run experiment with specified agent_cap."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=400)  # FIXED threshold
    
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    
    # Basin centers
    basin_A = (6.220353, 6.275283, 6.281831)
    basin_B = (6.09469, 6.083677, 6.250047)
    
    start_time = time.time()
    
    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
        
        swarm.evolve_cycle(delta_time=1.0)
    
    duration = time.time() - start_time
    
    # Get final state
    dominant, count, fraction = get_dominant_pattern(swarm.global_memory)
    
    if dominant:
        dist_A = np.linalg.norm(np.array(dominant) - np.array(basin_A))
        dist_B = np.linalg.norm(np.array(dominant) - np.array(basin_B))
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        basin = None
        dist_A = None
        dist_B = None
    
    return {
        'agent_cap': agent_cap,
        'basin': basin,
        'dominant': dominant,
        'fraction': fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': duration,
        'cycles_per_sec': cycles / duration
    }

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING OBSERVER EFFECT: Does agent_cap affect basin outcomes?")
    print("=" * 70)
    print("\nFixed parameters:")
    print("  threshold = 400 (known Basin B preference from C130)")
    print("  spread = 0.15")
    print("  mult = 1.0")
    print("  cycles = 1000")
    print("\nVarying: agent_cap")
    print()
    
    # Test different agent caps
    caps_to_test = [5, 10, 15, 25, 50]
    
    results = []
    for cap in caps_to_test:
        print(f"Testing agent_cap={cap}...", flush=True)
        result = run_with_agent_cap(cap, cycles=1000)
        results.append(result)
        print(f"  → Basin {result['basin']} (fraction={result['fraction']:.2f}, "
              f"{result['cycles_per_sec']:.1f} cycles/sec)")
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"{'Cap':>5} {'Basin':>6} {'Fraction':>10} {'Cycles/sec':>12} {'Duration':>10}")
    print("-" * 70)
    for r in results:
        print(f"{r['agent_cap']:>5} {r['basin']:>6} {r['fraction']:>10.2f} "
              f"{r['cycles_per_sec']:>12.1f} {r['duration']:>10.1f}s")
    
    # Check if basins differ
    basins = [r['basin'] for r in results]
    if len(set(basins)) > 1:
        print("\n🔥 OBSERVER EFFECT CONFIRMED!")
        print("   Different agent_caps → DIFFERENT BASINS")
        print("   User's hypothesis VALIDATED!")
    else:
        print("\n❌ No observer effect detected")
        print("   Same basin across all agent_caps")
    
    # Save results
    output_path = Path(__file__).parent / "results" / "agent_cap_test.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({
            'experiment': 'agent_cap_observer_effect',
            'fixed_params': {'threshold': 400, 'spread': 0.15, 'mult': 1.0},
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
