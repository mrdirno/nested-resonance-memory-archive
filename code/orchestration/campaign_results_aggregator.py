#!/usr/bin/env python3
"""
Campaign Results Aggregator - Cross-Experiment Analysis

Aggregates results across all campaign experiments (C186-C189) for comprehensive
analysis and Paper 4 manuscript generation. Provides statistical comparisons,
effect size calculations, and publication-ready data tables.

Part of DUALITY-ZERO nested-resonance-memory-archive infrastructure.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Date: 2025-11-05
Cycle: 1036+
License: GPL-3.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
import math

@dataclass
class ConditionSummary:
    """Statistical summary for a single condition"""
    condition_name: str
    experiment_id: str
    n_seeds: int

    # Composition metrics
    composition_time_mean: float
    composition_time_std: float
    composition_time_sem: float
    composition_time_ci95: Tuple[float, float]

    # Decomposition metrics
    decomposition_time_mean: float
    decomposition_time_std: float
    decomposition_time_sem: float
    decomposition_time_ci95: Tuple[float, float]

    # Population metrics
    final_population_mean: float
    final_population_std: float
    final_population_sem: float
    final_population_ci95: Tuple[float, float]

    # Clustering metrics
    cluster_size_mean: float
    cluster_size_std: float

    # Burst metrics
    burst_size_mean: float
    burst_size_std: float

    # Pattern metrics
    composition_count_mean: float
    decomposition_count_mean: float
    migration_count_mean: float

class CampaignResultsAggregator:
    """
    Aggregates and analyzes results across campaign experiments.

    Provides:
    - Cross-experiment statistical comparisons
    - Effect size calculations (Cohen's d)
    - Baseline comparisons for each experiment
    - Publication-ready data tables
    - CSV export for statistical software (R, SPSS, etc.)
    """

    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.summaries: List[ConditionSummary] = []
        self.raw_data: Dict[str, Dict[str, Any]] = {}

    def load_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Load experiment results from JSON file"""
        results_file = self.results_dir / f"{experiment_id}_results.json"

        if not results_file.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")

        with open(results_file, 'r') as f:
            data = json.load(f)

        self.raw_data[experiment_id] = data
        return data

    def compute_condition_summary(self, experiment_id: str,
                                  condition_name: str,
                                  seed_data: Dict[str, Dict[str, Any]]) -> ConditionSummary:
        """
        Compute statistical summary for a single condition.

        Args:
            experiment_id: Experiment identifier
            condition_name: Condition name
            seed_data: Dict mapping seed to metrics

        Returns:
            ConditionSummary with statistics
        """
        n_seeds = len(seed_data)

        # Extract metrics across seeds
        composition_times = []
        decomposition_times = []
        final_populations = []
        cluster_sizes = []
        burst_sizes = []
        composition_counts = []
        decomposition_counts = []
        migration_counts = []

        for seed, metrics in seed_data.items():
            if metrics.get('mean_composition_time') is not None:
                composition_times.append(metrics['mean_composition_time'])
            if metrics.get('mean_decomposition_time') is not None:
                decomposition_times.append(metrics['mean_decomposition_time'])
            if metrics.get('final_population') is not None:
                final_populations.append(metrics['final_population'])
            if metrics.get('mean_cluster_size') is not None and metrics['mean_cluster_size'] > 0:
                cluster_sizes.append(metrics['mean_cluster_size'])
            if metrics.get('mean_burst_size') is not None and metrics['mean_burst_size'] > 0:
                burst_sizes.append(metrics['mean_burst_size'])
            if metrics.get('total_compositions') is not None:
                composition_counts.append(metrics['total_compositions'])
            if metrics.get('total_decompositions') is not None:
                decomposition_counts.append(metrics['total_decompositions'])
            if metrics.get('total_migrations') is not None:
                migration_counts.append(metrics['total_migrations'])

        # Compute statistics
        def compute_stats(values: List[float]) -> Tuple[float, float, float, Tuple[float, float]]:
            """Compute mean, std, SEM, 95% CI"""
            if not values:
                return 0.0, 0.0, 0.0, (0.0, 0.0)

            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0.0
            sem = std / math.sqrt(len(values)) if len(values) > 0 else 0.0

            # 95% CI: mean ± 1.96 * SEM (approximation for large n)
            # For small n, should use t-distribution, but this is close enough
            ci_lower = mean - 1.96 * sem
            ci_upper = mean + 1.96 * sem

            return mean, std, sem, (ci_lower, ci_upper)

        comp_mean, comp_std, comp_sem, comp_ci = compute_stats(composition_times)
        decomp_mean, decomp_std, decomp_sem, decomp_ci = compute_stats(decomposition_times)
        pop_mean, pop_std, pop_sem, pop_ci = compute_stats(final_populations)
        cluster_mean, cluster_std, _, _ = compute_stats(cluster_sizes)
        burst_mean, burst_std, _, _ = compute_stats(burst_sizes)

        return ConditionSummary(
            condition_name=condition_name,
            experiment_id=experiment_id,
            n_seeds=n_seeds,
            composition_time_mean=comp_mean,
            composition_time_std=comp_std,
            composition_time_sem=comp_sem,
            composition_time_ci95=comp_ci,
            decomposition_time_mean=decomp_mean,
            decomposition_time_std=decomp_std,
            decomposition_time_sem=decomp_sem,
            decomposition_time_ci95=decomp_ci,
            final_population_mean=pop_mean,
            final_population_std=pop_std,
            final_population_sem=pop_sem,
            final_population_ci95=pop_ci,
            cluster_size_mean=cluster_mean,
            cluster_size_std=cluster_std,
            burst_size_mean=burst_mean,
            burst_size_std=burst_std,
            composition_count_mean=statistics.mean(composition_counts) if composition_counts else 0.0,
            decomposition_count_mean=statistics.mean(decomposition_counts) if decomposition_counts else 0.0,
            migration_count_mean=statistics.mean(migration_counts) if migration_counts else 0.0
        )

    def aggregate_campaign(self, experiment_ids: List[str]) -> List[ConditionSummary]:
        """
        Aggregate all experiments in campaign.

        Args:
            experiment_ids: List of experiment IDs to aggregate

        Returns:
            List of ConditionSummary objects
        """
        summaries = []

        for exp_id in experiment_ids:
            try:
                data = self.load_experiment(exp_id)
            except FileNotFoundError as e:
                print(f"Warning: {e}", file=sys.stderr)
                continue

            conditions = data.get('conditions', {})

            for cond_name, cond_data in conditions.items():
                seed_data = cond_data.get('seeds', {})
                if not seed_data:
                    continue

                summary = self.compute_condition_summary(exp_id, cond_name, seed_data)
                summaries.append(summary)

        self.summaries = summaries
        return summaries

    def compute_effect_size(self, baseline: ConditionSummary,
                           treatment: ConditionSummary,
                           metric: str = 'composition_time') -> float:
        """
        Compute Cohen's d effect size between baseline and treatment.

        Args:
            baseline: Baseline condition summary
            treatment: Treatment condition summary
            metric: Which metric to compare ('composition_time', 'decomposition_time', 'final_population')

        Returns:
            Cohen's d (standardized effect size)
        """
        metric_map = {
            'composition_time': ('composition_time_mean', 'composition_time_std'),
            'decomposition_time': ('decomposition_time_mean', 'decomposition_time_std'),
            'final_population': ('final_population_mean', 'final_population_std')
        }

        if metric not in metric_map:
            raise ValueError(f"Unknown metric: {metric}")

        mean_attr, std_attr = metric_map[metric]

        baseline_mean = getattr(baseline, mean_attr)
        baseline_std = getattr(baseline, std_attr)
        treatment_mean = getattr(treatment, mean_attr)
        treatment_std = getattr(treatment, std_attr)

        # Pooled standard deviation
        n1 = baseline.n_seeds
        n2 = treatment.n_seeds

        if n1 < 2 or n2 < 2:
            return 0.0

        pooled_std = math.sqrt(
            ((n1 - 1) * baseline_std**2 + (n2 - 1) * treatment_std**2) / (n1 + n2 - 2)
        )

        if pooled_std == 0:
            return 0.0

        # Cohen's d
        cohens_d = (treatment_mean - baseline_mean) / pooled_std

        return cohens_d

    def generate_comparison_table(self, experiment_id: str,
                                 metric: str = 'composition_time') -> str:
        """
        Generate comparison table for a single experiment.

        Compares all conditions to BASELINE for specified metric.

        Args:
            experiment_id: Experiment to generate table for
            metric: Metric to compare

        Returns:
            Formatted table string
        """
        # Filter summaries for this experiment
        exp_summaries = [s for s in self.summaries if s.experiment_id == experiment_id]

        if not exp_summaries:
            return f"No data for {experiment_id}"

        # Find baseline
        baseline = None
        for s in exp_summaries:
            if 'BASELINE' in s.condition_name.upper():
                baseline = s
                break

        if not baseline:
            return f"No BASELINE found for {experiment_id}"

        # Build table
        lines = []
        lines.append(f"Comparison Table: {experiment_id.upper()} - {metric.replace('_', ' ').title()}")
        lines.append("=" * 100)
        lines.append(f"{'Condition':<30} {'Mean':<12} {'±SEM':<12} {'95% CI':<25} {'vs BASELINE':<20}")
        lines.append("-" * 100)

        metric_map = {
            'composition_time': ('composition_time_mean', 'composition_time_sem', 'composition_time_ci95'),
            'decomposition_time': ('decomposition_time_mean', 'decomposition_time_sem', 'decomposition_time_ci95'),
            'final_population': ('final_population_mean', 'final_population_sem', 'final_population_ci95')
        }

        mean_attr, sem_attr, ci_attr = metric_map[metric]

        # Baseline row
        baseline_mean = getattr(baseline, mean_attr)
        baseline_sem = getattr(baseline, sem_attr)
        baseline_ci = getattr(baseline, ci_attr)

        lines.append(
            f"{baseline.condition_name:<30} "
            f"{baseline_mean:<12.3f} "
            f"±{baseline_sem:<11.3f} "
            f"[{baseline_ci[0]:.3f}, {baseline_ci[1]:.3f}]    "
            f"{'(baseline)':<20}"
        )

        # Treatment rows
        for summary in exp_summaries:
            if summary.condition_name == baseline.condition_name:
                continue

            mean = getattr(summary, mean_attr)
            sem = getattr(summary, sem_attr)
            ci = getattr(summary, ci_attr)

            # Compute effect size
            effect_size = self.compute_effect_size(baseline, summary, metric)

            # Percent change
            if baseline_mean != 0:
                pct_change = ((mean - baseline_mean) / baseline_mean) * 100
                comparison = f"d={effect_size:+.3f} ({pct_change:+.1f}%)"
            else:
                comparison = f"d={effect_size:+.3f}"

            lines.append(
                f"{summary.condition_name:<30} "
                f"{mean:<12.3f} "
                f"±{sem:<11.3f} "
                f"[{ci[0]:.3f}, {ci[1]:.3f}]    "
                f"{comparison:<20}"
            )

        lines.append("=" * 100)
        return "\n".join(lines)

    def generate_full_report(self, output_file: Optional[Path] = None) -> str:
        """
        Generate comprehensive campaign results report.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report string
        """
        lines = []
        lines.append("=" * 100)
        lines.append("CAMPAIGN RESULTS AGGREGATION REPORT")
        lines.append("=" * 100)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Results Directory: {self.results_dir}")
        lines.append("")

        # Summary statistics
        experiments = list(set(s.experiment_id for s in self.summaries))
        lines.append("CAMPAIGN SUMMARY")
        lines.append("-" * 100)
        lines.append(f"Total Experiments: {len(experiments)}")
        lines.append(f"Total Conditions: {len(self.summaries)}")
        lines.append(f"Total Seeds: {sum(s.n_seeds for s in self.summaries)}")
        lines.append("")

        # Per-experiment tables
        for exp_id in sorted(experiments):
            lines.append("")
            lines.append(self.generate_comparison_table(exp_id, 'composition_time'))
            lines.append("")
            lines.append(self.generate_comparison_table(exp_id, 'decomposition_time'))
            lines.append("")
            lines.append(self.generate_comparison_table(exp_id, 'final_population'))
            lines.append("")

        lines.append("=" * 100)

        report = "\n".join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)

        return report

    def export_csv(self, output_file: Path):
        """
        Export aggregated results to CSV for statistical analysis.

        Args:
            output_file: Path to CSV file
        """
        import csv

        with open(output_file, 'w', newline='') as f:
            if not self.summaries:
                return

            # Get field names from dataclass
            fieldnames = list(asdict(self.summaries[0]).keys())

            # Handle tuple CI fields specially
            fieldnames_flat = []
            for field in fieldnames:
                if 'ci95' in field:
                    fieldnames_flat.append(f"{field}_lower")
                    fieldnames_flat.append(f"{field}_upper")
                else:
                    fieldnames_flat.append(field)

            writer = csv.DictWriter(f, fieldnames=fieldnames_flat)
            writer.writeheader()

            for summary in self.summaries:
                row = asdict(summary)

                # Flatten CI tuples
                row_flat = {}
                for key, value in row.items():
                    if 'ci95' in key and isinstance(value, tuple):
                        row_flat[f"{key}_lower"] = value[0]
                        row_flat[f"{key}_upper"] = value[1]
                    else:
                        row_flat[key] = value

                writer.writerow(row_flat)

    def export_json(self, output_file: Path):
        """
        Export aggregated results to JSON.

        Args:
            output_file: Path to JSON file
        """
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'results_dir': str(self.results_dir),
                'num_experiments': len(set(s.experiment_id for s in self.summaries)),
                'num_conditions': len(self.summaries),
                'total_seeds': sum(s.n_seeds for s in self.summaries)
            },
            'summaries': [asdict(s) for s in self.summaries]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Command-line interface for campaign results aggregation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate campaign experiment results for comprehensive analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report for campaign
  python campaign_results_aggregator.py --campaign --output campaign_report.txt

  # Export to CSV for R/SPSS analysis
  python campaign_results_aggregator.py --campaign --csv campaign_results.csv

  # Export to JSON
  python campaign_results_aggregator.py --campaign --json campaign_results.json

  # Specific experiments only
  python campaign_results_aggregator.py cycle186 cycle187 --output report.txt
        """
    )

    parser.add_argument('experiments', nargs='*', help='Experiment IDs to aggregate')
    parser.add_argument('--campaign', action='store_true',
                       help='Aggregate full campaign (C186-C189)')
    parser.add_argument('--results-dir', type=Path,
                       default=Path(__file__).parent.parent.parent / 'experiments' / 'results',
                       help='Results directory path')
    parser.add_argument('--output', type=Path, help='Output report file (text)')
    parser.add_argument('--csv', type=Path, help='Export to CSV file')
    parser.add_argument('--json', type=Path, help='Export to JSON file')

    args = parser.parse_args()

    aggregator = CampaignResultsAggregator(args.results_dir)

    # Determine which experiments to aggregate
    if args.campaign:
        experiment_ids = ['cycle186', 'cycle187', 'cycle188', 'cycle189']
    elif args.experiments:
        experiment_ids = args.experiments
    else:
        parser.print_help()
        sys.exit(1)

    # Aggregate
    summaries = aggregator.aggregate_campaign(experiment_ids)

    if not summaries:
        print("Error: No data found for specified experiments", file=sys.stderr)
        sys.exit(1)

    print(f"Aggregated {len(summaries)} conditions across {len(experiment_ids)} experiments")

    # Generate outputs
    if args.output or not (args.csv or args.json):
        report = aggregator.generate_full_report(output_file=args.output)
        if not args.output:
            print(report)

    if args.csv:
        aggregator.export_csv(args.csv)
        print(f"Exported CSV to {args.csv}")

    if args.json:
        aggregator.export_json(args.json)
        print(f"Exported JSON to {args.json}")


if __name__ == '__main__':
    main()
