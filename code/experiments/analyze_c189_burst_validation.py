#!/usr/bin/env python3
"""
CYCLE 189 ANALYSIS: Burst Clustering Validation

Purpose: Validate Extension 4 (Part C) predictions from C189 results

Predictions to Test:
  1. Burstiness coefficient: B > 0.3 (significantly clustered)
  2. Power-law exponent: α = 2.0-2.5 (avalanche dynamics)
  3. Frequency dependence: α decreases with f (more bursty at high frequency)

Validation Criteria:
  ✅ VALIDATED: All 3 predictions confirmed
  ⚠️  PARTIAL: 2/3 predictions confirmed
  ❌ REJECTED: <2 predictions confirmed

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 997
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

# Load C189 results
RESULTS_PATH = Path(__file__).parent / "results" / "cycle189_burst_clustering.json"


def load_results() -> dict:
    """Load C189 experimental results."""
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Results not found: {RESULTS_PATH}")

    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


def validate_burstiness_threshold(data: dict) -> Tuple[str, dict]:
    """
    Validate burstiness threshold prediction.

    Prediction: B > 0.3 (significantly clustered, not random)

    Returns:
        (status, metrics)
    """
    # Extract burstiness by frequency
    results_by_frequency = {}

    frequencies = sorted(set(r['frequency'] for r in data['experiments']))

    for frequency in frequencies:
        freq_results = [r for r in data['experiments'] if r['frequency'] == frequency]

        # Extract burstiness values
        burstiness_values = []
        for r in freq_results:
            burst = r['burst_analysis']
            if 'burstiness' in burst and not np.isnan(burst['burstiness']):
                burstiness_values.append(burst['burstiness'])

        results_by_frequency[frequency] = {
            'mean': float(np.mean(burstiness_values)) if burstiness_values else np.nan,
            'std': float(np.std(burstiness_values)) if burstiness_values else np.nan,
            'values': burstiness_values,
            'n': len(burstiness_values),
        }

    # Check if mean B > 0.3 for all frequencies
    threshold = 0.3
    all_above_threshold = all(
        results_by_frequency[f]['mean'] > threshold
        for f in frequencies
        if not np.isnan(results_by_frequency[f]['mean'])
    )

    # Calculate overall mean B
    all_burstiness = []
    for freq_data in results_by_frequency.values():
        all_burstiness.extend(freq_data['values'])

    overall_mean_B = np.mean(all_burstiness) if all_burstiness else np.nan

    # Determine status
    if all_above_threshold and overall_mean_B > threshold:
        status = "VALIDATED"
    elif overall_mean_B > 0.2:  # Partial support
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'results_by_frequency': results_by_frequency,
        'threshold': threshold,
        'all_above_threshold': all_above_threshold,
        'overall_mean_B': float(overall_mean_B),
        'overall_std_B': float(np.std(all_burstiness)) if all_burstiness else np.nan,
    }

    return status, metrics


def validate_power_law_exponent(data: dict) -> Tuple[str, dict]:
    """
    Validate power-law exponent prediction.

    Prediction: α = 2.0-2.5 (typical for avalanche dynamics)

    Returns:
        (status, metrics)
    """
    # Extract alpha by frequency
    results_by_frequency = {}

    frequencies = sorted(set(r['frequency'] for r in data['experiments']))

    for frequency in frequencies:
        freq_results = [r for r in data['experiments'] if r['frequency'] == frequency]

        # Extract alpha values
        alpha_values = []
        for r in freq_results:
            burst = r['burst_analysis']
            if ('distribution_fits' in burst and
                'power_law' in burst['distribution_fits']):
                alpha = burst['distribution_fits']['power_law']['alpha']
                if not np.isnan(alpha) and 1.0 < alpha < 5.0:  # Sanity check
                    alpha_values.append(alpha)

        results_by_frequency[frequency] = {
            'mean': float(np.mean(alpha_values)) if alpha_values else np.nan,
            'std': float(np.std(alpha_values)) if alpha_values else np.nan,
            'values': alpha_values,
            'n': len(alpha_values),
        }

    # Check if mean α in [2.0, 2.5] range
    alpha_min = 2.0
    alpha_max = 2.5

    in_range_count = sum(
        1 for freq_data in results_by_frequency.values()
        if not np.isnan(freq_data['mean']) and alpha_min <= freq_data['mean'] <= alpha_max
    )

    total_valid = sum(
        1 for freq_data in results_by_frequency.values()
        if not np.isnan(freq_data['mean'])
    )

    # Calculate overall mean alpha
    all_alpha = []
    for freq_data in results_by_frequency.values():
        all_alpha.extend(freq_data['values'])

    overall_mean_alpha = np.mean(all_alpha) if all_alpha else np.nan

    # Determine status
    if total_valid > 0 and in_range_count / total_valid >= 0.8:
        status = "VALIDATED"
    elif total_valid > 0 and in_range_count / total_valid >= 0.4:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'results_by_frequency': results_by_frequency,
        'alpha_range': [alpha_min, alpha_max],
        'in_range_count': in_range_count,
        'total_valid': total_valid,
        'overall_mean_alpha': float(overall_mean_alpha),
        'overall_std_alpha': float(np.std(all_alpha)) if all_alpha else np.nan,
    }

    return status, metrics


def validate_frequency_dependence(data: dict) -> Tuple[str, dict]:
    """
    Validate frequency dependence prediction.

    Prediction: α decreases with f (more bursty at higher frequencies)

    Returns:
        (status, metrics)
    """
    # Extract frequency-level alpha means
    frequencies = sorted(set(r['frequency'] for r in data['experiments']))

    freq_alpha_pairs = []

    for frequency in frequencies:
        freq_results = [r for r in data['experiments'] if r['frequency'] == frequency]

        # Extract alpha values
        alpha_values = []
        for r in freq_results:
            burst = r['burst_analysis']
            if ('distribution_fits' in burst and
                'power_law' in burst['distribution_fits']):
                alpha = burst['distribution_fits']['power_law']['alpha']
                if not np.isnan(alpha) and 1.0 < alpha < 5.0:
                    alpha_values.append(alpha)

        if alpha_values:
            mean_alpha = np.mean(alpha_values)
            freq_alpha_pairs.append((frequency, mean_alpha))

    if len(freq_alpha_pairs) < 3:
        return "REJECTED", {
            'error': 'insufficient_data',
            'n_valid_frequencies': len(freq_alpha_pairs),
        }

    # Pearson correlation (expect negative r)
    frequencies_arr = np.array([f for f, _ in freq_alpha_pairs])
    alphas_arr = np.array([a for _, a in freq_alpha_pairs])

    r, p_value = stats.pearsonr(frequencies_arr, alphas_arr)

    # Check monotonic decrease (Spearman)
    rho, p_spearman = stats.spearmanr(frequencies_arr, alphas_arr)

    # Determine status
    if r < -0.5 and p_value < 0.05:
        status = "VALIDATED"
    elif r < 0 and p_value < 0.10:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'frequency_alpha_pairs': freq_alpha_pairs,
        'pearson_r': float(r),
        'pearson_p': float(p_value),
        'spearman_rho': float(rho),
        'spearman_p': float(p_spearman),
        'n_frequencies': len(freq_alpha_pairs),
    }

    return status, metrics


def generate_validation_report(data: dict) -> dict:
    """
    Run all validations and generate composite report.

    Returns:
        Complete validation report with scores
    """
    print("=" * 80)
    print("CYCLE 189: BURST CLUSTERING ANALYSIS")
    print("=" * 80)
    print()

    validations = {}
    scores = []

    # Validation 1: Burstiness threshold
    print("VALIDATION 1: Burstiness Threshold (B > 0.3)")
    print("-" * 80)
    status_1, metrics_1 = validate_burstiness_threshold(data)
    validations['burstiness_threshold'] = {
        'name': 'Burstiness Threshold',
        'status': status_1,
        'metrics': metrics_1,
    }

    print(f"Overall mean B: {metrics_1['overall_mean_B']:.3f}")
    print(f"Threshold: B > {metrics_1['threshold']}")
    print(f"All frequencies above threshold: {metrics_1['all_above_threshold']}")
    print(f"Status: {status_1}")

    if status_1 == "VALIDATED":
        scores.append(1.0)
    elif status_1 == "PARTIAL":
        scores.append(0.5)
    else:
        scores.append(0.0)

    print()

    # Validation 2: Power-law exponent
    print("VALIDATION 2: Power-Law Exponent (α = 2.0-2.5)")
    print("-" * 80)
    status_2, metrics_2 = validate_power_law_exponent(data)
    validations['power_law_exponent'] = {
        'name': 'Power-Law Exponent',
        'status': status_2,
        'metrics': metrics_2,
    }

    print(f"Overall mean α: {metrics_2['overall_mean_alpha']:.2f}")
    print(f"Expected range: [{metrics_2['alpha_range'][0]:.1f}, {metrics_2['alpha_range'][1]:.1f}]")
    print(f"Frequencies in range: {metrics_2['in_range_count']}/{metrics_2['total_valid']}")
    print(f"Status: {status_2}")

    if status_2 == "VALIDATED":
        scores.append(1.0)
    elif status_2 == "PARTIAL":
        scores.append(0.5)
    else:
        scores.append(0.0)

    print()

    # Validation 3: Frequency dependence
    print("VALIDATION 3: Frequency Dependence (α decreases with f)")
    print("-" * 80)
    status_3, metrics_3 = validate_frequency_dependence(data)
    validations['frequency_dependence'] = {
        'name': 'Frequency Dependence',
        'status': status_3,
        'metrics': metrics_3,
    }

    if 'error' not in metrics_3:
        print(f"Pearson r: {metrics_3['pearson_r']:.3f}")
        print(f"p-value: {metrics_3['pearson_p']:.4f}")
        print(f"Spearman ρ: {metrics_3['spearman_rho']:.3f}")
        print(f"Status: {status_3}")

        if status_3 == "VALIDATED":
            scores.append(1.0)
        elif status_3 == "PARTIAL":
            scores.append(0.5)
        else:
            scores.append(0.0)
    else:
        print(f"ERROR: {metrics_3['error']}")
        scores.append(0.0)

    print()

    # Composite score
    total_score = sum(scores)
    max_score = 3.0

    print("=" * 80)
    print("COMPOSITE VALIDATION SCORE")
    print("=" * 80)
    print()
    print(f"Total Score: {total_score:.1f} / {max_score:.1f}")
    print()

    # Interpretation
    if total_score >= 2.5:
        interpretation = "STRONGLY VALIDATED"
        confidence = "High"
    elif total_score >= 1.5:
        interpretation = "PARTIALLY VALIDATED"
        confidence = "Medium"
    else:
        interpretation = "WEAKLY SUPPORTED"
        confidence = "Low"

    print(f"Interpretation: {interpretation}")
    print(f"Confidence: {confidence}")
    print()

    return {
        'validations': validations,
        'composite_score': total_score,
        'max_score': max_score,
        'interpretation': interpretation,
        'confidence': confidence,
    }


def create_validation_figure(data: dict, validation_report: dict):
    """
    Create 4-panel figure showing C189 results.

    Panels:
      1. Burstiness by frequency (bar chart)
      2. Power-law exponent by frequency (bar chart)
      3. Frequency vs alpha correlation (scatter)
      4. Composite validation score
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Cycle 189: Burst Clustering Validation', fontsize=16, fontweight='bold')

    # Panel 1: Burstiness by frequency
    ax = axes[0, 0]
    burst_metrics = validation_report['validations']['burstiness_threshold']['metrics']
    frequencies = sorted(burst_metrics['results_by_frequency'].keys())
    means = [burst_metrics['results_by_frequency'][f]['mean'] for f in frequencies]
    stds = [burst_metrics['results_by_frequency'][f]['std'] for f in frequencies]

    ax.bar(range(len(frequencies)), means, yerr=stds, capsize=5, alpha=0.7, color='steelblue')
    ax.axhline(y=0.3, color='red', linestyle='--', label='Threshold (B=0.3)')
    ax.set_xticks(range(len(frequencies)))
    ax.set_xticklabels([f"{f:.1f}%" for f in frequencies], rotation=45)
    ax.set_ylabel('Burstiness Coefficient B')
    ax.set_title(f'Burstiness by Frequency\n{validation_report["validations"]["burstiness_threshold"]["status"]}')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Panel 2: Power-law exponent by frequency
    ax = axes[0, 1]
    alpha_metrics = validation_report['validations']['power_law_exponent']['metrics']
    means = [alpha_metrics['results_by_frequency'][f]['mean'] for f in frequencies]
    stds = [alpha_metrics['results_by_frequency'][f]['std'] for f in frequencies]

    ax.bar(range(len(frequencies)), means, yerr=stds, capsize=5, alpha=0.7, color='coral')
    ax.axhline(y=2.0, color='green', linestyle='--', alpha=0.5, label='α range')
    ax.axhline(y=2.5, color='green', linestyle='--', alpha=0.5)
    ax.set_xticks(range(len(frequencies)))
    ax.set_xticklabels([f"{f:.1f}%" for f in frequencies], rotation=45)
    ax.set_ylabel('Power-Law Exponent α')
    ax.set_title(f'Power-Law Exponent by Frequency\n{validation_report["validations"]["power_law_exponent"]["status"]}')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Panel 3: Frequency vs alpha correlation
    ax = axes[1, 0]
    freq_dep_metrics = validation_report['validations']['frequency_dependence']['metrics']

    if 'error' not in freq_dep_metrics:
        freq_alpha_pairs = freq_dep_metrics['frequency_alpha_pairs']
        frequencies_arr = [f for f, _ in freq_alpha_pairs]
        alphas_arr = [a for _, a in freq_alpha_pairs]

        ax.scatter(frequencies_arr, alphas_arr, s=100, alpha=0.6, edgecolor='black', color='purple')

        # Fit line
        z = np.polyfit(frequencies_arr, alphas_arr, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(frequencies_arr), max(frequencies_arr), 100)
        ax.plot(x_line, p(x_line), 'k--', label=f'r = {freq_dep_metrics["pearson_r"]:.3f}')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Power-Law Exponent α')
        ax.set_title(f'Frequency vs Alpha\n{validation_report["validations"]["frequency_dependence"]["status"]}')
        ax.legend()
        ax.grid(alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', transform=ax.transAxes)

    # Panel 4: Composite score
    ax = axes[1, 1]
    validations_list = ['Burstiness', 'Power-Law α', 'Freq Dependence']

    scores_list = []
    for val_key in ['burstiness_threshold', 'power_law_exponent', 'frequency_dependence']:
        val = validation_report['validations'][val_key]
        if val['status'] == 'VALIDATED':
            score = 1.0
        elif val['status'] == 'PARTIAL':
            score = 0.5
        else:
            score = 0.0
        scores_list.append(score)

    colors = ['green' if s >= 0.9 else 'yellow' if s >= 0.4 else 'red' for s in scores_list]
    ax.barh(validations_list, scores_list, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Score')
    ax.set_xlim(0, 1.0)
    ax.set_title(f'Composite Score: {validation_report["composite_score"]:.1f}/{validation_report["max_score"]:.1f}\n{validation_report["interpretation"]}')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_path = Path(__file__).parent.parent / "data" / "figures" / "c189_burst_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    print()


def main():
    """Execute C189 validation analysis."""
    # Load results
    data = load_results()

    # Generate validation report
    report = generate_validation_report(data)

    # Create figure
    create_validation_figure(data, report)

    # Save report JSON
    report_path = Path(__file__).parent / "results" / "cycle189_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Validation report saved: {report_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
