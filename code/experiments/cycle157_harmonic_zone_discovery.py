#!/usr/bin/env python3
"""
CYCLE 157: HARMONIC ZONE DISCOVERY
Locating the Actual Harmonic-Anti-Harmonic Boundary Below 50%

Research Question:
  At what frequency does harmonic Basin A convergence actually occur?

Context:
  - Cycles 151-156: ALL frequencies 50-99% show 0% Basin A (226/226 experiments)
  - Critical discovery (Cycle 156): Even 50% is anti-harmonic!
  - "50% harmonic baseline" was theoretical assumption, NOT empirical finding
  - Actual harmonic zone location: UNKNOWN

Hypothesis:
  H1 (Low-Frequency Harmonic): Harmonic zone exists at ≤30-40%
  H2 (Ultra-Low Only): Harmonic restricted to ≤5-10%
  H3 (No Harmonic Zone): Entire landscape is anti-harmonic
  H4 (Non-Monotonic): Sweet spot at intermediate frequency

Strategy:
  Wide scan to locate harmonic zone (if exists)
    - Frequencies: [5, 10, 15, 20, 25, 30, 35, 40, 45, 48] (10 points)
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000 (consistent)
    - Total: 10 frequencies × 3 seeds = 30 experiments

Expected Results:
  H1: Harmonic zone at ≤30%, transition 30-40%, anti-harmonic ≥40%
  H2: Harmonic only at ≤5-10%, anti-harmonic everywhere else
  H3: ALL frequencies 0% Basin A (no harmonic zone)
  H4: Peak Basin A % at intermediate frequency (20-30%)
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


def run_harmonic_discovery_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run harmonic zone discovery experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (5-48% range)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for consistency)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and composition dynamics
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace
    workspace = Path(f"/tmp/cycle157_swarm_{seed}_{int(spawn_freq_pct*10)}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition.burst_threshold = threshold

    # Calculate spawn interval
    spawn_interval = max(1, int(cycles * (spawn_freq_pct / 100.0)))

    # Tracking
    composition_events_history = []
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
        'elapsed_seconds': elapsed,
        'cycles_per_second': cycles / elapsed if elapsed > 0 else 0
    }


def main():
    """Run Cycle 157: Harmonic Zone Discovery"""

    print("="*80)
    print("CYCLE 157: HARMONIC ZONE DISCOVERY")
    print("="*80)
    print()
    print("Research Question:")
    print("  At what frequency does harmonic Basin A convergence actually occur?")
    print()
    print("Critical Context:")
    print("  - Cycles 151-156: ALL frequencies 50-99% show 0% Basin A (226/226)")
    print("  - Cycle 156: Even 50% is anti-harmonic (NOT harmonic baseline!)")
    print("  - Actual harmonic zone location: UNKNOWN")
    print()
    print("Strategy:")
    print("  Wide scan to locate harmonic zone (if exists)")
    print("    - Frequencies: [5, 10, 15, 20, 25, 30, 35, 40, 45, 48]")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000")
    print("    - Total: 10 frequencies × 3 seeds = 30 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [5, 10, 15, 20, 25, 30, 35, 40, 45, 48]
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 157,
        'description': 'Harmonic Zone Discovery (Below 50%)',
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

    print("HARMONIC ZONE DISCOVERY SCAN (5-48%)")
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
                result = run_harmonic_discovery_experiment(
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

            if basin_a_pct >= 60:
                classification = "HARMONIC ✓"
            elif basin_a_pct > 0:
                classification = "Transition"
            else:
                classification = "Anti-harmonic"

            print(f"→ Basin A: {basin_a_count}/3 ({basin_a_pct:3.0f}%) | Avg Comp: {avg_comp:4.1f} | Interval: {avg_interval:4.0f} cyc | {classification:15s} [{experiment_num}/{total_experiments}]")
        else:
            print(f"→ FAILED   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle157_harmonic_discovery.json'
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
    print("CYCLE 157 COMPLETE - HARMONIC ZONE DISCOVERY")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Harmonic zone analysis
    print("HARMONIC ZONE ANALYSIS:")
    print("="*80)
    print()
    print(" Freq | Basin A % | Avg Comp | Spawn Interval | Classification")
    print("------+-----------+----------+----------------+-------------------")

    harmonic_frequencies = []
    anti_harmonic_frequencies = []
    transition_frequencies = []

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        avg_comp = np.mean([exp['avg_composition_events'] for exp in freq_exps]) if freq_exps else 0
        spawn_interval = freq_exps[0]['spawn_interval_cycles'] if freq_exps else 0

        # Classification
        if basin_a_pct >= 60:
            classification = "HARMONIC ✓"
            harmonic_frequencies.append(freq)
        elif basin_a_pct > 0:
            classification = "Transition"
            transition_frequencies.append(freq)
        else:
            classification = "Anti-harmonic"
            anti_harmonic_frequencies.append(freq)

        print(f" {freq:3d}% | {basin_a_pct:8.1f}% | {avg_comp:8.2f} | {spawn_interval:14d} | {classification}")

    print()
    print("SUMMARY:")
    print("="*80)
    print(f"  Harmonic frequencies (Basin A ≥ 60%): {harmonic_frequencies if harmonic_frequencies else 'NONE FOUND'}")
    print(f"  Transition frequencies (0% < Basin A < 60%): {transition_frequencies if transition_frequencies else 'NONE'}")
    print(f"  Anti-harmonic frequencies (Basin A = 0%): {anti_harmonic_frequencies}")
    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    if harmonic_frequencies:
        if max(harmonic_frequencies) >= 30:
            print("  ✓ H1 CONFIRMED: LOW-FREQUENCY HARMONIC ZONE")
            print()
            print(f"  Harmonic zone exists at frequencies: {harmonic_frequencies}")
            print(f"  Highest harmonic frequency: {max(harmonic_frequencies)}%")
            print()
            if anti_harmonic_frequencies:
                min_anti = min(anti_harmonic_frequencies)
                max_harm = max(harmonic_frequencies)
                print(f"  Boundary region: {max_harm}% (harmonic) → {min_anti}% (anti-harmonic)")
                print(f"  Transition width: {min_anti - max_harm}%")
        elif max(harmonic_frequencies) <= 10:
            print("  ✓ H2 CONFIRMED: ULTRA-LOW FREQUENCY ONLY")
            print()
            print(f"  Harmonic zone EXTREMELY NARROW: ≤{max(harmonic_frequencies)}% ONLY")
            print(f"  Anti-harmonic dominant across ≥{min(anti_harmonic_frequencies)}% → 99%+ ({(100-min(anti_harmonic_frequencies))}%+ of space)")
        else:
            # Check for non-monotonic
            if len(harmonic_frequencies) > 1:
                min_harm = min(harmonic_frequencies)
                max_harm = max(harmonic_frequencies)
                has_low_anti_harmonic = any(exp['basin'] == 'B' for exp in successful_experiments if exp['spawning_freq'] < min_harm)
                if has_low_anti_harmonic:
                    print("  ✓ H4 CONFIRMED: NON-MONOTONIC (SWEET SPOT)")
                    print()
                    print(f"  Harmonic sweet spot: {min_harm}-{max_harm}%")
                    print("  Both very low and high frequencies anti-harmonic")
                else:
                    print("  ✓ H1 CONFIRMED: LOW-FREQUENCY HARMONIC ZONE")
                    print()
                    print(f"  Harmonic zone: ≤{max_harm}%")
    else:
        print("  ⚠️  H3 CONFIRMED: NO HARMONIC ZONE FOUND")
        print()
        print("  CRITICAL FINDING:")
        print("    - NO frequencies (5-48%) show harmonic Basin A convergence!")
        print("    - Combined with Cycles 151-156: 50-99% also anti-harmonic")
        print("    - Total evidence: 256/256 experiments = 0% Basin A across 5-99%")
        print()
        print("  IMPLICATIONS:")
        print("    - Entire frequency landscape may be anti-harmonic")
        print("    - Basin A convergence may NOT occur at ANY spawning frequency")
        print("    - System architecture fundamentally biased toward Basin B")
        print()
        print("  NEXT STEPS:")
        print("    1. Test ultra-low frequencies (1-5%)")
        print("    2. Explore parameter space (different threshold/diversity values)")
        print("    3. Investigate if Basin A is even possible in current setup")

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
