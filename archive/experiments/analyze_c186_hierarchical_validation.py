#!/usr/bin/env python3
"""
CYCLE 186 ANALYSIS: Meta-Population Hierarchical Validation

Purpose: Validate 6 theoretical predictions from C186_THEORETICAL_PREDICTIONS.md

Validation Scorecard:
  1. Intra-population homeostasis preservation
  2. Inter-population variance reduction
  3. Meta-stability at swarm level
  4. Migration effectiveness
  5. Energy-population correlation
  6. No migration-induced collapse

Score: 0-12 points (6 predictions × 2 points max)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 994
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

# Load C186 results
RESULTS_PATH = Path(__file__).parent / "results" / "cycle186_metapopulation_hierarchical_validation.json"


def load_results() -> dict:
    """Load C186 experimental results."""
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Results not found: {RESULTS_PATH}")

    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


def validate_prediction_1(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 1: Intra-population homeostasis preservation.

    Success Criteria:
      ✅ VALIDATED: Basin A ≥ 90%
      ⚠️  PARTIAL: 70% ≤ Basin A < 90%
      ❌ REJECTED: Basin A < 70%

    Returns:
        (status, score, metrics)
    """
    # Extract all population basin classifications
    all_basins = []
    for experiment in data['experiments']:
        for pop_result in experiment['populations']:
            all_basins.append(pop_result['basin'])

    basin_a_count = sum(1 for b in all_basins if b == 'A')
    basin_a_pct = (basin_a_count / len(all_basins)) * 100

    # Determine status
    if basin_a_pct >= 90:
        status = "VALIDATED"
        score = 2.0
    elif basin_a_pct >= 70:
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'basin_a_percentage': basin_a_pct,
        'basin_a_count': basin_a_count,
        'total_populations': len(all_basins),
        'threshold_90': 90.0,
        'threshold_70': 70.0,
    }

    return status, score, metrics


def validate_prediction_2(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 2: Inter-population variance reduction.

    Success Criteria:
      ✅ VALIDATED: CV_between < 0.8 × CV_within
      ⚠️  PARTIAL: 0.8 × CV_within ≤ CV_between < 1.0 × CV_within
      ❌ REJECTED: CV_between ≥ CV_within

    Returns:
        (status, score, metrics)
    """
    # Extract aggregate analysis
    agg = data['aggregate_analysis']
    cv_between = agg['mean_between_population_cv']
    cv_within = agg['mean_within_population_cv']

    # Calculate ratio
    ratio = cv_between / cv_within if cv_within > 0 else float('inf')

    # Determine status
    if ratio < 0.8:
        status = "VALIDATED"
        score = 2.0
    elif ratio < 1.0:
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'cv_between': cv_between,
        'cv_within': cv_within,
        'ratio': ratio,
        'threshold_validated': 0.8,
        'threshold_partial': 1.0,
    }

    return status, score, metrics


def validate_prediction_3(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 3: Meta-stability (swarm-level regulation).

    Success Criteria:
      ✅ VALIDATED: CV_swarm < 0.5 × CV_population
      ⚠️  PARTIAL: 0.5 × CV_population ≤ CV_swarm < 0.8 × CV_population
      ❌ REJECTED: CV_swarm ≥ CV_population

    Returns:
        (status, score, metrics)
    """
    # Extract swarm-level CV
    cv_swarm_values = [exp['swarm_metrics']['cv_population'] for exp in data['experiments']]
    cv_swarm = np.mean(cv_swarm_values)

    # Extract population-level CV (mean within populations)
    cv_pop_values = []
    for experiment in data['experiments']:
        for pop_result in experiment['populations']:
            cv_pop_values.append(pop_result['cv_population'])

    cv_population = np.mean(cv_pop_values)

    # Calculate ratio
    ratio = cv_swarm / cv_population if cv_population > 0 else float('inf')

    # Determine status
    if ratio < 0.5:
        status = "VALIDATED"
        score = 2.0
    elif ratio < 0.8:
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'cv_swarm': cv_swarm,
        'cv_population': cv_population,
        'ratio': ratio,
        'threshold_validated': 0.5,
        'threshold_partial': 0.8,
    }

    return status, score, metrics


def validate_prediction_4(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 4: Migration effectiveness.

    Success Criteria:
      ✅ VALIDATED: 10 ≤ migrations ≤ 18
      ⚠️  PARTIAL: 5 ≤ migrations < 10 or 18 < migrations ≤ 25
      ❌ REJECTED: migrations < 5 or migrations > 25

    Returns:
        (status, score, metrics)
    """
    # Extract migration counts
    migration_counts = [exp['hierarchical_metrics']['total_migrations'] for exp in data['experiments']]
    mean_migrations = np.mean(migration_counts)
    std_migrations = np.std(migration_counts)

    # Determine status
    if 10 <= mean_migrations <= 18:
        status = "VALIDATED"
        score = 2.0
    elif (5 <= mean_migrations < 10) or (18 < mean_migrations <= 25):
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'mean_migrations': mean_migrations,
        'std_migrations': std_migrations,
        'migration_counts': migration_counts,
        'expected_min': 10,
        'expected_max': 18,
        'partial_min': 5,
        'partial_max': 25,
    }

    return status, score, metrics


def validate_prediction_5(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 5: Energy-population correlation.

    Success Criteria:
      ✅ VALIDATED: r ≥ 0.80
      ⚠️  PARTIAL: 0.60 ≤ r < 0.80
      ❌ REJECTED: r < 0.60

    Note: This requires time-series data (energy_trajectory, population_trajectory)
          which may not be in JSON. If unavailable, estimate from mean values.

    Returns:
        (status, score, metrics)
    """
    # Extract mean energy and mean population for each population
    energy_vals = []
    population_vals = []

    for experiment in data['experiments']:
        for pop_result in experiment['populations']:
            energy_vals.append(pop_result['mean_energy'])
            population_vals.append(pop_result['mean_population'])

    # Calculate Pearson correlation
    if len(energy_vals) > 2:
        r, p_value = stats.pearsonr(energy_vals, population_vals)
    else:
        r, p_value = 0.0, 1.0

    # Determine status
    if r >= 0.80:
        status = "VALIDATED"
        score = 2.0
    elif r >= 0.60:
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'correlation_r': r,
        'p_value': p_value,
        'n_points': len(energy_vals),
        'threshold_validated': 0.80,
        'threshold_partial': 0.60,
    }

    return status, score, metrics


def validate_prediction_6(data: dict) -> Tuple[str, float, dict]:
    """
    PREDICTION 6: No migration-induced collapse.

    Success Criteria:
      ✅ VALIDATED: Basin B ≤ 10%
      ⚠️  PARTIAL: 10% < Basin B ≤ 20%
      ❌ REJECTED: Basin B > 20%

    Returns:
        (status, score, metrics)
    """
    # Extract all population basin classifications
    all_basins = []
    for experiment in data['experiments']:
        for pop_result in experiment['populations']:
            all_basins.append(pop_result['basin'])

    basin_b_count = sum(1 for b in all_basins if b == 'B')
    basin_b_pct = (basin_b_count / len(all_basins)) * 100

    # Determine status
    if basin_b_pct <= 10:
        status = "VALIDATED"
        score = 2.0
    elif basin_b_pct <= 20:
        status = "PARTIAL"
        score = 1.0
    else:
        status = "REJECTED"
        score = 0.0

    metrics = {
        'basin_b_percentage': basin_b_pct,
        'basin_b_count': basin_b_count,
        'total_populations': len(all_basins),
        'threshold_validated': 10.0,
        'threshold_partial': 20.0,
    }

    return status, score, metrics


def generate_validation_report(data: dict) -> dict:
    """
    Run all 6 prediction validations and generate composite report.

    Returns:
        Complete validation report with scores and interpretations
    """
    print("=" * 80)
    print("CYCLE 186: HIERARCHICAL VALIDATION ANALYSIS")
    print("=" * 80)
    print()

    validations = {}

    # Prediction 1
    print("PREDICTION 1: Intra-population homeostasis preservation")
    print("-" * 80)
    status_1, score_1, metrics_1 = validate_prediction_1(data)
    validations['prediction_1'] = {
        'name': 'Intra-population homeostasis preservation',
        'status': status_1,
        'score': score_1,
        'metrics': metrics_1
    }
    print(f"Basin A: {metrics_1['basin_a_percentage']:.1f}% ({metrics_1['basin_a_count']}/{metrics_1['total_populations']})")
    print(f"Status: {status_1} (Score: {score_1:.1f}/2.0)")
    print()

    # Prediction 2
    print("PREDICTION 2: Inter-population variance reduction")
    print("-" * 80)
    status_2, score_2, metrics_2 = validate_prediction_2(data)
    validations['prediction_2'] = {
        'name': 'Inter-population variance reduction',
        'status': status_2,
        'score': score_2,
        'metrics': metrics_2
    }
    print(f"CV_between: {metrics_2['cv_between']:.2f}%")
    print(f"CV_within: {metrics_2['cv_within']:.2f}%")
    print(f"Ratio: {metrics_2['ratio']:.3f} (target: <0.8)")
    print(f"Status: {status_2} (Score: {score_2:.1f}/2.0)")
    print()

    # Prediction 3
    print("PREDICTION 3: Meta-stability (swarm-level regulation)")
    print("-" * 80)
    status_3, score_3, metrics_3 = validate_prediction_3(data)
    validations['prediction_3'] = {
        'name': 'Meta-stability',
        'status': status_3,
        'score': score_3,
        'metrics': metrics_3
    }
    print(f"CV_swarm: {metrics_3['cv_swarm']:.2f}%")
    print(f"CV_population (mean): {metrics_3['cv_population']:.2f}%")
    print(f"Ratio: {metrics_3['ratio']:.3f} (target: <0.5)")
    print(f"Status: {status_3} (Score: {score_3:.1f}/2.0)")
    print()

    # Prediction 4
    print("PREDICTION 4: Migration effectiveness")
    print("-" * 80)
    status_4, score_4, metrics_4 = validate_prediction_4(data)
    validations['prediction_4'] = {
        'name': 'Migration effectiveness',
        'status': status_4,
        'score': score_4,
        'metrics': metrics_4
    }
    print(f"Mean migrations: {metrics_4['mean_migrations']:.1f} ± {metrics_4['std_migrations']:.1f}")
    print(f"Expected range: {metrics_4['expected_min']}-{metrics_4['expected_max']}")
    print(f"Status: {status_4} (Score: {score_4:.1f}/2.0)")
    print()

    # Prediction 5
    print("PREDICTION 5: Energy-population correlation")
    print("-" * 80)
    status_5, score_5, metrics_5 = validate_prediction_5(data)
    validations['prediction_5'] = {
        'name': 'Energy-population correlation',
        'status': status_5,
        'score': score_5,
        'metrics': metrics_5
    }
    print(f"Pearson r: {metrics_5['correlation_r']:.3f}")
    print(f"p-value: {metrics_5['p_value']:.4f}")
    print(f"n points: {metrics_5['n_points']}")
    print(f"Status: {status_5} (Score: {score_5:.1f}/2.0)")
    print()

    # Prediction 6
    print("PREDICTION 6: No migration-induced collapse")
    print("-" * 80)
    status_6, score_6, metrics_6 = validate_prediction_6(data)
    validations['prediction_6'] = {
        'name': 'No migration-induced collapse',
        'status': status_6,
        'score': score_6,
        'metrics': metrics_6
    }
    print(f"Basin B: {metrics_6['basin_b_percentage']:.1f}% ({metrics_6['basin_b_count']}/{metrics_6['total_populations']})")
    print(f"Threshold: ≤{metrics_6['threshold_validated']:.1f}%")
    print(f"Status: {status_6} (Score: {score_6:.1f}/2.0)")
    print()

    # Composite score
    total_score = score_1 + score_2 + score_3 + score_4 + score_5 + score_6

    print("=" * 80)
    print("COMPOSITE VALIDATION SCORECARD")
    print("=" * 80)
    print()
    print(f"Total Score: {total_score:.1f} / 12.0")
    print()

    # Interpretation
    if total_score >= 10:
        interpretation = "STRONGLY VALIDATED"
        action = "Extension 2 ready for publication (Paper 4)"
        confidence = "High"
    elif total_score >= 7:
        interpretation = "PARTIALLY VALIDATED"
        action = "Refinement needed, proceed with caution"
        confidence = "Medium"
    elif total_score >= 4:
        interpretation = "WEAKLY SUPPORTED"
        action = "Major revision required"
        confidence = "Low"
    else:
        interpretation = "REJECTED"
        action = "Alternative mechanisms required"
        confidence = "None"

    print(f"Interpretation: {interpretation}")
    print(f"Confidence: {confidence}")
    print(f"Recommended Action: {action}")
    print()

    # Summary table
    print("PREDICTION SUMMARY:")
    print("-" * 80)
    print(f"{'Prediction':<50} {'Status':<12} {'Score':<6}")
    print("-" * 80)
    for i in range(1, 7):
        pred = validations[f'prediction_{i}']
        print(f"{pred['name']:<50} {pred['status']:<12} {pred['score']:.1f}/2.0")
    print("-" * 80)
    print(f"{'TOTAL':<50} {'':<12} {total_score:.1f}/12.0")
    print()

    return {
        'validations': validations,
        'composite_score': total_score,
        'interpretation': interpretation,
        'confidence': confidence,
        'action': action,
    }


def create_validation_figure(data: dict, validation_report: dict):
    """
    Create 6-panel figure showing validation results.

    Panels:
      1. Basin classification (bar chart)
      2. Variance decomposition (bar chart)
      3. Meta-stability (bar chart)
      4. Migration histogram
      5. Energy-population correlation (scatter)
      6. Score summary (bar chart)
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Cycle 186: Hierarchical Validation Results', fontsize=16, fontweight='bold')

    # Panel 1: Basin classification
    ax = axes[0, 0]
    pred_1 = validation_report['validations']['prediction_1']
    basin_a_pct = pred_1['metrics']['basin_a_percentage']
    basin_b_pct = 100 - basin_a_pct
    ax.bar(['Basin A', 'Basin B'], [basin_a_pct, basin_b_pct], color=['green', 'red'], alpha=0.7)
    ax.axhline(90, color='gray', linestyle='--', label='Threshold (90%)')
    ax.set_ylabel('Percentage (%)')
    ax.set_title(f'P1: Intra-Pop Homeostasis\n{pred_1["status"]} ({pred_1["score"]:.1f}/2.0)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Panel 2: Variance decomposition
    ax = axes[0, 1]
    pred_2 = validation_report['validations']['prediction_2']
    cv_between = pred_2['metrics']['cv_between']
    cv_within = pred_2['metrics']['cv_within']
    ax.bar(['Between-Pop', 'Within-Pop'], [cv_between, cv_within], color=['blue', 'orange'], alpha=0.7)
    ax.set_ylabel('Coefficient of Variation (%)')
    ax.set_title(f'P2: Variance Reduction\n{pred_2["status"]} ({pred_2["score"]:.1f}/2.0)')
    ax.grid(axis='y', alpha=0.3)

    # Panel 3: Meta-stability
    ax = axes[0, 2]
    pred_3 = validation_report['validations']['prediction_3']
    cv_swarm = pred_3['metrics']['cv_swarm']
    cv_pop = pred_3['metrics']['cv_population']
    ax.bar(['Swarm-Level', 'Population-Level'], [cv_swarm, cv_pop], color=['purple', 'orange'], alpha=0.7)
    ax.set_ylabel('Coefficient of Variation (%)')
    ax.set_title(f'P3: Meta-Stability\n{pred_3["status"]} ({pred_3["score"]:.1f}/2.0)')
    ax.grid(axis='y', alpha=0.3)

    # Panel 4: Migration histogram
    ax = axes[1, 0]
    pred_4 = validation_report['validations']['prediction_4']
    migration_counts = pred_4['metrics']['migration_counts']
    ax.hist(migration_counts, bins=10, color='teal', alpha=0.7, edgecolor='black')
    ax.axvline(pred_4['metrics']['expected_min'], color='green', linestyle='--', label='Expected range')
    ax.axvline(pred_4['metrics']['expected_max'], color='green', linestyle='--')
    ax.set_xlabel('Total Migrations')
    ax.set_ylabel('Frequency')
    ax.set_title(f'P4: Migration Effectiveness\n{pred_4["status"]} ({pred_4["score"]:.1f}/2.0)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Panel 5: Energy-population correlation
    ax = axes[1, 1]
    pred_5 = validation_report['validations']['prediction_5']

    # Extract energy and population values
    energy_vals = []
    population_vals = []
    for experiment in data['experiments']:
        for pop_result in experiment['populations']:
            energy_vals.append(pop_result['mean_energy'])
            population_vals.append(pop_result['mean_population'])

    ax.scatter(population_vals, energy_vals, alpha=0.5, color='red', edgecolor='black')

    # Fit line
    if len(energy_vals) > 2:
        z = np.polyfit(population_vals, energy_vals, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(population_vals), max(population_vals), 100)
        ax.plot(x_line, p(x_line), 'b--', label=f'r = {pred_5["metrics"]["correlation_r"]:.3f}')

    ax.set_xlabel('Mean Population Size')
    ax.set_ylabel('Mean Population Energy')
    ax.set_title(f'P5: Energy-Population Correlation\n{pred_5["status"]} ({pred_5["score"]:.1f}/2.0)')
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel 6: Score summary
    ax = axes[1, 2]
    predictions = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
    scores = [validation_report['validations'][f'prediction_{i}']['score'] for i in range(1, 7)]
    colors = ['green' if s == 2.0 else 'yellow' if s == 1.0 else 'red' for s in scores]
    ax.barh(predictions, scores, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Score')
    ax.set_xlim(0, 2.0)
    ax.set_title(f'Composite Score: {validation_report["composite_score"]:.1f}/12.0\n{validation_report["interpretation"]}')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_path = Path(__file__).parent.parent / "data" / "figures" / "c186_hierarchical_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    print()


def main():
    """Execute C186 validation analysis."""
    # Load results
    data = load_results()

    # Generate validation report
    report = generate_validation_report(data)

    # Create figure
    create_validation_figure(data, report)

    # Save report JSON
    report_path = Path(__file__).parent / "results" / "cycle186_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Validation report saved: {report_path}")
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
