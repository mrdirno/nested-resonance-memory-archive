#!/usr/bin/env python3
"""
Statistical Power Analysis for Validation Experiments

Purpose: Determine sample size (n) sufficiency for detecting effects in C186-C189

This module calculates statistical power for validation experiments, determining
whether n=10 seeds provides sufficient power to detect predicted effects.

Analyses:
1. Power for one-sample t-tests (Basin A suppression vs threshold)
2. Power for paired t-tests (hierarchical vs single-population)
3. Power for ANOVA (network topology effects)
4. Power for correlation tests (runtime vs complexity)
5. Effect size estimation from pilot data

The goal is to ensure experiments have >80% power to detect meaningful effects,
validating methodological rigor before publication.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1023
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import numpy as np
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class PowerAnalysisResult:
    """Container for power analysis result."""
    test_type: str  # "one_sample_t", "paired_t", "anova", "correlation"
    effect_size: float
    sample_size: int
    alpha: float  # Significance level (usually 0.05)
    power: float  # Probability of detecting effect (target: 0.80)
    recommended_n: Optional[int] = None  # Minimum n for 80% power
    notes: str = ""


def calculate_noncentrality_parameter(
    effect_size: float,
    sample_size: int,
    test_type: str
) -> float:
    """
    Calculate noncentrality parameter for power analysis.

    Args:
        effect_size: Cohen's d or equivalent
        sample_size: Number of observations
        test_type: Type of statistical test

    Returns:
        Noncentrality parameter
    """
    if test_type == "one_sample_t":
        # δ = d * sqrt(n)
        return effect_size * math.sqrt(sample_size)

    elif test_type == "paired_t":
        # δ = d * sqrt(n)
        return effect_size * math.sqrt(sample_size)

    elif test_type == "anova":
        # δ = f * sqrt(n)
        # where f = Cohen's f (convert from d: f = d/2 for 2 groups)
        f = effect_size / 2
        return f * math.sqrt(sample_size)

    elif test_type == "correlation":
        # Fisher's z transformation
        # δ = 0.5 * ln((1+r)/(1-r)) * sqrt(n-3)
        if abs(effect_size) >= 1.0:
            return float('inf')
        z = 0.5 * math.log((1 + effect_size) / (1 - effect_size))
        return z * math.sqrt(sample_size - 3)

    else:
        return 0.0


def estimate_power_one_sample_t(
    effect_size: float,
    sample_size: int,
    alpha: float = 0.05
) -> float:
    """
    Estimate statistical power for one-sample t-test.

    Uses noncentrality parameter approximation.

    Args:
        effect_size: Cohen's d (mean difference / SD)
        sample_size: Number of observations
        alpha: Significance level

    Returns:
        Estimated power (0.0-1.0)
    """
    # Calculate noncentrality parameter
    delta = calculate_noncentrality_parameter(effect_size, sample_size, "one_sample_t")

    # Approximate power using normal distribution
    # Critical value for two-tailed test
    z_crit = 1.96  # For alpha = 0.05

    # Power = P(reject H0 | H1 true)
    # = P(|Z| > z_crit - delta)
    power = 1 - normal_cdf(z_crit - delta) + normal_cdf(-z_crit - delta)

    return max(0.0, min(1.0, power))


def normal_cdf(z: float) -> float:
    """
    Approximate normal CDF using error function.

    Args:
        z: Z-score

    Returns:
        P(Z ≤ z)
    """
    # Approximation: CDF(z) ≈ 0.5 * (1 + erf(z / sqrt(2)))
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def estimate_power_paired_t(
    effect_size: float,
    sample_size: int,
    alpha: float = 0.05
) -> float:
    """
    Estimate statistical power for paired t-test.

    Args:
        effect_size: Cohen's d for paired differences
        sample_size: Number of pairs
        alpha: Significance level

    Returns:
        Estimated power (0.0-1.0)
    """
    # Same as one-sample t-test for paired differences
    return estimate_power_one_sample_t(effect_size, sample_size, alpha)


def estimate_power_anova(
    effect_size: float,
    sample_size: int,
    num_groups: int,
    alpha: float = 0.05
) -> float:
    """
    Estimate statistical power for one-way ANOVA.

    Args:
        effect_size: Cohen's f (effect size for ANOVA)
        sample_size: Number of observations per group
        num_groups: Number of groups
        alpha: Significance level

    Returns:
        Estimated power (0.0-1.0)
    """
    # Total sample size
    n_total = sample_size * num_groups

    # Degrees of freedom
    df_between = num_groups - 1
    df_within = n_total - num_groups

    # Noncentrality parameter
    # λ = n * f^2
    lambda_param = sample_size * (effect_size ** 2)

    # Approximate power
    # For simplicity, use same approach as t-test
    # (Full implementation would use F-distribution)
    delta = math.sqrt(lambda_param)
    z_crit = 1.96  # Approximate for alpha = 0.05

    power = 1 - normal_cdf(z_crit - delta)

    return max(0.0, min(1.0, power))


def estimate_power_correlation(
    effect_size: float,
    sample_size: int,
    alpha: float = 0.05
) -> float:
    """
    Estimate statistical power for Pearson correlation test.

    Args:
        effect_size: Expected correlation coefficient r
        sample_size: Number of observations
        alpha: Significance level

    Returns:
        Estimated power (0.0-1.0)
    """
    if sample_size < 4:
        return 0.0

    # Fisher's z transformation
    delta = calculate_noncentrality_parameter(effect_size, sample_size, "correlation")

    z_crit = 1.96  # For alpha = 0.05

    power = 1 - normal_cdf(z_crit - delta) + normal_cdf(-z_crit - delta)

    return max(0.0, min(1.0, power))


def calculate_required_n(
    effect_size: float,
    test_type: str,
    target_power: float = 0.80,
    alpha: float = 0.05,
    num_groups: int = 2,
    max_n: int = 100
) -> int:
    """
    Calculate minimum n required to achieve target power.

    Args:
        effect_size: Expected effect size (Cohen's d, f, or r)
        test_type: Type of statistical test
        target_power: Desired power (usually 0.80)
        alpha: Significance level
        num_groups: Number of groups (for ANOVA)
        max_n: Maximum n to search

    Returns:
        Minimum sample size to achieve target power
    """
    # Binary search for minimum n
    low, high = 2, max_n

    while low < high:
        mid = (low + high) // 2

        # Calculate power for this n
        if test_type == "one_sample_t":
            power = estimate_power_one_sample_t(effect_size, mid, alpha)
        elif test_type == "paired_t":
            power = estimate_power_paired_t(effect_size, mid, alpha)
        elif test_type == "anova":
            power = estimate_power_anova(effect_size, mid, num_groups, alpha)
        elif test_type == "correlation":
            power = estimate_power_correlation(effect_size, mid, alpha)
        else:
            return max_n

        if power >= target_power:
            high = mid
        else:
            low = mid + 1

    return low


def analyze_basin_a_suppression_power(
    observed_mean: float,
    observed_sd: float,
    threshold: float,
    sample_size: int
) -> PowerAnalysisResult:
    """
    Power analysis for Basin A suppression test.

    H0: μ = threshold (5%)
    H1: μ < threshold

    Args:
        observed_mean: Observed mean Basin A %
        observed_sd: Observed standard deviation
        threshold: Threshold value (5%)
        sample_size: Current n

    Returns:
        PowerAnalysisResult
    """
    # Cohen's d = (threshold - observed_mean) / observed_sd
    # For suppression, we expect mean << threshold
    if observed_sd == 0:
        # Perfect suppression, infinite effect size
        effect_size = 10.0  # Arbitrarily large
    else:
        effect_size = abs(threshold - observed_mean) / observed_sd

    power = estimate_power_one_sample_t(effect_size, sample_size, alpha=0.05)

    recommended_n = None
    if power < 0.80:
        recommended_n = calculate_required_n(effect_size, "one_sample_t", target_power=0.80)

    notes = f"Testing H0: μ={threshold}% vs H1: μ<{threshold}%. Observed: μ={observed_mean:.2f}%, SD={observed_sd:.2f}%"

    return PowerAnalysisResult(
        test_type="one_sample_t",
        effect_size=effect_size,
        sample_size=sample_size,
        alpha=0.05,
        power=power,
        recommended_n=recommended_n,
        notes=notes
    )


def analyze_migration_consistency_power(
    observed_mean: float,
    observed_sd: float,
    predicted_range: Tuple[float, float],
    sample_size: int
) -> PowerAnalysisResult:
    """
    Power analysis for migration frequency test.

    H0: μ outside [min, max] range
    H1: μ within [min, max] range

    Args:
        observed_mean: Observed mean migrations
        observed_sd: Observed standard deviation
        predicted_range: (min, max) predicted range
        sample_size: Current n

    Returns:
        PowerAnalysisResult
    """
    min_val, max_val = predicted_range

    # Distance from nearest boundary
    if observed_mean < min_val:
        distance = min_val - observed_mean
    elif observed_mean > max_val:
        distance = observed_mean - max_val
    else:
        # Within range, distance to nearest boundary
        distance = min(observed_mean - min_val, max_val - observed_mean)

    # Effect size based on distance
    if observed_sd == 0:
        effect_size = 10.0 if distance == 0 else 0.0
    else:
        effect_size = abs(distance) / observed_sd

    power = estimate_power_one_sample_t(effect_size, sample_size, alpha=0.05)

    recommended_n = None
    if power < 0.80:
        recommended_n = calculate_required_n(effect_size, "one_sample_t", target_power=0.80)

    notes = f"Testing H1: μ∈[{min_val},{max_val}]. Observed: μ={observed_mean:.2f}, SD={observed_sd:.2f}"

    return PowerAnalysisResult(
        test_type="one_sample_t",
        effect_size=effect_size,
        sample_size=sample_size,
        alpha=0.05,
        power=power,
        recommended_n=recommended_n,
        notes=notes
    )


def analyze_network_topology_power(
    group_means: List[float],
    pooled_sd: float,
    sample_size_per_group: int
) -> PowerAnalysisResult:
    """
    Power analysis for network topology ANOVA.

    H0: μ_ring = μ_star = μ_fully_connected
    H1: At least one μ differs

    Args:
        group_means: List of group means
        pooled_sd: Pooled standard deviation across groups
        sample_size_per_group: n per group

    Returns:
        PowerAnalysisResult
    """
    num_groups = len(group_means)

    # Cohen's f = SD_between / SD_within
    # SD_between = sqrt(sum((μ_i - μ_grand)^2) / k)
    grand_mean = statistics.mean(group_means)

    if pooled_sd == 0:
        effect_size = 10.0
    else:
        variance_between = sum((m - grand_mean)**2 for m in group_means) / num_groups
        sd_between = math.sqrt(variance_between)
        effect_size = sd_between / pooled_sd  # Cohen's f

    power = estimate_power_anova(effect_size, sample_size_per_group, num_groups, alpha=0.05)

    recommended_n = None
    if power < 0.80:
        recommended_n = calculate_required_n(
            effect_size, "anova", target_power=0.80, num_groups=num_groups
        )

    notes = f"ANOVA with {num_groups} groups. Means: {group_means}, Pooled SD: {pooled_sd:.2f}"

    return PowerAnalysisResult(
        test_type="anova",
        effect_size=effect_size,
        sample_size=sample_size_per_group,
        alpha=0.05,
        power=power,
        recommended_n=recommended_n,
        notes=notes
    )


def analyze_runtime_correlation_power(
    expected_correlation: float,
    sample_size: int
) -> PowerAnalysisResult:
    """
    Power analysis for runtime vs complexity correlation.

    H0: ρ = 0
    H1: ρ ≠ 0

    Args:
        expected_correlation: Expected Pearson r
        sample_size: Number of observations

    Returns:
        PowerAnalysisResult
    """
    effect_size = expected_correlation

    power = estimate_power_correlation(effect_size, sample_size, alpha=0.05)

    recommended_n = None
    if power < 0.80:
        recommended_n = calculate_required_n(effect_size, "correlation", target_power=0.80)

    notes = f"Testing H0: ρ=0 vs H1: ρ≠0. Expected r={expected_correlation:.2f}"

    return PowerAnalysisResult(
        test_type="correlation",
        effect_size=effect_size,
        sample_size=sample_size,
        alpha=0.05,
        power=power,
        recommended_n=recommended_n,
        notes=notes
    )


def generate_power_analysis_report(results: List[PowerAnalysisResult]) -> str:
    """
    Generate markdown power analysis report.

    Args:
        results: List of PowerAnalysisResult objects

    Returns:
        Markdown formatted report
    """
    report = []

    report.append("# Statistical Power Analysis")
    report.append("")
    report.append("**Purpose:** Determine sample size sufficiency for detecting predicted effects")
    report.append("**Target:** Power ≥80% (80% probability of detecting real effects)")
    report.append("**Significance Level:** α=0.05")
    report.append("")

    # Summary table
    report.append("## Power Summary")
    report.append("")
    report.append("| Test | Effect Size | n | Power | Adequate? | Recommended n |")
    report.append("|------|-------------|---|-------|-----------|---------------|")

    for result in results:
        adequate = "✅ Yes" if result.power >= 0.80 else "⚠️ No"
        rec_n = f"{result.recommended_n}" if result.recommended_n else "N/A"

        report.append(f"| {result.test_type} | {result.effect_size:.3f} | {result.sample_size} | {result.power:.1%} | {adequate} | {rec_n} |")

    report.append("")

    # Detailed results
    report.append("## Detailed Analysis")
    report.append("")

    for i, result in enumerate(results, 1):
        report.append(f"### Test {i}: {result.test_type.replace('_', ' ').title()}")
        report.append("")
        report.append(f"- **Effect Size**: {result.effect_size:.3f}")
        report.append(f"- **Sample Size**: n={result.sample_size}")
        report.append(f"- **Alpha**: {result.alpha}")
        report.append(f"- **Power**: {result.power:.1%}")

        if result.power >= 0.80:
            report.append(f"- **Adequacy**: ✅ Sufficient (power ≥80%)")
        else:
            report.append(f"- **Adequacy**: ⚠️ Underpowered (power <80%)")
            if result.recommended_n:
                report.append(f"- **Recommended n**: {result.recommended_n} (to achieve 80% power)")

        report.append(f"- **Notes**: {result.notes}")
        report.append("")

    # Interpretation
    report.append("## Interpretation")
    report.append("")

    adequate_count = sum(1 for r in results if r.power >= 0.80)
    total_count = len(results)

    if adequate_count == total_count:
        report.append(f"✅ **All tests adequately powered** ({adequate_count}/{total_count})")
        report.append("")
        report.append("Current sample sizes provide >80% power to detect all predicted effects.")
        report.append("Methodology is statistically rigorous for publication.")
    else:
        report.append(f"⚠️ **Some tests underpowered** ({adequate_count}/{total_count} adequate)")
        report.append("")
        report.append("Recommendations:")

        for result in results:
            if result.power < 0.80 and result.recommended_n:
                report.append(f"- **{result.test_type}**: Increase n from {result.sample_size} to {result.recommended_n}")

        report.append("")

    report.append("---")
    report.append("")
    report.append("**Generated:** 2025-11-05 (Cycle 1023)")
    report.append("**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>")
    report.append("**Co-Authored-By:** Claude <noreply@anthropic.com>")

    return "\n".join(report)


def main():
    """Generate power analysis for C186-C189 validation experiments."""

    print("==" * 40)
    print("STATISTICAL POWER ANALYSIS")
    print("==" * 40)
    print()

    results = []

    # C186: Basin A Suppression (n=10)
    # Observed: mean=0%, SD=0% (perfect suppression)
    # Predicted: ≤5%
    basin_a_power = analyze_basin_a_suppression_power(
        observed_mean=0.0,
        observed_sd=0.1,  # Assume small SD for conservative estimate
        threshold=5.0,
        sample_size=10
    )
    results.append(basin_a_power)

    print("Basin A Suppression Test:")
    print(f"  Effect size: {basin_a_power.effect_size:.3f}")
    print(f"  Power: {basin_a_power.power:.1%}")
    print()

    # C186: Migration Consistency (n=10)
    # Observed: mean=14, SD=0
    # Predicted: 10-20
    migration_power = analyze_migration_consistency_power(
        observed_mean=14.0,
        observed_sd=2.0,  # Assume moderate SD
        predicted_range=(10.0, 20.0),
        sample_size=10
    )
    results.append(migration_power)

    print("Migration Consistency Test:")
    print(f"  Effect size: {migration_power.effect_size:.3f}")
    print(f"  Power: {migration_power.power:.1%}")
    print()

    # C187: Network Topology ANOVA (n=10 per group, 3 groups)
    # Assume moderate effect: Ring=10, Star=5, Fully-connected=2 (Basin A %)
    topology_power = analyze_network_topology_power(
        group_means=[10.0, 5.0, 2.0],
        pooled_sd=3.0,
        sample_size_per_group=10
    )
    results.append(topology_power)

    print("Network Topology ANOVA:")
    print(f"  Effect size (Cohen's f): {topology_power.effect_size:.3f}")
    print(f"  Power: {topology_power.power:.1%}")
    print()

    # Runtime-CV Correlation (n=10)
    # Expected strong correlation: r=0.7
    correlation_power = analyze_runtime_correlation_power(
        expected_correlation=0.7,
        sample_size=10
    )
    results.append(correlation_power)

    print("Runtime-CV Correlation Test:")
    print(f"  Expected r: {correlation_power.effect_size:.2f}")
    print(f"  Power: {correlation_power.power:.1%}")
    print()

    # Generate report
    report = generate_power_analysis_report(results)

    # Save to file
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/archive/analysis/STATISTICAL_POWER_ANALYSIS.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✅ Power analysis report saved to: {output_path}")
    print()
    print("==" * 40)


if __name__ == "__main__":
    main()
