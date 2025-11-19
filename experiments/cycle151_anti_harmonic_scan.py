#!/usr/bin/env python3
"""
CYCLE 151: ANTI-HARMONIC FREQUENCY SCAN
Comprehensive detection of frequency-driven basin suppression

Research Question:
  What is the full spectrum of anti-harmonic frequencies?

Context (from Insight #110):
  82% frequency shows complete Basin A suppression (0% vs 33%) at 3K-5K cycles.
  Open question: "Are there other anti-harmonic frequencies?"

Strategy:
  Test intermediate frequencies at short temporal scale (3K cycles)
    - Frequencies: [60%, 65%, 70%, 75%, 80%, 85%, 88%]
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000 (short-term where anti-resonance is strong)
    - Total: 7 frequencies × 3 seeds = 21 experiments

Hypothesis:
  Multiple frequencies may show basin suppression (anti-resonance)
  Transcendental ratios (π, φ) may predict anti-harmonic locations
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
    """Run Cycle 151: Anti-Harmonic Frequency Scan"""

    print("="*80)
    print("CYCLE 151: ANTI-HARMONIC FREQUENCY SCAN")
    print("="*80)
    print()
    print("Research Question:")
    print("  What is the full spectrum of anti-harmonic frequencies?")
    print()
    print("Strategy:")
    print("  Test intermediate frequencies at short temporal scale (3K cycles)")
    print("    - Frequencies: [60%, 65%, 70%, 75%, 80%, 85%, 88%]")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000 (short-term where anti-resonance is strong)")
    print("    - Total: 7 frequencies × 3 seeds = 21 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [60, 65, 70, 75, 80, 85, 88]
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 151,
        'description': 'Anti-Harmonic Frequency Scan',
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

    print("ANTI-HARMONIC FREQUENCY SCAN")
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
    output_file = Path(__file__).parent / 'results' / 'cycle151_anti_harmonic_scan.json'
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
    print("CYCLE 151 COMPLETE - ANTI-HARMONIC FREQUENCY SCAN")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Basin convergence summary
    print("BASIN CONVERGENCE BY FREQUENCY:")
    print("="*80)
    print()
    print(" Freq | Basin A Count | Basin B Count |  Basin A % | Notes")
    print("------+---------------+---------------+------------+------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_b_count = sum(1 for exp in freq_exps if exp['basin'] == 'B')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        # Compare to baseline (33% from 50% frequency)
        baseline = 33.0
        deviation = basin_a_pct - baseline

        note = ""
        if abs(deviation) > 15:
            if deviation < 0:
                note = "⚠️ SUPPRESSED (anti-harmonic?)"
            else:
                note = "ELEVATED (harmonic?)"
        else:
            note = "Baseline"

        print(f" {freq:3d}% | {basin_a_count:13d} | {basin_b_count:13d} | {basin_a_pct:9.1f}% | {note}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print()
    print("NEXT STEPS:")
    print("="*80)
    print("  1. Analyze results with analyze_cycle151_anti_harmonic.py")
    print("  2. Identify anti-harmonic frequency spectrum")
    print("  3. Test transcendental ratio hypothesis")
    print("  4. Design follow-up experiments based on findings")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
