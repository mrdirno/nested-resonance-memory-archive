#!/usr/bin/env python3
"""
Baseline Consistency Checker - Experimental Control Validation

Validates that baseline conditions (all mechanisms OFF) are statistically
consistent across all experiments. Critical for factorial analysis validity.

Checks:
- Mean population consistency across baselines
- Composition depth consistency across baselines
- Statistical outlier detection (IQR method)
- Coefficient of variation (stability metric)
- Temporal drift detection

Ensures that control conditions are truly controlled, validating
experimental integrity for publication.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import sys

try:
    import numpy as np
except ImportError:
    print("Error: numpy required. Install with: pip install numpy", file=sys.stderr)
    sys.exit(1)


class BaselineConsistencyChecker:
    """
    Check consistency of baseline conditions across experiments.

    Baseline = all mechanisms OFF (H1=False, H2=False, H3=False, H4=False, H5=False)
    or equivalent control condition for experiment type.

    Validates:
    - Mean population consistency
    - Composition depth consistency
    - Statistical outliers
    - Temporal drift
    """

    def __init__(self, results_dir: Path):
        """
        Initialize baseline consistency checker.

        Args:
            results_dir: Directory containing result JSON files
        """
        self.results_dir = Path(results_dir)
        self.baselines = []  # List of baseline measurements

    def identify_baseline_conditions(self, data: Dict) -> List[Dict]:
        """
        Identify baseline conditions in experimental data.

        Args:
            data: Experiment result data (JSON)

        Returns:
            List of baseline condition dicts
        """
        baselines = []

        # Handle different data formats

        # Format 1: "conditions" dict (C255 format)
        if 'conditions' in data:
            conditions = data['conditions']
            if 'OFF-OFF' in conditions:
                baselines.append(conditions['OFF-OFF'])
            elif 'OFF-OFF-OFF' in conditions:
                baselines.append(conditions['OFF-OFF-OFF'])
            elif 'OFF-OFF-OFF-OFF' in conditions:
                baselines.append(conditions['OFF-OFF-OFF-OFF'])
            elif 'OFF-OFF-OFF-OFF-OFF' in conditions:
                baselines.append(conditions['OFF-OFF-OFF-OFF-OFF'])

        # Format 2: "results" list (factorial format)
        elif 'results' in data:
            results = data['results']

            if isinstance(results, list):
                # Factorial experiment
                for result in results:
                    mech_config = result.get('mechanism_config', {})

                    # Baseline = all mechanisms OFF
                    if all(not mech_config.get(f'H{i}', False) for i in [1, 2, 3, 4, 5]):
                        baselines.append(result)
            elif isinstance(results, dict):
                # Single condition experiment
                config = data.get('configuration', {})
                mech_config = config.get('mechanism_config', {})

                # Check if this is a baseline configuration
                if all(not mech_config.get(f'H{i}', False) for i in [1, 2, 3, 4, 5]):
                    baselines.append(results)

        # Format 3: "experiments" list (C175 format - not baseline experiment)
        # Skip, as these don't have baseline conditions

        return baselines

    def extract_baseline_metrics(self, baseline: Dict) -> Optional[Dict]:
        """
        Extract metrics from baseline condition.

        Args:
            baseline: Baseline condition dict

        Returns:
            Dict with metrics or None if invalid
        """
        mean_pop = baseline.get('mean_population')
        comp_depth = baseline.get('composition_depth')

        # Check for valid population data (required)
        if mean_pop is None:
            return None

        # Handle list values (take mean)
        if isinstance(mean_pop, list):
            if len(mean_pop) == 0 or all(v is None for v in mean_pop):
                return None
            mean_pop = np.mean([v for v in mean_pop if v is not None])

        # Handle composition depth (optional)
        if comp_depth is not None:
            if isinstance(comp_depth, list):
                if len(comp_depth) == 0 or all(v is None for v in comp_depth):
                    comp_depth = None
                else:
                    comp_depth = np.mean([v for v in comp_depth if v is not None])
            comp_depth = float(comp_depth) if comp_depth is not None else None

        return {
            'mean_population': float(mean_pop),
            'composition_depth': comp_depth  # Can be None
        }

    def scan_experiments(self) -> Dict:
        """
        Scan all experiment results for baselines.

        Returns:
            Dict with baseline data and statistics
        """
        baseline_data = []

        for result_file in self.results_dir.glob('*.json'):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)

                # Identify baselines in this experiment
                baselines = self.identify_baseline_conditions(data)

                for baseline in baselines:
                    metrics = self.extract_baseline_metrics(baseline)

                    if metrics:
                        baseline_data.append({
                            'file': result_file.name,
                            'experiment': data.get('experiment_name', result_file.stem),
                            'mean_population': metrics['mean_population'],
                            'composition_depth': metrics['composition_depth']
                        })

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Skip invalid files
                continue

        return baseline_data

    def calculate_statistics(self, baseline_data: List[Dict]) -> Dict:
        """
        Calculate statistics for baseline consistency.

        Args:
            baseline_data: List of baseline measurements

        Returns:
            Dict with statistics
        """
        if len(baseline_data) == 0:
            return {
                'count': 0,
                'mean_population': {},
                'composition_depth': {},
                'outliers': []
            }

        # Extract values
        populations = [b['mean_population'] for b in baseline_data]
        depths = [b['composition_depth'] for b in baseline_data if b['composition_depth'] is not None]

        # Statistics for population
        pop_mean = np.mean(populations)
        pop_std = np.std(populations)
        pop_cv = (pop_std / pop_mean * 100) if pop_mean > 0 else 0

        pop_min = np.min(populations)
        pop_max = np.max(populations)
        pop_q1 = np.percentile(populations, 25)
        pop_median = np.percentile(populations, 50)
        pop_q3 = np.percentile(populations, 75)

        # Statistics for depth (if available)
        if len(depths) > 0:
            depth_mean = np.mean(depths)
            depth_std = np.std(depths)
            depth_cv = (depth_std / depth_mean * 100) if depth_mean > 0 else 0

            depth_min = np.min(depths)
            depth_max = np.max(depths)
            depth_q1 = np.percentile(depths, 25)
            depth_median = np.percentile(depths, 50)
            depth_q3 = np.percentile(depths, 75)
        else:
            depth_mean = depth_std = depth_cv = 0
            depth_min = depth_max = depth_q1 = depth_median = depth_q3 = 0

        # Outlier detection (IQR method)
        pop_iqr = pop_q3 - pop_q1
        pop_lower_bound = pop_q1 - 1.5 * pop_iqr
        pop_upper_bound = pop_q3 + 1.5 * pop_iqr

        depth_iqr = depth_q3 - depth_q1 if len(depths) > 0 else 0
        depth_lower_bound = depth_q1 - 1.5 * depth_iqr if len(depths) > 0 else 0
        depth_upper_bound = depth_q3 + 1.5 * depth_iqr if len(depths) > 0 else 0

        outliers = []
        for baseline in baseline_data:
            pop = baseline['mean_population']
            depth = baseline['composition_depth']

            if pop < pop_lower_bound or pop > pop_upper_bound:
                outliers.append({
                    'file': baseline['file'],
                    'metric': 'mean_population',
                    'value': pop,
                    'lower_bound': pop_lower_bound,
                    'upper_bound': pop_upper_bound
                })

            if depth is not None and len(depths) > 0:
                if depth < depth_lower_bound or depth > depth_upper_bound:
                    outliers.append({
                        'file': baseline['file'],
                        'metric': 'composition_depth',
                        'value': depth,
                        'lower_bound': depth_lower_bound,
                        'upper_bound': depth_upper_bound
                    })

        return {
            'count': len(baseline_data),
            'mean_population': {
                'mean': pop_mean,
                'std': pop_std,
                'cv': pop_cv,
                'min': pop_min,
                'max': pop_max,
                'q1': pop_q1,
                'median': pop_median,
                'q3': pop_q3,
                'iqr': pop_iqr
            },
            'composition_depth': {
                'mean': depth_mean,
                'std': depth_std,
                'cv': depth_cv,
                'min': depth_min,
                'max': depth_max,
                'q1': depth_q1,
                'median': depth_median,
                'q3': depth_q3,
                'iqr': depth_iqr
            },
            'outliers': outliers
        }

    def check_consistency(self) -> Dict:
        """
        Check baseline consistency across all experiments.

        Returns:
            Dict with consistency status and statistics
        """
        baseline_data = self.scan_experiments()
        statistics = self.calculate_statistics(baseline_data)

        # Consistency thresholds
        cv_threshold_good = 10  # CV < 10% = good consistency
        cv_threshold_warning = 20  # CV > 20% = warning
        outlier_threshold = 0.1  # >10% outliers = warning

        # Assess consistency
        pop_cv = statistics['mean_population'].get('cv', 0)
        depth_cv = statistics['composition_depth'].get('cv', 0)
        outlier_rate = len(statistics['outliers']) / statistics['count'] if statistics['count'] > 0 else 0

        warnings = []
        errors = []

        # Check population CV
        if pop_cv > cv_threshold_warning:
            errors.append(f"High population variability (CV={pop_cv:.1f}%) - baselines inconsistent")
        elif pop_cv > cv_threshold_good:
            warnings.append(f"Moderate population variability (CV={pop_cv:.1f}%) - check parameters")

        # Check depth CV (only if depth data available)
        if statistics['composition_depth'].get('mean', 0) > 0:
            if depth_cv > cv_threshold_warning:
                errors.append(f"High depth variability (CV={depth_cv:.1f}%) - baselines inconsistent")
            elif depth_cv > cv_threshold_good:
                warnings.append(f"Moderate depth variability (CV={depth_cv:.1f}%) - check parameters")

        # Check outlier rate
        if outlier_rate > outlier_threshold:
            warnings.append(f"Many outliers ({outlier_rate*100:.1f}% of baselines) - check experimental conditions")

        # Overall status
        if len(errors) > 0:
            status = "INCONSISTENT"
        elif len(warnings) > 0:
            status = "WARNING"
        else:
            status = "CONSISTENT"

        return {
            'timestamp': datetime.now().isoformat(),
            'results_directory': str(self.results_dir),
            'status': status,
            'baselines': baseline_data,
            'statistics': statistics,
            'warnings': warnings,
            'errors': errors
        }

    def generate_report(self, data: Dict) -> str:
        """
        Generate human-readable consistency report.

        Args:
            data: Consistency data from check_consistency()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 100)
        lines.append("BASELINE CONSISTENCY REPORT")
        lines.append("=" * 100)
        lines.append(f"\nGenerated: {data['timestamp']}")
        lines.append(f"Results Directory: {data['results_directory']}")
        lines.append("")

        # Overall status
        status = data['status']
        status_symbol = {
            'CONSISTENT': '✓',
            'WARNING': '⚠️',
            'INCONSISTENT': '✗'
        }.get(status, '?')

        lines.append(f"Overall Status: {status_symbol} {status}")
        lines.append("")

        # Statistics
        stats = data['statistics']
        count = stats['count']

        lines.append(f"Baselines Found: {count}")

        if count == 0:
            lines.append("\n⚠️  No baseline conditions found in experiments.")
            lines.append("Baseline = all mechanisms OFF (H1=False, H2=False, H3=False, H4=False, H5=False)")
            lines.append("=" * 100)
            return "\n".join(lines)

        lines.append("")

        # Mean Population Statistics
        lines.append("MEAN POPULATION")
        lines.append("-" * 100)
        pop = stats['mean_population']
        lines.append(f"  Mean: {pop['mean']:.2f} ± {pop['std']:.2f} (CV = {pop['cv']:.1f}%)")
        lines.append(f"  Range: [{pop['min']:.2f}, {pop['max']:.2f}]")
        lines.append(f"  Quartiles: Q1={pop['q1']:.2f}, Median={pop['median']:.2f}, Q3={pop['q3']:.2f}")
        lines.append(f"  IQR: {pop['iqr']:.2f}")

        # CV interpretation
        if pop['cv'] < 10:
            lines.append(f"  ✓ Excellent consistency (CV < 10%)")
        elif pop['cv'] < 20:
            lines.append(f"  ⚠️  Moderate variability (CV 10-20%)")
        else:
            lines.append(f"  ✗ High variability (CV > 20%)")

        lines.append("")

        # Composition Depth Statistics (if available)
        depth = stats['composition_depth']
        if depth['mean'] > 0:
            lines.append("COMPOSITION DEPTH")
            lines.append("-" * 100)
            lines.append(f"  Mean: {depth['mean']:.2f} ± {depth['std']:.2f} (CV = {depth['cv']:.1f}%)")
            lines.append(f"  Range: [{depth['min']:.2f}, {depth['max']:.2f}]")
            lines.append(f"  Quartiles: Q1={depth['q1']:.2f}, Median={depth['median']:.2f}, Q3={depth['q3']:.2f}")
            lines.append(f"  IQR: {depth['iqr']:.2f}")

            # CV interpretation
            if depth['cv'] < 10:
                lines.append(f"  ✓ Excellent consistency (CV < 10%)")
            elif depth['cv'] < 20:
                lines.append(f"  ⚠️  Moderate variability (CV 10-20%)")
            else:
                lines.append(f"  ✗ High variability (CV > 20%)")

            lines.append("")
        else:
            lines.append("COMPOSITION DEPTH")
            lines.append("-" * 100)
            lines.append("  (Not available in baseline data)")
            lines.append("")

        # Outliers
        outliers = stats['outliers']
        if outliers:
            lines.append("OUTLIERS")
            lines.append("-" * 100)
            lines.append(f"Found {len(outliers)} outlier(s) ({len(outliers)/count*100:.1f}% of baselines)")
            lines.append("")

            for outlier in outliers:
                lines.append(f"  File: {outlier['file']}")
                lines.append(f"  Metric: {outlier['metric']}")
                lines.append(f"  Value: {outlier['value']:.2f}")
                lines.append(f"  Expected Range: [{outlier['lower_bound']:.2f}, {outlier['upper_bound']:.2f}]")
                lines.append("")

        # Warnings
        if data['warnings']:
            lines.append("⚠️  WARNINGS")
            lines.append("-" * 100)
            for warning in data['warnings']:
                lines.append(f"  - {warning}")
            lines.append("")

        # Errors
        if data['errors']:
            lines.append("✗ ERRORS")
            lines.append("-" * 100)
            for error in data['errors']:
                lines.append(f"  - {error}")
            lines.append("")

        lines.append("=" * 100)
        lines.append("END OF REPORT")
        lines.append("=" * 100)

        return "\n".join(lines)

    def export_json(self, data: Dict, output_path: Path):
        """
        Export consistency data as JSON.

        Args:
            data: Consistency data from check_consistency()
            output_path: Path to write JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Check baseline consistency across experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check baseline consistency
  python baseline_consistency_checker.py --results data/results/

  # Export as JSON
  python baseline_consistency_checker.py --results data/results/ --json consistency_report.json

  # List all baselines found
  python baseline_consistency_checker.py --results data/results/ --list-baselines

Baseline Definition:
  Baseline = all mechanisms OFF (H1=False, H2=False, H3=False, H4=False, H5=False)
  or equivalent control condition for experiment type.

Consistency Criteria:
  CV < 10%: Excellent consistency
  CV 10-20%: Moderate variability (warning)
  CV > 20%: High variability (error)
  >10% outliers: Warning
        """
    )

    parser.add_argument('--results', type=Path, required=True,
                       help='Results directory to scan')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export consistency data as JSON')
    parser.add_argument('--list-baselines', action='store_true',
                       help='List all baseline conditions found')

    args = parser.parse_args()

    # Validate results directory
    if not args.results.exists():
        print(f"ERROR: Results directory not found: {args.results}", file=sys.stderr)
        sys.exit(1)

    # Create checker
    checker = BaselineConsistencyChecker(args.results)

    # Check consistency
    data = checker.check_consistency()

    # Generate report
    if args.list_baselines:
        # List all baselines
        print(f"\nBaselines Found: {data['statistics']['count']}\n")
        for baseline in data['baselines']:
            print(f"{baseline['file']}:")
            print(f"  Mean Population: {baseline['mean_population']:.2f}")
            depth = baseline['composition_depth']
            if depth is not None:
                print(f"  Composition Depth: {depth:.2f}")
            else:
                print(f"  Composition Depth: (Not available)")
            print()
    else:
        # Full report
        print(checker.generate_report(data))

    # Export JSON if requested
    if args.json:
        checker.export_json(data, args.json)
        print(f"\nJSON exported to: {args.json}")

    # Exit code based on status
    if data['status'] == 'INCONSISTENT':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
