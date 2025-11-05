#!/usr/bin/env python3
"""
CYCLE 188 ANALYSIS: Memory Effects Validation

Purpose: Validate Extension 4 (Part B) predictions from C188 results

Predictions to Test:
  1. Spawn success ranking: Long > Medium > Short > None
  2. Burstiness ranking: None > Short > Medium > Long
  3. Negative correlation between memory window and burstiness

Validation Criteria:
  ✅ VALIDATED: Both rankings correct AND correlation r < -0.7
  ⚠️  PARTIAL: One ranking correct OR correlation significant
  ❌ REJECTED: Neither ranking nor correlation validates

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


# Load C188 results
RESULTS_PATH = Path(__file__).parent / "results" / "cycle188_memory_effects.json"


def load_results() -> dict:
    """Load C188 experimental results."""
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Results not found: {RESULTS_PATH}")

    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


def validate_spawn_success_ranking(data: dict) -> Tuple[str, dict]:
    """
    Validate spawn success ranking prediction.

    Prediction: Long > Medium > Short > None

    Returns:
        (status, metrics)
    """
    # Extract spawn success by memory condition
    results_by_condition = {}

    for condition_name in ['none', 'short', 'medium', 'long']:
        cond_results = [r for r in data['experiments'] if r['memory_condition'] == condition_name]
        spawn_successes = [r['spawn_success_rate'] for r in cond_results]

        results_by_condition[condition_name] = {
            'mean': float(np.mean(spawn_successes)),
            'std': float(np.std(spawn_successes)),
            'values': spawn_successes,
        }

    # Check ranking
    ranking = sorted(results_by_condition.keys(), key=lambda k: results_by_condition[k]['mean'], reverse=True)
    expected_ranking = ['long', 'medium', 'short', 'none']

    ranking_correct = (ranking == expected_ranking)

    # Statistical tests (pairwise comparisons)
    t_long_medium, p_long_medium = stats.ttest_ind(
        results_by_condition['long']['values'],
        results_by_condition['medium']['values']
    )

    t_medium_short, p_medium_short = stats.ttest_ind(
        results_by_condition['medium']['values'],
        results_by_condition['short']['values']
    )

    t_short_none, p_short_none = stats.ttest_ind(
        results_by_condition['short']['values'],
        results_by_condition['none']['values']
    )

    # Determine status
    if ranking_correct and all(p < 0.05 for p in [p_long_medium, p_medium_short, p_short_none]):
        status = "VALIDATED"
    elif ranking_correct:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'results_by_condition': results_by_condition,
        'ranking': ranking,
        'expected_ranking': expected_ranking,
        'ranking_correct': ranking_correct,
        'p_long_vs_medium': float(p_long_medium),
        'p_medium_vs_short': float(p_medium_short),
        'p_short_vs_none': float(p_short_none),
    }

    return status, metrics


def validate_burstiness_ranking(data: dict) -> Tuple[str, dict]:
    """
    Validate burstiness ranking prediction.

    Prediction: None > Short > Medium > Long (higher memory → lower burstiness)

    Returns:
        (status, metrics)
    """
    # Extract burstiness by memory condition
    results_by_condition = {}

    for condition_name in ['none', 'short', 'medium', 'long']:
        cond_results = [r for r in data['experiments'] if r['memory_condition'] == condition_name]
        burstiness_values = [r['burstiness'] for r in cond_results]

        results_by_condition[condition_name] = {
            'mean': float(np.mean(burstiness_values)),
            'std': float(np.std(burstiness_values)),
            'values': burstiness_values,
        }

    # Check ranking
    ranking = sorted(results_by_condition.keys(), key=lambda k: results_by_condition[k]['mean'], reverse=True)
    expected_ranking = ['none', 'short', 'medium', 'long']

    ranking_correct = (ranking == expected_ranking)

    # Statistical tests
    t_none_short, p_none_short = stats.ttest_ind(
        results_by_condition['none']['values'],
        results_by_condition['short']['values']
    )

    t_short_medium, p_short_medium = stats.ttest_ind(
        results_by_condition['short']['values'],
        results_by_condition['medium']['values']
    )

    t_medium_long, p_medium_long = stats.ttest_ind(
        results_by_condition['medium']['values'],
        results_by_condition['long']['values']
    )

    # Determine status
    if ranking_correct and all(p < 0.05 for p in [p_none_short, p_short_medium, p_medium_long]):
        status = "VALIDATED"
    elif ranking_correct:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'results_by_condition': results_by_condition,
        'ranking': ranking,
        'expected_ranking': expected_ranking,
        'ranking_correct': ranking_correct,
        'p_none_vs_short': float(p_none_short),
        'p_short_vs_medium': float(p_short_medium),
        'p_medium_vs_long': float(p_medium_long),
    }

    return status, metrics


def validate_memory_burstiness_correlation(data: dict) -> Tuple[str, dict]:
    """
    Validate memory-burstiness correlation prediction.

    Prediction: Negative correlation r < -0.7 (longer memory → lower burstiness)

    Returns:
        (status, metrics)
    """
    # Extract memory window and burstiness for each experiment
    # Map conditions to numeric values
    condition_to_window = {
        'none': 0,
        'short': 100,
        'medium': 500,
        'long': 1000,
    }

    memory_windows = []
    burstiness_values = []

    for exp in data['experiments']:
        condition = exp['memory_condition']
        window = condition_to_window[condition]
        burstiness = exp['burstiness']

        memory_windows.append(window)
        burstiness_values.append(burstiness)

    # Calculate Pearson correlation
    r, p_value = stats.pearsonr(memory_windows, burstiness_values)

    # Determine status
    if r < -0.7 and p_value < 0.05:
        status = "VALIDATED"
    elif r < -0.5 and p_value < 0.05:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'correlation_r': float(r),
        'p_value': float(p_value),
        'n_points': len(memory_windows),
        'memory_range': [min(memory_windows), max(memory_windows)],
        'burstiness_range': [float(min(burstiness_values)), float(max(burstiness_values))],
    }

    return status, metrics


def generate_validation_report(data: dict) -> dict:
    """
    Run all validations and generate composite report.

    Returns:
        Complete validation report with scores
    """
    print("=" * 80)
    print("CYCLE 188: MEMORY EFFECTS ANALYSIS")
    print("=" * 80)
    print()

    validations = {}
    scores = []

    # Validation 1: Spawn success ranking
    print("VALIDATION 1: Spawn Success Ranking")
    print("-" * 80)
    status_1, metrics_1 = validate_spawn_success_ranking(data)
    validations['spawn_success_ranking'] = {
        'name': 'Spawn Success Ranking',
        'status': status_1,
        'metrics': metrics_1,
    }

    print("Ranking:")
    for i, condition in enumerate(metrics_1['ranking']):
        mean = metrics_1['results_by_condition'][condition]['mean']
        print(f"  {i+1}. {condition}: {mean:.2%}")

    print(f"Expected: {metrics_1['expected_ranking']}")
    print(f"Actual: {metrics_1['ranking']}")
    print(f"Status: {status_1}")

    if status_1 == "VALIDATED":
        scores.append(2.0)
    elif status_1 == "PARTIAL":
        scores.append(1.0)
    else:
        scores.append(0.0)

    print()

    # Validation 2: Burstiness ranking
    print("VALIDATION 2: Burstiness Ranking")
    print("-" * 80)
    status_2, metrics_2 = validate_burstiness_ranking(data)
    validations['burstiness_ranking'] = {
        'name': 'Burstiness Ranking',
        'status': status_2,
        'metrics': metrics_2,
    }

    print("Ranking:")
    for i, condition in enumerate(metrics_2['ranking']):
        mean = metrics_2['results_by_condition'][condition]['mean']
        print(f"  {i+1}. {condition}: B = {mean:.3f}")

    print(f"Expected: {metrics_2['expected_ranking']}")
    print(f"Actual: {metrics_2['ranking']}")
    print(f"Status: {status_2}")

    if status_2 == "VALIDATED":
        scores.append(2.0)
    elif status_2 == "PARTIAL":
        scores.append(1.0)
    else:
        scores.append(0.0)

    print()

    # Validation 3: Memory-burstiness correlation
    print("VALIDATION 3: Memory-Burstiness Correlation")
    print("-" * 80)
    status_3, metrics_3 = validate_memory_burstiness_correlation(data)
    validations['memory_burstiness_correlation'] = {
        'name': 'Memory-Burstiness Correlation',
        'status': status_3,
        'metrics': metrics_3,
    }

    print(f"Pearson r: {metrics_3['correlation_r']:.3f}")
    print(f"p-value: {metrics_3['p_value']:.4f}")
    print(f"Status: {status_3}")

    if status_3 == "VALIDATED":
        scores.append(1.0)
    elif status_3 == "PARTIAL":
        scores.append(0.5)
    else:
        scores.append(0.0)

    print()

    # Composite score
    total_score = sum(scores)
    max_score = 5.0  # 2 + 2 + 1

    print("=" * 80)
    print("COMPOSITE VALIDATION SCORE")
    print("=" * 80)
    print()
    print(f"Total Score: {total_score:.1f} / {max_score:.1f}")
    print()

    # Interpretation
    if total_score >= 4.0:
        interpretation = "STRONGLY VALIDATED"
        confidence = "High"
    elif total_score >= 2.5:
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
    Create 4-panel figure showing C188 results.

    Panels:
      1. Spawn success by memory condition (bar chart)
      2. Burstiness by memory condition (bar chart)
      3. Memory-burstiness correlation (scatter)
      4. Composite validation score
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Cycle 188: Memory Effects Validation', fontsize=16, fontweight='bold')

    # Panel 1: Spawn success by condition
    ax = axes[0, 0]
    spawn_metrics = validation_report['validations']['spawn_success_ranking']['metrics']
    conditions = ['none', 'short', 'medium', 'long']
    means = [spawn_metrics['results_by_condition'][c]['mean'] for c in conditions]
    stds = [spawn_metrics['results_by_condition'][c]['std'] for c in conditions]

    ax.bar(range(4), means, yerr=stds, capsize=5, alpha=0.7,
           color=['red', 'orange', 'yellow', 'green'])
    ax.set_xticks(range(4))
    ax.set_xticklabels(['None', 'Short', 'Medium', 'Long'], rotation=45)
    ax.set_ylabel('Spawn Success Rate')
    ax.set_title(f'Spawn Success by Memory Condition\n{spawn_metrics["status"]}')
    ax.grid(axis='y', alpha=0.3)

    # Panel 2: Burstiness by condition
    ax = axes[0, 1]
    burst_metrics = validation_report['validations']['burstiness_ranking']['metrics']
    means = [burst_metrics['results_by_condition'][c]['mean'] for c in conditions]
    stds = [burst_metrics['results_by_condition'][c]['std'] for c in conditions]

    ax.bar(range(4), means, yerr=stds, capsize=5, alpha=0.7,
           color=['red', 'orange', 'yellow', 'green'])
    ax.set_xticks(range(4))
    ax.set_xticklabels(['None', 'Short', 'Medium', 'Long'], rotation=45)
    ax.set_ylabel('Burstiness Coefficient B')
    ax.set_title(f'Burstiness by Memory Condition\n{burst_metrics["status"]}')
    ax.grid(axis='y', alpha=0.3)

    # Panel 3: Memory-burstiness correlation
    ax = axes[1, 0]
    corr_metrics = validation_report['validations']['memory_burstiness_correlation']['metrics']

    # Map conditions to colors
    condition_to_window = {'none': 0, 'short': 100, 'medium': 500, 'long': 1000}
    colors_map = {'none': 'red', 'short': 'orange', 'medium': 'yellow', 'long': 'green'}

    memory_windows = []
    burstiness_values = []
    colors = []

    for exp in data['experiments']:
        condition = exp['memory_condition']
        window = condition_to_window[condition]
        burstiness = exp['burstiness']

        memory_windows.append(window)
        burstiness_values.append(burstiness)
        colors.append(colors_map[condition])

    ax.scatter(memory_windows, burstiness_values, c=colors, alpha=0.6, edgecolor='black')

    # Fit line
    z = np.polyfit(memory_windows, burstiness_values, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(memory_windows), max(memory_windows), 100)
    ax.plot(x_line, p(x_line), 'k--', label=f'r = {corr_metrics["correlation_r"]:.3f}')

    ax.set_xlabel('Memory Window (cycles)')
    ax.set_ylabel('Burstiness Coefficient B')
    ax.set_title(f'Memory vs Burstiness\n{validation_report["validations"]["memory_burstiness_correlation"]["status"]}')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel 4: Composite score
    ax = axes[1, 1]
    validations_list = ['Spawn Ranking', 'Burst Ranking', 'Correlation']

    scores_list = []
    for val_key in ['spawn_success_ranking', 'burstiness_ranking', 'memory_burstiness_correlation']:
        val = validation_report['validations'][val_key]
        if val['status'] == 'VALIDATED':
            score = 2.0 if val_key != 'memory_burstiness_correlation' else 1.0
        elif val['status'] == 'PARTIAL':
            score = 1.0 if val_key != 'memory_burstiness_correlation' else 0.5
        else:
            score = 0.0
        scores_list.append(score)

    colors = ['green' if s >= 1.5 else 'yellow' if s >= 0.5 else 'red' for s in scores_list]
    ax.barh(validations_list, scores_list, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Score')
    ax.set_xlim(0, 2.0)
    ax.set_title(f'Composite Score: {validation_report["composite_score"]:.1f}/{validation_report["max_score"]:.1f}\n{validation_report["interpretation"]}')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_path = Path(__file__).parent.parent / "data" / "figures" / "c188_memory_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    print()


def main():
    """Execute C188 validation analysis."""
    # Load results
    data = load_results()

    # Generate validation report
    report = generate_validation_report(data)

    # Create figure
    create_validation_figure(data, report)

    # Save report JSON
    report_path = Path(__file__).parent / "results" / "cycle188_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Validation report saved: {report_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
