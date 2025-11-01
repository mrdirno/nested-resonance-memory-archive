#!/usr/bin/env python3
"""
Statistical Validation of Phase Transition Discovery

Performs rigorous statistical tests on the initialization → steady-state
transition discovered in temporal evolution analysis.

Tests:
1. Two-sample t-test (initialization vs steady-state resonance rates)
2. Bootstrap confidence intervals for transition time
3. Effect size calculation (Cohen's d)
4. Levene's test for variance homogeneity
5. Mann-Whitney U test (non-parametric alternative)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class StatisticalResults:
    """Statistical test results."""
    # T-test
    t_statistic: float
    t_pvalue: float
    degrees_freedom: int

    # Effect size
    cohens_d: float
    effect_interpretation: str

    # Bootstrap CI for means
    init_mean_ci: Tuple[float, float]
    steady_mean_ci: Tuple[float, float]

    # Variance test
    levene_statistic: float
    levene_pvalue: float
    variance_equal: bool

    # Non-parametric test
    mannwhitney_u: float
    mannwhitney_pvalue: float


class StatisticalValidator:
    """Validate phase transition with rigorous statistical tests."""

    def __init__(self, data_path: Path):
        """Initialize with temporal analysis data."""
        self.data_path = data_path
        self.data = self.load_data()

    def load_data(self) -> Dict:
        """Load temporal evolution analysis results."""
        json_files = list(self.data_path.glob("temporal_analysis_*.json"))
        if not json_files:
            raise FileNotFoundError(f"No temporal analysis data in {self.data_path}")

        latest = sorted(json_files)[-1]
        with open(latest) as f:
            return json.load(f)

    def extract_regime_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract resonance rates for initialization vs steady-state regimes.

        Returns:
            (initialization_resonance, steady_state_resonance) arrays
        """
        windows = self.data['windows']

        # Initialization: windows 0-2 (0-146h)
        init_resonance = np.array([
            w['resonance_rate'] for w in windows[:3]
        ])

        # Steady-state: windows 3-4 (146-244h)
        steady_resonance = np.array([
            w['resonance_rate'] for w in windows[3:]
        ])

        return init_resonance, steady_resonance

    def ttest_independent(
        self,
        init: np.ndarray,
        steady: np.ndarray
    ) -> Tuple[float, float, int]:
        """
        Perform two-sample t-test.

        H0: Mean resonance rate is equal between regimes
        H1: Mean resonance rate differs between regimes

        Returns:
            (t_statistic, p_value, degrees_of_freedom)
        """
        # Welch's t-test (does not assume equal variance)
        result = stats.ttest_ind(init, steady, equal_var=False)

        # Degrees of freedom for Welch's t-test
        n1, n2 = len(init), len(steady)
        s1, s2 = np.var(init, ddof=1), np.var(steady, ddof=1)
        df = ((s1/n1 + s2/n2)**2) / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))

        return result.statistic, result.pvalue, int(df)

    def cohens_d(self, init: np.ndarray, steady: np.ndarray) -> float:
        """
        Calculate Cohen's d effect size.

        Cohen's d interpretation:
        - Small: d ~ 0.2
        - Medium: d ~ 0.5
        - Large: d ~ 0.8
        - Very large: d > 1.2

        Returns:
            Cohen's d value
        """
        mean1, mean2 = init.mean(), steady.mean()
        std1, std2 = init.std(ddof=1), steady.std(ddof=1)
        n1, n2 = len(init), len(steady)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))

        d = (mean1 - mean2) / pooled_std
        return d

    def interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        d_abs = abs(d)
        if d_abs < 0.2:
            return "negligible"
        elif d_abs < 0.5:
            return "small"
        elif d_abs < 0.8:
            return "medium"
        elif d_abs < 1.2:
            return "large"
        else:
            return "very large"

    def bootstrap_ci(
        self,
        data: np.ndarray,
        n_bootstrap: int = 10000,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval for mean.

        Args:
            data: Sample data
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (default 95%)

        Returns:
            (lower_bound, upper_bound) of CI
        """
        bootstrap_means = []
        n = len(data)

        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_means.append(sample.mean())

        bootstrap_means = np.array(bootstrap_means)
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_means, 100 * alpha/2)
        upper = np.percentile(bootstrap_means, 100 * (1 - alpha/2))

        return (lower, upper)

    def levene_test(self, init: np.ndarray, steady: np.ndarray) -> Tuple[float, float]:
        """
        Levene's test for equality of variances.

        H0: Variances are equal
        H1: Variances differ

        Returns:
            (statistic, p_value)
        """
        result = stats.levene(init, steady)
        return result.statistic, result.pvalue

    def mann_whitney(self, init: np.ndarray, steady: np.ndarray) -> Tuple[float, float]:
        """
        Mann-Whitney U test (non-parametric alternative to t-test).

        H0: Distributions are identical
        H1: Distributions differ

        Returns:
            (U_statistic, p_value)
        """
        result = stats.mannwhitneyu(init, steady, alternative='two-sided')
        return result.statistic, result.pvalue

    def run_complete_validation(self) -> StatisticalResults:
        """Run all statistical tests."""
        print("="*80)
        print("STATISTICAL VALIDATION OF PHASE TRANSITION")
        print("="*80)

        # Extract data
        init, steady = self.extract_regime_data()

        print(f"\nData Summary:")
        print(f"  Initialization (n={len(init)}): {init.mean():.1%} ± {init.std():.1%}")
        print(f"  Steady-state (n={len(steady)}): {steady.mean():.1%} ± {steady.std():.1%}")
        print(f"  Difference: {(init.mean() - steady.mean()):.1%}")
        print()

        # 1. T-test
        print("1. Two-Sample T-Test (Welch's)")
        t_stat, t_p, df = self.ttest_independent(init, steady)
        print(f"  t({df}) = {t_stat:.3f}, p = {t_p:.6f}")
        print(f"  Result: {'SIGNIFICANT' if t_p < 0.05 else 'NOT SIGNIFICANT'} at α=0.05")
        print()

        # 2. Effect size
        print("2. Effect Size (Cohen's d)")
        d = self.cohens_d(init, steady)
        interp = self.interpret_effect_size(d)
        print(f"  d = {d:.3f} ({interp})")
        print()

        # 3. Bootstrap CIs
        print("3. Bootstrap Confidence Intervals (95%, n=10,000)")
        np.random.seed(42)  # Reproducibility
        init_ci = self.bootstrap_ci(init)
        steady_ci = self.bootstrap_ci(steady)
        print(f"  Initialization: [{init_ci[0]:.1%}, {init_ci[1]:.1%}]")
        print(f"  Steady-state: [{steady_ci[0]:.1%}, {steady_ci[1]:.1%}]")
        print(f"  Overlap: {'YES' if init_ci[1] > steady_ci[0] else 'NO'}")
        print()

        # 4. Variance test
        print("4. Levene's Test for Equality of Variances")
        lev_stat, lev_p = self.levene_test(init, steady)
        print(f"  W = {lev_stat:.3f}, p = {lev_p:.3f}")
        print(f"  Result: Variances {'equal' if lev_p > 0.05 else 'differ'} (α=0.05)")
        print()

        # 5. Non-parametric test
        print("5. Mann-Whitney U Test (Non-parametric)")
        u_stat, u_p = self.mann_whitney(init, steady)
        print(f"  U = {u_stat:.1f}, p = {u_p:.6f}")
        print(f"  Result: {'SIGNIFICANT' if u_p < 0.05 else 'NOT SIGNIFICANT'} at α=0.05")
        print()

        # Compile results
        results = StatisticalResults(
            t_statistic=t_stat,
            t_pvalue=t_p,
            degrees_freedom=df,
            cohens_d=d,
            effect_interpretation=interp,
            init_mean_ci=init_ci,
            steady_mean_ci=steady_ci,
            levene_statistic=lev_stat,
            levene_pvalue=lev_p,
            variance_equal=(lev_p > 0.05),
            mannwhitney_u=u_stat,
            mannwhitney_pvalue=u_p
        )

        print("="*80)
        print("VALIDATION COMPLETE")
        print("="*80)
        print("\nConclusion:")
        if t_p < 0.05 and u_p < 0.05 and abs(d) > 0.8:
            print("  ✅ Phase transition VALIDATED")
            print("     - Significant difference (p < 0.05)")
            print(f"     - Large effect size (d = {d:.2f})")
            print("     - Converging evidence (parametric + non-parametric)")
        else:
            print("  ⚠️  Phase transition UNCERTAIN")
            print("     - Further investigation needed")
        print()

        # Save results
        output_path = self.data_path / "statistical_validation_results.json"
        results_dict = {
            'ttest': {
                't_statistic': float(t_stat),
                'p_value': float(t_p),
                'degrees_freedom': int(df),
                'significant': bool(t_p < 0.05)
            },
            'effect_size': {
                'cohens_d': float(d),
                'interpretation': interp
            },
            'bootstrap_ci_95': {
                'initialization': [float(init_ci[0]), float(init_ci[1])],
                'steady_state': [float(steady_ci[0]), float(steady_ci[1])],
                'overlap': bool(init_ci[1] > steady_ci[0])
            },
            'levene_test': {
                'statistic': float(lev_stat),
                'p_value': float(lev_p),
                'variances_equal': bool(lev_p > 0.05)
            },
            'mann_whitney': {
                'u_statistic': float(u_stat),
                'p_value': float(u_p),
                'significant': bool(u_p < 0.05)
            }
        }

        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"Results saved: {output_path}")

        return results


def main():
    """Run statistical validation."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    data_path = workspace / "analysis" / "temporal_evolution"

    validator = StatisticalValidator(data_path)
    results = validator.run_complete_validation()

    return results


if __name__ == "__main__":
    main()
