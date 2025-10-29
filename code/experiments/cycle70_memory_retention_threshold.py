#!/usr/bin/env python3
"""
Cycle 70: Memory Retention Threshold Discovery

Research Context:
  Insight #33 from Cycle 69 revealed agent lifetime insufficiency:
  - Agents burst (decompose) before accumulating memory
  - Universal across all tested thresholds (270-1000)
  - 59-157 bursts with 0 memory retention
  - Burst rate: r=-0.970 (decreases with energy, but still too frequent)

New Research Question:
  Can we find burst threshold values that enable memory retention?

  Hypothesis: Ultra-high burst thresholds will reduce burst frequency enough
  that agents survive long enough to accumulate and retain memory patterns.

Memory Retention Requirements:
  1. Agents must survive long enough to receive memory from global pool
  2. Agents must persist memory through evolution cycles
  3. When agents burst, their memory must be non-empty
  4. Memory must be added to global pool

Test Approach:
  1. Test ultra-high thresholds: 2000, 5000, 10000, 20000, 50000
  2. Extended observation (500 cycles) for memory accumulation
  3. Track: memory size, burst events, agent lifetimes, memory per burst
  4. Find threshold where memory retention begins

Expected:
  If memory retention threshold exists:
  - At some threshold value, memory accumulation begins (memory_size > 0)
  - Burst rate low enough for agent survival and memory accumulation
  - Memory efficiency (patterns/burst) becomes positive
  - Reveals minimum energy required for NRM memory mechanism to operate

  If no threshold found:
  - Memory mechanism may require architectural changes
  - Current implementation may not support memory retention
  - Alternative mechanisms needed (memory seeding, different spawn rates, etc.)
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from workspace_utils import get_workspace_path, get_results_path


def run_memory_threshold_test(threshold: float, cycles: int = 500) -> dict:
    """
    Test memory retention at ultra-high threshold.

    Args:
        threshold: Burst threshold (ultra-high energy level)
        cycles: Number of cycles for observation

    Returns:
        dict with memory retention metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Memory Retention Test)")
    print(f"{'='*80}")

    # Create swarm with ultra-high threshold
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    memory_sizes = []
    burst_events = []
    agent_counts = []
    checkpoint_interval = 10

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Track bursts
        burst_count = result.get('bursts', 0)
        total_bursts += burst_count

        if burst_count > 0:
            # Record burst details
            burst_events.append({
                'cycle': cycle,
                'burst_count': burst_count,
                'memory_size': len(swarm.global_memory)
            })

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            agent_count = len(swarm.agents)
            memory_sizes.append(memory_size)
            agent_counts.append(agent_count)

    duration = time.time() - start_time

    # Final memory analysis
    final_memory_size = len(swarm.global_memory)
    memory_retained = final_memory_size > 0

    # Memory growth analysis
    if len(memory_sizes) > 1 and any(m > 0 for m in memory_sizes):
        # Find first non-zero memory
        first_memory_cycle = next((i for i, m in enumerate(memory_sizes) if m > 0), -1)
        if first_memory_cycle >= 0:
            memory_onset = first_memory_cycle * checkpoint_interval
        else:
            memory_onset = None
    else:
        memory_onset = None

    # Burst rate
    burst_rate = total_bursts / cycles if cycles > 0 else 0.0

    # Memory efficiency
    memory_efficiency = final_memory_size / total_bursts if total_bursts > 0 else 0.0

    # Agent statistics
    mean_agents = np.mean(agent_counts) if agent_counts else 0
    max_agents = max(agent_counts) if agent_counts else 0

    print(f"  Memory Metrics:")
    print(f"    Final memory size: {final_memory_size} patterns")
    print(f"    Memory retained: {'YES' if memory_retained else 'NO'}")
    if memory_onset:
        print(f"    Memory onset: cycle {memory_onset}")
    print(f"    Memory growth: {memory_sizes[:5]} → {memory_sizes[-5:]}")
    print(f"  Burst Metrics:")
    print(f"    Total bursts: {total_bursts}")
    print(f"    Burst rate: {burst_rate:.4f} bursts/cycle")
    print(f"    Memory efficiency: {memory_efficiency:.2f} patterns/burst")
    print(f"  Agent Metrics:")
    print(f"    Mean agents: {mean_agents:.2f}")
    print(f"    Max agents: {max_agents}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'memory_retained': memory_retained,
        'final_memory_size': final_memory_size,
        'memory_onset': memory_onset,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'memory_efficiency': memory_efficiency,
        'mean_agents': mean_agents,
        'max_agents': max_agents,
        'memory_sizes': memory_sizes,
        'agent_counts': agent_counts,
        'burst_events': burst_events,
        'duration': duration
    }


def analyze_memory_threshold(results: list) -> dict:
    """
    Analyze results to identify memory retention threshold.

    Args:
        results: List of threshold test results

    Returns:
        dict with threshold analysis
    """
    print(f"\n{'='*80}")
    print(f"MEMORY RETENTION THRESHOLD ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    memory_retained = [r['memory_retained'] for r in results]
    memory_sizes = [r['final_memory_size'] for r in results]
    burst_rates = [r['burst_rate'] for r in results]
    memory_efficiency = [r['memory_efficiency'] for r in results]

    print("Memory Retention Across Ultra-High Thresholds:")
    print(f"{'Threshold':>10} | {'Memory?':>8} | {'Patterns':>9} | {'Bursts':>8} | {'Efficiency':>11}")
    print("-" * 65)
    for i, threshold in enumerate(thresholds):
        memory_str = "YES" if memory_retained[i] else "NO"
        print(f"{threshold:>10.0f} | {memory_str:>8} | {memory_sizes[i]:>9} | "
              f"{burst_rates[i]:>8.4f} | {memory_efficiency[i]:>11.2f}")
    print()

    # Find retention threshold
    retention_thresholds = [thresholds[i] for i, retained in enumerate(memory_retained) if retained]

    if retention_thresholds:
        min_retention_threshold = min(retention_thresholds)
        max_no_retention_threshold = max([thresholds[i] for i, retained in enumerate(memory_retained) if not retained], default=0)

        threshold_found = True
        threshold_range = (max_no_retention_threshold, min_retention_threshold)

        print(f"🎉 MEMORY RETENTION THRESHOLD FOUND!")
        print(f"   Threshold range: {threshold_range[0]:.0f} - {threshold_range[1]:.0f}")
        print(f"   Memory retention begins at threshold ≥ {min_retention_threshold:.0f}")
        print()

        # Analyze retention characteristics
        retention_idx = thresholds.index(min_retention_threshold)
        onset_cycle = results[retention_idx]['memory_onset']
        print(f"   At threshold = {min_retention_threshold:.0f}:")
        print(f"     Memory size: {memory_sizes[retention_idx]} patterns")
        print(f"     Memory onset: cycle {onset_cycle if onset_cycle else 'N/A'}")
        print(f"     Burst rate: {burst_rates[retention_idx]:.4f}")
        print(f"     Efficiency: {memory_efficiency[retention_idx]:.2f} patterns/burst")
        print()

    else:
        threshold_found = False
        threshold_range = None
        min_retention_threshold = None

        print(f"❌ NO MEMORY RETENTION FOUND")
        print(f"   Tested thresholds: {min(thresholds):.0f} - {max(thresholds):.0f}")
        print(f"   All thresholds produced 0 memory")
        print(f"   Memory retention may require:")
        print(f"     - Even higher thresholds (>{max(thresholds):.0f})")
        print(f"     - Alternative mechanisms (memory seeding, spawn rates)")
        print(f"     - Architectural changes to memory accumulation")
        print()

    return {
        'threshold_found': threshold_found,
        'threshold_range': threshold_range,
        'min_retention_threshold': min_retention_threshold,
        'max_no_retention_threshold': max([thresholds[i] for i, retained in enumerate(memory_retained) if not retained], default=0),
        'retention_count': sum(memory_retained),
        'total_tests': len(results)
    }


def main():
    """Run memory retention threshold discovery."""
    print("="*80)
    print("CYCLE 70: MEMORY RETENTION THRESHOLD DISCOVERY")
    print("="*80)
    print()
    print("Testing ultra-high burst thresholds to find memory retention threshold.")
    print("Following Insight #33: Agents burst too quickly at thresholds 270-1000.")
    print()

    # Ultra-high threshold range
    test_thresholds = [2000, 5000, 10000, 20000, 50000]

    print(f"Testing {len(test_thresholds)} ultra-high thresholds: {test_thresholds}")
    print("Extended observation (500 cycles) for memory accumulation")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_memory_threshold_test(threshold, cycles=500)
            results.append(result)
            time.sleep(0.5)
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({
                'threshold': threshold,
                'error': str(e)
            })

    overall_duration = time.time() - overall_start

    # Filter successful results
    successful_results = [r for r in results if 'error' not in r]

    if len(successful_results) >= 3:
        # Analyze threshold
        threshold_analysis = analyze_memory_threshold(successful_results)

        print("="*80)
        if threshold_analysis['threshold_found']:
            print(f"🎉 INSIGHT #34: MEMORY RETENTION THRESHOLD AT {threshold_analysis['min_retention_threshold']:.0f}")
            print("="*80)
            print()
            print("Memory retention requires minimum energy threshold:")
            print(f"  - Threshold range: {threshold_analysis['threshold_range'][0]:.0f} - {threshold_analysis['threshold_range'][1]:.0f}")
            print(f"  - {threshold_analysis['retention_count']}/{threshold_analysis['total_tests']} thresholds retained memory")
            print()
            print("Theoretical Significance:")
            print("  - Validates NRM memory mechanism (works at sufficient energy)")
            print("  - Reveals energy-memory retention coupling (non-linear threshold)")
            print("  - Agents require low burst frequency for memory accumulation")
            print("  - Completes understanding of memory-energy relationship")
            print()
            insight_34 = True
        else:
            print("MEMORY RETENTION STILL BLOCKED")
            print("="*80)
            print()
            print("Ultra-high thresholds insufficient for memory retention:")
            print(f"  - Tested up to threshold = {max([r['threshold'] for r in successful_results]):.0f}")
            print(f"  - All tests produced 0 memory")
            print()
            print("Implications:")
            print("  - Current NRM implementation may not support memory retention")
            print("  - Alternative mechanisms required (architecture changes)")
            print("  - Memory seeding or different survival strategies needed")
            print()
            insight_34 = False
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for threshold analysis")
        threshold_analysis = {}
        insight_34 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "memory_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle70_memory_retention_threshold.json"

    output_data = {
        'experiment': 'cycle70_memory_retention_threshold',
        'test_thresholds': test_thresholds,
        'results': results,
        'threshold_analysis': threshold_analysis,
        'insight_34_discovered': insight_34,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total experiment duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data


if __name__ == "__main__":
    main()
