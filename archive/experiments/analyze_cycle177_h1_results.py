#!/usr/bin/env python3
"""
Cycle 177 Hypothesis 1 (Energy Pooling) Results Analysis

Analyzes experimental results from C177 H1 energy pooling experiment comparing
BASELINE (no pooling) vs POOLING (cooperative energy sharing) conditions.

Statistical tests:
- Independent samples t-test (BASELINE vs POOLING)
- Cohen's d effect size
- Hypothesis outcome classification

Author: Claude (DUALITY-ZERO-V2)
Principal Investigator: Aldrin Payopay
Date: 2025-10-26 (Cycle 227)
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path
from typing import Dict, List, Tuple


def load_results(results_file: str) -> Dict:
    """Load C177 H1 experimental results JSON."""
    with open(results_file, 'r') as f:
        return json.load(f)


def calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Calculate Cohen's d effect size between two groups.

    Interpretation:
    - d < 0.2: negligible
    - d = 0.2-0.5: small
    - d = 0.5-0.8: medium
    - d > 0.8: large
    - d > 1.2: very large
    - d > 1.5: huge
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (mean2 - mean1) / pooled_std


def classify_hypothesis_outcome(
    t_stat: float,
    p_value: float,
    cohens_d: float,
    baseline_mean: float,
    pooling_mean: float
) -> Tuple[str, str]:
    """
    Classify hypothesis outcome based on statistical tests.

    Returns:
        (outcome, interpretation) tuple

    Outcomes:
        STRONGLY CONFIRMED: p < 0.001, d > 1.5
        CONFIRMED: p < 0.01, d > 0.8
        MARGINAL SUPPORT: p < 0.05, d > 0.5
        REJECTED: p >= 0.05 or d < 0.5
    """
    # Check direction (pooling should increase population)
    if pooling_mean <= baseline_mean:
        return (
            "REJECTED",
            f"Energy pooling did not increase population. "
            f"POOLING mean ({pooling_mean:.2f}) ≤ BASELINE mean ({baseline_mean:.2f}). "
            f"Hypothesis direction violated."
        )

    # Classify based on p-value and effect size
    if p_value < 0.001 and cohens_d > 1.5:
        return (
            "STRONGLY CONFIRMED",
            f"Energy pooling dramatically increased sustained population "
            f"({baseline_mean:.2f} → {pooling_mean:.2f}). "
            f"Statistical significance: p = {p_value:.4f} (< 0.001). "
            f"Effect size: Cohen's d = {cohens_d:.2f} (huge effect). "
            f"Single-parent bottleneck successfully eliminated through cooperative energy sharing."
        )

    elif p_value < 0.01 and cohens_d > 0.8:
        return (
            "CONFIRMED",
            f"Energy pooling significantly increased sustained population "
            f"({baseline_mean:.2f} → {pooling_mean:.2f}). "
            f"Statistical significance: p = {p_value:.4f} (< 0.01). "
            f"Effect size: Cohen's d = {cohens_d:.2f} (large effect). "
            f"Single-parent bottleneck partially addressed, may require synergistic combinations."
        )

    elif p_value < 0.05 and cohens_d > 0.5:
        return (
            "MARGINAL SUPPORT",
            f"Energy pooling showed modest increase in sustained population "
            f"({baseline_mean:.2f} → {pooling_mean:.2f}). "
            f"Statistical significance: p = {p_value:.4f} (< 0.05). "
            f"Effect size: Cohen's d = {cohens_d:.2f} (medium effect). "
            f"Effect present but insufficient for full population sustainability. "
            f"Synergistic combinations recommended (H1+H2, H1+H4, H1+H5)."
        )

    else:
        return (
            "REJECTED",
            f"Energy pooling showed no significant effect on sustained population. "
            f"Mean change: {baseline_mean:.2f} → {pooling_mean:.2f}. "
            f"Statistical significance: p = {p_value:.4f} (not significant). "
            f"Effect size: Cohen's d = {cohens_d:.2f} (negligible to small). "
            f"Single-parent bottleneck NOT the primary constraint limiting populations. "
            f"Alternative hypotheses (H2, H4, H5) or architectural changes required."
        )


def analyze_energy_pooling_experiment(results: Dict) -> Dict:
    """
    Complete statistical analysis of C177 H1 results.

    Returns:
        Dictionary with analysis results and interpretation
    """
    # Extract condition data
    baseline_results = [r for r in results['experiments'] if r['condition'] == 'BASELINE']
    pooling_results = [r for r in results['experiments'] if r['condition'] == 'POOLING']

    # Extract primary metric: mean population
    baseline_pops = [r['mean_population'] for r in baseline_results]
    pooling_pops = [r['mean_population'] for r in pooling_results]

    # Descriptive statistics
    baseline_mean = np.mean(baseline_pops)
    baseline_std = np.std(baseline_pops, ddof=1)
    pooling_mean = np.mean(pooling_pops)
    pooling_std = np.std(pooling_pops, ddof=1)

    # Independent samples t-test (one-tailed: pooling > baseline)
    t_stat, p_value_two_tailed = stats.ttest_ind(pooling_pops, baseline_pops)
    p_value = p_value_two_tailed / 2  # One-tailed test

    # Effect size
    cohens_d = calculate_cohens_d(baseline_pops, pooling_pops)

    # Hypothesis outcome
    outcome, interpretation = classify_hypothesis_outcome(
        t_stat, p_value, cohens_d, baseline_mean, pooling_mean
    )

    # Secondary metrics
    baseline_births = [r['spawn_events'] for r in baseline_results]
    pooling_births = [r['spawn_events'] for r in pooling_results]
    baseline_deaths = [r['composition_events'] for r in baseline_results]
    pooling_deaths = [r['composition_events'] for r in pooling_results]

    # Birth rate comparison
    baseline_birth_rate = np.mean([b / 3000 for b in baseline_births])
    pooling_birth_rate = np.mean([b / 3000 for b in pooling_births])
    birth_rate_improvement = pooling_birth_rate / baseline_birth_rate if baseline_birth_rate > 0 else 0

    # Death rate comparison
    baseline_death_rate = np.mean([d / 3000 for d in baseline_deaths])
    pooling_death_rate = np.mean([d / 3000 for d in pooling_deaths])

    # Death-birth ratios
    baseline_db_ratio = baseline_death_rate / baseline_birth_rate if baseline_birth_rate > 0 else float('inf')
    pooling_db_ratio = pooling_death_rate / pooling_birth_rate if pooling_birth_rate > 0 else float('inf')

    # Compile analysis results
    analysis = {
        'hypothesis': 'H1 - Energy Pooling',
        'outcome': outcome,
        'interpretation': interpretation,
        'statistics': {
            'baseline': {
                'mean_population': baseline_mean,
                'std_population': baseline_std,
                'n': len(baseline_pops),
                'birth_rate': baseline_birth_rate,
                'death_rate': baseline_death_rate,
                'death_birth_ratio': baseline_db_ratio
            },
            'pooling': {
                'mean_population': pooling_mean,
                'std_population': pooling_std,
                'n': len(pooling_pops),
                'birth_rate': pooling_birth_rate,
                'death_rate': pooling_death_rate,
                'death_birth_ratio': pooling_db_ratio
            },
            't_test': {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            },
            'effect_size': {
                'cohens_d': cohens_d,
                'interpretation': (
                    'negligible' if abs(cohens_d) < 0.2 else
                    'small' if abs(cohens_d) < 0.5 else
                    'medium' if abs(cohens_d) < 0.8 else
                    'large' if abs(cohens_d) < 1.2 else
                    'very large' if abs(cohens_d) < 1.5 else
                    'huge'
                )
            },
            'improvements': {
                'population_change': pooling_mean - baseline_mean,
                'population_fold_change': pooling_mean / baseline_mean if baseline_mean > 0 else float('inf'),
                'birth_rate_improvement': birth_rate_improvement,
                'death_birth_ratio_change': pooling_db_ratio - baseline_db_ratio
            }
        }
    }

    return analysis


def generate_analysis_report(analysis: Dict) -> str:
    """Generate formatted analysis report."""
    stats = analysis['statistics']

    report = f"""
{'='*80}
CYCLE 177 HYPOTHESIS 1 (ENERGY POOLING) - RESULTS ANALYSIS
{'='*80}

HYPOTHESIS OUTCOME: {analysis['outcome']}

{analysis['interpretation']}

{'='*80}
STATISTICAL SUMMARY
{'='*80}

BASELINE (No Pooling):
  Mean Population:     {stats['baseline']['mean_population']:.2f} ± {stats['baseline']['std_population']:.2f} (n={stats['baseline']['n']})
  Birth Rate:          {stats['baseline']['birth_rate']:.4f} agents/cycle
  Death Rate:          {stats['baseline']['death_rate']:.4f} agents/cycle
  Death/Birth Ratio:   {stats['baseline']['death_birth_ratio']:.2f}×

POOLING (Cooperative Energy Sharing):
  Mean Population:     {stats['pooling']['mean_population']:.2f} ± {stats['pooling']['std_population']:.2f} (n={stats['pooling']['n']})
  Birth Rate:          {stats['pooling']['birth_rate']:.4f} agents/cycle
  Death Rate:          {stats['pooling']['death_rate']:.4f} agents/cycle
  Death/Birth Ratio:   {stats['pooling']['death_birth_ratio']:.2f}×

STATISTICAL TESTS:
  t-statistic:         {stats['t_test']['t_statistic']:.3f}
  p-value (one-tailed): {stats['t_test']['p_value']:.4f}
  Significant (α=0.05): {'YES' if stats['t_test']['significant'] else 'NO'}

EFFECT SIZE:
  Cohen's d:           {stats['effect_size']['cohens_d']:.2f}
  Interpretation:      {stats['effect_size']['interpretation'].upper()}

IMPROVEMENTS:
  Population Change:   {stats['improvements']['population_change']:+.2f} agents
  Population Fold Change: {stats['improvements']['population_fold_change']:.2f}×
  Birth Rate Improvement: {stats['improvements']['birth_rate_improvement']:.2f}×
  Death/Birth Ratio Change: {stats['improvements']['death_birth_ratio_change']:+.2f}

{'='*80}
"""
    return report


def main():
    """Execute C177 H1 results analysis."""
    # Load results
    results_file = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle177_h1_energy_pooling_results.json")

    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        print("Experiment may still be running.")
        return

    print("Loading C177 H1 results...")
    results = load_results(results_file)

    print("Performing statistical analysis...")
    analysis = analyze_energy_pooling_experiment(results)

    # Generate report
    report = generate_analysis_report(analysis)
    print(report)

    # Save analysis to file
    analysis_file = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/experiments/cycle177_h1_analysis.json")
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"Analysis saved to: {analysis_file}")

    # Recommendation
    if analysis['outcome'] in ['STRONGLY CONFIRMED', 'CONFIRMED']:
        print("\n" + "="*80)
        print("RECOMMENDATION: Integrate C177 results into Paper 2")
        print("  - Add Section 3.6: Energy Pooling Validation")
        print("  - Update Discussion 4.4.1 with empirical evidence")
        print("  - Generate population trajectory figure")
        print("="*80)
    elif analysis['outcome'] == 'MARGINAL SUPPORT':
        print("\n" + "="*80)
        print("RECOMMENDATION: Test synergistic combinations")
        print("  - H1+H2: Energy pooling + external sources")
        print("  - H1+H4: Energy pooling + composition throttling")
        print("  - H1+H5: Energy pooling + multi-generational recovery")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("RECOMMENDATION: Test alternative hypotheses")
        print("  - H2: External energy sources (task-based rewards)")
        print("  - H4: Composition throttling (density-dependent death)")
        print("  - H5: Multi-generational recovery (staggered spawning)")
        print("="*80)


if __name__ == "__main__":
    main()
