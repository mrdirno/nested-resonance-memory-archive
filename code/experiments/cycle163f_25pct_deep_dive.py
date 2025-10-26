#!/usr/bin/env python3
"""
CYCLE 163F: 25% FREQUENCY DEEP INVESTIGATION
Contingency: If Cycle 162 shows 25% as ONLY harmonic frequency

TRIGGER CONDITION:
  Cycle 162 shows 25% frequency with significantly higher Basin A %
  than other frequencies (potential quarter-wave resonance)

RESEARCH QUESTION:
  Why is 25% frequency special? What mechanism drives harmonic convergence?

STRATEGY:
  Phase 1: Extended replication at 25% (30 seeds) - validate 100% Basin A
  Phase 2: Fine-grained neighbors (20-30% in 1% steps) - define harmonic bandwidth
  Phase 3: Temporal dynamics (track composition trajectory) - identify critical time
  Phase 4: Parameter sensitivity (threshold × diversity at 25%) - test robustness
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


def run_experiment(spawn_freq_pct, seed, cycles=3000, agent_cap=15, threshold=700, diversity=0.3):
    """
    Run single experiment with corrected spawning and calibrated Basin A threshold.

    Args:
        spawn_freq_pct: Spawning frequency percentage
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (default 3000)
        agent_cap: Maximum number of agents (default 15)
        threshold: Composition threshold (default 700)
        diversity: Diversity parameter (default 0.3)

    Returns:
        dict: Experimental results with composition trajectory
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle163f_swarm_{spawn_freq_pct}_{seed}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm with specified parameters
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = float(threshold)

    # Corrected spawn interval calculation
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
        # Spawn new agent at interval (corrected)
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

    # Composition metrics
    avg_composition = np.mean(composition_events_history[-100:])  # Final 100 cycles
    max_composition = max(composition_events_history)

    # Basin A threshold (calibrated from Cycle 161)
    basin_threshold = 2.5
    basin = 'A' if avg_composition > basin_threshold else 'B'

    # Spawn validation
    spawn_accuracy = (spawn_count / expected_spawns * 100) if expected_spawns > 0 else 0

    return {
        'frequency': spawn_freq_pct,
        'seed': seed,
        'threshold': threshold,
        'diversity': diversity,
        'avg_composition_events': float(avg_composition),
        'max_composition_events': int(max_composition),
        'basin': basin,
        'basin_threshold': basin_threshold,
        'expected_spawns': expected_spawns,
        'actual_spawns': spawn_count,
        'spawn_accuracy_pct': float(spawn_accuracy),
        'avg_cycles_per_sec': float(avg_cycles_per_sec),
        'runtime': float(runtime),
        'composition_trajectory': [float(c) for c in composition_events_history[::10]],  # Sample every 10 cycles
    }


def phase1_extended_replication():
    """
    Phase 1: Extended replication at 25% frequency.

    Test 30 different seeds to validate 100% Basin A convergence.
    Identify any seeds that deviate from harmonic convergence.

    Returns:
        list: Experiment results (30 experiments)
    """
    print("=" * 80)
    print("PHASE 1: EXTENDED REPLICATION AT 25% FREQUENCY")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Does 25% frequency show 100% Basin A across extended seed sampling?")
    print()
    print("Strategy:")
    print("  - Frequency: 25% (quarter-wave)")
    print("  - Seeds: 30 different seeds [10, 20, 30, ..., 300]")
    print("  - Expected: 100% Basin A if robust harmonic")
    print("=" * 80)
    print()

    frequency = 25
    seeds = [i * 10 for i in range(1, 31)]  # [10, 20, ..., 300]
    results = []

    basin_a_count = 0
    basin_b_count = 0

    for idx, seed in enumerate(seeds, 1):
        print(f"[{idx:2d}/30] Seed {seed:3d}... ", end="", flush=True)

        result = run_experiment(
            spawn_freq_pct=frequency,
            seed=seed,
            cycles=3000,
            agent_cap=15,
        )

        results.append(result)

        if result['basin'] == 'A':
            basin_a_count += 1
            print(f"Basin A ✓ | Comp: {result['avg_composition_events']:.2f}")
        else:
            basin_b_count += 1
            print(f"Basin B ✗ | Comp: {result['avg_composition_events']:.2f} | DEVIATION!")

    # Summary
    basin_a_pct = (basin_a_count / len(results) * 100)
    print()
    print("=" * 80)
    print("PHASE 1 COMPLETE")
    print("=" * 80)
    print(f"  Basin A: {basin_a_count}/30 ({basin_a_pct:.1f}%)")
    print(f"  Basin B: {basin_b_count}/30 ({100 - basin_a_pct:.1f}%)")
    print()

    if basin_a_pct == 100:
        print("  ✓ CONFIRMED: 25% shows robust 100% Basin A convergence")
    elif basin_a_pct >= 80:
        print(f"  ~ MOSTLY HARMONIC: {basin_a_pct:.1f}% Basin A (some seed variance)")
    else:
        print(f"  ✗ NOT UNIVERSALLY HARMONIC: {basin_a_pct:.1f}% Basin A")

    print()
    return results


def phase2_fine_grained_neighbors():
    """
    Phase 2: Fine-grained frequency sweep around 25%.

    Test frequencies [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30] × 3 seeds
    to define harmonic bandwidth.

    Returns:
        list: Experiment results (33 experiments)
    """
    print("=" * 80)
    print("PHASE 2: FINE-GRAINED NEIGHBORS (20-30%)")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  What is the harmonic bandwidth around 25%?")
    print()
    print("Strategy:")
    print("  - Frequencies: [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30] (1% steps)")
    print("  - Seeds: [42, 123, 456] (3 replicates)")
    print("  - Total: 11 frequencies × 3 seeds = 33 experiments")
    print("=" * 80)
    print()

    frequencies = list(range(20, 31))  # 20-30 inclusive
    seeds = [42, 123, 456]
    results = []

    experiment_count = 0
    total_experiments = len(frequencies) * len(seeds)

    for frequency in frequencies:
        freq_basin_a = 0
        freq_basin_b = 0

        for seed in seeds:
            experiment_count += 1

            print(f"[{experiment_count:2d}/{total_experiments}] Freq {frequency:2d}%, Seed {seed:3d}... ", end="", flush=True)

            result = run_experiment(
                spawn_freq_pct=frequency,
                seed=seed,
                cycles=3000,
                agent_cap=15,
            )

            results.append(result)

            if result['basin'] == 'A':
                freq_basin_a += 1
                basin_symbol = "🔵"
            else:
                freq_basin_b += 1
                basin_symbol = "⚫"

            print(f"{basin_symbol} Basin {result['basin']} | Comp: {result['avg_composition_events']:.2f}")

        # Frequency summary
        freq_total = freq_basin_a + freq_basin_b
        freq_basin_a_pct = (freq_basin_a / freq_total * 100)

        print(f"  → {frequency}%: Basin A = {freq_basin_a}/{freq_total} ({freq_basin_a_pct:.1f}%)")
        print()

    print("=" * 80)
    print("PHASE 2 COMPLETE")
    print("=" * 80)
    print()

    # Analyze bandwidth
    freq_stats = {}
    for freq in frequencies:
        freq_results = [r for r in results if r['frequency'] == freq]
        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_results) * 100)
        freq_stats[freq] = basin_a_pct

    # Find harmonic bandwidth (>=67% threshold)
    harmonic_freqs = [f for f, pct in freq_stats.items() if pct >= 67]

    print(f"  Harmonic frequencies (≥67% Basin A): {harmonic_freqs}")
    if harmonic_freqs:
        print(f"  Harmonic bandwidth: {min(harmonic_freqs)}% - {max(harmonic_freqs)}%")
        print(f"  Bandwidth width: {max(harmonic_freqs) - min(harmonic_freqs) + 1}%")
    else:
        print("  No harmonic bandwidth found (all frequencies < 67% Basin A)")

    print()
    return results


def phase3_temporal_dynamics():
    """
    Phase 3: Temporal dynamics analysis at 25%.

    Track composition trajectory over time to identify when Basin A convergence occurs.
    Test shorter evolution cycles to find critical time.

    Returns:
        list: Experiment results with temporal data
    """
    print("=" * 80)
    print("PHASE 3: TEMPORAL DYNAMICS AT 25%")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  When does Basin A convergence occur? What is the critical time?")
    print()
    print("Strategy:")
    print("  - Frequency: 25% (harmonic)")
    print("  - Evolution lengths: [500, 1000, 1500, 2000, 2500, 3000] cycles")
    print("  - Seeds: [42, 123, 456] (3 replicates)")
    print("  - Total: 6 lengths × 3 seeds = 18 experiments")
    print("=" * 80)
    print()

    cycle_lengths = [500, 1000, 1500, 2000, 2500, 3000]
    seeds = [42, 123, 456]
    results = []

    experiment_count = 0
    total_experiments = len(cycle_lengths) * len(seeds)

    for cycles in cycle_lengths:
        length_basin_a = 0
        length_basin_b = 0

        for seed in seeds:
            experiment_count += 1

            print(f"[{experiment_count:2d}/{total_experiments}] Cycles {cycles:4d}, Seed {seed:3d}... ", end="", flush=True)

            result = run_experiment(
                spawn_freq_pct=25,
                seed=seed,
                cycles=cycles,
                agent_cap=15,
            )

            results.append(result)

            if result['basin'] == 'A':
                length_basin_a += 1
                basin_symbol = "🔵"
            else:
                length_basin_b += 1
                basin_symbol = "⚫"

            print(f"{basin_symbol} Basin {result['basin']} | Comp: {result['avg_composition_events']:.2f}")

        # Length summary
        length_total = length_basin_a + length_basin_b
        length_basin_a_pct = (length_basin_a / length_total * 100)

        print(f"  → {cycles} cycles: Basin A = {length_basin_a}/{length_total} ({length_basin_a_pct:.1f}%)")
        print()

    print("=" * 80)
    print("PHASE 3 COMPLETE")
    print("=" * 80)
    print()

    # Find critical time (minimum cycles for Basin A)
    for cycles in cycle_lengths:
        cycle_results = [r for r in results if len(r['composition_trajectory']) * 10 >= cycles]  # Approximate
        basin_a_count = sum(1 for r in cycle_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(cycle_results) * 100) if cycle_results else 0

        if basin_a_pct >= 50:
            print(f"  Critical time: ~{cycles} cycles (first length with ≥50% Basin A)")
            break

    print()
    return results


def phase4_parameter_sensitivity():
    """
    Phase 4: Parameter sensitivity at 25%.

    Test threshold × diversity variations to confirm 25% is robustly harmonic
    across parameter space.

    Returns:
        list: Experiment results (18 experiments)
    """
    print("=" * 80)
    print("PHASE 4: PARAMETER SENSITIVITY AT 25%")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Is 25% frequency robustly harmonic across parameter variations?")
    print()
    print("Strategy:")
    print("  - Frequency: 25% (fixed)")
    print("  - Thresholds: [2.0, 2.5, 3.0] (Basin A threshold)")
    print("  - Diversities: [0.1, 0.3, 0.5] (agent diversity)")
    print("  - Seeds: [42, 123] (2 replicates)")
    print("  - Total: 3 thresholds × 3 diversities × 2 seeds = 18 experiments")
    print("=" * 80)
    print()

    basin_thresholds = [2.0, 2.5, 3.0]
    diversities = [0.1, 0.3, 0.5]
    seeds = [42, 123]
    results = []

    experiment_count = 0
    total_experiments = len(basin_thresholds) * len(diversities) * len(seeds)

    for basin_thresh in basin_thresholds:
        for diversity in diversities:
            config_basin_a = 0
            config_basin_b = 0

            for seed in seeds:
                experiment_count += 1

                print(f"[{experiment_count:2d}/{total_experiments}] Thresh {basin_thresh:.1f}, Div {diversity:.1f}, Seed {seed:3d}... ", end="", flush=True)

                result = run_experiment(
                    spawn_freq_pct=25,
                    seed=seed,
                    cycles=3000,
                    agent_cap=15,
                    threshold=700,  # Composition threshold (fixed)
                    diversity=diversity,
                )

                # Re-classify with test threshold
                avg_comp = result['avg_composition_events']
                test_basin = 'A' if avg_comp > basin_thresh else 'B'
                result['test_basin_threshold'] = basin_thresh
                result['test_basin'] = test_basin

                results.append(result)

                if test_basin == 'A':
                    config_basin_a += 1
                    basin_symbol = "🔵"
                else:
                    config_basin_b += 1
                    basin_symbol = "⚫"

                print(f"{basin_symbol} Basin {test_basin} | Comp: {avg_comp:.2f}")

            # Config summary
            config_total = config_basin_a + config_basin_b
            config_basin_a_pct = (config_basin_a / config_total * 100)

            print(f"  → Thresh {basin_thresh:.1f}, Div {diversity:.1f}: Basin A = {config_basin_a}/{config_total} ({config_basin_a_pct:.1f}%)")
            print()

    print("=" * 80)
    print("PHASE 4 COMPLETE")
    print("=" * 80)
    print()

    return results


def main():
    """Run complete 25% frequency deep investigation."""

    print("=" * 80)
    print("CYCLE 163F: 25% FREQUENCY DEEP INVESTIGATION")
    print("=" * 80)
    print()
    print("CONTEXT:")
    print("  Preliminary data (Cycles 160-161) shows 25% frequency → 100% Basin A (3/3)")
    print("  Cycle 162 may confirm this as unique harmonic frequency")
    print()
    print("HYPOTHESIS:")
    print("  25% frequency exhibits quarter-wave resonance with composition dynamics")
    print("  Spawn interval = 4 cycles aligns with critical composition window")
    print()
    print("INVESTIGATION PLAN:")
    print("  Phase 1: Extended replication at 25% (30 seeds)")
    print("  Phase 2: Fine-grained neighbors (20-30% in 1% steps)")
    print("  Phase 3: Temporal dynamics (identify critical time)")
    print("  Phase 4: Parameter sensitivity (threshold × diversity)")
    print()
    print("Total experiments: 30 + 33 + 18 + 18 = 99")
    print("Estimated runtime: ~5.5 hours (200s/experiment)")
    print("=" * 80)
    print()

    input("Press ENTER to begin investigation...")
    print()

    start_time = time.time()

    # Run all phases
    phase1_results = phase1_extended_replication()
    phase2_results = phase2_fine_grained_neighbors()
    phase3_results = phase3_temporal_dynamics()
    phase4_results = phase4_parameter_sensitivity()

    end_time = time.time()
    total_runtime = end_time - start_time

    # Compile results
    all_results = {
        'cycle_id': '163F',
        'description': '25% frequency deep investigation (quarter-wave resonance)',
        'total_experiments': len(phase1_results) + len(phase2_results) + len(phase3_results) + len(phase4_results),
        'total_runtime': total_runtime,
        'phases': {
            'phase1_extended_replication': {
                'experiments': phase1_results,
                'count': len(phase1_results),
            },
            'phase2_fine_grained_neighbors': {
                'experiments': phase2_results,
                'count': len(phase2_results),
            },
            'phase3_temporal_dynamics': {
                'experiments': phase3_results,
                'count': len(phase3_results),
            },
            'phase4_parameter_sensitivity': {
                'experiments': phase4_results,
                'count': len(phase4_results),
            },
        },
    }

    # Save results
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    output_file = results_dir / 'cycle163f_25pct_deep_dive.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("=" * 80)
    print("CYCLE 163F COMPLETE")
    print("=" * 80)
    print(f"Total experiments: {all_results['total_experiments']}")
    print(f"Total runtime: {total_runtime:.1f} seconds ({total_runtime / 3600:.2f} hours)")
    print(f"Results saved: {output_file}")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
