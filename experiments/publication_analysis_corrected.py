#!/usr/bin/env python3
"""
PUBLICATION-QUALITY ANALYSIS: CORRECTED EXPERIMENTS (CYCLES 160-161)
Statistical analysis and visualization preparation for peer review

Context:
  Dual bugs discovered and corrected:
    1. Inverted spawn calculation (FIXED Cycle 160)
    2. Threshold miscalibration (CALIBRATED Cycle 161)

Purpose:
  Generate comprehensive statistical analysis suitable for publication:
    - Composition distribution analysis
    - Threshold sensitivity quantification
    - Seed-dependent variance characterization
    - Frequency-basin relationship (preliminary)
    - Comparison with broken implementation baseline

Output:
  Publication-ready statistics, tables, and data summaries
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats


def load_corrected_experiments():
    """Load only validated corrected experiments (Cycles 160-161)."""
    results_dir = Path(__file__).parent / 'results'

    experiments = []

    # Cycle 160: Spawn fix validation (15 experiments)
    with open(results_dir / 'cycle160_corrected_spawning.json', 'r') as f:
        data = json.load(f)
        for exp in data['experiments']:
            exp['cycle_id'] = 160
            exp['phase'] = 'spawn_validation'
            experiments.append(exp)

    # Cycle 161: Threshold calibration (3 experiments)
    with open(results_dir / 'cycle161_threshold_calibration.json', 'r') as f:
        data = json.load(f)
        for exp in data['experiments']:
            exp['cycle_id'] = 161
            exp['phase'] = 'threshold_calibration'
            experiments.append(exp)

    return experiments


def composition_distribution_analysis(experiments):
    """Analyze composition distribution with statistical rigor."""

    compositions = [exp['avg_composition_events'] for exp in experiments]

    # Descriptive statistics
    stats_dict = {
        'n': len(compositions),
        'mean': float(np.mean(compositions)),
        'median': float(np.median(compositions)),
        'std': float(np.std(compositions, ddof=1)),  # Sample std dev
        'sem': float(stats.sem(compositions)),  # Standard error of mean
        'min': float(min(compositions)),
        'max': float(max(compositions)),
        'range': float(max(compositions) - min(compositions)),
        'q25': float(np.percentile(compositions, 25)),
        'q75': float(np.percentile(compositions, 75)),
        'iqr': float(np.percentile(compositions, 75) - np.percentile(compositions, 25)),
    }

    # Confidence interval (95%)
    ci_95 = stats.t.interval(
        0.95,
        len(compositions) - 1,
        loc=stats_dict['mean'],
        scale=stats_dict['sem']
    )
    stats_dict['ci_95_lower'] = float(ci_95[0])
    stats_dict['ci_95_upper'] = float(ci_95[1])

    # Normality test (Shapiro-Wilk)
    shapiro_stat, shapiro_p = stats.shapiro(compositions)
    stats_dict['shapiro_w'] = float(shapiro_stat)
    stats_dict['shapiro_p'] = float(shapiro_p)
    stats_dict['is_normal'] = bool(shapiro_p > 0.05)  # Explicit bool conversion for JSON

    return stats_dict


def threshold_sensitivity_analysis(experiments):
    """Quantify basin classification sensitivity to threshold choice."""

    thresholds = [1.5, 2.0, 2.5, 3.0, 5.0, 7.0]

    sensitivity = {}

    for threshold in thresholds:
        basin_a_count = sum(
            1 for exp in experiments
            if exp['avg_composition_events'] > threshold
        )
        basin_a_pct = (basin_a_count / len(experiments) * 100)

        sensitivity[threshold] = {
            'basin_a_count': basin_a_count,
            'basin_b_count': len(experiments) - basin_a_count,
            'basin_a_pct': float(basin_a_pct),
            'basin_b_pct': float(100 - basin_a_pct),
        }

    # Find bistable region (40-60% Basin A)
    bistable_thresholds = [
        t for t in thresholds
        if 40 <= sensitivity[t]['basin_a_pct'] <= 60
    ]

    # Calculate threshold sensitivity metric (rate of change)
    threshold_sensitivities = []
    for i in range(len(thresholds) - 1):
        t1, t2 = thresholds[i], thresholds[i+1]
        pct1 = sensitivity[t1]['basin_a_pct']
        pct2 = sensitivity[t2]['basin_a_pct']
        delta_pct = abs(pct2 - pct1)
        delta_threshold = t2 - t1
        sensitivity_metric = delta_pct / delta_threshold
        threshold_sensitivities.append({
            'threshold_range': f"{t1}-{t2}",
            'sensitivity': float(sensitivity_metric),
        })

    return {
        'threshold_results': sensitivity,
        'bistable_thresholds': bistable_thresholds,
        'sensitivity_metrics': threshold_sensitivities,
    }


def seed_variance_analysis(experiments):
    """Characterize seed-dependent variation in basin selection."""

    # Group by frequency
    by_frequency = defaultdict(list)
    for exp in experiments:
        freq = exp['spawning_freq']
        by_frequency[freq].append({
            'seed': exp['seed'],
            'composition': exp['avg_composition_events'],
        })

    frequency_variance = {}

    for freq, exps in by_frequency.items():
        if len(exps) < 2:
            continue

        compositions = [e['composition'] for e in exps]

        # Variance metrics
        frequency_variance[freq] = {
            'n': len(compositions),
            'mean': float(np.mean(compositions)),
            'std': float(np.std(compositions, ddof=1)),
            'cv': float(np.std(compositions, ddof=1) / np.mean(compositions) * 100),  # Coefficient of variation
            'range': float(max(compositions) - min(compositions)),
        }

        # Basin classification variance (at threshold 2.5)
        basin_a_count = sum(1 for c in compositions if c > 2.5)
        frequency_variance[freq]['basin_a_pct'] = float(basin_a_count / len(compositions) * 100)

    # Overall seed variance (pooled across frequencies)
    all_freq_stds = [v['std'] for v in frequency_variance.values()]
    all_freq_cvs = [v['cv'] for v in frequency_variance.values()]

    pooled_variance = {
        'mean_within_freq_std': float(np.mean(all_freq_stds)),
        'mean_within_freq_cv': float(np.mean(all_freq_cvs)),
        'frequencies_tested': len(frequency_variance),
    }

    return {
        'by_frequency': frequency_variance,
        'pooled_statistics': pooled_variance,
    }


def frequency_landscape_preliminary(experiments):
    """Preliminary frequency-basin relationship (limited data)."""

    # Group by frequency
    by_frequency = defaultdict(lambda: {'basin_a': 0, 'basin_b': 0, 'compositions': []})

    for exp in experiments:
        freq = exp['spawning_freq']
        comp = exp['avg_composition_events']
        basin = 'A' if comp > 2.5 else 'B'  # Using calibrated threshold

        by_frequency[freq]['compositions'].append(comp)
        if basin == 'A':
            by_frequency[freq]['basin_a'] += 1
        else:
            by_frequency[freq]['basin_b'] += 1

    landscape = []
    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        total = data['basin_a'] + data['basin_b']

        landscape.append({
            'frequency': freq,
            'basin_a_count': data['basin_a'],
            'basin_b_count': data['basin_b'],
            'basin_a_pct': float(data['basin_a'] / total * 100),
            'n': total,
            'mean_composition': float(np.mean(data['compositions'])),
            'std_composition': float(np.std(data['compositions'], ddof=1)) if total > 1 else 0.0,
        })

    return landscape


def comparison_broken_vs_corrected():
    """Compare broken (Cycles 151-159) vs corrected (Cycles 160-161) implementations."""

    # Broken baseline from reclassification analysis
    results_dir = Path(__file__).parent / 'results'

    with open(results_dir / 'reclassification_analysis.json', 'r') as f:
        broken_data = json.load(f)

    with open(results_dir / 'corrected_experiments_analysis.json', 'r') as f:
        corrected_data = json.load(f)

    comparison = {
        'broken': {
            'n': broken_data['total_experiments'],
            'composition_mean': broken_data['composition_stats']['mean'],
            'composition_std': broken_data['composition_stats']['std'],
            'basin_a_pct_threshold_2_5': broken_data['threshold_results']['2.5']['basin_a_pct'],
        },
        'corrected': {
            'n': corrected_data['total_experiments'],
            'composition_mean': corrected_data['composition_stats']['mean'],
            'composition_std': corrected_data['composition_stats']['std'],
            'basin_a_pct_threshold_2_5': corrected_data['threshold_analysis']['2.5']['pct'],
        },
    }

    # Effect size (Cohen's d)
    pooled_std = np.sqrt(
        (comparison['broken']['composition_std']**2 + comparison['corrected']['composition_std']**2) / 2
    )
    cohens_d = (comparison['corrected']['composition_mean'] - comparison['broken']['composition_mean']) / pooled_std

    comparison['effect_size_cohens_d'] = float(cohens_d)
    comparison['interpretation'] = (
        'large' if abs(cohens_d) > 0.8 else
        'medium' if abs(cohens_d) > 0.5 else
        'small'
    )

    return comparison


def main():
    """Generate publication-quality analysis."""

    print("="*80)
    print("PUBLICATION-QUALITY ANALYSIS: CORRECTED EXPERIMENTS (CYCLES 160-161)")
    print("="*80)
    print()

    # Load data
    experiments = load_corrected_experiments()
    print(f"Loaded {len(experiments)} corrected experiments")
    print(f"  - Cycle 160 (spawn validation): {sum(1 for e in experiments if e['cycle_id'] == 160)}")
    print(f"  - Cycle 161 (threshold calibration): {sum(1 for e in experiments if e['cycle_id'] == 161)}")
    print()

    # Composition distribution
    print("1. COMPOSITION DISTRIBUTION ANALYSIS")
    print("="*80)
    comp_stats = composition_distribution_analysis(experiments)
    print(f"  N: {comp_stats['n']}")
    print(f"  Mean: {comp_stats['mean']:.3f} ± {comp_stats['sem']:.3f} (SEM)")
    print(f"  95% CI: [{comp_stats['ci_95_lower']:.3f}, {comp_stats['ci_95_upper']:.3f}]")
    print(f"  Median: {comp_stats['median']:.3f}")
    print(f"  Range: [{comp_stats['min']:.3f}, {comp_stats['max']:.3f}]")
    print(f"  IQR: [{comp_stats['q25']:.3f}, {comp_stats['q75']:.3f}]")
    print(f"  Std Dev: {comp_stats['std']:.3f}")
    print(f"  Normality: {'Normal' if comp_stats['is_normal'] else 'Non-normal'} (Shapiro-Wilk p={comp_stats['shapiro_p']:.4f})")
    print()

    # Threshold sensitivity
    print("2. THRESHOLD SENSITIVITY ANALYSIS")
    print("="*80)
    threshold_analysis = threshold_sensitivity_analysis(experiments)
    print("  Threshold | Basin A % | Classification")
    print("  ----------+-----------+------------------")
    for threshold, results in sorted(threshold_analysis['threshold_results'].items()):
        classification = "Bistable" if 40 <= results['basin_a_pct'] <= 60 else "Unimodal"
        print(f"  {threshold:8.1f}  | {results['basin_a_pct']:8.1f}% | {classification}")
    print()
    print(f"  Bistable thresholds: {threshold_analysis['bistable_thresholds']}")
    print()

    # Seed variance
    print("3. SEED-DEPENDENT VARIANCE ANALYSIS")
    print("="*80)
    seed_analysis = seed_variance_analysis(experiments)
    print("  Frequency | N | Mean Comp | Std Dev | CV (%) | Basin A %")
    print("  ----------+---+-----------+---------+--------+----------")
    for freq, stats in sorted(seed_analysis['by_frequency'].items()):
        print(f"  {freq:8.0f}% | {stats['n']} | {stats['mean']:9.3f} | {stats['std']:7.3f} | {stats['cv']:5.1f}% | {stats['basin_a_pct']:8.1f}%")
    print()
    pooled = seed_analysis['pooled_statistics']
    print(f"  Pooled Statistics:")
    print(f"    Mean within-frequency std: {pooled['mean_within_freq_std']:.3f}")
    print(f"    Mean coefficient of variation: {pooled['mean_within_freq_cv']:.1f}%")
    print()

    # Frequency landscape (preliminary)
    print("4. FREQUENCY-BASIN RELATIONSHIP (PRELIMINARY)")
    print("="*80)
    landscape = frequency_landscape_preliminary(experiments)
    for freq_data in landscape:
        freq = freq_data['frequency']
        basin_a_pct = freq_data['basin_a_pct']
        n = freq_data['n']
        mean_comp = freq_data['mean_composition']
        print(f"  {freq:3.0f}%: Basin A = {basin_a_pct:5.1f}% ({freq_data['basin_a_count']}/{n}) | Mean Comp = {mean_comp:.3f}")
    print()

    # Comparison with broken implementation
    print("5. BROKEN VS CORRECTED COMPARISON")
    print("="*80)
    comparison = comparison_broken_vs_corrected()
    print("  Metric                  | Broken (151-159) | Corrected (160-161)")
    print("  ------------------------+------------------+--------------------")
    print(f"  N experiments           | {comparison['broken']['n']:16} | {comparison['corrected']['n']:18}")
    print(f"  Mean composition        | {comparison['broken']['composition_mean']:16.3f} | {comparison['corrected']['composition_mean']:18.3f}")
    print(f"  Std composition         | {comparison['broken']['composition_std']:16.3f} | {comparison['corrected']['composition_std']:18.3f}")
    print(f"  Basin A % (thresh 2.5)  | {comparison['broken']['basin_a_pct_threshold_2_5']:15.1f}% | {comparison['corrected']['basin_a_pct_threshold_2_5']:17.1f}%")
    print()
    print(f"  Effect size (Cohen's d): {comparison['effect_size_cohens_d']:.3f} ({comparison['interpretation']} effect)")
    print()

    # Save full results
    output = {
        'composition_distribution': comp_stats,
        'threshold_sensitivity': threshold_analysis,
        'seed_variance': seed_analysis,
        'frequency_landscape': landscape,
        'broken_vs_corrected': comparison,
    }

    results_dir = Path(__file__).parent / 'results'
    output_file = results_dir / 'publication_analysis_corrected.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Full results saved: {output_file}")
    print()
    print("="*80)
    print()


if __name__ == '__main__':
    main()
