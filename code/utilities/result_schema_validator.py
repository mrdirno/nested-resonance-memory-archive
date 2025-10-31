#!/usr/bin/env python3
"""
Result Schema Validator - Experimental Data Structure Validation

Validates JSON result files against expected schemas for different
experiment types. Ensures structural integrity, required fields,
correct data types, and valid value ranges.

Supports multiple schema formats:
- Experiments List (C171, C175) - frequency/seed grid exploration
- Conditions Dict (C255+) - factorial mechanism combinations
- Results List (factorial) - multi-factor experimental designs

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict


class ResultSchemaValidator:
    """
    Validate experimental result files against expected schemas.

    Auto-detects schema format and validates:
    - Required fields present
    - Correct data types
    - Valid value ranges
    - Structural integrity
    """

    def __init__(self):
        """Initialize schema validator."""
        self.violations = []
        self.warnings = []

    def detect_schema_format(self, data: Any) -> Optional[str]:
        """
        Auto-detect schema format from data structure.

        Args:
            data: Parsed JSON data (dict or list)

        Returns:
            Schema format name or None if unrecognized
        """
        # Handle list at root level (some result files are arrays)
        if isinstance(data, list):
            return 'raw_list'

        # Handle non-dict data
        if not isinstance(data, dict):
            return None

        keys = set(data.keys())

        # Format 1: Experiments List
        if 'experiments' in keys and 'metadata' in keys:
            return 'experiments_list'

        # Format 2: Conditions Dict
        if 'conditions' in keys and 'metadata' in keys:
            return 'conditions_dict'

        # Format 3: Results List (factorial)
        if 'results' in keys and 'metadata' in keys:
            return 'results_list'

        # Format 4: Analysis results (meta-analysis, etc.)
        if 'analysis_type' in keys or 'summary' in keys:
            return 'analysis'

        return None

    def validate_metadata(self, metadata: Dict, file_path: Path) -> List[str]:
        """
        Validate metadata section (common to all formats).

        Args:
            metadata: Metadata dict
            file_path: Path to result file

        Returns:
            List of violation messages
        """
        violations = []

        # Required fields
        required_fields = ['cycle']
        for field in required_fields:
            if field not in metadata:
                violations.append(f"Missing required metadata field: {field}")

        # Recommended fields (warnings, not errors)
        recommended_fields = ['scenario', 'date', 'script']
        for field in recommended_fields:
            if field not in metadata:
                self.warnings.append(
                    f"{file_path.name}: Missing recommended metadata field: {field}"
                )

        # Type validation
        if 'cycle' in metadata:
            cycle = metadata['cycle']
            if not isinstance(cycle, (int, str)):
                violations.append(f"metadata.cycle must be int or str, got {type(cycle)}")

        if 'date' in metadata:
            date = metadata['date']
            if not isinstance(date, str):
                violations.append(f"metadata.date must be str, got {type(date)}")

        return violations

    def validate_experiments_list(self, data: Dict, file_path: Path) -> List[str]:
        """
        Validate experiments list format (C171, C175).

        Args:
            data: Full JSON data
            file_path: Path to result file

        Returns:
            List of violation messages
        """
        violations = []

        # Validate metadata
        if 'metadata' not in data:
            violations.append("Missing 'metadata' section")
            return violations  # Can't continue without metadata

        violations.extend(self.validate_metadata(data['metadata'], file_path))

        # Validate experiments list
        if 'experiments' not in data:
            violations.append("Missing 'experiments' list")
            return violations

        experiments = data['experiments']
        if not isinstance(experiments, list):
            violations.append(f"'experiments' must be list, got {type(experiments)}")
            return violations

        if len(experiments) == 0:
            self.warnings.append(f"{file_path.name}: Empty experiments list")

        # Validate each experiment
        for i, exp in enumerate(experiments):
            if not isinstance(exp, dict):
                violations.append(f"experiments[{i}] must be dict, got {type(exp)}")
                continue

            # Check for common fields (not all required, depends on experiment type)
            if 'frequency' in exp:
                if not isinstance(exp['frequency'], (int, float)):
                    violations.append(
                        f"experiments[{i}].frequency must be numeric, got {type(exp['frequency'])}"
                    )
                elif exp['frequency'] <= 0:
                    violations.append(
                        f"experiments[{i}].frequency must be positive, got {exp['frequency']}"
                    )

            if 'seed' in exp:
                if not isinstance(exp['seed'], int):
                    violations.append(
                        f"experiments[{i}].seed must be int, got {type(exp['seed'])}"
                    )

        return violations

    def validate_conditions_dict(self, data: Dict, file_path: Path) -> List[str]:
        """
        Validate conditions dict format (C255+).

        Args:
            data: Full JSON data
            file_path: Path to result file

        Returns:
            List of violation messages
        """
        violations = []

        # Validate metadata
        if 'metadata' not in data:
            violations.append("Missing 'metadata' section")
            return violations

        violations.extend(self.validate_metadata(data['metadata'], file_path))

        # Validate conditions dict
        if 'conditions' not in data:
            violations.append("Missing 'conditions' dict")
            return violations

        conditions = data['conditions']
        if not isinstance(conditions, dict):
            violations.append(f"'conditions' must be dict, got {type(conditions)}")
            return violations

        if len(conditions) == 0:
            self.warnings.append(f"{file_path.name}: Empty conditions dict")

        # Expected condition patterns for factorials
        expected_patterns = ['OFF-OFF', 'ON-OFF', 'OFF-ON', 'ON-ON']
        found_patterns = list(conditions.keys())

        # Check if baseline exists (OFF-OFF or OFF-OFF-OFF, etc.)
        baseline_patterns = [k for k in found_patterns if all(part == 'OFF' for part in k.split('-'))]
        if not baseline_patterns:
            self.warnings.append(
                f"{file_path.name}: No baseline condition (all OFF) found"
            )

        # Validate each condition
        for condition_name, condition_data in conditions.items():
            if not isinstance(condition_data, dict):
                violations.append(
                    f"conditions['{condition_name}'] must be dict, got {type(condition_data)}"
                )
                continue

            # Check for required metrics
            if 'mean_population' not in condition_data:
                violations.append(
                    f"conditions['{condition_name}'] missing 'mean_population'"
                )
            else:
                mean_pop = condition_data['mean_population']
                if not isinstance(mean_pop, (int, float)):
                    violations.append(
                        f"conditions['{condition_name}'].mean_population must be numeric, "
                        f"got {type(mean_pop)}"
                    )

        return violations

    def validate_results_list(self, data: Dict, file_path: Path) -> List[str]:
        """
        Validate results list format (factorial experiments).

        Args:
            data: Full JSON data
            file_path: Path to result file

        Returns:
            List of violation messages
        """
        violations = []

        # Validate metadata
        if 'metadata' not in data:
            violations.append("Missing 'metadata' section")
            return violations

        violations.extend(self.validate_metadata(data['metadata'], file_path))

        # Validate results list
        if 'results' not in data:
            violations.append("Missing 'results' list")
            return violations

        results = data['results']
        if not isinstance(results, list):
            violations.append(f"'results' must be list, got {type(results)}")
            return violations

        if len(results) == 0:
            self.warnings.append(f"{file_path.name}: Empty results list")

        # Validate each result
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                violations.append(f"results[{i}] must be dict, got {type(result)}")
                continue

            # Check for mechanism_config (factorial marker)
            if 'mechanism_config' in result:
                mech_config = result['mechanism_config']
                if not isinstance(mech_config, dict):
                    violations.append(
                        f"results[{i}].mechanism_config must be dict, "
                        f"got {type(mech_config)}"
                    )

        return violations

    def validate_file(self, file_path: Path) -> Dict:
        """
        Validate a single result file.

        Args:
            file_path: Path to result file

        Returns:
            Validation result dict
        """
        result = {
            'file': file_path.name,
            'valid': True,
            'schema_format': None,
            'violations': [],
            'warnings': []
        }

        # Read JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['violations'].append(f"Invalid JSON: {e}")
            return result
        except Exception as e:
            result['valid'] = False
            result['violations'].append(f"Error reading file: {e}")
            return result

        # Detect schema format
        schema_format = self.detect_schema_format(data)
        result['schema_format'] = schema_format

        if schema_format is None:
            result['valid'] = False
            result['violations'].append("Unrecognized schema format")
            return result

        # Validate based on schema
        self.violations = []
        self.warnings = []

        if schema_format == 'experiments_list':
            violations = self.validate_experiments_list(data, file_path)
        elif schema_format == 'conditions_dict':
            violations = self.validate_conditions_dict(data, file_path)
        elif schema_format == 'results_list':
            violations = self.validate_results_list(data, file_path)
        elif schema_format == 'analysis':
            # Analysis files have flexible schemas
            violations = []
            self.warnings.append(f"{file_path.name}: Analysis file (flexible schema)")
        elif schema_format == 'raw_list':
            # Raw list at root level (flexible schema, minimal validation)
            violations = []
            if len(data) == 0:
                self.warnings.append(f"{file_path.name}: Empty list")
            else:
                self.warnings.append(f"{file_path.name}: Raw list format ({len(data)} items)")
        else:
            violations = [f"Unknown schema format: {schema_format}"]

        result['violations'] = violations
        result['warnings'] = self.warnings

        if violations:
            result['valid'] = False

        return result

    def validate_directory(self, directory: Path) -> Dict:
        """
        Validate all result files in directory.

        Args:
            directory: Directory containing result files

        Returns:
            Summary dict with all validation results
        """
        results = []

        # Find all JSON files
        json_files = sorted(directory.glob('*.json'))

        for file_path in json_files:
            result = self.validate_file(file_path)
            results.append(result)

        # Calculate summary statistics
        total_files = len(results)
        valid_files = sum(1 for r in results if r['valid'])
        invalid_files = total_files - valid_files

        # Group by schema format
        schema_counts = defaultdict(int)
        for r in results:
            if r['schema_format']:
                schema_counts[r['schema_format']] += 1

        return {
            'timestamp': datetime.now().isoformat(),
            'directory': str(directory),
            'statistics': {
                'total_files': total_files,
                'valid_files': valid_files,
                'invalid_files': invalid_files,
                'validity_percent': (valid_files / total_files * 100) if total_files > 0 else 0
            },
            'schema_formats': dict(schema_counts),
            'results': results
        }

    def generate_report(self, validation_data: Dict) -> str:
        """
        Generate human-readable validation report.

        Args:
            validation_data: Validation data from validate_directory()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 100)
        lines.append("RESULT SCHEMA VALIDATION REPORT")
        lines.append("=" * 100)
        lines.append(f"\nGenerated: {validation_data['timestamp']}")
        lines.append(f"Directory: {validation_data['directory']}")
        lines.append("")

        # Statistics
        stats = validation_data['statistics']
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 100)
        lines.append(f"Total Files: {stats['total_files']}")
        lines.append(f"Valid Files: {stats['valid_files']} ({stats['validity_percent']:.1f}%)")
        lines.append(f"Invalid Files: {stats['invalid_files']}")
        lines.append("")

        # Schema format distribution
        schema_formats = validation_data['schema_formats']
        if schema_formats:
            lines.append("SCHEMA FORMAT DISTRIBUTION")
            lines.append("-" * 100)
            for schema, count in sorted(schema_formats.items()):
                lines.append(f"  {schema}: {count} files")
            lines.append("")

        # Invalid files
        invalid_results = [r for r in validation_data['results'] if not r['valid']]
        if invalid_results:
            lines.append("=" * 100)
            lines.append(f"✗ INVALID FILES ({len(invalid_results)})")
            lines.append("=" * 100)

            for result in invalid_results:
                lines.append(f"\n{result['file']}:")
                lines.append(f"  Schema Format: {result['schema_format'] or 'UNKNOWN'}")
                lines.append(f"  Violations ({len(result['violations'])}):")
                for violation in result['violations']:
                    lines.append(f"    - {violation}")

        # Warnings
        all_warnings = []
        for result in validation_data['results']:
            all_warnings.extend(result['warnings'])

        if all_warnings:
            lines.append("")
            lines.append("=" * 100)
            lines.append(f"⚠️  WARNINGS ({len(all_warnings)})")
            lines.append("=" * 100)

            for warning in all_warnings:
                lines.append(f"  - {warning}")

        # Valid files summary
        valid_results = [r for r in validation_data['results'] if r['valid']]
        if valid_results and not invalid_results:
            lines.append("")
            lines.append("=" * 100)
            lines.append(f"✓ ALL FILES VALID ({len(valid_results)})")
            lines.append("=" * 100)

        lines.append("")
        lines.append("=" * 100)
        lines.append("END OF REPORT")
        lines.append("=" * 100)

        return "\n".join(lines)

    def export_json(self, validation_data: Dict, output_path: Path):
        """
        Export validation data as JSON.

        Args:
            validation_data: Validation data from validate_directory()
            output_path: Path to write JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(validation_data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Validate experimental result file schemas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all results in directory
  python result_schema_validator.py --directory data/results/

  # Validate single file
  python result_schema_validator.py --file data/results/cycle255_h1h2_lightweight_results.json

  # Export validation data as JSON
  python result_schema_validator.py --directory data/results/ --json validation_report.json

  # Show only invalid files
  python result_schema_validator.py --directory data/results/ --invalid-only
        """
    )

    parser.add_argument('--directory', type=Path, default=None,
                       help='Directory containing result files')
    parser.add_argument('--file', type=Path, default=None,
                       help='Validate single file')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export validation data as JSON')
    parser.add_argument('--invalid-only', action='store_true',
                       help='Show only invalid files')

    args = parser.parse_args()

    # Create validator
    validator = ResultSchemaValidator()

    # Validate
    if args.file:
        # Single file validation
        result = validator.validate_file(args.file)

        print(f"File: {result['file']}")
        print(f"Schema Format: {result['schema_format']}")
        print(f"Valid: {'✓ Yes' if result['valid'] else '✗ No'}")

        if result['violations']:
            print(f"\nViolations ({len(result['violations'])}):")
            for violation in result['violations']:
                print(f"  - {violation}")

        if result['warnings']:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")

        if result['valid'] and not result['violations']:
            print("\n✓ File is valid")

    elif args.directory:
        # Directory validation
        validation_data = validator.validate_directory(args.directory)

        if args.invalid_only:
            # Show only invalid files
            invalid_results = [r for r in validation_data['results'] if not r['valid']]
            print(f"Invalid Files: {len(invalid_results)}")
            for result in invalid_results:
                print(f"\n{result['file']}:")
                print(f"  Schema Format: {result['schema_format'] or 'UNKNOWN'}")
                for violation in result['violations']:
                    print(f"    - {violation}")
        else:
            # Full report
            print(validator.generate_report(validation_data))

        # Export JSON if requested
        if args.json:
            validator.export_json(validation_data, args.json)
            print(f"\nJSON exported to: {args.json}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
