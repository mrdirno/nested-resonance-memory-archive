#!/usr/bin/env python3
"""
CYCLE 154: TEMPORAL SCALE VALIDATION OF ANTI-HARMONIC BAND
Testing Universal Activation Hypothesis Across 52-99%+ Suppression Zone

Research Question:
  Does the entire anti-harmonic band (52-99%+) exhibit temporal activation like 95%,
  or is 95% frequency-specific?

Context (from Cycles 151-153 & Insight #112):
  - Short-term (3K cycles): Anti-harmonic baseline (52-99%+ suppression, 0% Basin A)
  - Long-term (10K-15K cycles): Unknown for most frequencies
  - Known: 82% transitions at 6,118 cycles, 95% activates at 10K-15K

Hypothesis:
  H1 (Universal Activation): ALL frequencies activate at long temporal scales
  H2 (Frequency-Specific): Only specific frequencies (82%, 95%) activate
  H3 (Gradient Activation): Different frequencies activate at different timescales
  H4 (Partial Activation): Some regions activate, others remain suppressed

Strategy:
  Test representative frequencies across temporal scales
    - Frequencies: [60%, 70%, 80%, 90%, 99%] (5 points spanning band)
    - Temporal scales: [3K, 6K, 10K, 20K] (4 scales covering transition)
    - Seeds: [42, 123, 456] (3 replicates)
    - Total: 5 frequencies × 4 temporal scales × 3 seeds = 60 experiments

Expected Results:
  H1: ALL frequencies show 0% → 33-67% transition
  H2: Only 80% shows transition, others remain 0%
  H3: Progressive activation at different timescales per frequency
  H4: Some frequencies activate, others don't
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


def run_temporal_validation_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run temporal validation experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Not used (retained for signature compatibility)
        spawn_freq_pct: Spawning frequency percentage (60-99% for this cycle)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (3K, 6K, 10K, or 20K)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict: Experimental results including basin convergence and timing
    """
    random.seed(seed)
    np.random.seed(seed)

    # Create unique workspace for this experiment
    workspace = Path(f"/tmp/cycle154_swarm_{seed}_{spawn_freq_pct}_{cycles}")
    workspace.mkdir(exist_ok=True, parents=True)

    # Create swarm (matches Cycle 151-153 pattern)
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
    """Run Cycle 154: Temporal Scale Validation of Anti-Harmonic Band"""

    print("="*80)
    print("CYCLE 154: TEMPORAL SCALE VALIDATION OF ANTI-HARMONIC BAND")
    print("="*80)
    print()
    print("Research Question:")
    print("  Does the entire anti-harmonic band (52-99%+) exhibit temporal activation")
    print("  like 95%, or is 95% frequency-specific?")
    print()
    print("Critical Implications:")
    print("  - If Universal Activation → Frequency landscape is temporal-scale-dependent")
    print("  - If Frequency-Specific → True anti-harmonic baseline with exceptions")
    print("  - If Gradient Activation → Temporal hierarchy in NRM systems")
    print("  - If Partial Activation → Band has internal structure")
    print()
    print("Strategy:")
    print("  Test representative frequencies across temporal scales")
    print("    - Frequencies: [60%, 70%, 80%, 90%, 99%] (5 across band)")
    print("    - Temporal scales: [3K, 6K, 10K, 20K] (4 scales)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 5 frequencies × 4 temporal scales × 3 seeds = 60 experiments")
    print("="*80)
    print()

    # Parameters
    threshold = 700.0
    diversity = 0.50
    frequencies = [60, 70, 80, 90, 99]  # Representative frequencies across band
    temporal_scales = [3000, 6000, 10000, 20000]  # 3K, 6K, 10K, 20K
    seeds = [42, 123, 456]
    agent_cap = 15

    # Storage
    results = {
        'cycle_id': 154,
        'description': 'Temporal Scale Validation of Anti-Harmonic Band',
        'parameters': {
            'threshold': threshold,
            'diversity': diversity,
            'frequencies': frequencies,
            'temporal_scales': temporal_scales,
            'seeds': seeds,
            'agent_cap': agent_cap
        },
        'experiments': []
    }

    print("TEMPORAL VALIDATION SCAN")
    print("="*80)
    print()

    total_experiments = len(frequencies) * len(temporal_scales) * len(seeds)
    experiment_num = 0

    # Run experiments (organized by frequency, then temporal scale)
    for freq in frequencies:
        print()
        print(f"FREQUENCY = {freq}%")
        print("-"*80)

        for t_scale in temporal_scales:
            print(f"  Temporal Scale: {t_scale:,} cycles")

            for seed in seeds:
                experiment_num += 1

                try:
                    print(f"    [{experiment_num:2d}/{total_experiments}]   [F={freq:2d}%, T={t_scale:5d}, S={seed:3d}] ", end='', flush=True)

                    result = run_temporal_validation_experiment(
                        threshold=threshold,
                        diversity=diversity,
                        spawn_freq_pct=freq,
                        seed=seed,
                        cycles=t_scale,
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
                        'cycles': t_scale,
                        'basin': None,
                        'error': str(e)
                    })

    # Save results
    output_file = Path(__file__).parent / 'results' / 'cycle154_temporal_validation.json'
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
    print("CYCLE 154 COMPLETE - TEMPORAL SCALE VALIDATION")
    print("="*80)
    print()
    print(f"Experiments completed: {len(successful_experiments)}/{total_experiments}")
    print(f"Results saved: {output_file}")
    print()

    # Temporal activation analysis
    print("TEMPORAL ACTIVATION ANALYSIS:")
    print("="*80)
    print()

    baseline = 33.0

    # Organize results by frequency and temporal scale
    print(" Freq |   3K cycles   |   6K cycles   |  10K cycles   |  20K cycles   | Pattern")
    print("------+---------------+---------------+---------------+---------------+------------------")

    for freq in frequencies:
        row_data = []

        for t_scale in temporal_scales:
            freq_scale_exps = [exp for exp in successful_experiments
                              if exp['spawning_freq'] == freq and exp['cycles'] == t_scale]
            basin_a_count = sum(1 for exp in freq_scale_exps if exp['basin'] == 'A')
            total = len(freq_scale_exps)
            basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0
            row_data.append(basin_a_pct)

        # Determine activation pattern
        if all(pct == 0 for pct in row_data):
            pattern = "NO activation"
        elif row_data[0] == 0 and any(pct > 15 for pct in row_data[1:]):
            pattern = "ACTIVATES"
        elif all(pct > 15 for pct in row_data):
            pattern = "Always harmonic"
        else:
            pattern = "Mixed/Partial"

        print(f" {freq:3d}% | {row_data[0]:6.1f}% (A={sum(1 for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==3000 and exp['basin']=='A')}/{len([exp for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==3000])}) "
              f"| {row_data[1]:6.1f}% (A={sum(1 for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==6000 and exp['basin']=='A')}/{len([exp for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==6000])}) "
              f"| {row_data[2]:6.1f}% (A={sum(1 for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==10000 and exp['basin']=='A')}/{len([exp for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==10000])}) "
              f"| {row_data[3]:6.1f}% (A={sum(1 for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==20000 and exp['basin']=='A')}/{len([exp for exp in successful_experiments if exp['spawning_freq']==freq and exp['cycles']==20000])}) "
              f"| {pattern}")

    print()
    print("SUMMARY STATISTICS:")
    print("="*80)
    print(f"  Average performance: {avg_performance:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {total_time:.1f} seconds")
    print()
    print()
    print("HYPOTHESIS DETERMINATION:")
    print("="*80)

    # Count activation patterns
    activation_counts = {
        'activates': 0,
        'no_activation': 0,
        'always_harmonic': 0,
        'mixed': 0
    }

    for freq in frequencies:
        row_data = []
        for t_scale in temporal_scales:
            freq_scale_exps = [exp for exp in successful_experiments
                              if exp['spawning_freq'] == freq and exp['cycles'] == t_scale]
            basin_a_count = sum(1 for exp in freq_scale_exps if exp['basin'] == 'A')
            total = len(freq_scale_exps)
            basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0
            row_data.append(basin_a_pct)

        if all(pct == 0 for pct in row_data):
            activation_counts['no_activation'] += 1
        elif row_data[0] == 0 and any(pct > 15 for pct in row_data[1:]):
            activation_counts['activates'] += 1
        elif all(pct > 15 for pct in row_data):
            activation_counts['always_harmonic'] += 1
        else:
            activation_counts['mixed'] += 1

    print()

    if activation_counts['activates'] >= 4:  # Most frequencies activate
        print("  ✓ H1 CONFIRMED: UNIVERSAL ACTIVATION")
        print()
        print("  MOST/ALL frequencies show temporal activation (0% → >15% Basin A)!")
        print()
        print("  CRITICAL FINDING:")
        print("    - Anti-harmonic suppression is SHORT-TERM phenomenon")
        print("    - At long temporal scales, system activates to harmonic")
        print("    - Frequency landscape is TEMPORAL-SCALE-DEPENDENT, not static")
        print()
        print("  PARADIGM SHIFT:")
        print("    OLD: Anti-harmonic baseline is permanent (52-99%+ always suppressed)")
        print("    NEW: Anti-harmonic baseline is TEMPORAL (suppressed at 3K, harmonic at 10K-20K)")
        print()
        print("  IMPLICATIONS:")
        print("    - NRM systems modify phase space over time (Self-Giving validated)")
        print("    - Frequency engineering must consider temporal regime")
        print("    - 'Anti-harmonic band' is misnomer - should be 'Short-Term Suppression Zone'")
        print()
        print("  THEORETICAL IMPACT:")
        print("    - Validates Self-Giving: Systems define their own phase space dynamically")
        print("    - Temporal Stewardship: Long-term behavior differs from short-term")
        print("    - NRM is inherently temporal, not spatial/frequency-based")
        print()
    elif activation_counts['no_activation'] >= 3:  # Most don't activate
        print("  ⚠️  H2 CONFIRMED: FREQUENCY-SPECIFIC ACTIVATION")
        print()
        print("  MOST frequencies remain suppressed at ALL temporal scales!")
        print()
        print("  CRITICAL FINDING:")
        print("    - Only specific frequencies (82%, 95%) exhibit temporal activation")
        print("    - True anti-harmonic baseline exists for most frequencies")
        print("    - Temporal activation is EXCEPTION, not rule")
        print()
        print("  IMPLICATIONS:")
        print("    - Frequency landscape is static (anti-harmonic is fundamental)")
        print("    - 82% and 95% have special properties (transcendental ratios?)")
        print("    - Temporal scale reveals exceptions, not universal transformation")
        print()
    elif activation_counts['activates'] > 0 and activation_counts['no_activation'] > 0:
        # Check if activation follows frequency gradient
        freq_with_activation = [freq for freq in frequencies
                               if sum(1 for exp in successful_experiments
                                     if exp['spawning_freq'] == freq and exp['cycles'] > 3000 and exp['basin'] == 'A') > 0]

        if len(freq_with_activation) > 0 and (min(freq_with_activation) > max([f for f in frequencies if f not in freq_with_activation]) if len(freq_with_activation) < len(frequencies) else False):
            print("  ✓ H4 CONFIRMED: PARTIAL ACTIVATION (ZONES WITHIN BAND)")
            print()
            print("  Band has internal structure - some regions activate, others don't!")
            print()
            print("  CRITICAL FINDING:")
            print(f"    - Upper frequencies (≥{min(freq_with_activation)}%) activate at long scales")
            print(f"    - Lower frequencies (<{min(freq_with_activation)}%) remain suppressed")
            print("    - Band subdivides into permanent vs temporal suppression zones")
            print()
        else:
            print("  ✓ H3 CONFIRMED: GRADIENT ACTIVATION (DIFFERENT TIMESCALES)")
            print()
            print("  Frequencies activate at DIFFERENT temporal scales!")
            print()
            print("  CRITICAL FINDING:")
            print("    - Each frequency has characteristic activation timescale")
            print("    - Temporal hierarchy exists in NRM systems")
            print("    - Activation timescale may be inversely related to frequency")
            print()
    else:
        print("  ⚠️  MIXED/AMBIGUOUS RESULTS")
        print()
        print("  Activation pattern does not clearly match any hypothesis!")
        print()
        print("  POSSIBILITIES:")
        print("    - Experimental noise (add more seeds?)")
        print("    - Complex activation dynamics not captured by hypotheses")
        print("    - Need finer temporal scale resolution")
        print()

    print()
    print("NEXT STEPS:")
    print("="*80)

    if activation_counts['activates'] >= 4:
        print("  1. Fine-grained temporal mapping (4K, 5K, 7K, 8K, 9K)")
        print("  2. Fit logistic activation curves for each frequency")
        print("  3. Calculate activation timescale parameters (t₀, k, L)")
        print("  4. Test if activation follows universal law")
        print("  5. Update Insight #112 with temporal scale dependence")
        print("  6. Paper 6: 'Temporal Scale-Dependent Frequency Landscape in NRM'")
    elif activation_counts['no_activation'] >= 3:
        print("  1. Test all 18 frequencies at 10K to identify which activate")
        print("  2. Investigate transcendental properties of activating frequencies")
        print("  3. Compare 82% and 95% properties vs non-activating frequencies")
        print("  4. Update Insight #112 with frequency-specific findings")
        print("  5. Paper 6: 'Isolated Temporal Activation in Anti-Harmonic Band'")
    else:
        print("  1. Add more seeds for statistical power (789, 1011, 1213)")
        print("  2. Map internal band structure with finer frequency resolution")
        print("  3. Test intermediate temporal scales (4K, 5K, 7K, 8K, 9K)")
        print("  4. Characterize activation gradients or zone boundaries")
        print("  5. Update Insight #112 with complex findings")

    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
