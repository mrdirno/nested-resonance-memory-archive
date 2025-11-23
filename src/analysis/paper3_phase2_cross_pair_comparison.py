#!/usr/bin/env python3
"""
Paper 3 Phase 2: Cross-Pair Comparison Analysis

Compares 6 factorial pairs (H1×H2, H1×H4, H1×H5, H2×H4, H2×H5, H4×H5) to identify:
- Which mechanism combinations are synergistic vs antagonistic vs additive
- Patterns in interaction effects across different mechanism pairings
- Robustness of classifications across metrics
- Mechanistic insights from comparative analysis

Designed for immediate execution when C255-C260 complete (zero-delay finalization).

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


class CrossPairComparator:
    """
    Compare mechanism interactions across multiple factorial pairs.

    Analyzes patterns in synergy classifications to identify:
    - Which mechanisms cooperate (synergistic)
    - Which mechanisms interfere (antagonistic)
    - Which mechanisms combine additively
    - Consistency across different pairings
    """

    def __init__(self, classification_results: Dict):
        """
        Initialize comparator with Phase 1 classification results.

        Args:
            classification_results: Dict from paper3_phase1_synergy_classification.py
                                   Maps pair IDs to classification dicts
        """
        self.results = classification_results
        self.pairs = list(classification_results.keys())

    @classmethod
    def from_json(cls, json_path: Path):
        """Load Phase 1 results from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls(data)

    def classification_distribution(self) -> Dict:
        """Count classification types across all pairs."""
        distribution = {'SYNERGISTIC': 0, 'ANTAGONISTIC': 0, 'ADDITIVE': 0, 'ERROR': 0}

        for pair_id, result in self.results.items():
            if 'error' in result:
                distribution['ERROR'] += 1
            else:
                classification = result['classification']
                distribution[classification] += 1

        return distribution

    def synergy_magnitude_ranking(self) -> List[Tuple[str, float]]:
        """Rank pairs by synergy magnitude (absolute value)."""
        rankings = []

        for pair_id, result in self.results.items():
            if 'error' in result:
                continue

            synergy_abs = abs(result['synergy']['synergy_absolute'])
            rankings.append((pair_id, synergy_abs))

        # Sort by magnitude (descending)
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def mechanism_involvement_analysis(self) -> Dict:
        """
        Analyze which mechanisms appear in which interaction types.

        Returns:
            Dict mapping mechanisms (H1-H5) to their involvement in each classification
        """
        # Initialize tracking
        involvement = {
            'H1': {'synergistic': [], 'antagonistic': [], 'additive': []},
            'H2': {'synergistic': [], 'antagonistic': [], 'additive': []},
            'H4': {'synergistic': [], 'antagonistic': [], 'additive': []},
            'H5': {'synergistic': [], 'antagonistic': [], 'additive': []}
        }

        for pair_id, result in self.results.items():
            if 'error' in result:
                continue

            # Parse pair ID (e.g., 'H1xH2' → ['H1', 'H2'])
            mechanisms = pair_id.replace('x', ' ').split()
            classification = result['classification'].lower()

            for mech in mechanisms:
                if mech in involvement:
                    involvement[mech][classification].append(pair_id)

        return involvement

    def interaction_pattern_matrix(self) -> Dict:
        """
        Create interaction matrix showing all pairwise mechanism interactions.

        Returns:
            Dict with matrix representation of interactions
        """
        mechanisms = ['H1', 'H2', 'H4', 'H5']
        matrix = {}

        for i, mech_a in enumerate(mechanisms):
            for j, mech_b in enumerate(mechanisms):
                if i >= j:  # Skip diagonal and lower triangle
                    continue

                pair_id = f"{mech_a}x{mech_b}"
                if pair_id in self.results and 'error' not in self.results[pair_id]:
                    classification = self.results[pair_id]['classification']
                    synergy_pct = self.results[pair_id]['synergy']['synergy_percent']
                    matrix[pair_id] = {
                        'classification': classification,
                        'synergy_percent': synergy_pct
                    }
                else:
                    matrix[pair_id] = {'classification': 'MISSING', 'synergy_percent': 0}

        return matrix

    def statistical_summary(self) -> Dict:
        """Calculate statistical summary of synergy values."""
        synergy_values = []
        synergy_percent_values = []

        for pair_id, result in self.results.items():
            if 'error' in result:
                continue

            synergy_values.append(result['synergy']['synergy_absolute'])
            synergy_percent_values.append(result['synergy']['synergy_percent'])

        if len(synergy_values) == 0:
            return {'error': 'No valid synergy values'}

        return {
            'synergy_absolute': {
                'mean': np.mean(synergy_values),
                'std': np.std(synergy_values),
                'min': np.min(synergy_values),
                'max': np.max(synergy_values),
                'median': np.median(synergy_values)
            },
            'synergy_percent': {
                'mean': np.mean(synergy_percent_values),
                'std': np.std(synergy_percent_values),
                'min': np.min(synergy_percent_values),
                'max': np.max(synergy_percent_values),
                'median': np.median(synergy_percent_values)
            }
        }

    def generate_comparison_report(self) -> str:
        """Generate comprehensive cross-pair comparison report."""
        lines = []
        lines.append("=" * 80)
        lines.append("PAPER 3 PHASE 2: CROSS-PAIR COMPARISON")
        lines.append("=" * 80)
        lines.append("")

        # Classification distribution
        distribution = self.classification_distribution()
        lines.append("CLASSIFICATION DISTRIBUTION")
        lines.append("-" * 80)
        for class_type, count in distribution.items():
            if count > 0:
                pct = (count / len(self.pairs) * 100) if len(self.pairs) > 0 else 0
                lines.append(f"  {class_type:<15} {count:>2} pairs ({pct:>5.1f}%)")
        lines.append("")

        # Synergy magnitude ranking
        rankings = self.synergy_magnitude_ranking()
        lines.append("SYNERGY MAGNITUDE RANKING (Absolute)")
        lines.append("-" * 80)
        for i, (pair_id, magnitude) in enumerate(rankings, 1):
            result = self.results[pair_id]
            classification = result['classification']
            synergy_pct = result['synergy']['synergy_percent']
            lines.append(f"  {i}. {pair_id:<8} {magnitude:>10.2f} ({synergy_pct:>+7.2f}%) - {classification}")
        lines.append("")

        # Interaction pattern matrix
        matrix = self.interaction_pattern_matrix()
        lines.append("INTERACTION PATTERN MATRIX")
        lines.append("-" * 80)
        lines.append(f"{'Pair':<10} {'Classification':<15} {'Synergy %':<12}")
        lines.append("-" * 80)
        for pair_id, data in matrix.items():
            if data['classification'] != 'MISSING':
                lines.append(f"{pair_id:<10} {data['classification']:<15} {data['synergy_percent']:>10.2f}%")
            else:
                lines.append(f"{pair_id:<10} {data['classification']:<15} N/A")
        lines.append("")

        # Mechanism involvement analysis
        involvement = self.mechanism_involvement_analysis()
        lines.append("MECHANISM INVOLVEMENT ANALYSIS")
        lines.append("-" * 80)
        for mech, patterns in involvement.items():
            lines.append(f"  {mech}:")
            for pattern_type, pairs in patterns.items():
                if len(pairs) > 0:
                    lines.append(f"    {pattern_type.capitalize():<15} {len(pairs)} pairs: {', '.join(pairs)}")
                else:
                    lines.append(f"    {pattern_type.capitalize():<15} 0 pairs")
        lines.append("")

        # Statistical summary
        stats = self.statistical_summary()
        if 'error' not in stats:
            lines.append("STATISTICAL SUMMARY")
            lines.append("-" * 80)
            lines.append("  Synergy (Absolute):")
            lines.append(f"    Mean:   {stats['synergy_absolute']['mean']:>10.2f}")
            lines.append(f"    Std:    {stats['synergy_absolute']['std']:>10.2f}")
            lines.append(f"    Range:  [{stats['synergy_absolute']['min']:.2f}, {stats['synergy_absolute']['max']:.2f}]")
            lines.append(f"    Median: {stats['synergy_absolute']['median']:>10.2f}")
            lines.append("")
            lines.append("  Synergy (Percent of Baseline):")
            lines.append(f"    Mean:   {stats['synergy_percent']['mean']:>10.2f}%")
            lines.append(f"    Std:    {stats['synergy_percent']['std']:>10.2f}%")
            lines.append(f"    Range:  [{stats['synergy_percent']['min']:.2f}%, {stats['synergy_percent']['max']:.2f}%]")
            lines.append(f"    Median: {stats['synergy_percent']['median']:>10.2f}%")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def export_comparison_json(self, output_path: Path):
        """Export comparison analysis as JSON."""
        comparison_data = {
            'classification_distribution': self.classification_distribution(),
            'synergy_magnitude_ranking': [
                {'pair_id': pair_id, 'magnitude': mag}
                for pair_id, mag in self.synergy_magnitude_ranking()
            ],
            'interaction_matrix': self.interaction_pattern_matrix(),
            'mechanism_involvement': self.mechanism_involvement_analysis(),
            'statistical_summary': self.statistical_summary()
        }

        with open(output_path, 'w') as f:
            json.dump(comparison_data, f, indent=2)

        print(f"Comparison results exported to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare mechanism interactions across Paper 3 factorial pairs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all pairs using Phase 1 results
  python paper3_phase2_cross_pair_comparison.py \\
      --phase1-results paper3_phase1_results.json

  # Export comparison as JSON
  python paper3_phase2_cross_pair_comparison.py \\
      --phase1-results paper3_phase1_results.json \\
      --json paper3_phase2_comparison.json
        """
    )

    parser.add_argument('--phase1-results', type=Path, required=True,
                       help='Path to Phase 1 classification results JSON')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export comparison results as JSON to specified path')

    args = parser.parse_args()

    # Load Phase 1 results
    if not args.phase1_results.exists():
        print(f"Error: Phase 1 results not found at {args.phase1_results}", file=sys.stderr)
        sys.exit(1)

    comparator = CrossPairComparator.from_json(args.phase1_results)

    # Generate output
    if args.json:
        comparator.export_comparison_json(args.json)
    else:
        print(comparator.generate_comparison_report())


if __name__ == '__main__':
    main()
