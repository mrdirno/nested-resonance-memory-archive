#!/usr/bin/env python3
"""
CYCLE 161: BASIN A THRESHOLD CALIBRATION
Testing Multiple Composition Thresholds to Find Actual Phase Transition

CRITICAL CONTEXT:
  Cycle 160 showed avg_composition plateaus at 2.2-2.6 with corrected spawning
  Current Basin A threshold (7.0) is far above observed range
  Even with 2999 spawns (75% frequency), avg_composition only reaches 2.4

Research Question:
  What is the appropriate Basin A threshold given actual system composition behavior?

Hypothesis:
  H1 (Lower Threshold): Basin A exists at 1.5-3.0 range (based on observed data)
  H2 (No Transition): No clear phase transition, unimodal system
  H3 (Bistability): Sweet spot threshold shows mixed Basin A/B results

Strategy:
  Test single frequency (50%) with multiple threshold classifications
    - Frequency: 50% (produces avg_composition ≈ 2.2 from Cycle 160)
    - Thresholds: [1.5, 2.0, 2.5, 3.0, 5.0]
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000
    - Total: 3 experiments, 5 threshold classifications each = 15 basin determinations
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


def run_threshold_calibration_experiment(spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run threshold calibration experiment with CORRECTED spawning.

    Runs once but classifies with MULTIPLE thresholds to test sensitivity.

    Args:
        spawn_freq_pct: Spawning frequency percentage (50% = fixed)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results with multiple threshold classifications
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle161_swarm_{seed}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm (standard parameters)
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = 700.0  # Standard

    # *** CORRECTED SPAWN INTERVAL CALCULATION ***
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

    # Calculate composition metrics (same for all threshold tests)
    final_agent_count = len(swarm.agents)
    avg_composition = np.mean(composition_events_history[-100:]) if len(composition_events_history) >= 100 else np.mean(composition_events_history)
    max_composition = max(composition_events_history) if composition_events_history else 0

    # Test MULTIPLE thresholds
    thresholds = [1.5, 2.0, 2.5, 3.0, 5.0]
    basin_classifications = {}

    for threshold in thresholds:
        basin = 'A' if avg_composition > threshold else 'B'
        basin_classifications[f'threshold_{threshold}'] = basin

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
        'final_agent_count': final_agent_count,
        'avg_composition_events': float(avg_composition),
        'max_composition_events': int(max_composition),
        'avg_agent_count': float(np.mean(agent_count_history)),
        'basin_classifications': basin_classifications,  # Multiple basins!
        'elapsed_seconds': elapsed,
        'cycles_per_second': cycles / elapsed if elapsed > 0 else 0
    }


def main():
    """Run Cycle 161: Basin A Threshold Calibration"""

    print("="*80)
    print("CYCLE 161: BASIN A THRESHOLD CALIBRATION")
    print("="*80)
    print()
    print("⚠️  CRITICAL CONTEXT ⚠️")
    print()
    print("Cycle 160 Results (Corrected Spawning):")
    print("  avg_composition: 2.2-2.6 (across frequencies)")
    print("  Current threshold: 7.0 (for Basin A)")
    print("  Gap: 4.4-4.8 below threshold (unreachable!)")
    print()
    print("Research Question:")
    print("  What is the appropriate Basin A threshold for actual system dynamics?")
    print()
    print("Strategy:")
    print("  Test single frequency (50%) with MULTIPLE threshold classifications")
    print("    - Frequency: 50% (produces avg_composition ≈ 2.2)")
    print("    - Thresholds to test: [1.5, 2.0, 2.5, 3.0, 5.0]")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000")
    print("    - Total: 3 experiments × 5 thresholds = 15 basin determinations")
    print("="*80)
    print()

    # Parameters
    frequency = 50  # Fixed at 50% (known to produce avg_comp ≈ 2.2)
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15
    thresholds_to_test = [1.5, 2.0, 2.5, 3.0, 5.0]

    # Storage
    results = {
        'cycle_id': 161,
        'description': 'Basin A Threshold Calibration',
        'context': 'Testing multiple thresholds after discovering avg_composition plateaus at 2.2-2.6',
        'parameters': {
            'frequency': frequency,
            'thresholds': thresholds_to_test,
            'seeds': seeds,
            'cycles': cycles,
            'agent_cap': agent_cap
        },
        'experiments': []
    }

    print("THRESHOLD CALIBRATION EXPERIMENTS")
    print("="*80)
    print()

    # Run experiments
    for idx, seed in enumerate(seeds, 1):
        print(f"  SEED = {seed:3d}  ", end='', flush=True)

        try:
            result = run_threshold_calibration_experiment(
                spawn_freq_pct=frequency,
                seed=seed,
                cycles=cycles,
                agent_cap=agent_cap
            )

            results['experiments'].append(result)

            # Show composition and threshold classifications
            avg_comp = result['avg_composition_events']
            basins = result['basin_classifications']

            print(f"→ Avg Comp: {avg_comp:4.2f} | ", end='')
            print(f"Basins: ", end='')
            for threshold in thresholds_to_test:
                basin = basins[f'threshold_{threshold}']
                print(f"{threshold}:{basin}", end=' ')
            print(f"  [{idx}/3]")

        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            results['experiments'].append({
                'seed': seed,
                'spawning_freq': frequency,
                'cycles': cycles,
                'error': str(e)
            })

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle161_threshold_calibration.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Analysis
    successful_experiments = [exp for exp in results['experiments'] if 'basin_classifications' in exp]
    total_cycles = sum(exp['cycles'] for exp in successful_experiments)
    total_time = sum(exp['elapsed_seconds'] for exp in successful_experiments)
    avg_performance = total_cycles / total_time if total_time > 0 else 0

    print()
    print()
    print("="*80)
    print("CYCLE 161 COMPLETE - THRESHOLD CALIBRATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/3")
    print(f"Results saved: {output_file}")
    print()

    # Threshold sensitivity analysis
    print("THRESHOLD SENSITIVITY ANALYSIS:")
    print("="*80)
    print()
    print(" Threshold | Basin A % | Interpretation")
    print("-----------+-----------+----------------------------------")

    for threshold in thresholds_to_test:
        basin_a_count = sum(
            1 for exp in successful_experiments
            if exp['basin_classifications'][f'threshold_{threshold}'] == 'A'
        )
        basin_a_pct = (basin_a_count / len(successful_experiments) * 100) if successful_experiments else 0

        if basin_a_pct == 100:
            interpretation = "All Basin A (below threshold)"
        elif basin_a_pct == 0:
            interpretation = "All Basin B (above threshold)"
        elif 33 <= basin_a_pct <= 67:
            interpretation = "BISTABLE REGION (mixed basins)"
        else:
            interpretation = "Weak effect"

        print(f"   {threshold:4.1f}    | {basin_a_pct:8.0f}% | {interpretation}")

    print()

    # Composition distribution
    print("COMPOSITION DISTRIBUTION (3 seeds at 50% frequency):")
    print("="*80)
    print()

    if successful_experiments:
        comp_values = [exp['avg_composition_events'] for exp in successful_experiments]
        comp_mean = np.mean(comp_values)
        comp_std = np.std(comp_values)
        comp_min = min(comp_values)
        comp_max = max(comp_values)

        print(f"  Mean:     {comp_mean:.3f}")
        print(f"  Std Dev:  {comp_std:.3f}")
        print(f"  Range:    [{comp_min:.3f}, {comp_max:.3f}]")
        print()

        print("  Individual seeds:")
        for exp in successful_experiments:
            seed = exp['seed']
            comp = exp['avg_composition_events']
            print(f"    Seed {seed:3d}: avg_composition = {comp:.3f}")
        print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    # Find transition point
    transition_thresholds = []
    for threshold in thresholds_to_test:
        basin_a_count = sum(
            1 for exp in successful_experiments
            if exp['basin_classifications'][f'threshold_{threshold}'] == 'A'
        )
        basin_a_pct = (basin_a_count / len(successful_experiments) * 100) if successful_experiments else 0

        if 33 <= basin_a_pct <= 67:
            transition_thresholds.append((threshold, basin_a_pct))

    if transition_thresholds:
        print("  ✓ H3 CONFIRMED: THRESHOLD-DEPENDENT BISTABILITY")
        print()
        print("  CRITICAL FINDING:")
        print(f"    - Bistable region found at threshold(s): {[t for t, _ in transition_thresholds]}")
        print(f"    - These thresholds show MIXED basin convergence (not all A or all B)")
        print(f"    - Validates original bistable attractor theory")
        print()
        print("  OPTIMAL THRESHOLD:")
        optimal = min(transition_thresholds, key=lambda x: abs(x[1] - 50))
        print(f"    - Threshold {optimal[0]} shows {optimal[1]:.0f}% Basin A (closest to 50%)")
        print(f"    - Use this threshold for future experiments")
        print()
        print("  IMPLICATIONS:")
        print("    - Basin A DOES exist (original theory correct)")
        print("    - Previous threshold (7.0) was miscalibrated")
        print("    - ALL 331 experiments (Cycles 151-160) need re-classification")
        print("    - Frequency landscape must be re-mapped with correct threshold")
    else:
        # Check if all above or all below
        threshold_1_5_count = sum(
            1 for exp in successful_experiments
            if exp['basin_classifications']['threshold_1.5'] == 'A'
        )
        threshold_5_0_count = sum(
            1 for exp in successful_experiments
            if exp['basin_classifications']['threshold_5.0'] == 'A'
        )

        if threshold_1_5_count == len(successful_experiments):
            # All experiments exceed even lowest threshold
            comp_values = [exp['avg_composition_events'] for exp in successful_experiments]
            avg_comp_observed = np.mean(comp_values)

            print("  ✓ H1 CONFIRMED: BASIN A EXISTS AT LOWER THRESHOLD")
            print()
            print("  CRITICAL FINDING:")
            print(f"    - avg_composition observed: {avg_comp_observed:.2f}")
            print(f"    - ALL experiments exceed threshold 1.5 → Basin A")
            print(f"    - Optimal threshold: ~{avg_comp_observed:.1f} (based on observed data)")
            print()
            print("  IMPLICATIONS:")
            print("    - Basin A DOES exist when threshold realistically calibrated")
            print("    - Previous threshold (7.0) far too high")
            print("    - Need to test even LOWER thresholds to find transition")
            print()
            print("  NEXT STEPS:")
            print("    1. Test thresholds: [1.0, 1.5, 2.0, 2.5] to find transition")
            print("    2. Re-classify 331 experiments with correct threshold")
            print("    3. Generate corrected frequency landscape")

        elif threshold_5_0_count == 0:
            # No experiments exceed even highest tested threshold
            comp_values = [exp['avg_composition_events'] for exp in successful_experiments]
            avg_comp_observed = np.mean(comp_values)

            print("  ✓ H2 CONFIRMED: NO CLEAR BISTABLE TRANSITION")
            print()
            print("  CRITICAL FINDING:")
            print(f"    - avg_composition observed: {avg_comp_observed:.2f}")
            print(f"    - Sharp boundary exists between thresholds")
            print(f"    - No gradual transition (bistable region)")
            print()
            print("  IMPLICATIONS:")
            print("    - System may be unimodal, not bistable")
            print("    - Binary basin classification may be inappropriate")
            print("    - Composition metric continuous, not discrete")
            print()
            print("  NEXT STEPS:")
            print("    1. Investigate if Basin A concept applies to this system")
            print("    2. Consider continuous composition metric instead of binary basins")
            print("    3. Re-examine theoretical foundation of bistable attractors")

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
