#!/usr/bin/env python3
"""
Data Completeness Checker - Experimental Archive Integrity

Scans experiment scripts and result files to identify:
- Complete experiments (script + results exist)
- Missing results (script exists, no results)
- Orphaned results (results exist, no script)
- Data coverage statistics

Provides data-centric view complementing the paper-centric status tracker.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime


class DataCompletenessChecker:
    """
    Check completeness of experimental data archive.

    Scans:
    - code/experiments/*.py (experiment scripts)
    - data/results/*.json (result files)

    Reports:
    - Complete experiments (script + results)
    - Missing results (script exists, no results)
    - Orphaned results (results exist, no script)
    - Coverage statistics
    """

    def __init__(self, repo_root: Path):
        """
        Initialize completeness checker.

        Args:
            repo_root: Root directory of repository
        """
        self.repo_root = Path(repo_root)
        self.experiments_dir = self.repo_root / 'code' / 'experiments'
        self.results_dir = self.repo_root / 'data' / 'results'

        # Cycle pattern: cycle<number>
        self.cycle_pattern = re.compile(r'cycle(\d+)')

    def scan_experiments(self) -> Dict[int, List[Path]]:
        """
        Scan experiment scripts.

        Returns:
            Dict mapping cycle number to list of script paths
        """
        experiments = defaultdict(list)

        for script in self.experiments_dir.glob('cycle*.py'):
            match = self.cycle_pattern.search(script.stem)
            if match:
                cycle_num = int(match.group(1))
                experiments[cycle_num].append(script)

        return dict(experiments)

    def scan_results(self) -> Dict[int, List[Path]]:
        """
        Scan result files.

        Returns:
            Dict mapping cycle number to list of result paths
        """
        results = defaultdict(list)

        for result_file in self.results_dir.glob('cycle*.json'):
            match = self.cycle_pattern.search(result_file.stem)
            if match:
                cycle_num = int(match.group(1))
                results[cycle_num].append(result_file)

        return dict(results)

    def check_completeness(self) -> Dict:
        """
        Check data completeness.

        Returns:
            Dict with completeness status
        """
        experiments = self.scan_experiments()
        results = self.scan_results()

        # All cycle numbers
        all_cycles = sorted(set(experiments.keys()) | set(results.keys()))

        # Categorize cycles
        complete = []
        missing_results = []
        orphaned_results = []

        for cycle in all_cycles:
            has_experiment = cycle in experiments
            has_results = cycle in results

            if has_experiment and has_results:
                complete.append({
                    'cycle': cycle,
                    'scripts': [s.name for s in experiments[cycle]],
                    'results': [r.name for r in results[cycle]]
                })
            elif has_experiment and not has_results:
                missing_results.append({
                    'cycle': cycle,
                    'scripts': [s.name for s in experiments[cycle]]
                })
            elif not has_experiment and has_results:
                orphaned_results.append({
                    'cycle': cycle,
                    'results': [r.name for r in results[cycle]]
                })

        # Statistics
        total_cycles = len(all_cycles)
        complete_count = len(complete)
        missing_count = len(missing_results)
        orphaned_count = len(orphaned_results)

        completeness_pct = (complete_count / total_cycles * 100) if total_cycles > 0 else 0

        return {
            'timestamp': datetime.now().isoformat(),
            'repository': str(self.repo_root),
            'statistics': {
                'total_cycles': total_cycles,
                'complete': complete_count,
                'missing_results': missing_count,
                'orphaned_results': orphaned_count,
                'completeness_percent': completeness_pct
            },
            'complete': complete,
            'missing_results': missing_results,
            'orphaned_results': orphaned_results,
            'cycle_range': {
                'min': min(all_cycles) if all_cycles else 0,
                'max': max(all_cycles) if all_cycles else 0
            }
        }

    def generate_report(self, data: Dict) -> str:
        """
        Generate human-readable completeness report.

        Args:
            data: Completeness data from check_completeness()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 100)
        lines.append("EXPERIMENTAL DATA COMPLETENESS REPORT")
        lines.append("=" * 100)
        lines.append(f"\nGenerated: {data['timestamp']}")
        lines.append(f"Repository: {data['repository']}")
        lines.append("")

        # Statistics
        stats = data['statistics']
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 100)
        lines.append(f"Total Cycles: {stats['total_cycles']}")
        lines.append(f"Complete (script + results): {stats['complete']} ({stats['completeness_percent']:.1f}%)")
        lines.append(f"Missing Results (script only): {stats['missing_results']}")
        lines.append(f"Orphaned Results (results only): {stats['orphaned_results']}")
        lines.append("")

        cycle_range = data['cycle_range']
        lines.append(f"Cycle Range: C{cycle_range['min']} - C{cycle_range['max']}")
        lines.append("")

        # Complete cycles
        if data['complete']:
            lines.append("=" * 100)
            lines.append(f"COMPLETE CYCLES ({len(data['complete'])})")
            lines.append("=" * 100)

            for item in data['complete']:
                lines.append(f"\n✓ Cycle {item['cycle']}:")
                lines.append(f"  Scripts ({len(item['scripts'])}):")
                for script in item['scripts']:
                    lines.append(f"    - {script}")
                lines.append(f"  Results ({len(item['results'])}):")
                for result in item['results']:
                    lines.append(f"    - {result}")

        # Missing results
        if data['missing_results']:
            lines.append("")
            lines.append("=" * 100)
            lines.append(f"⚠️  MISSING RESULTS ({len(data['missing_results'])})")
            lines.append("=" * 100)
            lines.append("\nExperiment scripts exist but no result files found:")

            for item in data['missing_results']:
                lines.append(f"\n✗ Cycle {item['cycle']}:")
                lines.append(f"  Scripts:")
                for script in item['scripts']:
                    lines.append(f"    - {script}")
                lines.append(f"  → Action: Run experiment or verify results location")

        # Orphaned results
        if data['orphaned_results']:
            lines.append("")
            lines.append("=" * 100)
            lines.append(f"⚠️  ORPHANED RESULTS ({len(data['orphaned_results'])})")
            lines.append("=" * 100)
            lines.append("\nResult files exist but no experiment scripts found:")

            for item in data['orphaned_results']:
                lines.append(f"\n? Cycle {item['cycle']}:")
                lines.append(f"  Results:")
                for result in item['results']:
                    lines.append(f"    - {result}")
                lines.append(f"  → Action: Verify experiment script location or archive results")

        lines.append("")
        lines.append("=" * 100)
        lines.append("END OF REPORT")
        lines.append("=" * 100)

        return "\n".join(lines)

    def generate_summary(self, data: Dict) -> str:
        """
        Generate brief summary suitable for logging.

        Args:
            data: Completeness data from check_completeness()

        Returns:
            Brief summary string
        """
        stats = data['statistics']
        cycle_range = data['cycle_range']

        return (
            f"Data Completeness: {stats['complete']}/{stats['total_cycles']} cycles "
            f"({stats['completeness_percent']:.1f}%), "
            f"Range: C{cycle_range['min']}-C{cycle_range['max']}, "
            f"Missing: {stats['missing_results']}, "
            f"Orphaned: {stats['orphaned_results']}"
        )

    def export_json(self, data: Dict, output_path: Path):
        """
        Export completeness data as JSON.

        Args:
            data: Completeness data from check_completeness()
            output_path: Path to write JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Check experimental data completeness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full completeness report
  python data_completeness_checker.py

  # Brief summary only
  python data_completeness_checker.py --summary

  # Export as JSON
  python data_completeness_checker.py --json completeness_report.json

  # Check specific directory
  python data_completeness_checker.py --repo /path/to/repo

  # Show only problems (missing/orphaned)
  python data_completeness_checker.py --problems-only
        """
    )

    parser.add_argument('--repo', type=Path, default=Path.cwd(),
                       help='Repository root (default: current directory)')
    parser.add_argument('--summary', action='store_true',
                       help='Show brief summary only')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export as JSON to specified file')
    parser.add_argument('--problems-only', action='store_true',
                       help='Show only missing/orphaned cycles')

    args = parser.parse_args()

    # Create checker
    checker = DataCompletenessChecker(args.repo)

    # Check completeness
    data = checker.check_completeness()

    # Output
    if args.summary:
        print(checker.generate_summary(data))
    elif args.problems_only:
        # Show only problems
        stats = data['statistics']
        print(f"Missing Results: {stats['missing_results']}")
        if data['missing_results']:
            for item in data['missing_results']:
                print(f"  C{item['cycle']}: {', '.join(item['scripts'])}")

        print(f"\nOrphaned Results: {stats['orphaned_results']}")
        if data['orphaned_results']:
            for item in data['orphaned_results']:
                print(f"  C{item['cycle']}: {', '.join(item['results'])}")
    else:
        print(checker.generate_report(data))

    # Export JSON if requested
    if args.json:
        checker.export_json(data, args.json)
        print(f"\nJSON exported to: {args.json}")


if __name__ == '__main__':
    main()
