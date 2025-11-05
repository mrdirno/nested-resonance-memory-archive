#!/usr/bin/env python3
"""
CYCLE 187 ANALYSIS: Network Structure Effects Validation

Purpose: Validate Extension 1 predictions from C187 results

Predictions to Test:
  1. Spawn success ranking: Lattice > Random > Scale-Free
  2. Negative correlation between degree heterogeneity and spawn success
  3. Hub depletion in scale-free networks (degree-stratified analysis)

Validation Criteria:
  ✅ VALIDATED: Ranking correct AND correlation r < -0.7
  ⚠️  PARTIAL: Ranking correct OR correlation significant
  ❌ REJECTED: Neither ranking nor correlation validates

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 996
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple


# Load C187 results
RESULTS_PATH = Path(__file__).parent / "results" / "cycle187_network_structure_effects.json"


def load_results() -> dict:
    """Load C187 experimental results."""
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Results not found: {RESULTS_PATH}")

    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


def validate_ranking(data: dict) -> Tuple[str, dict]:
    """
    Validate spawn success ranking prediction.

    Prediction: Lattice > Random > Scale-Free

    Returns:
        (status, metrics)
    """
    # Extract spawn success by topology
    results_by_topology = {}
    for topology in ['scale_free', 'random', 'lattice']:
        topo_results = [r for r in data['experiments'] if r['topology'] == topology]
        spawn_successes = [r['spawn_success_rate'] for r in topo_results]

        results_by_topology[topology] = {
            'mean': float(np.mean(spawn_successes)),
            'std': float(np.std(spawn_successes)),
            'values': spawn_successes,
        }

    # Check ranking
    sf_mean = results_by_topology['scale_free']['mean']
    rand_mean = results_by_topology['random']['mean']
    lattice_mean = results_by_topology['lattice']['mean']

    ranking_correct = (lattice_mean > rand_mean > sf_mean)

    # Statistical significance (t-tests)
    # Test 1: Random > Scale-Free
    t_rand_sf, p_rand_sf = stats.ttest_ind(
        results_by_topology['random']['values'],
        results_by_topology['scale_free']['values']
    )

    # Test 2: Lattice > Random
    t_lattice_rand, p_lattice_rand = stats.ttest_ind(
        results_by_topology['lattice']['values'],
        results_by_topology['random']['values']
    )

    # Determine status
    if ranking_correct and p_rand_sf < 0.05 and p_lattice_rand < 0.05:
        status = "VALIDATED"
    elif ranking_correct or (p_rand_sf < 0.05):
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'scale_free_mean': sf_mean,
        'random_mean': rand_mean,
        'lattice_mean': lattice_mean,
        'ranking_correct': ranking_correct,
        't_random_vs_scalefree': float(t_rand_sf),
        'p_random_vs_scalefree': float(p_rand_sf),
        't_lattice_vs_random': float(t_lattice_rand),
        'p_lattice_vs_random': float(p_lattice_rand),
        'results_by_topology': results_by_topology,
    }

    return status, metrics


def validate_heterogeneity_correlation(data: dict) -> Tuple[str, dict]:
    """
    Validate degree heterogeneity correlation prediction.

    Prediction: Negative correlation r < -0.7 (higher heterogeneity → lower spawn success)

    Returns:
        (status, metrics)
    """
    # Extract heterogeneity and spawn success for each experiment
    heterogeneities = []
    spawn_successes = []

    for exp in data['experiments']:
        heterogeneity = exp['network_metrics']['degree_heterogeneity']
        spawn_success = exp['spawn_success_rate']

        heterogeneities.append(heterogeneity)
        spawn_successes.append(spawn_success)

    # Calculate Pearson correlation
    r, p_value = stats.pearsonr(heterogeneities, spawn_successes)

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
        'n_points': len(heterogeneities),
        'heterogeneity_range': [float(min(heterogeneities)), float(max(heterogeneities))],
        'spawn_success_range': [float(min(spawn_successes)), float(max(spawn_successes))],
    }

    return status, metrics


def validate_hub_depletion(data: dict) -> Tuple[str, dict]:
    """
    Validate hub depletion hypothesis (degree-stratified analysis).

    Prediction: Low-degree agents > high-degree agents in spawn success

    Returns:
        (status, metrics)
    """
    # Extract stratified results (only from scale-free networks)
    sf_results = [r for r in data['experiments'] if r['topology'] == 'scale_free']

    # Aggregate across all scale-free experiments
    low_degree_success = []
    high_degree_success = []

    for exp in sf_results:
        stratified = exp['stratified_spawn_success']['degree_bins']

        # Bin 0 = low degree, Bin 2 = high degree
        if '0' in stratified and '2' in stratified:
            low_degree_success.append(stratified['0']['spawn_success_rate'])
            high_degree_success.append(stratified['2']['spawn_success_rate'])

    if len(low_degree_success) == 0:
        return "REJECTED", {'error': 'No stratified data available'}

    # Calculate means
    mean_low = np.mean(low_degree_success)
    mean_high = np.mean(high_degree_success)

    # Test significance
    t_stat, p_value = stats.ttest_ind(low_degree_success, high_degree_success)

    # Determine status
    if mean_low > mean_high and p_value < 0.05:
        status = "VALIDATED"
    elif mean_low > mean_high:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    metrics = {
        'low_degree_mean': float(mean_low),
        'high_degree_mean': float(mean_high),
        'difference': float(mean_low - mean_high),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'n_experiments': len(low_degree_success),
    }

    return status, metrics


def generate_validation_report(data: dict) -> dict:
    """
    Run all validations and generate composite report.

    Returns:
        Complete validation report with scores
    """
    print("=" * 80)
    print("CYCLE 187: NETWORK STRUCTURE EFFECTS ANALYSIS")
    print("=" * 80)
    print()

    validations = {}
    scores = []

    # Validation 1: Ranking
    print("VALIDATION 1: Spawn Success Ranking")
    print("-" * 80)
    status_1, metrics_1 = validate_ranking(data)
    validations['ranking'] = {
        'name': 'Spawn Success Ranking',
        'status': status_1,
        'metrics': metrics_1,
    }

    print(f"Scale-Free: {metrics_1['scale_free_mean']:.2%}")
    print(f"Random: {metrics_1['random_mean']:.2%}")
    print(f"Lattice: {metrics_1['lattice_mean']:.2%}")
    print(f"Ranking: {'Lattice > Random > Scale-Free' if metrics_1['ranking_correct'] else 'INCORRECT'}")
    print(f"Status: {status_1}")

    if status_1 == "VALIDATED":
        scores.append(2.0)
    elif status_1 == "PARTIAL":
        scores.append(1.0)
    else:
        scores.append(0.0)

    print()

    # Validation 2: Heterogeneity correlation
    print("VALIDATION 2: Degree Heterogeneity Correlation")
    print("-" * 80)
    status_2, metrics_2 = validate_heterogeneity_correlation(data)
    validations['heterogeneity_correlation'] = {
        'name': 'Degree Heterogeneity Correlation',
        'status': status_2,
        'metrics': metrics_2,
    }

    print(f"Pearson r: {metrics_2['correlation_r']:.3f}")
    print(f"p-value: {metrics_2['p_value']:.4f}")
    print(f"Status: {status_2}")

    if status_2 == "VALIDATED":
        scores.append(1.0)
    elif status_2 == "PARTIAL":
        scores.append(0.5)
    else:
        scores.append(0.0)

    print()

    # Validation 3: Hub depletion
    print("VALIDATION 3: Hub Depletion (Scale-Free Networks)")
    print("-" * 80)
    status_3, metrics_3 = validate_hub_depletion(data)
    validations['hub_depletion'] = {
        'name': 'Hub Depletion',
        'status': status_3,
        'metrics': metrics_3,
    }

    if 'error' not in metrics_3:
        print(f"Low-degree spawn success: {metrics_3['low_degree_mean']:.2%}")
        print(f"High-degree spawn success: {metrics_3['high_degree_mean']:.2%}")
        print(f"Difference: {metrics_3['difference']:.2%}")
        print(f"p-value: {metrics_3['p_value']:.4f}")
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
    max_score = 4.0  # 2 + 1 + 1

    print("=" * 80)
    print("COMPOSITE VALIDATION SCORE")
    print("=" * 80)
    print()
    print(f"Total Score: {total_score:.1f} / {max_score:.1f}")
    print()

    # Interpretation
    if total_score >= 3.5:
        interpretation = "STRONGLY VALIDATED"
        confidence = "High"
    elif total_score >= 2.0:
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
    Create 4-panel figure showing C187 results.

    Panels:
      1. Spawn success by topology (bar chart)
      2. Heterogeneity vs spawn success (scatter)
      3. Degree-stratified spawn success (scale-free)
      4. Composite validation score
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Cycle 187: Network Structure Effects Validation', fontsize=16, fontweight='bold')

    # Panel 1: Spawn success by topology
    ax = axes[0, 0]
    ranking_metrics = validation_report['validations']['ranking']['metrics']
    topologies = ['scale_free', 'random', 'lattice']
    means = [ranking_metrics['results_by_topology'][t]['mean'] for t in topologies]
    stds = [ranking_metrics['results_by_topology'][t]['std'] for t in topologies]

    bars = ax.bar(range(3), means, yerr=stds, capsize=5, alpha=0.7,
                  color=['red', 'blue', 'green'])
    ax.set_xticks(range(3))
    ax.set_xticklabels(['Scale-Free', 'Random', 'Lattice'], rotation=45)
    ax.set_ylabel('Spawn Success Rate')
    ax.set_title(f'Spawn Success by Topology\n{ranking_metrics["status"]}')
    ax.grid(axis='y', alpha=0.3)

    # Panel 2: Heterogeneity correlation
    ax = axes[0, 1]
    het_metrics = validation_report['validations']['heterogeneity_correlation']['metrics']

    heterogeneities = []
    spawn_successes = []
    colors_by_topology = {'scale_free': 'red', 'random': 'blue', 'lattice': 'green'}
    colors = []

    for exp in data['experiments']:
        heterogeneities.append(exp['network_metrics']['degree_heterogeneity'])
        spawn_successes.append(exp['spawn_success_rate'])
        colors.append(colors_by_topology[exp['topology']])

    ax.scatter(heterogeneities, spawn_successes, c=colors, alpha=0.6, edgecolor='black')

    # Fit line
    z = np.polyfit(heterogeneities, spawn_successes, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(heterogeneities), max(heterogeneities), 100)
    ax.plot(x_line, p(x_line), 'k--', label=f'r = {het_metrics["correlation_r"]:.3f}')

    ax.set_xlabel('Degree Heterogeneity (CV)')
    ax.set_ylabel('Spawn Success Rate')
    ax.set_title(f'Heterogeneity vs Spawn Success\n{validation_report["validations"]["heterogeneity_correlation"]["status"]}')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel 3: Degree-stratified spawn success
    ax = axes[1, 0]
    hub_metrics = validation_report['validations']['hub_depletion']['metrics']

    if 'error' not in hub_metrics:
        bins = ['Low Degree', 'High Degree']
        values = [hub_metrics['low_degree_mean'], hub_metrics['high_degree_mean']]

        ax.bar(bins, values, alpha=0.7, color=['green', 'red'])
        ax.set_ylabel('Spawn Success Rate')
        ax.set_title(f'Hub Depletion (Scale-Free)\n{validation_report["validations"]["hub_depletion"]["status"]}')
        ax.grid(axis='y', alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'No stratified data', ha='center', va='center')

    # Panel 4: Composite score
    ax = axes[1, 1]
    validations_list = ['Ranking', 'Heterogeneity', 'Hub Depletion']

    scores_list = []
    for val_key in ['ranking', 'heterogeneity_correlation', 'hub_depletion']:
        val = validation_report['validations'][val_key]
        if val['status'] == 'VALIDATED':
            score = 2.0 if val_key == 'ranking' else 1.0
        elif val['status'] == 'PARTIAL':
            score = 1.0 if val_key == 'ranking' else 0.5
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
    output_path = Path(__file__).parent.parent / "data" / "figures" / "c187_network_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    print()


def main():
    """Execute C187 validation analysis."""
    # Load results
    data = load_results()

    # Generate validation report
    report = generate_validation_report(data)

    # Create figure
    create_validation_figure(data, report)

    # Save report JSON
    report_path = Path(__file__).parent / "results" / "cycle187_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Validation report saved: {report_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
