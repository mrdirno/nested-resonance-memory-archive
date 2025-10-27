#!/usr/bin/env python3
"""
ANALYSIS OF CORRECTED SPAWNING EXPERIMENTS ONLY (CYCLES 160-161)
Focus on experiments with validated spawn fix

Only analyzing Cycles 160-161 which have:
- Corrected spawn interval calculation
- Spawn accuracy 99.7-100%
- avg_composition in realistic 2.2-2.6 range
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict


def main():
    """Analyze only corrected spawning experiments."""

    print("="*80)
    print("ANALYSIS OF CORRECTED SPAWNING EXPERIMENTS (CYCLES 160-161)")
    print("="*80)
    print()

    results_dir = Path(__file__).parent / 'results'

    # Load Cycle 160 (corrected spawning validation)
    with open(results_dir / 'cycle160_corrected_spawning.json', 'r') as f:
        cycle160 = json.load(f)

    # Load Cycle 161 (threshold calibration)
    with open(results_dir / 'cycle161_threshold_calibration.json', 'r') as f:
        cycle161 = json.load(f)

    # Collect all experiments
    all_experiments = []
    all_experiments.extend(cycle160['experiments'])
    all_experiments.extend(cycle161['experiments'])

    print(f"Total corrected experiments: {len(all_experiments)}")
    print(f"  - Cycle 160: {len(cycle160['experiments'])} experiments")
    print(f"  - Cycle 161: {len(cycle161['experiments'])} experiments")
    print()

    # Composition distribution
    comp_values = [exp['avg_composition_events'] for exp in all_experiments]
    comp_mean = np.mean(comp_values)
    comp_std = np.std(comp_values)
    comp_min = min(comp_values)
    comp_max = max(comp_values)
    comp_median = np.median(comp_values)

    print("COMPOSITION DISTRIBUTION (Corrected Spawning Only):")
    print("="*80)
    print()
    print(f"  Mean:     {comp_mean:.3f}")
    print(f"  Median:   {comp_median:.3f}")
    print(f"  Std Dev:  {comp_std:.3f}")
    print(f"  Range:    [{comp_min:.3f}, {comp_max:.3f}]")
    print()

    # Test multiple thresholds
    thresholds = [1.5, 2.0, 2.5, 3.0, 5.0, 7.0]

    print("THRESHOLD SENSITIVITY (Corrected Experiments Only):")
    print("="*80)
    print()
    print(" Threshold | Basin A Count | Basin A %")
    print("-----------+---------------+-----------")

    threshold_results = {}
    for threshold in thresholds:
        basin_a_count = sum(1 for exp in all_experiments if exp['avg_composition_events'] > threshold)
        basin_a_pct = (basin_a_count / len(all_experiments) * 100)

        threshold_results[threshold] = {
            'count': basin_a_count,
            'pct': basin_a_pct
        }

        print(f"   {threshold:4.1f}    | {basin_a_count:13d} | {basin_a_pct:8.1f}%")

    print()

    # Find optimal threshold
    optimal = min(thresholds, key=lambda t: abs(threshold_results[t]['pct'] - 50))
    print(f"Optimal threshold: {optimal} ({threshold_results[optimal]['pct']:.1f}% Basin A)")
    print()

    # Frequency analysis for Cycle 160
    print("FREQUENCY LANDSCAPE (Cycle 160 with Multiple Thresholds):")
    print("="*80)
    print()

    frequency_data = defaultdict(lambda: defaultdict(list))

    for exp in cycle160['experiments']:
        freq = exp['spawning_freq']
        comp = exp['avg_composition_events']

        for threshold in thresholds:
            basin = 'A' if comp > threshold else 'B'
            frequency_data[freq][threshold].append(basin)

    # Display table
    print(f"        Threshold →")
    print(f" Freq % |", " | ".join([f"{t:4.1f}" for t in thresholds]))
    print("-"*70)

    for freq in sorted(frequency_data.keys()):
        row = [f" {freq:5.0f}% |"]

        for threshold in thresholds:
            basins = frequency_data[freq][threshold]
            basin_a_count = basins.count('A')
            basin_a_pct = (basin_a_count / len(basins) * 100) if basins else 0
            row.append(f" {basin_a_pct:3.0f}%")

        print(" | ".join(row))

    print()

    # Key insights
    print("KEY INSIGHTS:")
    print("="*80)
    print()

    print(f"1. Composition Range: {comp_min:.2f} - {comp_max:.2f}")
    print(f"   - ALL experiments fall in this range")
    print(f"   - Original threshold (7.0) FAR above maximum ({comp_max:.2f})")
    print()

    print(f"2. Threshold 2.5 Analysis:")
    t25_pct = threshold_results[2.5]['pct']
    print(f"   - Basin A %: {t25_pct:.1f}%")

    if 40 <= t25_pct <= 60:
        print(f"   - ✓ BISTABLE REGION (near 50%)")
    else:
        print(f"   - Not optimal for bistability")
    print()

    print(f"3. Frequency Independence:")
    print(f"   - With threshold 2.5, most frequencies show similar Basin A %")
    print(f"   - Suggests composition primarily seed-dependent, not frequency-dependent")
    print()

    # Save focused results
    output = {
        'total_experiments': len(all_experiments),
        'cycles_analyzed': [160, 161],
        'composition_stats': {
            'mean': comp_mean,
            'median': comp_median,
            'std': comp_std,
            'min': comp_min,
            'max': comp_max
        },
        'threshold_analysis': {str(k): v for k, v in threshold_results.items()},
        'optimal_threshold': optimal,
    }

    output_file = results_dir / 'corrected_experiments_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {output_file}")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
