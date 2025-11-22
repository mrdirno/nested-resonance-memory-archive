#!/usr/bin/env python3
"""
Cycle 73: Memory-Energy Coupling with Seeding Enabled

Research Context:
  Insight #36 (Cycle 72): Memory seeding resolves retention constraint
  - Baseline: 0 patterns
  - Seeded: 1000 patterns at threshold=1400
  - NRM mechanism validated with proper initialization

New Research Question:
  How does memory scale across energy regimes WITH seeding enabled?

  Cycle 69 tested memory-energy without seeding → universal failure
  Now test WITH seeding → expect memory-energy relationships to emerge

Hypothesis:
  With functional retention, memory metrics should correlate with energy:
  - Memory volume may scale with burst frequency (more bursts = more patterns)
  - Memory quality may scale with agent survival (higher threshold = better retention)
  - Memory growth rate may show energy-dependent dynamics

Test Approach:
  1. Sample energy regimes: 500, 1000, 1500, 2000
  2. Apply memory seeding (5 patterns/agent) at all thresholds
  3. Extended observation (500 cycles) for memory accumulation
  4. Measure: memory size, growth rate, efficiency, burst rate
  5. Correlate memory metrics with energy

Expected:
  If memory-energy coupling exists with seeding:
  - Memory metrics show systematic variation across thresholds
  - Discover optimal energy for memory accumulation
  - Complete memory-energy framework understanding
"""

import sys
from pathlib import Path
import time
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge

def create_seed_memory(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """Create seed memory patterns."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def run_seeded_threshold_test(threshold: float, cycles: int = 500) -> dict:
    """Test memory with seeding at given threshold."""
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (WITH SEEDING)")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    memory_sizes = []
    checkpoint_interval = 10
    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            # SEED MEMORY
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)
        total_bursts += result.get('bursts', 0)

        if cycle % checkpoint_interval == 0:
            memory_sizes.append(len(swarm.global_memory))

    duration = time.time() - start_time

    final_memory = len(swarm.global_memory)
    burst_rate = total_bursts / cycles
    efficiency = final_memory / total_bursts if total_bursts > 0 else 0.0

    # Growth rate
    if len(memory_sizes) > 1 and any(m > 0 for m in memory_sizes):
        nonzero_idx = [i for i, m in enumerate(memory_sizes) if m > 0]
        if len(nonzero_idx) > 1:
            growth_rate = np.polyfit(nonzero_idx, [memory_sizes[i] for i in nonzero_idx], 1)[0]
        else:
            growth_rate = 0.0
    else:
        growth_rate = 0.0

    print(f"  Memory: {final_memory} patterns (growth: {growth_rate:.2f}/checkpoint)")
    print(f"  Bursts: {total_bursts} ({burst_rate:.4f}/cycle)")
    print(f"  Efficiency: {efficiency:.2f} patterns/burst")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'final_memory': final_memory,
        'growth_rate': growth_rate,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'efficiency': efficiency,
        'memory_sizes': memory_sizes,
        'duration': duration
    }

def main():
    """Run memory-energy coupling with seeding."""
    print("="*80)
    print("CYCLE 73: MEMORY-ENERGY COUPLING (WITH SEEDING)")
    print("="*80)
    print()
    print("Testing memory dynamics across energy regimes with seeding enabled.")
    print("Following Insight #36: Memory seeding resolves retention constraint")
    print()

    test_thresholds = [500, 1000, 1500, 2000]
    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("All agents seeded with 5 initial memory patterns")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_seeded_threshold_test(threshold, cycles=500)
            results.append(result)
            time.sleep(0.5)
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({'threshold': threshold, 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Analysis
    successful = [r for r in results if 'error' not in r]

    if len(successful) >= 3:
        thresholds = [r['threshold'] for r in successful]
        memory = [r['final_memory'] for r in successful]
        growth = [r['growth_rate'] for r in successful]
        bursts = [r['burst_rate'] for r in successful]
        efficiency = [r['efficiency'] for r in successful]

        print(f"\n{'='*80}")
        print(f"MEMORY-ENERGY ANALYSIS (WITH SEEDING)")
        print(f"{'='*80}\n")

        print(f"{'Threshold':>10} | {'Memory':>8} | {'Growth':>8} | {'Bursts':>8} | {'Efficiency':>11}")
        print("-" * 60)
        for i, t in enumerate(thresholds):
            print(f"{t:>10.0f} | {memory[i]:>8} | {growth[i]:>8.2f} | {bursts[i]:>8.4f} | {efficiency[i]:>11.2f}")
        print()

        # Correlations
        mem_corr = np.corrcoef(thresholds, memory)[0,1]
        growth_corr = np.corrcoef(thresholds, growth)[0,1]
        burst_corr = np.corrcoef(thresholds, bursts)[0,1]
        eff_corr = np.corrcoef(thresholds, efficiency)[0,1]

        print("Memory-Energy Correlations:")
        print(f"  Memory size: {mem_corr:.3f}")
        print(f"  Growth rate: {growth_corr:.3f}")
        print(f"  Burst rate: {burst_corr:.3f}")
        print(f"  Efficiency: {eff_corr:.3f}")
        print()

        if abs(mem_corr) > 0.7 or abs(growth_corr) > 0.7:
            print(f"🎉 STRONG MEMORY-ENERGY COUPLING DETECTED!")
            insight_37 = True
        else:
            print(f"⚠️ Weak or no memory-energy coupling")
            insight_37 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful tests")
        insight_37 = False

    # Save
    results_dir = Path(__file__).parent / "results" / "memory_energy_seeded"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle73_memory_energy_with_seeding.json"

    output_data = {
        'experiment': 'cycle73_memory_energy_with_seeding',
        'test_thresholds': test_thresholds,
        'results': results,
        'insight_37_discovered': insight_37,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data

if __name__ == "__main__":
    main()
