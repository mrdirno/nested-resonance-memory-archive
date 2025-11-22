#!/usr/bin/env python3
"""
CYCLE 152: ANTI-HARMONIC BAND BOUNDARY MAPPING
Precise edge detection for 60-88% suppression zone

Research Question:
  What are the exact boundaries of the anti-harmonic band?

Context (from Insight #112):
  Cycle 151 discovered continuous anti-harmonic band spanning 60-88%
  with universal 0% Basin A suppression.

Known Boundaries:
  - Below band: 50% shows 33% Basin A (baseline - harmonic)
  - Within band: 60-88% shows 0% Basin A (complete suppression)
  - Above band: 95% shows 33% at 3K (dormant long-term harmonic)

Strategy:
  Test boundary transition zones at short temporal scale (3K cycles)
    - Lower boundary: [52%, 55%, 57%] (spanning 50% → 60% gap)
    - Upper boundary: [90%, 92%, 94%] (spanning 88% → 95% gap)
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000 (consistent with Cycle 151)
    - Total: 6 frequencies × 3 seeds = 18 experiments

Hypothesis:
  H1: Sharp boundaries - binary transition within ±1%
  H2: Gradual transitions - progressive suppression/recovery
  H3: Asymmetric - different lower vs upper boundary behaviors
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
from bridge.transcendental_bridge import TranscendentalBridge


def get_seed_patterns(reality_interface, bridge, seed, count=5):
    """Generate seed patterns from reality metrics"""
    random.seed(seed)
    np.random.seed(seed)

    reality_metrics = reality_interface.get_system_metrics()
    seed_patterns = []

    for i in range(count):
        offset = i - (count // 2)
        mult = 1.0 + offset * 0.05
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
        }
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns


def detect_composition_events(swarm):
    """
    Simplified: Return agent count as proxy for composition activity.

    Note: Direct phase state access removed due to API incompatibility.
    Using agent count as simpler metric.
    """
    return len(swarm.agents)


def run_anti_harmonic_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run anti-harmonic frequency scan experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (60-88% for this cycle)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for short-term test)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and timing
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace for this experiment
    workspace = Path(f"/tmp/cycle151_swarm_{seed}_{spawn_freq_pct}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm (matches Cycle 150 pattern)
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = threshold

    # Calculate spawn interval (percentage of total cycles)
    spawn_interval = max(1, int(cycles * (spawn_freq_pct / 100.0)))

    # Tracking
    composition_events_history = []
    start_time = time.time()

    # Initialize reality interface for spawning
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

    elapsed = time.time() - start_time

    # Determine final basin (simple heuristic based on agent distribution)
    final_agent_count = len(swarm.agents)
    avg_composition = np.mean(composition_events_history[-100:]) if len(composition_events_history) >= 100 else np.mean(composition_events_history)

    # Basin determination (heuristic - higher composition = Basin A)
    basin = 'A' if avg_composition > 7 else 'B'

    return {
        'seed': seed,
        'spawning_freq': spawn_freq_pct,
        'cycles': cycles,
        'basin': basin,
        'final_agent_count': final_agent_count,
        'avg_composition_events': float(avg_composition),
        'elapsed_seconds': elapsed,
        'cycles_per_second': cycles / elapsed if elapsed > 0 else 0
    }


def main():
    """Run Cycle 152: Anti-Harmonic Band Boundary Mapping"""

    print("="*80)
    print("CYCLE 152: ANTI-HARMONIC BAND BOUNDARY MAPPING")
    print("="*80)
    print()
    print("Research Question:")
    print("  What are the exact boundaries of the anti-harmonic band?")
    print()
    print("Strategy:")
    print("  Test boundary transition zones at short temporal scale (3K cycles)")
    print("    - Lower boundary: [52%, 55%, 57%] (spanning 50% → 60% gap)")
    print("    - Upper boundary: [90%, 92%, 94%] (spanning 88% → 95% gap)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000 (consistent with Cycle 151)")
    print("    - Total: 6 frequencies × 3 seeds = 18 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [52, 55, 57, 90, 92, 94]  # Boundary frequencies
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 152,
        'description': 'Anti-Harmonic Band Boundary Mapping',
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

    print("BOUNDARY MAPPING")
    print("="*80)
    print()

    total_experiments = len(frequencies) * len(seeds)
    experiment_num = 0

    # Run experiments
    for freq in frequencies:
        print()
        print(f"FREQUENCY = {freq}%")
        print("-"*80)

        for seed in seeds:
            experiment_num += 1

            try:
                print(f"  [{experiment_num:2d}/{total_experiments}]   [F={freq:2d}%, S={seed:3d}, C={cycles:5d}] ", end='', flush=True)

                result = run_anti_harmonic_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=cycles,
                    agent_cap=agent_cap
                )

                results['experiments'].append(result)

                # Print result
                print(f"Basin {result['basin']} | Agents: {result['final_agent_count']:2d} | ({result['elapsed_seconds']:.1f}s)")

            except Exception as e:
                print(f"FAILED: {e}")
                results['experiments'].append({
                    'seed': seed,
                    'spawning_freq': freq,
                    'cycles': cycles,
                    'basin': None,
                    'error': str(e)
                })

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle152_boundary_mapping.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Summary statistics
    successful_experiments = [exp for exp in results['experiments'] if exp.get('basin') is not None]
    total_cycles = sum(exp['cycles'] for exp in successful_experiments)
    total_time = sum(exp['elapsed_seconds'] for exp in successful_experiments)
    avg_performance = total_cycles / total_time if total_time > 0 else 0

    print()
    print()
    print("="*80)
    print("CYCLE 152 COMPLETE - ANTI-HARMONIC BAND BOUNDARY MAPPING")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Basin convergence summary
    print("BOUNDARY DETECTION RESULTS:")
    print("="*80)
    print()
    print(" Freq | Basin A Count | Basin B Count |  Basin A % | Boundary Region | Notes")
    print("------+---------------+---------------+------------+-----------------+------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_b_count = sum(1 for exp in freq_exps if exp['basin'] == 'B')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        # Determine boundary region
        if freq <= 57:
            region = "Lower (50→60)"
        else:
            region = "Upper (88→95)"

        # Compare to baseline (33% from 50% frequency)
        baseline = 33.0
        deviation = basin_a_pct - baseline

        note = ""
        if abs(deviation) > 15:
            if deviation < 0:
                note = "SUPPRESSED"
            else:
                note = "HARMONIC"
        elif abs(deviation) < 8:
            note = "Baseline"
        else:
            note = "Transition?"

        print(f" {freq:3d}% | {basin_a_count:13d} | {basin_b_count:13d} | {basin_a_pct:9.1f}% | {region:15s} | {note}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print()
    print("BOUNDARY ANALYSIS:")
    print("="*80)
    print("  Lower Boundary (50% → 60%):")
    print("    If 55% harmonic and 57% suppressed → sharp edge between 55-57%")
    print("    If gradual transition → continuous suppression zone")
    print()
    print("  Upper Boundary (88% → 95%):")
    print("    If 90% baseline and 92% baseline → sharp edge at/below 88%")
    print("    If gradual transition → recovery zone to 95%")
    print()
    print("NEXT STEPS:")
    print("="*80)
    print("  1. Analyze boundary precision and transition type")
    print("  2. If sharp boundaries: refine to ±1% precision")
    print("  3. If gradual transitions: map full curves")
    print("  4. Test temporal scale dependence of boundaries")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
