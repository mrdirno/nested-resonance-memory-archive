#!/usr/bin/env python3
"""
CYCLE 186 V2 COMPARATIVE ANALYSIS

Purpose: Compare C186 V1 (f_intra=2.5%) vs. V2 (f_intra=5.0%) to test viability hypothesis

Hypothesis:
  - Metapopulations require f_intra ≥ 5.0% for bootstrap and sustainability
  - C186 V1: 100% Basin B collapse (below threshold)
  - C186 V2: Expected Basin A > 0%, ideally ≥50% (above threshold)

Validation:
  - Run same 6-prediction scorecard on C186 V2
  - Compare scorecard results: V1 (7.0/12.0) vs. V2 (TBD)
  - Compare Basin A: V1 (0.0%) vs. V2 (TBD)
  - Test viability hypothesis: If Basin A ≥ 50%, hypothesis validated

Output:
  - Comparative scorecard figure (V1 vs. V2 side-by-side)
  - Basin A improvement analysis
  - Parameter sensitivity insights

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1041
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

# Paths
RESULTS_V1_PATH = Path(__file__).parent / "results" / "cycle186_metapopulation_hierarchical_validation.json"
RESULTS_V2_PATH = Path(__file__).parent / "results" / "cycle186_v2_metapopulation_hierarchical_validation.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "figures"


def load_results(path: Path) -> dict:
    """Load experiment results."""
    if not path.exists():
        raise FileNotFoundError(f"Results not found: {path}")

    with open(path, 'r') as f:
        return json.load(f)


def run_scorecard(data: dict) -> Dict[str, Tuple[str, float, dict]]:
    """Run 6-prediction validation scorecard."""

    # Prediction 1: Intra-population homeostasis (Basin A)
    all_basins = []
    for exp in data['experiments']:
        for pop in exp['populations']:
            all_basins.append(pop['basin'])

    basin_a_pct = (sum(1 for b in all_basins if b == 'A') / len(all_basins)) * 100
    if basin_a_pct >= 90:
        p1_status, p1_score = "VALIDATED", 2.0
    elif basin_a_pct >= 70:
        p1_status, p1_score = "PARTIAL", 1.0
    else:
        p1_status, p1_score = "REJECTED", 0.0

    p1_metrics = {'basin_a_percentage': basin_a_pct}

    # Prediction 2: Inter-population variance reduction
    agg = data['aggregate_analysis']
    cv_between = agg['mean_between_population_cv']
    cv_within = agg['mean_within_population_cv']
    ratio_2 = cv_between / cv_within if cv_within > 0 else float('inf')

    if ratio_2 < 0.8:
        p2_status, p2_score = "VALIDATED", 2.0
    elif ratio_2 < 1.0:
        p2_status, p2_score = "PARTIAL", 1.0
    else:
        p2_status, p2_score = "REJECTED", 0.0

    p2_metrics = {'cv_between': cv_between, 'cv_within': cv_within, 'ratio': ratio_2}

    # Prediction 3: Meta-stability
    cv_swarm = np.mean([exp['swarm_metrics']['cv_population'] for exp in data['experiments']])
    cv_pop_values = [pop['cv_population'] for exp in data['experiments'] for pop in exp['populations']]
    cv_population = np.mean(cv_pop_values)
    ratio_3 = cv_swarm / cv_population if cv_population > 0 else float('inf')

    if ratio_3 < 0.5:
        p3_status, p3_score = "VALIDATED", 2.0
    elif ratio_3 < 0.8:
        p3_status, p3_score = "PARTIAL", 1.0
    else:
        p3_status, p3_score = "REJECTED", 0.0

    p3_metrics = {'cv_swarm': cv_swarm, 'cv_population': cv_population, 'ratio': ratio_3}

    # Prediction 4: Migration effectiveness
    migration_counts = [exp['hierarchical_metrics']['total_migrations'] for exp in data['experiments']]
    mean_migrations = np.mean(migration_counts)

    if 10 <= mean_migrations <= 18:
        p4_status, p4_score = "VALIDATED", 2.0
    elif (5 <= mean_migrations < 10) or (18 < mean_migrations <= 25):
        p4_status, p4_score = "PARTIAL", 1.0
    else:
        p4_status, p4_score = "REJECTED", 0.0

    p4_metrics = {'mean_migrations': mean_migrations, 'std_migrations': np.std(migration_counts)}

    # Prediction 5: Energy-population correlation
    energy_vals = [pop['mean_energy'] for exp in data['experiments'] for pop in exp['populations']]
    population_vals = [pop['mean_population'] for exp in data['experiments'] for pop in exp['populations']]

    if len(energy_vals) > 2:
        r, p_value = stats.pearsonr(energy_vals, population_vals)
    else:
        r, p_value = 0.0, 1.0

    if r >= 0.80:
        p5_status, p5_score = "VALIDATED", 2.0
    elif r >= 0.60:
        p5_status, p5_score = "PARTIAL", 1.0
    else:
        p5_status, p5_score = "REJECTED", 0.0

    p5_metrics = {'correlation_r': r, 'p_value': p_value, 'n_points': len(energy_vals)}

    # Prediction 6: No migration-induced collapse
    basin_b_pct = 100 - basin_a_pct

    if basin_b_pct <= 10.0:
        p6_status, p6_score = "VALIDATED", 2.0
    elif basin_b_pct <= 30.0:
        p6_status, p6_score = "PARTIAL", 1.0
    else:
        p6_status, p6_score = "REJECTED", 0.0

    p6_metrics = {'basin_b_percentage': basin_b_pct, 'threshold': 10.0}

    return {
        'prediction_1': (p1_status, p1_score, p1_metrics),
        'prediction_2': (p2_status, p2_score, p2_metrics),
        'prediction_3': (p3_status, p3_score, p3_metrics),
        'prediction_4': (p4_status, p4_score, p4_metrics),
        'prediction_5': (p5_status, p5_score, p5_metrics),
        'prediction_6': (p6_status, p6_score, p6_metrics),
    }


def generate_comparative_figure(scorecard_v1: dict, scorecard_v2: dict, output_path: Path):
    """Generate side-by-side scorecard comparison figure."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 8), sharey=True)

    predictions = ['P1: Homeostasis', 'P2: Variance', 'P3: Meta-stability',
                   'P4: Migration', 'P5: Energy Corr', 'P6: No Collapse']

    # V1 scores
    v1_scores = [scorecard_v1[f'prediction_{i+1}'][1] for i in range(6)]
    v1_total = sum(v1_scores)

    # V2 scores
    v2_scores = [scorecard_v2[f'prediction_{i+1}'][1] for i in range(6)]
    v2_total = sum(v2_scores)

    # Plot V1
    colors_v1 = ['green' if s == 2.0 else 'orange' if s == 1.0 else 'red' for s in v1_scores]
    axes[0].barh(predictions, v1_scores, color=colors_v1, alpha=0.7)
    axes[0].set_xlim(0, 2.5)
    axes[0].set_xlabel('Score (0-2)')
    axes[0].set_title(f'C186 V1 (f_intra=2.5%)\nTotal: {v1_total:.1f}/12.0')
    axes[0].axvline(2.0, color='gray', linestyle='--', alpha=0.5)
    axes[0].grid(axis='x', alpha=0.3)

    # Plot V2
    colors_v2 = ['green' if s == 2.0 else 'orange' if s == 1.0 else 'red' for s in v2_scores]
    axes[1].barh(predictions, v2_scores, color=colors_v2, alpha=0.7)
    axes[1].set_xlim(0, 2.5)
    axes[1].set_xlabel('Score (0-2)')
    axes[1].set_title(f'C186 V2 (f_intra=5.0%)\nTotal: {v2_total:.1f}/12.0')
    axes[1].axvline(2.0, color='gray', linestyle='--', alpha=0.5)
    axes[1].grid(axis='x', alpha=0.3)

    plt.suptitle('C186 V1 vs. V2 Validation Scorecard Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    plt.close()


def main():
    """Execute C186 V2 comparative analysis."""
    print("=" * 80)
    print("C186 V2 COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()

    # Load results
    print("Loading results...")
    data_v1 = load_results(RESULTS_V1_PATH)
    data_v2 = load_results(RESULTS_V2_PATH)
    print(f"✓ C186 V1 loaded: {data_v1['metadata']['total_experiments']} experiments")
    print(f"✓ C186 V2 loaded: {data_v2['metadata']['total_experiments']} experiments")
    print()

    # Run scorecards
    print("Running validation scorecards...")
    scorecard_v1 = run_scorecard(data_v1)
    scorecard_v2 = run_scorecard(data_v2)
    print("✓ Scorecards complete")
    print()

    # Calculate totals
    total_v1 = sum(sc[1] for sc in scorecard_v1.values())
    total_v2 = sum(sc[1] for sc in scorecard_v2.values())

    # Basin A comparison
    basin_a_v1 = scorecard_v1['prediction_1'][2]['basin_a_percentage']
    basin_a_v2 = scorecard_v2['prediction_1'][2]['basin_a_percentage']
    basin_a_improvement = basin_a_v2 - basin_a_v1

    # Display results
    print("=" * 80)
    print("COMPARATIVE RESULTS")
    print("=" * 80)
    print()

    print("VALIDATION SCORECARD:")
    print("-" * 80)
    print(f"C186 V1 (f_intra=2.5%): {total_v1:.1f}/12.0 ({(total_v1/12)*100:.1f}%)")
    print(f"C186 V2 (f_intra=5.0%): {total_v2:.1f}/12.0 ({(total_v2/12)*100:.1f}%)")
    print(f"Improvement: {(total_v2 - total_v1):.1f} points ({((total_v2-total_v1)/12)*100:.1f} percentage points)")
    print()

    print("BASIN A CLASSIFICATION (CRITICAL):")
    print("-" * 80)
    print(f"C186 V1: {basin_a_v1:.1f}% Basin A (100% collapsed)")
    print(f"C186 V2: {basin_a_v2:.1f}% Basin A")
    print(f"Improvement: +{basin_a_improvement:.1f} percentage points")
    print()

    # Hypothesis testing
    print("VIABILITY HYPOTHESIS TEST:")
    print("-" * 80)
    print("Hypothesis: Metapopulations require f_intra ≥ 5.0% for viability")
    print(f"Success Criterion: Basin A ≥ 50%")
    print(f"Result: Basin A = {basin_a_v2:.1f}%")

    if basin_a_v2 >= 50:
        print("✅ HYPOTHESIS VALIDATED: f_intra=5.0% supports population sustainability")
    elif basin_a_v2 > 0:
        print("⚠️  HYPOTHESIS PARTIALLY SUPPORTED: Some improvement, but <50% threshold")
        print(f"   Recommendation: Test higher spawn rate (f_intra ≥ 10.0%)")
    else:
        print("❌ HYPOTHESIS REJECTED: f_intra=5.0% still insufficient")
        print(f"   Recommendation: Significant increase needed (f_intra ≥ 10.0% or higher)")
    print()

    # Per-prediction comparison
    print("PER-PREDICTION COMPARISON:")
    print("-" * 80)
    prediction_names = {
        'prediction_1': 'Intra-pop homeostasis (Basin A)',
        'prediction_2': 'Inter-pop variance reduction',
        'prediction_3': 'Meta-stability (swarm-level)',
        'prediction_4': 'Migration effectiveness',
        'prediction_5': 'Energy-population correlation',
        'prediction_6': 'No migration-induced collapse',
    }

    for pred_key, pred_name in prediction_names.items():
        status_v1, score_v1, _ = scorecard_v1[pred_key]
        status_v2, score_v2, _ = scorecard_v2[pred_key]
        improvement = score_v2 - score_v1

        print(f"{pred_name}:")
        print(f"  V1: {score_v1:.1f}/2.0 ({status_v1})")
        print(f"  V2: {score_v2:.1f}/2.0 ({status_v2})")
        print(f"  Δ:  {improvement:+.1f}")
        print()

    # Generate figures
    print("Generating comparative figures...")
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    fig_path = OUTPUT_DIR / "c186_v1_vs_v2_scorecard_comparison.png"
    generate_comparative_figure(scorecard_v1, scorecard_v2, fig_path)
    print()

    # Save comparative report
    report_path = Path(__file__).parent / "results" / "cycle186_v2_comparative_report.json"
    report = {
        'metadata': {
            'analysis_type': 'C186 V1 vs. V2 Comparative Validation',
            'v1_f_intra': 2.5,
            'v2_f_intra': 5.0,
            'hypothesis': 'Metapopulations require f_intra ≥ 5.0% for viability',
        },
        'scorecard_v1': {k: {'status': v[0], 'score': v[1], 'metrics': v[2]} for k, v in scorecard_v1.items()},
        'scorecard_v2': {k: {'status': v[0], 'score': v[1], 'metrics': v[2]} for k, v in scorecard_v2.items()},
        'totals': {
            'v1_total': total_v1,
            'v2_total': total_v2,
            'improvement': total_v2 - total_v1,
        },
        'basin_a_comparison': {
            'v1_basin_a': basin_a_v1,
            'v2_basin_a': basin_a_v2,
            'improvement': basin_a_improvement,
        },
        'hypothesis_test': {
            'criterion': 'Basin A ≥ 50%',
            'result': basin_a_v2,
            'validated': basin_a_v2 >= 50,
        },
    }

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Comparative report saved: {report_path}")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
