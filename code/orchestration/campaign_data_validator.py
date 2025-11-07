#!/usr/bin/env python3
"""
Campaign Data Validator - Post-Experiment Quality Control

Validates experimental data integrity, completeness, and quality for campaign
experiments (C186-C189). Provides early warning of issues before Paper 4 analysis.

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
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class ValidationResult:
    """Results of data validation check"""
    experiment_id: str
    status: str  # 'pass', 'fail', 'warning'
    issues: List[str]
    metrics: Dict[str, Any]

class CampaignDataValidator:
    """
    Validates experimental data integrity and quality for campaign experiments.

    Checks:
    - File existence and readability
    - Schema compliance
    - Data completeness (all seeds present)
    - Statistical sanity (outliers, NaNs, invalid values)
    - Metadata consistency
    - Temporal coverage
    """

    def __init__(self, results_dir: Path):
        """
        Initialize validator with results directory path.

        Args:
            results_dir: Path to directory containing experiment results
        """
        self.results_dir = Path(results_dir)
        self.validation_results: List[ValidationResult] = []

    def validate_experiment(self, experiment_id: str,
                          expected_seeds: int,
                          expected_conditions: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate a single experiment's data.

        Args:
            experiment_id: Experiment identifier (e.g., 'cycle186')
            expected_seeds: Number of seeds expected
            expected_conditions: Optional list of expected condition names

        Returns:
            ValidationResult with status and issues
        """
        issues = []
        metrics = {}

        # Find results file
        results_file = self.results_dir / f"{experiment_id}_results.json"

        if not results_file.exists():
            return ValidationResult(
                experiment_id=experiment_id,
                status='fail',
                issues=[f"Results file not found: {results_file}"],
                metrics={}
            )

        # Load data
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult(
                experiment_id=experiment_id,
                status='fail',
                issues=[f"JSON decode error: {e}"],
                metrics={}
            )
        except Exception as e:
            return ValidationResult(
                experiment_id=experiment_id,
                status='fail',
                issues=[f"File read error: {e}"],
                metrics={}
            )

        # Validate schema
        schema_issues = self._validate_schema(data)
        issues.extend(schema_issues)

        # Validate completeness
        completeness_issues, completeness_metrics = self._validate_completeness(
            data, expected_seeds, expected_conditions
        )
        issues.extend(completeness_issues)
        metrics.update(completeness_metrics)

        # Validate data quality
        quality_issues, quality_metrics = self._validate_data_quality(data)
        issues.extend(quality_issues)
        metrics.update(quality_metrics)

        # Validate metadata
        metadata_issues, metadata_metrics = self._validate_metadata(data)
        issues.extend(metadata_issues)
        metrics.update(metadata_metrics)

        # Determine status
        if any('CRITICAL' in issue for issue in issues):
            status = 'fail'
        elif issues:
            status = 'warning'
        else:
            status = 'pass'

        return ValidationResult(
            experiment_id=experiment_id,
            status=status,
            issues=issues,
            metrics=metrics
        )

    def _validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """Validate JSON schema compliance"""
        issues = []

        # Required top-level keys
        required_keys = ['experiment_id', 'conditions', 'metadata']
        for key in required_keys:
            if key not in data:
                issues.append(f"CRITICAL: Missing required key '{key}'")

        # Validate conditions structure
        if 'conditions' in data:
            if not isinstance(data['conditions'], dict):
                issues.append("CRITICAL: 'conditions' must be a dictionary")
            else:
                for cond_name, cond_data in data['conditions'].items():
                    if 'seeds' not in cond_data:
                        issues.append(f"CRITICAL: Condition '{cond_name}' missing 'seeds' key")
                    elif not isinstance(cond_data['seeds'], dict):
                        issues.append(f"CRITICAL: Condition '{cond_name}' seeds must be dictionary")

        return issues

    def _validate_completeness(self, data: Dict[str, Any],
                               expected_seeds: int,
                               expected_conditions: Optional[List[str]]) -> Tuple[List[str], Dict[str, Any]]:
        """Validate data completeness"""
        issues = []
        metrics = {}

        if 'conditions' not in data:
            return issues, metrics

        conditions = data['conditions']
        metrics['num_conditions'] = len(conditions)

        # Check expected conditions
        if expected_conditions:
            missing_conditions = set(expected_conditions) - set(conditions.keys())
            if missing_conditions:
                issues.append(f"WARNING: Missing conditions: {missing_conditions}")
            extra_conditions = set(conditions.keys()) - set(expected_conditions)
            if extra_conditions:
                issues.append(f"INFO: Extra conditions found: {extra_conditions}")

        # Check seed completeness for each condition
        seed_stats = {}
        for cond_name, cond_data in conditions.items():
            seeds = cond_data.get('seeds', {})
            num_seeds = len(seeds)
            seed_stats[cond_name] = num_seeds

            if num_seeds < expected_seeds:
                issues.append(
                    f"CRITICAL: Condition '{cond_name}' has {num_seeds}/{expected_seeds} seeds"
                )
            elif num_seeds > expected_seeds:
                issues.append(
                    f"WARNING: Condition '{cond_name}' has {num_seeds}/{expected_seeds} seeds (extra)"
                )

        metrics['seed_counts'] = seed_stats
        metrics['total_seeds'] = sum(seed_stats.values())
        metrics['expected_total'] = expected_seeds * len(conditions)

        return issues, metrics

    def _validate_data_quality(self, data: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """Validate statistical data quality"""
        issues = []
        metrics = {}

        if 'conditions' not in data:
            return issues, metrics

        # Collect all metric values for sanity checks
        composition_times = []
        decomposition_times = []
        cluster_sizes = []
        burst_sizes = []
        final_populations = []

        for cond_name, cond_data in data['conditions'].items():
            for seed, seed_data in cond_data.get('seeds', {}).items():
                # Check for required metrics
                required_metrics = [
                    'mean_composition_time',
                    'mean_decomposition_time',
                    'mean_cluster_size',
                    'mean_burst_size',
                    'final_population'
                ]

                for metric in required_metrics:
                    if metric not in seed_data:
                        issues.append(
                            f"WARNING: Condition '{cond_name}' seed {seed} missing '{metric}'"
                        )
                    else:
                        value = seed_data[metric]

                        # Check for invalid values
                        if value is None:
                            issues.append(
                                f"WARNING: Condition '{cond_name}' seed {seed} has None for '{metric}'"
                            )
                        elif isinstance(value, (int, float)):
                            if value < 0 and metric != 'mean_cluster_size':  # cluster_size can be NaN → -1
                                issues.append(
                                    f"WARNING: Condition '{cond_name}' seed {seed} has negative '{metric}': {value}"
                                )

                            # Collect valid values
                            if metric == 'mean_composition_time' and value > 0:
                                composition_times.append(value)
                            elif metric == 'mean_decomposition_time' and value > 0:
                                decomposition_times.append(value)
                            elif metric == 'mean_cluster_size' and value > 0:
                                cluster_sizes.append(value)
                            elif metric == 'mean_burst_size' and value > 0:
                                burst_sizes.append(value)
                            elif metric == 'final_population' and value >= 0:
                                final_populations.append(value)

        # Statistical summary
        def safe_stats(values: List[float], name: str) -> Dict[str, float]:
            """Calculate statistical summary metrics safely handling empty lists."""
            if not values:
                return {}
            return {
                f'{name}_mean': statistics.mean(values),
                f'{name}_median': statistics.median(values),
                f'{name}_stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
                f'{name}_min': min(values),
                f'{name}_max': max(values),
                f'{name}_n': len(values)
            }

        metrics.update(safe_stats(composition_times, 'composition_time'))
        metrics.update(safe_stats(decomposition_times, 'decomposition_time'))
        metrics.update(safe_stats(cluster_sizes, 'cluster_size'))
        metrics.update(safe_stats(burst_sizes, 'burst_size'))
        metrics.update(safe_stats(final_populations, 'final_population'))

        # Outlier detection (simple z-score based)
        def detect_outliers(values: List[float], name: str, threshold: float = 3.0):
            """Detect statistical outliers using z-score threshold method."""
            if len(values) < 3:
                return
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            if stdev == 0:
                return
            outliers = [v for v in values if abs((v - mean) / stdev) > threshold]
            if outliers:
                issues.append(
                    f"INFO: {len(outliers)} outliers detected in {name} (>{threshold}σ)"
                )

        detect_outliers(composition_times, 'composition_time')
        detect_outliers(decomposition_times, 'decomposition_time')
        detect_outliers(final_populations, 'final_population')

        return issues, metrics

    def _validate_metadata(self, data: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """Validate metadata consistency"""
        issues = []
        metrics = {}

        if 'metadata' not in data:
            issues.append("WARNING: No metadata found")
            return issues, metrics

        metadata = data['metadata']

        # Check required metadata fields
        required_fields = ['experiment_id', 'parameters']
        for field in required_fields:
            if field not in metadata:
                issues.append(f"WARNING: Missing metadata field '{field}'")

        # Check timestamp if present
        if 'timestamp' in metadata:
            try:
                datetime.fromisoformat(metadata['timestamp'])
                metrics['timestamp'] = metadata['timestamp']
            except (ValueError, TypeError):
                issues.append(f"WARNING: Invalid timestamp format: {metadata['timestamp']}")

        # Extract key parameters
        if 'parameters' in metadata:
            params = metadata['parameters']
            for key in ['frequency_range', 'max_time', 'num_agents', 'seeds']:
                if key in params:
                    metrics[f'param_{key}'] = params[key]

        return issues, metrics

    def validate_campaign(self, campaign_config: Dict[str, Dict[str, Any]]) -> Dict[str, ValidationResult]:
        """
        Validate all experiments in a campaign.

        Args:
            campaign_config: Dict mapping experiment_id to config:
                {
                    'cycle186': {'seeds': 10, 'conditions': ['BASELINE', ...]},
                    'cycle187': {'seeds': 10, 'conditions': [...]},
                    ...
                }

        Returns:
            Dict mapping experiment_id to ValidationResult
        """
        results = {}

        for exp_id, config in campaign_config.items():
            result = self.validate_experiment(
                experiment_id=exp_id,
                expected_seeds=config['seeds'],
                expected_conditions=config.get('conditions')
            )
            results[exp_id] = result
            self.validation_results.append(result)

        return results

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """
        Generate human-readable validation report.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CAMPAIGN DATA VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Results Directory: {self.results_dir}")
        lines.append("")

        # Summary statistics
        total = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r.status == 'pass')
        warnings = sum(1 for r in self.validation_results if r.status == 'warning')
        failed = sum(1 for r in self.validation_results if r.status == 'fail')

        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Experiments: {total}")
        lines.append(f"  ✓ Passed:        {passed} ({100*passed/total:.1f}%)" if total > 0 else "  ✓ Passed:        0")
        lines.append(f"  ⚠ Warnings:      {warnings} ({100*warnings/total:.1f}%)" if total > 0 else "  ⚠ Warnings:      0")
        lines.append(f"  ✗ Failed:        {failed} ({100*failed/total:.1f}%)" if total > 0 else "  ✗ Failed:        0")
        lines.append("")

        # Detailed results
        lines.append("DETAILED RESULTS")
        lines.append("-" * 80)

        for result in self.validation_results:
            status_symbol = {'pass': '✓', 'warning': '⚠', 'fail': '✗'}[result.status]
            lines.append(f"\n{status_symbol} {result.experiment_id.upper()} - {result.status.upper()}")
            lines.append("-" * 40)

            # Issues
            if result.issues:
                lines.append("  Issues:")
                for issue in result.issues:
                    lines.append(f"    • {issue}")
            else:
                lines.append("  No issues detected")

            # Key metrics
            if result.metrics:
                lines.append("  Key Metrics:")

                # Completeness metrics
                if 'num_conditions' in result.metrics:
                    lines.append(f"    Conditions: {result.metrics['num_conditions']}")
                if 'total_seeds' in result.metrics and 'expected_total' in result.metrics:
                    lines.append(
                        f"    Seeds: {result.metrics['total_seeds']}/{result.metrics['expected_total']}"
                    )

                # Quality metrics
                if 'composition_time_mean' in result.metrics:
                    lines.append(
                        f"    Composition Time: {result.metrics['composition_time_mean']:.2f} ± "
                        f"{result.metrics.get('composition_time_stdev', 0):.2f} cycles "
                        f"(n={result.metrics.get('composition_time_n', 0)})"
                    )
                if 'decomposition_time_mean' in result.metrics:
                    lines.append(
                        f"    Decomposition Time: {result.metrics['decomposition_time_mean']:.2f} ± "
                        f"{result.metrics.get('decomposition_time_stdev', 0):.2f} cycles "
                        f"(n={result.metrics.get('decomposition_time_n', 0)})"
                    )
                if 'final_population_mean' in result.metrics:
                    lines.append(
                        f"    Final Population: {result.metrics['final_population_mean']:.1f} ± "
                        f"{result.metrics.get('final_population_stdev', 0):.1f} agents "
                        f"(n={result.metrics.get('final_population_n', 0)})"
                    )

        lines.append("")
        lines.append("=" * 80)

        report = "\n".join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)

        return report


def main():
    """Command-line interface for campaign data validation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate experimental data integrity and quality for campaign experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single experiment
  python campaign_data_validator.py cycle186 --seeds 10

  # Validate full campaign
  python campaign_data_validator.py --campaign

  # Generate report to file
  python campaign_data_validator.py --campaign --output validation_report.txt
        """
    )

    parser.add_argument('experiment_id', nargs='?', help='Experiment ID to validate (e.g., cycle186)')
    parser.add_argument('--seeds', type=int, help='Expected number of seeds')
    parser.add_argument('--conditions', nargs='+', help='Expected condition names')
    parser.add_argument('--campaign', action='store_true', help='Validate full campaign (C186-C189)')
    parser.add_argument('--results-dir', type=Path,
                       default=Path(__file__).parent.parent.parent / 'experiments' / 'results',
                       help='Results directory path')
    parser.add_argument('--output', type=Path, help='Output report file')

    args = parser.parse_args()

    validator = CampaignDataValidator(args.results_dir)

    if args.campaign:
        # Validate full campaign
        campaign_config = {
            'cycle186': {
                'seeds': 10,
                'conditions': [
                    'BASELINE',
                    'DEPTH_05', 'DEPTH_10', 'DEPTH_15',
                    'RESONANCE_05', 'RESONANCE_10', 'RESONANCE_15',
                    'MEMORY_05', 'MEMORY_10', 'MEMORY_15'
                ]
            },
            'cycle187': {
                'seeds': 10,
                'conditions': [
                    'BASELINE',
                    'NETWORK_SPARSE', 'NETWORK_DENSE', 'NETWORK_SCALE_FREE'
                ]
            },
            'cycle188': {
                'seeds': 10,
                'conditions': [
                    'BASELINE',
                    'MEMORY_SHORT', 'MEMORY_LONG', 'MEMORY_HIERARCHICAL'
                ]
            },
            'cycle189': {
                'seeds': 10,
                'conditions': [
                    'BASELINE',
                    'BURST_SMALL', 'BURST_MEDIUM', 'BURST_LARGE',
                    'BURST_MIXED'
                ]
            }
        }

        results = validator.validate_campaign(campaign_config)

    elif args.experiment_id:
        # Validate single experiment
        if not args.seeds:
            print("Error: --seeds required for single experiment validation", file=sys.stderr)
            sys.exit(1)

        result = validator.validate_experiment(
            experiment_id=args.experiment_id,
            expected_seeds=args.seeds,
            expected_conditions=args.conditions
        )
        validator.validation_results.append(result)

    else:
        parser.print_help()
        sys.exit(1)

    # Generate and print report
    report = validator.generate_report(output_file=args.output)
    print(report)

    # Exit code based on validation status
    if any(r.status == 'fail' for r in validator.validation_results):
        sys.exit(1)
    elif any(r.status == 'warning' for r in validator.validation_results):
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
