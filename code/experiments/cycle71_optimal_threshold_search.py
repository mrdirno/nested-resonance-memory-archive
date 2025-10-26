#!/usr/bin/env python3
"""
Cycle 71: Optimal Burst Threshold Search

Research Context:
  Insights #33-34 revealed burst-survival paradox:
  - Low thresholds (270-1000): Too many bursts (59-157) → agents die before memory
  - High thresholds (2000-50000): No bursts (0) → no memory generation

  Two failure modes:
  1. Too many bursts → insufficient agent survival for memory retention
  2. No bursts → no memory generation events

New Research Question:
  Does an optimal "sweet spot" threshold exist between 1000-2000?

  Hypothesis: Intermediate threshold may achieve burst-survival balance:
  - Occasional bursts (memory generation)
  - Not too frequent (agent survival)
  - Enables memory accumulation for first time

Test Approach:
  1. Fine-grained scan: 1200, 1400, 1600, 1800 (between failure modes)
  2. Extended observation (500 cycles) for memory accumulation
  3. Track: memory size, burst frequency, agent survival, memory efficiency
  4. Identify if optimal zone exists

Expected Outcomes:
  A) Optimal threshold found: Memory > 0, burst rate moderate (0.01-0.05)
  B) No optimal zone: All thresholds fail (either too many or too few bursts)
  C) Phase transition: Sharp boundary where memory retention begins
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def run_optimal_threshold_test(threshold: float, cycles: int = 500) -> dict:
    """
    Test intermediate threshold for optimal burst-survival balance.

    Args:
        threshold: Burst threshold (intermediate range)
        cycles: Number of cycles for observation

    Returns:
        dict with comprehensive metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Optimal Zone Search)")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    memory_sizes = []
    burst_counts = []
    agent_counts = []
    checkpoint_interval = 10

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()
    total_bursts = 0
    first_memory_cycle = None

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Track bursts
        burst_count = result.get('bursts', 0)
        total_bursts += burst_count

        # Check for first memory appearance
        if first_memory_cycle is None and len(swarm.global_memory) > 0:
            first_memory_cycle = cycle

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            agent_count = len(swarm.agents)
            memory_sizes.append(memory_size)
            agent_counts.append(agent_count)
            burst_counts.append(total_bursts)

    duration = time.time() - start_time

    # Analysis
    final_memory_size = len(swarm.global_memory)
    memory_retained = final_memory_size > 0

    # Burst statistics
    burst_rate = total_bursts / cycles if cycles > 0 else 0.0
    memory_efficiency = final_memory_size / total_bursts if total_bursts > 0 else 0.0

    # Agent statistics
    mean_agents = np.mean(agent_counts) if agent_counts else 0
    min_agents = min(agent_counts) if agent_counts else 0
    max_agents = max(agent_counts) if agent_counts else 0

    # Memory growth
    if memory_retained and len(memory_sizes) > 1:
        # Calculate growth rate
        nonzero_idx = [i for i, m in enumerate(memory_sizes) if m > 0]
        if len(nonzero_idx) > 1:
            memory_growth_rate = np.polyfit(nonzero_idx, [memory_sizes[i] for i in nonzero_idx], 1)[0]
        else:
            memory_growth_rate = 0.0
    else:
        memory_growth_rate = 0.0

    # Classification
    if memory_retained:
        if burst_rate < 0.01:
            zone = "NEAR-HIGH (rare bursts)"
        elif burst_rate > 0.15:
            zone = "NEAR-LOW (frequent bursts)"
        else:
            zone = "OPTIMAL (balanced bursts)"
    else:
        if burst_rate == 0:
            zone = "TOO HIGH (no bursts)"
        else:
            zone = "TOO LOW (excessive bursts)"

    print(f"  Memory Metrics:")
    print(f"    Final memory: {final_memory_size} patterns")
    print(f"    Memory retained: {'YES ✓' if memory_retained else 'NO ✗'}")
    if first_memory_cycle:
        print(f"    First memory: cycle {first_memory_cycle}")
    if memory_retained:
        print(f"    Growth rate: {memory_growth_rate:.2f} patterns/checkpoint")
    print(f"  Burst Metrics:")
    print(f"    Total bursts: {total_bursts}")
    print(f"    Burst rate: {burst_rate:.4f} bursts/cycle")
    print(f"    Memory efficiency: {memory_efficiency:.2f} patterns/burst")
    print(f"  Agent Metrics:")
    print(f"    Mean agents: {mean_agents:.2f}")
    print(f"    Range: {min_agents}-{max_agents}")
    print(f"  Zone: {zone}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'memory_retained': memory_retained,
        'final_memory_size': final_memory_size,
        'first_memory_cycle': first_memory_cycle,
        'memory_growth_rate': memory_growth_rate,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'memory_efficiency': memory_efficiency,
        'mean_agents': mean_agents,
        'min_agents': min_agents,
        'max_agents': max_agents,
        'zone': zone,
        'memory_sizes': memory_sizes,
        'agent_counts': agent_counts,
        'burst_counts': burst_counts,
        'duration': duration
    }


def analyze_optimal_zone(results: list) -> dict:
    """
    Analyze results to identify optimal threshold zone.

    Args:
        results: List of threshold test results

    Returns:
        dict with optimal zone analysis
    """
    print(f"\n{'='*80}")
    print(f"OPTIMAL BURST-SURVIVAL ZONE ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    memory_retained = [r['memory_retained'] for r in results]
    memory_sizes = [r['final_memory_size'] for r in results]
    burst_rates = [r['burst_rate'] for r in results]
    zones = [r['zone'] for r in results]

    print("Burst-Survival Balance Across Intermediate Thresholds:")
    print(f"{'Threshold':>10} | {'Memory?':>8} | {'Patterns':>9} | {'Burst Rate':>11} | {'Zone':>25}")
    print("-" * 80)
    for i, threshold in enumerate(thresholds):
        memory_str = "YES ✓" if memory_retained[i] else "NO ✗"
        print(f"{threshold:>10.0f} | {memory_str:>8} | {memory_sizes[i]:>9} | "
              f"{burst_rates[i]:>11.4f} | {zones[i]:<25}")
    print()

    # Check for optimal zone
    optimal_thresholds = [thresholds[i] for i, retained in enumerate(memory_retained) if retained]

    if optimal_thresholds:
        optimal_found = True
        optimal_range = (min(optimal_thresholds), max(optimal_thresholds))

        print(f"🎉 OPTIMAL ZONE DISCOVERED!")
        print(f"   Threshold range: {optimal_range[0]:.0f} - {optimal_range[1]:.0f}")
        print(f"   {len(optimal_thresholds)}/{len(thresholds)} thresholds retained memory")
        print()

        # Analyze best threshold
        memory_idx = memory_sizes.index(max(memory_sizes))
        best_threshold = thresholds[memory_idx]
        best_result = results[memory_idx]

        print(f"   Best threshold: {best_threshold:.0f}")
        print(f"     Memory size: {best_result['final_memory_size']} patterns")
        print(f"     Burst rate: {best_result['burst_rate']:.4f}")
        print(f"     First memory: cycle {best_result['first_memory_cycle']}")
        print(f"     Growth rate: {best_result['memory_growth_rate']:.2f} patterns/checkpoint")
        print(f"     Zone: {best_result['zone']}")
        print()

    else:
        optimal_found = False
        optimal_range = None
        best_threshold = None

        print(f"❌ NO OPTIMAL ZONE FOUND")
        print(f"   Tested thresholds: {min(thresholds):.0f} - {max(thresholds):.0f}")
        print(f"   All thresholds failed to retain memory")
        print()

        # Analyze failure pattern
        if all(r == 0 for r in burst_rates):
            print(f"   Failure mode: No bursts (all thresholds too high)")
            print(f"   Recommendation: Test lower thresholds (<{min(thresholds):.0f})")
        elif all(r > 0.1 for r in burst_rates):
            print(f"   Failure mode: Too many bursts (all thresholds too low)")
            print(f"   Recommendation: Test higher thresholds (>{max(thresholds):.0f})")
        else:
            print(f"   Failure mode: Mixed (transition zone but no memory)")
            print(f"   Implication: Architectural limitation confirmed")
        print()

    return {
        'optimal_found': optimal_found,
        'optimal_range': optimal_range,
        'best_threshold': best_threshold,
        'retention_count': len(optimal_thresholds),
        'total_tests': len(results)
    }


def main():
    """Run optimal threshold search."""
    print("="*80)
    print("CYCLE 71: OPTIMAL BURST THRESHOLD SEARCH")
    print("="*80)
    print()
    print("Searching for optimal burst-survival balance in intermediate range.")
    print("Following Insights #33-34: Memory blocked at both extremes (270-1000, 2000-50000).")
    print()

    # Intermediate threshold range (between two failure modes)
    test_thresholds = [1200, 1400, 1600, 1800]

    print(f"Testing {len(test_thresholds)} intermediate thresholds: {test_thresholds}")
    print("Hypothesis: Optimal zone exists where occasional bursts enable memory")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_optimal_threshold_test(threshold, cycles=500)
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
        # Analyze optimal zone
        optimal_analysis = analyze_optimal_zone(successful_results)

        print("="*80)
        if optimal_analysis['optimal_found']:
            print(f"🎉 INSIGHT #35: OPTIMAL BURST THRESHOLD AT {optimal_analysis['best_threshold']:.0f}")
            print("="*80)
            print()
            print("Memory retention enabled at intermediate threshold:")
            print(f"  - Optimal range: {optimal_analysis['optimal_range'][0]:.0f} - {optimal_analysis['optimal_range'][1]:.0f}")
            print(f"  - {optimal_analysis['retention_count']}/{optimal_analysis['total_tests']} thresholds successful")
            print()
            print("Theoretical Significance:")
            print("  - Validates burst-survival balance hypothesis")
            print("  - Demonstrates NRM memory mechanism CAN work")
            print("  - Requires precise energy tuning for memory retention")
            print("  - Completes energy-memory framework understanding")
            print()
            insight_35 = True
        else:
            print("OPTIMAL ZONE NOT FOUND IN INTERMEDIATE RANGE")
            print("="*80)
            print()
            print("No memory retention in tested range (1200-1800):")
            print(f"  - {optimal_analysis['retention_count']}/{optimal_analysis['total_tests']} thresholds successful")
            print()
            print("Implications:")
            print("  - Optimal zone may not exist in 1000-2000 range")
            print("  - Architectural constraint may prevent memory retention")
            print("  - Alternative mechanisms required for memory accumulation")
            print()
            insight_35 = False
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for optimal zone analysis")
        optimal_analysis = {}
        insight_35 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "optimal_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle71_optimal_threshold_search.json"

    output_data = {
        'experiment': 'cycle71_optimal_threshold_search',
        'test_thresholds': test_thresholds,
        'results': results,
        'optimal_analysis': optimal_analysis,
        'insight_35_discovered': insight_35,
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
