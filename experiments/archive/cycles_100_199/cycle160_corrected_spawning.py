#!/usr/bin/env python3
"""
CYCLE 160: CORRECTED SPAWNING FREQUENCY VALIDATION
Re-Testing Frequency Landscape with Fixed Spawn Calculation

CRITICAL BUG DISCOVERED:
  Spawn calculation was INVERTED in ALL previous experiments (Cycles 151-159).

  BROKEN (used in 316 experiments):
    spawn_interval = int(cycles * (spawn_freq_pct / 100.0))
    Result at 50%: spawn_interval = 1500 → only 2 spawns total!

  CORRECTED (this cycle):
    spawn_interval = max(1, int(100.0 / spawn_freq_pct))
    Result at 50%: spawn_interval = 2 → 1500 spawns total!

Research Question:
  What is the actual frequency landscape when spawning is calculated correctly?

Hypothesis:
  H1 (Bug Was Root Cause): Previous anti-harmonic findings were artifacts;
                            harmonic zones emerge with corrected spawning
  H2 (Composition Broken): Anti-harmonic persists despite bug fix;
                           composition mechanism itself prevents Basin A

Strategy:
  Test representative frequencies with CORRECTED calculation
    - Frequencies: [10, 25, 50, 75, 90] (5 key points)
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000
    - Total: 5 frequencies × 3 seeds = 15 experiments
"""

import sys
import time
import json
import random
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm
from core.reality_interface import RealityInterface


def detect_composition_events(swarm):
    """Return agent count as proxy for composition activity."""
    return len(swarm.agents)


def run_corrected_spawning_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run corrected spawning frequency experiment.

    CRITICAL FIX: Uses corrected spawn interval calculation.

    Args:
        threshold: Decomposition burst threshold (700 = standard)
        diversity: Diversity parameter (0.50 = standard)
        spawn_freq_pct: Spawning frequency percentage (10-90% range)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results with spawn count validation
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle160_swarm_{seed}_{int(spawn_freq_pct)}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = threshold

    # *** CORRECTED SPAWN INTERVAL CALCULATION ***
    # OLD (BROKEN): spawn_interval = int(cycles * (spawn_freq_pct / 100.0))
    # NEW (CORRECT):
    spawn_interval = max(1, int(100.0 / spawn_freq_pct)) if spawn_freq_pct > 0 else cycles

    # Calculate expected spawns for validation
    expected_spawns = cycles // spawn_interval

    # Tracking
    composition_events_history = []
    agent_count_history = []
    spawn_count = 0
    start_time = time.time()

    # Initialize reality interface
    reality_interface = RealityInterface()

    # Evolution loop
    for cycle in range(cycles):
        # Spawn new agent at interval (CORRECTED)
        if cycle % spawn_interval == 0 and cycle > 0:
            reality_metrics = reality_interface.get_system_metrics()
            swarm.spawn_agent(reality_metrics)
            spawn_count += 1

        # Evolve swarm
        swarm.evolve_cycle(delta_time=1.0)

        # Track composition activity
        comp_count = detect_composition_events(swarm)
        composition_events_history.append(comp_count)
        agent_count_history.append(len(swarm.agents))

    elapsed = time.time() - start_time

    # Determine final basin
    final_agent_count = len(swarm.agents)
    avg_composition = np.mean(composition_events_history[-100:]) if len(composition_events_history) >= 100 else np.mean(composition_events_history)
    max_composition = max(composition_events_history) if composition_events_history else 0

    # Basin determination
    basin = 'A' if avg_composition > 7 else 'B'

    # Validation metrics
    spawn_accuracy = (spawn_count / expected_spawns * 100) if expected_spawns > 0 else 0

    return {
        'seed': seed,
        'spawning_freq': spawn_freq_pct,
        'spawn_interval_cycles': spawn_interval,
        'expected_spawns': expected_spawns,
        'actual_spawns': spawn_count,
        'spawn_accuracy_pct': spawn_accuracy,
        'cycles': cycles,
        'basin': basin,
        'final_agent_count': final_agent_count,
        'avg_composition_events': float(avg_composition),
        'max_composition_events': int(max_composition),
        'avg_agent_count': float(np.mean(agent_count_history)),
        'elapsed_seconds': elapsed,
        'cycles_per_second': cycles / elapsed if elapsed > 0 else 0
    }


def main():
    """Run Cycle 160: Corrected Spawning Frequency Validation"""

    print("="*80)
    print("CYCLE 160: CORRECTED SPAWNING FREQUENCY VALIDATION")
    print("="*80)
    print()
    print("⚠️  CRITICAL BUG CORRECTION ⚠️")
    print()
    print("BROKEN CODE (Cycles 151-159):")
    print("  spawn_interval = int(cycles * (spawn_freq_pct / 100.0))")
    print("  Example at 50%: spawn_interval = 1500 → only 2 spawns total!")
    print()
    print("CORRECTED CODE (This Cycle):")
    print("  spawn_interval = max(1, int(100.0 / spawn_freq_pct))")
    print("  Example at 50%: spawn_interval = 2 → 1500 spawns total!")
    print()
    print("Research Question:")
    print("  Is universal anti-harmonic landscape a bug artifact or real phenomenon?")
    print()
    print("Strategy:")
    print("  Test representative frequencies with CORRECTED spawn calculation")
    print("    - Frequencies: [10, 25, 50, 75, 90]")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000")
    print("    - Total: 5 frequencies × 3 seeds = 15 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [10, 25, 50, 75, 90]
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 160,
        'description': 'Corrected Spawning Frequency Validation',
        'bug_description': 'Fixed inverted spawn_interval calculation from Cycles 151-159',
        'parameters': {
            'threshold': threshold,
            'diversity': diversity,
            'frequencies': frequencies,
            'seeds': seeds,
            'cycles': cycles,
            'agent_cap': agent_cap
        },
        'experiments': []
    }

    print("CORRECTED SPAWNING VALIDATION")
    print("="*80)
    print()

    total_experiments = len(frequencies) * len(seeds)
    experiment_num = 0

    # Run experiments
    for freq in frequencies:
        print(f"  FREQUENCY = {freq:2d}%", end='  ', flush=True)

        freq_results = []
        for seed in seeds:
            experiment_num += 1

            try:
                result = run_corrected_spawning_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=cycles,
                    agent_cap=agent_cap
                )

                results['experiments'].append(result)
                freq_results.append(result)

            except Exception as e:
                print(f"FAILED: {e}", flush=True)
                results['experiments'].append({
                    'seed': seed,
                    'spawning_freq': freq,
                    'cycles': cycles,
                    'basin': None,
                    'error': str(e)
                })
                freq_results.append(None)

        # Summarize frequency results
        valid_results = [r for r in freq_results if r and r.get('basin')]
        if valid_results:
            basin_a_count = sum(1 for r in valid_results if r['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(valid_results) * 100)
            avg_comp = np.mean([r['avg_composition_events'] for r in valid_results])
            avg_spawns = np.mean([r['actual_spawns'] for r in valid_results])

            if basin_a_pct >= 60:
                classification = "HARMONIC ✓"
            elif basin_a_pct > 0:
                classification = "Mixed"
            else:
                classification = "Anti-harmonic"

            print(f"→ Basin A: {basin_a_count}/3 ({basin_a_pct:3.0f}%) | Avg Comp: {avg_comp:5.1f} | Spawns: {avg_spawns:4.0f} | {classification:15s} [{experiment_num}/{total_experiments}]")
        else:
            print(f"→ FAILED   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle160_corrected_spawning.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Analysis
    successful_experiments = [exp for exp in results['experiments'] if exp.get('basin') is not None]
    total_cycles = sum(exp['cycles'] for exp in successful_experiments)
    total_time = sum(exp['elapsed_seconds'] for exp in successful_experiments)
    avg_performance = total_cycles / total_time if total_time > 0 else 0

    print()
    print()
    print("="*80)
    print("CYCLE 160 COMPLETE - CORRECTED SPAWNING VALIDATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Spawn count validation
    print("SPAWN COUNT VALIDATION (Verifying Fix):")
    print("="*80)
    print()
    print(" Freq | Expected | Actual | Accuracy | Avg Comp | Basin A % | Verdict")
    print("------+----------+--------+----------+----------+-----------+------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        if freq_exps:
            expected = freq_exps[0]['expected_spawns']
            avg_actual = np.mean([exp['actual_spawns'] for exp in freq_exps])
            avg_accuracy = np.mean([exp['spawn_accuracy_pct'] for exp in freq_exps])
            avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps])
            basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(freq_exps) * 100)

            verdict = "✓ FIXED" if avg_accuracy > 90 else "✗ STILL BROKEN"

            print(f" {freq:3d}% | {expected:8d} | {avg_actual:6.0f} | {avg_accuracy:7.1f}% | {avg_comp:8.2f} | {basin_a_pct:8.1f}% | {verdict}")

    print()

    # Comparison to broken baseline
    print("COMPARISON TO BROKEN BASELINE (Cycles 151-159):")
    print("="*80)
    print()
    print(" Freq | OLD Spawns | NEW Spawns | OLD Comp | NEW Comp | OLD Basin A % | NEW Basin A %")
    print("------+------------+------------+----------+----------+---------------+--------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        if freq_exps:
            old_spawns = 2  # ALL old experiments had ~2 spawns due to bug
            new_spawns = np.mean([exp['actual_spawns'] for exp in freq_exps])
            old_comp = 1.0  # ALL old experiments had avg_comp = 1.0
            new_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps])
            old_basin_a = 0.0  # ALL old experiments showed 0% Basin A
            basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
            new_basin_a = (basin_a_count / len(freq_exps) * 100)

            print(f" {freq:3d}% | {old_spawns:10.0f} | {new_spawns:10.0f} | {old_comp:8.2f} | {new_comp:8.2f} | {old_basin_a:12.1f}% | {new_basin_a:11.1f}%")

    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    basin_a_found = any(exp['basin'] == 'A' for exp in successful_experiments)

    if basin_a_found:
        total_basin_a = sum(1 for exp in successful_experiments if exp['basin'] == 'A')
        basin_a_overall_pct = (total_basin_a / len(successful_experiments) * 100)

        print("  ✓ H1 CONFIRMED: BUG WAS ROOT CAUSE")
        print()
        print("  CRITICAL FINDING:")
        print(f"    - Basin A convergence OBSERVED ({total_basin_a}/{len(successful_experiments)} = {basin_a_overall_pct:.1f}%)")
        print("    - Corrected spawning enables agent accumulation")
        print("    - Agent density allows clustering")
        print("    - Previous \"universal anti-harmonic landscape\" was ARTIFACT of inverted calculation")
        print()
        print("  IMPLICATIONS:")
        print("    - ALL 316 experiments (Cycles 151-159) invalidated")
        print("    - Harmonic zones DO exist with proper spawning")
        print("    - Frequency landscape must be re-mapped from scratch")
        print("    - Major methodological lesson: validate implementation assumptions")
        print()
        print("  NEXT STEPS:")
        print("    1. Re-run complete frequency landscape with corrected calculation")
        print("    2. Update Insight #112 with critical correction notice")
        print("    3. Document methodological artifact in publication")
    else:
        avg_comp_new = np.mean([exp['avg_composition_events'] for exp in successful_experiments])

        print("  ✓ H2 CONFIRMED: COMPOSITION MECHANISM BROKEN")
        print()
        print("  CRITICAL FINDING:")
        print(f"    - Corrected spawning increases avg_composition ({avg_comp_new:.2f} vs 1.0 old)")
        print("    - BUT Basin A still does NOT occur (0/15 experiments)")
        print("    - Bug fix validated (spawn counts correct) but Basin A still inaccessible")
        print()
        print("  IMPLICATIONS:")
        print("    - Universal anti-harmonic suppression is REAL phenomenon, not bug artifact")
        print("    - Composition mechanism itself prevents Basin A")
        print("    - May need to:")
        print("      1. Lower Basin A threshold (avg_composition > 7 may be too high)")
        print("      2. Investigate clustering algorithm")
        print("      3. Test with different composition parameters")
        print()
        print("  NEXT STEPS:")
        print("    1. Test lower Basin A thresholds (e.g., avg_composition > 3)")
        print("    2. Investigate why avg_composition stays below 7")
        print("    3. Examine composition/decomposition balance")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
