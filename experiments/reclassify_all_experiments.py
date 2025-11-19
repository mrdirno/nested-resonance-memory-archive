#!/usr/bin/env python3
"""
RE-CLASSIFICATION OF ALL 331 EXPERIMENTS (CYCLES 151-161)
Testing Multiple Basin A Thresholds After Discovering Miscalibration

CONTEXT:
  - Cycle 160: Validated spawn fix, showed avg_composition = 2.2-2.6
  - Cycle 161: Found transition between threshold 2.0 (Basin A) and 2.5 (Basin B)
  - Original threshold (7.0) was far too high for actual system dynamics

PURPOSE:
  Re-classify all 331 experiments with realistic thresholds to determine
  if "universal anti-harmonic landscape" was threshold artifact.

APPROACH:
  Load all experiment results from Cycles 151-161
  Test multiple thresholds: [1.5, 2.0, 2.5, 3.0, 5.0, 7.0]
  Determine Basin A % for each threshold across all experiments
  Find optimal threshold that reveals frequency landscape structure
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict


def load_experiment_results():
    """Load all experiment results from Cycles 151-161."""
    results_dir = Path(__file__).parent / 'results'

    all_experiments = []
    cycle_files = [
        'cycle151_fine_grained_frequency_sweep.json',
        'cycle152_frequency_landscape_completion.json',
        'cycle153_extended_frequency_landscape.json',
        'cycle154_complete_frequency_spectrum.json',
        'cycle155_final_frequency_gaps.json',
        'cycle156_harmonic_boundary_investigation.json',
        'cycle157_harmonic_zone_discovery.json',
        'cycle158_ultra_low_frequency.json',
        'cycle159_parameter_space.json',
        'cycle160_corrected_spawning.json',
        'cycle161_threshold_calibration.json',
    ]

    for filename in cycle_files:
        filepath = results_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                cycle_id = data.get('cycle_id', 'unknown')
                experiments = data.get('experiments', [])

                for exp in experiments:
                    if 'avg_composition_events' in exp:
                        all_experiments.append({
                            'cycle_id': cycle_id,
                            'seed': exp.get('seed'),
                            'frequency': exp.get('spawning_freq'),
                            'threshold_param': exp.get('threshold'),
                            'diversity': exp.get('diversity'),
                            'avg_composition': exp['avg_composition_events'],
                            'max_composition': exp.get('max_composition_events'),
                            'original_basin': exp.get('basin'),
                        })

    return all_experiments


def reclassify_with_thresholds(experiments, thresholds):
    """Re-classify experiments with multiple Basin A thresholds."""

    results = {}

    for threshold in thresholds:
        # Classify each experiment
        for exp in experiments:
            avg_comp = exp['avg_composition']
            exp[f'basin_threshold_{threshold}'] = 'A' if avg_comp > threshold else 'B'

        # Calculate Basin A percentage
        basin_a_count = sum(1 for exp in experiments if exp[f'basin_threshold_{threshold}'] == 'A')
        basin_a_pct = (basin_a_count / len(experiments) * 100) if experiments else 0

        results[threshold] = {
            'basin_a_count': basin_a_count,
            'basin_a_pct': basin_a_pct,
            'total_experiments': len(experiments)
        }

    return results


def analyze_frequency_dependence(experiments, optimal_threshold):
    """Analyze Basin A % vs frequency with optimal threshold."""

    frequency_analysis = defaultdict(lambda: {'basin_a': 0, 'basin_b': 0})

    for exp in experiments:
        freq = exp.get('frequency')
        if freq is not None:
            basin = exp.get(f'basin_threshold_{optimal_threshold}')
            if basin == 'A':
                frequency_analysis[freq]['basin_a'] += 1
            elif basin == 'B':
                frequency_analysis[freq]['basin_b'] += 1

    # Calculate percentages
    frequency_results = []
    for freq in sorted(frequency_analysis.keys()):
        counts = frequency_analysis[freq]
        total = counts['basin_a'] + counts['basin_b']
        basin_a_pct = (counts['basin_a'] / total * 100) if total > 0 else 0

        frequency_results.append({
            'frequency': freq,
            'basin_a_count': counts['basin_a'],
            'basin_b_count': counts['basin_b'],
            'basin_a_pct': basin_a_pct,
            'total': total
        })

    return frequency_results


def main():
    """Run comprehensive re-classification analysis."""

    print("="*80)
    print("RE-CLASSIFICATION OF ALL EXPERIMENTS (CYCLES 151-161)")
    print("="*80)
    print()
    print("Context:")
    print("  - Original threshold: 7.0 (unreachable)")
    print("  - Observed avg_composition: 2.2-2.6 range")
    print("  - Cycle 161 found transition: threshold 2.0-2.5")
    print()
    print("Loading all experiment results...")

    # Load experiments
    experiments = load_experiment_results()
    print(f"  Loaded {len(experiments)} experiments from Cycles 151-161")
    print()

    # Test multiple thresholds
    thresholds = [1.5, 2.0, 2.5, 3.0, 5.0, 7.0]

    print("THRESHOLD SENSITIVITY ANALYSIS:")
    print("="*80)
    print()
    print(" Threshold | Basin A Count | Basin A % | Total Experiments")
    print("-----------+---------------+-----------+-------------------")

    threshold_results = reclassify_with_thresholds(experiments, thresholds)

    for threshold in thresholds:
        result = threshold_results[threshold]
        count = result['basin_a_count']
        pct = result['basin_a_pct']
        total = result['total_experiments']

        print(f"   {threshold:4.1f}    | {count:13d} | {pct:8.1f}% | {total:17d}")

    print()

    # Find optimal threshold (closest to 50% Basin A for bistable behavior)
    optimal_threshold = min(thresholds, key=lambda t: abs(threshold_results[t]['basin_a_pct'] - 50))
    optimal_pct = threshold_results[optimal_threshold]['basin_a_pct']

    print("OPTIMAL THRESHOLD DETERMINATION:")
    print("="*80)
    print()
    print(f"  Optimal threshold: {optimal_threshold}")
    print(f"  Basin A %: {optimal_pct:.1f}%")
    print(f"  Rationale: Closest to 50% (maximal bistable behavior)")
    print()

    # Frequency-dependent analysis with optimal threshold
    print(f"FREQUENCY LANDSCAPE (Threshold = {optimal_threshold}):")
    print("="*80)
    print()
    print(" Frequency | Basin A | Basin B | Basin A % | Classification")
    print("-----------+---------+---------+-----------+------------------")

    frequency_results = analyze_frequency_dependence(experiments, optimal_threshold)

    for freq_data in frequency_results:
        freq = freq_data['frequency']
        a_count = freq_data['basin_a_count']
        b_count = freq_data['basin_b_count']
        a_pct = freq_data['basin_a_pct']

        if a_pct >= 60:
            classification = "Harmonic"
        elif a_pct >= 40:
            classification = "Mixed"
        else:
            classification = "Anti-harmonic"

        print(f" {freq:8.1f}% | {a_count:7d} | {b_count:7d} | {a_pct:8.1f}% | {classification}")

    print()

    # Composition distribution
    print("COMPOSITION DISTRIBUTION:")
    print("="*80)
    print()

    comp_values = [exp['avg_composition'] for exp in experiments]
    comp_mean = np.mean(comp_values)
    comp_std = np.std(comp_values)
    comp_min = min(comp_values)
    comp_max = max(comp_values)
    comp_median = np.median(comp_values)

    print(f"  Mean:     {comp_mean:.3f}")
    print(f"  Median:   {comp_median:.3f}")
    print(f"  Std Dev:  {comp_std:.3f}")
    print(f"  Range:    [{comp_min:.3f}, {comp_max:.3f}]")
    print()

    # Save results
    output = {
        'total_experiments': len(experiments),
        'thresholds_tested': thresholds,
        'threshold_results': {str(k): v for k, v in threshold_results.items()},
        'optimal_threshold': optimal_threshold,
        'frequency_analysis': frequency_results,
        'composition_stats': {
            'mean': comp_mean,
            'median': comp_median,
            'std': comp_std,
            'min': comp_min,
            'max': comp_max
        }
    }

    output_file = Path(__file__).parent / 'results' / 'reclassification_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {output_file}")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
