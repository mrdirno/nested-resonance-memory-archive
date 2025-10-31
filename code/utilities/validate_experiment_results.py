#!/usr/bin/env python3
"""
Experiment Result Validator - Sanity checks before analysis

Validates experimental outputs for:
- File existence and completeness
- JSON structure validity
- Required fields presence
- Data type correctness
- Value range sanity checks
- Missing data detection
- Statistical outlier detection

Designed for early error detection before expensive analysis runs.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

try:
    import numpy as np
except ImportError:
    print("Error: numpy required. Install with: pip install numpy", file=sys.stderr)
    sys.exit(1)


class ExperimentResultValidator:
    """
    Validate experimental result files before analysis.

    Checks:
    - File structure (JSON validity)
    - Required fields (configuration, results, metrics)
    - Data completeness (no null/missing values in critical fields)
    - Value ranges (population > 0, depth >= 0, etc.)
    - Statistical sanity (mean vs median, outliers, variance)
    """

    def __init__(self, result_file: Path):
        """
        Initialize validator with result file.

        Args:
            result_file: Path to experimental result JSON
        """
        self.result_file = result_file
        self.data = None
        self.errors = []
        self.warnings = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        # Check 1: File exists
        if not self.result_file.exists():
            self.errors.append(f"File not found: {self.result_file}")
            return False, self.errors, self.warnings

        # Check 2: Valid JSON
        try:
            with open(self.result_file, 'r') as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return False, self.errors, self.warnings

        # Check 3: Top-level structure
        self._validate_structure()

        # Check 4: Configuration completeness
        self._validate_configuration()

        # Check 5: Results completeness
        self._validate_results()

        # Check 6: Value ranges
        self._validate_value_ranges()

        # Check 7: Statistical sanity
        self._validate_statistical_sanity()

        # Return summary
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_structure(self):
        """Validate top-level JSON structure."""
        required_top_level = ['experiment_name', 'configuration', 'results']

        for field in required_top_level:
            if field not in self.data:
                self.errors.append(f"Missing top-level field: {field}")

    def _validate_configuration(self):
        """Validate configuration completeness."""
        if 'configuration' not in self.data:
            return  # Already reported in structure check

        config = self.data['configuration']
        required_config = ['mechanism_config', 'cycles', 'seed']

        for field in required_config:
            if field not in config:
                self.errors.append(f"Missing configuration field: {field}")

        # Check mechanism config structure
        if 'mechanism_config' in config:
            mech_config = config['mechanism_config']
            if not isinstance(mech_config, dict):
                self.errors.append("mechanism_config must be a dict")
            else:
                # Check boolean mechanism flags
                expected_mechanisms = ['H1', 'H2', 'H3', 'H4', 'H5']
                for mech in expected_mechanisms:
                    if mech in mech_config:
                        if not isinstance(mech_config[mech], bool):
                            self.warnings.append(f"{mech} should be boolean (true/false)")

    def _validate_results(self):
        """Validate results completeness."""
        if 'results' not in self.data:
            return  # Already reported in structure check

        results = self.data['results']

        # Check if results is a dict or list
        if isinstance(results, dict):
            # Single-condition experiment
            self._validate_single_result(results, "results")
        elif isinstance(results, list):
            # Multi-condition experiment (factorial)
            if len(results) == 0:
                self.errors.append("Results list is empty")
            else:
                for i, result in enumerate(results):
                    self._validate_single_result(result, f"results[{i}]")
        else:
            self.errors.append("Results must be dict or list")

    def _validate_single_result(self, result: Dict, path: str):
        """Validate a single result dict."""
        # Required fields for a result
        required_result_fields = ['mean_population', 'composition_depth']

        for field in required_result_fields:
            if field not in result:
                self.errors.append(f"{path}: Missing required field '{field}'")
            else:
                value = result[field]

                # Check for null/None
                if value is None:
                    self.errors.append(f"{path}.{field}: Value is null")

                # Check data type
                if not isinstance(value, (int, float, list)):
                    self.errors.append(f"{path}.{field}: Invalid type {type(value)}")

                # If list, check for empty or all-null
                if isinstance(value, list):
                    if len(value) == 0:
                        self.errors.append(f"{path}.{field}: Empty list")
                    elif all(v is None for v in value):
                        self.errors.append(f"{path}.{field}: All values are null")

    def _validate_value_ranges(self):
        """Validate value ranges are sensible."""
        if 'results' not in self.data:
            return

        results = self.data['results']

        # Normalize to list
        if isinstance(results, dict):
            results_list = [results]
        else:
            results_list = results

        for i, result in enumerate(results_list):
            path = f"results[{i}]" if isinstance(self.data['results'], list) else "results"

            # Check population
            if 'mean_population' in result:
                pop = result['mean_population']
                if isinstance(pop, (int, float)):
                    if pop < 0:
                        self.errors.append(f"{path}.mean_population: Negative value {pop}")
                    elif pop == 0:
                        self.warnings.append(f"{path}.mean_population: Zero population (extinction?)")
                    elif pop > 100000:
                        self.warnings.append(f"{path}.mean_population: Very large value {pop} (>100k)")

            # Check composition depth
            if 'composition_depth' in result:
                depth = result['composition_depth']
                if isinstance(depth, (int, float)):
                    if depth < 0:
                        self.errors.append(f"{path}.composition_depth: Negative value {depth}")
                    elif depth > 1000:
                        self.warnings.append(f"{path}.composition_depth: Very large value {depth} (>1000)")

            # Check runtime
            if 'runtime_seconds' in result:
                runtime = result['runtime_seconds']
                if isinstance(runtime, (int, float)):
                    if runtime < 0:
                        self.errors.append(f"{path}.runtime_seconds: Negative value {runtime}")
                    elif runtime < 60:
                        self.warnings.append(f"{path}.runtime_seconds: Very short runtime {runtime}s (<1 min)")
                    elif runtime > 172800:  # 48 hours
                        self.warnings.append(f"{path}.runtime_seconds: Very long runtime {runtime/3600:.1f}h (>48h)")

    def _validate_statistical_sanity(self):
        """Validate statistical sanity of results."""
        if 'results' not in self.data:
            return

        results = self.data['results']

        # Normalize to list
        if isinstance(results, dict):
            results_list = [results]
        else:
            results_list = results

        # Collect populations across conditions
        populations = []
        for result in results_list:
            if 'mean_population' in result:
                pop = result['mean_population']
                if isinstance(pop, (int, float)) and pop > 0:
                    populations.append(pop)

        # Check if we have enough data
        if len(populations) < 2:
            return  # Need at least 2 values for comparison

        # Statistical checks
        mean_pop = np.mean(populations)
        median_pop = np.median(populations)
        std_pop = np.std(populations)

        # Check 1: Mean vs Median (skewness indicator)
        if mean_pop > 0:
            diff_pct = abs(mean_pop - median_pop) / mean_pop * 100
            if diff_pct > 50:
                self.warnings.append(f"Large mean-median difference ({diff_pct:.1f}%) - skewed distribution?")

        # Check 2: Coefficient of variation (CV)
        if mean_pop > 0:
            cv = (std_pop / mean_pop) * 100
            if cv > 200:
                self.warnings.append(f"Very high variability (CV={cv:.1f}%) - unstable system?")

        # Check 3: Outliers (IQR method)
        q1 = np.percentile(populations, 25)
        q3 = np.percentile(populations, 75)
        iqr = q3 - q1

        if iqr > 0:
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = [p for p in populations if p < lower_bound or p > upper_bound]

            if len(outliers) > 0:
                outlier_pct = len(outliers) / len(populations) * 100
                if outlier_pct > 20:
                    self.warnings.append(f"Many outliers ({outlier_pct:.1f}% of data) - check experimental conditions")

    def generate_report(self) -> str:
        """Generate human-readable validation report."""
        lines = []
        lines.append("=" * 80)
        lines.append("EXPERIMENT RESULT VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nFile: {self.result_file}")

        if self.data:
            exp_name = self.data.get('experiment_name', 'Unknown')
            lines.append(f"Experiment: {exp_name}")

            # Configuration summary
            if 'configuration' in self.data:
                config = self.data['configuration']
                lines.append(f"\nConfiguration:")
                lines.append(f"  Cycles: {config.get('cycles', 'N/A')}")
                lines.append(f"  Seed: {config.get('seed', 'N/A')}")

                if 'mechanism_config' in config:
                    mech = config['mechanism_config']
                    enabled = [k for k, v in mech.items() if v is True]
                    lines.append(f"  Mechanisms Enabled: {', '.join(enabled) if enabled else 'None'}")

            # Results summary
            if 'results' in self.data:
                results = self.data['results']
                if isinstance(results, list):
                    lines.append(f"\nResults: {len(results)} conditions")
                else:
                    lines.append(f"\nResults: Single condition")

        lines.append("")

        # Validation status
        is_valid = len(self.errors) == 0

        if is_valid:
            lines.append("✓ VALIDATION PASSED")
        else:
            lines.append("✗ VALIDATION FAILED")

        # Errors
        if self.errors:
            lines.append(f"\nERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"  {i}. {error}")

        # Warnings
        if self.warnings:
            lines.append(f"\nWARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {warning}")

        if is_valid and not self.warnings:
            lines.append("\n✓ No issues detected. Results are ready for analysis.")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Validate experimental result files before analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single result file
  python validate_experiment_results.py \\
      --file data/results/cycle255_h1h2_results.json

  # Validate all results in directory
  python validate_experiment_results.py \\
      --directory data/results/ \\
      --pattern "cycle25*.json"

  # Strict mode (fail on warnings)
  python validate_experiment_results.py \\
      --file data/results/cycle256_results.json \\
      --strict
        """
    )

    parser.add_argument('--file', type=Path, default=None,
                       help='Single result file to validate')
    parser.add_argument('--directory', type=Path, default=None,
                       help='Directory containing result files')
    parser.add_argument('--pattern', type=str, default="*.json",
                       help='File pattern for directory validation (default: *.json)')
    parser.add_argument('--strict', action='store_true',
                       help='Treat warnings as errors')

    args = parser.parse_args()

    # Validate arguments
    if not args.file and not args.directory:
        print("ERROR: Must specify --file or --directory", file=sys.stderr)
        sys.exit(1)

    # Collect files to validate
    files_to_validate = []

    if args.file:
        files_to_validate.append(args.file)

    if args.directory:
        if not args.directory.exists():
            print(f"ERROR: Directory not found: {args.directory}", file=sys.stderr)
            sys.exit(1)

        files_to_validate.extend(args.directory.glob(args.pattern))

    if not files_to_validate:
        print("ERROR: No files found to validate", file=sys.stderr)
        sys.exit(1)

    # Validate all files
    total_files = len(files_to_validate)
    passed = 0
    failed = 0
    warnings_count = 0

    print(f"\nValidating {total_files} file(s)...\n")

    for file_path in files_to_validate:
        validator = ExperimentResultValidator(file_path)
        is_valid, errors, warnings = validator.validate()

        if not is_valid:
            failed += 1
        elif args.strict and warnings:
            failed += 1
        else:
            passed += 1

        if warnings:
            warnings_count += len(warnings)

        # Print report
        print(validator.generate_report())
        print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Files: {total_files}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total Warnings: {warnings_count}")
    print("=" * 80)

    # Exit code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
