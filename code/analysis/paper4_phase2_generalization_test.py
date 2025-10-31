#!/usr/bin/env python3
"""
Paper 4 Phase 2: Generalization Test Analysis

Tests whether lower-order models predict higher-order behavior:
- Can pairwise models (Paper 3) predict 3-way interactions?
- Can pairwise + 3-way models predict 4-way interaction?

Quantifies prediction errors and classifies generalization quality:
- EXCELLENT: MAPE < 5%
- GOOD: MAPE 5-10%
- POOR: MAPE > 10%

Designed for immediate execution when C262-C263 complete (zero-delay finalization).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
import sys

try:
    import numpy as np
except ImportError:
    print("Error: numpy required. Install with: pip install numpy", file=sys.stderr)
    sys.exit(1)


class GeneralizationTester:
    """
    Test generalization of lower-order models to higher-order interactions.

    Hypothesis: If mechanisms combine additively across orders, then:
    - Pairwise models should predict 3-way behavior (within ±10%)
    - Pairwise + 3-way models should predict 4-way behavior (within ±10%)

    Rejection: If prediction errors > 10%, emergent synergies exist.
    """

    def __init__(
        self,
        pairwise_results: Dict,
        three_way_results: Dict,
        four_way_results: Dict = None
    ):
        """
        Initialize tester with Phase 1 results.

        Args:
            pairwise_results: Paper 3 pairwise classification results
            three_way_results: Paper 4 3-way synergy results
            four_way_results: Paper 4 4-way synergy results (optional)
        """
        self.pairwise_results = pairwise_results
        self.three_way_results = three_way_results
        self.four_way_results = four_way_results

    @classmethod
    def from_json(cls, pairwise_path: Path, three_way_path: Path, four_way_path: Path = None):
        """Load results from JSON files."""
        with open(pairwise_path, 'r') as f:
            pairwise = json.load(f)

        with open(three_way_path, 'r') as f:
            three_way = json.load(f)

        four_way = None
        if four_way_path and four_way_path.exists():
            with open(four_way_path, 'r') as f:
                four_way = json.load(f)

        return cls(pairwise, three_way, four_way)

    def test_3way_generalization(self) -> Dict:
        """
        Test if pairwise models predict 3-way behavior.

        Returns:
            Dict with generalization test results for all 3-way combinations
        """
        results = {}

        for combo_id, three_way_data in self.three_way_results.items():
            if 'error' in three_way_data:
                results[combo_id] = {'error': three_way_data['error']}
                continue

            # Extract prediction data
            prediction_data = three_way_data.get('prediction', {})

            predicted = prediction_data.get('from_pairwise', 0)
            observed = prediction_data.get('observed', 0)
            synergy_3way = prediction_data.get('synergy_3way_absolute', 0)
            synergy_3way_pct = prediction_data.get('synergy_3way_percent', 0)

            baseline = three_way_data.get('baseline', 1)

            # Calculate prediction error
            if observed > 0:
                absolute_error = abs(observed - predicted)
                percent_error = (absolute_error / observed * 100)
                mape = percent_error  # Mean absolute percentage error (single observation)
            else:
                absolute_error = abs(synergy_3way)
                percent_error = abs(synergy_3way_pct)
                mape = percent_error

            # Generalization quality classification
            if mape < 5:
                quality = 'EXCELLENT'
                interpretation = 'Pairwise model predicts 3-way behavior very accurately (<5% error)'
            elif mape < 10:
                quality = 'GOOD'
                interpretation = 'Pairwise model predicts 3-way behavior adequately (5-10% error)'
            else:
                quality = 'POOR'
                interpretation = 'Pairwise model fails to predict 3-way behavior (>10% error)'

            # Generalization verdict
            generalizes = abs(synergy_3way_pct) <= 10

            results[combo_id] = {
                'combination': combo_id,
                'predicted_from_pairwise': predicted,
                'observed': observed,
                'absolute_error': absolute_error,
                'percent_error': percent_error,
                'mape': mape,
                'synergy_3way_percent': synergy_3way_pct,
                'generalizes': generalizes,
                'quality': quality,
                'interpretation': interpretation
            }

        return results

    def test_4way_generalization(self) -> Dict:
        """
        Test if pairwise + 3-way models predict 4-way behavior.

        Returns:
            Dict with generalization test results for 4-way combination
        """
        if not self.four_way_results or 'error' in self.four_way_results:
            return {'error': '4-way results not available or contain errors'}

        # Extract 4-way prediction data
        prediction_data = self.four_way_results.get('prediction', {})

        predicted = prediction_data.get('from_lower_orders', 0)
        observed = prediction_data.get('observed', 0)
        synergy_4way = prediction_data.get('synergy_4way_absolute', 0)
        synergy_4way_pct = prediction_data.get('synergy_4way_percent', 0)

        baseline = self.four_way_results.get('baseline', 1)

        # Calculate prediction error
        if observed > 0:
            absolute_error = abs(observed - predicted)
            percent_error = (absolute_error / observed * 100)
            mape = percent_error
        else:
            absolute_error = abs(synergy_4way)
            percent_error = abs(synergy_4way_pct)
            mape = percent_error

        # Generalization quality classification
        if mape < 5:
            quality = 'EXCELLENT'
            interpretation = 'Lower-order models predict 4-way behavior very accurately (<5% error)'
        elif mape < 10:
            quality = 'GOOD'
            interpretation = 'Lower-order models predict 4-way behavior adequately (5-10% error)'
        else:
            quality = 'POOR'
            interpretation = 'Lower-order models fail to predict 4-way behavior (>10% error)'

        # Generalization verdict
        generalizes = abs(synergy_4way_pct) <= 10

        return {
            'combination': 'H1xH2xH4xH5',
            'predicted_from_lower_orders': predicted,
            'observed': observed,
            'absolute_error': absolute_error,
            'percent_error': percent_error,
            'mape': mape,
            'synergy_4way_percent': synergy_4way_pct,
            'generalizes': generalizes,
            'quality': quality,
            'interpretation': interpretation
        }

    def generalization_summary_statistics(self) -> Dict:
        """Calculate summary statistics for generalization performance."""
        three_way_tests = self.test_3way_generalization()

        # Collect valid 3-way errors
        three_way_mapes = []
        three_way_generalizes_count = 0
        three_way_total = 0

        for combo_id, result in three_way_tests.items():
            if 'error' in result:
                continue

            three_way_mapes.append(result['mape'])
            three_way_total += 1
            if result['generalizes']:
                three_way_generalizes_count += 1

        # 3-way statistics
        three_way_stats = {}
        if len(three_way_mapes) > 0:
            three_way_stats = {
                'mean_mape': np.mean(three_way_mapes),
                'std_mape': np.std(three_way_mapes),
                'min_mape': np.min(three_way_mapes),
                'max_mape': np.max(three_way_mapes),
                'median_mape': np.median(three_way_mapes),
                'generalization_rate': (three_way_generalizes_count / three_way_total * 100) if three_way_total > 0 else 0,
                'total_combinations': three_way_total
            }

        # 4-way statistics
        four_way_stats = {}
        four_way_test = self.test_4way_generalization()
        if 'error' not in four_way_test:
            four_way_stats = {
                'mape': four_way_test['mape'],
                'generalizes': four_way_test['generalizes'],
                'quality': four_way_test['quality']
            }

        return {
            'three_way': three_way_stats,
            'four_way': four_way_stats
        }

    def generate_generalization_report(self) -> str:
        """Generate comprehensive generalization test report."""
        lines = []
        lines.append("=" * 80)
        lines.append("PAPER 4 PHASE 2: GENERALIZATION TEST")
        lines.append("=" * 80)
        lines.append("")

        # 3-way generalization tests
        three_way_tests = self.test_3way_generalization()
        lines.append("3-WAY GENERALIZATION TEST")
        lines.append("Question: Can pairwise models (Paper 3) predict 3-way behavior?")
        lines.append("-" * 80)
        lines.append(f"{'Combination':<15} {'MAPE':<10} {'Quality':<12} {'Generalizes':<12}")
        lines.append("-" * 80)

        for combo_id, result in three_way_tests.items():
            if 'error' in result:
                lines.append(f"{combo_id:<15} ERROR: {result['error']}")
                continue

            generalizes_str = "YES" if result['generalizes'] else "NO"
            lines.append(f"{combo_id:<15} {result['mape']:>8.2f}% {result['quality']:<12} {generalizes_str:<12}")

        lines.append("")

        # 3-way summary statistics
        summary_stats = self.generalization_summary_statistics()
        if 'three_way' in summary_stats and summary_stats['three_way']:
            three_way_stats = summary_stats['three_way']
            lines.append("3-Way Summary Statistics:")
            lines.append(f"  Mean MAPE:          {three_way_stats.get('mean_mape', 0):>10.2f}%")
            lines.append(f"  Std MAPE:           {three_way_stats.get('std_mape', 0):>10.2f}%")
            lines.append(f"  Range MAPE:         [{three_way_stats.get('min_mape', 0):.2f}%, {three_way_stats.get('max_mape', 0):.2f}%]")
            lines.append(f"  Median MAPE:        {three_way_stats.get('median_mape', 0):>10.2f}%")
            lines.append(f"  Generalization Rate: {three_way_stats.get('generalization_rate', 0):>10.1f}% "
                        f"({three_way_generalizes_count}/{three_way_stats.get('total_combinations', 0)} combinations)")
            lines.append("")

        # 4-way generalization test
        four_way_test = self.test_4way_generalization()
        if 'error' not in four_way_test:
            lines.append("4-WAY GENERALIZATION TEST")
            lines.append("Question: Can pairwise + 3-way models predict 4-way behavior?")
            lines.append("-" * 80)

            generalizes_str = "YES" if four_way_test['generalizes'] else "NO"
            lines.append(f"Combination: {four_way_test['combination']}")
            lines.append(f"  MAPE:        {four_way_test['mape']:>10.2f}%")
            lines.append(f"  Quality:     {four_way_test['quality']}")
            lines.append(f"  Generalizes: {generalizes_str}")
            lines.append(f"  Interpretation: {four_way_test['interpretation']}")
            lines.append("")

        # Overall verdict
        lines.append("OVERALL GENERALIZATION VERDICT")
        lines.append("-" * 80)

        three_way_gen_rate = summary_stats.get('three_way', {}).get('generalization_rate', 0)
        four_way_generalizes = four_way_test.get('generalizes', False) if 'error' not in four_way_test else None

        if three_way_gen_rate >= 75:
            lines.append("  3-Way: PAIRWISE MODELS GENERALIZE (≥75% combinations within ±10%)")
        elif three_way_gen_rate >= 50:
            lines.append("  3-Way: PARTIAL GENERALIZATION (50-75% combinations within ±10%)")
        else:
            lines.append("  3-Way: EMERGENT SYNERGIES DOMINANT (<50% combinations within ±10%)")

        if four_way_generalizes is not None:
            if four_way_generalizes:
                lines.append("  4-Way: LOWER-ORDER MODELS GENERALIZE (within ±10%)")
            else:
                lines.append("  4-Way: EMERGENT 4-WAY SYNERGY (beyond ±10% prediction)")

        lines.append("")

        # Research implications
        lines.append("RESEARCH IMPLICATIONS")
        lines.append("-" * 80)

        if three_way_gen_rate >= 75 and four_way_generalizes:
            lines.append("  → SCENARIO A: ADDITIVE ARCHITECTURE")
            lines.append("     Mechanisms combine additively across orders.")
            lines.append("     Optimization: Tune mechanisms independently using pairwise models.")
        elif three_way_gen_rate < 50 or (four_way_generalizes is not None and not four_way_generalizes):
            lines.append("  → SCENARIO C: EMERGENT COMPLEXITY")
            lines.append("     Significant higher-order synergies present.")
            lines.append("     Optimization: Holistic optimization required; cannot decompose.")
        else:
            lines.append("  → SCENARIO B: PARTIAL EMERGENCE")
            lines.append("     Some 3-way synergies, but 4-way may be predictable.")
            lines.append("     Optimization: Consider triplets; 4-way may follow patterns.")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def export_generalization_json(self, output_path: Path):
        """Export generalization test results as JSON."""
        three_way_tests = self.test_3way_generalization()
        four_way_test = self.test_4way_generalization()
        summary_stats = self.generalization_summary_statistics()

        generalization_data = {
            'three_way_tests': three_way_tests,
            'four_way_test': four_way_test,
            'summary_statistics': summary_stats
        }

        with open(output_path, 'w') as f:
            json.dump(generalization_data, f, indent=2)

        print(f"Generalization test results exported to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Test generalization of lower-order models to higher-order behavior (Paper 4)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test 3-way and 4-way generalization
  python paper4_phase2_generalization_test.py \\
      --pairwise-results paper3_phase1_results.json \\
      --three-way-results paper4_phase1_3way_combined.json \\
      --four-way-results paper4_phase1_4way.json

  # Export as JSON
  python paper4_phase2_generalization_test.py \\
      --pairwise-results paper3_phase1_results.json \\
      --three-way-results paper4_phase1_3way_combined.json \\
      --four-way-results paper4_phase1_4way.json \\
      --json paper4_phase2_generalization.json
        """
    )

    parser.add_argument('--pairwise-results', type=Path, required=True,
                       help='Path to Paper 3 pairwise results JSON')
    parser.add_argument('--three-way-results', type=Path, required=True,
                       help='Path to Paper 4 3-way synergy results JSON')
    parser.add_argument('--four-way-results', type=Path, default=None,
                       help='Path to Paper 4 4-way synergy results JSON (optional)')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export generalization test results as JSON to specified path')

    args = parser.parse_args()

    # Load results
    if not args.pairwise_results.exists():
        print(f"Error: Pairwise results not found at {args.pairwise_results}", file=sys.stderr)
        sys.exit(1)

    if not args.three_way_results.exists():
        print(f"Error: 3-way results not found at {args.three_way_results}", file=sys.stderr)
        sys.exit(1)

    tester = GeneralizationTester.from_json(
        args.pairwise_results,
        args.three_way_results,
        args.four_way_results
    )

    # Generate output
    if args.json:
        tester.export_generalization_json(args.json)
    else:
        print(tester.generate_generalization_report())


if __name__ == '__main__':
    main()
