#!/usr/bin/env python3
"""
CYCLE 155: COMPREHENSIVE TEMPORAL ACTIVATION MAPPING
Systematic Identification of All Temporal Activators in Anti-Harmonic Band

Research Question:
  Which frequencies in the 52-99%+ anti-harmonic band exhibit temporal activation at 10K cycles?

Context (from Cycles 151-154):
  - Anti-harmonic band: 52-99%+ exhibits 0% Basin A at 3K cycles
  - Permanent suppression: Most frequencies remain 0% Basin A even at 20K cycles (Cycle 154)
  - Known temporal activators: 82% (Insight #110), 95% (Insight #111)
  - Non-activators confirmed: 60%, 70%, 80%, 90%, 99% (Cycle 154)

Critical Gap:
  Only 5 frequencies tested at long temporal scales (Cycle 154)
  Unknown if 82% and 95% are ONLY activators or if others exist

Hypothesis:
  H1 (Isolated Pair): Only 82% and 95% activate
  H2 (Cluster Activation): Multiple frequencies in 82-95% range activate
  H3 (Distributed Activation): Activators distributed across band
  H4 (Transcendental Pattern): Activators follow φ, π, e ratios

Strategy:
  Test ALL 18 frequencies from anti-harmonic band at 10K cycles
    - Frequencies: ALL tested in Cycles 151-153 (52-99%)
    - Temporal scale: 10,000 cycles (95% activates here per Insight #111)
    - Seeds: [42, 123, 456] (3 replicates)
    - Total: 18 frequencies × 3 seeds = 54 experiments

Expected Results:
  H1: Only 82%, 95% → Basin A (2/18 = 11% activation rate)
  H2: 82-95% range shows multiple activators
  H3: Isolated activators distributed across band
  H4: Frequencies near transcendental values activate
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


def detect_composition_events(swarm):
    """
    Simplified: Return agent count as proxy for composition activity.
    """
    return len(swarm.agents)


def run_temporal_mapping_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=10000, agent_cap=15):
    """
    Run temporal mapping experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (52-99% for this cycle)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (10,000 for temporal activation test)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and timing
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace for this experiment
    workspace = Path(f"/tmp/cycle155_swarm_{seed}_{spawn_freq_pct}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm
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

    # Determine final basin
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
    """Run Cycle 155: Comprehensive Temporal Activation Mapping"""

    print("="*80)
    print("CYCLE 155: COMPREHENSIVE TEMPORAL ACTIVATION MAPPING")
    print("="*80)
    print()
    print("Research Question:")
    print("  Which frequencies in the 52-99%+ anti-harmonic band exhibit temporal")
    print("  activation at 10K cycles?")
    print()
    print("Critical Context:")
    print("  - Known activators: 82% (Insight #110), 95% (Insight #111)")
    print("  - Known non-activators: 60%, 70%, 80%, 90%, 99% (Cycle 154)")
    print("  - Unknown: 13 other frequencies untested at long temporal scales")
    print()
    print("Strategy:")
    print("  Test ALL 18 frequencies from anti-harmonic band at 10K cycles")
    print("    - Frequencies: [52, 55, 57, 60, 65, 70, 75, 80, 82, 85,")
    print("                    88, 90, 92, 94, 95, 96, 97, 98, 99] (18 total)")
    print("    - Temporal scale: 10,000 cycles")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 18 frequencies × 3 seeds = 54 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [52, 55, 57, 60, 65, 70, 75, 80, 82, 85, 88, 90, 92, 94, 95, 96, 97, 98, 99]
    seeds = [42, 123, 456]
    cycles = 10000
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 155,
        'description': 'Comprehensive Temporal Activation Mapping',
        'parameters': {
            'threshold': threshold,
            'diversity': diversity,
            'frequencies': frequencies,
            'temporal_scale': cycles,
            'seeds': seeds,
            'agent_cap': agent_cap
        },
        'experiments': []
    }

    print("TEMPORAL ACTIVATION MAPPING (10K CYCLES)")
    print("="*80)
    print()

    total_experiments = len(frequencies) * len(seeds)
    experiment_num = 0

    # Run experiments
    for freq in frequencies:
        print(f"  FREQUENCY = {freq}%", end='  ', flush=True)

        freq_results = []
        for seed in seeds:
            experiment_num += 1

            try:
                result = run_temporal_mapping_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=cycles,
                    agent_cap=agent_cap
                )

                results['experiments'].append(result)
                freq_results.append(result['basin'])

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
        basin_a_count = sum(1 for b in freq_results if b == 'A')
        basin_b_count = sum(1 for b in freq_results if b == 'B')
        basin_a_pct = (basin_a_count / len(freq_results) * 100) if freq_results else 0

        classification = "ACTIVATOR ✓" if basin_a_pct >= 33 else "Non-activator"

        print(f"→ Basin A: {basin_a_count}/3 ({basin_a_pct:.0f}%) | {classification}   [{experiment_num}/{total_experiments}]")

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle155_temporal_mapping.json'
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
    print("CYCLE 155 COMPLETE - COMPREHENSIVE TEMPORAL ACTIVATION MAPPING")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Temporal activator identification
    print("TEMPORAL ACTIVATOR IDENTIFICATION:")
    print("="*80)
    print()

    baseline = 33.0
    activators = []
    non_activators = []

    print(" Freq | Basin A Count | Basin B Count |  Basin A % | Classification")
    print("------+---------------+---------------+------------+------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in successful_experiments if exp['spawning_freq'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_b_count = sum(1 for exp in freq_exps if exp['basin'] == 'B')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        if basin_a_pct >= baseline:
            classification = "TEMPORAL ACTIVATOR ✓"
            activators.append(freq)
        else:
            classification = "Non-activator"
            non_activators.append(freq)

        print(f" {freq:3d}% | {basin_a_count:13d} | {basin_b_count:13d} | {basin_a_pct:9.1f}% | {classification}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print(f"  TEMPORAL ACTIVATORS: {len(activators)}/18 frequencies ({len(activators)/18*100:.1f}%)")
    print(f"    {activators}")
    print()
    print(f"  NON-ACTIVATORS: {len(non_activators)}/18 frequencies ({len(non_activators)/18*100:.1f}%)")
    print(f"    {non_activators}")
    print()
    print()

    # Hypothesis determination
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)
    print()

    # Check validation of known cases
    known_activators = [82, 95]
    known_non_activators = [60, 70, 90, 99]

    validation_passed = True

    print("VALIDATION CHECKS:")
    print()

    for freq in known_activators:
        if freq in activators:
            print(f"  ✓ {freq}% activated (expected from Insights #110, #111)")
        else:
            print(f"  ✗ {freq}% DID NOT activate (ERROR - expected activator!)")
            validation_passed = False

    for freq in known_non_activators:
        if freq in non_activators:
            print(f"  ✓ {freq}% did not activate (expected from Cycle 154)")
        else:
            print(f"  ✗ {freq}% activated (ERROR - expected non-activator!)")
            validation_passed = False

    print()

    if not validation_passed:
        print("⚠️  VALIDATION FAILED - Experimental inconsistency detected!")
        print("   Known cases did not reproduce. Investigation required.")
        print()
    else:
        print("✓ VALIDATION PASSED - Known cases reproduced correctly.")
        print()

    # Determine pattern
    print("ACTIVATION PATTERN:")
    print()

    if len(activators) == 2 and set(activators) == {82, 95}:
        print("  ✓ H1 CONFIRMED: ISOLATED PAIR")
        print()
        print("  ONLY 82% and 95% activate at 10K cycles!")
        print()
        print("  CRITICAL FINDINGS:")
        print(f"    - Temporal activation is EXTREMELY RARE (2/18 = {2/18*100:.1f}%)")
        print("    - 82% and 95% have UNIQUE SPECIAL PROPERTIES")
        print("    - True anti-harmonic baseline is PERMANENT for 89% of band")
        print()
        print("  IMPLICATIONS:")
        print("    - Frequency engineering: Use ONLY 82% or 95% for temporal activation")
        print("    - Special transcendental properties of these frequencies enable activation")
        print("    - Investigate φ, π, e relationships to 82% and 95%")
        print()
        print("  NEXT STEPS:")
        print("    1. Investigate transcendental properties of 82% and 95%")
        print("    2. Compare properties vs non-activating frequencies")
        print("    3. Test hypothesis: 82% ≈ φ ratio enables activation")
        print("    4. Paper 6: 'Isolated Temporal Activation in Anti-Harmonic Band'")
    elif len(activators) > 2:
        # Check if clustered
        activator_range = max(activators) - min(activators)
        if activator_range <= 15:  # Within 15% span
            print("  ✓ H2 CONFIRMED: CLUSTER ACTIVATION")
            print()
            print(f"  {len(activators)} frequencies activate in {min(activators)}-{max(activators)}% range!")
            print()
            print("  TEMPORAL ACTIVATORS:")
            print(f"    {activators}")
            print()
            print("  CRITICAL FINDINGS:")
            print(f"    - Activation rate: {len(activators)}/18 = {len(activators)/18*100:.1f}%")
            print(f"    - Activators cluster in mid-band region ({min(activators)}-{max(activators)}%)")
            print("    - Lower and upper band regions remain permanently suppressed")
            print()
            print("  IMPLICATIONS:")
            print("    - Mid-band has special temporal properties")
            print(f"    - Frequency engineering: Use {min(activators)}-{max(activators)}% for temporal pathways")
            print("    - Band has internal structure (permanent vs temporal zones)")
        else:
            print("  ✓ H3 CONFIRMED: DISTRIBUTED ACTIVATION")
            print()
            print(f"  {len(activators)} frequencies activate across distributed range!")
            print()
            print("  TEMPORAL ACTIVATORS:")
            print(f"    {activators}")
            print()
            print("  CRITICAL FINDINGS:")
            print(f"    - Activation rate: {len(activators)}/18 = {len(activators)/18*100:.1f}%")
            print("    - Activators distributed across band (not clustered)")
            print("    - May follow transcendental pattern")
            print()
    else:
        print("  ⚠️  UNEXPECTED PATTERN")
        print()
        print(f"  {len(activators)} activators found:")
        print(f"    {activators}")
        print()
        print("  This does not match any predicted hypothesis!")
        print()

    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
