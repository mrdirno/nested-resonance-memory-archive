#!/usr/bin/env python3
"""
C190 Statistical Analysis: Variance Optimization

Tests four hypotheses about when stochastic variance improves system performance:
  H1: Deterministic superior in stable environments
  H2: Stochastic superior in noisy environments (robustness to parameter noise)
  H3: Hybrid optimal in dynamic environments (adaptation to time-varying parameters)
  H4: High variance optimal for exploration (diversity of outcomes)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08 (Cycle 1319, C190 Analysis)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import List, Dict, Tuple
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c190_variance_optimization.json")
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300
ALPHA_SIGNIFICANCE = 0.05

MECHANISM_ORDER = ['deterministic', 'hybrid_low', 'hybrid_mid', 'hybrid_high', 'flat']
MECHANISM_LABELS = {
    'deterministic': 'Deterministic\n(c=1.0)',
    'hybrid_low': 'Hybrid Low\n(c=0.75)',
    'hybrid_mid': 'Hybrid Mid\n(c=0.50)',
    'hybrid_high': 'Hybrid High\n(c=0.25)',
    'flat': 'Flat\n(prob.)',
}

ENVIRONMENT_ORDER = ['stable', 'noisy', 'dynamic', 'exploration']
ENVIRONMENT_LABELS = {
    'stable': 'Stable',
    'noisy': 'Noisy',
    'dynamic': 'Dynamic',
    'exploration': 'Exploration',
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_results() -> Dict:
    """Load C190 experimental results"""
    print("Loading C190 results...")
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    n_experiments = len(data['individual_results'])
    print(f"  Loaded {n_experiments} experiments")
    print(f"  Date: {data['date']}")
    print(f"  Cycles: {data['metadata']['cycles']}")
    print()

    return data

def organize_by_condition(results: List[Dict]) -> Dict[Tuple[str, str, float], List[float]]:
    """
    Organize results by (mechanism, environment, frequency)

    Returns:
        Dict mapping (mechanism, env, freq) → list of final populations
    """
    organized = defaultdict(list)

    for exp in results:
        key = (exp['spawn_mechanism'], exp['environment'], exp['f_intra_pct'])
        organized[key].append(exp['final_population'])

    return dict(organized)

# ============================================================================
# STATISTICAL TESTS
# ============================================================================

def welchs_ttest(group1: List[float], group2: List[float]) -> Tuple[float, float]:
    """
    Welch's t-test (unequal variances)

    Returns:
        (t_statistic, p_value)
    """
    return stats.ttest_ind(group1, group2, equal_var=False)

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

    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    return d

def levenes_test(*groups) -> Tuple[float, float]:
    """
    Levene's test for equality of variances

    Returns:
        (statistic, p_value)
    """
    return stats.levene(*groups)

def one_way_anova(*groups) -> Tuple[float, float]:
    """
    One-way ANOVA

    Returns:
        (F_statistic, p_value)
    """
    return stats.f_oneway(*groups)

# ============================================================================
# HYPOTHESIS TESTING
# ============================================================================

def test_h1_deterministic_stable(data: Dict) -> Dict:
    """
    H1: Deterministic superior in stable environments

    Test: Compare all mechanisms within stable environment
    Prediction: Deterministic > all others in mean population
    """
    print("=" * 80)
    print("HYPOTHESIS 1: Deterministic Superior in Stable Environment")
    print("=" * 80)
    print()

    results = {}

    # Test both frequencies
    for freq in [1.0, 2.0]:
        print(f"Testing f_intra = {freq}%:")
        print("-" * 40)

        # Get data for all mechanisms in stable environment
        mechanism_data = {}
        for mech in MECHANISM_ORDER:
            key = (mech, 'stable', freq)
            mechanism_data[mech] = data[key]

        # Print descriptive statistics
        for mech in MECHANISM_ORDER:
            pops = mechanism_data[mech]
            mean = np.mean(pops)
            std = np.std(pops, ddof=1)
            print(f"  {MECHANISM_LABELS[mech]:20s}: {mean:5.2f} ± {std:4.2f}")
        print()

        # Pairwise comparisons: deterministic vs others
        print("Pairwise Comparisons (Deterministic vs Others):")
        print()

        for mech in MECHANISM_ORDER[1:]:  # Skip deterministic
            det_pops = mechanism_data['deterministic']
            other_pops = mechanism_data[mech]

            t_stat, p_val = welchs_ttest(det_pops, other_pops)
            effect_size = cohens_d(det_pops, other_pops)

            print(f"  Deterministic vs {MECHANISM_LABELS[mech]}:")
            print(f"    t-statistic: {t_stat:+6.3f}")
            print(f"    p-value:     {p_val:7.4f} {'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'}")
            print(f"    Cohen's d:   {effect_size:+6.3f} ({'large' if abs(effect_size) >= 0.8 else 'medium' if abs(effect_size) >= 0.5 else 'small' if abs(effect_size) >= 0.2 else 'negligible'})")
            print()

        # ANOVA: overall mechanism effect
        groups = [mechanism_data[m] for m in MECHANISM_ORDER]
        F, p = one_way_anova(*groups)
        print(f"One-Way ANOVA (Mechanism Effect):")
        print(f"  F-statistic: {F:6.3f}")
        print(f"  p-value:     {p:7.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        print()

        # Levene's test: variance comparison
        W, p_lev = levenes_test(*groups)
        print(f"Levene's Test (Variance Equality):")
        print(f"  W-statistic: {W:6.3f}")
        print(f"  p-value:     {p_lev:7.4f} {'***' if p_lev < 0.001 else '**' if p_lev < 0.01 else '*' if p_lev < 0.05 else 'ns'}")
        print()

        results[freq] = {
            'mechanism_data': mechanism_data,
            'anova_F': F,
            'anova_p': p,
            'levene_W': W,
            'levene_p': p_lev,
        }

    print()
    return results

def test_h2_stochastic_noisy(data: Dict) -> Dict:
    """
    H2: Stochastic superior in noisy environments

    Test: Compare mechanisms within noisy environment
    Prediction: Stochastic/Hybrid > Deterministic (robustness to parameter noise)
    """
    print("=" * 80)
    print("HYPOTHESIS 2: Stochastic Superior in Noisy Environment")
    print("=" * 80)
    print()

    results = {}

    for freq in [1.0, 2.0]:
        print(f"Testing f_intra = {freq}%:")
        print("-" * 40)

        # Get data for all mechanisms in noisy environment
        mechanism_data = {}
        for mech in MECHANISM_ORDER:
            key = (mech, 'noisy', freq)
            mechanism_data[mech] = data[key]

        # Print descriptive statistics
        for mech in MECHANISM_ORDER:
            pops = mechanism_data[mech]
            mean = np.mean(pops)
            std = np.std(pops, ddof=1)
            print(f"  {MECHANISM_LABELS[mech]:20s}: {mean:5.2f} ± {std:4.2f}")
        print()

        # Test: Flat vs Deterministic (primary test of H2)
        det_pops = mechanism_data['deterministic']
        flat_pops = mechanism_data['flat']

        t_stat, p_val = welchs_ttest(flat_pops, det_pops)  # flat - deterministic
        effect_size = cohens_d(flat_pops, det_pops)

        print(f"Primary Test: Flat vs Deterministic")
        print(f"  t-statistic: {t_stat:+6.3f} ({'Flat > Det' if t_stat > 0 else 'Det > Flat'})")
        print(f"  p-value:     {p_val:7.4f} {'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'}")
        print(f"  Cohen's d:   {effect_size:+6.3f}")
        print()

        # ANOVA
        groups = [mechanism_data[m] for m in MECHANISM_ORDER]
        F, p = one_way_anova(*groups)
        print(f"One-Way ANOVA (Mechanism Effect):")
        print(f"  F-statistic: {F:6.3f}")
        print(f"  p-value:     {p:7.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        print()

        results[freq] = {
            'mechanism_data': mechanism_data,
            'flat_vs_det_t': t_stat,
            'flat_vs_det_p': p_val,
            'flat_vs_det_d': effect_size,
            'anova_F': F,
            'anova_p': p,
        }

    print()
    return results

def test_h3_hybrid_dynamic(data: Dict) -> Dict:
    """
    H3: Hybrid optimal in dynamic environments

    Test: Compare mechanisms within dynamic environment
    Prediction: Hybrid Mid > {Deterministic, Flat} (adaptation to time-varying)
    """
    print("=" * 80)
    print("HYPOTHESIS 3: Hybrid Optimal in Dynamic Environment")
    print("=" * 80)
    print()

    results = {}

    for freq in [1.0, 2.0]:
        print(f"Testing f_intra = {freq}%:")
        print("-" * 40)

        # Get data for all mechanisms in dynamic environment
        mechanism_data = {}
        for mech in MECHANISM_ORDER:
            key = (mech, 'dynamic', freq)
            mechanism_data[mech] = data[key]

        # Print descriptive statistics
        for mech in MECHANISM_ORDER:
            pops = mechanism_data[mech]
            mean = np.mean(pops)
            std = np.std(pops, ddof=1)
            print(f"  {MECHANISM_LABELS[mech]:20s}: {mean:5.2f} ± {std:4.2f}")
        print()

        # Test: Hybrid Mid vs Deterministic
        det_pops = mechanism_data['deterministic']
        hybrid_pops = mechanism_data['hybrid_mid']

        t_stat, p_val = welchs_ttest(hybrid_pops, det_pops)
        effect_size = cohens_d(hybrid_pops, det_pops)

        print(f"Hybrid Mid vs Deterministic:")
        print(f"  t-statistic: {t_stat:+6.3f} ({'Hybrid > Det' if t_stat > 0 else 'Det > Hybrid'})")
        print(f"  p-value:     {p_val:7.4f} {'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'}")
        print(f"  Cohen's d:   {effect_size:+6.3f}")
        print()

        # ANOVA
        groups = [mechanism_data[m] for m in MECHANISM_ORDER]
        F, p = one_way_anova(*groups)
        print(f"One-Way ANOVA (Mechanism Effect):")
        print(f"  F-statistic: {F:6.3f}")
        print(f"  p-value:     {p:7.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        print()

        results[freq] = {
            'mechanism_data': mechanism_data,
            'hybrid_vs_det_t': t_stat,
            'hybrid_vs_det_p': p_val,
            'hybrid_vs_det_d': effect_size,
            'anova_F': F,
            'anova_p': p,
        }

    print()
    return results

def test_h4_variance_exploration(data: Dict) -> Dict:
    """
    H4: High variance optimal for exploration

    Test: Exploration score = variance of final populations
    Prediction: Exploration score increases with mechanism variance
    """
    print("=" * 80)
    print("HYPOTHESIS 4: High Variance Optimal for Exploration")
    print("=" * 80)
    print()

    results = {}

    for freq in [1.0, 2.0]:
        print(f"Testing f_intra = {freq}%:")
        print("-" * 40)

        # Calculate exploration score (SD of final populations) for each mechanism
        exploration_scores = {}
        for mech in MECHANISM_ORDER:
            key = (mech, 'exploration', freq)
            pops = data[key]
            exploration_scores[mech] = np.std(pops, ddof=1)

        print("Exploration Scores (SD of outcomes):")
        for mech in MECHANISM_ORDER:
            score = exploration_scores[mech]
            print(f"  {MECHANISM_LABELS[mech]:20s}: {score:5.2f}")
        print()

        # Correlation: exploration score vs mechanism variance
        # Use certainty as proxy for expected variance
        certainty_values = {'deterministic': 1.0, 'hybrid_low': 0.75,
                           'hybrid_mid': 0.50, 'hybrid_high': 0.25, 'flat': 0.0}

        certainties = [certainty_values[m] for m in MECHANISM_ORDER]
        scores = [exploration_scores[m] for m in MECHANISM_ORDER]

        # Negative correlation expected (lower certainty = higher exploration)
        corr, p_val = stats.pearsonr(certainties, scores)

        print(f"Correlation (Certainty vs Exploration Score):")
        print(f"  Pearson r:   {corr:+6.3f} (expected negative)")
        print(f"  p-value:     {p_val:7.4f} {'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'}")
        print()

        results[freq] = {
            'exploration_scores': exploration_scores,
            'correlation_r': corr,
            'correlation_p': p_val,
        }

    print()
    return results

def test_environment_interaction(data: Dict) -> Dict:
    """
    Test Mechanism × Environment interaction

    Question: Does optimal mechanism depend on environment?
    """
    print("=" * 80)
    print("MECHANISM × ENVIRONMENT INTERACTION")
    print("=" * 80)
    print()

    results = {}

    for freq in [1.0, 2.0]:
        print(f"Testing f_intra = {freq}%:")
        print("-" * 40)

        # Organize data: mechanism × environment
        print("Mean Populations (Mechanism × Environment):")
        print()
        print(f"{'Mechanism':<20s} | {'Stable':>8s} | {'Noisy':>8s} | {'Dynamic':>8s} | {'Exploration':>11s}")
        print("-" * 80)

        mechanism_means = {}
        for mech in MECHANISM_ORDER:
            means = []
            for env in ENVIRONMENT_ORDER:
                key = (mech, env, freq)
                pops = data[key]
                mean = np.mean(pops)
                means.append(mean)
                print(f"{MECHANISM_LABELS[mech]:<20s} | {mean:8.2f} |", end='')
            print()
            mechanism_means[mech] = means
        print()

        # Check if environment has ANY effect
        print("Environment Effect Test:")
        for mech in MECHANISM_ORDER:
            env_groups = []
            for env in ENVIRONMENT_ORDER:
                key = (mech, env, freq)
                env_groups.append(data[key])

            F, p = one_way_anova(*env_groups)
            print(f"  {MECHANISM_LABELS[mech]:20s}: F={F:6.3f}, p={p:7.4f} {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")
        print()

        results[freq] = {
            'mechanism_means': mechanism_means,
        }

    print()
    return results

# ============================================================================
# FIGURES
# ============================================================================

def plot_mechanism_by_environment(data: Dict, output_dir: Path):
    """
    Figure 1: Mean Population vs Mechanism (by environment)
    4 subplots (one per environment)
    """
    print("Generating Figure 1: Mean Population vs Mechanism (by environment)...")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for idx, env in enumerate(ENVIRONMENT_ORDER):
        ax = axes[idx]

        # Get data for both frequencies
        for freq in [1.0, 2.0]:
            means = []
            sds = []
            for mech in MECHANISM_ORDER:
                key = (mech, env, freq)
                pops = data[key]
                means.append(np.mean(pops))
                sds.append(np.std(pops, ddof=1))

            x = np.arange(len(MECHANISM_ORDER))
            width = 0.35
            offset = -width/2 if freq == 1.0 else +width/2

            ax.bar(x + offset, means, width, yerr=sds,
                   label=f'f={freq}%', alpha=0.8, capsize=4)

        ax.set_xlabel('Spawn Mechanism', fontsize=10)
        ax.set_ylabel('Mean Final Population', fontsize=10)
        ax.set_title(f'{ENVIRONMENT_LABELS[env]} Environment', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([MECHANISM_LABELS[m] for m in MECHANISM_ORDER],
                          rotation=0, fontsize=8)
        ax.legend(fontsize=9)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    filepath = output_dir / "c190_fig1_mechanism_by_environment.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
    print(f"  Saved: {filepath}")
    plt.close()

def plot_variance_performance(data: Dict, output_dir: Path):
    """
    Figure 2: Variance vs Performance (all environments)
    Scatter plot: mechanism SD (x) vs mean population (y)
    Colors: environment type
    """
    print("Generating Figure 2: Variance vs Performance...")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for freq_idx, freq in enumerate([1.0, 2.0]):
        ax = axes[freq_idx]

        for env_idx, env in enumerate(ENVIRONMENT_ORDER):
            sds = []
            means = []

            for mech in MECHANISM_ORDER:
                key = (mech, env, freq)
                pops = data[key]
                sds.append(np.std(pops, ddof=1))
                means.append(np.mean(pops))

            ax.scatter(sds, means, label=ENVIRONMENT_LABELS[env],
                      s=100, alpha=0.7)

        ax.set_xlabel('Standard Deviation (Variance)', fontsize=11)
        ax.set_ylabel('Mean Final Population', fontsize=11)
        ax.set_title(f'f_intra = {freq}%', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)

    plt.tight_layout()

    filepath = output_dir / "c190_fig2_variance_performance.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
    print(f"  Saved: {filepath}")
    plt.close()

def plot_robustness_heatmap(data: Dict, output_dir: Path):
    """
    Figure 3: Robustness Heatmap
    X-axis: Mechanism
    Y-axis: Environment
    Color: Mean population (higher = better)
    """
    print("Generating Figure 3: Robustness Heatmap...")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for freq_idx, freq in enumerate([1.0, 2.0]):
        ax = axes[freq_idx]

        # Build matrix: environments (rows) × mechanisms (cols)
        matrix = np.zeros((len(ENVIRONMENT_ORDER), len(MECHANISM_ORDER)))

        for i, env in enumerate(ENVIRONMENT_ORDER):
            for j, mech in enumerate(MECHANISM_ORDER):
                key = (mech, env, freq)
                pops = data[key]
                matrix[i, j] = np.mean(pops)

        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Mean Population', fontsize=10)

        # Add text annotations
        for i in range(len(ENVIRONMENT_ORDER)):
            for j in range(len(MECHANISM_ORDER)):
                text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                             ha="center", va="center", color="black", fontsize=9)

        # Set labels
        ax.set_xticks(np.arange(len(MECHANISM_ORDER)))
        ax.set_yticks(np.arange(len(ENVIRONMENT_ORDER)))
        ax.set_xticklabels([MECHANISM_LABELS[m].replace('\n', ' ') for m in MECHANISM_ORDER],
                          rotation=45, ha='right', fontsize=9)
        ax.set_yticklabels([ENVIRONMENT_LABELS[e] for e in ENVIRONMENT_ORDER], fontsize=10)

        ax.set_title(f'f_intra = {freq}%', fontsize=12, fontweight='bold')
        ax.set_xlabel('Spawn Mechanism', fontsize=11)
        ax.set_ylabel('Environment', fontsize=11)

    plt.tight_layout()

    filepath = output_dir / "c190_fig3_robustness_heatmap.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
    print(f"  Saved: {filepath}")
    plt.close()

def plot_exploration_scores(data: Dict, output_dir: Path):
    """
    Figure 4: Exploration Score vs Mechanism
    Bar plot showing SD of outcomes for each mechanism
    """
    print("Generating Figure 4: Exploration Scores...")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for freq_idx, freq in enumerate([1.0, 2.0]):
        ax = axes[freq_idx]

        # Calculate exploration score (SD) for each mechanism
        scores = []
        for mech in MECHANISM_ORDER:
            key = (mech, 'exploration', freq)
            pops = data[key]
            scores.append(np.std(pops, ddof=1))

        x = np.arange(len(MECHANISM_ORDER))
        ax.bar(x, scores, alpha=0.8, color='steelblue')

        ax.set_xlabel('Spawn Mechanism', fontsize=11)
        ax.set_ylabel('Exploration Score (SD of Outcomes)', fontsize=11)
        ax.set_title(f'f_intra = {freq}%', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([MECHANISM_LABELS[m] for m in MECHANISM_ORDER],
                          rotation=0, fontsize=9)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    filepath = output_dir / "c190_fig4_exploration_scores.png"
    plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
    print(f"  Saved: {filepath}")
    plt.close()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 80)
    print("C190 STATISTICAL ANALYSIS: VARIANCE OPTIMIZATION")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Does stochastic variance improve system performance under specific conditions?")
    print()
    print("Hypotheses:")
    print("  H1: Deterministic superior in stable environments")
    print("  H2: Stochastic superior in noisy environments (robustness)")
    print("  H3: Hybrid optimal in dynamic environments (adaptation)")
    print("  H4: High variance optimal for exploration (diversity)")
    print()
    print("=" * 80)
    print()

    # Load data
    raw_data = load_results()
    data = organize_by_condition(raw_data['individual_results'])

    # Test hypotheses
    h1_results = test_h1_deterministic_stable(data)
    h2_results = test_h2_stochastic_noisy(data)
    h3_results = test_h3_hybrid_dynamic(data)
    h4_results = test_h4_variance_exploration(data)
    interaction_results = test_environment_interaction(data)

    # Generate figures
    print("=" * 80)
    print("GENERATING FIGURES")
    print("=" * 80)
    print()

    plot_mechanism_by_environment(data, OUTPUT_DIR)
    plot_variance_performance(data, OUTPUT_DIR)
    plot_robustness_heatmap(data, OUTPUT_DIR)
    plot_exploration_scores(data, OUTPUT_DIR)

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Figures saved to:", OUTPUT_DIR)
    print()

if __name__ == "__main__":
    main()
