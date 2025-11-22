#!/usr/bin/env python3
"""
Cycle 72: Memory Seeding Solution

Research Context:
  Insight #35 (Cycle 71) identified root cause of memory retention failure:
  - Agents spawn with ZERO memory
  - First burst: empty memory → 0 patterns retained
  - No memory accumulation mechanism during evolution
  - Universal failure across all thresholds (270-50000)

Root Cause Analysis:
  Memory generation requires bursts, but:
  1. Agents start empty (no initial memory)
  2. First burst extracts agent.memory → empty list
  3. Global memory never populated → nothing to redistribute
  4. Chicken-egg: Need memory to survive bursts, need bursts to get memory

Solution Hypothesis:
  **Memory Seeding**: Give agents initial memory patterns at spawn

  Implementation:
  - Generate seed memory from reality metrics (phase space transformation)
  - Each agent starts with N seed patterns (e.g., 5-10)
  - Seed patterns provide initial content for bursts
  - Should enable memory → burst → retention cycle

Test Approach:
  1. Implement memory seeding in agent spawn
  2. Test with moderate threshold (1400) where burst rate was 0.086
  3. Extended observation (500 cycles) for memory accumulation
  4. Compare to non-seeded baseline

Expected Outcomes:
  A) Memory seeding works: final_memory_size > 0, validates NRM mechanism
  B) Still fails: deeper architectural issues beyond initial memory
  C) Partial success: some memory but unstable/decaying

If successful, retest full threshold range with seeding enabled.
"""

import sys
from pathlib import Path
import time
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState


def create_seed_memory(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """
    Create seed memory patterns from reality metrics.

    Args:
        bridge: TranscendentalBridge for phase transformation
        reality_metrics: Reality metrics to convert to memory
        count: Number of seed patterns to create

    Returns:
        List of TranscendentalState seed patterns
    """
    seed_patterns = []

    for i in range(count):
        # Vary reality metrics slightly for diversity
        varied_metrics = {
            key: value * (0.8 + 0.4 * (i / count))
            for key, value in reality_metrics.items()
        }

        # Convert to phase space
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)

    return seed_patterns


def run_seeded_test(threshold: float, cycles: int = 500, seed_count: int = 5) -> dict:
    """
    Test memory retention with seeded agents.

    Args:
        threshold: Burst threshold
        cycles: Number of cycles
        seed_count: Number of seed patterns per agent

    Returns:
        dict with test results
    """
    print(f"\n{'='*80}")
    print(f"TESTING WITH MEMORY SEEDING (threshold={threshold}, seed={seed_count})")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Reality metrics
    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    # Tracking
    memory_sizes = []
    burst_counts = []
    checkpoint_interval = 10

    start_time = time.time()
    total_bursts = 0
    first_memory_cycle = None

    for cycle in range(1, cycles + 1):
        # Spawn with memory seeding
        if len(swarm.agents) < 15:
            # Spawn agent normally
            swarm.spawn_agent(reality_metrics)

            # SEED MEMORY: Add initial patterns to newly spawned agent
            if swarm.agents:
                # Get most recent agent (just spawned)
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]

                    # Create and add seed memory
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, seed_count)
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Track bursts
        burst_count = result.get('bursts', 0)
        total_bursts += burst_count

        # Check for first memory
        if first_memory_cycle is None and len(swarm.global_memory) > 0:
            first_memory_cycle = cycle

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            memory_sizes.append(memory_size)
            burst_counts.append(total_bursts)

    duration = time.time() - start_time

    # Analysis
    final_memory_size = len(swarm.global_memory)
    memory_retained = final_memory_size > 0
    burst_rate = total_bursts / cycles if cycles > 0 else 0.0
    memory_efficiency = final_memory_size / total_bursts if total_bursts > 0 else 0.0

    # Memory growth
    if memory_retained and len(memory_sizes) > 1:
        nonzero_idx = [i for i, m in enumerate(memory_sizes) if m > 0]
        if len(nonzero_idx) > 1:
            growth_rate = np.polyfit(nonzero_idx, [memory_sizes[i] for i in nonzero_idx], 1)[0]
        else:
            growth_rate = 0.0
    else:
        growth_rate = 0.0

    print(f"  Memory Metrics:")
    print(f"    Final memory: {final_memory_size} patterns")
    print(f"    Memory retained: {'YES ✓' if memory_retained else 'NO ✗'}")
    if first_memory_cycle:
        print(f"    First memory: cycle {first_memory_cycle}")
        print(f"    Growth rate: {growth_rate:.2f} patterns/checkpoint")
    print(f"  Burst Metrics:")
    print(f"    Total bursts: {total_bursts}")
    print(f"    Burst rate: {burst_rate:.4f}")
    print(f"    Memory efficiency: {memory_efficiency:.2f} patterns/burst")
    print(f"  Seeding:")
    print(f"    Seed patterns per agent: {seed_count}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'seed_count': seed_count,
        'memory_retained': memory_retained,
        'final_memory_size': final_memory_size,
        'first_memory_cycle': first_memory_cycle,
        'growth_rate': growth_rate,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'memory_efficiency': memory_efficiency,
        'memory_sizes': memory_sizes,
        'burst_counts': burst_counts,
        'duration': duration
    }


def run_comparison_test(threshold: float, cycles: int = 500) -> dict:
    """
    Run test WITHOUT seeding for comparison.

    Args:
        threshold: Burst threshold
        cycles: Number of cycles

    Returns:
        dict with baseline results
    """
    print(f"\n{'='*80}")
    print(f"BASELINE TEST (NO SEEDING, threshold={threshold})")
    print(f"{'='*80}")

    # Create swarm (no seeding)
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    # Tracking
    memory_sizes = []
    checkpoint_interval = 10

    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        # Normal spawn (no seeding)
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        result = swarm.evolve_cycle(delta_time=1.0)
        burst_count = result.get('bursts', 0)
        total_bursts += burst_count

        if cycle % checkpoint_interval == 0:
            memory_sizes.append(len(swarm.global_memory))

    duration = time.time() - start_time

    final_memory_size = len(swarm.global_memory)
    memory_retained = final_memory_size > 0
    burst_rate = total_bursts / cycles if cycles > 0 else 0.0

    print(f"  Final memory: {final_memory_size} (baseline)")
    print(f"  Total bursts: {total_bursts}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'seed_count': 0,  # No seeding
        'memory_retained': memory_retained,
        'final_memory_size': final_memory_size,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'duration': duration
    }


def main():
    """Run memory seeding solution test."""
    print("="*80)
    print("CYCLE 72: MEMORY SEEDING SOLUTION")
    print("="*80)
    print()
    print("Testing architectural fix: Seed agents with initial memory patterns")
    print("Following Insight #35: Root cause = zero initial memory")
    print()

    # Test configuration
    test_threshold = 1400  # Moderate burst rate (0.086 from Cycle 71)
    cycles = 500

    print(f"Test Configuration:")
    print(f"  Threshold: {test_threshold} (moderate burst rate)")
    print(f"  Cycles: {cycles}")
    print(f"  Seed patterns: 5 per agent")
    print("="*80)

    overall_start = time.time()

    # Run baseline (no seeding)
    print("\n### BASELINE TEST (Cycle 71 replication) ###")
    baseline = run_comparison_test(test_threshold, cycles)
    time.sleep(0.5)

    # Run seeded test
    print("\n### SEEDED TEST (Memory Seeding Enabled) ###")
    seeded = run_seeded_test(test_threshold, cycles, seed_count=5)

    overall_duration = time.time() - overall_start

    # Analysis
    print(f"\n{'='*80}")
    print(f"MEMORY SEEDING EFFECTIVENESS ANALYSIS")
    print(f"{'='*80}\n")

    print("Comparison:")
    print(f"  Baseline (no seed):  {baseline['final_memory_size']} patterns, {baseline['total_bursts']} bursts")
    print(f"  Seeded (5 patterns): {seeded['final_memory_size']} patterns, {seeded['total_bursts']} bursts")
    print()

    if seeded['memory_retained'] and not baseline['memory_retained']:
        # SUCCESS
        print(f"🎉 BREAKTHROUGH: Memory Seeding WORKS!")
        print(f"   Memory enabled: 0 → {seeded['final_memory_size']} patterns")
        print(f"   First memory: cycle {seeded['first_memory_cycle']}")
        print(f"   Growth rate: {seeded['growth_rate']:.2f} patterns/checkpoint")
        print(f"   Efficiency: {seeded['memory_efficiency']:.2f} patterns/burst")
        print()
        print("Theoretical Significance:")
        print("  - Validates NRM memory mechanism (works with seeding)")
        print("  - Confirms Insight #35 root cause (zero initial memory)")
        print("  - Demonstrates architectural fix resolves constraint")
        print("  - Memory seeding enables composition-decomposition memory retention")
        print()
        insight_36 = True

    elif seeded['memory_retained'] and baseline['memory_retained']:
        # BOTH WORK (unexpected)
        print(f"⚠️ UNEXPECTED: Both baseline and seeded have memory")
        print(f"   Baseline: {baseline['final_memory_size']} patterns")
        print(f"   Seeded: {seeded['final_memory_size']} patterns")
        print(f"   Seeding improvement: {seeded['final_memory_size'] - baseline['final_memory_size']}")
        print()
        insight_36 = True

    elif not seeded['memory_retained'] and not baseline['memory_retained']:
        # BOTH FAIL
        print(f"❌ Memory Seeding INSUFFICIENT")
        print(f"   Both tests produced 0 memory")
        print()
        print("Implications:")
        print("  - Seeding alone doesn't resolve constraint")
        print("  - Deeper architectural issues exist")
        print("  - May require alternative mechanisms:")
        print("    - Memory accumulation during evolution (not just bursts)")
        print("    - Different burst-memory coupling")
        print("    - Agent survival mechanisms")
        print()
        insight_36 = False

    else:
        # SEEDED FAILS, BASELINE WORKS (very unexpected)
        print(f"⚠️ ANOMALY: Baseline works but seeded doesn't")
        print(f"   Investigate seeding implementation")
        insight_36 = False

    print("="*80)

    # Save results
    results_dir = Path(__file__).parent / "results" / "memory_seeding"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle72_memory_seeding_solution.json"

    output_data = {
        'experiment': 'cycle72_memory_seeding_solution',
        'threshold': test_threshold,
        'cycles': cycles,
        'baseline': baseline,
        'seeded': seeded,
        'seeding_effective': seeded['memory_retained'] and not baseline['memory_retained'],
        'insight_36_discovered': insight_36,
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
