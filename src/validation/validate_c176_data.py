#!/usr/bin/env python3
"""
C176 V6 Data Validation Script

Validates experimental data files for structural correctness, completeness,
and consistency. Ensures data quality before Paper 2 finalization.

Checks:
- JSON file structure and schema
- Required fields present
- Data types correct
- Value ranges reasonable
- Cross-seed consistency
- Statistical anomalies

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-02
License: GPL-3.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np


class DataValidator:
    """Validates C176 V6 experimental data files."""

    def __init__(self, data_path: Path):
        """
        Initialize validator.

        Args:
            data_path: Path to experimental data JSON file
        """
        self.data_path = data_path
        self.data = None
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """
        Run complete validation suite.

        Returns:
            True if all validations pass, False otherwise
        """
        print("=" * 80)
        print("C176 V6 DATA VALIDATION")
        print("=" * 80)
        print(f"\nData file: {self.data_path}")
        print()

        # Load data
        if not self.load_data():
            return False

        # Run validation checks
        self.check_structure()
        self.check_metadata()
        self.check_results()
        self.check_seed_data()
        self.check_statistical_consistency()

        # Report results
        self.report()

        return len(self.errors) == 0

    def load_data(self) -> bool:
        """
        Load and parse JSON data file.

        Returns:
            True if successful, False otherwise
        """
        if not self.data_path.exists():
            self.errors.append(f"Data file not found: {self.data_path}")
            return False

        try:
            with open(self.data_path, 'r') as f:
                self.data = json.load(f)
            print("✓ Data file loaded successfully")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading data: {e}")
            return False

    def check_structure(self):
        """Check top-level data structure."""
        print("\nChecking data structure...")

        # Required top-level fields
        required_fields = ['experiment', 'parameters', 'results']
        for field in required_fields:
            if field not in self.data:
                self.errors.append(f"Missing required field: {field}")
            else:
                print(f"  ✓ Field present: {field}")

    def check_metadata(self):
        """Check experiment metadata."""
        print("\nChecking metadata...")

        if 'experiment' not in self.data:
            return

        experiment = self.data['experiment']

        # Verify experiment name
        if experiment != 'C176_V6_Incremental_Validation':
            self.warnings.append(
                f"Unexpected experiment name: {experiment}"
            )
        else:
            print(f"  ✓ Experiment: {experiment}")

        # Check parameters
        if 'parameters' not in self.data:
            return

        params = self.data['parameters']

        # Expected parameter values
        expected = {
            'initial_energy': 10.0,
            'spawn_cost': 3.0,
            'recovery_rate': 0.016,
            'spawn_frequency': 0.025,
            'max_cycles': 1000,
            'n_seeds': 5
        }

        for key, expected_value in expected.items():
            if key not in params:
                self.errors.append(f"Missing parameter: {key}")
            elif params[key] != expected_value:
                self.warnings.append(
                    f"Parameter mismatch: {key} = {params[key]} "
                    f"(expected {expected_value})"
                )
            else:
                print(f"  ✓ Parameter: {key} = {params[key]}")

    def check_results(self):
        """Check results array structure."""
        print("\nChecking results array...")

        if 'results' not in self.data:
            self.errors.append("Missing 'results' field")
            return

        results = self.data['results']

        if not isinstance(results, list):
            self.errors.append("'results' must be a list")
            return

        n_seeds = len(results)
        print(f"  ✓ Found {n_seeds} seed results")

        if n_seeds < 5:
            self.warnings.append(
                f"Only {n_seeds}/5 seeds present (experiment incomplete)"
            )
        elif n_seeds > 5:
            self.warnings.append(
                f"More than 5 seeds found ({n_seeds})"
            )
        else:
            print(f"  ✓ All 5 seeds present")

    def check_seed_data(self):
        """Check individual seed result structure."""
        print("\nChecking seed data...")

        if 'results' not in self.data:
            return

        # Required fields per seed
        required_fields = [
            'seed',
            'final_population',
            'mean_population',
            'cv_percent',
            'spawn_success',
            'total_spawn_attempts',
            'basin'
        ]

        optional_fields = [
            'population_trajectory',
            'energy_trajectory',
            'spawn_attempts'
        ]

        for i, result in enumerate(self.data['results']):
            seed = result.get('seed', f'unknown_{i}')
            print(f"\n  Seed {seed}:")

            # Check required fields
            for field in required_fields:
                if field not in result:
                    self.errors.append(
                        f"Seed {seed}: Missing required field '{field}'"
                    )
                else:
                    print(f"    ✓ {field}: {result[field]}")

            # Check optional fields (warn if missing)
            for field in optional_fields:
                if field not in result:
                    self.warnings.append(
                        f"Seed {seed}: Missing optional field '{field}'"
                    )

            # Validate value ranges
            self.check_value_ranges(seed, result)

    def check_value_ranges(self, seed: int, result: Dict):
        """
        Check if values are within reasonable ranges.

        Args:
            seed: Seed number
            result: Seed result dictionary
        """
        # Population should be positive
        if 'final_population' in result:
            pop = result['final_population']
            if pop < 1:
                self.errors.append(
                    f"Seed {seed}: Invalid final_population ({pop})"
                )
            elif pop > 50:
                self.warnings.append(
                    f"Seed {seed}: Unusually large population ({pop})"
                )

        # CV should be reasonable
        if 'cv_percent' in result:
            cv = result['cv_percent']
            if cv < 0:
                self.errors.append(
                    f"Seed {seed}: Negative CV ({cv})"
                )
            elif cv > 50:
                self.warnings.append(
                    f"Seed {seed}: Very high CV ({cv}%)"
                )

        # Spawn success should be 0-100%
        if 'spawn_success' in result:
            success = result['spawn_success']
            # Handle both decimal and percentage formats
            if success > 1.0:  # Percentage format
                if success < 0 or success > 100:
                    self.errors.append(
                        f"Seed {seed}: Invalid success rate ({success}%)"
                    )
            else:  # Decimal format
                if success < 0 or success > 1.0:
                    self.errors.append(
                        f"Seed {seed}: Invalid success rate ({success})"
                    )

        # Basin should be A, B, or C
        if 'basin' in result:
            basin = result['basin']
            if basin not in ['A', 'B', 'C']:
                self.errors.append(
                    f"Seed {seed}: Invalid basin classification ({basin})"
                )

    def check_statistical_consistency(self):
        """Check statistical consistency across seeds."""
        print("\nChecking statistical consistency...")

        if 'results' not in self.data or len(self.data['results']) < 2:
            print("  ⚠ Not enough seeds for consistency check")
            return

        # Extract success rates
        success_rates = []
        for result in self.data['results']:
            if 'spawn_success' in result:
                success = result['spawn_success']
                # Convert to percentage if in decimal
                if success <= 1.0:
                    success *= 100.0
                success_rates.append(success)

        if len(success_rates) < 2:
            return

        # Check for outliers (> 3 SD from mean)
        mean = np.mean(success_rates)
        sd = np.std(success_rates, ddof=1)

        print(f"  Success rates: {[f'{s:.1f}%' for s in success_rates]}")
        print(f"  Mean: {mean:.1f}%, SD: {sd:.1f}%")

        for i, success in enumerate(success_rates):
            seed = self.data['results'][i].get('seed', i)
            z_score = abs((success - mean) / sd) if sd > 0 else 0

            if z_score > 3:
                self.warnings.append(
                    f"Seed {seed}: Success rate ({success:.1f}%) is outlier "
                    f"(|z|={z_score:.2f} > 3)"
                )

        # Check coefficient of variation
        cv = (sd / mean * 100) if mean > 0 else 0
        print(f"  CV: {cv:.1f}%")

        if cv > 20:
            self.warnings.append(
                f"High variability across seeds (CV={cv:.1f}%)"
            )
        else:
            print(f"  ✓ Acceptable variability (CV < 20%)")

    def report(self):
        """Generate validation report."""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("\n✓ ALL CHECKS PASSED")
            print("  Data is valid and ready for analysis")
        else:
            if len(self.errors) > 0:
                print(f"\n✗ ERRORS ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  • {error}")

            if len(self.warnings) > 0:
                print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  • {warning}")

        print("\n" + "=" * 80)
        print()

        if len(self.errors) > 0:
            print("Action required: Fix errors before proceeding with analysis")
            return False
        elif len(self.warnings) > 0:
            print("Action suggested: Review warnings (may be acceptable)")
            return True
        else:
            print("Status: Data validated successfully")
            return True


def main():
    """Main execution function."""
    # Determine data path
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent
    data_path = repo_root / 'data' / 'results' / 'c176_v6_incremental_validation_results.json'

    # Create validator
    validator = DataValidator(data_path)

    # Run validation
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
