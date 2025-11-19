#!/usr/bin/env python3
"""
Paper 5C: Scaling Behavior Analysis - Experimental Framework

Tests NRM scale invariance by varying population sizes (50-800 agents)
while holding other parameters constant. Applies pattern mining from
Paper 5D to detect scaling exponents and critical population thresholds.

Research Question: How do NRM patterns change with agent population size?

Hypothesis: Temporal patterns are scale-invariant (α ≈ 0), while memory
consistency scales super-linearly (α > 0) due to redundancy effects.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class ScalingBehaviorConfig:
    """Configuration for scaling behavior experiments."""

    def __init__(self):
        """Initialize configuration with population size sweep."""

        # Population sizes to test (geometric progression)
        self.population_sizes = [50, 100, 200, 400, 800]

        # Fixed parameters (from C171/C175 stable regime)
        self.frequency = 2.5  # Hz (known stable)
        self.configuration = "baseline"  # Full NRM framework
        self.cycles_per_experiment = 5000
        self.sampling_window = 100  # Snapshot every 100 cycles (50 snapshots)

        # Replication seeds
        self.seeds = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # 10 replications

        # Output directory
        self.output_dir = Path("data/results/paper5c")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_experiment_conditions(self) -> List[Dict]:
        """Generate all experimental conditions.

        Returns:
            List of condition dictionaries
        """
        conditions = []

        for pop_size in self.population_sizes:
            for seed in self.seeds:
                condition = {
                    'population_size': pop_size,
                    'frequency': self.frequency,
                    'configuration': self.configuration,
                    'cycles': self.cycles_per_experiment,
                    'sampling_window': self.sampling_window,
                    'seed': seed,
                    'condition_name': f"pop{pop_size}_seed{seed}"
                }
                conditions.append(condition)

        return conditions

    def estimate_runtime(self, runtime_per_cycle: float = 0.0003) -> Dict:
        """Estimate total experiment runtime.

        Args:
            runtime_per_cycle: Seconds per simulation cycle (from C171/C175 benchmarks)

        Returns:
            Dictionary with runtime estimates
        """
        total_conditions = len(self.population_sizes) * len(self.seeds)
        total_cycles = total_conditions * self.cycles_per_experiment
        total_seconds = total_cycles * runtime_per_cycle
        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60

        # Breakdown by population size
        breakdown = {}
        for pop_size in self.population_sizes:
            count = len(self.seeds)
            cycles = count * self.cycles_per_experiment
            minutes = (cycles * runtime_per_cycle) / 60

            breakdown[f'pop{pop_size}'] = {
                'count': count,
                'total_cycles': cycles,
                'total_minutes': round(minutes, 1)
            }

        return {
            'total_conditions': total_conditions,
            'total_cycles': total_cycles,
            'total_seconds': round(total_seconds, 1),
            'total_minutes': round(total_minutes, 1),
            'total_hours': round(total_hours, 2),
            'breakdown': breakdown
        }


class ScalingBehaviorAnalyzer:
    """Analyze scaling behavior from experimental results."""

    def __init__(self, results_dir: Path):
        """Initialize analyzer.

        Args:
            results_dir: Directory containing experimental results
        """
        self.results_dir = Path(results_dir)
        self.results = {}

    def load_results(self, experiment_prefix: str = "pop") -> Dict:
        """Load all experimental results.

        Args:
            experiment_prefix: Prefix for result files

        Returns:
            Dictionary of results by population size
        """
        result_files = sorted(self.results_dir.glob(f"{experiment_prefix}*.json"))

        for result_file in result_files:
            with open(result_file, 'r') as f:
                data = json.load(f)
                pop_size = data.get('metadata', {}).get('population_size', 'unknown')

                if pop_size not in self.results:
                    self.results[pop_size] = []

                self.results[pop_size].append(data)

        return self.results

    def compute_scaling_exponents(self, metric_name: str) -> Dict:
        """Compute scaling exponent for a given metric.

        Formula: E(N) = E₀ · N^α
        Where α is the scaling exponent:
        - α = 0: Scale-invariant (constant with size)
        - α = 1: Linear scaling
        - α < 1: Sub-linear (diminishing returns)
        - α > 1: Super-linear (increasing returns)

        Args:
            metric_name: Name of metric to analyze

        Returns:
            Dictionary with scaling exponent and fit quality
        """
        population_sizes = []
        metric_values = []

        for pop_size, experiments in sorted(self.results.items()):
            if pop_size == 'unknown':
                continue

            # Compute mean metric across replications
            values = [self._extract_metric(exp, metric_name) for exp in experiments]
            mean_value = np.mean([v for v in values if v is not None])

            population_sizes.append(pop_size)
            metric_values.append(mean_value)

        # Log-log linear fit to get scaling exponent
        # log(E) = log(E₀) + α · log(N)
        if len(population_sizes) >= 3:
            log_N = np.log(population_sizes)
            log_E = np.log(metric_values)

            # Linear regression in log-log space
            coeffs = np.polyfit(log_N, log_E, 1)
            alpha = coeffs[0]  # Scaling exponent
            log_E0 = coeffs[1]  # Intercept (baseline)
            E0 = np.exp(log_E0)

            # Compute R² for fit quality
            predicted = np.polyval(coeffs, log_N)
            residuals = log_E - predicted
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((log_E - np.mean(log_E))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            return {
                'metric': metric_name,
                'scaling_exponent': round(alpha, 3),
                'baseline': round(E0, 3),
                'r_squared': round(r_squared, 3),
                'population_sizes': population_sizes,
                'metric_values': [round(v, 3) for v in metric_values],
                'interpretation': self._interpret_exponent(alpha)
            }

        return None

    def _extract_metric(self, experiment: Dict, metric_name: str) -> float:
        """Extract specific metric from experiment results.

        Args:
            experiment: Experiment results dictionary
            metric_name: Name of metric

        Returns:
            Metric value or None
        """
        # Map metric names to extraction logic
        if metric_name == 'pattern_count':
            patterns = experiment.get('patterns', {})
            return sum(len(p) for p in patterns.values())

        elif metric_name == 'temporal_stability':
            patterns = experiment.get('patterns', {}).get('temporal', [])
            if patterns:
                stabilities = [p.get('stability', 0) for p in patterns]
                return np.mean(stabilities)
            return None

        elif metric_name == 'memory_consistency':
            patterns = experiment.get('patterns', {}).get('memory', [])
            if patterns:
                consistencies = [p.get('consistency', 0) for p in patterns]
                return np.mean(consistencies)
            return None

        elif metric_name == 'composition_events':
            return experiment.get('metadata', {}).get('avg_composition_events', None)

        elif metric_name == 'final_population':
            return experiment.get('metadata', {}).get('final_agent_count', None)

        return None

    def _interpret_exponent(self, alpha: float) -> str:
        """Interpret scaling exponent.

        Args:
            alpha: Scaling exponent

        Returns:
            Human-readable interpretation
        """
        if abs(alpha) < 0.1:
            return "Scale-invariant (independent of population size)"
        elif 0.9 <= alpha <= 1.1:
            return "Linear scaling (proportional to population)"
        elif 0.1 <= alpha < 0.9:
            return "Sub-linear scaling (diminishing returns)"
        elif alpha > 1.1:
            return "Super-linear scaling (increasing returns)"
        elif alpha < -0.1:
            return "Inverse scaling (decreases with population)"
        else:
            return "Weak scaling relationship"

    def find_minimum_viable_population(self) -> Dict:
        """Find critical population threshold for pattern emergence.

        Returns:
            Dictionary with minimum viable population and transition metrics
        """
        population_sizes = sorted([p for p in self.results.keys() if p != 'unknown'])
        pattern_counts = []

        for pop_size in population_sizes:
            experiments = self.results[pop_size]
            mean_patterns = np.mean([
                sum(len(p) for p in exp.get('patterns', {}).values())
                for exp in experiments
            ])
            pattern_counts.append(mean_patterns)

        # Find first population with substantial patterns (>5)
        threshold_idx = next((i for i, count in enumerate(pattern_counts) if count > 5), None)

        if threshold_idx is not None:
            mvp = population_sizes[threshold_idx]
            return {
                'minimum_viable_population': mvp,
                'pattern_count_at_threshold': pattern_counts[threshold_idx],
                'population_sizes_tested': population_sizes,
                'pattern_counts': pattern_counts
            }

        return None


def generate_experimental_plan():
    """Generate experimental plan for Paper 5C."""
    print("="*70)
    print("PAPER 5C: SCALING BEHAVIOR ANALYSIS - EXPERIMENTAL PLAN")
    print("="*70)

    config = ScalingBehaviorConfig()

    print(f"\nPopulation sizes: {config.population_sizes}")
    print(f"Frequency: {config.frequency} Hz (fixed)")
    print(f"Configuration: {config.configuration}")
    print(f"Cycles per experiment: {config.cycles_per_experiment}")
    print(f"Seeds (replications): {len(config.seeds)}")

    # Generate conditions
    conditions = config.generate_experiment_conditions()
    print(f"\nTotal conditions: {len(conditions)}")

    # Runtime estimate
    runtime = config.estimate_runtime()
    print(f"\nRuntime estimates:")
    print(f"  Total conditions: {runtime['total_conditions']}")
    print(f"  Total cycles: {runtime['total_cycles']:,}")
    print(f"  Total time: {runtime['total_minutes']:.1f} minutes ({runtime['total_hours']:.2f} hours)")

    print(f"\nBreakdown by population size:")
    for pop, stats in runtime['breakdown'].items():
        print(f"  {pop}: {stats['count']} experiments, {stats['total_minutes']} minutes")

    # Save experimental plan
    plan = {
        'metadata': {
            'paper': 'Paper 5C - Scaling Behavior Analysis',
            'date_created': datetime.now().isoformat(),
            'confidence': '⭐⭐⭐⭐☆',
            'timeline': '2-3 weeks',
            'publication_target': 'Complexity or Journal of Complex Networks'
        },
        'conditions': conditions,
        'population_sizes': config.population_sizes,
        'fixed_parameters': {
            'frequency': config.frequency,
            'configuration': config.configuration,
            'cycles': config.cycles_per_experiment,
            'sampling_window': config.sampling_window,
            'seeds': config.seeds
        },
        'runtime_estimates': runtime
    }

    output_file = config.output_dir / "paper5c_experimental_plan.json"
    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"\nExperimental plan saved to: {output_file}")
    print("\n" + "="*70)
    print("PLAN GENERATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Review experimental plan")
    print("2. Execute experiments (after Papers 3-4 complete)")
    print("3. Apply Paper 5D pattern mining tools")
    print("4. Compute scaling exponents")
    print("5. Generate figures and complete manuscript")


if __name__ == "__main__":
    generate_experimental_plan()
