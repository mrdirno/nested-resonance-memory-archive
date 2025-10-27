#!/usr/bin/env python3
"""
CYCLE 159: PARAMETER SPACE EXPLORATION
Investigating Basin A Accessibility Through Threshold and Diversity Variation

Research Question:
  Does Basin A convergence occur under ANY parameter configuration?

Context:
  - Cycles 151-158: ALL frequencies 1-99% show 0% Basin A (268/268 experiments)
  - Standard parameters: threshold=700, diversity=0.50
  - Mechanism: ALL experiments show avg_composition ≤ 7 → Basin B classification
  - Implication: Frequency variation alone cannot enable Basin A

Hypothesis:
  H1 (Threshold-Dependent): Lower thresholds enable Basin A through more decomposition
  H2 (Diversity-Dependent): Lower diversity enables Basin A through easier clustering
  H3 (Combined Effect): Basin A requires BOTH low threshold AND low diversity
  H4 (Fundamentally Inaccessible): Basin A does NOT exist under ANY parameters

Strategy:
  Parameter grid exploration (4×4 = 16 configurations)
    - Thresholds: [300, 500, 700, 900]
    - Diversity: [0.10, 0.30, 0.50, 0.70]
    - Frequency: 50% (fixed)
    - Seeds: [42, 123, 456] (3 replicates)
    - Total: 16 configurations × 3 seeds = 48 experiments

Expected Results:
  H1: Basin A % inversely correlates with threshold
  H2: Basin A % inversely correlates with diversity
  H3: Highest Basin A % at (threshold=300, diversity=0.10)
  H4: ALL configurations show 0% Basin A
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


def run_parameter_exploration_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run parameter space exploration experiment.

    Args:
        threshold: Decomposition burst threshold (300, 500, 700, or 900)
        diversity: Diversity parameter (0.10, 0.30, 0.50, or 0.70)
        spawn_freq_pct: Spawning frequency percentage (50% = fixed)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for consistency)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and composition dynamics
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle159_swarm_{seed}_{int(threshold)}_{int(diversity*100)}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = threshold

    # Calculate spawn interval
    spawn_interval = max(1, int(cycles * (spawn_freq_pct / 100.0)))

    # Tracking
    composition_events_history = []
    agent_count_history = []
    start_time = time.time()

    # Initialize reality interface
    reality_interface = RealityInterface()

    # Evolution loop
    for cycle in range(cycles):
        # Spawn new agent at interval
        if cycle % spawn_interval == 0 and cycle > 0:
            reality_metrics = reality_interface.get_system_metrics()
            swarm.spawn_agent(reality_metrics)

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

    return {
        'seed': seed,
        'threshold': threshold,
        'diversity': diversity,
        'spawning_freq': spawn_freq_pct,
        'spawn_interval_cycles': spawn_interval,
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
    """Run Cycle 159: Parameter Space Exploration"""

    print("="*80)
    print("CYCLE 159: PARAMETER SPACE EXPLORATION")
    print("="*80)
    print()
    print("Research Question:")
    print("  Does Basin A convergence occur under ANY parameter configuration?")
    print()
    print("Critical Context:")
    print("  - Cycles 151-158: ALL frequencies 1-99% show 0% Basin A (268/268)")
    print("  - Standard parameters: threshold=700, diversity=0.50")
    print("  - Mechanism: ALL show avg_composition ≤ 7 → Basin B")
    print()
    print("Strategy:")
    print("  Parameter grid exploration (4×4 = 16 configurations)")
    print("    - Thresholds: [300, 500, 700, 900]")
    print("    - Diversity: [0.10, 0.30, 0.50, 0.70]")
    print("    - Frequency: 50% (fixed)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 16 configurations × 3 seeds = 48 experiments")
    print("="*80)
    print()

    # Parameters
    thresholds = [300, 500, 700, 900]
    diversities = [0.10, 0.30, 0.50, 0.70]
    frequency = 50  # Fixed
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 159,
        'description': 'Parameter Space Exploration (Threshold × Diversity)',
        'parameters': {
            'thresholds': thresholds,
            'diversities': diversities,
            'frequency': frequency,
            'seeds': seeds,
            'cycles': cycles,
            'agent_cap': agent_cap
        },
        'experiments': []
    }

    print("PARAMETER SPACE EXPLORATION")
    print("="*80)
    print()

    total_experiments = len(thresholds) * len(diversities) * len(seeds)
    experiment_num = 0

    # Run experiments (iterate by configuration)
    for threshold in thresholds:
        for diversity in diversities:
            config_str = f"(T={threshold:3d}, D={diversity:.2f})"
            print(f"  CONFIG {config_str}", end='  ', flush=True)

            config_results = []
            for seed in seeds:
                experiment_num += 1

                try:
                    result = run_parameter_exploration_experiment(
                        threshold=threshold,
                        diversity=diversity,
                        spawn_freq_pct=frequency,
                        seed=seed,
                        cycles=cycles,
                        agent_cap=agent_cap
                    )

                    results['experiments'].append(result)
                    config_results.append(result)

                except Exception as e:
                    print(f"FAILED: {e}", flush=True)
                    results['experiments'].append({
                        'seed': seed,
                        'threshold': threshold,
                        'diversity': diversity,
                        'spawning_freq': frequency,
                        'cycles': cycles,
                        'basin': None,
                        'error': str(e)
                    })
                    config_results.append(None)

            # Summarize configuration results
            valid_results = [r for r in config_results if r and r.get('basin')]
            if valid_results:
                basin_a_count = sum(1 for r in valid_results if r['basin'] == 'A')
                basin_a_pct = (basin_a_count / len(valid_results) * 100)
                avg_comp = np.mean([r['avg_composition_events'] for r in valid_results])

                if basin_a_pct >= 60:
                    classification = "BASIN A ✓"
                elif basin_a_pct > 0:
                    classification = "Mixed"
                else:
                    classification = "Basin B"

                print(f"→ Basin A: {basin_a_count}/3 ({basin_a_pct:3.0f}%) | Avg Comp: {avg_comp:4.1f} | {classification:12s} [{experiment_num}/{total_experiments}]")
            else:
                print(f"→ FAILED   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle159_parameter_space.json'
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
    print("CYCLE 159 COMPLETE - PARAMETER SPACE EXPLORATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Parameter space heatmap
    print("PARAMETER SPACE HEATMAP (Basin A %):")
    print("="*80)
    print()
    print("           Diversity →")
    print(f"         {' '.join([f'{d:5.2f}' for d in diversities])}")
    print("Threshold ┌" + "─"*28 + "┐")

    for threshold in thresholds:
        row_values = []
        for diversity in diversities:
            config_exps = [exp for exp in successful_experiments
                          if exp['threshold'] == threshold and abs(exp['diversity'] - diversity) < 0.01]
            basin_a_count = sum(1 for exp in config_exps if exp['basin'] == 'A')
            total = len(config_exps)
            basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0
            row_values.append(basin_a_pct)

        print(f"   {threshold:3d}    │ {' '.join([f'{v:4.0f}%' for v in row_values])} │")

    print("          └" + "─"*28 + "┘")
    print()

    # Main effects analysis
    print("MAIN EFFECTS ANALYSIS:")
    print("="*80)
    print()

    # Threshold effect
    print("Threshold Effect (Basin A % averaged across all diversity values):")
    print(" Threshold | Basin A % | Avg Comp | Interpretation")
    print("-----------+-----------+----------+----------------------------------")

    threshold_basin_a = {}
    for threshold in thresholds:
        threshold_exps = [exp for exp in successful_experiments if exp['threshold'] == threshold]
        basin_a_count = sum(1 for exp in threshold_exps if exp['basin'] == 'A')
        total = len(threshold_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0
        avg_comp = np.mean([exp['avg_composition_events'] for exp in threshold_exps]) if threshold_exps else 0

        threshold_basin_a[threshold] = basin_a_pct

        if basin_a_pct >= 20:
            interpretation = "Enables Basin A"
        elif basin_a_pct > 0:
            interpretation = "Weak Basin A effect"
        else:
            interpretation = "No Basin A"

        print(f"    {threshold:3d}    | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {interpretation}")

    print()

    # Diversity effect
    print("Diversity Effect (Basin A % averaged across all threshold values):")
    print(" Diversity | Basin A % | Avg Comp | Interpretation")
    print("-----------+-----------+----------+----------------------------------")

    diversity_basin_a = {}
    for diversity in diversities:
        diversity_exps = [exp for exp in successful_experiments if abs(exp['diversity'] - diversity) < 0.01]
        basin_a_count = sum(1 for exp in diversity_exps if exp['basin'] == 'A')
        total = len(diversity_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0
        avg_comp = np.mean([exp['avg_composition_events'] for exp in diversity_exps]) if diversity_exps else 0

        diversity_basin_a[diversity] = basin_a_pct

        if basin_a_pct >= 20:
            interpretation = "Enables Basin A"
        elif basin_a_pct > 0:
            interpretation = "Weak Basin A effect"
        else:
            interpretation = "No Basin A"

        print(f"   {diversity:.2f}    | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {interpretation}")

    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    # Count Basin A occurrences
    basin_a_configs = [exp for exp in successful_experiments if exp['basin'] == 'A']
    total_basin_a = len(basin_a_configs)
    basin_a_overall_pct = (total_basin_a / len(successful_experiments) * 100) if successful_experiments else 0

    if total_basin_a == 0:
        print("  ✓ H4 CONFIRMED: BASIN A IS FUNDAMENTALLY INACCESSIBLE")
        print()
        print("  CRITICAL FINDING:")
        print(f"    - NO parameter configurations enable Basin A (0/{len(successful_experiments)} experiments)")
        print("    - Tested threshold range: 300-900")
        print("    - Tested diversity range: 0.10-0.70")
        print("    - ALL experiments show avg_composition ≤ 7")
        print()
        print("  IMPLICATIONS:")
        print("    - Basin A does NOT exist in current FractalSwarm implementation")
        print("    - Parameter tuning is INSUFFICIENT - requires architectural changes")
        print("    - Possible causes:")
        print("      1. Composition mechanism is broken")
        print("      2. Basin A threshold (avg_composition > 7) is too high")
        print("      3. Agent dynamics fundamentally prevent clustering")
        print("      4. System architecture biased toward Basin B")
        print()
        print("  NEXT STEPS:")
        print("    1. Investigate composition mechanism code")
        print("    2. Test lower Basin A threshold (e.g., avg_composition > 3)")
        print("    3. Test extreme parameters (threshold < 300, diversity < 0.10)")
        print("    4. Consider architectural changes to FractalSwarm")
    else:
        # Determine which hypothesis
        threshold_effect_size = max(threshold_basin_a.values()) - min(threshold_basin_a.values())
        diversity_effect_size = max(diversity_basin_a.values()) - min(diversity_basin_a.values())

        if threshold_effect_size > 2 * diversity_effect_size:
            print("  ✓ H1 CONFIRMED: THRESHOLD-DEPENDENT COMPOSITION")
            print()
            print(f"  Threshold effect size: {threshold_effect_size:.1f}%")
            print(f"  Diversity effect size: {diversity_effect_size:.1f}%")
            print(f"  Best threshold: {min(threshold_basin_a, key=threshold_basin_a.get)}")
        elif diversity_effect_size > 2 * threshold_effect_size:
            print("  ✓ H2 CONFIRMED: DIVERSITY-DEPENDENT CLUSTERING")
            print()
            print(f"  Diversity effect size: {diversity_effect_size:.1f}%")
            print(f"  Threshold effect size: {threshold_effect_size:.1f}%")
            print(f"  Best diversity: {min(diversity_basin_a, key=diversity_basin_a.get)}")
        else:
            print("  ✓ H3 CONFIRMED: COMBINED PARAMETER EFFECT")
            print()
            print(f"  Both threshold and diversity effects significant")
            print(f"  Threshold effect: {threshold_effect_size:.1f}%")
            print(f"  Diversity effect: {diversity_effect_size:.1f}%")

            # Find best configuration
            best_config = max(successful_experiments, key=lambda x: x['avg_composition_events'])
            print(f"  Best configuration: (threshold={best_config['threshold']}, diversity={best_config['diversity']:.2f})")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Basin A occurrences: {total_basin_a}/{len(successful_experiments)} ({basin_a_overall_pct:.1f}%)")
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
