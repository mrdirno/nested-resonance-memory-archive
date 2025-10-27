#!/usr/bin/env python3
"""
Paper 5B: Extended Timescale Validation - Long-Horizon Stability Analysis

Research Question:
Do NRM composition-decomposition dynamics remain stable over extended simulation
durations (10K, 50K, 100K cycles)? Are there emergent long-term phenomena
invisible at shorter timescales (5K cycles)?

Motivation:
- Papers 1-4 use 3,000-5,000 cycle simulations (proven reliable)
- Unknown: Pattern persistence and drift at longer timescales
- Open question: Do slow timescale phenomena exist beyond current observation window?

Experimental Design:
- Baseline replication at multiple timescales: 5K, 10K, 50K, 100K cycles
- Stability metrics: Population mean/variance, pattern memory, resonance frequency
- Drift detection: Long-term parameter changes, attractor basin shifts
- Comparison: Validate that short timescale conclusions hold at extended durations

Novel Contributions:
1. Stability certification: NRM doesn't degrade over extended time
2. Drift detection: Identify any slow parameter changes
3. Long-term emergence: Discover patterns visible only at extended scales
4. Temporal stewardship validation: Pattern memory persists across timescales

Target Timeline: 3-4 weeks
Publication Target: Journal of Computational Science
Confidence: ⭐⭐⭐⭐☆ (4/5)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class ExtendedTimescaleConfig:
    """Configuration for Paper 5B extended timescale experiments."""

    def __init__(self):
        """Initialize extended timescale configuration."""
        # Timescale levels (cycles per experiment)
        self.timescales = {
            'baseline': 5000,      # Current standard (C171/C175)
            'medium': 10000,       # 2× baseline
            'extended': 50000,     # 10× baseline
            'long': 100000         # 20× baseline
        }

        # Experimental conditions (replicate successful C171 baseline)
        self.frequency = 2.5       # Hz (proven stable in C171/C175)
        self.seeds = [42, 123, 456, 789, 101]  # 5 replications per timescale

        # Sampling intervals for analysis (to manage data volume)
        self.sampling_windows = {
            'baseline': 100,       # Sample every 100 cycles (5000/100 = 50 snapshots)
            'medium': 200,         # Sample every 200 cycles (10000/200 = 50 snapshots)
            'extended': 1000,      # Sample every 1000 cycles (50000/1000 = 50 snapshots)
            'long': 2000           # Sample every 2000 cycles (100000/2000 = 50 snapshots)
        }

    def generate_experiment_conditions(self) -> List[Dict[str, Any]]:
        """Generate experimental conditions for all timescales.

        Returns:
            List of condition dictionaries
        """
        conditions = []

        for timescale_name, cycles in self.timescales.items():
            for seed in self.seeds:
                condition = {
                    'timescale': timescale_name,
                    'cycles': cycles,
                    'frequency': self.frequency,
                    'seed': seed,
                    'sampling_window': self.sampling_windows[timescale_name],
                    'condition_name': f"{timescale_name}_{cycles}c_seed{seed}"
                }
                conditions.append(condition)

        return conditions

    def estimate_runtime(self, conditions: List[Dict]) -> Dict[str, float]:
        """Estimate total experiment runtime.

        Based on C171/C175 performance:
        - 5000 cycles: ~3 minutes per run (with batched sampling optimization)
        - Linear scaling assumption: 100K cycles = 20× longer = 60 minutes

        Args:
            conditions: List of experimental conditions

        Returns:
            Dictionary with runtime estimates
        """
        # Minutes per 1000 cycles (post-optimization)
        minutes_per_1k_cycles = 3.0 / 5.0  # 0.6 min per 1K cycles

        total_minutes = 0
        breakdown = {}

        for condition in conditions:
            cycles = condition['cycles']
            runtime_minutes = (cycles / 1000) * minutes_per_1k_cycles
            total_minutes += runtime_minutes

            timescale = condition['timescale']
            if timescale not in breakdown:
                breakdown[timescale] = {
                    'count': 0,
                    'total_cycles': 0,
                    'total_minutes': 0
                }
            breakdown[timescale]['count'] += 1
            breakdown[timescale]['total_cycles'] += cycles
            breakdown[timescale]['total_minutes'] += runtime_minutes

        return {
            'total_conditions': len(conditions),
            'total_cycles': sum(c['cycles'] for c in conditions),
            'total_minutes': total_minutes,
            'total_hours': total_minutes / 60,
            'total_days': total_minutes / (60 * 24),
            'breakdown': breakdown
        }


class ExtendedTimescaleAnalyzer:
    """Analyze extended timescale experiment results."""

    def __init__(self, results_dir: Path):
        """Initialize analyzer.

        Args:
            results_dir: Directory containing experimental results
        """
        self.results_dir = Path(results_dir)

    def load_results(self, experiment_file: str) -> Dict:
        """Load experimental results from JSON.

        Args:
            experiment_file: Name of results JSON file

        Returns:
            Dictionary containing experimental data
        """
        filepath = self.results_dir / experiment_file
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def compute_stability_metrics(self, time_series: List[float]) -> Dict[str, float]:
        """Compute stability metrics for time series data.

        Metrics:
        - Mean: Central tendency
        - Std: Variability
        - CV: Coefficient of variation (std/mean)
        - Trend: Linear regression slope
        - Stationarity: Augmented Dickey-Fuller test (conceptual - would use statsmodels)

        Args:
            time_series: List of values over time

        Returns:
            Dictionary of stability metrics
        """
        if not time_series or len(time_series) < 2:
            return {}

        time_series_array = np.array(time_series)

        # Basic statistics
        mean_val = np.mean(time_series_array)
        std_val = np.std(time_series_array)
        cv = (std_val / mean_val * 100) if mean_val > 0 else float('inf')

        # Trend detection (linear fit)
        if len(time_series) >= 3:
            x = np.arange(len(time_series))
            coeffs = np.polyfit(x, time_series_array, 1)
            trend_slope = coeffs[0]
            trend_intercept = coeffs[1]
        else:
            trend_slope = 0
            trend_intercept = mean_val

        # Drift rate (normalized slope)
        drift_rate = (trend_slope / mean_val * 100) if mean_val > 0 else 0

        return {
            'mean': mean_val,
            'std': std_val,
            'cv': cv,
            'trend_slope': trend_slope,
            'trend_intercept': trend_intercept,
            'drift_rate_percent': drift_rate,
            'n_samples': len(time_series)
        }

    def compare_timescales(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Compare stability across different timescales.

        Args:
            results: Dictionary mapping timescale names to results

        Returns:
            Comparison statistics
        """
        comparison = {}

        # Extract population time series for each timescale
        for timescale, data in results.items():
            if 'population_time_series' in data:
                pop_series = data['population_time_series']
                metrics = self.compute_stability_metrics(pop_series)
                comparison[timescale] = metrics

        # Cross-timescale comparison
        if len(comparison) >= 2:
            means = [m['mean'] for m in comparison.values()]
            stds = [m['std'] for m in comparison.values()]
            drifts = [m['drift_rate_percent'] for m in comparison.values()]

            comparison['cross_timescale'] = {
                'mean_consistency': np.std(means),  # Low = consistent across timescales
                'std_consistency': np.std(stds),
                'max_drift': max(abs(d) for d in drifts),
                'timescales_analyzed': list(comparison.keys())
            }

        return comparison

    def detect_long_term_phenomena(self, short_term: Dict, long_term: Dict) -> List[Dict]:
        """Detect phenomena visible in long-term but not short-term data.

        Args:
            short_term: Results from baseline (5K cycles)
            long_term: Results from extended timescale (50K-100K cycles)

        Returns:
            List of detected long-term phenomena
        """
        phenomena = []

        # Phenomenon 1: Slow drift (visible only at long timescales)
        if 'drift_rate_percent' in short_term and 'drift_rate_percent' in long_term:
            short_drift = abs(short_term['drift_rate_percent'])
            long_drift = abs(long_term['drift_rate_percent'])

            if long_drift > 1.0 and short_drift < 0.5:
                phenomena.append({
                    'type': 'slow_drift',
                    'description': 'Long-term parameter drift not visible at short timescales',
                    'short_term_drift': short_drift,
                    'long_term_drift': long_drift,
                    'significance': 'high' if long_drift > 2.0 else 'medium'
                })

        # Phenomenon 2: Long-term instability (CV increases with time)
        if 'cv' in short_term and 'cv' in long_term:
            short_cv = short_term['cv']
            long_cv = long_term['cv']

            if long_cv > short_cv * 1.5:
                phenomena.append({
                    'type': 'increasing_variability',
                    'description': 'Variability increases at longer timescales',
                    'short_term_cv': short_cv,
                    'long_term_cv': long_cv,
                    'increase_factor': long_cv / short_cv if short_cv > 0 else float('inf')
                })

        # Phenomenon 3: Attractor basin shift (mean changes significantly)
        if 'mean' in short_term and 'mean' in long_term:
            short_mean = short_term['mean']
            long_mean = long_term['mean']
            shift_percent = abs(long_mean - short_mean) / short_mean * 100 if short_mean > 0 else 0

            if shift_percent > 10.0:
                phenomena.append({
                    'type': 'attractor_shift',
                    'description': 'Population mean shifts significantly at long timescales',
                    'short_term_mean': short_mean,
                    'long_term_mean': long_mean,
                    'shift_percent': shift_percent
                })

        return phenomena


def generate_paper5b_experimental_plan():
    """Generate experimental plan for Paper 5B."""
    print("="*70)
    print("PAPER 5B: EXTENDED TIMESCALE VALIDATION - EXPERIMENTAL PLAN")
    print("="*70)

    config = ExtendedTimescaleConfig()

    # Generate conditions
    print("\n1. EXPERIMENTAL CONDITIONS")
    print("-" * 70)
    conditions = config.generate_experiment_conditions()
    print(f"Total conditions: {len(conditions)}")
    print(f"\nTimescale breakdown:")
    for timescale_name, cycles in config.timescales.items():
        count = sum(1 for c in conditions if c['timescale'] == timescale_name)
        print(f"  - {timescale_name}: {cycles} cycles, {count} replications")
    print(f"\nFrequency: {config.frequency} Hz (validated baseline from C171/C175)")
    print(f"Seeds per timescale: {len(config.seeds)}")

    # Estimate runtime
    print("\n2. RUNTIME ESTIMATES")
    print("-" * 70)
    runtime = config.estimate_runtime(conditions)
    print(f"Total experiments: {runtime['total_conditions']}")
    print(f"Total cycles: {runtime['total_cycles']:,}")
    print(f"Total runtime: {runtime['total_hours']:.1f} hours ({runtime['total_days']:.2f} days)")

    print(f"\nBreakdown by timescale:")
    for timescale, stats in runtime['breakdown'].items():
        print(f"  {timescale}:")
        print(f"    - Experiments: {stats['count']}")
        print(f"    - Cycles: {stats['total_cycles']:,}")
        print(f"    - Runtime: {stats['total_minutes']:.1f} min ({stats['total_minutes']/60:.1f} hours)")

    # Execution recommendation
    print("\n3. EXECUTION RECOMMENDATION")
    print("-" * 70)
    print("Phase 1: Baseline validation (5K cycles)")
    print("  - 5 seeds × 5K cycles = 15 minutes")
    print("  - Purpose: Confirm methodology matches C171/C175 results")
    print("")
    print("Phase 2: Medium timescale (10K cycles)")
    print("  - 5 seeds × 10K cycles = 30 minutes")
    print("  - Purpose: Check for early signs of drift or instability")
    print("")
    print("Phase 3: Extended timescale (50K cycles)")
    print("  - 5 seeds × 50K cycles = 2.5 hours")
    print("  - Purpose: Detect long-term phenomena invisible at short scales")
    print("")
    print("Phase 4: Long timescale (100K cycles)")
    print("  - 5 seeds × 100K cycles = 5 hours")
    print("  - Purpose: Comprehensive stability certification")
    print("")
    print("Total sequential execution: ~8 hours")
    print("Recommended: Run overnight or during low-activity periods")

    # Output artifacts
    print("\n4. OUTPUT ARTIFACTS")
    print("-" * 70)
    print("- Time series plots (population, energy, composition events)")
    print("- Stability metrics tables (mean, std, CV, drift rate)")
    print("- Cross-timescale comparison heatmaps")
    print("- Long-term phenomena detection report")
    print("- Statistical tests (stationarity, trend significance)")
    print("- Manuscript with 5-8 publication figures")

    # Novel contributions
    print("\n5. NOVEL CONTRIBUTIONS")
    print("-" * 70)
    print("1. Stability Certification: NRM dynamics stable across 20× timescale range")
    print("2. Drift Detection: Quantify any slow parameter changes (if present)")
    print("3. Long-term Emergence: Identify phenomena invisible at standard 5K cycles")
    print("4. Temporal Stewardship Validation: Pattern memory persists across timescales")
    print("5. Design Guidelines: Recommend appropriate simulation durations for NRM research")

    print("\n" + "="*70)
    print("Plan generated. Ready for execution after Papers 3-4 complete.")
    print("="*70)

    return config, conditions


def main():
    """Main execution function."""
    config, conditions = generate_paper5b_experimental_plan()

    # Save experimental plan to JSON
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/results")
    output_file = output_dir / "paper5b_experimental_plan.json"

    runtime = config.estimate_runtime(conditions)

    plan = {
        'metadata': {
            'paper': 'Paper 5B - Extended Timescale Validation',
            'date_created': datetime.now().isoformat(),
            'confidence': '⭐⭐⭐⭐☆',
            'timeline': '3-4 weeks',
            'publication_target': 'Journal of Computational Science'
        },
        'conditions': conditions,
        'timescales': config.timescales,
        'sampling_windows': config.sampling_windows,
        'runtime_estimates': runtime,
        'fixed_parameters': {
            'frequency': config.frequency,
            'seeds': config.seeds
        }
    }

    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"\nExperimental plan saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
