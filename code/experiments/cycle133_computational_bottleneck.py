#!/usr/bin/env python3
"""
CYCLE 133: COMPUTATIONAL BOTTLENECK TEST (Extended)

Research Question:
  At what agent_cap does computational performance degrade?
  Cycle 132 tested 5-50 and found no effect. Now test higher scales.

Context:
  - Cycle 132: agent_cap 5-50 showed no bottleneck (~145 cyc/s consistent)
  - Hypothesis: Bottleneck exists at higher scales (predicted agent_cap > 500)
  - Testing: agent_cap ∈ {50, 100, 200, 500, 1000} to find breaking point

Method:
  - Fixed parameters: threshold=400, spread=0.15, mult=1.0, cycles=1000
  - Vary agent_cap: 50, 100, 200, 500, 1000
  - Measure: cycles/sec, basin outcome, memory usage

Expected:
  - Linear scaling up to some point
  - Then degradation (cycles/sec drops)
  - Potential memory issues at extreme scales

Safety:
  - Monitor psutil memory usage
  - Terminate if memory > 90%
  - Constitution limit: 100MB per agent max
"""

import sys
import time
import json
from pathlib import Path
import psutil
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def pattern_to_key(pattern):
    """Convert pattern to hashable key"""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))


def get_dominant_pattern(memory):
    """Get most common pattern"""
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction


def create_seed_memory_range(bridge, reality_metrics, mult, spread, count=5):
    """Create seed patterns"""
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


def run_with_agent_cap(agent_cap, cycles=1000):
    """
    Run experiment with specified agent_cap

    Returns:
        dict: Results including performance metrics
    """
    workspace = Path("./workspace")

    # Monitor initial memory
    process = psutil.Process()
    initial_memory_mb = process.memory_info().rss / (1024 * 1024)

    # Initialize swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=400)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    mult, spread = 1.0, 0.15

    # Basin centers
    basin_A = (6.220353, 6.275283, 6.281831)
    basin_B = (6.09469, 6.083677, 6.250047)

    start_time = time.time()
    cycle_times = []
    memory_samples = []

    # Run cycles with safety check
    for cycle in range(1, cycles + 1):
        cycle_start = time.time()

        # Safety check: memory usage
        current_memory_mb = process.memory_info().rss / (1024 * 1024)
        memory_percent = psutil.virtual_memory().percent

        if memory_percent > 90:
            print(f"  WARNING: Memory usage {memory_percent:.1f}% - terminating early")
            cycles = cycle - 1  # Actual cycles completed
            break

        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

        cycle_time = time.time() - cycle_start
        cycle_times.append(cycle_time)
        memory_samples.append(current_memory_mb)

        # Progress every 100 cycles
        if cycle % 100 == 0:
            avg_cycle_time = np.mean(cycle_times[-100:])
            print(f"  Cycle {cycle}/{cycles}: {1/avg_cycle_time:.1f} cyc/s, {current_memory_mb:.1f} MB")

    duration = time.time() - start_time

    # Final state
    dominant, count, fraction = get_dominant_pattern(swarm.global_memory)

    if dominant:
        dist_A = np.linalg.norm(np.array(dominant) - np.array(basin_A))
        dist_B = np.linalg.norm(np.array(dominant) - np.array(basin_B))
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        basin = 'NONE'
        dist_A, dist_B = None, None

    final_memory_mb = process.memory_info().rss / (1024 * 1024)
    memory_increase_mb = final_memory_mb - initial_memory_mb

    return {
        'agent_cap': agent_cap,
        'cycles_completed': cycles,
        'basin': basin,
        'dominant_fraction': fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': duration,
        'cycles_per_sec': cycles / duration,
        'avg_cycle_time_ms': np.mean(cycle_times) * 1000,
        'initial_memory_mb': initial_memory_mb,
        'final_memory_mb': final_memory_mb,
        'memory_increase_mb': memory_increase_mb,
        'peak_agents': len(swarm.agents)
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CYCLE 133: COMPUTATIONAL BOTTLENECK TEST (Extended)")
    print("=" * 70)
    print("Testing agent_cap: 50, 100, 200, 500, 1000")
    print("Finding computational breaking point")
    print()

    caps_to_test = [50, 100, 200, 500, 1000]
    results = []

    for cap in caps_to_test:
        print(f"Testing agent_cap={cap}...")
        result = run_with_agent_cap(cap, cycles=1000)
        results.append(result)

        print(f"  → Basin {result['basin']}")
        print(f"  → {result['cycles_per_sec']:.1f} cycles/sec")
        print(f"  → {result['memory_increase_mb']:.1f} MB memory increase")
        print(f"  → Peak agents: {result['peak_agents']}")
        print()

    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "cycle133_bottleneck_test.json"

    output_data = {
        'metadata': {
            'cycle': 133,
            'experiment': 'computational_bottleneck_extended',
            'caps_tested': caps_to_test
        },
        'results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Cap':>6} {'Basin':>6} {'Cyc/s':>8} {'AvgMs':>8} {'MemMB':>8} {'PkAgents':>10}")
    print("-" * 70)

    for r in results:
        print(f"{r['agent_cap']:>6} {r['basin']:>6} {r['cycles_per_sec']:>8.1f} "
              f"{r['avg_cycle_time_ms']:>8.2f} {r['memory_increase_mb']:>8.1f} "
              f"{r['peak_agents']:>10}")

    # Analyze degradation
    print()
    print("Performance Analysis:")
    print("-" * 70)

    baseline_cyc_per_sec = results[0]['cycles_per_sec']
    for r in results:
        degradation = (1 - r['cycles_per_sec'] / baseline_cyc_per_sec) * 100
        if degradation > 10:
            print(f"agent_cap={r['agent_cap']}: {degradation:.1f}% degradation (BOTTLENECK DETECTED)")
        else:
            print(f"agent_cap={r['agent_cap']}: {degradation:.1f}% degradation (scaling well)")

    print()
    print(f"Results saved: {output_path}")
    print("=" * 70)
