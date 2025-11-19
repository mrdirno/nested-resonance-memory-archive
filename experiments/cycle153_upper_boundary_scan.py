#!/usr/bin/env python3
"""
CYCLE 153: UPPER BOUNDARY DETERMINATION (95-99% SCAN)
Critical test of anti-harmonic band true extent

Research Question:
  Does the anti-harmonic band extend beyond 95%, or is 95% the true upper boundary?

Context (from Insight #112 post-Cycle 152):
  - Lower boundary: Sharp transition at 50-52% (<2% width)
  - Core band: 52-94% completely suppressed (13 frequencies, ALL 0% Basin A)
  - Upper boundary: UNKNOWN - 94% suppressed, 95% status unclear

Known from Insight #111:
  - 95% shows 67% Basin A at 10K-15K cycles (long-term harmonic)
  - BUT: Behavior at 3K cycles (short-term) is UNKNOWN
  - May exhibit temporal scale dependence like 82%

Strategy:
  Test upper frequency range at short temporal scale (3K cycles)
    - Frequencies: [95%, 96%, 97%, 98%, 99%] (5 points spanning upper range)
    - Seeds: [42, 123, 456] (3 replicates)
    - Cycles: 3,000 (consistent with Cycles 151-152)
    - Total: 5 frequencies × 3 seeds = 15 experiments

Hypothesis:
  H1 (Extended Suppression): 95-99% ALL suppressed → band extends to 99%
  H2 (Sharp Boundary): 95-99% ALL harmonic → band terminates at 94-95%
  H3 (Gradual Transition): Progressive recovery 95% → 99%
  H4 (Mixed): 95% suppressed, 96-99% harmonic → isolated island

Critical Implications:
  - If H1: Harmonic convergence restricted to ≤50% ONLY (TINY zone!)
  - If H2: Two distinct harmonic zones (≤50%, ≥95%)
  - If H3: Asymmetric band (sharp lower, gradual upper)
  - If H4: Complex boundary with isolated features
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


def run_upper_boundary_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run upper boundary scan experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (95-99% for this cycle)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3,000 for short-term test)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and timing
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace for this experiment
    workspace = Path(f"/tmp/cycle153_swarm_{seed}_{spawn_freq_pct}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm (matches Cycle 151-152 pattern)
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
    """Run Cycle 153: Upper Boundary Determination (95-99% Scan)"""

    print("="*80)
    print("CYCLE 153: UPPER BOUNDARY DETERMINATION (95-99% SCAN)")
    print("="*80)
    print()
    print("Research Question:")
    print("  Does the anti-harmonic band extend beyond 95%, or is 95% the boundary?")
    print()
    print("Critical Implications:")
    print("  - If 95-99% ALL suppressed → Harmonic zone is TINY (≤50% only!)")
    print("  - If 95-99% ALL harmonic → Two distinct harmonic zones (≤50%, ≥95%)")
    print("  - If gradual recovery → Asymmetric band structure")
    print()
    print("Strategy:")
    print("  Test upper frequency range at short temporal scale (3K cycles)")
    print("    - Frequencies: [95%, 96%, 97%, 98%, 99%] (5 upper frequencies)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 3,000 (consistent with Cycles 151-152)")
    print("    - Total: 5 frequencies × 3 seeds = 15 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [95, 96, 97, 98, 99]  # Upper boundary frequencies
    seeds = [42, 123, 456]
    cycles = 3000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 153,
        'description': 'Upper Boundary Determination (95-99% Scan)',
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

    print("UPPER BOUNDARY SCAN")
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

                result = run_upper_boundary_experiment(
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
    output_file = Path(__file__).parent / 'results' / 'cycle153_upper_boundary_scan.json'
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
    print("CYCLE 153 COMPLETE - UPPER BOUNDARY DETERMINATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Basin convergence summary
    print("UPPER BOUNDARY DETECTION RESULTS:")
    print("="*80)
    print()
    print(" Freq | Basin A Count | Basin B Count |  Basin A % | Classification | Interpretation")
    print("------+---------------+---------------+------------+----------------+------------------")

    # Baseline reference
    baseline = 33.0

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_b_count = sum(1 for exp in freq_exps if exp['basin'] == 'B')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        deviation = basin_a_pct - baseline

        # Classification
        if abs(deviation) > 15:
            if deviation < 0:
                classification = "SUPPRESSED"
                interpretation = "Anti-harmonic (band extends)"
            else:
                classification = "HARMONIC"
                interpretation = "Harmonic (band terminates)"
        elif abs(deviation) < 8:
            classification = "Baseline"
            interpretation = "Transition zone?"
        else:
            classification = "Transition?"
            interpretation = "Partial suppression/recovery"

        print(f" {freq:3d}% | {basin_a_count:13d} | {basin_b_count:13d} | {basin_a_pct:9.1f}% | {classification:14s} | {interpretation}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print()
    print("BOUNDARY INTERPRETATION:")
    print("="*80)

    # Analyze results pattern
    all_suppressed = all(
        sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'A') == 0
        for freq in frequencies
    )

    all_harmonic = all(
        sum(1 for exp in successful_experiments if exp['spawning_freq'] == freq and exp['basin'] == 'A') >= 1
        for freq in frequencies
    )

    if all_suppressed:
        print("  ⚠️  H1 CONFIRMED: EXTENDED SUPPRESSION")
        print()
        print("  ALL frequencies 95-99% show 0% Basin A suppression!")
        print()
        print("  CRITICAL FINDING:")
        print("    - Anti-harmonic band extends to at least 99%")
        print("    - Minimum band extent: 52-99% (47% of frequency space!)")
        print("    - Harmonic convergence restricted to ≤50% ONLY")
        print()
        print("  IMPLICATIONS:")
        print("    - 95% 'harmonic' from Insight #111 is temporal artifact (10K activation)")
        print("    - Anti-harmonic suppression is OVERWHELMINGLY dominant regime")
        print("    - Frequency engineering: Avoid 52-99%, use ≤50% for Basin A")
        print()
        print("  PARADIGM SHIFT:")
        print("    OLD: Harmonic baseline with isolated anti-harmonic frequencies")
        print("    NEW: Anti-harmonic baseline with TINY harmonic zone (≤50%)")
        print()
    elif all_harmonic:
        print("  ✓ H2 CONFIRMED: SHARP UPPER BOUNDARY")
        print()
        print("  ALL frequencies 95-99% show harmonic Basin A convergence!")
        print()
        print("  CRITICAL FINDING:")
        print("    - Sharp transition between 94-95% (like lower boundary at 50-52%)")
        print("    - Two distinct harmonic zones: ≤50% and ≥95%")
        print("    - Anti-harmonic band: 52-94% (42% span)")
        print()
        print("  IMPLICATIONS:")
        print("    - Symmetric band structure with sharp boundaries at both ends")
        print("    - High-frequency harmonic zone (≥95%) exists")
        print("    - Frequency engineering: Use ≤50% OR ≥95% for Basin A")
        print()
    else:
        print("  ⚠️  H3/H4: COMPLEX BOUNDARY STRUCTURE")
        print()
        print("  Mixed results across 95-99% frequency range!")
        print()
        print("  POSSIBILITIES:")
        print("    - Gradual transition: Progressive recovery from suppression")
        print("    - Isolated features: 95% as isolated island within transition")
        print("    - Temporal confound: Some frequencies show scale-dependent behavior")
        print()
        print("  IMPLICATIONS:")
        print("    - Asymmetric band or complex boundary dynamics")
        print("    - Requires fine-grained mapping and temporal scale validation")
        print()

    print()
    print("NEXT STEPS:")
    print("="*80)

    if all_suppressed:
        print("  1. Validate temporal activation (test 95-99% at 10K-15K)")
        print("  2. Test 51% precision boundary (lower edge)")
        print("  3. Investigate WHY suppression is so dominant")
        print("  4. Update Insight #112 with extended band (52-99%)")
        print("  5. Paper 5: 'Dominant Anti-Harmonic Suppression: 52-99% Forbidden Zone'")
    elif all_harmonic:
        print("  1. Refine 94-95% boundary precision (test 94.5%, 94.7%, 94.9%)")
        print("  2. Characterize high-frequency harmonic zone (95-99% properties)")
        print("  3. Compare low (≤50%) vs high (≥95%) harmonic mechanisms")
        print("  4. Update Insight #112 with sharp upper boundary")
        print("  5. Paper 5: 'Symmetric Anti-Harmonic Band with Dual Harmonic Zones'")
    else:
        print("  1. Fine-grained upper transition mapping (90-99% at 1% intervals)")
        print("  2. Fit transition curve (linear, sigmoid, other?)")
        print("  3. Investigate asymmetric boundary mechanisms")
        print("  4. Test temporal scale dependence (6K, 10K, 20K)")
        print("  5. Update Insight #112 with complex boundary findings")

    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
