#!/usr/bin/env python3
"""
Test: Does agent_cap (computational load) affect basin outcomes?
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter

# Add code directories to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "code"))
sys.path.insert(0, str(repo_root / "code" / "experiments"))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge
from workspace_utils import get_workspace_path, get_results_path

def create_seed_memory_range(bridge, reality_metrics, mult, spread, count=5):
    seed_patterns = []
    for i in range(count):
        offset = (i - count//2) * spread
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
        }
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

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
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=400)
    
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    mult, spread = 1.0, 0.15
    
    basin_A = (6.220353, 6.275283, 6.281831)
    basin_B = (6.09469, 6.083677, 6.250047)
    
    start_time = time.time()
    
    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, mult, spread, count=5)
                    newest_agent.memory.extend(seed_patterns)
        
        swarm.evolve_cycle(delta_time=1.0)
    
    duration = time.time() - start_time
    dominant, count, fraction = get_dominant_pattern(swarm.global_memory)
    
    if dominant:
        dist_A = np.linalg.norm(np.array(dominant) - np.array(basin_A))
        dist_B = np.linalg.norm(np.array(dominant) - np.array(basin_B))
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        basin = 'NONE'
        dist_A, dist_B = None, None
    
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
    print("OBSERVER EFFECT TEST: agent_cap impact on basin")
    print("=" * 70)
    print("Fixed: threshold=400, spread=0.15, mult=1.0, cycles=1000")
    print("Varying: agent_cap\n")
    
    caps_to_test = [5, 10, 15, 25, 50]
    results = []
    
    for cap in caps_to_test:
        print(f"Testing agent_cap={cap}...", end=' ', flush=True)
        result = run_with_agent_cap(cap, cycles=1000)
        results.append(result)
        print(f"→ Basin {result['basin']} ({result['cycles_per_sec']:.1f} cyc/s)")
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"{'Cap':>5} {'Basin':>6} {'Fraction':>10} {'Cycles/sec':>12}")
    print("-" * 70)
    for r in results:
        frac_str = f"{r['fraction']:.2f}" if r['fraction'] else "N/A"
        print(f"{r['agent_cap']:>5} {r['basin']:>6} {frac_str:>10} {r['cycles_per_sec']:>12.1f}")
    
    basins = [r['basin'] for r in results if r['basin'] != 'NONE']
    unique_basins = set(basins)
    
    if len(unique_basins) > 1:
        print("\n🔥 OBSERVER EFFECT CONFIRMED!")
        print("   Different agent_caps → DIFFERENT BASINS!")
    elif len(unique_basins) == 1:
        print(f"\n✓ Consistent basin: {basins[0]}")
    else:
        print("\n⚠️  No convergence (all NONE)")
    
    output_path = Path(__file__).parent / "results" / "agent_cap_test.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({'experiment': 'agent_cap_effect', 'results': results}, f, indent=2)
    print(f"\nSaved: {output_path}")
