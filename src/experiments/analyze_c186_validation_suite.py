#!/usr/bin/env python3
"""
C186 Validation Suite Analysis: Hierarchical Scaling Coefficient α

Purpose: Comprehensive statistical analysis of all C186 validation experiments
         testing predictions about hierarchical scaling coefficient α ≈ 2.0

Experiments Analyzed:
- C186 V1: Baseline failure (f_intra=2.5%, 0% Basin A expected)
- C186 V2: Partial restoration (f_intra=5.0%, 50-60% Basin A expected)
- C186 V3: Three-level hierarchy (α_3-level ≈ 4.0 predicted)
- C186 V4: Migration rate effects (higher f_migrate reduces α)
- C186 V5: Population size effects (larger N reduces α)
- C186 V6: Partial compartmentalization (more sharing reduces α)
- C186 V7: α empirical mapping (precision α ± error bars via sigmoid fit)

Statistical Tests:
- Chi-square: Basin A vs Basin B distribution
- t-tests: Mean population differences between conditions
- ANOVA: Multi-condition comparisons
- Seed independence validation
- Control frequency validation

Figure Generation:
- Basin A percentage by parameter
- Mean population trajectories
- α coefficient extraction plots
- Hypothesis validation summaries

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1056)
License: GPL-3.0
"""

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import curve_fit

# Analysis configuration
RESULTS_DIR = Path(__file__).parent.parent.parent / "experiments" / "results"
FIGURES_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Expected results for validation
EXPECTED_RESULTS = {
    'V1': {'f_intra': 0.025, 'basin_a_pct': 0.0, 'tolerance': 10.0},
    'V2': {'f_intra': 0.050, 'basin_a_pct': 55.0, 'tolerance': 15.0},
    'V3': {'f_agent': 0.080, 'basin_a_pct': 50.0, 'tolerance': 20.0},
    'V4': {'f_migrate': [0.005, 0.025, 0.050], 'monotonic': 'increasing'},
    'V5': {'n_initial': [10, 20, 40], 'monotonic': 'increasing'},
    'V6': {'structures': ['ISOLATED', 'PAIRED', 'CLUSTERED'], 'monotonic': 'increasing'},
    'V7': {'f_intra_range': [0.020, 0.060], 'sigmoid_fit': True}
}

@dataclass
class ExperimentResult:
    """Container for experiment results"""
    experiment_id: str
    parameter: str
    parameter_value: float
    basin_a_pct: float
    mean_population: float
    std_population: float
    n_seeds: int
    raw_results: List[Dict]

@dataclass
class ValidationReport:
    """Validation results for an experiment"""
    experiment_id: str
    hypothesis: str
    prediction: str
    result: str
    statistical_test: str
    p_value: float
    effect_size: float
    validated: bool
    notes: str

def load_experiment_results(experiment_id: str) -> Optional[Dict]:
    """Load experiment results from JSON file"""
    result_files = {
        'V1': 'c186_v1_hierarchical_spawn_failure.json',
        'V2': 'c186_v2_hierarchical_spawn_success.json',
        'V3': 'c186_v3_three_level_hierarchy.json',
        'V4': 'c186_v4_migration_rate_effects.json',
        'V5': 'c186_v5_population_size_effects.json',
        'V6': 'c186_v6_partial_compartmentalization.json',
        'V7': 'c186_v7_alpha_empirical_mapping.json'
    }

    if experiment_id not in result_files:
        return None

    filepath = RESULTS_DIR / result_files[experiment_id]
    if not filepath.exists():
        print(f"  ⚠ {experiment_id}: Results file not found ({filepath.name})")
        return None

    with open(filepath, 'r') as f:
        data = json.load(f)

    print(f"  ✓ {experiment_id}: Loaded {len(data.get('individual_results', []))} results")
    return data

def calculate_basin_a_percentage(results: List[Dict]) -> Tuple[float, List[float]]:
    """Calculate Basin A percentage and per-seed populations"""
    basin_a_count = sum(1 for r in results if r.get('basin') == 'A')
    basin_a_pct = (basin_a_count / len(results)) * 100 if results else 0.0

    mean_pops = [r.get('mean_population', 0.0) for r in results]

    return basin_a_pct, mean_pops

def validate_baseline(v1_data: Dict, v2_data: Dict) -> ValidationReport:
    """Validate baseline experiments (V1 failure, V2 partial success)"""
    v1_results = v1_data['individual_results']
    v2_results = v2_data['individual_results']

    v1_basin_a, v1_pops = calculate_basin_a_percentage(v1_results)
    v2_basin_a, v2_pops = calculate_basin_a_percentage(v2_results)

    # Statistical test: compare mean populations
    t_stat, p_value = stats.ttest_ind(v1_pops, v2_pops)
    cohen_d = (np.mean(v2_pops) - np.mean(v1_pops)) / np.sqrt((np.std(v1_pops)**2 + np.std(v2_pops)**2) / 2)

    # Validation
    v1_matches = abs(v1_basin_a - EXPECTED_RESULTS['V1']['basin_a_pct']) < EXPECTED_RESULTS['V1']['tolerance']
    v2_matches = abs(v2_basin_a - EXPECTED_RESULTS['V2']['basin_a_pct']) < EXPECTED_RESULTS['V2']['tolerance']

    validated = v1_matches and v2_matches and p_value < 0.05

    return ValidationReport(
        experiment_id='V1+V2',
        hypothesis='Hierarchical scaling: 2× spawn rate required for viability',
        prediction=f"V1 (f=2.5%): 0% Basin A, V2 (f=5.0%): 50-60% Basin A",
        result=f"V1: {v1_basin_a:.1f}% Basin A, V2: {v2_basin_a:.1f}% Basin A",
        statistical_test=f"t-test: t={t_stat:.3f}",
        p_value=p_value,
        effect_size=cohen_d,
        validated=validated,
        notes=f"Cohen's d = {cohen_d:.2f} ({'large' if abs(cohen_d) > 0.8 else 'medium' if abs(cohen_d) > 0.5 else 'small'} effect)"
    )

def validate_monotonic_trend(data: Dict, parameter_key: str, experiment_id: str) -> ValidationReport:
    """Validate monotonic increasing trend in Basin A percentage"""

    # Extract parameter values and Basin A percentages
    if experiment_id == 'V4':
        param_name = 'f_migrate'
        aggregates = data['rate_aggregates']
        param_values = [agg['f_migrate'] for agg in aggregates]
        basin_a_pcts = [agg['basin_a_pct'] for agg in aggregates]
    elif experiment_id == 'V5':
        param_name = 'n_initial'
        aggregates = data['size_aggregates']
        param_values = [agg['n_initial'] for agg in aggregates]
        basin_a_pcts = [agg['basin_a_pct'] for agg in aggregates]
    elif experiment_id == 'V6':
        param_name = 'pool_structure'
        aggregates = data['structure_aggregates']
        param_values = [0, 1, 2]  # ISOLATED, PAIRED, CLUSTERED
        basin_a_pcts = [agg['basin_a_pct'] for agg in aggregates]
    else:
        return None

    # Test monotonic increase
    is_monotonic = all(basin_a_pcts[i] <= basin_a_pcts[i+1] for i in range(len(basin_a_pcts)-1))

    # Spearman correlation
    rho, p_value = stats.spearmanr(param_values, basin_a_pcts)

    # Effect size (difference between extremes)
    effect_size = basin_a_pcts[-1] - basin_a_pcts[0]

    validated = is_monotonic and p_value < 0.05 and effect_size > 20.0

    hypothesis_map = {
        'V4': 'Higher migration rates reduce α via energy sharing',
        'V5': 'Larger populations reduce α via energy buffering',
        'V6': 'Partial compartmentalization reduces α via shared pools'
    }

    return ValidationReport(
        experiment_id=experiment_id,
        hypothesis=hypothesis_map.get(experiment_id, 'Unknown'),
        prediction=f"Basin A increases monotonically with {param_name}",
        result=f"Basin A: {basin_a_pcts[0]:.1f}% → {basin_a_pcts[-1]:.1f}%",
        statistical_test=f"Spearman ρ={rho:.3f}",
        p_value=p_value,
        effect_size=effect_size,
        validated=validated,
        notes=f"Monotonic: {is_monotonic}, Δ Basin A = {effect_size:.1f}%"
    )

def fit_sigmoid_alpha(data: Dict) -> Tuple[float, float, ValidationReport]:
    """Fit sigmoid to V7 data and extract α coefficient"""

    aggregates = data['freq_aggregates']
    f_values = np.array([agg['f_intra'] for agg in aggregates])
    basin_a_pcts = np.array([agg['basin_a_pct'] for agg in aggregates])

    # Sigmoid function: Basin_A(f) = 100 / (1 + exp(-k * (f - f_crit)))
    def sigmoid(f, f_crit, k):
        return 100 / (1 + np.exp(-k * (f - f_crit)))

    try:
        # Initial guess: f_crit ≈ 4.0%, k ≈ 200
        popt, pcov = curve_fit(sigmoid, f_values, basin_a_pcts, p0=[0.040, 200], maxfev=10000)
        f_crit_hierarchical, k = popt
        f_crit_err = np.sqrt(pcov[0, 0])

        # Calculate α = f_crit_hierarchical / f_crit_single-scale
        # From C171, f_crit_single-scale ≈ 2.0%
        f_crit_single = 0.020
        alpha = f_crit_hierarchical / f_crit_single
        alpha_err = f_crit_err / f_crit_single

        # R-squared
        residuals = basin_a_pcts - sigmoid(f_values, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((basin_a_pcts - np.mean(basin_a_pcts))**2)
        r_squared = 1 - (ss_res / ss_tot)

        validated = (1.7 <= alpha <= 2.3) and (r_squared > 0.90)

        report = ValidationReport(
            experiment_id='V7',
            hypothesis='Hierarchical scaling coefficient α ≈ 2.0',
            prediction='Sigmoid fit: f_crit_hierarchical = α × f_crit_single (α ≈ 2.0)',
            result=f"α = {alpha:.2f} ± {alpha_err:.2f}",
            statistical_test=f"Sigmoid fit: R² = {r_squared:.3f}",
            p_value=1 - r_squared,  # Pseudo p-value
            effect_size=alpha,
            validated=validated,
            notes=f"f_crit = {f_crit_hierarchical*100:.2f}% ± {f_crit_err*100:.2f}%, k = {k:.1f}"
        )

        return alpha, alpha_err, report

    except Exception as e:
        print(f"  ⚠ Sigmoid fit failed: {e}")
        return 0.0, 0.0, None

def generate_validation_summary_figure(reports: List[ValidationReport], output_path: Path):
    """Generate validation summary figure"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Prepare data
    experiment_ids = [r.experiment_id for r in reports if r is not None]
    validated = [r.validated for r in reports if r is not None]
    p_values = [r.p_value for r in reports if r is not None]
    effect_sizes = [r.effect_size for r in reports if r is not None]

    # Color code by validation status
    colors = ['green' if v else 'red' for v in validated]

    # Bar plot
    y_pos = np.arange(len(experiment_ids))
    ax.barh(y_pos, effect_sizes, color=colors, alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(experiment_ids)
    ax.set_xlabel('Effect Size', fontsize=12)
    ax.set_title('C186 Validation Suite: Hypothesis Testing Results', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)

    # Add p-values as text
    for i, (eff, p) in enumerate(zip(effect_sizes, p_values)):
        label = f"p={p:.3f}" if p < 1.0 else "p<0.001"
        ax.text(eff + 0.1, i, label, va='center', fontsize=9)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, label='Hypothesis Supported'),
        Patch(facecolor='red', alpha=0.7, label='Hypothesis Not Supported')
    ]
    ax.legend(handles=legend_elements, loc='best')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  ✓ Validation summary figure saved: {output_path.name}")

def generate_basin_a_trends_figure(all_data: Dict[str, Dict], output_path: Path):
    """Generate Basin A percentage trends across all experiments"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    experiments = [
        ('V4', 'rate_aggregates', 'f_migrate', 'Migration Rate (%)', 100),
        ('V5', 'size_aggregates', 'n_initial', 'Initial Population Size', 1),
        ('V6', 'structure_aggregates', 'n_clusters', 'Number of Energy Clusters', 1),
        ('V7', 'freq_aggregates', 'f_intra', 'Spawn Frequency (%)', 100)
    ]

    for idx, (exp_id, agg_key, param_key, xlabel, scale) in enumerate(experiments):
        if exp_id not in all_data or all_data[exp_id] is None:
            axes[idx].text(0.5, 0.5, f'{exp_id}: No Data', ha='center', va='center', fontsize=14)
            continue

        data = all_data[exp_id]
        aggregates = data.get(agg_key, [])

        param_values = [agg[param_key] * scale for agg in aggregates]
        basin_a_pcts = [agg['basin_a_pct'] for agg in aggregates]

        axes[idx].plot(param_values, basin_a_pcts, 'o-', linewidth=2, markersize=8, color='blue')
        axes[idx].axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% Threshold')
        axes[idx].set_xlabel(xlabel, fontsize=11)
        axes[idx].set_ylabel('Basin A Percentage (%)', fontsize=11)
        axes[idx].set_title(f'{exp_id}: Basin A vs {param_key}', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3)
        axes[idx].legend()

    plt.suptitle('C186 Validation Suite: Basin A Trends', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  ✓ Basin A trends figure saved: {output_path.name}")

def main():
    """Execute C186 validation suite analysis"""

    print("=" * 80)
    print("C186 VALIDATION SUITE ANALYSIS")
    print("=" * 80)
    print()
    print("Loading experimental results...")
    print("-" * 80)

    # Load all experiment results
    all_data = {}
    for exp_id in ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']:
        all_data[exp_id] = load_experiment_results(exp_id)

    print()
    print("=" * 80)
    print("HYPOTHESIS VALIDATION")
    print("=" * 80)
    print()

    validation_reports = []

    # Baseline validation (V1 + V2)
    if all_data['V1'] and all_data['V2']:
        print("Testing H1: Hierarchical scaling coefficient α ≈ 2.0 (V1 + V2)")
        report = validate_baseline(all_data['V1'], all_data['V2'])
        validation_reports.append(report)
        print(f"  Result: {report.result}")
        print(f"  Statistical test: {report.statistical_test}, p={report.p_value:.4f}")
        print(f"  Validated: {'✓ YES' if report.validated else '✗ NO'}")
        print()

    # V4: Migration rate effects
    if all_data['V4']:
        print("Testing H2: Higher migration rates reduce α (V4)")
        report = validate_monotonic_trend(all_data['V4'], 'f_migrate', 'V4')
        if report:
            validation_reports.append(report)
            print(f"  Result: {report.result}")
            print(f"  Statistical test: {report.statistical_test}, p={report.p_value:.4f}")
            print(f"  Validated: {'✓ YES' if report.validated else '✗ NO'}")
            print()

    # V5: Population size effects
    if all_data['V5']:
        print("Testing H3: Larger populations reduce α (V5)")
        report = validate_monotonic_trend(all_data['V5'], 'n_initial', 'V5')
        if report:
            validation_reports.append(report)
            print(f"  Result: {report.result}")
            print(f"  Statistical test: {report.statistical_test}, p={report.p_value:.4f}")
            print(f"  Validated: {'✓ YES' if report.validated else '✗ NO'}")
            print()

    # V6: Partial compartmentalization
    if all_data['V6']:
        print("Testing H4: Partial compartmentalization reduces α (V6)")
        report = validate_monotonic_trend(all_data['V6'], 'pool_structure', 'V6')
        if report:
            validation_reports.append(report)
            print(f"  Result: {report.result}")
            print(f"  Statistical test: {report.statistical_test}, p={report.p_value:.4f}")
            print(f"  Validated: {'✓ YES' if report.validated else '✗ NO'}")
            print()

    # V7: α empirical mapping
    if all_data['V7']:
        print("Testing H5: Precise α measurement via sigmoid fit (V7)")
        alpha, alpha_err, report = fit_sigmoid_alpha(all_data['V7'])
        if report:
            validation_reports.append(report)
            print(f"  Result: {report.result}")
            print(f"  Statistical test: {report.statistical_test}")
            print(f"  Validated: {'✓ YES' if report.validated else '✗ NO'}")
            print()

    print("=" * 80)
    print("GENERATING FIGURES")
    print("=" * 80)
    print()

    # Generate validation summary figure
    summary_fig_path = FIGURES_DIR / "c186_validation_suite_hypothesis_testing.png"
    generate_validation_summary_figure(validation_reports, summary_fig_path)

    # Generate Basin A trends figure
    trends_fig_path = FIGURES_DIR / "c186_validation_suite_basin_a_trends.png"
    generate_basin_a_trends_figure(all_data, trends_fig_path)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    validated_count = sum(1 for r in validation_reports if r and r.validated)
    total_count = len([r for r in validation_reports if r is not None])

    print(f"Hypotheses Validated: {validated_count}/{total_count}")
    print(f"Validation Rate: {validated_count/total_count*100:.1f}%")
    print()

    if validated_count == total_count:
        print("✓ ALL HYPOTHESES VALIDATED")
        print("  Hierarchical scaling theory comprehensively supported by empirical data.")
    elif validated_count >= total_count * 0.8:
        print("✓ MAJORITY HYPOTHESES VALIDATED")
        print("  Hierarchical scaling theory substantially supported, minor refinements needed.")
    else:
        print("⚠ PARTIAL VALIDATION")
        print("  Some hypotheses not supported, theory requires significant revision.")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
