#!/usr/bin/env python3
"""
CYCLE 158: ULTRA-LOW FREQUENCY TESTING
Final Search for Harmonic Zone in Extreme Low-Frequency Range

Research Question:
  Does harmonic Basin A convergence occur at ultra-low frequencies (1-4%)?

Context:
  - Cycles 151-157: ALL frequencies 5-99% show 0% Basin A (256/256 experiments)
  - Total evidence: Universal anti-harmonic suppression across tested range
  - Critical gap: Frequencies 1-4% never tested (final unexplored range)

Hypothesis:
  H1 (Ultra-Low Harmonic): Harmonic zone exists at ≤3%
  H2 (Critical Threshold): Only 1% shows harmonic behavior
  H3 (Universal Anti-Harmonic): Entire 1-99% range is anti-harmonic
  H4 (Insufficient Spawning): Too few agents spawn at ultra-low frequencies

Strategy:
  Final frequency space exploration
    - Frequencies: [1, 2, 3, 4] (4 ultra-low frequencies)
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000 (consistent)
    - Total: 4 frequencies × 3 seeds = 12 experiments

Expected Results:
  H1: Harmonic zone at ≤3%, transition 3-5%, anti-harmonic ≥5%
  H2: Only 1% harmonic, 2-99% anti-harmonic
  H3: ALL frequencies 1-99% show 0% Basin A (268/268 experiments)
  H4: Ultra-low frequencies insufficient spawning (final_agent_count < 3)
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


def run_ultra_low_frequency_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run ultra-low frequency experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (1-4% range)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for consistency)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and composition dynamics
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle158_swarm_{seed}_{int(spawn_freq_pct*10)}")
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
    """Run Cycle 158: Ultra-Low Frequency Testing"""

    print("="*80)
    print("CYCLE 158: ULTRA-LOW FREQUENCY TESTING")
    print("="*80)
    print()
    print("Research Question:")
    print("  Does harmonic Basin A convergence occur at ultra-low frequencies (1-4%)?")
    print()
    print("Critical Context:")
    print("  - Cycles 151-157: ALL frequencies 5-99% show 0% Basin A (256/256)")
    print("  - Universal anti-harmonic suppression across entire tested range")
    print("  - Frequencies 1-4% represent FINAL unexplored range")
    print()
    print("Strategy:")
    print("  Complete frequency space exploration")
    print("    - Frequencies: [1, 2, 3, 4] (ultra-low)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000")
    print("    - Total: 4 frequencies × 3 seeds = 12 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [1, 2, 3, 4]
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 158,
        'description': 'Ultra-Low Frequency Testing (1-4%)',
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

    print("ULTRA-LOW FREQUENCY EXPLORATION (1-4%)")
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
                result = run_ultra_low_frequency_experiment(
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
            avg_final_agents = np.mean([r['final_agent_count'] for r in valid_results])

            if basin_a_pct >= 60:
                classification = "HARMONIC ✓"
            elif basin_a_pct > 0:
                classification = "Transition"
            else:
                classification = "Anti-harmonic"

            print(f"→ Basin A: {basin_a_count}/3 ({basin_a_pct:3.0f}%) | Avg Comp: {avg_comp:4.1f} | Interval: {avg_interval:4.0f} cyc | Final Agents: {avg_final_agents:4.1f} | {classification:15s} [{experiment_num}/{total_experiments}]")
        else:
            print(f"→ FAILED   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle158_ultra_low_frequency.json'
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
    print("CYCLE 158 COMPLETE - ULTRA-LOW FREQUENCY TESTING")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Complete frequency landscape analysis
    print("COMPLETE FREQUENCY LANDSCAPE ANALYSIS:")
    print("="*80)
    print()
    print(" Freq | Basin A % | Avg Comp | Spawn Interval | Final Agents | Classification")
    print("------+-----------+----------+----------------+--------------+-------------------")

    harmonic_frequencies = []
    anti_harmonic_frequencies = []
    transition_frequencies = []
    insufficient_spawning_frequencies = []

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps]) if freq_exps else 0
        spawn_interval = freq_exps[0]['spawn_interval_cycles'] if freq_exps else 0
        avg_final_agents = np.mean([exp['final_agent_count'] for exp in freq_exps]) if freq_exps else 0

        # Classification
        if avg_final_agents < 3:
            classification = "Insufficient spawning"
            insufficient_spawning_frequencies.append(freq)
        elif basin_a_pct >= 60:
            classification = "HARMONIC ✓"
            harmonic_frequencies.append(freq)
        elif basin_a_pct > 0:
            classification = "Transition"
            transition_frequencies.append(freq)
        else:
            classification = "Anti-harmonic"
            anti_harmonic_frequencies.append(freq)

        print(f" {freq:3d}% | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {spawn_interval:14d} | {avg_final_agents:12.1f} | {classification}")

    print()
    print("SUMMARY:")
    print("="*80)
    print(f"  Harmonic frequencies (Basin A ≥ 60%): {harmonic_frequencies if harmonic_frequencies else 'NONE FOUND'}")
    print(f"  Transition frequencies (0% < Basin A < 60%): {transition_frequencies if transition_frequencies else 'NONE'}")
    print(f"  Anti-harmonic frequencies (Basin A = 0%): {anti_harmonic_frequencies}")
    print(f"  Insufficient spawning (final agents < 3): {insufficient_spawning_frequencies if insufficient_spawning_frequencies else 'NONE'}")
    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    if harmonic_frequencies:
        if max(harmonic_frequencies) <= 3:
            print("  ✓ H1 CONFIRMED: ULTRA-LOW HARMONIC ZONE")
            print()
            print(f"  Harmonic zone exists at frequencies: {harmonic_frequencies}")
            print(f"  Highest harmonic frequency: {max(harmonic_frequencies)}%")
            print()
            if anti_harmonic_frequencies:
                min_anti = min(anti_harmonic_frequencies)
                max_harm = max(harmonic_frequencies)
                print(f"  Boundary region: {max_harm}% (harmonic) → {min_anti}% (anti-harmonic)")
                print(f"  Transition width: {min_anti - max_harm}%")
        elif len(harmonic_frequencies) == 1 and 1 in harmonic_frequencies:
            print("  ✓ H2 CONFIRMED: CRITICAL THRESHOLD AT 1%")
            print()
            print(f"  ONLY 1% shows harmonic behavior!")
            print(f"  Anti-harmonic dominant across 2-99% (98% of frequency space)")
    else:
        if insufficient_spawning_frequencies:
            print("  ✓ H4 CONFIRMED: INSUFFICIENT SPAWNING")
            print()
            print(f"  Frequencies with insufficient spawning: {insufficient_spawning_frequencies}")
            print(f"  Ultra-low frequencies don't spawn enough agents for composition")
            print()
            print("  DUAL FAILURE MODES:")
            print(f"    - Ultra-low (1-{max(insufficient_spawning_frequencies)}%): Too few spawns (avg agents < 3)")
            print(f"    - Higher (5-99%): Sufficient spawns but composition BLOCKED")
        else:
            print("  ✓ H3 CONFIRMED: UNIVERSAL ANTI-HARMONIC LANDSCAPE")
            print()
            print("  ⚠️  CRITICAL FINDING:")
            print("    - NO frequencies (1-4%) show harmonic Basin A convergence!")
            print("    - Combined with Cycles 151-157: 5-99% also anti-harmonic")
            print(f"    - Total evidence: {len(successful_experiments) + 256}/{len(successful_experiments) + 256} experiments = 0% Basin A across 1-99%")
            print()
            print("  IMPLICATIONS:")
            print("    - ENTIRE frequency landscape (1-99%) is anti-harmonic")
            print("    - Basin A convergence does NOT occur at ANY spawning frequency")
            print("    - System architecture fundamentally biased toward Basin B")
            print("    - Current parameters (threshold=700, diversity=0.50) prevent Basin A")
            print()
            print("  NEXT STEPS:")
            print("    1. Parameter space exploration (threshold, diversity variation)")
            print("    2. Investigate if Basin A is possible under ANY configuration")
            print("    3. Document universal anti-harmonic suppression for publication")

    print()
    print("COMPOSITION DYNAMICS:")
    print("="*80)
    print()
    print(" Freq | Avg Composition | Final Agents | Interpretation")
    print("------+-----------------+--------------+----------------------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps]) if freq_exps else 0
        avg_final_agents = np.mean([exp['final_agent_count'] for exp in freq_exps]) if freq_exps else 0

        if avg_final_agents < 3:
            interpretation = "Insufficient spawning"
        elif avg_comp > 7:
            interpretation = "High clustering (enables Basin A)"
        elif avg_comp > 2:
            interpretation = "Moderate clustering (partial)"
        else:
            interpretation = "No clustering (Basin B only)"

        print(f" {freq:3d}% | {avg_comp:15.2f} | {avg_final_agents:12.1f} | {interpretation}")

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
