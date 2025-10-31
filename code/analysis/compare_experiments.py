#!/usr/bin/env python3
"""
Experiment Comparison Utility

Compare multiple experiments across key metrics:
- Runtime and variance
- Population dynamics (mean, std, CV)
- Synergy analysis (for factorial pairs)
- Statistical significance tests
- Side-by-side metric comparison

Supports Paper 8 Phase 1B (C256 vs C257-C260) and Paper 3 cross-pair analysis.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
import sys

try:
    import numpy as np
    from scipy import stats
except ImportError:
    print("Error: numpy and scipy required. Install with: pip install numpy scipy", file=sys.stderr)
    sys.exit(1)

class ExperimentComparator:
    """Compare multiple experiments across key metrics."""

    def __init__(self, experiment_paths: Dict[str, Path]):
        """
        Initialize comparator with experiment result files.

        Args:
            experiment_paths: Dict mapping experiment IDs to result JSON paths
                             e.g., {'C256': Path('cycle256_results.json')}
        """
        self.experiment_paths = experiment_paths
        self.experiments = {}
        self.load_experiments()

    def load_experiments(self):
        """Load experiment data from JSON files."""
        for exp_id, path in self.experiment_paths.items():
            if not path.exists():
                print(f"Warning: {exp_id} results not found at {path}", file=sys.stderr)
                continue

            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.experiments[exp_id] = data
                    print(f"Loaded {exp_id}: {len(data.get('results', []))} conditions")
            except Exception as e:
                print(f"Error loading {exp_id}: {e}", file=sys.stderr)

    def compare_runtimes(self) -> Dict:
        """Compare experiment runtimes."""
        runtime_data = {}

        for exp_id, data in self.experiments.items():
            runtime = data.get('metadata', {}).get('total_runtime_seconds', 0)
            runtime_hours = runtime / 3600

            runtime_data[exp_id] = {
                'runtime_seconds': runtime,
                'runtime_hours': runtime_hours,
                'runtime_formatted': f"{runtime_hours:.2f}h"
            }

        # Calculate speedups (if baseline provided)
        if 'C256' in runtime_data or 'baseline' in runtime_data:
            baseline_key = 'C256' if 'C256' in runtime_data else 'baseline'
            baseline_runtime = runtime_data[baseline_key]['runtime_seconds']

            for exp_id in runtime_data:
                if exp_id != baseline_key:
                    speedup = baseline_runtime / runtime_data[exp_id]['runtime_seconds']
                    runtime_data[exp_id]['speedup_vs_baseline'] = f"{speedup:.1f}×"

        return {
            'runtimes': runtime_data,
            'comparison': 'Baseline' if len(runtime_data) > 1 else 'Single experiment'
        }

    def compare_populations(self) -> Dict:
        """Compare population dynamics across experiments."""
        pop_data = {}

        for exp_id, data in self.experiments.items():
            results = data.get('results', [])

            # Extract population data from all conditions
            all_pops = []
            for condition in results:
                pops = condition.get('mean_population', [])
                if isinstance(pops, list):
                    all_pops.extend(pops)
                elif isinstance(pops, (int, float)):
                    all_pops.append(pops)

            if all_pops:
                pop_data[exp_id] = {
                    'mean': np.mean(all_pops),
                    'std': np.std(all_pops),
                    'min': np.min(all_pops),
                    'max': np.max(all_pops),
                    'cv': np.std(all_pops) / np.mean(all_pops) if np.mean(all_pops) > 0 else 0
                }

        return {'populations': pop_data}

    def compare_variance(self) -> Dict:
        """
        Compare runtime variance across experiments.

        Critical for Paper 8 Phase 1B: if H2+H3 correct, optimization
        should eliminate variance.
        """
        variance_data = {}

        for exp_id, data in self.experiments.items():
            # Extract per-cycle runtimes if available
            cycle_times = data.get('cycle_times', [])

            if cycle_times and len(cycle_times) > 1:
                variance_data[exp_id] = {
                    'variance': float(np.var(cycle_times)),
                    'std': float(np.std(cycle_times)),
                    'cv': float(np.std(cycle_times) / np.mean(cycle_times)) if np.mean(cycle_times) > 0 else 0,
                    'range': float(np.max(cycle_times) - np.min(cycle_times))
                }

        # Variance reduction analysis (if baseline exists)
        if 'C256' in variance_data or 'baseline' in variance_data:
            baseline_key = 'C256' if 'C256' in variance_data else 'baseline'
            baseline_var = variance_data[baseline_key]['variance']

            for exp_id in variance_data:
                if exp_id != baseline_key and baseline_var > 0:
                    reduction = (1 - variance_data[exp_id]['variance'] / baseline_var) * 100
                    variance_data[exp_id]['variance_reduction_pct'] = reduction

        return {'variance': variance_data}

    def statistical_tests(self) -> Dict:
        """
        Perform statistical significance tests between experiments.

        Tests:
        - Independent samples t-test (runtime differences)
        - Levene's test (variance equality)
        - Effect size (Cohen's d)
        """
        if len(self.experiments) < 2:
            return {'message': 'Need at least 2 experiments for statistical tests'}

        results = {}

        # Compare first two experiments (or baseline vs first optimized)
        exp_ids = list(self.experiments.keys())
        exp1_id = exp_ids[0]
        exp2_id = exp_ids[1] if len(exp_ids) > 1 else None

        if not exp2_id:
            return {'message': 'Need at least 2 experiments for comparison'}

        exp1_data = self.experiments[exp1_id]
        exp2_data = self.experiments[exp2_id]

        # Extract cycle times
        times1 = exp1_data.get('cycle_times', [])
        times2 = exp2_data.get('cycle_times', [])

        if len(times1) > 1 and len(times2) > 1:
            # Independent samples t-test
            t_stat, t_p = stats.ttest_ind(times1, times2)

            # Levene's test for equal variances
            levene_stat, levene_p = stats.levene(times1, times2)

            # Cohen's d effect size
            pooled_std = np.sqrt((np.var(times1) + np.var(times2)) / 2)
            cohens_d = (np.mean(times1) - np.mean(times2)) / pooled_std if pooled_std > 0 else 0

            results = {
                'comparison': f"{exp1_id} vs {exp2_id}",
                't_test': {
                    't_statistic': float(t_stat),
                    'p_value': float(t_p),
                    'significant': t_p < 0.05
                },
                'levene_test': {
                    'statistic': float(levene_stat),
                    'p_value': float(levene_p),
                    'equal_variances': levene_p > 0.05
                },
                'effect_size': {
                    'cohens_d': float(cohens_d),
                    'interpretation': interpret_cohens_d(cohens_d)
                }
            }

        return results

    def synergy_analysis(self) -> Dict:
        """
        Analyze synergy for factorial experiments (Paper 3).

        Synergy = Observed(A+B) - Predicted(A+B)
        where Predicted(A+B) = Observed(A) + Observed(B) - Observed(OFF)

        Positive synergy = cooperative (better than additive)
        Negative synergy = antagonistic (worse than additive)
        """
        synergy_results = {}

        for exp_id, data in self.experiments.items():
            results = data.get('results', [])

            # Need 4 conditions for factorial: OFF-OFF, ON-OFF, OFF-ON, ON-ON
            if len(results) != 4:
                continue

            # Extract conditions (assume standard order)
            conditions = {r['condition_name']: r for r in results}

            # Check if we have factorial structure
            required = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
            if not all(cond in conditions for cond in required):
                continue

            # Calculate synergy for each metric
            off_off = np.mean(conditions['OFF-OFF'].get('mean_population', [0]))
            on_off = np.mean(conditions['ON-OFF'].get('mean_population', [0]))
            off_on = np.mean(conditions['OFF-ON'].get('mean_population', [0]))
            on_on = np.mean(conditions['ON-ON'].get('mean_population', [0]))

            # Additive prediction: ON-OFF + OFF-ON - OFF-OFF
            predicted = on_off + off_on - off_off
            observed = on_on
            synergy = observed - predicted

            # Classification
            if abs(synergy) < 0.1 * off_off:  # Within 10% of baseline
                classification = 'ADDITIVE'
            elif synergy > 0:
                classification = 'SYNERGISTIC'
            else:
                classification = 'ANTAGONISTIC'

            synergy_results[exp_id] = {
                'observed_combined': observed,
                'predicted_combined': predicted,
                'synergy': synergy,
                'synergy_pct': (synergy / off_off * 100) if off_off > 0 else 0,
                'classification': classification
            }

        return {'synergy': synergy_results}

    def generate_summary_report(self) -> str:
        """Generate comprehensive comparison report."""
        lines = []
        lines.append("=" * 80)
        lines.append("EXPERIMENT COMPARISON REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Experiments loaded
        lines.append(f"Experiments: {len(self.experiments)}")
        for exp_id in self.experiments.keys():
            lines.append(f"  - {exp_id}")
        lines.append("")

        # Runtime comparison
        runtime_comp = self.compare_runtimes()
        lines.append("RUNTIME COMPARISON")
        lines.append("-" * 80)
        for exp_id, data in runtime_comp['runtimes'].items():
            speedup = f" (speedup: {data['speedup_vs_baseline']})" if 'speedup_vs_baseline' in data else ""
            lines.append(f"  {exp_id}: {data['runtime_formatted']}{speedup}")
        lines.append("")

        # Population comparison
        pop_comp = self.compare_populations()
        if pop_comp['populations']:
            lines.append("POPULATION DYNAMICS")
            lines.append("-" * 80)
            for exp_id, data in pop_comp['populations'].items():
                lines.append(f"  {exp_id}:")
                lines.append(f"    Mean: {data['mean']:.2f}")
                lines.append(f"    Std: {data['std']:.2f}")
                lines.append(f"    CV: {data['cv']:.2%}")
                lines.append(f"    Range: [{data['min']:.2f}, {data['max']:.2f}]")
            lines.append("")

        # Variance comparison
        var_comp = self.compare_variance()
        if var_comp['variance']:
            lines.append("VARIANCE COMPARISON")
            lines.append("-" * 80)
            for exp_id, data in var_comp['variance'].items():
                reduction = f" (reduction: {data['variance_reduction_pct']:.1f}%)" if 'variance_reduction_pct' in data else ""
                lines.append(f"  {exp_id}:")
                lines.append(f"    Variance: {data['variance']:.4f}")
                lines.append(f"    Std: {data['std']:.4f}")
                lines.append(f"    CV: {data['cv']:.2%}{reduction}")
            lines.append("")

        # Statistical tests
        stats_results = self.statistical_tests()
        if 't_test' in stats_results:
            lines.append("STATISTICAL TESTS")
            lines.append("-" * 80)
            lines.append(f"  Comparison: {stats_results['comparison']}")
            lines.append(f"  t-test: t={stats_results['t_test']['t_statistic']:.4f}, p={stats_results['t_test']['p_value']:.4f}")
            lines.append(f"    Significant: {stats_results['t_test']['significant']}")
            lines.append(f"  Levene's test: W={stats_results['levene_test']['statistic']:.4f}, p={stats_results['levene_test']['p_value']:.4f}")
            lines.append(f"    Equal variances: {stats_results['levene_test']['equal_variances']}")
            lines.append(f"  Effect size: Cohen's d={stats_results['effect_size']['cohens_d']:.4f} ({stats_results['effect_size']['interpretation']})")
            lines.append("")

        # Synergy analysis
        synergy_comp = self.synergy_analysis()
        if synergy_comp.get('synergy'):
            lines.append("SYNERGY ANALYSIS (Factorial Pairs)")
            lines.append("-" * 80)
            for exp_id, data in synergy_comp['synergy'].items():
                lines.append(f"  {exp_id}: {data['classification']}")
                lines.append(f"    Observed: {data['observed_combined']:.2f}")
                lines.append(f"    Predicted: {data['predicted_combined']:.2f}")
                lines.append(f"    Synergy: {data['synergy']:.2f} ({data['synergy_pct']:.1f}%)")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    elif abs_d < 1.2:
        return "large"
    else:
        return "very large"

def main():
    parser = argparse.ArgumentParser(
        description='Compare multiple experiments across key metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare C256 (baseline) vs C257-C260 (optimized) for Paper 8
  python compare_experiments.py \\
      --experiments \\
          C256=data/results/cycle256_results.json \\
          C257=data/results/cycle257_results.json \\
          C258=data/results/cycle258_results.json \\
          C259=data/results/cycle259_results.json \\
          C260=data/results/cycle260_results.json

  # Compare two factorial pairs for Paper 3
  python compare_experiments.py \\
      --experiments \\
          H1xH2=data/results/cycle255_results.json \\
          H1xH4=data/results/cycle256_results.json \\
      --synergy

  # Output as JSON
  python compare_experiments.py \\
      --experiments C256=results.json C257=results2.json \\
      --json
        """
    )

    parser.add_argument('--experiments', nargs='+', required=True,
                       help='Experiments to compare in format: ID=path (e.g., C256=results.json)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--synergy', action='store_true',
                       help='Include synergy analysis (for factorial experiments)')

    args = parser.parse_args()

    # Parse experiment paths
    experiment_paths = {}
    for exp_spec in args.experiments:
        if '=' not in exp_spec:
            print(f"Error: Invalid experiment spec '{exp_spec}'. Use format: ID=path", file=sys.stderr)
            sys.exit(1)

        exp_id, exp_path = exp_spec.split('=', 1)
        experiment_paths[exp_id] = Path(exp_path)

    # Create comparator
    comparator = ExperimentComparator(experiment_paths)

    if len(comparator.experiments) == 0:
        print("Error: No experiments loaded successfully", file=sys.stderr)
        sys.exit(1)

    # Generate report
    if args.json:
        # JSON output
        results = {
            'experiments': list(comparator.experiments.keys()),
            'runtimes': comparator.compare_runtimes(),
            'populations': comparator.compare_populations(),
            'variance': comparator.compare_variance(),
            'statistical_tests': comparator.statistical_tests()
        }

        if args.synergy:
            results['synergy'] = comparator.synergy_analysis()

        print(json.dumps(results, indent=2))
    else:
        # Human-readable report
        print(comparator.generate_summary_report())

if __name__ == '__main__':
    main()
