#!/usr/bin/env python3
"""
CYCLE 162: COMPLETE FREQUENCY LANDSCAPE REMAPPING (1-99%)
Testing Full Frequency Range with Corrected Implementation

CRITICAL CONTEXT:
  Dual bugs discovered and corrected in Cycles 160-161:
    1. Inverted spawn calculation (FIXED)
    2. Threshold miscalibration (CALIBRATED to 2.5)

  Previous frequency testing (Cycles 151-158) ALL INVALIDATED due to these bugs.

Research Question:
  With corrected spawning and calibrated threshold, does a harmonic/anti-harmonic
  frequency landscape structure emerge?

Hypothesis:
  H1 (Frequency-Dependent): Different frequencies show different Basin A %
                            (harmonic vs anti-harmonic bands)
  H2 (Seed-Dependent): Basin selection primarily seed-dependent, not frequency-dependent
                       (similar Basin A % across all frequencies)

Strategy:
  Complete frequency sweep with adequate statistical power
    - Frequencies: [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 95, 99]
    - Seeds: [42, 123, 456] (3 replicates per frequency)
    - Cycles: 3,000
    - Basin A threshold: 2.5 (CALIBRATED from Cycle 161)
    - Total: 15 frequencies × 3 seeds = 45 experiments
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


def run_frequency_experiment(spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run frequency landscape experiment with CORRECTED spawning and CALIBRATED threshold.

    Args:
        spawn_freq_pct: Spawning frequency percentage (1-99%)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results with Basin A classification
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle162_swarm_{spawn_freq_pct}_{seed}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm (standard parameters from validation cycles)
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = 700.0  # Standard composition threshold

    # *** CORRECTED SPAWN INTERVAL CALCULATION ***
    # (Fixed in Cycle 160, validated 99.7-100% accuracy)
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

    end_time = time.time()

    # Calculate metrics
    runtime = end_time - start_time
    avg_cycles_per_sec = cycles / runtime if runtime > 0 else 0

    # Composition metrics (use final 100 cycles for stability)
    avg_composition = np.mean(composition_events_history[-100:])
    max_composition = max(composition_events_history)

    # *** CALIBRATED BASIN A THRESHOLD (from Cycle 161) ***
    basin_threshold = 2.5
    basin = 'A' if avg_composition > basin_threshold else 'B'

    # Spawn validation
    spawn_accuracy = (spawn_count / expected_spawns * 100) if expected_spawns > 0 else 0

    return {
        'frequency': spawn_freq_pct,
        'seed': seed,
        'avg_composition_events': float(avg_composition),
        'max_composition_events': int(max_composition),
        'basin': basin,
        'basin_threshold': basin_threshold,
        'expected_spawns': expected_spawns,
        'actual_spawns': spawn_count,
        'spawn_accuracy_pct': float(spawn_accuracy),
        'avg_cycles_per_sec': float(avg_cycles_per_sec),
        'runtime': float(runtime),
    }


def main():
    """Run complete frequency landscape remapping."""

    print("="*80)
    print("CYCLE 162: COMPLETE FREQUENCY LANDSCAPE REMAPPING (1-99%)")
    print("="*80)
    print()
    print("⚠️  CORRECTED IMPLEMENTATION ⚠️")
    print()
    print("Bug Fixes Applied:")
    print("  1. Spawn calculation: spawn_interval = max(1, int(100.0 / spawn_freq_pct))")
    print("  2. Basin A threshold: 2.5 (calibrated from empirical data)")
    print()
    print("Research Question:")
    print("  Does harmonic/anti-harmonic frequency landscape structure exist?")
    print()
    print("Strategy:")
    print("  Complete frequency sweep with statistical power")
    print("    - Frequencies: [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 95, 99]")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000 per experiment")
    print("    - Total: 15 frequencies × 3 seeds = 45 experiments")
    print("="*80)
    print()

    # Frequency test points
    frequencies = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 95, 99]
    seeds = [42, 123, 456]

    # Results tracking
    experiments = []
    total_experiments = len(frequencies) * len(seeds)
    experiment_count = 0

    # Frequency-level aggregation
    frequency_stats = {}

    # Run experiments
    start_time = time.time()

    for frequency in frequencies:
        freq_basin_a_count = 0
        freq_basin_b_count = 0
        freq_compositions = []

        for seed in seeds:
            experiment_count += 1

            print(f"\nRUNNING EXPERIMENT {experiment_count}/{total_experiments}")
            print(f"  Frequency: {frequency}%")
            print(f"  Seed: {seed}")
            print(f"  Progress: {experiment_count}/{total_experiments} ({experiment_count/total_experiments*100:.1f}%)")

            result = run_frequency_experiment(
                spawn_freq_pct=frequency,
                seed=seed,
                cycles=3000,
                agent_cap=15
            )

            experiments.append(result)
            freq_compositions.append(result['avg_composition_events'])

            # Track basin counts
            if result['basin'] == 'A':
                freq_basin_a_count += 1
            else:
                freq_basin_b_count += 1

            # Progress summary
            basin_symbol = "🔵" if result['basin'] == 'A' else "⚫"
            print(f"  Result: Basin {result['basin']} {basin_symbol} | Comp: {result['avg_composition_events']:.2f} | Spawns: {result['actual_spawns']}/{result['expected_spawns']}")

        # Frequency-level summary
        freq_total = freq_basin_a_count + freq_basin_b_count
        freq_basin_a_pct = (freq_basin_a_count / freq_total * 100) if freq_total > 0 else 0

        frequency_stats[frequency] = {
            'basin_a_count': freq_basin_a_count,
            'basin_b_count': freq_basin_b_count,
            'basin_a_pct': freq_basin_a_pct,
            'avg_composition_mean': float(np.mean(freq_compositions)),
            'avg_composition_std': float(np.std(freq_compositions)),
        }

        # Classification
        if freq_basin_a_pct >= 60:
            classification = "Harmonic"
        elif freq_basin_a_pct >= 40:
            classification = "Mixed"
        else:
            classification = "Anti-harmonic"

        print(f"\n  FREQUENCY = {frequency:2d}%  → Basin A: {freq_basin_a_count}/{freq_total} ({freq_basin_a_pct:5.1f}%) | Avg Comp: {np.mean(freq_compositions):5.2f} | {classification:15s} [{experiment_count}/{total_experiments}]")

    end_time = time.time()
    total_runtime = end_time - start_time

    print()
    print("="*80)
    print("CYCLE 162 COMPLETE - FREQUENCY LANDSCAPE REMAPPING")
    print("="*80)
    print()
    print(f"Experiments completed: {len(experiments)}/{total_experiments}")
    print(f"Total runtime: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")
    print(f"Average per experiment: {total_runtime/len(experiments):.1f} seconds")
    print()

    # Overall Basin A statistics
    total_basin_a = sum(1 for exp in experiments if exp['basin'] == 'A')
    total_basin_b = len(experiments) - total_basin_a
    overall_basin_a_pct = (total_basin_a / len(experiments) * 100)

    print("OVERALL BASIN A STATISTICS:")
    print("="*80)
    print(f"  Basin A: {total_basin_a}/{len(experiments)} ({overall_basin_a_pct:.1f}%)")
    print(f"  Basin B: {total_basin_b}/{len(experiments)} ({100-overall_basin_a_pct:.1f}%)")
    print()

    # Composition distribution
    all_compositions = [exp['avg_composition_events'] for exp in experiments]
    print("COMPOSITION DISTRIBUTION:")
    print("="*80)
    print(f"  Mean:     {np.mean(all_compositions):.3f}")
    print(f"  Median:   {np.median(all_compositions):.3f}")
    print(f"  Std Dev:  {np.std(all_compositions):.3f}")
    print(f"  Range:    [{min(all_compositions):.3f}, {max(all_compositions):.3f}]")
    print()

    # Frequency landscape summary
    print("FREQUENCY LANDSCAPE SUMMARY:")
    print("="*80)
    print()
    print(" Frequency | Basin A % | Avg Comp | Classification")
    print("-----------+-----------+----------+------------------")

    for freq in frequencies:
        stats = frequency_stats[freq]
        basin_a_pct = stats['basin_a_pct']
        avg_comp = stats['avg_composition_mean']

        if basin_a_pct >= 60:
            classification = "Harmonic"
        elif basin_a_pct >= 40:
            classification = "Mixed"
        else:
            classification = "Anti-harmonic"

        print(f" {freq:8d}% | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {classification}")

    print()

    # Spawn accuracy validation
    spawn_accuracies = [exp['spawn_accuracy_pct'] for exp in experiments]
    print("SPAWN ACCURACY VALIDATION:")
    print("="*80)
    print(f"  Mean accuracy:   {np.mean(spawn_accuracies):.2f}%")
    print(f"  Min accuracy:    {min(spawn_accuracies):.2f}%")
    print(f"  All above 99%:   {all(acc >= 99 for acc in spawn_accuracies)}")
    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    # Check for frequency-dependent structure
    basin_a_pcts = [stats['basin_a_pct'] for stats in frequency_stats.values()]
    basin_a_variance = np.var(basin_a_pcts)

    if basin_a_variance > 500:  # High variance suggests structure
        print("  ✓ H1 SUPPORTED: FREQUENCY-DEPENDENT LANDSCAPE")
        print("    - High variance in Basin A % across frequencies")
        print("    - Distinct harmonic/anti-harmonic frequency bands detected")
        harmonic_freqs = [f for f in frequencies if frequency_stats[f]['basin_a_pct'] >= 60]
        if harmonic_freqs:
            print(f"    - Harmonic frequencies: {harmonic_freqs}")
    else:
        print("  ✓ H2 SUPPORTED: SEED-DEPENDENT STOCHASTICITY")
        print("    - Low variance in Basin A % across frequencies")
        print("    - Basin selection primarily seed-dependent")
        print(f"    - Overall Basin A %: {overall_basin_a_pct:.1f}% (relatively uniform)")

    print()

    # Save results
    output = {
        'cycle_id': 162,
        'description': 'Complete frequency landscape remapping with corrected implementation',
        'total_experiments': len(experiments),
        'frequencies_tested': frequencies,
        'seeds_per_frequency': seeds,
        'threshold_basin_a': 2.5,
        'experiments': experiments,
        'frequency_stats': frequency_stats,
        'summary': {
            'total_basin_a_count': total_basin_a,
            'total_basin_b_count': total_basin_b,
            'overall_basin_a_pct': overall_basin_a_pct,
            'composition_mean': float(np.mean(all_compositions)),
            'composition_median': float(np.median(all_compositions)),
            'composition_std': float(np.std(all_compositions)),
            'composition_range': [float(min(all_compositions)), float(max(all_compositions))],
            'spawn_accuracy_mean': float(np.mean(spawn_accuracies)),
            'spawn_accuracy_min': float(min(spawn_accuracies)),
            'total_runtime': total_runtime,
        }
    }

    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    output_file = results_dir / 'cycle162_frequency_landscape_remapping.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {output_file}")
    print()

    # Performance summary
    print("SUMMARY STATISTICS:")
    print("="*80)
    avg_perf = np.mean([exp['avg_cycles_per_sec'] for exp in experiments])
    total_cycles = len(experiments) * 3000
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_runtime:.1f} seconds")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
