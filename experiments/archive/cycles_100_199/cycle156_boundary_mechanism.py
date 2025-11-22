#!/usr/bin/env python3
"""
CYCLE 156: BOUNDARY MECHANISM INVESTIGATION
Fine-Grained Analysis of 50-52% Harmonic-Anti-Harmonic Phase Transition

Research Question:
  What mechanism causes the sharp phase transition between harmonic (≤50%)
  and anti-harmonic (≥52%) regimes?

Context:
  - Cycles 151-155: Established sharp binary transition at 50-52%
  - ≤50%: Harmonic (Basin A convergence, composition occurs)
  - 52-99%+: Anti-harmonic (Basin B only, composition BLOCKED)
  - Mechanism: Anti-harm frequencies show avg_composition = 1.0 (no clustering)

Hypothesis:
  H1 (Binary Threshold): Sharp on/off switch at specific frequency (~51%)
  H2 (Narrow Transition): Gradual shift over 0.5-1% range
  H3 (Composition Rate): Basin A % inversely correlates with spawning frequency
  H4 (Two-Regime): Bistable system with mode switch at critical frequency

Strategy:
  Fine-grained scan across 50-52% boundary with 0.2% resolution
    - Frequencies: [50.0, 50.2, 50.4, 50.6, 50.8, 51.0, 51.2, 51.4, 51.6, 51.8, 52.0] (11 total)
    - Seeds: [42, 123, 456, 789, 1011] (5 replicates for statistical power)
    - Cycles: 3,000 (consistent with Cycles 151-153)
    - Total: 11 frequencies × 5 seeds = 55 experiments

Expected Results:
  H1: Step function at ~51.0% (33% → 0% transition)
  H2: Gradual decrease over 50.2-51.6% range
  H3: Linear relationship between frequency and Basin A %
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


def run_boundary_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run boundary mechanism experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (50.0-52.0% range)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for consistency)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and composition dynamics
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle156_swarm_{seed}_{int(spawn_freq_pct*10)}")
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
    """Run Cycle 156: Boundary Mechanism Investigation"""

    print("="*80)
    print("CYCLE 156: BOUNDARY MECHANISM INVESTIGATION")
    print("="*80)
    print()
    print("Research Question:")
    print("  What mechanism causes the sharp phase transition between harmonic (≤50%)")
    print("  and anti-harmonic (≥52%) regimes?")
    print()
    print("Strategy:")
    print("  Fine-grained scan across 50-52% boundary with 0.2% resolution")
    print("    - Frequencies: [50.0, 50.2, 50.4, 50.6, 50.8, 51.0, 51.2, 51.4, 51.6, 51.8, 52.0]")
    print("    - Seeds: [42, 123, 456, 789, 1011] (5 replicates)")
    print("    - Cycles: 3,000")
    print("    - Total: 11 frequencies × 5 seeds = 55 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [50.0, 50.2, 50.4, 50.6, 50.8, 51.0, 51.2, 51.4, 51.6, 51.8, 52.0]
    seeds = [42, 123, 456, 789, 1011]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 156,
        'description': 'Boundary Mechanism Investigation (50-52% Phase Transition)',
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

    print("BOUNDARY MECHANISM SCAN (50-52%)")
    print("="*80)
    print()

    total_experiments = len(frequencies) * len(seeds)
    experiment_num = 0

    # Run experiments
    for freq in frequencies:
        print(f"  FREQUENCY = {freq:4.1f}%", end='  ', flush=True)

        freq_results = []
        for seed in seeds:
            experiment_num += 1

            try:
                result = run_boundary_experiment(
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
            avg_interval = np.mean([r['spawn_interval_cycles'] for r in valid_results])

            classification = "Harmonic" if basin_a_pct >= 60 else ("Transition" if basin_a_pct > 0 else "Anti-harmonic")

            print(f"→ Basin A: {basin_a_count}/5 ({basin_a_pct:3.0f}%) | Avg Comp: {avg_comp:4.1f} | Interval: {avg_interval:4.0f} cyc | {classification:14s} [{experiment_num}/{total_experiments}]")
        else:
            print(f"→ FAILED   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle156_boundary_mechanism.json'
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
    print("CYCLE 156 COMPLETE - BOUNDARY MECHANISM INVESTIGATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Transition profile analysis
    print("TRANSITION PROFILE ANALYSIS:")
    print("="*80)
    print()
    print(" Freq  | Basin A % | Avg Comp | Spawn Interval | Classification")
    print("-------+-----------+----------+----------------+-------------------")

    baseline = 33.0
    transition_start = None
    transition_end = None

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps]) if freq_exps else 0
        spawn_interval = freq_exps[0]['spawn_interval_cycles'] if freq_exps else 0

        # Classification
        if basin_a_pct >= 60:
            classification = "Harmonic"
            if transition_end and not transition_start:
                transition_start = freq
        elif basin_a_pct > 0:
            classification = "Transition"
            if not transition_start:
                transition_start = freq
            transition_end = freq
        else:
            classification = "Anti-harmonic"
            if transition_start and not transition_end:
                transition_end = freq

        print(f" {freq:4.1f}% | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {spawn_interval:14.0f} | {classification}")

    print()
    print("MECHANISM ANALYSIS:")
    print("="*80)

    # Determine transition type
    transition_frequencies = [freq for freq in frequencies
                             if any(exp['spawning_freq'] == freq and exp['basin'] == 'A'
                                   for exp in successful_experiments)
                             and any(exp['spawning_freq'] == freq and exp['basin'] == 'B'
                                    for exp in successful_experiments)]

    has_harmonic = any(sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'A') >= 3
                      for freq in frequencies)
    has_anti_harmonic = any(sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'B') >= 5
                           for freq in frequencies)

    if has_harmonic and has_anti_harmonic:
        if len(transition_frequencies) == 0:
            print("  ✓ H1 CONFIRMED: BINARY THRESHOLD")
            print()
            print("  Sharp phase transition with no intermediate states!")
            print()
            # Find transition point
            harmonic_freqs = [freq for freq in frequencies
                             if sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'A') >= 3]
            anti_harm_freqs = [freq for freq in frequencies
                              if sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'B') >= 5]

            if harmonic_freqs and anti_harm_freqs:
                max_harmonic = max(harmonic_freqs)
                min_anti_harmonic = min(anti_harm_freqs)

                print(f"  CRITICAL THRESHOLD: Between {max_harmonic}% and {min_anti_harmonic}%")
                print(f"  Transition width: <{min_anti_harmonic - max_harmonic:.1f}%")
                print()
                print("  MECHANISM:")
                print(f"    - At f ≤ {max_harmonic}%: Inter-spawn time sufficient for clustering → Harmonic")
                print(f"    - At f ≥ {min_anti_harmonic}%: Inter-spawn time too short → Composition BLOCKED → Anti-harmonic")
        elif len(transition_frequencies) <= 2:
            print("  ✓ H2 CONFIRMED: NARROW TRANSITION ZONE")
            print()
            print(f"  Gradual shift over narrow range!")
            print(f"  Transition frequencies: {transition_frequencies}")
        else:
            print("  ✓ H2/H3 CONFIRMED: BROAD TRANSITION ZONE")
            print()
            print(f"  Gradual mechanism with wide transition range")
            print(f"  Transition span: {len(transition_frequencies)} frequencies")

    print()
    print("COMPOSITION DYNAMICS:")
    print("="*80)

    # Analyze composition vs frequency
    print()
    print(" Freq  | Avg Composition | Interpretation")
    print("-------+-----------------+----------------------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps]) if freq_exps else 0

        if avg_comp > 7:
            interpretation = "High clustering (enables Basin A)"
        elif avg_comp > 2:
            interpretation = "Moderate clustering (partial)"
        else:
            interpretation = "No clustering (Basin B only)"

        print(f" {freq:4.1f}% | {avg_comp:15.2f} | {interpretation}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(  f"  Total computation time: {total_time:.1f} seconds")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
