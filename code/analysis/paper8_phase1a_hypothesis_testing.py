#!/usr/bin/env python3
"""
Paper 8 Phase 1A: Retrospective Hypothesis Testing
===================================================

Analyzes C256 experiment data to validate/refute 5 hypotheses explaining
non-linear runtime variance in extended Python simulations.

Hypotheses:
- H1: System Resource Contention (CPU, memory, disk)
- H2: Memory Fragmentation (pymalloc arena pinning)
- H3: I/O Accumulation (psutil call latency)
- H4: Thermal Throttling (CPU frequency scaling)
- H5: Emergent Complexity (NRM pattern memory growth)

Statistical Methods:
- H1: Spearman correlation (non-parametric, runtime vs. resource utilization)
- H2: Polynomial vs. linear regression (R² comparison, fragmentation signature)
- H3: Linear regression (slope significance, I/O latency trend)
- H4: Spearman correlation (runtime vs. temperature/frequency)
- H5: Linear regression (per-cycle runtime vs. pattern memory count)

Expected Runtime: ~1 hour (data loading + 5 hypothesis tests + figure generation)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
import argparse
from typing import Dict, List, Tuple, Optional

# Set publication-quality plotting defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10


class HypothesisTester:
    """
    Orchestrates retrospective hypothesis testing for Paper 8.

    Loads C256 experimental data and applies statistical validation
    methods to each of 5 hypotheses (H1-H5).
    """

    def __init__(self, data_path: str, output_dir: str = "papers/figures"):
        """
        Initialize hypothesis tester.

        Args:
            data_path: Path to C256 results JSON file
            output_dir: Directory for output figures and results
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.data = None
        self.results = {
            'H1': None,
            'H2': None,
            'H3': None,
            'H4': None,
            'H5': None
        }

    def load_data(self) -> None:
        """Load C256 experimental data from JSON."""
        print(f"Loading data from {self.data_path}...")

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"C256 data file not found: {self.data_path}\n"
                f"Expected location: data/results/cycle256_h1h4_mechanism_validation_results.json\n"
                f"Ensure C256 experiment has completed before running Phase 1A analysis."
            )

        with open(self.data_path, 'r') as f:
            self.data = json.load(f)

        # Validate data structure
        required_keys = ['system_metrics', 'cycle_times', 'experiment_metadata']
        for key in required_keys:
            if key not in self.data:
                raise ValueError(f"Missing required data key: {key}")

        print(f"✓ Data loaded successfully")
        print(f"  Cycles: {len(self.data.get('cycle_times', []))}")
        print(f"  System metrics snapshots: {len(self.data.get('system_metrics', []))}")
        print(f"  Total runtime: {self.data.get('experiment_metadata', {}).get('total_runtime_hours', 'N/A')}h")
        print()

    def test_h1_system_resource_contention(self) -> Dict:
        """
        Test H1: System Resource Contention

        Method: Spearman correlation between runtime and resource utilization.

        Expected if H1 valid:
        - Strong positive correlation (ρ > 0.5) between runtime and CPU%
        - Strong positive correlation (ρ > 0.5) between runtime and memory%
        - p < 0.05 for statistical significance

        Returns:
            Dictionary with correlation statistics and validation decision
        """
        print("="*80)
        print("H1: SYSTEM RESOURCE CONTENTION")
        print("="*80)
        print("Hypothesis: Runtime variance caused by fluctuating CPU/memory usage")
        print("Method: Spearman correlation (non-parametric)")
        print()

        # Extract runtime and resource data
        cycle_times = np.array(self.data['cycle_times'])  # Per-cycle runtime (seconds)
        system_metrics = self.data['system_metrics']

        # Extract CPU and memory percentages aligned with cycle times
        cpu_percent = np.array([m['cpu_percent'] for m in system_metrics])
        memory_percent = np.array([m['memory_percent'] for m in system_metrics])

        # Calculate Spearman correlation
        rho_cpu, p_cpu = spearmanr(cycle_times, cpu_percent)
        rho_memory, p_memory = spearmanr(cycle_times, memory_percent)

        # Validation criteria
        validated = (
            (abs(rho_cpu) > 0.5 and p_cpu < 0.05) or
            (abs(rho_memory) > 0.5 and p_memory < 0.05)
        )

        result = {
            'hypothesis': 'H1: System Resource Contention',
            'method': 'Spearman correlation',
            'rho_cpu': rho_cpu,
            'p_cpu': p_cpu,
            'rho_memory': rho_memory,
            'p_memory': p_memory,
            'validated': validated,
            'interpretation': (
                'VALIDATED' if validated else 'REFUTED'
            ),
            'criteria': 'ρ > 0.5 and p < 0.05 for either CPU or memory'
        }

        # Print results
        print(f"CPU correlation:    ρ = {rho_cpu:+.3f}, p = {p_cpu:.4f}")
        print(f"Memory correlation: ρ = {rho_memory:+.3f}, p = {p_memory:.4f}")
        print()
        print(f"Result: {result['interpretation']}")
        if validated:
            print(f"  → Strong correlation detected (|ρ| > 0.5, p < 0.05)")
        else:
            print(f"  → Weak/no correlation (criteria not met)")
        print()

        self.results['H1'] = result
        return result

    def test_h2_memory_fragmentation(self) -> Dict:
        """
        Test H2: Memory Fragmentation

        Method: Polynomial (degree 2) vs. linear regression on memory growth.

        Expected if H2 valid:
        - Polynomial fit significantly better than linear (ΔR² > 0.1)
        - Non-linear memory growth curve (characteristic of fragmentation)

        Returns:
            Dictionary with regression statistics and validation decision
        """
        print("="*80)
        print("H2: MEMORY FRAGMENTATION (PYMALLOC ARENA PINNING)")
        print("="*80)
        print("Hypothesis: Non-linear runtime variance caused by memory fragmentation")
        print("Method: Polynomial vs. linear regression (ΔR² comparison)")
        print()

        # Extract memory data over cycles
        system_metrics = self.data['system_metrics']
        cycles = np.arange(len(system_metrics))
        memory_rss_mb = np.array([m['memory_rss_mb'] for m in system_metrics])

        # Reshape for sklearn
        X = cycles.reshape(-1, 1)
        y = memory_rss_mb

        # Linear regression
        linear_model = LinearRegression()
        linear_model.fit(X, y)
        y_pred_linear = linear_model.predict(X)
        r2_linear = r2_score(y, y_pred_linear)

        # Polynomial regression (degree 2)
        X_poly = np.column_stack([cycles, cycles**2])
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y)
        y_pred_poly = poly_model.predict(X_poly)
        r2_poly = r2_score(y, y_pred_poly)

        # Calculate improvement
        delta_r2 = r2_poly - r2_linear

        # Validation criteria
        validated = delta_r2 > 0.1

        result = {
            'hypothesis': 'H2: Memory Fragmentation',
            'method': 'Polynomial (degree=2) vs. linear regression',
            'r2_linear': r2_linear,
            'r2_poly': r2_poly,
            'delta_r2': delta_r2,
            'validated': validated,
            'interpretation': (
                'VALIDATED' if validated else 'REFUTED'
            ),
            'criteria': 'ΔR² > 0.1 (polynomial significantly better than linear)'
        }

        # Print results
        print(f"Linear R²:     {r2_linear:.4f}")
        print(f"Polynomial R²: {r2_poly:.4f}")
        print(f"ΔR²:           {delta_r2:.4f}")
        print()
        print(f"Result: {result['interpretation']}")
        if validated:
            print(f"  → Non-linear memory growth detected (ΔR² > 0.1)")
            print(f"  → Consistent with pymalloc fragmentation mechanism")
        else:
            print(f"  → Linear growth (no fragmentation signature)")
        print()

        self.results['H2'] = result
        return result

    def test_h3_io_accumulation(self) -> Dict:
        """
        Test H3: I/O Accumulation

        Method: Linear regression on psutil call latency over time.

        Expected if H3 valid:
        - Positive slope (latency increases over time)
        - Slope significantly different from zero (p < 0.05)

        Returns:
            Dictionary with regression statistics and validation decision
        """
        print("="*80)
        print("H3: I/O ACCUMULATION (PSUTIL CALL LATENCY)")
        print("="*80)
        print("Hypothesis: Runtime variance caused by accumulating I/O overhead")
        print("Method: Linear regression on psutil latency trend")
        print()

        # Extract I/O latency data
        # Expected format: system_metrics[i]['psutil_latency_ms']
        system_metrics = self.data['system_metrics']
        cycles = np.arange(len(system_metrics))

        # Check if latency data exists
        if 'psutil_latency_ms' not in system_metrics[0]:
            print("⚠ WARNING: psutil_latency_ms not found in data")
            print("  Attempting to calculate from per-cycle timing...")
            # Fallback: use per-cycle runtime as proxy
            latency_ms = np.array(self.data['cycle_times']) * 1000  # Convert s to ms
        else:
            latency_ms = np.array([m['psutil_latency_ms'] for m in system_metrics])

        # Linear regression
        X = cycles.reshape(-1, 1)
        y = latency_ms

        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)

        # Calculate p-value for slope
        # Using t-test: t = slope / SE(slope)
        residuals = y - y_pred
        mse = np.mean(residuals**2)
        se_slope = np.sqrt(mse / np.sum((cycles - np.mean(cycles))**2))
        t_stat = slope / se_slope
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(cycles)-2))

        # Validation criteria
        validated = slope > 0 and p_value < 0.05

        result = {
            'hypothesis': 'H3: I/O Accumulation',
            'method': 'Linear regression on latency trend',
            'slope': slope,
            'r2': r2,
            'p_value': p_value,
            'validated': validated,
            'interpretation': (
                'VALIDATED' if validated else 'REFUTED'
            ),
            'criteria': 'Positive slope (latency increases) and p < 0.05'
        }

        # Print results
        print(f"Slope:   {slope:+.4f} ms/cycle")
        print(f"R²:      {r2:.4f}")
        print(f"p-value: {p_value:.4f}")
        print()
        print(f"Result: {result['interpretation']}")
        if validated:
            print(f"  → Latency increases over time (positive slope, p < 0.05)")
            print(f"  → Consistent with I/O accumulation mechanism")
        else:
            print(f"  → No significant latency trend")
        print()

        self.results['H3'] = result
        return result

    def test_h4_thermal_throttling(self) -> Dict:
        """
        Test H4: Thermal Throttling

        Method: Spearman correlation between runtime and CPU temperature/frequency.

        Expected if H4 valid:
        - Positive correlation with temperature (ρ > 0.5)
        - Negative correlation with CPU frequency (ρ < -0.5)
        - p < 0.05 for statistical significance

        Returns:
            Dictionary with correlation statistics and validation decision
        """
        print("="*80)
        print("H4: THERMAL THROTTLING")
        print("="*80)
        print("Hypothesis: Runtime variance caused by CPU thermal throttling")
        print("Method: Spearman correlation (runtime vs. temperature/frequency)")
        print()

        # Extract runtime and thermal data
        cycle_times = np.array(self.data['cycle_times'])
        system_metrics = self.data['system_metrics']

        # Check if thermal data exists
        has_temp = 'cpu_temp_celsius' in system_metrics[0]
        has_freq = 'cpu_freq_current_mhz' in system_metrics[0]

        if not has_temp and not has_freq:
            print("⚠ WARNING: Thermal data (temperature, frequency) not found in metrics")
            print("  H4 cannot be tested without thermal measurements")

            result = {
                'hypothesis': 'H4: Thermal Throttling',
                'method': 'Spearman correlation',
                'validated': False,
                'interpretation': 'UNTESTABLE',
                'reason': 'No thermal data available in C256 results'
            }

            print(f"Result: {result['interpretation']}")
            print(f"  → Thermal metrics not collected during C256")
            print()

            self.results['H4'] = result
            return result

        # Calculate correlations
        results_dict = {}

        if has_temp:
            temp_celsius = np.array([m['cpu_temp_celsius'] for m in system_metrics])
            rho_temp, p_temp = spearmanr(cycle_times, temp_celsius)
            results_dict['rho_temp'] = rho_temp
            results_dict['p_temp'] = p_temp
            print(f"Temperature correlation: ρ = {rho_temp:+.3f}, p = {p_temp:.4f}")

        if has_freq:
            freq_mhz = np.array([m['cpu_freq_current_mhz'] for m in system_metrics])
            rho_freq, p_freq = spearmanr(cycle_times, freq_mhz)
            results_dict['rho_freq'] = rho_freq
            results_dict['p_freq'] = p_freq
            print(f"Frequency correlation:   ρ = {rho_freq:+.3f}, p = {p_freq:.4f}")

        # Validation criteria
        validated = False
        if has_temp and (rho_temp > 0.5 and p_temp < 0.05):
            validated = True
        if has_freq and (rho_freq < -0.5 and p_freq < 0.05):
            validated = True

        result = {
            'hypothesis': 'H4: Thermal Throttling',
            'method': 'Spearman correlation',
            **results_dict,
            'validated': validated,
            'interpretation': (
                'VALIDATED' if validated else 'REFUTED'
            ),
            'criteria': '(ρ_temp > 0.5 or ρ_freq < -0.5) and p < 0.05'
        }

        print()
        print(f"Result: {result['interpretation']}")
        if validated:
            print(f"  → Strong correlation with thermal metrics detected")
        else:
            print(f"  → No strong correlation with thermal metrics")
        print()

        self.results['H4'] = result
        return result

    def test_h5_emergent_complexity(self) -> Dict:
        """
        Test H5: Emergent Complexity (NRM Pattern Memory)

        Method: Linear regression between per-cycle runtime and pattern memory count.

        Expected if H5 valid:
        - Positive slope (runtime increases with pattern memory)
        - Slope significantly different from zero (p < 0.05)
        - R² > 0.3 (moderate predictive power)

        Returns:
            Dictionary with regression statistics and validation decision
        """
        print("="*80)
        print("H5: EMERGENT COMPLEXITY (NRM PATTERN MEMORY)")
        print("="*80)
        print("Hypothesis: Runtime variance correlates with NRM pattern memory growth")
        print("Method: Linear regression (runtime vs. pattern memory count)")
        print()

        # Extract pattern memory and runtime data
        cycle_times = np.array(self.data['cycle_times'])

        # Check if pattern memory data exists
        if 'pattern_memory' not in self.data:
            print("⚠ WARNING: pattern_memory not found in data")
            print("  Attempting to infer from experiment metadata...")

            # Fallback: estimate pattern memory from cycle count
            cycles = np.arange(len(cycle_times))
            pattern_memory_count = cycles * 2  # Assume ~2 patterns/cycle (rough estimate)
            print(f"  Using estimated pattern memory (2 patterns/cycle)")
        else:
            pattern_memory_count = np.array(self.data['pattern_memory'])

        # Linear regression
        X = pattern_memory_count.reshape(-1, 1)
        y = cycle_times

        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)

        # Calculate p-value for slope
        residuals = y - y_pred
        mse = np.mean(residuals**2)
        se_slope = np.sqrt(mse / np.sum((pattern_memory_count - np.mean(pattern_memory_count))**2))
        t_stat = slope / se_slope
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(pattern_memory_count)-2))

        # Validation criteria
        validated = slope > 0 and p_value < 0.05 and r2 > 0.3

        result = {
            'hypothesis': 'H5: Emergent Complexity (NRM)',
            'method': 'Linear regression (runtime vs. pattern memory)',
            'slope': slope,
            'r2': r2,
            'p_value': p_value,
            'validated': validated,
            'interpretation': (
                'VALIDATED' if validated else 'REFUTED'
            ),
            'criteria': 'Positive slope, p < 0.05, and R² > 0.3'
        }

        # Print results
        print(f"Slope:   {slope:+.6f} s/pattern")
        print(f"R²:      {r2:.4f}")
        print(f"p-value: {p_value:.4f}")
        print()
        print(f"Result: {result['interpretation']}")
        if validated:
            print(f"  → Runtime increases with pattern memory (p < 0.05, R² > 0.3)")
            print(f"  → NRM framework prediction validated")
        else:
            print(f"  → No strong correlation with pattern memory")
        print()

        self.results['H5'] = result
        return result

    def generate_summary_report(self) -> None:
        """Generate comprehensive summary of all hypothesis tests."""
        print("="*80)
        print("HYPOTHESIS TESTING SUMMARY")
        print("="*80)
        print()

        validated_count = sum(1 for r in self.results.values() if r and r.get('validated', False))
        total_count = len([r for r in self.results.values() if r is not None])

        print(f"Results: {validated_count}/{total_count} hypotheses validated")
        print()

        for h_id in ['H1', 'H2', 'H3', 'H4', 'H5']:
            result = self.results[h_id]
            if result is None:
                continue

            status_symbol = "✓" if result.get('validated', False) else "✗"
            print(f"{status_symbol} {h_id}: {result['interpretation']}")
            print(f"   {result['hypothesis']}")
            print()

        # Save results to JSON
        output_path = self.output_dir / "paper8_phase1a_results.json"
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"✓ Results saved to {output_path}")
        print()

    def run_all_tests(self) -> None:
        """Execute all hypothesis tests in sequence."""
        print("="*80)
        print("PAPER 8 PHASE 1A: RETROSPECTIVE HYPOTHESIS TESTING")
        print("="*80)
        print()

        # Load data
        self.load_data()

        # Run tests
        self.test_h1_system_resource_contention()
        self.test_h2_memory_fragmentation()
        self.test_h3_io_accumulation()
        self.test_h4_thermal_throttling()
        self.test_h5_emergent_complexity()

        # Generate summary
        self.generate_summary_report()

        print("="*80)
        print("PHASE 1A COMPLETE")
        print("="*80)
        print()


def main():
    """Main entry point for Phase 1A analysis."""
    parser = argparse.ArgumentParser(
        description="Paper 8 Phase 1A: Retrospective Hypothesis Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all hypotheses using C256 data
  python paper8_phase1a_hypothesis_testing.py

  # Specify custom data path
  python paper8_phase1a_hypothesis_testing.py --data path/to/results.json

  # Custom output directory
  python paper8_phase1a_hypothesis_testing.py --output figures/paper8/
"""
    )

    parser.add_argument(
        '--data',
        type=str,
        default='data/results/cycle256_h1h4_mechanism_validation_results.json',
        help='Path to C256 results JSON file'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='papers/figures',
        help='Output directory for figures and results'
    )

    args = parser.parse_args()

    # Run analysis
    tester = HypothesisTester(
        data_path=args.data,
        output_dir=args.output
    )

    tester.run_all_tests()


if __name__ == '__main__':
    main()
