#!/usr/bin/env python3
"""
C188 Temporal Regulation Analysis Pipeline

Analyzes experimental results from C188 testing temporal memory effects on
composition dynamics. Tests pre-registered hypotheses H4.1-H4.3 regarding
autocorrelation, burstiness reduction, and refractory period effects.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08 (Cycle 1287+)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Experimental Design:
- 4 memory conditions: τ ∈ {100, 500, 1000, ∞} cycles
- 10 seeds per condition
- f_spawn = 2.0% (baseline)
- Duration = 3000 cycles
- N_max = 50 agents

Pre-Registered Hypotheses:
- H4.1: Negative autocorrelation in composition events (memory effect)
- H4.2: Burstiness reduction (B decreases with decreasing τ)
- H4.3: Refractory period verification (inter-spawn intervals > τ_memory)

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
import matplotlib.pyplot as plt
import matplotlib as mpl

# Publication-quality settings
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['font.family'] = 'sans-serif'


class C188TemporalAnalyzer:
    """
    Analyzes C188 temporal regulation experimental results.
    Tests hypotheses about memory effects on composition dynamics.
    """

    def __init__(self, results_dir: str, output_dir: str):
        """Initialize analyzer."""
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.tau_values = [100, 500, 1000, float('inf')]
        self.n_seeds = 10

        self.data = {tau: [] for tau in self.tau_values}
        self.hypotheses = {}

    def load_data(self) -> None:
        """Load all C188 experimental result files."""
        print("Loading C188 experimental data...")

        for tau in self.tau_values:
            tau_str = 'inf' if tau == float('inf') else str(int(tau))

            for seed in range(self.n_seeds):
                pattern = f"c188_tau{tau_str}_seed{seed:02d}.json"
                filepath = self.results_dir / pattern

                if not filepath.exists():
                    print(f"  WARNING: Missing {pattern}")
                    continue

                with open(filepath, 'r') as f:
                    result = json.load(f)
                    self.data[tau].append(result)

        for tau in self.tau_values:
            tau_str = '∞' if tau == float('inf') else str(int(tau))
            n_loaded = len(self.data[tau])
            print(f"  τ={tau_str}: {n_loaded}/{self.n_seeds} runs loaded")

    def calculate_autocorrelation(self, event_times: List[int], max_lag: int = 20) -> np.ndarray:
        """
        Calculate autocorrelation function for event times.

        Args:
            event_times: List of cycle numbers when events occurred
            max_lag: Maximum lag to calculate

        Returns:
            Array of autocorrelation values for lags 0 to max_lag
        """
        if len(event_times) < 10:
            return np.zeros(max_lag + 1)

        # Convert to binary time series
        max_time = max(event_times) + 1
        series = np.zeros(max_time)
        series[event_times] = 1

        # Calculate autocorrelation
        acf = np.correlate(series, series, mode='full')
        acf = acf[len(acf)//2:]  # Take only positive lags
        acf = acf[:max_lag+1]
        acf = acf / acf[0]  # Normalize

        return acf

    def test_h41_negative_autocorrelation(self) -> Dict:
        """
        Test H4.1: Negative autocorrelation in composition events.

        Memory should create anti-bunching (negative correlation at lag=1).

        Returns:
            Dict with autocorrelation statistics
        """
        print("\n=== Testing H4.1: Negative Autocorrelation ===")

        results = {}

        for tau in self.tau_values:
            if not self.data[tau]:
                continue

            lag1_correlations = []

            for run in self.data[tau]:
                if 'composition_events' in run:
                    events = run['composition_events']

                    if len(events) >= 10:
                        acf = self.calculate_autocorrelation(events, max_lag=5)
                        if len(acf) > 1:
                            lag1_correlations.append(acf[1])

            if lag1_correlations:
                results[tau] = {
                    'mean_acf_lag1': np.mean(lag1_correlations),
                    'std_acf_lag1': np.std(lag1_correlations),
                    'median_acf_lag1': np.median(lag1_correlations),
                    'n_negative': sum(1 for x in lag1_correlations if x < 0),
                    'n_runs': len(lag1_correlations),
                    'all_values': lag1_correlations
                }

                tau_str = '∞' if tau == float('inf') else str(int(tau))
                print(f"\nτ={tau_str}:")
                print(f"  Mean ACF(lag=1): {results[tau]['mean_acf_lag1']:.3f} ± {results[tau]['std_acf_lag1']:.3f}")
                print(f"  Negative correlations: {results[tau]['n_negative']}/{results[tau]['n_runs']}")

        # H4.1 passes if finite τ conditions show negative lag-1 autocorrelation
        h41_pass = False

        finite_tau = [t for t in self.tau_values if t != float('inf')]
        if finite_tau and all(t in results for t in finite_tau):
            # Criterion: Majority of finite-τ conditions show mean ACF(lag=1) < -0.1
            negative_conditions = sum(
                1 for t in finite_tau if results[t]['mean_acf_lag1'] < -0.1
            )
            h41_pass = (negative_conditions >= len(finite_tau) * 0.67)  # 2/3 conditions

        print(f"\nH4.1 Negative Autocorrelation: {'PASS ✓' if h41_pass else 'FAIL ✗'}")
        print(f"  Criterion: ≥67% finite-τ conditions show mean ACF(lag=1) < -0.1")

        self.hypotheses['H4.1'] = {
            'passed': h41_pass,
            'points': 2 if h41_pass else 0,
            'data': results
        }

        return results

    def calculate_burstiness(self, event_times: List[int]) -> float:
        """
        Calculate burstiness coefficient B.

        B = (σ - μ) / (σ + μ) where μ, σ are mean and std of inter-event intervals.

        B = 1: maximum burstiness (highly irregular)
        B = 0: Poisson process (random)
        B = -1: perfectly regular

        Args:
            event_times: List of cycle numbers when events occurred

        Returns:
            Burstiness coefficient
        """
        if len(event_times) < 2:
            return 0.0

        # Calculate inter-event intervals
        intervals = np.diff(sorted(event_times))

        if len(intervals) == 0:
            return 0.0

        mu = np.mean(intervals)
        sigma = np.std(intervals)

        if mu + sigma == 0:
            return 0.0

        B = (sigma - mu) / (sigma + mu)

        return B

    def test_h42_burstiness_reduction(self) -> Dict:
        """
        Test H4.2: Burstiness reduction (B decreases with decreasing τ).

        Shorter memory should spread events more evenly.

        Returns:
            Dict with burstiness statistics
        """
        print("\n=== Testing H4.2: Burstiness Reduction ===")

        results = {}

        for tau in self.tau_values:
            if not self.data[tau]:
                continue

            burstiness_values = []

            for run in self.data[tau]:
                if 'composition_events' in run:
                    events = run['composition_events']

                    if len(events) >= 3:
                        B = self.calculate_burstiness(events)
                        burstiness_values.append(B)

            if burstiness_values:
                results[tau] = {
                    'mean_B': np.mean(burstiness_values),
                    'std_B': np.std(burstiness_values),
                    'median_B': np.median(burstiness_values),
                    'n_runs': len(burstiness_values),
                    'all_values': burstiness_values
                }

                tau_str = '∞' if tau == float('inf') else str(int(tau))
                print(f"\nτ={tau_str}:")
                print(f"  Mean burstiness: B = {results[tau]['mean_B']:.3f} ± {results[tau]['std_B']:.3f}")

        # H4.2 passes if burstiness decreases monotonically with decreasing τ
        h42_pass = False

        if all(t in results for t in self.tau_values):
            B_values = [results[tau]['mean_B'] for tau in self.tau_values]

            # Check monotonic decrease: B(τ=100) < B(τ=500) < B(τ=1000) < B(τ=∞)
            is_monotonic = all(B_values[i] < B_values[i+1] for i in range(len(B_values)-1))

            # Statistical test: τ=100 significantly lower than τ=∞
            t_stat, p_val = stats.ttest_ind(
                results[100]['all_values'],
                results[float('inf')]['all_values']
            )

            h42_pass = (is_monotonic and p_val < 0.05 and t_stat < 0)

        print(f"\nH4.2 Burstiness Reduction: {'PASS ✓' if h42_pass else 'FAIL ✗'}")
        print(f"  Criterion: Monotonic decrease AND B(τ=100) < B(τ=∞) (p<0.05)")

        self.hypotheses['H4.2'] = {
            'passed': h42_pass,
            'points': 2 if h42_pass else 0,
            'data': results
        }

        return results

    def test_h43_refractory_period(self) -> Dict:
        """
        Test H4.3: Refractory period verification.

        Verify that inter-spawn intervals for same agent are > τ_memory.

        Returns:
            Dict with refractory period compliance statistics
        """
        print("\n=== Testing H4.3: Refractory Period Verification ===")

        results = {}

        for tau in self.tau_values:
            if tau == float('inf'):  # No refractory period in control
                continue

            if not self.data[tau]:
                continue

            compliance_rates = []

            for run in self.data[tau]:
                if 'spawn_history' in run:
                    # spawn_history: list of (cycle, agent_id) tuples
                    history = run['spawn_history']

                    # Group by agent
                    agent_spawns = {}
                    for cycle, agent_id in history:
                        if agent_id not in agent_spawns:
                            agent_spawns[agent_id] = []
                        agent_spawns[agent_id].append(cycle)

                    # Check intervals
                    violations = 0
                    total_intervals = 0

                    for agent_id, cycles in agent_spawns.items():
                        if len(cycles) < 2:
                            continue

                        intervals = np.diff(sorted(cycles))

                        for interval in intervals:
                            total_intervals += 1
                            if interval < tau:
                                violations += 1

                    if total_intervals > 0:
                        compliance_rate = 1 - (violations / total_intervals)
                        compliance_rates.append(compliance_rate)

            if compliance_rates:
                results[tau] = {
                    'mean_compliance': np.mean(compliance_rates),
                    'std_compliance': np.std(compliance_rates),
                    'n_runs': len(compliance_rates)
                }

                print(f"\nτ={int(tau)}:")
                print(f"  Mean compliance: {100*results[tau]['mean_compliance']:.1f}% ± {100*results[tau]['std_compliance']:.1f}%")

        # H4.3 passes if all finite-τ conditions show ≥90% compliance
        h43_pass = False

        finite_tau = [t for t in self.tau_values if t != float('inf')]
        if finite_tau and all(t in results for t in finite_tau):
            all_compliant = all(results[t]['mean_compliance'] >= 0.90 for t in finite_tau)
            h43_pass = all_compliant

        print(f"\nH4.3 Refractory Period: {'PASS ✓' if h43_pass else 'FAIL ✗'}")
        print(f"  Criterion: ≥90% interval compliance for all finite-τ conditions")

        self.hypotheses['H4.3'] = {
            'passed': h43_pass,
            'points': 2 if h43_pass else 0,
            'data': results
        }

        return results

    def generate_figures(self) -> None:
        """Generate publication-quality figures."""
        print("\n=== Generating Figures ===")

        self._plot_autocorrelation()
        self._plot_burstiness()
        self._plot_interval_distributions()

        print(f"\nFigures saved to: {self.output_dir}/")

    def _plot_autocorrelation(self) -> None:
        """Plot autocorrelation functions for each τ condition."""
        fig, ax = plt.subplots(figsize=(8, 6))

        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']

        for tau, color in zip(self.tau_values, colors):
            if not self.data[tau]:
                continue

            tau_str = '∞' if tau == float('inf') else str(int(tau))

            # Average ACF across runs
            all_acfs = []

            for run in self.data[tau]:
                if 'composition_events' in run:
                    events = run['composition_events']
                    if len(events) >= 10:
                        acf = self.calculate_autocorrelation(events, max_lag=20)
                        all_acfs.append(acf)

            if all_acfs:
                mean_acf = np.mean(all_acfs, axis=0)
                std_acf = np.std(all_acfs, axis=0)
                lags = np.arange(len(mean_acf))

                ax.plot(lags, mean_acf, color=color, linewidth=2, label=f'τ = {tau_str}')
                ax.fill_between(lags, mean_acf - std_acf, mean_acf + std_acf,
                               color=color, alpha=0.2)

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Lag (cycles)')
        ax.set_ylabel('Autocorrelation')
        ax.set_title('Composition Event Autocorrelation (H4.1)')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c188_autocorrelation.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c188_autocorrelation.png")

    def _plot_burstiness(self) -> None:
        """Plot burstiness coefficient vs. τ."""
        fig, ax = plt.subplots(figsize=(8, 6))

        if 'H4.2' in self.hypotheses and 'data' in self.hypotheses['H4.2']:
            data = self.hypotheses['H4.2']['data']

            tau_labels = []
            B_means = []
            B_stds = []

            for tau in self.tau_values:
                if tau in data:
                    tau_str = '∞' if tau == float('inf') else str(int(tau))
                    tau_labels.append(tau_str)
                    B_means.append(data[tau]['mean_B'])
                    B_stds.append(data[tau]['std_B'])

            if tau_labels:
                x = np.arange(len(tau_labels))
                ax.errorbar(x, B_means, yerr=B_stds, marker='o', markersize=8,
                           linewidth=2, capsize=5, color='#3498db')

                ax.set_xlabel('Memory Window (τ)')
                ax.set_ylabel('Burstiness Coefficient (B)')
                ax.set_title('Burstiness vs. Memory Window (H4.2)')
                ax.set_xticks(x)
                ax.set_xticklabels(tau_labels)
                ax.axhline(y=0, color='gray', linestyle=':', linewidth=1,
                          label='Poisson (B=0)')
                ax.legend()
                ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c188_burstiness.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c188_burstiness.png")

    def _plot_interval_distributions(self) -> None:
        """Plot inter-event interval distributions."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for idx, tau in enumerate(self.tau_values):
            ax = axes[idx]

            if not self.data[tau]:
                continue

            tau_str = '∞' if tau == float('inf') else str(int(tau))

            # Collect all intervals
            all_intervals = []

            for run in self.data[tau]:
                if 'composition_events' in run:
                    events = run['composition_events']
                    if len(events) >= 2:
                        intervals = np.diff(sorted(events))
                        all_intervals.extend(intervals)

            if all_intervals:
                ax.hist(all_intervals, bins=30, density=True, alpha=0.7,
                       color='#3498db', edgecolor='black')

                ax.set_xlabel('Inter-Event Interval (cycles)')
                ax.set_ylabel('Density')
                ax.set_title(f'τ = {tau_str}')

                # Add vertical line at τ for refractory period
                if tau != float('inf'):
                    ax.axvline(x=tau, color='red', linestyle='--', linewidth=2,
                              label=f'Refractory (τ={tau_str})')
                    ax.legend()

                ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c188_interval_distributions.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c188_interval_distributions.png")

    def calculate_composite_scorecard(self) -> Dict:
        """Calculate composite scorecard contribution."""
        print("\n=== Composite Scorecard (C188 Contribution) ===")

        total_points = 0
        max_points = 6  # H4.1 (2) + H4.2 (2) + H4.3 (2)

        for hyp_id in ['H4.1', 'H4.2', 'H4.3']:
            if hyp_id in self.hypotheses:
                points = self.hypotheses[hyp_id]['points']
                passed = self.hypotheses[hyp_id]['passed']
                total_points += points

                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {hyp_id}: {points}/2 points {status}")

        print(f"\nC188 Total: {total_points}/{max_points} points ({100*total_points/max_points:.0f}%)")

        return {
            'total_points': total_points,
            'max_points': max_points,
            'percentage': 100 * total_points / max_points,
            'hypotheses': self.hypotheses
        }

    def save_results(self) -> None:
        """Save analysis results to JSON."""
        output_file = self.output_dir / 'c188_analysis_results.json'

        results = {
            'experiment': 'C188_Temporal_Regulation',
            'date_analyzed': '2025-11-08',
            'hypotheses': self.hypotheses,
            'composite_scorecard': self.calculate_composite_scorecard()
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def run_full_analysis(self) -> None:
        """Execute complete C188 analysis pipeline."""
        print("="*60)
        print("C188 TEMPORAL REGULATION ANALYSIS")
        print("="*60)

        self.load_data()
        self.test_h41_negative_autocorrelation()
        self.test_h42_burstiness_reduction()
        self.test_h43_refractory_period()
        self.generate_figures()
        self.calculate_composite_scorecard()
        self.save_results()

        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)


def main():
    """Main entry point."""
    results_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4/c188"

    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    analyzer = C188TemporalAnalyzer(results_dir, output_dir)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
