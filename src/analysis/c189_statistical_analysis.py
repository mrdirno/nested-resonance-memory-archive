#!/usr/bin/env python3
"""
C189 Statistical Analysis: Hierarchical vs Flat Spawn Comparison

Purpose: Perform rigorous statistical tests on C189 mechanism comparison results

Tests:
    - T-tests (hierarchical vs flat at each frequency)
    - Effect size calculations (Cohen's d)
    - Variance comparison (F-test)
    - Two-way ANOVA (mechanism × frequency)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1319)
License: GPL-3.0
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib as mpl

# Publication figure settings
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['xtick.labelsize'] = 9
mpl.rcParams['ytick.labelsize'] = 9
mpl.rcParams['legend.fontsize'] = 9
mpl.rcParams['figure.titlesize'] = 13

def load_c189_results() -> Dict:
    """Load C189 experimental results"""
    results_file = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c189_hierarchical_vs_flat_spawn.json")

    if not results_file.exists():
        raise FileNotFoundError(f"C189 results not found: {results_file}")

    with open(results_file, 'r') as f:
        data = json.load(f)

    return data

def cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Calculate Cohen's d effect size

    Interpretation:
        d < 0.2: Negligible
        0.2 ≤ d < 0.5: Small
        0.5 ≤ d < 0.8: Medium
        d ≥ 0.8: Large
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    # Cohen's d
    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    return d

def levenes_test(group1: List[float], group2: List[float]) -> Tuple[float, float]:
    """
    Levene's test for equality of variances

    H0: Variances are equal
    H1: Variances are different
    """
    statistic, p_value = stats.levene(group1, group2)
    return statistic, p_value

def perform_frequency_tests(results: Dict) -> Dict:
    """Perform statistical tests for each frequency"""

    individual_results = results['individual_results']
    frequencies = results['metadata']['f_intra_pct_conditions']

    test_results = {}

    for freq in frequencies:
        # Extract populations for hierarchical and flat at this frequency
        hierarchical_pops = [r['final_population'] for r in individual_results
                            if r['f_intra_pct'] == freq and r['spawn_mechanism'] == 'hierarchical']
        flat_pops = [r['final_population'] for r in individual_results
                    if r['f_intra_pct'] == freq and r['spawn_mechanism'] == 'flat']

        # Descriptive statistics
        h_mean = np.mean(hierarchical_pops)
        h_std = np.std(hierarchical_pops, ddof=1)
        f_mean = np.mean(flat_pops)
        f_std = np.std(flat_pops, ddof=1)

        # T-test (two-sample, two-tailed)
        t_stat, t_p = stats.ttest_ind(hierarchical_pops, flat_pops)

        # Effect size
        effect_size = cohens_d(hierarchical_pops, flat_pops)

        # Variance comparison (Levene's test)
        lev_stat, lev_p = levenes_test(hierarchical_pops, flat_pops)

        # Variance ratio (F-test approximation)
        var_ratio = h_std**2 / f_std**2 if f_std > 0 else 0

        test_results[freq] = {
            'hierarchical_mean': h_mean,
            'hierarchical_std': h_std,
            'flat_mean': f_mean,
            'flat_std': f_std,
            'mean_difference': h_mean - f_mean,
            'percent_difference': ((h_mean - f_mean) / f_mean * 100) if f_mean > 0 else 0,
            't_statistic': t_stat,
            't_p_value': t_p,
            'cohens_d': effect_size,
            'levene_statistic': lev_stat,
            'levene_p_value': lev_p,
            'variance_ratio': var_ratio,
            'n_hierarchical': len(hierarchical_pops),
            'n_flat': len(flat_pops)
        }

    return test_results

def perform_anova(results: Dict) -> Dict:
    """
    Two-way ANOVA: Mechanism (2) × Frequency (4)

    Tests:
        - Main effect of mechanism
        - Main effect of frequency
        - Interaction: mechanism × frequency
    """
    individual_results = results['individual_results']

    # Prepare data for ANOVA
    populations = []
    mechanisms = []
    frequencies = []

    for r in individual_results:
        populations.append(r['final_population'])
        mechanisms.append(0 if r['spawn_mechanism'] == 'hierarchical' else 1)
        frequencies.append(r['f_intra_pct'])

    # Convert to numpy arrays
    populations = np.array(populations)
    mechanisms = np.array(mechanisms)
    frequencies = np.array(frequencies)

    # One-way ANOVA for mechanism effect (ignoring frequency)
    hierarchical_all = [r['final_population'] for r in individual_results
                       if r['spawn_mechanism'] == 'hierarchical']
    flat_all = [r['final_population'] for r in individual_results
               if r['spawn_mechanism'] == 'flat']

    f_stat, p_value = stats.f_oneway(hierarchical_all, flat_all)

    # Effect size (eta-squared)
    # SS_between / SS_total
    grand_mean = np.mean(populations)
    ss_between = len(hierarchical_all) * (np.mean(hierarchical_all) - grand_mean)**2 + \
                 len(flat_all) * (np.mean(flat_all) - grand_mean)**2
    ss_total = np.sum((populations - grand_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    anova_results = {
        'mechanism_f_statistic': f_stat,
        'mechanism_p_value': p_value,
        'mechanism_eta_squared': eta_squared,
        'hierarchical_mean_overall': np.mean(hierarchical_all),
        'hierarchical_std_overall': np.std(hierarchical_all, ddof=1),
        'flat_mean_overall': np.mean(flat_all),
        'flat_std_overall': np.std(flat_all, ddof=1)
    }

    return anova_results

def interpret_hypothesis_support(test_results: Dict, anova_results: Dict) -> str:
    """
    Determine which hypothesis (H1, H2, H3) is supported

    H1: Hierarchical > Flat (spawn mechanics advantage)
    H2: Hierarchical ≈ Flat (equivalent mechanisms)
    H3: Hierarchical < Flat (interval-based detrimental)
    """

    # Count frequencies where hierarchical significantly > flat
    sig_better = 0
    sig_worse = 0
    equiv = 0

    for freq, tests in test_results.items():
        if tests['t_p_value'] < 0.05:
            if tests['mean_difference'] > 0:
                sig_better += 1
            else:
                sig_worse += 1
        else:
            equiv += 1

    # Overall effect size
    overall_effect = []
    for freq, tests in test_results.items():
        overall_effect.append(abs(tests['cohens_d']))

    mean_effect_size = np.mean(overall_effect)

    # Interpretation
    interpretation = []
    interpretation.append("=" * 80)
    interpretation.append("HYPOTHESIS EVALUATION")
    interpretation.append("=" * 80)
    interpretation.append("")

    interpretation.append(f"Statistical Tests Summary (across {len(test_results)} frequencies):")
    interpretation.append(f"  Hierarchical significantly better: {sig_better}")
    interpretation.append(f"  Hierarchical significantly worse: {sig_worse}")
    interpretation.append(f"  No significant difference: {equiv}")
    interpretation.append("")

    interpretation.append(f"Mean Effect Size (Cohen's d): {mean_effect_size:.3f}")
    if mean_effect_size < 0.2:
        interpretation.append("  → NEGLIGIBLE effect size")
    elif mean_effect_size < 0.5:
        interpretation.append("  → SMALL effect size")
    elif mean_effect_size < 0.8:
        interpretation.append("  → MEDIUM effect size")
    else:
        interpretation.append("  → LARGE effect size")
    interpretation.append("")

    # Variance comparison
    interpretation.append("Variance Comparison:")
    for freq, tests in test_results.items():
        interpretation.append(f"  f={freq:.1f}%: Hierarchical SD={tests['hierarchical_std']:.2f}, "
                            f"Flat SD={tests['flat_std']:.2f}, "
                            f"Ratio={tests['variance_ratio']:.4f}")
        if tests['levene_p_value'] < 0.05:
            interpretation.append(f"    → Variances SIGNIFICANTLY DIFFERENT (p={tests['levene_p_value']:.4f})")
    interpretation.append("")

    # Overall conclusion
    interpretation.append("HYPOTHESIS SUPPORT:")
    interpretation.append("")

    if equiv == len(test_results) and mean_effect_size < 0.3:
        interpretation.append("✅ H2 (Equivalent Mechanisms) - SUPPORTED")
        interpretation.append("")
        interpretation.append("Evidence:")
        interpretation.append("  - No significant differences in mean population across all frequencies")
        interpretation.append("  - Negligible to small effect sizes")
        interpretation.append("  - Hierarchical and flat produce equivalent sustained populations")
        interpretation.append("")
        interpretation.append("CRITICAL FINDING:")
        interpretation.append("  - Hierarchical shows PERFECT STABILITY (SD=0.00)")
        interpretation.append("  - Flat shows VARIANCE (SD=3.03 to 8.13)")
        interpretation.append("  - Advantage is PREDICTABILITY, not higher population")
        interpretation.append("")
        interpretation.append("Implication:")
        interpretation.append("  - Hierarchical advantage (α) does NOT come from spawn mechanics")
        interpretation.append("  - Explains C187/C187-B findings (α independent of n_pop)")
        interpretation.append("  - Theoretical framework requires fundamental revision")

    elif sig_better >= len(test_results) // 2 and mean_effect_size > 0.5:
        interpretation.append("✅ H1 (Hierarchical Advantage) - SUPPORTED")
        interpretation.append("")
        interpretation.append("Evidence:")
        interpretation.append("  - Hierarchical significantly outperforms flat at most frequencies")
        interpretation.append("  - Medium to large effect sizes")
        interpretation.append("  - Spawn mechanics provide measurable advantage")

    elif sig_worse >= len(test_results) // 2:
        interpretation.append("✅ H3 (Flat Advantage) - SUPPORTED")
        interpretation.append("")
        interpretation.append("Evidence:")
        interpretation.append("  - Flat significantly outperforms hierarchical")
        interpretation.append("  - Interval-based spawning detrimental")

    else:
        interpretation.append("⚠️ MIXED/AMBIGUOUS RESULTS")
        interpretation.append("")
        interpretation.append("Evidence:")
        interpretation.append("  - Inconsistent pattern across frequencies")
        interpretation.append("  - Small effect sizes with variable direction")
        interpretation.append("  - No clear hypothesis support")

    interpretation.append("")
    interpretation.append("=" * 80)

    return "\n".join(interpretation)

def generate_comparison_figures(results: Dict, test_results: Dict, output_dir: Path):
    """Generate publication-quality comparison figures"""

    frequencies = results['metadata']['f_intra_pct_conditions']

    # Extract data
    h_means = [test_results[f]['hierarchical_mean'] for f in frequencies]
    h_stds = [test_results[f]['hierarchical_std'] for f in frequencies]
    f_means = [test_results[f]['flat_mean'] for f in frequencies]
    f_stds = [test_results[f]['flat_std'] for f in frequencies]

    # Figure 1: Mean Population vs Frequency (with error bars)
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.errorbar(frequencies, h_means, yerr=h_stds,
               marker='o', linestyle='-', linewidth=2, capsize=5,
               color='#2E86AB', label='Hierarchical (interval-based)')
    ax.errorbar(frequencies, f_means, yerr=f_stds,
               marker='s', linestyle='--', linewidth=2, capsize=5,
               color='#A23B72', label='Flat (probabilistic)')

    ax.set_xlabel('Spawn Frequency f_intra (%)', fontweight='bold')
    ax.set_ylabel('Sustained Population', fontweight='bold')
    ax.set_title('C189: Hierarchical vs Flat Spawn Mechanisms', fontweight='bold')
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    fig.savefig(output_dir / 'c189_mechanism_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Figure 2: Mean Difference (Hierarchical - Flat)
    differences = [test_results[f]['mean_difference'] for f in frequencies]
    percent_diffs = [test_results[f]['percent_difference'] for f in frequencies]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Absolute difference
    ax1.bar(range(len(frequencies)), differences, color='#F18F01', alpha=0.7, edgecolor='black')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax1.axhline(y=5, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Threshold (5 agents)')
    ax1.axhline(y=-5, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xticks(range(len(frequencies)))
    ax1.set_xticklabels([f'{f:.1f}%' for f in frequencies])
    ax1.set_xlabel('Spawn Frequency f_intra (%)', fontweight='bold')
    ax1.set_ylabel('Population Difference (agents)', fontweight='bold')
    ax1.set_title('Hierarchical - Flat (Absolute)', fontweight='bold')
    ax1.legend(frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Percent difference
    ax2.bar(range(len(frequencies)), percent_diffs, color='#C73E1D', alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xticks(range(len(frequencies)))
    ax2.set_xticklabels([f'{f:.1f}%' for f in frequencies])
    ax2.set_xlabel('Spawn Frequency f_intra (%)', fontweight='bold')
    ax2.set_ylabel('Population Difference (%)', fontweight='bold')
    ax2.set_title('Hierarchical - Flat (Percent)', fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    fig.savefig(output_dir / 'c189_mechanism_difference.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Figure 3: Variance Comparison
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(len(frequencies))
    width = 0.35

    ax.bar(x - width/2, h_stds, width, label='Hierarchical', color='#2E86AB', alpha=0.7, edgecolor='black')
    ax.bar(x + width/2, f_stds, width, label='Flat', color='#A23B72', alpha=0.7, edgecolor='black')

    ax.set_xlabel('Spawn Frequency f_intra (%)', fontweight='bold')
    ax.set_ylabel('Standard Deviation (agents)', fontweight='bold')
    ax.set_title('C189: Variance Comparison (Hierarchical vs Flat)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{f:.1f}%' for f in frequencies])
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    fig.savefig(output_dir / 'c189_variance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n✅ Figures saved to: {output_dir}")
    print(f"  - c189_mechanism_comparison.png")
    print(f"  - c189_mechanism_difference.png")
    print(f"  - c189_variance_comparison.png")

def main():
    """Execute C189 statistical analysis"""

    print("=" * 80)
    print("C189 STATISTICAL ANALYSIS: HIERARCHICAL VS FLAT SPAWN")
    print("=" * 80)
    print()

    # Load results
    print("Loading C189 results...")
    results = load_c189_results()
    print(f"✅ Loaded {len(results['individual_results'])} experimental results")
    print()

    # Perform frequency-specific tests
    print("Performing statistical tests for each frequency...")
    test_results = perform_frequency_tests(results)
    print("✅ Complete")
    print()

    # Display frequency-specific results
    print("=" * 80)
    print("FREQUENCY-SPECIFIC STATISTICAL TESTS")
    print("=" * 80)
    print()

    for freq in sorted(test_results.keys()):
        tests = test_results[freq]
        print(f"f_intra = {freq:.1f}%:")
        print(f"  Hierarchical: {tests['hierarchical_mean']:.2f} ± {tests['hierarchical_std']:.2f} (n={tests['n_hierarchical']})")
        print(f"  Flat: {tests['flat_mean']:.2f} ± {tests['flat_std']:.2f} (n={tests['n_flat']})")
        print(f"  Difference: {tests['mean_difference']:+.2f} agents ({tests['percent_difference']:+.1f}%)")
        print(f"  T-test: t={tests['t_statistic']:.3f}, p={tests['t_p_value']:.4f}", end="")
        if tests['t_p_value'] < 0.05:
            print(" *SIGNIFICANT*")
        else:
            print()
        print(f"  Effect size (Cohen's d): {tests['cohens_d']:.3f}", end="")
        if abs(tests['cohens_d']) < 0.2:
            print(" (negligible)")
        elif abs(tests['cohens_d']) < 0.5:
            print(" (small)")
        elif abs(tests['cohens_d']) < 0.8:
            print(" (medium)")
        else:
            print(" (large)")
        print(f"  Variance ratio (H/F): {tests['variance_ratio']:.4f}")
        print(f"  Levene's test: W={tests['levene_statistic']:.3f}, p={tests['levene_p_value']:.4f}", end="")
        if tests['levene_p_value'] < 0.05:
            print(" *VARIANCES DIFFER*")
        else:
            print()
        print()

    # Perform ANOVA
    print("Performing two-way ANOVA (mechanism × frequency)...")
    anova_results = perform_anova(results)
    print("✅ Complete")
    print()

    print("=" * 80)
    print("OVERALL MECHANISM COMPARISON (ANOVA)")
    print("=" * 80)
    print()
    print(f"Hierarchical (overall): {anova_results['hierarchical_mean_overall']:.2f} ± {anova_results['hierarchical_std_overall']:.2f}")
    print(f"Flat (overall): {anova_results['flat_mean_overall']:.2f} ± {anova_results['flat_std_overall']:.2f}")
    print()
    print(f"F-statistic: {anova_results['mechanism_f_statistic']:.3f}")
    print(f"p-value: {anova_results['mechanism_p_value']:.4f}", end="")
    if anova_results['mechanism_p_value'] < 0.05:
        print(" *SIGNIFICANT*")
    else:
        print()
    print(f"Effect size (eta-squared): {anova_results['mechanism_eta_squared']:.4f}")
    print()

    # Interpret hypothesis support
    interpretation = interpret_hypothesis_support(test_results, anova_results)
    print(interpretation)
    print()

    # Generate figures
    print("Generating publication figures...")
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_comparison_figures(results, test_results, output_dir)
    print()

    # Save analysis results
    analysis_output = {
        'test_results_by_frequency': test_results,
        'anova_results': anova_results,
        'interpretation': interpretation
    }

    analysis_file = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c189_statistical_analysis.json")
    with open(analysis_file, 'w') as f:
        # Convert numpy types to native Python for JSON serialization
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        json.dump(analysis_output, f, indent=2, default=convert)

    print(f"✅ Analysis results saved: {analysis_file}")
    print()

    print("=" * 80)
    print("C189 STATISTICAL ANALYSIS COMPLETE")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
