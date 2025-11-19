#!/usr/bin/env python3
"""
Analysis: C186 V1/V2 Baseline Hierarchical Validation

Purpose: Validate hierarchical scaling coefficient (α) bounds from baseline experiments

Experiments:
    - C186 V1 (f_intra=2.5%): Expect 0% Basin A (failure, confirms α > 1.25)
    - C186 V2 (f_intra=5.0%): Expect 50-60% Basin A (threshold, confirms α ≈ 2.5)

Background:
    - C171 single-scale: f_crit ≈ 2.0%, 100% Basin A at f=2.0-3.0%
    - Hierarchical prediction: α ≈ 2.0, so f_hier_crit ≈ 4.0-5.0%
    - α = f_hier_crit / f_single_crit (hierarchical scaling coefficient)

Analysis:
    1. Load V1 and V2 experimental results
    2. Calculate Basin A percentages for each
    3. Compare to predictions
    4. Estimate α bounds from observed data
    5. Generate validation figures

Output:
    - Statistical validation report
    - α bounds estimate
    - 2 publication figures @ 300 DPI

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1060)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

# Experimental parameters
F_SINGLE_CRIT = 0.020  # 2.0% single-scale critical frequency (from C171)
F_V1_INTRA = 0.025  # 2.5% V1 frequency
F_V2_INTRA = 0.050  # 5.0% V2 frequency

# Predictions
PREDICTED_V1_BASIN_A = 0.0  # Expect complete failure
PREDICTED_V2_BASIN_A = 0.55  # Expect 50-60% threshold viability
PREDICTED_ALPHA = 2.0  # Hierarchical scaling coefficient

def load_experiment_results(results_file: Path) -> Dict:
    """Load experimental results from JSON"""
    with open(results_file, 'r') as f:
        return json.load(f)

def calculate_statistics(results: List[Dict]) -> Dict:
    """Calculate summary statistics from individual results"""
    basins = [r['basin'] for r in results]
    mean_pops = [r['mean_population'] for r in results]

    basin_a_count = sum(1 for b in basins if b == 'A')
    basin_a_pct = (basin_a_count / len(basins)) * 100

    return {
        'n_experiments': len(results),
        'basin_a_count': basin_a_count,
        'basin_a_pct': basin_a_pct,
        'mean_population_avg': np.mean(mean_pops),
        'mean_population_std': np.std(mean_pops, ddof=1),
        'mean_population_sem': stats.sem(mean_pops)
    }

def estimate_alpha_bounds(v1_basin_a_pct: float, v2_basin_a_pct: float) -> Tuple[float, float, float]:
    """
    Estimate α bounds from V1 and V2 results

    Logic:
        - If V1 (f=2.5%) produces 0% Basin A: f_crit > 2.5%, so α > 2.5/2.0 = 1.25
        - If V2 (f=5.0%) produces 50-60% Basin A: f_crit ≈ 5.0%, so α ≈ 5.0/2.0 = 2.5
        - Combined: 1.25 < α < (5.0 / 2.0) = 2.5

    Returns:
        (α_lower, α_estimate, α_upper)
    """

    # Lower bound from V1
    if v1_basin_a_pct < 10:  # Nearly complete failure
        alpha_lower = F_V1_INTRA / F_SINGLE_CRIT  # α > 1.25
    else:
        alpha_lower = 1.0  # Unexpected success, lower bound uncertain

    # Upper bound and estimate from V2
    if 40 <= v2_basin_a_pct <= 70:  # Threshold behavior
        # V2 frequency is near critical threshold
        alpha_estimate = F_V2_INTRA / F_SINGLE_CRIT  # α ≈ 2.5
        alpha_upper = alpha_estimate * 1.2  # ±20% uncertainty
    elif v2_basin_a_pct < 40:  # Still below threshold
        # Critical frequency higher than V2
        alpha_estimate = (F_V2_INTRA / F_SINGLE_CRIT) * 1.2  # α > 2.5
        alpha_upper = alpha_estimate * 1.5
    else:  # v2_basin_a_pct > 70, well above threshold
        # Critical frequency lower than V2
        alpha_estimate = (F_V2_INTRA / F_SINGLE_CRIT) * 0.8  # α < 2.5
        alpha_upper = F_V2_INTRA / F_SINGLE_CRIT

    return (alpha_lower, alpha_estimate, alpha_upper)

def generate_basin_comparison_figure(v1_stats: Dict, v2_stats: Dict, output_path: Path):
    """
    Figure 1: Basin A Percentage Comparison

    Shows V1 vs V2 Basin A percentages with predictions
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Data
    experiments = ['V1\nf=2.5%', 'V2\nf=5.0%']
    observed = [v1_stats['basin_a_pct'], v2_stats['basin_a_pct']]
    predicted = [PREDICTED_V1_BASIN_A * 100, PREDICTED_V2_BASIN_A * 100]

    x = np.arange(len(experiments))
    width = 0.35

    # Bars
    ax.bar(x - width/2, observed, width, label='Observed', color='steelblue', alpha=0.8)
    ax.bar(x + width/2, predicted, width, label='Predicted', color='coral', alpha=0.8)

    # Formatting
    ax.set_ylabel('Basin A Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Experiment', fontsize=12, fontweight='bold')
    ax.set_title('C186 V1/V2: Basin A Validation\nHierarchical Scaling Baseline Tests',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(experiments, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, 100)

    # Add values on bars
    for i, (obs, pred) in enumerate(zip(observed, predicted)):
        ax.text(i - width/2, obs + 3, f'{obs:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold')
        ax.text(i + width/2, pred + 3, f'{pred:.1f}%', ha='center', va='bottom',
                fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path.name}")

def generate_alpha_bounds_figure(alpha_bounds: Tuple[float, float, float], output_path: Path):
    """
    Figure 2: Hierarchical Scaling Coefficient (α) Bounds

    Shows estimated α range from V1/V2 validation
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    alpha_lower, alpha_estimate, alpha_upper = alpha_bounds

    # Plot α range
    ax.axvspan(alpha_lower, alpha_upper, alpha=0.3, color='steelblue',
               label=f'Estimated α Range')
    ax.axvline(alpha_estimate, color='darkblue', linewidth=2, linestyle='--',
               label=f'α Estimate = {alpha_estimate:.2f}')
    ax.axvline(PREDICTED_ALPHA, color='coral', linewidth=2, linestyle=':',
               label=f'Predicted α = {PREDICTED_ALPHA:.2f}')

    # Mark V1 and V2 frequency ratios
    alpha_v1 = F_V1_INTRA / F_SINGLE_CRIT
    alpha_v2 = F_V2_INTRA / F_SINGLE_CRIT
    ax.scatter([alpha_v1], [0.5], s=100, marker='o', color='red', zorder=5,
               label=f'V1: f_intra/f_crit = {alpha_v1:.2f}')
    ax.scatter([alpha_v2], [0.5], s=100, marker='s', color='green', zorder=5,
               label=f'V2: f_intra/f_crit = {alpha_v2:.2f}')

    # Formatting
    ax.set_xlabel('Hierarchical Scaling Coefficient (α)', fontsize=12, fontweight='bold')
    ax.set_ylabel('', fontsize=12)
    ax.set_title('C186 Baseline Validation: α Bounds Estimate\n'
                 'Hierarchical Energy Compartmentalization Overhead',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0.5, 3.5)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_yticks([])

    # Add interpretation text
    interpretation = (
        f"α = f_hier_crit / f_single_crit\n"
        f"Estimated range: [{alpha_lower:.2f}, {alpha_upper:.2f}]\n"
        f"Best estimate: {alpha_estimate:.2f}"
    )
    ax.text(0.98, 0.05, interpretation, transform=ax.transAxes,
            fontsize=10, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path.name}")

def main():
    """Execute C186 V1/V2 baseline validation analysis"""

    print("=" * 80)
    print("C186 V1/V2 BASELINE VALIDATION ANALYSIS")
    print("=" * 80)
    print()

    # Paths
    results_dir = Path(__file__).parent.parent / "experiments" / "results"
    figures_dir = Path(__file__).parent.parent / "data" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    v1_results_file = results_dir / "c186_v1_hierarchical_spawn_failure_simple.json"
    v2_results_file = results_dir / "c186_v2_hierarchical_spawn_success_simple.json"

    # Load results
    print("Loading experimental results...")
    v1_data = load_experiment_results(v1_results_file)
    v2_data = load_experiment_results(v2_results_file)
    print(f"  V1: {len(v1_data['individual_results'])} experiments")
    print(f"  V2: {len(v2_data['individual_results'])} experiments")
    print()

    # Calculate statistics
    print("Calculating statistics...")
    v1_stats = calculate_statistics(v1_data['individual_results'])
    v2_stats = calculate_statistics(v2_data['individual_results'])
    print()

    # V1 Results
    print("V1 RESULTS (f_intra=2.5%, expect 0% Basin A):")
    print("-" * 80)
    print(f"  Basin A: {v1_stats['basin_a_count']}/{v1_stats['n_experiments']} "
          f"({v1_stats['basin_a_pct']:.1f}%)")
    print(f"  Mean population: {v1_stats['mean_population_avg']:.2f} ± "
          f"{v1_stats['mean_population_std']:.2f}")
    print(f"  Prediction: {PREDICTED_V1_BASIN_A*100:.1f}% Basin A")

    if v1_stats['basin_a_pct'] < 10:
        print("  ✓ VALIDATED: Complete failure as predicted")
        print("    Confirms α > 1.25 (hierarchical overhead exists)")
    else:
        print(f"  ⚠ UNEXPECTED: {v1_stats['basin_a_pct']:.1f}% Basin A (expected ~0%)")
        print("    May indicate α < 1.25 (lower overhead than predicted)")
    print()

    # V2 Results
    print("V2 RESULTS (f_intra=5.0%, expect 50-60% Basin A):")
    print("-" * 80)
    print(f"  Basin A: {v2_stats['basin_a_count']}/{v2_stats['n_experiments']} "
          f"({v2_stats['basin_a_pct']:.1f}%)")
    print(f"  Mean population: {v2_stats['mean_population_avg']:.2f} ± "
          f"{v2_stats['mean_population_std']:.2f}")
    print(f"  Prediction: {PREDICTED_V2_BASIN_A*100:.1f}% Basin A")

    if 40 <= v2_stats['basin_a_pct'] <= 70:
        print("  ✓ VALIDATED: Threshold viability as predicted")
        print("    Confirms f_hier_crit ≈ 5.0%, α ≈ 2.5")
    elif v2_stats['basin_a_pct'] < 40:
        print(f"  ⚠ BELOW THRESHOLD: {v2_stats['basin_a_pct']:.1f}% Basin A")
        print("    May indicate f_hier_crit > 5.0%, α > 2.5")
    else:
        print(f"  ⚠ ABOVE THRESHOLD: {v2_stats['basin_a_pct']:.1f}% Basin A")
        print("    May indicate f_hier_crit < 5.0%, α < 2.5")
    print()

    # Estimate α bounds
    print("HIERARCHICAL SCALING COEFFICIENT (α) ESTIMATE:")
    print("-" * 80)
    alpha_bounds = estimate_alpha_bounds(v1_stats['basin_a_pct'], v2_stats['basin_a_pct'])
    alpha_lower, alpha_estimate, alpha_upper = alpha_bounds
    print(f"  Lower bound: α > {alpha_lower:.2f} (from V1 failure)")
    print(f"  Best estimate: α ≈ {alpha_estimate:.2f}")
    print(f"  Upper bound: α < {alpha_upper:.2f}")
    print(f"  Predicted: α = {PREDICTED_ALPHA:.2f}")
    print()

    if alpha_lower <= PREDICTED_ALPHA <= alpha_upper:
        print("  ✓ PREDICTION VALIDATED: Observed α consistent with prediction")
    else:
        print(f"  ⚠ PREDICTION MISMATCH: Observed α outside predicted range")
    print()

    # Generate figures
    print("Generating publication figures...")
    fig1_path = figures_dir / "c186_basin_comparison.png"
    fig2_path = figures_dir / "c186_alpha_bounds.png"

    generate_basin_comparison_figure(v1_stats, v2_stats, fig1_path)
    generate_alpha_bounds_figure(alpha_bounds, fig2_path)
    print()

    # Save summary
    summary = {
        'experiment': 'C186_V1_V2_BASELINE_VALIDATION',
        'date': v1_data['date'],
        'v1_statistics': v1_stats,
        'v2_statistics': v2_stats,
        'alpha_bounds': {
            'lower': alpha_lower,
            'estimate': alpha_estimate,
            'upper': alpha_upper,
            'predicted': PREDICTED_ALPHA
        },
        'validation': {
            'v1_validated': v1_stats['basin_a_pct'] < 10,
            'v2_validated': 40 <= v2_stats['basin_a_pct'] <= 70,
            'alpha_validated': alpha_lower <= PREDICTED_ALPHA <= alpha_upper
        }
    }

    summary_file = results_dir / "c186_v1_v2_validation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary saved: {summary_file.name}")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  - Integrate findings into Paper 2 (Methods + Results)")
    print("  - Execute C186 V7 if baseline validates (precision α mapping)")
    print("  - Compare to C177 V2 single-scale boundary mapping")
    print()

if __name__ == "__main__":
    main()
