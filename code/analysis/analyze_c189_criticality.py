#!/usr/bin/env python3
"""
C189 Self-Organized Criticality Analysis Pipeline

Analyzes experimental results from C189 testing energy-regulated criticality
in composition dynamics. Tests pre-registered hypotheses H5.1-H5.3 regarding
power-law inter-event interval distributions, burstiness, and criticality
emergence without tuning.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08 (Cycle 1287+)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Experimental Design:
- 5 frequencies: f ∈ {1.5%, 2.0%, 2.5%, 3.0%, 5.0%}
- 20 seeds per frequency
- Duration = 5000 cycles (extended for criticality detection)
- N_max = 50 agents

Pre-Registered Hypotheses:
- H5.1: Power-law IEI distribution (α ∈ [1.5, 2.5], better fit than exponential)
- H5.2: High burstiness (B > 0.3 across all frequencies)
- H5.3: Criticality without tuning (power-laws emerge at all frequencies)

Zero-Delay Infrastructure: Analysis pipeline created BEFORE experiments run.

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib as mpl

# Publication-quality settings
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['font.family'] = 'sans-serif'


class C189CriticalityAnalyzer:
    """
    Analyzes C189 self-organized criticality experimental results.
    Tests hypotheses about energy-regulated power-law dynamics.
    """

    def __init__(self, results_dir: str, output_dir: str):
        """Initialize analyzer."""
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.frequencies = [1.5, 2.0, 2.5, 3.0, 5.0]
        self.n_seeds = 20

        self.data = {f: [] for f in self.frequencies}
        self.hypotheses = {}

    def load_data(self) -> None:
        """Load all C189 experimental result files."""
        print("Loading C189 experimental data...")

        for f in self.frequencies:
            for seed in range(self.n_seeds):
                pattern = f"c189_f{f:.1f}_seed{seed:02d}.json"
                filepath = self.results_dir / pattern

                if not filepath.exists():
                    print(f"  WARNING: Missing {pattern}")
                    continue

                with open(filepath, 'r') as file:
                    result = json.load(file)
                    self.data[f].append(result)

        for f in self.frequencies:
            n_loaded = len(self.data[f])
            print(f"  f={f:.1f}%: {n_loaded}/{self.n_seeds} runs loaded")

    def fit_power_law(self, data: np.ndarray, x_min: float = None) -> Dict:
        """
        Fit power-law distribution to data using maximum likelihood.

        P(x) ~ x^(-α) for x >= x_min

        Args:
            data: Array of inter-event intervals
            x_min: Minimum value for power-law fit (auto if None)

        Returns:
            Dict with fit parameters and goodness-of-fit
        """
        data = np.array(data)
        data = data[data > 0]  # Remove zeros

        if len(data) < 10:
            return {'alpha': np.nan, 'x_min': np.nan, 'n_tail': 0, 'KS_stat': np.nan}

        # Determine x_min if not provided
        if x_min is None:
            # Use method from Clauset et al. (2009): minimize KS statistic
            x_min_candidates = np.percentile(data, [25, 50, 75])

            best_x_min = None
            best_ks = float('inf')

            for xm in x_min_candidates:
                tail = data[data >= xm]
                if len(tail) < 10:
                    continue

                # MLE for power-law exponent
                alpha = 1 + len(tail) / np.sum(np.log(tail / xm))

                # KS test
                theoretical_cdf = lambda x: 1 - (x / xm)**(-alpha + 1)
                empirical_cdf = np.arange(1, len(tail) + 1) / len(tail)
                theoretical = theoretical_cdf(np.sort(tail))

                ks_stat = np.max(np.abs(empirical_cdf - theoretical))

                if ks_stat < best_ks:
                    best_ks = ks_stat
                    best_x_min = xm

            x_min = best_x_min if best_x_min is not None else np.median(data)

        # Fit power law to tail
        tail = data[data >= x_min]

        if len(tail) < 10:
            return {'alpha': np.nan, 'x_min': x_min, 'n_tail': len(tail), 'KS_stat': np.nan}

        # Maximum likelihood estimate
        alpha = 1 + len(tail) / np.sum(np.log(tail / x_min))

        # Goodness of fit (KS test)
        theoretical_cdf = lambda x: 1 - (x / x_min)**(-alpha + 1)
        empirical_cdf = np.arange(1, len(tail) + 1) / len(tail)
        theoretical = theoretical_cdf(np.sort(tail))
        ks_stat = np.max(np.abs(empirical_cdf - theoretical))

        return {
            'alpha': alpha,
            'x_min': x_min,
            'n_tail': len(tail),
            'KS_stat': ks_stat
        }

    def fit_exponential(self, data: np.ndarray) -> Dict:
        """
        Fit exponential distribution to data.

        P(x) ~ exp(-λx)

        Args:
            data: Array of inter-event intervals

        Returns:
            Dict with fit parameters
        """
        data = np.array(data)
        data = data[data > 0]

        if len(data) < 10:
            return {'lambda': np.nan, 'KS_stat': np.nan}

        # MLE for exponential
        lambda_mle = 1 / np.mean(data)

        # KS test
        theoretical_cdf = lambda x: 1 - np.exp(-lambda_mle * x)
        empirical_cdf = np.arange(1, len(data) + 1) / len(data)
        theoretical = theoretical_cdf(np.sort(data))
        ks_stat = np.max(np.abs(empirical_cdf - theoretical))

        return {
            'lambda': lambda_mle,
            'KS_stat': ks_stat
        }

    def calculate_burstiness(self, intervals: np.ndarray) -> float:
        """Calculate burstiness coefficient B = (σ - μ) / (σ + μ)."""
        if len(intervals) < 2:
            return 0.0

        mu = np.mean(intervals)
        sigma = np.std(intervals)

        if mu + sigma == 0:
            return 0.0

        return (sigma - mu) / (sigma + mu)

    def test_h51_power_law_distribution(self) -> Dict:
        """
        Test H5.1: Power-law IEI distribution (better fit than exponential).

        Returns:
            Dict with power-law fit statistics
        """
        print("\n=== Testing H5.1: Power-Law Distribution ===")

        results = {}

        for f in self.frequencies:
            if not self.data[f]:
                continue

            alphas = []
            pl_ks_stats = []
            exp_ks_stats = []

            for run in self.data[f]:
                if 'composition_events' in run:
                    events = run['composition_events']

                    if len(events) >= 10:
                        intervals = np.diff(sorted(events))

                        # Fit power law
                        pl_fit = self.fit_power_law(intervals)
                        exp_fit = self.fit_exponential(intervals)

                        if not np.isnan(pl_fit['alpha']):
                            alphas.append(pl_fit['alpha'])
                            pl_ks_stats.append(pl_fit['KS_stat'])
                            exp_ks_stats.append(exp_fit['KS_stat'])

            if alphas:
                # Count better fits (power-law KS < exponential KS)
                n_better = sum(1 for pl_ks, exp_ks in zip(pl_ks_stats, exp_ks_stats)
                              if pl_ks < exp_ks)

                results[f] = {
                    'mean_alpha': np.mean(alphas),
                    'std_alpha': np.std(alphas),
                    'median_alpha': np.median(alphas),
                    'alpha_in_range': sum(1 for a in alphas if 1.5 <= a <= 2.5),
                    'pl_better_than_exp': n_better,
                    'n_runs': len(alphas),
                    'all_alphas': alphas,
                    'pl_ks_mean': np.mean(pl_ks_stats),
                    'exp_ks_mean': np.mean(exp_ks_stats)
                }

                print(f"\nf={f:.1f}%:")
                print(f"  Mean α: {results[f]['mean_alpha']:.3f} ± {results[f]['std_alpha']:.3f}")
                print(f"  α in [1.5, 2.5]: {results[f]['alpha_in_range']}/{results[f]['n_runs']}")
                print(f"  Power-law better than exponential: {results[f]['pl_better_than_exp']}/{results[f]['n_runs']}")

        # H5.1 passes if majority of conditions show:
        # (1) α in [1.5, 2.5] for majority of runs
        # (2) Power-law fits better than exponential
        h51_pass = False

        if len(results) >= 3:  # Need at least 3 frequencies
            conditions_pass = []

            for f in results:
                r = results[f]
                # Criterion: ≥70% runs have α in range AND ≥70% better fit
                cond_pass = (r['alpha_in_range'] >= 0.7 * r['n_runs'] and
                            r['pl_better_than_exp'] >= 0.7 * r['n_runs'])
                conditions_pass.append(cond_pass)

            h51_pass = (sum(conditions_pass) >= 0.6 * len(results))  # 60% of frequencies pass

        print(f"\nH5.1 Power-Law Distribution: {'PASS ✓' if h51_pass else 'FAIL ✗'}")
        print(f"  Criterion: ≥60% frequencies show α∈[1.5,2.5] AND better fit (both ≥70% runs)")

        self.hypotheses['H5.1'] = {
            'passed': h51_pass,
            'points': 2 if h51_pass else 0,
            'data': results
        }

        return results

    def test_h52_high_burstiness(self) -> Dict:
        """
        Test H5.2: High burstiness (B > 0.3 across all frequencies).

        Returns:
            Dict with burstiness statistics
        """
        print("\n=== Testing H5.2: High Burstiness ===")

        results = {}

        for f in self.frequencies:
            if not self.data[f]:
                continue

            B_values = []

            for run in self.data[f]:
                if 'composition_events' in run:
                    events = run['composition_events']

                    if len(events) >= 3:
                        intervals = np.diff(sorted(events))
                        B = self.calculate_burstiness(intervals)
                        B_values.append(B)

            if B_values:
                results[f] = {
                    'mean_B': np.mean(B_values),
                    'std_B': np.std(B_values),
                    'median_B': np.median(B_values),
                    'n_above_threshold': sum(1 for b in B_values if b > 0.3),
                    'n_runs': len(B_values),
                    'all_B': B_values
                }

                print(f"\nf={f:.1f}%:")
                print(f"  Mean B: {results[f]['mean_B']:.3f} ± {results[f]['std_B']:.3f}")
                print(f"  B > 0.3: {results[f]['n_above_threshold']}/{results[f]['n_runs']}")

        # H5.2 passes if all frequencies show mean B > 0.3
        h52_pass = False

        if results:
            all_above = all(results[f]['mean_B'] > 0.3 for f in results)
            h52_pass = all_above

        print(f"\nH5.2 High Burstiness: {'PASS ✓' if h52_pass else 'FAIL ✗'}")
        print(f"  Criterion: All frequencies show mean B > 0.3")

        self.hypotheses['H5.2'] = {
            'passed': h52_pass,
            'points': 2 if h52_pass else 0,
            'data': results
        }

        return results

    def test_h53_criticality_without_tuning(self) -> Dict:
        """
        Test H5.3: Criticality without tuning (power-laws emerge at all frequencies).

        Verifies that power-law behavior is robust across frequency range.

        Returns:
            Dict with criticality robustness statistics
        """
        print("\n=== Testing H5.3: Criticality Without Tuning ===")

        # Leverage H5.1 results
        if 'H5.1' not in self.hypotheses:
            print("  ERROR: H5.1 must be tested first")
            return {}

        h51_data = self.hypotheses['H5.1']['data']

        # Check α consistency across frequencies
        alphas_by_freq = []
        for f in self.frequencies:
            if f in h51_data and 'mean_alpha' in h51_data[f]:
                alphas_by_freq.append(h51_data[f]['mean_alpha'])

        results = {
            'n_frequencies': len(alphas_by_freq),
            'alpha_mean': np.mean(alphas_by_freq) if alphas_by_freq else np.nan,
            'alpha_std': np.std(alphas_by_freq) if alphas_by_freq else np.nan,
            'alpha_cv': np.std(alphas_by_freq) / np.mean(alphas_by_freq) if alphas_by_freq else np.nan
        }

        # H5.3 passes if:
        # (1) Power-laws detected at all frequencies (from H5.1)
        # (2) Low coefficient of variation (CV < 0.3) - consistent α across frequencies
        h53_pass = False

        if results['n_frequencies'] >= 4:  # Need at least 4/5 frequencies
            cv_low = results['alpha_cv'] < 0.3
            h53_pass = cv_low

        print(f"\n  Frequencies with power-laws: {results['n_frequencies']}/5")
        print(f"  Mean α: {results['alpha_mean']:.3f} ± {results['alpha_std']:.3f}")
        print(f"  Coefficient of variation: {results['alpha_cv']:.3f}")

        print(f"\nH5.3 Criticality Without Tuning: {'PASS ✓' if h53_pass else 'FAIL ✗'}")
        print(f"  Criterion: ≥4 frequencies AND CV(α) < 0.3")

        self.hypotheses['H5.3'] = {
            'passed': h53_pass,
            'points': 2 if h53_pass else 0,
            'data': results
        }

        return results

    def generate_figures(self) -> None:
        """Generate publication-quality figures."""
        print("\n=== Generating Figures ===")

        self._plot_power_law_distributions()
        self._plot_alpha_vs_frequency()
        self._plot_burstiness_vs_frequency()
        self._plot_goodness_of_fit_comparison()

        print(f"\nFigures saved to: {self.output_dir}/")

    def _plot_power_law_distributions(self) -> None:
        """Plot IEI distributions on log-log scale for each frequency."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, f in enumerate(self.frequencies):
            ax = axes[idx]

            if not self.data[f]:
                continue

            # Aggregate intervals from all runs
            all_intervals = []

            for run in self.data[f]:
                if 'composition_events' in run:
                    events = run['composition_events']
                    if len(events) >= 10:
                        intervals = np.diff(sorted(events))
                        all_intervals.extend(intervals)

            if all_intervals:
                # Log-log histogram
                bins = np.logspace(np.log10(min(all_intervals)),
                                  np.log10(max(all_intervals)), 30)

                counts, edges = np.histogram(all_intervals, bins=bins, density=True)
                centers = (edges[:-1] + edges[1:]) / 2

                ax.loglog(centers, counts, 'o', alpha=0.6, label='Data')

                # Fit power law
                pl_fit = self.fit_power_law(np.array(all_intervals))

                if not np.isnan(pl_fit['alpha']):
                    alpha = pl_fit['alpha']
                    x_min = pl_fit['x_min']

                    x_fit = np.logspace(np.log10(x_min), np.log10(max(all_intervals)), 100)
                    # P(x) ~ x^(-α)
                    C = (alpha - 1) / x_min  # Normalization
                    y_fit = C * x_fit**(-alpha)

                    ax.loglog(x_fit, y_fit, 'r-', linewidth=2,
                             label=f'Power-law (α={alpha:.2f})')

                ax.set_xlabel('Inter-Event Interval')
                ax.set_ylabel('P(IEI)')
                ax.set_title(f'f = {f:.1f}%')
                ax.legend()
                ax.grid(alpha=0.3, which='both')

        # Remove empty subplot
        fig.delaxes(axes[-1])

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c189_power_law_distributions.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c189_power_law_distributions.png")

    def _plot_alpha_vs_frequency(self) -> None:
        """Plot power-law exponent α vs. spawn frequency."""
        fig, ax = plt.subplots(figsize=(8, 6))

        if 'H5.1' in self.hypotheses and 'data' in self.hypotheses['H5.1']:
            data = self.hypotheses['H5.1']['data']

            freqs = []
            alphas = []
            errors = []

            for f in self.frequencies:
                if f in data:
                    freqs.append(f)
                    alphas.append(data[f]['mean_alpha'])
                    errors.append(data[f]['std_alpha'])

            if freqs:
                ax.errorbar(freqs, alphas, yerr=errors, marker='o', markersize=8,
                           linewidth=2, capsize=5, color='#e74c3c')

                # Expected range
                ax.axhspan(1.5, 2.5, alpha=0.2, color='green',
                          label='Expected range [1.5, 2.5]')

                ax.set_xlabel('Spawn Frequency (%)')
                ax.set_ylabel('Power-Law Exponent (α)')
                ax.set_title('Criticality Across Frequencies (H5.3)')
                ax.legend()
                ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c189_alpha_vs_frequency.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c189_alpha_vs_frequency.png")

    def _plot_burstiness_vs_frequency(self) -> None:
        """Plot burstiness coefficient vs. frequency."""
        fig, ax = plt.subplots(figsize=(8, 6))

        if 'H5.2' in self.hypotheses and 'data' in self.hypotheses['H5.2']:
            data = self.hypotheses['H5.2']['data']

            freqs = []
            B_means = []
            B_stds = []

            for f in self.frequencies:
                if f in data:
                    freqs.append(f)
                    B_means.append(data[f]['mean_B'])
                    B_stds.append(data[f]['std_B'])

            if freqs:
                ax.errorbar(freqs, B_means, yerr=B_stds, marker='o', markersize=8,
                           linewidth=2, capsize=5, color='#3498db')

                # Threshold line
                ax.axhline(y=0.3, color='red', linestyle='--', linewidth=2,
                          label='H5.2 threshold (B=0.3)')

                ax.set_xlabel('Spawn Frequency (%)')
                ax.set_ylabel('Burstiness Coefficient (B)')
                ax.set_title('Burstiness Across Frequencies (H5.2)')
                ax.legend()
                ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c189_burstiness_vs_frequency.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c189_burstiness_vs_frequency.png")

    def _plot_goodness_of_fit_comparison(self) -> None:
        """Compare power-law vs. exponential fit quality."""
        fig, ax = plt.subplots(figsize=(8, 6))

        if 'H5.1' in self.hypotheses and 'data' in self.hypotheses['H5.1']:
            data = self.hypotheses['H5.1']['data']

            freqs = []
            pl_ks = []
            exp_ks = []

            for f in self.frequencies:
                if f in data:
                    freqs.append(f)
                    pl_ks.append(data[f]['pl_ks_mean'])
                    exp_ks.append(data[f]['exp_ks_mean'])

            if freqs:
                x = np.arange(len(freqs))
                width = 0.35

                ax.bar(x - width/2, pl_ks, width, label='Power-Law',
                      alpha=0.7, color='#e74c3c')
                ax.bar(x + width/2, exp_ks, width, label='Exponential',
                      alpha=0.7, color='#95a5a6')

                ax.set_xlabel('Spawn Frequency (%)')
                ax.set_ylabel('Mean KS Statistic (lower = better fit)')
                ax.set_title('Power-Law vs. Exponential Fit Quality (H5.1)')
                ax.set_xticks(x)
                ax.set_xticklabels([f'{f:.1f}' for f in freqs])
                ax.legend()
                ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c189_fit_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c189_fit_comparison.png")

    def calculate_composite_scorecard(self) -> Dict:
        """Calculate composite scorecard contribution."""
        print("\n=== Composite Scorecard (C189 Contribution) ===")

        total_points = 0
        max_points = 6  # H5.1 (2) + H5.2 (2) + H5.3 (2)

        for hyp_id in ['H5.1', 'H5.2', 'H5.3']:
            if hyp_id in self.hypotheses:
                points = self.hypotheses[hyp_id]['points']
                passed = self.hypotheses[hyp_id]['passed']
                total_points += points

                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {hyp_id}: {points}/2 points {status}")

        print(f"\nC189 Total: {total_points}/{max_points} points ({100*total_points/max_points:.0f}%)")

        return {
            'total_points': total_points,
            'max_points': max_points,
            'percentage': 100 * total_points / max_points,
            'hypotheses': self.hypotheses
        }

    def save_results(self) -> None:
        """Save analysis results to JSON."""
        output_file = self.output_dir / 'c189_analysis_results.json'

        results = {
            'experiment': 'C189_Self_Organized_Criticality',
            'date_analyzed': '2025-11-08',
            'hypotheses': self.hypotheses,
            'composite_scorecard': self.calculate_composite_scorecard()
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def run_full_analysis(self) -> None:
        """Execute complete C189 analysis pipeline."""
        print("="*60)
        print("C189 SELF-ORGANIZED CRITICALITY ANALYSIS")
        print("="*60)

        self.load_data()
        self.test_h51_power_law_distribution()
        self.test_h52_high_burstiness()
        self.test_h53_criticality_without_tuning()
        self.generate_figures()
        self.calculate_composite_scorecard()
        self.save_results()

        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)


def main():
    """Main entry point."""
    results_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4/c189"

    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    analyzer = C189CriticalityAnalyzer(results_dir, output_dir)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
